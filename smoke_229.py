# -*- coding: utf-8 -*-
"""Smoke 229 — кнопка «К списку врагов» не зависит от состояния FSM.

Баг: после загрузки картинки врага состояние очищалось, и список писал
«Подземелье не найдено». Теперь карточка врага несёт id подземелья в кнопке,
а список берёт id из callback_data (состояние — только запасной вариант).

Прогон: .\\.venv\\Scripts\\python.exe smoke_229.py
"""
import asyncio
import os
import sys
from types import SimpleNamespace

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke229.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB

sys.path.insert(0, os.path.dirname(__file__))


class FakeMessage:
    def __init__(self, user_id=1):
        self.from_user = SimpleNamespace(id=user_id, username=f"u{user_id}", full_name="X")
        self.chat = SimpleNamespace(id=user_id)
        self.sent = []

    async def answer(self, *a, **kw):
        self.sent.append((a, kw))

    async def edit_text(self, *a, **kw):
        self.sent.append((a, kw))


class FakeCallback:
    def __init__(self, user_id, data=""):
        self.from_user = SimpleNamespace(id=user_id, username=f"u{user_id}", full_name="X")
        self.message = FakeMessage(user_id)
        self.data = data

    async def answer(self, *a, **kw):
        return True


class FakeState:
    def __init__(self, data=None):
        self._data = dict(data or {})

    async def get_data(self):
        return dict(self._data)

    async def update_data(self, **kw):
        self._data.update(kw)

    async def clear(self):
        self._data.clear()


def _texts(msg):
    out = []
    for a, kw in msg.sent:
        if a:
            out.append(str(a[0]))
        if kw.get("text"):
            out.append(str(kw["text"]))
    return " | ".join(out)


def _back_buttons(msg):
    out = []
    for _a, kw in msg.sent:
        markup = kw.get("reply_markup")
        if markup:
            for row in markup.inline_keyboard:
                out.extend(b.callback_data or "" for b in row)
    return out


async def run():
    from database.db import (init_db, close_db, add_user, get_db, get_dungeon_enemies,
                             get_dungeon, seed_dungeon)
    from bot.handlers import admin as adm

    await init_db()
    await seed_dungeon()
    passed = failed = 0

    def check(name, cond, detail=""):
        nonlocal passed, failed
        if cond:
            passed += 1
            print(f"  OK  {name}")
        else:
            failed += 1
            print(f"  FAIL: {name} {detail}")

    ADMIN = 9992291
    await add_user(ADMIN, "admin229", "Админ", "Тест")
    conn = await get_db()
    await conn.execute("INSERT INTO user_roles (telegram_id, role) VALUES (?, 'super_admin')", (ADMIN,))
    await conn.commit()

    cur = await conn.execute("SELECT id FROM dungeons ORDER BY id")
    dungeon_id = (await cur.fetchone())["id"]
    dng = await get_dungeon(dungeon_id)
    enemy = (await get_dungeon_enemies(dungeon_id))[0]

    print("\n1. Карточка врага: кнопка «К списку» несёт id подземелья")
    cb = FakeCallback(ADMIN)
    await adm._enemy_card_send(cb, enemy["id"])
    back = [c for c in _back_buttons(cb.message) if c.startswith("dungeon:enemies")]
    check("кнопка есть", bool(back))
    check("кнопка несёт id подземелья", back == [f"dungeon:enemies:{enemy['dungeon_id']}"],
          str(back))

    print("\n2. Список открывается по id из кнопки, без состояния FSM")
    st = FakeState()
    cb2 = FakeCallback(ADMIN, data=f"dungeon:enemies:{dungeon_id}")
    await adm.dungeon_enemies_list(cb2, st)
    t2 = _texts(cb2.message)
    check("нет ошибки «Подземелье не найдено»", "не найдено" not in t2, t2[:200])
    check("список показан", dng["name"] in t2, t2[:200])
    check("id подземелья записан в состояние",
          (await st.get_data()).get("target_id") == dungeon_id)

    print("\n3. Путь без id (из меню подземелья) работает по состоянию")
    st2 = FakeState({"target_id": dungeon_id})
    cb3 = FakeCallback(ADMIN, data="dungeon:enemies")
    await adm.dungeon_enemies_list(cb3, st2)
    t3 = _texts(cb3.message)
    check("список открыт из состояния", dng["name"] in t3, t3[:200])

    print("\n4. Без id и без состояния — честная ошибка, а не падение")
    cb4 = FakeCallback(ADMIN, data="dungeon:enemies")
    await adm.dungeon_enemies_list(cb4, FakeState())
    t4 = _texts(cb4.message)
    check("ошибка «не найдено»", "не найдено" in t4, t4[:200])

    await close_db()
    print(f"\nИТОГО: {passed} passed, {failed} failed")
    return failed


if __name__ == "__main__":
    sys.exit(1 if asyncio.run(run()) else 0)
