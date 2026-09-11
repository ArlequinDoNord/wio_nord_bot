import os
from dotenv import load_dotenv

load_dotenv()

# Семантическое версионирование (SemVer): MAJOR.MINOR.PATCH
# - PATCH (x.x.1): исправление ошибок / мелкие правки
# - MINOR (x.1.x): новая функциональность (обратно совместимая)
# - MAJOR (1.x.x): крупные ломающие изменения (до 1.0 — на усмотрение)
# Стартуем с 0.1.0 (нестабильная фаза).
VERSION = "0.5.2"

# Краткое описание изменений текущей сборки (показывается в заставке приветствия
# под строкой «Версия сборки»). Обновлять при каждом бампе VERSION.
VERSION_NOTES = "Жильё покупается как переезд: подтверждение «заменит текущее», мебель возвращается в инвентарь. Магазин предупреждает о нехватке средств. Рыбалка блокируется в подземелье; от босса нельзя убежать. Маркер остатка наживки при забросе."

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]

# Чат для игровых оповещений (группа), если задан
_news_raw = os.getenv("NEWS_CHAT_ID", "").strip()
NEWS_CHAT_ID = int(_news_raw) if _news_raw.lstrip("-").isdigit() else None

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
    "housing": "Жильё",
    "furniture": "Мебель и расширения",
    "seeds": "Семена",
    "equipment": "Снаряжение",
    "resource": "Ресурсы",
    "special": "Особое",
    "souvenirs": "Сувениры",
    "library_card": "Читательские билеты",
    "fishing": "Рыбалка",
}

AP_MAX = 150
AP_DAILY_RECOVERY = 100
AP_BONUS_FROM_CONSUMABLE = 50

# Лимит ДОПОЛНИТЕЛЬНОГО восстановления ОД через расходники за сутки.
# Естественный запас — 150 ОД (ap_max). Сверху можно восстановить ещё 150 ОД,
# а при достижении лимита наступает состояние «истощён» (передозировка).
AP_DAILY_RESTORE_LIMIT = 150
AP_EXHAUSTED_MINUTES = 2880          # 2 суток
AP_EXHAUSTED_DAILY_RECOVERY = 75     # суточное восстановление в «истощении»
AP_EXHAUSTED_MAX_AP = 90             # максимум ОД в «истощении»

# Водоросли: лимит применения в сутки (при превышении — «несварение»)
SEAWEED_DAILY_LIMIT = 6
DIGESTIVE_UPSET_MINUTES = 1440       # 24 часа

# Рыбалка
FISH_AP_COST = 3                     # стоимость одного заброса удочки

# Вес улова: от него зависит цена продажи (множитель к базовой цене).
# Разница между «Мелкой» и «Большой» — 30% стоимости. key хранится в БД как
# индекс +1 (small=1, medium=2, large=3).
FISH_WEIGHTS = [
    {"key": "small",  "label": "Мелкая",  "mult": 1.00, "chance": 40},
    {"key": "medium", "label": "Средняя", "mult": 1.15, "chance": 40},
    {"key": "large",  "label": "Большая", "mult": 1.30, "chance": 20},
]

REPORT_DAILY_LIMIT = 3
REPORT_AUTO_APPROVE_TROOPS = 100
REPORT_MAX_TROOPS = 1000000
REPORT_MAX_REGION = 38  # 0 = Столица, 1..38 регионы

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
