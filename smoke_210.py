# -*- coding: utf-8 -*-
"""Smoke 210 — Древо клана: 5 Ламп у членов, здание строится — и Древо ставится.

1. Пятеро членов с Лампой, здание клана ещё не построено: установка отказывает
   (нужно здание), Древо не ставится.
2. Здание построено: с пятью Лампами установка проходит.
3. С четырьмя Лампами установка не проходит (порог 5).
"""
import asyncio
import sys

from tests_support import Checker, use_test_db

_TEST_DB = use_test_db(__file__, "smoke210")


async def main():
    check = Checker()

    import config
    import database.db as db
    from database.db import (init_db, close_db, add_user, get_db, get_item_by_name,
                             ensure_firelab_items, create_clan, add_clan_member,
                             set_clan_leader, ensure_clan_building, install_clan_expansion,
                             add_inventory_item, count_clan_lanterns)

    await init_db()
    await db.ensure_achievements()
    await ensure_firelab_items()
    lamp = await get_item_by_name(config.FIRE_LANTERN_NAME)

    UID = 210001
    members = [210101 + i for i in range(5)]
    await add_user(UID, "chief", "Глава", "")
    for m in members:
        await add_user(m, f"m{m}", f"Член {m}", "")

    clan_id = await create_clan("clan", "Древесники", "проверка", UID)
    await add_clan_member(clan_id, UID)
    await set_clan_leader(clan_id, UID)
    for m in members:
        await add_clan_member(clan_id, m)
    await ensure_clan_building(clan_id)

    print("\n1. Пятеро с Лампой, здание не построено")
    for m in members:
        await add_inventory_item(m, lamp["id"], 1)
    check("в клане 5 Ламп", await count_clan_lanterns(clan_id) == 5)
    ok, msg = await install_clan_expansion(clan_id, UID, 1, "tree")
    check("без здания Древо не ставится", not ok)
    check("сообщение говорит про здание", "здани" in msg.lower())

    print("\n2. Здание построено — Древо ставится")
    conn = await get_db()
    await conn.execute(
        "UPDATE clan_buildings SET status = 'built', building_type = 'house' WHERE clan_id = ?",
        (clan_id,))
    await conn.commit()
    ok, msg = await install_clan_expansion(clan_id, UID, 1, "tree")
    check(f"с пятью Лампами установка прошла ({msg[:40]})", ok)
    exp = await (await conn.execute(
        "SELECT expansion_type FROM clan_expansions WHERE clan_id = ? AND slot_index = 1",
        (clan_id,))).fetchone()
    check("в слоте 1 Древо", exp is not None and exp["expansion_type"] == "tree")

    print("\n3. Порог 5: четыре Лампы не хватает")
    clan2 = await create_clan("clan", "Четвёрка", "проверка", UID + 1)
    await add_user(UID + 1, "chief2", "Глава2", "")
    await add_clan_member(clan2, UID + 1)
    await set_clan_leader(clan2, UID + 1)
    four = [210201 + i for i in range(4)]
    for m in four:
        await add_user(m, f"f{m}", f"Ч {m}", "")
        await add_clan_member(clan2, m)
        await add_inventory_item(m, lamp["id"], 1)
    await ensure_clan_building(clan2)
    await conn.execute(
        "UPDATE clan_buildings SET status = 'built', building_type = 'house' WHERE clan_id = ?",
        (clan2,))
    await conn.commit()
    ok2, msg2 = await install_clan_expansion(clan2, UID + 1, 1, "tree")
    check("с четырьмя Лампами Древо не ставится", not ok2)

    failed = check.summary()
    await close_db()
    return failed


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
