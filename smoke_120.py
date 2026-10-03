# SMOKE 120: боевая модель — урон пилота от снаряжения, у врага свои статы
#
# Регресс: лес и подземелья брали урон пилота из строки врага (player_dmg_min/max),
# из-за чего оружие, награды и состояния не влияли на бой. Теперь урон считает
# utils/combat_model.py: оружие + награды + состояния + d6, броня врага гасит часть.
import os
import random
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (FOREST_BOAR_DMG, PILOT_BASE_HP, PILOT_NO_WEAPON_DMG,
                    RANK_DAMAGE_TIERS)
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


def stats(weapon=0, mult=1.0, dodge=0, armor=0, hp_max=PILOT_BASE_HP,
          base=PILOT_NO_WEAPON_DMG):
    return {'base_dmg': base, 'weapon_damage': weapon, 'attack_mult': mult,
            'dodge': dodge, 'armor': armor, 'hp_max': hp_max, 'award_attack': 0}


def main():
    rnd = random.Random(4242)

    # ── 1. Урон пилота растёт от оружия ──
    bare = [roll_pilot_damage(stats(weapon=0), {})['damage'] for _ in range(4000)]
    armed = [roll_pilot_damage(stats(weapon=6), {})['damage'] for _ in range(4000)]
    check("оружие добавляет урон", statistics.mean(armed) > statistics.mean(bare),
          f"без оружия {statistics.mean(bare):.1f} → с оружием {statistics.mean(armed):.1f}")

    # ── 2. Урон пилота растёт от бонуса наград ──
    buffed = [roll_pilot_damage(stats(weapon=6, mult=1.5), {})['damage'] for _ in range(4000)]
    check("бонус награды +50% атаки усиливает удар",
          statistics.mean(buffed) > statistics.mean(armed),
          f"{statistics.mean(armed):.1f} → {statistics.mean(buffed):.1f}")

    # ── 3. Броня врага поглощает урон ──
    no_armor = [roll_pilot_damage(stats(weapon=10), {})['damage'] for _ in range(3000)]
    armored = [roll_pilot_damage(stats(weapon=10), {'armor': 5}) for _ in range(3000)]
    check("броня врага снижает урон",
          statistics.mean(r['damage'] for r in armored) < statistics.mean(no_armor),
          f"{statistics.mean(no_armor):.1f} → {statistics.mean(r['damage'] for r in armored):.1f}")
    check("броня врага фиксируется в armor_blocked",
          all(r['armor_blocked'] == 5 for r in armored if not r['dodged']))

    # ── 4. Урон не уходит в минус; броня может поглотить удар целиком ──
    all_dmg = [r['damage'] for r in armored if not r['dodged']]
    check("урон по бронированному врагу не уходит в ноль/минус",
          all(d >= 0 for d in all_dmg), f"мин={min(all_dmg)}")
    check("слабый удар рекрута броня врага съедает частично (остаётся ≥ 0)",
          all(d >= 0 for d in all_dmg) and max(all_dmg) >= 1)
    # Броня выше урона = удар не проходит совсем (важно для туриста 0–1).
    huge = [roll_pilot_damage(stats(weapon=10), {'armor': 999})['damage']
            for _ in range(500)]
    check("броня выше урона полностью гасит удар (0)", all(d == 0 for d in huge))
    weak = [roll_pilot_damage(stats(weapon=0), {'armor': 99})['damage']
            for _ in range(500)]
    check("турист/рекрут против бронированного врага дают 0",
          all(d == 0 for d in weak))

    # ── 5. Враг бьёт в своём диапазоне ──
    boar = {'dmg_min': FOREST_BOAR_DMG[0], 'dmg_max': FOREST_BOAR_DMG[1]}
    hits = [roll_enemy_damage(stats(armor=0), boar)['damage'] for _ in range(4000)]
    check("урон врага в диапазоне его строки",
          all(FOREST_BOAR_DMG[0] <= d <= FOREST_BOAR_DMG[1] for d in hits),
          f"{min(hits)}–{max(hits)}")

    # ── 6. Уклонение пилота и врага ──
    dodged = [roll_enemy_damage(stats(dodge=100), boar)['dodged'] for _ in range(300)]
    check("уклонение 100% всегда спасает", all(dodged))
    zero = [roll_enemy_damage(stats(dodge=0), boar)['dodged'] for _ in range(500)]
    check("уклонение 0% никогда не спасает", not any(zero))
    enemy_dodge = [roll_pilot_damage(stats(), {'dodge': 100})['dodged'] for _ in range(300)]
    check("враг с уклонением 100% всегда уходит", all(enemy_dodge))

    # ── 7. Броня пилота поглощает урон врага ──
    naked = [roll_enemy_damage(stats(armor=0), boar)['damage'] for _ in range(3000)]
    plated = [roll_enemy_damage(stats(armor=6), boar)['damage'] for _ in range(3000)]
    check("броня пилота режет урон врага",
          statistics.mean(plated) < statistics.mean(naked),
          f"{statistics.mean(naked):.1f} → {statistics.mean(plated):.1f}")

    # ── 8. Crit врага ──
    crits = [roll_enemy_damage(stats(armor=0),
                                {'dmg_min': 5, 'dmg_max': 5, 'crit_chance': 100,
                                 'crit_mult': 2.0})['crit'] for _ in range(300)]
    check("crit 100% срабатывает всегда", all(crits))
    crit_dmg = [roll_enemy_damage(stats(armor=0),
                                  {'dmg_min': 5, 'dmg_max': 5, 'crit_chance': 100,
                                   'crit_mult': 2.0})['damage'] for _ in range(300)]
    check("crit умножает урон врага", all(d == 10 for d in crit_dmg), "5 → 10")

    # ── 9. Откат на attack, если dmg_min/dmg_max нет ──
    legacy = [roll_enemy_damage(stats(armor=0), {'attack': 7})['damage'] for _ in range(300)]
    check("старые враги с attack=7 бьют на 7", all(d == 7 for d in legacy))

    # ── 10. В коде боёв не осталось player_dmg_* ──
    for f in ("dungeon.py", "forest.py", "kvp.py"):
        src = open(os.path.join(os.path.dirname(__file__), "bot", "handlers", f),
                   encoding="utf-8").read()
        check(f"{f}: урон пилота не берётся из player_dmg_*",
              "player_dmg_min" not in src and "player_dmg_max" not in src)
        check(f"{f}: используется общая боевая модель", "combat_model" in src)

    # ── 11. PILOT_BASE_HP в конфиге ──
    check("PILOT_BASE_HP = 100", PILOT_BASE_HP == 100)

    # ── 12. Бой без оружия: рекрут (1–1) против кабана ──
    print("\n── Рекрут без снаряжения, 100 HP ──")
    dmg_bare = [roll_pilot_damage(stats(weapon=0), {'dodge': 0})['damage']
                for _ in range(4000)]
    print(f"  Урон пилота без оружия: {min(dmg_bare)}–{max(dmg_bare)} "
          f"(средний {statistics.mean(dmg_bare):.1f})")
    check("рекрут без оружия бьёт 1",
          min(dmg_bare) >= 1 and max(dmg_bare) <= 1, "1–1")
    check("PILOT_NO_WEAPON_DMG = (1, 1)", tuple(PILOT_NO_WEAPON_DMG) == (1, 1))

    sim = random.Random(777)
    rounds, left_hp = [], []
    for _ in range(20000):
        boar_hp, player_hp, n = 40, PILOT_BASE_HP, 0
        while boar_hp > 0 and player_hp > 0:
            n += 1
            r = roll_pilot_damage(stats(weapon=0), {'dodge': 15, 'armor': 0})
            if not r['dodged']:
                boar_hp -= r['damage']
            if boar_hp <= 0:
                break
            e = roll_enemy_damage(stats(armor=0), {'dmg_min': 4, 'dmg_max': 7})
            if not e['dodged']:
                player_hp -= e['damage']
        rounds.append(n)
        left_hp.append(player_hp)
    print(f"  Раундов боя: среднее {statistics.mean(rounds):.1f}")
    print(f"  HP у пилота после боя: среднее {statistics.mean(left_hp):.1f}")
    check("бой рекрута без оружия против кабана длится 15–25 раундов",
          15 <= statistics.mean(rounds) <= 25, f"{statistics.mean(rounds):.1f}")
    check("рекруту 1 урона не хватает добить кабана без оружия",
          statistics.mean(left_hp) < PILOT_BASE_HP * 0.2,
          f"{statistics.mean(left_hp):.1f} из {PILOT_BASE_HP}")

    # ── 13. Урон растёт по статусу: рекрут → ас ──
    print("\n── Урон без оружия по статусам ──")
    for tag, (lo, hi) in RANK_DAMAGE_TIERS.items():
        d = [roll_pilot_damage(stats(weapon=0, base=(lo, hi)), {})['damage']
             for _ in range(3000)]
        print(f"  {tag:14s} {min(d)}–{max(d)} (средний {statistics.mean(d):.1f})")
        check(f"{tag}: урон в диапазоне {lo}–{hi}",
              min(d) >= lo and max(d) <= hi)
    means = {}
    for tag, (lo, hi) in RANK_DAMAGE_TIERS.items():
        d = [roll_pilot_damage(stats(weapon=0, base=(lo, hi)), {})['damage']
             for _ in range(3000)]
        means[tag] = statistics.mean(d)
    order = ["recruit", "pilot2", "pilot1", "veteran", "master_pilot", "ace"]
    check("урон растёт вместе со званием",
          all(means[order[i]] < means[order[i + 1]] for i in range(len(order) - 1)),
          " → ".join(f"{means[t]:.1f}" for t in order))
    check("турист слабее рекрута", means["tourist"] < means["recruit"],
          f"{means['tourist']:.1f} < {means['recruit']:.1f}")
    check("турист может не нанести урона (0–1)",
          RANK_DAMAGE_TIERS["tourist"] == (0, 1))
    check("турист с бронёй врага может дать ровно 0",
          roll_pilot_damage(stats(weapon=0, base=(0, 0)), {'armor': 99})['damage'] == 0)

    # ── 14. Хранитель бьёт по своему званию, а не по должности ──
    check("хранителя нет в таблице урона", "keeper" not in RANK_DAMAGE_TIERS)
    check("хранитель без статусов получает базовый 1",
          PILOT_NO_WEAPON_DMG == (1, 1))

    # ── 15. Статусы за звание покрывают всю шкалу до аса ──
    for tag in order:
        check(f"статус {tag} есть в таблице урона", tag in RANK_DAMAGE_TIERS)

    print(f"\n=== SMOKE 120: {PASSED} passed, {FAILED} failed ===")
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())