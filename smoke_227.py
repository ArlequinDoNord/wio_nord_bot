# -*- coding: utf-8 -*-
"""Smoke 227 — уровень достижения снижает стоимость попытки рубки и руды (вариант B).

Правила (решение владельца 2026-11-18):
- уровень 1: без изменений (12 ОД);
- уровень 2: 11 ОД, уровень 3: 10 ОД, уровень 4: 9 ОД;
- минимум 1 ОД; бонус зависит только от текущего уровня.

Прогон: .\\.venv\\Scripts\\python.exe smoke_227.py
"""
import asyncio
import os
import sys

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke227.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB

sys.path.insert(0, os.path.dirname(__file__))


async def run():
    from database.db import (init_db, close_db, add_user, bump_achievement,
                             get_achievement_progress, gather_ap_cost, get_achievement_bonus,
                             ACHIEVEMENTS_DEF)
    from config import LOGGING_AP_COST, MINE_AP_COST

    await init_db()
    passed = failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
            print(f"  OK  {name}")
        else:
            failed += 1
            print(f"  FAIL: {name}")

    U = 9992271
    await add_user(U, "ap227", "Ап", "Тест")

    print("\n1. Конфиг достижений: бонусы стоимости по уровням")
    log_levels = {l["level"]: l["bonus"].get("logging_ap", 0) for l in ACHIEVEMENTS_DEF["logging"]["levels"]}
    min_levels = {l["level"]: l["bonus"].get("mining_ap", 0) for l in ACHIEVEMENTS_DEF["mining"]["levels"]}
    check("рубка: 0/-1/-2/-3 по уровням 1-4", log_levels == {1: 0, 2: -1, 3: -2, 4: -3})
    check("руда: 0/-1/-2/-3 по уровням 1-4", min_levels == {1: 0, 2: -1, 3: -2, 4: -3})

    print("\n2. Без уровня — базовая стоимость")
    check("рубка без уровня = 12", await gather_ap_cost(U, "logging", LOGGING_AP_COST) == 12)
    check("руда без уровня = 12", await gather_ap_cost(U, "mining", MINE_AP_COST) == 12)

    print("\n3. Уровни рубки (порог 10 / 50 / 200 / 500)")
    await bump_achievement(U, "logging", 10)
    lvl, _ = await get_achievement_progress(U, "logging")
    check("достигнут уровень 1", lvl == 1)
    check("уровень 1 — 12 ОД", await gather_ap_cost(U, "logging", LOGGING_AP_COST) == 12)
    await bump_achievement(U, "logging", 40)
    lvl, _ = await get_achievement_progress(U, "logging")
    check("достигнут уровень 2", lvl == 2)
    check("уровень 2 — 11 ОД", await gather_ap_cost(U, "logging", LOGGING_AP_COST) == 11)
    await bump_achievement(U, "logging", 150)
    lvl, _ = await get_achievement_progress(U, "logging")
    check("достигнут уровень 3", lvl == 3)
    check("уровень 3 — 10 ОД", await gather_ap_cost(U, "logging", LOGGING_AP_COST) == 10)
    await bump_achievement(U, "logging", 300)
    lvl, _ = await get_achievement_progress(U, "logging")
    check("достигнут уровень 4", lvl == 4)
    check("уровень 4 — 9 ОД", await gather_ap_cost(U, "logging", LOGGING_AP_COST) == 9)
    check("бонус не копится: текущий уровень даёт -3, а не -6",
          await get_achievement_bonus(U, "logging", "logging_ap") == -3)

    print("\n4. Руда считается отдельно от рубки")
    await bump_achievement(U, "mining", 60)
    lvl_m, _ = await get_achievement_progress(U, "mining")
    check("руда: достигнут уровень 2", lvl_m == 2)
    check("руда уровень 2 — 11 ОД", await gather_ap_cost(U, "mining", MINE_AP_COST) == 11)
    check("рубка не изменилась от руды", await gather_ap_cost(U, "logging", LOGGING_AP_COST) == 9)

    print("\n5. Минимум 1 ОД")
    check("база 1 с бонусом -3 даёт 1, а не 0 и не отрицательное",
          await gather_ap_cost(U, "logging", 1) == 1)

    await close_db()
    print(f"\nИТОГО: {passed} passed, {failed} failed")
    return failed


if __name__ == "__main__":
    sys.exit(1 if asyncio.run(run()) else 0)
