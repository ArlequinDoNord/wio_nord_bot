# -*- coding: utf-8 -*-
"""Smoke 191 — находки колодца Круговорота в общей таблице water_junk.

1. Колодец засеян проволокой и сеном (шансы из конфига), без озёрного мусора.
2. Миграция fire_well_junk_v1 убирает старые озёрные строки колодца (не правленные админом).
3. Бросок без наживки даёт только находки колодца или ничего.
4. Удалённая админом находка не возвращается, озеро и водохранилище не задеты.
"""
import asyncio
import os
import sys

os.environ["DATABASE_PATH"] = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "_test_smoke191.db")

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
    from database.db import (init_db, close_db, get_db, ensure_water_fish,
                             get_water_junk_rows, get_water_junk_map, remove_water_junk,
                             get_setting)
    from bot.handlers import fishing

    await init_db()
    # Имитация старой БД: колодцу достались озёрные находки (как до миграции)
    conn = await get_db()
    await conn.execute("DELETE FROM settings WHERE key = 'fire_well_junk_v1'")
    await conn.execute("DELETE FROM settings WHERE key = 'water_junk_seeded'")
    await conn.execute("DELETE FROM water_junk")
    await conn.execute(
        "INSERT INTO water_junk (water, name, chance) VALUES "
        "('fire_well', 'Кусочек водорослей', 15), ('fire_well', 'Старый сапог', 2)")
    await conn.commit()

    print("\n1. Миграция колодца")
    await ensure_water_fish()
    wmap = await get_water_junk_map("fire_well")
    check("озёрный мусор в колодце убран", "Кусочек водорослей" not in wmap
          and "Старый сапог" not in wmap)
    check("проволока на колодце", wmap.get(config.FIRE_WIRE_NAME, {}).get("chance") == 4)
    check("сено на колодце", wmap.get(config.FIRE_LAB_HAY_NAME, {}).get("chance") == 8)
    check("миграция отмечена флагом", (await get_setting("fire_well_junk_v1")) == "1")

    print("\n2. Бросок без наживки")
    allowed = {config.FIRE_WIRE_NAME, config.FIRE_LAB_HAY_NAME}
    seen = set()
    for _ in range(300):
        name = await fishing._pick_junk("fire_well")
        seen.add(name)
    check("выпадают только находки колодца или ничего", seen <= allowed | {None})
    check("проволока и сено выпадают", seen >= {config.FIRE_WIRE_NAME, config.FIRE_LAB_HAY_NAME})

    print("\n3. Админ убрал сено: не возвращается, остальное не задето")
    hay = [r for r in await get_water_junk_rows("fire_well") if r['name'] == config.FIRE_LAB_HAY_NAME][0]
    await remove_water_junk(hay['id'])
    await ensure_water_fish()
    check("сено не вернулось", config.FIRE_LAB_HAY_NAME not in
          [r['name'] for r in await get_water_junk_rows("fire_well")])
    check("проволока осталась", config.FIRE_WIRE_NAME in
          [r['name'] for r in await get_water_junk_rows("fire_well")])
    check("озеро не задето", len(await get_water_junk_rows("lake")) == 2)
    check("водохранилище не задето", len(await get_water_junk_rows("reservoir")) == 2)

    print(f"\nИТОГО: {passed} passed, {failed} failed")
    await close_db()
    return failed


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
