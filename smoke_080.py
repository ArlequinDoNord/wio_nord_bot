"""Smoke v0.15.21: полное удаление предмета из игры через Хранилище.

delete_item_completely чистит саму запись items и все ссылки:
инвентарь, снаряжение, дропы врагов, награды подземелий, источники ресурсов,
уловы рыбы, лоты рынка, виды рыбы в водоёмах, очереди производства, сделки.

Запуск: .venv\\Scripts\\python.exe smoke_080.py
"""
import asyncio
import json
import os
import sys

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke080.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB

sys.path.insert(0, os.path.dirname(__file__))


async def run():
    from database.db import (
        init_db, close_db, seed_default_items, seed_dungeon,
        ensure_dungeon_shop_items, ensure_dungeon_enemy_drops, ensure_life_items,
        ensure_dungeon_reservoir_items, ensure_water_fish, ensure_kvp_award,
        ensure_market_license_item,
        add_user, add_item, get_item, get_all_items,
        add_inventory_item, get_inventory,
        update_user, get_user,
        add_enemy_drop, get_enemy_drops,
        place_item_offer, get_item_offers,
        add_resource_source,
        add_run_item, get_run_items,
        create_trade,
        delete_item_completely,
    )

    await init_db()
    await seed_default_items()
    await seed_dungeon()
    await ensure_dungeon_shop_items()
    await ensure_dungeon_enemy_drops()
    await ensure_life_items()
    await ensure_dungeon_reservoir_items()
    await ensure_water_fish()
    await ensure_kvp_award()
    await ensure_market_license_item()

    uid = 999080
    uid2 = 999081
    await add_user(uid, "tester", "Тест", "")
    await add_user(uid2, "tester2", "Тест2", "")

    passed = 0
    failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
        else:
            failed += 1
            print(f"  FAIL: {name}")

    # ── 1. предмет + связи ──
    item_id = await add_item(
        name="Хранилищный реликт", description="тест", price=500, sell_price=250,
        rarity=3, category="special", stock=-1, added_by=uid)
    check("предмет создан", await get_item(item_id) is not None)

    await add_inventory_item(uid, item_id, quantity=3)
    inv_before = await get_inventory(uid)
    check("в инвентаре 3 шт", any(i.get('id') == item_id and i['quantity'] == 3
                                  for i in inv_before))

    await update_user(uid, equipment=json.dumps(
        {"weapon": item_id, "head": None, "armor": 999999},
        ensure_ascii=False))
    eq = (await get_user(uid))['equipment']
    check("снаряжение: оружие = предмет", eq and json.loads(eq).get('weapon') == item_id)

    from database.db import get_dungeon_enemies
    dng_id = (await _first_combat_dungeon())[0]['id']
    enemies = await get_dungeon_enemies(dng_id)
    rat = next((e for e in enemies if not e["is_boss"]), None)
    check("враг найден", rat is not None)
    if rat:
        await add_enemy_drop(rat['id'], item_id, 0.4, 2)
        check("дроп добавлен", any(d.get('item_id') == item_id
                                   for d in await get_enemy_drops(rat['id'])))

    await place_item_offer(uid2, item_id, 700)
    check("лот на рынке", await get_item_offers() and True)

    from database.db import get_all_dungeons
    d = await _first_combat_dungeon()
    await add_resource_source(uid, item_id, building_id=1)
    await create_trade(uid, uid2, item_id, 1, 0, None, 0, 10)

    # ── 2. полное удаление ──
    report = await delete_item_completely(item_id)

    check("предмет удалён из items", await get_item(item_id) is None)
    check("нет в списке Хранилища", all(i['id'] != item_id for i in await get_all_items()))
    check("инвентарь очищен",
          all(i.get('id') != item_id for i in await get_inventory(uid)))
    eq = (await get_user(uid))['equipment']
    check("снаряжение очищено", eq and json.loads(eq).get('weapon') is None)
    if rat:
        check("дроп врага убран", all(d.get('item_id') != item_id
                                      for d in await get_enemy_drops(rat['id'])))
        check("дропы других предметов врага сохранились",
              len(await get_enemy_drops(rat['id'])) >= 1)

    check("report: inventory", report.get('inventory') == 1)
    check("report: enemy_drops именно кол-во врагов", report.get('enemy_drops') == (1 if rat else 0))
    check("report: equipment 1 игрок", report.get('equipment') == 1)
    if d:
        pass  # get_all_dungeons уже проверен выше

    await close_db()
    print(f"\nSmoke 080: {passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)


async def _first_combat_dungeon():
    from database.db import get_all_dungeons
    return await get_all_dungeons(training=False)


if __name__ == "__main__":
    try:
        asyncio.run(run())
    except SystemExit:
        raise
    except Exception as e:
        from database.db import close_db
        asyncio.run(close_db())
        print(f"SMOKE ERROR: {e!r}")
        sys.exit(1)