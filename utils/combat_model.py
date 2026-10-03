"""Единая боевая модель для всех поединков.

Пилот атакует СВОИМ уроном: базовый урон по статусу (config.RANK_DAMAGE_TIERS —
«Ас» 4–8, «Ветеран» 2–4 и так далее) + урон оружия, затем бонусы наград и
состояния. Снаряжение врага (armor) поглощает часть урона, враг может
увернуться или crit'нуть. Каждый враг держит СВОИ параметры: hp, диапазон
урона dmg_min..dmg_max, dodge, armor, crit_chance/crit_mult.

Раньше лес и подземелья брали урон пилота из строки врага (player_dmg_min/max),
из-за чего снаряжение и награды не влияли на бой. Здесь считает только пилот.
"""
import random

from config import PILOT_BASE_HP, PILOT_NO_WEAPON_DMG
from utils.combat import roll_dodge
from utils.states import combat_multipliers, get_state_info


async def pilot_combat_stats(user_id: int) -> dict:
    """Боевые характеристики пилота: урон, уклонение, броня, макс. HP."""
    from database.db import (get_award_bonus, get_pilot_base_damage,
                             get_player_armor_with_bonus, get_player_dodge,
                             get_player_weapon_damage)

    weapon_damage = await get_player_weapon_damage(user_id)
    state_info = await get_state_info(user_id)
    mult = combat_multipliers(state_info['names'])
    bonus = await get_award_bonus(user_id)
    base_lo, base_hi = await get_pilot_base_damage(user_id)

    attack_mult = mult.get('attack_mult', 1.0) * (1.0 + bonus['attack'] / 100.0)
    return {
        'base_dmg': (int(base_lo), int(base_hi)),
        'weapon_damage': weapon_damage,
        'attack_mult': attack_mult,
        'dodge': await get_player_dodge(user_id, mult.get('dodge_mult', 1.0)),
        'armor': await get_player_armor_with_bonus(user_id),
        'hp_max': PILOT_BASE_HP + int(bonus.get('hp') or 0),
        'award_attack': bonus['attack'],
    }


def _enemy_range(enemy) -> tuple:
    """Диапазон урона врага: dmg_min..dmg_max, с откатом на attack."""
    lo = enemy.get('dmg_min') if isinstance(enemy, dict) else None
    hi = enemy.get('dmg_max') if isinstance(enemy, dict) else None
    if not lo or not hi:
        atk = enemy.get('attack') or 0 if isinstance(enemy, dict) else 0
        return int(atk), int(atk)
    return int(lo), int(hi)


def roll_pilot_damage(stats: dict, enemy) -> dict:
    """Удар пилота по врагу: базовый урон по статусу + оружие, затем броня и
    уклонение врага.

    Базовый урон берётся из stats['base_dmg'] — это RANK_DAMAGE_TIERS по самому
    сильному статусу игрока (без оружия это 1–1 у рекрута, 4–8 у аса, 0–1 у туриста).
    Снаряжение прибавляется к базе, дальше бонусы наград и состояния.

    Возвращает: damage (сколько HP снято), dodged, raw, armor_blocked, crit.
    """
    lo, hi = stats.get('base_dmg') or PILOT_NO_WEAPON_DMG
    raw = random.randint(int(lo), int(hi)) + int(stats.get('weapon_damage') or 0)
    raw = max(0, int(raw * stats['attack_mult']))

    enemy_dodge = int(enemy.get('dodge') or enemy.get('dodge_chance') or 0)
    if roll_dodge(enemy_dodge):
        return {'damage': 0, 'dodged': True, 'raw': raw, 'armor_blocked': 0, 'crit': False}

    damage = raw
    crit = False
    crit_chance = int(enemy.get('crit_chance') or 0)
    if crit_chance and random.randint(1, 100) <= crit_chance:
        damage = int(round(damage * float(enemy.get('crit_mult') or 1.5)))
        crit = True

    enemy_armor = int(enemy.get('armor') or 0)
    blocked = min(damage, enemy_armor)
    # Турист (0–1) может не нанести урона совсем, поэтому минимум — 0,
    # а не 1: иначе «может вообще не ударить» не получится.
    damage = max(0, damage - enemy_armor)
    return {'damage': damage, 'dodged': False, 'raw': raw,
            'armor_blocked': blocked, 'crit': crit}


def roll_enemy_damage(stats: dict, enemy) -> dict:
    """Удар врага по пилоту: свой диапазон урона, crit, поглощение бронёй."""
    player_dodge = int(stats.get('dodge') or 0)
    if roll_dodge(player_dodge):
        return {'damage': 0, 'dodged': True, 'raw': 0, 'armor_blocked': 0, 'crit': False}

    lo, hi = _enemy_range(enemy)
    if hi < lo:
        lo, hi = hi, lo
    damage = random.randint(lo, hi) if hi > 0 else random.randint(1, 4)

    crit = False
    crit_chance = int(enemy.get('crit_chance') or 0)
    if crit_chance and random.randint(1, 100) <= crit_chance:
        damage = int(round(damage * float(enemy.get('crit_mult') or 1.5)))
        crit = True

    armor = int(stats.get('armor') or 0)
    blocked = min(damage, armor)
    damage = max(1, damage - armor)
    return {'damage': damage, 'dodged': False, 'raw': damage + blocked,
            'armor_blocked': blocked, 'crit': crit}


def enemy_hp(enemy, default: int = 1) -> int:
    return int(enemy.get('hp') or default)