"""Smoke v0.22.5: переименование рецептов «Пожарить X» → «Жареный/Жареная/Жареное X».

Проверяет:
1. Рецепт, засеянный под старым именем, переименовывается В СИЛУ id (не создаётся дубль).
2. Выученные рецепты игрока (user_recipes) переживают переименование.
3. Товар «Рецепт: <старое>» переименовывается вместе с рецептом.
4. Товар-рецепт, для которого рецепта в базе нет, гасится (is_available = 0) —
   именно из-за таких товаров игрок платил 750 НМ за «Рецепт: Жареная форель»
   и получал «Рецепт не найден».
5. После миграции изучение по переименованному товару работает.
6. Миграция идемпотентна: второй прогон не плодит строки и не поднимает гаснутые товары.
7. Инварианты: у всех жареных результатов есть срок годности (FRIED_PREFIXES),
   у всех рецептов есть цена, старых имён в базе не осталось.

Запуск: .venv\\Scripts\\python.exe smoke_126.py
"""
import asyncio
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke126.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB

sys.path.insert(0, os.path.dirname(__file__))


async def run():
    from database.db import (
        init_db, close_db, add_user, ensure_recipes, ensure_recipe_shop_items,
        get_item, get_item_by_name, add_item, add_inventory_item, get_inventory_item,
        learn_recipe_from_item, has_user_recipe, get_learned_recipes,
        get_db, RECIPES_DEF, RECIPE_ITEM_PRICES, RECIPE_ITEM_PREFIX,
    )
    from bot.handlers.housing import FRIED_PREFIXES

    await init_db()

    passed = 0
    failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
            print(f"  ok   {name}")
        else:
            failed += 1
            print(f"  FAIL {name}")

    conn = await get_db()

    # ── 1. Готовим базу «до переименования»: рецепты и товары со старыми именами ──
    renamed = [r for r in RECIPES_DEF if r.get('old')]
    print(f"Переименовываемых рецептов в коде: {len(renamed)}")

    for r in renamed:
        await conn.execute(
            "INSERT INTO recipes (name, description, result_item_name, result_quantity, "
            "required_expansion, required_level, ingredients, ap_cost, production_time, "
            "rarity) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (r['old'], r['desc'], r['result'], r.get('qty', 1), r['exp'], r['lvl'],
             '[]', r['ap'], r['time'], r.get('rarity', 1)))
        # товар в магазине со старым именем
        price = RECIPE_ITEM_PRICES.get(r['name'], 100)
        await add_item(RECIPE_ITEM_PREFIX + r['old'], "старое описание",
                       price, price // 2, r.get('rarity', 1), 'recipes', -1, 0)
    await conn.commit()

    # Товар-сирота: рецепта с таким именем в базе нет и никогда не будет.
    await add_item(RECIPE_ITEM_PREFIX + "Несуществующий рецепт", "осиротевший товар",
                   500, 250, 1, 'recipes', -1, 0)
    # Коллизия как в проде: товар с НОВЫМ именем уже продаётся, пока рецепт назывался
    # «Пожарить форель» (именно так игрок платил 750 НМ за мёртвый рецепт).
    stale = await add_item(RECIPE_ITEM_PREFIX + "Жареная форель", "старый товар",
                           750, 375, 4, 'recipes', -1, 0)
    await conn.commit()

    # У обоих форелевых товаров лежит инвентарь — его нельзя потерять.
    uid_inv = 752003
    await add_user(uid_inv, f"u{uid_inv}", "Пилот3", "")
    trout = await get_item_by_name(RECIPE_ITEM_PREFIX + "Пожарить форель")
    await add_inventory_item(uid_inv, trout['id'], 2)
    await add_inventory_item(uid_inv, stale, 1)
    await conn.commit()

    before = await (await conn.execute(
        "SELECT id, name FROM recipes WHERE name LIKE 'Пожарить%'")).fetchall()
    check(f"до миграции рецептов со старым именем: {len(before)}", len(before) > 0)
    old_ids = {r['name']: r['id'] for r in before}

    # Игрок, который УЖЕ выучил рецепт «Пожарить сига» — его нельзя терять.
    uid = 752001
    await add_user(uid, f"u{uid}", "Пилот", "")

    async def rid(name):
        row = await (await conn.execute(
            "SELECT id FROM recipes WHERE name = ?", (name,))).fetchone()
        return row['id']

    sig_old_id = await rid("Пожарить сига")
    await conn.execute("INSERT OR IGNORE INTO user_recipes (user_id, recipe_id) VALUES (?, ?)",
                       (uid, sig_old_id))
    await conn.commit()
    check("до миграции рецепт выучен", await has_user_recipe(uid, sig_old_id))

    # ── 2. Миграция ──
    print("\nМиграция:")
    await ensure_recipes()
    await ensure_recipe_shop_items()

    after = await (await conn.execute(
        "SELECT id, name FROM recipes WHERE name LIKE 'Пожарить%'")).fetchall()
    check("старых имён в recipes не осталось", not after)

    total = (await (await conn.execute("SELECT COUNT(*) FROM recipes")).fetchone())['COUNT(*)']
    check(f"всего рецептов: {total} (ожидалось {len(RECIPES_DEF)})",
          total == len(RECIPES_DEF))

    dupes = await (await conn.execute(
        "SELECT name, COUNT(*) c FROM recipes GROUP BY name HAVING c > 1")).fetchall()
    check("дублей имён нет", not dupes)

    # ── 3. id сохранён, выученное не потеряно ──
    print("\nСохранение выученного:")
    sig_new_id = await rid("Жареный сиг")
    check("id рецепта сохранён при переименовании", sig_new_id == sig_old_id)
    check("выученный рецепт на месте", await has_user_recipe(uid, sig_new_id))
    learned = await get_learned_recipes(uid)
    check("в выученных — новое имя", any(x['name'] == "Жареный сиг" for x in learned))
    check("ничего не потеряно и лишнего не появилось",
          [x['name'] for x in learned] == ["Жареный сиг"])

    # ── 4. Товары ──
    print("\nТовары-рецепты:")
    new_item = await get_item_by_name(RECIPE_ITEM_PREFIX + "Жареный сиг")
    check("товар переименован", new_item is not None)
    check("старого товара не осталось",
          await get_item_by_name(RECIPE_ITEM_PREFIX + "Пожарить сига") is None)
    check("цена товара из RECIPE_ITEM_PRICES",
          new_item and new_item['price'] == RECIPE_ITEM_PRICES["Жареный сиг"])
    check("категория осталась 'recipes'", new_item and new_item['category'] == 'recipes')

    orphan = await get_item_by_name(RECIPE_ITEM_PREFIX + "Несуществующий рецепт")
    check("товар-сирота погашен", bool(orphan) and orphan['is_available'] == 0)

    # ── 4a. Коллизия дублей: в магазине должен остаться один «Рецепт: Жареная форель» ──
    print("\nСлияние дублей:")
    dup = await (await conn.execute(
        "SELECT id, is_available FROM items WHERE name = ? AND category = 'recipes'",
        (RECIPE_ITEM_PREFIX + "Жареная форель",))).fetchall()
    check("нет двух доступных товаров с одним именем",
          len([d for d in dup if d['is_available']]) == 1)
    merged_id = [d['id'] for d in dup if d['is_available']][0]
    check("в базе остался один товар с новым именем", len(dup) == 1)
    merged_inv = await get_inventory_item(uid_inv, merged_id)
    check("инвентарь обоих товаров сложен",
          bool(merged_inv) and merged_inv['quantity'] == 3)
    retired = await get_item_by_name(RECIPE_ITEM_PREFIX + "Пожарить форель")
    check("старый дубль погашен", bool(retired) and retired['is_available'] == 0)
    check("с погашенного товара инвентарь убран",
          not await get_inventory_item(uid_inv, retired['id']))
    check("выучить рецепт по объединённому товару можно",
          (await learn_recipe_from_item(uid_inv, merged_id))[0] is True)

    left_alive = await (await conn.execute(
        "SELECT name FROM items WHERE category = 'recipes' AND is_available = 1 "
        "AND name LIKE 'Рецепт: Пожарить%'")).fetchall()
    check("доступных товаров со старым именем не осталось", not left_alive)

    # ── 5. Изучение по переименованному товару работает ──
    print("\nИзучение:")
    uid2 = 752002
    await add_user(uid2, f"u{uid2}", "Пилот2", "")
    await add_inventory_item(uid2, new_item['id'], 1)
    before_inv = await get_inventory_item(uid2, new_item['id'])
    check("предмет-рецепт лежит в инвентаре", bool(before_inv))
    ok, msg = await learn_recipe_from_item(uid2, new_item['id'])
    check("изучение сработало", bool(ok) and "Жареный сиг" in msg)
    after_inv = await get_inventory_item(uid2, new_item['id'])
    check("после изучения предмет списан",
          not after_inv or (after_inv.get('quantity') or 0) < 1)
    check("повторное изучение отвечает «уже выучен»",
          (await learn_recipe_from_item(uid2, new_item['id']))[0] is False)

    # ── 6. Идемпотентность ──
    print("\nИдемпотентность:")
    await ensure_recipes()
    await ensure_recipe_shop_items()
    total2 = (await (await conn.execute("SELECT COUNT(*) FROM recipes")).fetchone())['COUNT(*)']
    check("повторный прогон не плодит рецепты", total2 == total)
    orphan2 = await get_item_by_name(RECIPE_ITEM_PREFIX + "Несуществующий рецепт")
    check("гаснущий товар не воскрешён", bool(orphan2) and orphan2['is_available'] == 0)

    # ── 7. Инварианты ──
    print("\nИнварианты:")
    rows = await (await conn.execute(
        "SELECT name, result_item_name, ingredients FROM recipes")).fetchall()
    fried = [r for r in rows if r['result_item_name'].startswith(FRIED_PREFIXES)]
    check(f"жареных результатов со сроком годности: {len(fried)}", len(fried) == 15)
    no_price = [r['name'] for r in rows if r['name'] not in RECIPE_ITEM_PRICES]
    check("у всех рецептов есть цена", not no_price)
    if no_price:
        print(f"    без цены: {no_price}")
    leftovers = [r['name'] for r in rows if r['name'].startswith('Пожарить')]
    check("имен «Пожарить …» не осталось", not leftovers)

    await close_db()
    print(f"\nИТОГО: {passed} ok, {failed} FAIL")
    if failed:
        print("ЕСТЬ ПАДЕНИЯ")
    else:
        print("ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ")
    for suffix in ("", "-wal", "-shm"):
        try:
            os.remove(_TEST_DB + suffix)
        except OSError:
            pass
    return 1 if failed else 0


if __name__ == "__main__":
    _code = 0
    try:
        _code = asyncio.run(run()) or 0
    except Exception:
        import traceback
        traceback.print_exc()
        _code = 1
    finally:
        # aiosqlite держит фоновый поток: при исключении процесс иначе не завершится.
        # os._exit не сбрасывает буфер — делаем это сами, иначе тест молчит.
        sys.stdout.flush()
        sys.stderr.flush()
        os._exit(_code)
