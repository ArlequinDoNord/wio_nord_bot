# -*- coding: utf-8 -*-
"""Smoke 220 — админ-редактор наград: переименование.

1. Обычная награда переименовывается; имя уникально, длина ≤ 60, пустое — отказ.
2. Уровни достижений и системные значки (ВУСП, «Опытный турист») переименовать нельзя.
3. В карточке редактора у обычной награды есть кнопка «Название», у системной — нет.
4. Ввод нового названия в редакторе: успех — состояние сброшено; отказ — состояние сохранено.
"""
import asyncio
import os
import sys
from types import SimpleNamespace

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke220.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB

sys.path.insert(0, os.path.dirname(__file__))


class FakeMessage:
    def __init__(self, text=""):
        self.text = text
        self.photo = None
        self.from_user = SimpleNamespace(id=1)
        self.sent = []
        self.edits = []

    async def answer(self, *a, **kw):
        self.sent.append((a, kw))

    async def edit_text(self, *a, **kw):
        self.edits.append((a, kw))


class FakeState:
    def __init__(self, data=None):
        self._state = "edit"
        self._data = dict(data or {})

    async def get_data(self):
        return dict(self._data)

    async def update_data(self, **kw):
        self._data.update(kw)

    async def set_state(self, s):
        self._state = s

    async def clear(self):
        self._data.clear()
        self._state = None


async def run():
    from database.db import (init_db, close_db, create_award, get_award, get_all_awards,
                             rename_award, ensure_achievements, ensure_kvp_award,
                             ensure_tourist_booklet, get_db)
    import config
    from bot.handlers import admin as adm

    await init_db()
    await ensure_achievements()
    await ensure_kvp_award()
    await ensure_tourist_booklet()

    passed = failed = 0

    async def _perm(_u, _p):
        return True

    adm.has_permission = _perm

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
            print(f"  OK  {name}")
        else:
            failed += 1
            print(f"  FAIL: {name}")

    ok, aid = await create_award("Старое имя", "тест", "🎖️", 1)
    check("обычная награда создана", ok)

    print("\n1. Переименование обычной награды")
    ok, reason = await rename_award(aid, "Новое имя")
    check("переименована", ok and (await get_award(aid))["name"] == "Новое имя")
    ok, reason = await rename_award(aid, "  ")
    check("пустое название — отказ", not ok and reason)
    ok, reason = await rename_award(aid, "я" * 61)
    check("длиннее 60 — отказ", not ok and "60" in reason)
    ok2, aid2 = await create_award("Занятое", "тест", "🏅", 1)
    ok, reason = await rename_award(aid, "Занятое")
    check("дубль имени — отказ", not ok and "уже существует" in reason)

    print("\n2. Системные награды нельзя переименовать")
    conn = await get_db()
    ach = await (await conn.execute(
        "SELECT id FROM awards WHERE achievement_key IS NOT NULL LIMIT 1")).fetchone()
    ok, reason = await rename_award(ach["id"], "Своё")
    check("уровень достижения — отказ", not ok and "достижения" in reason)
    kvp = await (await conn.execute("SELECT id FROM awards WHERE name = ?",
                                    ("Значок В.У.С.П.",))).fetchone()
    ok, reason = await rename_award(kvp["id"], "Своё")
    check("значок ВУСП — отказ", not ok and "Системную" in reason)
    tour = await (await conn.execute("SELECT id FROM awards WHERE name = ?",
                                     (config.TOURIST_BOOKLET_AWARD,))).fetchone()
    ok, reason = await rename_award(tour["id"], "Своё")
    check("«Опытный турист» — отказ", not ok and "Системную" in reason)

    print("\n3. Кнопка «Название» в карточке")
    def cbs_of(msg):
        out = []
        for _a, kw in msg.edits or msg.sent:
            m = kw.get("reply_markup")
            if m:
                out += [b.callback_data for row in m.inline_keyboard for b in row]
        return out

    msg = FakeMessage()
    await adm._award_edit_menu(msg, await get_award(aid))
    check("у обычной награды есть «Название»", f"aw_ei:{aid}:name" in cbs_of(msg))
    msg2 = FakeMessage()
    await adm._award_edit_menu(msg2, await get_award(tour["id"]))
    check("у «Опытного туриста» кнопки «Название» нет",
          f"aw_ei:{tour['id']}:name" not in cbs_of(msg2))

    print("\n4. Ввод в редакторе")
    st = FakeState({"edit_award_id": aid, "edit_field": "name"})
    await adm.award_edit_value(FakeMessage(text="Финальное имя"), st)
    check("успех: название изменено",
          (await get_award(aid))["name"] == "Финальное имя")
    check("успех: состояние сброшено", st._state is None)

    st2 = FakeState({"edit_award_id": aid, "edit_field": "name"})
    await adm.award_edit_value(FakeMessage(text="Занятое"), st2)
    check("отказ: состояние сохранено (можно повторить)", st2._state == "edit")
    check("отказ: название не менялось", (await get_award(aid))["name"] == "Финальное имя")

    await close_db()
    print(f"\nИТОГО: {passed} passed, {failed} failed")
    return failed


if __name__ == "__main__":
    sys.exit(1 if asyncio.run(run()) else 0)
