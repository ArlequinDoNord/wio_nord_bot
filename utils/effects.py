"""Словарь эффектов боя: правила совмещения DoT на цели (враг или пилот).

DoT-словарь цели: {вид: {"dmg": урон за ход, "ticks": ходов осталось}}.
- яд и кровотечение совмещаются; повторное наложение того же вида обновляет его;
- горение и обморожение взаимно гасят друг друга: при наложении снимаются оба.
"""

DOT_KINDS = ("poison", "bleed", "burn", "frostbite")

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
