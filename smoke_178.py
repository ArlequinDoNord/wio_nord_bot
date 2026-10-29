# -*- coding: utf-8 -*-
"""Smoke 178 — клановое Древо Пламенного Круговорота (расширение 'tree').

1. Конфиг: 'tree' в CLAN_EXPANSION_TYPES; предмет «Эссенция Памяти» сидится
   (22-й), sell 500.
2. Гейт: без Ламп у чланов установка Древа запрещена («7 Ламп»).
3. 7 чланов с Лампами в инвентаре → установка разрешена, таймер Эссии
   стартует (~30 суток).
4. 🧘 Медитация у Древа: первый чл. +20 ОД, повтор — 0, другой чл. — +20
   (личные отметки, в дополнение к домашней медитации лампы).
5. 🌿 Эссенция: таймер в прошлом → collect ok; глава (can_manage) собирает
   в инвентарь; альтернативно — на склад клана (qty на складском экране).
6. Upgrade Древа запрещён; роспуск клана чистит clan_tree_medit.
"""
import asyncio
import os
import sys
import time

os.environ["DATABASE_PATH"] = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "_test_smoke178.db")

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

    import database.db as db
    import config
    from database.db import (
        init_db, close_db, add_user, update_user, get_db,
        ensure_firelab_items, get_item_by_name, add_inventory_item,
        create_clan, add_clan_member, get_clan, get_clan_building,
        ensure_clan_building, set_clan_leader,
        install_clan_expansion, get_clan_expansion, get_clan_expansions,
        upgrade_clan_expansion, delete_clan,
        count_clan_lanterns, can_meditate_clan_tree, use_clan_tree_meditation,
        set_clan_tree_essence_next, get_clan_tree_essence_at,
        collect_clan_tree_essence, add_clan_storage, get_clan_storage,
        get_clan_storage_qty, add_ap, get_user, get_inventory_item,
    )
    await init_db()
    conn = await db.get_db()
    await conn.execute("PRAGMA foreign_keys=OFF")
    for tbl in ("inventory", "user_fire_fish", "user_awards", "awards",
                "user_achievements", "user_recipes", "recipes",
                "activity_log", "housing_slots", "player_housing",
                "fire_lab_sessions", "fire_lab_entries", "ap_log",
                "clan_tree_medit", "clan_expansions", "clan_garden",
                "clan_recipes", "clan_storage", "clan_shop_items",
                "clan_shop_purchases", "clan_members", "clan_requests",
                "clan_buildings", "clans", "items"):
        try:
            await conn.execute(f"DELETE FROM {tbl}")
            await conn.commit()
        except Exception:
            pass
    await conn.execute("PRAGMA foreign_keys=ON")

    # дом нужен для ведтох зданий
    base_items = await db.seed_dungeon() if hasattr(db, 'seed_dungeon') else True

    await db.ensure_achievements()
    items = await ensure_firelab_items()
    UID = 178001
    LIDS = [178101 + i for i in range(7)]   # 7 членов с Лампами
    await add_user(UID, 'l', 'Глава', "")
    for lid2 in LIDS:
        await add_user(lid2, f'l{lid2}', f'Член {lid2}', "")

    print("\n1. Конфиг и предметы")
    check("'tree' в CLAN_EXPANSION_TYPES",
          "tree" in getattr(config, "CLAN_EXPANSION_TYPES", ()))
    essence = await get_item_by_name(config.FIRE_TREE_CLAN_ESSENCE_NAME)
    check("«Эссенция Памяти» в сиде предметов", essence is not None)
    check("продажа Эссии 500 НМ",
          essence and int(essence['sell_price'] or 0) == 500)
    lamp = await get_item_by_name(config.FIRE_LANTERN_NAME)
    check("Лампа уже в сиде (Ф4б)", lamp is not None)

    print("\n2. Клан и гейт установки Древа")
    clan_id = await create_clan("clan", "Огнеросы", "проверка", UID)
    await add_clan_member(clan_id, UID)
    await set_clan_leader(clan_id, UID)
    building = await ensure_clan_building(clan_id)
    # ТЗ: установка расширений только в built — сразу «построено» для теста
    conn = await db.get_db()
    await conn.execute(
        "UPDATE clan_buildings SET status='built', building_type='house' "
        "WHERE clan_id = ?", (clan_id,))
    await conn.commit()
    # статус построено
    ok, msg = await install_clan_expansion(clan_id, UID, 1, "tree")
    check(f"без Ламп Древо не ставится ({msg[:40]}…)", not ok)
    check("в отказе говора про Лампы", "Ламп" in msg)
    lamps_now = await count_clan_lanterns(clan_id)
    check("в клане 0 Ламп", lamps_now == 0)

    print("\n3. 7 Ламп у членов → установка разрешена")
    for lid2 in LIDS:
        await add_clan_member(clan_id, lid2)
        await add_inventory_item(lid2, lamp['id'], 1)
    lamps_now = await count_clan_lanterns(clan_id)
    check("в клане 7 Ламп (все чланы)", lamps_now == 7)
    ok, msg = await install_clan_expansion(clan_id, UID, 1, "tree")
    check(f"установка прошла ({msg[:30]}…)", ok)
    exp = await get_clan_expansion(clan_id, 1)
    check("расширение type='tree' в слоте 1",
          exp and exp['expansion_type'] == 'tree')
    ess_ts = await get_clan_tree_essence_at(clan_id)
    days_left = (float(ess_ts) - time.time()) / 86400
    check(f"таймер Эссии ~30 суток ({days_left:.1f})",
          28 < days_left < 31)

    print("\n4. Медитация у Древа (каждому члену раз в сутки)")
    gained1 = await use_clan_tree_meditation(clan_id, UID)
    check("глава медитировал: +20 ОД", gained1 == 20)
    user = await get_user(UID)
    check("ОД реально вырос (база 100 → 120)", int(user['ap'] or 0) >= 120)
    check("повтор в тот же день — 0",
          await use_clan_tree_meditation(clan_id, UID) == 0)
    gained2 = await use_clan_tree_meditation(clan_id, LIDS[0])
    check("другой член тоже может медитировать: +20", gained2 == 20)
    check("у главы отметка в отдельной таблице (не слитая)",
          await can_meditate_clan_tree(clan_id, LIDS[1]) is True)

    print("\n5. Эссенция Памяти: сбор главой")
    ok, msg = await collect_clan_tree_essence(clan_id)
    check("до срока — отказ с таймером", not ok)
    await set_clan_tree_essence_next(clan_id, time.time() - 60)
    ok, msg = await collect_clan_tree_essence(clan_id)
    check("после срока — сбор разрешён", ok)
    # склад клана: «оставить на складе»
    await add_clan_storage(clan_id, essence['id'], 1)
    qty = await get_clan_storage_qty(clan_id, essence['id'])
    check("Эссенция на складе клана (+1)", qty == 1)
    # альтернативно — в инвентарь главы (продажа 500 НМ)
    await add_inventory_item(UID, essence['id'], 1)
    inv = await get_inventory_item(UID, essence['id'])
    check("Эссенция в инвентаре главы (на продажу)", int(inv['quantity'] or 0) >= 1)

    print("\n6. Ограничения и чистка")
    ok, msg = await upgrade_clan_expansion(clan_id, UID, 1)
    check("улучшение Древа запрещено", not ok)
    await delete_clan(clan_id)
    conn3 = await db.get_db()
    cur = await conn3.execute(
        "SELECT COUNT(*) AS c FROM clan_tree_medit WHERE clan_id = ?", (clan_id,))
    check("роспуск клана чистит medit-table",
          (await cur.fetchone())['c'] == 0)

    print(f"\nИТОГО: {passed} passed, {failed} failed")
    await close_db()
    if failed:
        sys.exit(1)


try:
    import random as rnd
    rnd.seed(178)
    asyncio.run(main())
except Exception:
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    try:
        os.remove(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "_test_smoke178.db"))
    except OSError:
        pass
