# -*- coding: utf-8 -*-
"""Smoke 196 — пожертвования Древу Огня, талисман памяти, испорченная еда.

1. Лимит сбора: огненный гриб/ягоды/руда добываются не больше требуемого количества.
2. Пожертвование: сдаётся по видам, больше требуемого не принимается.
3. Талисман памяти: выдаётся один раз после полного пожертвования; потом не сдать.
4. Талисман: регенерация +1 за ход, только когда надет.
5. Предметы пожертвований не продаются (цена 0, не на рынке).
6. «Испорченная рыба» переименовывается в «Испорченную еду», запасы сохраняются.
7. Ягоды пожертвования есть в таблице поиска ягод прогалины.
"""
import asyncio
import os
import sys

os.environ["DATABASE_PATH"] = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "_test_smoke196.db")

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
    from database.db import (init_db, close_db, add_user, get_item_by_name, add_item,
                             ensure_forest_enemies, ensure_firelab_items, add_inventory_item,
                             get_inventory_item, set_equipment_slot, get_talisman_regen,
                             tree_collect_allowed, tree_record_collect, tree_donate,
                             tree_donation_progress, get_db)

    await init_db()
    await ensure_firelab_items()
    await ensure_forest_enemies()
    UID = 196001
    await add_user(UID, "t", "Пилот 196", "")

    print("\n1. Лимит сбора")
    mush, berry, ore = config.FIRE_MUSHROOM_NAME, config.FIRE_BERRY_NAME, config.FIRE_ORE_NAME
    check("гриб сначала можно добыть", await tree_collect_allowed(UID, mush))
    await tree_record_collect(UID, mush)
    await tree_record_collect(UID, mush)
    check("после 2 грибов третий не выпадет", not await tree_collect_allowed(UID, mush))
    check("обычные предметы лимита не имеют", await tree_collect_allowed(UID, "Яблоко"))

    print("\n2. Пожертвование по видам")
    m_item = await get_item_by_name(mush)
    b_item = await get_item_by_name(berry)
    o_item = await get_item_by_name(ore)
    await add_inventory_item(UID, m_item['id'], 2)
    await add_inventory_item(UID, b_item['id'], 2)
    await add_inventory_item(UID, o_item['id'], 2)
    ok, _msg, granted = await tree_donate(UID, mush, qty=99)
    check("гриб сдан", ok and not granted)
    check("сдано 2 гриба", (await tree_donation_progress(UID))["items"][mush] == (2, 2))
    check("больше грибов не принимается", not (await tree_donate(UID, mush, qty=1))[0])
    ok, _msg, granted = await tree_donate(UID, berry, qty=99)
    check("ягоды сданы, талисмана ещё нет", ok and not granted)

    print("\n3. Талисман памяти — один раз")
    ok, _msg, granted = await tree_donate(UID, ore, qty=99)
    check("руда сдана — талисман выдан", ok and granted)
    tal = await get_item_by_name(config.FIRE_TALISMAN_NAME)
    inv = await get_inventory_item(UID, tal['id'])
    check("талисман в инвентаре", inv is not None and int(inv['quantity']) == 1)
    check("после полного пожертвования больше нельзя",
          not (await tree_donate(UID, ore, qty=1))[0])
    prog = await tree_donation_progress(UID)
    check("прогресс отмечен как получен", prog["talisman"] is True)

    print("\n4. Регенерация талисмана")
    check("не надет — регенерации нет", await get_talisman_regen(UID) == 0)
    await set_equipment_slot(UID, "talisman", tal['id'])
    check("надет — +1 за ход", await get_talisman_regen(UID) == config.FIRE_TALISMAN_REGEN == 1)

    print("\n5. Не продаётся")
    for name in (mush, berry, ore, config.FIRE_TALISMAN_NAME):
        it = await get_item_by_name(name)
        check(f"«{name}»: цена продажи 0, не на рынке",
              it is not None and int(it['sell_price']) == 0 and int(it['market_ok']) == 0)

    print("\n6. Испорченная еда")
    await add_item(name="Испорченная рыба", description="старое имя", price=1, sell_price=0,
                   rarity=1, category="consumable", stock=-1, added_by=0, ap_cost=0,
                   damage=0, heal=5)
    old = await get_item_by_name("Испорченная рыба")
    check("старое имя есть (перед миграцией)", old is not None)
    await add_inventory_item(UID, old['id'], 3)
    await db._rename_spoiled_food()
    renamed = await get_item_by_name(config.FIRE_SPOILED_FOOD_NAME)
    check("переименована в «Испорченную еду»", renamed is not None and renamed['id'] == old['id'])
    inv = await get_inventory_item(UID, renamed['id'])
    check("запасы сохранены", inv is not None and int(inv['quantity']) == 3)

    print("\n7. Ягоды пожертвования в поиске прогалины")
    clearing = config.FOREST_BERRY_TABLE["clearing"]
    check("Пылающие ягоды в таблице прогалины", any(k == berry for k, _ in clearing))
    check("прогалина: сумма 100%", sum(p for _, p in clearing) == 100)

    print(f"\nИТОГО: {passed} passed, {failed} failed")
    await close_db()
    return failed


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
