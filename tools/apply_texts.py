"""TEXTS_EDIT.md <-> utils/texts_overrides.json: правки текстов интерфейса владельцем.

Два режима:
  python tools/apply_texts.py --export   # перезаписать TEXTS_EDIT.md из текущих текстов
  python tools/apply_texts.py            # применить блоки «✏️ НОВЫЙ» в texts_overrides.json

Правила:
- Источник базы — utils/localization.py (STRINGS). Файл texts_overrides.json читается
  при импорте и накладывается поверх STRINGS, поэтому правки видны без изменения кода.
- В TEXTS_EDIT.md у каждого ключа два блока: «ТЕКУЩИЙ» (только для чтения) и «✏️ НОВЫЙ»
  (пусто — без изменений). Значения пишутся как JSON-строки в обратных кавычках,
  переносы — через \\n.
- При --export уже введённые, но не применённые «✏️ НОВЫЙ» сохраняются.
- Перед записью проверяется: ключ существует, обе локали заполнены, набор подстановок
  {name} совпадает с текущим текстом. Ошибка — ничего не пишется.
"""

import argparse
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

EDIT_PATH = os.path.join(ROOT, "TEXTS_EDIT.md")
OVERRIDES_PATH = os.path.join(ROOT, "utils", "texts_overrides.json")

LANGS = (("ru", "RU"), ("en", "EN"))
HEADER = """# TEXTS_EDIT.md — правки текстов интерфейса N.O.R.D.

> Как править: в блоке ключа впишите текст после «✏️ НОВЫЙ RU» / «✏️ НОВЫЙ EN» в виде
> JSON-строки в обратных кавычках, например `"Привет\\nМир"`. Пустое поле — без изменений.
> Потом: `python tools/apply_texts.py` (проверка и запись в `utils/texts_overrides.json`).
> «ТЕКУЩИЙ» — только для чтения: это значение после применения всех правок.
> Подстановки `{name}` менять нельзя — набор должен совпадать с текущим текстом.
> Сущности из БД (предметы, враги, локации) сюда не входят: они правятся в админ-боте.
"""

BLOCK_RE = re.compile(r"^### (?P<key>\S+)\s*$", re.M)
FIELD_RE = re.compile(r"^- (?P<label>ТЕКУЩИЙ|✏️ НОВЫЙ) (?P<lang>RU|EN):(?P<body>.*)$", re.M)
PLACEHOLDER_RE = re.compile(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}")


def _load_strings():
    from utils import localization
    return localization.STRINGS


def _base_strings():
    """STRINGS с наложенным texts_overrides.json: ТЕКУЩИЙ = то, что видит игрок."""
    import copy
    from utils import localization
    strings = copy.deepcopy(localization.STRINGS)
    if os.path.isfile(OVERRIDES_PATH):
        with open(OVERRIDES_PATH, encoding="utf-8") as f:
            for key, langs in json.load(f).items():
                if key in strings:
                    strings[key].update(langs)
    return strings


def _encode(value: str) -> str:
    return "`" + json.dumps(value, ensure_ascii=False) + "`"


def _decode(raw: str):
    text = raw.strip()
    if not text:
        return None
    if text.startswith("`") and text.endswith("`") and len(text) >= 2:
        text = text[1:-1]
    return json.loads(text)


def _read_pending_edits() -> dict:
    """Введённые, но не применённые «✏️ НОВЫЙ» из текущего TEXTS_EDIT.md."""
    if not os.path.isfile(EDIT_PATH):
        return {}
    with open(EDIT_PATH, encoding="utf-8") as f:
        text = f.read()
    pending = {}
    blocks = list(BLOCK_RE.finditer(text))
    for i, m in enumerate(blocks):
        key = m.group("key")
        end = blocks[i + 1].start() if i + 1 < len(blocks) else len(text)
        for fm in FIELD_RE.finditer(text[m.end():end]):
            if fm.group("label") == "✏️ НОВЫЙ" and fm.group("body").strip():
                pending.setdefault(key, {})[fm.group("lang").lower()] = fm.group("body")
    return pending


def export_edit_file(keep_pending: bool = True) -> int:
    strings = _base_strings()
    pending = _read_pending_edits() if keep_pending else {}
    out = [HEADER]
    for key in sorted(strings):
        entry = strings[key]
        out.append(f"\n### {key}\n")
        for lang, label in LANGS:
            cur = entry.get(lang) or entry.get("ru") or ""
            out.append(f"- ТЕКУЩИЙ {label}: {_encode(cur)}")
            new_raw = pending.get(key, {}).get(lang, "")
            out.append(f"- ✏️ НОВЫЙ {label}:{(' ' + new_raw.strip()) if new_raw else ''}")
        out.append("")
    with open(EDIT_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out))
    print(f"TEXTS_EDIT.md: {len(strings)} ключей, введённые правки сохранены: {sum(len(v) for v in pending.values())}")
    return 0


def _collect_new() -> dict:
    """{key: {lang: value}} из блоков «✏️ НОВЫЙ»; ошибки разбора — исключение."""
    with open(EDIT_PATH, encoding="utf-8") as f:
        text = f.read()
    strings = _load_strings()
    result = {}
    blocks = list(BLOCK_RE.finditer(text))
    for i, m in enumerate(blocks):
        key = m.group("key")
        end = blocks[i + 1].start() if i + 1 < len(blocks) else len(text)
        for fm in FIELD_RE.finditer(text[m.end():end]):
            if fm.group("label") != "✏️ НОВЫЙ":
                continue
            raw = fm.group("body")
            value = None
            try:
                value = _decode(raw)
            except json.JSONDecodeError as e:
                raise SystemExit(f"{key} {fm.group('lang')}: не разобрана строка ({e})")
            if value is None:
                continue
            lang = fm.group("lang").lower()
            if key not in strings:
                raise SystemExit(f"{key}: ключа нет в utils/localization.py")
            old = strings[key].get(lang) or strings[key].get("ru") or ""
            if set(PLACEHOLDER_RE.findall(old)) != set(PLACEHOLDER_RE.findall(value)):
                raise SystemExit(
                    f"{key} {lang.upper()}: подстановки {{...}} не совпадают с текущим текстом")
            result.setdefault(key, {})[lang] = value
    return result


def apply_edits() -> int:
    if not os.path.isfile(EDIT_PATH):
        print("TEXTS_EDIT.md не найден — сначала --export")
        return 1
    new = _collect_new()
    if not new:
        print("Новых правок нет.")
        return 0
    current = {}
    if os.path.isfile(OVERRIDES_PATH):
        with open(OVERRIDES_PATH, encoding="utf-8") as f:
            current = json.load(f)
    for key, langs in new.items():
        current.setdefault(key, {}).update(langs)
    with open(OVERRIDES_PATH, "w", encoding="utf-8", newline="\n") as f:
        json.dump(current, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")
    print(f"Применено: {sum(len(v) for v in new.values())} строк в {len(new)} ключах.")
    export_edit_file(keep_pending=False)
    print("Дальше: компиляция, смоуки, коммит.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Правки текстов через TEXTS_EDIT.md")
    parser.add_argument("--export", action="store_true", help="перезаписать TEXTS_EDIT.md")
    args = parser.parse_args()
    return export_edit_file() if args.export else apply_edits()


if __name__ == "__main__":
    sys.exit(main())
