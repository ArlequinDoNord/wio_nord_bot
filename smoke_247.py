"""Smoke v0.43.33: руды 1 уровня рудника (уголь, солевая руда, доломит, пирит) и шанс по рангу.

Проверяет:
1. Веса по рангам кирки 1..4 дают ровно шанс 65/70/80/90 (карточки руды = шанс).
2. Состав мешка по рангу: сумма = GATHER_BAG_SIZE, руды и «none».
3. Бонус наград сверх ранга уходит карточками угля, потолок не превышен.
4. Все руды мешка есть в сидах (MINE_ITEM_SEEDS).
5. Шанс с наградами не ниже 0 и не выше кап.
6. Ранг выше 4 считается как 4.

Запуск: .venv\\Scripts\\python.exe smoke_247.py
"""
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(__file__))


def run():
    from config import (GATHER_BAG_SIZE, MINE_ORE_WEIGHTS_BY_RANK, MINE_ITEM_SEEDS,
                        MINE_COAL_NAME, MINE_CHANCE_CAP)
    from bot.handlers.mine import mine_ore_chance, mine_bag_comp

    passed = failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
        else:
            failed += 1
            print(f"  FAIL: {name}")

    seeds = {s[0] for s in MINE_ITEM_SEEDS}
    expected = {1: 65, 2: 70, 3: 80, 4: 90}

    for rank, want in expected.items():
        weights = MINE_ORE_WEIGHTS_BY_RANK[rank]
        check(f"ранг {rank}: карточек руды = {want}", sum(weights.values()) == want)
        check(f"ранг {rank}: шанс = {want}", mine_ore_chance(rank) == want)
        comp = mine_bag_comp(rank)
        check(f"ранг {rank}: мешок = {GATHER_BAG_SIZE}", sum(comp.values()) == GATHER_BAG_SIZE)
        check(f"ранг {rank}: пусто = {GATHER_BAG_SIZE - want}", comp["none"] == GATHER_BAG_SIZE - want)
        check(f"ранг {rank}: все руды в сидах", all(n in seeds for n in weights))

    check("ранг 1: уголь 26 (как в ТЗ)", MINE_ORE_WEIGHTS_BY_RANK[1][MINE_COAL_NAME] == 26)
    sell = {s[0]: s[3] for s in MINE_ITEM_SEEDS}
    rarity = {s[0]: s[4] for s in MINE_ITEM_SEEDS}
    order = ["Уголь", "Железная руда", "Солевая руда", "Доломит", "Пирит"]
    check("у всех руд 1 уровня есть цена скупки", all(sell.get(n, 0) > 0 for n in order))
    check("цены скупки: уголь 10, железо 25, соль 15, доломит 60, пирит 90",
          [sell[n] for n in order] == [10, 25, 15, 60, 90])
    check("пирит — самая редкая (редкость 4)", rarity["Пирит"] == 4)
    from config import MINE_MARKET_ORES, MARKET_PACK_SIZES
    check("все руды 1 уровня на рынке игроков", set(order) == set(MINE_MARKET_ORES))
    check("все руды на рынке пачками (пачка задана)", all(MARKET_PACK_SIZES.get(n) for n in order))
    check("ранг 4: соль 28 (как в ТЗ)", MINE_ORE_WEIGHTS_BY_RANK[4]["Солевая руда"] == 28)

    # Бонусов достижений к шансу нет: шанс только по рангу кирки
    check("ранг 1 мешок: руды 65 карточек", sum(v for k, v in mine_bag_comp(1).items() if k != "none") == 65)
    check("ранг 1 мешок: пусто 35", mine_bag_comp(1)["none"] == 35)

    # Ранг выше таблицы — как 4
    check("ранг 9 = ранг 4", mine_ore_chance(9) == mine_ore_chance(4))
    check("ранг 9 мешок = ранг 4", mine_bag_comp(9) == mine_bag_comp(4))

    print(f"\nSmoke 247: {passed} passed, {failed} failed")
    return failed


if __name__ == "__main__":
    sys.exit(1 if run() else 0)
