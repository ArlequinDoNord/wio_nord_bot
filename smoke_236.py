# -*- coding: utf-8 -*-
"""Smoke 236 — контракты на поставку (utils/market_contracts.py).

Проверяет: расчёт суммы и налога, минимум и лимиты, эскроу, штатное закрытие,
отмену по варианту А (до 5 успешных) и Б (с 5-й), лимит 100 после 5 закрытых
на максимум, истечение срока. Гражданство подставляется в тесте (_is_citizen).

Прогон: .\\.venv\\Scripts\\python.exe smoke_236.py
"""
import asyncio
import os
import sys

_TEST_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_test_smoke236.db")
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
    from database.db import (init_db, close_db, add_user, update_user, get_user, get_db,
                             get_item_by_name, get_inventory_item, add_inventory_item,
                             ensure_mine_items)
    from config import MINE_ORE_NAME
    from utils import market_contracts as MC

    async def _citizen(uid):
        return uid in (1001, 1002, 1003)
    MC._is_citizen = _citizen

    await init_db()
    try:
        await ensure_mine_items()
        buyer, supplier = 1001, 1002
        await add_user(buyer, "buyer", "Buyer", "")
        await add_user(supplier, "supplier", "Supplier", "")
        ore = await get_item_by_name(MINE_ORE_NAME)
        unit_min = int(ore["sell_price"] or 0)
        print(f"  (казённая цена руды в тесте: {unit_min} НМ)")

        print("\n1. Расчёт")
        q = MC.quote(40, 20, 40)
        check("сумма 20×40 = 800", q["total"] == 800)
        check("налог 12% = 96", q["tax"] == 96)
        check("итог заказчику = 896", q["pay"] == 896)

        print("\n2. Ограничения выставления")
        await update_user(buyer, nordmarks=100000)
        ok, msg = await MC.create_contract(buyer, ore["id"], 19, unit_min)
        check("меньше 20 нельзя", ok is False)
        ok, msg = await MC.create_contract(buyer, ore["id"], 51, unit_min)
        check("больше 50 нельзя до разблокировки", ok is False)
        ok, msg = await MC.create_contract(buyer, ore["id"], 20, max(0, unit_min - 1))
        check("цена ниже казённой нельзя", ok is False)
        await update_user(supplier, nordmarks=0)
        ok, msg = await MC.create_contract(supplier, ore["id"], 20, unit_min + 5)
        check("без денег на эскроу выставить нельзя", ok is False)

        print("\n3. Выставление и эскроу")
        await update_user(buyer, nordmarks=10000)
        before = (await get_user(buyer))["nordmarks"]
        ok, cid = await MC.create_contract(buyer, ore["id"], 20, unit_min)
        check("контракт выставлен", ok is True)
        pay = MC.quote(unit_min, 20, unit_min)["pay"]
        after = (await get_user(buyer))["nordmarks"]
        check("с заказчика списано сумма + налог", before - after == pay)
        conn = await get_db()
        cur = await conn.execute("SELECT balance FROM treasury WHERE id = 1")
        treas = (await cur.fetchone())["balance"]
        check("налог поступил в казну", treas >= MC.quote(unit_min, 20, unit_min)["tax"])

        print("\n4. Штатное закрытие")
        sup_before = (await get_user(supplier))["nordmarks"]
        await add_inventory_item(supplier, ore["id"], 20)
        ok, _ = await MC.close_contract(supplier, cid)
        check("исполнитель закрыл контракт", ok is True)
        check("исполнитель получил сумму без налога",
              (await get_user(supplier))["nordmarks"] - sup_before == MC.quote(unit_min, 20, unit_min)["total"])
        inv = await get_inventory_item(buyer, ore["id"])
        check("заказчик получил товар", inv is not None and inv["quantity"] >= 20)

        print("\n5. Отмена по варианту А (до 5 успешных)")
        ok, cid2 = await MC.create_contract(buyer, ore["id"], 20, unit_min)
        b0 = (await get_user(buyer))["nordmarks"]
        ok, refund = await MC.cancel_contract(buyer, cid2)
        check("вариант А: возврат = сумма (налог остаётся)",
              refund == MC.quote(unit_min, 20, unit_min)["total"])
        check("деньги вернулись", (await get_user(buyer))["nordmarks"] - b0 == refund)

        print("\n6. Отмена по варианту Б (с 5-й успешной сделки)")
        conn = await get_db()
        for _ in range(5):
            await conn.execute(
                "INSERT INTO market_contracts (buyer_id, item_id, qty, unit_price, total, tax, status, expires_at) "
                "VALUES (?, ?, 20, ?, ?, ?, 'closed', datetime('now','+1 day'))",
                (buyer, ore["id"], unit_min, 20 * unit_min, 20 * unit_min * 12 // 100))
        await conn.commit()
        ok, cid3 = await MC.create_contract(buyer, ore["id"], 20, unit_min)
        b1 = (await get_user(buyer))["nordmarks"]
        ok, refund = await MC.cancel_contract(buyer, cid3)
        t = MC.quote(unit_min, 20, unit_min)
        check("вариант Б: возврат = сумма + налог − 25% налога",
              refund == t["total"] + t["tax"] - int(t["tax"] * MC.CANCEL_TAX_SHARE))
        check("деньги вернулись по варианту Б", (await get_user(buyer))["nordmarks"] - b1 == refund)

        print("\n7. Лимит 100 после 5 закрытых на максимум")
        check("сейчас лимит 50 (5 закрытых на 50 ещё нет)", await MC.max_qty_for(buyer) == 50)
        for _ in range(5):
            await conn.execute(
                "INSERT INTO market_contracts (buyer_id, item_id, qty, unit_price, total, tax, status, expires_at) "
                "VALUES (?, ?, 50, ?, ?, ?, 'closed', datetime('now','+1 day'))",
                (buyer, ore["id"], unit_min, 50 * unit_min, 50 * unit_min * 12 // 100))
        await conn.commit()
        check("после 5 закрытых на 50 лимит 100", await MC.max_qty_for(buyer) == 100)

        print("\n8. Срок: истёкший контракт возвращает эскроу")
        await update_user(buyer, nordmarks=10000)
        ok, cid4 = await MC.create_contract(buyer, ore["id"], 20, unit_min)
        await conn.execute("UPDATE market_contracts SET expires_at = datetime('now','-1 day') WHERE id = ?",
                           (cid4,))
        await conn.commit()
        n = await MC.expire_contracts()
        check("истёкший контракт снят", n >= 1)
        cur = await conn.execute("SELECT status FROM market_contracts WHERE id = ?", (cid4,))
        check("статус expired", (await cur.fetchone())["status"] == "expired")
    finally:
        await close_db()


if __name__ == "__main__":
    asyncio.run(run())
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
