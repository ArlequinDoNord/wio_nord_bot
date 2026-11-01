# -*- coding: utf-8 -*-
"""Smoke 190 — выученный рецепт работает, даже если скрыт из магазина.

is_available — только видимость в магазине. Праздничные рецепты скрыты, но выдаются
свитком (лавка/достижение): свиток должен выучиваться и крафт должен работать.

1. Скрытый рецепт: свиток выучивается, рецепт попадает в список выученных.
2. Повторный запуск (ensure_recipes) не выставляет видимость обратно и не отнимает рецепт.
"""
import asyncio
import os
import sys

os.environ["DATABASE_PATH"] = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "_test_smoke190.db")

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

    from database.db import (init_db, close_db, get_db, add_user, get_item_by_name,
                             add_inventory_item, get_inventory_item, ensure_firelab_items,
                             get_learned_recipes,
                             ensure_recipes, ensure_recipe_shop_items, learn_recipe_from_item,
                             get_setting, has_user_recipe)

    await init_db()
    await ensure_firelab_items()
    await ensure_recipes()
    await ensure_recipe_shop_items()
    conn = await get_db()
    UID = 190001
    await add_user(UID, "t", "Пилот 190", "")

    item = await get_item_by_name("Рецепт: Тыквенный пирог")
    recipe = await (await conn.execute(
        "SELECT id FROM recipes WHERE name = 'Тыквенный пирог'")).fetchone()
    check("свиток и рецепт созданы", item is not None and recipe is not None)

    print("\n1. Рецепт скрыт из магазина: свиток всё равно выучивается и работает")
    await conn.execute("UPDATE recipes SET is_available = 0 WHERE name = 'Тыквенный пирог'")
    await conn.execute("UPDATE items SET is_available = 0 WHERE name = 'Рецепт: Тыквенный пирог'")
    await conn.commit()
    await add_inventory_item(UID, item['id'], 1)
    ok, msg = await learn_recipe_from_item(UID, item['id'])
    check("свиток выучился при скрытом рецепте", ok is True)
    check("свиток списан после обучения", (await get_inventory_item(UID, item['id'])) is None
          or int((await get_inventory_item(UID, item['id']))['quantity']) == 0)
    learned = [r['name'] for r in await get_learned_recipes(UID)]
    check("рецепт в списке выученных (для крафта)", "Тыквенный пирог" in learned)

    print("\n2. Повторный запуск не выставляет рецепт обратно")
    await ensure_recipes()
    row = await (await conn.execute(
        "SELECT is_available FROM recipes WHERE name = 'Тыквенный пирог'")).fetchone()
    check("скрытие админа сохраняется", row['is_available'] == 0)
    learned = [r['name'] for r in await get_learned_recipes(UID)]
    check("выученный рецепт остаётся доступен после перезапуска", "Тыквенный пирог" in learned)

    print(f"\nИТОГО: {passed} passed, {failed} failed")
    await close_db()
    return failed


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
