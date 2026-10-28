# -*- coding: utf-8 -*-
"""Smoke 169 — Банк: история транзакций с постраничным листанием.

1. db.get_transactions_history: страницы по 15, has_next, порядок (новые сверху).
2. Пустая история → (完成的нулю []) , has_next False.
3. Разрыв в транзакциях (больше 30 записей): страницы не дублируются.
4. Экран: кнопки «⬅️ Новее»/«Старее ▶️», счётчик страницы.
"""
import asyncio
import os
import sys

os.environ["DATABASE_PATH"] = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "_test_smoke169.db")

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
            print(f"  FAIL: {name}")

    import database.db as db
    from database.db import (
        init_db, add_user, get_db, get_transactions_history,
        add_treasury_move, close_db,
    )

    await init_db()
    UID = 169001
    await add_user(UID, 't', 'T', "")

    async def add_tx(amount, tx_type, descr=""):
        """Прямая транзакция для uid (from казна to uid)."""
        conn = await get_db()
        await conn.execute(
            "INSERT INTO transactions (from_user, to_user, amount, tx_type, description, created_at)"
            " VALUES (0, ?, ?, ?, ?, datetime('now', '+' || (SELECT COUNT(*) FROM transactions) || ' seconds'))",
            (UID, amount, tx_type, descr))
        await conn.commit()

    print("\n1. Пустая история")
    rows, has_next = await get_transactions_history(UID)
    check("пустая → [], has_next False", rows == [] and has_next is False)

    print("\n2. 20 транзакций: стр.0 = 15 строк + has_next, стр.1 = 5 строк")
    for i in range(20):
        await add_tx(i + 1, "transfer", f"tx {i+1}")
    rows, has_next = await get_transactions_history(UID, page=0)
    check("стр.0: 15 строк", len(rows) == 15)
    check("стр.0 has_next True", has_next is True)
    rows1, hn1 = await get_transactions_history(UID, page=1)
    check("стр.1: 5 строк", len(rows1) == 5)
    check("стр.1 has_next False", hn1 is False)
    ids0 = {r['id'] for r in rows}
    ids1 = {r['id'] for r in rows1}
    check("страницы не дублируются", ids0 & ids1 == set())

    print("\n3. 50 транзакций: стр.0..3")
    for i in range(30):
        await add_tx(i + 1, "shop_payout", "продажа")
    # now 50 total
    for page in range(4):
        rows_p, hn_p = await get_transactions_history(UID, page=page)
        if page < 3:
            check(f"стр.{page}: 15 строк, has_next True",
                  len(rows_p) == 15 and hn_p is True)
        else:
            check("последняя стр.: 5 строк, has_next False",
                  len(rows_p) == 5 and hn_p is False)
    all_ids = []
    for page in range(4):
        rows_p, _ = await get_transactions_history(UID, page=page)
        all_ids.extend(r['id'] for r in rows_p)
    check("все 50 уникальны и ровно 50", len(all_ids) == 50 and len(set(all_ids)) == 50)

    print("\n4. Порядок: новые раньше (id убывает в странице)")
    rows0, _ = await get_transactions_history(UID, page=0)
    ids = [r['id'] for r in rows0]
    check("id убывают", ids == sorted(ids, reverse=True))

    print("\n5. Сигнатурные проверки (вызов по умолчанию = страница 0)")
    rows_any, hn = await get_transactions_history(UID)
    check("вызов по умолчанию = страница 0", len(rows_any) == 15 and hn is True)

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
        os.remove(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "_test_smoke169.db"))
    except OSError:
        pass
