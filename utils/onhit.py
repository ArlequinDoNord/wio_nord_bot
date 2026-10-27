"""Единая система эффектов при ударе врага (v0.38.0).

Каждый враг хранит свой список эффектов в колонке on_hit_effects
(JSON-массив: [{"kind": "bleed", "chance": 25, "dmg": 4}, ...]) — см.
ON_HIT_EFFECTS в config.py. При каждом попавшем ответном ударе каждый
эффект бросается независимо; прошедшие пишутся в store боя (store['on_hit']),
длительность считается в ходах:

  * bleed / poison  — без rounds_left: живут до конца боя, текут HP/ход;
  * frostbite       — rounds_left ходов (лечение ×0.5);
  * state (ключи STATE_CONF, enemy_appliable) — rounds_left ходов:
    модификаторы атаки/крита/уклонения читаются через battle_state_keys()
    в pilot_combat_stats, блок расходников — consumables_blocked_by_battle().

Store боя: обычный dict боя (лес/мышь/змея/моллюск) либо FSM-данные забега
данжа. ACTIVE — реестр user_id → store для блокировки расходников вне
боевых хендлеров (process_item_use). Очистку (unregister/clear) делают боевые
хендлеры при победе/поражении/побеге/конце забега.
"""

import json
import random

from config import ON_HIT_EFFECTS, ON_HIT_STATE_ROUNDS
from utils.states import STATE_CONF

# Пользователи с активными боевыми эффектами: user_id -> store.
ACTIVE = {}


def parse_on_hit_effects(raw) -> list:
    """Колонка on_hit_effects (JSON-строка) → список dict-эффектов."""
    if not raw:
        return []
    if isinstance(raw, list):
        data = raw
    else:
        try:
            data = json.loads(raw)
        except (ValueError, TypeError):
            return []
    if not isinstance(data, list):
        return []
    return [e for e in data
            if isinstance(e, dict) and e.get('kind') in ON_HIT_EFFECTS]


def get_store(store: dict) -> dict:
    """Лениво создаёт dict активных эффектов в store боя."""
    if not isinstance(store.get('on_hit'), dict):
        store['on_hit'] = {}
    return store['on_hit']


def register(user_id: int, store: dict):
    ACTIVE[user_id] = store


def unregister(user_id: int):
    ACTIVE.pop(user_id, None)


def clear(store: dict):
    store.pop('on_hit', None)


def consumables_blocked_by_battle(user_id: int):
    """Текст блокировки расходников от боевого эффекта, либо None.

    Ищет среди активных боевых эффектов состояния с blocks_consumables
    («оглушён» и далее — см. STATE_CONF).
    """
    store = ACTIVE.get(user_id)
    if not store:
        return None
    on_hit = store.get('on_hit') or {}
    for key in on_hit:
        conf = STATE_CONF.get(key)
        if conf and conf.get('blocks_consumables'):
            return (f"{conf['emoji']} {conf['title']}: в бою сейчас нельзя "
                    f"применять расходники и зелья.")
    return None


def battle_state_keys(store: dict) -> list:
    """Ключи STATE_CONF из активных боевых эффектов (для pilot_combat_stats)."""
    return [k for k in (store.get('on_hit') or {}) if k in STATE_CONF]


def roll_procs(effects: list) -> list:
    """Независимые броски каждого эффекта врага. Возвращает прошедшие procs."""
    procs = []
    for eff in effects or ():
        kind = eff.get('kind')
        conf = ON_HIT_EFFECTS.get(kind)
        if not conf:
            continue
        if kind == "lifesteal":
            chance = int(eff.get('chance') or 0)
            if chance <= 0:
                continue
            if random.randint(1, 100) > chance:
                continue
            procs.append({
                "kind": "lifesteal",
                "pct": max(0, int(eff.get('pct') or eff.get('heal_pct') or 0)),
            })
            continue
        chance = int(eff.get('chance') or 0)
        if chance <= 0:
            continue
        if random.randint(1, 100) > chance:
            continue
        proc = {"kind": kind}
        if kind in ("bleed", "poison"):
            proc["dmg"] = max(1, int(eff.get('dmg') or 1))
        elif kind == "frostbite":
            proc["rounds"] = max(1, int(eff.get('rounds')
                                        or conf.get('default_rounds') or 4))
        elif kind == "state":
            key = eff.get('key')
            if key not in STATE_CONF:
                continue
            proc["key"] = key
            proc["rounds"] = max(1, int(eff.get('rounds')
                                        or ON_HIT_STATE_ROUNDS.get(key) or 3))
        procs.append(proc)
    return procs


def roll_lifesteal(effects: list) -> dict | None:
    """Бросок эффекта lifesteal из пула on_hit_effects."""
    procs = roll_procs(effects or [])
    for proc in procs:
        if proc.get('kind') == 'lifesteal':
            return proc
    return None


def apply_lifesteal_to_attacker(hp: int, hp_max: int, damage_dealt: int,
                                eff: dict | None) -> tuple[int, int, str | None]:
    """Лечение атакующего от процента нанесённого урона. lifesteal в коде."""
    if not eff or eff.get('kind') != 'lifesteal':
        return int(hp), 0, None
    pct = max(0, int(eff.get('pct') or eff.get('heal_pct') or 0))
    if pct <= 0 or damage_dealt <= 0:
        return int(hp), 0, None
    healed = max(1, int((int(damage_dealt) * pct + 99) // 100))
    hp_max = max(1, int(hp_max or hp))
    new_hp = min(hp_max, int(hp) + healed)
    healed = max(0, new_hp - int(hp))
    if healed <= 0:
        return int(hp), 0, None
    return new_hp, healed, f"🩸 Кровопийца: +{healed} HP"


def apply_procs(user_id: int, store: dict, procs: list, enemy_name: str = "Враг") -> list:
    """Пишет прошедшие эффекты в store боя; возвращает фразы для текста боя."""
    on_hit = get_store(store)
    register(user_id, store)
    lines = []
    for proc in procs:
        kind = proc['kind']
        if kind == "lifesteal":
            continue
        if kind == "bleed":
            on_hit['bleed'] = {"dmg": proc['dmg']}
            lines.append(f"🩸 {enemy_name} ранил тебя! Кровотечение: "
                         f"−{proc['dmg']} HP каждый ход до конца боя.")
        elif kind == "poison":
            on_hit['poison'] = {"dmg": proc['dmg']}
            lines.append(f"☠️ {enemy_name} отравил тебя! Яд: "
                         f"−{proc['dmg']} HP каждый ход до конца боя.")
        elif kind == "frostbite":
            on_hit['frostbite'] = {"rounds_left": proc['rounds']}
            lines.append(f"💧 {enemy_name} окутал тебя морозом! Обморожение: "
                         f"лечение −50%, {proc['rounds']} ход(ов).")
        elif kind == "state":
            key = proc['key']
            sconf = STATE_CONF[key]
            on_hit[key] = {"rounds_left": proc['rounds']}
            lines.append(f"{sconf['emoji']} {enemy_name} накладывает "
                         f"«{sconf['title']}» ({proc['rounds']} ход(ов)): "
                         f"{sconf['hint']}")
    return lines


def tick_dots(store: dict) -> tuple:
    """Откат HP-DoT (кровотечение/яд) в начале хода. → (урон, фразы)."""
    on_hit = store.get('on_hit') or {}
    dmg = 0
    lines = []
    bleed = on_hit.get('bleed')
    if isinstance(bleed, dict):
        d = int(bleed.get('dmg') or 0)
        dmg += d
        lines.append(f"🩸 Кровотечение: −{d} HP.")
    poison = on_hit.get('poison')
    if isinstance(poison, dict):
        d = int(poison.get('dmg') or 0)
        dmg += d
        lines.append(f"☠️ Яд: −{d} HP.")
    return dmg, lines


def end_round(store: dict) -> list:
    """Спад срочных эффектов (frostbite/state) в конце хода. → фразы."""
    on_hit = get_store(store)
    lines = []
    for key in list(on_hit.keys()):
        eff = on_hit[key]
        if not isinstance(eff, dict) or 'rounds_left' not in eff:
            continue
        eff['rounds_left'] = int(eff['rounds_left']) - 1
        if eff['rounds_left'] <= 0:
            del on_hit[key]
            if key in STATE_CONF:
                conf = STATE_CONF[key]
                lines.append(f"{conf['emoji']} {conf['title']} прошло.")
            else:
                kconf = ON_HIT_EFFECTS.get(key, {})
                lines.append(f"{kconf.get('emoji', '')} "
                             f"{kconf.get('title', key)} прошло.")
    return lines


def frostbite_active(store: dict) -> bool:
    return isinstance((store.get('on_hit') or {}).get('frostbite'), dict)


def has_dot(store: dict, kind: str) -> bool:
    """Есть ли активный DoT указанного вида (bleed/poison)."""
    return isinstance((store.get('on_hit') or {}).get(kind), dict)


def heal_multiplier(store: dict) -> float:
    """Множитель лечения: обморожение — ×0.5, иначе 1.0."""
    return 0.5 if frostbite_active(store) else 1.0


def active_line(store: dict) -> str:
    """Строка активных эффектов для экрана боя ("" если их нет)."""
    on_hit = store.get('on_hit') or {}
    parts = []
    bleed = on_hit.get('bleed')
    if isinstance(bleed, dict):
        parts.append(f"🩸 Кровотечение −{int(bleed.get('dmg') or 0)} HP/ход")
    poison = on_hit.get('poison')
    if isinstance(poison, dict):
        parts.append(f"☠️ Яд −{int(poison.get('dmg') or 0)} HP/ход")
    if frostbite_active(store):
        parts.append("💧 Обморожение (лечение −50%)")
    for key in on_hit:
        conf = STATE_CONF.get(key)
        if not conf:
            continue
        eff = on_hit[key]
        rounds = eff.get('rounds_left') if isinstance(eff, dict) else None
        suffix = f" ({rounds} х.)" if rounds is not None else ""
        parts.append(f"{conf['emoji']} {conf['title']}{suffix}")
    return "; ".join(parts)
