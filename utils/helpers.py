from datetime import datetime, timedelta, timezone

from config import RARITY_LEVELS, RARITY_EMOJI

MOSCOW_TZ = timezone(timedelta(hours=3))

# Периоды времени суток (по московскому времени):
DAWN = (8, 0, 8, 10)    # рассвет: 08:00–08:10
SUNSET = (19, 0, 19, 10)  # закат: 19:00–19:10


def plural_nordmark(n: int) -> str:
    """Склонение слова «нордмарка» в зависимости от числа."""
    n_abs = abs(n)
    n10 = n_abs % 10
    n100 = n_abs % 100
    if n10 == 1 and n100 != 11:
        return "нордмарка"
    if 2 <= n10 <= 4 and not (12 <= n100 <= 14):
        return "нордмарки"
    return "нордмарок"


def format_amount(amount: int) -> str:
    return f"{amount:,}".replace(",", " ")


def rarity_label(rarity: int) -> str:
    return RARITY_LEVELS.get(rarity, "Обычный")


def rarity_emoji(rarity: int) -> str:
    return RARITY_EMOJI.get(rarity, "⬜")


def category_label(category: str) -> str:
    from config import ITEM_CATEGORIES
    return ITEM_CATEGORIES.get(category, category)


def time_of_day_key(now: datetime | None = None) -> str:
    """Возвращает ключ времени суток по московскому времени (UTC+3).

    dawn   — 08:00–08:10
    day    — 08:10–19:00
    sunset — 19:00–19:10
    night  — 19:10–08:00
    """
    now = (now or datetime.now()).astimezone(MOSCOW_TZ)
    minutes = now.hour * 60 + now.minute

    dawn_start = DAWN[0] * 60 + DAWN[1]
    dawn_end = DAWN[2] * 60 + DAWN[3]
    sunset_start = SUNSET[0] * 60 + SUNSET[1]
    sunset_end = SUNSET[2] * 60 + SUNSET[3]

    if dawn_start <= minutes < dawn_end:
        return "dawn"
    if sunset_start <= minutes < sunset_end:
        return "sunset"
    if dawn_end <= minutes < sunset_start:
        return "day"
    return "night"


def resolve_image(base_key: str, now: datetime | None = None) -> str:
    """Собирает путь к картинке по базовому ключу и времени суток.

    Пример: "city/arkholm" -> "assets/img/city/arkholm_day.jpg"
    """
    return f"assets/img/{base_key}_{time_of_day_key(now)}.jpg"
