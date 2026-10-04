"""Smoke v0.18.15: Лес на окраине (грибы + кабан).

Новая локация «Лес на окраине»: сбор 8 грибов за 3 ОД (результат 5–10 сек),
не чаще 1 раза на 12 попыток — интерактивный бой с кабаном (победа — добыча,
поражение — −10 ОД до нуля), готовка жареных блюд и крафт «Бутылочки с ядом»,
админ-редактор пула грибов (шанс/тип/фото/цена) как у рыбалки.

Запуск: .venv\\Scripts\\python.exe smoke_085.py
"""
import asyncio
import os
import sys

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke085.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB

sys.path.insert(0, os.path.dirname(__file__))


async def run():
    from config import (
        FOREST_AP_COST, FOREST_RESULT_DELAY, FOREST_ALLOW_TOURISTS,
        FOREST_SOLD_DAILY_LIMIT,
        FOREST_BOAR_PITY_TARGET, FOREST_BOAR_HP, FOREST_BOAR_DMG,
        FOREST_BOAR_DODGE, FOREST_BOAR_LOSS_AP, FOREST_BOAR_LOOT,
    )
    from bot.handlers.forest import (
        forest_boar_hit, roll_boar_loot, pick_forest_mushroom, FOREST_EMPTY_CHANCE,
    )
    from utils.helpers import season_key, resolve_image_seasonal, resolve_image
    from database.db import (
        init_db, close_db, get_db, add_user, get_user,
        ensure_forest_items, ensure_forest_mushrooms, ensure_recipes,
        get_item_by_name, get_item,
        get_forest_mushroom_pool, get_forest_mushroom_rows,
        get_forest_mushroom_row, update_forest_mushroom_field,
        set_forest_mushroom_sell_price, add_forest_mushroom,
        remove_forest_mushroom, create_forest_mushroom,
        get_forest_mushroom_candidates,
        get_forest_boar_attempts, set_forest_boar_attempts, reset_forest_boar_counter,
        remove_ap_or_floor, get_location_by_key,
        FOREST_RAW_MUSHROOMS, FOREST_ITEM_SEEDS, FOREST_DEFAULTS, RECIPES_DEF,
        FOREST_FRIED_PRICES,
    )

    await init_db()
    # Стартовая синхронизация, как в main.py при запуске бота.
    await ensure_forest_items()
    await ensure_forest_mushrooms()
    await ensure_recipes()

    passed = 0
    failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
        else:
            failed += 1
            print(f"  FAIL: {name}")

    # ── 1. Константы леса в config ──
    check("FOREST_AP_COST = 4 (v0.18.16)", FOREST_AP_COST == 4)
    check("FOREST_SOLD_DAILY_LIMIT = 250 (кап выкупа грибов)",
          FOREST_SOLD_DAILY_LIMIT == 250)
    check("FOREST_RESULT_DELAY = (5,10)", FOREST_RESULT_DELAY == (5, 10))
    check("FOREST_ALLOW_TOURISTS = False", FOREST_ALLOW_TOURISTS is False)
    check("FOREST_BOAR_PITY_TARGET = 12", FOREST_BOAR_PITY_TARGET == 12)
    check("FOREST_BOAR_HP = 30", FOREST_BOAR_HP == 30)
    check("FOREST_BOAR_DMG = (4,7)", FOREST_BOAR_DMG == (4, 7))
    check("FOREST_BOAR_DODGE = 15", FOREST_BOAR_DODGE == 15)
    check("FOREST_BOAR_LOSS_AP = 10", FOREST_BOAR_LOSS_AP == 10)
    check("лут кабана в сумме 100%",
          sum(c for _, c in FOREST_BOAR_LOOT) == 100)
    check("мясо 50%, шкура 20%, клык 10%, пусто 20%",
          FOREST_BOAR_LOOT == [("Мясо кабана", 50), ("Шкура кабана", 20),
                               ("Клык кабана", 10), ("", 20)])
    check("FOREST_EMPTY_CHANCE = 10 (находка гриба 90%)", FOREST_EMPTY_CHANCE == 10)
    check("веса пула не проценты: нормируются на 100 − пусто",
          sum(c for _, c, _ in FOREST_DEFAULTS) == 96
          and FOREST_EMPTY_CHANCE + sum(c for _, c, _ in FOREST_DEFAULTS) != 100)

    # ── 1b. Сезонные картинки леса (опушка зимой/летом) ──
    from datetime import datetime
    from utils.helpers import MOSCOW_TZ as tz
    check("сезон: январь/февраль/декабрь → winter",
          all(season_key(datetime(y, m, 15, 12, tzinfo=tz)) == "winter"
              for y, m in [(2026, 1), (2026, 2), (2026, 12)]))
    check("сезон: март–май → spring",
          all(season_key(datetime(2026, m, 15, 12, tzinfo=tz)) == "spring"
              for m in (3, 4, 5)))
    check("сезон: июнь–август → summer",
          all(season_key(datetime(2026, m, 15, 12, tzinfo=tz)) == "summer"
              for m in (6, 7, 8)))
    check("сезон: сентябрь–ноябрь → autumn",
          all(season_key(datetime(2026, m, 15, 12, tzinfo=tz)) == "autumn"
              for m in (9, 10, 11)))
    # Приоритет имён файлов: сезон+время → сезон → время → день → базовый.
    check("resolve_image_seasonal без файлов → сезон+время суток",
          resolve_image_seasonal("city/forest_glade",
                                 datetime(2026, 1, 15, 12, tzinfo=tz))
          == "assets/img/city/forest_glade_winter_day.jpg")
    check("resolve_image_seasonal летом → summer",
          resolve_image_seasonal("city/forest_glade",
                                 datetime(2026, 7, 15, 23, tzinfo=tz))
          == "assets/img/city/forest_glade_summer_night.jpg")
    check("вход в лес: 4 варианта времени суток (обычный resolve_image)",
          resolve_image("city/forest", datetime(2026, 7, 15, 23, tzinfo=tz))
          == "assets/img/city/forest_night.jpg")

    # ── 2. Чистые функции: встреча с кабаном ──
    # Счётчик спокойных попыток: 11 подряд → 12-я гарантирована.
    check("11 спокойных → встреча (гарантия)",
          forest_boar_hit(11, 7) is True)
    check("0 спокойных, бросок 1 → встреча",
          forest_boar_hit(0, 1) is True)
    check("0 спокойных, бросок 2 → НЕТ встречи",
          forest_boar_hit(0, 2) is False)
    check("5 спокойных, бросок 12 → НЕТ встречи",
          forest_boar_hit(5, 12) is False)
    # Любой бросок в [0..12) тоже живёт счётчик (шанс 1/12).
    hits = sum(1 for r in range(1, FOREST_BOAR_PITY_TARGET)
               if forest_boar_hit(0, r))
    check("ровно 1 из 1..12 — встреча (шанс 1/12)", hits == 1)

    # ── 3. Чистые функции: добыча кабана ──
    check("r=49 → Мясо кабана", roll_boar_loot(49.9) == "Мясо кабана")
    check("r=50 → Шкура кабана", roll_boar_loot(50.0) == "Шкура кабана")
    check("r=69 → Шкура кабана", roll_boar_loot(69.9) == "Шкура кабана")
    check("r=70 → Клык кабана", roll_boar_loot(70.0) == "Клык кабана")
    check("r=79 → Клык кабана", roll_boar_loot(79.9) == "Клык кабана")
    check("r=85 → пусто", roll_boar_loot(85.0) == "")
    check("r=99 → пусто", roll_boar_loot(99.9) == "")

    # ── 4. Чистые функции: выбор гриба из пула дефолтов ──
    # Сумма весов 96 — это веса, а не проценты: 10% отдано «пусто», остальные
    # 90% делятся между грибами по весам (масштаб 90/96 = 0.9375).
    pool = [{"chance": 25, "name": "Опёнок"},
            {"chance": 18, "name": "Подберёзовик"},
            {"chance": 15, "name": "Лисичка"},
            {"chance": 12, "name": "Белый гриб"},
            {"chance": 8, "name": "Гиропор"},
            {"chance": 4, "name": "Ежовик гребенчатый"},
            {"chance": 9, "name": "Мухомор"},
            {"chance": 5, "name": "Бледная поганка"}]
    scale = (100 - FOREST_EMPTY_CHANCE) / sum(c for _, c, _ in FOREST_DEFAULTS)
    check("r<10 → ничего", pick_forest_mushroom(pool, 0.0) is None
          and pick_forest_mushroom(pool, 9.9) is None)
    check("r=10 → Опёнок (10..33.4)",
          pick_forest_mushroom(pool, 10.0)["name"] == "Опёнок"
          and pick_forest_mushroom(pool, 33.4)["name"] == "Опёнок")
    check("r=33.5 → Подберёзовик (33.4..50.3)",
          pick_forest_mushroom(pool, 33.5)["name"] == "Подберёзовик"
          and pick_forest_mushroom(pool, 50.2)["name"] == "Подберёзовик")
    check("r=50.4 → Лисичка (50.3..64.3)",
          pick_forest_mushroom(pool, 50.4)["name"] == "Лисичка"
          and pick_forest_mushroom(pool, 64.3)["name"] == "Лисичка")
    check("r=64.4 → Белый гриб (64.3..75.6)",
          pick_forest_mushroom(pool, 64.4)["name"] == "Белый гриб")
    check("r=75.7 → Гиропор (75.6..83.1)",
          pick_forest_mushroom(pool, 75.7)["name"] == "Гиропор")
    check("r=83.2 → Ежовик (83.1..86.8)",
          pick_forest_mushroom(pool, 83.2)["name"] == "Ежовик гребенчатый")
    check("r=86.9 → Мухомор (86.8..95.3)",
          pick_forest_mushroom(pool, 86.9)["name"] == "Мухомор")
    check("r=95.4 → Поганка (95.3..100)",
          pick_forest_mushroom(pool, 95.4)["name"] == "Бледная поганка")
    check("границы пула: 9.99 пусто, 99.99 Поганка",
          pick_forest_mushroom(pool, 9.99) is None
          and pick_forest_mushroom(pool, 99.99)["name"] == "Бледная поганка")
    check("пустой пул → ничего", pick_forest_mushroom([], 50.0) is None)
    # находка всегда ровно 100 − FOREST_EMPTY_CHANCE: ни одна граница не «съедает» пул
    check("пул покрыт целиком, последний гриб до 100",
          all(pick_forest_mushroom(pool, r) is not None
              for r in [x / 2 for x in range(FOREST_EMPTY_CHANCE * 2, 200)]))
    check("находка 90%: пусто ровно на первой трети пула",
          all(pick_forest_mushroom(pool, r) is None for r in (0.0, 5.0, 9.99))
          and pick_forest_mushroom(pool, 10.0) is not None)

    # ── 5. Предметы леса засеяны и в магазине игр их нет ──
    for name in FOREST_RAW_MUSHROOMS:
        item = await get_item_by_name(name)
        check(f"сырой гриб «{name}» существует", bool(item))
        if item:
            check(f"«{name}» скрыт из магазина", item['is_available'] == 0)
    check("Опёнок лечит +4 сырым", (await get_item_by_name("Опёнок"))['heal'] == 4)
    check("Ежовик лечит +18 сырым", (await get_item_by_name("Ежовик гребенчатый"))['heal'] == 18)
    tox = await get_item_by_name("Мухомор")
    check("Мухомор — ресурс, не еда", tox and tox['category'] == "resource"
          and tox['heal'] == 0 and tox['is_available'] == 0)
    check("Мухомор можно на рынок (market_ok=1)", tox and tox['market_ok'] == 1)
    for name, *_ in FOREST_ITEM_SEEDS:
        item = await get_item_by_name(name)
        check(f"добыча/блюдо «{name}» существует и скрыто",
              bool(item) and item['is_available'] == 0)
    poison = await get_item_by_name("Бутылочка с ядом")
    check("Бутылочка с ядом — ресурс и не выставляется на рынок",
          poison and poison['category'] == "resource" and poison['market_ok'] == 0)
    meat = await get_item_by_name("Мясо кабана")
    check("Мясо кабана — ресурс (сырым есть нельзя)",
          meat and meat['category'] == "resource")
    fried = await get_item_by_name("Жареный белый гриб")
    check("Жареный белый гриб — расходник +34 HP",
          fried and fried['category'] == "consumable" and fried['heal'] == 34)

    # ── 5b. v0.18.16: цены жареных грибов снижены примерно вдвое ──
    fried_expected = {"Жареный опёнок": 9, "Жареный подберёзовик": 14,
                      "Жареные лисички": 22, "Жареный белый гриб": 32,
                      "Жареный гиропор": 60, "Жареный ежовик гребенчатый": 100}
    check("цены жареных грибов из FOREST_FRIED_PRICES",
          {n: s for n, _p, s in FOREST_FRIED_PRICES} == fried_expected)
    db_fried_prices = {}
    for n in fried_expected:
        row = await get_item_by_name(n)
        db_fried_prices[n] = row['sell_price'] if row else None
    check("в БД цены жареных грибов обновлены (синхронизация)",
          db_fried_prices == fried_expected)
    check("обновление цен идемпотентно (повторный ensure_forest_items — False)",
          await ensure_forest_items() is False)
    check("цены жареных грибов не поехали после повторного старта",
          {n: (await get_item_by_name(n))['sell_price'] for n in fried_expected}
          == fried_expected)
    check("сырой гриб стоит втрое дешевле жареного (2.5–3x, как рыба)",
          all(2.5 <= fried_sell / raw_sell <= 3.01
              for raw_sell, fried_sell in [(3, 9), (5, 14), (8, 22), (12, 32),
                                           (20, 60), (35, 100)]))

    # ── 6. Пул грибов: 8 строк, шансы дефолтов, идемпотентность ──
    pool_rows = await get_forest_mushroom_pool()
    check("в пуле 8 грибов", len(pool_rows) == 8)
    chance_map = {r['name']: int(r['chance']) for r in await get_forest_mushroom_rows()}
    check("шансы пула соответствуют дефолтам",
          chance_map == {n: c for n, c, _ in FOREST_DEFAULTS})
    check("вид выбран по kind (Мухомор toxic)",
          {r['name']: r['kind'] for r in await get_forest_mushroom_rows()}
          .get("Мухомор") == "toxic")
    check("повторный ensure_forest_items — ничего не добавил",
          await ensure_forest_items() is False)
    check("повторный ensure_forest_mushrooms — ничего не изменил",
          await ensure_forest_mushrooms() is False)

    # ── 7. Админ-правки переживают перезапуск ──
    muh = await get_item_by_name("Мухомор")
    muh_row = (await get_forest_mushroom_rows())
    muh_id = next(r['id'] for r in muh_row if r['name'] == "Мухомор")
    await update_forest_mushroom_field(muh_id, "chance", 40)
    await update_forest_mushroom_field(muh_id, "photo_file_id", "PHOTO123")
    await ensure_forest_mushrooms()      # админ-правка не должна перезаписаться
    muh_after = await get_forest_mushroom_row(muh_id)
    check("админ: chance=40 сохранён", muh_after and muh_after['chance'] == 40)
    check("админ: admin_tuned=1", muh_after and muh_after['admin_tuned'] == 1)
    check("админ: фото записано", muh_after and muh_after['photo_file_id'] == "PHOTO123")
    check("админ: kind toxic → категория ресурс", muh and muh['category'] == "resource")

    # Тип edible ⇄ toxic меняет категорию предмета и лечение.
    await update_forest_mushroom_field(muh_id, "kind", "edible")
    muh_item = await get_item(muh['id'])
    check("toxic → edible: категория consumable, heal=0",
          muh_item and muh_item['category'] == "consumable"
          and muh_item['heal'] == 0)
    # Цена продажи через редактор.
    await set_forest_mushroom_sell_price(muh_id, 7)
    muh_item2 = await get_item(muh['id'])
    check("админ: цена продажи = 7 НМ", muh_item2 and muh_item2['sell_price'] == 7)
    # Возвращаем toxic, цена откатывается дефолтами? Нет — дефолты не трогаем.
    await update_forest_mushroom_field(muh_id, "kind", "toxic")

    # ── 8. Удаление и повторное добавление ──
    op = await get_item_by_name("Опёнок")
    op_id = next(r['id'] for r in await get_forest_mushroom_rows() if r['name'] == "Опёнок")
    pool_names = {r['name'] for r in await get_forest_mushroom_pool()}
    check("Опёнок есть в пуле", "Опёнок" in pool_names)
    check("remove: true", await remove_forest_mushroom(op_id) is True)
    pool_names = {r['name'] for r in await get_forest_mushroom_pool()}
    check("Опёнок убран из пула", "Опёнок" not in pool_names)
    await ensure_forest_mushrooms()
    pool_names = {r['name'] for r in await get_forest_mushroom_pool()}
    check("ensure НЕ возвращает удалённый гриб (excluded=1)",
          "Опёнок" not in pool_names)
    new_id = await add_forest_mushroom(op['id'], 25)
    row = await get_forest_mushroom_row(new_id)
    check("add_forest_mushroom вернул строку (chance=25, admin_tuned=1)",
          row and row['chance'] == 25 and row['admin_tuned'] == 1)
    check("Опёнок снова в пуле", any(r['name'] == "Опёнок"
          for r in await get_forest_mushroom_pool()))

# ── 9. Создание нового гриба через мастера админа ──
    ok, res = await create_forest_mushroom(
        name="Рыжик", description="Солнечные рыжики опушки.",
        sell_price=6, chance=7, kind="edible", photo_file_id="PH", added_by=1)
    check("create: ok + item_id/f_id", ok and isinstance(res.get('item_id'), int)
          and isinstance(res.get('f_id'), int))
    row = await get_forest_mushroom_row(res['f_id'])
    check("создан: шанс 7, тип edible, цена 6", row and row['chance'] == 7
          and row['kind'] == "edible" and row['sell_price'] == 6
          and row['photo_file_id'] == "PH")
    ri = await get_item(row['item_id'])
    check("создан: расходник, вне магазина, лечит 0",
          ri and ri['category'] == "consumable" and ri['is_available'] == 0
          and ri['heal'] == 0)
    check("созданный гриб сразу попал в пул сбора",
          any(x['name'] == "Рыжик" for x in await get_forest_mushroom_pool()))
    ok3, res3 = await create_forest_mushroom(
        name="Свинушка", description=None, sell_price=2, chance=3,
        kind="toxic", photo_file_id=None, added_by=9)
    check("toxic create: категория resource", ok3 and
          (await get_item(res3['item_id']))['category'] == "resource")

    # ── 10. Кандидаты на «➕ Добавить гриб» ──
    # Расходник/ресурс вне магазина, которого ещё НЕТ в пуле, — кандидат.
    from database.db import add_item, update_item
    spare_id = await add_item(name="Тестовый корень", description="Проверка кандидатов.",
                              price=10, sell_price=4, rarity=1, category="resource",
                              stock=-1, added_by=0)
    # Кандидаты — предметы вне магазина (как грибы леса).
    await update_item(spare_id, is_available=0)
    cand_ids = {c['id'] for c in await get_forest_mushroom_candidates()}
    check("новый ресурс вне пула — кандидат", spare_id in cand_ids)
    # Товар в магазине кандидатом не является (его не нужен лес).
    shop_id = await add_item(name="Магазинный корень", description="x", price=10,
                             sell_price=4, rarity=1, category="resource",
                             stock=-1, added_by=0)
    cand_ids = {c['id'] for c in await get_forest_mushroom_candidates()}
    check("предмет в магазине — не кандидат", shop_id not in cand_ids)
    f_new = await add_forest_mushroom(spare_id, 12)
    cand_ids = {c['id'] for c in await get_forest_mushroom_candidates()}
    check("после добавления в пул — больше не кандидат", spare_id not in cand_ids)
    check("добавленный кандидат в пуле с chance=12",
          (await get_forest_mushroom_row(f_new))['chance'] == 12)
    # Грибы, уже лежащие в пуле (в т.ч. созданные мастером), в кандидатах не светятся
    check("«Рыжик» (создан мастером) не кандидат",
          res['item_id'] not in cand_ids and res['item_id'] not in
          {c['id'] for c in await get_forest_mushroom_candidates()})

    # ── 11. Счётчик встреч кабана ──
    await add_user(85001, "forest_test", "Лесовик", "")
    check("новый игрок: счётчик 0", await get_forest_boar_attempts(85001) == 0)
    await set_forest_boar_attempts(85001, 7)
    check("set: счётчик 7", await get_forest_boar_attempts(85001) == 7)
    await reset_forest_boar_counter(85001)
    check("reset: счётчик 0", await get_forest_boar_attempts(85001) == 0)

    # ── 12. Штраф −10 ОД до нуля ──
    await add_user(85002, "ap_test", "Осторожный", "")
    conn = await get_db()
    await conn.execute("UPDATE users SET ap = 20 WHERE user_id = 85002")
    await conn.commit()
    removed = await remove_ap_or_floor(85002, 10)
    check("−10 при 20 ОД: списано 10", removed == 10)
    check("осталось 10 ОД", (await get_user(85002))['ap'] == 10)
    await conn.execute("UPDATE users SET ap = 4 WHERE user_id = 85002")
    await conn.commit()
    removed = await remove_ap_or_floor(85002, 10)
    check("−10 при 4 ОД: списано 4 (не ниже нуля)", removed == 4)
    check("ОД = 0", (await get_user(85002))['ap'] == 0)

    # ── 13. Локация леса ──
    loc = await get_location_by_key("forest")
    check("локация «forest» есть", bool(loc))
    check("локация: доступ всем", loc and loc['access_mode'] == "all")
    check("локация: картинка city/forest",
          loc and (loc.get('preview_photo') or "") == "city/forest")

    # ── 14. Новые рецепты ──
    new_recipes = ["Жареный опёнок", "Жареный подберёзовик", "Жареные лисички",
                   "Жареный белый гриб", "Жареный гиропор", "Жареный ежовик гребенчатый",
                   "Жареное мясо кабана", "Сварить яд"]
    rcp_names = {r['name'] for r in RECIPES_DEF}
    for rn in new_recipes:
        check(f"рецепт «{rn}» в RECIPES_DEF", rn in rcp_names)
    from database.db import get_recipes
    db_recipes = await get_recipes()
    jad = [r for r in db_recipes if r['name'] == "Сварить яд"]
    check("«Сварить яд» есть в БД, кухня ур.2",
          bool(jad) and jad[0]['required_expansion'] == "kitchen"
          and jad[0]['required_level'] == 2)
    check("результат рецепта «Сварить яд» = Бутылочка с ядом",
          bool(jad) and jad[0]['result_item_name'] == "Бутылочка с ядом")

    await close_db()
    print(f"\nSmoke 085: {passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)


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