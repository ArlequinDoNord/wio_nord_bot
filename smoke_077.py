"""Smoke v0.15.15: суточная выплата отчётов не теряется при рестарте.

Регрессия на баг: строка миграции в init_db выполнялась при КАЖДОМ старте бота
(`UPDATE reports SET paid = 1 WHERE status = 'approved'`), помечая одобренные,
но ещё не выплаченные отчёты как оплаченные до суточной payout_reports — выплата
терялась навсегда (без начисления и транзакции).

Проверяет:
1. После approve_report отчёт имеет paid=0.
2. Повторный init_db() (симуляция рестарта) НЕ трогает paid одобренного отчёта.
3. payout_reports() начисляет войска и нордмарки с налогом и ставит paid=1.
4. Казна получает налог, создаётся транзакция report.

Запуск: .venv\\Scripts\\python.exe smoke_077.py
"""
import asyncio
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke077.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB

sys.path.insert(0, os.path.dirname(__file__))


async def run():
    from database.db import (
        init_db, close_db, add_user, add_report, approve_report,
        pay_salaries, get_treasury_balance, get_db,
    )

    await init_db()
    U = 753001
    await add_user(U, "u753001", "Т1-отчётник", "")

    passed = 0
    failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
        else:
            failed += 1
            print(f"  FAIL: {name}")

    rid, credited = await add_report(U, "shot", 500, 500, "test")
    check("add_report: credited 500", credited == 500)
    paid = await approve_report(rid, 0, 500)
    check("approve_report: возвращает credited", paid == 500)

    state = await _report_state(rid)
    check("после одобрения paid=0 (ждёт суточной выплаты)", state['paid'] == 0
          and state['status'] == 'approved')

    # СИМУЛЯЦИЯ РЕСТАРТА БОТА — init_db инициализируется при каждом старте.
    await init_db()

    state = await _report_state(rid)
    check("рестарт НЕ помечает отчёт оплаченным (был баг)", state['paid'] == 0)

    bal_before = await get_treasury_balance()
    res = await pay_salaries()  # НЕ платит отчёты — это другой цикл
    from database.db import payout_reports
    payouts = await payout_reports()

    state = await _report_state(rid)
    check("payout_reports начислил и paid=1", state['paid'] == 1)
    check("выплата: 500 войск", payouts and payouts[0]['troops'] == 500)
    # налог 15% от 500 = 75 → на руки 425
    check("выплата: нордмарки 425 (налог 75)", payouts and payouts[0]['nordmarks'] == 425
          and payouts[0]['tax'] == 75)
    check("казна получила налог 75", (await get_treasury_balance()) - bal_before == 75)

    conn = await get_db()
    cur = await conn.execute("SELECT COUNT(*) AS n FROM transactions WHERE tx_type='report' AND to_user=?", (U,))
    check("создана транзакция report", (await cur.fetchone())['n'] == 1)
    cur = await conn.execute("SELECT troops, nordmarks FROM users WHERE user_id=?", (U,))
    u = await cur.fetchone()
    check("балансы игрока начислены", u['troops'] == 500 and u['nordmarks'] >= 425)

    await close_db()
    print(f"\nSmoke 077: {passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)


async def _report_state(rid):
    from database.db import get_db
    conn = await get_db()
    cur = await conn.execute("SELECT status, paid, credited_troops FROM reports WHERE id = ?", (rid,))
    row = await cur.fetchone()
    return dict(row) if row else {}


if __name__ == "__main__":
    try:
        asyncio.run(run())
    except SystemExit:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        from database.db import close_db
        asyncio.run(close_db())
        print(f"SMOKE ERROR: {e!r}")
        sys.exit(1)