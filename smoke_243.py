"""Smoke v0.43.29: опыт за обычные активности (звание + xp_balance).

Проверяет:
1. Начисление пишет одновременно в troops и xp_balance, суточный учёт — в activity_xp_daily.
2. Суточный лимит ACTIVITY_XP_DAILY_CAP режет начисление, сообщение о лимите один раз.
3. Потолок MAX_SELF_RANK_TROOPS: остаток до 4040 режет начисление, сверх — ничего.
4. Туристам опыт не начисляется, сообщений нет.
5. Строки «+N XP» и «Лимит усвоения опыта достигнут» на ru и en.

Запуск: .venv\\Scripts\\python.exe smoke_243.py
"""
import asyncio
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke243.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB
os.environ["ADMIN_IDS"] = "443001"

sys.path.insert(0, os.path.dirname(__file__))

PILOT, PILOT_CAP, PILOT_NEAR, TOURIST, PILOT_EN = 880001, 880002, 880003, 880004, 880005


async def run():
    from database.db import (init_db, close_db, get_db, add_user, update_user, get_user,
                             grant_activity_xp, get_status_by_tag, grant_status)
    from utils.activity_xp import activity_xp_line
    from utils.localization import use_lang

    await init_db()
    passed = failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
        else:
            failed += 1
            print(f"  FAIL: {name}")

    async def reset_today(uid):
        conn = await get_db()
        await conn.execute("DELETE FROM activity_xp_daily WHERE user_id = ?", (uid,))
        await conn.commit()

    try:
        for uid in (PILOT, PILOT_CAP, PILOT_NEAR, PILOT_EN):
            await add_user(uid, f"act{uid}", "Пилот", "Тест")
        await add_user(TOURIST, "act_t", "Турист", "Тест")
        tourist_st = await get_status_by_tag("tourist")
        if tourist_st:
            await grant_status(TOURIST, tourist_st["id"], 0)

        # 1. Обычное начисление: troops и xp_balance одинаково
        r = await grant_activity_xp(PILOT, 4)
        u = await get_user(PILOT)
        check("начисление 4 ок", r == {'granted': 4, 'limit_hit': False})
        check("troops +4", u['troops'] == 4)
        check("xp_balance +4", u['xp_balance'] == 4)

        # 2. Суточный лимит 50: ещё 60 → выдаём 46, сообщение о лимите
        r = await grant_activity_xp(PILOT, 60)
        check("до лимита выдано 46", r['granted'] == 46)
        check("сообщение о лимите при первом упоре", r['limit_hit'] is True)
        u = await get_user(PILOT)
        check("troops после лимита = 50", u['troops'] == 50)
        r = await grant_activity_xp(PILOT, 4)
        check("сверх лимита ничего не выдано", r['granted'] == 0)
        check("сообщение о лимите не повторяется в тот же день", r['limit_hit'] is False)

        # 3. Потолок звания: остаток до 4040 режет начисление
        await reset_today(PILOT_CAP)
        await update_user(PILOT_CAP, troops=4030, xp_balance=4030)
        r = await grant_activity_xp(PILOT_CAP, 50)
        check("у порога 4030 выдано только 10", r['granted'] == 10)
        check("у порога сообщение о лимите", r['limit_hit'] is True)
        u = await get_user(PILOT_CAP)
        check("troops ровно 4040", u['troops'] == 4040)
        check("xp_balance ровно 4040", u['xp_balance'] == 4040)
        await reset_today(PILOT_CAP)
        r = await grant_activity_xp(PILOT_CAP, 5)
        check("на пороге 4040 опыт не растёт", r['granted'] == 0)
        check("на пороге после сброса суточного учёта сообщение снова одно", r['limit_hit'] is True)
        r = await grant_activity_xp(PILOT_CAP, 5)
        check("и больше не повторяется", r['limit_hit'] is False)

        # 4. Турист: ничего не начисляется
        r = await grant_activity_xp(TOURIST, 4)
        ut = await get_user(TOURIST)
        check("турист: ничего не выдано", r == {'granted': 0, 'limit_hit': False})
        check("турист: troops не изменились", (ut['troops'] or 0) == 0)

        # 5. Тексты ru/en
        await update_user(PILOT_EN, troops=0, xp_balance=0)
        line = await activity_xp_line(PILOT_EN, 4)
        check("ru: строка «+4 XP»", "+4 XP" in line)
        await update_user(PILOT_EN, troops=4040)
        await reset_today(PILOT_EN)
        line = await activity_xp_line(PILOT_EN, 4)
        check("ru: строка лимита", "Лимит усвоения опыта достигнут." in line)
        use_lang("en")
        try:
            await reset_today(PILOT_EN)
            line = await activity_xp_line(PILOT_EN, 4)
            check("en: строка лимита", "Experience intake limit reached." in line)
        finally:
            use_lang("ru")
    finally:
        await close_db()
        if os.path.exists(_TEST_DB):
            os.remove(_TEST_DB)

    print(f"\nSmoke 243: {passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)


asyncio.run(run())
