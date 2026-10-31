# -*- coding: utf-8 -*-
"""Smoke 186 — праздничный сет: уворот 2%/4% и регенерация +1 при 3 одежды + оружие.

Оружие — один слот «weapon», значит оружий из сета максимум одно.
"""
import asyncio
import os
import sys

os.environ["DATABASE_PATH"] = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "_test_smoke186.db")

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

    import config
    import database.db as db
    from database.db import (init_db, close_db, get_db, add_user, update_user,
                             ensure_firelab_items, get_item_by_name,
                             add_inventory_item, set_equipment_slot,
                             get_fire_set_status, get_player_dodge)

    await init_db()
    conn = await get_db()
    for tbl in ("inventory", "users"):
        await conn.execute(f"DELETE FROM {tbl}")
        await conn.commit()
    await ensure_firelab_items()
    UID = 186001
    await add_user(UID, 't', 'Пилот 186', "")
    await update_user(UID, nordmarks=1000)

    async def wear(name, slot):
        item = await get_item_by_name(name)
        if item is None:
            raise RuntimeError(f"нет предмета {name}")
        await add_inventory_item(UID, item['id'], 1)
        await set_equipment_slot(UID, slot, item['id'])

    print("\n1. Два предмета сета → уворот +2%")
    await wear(config.FIRE_CLOAK_NAME, "body")
    await wear(config.FIRE_GLOVES_NAME, "hands")
    st = await get_fire_set_status(UID)
    check("2 одежды: dodge 2, regen 0", st['dodge'] == 2 and st['regen'] == 0)

    print("\n2. Три одежды, без оружия → уворот +2%, регенерации нет")
    await wear(config.FIRE_CROWN_NAME, "head")
    st = await get_fire_set_status(UID)
    check("3 одежды: dodge 2, regen 0", st['dodge'] == 2 and st['regen'] == 0)

    print("\n3. Три одежды и одно оружие → уворот +4%, регенерация +1")
    await wear(config.FIRE_KEYS_NAME, "weapon")
    st = await get_fire_set_status(UID)
    check("3 одежды + оружие: dodge 4, regen 1", st['dodge'] == 4 and st['regen'] == config.FIRE_SET_REGEN_HP)
    base = await get_player_dodge(UID)
    await wear(config.FIRE_CANE_NAME, "weapon")
    st2 = await get_fire_set_status(UID)
    check("замена оружия на трость — сет остаётся", st2['dodge'] == 4 and st2['regen'] == 1)
    check("уворот пилота учитывает +4%", (await get_player_dodge(UID)) >= base)

    print(f"\nИТОГО: {passed} passed, {failed} failed")
    await close_db()
    return failed


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
