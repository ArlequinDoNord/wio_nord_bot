# -*- coding: utf-8 -*-
"""Smoke 215 — «Кислородная маска» удалена; английские разделы города/инвентаря/магазина.

1. Маска не входит в стартовый набор (DEFAULT_ITEMS) и попадает в RETIRED_ITEMS.
2. Если маска есть в БД (инвентарь + снаряжение), init_db() её чистит.
3. Города: названия локаций в ru — как раньше, в en — перевод (place_name).
4. Подменю города (Деловой/Административный/Загородные) и главный список.
5. Разделы магазина и инвентаря, категории предметов — ru и en.
"""
import asyncio
import json
import os
import sys

os.environ["DATABASE_PATH"] = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "_test_smoke215.db")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

MASK = "Кислородная маска"


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

    import config
    from database.db import init_db, get_db, add_user, close_db, get_item_by_name
    from utils.i18n import _current, place_name
    from utils.helpers import category_label
    from keyboards.keyboards import (
        city_keyboard, business_quarter_keyboard, admin_quarter_keyboard,
        countryside_keyboard, shop_keyboard, shop_catalog_keyboard,
    )
    from bot.handlers.inventory import inv_categories_markup

    print("\n1. Маска удалена из кода")
    import database.db as D
    default_names = {entry[0] for entry in D.DEFAULT_ITEMS}
    check("нет в DEFAULT_ITEMS", MASK not in default_names)
    check("есть в RETIRED_ITEMS", MASK in D.RETIRED_ITEMS)

    print("\n2. Старт чистит маску из БД")
    await init_db()
    conn = await get_db()
    await conn.execute(
        "INSERT INTO items (name, description, price, sell_price, rarity, category, stock, added_by)"
        " VALUES (?, 'тест', 90, 45, 1, 'equipment', -1, 0)", (MASK,))
    uid = 215001
    await add_user(uid, 'm', 'Маска', "")
    item = await get_item_by_name(MASK)
    await conn.execute(
        "INSERT INTO inventory (user_id, item_id, quantity) VALUES (?, ?, 1)", (uid, item["id"]))
    await conn.commit()
    await init_db()
    check("после init_db маски нет в items", await get_item_by_name(MASK) is None)
    cur = await conn.execute("SELECT COUNT(*) AS c FROM inventory WHERE user_id = ?", (uid,))
    check("инвентарь пилота очищен от маски", (await cur.fetchone())["c"] == 0)

    print("\n3. place_name: ru как есть, en — перевод")
    check("ru: кнопка из БД не меняется", place_name("kvp", "Курс выживания") == "Курс выживания")
    from utils.helpers import is_main_menu_text
    check("«Банк», «Каталог», «Улов» не считаются кнопкой меню (FSM)",
          not any(is_main_menu_text(x) for x in ("Банк", "Каталог", "Улов", "Оружие")))
    token = _current.set("en")
    try:
        check("en: kvp → Survival Course", place_name("kvp", "Курс выживания") == "Survival Course")
        check("en: неизвестный ключ — исходная строка", place_name("zzz", "Что-то") == "Что-то")
    finally:
        _current.reset(token)

    def texts(markup):
        return [b.text for row in markup.inline_keyboard for b in row]

    print("\n4. Город: главный список и подменю (ru / en)")
    locs = [{"key": "kvp", "name": "Курс выживания"}]
    check("ru: главный список «🧭 Курс выживания»",
          "🧭 Курс выживания" in texts(city_keyboard(locations=locs)))
    token = _current.set("en")
    try:
        en_city = texts(city_keyboard(locations=locs))
        check("en: главный список «🧭 Survival Course»", "🧭 Survival Course" in en_city)
        en_bq = texts(business_quarter_keyboard())
        check("en: деловой квартал — Library / Contract Board",
              "📚 Library" in en_bq and "📜 Contract Board" in en_bq)
        en_aq = texts(admin_quarter_keyboard())
        check("en: административный — Bank / Air Force HQ",
              "🏦 Bank" in en_aq and "🎖️ Air Force HQ" in en_aq)
        en_cs = texts(countryside_keyboard())
        check("en: загородные — Outskirts Forest / Iron Mine",
              "🌲 Outskirts Forest" in en_cs and "⛏️ Iron Mine" in en_cs)
        check("en: кнопки «В город» переведены", "🔙 Back to city" in en_bq)
        check("en: разделы магазина", texts(shop_keyboard()) == [
            "Catalog", "My purchases", "Sell an item"])
        check("en: категория магазина", "Weapons (2)" in texts(shop_catalog_keyboard({"weapon": 2})))
        check("en: категория предметов", category_label("weapon") == "Weapons")
        inv_en = texts(inv_categories_markup(
            [{"category": "weapon", "quantity": 1}],
            [{"name": "Сиг", "item_id": 1, "weight": 1, "rarity": 1}]))
        check("en: инвентарь — Gear / Catch / Weapons",
              "🛡️ Gear" in inv_en and "🐟 Catch — 1" in inv_en
              and any("Weapons" in t for t in inv_en))
    finally:
        _current.reset(token)

    print("\n5. Русский интерфейс не изменился")
    ru_bq = texts(business_quarter_keyboard())
    check("ru: деловой квартал — прежние надписи",
          "📚 Библиотека" in ru_bq and "📜 Доска контрактов" in ru_bq
          and "🔬 НИИ Северной Кибернетики" in ru_bq)
    check("ru: категория магазина", category_label("weapon") == "Оружие")
    check("ru: категория mining", category_label("mining") == "⛏ Добыча ресурсов")
    ru_inv = texts(inv_categories_markup(
        [{"category": "weapon", "quantity": 1}],
        [{"name": "Сиг", "item_id": 1, "weight": 1, "rarity": 1}]))
    check("ru: инвентарь — Снаряжение / Улов", "🛡️ Снаряжение" in ru_inv
          and "🐟 Улов — 1" in ru_inv)
    check("ru: разделы магазина", texts(shop_keyboard()) == [
        "Каталог", "Мои покупки", "Продать товар"])

    print(f"\nИТОГО: {passed} passed, {failed} failed")
    await close_db()
    if failed:
        sys.exit(1)


try:
    asyncio.run(main())
except Exception:
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    try:
        os.remove(os.path.join(os.path.dirname(os.path.abspath(__file__)), "_test_smoke215.db"))
    except OSError:
        pass
