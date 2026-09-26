import json
import time
import aiosqlite
from config import (DB_PATH, SPECIAL_DEPT_ATTEMPTS_LIMIT, SPECIAL_DEPT_BLOCK_MINUTES,
                    DUNGEON_RUN_STALE_SEC)
from config import get_effective_rank

db: aiosqlite.Connection | None = None


async def get_db() -> aiosqlite.Connection:
    global db
    if db is None:
        db = await aiosqlite.connect(DB_PATH, isolation_level=None)

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
            nordmarks_earned INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );

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
            troops_24h INTEGER DEFAULT 0,
            active_pilots_72h INTEGER DEFAULT 0,
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

        CREATE TABLE IF NOT EXISTS admin_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            target_id INTEGER,
            details TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

        CREATE TABLE IF NOT EXISTS nii_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            photo_file_id TEXT,
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

        CREATE TABLE IF NOT EXISTS clans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kind TEXT NOT NULL DEFAULT 'clan',          -- 'clan' | 'party'
            name TEXT NOT NULL,
            description TEXT DEFAULT '',
            photo_file_id TEXT,
            leader_id INTEGER,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS clan_members (
            clan_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (clan_id, user_id)
        );

        CREATE TABLE IF NOT EXISTS clan_requests (
            clan_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (clan_id, user_id)
        );

        CREATE TABLE IF NOT EXISTS user_recipes (
            user_id INTEGER NOT NULL,
            recipe_id INTEGER NOT NULL,
            learned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, recipe_id)
        );
    """)
    await conn.commit()

    # Миграция: колонки required_status и sort_order (если нет)
    await _ensure_column(conn, "items", "required_status", "TEXT")
    await _ensure_column(conn, "buildings", "required_status", "TEXT")
    await _ensure_column(conn, "statuses", "sort_order", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "users", "promoted_rank", "TEXT")
    await _ensure_column(conn, "users", "notify_enabled", "INTEGER DEFAULT 1")
    await _ensure_column(conn, "users", "profile_public", "INTEGER DEFAULT 1")
    await _ensure_column(conn, "users", "about", "TEXT DEFAULT ''")
    await _ensure_column(conn, "users", "equipment", "TEXT DEFAULT '{}'")
    await _ensure_column(conn, "users", "salary", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "users", "salary_period_days", "INTEGER DEFAULT 7")
    await _ensure_column(conn, "users", "last_salary_date", "TIMESTAMP")
    await _ensure_column(conn, "users", "salary_debt", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "items", "armor", "INTEGER DEFAULT 0")
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
    await _ensure_column(conn, "player_dungeon_run", "loot_nm", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "player_dungeon_run", "started_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    # «Аптечка» — это +AP (энергетик); лечит HP в данже «Малая настойка здоровья»
    await conn.execute("UPDATE items SET name = 'Энергетик', description = 'Восстанавливает силы: даёт +AP при использовании.' WHERE name = 'Аптечка'")
    await _ensure_column(conn, "users", "ap_restored_day", "TEXT DEFAULT NULL")
    await _ensure_column(conn, "users", "ap_restored_today", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "items", "damage", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "items", "heal", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "dungeon_enemies", "drops", "TEXT DEFAULT '[]'")
    await _ensure_column(conn, "dungeon_enemies", "image", "TEXT")
    await _ensure_column(conn, "dungeon_enemies", "poison_chance", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "dungeon_enemies", "poison_dmg", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "dungeon_enemies", "description", "TEXT")
    await _ensure_column(conn, "dungeon_enemies", "dodge", "INTEGER DEFAULT 0")
    # admin_tuned=1 — врага правил админ через бота: стартовая синхронизация
    # (ensure_dungeon_enemy_drops / seed_kvp) больше не перезаписывает его характеристики.
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
    # Выкуп рыбы казной: суточный лимит НМ на игрока (FISH_TREASURY_DAILY_LIMIT)
    await _ensure_column(conn, "users", "fish_sold_day", "TEXT DEFAULT NULL")
    await _ensure_column(conn, "users", "fish_sold_today", "INTEGER DEFAULT 0")
    # Встроенные расширения жилья (например, кухня в студии): embedded=1 — не возвращается
    # в инвентарь при переезде и не может быть снята вручную.
    await _ensure_column(conn, "housing_slots", "embedded", "INTEGER DEFAULT 0")
    # Счётчик установок расширений: первая в доме — бесплатно, далее перепланировка платная.
    await _ensure_column(conn, "player_housing", "expansions_installed", "INTEGER DEFAULT 0")
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
    # v0.10.0: рынок (слоты продажи + лицензия) и налог на жильё
    await _ensure_column(conn, "dungeons", "is_training", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "users", "market_license_expires", "TEXT DEFAULT NULL")
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
    # v0.15.0: авиакрыло пилота ('1'/'2'/'3' → метка в utils/wings.py; NULL — нет крыла).
    await _ensure_column(conn, "users", "wing", "TEXT")
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
    await conn.commit()
    await seed_locations(conn)
    # Снятые с игры предметы (T-Меч, T-Броня, учебные машины) — полное удаление.
    await purge_retired_items()


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
        ("nii", "НИИ Северной Кибернетики и кремниевых систем", "НИИ Северной Кибернетики и кремниевых систем: здесь пилоты оставляют жалобы и запросы на доработку бота.",
         "all", None, ["пьян"], "city/nii"),
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


async def add_nordmarks(user_id: int, amount: int, tx_type: str, description: str = ""):
    conn = await get_db()
    await conn.execute("UPDATE users SET nordmarks = nordmarks + ? WHERE user_id = ?", (amount, user_id))
    await conn.execute(
        "INSERT INTO transactions (to_user, amount, tx_type, description) VALUES (?, ?, ?, ?)",
        (user_id, amount, tx_type, description)
    )
    await conn.commit()


async def remove_nordmarks(user_id: int, amount: int, tx_type: str, description: str = ""):
    conn = await get_db()
    await conn.execute("UPDATE users SET nordmarks = nordmarks - ? WHERE user_id = ?", (amount, user_id))
    await conn.execute(
        "INSERT INTO transactions (from_user, amount, tx_type, description) VALUES (?, ?, ?, ?)",
        (user_id, amount, tx_type, description)
    )
    await conn.commit()


async def transfer_nordmarks(from_user: int, to_user: int, amount: int, description: str = ""):
    conn = await get_db()
    await conn.execute("UPDATE users SET nordmarks = nordmarks - ? WHERE user_id = ?", (amount, from_user))
    await conn.execute("UPDATE users SET nordmarks = nordmarks + ? WHERE user_id = ?", (amount, to_user))
    await conn.execute(
        "INSERT INTO transactions (from_user, to_user, amount, tx_type, description) VALUES (?, ?, ?, ?, ?)",
        (from_user, to_user, amount, "transfer", description)
    )
    await conn.commit()


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


async def daily_ap_recovery():
    """Суточное восстановление ОД — раз в сутки.

    Начисляет AP_DAILY_RECOVERY (100 ОД) до потолка ap_max; для состояния
    «истощён» — AP_EXHAUSTED_DAILY_RECOVERY (75 ОД) до AP_EXHAUSTED_MAX_AP (90).
    Срабатывает только если день не совпадает с users.ap_recovery_day: рестарты
    бота посреди дня не раздают ОД повторно. Счётчики (ap_restored_today,
    seaweed_used_today, fountain_used_today) обнуляются при смене суток.
    Каждое начисление пишется в ap_log.
    """
    from config import (AP_DAILY_RECOVERY, AP_EXHAUSTED_DAILY_RECOVERY, AP_EXHAUSTED_MAX_AP)
    today = datetime.utcnow().strftime("%Y-%m-%d")
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

    # Обнуление суточных счётчиков при смене суток (то же поведение, что и раньше).
    await conn.execute("""
        UPDATE users SET
            ap_restored_today = CASE WHEN ap_restored_day = date('now') THEN ap_restored_today ELSE 0 END,
            ap_restored_day = CASE WHEN ap_restored_day = date('now') THEN ap_restored_day ELSE date('now') END,
            seaweed_used_today = CASE WHEN seaweed_used_day = date('now') THEN seaweed_used_today ELSE 0 END,
            seaweed_used_day = CASE WHEN seaweed_used_day = date('now') THEN seaweed_used_day ELSE date('now') END,
            fountain_used_today = CASE WHEN fountain_used_day = date('now') THEN fountain_used_today ELSE 0 END,
            fountain_used_day = CASE WHEN fountain_used_day = date('now') THEN fountain_used_day ELSE date('now') END,
            fish_sold_today = CASE WHEN fish_sold_day = date('now') THEN fish_sold_today ELSE 0 END,
            fish_sold_day = CASE WHEN fish_sold_day = date('now') THEN fish_sold_day ELSE date('now') END
    """)
    await conn.commit()


async def add_item(name: str, description: str, price: int, sell_price: int,
                   rarity: int, category: str, stock: int, added_by: int,
                   photo_file_id: str = None, ap_cost: int = 0,
                   production_time_hours: int = 0, produced_by: int = None,
                   damage: int = 0, heal: int = 0, armor: int = 0,
                   drink_effect: str = None, equip_slot: str = None,
                   market_ok: int = None, plant_name: str = None,
                   weapon_effect: str = None,
                   weapon_effect_chance: int = 0,
                   weapon_effect_dmg: int = 0,
                   housing_type: str = None,
                   housing_slots: int = None,
                   regen: int = 0,
                   required_status: str = None):
    conn = await get_db()
    # v0.13.3: рыба (категория fishing) по умолчанию выставляется на рынок;
    # у остальных предметов — только скупщик, пока админ не включит флаг.
    if market_ok is None:
        market_ok = 1 if category == "fishing" else 0
    cursor = await conn.execute(
        """INSERT INTO items (name, description, photo_file_id, price, sell_price,
           rarity, category, stock, added_by, ap_cost, production_time_hours, produced_by, damage, heal, armor, drink_effect, equip_slot, market_ok, plant_name,
           weapon_effect, weapon_effect_chance, weapon_effect_dmg, housing_type, housing_slots, regen, required_status)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (name, description, photo_file_id, price, sell_price, rarity, category,
         stock, added_by, ap_cost, production_time_hours, produced_by, damage, heal, armor, drink_effect, equip_slot, market_ok, plant_name,
         weapon_effect or None, weapon_effect_chance, weapon_effect_dmg,
         housing_type, housing_slots, regen, required_status)
    )
    await conn.commit()
    return cursor.lastrowid


async def get_item(item_id: int):
    conn = await get_db()
    cursor = await conn.execute("SELECT * FROM items WHERE id = ?", (item_id,))
    return await cursor.fetchone()


async def get_available_items(category: str = None, rarity: int = None):
    conn = await get_db()
    query = "SELECT * FROM items WHERE is_available = 1"
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
    today = datetime.utcnow().strftime("%Y-%m-%d")
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

            today = datetime.utcnow().strftime("%Y-%m-%d")
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
    conn = await get_db()
    cursor = await conn.execute(
        "INSERT INTO polls (admin_id, question, options) VALUES (?, ?, ?)",
        (admin_id, question, options)
    )
    await conn.commit()
    return cursor.lastrowid


async def get_polls_created_today(admin_id: int) -> int:
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT COUNT(*) AS cnt FROM polls WHERE admin_id = ? "
        "AND created_at >= datetime('now', 'start of day')",
        (admin_id,)
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
    """Сколько выпусков опубликовал игрок за текущие сутки (МСК)."""
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT COUNT(*) AS cnt FROM news_releases "
        "WHERE author_id = ? AND substr(created_at, 1, 10) = ?",
        (user_id, datetime.now(MOSCOW_TZ).strftime("%Y-%m-%d"))
    )
    row = await cursor.fetchone()
    return row['cnt'] if row else 0


NII_DAILY_LIMIT = 2  # максимум обращений в сутки от одного пилота


async def count_nii_reports_today(user_id: int) -> int:
    """Сколько обращений в НИИ пилот отправил за текущие сутки (МСК)."""
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT COUNT(*) AS cnt FROM nii_reports "
        "WHERE user_id = ? AND date(created_at, 'localtime') = date('now', 'localtime')",
        (user_id,)
    )
    row = await cursor.fetchone()
    return row['cnt'] if row else 0


async def add_nii_report(user_id: int, text: str, photo_file_id: str = None) -> int:
    """Сохранить обращение в НИИ. Возвращает id записи."""
    conn = await get_db()
    cursor = await conn.execute(
        "INSERT INTO nii_reports (user_id, text, photo_file_id, status, created_at) "
        "VALUES (?, ?, ?, 'open', ?)",
        (user_id, text, photo_file_id, datetime.now(MOSCOW_TZ).isoformat())
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
    """Пилоты, которым пора выплатить зарплату.

    Фиксированный календарный график: выплата один раз в неделю,
    в воскресенье (UTC). Не зависит от даты назначения зарплаты.
    Защита от дублей: платим, только если в текущей календарной
    неделе выплата ещё не проводилась.
    """
    conn = await get_db()
    # date('now','weekday 0','-6 days') — понедельник текущей календарной недели (UTC)
    cursor = await conn.execute(
        "SELECT user_id, username, first_name, salary, salary_debt FROM users "
        "WHERE salary IS NOT NULL AND salary > 0 "
        "AND strftime('%w', 'now') = '0' "
        "AND (last_salary_date IS NULL OR "
        "     date(last_salary_date) < date('now', 'weekday 0', '-6 days'))"
    )
    return await cursor.fetchall()


async def mark_salary_paid(user_id: int):
    conn = await get_db()
    await conn.execute(
        "UPDATE users SET last_salary_date = datetime('now') WHERE user_id = ?", (user_id,)
    )
    await conn.commit()


async def pay_salaries() -> dict:
    """Выплачивает зарплаты всем, кому пора (календарное воскресенье).

    Логика: оплачивается ставка за неделю + накопленный ранее долг.
    Если казны не хватает — платим сколько возможно (если есть хоть что-то),
    остаток копится в salary_debt, last_salary_date не меняется (долг растёт
    каждую пропущенную неделю). Возвращает статистику для уведомления.
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

from datetime import datetime, timedelta
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
        "SELECT COUNT(*) AS cnt FROM reports WHERE user_id = ? AND date(created_at) = date('now')",
        (user_id,)
    )
    row = await cursor.fetchone()
    return row['cnt'] if row else 0


def _wall_today_key() -> str:
    """Ключ текущих суток по МСК (YYYY-MM-DD) для лимита «N изречений в сутки»."""
    from utils.helpers import MOSCOW_TZ
    from datetime import datetime
    return datetime.now(MOSCOW_TZ).strftime("%Y-%m-%d")


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
    if count >= WALL_REVIEW_TOTAL:
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


async def wall_author_name(user) -> str:
    """Имя автора изречения: позывной, @username, иначе реальное имя."""
    if not user:
        return "Неизвестный"
    from bot.handlers.profile import _pilot_name
    return _pilot_name(user)


async def add_report(user_id: int, screenshot_file_id: str, troops_reported: int, total_troops: int = 0, region: str = ""):
    """Добавить отчёт. Возвращает (report_id, credited_troops).

    За сутки оплачивается только дельта между ранее засчитанным значением
    (последний одобренный отчёт за сегодня) и новым значением.
    troops_reported хранит заявленное значение, credited_troops — сумму к оплате.
    """
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT COALESCE(MAX(troops_reported), 0) AS prev_today FROM reports "
        "WHERE user_id = ? AND status = 'approved' AND date(created_at) = date('now')",
        (user_id,)
    )
    row = await cursor.fetchone()
    prev_today = row['prev_today'] if row else 0
    credited = max(0, troops_reported - prev_today)

    cursor = await conn.execute(
        "INSERT INTO reports (user_id, screenshot_file_id, troops_reported, total_troops, region, credited_troops) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, screenshot_file_id, troops_reported, total_troops, region, credited)
    )
    await conn.commit()
    return cursor.lastrowid, credited


async def approve_report(report_id: int, reviewed_by: int, troops: int):
    """Одобрить отчёт. Возвращает дельту к начислению (войск) или False,
    если отчёт не найден.

    Дельту пересчитываем на момент одобрения: база — максимальное заявленное значение
    среди УЖЕ одобренных за сегодня отчётов (этот ещё не одобрен). Это исключает двойную
    оплату, когда отчёт ждёт проверки, а пилот параллельно сдал и получил оплату за
    больший отчёт. Итог за сутки всегда = максимум заявки, а не сумма.

    Начисление здесь НЕ производится: допущенные отчёты копятся, а оплата выполняется
    раз в сутки функцией payout_reports() (в начале следующих суток).

    Для старых отчётов (credited_troops IS NULL, до введения дельты) — вся заявка целиком.
    """
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT user_id, troops_reported, credited_troops FROM reports WHERE id = ?", (report_id,)
    )
    row = await cursor.fetchone()
    if not row:
        return False

    user_id = row['user_id']
    if troops is not None and row['credited_troops'] is not None:
        cursor = await conn.execute(
            "SELECT COALESCE(MAX(troops_reported), 0) AS approved_today FROM reports "
            "WHERE user_id = ? AND status = 'approved' AND id != ? "
            "AND date(created_at) = date('now')",
            (user_id, report_id)
        )
        base_row = await cursor.fetchone()
        base = base_row['approved_today'] if base_row else 0
        troops = max(0, row['troops_reported'] - base)
    else:
        troops = row['credited_troops'] if row['credited_troops'] is not None else row['troops_reported']

    await conn.execute(
        "UPDATE reports SET status = 'approved', reviewed_by = ?, credited_troops = ?, paid = 0 WHERE id = ?",
        (reviewed_by, troops, report_id)
    )
    await conn.commit()
    return troops


async def payout_reports() -> list:
    """Суточное начисление за одобренные отчёты (раз в начале следующих суток).

    Собирает все одобренные, ещё не оплаченные отчёты (paid = 0), одной суммой
    начисляет войска и нордмарки (за вычетом налога в казну), помечает их
    оплаченными. Возвращает итоги для уведомлений:
    [{'user_id', 'troops', 'nordmarks', 'tax', 'count', 'total_troops', 'total_nordmarks'}]
    """
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT r.user_id, r.id AS report_id, COALESCE(r.credited_troops, r.troops_reported) AS troops "
        "FROM reports r WHERE r.status = 'approved' AND r.paid = 0"
    )
    rows = await cursor.fetchall()
    if not rows:
        return []

    agg = {}
    for r in rows:
        entry = agg.setdefault(r['user_id'], {'report_ids': [], 'troops': 0})
        entry['report_ids'].append(r['report_id'])
        entry['troops'] += r['troops']

    tax_percent = await get_report_tax_percent()
    results = []
    for uid, data in agg.items():
        troops_total = data['troops']
        report_ids = data['report_ids']
        placeholders = ", ".join("?" * len(report_ids))
        if troops_total <= 0:
            await conn.execute(f"UPDATE reports SET paid = 1 WHERE id IN ({placeholders})", report_ids)
            continue
        tax = int(troops_total * tax_percent / 100)
        nordmarks = troops_total - tax
        await conn.execute("UPDATE users SET troops = troops + ? WHERE user_id = ?", (troops_total, uid))
        await conn.execute("UPDATE users SET nordmarks = nordmarks + ? WHERE user_id = ?", (nordmarks, uid))
        await conn.execute(
            "INSERT INTO transactions (to_user, amount, tx_type, description) VALUES (?, ?, ?, ?)",
            (uid, nordmarks, "report",
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
            "SELECT troops, nordmarks, promoted_rank FROM users WHERE user_id = ?", (uid,)
        )
        u = await cur.fetchone()
        if u:
            rank = get_effective_rank(u['troops'], u['promoted_rank'])
            await grant_status_for_rank(uid, rank)
        results.append({
            'user_id': uid,
            'troops': troops_total,
            'nordmarks': nordmarks,
            'tax': tax,
            'count': len(report_ids),
            'total_troops': u['troops'] if u else troops_total,
            'total_nordmarks': u['nordmarks'] if u else nordmarks,
        })
    await conn.commit()
    return results


async def reject_report(report_id: int, reviewed_by: int):
    conn = await get_db()
    await conn.execute(
        "UPDATE reports SET status = 'rejected', reviewed_by = ? WHERE id = ?",
        (reviewed_by, report_id)
    )
    await conn.commit()


async def get_pending_reports():
    conn = await get_db()
    cursor = await conn.execute(
        """SELECT r.*, u.first_name, u.username FROM reports r
           JOIN users u ON r.user_id = u.user_id
           WHERE r.status = 'pending' ORDER BY r.created_at"""
    )
    return await cursor.fetchall()


async def get_user_reports(user_id: int):
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT * FROM reports WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,)
    )
    return await cursor.fetchall()


async def recompute_region_stats():
    """Пересчитывает статистику по регионам из одобренных отчётов.

    troops_24h        — по каждому пилоту и календарным суткам берётся ТОЛЬКО
                        последний отчёт за сутки (его troops_reported), затем сумма
                        по региону за последние 24 часа
    active_pilots_72h — число уникальных пилотов с одобренными отчётами за последние 72 часа
    """
    conn = await get_db()
    await conn.execute("DELETE FROM region_stats")

    cur = await conn.execute("""
        SELECT region, COUNT(DISTINCT user_id) AS pilots
        FROM reports
        WHERE status = 'approved'
          AND region IS NOT NULL AND region != ''
          AND created_at >= datetime('now', '-72 hours')
        GROUP BY region
    """)
    pilots_72 = {row['region']: row['pilots'] for row in await cur.fetchall()}

    cur = await conn.execute("""
        SELECT region, COALESCE(SUM(troops_reported), 0) AS troops_24h
        FROM (
            SELECT r.region, r.troops_reported,
                   ROW_NUMBER() OVER (
                       PARTITION BY r.user_id, date(r.created_at)
                       ORDER BY r.created_at DESC, r.id DESC
                   ) AS rn
            FROM reports r
            WHERE r.status = 'approved'
              AND r.region IS NOT NULL AND r.region != ''
              AND r.created_at >= datetime('now', '-24 hours')
        )
        WHERE rn = 1
        GROUP BY region
    """)
    troops_24h = {row['region']: row['troops_24h'] for row in await cur.fetchall()}

    regions = set(list(pilots_72.keys()) + list(troops_24h.keys()))
    for region in regions:
        await conn.execute(
            "INSERT INTO region_stats (region, troops_24h, active_pilots_72h, computed_at) "
            "VALUES (?, ?, ?, datetime('now'))",
            (region, troops_24h.get(region, 0), pilots_72.get(region, 0))
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

    Возвращает число статусов, выданных заново. Идемпотентна.
    """
    conn = await get_db()
    cursor = await conn.execute("SELECT user_id, troops, promoted_rank FROM users")
    rows = await cursor.fetchall()
    granted = 0
    for row in rows:
        rank = get_effective_rank(row['troops'], row['promoted_rank'])
        if await grant_status_for_rank(row['user_id'], rank):
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
    await grant_status_for_rank(user_id, rank_name, promoted_by)


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


async def get_transactions_history(user_id: int, limit: int = 10):
    conn = await get_db()
    cursor = await conn.execute("""
        SELECT * FROM transactions
        WHERE from_user = ? OR to_user = ?
        ORDER BY created_at DESC LIMIT ?
    """, (user_id, user_id, limit))
    return await cursor.fetchall()


async def get_all_users():
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT user_id, username, first_name, last_name, wing FROM users"
    )
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
    # самый сильный статус игрока
    cursor = await conn.execute("""
        SELECT MAX(s.sort_order) as top FROM user_statuses us
        JOIN statuses s ON us.status_id = s.id
        WHERE us.user_id = ?
    """, (user_id,))
    top = (await cursor.fetchone())['top']
    if top is None:
        return False
    return top >= req['sort_order']


async def user_status_visibility_top(user_id: int):
    """Верхняя граница sort_order для видимости предметов магазина.

    Для мотивации и «неожиданности» новинок игрок видит товары своего статуса
    и одной следующей ступени иерархии (требуется статус не далее следующего),
    а предметы на две ступени выше и дальше — скрываются.

    Возвращает sort_order этого статуса-«витрины»; None — если у игрока нет
    статусов (видны только товары без требования).
    """
    conn = await get_db()
    cursor = await conn.execute("""
        SELECT MAX(s.sort_order) as top FROM user_statuses us
        JOIN statuses s ON us.status_id = s.id
        WHERE us.user_id = ?
    """, (user_id,))
    top = (await cursor.fetchone())['top']
    if top is None:
        return None
    cursor = await conn.execute(
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
                       created_by: int = None):
    conn = await get_db()
    try:
        cursor = await conn.execute(
            "INSERT INTO awards (name, description, emoji, created_by) VALUES (?, ?, ?, ?)",
            (name, description, emoji, created_by)
        )
        await conn.commit()
        return True, cursor.lastrowid
    except Exception:
        return False, "Награда с таким названием уже существует"


async def get_all_awards():
    conn = await get_db()
    cursor = await conn.execute("SELECT * FROM awards ORDER BY id")
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
               "bonus_dodge", "bonus_fishing", "bonus_hp"}
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
    """Суммарные бонусы всех наград игрока (в %; hp — в единицах HP)."""
    conn = await get_db()
    cursor = await conn.execute("""
        SELECT COALESCE(SUM(a.bonus_attack), 0) AS attack,
               COALESCE(SUM(a.bonus_defense), 0) AS defense,
               COALESCE(SUM(a.bonus_dodge), 0) AS dodge,
               COALESCE(SUM(a.bonus_fishing), 0) AS fishing,
               COALESCE(SUM(a.bonus_hp), 0) AS hp
        FROM user_awards ua
        JOIN awards a ON ua.award_id = a.id
        WHERE ua.user_id = ?
    """, (user_id,))
    row = await cursor.fetchone()
    return dict(row) if row else {"attack": 0, "defense": 0, "dodge": 0, "fishing": 0, "hp": 0}


async def set_callsign(user_id: int, callsign: str):
    """Устанавливает игровой позывной пилота (показывается в карточке)."""
    conn = await get_db()
    await conn.execute("UPDATE users SET callsign = ? WHERE user_id = ?",
                       (callsign or None, user_id))
    await conn.commit()


async def set_wing(user_id: int, wing: str = None):
    """Устанавливает авиакрыло пилота ('1'/'2'/'3'); None — снять крыло."""
    conn = await get_db()
    await conn.execute("UPDATE users SET wing = ? WHERE user_id = ?",
                       (wing if wing else None, user_id))
    await conn.commit()


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


async def add_user_role(user_id: int, role: str, granted_by: int = None):
    """Выдать роль пилоту (INSERT OR IGNORE) — например, wing_commander."""
    conn = await get_db()
    await conn.execute(
        "INSERT OR IGNORE INTO user_roles (telegram_id, role, granted_by) VALUES (?, ?, ?)",
        (user_id, role, granted_by)
    )
    await conn.commit()


async def remove_user_role(user_id: int, role: str):
    """Снять роль с пилота."""
    conn = await get_db()
    await conn.execute("DELETE FROM user_roles WHERE telegram_id = ? AND role = ?",
                       (user_id, role))
    await conn.commit()


async def grant_award(user_id: int, award_id: int, granted_by: int = None,
                      comment: str = None):
    conn = await get_db()
    try:
        await conn.execute(
            "INSERT INTO user_awards (user_id, award_id, granted_by, comment) VALUES (?, ?, ?, ?)",
            (user_id, award_id, granted_by, comment)
        )
        await conn.commit()
        return True, "Награда выдана"
    except Exception as e:
        error = str(e).lower()
        if "foreign key" in error:
            return False, "Игрок не найден — регистрация нужна через /start"
        return False, "Не удалось выдать награду"


async def revoke_award(user_award_id: int):
    conn = await get_db()
    await conn.execute("DELETE FROM user_awards WHERE id = ?", (user_award_id,))
    await conn.commit()


async def get_user_awards(user_id: int):
    """Награды игрока (с данными награды и датой выдачи)."""
    conn = await get_db()
    cursor = await conn.execute("""
        SELECT ua.id as grant_id, ua.comment, ua.created_at AS granted_at,
               a.id AS award_id, a.name, a.description, a.emoji
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
    if not tag:
        return True
    conn = await get_db()
    # уровень (sort_order) требуемого тега
    cursor = await conn.execute(
        "SELECT sort_order FROM statuses WHERE access_tag = ?", (tag,))
    req = await cursor.fetchone()
    if not req:
        return False
    # самый сильный статус игрока
    cursor = await conn.execute("""
        SELECT MAX(s.sort_order) as top FROM user_statuses us
        JOIN statuses s ON us.status_id = s.id
        WHERE us.user_id = ?
    """, (user_id,))
    top = (await cursor.fetchone())['top']
    if top is None:
        return False
    return top >= req['sort_order']


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
    """Текущие сутки (МСК) для лимита выкупа рыбы казной."""
    from utils.helpers import MOSCOW_TZ
    return datetime.now(MOSCOW_TZ).strftime("%Y-%m-%d")


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
        ("Мерцающий сом", 62, 62),
        ("Искрящийся угорь", 33, 33),
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
               wf.photo_file_id, wf.admin_tuned, wf.kind,
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
               wf.photo_file_id, wf.admin_tuned, wf.kind,
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


def _enemy_to_fields(enemy):
    """Раскладывает кортеж врага DEFAULT_DUNGEON в словарь полей БД.

    Позиции: name, hp, atk, reward, is_boss, drops, image, poison_chance,
    poison_dmg, dodge, bleed_chance, bleed_dmg, frostbite_chance, description.
    """
    (name, hp, atk, reward, is_boss, drops) = enemy[:6]
    return {
        "name": name,
        "hp": hp,
        "attack": atk,
        "reward_nm": reward,
        "is_boss": int(is_boss),
        "drops": drops,
        "image": enemy[6] if len(enemy) > 6 else None,
        "poison_chance": enemy[7] if len(enemy) > 7 else 0,
        "poison_dmg": enemy[8] if len(enemy) > 8 else 0,
        "dodge": enemy[9] if len(enemy) > 9 else 0,
        "bleed_chance": enemy[10] if len(enemy) > 10 else 0,
        "bleed_dmg": enemy[11] if len(enemy) > 11 else 0,
        "frostbite_chance": enemy[12] if len(enemy) > 12 else 0,
        "description": enemy[13] if len(enemy) > 13 else None,
    }


DUNGEON_ENEMY_INSERT_COLS = (
    "dungeon_id, floor, name, hp, attack, reward_nm, is_boss, drops, image, "
    "poison_chance, poison_dmg, dodge, bleed_chance, bleed_dmg, frostbite_chance, description"
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
                f"VALUES ({','.join(['?'] * 16)})",
                (dungeon_id, floor_idx, f["name"], f["hp"], f["attack"], f["reward_nm"],
                 f["is_boss"], json.dumps(f["drops"], ensure_ascii=False), f["image"],
                 f["poison_chance"], f["poison_dmg"], f["dodge"],
                 f["bleed_chance"], f["bleed_dmg"], f["frostbite_chance"], f["description"])
            )
        boss = floor_data["boss"]
        bf = _enemy_to_fields(boss)
        await conn.execute(
            f"INSERT INTO dungeon_enemies ({DUNGEON_ENEMY_INSERT_COLS}) "
            f"VALUES ({','.join(['?'] * 16)})",
            (dungeon_id, floor_idx, bf["name"], bf["hp"], bf["attack"], bf["reward_nm"],
             bf["is_boss"], json.dumps(bf["drops"], ensure_ascii=False), bf["image"],
             bf["poison_chance"], bf["poison_dmg"], bf["dodge"],
             bf["bleed_chance"], bf["bleed_dmg"], bf["frostbite_chance"], bf["description"])
        )

    await conn.commit()
    return True


# ============ ДАНЖ: КУРС ВЫЖИВАНИЯ ДЛЯ ПИЛОТОВ (К.В.П.) ============

KVP_DUNGEON_NAME = "Курс Выживания для Пилотов (К.В.П.)"
KVP_BADGE_NAME = "Значок В.У.С.П."
KVP_MAX_COMPLETIONS = 4
KVP_OD_COST = 5  # стоимость прохождения препятствия (одиночное действие)

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
            "INSERT INTO dungeon_enemies (dungeon_id, floor, name, hp, attack, reward_nm, is_boss, drops, image, poison_chance, poison_dmg, dodge, description) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (dungeon_id, 1, name, hp, atk, reward, int(is_boss),
             json.dumps(drops, ensure_ascii=False), image, poison_chance, poison_dmg, dodge, desc)
        )
    await conn.commit()
    return dungeon_id


async def get_kvp_dungeon():
    """Возвращает тренировочный данж К.В.П. или None."""
    dungeons = await get_all_dungeons(training=True)
    return dungeons[0] if dungeons else None


async def ensure_kvp_items():
    """Добавляет предметы К.В.П. (Офицерский стек), если их ещё нет.

    «Офицерский стек» — эксклюзивный лут босса для новичков: в магазине не
    продаётся (is_available=0), а продажа игроком не возвращает его в продажу.
    """
    conn = await get_db()
    cursor = await conn.execute("SELECT id FROM items WHERE name = 'Офицерский стек'")
    row = await cursor.fetchone()
    if row:
        # Миграция: скрыть из магазина уже созданный предмет.
        await conn.execute(
            "UPDATE items SET is_available = 0 WHERE name = 'Офицерский стек'")
        await conn.commit()
        return
    item_id = await add_item(
        name="Офицерский стек",
        description="Офицерский стек Старшего сержанта. Тяжёлый, но дисциплинирующий.",
        price=100, sell_price=50, rarity=3, category="weapon",
        stock=-1, added_by=0, ap_cost=0,
        damage=2, heal=0, armor=0, drink_effect=None
    )
    await update_item(item_id, is_available=0)


async def ensure_kvp_award():
    """Создаёт награду «Значок В.У.С.П.», если её ещё нет; обновляет описание у существующей."""
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
ENEMY_EDITABLE_FIELDS = ("hp", "attack", "dodge", "poison_chance",
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


async def get_player_dodge(user_id: int, dodge_mult: float = 1.0) -> int:
    """Уклонение пилота в %: база 3% + суммарный бонус наград, × модификатор состояний."""
    dodge = PLAYER_BASE_DODGE
    dodge += (await get_award_bonus(user_id))['dodge']
    if dodge_mult != 1.0:
        dodge = int(round(dodge * dodge_mult))
    return max(0, dodge)


async def get_player_armor_with_bonus(user_id: int) -> int:
    """Защита брони с учётом % бонуса защиты от наград."""
    armor = await get_player_armor(user_id)
    if armor <= 0:
        return 0
    bonus = await get_award_bonus(user_id)
    return int(round(armor * (1 + bonus['defense'] / 100.0)))


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
        ("Яблочное семечко", "Семечко яблони. Посади в кадку в жилье — вырастет яблоня.",
         30, 15, 1, "seeds", 10, 0, "pilot2", 1),
        ("Бутылка чистой воды", "Чистая вода из артезианской скважины. Основа для настоек и энергетиков.",
         20, 10, 1, "resource", -1, 0, "pilot2", 1),
        ("Соль", "Каменная соль из лавки. Специи для готовки рыбы: ни одно жареное блюдо не обходится без щепотки.",
         5, 2, 1, "consumable", -1, 0, None, 1),
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
         1200, 600, 4),
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
         2000, 1000, 4, 140),
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
                    f"VALUES ({','.join(['?'] * 16)})",
                    (dungeon_id, floor_idx, f["name"], f["hp"], f["attack"], f["reward_nm"],
                     f["is_boss"], drops_json, f["image"],
                     f["poison_chance"], f["poison_dmg"], f["dodge"],
                     f["bleed_chance"], f["bleed_dmg"], f["frostbite_chance"], f["description"])
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
                            "bleed_chance = ?, bleed_dmg = ?, frostbite_chance = ?"
                    base_vals += [f["description"], f["hp"], f["attack"], f["reward_nm"],
                                  drops_json, f["image"],
                                  f["poison_chance"], f["poison_dmg"], f["dodge"],
                                  f["bleed_chance"], f["bleed_dmg"], f["frostbite_chance"]]
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


# ---------- Рецепты ----------

RECIPES_DEF = [
    {"name": "Пожарить сига", "desc": "Жареный сиг со специями: +15 HP в бою подземелья. Срок годности: 4 суток.",
     "result": "Жареный сиг", "qty": 1, "exp": "kitchen", "lvl": 1,
     "ingredients": [("Сиг", 1), ("Соль", 1)], "ap": 5, "time": 20, "rarity": 1},
    {"name": "Пожарить муксуна", "desc": "Жареный муксун со специями: +30 HP в бою подземелья. Срок годности: 4 суток.",
     "result": "Жареный муксун", "qty": 1, "exp": "kitchen", "lvl": 1,
     "ingredients": [("Муксун", 1), ("Соль", 1)], "ap": 5, "time": 20, "rarity": 1},
    {"name": "Пожарить чира", "desc": "Жареный чир со специями: +45 HP в бою подземелья. Срок годности: 4 суток.",
     "result": "Жареный чир", "qty": 1, "exp": "kitchen", "lvl": 1,
     "ingredients": [("Чир", 1), ("Соль", 1)], "ap": 7, "time": 25, "rarity": 1},
    {"name": "Пожарить налима", "desc": "Жареный налим со специями: +55 HP в бою подземелья. Срок годности: 4 суток.",
     "result": "Жареный налим", "qty": 1, "exp": "kitchen", "lvl": 1,
     "ingredients": [("Налим", 1), ("Соль", 1)], "ap": 8, "time": 25, "rarity": 1},
    {"name": "Пожарить сома", "desc": "Жареный сом со специями и водорослями: +65 HP в бою подземелья. Срок годности: 4 суток.",
     "result": "Жареный сом", "qty": 1, "exp": "kitchen", "lvl": 1,
     "ingredients": [("Мерцающий сом", 1), ("Соль", 1), ("Кусочек водорослей", 1)], "ap": 9, "time": 30, "rarity": 1},
    {"name": "Пожарить угря", "desc": "Хрустящий жареный угорь с водорослями: +90 HP в бою подземелья. Срок годности: 4 суток.",
     "result": "Жареный угорь", "qty": 1, "exp": "kitchen", "lvl": 2,
     "ingredients": [("Искрящийся угорь", 1), ("Соль", 1), ("Кусочек водорослей", 1)], "ap": 12, "time": 40, "rarity": 2},
    {"name": "Пожарить форель", "desc": "Светящаяся форель, пожаренная до золотой корочки: +140 HP в бою подземелья. Срок годности: 4 суток.",
     "result": "Жареный форель", "qty": 1, "exp": "kitchen", "lvl": 3,
     "ingredients": [("Светящаяся форель", 1), ("Соль", 1), ("Кусочек водорослей", 1)], "ap": 16, "time": 50, "rarity": 4},
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
]


async def ensure_recipes():
    """Идемпотентно засевает рецепты и синхронизирует уже существующие.

    Рецепты обновляются по названию: если строка уже есть — перезаписываем состав
    и описание, иначе добавляем новую. Это нужно, чтобы смена рецептуры
    (например, добавление соли в жареную рыбу) доезжала до существующих БД.
    """
    conn = await get_db()
    changed = False
    for r in RECIPES_DEF:
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
    apple = await get_item_by_name(APPLE_NAME)
    if not apple:
        return False, "Яблоко не настроено в базе. Сообщи хранителю."
    await add_inventory_item(user_id, apple['id'], fruits)
    # Таймер обновляется только при сборе
    data['last_harvest_at'] = time.time()
    data.pop('fruits', None)
    data.pop('next_fruit_at', None)
    await set_housing_slot(user_id, slot_index, "plant_pot", 1, data)
    return True, (apple, fruits)


# ---------- Фонтан (восстановление ОД раз в сутки) ----------

async def can_use_fountain(user_id: int) -> bool:
    user = await get_user(user_id)
    if not user:
        return False
    today = datetime.utcnow().strftime("%Y-%m-%d")
    return not (user.get('fountain_used_day') == today and (user.get('fountain_used_today') or 0) >= 1)


async def mark_fountain_used(user_id: int):
    today = datetime.utcnow().strftime("%Y-%m-%d")
    user = await get_user(user_id)
    used = 1 if user and user.get('fountain_used_day') == today else 1
    await update_user(user_id, fountain_used_day=today, fountain_used_today=used)


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
                      leader_id=None):
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
    if sets:
        vals.append(clan_id)
        await conn.execute(f"UPDATE clans SET {', '.join(sets)} WHERE id = ?", vals)
        await conn.commit()


async def set_clan_leader(clan_id: int, leader_id: int = None):
    conn = await get_db()
    await conn.execute("UPDATE clans SET leader_id = ? WHERE id = ?", (leader_id, clan_id))
    await conn.commit()


async def delete_clan(clan_id: int):
    conn = await get_db()
    await conn.execute("DELETE FROM clan_requests WHERE clan_id = ?", (clan_id,))
    await conn.execute("DELETE FROM clan_members WHERE clan_id = ?", (clan_id,))
    await conn.execute("DELETE FROM clans WHERE id = ?", (clan_id,))
    await conn.commit()


async def add_clan_member(clan_id: int, user_id: int):
    conn = await get_db()
    await conn.execute(
        "INSERT OR IGNORE INTO clan_members (clan_id, user_id) VALUES (?, ?)",
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

RECIPE_ITEM_PRICES = {
    "Пожарить сига": 60,
    "Пожарить муксуна": 60,
    "Пожарить чира": 70,
    "Пожарить налима": 80,
    "Пожарить сома": 90,
    "Пожарить угря": 220,
    "Пожарить форель": 750,
    "Комбинированная наживка": 90,
    "Пара сапог": 320,
    "Малая настойка здоровья": 150,
    "Энергетик": 280,
    "Улучшенная настойка здоровья": 480,
}


async def ensure_recipe_shop_items():
    """Создаёт в магазине предметы-рецепты категории 'recipes'.

    Предмет «Рецепт: <название>» при использовании из инвентаря открывает
    соответствующий рецепт для пилота (таблица user_recipes).
    """
    conn = await get_db()
    changed = False
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
        desc = (f"📜 Обучает рецепту: {r['name']}.\n"
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
    if changed:
        await conn.commit()
    return changed


async def learn_recipe_from_item(user_id: int, item_id: int):
    """Использование предмета-рецепта: открывает рецепт навсегда.

    Возвращает (ok, сообщение). Предмет списывается из инвентаря.
    """
    item = await get_item(item_id)
    if not item or item.get('category') != 'recipes':
        return False, "Это не рецепт."
    inv_row = await get_inventory_item(user_id, item_id)
    if not inv_row or (inv_row.get('quantity') or 0) < 1:
        return False, "У тебя нет этого рецепта в инвентаре."
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
