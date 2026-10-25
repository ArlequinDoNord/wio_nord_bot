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
    # Благословения Белого Волка Севера (лес). Суточные, положительные: усиливают
    # бой, лечение и цены. Пока активно любое из них — волк не встречается снова.
    "внимание севера": {
        "emoji": "❄️",
        "title": "Внимание Севера",
        "default_minutes": 1440,     # 24 часа
        "attack_mult": 1.05,         # урон +5%
        "dodge_mult": 1.05,          # уклонение +5%
        "hint": "Белый Волк Севера заметил тебя и отпустил. +5% к урону и "
                "уклонению на сутки. Пока действует — волк не придёт снова.",
    },
    "благословение севера": {
        "emoji": "🌟",
        "title": "Благословение Севера",
        "default_minutes": 1440,     # 24 часа
        "attack_mult": 1.10,         # атака +10%
        "dodge_mult": 1.10,          # уклонение +10%
        "heal_pct": 5,               # эффективность лечения +5%
        "shop_discount": 3,          # цены в магазинах −3%
        "hint": "Боги Нордхайма отметили тебя за встречу с Белым Волком: "
                "+10% к атаке и уклонению, +5% к лечению, −3% к ценам в магазинах "
                "на сутки. Пока действует — волк не придёт снова.",
    },
    # Ослепление Неясытью (Лесозаготовка): боевое состояние, накладывается
    # врагом в бою на ходы (единая система эффектов при ударе, v0.38.0) и
    # админом вручную (минуты). Снижает урон («шанс попадания» проявляется
    # как слабые промахивающиеся удары) и уклонение: в темноте и цели мельче,
    # и увернуться труднее.
    "ослеплён": {
        "emoji": "🌑",
        "title": "Ослеплён",
        "default_minutes": 30,
        "attack_mult": 0.7,          # атака −30%
        "dodge_mult": 0.5,           # уклонение −50%
        "enemy_appliable": True,     # враг может наложить в бою (на ходы)
        "hint": "Неясыть ослепила тебя: в темноте удары мимо цели, "
                "уклонение едва работает.",
    },
    # Оглушение (v0.38.0): враг оглушает на ходы боя — точность и крит
    # снижаются, уклонение хуже, расходники/зелья недоступны. Крит множится
    # отдельным полем crit_mult (см. combat_multipliers).
    "оглушён": {
        "emoji": "💫",
        "title": "Оглушён",
        "default_minutes": 5,        # для ручной выдачи админом
        "attack_mult": 0.7,          # точность: слабые промахивающиеся удары
        "crit_mult": 0.5,            # шанс крита −50%
        "dodge_mult": 0.5,           # уклонение −50%
        "blocks_consumables": True,  # расходники/зелья запрещены
        "enemy_appliable": True,     # враг может наложить в бою (на ходы)
        "hint": "Оглушение: точность, крит и уклонение снижены, "
                "расходники недоступны.",
    },
}

# Благословения Белого Волка Севера: пока активно любое — волк не встречается.
BLESSING_STATES = ("внимание севера", "благословение севера")

# Состояния, которые враг может наложить при ударе (пул пикера в админке
# редактора врагов, v0.38.0). Новое вражеское состояние = флаг enemy_appliable.
def enemy_appliable_states() -> list:
    return [k for k, c in STATE_CONF.items() if c.get("enemy_appliable")]

NORMAL = "нормально"

# Состояния опьянения: их укорачивают душевая и ванная (см. bot/handlers/housing.py).
DRUNK_STATES = ("пьян", "очень пьян")


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
        for key in ("attack_mult", "dodge_mult", "crit_mult"):
            if key in conf:
                result[key] = result.get(key, 1.0) * conf[key]
    result = {k: v for k, v in result.items() if v != 1.0}
    return result


def battle_state_multipliers(state_keys: list) -> dict:
    """Боевые модификаторы из СОСТОЯНИЙ, наложенных врагом в бою.

    Те же поля STATE_CONF (attack_mult/dodge_mult/crit_mult), что и у
    глобальных состояний, но источник — эффекты текущего боя (kind='state'),
    а не users.state. Перемножаются между собой.
    """
    result = {}
    for key in state_keys:
        conf = STATE_CONF.get(key)
        if not conf:
            continue
        for mkey in ("attack_mult", "dodge_mult", "crit_mult"):
            if mkey in conf:
                result[mkey] = result.get(mkey, 1.0) * conf[mkey]
    result = {k: v for k, v in result.items() if v != 1.0}
    return result


def state_heal_pct(state_names: list) -> int:
    """Суммарный бонус к эффективности лечения (%) от активных состояний."""
    total = 0
    for name in state_names:
        conf = STATE_CONF.get(name) or {}
        total += int(conf.get('heal_pct', 0) or 0)
    return total


def state_shop_discount(state_names: list) -> int:
    """Суммарная скидка в магазинах (%) от активных состояний."""
    total = 0
    for name in state_names:
        conf = STATE_CONF.get(name) or {}
        total += int(conf.get('shop_discount', 0) or 0)
    return total


def is_blessed(state_names: list) -> bool:
    """Есть ли у игрока активное благословение Белого Волка Севера."""
    return any(n in BLESSING_STATES for n in state_names)


async def get_heal_bonus_pct(user_id: int) -> int:
    """Бонус к лечению (%) из активных состояний игрока."""
    info = await get_state_info(user_id)
    return state_heal_pct(info['names'])


async def get_shop_discount_pct(user_id: int) -> int:
    """Скидка в магазинах (%) из активных состояний игрока."""
    info = await get_state_info(user_id)
    return state_shop_discount(info['names'])


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


async def reduce_state_minutes(user_id: int, state_keys, minutes: int,
                               caused_by: int = None, reason: str = "") -> list:
    """Сократить остаток указанных состояний на `minutes` (не ниже нуля).

    Остаток считается по `applied_at + minutes`, поэтому сокращение переписывает
    состояние через set_user_state с новым остатком (applied_at = сейчас):
    эффект не продлевается, а именно укорачивается. Если остаток дошёл до нуля,
    состояние снимается совсем. Возвращает список изменений для текста игроку:
    [{"key", "title", "before", "after", "removed"}, ...].
    """
    if not state_keys or not minutes or int(minutes) <= 0:
        return []
    wanted = set(state_keys)
    cut = int(minutes)
    info = await get_state_info(user_id)
    changes = []
    for s in info.get('states') or []:
        key = s['key']
        if key not in wanted:
            continue
        left = s.get('minutes_left')
        if left is None:
            eff = s.get('effects') or {}
            left = int(eff.get('minutes') or s['conf'].get('default_minutes') or 0)
        left = max(0, int(left))
        new_left = max(0, left - cut)
        note = reason or f"сокращено на {cut} мин. ({key})"
        if new_left <= 0:
            await remove_user_state(user_id, key, caused_by, note)
        else:
            await set_user_state(user_id, key, new_left, caused_by, note)
        changes.append({
            "key": key,
            "title": s['title'],
            "before": left,
            "after": new_left,
            "removed": new_left <= 0,
        })
    return changes


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