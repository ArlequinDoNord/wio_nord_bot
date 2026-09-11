"""Система состояний игроков.

Состояние (users.state + users.state_effects JSON) влияет на бой и на доступ
к местам. Сейчас состояния выдаёт админ; снятие — по истечении срока или админом.

Дальше это расширится предметами-статусами, которые можно применять на других.
"""

import json
from datetime import datetime, timedelta

from database.db import (
    get_user, set_user_state, clear_user_state, drop_expired_state,
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
        "hint": "Слишком много водорослей! Нельзя применять расходники (в том числе для восстановления ОД). "
                "Пройдёт через сутки.",
    },
}

NORMAL = "нормально"


def state_keys() -> list:
    return list(STATE_CONF.keys())


def place_blocked(state_name: str, place: str) -> bool:
    conf = STATE_CONF.get(state_name)
    return bool(conf and place in conf.get('blocks', []))


def combat_multipliers(state_name: str) -> dict:
    conf = STATE_CONF.get(state_name)
    if not conf:
        return {}
    return {key: conf[key] for key in ("attack_mult", "dodge_mult") if key in conf}


def _parse_effects(effects_str):
    if effects_str and effects_str != "{}":
        try:
            return json.loads(effects_str)
        except (ValueError, TypeError):
            return {}
    return {}


async def get_state_info(user_id: int) -> dict:
    """Возвращает актуальное состояние игрока (с учётом истечения срока).

    Результат: {"name": "пьян", "minutes_left": 12, "effects": {...}, "conf": {...}}
    """
    user = await get_user(user_id)
    if not user:
        return {"name": NORMAL, "minutes_left": None, "effects": {}, "conf": None}
    user = dict(user)
    state = user.get('state') or NORMAL
    effects_str = user.get('state_effects') or "{}"
    refreshed = await drop_expired_state(user_id, state, effects_str)
    if refreshed != state:
        state = refreshed
        effects_str = "{}"
    effects = _parse_effects(effects_str)
    conf = STATE_CONF.get(state)

    minutes_left = None
    if conf and effects.get('applied_at'):
        try:
            applied = datetime.strptime(effects['applied_at'], "%Y-%m-%d %H:%M:%S")
            end = applied + timedelta(minutes=int(effects.get('minutes', 0)))
            minutes_left = max(0, int((end - datetime.now()).total_seconds() // 60))
        except (ValueError, TypeError, KeyError):
            minutes_left = None

    return {"name": state, "minutes_left": minutes_left, "effects": effects, "conf": conf}


def format_state_line(info: dict) -> str:
    """Строка состояния для профиля/карточки. "" если состояние нормальное."""
    conf = info['conf']
    if not conf:
        return ""
    minutes = info['minutes_left']
    time_part = f" ({minutes} мин.)" if minutes is not None else ""
    return f"{conf['emoji']} Состояние: {conf['title']}{time_part}"


async def apply_state_to(user_id: int, state_key: str, caused_by: int = None,
                         minutes: int = None, reason: str = "", meta: dict = None):
    conf = STATE_CONF[state_key]
    minutes = minutes or conf['default_minutes']
    await set_user_state(user_id, state_key, minutes, caused_by, reason, meta)


async def clear_state_of(user_id: int, caused_by: int = None, reason: str = "состояние снято"):
    await clear_user_state(user_id, caused_by, reason)


async def is_place_blocked(user_id: int, place: str) -> bool:
    info = await get_state_info(user_id)
    return place_blocked(info['name'], place)


async def blocked_places_text(user_id: int) -> str:
    info = await get_state_info(user_id)
    if not info['conf']:
        return ""
    labels = [PLACE_LABELS[p] for p in info['conf'].get('blocks', []) if p in PLACE_LABELS]
    return ", ".join(labels) if labels else ""