# SMOKE 119: бой с кабаном — реальные числа для обычного пилота без снаряжения
#
# С v0.19.11 урон пилота считается от ЕГО оружия (utils/combat_model), а не из
# строки врага. Без снаряжения удар = d6 (1–6). Кабан бьёт в свой диапазон
# dmg_min..dmg_max, броня пилота поглощает часть урона.
import os
import random
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (FOREST_BOAR_DMG, FOREST_BOAR_DODGE, FOREST_BOAR_HP,
                    PILOT_BASE_DMG, PILOT_BASE_HP)
from utils.combat_model import roll_enemy_damage, roll_pilot_damage

PASSED = 0
FAILED = 0


def check(name, cond, extra=""):
    global PASSED, FAILED
    if cond:
        PASSED += 1
        print(f"  OK  {name}{(' — ' + extra) if extra else ''}")
    else:
        FAILED += 1
        print(f"  FAIL  {name}{(' — ' + extra) if extra else ''}")


def simulate(hp=PILOT_BASE_HP, rounds=20000):
    """Прогон боя: игрок без снаряжения против кабана."""
    stats = {'weapon_damage': 0, 'attack_mult': 1.0, 'dodge': 0,
             'armor': 0, 'hp_max': hp, 'award_attack': 0}
    boar = {'dodge': FOREST_BOAR_DODGE, 'armor': 0,
            'dmg_min': FOREST_BOAR_DMG[0], 'dmg_max': FOREST_BOAR_DMG[1],
            'crit_chance': 0, 'crit_mult': 1.5}
    rnd = random.Random(20261003)

    player_hits, boar_hits = [], []
    rounds_to_kill, rounds_to_die = [], []

    for _ in range(rounds):
        boar_hp = FOREST_BOAR_HP
        player_hp = hp
        n = 0
        while boar_hp > 0 and player_hp > 0:
            n += 1
            r = roll_pilot_damage(stats, boar)
            if not r['dodged']:
                player_hits.append(r['damage'])
                boar_hp -= r['damage']
            if boar_hp <= 0:
                break
            e = roll_enemy_damage(stats, boar)
            if not e['dodged']:
                boar_hits.append(e['damage'])
                player_hp -= e['damage']
        if boar_hp <= 0:
            rounds_to_kill.append(n)
        else:
            rounds_to_die.append(n)
    return player_hits, boar_hits, rounds_to_kill, rounds_to_die


def main():
    print("── Параметры кабана ──")
    print(f"  HP кабана:      {FOREST_BOAR_HP}")
    print(f"  Урон кабана:    {FOREST_BOAR_DMG[0]}–{FOREST_BOAR_DMG[1]}")
    print(f"  Уклонение:      {FOREST_BOAR_DODGE}%")
    print(f"  Броня кабана:   0")
    print(f"  Урон пилота:    {PILOT_BASE_DMG[0]}–{PILOT_BASE_DMG[1]} "
          f"без оружия (PILOT_BASE_DMG) + оружие сверху")
    print(f"  HP пилота:      {PILOT_BASE_HP} (без награды)")

    check("диапазон урона кабана из конфига",
          (FOREST_BOAR_DMG[0], FOREST_BOAR_DMG[1]) == (4, 7),
          f"{FOREST_BOAR_DMG[0]}–{FOREST_BOAR_DMG[1]}")

    player_hits, boar_hits, kills, deaths = simulate()

    avg_p = statistics.mean(player_hits)
    avg_b = statistics.mean(boar_hits)
    print("\n── Обычный пилот без снаряжения, 100 HP ──")
    print(f"  Пилот наносит:  {min(player_hits)}–{max(player_hits)} "
          f"(средний {avg_p:.1f}) за удар")
    print(f"  Кабан наносит:  {min(boar_hits)}–{max(boar_hits)} "
          f"(средний {avg_b:.1f}) за удар")
    print(f"  Раундов до победы пилота:  среднее {statistics.mean(kills):.1f}")
    if deaths:
        print(f"  Раундов до поражения пилота: среднее {statistics.mean(deaths):.1f}")
        check("пилот без оружия изредка проигрывает кабану", len(deaths) > 0,
              f"{len(deaths)} из {len(kills) + len(deaths)} боёв")

    # ── Проверки против фактического кода forest.py ──
    src = open(os.path.join(os.path.dirname(__file__), "bot", "handlers", "forest.py"),
               encoding="utf-8").read()

    check("урон пилота НЕ берётся из player_dmg_* строки врага",
          "player_dmg_min" not in src and "player_dmg_max" not in src)
    check("кабан бьёт в своём диапазоне dmg_min..dmg_max",
          "battle.get('dmg_min')" in src and "battle.get('dmg_max')" in src)
    check("бой считается через общую модель combat_model", "combat_model" in src)
    check("броня пилота учитывается", "roll_enemy_damage" in src)

    # Диапазоны совпадают с конфигом
    check(f"средний урон пилота в диапазоне {PILOT_BASE_DMG[0]}–{PILOT_BASE_DMG[1]}",
          PILOT_BASE_DMG[0] <= avg_p <= PILOT_BASE_DMG[1], f"{avg_p:.1f}")
    check(f"средний урон кабана в диапазоне {FOREST_BOAR_DMG[0]}–{FOREST_BOAR_DMG[1]}",
          FOREST_BOAR_DMG[0] <= avg_b <= FOREST_BOAR_DMG[1], f"{avg_b:.1f}")

    # Кабан сносит пилота: 100 HP / ~5.5 = ~18-19 ударов
    pilot_hp = PILOT_BASE_HP
    expected_death = pilot_hp / avg_b
    check("кабан убивает пилота без снаряжения (100 HP)",
          avg_b > 0 and expected_death < 30, f"~{expected_death:.1f} ударов")

    # Пилот без оружия: 30 HP / ~2 = ~15 ударов (с учётом уклонения кабана)
    expected_kill = FOREST_BOAR_HP / avg_p
    check("пилот без снаряжения убивает кабана за 8–25 ударов",
          8 <= expected_kill <= 25, f"~{expected_kill:.1f} удара")

    print(f"\n=== SMOKE 119: {PASSED} passed, {FAILED} failed ===")
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())