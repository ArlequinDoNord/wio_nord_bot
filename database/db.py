import json
import aiosqlite
from config import DB_PATH

db: aiosqlite.Connection | None = None


async def get_db() -> aiosqlite.Connection:
    global db
    if db is None:
        db = await aiosqlite.connect(DB_PATH, isolation_level=None)
        db.row_factory = aiosqlite.Row
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
            notify_enabled INTEGER DEFAULT 1,
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
            is_active INTEGER DEFAULT 1
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

        CREATE TABLE IF NOT EXISTS locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            description TEXT,
            access_mode TEXT NOT NULL DEFAULT 'all',
            required_status TEXT,
            blocking_states TEXT DEFAULT '[]',
            preview_photo TEXT,
            sort_order INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

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
    """)
    await conn.commit()

    # Миграция: колонки required_status и sort_order (если нет)
    await _ensure_column(conn, "items", "required_status", "TEXT")
    await _ensure_column(conn, "buildings", "required_status", "TEXT")
    await _ensure_column(conn, "statuses", "sort_order", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "users", "promoted_rank", "TEXT")
    await _ensure_column(conn, "users", "notify_enabled", "INTEGER DEFAULT 1")
    await _ensure_column(conn, "users", "equipment", "TEXT DEFAULT '{}'")
    await _ensure_column(conn, "users", "salary", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "users", "salary_period_days", "INTEGER DEFAULT 7")
    await _ensure_column(conn, "users", "last_salary_date", "TIMESTAMP")
    await _ensure_column(conn, "users", "salary_debt", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "items", "armor", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "reports", "total_troops", "INTEGER DEFAULT 0")
    # credited_troops без DEFAULT: у старых отчётов (до миграции) будет NULL
    await _ensure_column(conn, "reports", "credited_troops", "INTEGER")
    # paid=1 — отчёт оплачен суточным начислением; старые одобренные уже оплачены
    await _ensure_column(conn, "reports", "paid", "INTEGER DEFAULT 0")
    await conn.execute("UPDATE reports SET paid = 1 WHERE status = 'approved'")
    await _ensure_column(conn, "player_dungeon_run", "loot_nm", "INTEGER DEFAULT 0")
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
    await _ensure_column(conn, "items", "cure_poison", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "locations", "preview_photo", "TEXT")
    # Опросы: кто и когда закрыл (для архива закрытых голосований)
    await _ensure_column(conn, "polls", "closed_by", "INTEGER")
    await _ensure_column(conn, "polls", "closed_at", "TIMESTAMP")
    # Базовые статусы иерархии: Пилот — гражданин (0), Турист — гость (-10).
    # Старые записи Пилота, которым ранее могли поставить высокий уровень, возвращаем к 0.
    await conn.execute("UPDATE statuses SET sort_order = 0 WHERE access_tag = 'pilot'")
    await conn.execute("UPDATE statuses SET sort_order = -10 WHERE access_tag = 'tourist'")
    await conn.commit()
    await ensure_base_statuses()
    await conn.commit()
    await seed_locations(conn)


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
    ]
    for key, name, desc, mode, req_status, blocking, preview in base:
        await conn.execute(
            "INSERT OR IGNORE INTO locations (key, name, description, access_mode, required_status, blocking_states, preview_photo) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (key, name, desc, mode, req_status, json.dumps(blocking, ensure_ascii=False), preview)
        )
    await conn.commit()


async def _ensure_column(conn, table: str, column: str, coltype: str):
    """Добавляет колонку в таблицу, если её ещё нет."""
    cursor = await conn.execute(f"PRAGMA table_info({table})")
    cols = [row['name'] for row in await cursor.fetchall()]
    if column not in cols:
        await conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {coltype}")
    await conn.commit()


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


async def get_user(user_id: int):
    """Возвращает игрока словарём с учётом протухших состояний.

    При активном состоянии «истощён» ap_max заменяется на лимит истощения (90).
    """
    from config import AP_EXHAUSTED_MAX_AP
    conn = await get_db()
    cursor = await conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = await cursor.fetchone()
    if not row:
        return None
    user = dict(row)
    state = user.get('state') or 'нормально'
    refreshed = await drop_expired_state(user_id, state, user.get('state_effects') or "{}")
    if refreshed != state:
        user['state'] = refreshed
    if refreshed == 'истощён':
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


async def add_ap(user_id: int, amount: int):
    """Добавить ОД. При состоянии «истощён» потолок — AP_EXHAUSTED_MAX_AP (90)."""
    from config import AP_EXHAUSTED_MAX_AP
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT state, state_effects, ap_max FROM users WHERE user_id = ?", (user_id,)
    )
    row = await cursor.fetchone()
    if not row:
        return
    state = await drop_expired_state(user_id, row['state'], row['state_effects'])
    cap = AP_EXHAUSTED_MAX_AP if state == 'истощён' else row['ap_max']
    await conn.execute(
        "UPDATE users SET ap = MIN(?, ap + ?) WHERE user_id = ?",
        (cap, amount, user_id)
    )
    await conn.commit()


async def remove_ap(user_id: int, amount: int) -> bool:
    conn = await get_db()
    cursor = await conn.execute("SELECT ap FROM users WHERE user_id = ?", (user_id,))
    row = await cursor.fetchone()
    if not row or row['ap'] < amount:
        return False
    await conn.execute("UPDATE users SET ap = ap - ? WHERE user_id = ?", (amount, user_id))
    await conn.commit()
    return True


async def daily_ap_recovery():
    """Суточное восстановление ОД.

    В состоянии «истощён»: +75 ОД, потолок 90. Счётчик восстановления через
    расходники (ap_restored_today) обнуляется только при смене суток.
    """
    from config import (AP_DAILY_RECOVERY, AP_EXHAUSTED_DAILY_RECOVERY, AP_EXHAUSTED_MAX_AP)
    conn = await get_db()
    await conn.execute("""
        UPDATE users SET
            ap = MIN(CASE WHEN state = 'истощён' THEN ? ELSE ap_max END,
                     ap + CASE WHEN state = 'истощён' THEN ? ELSE ? END),
            ap_restored_today = CASE WHEN ap_restored_day = date('now') THEN ap_restored_today ELSE 0 END,
            ap_restored_day = CASE WHEN ap_restored_day = date('now') THEN ap_restored_day ELSE date('now') END
    """, (AP_EXHAUSTED_MAX_AP, AP_EXHAUSTED_DAILY_RECOVERY, AP_DAILY_RECOVERY))
    await conn.commit()


async def add_item(name: str, description: str, price: int, sell_price: int,
                   rarity: int, category: str, stock: int, added_by: int,
                   photo_file_id: str = None, ap_cost: int = 0,
                   production_time_hours: int = 0, produced_by: int = None,
                   damage: int = 0, heal: int = 0, armor: int = 0):
    conn = await get_db()
    cursor = await conn.execute(
        """INSERT INTO items (name, description, photo_file_id, price, sell_price,
           rarity, category, stock, added_by, ap_cost, production_time_hours, produced_by, damage, heal, armor)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (name, description, photo_file_id, price, sell_price, rarity, category,
         stock, added_by, ap_cost, production_time_hours, produced_by, damage, heal, armor)
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


async def update_item(item_id: int, **kwargs):
    conn = await get_db()
    sets = ", ".join(f"{k} = ?" for k in kwargs)
    values = list(kwargs.values()) + [item_id]
    await conn.execute(f"UPDATE items SET {sets} WHERE id = ?", values)
    await conn.commit()


async def delete_item(item_id: int):
    conn = await get_db()
    await conn.execute("DELETE FROM items WHERE id = ?", (item_id,))
    await conn.commit()


async def add_inventory_item(user_id: int, item_id: int, quantity: int = 1):
    conn = await get_db()
    await conn.execute("""
        INSERT INTO inventory (user_id, item_id, quantity)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id, item_id) DO UPDATE SET quantity = quantity + ?
    """, (user_id, item_id, quantity, quantity))
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


async def process_item_use(user_id: int, item_id: int) -> tuple:
    item = await get_item(item_id)
    if not item:
        return False, "Предмет не найден"

    inv_item = await get_inventory_item(user_id, item_id)
    if not inv_item or inv_item['quantity'] < 1:
        return False, "У тебя нет этого предмета"

    if item['category'] == 'consumable':
        if item['heal'] > 0:
            return False, "Это зелье можно применить только в бою подземелья 💊"

        if item['ap_cost'] > 0:
            from config import (AP_BONUS_FROM_CONSUMABLE, AP_DAILY_RESTORE_LIMIT,
                                AP_EXHAUSTED_MINUTES, AP_EXHAUSTED_DAILY_RECOVERY, AP_EXHAUSTED_MAX_AP)
            user = await get_user(user_id)
            if not user:
                return False, "Пользователь не найден"

            if user.get('state') == 'истощён':
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

            amount = min(AP_BONUS_FROM_CONSUMABLE, remaining)
            await remove_inventory_item(user_id, item_id, 1)
            await add_ap(user_id, amount)
            restored_today += amount
            conn = await get_db()
            await conn.execute(
                "UPDATE users SET ap_restored_today = ?, ap_restored_day = ? WHERE user_id = ?",
                (restored_today, today, user_id)
            )
            await conn.commit()

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
            return True, (
                f"Ты использовал {item['name']} и получил +{amount} AP! "
                f"Осталось восстановить ОД сегодня: {AP_DAILY_RESTORE_LIMIT - restored_today}."
            )

        await remove_inventory_item(user_id, item_id, 1)
        return True, f"Ты использовал {item['name']}!"

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
    """Установить состояние игрока. Метаданные (срок действия и причина) — в state_effects JSON."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    effects = {"applied_at": now, "minutes": minutes, "caused_by": caused_by, "reason": reason}
    if meta:
        effects.update(meta)
    conn = await get_db()
    cursor = await conn.execute("SELECT state FROM users WHERE user_id = ?", (user_id,))
    row = await cursor.fetchone()
    old_state = row['state'] if row else "нормально"

    await conn.execute(
        "UPDATE users SET state = ?, state_effects = ? WHERE user_id = ?",
        (state_text, json.dumps(effects, ensure_ascii=False), user_id)
    )
    await conn.execute(
        "INSERT INTO state_log (user_id, old_state, new_state, reason, caused_by) VALUES (?, ?, ?, ?, ?)",
        (user_id, old_state, state_text, reason or "изменение состояния", caused_by)
    )
    await conn.commit()


async def clear_user_state(user_id: int, caused_by: int = None, reason: str = "состояние снято"):
    """Снять состояние: вернуть игрока в «нормально»."""
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


async def drop_expired_state(user_id: int, state_text: str, state_effects: str) -> str:
    """Если срок состояния истёк — снять его. Возвращает актуальный state_text.

    state_effects — JSON вида {"applied_at": "2026-09-06 12:00:00", "minutes": 60, ...}.
    """
    if state_text == "нормально" or not state_effects:
        return state_text
    try:
        effects = json.loads(state_effects)
    except (ValueError, TypeError):
        return state_text
    applied = datetime.strptime(effects['applied_at'], "%Y-%m-%d %H:%M:%S")
    minutes = int(effects.get('minutes', 0))
    if applied + timedelta(minutes=minutes) <= datetime.now():
        await clear_user_state(user_id, effects.get('caused_by'), f"срок действия истёк ({state_text})")
        return "нормально"
    return state_text


async def count_reports_today(user_id: int) -> int:
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT COUNT(*) AS cnt FROM reports WHERE user_id = ? AND date(created_at) = date('now')",
        (user_id,)
    )
    row = await cursor.fetchone()
    return row['cnt'] if row else 0


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
            "SELECT troops, nordmarks FROM users WHERE user_id = ?", (uid,)
        )
        u = await cur.fetchone()
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
    """Игроки, чьи войска соответствуют званию выше Лейтенанта,
    но звание ещё не присвоено через админку."""
    from config import RANKS
    lieutenant_troops = 1500
    result = []
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT user_id, first_name, username, troops, promoted_rank FROM users WHERE troops >= ?",
        (lieutenant_troops,)
    )
    for row in await cursor.fetchall():
        if row['promoted_rank']:
            continue
        next_rank = None
        for rank_name, required in RANKS:
            if rank_name in ("Рекрут", "Рядовой", "Капрал", "Сержант", "Лейтенант"):
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


async def promote_user_rank(user_id: int, rank_name: str, promoted_by: int):
    conn = await get_db()
    await conn.execute(
        "UPDATE users SET promoted_rank = ? WHERE user_id = ?",
        (rank_name, user_id)
    )
    await conn.commit()
    await log_action(promoted_by, 'promote_rank', user_id, f"rank={rank_name}")


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
    cursor = await conn.execute("SELECT user_id, username, first_name, last_name FROM users")
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

    Пилот (гражданин) — 0, Турист (гость) — -10, Ветеран — 5, VIP — 10.
    """
    base = [
        ("Турист", "tourist", "Гость Нордхайма. Права ограничены.", -10),
        ("Пилот", "pilot", "Гражданин Нордхайма. Базовый статус пилота.", 0),
        ("Ветеран", "veteran", "Ветеран боевых действий.", 5),
        ("VIP", "vip", "Особо важная персона.", 10),
    ]
    conn = await get_db()
    for name, tag, desc, level in base:
        cursor = await conn.execute("SELECT id FROM statuses WHERE access_tag = ?", (tag,))
        if await cursor.fetchone():
            continue
        await create_status(name, tag, desc, sort_order=level)
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
    blocking = json.loads(loc['blocking_states'] or '[]')
    if blocking:
        from utils.states import get_state_info
        info = await get_state_info(user_id)
        if info['name'] in blocking:
            return False
    return True


async def location_access_label(mode: str, req_status: str) -> str:
    if mode == "all" or not mode:
        return "🌐 Всем"
    if mode == "exact":
        return f"🎯 Только: {req_status}"
    return f"📈 {req_status} и выше"


# ============ СИД: ТЕСТОВЫЕ ТОВАРЫ ============

DEFAULT_ITEMS = [
    # (name, description, price, sell_price, rarity, category, stock, ap_cost, damage, heal)
    ("Учебный истребитель", "Базовая учебная машина для новичков.", 250, 125, 2, "weapon", 5, 0, 8, 0),
    ("Стандартный пулемёт", "Надёжное вооружение для воздушных боёв.", 150, 75, 1, "weapon", 10, 0, 5, 0),
    ("Энергетик", "Восстанавливает силы: даёт +AP при использовании.", 50, 25, 1, "consumable", 20, 50, 0, 0),
    ("Топливо", "Запас топлива для вылетов. +AP при использовании.", 40, 20, 1, "consumable", 20, 30, 0, 0),
    ("Ремкомплект", "Мелкий ремонт техники.", 80, 40, 2, "consumable", 15, 40, 0, 0),
    ("Лётный шлем", "Защищает пилота в бою.", 120, 60, 2, "equipment", 10, 0, 3, 0, 4),
    ("Кислородная маска", "Для высотных полётов.", 90, 45, 1, "equipment", 10, 0, 2, 0, 2),
    ("Ангар-бокс", "Личное хранилище для техники.", 500, 250, 3, "building", 3, 0, 0, 0),
    ("Металл", "Сырьё для производства.", 30, 15, 1, "resource", 50, 0, 0, 0),
    ("Кристаллы", "Редкое сырьё, используется в производстве.", 200, 100, 4, "resource", 10, 0, 0, 0),
    ("Медаль «Крыло»", "Особая награда за заслуги.", 1000, 500, 5, "special", 1, 0, 0, 0),
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
    return True


# ============ ДАНЖ: ТЕСТОВЫЙ ДАНЖ ============

DEFAULT_DUNGEON = {
    "name": "Крысиный Подвал",
    "description": "Тёмный подвал под штабом. Крысы мутировали и захватили его.",
    "floors": [
        {
            "enemies": [
                ("Крыса", 15, 3, 0, False, [{"item": "Хвост крысы", "chance": 0.15, "qty": 1}], "assets/img/enemies/rat.jpg", 0, 0),
                ("Ядовитая крыса", 20, 5, 0, False, [{"item": "Хвост крысы", "chance": 0.25, "qty": 1}], "assets/img/enemies/poison_rat.jpg", 35, 5),
                ("Кристальный паук", 18, 4, 0, False, [
                    {"item": "Паутина паука", "chance": 0.15, "qty": 1},
                    {"item": "Осколок кристалла", "chance": 0.05, "qty": 1},
                ], "assets/img/enemies/crystal_spider.jpg", 0, 0),
            ],
            "boss": ("Король крыс", 50, 8, 15, True, [
                {"item": "Хвост крысы", "chance": 0.4, "qty": 2},
                {"item": "Осколок кристалла", "chance": 0.2, "qty": 1},
            ], "assets/img/enemies/rat_king.jpg", 0, 0),
        },
    ],
}


async def seed_dungeon():
    conn = await get_db()
    cursor = await conn.execute("SELECT COUNT(*) as c FROM dungeons")
    row = await cursor.fetchone()
    if row['c'] > 0:
        return False

    cur = await conn.execute(
        "INSERT INTO dungeons (name, description, floors_count, rooms_per_floor) VALUES (?, ?, ?, ?)",
        (DEFAULT_DUNGEON["name"], DEFAULT_DUNGEON["description"],
         len(DEFAULT_DUNGEON["floors"]), 10)
    )
    dungeon_id = cur.lastrowid

    for floor_idx, floor_data in enumerate(DEFAULT_DUNGEON["floors"], 1):
        for enemy in floor_data["enemies"]:
            (name, hp, atk, reward, is_boss, drops) = enemy[:6]
            image = enemy[6] if len(enemy) > 6 else None
            poison_chance = enemy[7] if len(enemy) > 7 else 0
            poison_dmg = enemy[8] if len(enemy) > 8 else 0
            await conn.execute(
                "INSERT INTO dungeon_enemies (dungeon_id, floor, name, hp, attack, reward_nm, is_boss, drops, image, poison_chance, poison_dmg) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (dungeon_id, floor_idx, name, hp, atk, reward, int(is_boss),
                 json.dumps(drops, ensure_ascii=False), image, poison_chance, poison_dmg)
            )
        boss = floor_data["boss"]
        boss_drops = boss[5] if len(boss) > 5 else []
        boss_image = boss[6] if len(boss) > 6 else None
        boss_poison_chance = boss[7] if len(boss) > 7 else 0
        boss_poison_dmg = boss[8] if len(boss) > 8 else 0
        await conn.execute(
            "INSERT INTO dungeon_enemies (dungeon_id, floor, name, hp, attack, reward_nm, is_boss, drops, image, poison_chance, poison_dmg) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (dungeon_id, floor_idx, boss[0], boss[1], boss[2], boss[3], int(boss[4]),
             json.dumps(boss_drops, ensure_ascii=False), boss_image, boss_poison_chance, boss_poison_dmg)
        )

    await conn.commit()
    return True


async def get_all_dungeons():
    conn = await get_db()
    cursor = await conn.execute("SELECT * FROM dungeons WHERE is_active = 1")
    return await cursor.fetchall()


async def get_dungeon(dungeon_id: int):
    conn = await get_db()
    cursor = await conn.execute("SELECT * FROM dungeons WHERE id = ?", (dungeon_id,))
    return await cursor.fetchone()


async def get_floor_enemies(dungeon_id: int, floor: int):
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT * FROM dungeon_enemies WHERE dungeon_id = ? AND floor = ?",
        (dungeon_id, floor)
    )
    return await cursor.fetchall()


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

    await conn.execute(
        "INSERT INTO player_dungeon_run (user_id, dungeon_id, floor, room_number, hp, hp_max, is_active) VALUES (?,?,?,?,?,?,?)",
        (user_id, dungeon_id, 1, 0, 100, 100, 1)
    )
    await conn.commit()


async def get_active_run(user_id: int):
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT * FROM player_dungeon_run WHERE user_id = ? AND is_active = 1",
        (user_id,)
    )
    return await cursor.fetchone()


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


async def get_player_armor(user_id: int) -> int:
    """Защита активного снаряжения игрока (слот 'armor' в equipment)."""
    eq = await get_equipment(user_id)
    armor_id = eq.get('armor')
    if not armor_id:
        return 0
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT armor FROM items WHERE id = ?",
        (armor_id,)
    )
    row = await cursor.fetchone()
    return row['armor'] if row else 0


async def get_equipment(user_id: int) -> dict:
    """Возвращает активное снаряжение игрока: {"weapon": id, "armor": id}."""
    conn = await get_db()
    cursor = await conn.execute("SELECT equipment FROM users WHERE user_id = ?", (user_id,))
    row = await cursor.fetchone()
    if not row or not row['equipment']:
        return {}
    try:
        eq = json.loads(row['equipment'])
        if not isinstance(eq, dict):
            return {}
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


async def get_equipment_slot_items(user_id: int):
    """Предметы, выставленные в активные слоты зелий (potion1/potion2), с наличием в инвентаре."""
    eq = await get_equipment(user_id)
    slots = [('potion1', eq.get('potion1')), ('potion2', eq.get('potion2'))]
    result = []
    for slot, item_id in slots:
        if not item_id:
            continue
        conn = await get_db()
        cursor = await conn.execute("""
            SELECT i.id, i.name, i.heal, i.cure_poison, COALESCE(inv.quantity, 0) as quantity
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


async def ensure_dungeon_enemy_drops():
    """Синхронизирует врагов существующего данжа с DEFAULT_DUNGEON (дропы, HP, награды)."""
    conn = await get_db()

    dungeons = await get_all_dungeons()
    if not dungeons:
        return
    dungeon_id = dungeons[0]['id']

    expected = set()
    for floor_idx, floor_data in enumerate(DEFAULT_DUNGEON["floors"], 1):
        for enemy in floor_data["enemies"]:
            (name, hp, atk, reward, is_boss, drops) = enemy[:6]
            image = enemy[6] if len(enemy) > 6 else None
            poison_chance = enemy[7] if len(enemy) > 7 else 0
            poison_dmg = enemy[8] if len(enemy) > 8 else 0
            expected.add(name)
            drops_json = json.dumps(drops, ensure_ascii=False)
            cursor = await conn.execute(
                "SELECT COUNT(*) as c FROM dungeon_enemies WHERE dungeon_id = ? AND name = ? AND is_boss = 0",
                (dungeon_id, name)
            )
            if (await cursor.fetchone())['c'] == 0:
                await conn.execute(
                    "INSERT INTO dungeon_enemies (dungeon_id, floor, name, hp, attack, reward_nm, is_boss, drops, image, poison_chance, poison_dmg) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                    (dungeon_id, floor_idx, name, hp, atk, reward, 0, drops_json, image, poison_chance, poison_dmg)
                )
            else:
                await conn.execute(
                    "UPDATE dungeon_enemies SET hp = ?, attack = ?, reward_nm = ?, drops = ?, image = ?, poison_chance = ?, poison_dmg = ? "
                    "WHERE dungeon_id = ? AND name = ? AND is_boss = 0",
                    (hp, atk, reward, drops_json, image, poison_chance, poison_dmg, dungeon_id, name)
                )

        boss = floor_data["boss"]
        expected.add(boss[0])
        boss_drops_json = json.dumps(boss[5] if len(boss) > 5 else [], ensure_ascii=False)
        boss_image = boss[6] if len(boss) > 6 else None
        boss_poison_chance = boss[7] if len(boss) > 7 else 0
        boss_poison_dmg = boss[8] if len(boss) > 8 else 0
        cursor = await conn.execute(
            "SELECT COUNT(*) as c FROM dungeon_enemies WHERE dungeon_id = ? AND name = ? AND is_boss = 1",
            (dungeon_id, boss[0])
        )
        if (await cursor.fetchone())['c'] == 0:
            await conn.execute(
                "INSERT INTO dungeon_enemies (dungeon_id, floor, name, hp, attack, reward_nm, is_boss, drops, image, poison_chance, poison_dmg) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (dungeon_id, floor_idx, boss[0], boss[1], boss[2], boss[3], 1, boss_drops_json, boss_image, boss_poison_chance, boss_poison_dmg)
            )
        else:
            await conn.execute(
                "UPDATE dungeon_enemies SET hp = ?, attack = ?, reward_nm = ?, drops = ?, image = ?, poison_chance = ?, poison_dmg = ? "
                "WHERE dungeon_id = ? AND name = ? AND is_boss = 1",
                (boss[1], boss[2], boss[3], boss_drops_json, boss_image, boss_poison_chance, boss_poison_dmg, dungeon_id, boss[0])
            )

    # Удаляем врагов, которых больше нет в конфиге (старый состав)
    cursor = await conn.execute(
        "SELECT id, name FROM dungeon_enemies WHERE dungeon_id = ? AND name NOT IN (%s)"
        % ",".join("?" * len(expected)), (dungeon_id, *expected)
    )
    to_delete = await cursor.fetchall()
    for row in to_delete:
        await conn.execute("DELETE FROM dungeon_enemies WHERE id = ?", (row['id'],))

    # этажей в данже = 1
    await conn.execute("UPDATE dungeons SET floors_count = ? WHERE id = ?", (len(DEFAULT_DUNGEON["floors"]), dungeon_id))
    await conn.commit()


# ============ ЛОГ АКТИВНОСТИ ИГРОКОВ ============

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
        "SELECT id, user_id, action, details, created_at FROM activity_log "
        "ORDER BY id DESC LIMIT ?",
        (limit,)
    )
    return await cursor.fetchall()


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
