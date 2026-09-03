from config import RARITY_LEVELS, RARITY_EMOJI


def format_amount(amount: int) -> str:
    return f"{amount:,}".replace(",", " ")


def rarity_label(rarity: int) -> str:
    return RARITY_LEVELS.get(rarity, "Обычный")


def rarity_emoji(rarity: int) -> str:
    return RARITY_EMOJI.get(rarity, "⬜")


def category_label(category: str) -> str:
    from config import ITEM_CATEGORIES
    return ITEM_CATEGORIES.get(category, category)
