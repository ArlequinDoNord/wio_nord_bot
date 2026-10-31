# -*- coding: utf-8 -*-
"""Smoke 183 — способность врага «пробитие брони» (on_hit_effects kind=armor_pierce).

1. armor_hit: без пробития броня вычитается (не ниже minimum), с пробитием — pct% урона без брони.
2. roll_enemy_damage: шанс 100 и pct 50 — половина урона при броне 6; шанс 0 — обычный вычет брони.
3. onhit.roll_procs не превращает armor_pierce в обычное наложение.
4. ON_HIT_EFFECTS содержит armor_pierce с параметрами (виден в админке).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    passed = failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
            print(f"  OK  {name}")
        else:
            failed += 1
            print(f"  FAIL {name}")

    import config
    from utils import combat_model as cm
    from utils import onhit

    print("\n1. armor_hit")
    h = cm.armor_hit(7, 6, None, minimum=1)
    check("без пробития: 7 - 6 = 1, броня поглотила 6", h['damage'] == 1 and h['armor_blocked'] == 6
          and not h['pierced'])
    h = cm.armor_hit(7, 6, 100, minimum=1)
    check("пробитие 100%: весь урон 7, броня не режет", h['damage'] == 7 and h['pierced'])
    h = cm.armor_hit(7, 6, 50, minimum=1)
    check("пробитие 50%: половина 4 (округление), броня не режет", h['damage'] == 4 and h['pierced'])
    h = cm.armor_hit(3, 9, None, minimum=0)
    check("minimum=0 (лабиринт): урон не уходит ниже 0", h['damage'] == 0)

    print("\n2. roll_enemy_damage с способностью на врага")
    stats = {'dodge': 0, 'armor': 6}
    fixed = {'dmg_min': 7, 'dmg_max': 7, 'on_hit_effects': [
        {"kind": "armor_pierce", "chance": 100, "pct": 50}]}
    res = [cm.roll_enemy_damage(stats, fixed) for _ in range(200)]
    check("шанс 100%, pct 50: всегда 4 урона", all(r['damage'] == 4 and r['pierced'] for r in res))
    none_ = {'dmg_min': 7, 'dmg_max': 7, 'on_hit_effects': [
        {"kind": "armor_pierce", "chance": 0, "pct": 100}]}
    res0 = [cm.roll_enemy_damage(stats, none_) for _ in range(200)]
    check("шанс 0%: обычный вычет брони, 1 урона", all(r['damage'] == 1 and not r['pierced'] for r in res0))
    full = {'dmg_min': 7, 'dmg_max': 7, 'on_hit_effects': [
        {"kind": "armor_pierce", "chance": 100, "pct": 100}]}
    check("шанс 100%, pct 100: весь урон 7", cm.roll_enemy_damage(stats, full)['damage'] == 7)
    check("явный pierce_pct перекрывает способность врага",
          cm.roll_enemy_damage(stats, none_, pierce_pct=100)['damage'] == 7)
    check("без on_hit_effects — как раньше", cm.roll_enemy_damage(stats, {'dmg_min': 7, 'dmg_max': 7})['damage'] == 1)

    print("\n3. onhit")
    check("roll_procs не выдаёт armor_pierce как наложение",
          onhit.roll_procs([{"kind": "armor_pierce", "chance": 100, "pct": 50}]) == [])
    check("roll_armor_pierce: шанс 100 → 50", onhit.roll_armor_pierce(
        [{"kind": "armor_pierce", "chance": 100, "pct": 50}]) == 50)
    check("roll_armor_pierce без способности → None", onhit.roll_armor_pierce([]) is None)

    print("\n4. конфиг")
    spec = config.ON_HIT_EFFECTS.get("armor_pierce") or {}
    check("armor_pierce в ON_HIT_EFFECTS с параметрами chance и pct",
          [p[0] for p in spec.get("params", ())] == ["chance", "pct"])
    check("armor_pierce в порядке видов", "armor_pierce" in config.ON_HIT_KIND_ORDER)

    print("\n5. Редактор on-hit в админке (врагов лабиринта тоже)")
    from bot.handlers import admin as adm
    opts = [item for item, _ in adm._onhit_options()]
    check("«Пробитие брони» есть в списке для выбора", "armor_pierce" in opts)
    check("ввод «30 50» разбирается",
          adm._onhit_parse_params("30 50", "armor_pierce") == {"kind": "armor_pierce", "chance": 30, "pct": 50})
    check("ввод «30 150» отклоняется", adm._onhit_parse_params("30 150", "armor_pierce") is None)
    check("строка эффекта выводится",
          "мимо брони" in adm._onhit_effect_line({"kind": "armor_pierce", "chance": 30, "pct": 50}))

    print(f"\nИТОГО: {passed} passed, {failed} failed")
    return failed


if __name__ == "__main__":
    sys.exit(main())
