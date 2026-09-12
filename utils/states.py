"""Система состояний игроков.

У игрока может быть несколько состояний одновременно (users.state — список ключей
через запятую, users.state_effects — JSON dict {ключ: effects}). Состояния влияют
на бой и на доступ к местам. Выдают их админ, предметы или игровые события;
снятие — по истечении срока каждого состояния или админом.

Дальше это расширится предметами-статусами, которые можно применять на других.
"""

import json
from datetime import datetime, timedelta

from database.db import (
    get_user, set_user_state, clear_user_state, remove_user_state,
)

# Ключи мест, которые могут блокироваться состояниями
PLACE_LABELS = {
    "townhall": "🏛️ Ратуша",
    "library": "📚 Библиотека",
}

# Конфигурация состояний: боевые модификаторы и блокируемые места
STATE_CONF = {
    "пьян": {
        "emoji": "🍺",
        "title": "Пьян",
        "default_minutes": 60,
        "attack_mult": 0.8,          # атака −20%
        "dodge_mult": 0.7,           # уклонение −30%
        "blocks": ["townhall", "library"],
        "hint": "Выпил лишнего. В Ратушу и Библиотеку не пускают, в бою руки не слушаются.",
    },
    "очень пьян": {
        "emoji": "🥴",
        "title": "Очень пьян",
        "default_minutes": 360,      # 6 часов
        "attack_mult": 0.5,          # атака −50%
        "dodge_mult": 0.5,           # уклонение −50%
        # Блокирует все места с механикой входа.
        "blocks": ["__all__"],
        "blocks_consumables": True,  # нельзя применять расходники/зелья
        "replaces": ["пьян"],        # при наложении заменяет менее сильное состояние
        "hint": "Ты едва держишься на ногах: атака и уклонение сильно снижены, "
                "зелья и расходники недоступны, вход во все здания закрыт. Пройдёт через 6 часов.",
    },
    "истощён": {
        "emoji": "🥵",
        "title": "Истощён",
        "default_minutes": 2880,     # 2 суток
        "blocks": [],
        "hint": "Истощение от перегрузки ОД: лимит восстановления за сутки исчерпан. "
                "Восстановление 75 ОД/сутки, максимум 90 ОД.",
    },
    "несварение": {
        "emoji": "🤢",
        "title": "Несварение",
        "default_minutes": 1440,     # 24 часа
        "blocks": [],
        "blocks_consumables": True,  # нельзя применять расходники (в т.ч. +ОД)
        "hint": "Слишком много водорослей! Нельзя применять расходники (в том числе для восстановления ОД). "
                "Пройдёт через сутки.",
    },
}

NORMAL = "нормально"


def state_keys() -> list:
    return list(STATE_CONF.keys())


def place_blocked(state_names: list, place: str) -> bool:
    """Блокирует ли место хотя бы одно из активных состояний.

    Состояние с blocks=["__all__"] блокирует все места с механикой входа.
    """
    for name in state_names:
        conf = STATE_CONF.get(name)
        if not conf:
            continue
        blocks = conf.get('blocks', [])
        if "__all__" in blocks or place in blocks:
            return True
    return False


def consumables_blocked(state_names: list) -> list:
    """Состояния, которые запрещают применение расходников/зелий."""
    return [n for n in state_names
            if STATE_CONF.get(n, {}).get('blocks_consumables')]


def combat_multipliers(state_names: list) -> dict:
    """Боевые модификаторы из всех активных состояний (перемножаются)."""
    result = {}
    for name in state_names:
        conf = STATE_CONF.get(name)
        if not conf:
            continue
        for key in ("attack_mult", "dodge_mult"):
            if key in conf:
                result[key] = result.get(key, 1.0) * conf[key]
    result = {k: v for k, v in result.items() if v != 1.0}
    return result


def _parse_effects(effects_str):
    if effects_str and effects_str != "{}":
        try:
            return json.loads(effects_str)
        except (ValueError, TypeError):
            return {}
    return {}


async def get_state_info(user_id: int) -> dict:
    """Возвращает все активные состояния игрока (с учётом истечения сроков).

    Результат: {"name": "Пьян, Истощён"|"нормально",
                "names": ["пьян", "истощён"],
                "states": [{"key", "title", "emoji", "minutes_left", "effects", "conf"}, ...]}
    """
    user = await get_user(user_id)
    if not user:
        return {"name": NORMAL, "names": [NORMAL], "states": [], "conf": None}
    user = dict(user)
    state_col = user.get('state') or NORMAL
    effects = _parse_effects(user.get('state_effects') or "{}")

    names = [n for n in state_col.split(", ") if n and n != NORMAL] if state_col != NORMAL else []
    states = []
    for key in names:
        conf = STATE_CONF.get(key)
        if not conf:
            continue
        eff = effects.get(key) or {}
        minutes_left = None
        if eff.get('applied_at'):
            try:
                applied = datetime.strptime(eff['applied_at'], "%Y-%m-%d %H:%M:%S")
                end = applied + timedelta(minutes=int(eff.get('minutes', 0)))
                minutes_left = max(0, int((end - datetime.now()).total_seconds() // 60))
            except (ValueError, TypeError, KeyError):
                minutes_left = None
        states.append({
            "key": key,
            "title": conf['title'],
            "emoji": conf['emoji'],
            "minutes_left": minutes_left,
            "effects": eff,
            "conf": conf,
        })

    if states:
        display = ", ".join(f"{s['conf']['emoji']} {s['conf']['title']}" for s in states)
        return {"name": display, "names": [s['key'] for s in states],
                "states": states, "conf": states[-1]['conf']}
    return {"name": NORMAL, "names": [NORMAL], "states": [], "conf": None}


def format_state_line(info: dict) -> str:
    """Строка состояния для профиля/карточки. "" если состояние нормальное.

    Одно состояние: «🍺 Состояние: Пьян (12 мин.)»
    Несколько:      «Состояния: 🍺 Пьян (12 мин.), 🥵 Истощён (2 мин.)»
    """
    states = info.get('states') or []
    if not states:
        return ""
    parts = []
    for s in states:
        minutes = s['minutes_left']
        time_part = f" ({minutes} мин.)" if minutes is not None else ""
        parts.append(f"{s['emoji']} {s['title']}{time_part}")
    word = "Состояние" if len(parts) == 1 else "Состояния"
    return f"{word}: {', '.join(parts)}"


async def apply_state_to(user_id: int, state_key: str, caused_by: int = None,
                         minutes: int = None, reason: str = "", meta: dict = None):
    conf = STATE_CONF[state_key]
    minutes = minutes or conf['default_minutes']

    # Усиленный вариант заменяет более слабое состояние (напр. «очень пьян» → «пьян»).
    for prev in conf.get('replaces') or []:
        await remove_user_state(user_id, prev, caused_by,
                                reason=f"заменено на «{conf['title']}»")

    await set_user_state(user_id, state_key, minutes, caused_by, reason, meta)


async def clear_state_of(user_id: int, state_key: str = None, caused_by: int = None,
                         reason: str = "состояние снято"):
    """Снять одно состояние либо все (state_key=None)."""
    if state_key is None:
        await clear_user_state(user_id, caused_by, reason)
    else:
        await remove_user_state(user_id, state_key, caused_by, reason)


async def is_place_blocked(user_id: int, place: str) -> bool:
    info = await get_state_info(user_id)
    return place_blocked(info['names'], place)


async def blocked_places_text(user_id: int) -> str:
    info = await get_state_info(user_id)
    if not info['states']:
        return ""
    labels = []
    for s in info['states']:
        blocks = s['conf'].get('blocks', [])
        if "__all__" in blocks:
            return "все здания и локации"
        for p in blocks:
            if p in PLACE_LABELS and PLACE_LABELS[p] not in labels:
                labels.append(PLACE_LABELS[p])
    return ", ".join(labels)