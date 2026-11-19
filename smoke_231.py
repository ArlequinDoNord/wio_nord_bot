# -*- coding: utf-8 -*-
"""Smoke 231 — правки текстов через TEXTS_EDIT.md (tools/apply_texts.py).

Проверяет на временных файлах (боевые тексты не трогаются):
- экспорт создаёт блоки ключей с ТЕКУЩИЙ и пустым «✏️ НОВЫЙ»;
- введённая правка применяется в texts_overrides.json;
- после применения блок «✏️ НОВЫЙ» очищается;
- подстановки {..} должны совпадать с текущим текстом, иначе ошибка и ничего не пишется;
- ключ уведомления о подземелье есть на ru и en (для английского оповещения).

Прогон: .\\.venv\\Scripts\\python.exe smoke_231.py
"""
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))

passed = failed = 0
KEY = "dungeon.notify.boss_won"


def check(name, cond):
    global passed, failed
    if cond:
        passed += 1
        print(f"  OK  {name}")
    else:
        failed += 1
        print(f"  FAIL: {name}")


def set_new_value(text: str, key: str, lang_label: str, value: str) -> str:
    """Вписывает значение в «✏️ НОВЫЙ <LANG>» блока ключа."""
    start = text.index(f"### {key}\n")
    marker = f"- ✏️ НОВЫЙ {lang_label}:"
    pos = text.index(marker, start)
    line_end = text.index("\n", pos)
    return text[:pos] + f"{marker} `{json.dumps(value, ensure_ascii=False)}`" + text[line_end:]


def read_new_value(text: str, key: str, lang_label: str) -> str:
    start = text.index(f"### {key}\n")
    marker = f"- ✏️ НОВЫЙ {lang_label}:"
    pos = text.index(marker, start)
    line_end = text.index("\n", pos)
    return text[pos + len(marker):line_end].strip()


def main():
    import apply_texts as A
    from utils import localization

    tmp = tempfile.mkdtemp(prefix="texts_edit_")
    A.EDIT_PATH = os.path.join(tmp, "TEXTS_EDIT.md")
    A.OVERRIDES_PATH = os.path.join(tmp, "texts_overrides.json")

    print("\n1. Экспорт")
    A.export_edit_file()
    with open(A.EDIT_PATH, encoding="utf-8") as f:
        text = f.read()
    check("файл создан и содержит ключ уведомления", f"### {KEY}\n" in text)
    check("пустые «НОВЫЙ» по умолчанию", read_new_value(text, KEY, "EN") == "")

    print("\n2. Правка и применение")
    text = set_new_value(text, KEY, "EN", "Boss «{boss}» is down, thanks to {who}!")
    with open(A.EDIT_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    A.apply_edits()
    with open(A.OVERRIDES_PATH, encoding="utf-8") as f:
        overrides = json.load(f)
    check("правка записана в overrides",
          overrides.get(KEY, {}).get("en") == "Boss «{boss}» is down, thanks to {who}!")
    with open(A.EDIT_PATH, encoding="utf-8") as f:
        after = f.read()
    check("после применения блок «НОВЫЙ» очищен", read_new_value(after, KEY, "EN") == "")

    print("\n3. Несовпадение подстановок — отказ")
    bad = set_new_value(after, KEY, "RU", "🏆 {who} прошёл подземелье!")
    with open(A.EDIT_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write(bad)
    raised = False
    try:
        A.apply_edits()
    except SystemExit:
        raised = True
    check("ошибка при пропавшей подстановке {boss}", raised)
    with open(A.OVERRIDES_PATH, encoding="utf-8") as f:
        still = json.load(f)
    check("при ошибке ничего не записано", "ru" not in still.get(KEY, {}))

    print("\n4. Ключ уведомления на обоих языках")
    entry = localization.STRINGS.get(KEY, {})
    check("есть ru", bool(entry.get("ru")))
    check("есть en", bool(entry.get("en")))

    return failed > 0


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
