# -*- coding: utf-8 -*-
"""TEXTS_CATALOG.md — каталог всех текстов-описаний (предметы, локации, враги,
награды, рецепты, статусы, книги) из БД.

Зачем: владелец правит формулировки в одном файле, затем просит агента
«примени TEXTS_CATALOG.md» — правки переносятся в БД и в сиды, файл
перегенерируется.

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

ENEMY_SOURCES = (
    ("forest", "Лес и Белый Волк Севера", "forest_enemies"),
    ("dungeon", "Подземелье", "dungeon_enemies"),
    ("reservoir", "Водохранилище / моллюск", "fishing_enemies"),
)


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


def has_column(conn, table, column):
    return column in {r[1] for r in conn.execute(f"PRAGMA table_info({table})")}


def text(value):
    return "" if value is None else str(value)


def one_line(value):
    return " ".join(text(value).split())


def block(heading, meta, body, empty_note="—"):
    """Один элемент каталога. body — описание (может быть многострочным)."""
    body = text(body)
    lines = [f"### {heading}"]
    if meta:
        lines.append(f"- {meta}")
    if body.strip():
        body_lines = text(body).splitlines() or [""]
        lines.append(f"- описание: {body_lines[0].strip()}")
        for extra in body_lines[1:]:
            lines.append(f"  {extra.strip()}")
    else:
        lines.append(f"- описание: {empty_note}")
    return "\n".join(lines)


def render(conn):
    out = []
    add = out.append
    add("# TEXTS_CATALOG.md — каталог описаний N.O.R.D.")
    add("")
    add("> **Сгенерировано** `tools/export_texts.py` из боевой БД. Боевые тексты")
    add("> (лес, волк, моллюск, подземелье, К.В.П., шахта) — в `BATTLE_TEXTS.md`,")
    add("> интерфейс/кнопки — в `utils/i18n.py`.")
    add(">")
    add("> **Как править:** меняйте только текст после `- описание:` (и названия,")
    add("> если нужно). ID в заголовках (`ITEM-123`, `FOE-forest-2`) — служебные,")
    add("> не удаляйте и не меняйте. Метаданные (редкость, цены, HP, шансы) — только")
    add("> для справки: баланс правится отдельно, из этого файла они не переносятся.")
    add(">")
    add("> После правок скажите агенту «примени TEXTS_CATALOG.md»: изменения уйдут")
    add("> в БД и в сиды (`database/db.py`, `config.py`), файл перегенерируется.")
    add("> Генератор **перезаписывает** файл — не храните правки только здесь.")
    add("")
    add(f"_Снимок: {date.today().isoformat()}_")
    add("")

    nav = []
    sections = []

    # ── Предметы ──────────────────────────────────────────────────────────
    if has_table(conn, "items"):
        rows = conn.execute(
            "SELECT id, name, description, rarity, category, price, sell_price, "
            "is_available, loot_only, stock FROM items ORDER BY category, name").fetchall()
        by_cat = {}
        for r in rows:
            by_cat.setdefault(text(r["category"]) or "—", []).append(r)
        body = []
        body.append(f"Всего: **{len(rows)}**.")
        body.append("")
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
        sections.append(("предметы", f"Предметы ({len(rows)})", body))

    # ── Локации ───────────────────────────────────────────────────────────
    if has_table(conn, "locations"):
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
        sections.append(("локации", f"Локации ({len(rows)})", body))

    # ── Враги ─────────────────────────────────────────────────────────────
    foe_total = 0
    body = []
    for source, title, table in ENEMY_SOURCES:
        if not has_table(conn, table):
            continue
        rows = conn.execute(
            f"SELECT * FROM {table} ORDER BY id").fetchall()
        if not rows:
            continue
        foe_total += len(rows)
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
    if foe_total:
        sections.append(("враги", f"Враги ({foe_total})", body))

    # ── Награды ───────────────────────────────────────────────────────────
    if has_table(conn, "awards"):
        rows = conn.execute("SELECT id, name, description, emoji FROM awards ORDER BY id").fetchall()
        body = [f"Всего: **{len(rows)}**.", ""]
        for r in rows:
            meta = f"эмодзи: {text(r['emoji']) or '—'}"
            body.append(block(f"AWARD-{r['id']} · {r['name']}", meta, r["description"]))
            body.append("")
        sections.append(("награды", f"Награды ({len(rows)})", body))

    # ── Рецепты ───────────────────────────────────────────────────────────
    if has_table(conn, "recipes"):
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
        sections.append(("рецепты", f"Рецепты ({len(rows)})", body))

    # ── Статусы ───────────────────────────────────────────────────────────
    if has_table(conn, "statuses"):
        rows = conn.execute(
            "SELECT id, name, description, access_tag, sort_order FROM statuses "
            "ORDER BY sort_order, id").fetchall()
        body = [f"Всего: **{len(rows)}**.", ""]
        for r in rows:
            meta = f"тег доступа: {text(r['access_tag']) or '—'} · порядок: {r['sort_order']}"
            body.append(block(f"STATUS-{r['id']} · {r['name']}", meta, r["description"]))
            body.append("")
        sections.append(("статусы", f"Статусы ({len(rows)})", body))

    # ── Книги ─────────────────────────────────────────────────────────────
    if has_table(conn, "library_books"):
        rows = conn.execute(
            "SELECT id, section, title, author, description FROM library_books "
            "ORDER BY section, title").fetchall()
        if rows:
            body = [f"Всего: **{len(rows)}**.", ""]
            for r in rows:
                meta = f"раздел: {r['section']} · автор: {text(r['author']) or '—'}"
                body.append(block(f"BOOK-{r['id']} · {r['title']}", meta, r["description"]))
                body.append("")
            sections.append(("книги", f"Книги ({len(rows)})", body))

    for anchor, title, body in sections:
        nav.append(f"- [{title}](#{anchor})")
    add("## Содержание")
    add("")
    for line in nav:
        add(line)
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
