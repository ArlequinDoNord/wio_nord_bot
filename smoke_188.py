# -*- coding: utf-8 -*-
"""Smoke 188 — слияние старых видов протухшей рыбы в «Испорченную рыбу».

1. Старые «Испорченный …» с запасами у двух игроков.
2. merge_spoiled_fish переносит количество в «Испорченную рыбу», старые прячутся.
3. purge_retired_items удаляет старые предметы без потери запасов.
4. Повторный запуск ничего не меняет (идемпотентность).
"""
import asyncio
import os
import sys

os.environ["DATABASE_PATH"] = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "_test_smoke188.db")

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

    import database.db as db
    from database.db import (init_db, close_db, get_db, add_user, add_item,
                             get_item_by_name, add_inventory_item, get_inventory_item,
                             ensure_life_items, merge_spoiled_fish, purge_retired_items)

    await init_db()
    await ensure_life_items()
    conn = await get_db()
    U1, U2 = 188001, 188002
    for uid in (U1, U2):
        await add_user(uid, "t", f"Пилот {uid}", "")

    print("\n1. Старые виды с запасами")
    for name in ("Испорченный сиг", "Испорченный сом"):
        await add_item(name=name, description="старый", price=10, sell_price=5, rarity=1,
                       category="consumable", stock=-1, added_by=0, ap_cost=0,
                       damage=0, heal=5)
    sig = await get_item_by_name("Испорченный сиг")
    som = await get_item_by_name("Испорченный сом")
    await add_inventory_item(U1, sig['id'], 3)
    await add_inventory_item(U1, som['id'], 2)
    await add_inventory_item(U2, som['id'], 4)
    check("старые предметы созданы", sig is not None and som is not None)

    print("\n2. Слияние")
    moved = await merge_spoiled_fish()
    target = await get_item_by_name("Испорченная еда")
    check("«Испорченная еда» засеяна", target is not None)
    check("перенесено 3+2+4 = 9", moved == 9)
    inv1 = await get_inventory_item(U1, target['id'])
    inv2 = await get_inventory_item(U2, target['id'])
    check("у игрока 1 — 5 штук", inv1 is not None and int(inv1['quantity']) == 5)
    check("у игрока 2 — 4 штуки", inv2 is not None and int(inv2['quantity']) == 4)
    check("старый сиг спрятан", (await get_item_by_name("Испорченный сиг"))['is_available'] == 0)
    check("старый инвентарь очищен",
          await get_inventory_item(U1, sig['id']) is None)

    print("\n3. Старые предметы спрятаны, очистка не трогает запасы")
    await purge_retired_items()
    check("старый сом не удалён, а спрятан", (await get_item_by_name("Испорченный сом"))['is_available'] == 0)
    inv1 = await get_inventory_item(U1, target['id'])
    check("у игрока 1 после очистки всё ещё 5", inv1 is not None and int(inv1['quantity']) == 5)

    print("\n4. Повторный запуск не меняет результат")
    moved2 = await merge_spoiled_fish()
    inv1 = await get_inventory_item(U1, target['id'])
    check("повтор переносит 0", moved2 == 0)
    check("у игрока 1 всё ещё 5", inv1 is not None and int(inv1['quantity']) == 5)

    print(f"\nИТОГО: {passed} passed, {failed} failed")
    await close_db()
    return failed


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
