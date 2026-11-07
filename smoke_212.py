# -*- coding: utf-8 -*-
"""Smoke 212 — иерархия клана: кнопка члена и назначение роли реально обрабатываются.

Регресс v0.43.6/v0.43.7: кнопка члена имела формат clanhier:set:{clan}:{uid},
а колбэк брал clan_id из parts[1] → int('set') падал, пилоты не нажимались.
Здесь вызываем реальный clan_hierarchy_cb с фейковым callback.
"""
import asyncio
import os
import sys

os.environ["DATABASE_PATH"] = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "_test_smoke212.db")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class _Msg:
    photo = None

    def __init__(self):
        self.edits = []

    async def edit_text(self, text, **kw):
        self.edits.append(text)

    async def answer(self, *a, **kw):
        pass


class _User:
    def __init__(self, uid):
        self.id = uid


class _CB:
    def __init__(self, uid, data):
        self.from_user = _User(uid)
        self.data = data
        self.message = _Msg()
        self.alerts = []

    async def answer(self, text=None, show_alert=False, **kw):
        if show_alert:
            self.alerts.append(text)


async def main():
    passed = failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
            print(f"  OK  {name}")
        else:
            failed += 1
            print(f"  FAIL: {name}")

    import database.db as db
    from database.db import (
        init_db, seed_default_items, add_user, create_clan, add_clan_member,
        set_clan_leader, get_clan_member_role, close_db,
    )
    import bot.handlers.clans as clans

    await init_db()
    await seed_default_items()

    LEADER, MEMBER = 212101, 212102
    for uid, nm in ((LEADER, 'L'), (MEMBER, 'M')):
        await add_user(uid, nm.lower(), nm, "")
    cid = await create_clan("clan", "HH", "Иерархия", LEADER)
    await add_clan_member(cid, LEADER)
    await set_clan_leader(cid, LEADER)
    await add_clan_member(cid, MEMBER)

    print("\n1. Экран иерархии у главы")
    cb = _CB(LEADER, f"clanhier:{cid}")
    try:
        await clans.clan_hierarchy_cb(cb)
        check("экран иерархии открывается", bool(cb.message.edits))
    except Exception as e:
        check(f"экран иерархии без исключения ({e!r})", False)

    print("\n2. Нажатие на члена (экран выбора роли)")
    cb = _CB(LEADER, f"clanhier:{cid}:set:{MEMBER}")
    try:
        await clans.clan_hierarchy_cb(cb)
        check("экран выбора роли открывается", bool(cb.message.edits))
        check("на экране имя/текущая роль", any("назначить должность" in t for t in cb.message.edits))
    except Exception as e:
        check(f"нажатие на члена без исключения ({e!r})", False)

    print("\n3. Назначение роли")
    cb = _CB(LEADER, f"clanhier:{cid}:pick:{MEMBER}:elder")
    try:
        await clans.clan_hierarchy_cb(cb)
        check("роль elder записана", await get_clan_member_role(cid, MEMBER) == 'elder')
    except Exception as e:
        check(f"назначение без исключения ({e!r})", False)

    print("\n4. Не-глава не назначает")
    cb = _CB(MEMBER, f"clanhier:{cid}:pick:{MEMBER}:banner")
    try:
        await clans.clan_hierarchy_cb(cb)
        check("не-глава получает отказ", bool(cb.alerts))
        check("роль не изменилась", await get_clan_member_role(cid, MEMBER) == 'elder')
    except Exception as e:
        check(f"отказ без исключения ({e!r})", False)

    await close_db()
    print(f"\nИТОГО: {passed} passed, {failed} failed")
    return failed


if __name__ == "__main__":
    sys.exit(1 if asyncio.run(main()) else 0)
