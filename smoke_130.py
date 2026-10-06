"""Smoke 130 — ВСЕ суточные лимиты живут по игровым суткам 10:00 МСК (v0.22.8).

Раньше сутки были в трёх разных зонах: ОД/расходники/алкоголь/фонтан — по UTC
(смена в 03:00 МСК), рыба/лес/стена/опросы/речи — по МСК (смена в 00:00 МСК),
отчёты — как и положено, с 10:00 МСК. Пилот за день ловил два сброса лимитов и
три разные границы «сегодня».

Проверяется:
1. Ключи-функции (рыба/лес, стена, опросы, речи) возвращают today_report_day().
2. Граница 10:00 МСК на произвольных метках — Python и SQL дают одно и то же,
   включая коварный случай «UTC-день уже новый, а игровые сутки ещё старые».
3. Суточный цикл обнуляет ВСЕ счётчики (раньше 4 из 9) и сбрасывает спец-отдел.
4. Счётчик, взятый ВНУТРИ суток, циклом не затирается.
5. Фонтан считает по ключу, а не по календарю.
6. НИИ и новости считают через _report_day, а не через substr/date от календаря.
7. Нормализация «опережающих» ключей при старте не теряет счётчик.

Запуск: .venv\\Scripts\\python.exe smoke_130.py
"""
import asyncio
import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

FAILED = []


def check(name, cond, extra=""):
    print(("  ok   " if cond else "  FAIL ") + name + (f"   [{extra}]" if extra else ""))
    if not cond:
        FAILED.append(name)


async def main():
    import config
    DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_test_smoke130.db")
    for suffix in ("", "-wal", "-shm"):
        try:
            os.remove(DB_PATH + suffix)
        except OSError:
            pass
    config.DB_PATH = DB_PATH

    import database.db as db
    db.DB_PATH = DB_PATH
    from database.db import (
        init_db, close_db, get_db, add_user, add_nii_report,
        today_report_day, shift_report_day, report_day_value_of, _report_day,
        fish_sold_day_key, _wall_today_key, _poll_today_key, _rep_speech_today_key,
        daily_ap_recovery, _normalize_daily_keys, can_use_fountain, mark_fountain_used,
        count_nii_reports_today, get_news_count_today,
    )
    from utils.helpers import MOSCOW_TZ

    await init_db()

    today = today_report_day()
    yesterday = shift_report_day(today, -1)
    conn = await get_db()

    # ── 1. Все ключи-функции → единый игровой день ──
    print("\n1. Единый ключ игровых суток")
    check("fish_sold_day_key == today_report_day", fish_sold_day_key() == today,
          f"{fish_sold_day_key()}")
    check("_wall_today_key == today_report_day", _wall_today_key() == today,
          f"{_wall_today_key()}")
    check("_poll_today_key == today_report_day", _poll_today_key() == today,
          f"{_poll_today_key()}")
    check("_rep_speech_today_key == today_report_day", _rep_speech_today_key() == today,
          f"{_rep_speech_today_key()}")

    # ── 2. Граница 10:00 МСК (created_at хранится в UTC) ──
    print("\n2. Граница 10:00 МСК")
    check("06:59:59 UTC = 09:59 МСК → прошлые сутки",
          report_day_value_of("2026-10-06 06:59:59") == "2026-10-05")
    check("07:00:00 UTC = 10:00 МСК → текущие сутки",
          report_day_value_of("2026-10-06 07:00:00") == "2026-10-06")
    check("01:00 UTC = 04:00 МСК (календарь UTC уже новый) → прошлые сутки",
          report_day_value_of("2026-10-06 01:00:00") == "2026-10-05")
    check("23:59 UTC = 02:59 МСК следующего дня → сутки этого числа",
          report_day_value_of("2026-10-06 23:59:59") == "2026-10-06")

    for ts, exp in (("2026-10-06 06:59:59", "2026-10-05"),
                    ("2026-10-06 07:00:00", "2026-10-06"),
                    ("2026-10-06 01:00:00", "2026-10-05"),
                    ("2026-10-06 23:59:59", "2026-10-06")):
        row = await (await conn.execute(
            f"SELECT {_report_day('?')} AS d", (ts,))).fetchone()
        check(f"SQL _report_day({ts}) == Python", row['d'] == exp, f"{row['d']} vs {exp}")

    # ── 3. Суточный цикл обнуляет ВСЕ счётчики ──
    print("\n3. Сброс всех счётчиков в 10:00")
    U1 = 130001
    await add_user(U1, "u130001", "Т1", "")
    old = "2000-01-01"
    await conn.execute("""
        UPDATE users SET
            ap_recovery_day = ?, ap = 10,
            ap_restored_day = ?, ap_restored_today = 50,
            seaweed_used_day = ?, seaweed_used_today = 2,
            fountain_used_day = ?, fountain_used_today = 1,
            fish_sold_day = ?, fish_sold_today = 100,
            forest_sold_day = ?, forest_sold_today = 7,
            alcohol_weak_used_day = ?, alcohol_weak_used_today = 3,
            alcohol_strong_used_day = ?, alcohol_strong_used_today = 1,
            special_fails_today = 2
        WHERE user_id = ?
    """, (old, old, old, old, old, old, old, old, U1))
    await conn.commit()

    await daily_ap_recovery()
    row = await (await conn.execute(
        "SELECT * FROM users WHERE user_id = ?", (U1,))).fetchone()
    cols_today = ("ap_restored_today", "seaweed_used_today", "fountain_used_today",
                  "fish_sold_today", "forest_sold_today",
                  "alcohol_weak_used_today", "alcohol_strong_used_today",
                  "special_fails_today")
    for col in cols_today:
        check(f"{col} обнулён", (row[col] or 0) == 0, f"{row[col]}")
    cols_day = ("ap_recovery_day", "ap_restored_day", "seaweed_used_day",
                "fountain_used_day", "fish_sold_day", "forest_sold_day",
                "alcohol_weak_used_day", "alcohol_strong_used_day")
    for col in cols_day:
        check(f"{col} = игровой день", row[col] == today, f"{row[col]} vs {today}")
    check("суточное ОД начислено (10→110)", row['ap'] == 110, f"{row['ap']}")

    # ── 4. Внутри суток счётчик цикл не затирает ──
    print("\n4. Счётчик внутри суток")
    U2 = 130002
    await add_user(U2, "u130002", "Т2", "")
    await conn.execute("""
        UPDATE users SET
            ap_recovery_day = ?, ap = 5,
            ap_restored_day = ?, ap_restored_today = 42,
            seaweed_used_day = ?, seaweed_used_today = 5,
            fountain_used_day = ?, fountain_used_today = 1,
            fish_sold_day = ?, fish_sold_today = 33,
            forest_sold_day = ?, forest_sold_today = 4,
            alcohol_weak_used_day = ?, alcohol_weak_used_today = 2,
            alcohol_strong_used_day = ?, alcohol_strong_used_today = 1,
            special_fails_today = 2
        WHERE user_id = ?
    """, (today, today, today, today, today, today, today, today, U2))
    await conn.commit()

    await daily_ap_recovery()
    row2 = await (await conn.execute(
        "SELECT * FROM users WHERE user_id = ?", (U2,))).fetchone()
    for col, exp in (("ap_restored_today", 42), ("seaweed_used_today", 5),
                     ("fountain_used_today", 1), ("fish_sold_today", 33),
                     ("forest_sold_today", 4), ("alcohol_weak_used_today", 2),
                     ("alcohol_strong_used_today", 1)):
        check(f"{col} сохранён внутри суток", (row2[col] or 0) == exp,
              f"{row2[col]} vs {exp}")
    check("ОД не начислены повторно (guard)", row2['ap'] == 5, f"{row2['ap']}")
    check("спец-отдел: счётчик ошибок сброшен в 10:00",
          (row2['special_fails_today'] or 0) == 0, f"{row2['special_fails_today']}")

    # ── 5. Фонтан ──
    print("\n5. Фонтан")
    U3 = 130003
    await add_user(U3, "u130003", "Т3", "")
    await conn.execute(
        "UPDATE users SET fountain_used_day = ?, fountain_used_today = 1 WHERE user_id = ?",
        (today, U3))
    await conn.commit()
    check("сегодня уже пил → нельзя", not await can_use_fountain(U3))
    await conn.execute(
        "UPDATE users SET fountain_used_day = ?, fountain_used_today = 1 WHERE user_id = ?",
        (yesterday, U3))
    await conn.commit()
    check("вчера пил → можно", await can_use_fountain(U3))
    await mark_fountain_used(U3)
    row3 = await (await conn.execute(
        "SELECT fountain_used_day, fountain_used_today FROM users WHERE user_id = ?",
        (U3,))).fetchone()
    check("после глотка: день = игровой, счёт = 1",
          row3['fountain_used_day'] == today and row3['fountain_used_today'] == 1,
          f"{row3['fountain_used_day']} {row3['fountain_used_today']}")

    # ── 6. НИИ и новости считаются через _report_day ──
    print("\n6. НИИ / новости")
    U4 = 130004
    await add_user(U4, "u130004", "Т4", "")
    await add_nii_report(U4, "тестовое обращение")
    check("обращение «сейчас» входит в текущие сутки",
          await count_nii_reports_today(U4) == 1, f"{await count_nii_reports_today(U4)}")

    msk_now = datetime.now(MOSCOW_TZ)
    morning = msk_now.replace(hour=8, minute=0, second=0, microsecond=0)
    evening = msk_now.replace(hour=11, minute=0, second=0, microsecond=0)
    m_utc = (morning - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S")
    e_utc = (evening - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S")
    check("08:00 и 11:00 МСК одного числа — РАЗНЫЕ игровые сутки",
          report_day_value_of(m_utc) != report_day_value_of(e_utc),
          f"{report_day_value_of(m_utc)} / {report_day_value_of(e_utc)}")
    check("ровно один из двух интервалов — текущие сутки",
          (1 if report_day_value_of(m_utc) == today else 0)
          + (1 if report_day_value_of(e_utc) == today else 0) == 1,
          f"утро={report_day_value_of(m_utc)}, день={report_day_value_of(e_utc)}, "
          f"сегодня={today}")

    # Вставляем строки с заданным временем: add_nii_report всегда пишет «сейчас».
    async def nii_at(uid, text, when_msk):
        await conn.execute(
            "INSERT INTO nii_reports (user_id, text, photo_file_id, status, created_at) "
            "VALUES (?, ?, NULL, 'open', ?)", (uid, text, when_msk.isoformat()))
        await conn.commit()

    U5 = 130005
    await add_user(U5, "u130005", "Т5", "")
    await nii_at(U5, "утреннее (08:00 МСК)", morning)
    morn_cnt = await count_nii_reports_today(U5)
    exp_morn = 1 if report_day_value_of(m_utc) == today else 0
    check("утренняя строка считается по игровому дню", morn_cnt == exp_morn,
          f"{morn_cnt} vs {exp_morn}")

    U6 = 130006
    await add_user(U6, "u130006", "Т6", "")
    await nii_at(U6, "дневное (11:00 МСК)", evening)
    day_cnt = await count_nii_reports_today(U6)
    exp_day = 1 if report_day_value_of(e_utc) == today else 0
    check("дневная строка считается по игровому дню", day_cnt == exp_day,
          f"{day_cnt} vs {exp_day}")

    # Новости: created_at хранится МСК-isoformat, правило то же
    U7 = 130007
    await add_user(U7, "u130007", "Т7", "")
    for tag, when in (("утро", morning), ("день", evening)):
        await conn.execute(
            "INSERT INTO news_releases (title, body, photo_file_id, author_id, "
            "author_name, created_at) VALUES (?, ?, NULL, ?, ?, ?)",
            (f"Выпуск {tag}", "текст", U7, "Т7", when.isoformat()))
    await conn.commit()
    news_cnt = await get_news_count_today(U7)
    exp_news = (1 if report_day_value_of(m_utc) == today else 0) + \
               (1 if report_day_value_of(e_utc) == today else 0)
    check("новости считаются по игровому дню (ровно 1 из 2)",
          news_cnt == exp_news == 1, f"{news_cnt} vs {exp_news}")

    # ── 7. Нормализация «опережающих» ключей ──
    print("\n7. Нормализация при старте")
    U8 = 130008
    await add_user(U8, "u130008", "Т8", "")
    future = shift_report_day(today, 1)
    await conn.execute(
        "UPDATE users SET ap_restored_day = ?, ap_restored_today = 60, "
        "ap_recovery_day = ? WHERE user_id = ?",
        (future, future, U8))
    await conn.commit()
    await _normalize_daily_keys()
    row8 = await (await conn.execute(
        "SELECT ap_restored_day, ap_restored_today, ap_recovery_day "
        "FROM users WHERE user_id = ?", (U8,))).fetchone()
    check("будущий ключ прижат к игровому дню",
          row8['ap_restored_day'] == today and row8['ap_recovery_day'] == today,
          f"{row8['ap_restored_day']} {row8['ap_recovery_day']}")
    check("счётчик при этом сохранился", row8['ap_restored_today'] == 60,
          f"{row8['ap_restored_today']}")

    await close_db()
    print(f"\nSmoke 130: {len(FAILED)} провалено" if FAILED else "\nВСЕ ПРОВЕРКИ ПРОЙДЕНЫ")
    if FAILED:
        print(FAILED)
    sys.exit(1 if FAILED else 0)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except SystemExit:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"SMOKE ERROR: {e!r}")
        try:
            from database.db import close_db
            asyncio.run(close_db())
        except Exception:
            pass
        sys.exit(1)
