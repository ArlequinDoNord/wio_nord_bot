# -*- coding: utf-8 -*-
"""Smoke 206 — шансы дропов Лабиринта связаны с полем редкости предмета.

Редкий лут = предмет с полем rarity >= FIRE_LAB_RARE_MIN_RARITY («Редкий» и выше).
Его шанс растёт аддитивно: +FIRE_LAB_RARE_TIER_BONUS за каждый тир.
Остальные предметы растут множителем тира, как раньше.

1. Редкий предмет (редкость 3), базовый 1%: тир 0 = 1%, тир 10 = 15%, шаг +1.4 п.п.
2. Редкий предмет с базовым 6% (перчатки): тир 10 = 20%.
3. Обычный предмет (редкость 1), базовый 45%: множителем, тир 10 = 61.2%.
4. Шанс не выходит за 100%.
5. Без данных о редкости предмет считается обычным (обратная совместимость).
"""
import sys

from tests_support import Checker

import config


def main():
    check = Checker()
    from bot.handlers.fire_event import _tier_enemy

    def enemy(item_id, chance):
        return {"key": "x", "name": "x", "hp": 10, "armor": 0, "dodge": 0,
                "dmg_min": 1, "dmg_max": 2, "drops": [{"item_id": item_id, "qty": 1, "chance": chance}]}

    print("\n1. Константы")
    check("порог редкости лута = 3", config.FIRE_LAB_RARE_MIN_RARITY == 3)
    check("бонус = 1.4 п.п. за тир", abs(config.FIRE_LAB_RARE_TIER_BONUS - 0.014) < 1e-9)

    print("\n2. Редкий предмет (редкость 3), базовый 1%")
    rar = {181: 3}
    chances = {t: _tier_enemy(enemy(181, 0.01), t, rar)["drops"][0]["chance"] for t in range(11)}
    check("тир 0: 1%", abs(chances[0] - 0.01) < 1e-9)
    check("тир 10: 15%", abs(chances[10] - 0.15) < 1e-9)
    steps = [round(chances[t + 1] - chances[t], 6) for t in range(10)]
    check("каждый тир +1.4 п.п.", all(abs(s - 0.014) < 1e-9 for s in steps))

    print("\n3. Редкий предмет с базовым 6% (перчатки)")
    c = _tier_enemy(enemy(183, 0.06), 10, {183: 3})["drops"][0]["chance"]
    check("тир 10: 20%", abs(c - 0.20) < 1e-9)

    print("\n4. Обычный предмет (редкость 1) — множителем")
    c0 = _tier_enemy(enemy(172, 0.45), 0, {172: 1})["drops"][0]["chance"]
    c10 = _tier_enemy(enemy(172, 0.45), 10, {172: 1})["drops"][0]["chance"]
    check("тир 0: 45%", abs(c0 - 0.45) < 1e-9)
    check("тир 10: 45% × 1.36 = 61.2%", abs(c10 - 0.612) < 1e-9)

    print("\n5. Предел 100%")
    check("редкий 99% на тире 10 не больше 1.0",
          _tier_enemy(enemy(181, 0.99), 10, {181: 3})["drops"][0]["chance"] <= 1.0)

    print("\n6. Без данных о редкости — обычный")
    c_none = _tier_enemy(enemy(181, 0.01), 10)["drops"][0]["chance"]
    check("без карты редкостей растёт множителем (1% × 1.36)", abs(c_none - 0.0136) < 1e-9)

    failed = check.summary()
    return failed


if __name__ == "__main__":
    sys.exit(main())
