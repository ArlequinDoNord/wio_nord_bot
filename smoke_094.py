"""Smoke v0.17.0: оплата заявки «за сутки» вместо прироста «всего» + накопительный XP.

Новое правило: «всего» — остаток очков пилота в регионе (статистика), а не счётчик
фарма, поэтому оно может уменьшаться (оборона) и расти не от фарма. К оплате идёт
заявка «за сутки» в пределах суточного лимита 4000, независимо от «всего».
Сутки считаются от 05:05 МСК до 05:05 МСК. XP копится 1:1 с фармом и без налога.

Проверяем: неизменное «всего», несколько отчётов за сутки, лимит, сутки по циклу
выплаты, справку за прошлые сутки, XP без налога, региональную статистику по «всего»,
пересчёт висящих отчётов и отсутствие налога у XP.

Запуск: .venv\\Scripts\\python.exe smoke_094.py
"""
import asyncio
import os
import sys

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke094.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB

sys.path.insert(0, os.path.dirname(__file__))


async def run():
    from datetime import timedelta, timezone
    import database.db as dbmod
    from database.db import (
        init_db, close_db, add_user, add_report, approve_report, payout_reports,
        report_payout_context, get_user, get_db, get_report_daily_pay_cap,
        report_prev_day_total, recompute_region_stats, get_region_stats,
        _report_day, report_day_bounds, _TODAY_MSK,
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

    async def _report_at(uid, daily, total, region="0", status="approved",
                         credited=None, paid=1, ts_utc=None):
        """Отчёт с произвольным моментом created_at (UTC-строка)."""
        conn = await get_db()
        await conn.execute(
            "INSERT INTO reports (user_id, screenshot_file_id, troops_reported, total_troops, "
            "region, credited_troops, status, paid, created_at) "
            "VALUES (?, 'f', ?, ?, ?, ?, ?, ?, ?)",
            (uid, daily, total, region, credited, status, paid, ts_utc))
        await conn.commit()

    start, end = report_day_bounds()
    # Время «позавчера»/«вчера» относительно границы суток (05:05 МСК).
    yday = (start - timedelta(hours=1)).astimezone(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    d2 = (start - timedelta(days=1, hours=1)).astimezone(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

    # ── 1. Сутки идут от 05:05 МСК: отчёт за час до границы — вчерашние ──
    check("отчёт часом раньше границы попадает в прошлые сутки",
          _report_day(yday) != _TODAY_MSK)
    check("отчёт сутки назад попадает в прошлые сутки",
          _report_day(d2) != _TODAY_MSK)
    check("граница суток = 05:05 МСК", (start.hour, start.minute) == (5, 5))
    check("сутки длятся ровно сутки", (end - start) == timedelta(days=1))

    # ── 2. «Всего» не растёт — фарм всё равно оплачивается (кейс Антонио) ──
    UA = 91001
    await add_user(UA, "antonio", "Антонио", "Полк")
    await _report_at(UA, 291, 7045, "25", ts_utc=yday)
    ctx = await report_payout_context(UA, 291, 7045)
    check("«всего» не выросло → заявка 291 оплачивается", ctx['payable'] == 291)
    check("счётчик суток чист (вчерашний отчёт не в лимите)", ctx['assigned_today'] == 0)

    # ── 3. Несколько отчётов за сутки суммируются ──
    rid1, c1 = await add_report(UA, "f", 100, 7045, "25")
    rid2, c2 = await add_report(UA, "f", 200, 7145, "25")
    rid3, c3 = await add_report(UA, "f", 50, 7395, "25")
    check("три отчёта за сутки: 100 + 200 + 50", (c1, c2, c3) == (100, 200, 50))
    ctx = await report_payout_context(UA, 100, 7495)
    check("уже принято за сутки = 350", ctx['assigned_today'] == 350)
    check("остаток лимита 4000 − 350 = 3650", ctx['room_today'] == 3650)

    # ── 4. Суточный лимит 4000 режет, а не «всего» ──
    UB = 91002
    await add_user(UB, "limit", "Лимит", "Тест")
    _, c = await add_report(UB, "f", 999999, 7045, "0")
    check("заявка выше лимита обрезана до 4000", c == 4000)
    ctx = await report_payout_context(UB, 1, 7045)
    check("после лимита остатка нет", ctx['payable'] == 0 and ctx['capped_by_limit'])

    # ── 5. Справка «за прошлые сутки» — сумма за сутки, а не «всего» ──
    check("справка за прошлые сутки = 291 (не 7045)", await report_prev_day_total(UA) == 291)

    # ── 6. XP копится 1:1 с фармом, налог только на деньги ──
    await approve_report(rid1, 0)
    await approve_report(rid2, 0)
    await approve_report(rid3, 0)
    payouts = await payout_reports()
    paid = [p for p in payouts if p['user_id'] == UA]
    check("выплата за сутки = 350", paid and paid[0]['troops'] == 350)
    check("XP начислен так же 1:1 (350)", paid and paid[0]['xp'] == 350)
    check("XP без налога: начислено столько же, сколько войск",
          paid and paid[0]['xp'] == paid[0]['troops'])
    u = await get_user(UA)
    check("баланс XP пилота = 350", u['xp_balance'] == 350)
    check("опыт звания (users.troops) = 350", u['troops'] == 350)

    # ── 7. Региональная статистика = сумма «всего» последнего отчёта ──
    await recompute_region_stats()
    stats = {r['region']: r for r in await get_region_stats()}
    # У Антонио последний отчёт: 7395 всего, регион 25
    check("регион 25: силы = «всего» последнего отчёта (7395)",
          stats["25"]['troops_24h'] == 7395)
    check("регион 25: 1 активный пилот", stats["25"]['active_pilots_72h'] == 1)

    # ── 7b. Силы региона НЕ обнуляются со временем (остаток, а не поток) ──
    # Пилот не «испарявается» из региона, просто его отчёт старше 72 часов:
    # в регионе он остаётся, потому что силы берутся из последнего отчёта.
    conn2 = await get_db()
    await conn2.execute("UPDATE reports SET created_at = ? WHERE user_id = ?",
                        ((start - timedelta(days=5, hours=1)).astimezone(timezone.utc)
                         .strftime('%Y-%m-%d %H:%M:%S'), UA))
    await conn2.commit()
    await recompute_region_stats()
    stats_old = {r['region']: r for r in await get_region_stats()}
    check("отчёт старше 5 суток — силы региона на месте (7395), не 0",
          stats_old["25"]['troops_24h'] == 7395)
    check("пилот остаётся в регионе, даже если давно не сдавал отчёт",
          stats_old["25"]['active_pilots_72h'] == 1)
    # Возвращаем дату, чтобы дальнейшие проверки не зависели от этого сдвига
    await conn2.execute("UPDATE reports SET created_at = datetime('now') WHERE user_id = ?", (UA,))
    await conn2.commit()
    await recompute_region_stats()
    check("лимит суток по умолчанию 4000", await get_report_daily_pay_cap() == 4000)

    # ── 8. Висящий отчёт с credited=0 пересчитывается по новому правилу ──
    conn = await get_db()
    cur = await conn.execute(
        "INSERT INTO reports (user_id, screenshot_file_id, troops_reported, total_troops, "
        "region, credited_troops, status, created_at) "
        "VALUES (?, 'f', 291, 7045, '25', 0, 'pending', datetime('now'))", (UA,))
    stuck = cur.lastrowid
    await conn.commit()
    check("висящий pending с credited=0 оплачивается по заявке",
          await approve_report(stuck, 0) == 291)

    # ── 9. Отчёт сдан вчера, одобрен сегодня: лимит берётся по ЕГО суткам ──
    # Регресс: раньше одобрение считалось по текущим суткам, и сегодняшний отчёт
    # (3900) съедал лимит, из-за чего вчерашний фарм резался с 291 до 100.
    UB = 91012
    await add_user(UB, "late", "ПилотОпоздал", "Тест")
    rid_y, credited_y = await add_report(UB, "f", 291, 7045, "25")
    await conn.execute("UPDATE reports SET created_at = ? WHERE id = ?", (yday, rid_y))
    rid_t, credited_t = await add_report(UB, "f", 3900, 8000, "25")
    await conn.commit()
    check("сегодняшний отчёт съедает лимит сегодняшних суток", credited_t == 3900)
    check("одобрение ВЧЕРАШНЕГО отчёта не режется сегодняшним лимитом",
          await approve_report(rid_y, 0) == 291)
    check("одобрение сегодняшнего — по сегодняшнему лимиту",
          await approve_report(rid_t, 0) == 3900)
    paid_b = [p for p in await payout_reports() if p['user_id'] == UB]
    check("выплата за оба отчёта = 4191 (291 + 3900)",
          paid_b and paid_b[0]['troops'] == 4191)

    # ── 10. Вчерашний отчёт не отнимает лимит у сегодняшнего и наоборот ──
    UC = 91003
    await add_user(UC, "mix", "ПилотСмешанный", "Тест")
    rid_c1, _ = await add_report(UC, "f", 4000, 4000, "13")
    await conn.execute("UPDATE reports SET created_at = ? WHERE id = ?", (yday, rid_c1))
    rid_c2, c_c2 = await add_report(UC, "f", 4000, 8000, "13")
    await conn.commit()
    check("вчерашний отчёт 4000 не съел сегодняшний лимит", c_c2 == 4000)
    check("одобрение вчерашнего 4000", await approve_report(rid_c1, 0) == 4000)
    check("одобрение сегодняшнего 4000", await approve_report(rid_c2, 0) == 4000)

    # ── 11. Переезд пилота: силы И число пилотов переезжают вместе ──
    # Свой регион 11, чтобы не пересекаться с остальными проверками.
    UD = 91004
    await add_user(UD, "move", "ПилотПереезд", "Тест")
    rid_d1, _ = await add_report(UD, "f", 100, 5000, "11")
    await conn.execute("UPDATE reports SET status = 'approved' WHERE id = ?", (rid_d1,))
    await conn.execute("UPDATE reports SET created_at = ? WHERE id = ?", (yday, rid_d1))
    await conn.commit()
    await recompute_region_stats()
    s1 = {r['region']: r for r in await get_region_stats()}
    check("до переезда регион 11: 5000 и 1 пилот",
          (s1["11"]['troops_24h'], s1["11"]['active_pilots_72h']) == (5000, 1))

    # Переезд: новый отчёт из другого региона
    rid_d2, _ = await add_report(UD, "f", 100, 5200, "12")
    await conn.execute("UPDATE reports SET status = 'approved' WHERE id = ?", (rid_d2,))
    await conn.commit()
    await recompute_region_stats()
    s2 = {r['region']: r for r in await get_region_stats()}
    check("после переезда старый регион 11 выпал из статистики (пилотов нет)",
          "11" not in s2)
    check("новый регион 12: силы 5200 и 1 пилот",
          (s2["12"]['troops_24h'], s2["12"]['active_pilots_72h']) == (5200, 1))

    # Пилот не учитывается в двух регионах сразу
    total_pilots = sum(r['active_pilots_72h'] for r in s2.values())
    check("пилот не задвоен в статистике по регионам", total_pilots == 4)

    # ── 12. Показания пилотов одного региона складываются ──
    UE = 91005
    await add_user(UE, "pair", "ПилотПара", "Тест")
    rid_e, _ = await add_report(UE, "f", 100, 3000, "13")
    await conn.execute("UPDATE reports SET status = 'approved' WHERE id = ?", (rid_e,))
    await conn.commit()
    await recompute_region_stats()
    s3 = {r['region']: r for r in await get_region_stats()}
    # В регионе 13 теперь два пилота: этот (3000) и пилот из теста 10, у которого
    # последний одобренный отчёт содержит «всего» = 8000
    check("показания пилотов региона складываются (3000 + 8000 = 11000)",
          s3["13"]['troops_24h'] == 11000)
    check("в регионе 13 два пилота", s3["13"]['active_pilots_72h'] == 2)

    # ── 13. Повторный пересчёт на тех же данных ничего не ломает ──
    await recompute_region_stats()
    s4 = {r['region']: r for r in await get_region_stats()}
    check("повторный пересчёт даёт тот же результат",
          {k: (v['troops_24h'], v['active_pilots_72h']) for k, v in s4.items()}
          == {k: (v['troops_24h'], v['active_pilots_72h']) for k, v in s3.items()})
    # Логгер db.py нужен миграциям на старте: без него init_db падал бы с NameError
    check("в database.db есть logger для миграций", dbmod.logger is not None)

    await close_db()
    print(f"\nSmoke 094: {passed} passed, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    async def _main():
        try:
            return await run()
        finally:
            from database.db import close_db
            await close_db()

    sys.exit(asyncio.run(_main()))
