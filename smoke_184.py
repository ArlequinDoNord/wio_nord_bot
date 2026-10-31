# -*- coding: utf-8 -*-
"""Smoke 184 — клан: назначение должностей главой и роспуск клана главой-одиночкой.

1. Глава назначает участника (clanhier:…:pick:…): роль сохраняется, на колбэк ровно один ответ.
2. Глава с другими участниками не может выйти/распустить клан.
3. Глава-одиночка распускает клан: клан удаляется, пилот свободен.
"""
import asyncio
import os
import sys

os.environ["DATABASE_PATH"] = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "_test_smoke184.db")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def main():
    passed = failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
            print(f"  OK  {name}")
        else:
            failed += 1
            print(f"  FAIL {name}")

    from database.db import (init_db, close_db, get_db, add_user, create_clan,
                             add_clan_member, set_clan_leader, get_clan,
                             get_clan_member_role, get_user_clan)
    from bot.handlers import clans as cl

    await init_db()
    conn = await get_db()
    for tbl in ("clan_members", "clan_requests", "clans", "users"):
        await conn.execute(f"DELETE FROM {tbl}")
        await conn.commit()
    LEADER, A, B, C = 184001, 184002, 184003, 184004
    for uid in (LEADER, A, B, C):
        await add_user(uid, f"u{uid}", f"Пилот {uid}", "")

    class FakeMsg:
        photo = None
        chat = type("C", (), {"id": LEADER})()
        message_id = 1
        async def answer(self, text=None, **kw):
            return True
        async def edit_text(self, text=None, **kw):
            return True
        async def edit_caption(self, **kw):
            return True
        async def edit_media(self, **kw):
            return True
        async def delete(self):
            return True

    class FakeCB:
        def __init__(self, uid, data):
            self.from_user = type("U", (), {"id": uid})()
            self.data = data
            self.message = FakeMsg()
            self.answers = []
        async def answer(self, text=None, show_alert=False, **kw):
            self.answers.append(text)
            return True

    print("\n1. Глава назначает должность участнику")
    cid = await create_clan("clan", "TT", "Тест", LEADER)
    await add_clan_member(cid, LEADER)
    await set_clan_leader(cid, LEADER)
    await add_clan_member(cid, A)
    await add_clan_member(cid, B)
    cb = FakeCB(LEADER, f"clanhier:{cid}:pick:{A}:seneschal")
    await cl.clan_hierarchy_cb(cb)
    check("участник A стал сенешалем", await get_clan_member_role(cid, A) == "seneschal")
    check("на колбэк ровно один ответ", len(cb.answers) == 1)

    print("\n2. Глава с другими участниками клан не распускает")
    cb2 = FakeCB(LEADER, f"clans:leave:{cid}")
    await cl.clan_leave_cb(cb2)
    check("клан не удалён, пока есть участники", (await get_clan(cid)) is not None)

    print("\n3. Глава-одиночка распускает клан")
    solo = await create_clan("clan", "SO", "Соло", C)
    await add_clan_member(solo, C)
    await set_clan_leader(solo, C)
    await cl.clan_leave_cb(FakeCB(C, f"clans:leave:{solo}"))
    check("клан удалён", (await get_clan(solo)) is None)
    check("пилот свободен", (await get_user_clan(C, 'clan')) is None)

    print(f"\nИТОГО: {passed} passed, {failed} failed")
    await close_db()
    return failed


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
