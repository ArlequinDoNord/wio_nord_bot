# -*- coding: utf-8 -*-
"""Smoke 190 — свиток «Рецепт: Тыквенный пирог» применяется, даже если рецепт был скрыт.

1. Рецепт скрыт: использование не списывает свиток, сообщение «временно недоступен».
2. Одноразовая миграция возвращает рецепт и свиток в продажу.
3. Повторный запуск не трогает решение админа (скрытие после миграции сохраняется).
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

    print("\n1. Рецепт скрыт: применение отказано, свиток не списан")
    await conn.execute("UPDATE recipes SET is_available = 0 WHERE name = 'Тыквенный пирог'")
    await conn.execute("UPDATE items SET is_available = 0 WHERE name = 'Рецепт: Тыквенный пирог'")
    await conn.execute("DELETE FROM settings WHERE key = 'pie_recipe_visible_v1'")
    await conn.commit()
    await add_inventory_item(UID, item['id'], 1)
    ok, msg = await learn_recipe_from_item(UID, item['id'])
    check("отказ при скрытом рецепте", ok is False)
    check("сообщение «временно недоступен»", "временно недоступен" in msg)
    inv = await get_inventory_item(UID, item['id'])
    check("свиток не списан", inv is not None and int(inv['quantity']) == 1)

    print("\n2. Миграция возвращает рецепт в продажу")
    await ensure_recipes()
    check("флаг миграции выставлен", (await get_setting("pie_recipe_visible_v1")) == "1")
    ok, msg = await learn_recipe_from_item(UID, item['id'])
    check("свиток применился", ok is True)
    check("рецепт выучен", await has_user_recipe(UID, recipe['id']))

    print("\n3. Решение админа после миграции не перезаписывается")
    await add_user(UID + 1, "t", "Пилот 190b", "")
    await conn.execute("UPDATE recipes SET is_available = 0 WHERE name = 'Тыквенный пирог'")
    await conn.commit()
    await ensure_recipes()
    row = await (await conn.execute(
        "SELECT is_available FROM recipes WHERE name = 'Тыквенный пирог'")).fetchone()
    check("скрытие админа сохраняется", row['is_available'] == 0)

    print(f"\nИТОГО: {passed} passed, {failed} failed")
    await close_db()
    return failed


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
