# -*- coding: utf-8 -*-
"""TEXTS_CATALOG.md — единый каталог ВСЕХ текстов, которые видит игрок.

Разделы (темы):
  1. Интерфейс и кнопки — из utils/i18n.py (STRINGS, ru/en)
  2. Боевые тексты — встроены из BATTLE_TEXTS.md
  3. Предметы, локации, враги, награды, рецепты, статусы, книги — из БД

Владелец правит тексты прямо в каталоге, затем просит агента
«примени TEXTS_CATALOG.md»: правки уходят в i18n.py / BATTLE_TEXTS.md / код
боевых хендлеров / БД и сиды, после чего файл перегенерируется.

Запуск:
    .venv\\Scripts\\python.exe tools\\export_texts.py
    .venv\\Scripts\\python.exe tools\\export_texts.py --db путь\\к\\nordmark.db
    .venv\\Scripts\\python.exe tools\\export_texts.py --check   # только проверка

База по умолчанию: переменная окружения DATABASE_PATH, иначе ./data/nordmark.db.
Для актуализации на боевых данных: скачать прод-БД и передать через --db.
"""
import argparse
import os
import sqlite3
import sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "TEXTS_CATALOG.md")
BATTLE = os.path.join(ROOT, "BATTLE_TEXTS.md")

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
)


# ────────────────────────────────────────────────────────────────────────────
# Общие помощники
# ────────────────────────────────────────────────────────────────────────────

def connect(path):
    if not os.path.exists(path):
        sys.exit(f"Нет файла БД: {path}\nУкажите --db или DATABASE_PATH.")
    conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


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


# ────────────────────────────────────────────────────────────────────────────
# Разделы
# ────────────────────────────────────────────────────────────────────────────

def render_ui():
    """Интерфейс и кнопки из utils/i18n.STRINGS (ru/en)."""
    if ROOT not in sys.path:
        sys.path.insert(0, ROOT)
    from utils.i18n import STRINGS  # noqa: WPS433 (осознанный импорт проекта)

    groups = {}
    for key in sorted(STRINGS):
        prefix = key.split(".", 1)[0]
        groups.setdefault(prefix, []).append(key)

    body = [
        f"Всего строк: **{len(STRINGS)}** (ru + en).",
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
            body.append(ui_block(key, STRINGS[key]))
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
            if "spot" in keys:
                meta_parts.append(f"spot: {r['spot']}")
            if "hp" in keys:
                meta_parts.append(f"HP: {r['hp']}")
            if "dmg_min" in keys and "dmg_max" in keys:
                meta_parts.append(f"урон: {r['dmg_min']}–{r['dmg_max']}")
            if "chance" in keys and r["chance"] is not None:
                meta_parts.append(f"шанс: {r['chance']}")
            if "enabled" in keys:
                meta_parts.append(f"включён: {'да' if r['enabled'] else 'нет'}")
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


# ────────────────────────────────────────────────────────────────────────────

def render(conn):
    sections = [
        ("интерфейс", "Интерфейс и кнопки", render_ui()),
        ("боевые-тексты", "Боевые тексты", render_battle()),
    ]
    for anchor, title, builder in (
            ("предметы", "Предметы", render_items),
            ("локации", "Локации", render_locations),
            ("враги", "Враги", render_enemies),
            ("награды", "Награды", render_awards),
            ("рецепты", "Рецепты", render_recipes),
            ("статусы", "Статусы", render_statuses),
            ("книги", "Книги", render_books)):
        content = builder(conn)
        if content:
            sections.append((anchor, title, content))

    out = []
    add = out.append
    add("# TEXTS_CATALOG.md — все тексты N.O.R.D. в одном файле")
    add("")
    add("> Единый каталог того, что видит игрок, разбитый по темам. Сгенерирован")
    add("> `tools/export_texts.py` из трёх источников: `utils/i18n.py` (интерфейс),")
    add("> `BATTLE_TEXTS.md` (боевые тексты) и боевая БД (описания сущностей).")
    add(">")
    add("> **Как править:** меняйте сам текст. Служебные ID (`UI-…`, `ITEM-123`,")
    add("> `LOC-…`, `FOE-…`) не переименовывайте — по ним правки переносятся обратно.")
    add("> `{...}` — живые подстановки: удалять/переименовывать нельзя.")
    add("> Метаданные (редкость, цены, HP, шансы) — только справка, баланс правится")
    add("> отдельно и из каталога не переносится.")
    add(">")
    add("> Когда закончите — скажите агенту «примени TEXTS_CATALOG.md»: правки уйдут")
    add("> в `utils/i18n.py`, `BATTLE_TEXTS.md` + боевые хендлеры, БД и сиды,")
    add("> после чего каталог будет перегенерирован. Генератор **перезаписывает**")
    add("> этот файл, поэтому не храните правки только здесь.")
    add("")
    add(f"_Снимок: {date.today().isoformat()}_")
    add("")
    add("## Содержание")
    add("")
    for anchor, title, body in sections:
        add(f"- [{title}](#{anchor})")
    add("")
    for anchor, title, body in sections:
        add(f'<a id="{anchor}"></a>')
        add("")
        add(f"## {title}")
        add("")
        for line in body:
            add(line)
        add("")
    return "\n".join(out).rstrip() + "\n"


def main():
    parser = argparse.ArgumentParser(description="Генератор TEXTS_CATALOG.md")
    parser.add_argument("--db", default=os.environ.get("DATABASE_PATH")
                        or os.path.join(ROOT, "data", "nordmark.db"))
    parser.add_argument("--out", default=OUT)
    parser.add_argument("--check", action="store_true",
                        help="не писать файл, только сравнить с текущим")
    args = parser.parse_args()

    conn = connect(args.db)
    try:
        content = render(conn)
    finally:
        conn.close()

    old = ""
    if os.path.exists(args.out):
        with open(args.out, encoding="utf-8") as fh:
            old = fh.read()

    if args.check:
        if old != content:
            print("TEXTS_CATALOG.md устарел — запустите tools/export_texts.py")
            return 1
        print("TEXTS_CATALOG.md актуален")
        return 0

    with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(content)
    print(f"written {os.path.basename(args.out)} ({len(content.encode('utf-8'))} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
