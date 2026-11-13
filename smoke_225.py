# -*- coding: utf-8 -*-
"""Smoke 225 — лимит на руках на аккаунт (купленное в магазине).

Правила (решения владельца 2026-11-13):
1. inventory.shop_qty — сколько из quantity куплено в магазине. Добытое, скрафченное,
   полученное с рынка и из наград в счёт лимита не входит.
2. Расход сначала идёт за добытым: триггер подтягивает shop_qty к остатку, когда
   количество падает ниже числа купленных. Пилот не выбирает, какую штуку тратит, поэтому
   порядок задан игрой.
3. items.shop_limit (0 = без лимита): покупка в магазине блокируется, если
   shop_qty + покупаемое > лимит.
4. В инвентаре строка «×4 · 🛠2 / 🛒2 · лим. 2/2».

Прогон: .\\.venv\\Scripts\\python.exe smoke_225.py
"""
import asyncio
import os
import sys
from types import SimpleNamespace

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke225.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB

sys.path.insert(0, os.path.dirname(__file__))


class FakeMessage:
    def __init__(self, text="", user_id=1):
        self.text = text
        self.photo = None
        self.from_user = SimpleNamespace(id=user_id, username=f"u{user_id}",
                                         full_name=f"User {user_id}")
        self.chat = SimpleNamespace(id=user_id)
        self.sent = []

    async def answer(self, *a, **kw):
        self.sent.append((a, kw))

    async def edit_text(self, *a, **kw):
        self.sent.append((a, kw))


class FakeCallback:
    def __init__(self, user_id, data=""):
        self.from_user = SimpleNamespace(id=user_id, username=f"u{user_id}",
                                         full_name=f"User {user_id}")
        self.message = FakeMessage(user_id=user_id)
        self.data = data

    async def answer(self, *a, **kw):
        return True


class FakeState:
    def __init__(self):
        self._state = None
        self._data = {}

    async def get_state(self):
        return self._state

    async def set_state(self, s):
        self._state = s

    async def get_data(self):
        return dict(self._data)

    async def update_data(self, **kw):
        self._data.update({k: v for k, v in kw.items() if v is not None})

    async def clear(self):
        self._data.clear()
        self._state = None


def _texts(msg):
    return " ".join(str(a[0]) for a in msg.sent if a)


async def run():
    from database.db import (init_db, close_db, add_user, add_item, update_item,
                             add_inventory_item, remove_inventory_item, get_inventory_item,
                             shop_limit_status, get_item, get_db)
    from bot.handlers.inventory import inv_stock_label
    from bot.handlers import admin as adm
    from utils import i18n

    await init_db()
    passed = failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
            print(f"  OK  {name}")
        else:
            failed += 1
            print(f"  FAIL: {name}")

    ADMIN = 9992251
    PILOT = 9992252
    await add_user(ADMIN, "inspector225", "Инспектор", "МВД")
    await add_user(PILOT, "pilot225", "Пилот", "Тестов")
    conn = await get_db()
    await conn.execute("INSERT INTO user_roles (telegram_id, role) VALUES (?, 'super_admin')",
                       (ADMIN,))
    await conn.commit()

    salt = await add_item(name="__smoke225_salt__", description="", price=5, sell_price=2,
                          rarity=1, category="consumable", stock=-1, added_by=0)
    await update_item(salt, shop_limit=2)

    async def qty_shop():
        row = await get_inventory_item(PILOT, salt)
        return (row["quantity"], row["shop_qty"]) if row else (0, 0)

    print("\n1. Схема: колонки и триггер")
    cols = [r["name"] for r in await (await conn.execute("PRAGMA table_info(inventory)")).fetchall()]
    check("в inventory есть shop_qty", "shop_qty" in cols)
    icols = [r["name"] for r in await (await conn.execute("PRAGMA table_info(items)")).fetchall()]
    check("в items есть shop_limit", "shop_limit" in icols)
    trg = await (await conn.execute(
        "SELECT name FROM sqlite_master WHERE type='trigger' AND name='trg_inventory_shop_clamp'")
    ).fetchone()
    check("триггер установлен", trg is not None)

    print("\n2. Добытые 2 + купленные 2 (лимит 2)")
    await add_inventory_item(PILOT, salt, 2)
    await add_inventory_item(PILOT, salt, 2, from_shop=True)
    check("всего 4, куплено 2", await qty_shop() == (4, 2))
    check("докупить нельзя (2 из 2)", await shop_limit_status(PILOT, salt) == (2, 2))

    print("\n3. Потратили добытую — купленные на месте")
    await remove_inventory_item(PILOT, salt, 1)
    check("всего 3, куплено 2", await qty_shop() == (3, 2))
    check("докупить по-прежнему нельзя", (await shop_limit_status(PILOT, salt))[0] == 2)
    await remove_inventory_item(PILOT, salt, 1)
    check("всего 2, куплено 2 (добытые кончились)", await qty_shop() == (2, 2))

    print("\n4. Потратили купленную — лимит освободился")
    await remove_inventory_item(PILOT, salt, 1)
    check("всего 1, куплено 1", await qty_shop() == (1, 1))
    held, lim = await shop_limit_status(PILOT, salt)
    check("можно докупить 1", lim - held == 1)

    print("\n5. Докупили 1")
    await add_inventory_item(PILOT, salt, 1, from_shop=True)
    check("всего 2, куплено 2", await qty_shop() == (2, 2))

    print("\n6. Рынок и добыча не считаются покупкой в магазине")
    await add_inventory_item(PILOT, salt, 3)
    check("после добычи 3: всего 5, куплено 2", await qty_shop() == (5, 2))
    check("лимит не сработал на добытом", (await shop_limit_status(PILOT, salt))[0] == 2)

    print("\n7. Прямой SQL-расход тоже срабатывает (триггер, а не обход через функцию)")
    await conn.execute("UPDATE inventory SET quantity = 1 WHERE user_id = ? AND item_id = ?",
                       (PILOT, salt))
    await conn.commit()
    check("количество 1 — куплено подтянулось до 1", await qty_shop() == (1, 1))

    print("\n8. Без лимита (0) покупка не ограничена")
    await update_item(salt, shop_limit=0)
    check("лимит 0 — статус без ограничения", (await shop_limit_status(PILOT, salt))[1] == 0)
    await update_item(salt, shop_limit=2)

    print("\n9. Строка в инвентаре")
    check("×4 · 🛠2 / 🛒2 · лим. 2/2", inv_stock_label(4, 2, 2) == "×4 · 🛠2 / 🛒2 · лим. 2/2")
    check("без купленных и лимита — просто ×4", inv_stock_label(4, 0, 0) == "×4")
    check("лимит без покупок: ×3 · 🛠3 / 🛒0 · лим. 0/2",
          inv_stock_label(3, 0, 2) == "×3 · 🛠3 / 🛒0 · лим. 0/2")
    check("купленных больше остатка не показываем",
          inv_stock_label(1, 5, 2) == "×1 · 🛠0 / 🛒1 · лим. 1/2")

    print("\n10. Админка: задать лимит")
    st = FakeState()
    cb = FakeCallback(ADMIN, f"storage:shoplim:{salt}")
    await adm.storage_shop_limit_ask(cb, st)
    check("бот ждёт число", st._state == adm.AdminShopLimit.value.state)
    msg = FakeMessage(text="1001", user_id=ADMIN)
    await adm.storage_shop_limit_value(msg, st)
    check("1001 отклонено", "от 0 до 1000" in _texts(msg))
    msg = FakeMessage(text="abc", user_id=ADMIN)
    await adm.storage_shop_limit_value(msg, st)
    check("нечисловой ввод отклонён", "от 0 до 1000" in _texts(msg))
    msg = FakeMessage(text="5", user_id=ADMIN)
    await adm.storage_shop_limit_value(msg, st)
    check("лимит 5 сохранён", (await get_item(salt))["shop_limit"] == 5)
    check("состояние сброшено", st._state is None)

    print("\n11. Английский интерфейс")
    token = i18n._current.set("en")
    try:
        text = i18n.t("shop.limit_reached", held=2, limit=2)
        check("EN: отказ по лимиту", "Hand limit reached" in text)
    finally:
        i18n._current.reset(token)

    await close_db()
    print(f"\nИТОГО: {passed} passed, {failed} failed")
    return failed


if __name__ == "__main__":
    sys.exit(1 if asyncio.run(run()) else 0)
