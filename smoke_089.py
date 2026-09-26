"""Smoke v0.15.32: оплата отчётов — только за те сутки, в которые пилот сдал отчёт.

Правило: к оплате идёт не заявка «сколько заработал за сутки», а прирост счётчика
«всего» относительно прошлых дней, и не больше заявки. Поэтому заявка
«всё накопленное за все дни» в обоих полях не проходит — платится только прирост.
Несколько отчётов за сутки не суммируются (платится максимум), отклонённые отчёты
не поднимают базу, первый отчёт (базы нет) не проходит автоодобрение.

Запуск: .venv\\Scripts\\python.exe smoke_089.py
"""
import asyncio
import os
import sys

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke089.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB

sys.path.insert(0, os.path.dirname(__file__))


async def _yesterday_report(uid, daily, total, status="approved", credited=None):
    """Отчёт «за вчера»: напрямую в БД, чтобы задать базу прошлых дней."""
    from database.db import get_db
    conn = await get_db()
    await conn.execute(
        "INSERT INTO reports (user_id, screenshot_file_id, troops_reported, total_troops, "
        "region, credited_troops, status, paid, created_at) "
        "VALUES (?, 'f', ?, ?, '0', ?, ?, 1, datetime('now', '-1 day'))",
        (uid, daily, total, credited, status))
    await conn.commit()


async def run():
    from database.db import (
        init_db, close_db, add_user, add_report, approve_report, payout_reports,
        report_payout_context, get_user, count_reports_today, get_db,
        get_report_auto_approve_troops, get_region_stats, recompute_region_stats,
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

    U = 51001
    await add_user(U, "rep01", "Репёрт", "Тестов")
    # У второго пилота история есть — для проверки базы
    U2 = 51002
    await add_user(U2, "rep02", "Второй", "Тестов")

    # ── 1. Первый отчёт: базы нет ──
    ctx = await report_payout_context(U, 782, 782)
    check("первый отчёт: база неизвестна", ctx["base_known"] is False and ctx["base"] is None)
    check("первый отчёт: к оплате по заявке", ctx["payable"] == 782)
    rid, credited = await add_report(U, "f", 782, 782, "0")
    check("add_report первого отчёта: credited 782", credited == 782)

    # ── 2. База = максимум «всего» прошлых дней ──
    await _yesterday_report(U2, 900, 14000)
    ctx = await report_payout_context(U2, 15000, 15000)
    check("база взята из прошлых дней (14000)", ctx["base"] == 14000)
    check("прирост = всего − база (1000)", ctx["growth"] == 1000)
    check("заявка «всё накопленное» урезана до прироста", ctx["payable"] == 1000)

    # ── 3. Именно тот случай из жалобы: одно число во всех полях ──
    U3 = 51003
    await add_user(U3, "rep03", "Третий", "")
    await _yesterday_report(U3, 782, 400)      # вчера накоплено 400
    ctx = await report_payout_context(U3, 782, 782)   # сегодня вписал 782 и туда, и туда
    check("жалоба: вписано 782/782 → к оплате только прирост 382", ctx["payable"] == 382)
    check("жалоба: прирост посчитан от базы 400", ctx["growth"] == 382)

    # ── 4. Заявка меньше прироста — платится заявка ──
    ctx = await report_payout_context(U3, 100, 700)
    check("заявка меньше прироста → к оплате заявка", ctx["payable"] == 100)

    # ── 5. «Всего» не выросло — оплаты нет ──
    ctx = await report_payout_context(U3, 500, 400)
    check("прироста нет → к оплате 0", ctx["payable"] == 0 and ctx["growth"] == 0)

    # ── 6. Несколько отчётов за сутки не суммируются ──
    U4 = 51004
    await add_user(U4, "rep04", "Четвёртый", "")
    await _yesterday_report(U4, 100, 1000)
    r1, c1 = await add_report(U4, "f", 100, 1100, "1")   # прирост 100
    r2, c2 = await add_report(U4, "f", 200, 1200, "1")   # прирост 200
    r3, c3 = await add_report(U4, "f", 300, 1300, "1")   # прирост 300
    check("3 отчёта за сутки: 100 + 100 + 100 (итого 300 = максимум)",
          (c1, c2, c3) == (100, 100, 100))
    await approve_report(r1, 0, c1)
    await approve_report(r2, 0, c2)
    await approve_report(r3, 0, c3)
    payouts = await payout_reports()
    paid4 = [p for p in payouts if p['user_id'] == U4]
    check("выплата за сутки = 300, не 600", paid4 and paid4[0]['troops'] == 300)

    # ── 7. Отклонённый отчёт не поднимает базу ──
    U5 = 51005
    await add_user(U5, "rep05", "Пятый", "")
    await _yesterday_report(U5, 999999, 999999, status="rejected", credited=999999)
    ctx = await report_payout_context(U5, 500, 2500)
    check("отклонённый отчёт не в базе (базы нет)", ctx["base_known"] is False)
    check("после отклонённого — оплата по заявке", ctx["payable"] == 500)

    # ── 8. approve_report: пересчёт, частичное одобрение, потолок ──
    U6 = 51006
    await add_user(U6, "rep06", "Шестой", "")
    await _yesterday_report(U6, 100, 1000)
    rid6, credited6 = await add_report(U6, "f", 500, 1300, "2")   # прирост 300 → credited 300
    check("add_report: credited = прирост (300)", credited6 == 300)
    got = await approve_report(rid6, 1, 300)
    check("approve: 300", got == 300)
    # Повторное одобрение того же отчёта (имитация гонки) — не удваивает и не обнуляет
    got2 = await approve_report(rid6, 1, 300)
    check("повторное одобрение идемпотентно (300)", got2 == 300)

    U7 = 51007
    await add_user(U7, "rep07", "Седьмой", "")
    await _yesterday_report(U7, 100, 1000)
    rid7, credited7 = await add_report(U7, "f", 400, 1200, "2")   # прирост 200
    partial = await approve_report(rid7, 1, 120)                 # админ режет до 120
    check("частичное одобрение (120 из 200)", partial == 120)

    # ── 8b. Порядок одобрения не влияет на итог за сутки ──
    U9 = 51009
    await add_user(U9, "rep09", "Девятый", "")
    await _yesterday_report(U9, 100, 1000)
    a1, _ = await add_report(U9, "f", 100, 1100, "3")
    a2, _ = await add_report(U9, "f", 200, 1200, "3")
    a3, _ = await add_report(U9, "f", 300, 1300, "3")
    for rid_ in (a3, a1, a2):            # одобряем в обратном порядке
        await approve_report(rid_, 1)
    payouts = await payout_reports()
    paid9 = [p for p in payouts if p['user_id'] == U9]
    check("обратный порядок одобрения → тот же итог 300", paid9 and paid9[0]['troops'] == 300)

    # ── 9. Старые отчёты без credited (NULL) — вся заявка, как раньше ──
    U8 = 51008
    await add_user(U8, "rep08", "Восьмой", "")
    conn = await get_db()
    cur = await conn.execute(
        "INSERT INTO reports (user_id, screenshot_file_id, troops_reported, total_troops, "
        "region, credited_troops, status, created_at) "
        "VALUES (?, 'f', 700, 700, '0', NULL, 'pending', datetime('now'))", (U8,))
    legacy_id = cur.lastrowid
    await conn.commit()
    check("старый отчёт (NULL) → вся заявка", await approve_report(legacy_id, 1, 700) == 700)

    # ── 10. Сутки считаются по МСК: отчёт «вчера» не попадает в сегодняшний лимит ──
    check("счётчик суток не считает вчерашний отчёт", await count_reports_today(U2) == 0)
    await add_report(U2, "f", 100, 1500, "0")
    check("после сегодняшнего отчёта счётчик = 1", await count_reports_today(U2) == 1)

    # ── 11. Статистика регионов считает фактически засчитанное, а не заявку ──
    await recompute_region_stats()
    stats = {r['region']: r for r in await get_region_stats()}
    # За сутки по пилоту берётся последний отчёт: у U4 это 100 (а не заявка 300).
    check("регион 1: 24ч = засчитанное последнего отчёта (100), не заявка (300) и не сумма (600)",
          stats["1"]['troops_24h'] == 100)

    # ── 12. Баланс игрока не завышен ──
    u4 = await get_user(U4)
    check("войска игрока = 300 (а не сумма отчётов 600)", u4['troops'] == 300)

    await close_db()
    print(f"\nSmoke 089: {passed} passed, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    async def _main():
        try:
            return await run()
        finally:
            from database.db import close_db
            await close_db()

    sys.exit(asyncio.run(_main()))
