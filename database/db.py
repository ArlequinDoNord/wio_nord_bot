import json
import aiosqlite
from config import DB_PATH

db: aiosqlite.Connection | None = None


async def get_db() -> aiosqlite.Connection:
    global db
    if db is None:
        db = await aiosqlite.connect(DB_PATH)
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
            nordmarks INTEGER DEFAULT 100,
            ap INTEGER DEFAULT 100,
            ap_max INTEGER DEFAULT 150,
            state TEXT DEFAULT 'нормально',
            state_effects TEXT DEFAULT '{}',
            promoted_rank TEXT,
            status_text TEXT DEFAULT 'Боевой пилот',
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
    """)
    await conn.commit()

    # Миграция: колонки required_status и sort_order (если нет)
    await _ensure_column(conn, "items", "required_status", "TEXT")
    await _ensure_column(conn, "buildings", "required_status", "TEXT")
    await _ensure_column(conn, "statuses", "sort_order", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "users", "promoted_rank", "TEXT")
    await _ensure_column(conn, "reports", "total_troops", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "items", "damage", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "items", "heal", "INTEGER DEFAULT 0")
    await _ensure_column(conn, "dungeon_enemies", "drops", "TEXT DEFAULT '[]'")
    await _ensure_column(conn, "dungeon_enemies", "image", "TEXT")
    # Базовый статус «Пилот» всегда на самом низком уровне иерархии.
    # (Раньше старый миграционный апдейт мог выставить ему высокий уровень.)
    await conn.execute("UPDATE statuses SET sort_order = 0 WHERE access_tag = 'pilot'")
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
        INSERT OR IGNORE INTO users (user_id, username, first_name, last_name)
        VALUES (?, ?, ?, ?)
    """, (user_id, username, first_name, last_name))
    await conn.commit()


async def get_user(user_id: int):
    conn = await get_db()
    cursor = await conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    return await cursor.fetchone()


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
    conn = await get_db()
    await conn.execute("""
        UPDATE users SET ap = MIN(ap_max, ap + ?) WHERE user_id = ?
    """, (amount, user_id))
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
    conn = await get_db()
    await conn.execute("""
        UPDATE users SET ap = MIN(ap_max, ap + 100)
    """)
    await conn.commit()


async def add_item(name: str, description: str, price: int, sell_price: int,
                   rarity: int, category: str, stock: int, added_by: int,
                   photo_file_id: str = None, ap_cost: int = 0,
                   production_time_hours: int = 0, produced_by: int = None,
                   damage: int = 0, heal: int = 0):
    conn = await get_db()
    cursor = await conn.execute(
        """INSERT INTO items (name, description, photo_file_id, price, sell_price,
           rarity, category, stock, added_by, ap_cost, production_time_hours, produced_by, damage, heal)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (name, description, photo_file_id, price, sell_price, rarity, category,
         stock, added_by, ap_cost, production_time_hours, produced_by, damage, heal)
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

        await remove_inventory_item(user_id, item_id, 1)

        if item['ap_cost'] > 0:
            from config import AP_BONUS_FROM_CONSUMABLE
            await add_ap(user_id, AP_BONUS_FROM_CONSUMABLE)
            return True, f"Ты использовал {item['name']} и получил +{AP_BONUS_FROM_CONSUMABLE} AP!"

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
    return cursor.lastrowid


async def update_trade(trade_id: int, status: str):
    conn = await get_db()
    await conn.execute("UPDATE trades SET status = ? WHERE id = ?", (status, trade_id))
    await conn.commit()


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


async def get_poll(poll_id: int):
    conn = await get_db()
    cursor = await conn.execute("SELECT * FROM polls WHERE id = ?", (poll_id,))
    return await cursor.fetchone()


async def get_active_polls():
    conn = await get_db()
    cursor = await conn.execute("SELECT * FROM polls WHERE is_active = 1")
    return await cursor.fetchall()


async def close_poll(poll_id: int):
    conn = await get_db()
    await conn.execute("UPDATE polls SET is_active = 0 WHERE id = ?", (poll_id,))
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


async def set_state(user_id: int, new_state: str, reason: str, caused_by: int = None):
    conn = await get_db()
    cursor = await conn.execute("SELECT state FROM users WHERE user_id = ?", (user_id,))
    row = await cursor.fetchone()
    old_state = row['state'] if row else "нормально"

    await conn.execute("UPDATE users SET state = ? WHERE user_id = ?", (new_state, user_id))
    await conn.execute(
        "INSERT INTO state_log (user_id, old_state, new_state, reason, caused_by) VALUES (?, ?, ?, ?, ?)",
        (user_id, old_state, new_state, reason, caused_by)
    )
    await conn.commit()


async def add_report(user_id: int, screenshot_file_id: str, troops_reported: int, total_troops: int = 0, region: str = ""):
    conn = await get_db()
    cursor = await conn.execute(
        "INSERT INTO reports (user_id, screenshot_file_id, troops_reported, total_troops, region) VALUES (?, ?, ?, ?, ?)",
        (user_id, screenshot_file_id, troops_reported, total_troops, region)
    )
    await conn.commit()
    return cursor.lastrowid


async def approve_report(report_id: int, reviewed_by: int, troops: int):
    conn = await get_db()
    cursor = await conn.execute("SELECT user_id FROM reports WHERE id = ?", (report_id,))
    row = await cursor.fetchone()
    if not row:
        return False

    user_id = row['user_id']
    nordmarks_earned = troops

    await conn.execute(
        "UPDATE reports SET status = 'approved', reviewed_by = ?, troops_reported = ?, nordmarks_earned = ? WHERE id = ?",
        (reviewed_by, troops, nordmarks_earned, report_id)
    )
    await conn.execute("UPDATE users SET troops = troops + ? WHERE user_id = ?", (troops, user_id))
    await conn.execute("UPDATE users SET nordmarks = nordmarks + ? WHERE user_id = ?", (nordmarks_earned, user_id))
    await conn.execute(
        "INSERT INTO transactions (to_user, amount, tx_type, description) VALUES (?, ?, ?, ?)",
        (user_id, nordmarks_earned, "report", f"Начисление за отчёт #{report_id}")
    )
    await conn.commit()
    return True


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

    troops_24h        — сумма troops_reported по одобренным отчётам за последние 24 часа
    active_pilots_72h — число уникальных пилотов с одобренными отчётами за последние 72 часа
    """
    conn = await get_db()
    await conn.execute("DELETE FROM region_stats")
    cursor = await conn.execute("""
        SELECT region,
               COALESCE(SUM(troops_reported), 0) AS troops_24h,
               COUNT(DISTINCT user_id) AS active_pilots_72h
        FROM reports
        WHERE status = 'approved'
          AND created_at >= datetime('now', '-72 hours')
        GROUP BY region
        HAVING region IS NOT NULL AND region != ''
    """)
    rows = await cursor.fetchall()
    for row in rows:
        troops_72h_reporters = row['active_pilots_72h']
        # Отдельно считаем войска за 24 часа
        cur2 = await conn.execute("""
            SELECT COALESCE(SUM(troops_reported), 0) AS t
            FROM reports
            WHERE status = 'approved' AND region = ?
              AND created_at >= datetime('now', '-24 hours')
        """, (row['region'],))
        troops_24h = (await cur2.fetchone())['t']
        await conn.execute(
            "INSERT INTO region_stats (region, troops_24h, active_pilots_72h, computed_at) VALUES (?, ?, ?, datetime('now'))",
            (row['region'], troops_24h, troops_72h_reporters)
        )
    await conn.commit()
    return len(rows)


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


async def ensure_base_status(user_id: int):
    """Базовый статус «Пилот»: создаёт при отсутствии и выдаёт игроку по умолчанию."""
    conn = await get_db()
    cursor = await conn.execute("SELECT id FROM statuses WHERE access_tag = 'pilot'")
    row = await cursor.fetchone()
    if row:
        status_id = row['id']
    else:
        created, status_id = await create_status("Пилот", "pilot", "Базовый статус нового пилота",
                                                 sort_order=0)
        if not created:
            cursor = await conn.execute("SELECT id FROM statuses WHERE access_tag = 'pilot'")
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


# ============ СИД: ТЕСТОВЫЕ ТОВАРЫ ============

DEFAULT_ITEMS = [
    # (name, description, price, sell_price, rarity, category, stock, ap_cost, damage, heal)
    ("Учебный истребитель", "Базовая учебная машина для новичков.", 250, 125, 2, "weapon", 5, 0, 8, 0),
    ("Стандартный пулемёт", "Надёжное вооружение для воздушных боёв.", 150, 75, 1, "weapon", 10, 0, 5, 0),
    ("Аптечка", "Восстанавливает силы. Использование даёт +AP.", 50, 25, 1, "consumable", 20, 50, 0, 0),
    ("Топливо", "Запас топлива для вылетов. +AP при использовании.", 40, 20, 1, "consumable", 20, 30, 0, 0),
    ("Ремкомплект", "Мелкий ремонт техники.", 80, 40, 2, "consumable", 15, 40, 0, 0),
    ("Лётный шлем", "Защищает пилота в бою.", 120, 60, 2, "equipment", 10, 0, 3, 0),
    ("Кислородная маска", "Для высотных полётов.", 90, 45, 1, "equipment", 10, 0, 2, 0),
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

    for (name, desc, price, sell_price, rarity, category, stock, ap_cost, damage, heal) in DEFAULT_ITEMS:
        await add_item(
            name=name, description=desc, price=price, sell_price=sell_price,
            rarity=rarity, category=category, stock=stock, added_by=0, ap_cost=ap_cost,
            damage=damage, heal=heal,
        )
    return True


# ============ ДАНЖ: ТЕСТОВЫЙ ДАНЖ ============

DEFAULT_DUNGEON = {
    "name": "Крысиный Подвал",
    "description": "Тёмный подвал под штабом. Крысы мутировали и захватили его.",
    "floors": [
        {
            "enemies": [
                ("Крыса", 15, 3, 0, False, [{"item": "Хвост крысы", "chance": 0.2, "qty": 1}], "assets/img/enemies/rat.jpg"),
                ("Ядовитая крыса", 20, 5, 0, False, [{"item": "Хвост крысы", "chance": 0.35, "qty": 1}], "assets/img/enemies/poison_rat.jpg"),
                ("Кристальный паук", 18, 4, 0, False, [
                    {"item": "Паутина паука", "chance": 0.2, "qty": 1},
                    {"item": "Осколок кристалла", "chance": 0.05, "qty": 1},
                ], "assets/img/enemies/crystal_spider.jpg"),
            ],
            "boss": ("Король крыс", 50, 8, 15, True, [
                {"item": "Хвост крысы", "chance": 0.5, "qty": 2},
                {"item": "Осколок кристалла", "chance": 0.2, "qty": 1},
            ], "assets/img/enemies/rat_king.jpg"),
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
            await conn.execute(
                "INSERT INTO dungeon_enemies (dungeon_id, floor, name, hp, attack, reward_nm, is_boss, drops, image) VALUES (?,?,?,?,?,?,?,?,?)",
                (dungeon_id, floor_idx, name, hp, atk, reward, int(is_boss),
                 json.dumps(drops, ensure_ascii=False), image)
            )
        boss = floor_data["boss"]
        boss_drops = boss[5] if len(boss) > 5 else []
        boss_image = boss[6] if len(boss) > 6 else None
        await conn.execute(
            "INSERT INTO dungeon_enemies (dungeon_id, floor, name, hp, attack, reward_nm, is_boss, drops, image) VALUES (?,?,?,?,?,?,?,?,?)",
            (dungeon_id, floor_idx, boss[0], boss[1], boss[2], boss[3], int(boss[4]),
             json.dumps(boss_drops, ensure_ascii=False), boss_image)
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
    await conn.commit()


async def get_player_weapon_damage(user_id: int) -> int:
    """Суммарный урон оружия в инвентаре игрока."""
    conn = await get_db()
    cursor = await conn.execute("""
        SELECT COALESCE(SUM(i.damage * inv.quantity), 0) as total_damage
        FROM inventory inv
        JOIN items i ON inv.item_id = i.id
        WHERE inv.user_id = ? AND i.category = 'weapon'
    """, (user_id,))
    row = await cursor.fetchone()
    return row['total_damage'] if row else 0


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
        SELECT i.id, i.name, i.heal, inv.quantity
        FROM inventory inv JOIN items i ON inv.item_id = i.id
        WHERE inv.user_id = ? AND i.category = 'consumable' AND i.heal > 0 AND inv.quantity > 0
        ORDER BY i.heal DESC
    """, (user_id,))
    return await cursor.fetchall()


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

    cursor = await conn.execute("SELECT COUNT(*) as c FROM items WHERE name = ?", ("Хвост крысы",))
    if (await cursor.fetchone())['c'] == 0:
        await add_item(
            name="Хвост крысы",
            description="Трофей с крыс подземелья. Используется для производства настоек.",
            price=10, sell_price=5, rarity=2, category="resource",
            stock=-1, added_by=0, ap_cost=0, damage=0, heal=0,
        )
        added = True

    for (tname, tdesc) in (("Паутина паука", "Редкий трофей с пауков подземелья. Используется в производстве."),
                           ("Осколок кристалла", "Очень редкий трофей с кристальных пауков. Нужен для крафта.")):
        cursor = await conn.execute("SELECT COUNT(*) as c FROM items WHERE name = ?", (tname,))
        if (await cursor.fetchone())['c'] == 0:
            await add_item(
                name=tname, description=tdesc, price=15, sell_price=7, rarity=3,
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
            expected.add(name)
            drops_json = json.dumps(drops, ensure_ascii=False)
            cursor = await conn.execute(
                "SELECT COUNT(*) as c FROM dungeon_enemies WHERE dungeon_id = ? AND name = ? AND is_boss = 0",
                (dungeon_id, name)
            )
            if (await cursor.fetchone())['c'] == 0:
                await conn.execute(
                    "INSERT INTO dungeon_enemies (dungeon_id, floor, name, hp, attack, reward_nm, is_boss, drops, image) VALUES (?,?,?,?,?,?,?,?,?)",
                    (dungeon_id, floor_idx, name, hp, atk, reward, 0, drops_json, image)
                )
            else:
                await conn.execute(
                    "UPDATE dungeon_enemies SET hp = ?, attack = ?, reward_nm = ?, drops = ?, image = ? "
                    "WHERE dungeon_id = ? AND name = ? AND is_boss = 0",
                    (hp, atk, reward, drops_json, image, dungeon_id, name)
                )

        boss = floor_data["boss"]
        expected.add(boss[0])
        boss_drops_json = json.dumps(boss[5] if len(boss) > 5 else [], ensure_ascii=False)
        boss_image = boss[6] if len(boss) > 6 else None
        cursor = await conn.execute(
            "SELECT COUNT(*) as c FROM dungeon_enemies WHERE dungeon_id = ? AND name = ? AND is_boss = 1",
            (dungeon_id, boss[0])
        )
        if (await cursor.fetchone())['c'] == 0:
            await conn.execute(
                "INSERT INTO dungeon_enemies (dungeon_id, floor, name, hp, attack, reward_nm, is_boss, drops, image) VALUES (?,?,?,?,?,?,?,?,?)",
                (dungeon_id, floor_idx, boss[0], boss[1], boss[2], boss[3], 1, boss_drops_json, boss_image)
            )
        else:
            await conn.execute(
                "UPDATE dungeon_enemies SET hp = ?, attack = ?, reward_nm = ?, drops = ?, image = ? "
                "WHERE dungeon_id = ? AND name = ? AND is_boss = 1",
                (boss[1], boss[2], boss[3], boss_drops_json, boss_image, dungeon_id, boss[0])
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
