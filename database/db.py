import json
import logging
import random
import time
import aiosqlite
import atexit
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config
from config import (DB_PATH, SPECIAL_DEPT_ATTEMPTS_LIMIT, SPECIAL_DEPT_BLOCK_MINUTES,
                    DUNGEON_RUN_STALE_SEC, FOREST_BOAR_SEED, FOREST_WHITE_WOLF_SEED, FOREST_BOAR_HP, MOLLUSK_SEED,
                    MOLLUSK_ITEM_SEEDS, MOLLUSK_ENEMY_DROPS, PILOT_CRIT_MULT,
                    MINE_BAT_SEED, MINE_ITEM_SEEDS, MINE_ENEMY_DROPS, MINE_SHOP_ITEMS,
                    MINE_PICKAXE_NAME, MINE_ORE_NAME, MINE_BAT_SPOT,
                    LOGGING_SNAKE_SEED, LOGGING_OWL_SEED, LOGGING_ITEM_SEEDS,
                    LOGGING_ENEMY_DROPS, LOGGING_SHOP_ITEMS,
                    LOGGING_MARKET_RESOURCES)
from config import get_effective_rank

logger = logging.getLogger(__name__)

db: aiosqlite.Connection | None = None


async def get_db() -> aiosqlite.Connection:
    global db
    if db is None:
        conn = aiosqlite.connect(DB_PATH, isolation_level=None)
        # Поток воркера aiosqlite — обычный, НЕ daemon: если скрипт упал
        # до close_db(), процесс не завершается НИКОГДА (тест «зависает»
        # вместо того, чтобы упасть, — прогон всех смоуков встаёт).
        # Флаг daemon выставляем ДО старта потока (поток создаётся в
        # __init__ Connection и стартует только при await). Это правится
        # централизованно, без переписывания сотни смоуков.
        try:
            conn._thread.daemon = True
        except Exception:
            pass
        db = await conn

        def _dict_factory(cursor, row):
            """Dict-строка БД вместо sqlite3.Row.

            Row не имеет .get() — из-за этого handler'ы падают с
            AttributeError повторяющимся классом. Dict даёт и [],
            и .get(), и .keys(), и 'key in row' — все паттерны
            кода работают без изменений.
            """
            return {col[0]: row[i] for i, col in enumerate(cursor.description)}

        db.row_factory = _dict_factory
        await db.execute("PRAGMA journal_mode=WAL")
        await db.execute("PRAGMA foreign_keys=ON")
    return db


async def close_db():
    global db
    if db:
        await db.close()
        db = None


def _atexit_close_db():
    """Закрыть БД при выходе из скрипта.

    Нужен смоукам, которые упали до close_db(): без этого остаётся
    непрочитанное соединение и «висящий» тест вместо падения.
    """
    global db
    if db is None:
        return
    try:
        db.stop()
    except Exception:
        pass
    db = None


atexit.register(_atexit_close_db)


async def init_db():
    conn = await get_db()
    await conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            photo_file_id TEXT,
            troops INTEGER DEFAULT 0,
            nordmarks INTEGER DEFAULT 10,
            ap INTEGER DEFAULT 100,
            ap_max INTEGER DEFAULT 150,
            state TEXT DEFAULT 'нормально',
            state_effects TEXT DEFAULT '{}',
            promoted_rank TEXT,
            status_text TEXT DEFAULT 'Боевой пилот',
            about TEXT DEFAULT '',
            notify_enabled INTEGER DEFAULT 1,
            profile_public INTEGER DEFAULT 1,
            equipment TEXT DEFAULT '{}',
            salary INTEGER DEFAULT 0,
            salary_period_days INTEGER DEFAULT 7,
            last_salary_date TIMESTAMP,
            salary_debt INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            photo_file_id TEXT,
            price INTEGER NOT NULL,
            sell_price INTEGER NOT NULL,
            rarity INTEGER DEFAULT 1,
            category TEXT DEFAULT 'special',
            is_available INTEGER DEFAULT 1,
            stock INTEGER DEFAULT -1,
            added_by INTEGER,
            produced_by INTEGER,
            production_time_hours INTEGER DEFAULT 0,
            ap_cost INTEGER DEFAULT 0,
            heal INTEGER DEFAULT 0,
            armor INTEGER DEFAULT 0,
            drink_effect TEXT DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            item_id INTEGER NOT NULL,
            quantity INTEGER DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (item_id) REFERENCES items(id),
            UNIQUE(user_id, item_id)
        );

        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_user INTEGER,
            to_user INTEGER,
            amount INTEGER NOT NULL,
            tx_type TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_user INTEGER NOT NULL,
            to_user INTEGER NOT NULL,
            from_item_id INTEGER,
            from_item_qty INTEGER DEFAULT 0,
            from_nordmarks INTEGER DEFAULT 0,
            to_item_id INTEGER,
            to_item_qty INTEGER DEFAULT 0,
            to_nordmarks INTEGER DEFAULT 0,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (from_user) REFERENCES users(user_id),
            FOREIGN KEY (to_user) REFERENCES users(user_id)
        );

        CREATE TABLE IF NOT EXISTS polls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_id INTEGER NOT NULL,
            question TEXT NOT NULL,
            options TEXT NOT NULL,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS poll_votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            poll_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            option_index INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (poll_id) REFERENCES polls(id),
            UNIQUE(poll_id, user_id)
        );

        CREATE TABLE IF NOT EXISTS news_releases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            body TEXT DEFAULT '',
            photo_file_id TEXT,
            author_id INTEGER NOT NULL,
            author_name TEXT DEFAULT '',
            created_at TEXT NOT NULL DEFAULT '',
            edited INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS daily_limits (
            admin_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            spent INTEGER DEFAULT 0,
            PRIMARY KEY (admin_id, date)
        );

        CREATE TABLE IF NOT EXISTS treasury (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            balance INTEGER DEFAULT 0
        );

        INSERT OR IGNORE INTO treasury (id, balance) VALUES (1, 0);

        CREATE TABLE IF NOT EXISTS award_monthly_paid (
            user_id INTEGER NOT NULL,
            award_id INTEGER NOT NULL,
            month TEXT NOT NULL,
            paid_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, award_id, month)
        );

        CREATE TABLE IF NOT EXISTS role_salaries (
            role TEXT PRIMARY KEY,
            amount INTEGER NOT NULL DEFAULT 0
        );
        INSERT OR IGNORE INTO role_salaries (role, amount) VALUES
            ('shop_admin', 200),
            ('finance_admin', 200),
            ('finance_helper', 50),
            ('moderator', 200),
            ('mvd_helper', 50),
            ('representative', 350),
            ('wing_commander', 150),
            ('wing_deputy', 75),
            ('librarian', 100),
            ('journalist', 70),
            ('editor', 120);

        CREATE TABLE IF NOT EXISTS role_salary_paid (
            user_id INTEGER NOT NULL,
            month TEXT NOT NULL,
            amount INTEGER DEFAULT 0,
            paid_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, month)
        );

        -- v0.22.18: пропорциональные выплаты при досрочном снятии должности.
        -- Отдельный табель (не role_salary_paid), чтобы частичная выплата при
        -- снятии НЕ блокировала обычный оклад 28-го по остальным должностям.
        CREATE TABLE IF NOT EXISTS role_dismissal_paid (
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            month TEXT NOT NULL,
            amount INTEGER DEFAULT 0,
            paid_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, role, month)
        );

        CREATE TABLE IF NOT EXISTS news_pub_paid (
            user_id INTEGER NOT NULL,
            month TEXT NOT NULL,
            count INTEGER DEFAULT 0,
            PRIMARY KEY (user_id, month)
        );

        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL DEFAULT ''
        );

        INSERT OR IGNORE INTO settings (key, value) VALUES ('report_tax_percent', '15');
        INSERT OR IGNORE INTO settings (key, value) VALUES ('sale_tax_percent', '15');
        INSERT OR IGNORE INTO settings (key, value) VALUES ('report_auto_approve_troops', '100');

        CREATE TABLE IF NOT EXISTS library_cards (
            user_id INTEGER NOT NULL,
            card_type TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            PRIMARY KEY (user_id, card_type)
        );

        CREATE TABLE IF NOT EXISTS library_books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            section TEXT NOT NULL,
            title TEXT NOT NULL,
            author TEXT DEFAULT '',
            description TEXT DEFAULT '',
            cover_file_id TEXT,
            file_id TEXT,
            file_type TEXT,
            url TEXT,
            added_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_user INTEGER NOT NULL,
            to_user INTEGER NOT NULL,
            interaction_type TEXT NOT NULL,
            state_change TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (from_user) REFERENCES users(user_id),
            FOREIGN KEY (to_user) REFERENCES users(user_id)
        );

        -- Дом Дуэлей (PvP): один активный поединок на игрока.
        -- status: invited (вызов брошен) | active (бой идёт) | declined |
        --         finished (есть победитель/ничья) | expired (вызов не принят /
        --         дуэль зависла и обнулена как void).
        -- {challenger,opponent}_atk / _def — зоны текущего раунда (NULL = ещё
        -- не выбрана). Раунд резолвится, когда заполнены все четыре поля.
        CREATE TABLE IF NOT EXISTS duel_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            challenger_id INTEGER NOT NULL,
            opponent_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'invited',
            challenger_hp INTEGER NOT NULL DEFAULT 0,
            opponent_hp INTEGER NOT NULL DEFAULT 0,
            challenger_hp_max INTEGER NOT NULL DEFAULT 0,
            opponent_hp_max INTEGER NOT NULL DEFAULT 0,
            turn INTEGER NOT NULL DEFAULT 1,
            challenger_atk TEXT,
            challenger_def TEXT,
            opponent_atk TEXT,
            opponent_def TEXT,
            winner_id INTEGER,
            rating_delta INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (challenger_id) REFERENCES users(user_id),
            FOREIGN KEY (opponent_id) REFERENCES users(user_id)
        );

        CREATE INDEX IF NOT EXISTS idx_duel_runs_challenger
            ON duel_runs (challenger_id, status);
        CREATE INDEX IF NOT EXISTS idx_duel_runs_opponent
            ON duel_runs (opponent_id, status);

        CREATE TABLE IF NOT EXISTS buildings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            photo_file_id TEXT,
            price INTEGER NOT NULL,
            category TEXT DEFAULT 'production',
            production_type TEXT,
            production_item_id INTEGER,
            production_time_hours INTEGER DEFAULT 24,
            requires_resources INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS user_buildings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            building_id INTEGER NOT NULL,
            level INTEGER DEFAULT 1,
            purchased_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (building_id) REFERENCES buildings(id),
            UNIQUE(user_id, building_id)
        );

        CREATE TABLE IF NOT EXISTS production_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            building_id INTEGER NOT NULL,
            recipe_item_id INTEGER NOT NULL,
            ap_cost INTEGER NOT NULL,
            resources_used TEXT DEFAULT '{}',
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completes_at TIMESTAMP NOT NULL,
            status TEXT DEFAULT 'active',
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (building_id) REFERENCES buildings(id),
            FOREIGN KEY (recipe_item_id) REFERENCES items(id)
        );

        CREATE TABLE IF NOT EXISTS dungeon_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            floor INTEGER DEFAULT 1,
            enemies_defeated INTEGER DEFAULT 0,
            items_found TEXT DEFAULT '[]',
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            UNIQUE(user_id)
        );

        CREATE TABLE IF NOT EXISTS dungeon_rewards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            item_id INTEGER NOT NULL,
            floor INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (item_id) REFERENCES items(id)
        );

        CREATE TABLE IF NOT EXISTS dungeons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            floors_count INTEGER DEFAULT 1,
            rooms_per_floor INTEGER DEFAULT 10,
            is_active INTEGER DEFAULT 1,
            photo_dawn TEXT,
            photo_day TEXT,
            photo_sunset TEXT,
            photo_night TEXT
        );

        CREATE TABLE IF NOT EXISTS dungeon_enemies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dungeon_id INTEGER NOT NULL,
            floor INTEGER NOT NULL,
            name TEXT NOT NULL,
            hp INTEGER NOT NULL,
            attack INTEGER NOT NULL,
            reward_nm INTEGER DEFAULT 5,
            is_boss INTEGER DEFAULT 0,
            drops TEXT DEFAULT '[]',
            dodge INTEGER DEFAULT 0,
            FOREIGN KEY (dungeon_id) REFERENCES dungeons(id)
        );

        CREATE TABLE IF NOT EXISTS dungeon_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dungeon_id INTEGER NOT NULL,
            floor INTEGER NOT NULL,
            item_id INTEGER NOT NULL,
            drop_chance REAL DEFAULT 0.1,
            FOREIGN KEY (dungeon_id) REFERENCES dungeons(id),
            FOREIGN KEY (item_id) REFERENCES items(id)
        );

        CREATE TABLE IF NOT EXISTS player_dungeon_run (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            dungeon_id INTEGER NOT NULL,
            floor INTEGER DEFAULT 1,
            room_number INTEGER DEFAULT 0,
            hp INTEGER DEFAULT 100,
            hp_max INTEGER DEFAULT 100,
            is_active INTEGER DEFAULT 1,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (dungeon_id) REFERENCES dungeons(id),
            UNIQUE(user_id)
        );

        CREATE TABLE IF NOT EXISTS player_dungeon_inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER NOT NULL,
            item_id INTEGER NOT NULL,
            quantity INTEGER DEFAULT 1,
            FOREIGN KEY (run_id) REFERENCES player_dungeon_run(id),
            FOREIGN KEY (item_id) REFERENCES items(id),
            UNIQUE(run_id, item_id)
        );

        CREATE TABLE IF NOT EXISTS player_kvp (
            user_id INTEGER PRIMARY KEY,
            completions INTEGER DEFAULT 0,
            badge_awarded INTEGER DEFAULT 0,
            stick_dropped INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );

        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            screenshot_file_id TEXT,
            troops_reported INTEGER NOT NULL,
            region TEXT,
    status TEXT DEFAULT 'pending',
    reviewed_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );
        CREATE INDEX IF NOT EXISTS idx_reports_created ON reports(created_at);

        CREATE TABLE IF NOT EXISTS resource_sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            item_id INTEGER NOT NULL,
            building_id INTEGER,
            interval_days INTEGER DEFAULT 3,
            last_harvest TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (item_id) REFERENCES items(id)
        );

        CREATE TABLE IF NOT EXISTS region_stats (
    region TEXT PRIMARY KEY,
    troops_total INTEGER DEFAULT 0,
    pilots_count INTEGER DEFAULT 0,
            computed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS state_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            old_state TEXT,
            new_state TEXT,
            reason TEXT,
            caused_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );

        CREATE TABLE IF NOT EXISTS user_roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            granted_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(telegram_id, role)
        );

        CREATE TABLE IF NOT EXISTS wing_commanders (
            wing TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS wing_deputies (
        wing TEXT PRIMARY KEY,
        user_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

        -- v0.18.13: формирования ВВС в БД (редактор в штабе). Ключ пилота в users.wing
        -- ссылается сюда (legacy '1'..'4'; новые — 'N АБ', где АБ — две заглавные буквы).
        -- Номер и аббревиатура хранятся отдельно, чтобы метка всегда была «число + 2 буквы».
        CREATE TABLE IF NOT EXISTS wings (
            key TEXT PRIMARY KEY,
            num TEXT NOT NULL DEFAULT '',
            abbr TEXT NOT NULL DEFAULT '',
            name TEXT NOT NULL DEFAULT '',
            callsign TEXT NOT NULL DEFAULT '',
            emoji TEXT NOT NULL DEFAULT '',
            sort_order INTEGER DEFAULT 0
        );

        INSERT OR IGNORE INTO wings (key, num, abbr, name, callsign, emoji, sort_order) VALUES
            ('1', '1', 'АК', 'Авиакрыло', 'Небесные Волки', '🐺', 1),
            ('2', '2', 'АК', 'Авиакрыло', 'Полярные Совы', '🦉', 2),
            ('3', '3', 'АК', 'Авиакрыло', 'Тени Нордхама', '🌑', 3),
            ('4', '4', 'СО', 'Спец отряд', 'Polaris', '❄️', 4),
            ('reserve', '', 'Резерв', 'Резерв', 'Свободные пилоты', '🪖', 99);

    CREATE TABLE IF NOT EXISTS admin_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            target_id INTEGER,
            details TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS report_notify_tiers (
        user_id INTEGER NOT NULL,
        day TEXT NOT NULL,
        tier INTEGER NOT NULL DEFAULT 0,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (user_id, day)
    );

    CREATE TABLE IF NOT EXISTS activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            details TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );
        CREATE INDEX IF NOT EXISTS idx_activity_user ON activity_log(user_id, id);

        CREATE TABLE IF NOT EXISTS ap_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            delta INTEGER NOT NULL,
            ap_before INTEGER NOT NULL,
            ap_after INTEGER NOT NULL,
            reason TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );
        CREATE INDEX IF NOT EXISTS idx_ap_user ON ap_log(user_id, id);

        CREATE TABLE IF NOT EXISTS location_visits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            location_key TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );
        CREATE INDEX IF NOT EXISTS idx_locvis_user ON location_visits(user_id, id);
        CREATE INDEX IF NOT EXISTS idx_locvis_loc ON location_visits(location_key, created_at);

        CREATE TABLE IF NOT EXISTS booklet_visits (
            user_id INTEGER NOT NULL,
            location_key TEXT NOT NULL,
            visited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, location_key),
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );

        CREATE TABLE IF NOT EXISTS booklet_claims (
            user_id INTEGER PRIMARY KEY,
            claimed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );

        CREATE TABLE IF NOT EXISTS nii_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            photo_file_id TEXT,
            photo2_file_id TEXT,
            status TEXT DEFAULT 'open',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );
        CREATE INDEX IF NOT EXISTS idx_nii_user ON nii_reports(user_id, id);
        CREATE INDEX IF NOT EXISTS idx_nii_created ON nii_reports(created_at);

        CREATE TABLE IF NOT EXISTS locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            description TEXT,
            access_mode TEXT NOT NULL DEFAULT 'all',
            required_status TEXT,
            blocking_states TEXT DEFAULT '[]',
            preview_photo TEXT,
            photo_dawn TEXT,
            photo_day TEXT,
            photo_sunset TEXT,
            photo_night TEXT,
            sort_order INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS park_statues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            image_dawn TEXT,
            image_day TEXT,
            image_sunset TEXT,
            image_night TEXT,
            created_by INTEGER,
            sort_order INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS fish_catches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            item_id INTEGER NOT NULL,
            weight INTEGER NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            sold_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (item_id) REFERENCES items(id)
        );
        CREATE INDEX IF NOT EXISTS idx_fish_catches_user ON fish_catches(user_id, sold_at);

        CREATE TABLE IF NOT EXISTS market_fish (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            seller_id INTEGER NOT NULL,
            item_id INTEGER NOT NULL,
            weight INTEGER NOT NULL DEFAULT 1,
            price INTEGER NOT NULL,
            remaining_sec INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (seller_id) REFERENCES users(user_id),
            FOREIGN KEY (item_id) REFERENCES items(id)
        );
        CREATE INDEX IF NOT EXISTS idx_market_fish ON market_fish(created_at);

        CREATE TABLE IF NOT EXISTS market_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            seller_id INTEGER NOT NULL,
            item_id INTEGER NOT NULL,
            price INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (seller_id) REFERENCES users(user_id),
            FOREIGN KEY (item_id) REFERENCES items(id)
        );
        CREATE INDEX IF NOT EXISTS idx_market_items ON market_items(created_at);

        CREATE TABLE IF NOT EXISTS statuses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            access_tag TEXT,
            description TEXT,
            sort_order INTEGER DEFAULT 0,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS user_statuses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            status_id INTEGER NOT NULL,
            granted_by INTEGER,
            is_selected INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, status_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (status_id) REFERENCES statuses(id)
        );

        CREATE TABLE IF NOT EXISTS awards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            emoji TEXT DEFAULT '🏅',
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS user_awards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            award_id INTEGER NOT NULL,
            granted_by INTEGER,
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (award_id) REFERENCES awards(id)
        );

        CREATE TABLE IF NOT EXISTS user_achievements (
            user_id INTEGER NOT NULL,
            akey TEXT NOT NULL,
            level INTEGER NOT NULL DEFAULT 0,
            progress INTEGER NOT NULL DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, akey),
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );

        CREATE TABLE IF NOT EXISTS city_storage (
            item_id INTEGER PRIMARY KEY,
            qty INTEGER NOT NULL DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (item_id) REFERENCES items(id)
        );

        CREATE TABLE IF NOT EXISTS player_housing (
            user_id INTEGER PRIMARY KEY,
            housing_type TEXT DEFAULT 'municipal',
            purchased_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );

        CREATE TABLE IF NOT EXISTS housing_slots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            slot_index INTEGER NOT NULL,
            expansion_type TEXT,
            expansion_level INTEGER DEFAULT 1,
            plant_data TEXT DEFAULT '{}',
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            UNIQUE(user_id, slot_index)
        );

        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            result_item_name TEXT NOT NULL,
            result_quantity INTEGER DEFAULT 1,
            required_expansion TEXT,
            required_level INTEGER DEFAULT 1,
            ingredients TEXT NOT NULL DEFAULT '[]',
            ap_cost INTEGER DEFAULT 0,
            production_time INTEGER DEFAULT 30,
            rarity INTEGER DEFAULT 1,
            is_available INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS water_fish (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            water TEXT NOT NULL,
            item_id INTEGER NOT NULL,
            day_weight INTEGER DEFAULT 0,
            night_weight INTEGER DEFAULT 0,
            photo_file_id TEXT,
            admin_tuned INTEGER DEFAULT 0,
            super_rare INTEGER DEFAULT 0,
            UNIQUE(water, item_id)
        );

        CREATE TABLE IF NOT EXISTS water_junk (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            water TEXT NOT NULL,
            name TEXT NOT NULL,
            chance INTEGER DEFAULT 15,
            photo_file_id TEXT,
            admin_tuned INTEGER DEFAULT 0,
            UNIQUE(water, name)
        );

        CREATE TABLE IF NOT EXISTS forest_mushrooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL UNIQUE,
            chance INTEGER DEFAULT 10,
            kind TEXT DEFAULT 'edible',
            photo_file_id TEXT,
            admin_tuned INTEGER DEFAULT 0,
            excluded INTEGER DEFAULT 0,
            zone TEXT DEFAULT 'clearing'
        );

        -- Враги вне подземелья (лес, рыбалка). Набор колонок одинаковый у обеих
        -- таблиц, чтобы единый админ-редактор работал с ними одинаково.
        -- key — технический идентификатор ('boar', 'mollusk'), spot — место
        -- встречи внутри источника ('forest', 'reservoir').
        CREATE TABLE IF NOT EXISTS forest_enemies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT,
            spot TEXT DEFAULT 'forest',
            name TEXT NOT NULL,
            hp INTEGER DEFAULT 30,
            dmg_min INTEGER DEFAULT 5,
            dmg_max INTEGER DEFAULT 9,
            dodge INTEGER DEFAULT 0,
            loss_ap INTEGER DEFAULT 0,
            bleed_chance INTEGER DEFAULT 0,
            bleed_dmg INTEGER DEFAULT 0,
            chance REAL DEFAULT 0,
            pity_target INTEGER DEFAULT 0,
            reward_nm INTEGER DEFAULT 0,
            drops TEXT DEFAULT '[]',
            description TEXT,
            image TEXT,
            photo_key TEXT,
            enabled INTEGER DEFAULT 1,
            admin_tuned INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS fishing_enemies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT,
            spot TEXT DEFAULT 'reservoir',
            name TEXT NOT NULL,
            hp INTEGER DEFAULT 30,
            dmg_min INTEGER DEFAULT 5,
            dmg_max INTEGER DEFAULT 9,
            dodge INTEGER DEFAULT 0,
            loss_ap INTEGER DEFAULT 0,
            bleed_chance INTEGER DEFAULT 0,
            bleed_dmg INTEGER DEFAULT 0,
            chance REAL DEFAULT 0,
            pity_target INTEGER DEFAULT 0,
            reward_nm INTEGER DEFAULT 0,
            drops TEXT DEFAULT '[]',
            description TEXT,
            image TEXT,
            photo_key TEXT,
            enabled INTEGER DEFAULT 1,
            admin_tuned INTEGER DEFAULT 0
        );
        -- v0.31.0: Железная копи — враги ресурсной локации (Летучая мышь).
        -- Набор колонок повторяет forest_enemies/fishing_enemies: единый
        -- админ-редактор и общие CRUD-функции работают через source='mine'.
        CREATE TABLE IF NOT EXISTS mine_enemies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT,
            spot TEXT DEFAULT 'iron',
            name TEXT NOT NULL,
            hp INTEGER DEFAULT 30,
            dmg_min INTEGER DEFAULT 5,
            dmg_max INTEGER DEFAULT 9,
            dodge INTEGER DEFAULT 0,
            loss_ap INTEGER DEFAULT 0,
            bleed_chance INTEGER DEFAULT 0,
            bleed_dmg INTEGER DEFAULT 0,
            chance REAL DEFAULT 0,
            pity_target INTEGER DEFAULT 0,
            reward_nm INTEGER DEFAULT 0,
            drops TEXT DEFAULT '[]',
            description TEXT,
            image TEXT,
            photo_key TEXT,
            enabled INTEGER DEFAULT 1,
            admin_tuned INTEGER DEFAULT 0
        );
        -- v0.37.0: Лесозаготовка — враги ресурсной локации в лесу
        -- (Лесная змея и Неясыть). Набор колонок как у mine_enemies.
        CREATE TABLE IF NOT EXISTS logging_enemies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT,
            spot TEXT DEFAULT 'logging',
            name TEXT NOT NULL,
            hp INTEGER DEFAULT 30,
            dmg_min INTEGER DEFAULT 5,
            dmg_max INTEGER DEFAULT 9,
            dodge INTEGER DEFAULT 0,
            loss_ap INTEGER DEFAULT 0,
            bleed_chance INTEGER DEFAULT 0,
            bleed_dmg INTEGER DEFAULT 0,
            chance REAL DEFAULT 0,
            pity_target INTEGER DEFAULT 0,
            reward_nm INTEGER DEFAULT 0,
            drops TEXT DEFAULT '[]',
            description TEXT,
            image TEXT,
            photo_key TEXT,
            enabled INTEGER DEFAULT 1,
            admin_tuned INTEGER DEFAULT 0
        );

        -- Враги Огненного Лабиринта (событие «Дни Пламенного Круговорота»).
        CREATE TABLE IF NOT EXISTS firelab_enemies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT,
            spot TEXT DEFAULT 'firelab',
            name TEXT NOT NULL,
            hp INTEGER DEFAULT 30,
            dmg_min INTEGER DEFAULT 5,
            dmg_max INTEGER DEFAULT 9,
            armor INTEGER DEFAULT 0,
            dodge INTEGER DEFAULT 0,
            loss_ap INTEGER DEFAULT 0,
            bleed_chance INTEGER DEFAULT 0,
            bleed_dmg INTEGER DEFAULT 0,
            chance REAL DEFAULT 0,
            pity_target INTEGER DEFAULT 0,
            reward_nm INTEGER DEFAULT 0,
            drops TEXT DEFAULT '[]',
            description TEXT,
            image TEXT,
            photo_key TEXT,
            enabled INTEGER DEFAULT 1,
            admin_tuned INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS wall_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_day TEXT NOT NULL DEFAULT '',
            tier INTEGER DEFAULT 0,
            cost INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );

        CREATE TABLE IF NOT EXISTS wall_archives (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            period_start TEXT NOT NULL DEFAULT '',
            period_end TEXT NOT NULL DEFAULT '',
            post_count INTEGER DEFAULT 0,
            archived_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS wall_archive_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            archive_id INTEGER NOT NULL,
            post_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT '',
            created_day TEXT NOT NULL DEFAULT '',
            cost INTEGER DEFAULT 0,
            tier INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS clans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kind TEXT NOT NULL DEFAULT 'clan',          -- 'clan' | 'party'
            name TEXT NOT NULL,
            description TEXT DEFAULT '',
            photo_file_id TEXT,
            leader_id INTEGER,
            created_by INTEGER,
            tree_amber_at TEXT DEFAULT NULL,            -- Древо: таймер Эссии
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS clan_members (
            clan_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL DEFAULT 'member',
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (clan_id, user_id)
        );

        CREATE TABLE IF NOT EXISTS clan_requests (
            clan_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (clan_id, user_id)
        );

        CREATE TABLE IF NOT EXISTS clan_storage (
            clan_id INTEGER NOT NULL,
            item_id INTEGER NOT NULL,
            qty INTEGER NOT NULL DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (clan_id, item_id)
        );

        CREATE TABLE IF NOT EXISTS clan_build_contrib (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            clan_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            item_id INTEGER NOT NULL,
            qty INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_clan_storage_clan ON clan_storage(clan_id);
        CREATE INDEX IF NOT EXISTS idx_clan_contrib_clan ON clan_build_contrib(clan_id);

        CREATE TABLE IF NOT EXISTS clan_buildings (
            clan_id INTEGER PRIMARY KEY,
            building_type TEXT,
            target_type TEXT,
            status TEXT NOT NULL DEFAULT 'choosing',
            required_json TEXT,
            price_nm INTEGER DEFAULT 0,
            chosen_at TIMESTAMP,
            started_at TIMESTAMP,
            completes_at TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            building_photo_file_id TEXT
        );

        CREATE TABLE IF NOT EXISTS clan_expansions (
            clan_id INTEGER NOT NULL,
            slot_index INTEGER NOT NULL,
            expansion_type TEXT NOT NULL,
            expansion_level INTEGER DEFAULT 1,
            installed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (clan_id, slot_index)
        );

        CREATE UNIQUE INDEX IF NOT EXISTS idx_clan_expansion_type
            ON clan_expansions(clan_id, expansion_type);

        CREATE TABLE IF NOT EXISTS clan_garden (
            clan_id INTEGER NOT NULL,
            plot_index INTEGER NOT NULL,
            seed_name TEXT NOT NULL,
            plant_name TEXT,
            planted_by INTEGER,
            stage_started_at REAL,
            last_harvest_at REAL,
            planted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (clan_id, plot_index)
        );

        -- Клановая библиотека рецептов (Фаза 6).
        CREATE TABLE IF NOT EXISTS clan_recipes (
            clan_id INTEGER NOT NULL,
            recipe_id INTEGER NOT NULL,
            donated_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (clan_id, recipe_id)
        );
        CREATE INDEX IF NOT EXISTS idx_clan_recipes_clan ON clan_recipes(clan_id);

        -- Клановая лавка (Фаза 7): витрина расширения «shop».
        CREATE TABLE IF NOT EXISTS clan_shop_items (
            clan_id INTEGER NOT NULL,
            item_id INTEGER NOT NULL,
            price INTEGER NOT NULL,
            stock INTEGER DEFAULT -1,
            is_active INTEGER DEFAULT 1,
            PRIMARY KEY (clan_id, item_id)
        );
        CREATE INDEX IF NOT EXISTS idx_clan_shop_clan ON clan_shop_items(clan_id);

        -- Суточный лимит покупок (Фаза 7): счётчик на (клан, пилот, день).
        CREATE TABLE IF NOT EXISTS clan_shop_purchases (
            clan_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            buy_day TEXT NOT NULL DEFAULT '',
            qty INTEGER DEFAULT 0,
            PRIMARY KEY (clan_id, user_id, buy_day)
        );

        -- Дни Пламенного Круговорота: сессии Огненного Лабиринта (событие).
        CREATE TABLE IF NOT EXISTS fire_lab_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'active',      -- active/dead/left/finished/expired/event_closed
            hp INTEGER NOT NULL DEFAULT 0,
            hp_max INTEGER NOT NULL DEFAULT 0,
            steps INTEGER NOT NULL DEFAULT 0,           -- комнат-развилок пройдено
            path_history TEXT NOT NULL DEFAULT '[]',    -- выбранные пути ('L'/'S'/'R')
            blessing INTEGER NOT NULL DEFAULT 0,        -- благословение Древа Огня (эта сессия)
            well_visits INTEGER NOT NULL DEFAULT 0,
            tree_visits INTEGER NOT NULL DEFAULT 0,
            chest_visits INTEGER NOT NULL DEFAULT 0,
            boss_defeated INTEGER NOT NULL DEFAULT 0,
            entered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_active_at TIMESTAMP,
            ended_at TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_fire_lab_user ON fire_lab_sessions(user_id, status);

        -- Учёт входов в лабиринт (дневной лимит: (user, day) → count).
        CREATE TABLE IF NOT EXISTS fire_lab_entries (
            user_id INTEGER NOT NULL,
            day TEXT NOT NULL DEFAULT '',
            qty INTEGER DEFAULT 0,
            PRIMARY KEY (user_id, day)
        );

        -- Огненное эхо: Тир сложности лабиринта у пилота (кап FIRE_LAB_TIER_MAX).
        CREATE TABLE IF NOT EXISTS fire_lab_tier (
            user_id INTEGER PRIMARY KEY,
            tier INTEGER NOT NULL DEFAULT 0,
            runs INTEGER NOT NULL DEFAULT 0,            -- сколько раз пройдено 25 комнат
            updated_at TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS user_recipes (
            user_id INTEGER NOT NULL,
            recipe_id INTEGER NOT NULL,
            learned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, recipe_id)
        );

        -- Книга рецептов: предмет-книга (items, category='recipes') -> набор рецептов.
        -- Пустых книг не бывает (менеджер требует минимум один рецепт).
        CREATE TABLE IF NOT EXISTS recipe_book_items (
            book_item_id INTEGER NOT NULL,
            recipe_id INTEGER NOT NULL,
            PRIMARY KEY (book_item_id, recipe_id)
        );
    """)
    await conn.commit()

    # Миграция: колонки required_status и sort_order (если нет)
    await _ensure_column(conn, "items", "required_status", "TEXT")
    await _ensure_column(conn, "buildings", "required_status", "TEXT")
    await _ensure_column(conn, "statuses", "sort_order", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "clan_members", "role", "TEXT NOT NULL DEFAULT 'member'")
    await _backfill_clan_member_roles()
    await _ensure_column(conn, "users", "promoted_rank", "TEXT")
    # Тратимый опыт: копится 1:1 с суточным фармом, не облагается налогом, звание
    # по нему НЕ считается (звание — по users.troops). Создан для будущего магазина
    # уникальных покупок: тратить можно, звания остаются.
    xp_added = await _ensure_column(conn, "users", "xp_balance", "INTEGER DEFAULT 0")
    # v0.18.5: накопительный опыт выравнивается с войсками ОДИН раз. Поле появилось
    # позже (v0.17.0), поэтому у ветеранов xp_balance меньше troops: раньше опыт
    # копился только с новых выплат. Тратить опыт пока негде (магазин уникальных
    # покупок не реализован), поэтому разово приравниваем к войскам. Повторно не
    # запускается (флаг в settings): в будущем расхождение станет законным.
    _xp_backfill = await (await conn.execute(
        "SELECT value FROM settings WHERE key = 'xp_backfill_v0185'")).fetchone()
    if not _xp_backfill:
        await conn.execute("UPDATE users SET xp_balance = troops "
                           "WHERE COALESCE(xp_balance, 0) < troops")
        await conn.execute(
            "INSERT INTO settings (key, value) VALUES ('xp_backfill_v0185', '1') "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value")
        await conn.commit()
        logger.info("Накопительный опыт выровнен с войсками (v0.18.5)")
    await _ensure_column(conn, "users", "notify_enabled", "INTEGER DEFAULT 1")
    await _ensure_column(conn, "users", "profile_public", "INTEGER DEFAULT 1")
    await _ensure_column(conn, "users", "about", "TEXT DEFAULT ''")
    await _ensure_column(conn, "users", "equipment", "TEXT DEFAULT '{}'")
    await _ensure_column(conn, "users", "salary", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "users", "salary_period_days", "INTEGER DEFAULT 7")
    await _ensure_column(conn, "users", "last_salary_date", "TIMESTAMP")
    await _ensure_column(conn, "users", "salary_debt", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "items", "armor", "INTEGER DEFAULT 0")
    # Критический удар пилота: шанс в процентах и множитель урона.
    # Суммируются по всем надетым предметам — см. get_player_crit_chance.
    await _ensure_column(conn, "items", "crit_chance", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "items", "crit_mult", "REAL DEFAULT 0")
    # Слот тела для предметов снаряжения: 'head' | 'body' | 'hands' | 'legs'
    await _ensure_column(conn, "items", "equip_slot", "TEXT")
    await conn.execute("UPDATE items SET equip_slot = 'head' WHERE name = 'Лётный шлем' AND equip_slot IS NULL")
    await conn.execute("UPDATE items SET equip_slot = 'body' WHERE category = 'equipment' AND armor > 0 AND equip_slot IS NULL")
    await _ensure_column(conn, "reports", "total_troops", "INTEGER DEFAULT 0")
    # credited_troops без DEFAULT: у старых отчётов (до миграции) будет NULL
    await _ensure_column(conn, "reports", "credited_troops", "INTEGER")
    # paid=1 — отчёт оплачен суточным начислением. При создании колонки старые
    # одобренные отчёты уже оплачены старой механикой (начисление при одобрении) —
    # помечаем их оплаченными ОДИН раз, чтобы суточная выплата не задвоила им начисление.
    # ВАЖНО: выполняется только при создании колонки. Безусловный UPDATE при каждом
    # старте помечал бы «оплаченными» одобренные, но ещё не выплаченные отчёты
    # (payout_reports идёт раз в сутки), и они терялись навсегда без начисления.
    paid_created = await _ensure_column(conn, "reports", "paid", "INTEGER DEFAULT 0")
    if paid_created:
        await conn.execute("UPDATE reports SET paid = 1 WHERE status = 'approved'")
    # v0.17.0: отчётные сутки идут от выплаты до выплаты, оплата — по заявке «за сутки»
    # (раньше она упиралась в прирост «всего», из-за чего честные заявки обнулялись).
    # Висящие отчёты, посчитанные по старому правилу в ноль, пересчитываем — иначе
    # они так и висели бы с нулевой суммой. Условие самопроверяющееся (висящий отчёт
    # с нулевым засчитанным и ненулевой заявкой), поэтому повторный старт безвреден.
    stale_pending = await (await conn.execute(
        "SELECT id, user_id, troops_reported FROM reports "
        "WHERE status = 'pending' AND COALESCE(credited_troops, 0) = 0 "
        "AND COALESCE(troops_reported, 0) > 0"
    )).fetchall()
    for _r in stale_pending:
        _ctx = await report_payout_context(_r['user_id'], _r['troops_reported'],
                                           exclude_id=_r['id'])
        await conn.execute("UPDATE reports SET credited_troops = ? WHERE id = ?",
                           (_ctx["payable"], _r['id']))
    if stale_pending:
        await conn.commit()
        logger.info("Отчёты пересчитаны под новое правило оплаты: %d", len(stale_pending))
    # v0.17.0: накопленный пересчёт статистики регионов — она хранится готовой
    # (region_stats), а пересчитывалась только по кнопке админа. После смены правила
    # в таблице лежат значения, посчитанные по старой логике (суточный заработок за
    # окно 24ч), поэтому пересчитываем на старте: иначе после деплоя админ увидел бы
    # старые числа до первого суточного цикла. Дальше цикл поддерживает их сам.
    # v0.22.2: имена колонок региональной статистики врали. troops_24h и
    # active_pilots_72h обещали окна времени (24 часа / 72 часа), а окна нет: это
    # «остаток» — сумма «всего» каждого пилота по его последнему одобренному отчёту,
    # и сколько пилотов этот отчёт сдали. «troops_total» читается как «всего сил»,
    # но новичок всё равно ждёт потока, поэтому смысл держится в докстринге
    # recompute_region_stats(), а не в имени колонки.
    _region_stats_cols = {r['name'] for r in await (await conn.execute(
        "PRAGMA table_info(region_stats)")).fetchall()}
    for _old, _new in (("troops_24h", "troops_total"),
                       ("active_pilots_72h", "pilots_count")):
        if _old in _region_stats_cols:
            await conn.execute(
                f"ALTER TABLE region_stats RENAME COLUMN {_old} TO {_new}")
    await conn.commit()
    _old_stats = await (await conn.execute(
        "SELECT COUNT(*) AS n FROM region_stats")).fetchone()
    if _old_stats and _old_stats['n']:
        try:
            await recompute_region_stats()
            logger.info("Статистика регионов пересчитана под новое правило")
        except Exception as e:
            logger.error("Не удалось пересчитать статистику регионов: %s", e)
    # v0.18.0: «Офицерский стек» выведен из игры — он был старой версией «Сержантской
    # трости» (⚔️2 без эффекта против ⚔️3 с оглушением). Странность была в том, что
    # предмет держался на сиде ensure_kvp_items(): удаление из БД не помогало, он
    # воскресал при каждом старте. Теперь сид переписан на трость, поэтому здесь
    # же убираем сам стек. Удаляем только если его никто не держит: сорванная
    # выдача хуже, чем лишний товар в каталоге — такой случай лучше разбирать руками.
    _stick = await (await conn.execute(
        "SELECT id FROM items WHERE name = 'Офицерский стек'")).fetchone()
    if _stick:
        _holders = await (await conn.execute(
            "SELECT COUNT(*) AS n FROM inventory WHERE item_id = ?",
            (_stick['id'],))).fetchone()
        if not _holders['n']:
            await conn.execute("DELETE FROM items WHERE id = ?", (_stick['id'],))
            logger.info("«Офицерский стек» удалён: заменён «Сержантской тростью»")
        else:
            logger.warning(
                "«Офицерский стек» остался в игре: %d шт. у игроков", _holders['n'])
    # Трость была продублирована в дропе босса курса (25%, добавлено админом вручную
    # в БД): из-за этого она фармилась повторно, без ограничения «раз за аккаунт».
    # Теперь единственный путь — 30% с босса прямо в коде курса (kvp.py), один раз.
    _cane = await (await conn.execute(
        "SELECT id FROM items WHERE name = ?", (KVP_CANE_NAME,))).fetchone()
    _cane_id = _cane['id'] if _cane else None
    _drops_fixed = 0
    for _enemy in await (await conn.execute(
            "SELECT id, drops FROM dungeon_enemies "
            "WHERE name = ? AND drops IS NOT NULL", ('Старший сержант',))).fetchall():
        try:
            _drops = json.loads(_enemy['drops'] or '[]')
        except (TypeError, ValueError):
            continue
        if not isinstance(_drops, list) or not _drops:
            continue
        _kept = [d for d in _drops
                 if not (isinstance(d, dict)
                         and ((_cane_id and d.get('item_id') == _cane_id)
                              or d.get('item') == KVP_CANE_NAME))]
        if len(_kept) != len(_drops):
            await conn.execute("UPDATE dungeon_enemies SET drops = ? WHERE id = ?",
                               (json.dumps(_kept, ensure_ascii=False), _enemy['id']))
            _drops_fixed += 1
    if _drops_fixed:
        await conn.commit()
        logger.info("Дроп «Сержантской трости» убран из врагов: %d", _drops_fixed)
    await _ensure_column(conn, "player_dungeon_run", "loot_nm", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "player_dungeon_run", "started_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    # «Аптечка» — это +AP (энергетик); лечит HP в данже «Малая настойка здоровья»
    await conn.execute("UPDATE items SET name = 'Энергетик', description = 'Восстанавливает силы: даёт +AP при использовании.' WHERE name = 'Аптечка'")
    await _ensure_column(conn, "users", "ap_restored_day", "TEXT DEFAULT NULL")
    await _ensure_column(conn, "users", "ap_restored_today", "INTEGER DEFAULT 0")
    # Дом Дуэлей: личный рейтинг и статистика поединков.
    await _ensure_column(conn, "users", "duel_rating", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "users", "duel_wins", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "users", "duel_losses", "INTEGER DEFAULT 0")
    # Время последней активности (epoch, сек). Обновляется middleware при каждом
    # апдейте игрока и используется для показа статуса онлайна в Доме Дуэлей.
    await _ensure_column(conn, "users", "last_active", "REAL DEFAULT 0")
    await _ensure_column(conn, "items", "damage", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "items", "heal", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "dungeon_enemies", "drops", "TEXT DEFAULT '[]'")
    await _ensure_column(conn, "dungeon_enemies", "image", "TEXT")
    await _ensure_column(conn, "dungeon_enemies", "poison_chance", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "dungeon_enemies", "poison_dmg", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "dungeon_enemies", "description", "TEXT")
    await _ensure_column(conn, "dungeon_enemies", "dodge", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "dungeon_enemies", "damage_min", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "dungeon_enemies", "damage_max", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "dungeon_enemies", "armor", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "dungeon_enemies", "dodge_chance", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "dungeon_enemies", "crit_chance", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "dungeon_enemies", "crit_mult", "REAL DEFAULT 1.5")
    await _ensure_column(conn, "dungeon_enemies", "abilities", "TEXT DEFAULT '[]'")
    await _ensure_column(conn, "forest_enemies", "armor", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "forest_enemies", "dodge_chance", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "forest_enemies", "crit_chance", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "forest_enemies", "crit_mult", "REAL DEFAULT 1.5")
    await _ensure_column(conn, "forest_enemies", "abilities", "TEXT DEFAULT '[]'")
    # v0.23.3: кровотечение у внешних врагов (волк в лесу и т.п.).
    await _ensure_column(conn, "forest_enemies", "bleed_chance", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "forest_enemies", "bleed_dmg", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "fishing_enemies", "bleed_chance", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "fishing_enemies", "bleed_dmg", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "fishing_enemies", "armor", "INTEGER DEFAULT 0")
    # v0.31.0: Железная копи — те же внешние колонки для mine_enemies.
    await _ensure_column(conn, "mine_enemies", "armor", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "mine_enemies", "dodge_chance", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "mine_enemies", "crit_chance", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "mine_enemies", "crit_mult", "REAL DEFAULT 1.5")
    await _ensure_column(conn, "mine_enemies", "abilities", "TEXT DEFAULT '[]'")
    await _ensure_column(conn, "mine_enemies", "bleed_chance", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "mine_enemies", "bleed_dmg", "INTEGER DEFAULT 0")
    # v0.37.0: Лесозаготовка — те же внешние колонки для logging_enemies
    # (яда змеи хватает полей bleed_* из CREATE TABLE, остальное — редактору).
    await _ensure_column(conn, "logging_enemies", "armor", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "logging_enemies", "dodge_chance", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "logging_enemies", "crit_chance", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "logging_enemies", "crit_mult", "REAL DEFAULT 1.5")
    await _ensure_column(conn, "logging_enemies", "abilities", "TEXT DEFAULT '[]'")
    # v0.38.0: единая система эффектов при ударе врага. Колонка хранит
    # JSON-массив [{"kind": "bleed", "chance": 25, "dmg": 4}, ...] у всех
    # врагов; legacy-колонки bleed_*/poison_*/frostbite_chance мигрируются
    # в неё при старте (_migrate_enemy_on_hit_effects) и больше не читаются.
    for _t in ("dungeon_enemies", "forest_enemies", "fishing_enemies",
               "mine_enemies", "logging_enemies"):
        await _ensure_column(conn, _t, "on_hit_effects", "TEXT DEFAULT NULL")
    # admin_tuned=1 в обычных врагах dungeon не должен мешать: миграции по дропам
    # (ensure_dungeon_enemy_drops / seed_kvp) запускаются только по admin_tuned>0
    await _ensure_column(conn, "dungeon_enemies", "admin_tuned", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "items", "cure_poison", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "locations", "preview_photo", "TEXT")
    await _ensure_column(conn, "locations", "photo_dawn", "TEXT")
    await _ensure_column(conn, "locations", "photo_day", "TEXT")
    await _ensure_column(conn, "locations", "photo_sunset", "TEXT")
    await _ensure_column(conn, "locations", "photo_night", "TEXT")
    # v0.15.22: счётчик входов в локацию (для анализа популярности аспектов)
    await _ensure_column(conn, "locations", "visits", "INTEGER DEFAULT 0")
    # v0.15.23: регенерация расходника — % от эффективного лечения, разливается
    # по ходам боя и затухает (см. regen_amounts в bot/handlers/dungeon.py).
    await _ensure_column(conn, "items", "regen", "INTEGER DEFAULT 0")
    # Подземелья: картинка входа по времени суток (как у локаций)
    await _ensure_column(conn, "dungeons", "photo_dawn", "TEXT")
    await _ensure_column(conn, "dungeons", "photo_day", "TEXT")
    await _ensure_column(conn, "dungeons", "photo_sunset", "TEXT")
    await _ensure_column(conn, "dungeons", "photo_night", "TEXT")
    # Картинки комнат-препятствий К.В.П. (вода/верёвка), задаются админом
    await _ensure_column(conn, "dungeons", "photo_water", "TEXT")
    await _ensure_column(conn, "dungeons", "photo_rope", "TEXT")
    # excluded=1 — рыбу убрали из водоёма через админа: пул её не показывает,
    # а стартовая синхронизация (ensure_water_fish) не возвращает её обратно.
    await _ensure_column(conn, "water_fish", "excluded", "INTEGER DEFAULT 0")
    # Рыбалка: выбранная игроком наживка ('worms'/'spider'/'none', '' = авто)
    await _ensure_column(conn, "users", "fishing_bait", "TEXT DEFAULT ''")
    # Позывной пилота (игровой ник, выставляется админом; показывается в карточке)
    await _ensure_column(conn, "users", "callsign", "TEXT")
    # Награды: картинка и процентные бонусы (в % к атаке/защите/уклонению/рыбалке и +HP)
    await _ensure_column(conn, "awards", "image", "TEXT")
    await _ensure_column(conn, "awards", "bonus_attack", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "awards", "bonus_defense", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "awards", "bonus_dodge", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "awards", "bonus_fishing", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "awards", "bonus_hp", "INTEGER DEFAULT 0")
    # v0.20.0: бонус к шансу критического удара (в процентах). Складывается
    # с базовым шансом по званию и с crit_chance снаряжения.
    await _ensure_column(conn, "awards", "bonus_crit", "INTEGER DEFAULT 0")
    # v0.18.2: экономические бонусы медалей — скидка в магазине (в %) и
    # снижение налога с отчёта (в процентных пунктах от ставки).
    await _ensure_column(conn, "awards", "bonus_shop_discount", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "awards", "bonus_report_tax", "INTEGER DEFAULT 0")
    # v0.18.13: денежные премии наград — разовая (при выдаче) и ежемесячная,
    # выплачиваются ТОЛЬКО из казны (treasury), никогда не создаются из воздуха.
    await _ensure_column(conn, "awards", "reward_nm", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "awards", "monthly_nm", "INTEGER DEFAULT 0")
    # v0.22.16: достижения. Строки awards выступают «уровнями» ачивки:
    # achievement_key/achievement_level связывают награду с DEF-уровнем,
    # bonus_json хранит точечные бонусы уровня (лечение, ОД, шанс лута/редкого,
    # урон по контексту, яд, наценку рынка и т.п.), которые нельзя вынести в
    # глобальные bonus_* — те применяются только в своих игровых точках.
    await _ensure_column(conn, "awards", "achievement_key", "TEXT DEFAULT NULL")
    await _ensure_column(conn, "awards", "achievement_level", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "awards", "bonus_json", "TEXT DEFAULT '{}'")
    # v0.32.1: второе фото в обращениях НИИ (до 2 скриншотов)
    await _ensure_column(conn, "nii_reports", "photo2_file_id", "TEXT DEFAULT NULL")
    # Формирования ВВС (редактор в штабе): поля добавляются на случай старой
    # схемы без них.
    await _ensure_column(conn, "wings", "num", "TEXT DEFAULT ''")
    await _ensure_column(conn, "wings", "abbr", "TEXT DEFAULT ''")
    await _ensure_column(conn, "wings", "name", "TEXT DEFAULT ''")
    await _ensure_column(conn, "wings", "callsign", "TEXT DEFAULT ''")
    await _ensure_column(conn, "wings", "emoji", "TEXT DEFAULT ''")
    await _ensure_column(conn, "wings", "sort_order", "INTEGER DEFAULT 0")
    # Счётчик водорослей (для «несварения»: >6 в сутки → запрет расходников на 24 ч)
    await _ensure_column(conn, "users", "seaweed_used_today", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "users", "seaweed_used_day", "TEXT DEFAULT NULL")
    # День последнего суточного восстановления ОД: рестарты бота посреди дня
    # не начисляют +100 ОД повторно, восстановление срабатывает раз в сутки.
    await _ensure_column(conn, "users", "ap_recovery_day", "TEXT DEFAULT NULL")
    # Счётчик бутылок пива (для состояний «пьян»/«очень пьян»)
    await _ensure_column(conn, "users", "beer_used_today", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "users", "beer_used_day", "TEXT DEFAULT NULL")
    await _ensure_column(conn, "items", "drink_effect", "TEXT DEFAULT NULL")
    await _ensure_column(conn, "users", "alcohol_weak_used_today", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "users", "alcohol_weak_used_day", "TEXT DEFAULT NULL")
    await _ensure_column(conn, "users", "alcohol_strong_used_today", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "users", "alcohol_strong_used_day", "TEXT DEFAULT NULL")
    # Спец-отдел: неверные попытки ввода кода и время блокировки покупок (бан на 24 ч)
    await _ensure_column(conn, "users", "special_fails_today", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "users", "special_blocked_until", "TEXT DEFAULT NULL")
    # Опросы: кто и когда закрыл (для архива закрытых голосований)
    await _ensure_column(conn, "polls", "closed_by", "INTEGER")
    await _ensure_column(conn, "polls", "closed_at", "TIMESTAMP")
    # Срок годности жареной рыбы (время истечения в инвентаре)
    await _ensure_column(conn, "inventory", "expires_at", "TIMESTAMP")
    # Данные растения в кадке при хранении в инвентаре (переезд / снятие)
    await _ensure_column(conn, "inventory", "plant_data", "TEXT")
    # Срок годности сырой (неприготовленной) рыбы: 4 дня с момента поимки.
    # У старых уловов expires_at пустой — они считаются свежими (фолбэк в коде).
    await _ensure_column(conn, "fish_catches", "expires_at", "TIMESTAMP")
    # Фонтан в парке: 1 восстановление ОД в сутки
    await _ensure_column(conn, "users", "fountain_used_day", "TEXT DEFAULT NULL")
    await _ensure_column(conn, "users", "fountain_used_today", "INTEGER DEFAULT 0")
    # Душевая в жилье: 1 восстановление ОД в сутки (душевая +25, ванна с душем +50)
    await _ensure_column(conn, "users", "shower_used_day", "TEXT DEFAULT NULL")
    # v0.41.2 Ф4б: Лампа Круговорота в личном жилье (генератор, не привязан к празднику)
    await _ensure_column(conn, "users", "lantern_medit_day", "TEXT DEFAULT NULL")
    await _ensure_column(conn, "users", "lantern_amber_at", "TEXT DEFAULT NULL")
    # v0.41.4: Древо Пламенного Круговорота (клан. расширение 'tree')
    await _ensure_column(conn, "clans", "tree_amber_at", "TEXT DEFAULT NULL")
    await conn.execute(FIRE_TREE_MEDIT_TABLE_SQL)
    await _ensure_column(conn, "users", "shower_used_today", "INTEGER DEFAULT 0")
    # Выкуп рыбы казной: суточный лимит НМ на игрока (FISH_TREASURY_DAILY_LIMIT)
    await _ensure_column(conn, "users", "fish_sold_day", "TEXT DEFAULT NULL")
    await _ensure_column(conn, "users", "fish_sold_today", "INTEGER DEFAULT 0")
    # v0.18.15: счётчик попыток сбора грибов с момента последней встречи кабана.
    await _ensure_column(conn, "users", "forest_attempts_since_boar", "INTEGER DEFAULT 0")
    # v0.23.3: отдельный счётчик для гарантии волка (не реже, чем раз в 24 поиска).
    await _ensure_column(conn, "users", "forest_attempts_since_wolf", "INTEGER DEFAULT 0")
    # v0.31.0: счётчик попыток добычи руды с последней встречи с Летучей мышью
    # (гарантия встречи раз в MINE_BAT_PITY_TARGET попыток).
    await _ensure_column(conn, "users", "mine_attempts_since_bat", "INTEGER DEFAULT 0")
    # v0.37.0: счётчики попыток рубки Лесозаготовки с последней встречи
    # со Змеёй и с Неясытью (у каждого врага свой, как у кабана и волка).
    await _ensure_column(conn, "users", "logging_attempts_since_snake", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "users", "logging_attempts_since_owl", "INTEGER DEFAULT 0")
    # v0.18.16: выкуп грибов казной — суточный лимит НМ на игрока
    # (FOREST_SOLD_DAILY_LIMIT). Счётчик сбрасывается при смене суток МСК.
    await _ensure_column(conn, "users", "forest_sold_day", "TEXT DEFAULT NULL")
    await _ensure_column(conn, "users", "forest_sold_today", "INTEGER DEFAULT 0")
    # v0.18.17: сезонные картинки локаций (JSON {сезон: {время суток: file_id}}).
    # Задаются в админ-редакторе локаций, показываются по календарю (см. utils.helpers).
    await _ensure_column(conn, "locations", "season_photos", "TEXT DEFAULT NULL")
    # v0.18.18: отдельная картинка опушки леса (грибы). Намеренно не картинка
    # входа в лес: опушка — самостоятельная картинка, задаётся админом отдельно.
    await _ensure_column(conn, "locations", "glade_photo", "TEXT DEFAULT NULL")
    await _ensure_column(conn, "locations", "clearing_photo", "TEXT DEFAULT NULL")
    # v0.32.0: отдельная картинка 1-го уровня шахт (Железная копь) — по аналогии
    # с опушкой/прогалиной леса: вход в копь и спуск внутрь — разные картинки.
    await _ensure_column(conn, "locations", "mine_level_photo", "TEXT DEFAULT NULL")
    # v0.32.1: внутренняя картинка Городских складов (отдельно от превью)
    await _ensure_column(conn, "locations", "storage_photo", "TEXT DEFAULT NULL")
    # v0.37.1: внутренняя картинка Лесозаготовки (фон окна рубки) — по аналогии
    # с опушкой/прогалиной леса: задаётся в картинках локации «Лес», хранится на
    # строке леса; без неё окно берёт сезонный локальный файл (city/logging).
    await _ensure_column(conn, "locations", "logging_photo", "TEXT DEFAULT NULL")
    # v0.18.18: лес разделён на две зоны — опушка (glade) и лесная поляна
    # (clearing). Пул грибов каждой зоны — в forest_zone_pool, сам каталог грибов
    # (forest_mushrooms) остаётся общим: один и тот же гриб может попадать и на
    # опушку, и на поляну, но со своим весом в каждой зоне.
    await _ensure_column(conn, "forest_mushrooms", "zone", "TEXT DEFAULT 'clearing'")
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS forest_zone_pool (
            area TEXT NOT NULL DEFAULT 'clearing',
            mushroom_id INTEGER NOT NULL,
            chance INTEGER DEFAULT 10,
            PRIMARY KEY (area, mushroom_id)
        )
    """)
    # Настройки зон леса: цена поиска в ОД, допуск туристов, кабан, открытость.
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS forest_zones (
            key TEXT PRIMARY KEY,
            title TEXT,
            ap_cost INTEGER DEFAULT 4,
            allow_tourists INTEGER DEFAULT 0,
            boar_enabled INTEGER DEFAULT 0,
            boar_chance INTEGER DEFAULT 8,
            boar_every INTEGER DEFAULT 12,
            enabled INTEGER DEFAULT 1
        )
    """)
    # Общие настройки леса (выкуп казной) — key/value, чтобы не плодить колонки.
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS forest_settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    # Встроенные расширения жилья (например, кухня в студии): embedded=1 — не возвращается
    # в инвентарь при переезде и не может быть снята вручную.
    await _ensure_column(conn, "housing_slots", "embedded", "INTEGER DEFAULT 0")
    # Счётчик установок расширений: первая в доме — бесплатно, далее перепланировка платная.
    await _ensure_column(conn, "player_housing", "expansions_installed", "INTEGER DEFAULT 0")
    # v0.19.0: жизнь опроса ограничена POLL_MAX_DAYS суток. closes_at проставляется
    # при создании опроса (create_poll), поэтому уже созданные опросы получают срок
    # от своего created_at, а не от даты деплоя. created_at в polls кладётся
    # CURRENT_TIMESTAMP (UTC, 'YYYY-MM-DD HH:MM:SS') — прибавляем к нему сутки.
    await _ensure_column(conn, "polls", "closes_at", "TIMESTAMP")
    await conn.execute(
        "UPDATE polls SET closes_at = datetime(created_at, ?) "
        "WHERE is_active = 1 AND (closes_at IS NULL OR closes_at = '')",
        (f"+{config.POLL_MAX_DAYS} days",)
    )
    # Архив опросов библиотеки: попадает всё, что вытеснено из меню голосования
    # (старше POLL_VISIBLE новейших). is_archived — флаг «в архиве», archived_day —
    # дата (МСК, 'YYYY-MM-DD') ухода в архив: по ней раздел «Опросы» в библиотеке
    # группирует записи по дням.
    await _ensure_column(conn, "polls", "is_archived", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "polls", "archived_day", "TEXT DEFAULT ''")
    # Речь представителя: обращения к городу (лимит REP_SPEECH_PER_DAY в сутки).
    # created_day — ключ суток МСК для суточного лимита, edited — правил ли
    # представитель уже опубликованное обращение.
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS rep_speeches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_day TEXT NOT NULL DEFAULT '',
            edited INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)
    # Убраны из магазина товары без функционала (вернуть можно через админ-добавление товаров)
    await conn.execute("UPDATE items SET is_available = 0 WHERE name IN "
                       "('Ангар-бокс','Металл','Кристаллы','Медаль «Крыло»','Топливо','Ремкомплект')")
    # Лётный шлем и Кислородная маска — только броня, без урона.
# Если колонка armor добавилась после сида (значение осталось 0), восстанавливаем значения.
    await conn.execute("UPDATE items SET damage = 0 WHERE name IN ('Лётный шлем','Кислородная маска')")
    await conn.execute("UPDATE items SET armor = 4 WHERE name = 'Лётный шлем' AND armor = 0")
    await conn.execute("UPDATE items SET armor = 2 WHERE name = 'Кислородная маска' AND armor = 0")
    # Базовые статусы иерархии: Пилот — гражданин (0), Турист — гость (-10).
    # Старые записи Пилота, которым ранее могли поставить высокий уровень, возвращаем к 0.
    await conn.execute("UPDATE statuses SET sort_order = 2 WHERE access_tag = 'pilot'")
    await conn.execute("UPDATE statuses SET sort_order = -10 WHERE access_tag = 'tourist'")
    # v0.19.12: кабану поднято HP до 40. Правки админа (admin_tuned=1) не трогаем.
    await conn.execute(
        "UPDATE forest_enemies SET hp = ? WHERE key = 'boar' AND hp < ? AND admin_tuned = 0",
        (FOREST_BOAR_HP, FOREST_BOAR_HP))
    # v0.10.0: рынок (слоты продажи + лицензия) и налог на жильё
    await _ensure_column(conn, "dungeons", "is_training", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "users", "market_license_expires", "TEXT DEFAULT NULL")
    await _ensure_column(conn, "users", "callsign_free_used", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "market_fish", "base_price", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "player_housing", "tax_last_check", "TEXT DEFAULT NULL")
    await _ensure_column(conn, "player_housing", "tax_unpaid_months", "INTEGER DEFAULT 0")
    # v0.12.0: расширение Крысиного Подвала — 2 этажа, кровотечение и обморожение.
    # Кровотечение (bleed): урон каждый ход, спадает через N ходов. Обморожение:
    # снижает лечение, снимается напитками (cure_frostbite) или само через N ходов.
    await _ensure_column(conn, "dungeon_enemies", "bleed_chance", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "dungeon_enemies", "bleed_dmg", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "dungeon_enemies", "frostbite_chance", "INTEGER DEFAULT 0")
    # items.cure_frostbite=1 — напиток снимает обморожение в бою подземелья.
    await _ensure_column(conn, "items", "cure_frostbite", "INTEGER DEFAULT 0")
    # dungeons.rooms_map — число обычных комнат по этажам (JSON-массив, e.g. [9,8]).
    # Босс этажа встречается, когда room_number >= rooms_map[floor-1].
    await _ensure_column(conn, "dungeons", "rooms_map", "TEXT")
    # v0.13.2: предметы, которые можно выставлять на рыночную витрину
    # (рынок), а не только продавать скупщику. Не выставленные — только скупщик.
    await _ensure_column(conn, "items", "market_ok", "INTEGER DEFAULT 0")
    # v0.13.3: тип улова — 'fish' (рыба: вес, порча) или 'resource' (находка:
    # без срока годности, ингредиент). Также тип на записи водоёма.
    await _ensure_column(conn, "fish_catches", "kind", "TEXT DEFAULT 'fish'")
    await _ensure_column(conn, "water_fish", "kind", "TEXT DEFAULT 'fish'")
    # v0.22.18: супер-редкая рыба — ловится только пилотами с достижением
    # «Бывалый» 4-го уровня (bonus super_rare). Помечается админом.
    await _ensure_column(conn, "water_fish", "super_rare", "INTEGER DEFAULT 0")
    # v0.13.7: как называется выросшее растение в кадке (для предметов-семечек).
    # Задаётся админом в мастере создания товара (шаг для категории "seeds").
    await _ensure_column(conn, "items", "plant_name", "TEXT")
    # v0.13.7: разовый backfill — у уже существующего семечка яблони
    # название растения в кадке = «Яблоня».
    await conn.execute(
        "UPDATE items SET plant_name = 'Яблоня' "
        "WHERE category = 'seeds' AND name = 'Яблочное семечко' AND plant_name IS NULL")
    # v0.14.3: особые эффекты оружия (на врага в бою подземелья).
    # weapon_effect: 'poison' | 'bleed' | 'frostbite' | 'stun' | NULL (нет эффекта);
    # weapon_effect_chance: шанс срабатывания при попадании, %;
    # для DoT (poison/bleed/frostbite) weapon_effect_dmg — урон за ход;
    # для 'stun' weapon_effect_dmg — штраф к точности врага, % (шанс его промаха).
    await _ensure_column(conn, "items", "weapon_effect", "TEXT")
    await _ensure_column(conn, "items", "weapon_effect_chance", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "items", "weapon_effect_dmg", "INTEGER DEFAULT 0")
    # v0.41.2 Огненный Лабиринт (Фаза 4): экип-бонусы лечения/уклонения.
    # heal_bonus_pct — % к лечению расходников; dodge_bonus — +пп к уклонению.
    await _ensure_column(conn, "items", "heal_bonus_pct", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "items", "dodge_bonus", "INTEGER DEFAULT 0")
    # v0.41.3: переименование трёх праздничных рыб (скрытые лут-предметы, а не
    # магазинные) — для БД, засеянной ещё со старыми именами v0.41.2.
    await conn.execute(
        "UPDATE items SET name = 'Спектральная Латимерия' WHERE name = 'Призрачный Осетр'")
    await conn.execute(
        "UPDATE items SET name = 'Скелетная Арована' WHERE name = 'Костяная Душа'")
    await conn.execute(
        "UPDATE items SET name = 'Пылающая Душа' WHERE name = 'Пламенный Карп'")
    # v0.41.3: праздничные предметы не видны в магазине (только лут/крафт);
    # лов/рынок/скупка не трогаются — правила «как у обычного улова» остаются.
    await conn.execute(
        "UPDATE items SET is_available = 0 WHERE name IN ("
        "'Спектральная Латимерия', 'Скелетная Арована', 'Пылающая Душа',"
        "'Пучок сена', 'Ветка дерева', 'Рецепт: Тыквенный пирог',"
        "'Рецепт: Обжигающая трость', 'Леденец языков пламени',"
        "'Кусочек тыквенного пирога', 'Семечко тыквы', 'Тыква',"
        "'Перо ворона', 'Моток железной проволоки', 'Ручное пламенеющее устройство',"
        "'Сахар', 'Яйца', 'Огненный венец', 'Плащ Памяти',"
        "'Перчатки стража посевов', 'Вилы', 'Обжигающая трость',"
        "'Лампа Круговорота', 'Пламя Памяти', 'Эссенция Памяти')")
    # v0.15.0: авиакрыло пилота ('1'/'2'/'3' → метка в utils/wings.py; NULL — нет крыла).
    await _ensure_column(conn, "users", "wing", "TEXT")
    # v0.21.0: users.legioner — «легионерный» флаг. НЕ в иерархии статусов:
    # кеп доступа и запрет голосования считаются по нему, а не по sort_order.
    await _ensure_column(conn, "users", "legioner", "INTEGER DEFAULT 0")
    # v0.13.3: рыба (предметы категории fishing) выставляется на рынок по
    # умолчанию. Разовое обновление для уже существующих предметов.
    cur = await conn.execute(
        "SELECT value FROM settings WHERE key = 'mig_v0133_fish_market_ok'")
    if not (await cur.fetchone()):
        await conn.execute("UPDATE items SET market_ok = 1 WHERE category = 'fishing'")
        await conn.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES ('mig_v0133_fish_market_ok', '1')")
    await conn.commit()
    await ensure_base_statuses()
    # v0.15.24: авто-статусы по званиям — разовый бэкфилл по текущим войскам/званиям.
    mig_statuses = await (await conn.execute(
        "SELECT value FROM settings WHERE key = 'mig_rank_statuses'")).fetchone()
    if not mig_statuses:
        await backfill_rank_statuses()
        await conn.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES ('mig_rank_statuses', '1')")
        await conn.commit()
    # v0.18.14: кумулятивная выдача статусов по званию — догонка. Раньше выдавался
    # статус только за текущее звание, и игроки, перешагнувшие закреплённую ступень
    # (Ефрейтор → «Пилот 2 класса») до задней следующей, теряли статус безвозвратно.
    mig_statuses_v2 = await (await conn.execute(
        "SELECT value FROM settings WHERE key = 'mig_rank_statuses_v2'")).fetchone()
    if not mig_statuses_v2:
        await backfill_rank_statuses()
        await conn.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES ('mig_rank_statuses_v2', '1')")
        await conn.commit()
    # v0.15.17: единая шкала статусов — «Пилот» → «Пилот 2 класса», «VIP» → «Ас».
    # Старые теги удаляются, игроки и товары переводятся на новые.
    for old_tag, new_tag in (("pilot", "pilot2"), ("vip", "ace"), ("WHR", "keeper")):
        old = await (await conn.execute(
            "SELECT id FROM statuses WHERE access_tag = ?", (old_tag,))).fetchone()
        if not old:
            continue
        new = await (await conn.execute(
            "SELECT id FROM statuses WHERE access_tag = ?", (new_tag,))).fetchone()
        if new:
            await conn.execute(
                "UPDATE user_statuses SET status_id = ? WHERE status_id = ?",
                (new["id"], old["id"]))
            await conn.execute("DELETE FROM statuses WHERE id = ?", (old["id"],))
        else:
            await conn.execute(
                "UPDATE statuses SET access_tag = ?, name = ?, sort_order = 100 WHERE id = ?",
                (new_tag, "Хранитель", old["id"]))
    await conn.execute(
        "UPDATE items SET required_status = 'pilot2' WHERE required_status = 'pilot'")
    await conn.execute(
        "UPDATE items SET required_status = 'master_pilot' WHERE required_status = 'vip'")
    await conn.execute(
        "UPDATE buildings SET required_status = 'pilot2' WHERE required_status = 'pilot'")
    # v0.15.18: жильё с параметрами в самом предмете — тип (housing_type) и число
    # слотов расширений (housing_slots; NULL = число слота по умолчанию типа).
    # В player_housing хранится отображаемое название дома (housing_label, например
    # «Особняк №1») и индивидуальный лимит слотов (housing_slots).
    await _ensure_column(conn, "items", "housing_type", "TEXT")
    await _ensure_column(conn, "items", "housing_slots", "INTEGER")
    await _ensure_column(conn, "player_housing", "housing_label", "TEXT")
    await _ensure_column(conn, "player_housing", "housing_slots", "INTEGER")
    # v0.15.28: «только лут» — предмет существует как дроп врагов и не попадает
    # в витрину магазина (get_available_items/visible_items его скрывают).
    await _ensure_column(conn, "items", "loot_only", "INTEGER DEFAULT 0")
    # v0.23.3: player_dmg_min/max — рудимент: урон пилота считается общей
    # боевой моделью (utils/combat_model), из строки врага он не берётся.
    # Убираем колонки у старых БД (у свежих их уже нет в CREATE TABLE).
    for _enemy_table in ("forest_enemies", "fishing_enemies"):
        await _drop_column(conn, _enemy_table, "player_dmg_min")
        await _drop_column(conn, _enemy_table, "player_dmg_max")
    await conn.commit()
    await seed_locations(conn)
    # Снятые с игры предметы (T-Меч, T-Броня, учебные машины) — полное удаление.
    await purge_retired_items()
    # v0.18.13: казна платит награды → исторические выплаты значков списываем
    # с казны задним числом; формирования ВВС читаем в кэш штаба/профиля.
    await load_wings_cache()
    # v0.35.0: формирование «Резерв» — все пилоты (с гражданством) без крыла
    # переводятся в 'reserve'; при снятии крыла set_wing(None) тоже пишет 'reserve'.
    mig_reserve = await (await conn.execute(
        "SELECT value FROM settings WHERE key = 'mig_reserve_wing'")).fetchone()
    if not mig_reserve:
        # Граждане (user_statuses с access_tag пилотского уровня и выше, кроме
        # легионеров и туристов) — wing IS NULL → 'reserve'.
        await conn.execute("""
            UPDATE users SET wing = 'reserve'
            WHERE wing IS NULL
              AND user_id IN (
                  SELECT us.user_id FROM user_statuses us
                  JOIN statuses st ON st.id = us.status_id
                  WHERE st.access_tag IN ('pilot2','pilot1','veteran','master_pilot','ace')
              )
              AND COALESCE(legioner, 0) = 0
        """)
        await conn.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES ('mig_reserve_wing', '1')")
        await conn.commit()
    await _balance_legacy_booklet_payouts()
    # v0.22.8: единые игровые сутки (10:00 МСК) — прижать «опережающие» ключи.
    await _normalize_daily_keys()
    # v0.38.0: legacy-колонки эффектов врагов (bleed_*/poison_*/frostbite_*)
    # переносим в on_hit_effects (JSON). Идемпотентно, по NULL-строкам.
    await _migrate_enemy_on_hit_effects()
    # v0.38.1: ребаланс водохранилища (цены форели + веса пула).
    await _migrate_reservoir_balance()
    # Клан-холл: фото готового здания (добавляет клан, админ проставляет)
    await _ensure_column(conn, "clan_buildings", "building_photo_file_id", "TEXT")
    await _ensure_column(conn, "firelab_enemies", "on_hit_effects", "TEXT DEFAULT NULL")
    await _ensure_column(conn, "firelab_enemies", "armor", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "fire_lab_sessions", "enemy_json", "TEXT DEFAULT NULL")
    await _ensure_column(conn, "fire_lab_sessions", "effects_json", "TEXT DEFAULT NULL")
    await _ensure_column(conn, "fire_lab_sessions", "boss_encounters", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "fire_lab_sessions", "fish_used", "INTEGER DEFAULT 0")
    # Праздничная рыбалка (Колодец): отмеченные виды рыбы пилота (UNIQUE).
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS user_fire_fish (
            user_id INTEGER NOT NULL,
            item_id INTEGER NOT NULL,
            marked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, item_id)
        )
    """)
    await conn.commit()


async def _migrate_reservoir_balance():
    """v0.38.1: ребаланс подземного водохранилища.

    Цены «Светящаяся форель» (sell 600→450, price 1200→900) и «Жареный форель»
    (sell 1000→600, price 2000→1200), плюс веса пула (сом 62→70, угорь 33→25).
    Обновляет ТОЛЬКО строки с прежними значениями (не трогает админские правки
    на другие числа), идемпотентно при каждом старте.
    """
    conn = await get_db()
    price_fix = [
        ("Светящаяся форель", 1200, 900, 600, 450),
        ("Жареный форель", 2000, 1200, 1000, 600),
    ]
    for name, old_price, new_price, old_sell, new_sell in price_fix:
        await conn.execute(
            "UPDATE items SET price = ?, sell_price = ? "
            "WHERE name = ? AND price = ? AND sell_price = ?",
            (new_price, new_sell, name, old_price, old_sell))
    weight_fix = [("Мерцающий сом", 62, 70), ("Искрящийся угорь", 33, 25)]
    for name, old_w, new_w in weight_fix:
        item = await get_item_by_name(name)
        if item:
            await conn.execute(
                "UPDATE water_fish SET day_weight = ?, night_weight = ? "
                "WHERE water = 'reservoir' AND item_id = ? "
                "AND day_weight = ? AND night_weight = ?",
                (new_w, new_w, item['id'], old_w, old_w))
    await conn.commit()


async def _migrate_enemy_on_hit_effects():
    """v0.38.0: миграция legacy-колонок эффектов врагов в on_hit_effects.

    Заполняет только строки, где on_hit_effects IS NULL (идемпотентно при
    каждом старте). logging_enemies: bleed_* — это боевой яд змеи, поэтому
    мигрирует в kind='poison' (боевая семантика лесозаготовки).
    """
    conn = await get_db()
    frostbite_rounds = config.ON_HIT_EFFECTS["frostbite"].get("default_rounds", 4)
    plans = [
        ("dungeon_enemies", "bleed", ("bleed_chance", "bleed_dmg"), None),
        ("dungeon_enemies", "poison", ("poison_chance", "poison_dmg"), None),
        ("dungeon_enemies", "frostbite", ("frostbite_chance", None), frostbite_rounds),
        ("forest_enemies", "bleed", ("bleed_chance", "bleed_dmg"), None),
        ("fishing_enemies", "bleed", ("bleed_chance", "bleed_dmg"), None),
        ("mine_enemies", "bleed", ("bleed_chance", "bleed_dmg"), None),
        ("logging_enemies", "poison", ("bleed_chance", "bleed_dmg"), None),
    ]
    changed = False
    for table in ("dungeon_enemies", "forest_enemies", "fishing_enemies",
                  "mine_enemies", "logging_enemies"):
        cursor = await conn.execute(
            f"SELECT * FROM {table} WHERE on_hit_effects IS NULL")
        rows = await cursor.fetchall()
        for row in rows:
            keys = row.keys()
            effects = []
            for plan_table, kind, cols, rounds in plans:
                if plan_table != table or cols[0] not in keys:
                    continue
                chance = int(row[cols[0]] or 0)
                if chance <= 0:
                    continue
                eff = {"kind": kind, "chance": chance}
                if cols[1] and cols[1] in keys and int(row[cols[1]] or 0) > 0:
                    eff["dmg"] = int(row[cols[1]])
                if rounds:
                    eff["rounds"] = rounds
                effects.append(eff)
            await conn.execute(
                f"UPDATE {table} SET on_hit_effects = ? WHERE id = ?",
                (json.dumps(effects, ensure_ascii=False), row['id']))
            changed = True
    if changed:
        await conn.commit()


async def seed_locations(conn):
    """Засеивает базовые локации города (Ратуша, Библиотека) как пример управляемого доступа.

    Ратуша и Библиотека по умолчанию: режим 'all' (всем) + состояние «пьян»
    блокирует вход (сохраняем текущее поведение).
    """
    base = [
        ("townhall", "Ратуша", "Публичное здание города, где собираются пилоты и решаются вопросы города.",
         "all", None, ["пьян"], "city/rathaus"),
        ("library", "Библиотека", "Хранилище знаний Нордхайма. Вход по читательскому билету.",
         "all", None, ["пьян"], "city/library"),
        ("park", "Городской парк", "Тенистые аллеи, пруд и статуи. Открыт для всех — и для пилотов, и для туристов.",
         "all", None, ["пьян"], "city/park"),
        ("gossmi", "ГосСМИ", "Медиацентр Нордхайма. Здесь корреспонденты готовят выпуски городских новостей.",
         "all", None, ["пьян"], "city/media"),
        ("bank", "Банк", "НОРДБАНК — финансовое сердце Нордхайма: счета, переводы и казна. Для туристов счёт ограничен 200 НМ.",
         "all", None, ["пьян"], "city/bank"),
        ("kvp", "Курс выживания", "Курс выживания для пилотов. Набор испытаний для пилотов ВВС Нордхайма.",
         "all", None, ["пьян"], "city/kvp"),
        ("hq", "Штаб ВВС", "Командный центр военно-воздушных сил Нордхайма. Отсюда отдаются приказы авиакрыльям и комплектуется состав.",
         "all", None, ["пьян"], "city/hq"),
        ("contracts", "Доска контрактов", "Доска штаба сухопутных войск: контракты на зачистку подземелий. Вход по пилотскому удостоверению.",
         "all", None, ["пьян"], "city/contracts"),
        ("duel_house", "Дом Дуэлей", "Арена чести для пилотов: поединки один на один «зона на зону». Вход с пилота второго класса.",
         "min", "pilot2", ["пьян"], "city/duel_house"),
        ("nii", "НИИ Северной Кибернетики и кремниевых систем", "НИИ Северной Кибернетики и кремниевых систем: здесь пилоты оставляют жалобы и запросы на доработку бота.",
         "all", None, ["пьян"], "city/nii"),
        ("forest", "Лес на окраине", "Тёмный еловый лес на окраине Аркхольма. Здесь водятся грибы и не только: говорят, по опушкам бродит злобный кабан.",
         "all", None, ["пьян"], "city/forest"),
        ("mine", "Железная копи", "Тёплые штольни железных копей Нордхайма. Здесь добывают руду — и не только.",
         "min", "pilot1", ["пьян"], "city/mine"),
        ("storage", "Городские склады", "Складские ангары Аркхольма: сюда свозят ресурсы, выкупленные казной у пилотов. Вход с «Пилота 1 класса».",
         "min", "pilot1", ["пьян"], "city/storage"),
        # Доступ в МВД — не через access_mode/required_status, а хардкодом в
        # location_enter (как ГосСМИ и Штаб ВВС): роли МВД/Вице-доминуса/
        # Представителя/Хранителя либо статус «Хранитель» (keeper).
        ("mvd", "Здание МВД", "Здание Министерства внутренних дел Нордхайма. Здесь хранится архив сданных отчётов и ведётся проверка пилотской отчётности.",
         "all", None, ["пьян"], "city/mvd"),
    ]
    for key, name, desc, mode, req_status, blocking, preview in base:
        await conn.execute(
            "INSERT OR IGNORE INTO locations (key, name, description, access_mode, required_status, blocking_states, preview_photo) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (key, name, desc, mode, req_status, json.dumps(blocking, ensure_ascii=False), preview)
        )
    # Разовая миграция текста описания локации К.В.П. (не трогаем ручные правки админа).
    await conn.execute(
        "UPDATE locations SET description = ? WHERE key = 'kvp' AND description = ?",
        ("Курс выживания для пилотов. Набор испытаний для пилотов ВВС Нордхайма.",
         "Тренировочный полигон для пилотов. 8 комнат с препятствиями и босс — Старший сержант.")
    )
    # v0.23.3: Дом Дуэлей открыт с «Пилота 2 класса» — снижаем требование
    # (раньше pilot1) и правим текст, но только если строка ещё со старыми
    # значениями (ручные правки админа не затираем).
    await conn.execute(
        "UPDATE locations SET required_status = 'pilot2' "
        "WHERE key = 'duel_house' AND required_status = 'pilot1'")
    await conn.execute(
        "UPDATE locations SET description = ? WHERE key = 'duel_house' AND description = ?",
        ("Арена чести для пилотов: поединки один на один «зона на зону». Вход с пилота второго класса.",
         "Арена чести для пилотов: поединки один на один «зона на зону». Вход с пилота первого класса.")
    )
    await conn.commit()


# ============ УДАЛЕНИЕ СНЯТЫХ С ИГРЫ ПРЕДМЕТОВ ============

# Предметы, полностью выведенные из игры: товары, инвентарь, снаряжение,
# дропы и сделки с ними очищаются при миграции.
RETIRED_ITEMS = ["Учебный истребитель", "Стандартный пулемёт", "T-Меч", "T-Броня",
                 "Бутылка пива"]


async def purge_retired_items():
    """Убирает снятые с игры предметы из всех таблиц и колонок.

    Вызывается на старте: удаляет сами записи items и все ссылки на них
    (инвентарь, снаряжение, дропы, очереди производства, сделки, здания).
    """
    conn = await get_db()
    if not RETIRED_ITEMS:
        return False
    placeholders = ",".join("?" * len(RETIRED_ITEMS))
    cursor = await conn.execute(
        f"SELECT id FROM items WHERE name IN ({placeholders})", RETIRED_ITEMS
    )
    ids = [row["id"] for row in await cursor.fetchall()]
    if not ids:
        return False
    id_ph = ",".join("?" * len(ids))

    for table, col in (("inventory", "item_id"),
                       ("player_dungeon_inventory", "item_id"),
                       ("dungeon_rewards", "item_id"),
                       ("dungeon_items", "item_id"),
                       ("resource_sources", "item_id"),
                       ("fish_catches", "item_id"),
                       ("production_queue", "recipe_item_id")):
        await conn.execute(f"DELETE FROM {table} WHERE {col} IN ({id_ph})", ids)
    await conn.execute(f"UPDATE trades SET from_item_id = NULL WHERE from_item_id IN ({id_ph})", ids)
    await conn.execute(f"UPDATE trades SET to_item_id = NULL WHERE to_item_id IN ({id_ph})", ids)
    await conn.execute(f"UPDATE buildings SET production_item_id = NULL WHERE production_item_id IN ({id_ph})", ids)

    # Снаряжение игроков: любые слоты equipment, ссылающиеся на удаляемые предметы.
    cur = await conn.execute("SELECT user_id, equipment FROM users WHERE equipment IS NOT NULL AND equipment != '{}'")
    for row in await cur.fetchall():
        try:
            eq = json.loads(row["equipment"])
        except (ValueError, TypeError):
            continue
        changed = False
        for slot in ("weapon", "armor", "weapon_aux", "head", "body", "hands", "legs",
                     "potion1", "potion2", "potion3"):
            if eq.get(slot) in ids:
                eq.pop(slot, None)
                changed = True
        if changed:
            await conn.execute(
                "UPDATE users SET equipment = ? WHERE user_id = ?",
                (json.dumps(eq, ensure_ascii=False), row["user_id"])
            )

    await conn.execute(f"DELETE FROM items WHERE id IN ({id_ph})", ids)
    await conn.commit()
    return True


async def _ensure_column(conn, table: str, column: str, coltype: str) -> bool:
    """Добавляет колонку в таблицу, если её ещё нет.

    Возвращает True, если колонка была только что создана (миграция), иначе False.
    """
    cursor = await conn.execute(f"PRAGMA table_info({table})")
    cols = [row['name'] for row in await cursor.fetchall()]
    if column not in cols:
        await conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {coltype}")
        await conn.commit()
        return True
    return False


async def _drop_column(conn, table: str, column: str) -> bool:
    """Удаляет колонку из таблицы, если она есть (нужен SQLite ≥ 3.35).

    Возвращает True, если колонка была удалена. На старых SQLite (или если
    колонка задействована в индексе/ограничении) молча оставляет как есть —
    колонка-рудимент просто перестаёт использоваться кодом.
    """
    cursor = await conn.execute(f"PRAGMA table_info({table})")
    cols = [row['name'] for row in await cursor.fetchall()]
    if column not in cols:
        return False
    try:
        await conn.execute(f"ALTER TABLE {table} DROP COLUMN {column}")
        await conn.commit()
        return True
    except Exception:
        return False


async def add_user(user_id: int, username: str, first_name: str, last_name: str):
    conn = await get_db()
    await conn.execute("""
        INSERT INTO users (user_id, username, first_name, last_name, nordmarks)
        VALUES (?, ?, ?, ?, 10)
        ON CONFLICT(user_id) DO UPDATE SET
            username = excluded.username,
            first_name = excluded.first_name,
            last_name = excluded.last_name
    """, (user_id, username, first_name, last_name))
    await conn.commit()


def _load_state_effects(state_col: str, state_effects: str) -> dict:
    """Парсит state_effects в dict {ключ состояния: effects}.

    Поддерживает legacy плоский формат {"applied_at", "minutes", ...},
    где ключ состояния берётся из столбца state.
    """
    try:
        data = json.loads(state_effects) if state_effects else {}
    except (ValueError, TypeError):
        data = {}
    if not isinstance(data, dict):
        data = {}
    if "applied_at" in data:
        key = state_col if state_col and state_col != "нормально" else ""
        if key:
            return {key: data}
        return {}
    return {k: v for k, v in data.items() if isinstance(v, dict)}


def _state_col_value(effects: dict) -> str:
    keys = list(effects.keys())
    return ", ".join(keys) if keys else "нормально"


async def _refresh_user_states(user_id: int) -> dict:
    """Читает состояния игрока, снимает протухшие и возвращает {ключ: effects}."""
    conn = await get_db()
    cursor = await conn.execute("SELECT state, state_effects FROM users WHERE user_id = ?", (user_id,))
    row = await cursor.fetchone()
    if not row:
        return {}
    effects = _load_state_effects(row['state'], row['state_effects'])
    now = datetime.now()
    changed = False
    for key in list(effects.keys()):
        eff = effects[key] or {}
        try:
            applied = datetime.strptime(eff['applied_at'], "%Y-%m-%d %H:%M:%S")
            minutes = int(eff.get('minutes', 0))
        except (ValueError, TypeError, KeyError):
            continue
        if applied + timedelta(minutes=minutes) <= now:
            del effects[key]
            changed = True
            await conn.execute(
                "INSERT INTO state_log (user_id, old_state, new_state, reason, caused_by) "
                "VALUES (?, ?, ?, ?, ?)",
                (user_id, key, "нормально", f"срок действия истёк ({key})", eff.get('caused_by'))
            )
    if changed:
        await conn.execute(
            "UPDATE users SET state = ?, state_effects = ? WHERE user_id = ?",
            (_state_col_value(effects), json.dumps(effects, ensure_ascii=False), user_id)
        )
        await conn.commit()
    return effects


async def get_user(user_id: int):
    """Возвращает игрока словарём с учётом протухших состояний.

    При активном состоянии «истощён» ap_max заменяется на лимит истощения (90).
    user['state'] — строка состояний через запятую, user['state_keys'] — список.
    """
    from config import AP_EXHAUSTED_MAX_AP
    conn = await get_db()
    cursor = await conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = await cursor.fetchone()
    if not row:
        return None
    user = dict(row)
    effects = await _refresh_user_states(user_id)
    user['state'] = _state_col_value(effects)
    user['state_effects'] = json.dumps(effects, ensure_ascii=False)
    user['state_keys'] = list(effects.keys())
    if 'истощён' in effects:
        user['ap_max'] = AP_EXHAUSTED_MAX_AP
    return user


async def update_user(user_id: int, **kwargs):
    conn = await get_db()
    sets = ", ".join(f"{k} = ?" for k in kwargs)
    values = list(kwargs.values()) + [user_id]
    await conn.execute(f"UPDATE users SET {sets} WHERE user_id = ?", values)
    await conn.commit()


async def _maybe_money_achievement(user_id: int):
    """Ачивка «Золото» растёт вверх от единовременного максимума баланса."""
    conn = await get_db()
    cursor = await conn.execute("SELECT nordmarks FROM users WHERE user_id = ?", (user_id,))
    row = await cursor.fetchone()
    if row:
        await set_achievement_progress(user_id, "money", row['nordmarks'] or 0)


async def add_nordmarks(user_id: int, amount: int, tx_type: str, description: str = ""):
    conn = await get_db()
    await conn.execute("UPDATE users SET nordmarks = nordmarks + ? WHERE user_id = ?", (amount, user_id))
    await conn.execute(
        "INSERT INTO transactions (to_user, amount, tx_type, description) VALUES (?, ?, ?, ?)",
        (user_id, amount, tx_type, description)
    )
    await conn.commit()
    await _maybe_money_achievement(user_id)


async def remove_nordmarks(user_id: int, amount: int, tx_type: str, description: str = ""):
    conn = await get_db()
    await conn.execute("UPDATE users SET nordmarks = nordmarks - ? WHERE user_id = ?", (amount, user_id))
    await conn.execute(
        "INSERT INTO transactions (from_user, amount, tx_type, description) VALUES (?, ?, ?, ?)",
        (user_id, amount, tx_type, description)
    )
    await conn.commit()
    await _maybe_money_achievement(user_id)


async def transfer_nordmarks(from_user: int, to_user: int, amount: int, description: str = ""):
    conn = await get_db()
    await conn.execute("UPDATE users SET nordmarks = nordmarks - ? WHERE user_id = ?", (amount, from_user))
    await conn.execute("UPDATE users SET nordmarks = nordmarks + ? WHERE user_id = ?", (amount, to_user))
    await conn.execute(
        "INSERT INTO transactions (from_user, to_user, amount, tx_type, description) VALUES (?, ?, ?, ?, ?)",
        (from_user, to_user, amount, "transfer", description)
    )
    await conn.commit()
    await _maybe_money_achievement(from_user)
    await _maybe_money_achievement(to_user)


async def add_ap(user_id: int, amount: int, reason: str = None):
    """Добавить ОД. При состоянии «истощён» потолок — AP_EXHAUSTED_MAX_AP (90).

    reason — причина изменения (пишется в ap_log для аудита экономики).
    """
    from config import AP_EXHAUSTED_MAX_AP
    if amount <= 0:
        return
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT ap, ap_max FROM users WHERE user_id = ?", (user_id,)
    )
    row = await cursor.fetchone()
    if not row:
        return
    effects = await _refresh_user_states(user_id)
    cap = AP_EXHAUSTED_MAX_AP if 'истощён' in effects else row['ap_max']
    added = min(amount, cap - row['ap'])
    if added <= 0:
        return
    await log_ap_change(user_id, added, reason)
    await conn.execute(
        "UPDATE users SET ap = ap + ? WHERE user_id = ?",
        (added, user_id)
    )
    await conn.commit()


async def remove_ap(user_id: int, amount: int, reason: str = None) -> bool:
    conn = await get_db()
    cursor = await conn.execute("SELECT ap FROM users WHERE user_id = ?", (user_id,))
    row = await cursor.fetchone()
    if not row or row['ap'] < amount:
        return False
    await log_ap_change(user_id, -amount, reason)
    await conn.execute("UPDATE users SET ap = ap - ? WHERE user_id = ?", (amount, user_id))
    await conn.commit()
    return True


async def _normalize_daily_keys():
    """Прижать суточные ключи *_day к текущим игровым суткам, если они «впереди».

    Старый код писал в *_day календарную дату: UTC (смена в 03:00 МСК) для ОД,
    расходников, алкоголя и фонтана, МСК (смена в 00:00) для рыбы/леса. После
    перехода на игровые сутки 10:00 МСК в окне между старой и новой границей
    записанное значение оказывается на день «позднее» нового ключа, и счётчик
    читается как неиспользованный — пилот получил бы второй заход по лимиту.

    Прижатие меняет только день, счёт сохраняет, а в 10:00 счётчик обнулится по
    обычному правилу. Идемпотентно (вызывается при каждом старте) и дешёво:
    UPDATE без WHERE по строкам с «будущей» датой почти ничего не трогает.
    """
    day = today_report_day()
    conn = await get_db()
    for col in ("ap_recovery_day", "ap_restored_day", "seaweed_used_day",
                "fountain_used_day", "shower_used_day", "fish_sold_day",
                "forest_sold_day",
                "alcohol_weak_used_day", "alcohol_strong_used_day"):
        await conn.execute(
            f"UPDATE users SET {col} = ? WHERE {col} IS NOT NULL AND {col} > ?",
            (day, day))
    await conn.commit()


async def daily_ap_recovery():
    """Суточное восстановление ОД — раз в сутки, в 10:00 МСК.

    Начисляет AP_DAILY_RECOVERY (100 ОД) до потолка ap_max; для состояния
    «истощён» — AP_EXHAUSTED_DAILY_RECOVERY (75 ОД) до AP_EXHAUSTED_MAX_AP (90).
    Срабатывает только если день не совпадает с users.ap_recovery_day: рестарты
    бота посреди дня не раздают ОД повторно. Счётчики (ap_restored_today,
    seaweed_used_today, fountain_used_today) обнуляются при смене суток.
    Каждое начисление пишется в ap_log.

    Сутки здесь — ИГРОВЫЕ (today_report_day, 10:00 МСК), как у отчётов: ОД,
    лимиты расходников, фонтан, рыба/лес, стена, опросы и алкоголь обновляются
    в одну и ту же минуту вместе с выплатами.
    """
    from config import (AP_DAILY_RECOVERY, AP_EXHAUSTED_DAILY_RECOVERY, AP_EXHAUSTED_MAX_AP)
    today = today_report_day()
    conn = await get_db()

    cursor = await conn.execute(
        "SELECT user_id, ap, ap_max, state, ap_recovery_day FROM users"
    )
    rows = await cursor.fetchall()
    for row in rows:
        exhausted = 'истощён' in (row['state'] or '')
        cap = AP_EXHAUSTED_MAX_AP if exhausted else row['ap_max']
        rec = AP_EXHAUSTED_DAILY_RECOVERY if exhausted else AP_DAILY_RECOVERY
        prev_day = row['ap_recovery_day']
        if prev_day == today:
            continue
        before = row['ap']
        new_ap = min(cap, before + rec)
        if new_ap == before:
            await conn.execute(
                "UPDATE users SET ap_recovery_day = ? WHERE user_id = ?",
                (today, row['user_id'])
            )
            continue
        reason = "суточное восстановление ОД"
        if exhausted:
            reason = "суточное восстановление ОД (истощён)"
        await log_ap_change(row['user_id'], new_ap - before, reason)
        await conn.execute(
            "UPDATE users SET ap = ?, ap_recovery_day = ? WHERE user_id = ?",
            (new_ap, today, row['user_id'])
        )
    await conn.commit()

    # Обнуление суточных счётчиков. Ключ — те же игровые сутки, что и у отчётов
    # (10:00 МСК → 10:00 МСК), поэтому ВСЕ лимиты переезжают вместе с выплатами.
    # Раньше здесь стоял date('now') (календарь UTC = 03:00 МСК) и обнулялись только
    # 4 счётчика из 9 — алкоголь, лес и спец-отдел сбрасывались кто во что горазд.
    # Ленивые проверки (fish_sale_daily_left, can_use_fountain и др.) обнуляются и
    # сами по несовпадению ключа: блок нужен, чтобы счётчик обнулился даже если
    # пилот в этот день в раздел не заходил.
    await conn.execute("""
        UPDATE users SET
            ap_restored_today = CASE WHEN ap_restored_day = ? THEN ap_restored_today ELSE 0 END,
            ap_restored_day = ?,
            seaweed_used_today = CASE WHEN seaweed_used_day = ? THEN seaweed_used_today ELSE 0 END,
            seaweed_used_day = ?,
            fountain_used_today = CASE WHEN fountain_used_day = ? THEN fountain_used_today ELSE 0 END,
            fountain_used_day = ?,
            shower_used_today = CASE WHEN shower_used_day = ? THEN shower_used_today ELSE 0 END,
            shower_used_day = ?,
            fish_sold_today = CASE WHEN fish_sold_day = ? THEN fish_sold_today ELSE 0 END,
            fish_sold_day = ?,
            forest_sold_today = CASE WHEN forest_sold_day = ? THEN forest_sold_today ELSE 0 END,
            forest_sold_day = ?,
            alcohol_weak_used_today = CASE WHEN alcohol_weak_used_day = ? THEN alcohol_weak_used_today ELSE 0 END,
            alcohol_weak_used_day = ?,
            alcohol_strong_used_today = CASE WHEN alcohol_strong_used_day = ? THEN alcohol_strong_used_today ELSE 0 END,
            alcohol_strong_used_day = ?,
            special_fails_today = 0
    """, (today,) * 16)
    await conn.commit()


async def add_item(name: str, description: str, price: int, sell_price: int,
                   rarity: int, category: str, stock: int, added_by: int,
                   photo_file_id: str = None, ap_cost: int = 0,
                   production_time_hours: int = 0, produced_by: int = None,
                   damage: int = 0, heal: int = 0, armor: int = 0,
                   crit_chance: float = 0, crit_mult: float = 0,
                   drink_effect: str = None, equip_slot: str = None,
                   market_ok: int = None, plant_name: str = None,
                   weapon_effect: str = None,
                   weapon_effect_chance: int = 0,
                   weapon_effect_dmg: int = 0,
                   housing_type: str = None,
                   housing_slots: int = None,
                   regen: int = 0,
                   required_status: str = None,
                   loot_only: int = 0):
    conn = await get_db()
    # v0.13.3: рыба (категория fishing) по умолчанию выставляется на рынок;
    # у остальных предметов — только скупщик, пока админ не включит флаг.
    if market_ok is None:
        market_ok = 1 if category == "fishing" else 0
    cursor = await conn.execute(
        """INSERT INTO items (name, description, photo_file_id, price, sell_price,
           rarity, category, stock, added_by, ap_cost, production_time_hours, produced_by, damage, heal, armor, crit_chance, crit_mult, drink_effect, equip_slot, market_ok, plant_name,
           weapon_effect, weapon_effect_chance, weapon_effect_dmg, housing_type, housing_slots, regen, required_status, loot_only)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (name, description, photo_file_id, price, sell_price, rarity, category,
         stock, added_by, ap_cost, production_time_hours, produced_by, damage, heal, armor,
         crit_chance, crit_mult,
         drink_effect, equip_slot, market_ok, plant_name,
         weapon_effect or None, weapon_effect_chance, weapon_effect_dmg,
         housing_type, housing_slots, regen, required_status, loot_only)
    )
    await conn.commit()
    return cursor.lastrowid


async def get_item(item_id: int):
    conn = await get_db()
    cursor = await conn.execute("SELECT * FROM items WHERE id = ?", (item_id,))
    return await cursor.fetchone()


async def get_available_items(category: str = None, rarity: int = None):
    conn = await get_db()
    query = "SELECT * FROM items WHERE is_available = 1 AND IFNULL(loot_only, 0) = 0"
    params = []
    if category:
        query += " AND category = ?"
        params.append(category)
    if rarity:
        query += " AND rarity = ?"
        params.append(rarity)
    query += " ORDER BY rarity, price"
    cursor = await conn.execute(query, params)
    return await cursor.fetchall()


async def get_all_items():
    """Все существующие предметы (включая распроданные и скрытые) для Хранилища."""
    conn = await get_db()
    cursor = await conn.execute("SELECT * FROM items ORDER BY category, name")
    return await cursor.fetchall()


async def get_items_by_category(category: str):
    """Все предметы в конкретной категории (для хранилища)."""
    if category == "all":
        return await get_all_items()
    conn = await get_db()
    cursor = await conn.execute("SELECT * FROM items WHERE category = ? ORDER BY name", (category,))
    return await cursor.fetchall()


async def count_items_by_category():
    conn = await get_db()
    cursor = await conn.execute("SELECT category, COUNT(*) AS c FROM items GROUP BY category")
    rows = await cursor.fetchall()
    return {r['category']: r['c'] for r in rows}


async def update_item(item_id: int, **kwargs):
    conn = await get_db()
    sets = ", ".join(f"{k} = ?" for k in kwargs)
    values = list(kwargs.values()) + [item_id]
    await conn.execute(f"UPDATE items SET {sets} WHERE id = ?", values)
    await conn.commit()


# Допустимые типы действия напитка (items.drink_effect).
# None/'' = не напиток. 'none' = безалкогольный напиток без действия на состояние.
DRINK_EFFECTS = (
    "alcohol_weak", "alcohol_strong", "indigestion",
    "exhaustion", "indigestion_exhaustion", "none",
)


async def consume_drink(user_id: int, item_id: int):
    """Применяет действие напитка (после списания предмета из инвентаря).

    Возвращает (ok, message).
    - alcohol_weak:  3-я за сутки → «пьян», 6-я → «очень пьян»;
    - alcohol_strong: 1-я → «пьян», 2-я → «очень пьян»;
    - indigestion / exhaustion / indigestion_exhaustion: состояния на сутки/2 суток;
    - none: без действия на состояние.
    """
    from config import (ALCOHOL_WEAK_DRUNK_LIMIT, ALCOHOL_WEAK_VERY_DRUNK_LIMIT,
                        ALCOHOL_STRONG_DRUNK_LIMIT, ALCOHOL_STRONG_VERY_DRUNK_LIMIT,
                        DRUNK_MINUTES, VERY_DRUNK_MINUTES)
    from utils.states import apply_state_to
    from utils.helpers import row_get

    item = await get_item(item_id)
    if not item:
        return False, "Предмет не найден."
    effect = row_get(item, "drink_effect")
    if effect is None:
        return False, "Это не напиток с эффектом."
    if effect not in DRINK_EFFECTS:
        return False, "Неизвестный тип напитка."

    user = await get_user(user_id)
    if not user:
        return False, "Ты не зарегистрирован."
    name = item["name"]
    today = today_report_day()
    conn = await get_db()

    if effect in ("alcohol_weak", "alcohol_strong"):
        if effect == "alcohol_strong":
            drunk_limit, very_limit = ALCOHOL_STRONG_DRUNK_LIMIT, ALCOHOL_STRONG_VERY_DRUNK_LIMIT
            cnt_col, day_col = "alcohol_strong_used_today", "alcohol_strong_used_day"
            glass = "🥃"
            kind = "крепкий алкоголь"
        else:
            drunk_limit, very_limit = ALCOHOL_WEAK_DRUNK_LIMIT, ALCOHOL_WEAK_VERY_DRUNK_LIMIT
            cnt_col, day_col = "alcohol_weak_used_today", "alcohol_weak_used_day"
            glass = "🍺"
            kind = "слабоалкогольный напиток"
        used = int(user.get(cnt_col) or 0)
        if user.get(day_col) != today:
            used = 0
        used += 1
        await conn.execute(
            f"UPDATE users SET {cnt_col} = ?, {day_col} = ? WHERE user_id = ?",
            (used, today, user_id))
        await conn.commit()

        if used >= very_limit:
            await apply_state_to(user_id, "очень пьян",
                                 minutes=VERY_DRUNK_MINUTES,
                                 reason=f"выпит {kind} «{name}» ({used} шт./сутки)")
            return True, (
                f"{glass} Ты выпил «{name}». "
                f"🥴 Состояние «Очень пьян» на {VERY_DRUNK_MINUTES} минут! "
                f"Зелья недоступны, вход во все здания закрыт, в бою атака −50%."
            )
        if used >= drunk_limit:
            await apply_state_to(user_id, "пьян",
                                 minutes=DRUNK_MINUTES,
                                 reason=f"выпит {kind} «{name}» ({used} шт./сутки)")
            return True, (
                f"{glass} Ты выпил «{name}». "
                f"🍺 Состояние «Пьян» на {DRUNK_MINUTES} минут. "
                f"В Ратушу и Библиотеку не пускают, в бою атака −20%."
            )
        return True, (
            f"{glass} Ты выпил «{name}». "
            f"Приятного аппетита!"
        )

    # Безалкогольные эффекты.
    parts = []
    if effect in ("indigestion", "indigestion_exhaustion"):
        await apply_state_to(user_id, "несварение",
                             reason=f"выпит напиток «{name}»")
        parts.append("🤢 Наступило «Несварение»: расходники недоступны (24 часа).")
    if effect in ("exhaustion", "indigestion_exhaustion"):
        await apply_state_to(user_id, "истощён",
                             reason=f"выпит напиток «{name}»")
        parts.append("🥵 Наступило «Истощён»: суточное восстановление ОД сильно снижено (2 суток).")
    if parts:
        return True, f"Ты выпил «{name}».\n\n" + "\n\n".join(parts)
    return True, f"Ты выпил «{name}». Приятного аппетита!"


async def delete_item(item_id: int):
    conn = await get_db()
    await conn.execute("DELETE FROM items WHERE id = ?", (item_id,))
    await conn.commit()


async def delete_item_completely(item_id: int):
    """Полное удаление предмета из игры: сама запись items + все ссылки.

    Чистит инвентари, снаряжение игроков, дропы врагов, награды подземелий,
    источники ресурсов, уловы рыбы, лоты рынка, виды рыбы в водоёмах,
    очереди производства и активные сделки. Возвращает словарь с числом
    удалённых записей по каждой таблице (для отчёта в Хранилище).
    """
    conn = await get_db()
    report = {}

    for table, col in (("inventory", "item_id"),
                       ("player_dungeon_inventory", "item_id"),
                       ("dungeon_rewards", "item_id"),
                       ("dungeon_items", "item_id"),
                       ("resource_sources", "item_id"),
                       ("fish_catches", "item_id"),
                       ("market_items", "item_id"),
                       ("market_fish", "item_id"),
                       ("water_fish", "item_id"),
                       ("production_queue", "recipe_item_id")):
        cur = await conn.execute(f"SELECT COUNT(*) AS c FROM {table} WHERE {col} = ?", (item_id,))
        row = await cur.fetchone()
        n = row["c"] if row else 0
        if n:
            await conn.execute(f"DELETE FROM {table} WHERE {col} = ?", (item_id,))
        report[table] = n

    # Сделки и здания: предмет просто «выпадает» из записи.
    cur = await conn.execute("SELECT COUNT(*) AS c FROM trades WHERE from_item_id = ? OR to_item_id = ?",
                             (item_id, item_id))
    row = await cur.fetchone()
    trades_n = row["c"] if row else 0
    if trades_n:
        await conn.execute("UPDATE trades SET from_item_id = NULL WHERE from_item_id = ?", (item_id,))
        await conn.execute("UPDATE trades SET to_item_id = NULL WHERE to_item_id = ?", (item_id,))
    report["trades"] = trades_n
    cur = await conn.execute("SELECT COUNT(*) AS c FROM buildings WHERE production_item_id = ?", (item_id,))
    row = await cur.fetchone()
    b_n = row["c"] if row else 0
    if b_n:
        await conn.execute("UPDATE buildings SET production_item_id = NULL WHERE production_item_id = ?", (item_id,))
    report["buildings"] = b_n

    # Снаряжение игроков: любые слоты equipment, ссылающиеся на предмет.
    eq_n = 0
    cur = await conn.execute("SELECT user_id, equipment FROM users WHERE equipment IS NOT NULL AND equipment != '{}'")
    for row in await cur.fetchall():
        try:
            eq = json.loads(row["equipment"])
        except (ValueError, TypeError):
            continue
        changed = False
        for slot in ("weapon", "armor", "weapon_aux", "head", "body", "hands", "legs",
                     "potion1", "potion2", "potion3"):
            if eq.get(slot) == item_id:
                eq.pop(slot, None)
                changed = True
        if changed:
            await conn.execute(
                "UPDATE users SET equipment = ? WHERE user_id = ?",
                (json.dumps(eq, ensure_ascii=False), row["user_id"])
            )
            eq_n += 1
    report["equipment"] = eq_n

    # Дропы врагов: JSON-списки с item_id-записью.
    drops_n = 0
    cur = await conn.execute("SELECT id, drops FROM dungeon_enemies WHERE drops IS NOT NULL AND drops != '[]'")
    for row in await cur.fetchall():
        try:
            dlist = json.loads(row["drops"])
        except (ValueError, TypeError):
            continue
        if not isinstance(dlist, list):
            continue
        new_drops = [d for d in dlist
                     if not (isinstance(d, dict) and d.get("item_id") is not None
                             and int(d.get("item_id", 0)) == item_id)]
        if len(new_drops) != len(dlist):
            await conn.execute("UPDATE dungeon_enemies SET drops = ?, admin_tuned = 1 WHERE id = ?",
                               (json.dumps(new_drops, ensure_ascii=False), row["id"]))
            drops_n += 1
    report["enemy_drops"] = drops_n

    await conn.execute("DELETE FROM items WHERE id = ?", (item_id,))
    await conn.commit()
    return report


async def add_inventory_item(user_id: int, item_id: int, quantity: int = 1, expires_at: str = None):
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT quantity, expires_at FROM inventory WHERE user_id = ? AND item_id = ?",
        (user_id, item_id)
    )
    row = await cursor.fetchone()
    if row:
        # У одной стопки — ранний срок истечения (минимальный из добавленных).
        new_exp = row['expires_at']
        if expires_at:
            new_exp = min(str(row['expires_at']), str(expires_at)) if row['expires_at'] else str(expires_at)
        await conn.execute(
            "UPDATE inventory SET quantity = quantity + ?, expires_at = ? WHERE user_id = ? AND item_id = ?",
            (quantity, new_exp, user_id, item_id)
        )
    else:
        await conn.execute(
            "INSERT INTO inventory (user_id, item_id, quantity, expires_at) VALUES (?, ?, ?, ?)",
            (user_id, item_id, quantity, expires_at)
        )
    await conn.commit()
    # Хук «Чтящий Предков» (Фаза 4): любой путь получения компонента проверяется.
    try:
        cur = await conn.execute("SELECT name FROM items WHERE id = ?", (item_id,))
        it = await cur.fetchone()
        nm = it['name'] if it else None
        if nm and (nm in FIRE_KEEPER_GEAR_NAMES
                   or nm == getattr(config, "FIRE_PUMPKIN_SEED_NAME", "")
                   or nm == getattr(config, "FIRE_LAB_RECIPE_NAME", "")):
            lvl, anm, _prev = await check_fire_keeper(user_id)
            if lvl:
                await log_activity(user_id, "firelab",
                                   f"Достижение «{anm}» — набор собран")
    except Exception:
        pass


async def remove_inventory_item(user_id: int, item_id: int, quantity: int = 1) -> bool:
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?",
        (user_id, item_id)
    )
    row = await cursor.fetchone()
    if not row or row['quantity'] < quantity:
        return False
    if row['quantity'] == quantity:
        await conn.execute(
            "DELETE FROM inventory WHERE user_id = ? AND item_id = ?",
            (user_id, item_id)
        )
    else:
        await conn.execute(
            "UPDATE inventory SET quantity = quantity - ? WHERE user_id = ? AND item_id = ?",
            (quantity, user_id, item_id)
        )
    await conn.commit()
    return True


async def get_inventory(user_id: int):
    conn = await get_db()
    cursor = await conn.execute("""
        SELECT i.*, inv.quantity FROM inventory inv
        JOIN items i ON inv.item_id = i.id
        WHERE inv.user_id = ? AND inv.quantity > 0
        ORDER BY i.category, i.rarity DESC
    """, (user_id,))
    return await cursor.fetchall()


async def get_inventory_item(user_id: int, item_id: int):
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT * FROM inventory WHERE user_id = ? AND item_id = ?",
        (user_id, item_id)
    )
    return await cursor.fetchone()


async def get_inventory_plant_data(user_id: int, item_id: int) -> dict | None:
    """Данные растения (plant_data) из строки инвентаря или None."""
    row = await get_inventory_item(user_id, item_id)
    if not row:
        return None
    raw = row.get("plant_data") if hasattr(row, "get") else None
    if raw:
        try:
            return json.loads(raw)
        except Exception:
            pass
    return None


async def set_inventory_plant_data(user_id: int, item_id: int, plant_data: dict | None):
    """Сохранить / очистить plant_data в строке инвентаря."""
    conn = await get_db()
    val = json.dumps(plant_data, ensure_ascii=False) if plant_data else None
    await conn.execute(
        "UPDATE inventory SET plant_data = ? WHERE user_id = ? AND item_id = ?",
        (val, user_id, item_id)
    )
    await conn.commit()


async def get_inventory_expiry(user_id: int, item_id: int):
    """Срок годности предмета в инвентаре (секунды эпохи) или None."""
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT expires_at FROM inventory WHERE user_id = ? AND item_id = ?",
        (user_id, item_id)
    )
    row = await cursor.fetchone()
    return row['expires_at'] if row else None


async def process_item_use(user_id: int, item_id: int) -> tuple:
    item = await get_item(item_id)
    if not item:
        return False, "Предмет не найден"

    inv_item = await get_inventory_item(user_id, item_id)
    if not inv_item or inv_item['quantity'] < 1:
        return False, "У тебя нет этого предмета"

    if item['category'] == 'consumable':
        from utils.states import consumables_blocked
        from utils.helpers import row_get

        user = await get_user(user_id)
        if not user:
            return False, "Пользователь не найден"
        state_keys = user.get('state_keys') or []

        # Состояния, блокирующие расходники («несварение», «очень пьян»).
        blocked_by = consumables_blocked(state_keys)
        if blocked_by:
            if "очень пьян" in blocked_by:
                return False, (
                    "🥴 Ты слишком пьян, чтобы что-то применять. "
                    "Зелья и расходники станут доступны, когда «очень пьян» пройдёт (6 часов)."
                )
            return False, (
                "🤢 Несварение: пищеварение на паузе. "
                "Расходники нельзя применять ещё сутки."
            )

        # v0.38.0: боевые эффекты врага (оглушение и далее) тоже запрещают
        # расходники, пока активны в текущем бою.
        from utils import onhit as onhit_mod
        battle_block = onhit_mod.consumables_blocked_by_battle(user_id)
        if battle_block:
            return False, battle_block

        # Напиток с действием: пиво и прочие пьются где угодно
        # (+10 HP засчитывается в бою подземелья отдельным путём).
        if row_get(item, 'drink_effect'):
            ok = await remove_inventory_item(user_id, item_id, 1)
            if not ok:
                return False, "Не удалось списать напиток."
            return await consume_drink(user_id, item_id)

        if item['heal'] > 0:
            return False, "Это зелье можно применить только в бою подземелья 💊"

        if item['ap_cost'] > 0:
            from config import (AP_DAILY_RESTORE_LIMIT,
                                AP_EXHAUSTED_MINUTES, AP_EXHAUSTED_DAILY_RECOVERY, AP_EXHAUSTED_MAX_AP,
                                SEAWEED_DAILY_LIMIT, DIGESTIVE_UPSET_MINUTES)

            if 'истощён' in state_keys:
                return False, (
                    "🥵 Ты истощён и не можешь восстанавливать ОД через расходники "
                    f"в ближайшие 2 суток.\nВосстановление: {AP_EXHAUSTED_DAILY_RECOVERY} ОД/сутки, "
                    f"максимум {AP_EXHAUSTED_MAX_AP} ОД."
                )

            today = today_report_day()
            restored_today = user.get('ap_restored_today') or 0
            if user.get('ap_restored_day') != today:
                restored_today = 0
            remaining = AP_DAILY_RESTORE_LIMIT - restored_today
            if remaining <= 0:
                return False, (
                    f"🥵 Лимит восстановления ОД за сутки исчерпан ({AP_DAILY_RESTORE_LIMIT} ОД). "
                    f"Восстановление продолжится в новые сутки."
                )

            # Водоросли: считаем дневное применение → несварение при превышении лимита.
            is_seaweed = item['name'] == "Кусочек водорослей"
            seaweed_used = 0
            if is_seaweed:
                seaweed_used = user.get('seaweed_used_today') or 0
                if user.get('seaweed_used_day') != today:
                    seaweed_used = 0
                if seaweed_used >= SEAWEED_DAILY_LIMIT:
                    return False, (
                        f"🤢 Сегодня ты уже съел {seaweed_used} водорослей (лимит {SEAWEED_DAILY_LIMIT}). "
                        f"Наступило несварение на сутки."
                    )

            amount = min(item['ap_cost'], remaining)
            await remove_inventory_item(user_id, item_id, 1)
            await add_ap(user_id, amount, reason=f"расходник «{item['name']}»")
            restored_today += amount
            conn = await get_db()
            if is_seaweed:
                seaweed_used += 1
                await conn.execute(
                    "UPDATE users SET ap_restored_today = ?, ap_restored_day = ?, "
                    "seaweed_used_today = ?, seaweed_used_day = ? WHERE user_id = ?",
                    (restored_today, today, seaweed_used, today, user_id)
                )
            else:
                await conn.execute(
                    "UPDATE users SET ap_restored_today = ?, ap_restored_day = ? WHERE user_id = ?",
                    (restored_today, today, user_id)
                )
            await conn.commit()

            # Водоросли: на 6-й штуке наступает несварение на сутки.
            if is_seaweed and seaweed_used >= SEAWEED_DAILY_LIMIT:
                await set_user_state(
                    user_id, "несварение", DIGESTIVE_UPSET_MINUTES, user_id,
                    f"Съедено {seaweed_used} водорослей за сутки (лимит {SEAWEED_DAILY_LIMIT})"
                )
                return True, (
                    f"Ты использовал {item['name']} и получил +{amount} AP!\n"
                    f"🤢 Ты съел {seaweed_used} водорослей за сегодня — наступило несварение на сутки. "
                    f"Расходники недоступны. Продолжай завтра!"
                )

            if restored_today >= AP_DAILY_RESTORE_LIMIT:
                await set_user_state(
                    user_id, "истощён", AP_EXHAUSTED_MINUTES, user_id,
                    f"Лимит восстановления ОД за сутки ({AP_DAILY_RESTORE_LIMIT}) исчерпан"
                )
                return True, (
                    f"Ты использовал {item['name']} и получил +{amount} AP!\n"
                    f"⚠️ Лимит восстановления ОД за сутки ({AP_DAILY_RESTORE_LIMIT}) исчерпан — "
                    f"наступило состояние «истощён» на 2 суток.\n"
                    f"Восстановление: {AP_EXHAUSTED_DAILY_RECOVERY} ОД/сутки, максимум {AP_EXHAUSTED_MAX_AP} ОД."
                )
            if is_seaweed:
                left_seaweed = max(0, SEAWEED_DAILY_LIMIT - seaweed_used)
                return True, (
                    f"Ты использовал {item['name']} и получил +{amount} AP! "
                    f"Водорослей сегодня: {seaweed_used}/{SEAWEED_DAILY_LIMIT} "
                    f"(ещё {left_seaweed} до несварения)."
                )
            return True, (
                f"Ты использовал {item['name']} и получил +{amount} AP! "
                f"Осталось восстановить ОД сегодня: {AP_DAILY_RESTORE_LIMIT - restored_today}."
            )

        await remove_inventory_item(user_id, item_id, 1)
        return True, f"Ты использовал {item['name']}!"

    if item['category'] == 'recipes':
        return await learn_recipe_from_item(user_id, item_id)

    return False, "Этот предмет нельзя использовать так"


async def create_trade(from_user: int, to_user: int, from_item_id: int, from_item_qty: int,
                       from_nordmarks: int, to_item_id: int, to_item_qty: int, to_nordmarks: int):
    conn = await get_db()
    cursor = await conn.execute("""
        INSERT INTO trades (from_user, to_user, from_item_id, from_item_qty, from_nordmarks,
                           to_item_id, to_item_qty, to_nordmarks)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (from_user, to_user, from_item_id, from_item_qty, from_nordmarks, to_item_id, to_item_qty, to_nordmarks))
    await conn.commit()
    trade_id = cursor.lastrowid
    await log_activity(from_user, "trade_create", f"Предложил обмен #{trade_id} игроку {to_user}")
    return trade_id


async def update_trade(trade_id: int, status: str):
    conn = await get_db()
    await conn.execute("UPDATE trades SET status = ? WHERE id = ?", (status, trade_id))
    await conn.commit()
    trade = await get_trade(trade_id)
    if not trade:
        return
    if status == "accepted":
        await log_activity(trade['from_user'], "trade_accepted", f"Обмен #{trade_id} принят")
        await log_activity(trade['to_user'], "trade_accepted", f"Обмен #{trade_id} принят")
    elif status == "declined":
        await log_activity(trade['to_user'], "trade_declined", f"Обмен #{trade_id} отклонён")


async def get_pending_trades(user_id: int):
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT * FROM trades WHERE (from_user = ? OR to_user = ?) AND status = 'pending'",
        (user_id, user_id)
    )
    return await cursor.fetchall()


async def get_trade(trade_id: int):
    conn = await get_db()
    cursor = await conn.execute("SELECT * FROM trades WHERE id = ?", (trade_id,))
    return await cursor.fetchone()


async def create_poll(admin_id: int, question: str, options: str):
    """Создать опрос. Срок закрытия (closes_at) — POLL_MAX_DAYS суток от сейчас (UTC,
    как created_at). Опрос не закрыл автор — закроется сам, см. close_expired_polls."""
    from datetime import datetime, timedelta, timezone
    from config import POLL_MAX_DAYS
    conn = await get_db()
    now_utc = datetime.now(timezone.utc)
    closes_at = (now_utc + timedelta(days=POLL_MAX_DAYS)).strftime("%Y-%m-%d %H:%M:%S")
    cursor = await conn.execute(
        "INSERT INTO polls (admin_id, question, options, created_at, closes_at) "
        "VALUES (?, ?, ?, ?, ?)",
        (admin_id, question, options, now_utc.strftime("%Y-%m-%d %H:%M:%S"), closes_at)
    )
    await conn.commit()
    return cursor.lastrowid


async def get_polls_created_today(admin_id: int) -> int:
    """Сколько опросов создал админ за текущие игровые сутки (10:00 МСК)."""
    conn = await get_db()
    cursor = await conn.execute(
        f"SELECT COUNT(*) AS cnt FROM polls WHERE admin_id = ? "
        f"AND {_report_day('created_at')} = ?",
        (admin_id, today_report_day())
    )
    row = await cursor.fetchone()
    return row['cnt'] if row else 0


# ============ АРХИВ ОПРОСОВ И АВТОЗАКРЫТИЕ ============

def _poll_today_key() -> str:
    """Ключ текущих игровых суток (10:00 МСК) — день ухода опроса в архив."""
    return today_report_day()


async def get_visible_polls(limit: int = None):
    """Опросы, которые висят в меню голосования: новейшие POLL_VISIBLE из неархивных.

    Закрытые среди них тоже возвращаются — в меню они помечены 🔒, чтобы ушедший
    из голосования опрос не исчезал из поля зрения сразу.
    """
    from config import POLL_VISIBLE
    conn = await get_db()
    n = limit if limit is not None else POLL_VISIBLE
    cursor = await conn.execute(
        "SELECT * FROM polls WHERE COALESCE(is_archived, 0) = 0 "
        "ORDER BY id DESC LIMIT ?", (n,)
    )
    return await cursor.fetchall()


async def count_visible_active_polls() -> int:
    """Сколько активных (открытых) опросов сейчас в меню — счётчик в Ратуше."""
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT COUNT(*) AS cnt FROM polls WHERE is_active = 1 AND COALESCE(is_archived, 0) = 0"
    )
    row = await cursor.fetchone()
    return row['cnt'] if row else 0


async def close_expired_polls() -> int:
    """Автозакрытие опросов, у которых вышел срок POLL_MAX_DAYS.

    Закрытие по сроку — обычное закрытие: closed_at проставляется, автор не пишется
    (closed_by остаётся NULL), голоса сохраняются, опрос остаётся в меню (если он
    в числе новейших) под знаком 🔒. Возвращает число закрытых.
    """
    from datetime import datetime, timezone
    conn = await get_db()
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    cursor = await conn.execute(
        "UPDATE polls SET is_active = 0, closed_at = ? "
        "WHERE is_active = 1 AND closes_at IS NOT NULL AND closes_at != '' "
        "AND closes_at <= ?", (now_utc, now_utc)
    )
    await conn.commit()
    return cursor.rowcount


def datetime_now_utc_str() -> str:
    """Текущее время UTC строкой 'YYYY-MM-DD HH:MM:SS' — формат колонок polls."""
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


async def archive_old_polls(keep: int = None) -> int:
    """Увести в архив всё, что не влезло в меню голосования.

    В меню остаются keep (= POLL_VISIBLE) новейших неархивных опросов; всё, что
    старше — is_archived = 1, archived_day = сегодняшние сутки МСК. По archived_day
    раздел «Опросы» в библиотеке собирает записи по дням.

    Голоса и результаты не трогаем: архивный опрос остаётся доступен по ссылке.
    Возвращает число отправленных в архив.
    """
    from config import POLL_VISIBLE
    conn = await get_db()
    n = keep if keep is not None else POLL_VISIBLE
    cursor = await conn.execute(
        "UPDATE polls SET is_archived = 1, archived_day = ?, "
        "is_active = 0, closed_at = COALESCE(closed_at, ?) "
        "WHERE COALESCE(is_archived, 0) = 0 AND id NOT IN "
        "(SELECT id FROM polls WHERE COALESCE(is_archived, 0) = 0 ORDER BY id DESC LIMIT ?)",
        (_poll_today_key(), datetime_now_utc_str(), n)
    )
    await conn.commit()
    return cursor.rowcount


async def maintain_polls() -> dict:
    """Обслуживание опросов: сначала закрыть истёкшие, потом увести лишние в архив.

    Порядок важен: истёкший опрос сначала закрывается (событие с отметкой времени),
    и только потом может попасть в архив. Вызывается из меню голосования (лениво,
    перед показом) и из суточного планировщика — чтобы истёкшее не висело до утра.
    """
    closed = await close_expired_polls()
    archived = await archive_old_polls()
    return {"closed": closed, "archived": archived}


async def get_archived_poll_days(page: int = 0, per_page: int = 5) -> list:
    """Дни архива опросов (новые сверху) с числом опросов в каждом — раздел
    «Опросы» библиотеки. Страница = страница дней, не опросов."""
    conn = await get_db()
    offset = max(0, page) * per_page
    cursor = await conn.execute(
        "SELECT archived_day, COUNT(*) AS cnt FROM polls "
        "WHERE COALESCE(is_archived, 0) = 1 AND archived_day != '' "
        "GROUP BY archived_day ORDER BY archived_day DESC LIMIT ? OFFSET ?",
        (per_page, offset)
    )
    return await cursor.fetchall()


async def count_archived_poll_days() -> int:
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT COUNT(DISTINCT archived_day) AS n FROM polls "
        "WHERE COALESCE(is_archived, 0) = 1 AND archived_day != ''"
    )
    row = await cursor.fetchone()
    return row['n'] if row else 0


async def count_archived_polls() -> int:
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT COUNT(*) AS n FROM polls WHERE COALESCE(is_archived, 0) = 1"
    )
    row = await cursor.fetchone()
    return row['n'] if row else 0


async def get_archived_polls_by_day(day: str, page: int = 0, per_page: int = 6) -> list:
    """Опросы одного дня архива (новые сверху) — то, что под заголовком-днём."""
    conn = await get_db()
    offset = max(0, page) * per_page
    cursor = await conn.execute(
        "SELECT * FROM polls WHERE COALESCE(is_archived, 0) = 1 AND archived_day = ? "
        "ORDER BY id DESC LIMIT ? OFFSET ?",
        (day, per_page, offset)
    )
    return await cursor.fetchall()


async def count_archived_polls_by_day(day: str) -> int:
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT COUNT(*) AS n FROM polls "
        "WHERE COALESCE(is_archived, 0) = 1 AND archived_day = ?", (day,)
    )
    row = await cursor.fetchone()
    return row['n'] if row else 0


# ============ РЕЧЬ ПРЕДСТАВИТЕЛЯ ============

def _rep_speech_today_key() -> str:
    """Ключ текущих игровых суток (10:00 МСК) — суточный лимит обращений представителя."""
    return today_report_day()


async def add_rep_speech(user_id: int, text: str) -> int:
    """Опубликовать обращение представителя. Возвращает id записи."""
    conn = await get_db()
    cursor = await conn.execute(
        "INSERT INTO rep_speeches (user_id, text, created_at, created_day) "
        "VALUES (?, ?, ?, ?)",
        (user_id, text, datetime_now_utc_str(), _rep_speech_today_key())
    )
    await conn.commit()
    return cursor.lastrowid


async def update_rep_speech(speech_id: int, text: str) -> bool:
    """Правка опубликованного обращения (не используется: правки обращения
    нет, любое изменение — новое обращение; оставлено для истории БД)."""
    conn = await get_db()
    cursor = await conn.execute(
        "UPDATE rep_speeches SET text = ?, edited = 1 WHERE id = ?", (text, speech_id)
    )
    await conn.commit()
    return cursor.rowcount > 0


async def delete_rep_speech(speech_id: int) -> bool:
    """Удаление обращения. Запись уходит совсем, поэтому суточный счётчик
    обращений представителя уменьшается — удаление ничего не стоит."""
    conn = await get_db()
    cursor = await conn.execute(
        "DELETE FROM rep_speeches WHERE id = ?", (speech_id,)
    )
    await conn.commit()
    return cursor.rowcount > 0


async def get_latest_rep_speech() -> dict | None:
    """Последнее обращение представителя — то, что висит «Голосом» на заголовке города."""
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT s.*, u.username, u.callsign, u.first_name, u.last_name "
        "FROM rep_speeches s LEFT JOIN users u ON u.user_id = s.user_id "
        "ORDER BY s.id DESC LIMIT 1"
    )
    return await cursor.fetchone()


async def get_rep_speech(speech_id: int) -> dict | None:
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT s.*, u.username, u.callsign, u.first_name, u.last_name "
        "FROM rep_speeches s LEFT JOIN users u ON u.user_id = s.user_id "
        "WHERE s.id = ?", (speech_id,)
    )
    return await cursor.fetchone()


async def count_rep_speeches_today(user_id: int) -> int:
    """Сколько обращений представитель уже опубликовал сегодня (суточный лимит)."""
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT COUNT(*) AS cnt FROM rep_speeches WHERE user_id = ? AND created_day = ?",
        (user_id, _rep_speech_today_key())
    )
    row = await cursor.fetchone()
    return row['cnt'] if row else 0


# ============ НОВОСТИ ГOССМИ ============

async def add_news(title: str, body: str, author_id: int, author_name: str,
                   photo_file_id: str = None) -> int:
    """Опубликовать новостной выпуск. Возвращает id записи."""
    conn = await get_db()
    cursor = await conn.execute(
        "INSERT INTO news_releases (title, body, photo_file_id, author_id, author_name, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (title, body, photo_file_id, author_id, author_name,
         datetime.now(MOSCOW_TZ).isoformat())
    )
    await conn.commit()
    return cursor.lastrowid


async def get_news(id: int):
    conn = await get_db()
    cursor = await conn.execute("SELECT * FROM news_releases WHERE id = ?", (id,))
    return await cursor.fetchone()


async def get_latest_news(limit: int = 10) -> list:
    """Последние выпуски (новые сверху) для ленты."""
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT * FROM news_releases ORDER BY rowid DESC LIMIT ?", (limit,))
    return await cursor.fetchall()


async def get_all_news(min_age_days: float = 0) -> list:
    """Все выпуски (для архива в библиотеке), новые сверху.

    min_age_days > 0: показывать только выпуски старше N дней.
    """
    conn = await get_db()
    if min_age_days > 0:
        from datetime import datetime, timedelta
        from utils.helpers import MOSCOW_TZ
        cutoff = (datetime.now(MOSCOW_TZ) - timedelta(days=min_age_days)).isoformat()
        cursor = await conn.execute(
            "SELECT * FROM news_releases WHERE (created_at IS NULL OR created_at <= ?) "
            "ORDER BY rowid DESC",
            (cutoff,)
        )
    else:
        cursor = await conn.execute("SELECT * FROM news_releases ORDER BY rowid DESC")
    return await cursor.fetchall()


async def update_news(id: int, title: str = None, body: str = None,
                      photo_file_id: str = None) -> bool:
    """Изменить выпуск (редактор). photo_file_id=None — без изменений."""
    sets, params = [], []
    if title is not None:
        sets.append("title = ?")
        params.append(title)
    if body is not None:
        sets.append("body = ?")
        params.append(body)
    if photo_file_id is not None:
        sets.append("photo_file_id = ?")
        params.append(photo_file_id)
    if not sets:
        return False
    sets.append("edited = 1")
    params.append(id)
    conn = await get_db()
    await conn.execute(f"UPDATE news_releases SET {', '.join(sets)} WHERE id = ?", params)
    await conn.commit()
    return True


async def delete_news(id: int) -> bool:
    conn = await get_db()
    cursor = await conn.execute("DELETE FROM news_releases WHERE id = ?", (id,))
    await conn.commit()
    return cursor.rowcount > 0


async def get_news_count_today(user_id: int) -> int:
    """Сколько выпусков опубликовал игрок за текущие игровые сутки (10:00 МСК)."""
    conn = await get_db()
    cursor = await conn.execute(
        f"SELECT COUNT(*) AS cnt FROM news_releases "
        f"WHERE author_id = ? AND {_report_day('created_at')} = ?",
        (user_id, today_report_day())
    )
    row = await cursor.fetchone()
    return row['cnt'] if row else 0


NII_DAILY_LIMIT = 2  # максимум обращений в сутки от одного пилота


async def count_nii_reports_today(user_id: int) -> int:
    """Сколько обращений в НИИ пилот отправил за текущие игровые сутки (10:00 МСК)."""
    conn = await get_db()
    cursor = await conn.execute(
        f"SELECT COUNT(*) AS cnt FROM nii_reports "
        f"WHERE user_id = ? AND {_report_day('created_at')} = ?",
        (user_id, today_report_day())
    )
    row = await cursor.fetchone()
    return row['cnt'] if row else 0


async def add_nii_report(user_id: int, text: str, photo_file_id: str = None,
                          photo2_file_id: str = None) -> int:
    """Сохранить обращение в НИИ. Возвращает id записи."""
    conn = await get_db()
    cursor = await conn.execute(
        "INSERT INTO nii_reports (user_id, text, photo_file_id, photo2_file_id, "
        "status, created_at) "
        "VALUES (?, ?, ?, ?, 'open', ?)",
        (user_id, text, photo_file_id, photo2_file_id,
         datetime.now(MOSCOW_TZ).isoformat())
    )
    await conn.commit()
    return cursor.lastrowid


async def get_nii_report(report_id: int):
    conn = await get_db()
    cursor = await conn.execute("SELECT * FROM nii_reports WHERE id = ?", (report_id,))
    return await cursor.fetchone()


async def get_my_nii_reports(user_id: int, limit: int = 10) -> list:
    """Свои обращения (новые сверху)."""
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT * FROM nii_reports WHERE user_id = ? ORDER BY id DESC LIMIT ?",
        (user_id, limit)
    )
    return await cursor.fetchall()


async def get_all_nii_reports(status: str = None, limit: int = 50) -> list:
    """Все обращения (для Хранителей/супер-админа), новые сверху."""
    conn = await get_db()
    if status:
        cursor = await conn.execute(
            "SELECT * FROM nii_reports WHERE status = ? ORDER BY id DESC LIMIT ?",
            (status, limit)
        )
    else:
        cursor = await conn.execute(
            "SELECT * FROM nii_reports ORDER BY id DESC LIMIT ?", (limit,))
    return await cursor.fetchall()


async def set_nii_report_status(report_id: int, status: str) -> bool:
    """Сменить статус обращения (Хранитель/админ): open/done/closed."""
    conn = await get_db()
    cursor = await conn.execute(
        "UPDATE nii_reports SET status = ? WHERE id = ?", (status, report_id))
    await conn.commit()
    return cursor.rowcount > 0


async def nii_notify_ids() -> list:
    """Telegram-id всех, кому приходит оповещение о новых обращениях в НИИ:
    игроки со статусом «Хранитель» (access_tag='keeper') + супер-админы
    (ADMIN_IDS и роли super_admin). Без дубликатов."""
    from config import ADMIN_IDS
    ids = set(ADMIN_IDS)
    conn = await get_db()
    cursor = await conn.execute("""
        SELECT DISTINCT us.user_id FROM user_statuses us
        JOIN statuses s ON us.status_id = s.id
        WHERE s.access_tag = 'keeper'
    """)
    for row in await cursor.fetchall():
        ids.add(row['user_id'])
    cursor = await conn.execute(
        "SELECT DISTINCT telegram_id FROM user_roles WHERE role = 'super_admin'")
    for row in await cursor.fetchall():
        ids.add(row['telegram_id'])
    return list(ids)


async def vote_poll(poll_id: int, user_id: int, option_index: int) -> bool:
    conn = await get_db()
    try:
        await conn.execute(
            "INSERT INTO poll_votes (poll_id, user_id, option_index) VALUES (?, ?, ?)",
            (poll_id, user_id, option_index)
        )
        await conn.commit()
        return True
    except aiosqlite.IntegrityError:
        return False


async def get_poll_results(poll_id: int):
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT option_index, COUNT(*) as cnt FROM poll_votes WHERE poll_id = ? GROUP BY option_index",
        (poll_id,)
    )
    return await cursor.fetchall()


async def user_voted(poll_id: int, user_id: int) -> bool:
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT 1 FROM poll_votes WHERE poll_id = ? AND user_id = ?",
        (poll_id, user_id)
    )
    return await cursor.fetchone() is not None


async def get_user_voted_polls_count(user_id: int) -> int:
    """Сколько всего опросов уже прошёл пилот (хотя бы раз проголосовал)."""
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT COUNT(DISTINCT poll_id) AS cnt FROM poll_votes WHERE user_id = ?",
        (user_id,)
    )
    row = await cursor.fetchone()
    return row['cnt'] if row else 0


async def get_poll_vote_option(poll_id: int, user_id: int):
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT option_index FROM poll_votes WHERE poll_id = ? AND user_id = ?",
        (poll_id, user_id)
    )
    row = await cursor.fetchone()
    return row['option_index'] if row else None


async def get_poll(poll_id: int):
    conn = await get_db()
    cursor = await conn.execute("SELECT * FROM polls WHERE id = ?", (poll_id,))
    return await cursor.fetchone()


async def get_active_polls():
    conn = await get_db()
    cursor = await conn.execute("SELECT * FROM polls WHERE is_active = 1")
    return await cursor.fetchall()


async def close_poll(poll_id: int, closed_by: int = None):
    conn = await get_db()
    await conn.execute(
        "UPDATE polls SET is_active = 0, closed_by = COALESCE(?, closed_by), "
        "closed_at = datetime('now') WHERE id = ? AND is_active = 1",
        (closed_by, poll_id)
    )
    await conn.commit()


async def get_closed_polls():
    """Закрытые опросы (архив), свежие сверху."""
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT * FROM polls WHERE is_active = 0 ORDER BY COALESCE(closed_at, created_at) DESC"
    )
    return await cursor.fetchall()


# ============ СУТОЧНЫЕ ЛИМИТЫ (Квестор: начисления) ============

async def get_daily_spent(admin_id: int, date: str) -> int:
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT spent FROM daily_limits WHERE admin_id = ? AND date = ?",
        (admin_id, date)
    )
    row = await cursor.fetchone()
    return row['spent'] if row else 0


async def add_daily_spent(admin_id: int, date: str, amount: int):
    conn = await get_db()
    await conn.execute(
        """INSERT INTO daily_limits (admin_id, date, spent) VALUES (?, ?, ?)
           ON CONFLICT(admin_id, date) DO UPDATE SET spent = spent + ?""",
        (admin_id, date, amount, amount)
    )
    await conn.commit()


# ============ КАЗНА НОРДХАЙМА ============

TREASURY_ID = 0  # служебный идентификатор казны в транзакциях

async def get_treasury_balance() -> int:
    conn = await get_db()
    cursor = await conn.execute("SELECT balance FROM treasury WHERE id = 1")
    row = await cursor.fetchone()
    return row['balance'] if row else 0


async def add_treasury(amount: int, description: str = ""):
    """Начисление в казну (например, налог с отчёта)."""
    conn = await get_db()
    await conn.execute("UPDATE treasury SET balance = balance + ? WHERE id = 1", (amount,))
    await conn.execute(
        "INSERT INTO transactions (to_user, amount, tx_type, description) VALUES (?, ?, ?, ?)",
        (TREASURY_ID, amount, "treasury", description)
    )
    await conn.commit()


async def transfer_to_treasury(from_user: int, amount: int, description: str = ""):
    """Перевод из кошелька игрока в казну."""
    conn = await get_db()
    await conn.execute("UPDATE users SET nordmarks = nordmarks - ? WHERE user_id = ?", (amount, from_user))
    await conn.execute("UPDATE treasury SET balance = balance + ? WHERE id = 1", (amount,))
    await conn.execute(
        "INSERT INTO transactions (from_user, to_user, amount, tx_type, description) VALUES (?, ?, ?, ?, ?)",
        (from_user, TREASURY_ID, amount, "treasury", description)
    )
    await conn.commit()


async def transfer_from_treasury(to_user: int, amount: int, description: str = ""):
    """Выплата из казны игроку (только глава Минфина)."""
    conn = await get_db()
    await conn.execute("UPDATE treasury SET balance = balance - ? WHERE id = 1", (amount,))
    await conn.execute("UPDATE users SET nordmarks = nordmarks + ? WHERE user_id = ?", (amount, to_user))
    await conn.execute(
        "INSERT INTO transactions (from_user, to_user, amount, tx_type, description) VALUES (?, ?, ?, ?, ?)",
        (TREASURY_ID, to_user, amount, "treasury", description)
    )
    await conn.commit()


async def get_treasury_stats() -> dict:
    """Статистика по казне: входящие (to_user = 0), исходящие (from_user = 0).

    Входящие группируются по происхождению (description) и игроку-отправителю,
    исходящие — по получателю.
    """
    conn = await get_db()
    cur = await conn.execute(
        "SELECT COALESCE(SUM(amount), 0) AS total, COUNT(*) AS cnt "
        "FROM transactions WHERE to_user = ?",
        (TREASURY_ID,)
    )
    incoming = await cur.fetchone()

    cur = await conn.execute(
        "SELECT COALESCE(SUM(amount), 0) AS total "
        "FROM transactions WHERE from_user = ?",
        (TREASURY_ID,)
    )
    outgoing = await cur.fetchone()

    # Входящие по описанию (источнику пополнения)
    cur = await conn.execute(
        "SELECT description, SUM(amount) AS total, COUNT(*) AS cnt "
        "FROM transactions WHERE to_user = ? GROUP BY description "
        "ORDER BY total DESC LIMIT 15",
        (TREASURY_ID,)
    )
    by_desc = [dict(r) for r in await cur.fetchall()]

    # Входящие по отправителю-игроку (пожертвования / переводы в казну)
    cur = await conn.execute(
        "SELECT from_user, SUM(amount) AS total, COUNT(*) AS cnt "
        "FROM transactions WHERE to_user = ? AND from_user IS NOT NULL "
        "GROUP BY from_user ORDER BY total DESC LIMIT 10",
        (TREASURY_ID,)
    )
    by_from = [dict(r) for r in await cur.fetchall()]

    # Исходящие по получателю (выплаты из казны)
    cur = await conn.execute(
        "SELECT to_user, SUM(amount) AS total, COUNT(*) AS cnt "
        "FROM transactions WHERE from_user = ? "
        "GROUP BY to_user ORDER BY total DESC LIMIT 10",
        (TREASURY_ID,)
    )
    by_to = [dict(r) for r in await cur.fetchall()]

    return {
        "incoming_total": incoming['total'],
        "incoming_count": incoming['cnt'],
        "outgoing_total": outgoing['total'],
        "by_desc": by_desc,
        "by_from": by_from,
        "by_to": by_to,
    }


async def _balance_legacy_booklet_payouts():
    """Один раз списывает с казны старые выплаты значков «Опытный турист».

    До v0.18.13 премия буклета (20 НМ) начислялась игроку «из воздуха» — казна
    не участвовала. Теперь все премии наград платятся из казны, поэтому
    исторические выплаты вписываем в бюджет задним числом: помечаем те
    транзакции исходящими из казны (from_user = TREASURY_ID) — они сразу
    появятся в статистике казны, а баланс уменьшаем на сумму этих выплат
    (не в минус). Идемпотентно: после первого прогона транзакции помечены.
    """
    conn = await get_db()
    cur = await conn.execute(
        "SELECT COALESCE(SUM(amount), 0) AS total FROM transactions "
        "WHERE tx_type = 'booklet' AND from_user IS NULL AND to_user != 0 AND amount > 0")
    total = (await cur.fetchone())['total'] or 0
    if total <= 0:
        return
    await conn.execute(
        "UPDATE transactions SET from_user = ? "
        "WHERE tx_type = 'booklet' AND from_user IS NULL AND to_user != 0 AND amount > 0",
        (TREASURY_ID,))
    balance = await get_treasury_balance()
    if balance > 0:
        await conn.execute(
            "UPDATE treasury SET balance = MAX(0, balance - ?) WHERE id = 1",
            (total,))
    await conn.commit()


# ============ ЗАРПЛАТЫ ============

async def get_salaried_users():
    """Все пилоты с назначенной зарплатой (salary > 0)."""
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT user_id, username, first_name, salary, salary_period_days, last_salary_date, salary_debt "
        "FROM users WHERE salary IS NOT NULL AND salary > 0 ORDER BY salary DESC"
    )
    return await cursor.fetchall()


async def get_user_salary(user_id: int) -> dict:
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT salary, salary_period_days, last_salary_date FROM users WHERE user_id = ?",
        (user_id,)
    )
    row = await cursor.fetchone()
    return dict(row) if row else {"salary": 0, "salary_period_days": 7, "last_salary_date": None}


async def set_user_salary(user_id: int, amount: int, period_days: int = 7, admin_id: int = None):
    """Назначить/изменить зарплату пилоту.

    Выплата идёт по фиксированному календарному графику (воскресенье),
    не зависит от даты назначения. last_salary_date не сбрасываем:
    если в текущей неделе платёж уже прошёл — следующая выплата будет
    в следующее воскресенье (защита от дублей).
    """
    conn = await get_db()
    if amount <= 0:
        await conn.execute(
            "UPDATE users SET salary = 0 WHERE user_id = ?", (user_id,)
        )
    else:
        await conn.execute(
            "UPDATE users SET salary = ?, salary_period_days = ? WHERE user_id = ?",
            (amount, period_days, user_id)
        )
    await conn.commit()


async def get_salaries_due() -> list:
    """Пилоты, которым пора выплатить зарплату (месячный график).

    Фиксированный график: выплата один раз в месяц — с 28-го числа (МСК),
    та же дата, что и у окладов за должности. Не зависит от даты назначения
    зарплаты. Защита от дублей: платим, только если в текущем календарном
    месяце выплата ещё не проводилась (last_salary_date — прошлый месяц
    или отсутствует). 29–31-е числа добивают тех, кто не был оплачен 28-го
    (если бот лежал).
    """
    conn = await get_db()
    # MSK = UTC+3 (без перехода на летнее время): берём «сейчас» в МСК,
    # чтобы 28-е не срезалось/не дублировалось около полуночи по UTC.
    cursor = await conn.execute(
        "SELECT user_id, username, first_name, salary, salary_debt FROM users "
        "WHERE (salary IS NOT NULL AND salary > 0 "
        "      OR salary_debt IS NOT NULL AND salary_debt > 0) "
        "AND CAST(strftime('%d', datetime('now', '+3 hours')) AS INTEGER) >= 28 "
        "AND (last_salary_date IS NULL OR "
        "     strftime('%Y-%m', last_salary_date) < "
        "     strftime('%Y-%m', datetime('now', '+3 hours')))"
    )
    return await cursor.fetchall()


async def mark_salary_paid(user_id: int):
    conn = await get_db()
    await conn.execute(
        "UPDATE users SET last_salary_date = datetime('now') WHERE user_id = ?", (user_id,)
    )
    await conn.commit()


async def pay_salaries() -> dict:
    """Выплачивает зарплаты всем, кому пора (месячный график: с 28-го числа).

    Логика: оплачивается ставка за месяц + накопленный ранее долг.
    Если казны не хватает — платим сколько возможно (если есть хоть что-то),
    остаток копится в salary_debt, last_salary_date не меняется (долг растёт
    каждую пропущенную выплату). Возвращает статистику для уведомления.
    """
    balance = await get_treasury_balance()
    due = await get_salaries_due()
    paid = []
    debt = []
    reserves = 0  # сколько всего не хватило

    for u in due:
        uid = u['user_id']
        weekly = u['salary']
        owed = weekly + (u['salary_debt'] or 0)  # ставка + накопленный долг

        if owed <= 0:
            continue

        if balance >= owed:
            # оплачиваем всё: ставка + долг
            await add_treasury_move(owed, u)
            balance -= owed
            await clear_salary_debt(uid)
            await mark_salary_paid(uid)
            paid.append((uid, owed))
        elif balance > 0:
            # казны не хватает на всё — платим сколько есть, остаток в долг
            await add_treasury_move(balance, u)
            rest = owed - balance
            await add_salary_debt(uid, rest)
            reserves += rest
            balance = 0
            # last_salary_date не обновляем: долг продолжит накапливаться
            debt.append((uid, rest))
        else:
            # казны совсем нет — вся сумма в долг
            rest = owed
            await add_salary_debt(uid, rest)
            reserves += rest
            debt.append((uid, rest))

    return {
        "paid": paid,
        "debt": debt,
        "reserves": reserves,
    }


async def add_salary_debt(user_id: int, amount: int):
    conn = await get_db()
    await conn.execute(
        "UPDATE users SET salary_debt = salary_debt + ? WHERE user_id = ?",
        (amount, user_id)
    )
    await conn.commit()


async def clear_salary_debt(user_id: int):
    conn = await get_db()
    await conn.execute(
        "UPDATE users SET salary_debt = 0 WHERE user_id = ?", (user_id,)
    )
    await conn.commit()


async def add_treasury_move(amount: int, user_row):
    """Выплата зарплаты игроку из казны (служебная) + транзакции."""
    conn = await get_db()
    await conn.execute("UPDATE treasury SET balance = balance - ? WHERE id = 1", (amount,))
    await conn.execute(
        "UPDATE users SET nordmarks = nordmarks + ? WHERE user_id = ?",
        (amount, user_row['user_id'])
    )
    await conn.execute(
        "INSERT INTO transactions (from_user, to_user, amount, tx_type, description) VALUES (?, ?, ?, ?, ?)",
        (TREASURY_ID, user_row['user_id'], amount, "salary",
         f"Зарплата ({user_row['first_name'] or user_row['username'] or user_row['user_id']})")
    )
    await conn.commit()


async def get_treasury_debts() -> dict:
    """Долги по выплатам из казны.

    Возвращает накопленные долги по зарплатам (salary_debt — не хватило
    средств на момент выплаты) и прогноз на следующую выплату: хватит ли
    текущего баланса на весь фонд заработных плат.
    """
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT user_id, username, first_name, salary, salary_period_days, "
        "last_salary_date, salary_debt FROM users "
        "WHERE salary_debt IS NOT NULL AND salary_debt > 0 "
        "ORDER BY salary_debt DESC"
    )
    debtors = [dict(r) for r in await cursor.fetchall()]
    total_debt = sum(int(r['salary_debt'] or 0) for r in debtors)

    cursor = await conn.execute(
        "SELECT salary, salary_debt FROM users "
        "WHERE salary IS NOT NULL AND salary > 0"
    )
    salaried = await cursor.fetchall()
    next_pay_need = sum(int(u['salary'] or 0) + int(u['salary_debt'] or 0) for u in salaried)

    balance = await get_treasury_balance()
    return {
        "debtors": debtors,
        "total_debt": total_debt,
        "salaried_count": len(salaried),
        "next_pay_need": next_pay_need,
        "shortfall": max(next_pay_need - balance, 0),
        "balance": balance,
    }


# ============ ДНИ ПЛАМЕННОГО КРУГОВОРОТА (событие, ТЗ — FIRE_EVENT.md) ============

def fire_event_active() -> bool:
    """Сейчас ли идёт событие (окно дат по МСК, рубильник FIRE_EVENT_ENABLED)."""
    if not getattr(config, "FIRE_EVENT_ENABLED", False):
        return False
    from utils.helpers import MOSCOW_TZ
    from datetime import timedelta
    msk = datetime.now(MOSCOW_TZ)
    y, mo, d, hh, mm = (getattr(config, "FIRE_EVENT_START", None) or (2026, 10, 30, 0, 0))
    start = msk.replace(year=y, month=mo, day=d, hour=hh, minute=mm, second=0, microsecond=0)
    end = start + timedelta(days=int(getattr(config, "FIRE_EVENT_DURATION_DAYS", 5) or 5))
    return start <= msk < end


def fire_event_visible() -> bool:
    """Кнопка города: событие активно И лабиринт открыт (FIRE_LAB_ENABLED)."""
    return bool(getattr(config, "FIRE_LAB_ENABLED", False)) and fire_event_active()


async def get_fire_lab_entries_today(user_id: int, day: str) -> int:
    """Сколько заходов в лабиринт сделал игрок за указанный игровой день."""
    conn = await get_db()
    cur = await conn.execute(
        "SELECT qty FROM fire_lab_entries WHERE user_id = ? AND day = ?",
        (user_id, day))
    row = await cur.fetchone()
    return int(row['qty'] or 0) if row else 0


async def inc_fire_lab_entries(user_id: int, day: str) -> int:
    """+1 вход в лабиринт; возвращает обновлённое число за день."""
    conn = await get_db()
    cur = await conn.execute(
        "INSERT INTO fire_lab_entries (user_id, day, qty) VALUES (?, ?, 1) "
        "ON CONFLICT(user_id, day) DO UPDATE SET qty = qty + 1",
        (user_id, day))
    await conn.commit()
    return await get_fire_lab_entries_today(user_id, day)


async def create_fire_lab_session(user_id: int, hp: int) -> int:
    """Новая сессия лабиринта (status='active'); возвращает id сессии."""
    conn = await get_db()
    cur = await conn.execute(
        "INSERT INTO fire_lab_sessions (user_id, status, hp, hp_max, last_active_at, fish_used) "
        "VALUES (?, 'active', ?, ?, datetime('now'), 0)", (user_id, hp, hp))
    await conn.commit()
    return int(cur.lastrowid or 0)


async def bump_fire_lab_room_visit(session_id: int, room: str) -> int:
    """+1 к счётчику посещений особой комнаты (well/tree/chest); возвращает новое значение.

    Вход в Колодец обнуляет попытки праздничной рыбалки (fish_used=0): лимит —
    per visit, не за сессию.
    """
    col = {"well": "well_visits", "tree": "tree_visits", "chest": "chest_visits"}.get(room)
    if not col:
        return 0
    conn = await get_db()
    if room == "well":
        await conn.execute(
            f"UPDATE fire_lab_sessions SET {col} = {col} + 1, fish_used = 0 "
            "WHERE id = ?", (session_id,))
    else:
        await conn.execute(
            f"UPDATE fire_lab_sessions SET {col} = {col} + 1 WHERE id = ?",
            (session_id,))
    await conn.commit()
    cur = await conn.execute(
        f"SELECT {col} AS v FROM fire_lab_sessions WHERE id = ?", (session_id,))
    row = await cur.fetchone()
    return int(row['v'] or 0) if row else 0


async def set_fire_lab_blessing(session_id: int) -> None:
    """Благословение Древа Огня на остаток сессии (после визита в Древо)."""
    conn = await get_db()
    await conn.execute(
        "UPDATE fire_lab_sessions SET blessing = 1 WHERE id = ?", (session_id,))
    await conn.commit()


async def get_fire_lab_fish_used(session_id: int) -> int:
    """Сколько попыток рыбалки потрачено в текущем визите в Колодец."""
    conn = await get_db()
    cur = await conn.execute(
        "SELECT fish_used FROM fire_lab_sessions WHERE id = ?", (session_id,))
    row = await cur.fetchone()
    return int(row['fish_used'] or 0) if row else 0


async def inc_fire_lab_fish_used(session_id: int) -> int:
    """+1 попытка рыбалки; атомарно допускает только в пределах лимита за визит.

    Возвращает НОВОЕ значение (0 — попытка не зачлась: лимит уже исчерпан).
    """
    conn = await get_db()
    cap = int(getattr(config, "FIRE_LAB_WELL_FISH_TRIES", 6) or 6)
    cur = await conn.execute(
        "UPDATE fire_lab_sessions SET fish_used = fish_used + 1 "
        "WHERE id = ? AND fish_used < ?", (session_id, cap))
    if not cur.rowcount:
        await conn.commit()
        return 0
    await conn.commit()
    return await get_fire_lab_fish_used(session_id)


async def mark_fire_fish_caught(user_id: int, item_id: int) -> bool:
    """Отметить пойманную праздничную рыбу (UNIQUE per user+item).

    Возвращает True, если этот вид пойман впервые (для текста «Новая рыба!»).
    """
    conn = await get_db()
    cur = await conn.execute(
        "SELECT 1 FROM user_fire_fish WHERE user_id = ? AND item_id = ?",
        (user_id, item_id))
    fresh = await cur.fetchone() is None
    if fresh:
        await conn.execute(
            "INSERT OR IGNORE INTO user_fire_fish (user_id, item_id) VALUES (?, ?)",
            (user_id, item_id))
        await conn.commit()
    return fresh


async def count_fire_fish_kinds(user_id: int) -> int:
    """Сколько видов праздничной рыбы пилот поймал за время события."""
    conn = await get_db()
    cur = await conn.execute(
        "SELECT COUNT(*) AS c FROM user_fire_fish WHERE user_id = ?", (user_id,))
    row = await cur.fetchone()
    return int(row['c'] or 0)


FIRE_KEEPER_GEAR_NAMES = (  # экип набора «Чтящий Предков»
    "Огненный венец", "Плащ Памяти", "Перчатки стража посевов", "Вилы",
)


async def fire_keeper_progress(user_id: int) -> dict:
    """Прогресс набора «Чтящий Предков»: {'gears': {имя: bool}, 'seeds': bool,
    'recipes': {имя: bool}, 'done': bool}."""
    conn = await get_db()
    gears = {}
    for nm in FIRE_KEEPER_GEAR_NAMES:
        cur = await conn.execute("SELECT id FROM items WHERE name = ?", (nm,))
        it = await cur.fetchone()
        ok = False
        if it:
            inv = await get_inventory_item(user_id, it['id'])
            ok = bool(inv and int(inv['quantity'] or 0) > 0)
        gears[nm] = ok
    cur = await conn.execute("SELECT id FROM items WHERE name = ?",
                             (getattr(config, "FIRE_PUMPKIN_SEED_NAME", "Семечко тыквы"),))
    seed_ok = False
    seed_row = await cur.fetchone()
    if seed_row:
        inv = await get_inventory_item(user_id, seed_row['id'])
        seed_ok = bool(inv and int(inv['quantity'] or 0) > 0)
    recipes = {}
    for rname in ("Тыквенный пирог", "Обжигающая трость"):
        cur = await conn.execute(
            "SELECT id FROM recipes WHERE name = ?", (rname,))
        rrow = await cur.fetchone()
        recipes[rname] = bool(rrow and await has_user_recipe(
            user_id, int(rrow['id'])))
    done = all(gears.values()) and seed_ok and all(recipes.values())
    return {"gears": gears, "seeds": seed_ok, "recipes": recipes, "done": done}


async def check_fire_keeper(user_id: int) -> tuple[int, str, str]:
    """Одна точка проверки набора «Чтящий Предков»; вызывается после любого
    получения/использования компонента.

    Возвращает (level|None, имя_уровня|None, имя_предыдущего|None).
    """
    prog = await fire_keeper_progress(user_id)
    if not prog["done"]:
        return None, None, None
    return await set_achievement_progress(
        user_id, "fire_keeper", 1)


async def touch_fire_lab_session(session_id: int) -> None:
    """Отметить активность игрока в сессии (продление TTL)."""
    conn = await get_db()
    await conn.execute(
        "UPDATE fire_lab_sessions SET last_active_at = datetime('now') WHERE id = ?",
        (session_id,))
    await conn.commit()


async def get_active_fire_lab_session(user_id: int):
    """Активная сессия лабиринта игрока (или None).

    Ленивое закрытие по TTL: если сессия активна, но последнее действие игрока
    старше `FIRE_LAB_SESSION_TTL_SEC` (1 ч) — сессия закрывается со статусом
    `expired` и активной не считается (повторный вход — снова платный).
    """
    conn = await get_db()
    cur = await conn.execute(
        "SELECT * FROM fire_lab_sessions WHERE user_id = ? AND status = 'active' "
        "ORDER BY id DESC LIMIT 1", (user_id,))
    s = await cur.fetchone()
    if not s:
        return None
    ttl = int(getattr(config, "FIRE_LAB_SESSION_TTL_SEC", 3600) or 3600)
    last = s['last_active_at'] or s['entered_at']
    if last:
        try:
            from datetime import datetime, timedelta
            from utils.helpers import MOSCOW_TZ
            # SQLite datetime('now') = UTC; приводим к UTC-timezone-aware
            last_dt = datetime.fromisoformat(last.replace(' ', 'T')).replace(tzinfo=timezone.utc)
        except Exception:
            last_dt = None
        if last_dt:
            from datetime import timezone as _tz
            now = datetime.now(_tz.utc)
            if now - last_dt > timedelta(seconds=ttl):
                await end_fire_lab_session(int(s['id']), 'expired')
                return None
    return s


async def end_fire_lab_session(session_id: int, status: str) -> None:
    """Закрыть сессию лабиринта со статусом dead/left/finished/expired/event_closed."""
    conn = await get_db()
    await conn.execute(
        "UPDATE fire_lab_sessions SET status = ?, ended_at = datetime('now') "
        "WHERE id = ?", (status, session_id))
    await conn.commit()


async def get_fire_lab_tier(user_id: int) -> int:
    """Тир «Огненного эха» пилота (0..FIRE_LAB_TIER_MAX)."""
    conn = await get_db()
    cur = await conn.execute("SELECT tier FROM fire_lab_tier WHERE user_id = ?", (user_id,))
    row = await cur.fetchone()
    return int(row['tier'] or 0) if row else 0


async def inc_fire_lab_tier(user_id: int) -> int:
    """+1 к Тиру за полное прохождение 25 комнат; кап FIRE_LAB_TIER_MAX.

    Возвращает новый Тир. runs (полных прогонов) учитывает все, даже после капа.
    """
    conn = await get_db()
    cap = int(getattr(config, "FIRE_LAB_TIER_MAX", 5) or 5)
    cur = await conn.execute(
        "INSERT INTO fire_lab_tier (user_id, tier, runs, updated_at) "
        "VALUES (?, 1, 1, datetime('now')) "
        "ON CONFLICT(user_id) DO UPDATE SET "
        "tier = CASE WHEN tier < ? THEN tier + 1 ELSE tier END, "
        "runs = runs + 1, updated_at = datetime('now')",
        (user_id, cap))
    await conn.commit()
    return await get_fire_lab_tier(user_id)


def firelab_tier_enemy_bonus(tier: int) -> int:
    """Доп. HP всем врагам на указанном Тире: 1–4 по +2, 5-й разово +8 (итог +16)."""
    step = int(getattr(config, "FIRE_LAB_TIER_HP_STEP", 2) or 2)
    last = int(getattr(config, "FIRE_LAB_TIER_HP_LAST", 8) or 8)
    cap = int(getattr(config, "FIRE_LAB_TIER_MAX", 5) or 5)
    tier = max(0, min(int(tier), cap))
    return step * min(tier, cap - 1) + (last if tier >= cap else 0)


def firelab_tier_loot_mult(tier: int) -> float:
    """Множитель шансов лута: Тир 1–4 → ×(1+2%)…, Тир 5 → ×(1+10%)."""
    step = float(getattr(config, "FIRE_LAB_TIER_LOOT_STEP", 0.02) or 0.02)
    last = float(getattr(config, "FIRE_LAB_TIER_LOOT_LAST", 0.10) or 0.10)
    cap = int(getattr(config, "FIRE_LAB_TIER_MAX", 5) or 5)
    tier = max(0, min(int(tier), cap))
    bonus = step * min(tier, cap - 1) + (last if tier >= cap else 0)
    return 1.0 + bonus


# ============ ОКЛАДЫ ЗА ДОЛЖНОСТИ (ролевые, раз в месяц 28-го) ============

async def get_role_salary_map() -> dict:
    """Справочник окладов по должностям: {role: НМ/мес}. Нули отбрасываются."""
    conn = await get_db()
    cursor = await conn.execute("SELECT role, amount FROM role_salaries")
    rows = await cursor.fetchall()
    return {r['role']: int(r['amount'] or 0) for r in rows if int(r['amount'] or 0) > 0}


def _role_pay_out(amounts: list) -> int:
    """Оклад по должностям: самая высокооплачиваемая полностью, остальные −50%.

    Роли с одинаковой суммой считаются как есть: первая из них проходит как «макс»,
    вторая режется наполовину. Округление вниз (int).
    """
    amounts = sorted(int(a) for a in amounts if int(a) > 0)
    if not amounts:
        return 0
    return amounts[-1] + sum(int(a * 0.5) for a in amounts[:-1])


async def get_user_db_roles(telegram_id: int) -> list:
    """Реальные роли из user_roles (без подмены супер-админом из ADMIN_IDS).

    get_user_role() для владельца возвращает только ['super_admin'], из-за чего
    его фактические оплачиваемые должности (у super_admin оклада нет) не
    участвовали в расчёте окладов. Оклады считают по этой функции.
    """
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT role FROM user_roles WHERE telegram_id = ?", (telegram_id,))
    return [row['role'] for row in await cursor.fetchall()]


async def role_salary_info(user_id: int) -> dict:
    """Оклады пилота для профиля: {'entries': [{role, amount}...], 'total': int}.

    entries отсортированы по убыванию; первая запись — должность, идущая в полном
    размере, остальные в информационных целях показываются как есть (вычитание 50%
    применяется только к выплате).
    """
    sals = await get_role_salary_map()
    roles = await get_user_db_roles(user_id)
    entries = [{"role": r, "amount": sals[r]} for r in roles if r in sals]
    entries.sort(key=lambda e: e["amount"], reverse=True)
    return {"entries": entries, "total": _role_pay_out([e["amount"] for e in entries])}


async def pay_role_salaries() -> dict:
    """Ежемесячные оклады за должности ИЗ КАЗНЫ (вызов — 28-го числа, main.scheduled_jobs).

    Берутся роли на дату выплаты: несколько должностей → самая высокооплачиваемая
    полностью, остальные −50% (см. _role_pay_out). Нехватка казны уходит в salary_debt
    и догоняется тем же циклом, что и зарплаты. Защита от дублей: табель
    role_salary_paid(user_id, месяц). Хранитель/глава клана оклада не имеют —
    в справочнике их нет.

    Возвращает {'paid': [...], 'debt': [...], 'reserves': int, 'skipped': int}.
    """
    month = datetime.now(MOSCOW_TZ).strftime("%Y-%m")
    conn = await get_db()
    cursor = await conn.execute("SELECT DISTINCT telegram_id FROM user_roles")
    ids = [r['telegram_id'] for r in await cursor.fetchall()]

    sals = await get_role_salary_map()
    from utils.permissions import get_user_role
    paid, debt, skipped = [], [], 0
    reserves = 0

    for uid in ids:
        roles = await get_user_db_roles(uid)
        total = _role_pay_out([sals[r] for r in roles if r in sals])
        if total <= 0:
            skipped += 1
            continue
        done = await (await conn.execute(
            "SELECT 1 FROM role_salary_paid WHERE user_id = ? AND month = ?",
            (uid, month))).fetchone()
        if done:
            continue
        before = (await (await conn.execute(
            "SELECT salary_debt FROM users WHERE user_id = ?", (uid,))).fetchone())['salary_debt'] or 0
        await _cash_from_treasury(uid, total, "salary", "Оклад по должности (28-е число)")
        after = (await (await conn.execute(
            "SELECT salary_debt FROM users WHERE user_id = ?", (uid,))).fetchone())['salary_debt'] or 0
        await conn.execute(
            "INSERT OR IGNORE INTO role_salary_paid (user_id, month, amount) VALUES (?, ?, ?)",
            (uid, month, total))
        if after > before:
            short = after - before
            reserves += short
            debt.append((uid, total, short))
        else:
            paid.append((uid, total))
    await conn.commit()
    return {"paid": paid, "debt": debt, "reserves": reserves, "skipped": skipped}


async def get_role_salary_recipients() -> list:
    """Список получателей окладов за должности (для раздела «Зарплаты»).

    Возвращает [{user_id, first_name, username, roles: [ключ роли...],
    total}] — total по формуле _role_pay_out (самая дорогая полностью,
    остальные −50%). Роли без оклада в справочнике не попадают; пилоты без
    оплачиваемых ролей отбрасываются.
    """
    conn = await get_db()
    sals = await get_role_salary_map()
    cursor = await conn.execute(
        "SELECT DISTINCT ur.telegram_id, u.first_name, u.username "
        "FROM user_roles ur LEFT JOIN users u ON u.user_id = ur.telegram_id "
        "ORDER BY u.first_name"
    )
    out = []
    for r in await cursor.fetchall():
        cur = await conn.execute(
            "SELECT role FROM user_roles WHERE telegram_id = ?", (r['telegram_id'],))
        roles = [row['role'] for row in await cur.fetchall()]
        paid_roles = [ro for ro in roles if ro in sals]
        if not paid_roles:
            continue
        paid_roles.sort(key=lambda ro: sals[ro], reverse=True)
        out.append({
            'user_id': r['telegram_id'],
            'first_name': r['first_name'],
            'username': r['username'],
            'roles': paid_roles,
            'total': _role_pay_out([sals[ro] for ro in paid_roles]),
        })
    return out


async def pay_role_salary_on_revoke(user_id: int, role: str):
    """Пропорциональная выплата оклада при досрочном снятии должности.

    Считается маржинальная доля должности в окладной формуле (самая дорогая роль
    идёт полностью, остальные −50%), умноженная на долю дней текущего месяца, что
    пилот пробыл в должности (от выдачи до снятия). Если полный оклад за месяц уже
    выплачен (28-е) — выплаты нет. Повторное снятие в том же месяце не платит снова
    (табель role_dismissal_paid). Выплата — из казны (нехватка → salary_debt).

    Вызывается ДО удаления строки user_roles. Возвращает
    {'amount', 'days', 'total_days'} либо None, если платить нечего.
    """
    sals = await get_role_salary_map()
    if sals.get(role, 0) <= 0:
        return None
    conn = await get_db()
    roles = await get_user_db_roles(user_id)
    if role not in roles:
        return None
    marginal = (_role_pay_out([sals[r] for r in roles if r in sals])
                - _role_pay_out([sals[r] for r in roles if r in sals and r != role]))
    if marginal <= 0:
        return None

    now = datetime.now(MOSCOW_TZ)
    month = now.strftime("%Y-%m")
    if await (await conn.execute(
            "SELECT 1 FROM role_salary_paid WHERE user_id = ? AND month = ?",
            (user_id, month))).fetchone():
        return None
    if await (await conn.execute(
            "SELECT 1 FROM role_dismissal_paid WHERE user_id = ? AND role = ? AND month = ?",
            (user_id, role, month))).fetchone():
        return None

    row = await (await conn.execute(
        "SELECT created_at FROM user_roles WHERE telegram_id = ? AND role = ?",
        (user_id, role))).fetchone()
    import calendar
    total_days = calendar.monthrange(now.year, now.month)[1]
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    granted = month_start
    raw = (row or {}).get("created_at")
    if raw:
        try:
            from datetime import timezone
            g = datetime.strptime(str(raw)[:19], "%Y-%m-%d %H:%M:%S")
            g = g.replace(tzinfo=timezone.utc).astimezone(MOSCOW_TZ)
            if g > granted:
                granted = g
        except ValueError:
            pass
    days = max(1, min((now.date() - granted.date()).days + 1, total_days))
    payout = int(marginal * days / total_days)
    if payout <= 0:
        return None
    await _cash_from_treasury(
        user_id, payout, "salary",
        f"Пропорциональный оклад при снятии должности ({role})")
    await conn.execute(
        "INSERT OR IGNORE INTO role_dismissal_paid (user_id, role, month, amount) "
        "VALUES (?, ?, ?, ?)", (user_id, role, month, payout))
    await conn.commit()
    return {"amount": payout, "days": days, "total_days": total_days}


async def award_news_publication(user_id: int) -> bool:
    """Гонорар ГосСМИ: +NEWS_PUBLISH_BONUS НМ за публикацию журналисту/редактору.

    Кап NEWS_PUBLISH_CAP публикаций в месяц на игрока — дальше считаем, но не платим.
    Гонорар идёт из казны (нехватка — в salary_debt). Хранитель (super_admin) без
    оклада — без гонорара. Возвращает True, если начислено.
    """
    from config import NEWS_PUBLISH_BONUS, NEWS_PUBLISH_CAP, ADMIN_IDS
    from utils.permissions import get_user_role
    if user_id in ADMIN_IDS:
        return False
    roles = await get_user_role(user_id)
    if not any(r in ("journalist", "editor") for r in roles):
        return False
    month = datetime.now(MOSCOW_TZ).strftime("%Y-%m")
    conn = await get_db()
    row = await (await conn.execute(
        "SELECT count FROM news_pub_paid WHERE user_id = ? AND month = ?",
        (user_id, month))).fetchone()
    cnt = (row['count'] or 0) if row else 0
    await conn.execute(
        "INSERT INTO news_pub_paid (user_id, month, count) VALUES (?, ?, ?) "
        "ON CONFLICT(user_id, month) DO UPDATE SET count = news_pub_paid.count + 1",
        (user_id, month, cnt + 1))
    await conn.commit()
    if cnt >= NEWS_PUBLISH_CAP or user_id in ADMIN_IDS:
        return False
    await _cash_from_treasury(user_id, NEWS_PUBLISH_BONUS, "news", "Гонорар за публикацию ГосСМИ")
    return True


# ============ НАЛОГ НА ОТЧЁТЫ ============

async def get_report_tax_percent() -> int:
    """Текущая ставка налога с отчётов в процентах (по умолчанию 15)."""
    conn = await get_db()
    cursor = await conn.execute("SELECT value FROM settings WHERE key = 'report_tax_percent'")
    row = await cursor.fetchone()
    if not row:
        return 15
    try:
        return int(row['value'])
    except (TypeError, ValueError):
        return 15


async def set_report_tax_percent(percent: int):
    conn = await get_db()
    await conn.execute(
        "INSERT INTO settings (key, value) VALUES ('report_tax_percent', ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (str(percent),)
    )
    await conn.commit()


# ============ ПОРОГ АВТОПРОВЕРКИ ОТЧЁТОВ ============

REPORT_AUTO_APPROVE_SETTING_KEY = "report_auto_approve_troops"


async def get_report_auto_approve_troops() -> int:
    """Порог автопроверки отчётов: отчёты до этого значения (войск за сутки)
    принимаются автоматически, больше — уходят на проверку админу/МВД.
    Дефолт — 100 (как в config.REPORT_AUTO_APPROVE_TROOPS)."""
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT value FROM settings WHERE key = ?", (REPORT_AUTO_APPROVE_SETTING_KEY,)
    )
    row = await cursor.fetchone()
    if not row:
        return 100
    try:
        return int(row['value'])
    except (TypeError, ValueError):
        return 100


async def set_report_auto_approve_troops(value: int):
    conn = await get_db()
    await conn.execute(
        "INSERT INTO settings (key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (REPORT_AUTO_APPROVE_SETTING_KEY, str(value))
    )
    await conn.commit()


# ============ СУТОЧНЫЙ ЛИМИТ ОПЛАТЫ ОТЧЁТОВ ============

REPORT_DAILY_PAY_CAP_SETTING_KEY = "report_daily_pay_cap"


async def get_report_daily_pay_cap() -> int:
    """Сколько войск максимум можно начислить за одни сутки по всем отчётам пилота.

    По умолчанию 4000 (config.REPORT_DAILY_PAY_CAP). 0 — без ограничения.
    Ограничивается только оплата за сутки; значение «всего» не ограничивается
    (в регионе за пару месяцев накапливаются десятки тысяч).
    """
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT value FROM settings WHERE key = ?", (REPORT_DAILY_PAY_CAP_SETTING_KEY,)
    )
    row = await cursor.fetchone()
    if not row:
        return config.REPORT_DAILY_PAY_CAP
    try:
        return max(0, int(row['value']))
    except (TypeError, ValueError):
        return config.REPORT_DAILY_PAY_CAP


async def set_report_daily_pay_cap(value: int):
    conn = await get_db()
    await conn.execute(
        "INSERT INTO settings (key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (REPORT_DAILY_PAY_CAP_SETTING_KEY, str(max(0, int(value))))
    )
    await conn.commit()


# ============ ЧАТ ОПОВЕЩЕНИЙ (ТОПИК СУПЕРГРУППЫ) ============

NEWS_CHAT_SETTING_KEY = "news_chat_id"
NEWS_TOPIC_SETTING_KEY = "news_topic_id"


async def _get_setting_int(key: str, default=None):
    conn = await get_db()
    cursor = await conn.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = await cursor.fetchone()
    if not row or row['value'] in (None, ''):
        return default
    try:
        return int(row['value'])
    except (TypeError, ValueError):
        return default


async def get_setting(key: str, default: str = None) -> str | None:
    """Строковое значение из таблицы settings (или default, если ключа нет)."""
    conn = await get_db()
    cursor = await conn.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = await cursor.fetchone()
    if not row or row['value'] in (None, ''):
        return default
    return row['value']


async def set_setting(key: str, value: str):
    """Сохранить строковое значение в settings (upsert + commit)."""
    conn = await get_db()
    await conn.execute(
        "INSERT INTO settings (key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (key, str(value))
    )
    await conn.commit()


async def set_news_chat(chat_id: int, topic_id: int = None):
    """Куда слать игровые оповещения: чат + (для форума) топик.

    Пустое значение chat_id отключает оповещения.
    """
    conn = await get_db()
    if chat_id:
        await conn.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (NEWS_CHAT_SETTING_KEY, str(int(chat_id)))
        )
    else:
        await conn.execute("DELETE FROM settings WHERE key = ?", (NEWS_CHAT_SETTING_KEY,))
    if topic_id:
        await conn.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (NEWS_TOPIC_SETTING_KEY, str(int(topic_id)))
        )
    else:
        await conn.execute("DELETE FROM settings WHERE key = ?", (NEWS_TOPIC_SETTING_KEY,))
    await conn.commit()
    await _reset_chat_guard_cache()


async def get_news_chat() -> tuple:
    """(chat_id, topic_id) для оповещений. Пусто — оповещения выключены.

    Значение из настроек важнее переменной окружения: её можно задать прямо в боте.
    """
    chat_id = await _get_setting_int(NEWS_CHAT_SETTING_KEY)
    if chat_id is None and config.NEWS_CHAT_ID:
        chat_id = int(config.NEWS_CHAT_ID)
    topic_id = await _get_setting_int(NEWS_TOPIC_SETTING_KEY)
    if chat_id is None:
        return None, None
    return chat_id, topic_id


# Чаты, в которых бот работает кроме личных сообщений (список через запятую).
ALLOWED_CHATS_SETTING_KEY = "allowed_chats"


async def _reset_chat_guard_cache():
    """Сбросить кэш белого списка чатов, чтобы новый чат заработал сразу."""
    try:
        from utils.chat_guard import reset_cache
        reset_cache()
    except Exception:
        pass


async def get_allowed_chats() -> list:
    """Белый список чатов, где бот отвечает (сверх личных сообщений)."""
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT value FROM settings WHERE key = ?", (ALLOWED_CHATS_SETTING_KEY,)
    )
    row = await cursor.fetchone()
    if not row or not row['value']:
        return []
    out = []
    for raw in str(row['value']).replace(';', ',').split(','):
        raw = raw.strip()
        if not raw:
            continue
        digits = raw.lstrip('-')
        if digits.isdigit():
            out.append(int(raw))
    return out


async def set_allowed_chats(chats: list):
    conn = await get_db()
    value = ','.join(str(int(c)) for c in chats if c)
    await conn.execute(
        "INSERT INTO settings (key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (ALLOWED_CHATS_SETTING_KEY, value)
    )
    await conn.commit()
    await _reset_chat_guard_cache()


# ============ НАЛОГ НА ПРОДАЖИ ============

async def get_sale_tax_percent() -> int:
    """Налог с продаж товаров игроков в процентах (по умолчанию 15)."""
    conn = await get_db()
    cursor = await conn.execute("SELECT value FROM settings WHERE key = 'sale_tax_percent'")
    row = await cursor.fetchone()
    if not row:
        return 15
    try:
        return int(row['value'])
    except (TypeError, ValueError):
        return 15


async def set_sale_tax_percent(percent: int):
    conn = await get_db()
    await conn.execute(
        "INSERT INTO settings (key, value) VALUES ('sale_tax_percent', ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (str(percent),)
    )
    await conn.commit()


# ============ СПЕЦ-ОТДЕЛ ============

# Код доступа к спец-отделу (задаётся админом с правами can_manage_shop).
SPECIAL_DEPT_CODE_KEY = "special_dept_code"


async def get_special_dept_code() -> str:
    """Текущий код доступа к спец-отделу (пустая строка — спец-отдел закрыт)."""
    conn = await get_db()
    cursor = await conn.execute("SELECT value FROM settings WHERE key = ?", (SPECIAL_DEPT_CODE_KEY,))
    row = await cursor.fetchone()
    return row['value'] if row else ""


async def set_special_dept_code(code: str):
    """Задать/сменить код доступа к спец-отделу ('' — закрыть отдел)."""
    conn = await get_db()
    await conn.execute(
        "INSERT INTO settings (key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (SPECIAL_DEPT_CODE_KEY, code)
    )
    await conn.commit()


async def get_special_fails(user_id: int) -> int:
    """Сколько раз сегодня игрок вводил неверный код спец-отдела."""
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT special_fails_today FROM users WHERE user_id = ?", (user_id,))
    row = await cursor.fetchone()
    return row['special_fails_today'] if row else 0


async def add_special_fail(user_id: int) -> int:
    """Увеличить счётчик неверных кодов на 1. Возвращает новое значение."""
    conn = await get_db()
    await conn.execute(
        "UPDATE users SET special_fails_today = special_fails_today + 1 WHERE user_id = ?",
        (user_id,)
    )
    await conn.commit()
    return await get_special_fails(user_id)


async def register_special_fail(user_id: int) -> bool:
    """Зарегистрировать неверный ввод кода.

    При достижении лимита спец-отдел блокируется на 24 часа, счётчик обнуляется.
    Возвращает True, если игрок только что получил бан.
    """
    fails = await add_special_fail(user_id)
    if fails >= SPECIAL_DEPT_ATTEMPTS_LIMIT:
        await set_special_blocked(user_id, SPECIAL_DEPT_BLOCK_MINUTES)
        await reset_special_fails(user_id)
        return True
    return False


async def reset_special_fails(user_id: int):
    """Обнулить счётчик неверных кодов (после успешной попытки)."""
    conn = await get_db()
    await conn.execute(
        "UPDATE users SET special_fails_today = 0 WHERE user_id = ?", (user_id,))
    await conn.commit()


async def is_special_blocked(user_id: int) -> bool:
    """Забанен ли игрок (покупки в спец-отделе закрыты на 24 часа)."""
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT special_blocked_until FROM users WHERE user_id = ?", (user_id,))
    row = await cursor.fetchone()
    if not row or not row['special_blocked_until']:
        return False
    until = row['special_blocked_until']
    try:
        until_ts = float(until)
    except (TypeError, ValueError):
        return False
    return time.time() < until_ts


async def set_special_blocked(user_id: int, minutes: int):
    """Установить бан покупок в спец-отделе на `minutes` минут."""
    conn = await get_db()
    until_ts = time.time() + minutes * 60
    await conn.execute(
        "UPDATE users SET special_blocked_until = ? WHERE user_id = ?",
        (str(until_ts), user_id)
    )
    await conn.commit()


async def clear_special_blocked(user_id: int):
    """Снять бан (после успешного ввода кода)."""
    conn = await get_db()
    await conn.execute(
        "UPDATE users SET special_blocked_until = NULL WHERE user_id = ?", (user_id,))
    await conn.commit()
    await reset_special_fails(user_id)


async def special_dept_block_left_minutes(user_id: int) -> int:
    """Сколько минут осталось до снятия бана (0 — не забанен)."""
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT special_blocked_until FROM users WHERE user_id = ?", (user_id,))
    row = await cursor.fetchone()
    if not row or not row['special_blocked_until']:
        return 0
    until = row['special_blocked_until']
    try:
        until_ts = float(until)
    except (TypeError, ValueError):
        return 0
    left = int((until_ts - time.time()) // 60)
    return max(0, left)


# ============ БИБЛИОТЕКА НОРДХАЙМА ============

# Разделы библиотеки и типы карт
LIBRARY_SECTIONS = ("history", "laws", "religion", "fiction", "encyclopedias")
CARD_BASIC_SECTIONS = ("history", "laws", "fiction")   # обычный билет
CARD_BASIC_COST = 300
CARD_SILVER_COST = 1000
CARD_SILVER_STATUS = "veteran"

from datetime import datetime, timedelta, timezone
from utils.helpers import MOSCOW_TZ


async def activate_library_card(user_id: int, card_type: str, days: int = 30):
    """Активирует (или продлевает) читательский билет пользователя."""
    conn = await get_db()
    now = datetime.now(MOSCOW_TZ)
    expires = (now + timedelta(days=days)).isoformat()
    await conn.execute(
        """INSERT INTO library_cards (user_id, card_type, expires_at) VALUES (?, ?, ?)
           ON CONFLICT(user_id, card_type) DO UPDATE SET expires_at = excluded.expires_at""",
        (user_id, card_type, expires)
    )
    await conn.commit()


async def get_library_cards(user_id: int) -> list:
    """Активные карты пользователя (не просроченные)."""
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT * FROM library_cards WHERE user_id = ? AND expires_at > ?",
        (user_id, datetime.now(MOSCOW_TZ).isoformat())
    )
    rows = await cursor.fetchall()
    return [dict(r) for r in rows]


async def can_access_sections(user_id: int) -> list:
    """Какие разделы библиотеки открыты пользователю.

    Без карты — пусто; обычная карта — история/законы/художественная;
    серебряная карта — все разделы.
    """
    cards = await get_library_cards(user_id)
    types = {c['card_type'] for c in cards}
    if "silver" in types:
        return list(LIBRARY_SECTIONS)
    if "basic" in types:
        return list(CARD_BASIC_SECTIONS)
    return []


async def has_library_access(user_id: int) -> bool:
    """Есть ли у пользователя хоть какой-то активный читательский билет."""
    return bool(await get_library_cards(user_id))


async def add_library_book(section: str, title: str, author: str, description: str,
                           cover_file_id: str = None, file_id: str = None,
                           file_type: str = None, url: str = None, added_by: int = 0) -> int:
    conn = await get_db()
    cursor = await conn.execute(
        """INSERT INTO library_books
           (section, title, author, description, cover_file_id, file_id, file_type, url, added_by)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (section, title, author, description, cover_file_id, file_id, file_type, url, added_by)
    )
    await conn.commit()
    return cursor.lastrowid


async def get_library_books(section: str) -> list:
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT * FROM library_books WHERE section = ? ORDER BY title",
        (section,)
    )
    return await cursor.fetchall()


async def get_library_book(book_id: int):
    conn = await get_db()
    cursor = await conn.execute("SELECT * FROM library_books WHERE id = ?", (book_id,))
    return await cursor.fetchone()


async def delete_library_book(book_id: int):
    conn = await get_db()
    await conn.execute("DELETE FROM library_books WHERE id = ?", (book_id,))
    await conn.commit()


async def add_interaction(from_user: int, to_user: int, interaction_type: str):
    conn = await get_db()
    state_changes = {
        "помощь": 5,
        "похвала": 3,
        "поддержка": 2,
        "вызов": -3,
    }
    change = state_changes.get(interaction_type, 0)
    state_str = str(change) if change != 0 else "0"

    await conn.execute(
        "INSERT INTO interactions (from_user, to_user, interaction_type, state_change) VALUES (?, ?, ?, ?)",
        (from_user, to_user, interaction_type, state_str)
    )

    if change != 0:
        await conn.execute(
            "UPDATE users SET state = MAX(0, MIN(100, state + ?)) WHERE user_id = ?",
            (change, to_user)
        )

    await conn.commit()
    return change


async def set_user_state(user_id: int, state_text: str, minutes: int, caused_by: int = None, reason: str = "",
                         meta: dict = None):
    """Добавить/обновить одно состояние в списке состояний игрока.

    Остальные состояния сохраняются. state_effects — dict {ключ: effects}.
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    effects_data = {"applied_at": now, "minutes": minutes, "caused_by": caused_by, "reason": reason}
    if meta:
        effects_data.update(meta)
    conn = await get_db()
    cursor = await conn.execute("SELECT state, state_effects FROM users WHERE user_id = ?", (user_id,))
    row = await cursor.fetchone()
    old_state = row['state'] if row else "нормально"
    effects = _load_state_effects(row['state'] if row else "", row['state_effects'] if row else "{}")
    effects[state_text] = effects_data
    new_state = _state_col_value(effects)

    await conn.execute(
        "UPDATE users SET state = ?, state_effects = ? WHERE user_id = ?",
        (new_state, json.dumps(effects, ensure_ascii=False), user_id)
    )
    await conn.execute(
        "INSERT INTO state_log (user_id, old_state, new_state, reason, caused_by) VALUES (?, ?, ?, ?, ?)",
        (user_id, old_state, new_state, reason or "изменение состояния", caused_by)
    )
    await conn.commit()


async def remove_user_state(user_id: int, state_text: str, caused_by: int = None, reason: str = "состояние снято"):
    """Снять одно состояние игрока, остальные сохраняются."""
    conn = await get_db()
    cursor = await conn.execute("SELECT state, state_effects FROM users WHERE user_id = ?", (user_id,))
    row = await cursor.fetchone()
    if not row:
        return
    old_state = row['state'] if row else "нормально"
    effects = _load_state_effects(row['state'] if row else "", row['state_effects'] if row else "{}")
    if state_text not in effects:
        return
    del effects[state_text]
    new_state = _state_col_value(effects)
    await conn.execute(
        "UPDATE users SET state = ?, state_effects = ? WHERE user_id = ?",
        (new_state, json.dumps(effects, ensure_ascii=False), user_id)
    )
    if old_state != new_state:
        await conn.execute(
            "INSERT INTO state_log (user_id, old_state, new_state, reason, caused_by) VALUES (?, ?, ?, ?, ?)",
            (user_id, old_state, new_state, reason, caused_by)
        )
    await conn.commit()


async def clear_user_state(user_id: int, caused_by: int = None, reason: str = "состояние снято"):
    """Снять все состояния: вернуть игрока в «нормально»."""
    conn = await get_db()
    cursor = await conn.execute("SELECT state, state_effects FROM users WHERE user_id = ?", (user_id,))
    row = await cursor.fetchone()
    old_state = row['state'] if row else "нормально"
    old_effects = row['state_effects'] if row else "{}"
    if old_state == "нормально":
        return

    await conn.execute(
        "UPDATE users SET state = 'нормально', state_effects = ? WHERE user_id = ?",
        (json.dumps({}), user_id)
    )
    await conn.execute(
        "INSERT INTO state_log (user_id, old_state, new_state, reason, caused_by) VALUES (?, ?, ?, ?, ?)",
        (user_id, old_state, "нормально", reason, caused_by)
    )
    await conn.commit()


async def drop_expired_state(user_id: int, state_col: str, state_effects: str) -> str:
    """Снять все истёкшие состояния. Возвращает актуальный state (через запятую).

    state_effects — JSON dict {ключ: {"applied_at", "minutes", ...}} либо legacy
    плоский формат {"applied_at": "...", "minutes": 60}.
    """
    old_effects = _load_state_effects(state_col, state_effects)
    if not old_effects:
        return "нормально"
    now = datetime.now()
    remaining = {}
    for key, eff in old_effects.items():
        try:
            applied = datetime.strptime(eff['applied_at'], "%Y-%m-%d %H:%M:%S")
            minutes = int(eff.get('minutes', 0))
        except (ValueError, TypeError, KeyError):
            remaining[key] = eff
            continue
        if applied + timedelta(minutes=minutes) <= now:
            await clear_user_state(user_id, eff.get('caused_by'), f"срок действия истёк ({key})")
        else:
            remaining[key] = eff
    return _state_col_value(remaining)


async def count_reports_today(user_id: int) -> int:
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT COUNT(*) AS cnt FROM reports "
        f"WHERE user_id = ? AND {_report_day('created_at')} = ?",
        (user_id, _today_msk())
    )
    row = await cursor.fetchone()
    return row['cnt'] if row else 0


def _wall_today_key() -> str:
    """Ключ текущих игровых суток (10:00 МСК) для лимита «N изречений в сутки»."""
    return today_report_day()


async def count_wall_posts_today(user_id: int) -> int:
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT COUNT(*) AS cnt FROM wall_posts WHERE user_id = ? AND created_day = ?",
        (user_id, _wall_today_key())
    )
    row = await cursor.fetchone()
    return row['cnt'] if row else 0


def wall_post_tier(cost: int) -> int:
    """Номер ценовой ступени по стоимости изречения (0 — бесплатное)."""
    if cost <= 0:
        return 0
    if cost <= 30:
        return 1
    if cost <= 90:
        return 2
    return 3


async def add_wall_post(user_id: int, text: str) -> dict | None:
    """Добавить изречение на стену. Возвращает dict с post_id/cost/tier
    или None, если дневной лимит исчерпан."""
    from config import WALL_TEXT_MAX_LEN, WALL_FREE_PER_DAY, WALL_PAID_STEPS, WALL_REVIEW_TOTAL
    text = text.strip()
    if not text or len(text) > WALL_TEXT_MAX_LEN:
        return None
    count = await count_wall_posts_today(user_id)
    # Ачивка «Стена» (писатель): каждый уровень даёт +1 к дневному лимиту.
    limit = WALL_REVIEW_TOTAL + await get_achievement_level(user_id, "writer")
    if count >= limit:
        return None
    cost = 0
    if count >= WALL_FREE_PER_DAY:
        paid_index = count - WALL_FREE_PER_DAY
        for quota, price in WALL_PAID_STEPS:
            if paid_index < quota:
                cost = price
                break
            paid_index -= quota
    had_nm = True
    if cost > 0:
        user = await get_user(user_id)
        had_nm = bool(user and user['nordmarks'] >= cost)
        if had_nm:
            await remove_nordmarks(user_id, cost, "wall", "Изречение на стене")
    if not had_nm:
        return {"post_id": None, "cost": cost, "tier": wall_post_tier(cost), "need_nm": True}
    conn = await get_db()
    cursor = await conn.execute(
        "INSERT INTO wall_posts (user_id, text, created_day, tier, cost) VALUES (?, ?, ?, ?, ?)",
        (user_id, text, _wall_today_key(), wall_post_tier(cost), cost)
    )
    await conn.commit()
    return {"post_id": cursor.lastrowid, "cost": cost, "tier": wall_post_tier(cost), "need_nm": False}


async def get_wall_posts(page: int = 0, page_size: int = 5) -> list:
    """Страница изречений (свежие сверху): id, text, author (user), cost, tier, created_at."""
    from config import WALL_PAGE_SIZE
    conn = await get_db()
    limit = page_size if page_size else WALL_PAGE_SIZE
    offset = page * limit
    cursor = await conn.execute(
        "SELECT w.*, u.username, u.callsign, u.first_name, u.last_name "
        "FROM wall_posts w LEFT JOIN users u ON u.user_id = w.user_id "
        "ORDER BY w.id DESC LIMIT ? OFFSET ?",
        (limit, offset)
    )
    rows = await cursor.fetchall()
    return [dict(r) for r in rows]


async def get_wall_post(post_id: int) -> dict | None:
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT w.*, u.username, u.callsign, u.first_name, u.last_name "
        "FROM wall_posts w LEFT JOIN users u ON u.user_id = w.user_id "
        "WHERE w.id = ?",
        (post_id,)
    )
    row = await cursor.fetchone()
    return dict(row) if row else None


async def count_wall_posts() -> int:
    conn = await get_db()
    cursor = await conn.execute("SELECT COUNT(*) AS cnt FROM wall_posts")
    row = await cursor.fetchone()
    return row['cnt'] if row else 0


async def delete_wall_post(post_id: int) -> dict | None:
    """Удалить изречение. Возвращает dict {author_id, refund} — возврат ⅓
    цены автору платного изречения (бесплатные — без возврата)."""
    post = await get_wall_post(post_id)
    if not post:
        return None
    await _delete_wall_rows(post_id)
    refund = post['cost'] // 3 if post['cost'] > 0 else 0
    if refund > 0:
        await add_nordmarks(post['user_id'], refund, "wall_refund", "Возврат за удалённое изречение (⅓)")
    return {"author_id": post['user_id'], "refund": refund, "cost": post['cost']}


async def _delete_wall_rows(post_id: int):
    conn = await get_db()
    await conn.execute("DELETE FROM wall_posts WHERE id = ?", (post_id,))
    await conn.commit()


# ============ АРХИВ СТЕНЫ ИЗРЕЧЕНИЙ ============

WALL_ARCHIVE_WEEK_SETTING_KEY = "wall_last_checked_week"

_WALL_MONTHS = {
    1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель", 5: "Май", 6: "Июнь",
    7: "Июль", 8: "Август", 9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь",
}


def _wall_archive_title(start_day: str, end_day: str) -> str:
    """Заголовок записи архива стены — «неделя · месяц · год».

    Одна календарная неделя: «Неделя 38 · Сентябрь 2026». Несколько недель
    (стена копилась и не архивировалась): период по датам с диапазоном недель
    «02.09 — 20.09 2026 · Недели 36–38».
    """
    try:
        sd = datetime.strptime(start_day[:10], "%Y-%m-%d")
        ed = datetime.strptime(end_day[:10], "%Y-%m-%d")
    except (TypeError, ValueError):
        return f"Архив {start_day} — {end_day}"
    sy, sw, _ = sd.isocalendar()
    ey, ew, _ = ed.isocalendar()
    if sy == ey and sw == ew:
        return f"Неделя {sw} · {_WALL_MONTHS.get(ed.month, ed.month)} {ed.year}"
    if sy == ey:
        weeks = f"Недели {sw}" + (f"–{ew}" if ew != sw else "")
        return f"{sd:%d.%m} — {ed:%d.%m} {ed.year} · {weeks}"
    return f"{sd:%d.%m.%Y} — {ed:%d.%m.%Y}"


async def _all_wall_posts() -> list:
    """Все изречения на стене (свежие сверху) с авторами — как get_wall_posts.

    Период архива считается по created_day (сутки по МСК), у старых записей
    пустой — запасёмся и created_at.
    """
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT w.*, u.username, u.callsign, u.first_name, u.last_name "
        "FROM wall_posts w LEFT JOIN users u ON u.user_id = w.user_id "
        "ORDER BY w.id DESC"
    )
    return await cursor.fetchall()


async def add_wall_archive(title: str, period_start: str, period_end: str,
                           post_count: int) -> int:
    conn = await get_db()
    cursor = await conn.execute(
        "INSERT INTO wall_archives (title, period_start, period_end, post_count) "
        "VALUES (?, ?, ?, ?)",
        (title, period_start, period_end, post_count)
    )
    await conn.commit()
    return cursor.lastrowid


async def _copy_wall_posts_to_archive(archive_id: int, posts: list):
    conn = await get_db()
    rows = [
        (archive_id, p['id'], p['user_id'], p['text'], p['created_at'],
         (p.get('created_day') or ''), p.get('cost') or 0, p.get('tier') or 0)
        for p in posts
    ]
    if rows:
        await conn.executemany(
            "INSERT INTO wall_archive_posts "
            "(archive_id, post_id, user_id, text, created_at, created_day, cost, tier) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            rows
        )
    await conn.commit()


async def clear_wall_posts() -> int:
    """Очистить стену после архивации. Возвращает число удалённых записей."""
    conn = await get_db()
    cursor = await conn.execute("DELETE FROM wall_posts")
    await conn.commit()
    return cursor.rowcount


async def count_wall_archives() -> int:
    conn = await get_db()
    cursor = await conn.execute("SELECT COUNT(*) AS n FROM wall_archives")
    row = await cursor.fetchone()
    return row['n'] if row else 0


async def get_wall_archives(page: int = 0, page_size: int = 8) -> list:
    """Записи архива (новые сверху): id, title, период, число изречений."""
    conn = await get_db()
    offset = max(0, page) * page_size
    cursor = await conn.execute(
        "SELECT id, title, period_start, period_end, post_count, archived_at "
        "FROM wall_archives ORDER BY id DESC LIMIT ? OFFSET ?",
        (page_size, offset)
    )
    return await cursor.fetchall()


async def get_wall_archive(archive_id: int) -> dict | None:
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT id, title, period_start, period_end, post_count, archived_at "
        "FROM wall_archives WHERE id = ?",
        (archive_id,)
    )
    return await cursor.fetchone()


async def count_wall_archive_posts(archive_id: int) -> int:
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT COUNT(*) AS n FROM wall_archive_posts WHERE archive_id = ?",
        (archive_id,)
    )
    row = await cursor.fetchone()
    return row['n'] if row else 0


async def get_wall_archive_posts(archive_id: int, page: int = 0,
                                 page_size: int = 5) -> list:
    """Страница изречений внутри записи архива (свежие сверху) — как на стене."""
    conn = await get_db()
    offset = max(0, page) * page_size
    cursor = await conn.execute(
        "SELECT p.*, u.username, u.callsign, u.first_name, u.last_name "
        "FROM wall_archive_posts p LEFT JOIN users u ON u.user_id = p.user_id "
        "WHERE p.archive_id = ? ORDER BY p.post_id DESC LIMIT ? OFFSET ?",
        (archive_id, page_size, offset)
    )
    return await cursor.fetchall()


async def maybe_archive_wall_weekly():
    """Еженедельная проверка стены (пн 10:00 МСК, вызывается из суточного цикла).

    Раз в календарную неделю (ключ в settings, смена недели — триггер): если
    изречений на стене больше одной страницы (WALL_PAGE_SIZE) — собрать всё в
    архив с периодом от первой до последней записи и очистить стену. Если
    меньше или ровно страница — стену не трогаем, следующая проверка через
    неделю: период архива тогда покроет несколько недель одним периодом.

    Возвращает None, если проверка на этой неделе уже была; dict с результатом
    иначе: {"archived": bool, "count": int, "archive_id": int | None}.
    """
    from datetime import datetime
    from utils.helpers import MOSCOW_TZ
    from config import WALL_PAGE_SIZE
    conn = await get_db()
    now = datetime.now(MOSCOW_TZ)
    year, week, _ = now.isocalendar()
    week_key = f"{year}-W{week:02d}"

    cursor = await conn.execute(
        "SELECT value FROM settings WHERE key = ?", (WALL_ARCHIVE_WEEK_SETTING_KEY,))
    row = await cursor.fetchone()
    if row and row['value'] == week_key:
        return None

    await conn.execute(
        "INSERT INTO settings (key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (WALL_ARCHIVE_WEEK_SETTING_KEY, week_key))
    await conn.commit()

    total = await count_wall_posts()
    if total <= WALL_PAGE_SIZE:
        return {"archived": False, "count": total, "archive_id": None}

    posts = await _all_wall_posts()
    days = []
    for p in posts:
        d = (p.get('created_day') or '').strip()
        if not d:
            d = (p.get('created_at') or '')[:10]
        if d:
            days.append(d)
    period_start = min(days)
    period_end = max(days)
    title = _wall_archive_title(period_start, period_end)
    archive_id = await add_wall_archive(title, period_start, period_end, len(posts))
    await _copy_wall_posts_to_archive(archive_id, posts)
    cleared = await clear_wall_posts()
    return {"archived": True, "count": cleared, "archive_id": archive_id}


async def wall_author_name(user) -> str:
    """Имя автора изречения: позывной, @username, иначе реальное имя."""
    if not user:
        return "Неизвестный"
    from bot.handlers.profile import _pilot_name
    return _pilot_name(user)


def _report_day(date_expr: str) -> str:
    """Отчётные сутки по Нордхайму: от выплаты до выплаты (10:00 МСК → 10:00 МСК).

    created_at хранится в UTC. Сутки начинаются в 10:00 МСК, поэтому к времени
    отчёта прибавляется смещение «+3 часа минус 10 часов» = −7:00, и берётся
    дата. Отчёт, сданный в 04:00 МСК, попадает в ПРЕДЫДУЩИЕ сутки (те, что
    закрылись в 10:00) — он честно заработан ночью.
    """
    from config import REPORT_DAY_START_HOUR, REPORT_DAY_START_MINUTE
    offset_minutes = 3 * 60 - REPORT_DAY_START_HOUR * 60 - REPORT_DAY_START_MINUTE
    sign = "+" if offset_minutes >= 0 else "-"
    return (f"date({date_expr}, '{sign}{abs(offset_minutes)} minutes')")


def report_day_value_of(created_at: str) -> str:
    """Отчётные сутки 'YYYY-MM-DD' для created_at (UTC) — ровно то же правило, что у
    SQL _report_day. Нужна вне SQL: например, для похвалы (день самого отчёта) и
    для отображения. None, если дата не разобралась."""
    from config import REPORT_DAY_START_HOUR, REPORT_DAY_START_MINUTE
    try:
        dt = datetime.strptime(str(created_at)[:19], "%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return None
    offset_minutes = 3 * 60 - REPORT_DAY_START_HOUR * 60 - REPORT_DAY_START_MINUTE
    return (dt + timedelta(minutes=offset_minutes)).strftime("%Y-%m-%d")


def today_report_day() -> str:
    """Текущие отчётные сутки 'YYYY-MM-DD' — то же, что SQL _TODAY_MSK, но в Python.

    Нужно для правила «одобрил отчёт за прошлые сутки после 10:00 → плати сразу»:
    отчёт из более ранних суток, чем сегодняшние, утренний цикл уже пропустил.
    """
    return report_day_value_of(datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"))


def _today_msk() -> str:
    """Текущие отчётные сутки 'YYYY-MM-DD' — ЕДИНЫЙ источник «сейчас» для денег.

    Раньше здесь стоял готовый SQL-фрагмент date('now', '-420 minutes'), а рядом
    жил его Python-двойник today_report_day(). Две реализации «сейчас» — это
    риск: на такой разъезд попадает решение «платить сразу или в 10:00», то есть
    деньги. Теперь эталон один (Python), а в SQL уходит строкой-параметром.
    """
    return today_report_day()


# Готовая SQL-строка «текущие сутки». Оставлена только для случаев, где запрос
# НЕ принимает параметры; везде, где решаются деньги или доступ, используй
# _today_msk() как '?'-параметр.
_TODAY_MSK = _report_day("'now'")


def report_day_bounds() -> tuple:
    """Границы текущих отчётных суток как datetime в МСК: (начало, конец).

    Начало — ближайший прошедший 10:00 МСК, конец — следующий. Отчёты внутри
    этого окна оплачиваются вместе в 10:00.
    """
    from config import REPORT_DAY_START_HOUR, REPORT_DAY_START_MINUTE
    msk = timezone(timedelta(hours=3))
    now = datetime.now(msk)
    start = now.replace(hour=REPORT_DAY_START_HOUR, minute=REPORT_DAY_START_MINUTE,
                        second=0, microsecond=0)
    if now < start:
        start -= timedelta(days=1)
    return start, start + timedelta(days=1)


def report_day_label_for(day: str) -> str:
    """Заголовок отчётных СУТОК конкретного отчёта по его дню 'YYYY-MM-DD'.

    Нужно там, где показывают сутки конкретного отчёта (карточка на проверке,
    «принять», «поправить цифры»): у отчёта, сданного до 10:00 МСК, сутки
    ПРЕДЫДУЩИЕ, и надпись про текущие сутки вводила в заблуждение — админ видел
    «30.09 — 01.10» для отчёта за 29-е число. Метка берётся из дня самого
    отчёта, поэтому совпадает с решением об оплате в approve_report.
    """
    from config import REPORT_DAY_START_HOUR, REPORT_DAY_START_MINUTE
    try:
        d = datetime.strptime(str(day)[:10], "%Y-%m-%d")
    except (ValueError, TypeError):
        return report_day_label()
    start = d.replace(hour=REPORT_DAY_START_HOUR, minute=REPORT_DAY_START_MINUTE)
    end = start + timedelta(days=1)
    fmt = "%d.%m %H:%M"
    return f"{start.strftime(fmt)} — {end.strftime(fmt)}"


def shift_report_day(day: str, delta_days: int) -> str:
    """Сдвинуть день отчётных суток 'YYYY-MM-DD' на N суток."""
    try:
        d = datetime.strptime(str(day)[:10], "%Y-%m-%d")
    except (ValueError, TypeError):
        return day
    return (d + timedelta(days=delta_days)).strftime("%Y-%m-%d")


def report_day_label(offset_days: int = 0) -> str:
    """Заголовок ТЕКУЩИХ отчётных суток (со сдвигом): «28.09 10:00 — 29.09 10:00»."""
    return report_day_label_for(shift_report_day(today_report_day(), offset_days))


def created_at_msk(created_at: str) -> str:
    """Время сдачи отчёта по МСК для интерфейса: «30.09 08:40».

    created_at в базе — UTC (SQLite CURRENT_TIMESTAMP), поэтому без пересчёта
    админ видел сдачу в 05:40 вместо 08:40.
    """
    try:
        dt = datetime.strptime(str(created_at)[:19], "%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return "—"
    msk = timezone(timedelta(hours=3))
    return dt.replace(tzinfo=timezone.utc).astimezone(msk).strftime("%d.%m %H:%M")


async def _report_base_total(conn, user_id: int, exclude_id: int = None):
    """Сколько пилот накопил в ПРОШЛЫХ отчётных сутках — максимум поля «всего».

    В оплате это поле больше не участвует: «всего» — это остаток очков пилота в
    регионе, а не обязательный счётчик (очки могут уйти на оборону, регион может
    смениться). Функция оставлена для статистики и справки.

    Отклонённые отчёты в базу не идут: иначе отклонённая завышенная заявка
    вводила бы в заблуждение при разборе.
    """
    sql = ("SELECT MAX(total_troops) AS base FROM reports "
           "WHERE user_id = ? AND status != 'rejected' AND total_troops IS NOT NULL "
           f"AND {_report_day('created_at')} < ?")
    params = [user_id, _today_msk()]
    if exclude_id:
        sql += " AND id != ?"
        params.append(exclude_id)
    row = await (await conn.execute(sql, tuple(params))).fetchone()
    return row['base'] if row else None


def _report_cycle_day_of(created_at: str) -> str:
    """Отчётные сутки ('YYYY-MM-DD') конкретного отчёта по его created_at (UTC).

    Нужна, когда отчёт одобряют в следующие сутки: лимит считается по суткам САМОГО
    отчёта, а не по текущим. Должна совпадать с report_day_value_of: раньше метка
    UTC трактовалась как МСК, и отчёты, сданные ночью/утром (до границы в МСК),
    получали НЕВЕРНЫЕ сутки именно там, где лимит решает судьбу выплаты.
    """
    return report_day_value_of(created_at)


async def _report_assigned_today(conn, user_id: int, exclude_id: int = None,
                                 cycle_day: str = None) -> int:
    """Сумма заявок «за сутки» по всем не-отклонённым отчётам суток.

    ⚠️ Это СПРАВОЧНАЯ величина, а не сумма к выплате: несколько отчётов за сутки
    больше не складываются (см. report_payout_context — платит последний).
    Нужна для показа в админке и в форме отчёта.
    """
    if cycle_day:
        day_sql = "?"
        params = [user_id, cycle_day]
    else:
        day_sql = "?"
        params = [user_id, _today_msk()]
    sql = ("SELECT COALESCE(SUM(COALESCE(credited_troops, troops_reported)), 0) AS s FROM reports "
           "WHERE user_id = ? AND status != 'rejected' "
           f"AND {_report_day('created_at')} = {day_sql}")
    if exclude_id:
        sql += " AND id != ?"
        params.append(exclude_id)
    row = await (await conn.execute(sql, tuple(params))).fetchone()
    return row['s'] if row else 0


async def _last_report_id_of_day(conn, user_id: int, cycle_day: str = None):
    """id ПОСЛЕДНЕГО не-отклонённого отчёта суток — тот, чьё «за сутки» и платится.

    Сортировка (created_at, id) — та же, что у региональной статистики, чтобы
    «последний отчёт» понимался везде одинаково. Отклонённые не считаются: если
    последний отчёт отклонили, последним становится предыдущий.
    """
    row = await (await conn.execute(
        "SELECT id FROM reports WHERE user_id = ? AND status != 'rejected' "
        f"AND {_report_day('created_at')} = ? "
        "ORDER BY created_at DESC, id DESC LIMIT 1",
        (user_id, cycle_day or _today_msk()))).fetchone()
    return row['id'] if row else None


async def _report_paid_today(conn, user_id: int, cycle_day: str = None,
                             exclude_id: int = None) -> int:
    """Сколько УЖЕ реально выплачено за эти сутки (отчёты с paid = 1).

    Нужно, чтобы при смене «последнего» отчёта (например, его отклонили и
    последним стал предыдущий) не выплатить за сутки дважды.

    Статус здесь ВАЖЕН: фильтра status != 'rejected' быть не должно. Отчёт, который
    уже оплатили, а потом отклонили, всё равно принёс пилоту деньги — забыв его в
    подсчёте, мы бы выплатили предыдущему отчёту сверху.

    Fallback на troops_reported — не формальность: у выплаченных отчётов, созданных
    ДО v0.22.0, credited_troops бывает NULL, и сумма по ним вышла бы нулевой, то
    есть «уже выплачено» обнулилось и сутки можно было бы заплатить сверху. У
    погашенных отчётов credited_troops = 0 (не NULL), поэтому fallback им не мешает.
    """
    sql = ("SELECT COALESCE(SUM(COALESCE(credited_troops, troops_reported, 0)), 0) AS s "
           "FROM reports WHERE user_id = ? AND paid = 1 "
           f"AND {_report_day('created_at')} = ?")
    params = [user_id, cycle_day or _today_msk()]
    if exclude_id:
        sql += " AND id != ?"
        params.append(exclude_id)
    row = await (await conn.execute(sql, tuple(params))).fetchone()
    return row['s'] if row else 0


async def report_day_credited_total(user_id: int, exclude_id: int = None, day: str = None) -> int:
    """Сколько начислено за отчётные сутки — берём ПОСЛЕДНИЙ одобренный отчёт.

    Раньше здесь была сумма по всем одобренным отчётам суток, но с v0.22.0 платится
    не сумма, а «за сутки» из последнего отчёта (суточное — снимок). Похвала в общий
    чат обязана считаться от того же числа, что и выплата, иначе пилот, сдавший три
    отчёта, получал бы публичную похвалу за тройной фарм, которого ему не платили.

    Висящие (pending) отчёты не считаются: похвала приходит только за принятые.
    Порядок тот же, что у выплаты, — (created_at, id).

    day — конкретные отчётные сутки 'YYYY-MM-DD'. По умолчанию — текущие. День САМОГО
    отчёта нужен, когда отчёт одобряют на следующих сутках: иначе очка пилота за вчера
    не попадут в «сегодня», и похвала не уйдёт.
    """
    conn = await get_db()
    params = [user_id, day if day is not None else _today_msk()]
    sql = ("SELECT COALESCE(credited_troops, troops_reported, 0) AS s "
           "FROM reports WHERE user_id = ? AND status = 'approved' "
           f"AND {_report_day('created_at')} = ?")
    if exclude_id:
        sql += " AND id != ?"
        params.append(exclude_id)
    sql += " ORDER BY created_at DESC, id DESC LIMIT 1"
    row = await (await conn.execute(sql, tuple(params))).fetchone()
    return row['s'] if row else 0


async def get_report_notify_tier(user_id: int, day: str = None) -> int:
    """Максимальный уровень похвалы, уже отправленный за отчётные сутки (0 — не было).

    day — сутки 'YYYY-MM-DD' (по умолчанию текущие).
    """
    conn = await get_db()
    row = await (await conn.execute(
        "SELECT tier FROM report_notify_tiers WHERE user_id = ? AND day = ?",
        (user_id, day if day is not None else _today_msk())
    )).fetchone()
    return row['tier'] if row else 0


async def bump_report_notify_tier(user_id: int, tier: int, day: str = None) -> int:
    """Запомнить отправленный уровень похвалы за сутки. Возвращает уровень после записи.

    Уровень только растёт: повторное оповещение того же уровня за сутки невозможно,
    но переход на следующий (например, 160 → 350 за день) проходит.

    day — сутки 'YYYY-MM-DD' (по умолчанию текущие).
    """
    conn = await get_db()
    await conn.execute(
        "INSERT INTO report_notify_tiers (user_id, day, tier) VALUES (?, ?, ?) "
        "ON CONFLICT(user_id, day) DO UPDATE SET tier = MAX(tier, excluded.tier), "
        "updated_at = CURRENT_TIMESTAMP",
        (user_id, day if day is not None else _today_msk(), tier)
    )
    await conn.commit()
    return await get_report_notify_tier(user_id, day=day)


async def report_payout_context(user_id: int, daily_claim: int, total_claim: int = 0,
                                exclude_id: int = None, cycle_day: str = None) -> dict:
    """Расчёт суммы к оплате за отчёт: платим ЗА СУТКИ, в которые пилот сдал отчёт.

    Правило: к оплате идёт заявка «за сутки» (суточный фарм), и только она. Поле
    «всего» в оплате НЕ участвует — это остаток очков пилота в регионе, а не
    обязательный счётчик.

    НЕСКОЛЬКО ОТЧЁТОВ ЗА СУТКИ НЕ СУММИРУЮТСЯ (правило владельца 2026-10-03).
    Суточное — это снимок, а не приход: за сутки оно копится с нуля до своего
    максимума, и каждый следующий отчёт показывает БОЛЬШЕЕ значение, заменяя
    предыдущее. Платится поэтому «за сутки» из ПОСЛЕДНЕГО отчёта суток, а не
    сумма заявок. Иначе пилот, сдавший три отчёта за день, получил бы тройную
    выплату за один и тот же суточный фарм.

    Из этого следует важное для выплат:
      • отчёт, который НЕ последний в своих сутках, платит 0 (superseded) — но
        он остаётся в истории и считается статистикой;
      • потолок report_daily_pay_cap (по умолчанию 4000) теперь ограничивает
        ОДИН итоговый снимок, а не сумму за сутки;
      • за сутки платят один раз: из снимка вычитается уже выплаченное за эти сутки
        (already_paid, см. ниже), результат не опускается ниже нуля.

    cycle_day — конкретные отчётные сутки 'YYYY-MM-DD' вместо текущих. Нужен при
    одобрении отчёта из прошлых суток: и «последний отчёт», и уже выплаченное
    считаются по тем суткам, в которых отчёт был сдан.

    Возвращает: payable (к оплате), claim (заявка), assigned_today (справочно, сумма
    заявок суток), cap, capped_by_limit, room_today, superseded, is_last,
    already_paid, total_claim (справочно), base (справочно), base_known,
    prev_day_total, day_label.
    """
    conn = await get_db()
    day = cycle_day or today_report_day()
    assigned = await _report_assigned_today(conn, user_id, exclude_id, day)
    claim = max(0, daily_claim or 0)

    cap = await get_report_daily_pay_cap()
    # 0 — без ограниления.
    cap = cap if (cap or 0) > 0 else None

    # Платит только последний отчёт суток.
    #   exclude_id is None → это предпросмотр НОВОЙ заявки (форма отчёта): новая
    #     заявка по определению последняя, платится она.
    #   exclude_id задан → это уже существующий отчёт (одобрение/правка): он
    #     последний, если в сутках нет более свежих не-отклонённых отчётов.
    if exclude_id is None:
        is_last = True
    else:
        last_id = await _last_report_id_of_day(conn, user_id, day)
        is_last = last_id is None or last_id == exclude_id

    already_paid = await _report_paid_today(conn, user_id, day, exclude_id)

    if not is_last:
        # Не последний отчёт суток: платить нечего, его заявку уже перекрыл
        # более свежий снимок.
        payable = 0
    else:
        payable = min(claim, cap) if cap is not None else claim
        # За сутки платят ОДИН раз: из снимка вычитается всё, что по этим суткам уже
        # выплачено, и результат не опускается ниже нуля. Без вычитания сутки
        # переплачивались бы: снимок 50 оплачен в 10:00, пилот сдал отчёт на 900 —
        # и к уже выданным 50 прибавилось бы ещё 900.
        # Ноль означает и «последний отчёт отклонили, заплатили предыдущий»: деньги
        # за сутки уже у пилота, повторная выплата была бы двойной.
        payable = max(0, payable - already_paid)

    return {
        "payable": max(0, payable),
        "claim": claim,
        "total_claim": max(0, total_claim or 0),
        "assigned_today": assigned,
        "cap": cap,
        "capped_by_limit": cap is not None and claim > cap,
        "room_today": None if cap is None else max(0, cap - max(assigned, already_paid)),
        "superseded": not is_last,
        "is_last": is_last,
        "already_paid": already_paid,
        "base": await _report_base_total(conn, user_id, exclude_id),
        "base_known": True,
        "prev_day_total": await report_prev_day_total(user_id),
        "cycle_day": day,
        "day_label": report_day_label_for(cycle_day) if cycle_day else report_day_label(),
    }


async def report_prev_day_total(user_id: int) -> int:
    """Сколько пилот сдал за ПРОШЛЫЕ отчётные сутки (снимок, не сумма заявок).

    Подставляется в форму отчёта, чтобы пилот видел, с чем сравнивать сегодняшний
    фарм, и не путал накопленное «всего» с суточным заработком.

    С v0.22.0 берётся ПОСЛЕДНИЙ не-отклонённый отчёт прошлых суток, а не сумма
    заявок: суточное — снимок (см. report_payout_context), и сравнивать сегодняшний
    снимок с вчерашней суммой нескольких отчётов бессмысленно — она никогда бы не
    совпала с оплатой. Порядок тот же, что у выплаты, — (created_at, id).
    """
    conn = await get_db()
    row = await (await conn.execute(
        "SELECT COALESCE(credited_troops, troops_reported, 0) AS s "
        "FROM reports WHERE user_id = ? AND status != 'rejected' "
        f"AND {_report_day('created_at')} = date(?, '-1 day') "
        "ORDER BY created_at DESC, id DESC LIMIT 1",
        (user_id, _today_msk())
    )).fetchone()
    return row['s'] if row else 0


async def correct_report_numbers(report_id: int, troops_reported: int, total_troops: int,
                                 corrected_by: int = None) -> dict:
    """Исправить цифры отчёта: «за сутки» и «всего» (для супер-админа).

    Пилоты часто путают поля (пишут «всё накопленное» в «за сутки»), и такая заявка
    искажает статистику. Здесь заявка заменяется на проверенную, а credited_troops
    ПЕРЕСЧИТЫВАЕТСЯ по правилу report_payout_context — как при обычной сдаче, поэтому
    оплата остаётся в пределах суточного лимита.

    Править можно только отчёты в статусе pending: одобренные и выплаченные не трогаем.
    Возвращает контекст оплаты после правки (claim/payable/assigned_today) либо
    {'error': ...}.

    Счёт идёт по суткам САМОГО отчёта (по его created_at): висящий отчёт за прошлые
    сутки не должен показывать лимит и «уже засчитано» сегодняшнего дня.
    """
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT user_id, troops_reported, total_troops, status, created_at FROM reports WHERE id = ?",
        (report_id,)
    )
    row = await cursor.fetchone()
    if not row:
        return {"error": "Отчёт не найден."}
    if row['status'] != 'pending':
        return {"error": f"Отчёт #{report_id} уже не в очереди "
                         f"(статус: {row['status']}) — править нельзя."}

    ctx = await report_payout_context(row['user_id'], troops_reported, total_troops,
                                      exclude_id=report_id,
                                      cycle_day=_report_cycle_day_of(row['created_at']))
    await conn.execute(
        "UPDATE reports SET troops_reported = ?, total_troops = ?, credited_troops = ? "
        "WHERE id = ?",
        (troops_reported, total_troops, ctx["payable"], report_id)
    )
    await conn.commit()
    ctx['old_daily'] = row['troops_reported']
    ctx['old_total'] = row['total_troops']
    return ctx


async def add_report(user_id: int, screenshot_file_id: str, troops_reported: int, total_troops: int = 0, region: str = ""):
    """Добавить отчёт. Возвращает (report_id, credited_troops).

    troops_reported — заявка «за сутки», total_troops — заявка «всего»,
    credited_troops — сумма к оплате (см. report_payout_context).

    Регион нормализуется здесь, а не в хендлере: колонка TEXT, а региональная
    статистика группирует по ней (`GROUP BY region`), поэтому «07» и «7» стали бы
    двумя разными регионами и силы пилота разъехались бы между ними. add_report —
    единственная точка записи в reports, поэтому гарантия тут одна и не обходится.
    """
    region_text = str(region or "").strip()
    if region_text.isdigit():
        region = str(int(region_text))
    ctx = await report_payout_context(user_id, troops_reported, total_troops)
    conn = await get_db()
    cursor = await conn.execute(
        "INSERT INTO reports (user_id, screenshot_file_id, troops_reported, total_troops, region, credited_troops) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, screenshot_file_id, troops_reported, total_troops, region, ctx["payable"])
    )
    await conn.commit()
    return cursor.lastrowid, ctx["payable"]


async def approve_report(report_id: int, reviewed_by: int, troops: int = None):
    """Одобрить отчёт. Возвращает сумму к начислению (войск) или False, если отчёт не найден.

    Сумма к начислению = «за сутки» из ПОСЛЕДНЕГО по времени отчёта отчётных суток,
    в пределах суточного лимита (правило report_payout_context). Более ранние отчёты
    суток выплату не получают: суточное копится от нуля до максимума и каждый следующий
    отчёт его ЗАМЕНЯЕТ, а не складывается с предыдущими. Если последний отчёт ещё не
    одобрен, выплата суток ждёт его — платить не за тот снимок нельзя.

    Сумма ПЕРЕСЧИТЫВАЕТСЯ в момент одобрения, а не берётся из credited_troops: пока
    отчёт висел, пилот мог сдать ещё отчёты за эти сутки. Пересчёт гарантирует, что
    лимит не превысится.

    Лимит берётся по суткам САМОГО отчёта, а не по текущим: отчёт, сданный вчера и
    одобренный сегодня, считается по вчерашнему лимиту — иначе сегодняшние отчёты
    пилота урезали бы вчерашний фарм.

    Переданный troops может только УМЕНЬШИТЬ сумму (частичное одобрение админом),
    но не увеличить её выше заявки.

    МОМЕНТ ОПЛАТЫ (v0.18.6, правило владельца): отчёт за сутки, чей «расчётный»
    10:00 ещё НЕ наступил (отчёт текущих суток), оплачивается раз в сутки в 10:00 МСК
    функцией payout_reports(). А вот отчёт, одобренный ПОСЛЕ того, как его 10:00 уже
    прошло (это всегда отчёт из прошлых суток: утренний цикл его пропустил), а заняться
    им некому до завтра — платится СРАЗУ при одобрении, чтобы пилот не ждал почти
    сутки уже заработанного. Мгновенная оплата идёт через _apply_report_payout, той же
    формулой, что и суточная: войска + опыт 1:1, нордмарки за вычетом налога в казну.
    """
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT user_id, troops_reported, created_at FROM reports WHERE id = ?", (report_id,)
    )
    row = await cursor.fetchone()
    if not row:
        # Не 0, а тоже число: вызывающий код трактует результат как сумму к оплате, а
        # False == 0 в Python — раньше пилот получал «К оплате 0: суточный лимит уже
        # выбран» вместо «отчёт не найден». Отчёт мог исчезнуть только гонкой с БД, но
        # врать о причине нельзя.
        logger.warning("approve_report: отчёт %s не найден", report_id)
        return 0

    # Лимит считаем по суткам САМОГО отчёта: одобрение часто приходит на следующие
    # сутки, и по текущим суткам лимит уже съеден другими отчётами пилота.
    ctx = await report_payout_context(row['user_id'], row['troops_reported'],
                                      exclude_id=report_id,
                                      cycle_day=_report_cycle_day_of(row['created_at']))
    amount = ctx["payable"]
    if troops is not None:
        amount = min(amount, max(0, troops))

    # Правило «одобрил после расчётных 10:00 → плати сразу». Условие: отчёт за
    # сутки РАНЬШЕ текущих — ровно тогда его 10:00 уже прошло. Одобрение и «захват»
    # (paid=1) делаем в ОДНОМ запросе (WHERE status='pending'): суточный цикл видит
    # только approved+paid=0, поэтому гонки «оплатили дважды» быть не может.
    report_day = report_day_value_of(row['created_at'])
    if report_day is not None and report_day < today_report_day():
        cur = await conn.execute(
            "UPDATE reports SET status = 'approved', reviewed_by = ?, credited_troops = ?, "
            "paid = 1 WHERE id = ? AND status = 'pending'",
            (reviewed_by, amount, report_id)
        )
        claimed = cur.rowcount
        if claimed:
            if ctx["superseded"]:
                # Отчёт перекрыт более свежим снимком: денег не приносит. Но paid=1
                # ему НЕ ставим — если тот, кто его перекрыл, потом отклонит, этот
                # отчёт снова станет последним, и его пересчитает
                # _reopen_report_day() (см. reject_report).
                await conn.execute(
                    "UPDATE reports SET paid = 0 WHERE id = ?", (report_id,))
            else:
                await _apply_report_payout(conn, row['user_id'], [report_id], amount)
                # Более ранние отчёты тех же суток выплату не получают: она уже учтена
                # по последнему отчёту. Помечаем оплаченными, чтобы суточный цикл их
                # потом не подхватил и не выплатил повторно.
                await _suppress_superseded(conn, row['user_id'], report_id,
                                           cycle_day=report_day, credited=0)
        await conn.commit()
        return amount if claimed else 0

    cur = await conn.execute(
        "UPDATE reports SET status = 'approved', reviewed_by = ?, credited_troops = ?, paid = 0 "
        "WHERE id = ? AND status = 'pending'",
        (reviewed_by, amount, report_id)
    )
    await conn.commit()
    return amount if cur.rowcount else 0


async def _suppress_superseded(conn, user_id: int, winner_id: int,
                               cycle_day: str = None, credited: int = 0) -> int:
    """Погасить более ранние ОДОБРЕННЫЕ отчёты тех же суток, что и winner_id.

    Они не приносят денег: их заявку «за сутки» перекрыл более свежий снимок
    (см. report_payout_context). Ставим paid=1 и credited_troops=credited, чтобы
    суточный цикл их больше не видел и не выплатил повторно. Возвращает число
    погашенных отчётов.

    Только status='approved' — и это важно: PENDING нельзя гасить. Отчёт, который
    ещё не рассмотрен, не может быть «перекрыт снимком» в смысле выплаты, и его
    credited_troops = 0 пережил бы отклонение того, кто его перекрывал: сутки
    остались бы с принятым отчётом и нулевой выплатой.
    """
    cur = await conn.execute(
        "UPDATE reports SET paid = 1, credited_troops = ? "
        f"WHERE user_id = ? AND status = 'approved' AND id != ? AND paid = 0 "
        f"AND {_report_day('created_at')} = ?",
        (credited, user_id, winner_id, cycle_day or _today_msk())
    )
    return cur.rowcount or 0


async def _apply_report_payout(conn, user_id: int, report_ids: list, troops_total: int) -> dict:
    """Начислить пилоту оплату за уже «захваченные» отчёты (одна функция для суточного
    цикла и мгновенной оплаты при одобрении).

    report_ids считаются ПРИНАДЛЕЖАЩИМИ этому циклу выплаты: вызывающий обязан
    пометить их paid=1 до/внутри вызова и не звать функцию дважды для одного отчёта.
    Возвращает итог для уведомления (как у payout_reports) либо None при troops_total
    <= 0 (ничего начислять). НЕ делает conn.commit() — вызывающий завершает сделку.
    """
    placeholders = ", ".join("?" * len(report_ids))
    if troops_total <= 0:
        await conn.execute(f"UPDATE reports SET paid = 1 WHERE id IN ({placeholders})", report_ids)
        return None
    # Ставка индивидуальная: у пилота с медалью налог ниже (report_tax_percent_for).
    tax_percent = await report_tax_percent_for(user_id)
    tax = int(troops_total * tax_percent / 100)
    nordmarks = troops_total - tax
    # Войска = накопленный опыт (звание). xp_balance = тратимый опыт, 1:1 с фармом
    # и без налога: налог платится только с выплачиваемых нордмарок.
    await conn.execute(
        "UPDATE users SET troops = troops + ?, xp_balance = COALESCE(xp_balance, 0) + ? "
        "WHERE user_id = ?",
        (troops_total, troops_total, user_id)
    )
    await conn.execute("UPDATE users SET nordmarks = nordmarks + ? WHERE user_id = ?", (nordmarks, user_id))
    await conn.execute(
        "INSERT INTO transactions (to_user, amount, tx_type, description) VALUES (?, ?, ?, ?)",
        (user_id, nordmarks, "report",
         f"Оплата по отчётам (шт: {len(report_ids)}, за вычетом налога)")
    )
    await conn.execute("UPDATE treasury SET balance = balance + ? WHERE id = 1", (tax,))
    if tax > 0:
        await conn.execute(
            "INSERT INTO transactions (to_user, amount, tx_type, description) VALUES (?, ?, ?, ?)",
            (TREASURY_ID, tax, "treasury", f"Налог {tax_percent}% с отчётов")
        )
    await conn.execute(f"UPDATE reports SET paid = 1 WHERE id IN ({placeholders})", report_ids)
    cur = await conn.execute(
        "SELECT troops, nordmarks, promoted_rank, COALESCE(xp_balance, 0) AS xp_balance "
        "FROM users WHERE user_id = ?", (user_id,)
    )
    u = await cur.fetchone()
    if u:
        rank = get_effective_rank(u['troops'], u['promoted_rank'])
        await grant_all_rank_statuses(user_id, rank)
    return {
        'user_id': user_id,
        'troops': troops_total,
        'xp': troops_total,
        'xp_balance': u['xp_balance'] if u else troops_total,
        'nordmarks': nordmarks,
        'tax': tax,
        'count': len(report_ids),
        'total_troops': u['troops'] if u else troops_total,
        'total_nordmarks': u['nordmarks'] if u else nordmarks,
    }


async def payout_reports() -> list:
    """Суточное начисление за одобренные отчёты — в 10:00 МСК, в начале новых суток.

    Платится НЕ сумма отчётов, а «за сутки» только из ПОСЛЕДНЕГО одобренного отчёта
    каждых отчётных суток пилота (правило владельца: суточное — это снимок, оно
    копится с нуля до максимума, и каждый следующий отчёт заменяет предыдущий).
    Поэтому группируем по (пилот, сутки), а не по одному пилоту: иначе три отчёта
    за одни сутки сложились бы в тройную выплату за один суточный фарм.

    Если последний отчёт суток ещё не одобрен (висят earlier-одобренные) — сутки
    не выплачиваются: ждём одобрения последнего, иначе заплатили бы не за тот снимок.

    К выплате берётся credited_troops последнего отчёта — это дельта, посчитанная при
    одобрении (заявка под капом минус уже выплаченное за сутки). Поэтому здесь НЕ
    вычитается уже выплаченное повторно: subtraction живёт в approve_report /
    report_payout_context, иначе сутки платились бы на выплаченное меньше.

      • войска (users.troops) — это накопленный опыт, по нему звание;
      • опыт (users.xp_balance) — тратимый, копится 1:1 с суточным фармом и НЕ облагается
        налогом: госналог берётся только с выплачиваемых денег;
      • нордмарки = войска за вычетом налога в казну.
    Помечает отчёты оплаченными. Возвращает итоги для уведомлений:
    [{'user_id', 'troops', 'xp', 'nordmarks', 'tax', 'count', 'total_troops', 'total_nordmarks'}]
    """
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT r.user_id, r.id AS report_id, r.created_at, "
        "COALESCE(r.credited_troops, r.troops_reported) AS troops, "
        f"{_report_day('r.created_at')} AS cycle_day "
        "FROM reports r WHERE r.status = 'approved' AND r.paid = 0"
    )
    rows = await cursor.fetchall()
    if not rows:
        return []

    # Кто сдавал отчёты в эти сутки — чтобы отличить «ещё не одобрен последний» от
    # «одобрены все». Не-отклонённые: отклонённый последний не блокирует выплату.
    by_day = {}
    for r in rows:
        by_day.setdefault((r['user_id'], r['cycle_day']), []).append(r)
    unapproved = {}
    for key in by_day:
        uid, day = key
        row = await (await conn.execute(
            "SELECT COUNT(*) AS c FROM reports WHERE user_id = ? AND status = 'pending' "
            f"AND {_report_day('created_at')} = ?",
            (uid, day))).fetchone()
        unapproved[key] = row['c'] if row else 0

    results = []
    for (uid, day), day_rows in by_day.items():
        if unapproved[(uid, day)]:
            continue  # последний ещё не одобрен — платить пока не за что
        # Последний = максимум по (created_at, id), тот же порядок, что в статистике.
        last = max(day_rows, key=lambda r: (r['created_at'], r['report_id']))
        # Сумма к выплате УЖЕ посчитана при одобрении и лежит в credited_troops:
        # approve_report записал туда дельту (заявка под капом минус уже выплаченное
        # за сутки). Вычитать already_paid здесь второй раз нельзя — получилось бы
        # двойное уменьшение (отчёт, одобренный после выплаты части суток, заплатил бы
        # заявку минус выплаченное минус выплаченное). Fallback на troops_reported —
        # для строк, созданных до v0.22.0, где credited_troops ещё NULL.
        amount = max(0, last['troops'] or 0)
        ids = [r['report_id'] for r in day_rows]
        cur = await conn.execute(
            f"UPDATE reports SET paid = 1 WHERE id IN ({', '.join('?' * len(ids))})", ids)
        claimed = cur.rowcount
        if amount > 0 and claimed:
            res = await _apply_report_payout(conn, uid, ids, amount)
            if res:
                results.append(res)
    await conn.commit()
    return results


async def _reopen_report_day(conn, user_id: int, cycle_day: str) -> dict:
    """Пересчитать нового последнего по суткам после отклонения отчёта.

    Зачем: у отчёта, который был последним, `credited_troops` = полная его доля, и он
    оплачен. Если его отклонить, последним становится предыдущий — а его
    `credited_troops` был посчитан, когда он ещё был superseded (0), и он помечен
    paid=1. Без этого пересчёта сутки просто не платились бы: отчёт принят, а деньги
    не выданы (проверено smoke_094/smoke_124).

    Пересчитываем по тем же правилам, что и одобрение: снимок под капом минус уже
    выплаченное за сутки, но не ниже нуля. Если сутки уже закрылись (их 10:00
    прошло) — платим сразу, иначе отчёт ждёт суточного цикла в 10:00.

    Молчим, если нового последнего нет, он не принят или уже оплачен: платить
    нечего, а пересчитывать чужое одобрение нельзя.
    """
    last_id = await _last_report_id_of_day(conn, user_id, cycle_day)
    if last_id is None:
        return {}
    row = await (await conn.execute(
        "SELECT troops_reported, status, paid FROM reports WHERE id = ?",
        (last_id,))).fetchone()
    if not row or row['status'] != 'approved' or row['paid']:
        return {}

    claim = max(0, row['troops_reported'] or 0)
    cap = await get_report_daily_pay_cap()
    cap = cap if (cap or 0) > 0 else None
    already = await _report_paid_today(conn, user_id, cycle_day, exclude_id=last_id)
    amount = max(0, (min(claim, cap) if cap is not None else claim) - already)
    instant = bool(cycle_day) and cycle_day < today_report_day()
    await conn.execute(
        f"UPDATE reports SET credited_troops = ?, paid = {1 if instant else 0} WHERE id = ?",
        (amount, last_id))
    if instant:
        await _apply_report_payout(conn, user_id, [last_id], amount)
        await _suppress_superseded(conn, user_id, last_id,
                                   cycle_day=cycle_day, credited=0)
    return {'report_id': last_id, 'amount': amount, 'instant': instant}


async def reject_report(report_id: int, reviewed_by: int):
    conn = await get_db()
    row = await (await conn.execute(
        "SELECT user_id, created_at FROM reports WHERE id = ?", (report_id,))).fetchone()
    await conn.execute(
        "UPDATE reports SET status = 'rejected', reviewed_by = ? WHERE id = ?",
        (reviewed_by, report_id)
    )
    await conn.commit()
    # Отклонение могло отдать сутки предыдущему отчёту — пересчитываем его долю.
    if row:
        await _reopen_report_day(conn, row['user_id'],
                                 _report_cycle_day_of(row['created_at']))
        await conn.commit()


async def get_pending_reports():
    conn = await get_db()
    # Второй ключ обязателен: у отчётов, сданных в одну секунду, created_at совпадает,
    # и без r.id SQLite возвращал их в произвольном порядке — «Следующий ▶️» в админке
    # показывал тот же отчёт снова (очередь «перемешивалась» между запросами).
    cursor = await conn.execute(
        """SELECT r.*, u.first_name, u.username, u.callsign FROM reports r
           JOIN users u ON r.user_id = u.user_id
           WHERE r.status = 'pending' ORDER BY r.created_at, r.id"""
    )
    return await cursor.fetchall()


async def get_approved_reports(limit: int = 20) -> list:
    """Последние принятые (approved) отчёты — для вкладки «Принятые отчёты»."""
    conn = await get_db()
    cursor = await conn.execute(
        """SELECT r.*, u.first_name, u.username, u.callsign FROM reports r
           JOIN users u ON r.user_id = u.user_id
           WHERE r.status = 'approved'
           ORDER BY r.created_at DESC, r.id DESC LIMIT ?""",
        (limit,)
    )
    return await cursor.fetchall()


async def count_approved_reports(unpaid_only: bool = False) -> int:
    """Сколько принятых отчётов (unpaid_only=True — среди них ещё не оплаченных)."""
    conn = await get_db()
    cur = await conn.execute(
        "SELECT COUNT(*) AS n FROM reports WHERE status = 'approved' "
        + ("AND paid = 0" if unpaid_only else ""))
    row = await cur.fetchone()
    return row['n'] if row else 0


async def get_user_reports(user_id: int):
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT * FROM reports WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,)
    )
    return await cursor.fetchall()


async def count_reports_all() -> int:
    """Сколько отчётов сдано за всё время (счётчик архива Здания МВД)."""
    conn = await get_db()
    cur = await conn.execute("SELECT COUNT(*) AS n FROM reports")
    row = await cur.fetchone()
    return row['n'] if row else 0


async def get_reports_page(offset: int, limit: int) -> list:
    """Страница архива отчётов (Здание МВД): новые сверху, с автором.

    Как в get_pending_reports: второй ключ ORDER BY (r.id) обязателен —
    у отчётов в одну секунду created_at совпадает, и порядок «плавает».
    """
    conn = await get_db()
    cursor = await conn.execute(
        """SELECT r.*, u.first_name, u.username, u.callsign FROM reports r
           JOIN users u ON r.user_id = u.user_id
           ORDER BY r.created_at DESC, r.id DESC LIMIT ? OFFSET ?""",
        (limit, offset)
    )
    return await cursor.fetchall()


async def get_report_with_user(report_id: int):
    """Один отчёт с данными автора — карточка архива Здания МВД."""
    conn = await get_db()
    cursor = await conn.execute(
        """SELECT r.*, u.first_name, u.username, u.callsign FROM reports r
           JOIN users u ON r.user_id = u.user_id WHERE r.id = ?""",
        (report_id,)
    )
    return await cursor.fetchone()


async def get_report_neighbors(report_id: int):
    """Соседи отчёта в порядке архива (новые сверху): (prev_id, next_id).

    prev — более новый отчёт (выше в списке), next — более старый (ниже).
    Порядок тот же, что у get_reports_page (created_at DESC, id DESC), поэтому
    сравнение идёт по паре (created_at, id) — иначе отчёты одной секунды «плывут».
    """
    conn = await get_db()
    cur_prev = await conn.execute(
        """SELECT id FROM reports
           WHERE (created_at, id) > (SELECT created_at, id FROM reports WHERE id = ?)
           ORDER BY created_at ASC, id ASC LIMIT 1""",
        (report_id,)
    )
    prev_row = await cur_prev.fetchone()
    cur_next = await conn.execute(
        """SELECT id FROM reports
           WHERE (created_at, id) < (SELECT created_at, id FROM reports WHERE id = ?)
           ORDER BY created_at DESC, id DESC LIMIT 1""",
        (report_id,)
    )
    next_row = await cur_next.fetchone()
    return (prev_row['id'] if prev_row else None,
            next_row['id'] if next_row else None)



async def recompute_region_stats():
    """Пересчитывает статистику по регионам из одобренных отчётов.

    Раскладка строится по ПОСЛЕДНЕМУ одобренному отчёту каждого пилота: его регион и
    его поле «всего» (сколько очков у него накоплено). Поэтому показания пилотов
    складываются в сумму по региону, а переезд пилота сразу переносит и его силы, и
    его самого: старый регион теряет и войска, и пилота, новый — получает.

      • СИЛЫ (troops_total)  — сумма «всего» пилотов региона. Это остаток, а не поток
                                 за сутки, поэтому возраст отчёта не важен: накопленное
                                 не испаряется само, и силы не обнуляются, когда отчёт
                                 старше суток. Окна 24 часа тут НЕТ.
      • ПИЛОТЫ (pilots_count) — сколько пилотов сейчас стоят в регионе. Раньше
                                 считалось за окно 72 часа, из-за чего переехавший
                                 пилот учитывался в старом и новом регионах сразу, и
                                 сумма пилотов по регионам превышала число людей.
                                 Окна 72 часов тут тоже НЕТ.
    """
    conn = await get_db()
    await conn.execute("DELETE FROM region_stats")

    cur = await conn.execute("""
        SELECT region,
               COALESCE(SUM(stock), 0) AS troops,
               COUNT(*) AS pilots
        FROM (
            SELECT r.region, COALESCE(r.total_troops, 0) AS stock,
                   ROW_NUMBER() OVER (
                       PARTITION BY r.user_id
                       ORDER BY r.created_at DESC, r.id DESC
                   ) AS rn
            FROM reports r
            WHERE r.status = 'approved'
              AND r.region IS NOT NULL AND r.region != ''
        )
        WHERE rn = 1
        GROUP BY region
    """)
    regions = {}
    for row in await cur.fetchall():
        regions[row['region']] = (row['troops'], row['pilots'])

    for region, (troops, pilots) in regions.items():
        await conn.execute(
            "INSERT INTO region_stats (region, troops_total, pilots_count, computed_at) "
            "VALUES (?, ?, ?, datetime('now'))",
            (region, troops, pilots)
        )
    await conn.commit()
    return len(regions)


async def get_region_stats():
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT * FROM region_stats ORDER BY region"
    )
    return await cursor.fetchall()


async def get_users_for_rank_promotion():
    """Игроки, чьи войска достаточны для звания выше «Старший Лейтенант»,
    но звание ещё не присвоено через админку (список-подсказка для админа)."""
    from config import RANKS, AUTO_RANK_NAMES
    auto_cap = next((req for name, req in RANKS if name == AUTO_RANK_NAMES[-1]), 0)
    result = []
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT user_id, first_name, username, troops, promoted_rank FROM users WHERE troops >= ?",
        (auto_cap,)
    )
    for row in await cursor.fetchall():
        if row['promoted_rank']:
            continue
        next_rank = None
        for rank_name, required in RANKS:
            if rank_name in AUTO_RANK_NAMES:
                continue
            if row['troops'] >= required:
                next_rank = rank_name
            else:
                break
        if next_rank:
            result.append({
                "user_id": row['user_id'],
                "first_name": row['first_name'],
                "username": row['username'],
                "troops": row['troops'],
                "next_rank": next_rank,
            })
    return result


async def get_pilot_base_damage(user_id: int) -> tuple:
    """Базовый урон пилота в бою: (минимум, максимум) по его званию.

    Считается по званию (войска + админ-назначение), а не по выданным статусам:
    у Хранителя (sort_order 100) user_has_status_tag считает «есть» любой статус,
    поэтому по статусам он получил бы асий урон независимо от звания.

    Логика: берётся самый высокий статус из шкалы RANK_DAMAGE_TIERS, который
    положен званию не выше текущего. Турист (sort_order -10, ещё без звания)
    может совсем не нанести урона. Если звание неизвестно — PILOT_NO_WEAPON_DMG.
    """
    from config import (PILOT_NO_WEAPON_DMG, RANK_DAMAGE_TIERS, RANKS,
                        RANK_STATUS_TAGS)

    # Порядок тегов — от сильного к слабому (ace → … → recruit).
    tag_to_req = {}
    for rname, req in RANKS:
        tag = RANK_STATUS_TAGS.get(rname)
        if tag:
            tag_to_req[tag] = max(tag_to_req.get(tag, 0), req)
    tag_to_req["recruit"] = max(tag_to_req.get("recruit", 0),
                                RANKS[0][1])

    user = await get_user(user_id)
    if not user:
        return tuple(PILOT_NO_WEAPON_DMG)
    rank = get_effective_rank(user['troops'] or 0, user['promoted_rank'])
    rank_req = RANKS[0][1]
    for rname, req in RANKS:
        if rname == rank:
            rank_req = req
            break

    if await user_is_tourist(user_id):
        return tuple(RANK_DAMAGE_TIERS["tourist"])

    for tag, dmg in RANK_DAMAGE_TIERS.items():
        if tag == "tourist":
            continue
        req = tag_to_req.get(tag)
        if req is not None and req <= rank_req:
            return tuple(dmg)
    return tuple(PILOT_NO_WEAPON_DMG)


async def get_pilot_crit_chance(user_id: int) -> float:
    """Базовый шанс крита пилота по званию, в %.

    Считается ровно по той же логике и по той же шкале, что
    get_pilot_base_damage, только берёт RANK_CRIT_CHANCE. Это сделано
    специально одной функцией, а не «крил = урон / константа», чтобы
    пороги звания всегда совпадали: игрок, которому уже положен асий урон,
    автоматически получает и асий крит, а не что-то промежуточное.
    """
    from config import (PILOT_NO_WEAPON_DMG, RANKS, RANK_CRIT_CHANCE,
                        RANK_STATUS_TAGS)

    tag_to_req = {}
    for rname, req in RANKS:
        tag = RANK_STATUS_TAGS.get(rname)
        if tag:
            tag_to_req[tag] = max(tag_to_req.get(tag, 0), req)
    tag_to_req["recruit"] = max(tag_to_req.get("recruit", 0), RANKS[0][1])

    user = await get_user(user_id)
    if not user:
        return float(RANK_CRIT_CHANCE.get("recruit", 0.0))
    rank = get_effective_rank(user['troops'] or 0, user['promoted_rank'])
    rank_req = RANKS[0][1]
    for rname, req in RANKS:
        if rname == rank:
            rank_req = req
            break

    if await user_is_tourist(user_id):
        return float(RANK_CRIT_CHANCE.get("tourist", 0.0))

    for tag, chance in RANK_CRIT_CHANCE.items():
        if tag == "tourist":
            continue
        req = tag_to_req.get(tag)
        if req is not None and req <= rank_req:
            return float(chance)
    return 0.0


async def grant_status_for_rank(user_id: int, rank_name: str, granted_by: int = 0):
    """Выдать игроку статус, закреплённый за званием, если его ещё нет.

    Впервые выданный статус становится выбранным (активным), чтобы статус
    «появился» вместе со званием. Возвращает статус или None.
    """
    from config import RANK_STATUS_TAGS
    tag = RANK_STATUS_TAGS.get(rank_name)
    if not tag:
        return None
    if not await get_user(user_id):
        return None
    status = await get_status_by_tag(tag)
    if not status:
        return None
    if await user_has_status_tag(user_id, tag):
        return None
    await grant_status(user_id, status['id'], granted_by)
    await set_selected_status(user_id, status['id'])
    return status


async def grant_all_rank_statuses(user_id: int, rank_name: str, granted_by: int = 0) -> int:
    """Выдать статусы за текущее звание и все пройденные ступени (кумулятивно).

    Статус за звание закреплён только за частью шкалы (RANK_STATUS_TAGS); без
    кумулятивности игрок, перешагнувший закреплённую ступень (например Ефрейтор →
    «Пилот 2 класса») и остановившийся перед следующей закреплённой (Ст. Сержант),
    навсегда терял бы статус. Здесь выдаётся всё, что положено за текущее звание
    и ниже по шкале. Возвращает число впервые выданных статусов.
    """
    from config import RANKS, RANK_STATUS_TAGS
    rank_req = None
    for rname, req in RANKS:
        if rname == rank_name:
            rank_req = req
            break
    if rank_req is None:
        return 0
    granted = 0
    for rname, req in RANKS:
        if req > rank_req:
            break
        if RANK_STATUS_TAGS.get(rname):
            if await grant_status_for_rank(user_id, rname, granted_by):
                granted += 1
    return granted


async def ensure_rank_statuses_for_troops(user_id: int):
    """Выдать статус по текущему званию игрока (по войскам или админ-назначению)."""
    user = await get_user(user_id)
    if not user:
        return None
    rank = get_effective_rank(
        user['troops'],
        user['promoted_rank'] if 'promoted_rank' in user.keys() else None
    )
    return await grant_status_for_rank(user_id, rank)


async def backfill_rank_statuses():
    """Разово выдать статусы по текущим званиям всех пилотов (войска и админ-звания).

    Выдача кумулятивная: статусы за текущее звание и все пройденные ступени.
    Возвращает число игроков, которым выдано хотя бы по одному статусу.
    Идемпотентна.
    """
    conn = await get_db()
    cursor = await conn.execute("SELECT user_id, troops, promoted_rank FROM users")
    rows = await cursor.fetchall()
    granted = 0
    for row in rows:
        rank = get_effective_rank(row['troops'], row['promoted_rank'])
        if await grant_all_rank_statuses(row['user_id'], rank) > 0:
            granted += 1
    return granted


async def promote_user_rank(user_id: int, rank_name: str, promoted_by: int):
    """Присвоить звание решением админа (порог войск не проверяется — свободное решение).

    Закреплённый за званием статус выдаётся автоматически.
    """
    conn = await get_db()
    await conn.execute(
        "UPDATE users SET promoted_rank = ? WHERE user_id = ?",
        (rank_name, user_id)
    )
    await conn.commit()
    from utils.permissions import log_action
    await log_action(promoted_by, 'promote_rank', user_id, f"rank={rank_name}")
    await grant_all_rank_statuses(user_id, rank_name, promoted_by)


async def add_building(name: str, description: str, price: int, category: str,
                       production_type: str = None, production_item_id: int = None,
                       production_time_hours: int = 24, requires_resources: int = 0,
                       photo_file_id: str = None):
    conn = await get_db()
    cursor = await conn.execute(
        """INSERT INTO buildings (name, description, photo_file_id, price, category,
           production_type, production_item_id, production_time_hours, requires_resources)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (name, description, photo_file_id, price, category, production_type,
         production_item_id, production_time_hours, requires_resources)
    )
    await conn.commit()
    return cursor.lastrowid


async def get_building(building_id: int):
    conn = await get_db()
    cursor = await conn.execute("SELECT * FROM buildings WHERE id = ?", (building_id,))
    return await cursor.fetchone()


async def get_all_buildings():
    conn = await get_db()
    cursor = await conn.execute("SELECT * FROM buildings")
    return await cursor.fetchall()


async def buy_building(user_id: int, building_id: int) -> tuple:
    building = await get_building(building_id)
    if not building:
        return False, "Здание не найдено"

    user = await get_user(user_id)
    if not user:
        return False, "Пользователь не найден"

    if user['nordmarks'] < building['price']:
        return False, f"Недостаточно средств. Нужно: {building['price']} НМ"

    conn = await get_db()
    existing = await conn.execute(
        "SELECT id FROM user_buildings WHERE user_id = ? AND building_id = ?",
        (user_id, building_id)
    )
    if await existing.fetchone():
        return False, "У тебя уже есть это здание"

    await remove_nordmarks(user_id, building['price'], "building_purchase", f"Покупка здания: {building['name']}")
    await conn.execute(
        "INSERT INTO user_buildings (user_id, building_id) VALUES (?, ?)",
        (user_id, building_id)
    )
    await conn.commit()
    return True, f"Ты купил здание: {building['name']}!"


async def get_user_buildings(user_id: int):
    conn = await get_db()
    cursor = await conn.execute("""
        SELECT b.*, ub.level, ub.purchased_at FROM user_buildings ub
        JOIN buildings b ON ub.building_id = b.id
        WHERE ub.user_id = ?
    """, (user_id,))
    return await cursor.fetchall()


async def get_transactions_history(user_id: int, page: int = 0, per_page: int = 15):
    """История транзакций постранично (от новых к старым).

    Возвращает (rows, has_next): rows — пер_page записей c OFFSET page*per_page,
    has_next — есть ли следующая страница (запрошен лишний ряд).
    """
    conn = await get_db()
    off = max(0, int(page)) * per_page
    cursor = await conn.execute("""
        SELECT * FROM transactions
        WHERE from_user = ? OR to_user = ?
        ORDER BY created_at DESC, id DESC
        LIMIT ? OFFSET ?
    """, (user_id, user_id, per_page + 1, off))
    rows = await cursor.fetchall()
    has_next = len(rows) > per_page
    return rows[:per_page], has_next


def _citizens_sql(user_id_expr: str = "users.user_id") -> str:
    """Единый SQL-фрагмент «гражданство»: старший статус пилота (sort_order >= 1).

    Одно определение гражданства во всём коде: отсекает «Туриста» (-10) и игроков
    без статусов, но пропускает legacy-«Пилот» (2) и «Хранителя» (100). Используется
    и в списках штаба (get_all_users/get_unassigned_pilots/count_unassigned_pilots),
    и в citizen_user_ids() — списки и проверка в действии не разойдутся.
    """
    return f"""EXISTS (
        SELECT 1 FROM user_statuses us_c
        JOIN statuses s_c ON us_c.status_id = s_c.id
        WHERE us_c.user_id = {user_id_expr}
          AND s_c.sort_order = (
              SELECT MAX(s2.sort_order) FROM user_statuses us2
              JOIN statuses s2 ON us2.status_id = s2.id
              WHERE us2.user_id = us_c.user_id
          )
          AND s_c.sort_order >= 1
    )"""


async def get_all_users(citizens_only: bool = False):
    """Все пользователи; citizens_only=True — только гражданские (sort_order >= 1)."""
    conn = await get_db()
    sql = "SELECT user_id, username, first_name, last_name, wing FROM users"
    if citizens_only:
        sql += " WHERE " + _citizens_sql()
    cursor = await conn.execute(sql)
    return await cursor.fetchall()


async def add_resource_source(user_id: int, item_id: int, building_id: int = None, interval_days: int = 3):
    conn = await get_db()
    await conn.execute(
        "INSERT INTO resource_sources (user_id, item_id, building_id, interval_days) VALUES (?, ?, ?, ?)",
        (user_id, item_id, building_id, interval_days)
    )
    await conn.commit()


async def harvest_resources(user_id: int):
    conn = await get_db()
    cursor = await conn.execute("""
        SELECT rs.*, i.name as item_name FROM resource_sources rs
        JOIN items i ON rs.item_id = i.id
        WHERE rs.user_id = ? AND (
            rs.last_harvest IS NULL
            OR datetime(rs.last_harvest, '+' || rs.interval_days || ' days') <= datetime('now')
        )
    """, (user_id,))
    sources = await cursor.fetchall()

    harvested = []
    for source in sources:
        await add_inventory_item(user_id, source['item_id'], 1)
        await conn.execute(
            "UPDATE resource_sources SET last_harvest = datetime('now') WHERE id = ?",
            (source['id'],)
        )
        harvested.append(source['item_name'])

    await conn.commit()
    return harvested


# ============ СТАТУСЫ ============

async def create_status(name: str, access_tag: str = None, description: str = None,
                        created_by: int = None, sort_order: int = 0):
    conn = await get_db()
    try:
        cursor = await conn.execute(
            "INSERT INTO statuses (name, access_tag, description, created_by, sort_order) VALUES (?, ?, ?, ?, ?)",
            (name, access_tag, description, created_by, sort_order)
        )
        await conn.commit()
        return True, cursor.lastrowid
    except Exception:
        return False, "Статус с таким названием уже существует"


async def ensure_base_statuses():
    """Создаёт базовые статусы иерархии, если их нет.

    Особые: Турист (гость, -10), Хранитель (доверенное лицо командования, 100).
    Карьера пилота: Рекрут (1) → Пилот 2 класса (2) → Пилот 1 класса (3) →
    Ветеран (5) → Мастер-пилот (6) → Ас (9).
    sort_order выставляются принудительно (синхронизирует старые БД).
    """
    base = [
        ("Турист", "tourist", "Гость Нордхайма. Права ограничены.", -10),
        ("Рекрут", "recruit", "Кандидат в пилоты. Живёт в общем кубрике. "
                              "Сдаёт отчёты, покупает, проходит обучение.", 1),
        ("Пилот 2 класса", "pilot2", "Базовый статус пилота ВВС Нордхайма.", 2),
        ("Пилот 1 класса", "pilot1", "Пилот, допущенный к задачам повышенной сложности.", 3),
        ("Ветеран", "veteran", "Ветеран боевых действий.", 5),
        ("Мастер-пилот", "master_pilot", "Мастер лётного дела и подземелий.", 6),
        ("Ас", "ace", "Ас ВВС Нордхайма.", 9),
        ("Хранитель", "keeper", "Доверенное лицо командования. Полный доступ.", 100),
        # Легионер (v0.21.0) — НЕ ступень карьеры, а отдельная роль: сортировка
        # в иерархии его НЕ поднимает, потому что настоящий кеп живёт во флаге
        # users.legioner (см. effective_access_top). sort_order = 5 (как у
        # Ветерана) нужен лишь затем, чтобы витрина и MAX(sort_order) вели себя
        # разумно, пока флаг выключен. В canonical dict его нет намеренно:
        # принудительная канонизация не должна была бы его перетирать.
        ("🦅 Легионер", "legioner", "Пилот с гражданством чужого государства. "
                                    "Обычная служба, но доступы не выше Ветерана "
                                    "и права голоса нет.", 5),
    ]
    conn = await get_db()
    for name, tag, desc, level in base:
        cursor = await conn.execute("SELECT id FROM statuses WHERE access_tag = ?", (tag,))
        if await cursor.fetchone():
            continue
        await create_status(name, tag, desc, sort_order=level)
        await conn.commit()

    # Принудительная канонизация уровней базовой иерархии (идиот-безопасно).
    canonical = {"tourist": -10, "recruit": 1, "pilot2": 2, "pilot1": 3,
                 "veteran": 5, "master_pilot": 6, "ace": 9, "keeper": 100}
    for tag, level in canonical.items():
        await conn.execute(
            "UPDATE statuses SET sort_order = ? WHERE access_tag = ?", (level, tag))
    await conn.commit()


async def ensure_base_status(user_id: int):
    """Базовый статус «Турист» для каждого нового игрока.

    Гражданство «Пилот» выдаёт суперадмин вручную после проверки.
    """
    conn = await get_db()
    cursor = await conn.execute("SELECT id FROM statuses WHERE access_tag = 'tourist'")
    row = await cursor.fetchone()
    if row:
        status_id = row['id']
    else:
        created, status_id = await create_status(
            "Турист", "tourist", "Гость Нордхайма. Права ограничены.",
            sort_order=-10)
        if not created:
            cursor = await conn.execute("SELECT id FROM statuses WHERE access_tag = 'tourist'")
            status_id = (await cursor.fetchone())['id']

    try:
        await conn.execute(
            "INSERT INTO user_statuses (user_id, status_id) VALUES (?, ?)",
            (user_id, status_id)
        )
        await conn.commit()
    except Exception:
        pass

    if not await get_selected_status(user_id):
        await set_selected_status(user_id, status_id)


async def delete_status(status_id: int):
    conn = await get_db()
    await conn.execute("DELETE FROM user_statuses WHERE status_id = ?", (status_id,))
    await conn.execute("DELETE FROM statuses WHERE id = ?", (status_id,))
    await conn.commit()


async def get_all_statuses():
    conn = await get_db()
    cursor = await conn.execute("SELECT * FROM statuses ORDER BY id")
    return await cursor.fetchall()


async def get_status(status_id: int):
    conn = await get_db()
    cursor = await conn.execute("SELECT * FROM statuses WHERE id = ?", (status_id,))
    return await cursor.fetchone()


async def get_status_by_tag(tag: str):
    if not tag:
        return None
    conn = await get_db()
    cursor = await conn.execute("SELECT * FROM statuses WHERE access_tag = ?", (tag,))
    return await cursor.fetchone()


async def grant_status(user_id: int, status_id: int, granted_by: int = None):
    conn = await get_db()
    try:
        await conn.execute(
            "INSERT INTO user_statuses (user_id, status_id, granted_by) VALUES (?, ?, ?)",
            (user_id, status_id, granted_by)
        )
        await conn.commit()
        return True, "Статус выдан"
    except Exception as e:
        error = str(e).lower()
        if "foreign key" in error:
            return False, "Игрок не найден — выдавать статус можно только зарегистрированным участникам (нужно /start)"
        return False, "У игрока уже есть этот статус"


async def revoke_status(user_id: int, status_id: int):
    conn = await get_db()
    await conn.execute(
        "DELETE FROM user_statuses WHERE user_id = ? AND status_id = ?",
        (user_id, status_id)
    )
    await conn.commit()


async def get_user_statuses(user_id: int):
    """Все статусы игрока + флаг выбранного."""
    conn = await get_db()
    cursor = await conn.execute("""
        SELECT s.*, us.is_selected
        FROM user_statuses us
        JOIN statuses s ON us.status_id = s.id
        WHERE us.user_id = ?
        ORDER BY s.id
    """, (user_id,))
    return await cursor.fetchall()


async def get_selected_status(user_id: int):
    conn = await get_db()
    cursor = await conn.execute("""
        SELECT s.* FROM user_statuses us
        JOIN statuses s ON us.status_id = s.id
        WHERE us.user_id = ? AND us.is_selected = 1
        LIMIT 1
    """, (user_id,))
    return await cursor.fetchone()


async def set_selected_status(user_id: int, status_id: int):
    conn = await get_db()
    await conn.execute("UPDATE user_statuses SET is_selected = 0 WHERE user_id = ?", (user_id,))
    await conn.execute(
        "UPDATE user_statuses SET is_selected = 1 WHERE user_id = ? AND status_id = ?",
        (user_id, status_id)
    )
    await conn.commit()
    return True


# Потолок доступа для легионера: «не выше Ветерана». Взят из config, а не
# зашит числом, чтобы каноническая иерархия осталась единственным источником
# истины (veteran = 5).
LEGIONER_ACCESS_TAG = "legioner"


def _legioner_access_sort_order() -> int:
    """sort_order, до которого ограничены доступы легионера."""
    from config import LEGIONER_ACCESS_CAP_ORDER

    return LEGIONER_ACCESS_CAP_ORDER


async def is_legioner(user_id: int) -> bool:
    """Помечен ли игрок как легионер (по флагу, а не по sort_order статуса)."""
    conn = await get_db()
    row = await (await conn.execute(
        "SELECT legioner FROM users WHERE user_id = ?", (user_id,))).fetchone()
    return bool(row and row['legioner'])


async def set_legioner(user_id: int, value: bool) -> bool:
    """Поставить/снять флаг легионера. True — включить, False — снять.

    Кепит права доступа и голосование. Строка статуса «🦅 Легионер» в
    user_statuses выдаётся отдельно (вариант А: кнопка в админ-карточке
    выдаёт и статус, и флаг), потому что именно статус игрок выбирает себе
    сам в профиле как отображаемый.
    """
    conn = await get_db()
    cur = await conn.execute(
        "UPDATE users SET legioner = ? WHERE user_id = ?",
        (1 if value else 0, user_id))
    await conn.commit()
    return cur.rowcount > 0


async def effective_access_top(user_id: int):
    """Верхняя ступень доступа игрока С УЧЁТОМ кепа легионера.

    Единая точка правды для всех гейтов: витрины магазина, покупки, локаций,
    КВП, профиля, жилья и НИИ. Легионеру доступы не выше Ветерана, поэтому
    возвращается константа, а не его реальный MAX(sort_order).

    None — у игрока вообще нет статусов.
    """
    conn = await get_db()
    row = await (await conn.execute("SELECT legioner FROM users WHERE user_id = ?",
                                    (user_id,))).fetchone()
    if row and row['legioner']:
        return _legioner_access_sort_order()
    row = await (await conn.execute("""
        SELECT MAX(s.sort_order) as top FROM user_statuses us
        JOIN statuses s ON us.status_id = s.id
        WHERE us.user_id = ?
    """, (user_id,))).fetchone()
    return row['top'] if row else None


# Доступ по рангу: открыт, если у игрока есть статус не слабее требуемого (sort_order >=)
async def user_has_status_tag(user_id: int, tag: str) -> bool:
    if not tag:
        return True
    conn = await get_db()
    # уровень (sort_order) требуемого тега
    cursor = await conn.execute(
        "SELECT sort_order FROM statuses WHERE access_tag = ?", (tag,))
    req = await cursor.fetchone()
    if not req:
        return False
    # самый сильный статус игрока, с кепом легионера
    top = await effective_access_top(user_id)
    if top is None:
        return False
    return top >= req['sort_order']


async def user_status_visibility_top(user_id: int):
    """Верхняя граница sort_order для видимости предметов магазина.

    Для мотивации и «неожиданности» новинок игрок видит товары своего статуса
    и одной следующей ступени иерархии (требуется статус не далее следующего),
    а предметы на две ступени выше и дальше — скрываются.

    Считается от effective_access_top(), поэтому легионер видит ровно витрину
    Ветерана: кеп ставится ДО расчёта «+1 ступень», иначе он сдвинул бы границу.

    Возвращает sort_order этого статуса-«витрины»; None — если у игрока нет
    статусов (видны только товары без требования).
    """
    top = await effective_access_top(user_id)
    if top is None:
        return None
    cursor = await get_db()
    cursor = await cursor.execute(
        "SELECT MIN(sort_order) AS nxt FROM statuses WHERE sort_order > ?", (top,))
    nxt = (await cursor.fetchone())['nxt']
    if nxt is None:
        return top  # у игрока максимальный статус — видна вся витрина
    return nxt


async def user_is_tourist(user_id: int) -> bool:
    """Турист ли (гость, не получивший пилотскую карьеру).

    Учитывает каноническую иерархию: Турист — -10, Рекрут — 1.
    Рекрут и выше — не турист.
    """
    conn = await get_db()
    cursor = await conn.execute("""
        SELECT MAX(s.sort_order) as top FROM user_statuses us
        JOIN statuses s ON us.status_id = s.id
        WHERE us.user_id = ?
    """, (user_id,))
    top = (await cursor.fetchone())['top']
    if top is None:
        return False
    return top < 1


async def create_award(name: str, description: str = None, emoji: str = "🏅",
                       created_by: int = None, **bonuses):
    """Создать награду. Бонусы — kwargs: bonus_attack/defense/dodge/fishing/hp,
    bonus_crit (%, шанс крита), bonus_shop_discount (%, скидка в магазине),
    bonus_report_tax (п.п. налога)."""
    allowed = {"bonus_attack", "bonus_defense", "bonus_dodge", "bonus_fishing",
               "bonus_hp", "bonus_crit", "bonus_shop_discount", "bonus_report_tax",
               "reward_nm", "monthly_nm"}
    clean = {k: max(0, int(v or 0)) for k, v in bonuses.items() if k in allowed}
    cols = ["name", "description", "emoji", "created_by"] + list(clean)
    conn = await get_db()
    try:
        cursor = await conn.execute(
            f"INSERT INTO awards ({', '.join(cols)}) "
            f"VALUES ({', '.join('?' * len(cols))})",
            (name, description, emoji, created_by, *clean.values())
        )
        await conn.commit()
        return True, cursor.lastrowid
    except Exception:
        return False, "Награда с таким названием уже существует"


async def get_all_awards(include_achievements: bool = True) -> list:
    """Все награды. include_achievements=False — без строк-уровней достижений.

    Строки ачивок (awards с заполненным achievement_key) в обычных админ-списках
    наград лишние: их десятки, они раздувают вывод и путают с медалями.
    """
    conn = await get_db()
    if include_achievements:
        cursor = await conn.execute("SELECT * FROM awards ORDER BY id")
    else:
        cursor = await conn.execute(
            "SELECT * FROM awards WHERE achievement_key IS NULL ORDER BY id")
    return await cursor.fetchall()


async def get_achievement_awards() -> list:
    """Строки-уровни достижений (awards с achievement_key), по ачивке и уровню."""
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT * FROM awards WHERE achievement_key IS NOT NULL "
        "ORDER BY achievement_key, achievement_level")
    return await cursor.fetchall()


async def get_award(award_id: int):
    conn = await get_db()
    cursor = await conn.execute("SELECT * FROM awards WHERE id = ?", (award_id,))
    return await cursor.fetchone()


async def delete_award(award_id: int):
    conn = await get_db()
    await conn.execute("DELETE FROM user_awards WHERE award_id = ?", (award_id,))
    await conn.execute("DELETE FROM awards WHERE id = ?", (award_id,))
    await conn.commit()


async def update_award(award_id: int, **fields) -> bool:
    """Обновление награды: описание, картинка, процентные бонусы. None = очистить."""
    allowed = {"description", "image", "bonus_attack", "bonus_defense",
               "bonus_dodge", "bonus_fishing", "bonus_hp", "bonus_crit",
               "bonus_shop_discount", "bonus_report_tax",
               "reward_nm", "monthly_nm"}
    updates = {k: v for k, v in fields.items() if k in allowed}
    if not updates:
        return False
    conn = await get_db()
    sets = ", ".join(f"{k} = ?" for k in updates)
    await conn.execute(
        f"UPDATE awards SET {sets} WHERE id = ?",
        (*updates.values(), award_id)
    )
    await conn.commit()
    return True


async def get_award_bonus(user_id: int) -> dict:
    """Суммарные бонусы всех наград игрока (в %; hp — в единицах HP).

    shop_discount — суммарная скидка в магазине в % (потолок AWARD_MAX_SHOP_DISCOUNT),
    report_tax — суммарное снижение налога с отчёта в процентных пунктах.
    """
    conn = await get_db()
    cursor = await conn.execute("""
        SELECT COALESCE(SUM(a.bonus_attack), 0) AS attack,
               COALESCE(SUM(a.bonus_defense), 0) AS defense,
               COALESCE(SUM(a.bonus_dodge), 0) AS dodge,
               COALESCE(SUM(a.bonus_fishing), 0) AS fishing,
               COALESCE(SUM(a.bonus_hp), 0) AS hp,
               COALESCE(SUM(a.bonus_shop_discount), 0) AS shop_discount,
               COALESCE(SUM(a.bonus_report_tax), 0) AS report_tax,
               COALESCE(SUM(a.bonus_crit), 0) AS crit
        FROM user_awards ua
        JOIN awards a ON ua.award_id = a.id
        WHERE ua.user_id = ?
    """, (user_id,))
    row = await cursor.fetchone()
    if not row:
        return {"attack": 0, "defense": 0, "dodge": 0, "fishing": 0, "hp": 0,
                "shop_discount": 0, "report_tax": 0, "crit": 0}
    return dict(row)


async def shop_price_for(user_id: int, price: int, category: str = None) -> int:
    """Цена товара для конкретного пилота с учётом скидок от медалей.

    ЕДИНСТВЕННОЕ место, где считается итоговая цена: и карточка товара, и
    списание НМ обязаны звать его, иначе покажут одну сумму, а снимут другую.
    Скидка медалей — в процентах, потолок AWARD_MAX_SHOP_DISCOUNT. Округление
    вниз, но не ниже 1 НМ: иначе копеечный товар становится бесплатным.

    category — категория товара: для «library_card» дополнительно применяется
    скидка достижения «Стена» (ticket_pct, доступна на 4-м уровне) поверх
    медальной, без общего потолка.

    Поверх всего применяется скидка от состояний (например, благословение
    Белого Волка Севера −3%), у неё отдельного потолка нет.
    """
    from config import AWARD_MAX_SHOP_DISCOUNT
    from utils.states import get_shop_discount_pct
    price = int(price or 0)
    if price <= 0:
        return max(0, price)
    # Скидка от состояний (благословение Белого Волка Севера) применяется поверх.

    def _with_state(value: int) -> int:
        if state_pct > 0:
            return max(1, value * (100 - state_pct) // 100)
        return value

    state_pct = await get_shop_discount_pct(user_id) if user_id else 0
    discount = (await get_award_bonus(user_id))['shop_discount']
    if category == "library_card":
        ticket = await get_achievement_bonus(user_id, "writer", "ticket_pct")
        if ticket > 0:
            discount += ticket
            # Медальную часть ограничивает общий потолок, часть от достижения — нет.
            medal_part = min(int(discount - ticket), AWARD_MAX_SHOP_DISCOUNT)
            price = max(1, price * (100 - medal_part) // 100)
            return _with_state(max(1, price * (100 - int(ticket)) // 100))
    if discount <= 0:
        return _with_state(price)
    discount = min(int(discount), AWARD_MAX_SHOP_DISCOUNT)
    return _with_state(max(1, price * (100 - discount) // 100))


async def report_tax_percent_for(user_id: int) -> int:
    """Ставка налога с отчёта для пилота: общая минус снижения от медалей.

    Снижение задано в процентных пунктах (медаль -5 при ставке 15% → 10%).
    Ниже AWARD_MIN_REPORT_TAX не опускаем — отчёт не должен стать бесплатным.
    """
    from config import AWARD_MIN_REPORT_TAX
    base = await get_report_tax_percent()
    reduction = (await get_award_bonus(user_id))['report_tax']
    if reduction <= 0:
        return base
    return max(AWARD_MIN_REPORT_TAX, base - int(reduction))


async def set_callsign(user_id: int, callsign: str):
    """Устанавливает игровой позывной пилота (показывается в карточке)."""
    conn = await get_db()
    await conn.execute("UPDATE users SET callsign = ? WHERE user_id = ?",
                       (callsign or None, user_id))
    await conn.commit()


async def set_callsign_free_used(user_id: int, used: int = 1):
    """Отмечает, что бесплатная смена/установка позывного использована (1 раз)."""
    conn = await get_db()
    await conn.execute("UPDATE users SET callsign_free_used = ? WHERE user_id = ?",
                       (1 if used else 0, user_id))
    await conn.commit()


async def get_callsign_free_used(user_id: int) -> bool:
    """Проверяет, использовалась ли бесплатная установка позывного."""
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT callsign_free_used FROM users WHERE user_id = ?",
        (user_id,))
    row = await cursor.fetchone()
    if not row:
        return False
    val = row['callsign_free_used'] if isinstance(row, dict) or hasattr(row, 'keys') else (row[0] if row else 0)
    try:
        return int(val or 0) == 1
    except (ValueError, TypeError):
        return False


async def set_wing(user_id: int, wing: str = None):
    """Устанавливает авиакрыло пилота ('1'/'2'/'3'); None — перевести в «Резерв».

    Пилот без формирования (или при снятии крыла) попадает в крыло 'reserve'
    (🪖 Резерв): командиры набирают себе пилотов именно оттуда.
    """
    conn = await get_db()
    await conn.execute("UPDATE users SET wing = ? WHERE user_id = ?",
                       (wing if wing else 'reserve', user_id))
    await conn.commit()


# ============ ФОРМИРОВАНИЯ ВВС (редактор в штабе) ============

async def load_wings_cache():
    """Перечитать формирования из БД в кэш utils.wings (метки штаба/профиля).

    Айос.также при старте (после init_db) и после каждого изменения.
    """
    from utils.wings import set_wings
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT key, num, abbr, name, callsign, emoji, sort_order "
        "FROM wings ORDER BY sort_order, key")
    set_wings(await cursor.fetchall())


async def get_wing_rows() -> list:
    """Все формирования (ключ + поля) в порядке сортировки."""
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT key, num, abbr, name, callsign, emoji, sort_order "
        "FROM wings ORDER BY sort_order, key")
    return await cursor.fetchall()


async def get_wing_row(key: str):
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT key, num, abbr, name, callsign, emoji, sort_order "
        "FROM wings WHERE key = ?", (key,))
    return await cursor.fetchone()


async def create_wing(num: str, abbr: str, name: str, callsign: str,
                      emoji: str, sort_order: int = None) -> tuple:
    """Создать новое формирование ВВС из штаба.

    Формат нового формирования по ТЗ: сначала ЧИСЛО, потом две ЗАГЛАВНЫЕ
    буквы — сокращение от полного названия (например «5 ИШ» → «Истребители
    Шторма»), затем позывной. Возвращает (ok, текст).
    """
    num = str(num or "").strip()
    abbr = str(abbr or "").strip().upper()
    name = str(name or "").strip()
    callsign = str(callsign or "").strip()
    emoji = str(emoji or "").strip()
    import re
    if not re.fullmatch(r"\d{1,3}", num):
        return False, "❌ Число формирования — это номер (например 5), а не текст."
    if not re.fullmatch(r"[А-ЯЁ]{2}", abbr):
        return False, ("❌ Аббревиатура — ровно ДВЕ ЗАГЛАВНЫЕ буквы, сокращение "
                       "полного названия (например ИШ → «Истребители Шторма»).")
    if not name:
        return False, "❌ Полное название формирования не может быть пустым."
    key = f"{int(num)} {abbr}"
    conn = await get_db()
    try:
        await conn.execute(
            "INSERT INTO wings (key, num, abbr, name, callsign, emoji, sort_order) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (key, str(int(num)), abbr, name, callsign, emoji, sort_order or 999))
        await conn.commit()
    except Exception:
        return False, "❌ Такое формирование уже есть (тот же номер и аббревиатура)."
    await load_wings_cache()
    return True, f"✅ Создано формирование: {emoji or ''} {key} «{callsign or name}»".strip()


async def update_wing(key: str, name: str = None, callsign: str = None,
                      emoji: str = None) -> bool:
    """Переименовать формирование / сменить позывной / эмодзи (но не номер и аббревиатуру)."""
    conn = await get_db()
    sets, params = [], []
    if name is not None:
        sets.append("name = ?")
        params.append(str(name or "").strip())
    if callsign is not None:
        sets.append("callsign = ?")
        params.append(str(callsign or "").strip())
    if emoji is not None:
        sets.append("emoji = ?")
        params.append(str(emoji or "").strip())
    if not sets:
        return False
    params.append(key)
    await conn.execute(f"UPDATE wings SET {', '.join(sets)} WHERE key = ?", params)
    await conn.commit()
    await load_wings_cache()
    return True


async def delete_wing(key: str) -> tuple:
    """Удалить формирование. Занятое (состав/командир/заместитель) — нельзя."""
    conn = await get_db()
    members = await get_wing_members(key)
    if members:
        return False, "❌ В формировании есть пилоты — сначала переведи их."
    cmd = await (await conn.execute(
        "SELECT user_id FROM wing_commanders WHERE wing = ?", (key,))).fetchone()
    if cmd:
        return False, "❌ Сначала сними командира формирования."
    dep = await (await conn.execute(
        "SELECT user_id FROM wing_deputies WHERE wing = ?", (key,))).fetchone()
    if dep:
        return False, "❌ Сначала сними заместителя формирования."
    row = await get_wing_row(key)
    if not row:
        return False, "❌ Формирование не найдено."
    await conn.execute("DELETE FROM wings WHERE key = ?", (key,))
    await conn.commit()
    await load_wings_cache()
    return True, f"✅ Формирование «{row['num']} {row['abbr']}» удалено."


async def get_wing_members(wing: str = None) -> list:
    """Telegram-id пилотов конкретного крыла (wing='1'/'2'/'3').

    Если крыло не указано — все пилоты, состоящие в любом авиакрыле.
    """
    conn = await get_db()
    if wing:
        cursor = await conn.execute("SELECT user_id FROM users WHERE wing = ?", (wing,))
    else:
        cursor = await conn.execute(
            "SELECT user_id FROM users WHERE wing IS NOT NULL AND wing != ''"
        )
    return [row['user_id'] for row in await cursor.fetchall()]


async def get_wing_commander(wing: str):
    """Telegram-id командира конкретного крыла (wing='1'/'2'/'3') или None."""
    conn = await get_db()
    cursor = await conn.execute("SELECT user_id FROM wing_commanders WHERE wing = ?", (wing,))
    row = await cursor.fetchone()
    return row['user_id'] if row else None


async def get_wing_commanders() -> dict:
    """Словарь {крыло: telegram-id командира} по всем крыльям."""
    conn = await get_db()
    cursor = await conn.execute("SELECT wing, user_id FROM wing_commanders")
    return {row['wing']: row['user_id'] for row in await cursor.fetchall()}


async def get_wing_commander_by_user(user_id: int):
    """Ключ крыла ('1'/'2'/'3'), которым командует пилот, или None."""
    conn = await get_db()
    cursor = await conn.execute("SELECT wing FROM wing_commanders WHERE user_id = ?", (user_id,))
    row = await cursor.fetchone()
    return row['wing'] if row else None


async def set_wing_commander(wing: str, user_id: int = None):
    """Назначить командира крыла; user_id=None — снять (удалить запись)."""
    conn = await get_db()
    if user_id is None:
        await conn.execute("DELETE FROM wing_commanders WHERE wing = ?", (wing,))
    else:
        await conn.execute(
            "INSERT INTO wing_commanders (wing, user_id) VALUES (?, ?) "
            "ON CONFLICT(wing) DO UPDATE SET user_id = excluded.user_id",
            (wing, user_id)
        )
    await conn.commit()


async def get_wing_deputy(wing: str):
    """Telegram-id заместителя командира крыла или None."""
    conn = await get_db()
    cursor = await conn.execute("SELECT user_id FROM wing_deputies WHERE wing = ?", (wing,))
    row = await cursor.fetchone()
    return row['user_id'] if row else None


async def get_wing_deputies() -> dict:
    """Словарь {крыло: telegram-id заместителя} по всем крыльям."""
    conn = await get_db()
    cursor = await conn.execute("SELECT wing, user_id FROM wing_deputies")
    return {row['wing']: row['user_id'] for row in await cursor.fetchall()}


async def get_wing_deputy_by_user(user_id: int):
    """Ключ крыла ('1'/'2'/'3'), в которой пилот — заместитель, или None."""
    conn = await get_db()
    cursor = await conn.execute("SELECT wing FROM wing_deputies WHERE user_id = ?", (user_id,))
    row = await cursor.fetchone()
    return row['wing'] if row else None


async def set_wing_deputy(wing: str, user_id: int = None):
    """Назначить заместителя командира крыла; user_id=None — снять.

    Пилот не может быть заместителем двух крыльев сразу: прежняя запись снимается.
    """
    conn = await get_db()
    if user_id is None:
        await conn.execute("DELETE FROM wing_deputies WHERE wing = ?", (wing,))
    else:
        await conn.execute("DELETE FROM wing_deputies WHERE user_id = ?", (user_id,))
        await conn.execute(
            "INSERT INTO wing_deputies (wing, user_id) VALUES (?, ?) "
            "ON CONFLICT(wing) DO UPDATE SET user_id = excluded.user_id",
            (wing, user_id)
        )
    await conn.commit()


async def get_wing_staff_wing(user_id: int):
    """Крыло, в котором пилот — командир или заместитель (командир важнее), иначе None."""
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT wing, 'commander' AS role FROM wing_commanders WHERE user_id = ? "
        "UNION ALL "
        "SELECT wing, 'deputy' AS role FROM wing_deputies WHERE user_id = ?",
        (user_id, user_id)
    )
    row = await cursor.fetchone()
    return row['wing'] if row else None


async def get_wing_staff_role(user_id: int) -> str:
    """'commander' / 'deputy' / '' — должность пилота в крыле."""
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT 'commander' AS role FROM wing_commanders WHERE user_id = ? "
        "UNION ALL "
        "SELECT 'deputy' AS role FROM wing_deputies WHERE user_id = ? LIMIT 1",
        (user_id, user_id)
    )
    row = await cursor.fetchone()
    return row['role'] if row else ''


async def count_unassigned_pilots(citizens_only: bool = False) -> int:
    """Сколько пилотов ещё не в составе ни одного крыла — их можно взять в состав."""
    conn = await get_db()
    sql = ("SELECT COUNT(*) AS n FROM users "
           "WHERE (wing IS NULL OR wing = '' OR wing = 'none')")
    if citizens_only:
        sql += " AND " + _citizens_sql()
    cursor = await conn.execute(sql)
    row = await cursor.fetchone()
    return row['n'] if row else 0


async def get_unassigned_pilots(limit: int = None, offset: int = 0,
                                citizens_only: bool = False) -> list:
    """Пилоты в Резерве (wing='reserve') — их командир может принять в крыло.

    Старые NULL/'' трактуем как Резерв тоже (переходный период до миграции).
    """
    conn = await get_db()
    sql = ("SELECT user_id, username, first_name, last_name, wing FROM users "
           "WHERE (wing IS NULL OR wing = '' OR wing = 'none' OR wing = 'reserve')")
    if citizens_only:
        sql += " AND " + _citizens_sql()
    sql += " ORDER BY user_id"
    params = []
    if limit is not None:
        sql += " LIMIT ? OFFSET ?"
        params = [limit, offset]
    cursor = await conn.execute(sql, tuple(params))
    return await cursor.fetchall()


async def get_wing_member_rows(wing: str, limit: int = None, offset: int = 0) -> list:
    """Пилоты крыла (для «убрать из состава» и выбора заместителя).

    Помимо идентификационных полей возвращает и troops (накопленные войска
    пилота) — пригодилось в «Составе формирования».
    """
    conn = await get_db()
    sql = ("SELECT user_id, username, first_name, last_name, wing, troops FROM users "
           "WHERE wing = ? ORDER BY user_id")
    params = [wing]
    if limit is not None:
        sql += " LIMIT ? OFFSET ?"
        params += [limit, offset]
    cursor = await conn.execute(sql, tuple(params))
    return await cursor.fetchall()


async def count_wing_members(wing: str) -> int:
    conn = await get_db()
    cursor = await conn.execute("SELECT COUNT(*) AS n FROM users WHERE wing = ?", (wing,))
    row = await cursor.fetchone()
    return row['n'] if row else 0


async def wing_members_report_farms(wing: str) -> list:
    """Пилоты крыла (строй-строки users) + их фарм за сутки: 'prev_farm' и 'today_farm'.

    Фарм берётся из последнего ПРИНЯТОГО отчёта за конкретные отчётные сутки
    (10:00 МСК → 10:00 МСК) — ровно как считается выплата (report_day_credited_total,
    с v0.22.0 это последний снимок, а не сумма отчётов). Текущие сутки показывают
    только уже одобренное — отчёт, висящий на проверке, в цифру не идёт. Нужно
    командирам крыльев: видят, кто реально фармит, а кто нет, без пересчёта по
    одному пилоту.

    Дополнительно каждый пилот несёт 'region' — регион из его ПОСЛЕДНЕГО принятого
    отчёта (как в recompute_region_stats, старшинство по created_at, затем id) и
    'troops' — накопленный объём войск из users.
    """
    conn = await get_db()
    today = today_report_day()
    prev_day = report_day_value_of(
        (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    )
    day_expr = _report_day('created_at')
    # Снимок, а не сумма: rn = 1 оставляет последний принятый отчёт каждых суток.
    # Раньше здесь стоял SUM(...) GROUP BY user_id, day — командир видел сумму всех
    # отчётов пилота за сутки, то есть цифру, которой никогда не выплачивалось.
    cursor = await conn.execute(f"""
        SELECT user_id, day, farm FROM (
            SELECT user_id, {day_expr} AS day,
                   COALESCE(credited_troops, troops_reported, 0) AS farm,
                   ROW_NUMBER() OVER (
                       PARTITION BY user_id, {day_expr}
                       ORDER BY created_at DESC, id DESC
                   ) AS rn
            FROM reports
            WHERE status = 'approved'
        )
        WHERE rn = 1
          AND day IN (?, ?)
          AND user_id IN (SELECT user_id FROM users WHERE wing = ?)
    """, (prev_day, today, wing))
    farms = {}
    for row in await cursor.fetchall():
        farms.setdefault(row['user_id'], {})[row['day']] = row['farm']

    # Регион: последний принятый отчёт пилота (регион не пуст). Та же раскладка,
    # что в recompute_region_stats: ORDER BY created_at DESC, id DESC, rn = 1.
    cur = await conn.execute("""
        SELECT user_id, region, total_troops FROM (
            SELECT r.user_id, r.region, COALESCE(r.total_troops, 0) AS total_troops,
                   ROW_NUMBER() OVER (
                       PARTITION BY r.user_id
                       ORDER BY r.created_at DESC, r.id DESC
                   ) AS rn
            FROM reports r
            WHERE r.status = 'approved'
              AND r.region IS NOT NULL AND r.region != ''
        )
        WHERE rn = 1
          AND user_id IN (SELECT user_id FROM users WHERE wing = ?)
    """, (wing,))
    regions = {row['user_id']: (row['region'], row['total_troops'] or 0)
               for row in await cur.fetchall()}

    members = await get_wing_member_rows(wing)
    result = []
    for u in members:
        d = dict(u)
        d['prev_farm'] = farms.get(u['user_id'], {}).get(prev_day, 0) or 0
        d['today_farm'] = farms.get(u['user_id'], {}).get(today, 0) or 0
        region_info = regions.get(u['user_id'])
        d['region'] = region_info[0] if region_info else None
        # Сколько сил пилот заявил в регионе («всего» его последнего принятого отчёта) —
        # именно эта цифра складывается в силы региона в recompute_region_stats.
        d['region_troops'] = region_info[1] if region_info else None
        result.append(d)
    return result


async def add_user_role(user_id: int, role: str, granted_by: int = None):
    """Выдать роль пилоту (INSERT OR IGNORE) — например, wing_commander."""
    conn = await get_db()
    await conn.execute(
        "INSERT OR IGNORE INTO user_roles (telegram_id, role, granted_by) VALUES (?, ?, ?)",
        (user_id, role, granted_by)
    )
    await conn.commit()


async def remove_user_role(user_id: int, role: str):
    """Снять роль с пилота.

    Окладным должностям перед удалением начисляется пропорциональный оклад за
    отработанные в текущем месяце дни (см. pay_role_salary_on_revoke).
    """
    payout = await pay_role_salary_on_revoke(user_id, role)
    conn = await get_db()
    await conn.execute("DELETE FROM user_roles WHERE telegram_id = ? AND role = ?",
                       (user_id, role))
    await conn.commit()
    return payout


async def _award_cash_payout(user_id: int, award: dict, amount: int) -> None:
    """Выплата денежной премии награды ИЗ КАЗНЫ.

    Не создаёт НМ из воздуха: казна списывается, игрок получает на счёт, в бан
    пишется транзакция. Если казны не хватает — платим чем есть, остаток копится
    в salary_debt (казна остаётся должна игроку) и будет отдан тем же циклом,
    что и зарплаты (см. pay_salaries / get_salaries_due).
    """
    amount = int(amount or 0)
    if amount <= 0:
        return
    name = award['name'] if award and award.get('name') else 'награда'
    conn = await get_db()
    balance = await get_treasury_balance()
    if balance >= amount:
        paid = amount
        await conn.execute("UPDATE treasury SET balance = balance - ? WHERE id = 1", (paid,))
        await conn.execute(
            "UPDATE users SET nordmarks = nordmarks + ? WHERE user_id = ?", (paid, user_id))
        await conn.execute(
            "INSERT INTO transactions (from_user, to_user, amount, tx_type, description) "
            "VALUES (?, ?, ?, ?, ?)",
            (TREASURY_ID, user_id, paid, "award",
             f"Награда «{name}»: {paid} НМ из казны")
        )
        await conn.commit()
    elif balance > 0:
        paid = balance
        await conn.execute("UPDATE treasury SET balance = 0 WHERE id = 1")
        await conn.execute(
            "UPDATE users SET nordmarks = nordmarks + ? WHERE user_id = ?", (paid, user_id))
        await conn.execute(
            "INSERT INTO transactions (from_user, to_user, amount, tx_type, description) "
            "VALUES (?, ?, ?, ?, ?)",
            (TREASURY_ID, user_id, paid, "award",
             f"Награда «{name}»: {paid} НМ из казны (частично)")
        )
        await conn.commit()
        await add_salary_debt(user_id, amount - paid)
    else:
        await add_salary_debt(user_id, amount)


async def _cash_from_treasury(user_id: int, amount: int, tx_type: str,
                              description: str) -> None:
    """Выплата ИЗ КАЗНЫ с механизмом долга (тот же, что у зарплат).

    Не создаёт НМ из воздуха: казна списывается, игрок получает на счёт, пишется
    транзакция. Если казны не хватает — платим чем есть, остаток копится в
    salary_debt (казна остаётся должна игроку) и догоняется циклом зарплат
    (см. pay_salaries / get_salaries_due). Универсален для окладов, гонораров
    за публикации и премий наград.
    """
    amount = int(amount or 0)
    if amount <= 0:
        return
    conn = await get_db()
    balance = await get_treasury_balance()
    if balance >= amount:
        paid = amount
        await conn.execute("UPDATE treasury SET balance = balance - ? WHERE id = 1", (paid,))
        await conn.execute(
            "UPDATE users SET nordmarks = nordmarks + ? WHERE user_id = ?", (paid, user_id))
        await conn.execute(
            "INSERT INTO transactions (from_user, to_user, amount, tx_type, description) "
            "VALUES (?, ?, ?, ?, ?)",
            (TREASURY_ID, user_id, paid, tx_type, description))
        await conn.commit()
    elif balance > 0:
        paid = balance
        await conn.execute("UPDATE treasury SET balance = 0 WHERE id = 1")
        await conn.execute(
            "UPDATE users SET nordmarks = nordmarks + ? WHERE user_id = ?", (paid, user_id))
        await conn.execute(
            "INSERT INTO transactions (from_user, to_user, amount, tx_type, description) "
            "VALUES (?, ?, ?, ?, ?)",
            (TREASURY_ID, user_id, paid, tx_type, description + " (частично)"))
        await conn.commit()
        await add_salary_debt(user_id, amount - paid)
    else:
        await add_salary_debt(user_id, amount)


async def grant_award(user_id: int, award_id: int, granted_by: int = None,
                      comment: str = None):
    """Выдать награду. Возвращает (ok, текст).

    ВАЖНО: это единственная точка выдачи наград, но оповещение в общий чат здесь
    НЕ отправляется (нет доступа к боту) — после успешной выдачи вызывающий обязан
    вызвать utils.notify.notify_award(bot, user, "эмодзи Название", user_id).

    Денежная премия награды (awards.reward_nm) выплачивается из казны отдельным
    шагом — деньги на счёт игрока НЕ создаются из ничего.
    """
    conn = await get_db()
    try:
        await conn.execute(
            "INSERT INTO user_awards (user_id, award_id, granted_by, comment) VALUES (?, ?, ?, ?)",
            (user_id, award_id, granted_by, comment)
        )
        await conn.commit()
    except Exception as e:
        error = str(e).lower()
        if "foreign key" in error:
            return False, "Игрок не найден — регистрация нужна через /start"
        return False, "Не удалось выдать награду"

    award = await (await conn.execute(
        "SELECT id, name, reward_nm FROM awards WHERE id = ?", (award_id,))).fetchone()
    if award and (award['reward_nm'] or 0) > 0:
        await _award_cash_payout(user_id, award, award['reward_nm'])
        return True, f"Награда выдана (+{award['reward_nm']} НМ из казны)"
    return True, "Награда выдана"


async def revoke_award(user_award_id: int):
    conn = await get_db()
    await conn.execute("DELETE FROM user_awards WHERE id = ?", (user_award_id,))
    await conn.commit()


async def get_user_awards(user_id: int):
    """Награды игрока (с данными награды и датой выдачи)."""
    conn = await get_db()
    cursor = await conn.execute("""
        SELECT ua.id as grant_id, ua.comment, ua.created_at AS granted_at,
               a.id AS award_id, a.name, a.description, a.emoji, a.image,
               a.bonus_attack, a.bonus_defense, a.bonus_dodge, a.bonus_fishing,
               a.bonus_hp, a.bonus_crit, a.bonus_shop_discount, a.bonus_report_tax,
               a.reward_nm, a.monthly_nm
        FROM user_awards ua
        JOIN awards a ON ua.award_id = a.id
        WHERE ua.user_id = ?
        ORDER BY ua.created_at DESC
    """, (user_id,))
    return await cursor.fetchall()


async def get_award_recipients(award_id: int):
    """Кому выдали конкретную награду."""
    conn = await get_db()
    cursor = await conn.execute("""
        SELECT u.user_id, u.username, u.first_name, ua.comment, ua.created_at AS granted_at
        FROM user_awards ua
        JOIN users u ON ua.user_id = u.user_id
        WHERE ua.award_id = ?
        ORDER BY ua.created_at DESC
    """, (award_id,))
    return await cursor.fetchall()


async def pay_award_monthly() -> dict:
    """Ежемесячные наградные выплаты ИЗ КАЗНЫ.

    Деньги не создаются из воздуха: каждая награда с awards.monthly_nm > 0
    платит владельцам раз в календарный месяц (YYYY-MM по Москве), если за этот
    месяц ещё не платили (таблица award_monthly_paid). Нехватка казны уходит
    в salary_debt и догоняется циклом зарплат.

    Возвращает {'paid': [...], 'debt': [...], 'skipped': [...]}.
    """
    month = datetime.now(MOSCOW_TZ).strftime("%Y-%m")
    conn = await get_db()
    cursor = await conn.execute("""
        SELECT ua.user_id, a.id AS award_id, a.name, a.monthly_nm
        FROM user_awards ua
        JOIN awards a ON ua.award_id = a.id
        WHERE a.monthly_nm IS NOT NULL AND a.monthly_nm > 0
          AND NOT EXISTS (
              SELECT 1 FROM award_monthly_paid amp
              WHERE amp.user_id = ua.user_id AND amp.award_id = ua.award_id
                AND amp.month = ?
          )
    """, (month,))
    rows = await cursor.fetchall()

    paid, debt, skipped = [], [], []
    for row in rows:
        award = {"id": row['award_id'], "name": row['name']}
        before_debt = (await (await conn.execute(
            "SELECT salary_debt FROM users WHERE user_id = ?", (row['user_id'],))).fetchone())['salary_debt'] or 0
        await _award_cash_payout(row['user_id'], award, row['monthly_nm'])
        after_debt = (await (await conn.execute(
            "SELECT salary_debt FROM users WHERE user_id = ?", (row['user_id'],))).fetchone())['salary_debt'] or 0
        await conn.execute(
            "INSERT OR IGNORE INTO award_monthly_paid (user_id, award_id, month) "
            "VALUES (?, ?, ?)",
            (row['user_id'], row['award_id'], month))
        if after_debt > before_debt:
            debt.append((row['user_id'], row['award_id'],
                         award['name'], after_debt - before_debt))
        else:
            paid.append((row['user_id'], row['award_id'], award['name'], row['monthly_nm']))
    await conn.commit()
    return {"paid": paid, "debt": debt, "skipped": skipped}


# ============ ЛОКАЦИИ (статусный доступ + блокирующие состояния) ============

async def get_location(location_id: int):
    conn = await get_db()
    cursor = await conn.execute("SELECT * FROM locations WHERE id = ?", (location_id,))
    return await cursor.fetchone()


async def get_location_by_key(key: str):
    conn = await get_db()
    cursor = await conn.execute("SELECT * FROM locations WHERE key = ?", (key,))
    return await cursor.fetchone()


async def get_all_locations():
    conn = await get_db()
    cursor = await conn.execute("SELECT * FROM locations ORDER BY sort_order, id")
    return await cursor.fetchall()


async def create_location(key: str, name: str, description: str = None,
                          access_mode: str = "all", required_status: str = None,
                          blocking_states: list = None):
    conn = await get_db()
    try:
        await conn.execute(
            "INSERT INTO locations (key, name, description, access_mode, required_status, blocking_states) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (key, name, description, access_mode, required_status,
             json.dumps(blocking_states or [], ensure_ascii=False))
        )
        await conn.commit()
        return True, None
    except Exception as e:
        return False, str(e)


async def update_location_access(location_id: int, access_mode: str = None,
                                 required_status: str = None,
                                 blocking_states: list = None):
    conn = await get_db()
    loc = await get_location(location_id)
    if not loc:
        return False
    cur_mode = access_mode if access_mode is not None else loc['access_mode']
    cur_req = required_status if required_status is not None else loc['required_status']
    cur_block = blocking_states if blocking_states is not None else json.loads(loc['blocking_states'] or '[]')
    await conn.execute(
        "UPDATE locations SET access_mode = ?, required_status = ?, blocking_states = ? WHERE id = ?",
        (cur_mode, cur_req, json.dumps(cur_block, ensure_ascii=False), location_id)
    )
    await conn.commit()
    return True


_LOC_UNSET = object()


async def update_location_content(location_id: int, *, name=_LOC_UNSET,
                                  description=_LOC_UNSET, preview_photo=_LOC_UNSET):
    """Обновить название/описание/картинку локации. _LOC_UNSET — поле не трогаем."""
    conn = await get_db()
    loc = await get_location(location_id)
    if not loc:
        return False
    cur_name = name if name is not _LOC_UNSET else loc['name']
    cur_desc = description if description is not _LOC_UNSET else loc['description']
    cur_photo = preview_photo if preview_photo is not _LOC_UNSET else loc['preview_photo']
    await conn.execute(
        "UPDATE locations SET name = ?, description = ?, preview_photo = ? WHERE id = ?",
        (cur_name, cur_desc, cur_photo, location_id)
    )
    await conn.commit()
    return True


LOCATION_PHOTO_KEYS = ("dawn", "day", "sunset", "night")
# Ключи фото подземелья: вход по времени суток + комнаты-препятствия К.В.П.
DUNGEON_PHOTO_KEYS = LOCATION_PHOTO_KEYS + ("water", "rope")


async def update_dungeon_photos(dungeon_id: int, photos: dict):
    """Задать file_id картинок подземелья (ключи DUNGEON_PHOTO_KEYS).

    Один конкретный слот: update_dungeon_photos(id, {'day': file_id}).
    Сброс слота ('—'): update_dungeon_photos(id, {'day': None}).
    """
    conn = await get_db()
    dng = await get_dungeon(dungeon_id)
    if not dng:
        return False
    cur = {}
    for k in DUNGEON_PHOTO_KEYS:
        cur[k] = dng[f"photo_{k}"]
    cur.update({k: v for k, v in photos.items() if k in DUNGEON_PHOTO_KEYS})
    await conn.execute(
        "UPDATE dungeons SET photo_dawn = ?, photo_day = ?, photo_sunset = ?, "
        "photo_night = ?, photo_water = ?, photo_rope = ? WHERE id = ?",
        (cur["dawn"], cur["day"], cur["sunset"], cur["night"], cur["water"], cur["rope"], dungeon_id)
    )
    await conn.commit()
    return True


async def update_location_photos(location_id: int, photos: dict):
    """Задать file_id картинок здания по времени суток (ключи LOCATION_PHOTO_KEYS).

    Один конкретный слот: update_location_photos(id, {'day': file_id}).
    Сброс слота ('—'): update_location_photos(id, {'day': None}).
    """
    conn = await get_db()
    loc = await get_location(location_id)
    if not loc:
        return False
    cur = {}
    for k in LOCATION_PHOTO_KEYS:
        cur[k] = loc[f"photo_{k}"]
    cur.update({k: v for k, v in photos.items() if k in LOCATION_PHOTO_KEYS})
    await conn.execute(
        "UPDATE locations SET photo_dawn = ?, photo_day = ?, photo_sunset = ?, photo_night = ? WHERE id = ?",
        (cur["dawn"], cur["day"], cur["sunset"], cur["night"], location_id)
    )
    await conn.commit()
    return True


# Сезоны картинок локаций (совпадают с SEASON_MONTHS в utils/helpers.py).
LOCATION_SEASONS = ("winter", "spring", "summer", "autumn")


def location_season_photos_raw(loc) -> dict:
    """Сезонные фото локации: {сезон: {время суток: file_id}} из season_photos."""
    try:
        data = json.loads(loc.get("season_photos") or "{}")
        if isinstance(data, dict):
            return {s: (d if isinstance(d, dict) else {}) for s, d in data.items()}
    except (ValueError, TypeError):
        pass
    return {}


async def update_location_season_photo(location_id: int, season: str, tod: str, file_id):
    """Задать (или убрать при None) картинку локации на сезон + время суток.

    Убирает запись, когда в сезоне не остаётся ни одного слота ('—').
    """
    if season not in LOCATION_SEASONS or tod not in LOCATION_PHOTO_KEYS:
        return False
    conn = await get_db()
    loc = await get_location(location_id)
    if not loc:
        return False
    photos = location_season_photos_raw(loc)
    slot = dict(photos.get(season) or {})
    if file_id is None:
        slot.pop(tod, None)
        if slot:
            photos[season] = slot
        else:
            photos.pop(season, None)
    else:
        slot[tod] = file_id
        photos[season] = slot
    await conn.execute(
        "UPDATE locations SET season_photos = ? WHERE id = ?",
        (json.dumps(photos, ensure_ascii=False), location_id)
    )
    await conn.commit()
    return True


async def clear_location_season_photos(location_id: int) -> bool:
    """Сбросить все сезонные картинки локации."""
    conn = await get_db()
    if not await get_location(location_id):
        return False
    await conn.execute("UPDATE locations SET season_photos = NULL WHERE id = ?", (location_id,))
    await conn.commit()
    return True


async def clear_location_season(location_id: int, season: str) -> bool:
    """Сбросить картинки одного сезона локации."""
    if season not in LOCATION_SEASONS:
        return False
    conn = await get_db()
    loc = await get_location(location_id)
    if not loc:
        return False
    photos = location_season_photos_raw(loc)
    if season in photos:
        photos.pop(season, None)
        await conn.execute(
            "UPDATE locations SET season_photos = ? WHERE id = ?",
            (json.dumps(photos, ensure_ascii=False), location_id)
        )
        await conn.commit()
    return True


def location_photo_for_tod(loc, season: str, tod: str):
    """file_id фото локации на момент показа.

    Приоритет: слот «сезон × время суток» (с фолбэком по суткам внутри сезона) →
    обычные слоты photo_<tod> (ввод, без сезона) → None.
    """
    slots = location_season_photos_raw(loc).get(season) or {}
    for key in (tod, "dawn", "day", "sunset", "night"):
        if slots.get(key):
            return slots[key]
    for key in (f"photo_{tod}", "photo_dawn", "photo_day", "photo_sunset", "photo_night"):
        if loc.get(key):
            return loc[key]
    return None


def location_glade_photo(loc):
    """file_id отдельной картинки опушки леса (None → показываем локальный файл).

    Опушка намеренно не наследует фото входа в лес: это самостоятельная картинка
    (место сбора грибов), задаётся админом отдельной кнопкой в редакторе.
    """
    if not loc:
        return None
    return loc.get("glade_photo") or None


async def update_location_glade_photo(location_id: int, file_id):
    """Задать (file_id) или убрать (None) картинку опушки леса."""
    conn = await get_db()
    if not await get_location(location_id):
        return False
    await conn.execute("UPDATE locations SET glade_photo = ? WHERE id = ?",
                       (file_id, location_id))
    await conn.commit()
    return True


async def update_location_clearing_photo(location_id: int, file_id):
    """Задать (file_id) или убрать (None) картинку прогалины."""
    conn = await get_db()
    if not await get_location(location_id):
        return False
    await conn.execute("UPDATE locations SET clearing_photo = ? WHERE id = ?",
                       (file_id, location_id))
    await conn.commit()
    return True


def location_mine_level_photo(loc):
    """file_id отдельной картинки 1-го уровня шахт (None → локальный файл по сезону).

    Уровень шахт намеренно не наследует фото входа в копь: это самостоятельная
    картинка (место добычи руды), задаётся админом отдельной кнопкой в редакторе.
    """
    if not loc:
        return None
    if isinstance(loc, dict):
        return loc.get('mine_level_photo') or None
    try:
        return loc['mine_level_photo']
    except Exception:
        try:
            return dict(loc).get('mine_level_photo')
        except Exception:
            return None


async def update_location_mine_level_photo(location_id: int, file_id):
    """Задать (file_id) или убрать (None) картинку 1-го уровня шахт."""
    conn = await get_db()
    if not await get_location(location_id):
        return False
    await conn.execute("UPDATE locations SET mine_level_photo = ? WHERE id = ?",
                       (file_id, location_id))
    await conn.commit()
    return True


def location_storage_photo(loc):
    """file_id отдельной картинки зала «Городские склады» (None → локальный файл)."""
    if not loc:
        return None
    if isinstance(loc, dict):
        return loc.get('storage_photo') or None
    try:
        return loc['storage_photo']
    except Exception:
        try:
            return dict(loc).get('storage_photo')
        except Exception:
            return None


async def update_location_storage_photo(location_id: int, file_id):
    """Задать (file_id) или убрать (None) картинку зала «Городские склады»."""
    conn = await get_db()
    if not await get_location(location_id):
        return False
    await conn.execute("UPDATE locations SET storage_photo = ? WHERE id = ?",
                       (file_id, location_id))
    await conn.commit()
    return True


def location_logging_photo(loc):
    """file_id картинки Лесозаготовки (None → сезонный локальный файл).

    Как и опушка с прогалиной, Лесозаготовка — самостоятельная картинка,
    задаётся админом отдельной кнопкой в редакторе картинок локации «Лес».
    """
    if not loc:
        return None
    if isinstance(loc, dict):
        return loc.get('logging_photo') or None
    try:
        return loc['logging_photo']
    except Exception:
        try:
            return dict(loc).get('logging_photo')
        except Exception:
            return None


async def update_location_logging_photo(location_id: int, file_id):
    """Задать (file_id) или убрать (None) картинку Лесозаготовки."""
    conn = await get_db()
    if not await get_location(location_id):
        return False
    await conn.execute("UPDATE locations SET logging_photo = ? WHERE id = ?",
                       (file_id, location_id))
    await conn.commit()
    return True


async def add_city_storage(item_id: int, qty: int) -> None:
    """Накопительно кладёт на городской склад qty единиц ресурса.

    Продажа ресурса в казну не «сжигает» его: город копит проданное (руду,
    самоцветы, а позже дерево/уголь и т.п.). Позже склад пойдёт на строительство.
    """
    if not item_id or qty <= 0:
        return
    conn = await get_db()
    await conn.execute(
        "INSERT INTO city_storage (item_id, qty, updated_at) "
        "VALUES (?, ?, CURRENT_TIMESTAMP) "
        "ON CONFLICT(item_id) DO UPDATE SET "
        "qty = qty + excluded.qty, updated_at = CURRENT_TIMESTAMP",
        (item_id, qty))
    await conn.commit()


async def get_city_storage() -> list:
    """Содержимое городского склада: строки с qty>0, по названию предмета."""
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT cs.item_id AS item_id, cs.qty AS qty, i.name AS name, "
        "i.category AS category "
        "FROM city_storage cs JOIN items i ON i.id = cs.item_id "
        "WHERE cs.qty > 0 ORDER BY i.name")
    return await cursor.fetchall()


async def user_has_exact_status(user_id: int, tag: str) -> bool:
    """Игрок имеет ровно этот статус в списке своих статусов (по access_tag)."""
    if not tag:
        return False
    conn = await get_db()
    cursor = await conn.execute("""
        SELECT 1 FROM user_statuses us
        JOIN statuses s ON us.status_id = s.id
        WHERE us.user_id = ? AND s.access_tag = ?
    """, (user_id, tag))
    return await cursor.fetchone() is not None


async def users_with_top_status_tag(tag: str) -> set:
    """Игроки, у которых СТАРШИЙ статус (max sort_order) — именно этот тег.

    Нужно для отметки туристов: «Турист» есть почти у всех (выдаётся при
    регистрации), но гостем считается только тот, у кого он и есть старший.
    """
    if not tag:
        return set()
    conn = await get_db()
    cursor = await conn.execute("""
        SELECT us.user_id, s.access_tag FROM user_statuses us
        JOIN statuses s ON us.status_id = s.id
        WHERE s.sort_order = (
            SELECT MAX(s2.sort_order) FROM user_statuses us2
            JOIN statuses s2 ON us2.status_id = s2.id
            WHERE us2.user_id = us.user_id
        )
    """)
    return {r['user_id'] for r in await cursor.fetchall() if r['access_tag'] == tag}


async def user_is_tourist(user_id: int) -> bool:
    """Пилот ещё турист: его старший статус — «Турист» (гражданства нет)."""
    conn = await get_db()
    cursor = await conn.execute("""
        SELECT s.access_tag FROM user_statuses us
        JOIN statuses s ON us.status_id = s.id
        WHERE us.user_id = ?
        ORDER BY s.sort_order DESC, s.id DESC LIMIT 1
    """, (user_id,))
    row = await cursor.fetchone()
    return bool(row) and row['access_tag'] == 'tourist'


async def citizen_user_ids() -> set:
    """user_id'ы пилотов с гражданством: старший статус не ниже «Рекрута» (sort_order >= 1).

    Единое определение гражданства для всего кода через _citizens_sql():
    отсекает «Туриста» (-10) и игроков вообще без статусов, но не трогает
    legacy-статус «Пилот» (2) и «Хранителя» (100) — Хранитель это такой же пилот,
    просто с правами.
    """
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT user_id FROM users WHERE " + _citizens_sql()
    )
    return {r['user_id'] for r in await cursor.fetchall()}


async def can_enter_location(user_id: int, key: str) -> bool:
    """Проверка доступа к локации: статусный режим + блокирующие состояния.

    НЕ проверяет специфичные условия типа читательского билета (это делает
    сам обработчик локации поверх этой функции).
    """
    loc = await get_location_by_key(key)
    if not loc:
        return True

    # 1) Статусный доступ
    mode = loc['access_mode']
    status_ok = True
    if mode == "min":
        status_ok = await user_has_status_tag(user_id, loc['required_status'])
    elif mode == "exact":
        status_ok = await user_has_exact_status(user_id, loc['required_status'])
    if not status_ok:
        return False

    # 2) Состояние не должно быть в блокирующих для этой локации
    from utils.states import place_blocked, get_state_info
    if place_blocked((await get_state_info(user_id))['names'], key):
        return False
    blocking = json.loads(loc['blocking_states'] or '[]')
    if blocking:
        info = await get_state_info(user_id)
        if any(name in blocking for name in info['names']):
            return False
    return True


async def location_access_label(mode: str, req_status: str) -> str:
    if mode == "all" or not mode:
        return "🌐 Всем"
    if mode == "exact":
        return f"🎯 Только: {req_status}"
    return f"📈 {req_status} и выше"


# ============ ГОРОДСКОЙ ПАРК (статуи) ============

# Порядок вариантов картинки статуи по времени суток.
PARK_TOD_KEYS = ("dawn", "day", "sunset", "night")


async def get_park_statues():
    conn = await get_db()
    cursor = await conn.execute("SELECT * FROM park_statues ORDER BY sort_order, id")
    rows = await cursor.fetchall()
    return [dict(r) for r in rows]


async def get_park_statue(statue_id: int):
    conn = await get_db()
    cursor = await conn.execute("SELECT * FROM park_statues WHERE id = ?", (statue_id,))
    row = await cursor.fetchone()
    return dict(row) if row else None


async def add_park_statue(name: str, description: str, images: dict, created_by: int):
    """Добавляет статую. images: {'dawn': file_id|None, 'day': ..., 'sunset': ..., 'night': ...}."""
    conn = await get_db()
    cursor = await conn.execute("SELECT COALESCE(MAX(sort_order), 0) + 1 AS n FROM park_statues")
    row = await cursor.fetchone()
    await conn.execute(
        "INSERT INTO park_statues (name, description, image_dawn, image_day, image_sunset, image_night, created_by, sort_order) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (name, description,
         images.get('dawn'), images.get('day'), images.get('sunset'), images.get('night'),
         created_by, row['n'])
    )
    await conn.commit()


async def delete_park_statue(statue_id: int):
    conn = await get_db()
    await conn.execute("DELETE FROM park_statues WHERE id = ?", (statue_id,))
    await conn.commit()


async def update_park_statue(statue_id: int, **fields):
    """Обновляет одно или несколько полей статуи (name/description/image_*)."""
    if not fields:
        return
    allowed = {'name', 'description', 'image_dawn', 'image_day', 'image_sunset', 'image_night'}
    sets = {k: v for k, v in fields.items() if k in allowed}
    if not sets:
        return
    conn = await get_db()
    assignments = ", ".join(f"{k} = ?" for k in sets)
    await conn.execute(
        f"UPDATE park_statues SET {assignments} WHERE id = ?",
        list(sets.values()) + [statue_id]
    )
    await conn.commit()


# ============ УЛОВ (рыбалка): рыба с весом ============

async def add_fish_catch(user_id: int, item_id: int, weight: int = 1,
                         kind: str = "fish", expires_at: str | None = None) -> int:
    """Записывает пойманный улов с весом/типом.

    kind='fish' — рыба, портится через 4 дня по умолчанию.
    kind='resource' — ресурс/находка, портится не портится (expires_at=None).
    Если expires_at передан явно (рынок: мороз улова), используется он.
    """
    conn = await get_db()
    if expires_at is None and kind == "fish":
        expires_at = str(int(time.time()) + RAW_FISH_SHELF_SEC)
    cursor = await conn.execute(
        "INSERT INTO fish_catches (user_id, item_id, weight, kind, expires_at) "
        "VALUES (?, ?, ?, ?, ?)",
        (user_id, item_id, weight, kind or "fish", expires_at)
    )
    await conn.commit()
    return cursor.lastrowid


async def get_fish_catches(user_id: int):
    """Свежие (непротухшие) непроданные уловы игрока вместе с данными предмета.

    Протухшая рыба удаляется (срок годности 4 дня), в инвентарь не попадает
    и не может быть использована в рецептах кухни.
    """
    conn = await get_db()
    now = int(time.time())
    await conn.execute(
        "DELETE FROM fish_catches WHERE user_id = ? AND sold_at IS NULL "
        "AND expires_at IS NOT NULL AND CAST(expires_at AS REAL) <= ?",
        (user_id, now)
    )
    await conn.commit()
    cursor = await conn.execute("""
        SELECT fc.id, fc.user_id, fc.item_id, fc.weight, fc.kind, fc.created_at, fc.expires_at,
               i.name, i.sell_price, i.rarity, i.description
        FROM fish_catches fc
        JOIN items i ON i.id = fc.item_id
        WHERE fc.user_id = ? AND fc.sold_at IS NULL
        ORDER BY fc.id
    """, (user_id,))
    rows = await cursor.fetchall()
    result = []
    for r in rows:
        r = dict(r)
        kind = r.get('kind', 'fish') or 'fish'
        r['kind'] = kind
        exp = r.get('expires_at')
        try:
            expi = int(float(exp)) if exp else None
        except (TypeError, ValueError):
            expi = None
        if kind == 'resource' or expi is None:
            # Уловы ресурсов и уловы до введения срока годности не портятся.
            if kind != 'resource':
                expi = now + RAW_FISH_SHELF_SEC
            else:
                expi = None
        r['remaining_sec'] = max(0, expi - now) if expi else 0
        result.append(r)
    return result


async def take_fish_catch(user_id: int, item_id: int, weight: int):
    """Забирает один свежий улов (для продажи на рынок) и возвращает его данные.

    Возвращает None, если свежего улова нет. Улов удаляется из fish_catches,
    а оставшийся срок годности можно «заморозить» для маркета.
    """
    conn = await get_db()
    now = int(time.time())
    cursor = await conn.execute(
        "SELECT id, expires_at FROM fish_catches WHERE user_id = ? AND item_id = ? "
        "AND weight = ? AND sold_at IS NULL "
        "AND (expires_at IS NULL OR CAST(expires_at AS REAL) > ?) "
        "ORDER BY id LIMIT 1",
        (user_id, item_id, weight, now)
    )
    row = await cursor.fetchone()
    if not row:
        return None
    await conn.execute("DELETE FROM fish_catches WHERE id = ?", (row['id'],))
    await conn.commit()
    return dict(row)


async def get_fish_catch(catch_id: int):
    conn = await get_db()
    cursor = await conn.execute("""
        SELECT fc.*, i.name, i.sell_price, i.rarity
        FROM fish_catches fc JOIN items i ON i.id = fc.item_id
        WHERE fc.id = ?
    """, (catch_id,))
    return await cursor.fetchone()


async def sell_one_fish_catch(user_id: int, item_id: int, weight: int) -> bool:
    """Списывает один свежий непроданный улов рыбы с данным весом. True — если был."""
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT id FROM fish_catches WHERE user_id = ? AND item_id = ? AND weight = ? "
        "AND sold_at IS NULL "
        "AND (expires_at IS NULL OR CAST(expires_at AS REAL) > ?) "
        "ORDER BY id LIMIT 1",
        (user_id, item_id, weight, int(time.time()))
    )
    row = await cursor.fetchone()
    if not row:
        return False
    await conn.execute("DELETE FROM fish_catches WHERE id = ?", (row['id'],))
    await conn.commit()
    return True


def fish_sold_day_key() -> str:
    """Текущие игровые сутки (10:00 МСК) для лимитов выкупа казной — рыба и лес."""
    return today_report_day()


async def fish_sold_today(user_id: int) -> int:
    """Сколько НМ игрок уже выручил за рыбу «скупщику» сегодня (МСК)."""
    conn = await get_db()
    row = await (await conn.execute(
        "SELECT fish_sold_today FROM users WHERE user_id = ?", (user_id,)
    )).fetchone()
    if not row:
        return 0
    return row['fish_sold_today'] or 0


async def fish_sale_daily_left(user_id: int) -> bool:
    """Открыта ли ещё возможность выкупа рыбы казной сегодня.

    Сбрасывает счётчик при смене суток (фолбэк, если daily_ap_recovery
    не успел или пользователь новый).
    """
    from config import FISH_TREASURY_DAILY_LIMIT
    conn = await get_db()
    user = await (await conn.execute(
        "SELECT fish_sold_today, fish_sold_day FROM users WHERE user_id = ?", (user_id,)
    )).fetchone()
    if not user:
        return True
    day = fish_sold_day_key()
    if user['fish_sold_day'] != day:
        await conn.execute(
            "UPDATE users SET fish_sold_today = 0, fish_sold_day = ? WHERE user_id = ?",
            (day, user_id)
        )
        await conn.commit()
        return True
    return (user['fish_sold_today'] or 0) < FISH_TREASURY_DAILY_LIMIT


async def add_fish_sale_amount(user_id: int, amount: int):
    """Учитывает вырученные НМ за рыбу в суточном лимите выкупа."""
    conn = await get_db()
    day = fish_sold_day_key()
    user = await (await conn.execute(
        "SELECT fish_sold_today, fish_sold_day FROM users WHERE user_id = ?", (user_id,)
    )).fetchone()
    if not user:
        return
    if user['fish_sold_day'] != day:
        await conn.execute(
            "UPDATE users SET fish_sold_today = ?, fish_sold_day = ? WHERE user_id = ?",
            (amount, day, user_id)
        )
    else:
        await conn.execute(
            "UPDATE users SET fish_sold_today = fish_sold_today + ? WHERE user_id = ?",
            (amount, user_id)
        )
    await conn.commit()


# ──────────────── Выкуп грибов казной: суточный лимит (v0.18.16) ────────────────
# Лес — единственный источник грибов, и без потолка он перебивал рыбалку: выручка
# за сутки не ограничена. Казна покупает грибы (сырые и жареные) не больше
# FOREST_SOLD_DAILY_LIMIT НМ в сутки на игрока — по аналогии с рыбой. Счётчик
# сбрасывается при смене суток МСК. Рынок игроков лимит не затрагивает.


def is_forest_mushroom_name(name: str) -> bool:
    """Гриб ли это по названию — сырой из пула леса или жареный."""
    if not name:
        return False
    if name in FOREST_RAW_MUSHROOMS:
        return True
    return any(name == fried for fried, _price, _sell in FOREST_FRIED_PRICES)


async def is_forest_mushroom(item: dict) -> bool:
    """Гриб ли предмет — с учётом грибов, добавленных админом в пул леса."""
    if not item:
        return False
    if is_forest_mushroom_name(item['name']):
        return True
    conn = await get_db()
    row = await (await conn.execute(
        "SELECT 1 FROM forest_mushrooms WHERE item_id = ? AND excluded = 0",
        (item['id'],)
    )).fetchone()
    return row is not None


async def forest_sold_today(user_id: int) -> int:
    """Сколько НМ игрок уже выручил за грибы сегодня (МСК)."""
    conn = await get_db()
    row = await (await conn.execute(
        "SELECT forest_sold_today FROM users WHERE user_id = ?", (user_id,)
    )).fetchone()
    if not row:
        return 0
    return row['forest_sold_today'] or 0


async def forest_sale_daily_left(user_id: int) -> int:
    """Сколько НМ ещё можно выручить за грибы сегодня (0 — лимит выбран).

    Лимит берётся из настроек леса (forest_settings 'sold_daily_limit'), поэтому
    правится из админки без правки кода; при отсутствии записи — из конфига.
    """
    from config import FOREST_SOLD_DAILY_LIMIT
    stored = await get_forest_setting("sold_daily_limit", FOREST_SOLD_DAILY_LIMIT)
    try:
        limit = max(0, int(stored))
    except (TypeError, ValueError):
        limit = FOREST_SOLD_DAILY_LIMIT
    conn = await get_db()
    user = await (await conn.execute(
        "SELECT forest_sold_today, forest_sold_day FROM users WHERE user_id = ?", (user_id,)
    )).fetchone()
    if not user:
        return limit
    day = fish_sold_day_key()
    if user['forest_sold_day'] != day:
        await conn.execute(
            "UPDATE users SET forest_sold_today = 0, forest_sold_day = ? WHERE user_id = ?",
            (day, user_id)
        )
        await conn.commit()
        return limit
    return max(0, limit - (user['forest_sold_today'] or 0))


async def add_forest_sale_amount(user_id: int, amount: int):
    """Учитывает вырученные НМ за грибы в суточном лимите выкупа."""
    conn = await get_db()
    day = fish_sold_day_key()
    user = await (await conn.execute(
        "SELECT forest_sold_day FROM users WHERE user_id = ?", (user_id,)
    )).fetchone()
    if not user:
        return
    if user['forest_sold_day'] != day:
        await conn.execute(
            "UPDATE users SET forest_sold_today = ?, forest_sold_day = ? WHERE user_id = ?",
            (amount, day, user_id)
        )
    else:
        await conn.execute(
            "UPDATE users SET forest_sold_today = forest_sold_today + ? WHERE user_id = ?",
            (amount, user_id)
        )
    await conn.commit()


async def migrate_legacy_junk():
    """Переносит старые копии мусора (сапог, водоросли) из инвентаря в улов.

    v0.13.3: всё, что добыто рыбалкой, хранится в fish_catches (kind='resource',
    вес 1, без срока годности). До этого «мусор» выдавался в items/inventory.
    """
    conn = await get_db()
    names = ("Старый сапог", "Кусочек водорослей")
    placeholders = ",".join("?" * len(names))
    cursor = await conn.execute(
        f"SELECT id, name, is_available FROM items WHERE name IN ({placeholders})", names)
    items = {r['name']: r['id'] for r in await cursor.fetchall()}
    if not items:
        return 0
    moved = 0
    for name, item_id in items.items():
        rows = await (await conn.execute(
            "SELECT id, user_id, quantity FROM inventory WHERE item_id = ? AND quantity > 0",
            (item_id,))).fetchall()
        for r in rows:
            for _ in range(r['quantity']):
                await conn.execute(
                    "INSERT INTO fish_catches (user_id, item_id, weight, kind, expires_at) "
                    "VALUES (?, ?, 1, 'resource', NULL)",
                    (r['user_id'], item_id)
                )
                moved += 1
            await conn.execute("DELETE FROM inventory WHERE id = ?", (r['id'],))
    if moved:
        await conn.commit()
    return moved


# ============ МАРКЕТ УЛОВА: рыба, выставленная на продажу в магазине ============

async def add_fish_offer(seller_id: int, item_id: int, weight: int,
                         price: int, remaining_sec: int, base_price: int = 0) -> int:
    """Выставляет свежий улов в магазин. Срок годности «замирает» на остатке."""
    conn = await get_db()
    cursor = await conn.execute(
        "INSERT INTO market_fish (seller_id, item_id, weight, price, remaining_sec, base_price) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (seller_id, item_id, weight, price, max(1, remaining_sec), base_price)
    )
    await conn.commit()
    return cursor.lastrowid


async def get_fish_offers():
    """Активные объявления пойманной рыбы в магазине (со сведениями о предмете)."""
    conn = await get_db()
    cursor = await conn.execute("""
        SELECT mf.id, mf.seller_id, mf.item_id, mf.weight, mf.price, mf.remaining_sec,
               i.name, i.rarity
        FROM market_fish mf
        JOIN items i ON i.id = mf.item_id
        ORDER BY mf.id
    """)
    return await cursor.fetchall()


# ──────────────── Рынок: обычные предметы (market_items) ────────────────

async def place_item_offer(seller_id: int, item_id: int, price: int) -> int:
    """Выставляет обычный предмет на рыночную витрину. Возвращает id объявления."""
    conn = await get_db()
    cursor = await conn.execute(
        "INSERT INTO market_items (seller_id, item_id, price) VALUES (?, ?, ?)",
        (seller_id, item_id, price)
    )
    await conn.commit()
    return cursor.lastrowid


async def get_item_offers():
    """Активные объявления обычных предметов на рынке (со сведениями о предмете)."""
    conn = await get_db()
    cursor = await conn.execute("""
        SELECT mi.id, mi.seller_id, mi.item_id, mi.price,
               i.name, i.rarity, i.sell_price
        FROM market_items mi
        JOIN items i ON i.id = mi.item_id
        ORDER BY mi.id
    """)
    return await cursor.fetchall()


async def get_item_offer(offer_id: int):
    """Одно объявление обычного предмета (со сведениями о предмете)."""
    conn = await get_db()
    cursor = await conn.execute("""
        SELECT mi.*, i.name, i.rarity, i.sell_price
        FROM market_items mi
        JOIN items i ON i.id = mi.item_id
        WHERE mi.id = ?
    """, (offer_id,))
    return await cursor.fetchone()


async def remove_item_offer(offer_id: int) -> bool:
    """Удаляет объявление обычного предмета (куплено или снято)."""
    conn = await get_db()
    cursor = await conn.execute("DELETE FROM market_items WHERE id = ?", (offer_id,))
    await conn.commit()
    return cursor.rowcount > 0


async def get_fish_offer(offer_id: int):
    conn = await get_db()
    cursor = await conn.execute("""
        SELECT mf.*, i.name, i.rarity, i.sell_price
        FROM market_fish mf
        JOIN items i ON i.id = mf.item_id
        WHERE mf.id = ?
    """, (offer_id,))
    return await cursor.fetchone()


async def remove_fish_offer(offer_id: int) -> bool:
    """Удаляет объявление (рыба куплена или снята)."""
    conn = await get_db()
    cursor = await conn.execute("DELETE FROM market_fish WHERE id = ?", (offer_id,))
    await conn.commit()
    return cursor.rowcount > 0


# ---------- Пулы рыбалки по водоёмам (water_fish) ----------

# Дефолтные веса рыб по водоёмам (имена → день, ночь). Админ может править
# веса/картинку/цену через редактор рыбалки; тогда строка помечается admin_tuned
# и на старте не перезаписывается.
WATER_FISH_DEFAULTS = {
    "lake": [
        ("Сиг", 65, 63),
        ("Муксун", 25, 23),
        ("Чир", 10, 9),
        ("Налим", 0, 5),
    ],
    "reservoir": [
        ("Мерцающий сом", 70, 70),
        ("Искрящийся угорь", 25, 25),
        ("Светящаяся форель", 5, 5),
    ],
}
WATER_LABELS = {"lake": "Озеро в парке", "reservoir": "Подземное водохранилище"}

# Находки со дна без наживки (мусор): имя → базовый шанс выпадения %.
# Шансы и картинки правятся админом в редакторе рыбалки (таблица water_junk),
# стартовая синхронизация не перезаписывает правки (admin_tuned).
JUNK_ITEM_NAMES = ("Кусочек водорослей", "Старый сапог")
JUNK_DEFAULT_CHANCES = {"Кусочек водорослей": 15, "Старый сапог": 2}
JUNK_EMOJI = {"Кусочек водорослей": "🥬", "Старый сапог": "👢"}


async def ensure_water_fish():
    """Идемпотентно засевает water_fish из дефолтов. Правившие админом строки
    (admin_tuned=1) не перезаписываются."""
    conn = await get_db()
    changed = False
    for water, entries in WATER_FISH_DEFAULTS.items():
        for name, day_w, night_w in entries:
            item = await get_item_by_name(name)
            if not item:
                continue
            cursor = await conn.execute(
                "SELECT id, admin_tuned, day_weight, night_weight, excluded FROM water_fish "
                "WHERE water = ? AND item_id = ?",
                (water, item['id'])
            )
            row = await cursor.fetchone()
            if row is None:
                await conn.execute(
                    "INSERT INTO water_fish (water, item_id, day_weight, night_weight) "
                    "VALUES (?, ?, ?, ?)",
                    (water, item['id'], day_w, night_w)
                )
                changed = True
            elif not row['excluded'] and not row['admin_tuned'] and (
                    row['day_weight'] != day_w or row['night_weight'] != night_w
            ):
                await conn.execute(
                    "UPDATE water_fish SET day_weight = ?, night_weight = ? WHERE id = ?",
                    (day_w, night_w, row['id'])
                )
                changed = True
    # Находки со дна (без наживки): шанс и картинка на водоём.
    # Существующие строки не трогаем — только добираем отсутствующие,
    # поэтому правки админа (admin_tuned) переживают перезапуски.
    for _water in WATER_LABELS:
        for _jname in JUNK_ITEM_NAMES:
            _jc = await conn.execute(
                "SELECT id FROM water_junk WHERE water = ? AND name = ?",
                (_water, _jname)
            )
            if not (await _jc.fetchone()):
                await conn.execute(
                    "INSERT INTO water_junk (water, name, chance) VALUES (?, ?, ?)",
                    (_water, _jname, JUNK_DEFAULT_CHANCES.get(_jname, 0))
                )
                changed = True
    if changed:
        await conn.commit()
    return changed


async def get_water_junk_rows(water: str):
    """Находки со дна водоёма для админ-карточки."""
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT id, water, name, chance, photo_file_id, admin_tuned "
        "FROM water_junk WHERE water = ? ORDER BY id",
        (water,)
    )
    return await cursor.fetchall()


async def get_water_junk_map(water: str) -> dict:
    """name → {'chance': %, 'photo_file_id': ...|None}. Пустые водоёмы
    отдают дефолтные шансы из JUNK_DEFAULT_CHANCES (слоёный фолбэк)."""
    rows = await get_water_junk_rows(water)
    if not rows:
        return {n: {"chance": JUNK_DEFAULT_CHANCES.get(n, 0), "photo_file_id": None}
                for n in JUNK_ITEM_NAMES}
    return {r['name']: {"chance": r['chance'] or 0,
                        "photo_file_id": r['photo_file_id']} for r in rows}


async def update_water_junk(water: str, name: str, field: str, value) -> bool:
    """Правка находки водоёма (chance / photo_file_id). Помечает admin_tuned,
    чтобы стартовая синхронизация не вернула дефолтные значения."""
    conn = await get_db()
    if field not in ("chance", "photo_file_id"):
        return False
    if field == "chance":
        await conn.execute(
            "UPDATE water_junk SET chance = ?, admin_tuned = 1 "
            "WHERE water = ? AND name = ?",
            (max(0, int(value)), water, name)
        )
    else:
        await conn.execute(
            "UPDATE water_junk SET photo_file_id = ?, admin_tuned = 1 "
            "WHERE water = ? AND name = ?",
            (value or None, water, name)
        )
    await conn.commit()
    return True


async def get_water_fish_rows(water: str):
    """Все рыбы водоёма для админ-редактора (с данными предмета)."""
    conn = await get_db()
    cursor = await conn.execute("""
        SELECT wf.id, wf.water, wf.item_id, wf.day_weight, wf.night_weight,
               wf.photo_file_id, wf.admin_tuned, wf.kind, wf.super_rare,
               i.name, i.sell_price, i.rarity, i.price, i.market_ok
        FROM water_fish wf
        JOIN items i ON i.id = wf.item_id
        WHERE wf.water = ? AND wf.excluded = 0
        ORDER BY wf.id
    """, (water,))
    return await cursor.fetchall()


async def get_water_fish_row(wf_id: int):
    """Одна рыба водоёма с данными предмета (для карточки админа)."""
    conn = await get_db()
    cursor = await conn.execute("""
        SELECT wf.id, wf.water, wf.item_id, wf.day_weight, wf.night_weight,
               wf.photo_file_id, wf.admin_tuned, wf.kind, wf.super_rare,
               i.name, i.sell_price, i.rarity, i.price, i.market_ok
        FROM water_fish wf
        JOIN items i ON i.id = wf.item_id
        WHERE wf.id = ?
    """, (wf_id,))
    return await cursor.fetchone()


async def get_water_fish_pool(water: str):
    """Пулы: список рыб водоёма с весами (день/ночь), фото и ценой продажи."""
    conn = await get_db()
    cursor = await conn.execute("""
        SELECT wf.id, wf.item_id, wf.day_weight, wf.night_weight, wf.photo_file_id, wf.kind,
               wf.super_rare,
               i.name, i.sell_price, i.rarity
        FROM water_fish wf
        JOIN items i ON i.id = wf.item_id
        WHERE wf.water = ? AND wf.excluded = 0 AND (wf.day_weight > 0 OR wf.night_weight > 0)
        ORDER BY wf.id
    """, (water,))
    return await cursor.fetchall()


async def get_water_fish_photo_by_name(water: str, name: str):
    """Telegram photo_file_id рыбы в водоёме (или None)."""
    conn = await get_db()
    cursor = await conn.execute("""
        SELECT wf.photo_file_id FROM water_fish wf
        JOIN items i ON i.id = wf.item_id
        WHERE wf.water = ? AND i.name = ? AND wf.photo_file_id IS NOT NULL
        LIMIT 1
    """, (water, name))
    row = await cursor.fetchone()
    return row['photo_file_id'] if row else None


async def get_water_fish_kind(water: str, name: str) -> str:
    """Тип записи водоёма: 'fish' или 'resource' (по умолчанию 'fish')."""
    conn = await get_db()
    cursor = await conn.execute("""
        SELECT wf.kind FROM water_fish wf
        JOIN items i ON i.id = wf.item_id
        WHERE wf.water = ? AND i.name = ?
        LIMIT 1
    """, (water, name))
    row = await cursor.fetchone()
    kind = (row['kind'] if row else None) or 'fish'
    return kind if kind in ("fish", "resource") else "fish"


async def update_water_fish_field(wf_id: int, field: str, value) -> bool:
    """Правка рыбы в водоёме (day_weight/night_weight/kind/photo_file_id). Помечает admin_tuned."""
    conn = await get_db()
    if field in ("day_weight", "night_weight"):
        await conn.execute(
            f"UPDATE water_fish SET {field} = ?, admin_tuned = 1 WHERE id = ?",
            (int(value), wf_id)
        )
    elif field == "kind":
        kind = "resource" if str(value) == "resource" else "fish"
        await conn.execute(
            "UPDATE water_fish SET kind = ?, admin_tuned = 1 WHERE id = ?",
            (kind, wf_id)
        )
    elif field == "photo_file_id":
        await conn.execute(
            "UPDATE water_fish SET photo_file_id = ?, admin_tuned = 1 WHERE id = ?",
            (value or None, wf_id)
        )
    elif field == "super_rare":
        await conn.execute(
            "UPDATE water_fish SET super_rare = ?, admin_tuned = 1 WHERE id = ?",
            (1 if value else 0, wf_id)
        )
    else:
        return False
    await conn.commit()
    return True


async def set_water_fish_sell_price(wf_id: int, sell_price: int) -> bool:
    """Цена продажи рыбы (обновляет items.sell_price). Помечает admin_tuned."""
    conn = await get_db()
    cursor = await conn.execute("SELECT item_id FROM water_fish WHERE id = ?", (wf_id,))
    row = await cursor.fetchone()
    if not row:
        return False
    await conn.execute("UPDATE items SET sell_price = ? WHERE id = ?", (int(sell_price), row['item_id']))
    await conn.execute("UPDATE water_fish SET admin_tuned = 1 WHERE id = ?", (wf_id,))
    await conn.commit()
    return True


async def add_water_fish(water: str, item_id: int, day_weight: int = 1,
                         night_weight: int = 1) -> int | None:
    """Добавляет рыбу в водоём (или возвращает убранную). Помечает admin_tuned,
    чтобы стартовая синхронизация не перезаписала настройки. Возвращает wf_id."""
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT id FROM water_fish WHERE water = ? AND item_id = ?",
        (water, item_id)
    )
    row = await cursor.fetchone()
    if row:
        wf_id = row['id']
        await conn.execute(
            "UPDATE water_fish SET excluded = 0, day_weight = ?, night_weight = ?, "
            "admin_tuned = 1 WHERE id = ?",
            (int(day_weight), int(night_weight), wf_id)
        )
    else:
        cursor = await conn.execute(
            "INSERT INTO water_fish (water, item_id, day_weight, night_weight, admin_tuned) "
            "VALUES (?, ?, ?, ?, 1)",
            (water, item_id, int(day_weight), int(night_weight))
        )
        wf_id = cursor.lastrowid
    await conn.commit()
    return wf_id


async def remove_water_fish(wf_id: int) -> bool:
    """Убирает рыбу из водоёма (мягкое удаление: excluded=1)."""
    conn = await get_db()
    cursor = await conn.execute(
        "UPDATE water_fish SET excluded = 1, admin_tuned = 1 WHERE id = ?", (wf_id,)
    )
    await conn.commit()
    return cursor.rowcount > 0


async def create_water_fish(water: str, name: str, sell_price: int,
                            day_weight: int = 1, night_weight: int = 1,
                            description: str = None,
                            photo_file_id: str = None,
                            added_by: int = None,
                            super_rare: int = 0) -> tuple:
    """Создаёт новую рыбу прямо в водоёме: предмет (категория fishing) +
    запись пула water_fish. Предмет НЕ попадает в магазин (is_available=0) и
    ловится только в этом водоёме; строка помечается admin_tuned, чтобы
    стартовая синхронизация её не перезаписала.

    Возвращает (ok, result): True, {item_id, wf_id} либо False, текст ошибки."""
    conn = await get_db()
    try:
        cursor = await conn.execute(
            """INSERT INTO items (name, description, photo_file_id, price,
               sell_price, rarity, category, stock, added_by, market_ok)
               VALUES (?, ?, ?, 0, ?, 1, 'fishing', -1, ?, 1)""",
            (name, description, photo_file_id, int(sell_price), added_by)
        )
        item_id = cursor.lastrowid
        await conn.execute(
            "UPDATE items SET is_available = 0 WHERE id = ?", (item_id,))
        cursor = await conn.execute(
            """INSERT INTO water_fish (water, item_id, day_weight, night_weight,
               photo_file_id, admin_tuned, super_rare)
               VALUES (?, ?, ?, ?, ?, 1, ?)""",
            (water, item_id, int(day_weight), int(night_weight), photo_file_id,
             1 if super_rare else 0)
        )
        wf_id = cursor.lastrowid
        await conn.commit()
        return True, {"item_id": item_id, "wf_id": wf_id}
    except Exception:
        await conn.rollback()
        return False, "Не удалось создать рыбу — проверь параметры."


async def get_water_fish_candidates(water: str):
    """Рыбы и ресурсы (предметы категорий fishing/resource/consumable вне магазина),
    которых ещё нет в водоёме, — для кнопки «Добавить рыбу»."""
    conn = await get_db()
    cursor = await conn.execute("""
        SELECT i.id, i.name, i.sell_price, i.rarity, i.category
        FROM items i
        WHERE i.category IN ('fishing', 'resource', 'consumable')
          AND i.is_available = 0
          AND i.id NOT IN (
              SELECT item_id FROM water_fish WHERE water = ? AND excluded = 0
          )
        ORDER BY i.name
    """, (water,))
    return await cursor.fetchall()


# ──────────────── Лес на окраине: грибы (v0.18.15) ────────────────

# Пул грибов леса: имя → (вес в пуле, тип). Сумма весов 96 — это НЕ проценты:
# находка гриба задаётся константой FOREST_EMPTY_CHANCE в bot/handlers/forest.py
# (10% «ничего не нашёл»), а оставшиеся 90% делятся между грибами по их весам.
# Крайняя редкость — у Ежовика гребенчатого, самая частая — Опёнок.
FOREST_DEFAULTS = [
    ("Опёнок", 25, "edible"),
    ("Подберёзовик", 18, "edible"),
    ("Лисичка", 15, "edible"),
    ("Белый гриб", 12, "edible"),
    ("Гиропор", 8, "edible"),
    ("Ежовик гребенчатый", 4, "edible"),
    ("Мухомор", 9, "toxic"),
    ("Бледная поганка", 5, "toxic"),
]

# Параметры сырых грибов: имя → (цена, продажа, редкость, heal, тип).
# heal > 0 у съедобных — можно съесть сырым (в бою подземелья, как зелья);
# ядовитые — ресурс (есть нельзя).
FOREST_RAW_MUSHROOMS = {
    "Опёнок": (20, 3, 1, 4, "edible"),
    "Подберёзовик": (30, 5, 1, 6, "edible"),
    "Лисичка": (45, 8, 2, 8, "edible"),
    "Белый гриб": (60, 12, 2, 10, "edible"),
    "Гиропор": (120, 20, 3, 14, "edible"),
    "Ежовик гребенчатый": (200, 35, 4, 18, "edible"),
    "Мухомор": (15, 3, 1, 0, "toxic"),
    "Бледная поганка": (20, 4, 2, 0, "toxic"),
}

# Остальные предметы леса: имя → (описание, цена, продажа, редкость, категория, heal, market_ok).
# Все вне магазина (is_available=0): добываются только в лесу/через крафт.
FOREST_ITEM_SEEDS = [
    ("Мясо кабана",
     "Свежее мясо кабана с лесной охоты. В сыром виде есть нельзя — прожарь на кухне.",
     40, 10, 2, "resource", 0, 1),
    ("Шкура кабана",
     "Сырая и тяжёлая шкура старого кабана. Битва была не зря — пригодится для крафта.",
     60, 15, 3, "resource", 0, 1),
    ("Клык кабана",
     "Опасный изогнутый клык старого кабана. Редкая добыча — набитые мастера возьмут такой в работу.",
     100, 40, 4, "resource", 0, 1),
    ("Мясо волка",
     "Парное мясо серого волка. В сыром виде есть нельзя — прожарь на кухне.",
     35, 8, 1, "resource", 0, 1),
    ("Шкура волка",
     "Плотная серая шкура волка. Ценится у мастеров-скорняков.",
     90, 35, 3, "resource", 0, 1),
    ("Клык волка",
     "Острый клык старого волка. Редкая добыча — оружейники возьмут такой в работу.",
     120, 50, 4, "resource", 0, 1),
    ("Жареный опёнок",
     "Поджаренные на углях опята: +12 HP в бою. Срок годности 4 суток.",
     18, 9, 1, "consumable", 12, 1),
    ("Жареный подберёзовик",
     "Поджаренный на углях подберёзовик: +18 HP в бою. Срок годности 4 суток.",
     28, 14, 1, "consumable", 18, 1),
    ("Жареные лисички",
     "Ароматные жареные лисички: +26 HP в бою. Срок годности 4 суток.",
     44, 22, 2, "consumable", 26, 1),
    ("Жареный белый гриб",
     "Жареный белый гриб — гордость охотника: +34 HP в бою. Срок годности 4 суток.",
     64, 32, 2, "consumable", 34, 1),
    ("Жареный гиропор",
     "Редкий жареный гиропор: +48 HP в бою. Срок годности 4 суток.",
     120, 60, 3, "consumable", 48, 1),
    ("Жареный ежовик гребенчатый",
     "Деликатес из самого редкого гриба леса: +70 HP в бою. Срок годности 4 суток.",
     200, 100, 4, "consumable", 70, 1),
    ("Жареное мясо кабана",
     "Жаренное на костре мясо кабана: +30 HP в бою. Срок годности 4 суток.",
     90, 45, 2, "consumable", 30, 1),
    ("Бутылочка с ядом",
     "Мутное зелье, сваренное из ядовитых лесных грибов. На рынок выставлять нельзя — "
     "пригодится кузнецу для улучшения оружия (например, ножа).",
     150, 75, 2, "resource", 0, 0),
    ("Грибной целебный порошок",
     "Сухой целебный порошок из перетёртых лесных грибов. Базовый ресурс для алхимии и крафта.",
     15, 5, 1, "resource", 0, 1),
    ("Грибная эссенция",
     "Концентрированная вытяжка из редких лесных грибов. Ценный ингредиент для особых рецептов.",
     120, 45, 3, "resource", 0, 1),
    ("Ядовитый грибной порошок",
     "Едкий порошок из высушенных ядовитых грибов. Опасный ресурс для ядов и ремесла.",
     20, 6, 2, "resource", 0, 1),
]

# Прямая добыча с врагов — только с них и ниоткуда: вне магазина (is_available=0),
# вне рынка игроков (market_ok=0) и помечена loot_only, чтобы админ видел пометку
# «Только лут с врагов» и случайно не вернул её в продажу. Продать в казну за
# деньги по-прежнему можно, крафт и выдача с врагов работают как раньше.
FOREST_ENEMY_DROPS = ("Мясо кабана", "Шкура кабана", "Клык кабана",
                      "Мясо волка", "Шкура волка", "Клык волка")

# Цены продажи жареных грибов (v0.18.16, были вдвое выше): имя → (цена, продажа).
# Синхронизируются при каждом старте, поэтому пересчёт задевает и прод-БД.
FOREST_FRIED_PRICES = (
    ("Жареный опёнок", 18, 9),
    ("Жареный подберёзовик", 28, 14),
    ("Жареные лисички", 44, 22),
    ("Жареный белый гриб", 64, 32),
    ("Жареный гиропор", 120, 60),
    ("Жареный ежовик гребенчатый", 200, 100),
)


async def ensure_forest_items():
    """Идемпотентно создаёт предметы леса (грибы, добыча кабана, жареные блюда, яд).

    Все предметы вне магазина (is_available=0): добываются только в лесу или
    через рецепты. Съедобные грибы можно выставлять на рынок (market_ok=1).
    """
    conn = await get_db()
    added = False

    # Сырые грибы: категория по типу (съедобный — расходник с лечением в бою).
    for name, (price, sell, rare, heal, kind) in FOREST_RAW_MUSHROOMS.items():
        cursor = await conn.execute("SELECT COUNT(*) as c FROM items WHERE name = ?", (name,))
        if (await cursor.fetchone())['c'] == 0:
            category = "consumable" if kind == "edible" else "resource"
            desc = (
                "Лесной гриб: можно съесть сырым (+%d HP в бою подземелья). Лучше пожарить на кухне."
                % heal if heal else
                "Ядовитый лесной гриб: есть нельзя. Понадобится, чтобы сварить «Бутылочку с ядом»."
            )
            await add_item(name=name, description=desc, price=price, sell_price=sell,
                           rarity=rare, category=category, stock=-1, added_by=0,
                           ap_cost=0, damage=0, heal=heal, market_ok=1)
            added = True
    # Синхронизация сырых грибов у существующих БД: лечение (как жареная рыба)
    # и скрытие из магазина (is_available=0) — грибы только из леса.
    for name, (price, sell, rare, heal, kind) in FOREST_RAW_MUSHROOMS.items():
        cursor = await conn.execute(
            "SELECT id FROM items WHERE name = ? AND (heal != ? OR is_available != 0)",
            (name, heal if kind == "edible" else 0)
        )
        rows = await cursor.fetchall()
        for r in rows:
            await conn.execute(
                "UPDATE items SET is_available = 0, heal = ? WHERE id = ?",
                (heal if kind == "edible" else 0, r['id'])
            )
            added = True

    # Мясо/шкура/клык кабана, жареные блюда, бутылочка с ядом.
    for (name, desc, price, sell, rare, category, heal, market_ok) in FOREST_ITEM_SEEDS:
        cursor = await conn.execute("SELECT COUNT(*) as c FROM items WHERE name = ?", (name,))
        if (await cursor.fetchone())['c'] == 0:
            item_id = await add_item(name=name, description=desc, price=price, sell_price=sell,
                                     rarity=rare, category=category, stock=-1, added_by=0,
                                     ap_cost=0, damage=0, heal=heal, market_ok=market_ok)
            await update_item(item_id, is_available=0)
            added = True

    # v0.18.16: цены продажи жареных грибов снижены примерно вдвое — иначе кухня
    # давала 5–6x цены сырья (у жареной рыбы ровно 2x) и лес обгонял рыбалку.
    # Идемпотентная синхронизация: на проде блюда уже созданы со старыми ценами.
    for name, price, sell in FOREST_FRIED_PRICES:
        await conn.execute(
            "UPDATE items SET sell_price = ?, price = ? WHERE name = ? AND sell_price != ?",
            (sell, price, name, sell)
        )

    # Добыча кабана — строго loot-only: не в магазине и не на рынке игроков.
    # Идемпотентно, поэтому уже созданные строки тоже чинятся (флаг ставится при каждом
    # старте, независимо от того, создан предмет сейчас или давно).
    for name in FOREST_ENEMY_DROPS:
        await conn.execute(
            "UPDATE items SET is_available = 0, market_ok = 0, loot_only = 1 WHERE name = ?",
            (name,))

    # Грибные порошки и эссенция — только через переработку на кухне: в магазин
    # не выкладываются (is_available=0, stock=-1), при продаже скупщику уходят
    # на городские склады (category='resource').
    for name in ("Грибной целебный порошок", "Грибная эссенция", "Ядовитый грибной порошок"):
        await conn.execute(
            "UPDATE items SET is_available = 0, stock = -1, category = 'resource' WHERE name = ?",
            (name,))

    if added:
        await conn.commit()
    return added


async def ensure_mine_items():
    """Идемпотентно создаёт предметы Железной копи (кирка, руда, самоцветы).

    Кирка — товар магазина (is_available=1), руда — добыча шахты (вне магазина,
    market_ok=0, но без loot_only: её выкупает казна), самоцветы — прямой лут
    Летучей мыши (loot_only=1, market_ok=0).
    """
    conn = await get_db()
    added = False
    for (name, desc, price, sell, rare, category, heal) in MINE_ITEM_SEEDS:
        cursor = await conn.execute("SELECT id FROM items WHERE name = ?", (name,))
        row = await cursor.fetchone()
        is_drop = name in MINE_ENEMY_DROPS
        in_shop = name in MINE_SHOP_ITEMS
        if row is None:
            item_id = await add_item(name=name, description=desc, price=price, sell_price=sell,
                                     rarity=rare, category=category, stock=-1, added_by=0,
                                     ap_cost=0, damage=0, heal=heal, market_ok=0)
            await update_item(item_id, is_available=1 if in_shop else 0,
                              loot_only=1 if is_drop else 0)
            added = True
        else:
            await conn.execute(
                "UPDATE items SET is_available = ?, market_ok = 0, loot_only = ?, heal = ? "
                "WHERE id = ?",
                (1 if in_shop else 0, 1 if is_drop else 0, heal, row['id']))
    if added:
        await conn.commit()
    return added


async def ensure_mine_enemies():
    """Идемпотентно засевает врагов копи (Летучая мышь) из MINE_BAT_SEED.

    Сначала создаёт предметы добычи, чтобы дропы мыши нашли свои item_id.
    """
    await ensure_mine_items()
    return await _ensure_source_enemies("mine", MINE_BAT_SEED)


async def ensure_logging_items():
    """Идемпотентно создаёт предметы Лесозаготовки (топор, бревна, дропы).

    Топор — товар магазина (is_available=1, та же категория mining, что и
    Кирка). Бревна — ресурс (вне магазина, market_ok=0, без loot_only:
    их выкупает казна). Дропы змеи и неясыти — прямой лут (loot_only=1,
    market_ok=0). Доски и паки дров — ресурсы переработки: казна выкупает
    их И игроки торгуют между собой (market_ok=1, вне магазина).
    """
    conn = await get_db()
    added = False
    for (name, desc, price, sell, rare, category, heal) in LOGGING_ITEM_SEEDS:
        cursor = await conn.execute("SELECT id FROM items WHERE name = ?", (name,))
        row = await cursor.fetchone()
        is_drop = name in LOGGING_ENEMY_DROPS
        in_shop = name in LOGGING_SHOP_ITEMS
        marketable = name in LOGGING_MARKET_RESOURCES
        market_ok = 1 if marketable else 0
        if row is None:
            item_id = await add_item(name=name, description=desc, price=price, sell_price=sell,
                                     rarity=rare, category=category, stock=-1, added_by=0,
                                     ap_cost=0, damage=0, heal=heal, market_ok=market_ok)
            await update_item(item_id, is_available=1 if in_shop else 0,
                              loot_only=1 if is_drop else 0)
            added = True
        else:
            # market_ok обновляем ТОЛЬКО у ресурсов переработки: у прочих
            # предметов ветки не трогаем, чтобы не затирать админские правки.
            if marketable:
                await conn.execute(
                    "UPDATE items SET is_available = ?, market_ok = 1, loot_only = ?, heal = ? "
                    "WHERE id = ?",
                    (1 if in_shop else 0, 1 if is_drop else 0, heal, row['id']))
            else:
                await conn.execute(
                    "UPDATE items SET is_available = ?, market_ok = 0, loot_only = ?, heal = ? "
                    "WHERE id = ?",
                    (1 if in_shop else 0, 1 if is_drop else 0, heal, row['id']))
    if added:
        await conn.commit()
    return added


async def ensure_logging_enemies():
    """Идемпотентно засевает врагов Лесозаготовки (Змея и Неясыть).

    Сначала создаёт предметы добычи, чтобы дропы нашли свои item_id.
    """
    await ensure_logging_items()
    created_snake = await _ensure_source_enemies("logging", LOGGING_SNAKE_SEED)
    created_owl = await _ensure_source_enemies("logging", LOGGING_OWL_SEED)
    return created_snake or created_owl


async def ensure_forest_mushrooms():
    """Идемпотентно засевает пул грибов леса из FOREST_DEFAULTS.

    Правившие админом строки (admin_tuned=1) и удалённые (excluded=1)
    не перезаписываются — как water_fish.
    """
    conn = await get_db()
    changed = False
    for name, chance, kind in FOREST_DEFAULTS:
        item = await get_item_by_name(name)
        if not item:
            continue
        cursor = await conn.execute(
            "SELECT id, admin_tuned, chance, excluded FROM forest_mushrooms WHERE item_id = ?",
            (item['id'],)
        )
        row = await cursor.fetchone()
        if row is None:
            await conn.execute(
                "INSERT INTO forest_mushrooms (item_id, chance, kind) VALUES (?, ?, ?)",
                (item['id'], chance, kind)
            )
            changed = True
        elif not row['excluded'] and not row['admin_tuned'] and row['chance'] != chance:
            await conn.execute(
                "UPDATE forest_mushrooms SET chance = ? WHERE id = ?", (chance, row['id'])
            )
            changed = True
    if changed:
        await conn.commit()
    # v0.18.18: после сида каталога разложить его по зонам (поляна + опушка).
    # Здесь, а не только в main.py, чтобы любой вход — и тесты — видел готовые пулы.
    await ensure_forest_zones()
    return changed


async def get_forest_mushroom_pool(area: str = "clearing"):
    """Грибы зоны леса для сбора: с шансом зоны, фото, ценой и лечением предмета.

    Шансы берутся из forest_zone_pool — свой вес у гриба в каждой зоне (на опушке
    и на поляне один и тот же гриб может стоить по-разному). 'chance' в
    forest_mushrooms — вес гриба в зоне 'clearing' (историческое поле).
    """
    if area not in FOREST_AREAS:
        area = "clearing"
    conn = await get_db()
    cursor = await conn.execute("""
        SELECT fm.id, fm.item_id, zp.mushroom_id, zp.chance, fm.photo_file_id, fm.kind,
               i.name, i.sell_price, i.rarity, i.heal
        FROM forest_zone_pool zp
        JOIN forest_mushrooms fm ON fm.id = zp.mushroom_id
        JOIN items i ON i.id = fm.item_id
        WHERE zp.area = ? AND fm.excluded = 0 AND zp.chance > 0
        ORDER BY fm.id
    """, (area,))
    return await cursor.fetchall()


# ──────────────── Зоны леса: опушка и лесная поляна (v0.18.18) ────────────────
# Лес разделён на две зоны. Опушка — простое начало: только четыре первых
# съедобных гриба и Бледная поганка, кабана нет, туристов пускаем. Лесная поляна
# — «второй уровень»: весь пул грибов и кабан, туристам закрыта (не местные,
# легко заблудиться). Всё содержимое зон правится в админ-редакторе леса.
FOREST_AREAS = ("glade", "clearing")

# Значения по умолчанию (используются, пока строки в forest_zones не созданы):
# опушка — 4 ОД и туристы допущены; поляна — 5 ОД, только пилоты, кабан.
FOREST_AREA_DEFAULTS = {
    "glade": {
        "title": "Опушка леса",
        "ap_cost": 4,
        "allow_tourists": 1,
        "boar_enabled": 0,
        "boar_chance": 0,
        "boar_every": 0,
        "enabled": 1,
    },
    "clearing": {
        "title": "Лесная поляна",
        "ap_cost": 5,
        "allow_tourists": 0,
        "boar_enabled": 1,
        # 0 = брать шанс и гарантию из карточки врага («⚔️ Враги» → лес).
        # Ненулевое значение перекрывает карточку — удобно, если поляна опаснее.
        "boar_chance": 0,
        "boar_every": 0,
        "enabled": 1,
    },
}

# Пул опушки по умолчанию: четыре первых простых гриба + Бледная поганка.
FOREST_GLADE_DEFAULTS = [
    ("Опёнок", 40),
    ("Подберёзовик", 30),
    ("Лисичка", 18),
    ("Белый гриб", 8),
    ("Бледная поганка", 4),
]

FOREST_ZONE_FIELDS = ("title", "ap_cost", "allow_tourists", "boar_enabled",
                      "boar_chance", "boar_every", "enabled")
_FOREST_ZONE_INT = ("ap_cost", "allow_tourists", "boar_enabled",
                    "boar_chance", "boar_every", "enabled")


async def get_forest_zones() -> dict:
    """Настройки всех зон леса: {area: {...}}. Дефолты подставляются за строку из БД."""
    zones = {}
    for area, defaults in FOREST_AREA_DEFAULTS.items():
        row = dict(defaults)
        row["key"] = area
        zones[area] = row
    conn = await get_db()
    for row in await (await conn.execute("SELECT * FROM forest_zones")).fetchall():
        if row["key"] in zones:
            for field in FOREST_ZONE_FIELDS:
                if row[field] is not None:
                    zones[row["key"]][field] = row[field]
    return zones


async def get_forest_zone(area: str) -> dict:
    """Настройки одной зоны леса (с дефолтами)."""
    return (await get_forest_zones()).get(area) or dict(
        FOREST_AREA_DEFAULTS.get(area) or FOREST_AREA_DEFAULTS["clearing"], key=area)


async def update_forest_zone(area: str, **fields) -> bool:
    """Правка настроек зоны: цена ОД, туристы, кабан, открытость, название."""
    if area not in FOREST_AREAS:
        return False
    data = {k: v for k, v in fields.items() if k in FOREST_ZONE_FIELDS}
    if not data:
        return False
    for k in _FOREST_ZONE_INT:
        if k in data:
            data[k] = max(0 if k != "ap_cost" else 1, int(data[k] or 0))
    sets = ", ".join(f"{k} = ?" for k in data)
    conn = await get_db()
    await conn.execute(
        f"INSERT INTO forest_zones (key, {', '.join(data)}) VALUES (?, "
        f"{', '.join('?' * len(data))}) "
        f"ON CONFLICT(key) DO UPDATE SET {', '.join(f'{k} = excluded.{k}' for k in data)}",
        (area, *data.values()),
    )
    await conn.commit()
    return True


async def get_forest_setting(key: str, default=None):
    """Общая настройка леса (например, выкуп казной 'sold_daily_limit')."""
    conn = await get_db()
    row = await (await conn.execute(
        "SELECT value FROM forest_settings WHERE key = ?", (key,))).fetchone()
    if not row or row["value"] is None:
        return default
    return row["value"]


async def set_forest_setting(key: str, value):
    conn = await get_db()
    await conn.execute(
        "INSERT INTO forest_settings (key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value", (key, str(value)))
    await conn.commit()
    return True


async def get_forest_zone_pool(area: str) -> list:
    """Грибы зоны для админ-редактора (вес зоны + данные предмета)."""
    if area not in FOREST_AREAS:
        area = "clearing"
    conn = await get_db()
    cursor = await conn.execute("""
        SELECT fm.id, fm.item_id, zp.mushroom_id, zp.chance, fm.photo_file_id,
               fm.admin_tuned, fm.kind, i.name, i.sell_price, i.rarity, i.price,
               i.market_ok, i.heal
        FROM forest_zone_pool zp
        JOIN forest_mushrooms fm ON fm.id = zp.mushroom_id
        JOIN items i ON i.id = fm.item_id
        WHERE zp.area = ?
        ORDER BY fm.id
    """, (area,))
    return await cursor.fetchall()


async def get_forest_zone_candidates(area: str) -> list:
    """Грибы каталога, которых ещё нет в зоне (для добавления)."""
    if area not in FOREST_AREAS:
        area = "clearing"
    conn = await get_db()
    cursor = await conn.execute("""
        SELECT fm.id AS mushroom_id, fm.item_id, fm.kind, i.name, i.sell_price
        FROM forest_mushrooms fm
        JOIN items i ON i.id = fm.item_id
        WHERE fm.excluded = 0
          AND fm.id NOT IN (SELECT mushroom_id FROM forest_zone_pool WHERE area = ?)
        ORDER BY fm.id
    """, (area,))
    return await cursor.fetchall()


async def add_forest_mushroom_to_zone(area: str, mushroom_id: int, chance: int = 10) -> bool:
    """Добавить гриб каталога в зону с весом (chance=0 — не выпадает)."""
    if area not in FOREST_AREAS:
        return False
    conn = await get_db()
    row = await (await conn.execute(
        "SELECT id FROM forest_mushrooms WHERE id = ?", (mushroom_id,))).fetchone()
    if not row:
        return False
    await conn.execute(
        "INSERT INTO forest_zone_pool (area, mushroom_id, chance) VALUES (?, ?, ?) "
        "ON CONFLICT(area, mushroom_id) DO UPDATE SET chance = excluded.chance",
        (area, mushroom_id, max(0, int(chance or 0))))
    await conn.commit()
    return True


async def remove_forest_mushroom_from_zone(area: str, mushroom_id: int) -> bool:
    """Убрать гриб из зоны (в каталоге он остаётся)."""
    if area not in FOREST_AREAS:
        return False
    conn = await get_db()
    await conn.execute(
        "DELETE FROM forest_zone_pool WHERE area = ? AND mushroom_id = ?",
        (area, mushroom_id))
    await conn.commit()
    return True


async def set_forest_zone_chance(area: str, mushroom_id: int, chance: int) -> bool:
    """Задать вес гриба в зоне (0 — не выпадает, но остаётся в списке)."""
    if area not in FOREST_AREAS:
        return False
    conn = await get_db()
    cur = await conn.execute(
        "UPDATE forest_zone_pool SET chance = ? WHERE area = ? AND mushroom_id = ?",
        (max(0, int(chance or 0)), area, mushroom_id))
    await conn.commit()
    return cur.rowcount > 0


async def ensure_forest_zones():
    """Разовый перенос старого пула леса в зону поляны и засев пула опушки.

    До v0.18.18 пул был один и общий. Теперь «поляна» повторяет его как есть, а
    опушка получает четыре первых съедобных гриба + Бледную поганку. Повторный
    запуск ничего не перетирает: веса админа в forest_zone_pool остаются.
    """
    conn = await get_db()
    # v0.18.19: цена ОД опушки 3→4, поляны 4→5. Правим только строки, оставшиеся
    # на старых дефолтах, — чтобы не затереть цену, которую поменял админ.
    for area, old_cost, new_cost in (("glade", 3, 4), ("clearing", 4, 5)):
        await conn.execute(
            "UPDATE forest_zones SET ap_cost = ? WHERE key = ? AND ap_cost = ?",
            (new_cost, area, old_cost))
    await conn.execute(
        "INSERT OR IGNORE INTO forest_zone_pool (area, mushroom_id, chance) "
        "SELECT 'clearing', id, chance FROM forest_mushrooms WHERE excluded = 0")
    has_glade = await (await conn.execute(
        "SELECT 1 FROM forest_zone_pool WHERE area = 'glade' LIMIT 1")).fetchone()
    if not has_glade:
        for name, chance in FOREST_GLADE_DEFAULTS:
            item = await get_item_by_name(name)
            if not item:
                continue
            row = await (await conn.execute(
                "SELECT id FROM forest_mushrooms WHERE item_id = ? AND excluded = 0",
                (item['id'],))).fetchone()
            if not row:
                continue
            await conn.execute(
                "INSERT OR IGNORE INTO forest_zone_pool (area, mushroom_id, chance) "
                "VALUES ('glade', ?, ?)", (row['id'], chance))
    for area, defaults in FOREST_AREA_DEFAULTS.items():
        await conn.execute(
            "INSERT OR IGNORE INTO forest_zones (key, title, ap_cost, allow_tourists, "
            "boar_enabled, boar_chance, boar_every, enabled) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (area, defaults['title'], defaults['ap_cost'], defaults['allow_tourists'],
             defaults['boar_enabled'], defaults['boar_chance'], defaults['boar_every'],
             defaults['enabled']))
    limit = await (await conn.execute(
        "SELECT 1 FROM forest_settings WHERE key = 'sold_daily_limit'")).fetchone()
    if not limit:
        from config import FOREST_SOLD_DAILY_LIMIT
        await conn.execute(
            "INSERT OR IGNORE INTO forest_settings (key, value) VALUES ('sold_daily_limit', ?)",
            (str(FOREST_SOLD_DAILY_LIMIT),))
    await conn.commit()
    return True

async def get_forest_mushroom_rows():
    """Все грибы леса для админ-редактора (с данными предмета)."""
    conn = await get_db()
    cursor = await conn.execute("""
        SELECT fm.id, fm.item_id, fm.chance, fm.photo_file_id, fm.admin_tuned, fm.kind,
               i.name, i.sell_price, i.rarity, i.price, i.market_ok, i.heal
        FROM forest_mushrooms fm
        JOIN items i ON i.id = fm.item_id
        WHERE fm.excluded = 0
        ORDER BY fm.id
    """)
    return await cursor.fetchall()


async def get_forest_mushroom_row(f_id: int):
    """Один гриб леса с данными предмета (для карточки админа)."""
    conn = await get_db()
    cursor = await conn.execute("""
        SELECT fm.id, fm.item_id, fm.chance, fm.photo_file_id, fm.admin_tuned, fm.kind,
               i.name, i.sell_price, i.rarity, i.price, i.market_ok, i.heal
        FROM forest_mushrooms fm
        JOIN items i ON i.id = fm.item_id
        WHERE fm.id = ?
    """, (f_id,))
    return await cursor.fetchone()


async def update_forest_mushroom_field(f_id: int, field: str, value) -> bool:
    """Правка гриба леса (chance/kind/photo_file_id). Помечает admin_tuned.

    Переключение типа edible ⇄ toxic меняет и категорию предмета: съедобный —
    расходник с лечением, ядовитый — ресурс (есть нельзя).
    """
    conn = await get_db()
    if field == "chance":
        await conn.execute(
            "UPDATE forest_mushrooms SET chance = ?, admin_tuned = 1 WHERE id = ?",
            (int(value), f_id)
        )
    elif field == "kind":
        kind = "toxic" if str(value) == "toxic" else "edible"
        await conn.execute(
            "UPDATE forest_mushrooms SET kind = ?, admin_tuned = 1 WHERE id = ?",
            (kind, f_id)
        )
        cursor = await conn.execute("SELECT item_id FROM forest_mushrooms WHERE id = ?", (f_id,))
        row = await cursor.fetchone()
        if row:
            await conn.execute(
                "UPDATE items SET category = ?, heal = 0 WHERE id = ?",
                ("resource" if kind == "toxic" else "consumable", row['item_id'])
            )
    elif field == "photo_file_id":
        await conn.execute(
            "UPDATE forest_mushrooms SET photo_file_id = ?, admin_tuned = 1 WHERE id = ?",
            (value or None, f_id)
        )
    else:
        return False
    await conn.commit()
    return True


async def set_forest_mushroom_sell_price(f_id: int, sell_price: int) -> bool:
    """Цена продажи гриба (обновляет items.sell_price). Помечает admin_tuned."""
    conn = await get_db()
    cursor = await conn.execute("SELECT item_id FROM forest_mushrooms WHERE id = ?", (f_id,))
    row = await cursor.fetchone()
    if not row:
        return False
    await conn.execute("UPDATE items SET sell_price = ? WHERE id = ?", (int(sell_price), row['item_id']))
    await conn.execute("UPDATE forest_mushrooms SET admin_tuned = 1 WHERE id = ?", (f_id,))
    await conn.commit()
    return True


async def add_forest_mushroom(item_id: int, chance: int = 10) -> int | None:
    """Добавляет гриб в пул леса (или возвращает удалённый). Помечает admin_tuned."""
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT id FROM forest_mushrooms WHERE item_id = ?", (item_id,)
    )
    row = await cursor.fetchone()
    if row:
        f_id = row['id']
        await conn.execute(
            "UPDATE forest_mushrooms SET excluded = 0, chance = ?, admin_tuned = 1 WHERE id = ?",
            (int(chance), f_id)
        )
    else:
        cursor = await conn.execute(
            "INSERT INTO forest_mushrooms (item_id, chance, admin_tuned) VALUES (?, ?, 1)",
            (item_id, int(chance))
        )
        f_id = cursor.lastrowid
    await conn.commit()
    return f_id


async def remove_forest_mushroom(f_id: int) -> bool:
    """Убирает гриб из пула леса (мягкое удаление: excluded=1)."""
    conn = await get_db()
    cursor = await conn.execute(
        "UPDATE forest_mushrooms SET excluded = 1, admin_tuned = 1 WHERE id = ?", (f_id,)
    )
    await conn.commit()
    return cursor.rowcount > 0


async def create_forest_mushroom(name: str, description: str, sell_price: int,
                                 chance: int = 10, kind: str = "edible",
                                 photo_file_id: str = None,
                                 added_by: int = None) -> tuple:
    """Создаёт новый гриб леса: предмет (вне магазина) + запись пула.

    Возвращает (ok, result): True, {item_id, f_id} либо False, текст ошибки."""
    conn = await get_db()
    try:
        category = "consumable" if kind == "edible" else "resource"
        heal = 0
        cursor = await conn.execute(
            """INSERT INTO items (name, description, photo_file_id, price,
               sell_price, rarity, category, stock, added_by, market_ok)
               VALUES (?, ?, ?, ?, ?, 1, ?, -1, ?, 1)""",
            (name, description, photo_file_id, int(sell_price) * 2, int(sell_price),
             category, added_by)
        )
        item_id = cursor.lastrowid
        await conn.execute(
            "UPDATE items SET is_available = 0, heal = ? WHERE id = ?", (heal, item_id))
        cursor = await conn.execute(
            """INSERT INTO forest_mushrooms (item_id, chance, kind, photo_file_id, admin_tuned)
               VALUES (?, ?, ?, ?, 1)""",
            (item_id, int(chance), kind, photo_file_id)
        )
        f_id = cursor.lastrowid
        # v0.18.18: новый гриб сразу попадает в пул поляны (там полный набор).
        # На опушку его добавит админ кнопкой в редакторе зоны.
        await conn.execute(
            "INSERT OR IGNORE INTO forest_zone_pool (area, mushroom_id, chance) "
            "VALUES ('clearing', ?, ?)", (f_id, int(chance)))
        await conn.commit()
        return True, {"item_id": item_id, "f_id": f_id}
    except Exception:
        await conn.rollback()
        return False, "Не удалось создать гриб — проверь параметры."


async def get_forest_mushroom_candidates():
    """Расходники/ресурсы (вне магазина), которых ещё нет в пуле леса, —
    для кнопки «➕ Добавить гриб»."""
    conn = await get_db()
    cursor = await conn.execute("""
        SELECT i.id, i.name, i.sell_price, i.rarity, i.category
        FROM items i
        WHERE i.category IN ('resource', 'consumable')
          AND i.is_available = 0
          AND i.id NOT IN (SELECT item_id FROM forest_mushrooms WHERE excluded = 0)
        ORDER BY i.name
    """)
    return await cursor.fetchall()


# ============ ВРАГИ ЛЕСА И РЫБАЛКИ (единый админ-редактор) ============
# Набор колонок у forest_enemies и fishing_enemies одинаковый, поэтому все
# запросы идут через общие функции с ключом источника ('forest' / 'fishing').
# Враги подземелья остаются в dungeon_enemies — их боевой код не трогаем.

ENEMY_SOURCE_TABLES = {"forest": "forest_enemies", "fishing": "fishing_enemies",
                       "mine": "mine_enemies", "logging": "logging_enemies",
                       "firelab": "firelab_enemies"}

# Поля врага, которые админ правит через бота.
SOURCE_ENEMY_FIELDS = ("name", "hp", "dmg_min", "dmg_max", "dodge", "armor",
                       "loss_ap", "bleed_chance", "bleed_dmg", "chance",
                       "pity_target", "reward_nm", "description", "image",
                       "photo_key", "enabled", "spot", "on_hit_effects")

ENEMY_SEED_FIELDS = ("key", "spot", "name", "hp", "dmg_min", "dmg_max", "dodge",
                     "loss_ap", "bleed_chance", "bleed_dmg", "chance",
                     "pity_target", "reward_nm", "description", "photo_key",
                     "on_hit_effects")


def _enemy_source_table(source: str) -> str:
    table = ENEMY_SOURCE_TABLES.get(source)
    if not table:
        raise ValueError(f"Неизвестный источник врагов: {source}")
    return table


async def ensure_forest_enemies():
    """Идемпотентно засевает врагов леса (кабан и Белый Волк Севера).

    Правившие админом строки (admin_tuned=1) не перезаписываются. Отдельно
    мигрируем legacy-шанс кабана: раньше он жёстко равнялся 100/PITY (8.33%) —
    если значение всё ещё равно этому дефолту, ставим новый базовый шанс
    (config.FOREST_BOAR_CHANCE), не трогая ручные правки. Убираем legacy-строку
    серого волка (key='wolf'): его заменил Белый Волк Севера (key='white_wolf').
    """
    await ensure_forest_items()
    conn = await get_db()
    await conn.execute("DELETE FROM forest_enemies WHERE key = 'wolf'")
    await conn.commit()
    created_boar = await _ensure_source_enemies("forest", FOREST_BOAR_SEED)
    created_wolf = await _ensure_source_enemies("forest", FOREST_WHITE_WOLF_SEED)
    created = created_boar or created_wolf
    legacy_chance = round(100 / config.FOREST_BOAR_PITY_TARGET, 2)
    await conn.execute(
        "UPDATE forest_enemies SET chance = ? "
        "WHERE key = 'boar' AND ROUND(chance, 2) = ?",
        (config.FOREST_BOAR_CHANCE, legacy_chance))
    await conn.commit()
    return created


async def ensure_firelab_enemies() -> bool:
    """Идемпотентно засевает врагов Огненного Лабиринта (4 обычных + босс).

    ENEMY_SEED_FIELDS не знает колонку armor — после посева дотягиваем её
    отдельным UPDATE (только нетронутые админом строки admin_tuned=0).
    """
    conn = await get_db()
    created = False
    for seed in getattr(config, "FIRELAB_ENEMY_SEEDS", ()):
        ok = await _ensure_source_enemies("firelab", seed)
        created = created or ok
        armor = int(seed.get("armor") or 0)
        await conn.execute(
            "UPDATE firelab_enemies SET armor = ? WHERE key = ? AND admin_tuned = 0",
            (armor, seed.get("key")))
    await conn.commit()
    return created


async def ensure_firelab_items() -> dict:
    """Идемпотентно создаёт предметы Фазы 3 «Дней Пламенного Круговорота».

    Ручные правки админа не перетираются — предмет заводится только при
    отсутствии по имени. Возвращает {имя: item_id} для быстрых проверок.

    Новое: 3 рыбы (fishing, торгуемые), еда (пирог, леденец), ресурсы
    (сено, ветка) и предмет-рецепт для крафта тыквенного пирога (рецепт-
    строка создаётся недоступной — состав согласует владелец на Фазе 4).
    """
    out: dict = {}
    items = (
        # (name, description, price, sell_price, rarity, category, heal, loot_only)
        (config.FIRE_LAB_FISH_OSETR_NAME,
         "Тихий осетр из колодца Огненного Лабиринта: чешуя мерцает дымкой. "
         "Ценится как обычный улов.", 0, 30, 2, "fishing", 0, 0),
        (config.FIRE_LAB_FISH_SOUL_NAME,
         "Костяная душа рыбы: холодеет даже сквозь колодец. Такие в Нордхайме "
         "не вылавливают — прорываются.", 0, 45, 3, "fishing", 0, 0),
        (config.FIRE_LAB_FISH_CARP_NAME,
         "Карп, что не испугался пламени: тёплый, как тлеющие угли. Самая "
         "редкая праздничная рыба.", 0, 90, 4, "fishing", 0, 0),
        (config.FIRE_LAB_PIE_NAME,
         "Ломоть тыквенного пирога с праздничного стола: тёплая корочка, "
         "внутри — золотистая тыква и искры корицы.", 0, 15, 2, "consumable",
         int(getattr(config, "FIRE_LAB_PIE_HEAL", 15) or 15), 1),
        (config.FIRE_LAB_CANDY_NAME,
         "Леденец из праздника Круговорота: обжигает язык, гасит голод и "
         "чуть-чуть лечит.", 0, 10, 1, "consumable",
         int(getattr(config, "FIRE_LAB_CANDY_HEAL", 12) or 12), 1),
        (config.FIRE_LAB_HAY_NAME,
         "Сено из развилок Лабиринта: Пугало смотрит на него с уважением. "
         "Ресурс для будущих поделок.", 0, 5, 1, "resource", 0, 1),
        (config.FIRE_LAB_BRANCH_NAME,
         "Чёрная ветка, сплетённая паутиной Хуба: лёгкая, но сломать не просто. "
         "Ресурс для будущих поделок.", 0, 4, 1, "resource", 0, 1),
        (config.FIRE_LAB_RECIPE_NAME,
         "Праздничный рецепт из сундука: свиток с правилами тыквенного "
         "пирога. Используй, чтобы выучить рецепт навсегда.",
         0, 0, 3, "recipes", 0, 1),
        # --- Фаза 4: посадка/ингредиенты ---
        (config.FIRE_PUMPKIN_SEED_NAME,
         "Семечко тыквы из Огненного Лабиринта. Посади в кадку в жилье — "
         "вырастет тыква (2 суток до первого плода).",
         25, 12, 2, "seeds", 0, 0),
        (config.FIRE_PUMPKIN_NAME,
         "Спелая тыква с праздничной плантации: золотистая, тугая, слегка "
         "тёплая. Ингредиент для пирога.",
         0, 12, 1, "resource", 0, 0),
        (config.FIRE_CROW_FEATHER_NAME,
         "Чёрное перо ворона из Лабиринта: пахнет гарью и остаётся холодным "
         "на ощупь. Ресурс для будущих поделок.",
         0, 6, 1, "resource", 0, 1),
        (config.FIRE_WIRE_NAME,
         "Крепкий моток железной проволоки со склада: для ремёсел и токов "
         "огня. Ингредиент Обжигающей трости.",
         40, 20, 1, "resource", 0, 0),
        (config.FIRE_SUGAR_NAME,
         "Мешочек белого сахара с рынка. Ингредиент праздничной выпечки.",
         6, 3, 1, "consumable", 0, 0),
        (config.FIRE_EGGS_NAME,
         "Парочка свежих яиц с птичьего двора. В тесто — по рецепту.",
         12, 6, 1, "consumable", 0, 0),
        # --- Фаза 4: экипировка (броня 2 + бонус по слоту) ---
        (config.FIRE_CROWN_NAME,
         "Тлеющий венец стража Круговорота: тёплые ветки в короне углей. "
         f"Броня 2, лечение расходников +{getattr(config, 'FIRE_CROWN_HEAL_BONUS_PCT', 25)}%.",
         0, 150, 3, "equipment", 0, 1),
        (config.FIRE_CLOAK_NAME,
         "Плащ, сотканный из дыма и памяти домов. Броня 2, уклонение "
         f"+{getattr(config, 'FIRE_CLOAK_DODGE', 5)}%.",
         0, 130, 3, "equipment", 0, 1),
        (config.FIRE_GLOVES_NAME,
         "Рукавицы стражей посевов: жар не проведёшь. Броня 2, уклонение "
         f"+{getattr(config, 'FIRE_GLOVES_DODGE', 3)}%.",
         0, 110, 3, "equipment", 0, 1),
        # --- Фаза 4: оружие ---
        (config.FIRE_KEYS_NAME,
         "Вилы стража посевов: одиночная зубастая работа. "
         f"К удару +{getattr(config, 'FIRE_KEYS_DMG', 2)}, шанс кровотечения "
         f"{getattr(config, 'FIRE_KEYS_BLEED_P', 10)}% (−{getattr(config, 'FIRE_KEYS_BLEED_DMG', 2)} HP/ход).",
         180, 90, 2, "weapon", 0, 0),
        (config.FIRE_CANE_NAME,
         "Сержантская трость, закованная в РПУ: поджигает врага при ударе. "
         f"К удару +{getattr(config, 'FIRE_CANE_DMG', 3)}, шанс поджога "
         f"{getattr(config, 'FIRE_CANE_BURN_P', 20)}% "
         f"(−{getattr(config, 'FIRE_CANE_BURN_DMG', 2)} HP/ход). Только крафт.",
         0, 220, 4, "weapon", 0, 1),
        (config.FIRE_LANTERN_NAME,
         "Лампа Круговорота — награда тем, кто помнит предков. Ставится в "
         "личное жильё (медитация и Пламя Памяти).",
         0, 0, 5, "special", 0, 1),
        (config.FIRE_AMBER_NAME,
         "Кусок янтаря с тёплым пламенем внутри. Можно продать за 100 НМ "
         "или сберечь как ресурс будущих крафтов.",
         0, 100, 3, "resource", 0, 0),
        (config.FIRE_TREE_CLAN_ESSENCE_NAME,
         "Большой кристалл янтаря из Древа Круговорота: тёплый, как очаг всех "
         "домов разом. Продаётся скупщику за 500 НМ или пойдёт на склад клана "
         "под будущие крафты.",
         0, int(getattr(config, "FIRE_TREE_CLAN_ESSENCE_SELL", 500) or 500),
         4, "resource", 0, 0),
        (config.FIRE_FLAME_DEVICE_NAME,
         "Ручное пламенеющее устройство: тлеет, точно маленький майак. "
         "Сердце Обжигающей трости.",
         0, 60, 3, "resource", 0, 1),
        ("Рецепт: Обжигающая трость",
         "Свиток, снятый с алтаря Тыквы: правила заковки трости в огонь. "
         "Используй, чтобы выучить рецепт навсегда.",
         0, 0, 3, "recipes", 0, 1),
    )
    for name, desc, price, sell, rarity, cat, heal, loot_only in items:
        item = await get_item_by_name(name)
        if not item:
            item_id = await add_item(
                name=name, description=desc, price=price, sell_price=sell,
                rarity=rarity, category=cat, stock=-1, added_by=0,
                ap_cost=0, damage=0, heal=heal, armor=0,
                drink_effect=None, weapon_effect=None, loot_only=loot_only)
            item = await get_item(item_id)
            await _firelab_seed_extras(name, int(item['id']))
        out[name] = int(item['id'])

    # Рецепты праздника:
    #  • «Тыквенный пирог» — Тыква + Мука + Соль + Сахар + Яйца×2 (владелец
    #    поправит состав в менеджере рецептов);
    #  • «Обжигающая трость» — Сержантская трость + моток железной проволоки +
    #    Ручное пламенеющее устройство (состав из ТЗ, верстак).
    conn = await get_db()
    cur = await conn.execute(
        "SELECT id, ingredients FROM recipes WHERE name = ?", ("Тыквенный пирог",))
    row = await cur.fetchone()
    pie_ings = [("Тыква", 1), ("Мука", 1), ("Соль", 1),
                ("Сахар", 1), (config.FIRE_EGGS_NAME, 2)]
    if not row:
        await conn.execute(
            "INSERT INTO recipes (name, description, result_item_name, "
            "result_quantity, required_expansion, required_level, ingredients, "
            "ap_cost, production_time, rarity, is_available) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ("Тыквенный пирог",
             "Праздничный пирог из тыквы. Ингредиенты уточнит Хранитель.",
             config.FIRE_LAB_PIE_NAME, 2, "kitchen", 2,
             json.dumps(pie_ings, ensure_ascii=False), 3, 60, 3, 1))
    elif not row['ingredients'] or row['ingredients'] == "[]":
        await conn.execute(
            "UPDATE recipes SET ingredients = ? WHERE name = ?",
            (json.dumps(pie_ings, ensure_ascii=False), "Тыквенный пирог"))
    cur = await conn.execute(
        "SELECT id FROM recipes WHERE name = ?", ("Обжигающая трость",))
    if not await cur.fetchone():
        flame_device = getattr(config, "FIRE_FLAME_DEVICE_NAME",
                               "Ручное пламенеющее устройство")
        await conn.execute(
            "INSERT INTO recipes (name, description, result_item_name, "
            "result_quantity, required_expansion, required_level, ingredients, "
            "ap_cost, production_time, rarity, is_available) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ("Обжигающая трость",
             "Офицерский стержень чести, закованный в огонь: Сержантская "
             "трость + моток железной проволоки + ручное пламенеющее "
             "устройство. Слегка поджигает врага при ударе.",
             config.FIRE_CANE_NAME, 1, "workbench", 1,
             json.dumps([("Сержантская трость", 1),
                         (config.FIRE_WIRE_NAME, 1),
                         (flame_device, 1)],
                        ensure_ascii=False),
             8, 120, 4, 1))
    await conn.commit()
    # Праздничные предметы НЕ продаются в магазине (только лут/крафт/улов);
    # рынок/скупка работают как у обычного улова. Безопасно повторять.
    await conn.execute(
        "UPDATE items SET is_available = 0 WHERE name IN ("
        + ",".join("?" * len(out)) + ")", tuple(out.keys()))
    await conn.commit()
    return out


async def _firelab_seed_extras(name: str, item_id: int):
    """После создания предмета Фазы 4 — его спец-колонки (новое создание only),
    чтобы ручные правки админа не перетирались."""
    c = config
    if name == c.FIRE_PUMPKIN_SEED_NAME:
        await update_item(item_id, plant_name=c.FIRE_PUMPKIN_NAME)
    elif name == c.FIRE_LANTERN_NAME:
        # Лампа — мебель для личного жилья (expansion 'lantern', генератор Ф4б).
        await update_item(item_id, category="furniture")
    elif name == c.FIRE_CROWN_NAME:
        await update_item(item_id, equip_slot="head", armor=2,
                          heal_bonus_pct=int(c.FIRE_CROWN_HEAL_BONUS_PCT))
    elif name == c.FIRE_CLOAK_NAME:
        await update_item(item_id, equip_slot="body", armor=2,
                          dodge_bonus=int(c.FIRE_CLOAK_DODGE))
    elif name == c.FIRE_GLOVES_NAME:
        await update_item(item_id, equip_slot="hands", armor=2,
                          dodge_bonus=int(c.FIRE_GLOVES_DODGE))
    elif name == c.FIRE_KEYS_NAME:
        await update_item(item_id, damage=int(c.FIRE_KEYS_DMG),
                          weapon_effect="bleed",
                          weapon_effect_chance=int(c.FIRE_KEYS_BLEED_P),
                          weapon_effect_dmg=int(c.FIRE_KEYS_BLEED_DMG))
    elif name == c.FIRE_CANE_NAME:
        await update_item(item_id, damage=int(c.FIRE_CANE_DMG),
                          weapon_effect="burn",
                          weapon_effect_chance=int(c.FIRE_CANE_BURN_P),
                          weapon_effect_dmg=int(c.FIRE_CANE_BURN_DMG))


async def ensure_fishing_enemies():
    """Идемпотентно засевает врагов рыбалки (мутировавший моллюск) из MOLLUSK_SEED."""
    await ensure_mollusk_items()
    return await _ensure_source_enemies("fishing", MOLLUSK_SEED)


async def ensure_mollusk_items():
    """Идемпотентно создаёт предметы моллюска (из его добычи и готового блюда).

    Мясо и жемчужина — прямой лут с врага, поэтому строго loot-only: вне магазина,
    вне рынка игроков (market_ok=0), с пометкой loot_only. Жареное мясо — крафт,
    оно остаётся торгуемым.
    """
    conn = await get_db()
    added = False
    for (name, desc, price, sell, rare, category, heal) in MOLLUSK_ITEM_SEEDS:
        cursor = await conn.execute("SELECT id FROM items WHERE name = ?", (name,))
        row = await cursor.fetchone()
        if row is None:
            item_id = await add_item(name=name, description=desc, price=price, sell_price=sell,
                                     rarity=rare, category=category, stock=-1, added_by=0,
                                     ap_cost=0, damage=0, heal=heal,
                                     market_ok=0 if name in MOLLUSK_ENEMY_DROPS else 1)
            await update_item(item_id, is_available=0,
                              loot_only=1 if name in MOLLUSK_ENEMY_DROPS else 0)
            added = True
        else:
            is_drop = name in MOLLUSK_ENEMY_DROPS
            await conn.execute(
                "UPDATE items SET is_available = 0, heal = ?, market_ok = ?, loot_only = ? "
                "WHERE id = ?",
                (heal, 0 if is_drop else 1, 1 if is_drop else 0, row['id']))
    if added:
        await conn.commit()
    return added


async def _ensure_source_enemies(source: str, seed: dict) -> bool:
    """Создаёт строку врага по сиду, если её ещё нет (по ключу key)."""
    conn = await get_db()
    table = _enemy_source_table(source)
    cursor = await conn.execute(
        f"SELECT id FROM {table} WHERE key = ?", (seed.get("key"),))
    if await cursor.fetchone():
        return False
    values = {k: seed.get(k) for k in ENEMY_SEED_FIELDS}
    # v0.38.0: эффекты при ударе — JSON-массив на строке врага.
    if isinstance(values.get("on_hit_effects"), list):
        values["on_hit_effects"] = json.dumps(values["on_hit_effects"],
                                              ensure_ascii=False)
    # Дропы сида: имена предметов → item_id (часть может отсутствовать в БД).
    drops = []
    for item_name, chance in seed.get("loot") or ():
        item = await get_item_by_name(item_name)
        if item:
            drops.append({"item_id": item['id'], "chance": round(float(chance) / 100, 4), "qty": 1})
    cols = list(ENEMY_SEED_FIELDS) + ["drops"]
    vals = [values[k] for k in ENEMY_SEED_FIELDS] + [json.dumps(drops, ensure_ascii=False)]
    await conn.execute(
        f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({','.join(['?'] * len(cols))})",
        vals)
    await conn.commit()
    return True


async def get_source_enemies(source: str, spot: str = None, enabled_only: bool = False):
    """Враги источника (лес/рыбалка) для игрового кода и админ-редактора."""
    conn = await get_db()
    table = _enemy_source_table(source)
    sql = f"SELECT * FROM {table} WHERE 1=1"
    params = []
    if spot is not None:
        sql += " AND spot = ?"
        params.append(spot)
    if enabled_only:
        sql += " AND enabled = 1"
    sql += " ORDER BY id"
    cursor = await conn.execute(sql, params)
    return await cursor.fetchall()


async def get_source_enemy(source: str, enemy_id: int):
    conn = await get_db()
    table = _enemy_source_table(source)
    cursor = await conn.execute(f"SELECT * FROM {table} WHERE id = ?", (enemy_id,))
    return await cursor.fetchone()


async def get_source_enemy_by_key(source: str, key: str, spot: str = None):
    """Враг по техническому ключу ('boar', 'mollusk') — используется игровым кодом."""
    conn = await get_db()
    table = _enemy_source_table(source)
    sql = f"SELECT * FROM {table} WHERE key = ?"
    params = [key]
    if spot is not None:
        sql += " AND spot = ?"
        params.append(spot)
    cursor = await conn.execute(sql, params)
    return await cursor.fetchone()


async def get_source_enemy_drops(source: str, enemy_id: int) -> list:
    """Дропы врага как список dict (формат как у dungeon_enemies)."""
    enemy = await get_source_enemy(source, enemy_id)
    if not enemy or not enemy.get('drops'):
        return []
    try:
        drops = json.loads(enemy['drops'])
    except (json.JSONDecodeError, TypeError):
        return []
    return drops if isinstance(drops, list) else []


async def set_source_enemy_drops(source: str, enemy_id: int, drops: list):
    conn = await get_db()
    table = _enemy_source_table(source)
    await conn.execute(
        f"UPDATE {table} SET drops = ?, admin_tuned = 1 WHERE id = ?",
        (json.dumps(drops, ensure_ascii=False), enemy_id))
    await conn.commit()


async def add_source_enemy_drop(source: str, enemy_id: int, item_id: int, chance: float, qty: int = 1):
    """Добавляет дроп врагу (item_id + шанс 0–1 + кол-во); тот же предмет — заменяется."""
    drops = await get_source_enemy_drops(source, enemy_id)
    entry = {"item_id": item_id, "chance": max(0.0, min(1.0, float(chance))), "qty": max(1, int(qty))}
    for d in drops:
        if d.get('item_id') == item_id:
            d.update(entry)
            await set_source_enemy_drops(source, enemy_id, drops)
            return
    drops.append(entry)
    await set_source_enemy_drops(source, enemy_id, drops)


async def remove_source_enemy_drop(source: str, enemy_id: int, index: int) -> bool:
    drops = await get_source_enemy_drops(source, enemy_id)
    if not 0 <= index < len(drops):
        return False
    del drops[index]
    await set_source_enemy_drops(source, enemy_id, drops)
    return True


def _parse_on_hit_effects(raw) -> list:
    """JSON-строка on_hit_effects → список dict (валидация kind — в onhit)."""
    if not raw:
        return []
    try:
        data = json.loads(raw)
    except (ValueError, TypeError):
        return []
    return data if isinstance(data, list) else []


async def get_source_enemy_on_hit_effects(source: str, enemy_id: int) -> list:
    """Эффекты при ударе врага-источника (лес/рыбалка/копь/лесозаготовка)."""
    enemy = await get_source_enemy(source, enemy_id)
    if not enemy:
        return []
    return _parse_on_hit_effects(enemy.get('on_hit_effects'))


async def set_source_enemy_on_hit_effects(source: str, enemy_id: int, effects: list):
    """Правит эффекты при ударе врага-источника; помечает admin_tuned=1."""
    conn = await get_db()
    table = _enemy_source_table(source)
    await conn.execute(
        f"UPDATE {table} SET on_hit_effects = ?, admin_tuned = 1 WHERE id = ?",
        (json.dumps(effects, ensure_ascii=False), enemy_id))
    await conn.commit()


async def get_enemy_on_hit_effects(enemy_id: int) -> list:
    """Эффекты при ударе врага подземелья (dungeon_enemies)."""
    enemy = await get_enemy(enemy_id)
    if not enemy:
        return []
    return _parse_on_hit_effects(enemy.get('on_hit_effects'))


async def set_enemy_on_hit_effects(enemy_id: int, effects: list):
    conn = await get_db()
    await conn.execute(
        "UPDATE dungeon_enemies SET on_hit_effects = ? WHERE id = ?",
        (json.dumps(effects, ensure_ascii=False), enemy_id))
    await conn.commit()


async def update_source_enemy(source: str, enemy_id: int, **fields) -> bool:
    """Правка врага через админ-бота; помечает admin_tuned=1."""
    conn = await get_db()
    table = _enemy_source_table(source)
    sets, vals = [], []
    for key, val in fields.items():
        if key not in SOURCE_ENEMY_FIELDS:
            continue
        sets.append(f"{key} = ?")
        vals.append(val)
    if not sets:
        return False
    sets.append("admin_tuned = 1")
    vals.append(enemy_id)
    await conn.execute(f"UPDATE {table} SET {', '.join(sets)} WHERE id = ?", vals)
    await conn.commit()
    return True


async def add_source_enemy(source: str, **fields) -> int:
    """Создаёт врага в источнике (админ-редактор). Возвращает id."""
    conn = await get_db()
    table = _enemy_source_table(source)
    cols, vals = [], []
    for key in ENEMY_SEED_FIELDS + ("drops", "enabled"):
        if key not in fields:
            continue
        val = fields[key]
        if key == "drops" and isinstance(val, list):
            val = json.dumps(val, ensure_ascii=False)
        if key == "on_hit_effects" and isinstance(val, list):
            val = json.dumps(val, ensure_ascii=False)
        cols.append(key)
        vals.append(val)
    cursor = await conn.execute(
        f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({','.join(['?'] * len(cols))})", vals)
    await conn.commit()
    return cursor.lastrowid


async def delete_source_enemy(source: str, enemy_id: int) -> bool:
    conn = await get_db()
    table = _enemy_source_table(source)
    cursor = await conn.execute(f"DELETE FROM {table} WHERE id = ?", (enemy_id,))
    await conn.commit()
    return cursor.rowcount > 0


async def get_fishing_spots() -> list:
    """Водоёмы с врагами рыбалки: список (spot, число врагов)."""
    conn = await get_db()
    cursor = await conn.execute("""
        SELECT spot, COUNT(*) AS c FROM fishing_enemies
        WHERE enabled = 1 GROUP BY spot ORDER BY spot
    """)
    return await cursor.fetchall()


def enemy_encounter_hit(chance: float, roll: float, attempts: int = 0, pity: int = 0) -> bool:
    """Встреча с врагом: шанс в процентах + бросок (0–100) + гарантия.

    attempts — число спокойных попыток подряд, pity — встреча гарантирована
    на pity-й попытке (0 = без гарантии, только шанс)."""
    if pity > 0 and attempts + 1 >= pity:
        return True
    return roll < float(chance)


def roll_enemy_drops(drops: list, rolls: list = None, loot_bonus_pct: float = 0) -> list:
    """Бросок дропов врага: возвращает список выпавших [{item_id, chance, qty}].

    Каждый дроп бросается НЕЗАВИСИМО (как в данжах), поэтому редкий предмет
    остаётся достижимым: мясо 70% и жемчужина 2% — разные броски.
    rolls — готовые значения бросков (для тестов), иначе random.random().
    Пустой список = выпало несколько предметов; [] = ничего не выпало.
    loot_bonus_pct — бонус к шансу дропа (например, «Зверь Севера»): шанс
    каждого дропа умножается на (1 + pct/100), не выше 1.0.
    """
    picked = []
    for i, d in enumerate(drops or ()):
        if not isinstance(d, dict):
            continue
        roll = rolls[i] if rolls is not None and i < len(rolls) else random.random()
        chance = float(d.get('chance') or 0)
        if loot_bonus_pct and chance > 0:
            chance = min(1.0, chance * (1 + loot_bonus_pct / 100.0))
        if roll < chance:
            picked.append(d)
    return picked


# ─── Лес: счётчик попыток с момента последней встречи кабана ───

async def get_forest_boar_attempts(user_id: int) -> int:
    """Число попыток сбора грибов с последней встречи кабана (для гарантии 1/12)."""
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT forest_attempts_since_boar FROM users WHERE user_id = ?", (user_id,))
    row = await cursor.fetchone()
    return int(row['forest_attempts_since_boar']) if row and row['forest_attempts_since_boar'] else 0


async def set_forest_boar_attempts(user_id: int, attempts: int):
    conn = await get_db()
    await conn.execute(
        "UPDATE users SET forest_attempts_since_boar = ? WHERE user_id = ?",
        (max(0, int(attempts)), user_id)
    )
    await conn.commit()


async def reset_forest_boar_counter(user_id: int):
    """Сброс счётчика после встречи кабана (начало боя)."""
    await set_forest_boar_attempts(user_id, 0)


# ─── Лес: счётчик попыток с момента последней встречи волка (гарантия 1/24) ───

async def get_forest_wolf_attempts(user_id: int) -> int:
    """Число поисков грибов с последней встречи волка (для гарантии 1/24)."""
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT forest_attempts_since_wolf FROM users WHERE user_id = ?", (user_id,))
    row = await cursor.fetchone()
    return int(row['forest_attempts_since_wolf']) if row and row['forest_attempts_since_wolf'] else 0


async def set_forest_wolf_attempts(user_id: int, attempts: int):
    conn = await get_db()
    await conn.execute(
        "UPDATE users SET forest_attempts_since_wolf = ? WHERE user_id = ?",
        (max(0, int(attempts)), user_id)
    )
    await conn.commit()


async def reset_forest_wolf_counter(user_id: int):
    """Сброс счётчика после встречи волка (начало боя)."""
    await set_forest_wolf_attempts(user_id, 0)


# ─── Железная копи: счётчик попыток с момента последней встречи мыши (1/12) ───

async def get_mine_bat_attempts(user_id: int) -> int:
    """Число попыток добычи руды с последней встречи Летучей мыши (гарантия 1/12)."""
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT mine_attempts_since_bat FROM users WHERE user_id = ?", (user_id,))
    row = await cursor.fetchone()
    return int(row['mine_attempts_since_bat']) if row and row['mine_attempts_since_bat'] else 0


async def set_mine_bat_attempts(user_id: int, attempts: int):
    conn = await get_db()
    await conn.execute(
        "UPDATE users SET mine_attempts_since_bat = ? WHERE user_id = ?",
        (max(0, int(attempts)), user_id)
    )
    await conn.commit()


async def reset_mine_bat_counter(user_id: int):
    """Сброс счётчика после встречи мыши (начало боя)."""
    await set_mine_bat_attempts(user_id, 0)


async def get_logging_snake_attempts(user_id: int) -> int:
    """Число попыток рубки с последней встречи Змеи (гарантия раз в N)."""
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT logging_attempts_since_snake FROM users WHERE user_id = ?", (user_id,))
    row = await cursor.fetchone()
    return int(row['logging_attempts_since_snake']) if row and row['logging_attempts_since_snake'] else 0


async def set_logging_snake_attempts(user_id: int, attempts: int):
    conn = await get_db()
    await conn.execute(
        "UPDATE users SET logging_attempts_since_snake = ? WHERE user_id = ?",
        (max(0, int(attempts)), user_id)
    )
    await conn.commit()


async def reset_logging_snake_counter(user_id: int):
    """Сброс счётчика после встречи Змеи (начало боя)."""
    await set_logging_snake_attempts(user_id, 0)


async def get_logging_owl_attempts(user_id: int) -> int:
    """Число попыток рубки с последней встречи Неясыти (гарантия раз в N)."""
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT logging_attempts_since_owl FROM users WHERE user_id = ?", (user_id,))
    row = await cursor.fetchone()
    return int(row['logging_attempts_since_owl']) if row and row['logging_attempts_since_owl'] else 0


async def set_logging_owl_attempts(user_id: int, attempts: int):
    conn = await get_db()
    await conn.execute(
        "UPDATE users SET logging_attempts_since_owl = ? WHERE user_id = ?",
        (max(0, int(attempts)), user_id)
    )
    await conn.commit()


async def reset_logging_owl_counter(user_id: int):
    """Сброс счётчика после встречи Неясыти (начало боя)."""
    await set_logging_owl_attempts(user_id, 0)


async def remove_ap_or_floor(user_id: int, amount: int) -> int:
    """Списывает ОД, но не ниже нуля (для штрафа за проигрыш кабану).

    Возвращает фактически списанное количество ОД."""
    amount = max(0, int(amount))
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT ap FROM users WHERE user_id = ?", (user_id,))
    row = await cursor.fetchone()
    if not row:
        return 0
    had = int(row['ap'] or 0)
    removed = min(had, amount)
    await conn.execute(
        "UPDATE users SET ap = MAX(ap - ?, 0) WHERE user_id = ?", (amount, user_id))
    await conn.commit()
    return removed


# ──────────────── Рынок: слоты продажи + лицензия ────────────────

async def get_market_slots_info(user_id: int) -> dict:
    """Информация о слотах продажи: total, active_count, license_active, license_expires."""
    from config import MARKET_BASE_SLOTS, MARKET_LICENSE_SLOTS
    from utils.helpers import MOSCOW_TZ
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT market_license_expires FROM users WHERE user_id = ?", (user_id,))
    row = await cursor.fetchone()
    now_str = datetime.now(MOSCOW_TZ).strftime("%Y-%m-%d %H:%M:%S")
    license_expires = row['market_license_expires'] if row and 'market_license_expires' in row.keys() else None
    license_active = False
    if license_expires:
        try:
            license_active = license_expires > now_str
        except TypeError:
            license_active = False
    total = MARKET_BASE_SLOTS + (MARKET_LICENSE_SLOTS if license_active else 0)
    total += await get_achievement_bonus(user_id, "trader", "market_slots")

    cursor = await conn.execute(
        "SELECT COUNT(*) as c FROM market_fish WHERE seller_id = ?", (user_id,))
    fish_count = (await cursor.fetchone())['c']
    cursor = await conn.execute(
        "SELECT COUNT(*) as c FROM market_items WHERE seller_id = ?", (user_id,))
    item_count = (await cursor.fetchone())['c']
    return {"total_slots": total, "active_count": fish_count + item_count,
            "license_active": license_active, "license_expires": license_expires}


async def count_user_market_offers(user_id: int) -> int:
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT COUNT(*) as c FROM market_fish WHERE seller_id = ?", (user_id,))
    fish_count = (await cursor.fetchone())['c']
    cursor = await conn.execute(
        "SELECT COUNT(*) as c FROM market_items WHERE seller_id = ?", (user_id,))
    item_count = (await cursor.fetchone())['c']
    return fish_count + item_count


async def activate_market_license(user_id: int):
    """Активировать торговую лицензию на 30 дней (или продлить)."""
    from config import MARKET_LICENSE_DAYS
    from utils.helpers import MOSCOW_TZ
    conn = await get_db()
    now = datetime.now(MOSCOW_TZ)
    expires = (now + timedelta(days=MARKET_LICENSE_DAYS)).strftime("%Y-%m-%d %H:%M:%S")
    cursor = await conn.execute(
        "SELECT market_license_expires FROM users WHERE user_id = ?", (user_id,))
    row = await cursor.fetchone()
    if row and 'market_license_expires' in row.keys() and row['market_license_expires']:
        try:
            old_exp = datetime.strptime(row['market_license_expires'], "%Y-%m-%d %H:%M:%S")
            if old_exp > now:
                expires = (old_exp + timedelta(days=MARKET_LICENSE_DAYS)).strftime("%Y-%m-%d %H:%M:%S")
        except (TypeError, ValueError):
            pass
    await conn.execute(
        "UPDATE users SET market_license_expires = ? WHERE user_id = ?", (expires, user_id))
    await conn.commit()


async def ensure_market_license_item():
    """Идемпотентно добавляет «Торговую лицензию» в магазин."""
    from config import MARKET_LICENSE_PRICE
    cursor = await (await get_db()).execute(
        "SELECT COUNT(*) as c FROM items WHERE name = ?", ("Торговая лицензия",))
    if (await cursor.fetchone())['c'] > 0:
        return False
    await add_item(
        name="Торговая лицензия",
        description="Даёт +2 слота для продажи на рыбном рынке на 30 дней. "
                    "Продлевается при повторной покупке.",
        price=MARKET_LICENSE_PRICE, sell_price=0, rarity=3,
        category="license", stock=-1, added_by=0, ap_cost=0, damage=0, heal=0,
    )
    return True


# ──────────────── Налог на недвижимость ────────────────

async def get_housing_tax_rate(housing_type: str) -> int:
    """Ставка налога (НМ/мес) по типу жилья."""
    from config import HOUSING_TAX
    return HOUSING_TAX.get(housing_type, 0)


async def is_housing_tax_paid(user_id: int) -> bool:
    """Оплачен ли налог за текущий месяц.

    tax_last_check == текущий месяц означает, что месяц уже обработан суточным
    прогоном или ручной оплатой. Но если денег не хватило, tax_unpaid_months
    увеличивается — значит налог именно оплачен не был.
    """
    from utils.helpers import MOSCOW_TZ
    h = await get_player_housing(user_id)
    current_month = datetime.now(MOSCOW_TZ).strftime("%Y-%m")
    return (h.get('tax_last_check') or '') == current_month and (h.get('tax_unpaid_months') or 0) == 0


async def pay_housing_tax(user_id: int) -> tuple:
    """Оплатить налог за текущий месяц. Возвращает (ok: bool, msg: str)."""
    from utils.helpers import MOSCOW_TZ
    h = await get_player_housing(user_id)
    ht = h['housing_type']
    rate = await get_housing_tax_rate(ht)
    if rate <= 0:
        return False, "🏠 Налог на муниципальное жильё не взимается."
    user = await get_user(user_id)
    if not user:
        return False, "❌ Пользователь не найден."
    now = datetime.now(MOSCOW_TZ)
    current_month = now.strftime("%Y-%m")
    last_check = h.get('tax_last_check')
    if last_check == current_month:
        return False, f"✅ Налог за {current_month} уже оплачен."
    if user['nordmarks'] < rate:
        need = rate - user['nordmarks']
        return False, (
            f"❌ Недостаточно! Нужно {rate} НМ, у тебя {user['nordmarks']} НМ "
            f"(не хватает {need})."
        )
    await remove_nordmarks(user_id, rate, "housing_tax", f"Оплата налога за жильё ({ht})")
    conn = await get_db()
    await conn.execute(
        "UPDATE player_housing SET tax_last_check = ?, tax_unpaid_months = 0 "
        "WHERE user_id = ?", (current_month, user_id))
    await conn.commit()
    return True, f"✅ Налог за {current_month} оплачен: {rate} НМ."


async def pay_housing_debt(user_id: int) -> tuple:
    """Погасить всю накопленную задолженность по налогу. Возвращает (ok: bool, msg: str)."""
    from utils.helpers import MOSCOW_TZ
    h = await get_player_housing(user_id)
    ht = h['housing_type']
    rate = await get_housing_tax_rate(ht)
    if rate <= 0:
        return False, "🏠 Налог на муниципальное жильё не взимается."
    unpaid = h.get('tax_unpaid_months') or 0
    if unpaid <= 0:
        return False, "✅ Задолженности по налогу нет."
    debt = unpaid * rate
    user = await get_user(user_id)
    if not user:
        return False, "❌ Пользователь не найден."
    if user['nordmarks'] < debt:
        need = debt - user['nordmarks']
        return False, (
            f"❌ Недостаточно! Нужно {debt} НМ для долга, у тебя {user['nordmarks']} НМ "
            f"(не хватает {need})."
        )
    await remove_nordmarks(user_id, debt, "housing_tax",
                           f"Погашение долга по налогу на жильё ({unpaid} мес.)")
    conn = await get_db()
    await conn.execute(
        "UPDATE player_housing SET tax_unpaid_months = 0 WHERE user_id = ?", (user_id,))
    await conn.commit()
    return True, f"✅ Задолженность погашена: {unpaid} мес. × {rate} НМ = {debt} НМ."


async def run_housing_tax():
    """Суточный прогон: списание налога, начисление просрочки, изъятие жилья.

    Возвращает список user_id, у кого изъято жильё.
    """
    from config import HOUSING_TAX
    from bot.handlers.housing import FURNITURE_BY_EXPANSION
    from utils.helpers import MOSCOW_TZ
    conn = await get_db()
    now = datetime.now(MOSCOW_TZ)
    current_month = now.strftime("%Y-%m")
    forfeited = []

    cursor = await conn.execute(
        "SELECT ph.user_id, ph.housing_type, ph.tax_last_check, ph.tax_unpaid_months "
        "FROM player_housing ph WHERE ph.housing_type != 'municipal'"
    )
    rows = await cursor.fetchall()
    for r in rows:
        uid = r['user_id']
        ht = r['housing_type']
        rate = HOUSING_TAX.get(ht, 0)
        if rate <= 0:
            continue
        last_check = r['tax_last_check']
        unpaid = r['tax_unpaid_months'] or 0
        if last_check == current_month:
            continue

        user = await get_user(uid)
        if user and user['nordmarks'] >= rate:
            await remove_nordmarks(uid, rate, "housing_tax",
                                   f"Ежемесячный налог за жильё ({ht})")
            unpaid = 0
        else:
            unpaid += 1

        await conn.execute(
            "UPDATE player_housing SET tax_last_check = ?, tax_unpaid_months = ? "
            "WHERE user_id = ?", (current_month, unpaid, uid))
        await conn.commit()

        if unpaid >= 3:
            slots = await get_housing_slots(uid)
            for i, s in slots.items():
                et, lvl = s.get("expansion_type"), s.get("expansion_level", 1)
                await set_housing_slot(uid, i, None)
                if s.get("embedded"):
                    continue
                fname = FURNITURE_BY_EXPANSION.get((et, lvl))
                if fname:
                    fi = await get_item_by_name(fname)
                    if fi:
                        await add_inventory_item(uid, fi["id"], 1)
            await set_player_housing(uid, "municipal")
            await conn.execute(
                "UPDATE player_housing SET tax_unpaid_months = 0 WHERE user_id = ?", (uid,))
            await conn.commit()
            await log_activity(uid, "housing_forfeit", "Жильё изъято за неуплату налога")
            forfeited.append(uid)

    return forfeited


# ============ СИД: ТЕСТОВЫЕ ТОВАРЫ ============

DEFAULT_ITEMS = [
    # (name, description, price, sell_price, rarity, category, stock, ap_cost, damage, heal)
    ("Энергетик", "Восстанавливает силы: даёт +AP при использовании.", 50, 25, 1, "consumable", 100, 50, 0, 0),
    ("Лётный шлем", "Защищает пилота в бою.", 120, 60, 2, "equipment", 10, 0, 0, 0, 4),
    ("Кислородная маска", "Для высотных полётов.", 90, 45, 1, "equipment", 10, 0, 0, 0, 2),
    ("Малая настойка здоровья", "Восстанавливает 20 HP. Применяется в бою подземелья.", 40, 20, 2, "consumable", 30, 0, 0, 20),
]


async def seed_default_items():
    """Заполняет магазин базовым набором товаров, если он пуст и не было своих товаров."""
    conn = await get_db()
    cursor = await conn.execute("SELECT COUNT(*) as c FROM items")
    row = await cursor.fetchone()
    if row['c'] > 0:
        return False

    for entry in DEFAULT_ITEMS:
        name, desc, price, sell_price, rarity, category, stock, ap_cost, damage, heal = entry[:10]
        armor = entry[10] if len(entry) > 10 else 0
        await add_item(
            name=name, description=desc, price=price, sell_price=sell_price,
            rarity=rarity, category=category, stock=stock, added_by=0, ap_cost=ap_cost,
            damage=damage, heal=heal, armor=armor,
        )
    # Куда надевается базовая броня (fresh-BD: миграция выше в init_db ещё не видела эти строки)
    await conn.execute("UPDATE items SET equip_slot = 'head' WHERE name = 'Лётный шлем' AND equip_slot IS NULL")
    await conn.execute("UPDATE items SET equip_slot = 'body' WHERE category = 'equipment' AND armor > 0 AND equip_slot IS NULL")
    await conn.commit()
    return True


# ============ ДАНЖ: ТЕСТОВЫЙ ДАНЖ ============

# Формат врага в конфиге (кортеж):
#   (name, hp, atk, reward, is_boss, drops, image, poison_chance, poison_dmg,
#    dodge, bleed_chance, bleed_dmg, frostbite_chance, description)
# Кровотечение: урон каждый ход, спадает через 3 хода. Обморожение: снижает
# лечение (×0.5), само проходит через 4 хода или сразу от напитка cure_frostbite.
DEFAULT_DUNGEON = {
    "name": "Крысиный Подвал",
    "description": "Тёмный подвал под штабом. Крысы мутировали и захватили его. "
                   "Ходят слухи, что в глубине подвала есть подземное водохранилище с невиданной рыбой.",
    "floors": [
        {
            # Этаж 1: 9 комнат + 10-я — «Крысиный капитан» (промежуточный босс).
            "rooms": 9,
            "enemies": [
                ("Крыса", 15, 3, 0, False, [{"item": "Хвост крысы", "chance": 0.15, "qty": 1}], "assets/img/enemies/rat.jpg", 0, 0, 7),
                ("Ядовитая крыса", 20, 5, 0, False, [{"item": "Хвост крысы", "chance": 0.25, "qty": 1}], "assets/img/enemies/poison_rat.jpg", 35, 5, 7),
                ("Кристальный паук", 18, 4, 0, False, [
                    {"item": "Паутина паука", "chance": 0.15, "qty": 1},
                    {"item": "Осколок кристалла", "chance": 0.05, "qty": 1},
                    {"item": "Лапка кристального паука", "chance": 0.05, "qty": 1},
                    {"item": "Лапка паука", "chance": 0.2, "qty": 1},
                ], "assets/img/enemies/crystal_spider.jpg", 0, 0, 12),
            ],
            "boss": ("Крысиный капитан", 45, 7, 10, True, [
                {"item": "Хвост крысы", "chance": 0.4, "qty": 2},
                {"item": "Паутина паука", "chance": 0.2, "qty": 1},
                {"item": "Осколок кристалла", "chance": 0.1, "qty": 1},
            ], None, 0, 0, 8, 0, 0, 0,
             "Старый главарь крысиной армады. Носит ржавый шлем от кастрюли и "
             "считает себя генералом: отдаёт команды, но подопечные его не слушают. "
             "Пока он жив — крысы будут лезть со всех сторон."),
        },
        {
            # Этаж 2: 8 комнат + 9-я — «Король крыс» (главный босс).
            "rooms": 8,
            "enemies": [
                ("Прислужник короля", 22, 5, 0, False, [
                    {"item": "Хвост крысы", "chance": 0.3, "qty": 1},
                    {"item": "Кусочек королевского сыра", "chance": 0.08, "qty": 1},
                ], None, 0, 0, 9, 25, 3, 0,
                 "Личный гонец Короля крыс. Крыса, которая научилась держать палку. "
                 "Плохо говорит, хорошо дерётся — и очень больно кусается."),
                ("Чумная крыса", 25, 6, 0, False, [
                    {"item": "Хвост крысы", "chance": 0.35, "qty": 1},
                    {"item": "Коготь чумной крысы", "chance": 0.1, "qty": 1},
                ], None, 20, 3, 8, 35, 4, 0,
                 "Носитель заразы. Укус оставляет рваные раны, которые долго кровоточат. "
                 "Если она прокусит броню — считай, ты уже истекаешь кровью."),
                ("Морозный паук", 26, 5, 0, False, [
                    {"item": "Паутина паука", "chance": 0.15, "qty": 1},
                    {"item": "Лапка паука", "chance": 0.2, "qty": 1},
                    {"item": "Сосулька-паутина", "chance": 0.05, "qty": 1},
                ], None, 15, 3, 10, 0, 0, 35,
                 "Мутировавший паук с ледяной жилы. Плетёт паутину из мороза: "
                 "затянет жертву — и та начинает мёрзнуть даже в летнем подвале."),
            ],
            "boss": ("Король крыс", 80, 9, 20, True, [
                {"item": "Хвост крысы", "chance": 0.5, "qty": 3},
                {"item": "Осколок кристалла", "chance": 0.3, "qty": 1},
                {"item": "Метка Короля крыс", "chance": 0.1, "qty": 1},
            ], "assets/img/enemies/rat_king.jpg", 0, 0, 12, 30, 5, 0,
             "Повелитель крыс и хозяин подвала. Набрал вес, но не потерял хватку. "
             "Один свист — и на защиту логова поднимается вся крысиная армада."),
        },
    ],
}


def _legacy_effects_json(poison_chance=0, poison_dmg=0, bleed_chance=0,
                         bleed_dmg=0, frostbite_chance=0) -> str:
    """Собирает JSON on_hit_effects из legacy-полей кортежа сида данжа."""
    effects = []
    if int(bleed_chance or 0) > 0:
        eff = {"kind": "bleed", "chance": int(bleed_chance)}
        if int(bleed_dmg or 0) > 0:
            eff["dmg"] = int(bleed_dmg)
        effects.append(eff)
    if int(poison_chance or 0) > 0:
        eff = {"kind": "poison", "chance": int(poison_chance)}
        if int(poison_dmg or 0) > 0:
            eff["dmg"] = int(poison_dmg)
        effects.append(eff)
    if int(frostbite_chance or 0) > 0:
        effects.append({
            "kind": "frostbite", "chance": int(frostbite_chance),
            "rounds": config.ON_HIT_EFFECTS["frostbite"].get("default_rounds", 4),
        })
    return json.dumps(effects, ensure_ascii=False)


def _enemy_to_fields(enemy):
    """Раскладывает кортеж врага DEFAULT_DUNGEON в словарь полей БД.

    Позиции: name, hp, atk, reward, is_boss, drops, image, poison_chance,
    poison_dmg, dodge, bleed_chance, bleed_dmg, frostbite_chance, description.
    """
    (name, hp, atk, reward, is_boss, drops) = enemy[:6]
    poison_chance = enemy[7] if len(enemy) > 7 else 0
    poison_dmg = enemy[8] if len(enemy) > 8 else 0
    bleed_chance = enemy[10] if len(enemy) > 10 else 0
    bleed_dmg = enemy[11] if len(enemy) > 11 else 0
    frostbite_chance = enemy[12] if len(enemy) > 12 else 0
    return {
        "name": name,
        "hp": hp,
        "attack": atk,
        "reward_nm": reward,
        "is_boss": int(is_boss),
        "drops": drops,
        "image": enemy[6] if len(enemy) > 6 else None,
        "poison_chance": poison_chance,
        "poison_dmg": poison_dmg,
        "dodge": enemy[9] if len(enemy) > 9 else 0,
        "bleed_chance": bleed_chance,
        "bleed_dmg": bleed_dmg,
        "frostbite_chance": frostbite_chance,
        "description": enemy[13] if len(enemy) > 13 else None,
        # v0.38.0: единая система эффектов при ударе — JSON из legacy-полей.
        "on_hit_effects": _legacy_effects_json(
            poison_chance, poison_dmg, bleed_chance, bleed_dmg, frostbite_chance),
    }


DUNGEON_ENEMY_INSERT_COLS = (
    "dungeon_id, floor, name, hp, attack, reward_nm, is_boss, drops, image, "
    "poison_chance, poison_dmg, dodge, bleed_chance, bleed_dmg, frostbite_chance, "
    "description, on_hit_effects"
)


async def seed_dungeon():
    conn = await get_db()
    cursor = await conn.execute("SELECT COUNT(*) as c FROM dungeons")
    row = await cursor.fetchone()
    if row['c'] > 0:
        return False

    rooms_map = ",".join(["?"] * len(DEFAULT_DUNGEON["floors"]))
    rooms_vals = [floor_data.get("rooms", 10) for floor_data in DEFAULT_DUNGEON["floors"]]
    cur = await conn.execute(
        "INSERT INTO dungeons (name, description, floors_count, rooms_per_floor, rooms_map) VALUES (?, ?, ?, ?, ?)",
        (DEFAULT_DUNGEON["name"], DEFAULT_DUNGEON["description"],
         len(DEFAULT_DUNGEON["floors"]), rooms_vals[0] if rooms_vals else 10,
         json.dumps(rooms_vals, ensure_ascii=False))
    )
    dungeon_id = cur.lastrowid

    for floor_idx, floor_data in enumerate(DEFAULT_DUNGEON["floors"], 1):
        for enemy in floor_data["enemies"]:
            f = _enemy_to_fields(enemy)
            await conn.execute(
                f"INSERT INTO dungeon_enemies ({DUNGEON_ENEMY_INSERT_COLS}) "
                f"VALUES ({','.join(['?'] * 17)})",
                (dungeon_id, floor_idx, f["name"], f["hp"], f["attack"], f["reward_nm"],
                 f["is_boss"], json.dumps(f["drops"], ensure_ascii=False), f["image"],
                 f["poison_chance"], f["poison_dmg"], f["dodge"],
                 f["bleed_chance"], f["bleed_dmg"], f["frostbite_chance"],
                 f["description"], f["on_hit_effects"])
            )
        boss = floor_data["boss"]
        bf = _enemy_to_fields(boss)
        await conn.execute(
            f"INSERT INTO dungeon_enemies ({DUNGEON_ENEMY_INSERT_COLS}) "
            f"VALUES ({','.join(['?'] * 17)})",
            (dungeon_id, floor_idx, bf["name"], bf["hp"], bf["attack"], bf["reward_nm"],
             bf["is_boss"], json.dumps(bf["drops"], ensure_ascii=False), bf["image"],
             bf["poison_chance"], bf["poison_dmg"], bf["dodge"],
             bf["bleed_chance"], bf["bleed_dmg"], bf["frostbite_chance"],
             bf["description"], bf["on_hit_effects"])
        )

    await conn.commit()
    return True


# ============ ДАНЖ: КУРС ВЫЖИВАНИЯ ДЛЯ ПИЛОТОВ (К.В.П.) ============

KVP_DUNGEON_NAME = "Курс Выживания для Пилотов (К.В.П.)"
KVP_BADGE_NAME = "Значок В.У.С.П."
# Эксклюзивная награда босса курса. Заменила «Офицерский стек» (⚔️2), который был
# его старой версией: та же роль в игре, но слабее и без эффекта. Единственный
# источник трости — босс К.В.П., один раз на аккаунт (см. kvp.py CANE_CHANCE).
KVP_CANE_NAME = "Сержантская трость"
KVP_MAX_COMPLETIONS = 4
KVP_OD_COST = 5  # стоимость прохождения препятствия (одиночное действие)

# Предметы, которые нельзя передать другому игроку. Трость КВП — личная награда за
# босса: её можно продать скупщику (sell_price), но нельзя ни отдать, ни выставить
# на рынок. Проверка идёт по названию, а не по флагу loot_only: лут (кабан, моллюск)
# игроками передаётся свободно.
UNTRANSFERABLE_ITEMS = frozenset({KVP_CANE_NAME})

# Враги курса: (name, hp, atk, reward, is_boss, drops, image, poison_chance, poison_dmg, dodge, description)
KVP_ENEMIES = [
    ("Ефрейтор", 15, 2, 0, False, [], None, 0, 0, 5,
     "Если Ефрейтор без оружия спотыкается о собственную нерасторопность, курс считается пройденным."),
    ("Старший сержант", 40, 5, 0, True, [], None, 0, 0, 10,
     "Командир курса. Самый страшный босс — способен отчитать так, что хочется покинуть часть."),
]


async def seed_kvp():
    """Создаёт тренировочный данж К.В.П. с врагами (Ефрейтор, Старший сержант), если его нет."""
    conn = await get_db()
    cursor = await conn.execute("SELECT id FROM dungeons WHERE name = ?", (KVP_DUNGEON_NAME,))
    existing = await cursor.fetchone()
    if existing:
        # Разовая миграция текста описания (не трогаем ручные правки админа).
        await conn.execute(
            "UPDATE dungeons SET description = ? WHERE id = ? AND description = ?",
            ("Курс выживания для пилотов. Набор испытаний для пилотов ВВС Нордхайма.",
             existing['id'],
             "Тренировочный полигон для пилотов: 8 комнат со случайными препятствиями и боссом.")
        )
        # Синхронизируем боевые характеристики врагов курса с кодом (HP/АТК/уклонение),
        # не трогая описания и картинки, которые мог править админ.
        # Врагов, которых правил админ через бота (admin_tuned=1), не перезаписываем.
        for (name, hp, atk, reward, is_boss, drops, image, pc, pd, dodge, desc) in KVP_ENEMIES:
            await conn.execute(
                "UPDATE dungeon_enemies SET hp = ?, attack = ?, dodge = ? "
                "WHERE dungeon_id = ? AND name = ? AND is_boss = ? AND admin_tuned = 0",
                (hp, atk, dodge, existing['id'], name, int(is_boss))
            )
        await conn.commit()
        return existing['id']

    cur = await conn.execute(
        "INSERT INTO dungeons (name, description, floors_count, rooms_per_floor, is_training) VALUES (?,?,?,?,?)",
        (KVP_DUNGEON_NAME,
         "Курс выживания для пилотов. Набор испытаний для пилотов ВВС Нордхайма.",
         1, 8, 1)
    )
    dungeon_id = cur.lastrowid

    for name, hp, atk, reward, is_boss, drops, image, poison_chance, poison_dmg, dodge, desc in KVP_ENEMIES:
        await conn.execute(
            "INSERT INTO dungeon_enemies (dungeon_id, floor, name, hp, attack, reward_nm, is_boss, drops, image, poison_chance, poison_dmg, dodge, description, on_hit_effects) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (dungeon_id, 1, name, hp, atk, reward, int(is_boss),
             json.dumps(drops, ensure_ascii=False), image, poison_chance, poison_dmg, dodge, desc,
             _legacy_effects_json(poison_chance, poison_dmg))
        )
    await conn.commit()
    return dungeon_id


async def get_kvp_dungeon():
    """Возвращает тренировочный данж К.В.П. или None."""
    dungeons = await get_all_dungeons(training=True)
    return dungeons[0] if dungeons else None


async def ensure_kvp_items():
    """Обеспечивает эксклюзивный предмет К.В.П. — «Сержантскую трость».

    Трость заменила «Офицерский стек» (v0.18.0): стек был её более слабой версией
    (⚔️2 без эффекта), и он же был прописан сидом — из-за чего предмет нельзя было
    вывести из игры, он воскресал при каждом старте. Теперь трость создаётся
    только если её ещё нет: параметры, выставленные админом (цена, остаток,
    эффект), не перетираются.

    Трость не продаётся в магазине (loot_only), единственный источник — босс
    курса, один раз на аккаунт (см. kvp.py CANE_CHANCE).
    """
    conn = await get_db()
    cursor = await conn.execute("SELECT id FROM items WHERE name = ?", (KVP_CANE_NAME,))
    if await cursor.fetchone():
        return
    await add_item(
        name=KVP_CANE_NAME,
        description=("Трость Старшего сержанта. Замахнётся — и противник на пару "
                     "ходов теряет бой."),
        price=200, sell_price=100, rarity=2, category="weapon",
        stock=-1, added_by=0, ap_cost=0,
        damage=3, heal=0, armor=0, drink_effect=None,
        weapon_effect="stun", loot_only=1,
    )


async def ensure_duel_items():
    """Товары Дома Дуэлей: дуэльные перчатки (отдельный слот) и клубная карта.

    Оба предмета продаются в обычном магазине с доступа с пилота второго класса.
    Перчатки — экипировка (слот 'duel', категория 'duel_gear', урон 7): работают
    только в дуэлях, в PvE не учитываются. Карта — членский билет клуба.
    Идемпотентно: если предмет уже есть, параметры админа не перетираются.
    """
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT id FROM items WHERE name = ?", (config.DUEL_GLOVES_NAME,))
    if not await cursor.fetchone():
        await add_item(
            name=config.DUEL_GLOVES_NAME,
            description=("Перчатки для дуэлей в Доме Дуэлей. Работают только в "
                         "поединках на арене, в других боях бесполезны."),
            price=config.DUEL_GLOVES_PRICE, sell_price=config.DUEL_GLOVES_SELL,
            rarity=3, category="duel_gear", stock=-1, added_by=0, ap_cost=0,
            damage=config.DUEL_GLOVES_DAMAGE, heal=0, armor=0,
            equip_slot="duel", required_status=config.DUEL_ACCESS_TAG,
        )
    cursor = await conn.execute(
        "SELECT id FROM items WHERE name = ?", (config.DUEL_CLUB_CARD_NAME,))
    if not await cursor.fetchone():
        await add_item(
            name=config.DUEL_CLUB_CARD_NAME,
            description=("Членский билет Дома Дуэлей. Даёт право вызывать "
                         "пилотов на арену и принимать вызовы."),
            price=config.DUEL_CLUB_CARD_PRICE, sell_price=config.DUEL_CLUB_CARD_SELL,
            rarity=2, category="duel_card", stock=-1, added_by=0, ap_cost=0,
            required_status=config.DUEL_ACCESS_TAG,
        )
    # v0.23.3: цены предметов снижены и порог доступа опущен до pilot2. Уже
    # созданные на проде строки правим только пока они на СТАРЫХ значениях —
    # ручные правки админа (иная цена/статус) не затираются.
    await conn.execute(
        "UPDATE items SET price = ?, sell_price = ? "
        "WHERE name = ? AND price = ? AND sell_price = ?",
        (config.DUEL_GLOVES_PRICE, config.DUEL_GLOVES_SELL,
         config.DUEL_GLOVES_NAME, 400, 200))
    await conn.execute(
        "UPDATE items SET price = ?, sell_price = ? "
        "WHERE name = ? AND price = ? AND sell_price = ?",
        (config.DUEL_CLUB_CARD_PRICE, config.DUEL_CLUB_CARD_SELL,
         config.DUEL_CLUB_CARD_NAME, 300, 150))
    await conn.execute(
        "UPDATE items SET required_status = ? "
        "WHERE required_status = 'pilot1' AND name IN (?, ?)",
        (config.DUEL_ACCESS_TAG, config.DUEL_GLOVES_NAME, config.DUEL_CLUB_CARD_NAME))
    await conn.commit()


async def cleanup_mojibake_duel_items() -> int:
    """Удаляет дубли товаров арены, появившиеся до v0.23.6 из-за битой кодировки
    config (UTF-8, прочитанный как cp1251 и сохранённый обратно как UTF-8).

    Такие строки невалидны и задваивают товары в магазине арены. Возвращает
    число убранных строк. Если у предмета есть владельцы — прячет его (is_available=0),
    иначе удаляет.
    """
    conn = await get_db()
    junk_names = []
    for name in (config.DUEL_GLOVES_NAME, config.DUEL_CLUB_CARD_NAME):
        try:
            junk_names.append(name.encode("utf-8").decode("cp1251"))
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass
    if not junk_names:
        return 0
    placeholders = ",".join("?" * len(junk_names))
    cursor = await conn.execute(
        f"SELECT id FROM items WHERE name IN ({placeholders})", tuple(junk_names))
    ids = [r['id'] for r in await cursor.fetchall()]
    if not ids:
        return 0
    removed = 0
    for item_id in ids:
        cursor = await conn.execute(
            "SELECT 1 FROM inventory WHERE item_id = ? LIMIT 1", (item_id,))
        if await cursor.fetchone():
            await conn.execute(
                "UPDATE items SET is_available = 0 WHERE id = ?", (item_id,))
        else:
            await conn.execute("DELETE FROM items WHERE id = ?", (item_id,))
        removed += 1
    await conn.commit()
    return removed


def _demojibake(text: str):
    """Восстанавливает строку, дважды перекодированную UTF-8 → cp1251 → UTF-8.

    Возвращает исправленный текст или None, если строка не является mojibake
    (или не восстанавливается). Надёжный признак: cp1251-байты строки снова
    читаются как UTF-8. Для корректного русского текста это почти никогда не
    проходит, поэтому ложных срабатываний практически нет.
    """
    if not text:
        return None
    try:
        fixed = text.encode("cp1251").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return None
    return fixed if fixed and fixed != text else None


async def _merge_item_refs(conn, bad_id: int, good_id: int):
    """Переносит все ссылки на предмет bad_id на предмет good_id (слияние дублей).

    Инвентарь сливается с суммированием количеств; остальные ссылки (снаряжение,
    дропы, рецепты, лоты, очереди) перепривязываются. Сама строка items удаляется
    вызывающим кодом.
    """
    # Инвентарь: у кого есть оба предмета — складываем количества.
    await conn.execute(
        "UPDATE inventory SET quantity = quantity + "
        "(SELECT b.quantity FROM inventory b WHERE b.user_id = inventory.user_id AND b.item_id = ?) "
        "WHERE item_id = ? AND EXISTS "
        "(SELECT 1 FROM inventory b WHERE b.user_id = inventory.user_id AND b.item_id = ?)",
        (bad_id, good_id, bad_id))
    await conn.execute(
        "DELETE FROM inventory WHERE item_id = ? AND EXISTS "
        "(SELECT 1 FROM inventory g WHERE g.user_id = inventory.user_id AND g.item_id = ?)",
        (bad_id, good_id))
    await conn.execute("UPDATE inventory SET item_id = ? WHERE item_id = ?", (good_id, bad_id))

    # Прочие однострочные ссылки на предмет.
    for table, col in (("player_dungeon_inventory", "item_id"),
                       ("dungeon_rewards", "item_id"),
                       ("dungeon_items", "item_id"),
                       ("resource_sources", "item_id"),
                       ("fish_catches", "item_id"),
                       ("market_items", "item_id"),
                       ("market_fish", "item_id"),
                       ("water_fish", "item_id"),
                       ("production_queue", "recipe_item_id"),
                       ("buildings", "production_item_id")):
        await conn.execute(f"UPDATE {table} SET {col} = ? WHERE {col} = ?", (good_id, bad_id))
    await conn.execute("UPDATE trades SET from_item_id = ? WHERE from_item_id = ?", (good_id, bad_id))
    await conn.execute("UPDATE trades SET to_item_id = ? WHERE to_item_id = ?", (good_id, bad_id))

    # Снаряжение игроков (JSON-слоты).
    cur = await conn.execute(
        "SELECT user_id, equipment FROM users WHERE equipment IS NOT NULL AND equipment != '{}'")
    for row in await cur.fetchall():
        try:
            eq = json.loads(row["equipment"])
        except (ValueError, TypeError):
            continue
        changed = False
        for slot, val in list(eq.items()):
            if val == bad_id:
                eq[slot] = good_id
                changed = True
        if changed:
            await conn.execute("UPDATE users SET equipment = ? WHERE user_id = ?",
                               (json.dumps(eq, ensure_ascii=False), row["user_id"]))

    # Дропы врагов (JSON-список с item_id).
    cur = await conn.execute(
        "SELECT id, drops FROM dungeon_enemies WHERE drops IS NOT NULL AND drops != '[]'")
    for row in await cur.fetchall():
        try:
            dlist = json.loads(row["drops"])
        except (ValueError, TypeError):
            continue
        if not isinstance(dlist, list):
            continue
        changed = False
        for d in dlist:
            if isinstance(d, dict) and d.get("item_id") is not None and int(d["item_id"]) == bad_id:
                d["item_id"] = good_id
                changed = True
        if changed:
            await conn.execute(
                "UPDATE dungeon_enemies SET drops = ?, admin_tuned = 1 WHERE id = ?",
                (json.dumps(dlist, ensure_ascii=False), row["id"]))

    # Ингредиенты рецептов (JSON-список).
    cur = await conn.execute(
        "SELECT id, ingredients FROM recipes WHERE ingredients IS NOT NULL AND ingredients != '[]'")
    for row in await cur.fetchall():
        try:
            ing = json.loads(row["ingredients"])
        except (ValueError, TypeError):
            continue
        if not isinstance(ing, list):
            continue
        changed = False
        for e in ing:
            if isinstance(e, dict) and e.get("item_id") is not None and int(e["item_id"]) == bad_id:
                e["item_id"] = good_id
                changed = True
        if changed:
            await conn.execute("UPDATE recipes SET ingredients = ? WHERE id = ?",
                               (json.dumps(ing, ensure_ascii=False), row["id"]))


async def repair_mojibake_entities() -> dict:
    """Чинит записи с битой кодировкой (UTF-8, прочитанный как cp1251).

    Причина: раньше config.py на короткое время был дважды перекодирован, и
    `ensure_*` засеяли предметы/награды с «крякозябрами» — появлялись дубли товаров
    (например, «Буклет туриста» и его битый двойник). Здесь:
      * если у битой записи есть корректный двойник по имени — переносим все ссылки
        на двойника и удаляем битую строку (слияние);
      * иначе — восстанавливаем имя/описание на месте.
    Идемпотентно. Возвращает отчёт по категориям.
    """
    conn = await get_db()
    report = {"items_merged": 0, "items_fixed": 0,
              "awards_merged": 0, "awards_fixed": 0}

    cur = await conn.execute("SELECT id, name, description FROM items")
    for row in await cur.fetchall():
        fixed = _demojibake(row["name"])
        if not fixed:
            continue
        cur2 = await conn.execute(
            "SELECT id FROM items WHERE name = ? AND id != ?", (fixed, row["id"]))
        twin = await cur2.fetchone()
        if twin:
            await _merge_item_refs(conn, row["id"], twin["id"])
            await conn.execute("DELETE FROM items WHERE id = ?", (row["id"],))
            report["items_merged"] += 1
        else:
            desc_fixed = _demojibake(row["description"]) or row["description"]
            await conn.execute(
                "UPDATE items SET name = ?, description = ? WHERE id = ?",
                (fixed, desc_fixed, row["id"]))
            report["items_fixed"] += 1

    cur = await conn.execute("SELECT id, name, description FROM awards")
    for row in await cur.fetchall():
        fixed = _demojibake(row["name"])
        if not fixed:
            continue
        cur2 = await conn.execute(
            "SELECT id FROM awards WHERE name = ? AND id != ?", (fixed, row["id"]))
        twin = await cur2.fetchone()
        if twin:
            await conn.execute(
                "UPDATE user_awards SET award_id = ? WHERE award_id = ?", (twin["id"], row["id"]))
            await conn.execute(
                "UPDATE award_monthly_paid SET award_id = ? WHERE award_id = ?",
                (twin["id"], row["id"]))
            await conn.execute("DELETE FROM awards WHERE id = ?", (row["id"],))
            report["awards_merged"] += 1
        else:
            desc_fixed = _demojibake(row["description"]) or row["description"]
            await conn.execute(
                "UPDATE awards SET name = ?, description = ? WHERE id = ?",
                (fixed, desc_fixed, row["id"]))
            report["awards_fixed"] += 1

    await conn.commit()
    return report


async def ensure_kvp_award():
    KVP_BADGE_DESCRIPTION = (
        "Выживание, уклонение, сопротивление и побег. Постоянный бонус: "
        "+2% урона и +3% уклонения в подземельях."
    )
    await create_award(
        name=KVP_BADGE_NAME,
        description=KVP_BADGE_DESCRIPTION,
        emoji="🎖️",
        created_by=None,
    )
    conn = await get_db()
    cursor = await conn.execute("SELECT id FROM awards WHERE name = ?", (KVP_BADGE_NAME,))
    row = await cursor.fetchone()
    if row:
        await conn.execute(
            "UPDATE awards SET description = ? WHERE id = ? AND description != ?",
            (KVP_BADGE_DESCRIPTION, row['id'], KVP_BADGE_DESCRIPTION)
        )
        # Дефолтные бонусы нашивки (2% атаки, 3% уклонения) — только пока не настроены
        # (колонки имеют DEFAULT 0, поэтому «не настроен» = 0/0).
        await conn.execute(
            "UPDATE awards SET bonus_attack = ?, bonus_dodge = ? "
            "WHERE id = ? AND bonus_attack = 0 AND bonus_dodge = 0",
            (2, 3, row['id'])
        )
        await conn.commit()


# ── Буклет туриста ─────────────────────────────────────────────────────────────

async def get_booklet_item():
    """Предмет «Буклет туриста» из каталога (None, если ещё не создан)."""
    return await get_item_by_name(config.TOURIST_BOOKLET_NAME)


async def ensure_tourist_booklet():
    """Создаёт предмет «Буклет туриста» и награду «Опытный турист», если их нет.

    Как и ensure_kvp_items: предмет создаётся только при отсутствии, ручные правки
    админа (цена, описание) не перетираются. Буклет в сувенирной категории — виден
    и туристам, и гражданам; продажа отключена (sell_price = 0).
    """
    item = await get_booklet_item()
    if not item:
        await add_item(
            name=config.TOURIST_BOOKLET_NAME,
            description=config.TOURIST_BOOKLET_DESCRIPTION,
            price=config.TOURIST_BOOKLET_PRICE,
            sell_price=config.TOURIST_BOOKLET_SELL_PRICE,
            rarity=1, category="souvenirs",
            stock=-1, added_by=0, ap_cost=0,
            damage=0, heal=0, armor=0, drink_effect=None,
            weapon_effect=None, loot_only=0,
        )
    await create_award(
        name=config.TOURIST_BOOKLET_AWARD,
        description=config.TOURIST_BOOKLET_AWARD_DESCRIPTION,
        emoji=config.TOURIST_BOOKLET_AWARD_EMOJI,
        created_by=None,
        reward_nm=config.TOURIST_BOOKLET_REWARD_NM,
    )
    # У уже существующей награды (созданной до появления премий) проставляем
    # разовую премию один раз — при условии, что её ещё не настраивал админ
    # (0 = не настроено). Дальше премией рулит редактор наград.
    conn = await get_db()
    await conn.execute(
        "UPDATE awards SET reward_nm = ? WHERE name = ? AND reward_nm = 0",
        (config.TOURIST_BOOKLET_REWARD_NM, config.TOURIST_BOOKLET_AWARD)
    )
    await conn.commit()


async def has_booklet(user_id: int) -> bool:
    """Есть ли у игрока «Буклет туриста» в инвентаре."""
    item = await get_booklet_item()
    if not item:
        return False
    inv = await get_inventory_item(user_id, item['id'])
    return bool(inv and inv['quantity'] > 0)


async def mark_booklet_visit(user_id: int, location_key: str):
    """Отмечает локацию в буклете, если ключ входит в список буклета и буклет есть.

    Пишется только НОВОЕ посещение (после покупки) — ретроспективы нет: без буклета
    в инвентаре записи не создаются.
    """
    if location_key not in config.TOURIST_BOOKLET_LOCATIONS:
        return
    if not await has_booklet(user_id):
        return
    conn = await get_db()
    await conn.execute(
        "INSERT OR IGNORE INTO booklet_visits (user_id, location_key, visited_at) "
        "VALUES (?, ?, datetime('now'))",
        (user_id, location_key)
    )
    await conn.commit()


async def get_booklet_visits(user_id: int) -> set:
    """Набор посещённых ключей локаций буклета."""
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT location_key FROM booklet_visits WHERE user_id = ?", (user_id,))
    return {row['location_key'] for row in await cursor.fetchall()}


async def is_booklet_claimed(user_id: int) -> bool:
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT 1 FROM booklet_claims WHERE user_id = ?", (user_id,))
    return bool(await cursor.fetchone())


async def get_locations_by_keys(keys) -> dict:
    """{location_key: name} для переданных ключей (порядок key_dict Preserves)."""
    if not keys:
        return {}
    conn = await get_db()
    placeholders = ",".join("?" * len(list(keys)))
    cursor = await conn.execute(
        f"SELECT key, name FROM locations WHERE key IN ({placeholders})",
        tuple(keys))
    return {row['key']: row['name'] for row in await cursor.fetchall()}


async def claim_booklet_reward(user_id: int) -> tuple:
    """Выдача награды буклета: значок + 20 НМ, один раз на аккаунт.

    Возвращает (ok, текст). Проверяются все 9 локаций и отсутствие повторной
    выдачи; предмет не списывается — буклет остаётся как сувенир.
    """
    if await is_booklet_claimed(user_id):
        return False, "Награда за буклет уже получена."

    visits = await get_booklet_visits(user_id)
    needed = set(config.TOURIST_BOOKLET_LOCATIONS)
    missing = needed - visits
    if missing:
        names = await get_locations_by_keys(missing)
        labels = [names[k] or k for k in config.TOURIST_BOOKLET_LOCATIONS if k in missing]
        return False, (
            f"Посетил не все локации: не хватает — {', '.join(labels)}.\n"
            f"Собери {len(config.TOURIST_BOOKLET_LOCATIONS)}/{len(config.TOURIST_BOOKLET_LOCATIONS)}."
        )

    conn = await get_db()
    cursor = await conn.execute(
        "SELECT id FROM awards WHERE name = ?", (config.TOURIST_BOOKLET_AWARD,))
    award = await cursor.fetchone()
    if not award:
        return False, "Награда ещё не настроена — сообщи командованию."

    # Отмечаем получение и выдаём значок через grant_award: единственную точку
    # выдачи наград. Разовая премия (reward_nm) платится из казны, а не
    # создаётся из воздуха. При неудаче откатываем отметку — игрок повторит.
    try:
        await conn.execute(
            "INSERT INTO booklet_claims (user_id, claimed_at) VALUES (?, datetime('now'))",
            (user_id,))
        await conn.commit()
    except Exception:
        await conn.rollback()
        return False, "Не удалось получить награду — попробуй ещё раз."

    granted, _ = await grant_award(
        user_id, award['id'], None,
        comment=f"Буклет туриста: все {len(config.TOURIST_BOOKLET_LOCATIONS)} локаций")
    if not granted:
        await conn.execute("DELETE FROM booklet_claims WHERE user_id = ?", (user_id,))
        await conn.commit()
        return False, "Не удалось получить награду — попробуй ещё раз."

    await log_activity(
        user_id, "booklet_claim",
        f"Буклет туриста: награда «{config.TOURIST_BOOKLET_AWARD}», "
        f"+{config.TOURIST_BOOKLET_REWARD_NM} НМ из казны"
    )
    return True, (
        f"🧭 {config.TOURIST_BOOKLET_AWARD_EMOJI} «{config.TOURIST_BOOKLET_AWARD}» получен!\n"
        f"Все локации Нордхайма отмечены, командование не забудет такого гостя.\n\n"
        f"💰 Награда: +{config.TOURIST_BOOKLET_REWARD_NM} НМ (из казны)"
    )


async def ensure_kvp_user(user_id: int):
    """Гарантирует наличие строки прогресса К.В.П. для игрока."""
    conn = await get_db()
    await conn.execute(
        "INSERT OR IGNORE INTO player_kvp (user_id) VALUES (?)", (user_id,))
    await conn.commit()


async def get_kvp_progress(user_id: int):
    """Прогресс К.В.П.: {'completions', 'badge_awarded', 'stick_dropped'} или нулевые значения."""
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT completions, badge_awarded, stick_dropped FROM player_kvp WHERE user_id = ?",
        (user_id,)
    )
    row = await cursor.fetchone()
    if not row:
        return {"completions": 0, "badge_awarded": 0, "stick_dropped": 0}
    return dict(row)


async def increment_kvp_completions(user_id: int):
    await ensure_kvp_user(user_id)
    conn = await get_db()
    await conn.execute(
        "UPDATE player_kvp SET completions = completions + 1 WHERE user_id = ?", (user_id,))
    await conn.commit()


async def mark_kvp_badge(user_id: int):
    await ensure_kvp_user(user_id)
    conn = await get_db()
    await conn.execute(
        "UPDATE player_kvp SET badge_awarded = 1 WHERE user_id = ?", (user_id,))
    await conn.commit()


async def mark_kvp_stick(user_id: int):
    await ensure_kvp_user(user_id)
    conn = await get_db()
    await conn.execute(
        "UPDATE player_kvp SET stick_dropped = 1 WHERE user_id = ?", (user_id,))
    await conn.commit()


async def user_has_award_name(user_id: int, award_name: str) -> bool:
    """Есть ли у игрока награда с данным названием (постоянный бонус, экипировка не нужна)."""
    conn = await get_db()
    cursor = await conn.execute("""
        SELECT 1 FROM user_awards ua
        JOIN awards a ON ua.award_id = a.id
        WHERE ua.user_id = ? AND a.name = ?
        LIMIT 1
    """, (user_id, award_name))
    return (await cursor.fetchone()) is not None


async def get_all_dungeons(training=None):
    """Все активные подземелья. training=None — все, True — только тренировочные, False — только боевые."""
    conn = await get_db()
    q = "SELECT * FROM dungeons WHERE is_active = 1"
    if training is not None:
        q += " AND is_training = ?"
        cursor = await conn.execute(q, (int(training),))
    else:
        cursor = await conn.execute(q)
    return await cursor.fetchall()


async def get_dungeon(dungeon_id: int):
    conn = await get_db()
    cursor = await conn.execute("SELECT * FROM dungeons WHERE id = ?", (dungeon_id,))
    return await cursor.fetchone()


async def get_dungeon_rooms_map(dungeon_id: int) -> list:
    """Число обычных комнат до босса по этажам данжа (JSON-массив, e.g. [9, 8]).

    Босс этажа встречается, когда room_number >= rooms_map[floor-1].
    Для старых данжей без rooms_map — фолбэк на rooms_per_floor.
    """
    dng = await get_dungeon(dungeon_id)
    if not dng:
        return []
    raw = dng.get('rooms_map') if 'rooms_map' in (dng.keys() if hasattr(dng, 'keys') else []) else None
    if not raw:
        return [int(dng['rooms_per_floor'] or 10)]
    try:
        rooms = json.loads(raw)
        if not isinstance(rooms, list) or not rooms:
            return [int(dng['rooms_per_floor'] or 10)]
        return [int(r) for r in rooms]
    except (ValueError, TypeError):
        return [int(dng['rooms_per_floor'] or 10)]


async def get_floor_enemies(dungeon_id: int, floor: int):
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT * FROM dungeon_enemies WHERE dungeon_id = ? AND floor = ?",
        (dungeon_id, floor)
    )
    return await cursor.fetchall()


async def get_enemy(enemy_id: int):
    conn = await get_db()
    cursor = await conn.execute("SELECT * FROM dungeon_enemies WHERE id = ?", (enemy_id,))
    return await cursor.fetchone()


async def get_dungeon_enemies(dungeon_id: int):
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT * FROM dungeon_enemies WHERE dungeon_id = ? ORDER BY is_boss, floor, id",
        (dungeon_id,)
    )
    return await cursor.fetchall()


# Поля врага, которые админ правит через бота.
ENEMY_EDITABLE_FIELDS = ("hp", "attack", "dodge", "armor", "poison_chance",
                         "poison_dmg", "reward_nm", "drops",
                         "bleed_chance", "bleed_dmg", "frostbite_chance",
                         "description", "image")


async def update_enemy_fields(enemy_id: int, **fields):
    """Правит характеристики врага через админ-бота; помечает admin_tuned=1,
    чтобы стартовая синхронизация (ensure_dungeon_enemy_drops / seed_kvp)
    больше не перезаписывала эти значения."""
    conn = await get_db()
    sets, vals = [], []
    for key, val in fields.items():
        if key not in ENEMY_EDITABLE_FIELDS:
            continue
        if key == "drops" and isinstance(val, list):
            val = json.dumps(val, ensure_ascii=False)
        sets.append(f"{key} = ?")
        vals.append(val)
    if not sets:
        return False
    sets.append("admin_tuned = 1")
    vals.append(enemy_id)
    await conn.execute(
        f"UPDATE dungeon_enemies SET {', '.join(sets)} WHERE id = ?", vals)
    await conn.commit()
    return True


async def get_enemy_drops(enemy_id: int) -> list:
    """Дропы врага как список dict; пустой список, если дропов нет."""
    enemy = await get_enemy(enemy_id)
    if not enemy or not enemy.get('drops'):
        return []
    try:
        drops = json.loads(enemy['drops'])
    except (json.JSONDecodeError, TypeError):
        return []
    return drops if isinstance(drops, list) else []


async def set_enemy_drops(enemy_id: int, drops: list):
    """Сохраняет список дропов врага (JSON) и помечает admin_tuned=1."""
    conn = await get_db()
    await conn.execute(
        "UPDATE dungeon_enemies SET drops = ?, admin_tuned = 1 WHERE id = ?",
        (json.dumps(drops, ensure_ascii=False), enemy_id))
    await conn.commit()


async def add_enemy_drop(enemy_id: int, item_id: int, chance: float, qty: int):
    """Добавляет дроп: item_id + шанс (0–1) + кол-во. Существующий item_id — заменяется."""
    drops = await get_enemy_drops(enemy_id)
    entry = {"item_id": item_id, "chance": chance, "qty": max(1, int(qty))}
    for d in drops:
        if d.get('item_id') == item_id:
            d.update(entry)
            await set_enemy_drops(enemy_id, drops)
            return
    drops.append(entry)
    await set_enemy_drops(enemy_id, drops)


async def remove_enemy_drop(enemy_id: int, index: int) -> bool:
    """Удаляет дроп по индексу. True, если удалено."""
    drops = await get_enemy_drops(enemy_id)
    if not 0 <= index < len(drops):
        return False
    del drops[index]
    await set_enemy_drops(enemy_id, drops)
    return True


async def start_dungeon_run(user_id: int, dungeon_id: int):
    conn = await get_db()
    # Удаляем старые забеги игрока вместе со связанным инвентарём,
    # иначе INSERT OR REPLACE упадёт с FOREIGN KEY constraint
    cursor = await conn.execute(
        "SELECT id FROM player_dungeon_run WHERE user_id = ?",
        (user_id,)
    )
    old_runs = await cursor.fetchall()
    for run in old_runs:
        await conn.execute(
            "DELETE FROM player_dungeon_inventory WHERE run_id = ?",
            (run['id'],)
        )
        await conn.execute(
            "DELETE FROM player_dungeon_run WHERE id = ?",
            (run['id'],)
        )

    bonus = await get_award_bonus(user_id)

    await conn.execute(
        "INSERT INTO player_dungeon_run (user_id, dungeon_id, floor, room_number, hp, hp_max, is_active, started_at) VALUES (?,?,?,?,?,?,?,?)",
        (user_id, dungeon_id, 1, 0, 100 + bonus['hp'], 100 + bonus['hp'], 1, int(time.time()))
    )
    await conn.commit()


def _parse_sqlite_ts(value) -> float | None:
    """SQLite CURRENT_TIMESTAMP = 'YYYY-MM-DD HH:MM:SS' в UTC."""
    from datetime import datetime, timezone
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return datetime.strptime(value, "%Y-%m-%d %H:%M:%S").replace(
                tzinfo=timezone.utc
            ).timestamp()
        except Exception:
            try:
                return datetime.fromisoformat(value).replace(
                    tzinfo=timezone.utc
                ).timestamp()
            except Exception:
                return None
    return None


async def get_active_run(user_id: int):
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT * FROM player_dungeon_run WHERE user_id = ? AND is_active = 1",
        (user_id,)
    )
    run = await cursor.fetchone()
    if run is None:
        return None
    # Принудительный сброс протухших забегов: если пилот застрял (или просто
    # вышел из подземелья в город и забыл про забег) — через час забег сам
    # завершается и больше не блокирует рыбалку и другие зоны.
    started_ts = _parse_sqlite_ts(run.get('started_at'))
    if started_ts is not None and time.time() - started_ts > DUNGEON_RUN_STALE_SEC:
        await finalize_run_for(user_id, run['id'], "dungeon_timeout",
                               "Забег сброшен: вышло время пребывания в подземелье",
                               loot_nm=run.get('loot_nm') or 0)
        return None
    return run


async def finalize_run_for(user_id: int, run_id: int, reason: str, note: str,
                           loot_nm: int = 0):
    """Завершает забег: переносит собранный лут и НМ в инвентарь и делает забег неактивным."""
    items = await transfer_run_items_to_inventory(user_id, run_id)
    if loot_nm > 0:
        await add_nordmarks(user_id, loot_nm, reason, "Вынесено из подземелья")
    await end_run(run_id, 0)
    try:
        await log_activity(user_id, reason, note)
    except Exception:
        pass
    return items, loot_nm


async def update_run_hp(run_id: int, hp: int):
    conn = await get_db()
    await conn.execute("UPDATE player_dungeon_run SET hp = ? WHERE id = ?", (hp, run_id))
    await conn.commit()


async def advance_room(run_id: int):
    conn = await get_db()
    await conn.execute(
        "UPDATE player_dungeon_run SET room_number = room_number + 1 WHERE id = ?",
        (run_id,)
    )
    await conn.commit()


async def advance_floor(run_id: int, floor: int):
    """Переводит забег на следующий этаж: сбрасывает комнаты на 0."""
    conn = await get_db()
    await conn.execute(
        "UPDATE player_dungeon_run SET floor = ?, room_number = 0 WHERE id = ?",
        (floor, run_id)
    )
    await conn.commit()


async def end_run(run_id: int, is_active: int = 0):
    conn = await get_db()
    await conn.execute("UPDATE player_dungeon_run SET is_active = ? WHERE id = ?", (is_active, run_id))
    await conn.commit()


async def add_run_item(run_id: int, item_id: int, quantity: int = 1):
    conn = await get_db()
    await conn.execute("""
        INSERT INTO player_dungeon_inventory (run_id, item_id, quantity)
        VALUES (?, ?, ?)
        ON CONFLICT(run_id, item_id) DO UPDATE SET quantity = quantity + excluded.quantity
    """, (run_id, item_id, quantity))
    await conn.commit()


async def add_run_nordmarks(run_id: int, amount: int):
    """Копит найденные в забеге нордмарки (начисляются при выходе из подземелья)."""
    if amount <= 0:
        return
    conn = await get_db()
    await conn.execute(
        "UPDATE player_dungeon_run SET loot_nm = loot_nm + ? WHERE id = ?",
        (amount, run_id)
    )
    await conn.commit()


async def get_run_items(run_id: int):
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT i.name, pdi.quantity FROM player_dungeon_inventory pdi JOIN items i ON pdi.item_id = i.id WHERE pdi.run_id = ?",
        (run_id,)
    )
    return await cursor.fetchall()


async def clear_run_items(run_id: int):
    conn = await get_db()
    await conn.execute("DELETE FROM player_dungeon_inventory WHERE run_id = ?", (run_id,))


async def transfer_run_items_to_inventory(user_id: int, run_id: int) -> list:
    """Переносит найденный в забеге лут (player_dungeon_inventory) в реальный
    инвентарь игрока и чистит временный. Возвращает [(название, кол-во)]."""
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT item_id, quantity FROM player_dungeon_inventory WHERE run_id = ?",
        (run_id,)
    )
    rows = await cursor.fetchall()
    transferred = []
    for r in rows:
        await add_inventory_item(user_id, r['item_id'], r['quantity'])
        cur2 = await conn.execute("SELECT name FROM items WHERE id = ?", (r['item_id'],))
        it = await cur2.fetchone()
        name = it['name'] if it else f"#{r['item_id']}"
        transferred.append((name, r['quantity']))
    await conn.execute("DELETE FROM player_dungeon_inventory WHERE run_id = ?", (run_id,))
    await conn.commit()
    return transferred
    await conn.commit()


async def get_player_weapon_damage(user_id: int) -> int:
    """Урон активного оружия игрока (слот 'weapon' в equipment)."""
    eq = await get_equipment(user_id)
    weapon_id = eq.get('weapon')
    if not weapon_id:
        return 0
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT damage FROM items WHERE id = ? AND category = 'weapon'",
        (weapon_id,)
    )
    row = await cursor.fetchone()
    return row['damage'] if row else 0


async def get_player_duel_gear_damage(user_id: int) -> int:
    """Урон дуэльного снаряжения (слот 'duel' в equipment).

    Применяется ТОЛЬКО в дуэлях: обычное оружие на арене не используется.
    """
    eq = await get_equipment(user_id)
    item_id = eq.get('duel')
    if not item_id:
        return 0
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT damage FROM items WHERE id = ? AND category = 'duel_gear'",
        (item_id,)
    )
    row = await cursor.fetchone()
    return row['damage'] if row else 0


async def get_equipped_weapon(user_id: int):
    """Полная запись активного оружия игрока (слот 'weapon') или None."""
    eq = await get_equipment(user_id)
    weapon_id = eq.get('weapon')
    if not weapon_id:
        return None
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT * FROM items WHERE id = ? AND category = 'weapon'",
        (weapon_id,)
    )
    return await cursor.fetchone()


async def get_player_armor(user_id: int) -> int:
    """Суммарная защита брони: голова + тело + руки + ноги."""
    eq = await get_equipment(user_id)
    ids = [eq[s] for s in ARMOR_SLOTS if eq.get(s)]
    if not ids:
        return 0
    ph = ",".join("?" * len(ids))
    conn = await get_db()
    cursor = await conn.execute(
        f"SELECT COALESCE(SUM(armor), 0) AS s FROM items WHERE id IN ({ph})", ids
    )
    row = await cursor.fetchone()
    return row['s'] if row else 0


# Базовое уклонение пилота (%) — остальное добавляют награды.
PLAYER_BASE_DODGE = 3


# Потолок суммарного шанса крита, %. Выше 75 делать смысла нет: при множителе
# 1.4 крит и так бьёт очень сильно, а 100% сделало бы бой полностью случайным.
MAX_CRIT_CHANCE = 75


async def get_player_crit_chance(user_id: int) -> float:
    """Суммарный шанс крита пилота в %.

    Складывается из трёх источников (решение владельца 2026-10-03):
    базовый шанс по званию (RANK_CRIT_CHANCE), crit_chance надетого снаряжения
    и bonus_crit наград. Результат ограничен MAX_CRIT_CHANCE.

    Шанс может быть дробным (шаг базовой шкалы — 1.5%), поэтому возвращается
    float, а не int.
    """
    chance = await get_pilot_crit_chance(user_id)
    chance += await get_player_gear_crit_chance(user_id)
    chance += int((await get_award_bonus(user_id)).get('crit') or 0)
    return max(0.0, min(float(MAX_CRIT_CHANCE), chance))


async def get_player_gear_crit_chance(user_id: int) -> float:
    """Суммарный crit_chance по всем надетым предметам (в %)."""
    eq = await get_equipment(user_id)
    ids = [i for i in eq.values() if i]
    if not ids:
        return 0.0
    ph = ",".join("?" * len(ids))
    conn = await get_db()
    cursor = await conn.execute(
        f"SELECT COALESCE(SUM(crit_chance), 0) AS s FROM items WHERE id IN ({ph})", ids
    )
    row = await cursor.fetchone()
    return float(row['s'] or 0) if row else 0.0


async def get_player_crit_mult(user_id: int) -> float:
    """Множитель урона при крите: базовый PILOT_CRIT_MULT плюс crit_mult
    надетого снаряжения. Если снаряжение ничего не добавляет — базовый.
    """
    mult = float(PILOT_CRIT_MULT or 1.0)
    eq = await get_equipment(user_id)
    ids = [i for i in eq.values() if i]
    if ids:
        ph = ",".join("?" * len(ids))
        conn = await get_db()
        cursor = await conn.execute(
            f"SELECT COALESCE(SUM(crit_mult), 0) AS s FROM items WHERE id IN ({ph})", ids
        )
        row = await cursor.fetchone()
        extra = float(row['s'] or 0) if row else 0.0
        if extra:
            mult += extra
    return max(1.0, mult)


async def get_player_dodge(user_id: int, dodge_mult: float = 1.0) -> int:
    """Уклонение пилота в %: база 3% + награды + экип (items.dodge_bonus), × состояния."""
    dodge = PLAYER_BASE_DODGE
    dodge += (await get_award_bonus(user_id))['dodge']
    eq = await get_equipment(user_id)
    ids = [i for i in eq.values() if i]
    if ids:
        conn = await get_db()
        ph = ",".join("?" * len(ids))
        cursor = await conn.execute(
            f"SELECT COALESCE(SUM(dodge_bonus), 0) AS s FROM items WHERE id IN ({ph})",
            ids)
        row = await cursor.fetchone()
        dodge += int(row['s'] or 0) if row else 0
    if dodge_mult != 1.0:
        dodge = int(round(dodge * dodge_mult))
    return max(0, dodge)


async def get_player_heal_bonus_pct(user_id: int) -> int:
    """% к лечению расходников от надетого экипа (items.heal_bonus_pct), потолок 100%."""
    eq = await get_equipment(user_id)
    ids = [i for i in eq.values() if i]
    if not ids:
        return 0
    conn = await get_db()
    ph = ",".join("?" * len(ids))
    cursor = await conn.execute(
        f"SELECT COALESCE(SUM(heal_bonus_pct), 0) AS s FROM items WHERE id IN ({ph})",
        ids)
    row = await cursor.fetchone()
    pct = int(row['s'] or 0) if row else 0
    return max(0, min(100, pct))


async def get_player_armor_with_bonus(user_id: int) -> int:
    """Защита брони с учётом % бонуса защиты от наград."""
    armor = await get_player_armor(user_id)
    if armor <= 0:
        return 0
    bonus = await get_award_bonus(user_id)
    return int(round(armor * (1 + bonus['defense'] / 100.0)))


# ============ ДОМ ДУЭЛЕЙ (PvP) ============

async def get_user_duel_stats(user_id: int) -> dict:
    """Личный рейтинг и счётчик побед/поражений игрока."""
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT duel_rating, duel_wins, duel_losses FROM users WHERE user_id = ?",
        (user_id,))
    row = await cursor.fetchone()
    if not row:
        return {'rating': 0, 'wins': 0, 'losses': 0}
    return {
        'rating': row['duel_rating'] or 0,
        'wins': row['duel_wins'] or 0,
        'losses': row['duel_losses'] or 0,
    }


async def get_duel(duel_id: int):
    conn = await get_db()
    cursor = await conn.execute("SELECT * FROM duel_runs WHERE id = ?", (duel_id,))
    return await cursor.fetchone()


async def _expire_duel(duel_id: int):
    conn = await get_db()
    await conn.execute(
        "UPDATE duel_runs SET status = 'expired', updated_at = CURRENT_TIMESTAMP "
        "WHERE id = ?", (duel_id,))
    await conn.commit()


async def get_active_duel(user_id: int):
    """Незавершённый поединок игрока (invited/active) или None.

    Просроченный вызов и зависший бой лениво переводятся в 'expired', чтобы
    игрок не остался заблокированным навсегда (см. DUEL_CHALLENGE_TIMEOUT_SEC
    и DUEL_STALE_SEC).
    """
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT * FROM duel_runs WHERE (challenger_id = ? OR opponent_id = ?) "
        "AND status IN ('invited', 'active') ORDER BY id DESC LIMIT 1",
        (user_id, user_id))
    row = await cursor.fetchone()
    if row is None:
        return None
    ts = _parse_sqlite_ts(row.get('updated_at')) or _parse_sqlite_ts(row.get('created_at'))
    if ts is not None:
        limit = (config.DUEL_CHALLENGE_TIMEOUT_SEC
                 if row['status'] == 'invited' else config.DUEL_STALE_SEC)
        if time.time() - ts > limit:
            await _expire_duel(row['id'])
            return None
    return row


async def expire_stale_duels() -> int:
    """Принудительно гасит все зависшие дуэли: неотвеченный вызов дольше
    DUEL_CHALLENGE_TIMEOUT_SEC и незавершённый бой дольше DUEL_STALE_SEC.

    Нужно, чтобы брошенные поединки не висели в БД вечно, если ни один из
    участников не зайдёт в арену (ленивая чистка в get_active_duel тогда не
    сработает). Возвращает число погашенных строк.
    """
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT id, status, updated_at, created_at FROM duel_runs "
        "WHERE status IN ('invited', 'active')")
    rows = await cursor.fetchall()
    now = time.time()
    expired = 0
    for row in rows:
        ts = (_parse_sqlite_ts(row.get('updated_at'))
              or _parse_sqlite_ts(row.get('created_at')))
        if ts is None:
            continue
        limit = (config.DUEL_CHALLENGE_TIMEOUT_SEC
                 if row['status'] == 'invited' else config.DUEL_STALE_SEC)
        if now - ts > limit:
            await conn.execute(
                "UPDATE duel_runs SET status = 'expired', updated_at = CURRENT_TIMESTAMP "
                "WHERE id = ?", (row['id'],))
            expired += 1
    if expired:
        await conn.commit()
    return expired


async def create_duel_challenge(challenger_id: int, opponent_id: int):
    """Бросает вызов на дуэль. None, если у кого-то уже идёт поединок."""
    if challenger_id == opponent_id:
        return None
    if await get_active_duel(challenger_id) or await get_active_duel(opponent_id):
        return None
    conn = await get_db()
    cursor = await conn.execute(
        "INSERT INTO duel_runs (challenger_id, opponent_id, status) VALUES (?, ?, 'invited')",
        (challenger_id, opponent_id))
    await conn.commit()
    return cursor.lastrowid


async def accept_duel(duel_id: int, user_id: int, ch_hp: int, ch_max: int,
                      op_hp: int, op_max: int) -> bool:
    """Принимает вызов (только приглашённый). True при успехе."""
    row = await get_duel(duel_id)
    if not row or row['status'] != 'invited' or row['opponent_id'] != user_id:
        return False
    conn = await get_db()
    await conn.execute(
        "UPDATE duel_runs SET status = 'active', challenger_hp = ?, "
        "challenger_hp_max = ?, opponent_hp = ?, opponent_hp_max = ?, turn = 1, "
        "updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (ch_hp, ch_max, op_hp, op_max, duel_id))
    await conn.commit()
    return True


async def decline_duel(duel_id: int):
    conn = await get_db()
    await conn.execute(
        "UPDATE duel_runs SET status = 'declined', updated_at = CURRENT_TIMESTAMP "
        "WHERE id = ?", (duel_id,))
    await conn.commit()


async def set_duel_zone(duel_id: int, user_id: int, atk: str, def_zone: str) -> bool:
    """Запоминает зоны атаки/защиты игрока в текущем раунде."""
    row = await get_duel(duel_id)
    if not row or row['status'] != 'active':
        return False
    if user_id == row['challenger_id']:
        col_a, col_d = 'challenger_atk', 'challenger_def'
    elif user_id == row['opponent_id']:
        col_a, col_d = 'opponent_atk', 'opponent_def'
    else:
        return False
    conn = await get_db()
    await conn.execute(
        f"UPDATE duel_runs SET {col_a} = ?, {col_d} = ?, "
        "updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (atk, def_zone, duel_id))
    await conn.commit()
    return True


def duel_round_ready(row) -> bool:
    """Оба участника сделали выбор зон в текущем раунде."""
    return bool(row['challenger_atk'] and row['challenger_def']
                and row['opponent_atk'] and row['opponent_def'])


async def apply_duel_round(duel_id: int, ch_hp: int, op_hp: int, turn: int):
    """Фиксирует итог раунда: новые HP, очистка зон, следующий ход."""
    conn = await get_db()
    await conn.execute(
        "UPDATE duel_runs SET challenger_hp = ?, opponent_hp = ?, turn = ?, "
        "challenger_atk = NULL, challenger_def = NULL, opponent_atk = NULL, "
        "opponent_def = NULL, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (ch_hp, op_hp, turn, duel_id))
    await conn.commit()


async def finish_duel(duel_id: int, winner_id, rating_delta: int):
    conn = await get_db()
    await conn.execute(
        "UPDATE duel_runs SET status = 'finished', winner_id = ?, rating_delta = ?, "
        "updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (winner_id, rating_delta, duel_id))
    await conn.commit()


async def apply_duel_result(user_id: int, rating_delta: int, result: str):
    """result: 'win' | 'loss' | 'draw'. Обновляет рейтинг и счётчики."""
    conn = await get_db()
    if result == 'win':
        await conn.execute(
            "UPDATE users SET duel_rating = duel_rating + ?, duel_wins = duel_wins + 1 "
            "WHERE user_id = ?", (rating_delta, user_id))
    elif result == 'loss':
        await conn.execute(
            "UPDATE users SET duel_rating = duel_rating + ?, duel_losses = duel_losses + 1 "
            "WHERE user_id = ?", (rating_delta, user_id))
    else:
        await conn.execute(
            "UPDATE users SET duel_rating = duel_rating + ? WHERE user_id = ?",
            (rating_delta, user_id))
    await conn.commit()


async def has_duel_club_card(user_id: int) -> bool:
    """Есть ли у игрока клубная карта Дома Дуэлей."""
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT 1 FROM inventory inv JOIN items i ON inv.item_id = i.id "
        "WHERE inv.user_id = ? AND i.name = ? LIMIT 1",
        (user_id, config.DUEL_CLUB_CARD_NAME))
    return await cursor.fetchone() is not None


async def get_duel_rating_top(limit: int = 10):
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT user_id, duel_rating, duel_wins, duel_losses FROM users "
        "WHERE duel_rating != 0 OR duel_wins != 0 OR duel_losses != 0 "
        "ORDER BY duel_rating DESC, duel_wins DESC LIMIT ?", (limit,))
    return await cursor.fetchall()


async def get_duel_opponents(exclude_id: int, limit: int = 20):
    """Пилоты, которых можно вызвать: статус не ниже требуемого для арены."""
    conn = await get_db()
    req = await (await conn.execute(
        "SELECT sort_order FROM statuses WHERE access_tag = ?",
        (config.DUEL_ACCESS_TAG,))).fetchone()
    if not req:
        return []
    cursor = await conn.execute("""
        SELECT u.user_id, u.username, u.callsign, u.first_name, u.last_name,
               u.duel_rating, u.duel_wins, u.duel_losses, u.last_active,
               MAX(s.sort_order) AS top
        FROM users u
        JOIN user_statuses us ON us.user_id = u.user_id
        JOIN statuses s ON us.status_id = s.id
        WHERE u.user_id != ?
        GROUP BY u.user_id
        HAVING top >= ?
        ORDER BY u.duel_rating DESC, u.duel_wins DESC, u.user_id
        LIMIT ?
    """, (exclude_id, req['sort_order'], limit))
    return await cursor.fetchall()


async def touch_user_active(user_id: int, ts: float = None):
    """Отметить время последней активности игрока (epoch, сек)."""
    conn = await get_db()
    await conn.execute(
        "UPDATE users SET last_active = ? WHERE user_id = ?",
        (time.time() if ts is None else ts, user_id))
    await conn.commit()


# Слоты снаряжения в users.equipment.
ARMOR_SLOTS = ("head", "body", "hands", "legs")
# Дымовая шашка — расходник побега (отдельный слот, до DUNGEON_SMOKE_MAX за забег).
SMOKE_ITEM_NAME = "Дымовая шашка"
EQUIPMENT_SLOT_LABELS = {
    "weapon": "Основное оружие",
    "weapon_aux": "Вспомогательное оружие",
    "head": "Голова",
    "body": "Тело",
    "hands": "Руки",
    "legs": "Ноги",
    "potion1": "Активный слот 1",
    "potion2": "Активный слот 2",
    "potion3": "Активный слот 3",
    "smoke": "Дымовая шашка",
    "duel": "🥊 Дуэльное снаряжение",
}
# Слоты, которые сейчас заблокированы (откроются позже).
EQUIPMENT_LOCKED_SLOTS = {"weapon_aux", "potion3"}


def item_fits_slot(item, slot: str) -> bool:
    """Подходит ли предмет в слот снаряжения (для списка подходящего в инвентаре)."""
    category = item['category']
    if slot == 'weapon':
        return category == 'weapon'
    if slot in ARMOR_SLOTS:
        if category != 'equipment' or not (item['armor'] or 0):
            return False
        if hasattr(item, 'keys'):
            eq_slot = item['equip_slot'] if 'equip_slot' in item.keys() and item['equip_slot'] else 'body'
        else:
            eq_slot = item.get('equip_slot') or 'body'
        return eq_slot == slot
    if slot in ('potion1', 'potion2'):
        return category == 'consumable' and item.get('name') != SMOKE_ITEM_NAME
    if slot == 'smoke':
        return category == 'consumable' and item['name'] == SMOKE_ITEM_NAME
    if slot == 'duel':
        # Дуэльное снаряжение — только в отдельный слот (в PvE не влияет).
        return category == 'duel_gear'
    return False


async def get_equipment(user_id: int) -> dict:
    """Возвращает активное снаряжение игрока: {slot: item_id}."""
    conn = await get_db()
    cursor = await conn.execute("SELECT equipment FROM users WHERE user_id = ?", (user_id,))
    row = await cursor.fetchone()
    if not row or not row['equipment']:
        return {}
    try:
        eq = json.loads(row['equipment'])
        if not isinstance(eq, dict):
            return {}
        # Миграция старого одиночного слота 'armor' → 'body'
        if 'armor' in eq and not eq.get('body'):
            eq['body'] = eq.pop('armor')
        return {slot: v for slot, v in eq.items() if v}
    except (ValueError, TypeError):
        return {}


async def set_equipment_slot(user_id: int, slot: str, item_id: int):
    """Устанавливает предмет в слот снаряжения. slot: 'weapon' | 'armor'."""
    eq = await get_equipment(user_id)
    eq[slot] = item_id
    await conn_update_equipment(user_id, eq)


async def clear_equipment_slot(user_id: int, slot: str):
    """Снимает предмет из слота снаряжения."""
    eq = await get_equipment(user_id)
    eq.pop(slot, None)
    await conn_update_equipment(user_id, eq)


async def conn_update_equipment(user_id: int, eq: dict):
    conn = await get_db()
    await conn.execute(
        "UPDATE users SET equipment = ? WHERE user_id = ?",
        (json.dumps(eq, ensure_ascii=False), user_id)
    )
    await conn.commit()


async def get_item_by_name(name: str):
    conn = await get_db()
    cursor = await conn.execute("SELECT * FROM items WHERE name = ?", (name,))
    return await cursor.fetchone()


async def get_user_contract_count(user_id: int) -> int:
    """Количество контрактов на зачистку у игрока."""
    conn = await get_db()
    cursor = await conn.execute("""
        SELECT COALESCE(inv.quantity, 0) as qty
        FROM inventory inv JOIN items i ON inv.item_id = i.id
        WHERE inv.user_id = ? AND i.name = 'Контракт на зачистку' AND inv.quantity > 0
    """, (user_id,))
    row = await cursor.fetchone()
    return row['qty'] if row else 0


async def get_user_potions(user_id: int):
    """Зелья здоровья в обычном инвентаре игрока."""
    conn = await get_db()
    cursor = await conn.execute("""
        SELECT i.id, i.name, i.heal, i.photo_file_id, inv.quantity
        FROM inventory inv JOIN items i ON inv.item_id = i.id
        WHERE inv.user_id = ? AND i.category = 'consumable' AND i.heal > 0 AND inv.quantity > 0
        ORDER BY i.heal DESC
    """, (user_id,))
    return await cursor.fetchall()


async def get_equipment_slot_items(user_id: int, include_smoke: bool = False):
    """Предметы в активных слотах зелий (potion1/potion2), с наличием в инвентаре.

    include_smoke=True также добавляет слот дымовой шашки (для боевых клавиатур
    обычных врагов; его нет в бою с боссом: от босса не убежать).
    """
    eq = await get_equipment(user_id)
    slots = [('potion1', eq.get('potion1')), ('potion2', eq.get('potion2'))]
    if include_smoke:
        slots.append(('smoke', eq.get('smoke')))
    result = []
    for slot, item_id in slots:
        if not item_id:
            continue
        conn = await get_db()
        cursor = await conn.execute("""
            SELECT i.id, i.name, i.heal, i.cure_poison, i.cure_frostbite,
                   COALESCE(inv.quantity, 0) as quantity
            FROM items i LEFT JOIN inventory inv ON inv.item_id = i.id AND inv.user_id = ?
            WHERE i.id = ? AND i.category = 'consumable'
        """, (user_id, item_id))
        row = await cursor.fetchone()
        if row and row['quantity'] > 0:
            result.append((slot, row))
    return result


async def ensure_dungeon_shop_items():
    """Идемпотентно добавляет предметы данжа (зелье в магазин, трофеи) — для существующих БД."""
    conn = await get_db()
    added = False

    cursor = await conn.execute("SELECT COUNT(*) as c FROM items WHERE name = ?", ("Малая настойка здоровья",))
    if (await cursor.fetchone())['c'] == 0:
        await add_item(
            name="Малая настойка здоровья",
            description="Восстанавливает 20 HP. Применяется в бою подземелья.",
            price=40, sell_price=20, rarity=2, category="consumable",
            stock=30, added_by=0, ap_cost=0, damage=0, heal=20,
        )
        added = True

    cursor = await conn.execute("SELECT COUNT(*) as c FROM items WHERE name = ?", ("Антидот",))
    if (await cursor.fetchone())['c'] == 0:
        antidote_id = await add_item(
            name="Антидот",
            description="Снимает отравление. Применяется в бою подземелья, если враг тебя отравил.",
            price=60, sell_price=30, rarity=2, category="consumable",
            stock=20, added_by=0, ap_cost=0, damage=0, heal=0,
        )
        await update_item(antidote_id, cure_poison=1)
        added = True

    cursor = await conn.execute("SELECT COUNT(*) as c FROM items WHERE name = ?", (SMOKE_ITEM_NAME,))
    if (await cursor.fetchone())['c'] == 0:
        await add_item(
            name=SMOKE_ITEM_NAME,
            description="Дымовая шашка для побега в подземелье: с ней шанс убежать 95%. "
                        "Ставится в отдельный слот снаряжения; с собой за забег можно взять не больше 2 шт.",
            price=80, sell_price=40, rarity=2, category="consumable",
            stock=-1, added_by=0, ap_cost=0, damage=0, heal=0,
        )
        added = True

    cursor = await conn.execute("SELECT COUNT(*) as c FROM items WHERE name = ?", ("Хвост крысы",))
    if (await cursor.fetchone())['c'] == 0:
        await add_item(
            name="Хвост крысы",
            description="Трофей с крыс подземелья. Используется для производства настоек.",
            price=10, sell_price=5, rarity=2, category="resource",
            stock=-1, added_by=0, ap_cost=0, damage=0, heal=0,
        )
        added = True

    cursor = await conn.execute("SELECT COUNT(*) as c FROM items WHERE name = ?", ("Паутина паука",))
    if (await cursor.fetchone())['c'] == 0:
        await add_item(
            name="Паутина паука", description="Редкий трофей с пауков подземелья. Используется в производстве.",
            price=15, sell_price=7, rarity=3,
            category="resource", stock=-1, added_by=0, ap_cost=0, damage=0, heal=0,
        )
        added = True

    cursor = await conn.execute("SELECT COUNT(*) as c FROM items WHERE name = ?", ("Осколок кристалла",))
    if (await cursor.fetchone())['c'] == 0:
        await add_item(
            name="Осколок кристалла", description="Очень редкий трофей с кристальных пауков. Нужен для крафта.",
            price=40, sell_price=20, rarity=3,
            category="resource", stock=-1, added_by=0, ap_cost=0, damage=0, heal=0,
        )
        added = True

    # Трофеи 2-го этажа Крысиного Подвала (v0.12.0).
    for trophy in (
        ("Кусочек королевского сыра", "Пахучий ломоть сыра, который ворует свита Короля крыс.", 25, 12, 3),
        ("Коготь чумной крысы", "Коготь, оставляющий рваные раны. Приносит удачу на рыбалке.", 35, 17, 3),
        ("Сосулька-паутина", "Застывшая паутина морозного паука. Ингредиент для будущего крафта.", 45, 22, 3),
        ("Метка Короля крыс", "Клеймо, которое Король крыс ставит верным слугам. Любопытный трофей.", 150, 75, 4),
    ):
        cursor = await conn.execute("SELECT COUNT(*) as c FROM items WHERE name = ?", (trophy[0],))
        if (await cursor.fetchone())['c'] == 0:
            await add_item(
                name=trophy[0], description=trophy[1], price=trophy[2], sell_price=trophy[3],
                rarity=trophy[4], category="resource", stock=-1,
                added_by=0, ap_cost=0, damage=0, heal=0,
            )
            added = True

    # Трофеи данжа: появляются в магазине, только когда кто-то продаёт их из инвентаря.
    # Продажа игроком добавляет stock (+1) и включает is_available; при остатке 0 товар снова скрыт.
    await conn.execute("UPDATE items SET is_available = 0, stock = 0 WHERE name IN "
                       "('Хвост крысы','Паутина паука','Осколок кристалла',"
                       "'Кусочек королевского сыра','Коготь чумной крысы',"
                       "'Сосулька-паутина','Метка Короля крыс')")

    # --- Рыбалка ---
    for (fname, fdesc, fprice, fsell, frarity) in (
        ("Удочка из орешника", "Простая лёгкая удочка. Ранг 1: +10% к шансу улова.", 200, 100, 1),
        ("Черви", "Наживка для рыбалки: +15% к шансу улова. Расходуется при забросе, используется только для рыбалки.", 10, 5, 1),
    ):
        cursor = await conn.execute("SELECT COUNT(*) as c FROM items WHERE name = ?", (fname,))
        if (await cursor.fetchone())['c'] == 0:
            await add_item(
                name=fname, description=fdesc, price=fprice, sell_price=fsell, rarity=frarity,
                category="fishing", stock=-1, added_by=0, ap_cost=0, damage=0, heal=0,
            )
            added = True

    cursor = await conn.execute("SELECT COUNT(*) as c FROM items WHERE name = ?", ("Лапка кристального паука",))
    if (await cursor.fetchone())['c'] == 0:
        await add_item(
            name="Лапка кристального паука",
            description="Редкий дроп с кристальных пауков. Наживка для рыбалки: +25% к шансу улова.",
            price=60, sell_price=30, rarity=3,
            category="fishing", stock=0, added_by=0, ap_cost=0, damage=0, heal=0,
        )
        added = True

    for (fname, fdesc, fsell, frarity) in (
        ("Сиг", "Обычная рыба из паркового озера. Сырьё для будущей готовки.", 15, 1),
        ("Муксун", "Редкая рыба из паркового озера. Ценится на рынке.", 35, 2),
        ("Чир", "Очень редкая рыба из паркового озера. Деликатес.", 80, 3),
        ("Налим", "Ночная рыба из паркового озера. Очень редкий улов.", 120, 3),
    ):
        cursor = await conn.execute("SELECT COUNT(*) as c FROM items WHERE name = ?", (fname,))
        if (await cursor.fetchone())['c'] == 0:
            await add_item(
                name=fname, description=fdesc, price=fsell * 2, sell_price=fsell, rarity=frarity,
                category="fishing", stock=-1, added_by=0, ap_cost=0, damage=0, heal=0,
            )
            added = True

    # Мусор со дна озера (без наживки): водоросли — расходник (+1 ОД) и сырьё для
    # будущих энергетиков, появляются в магазине, когда их продаёт пилот (stock=0);
    # сапог — продажа за 15 НМ, в магазин не попадает.
    for (jname, jdesc, jprice, jsell, jstock) in (
            ("Кусочек водорослей", "Съешь и немного взбодришься: +1 ОД при использовании. Улов без наживки.", 5, 3, 0),
            ("Старый сапог", "Проржавевший сапог со дна паркового озера. Продаётся за гроши.", 0, 15, -1),
    ):
        cursor = await conn.execute("SELECT COUNT(*) as c FROM items WHERE name = ?", (jname,))
        if (await cursor.fetchone())['c'] == 0:
            jap_cost = 1 if jname == "Кусочек водорослей" else 0
            await add_item(
                name=jname, description=jdesc, price=jprice, sell_price=jsell, rarity=1,
                category="consumable" if jap_cost else "resource",
                stock=jstock, added_by=0, ap_cost=jap_cost, damage=0, heal=0,
            )
            added = True

    # Миграция для существующих БД: водоросли — расходник с +1 ОД (были resource).
    await conn.execute(
        "UPDATE items SET category = 'consumable', ap_cost = 1, "
        "description = 'Съешь и немного взбодришься: +1 ОД при использовании. Улов без наживки.' "
        "WHERE name = 'Кусочек водорослей'"
    )

    # Рыба — только из рыбалки, в магазин не попадает (stock=-1 безлимит, но
    # is_available=0). Лапка и водоросли — трофей: появляются на рынке после
    # продажи игроком (is_available поднимается в inv_sell). Сапог — безлимит,
    # в магазине не нужен.
    await conn.execute("UPDATE items SET is_available = 0 WHERE name IN "
                       "('Сиг','Муксун','Чир','Налим','Лапка кристального паука',"
                       "'Кусочек водорослей','Старый сапог')")

    cursor = await conn.execute("SELECT COUNT(*) as c FROM items WHERE name = ?", ("Контракт на зачистку",))
    if (await cursor.fetchone())['c'] == 0:
        contract_id = await add_item(
            name="Контракт на зачистку",
            description="Задание на зачистку Крысиного подвала. Даёт право на один вход. Только для Ветеранов.",
            price=100, sell_price=50, rarity=3, category="special",
            stock=50, added_by=0, ap_cost=0, damage=0, heal=0,
        )
        await update_item(contract_id, required_status="veteran")
        added = True

    for (sname, sdesc, sprice, srarity, sstock) in (
        ("Магнит «Нордхайм»", "Сувенир с видами Нордхайма.", 15, 1, 50),
        ("Кружка «Аркхольм»", "Сувенирная кружка с гербом города.", 25, 2, 30),
        ("Открытка «Город Аркхольм»", "Почтовая открытка с панорамой Аркхольма.", 10, 1, 100),
    ):
        cursor = await conn.execute("SELECT COUNT(*) as c FROM items WHERE name = ?", (sname,))
        if (await cursor.fetchone())['c'] == 0:
            await add_item(
                name=sname, description=sdesc, price=sprice, sell_price=sprice // 2, rarity=srarity,
                category="souvenirs", stock=sstock, added_by=0, ap_cost=0, damage=0, heal=0,
            )
            added = True

    # --- Читательские билеты библиотеки ---
    cursor = await conn.execute("SELECT COUNT(*) as c FROM items WHERE name = ?", ("Читательский билет",))
    if (await cursor.fetchone())['c'] == 0:
        await add_item(
            name="Читательский билет",
            description="Даёт доступ к разделам «История», «Законы» и «Художественная литература» библиотеки на 30 дней.",
            price=300, sell_price=0, rarity=2, category="library_card",
            stock=-1, added_by=0, ap_cost=0, damage=0, heal=0,
        )
        added = True

    cursor = await conn.execute("SELECT COUNT(*) as c FROM items WHERE name = ?", ("Серебряный читательский билет",))
    if (await cursor.fetchone())['c'] == 0:
        silver_id = await add_item(
            name="Серебряный читательский билет",
            description="Открывает ВСЕ разделы библиотеки на 30 дней. Только для Ветеранов.",
            price=1000, sell_price=0, rarity=3, category="library_card",
            stock=-1, added_by=0, ap_cost=0, damage=0, heal=0,
        )
        await update_item(silver_id, required_status="veteran")
        added = True

    return added


async def ensure_life_items():
    """Идемпотентно добавляет предметы жилья, мебели, семян, ресурсов и продовольствия."""
    conn = await get_db()
    added = False

    # Кадка переименована: «Кадка с растением» → «Кадка для растений» (и в старых БД).
    # Делаем до сидирования ниже, чтобы не появился дубль с новым именем.
    await conn.execute(
        "UPDATE items SET name = 'Кадка для растений' WHERE name = 'Кадка с растением'"
    )

    def _item(name: str):
        return name

    # (имя, описание, цена, продажа, рарность, категория, stock, heal, required_status, is_available)
    items = [
        ("Студия", "Квартира-студия: одна комната и свободная планировка. 1 слот расширений.",
         500, 250, 2, "housing", -1, 0, "pilot2", 1),
        ("Квартира", "Просторная двухкомнатная квартира. 2 слота расширений.",
         1500, 750, 3, "housing", -1, 0, "pilot1", 1),
        ("Улучшенное жильё", "Просторное жильё с несколькими комнатами. Ветеранская планировка: 3 слота расширений.",
         3000, 1500, 4, "housing", -1, 0, "veteran", 1),
        ("Особняк", "Роскошный особняк для Мастер-пилота. 6 слотов расширений и свобода в оформлении.",
         5000, 2500, 5, "housing", -1, 0, "master_pilot", 1),
        ("Кухня 1 уровня", "Простая кухня: можно жарить рыбу.",
         100, 50, 1, "furniture", -1, 0, "pilot2", 1),
        ("Кухня 2 уровня", "Кухня с плитой: варка настоек.",
         300, 150, 2, "furniture", -1, 0, "pilot1", 1),
        ("Кухня 3 уровня", "Кухня с полным набором инструментов: энергетики и редкие настойки.",
         800, 400, 3, "furniture", -1, 0, "master_pilot", 1),
        ("Верстак", "Рабочее место для сборки простых предметов.",
         150, 75, 1, "furniture", -1, 0, "pilot2", 1),
        ("Кадка для растений", "Кадка для выращивания растений. Пустая — в неё сажаются семена.",
         200, 100, 1, "furniture", -1, 0, "pilot2", 1),
        ("Душевая", "Простая душевая кабина. Раз в сутки можно принять душ: +25 ОД.",
         450, 225, 1, "furniture", -1, 0, "pilot1", 1),
        ("Ванная с душем", "Просторная ванная комната с душем. Раз в сутки можно принять ванну: +50 ОД.",
         950, 475, 2, "furniture", -1, 0, "veteran", 1),
        ("Яблочное семечко", "Семечко яблони. Посади в кадку в жилье — вырастет яблоня.",
         30, 15, 1, "seeds", 10, 0, "pilot2", 1),
        ("Бутылка чистой воды", "Чистая вода из артезианской скважины. Основа для настоек и энергетиков.",
         20, 10, 1, "resource", -1, 0, "pilot2", 1),
        ("Соль", "Каменная соль из лавки. Специи для готовки рыбы: ни одно жареное блюдо не обходится без щепотки.",
         5, 2, 1, "consumable", -1, 0, None, 1),
        ("Мука", "Мука с парковской мельницы. Для выпечки: без неё не испечёшь рыбный пирог.",
         8, 4, 1, "consumable", -1, 0, None, 1),
        ("Лапка паука", "Высушенная лапка обычного паука. Ингредиент для комбинированной наживки.",
         10, 5, 1, "resource", 0, 0, None, 0),
        ("Жареный сиг", "Жаренный на углях сиг. +15 HP в бою. Срок годности 4 суток.",
         60, 30, 1, "consumable", -1, 15, None, 0),
        ("Жареный муксун", "Нежный жареный муксун. +30 HP в бою. Срок годности 4 суток.",
         140, 70, 2, "consumable", -1, 30, None, 0),
        ("Жареный чир", "Деликатес: жареный чир. +45 HP в бою. Срок годности 4 суток.",
         300, 150, 3, "consumable", -1, 45, None, 0),
        ("Жареный налим", "Праздничный ужин: жареный налим. +55 HP в бою. Срок годности 4 суток.",
         440, 220, 3, "consumable", -1, 55, None, 0),
        ("Испорченный сиг", "Протухшая рыба. Слегка восстанавливает HP, но навлекает несварение.",
         14, 7, 1, "consumable", -1, 5, None, 0),
        ("Испорченный муксун", "Протухшая рыба. Слегка восстанавливает HP, но навлекает несварение.",
         34, 17, 2, "consumable", -1, 5, None, 0),
        ("Испорченный чир", "Протухший деликатес. Слегка восстанавливает HP, но навлекает несварение.",
         80, 40, 3, "consumable", -1, 5, None, 0),
        ("Испорченный налим", "Протухшая ночная добыча. Слегка восстанавливает HP, но навлекает несварение.",
         120, 60, 3, "consumable", -1, 5, None, 0),
        ("Яблоко", "Свежее яблоко из кадки. +15 HP в бою. Иногда из него выпадает семечко.",
         20, 10, 1, "consumable", -1, 15, None, 0),
        ("Улучшенная настойка здоровья", "Мощный эликсир: +50 HP в бою подземелья.",
         80, 40, 3, "consumable", 20, 50, None, 1),
        ("Комбинированная наживка", "Сборная наживка с верстака: +30% к шансу улова. Расходуется при забросе.",
         30, 15, 2, "fishing", -1, 0, None, 0),
        # Пиво «Мерцание Севера»: фирменный напиток города. Пьётся где угодно,
        # в бою подземелья дополнительно даёт +HP. 3-я бутылка за сутки → «пьян»;
        # 6-я → «очень пьян» (блок расходников, всех входов, 6 часов).
        ("Пиво \"Мерцание Севера\"", "Фирменное холодное пиво Нордхайма. "
         "Восстанавливает 10 HP в бою подземелья. Пьётся где угодно, но держи себя в руках: "
         "3 бутылки за сутки — и ты пьян, 6 — совсем плохо.",
         40, 20, 1, "consumable", -1, 10, None, 1),
    ]
    for (name, desc, price, sell, rarity, category, stock, heal, req_status, is_avail) in items:
        cursor = await conn.execute("SELECT COUNT(*) as c FROM items WHERE name = ?", (name,))
        if (await cursor.fetchone())['c'] == 0:
            item_id = await add_item(
                name=name, description=desc, price=price, sell_price=sell, rarity=rarity,
                category=category, stock=stock, added_by=0, ap_cost=0, damage=0, heal=heal,
            )
            if req_status:
                await update_item(item_id, required_status=req_status)
            if not is_avail:
                await update_item(item_id, is_available=0)
            added = True

    # --- Обувь с верстака (v0.15.7): «Пара сапог» из старой обуви, паутины,
    # клея и набора игл. Клей и набор игл продаются в лавке, пара сапог —
    # только через рецепт верстака (is_available=0, как жареная рыба). ---
    for (name, desc, price, sell, rarity, category) in (
        ("Клей", "Клей из смолы и рыбьего желатина: скрепляет что угодно — вплоть до подошвы.",
         40, 20, 2, "consumable"),
        ("Набор игл", "Швейные иглы разных размеров. Для ремонта и сборки снаряжения.",
         35, 17, 2, "resource"),
    ):
        cursor = await conn.execute("SELECT COUNT(*) as c FROM items WHERE name = ?", (name,))
        if (await cursor.fetchone())['c'] == 0:
            await add_item(
                name=name, description=desc, price=price, sell_price=sell, rarity=rarity,
                category=category, stock=-1, added_by=0, ap_cost=0, damage=0, heal=0,
            )
            added = True

    cursor = await conn.execute("SELECT COUNT(*) as c FROM items WHERE name = ?", ("Пара сапог",))
    if (await cursor.fetchone())['c'] == 0:
        boots_id = await add_item(
            name="Пара сапог",
            description="Прочные сапоги, собранные на верстаке из старых сапог и паутины паука. Броня ног: 2.",
            price=120, sell_price=40, rarity=2, category="equipment", stock=-1,
            added_by=0, ap_cost=0, damage=0, heal=0, armor=2, equip_slot="legs",
        )
        await update_item(boots_id, is_available=0)
        added = True
    # Подстраховка старых БД: слот и броня ног.
    await conn.execute("UPDATE items SET equip_slot = 'legs' WHERE name = 'Пара сапог' AND equip_slot IS NULL")
    await conn.execute("UPDATE items SET armor = 2 WHERE name = 'Пара сапог' AND (armor IS NULL OR armor = 0)")

    # --- Рыбный пирог (v0.22.11): 5 карасей + сиг + муксун. Единственное блюдо
    # с регенерацией: +80 HP и 60% от лечения тиками в следующие 3 хода боя. ---
    cursor = await conn.execute("SELECT COUNT(*) as c FROM items WHERE name = 'Рыбный пирог'")
    if (await cursor.fetchone())['c'] == 0:
        pie_id = await add_item(
            name="Рыбный пирог",
            description=("Запечённый пирог с карасём, сигом и муксуном. "
                         "+80 HP в бою подземелья и регенерация 60% от лечения следующие "
                         "3 хода. Срок годности 4 суток."),
            price=400, sell_price=200, rarity=3, category="consumable", stock=-1,
            added_by=0, ap_cost=0, damage=0, heal=80, regen=60,
        )
        await update_item(pie_id, is_available=0)
        added = True
    await conn.execute("UPDATE items SET heal = 80 WHERE name = 'Рыбный пирог' AND heal != 80")
    await conn.execute("UPDATE items SET regen = 60 WHERE name = 'Рыбный пирог' AND regen != 60")
    await conn.execute("UPDATE items SET is_available = 0 WHERE name = 'Рыбный пирог'")

    # Типы напитков: привязываем действие на состояние к напиткам по имени
    # (миграция старых БД + сидирование новых). Один напиток — одно действие.
    drink_sync = {
        "alcohol_weak": ("Пиво \"Мерцание Севера\"",),
    }
    for effect, names in drink_sync.items():
        await conn.execute(
            "UPDATE items SET drink_effect = ? WHERE name IN ({})".format(
                ",".join("?" * len(names))), (effect,) + tuple(names)
        )

    # Синхронизация цен/статусов для уже существующих жилья-предметов (напр. в старых БД v0.5.0-ранний).
    housing_sync = {
        "Студия": {"price": 500, "sell_price": 250, "required_status": "pilot2"},
        "Квартира": {"price": 1500, "sell_price": 750, "required_status": "pilot1"},
        "Улучшенное жильё": {"price": 3000, "sell_price": 1500, "required_status": "veteran"},
        "Особняк": {"price": 5000, "sell_price": 2500, "required_status": "master_pilot"},
    }
    for name, vals in housing_sync.items():
        await conn.execute(
            "UPDATE items SET price = ?, sell_price = ?, required_status = ? WHERE name = ?",
            (vals["price"], vals["sell_price"], vals["required_status"], name)
        )

    # Синхронизация HP жареной рыбы (уменьшено на 15)
    fried_heal_sync = {
        "Жареный сиг": 15, "Жареный муксун": 30,
        "Жареный чир": 45, "Жареный налим": 55,
    }
    for name, heal in fried_heal_sync.items():
        await conn.execute("UPDATE items SET heal = ? WHERE name = ? AND heal != ?",
                           (heal, name, heal))

    # Лапка паука добавлен в дропы кристального паука в DEFAULT_DUNGEON
    # (синхронизируется через ensure_dungeon_enemy_drops на старте).
    await conn.commit()
    return added


async def ensure_dungeon_reservoir_items():
    """Идемпотентно добавляет предметы водохранилища подземелья (v0.12.0).

    Рыба водохранилища ловится только в подземном водохранилище и в магазин
    не попадает. Напитки-лечение снимают обморожение в бою подземелья.
    """
    conn = await get_db()
    added = False

    # Рыба водохранилища: (имя, описание, цена, продажа, рарность).
    reservoir_fish = (
        ("Мерцающий сом", "Рыба из подземного водохранилища. Тёмная чешуя мерцает, как вода. Обычный, но вкусный улов.",
         240, 120, 2),
        ("Искрящийся угорь", "Редкая рыба-электрик из подземного водохранилища. При разряде светится изнутри.",
         500, 250, 3),
        ("Светящаяся форель", "Секретная рыба водохранилища. Сияет холодным светом, как маленькая луна. Такой почти никто не видел.",
         900, 450, 4),
    )
    for (fname, fdesc, fprice, fsell, frarity) in reservoir_fish:
        cursor = await conn.execute("SELECT COUNT(*) as c FROM items WHERE name = ?", (fname,))
        if (await cursor.fetchone())['c'] == 0:
            await add_item(
                name=fname, description=fdesc, price=fprice, sell_price=fsell, rarity=frarity,
                category="fishing", stock=-1, added_by=0, ap_cost=0, damage=0, heal=0,
            )
            added = True
        await conn.execute("UPDATE items SET is_available = 0 WHERE name = ?", (fname,))

    # Жареная рыба водохранилища (рецепты «Пожарить …» требуют соль + кусочек водорослей).
    # (имя, описание, цена, продажа, рарность, heal)
    reservoir_fried = (
        ("Жареный сом", "Жареный сом со специями и водорослями. +65 HP в бою подземелья. Срок годности 4 суток.",
         520, 260, 2, 65),
        ("Жареный угорь", "Хрустящий жареный угорь с водорослями. +90 HP в бою подземелья. Срок годности 4 суток.",
         850, 425, 3, 90),
        ("Жареный форель", "Светящаяся форель, пожаренная до золотой корочки. +140 HP в бою подземелья. Срок годности 4 суток.",
         1200, 600, 4, 140),
    )
    for (iname, idesc, iprice, isell, irarity, iheal) in reservoir_fried:
        cursor = await conn.execute("SELECT COUNT(*) as c FROM items WHERE name = ?", (iname,))
        if (await cursor.fetchone())['c'] == 0:
            await add_item(
                name=iname, description=idesc, price=iprice, sell_price=isell, rarity=irarity,
                category="consumable", stock=-1, added_by=0, ap_cost=0, damage=0, heal=iheal,
            )
            added = True
        await conn.execute("UPDATE items SET is_available = 0 WHERE name = ?", (iname,))
        await conn.execute("UPDATE items SET heal = ? WHERE name = ? AND heal != ?", (iheal, iname, iheal))

    # Испорченная рыба водохранилища (после порчи).
    reservoir_spoiled = (
        ("Испорченный сом", "Протухший сом. Слегка восстанавливает HP, но навлекает несварение.",
         90, 45, 2, 5),
        ("Испорченный угорь", "Протухший угорь. Слегка восстанавливает HP, но навлекает несварение.",
         150, 75, 3, 5),
        ("Испорченный форель", "Спавший свет. Слегка восстанавливает HP, но навлекает несварение.",
         360, 180, 4, 5),
    )
    for (iname, idesc, iprice, isell, irarity, iheal) in reservoir_spoiled:
        cursor = await conn.execute("SELECT COUNT(*) as c FROM items WHERE name = ?", (iname,))
        if (await cursor.fetchone())['c'] == 0:
            await add_item(
                name=iname, description=idesc, price=iprice, sell_price=isell, rarity=irarity,
                category="consumable", stock=-1, added_by=0, ap_cost=0, damage=0, heal=iheal,
            )
            added = True
        await conn.execute("UPDATE items SET is_available = 0 WHERE name = ?", (iname,))

    # Напитки-лечение обморожения. (имя, описание, цена, продажа, рарность, heal, drink_effect).
    cure_frostbite_drinks = (
        ("Огненная вода (водка)", "Крепкая, жгучая, «настоящая» — греет до костей. "
         "В бою подземелья снимает обморожение и восстанавливает 10 HP. Не злоупотребляй.",
         70, 35, 2, 10, "alcohol_strong"),
        ("Горячий ягодный морс", "Горячий морс из северных ягод. Согревает и лечит: "
         "в бою подземелья снимает обморожение и восстанавливает 10 HP.",
         35, 17, 1, 10, "none"),
    )
    for (dname, ddesc, dprice, dsell, drarity, dheal, deffect) in cure_frostbite_drinks:
        cursor = await conn.execute("SELECT COUNT(*) as c FROM items WHERE name = ?", (dname,))
        if (await cursor.fetchone())['c'] == 0:
            item_id = await add_item(
                name=dname, description=ddesc, price=dprice, sell_price=dsell, rarity=drarity,
                category="consumable", stock=-1, added_by=0, ap_cost=0, damage=0, heal=dheal,
            )
            await update_item(item_id, drink_effect=deffect, cure_frostbite=1)
            added = True
        else:
            await conn.execute(
                "UPDATE items SET drink_effect = ?, cure_frostbite = 1, heal = ? WHERE name = ?",
                (deffect, dheal, dname)
            )

    await conn.commit()
    return added


async def ensure_dungeon_enemy_drops():
    """Синхронизирует врагов существующего данжа с DEFAULT_DUNGEON (дропы, HP, награды,
    этажи, описания боссов, новые статусные поля кровотечения/обморожения)."""
    conn = await get_db()

    dungeons = await get_all_dungeons(training=False)
    if not dungeons:
        return
    dungeon_id = dungeons[0]['id']

    # Комнат по этажам (JSON) и число этажей — из конфига.
    rooms_vals = [floor_data.get("rooms", 10) for floor_data in DEFAULT_DUNGEON["floors"]]
    await conn.execute(
        "UPDATE dungeons SET rooms_map = ?, rooms_per_floor = ?, floors_count = ? WHERE id = ?",
        (json.dumps(rooms_vals, ensure_ascii=False), rooms_vals[0], len(DEFAULT_DUNGEON["floors"]), dungeon_id)
    )

    expected = set()
    for floor_idx, floor_data in enumerate(DEFAULT_DUNGEON["floors"], 1):
        for enemy in floor_data["enemies"] + [floor_data["boss"]]:
            f = _enemy_to_fields(enemy)
            expected.add(f["name"])
            drops_json = json.dumps(f["drops"], ensure_ascii=False)
            cursor = await conn.execute(
                "SELECT admin_tuned FROM dungeon_enemies WHERE dungeon_id = ? AND name = ? AND is_boss = ?",
                (dungeon_id, f["name"], f["is_boss"])
            )
            existing = await cursor.fetchone()
            if existing is None:
                await conn.execute(
                    f"INSERT INTO dungeon_enemies ({DUNGEON_ENEMY_INSERT_COLS}) "
                    f"VALUES ({','.join(['?'] * 17)})",
                    (dungeon_id, floor_idx, f["name"], f["hp"], f["attack"], f["reward_nm"],
                     f["is_boss"], drops_json, f["image"],
                     f["poison_chance"], f["poison_dmg"], f["dodge"],
                     f["bleed_chance"], f["bleed_dmg"], f["frostbite_chance"],
                     f["description"], f["on_hit_effects"])
                )
            else:
                # Этаж синхронизируем всегда (нужен для переезда боссов между ярусами).
                # Описание/картинка тоже правится админом через бота — поэтому их,
                # как и боевую статистику, не трогаем, если врага калибровал админ.
                base = "floor = ?"
                base_vals = [floor_idx]
                if not existing['admin_tuned']:
                    base += ", description = ?, hp = ?, attack = ?, reward_nm = ?, drops = ?, image = ?, " \
                            "poison_chance = ?, poison_dmg = ?, dodge = ?, " \
                            "bleed_chance = ?, bleed_dmg = ?, frostbite_chance = ?, on_hit_effects = ?"
                    base_vals += [f["description"], f["hp"], f["attack"], f["reward_nm"],
                                  drops_json, f["image"],
                                  f["poison_chance"], f["poison_dmg"], f["dodge"],
                                  f["bleed_chance"], f["bleed_dmg"], f["frostbite_chance"],
                                  f["on_hit_effects"]]
                base_vals += [dungeon_id, f["name"], f["is_boss"]]
                await conn.execute(
                    f"UPDATE dungeon_enemies SET {base} "
                    f"WHERE dungeon_id = ? AND name = ? AND is_boss = ?",
                    base_vals
                )

    # Удаляем врагов, которых больше нет в конфиге (старый состав).
    # Врагов, которых правил админ через бота, не трогаем.
    cursor = await conn.execute(
        "SELECT id, name FROM dungeon_enemies WHERE dungeon_id = ? AND name NOT IN (%s) AND admin_tuned = 0"
        % ",".join("?" * len(expected)), (dungeon_id, *expected)
    )
    to_delete = await cursor.fetchall()
    for row in to_delete:
        await conn.execute("DELETE FROM dungeon_enemies WHERE id = ?", (row['id'],))

    await conn.commit()


# ============ ЖИЛЬЁ, РЕЦЕПТЫ, РАСТЕНИЯ ============

# Типы жилья и число слотов расширений.
KUBRIK_DESC = ('Жилой бокс «Кубрик Кубик»: индивидуальное пространство 4 на 4 метра, '
               'уголок приватности рекрута в огромном здании казённого жилого модуля '
               'эскадрилий. Есть электричество и отопление, остальные удобства — на этаже, '
               'слева и справа в конце коридора.')
STUDIO_DESC = ('Квартира-студия в рабочем районе: стены не могут похвастаться толщиной, '
               'а звуки улицы вряд ли дадут долго спать поутру. Зато не надо ждать очередь '
               'в ванну и составлять расписание на пользование плитой. Маленький духовой шкаф, '
               'совмещённый с плиткой, уже входит в стоимость — социальная программа '
               '«Забота Нордхайма».')
APARTMENT_DESC = ('Двухкомнатная квартира — жильё среднего класса. Просторные комнаты '
                  'и довольно толстые стены, чтобы не отвлекаться на крики или странные '
                  'музыкальные предпочтения соседей. Отдельное помещение для кухни '
                  'и совмещённый санузел.')
HOUSING_TYPES = {
    "municipal": {"name": "Кубрик", "slots": 0, "desc": KUBRIK_DESC},
    "studio": {"name": "Студия", "slots": 1, "desc": STUDIO_DESC},
    "apartment": {"name": "Квартира", "slots": 2, "desc": APARTMENT_DESC},
    "improved": {"name": "Улучшенное жильё", "slots": 3},
    "mansion": {"name": "Особняк", "slots": 6},
}
HOUSING_ORDER = ["municipal", "studio", "apartment", "improved", "mansion"]

# Стадии роста растения: (название, длительность_суток). Последняя — без конца.
PLANT_STAGES = [
    ("Семя", 2),
    ("Росток", 4),
    ("Саженец", 8),
    ("Цветущее", 16),
    ("Плодоносящее", None),
]
FRUIT_EVERY_DAYS = 2
APPLE_SEED_NAME = "Яблочное семечко"
APPLE_NAME = "Яблоко"
# Название растения в кадке: seed_name → как называется выросшее растение
# (семечко — это товар в магазине, в кадке выращивается само растение).
# Неизвестные семечки показываются своим названием (как раньше).
PLANT_NAMES = {
    "Яблочное семечко": "Яблоня",
}
# Что даёт сбор с растения: seed_name → название предмета-плода.
# Новое семечко без записи по умолчанию даёт яблоко (как было в жилье).
PLANT_HARVEST = {
    "Яблочное семечко": APPLE_NAME,
}
# v0.41.2 Огненный Лабиринт (Фаза 4): тыква — праздничное растение.
if getattr(config, "FIRE_PUMPKIN_SEED_NAME", None):
    _pumpkin_plant = getattr(config, "FIRE_PUMPKIN_NAME", "Тыква")
    PLANT_NAMES[config.FIRE_PUMPKIN_SEED_NAME] = _pumpkin_plant
    PLANT_HARVEST[config.FIRE_PUMPKIN_SEED_NAME] = _pumpkin_plant


def plant_harvest_name(seed_name: str | None) -> str:
    """Название плода, который даёт растение этого семечка."""
    return PLANT_HARVEST.get(seed_name or "", APPLE_NAME)
FOOD_SHELF_DAYS = 4  # срок годности жареной рыбы (96 часов)
# Срок годности сырой (неприготовленной) рыбы: 4 дня с момента поимки.
RAW_FISH_SHELF_DAYS = 4
RAW_FISH_SHELF_SEC = RAW_FISH_SHELF_DAYS * 86400


async def ensure_player_housing(user_id: int):
    """Возвращает жильё игрока, создавая муниципальную квартиру для пилота при первом обращении."""
    conn = await get_db()
    cursor = await conn.execute("SELECT * FROM player_housing WHERE user_id = ?", (user_id,))
    row = await cursor.fetchone()
    if row:
        return dict(row)
    await conn.execute(
        "INSERT OR IGNORE INTO player_housing (user_id, housing_type) VALUES (?, 'municipal')",
        (user_id,)
    )
    await conn.commit()
    return {"user_id": user_id, "housing_type": "municipal", "purchased_at": None}


async def get_player_housing(user_id: int):
    return await ensure_player_housing(user_id)


async def set_player_housing(user_id: int, housing_type: str,
                             housing_label: str = None, housing_slots: int = None):
    conn = await get_db()
    if housing_slots is None:
        # Если число слотов не задано — берём дефолт типа (и снимаем прежний лимит).
        await conn.execute(
            "INSERT OR REPLACE INTO player_housing "
            "(user_id, housing_type, purchased_at, housing_label, housing_slots) "
            "VALUES (?, ?, datetime('now'), ?, NULL)",
            (user_id, housing_type, housing_label)
        )
    else:
        await conn.execute(
            "INSERT OR REPLACE INTO player_housing "
            "(user_id, housing_type, purchased_at, housing_label, housing_slots) "
            "VALUES (?, ?, datetime('now'), ?, ?)",
            (user_id, housing_type, housing_label, housing_slots)
        )
    await conn.commit()


async def get_housing_slots(user_id: int) -> dict:
    """Слоты расширений жилья: {slot_index: row}."""
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT * FROM housing_slots WHERE user_id = ? ORDER BY slot_index", (user_id,)
    )
    rows = await cursor.fetchall()
    return {row['slot_index']: dict(row) for row in rows}


async def get_housing_expansions_installed(user_id: int) -> int:
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT expansions_installed FROM player_housing WHERE user_id = ?", (user_id,)
    )
    row = await cursor.fetchone()
    return row['expansions_installed'] if row else 0


async def increment_housing_expansions(user_id: int):
    conn = await get_db()
    await conn.execute(
        "UPDATE player_housing SET expansions_installed = expansions_installed + 1 WHERE user_id = ?",
        (user_id,)
    )
    await conn.commit()


async def set_housing_slot(user_id: int, slot_index: int, expansion_type: str = None,
                           expansion_level: int = 1, plant_data: dict = None,
                           embedded: bool = False):
    conn = await get_db()
    if not expansion_type:
        await conn.execute(
            "DELETE FROM housing_slots WHERE user_id = ? AND slot_index = ?",
            (user_id, slot_index)
        )
    else:
        pd = json.dumps(plant_data or {}, ensure_ascii=False)
        await conn.execute(
            "INSERT INTO housing_slots (user_id, slot_index, expansion_type, expansion_level, plant_data, embedded) "
            "VALUES (?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(user_id, slot_index) DO UPDATE SET "
            "expansion_type = excluded.expansion_type, expansion_level = excluded.expansion_level, "
            "plant_data = excluded.plant_data, embedded = excluded.embedded",
            (user_id, slot_index, expansion_type, expansion_level, pd, 1 if embedded else 0)
        )
    await conn.commit()


# ---------- Достижения (ачивки) ----------
# ТЗ владельца (2026-10-08, документ в PLAN.md). Каждая ачивка = 4 уровня
# (строки `awards`), прогресс ведётся в `user_achievements`. Пороговые бонусы
# уровней: числа ниже — стартовые значения (в ТЗ заданы точно только наценки
# торговца), их можно точечно менять в DEF, ensure_achievements() пересинхронизи-
# рованная описания и бонусы на старте бота.

BONUS_BONUS_LABELS = {
    "heal_pct": "к лечению",
    "craft_ap_pct": "скидка ОД крафта",
    "ap_bonus": "к восстановлению ОД",
    "loot_pct": "к шансу добычи",
    "dmg_forest": "к урону по лесным существам",
    "rarity_pct": "к шансу редких находок",
    "dmg_dungeon": "к урону в подземельях",
    "bonus_dodge": "к уклонению",
    "bonus_fishing": "к шансу рыбалки",
    "poison_res_pct": "к сопротивлению яду",
    "markup_pct": "к наценке рынка",
    "market_slots": "к слотам рынка",
    "ticket_pct": "скидка на читательский билет",
    "regen_hp": "постоянная регенерация HP",
    "super_rare": "доступ к супер-редкой рыбе",
    "mining_pct": "% к шансу добычи руды",
    "logging_pct": "% к шансу рубки деревьев",
}


def describe_achievement_bonus(bonus: dict) -> str:
    """Человекочитаемое описание бонусов уровня ачивки для экранов."""
    parts = []
    for key, val in (bonus or {}).items():
        label = BONUS_BONUS_LABELS.get(key)
        if not label:
            continue
        if key in ("super_rare", "regen_hp") and val == 1:
            parts.append(label)
        else:
            parts.append(f"+{val} {label}")
    return ", ".join(parts) if parts else ""


ACHIEVEMENTS_DEF = {
    "cooking": {
        "title": "Готовка", "emoji": "🍳", "metric": "приготовлено блюд",
        "levels": [
            {"level": 1, "threshold": 10, "name": "Соль белая смерть",
             "bonus": {"heal_pct": 3}},
            {"level": 2, "threshold": 50, "name": "Главное вовремя перевернуть",
             "bonus": {"heal_pct": 6}},
            {"level": 3, "threshold": 200, "name": "Горячее сырым не бывает",
             "bonus": {"heal_pct": 10}},
            {"level": 4, "threshold": 500, "name": "Друг Фьерна",
             "bonus": {"heal_pct": 15}},
        ],
    },
    "craft": {
        "title": "Крафт", "emoji": "🔨", "metric": "создано вещей",
        "levels": [
            {"level": 1, "threshold": 5, "name": "Я у мамы инженер",
             "bonus": {"craft_ap_pct": 5}},
            {"level": 2, "threshold": 25, "name": "Кулибин",
             "bonus": {"craft_ap_pct": 10}},
            {"level": 3, "threshold": 100, "name": "Левша",
             "bonus": {"craft_ap_pct": 15}},
            {"level": 4, "threshold": 300, "name": "Подмастерье Хрофта",
             "bonus": {"craft_ap_pct": 20}},
        ],
    },
    "books": {
        "title": "Библиотека", "emoji": "📚", "metric": "изучено книг",
        "levels": [
            {"level": 1, "threshold": 3, "name": "Трёхкнижник", "bonus": {}},
            {"level": 2, "threshold": 10, "name": "Увлечённый", "bonus": {}},
            {"level": 3, "threshold": 25, "name": "Буквоед", "bonus": {}},
            {"level": 4, "threshold": 50, "name": "Библиарий Тиды", "bonus": {}},
        ],
    },
    "mining": {
        "title": "Шахты", "emoji": "⛏️", "metric": "добыто руды",
        "levels": [
            {"level": 1, "threshold": 10, "name": "Осколок",
             "bonus": {"mining_pct": 2}},
            {"level": 2, "threshold": 50, "name": "Старатель",
             "bonus": {"mining_pct": 4}},
            {"level": 3, "threshold": 150, "name": "Армадило",
             "bonus": {"mining_pct": 7}},
            {"level": 4, "threshold": 400, "name": "Глашатай Скади",
             "bonus": {"mining_pct": 10}},
        ],
    },
    "logging": {
        "title": "Лесозаготовка", "emoji": "🪓", "metric": "срублено деревьев",
        "levels": [
            {"level": 1, "threshold": 10, "name": "Обух",
             "bonus": {"logging_pct": 2}},
            {"level": 2, "threshold": 50, "name": "Колун",
             "bonus": {"logging_pct": 4}},
            {"level": 3, "threshold": 200, "name": "Мастер Лесоруб",
             "bonus": {"logging_pct": 7}},
            {"level": 4, "threshold": 500, "name": "Хозяин Леса",
             "bonus": {"logging_pct": 10}},
        ],
    },
    "writer": {
        "title": "Стена", "emoji": "✍️", "metric": "постов на стене",
        "levels": [
            {"level": 1, "threshold": 10, "name": "Словоплёт", "bonus": {}},
            {"level": 2, "threshold": 40, "name": "Графоман", "bonus": {}},
            {"level": 3, "threshold": 100, "name": "Чернильная душа", "bonus": {}},
            {"level": 4, "threshold": 300, "name": "Родственник К. Л. М.",
             "bonus": {"ticket_pct": 50}},
        ],
    },
    "trader": {
        "title": "Рынок", "emoji": "🏪", "metric": "выставлено и куплено товаров",
        "levels": [
            {"level": 1, "threshold": 10, "name": "Челнок",
             "bonus": {"markup_pct": 2, "market_slots": 0}},
            {"level": 2, "threshold": 25, "name": "Лавочник",
             "bonus": {"markup_pct": 4, "market_slots": 0}},
            {"level": 3, "threshold": 50, "name": "Купец",
             "bonus": {"markup_pct": 6, "market_slots": 1}},
            {"level": 4, "threshold": 150, "name": "Весы Лагума",
             "bonus": {"markup_pct": 11, "market_slots": 2}},
        ],
    },
    "fountain": {
        "title": "Фонтан", "emoji": "⛲", "metric": "использований фонтана",
        "levels": [
            {"level": 1, "threshold": 10, "name": "Вся эта жизнь",
             "bonus": {"ap_bonus": 1}},
            {"level": 2, "threshold": 30, "name": "Это не ложка…",
             "bonus": {"ap_bonus": 2}},
            {"level": 3, "threshold": 60, "name": "Взгляд внутрь",
             "bonus": {"ap_bonus": 3}},
            {"level": 4, "threshold": 240, "name": "42",
             "bonus": {"ap_bonus": 4}},
        ],
    },
    "hunter": {
        "title": "Охота", "emoji": "🐗", "metric": "добыто лесных зверей",
        "levels": [
            {"level": 1, "threshold": 10, "name": "Глупец",
             "bonus": {"loot_pct": 3}},
            {"level": 2, "threshold": 30, "name": "Смельчак",
             "bonus": {"loot_pct": 6}},
            {"level": 3, "threshold": 50, "name": "Храбрец",
             "bonus": {"loot_pct": 10}},
            {"level": 4, "threshold": 150, "name": "Зверь Севера",
             "bonus": {"loot_pct": 15, "dmg_forest": 10}},
        ],
    },
    "mushrooms": {
        "title": "Грибы", "emoji": "🍄", "metric": "грибов собрано",
        "levels": [
            {"level": 1, "threshold": 25, "name": "Любопытный",
             "bonus": {"rarity_pct": 2}},
            {"level": 2, "threshold": 75, "name": "Грибник",
             "bonus": {"rarity_pct": 4}},
            {"level": 3, "threshold": 300, "name": "Тихий охотник",
             "bonus": {"rarity_pct": 7}},
            {"level": 4, "threshold": 600, "name": "Лесник Хельды",
             "bonus": {"rarity_pct": 10}},
        ],
    },
    "monsters": {
        "title": "Монстры", "emoji": "👹",
        "metric": "повержено чудовищ (подземелья и шахты)",
        "levels": [
            {"level": 1, "threshold": 15, "name": "Претендент",
             "bonus": {"dmg_dungeon": 3}},
            {"level": 2, "threshold": 50, "name": "Ретиарий",
             "bonus": {"dmg_dungeon": 6}},
            {"level": 3, "threshold": 120, "name": "Мимик",
             "bonus": {"dmg_dungeon": 10}},
            {"level": 4, "threshold": 300, "name": "Монстр",
             "bonus": {"dmg_dungeon": 15, "bonus_dodge": 2}},
        ],
    },
    "fishing": {
        "title": "Рыбалка", "emoji": "🎣", "metric": "рыбы поймано",
        "levels": [
            {"level": 1, "threshold": 15, "name": "Новичок",
             "bonus": {"bonus_fishing": 3, "rarity_pct": 2}},
            {"level": 2, "threshold": 40, "name": "Любитель",
             "bonus": {"bonus_fishing": 6, "rarity_pct": 4}},
            {"level": 3, "threshold": 100, "name": "Бывалый",
             "bonus": {"bonus_fishing": 10, "rarity_pct": 7}},
            {"level": 4, "threshold": 300, "name": "Друг Инъёрда",
             "bonus": {"bonus_fishing": 15, "rarity_pct": 10, "super_rare": 1}},
        ],
    },
    "raider": {
        "title": "Глубины", "emoji": "🏚️",
        "metric": "побеждено финальных боссов подземелий",
        "levels": [
            {"level": 1, "threshold": 10, "name": "Разведчик",
             "bonus": {"dmg_dungeon": 3}},
            {"level": 2, "threshold": 25, "name": "Сталкер",
             "bonus": {"dmg_dungeon": 6}},
            {"level": 3, "threshold": 60, "name": "Тень",
             "bonus": {"dmg_dungeon": 10}},
            {"level": 4, "threshold": 120, "name": "Хранитель подземелий",
             "bonus": {"dmg_dungeon": 15}},
        ],
    },
    "money": {
        "title": "Золото", "emoji": "💰",
        "metric": "средств на счету (единовременный максимум)",
        "levels": [
            {"level": 1, "threshold": 500, "name": "Копилка", "bonus": {}},
            {"level": 2, "threshold": 5000, "name": "Сундук", "bonus": {}},
            {"level": 3, "threshold": 20000, "name": "Сын дракона", "bonus": {}},
            {"level": 4, "threshold": 50000, "name": "Золотой запас Севера", "bonus": {}},
        ],
    },
    "reports": {
        "title": "НИИ", "emoji": "📋", "metric": "рассмотрено обращений в НИИ",
        "levels": [
            {"level": 1, "threshold": 1, "name": "Внимательный",
             "bonus": {}, "reward_nm": 20},
            {"level": 2, "threshold": 10, "name": "Испытатель",
             "bonus": {}, "reward_nm": 200},
             {"level": 3, "threshold": 30, "name": "Наладчик",
              "bonus": {}, "reward_nm": 500},
             {"level": 4, "threshold": 60, "name": "Глас Хрофта",
              "bonus": {}, "reward_nm": 0,
              "reward_item": "Рецепт высшего качества"},
        ],
    },
    "duels": {
        "title": "Дуэли", "emoji": "⚔️", "metric": "побед в дуэлях",
        "levels": [
            {"level": 1, "threshold": 1, "name": "Вызов",
             "bonus": {"bonus_dodge": 1}},
            {"level": 2, "threshold": 7, "name": "Клинок",
             "bonus": {"bonus_dodge": 2}},
            {"level": 3, "threshold": 30, "name": "Мастер клинка",
             "bonus": {"bonus_dodge": 3}},
            {"level": 4, "threshold": 100, "name": "Клык Волка",
             "bonus": {"bonus_dodge": 3}},
        ],
    },
    "elixir": {
        "title": "Эликсиры", "emoji": "🧪", "metric": "применений эликсира",
        "levels": [
            {"level": 1, "threshold": 5, "name": "Живая вода",
             "bonus": {"heal_pct": 5}},
            {"level": 2, "threshold": 20, "name": "Здравница",
             "bonus": {"heal_pct": 10}},
            {"level": 3, "threshold": 70, "name": "Неуязвимый",
             "bonus": {"heal_pct": 15}},
            {"level": 4, "threshold": 200, "name": "Дар Инъёрда",
             "bonus": {"regen_hp": 1}},
        ],
    },
    "antidote": {
        "title": "Антидоты", "emoji": "🛡️", "metric": "применений антидота",
        "levels": [
            {"level": 1, "threshold": 5, "name": "Заветы Митридата",
             "bonus": {"poison_res_pct": 10}},
            {"level": 2, "threshold": 25, "name": "Чистый",
             "bonus": {"poison_res_pct": 20}},
            {"level": 3, "threshold": 60, "name": "Адаптированный",
             "bonus": {"poison_res_pct": 30}},
            {"level": 4, "threshold": 200, "name": "Щит Хельды",
             "bonus": {"poison_res_pct": 40}},
        ],
    },
    "fire_fisher": {
        "title": "Праздничная рыбалка", "emoji": "🪣",
        "metric": "видов праздничной рыбы поймано (осетр, душа, карп)",
        "levels": [
            {"level": 1, "threshold": int(getattr(config, "FIRE_FISHER_THRESHOLD", 3) or 3),
             "name": "Рыбак древних", "bonus": {},
             "reward_nm": int(getattr(config, "FIRE_FISHER_REWARD_NM", 150) or 150)},
        ],
    },
    "fire_keeper": {
        "title": "Круговорот", "emoji": "🪔",
        "metric": "собраны все 7 знаков почитания предков (экип, семя, рецепты)",
        "levels": [
            {"level": 1, "threshold": 1, "name": "Чтящий Предков", "bonus": {},
             "reward_nm": 0,
             "reward_item": getattr(config, "FIRE_LANTERN_NAME", "Лампа Круговорота")},
        ],
    },
}


async def ensure_achievements():
    """Идемпотентно засевает награды-уровни достижений и синхронизирует их.

    Строки awards для ачивок живут единым списком с обычными наградами: выдача
    уровня идёт через grant_award(), ревока — через revoke_award(), так что
    «Список наград пилота» и бонусы медалей работают как для ручных наград.
    """
    conn = await get_db()
    for akey, spec in ACHIEVEMENTS_DEF.items():
        for lvl in spec["levels"]:
            bonus = dict(lvl.get("bonus", {}))
            bonus_cols = {}
            for col in ("bonus_dodge", "bonus_fishing"):
                if col in bonus:
                    bonus_cols[col] = bonus.pop(col)
            desc = (f"{spec['metric']} — {lvl['threshold']}. Уровень {lvl['level']}."
                    + (f" Бонус: {describe_achievement_bonus(lvl.get('bonus', {}))}." if lvl.get("bonus") else ""))
            if lvl.get("reward_item"):
                desc += f" Награда: предмет «{lvl['reward_item']}»."
            await create_award(
                name=lvl["name"],
                description=desc,
                emoji=spec["emoji"],
                created_by=None,
                reward_nm=lvl.get("reward_nm", 0),
                **bonus_cols,
            )
            row = await (await conn.execute(
                "SELECT id FROM awards WHERE name = ?", (lvl["name"],))).fetchone()
            if row:
                sql = ("UPDATE awards SET achievement_key = ?, achievement_level = ?, "
                       "bonus_json = ?, description = ?")
                params = [akey, lvl["level"], json.dumps(bonus, ensure_ascii=False), desc]
                if bonus_cols:
                    sql += ", " + ", ".join(f"{k} = ?" for k in bonus_cols)
                    params += [bonus_cols[k] for k in bonus_cols]
                sql += " WHERE id = ?"
                params.append(row["id"])
                await conn.execute(sql, params)
    await conn.commit()


async def _achievement_level_progress(conn, user_id: int, akey: str):
    cursor = await conn.execute(
        "SELECT level, progress FROM user_achievements WHERE user_id = ? AND akey = ?",
        (user_id, akey))
    row = await cursor.fetchone()
    return (row["level"], row["progress"]) if row else (0, 0)


async def _apply_achievement_threshold(conn, user_id: int, akey: str,
                                       spec: dict, level: int, progress: int):
    """Повышает уровень ачивки по прогрессу: ревока прошлого уровня и выдача нового."""
    target = None
    for lvl in spec["levels"]:
        if progress >= lvl["threshold"]:
            target = lvl
        else:
            break
    if not target or target["level"] == level:
        return None, None, None
    prev_name = None
    if level:
        prev = await (await conn.execute(
            "SELECT id, name FROM awards WHERE achievement_key = ? AND achievement_level = ?",
            (akey, level))).fetchone()
        if prev:
            prev_name = prev["name"]
            ua = await (await conn.execute(
                "SELECT id FROM user_awards WHERE user_id = ? AND award_id = ?",
                (user_id, prev["id"]))).fetchone()
            if ua:
                await revoke_award(ua["id"])
    await conn.execute(
        "UPDATE user_achievements SET level = ?, updated_at = datetime('now') "
        "WHERE user_id = ? AND akey = ?",
        (target["level"], user_id, akey))
    await conn.commit()
    award = await (await conn.execute(
        "SELECT id FROM awards WHERE achievement_key = ? AND achievement_level = ?",
        (akey, target["level"]))).fetchone()
    if award:
        await grant_award(user_id, award["id"], granted_by=0, comment="Достижение")
    # Редкий предмет за уровень ачивки (владелец создаёт его сам): ищем по
    # имени и кладём в инвентарь. Пока предмет не создан — тихо пропускаем.
    reward_item_name = target.get("reward_item")
    if reward_item_name:
        item_row = await (await conn.execute(
            "SELECT id FROM items WHERE name = ?", (reward_item_name,))).fetchone()
        if item_row:
            await add_inventory_item(user_id, item_row["id"], 1)
    return target["level"], target["name"], prev_name


async def bump_achievement(user_id: int, akey: str, delta: int = 1):
    """Прибавить delta к прогрессу достижения; при прохождении порога выдаёт уровень.

    Возвращает (новый_уровень, название_нового_уровня, название_отобранного)
    или (None, None, None), если уровень не сменился. Игровые точки просто
    вызывают эту функцию после успешного события.
    """
    spec = ACHIEVEMENTS_DEF.get(akey)
    if not spec or delta <= 0:
        return None, None, None
    conn = await get_db()
    await conn.execute(
        "INSERT INTO user_achievements (user_id, akey, level, progress, updated_at) "
        "VALUES (?, ?, 0, ?, datetime('now')) "
        "ON CONFLICT(user_id, akey) DO UPDATE SET "
        "progress = progress + ?, updated_at = datetime('now')",
        (user_id, akey, delta, delta))
    await conn.commit()
    level, progress = await _achievement_level_progress(conn, user_id, akey)
    return await _apply_achievement_threshold(conn, user_id, akey, spec, level, progress)


async def set_achievement_progress(user_id: int, akey: str, value: int):
    """Установить прогресс с сохранением максимума (вверх от текущего).

    Нужен для «единовременных» ачивок вроде money — текущий баланс приходит
    вниз при тратах, но прогресс никогда не уменьшается.
    """
    spec = ACHIEVEMENTS_DEF.get(akey)
    if not spec or value <= 0:
        return None, None, None
    conn = await get_db()
    await conn.execute(
        "INSERT INTO user_achievements (user_id, akey, level, progress, updated_at) "
        "VALUES (?, ?, 0, ?, datetime('now')) "
        "ON CONFLICT(user_id, akey) DO UPDATE SET "
        "progress = MAX(progress, ?), updated_at = datetime('now')",
        (user_id, akey, value, value))
    await conn.commit()
    level, progress = await _achievement_level_progress(conn, user_id, akey)
    return await _apply_achievement_threshold(conn, user_id, akey, spec, level, progress)


async def get_achievement_progress(user_id: int, akey: str):
    """(level, progress) для конкретной ачивки (0, 0), если ещё не начата."""
    conn = await get_db()
    return await _achievement_level_progress(conn, user_id, akey)


async def get_achievement_level(user_id: int, akey: str) -> int:
    level, _ = await get_achievement_progress(user_id, akey)
    return level


async def get_achievement_bonus(user_id: int, akey: str, key: str) -> int:
    """Точечный бонус текущего уровня ачивки (0, если уровень не открыт)."""
    level, _ = await get_achievement_progress(user_id, akey)
    if level <= 0:
        return 0
    spec = ACHIEVEMENTS_DEF.get(akey)
    if not spec:
        return 0
    for lvl in spec["levels"]:
        if lvl["level"] == level:
            return int(lvl.get("bonus", {}).get(key, 0) or 0)
    return 0


async def get_user_achievements(user_id: int) -> list:
    """Данные для экрана «Достижения»: показываем только достижения, которые есть у пилота."""
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT akey, level, progress FROM user_achievements WHERE user_id = ?",
        (user_id,))
    rows = {r["akey"]: r for r in await cursor.fetchall()}
    result = []
    for akey, spec in ACHIEVEMENTS_DEF.items():
        r = rows.get(akey)
        if not r:
            continue
        result.append({
            "akey": akey,
            "title": spec["title"],
            "emoji": spec["emoji"],
            "metric": spec["metric"],
            "levels": spec["levels"],
            "level": r["level"],
            "progress": r["progress"],
        })
    return result


# ---------- Рецепты ----------

RECIPES_DEF = [
    {"name": "Жареный сиг", "old": "Пожарить сига", "desc": "Жареный сиг со специями: +15 HP в бою подземелья. Срок годности: 4 суток.",
     "result": "Жареный сиг", "qty": 1, "exp": "kitchen", "lvl": 1,
     "ingredients": [("Сиг", 1), ("Соль", 1)], "ap": 5, "time": 20, "rarity": 1},
    {"name": "Жареный муксун", "old": "Пожарить муксуна", "desc": "Жареный муксун со специями: +30 HP в бою подземелья. Срок годности: 4 суток.",
     "result": "Жареный муксун", "qty": 1, "exp": "kitchen", "lvl": 1,
     "ingredients": [("Муксун", 1), ("Соль", 1)], "ap": 5, "time": 20, "rarity": 1},
    {"name": "Жареный чир", "old": "Пожарить чира", "desc": "Жареный чир со специями: +45 HP в бою подземелья. Срок годности: 4 суток.",
     "result": "Жареный чир", "qty": 1, "exp": "kitchen", "lvl": 1,
     "ingredients": [("Чир", 1), ("Соль", 1)], "ap": 7, "time": 25, "rarity": 1},
    {"name": "Жареный налим", "old": "Пожарить налима", "desc": "Жареный налим со специями: +55 HP в бою подземелья. Срок годности: 4 суток.",
     "result": "Жареный налим", "qty": 1, "exp": "kitchen", "lvl": 1,
     "ingredients": [("Налим", 1), ("Соль", 1)], "ap": 8, "time": 25, "rarity": 1},
    {"name": "Жареный сом", "old": "Пожарить сома", "desc": "Жареный сом со специями и водорослями: +65 HP в бою подземелья. Срок годности: 4 суток.",
     "result": "Жареный сом", "qty": 1, "exp": "kitchen", "lvl": 1,
     "ingredients": [("Мерцающий сом", 1), ("Соль", 1), ("Кусочек водорослей", 1)], "ap": 9, "time": 30, "rarity": 1},
    {"name": "Жареный угорь", "old": "Пожарить угря", "desc": "Хрустящий жареный угорь с водорослями: +90 HP в бою подземелья. Срок годности: 4 суток.",
     "result": "Жареный угорь", "qty": 1, "exp": "kitchen", "lvl": 2,
     "ingredients": [("Искрящийся угорь", 1), ("Соль", 1), ("Кусочек водорослей", 1)], "ap": 12, "time": 40, "rarity": 2},
    {"name": "Жареная форель", "old": "Пожарить форель", "desc": "Светящаяся форель, пожаренная до золотой корочки: +140 HP в бою подземелья. Срок годности: 4 суток.",
     "result": "Жареный форель", "qty": 1, "exp": "kitchen", "lvl": 3,
     "ingredients": [("Светящаяся форель", 1), ("Соль", 1), ("Кусочек водорослей", 1)], "ap": 16, "time": 50, "rarity": 4},
    {"name": "Жареный опёнок", "old": "Пожарить опёнка", "desc": "Жареный опёнок со специями: +12 HP в бою подземелья. Срок годности: 4 суток.",
     "result": "Жареный опёнок", "qty": 1, "exp": "kitchen", "lvl": 1,
     "ingredients": [("Опёнок", 1), ("Соль", 1)], "ap": 5, "time": 20, "rarity": 1},
    {"name": "Жареный подберёзовик", "old": "Пожарить подберёзовик", "desc": "Жареный подберёзовик со специями: +18 HP в бою подземелья. Срок годности: 4 суток.",
     "result": "Жареный подберёзовик", "qty": 1, "exp": "kitchen", "lvl": 1,
     "ingredients": [("Подберёзовик", 1), ("Соль", 1)], "ap": 5, "time": 20, "rarity": 1},
    {"name": "Жареные лисички", "old": "Пожарить лисички", "desc": "Ароматные жареные лисички: +26 HP в бою подземелья. Срок годности: 4 суток.",
     "result": "Жареные лисички", "qty": 1, "exp": "kitchen", "lvl": 1,
     "ingredients": [("Лисичка", 2), ("Соль", 1)], "ap": 7, "time": 25, "rarity": 1},
    {"name": "Жареный белый гриб", "old": "Пожарить белый гриб", "desc": "Жареный белый гриб: +34 HP в бою подземелья. Срок годности: 4 суток.",
     "result": "Жареный белый гриб", "qty": 1, "exp": "kitchen", "lvl": 2,
     "ingredients": [("Белый гриб", 1), ("Соль", 1)], "ap": 8, "time": 30, "rarity": 2},
    {"name": "Жареный гиропор", "old": "Пожарить гиропор", "desc": "Редкий жареный гиропор: +48 HP в бою подземелья. Срок годности: 4 суток.",
     "result": "Жареный гиропор", "qty": 1, "exp": "kitchen", "lvl": 2,
     "ingredients": [("Гиропор", 1), ("Соль", 1)], "ap": 12, "time": 40, "rarity": 2},
    {"name": "Жареный ежовик гребенчатый", "old": "Пожарить ежовик гребенчатый", "desc": "Деликатес из самого редкого гриба леса: +70 HP в бою подземелья. Срок годности: 4 суток.",
     "result": "Жареный ежовик гребенчатый", "qty": 1, "exp": "kitchen", "lvl": 3,
     "ingredients": [("Ежовик гребенчатый", 1), ("Соль", 1)], "ap": 16, "time": 50, "rarity": 4},
    {"name": "Жареное мясо кабана", "old": "Пожарить мясо кабана", "desc": "Жаренное на костре мясо кабана: +30 HP в бою подземелья. Срок годности: 4 суток.",
     "result": "Жареное мясо кабана", "qty": 1, "exp": "kitchen", "lvl": 1,
     "ingredients": [("Мясо кабана", 1), ("Соль", 1)], "ap": 6, "time": 25, "rarity": 2},
    {"name": "Жареное мясо моллюска", "old": "Пожарить мясо моллюска", "desc": "Жареное мясо мутировавшего моллюска: +26 HP в бою подземелья. Срок годности: 4 суток.",
     "result": "Жареное мясо моллюска", "qty": 1, "exp": "kitchen", "lvl": 2,
     "ingredients": [("Мясо моллюска", 1), ("Соль", 1)], "ap": 8, "time": 25, "rarity": 3},
    {"name": "Сварить яд", "desc": "Мутное зелье из ядовитых лесных грибов: основа для улучшения оружия кузнецом.",
     "result": "Бутылочка с ядом", "qty": 1, "exp": "kitchen", "lvl": 2,
     "ingredients": [("Мухомор", 2), ("Бледная поганка", 1), ("Бутылка чистой воды", 1)], "ap": 10, "time": 30, "rarity": 2},
    {"name": "Комбинированная наживка", "desc": "Собирается на верстаке. +30% к шансу улова.",
     "result": "Комбинированная наживка", "qty": 1, "exp": "workbench", "lvl": 1,
     "ingredients": [("Лапка паука", 1), ("Черви", 1)], "ap": 5, "time": 20, "rarity": 1},
    {"name": "Пара сапог", "desc": "Сборка обуви на верстаке: два старых сапога со дна, "
     "паутина паука, клей и набор игл. Броня ног: 2.",
     "result": "Пара сапог", "qty": 1, "exp": "workbench", "lvl": 1,
     "ingredients": [("Старый сапог", 2), ("Паутина паука", 1), ("Клей", 1), ("Набор игл", 1)],
     "ap": 6, "time": 45, "rarity": 2},
    {"name": "Малая настойка здоровья", "desc": "Восстанавливает 20 HP в бою подземелья.",
     "result": "Малая настойка здоровья", "qty": 1, "exp": "kitchen", "lvl": 2,
     "ingredients": [("Бутылка чистой воды", 1), ("Осколок кристалла", 1)], "ap": 10, "time": 30, "rarity": 1},
    {"name": "Энергетик", "desc": "+50 ОД при использовании.",
     "result": "Энергетик", "qty": 1, "exp": "kitchen", "lvl": 3,
     "ingredients": [("Бутылка чистой воды", 1), ("Кусочек водорослей", 4)], "ap": 15, "time": 45, "rarity": 1},
    {"name": "Улучшенная настойка здоровья", "desc": "Восстанавливает 50 HP в бою подземелья. Редкий рецепт.",
     "result": "Улучшенная настойка здоровья", "qty": 1, "exp": "kitchen", "lvl": 3,
     "ingredients": [("Яблоко", 1), ("Бутылка чистой воды", 1), ("Осколок кристалла", 1), ("Кусочек водорослей", 2)],
     "ap": 20, "time": 60, "rarity": 3},
    {"name": "Рыбный пирог", "desc": "Праздничный пирог из пяти карасей, сига и муксуна: "
     "+80 HP в бою подземелья и регенерация 60% от лечения следующие 3 хода. Срок годности 4 суток.",
     "result": "Рыбный пирог", "qty": 1, "exp": "kitchen", "lvl": 2,
     "ingredients": [("Карась", 5), ("Сиг", 1), ("Муксун", 1), ("Соль", 1), ("Мука", 1)],
     "ap": 8, "time": 40, "rarity": 3},
]


async def ensure_recipes():
    """Идемпотентно засевает рецепты и синхронизирует уже существующие.

    Рецепты обновляются по названию: если строка уже есть — перезаписываем состав
    и описание, иначе добавляем новый. Это нужно, чтобы смена рецептуры
    (например, добавление соли в жареную рыбу) доезжала до существующих БД.

    Переименование (ключ 'old' у рецепта) меняет name у существующей строки
    В СИЛУ id, а не добавляет новую строку. Иначе игроки потеряли бы выученные
    рецепты (user_recipes ссылается на id), а купленные предметы-рецепты со
    старым названием стали бы мёртвыми: learn_recipe_from_item() ищет рецепт
    по имени и отвечает «Рецепт не найден».
    """
    conn = await get_db()
    changed = False
    for r in RECIPES_DEF:
        old = r.get('old')
        if old:
            old_row = await (await conn.execute(
                "SELECT id FROM recipes WHERE name = ? AND required_expansion = ? "
                "AND required_level = ?", (old, r['exp'], r['lvl']))).fetchone()
            if old_row:
                new_row = await (await conn.execute(
                    "SELECT id FROM recipes WHERE name = ? AND required_expansion = ? "
                    "AND required_level = ?", (r['name'], r['exp'], r['lvl']))).fetchone()
                if new_row:
                    # Целевое имя уже занято (напр. товар продавался, а рецепт назывался
                    # иначе): переносим выученное на актуальную строку, старую гасим,
                    # чтобы в базе не осталось двух рецептов с одним названием.
                    await conn.execute(
                        "INSERT OR IGNORE INTO user_recipes (user_id, recipe_id) "
                        "SELECT user_id, ? FROM user_recipes WHERE recipe_id = ?",
                        (new_row['id'], old_row['id']))
                    await conn.execute(
                        "UPDATE recipes SET is_available = 0 WHERE id = ?", (old_row['id'],))
                else:
                    await conn.execute(
                        "UPDATE recipes SET name = ? WHERE id = ?",
                        (r['name'], old_row['id']))
                changed = True
        cursor = await conn.execute(
            "SELECT id FROM recipes WHERE name = ? AND required_expansion = ? AND required_level = ?",
            (r['name'], r['exp'], r['lvl']))
        row = await cursor.fetchone()
        ingredients = json.dumps(r['ingredients'], ensure_ascii=False)
        if row:
            await conn.execute(
                "UPDATE recipes SET description = ?, result_item_name = ?, result_quantity = ?, "
                "ingredients = ?, ap_cost = ?, production_time = ?, rarity = ? WHERE id = ?",
                (r['desc'], r['result'], r.get('qty', 1), ingredients,
                 r['ap'], r['time'], r.get('rarity', 1), row['id']))
            changed = True
        else:
            await conn.execute(
                "INSERT INTO recipes (name, description, result_item_name, result_quantity, "
                "required_expansion, required_level, ingredients, ap_cost, production_time, rarity) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (r['name'], r['desc'], r['result'], r.get('qty', 1), r['exp'], r['lvl'],
                 ingredients, r['ap'], r['time'], r.get('rarity', 1))
            )
            changed = True
    if changed:
        await conn.commit()
    return changed


async def get_recipes(expansion: str = None, level: int = None):
    """Доступные рецепты. Если задан уровень — рецепты, открываемые расширением этого уровня."""
    conn = await get_db()
    q = "SELECT * FROM recipes WHERE is_available = 1"
    params = []
    if expansion:
        q += " AND required_expansion = ?"
        params.append(expansion)
        if level is not None:
            q += " AND required_level <= ?"
            params.append(level)
    q += " ORDER BY required_level, rarity, id"
    cursor = await conn.execute(q, params)
    return await cursor.fetchall()


async def get_recipe(recipe_id: int):
    conn = await get_db()
    cursor = await conn.execute("SELECT * FROM recipes WHERE id = ?", (recipe_id,))
    return await cursor.fetchone()


# ---------- Менеджер рецептов (v0.22.13): создание/правка/удаление ----------
# Рецепты, созданные в админ-панели, лежат в той же таблице recipes, но НЕ
# должны перезатираться ensure_recipes(): она работает только по RECIPES_DEF
# (по имени+расширению+уровню), поэтому менеджерные строки она не трогает.
# Товар-рецепт «Рецепт: <название>» вносится в лавку напрямую (sync-версия
# ensure_recipe_shop_items для одной строки).

async def list_recipes_for_admin() -> list:
    """Все рецепты (включая скрытые), для админ-менеджера рецептов."""
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT * FROM recipes ORDER BY required_expansion, required_level, id")
    return await cursor.fetchall()


def _norm_recipe_ingredients(ingredients):
    """Приводит ингредиенты рецепта к списку пар [name, qty].

    Крафт (housing.py) читает ingredients как `for ing_name, qty in ...` —
    пары, как в RECIPES_DEF. Менеджер рецептов хранит словари
    {'name': ..., 'qty': ...} — здесь они выравниваются к общему формату.
    """
    norm = []
    for ing in ingredients:
        if isinstance(ing, dict):
            norm.append([ing["name"], ing["qty"]])
        else:
            norm.append([ing[0], ing[1]])
    return norm


async def upsert_recipe(name: str, desc: str, result_item_name: str,
                        result_quantity: int, required_expansion: str,
                        required_level: int, ingredients: list,
                        ap_cost: int, production_time: int, rarity: int,
                        recipe_id: int = None) -> int:
    """Создаёт новый рецепт или обновляет существующий по id. Возвращает id."""
    conn = await get_db()
    ing_json = json.dumps(list(_norm_recipe_ingredients(ingredients)), ensure_ascii=False)
    if recipe_id:
        row = await (await conn.execute(
            "SELECT id FROM recipes WHERE id = ?", (recipe_id,))).fetchone()
        if row:
            await conn.execute(
                "UPDATE recipes SET name = ?, description = ?, result_item_name = ?, "
                "result_quantity = ?, required_expansion = ?, required_level = ?, "
                "ingredients = ?, ap_cost = ?, production_time = ?, rarity = ?, "
                "is_available = 1 WHERE id = ?",
                (name, desc, result_item_name, result_quantity, required_expansion,
                 required_level, ing_json, ap_cost, production_time, rarity, recipe_id))
            await conn.commit()
            return recipe_id
    cursor = await conn.execute(
        "INSERT INTO recipes (name, description, result_item_name, result_quantity, "
        "required_expansion, required_level, ingredients, ap_cost, production_time, "
        "rarity, is_available) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)",
        (name, desc, result_item_name, result_quantity, required_expansion,
         required_level, ing_json, ap_cost, production_time, rarity))
    await conn.commit()
    return cursor.lastrowid


async def ensure_recipe_shop_item(recipe: dict, price: int = None):
    """Синхронизирует товар-рецепт «Рецепт: <name>» с рецептом (менеджер).

    Создаёт предмет категории 'recipes', если его нет, иначе обновляет цену/
    описание/редкость и включает в магазине. Цена при создании — из
    RECIPE_ITEM_PRICES (менеджерные рецепты получают дефолт 100), при обновлении
    сохраняется цена, уже стоящая на товаре, если явно не передана `price` —
    иначе админская настройка цены терялась бы при правке других полей.
    """
    item_name = RECIPE_ITEM_PREFIX + recipe['name']
    desc = (f"📜 Обучает рецепту: {recipe['name']}.\n"
            f"{recipe['description'] or ''}\n"
            f"Используй из инвентаря, чтобы выучить рецепт и крафтить в жилье.")
    conn = await get_db()
    item = await get_item_by_name(item_name)
    if price is None:
        price = item['price'] if item else RECIPE_ITEM_PRICES.get(recipe['name'], 100)
    if item:
        await conn.execute(
            "UPDATE items SET description = ?, price = ?, sell_price = ?, rarity = ?, "
            "category = 'recipes', is_available = 1 WHERE id = ?",
            (desc, price, price // 2, recipe.get('rarity', 1), item['id']))
    else:
        await add_item(item_name, desc, price, price // 2, recipe.get('rarity', 1),
                       'recipes', -1, 0)
    await conn.commit()


async def find_recipe(name: str, required_expansion: str,
                      required_level: int) -> dict:
    """Строка рецепта по имени+расширению+уровню (проверка дубликатов)."""
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT id, is_available FROM recipes WHERE name = ? "
        "AND required_expansion = ? AND required_level = ?",
        (name, required_expansion, required_level))
    return await cursor.fetchone()


async def set_recipe_visible(recipe_id: int, visible: bool) -> bool:
    """Показать/скрыть рецепт и его товар «Рецепт: …» в лавке (менеджер)."""
    conn = await get_db()
    recipe = await get_recipe(recipe_id)
    if not recipe:
        return False
    flag = 1 if visible else 0
    await conn.execute(
        "UPDATE recipes SET is_available = ? WHERE id = ?", (flag, recipe_id))
    await conn.execute(
        "UPDATE items SET is_available = ? WHERE name = ? AND category = 'recipes'",
        (flag, RECIPE_ITEM_PREFIX + recipe['name']))
    await conn.commit()
    return True


async def delete_recipe(recipe_id: int) -> bool:
    """Удаление рецепта менеджером: гасит рецепт и товар «Рецепт: …» в лавке.

    Строка остаётся в базе (is_available = 0), чтобы не терять выученные
    записи игроков (user_recipes ссылается на id). Пилоты, уже выучившие
    рецепт, теряют доступ к крафту — это и есть «удаление» из игры.
    """
    conn = await get_db()
    recipe = await get_recipe(recipe_id)
    if not recipe:
        return False
    await conn.execute(
        "UPDATE recipes SET is_available = 0 WHERE id = ?", (recipe_id,))
    await conn.execute(
        "UPDATE items SET is_available = 0 WHERE name = ? AND category = 'recipes'",
        (RECIPE_ITEM_PREFIX + recipe['name'],))
    await conn.commit()
    return True


# ---------- Книги рецептов (менеджер) ----------

async def set_recipe_book(book_item_id: int, recipe_ids) -> int:
    """Привязывает предмет-книгу к набору рецептов (перезаписывает набор)."""
    conn = await get_db()
    await conn.execute(
        "DELETE FROM recipe_book_items WHERE book_item_id = ?", (book_item_id,))
    seen = []
    for rid in recipe_ids:
        rid = int(rid)
        if rid in seen:
            continue
        seen.append(rid)
        await conn.execute(
            "INSERT OR IGNORE INTO recipe_book_items (book_item_id, recipe_id) "
            "VALUES (?, ?)", (book_item_id, rid))
    await conn.commit()
    return len(seen)


async def get_recipe_book_recipes(book_item_id: int) -> list:
    """Рецепты, которые открывает книга (включая скрытые — фильтрует вызывающий)."""
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT r.* FROM recipe_book_items b JOIN recipes r ON r.id = b.recipe_id "
        "WHERE b.book_item_id = ? ORDER BY r.required_expansion, r.required_level, r.name",
        (book_item_id,))
    return await cursor.fetchall()


async def list_recipe_books() -> list:
    """Все предметы-книги (включая скрытые) с числом рецептов — для админ-списка."""
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT i.*, COUNT(b.recipe_id) AS recipes_count FROM items i "
        "JOIN recipe_book_items b ON b.book_item_id = i.id "
        "GROUP BY i.id ORDER BY i.name")
    return await cursor.fetchall()


async def set_recipe_book_visible(book_item_id: int, visible: bool) -> bool:
    conn = await get_db()
    exists = await (await conn.execute(
        "SELECT 1 FROM recipe_book_items WHERE book_item_id = ?", (book_item_id,))).fetchone()
    if not exists:
        return False
    await conn.execute(
        "UPDATE items SET is_available = ? WHERE id = ?",
        (1 if visible else 0, book_item_id))
    await conn.commit()
    return True


async def delete_recipe_book(book_item_id: int) -> bool:
    """Скрывает книгу из лавки; связка с рецептами остаётся (мягкое удаление)."""
    conn = await get_db()
    exists = await (await conn.execute(
        "SELECT 1 FROM recipe_book_items WHERE book_item_id = ?", (book_item_id,))).fetchone()
    if not exists:
        return False
    await conn.execute(
        "UPDATE items SET is_available = 0 WHERE id = ?", (book_item_id,))
    await conn.commit()
    return True


# ---------- Учёт и списание ингредиентов (в т.ч. уловов рыбы) ----------

async def get_ingredient_map(user_id: int) -> dict:
    """Название → количество: инвентарь + непроданные уловы рыбы.

    Рыба ловится в таблицу fish_catches, а не в items/inventory, поэтому
    рецепты кухни не могли «видеть» улов. Объединяем обе базы.
    """
    counts: dict = {}
    inv = [dict(i) for i in await get_inventory(user_id)]
    now = time.time()
    for i in inv:
        # Срок годности: протухшее сырьё в рецепты не идёт (например, купленная рыба).
        exp = i.get('expires_at')
        try:
            expi = float(exp) if exp else None
        except (TypeError, ValueError):
            expi = None
        if expi and expi <= now:
            continue
        counts[i['name']] = counts.get(i['name'], 0) + i['quantity']
    catches = await get_fish_catches(user_id)
    for c in catches:
        counts[c['name']] = counts.get(c['name'], 0) + 1
    return counts


async def remove_fish_catches_by_name(user_id: int, name: str, qty: int) -> bool:
    """Списывает qty непроданных уловов рыбы по названию. True — если хватило."""
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT fc.id FROM fish_catches fc JOIN items i ON i.id = fc.item_id "
        "WHERE fc.user_id = ? AND i.name = ? AND fc.sold_at IS NULL "
        "AND (fc.expires_at IS NULL OR CAST(fc.expires_at AS REAL) > ?) "
        "ORDER BY fc.id LIMIT ?",
        (user_id, name, time.time(), qty)
    )
    rows = await cursor.fetchall()
    if len(rows) < qty:
        return False
    ids = [r['id'] for r in rows]
    await conn.execute(
        f"DELETE FROM fish_catches WHERE id IN ({','.join('?' * len(ids))})", ids
    )
    await conn.commit()
    return True


async def consume_ingredient(user_id: int, name: str, qty: int) -> bool:
    """Списывает ингредиент по названию: сначала инвентарь, затем уловы рыбы."""
    item = await get_item_by_name(name)
    remaining = qty
    if item:
        inv = await get_inventory_item(user_id, item['id'])
        if inv and inv['quantity'] > 0:
            from_inv = min(remaining, inv['quantity'])
            if not await remove_inventory_item(user_id, item['id'], from_inv):
                return False
            remaining -= from_inv
    if remaining > 0:
        return await remove_fish_catches_by_name(user_id, name, remaining)
    return True


# ---------- Порча жареной рыбы ----------

async def process_food_expiry(user_id: int) -> int:
    """Конвертирует протухшую жареную рыбу в испорченную. Возвращает число превращённых."""
    conn = await get_db()
    now = time.time()
    # Срок хранится в секундах с эпохи (эпоха = int). Возможен и строковый вариант из legacy.
    cursor = await conn.execute(
        "SELECT inv.id, inv.item_id, inv.quantity, inv.expires_at, i.name FROM inventory inv "
        "JOIN items i ON inv.item_id = i.id "
        "WHERE inv.user_id = ? AND inv.expires_at IS NOT NULL AND inv.expires_at != ''",
        (user_id,)
    )
    rows = await cursor.fetchall()
    converted = 0
    for row in rows:
        try:
            exp = float(row['expires_at'])
        except (TypeError, ValueError):
            continue
        if exp >= now:
            continue
        spoiled_name = "Испорченный " + row['name'].replace("Жареный ", "", 1)
        spoiled = await get_item_by_name(spoiled_name)
        await conn.execute("DELETE FROM inventory WHERE id = ?", (row['id'],))
        if spoiled:
            await add_inventory_item(user_id, spoiled['id'], row['quantity'])
        converted += row['quantity']
    if converted:
        await conn.commit()
    return converted


async def get_inventory_with_expiry(user_id: int):
    """Инвентарь с данными о сроке годности (для карточек предметов)."""
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT i.*, inv.quantity, inv.expires_at FROM inventory inv "
        "JOIN items i ON inv.item_id = i.id "
        "WHERE inv.user_id = ? AND inv.quantity > 0 "
        "ORDER BY i.category, i.rarity DESC",
        (user_id,)
    )
    return await cursor.fetchall()


# ---------- Растение (кадка) ----------

async def plant_seed(user_id: int, slot_index: int, seed_item_id: int):
    """Сажает семечко в пустую кадку. Возвращает (получилось, сообщение)."""
    seed = await get_item(seed_item_id)
    if not seed or seed['category'] != 'seeds':
        return False, "Это не семечко."
    inv = await get_inventory_item(user_id, seed_item_id)
    if not inv or inv['quantity'] < 1:
        return False, "Семечка нет в инвентаре."
    now = time.time()
    seed_plant_name = seed.get('plant_name') or PLANT_NAMES.get(seed['name'], seed['name'])
    plant_data = {
        "seed": seed['name'],
        "plant_name": seed_plant_name,
        "stage_started_at": now,
        "last_harvest_at": None,
        "fruits": 0,
    }
    await set_housing_slot(user_id, slot_index, "plant_pot", 1, plant_data)
    await remove_inventory_item(user_id, seed_item_id, 1)
    return True, seed['name']


FRUIT_MAX = 5


def plant_stage_info(data: dict, now: float):
    """Данные о текущем состоянии растения: стадия, накопленные плоды, время до следующего плода.

    Логика плодов: созревшее дерево даёт по 1 плоду каждые 2 суток, максимум 5.
    Пока плоды не собраны — таймер стоит (новые плоды не появляются).
    data: {seed, stage_started_at (epoch), last_harvest_at (epoch|None)}
    """
    data = dict(data or {})
    started = float(data.get('stage_started_at') or now)
    elapsed = max(0.0, now - started)

    boundaries = []
    cum = 0
    for _name, days in PLANT_STAGES[:-1]:
        cum += days * 86400
        boundaries.append(cum)

    stage = 0
    for i, b in enumerate(boundaries, start=1):
        if elapsed >= b:
            stage = i
        else:
            break

    fruits = 0
    next_in = 0.0

    if stage < 4:
        next_in = boundaries[stage] - elapsed
    else:
        t4 = started + boundaries[3]
        base = float(data.get('last_harvest_at') or t4)
        interval = FRUIT_EVERY_DAYS * 86400
        since_base = max(0.0, now - base)
        fruits = min(FRUIT_MAX, int(since_base // interval))
        if fruits >= FRUIT_MAX:
            next_in = 0.0  # кап 5 — ждём сбора, таймер не идёт
        else:
            next_in = interval - (since_base % interval)

    return {
        "stage": stage,
        "next_in": max(0.0, next_in),
        "fruit_ready": fruits > 0,
        "fruits": fruits,
        "data": data,
    }


async def harvest_plant(user_id: int, slot_index: int):
    """Собирает ВСЕ накопленные плоды (макс. 5). Возвращает (получилось, сообщение)."""
    slots = await get_housing_slots(user_id)
    slot = slots.get(slot_index)
    if not slot or slot.get('expansion_type') != 'plant_pot':
        return False, "Кадки с растением здесь нет."
    data = json.loads(slot.get('plant_data') or '{}')
    info = plant_stage_info(data, time.time())
    fruits = info['fruits']
    if fruits <= 0:
        return False, "Плодов ещё нет."
    fruit_name = plant_harvest_name(data.get('seed'))
    fruit = await get_item_by_name(fruit_name)
    if not fruit:
        return False, f"«{fruit_name}» не настроено в базе. Сообщи хранителю."
    await add_inventory_item(user_id, fruit['id'], fruits)
    # Таймер обновляется только при сборе
    data['last_harvest_at'] = time.time()
    data.pop('fruits', None)
    data.pop('next_fruit_at', None)
    await set_housing_slot(user_id, slot_index, "plant_pot", 1, data)
    return True, (fruit, fruits)


# ---------- Клановый сад (Фаза 5) ----------

def clan_garden_plots(level: int | None) -> int:
    """Сколько грядок даёт сад этого уровня (по умолчанию — как 1-й уровень)."""
    plots = getattr(config, "CLAN_GARDEN_PLOTS", {}) or {}
    return int(plots.get(int(level or 1)) or plots.get(1) or 2)


async def get_clan_garden(clan_id: int) -> dict:
    """Грядки клана: plot_index → строка (пустых грядок в таблице нет)."""
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT * FROM clan_garden WHERE clan_id = ? ORDER BY plot_index",
        (clan_id,))
    rows = await cursor.fetchall()
    return {int(r["plot_index"]): dict(r) for r in rows}


def clan_plot_info(plot, now: float | None = None) -> dict:
    """Состояние растения на грядке (стадии/плоды — те же, что в жилье)."""
    if not plot:
        return plant_stage_info({}, now or time.time())
    now = now or time.time()
    data = {
        "seed": plot.get("seed_name"),
        "plant_name": plot.get("plant_name"),
        "stage_started_at": float(plot.get("stage_started_at") or now),
        "last_harvest_at": plot.get("last_harvest_at"),
    }
    info = plant_stage_info(data, now)
    info["data"] = data
    return info


async def plant_clan_seed(clan_id: int, user_id: int, plot_index: int,
                          seed_item_id: int, max_plots: int):
    """Посадка семечка на общую грядку (семя — из личного инвентаря).

    Возвращает (получилось, сообщение). Грядка запоминает, кто посадил.
    """
    plot_index = int(plot_index or 0)
    if plot_index < 1 or plot_index > int(max_plots or 0):
        return False, "Такой грядки в саду нет."
    seed = await get_item(seed_item_id)
    if not seed or seed.get("category") != "seeds":
        return False, "Это не семечко."
    inv = await get_inventory_item(user_id, seed_item_id)
    if not inv or int(inv["quantity"] or 0) < 1:
        return False, "Семечка нет в инвентаре."

    plant_name = seed.get("plant_name") or PLANT_NAMES.get(seed["name"], seed["name"])
    conn = await get_db()
    cursor = await conn.execute(
        "INSERT OR IGNORE INTO clan_garden "
        "(clan_id, plot_index, seed_name, plant_name, planted_by, stage_started_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (clan_id, plot_index, seed["name"], plant_name, user_id, time.time()))
    await conn.commit()
    if cursor.rowcount != 1:
        return False, "Грядка уже занята."
    if not await remove_inventory_item(user_id, seed_item_id, 1):
        # Откат: не оставляем «призрак» посадки без списанного семечка.
        await conn.execute(
            "DELETE FROM clan_garden WHERE clan_id = ? AND plot_index = ?",
            (clan_id, plot_index))
        await conn.commit()
        return False, "Не удалось списать семечко."
    return True, seed["name"]


async def harvest_clan_plot(clan_id: int, plot_index: int):
    """Сбор плодов с одной грядки в клановый склад.

    Возвращает (успех, данные {name, qty} или текст ошибки). Оптимистичный
    лок по `last_harvest_at` не даёт собрать один и тот же урожай дважды.
    """
    garden = await get_clan_garden(clan_id)
    plot = garden.get(int(plot_index or 0))
    if not plot:
        return False, "Грядка пуста."

    now = time.time()
    info = clan_plot_info(plot, now)
    fruits = int(info["fruits"])
    if fruits <= 0:
        return False, "Плодов ещё нет."

    fruit_name = plant_harvest_name(plot.get("seed_name"))
    fruit = await get_item_by_name(fruit_name)
    if not fruit:
        return False, f"«{fruit_name}» не настроено в базе. Сообщи хранителю."

    prev = plot.get("last_harvest_at")
    conn = await get_db()
    if prev is None:
        cursor = await conn.execute(
            "UPDATE clan_garden SET last_harvest_at = ? "
            "WHERE clan_id = ? AND plot_index = ? AND last_harvest_at IS NULL",
            (now, clan_id, int(plot_index)))
    else:
        cursor = await conn.execute(
            "UPDATE clan_garden SET last_harvest_at = ? "
            "WHERE clan_id = ? AND plot_index = ? AND last_harvest_at = ?",
            (now, clan_id, int(plot_index), prev))
    await conn.commit()
    if cursor.rowcount != 1:
        return False, "Урожай уже собрали."

    await add_clan_storage(clan_id, fruit["id"], fruits)
    return True, {"name": fruit["name"], "qty": fruits, "item_id": fruit["id"]}


# ---------- Фонтан (восстановление ОД раз в сутки) ----------

async def can_use_fountain(user_id: int) -> bool:
    user = await get_user(user_id)
    if not user:
        return False
    today = today_report_day()
    return not (user.get('fountain_used_day') == today and (user.get('fountain_used_today') or 0) >= 1)


async def mark_fountain_used(user_id: int):
    today = today_report_day()
    user = await get_user(user_id)
    # Обе ветки раньше возвращали 1: счётчик не рос, если фонтан в один день
    # почему-то обошёл can_use_fountain. Считаем честно, ограничение — 1/сут.
    used = ((user.get('fountain_used_today') or 0) + 1) if user and user.get('fountain_used_day') == today else 1
    await update_user(user_id, fountain_used_day=today, fountain_used_today=used)


# ---------- Душевая (восстановление ОД раз в сутки) ----------

async def can_use_shower(user_id: int) -> bool:
    user = await get_user(user_id)
    if not user:
        return False
    today = today_report_day()
    return not (user.get('shower_used_day') == today and (user.get('shower_used_today') or 0) >= 1)


async def mark_shower_used(user_id: int):
    today = today_report_day()
    user = await get_user(user_id)
    used = ((user.get('shower_used_today') or 0) + 1) if user and user.get('shower_used_day') == today else 1
    await update_user(user_id, shower_used_day=today, shower_used_today=used)


# ============ ЛАМПА КРУГОВОРОТА (Ф4б: генератор в личном жилье) ============

async def has_lantern_installed(user_id: int) -> bool:
    """Лампа Круговорота стоит в личном жильё (расширение 'lantern')."""
    slots = await get_housing_slots(user_id)
    return any((s or {}).get('expansion_type') == 'lantern' for s in slots.values())


async def can_meditate_lantern(user_id: int) -> bool:
    """Медитация у Лампы — раз в сутки (независимо от душа/фонтана)."""
    user = await get_user(user_id)
    if not user:
        return False
    return user.get('lantern_medit_day') != today_report_day()


async def mark_lantern_meditated(user_id: int):
    await update_user(user_id, lantern_medit_day=today_report_day())


async def use_lantern_meditation(user_id: int) -> int:
    """🪔 Медитация: +AP раз в сутки. Возвращает сколько ОД начислено (0 — уже сегодня)."""
    if not await has_lantern_installed(user_id):
        return 0
    if not await can_meditate_lantern(user_id):
        return 0
    ap = int(getattr(config, "FIRE_LANTERN_MEDIT_AP", 20) or 20)
    await mark_lantern_meditated(user_id)
    await add_ap(user_id, ap, reason="Лампа Круговорота: медитация")
    await log_activity(user_id, "firelab", f"Медитация у Лампы: +{ap} ОД")
    return ap


async def set_lantern_amber_next(user_id: int, ts: float | None = None):
    """Точка следующего Пламени Памяти (unix ts). None — не стоит (новая Лампа)."""
    if ts is None:
        from datetime import timedelta
        ts = (datetime.now(MOSCOW_TZ)
              + timedelta(days=int(getattr(config, "FIRE_LANTERN_AMBER_DAYS", 7) or 7))
              ).timestamp()
    await update_user(user_id, lantern_amber_at=str(int(ts)))


async def get_lantern_amber_at(user_id: int) -> float | None:
    """unix ts следующего янтаря (или None, если таймер не начат)."""
    user = await get_user(user_id)
    raw = (user or {}).get('lantern_amber_at')
    if not raw:
        return None
    try:
        return float(raw)
    except (TypeError, ValueError):
        return None


async def grant_lantern_amber_if_due(user_id: int) -> int:
    """Если Лампа стоит и время пришло — Пламя Памяти в инвентарь (+1 шт.

    Возвращает количество янтарей, начисленных сейчас (0 — не пора).
    """
    from utils.helpers import MOSCOW_TZ
    if not await has_lantern_installed(user_id):
        return 0
    granted = 0
    amber = await get_item_by_name(
        getattr(config, "FIRE_AMBER_NAME", "Пламя Памяти"))
    if not amber:
        return 0
    ts = await get_lantern_amber_at(user_id)
    if ts is None:
        await set_lantern_amber_next(user_id)
        return 0
    now = datetime.now(MOSCOW_TZ).timestamp()
    days = int(getattr(config, "FIRE_LANTERN_AMBER_DAYS", 7) or 7)
    step_ts = days * 86400
    while now >= ts:
        await add_inventory_item(user_id, amber['id'], 1)
        granted += 1
        await log_activity(user_id, "firelab", "Пламя Памяти из Лампы (+1 янтарь)")
        ts += step_ts
    if granted:
        await update_user(user_id, lantern_amber_at=str(int(ts)))
    return granted


async def get_lantern_owners() -> list[int]:
    """Все пилоты с установленной Лампой (для ежедневного цикла)."""
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT DISTINCT user_id FROM housing_slots WHERE expansion_type = 'lantern'")
    return [int(r['user_id']) for r in await cursor.fetchall()]


# ============ Картинки праздника (админ-менеджер, file_id) ============

FIRE_PHOTO_KEYS = ("entry", "fork", "well", "tree")

FIRE_PHOTO_LABELS = {
    "entry": "🚪 Вход в Лабиринт",
    "fork": "🔀 Развилка (выбор пути)",
    "well": "🪣 Колодец",
    "tree": "🌳 Древо Огня (комната)",
}


async def get_fire_photo(key: str) -> str | None:
    """file_id картинки праздника из Картинки-менеджера (или None)."""
    conn = await get_db()
    cur = await conn.execute(
        "SELECT value FROM settings WHERE key = ?", (f"fire_photo:{key}",))
    row = await cur.fetchone()
    return (row['value'] or None) if row else None


async def set_fire_photo(key: str, file_id: str | None):
    """Задать (file_id) или убрать (None) картинку точки праздника."""
    conn = await get_db()
    skey = f"fire_photo:{key}"
    if file_id is None:
        await conn.execute("DELETE FROM settings WHERE key = ?", (skey,))
    else:
        await conn.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (skey, file_id))
    await conn.commit()


# ============ Сувенир праздника туристу (разово, бесплатно) ============

async def grant_fire_souvenir(user_id: int) -> bool:
    """Разовый бесплатный леденец туристу у входа в Лабиринт.

    Возвращает True, если сувенир выдан сейчас (первый раз); False — уже был.
    Отметка хранится в таблице fire_souvenirs (user_id PK).
    """
    conn = await get_db()
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS fire_souvenirs (
            user_id INTEGER PRIMARY KEY,
            granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur = await conn.execute(
        "SELECT 1 FROM fire_souvenirs WHERE user_id = ?", (user_id,))
    if await cur.fetchone():
        return False
    await conn.execute(
        "INSERT OR IGNORE INTO fire_souvenirs (user_id) VALUES (?)", (user_id,))
    await conn.commit()
    return True


# ============ ДРЕВО ПЛАМЕННОГО КРУГОВОРОТА (клановое расширение 'tree') ============

async def count_clan_lanterns(clan_id: int) -> int:
    """Сколько чланов клана имеют Лампу Круговорота (в инвентаре, qty>0)."""
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT id FROM items WHERE name = ?",
        (getattr(config, "FIRE_LANTERN_NAME", "Лампа Круговорота"),))
    lamp = await cursor.fetchone()
    if not lamp:
        return 0
    cursor = await conn.execute("""
        SELECT COUNT(DISTINCT cm.user_id) AS c
        FROM clan_members cm
        JOIN inventory i ON i.user_id = cm.user_id AND i.item_id = ? AND i.quantity > 0
        WHERE cm.clan_id = ?
    """, (lamp['id'], clan_id))
    row = await cursor.fetchone()
    return int(row['c'] or 0)


FIRE_TREE_MEDIT_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS clan_tree_medit (
        clan_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        medit_day TEXT NOT NULL DEFAULT '',
        PRIMARY KEY (clan_id, user_id)
    )
"""


async def can_meditate_clan_tree(clan_id: int, user_id: int) -> bool:
    """Медитация у Древа — раз в сутки у каждого члена (в доп. к домашней Лампе)."""
    conn = await get_db()
    today = today_report_day()
    await conn.execute(FIRE_TREE_MEDIT_TABLE_SQL)
    cur = await conn.execute(
        "SELECT medit_day FROM clan_tree_medit WHERE clan_id = ? AND user_id = ?",
        (clan_id, user_id))
    row = await cur.fetchone()
    return not (row and row['medit_day'] == today)


async def get_clan_tree_medit_day(clan_id: int, user_id: int) -> str | None:
    """Последний день медитации у Древа (для подсказки «приходи завтра»)."""
    conn = await get_db()
    await conn.execute(FIRE_TREE_MEDIT_TABLE_SQL)
    cur = await conn.execute(
        "SELECT medit_day FROM clan_tree_medit WHERE clan_id = ? AND user_id = ?",
        (clan_id, user_id))
    row = await cur.fetchone()
    return row['medit_day'] if row else None


async def use_clan_tree_meditation(clan_id: int, user_id: int) -> int:
    """🧘 Медитация у Древа: +AP раз в сутки (у каждого члена своя отметка).

    Возвращает сколько ОД начислено (0 — уже сегодня).
    """
    if not await can_meditate_clan_tree(clan_id, user_id):
        return 0
    ap = int(getattr(config, "FIRE_TREE_CLAN_MEDIT_AP", 20) or 20)
    conn = await get_db()
    await conn.execute(FIRE_TREE_MEDIT_TABLE_SQL)
    await conn.execute(
        "INSERT INTO clan_tree_medit (clan_id, user_id, medit_day) VALUES (?, ?, ?) "
        "ON CONFLICT(clan_id, user_id) DO UPDATE SET medit_day = ?",
        (clan_id, user_id, today_report_day(), today_report_day()))
    await conn.commit()
    await add_ap(user_id, ap, reason="Древо Круговорота: медитация")
    await log_activity(user_id, "firelab",
                       f"Медитация у Древа клана #{clan_id}: +{ap} ОД")
    return ap


async def set_clan_tree_essence_next(clan_id: int, ts: float | None = None):
    """Точка следующей Эссенции Памяти (unix ts); старт — с установки Древа."""
    if ts is None:
        ts = (datetime.now(MOSCOW_TZ)
              + timedelta(days=int(getattr(config, "FIRE_TREE_CLAN_ESSENCE_DAYS", 30) or 30))
              ).timestamp()
    await update_clan(clan_id, tree_amber_at=str(int(ts)))


async def get_clan_tree_essence_at(clan_id: int) -> float | None:
    """unix ts следующей Эссенции (или None — таймер не запущен)."""
    conn = await get_db()
    cur = await conn.execute(
        "SELECT tree_amber_at FROM clans WHERE id = ?", (clan_id,))
    row = await cur.fetchone()
    raw = (row or {}).get('tree_amber_at')
    if not raw:
        return None
    try:
        return float(raw)
    except (TypeError, ValueError):
        return None


async def collect_clan_tree_essence(clan_id: int) -> tuple[bool, str]:
    """Сбор Эссии Памяти главой (кнопка). Двa способа хранить — независимо:

    Возвращает (ok, сообщение). Складывается в клановый склад или инвентарь —
    решает вызывающий код, этот хелпер только проверяет таймер и переставляет.
    """
    from utils.helpers import MOSCOW_TZ
    conn = await get_db()
    cur = await conn.execute(
        "SELECT tree_amber_at FROM clans WHERE id = ?", (clan_id,))
    row = await cur.fetchone()
    if not row or not row['tree_amber_at']:
        return False, "⏳ Древо ещё начало жить — таймер Эссии уже запущен, ждём."
    try:
        ts = float(row['tree_amber_at'])
    except (TypeError, ValueError):
        return False, "⚠️ Таймер Эссии повреждён — сообщи хранителю."
    now = datetime.now(MOSCOW_TZ).timestamp()
    if now < ts:
        left_days = (ts - now) / 86400
        return False, (f"⏳ Эссенция Памяти ещё зреет: осталось ~{max(0, int(left_days)) + 1} сут.")
    await set_clan_tree_essence_next(clan_id)
    return True, "🌿 Эссенция Памяти созрела!"


# ============ ЛОГ АКТИВНОСТИ ИГРОКОВ ============

async def log_ap_change(user_id: int, delta: int, reason: str = None):
    """Записать изменение ОД в ap_log (delta со знаком).

    Вызывать ДО применения изменения: ap_before = текущее значение ОД,
    ap_after = ap_before + delta. Так трейл каждый раз честный. Для аудита
    экономики: видно, откуда пришли и куда ушли очки действий. Некритичная
    операция — сбой записи лога не ломает игру.
    """
    conn = await get_db()
    try:
        cursor = await conn.execute("SELECT ap FROM users WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        if not row:
            return
        before = row['ap']
        after = max(0, before + delta)
        await conn.execute(
            "INSERT INTO ap_log (user_id, delta, ap_before, ap_after, reason) "
            "VALUES (?, ?, ?, ?, ?)",
            (user_id, delta, before, after, reason)
        )
        await conn.commit()
    except Exception:
        pass


async def log_activity(user_id: int, action: str, details: str = None):
    """Записать событие из жизни игрока (для просмотра админом)."""
    conn = await get_db()
    try:
        await conn.execute(
            "INSERT INTO activity_log (user_id, action, details) VALUES (?, ?, ?)",
            (user_id, action, details)
        )
        await conn.commit()
    except Exception:
        pass


async def get_user_activity(user_id: int, limit: int = 50):
    """Последние действия игрока."""
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT id, action, details, created_at FROM activity_log "
        "WHERE user_id = ? ORDER BY id DESC LIMIT ?",
        (user_id, limit)
    )
    return await cursor.fetchall()


async def get_recent_activity(limit: int = 30):
    """Последние действия всех игроков (общий поток)."""
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT a.id, a.user_id, a.action, a.details, a.created_at, "
        "u.username, u.first_name "
        "FROM activity_log a "
        "LEFT JOIN users u ON u.user_id = a.user_id "
        "ORDER BY a.id DESC LIMIT ?",
        (limit,)
    )
    return await cursor.fetchall()


async def get_activity_by_action(action: str, limit: int = 30):
    """Последние действия игроков по конкретному типу (фильтр общего потока)."""
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT a.id, a.user_id, a.action, a.details, a.created_at, "
        "u.username, u.first_name "
        "FROM activity_log a "
        "LEFT JOIN users u ON u.user_id = a.user_id "
        "WHERE a.action = ? ORDER BY a.id DESC LIMIT ?",
        (action, limit)
    )
    return await cursor.fetchall()


async def get_activity_like(pattern: str, limit: int = 30):
    """Последние действия по маске действия (например 'dungeon%')."""
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT a.id, a.user_id, a.action, a.details, a.created_at, "
        "u.username, u.first_name "
        "FROM activity_log a "
        "LEFT JOIN users u ON u.user_id = a.user_id "
        "WHERE a.action LIKE ? ORDER BY a.id DESC LIMIT ?",
        (pattern, limit)
    )
    return await cursor.fetchall()


async def prune_activity_log(days: int = 30):
    """Удалить из activity_log записи старше заданного числа дней (защита от роста таблицы)."""
    conn = await get_db()
    deleted = await conn.execute(
        "DELETE FROM activity_log WHERE created_at < datetime('now', ?)",
        (f"-{days} days",)
    )
    await conn.commit()
    return deleted.rowcount


# ============ ЛОГИРОВАНИЕ ПЕРЕХОДОВ ПО ЛОКАЦИЯМ ============

async def log_location_visit(user_id: int, location_key: str):
    """Записать вход игрока в локацию (для анализа популярности аспектов игры).

    Пишет строку в location_visits и увеличивает счётчик visits у локации.
    Некритичная операция — сбой записи не ломает игру.
    """
    conn = await get_db()
    try:
        await conn.execute(
            "INSERT INTO location_visits (user_id, location_key) VALUES (?, ?)",
            (user_id, location_key)
        )
        await conn.execute(
            "UPDATE locations SET visits = COALESCE(visits, 0) + 1 WHERE key = ?",
            (location_key,)
        )
        await conn.commit()
    except Exception:
        pass


async def get_location_visit_stats(days: int = None):
    """Агрегированная популярность локаций: ключ, имя, число входов, число игроков.

    days=None — за всё время, иначе за последние N дней. Сортировка по входам.
    """
    conn = await get_db()
    where = ""
    params = ()
    if days:
        where = "WHERE v.created_at >= datetime('now', ?)"
        params = (f"-{days} days",)
    cursor = await conn.execute(
        "SELECT v.location_key, "
        "COALESCE(l.name, v.location_key) AS name, "
        "COUNT(*) AS visits, COUNT(DISTINCT v.user_id) AS players "
        "FROM location_visits v "
        "LEFT JOIN locations l ON l.key = v.location_key "
        f"{where} "
        "GROUP BY v.location_key ORDER BY visits DESC, v.location_key",
        params
    )
    return await cursor.fetchall()


async def get_location_visit_totals(days: int = None):
    """Итоги по переходам: всего входов и уникальных игроков (days=None — всё время)."""
    conn = await get_db()
    where = ""
    params = ()
    if days:
        where = "WHERE created_at >= datetime('now', ?)"
        params = (f"-{days} days",)
    cursor = await conn.execute(
        f"SELECT COUNT(*) AS visits, COUNT(DISTINCT user_id) AS players "
        f"FROM location_visits {where}",
        params
    )
    return await cursor.fetchone()


async def prune_location_visits(days: int = 90):
    """Удалить записи переходов старше заданного числа дней (защита от роста таблицы)."""
    conn = await get_db()
    deleted = await conn.execute(
        "DELETE FROM location_visits WHERE created_at < datetime('now', ?)",
        (f"-{days} days",)
    )
    await conn.commit()
    return deleted.rowcount


async def clear_user_photo(user_id: int):
    """Удалить фото профиля игрока (фото установлено заново нельзя — через /profile)."""
    conn = await get_db()
    await conn.execute(
        "UPDATE users SET photo_file_id = NULL WHERE user_id = ?", (user_id,))
    await conn.commit()


async def get_user_photo(user_id: int):
    """Фото профиля игрока (file_id) или None."""
    conn = await get_db()
    cursor = await conn.execute("SELECT photo_file_id FROM users WHERE user_id = ?", (user_id,))
    row = await cursor.fetchone()
    if not row:
        return None
    return row['photo_file_id']


# ---------- Кланы и партии ----------

KIND_LABELS = {"clan": "клан", "party": "партия"}


async def create_clan(kind: str, name: str, description: str, creator_id: int) -> int:
    conn = await get_db()
    cursor = await conn.execute(
        "INSERT INTO clans (kind, name, description, created_by) VALUES (?, ?, ?, ?)",
        (kind, name, description, creator_id))
    await conn.commit()
    return cursor.lastrowid


async def get_clan(clan_id: int):
    conn = await get_db()
    cursor = await conn.execute("SELECT * FROM clans WHERE id = ?", (clan_id,))
    return await cursor.fetchone()


async def get_clans(kind: str = None):
    conn = await get_db()
    if kind:
        cursor = await conn.execute(
            "SELECT * FROM clans WHERE kind = ? ORDER BY name COLLATE NOCASE", (kind,))
    else:
        cursor = await conn.execute("SELECT * FROM clans ORDER BY kind, name COLLATE NOCASE")
    return await cursor.fetchall()


async def update_clan(clan_id: int, name=None, description=None, photo_file_id=None,
                      leader_id=None, tree_amber_at=None):
    conn = await get_db()
    sets, vals = [], []
    if name is not None:
        sets.append("name = ?")
        vals.append(name)
    if description is not None:
        sets.append("description = ?")
        vals.append(description)
    if photo_file_id is not None:
        sets.append("photo_file_id = ?")
        vals.append(photo_file_id)
    if leader_id is not None:
        sets.append("leader_id = ?")
        vals.append(leader_id)
    if tree_amber_at is not None:
        sets.append("tree_amber_at = ?")
        vals.append(str(tree_amber_at))
    if sets:
        vals.append(clan_id)
        await conn.execute(f"UPDATE clans SET {', '.join(sets)} WHERE id = ?", vals)
        await conn.commit()


async def set_clan_leader(clan_id: int, leader_id: int = None):
    conn = await get_db()
    await conn.execute("UPDATE clans SET leader_id = ? WHERE id = ?", (leader_id, clan_id))
    await conn.commit()
    try:
        await _backfill_clan_member_roles()
    except Exception:
        pass


async def delete_clan(clan_id: int):
    conn = await get_db()
    await conn.execute("DELETE FROM clan_requests WHERE clan_id = ?", (clan_id,))
    await conn.execute("DELETE FROM clan_members WHERE clan_id = ?", (clan_id,))
    await conn.execute("DELETE FROM clan_storage WHERE clan_id = ?", (clan_id,))
    await conn.execute("DELETE FROM clan_build_contrib WHERE clan_id = ?", (clan_id,))
    await conn.execute("DELETE FROM clan_expansions WHERE clan_id = ?", (clan_id,))
    await conn.execute("DELETE FROM clan_garden WHERE clan_id = ?", (clan_id,))
    await conn.execute("DELETE FROM clan_recipes WHERE clan_id = ?", (clan_id,))
    await conn.execute("DELETE FROM clan_shop_purchases WHERE clan_id = ?", (clan_id,))
    await conn.execute("DELETE FROM clan_shop_items WHERE clan_id = ?", (clan_id,))
    await conn.execute("DELETE FROM clan_tree_medit WHERE clan_id = ?", (clan_id,))
    await conn.execute("DELETE FROM clan_buildings WHERE clan_id = ?", (clan_id,))
    await conn.execute("DELETE FROM clans WHERE id = ?", (clan_id,))
    await conn.commit()


async def get_clan_storage(clan_id: int) -> list:
    """Содержимое кланового склада: строки qty>0 с названием и категорией."""
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT cs.item_id AS item_id, cs.qty AS qty, i.name AS name, "
        "i.category AS category "
        "FROM clan_storage cs JOIN items i ON i.id = cs.item_id "
        "WHERE cs.clan_id = ? AND cs.qty > 0 "
        "ORDER BY i.category, i.name COLLATE NOCASE", (clan_id,))
    return await cursor.fetchall()


async def get_clan_storage_qty(clan_id: int, item_id: int) -> int:
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT qty FROM clan_storage WHERE clan_id = ? AND item_id = ?",
        (clan_id, item_id))
    row = await cursor.fetchone()
    return row['qty'] if row else 0


async def add_clan_storage(clan_id: int, item_id: int, qty: int) -> None:
    """Пополнение/списание склада. Отрицательный остаток обрезается до нуля."""
    if not qty:
        return
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT qty FROM clan_storage WHERE clan_id = ? AND item_id = ?",
        (clan_id, item_id))
    row = await cursor.fetchone()
    if row:
        new_qty = max(0, row['qty'] + qty)
        await conn.execute(
            "UPDATE clan_storage SET qty = ?, updated_at = datetime('now') "
            "WHERE clan_id = ? AND item_id = ?",
            (new_qty, clan_id, item_id))
    elif qty > 0:
        await conn.execute(
            "INSERT INTO clan_storage (clan_id, item_id, qty) VALUES (?, ?, ?)",
            (clan_id, item_id, qty))
    await conn.commit()


async def take_clan_storage(clan_id: int, item_id: int, qty: int) -> bool:
    """Списать qty со склада, если хватает. Возвращает успех."""
    if qty <= 0:
        return False
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT qty FROM clan_storage WHERE clan_id = ? AND item_id = ?",
        (clan_id, item_id))
    row = await cursor.fetchone()
    if not row or row['qty'] < qty:
        return False
    await conn.execute(
        "UPDATE clan_storage SET qty = qty - ?, updated_at = datetime('now') "
        "WHERE clan_id = ? AND item_id = ?",
        (qty, clan_id, item_id))
    await conn.commit()
    return True


async def donate_to_clan_storage(clan_id: int, user_id: int, item_id: int,
                                 qty: int) -> bool:
    """Передать ресурс из личного инвентаря на склад клана.

    Вклад невозвратен. Разрешены только предметы категории 'resource'.
    """
    if qty <= 0:
        return False
    item = await get_item(item_id)
    if not item or item['category'] != 'resource':
        return False
    if not await remove_inventory_item(user_id, item_id, qty):
        return False
    await add_clan_storage(clan_id, item_id, qty)
    conn = await get_db()
    await conn.execute(
        "INSERT INTO clan_build_contrib (clan_id, user_id, item_id, qty) "
        "VALUES (?, ?, ?, ?)", (clan_id, user_id, item_id, qty))
    await conn.commit()
    return True


async def get_clan_contributions(clan_id: int, limit: int = 50) -> list:
    """Последние вклады клана: кто, что и сколько внёс."""
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT cb.id, cb.user_id, cb.item_id, cb.qty, cb.created_at, "
        "i.name AS item_name, u.first_name AS user_name "
        "FROM clan_build_contrib cb "
        "LEFT JOIN items i ON i.id = cb.item_id "
        "LEFT JOIN users u ON u.user_id = cb.user_id "
        "WHERE cb.clan_id = ? ORDER BY cb.id DESC LIMIT ?",
        (clan_id, limit))
    return await cursor.fetchall()


async def add_clan_member(clan_id: int, user_id: int):
    conn = await get_db()
    await conn.execute(
        "INSERT OR IGNORE INTO clan_members (clan_id, user_id, role) VALUES (?, ?, 'member')",
        (clan_id, user_id))
    await conn.execute("DELETE FROM clan_requests WHERE clan_id = ? AND user_id = ?",
                       (clan_id, user_id))
    await conn.commit()


async def remove_clan_member(clan_id: int, user_id: int):
    conn = await get_db()
    await conn.execute(
        "DELETE FROM clan_members WHERE clan_id = ? AND user_id = ?", (clan_id, user_id))
    await conn.commit()


async def is_clan_member(clan_id: int, user_id: int) -> bool:
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT 1 FROM clan_members WHERE clan_id = ? AND user_id = ?", (clan_id, user_id))
    return await cursor.fetchone() is not None


async def get_clan_members(clan_id: int):
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT u.* FROM clan_members cm JOIN users u ON u.user_id = cm.user_id "
        "WHERE cm.clan_id = ? ORDER BY u.first_name COLLATE NOCASE", (clan_id,))
    return await cursor.fetchall()


async def get_clan_member_ids(clan_id: int) -> list:
    conn = await get_db()
    cursor = await conn.execute("SELECT user_id FROM clan_members WHERE clan_id = ?", (clan_id,))
    rows = await cursor.fetchall()
    return [r['user_id'] for r in rows]


async def get_user_clan(user_id: int, kind: str = 'clan'):
    """Объединение указанного вида (клан/партия), где состоит пилот, или None."""
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT c.* FROM clans c JOIN clan_members cm ON cm.clan_id = c.id "
        "WHERE cm.user_id = ? AND c.kind = ? LIMIT 1", (user_id, kind))
    return await cursor.fetchone()


async def get_user_clans(user_id: int):
    """Все объединения (клан и/или партия), где состоит пилот."""
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT c.* FROM clans c JOIN clan_members cm ON cm.clan_id = c.id "
        "WHERE cm.user_id = ?", (user_id,))
    return await cursor.fetchall()


async def is_clan_leader(user_id: int):
    """ID объединения, главой которого является пилот, или None."""
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT id FROM clans WHERE leader_id = ? LIMIT 1", (user_id,))
    row = await cursor.fetchone()
    return row['id'] if row else None


async def add_clan_request(clan_id: int, user_id: int):
    conn = await get_db()
    await conn.execute(
        "INSERT OR IGNORE INTO clan_requests (clan_id, user_id) VALUES (?, ?)",
        (clan_id, user_id))
    await conn.commit()


async def remove_clan_request(clan_id: int, user_id: int):
    conn = await get_db()
    await conn.execute(
        "DELETE FROM clan_requests WHERE clan_id = ? AND user_id = ?", (clan_id, user_id))
    await conn.commit()


async def has_clan_request(clan_id: int, user_id: int) -> bool:
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT 1 FROM clan_requests WHERE clan_id = ? AND user_id = ?", (clan_id, user_id))
    return await cursor.fetchone() is not None


async def get_clan_pending_requests(clan_id: int):
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT u.*, r.created_at FROM clan_requests r JOIN users u ON u.user_id = r.user_id "
        "WHERE r.clan_id = ? ORDER BY r.created_at", (clan_id,))
    return await cursor.fetchall()


# ---------- Рецепты у пилота ----------

async def learn_recipe(user_id: int, recipe_id: int):
    conn = await get_db()
    await conn.execute(
        "INSERT OR IGNORE INTO user_recipes (user_id, recipe_id) VALUES (?, ?)",
        (user_id, recipe_id))
    await conn.commit()


async def has_user_recipe(user_id: int, recipe_id: int) -> bool:
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT 1 FROM user_recipes WHERE user_id = ? AND recipe_id = ?",
        (user_id, recipe_id))
    return await cursor.fetchone() is not None


async def get_learned_recipes(user_id: int, expansion: str = None, level: int = None):
    """Рецепты, открытые у пилота, в контексте расширения и уровня расширения."""
    conn = await get_db()
    q = ("SELECT r.* FROM recipes r JOIN user_recipes ur ON ur.recipe_id = r.id "
         "WHERE ur.user_id = ? AND r.is_available = 1")
    params = [user_id]
    if expansion:
        q += " AND r.required_expansion = ?"
        params.append(expansion)
        if level is not None:
            q += " AND r.required_level <= ?"
            params.append(level)
    q += " ORDER BY r.required_level, r.rarity, r.id"
    cursor = await conn.execute(q, params)
    return await cursor.fetchall()


# ---------- Рецепты как товары магазина ----------

RECIPE_ITEM_PREFIX = "Рецепт: "
BOOK_ITEM_PREFIX = "Книга рецептов: "

RECIPE_ITEM_PRICES = {
    "Жареный сиг": 60,
    "Жареный муксун": 60,
    "Жареный чир": 70,
    "Жареный налим": 80,
    "Жареный сом": 90,
    "Жареный угорь": 220,
    "Жареная форель": 750,
    "Жареный опёнок": 60,
    "Жареный подберёзовик": 60,
    "Жареные лисички": 90,
    "Жареный белый гриб": 120,
    "Жареный гиропор": 220,
    "Жареный ежовик гребенчатый": 750,
    "Жареное мясо кабана": 90,
    "Сварить яд": 400,
    "Комбинированная наживка": 90,
    "Пара сапог": 320,
    "Малая настойка здоровья": 150,
    "Энергетик": 280,
    "Улучшенная настойка здоровья": 480,
    "Жареное мясо моллюска": 100,
    "Рыбный пирог": 150,
}


async def _merge_inventory(conn, from_item_id: int, to_item_id: int):
    """Переносит строки инвентаря с одного товара на другой, складывая количество.

    Нужна при слиянии дублей товаров: user_id + item_id — первичный ключ, поэтому
    простое UPDATE ... SET item_id упрётся в конфликт. Количество складываем,
    а не затираем, иначе игрок потеряет купленное.
    """
    rows = await (await conn.execute(
        "SELECT user_id, quantity FROM inventory WHERE item_id = ?", (from_item_id,)
    )).fetchall()
    for row in rows:
        target = await (await conn.execute(
            "SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?",
            (row['user_id'], to_item_id))).fetchone()
        if target:
            await conn.execute(
                "UPDATE inventory SET quantity = ? WHERE user_id = ? AND item_id = ?",
                ((target['quantity'] or 0) + (row['quantity'] or 0),
                 row['user_id'], to_item_id))
            await conn.execute(
                "DELETE FROM inventory WHERE user_id = ? AND item_id = ?",
                (row['user_id'], from_item_id))
        else:
            await conn.execute(
                "UPDATE inventory SET item_id = ? WHERE user_id = ? AND item_id = ?",
                (to_item_id, row['user_id'], from_item_id))


async def ensure_recipe_shop_items():
    """Создаёт в магазине предметы-рецепты категории 'recipes'.

    Предмет «Рецепт: <название>» при использовании из инвентаря открывает
    соответствующий рецепт для пилота (таблица user_recipes).

    Переименованные рецепты (ключ 'old') тянут за собой и товар: игнорировать
    старый товар нельзя, learn_recipe_from_item() ищет рецепт ровно по имени.
    Товары, чей рецепт в базе отсутствует, гасятся (is_available = 0) — иначе
    они продаются, но выучить их нельзя.
    """
    conn = await get_db()
    changed = False
    for r in RECIPES_DEF:
        old = r.get('old')
        if not old:
            continue
        old_name = RECIPE_ITEM_PREFIX + old
        new_name = RECIPE_ITEM_PREFIX + r['name']
        old_item = await (await conn.execute(
            "SELECT id FROM items WHERE name = ? AND category = 'recipes'", (old_name,)
        )).fetchone()
        if not old_item:
            continue
        new_item = await (await conn.execute(
            "SELECT id FROM items WHERE name = ? AND category = 'recipes'", (new_name,)
        )).fetchone()
        if new_item:
            # Товар с новым именем уже есть (например, «Рецепт: Жареная форель»
            # продавался, пока рецепт назывался «Пожарить форель»). Складываем
            # инвентарь старого товара в существующий и гасим дубль, иначе в магазине
            # один рецепт будет показан дважды, а часть выданного — отыгравшая.
            await _merge_inventory(conn, old_item['id'], new_item['id'])
            await conn.execute(
                "UPDATE items SET is_available = 0 WHERE id = ?", (old_item['id'],))
        else:
            await conn.execute(
                "UPDATE items SET name = ? WHERE id = ?", (new_name, old_item['id']))
        changed = True
    for r in RECIPES_DEF:
        row = await conn.execute(
            "SELECT id FROM recipes WHERE name = ? AND required_expansion = ? AND required_level = ?",
            (r['name'], r['exp'], r['lvl']))
        recipe_row = await row.fetchone()
        if not recipe_row:
            continue
        item_name = RECIPE_ITEM_PREFIX + r['name']
        item = await get_item_by_name(item_name)
        price = RECIPE_ITEM_PRICES.get(r['name'], 100)
        exp_label = {"kitchen": "кухня", "workbench": "верстак"}.get(r['exp'], r['exp'])
        desc = (f"📜 Обучает рецепту: {r['name']}.\n"
                f"Крафтится на: {exp_label} уровня {r['lvl']}.\n"
                f"{r['desc']}\n"
                f"Используй из инвентаря, чтобы выучить рецепт и крафтить в жилье.")
        if item:
            await conn.execute(
                "UPDATE items SET description = ?, price = ?, sell_price = ?, rarity = ?, "
                "category = 'recipes', is_available = 1 WHERE id = ?",
                (desc, price, price // 2, r.get('rarity', 1), item['id']))
            changed = True
        else:
            await add_item(item_name, desc, price, price // 2, r.get('rarity', 1),
                           'recipes', -1, 0)
            changed = True
    # Гасим товары-рецепты, для которых рецепта в базе нет: продавать их бессмысленно,
    # а learn_recipe_from_item() на них отвечает «Рецепт не найден».
    known = {r['name'] for r in await (await conn.execute(
        "SELECT name FROM recipes WHERE is_available = 1")).fetchall()}
    for it in await (await conn.execute(
            "SELECT id, name FROM items WHERE category = 'recipes' AND is_available = 1"
    )).fetchall():
        title = it['name']
        if title.startswith(BOOK_ITEM_PREFIX):
            # Книги рецептов — отдельный вид носителя: их состав лежит в
            # recipe_book_items, а видимостью управляет менеджер книг.
            # Без этого пропуска старт гасил бы все созданные книги.
            continue
        if title.startswith(RECIPE_ITEM_PREFIX):
            title = title[len(RECIPE_ITEM_PREFIX):]
        if title not in known:
            await conn.execute(
                "UPDATE items SET is_available = 0 WHERE id = ?", (it['id'],))
            changed = True
    if changed:
        await conn.commit()
    return changed


async def learn_recipe_from_item(user_id: int, item_id: int):
    """Использование предмета-рецепта: открывает рецепт(ы) навсегда.

    Поддерживает два вида носителей в категории 'recipes':
    - свиток «Рецепт: <название>» — один рецепт, ищется по имени;
    - книга «Книга рецептов: <название>» — набор из `recipe_book_items`,
      открывает все рецепты книги, которые ещё не выучены и не скрыты.
    Возвращает (ok, сообщение). Предмет списывается из инвентаря только если
    реально открылся хотя бы один рецепт.
    """
    item = await get_item(item_id)
    if not item or item.get('category') != 'recipes':
        return False, "Это не рецепт."
    inv_row = await get_inventory_item(user_id, item_id)
    if not inv_row or (inv_row.get('quantity') or 0) < 1:
        return False, "У тебя нет этого рецепта в инвентаре."

    book_recipes = await get_recipe_book_recipes(item_id)
    if not book_recipes and item['name'].startswith(BOOK_ITEM_PREFIX):
        return False, "В этой книге нет рецептов — предмет испорчен."
    if book_recipes:
        learned, already = [], []
        for recipe in book_recipes:
            if not recipe['is_available']:
                continue
            if await has_user_recipe(user_id, recipe['id']):
                already.append(recipe['name'])
                continue
            await learn_recipe(user_id, recipe['id'])
            learned.append(recipe['name'])
        if not learned:
            return False, "Все рецепты из этой книги уже выучены или недоступны."
        await remove_inventory_item(user_id, item_id, 1)
        await log_activity(
            user_id, "recipe_learn",
            f"Выучил по книге «{item['name']}»: {', '.join(learned)}")
        msg = f"📖 Ты выучил рецепты: {', '.join(learned)}."
        if already:
            msg += f"\n(уже были: {', '.join(already)})"
        return True, msg

    recipe_name = item['name']
    if recipe_name.startswith(RECIPE_ITEM_PREFIX):
        recipe_name = recipe_name[len(RECIPE_ITEM_PREFIX):]
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT * FROM recipes WHERE name = ? AND is_available = 1", (recipe_name,))
    recipe = await cursor.fetchone()
    if not recipe:
        return False, "Рецепт не найден."
    if await has_user_recipe(user_id, recipe['id']):
        return False, f"Рецепт «{recipe['name']}» уже выучен."
    await learn_recipe(user_id, recipe['id'])
    await remove_inventory_item(user_id, item_id, 1)
    await log_activity(user_id, "recipe_learn", f"Выучил рецепт «{recipe['name']}»")
    # Хук «Чтящий Предков» (Фаза 4): рецепты — часть набора.
    try:
        if await has_user_recipe(user_id, recipe['id']):
            await check_fire_keeper(user_id)
    except Exception:
        pass
    return True, f"📜 Ты выучил рецепт «{recipe['name']}»! Теперь он доступен в крафте."


async def ensure_user_recipes_backfill():
    """Разово открывает все рецепты существующим игрокам.

    До введения магазинных рецептов все они были доступны всем пилотам сразу;
    после ввода — только покупка/лут/использование. Чтобы не отнимать уже
    привычный крафт, при первом запуске фичи рецепты открываются всем текущим
    пользователям. Новые игроки рецепты не получают.
    """
    conn = await get_db()
    cursor = await conn.execute("SELECT COUNT(*) AS c FROM user_recipes")
    total = await cursor.fetchone()
    if total and total['c'] > 0:
        return False
    rc = await conn.execute("SELECT id FROM recipes")
    recipe_ids = [r['id'] for r in await rc.fetchall()]
    if not recipe_ids:
        return False
    uc = await conn.execute("SELECT user_id FROM users")
    user_ids = [u['user_id'] for u in await uc.fetchall()]
    if not user_ids:
        return False
    pairs = [(uid, rid) for uid in user_ids for rid in recipe_ids]
    await conn.executemany(
        "INSERT OR IGNORE INTO user_recipes (user_id, recipe_id) VALUES (?, ?)", pairs)
    await conn.commit()
    return True


def location_glade_photo(loc):
    if not loc:
        return None
    if isinstance(loc, dict):
        return loc.get('glade_photo') or None
    try:
        return loc['glade_photo']
    except Exception:
        try:
            return dict(loc).get('glade_photo')
        except Exception:
            return None


def location_clearing_photo(loc):
    if not loc:
        return None
    if isinstance(loc, dict):
        return loc.get('clearing_photo') or None
    try:
        return loc['clearing_photo']
    except Exception:
        try:
            return dict(loc).get('clearing_photo')
        except Exception:
            return None

async def _backfill_clan_member_roles():
    """Синхронизирует роли членов клана с главой клана (leader_id)."""
    try:
        conn = await get_db()
        await conn.execute(
            "UPDATE clan_members SET role = 'leader' WHERE role <> 'leader' AND EXISTS ("
            "SELECT 1 FROM clans WHERE clans.id = clan_members.clan_id AND clans.leader_id = clan_members.user_id"
            ")"
        )
        await conn.execute(
            "UPDATE clan_members SET role = 'member' WHERE role = 'leader' AND NOT EXISTS ("
            "SELECT 1 FROM clans WHERE clans.id = clan_members.clan_id AND clans.leader_id = clan_members.user_id"
            ")"
        )
        await conn.commit()
    except Exception:
        pass


async def get_clan_member_role(clan_id: int, user_id: int) -> str:
    conn = await get_db()
    cur = await conn.execute(
        "SELECT role FROM clan_members WHERE clan_id = ? AND user_id = ?",
        (clan_id, user_id))
    row = await cur.fetchone()
    if not row:
        return ''
    return (row['role'] or 'member').strip().lower()


async def get_clan_member_roles(clan_id: int) -> dict:
    """{user_id: role} по всем членам клана (для экрана иерархии)."""
    conn = await get_db()
    cur = await conn.execute(
        "SELECT user_id, role FROM clan_members WHERE clan_id = ?", (clan_id,))
    out = {}
    for r in await cur.fetchall():
        out[int(r['user_id'])] = (r['role'] or 'member').strip().lower()
    return out


async def set_clan_member_role(clan_id: int, user_id: int, role: str) -> bool:
    """Назначает роль члену клана.

    seneschal/banner/elder — эксклюзивные должности: носитель прежний
    автоматически понижается до 'member'. 'leader' идёт через set_clan_leader.
    """
    import config as _config
    role = (role or '').strip().lower()
    # 'leader' смена через set_clan_leader (перекидывает роль автоматически)
    if role == 'leader' or role not in getattr(_config, 'CLAN_ROLES', {}):
        return False
    conn = await get_db()
    cur = await conn.execute(
        "SELECT 1 FROM clan_members WHERE clan_id = ? AND user_id = ?",
        (clan_id, user_id))
    if not await cur.fetchone():
        return False
    # эксклюзивность должности
    await conn.execute(
        "UPDATE clan_members SET role = 'member' WHERE clan_id = ? AND role = ? AND user_id <> ?",
        (clan_id, role, user_id))
    cur = await conn.execute(
        "UPDATE clan_members SET role = ? WHERE clan_id = ? AND user_id = ?",
        (role, clan_id, user_id))
    await conn.commit()
    return cur.rowcount > 0


async def can_manage_clan_hall(clan_id: int, user_id: int) -> bool:
    """Право управлять клан-холлом (выбор/старт/отмена стройки, расширения)."""
    clan = await get_clan(clan_id)
    if not clan or clan['kind'] != 'clan':
        return False
    role = await get_clan_member_role(clan_id, user_id)
    if role in ('leader', 'seneschal'):
        return True
    # fallback на главу клана
    return bool(clan['leader_id'] and int(clan['leader_id']) == int(user_id))


async def can_withdraw_clan_storage(clan_id: int, user_id: int) -> bool:
    """Вывод со склада клана — только глава клана."""
    clan = await get_clan(clan_id)
    if not clan or clan['kind'] != 'clan':
        return False
    role = await get_clan_member_role(clan_id, user_id)
    if role == 'leader':
        return True
    return bool(clan['leader_id'] and int(clan['leader_id']) == int(user_id))


async def can_harvest_clan_garden(clan_id: int, user_id: int) -> bool:
    """Сбор урожая в клановом саду — лидер или офицер клана."""
    clan = await get_clan(clan_id)
    if not clan or clan['kind'] != 'clan':
        return False
    role = await get_clan_member_role(clan_id, user_id)
    if role in ('leader', 'seneschal'):
        return True
    return bool(clan['leader_id'] and int(clan['leader_id']) == int(user_id))


async def get_clan_building(clan_id: int):
    conn = await get_db()
    cur = await conn.execute("SELECT * FROM clan_buildings WHERE clan_id = ?", (clan_id,))
    return await cur.fetchone()


async def get_all_clan_buildings() -> list:
    """Все здания кланов (для админ-менеджера картинок). Пропускают и без статуса."""
    conn = await get_db()
    cur = await conn.execute(
        "SELECT b.*, c.name AS clan_name FROM clan_buildings b "
        "JOIN clans c ON c.id = b.clan_id WHERE c.kind = 'clan' "
        "ORDER BY c.name COLLATE NOCASE")
    return await cur.fetchall()


async def ensure_clan_building(clan_id: int):
    conn = await get_db()
    await conn.execute(
        "INSERT OR IGNORE INTO clan_buildings (clan_id, status) VALUES (?, 'choosing')",
        (clan_id,))
    await conn.commit()
    return await get_clan_building(clan_id)


async def get_clan_construction_photo() -> str | None:
    """Общая картинка-заглушка стройки кланового здания (file_id из settings)."""
    conn = await get_db()
    cur = await conn.execute(
        "SELECT value FROM settings WHERE key = 'clan_construction_photo'")
    row = await cur.fetchone()
    val = (row['value'] or '').strip() if row and row['value'] else ''
    return val or None


async def set_clan_construction_photo(photo_file_id: str | None) -> None:
    """Установить или сбросить общую картинку-заглушку стройки."""
    conn = await get_db()
    if photo_file_id:
        await conn.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES ('clan_construction_photo', ?)",
            (photo_file_id.strip(),))
    else:
        await conn.execute("DELETE FROM settings WHERE key = 'clan_construction_photo'")
    await conn.commit()


# --- Картинки расширений клан-холла (Фаза 8) ---
def clan_expansion_photo_key(exp_type: str) -> str:
    """Ключ settings для индивидуальной картинки расширения."""
    return f"clanh_exp_photo_{exp_type}"


async def get_clan_expansion_photo(exp_type: str) -> str | None:
    """Индивидуальная картинка экрана расширения (file_id из settings или None)."""
    conn = await get_db()
    cur = await conn.execute(
        "SELECT value FROM settings WHERE key = ?",
        (clan_expansion_photo_key(exp_type),))
    row = await cur.fetchone()
    val = (row['value'] or '').strip() if row and row['value'] else ''
    return val or None


async def set_clan_expansion_photo(exp_type: str, photo_file_id: str | None) -> None:
    """Установить/сбросить картинку расширения (None — удалить ключ)."""
    conn = await get_db()
    key = clan_expansion_photo_key(exp_type)
    if photo_file_id:
        await conn.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            (key, photo_file_id.strip()))
    else:
        await conn.execute("DELETE FROM settings WHERE key = ?", (key,))
    await conn.commit()


async def set_clan_building_photo(clan_id: int, photo_file_id: str | None):
    """Установить или сбросить индивидуальную картинку готового здания клана."""
    await ensure_clan_building(clan_id)
    conn = await get_db()
    await conn.execute(
        """UPDATE clan_buildings SET building_photo_file_id = ?, updated_at = datetime('now')
           WHERE clan_id = ?""",
        (photo_file_id, clan_id))
    await conn.commit()


async def set_clan_building_choice(clan_id: int, building_type: str,
                                   required_json: str, price_nm: int):
    await ensure_clan_building(clan_id)
    conn = await get_db()
    await conn.execute(
        """UPDATE clan_buildings SET building_type = ?, target_type = NULL, status = 'funding',
           required_json = ?, price_nm = ?, chosen_at = datetime('now'),
           started_at = NULL, completes_at = NULL, updated_at = datetime('now')
           WHERE clan_id = ?""",
        (building_type, required_json, int(price_nm), clan_id))
    await conn.commit()


CLAN_BUILDING_CHAIN = ("house", "manor", "castle")


def next_clan_building_type(current: str | None) -> str | None:
    """Следующий уровень здания по цепочке house → manor → castle (или None)."""
    try:
        idx = CLAN_BUILDING_CHAIN.index(current or "")
    except ValueError:
        return None
    if idx + 1 >= len(CLAN_BUILDING_CHAIN):
        return None
    return CLAN_BUILDING_CHAIN[idx + 1]


async def has_clan_project_contributions(clan_id: int) -> bool:
    """Были ли вклады в склад после выбора текущего проекта (chosen_at)."""
    b = await get_clan_building(clan_id)
    if not b or not b['chosen_at']:
        return False
    conn = await get_db()
    cur = await conn.execute(
        "SELECT 1 FROM clan_build_contrib WHERE clan_id = ? AND created_at >= ? LIMIT 1",
        (clan_id, b['chosen_at']))
    return (await cur.fetchone()) is not None


async def choose_clan_building(clan_id: int, user_id: int,
                               building_type: str) -> tuple[bool, str]:
    """Выбор типа здания главой клана (фиксирует снимок required_json и price_nm)."""
    if not await can_manage_clan_hall(clan_id, user_id):
        return False, "❌ Выбирать проект здания может только глава клана."
    btypes = getattr(config, "CLAN_BUILDING_TYPES", {})
    if building_type not in btypes:
        return False, "❌ Неизвестный тип здания."
    b = await ensure_clan_building(clan_id)
    if b['status'] not in ('choosing', 'funding'):
        return False, "❌ Здание уже строится или построено."
    if b['status'] == 'funding' and await has_clan_project_contributions(clan_id):
        return False, "❌ В проект уже внесены ресурсы — сначала отмени сбор или заверши стройку."
    cfg = btypes[building_type]
    req_json = json.dumps(cfg.get('required') or {}, ensure_ascii=False)
    price_nm = int(cfg.get('price_nm') or 0)
    await set_clan_building_choice(clan_id, building_type, req_json, price_nm)
    return True, f"✅ Выбран проект: «{cfg['name']}». Можно собирать ресурсы!"


async def choose_clan_upgrade(clan_id: int, user_id: int) -> tuple[bool, str]:
    """Выбор улучшения построенного здания до следующего уровня (вариант A).

    Строка остаётся одна: `building_type` — текущий уровень, `target_type` —
    цель. Снимок требований и цены фиксируется по целевому уровню.
    """
    if not await can_manage_clan_hall(clan_id, user_id):
        return False, "❌ Улучшать здание может только глава клана."
    b = await ensure_clan_building(clan_id)
    if b['status'] != 'built' or not b['building_type']:
        return False, "❌ Улучшать можно только построенное здание."
    target = next_clan_building_type(b['building_type'])
    if not target:
        return False, "❌ Здание уже улучшено до максимального уровня."
    btypes = getattr(config, "CLAN_BUILDING_TYPES", {})
    tcfg = btypes.get(target)
    if not tcfg:
        return False, "❌ Неизвестный тип здания."
    req_json = json.dumps(tcfg.get('required') or {}, ensure_ascii=False)
    price_nm = int(tcfg.get('price_nm') or 0)
    conn = await get_db()
    await conn.execute(
        """UPDATE clan_buildings SET target_type = ?, status = 'upgrade_funding',
           required_json = ?, price_nm = ?, chosen_at = datetime('now'),
           started_at = NULL, completes_at = NULL, updated_at = datetime('now')
           WHERE clan_id = ?""",
        (target, req_json, price_nm, clan_id))
    await conn.commit()
    return True, f"⬆️ Выбрано улучшение до «{tcfg['name']}». Можно собирать ресурсы!"


async def cancel_clan_building_funding(clan_id: int):
    conn = await get_db()
    await conn.execute(
        """UPDATE clan_buildings SET building_type = NULL, target_type = NULL,
           status = 'choosing', required_json = NULL, price_nm = 0,
           chosen_at = NULL, started_at = NULL, completes_at = NULL,
           updated_at = datetime('now') WHERE clan_id = ?""",
        (clan_id,))
    await conn.commit()


async def cancel_clan_upgrade(clan_id: int):
    """Отмена сбора на улучшение: здание остаётся на текущем уровне (`built`)."""
    conn = await get_db()
    await conn.execute(
        """UPDATE clan_buildings SET target_type = NULL, status = 'built',
           required_json = NULL, price_nm = 0, chosen_at = NULL,
           started_at = NULL, completes_at = NULL,
           updated_at = datetime('now') WHERE clan_id = ?""",
        (clan_id,))
    await conn.commit()


async def cancel_clan_building(clan_id: int, user_id: int) -> tuple[bool, str]:
    """Отмена выбранного проекта/улучшения (ресурсы остаются на складе)."""
    if not await can_manage_clan_hall(clan_id, user_id):
        return False, "❌ Отменить проект может только глава клана."
    b = await ensure_clan_building(clan_id)
    if b['status'] == 'upgrade_funding':
        await cancel_clan_upgrade(clan_id)
        return True, "↩️ Улучшение отменено. Все внесённые ресурсы остались на складе клана."
    if b['status'] != 'funding':
        return False, "❌ Отменить проект можно только на этапе сбора ресурсов."
    await cancel_clan_building_funding(clan_id)
    return True, "↩️ Сбор отменён. Все внесённые ресурсы остались на складе клана."


async def get_clan_project_progress(clan_id: int,
                                    required: dict | None = None) -> tuple[list[dict], bool]:
    """Прогресс по ресурсам проекта: список {name, item_id, need, have, ok} и флаг all_ok."""
    if required is None:
        b = await get_clan_building(clan_id)
        try:
            required = json.loads((b['required_json'] if b else None) or "{}")
        except Exception:
            required = {}
    rows = []
    all_ok = bool(required)
    for name, need in (required or {}).items():
        need = int(need or 0)
        if need <= 0:
            continue
        item = await get_item_by_name(name)
        item_id = item['id'] if item else None
        have = await get_clan_storage_qty(clan_id, item_id) if item_id else 0
        ok = have >= need
        if not ok:
            all_ok = False
        rows.append({
            "name": name,
            "item_id": item_id,
            "need": need,
            "have": have,
            "ok": ok,
        })
    return rows, all_ok


async def start_clan_building(clan_id: int, completes_at: str):
    conn = await get_db()
    await conn.execute(
        """UPDATE clan_buildings SET status = 'building', started_at = datetime('now'),
           completes_at = ?, updated_at = datetime('now') WHERE clan_id = ?""",
        (completes_at, clan_id))
    await conn.commit()


async def start_clan_upgrading(clan_id: int, target_type: str, required_json: str,
                               price_nm: int, completes_at: str):
    conn = await get_db()
    await conn.execute(
        """UPDATE clan_buildings SET target_type = ?, status = 'upgrading',
           required_json = ?, price_nm = ?, started_at = datetime('now'),
           completes_at = ?, updated_at = datetime('now') WHERE clan_id = ?""",
        (target_type, required_json, price_nm, completes_at, clan_id))
    await conn.commit()


async def deduct_clan_storage_items(clan_id: int, items: dict):
    conn = await get_db()
    for item_id, need in items.items():
        if need <= 0:
            continue
        await conn.execute(
            """UPDATE clan_storage SET qty = MAX(0, qty - ?), updated_at = datetime('now')
               WHERE clan_id = ? AND item_id = ?""",
            (need, clan_id, int(item_id)))
    await conn.commit()


async def start_clan_building_project(clan_id: int, user_id: int,
                                      skip_resources: bool = False) -> tuple[bool, str, dict | None]:
    """Старт строительства здания главой клана.

    Два способа оплаты:
    - обычный: на складе клана собраны все ресурсы проекта, с главы списывается
      базовый `price_nm`, ресурсы со склада списываются ровно по норме;
    - без ресурсов (`skip_resources=True`): склад клана не трогаем, глава платит
      `price_nm × config.CLAN_BUILDING_NO_RESOURCES_MULT` (двойная цена).
    """
    if not await can_manage_clan_hall(clan_id, user_id):
        return False, "❌ Запустить стройку может только глава клана.", None
    b = await ensure_clan_building(clan_id)
    if b['status'] not in ('funding', 'upgrade_funding'):
        return False, "❌ Проект здания не находится на этапе сбора ресурсов.", None
    is_upgrade = b['status'] == 'upgrade_funding'
    btypes = getattr(config, "CLAN_BUILDING_TYPES", {})
    if is_upgrade:
        btype = b['target_type']
        current_type = b['building_type']
        if not btype or not current_type or btype not in btypes or current_type not in btypes:
            return False, "❌ Неизвестный тип здания.", None
    else:
        btype = b['building_type']
        current_type = btype
        if not btype or btype not in btypes:
            return False, "❌ Неизвестный тип здания.", None

    price_base = int(b['price_nm'] or 0)
    mult = int(getattr(config, "CLAN_BUILDING_NO_RESOURCES_MULT", 2) or 2)
    progress = []
    if skip_resources:
        price_nm = price_base * mult
    else:
        try:
            required = json.loads(b['required_json'] or "{}")
        except Exception:
            required = {}
        progress, all_ok = await get_clan_project_progress(clan_id, required)
        if not all_ok:
            return False, "❌ На складе клана ещё не собраны все необходимые ресурсы.", None
        price_nm = price_base

    leader = await get_user(user_id)
    have_nm = int((leader['nordmarks'] if leader else 0) or 0)
    if have_nm < price_nm:
        if skip_resources:
            return (False,
                    f"❌ Для стройки без ресурсов нужно {price_nm} НМ "
                    f"(двойная цена), у главы есть {have_nm} НМ.",
                    None)
        return (False,
                f"❌ Недостаточно нордмарок у главы клана: нужно {price_nm} НМ, есть {have_nm} НМ.",
                None)

    # С ресурсами: списываем ровно требуемые ресурсы со склада (излишки остаются).
    # Без ресурсов: склад не трогаем — всё оплачено нордмарками.
    if not skip_resources:
        to_deduct = {r['item_id']: r['need'] for r in progress if r['item_id'] and r['need'] > 0}
        await deduct_clan_storage_items(clan_id, to_deduct)

    # Списываем НМ с лидера (транзакция clan_build)
    bname = btypes[btype]['name']
    if price_nm > 0:
        if is_upgrade:
            reason = (f"Улучшение здания клана «{btypes[current_type]['name']}» "
                      f"до «{bname}»")
        else:
            reason = f"Строительство здания клана «{bname}»"
        if skip_resources:
            reason += " без сбора ресурсов (двойная оплата)"
        await remove_nordmarks(user_id, price_nm, "clan_build", reason)
    days = int(btypes[btype].get('days') or 2)
    completes_at = (datetime.now(timezone.utc) + timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
    if is_upgrade:
        await start_clan_upgrading(clan_id, btype, b['required_json'] or "{}",
                                   price_nm, completes_at)
        msg = f"🚧 Улучшение до «{bname}» начато! Завершится {completes_at[:10]}."
    else:
        await start_clan_building(clan_id, completes_at)
        msg = f"🏗 Строительство «{bname}» начато! Завершится {completes_at[:10]}."
    updated = await get_clan_building(clan_id)
    if skip_resources:
        msg += f" Ресурсы не понадобились: оплачено {price_nm} НМ (двойная цена)."
    return True, msg, updated


async def set_clan_building_built(clan_id: int, building_type: str,
                                  clear_photo: bool = False):
    """Фиксирует готовое здание. При апгрейде (`clear_photo=True`) фото сбрасывается.

    После улучшения индивидуальное фото текущего уровня больше не подходит:
    показываем дефолтную картинку нового уровня, пока админ не загрузит своё.
    """
    conn = await get_db()
    photo_sql = ", building_photo_file_id = NULL" if clear_photo else ""
    await conn.execute(
        f"""UPDATE clan_buildings SET building_type = ?, target_type = NULL,
           status = 'built', required_json = NULL, price_nm = 0,
           started_at = NULL, completes_at = NULL{photo_sql},
           updated_at = datetime('now')
           WHERE clan_id = ?""",
        (building_type, clan_id))
    await conn.commit()


async def resolve_clan_building_with_event(clan_id: int) -> tuple[object, str | None]:
    """Ленивое разрешение таймера стройки/апгрейда.

    Возвращает (row, event), где event in (None, 'built', 'upgraded').
    """
    b = await ensure_clan_building(clan_id)
    if not b or b['status'] not in ('building', 'upgrading') or not b['completes_at']:
        return b, None
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    if str(b['completes_at']) > now_str:
        return b, None
    if b['status'] == 'upgrading':
        new_type = b['target_type'] or b['building_type']
        event = 'upgraded'
        await set_clan_building_built(clan_id, new_type, clear_photo=True)
    else:
        new_type = b['building_type']
        event = 'built'
        await set_clan_building_built(clan_id, new_type)
    return await get_clan_building(clan_id), event


async def resolve_clan_building(clan_id: int):
    """Ленивое разрешение таймера стройки/апгрейда при открытии холла."""
    row, _ = await resolve_clan_building_with_event(clan_id)
    return row


async def resolve_due_clan_buildings() -> list[dict]:
    """Проход по всем активным стройкам/апгрейдам кланов, у которых вышел срок."""
    conn = await get_db()
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    cur = await conn.execute(
        """SELECT clan_id FROM clan_buildings
           WHERE status IN ('building', 'upgrading')
             AND completes_at IS NOT NULL AND completes_at <= ?""",
        (now_str,))
    rows = await cur.fetchall()
    done = []
    for r in rows:
        cid = int(r['clan_id'])
        updated, event = await resolve_clan_building_with_event(cid)
        if event and updated:
            done.append({
                "clan_id": cid,
                "event": event,
                "building_type": updated['building_type'],
            })
    return done


# ── Расширения клан-холла (Фаза 3) ────────────────────────────────────────────

CLAN_EXPANSION_RESERVE_SLOT = 7


def clan_expansion_slots(building_type: str | None) -> int:
    """Сколько слотов расширений реально доступно для типа здания.

    У резиденции 7-й слот объявлен в конфиге, но оставлен резервом под будущие
    механики — устанавливать туда расширения нельзя.
    """
    cfg = getattr(config, "CLAN_BUILDING_TYPES", {}).get(building_type or "", {})
    slots = int(cfg.get("slots") or 0)
    if building_type == "castle" and slots >= CLAN_EXPANSION_RESERVE_SLOT:
        slots -= 1
    return slots


def clan_expansion_max_level(building_type: str | None) -> int:
    """Максимальный уровень расширения для типа здания (дом/поместье 2, резиденция 4)."""
    cfg = getattr(config, "CLAN_BUILDING_TYPES", {}).get(building_type or "", {})
    return int(cfg.get("max_level") or 1)


def clan_expansion_name(expansion_type: str | None) -> str:
    info = getattr(config, "CLAN_EXPANSION_INFO", {}).get(expansion_type or "", {})
    return info.get("name") or expansion_type or "Расширение"


def clan_expansion_icon(expansion_type: str | None) -> str:
    info = getattr(config, "CLAN_EXPANSION_INFO", {}).get(expansion_type or "", {})
    return info.get("icon") or "🔧"


async def get_clan_expansions(clan_id: int) -> list:
    """Все установленные расширения клана, по порядку слотов."""
    conn = await get_db()
    cur = await conn.execute(
        "SELECT * FROM clan_expansions WHERE clan_id = ? ORDER BY slot_index",
        (clan_id,))
    return await cur.fetchall()


async def get_clan_expansion(clan_id: int, slot_index: int):
    conn = await get_db()
    cur = await conn.execute(
        "SELECT * FROM clan_expansions WHERE clan_id = ? AND slot_index = ?",
        (clan_id, int(slot_index)))
    return await cur.fetchone()


async def install_clan_expansion(clan_id: int, user_id: int, slot_index: int,
                                 expansion_type: str) -> tuple[bool, str]:
    """Установка расширения в пустой слот: бесплатно, только глава, только `built`."""
    if not await can_manage_clan_hall(clan_id, user_id):
        return False, "❌ Устанавливать расширения может только глава клана."
    row = await get_clan_building(clan_id)
    if not row or row['status'] != 'built' or not row['building_type']:
        return False, "❌ Установка расширений доступна только в готовом здании (не во время работ)."
    btype = row['building_type']
    max_slot = clan_expansion_slots(btype)
    slot_index = int(slot_index)
    if slot_index < 1 or slot_index > max_slot:
        if btype == "castle" and slot_index == CLAN_EXPANSION_RESERVE_SLOT:
            return False, "🔒 7-й слот резиденции — резерв под будущие механики."
        return False, f"❌ В этом здании доступно слотов: {max_slot}."
    exp_types = getattr(config, "CLAN_EXPANSION_TYPES", ())
    if expansion_type not in exp_types:
        return False, "❌ Неизвестный тип расширения."
    conn = await get_db()
    cur = await conn.execute(
        "SELECT slot_index FROM clan_expansions WHERE clan_id = ? AND slot_index = ?",
        (clan_id, slot_index))
    if await cur.fetchone():
        return False, "❌ Этот слот уже занят расширением."
    cur = await conn.execute(
        "SELECT slot_index FROM clan_expansions WHERE clan_id = ? AND expansion_type = ?",
        (clan_id, expansion_type))
    existing = await cur.fetchone()
    if existing:
        return False, (f"❌ Расширение «{clan_expansion_name(expansion_type)}» "
                       f"уже установлено в слоте {int(existing['slot_index'])}.")
    # Гейт «Древа Пламенного Круговорота»: нужно N Ламп у членов клана.
    if expansion_type == "tree":
        req = int(getattr(config, "FIRE_TREE_CLAN_REQ_LAMPS", 7) or 7)
        have = await count_clan_lanterns(clan_id)
        if have < req:
            return False, (f"🔒 «{clan_expansion_name('tree')}» открывается "
                           f"при {req} Лампах у членов клана — сейчас их {have}.")
    try:
        await conn.execute(
            """INSERT INTO clan_expansions (clan_id, slot_index, expansion_type, expansion_level)
               VALUES (?, ?, ?, 1)""",
            (clan_id, slot_index, expansion_type))
        if expansion_type == "tree":
            # старт таймера Эссии Памяти с момента установки Древа
            ts = (datetime.now(MOSCOW_TZ)
                  + timedelta(days=int(getattr(config, "FIRE_TREE_CLAN_ESSENCE_DAYS", 30) or 30))
                  ).timestamp()
            await conn.execute(
                "UPDATE clans SET tree_amber_at = ? WHERE id = ?",
                (str(int(ts)), clan_id))
        await conn.commit()
    except aiosqlite.IntegrityError:
        return False, "❌ Не удалось установить расширение: слот или тип уже занят."
    return True, (f"✅ В слоте {slot_index} установлено: "
                  f"{clan_expansion_icon(expansion_type)} {clan_expansion_name(expansion_type)}.")


async def upgrade_clan_expansion(clan_id: int, user_id: int,
                                 slot_index: int) -> tuple[bool, str]:
    """Мгновенное улучшение расширения: НМ главы + ресурсы с кланового склада."""
    if not await can_manage_clan_hall(clan_id, user_id):
        return False, "❌ Улучшать расширения может только глава клана."
    exp0 = await get_clan_expansion(clan_id, slot_index)
    if exp0 and exp0['expansion_type'] == 'tree':
        return False, "❌ Древо Пламенного Круговорота не улучшается."
    row = await get_clan_building(clan_id)
    if not row or row['status'] != 'built' or not row['building_type']:
        return False, "❌ Улучшать расширения можно только в готовом здании (не во время работ)."
    exp = await get_clan_expansion(clan_id, slot_index)
    if not exp:
        return False, "❌ В этом слоте нет расширения."
    level = int(exp['expansion_level'] or 1)
    max_level = clan_expansion_max_level(row['building_type'])
    if level >= max_level:
        return False, f"❌ Достигнут максимальный уровень расширения ({max_level})."
    next_level = level + 1
    upgrades = getattr(config, "CLAN_EXPANSION_UPGRADE", {})
    cfg = upgrades.get(next_level) or {}
    price_nm = int(cfg.get("nm") or 0)
    required = cfg.get("required") or {}
    if not cfg:
        return False, "❌ Для этого уровня не настроена стоимость улучшения."
    progress, all_ok = await get_clan_project_progress(clan_id, required)
    if not all_ok:
        missing = ", ".join(f"{r['name']} {r['have']}/{r['need']}"
                            for r in progress if not r['ok'])
        return False, f"❌ На складе клана не хватает ресурсов: {missing}."
    leader = await get_user(user_id)
    have_nm = int((leader['nordmarks'] if leader else 0) or 0)
    if have_nm < price_nm:
        return False, (f"❌ Недостаточно нордмарок у главы: нужно {price_nm} НМ, "
                       f"есть {have_nm} НМ.")
    to_deduct = {r['item_id']: r['need'] for r in progress
                 if r['item_id'] and r['need'] > 0}
    if to_deduct:
        await deduct_clan_storage_items(clan_id, to_deduct)
    if price_nm > 0:
        await remove_nordmarks(
            user_id, price_nm, "clan_expansion",
            f"Улучшение расширения «{clan_expansion_name(exp['expansion_type'])}» "
            f"до уровня {next_level}")
    conn = await get_db()
    await conn.execute(
        """UPDATE clan_expansions SET expansion_level = ?
           WHERE clan_id = ? AND slot_index = ?""",
        (next_level, clan_id, int(slot_index)))
    await conn.commit()
    return True, (f"⬆️ Расширение «{clan_expansion_name(exp['expansion_type'])}» "
                  f"улучшено до уровня {next_level}.")


# --- Клан-холл: библиотека рецептов (Фаза 6) ---

async def get_clan_recipes(clan_id: int):
    """Список рецептов, сданных в клановую библиотеку."""
    conn = await get_db()
    cur = await conn.execute(
        """SELECT cr.recipe_id, cr.donated_by, cr.created_at,
                  r.name as recipe_name, r.result_item_name, r.result_quantity
           FROM clan_recipes cr
           LEFT JOIN recipes r ON r.id = cr.recipe_id
           WHERE cr.clan_id = ?
           ORDER BY cr.created_at ASC""",
        (clan_id,),
    )
    return await cur.fetchall()


async def has_clan_recipe(clan_id: int, recipe_id: int) -> bool:
    conn = await get_db()
    cur = await conn.execute(
        "SELECT 1 FROM clan_recipes WHERE clan_id = ? AND recipe_id = ?",
        (clan_id, recipe_id),
    )
    row = await cur.fetchone()
    return row is not None


async def donate_recipe_to_clan_library(clan_id: int, user_id: int,
                                        item_id: int) -> tuple:
    """Сдаёт предмет-рецепт/книгу в клановую библиотеку (Фаза 6).

    Предмет (items, category='recipes') списывается из инвентаря навсегда;
    все рецепты, которые он открывает (recipe_book_items), пишутся
    в clan_recipes и становятся доступны всем членам клана.

    Возвращает (ok, текст_для_игрока, added_recipe_ids).
    """
    conn = await get_db()
    cur = await conn.execute("SELECT * FROM items WHERE id = ?", (item_id,))
    item = await cur.fetchone()
    if not item:
        return False, "Предмет не найден.", []
    if item.get('category') != 'recipes':
        return False, "Это не предмет-рецепт.", []
    inv_row = await get_inventory_item(user_id, item_id)
    if not inv_row or int(inv_row.get('quantity') or 0) < 1:
        return False, "У тебя нет этого предмета.", []
    book_rows = await get_recipe_book_recipes(item_id)
    if book_rows:
        recipe_ids = [int(r['id']) for r in book_rows if r.get('is_available')]
    else:
        # Свиток «Рецепт: <название>»: рецепт ищется по имени носителя.
        title = item.get('name') or ''
        title = title[len(RECIPE_ITEM_PREFIX):] if title.startswith(RECIPE_ITEM_PREFIX) else title
        cur = await conn.execute(
            "SELECT id FROM recipes WHERE name = ? AND is_available = 1", (title,))
        row = await cur.fetchone()
        recipe_ids = [int(row['id'])] if row else []
    if not recipe_ids:
        return False, "В этой книге нет доступных рецептов.", []
    added = []
    for rid in recipe_ids:
        if await has_clan_recipe(clan_id, rid):
            continue
        await conn.execute(
            "INSERT OR IGNORE INTO clan_recipes (clan_id, recipe_id, donated_by) "
            "VALUES (?, ?, ?)", (clan_id, rid, user_id))
        added.append(rid)
    if not added:
        return False, "Все рецепты из этой книги уже есть в клановой библиотеке.", []
    if not await remove_inventory_item(user_id, item_id, 1):
        return False, "Не удалось списать предмет из инвентаря.", []
    return True, f"Книга сдана в клановую библиотеку. Рецепт(ов) открыто: {len(added)}.", added


async def get_clan_recipes_ids(clan_id: int):
    conn = await get_db()
    cur = await conn.execute("SELECT recipe_id FROM clan_recipes WHERE clan_id = ?", (clan_id,))
    res = await cur.fetchall()
    return {r['recipe_id'] for r in res}


# --- Клан-холл: клановая лавка (Фаза 7) ---

async def get_clan_shop_items(clan_id: int, active_only: bool = True) -> list:
    """Витрина клановой лавки: позиции расширения «shop» с данными предметов."""
    conn = await get_db()
    q = ("SELECT csi.item_id, csi.price, csi.stock, csi.is_active, "
         "i.name, i.description, i.category, i.rarity, i.is_available "
         "FROM clan_shop_items csi JOIN items i ON i.id = csi.item_id "
         "WHERE csi.clan_id = ?")
    if active_only:
        q += " AND csi.is_active = 1"
    q += " ORDER BY i.name COLLATE NOCASE"
    cur = await conn.execute(q, (clan_id,))
    return await cur.fetchall()


async def get_clan_shop_item(clan_id: int, item_id: int):
    conn = await get_db()
    cur = await conn.execute(
        "SELECT csi.item_id, csi.price, csi.stock, csi.is_active, "
        "i.name, i.description, i.category, i.rarity, i.is_available "
        "FROM clan_shop_items csi JOIN items i ON i.id = csi.item_id "
        "WHERE csi.clan_id = ? AND csi.item_id = ?", (clan_id, item_id))
    return await cur.fetchone()


async def upsert_clan_shop_item(clan_id: int, item_id: int, price: int,
                                stock: int = -1, is_active: bool = True) -> bool:
    """Добавляет/обновляет позицию витрины клановой лавки (админский метод).

    price >= 1, stock = -1 — безлимит. Используется и для клановой накидки
    (личный предмет каждого клана), и для точечных товаров.
    """
    conn = await get_db()
    await conn.execute(
        "INSERT INTO clan_shop_items (clan_id, item_id, price, stock, is_active) "
        "VALUES (?, ?, ?, ?, ?) "
        "ON CONFLICT(clan_id, item_id) DO UPDATE SET "
        "price = excluded.price, stock = excluded.stock, is_active = excluded.is_active",
        (clan_id, item_id, max(1, int(price)), int(stock), 1 if is_active else 0))
    await conn.commit()
    return True


async def set_clan_shop_active(clan_id: int, item_id: int, is_active: bool) -> bool:
    conn = await get_db()
    cur = await conn.execute(
        "UPDATE clan_shop_items SET is_active = ? WHERE clan_id = ? AND item_id = ?",
        (1 if is_active else 0, clan_id, item_id))
    await conn.commit()
    return cur.rowcount > 0


async def delete_clan_shop_item(clan_id: int, item_id: int) -> bool:
    conn = await get_db()
    cur = await conn.execute(
        "DELETE FROM clan_shop_items WHERE clan_id = ? AND item_id = ?",
        (clan_id, item_id))
    await conn.commit()
    return cur.rowcount > 0


def clan_shop_day() -> str:
    """Игровые сутки лавки (по МСК, как сутки в остальной экономике)."""
    return time.strftime("%Y-%m-%d")


async def get_clan_shop_bought_today(clan_id: int, user_id: int) -> int:
    conn = await get_db()
    cur = await conn.execute(
        "SELECT qty FROM clan_shop_purchases "
        "WHERE clan_id = ? AND user_id = ? AND buy_day = ?",
        (clan_id, user_id, clan_shop_day()))
    row = await cur.fetchone()
    return int(row['qty']) if row else 0


async def buy_clan_shop_item(clan_id: int, user_id: int, item_id: int) -> tuple:
    """Покупка в клановой лавке: проверки и списания атомарной цепочкой.

    Проверяются: позиция в витрине, активность, существование предмета,
    суточный лимит покупок, остаток и баланс НМ. Хранит счётчик в
    clan_shop_purchases, выдаёт предмет в личный инвентарь.
    Возвращает (ok, текст, bought_left).
    """
    row = await get_clan_shop_item(clan_id, item_id)
    if not row:
        return False, "❌ Позиции нет в лавке.", None
    if not row.get('is_active'):
        return False, "❌ Товар скрыт из лавки.", None
    if not row.get('is_available'):
        return False, "❌ Предмет больше не существует.", None

    limit = int(getattr(config, "CLAN_SHOP_DAILY_LIMIT", 3) or 0)
    if limit > 0:
        bought = await get_clan_shop_bought_today(clan_id, user_id)
        if bought >= limit:
            return False, (f"❌ Дневной лимит покупок исчерпан "
                           f"({limit}/день)."), None
    price = max(1, int(row.get('price') or 1))
    user = await get_user(user_id)
    if not user or int(user.get('nordmarks') or 0) < price:
        return False, "❌ Не хватает НМ.", None
    stock = row.get('stock')
    stock = int(stock) if stock is not None else -1
    if stock == 0:
        return False, "❌ Распродано.", None
    conn = await get_db()
    if stock > 0:
        cur = await conn.execute(
            "UPDATE clan_shop_items SET stock = stock - 1 "
            "WHERE clan_id = ? AND item_id = ? AND stock > 0",
            (clan_id, item_id))
        if cur.rowcount == 0:
            return False, "❌ Распродано.", None
    await conn.execute(
        "INSERT INTO clan_shop_purchases (clan_id, user_id, buy_day, qty) "
        "VALUES (?, ?, ?, 1) "
        "ON CONFLICT(clan_id, user_id, buy_day) DO UPDATE SET qty = qty + 1",
        (clan_id, user_id, clan_shop_day()))
    # Баланс уже подтверждён прямой проверкой — списываем.
    await remove_nordmarks(user_id, price, "clan_shop",
                           f"Покупка в клановой лавке")
    # НМ списаны — зачисляем предмет
    await add_inventory_item(user_id, item_id, 1)
    bought_now = await get_clan_shop_bought_today(clan_id, user_id) \
        if limit > 0 else None
    left = (limit - bought_now) if limit > 0 else None
    return True, (f"🏪 Куплено: {row.get('name')} — списано {price} НМ."), left
