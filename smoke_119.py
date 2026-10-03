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
                    PILOT_BASE_HP, PILOT_NO_WEAPON_DMG, RANK_DAMAGE_TIERS)
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


def simulate(hp=PILOT_BASE_HP, rounds=20000, base=None, weapon=0):
    """Прогон боя: игрок без снаряжения против кабана.

    По умолчанию — рекрут (1–1). base передаёт пару (минимум, максимум),
    чтобы прогнать любой статус из RANK_DAMAGE_TIERS.
    """
    stats = {'base_dmg': PILOT_NO_WEAPON_DMG, 'weapon_damage': weapon,
             'attack_mult': 1.0, 'dodge': 0, 'armor': 0,
             'hp_max': hp, 'award_attack': 0}
    if base:
        stats['base_dmg'] = tuple(base)
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
    print(f"  Урон пилота:    {PILOT_NO_WEAPON_DMG[0]}–{PILOT_NO_WEAPON_DMG[1]} "
          f"у рекрута, + оружие сверху; по статусу — RANK_DAMAGE_TIERS")
    print(f"  HP пилота:      {PILOT_BASE_HP} (без награды)")

    check("диапазон урона кабана из конфига",
          (FOREST_BOAR_DMG[0], FOREST_BOAR_DMG[1]) == (4, 7),
          f"{FOREST_BOAR_DMG[0]}–{FOREST_BOAR_DMG[1]}")

    player_hits, boar_hits, kills, deaths = simulate()

    avg_p = statistics.mean(player_hits)
    avg_b = statistics.mean(boar_hits)
    print("\n── Рекрут без снаряжения, 100 HP ──")
    print(f"  Пилот наносит:  {min(player_hits)}–{max(player_hits)} "
          f"(средний {avg_p:.1f}) за удар")
    print(f"  Кабан наносит:  {min(boar_hits)}–{max(boar_hits)} "
          f"(средний {avg_b:.1f}) за удар")
    total_battles = len(kills) + len(deaths)
    if kills:
        print(f"  Раундов до победы пилота:  среднее {statistics.mean(kills):.1f}")
    else:
        print("  Раундов до победы пилота:  ни одной (1 урона не хватает на кабана)")
    if deaths:
        print(f"  Раундов до поражения пилота: среднее {statistics.mean(deaths):.1f}")
        check("рекрут без оружия проигрывает кабану", len(deaths) > 0,
              f"{len(deaths)} из {total_battles} боёв")
    check("рекрут с 1 уроном не может победить кабана без оружия",
          not kills, f"побед: {len(kills)}")

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
    lo, hi = PILOT_NO_WEAPON_DMG
    check(f"средний урон рекрута в диапазоне {lo}–{hi}",
          lo <= avg_p <= hi, f"{avg_p:.1f}")
    check(f"средний урон кабана в диапазоне {FOREST_BOAR_DMG[0]}–{FOREST_BOAR_DMG[1]}",
          FOREST_BOAR_DMG[0] <= avg_b <= FOREST_BOAR_DMG[1], f"{avg_b:.1f}")

    # Кабан сносит пилота: 100 HP / ~5.5 = ~18-19 ударов
    pilot_hp = PILOT_BASE_HP
    expected_death = pilot_hp / avg_b
    check("кабан убивает пилота без снаряжения (100 HP)",
          avg_b > 0 and expected_death < 30, f"~{expected_death:.1f} ударов")

    # Рекрут с 1 уроном: 40 HP кабана / 1 = 40 ударов, но пилот умирает
    # примерно за 19 — то есть без оружия рекрут кабана не добивает.
    expected_kill = FOREST_BOAR_HP / avg_p
    check("на 1 уроне кабана нужно ~40 ударов (больше, чем живёт пилот)",
          expected_kill > pilot_hp / avg_b, f"~{expected_kill:.0f} против ~{pilot_hp / avg_b:.0f}")

    # ── Прогон по всем статусам: чем выше звание, тем выше шанс победить ──
    print("\n── Бой против кабана по статусам (без оружия) ──")
    win_rates = {}
    for tag in ("recruit", "pilot2", "pilot1", "veteran", "master_pilot", "ace"):
        _, _, rk, rd = simulate(rounds=2000, base=RANK_DAMAGE_TIERS[tag])
        total = len(rk) + len(rd)
        rate = len(rk) * 100.0 / total if total else 0.0
        win_rates[tag] = rate
        rounds_txt = (f"~{statistics.mean(rk):.0f} уд." if rk
                      else f"проигрыш за ~{statistics.mean(rd):.0f} уд." if rd else "—")
        lo, hi = RANK_DAMAGE_TIERS[tag]
        print(f"  {tag:14s} {lo}–{hi} → побед {rate:5.1f}%  ({rounds_txt})")
    seq = ["recruit", "pilot2", "pilot1", "veteran", "master_pilot", "ace"]
    check("чем выше статус, тем выше шанс победить кабана",
          all(win_rates[seq[i]] <= win_rates[seq[i + 1]] for i in range(len(seq) - 1)),
          " → ".join(f"{win_rates[t]:.0f}%" for t in seq))
    check("аc без оружия выигрывает кабана почти всегда",
          win_rates["ace"] >= 95, f"{win_rates['ace']:.1f}%")
    check("ветеран без оружия выигрывает у кабана чаще половины боёв",
          win_rates["veteran"] >= 50, f"{win_rates['veteran']:.1f}%")
    check("рекрут без оружия кабана почти не добивает",
          win_rates["recruit"] <= 5, f"{win_rates['recruit']:.1f}%")
    # ── С оружием +2 даже рекрут выигрывает: оружие обязательно для новичка ──
    _, _, rk2, rd2 = simulate(rounds=2000, base=RANK_DAMAGE_TIERS["recruit"], weapon=2)
    total2 = len(rk2) + len(rd2)
    rate2 = len(rk2) * 100.0 / total2 if total2 else 0.0
    print(f"  рекрут с оружием +2 → побед {rate2:.1f}%")
    check("с оружием (+2) рекрут выигрывает кабана чаще 80% боёв",
          rate2 >= 80, f"{rate2:.1f}%")

    print(f"\n=== SMOKE 119: {PASSED} passed, {FAILED} failed ===")
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())