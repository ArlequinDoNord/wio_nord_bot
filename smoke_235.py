# -*- coding: utf-8 -*-
"""Smoke 235 — паки руды на рынке (market_items.qty).

- старые лоты (без количества) — qty = 1;
- пак руды сохраняется с количеством и ценой за весь лот;
- размеры паков задаются в config.MARKET_PACK_SIZES (руда = 5).

Прогон: .\\.venv\\Scripts\\python.exe smoke_235.py
"""
import asyncio
import os
import sys

_TEST_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_test_smoke235.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

passed = failed = 0


def check(name, cond):
    global passed, failed
    if cond:
        passed += 1
        print(f"  OK  {name}")
    else:
        failed += 1
        print(f"  FAIL: {name}")


async def run():
    from config import MARKET_PACK_SIZES, MINE_ORE_NAME
    from database.db import (init_db, close_db, add_user, get_item_by_name,
                             place_item_offer, get_item_offer, get_item_offers, remove_item_offer)

    from database.db import ensure_mine_items
    await init_db()
    try:
        await ensure_mine_items()
        await add_user(901, "seller", "Seller", "")
        ore = await get_item_by_name(MINE_ORE_NAME)
        check("руда есть в каталоге предметов", ore is not None)
        check("руда продаётся паком по 5", MARKET_PACK_SIZES.get(MINE_ORE_NAME) == 5)

        print("\n1. Одиночный лот (старый путь)")
        single = await place_item_offer(901, ore["id"], 100)
        check("qty по умолчанию = 1", (await get_item_offer(single))["qty"] == 1)

        print("\n2. Пак руды: 5 единиц, цена за весь пак")
        pack = await place_item_offer(901, ore["id"], 575, qty=5)
        row = await get_item_offer(pack)
        check("в лоте 5 единиц", row["qty"] == 5)
        check("цена за пак сохранена", row["price"] == 575)
        listed = {r["id"]: r["qty"] for r in await get_item_offers()}
        check("в списке рынка виден пак с количеством", listed.get(pack) == 5)

        print("\n3. Снятие пака")
        check("пак снимается", await remove_item_offer(pack) is True)
        await remove_item_offer(single)
    finally:
        await close_db()


if __name__ == "__main__":
    asyncio.run(run())
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
