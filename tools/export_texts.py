# -*- coding: utf-8 -*-
"""TEXTS_CATALOG.md — единый каталог ВСЕХ текстов, которые видит игрок.

Разделы (темы):
  1. Интерфейс и кнопки — utils/i18n.py (STRINGS, ru/en)
  2. Боевые тексты — встроены из BATTLE_TEXTS.md
  3. Сущности из БД: предметы, локации, подземелья, враги, награды, рецепты,
     статусы, книги, постройки, памятники
  4. «Тексты в коде» — приложение: русские строки из bot/, utils/, keyboards/
     и main.py, которые ещё не вынесены в i18n

Актуализация (обязательно перед деплоем):
  * в заголовке файла лежит отпечаток источников
    `<!-- texts-catalog: code=… seeds=… db=… -->`;
  * `--check` падает, если изменились тексты в коде (`code`) или состав
    текстов в сидах (`seeds`), а каталог не перегенерирован;
  * разделы сущностей при генерации всегда собираются из снимка прод-БД
    + прогон сидов сверху, поэтому новинки из кода попадают в каталог
    ещё до деплоя.

Запуск:
    .venv\\Scripts\\python.exe tools\\export_texts.py --db путь\\к\\nordmark.db
    .venv\\Scripts\\python.exe tools\\export_texts.py --from-seeds [--db база.db]
    .venv\\Scripts\\python.exe tools\\export_texts.py --check
    .venv\\Scripts\\python.exe tools\\export_texts.py        # без БД: обновит
        # только разделы из кода, разделы сущностей возьмёт из файла

База по умолчанию: переменная окружения DATABASE_PATH, иначе ./data/nordmark.db.
Для актуализации на боевых данных: скачать прод-БД и передать через --db.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "TEXTS_CATALOG.md")
BATTLE = os.path.join(ROOT, "BATTLE_TEXTS.md")
BUILD_SEEDS = os.path.join(ROOT, "tools", "build_seed_db.py")

MARKER_RE = re.compile(r"<!-- texts-catalog: code=([0-9a-f]+) seeds=([0-9a-f]+) db=([0-9a-f]+) -->")
DB_START = "<!-- texts-catalog-db:start -->"
DB_END = "<!-- texts-catalog-db:end -->"

# ── Тексты в коде ───────────────────────────────────────────────────────────
CODE_DIRS = ("bot", "utils", "keyboards")
CODE_FILES = ("main.py",)
# i18n разбирается отдельно (раздел «Интерфейс и кнопки») — не дублируем.
CODE_SKIP_FILES = {"utils/i18n.py"}
CYR_RE = re.compile(r"[А-Яа-яЁё]")
SQL_RE = re.compile(
    r"\b(SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP|PRAGMA|REPLACE|FROM|WHERE|JOIN|VALUES)\b")

CATEGORY_RU = {
    "weapon": "оружие",
    "armor": "броня",
    "equipment": "снаряжение",
    "consumable": "расходники и еда",
    "resource": "ресурсы",
    "fishing": "рыба",
    "fish": "рыба",
    "food": "еда",
    "tool": "инструменты",
    "housing": "жильё",
    "furniture": "мебель",
    "building": "постройки",
    "mining": "шахта и руда",
    "seeds": "семена",
    "recipes": "рецепты-предметы",
    "license": "лицензии",
    "special": "особые",
    "souvenirs": "сувениры",
    "duel_card": "карты дуэли",
    "duel_gear": "снаряжение дуэли",
    "library_card": "библиотечные карты",
    "book": "книги",
    "junk": "хлам",
    "treasure": "сокровища",
    "artifact": "артефакты",
}

# Порядок разделов в каталоге: сначала ходовое, потом служебное.
CATEGORY_ORDER = [
    "weapon", "armor", "equipment", "consumable", "resource", "fishing",
    "mining", "seeds", "housing", "furniture", "building", "tool",
    "recipes", "license", "duel_card", "duel_gear", "library_card",
    "souvenirs", "special", "junk", "treasure", "artifact", "food", "fish",
]

# Подписи для групп ключей интерфейса (префикс до первой точки).
UI_GROUP_RU = {
    "btn": "кнопки главного меню",
    "menu": "общие экраны",
    "lang": "переключение языка",
    "city": "город",
    "profile": "профиль",
    "rarity": "редкость предметов",
    "sell": "продажа",
    "shop": "магазин",
    "inv": "инвентарь",
    "inventory": "инвентарь",
    "market": "рынок игроков",
    "bank": "банк и штрафы",
    "fines": "штрафы",
    "clan": "клан",
    "clanh": "клан-холл",
    "forest": "лес",
    "dungeon": "подземелье",
    "mine": "шахта",
    "kvp": "К.В.П.",
    "fish": "рыбалка",
    "fishing": "рыбалка",
    "housing": "жильё",
    "cook": "кухня",
    "craft": "крафт",
    "job": "работа",
    "report": "отчёты",
    "news": "новости",
    "admin": "админка",
    "award": "награды",
    "status": "статусы",
    "duel": "дуэли",
    "contract": "контракты",
    "nii": "НИИ",
    "library": "библиотека",
    "book": "книги",
    "error": "ошибки",
    "common": "общее",
}

ENEMY_SOURCES = (
    ("forest", "Лес и Белый Волк Севера", "forest_enemies"),
    ("dungeon", "Подземелье", "dungeon_enemies"),
    ("reservoir", "Водохранилище / моллюск", "fishing_enemies"),
    ("mine", "Шахта / Железная копия", "mine_enemies"),
    ("logging", "Лесозаготовка", "logging_enemies"),
    ("firelab", "Огненный Лабиринт", "firelab_enemies"),
)

# Таблицы, тексты которых сверяются отпечатком сидов (имя + описание).
SEED_SIGNATURES = (
    "items", "locations", "dungeons", "forest_enemies", "dungeon_enemies",
    "fishing_enemies", "mine_enemies", "logging_enemies", "firelab_enemies",
    "awards", "recipes", "statuses", "library_books", "park_statues", "buildings",
)


# ────────────────────────────────────────────────────────────────────────────
# Общие помощники
# ────────────────────────────────────────────────────────────────────────────

def connect(path):
    conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def db_connection(path):
    conn = connect(path)
    try:
        yield conn
    finally:
        conn.close()


def has_table(conn, name):
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,)).fetchone()
    return row is not None


def text(value):
    return "" if value is None else str(value)


def block(heading, meta, body, empty_note="—"):
    """Элемент каталога: заголовок, метаданные, описание."""
    body = text(body)
    lines = [f"### {heading}"]
    if meta:
        lines.append(f"- {meta}")
    if body.strip():
        body_lines = body.splitlines() or [""]
        lines.append(f"- описание: {body_lines[0].strip()}")
        for extra in body_lines[1:]:
            lines.append(f"  {extra.strip()}")
    else:
        lines.append(f"- описание: {empty_note}")
    return "\n".join(lines)


def ui_block(key, variants):
    """Элемент интерфейсной строки: RU/EN в цитатах (сохраняют любые символы)."""
    lines = [f"### UI-{key}"]
    for lang in ("ru", "en"):
        value = text(variants.get(lang, ""))
        lines.append(f"- {lang.upper()}:")
        if value.strip():
            for part in value.splitlines():
                lines.append(f"  > {part}" if part else "  >")
        else:
            lines.append("  > —")
    return "\n".join(lines)


def digest(parts):
    h = hashlib.sha256()
    for part in parts:
        h.update(part.encode("utf-8"))
        h.update(b"\n")
    return h.hexdigest()[:16]


# ────────────────────────────────────────────────────────────────────────────
# Тексты в коде (AST)
# ────────────────────────────────────────────────────────────────────────────

class CodeTextVisitor(ast.NodeVisitor):
    """Собирает русские строки, группируя их по файлу и функции."""

    def __init__(self, rel_path, skip_ids):
        self.rel_path = rel_path
        self.skip_ids = skip_ids
        self.stack = []
        self.items = []  # (rel_path, func, text)

    # контекст функции/класса
    def visit_FunctionDef(self, node):
        self.stack.append(node.name)
        self.generic_visit(node)
        self.stack.pop()

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, node):
        self.stack.append(node.name)
        self.generic_visit(node)
        self.stack.pop()

    def _add(self, node, value):
        if id(node) in self.skip_ids:
            return
        value = value.strip()
        if len(value) < 2 or not CYR_RE.search(value):
            return
        if SQL_RE.search(value):
            return
        func = ".".join(self.stack) if self.stack else "(модуль)"
        self.items.append((self.rel_path, func, value))

    def visit_Constant(self, node):
        if isinstance(node.value, str):
            self._add(node, node.value)

    def visit_JoinedStr(self, node):
        parts = []
        for value in node.values:
            if isinstance(value, ast.Constant):
                parts.append(str(value.value))
            elif isinstance(value, ast.FormattedValue):
                inner = value.value
                if isinstance(inner, ast.Name):
                    parts.append("{" + inner.id + "}")
                else:
                    parts.append("{…}")
        self._add(node, "".join(parts))


def _docstring_ids(tree):
    out = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            body = getattr(node, "body", [])
            if (body and isinstance(body[0], ast.Expr)
                    and isinstance(body[0].value, ast.Constant)
                    and isinstance(body[0].value.value, str)):
                out.add(id(body[0].value))
    return out


def _non_player_ids(tree):
    """id узлов внутри logger/print/raise/re.compile — это не тексты игрока."""
    out = set()

    def collect(node):
        for sub in ast.walk(node):
            out.add(id(sub))

    for node in ast.walk(tree):
        if isinstance(node, ast.Raise):
            if node.exc is not None:
                collect(node.exc)
            continue
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        name = ""
        if isinstance(func, ast.Attribute):
            name = func.attr
            if isinstance(func.value, ast.Name):
                name = func.value.id + "." + func.attr
        elif isinstance(func, ast.Name):
            name = func.id
        if (name.startswith("logger.") or name.startswith("logging.")
                or name in ("print", "re.compile", "warnings.warn")):
            for arg in node.args:
                collect(arg)
    return out


def _iter_code_files():
    for directory in CODE_DIRS:
        base_dir = os.path.join(ROOT, directory)
        for base, _dirs, names in os.walk(base_dir):
            if "__pycache__" in base:
                continue
            for name in sorted(names):
                if not name.endswith(".py"):
                    continue
                yield os.path.join(base, name)
    for name in CODE_FILES:
        yield os.path.join(ROOT, name)


def scan_code_texts():
    """Возвращает отсортированный список (файл, функция, текст) без повторов."""
    seen = set()
    out = []
    for path in _iter_code_files():
        rel = os.path.relpath(path, ROOT).replace("\\", "/")
        if rel in CODE_SKIP_FILES:
            continue
        try:
            with open(path, encoding="utf-8") as fh:
                tree = ast.parse(fh.read())
        except (SyntaxError, OSError) as exc:
            print(f"warning: {rel} пропущен ({exc})", file=sys.stderr)
            continue
        visitor = CodeTextVisitor(rel, _docstring_ids(tree) | _non_player_ids(tree))
        visitor.visit(tree)
        for item in visitor.items:
            if item in seen:
                continue
            seen.add(item)
            out.append(item)
    out.sort(key=lambda item: (item[0], item[1], item[2]))
    return out


def render_code_texts(entries):
    body = [
        f"Всего текстов: **{len(entries)}** (уникальные вхождения по файлам и функциям).",
        "",
        "> Эти строки пока живут прямо в коде (не в `utils/i18n.py`). Раздел нужен для",
        "> полноты: по нему видно всё, что игрок может увидеть. Новые тексты лучше сразу",
        "> заводить ключами в `utils/i18n.py` (ru + en) — тогда они попадут в раздел",
        "> «Интерфейс и кнопки» с переводом. Здесь правки переносятся по тексту в",
        "> указанной функции соответствующего файла.",
        "",
    ]
    by_file = {}
    for rel, func, value in entries:
        by_file.setdefault(rel, {}).setdefault(func, []).append(value)
    for rel in sorted(by_file):
        body.append(f"#### `{rel}` ({sum(len(v) for v in by_file[rel].values())})")
        body.append("")
        for func in sorted(by_file[rel]):
            body.append(f"##### `{func}`")
            body.append("")
            for value in sorted(by_file[rel][func]):
                lines = value.splitlines() or [""]
                body.append(f"- {lines[0]}")
                for extra in lines[1:]:
                    body.append(f"  {extra}" if extra else "  ")
            body.append("")
    return body


# ────────────────────────────────────────────────────────────────────────────
# Отпечатки источников
# ────────────────────────────────────────────────────────────────────────────

def i18n_strings():
    if ROOT not in sys.path:
        sys.path.insert(0, ROOT)
    from utils.i18n import STRINGS  # noqa: WPS433 (осознанный импорт проекта)

    return STRINGS


def code_fingerprint(entries=None):
    entries = scan_code_texts() if entries is None else entries
    parts = []
    for key in sorted(i18n_strings()):
        variants = i18n_strings()[key]
        for lang in ("ru", "en"):
            parts.append(f"ui|{key}|{lang}|{text(variants.get(lang, ''))}")
    if os.path.exists(BATTLE):
        with open(BATTLE, encoding="utf-8") as fh:
            parts.append("battle|" + fh.read())
    for rel, func, value in entries:
        parts.append(f"code|{rel}|{func}|{value}")
    return digest(parts)


def seed_signature_lines(db_path):
    conn = connect(db_path)
    try:
        lines = []
        for table in SEED_SIGNATURES:
            if not has_table(conn, table):
                continue
            columns = [row[1] for row in conn.execute(f"PRAGMA table_info({table})")]
            identity = next((c for c in ("key", "name", "title") if c in columns), None)
            if identity is None:
                continue
            select = [identity, "description"] if "description" in columns else [identity]
            for row in conn.execute(
                    f"SELECT {', '.join(select)} FROM {table}"):
                values = [" ".join(text(v).split()) for v in row]
                lines.append("|".join([table] + values))
        lines.sort()
        return lines
    finally:
        conn.close()


def seed_fingerprint(db_path):
    return digest(seed_signature_lines(db_path))


# ────────────────────────────────────────────────────────────────────────────
# Временная БД: сиды поверх снимка
# ────────────────────────────────────────────────────────────────────────────

@contextmanager
def seeded_db(base_path=None):
    """Создаёт временную БД: сиды кода (и, если задан, снимок прод-БД сверху)."""
    tmp_dir = tempfile.mkdtemp(prefix="texts_catalog_")
    path = os.path.join(tmp_dir, "seed.db")
    try:
        cmd = [sys.executable, BUILD_SEEDS, path, "--quiet"]
        if base_path:
            cmd += ["--base", base_path]
        env = dict(os.environ)
        env["PYTHONIOENCODING"] = "utf-8"
        result = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True,
                                encoding="utf-8", errors="replace")
        if result.returncode != 0:
            sys.stderr.write(result.stdout or "")
            sys.stderr.write(result.stderr or "")
            raise SystemExit("Не удалось собрать БД из сидов (tools/build_seed_db.py).")
        yield path
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


# ────────────────────────────────────────────────────────────────────────────
# Разделы из кода
# ────────────────────────────────────────────────────────────────────────────

def render_ui():
    strings = i18n_strings()
    groups = {}
    for key in sorted(strings):
        prefix = key.split(".", 1)[0]
        groups.setdefault(prefix, []).append(key)

    body = [
        f"Всего строк: **{len(strings)}** (ru + en).",
        "",
        "> `{...}` — подстановки (`{name}`, `{qty}`, `{price}` и т.п.). "
        "Их нельзя удалять или переименовывать — только переставлять.",
        "> Кнопки ловятся по ключу, поэтому менять сам текст кнопки безопасно.",
        "",
    ]
    for prefix in sorted(groups):
        title = UI_GROUP_RU.get(prefix, prefix)
        body.append(f"#### {title} · `{prefix}.` ({len(groups[prefix])})")
        body.append("")
        for key in groups[prefix]:
            body.append(ui_block(key, strings[key]))
            body.append("")
    return body


def render_battle():
    """Боевые тексты: встраиваем BATTLE_TEXTS.md (заголовки на уровень ниже)."""
    if not os.path.exists(BATTLE):
        return ["_BATTLE_TEXTS.md не найден._"]
    with open(BATTLE, encoding="utf-8") as fh:
        lines = fh.read().splitlines()

    # Убираем H1 и шапку до первого разделителя ---
    start = 0
    for idx, line in enumerate(lines):
        if line.strip() == "---":
            start = idx + 1
            break
    lines = lines[start:]
    while lines and not lines[0].strip():
        lines.pop(0)

    out = [
        "> Раздел встроен из `BATTLE_TEXTS.md` (источник правок боевых текстов).",
        "> Правила те же: правьте блок «✏️ НОВЫЙ», «ТЕКУЩИЙ» — ориентир.",
        "> После применения правок обновляются код, смоуки и `BATTLE_TEXTS.md`.",
    ]
    in_fence = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
        if not in_fence and line.startswith("#"):
            line = "#" + line
        out.append(line)
    return out


# ────────────────────────────────────────────────────────────────────────────
# Разделы из БД
# ────────────────────────────────────────────────────────────────────────────

def render_items(conn):
    rows = conn.execute(
        "SELECT id, name, description, rarity, category, price, sell_price, "
        "is_available, loot_only FROM items ORDER BY category, name").fetchall()
    by_cat = {}
    for r in rows:
        by_cat.setdefault(text(r["category"]) or "—", []).append(r)
    body = [f"Всего: **{len(rows)}**.", ""]
    for cat in sorted(by_cat, key=lambda c: (
            CATEGORY_ORDER.index(c) if c in CATEGORY_ORDER else len(CATEGORY_ORDER), c)):
        body.append(f"#### {CATEGORY_RU.get(cat, cat)} ({len(by_cat[cat])})")
        body.append("")
        for r in by_cat[cat]:
            meta = (f"редкость: {r['rarity']} · категория: {cat} · "
                    f"цена: {r['price']} / скупщик: {r['sell_price']} · "
                    f"в продаже: {'да' if r['is_available'] else 'нет'}"
                    f"{' · только лут' if r['loot_only'] else ''}")
            body.append(block(f"ITEM-{r['id']} · {r['name']}", meta, r["description"]))
            body.append("")
    return body


def render_locations(conn):
    rows = conn.execute(
        "SELECT id, key, name, description, access_mode, required_status "
        "FROM locations ORDER BY id").fetchall()
    body = [f"Всего: **{len(rows)}**.", ""]
    for r in rows:
        meta = f"ключ: `{r['key']}` · доступ: {r['access_mode']}"
        if text(r["required_status"]):
            meta += f" · статус: {r['required_status']}"
        body.append(block(f"LOC-{r['key']} · {r['name']}", meta, r["description"]))
        body.append("")
    return body


def render_dungeons(conn):
    if not has_table(conn, "dungeons"):
        return None
    rows = conn.execute(
        "SELECT id, name, description, floors_count, rooms_per_floor, is_active, "
        "is_training FROM dungeons ORDER BY id").fetchall()
    if not rows:
        return None
    body = [f"Всего: **{len(rows)}**.", ""]
    for r in rows:
        meta = (f"этажей: {r['floors_count']} · комнат на этаже: {r['rooms_per_floor']} · "
                f"активно: {'да' if r['is_active'] else 'нет'}"
                f"{' · тренировочное' if r['is_training'] else ''}")
        body.append(block(f"DUN-{r['id']} · {r['name']}", meta, r["description"]))
        body.append("")
    return body


def render_enemies(conn):
    body = []
    total = 0
    for source, title, table in ENEMY_SOURCES:
        if not has_table(conn, table):
            continue
        rows = conn.execute(f"SELECT * FROM {table} ORDER BY id").fetchall()
        if not rows:
            continue
        total += len(rows)
        body.append(f"#### {title} ({len(rows)})")
        body.append("")
        for r in rows:
            keys = r.keys()
            meta_parts = [f"источник: {source}"]
            for column in ("spot", "hp", "chance", "enabled"):
                if column in keys and r[column] is not None:
                    meta_parts.append(f"{column}: {r[column]}")
            if "dmg_min" in keys and "dmg_max" in keys:
                meta_parts.append(f"урон: {r['dmg_min']}–{r['dmg_max']}")
            key = (text(r["key"]) if "key" in keys else "") or str(r["id"])
            body.append(block(f"FOE-{source}-{key} · {r['name']}",
                              " · ".join(meta_parts),
                              r["description"] if "description" in keys else ""))
            body.append("")
    if not total:
        return None
    return [f"Всего: **{total}**.", ""] + body


def render_awards(conn):
    rows = conn.execute("SELECT id, name, description, emoji FROM awards ORDER BY id").fetchall()
    body = [f"Всего: **{len(rows)}**.", ""]
    for r in rows:
        body.append(block(f"AWARD-{r['id']} · {r['name']}",
                          f"эмодзи: {text(r['emoji']) or '—'}", r["description"]))
        body.append("")
    return body


def render_recipes(conn):
    rows = conn.execute(
        "SELECT id, name, description, result_item_name, result_quantity, rarity, "
        "is_available, required_level FROM recipes ORDER BY id").fetchall()
    body = [f"Всего: **{len(rows)}**.", ""]
    for r in rows:
        meta = (f"результат: {r['result_item_name']} ×{r['result_quantity']} · "
                f"сложность (редкость рецепта): {r['rarity']} · "
                f"уровень: {r['required_level']} · "
                f"доступен: {'да' if r['is_available'] else 'нет'}")
        body.append(block(f"RECIPE-{r['id']} · {r['name']}", meta, r["description"]))
        body.append("")
    return body


def render_statuses(conn):
    rows = conn.execute(
        "SELECT id, name, description, access_tag, sort_order FROM statuses "
        "ORDER BY sort_order, id").fetchall()
    body = [f"Всего: **{len(rows)}**.", ""]
    for r in rows:
        meta = f"тег доступа: {text(r['access_tag']) or '—'} · порядок: {r['sort_order']}"
        body.append(block(f"STATUS-{r['id']} · {r['name']}", meta, r["description"]))
        body.append("")
    return body


def render_books(conn):
    if not has_table(conn, "library_books"):
        return None
    rows = conn.execute(
        "SELECT id, section, title, author, description FROM library_books "
        "ORDER BY section, title").fetchall()
    if not rows:
        return None
    body = [f"Всего: **{len(rows)}**.", ""]
    for r in rows:
        meta = f"раздел: {r['section']} · автор: {text(r['author']) or '—'}"
        body.append(block(f"BOOK-{r['id']} · {r['title']}", meta, r["description"]))
        body.append("")
    return body


def render_buildings(conn):
    if not has_table(conn, "buildings"):
        return None
    rows = conn.execute(
        "SELECT id, name, description FROM buildings ORDER BY id").fetchall()
    if not rows:
        return None
    body = [f"Всего: **{len(rows)}**.", ""]
    for r in rows:
        body.append(block(f"BUILDING-{r['id']} · {r['name']}", "", r["description"]))
        body.append("")
    return body


def render_statues(conn):
    if not has_table(conn, "park_statues"):
        return None
    rows = conn.execute(
        "SELECT id, name, description, sort_order FROM park_statues "
        "ORDER BY sort_order, id").fetchall()
    if not rows:
        return None
    body = [f"Всего: **{len(rows)}**.", ""]
    for r in rows:
        body.append(block(f"STATUE-{r['id']} · {r['name']}",
                          f"порядок: {r['sort_order']}", r["description"]))
        body.append("")
    return body


DB_RENDERERS = (
    ("предметы", "Предметы", render_items),
    ("локации", "Локации", render_locations),
    ("подземелья", "Подземелья", render_dungeons),
    ("враги", "Враги", render_enemies),
    ("награды", "Награды", render_awards),
    ("рецепты", "Рецепты", render_recipes),
    ("статусы", "Статусы", render_statuses),
    ("книги", "Книги", render_books),
    ("постройки", "Постройки", render_buildings),
    ("памятники", "Памятники", render_statues),
)


def render_db_sections(conn):
    """Возвращает ([(anchor, title, lines), ...], db_fingerprint)."""
    sections = []
    for anchor, title, renderer in DB_RENDERERS:
        content = renderer(conn)
        if content:
            sections.append((anchor, title, content))
    flat = []
    for _anchor, _title, content in sections:
        flat.extend(content)
    return sections, digest(flat)


def parse_db_block(file_text):
    """Достаёт разделы сущностей и db-отпечаток из ранее сгенерированного файла."""
    if DB_START not in file_text or DB_END not in file_text:
        raise SystemExit(
            "В TEXTS_CATALOG.md нет блока сущностей (маркеры texts-catalog-db).\n"
            "Перегенерируйте каталог с БД: tools/export_texts.py --db <снимок>")
    inner = file_text.split(DB_START, 1)[1].split(DB_END, 1)[0]
    pattern = re.compile(r'^<a id="([^"]+)"></a>\s*\n\s*\n## (.+)$', re.M)
    matches = list(pattern.finditer(inner))
    sections = []
    for idx, match in enumerate(matches):
        begin = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(inner)
        lines = inner[begin:end].strip("\n").splitlines()
        sections.append((match.group(1), match.group(2).strip(), lines))
    marker = MARKER_RE.search(file_text)
    return sections, marker.group(3)


# ────────────────────────────────────────────────────────────────────────────
# Сборка файла
# ────────────────────────────────────────────────────────────────────────────

def build_catalog(db_sections, db_fp, code_fp, seeds_fp, snapshot_note, entries):
    code_sections = [
        ("интерфейс", "Интерфейс и кнопки", render_ui()),
        ("боевые-тексты", "Боевые тексты", render_battle()),
    ]
    code_sections.append(("тексты-в-коде", "Тексты в коде (приложение)",
                          render_code_texts(entries)))

    out = []
    add = out.append
    add("# TEXTS_CATALOG.md — все тексты N.O.R.D. в одном файле")
    add("")
    add("> Единый каталог того, что видит игрок, разбитый по темам. Генерируется")
    add("> `tools/export_texts.py` из трёх источников: `utils/i18n.py` (интерфейс),")
    add("> `BATTLE_TEXTS.md` (боевые тексты) и БД (описания сущностей), плюс")
    add("> приложение с русскими строками, которые пока живут прямо в коде.")
    add(">")
    add("> **Как править:** меняйте сам текст. Служебные ID (`UI-…`, `ITEM-123`,")
    add("> `LOC-…`, `FOE-…`) не переименовывайте — по ним правки переносятся обратно.")
    add("> `{...}` — живые подстановки: удалять/переименовывать нельзя.")
    add("> Метаданные (редкость, цены, HP, шансы) — только справка, баланс правится")
    add("> отдельно и из каталога не переносится.")
    add(">")
    add("> Когда закончите — скажите агенту «примени TEXTS_CATALOG.md»: правки уйдут")
    add("> в `utils/i18n.py`, `BATTLE_TEXTS.md` + боевые хендлеры, код/БД и сиды,")
    add("> после чего каталог будет перегенерирован. Генератор **перезаписывает**")
    add("> этот файл, поэтому не храните правки только здесь.")
    add(">")
    add("> **Актуальность:** `tools/export_texts.py --check` сверяет отпечатки")
    add("> источников ниже. Изменили текст в коде или сиде — перегенерируйте каталог")
    add("> (проверка встроена в `tools/docs_check_sync.py` и `tools/release_bump.py`).")
    add("")
    add(f"<!-- texts-catalog: code={code_fp} seeds={seeds_fp} db={db_fp} -->")
    add("")
    add(f"_Снимок: {date.today().isoformat()} · {snapshot_note}_")
    add("")
    add("## Содержание")
    add("")
    for anchor, title, _content in code_sections:
        add(f"- [{title}](#{anchor})")
    for anchor, title, _content in db_sections:
        add(f"- [{title}](#{anchor})")
    add("")
    for anchor, title, content in code_sections[:2]:
        add(f'<a id="{anchor}"></a>')
        add("")
        add(f"## {title}")
        add("")
        for line in content:
            add(line)
        add("")
    add(DB_START)
    for anchor, title, content in db_sections:
        add(f'<a id="{anchor}"></a>')
        add("")
        add(f"## {title}")
        add("")
        for line in content:
            add(line)
        add("")
    add(DB_END)
    for anchor, title, content in code_sections[2:]:
        add(f'<a id="{anchor}"></a>')
        add("")
        add(f"## {title}")
        add("")
        for line in content:
            add(line)
        add("")
    return "\n".join(out).rstrip() + "\n"


def read_file(path):
    if not os.path.exists(path):
        return ""
    with open(path, encoding="utf-8") as fh:
        return fh.read()


# ────────────────────────────────────────────────────────────────────────────
# main
# ────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Генератор TEXTS_CATALOG.md")
    parser.add_argument("--db", default=os.environ.get("DATABASE_PATH")
                        or os.path.join(ROOT, "data", "nordmark.db"),
                        help="снимок БД (по умолчанию DATABASE_PATH / data/nordmark.db)")
    parser.add_argument("--out", default=OUT)
    parser.add_argument("--check", action="store_true",
                        help="не писать файл, только сверить отпечатки")
    parser.add_argument("--from-seeds", action="store_true",
                        help="собрать разделы сущностей из сидов кода (можно с --base через --db)")
    parser.add_argument("--raw-db", action="store_true",
                        help="не накатывать сиды на снимок БД (только для диагностики)")
    args = parser.parse_args()

    old = read_file(args.out)
    marker = MARKER_RE.search(old)
    stored = marker.groups() if marker else None

    db_path = os.path.abspath(args.db)
    have_db = not args.from_seeds and os.path.exists(db_path)

    entries = scan_code_texts()
    code_fp = code_fingerprint(entries)

    # Отпечаток сидов считается всегда — по свежей БД из кода.
    with seeded_db() as seed_path:
        seeds_fp = seed_fingerprint(seed_path)

    if args.check:
        if not stored:
            print("TEXTS_CATALOG.md: нет отпечатка источников (старый формат).")
            print("Перегенерируйте: tools/export_texts.py --db <снимок БД>")
            return 1
        bad = []
        if stored[0] != code_fp:
            bad.append("code — тексты в коде/i18n/BATTLE_TEXTS")
        if stored[1] != seeds_fp:
            bad.append("seeds — тексты сущностей в сидах")
        db_checked = False
        if have_db or args.raw_db:
            if args.raw_db:
                with db_connection(db_path) as conn:
                    _sections, db_fp = render_db_sections(conn)
            else:
                with seeded_db(db_path) as seeded:
                    with db_connection(seeded) as conn:
                        _sections, db_fp = render_db_sections(conn)
            db_checked = True
            if stored[2] != db_fp:
                bad.append("db — разделы сущностей из БД")
        if bad:
            print("TEXTS_CATALOG.md устарел:")
            for item in bad:
                print(f"  • {item}")
            print("Перегенерируйте: .venv\\Scripts\\python.exe tools\\export_texts.py "
                  "--db <снимок прод-БД>")
            return 1
        note = "code, seeds" + (", db" if db_checked else " (db не проверялся: нет БД)")
        print(f"TEXTS_CATALOG.md актуален ({note})")
        return 0

    # Генерация
    if args.raw_db:
        if not os.path.exists(db_path):
            sys.exit(f"Нет файла БД: {db_path}")
        with db_connection(db_path) as conn:
            db_sections, db_fp = render_db_sections(conn)
        note = "источник: снимок БД без сидов"
    elif args.from_seeds:
        base = db_path if os.path.exists(db_path) else None
        with seeded_db(base) as seeded:
            with db_connection(seeded) as conn:
                db_sections, db_fp = render_db_sections(conn)
        note = ("источник: прод-БД + сиды" if base else
                "источник: только сиды кода (без прод-БД — черновик)")
    elif have_db:
        with seeded_db(db_path) as seeded:
            with db_connection(seeded) as conn:
                db_sections, db_fp = render_db_sections(conn)
        note = "источник: прод-БД + сиды"
    else:
        if not stored:
            sys.exit(f"Нет файла БД: {db_path}\n"
                     "Укажите --db <снимок прод-БД> или --from-seeds.")
        if stored[1] != seeds_fp:
            sys.exit(
                "Сиды изменились, а БД для актуализации нет.\n"
                "Нужен снимок прод-БД: tools/export_texts.py --db <снимок>\n"
                "Черновик только из сидов: --from-seeds (потеряет админ-контент).")
        db_sections, db_fp = parse_db_block(old)
        note_match = re.search(r"^_Снимок: .*? · (.*)_$", old, re.M)
        note = (note_match.group(1) if note_match
                else "источник: разделы сущностей из предыдущей версии каталога")

    content = build_catalog(db_sections, db_fp, code_fp, seeds_fp, note, entries)
    with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(content)
    print(f"written {os.path.basename(args.out)} ({len(content.encode('utf-8'))} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
