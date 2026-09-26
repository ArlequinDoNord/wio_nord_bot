"""Smoke v0.15.33: супер-админ может поправить цифры отчёта («за сутки»/«всего») перед приёмом.

Зачем: пилоты путают поля и вписывают «всё накопленное» в «за сутки» — такая заявка
искажает статистику. Правка применяется только к отчёту в очереди (pending), сумма к
выдаче пересчитывается по общему правилу (прирост «всего» от базы прошлых дней), и уже
затем отчёт можно принять.

Запуск: .venv\\Scripts\\python.exe smoke_090.py
"""
import asyncio
import os
import sys

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke090.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB

sys.path.insert(0, os.path.dirname(__file__))


async def _yesterday_report(uid, daily, total, status="approved", credited=None):
    from database.db import get_db
    conn = await get_db()
    await conn.execute(
        "INSERT INTO reports (user_id, screenshot_file_id, troops_reported, total_troops, "
        "region, credited_troops, status, paid, created_at) "
        "VALUES (?, 'f', ?, ?, '0', ?, ?, 1, datetime('now', '-1 day'))",
        (uid, daily, total, credited, status))
    await conn.commit()


async def _row(report_id):
    from database.db import get_db
    conn = await get_db()
    cur = await conn.execute(
        "SELECT troops_reported, total_troops, credited_troops, status FROM reports WHERE id = ?",
        (report_id,))
    return await cur.fetchone()


async def run():
    from database.db import (
        init_db, close_db, add_user, add_report, approve_report, correct_report_numbers,
        payout_reports, get_pending_reports, get_db, get_user,
    )

    await init_db()
    passed = 0
    failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
        else:
            failed += 1
            print(f"  FAIL: {name}")

    SUPER = 60001
    await add_user(SUPER, "super", "Супер", "Админ")

    # ── 1. Правка завышенной заявки по пилоту с историей ──
    U = 61001
    await add_user(U, "fix01", "Пилот", "Один")
    await _yesterday_report(U, 400, 400)            # вчера накоплено 400
    rid, credited = await add_report(U, "f", 782, 782, "0")   # пилот вписал 782 и туда, и туда
    check("до правки к выдаче прирост 382", credited == 382)

    ctx = await correct_report_numbers(rid, 100, 600, SUPER)  # супер-админ исправил
    check("после правки пересчёт по новым цифрам", ctx['payable'] == 100 and ctx['growth'] == 200)
    row = await _row(rid)
    check("в БД записаны исправленные цифры", (row['troops_reported'], row['total_troops']) == (100, 600))
    check("credited_troops = пересчитанная сумма", row['credited_troops'] == 100)
    check("отчёт всё ещё в очереди (не одобрен)", row['status'] == 'pending')
    check("отчёт виден в очереди на проверку", any(r['id'] == rid for r in await get_pending_reports()))

    # Приём после правки платит ИСПРАВЛЕННУЮ сумму
    amount = await approve_report(rid, SUPER)
    check("приём платит исправленную сумму (100)", amount == 100)
    check("статистика видит исправленные числа", (await _row(rid))['troops_reported'] == 100)

    # ── 2. Правка первого отчёта (базы нет) ──
    U2 = 61002
    await add_user(U2, "fix02", "Пилот", "Два")
    rid2, c2 = await add_report(U2, "f", 5000, 5000, "0")
    ctx2 = await correct_report_numbers(rid2, 250, 5000, SUPER)
    check("первый отчёт: к выдаче по исправленной сумме", ctx2['payable'] == 250)
    check("первый отчёт: base_known = False", ctx2['base_known'] is False)
    check("приём первого отчёта платит 250", await approve_report(rid2, SUPER) == 250)

    # ── 3. Правка невозможна вне очереди ──
    r_appr = await _row(rid2)
    check("одобренный отчёт: статус approved", r_appr['status'] == 'approved')
    err = await correct_report_numbers(rid2, 1, 1, SUPER)
    check("одобренный отчёт править нельзя", 'error' in err)
    check("одобренный отчёт не изменился", (await _row(rid2))['credited_troops'] == 250)

    U3 = 61003
    await add_user(U3, "fix03", "Пилот", "Три")
    rid3, _ = await add_report(U3, "f", 100, 100, "0")
    from database.db import reject_report
    await reject_report(rid3, SUPER)
    err3 = await correct_report_numbers(rid3, 50, 50, SUPER)
    check("отклонённый отчёт править нельзя", 'error' in err3)

    err4 = await correct_report_numbers(999999, 10, 10, SUPER)
    check("несуществующий отчёт → ошибка", 'error' in err4)

    # ── 4. Правка «всего» вниз обнуляет выплату, если прироста нет ──
    U4 = 61004
    await add_user(U4, "fix04", "Пилот", "Четыре")
    await _yesterday_report(U4, 100, 1000)
    rid4, c4 = await add_report(U4, "f", 300, 1200, "1")     # прирост 200 → к выдаче 200
    check("до правки к выдаче 200", c4 == 200)
    ctx4 = await correct_report_numbers(rid4, 300, 1000, SUPER)   # «всего» не выросло
    check("«всего» не выросло → прирост 0", ctx4['growth'] == 0 and ctx4['payable'] == 0)
    check("приём даёт 0, лишнего не платится", await approve_report(rid4, SUPER) == 0)

    # ── 5. Выплата после правки не завышает баланс ──
    await payout_reports()
    u1 = await get_user(U)
    check("баланс пилота = выплаченному (100)", u1['troops'] == 100)

    await close_db()
    print(f"\nSmoke 090: {passed} passed, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    async def _main():
        try:
            return await run()
        finally:
            from database.db import close_db
            await close_db()

    sys.exit(asyncio.run(_main()))
