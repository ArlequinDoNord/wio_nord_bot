"""Smoke v0.18.5: цикл в 05:05, выравнивание опыта, похвала по дню отчёта, отчёты.

Проверяем:
  • однократный бэкфилл xp_balance = troops (после него значения равны, повторно
    цикл не выравнивает);
  • похвала в общий чат по дню САМОГО отчёта: отчёт за вчера (отчётные сутки
    вчерашние), одобренный сегодня, раньше давал 0 и молчал — теперь отправляется;
  • дедуп похвалы за сутки и запись уровня;
  • get_approved_reports / count_approved_reports (метки оплаченности);
  • архив стены изречений: только суперадмин (ADMIN_IDS) и читательский билет,
    корреспондент ГосСМИ больше не проходит.

Запуск: .venv\\Scripts\\python.exe smoke_099.py
"""
import asyncio
import os
import sys

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke099.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB

sys.path.insert(0, os.path.dirname(__file__))


class FakeBot:
    def __init__(self):
        self.sent = []

    async def send_message(self, chat_id, text, **kwargs):
        self.sent.append((chat_id, text))
        return None


async def run():
    from database.db import (
        init_db, close_db, get_db, add_user, get_user,
        set_news_chat, report_day_value_of,
        report_day_credited_total, get_report_notify_tier,
        get_approved_reports, count_approved_reports, get_pending_reports,
        has_library_access,
    )
    from bot.handlers.wall import _archive_allowed
    from utils.notify import notify_report_praise
    from config import ADMIN_IDS

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

    U1 = 98101  # пилот с большим ночным отчётом
    U2 = 98102  # пилот с отчётом ниже порога
    JORE = 98103  # журналист ГосСМИ (без билета)
    TICK = 98104  # владелец читательского билета
    NOONE = 98105  # случайный без прав

    await add_user(U1, "ace_pilot", "Ас", "")
    await add_user(U2, "small_pilot", "Малыш", "")
    await add_user(JORE, "journalist", "Журналист", "")
    await add_user(TICK, "reader", "Читатель", "")
    await add_user(NOONE, "nobody", "Никто", "")

    await set_news_chat(-100777, 42)

    # ── 1. Бэкфилл накопительного опыта ──
    # Напрочь: игрок «накопил» войска до появления поля (xp_balance = 0).
    conn = await get_db()
    await conn.execute("UPDATE users SET troops = 190, xp_balance = 0 WHERE user_id = ?", (U1,))
    await conn.execute("DELETE FROM settings WHERE key = 'xp_backfill_v0185'")
    await conn.commit()
    await init_db()  # повторный запуск = рестарт бота/деплой
    u = await get_user(U1)
    check("бэкфилл: xp_balance = troops (190)", u['xp_balance'] == 190)
    # Повторный старт НЕ должен выравнивать снова: расхождение становится законным,
    # когда появится трата опыта.
    await conn.execute("UPDATE users SET xp_balance = 5 WHERE user_id = ?", (U1,))
    await conn.commit()
    await init_db()
    u = await get_user(U1)
    check("повторный старт не пере-выравнивает", u['xp_balance'] == 5)

    # ── 2. День отчёта (report_day_value_of) ──
    check("день ночного отчёта (21:46 UTC) = вчера (28.09)",
          report_day_value_of("2026-09-28 21:46:41") == "2026-09-28")
    check("сегодняшний отчёт (06:11 UTC) = 29.09",
          report_day_value_of("2026-09-29 06:11:22") == "2026-09-29")
    check("мусор даёт None", report_day_value_of("не дата") is None)

    # ── 3. Похвала по дню отчёта, а не по дню одобрения ──
    # Пилот сдал ночью (отчётные сутки 28.09), админ одобряет завтра. Без дня —
    # «сегодняшняя» сумма 0 → тишина. С днём 28.09 — сумма 160 → мастерство.
    await conn.execute(
        "INSERT INTO reports (user_id, screenshot_file_id, troops_reported, "
        "total_troops, credited_troops, region, status, paid, created_at) "
        "VALUES (?, '', 160, 160, 160, '25', 'approved', 1, '2026-09-28 23:10:00')",
        (U1,))
    await conn.commit()

    bot = FakeBot()
    pilot = await get_user(U1)
    # Старое поведение (без дня): сегодня уже другие сутки — сумма за сегодня 0.
    ok_old = await notify_report_praise(bot, pilot, U1)
    check("похвала БЕЗ дня отчёта молчит (сумма за сегодня 0)", ok_old is False and not bot.sent)
    ok_new = await notify_report_praise(bot, pilot, U1, day="2026-09-28")
    check("похвала С днём отчёта отправляется",
          ok_new is True and any("мастерство" in t for _, t in bot.sent))
    check("уровень за сутки запомнен",
          await get_report_notify_tier(U1, day="2026-09-28") == 1)
    ok_again = await notify_report_praise(bot, pilot, U1, day="2026-09-28")
    check("повтор · за те же сутки молчит", ok_again is False)

    # ── 4. Сумма за день видна по тем же отчётным суткам ──
    check("report_day_credited_total по дню = 160", await report_day_credited_total(U1, day="2026-09-28") == 160)
    check("report_day_credited_total сегодня = 0 (отчёт за вчера)", await report_day_credited_total(U1) == 0)

    # ── 5. Принятые отчёты и метки оплаченности ──
    await conn.execute(
        "INSERT INTO reports (user_id, screenshot_file_id, troops_reported, "
        "total_troops, credited_troops, region, status, paid, created_at) "
        "VALUES (?, '', 200, 200, 200, '25', 'approved', 0, '2026-09-29 01:00:00')",
        (U1,))
    await conn.commit()
    done = await get_approved_reports(10)
    check("get_approved_reports: 2 принятых", len(done) == 2)
    check("отсортированы свежие сверху", done[0]['created_at'] > done[1]['created_at'])
    row = done[0]
    check("у принятого есть paid", row['paid'] in (0, 1))
    check("всего принятых 2", await count_approved_reports() == 2)
    check("не оплачен среди них 1", await count_approved_reports(unpaid_only=True) == 1)
    check("в очереди никого", await get_pending_reports() == [])

    # ── 6. Архив стены: только суперадмин и билет ──
    from database.db import activate_library_card
    await activate_library_card(TICK, "basic", days=30)
    conn = await get_db()
    await conn.execute(
        "INSERT INTO user_roles (telegram_id, role, granted_by) VALUES (?, 'journalist', ?)",
        (JORE, 1))
    await conn.commit()
    check("суперадмин (ADMIN_IDS) имеет доступ",
          not ADMIN_IDS or await _archive_allowed(ADMIN_IDS[0]) is True)
    check("корреспондент ГосСМИ больше НЕ проходит",
          await _archive_allowed(JORE) is False)
    check("читательский билет даёт доступ", await _archive_allowed(TICK) is True)
    check("без прав — отказ", await _archive_allowed(NOONE) is False)

    await close_db()
    print(f"\nSmoke 099: {passed} passed, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    async def _main():
        try:
            return await run()
        finally:
            from database.db import close_db
            await close_db()

    sys.exit(asyncio.run(_main()))