"""Smoke v0.15.32 (обновлён под v0.22.0): оплата отчётов — заявка «за сутки».

Правило: к оплате идёт заявка «сколько заработал за сутки» в пределах суточного
лимита. Поле «всего» (остаток очков пилота в регионе) в оплате НЕ участвует: оно
может уменьшаться на обороне и расти не от фарма. «Всего» и регион идут в
статистику сил по регионам.

Несколько отчётов за сутки НЕ суммируются (v0.22.0): суточное — это снимок, оно
копилось с нуля до максимума, и каждый следующий отчёт заменяет предыдущий. Платят
по последнему отчёту суток, даже если он меньше предыдущего. Отклонённые отчёты не
съедают лимит, повторное одобрение не платит дважды, опыт копится 1:1 с фармом и
без налога.

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
    """Отчёт «за вчера»: напрямую в БД, часом раньше границы текущих суток.

    Граница берётся из report_day_bounds(), а не «сейчас минус сутки»: сутки идут
    от 10:00 МСК, и в 00:00–10:00 МСК «минус сутки» попал бы внутрь тех же суток.
    """
    from datetime import timedelta, timezone
    from database.db import get_db, report_day_bounds
    start, _end = report_day_bounds()
    ts = (start - timedelta(hours=1)).astimezone(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    conn = await get_db()
    await conn.execute(
        "INSERT INTO reports (user_id, screenshot_file_id, troops_reported, total_troops, "
        "region, credited_troops, status, paid, created_at) "
        "VALUES (?, 'f', ?, ?, '0', ?, ?, 1, ?)",
        (uid, daily, total, credited, status, ts))
    await conn.commit()


async def run():
    from database.db import (
        init_db, close_db, add_user, add_report, approve_report, payout_reports,
        report_payout_context, get_user, count_reports_today, get_db, reject_report,
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
    # У второго пилота история есть — для проверки справки по «всего»
    U2 = 51002
    await add_user(U2, "rep02", "Второй", "Тестов")

    # ── 1. Первый отчёт: платим заявку «за сутки» ──
    ctx = await report_payout_context(U, 782, 782)
    check("первый отчёт: к оплате по заявке", ctx["payable"] == 782)
    rid, credited = await add_report(U, "f", 782, 782, "0")
    check("add_report первого отчёта: credited 782", credited == 782)

    # ── 2. «Всего» — только справочные данные, на оплату не влияет ──
    await _yesterday_report(U2, 900, 14000)
    ctx = await report_payout_context(U2, 900, 14000)   # «всего» не изменилось
    check("«всего» в оплате не участвует (заявка 900 оплачена вся)", ctx["payable"] == 900)
    check("«всего» остаётся справкой (14000)", ctx["base"] == 14000)
    ctx = await report_payout_context(U2, 15000, 15000)
    check("суточный лимит режет заявку (15000 → 4000)", ctx["payable"] == 4000)

    # ── 3. Именно тот случай из жалобы: «всего» не выросло, а фарм есть ──
    U3 = 51003
    await add_user(U3, "rep03", "Третий", "")
    await _yesterday_report(U3, 782, 400)      # вчера накоплено 400
    ctx = await report_payout_context(U3, 782, 782)   # сегодня вписал 782 и туда, и туда
    check("«всего» не выросло — фарм 782 оплачивается полностью", ctx["payable"] == 782)

    # ── 3b. Реальный случай Антонио: заявка 291, «всего» без изменений ──
    U3b = 510031
    await add_user(U3b, "antonio", "Антонио", "")
    await _yesterday_report(U3b, 1, 7045)
    ctx = await report_payout_context(U3b, 291, 7045)
    check("Антонио: 291 за сутки оплачиваются, «всего» не урезает", ctx["payable"] == 291)

    # ── 4. Заявка больше «всего» (накопленное ушло на оборону) — платится заявка ──
    ctx = await report_payout_context(U3, 500, 400)
    check("«всего» меньше заявки (оборона) → к оплате заявка", ctx["payable"] == 500)

    # ── 5. Несколько отчётов за сутки: платит ПОСЛЕДНИЙ, а не сумма ──
    # Правило владельца (2026-10-03): суточное — снимок, отчёты не складываются.
    U4 = 51004
    await add_user(U4, "rep04", "Четвёртый", "")
    await _yesterday_report(U4, 100, 1000)
    r1, c1 = await add_report(U4, "f", 100, 1100, "1")
    r2, c2 = await add_report(U4, "f", 200, 1200, "1")
    r3, c3 = await add_report(U4, "f", 300, 1300, "1")
    check("заявка каждого отчёта засчитывается целиком при сдаче",
          (c1, c2, c3) == (100, 200, 300))
    await approve_report(r1, 0, c1)
    await approve_report(r2, 0, c2)
    await approve_report(r3, 0, c3)
    payouts = await payout_reports()
    paid4 = [p for p in payouts if p['user_id'] == U4]
    check("выплата за сутки = последний отчёт (300), не сумма 600",
          paid4 and paid4[0]['troops'] == 300)

    # ── 6. Отклонённый отчёт не тратит суточный лимит ──
    U5 = 51005
    await add_user(U5, "rep05", "Пятый", "")
    r5, _c5 = await add_report(U5, "f", 999999, 999999, "0")
    await reject_report(r5, 1)
    ctx = await report_payout_context(U5, 500, 2500)
    check("отклонённый отчёт не съедает лимит суток", ctx["payable"] == 500)

    # ── 7. approve_report: пересчёт по лимиту, частичное одобрение ──
    U6 = 51006
    await add_user(U6, "rep06", "Шестой", "")
    await _yesterday_report(U6, 100, 1000)
    rid6, credited6 = await add_report(U6, "f", 500, 1300, "2")
    check("add_report: credited = заявка (500)", credited6 == 500)
    got = await approve_report(rid6, 1, 500)
    check("approve: 500", got == 500)
    # Повторное одобрение того же отчёта (имитация гонки/повторного нажатия) НЕ платит:
    # отчёт уже не pending, а выдача по нему была. Раньше здесь возвращалось 500.
    got2 = await approve_report(rid6, 1, 500)
    check("повторное одобрение не выдаёт деньги снова (0)", got2 == 0)

    U7 = 51007
    await add_user(U7, "rep07", "Седьмой", "")
    await _yesterday_report(U7, 100, 1000)
    rid7, credited7 = await add_report(U7, "f", 400, 1200, "2")
    partial = await approve_report(rid7, 1, 120)                 # админ режет до 120
    check("частичное одобрение (120 из 400)", partial == 120)

    # ── 7b. Порядок одобрения не влияет на итог за сутки ──
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
    check("обратный порядок одобрения → итог тот же (последний отчёт)",
          paid9 and paid9[0]['troops'] == 300)

    # ── 8. Старые отчёты без credited (NULL) — вся заявка, как раньше ──
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

    # ── 9. Сутки считаются по циклу выплаты: отчёт «вчера» не в сегодняшнем лимите ──
    check("счётчик суток не считает вчерашний отчёт", await count_reports_today(U2) == 0)
    await add_report(U2, "f", 100, 1500, "0")
    check("после сегодняшнего отчёта счётчик = 1", await count_reports_today(U2) == 1)

    # ── 10. Статистика регионов: силы = накопленное «всего» пилота ──
    await recompute_region_stats()
    stats = {r['region']: r for r in await get_region_stats()}
    # У U4 последний отчёт: 1300 всего, 3 пилота в регионе 1 за 72ч
    check("регион 1: силы = «всего» последнего отчёта пилота (1300)",
          stats["1"]['troops_24h'] == 1300)
    check("регион 1: активных пилотов за 72ч = 1", stats["1"]['active_pilots_72h'] == 1)

    # ── 11. Баланс игрока = выплаченному, опыт копится 1:1 и без налога ──
    u4 = await get_user(U4)
    check("войска игрока = последний отчёт суток (300)", u4['troops'] == 300)
    check("накопительный опыт = 300 (1:1 с фармом)", u4['xp_balance'] == 300)

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
