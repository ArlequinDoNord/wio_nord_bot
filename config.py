import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]

# Путь к базе данных (aiosqlite)
DB_PATH = os.getenv("DATABASE_PATH", "database/nordmark.db")

RANKS = [
    ("Рекрут", 0),
    ("Рядовой", 50),
    ("Капрал", 150),
    ("Сержант", 350),
    ("Лейтенант", 700),
    ("Капитан", 1200),
    ("Майор", 2000),
    ("Подполковник", 3500),
    ("Полковник", 5500),
    ("Генерал-майор", 8000),
    ("Генерал-лейтенант", 12000),
    ("Генерал", 20000),
]

RARITY_LEVELS = {
    1: "Обычный",
    2: "Качественный",
    3: "Редкий",
    4: "Шедевр",
    5: "Легендарный",
}

RARITY_EMOJI = {
    1: "⬜",
    2: "🟩",
    3: "🟦",
    4: "🟪",
    5: "🟧",
}

ITEM_CATEGORIES = {
    "weapon": "Оружие",
    "consumable": "Расходники",
    "building": "Недвижимость",
    "equipment": "Снаряжение",
    "resource": "Ресурсы",
    "special": "Особое",
}

AP_MAX = 150
AP_DAILY_RECOVERY = 100
AP_BONUS_FROM_CONSUMABLE = 50

REPORT_AUTO_APPROVE_TROOPS = 500

# --- Система званий (на основе войск) ---


def get_rank(troops: int) -> str:
    rank = RANKS[0][0]
    for rank_name, required in RANKS:
        if troops >= required:
            rank = rank_name
        else:
            break
    return rank


def get_next_rank(troops: int) -> tuple:
    for rank_name, required in RANKS:
        if troops < required:
            return rank_name, required
    return RANKS[-1][0], RANKS[-1][1]


def get_rank_index(troops: int) -> int:
    for i, (rank_name, required) in enumerate(RANKS):
        if troops < required:
            return max(0, i - 1)
    return len(RANKS) - 1
