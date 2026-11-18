# -*- coding: utf-8 -*-
"""Smoke 228 — словарь эффектов боя (шаг 1): мульти-DoT на враге.

Правила (решения владельца 2026-11-18):
- яд и кровотечение совмещаются, у каждого свой урон и счётчик;
- обморожение и горение гасят друг друга: при наложении снимаются оба;
- повторное наложение того же вида обновляет его;
- в боевом коде dungeon.py больше нет одиночного слота enemy_effect.

Прогон: .\\.venv\\Scripts\\python.exe smoke_228.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

passed = failed = 0


def check(name, cond):
    global passed, failed
    if cond:
        passed += 1
        print(f"  OK  {name}")
    else:
        failed += 1
        print(f"  FAIL: {name}")


def main():
    from utils import effects as E

    print("\n1. Яд и кровотечение совмещаются")
    d = {}
    E.apply_dot(d, "poison", 10, 3)
    E.apply_dot(d, "bleed", 4, 2)
    check("оба DoT висят одновременно", set(d) == {"poison", "bleed"})

    print("\n2. Тик суммирует урон всех DoT и уменьшает счётчики")
    total, parts = E.tick_dots(d)
    check("урон за ход = 10 + 4", total == 14)
    check("части тика названы по видам", dict(parts) == {"poison": 10, "bleed": 4})
    check("яд осталось 2 хода", d["poison"]["ticks"] == 2)
    check("кровотечение осталось 1 ход", d["bleed"]["ticks"] == 1)
    E.tick_dots(d)
    check("кровотечение спало после своих 2 ходов", "bleed" not in d)
    check("яд ещё висит на третьем ходу", "poison" in d)

    print("\n3. Повторное наложение того же вида обновляет его")
    E.apply_dot(d, "poison", 6, 3)
    check("яд обновлён: урон 6, 3 хода", d["poison"] == {"dmg": 6, "ticks": 3})

    print("\n4. Обморожение и горение гасят друг друга")
    d = {}
    E.apply_dot(d, "burn", 5, 3)
    res = E.apply_dot(d, "frostbite", 5, 4)
    check("обморожение не наложилось", res["applied"] is False)
    check("горение снято", "burn" not in d)
    check("результат сообщает, что погасило", res["cancelled"] == "burn")
    d = {}
    E.apply_dot(d, "frostbite", 5, 4)
    res = E.apply_dot(d, "burn", 5, 3)
    check("и наоборот: горение гасит обморожение", res["applied"] is False and "frostbite" not in d)

    print("\n5. Яд не гасится горением и обморожением")
    d = {}
    E.apply_dot(d, "poison", 8, 3)
    E.apply_dot(d, "burn", 5, 3)
    check("яд и горение висят вместе", set(d) == {"poison", "burn"})

    print("\n6. Боевой код: одиночного слота enemy_effect больше нет")
    src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "bot", "handlers", "dungeon.py"), encoding="utf-8").read()
    import re
    check("в dungeon.py нет одиночного ключа enemy_effect",
          re.search(r"\benemy_effect\b", src) is None)
    check("в dungeon.py используется enemy_dots", "enemy_dots" in src)

    print("\n7. Боевые фразы: каждый ключ battle.* есть на ru и en")
    from utils.i18n import STRINGS
    battle_keys = [k for k in STRINGS if k.startswith("battle.")]
    check("ключи battle.* заведены", len(battle_keys) >= 10)
    check("у каждого battle.* есть ru и en",
          all(STRINGS[k].get("ru") and STRINGS[k].get("en") for k in battle_keys))

    print(f"\nИТОГО: {passed} passed, {failed} failed")
    return failed


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
