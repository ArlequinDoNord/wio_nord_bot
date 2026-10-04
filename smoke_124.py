"""Smoke 124 — оплата отчётов по ПОСЛЕДНЕМУ снимку суток (v0.22.0).

Правило владельца (2026-10-03): за отчётные сутки (10:00 МСК → 10:00 МСК) платится
«за сутки» из ПОСЛЕДНЕГО отчёта, а не сумма отчётов. Суточное — снимок: оно копится
с нуля до максимума, каждый следующий отчёт заменяет предыдущий.

Проверяет:
   1. Ранний отчёт суток superseded: платит 0, сумма заявок остаётся справочной.
   2. Последний отчёт платит свою сумму; скидывает ли сумма копилок — неважно.
   3. Кап ограничивает ОДИН снимок, а не сумму суток.
   4. payout_reports() платит по последнему отчёту и не платит дважды.
   5. Неодобренный последний отчёт блокирует выплату суток; после одобрения — платит.
   6. Отклонение уже оплаченного последнего отчёта не открывает вторую выплату.
   7. approve_report не выдаёт деньги повторно по уже одобренному отчёту.
   8. Граница 10:00 МСК: 09:59:59 — вчерашние сутки, 10:00:00 — сегодняшние.
   9. Единый эталон «сейчас»: _today_msk() == today_report_day(), и отчёт за
      прошлые сутки не тратит лимит сдачи сегодняшних.
  10. Мои отчёты: created_at_msk/report_day_value_of согласованы (сдача в 08:00 МСК
      показывается как сегодняшние 08:00, а сутки — как вчерашние).
"""
import asyncio
import os
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

PASS, FAIL = 0, 0


def check(name, cond):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  OK  {name}")
    else:
        FAIL += 1
        print(f"FAIL  {name}")


async def main():
    global DB_PATH
    import config
    DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_test_smoke124.db")
    for suffix in ("", "-wal", "-shm"):
        try:
            os.remove(DB_PATH + suffix)
        except OSError:
            pass
    config.DB_PATH = DB_PATH

    import database.db as db
    db.DB_PATH = DB_PATH
    from database.db import (
        init_db, close_db, get_db, add_user, add_report, approve_report,
        reject_report, payout_reports, report_payout_context, set_report_daily_pay_cap,
        get_report_daily_pay_cap, report_day_value_of, created_at_msk, today_report_day,
        count_reports_today, _today_msk, _report_cycle_day_of,
        recompute_region_stats, get_region_stats,
    )

    await init_db()

    day = today_report_day()          # текущие отчётные сутки 'YYYY-MM-DD'
    day_dt = datetime.strptime(day, "%Y-%m-%d")

    def msk(day_offset, hour, minute=0, second=0):
        """МСК-время заданных суток → UTC-строка created_at (в базе хранится UTC)."""
        return ((day_dt + timedelta(days=day_offset)).replace(
            hour=hour, minute=minute, second=second)
            - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S")

    def at(hour, minute=0):
        """МСК-время внутри текущих суток → UTC-строка created_at."""
        return msk(0, hour, minute)

    async def stamp(rid, utc_str):
        conn = await get_db()
        await conn.execute("UPDATE reports SET created_at = ? WHERE id = ?", (utc_str, rid))
        await conn.commit()

    async def troops_of(uid):
        conn = await get_db()
        row = await (await conn.execute(
            "SELECT troops FROM users WHERE user_id = ?", (uid,))).fetchone()
        return row['troops'] if row else 0

    async def xp_of(uid):
        conn = await get_db()
        row = await (await conn.execute(
            "SELECT xp_balance FROM users WHERE user_id = ?", (uid,))).fetchone()
        return row['xp_balance'] if row else 0

    await add_user(1001, "u1", "U1", "Лётчик")
    await add_user(1002, "u2", "U2", "Лётчик")
    await add_user(1003, "u3", "U3", "Лётчик")
    await add_user(1004, "u4", "U4", "Лётчик")
    await add_user(1005, "u5", "U5", "Лётчик")
    await add_user(1006, "u6", "U6", "Лётчик")
    await add_user(1007, "u7", "U7", "Лётчик")
    for _uid, _un in ((1008, "w8"), (1009, "w9"), (1010, "w10"), (1011, "w11"),
                      (1012, "w12"), (1013, "w13"), (1014, "w14")):
        await add_user(_uid, _un, "Окна", "Окна")
    await set_report_daily_pay_cap(4000)

    # ── 8. Граница 10:00 МСК (до всех выплат, чистые функции) ───────────────
    print("\n= Граница отчётных суток 10:00 МСК =")
    check("09:59:59 МСК → вчерашние сутки",
          report_day_value_of(msk(0, 9, 59, 59))
          == (day_dt - timedelta(days=1)).strftime("%Y-%m-%d"))
    check("10:00:00 МСК → сегодняшние сутки",
          report_day_value_of(msk(0, 10, 0, 0)) == day)
    check("сдача 08:00 МСК = вчерашние сутки, но время сегодняшнее",
          report_day_value_of(msk(0, 8, 0))
          == (day_dt - timedelta(days=1)).strftime("%Y-%m-%d")
          and created_at_msk(msk(0, 8, 0))[-5:] == "08:00")

    # ── 9. Единый эталон «сейчас» ─────────────────────────────────────────
    print("\n= Единый источник времени =")
    check("_today_msk() == today_report_day()", _today_msk() == today_report_day())

    # ── 1-2. Три отчёта за сутки: платит последний ─────────────────────────
    print("\n= Три отчёта за сутки: платит последний =")
    UA = 1001
    r1, _ = await add_report(UA, "s", 300, 300, "1")
    await stamp(r1, at(11))
    r2, _ = await add_report(UA, "s", 700, 700, "1")
    await stamp(r2, at(14))
    r3, _ = await add_report(UA, "s", 1200, 1200, "1")
    await stamp(r3, at(18))

    c1 = await report_payout_context(UA, 300, 300, exclude_id=r1, cycle_day=day)
    check("ранний отчёт помечен superseded", c1["superseded"] is True)
    check("ранний отчёт платит 0", c1["payable"] == 0)
    c2 = await report_payout_context(UA, 700, 700, exclude_id=r2, cycle_day=day)
    check("средний отчёт superseded", c2["superseded"] is True and c2["payable"] == 0)
    c3 = await report_payout_context(UA, 1200, 1200, exclude_id=r3, cycle_day=day)
    check("последний отчёт — не superseded", c3["superseded"] is False)
    check(f"последний отчёт платит свою сумму ({c3['payable']})", c3["payable"] == 1200)
    check(f"сумма заявок за сутки справочно, без себя ({c3['assigned_today']})",
          c3["assigned_today"] == 1000)

    # Последний МЕНЬШЕ предыдущего — всё равно платится последний.
    UB = 1002
    b1, _ = await add_report(UB, "s", 900, 900, "2")
    await stamp(b1, at(12))
    b2, _ = await add_report(UB, "s", 400, 400, "2")
    await stamp(b2, at(19))
    bc1 = await report_payout_context(UB, 900, 900, exclude_id=b1, cycle_day=day)
    bc2 = await report_payout_context(UB, 400, 400, exclude_id=b2, cycle_day=day)
    check("отчёт 900 superseded", bc1["superseded"] is True and bc1["payable"] == 0)
    check("последний (меньший) отчёт платит 400, а не 1300", bc2["payable"] == 400)

    # ── 3. Кап режет один снимок ──────────────────────────────────────────
    print("\n= Суточный кап =")
    UC = 1003
    c_1, _ = await add_report(UC, "s", 3000, 3000, "3")
    await stamp(c_1, at(11))
    c_2, _ = await add_report(UC, "s", 6000, 6000, "3")
    await stamp(c_2, at(16))
    cc2 = await report_payout_context(UC, 6000, 6000, exclude_id=c_2, cycle_day=day)
    check(f"кап 4000 режет последний снимок ({cc2['payable']})", cc2["payable"] == 4000)
    check("capped_by_limit выставлен", cc2["capped_by_limit"] is True)
    check("кап не суммируется с ранним отчётом (3000 не добавлены)",
          cc2["payable"] == 4000 and cc2["assigned_today"] == 3000)
    await set_report_daily_pay_cap(0)
    cc0 = await report_payout_context(UC, 6000, 6000, exclude_id=c_2, cycle_day=day)
    check("кап 0 = без ограничения", cc0["payable"] == 6000 and cc0["cap"] is None)
    await set_report_daily_pay_cap(4000)

    # ── 4. payout_reports: по последнему и без двойной выплаты ────────────
    print("\n= payout_reports() =")
    await approve_report(r1, 0)
    await approve_report(r2, 0)
    await approve_report(r3, 0)
    for rid in (b1, b2, c_1, c_2):
        await approve_report(rid, 0)

    before_u1 = await troops_of(UA)
    await payout_reports()
    gained = (await troops_of(UA)) - before_u1
    check(f"выплачено по последнему отчёту, не сумма ({gained})", gained == 1200)
    check("опыт 1:1 с войсками", (await xp_of(UA)) >= 1200)

    before_u1 = await troops_of(UA)
    await payout_reports()
    check("повторный payout_reports() не платит дважды",
          (await troops_of(UA)) == before_u1)

    # ── 5. Неодобренный последний отчёт блокирует выплату ─────────────────
    print("\n= Последний отчёт ещё не одобрен =")
    UD = 1004
    d1, _ = await add_report(UD, "s", 500, 500, "4")
    await stamp(d1, at(13))
    d2, _ = await add_report(UD, "s", 800, 800, "4")
    await stamp(d2, at(17))
    await approve_report(d1, 0)
    before = await troops_of(UD)
    await payout_reports()
    check("сутки не выплачены, пока последний отчёт не одобрен",
          (await troops_of(UD)) == before)
    await approve_report(d2, 0)
    await payout_reports()
    check(f"после одобрения последнего выплачено 800 ({(await troops_of(UD)) - before})",
          (await troops_of(UD)) - before == 800)

    # ── 6. Отклонение оплаченного последнего не открывает 2-ю выплату ─────
    print("\n= Отклонение уже оплаченного последнего отчёта =")
    UE = 1005
    e1, _ = await add_report(UE, "s", 600, 600, "5")
    await stamp(e1, at(11))
    e2, _ = await add_report(UE, "s", 1000, 1000, "5")
    await stamp(e2, at(15))
    await approve_report(e1, 0)
    await approve_report(e2, 0)
    before = await troops_of(UE)
    await payout_reports()
    check(f"первая выплата 1000 ({(await troops_of(UE)) - before})",
          (await troops_of(UE)) - before == 1000)

    await reject_report(e2, 0)
    ec1 = await report_payout_context(UE, 600, 600, exclude_id=e1, cycle_day=day)
    check("после отклонения последнего бывший последний снова superseded-кандидат",
          ec1["superseded"] is False)
    check(f"но уже выплачено {ec1['already_paid']} — доплаты нет",
          ec1["already_paid"] == 1000 and ec1["payable"] == 0)
    before = await troops_of(UE)
    await payout_reports()
    check("повторная выплата не прошла", (await troops_of(UE)) == before)

    # ── 7. Повторное одобрение ────────────────────────────────────────────
    print("\n= Повторное одобрение =")
    dup = await approve_report(e1, 0)
    check(f"повторное одобрение вернуло 0 (было {dup})", dup == 0)
    before = await troops_of(UE)
    await payout_reports()
    check("и не выплатило ничего сверху", (await troops_of(UE)) == before)

    # ── 7b. Отчёт за ПРОШЛЫЕ сутки: одобрен, оплачен сразу ─────────────────
    # Отдельный пилот: у UE сутки уже оплачены, и мгновенная выплата пересчитала бы
    # его снимок по сегодняшним суткам и дала бы 0 вместо полной суммы.
    UG = 1006
    # Час внутри ПРОШЛЫХ отчётных суток: 14:00 МСК вчерашнего цикла. Именно цикл по
    # МСК, а не календарный «вчерашний» день UTC: после полуночи UTC «вчера 12:00
    # UTC» — это 15:00 МСК СЕГОДНЯШНИХ суток, мгновенной выплаты там ещё нет, и тест
    # проверял бы не то, что назвал.
    g1, _ = await add_report(UG, "s", 700, 700, "6")
    await stamp(g1, msk(-1, 14))
    paid_now = await approve_report(g1, 0)
    check(f"прошлые сутки: одобрение платит сразу ({paid_now})", paid_now == 700)
    check("и сразу начисляет", (await troops_of(UG)) == 700)
    check("повторное одобрение прошлых суток тоже возвращает 0",
          await approve_report(g1, 0) == 0)
    before = await troops_of(UG)
    await payout_reports()
    check("мгновенная выплата не дублируется суточным циклом",
          (await troops_of(UG)) == before)

    # ── 7c. Новый снимок после выплаты: сутки платятся ОДИН раз ────────────
    # Регресс на двойное вычитание: approve_report уже записал в credited_troops
    # дельту (снимок минус выплаченное), поэтому payout_reports берёт её как есть.
    # Раньше он вычитал выплаченное второй раз и платил 1200 − 1200 − 1200 = 0.
    UH = 1007
    h1, _ = await add_report(UH, "s", 300, 300, "7")
    await stamp(h1, at(12))
    await approve_report(h1, 0)
    await payout_reports()
    before_h = await troops_of(UH)
    h2, _ = await add_report(UH, "s", 900, 900, "7")
    await stamp(h2, at(19))
    top_up = await approve_report(h2, 0)
    check(f"новый снимок платит разницу (900 − 300 = 600, было {top_up})",
          top_up == 600)
    await payout_reports()
    gained_h = (await troops_of(UH)) - before_h
    check(f"доплата 600, за сутки всего 900, а не 1200 ({gained_h})",
          gained_h == 600 and (await troops_of(UH)) == 900)

    # ── 10. Окна одобрения: сегодня / вчера / позавчера ────────────────────
    # Смысл раздела: отчёт, чьё расчётное 10:00 уже прошло, платится СРАЗУ при
    # одобрении («мгновенная выплата»), иначе пилот ждал бы почти сутки. Сутки, чьё
    # 10:00 ещё не наступило, ждут суточного цикла. Проверяем обе стороны, включая
    # переход «последний отклонён → предыдущий становится последним».
    print("\n= Окна одобрения =")

    # 1) Вчерашний отчёт, одобряю сегодня → сразу.
    UI1 = 1008
    await add_user(UI1, "w1", "ВчераОдин", "Окна")
    i1, _ = await add_report(UI1, "s", 500, 500, "8")
    await stamp(i1, msk(-1, 14))
    check(f"вчерашний отчёт одобрен сразу ({await approve_report(i1, 0)})",
          await troops_of(UI1) == 500)
    before = await troops_of(UI1)
    await payout_reports()
    check("суточный цикл не доплачивает сверху", (await troops_of(UI1)) == before)

    # 2) Позавчерашний отчёт → тоже сразу: правило «прошло 10:00», а не «вчера».
    UI2 = 1009
    await add_user(UI2, "w2", "Позавчера", "Окна")
    i2, _ = await add_report(UI2, "s", 600, 600, "9")
    await stamp(i2, msk(-2, 12))
    check(f"отчёт двухдневной давности одобрен сразу ({await approve_report(i2, 0)})",
          await troops_of(UI2) == 600)

    # 3) Вчера два отчёта: одобряю ПОЗДНИЙ → платится поздний, ранний superseded.
    UI3 = 1010
    await add_user(UI3, "w3", "ВчераПара", "Окна")
    j1, _ = await add_report(UI3, "s", 400, 400, "10")
    await stamp(j1, msk(-1, 14))
    j2, _ = await add_report(UI3, "s", 900, 900, "10")
    await stamp(j2, msk(-1, 19))
    check(f"поздний вчерашний отчёт платится сразу ({await approve_report(j2, 0)})",
          await troops_of(UI3) == 900)
    check("ранний вчерашний superseded — платит 0",
          await approve_report(j1, 0) == 0)
    before = await troops_of(UI3)
    await payout_reports()
    check("ранний не доплачивается позже", (await troops_of(UI3)) == before)

    # 4) Вчера два отчёта: одобряю РАННИЙ, пока поздний ещё pending → 0.
    #    Если поздний потом отклоняют, сутки отдаются раннему — и сразу.
    UI4 = 1011
    await add_user(UI4, "w4", "ВчераПозднийОтклонён", "Окна")
    k1, _ = await add_report(UI4, "s", 500, 500, "11")
    await stamp(k1, msk(-1, 14))
    k2, _ = await add_report(UI4, "s", 800, 800, "11")
    await stamp(k2, msk(-1, 20))
    check("ранний при висящем позднем не платится", await approve_report(k1, 0) == 0)
    check("и пилоту пока ничего не начислено", (await troops_of(UI4)) == 0)
    await reject_report(k2, 0)
    check("отклонён поздний → ранний стал последним и оплачен сразу (500)",
          (await troops_of(UI4)) == 500)

    # 5) То же для НЕзакрытых суток: ждём 10:00, а не платим сразу.
    UI5 = 1012
    await add_user(UI5, "w5", "Сегодня", "Окна")
    m1, _ = await add_report(UI5, "s", 700, 700, "12")
    await stamp(m1, at(13))
    check("сегодняшний отчёт одобрен, но не выплачен",
          await approve_report(m1, 0) == 700 and (await troops_of(UI5)) == 0)
    await payout_reports()
    check("суточный цикл выплатил 700", (await troops_of(UI5)) == 700)

    # 6) Отклонение уже оплаченного последнего → доплаты нет.
    UI6 = 1013
    await add_user(UI6, "w6", "ОплаченныйОтклонён", "Окна")
    n1, _ = await add_report(UI6, "s", 1200, 1200, "13")
    await stamp(n1, at(16))
    await approve_report(n1, 0)
    await payout_reports()
    check("сегодняшние сутки выплачены 1200", (await troops_of(UI6)) == 1200)
    await reject_report(n1, 0)
    before = await troops_of(UI6)
    await payout_reports()
    check("отклонение оплаченного не открывает вторую выплату",
          (await troops_of(UI6)) == before)

    # ── 9. Лимит сдачи и эталон времени ───────────────────────────────────
    print("\n= Сутки отчёта в сдаче =")
    conn = await get_db()
    old_day = (day_dt - timedelta(days=1)).strftime("%Y-%m-%d")
    await conn.execute(
        "UPDATE reports SET created_at = ? WHERE id = ?",
        (f"{old_day} 11:00:00", r3))
    await conn.commit()
    check("отчёт за прошлые сутки попадает в сутки по created_at",
          _report_cycle_day_of(f"{old_day} 11:00:00") == old_day)
    check("утёкший в прошлые сутки отчёт не тратит лимит сдачи сегодня",
          await count_reports_today(UA) == 2)
    await stamp(r3, at(18))
    check("после возврата в текущие сутки счётчик снова 3",
          await count_reports_today(UA) == 3)

    # ── 11. Регион нормализуется при записи ────────────────────────────────
    # reports.region — TEXT, а региональная статистика группирует по этой строке.
    # Без нормализации «07» и «7» — два разных региона, и силы пилота разъезжаются.
    print("\n= Нормализация региона =")
    UR1 = 1014
    await add_user(UR1, "w14", "РегионВедущийНоль", "Окна")
    # Регионы 30 и 31 в этом смоуке не использует никто — иначе проверка «пилот уехал»
    # путалась бы с чужими силами в том же регионе.
    t1, _ = await add_report(UR1, "s", 100, 100, "030")
    t2, _ = await add_report(UR1, "s", 200, 200, "30")
    conn = await get_db()
    stored = [r['region'] for r in await (await conn.execute(
        "SELECT region FROM reports WHERE id IN (?, ?) ORDER BY id", (t1, t2))).fetchall()]
    check("«030» и «30» сохраняются как один регион «30»", stored == ['30', '30'])
    await approve_report(t1, 0)
    await approve_report(t2, 0)
    await recompute_region_stats()
    stats = {r['region']: (r['troops_total'], r['pilots_count'])
             for r in await get_region_stats()}
    check("пилот с регионом «30» учтён один раз и со своими силами",
          stats.get('30') == (200, 1))
    # Пилот переехал в регион 31: сила 200 из «30» должна уехать вместе с ним, иначе
    # «30» и «030» разъедутся на два региона, если хоть одна строка минует нормализацию.
    t3, _ = await add_report(UR1, "s", 300, 300, "031")
    await approve_report(t3, 0)
    await recompute_region_stats()
    stats = {r['region']: (r['troops_total'], r['pilots_count'])
             for r in await get_region_stats()}
    check("переезд увозит силы пилота в новый регион",
          stats.get('31') == (300, 1) and '30' not in stats)

    # ── 12. Одобрение несуществующего отчёта не притворяется лимитом ───────
    check("одобрение несуществующего отчёта вернуло 0, а не False",
          await approve_report(999999, 0) == 0 and (await approve_report(999999, 0)) is not False)

    await close_db()
    print(f"\n{'=' * 46}\nPASS: {PASS}   FAIL: {FAIL}")
    print("SMOKE 124 OK" if FAIL == 0 else "SMOKE 124 FAILED")
    return 1 if FAIL else 0


DB_PATH = None


async def _cleanup():
    """Закрыть БД и убрать файлы. Без этого при падении внутри main процесс
    не завершается: aiosqlite держит свой поток, и тест молчаит вместо ошибки."""
    try:
        from database.db import close_db
        await close_db()
    except Exception:
        pass
    for suffix in ("", "-wal", "-shm"):
        try:
            os.remove(DB_PATH + suffix)
        except (OSError, NameError):
            pass


if __name__ == "__main__":
    code = 1
    try:
        code = asyncio.run(main()) or 0
    except Exception:
        import traceback
        traceback.print_exc()
    finally:
        asyncio.run(_cleanup())
    sys.exit(code)
