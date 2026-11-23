"""Smoke v0.43.28: догон суточного цикла после рестарта.

Проверяет:
1. _run_daily_core: при успехе ставит отметку игровых суток (daily_core_day).
2. При ошибке восстановления ОД отметку не ставит (догон повторится при следующем старте).
3. Догон до 10:00 МСК не запускается.
4. Догон после 10:00 МСК запускается, если сутки не отмечены.
5. Повторный догон в те же сутки ничего не делает (нет повторной выплаты).

Запуск: .venv\\Scripts\\python.exe smoke_242.py
"""
import asyncio
import os
import sys
from datetime import datetime, timedelta, timezone

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke242.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB
os.environ["ADMIN_IDS"] = "442001"

sys.path.insert(0, os.path.dirname(__file__))

MSK = timezone(timedelta(hours=3))


class FakeBot:
    def __init__(self):
        self.sent = []

    async def send_message(self, chat_id, text, **kw):
        self.sent.append((chat_id, text))


async def run():
    import main as M
    from database.db import init_db, close_db, get_setting, set_setting, today_report_day

    await init_db()
    passed = failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
        else:
            failed += 1
            print(f"  FAIL: {name}")

    calls = {"ap": 0, "payout": 0}
    fail_ap = {"on": False}

    async def fake_ap():
        calls["ap"] += 1
        if fail_ap["on"]:
            raise RuntimeError("boom")

    async def fake_payout():
        calls["payout"] += 1
        return []

    real_ap, real_payout = M.daily_ap_recovery, M.payout_reports
    M.daily_ap_recovery = fake_ap
    M.payout_reports = fake_payout
    bot = FakeBot()
    try:
        await set_setting(M.CORE_DAY_SETTING, "2000-01-01")

        ok = await M._run_daily_core(bot, "тест")
        check("успешный цикл возвращает True", ok is True)
        check("отметка суток записана", await get_setting(M.CORE_DAY_SETTING) == today_report_day())
        check("ОД и отчёты вызваны по разу", calls == {"ap": 1, "payout": 1})

        # 3. До 10:00 МСК догон не запускается
        await set_setting(M.CORE_DAY_SETTING, "2000-01-01")
        early = datetime.now(MSK).replace(hour=9, minute=0, second=0, microsecond=0)
        ran = await M._catchup_daily_core(bot, now=early)
        check("до 10:00 МСК догон не запускается", ran is False)
        check("до 10:00 ОД не трогали", calls["ap"] == 1)

        # 4. После 10:00 МСК, сутки не отмечены — догон запускается
        late = datetime.now(MSK).replace(hour=23, minute=0, second=0, microsecond=0)
        ran = await M._catchup_daily_core(bot, now=late)
        check("после 10:00 МСК догон запускается", ran is True)
        check("догон вызвал ОД и отчёты", calls == {"ap": 2, "payout": 2})
        check("после догона сутки отмечены", await get_setting(M.CORE_DAY_SETTING) == today_report_day())

        # 5. Повторный старт в те же сутки — ничего не делает
        ran = await M._catchup_daily_core(bot, now=late)
        check("повторный догон в те же сутки не запускается", ran is False)
        check("повторно ОД и отчёты не вызывались", calls == {"ap": 2, "payout": 2})

        # 2. Ошибка восстановления ОД — отметку не ставим
        await set_setting(M.CORE_DAY_SETTING, "2000-01-01")
        fail_ap["on"] = True
        ok = await M._run_daily_core(bot, "тест с ошибкой")
        check("при ошибке ОД возвращает False", ok is False)
        check("при ошибке отметка не ставится", await get_setting(M.CORE_DAY_SETTING) == "2000-01-01")
    finally:
        M.daily_ap_recovery = real_ap
        M.payout_reports = real_payout
        await close_db()
        if os.path.exists(_TEST_DB):
            os.remove(_TEST_DB)

    print(f"\nSmoke 242: {passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)


asyncio.run(run())
