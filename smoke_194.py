# -*- coding: utf-8 -*-
"""Smoke 194 — шансы комнат Огненного Лабиринта по таблице FIRE_LAB_ROOM_WEIGHTS.

Статистика по большой выборке: доли исходов близки к целевым (±1.5 п.п.).
1. До 13-й комнаты, древо и колодец доступны: древо 9, колодец 6, враг 60, пусто 25.
2. Древо и колодец исчерпаны: враг 65, пусто 35.
3. С 13-й комнаты, босс доступен: древо 9, колодец 6, босс 32, враг 41, пусто 12.
4. С 13-й комнаты, оба босса уже были: древо 9, колодец 6, враг 60, пусто 25.
"""
import asyncio
import os
import random
import sys
from collections import Counter

os.environ["DATABASE_PATH"] = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "_test_smoke194.db")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

N = 60000


async def sample(fe, session):
    counts = Counter()
    for _ in range(N):
        counts[await fe._roll_room(1, session, "L", [])] += 1
    return {k: 100.0 * v / N for k, v in counts.items()}


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

    from bot.handlers import fire_event as fe
    random.seed(194)

    cases = [
        ("1. до босса, древо и колодец доступны",
         dict(tree_visits=0, well_visits=0, boss_encounters=0, steps=0),
         {"tree": 9, "well": 6, "enemy": 60, "empty": 25, "boss": 0}),
        ("2. древо и колодец исчерпаны",
         dict(tree_visits=1, well_visits=3, boss_encounters=0, steps=0),
         {"tree": 0, "well": 0, "enemy": 65, "empty": 35, "boss": 0}),
        ("3. с 13-й комнаты, босс доступен",
         dict(tree_visits=0, well_visits=0, boss_encounters=0, steps=13),
         {"tree": 9, "well": 6, "boss": 32, "enemy": 41, "empty": 12}),
        ("4. с 13-й комнаты, оба босса уже были",
         dict(tree_visits=0, well_visits=0, boss_encounters=2, steps=13),
         {"tree": 9, "well": 6, "enemy": 60, "empty": 25, "boss": 0}),
    ]
    for title, sess, want in cases:
        print(f"\n{title}")
        got = await sample(fe, sess)
        for key, target in want.items():
            value = got.get(key, 0.0)
            check(f"{key}: {value:.1f}% (цель {target}%)", abs(value - target) <= 1.5)

    print(f"\nИТОГО: {passed} passed, {failed} failed")
    return failed


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
