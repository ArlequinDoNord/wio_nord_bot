# -*- coding: utf-8 -*-
"""Smoke 201 — огненный гриб на прогалину.

1. Гриб появляется на прогалине с весом 15 и не появляется на опушке.
2. По 5 снимается с трёх самых частых грибов прогалины; сумма весов не меняется.
3. Повторный запуск ничего не меняет (флаг fire_mushroom_pool_v1).
4. Гриб не съедобный (kind = toxic).
"""
import asyncio
import os
import sys

os.environ["DATABASE_PATH"] = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "_test_smoke201.db")
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

    db_file = os.environ["DATABASE_PATH"]
    if os.path.exists(db_file):
        os.remove(db_file)

    import config
    import database.db as db
    from database.db import (init_db, close_db, get_item_by_name, ensure_forest_mushrooms,
                             ensure_forest_zones, ensure_forest_enemies, get_forest_zone_pool)

    from database.db import add_forest_mushroom_to_zone, get_forest_zone_candidates, ensure_forest_items

    await init_db()
    await ensure_forest_items()
    await ensure_forest_mushrooms()
    await ensure_forest_zones()
    weights = [25, 18, 15, 12, 9, 8, 5, 4]
    cands = await get_forest_zone_candidates("clearing")
    for cand, w in zip(cands, weights):
        await add_forest_mushroom_to_zone("clearing", cand["mushroom_id"], w)
    before = {r["name"]: r["chance"] for r in await get_forest_zone_pool("clearing")}
    check("в пуле прогалины 8 грибов с весами", len(before) == 8)
    total_before = sum(before.values())
    top3 = sorted(before, key=lambda n: (-before[n], n))[:3]
    await ensure_forest_enemies()

    fire = await get_item_by_name(config.FIRE_MUSHROOM_NAME)
    print("\n1. Огненный гриб на прогалине")
    check("предмет создан", fire is not None)
    after = {r["name"]: r["chance"] for r in await get_forest_zone_pool("clearing")}
    check("на прогалине вес 15", after.get(fire["name"]) == 15)
    glade = {r["name"] for r in await get_forest_zone_pool("glade")}
    check("на опушке его нет", fire["name"] not in glade)

    print("\n2. Снятие у самых редких по 1")
    rare5 = sorted(before, key=lambda n: (before[n], n))[:5]
    check("у пяти самых редких -1",
          all(after[n] == max(0, before[n] - 1) for n in rare5))
    check("верхние три не тронуты",
          all(after[n] == before[n] for n in before if n not in rare5))
    check("сумма снятого = 5 (остальное — огненному грибу)",
          sum(before[n] - after[n] for n in before) == 5)

    print("\n2а. Пустота на прогалине 0%, на опушке 10%")
    from bot.handlers.forest import pick_forest_mushroom, FOREST_EMPTY_BY_AREA
    rows = [{"chance": v, "name": n} for n, v in after.items()]
    check("прогалина: пустоты нет (r=99.9 → гриб)",
          pick_forest_mushroom(rows, 99.9, empty_chance=FOREST_EMPTY_BY_AREA["clearing"]) is not None)
    check("опушка: пустота 10% (r=5 → пусто)",
          pick_forest_mushroom(rows, 5, empty_chance=10) is None)

    print("\n3. Повторный запуск")
    snapshot = dict(after)
    await ensure_forest_enemies()
    again = {r["name"]: r["chance"] for r in await get_forest_zone_pool("clearing")}
    check("повтор не меняет веса", again == snapshot)

    print("\n4. Тип гриба")
    conn = await db.get_db()
    row = await (await conn.execute(
        "SELECT kind FROM forest_mushrooms WHERE item_id = ?", (fire["id"],))).fetchone()
    check("kind = toxic (не съедобный)", row is not None and row["kind"] == "toxic")

    print(f"\nИТОГО: {passed} passed, {failed} failed")
    await close_db()
    return failed


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
