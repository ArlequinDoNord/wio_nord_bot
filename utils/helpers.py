from config import RARITY_LEVELS, RARITY_EMOJI


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
