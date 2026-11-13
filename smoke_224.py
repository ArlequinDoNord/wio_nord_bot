# -*- coding: utf-8 -*-
"""Smoke 224 — авто-выкладка товаров «как госпоставка» (раз в неделю).

Правила (решения владельца 2026-11-13):
1. Выкладка доводит конечный остаток до restock_target, если он ниже цели.
   Остаток выше цели не трогаем; безлимит (stock = -1) и выключенные не трогаем.
2. Раз в ISO-неделю (по МСК): повторный суточный цикл и рестарт не дают второй выкладки.
   Если понедельник пропущен, выкладка уходит в первый суточный цикл недели.
3. В карточке хранилища кнопка есть только у конечных товаров из продажи.
4. Включение без цели сначала спрашивает число; число включает выкладку.

Прогон: .\\.venv\\Scripts\\python.exe smoke_224.py
"""
import asyncio
import os
import sys
from datetime import datetime, timedelta
from types import SimpleNamespace

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke224.db")
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

    async def answer_photo(self, *a, **kw):
        self.sent.append((a, kw))

    async def edit_text(self, *a, **kw):
        self.sent.append((a, kw))


class FakeCallback:
    def __init__(self, user_id, data=""):
        self.from_user = SimpleNamespace(id=user_id, username=f"u{user_id}",
                                         full_name=f"User {user_id}")
        self.message = FakeMessage(user_id=user_id)
        self.data = data
        self.answers = []

    async def answer(self, *a, **kw):
        self.answers.append((a, kw))
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


def _kb_texts(msg):
    out = []
    for _a, kw in msg.sent:
        markup = kw.get("reply_markup")
        if markup:
            for row in markup.inline_keyboard:
                out.extend(b.text for b in row)
    return " | ".join(out)


def _kb_callbacks(msg):
    out = []
    for _a, kw in msg.sent:
        markup = kw.get("reply_markup")
        if markup:
            for row in markup.inline_keyboard:
                out.extend(b.callback_data or "" for b in row)
    return out


async def run():
    from database.db import (init_db, close_db, add_item, get_item, update_item,
                             run_weekly_restock, get_setting, get_db)
    from utils.helpers import MOSCOW_TZ
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

    ADMIN = 9992241
    conn = await get_db()
    await conn.execute("INSERT INTO user_roles (telegram_id, role) VALUES (?, 'super_admin')",
                       (ADMIN,))
    await conn.commit()

    # Понедельник 16.11.2026 10:00 МСК; дальше — понедельник 23.11, пропущенный 30.11 и вторник 01.12.
    MON_W = datetime(2026, 11, 16, 10, 0, tzinfo=MOSCOW_TZ)
    MON_W1 = MON_W + timedelta(days=7)
    TUE_W2 = MON_W + timedelta(days=15)

    print("\n1. Миграция: колонки авто-выкладки")
    cols = [r["name"] for r in await (await conn.execute("PRAGMA table_info(items)")).fetchall()]
    check("есть restock_enabled", "restock_enabled" in cols)
    check("есть restock_target", "restock_target" in cols)

    print("\n2. Выкладка доводит конечный остаток до цели")
    a = await add_item(name="__smoke224_a__", description="", price=10, sell_price=5,
                       rarity=1, category="special", stock=3, added_by=0)
    await update_item(a, restock_enabled=1, restock_target=10, is_available=0)
    done = await run_weekly_restock(MON_W)
    row = await get_item(a)
    check("остаток стал 10", row["stock"] == 10)
    check("товар снова в продаже", row["is_available"] == 1)
    check("в ответе есть товар", any(x[0] == "__smoke224_a__" for x in done))

    print("\n3. Один раз за неделю: повтор и рестарт не выкладывают снова")
    await update_item(a, stock=2)
    again = await run_weekly_restock(MON_W + timedelta(hours=3))
    check("повторный вызов на той же неделе ничего не делает", again == [])
    check("остаток не тронут повтором", (await get_item(a))["stock"] == 2)
    check("неделя записана в settings", bool(await get_setting("restock_last_week")))

    print("\n4. Следующая неделя — снова выкладка")
    w1 = await run_weekly_restock(MON_W1)
    check("на следующей неделе выложено", any(x[0] == "__smoke224_a__" for x in w1))
    check("остаток снова 10", (await get_item(a))["stock"] == 10)

    print("\n5. Пропущенный понедельник: выкладка уходит на вторник")
    await update_item(a, stock=1)
    tue = await run_weekly_restock(TUE_W2)
    check("вторник той же недели тоже выкладывает", any(x[0] == "__smoke224_a__" for x in tue))
    check("остаток 10 после вторника", (await get_item(a))["stock"] == 10)

    print("\n6. Что не трогаем")
    b = await add_item(name="__smoke224_above__", description="", price=10, sell_price=5,
                       rarity=1, category="special", stock=25, added_by=0)
    await update_item(b, restock_enabled=1, restock_target=10)
    c = await add_item(name="__smoke224_unlim__", description="", price=10, sell_price=5,
                       rarity=1, category="special", stock=-1, added_by=0)
    await update_item(c, restock_enabled=1, restock_target=10)
    d = await add_item(name="__smoke224_off__", description="", price=10, sell_price=5,
                       rarity=1, category="special", stock=0, added_by=0)
    await update_item(d, restock_enabled=0, restock_target=10)
    await run_weekly_restock(MON_W1 + timedelta(days=14))
    check("выше цели — не трогаем", (await get_item(b))["stock"] == 25)
    check("безлимит не превращаем в конечный", (await get_item(c))["stock"] == -1)
    check("выключенный не выкладываем", (await get_item(d))["stock"] == 0)

    print("\n7. Карточка хранилища: кнопка только у конечных товаров")
    import database.db as dbmod
    async def _no_sources(_item_id):
        return []
    dbmod.get_item_sources = _no_sources
    from bot.handlers import admin as adm
    st = FakeState()
    cb = FakeCallback(ADMIN, f"storage:item:{a}")
    await adm.storage_item(cb, st)
    cbs = _kb_callbacks(cb.message)
    check("у конечного товара есть кнопка авто-выкладки",
          f"storage:auto:{a}" in cbs)
    cb = FakeCallback(ADMIN, f"storage:item:{c}")
    await adm.storage_item(cb, st)
    check("у безлимита кнопки нет", f"storage:auto:{c}" not in _kb_callbacks(cb.message))

    print("\n8. Включение без цели: сначала спрашиваем число")
    e = await add_item(name="__smoke224_new__", description="", price=10,
                       sell_price=5, rarity=1, category="special", stock=4, added_by=0)
    await update_item(e, restock_enabled=0, restock_target=0)
    st = FakeState()
    cb = FakeCallback(ADMIN, f"storage:auto_toggle:{e}")
    await adm.storage_auto_toggle(cb, st)
    check("бот ждёт число", st._state == adm.AdminRestockAuto.target.state)
    check("без цели не включился", not (await get_item(e))["restock_enabled"])

    msg = FakeMessage(text="0", user_id=ADMIN)
    await adm.storage_auto_target_value(msg, st)
    check("0 отклонён", "от 1 до 100000" in _texts(msg))
    check("состояние сохранено после ошибки", st._state == adm.AdminRestockAuto.target.state)

    msg = FakeMessage(text="12", user_id=ADMIN)
    await adm.storage_auto_target_value(msg, st)
    row = await get_item(e)
    check("цель 12 записана", row["restock_target"] == 12)
    check("выкладка включилась", row["restock_enabled"] == 1)
    check("состояние сброшено", st._state is None)

    print("\n9. Выключение и повторное включение")
    cb = FakeCallback(ADMIN, f"storage:auto_toggle:{e}")
    await adm.storage_auto_toggle(cb, FakeState())
    check("выключилась", (await get_item(e))["restock_enabled"] == 0)
    cb = FakeCallback(ADMIN, f"storage:auto_toggle:{e}")
    await adm.storage_auto_toggle(cb, FakeState())
    check("включилась снова", (await get_item(e))["restock_enabled"] == 1)

    print("\n10. Английский интерфейс")
    token = i18n._current.set("en")
    try:
        check("EN: кнопка", i18n.t("restock.btn") == "🔁 Weekly auto-restock")
        check("EN: экран содержит Monday", "Monday" in i18n.t(
            "restock.screen", name="X", state="on", stock=1))
    finally:
        i18n._current.reset(token)

    await close_db()
    print(f"\nИТОГО: {passed} passed, {failed} failed")
    return failed


if __name__ == "__main__":
    sys.exit(1 if asyncio.run(run()) else 0)
