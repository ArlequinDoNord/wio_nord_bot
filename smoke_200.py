# -*- coding: utf-8 -*-
"""Smoke 200 — профиль «Достижения» и «Собиратель ягод».

1. Статус достижения с одним уровнем не падает (раньше levels[1] → IndexError).
2. Экран «Достижения» отвечает текстом для пилота с ачивкой из одного уровня.
3. Собиратель ягод: пороги 10/60/240/600 и бонус rarity_pct 2/2/4/8.
4. Выбор ягоды: бонус переносит долю у черники на редкие, сумма шансов не меняется.
5. На опушке (нет черники в пуле бонус не действует, медведь не редкий).
"""
import asyncio
import os
import sys

os.environ["DATABASE_PATH"] = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "_test_smoke200.db")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

BLUE, RASP, STRAW, BEAR, FIRE = "Горсть черники", "Горсть малины", "Горсть земляники", "bear", "Горсть Пылающих ягод"


class _Msg:
    def __init__(self):
        self.texts = []

    async def answer(self, text, **kw):
        self.texts.append(text)


class _User:
    def __init__(self, uid):
        self.id = uid


class _Cb:
    def __init__(self, uid):
        self.from_user = _User(uid)
        self.message = _Msg()

    async def answer(self, *a, **kw):
        return None


async def main():
    passed = failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
            print(f"  OK  {name}")
        else:
            failed += 1
            print(f"  FAIL {name}")

    db_file = os.environ["DATABASE_PATH"]
    if os.path.exists(db_file):
        os.remove(db_file)

    import database.db as db
    from database.db import (init_db, close_db, add_user, ensure_achievements,
                             bump_achievement, get_achievement_bonus, get_achievement_level,
                             ACHIEVEMENTS_DEF)
    from bot.handlers.profile import _achievement_status, profile_achievements
    from bot.handlers.forest import pick_forest_berry

    await init_db()
    await ensure_achievements()
    uid = 880001
    await add_user(uid, "u880001", "Тест", "")

    print("\n1. Статус одноуровневой ачивки")
    single = ACHIEVEMENTS_DEF["fire_fisher"]["levels"]
    check("уровень 0 — прогресс до порога",
          _achievement_status(single, 0, 1).startswith("1/3 → Рыбак древних"))
    check("уровень 1 — выполнено, без падения",
          _achievement_status(single, 1, 3).startswith("выполнено (уровень 1: Рыбак древних)"))
    four = ACHIEVEMENTS_DEF["mushrooms"]["levels"]
    check("4 уровня: уровень 2 показывает следующий порог",
          _achievement_status(four, 2, 80).startswith("80/300 → Тихий охотник"))
    check("4 уровня: уровень 4 — выполнено",
          _achievement_status(four, 4, 700).startswith("выполнено (уровень 4: Лесник Хельды)"))

    print("\n2. Экран «Достижения» для пилота с одноуровневой ачивкой")
    await bump_achievement(uid, "fire_fisher", 3)
    cb = _Cb(uid)
    await profile_achievements(cb)
    text = "\n".join(cb.message.texts)
    check("экран ответил текстом", bool(cb.message.texts))
    check("в тексте есть «Рыбак древних» как выполнено", "выполнено (уровень 1: Рыбак древних)" in text)

    print("\n3. Собиратель ягод: пороги и бонус")
    check("ачивка есть", "berries" in ACHIEVEMENTS_DEF)
    await bump_achievement(uid, "berries", 9)
    check("9 горстей — ещё без уровня", await get_achievement_level(uid, "berries") == 0)
    await bump_achievement(uid, "berries", 1)
    check("10 горстей — уровень 1, бонус +2%",
          await get_achievement_level(uid, "berries") == 1
          and await get_achievement_bonus(uid, "berries", "rarity_pct") == 2)
    await bump_achievement(uid, "berries", 50)
    check("60 горстей — уровень 2, бонус +2%",
          await get_achievement_level(uid, "berries") == 2
          and await get_achievement_bonus(uid, "berries", "rarity_pct") == 2)
    await bump_achievement(uid, "berries", 180)
    check("240 горстей — уровень 3, бонус +4%",
          await get_achievement_level(uid, "berries") == 3
          and await get_achievement_bonus(uid, "berries", "rarity_pct") == 4)
    await bump_achievement(uid, "berries", 360)
    check("600 горстей — уровень 4, бонус +8%",
          await get_achievement_level(uid, "berries") == 4
          and await get_achievement_bonus(uid, "berries", "rarity_pct") == 8)

    print("\n4. Выбор ягоды на прогалине")
    clearing = [
        {"ref": "item:1", "name": BLUE, "chance": 40, "item_id": 1},
        {"ref": "item:2", "name": RASP, "chance": 25, "item_id": 2},
        {"ref": "item:3", "name": STRAW, "chance": 20, "item_id": 3},
        {"ref": BEAR, "name": "Медведь", "chance": 5, "item_id": None},
        {"ref": "item:4", "name": FIRE, "chance": 10, "item_id": 4},
    ]
    check("без бонуса r=36 → черника", pick_forest_berry(clearing, 36)["name"] == BLUE)
    check("без бонуса r=99 → Пылающие", pick_forest_berry(clearing, 99)["name"] == FIRE)
    check("без бонуса r=100 → пусто", pick_forest_berry(clearing, 100) is None)
    check("бонус 8%: r=36 → малина (черника уступила долю)",
          pick_forest_berry(clearing, 36, rare_bonus=8)["name"] == RASP)
    check("бонус 8%: r=35 → всё ещё черника",
          pick_forest_berry(clearing, 35, rare_bonus=8)["name"] == BLUE)
    check("бонус 8%: медведь не растёт (r в его окне — медведь)",
          pick_forest_berry(clearing, 86.0, rare_bonus=8)["name"] == "Медведь")
    total_before = sum(r["chance"] for r in clearing)
    hits = {}
    for i in range(10000):
        row = pick_forest_berry(clearing, i / 100.0, rare_bonus=8)
        key = row["name"] if row else None
        hits[key] = hits.get(key, 0) + 1
    check("сумма шансов сохраняется (100)", total_before == 100)
    check("бонус 8% даёт малине больше 25% (≈27%)",
          abs(hits.get(RASP, 0) / 100.0 - 27) < 1.0)

    print("\n5. Опушка")
    glade = [{"ref": "item:1", "name": BLUE, "chance": 50, "item_id": 1}]
    check("опушка: бонус не влияет (r=49 → черника)",
          pick_forest_berry(glade, 49, rare_bonus=8)["name"] == BLUE)
    check("опушка: пусто остаётся 50%", pick_forest_berry(glade, 50, rare_bonus=8) is None)
    no_blue = [{"ref": "item:2", "name": RASP, "chance": 25, "item_id": 2}]
    check("без черники бонус не действует (r=25 → пусто)",
          pick_forest_berry(no_blue, 25, rare_bonus=8) is None)

    print(f"\nИТОГО: {passed} passed, {failed} failed")
    await close_db()
    return failed


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
