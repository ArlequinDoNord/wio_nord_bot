# -*- coding: utf-8 -*-
"""Smoke 233 — назначение и снятие главы клана (роли членов синхронизированы).

Регрессия: «Снять главу» через update_clan(leader_id=None) ничего не меняло
(None пропускается), а назначение нового главы через update_clan не пересчитывало
роль leader у прежнего главы. Теперь оба пути идут через set_clan_leader.

Прогон: .\\.venv\\Scripts\\python.exe smoke_233.py
"""
import asyncio
import os
import sys

_TEST_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_test_smoke233.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

passed = failed = 0


def check(name, cond):
    global passed, failed
    if cond:
        passed += 1
        print(f"  OK  {name}")
    else:
        failed += 1
        print(f"  FAIL: {name}")


async def run():
    from database.db import (init_db, close_db, add_user, create_clan, add_clan_member,
                             set_clan_leader, get_clan, get_clan_member_roles)

    await init_db()
    try:
        for uid in (801, 802, 803):
            await add_user(uid, f"p{uid}", f"P{uid}", "")
        cid = await create_clan("clan", "Test Wolf", "d", 801)
        for uid in (801, 802, 803):
            await add_clan_member(cid, uid)

        print("\n1. Назначить главу, пока старый глава на месте")
        await set_clan_leader(cid, 801)
        await set_clan_leader(cid, 802)
        roles = await get_clan_member_roles(cid)
        check("новый глава: leader_id обновлён", (await get_clan(cid))["leader_id"] == 802)
        check("новый глава: роль leader в составе", roles.get(802) == "leader")
        check("прежний глава: роль снята (member)", roles.get(801) == "member")

        print("\n2. Снять главу")
        await set_clan_leader(cid, None)
        roles = await get_clan_member_roles(cid)
        check("глава снят: leader_id пуст", (await get_clan(cid))["leader_id"] is None)
        check("ни у кого нет роли leader", "leader" not in roles.values())
    finally:
        await close_db()


if __name__ == "__main__":
    asyncio.run(run())
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
