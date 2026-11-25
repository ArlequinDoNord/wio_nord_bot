"""Smoke v0.43.33: одна штука каждого вида рыбы в сутки продаётся сверх лимита казны.

Проверяет (жареная рыба, _fried_fish_cap; сырая — учёт по виду в БД):
1. Лимит исчерпан (500): первый вид продаётся 1 штуку, второй раз тот же вид — нет.
2. Другой вид в тот же день тоже проходит 1 штуку (правило по видам, а не по дню).
3. Учёт по виду сбрасывается на новые сутки (день в ключе).
4. Внутри лимита вид учитывается как обычная продажа.

Запуск: .venv\\Scripts\\python.exe smoke_248.py
"""
import asyncio
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke248.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB
os.environ["ADMIN_IDS"] = "448001"

sys.path.insert(0, os.path.dirname(__file__))

P = 884001


async def run():
    from database.db import (init_db, close_db, add_user, add_item, get_item_by_name,
                             add_fish_sale_amount, mark_fish_kind_sold, fish_kind_sold_today)
    from bot.handlers.inventory import _fried_fish_cap
    from config import FISH_TREASURY_DAILY_LIMIT

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
        await add_user(P, "kinds1", "Пилот", "Один")
        await add_item(name="Жареный форель", description="тест", price=1066, sell_price=533,
                       rarity=4, category="consumable", stock=-1, added_by=0,
                       ap_cost=0, damage=0, heal=140)
        await add_item(name="Жареный сом", description="тест", price=320, sell_price=160,
                       rarity=2, category="consumable", stock=-1, added_by=0,
                       ap_cost=0, damage=0, heal=65)
        forel = await get_item_by_name("Жареный форель")
        som = await get_item_by_name("Жареный сом")

        # 1. Лимит исчерпан
        await add_fish_sale_amount(P, FISH_TREASURY_DAILY_LIMIT)
        qty, _, err = await _fried_fish_cap(P, forel, 3)
        check("лимит исчерпан: форель продаётся 1 шт.", qty == 1 and err == "")
        await mark_fish_kind_sold(P, forel['id'], 1)
        qty, _, err = await _fried_fish_cap(P, forel, 1)
        check("вторая форель в тот же день — отказ", qty == 0 and err != "")

        # 2. Другой вид — своя штука
        qty, _, err = await _fried_fish_cap(P, som, 2)
        check("другой вид (сом) — 1 шт. сверх лимита", qty == 1 and err == "")
        await mark_fish_kind_sold(P, som['id'], 1)
        check("учёт вида: сом отмечен", await fish_kind_sold_today(P, som['id']))

        # 3. Учёт по дню: в другие сутки вид снова свободен
        from database import db as _db
        original = _db.fish_sold_day_key
        _db.fish_sold_day_key = lambda: "2099-01-01"
        try:
            check("на новые сутки форель снова не продана", not await fish_kind_sold_today(P, forel['id']))
        finally:
            _db.fish_sold_day_key = original

        # 4. Внутри лимита — обычная продажа
        P2 = P + 1
        await add_user(P2, "kinds2", "Пилот", "Два")
        qty, note, err = await _fried_fish_cap(P2, som, 2)
        check("внутри лимита: 2 шт. без примечания", qty == 2 and note == "" and err == "")
    finally:
        await close_db()
        if os.path.exists(_TEST_DB):
            os.remove(_TEST_DB)

    print(f"\nSmoke 248: {passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)


asyncio.run(run())
