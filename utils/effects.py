"""Словарь эффектов боя: правила совмещения DoT на цели (враг или пилот).

DoT-словарь цели: {вид: {"dmg": урон за ход, "ticks": ходов осталось}}.
- яд и кровотечение совмещаются; повторное наложение того же вида обновляет его;
- горение и обморожение взаимно гасят друг друга: при наложении снимаются оба.
"""

DOT_KINDS = ("poison", "bleed", "burn", "frostbite")
# Все виды эффектов, которые может получить враг (включая оглушение и заморозку).
ENEMY_EFFECT_KINDS = ("poison", "bleed", "burn", "frostbite", "stun")


def parse_resist(raw) -> dict:
    """Разбирает иммунитеты/сопротивления врага. Пустое или битое — без защиты."""
    import json
    data = raw
    if isinstance(raw, (str, bytes)):
        try:
            data = json.loads(raw) if raw else {}
        except (ValueError, TypeError):
            data = {}
    if not isinstance(data, dict):
        data = {}
    immune = [k for k in (data.get("immune") or []) if k in ENEMY_EFFECT_KINDS]
    resist = {}
    for k, v in (data.get("resist") or {}).items():
        if k in ENEMY_EFFECT_KINDS:
            try:
                resist[k] = min(1.0, max(0.0, float(v)))
            except (TypeError, ValueError):
                continue
    return {"immune": immune, "resist": resist}


def is_immune(resist: dict, kind: str) -> bool:
    return kind in (resist or {}).get("immune", [])


def effective_chance(chance: int, resist: dict, kind: str) -> int:
    """Шанс наложения с учётом сопротивления вида (доля 0.5 — вдвое реже)."""
    mult = (resist or {}).get("resist", {}).get(kind, 1.0)
    return max(0, int(round(int(chance) * float(mult))))

# Какой вид гасит наложение другого (оба снимаются, новый не накладывается).
CANCELS = {"burn": "frostbite", "frostbite": "burn"}


def apply_dot(dots: dict, kind: str, dmg: int, ticks: int) -> dict:
    """Накладывает DoT на цель. Возвращает {"applied": bool, "cancelled": вид или None}."""
    opposite = CANCELS.get(kind)
    if opposite and opposite in dots:
        del dots[opposite]
        return {"applied": False, "cancelled": opposite}
    dots[kind] = {"dmg": max(1, int(dmg)), "ticks": max(1, int(ticks))}
    return {"applied": True, "cancelled": None}


def tick_dots(dots: dict) -> tuple:
    """Тик всех DoT цели: урон за ход и список (вид, урон). Спавшие виды удаляются."""
    total = 0
    parts = []
    for kind in list(dots):
        entry = dots[kind]
        dmg = int(entry.get("dmg") or 0)
        total += dmg
        parts.append((kind, dmg))
        left = int(entry.get("ticks") or 0) - 1
        if left <= 0:
            del dots[kind]
        else:
            entry["ticks"] = left
    return total, parts
