# -*- coding: utf-8 -*-
"""Smoke 217 — вкладка «Выученные рецепты» в профиле и переименование «Лесная поляна» → «Прогалина».

1. Пустой список: текст «Пока ни один рецепт не выучен», кнопка «В профиль».
2. Выучено больше страницы: листание, группы по станциям, порядок кухня → верстак.
3. Карточка: ингредиенты пилота (✅/❌), ОД, станция; не выученный рецепт → None.
4. Английский интерфейс: заголовки и кнопки переведены.
5. Миграция зоны: старый заголовок → «Прогалина»; правка админа не перетирается.
"""
import asyncio
import sys

from tests_support import Checker, use_test_db

_TEST_DB = use_test_db(__file__, "smoke217")

UID = 217001


async def main():
    check = Checker()

    from database.db import (
        init_db, close_db, add_user, get_recipes, learn_recipe, get_item_by_name,
        add_inventory_item, get_db, ensure_forest_zones, ensure_recipes, add_item,
    )
    from bot.handlers import profile as pf
    from utils.i18n import _current

    await init_db()
    await ensure_recipes()
    await add_user(UID, 'rc', 'Рецепты', "")

    def texts(kb):
        return [b.text for row in kb.inline_keyboard for b in row]

    def cbs(kb):
        return [b.callback_data for row in kb.inline_keyboard for b in row]

    print("\n1. Пустой список")
    text, kb = await pf.build_recipes_screen(UID, 0)
    check("пусто: текст «Пока ни один рецепт не выучен»", "Пока ни один рецепт не выучен" in text)
    check("пусто: только кнопка «В профиль»", cbs(kb) == ["profile:open"])

    print("\n2. Выучено больше страницы")
    kitchen = await get_recipes(expansion="kitchen")
    workbench = await get_recipes(expansion="workbench")
    everything = list(kitchen) + list(workbench)
    for r in everything:
        await learn_recipe(UID, r["id"])
    total = len(everything)
    check("рецептов больше одной страницы", total > pf.RECIPES_PER_PAGE)

    text1, kb1 = await pf.build_recipes_screen(UID, 0)
    check("заголовок с числом рецептов", f"({total})" in text1)
    check("на первой странице 8 кнопок рецептов",
          sum(1 for c in cbs(kb1) if c and c.startswith("profile:recipe:")) == pf.RECIPES_PER_PAGE)
    check("есть «вперёд»", "profile:recipes:1" in cbs(kb1))
    check("«назад» на первой странице нет", "profile:recipes:-1" not in cbs(kb1))
    check("группа «Кухня» в тексте", "🍳 Кухня" in text1)
    if kitchen and workbench:
        check("кухня идёт раньше верстака", text1.index("🍳 Кухня") < text1.index("🔨 Верстак")
              if "🔨 Верстак" in text1 else True)

    last_page = -(-total // pf.RECIPES_PER_PAGE) - 1
    text_last, kb_last = await pf.build_recipes_screen(UID, last_page)
    check("последняя страница: «вперёд» нет", f"profile:recipes:{last_page + 1}" not in cbs(kb_last))
    check("последняя страница: «назад» есть", f"profile:recipes:{last_page - 1}" in cbs(kb_last))
    text_over, _ = await pf.build_recipes_screen(UID, 999)
    check("страница сверх диапазона — последняя", text_over == text_last)

    print("\n3. Карточка")
    sample = everything[0]
    card = await pf.build_recipe_card(UID, sample["id"])
    check("карточка выученного рецепта есть", card is not None)
    if card:
        ctext, ckb = card
        check("в карточке название рецепта", sample["name"] in ctext)
        check("есть строка ОД", "ОД:" in ctext)
        check("есть кнопка «К рецептам»", "profile:recipes" in cbs(ckb))
        check("есть ингредиенты", "Ингредиенты:" in ctext or "Ингредиентов нет." in ctext)
    check("не выученный рецепт → None", await pf.build_recipe_card(UID + 1, sample["id"]) is None)

    print("\n3б. ✅ у ингредиента, которого есть достаточно")
    from utils.crafting import parse_ingredients
    pick = None
    for r in everything:
        ings = parse_ingredients(r)
        if not ings:
            continue
        ing_name = ings[0][0]
        if not await get_item_by_name(ing_name):
            await add_item(ing_name, "тестовый ингредиент", 10, 5, 1, "resource", -1, 0)
        pick = (r, ing_name)
        break
    check("нашёлся рецепт с ингредиентом-предметом", pick is not None)
    if pick:
        r, ing_name = pick
        item = await get_item_by_name(ing_name)
        await add_inventory_item(UID, item["id"], 999)
        ctext2, _ = await pf.build_recipe_card(UID, r["id"])
        check("есть ✅ при наличии", "✅" in ctext2)

    print("\n4. Английский интерфейс")
    token = _current.set("en")
    try:
        text_en, kb_en = await pf.build_recipes_screen(UID, 0)
        check("en: заголовок «LEARNED RECIPES»", "LEARNED RECIPES" in text_en)
        check("en: группа «Kitchen»", "Kitchen" in text_en)
        check("en: кнопка «Back to profile»", "🏠 Back to profile" in texts(kb_en) or
              "🔙 Back to profile" in texts(kb_en) or any("Back to profile" in t for t in texts(kb_en)))
        card_en = await pf.build_recipe_card(UID, sample["id"])
        check("en: карточка с «AP:»", card_en is not None and "AP:" in card_en[0])
    finally:
        _current.reset(token)

    print("\n5. Миграция «Лесная поляна» → «Прогалина»")
    conn = await get_db()
    await conn.execute("UPDATE forest_zones SET title = 'Лесная поляна' WHERE key = 'clearing'")
    await conn.commit()
    await ensure_forest_zones()
    cur = await conn.execute("SELECT title FROM forest_zones WHERE key = 'clearing'")
    check("старый заголовок переименован", (await cur.fetchone())["title"] == "Прогалина")
    cur = await conn.execute("SELECT title FROM forest_zones WHERE key = 'glade'")
    check("опушка не тронута", (await cur.fetchone())["title"] == "Опушка леса")
    await conn.execute("UPDATE forest_zones SET title = 'Тайная тропа' WHERE key = 'clearing'")
    await conn.commit()
    await ensure_forest_zones()
    cur = await conn.execute("SELECT title FROM forest_zones WHERE key = 'clearing'")
    check("правка админа не перетирается", (await cur.fetchone())["title"] == "Тайная тропа")

    failed = check.summary()
    await close_db()
    return failed


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
