"""Smoke 129 — позднее одобрение второго отчёта платит ТОЛЬКО РАЗНИЦУ (v0.22.7).

Правило владельца: суточное — это СНИМОК, а не приход. Если за отчётные сутки
пилот сдал два отчёта (15:00 — суточные 100, 23:00 — суточные 150), то за сутки
полагается 150, а не 250. Отсюда и обязательное следствие для ПОЗДНЕГО одобрения:
  • если первый отчёт (100) уже одобрен и оплачен, а второй (150) одобряют после
    расчётных 10:00 — выплачивается только разница 50, итого за сутки 150;
  • если второй (80) МЕНЬШЕ уже оплаченного — выплачивается 0: снимок неактуальный.

Проверяются обе ветки approve_report (мгновенная оплата за прошлые сутки и
отложенная через суточный цикл в 10:00), блокировка цикла висящим PENDING и
защита от повторной выплаты при следующем запуске цикла.

Запуск: .venv\\Scripts\\python.exe smoke_129.py
"""
import asyncio
import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

FAILED = []
NM0 = 10  # add_user заводит новому пилоту 10 НМ — от выплаты отсчитываем


def check(name, cond, extra=""):
    print(("  ok   " if cond else "  FAIL ") + name + (f"   [{extra}]" if extra else ""))
    if not cond:
        FAILED.append(name)


async def main():
    import config
    DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_test_smoke129.db")
    for suffix in ("", "-wal", "-shm"):
        try:
            os.remove(DB_PATH + suffix)
        except OSError:
            pass
    config.DB_PATH = DB_PATH

    import database.db as db
    db.DB_PATH = DB_PATH
    from database.db import (init_db, close_db, get_db, add_user, add_report,
                             approve_report, payout_reports, today_report_day)

    await init_db()

    today = today_report_day()
    today_dt = datetime.strptime(today, "%Y-%m-%d")
    y = today_dt - timedelta(days=1)   # прошлые сутки [y 10:00 .. y+1 10:00) МСК

    def past(hour, minute=0):
        """МСК-время прошлых суток → UTC-строка created_at (в базе хранится UTC)."""
        return (y.replace(hour=hour, minute=minute) - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S")

    def cur(hour, minute=0):
        """МСК-время текущих суток → UTC-строка created_at."""
        return (today_dt.replace(hour=hour, minute=minute) - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S")

    async def stamp(rid, utc_str):
        conn = await get_db()
        await conn.execute("UPDATE reports SET created_at = ? WHERE id = ?", (utc_str, rid))
        await conn.commit()

    async def val(uid, col):
        conn = await get_db()
        row = await (await conn.execute(
            f"SELECT {col} FROM users WHERE user_id = ?", (uid,))).fetchone()
        return row[col] or 0

    async def rows(uid):
        conn = await get_db()
        return [dict(r) for r in await (await conn.execute(
            "SELECT id, status, credited_troops, paid, troops_reported FROM reports "
            "WHERE user_id = ? ORDER BY id", (uid,))).fetchall()]

    ADM = 999

    # ── A. Оба за прошлые сутки, одобрены ПОЗЖЕ 10:00: 100, затем 150 ───────
    print("\nA. Прошлые сутки, одобрения позже 10:00: 100 затем 150 (больше)")
    await add_user(1, "a", "A", "Лётчик")
    r1, _ = await add_report(1, "f1", 100, 1000)
    await stamp(r1, past(15))
    a1 = await approve_report(r1, ADM)
    check("первый одобрен: выплачено 100 сразу", a1 == 100, f"={a1}")
    r2, _ = await add_report(1, "f2", 150, 1050)
    await stamp(r2, past(23))
    a2 = await approve_report(r2, ADM)
    check("второй одобрен позже: выплачено ТОЛЬКО разница 50", a2 == 50, f"={a2}")
    check("итого за сутки 150, а НЕ 250", await val(1, "troops") == 150,
          f"={await val(1, 'troops')}")
    nm = await val(1, "nordmarks") - NM0
    check("НМ = 85 + 43 = 128 (налог 15% с каждой выплаты)", nm == 128, f"={nm}")
    rr = await rows(1)
    check("оба отчёта помечены paid=1", all(r['paid'] == 1 for r in rr),
          f"{[(r['id'], r['credited_troops'], r['paid']) for r in rr]}")

    # ── B. 100 уже выплачено, второй 80 (меньше) — выплаты нет ──────────────
    print("\nB. Прошлые сутки: 100 выплачено, потом одобряют 80 (меньше)")
    await add_user(2, "b", "B", "Лётчик")
    r1, _ = await add_report(2, "f1", 100, 1000)
    await stamp(r1, past(15))
    await approve_report(r1, ADM)
    r2, _ = await add_report(2, "f2", 80, 1080)
    await stamp(r2, past(23))
    a2 = await approve_report(r2, ADM)
    check("второй: к выплате 0", a2 == 0, f"={a2}")
    check("итого осталось 100", await val(2, "troops") == 100, f"={await val(2, 'troops')}")
    nm = await val(2, "nordmarks") - NM0
    check("НМ остались от первой выплаты: 85", nm == 85, f"={nm}")

    # ── C. Оба одобрены вовремя — платит только последний снимок ─────────────
    print("\nC. Текущие сутки, оба одобрения вовремя (до 10:00)")
    await add_user(3, "c", "C", "Лётчик")
    r1, _ = await add_report(3, "f1", 100, 1000)
    await stamp(r1, cur(15))
    a1 = await approve_report(r1, ADM)
    check("первый одобрен: 100 (в момент одобрения он был последним)", a1 == 100, f"={a1}")
    r2, _ = await add_report(3, "f2", 150, 1050)
    await stamp(r2, cur(23))
    a2 = await approve_report(r2, ADM)
    check("второй одобрен: 150", a2 == 150, f"={a2}")
    res = await payout_reports()
    got = [(r['troops'], r['nordmarks']) for r in res]
    check("цикл в 10:00 платит ОДИН платёж 150, а не 100+150", got == [(150, 128)], f"={got}")
    check("итого 150", await val(3, "troops") == 150, f"={await val(3, 'troops')}")

    # ── D. Висящий PENDING не даёт циклу заплатить за сутки ─────────────────
    print("\nD. Текущие сутки: второй отчёт ещё PENDING на момент цикла")
    await add_user(4, "d", "D", "Лётчик")
    r1, _ = await add_report(4, "f1", 100, 1000)
    await stamp(r1, cur(15))
    await approve_report(r1, ADM)
    r2, _ = await add_report(4, "f2", 150, 1050)
    await stamp(r2, cur(23))
    res = await payout_reports()
    check("цикл не платит: последний не одобрен", len(res) == 0, f"res={res}")
    check("баланс 0 — сутки ждут", await val(4, "troops") == 0, f"={await val(4, 'troops')}")
    a2 = await approve_report(r2, ADM)
    check("после одобрения второго к выплате 150", a2 == 150, f"={a2}")
    check("одобрение текущих суток ждёт 10:00, баланс ещё 0",
          await val(4, "troops") == 0, f"={await val(4, 'troops')}")
    res = await payout_reports()
    check("на цикле выходит 150 одним платежом",
          [(r['troops'], r['nordmarks']) for r in res] == [(150, 128)], f"={res}")
    check("итого 150", await val(4, "troops") == 150, f"={await val(4, 'troops')}")

    # ── F. Точная копия прод-состояния «Улаги» ──────────────────────────────
    print("\nF. Прод-состояние: #1 approved/paid=0, #2 pending — одобряем #2")
    await add_user(5, "ulaga", "UlagaIvan", "Пилот")
    r1, _ = await add_report(5, "f1", 167, 1500)
    await stamp(r1, past(20, 46))
    r2, _ = await add_report(5, "f2", 212, 1712)
    await stamp(r2, past(23, 36))
    # Прод выглядит именно так: первый принят, но НЕ оплачен (10:00 суток прошло,
    # когда #2 ещё висел pending — цикл пропустил сутки), второй ждёт решения.
    conn = await get_db()
    await conn.execute(
        "UPDATE reports SET status='approved', credited_troops=167, paid=0, reviewed_by=? "
        "WHERE id=?", (ADM, r1))
    await conn.commit()
    check("баланс 0 — за сутки ещё ничего не выдано", await val(5, "troops") == 0,
          f"={await val(5, 'troops')}")
    res = await payout_reports()
    check("утренний цикл пропускает сутки (висит PENDING)", len(res) == 0, f"res={res}")

    a2 = await approve_report(r2, ADM)
    check("одобрение второго: полные 212, а НЕ 167+212=379", a2 == 212, f"={a2}")
    check("итого за сутки 212 — платится только больший снимок",
          await val(5, "troops") == 212, f"={await val(5, 'troops')}")
    nm = await val(5, "nordmarks") - NM0
    check("НМ = 181 (212 − налог 31)", nm == 181, f"={nm}")
    rr = await rows(5)
    check("первый отчёт погашен: credited=0, деньги не получил",
          rr[0]['credited_troops'] == 0 and rr[0]['paid'] == 1,
          f"credited={rr[0]['credited_troops']} paid={rr[0]['paid']}")
    check("второй отчёт оплачен", rr[1]['paid'] == 1 and rr[1]['credited_troops'] == 212,
          f"credited={rr[1]['credited_troops']} paid={rr[1]['paid']}")

    # ── F2. Тот же день, но первый отчёт успели оплатить (цикл в 10:00) ──────
    print("\nF2. Те же цифры, но #1 уже оплачен — второй должен дать разницу")
    await add_user(6, "ulaga2", "Ulaga2", "Пилот")
    r1, _ = await add_report(6, "f1", 167, 1500)
    await stamp(r1, past(20, 46))
    conn = await get_db()
    await conn.execute(
        "UPDATE reports SET status='approved', credited_troops=167, paid=1, reviewed_by=? "
        "WHERE id=?", (ADM, r1))
    await conn.execute(
        "UPDATE users SET troops = troops + 167, xp_balance = COALESCE(xp_balance,0) + 167 "
        "WHERE user_id = ?", (6,))
    await conn.commit()
    r2, _ = await add_report(6, "f2", 212, 1712)
    await stamp(r2, past(23, 36))
    a2 = await approve_report(r2, ADM)
    check("второй: только разница 212 − 167 = 45", a2 == 45, f"={a2}")
    check("итого за сутки те же 212", await val(6, 'troops') == 212,
          f"={await val(6, 'troops')}")
    rr = await rows(6)
    check("первый остался с 167, второй погашен в 0",
          rr[0]['credited_troops'] == 167 and rr[1]['credited_troops'] == 45,
          f"{[(r['id'], r['credited_troops']) for r in rr]}")

    # ── E. Повторный цикл ничего не доплачивает ─────────────────────────────
    print("\nE. Повторный запуск суточного цикла")
    before = {u: (await val(u, 'troops'), await val(u, 'nordmarks')) for u in (1, 2, 3, 4, 5, 6)}
    res = await payout_reports()
    after = {u: (await val(u, 'troops'), await val(u, 'nordmarks')) for u in (1, 2, 3, 4, 5, 6)}
    check("цикл ничего не выдал", len(res) == 0, f"res={res}")
    check("балансы всех пилотов не изменились", before == after, f"{before} -> {after}")

    await close_db()
    ok = not FAILED
    print("\n" + ("ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ" if ok else f"ПРОВАЛЕНО ({len(FAILED)}): {FAILED}"))
    for suffix in ("", "-wal", "-shm"):
        try:
            os.remove(DB_PATH + suffix)
        except OSError:
            pass
    sys.exit(0 if ok else 1)


asyncio.run(main())
