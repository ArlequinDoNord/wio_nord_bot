"""Smoke v0.43.29: лёгкие и сильные активности, опыт за полевых зверей.

Проверяет:
1. До Старшего Сержанта лёгкие действия (руда, грибы, рыба) дают опыт.
2. С Старшего Сержанта лёгкие действия опыт не дают (без сообщения о лимите).
3. С Старшего Сержанта сильные действия (рубка, враги подземелья, кабан) опыт дают.
4. Таблица ACTIVITY_XP_BEASTS: кабан сильный, летучая мышь и змея лёгкие.
5. Строка опыта за зверя в ru: «+2 XP» для медведя.

Запуск: .venv\\Scripts\\python.exe smoke_244.py
"""
import asyncio
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke244.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB
os.environ["ADMIN_IDS"] = "444001"

sys.path.insert(0, os.path.dirname(__file__))

NOVICE, SENIOR, LIGHT_OK = 881001, 881002, 881003


async def run():
    from database.db import init_db, close_db, add_user, update_user, get_user, grant_activity_xp
    from utils.activity_xp import beast_xp_line
    from config import ACTIVITY_XP_BEASTS

    await init_db()
    passed = failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
        else:
            failed += 1
            print(f"  FAIL: {name}")

    try:
        for uid in (NOVICE, SENIOR, LIGHT_OK):
            await add_user(uid, f"lgt{uid}", "Пилот", "Тест")

        # 1. До Старшего Сержанта лёгкое даёт опыт
        await update_user(NOVICE, troops=1000, xp_balance=1000)
        r = await grant_activity_xp(NOVICE, 2, light=True)
        check("Сержант: лёгкое даёт опыт", r['granted'] == 2)

        # 2. С Старшего Сержанта лёгкое не даёт, сообщения нет
        await update_user(SENIOR, troops=1500, xp_balance=1500)
        r = await grant_activity_xp(SENIOR, 2, light=True)
        u = await get_user(SENIOR)
        check("Старший Сержант: лёгкое не даёт опыт", r == {'granted': 0, 'limit_hit': False})
        check("Старший Сержант: troops не изменились", u['troops'] == 1500)

        # 3. С Старшего Сержанта сильное даёт опыт
        r = await grant_activity_xp(SENIOR, 2, light=False)
        u = await get_user(SENIOR)
        check("Старший Сержант: сильное даёт опыт", r['granted'] == 2)
        check("Старший Сержант: troops +2", u['troops'] == 1502)
        check("Старший Сержант: xp_balance +2", u['xp_balance'] == 1502)

        # 4. Таблица зверей
        check("кабан сильный", ACTIVITY_XP_BEASTS["boar"] == (1, False))
        check("медведь сильный, 2 XP", ACTIVITY_XP_BEASTS["bear"] == (2, False))
        check("летучая мышь лёгкая", ACTIVITY_XP_BEASTS["bat"][1] is True)
        check("змея лёгкая", ACTIVITY_XP_BEASTS["snake"][1] is True)

        # 5. Строка опыта за медведя (ru)
        await update_user(LIGHT_OK, troops=0, xp_balance=0)
        line = await beast_xp_line(LIGHT_OK, "bear")
        check("ru: медведь «+2 XP»", "+2 XP" in line)
        line = await beast_xp_line(LIGHT_OK, "unknown_beast")
        check("неизвестный зверь: без опыта", line == "")
    finally:
        await close_db()
        if os.path.exists(_TEST_DB):
            os.remove(_TEST_DB)

    print(f"\nSmoke 244: {passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)


asyncio.run(run())
