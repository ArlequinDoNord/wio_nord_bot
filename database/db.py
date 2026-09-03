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
    """)
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
                   production_time_hours: int = 0, produced_by: int = None):
    conn = await get_db()
    cursor = await conn.execute(
        """INSERT INTO items (name, description, photo_file_id, price, sell_price,
           rarity, category, stock, added_by, ap_cost, production_time_hours, produced_by)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (name, description, photo_file_id, price, sell_price, rarity, category,
         stock, added_by, ap_cost, production_time_hours, produced_by)
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


async def add_report(user_id: int, screenshot_file_id: str, troops_reported: int, region: str = ""):
    conn = await get_db()
    cursor = await conn.execute(
        "INSERT INTO reports (user_id, screenshot_file_id, troops_reported, region) VALUES (?, ?, ?, ?)",
        (user_id, screenshot_file_id, troops_reported, region)
    )
    await conn.commit()
    return cursor.lastrowid


async def approve_report(report_id: int, reviewed_by: int, nordmarks_earned: int):
    conn = await get_db()
    cursor = await conn.execute("SELECT user_id FROM reports WHERE id = ?", (report_id,))
    row = await cursor.fetchone()
    if not row:
        return False

    user_id = row['user_id']
    await conn.execute(
        "UPDATE reports SET status = 'approved', reviewed_by = ?, nordmarks_earned = ? WHERE id = ?",
        (reviewed_by, nordmarks_earned, report_id)
    )
    await conn.execute("UPDATE users SET troops = troops + ? WHERE user_id = ?", (nordmarks_earned, user_id))
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


# ============ СИД: ТЕСТОВЫЕ ТОВАРЫ ============

DEFAULT_ITEMS = [
    # (name, description, price, sell_price, rarity, category, stock, ap_cost)
    ("Учебный истребитель", "Базовая учебная машина для новичков.", 250, 125, 2, "weapon", 5, 0),
    ("Стандартный пулемёт", "Надёжное вооружение для воздушных боёв.", 150, 75, 1, "weapon", 10, 0),
    ("Аптечка", "Восстанавливает силы. Использование даёт +AP.", 50, 25, 1, "consumable", 20, 50),
    ("Топливо", "Запас топлива для вылетов. +AP при использовании.", 40, 20, 1, "consumable", 20, 30),
    ("Ремкомплект", "Мелкий ремонт техники.", 80, 40, 2, "consumable", 15, 40),
    ("Лётный шлем", "Защищает пилота в бою.", 120, 60, 2, "equipment", 10, 0),
    ("Кислородная маска", "Для высотных полётов.", 90, 45, 1, "equipment", 10, 0),
    ("Ангар-бокс", "Личное хранилище для техники.", 500, 250, 3, "building", 3, 0),
    ("Металл", "Сырьё для производства.", 30, 15, 1, "resource", 50, 0),
    ("Кристаллы", "Редкое сырьё, используется в производстве.", 200, 100, 4, "resource", 10, 0),
    ("Медаль «Крыло»", "Особая награда за заслуги.", 1000, 500, 5, "special", 1, 0),
]


async def seed_default_items():
    """Заполняет магазин базовым набором товаров, если он пуст и не было своих товаров."""
    conn = await get_db()
    cursor = await conn.execute("SELECT COUNT(*) as c FROM items")
    row = await cursor.fetchone()
    if row['c'] > 0:
        return False

    for (name, desc, price, sell_price, rarity, category, stock, ap_cost) in DEFAULT_ITEMS:
        await add_item(
            name=name, description=desc, price=price, sell_price=sell_price,
            rarity=rarity, category=category, stock=stock, added_by=0, ap_cost=ap_cost,
        )
    return True
