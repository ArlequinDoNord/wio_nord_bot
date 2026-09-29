"""Smoke v0.18.8: состав боевого формирования — фарм пилотов крыла за сутки.

Командир/заместитель крыла в штабе ВВС видит по каждому пилоту своего крыла:
фарм за прошлые отчётные сутки и фарм за текущие (только уже одобренное).
Проверяем саму выборку wing_members_report_farms:
  • прошлые сутки считаются по границе 10:00 МСК (отчёт за 09:00 МСК — «вчера»);
  • текущие показывают только ПРИНЯТЫЕ отчёты (pending/rejected в цифру не идут);
  • пилоты других крыльев не подмешиваются; пустое крыло — пустой список;
  • кнопка «Состав формирования» появляется в меню штаба только с правом.

Запуск: .venv\\Scripts\\python.exe smoke_100.py
"""
import asyncio
import os
import shutil
import sys
import tempfile
from datetime import timedelta, timezone

WORK = tempfile.mkdtemp(prefix="sm100_")
os.environ["DATABASE_PATH"] = os.path.join(WORK, "t.db")
sys.path.insert(0, os.path.dirname(__file__))

from database import db as D


def check(name, cond):
    print(("  ok   " if cond else "  FAIL ") + name)
    if not cond:
        FAILED.append(name)


FAILED = []


async def _insert(uid, troops, created_utc, status="approved", credited=None, paid=1, region="1"):
    """Отчёт напрямую в БД (как smoke_089): статуc, засчитанное и оплата задаются явно."""
    conn = await D.get_db()
    await conn.execute(
        "INSERT INTO reports (user_id, screenshot_file_id, troops_reported, total_troops, "
        "region, credited_troops, status, paid, created_at) "
        "VALUES (?, 'f', ?, ?, ?, ?, ?, ?, ?)",
        (uid, troops, troops, region, credited if credited is not None else troops,
         status, paid, created_utc)
    )
    await conn.commit()


async def main():
    await D.init_db()

    # Звенья из будущего: 4 пилота в «1» (Омега — для регионов) и 1 в «2» — чужие не должны попадать.
    for uid, name in ((101, "Альфа"), (102, "Бета"), (103, "Гамма"), (104, "Омега"), (201, "Дельта")):
        await D.add_user(uid, f"wing{uid}", name, "Тестов")
    await D.set_wing(101, "1")
    await D.set_wing(102, "1")
    await D.set_wing(103, "1")
    await D.set_wing(104, "1")
    await D.set_wing(201, "2")

    db = await D.get_db()
    await db.execute("UPDATE users SET troops = ? WHERE user_id = ?", (1234, 101))
    await db.commit()

    start, _end = D.report_day_bounds()  # начало текущих отчётных суток в МСК
    prev_ts = (start - timedelta(hours=1)).astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    today_ts = (start + timedelta(hours=2)).astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    check("метки «вчера» и «сегодня» не совпали",
          prev_ts != today_ts
          and D.report_day_value_of(prev_ts) != D.report_day_value_of(today_ts))

    farms = await D.wing_members_report_farms("3")
    check("пустое крыло — пустой список", farms == [])

    # Альфа: 300 принято вчера + 200 принято сегодня + 999 висит сегодня + 400 отклонено сегодня
    await _insert(101, 300, prev_ts)
    await _insert(101, 200, today_ts)
    await _insert(101, 999, today_ts, status="pending", paid=0)
    await _insert(101, 400, today_ts, status="rejected", paid=0)
    # Бета: 150 принято вчера, сегодня — только висящий отчёт
    await _insert(102, 150, prev_ts)
    await _insert(102, 500, today_ts, status="pending", paid=0)
    # Гамма: отчётов не сдавал
    # Омега: принятый отчёт сегодня в регионе «3» (его регион последнего отчёта)
    await _insert(104, 250, today_ts, region="3")
    # Дельта (крыло 2): 770 вчера — чужая выписка не должна попасть в «1»

    await _insert(201, 770, prev_ts)

    farms = {f["user_id"]: f for f in await D.wing_members_report_farms("1")}
    check("крыло 1: четыре пилота", set(farms) == {101, 102, 103, 104})

    a = farms[101]
    check("Альфа: вчера 300", a["prev_farm"] == 300)
    check("Альфа: сегодня 200 (pending и rejected не считаются)", a["today_farm"] == 200)
    check("Альфа: регион последнего отчёта '1'", a["region"] == "1")
    check("Альфа: troops берутся из users (1234)", a["troops"] == 1234)

    b = farms[102]
    check("Бета: вчера 150", b["prev_farm"] == 150)
    check("Бета: сегодня 0 (отчёт ещё на проверке)", b["today_farm"] == 0)

    g = farms[103]
    check("Гамма без отчётов: 0 / 0", g["prev_farm"] == 0 and g["today_farm"] == 0)
    check("Гамма без отчётов: региона нет", g["region"] is None)

    o = farms[104]
    check("Омега: регион из последнего ПРИНЯТОГО отчёта '3'", o["region"] == "3")

    other = await D.wing_members_report_farms("2")
    check("Дельта в крыле 2: вчера 770", other and other[0]["user_id"] == 201 and other[0]["prev_farm"] == 770)
    check("крыло 2: дельта одна", len(other) == 1)

    # Чужой пилот не просочился в крыло 1
    check("чужие пилоты не подмешаны",
          all(u["user_id"] != 201 for u in await D.wing_members_report_farms("1")))

    # Кнопка «Состав формирования» в меню штаба — по праву командира/заместителя
    from bot.handlers.hq import hq_menu_markup
    m = hq_menu_markup(wing_farm_ok=True)
    labels = [b.text for row in m.inline_keyboard for b in row]
    check("кнопка «Состав формирования» есть с правом", "🪽 Состав формирования" in labels)
    m0 = hq_menu_markup(wing_farm_ok=False)
    labels0 = [b.text for row in m0.inline_keyboard for b in row]
    check("кнопки нет без права", "🪽 Состав формирования" not in labels0)

    await D.close_db()
    shutil.rmtree(WORK, ignore_errors=True)
    total = len(FAILED)
    print("\nSmoke 100: " + ("all passed" if not total else f"{total} failed"))
    sys.exit(1 if FAILED else 0)


asyncio.run(main())