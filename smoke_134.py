"""Smoke v0.22.13: менеджер рецептов крафта (создание/правка/удаление).

Проверяем:
  • DB-слой: list_recipes_for_admin, upsert_recipe (создать + обновить по id),
    find_recipe (дубликаты), ensure_recipe_shop_item (товар «Рецепт: …»,
    цена сохраняется при повторной синхронизации), set_recipe_visible,
    delete_recipe;
  • менеджерные рецепты не участвуют в ensure_recipes() (сидирование идёт
    только по RECIPES_DEF) и не гаснутся ensure_recipe_shop_items() (товар
    живёт, пока рецепт в базе доступен);
  • разводка в исходниках: модуль bot/handlers/admin_recipes.py подключён
    в main.py (включая middleware), из админ-панели есть кнопка recadm:menu,
    коллизий namespace recadm: нет (см. также smoke_127).

Запуск: .venv\\Scripts\\python.exe smoke_134.py
"""
import asyncio
import json
import os
import sys

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke134.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB

sys.path.insert(0, os.path.dirname(__file__))

ROOT = os.path.dirname(__file__)


async def run():
    from database.db import (init_db, close_db, get_db, get_item_by_name,
                             list_recipes_for_admin, upsert_recipe,
                             find_recipe, ensure_recipe_shop_item,
                             set_recipe_visible, delete_recipe,
                             ensure_recipes, ensure_recipe_shop_items,
                             get_recipe)
    await init_db()

    passed = 0
    failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
            print(f"  OK   {name}")
        else:
            failed += 1
            print(f"  FAIL {name}")

    # ---- создание/правка/чтение ----
    rid = await upsert_recipe(
        "Пробный пирог", "Пробный рецепт менеджера.", "Пробный пирог", 1,
        "kitchen", 2, [("Карась", 5), ("Мука", 1)], 8, 40, 3)
    check("upsert_recipe создал рецепт", isinstance(rid, int) and rid > 0)

    r = await get_recipe(rid)
    check("рецепт читается", r is not None and r["name"] == "Пробный пирог")
    check("ингредиенты сохранились", json.loads(r["ingredients"]) == [["Карась", 5], ["Мука", 1]])

    dict_rid = await upsert_recipe(
        "Пробный суп", "Диктовые ингредиенты.", "Пробный суп", 1,
        "kitchen", 1, [{"name": "Сиг", "qty": 2}, {"name": "Муксун", "qty": 1}], 6, 30, 2)
    r = await get_recipe(dict_rid)
    check("словарные ингредиенты нормализуются в пары",
          json.loads(r["ingredients"]) == [["Сиг", 2], ["Муксун", 1]])

    rid2 = await upsert_recipe(
        "Пробный пирог", "Обновлённое описание.", "Пробный пирог", 2,
        "kitchen", 2, [("Карась", 5), ("Мука", 2)], 9, 50, 3, recipe_id=rid)
    check("upsert_recipe обновил по id", rid2 == rid)
    r = await get_recipe(rid)
    check("правка применилась", r["result_quantity"] == 2 and r["production_time"] == 50
          and r["description"] == "Обновлённое описание.")

    dup = await find_recipe("Пробный пирог", "kitchen", 2)
    check("find_recipe находит дубликат", dup is not None and dup["id"] == rid)
    check("find_recipe не видит другой уровень", await find_recipe("Пробный пирог", "kitchen", 1) is None)

    # ---- товар-рецепт и цена ----
    await ensure_recipe_shop_item(r, price=250)
    item = await get_item_by_name("Рецепт: Пробный пирог")
    check("товар «Рецепт: …» создан", item is not None and item["category"] == "recipes"
          and item["is_available"] == 1)
    check("цена товара задана", item["price"] == 250 and item["sell_price"] == 125)

    await ensure_recipe_shop_item(r)
    item2 = await get_item_by_name("Рецепт: Пробный пирог")
    check("повторная синхронизация не сбрасывает цену", item2["price"] == 250)

    # ---- ensure_recipes/ensure_recipe_shop_items не трогают менеджера ----
    await ensure_recipes()
    check("ensure_recipes не удаляет менеджерный рецепт",
          await get_recipe(rid) is not None)
    r = await get_recipe(rid)
    check("ensure_recipes не меняет правки менеджера",
          r["result_quantity"] == 2 and r["description"] == "Обновлённое описание.")
    await ensure_recipe_shop_items()
    item3 = await get_item_by_name("Рецепт: Пробный пирог")
    check("ensure_recipe_shop_items не гасит товар доступного менеджерного рецепта",
          item3 is not None and item3["is_available"] == 1)

    # ---- видимость и удаление ----
    await set_recipe_visible(rid, False)
    r = await get_recipe(rid)
    item4 = await get_item_by_name("Рецепт: Пробный пирог")
    check("set_recipe_visible(false) гасит рецепт и товар",
          r["is_available"] == 0 and item4["is_available"] == 0)
    await set_recipe_visible(rid, True)
    check("set_recipe_visible(true) возвращает",
          (await get_recipe(rid))["is_available"] == 1
          and (await get_item_by_name("Рецепт: Пробный пирог"))["is_available"] == 1)

    ok = await delete_recipe(rid)
    check("delete_recipe скрывает рецепт", ok and (await get_recipe(rid))["is_available"] == 0)
    item5 = await get_item_by_name("Рецепт: Пробный пирог")
    check("delete_recipe скрывает товар из лавки", item5 is not None and item5["is_available"] == 0)

    await ensure_recipes()
    await ensure_recipe_shop_items()
    item6 = await get_item_by_name("Рецепт: Пробный пирог")
    check("после удаления ensure_* не возвращают товар в лавку",
          item6 is not None and item6["is_available"] == 0)

    # ---- разводка в исходниках ----
    mod = os.path.join(ROOT, "bot", "handlers", "admin_recipes.py")
    with open(mod, encoding="utf-8") as f:
        src = f.read()
    check("модуль admin_recipes.py есть", os.path.exists(mod))
    check("router в менеджере", "router = Router()" in src)
    check("префикс recadm: в callbacks", "recadm:menu" in src and "recadm:open:" in src)

    with open(os.path.join(ROOT, "main.py"), encoding="utf-8") as f:
        main_src = f.read()
    check("admin_recipes подключён в main.py",
          "from bot.handlers.admin_recipes import router as admin_recipes_router" in main_src
          and "include_router(admin_recipes_router)" in main_src)
    check("админка+менеджер до новостей",
          main_src.find("include_router(admin_router)") < main_src.find("include_router(news_router)")
          and main_src.find("include_router(admin_recipes_router)") < main_src.find("include_router(news_router)"))
    check("менеджер в middleware-цикле", "admin_recipes_router" in main_src.split(
        "for r in (")[1].split("):")[0])

    with open(os.path.join(ROOT, "keyboards", "keyboards.py"), encoding="utf-8") as f:
        kb = f.read()
    check("кнопка менеджера в админ-панели (can_manage_shop)",
          "recadm:menu" in kb and "\"✿ Менеджер рецептов\"" in kb or "\"📜 Менеджер рецептов\"" in kb)

    await close_db()
    print()
    print(f"ИТОГО: {passed} OK, {failed} FAIL")
    return failed


if __name__ == "__main__":
    sys.exit(asyncio.run(run()))