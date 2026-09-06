import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]

# Путь к базе данных (aiosqlite)
DB_PATH = os.getenv("DATABASE_PATH", "database/nordmark.db")

RANKS = [
    ("Рекрут", 0),
    ("Рядовой", 100),
    ("Капрал", 250),
    ("Сержант", 550),
    ("Лейтенант", 1500),
    ("Капитан", 3500),
    ("Майор", 7000),
    ("Подполковник", 11000),
    ("Полковник", 15000),
    ("Генерал-майор", 22000),
    ("Генерал-лейтенант", 33000),
    ("Генерал", 50000),
]

# До этого звания (по войскам) пилот набирает войска через отчёты;
# свыше — только ручная выдача главным админом/МВД.
MAX_SELF_RANK_TROOPS = 1500

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
    "souvenirs": "Сувениры",
    "library_card": "Читательские билеты",
}

AP_MAX = 150
AP_DAILY_RECOVERY = 100
AP_BONUS_FROM_CONSUMABLE = 50

REPORT_AUTO_APPROVE_TROOPS = 100

# --- Система званий (на основе войск) ---


AUTO_PROMOTE_MAX_TROOPS = 1500


def get_rank(troops: int) -> str:
    """Звание по войскам (автоматическое, до любого уровня)."""
    rank = RANKS[0][0]
    for rank_name, required in RANKS:
        if troops >= required:
            rank = rank_name
        else:
            break
    return rank


def get_effective_rank(troops: int, promoted_rank: str = None) -> str:
    """Звание для отображения: если есть admin-назначение — используем его,
    иначе автоматическое, но не выше Лейтенанта."""
    if promoted_rank:
        return promoted_rank
    rank = RANKS[0][0]
    for rank_name, required in RANKS:
        if troops >= required:
            rank = rank_name
        else:
            break
    if rank not in ("Рекрут", "Рядовой", "Капрал", "Сержант", "Лейтенант"):
        rank = "Лейтенант"
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
