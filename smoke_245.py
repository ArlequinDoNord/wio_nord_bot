"""Smoke v0.43.30: жареная рыба на треть дороже сырой, общий лимит казны 500 НМ;
протухшая рыба превращается в один предмет «Испорченная еда».

Проверяет:
1. Миграция _migrate_fried_fish_prices переводит старую цену жареного сома (260) в 160
   и идемпотентна; чужую цену (админскую) не трогает.
2. Лимит казны на рыбу FISH_TREASURY_DAILY_LIMIT = 500, жареная рыба в FRIED_FISH_NAMES.
3. Остаток лимита учитывает и сырую, и жареную рыбу (общий счётчик).
4. _fried_fish_cap режет количество по остатку и отказывает при исчерпании.
5. Протухшая сырая рыба → одна «Испорченная еда» за каждую штуку; цена испорченной 3 НМ.

Запуск: .venv\\Scripts\\python.exe smoke_245.py
"""
import asyncio
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke245.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB
os.environ["ADMIN_IDS"] = "445001"

sys.path.insert(0, os.path.dirname(__file__))

PILOT, PILOT2, PILOT3 = 882001, 882002, 882003


async def run():
    from database.db import (init_db, close_db, get_db, add_user, add_item, get_item_by_name,
                             fish_treasury_left, add_fish_sale_amount, _migrate_fried_fish_prices)
    from config import FISH_TREASURY_DAILY_LIMIT, FRIED_FISH_NAMES
    from bot.handlers.inventory import _fried_fish_cap

    await init_db()
    passed = failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
        else:
            failed += 1
            print(f"  FAIL: {name}")

    try:
        conn = await get_db()
        await add_user(PILOT, "fry1", "Пилот", "Один")
        await add_user(PILOT2, "fry2", "Пилот", "Два")
        await add_item(name="Жареный сом", description="тест", price=520, sell_price=260,
                       rarity=2, category="consumable", stock=-1, added_by=0,
                       ap_cost=0, damage=0, heal=65)
        await add_item(name="Жареный угорь", description="тест", price=850, sell_price=425,
                       rarity=3, category="consumable", stock=-1, added_by=0,
                       ap_cost=0, damage=0, heal=90)

        # 1. Миграция цены
        await conn.execute("UPDATE items SET sell_price = 260 WHERE name = 'Жареный сом'")
        await conn.execute("UPDATE items SET sell_price = 999 WHERE name = 'Жареный угорь'")
        await conn.commit()
        await _migrate_fried_fish_prices()
        som = await get_item_by_name("Жареный сом")
        check("сом: 260 → 160", som['sell_price'] == 160)
        ugor = await get_item_by_name("Жареный угорь")
        check("админская цена угря не тронута", ugor['sell_price'] == 999)
        await _migrate_fried_fish_prices()
        som = await get_item_by_name("Жареный сом")
        check("миграция идемпотентна", som['sell_price'] == 160)

        # 2. Константы
        check("лимит казны на рыбу = 500", FISH_TREASURY_DAILY_LIMIT == 500)
        check("жареный сом в FRIED_FISH_NAMES", "Жареный сом" in FRIED_FISH_NAMES)
        check("сырой сом не в FRIED_FISH_NAMES", "Мерцающий сом" not in FRIED_FISH_NAMES)

        # 3. Общий счётчик: сырая рыба уже выручила 490 НМ
        check("новый игрок: остаток 500", await fish_treasury_left(PILOT2) == 500)
        await add_fish_sale_amount(PILOT, 490)
        check("после 490 НМ остаток 10", await fish_treasury_left(PILOT) == 10)

        # 4. Отказ, когда остатка не хватает даже на одну штуку
        qty, note, err = await _fried_fish_cap(PILOT, som, 3)
        check("на 1 шт. не хватает — ошибка", qty == 0 and err != "")

        # 4б. Режем количество по остатку
        qty, note, err = await _fried_fish_cap(PILOT2, som, 10)
        check("новый игрок: 10 шт. режутся до 3 (500 // 160)", qty == 3 and note != "" and err == "")
        qty, note, err = await _fried_fish_cap(PILOT2, som, 2)
        check("2 шт. проходят без примечания", qty == 2 and note == "" and err == "")

        # 4в. Исчерпанный лимит
        await add_fish_sale_amount(PILOT2, 500)
        qty, note, err = await _fried_fish_cap(PILOT2, som, 1)
        check("исчерпанный лимит — ошибка", qty == 0 and "исчерпан" in err)

        # 4г. Первая штука за день продаётся, даже если дороже лимита (форель 600 при лимите 500)
        await add_item(name="Жареный форель", description="тест", price=1066, sell_price=533,
                       rarity=4, category="consumable", stock=-1, added_by=0,
                       ap_cost=0, damage=0, heal=140)
        forel = await get_item_by_name("Жареный форель")
        await add_user(PILOT3, "fry3", "Пилот", "Три")
        qty, note, err = await _fried_fish_cap(PILOT3, forel, 2)
        check("первая форель 600 за день проходит (1 шт.)", qty == 1 and err == "")
        await add_fish_sale_amount(PILOT3, 600)
        qty, note, err = await _fried_fish_cap(PILOT3, forel, 1)
        check("вторая форель за тот же день — отказ", qty == 0 and err != "")

        # 5. Протухшая сырая рыба → «Испорченная еда», по одной штуке на улов
        import time
        from config import FIRE_SPOILED_FOOD_NAME
        from database.db import spoil_expired_catches, add_fish_catch, get_inventory_item
        await add_item(name="Мерцающий сом", description="тест", price=240, sell_price=120,
                       rarity=1, category="fishing", stock=-1, added_by=0,
                       ap_cost=0, damage=0, heal=0)
        await add_item(name=FIRE_SPOILED_FOOD_NAME, description="тест", price=1, sell_price=0,
                       rarity=1, category="consumable", stock=-1, added_by=0,
                       ap_cost=0, damage=0, heal=5)
        from database.db import _migrate_spoiled_food_price
        await _migrate_spoiled_food_price()
        spoiled = await get_item_by_name(FIRE_SPOILED_FOOD_NAME)
        check("испорченная еда: цена 3 НМ", spoiled['sell_price'] == 3)
        fish = await get_item_by_name("Мерцающий сом")
        now = int(time.time())
        await add_fish_catch(PILOT2, fish['id'], 1, kind="fish", expires_at=str(now - 10))
        await add_fish_catch(PILOT2, fish['id'], 1, kind="fish", expires_at=str(now - 5))
        await add_fish_catch(PILOT2, fish['id'], 1, kind="fish", expires_at=str(now + 3600))
        converted = await spoil_expired_catches(PILOT2)
        check("два протухших улова превращены", converted == 2)
        inv = await get_inventory_item(PILOT2, spoiled['id'])
        check("в инвентаре две испорченные еды", inv is not None and inv['quantity'] == 2)
        conn = await get_db()
        left = (await (await conn.execute(
            "SELECT COUNT(*) AS c FROM fish_catches WHERE user_id = ? AND sold_at IS NULL",
            (PILOT2,))).fetchone())['c']
        check("свежий улов остался", left == 1)
    finally:
        await close_db()
        if os.path.exists(_TEST_DB):
            os.remove(_TEST_DB)

    print(f"\nSmoke 245: {passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)


asyncio.run(run())
