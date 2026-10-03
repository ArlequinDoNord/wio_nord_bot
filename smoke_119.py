# SMOKE 119: бой с кабаном — реальные числа для обычного пилота без снаряжения
#
# Вопрос: сколько наносит обычный пилот без снаряжения и сколько атакует кабан.
# Модель бояforest.py: игрок бьёт player_dmg_min..player_dmg_max из строки врага,
# кабан бьёт dmg_min..dmg_max, у игрока 100 HP + бонус награды за HP.
import os
import random
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (FOREST_BOAR_HP, FOREST_BOAR_DMG, FOREST_BOAR_DODGE,
                    FOREST_BOAR_SEED)

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


def simulate(seed_player=(9, 15), hp=100, rounds=20000):
    """Прогон боя: игрок без снаряжения (100 HP) против кабана."""
    p_lo, p_hi = seed_player
    b_lo, b_hi = FOREST_BOAR_DMG
    boar_hp = FOREST_BOAR_HP
    player_hp = hp
    rnd = random.Random(20261003)

    player_hits, boar_hits = [], []
    rounds_to_kill, rounds_to_die = [], []

    for _ in range(rounds):
        boar_hp = FOREST_BOAR_HP
        player_hp = hp
        n = 0
        while boar_hp > 0 and player_hp > 0:
            n += 1
            if rnd.random() * 100 < FOREST_BOAR_DODGE:
                pass  # зверь увернулся
            else:
                hit = rnd.randint(p_lo, p_hi)
                player_hits.append(hit)
                boar_hp -= hit
            if boar_hp <= 0:
                break
            b_hit = rnd.randint(b_lo, b_hi)
            boar_hits.append(b_hit)
            player_hp -= b_hit
        if boar_hp <= 0:
            rounds_to_kill.append(n)
        else:
            rounds_to_die.append(n)
    return player_hits, boar_hits, rounds_to_kill, rounds_to_die


def main():
    print("── Параметры кабана (сид по умолчанию) ──")
    print(f"  HP кабана:      {FOREST_BOAR_SEED['hp']} (config FOREST_BOAR_HP={FOREST_BOAR_HP})")
    print(f"  Урон кабана:    {FOREST_BOAR_DMG[0]}–{FOREST_BOAR_DMG[1]}")
    print(f"  Уклонение:      {FOREST_BOAR_DODGE}%")
    print("  Урон игрока:    9–15 (player_dmg_min/max из строки врага, НЕ снаряжение)")
    print("  HP игрока:      100 (без награды)")

    p_lo = int(FOREST_BOAR_SEED.get("player_dmg_min") or 9)
    p_hi = int(FOREST_BOAR_SEED.get("player_dmg_max") or 15)

    check("сид кабана содержит player_dmg_min", "player_dmg_min" in FOREST_BOAR_SEED)
    check("диапазон урона кабана из сида",
          (FOREST_BOAR_SEED["dmg_min"], FOREST_BOAR_SEED["dmg_max"]) == FOREST_BOAR_DMG,
          f"{FOREST_BOAR_SEED['dmg_min']}–{FOREST_BOAR_SEED['dmg_max']}")

    player_hits, boar_hits, kills, deaths = simulate((p_lo, p_hi))

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

    # ── Проверки против фактического кода forest.py ──
    src = open(os.path.join(os.path.dirname(__file__), "bot", "handlers", "forest.py"),
               encoding="utf-8").read()

    check("урон игрока из player_dmg_min/max строки врага",
          "battle.get('player_dmg_min')" in src and "battle.get('player_dmg_max')" in src)
    check("кабан бьёт в своём диапазоне dmg_min..dmg_max",
          "battle.get('dmg_min')" in src and "battle.get('dmg_max')" in src)
    check("игрок НЕ бьёт player_damage из equipment (старая модель)",
          "player_damage" not in src)
    check("в бою кабана нет расчёта от брони/снаряжения",
          "armor" not in src.lower())

    # Диапазоны совпадают с конфигом
    check(f"средний урон пилота в диапазоне {p_lo}–{p_hi}", p_lo <= avg_p <= p_hi,
          f"{avg_p:.1f}")
    check(f"средний урон кабана в диапазоне {FOREST_BOAR_DMG[0]}–{FOREST_BOAR_DMG[1]}",
          FOREST_BOAR_DMG[0] <= avg_b <= FOREST_BOAR_DMG[1], f"{avg_b:.1f}")

    # Кабан сносит пилота: 100 HP / ~5.5 = ~18-19 ударов
    pilot_hp = 100
    expected_death = pilot_hp / avg_b
    check("кабан убивает пилота без снаряжения (100 HP)",
          avg_b > 0 and expected_death < 30, f"~{expected_death:.1f} ударов")

    # Пилот убивает кабана: 30 HP / ~12 = ~2.5 удара
    expected_kill = FOREST_BOAR_HP / avg_p
    check("пилот без снаряжения убивает кабана за 2–4 удара",
          2 <= expected_kill <= 4, f"~{expected_kill:.1f} удара")

    print(f"\n=== SMOKE 119: {PASSED} passed, {FAILED} failed ===")
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())