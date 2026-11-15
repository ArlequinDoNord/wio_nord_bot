# -*- coding: utf-8 -*-
"""Smoke 226 — мешок добычи (рубка и руда).

Правила (решения владельца 2026-11-15):
1. Мешок на GATHER_BAG_SIZE (100) карточек: исход попытки = карточка, состав из текущих шансов.
   За полный мешок выходит ровно столько карточек каждого исхода, сколько задано.
2. Мешок персональный и без суточного сброса: остаток хранится в базе.
3. Мешок пересобирается, когда состав изменился (новый инструмент, бонус наград).
4. События (змея, неясыть, летучая мышь, скользящий удар, пламенная руда) тянутся
   отдельными бросками до мешка и карточку не тратят.

Прогон: .\\.venv\\Scripts\\python.exe smoke_226.py
"""
import asyncio
import os
import sys
from collections import Counter

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke226.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB

sys.path.insert(0, os.path.dirname(__file__))


async def run():
    from database.db import init_db, close_db, add_user, draw_gather_card, get_db
    from config import GATHER_BAG_SIZE, LOGGING_AXE_SLIP_CHANCE
    from bot.handlers.logging_site import logging_wood_chance
    from bot.handlers.mine import mine_ore_chance

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

    A, B = 9992261, 9992262
    await add_user(A, "bagA", "Альфа", "Тест")
    await add_user(B, "bagB", "Бета", "Тест")

    print("\n1. Размер мешка и состав из шансов")
    check("мешок 100 карточек", GATHER_BAG_SIZE == 100)
    check("рубка ранг 1 → бревно 50%", logging_wood_chance(1) == 50)
    check("рубка ранг 2 → бревно 65%", logging_wood_chance(2) == 65)
    check("руда ранг 1 → руда 45%", mine_ore_chance(1) == 45)

    print("\n2. Полный мешок: ровно заданное число карточек каждого исхода")
    comp = {"wood": 50, "firewood": 50}
    first = [await draw_gather_card(A, "logging", comp) for _ in range(100)]
    cnt = Counter(first)
    check("из 100 попыток 50 бревен", cnt["wood"] == 50)
    check("из 100 попыток 50 дров", cnt["firewood"] == 50)

    print("\n3. Пересборка мешка на новом составе (инструмент ранга 2)")
    comp2 = {"wood": 65, "firewood": 35}
    second = [await draw_gather_card(A, "logging", comp2) for _ in range(100)]
    cnt2 = Counter(second)
    check("после смены состава: 65 бревен", cnt2["wood"] == 65)
    check("после смены состава: 35 дров", cnt2["firewood"] == 35)

    print("\n4. Остаток сохраняется между вызовами (без суточного сброса)")
    await draw_gather_card(B, "mine", {"ore": 45, "none": 55})
    await draw_gather_card(B, "mine", {"ore": 45, "none": 55})
    conn = await get_db()
    row = await (await conn.execute(
        "SELECT cards FROM gather_bags WHERE user_id = ? AND activity = 'mine'", (B,))).fetchone()
    import json
    left = json.loads(row["cards"])
    check("после двух попыток в мешке 98 карточек", len(left) == 98)
    check("в остатке только исходы состава", set(left) <= {"ore", "none"})

    print("\n5. Мешок персональный: у второго пилота свой мешок")
    b_first = [await draw_gather_card(A, "mine", {"ore": 45, "none": 55}) for _ in range(3)]
    row_b = await (await conn.execute(
        "SELECT cards FROM gather_bags WHERE user_id = ? AND activity = 'mine'", (A,))).fetchone()
    check("у пилота A мешок руды независим от B", len(json.loads(row_b["cards"])) == 97)
    check("три попытки проведены", len(b_first) == 3)

    print("\n6. Некорректный состав не принимается")
    try:
        await draw_gather_card(A, "logging", {"wood": 40, "firewood": 40})
        check("сумма ≠ 100 отклонена", False)
    except ValueError:
        check("сумма ≠ 100 отклонена", True)

    print("\n7. Порядок событий: бросок события идёт до мешка")
    import inspect
    from bot.handlers import logging_site, mine
    src_log = inspect.getsource(logging_site)
    src_mine = inspect.getsource(mine)
    check("рубка: змея и неясыть до мешка",
          src_log.index("snake = await _snake()") < src_log.index('draw_gather_card(user_id, "logging"'))
    check("рубка: скользящий удар — карточка мешка",
          '"slip": LOGGING_AXE_SLIP_CHANCE' in src_log)
    check("рубка: отдельного броска скольжения больше нет",
          "random.random() * 100 < LOGGING_AXE_SLIP_CHANCE" not in src_log)
    check("скольжение целое число (2%)", isinstance(LOGGING_AXE_SLIP_CHANCE, int))
    check("руда: летучая мышь до мешка",
          src_mine.index("bat = await _bat()") < src_mine.index("_mine_card(user_id, chance)"))
    check("руда: пламенная руда до мешка",
          src_mine.index("FIRE_ORE_CHANCE") < src_mine.index("_mine_card(user_id, chance)"))

    await close_db()
    print(f"\nИТОГО: {passed} passed, {failed} failed")
    return failed


if __name__ == "__main__":
    sys.exit(1 if asyncio.run(run()) else 0)
