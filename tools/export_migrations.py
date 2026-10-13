"""Экспорт истории миграций БД в MIGRATIONS.md.

Разделы:
  1. Колоночные миграции `_ensure_column(conn, "table", "col", "type")` из
     `database/db.py`, сгруппированные по таблице (с номерами строк).
  2. Идемпотентные засевы/миграции данных (`ensure_*`, `seed_*`, `backfill`,
     `migrate_*`) — какие вызываются из `main.py` при старте.

Запуск:
    .venv\\Scripts\\python.exe tools/export_migrations.py [out.md]
"""
import ast
import os
import re
import sys
from collections import OrderedDict, defaultdict

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "database", "db.py")


def rel(p):
    return os.path.relpath(p, ROOT).replace("\\", "/")


src = open(DB, encoding="utf-8").read()
lines = src.splitlines()
tree = ast.parse(src, filename=DB)

cols = []   # (table, col, type, lineno)
seeders = []  # (name, lineno, first-doc-line)
for node in ast.walk(tree):
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
            and node.func.id == "_ensure_column" and len(node.args) >= 4:
        try:
            table = ast.literal_eval(node.args[1])
            col = ast.literal_eval(node.args[2])
            typ = ast.literal_eval(node.args[3])
            cols.append((table, col, typ, node.lineno))
        except Exception:
            pass
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and re.match(
            r"(ensure_|seed_|backfill|migrate_)", node.name):
        doc = (ast.get_docstring(node) or "").strip().splitlines()
        seeders.append((node.name, node.lineno, doc[0].strip() if doc else ""))

main_src = open(os.path.join(ROOT, "main.py"), encoding="utf-8").read()

by_table = defaultdict(list)
for table, col, typ, ln in cols:
    by_table[table].append((col, typ, ln))

out = []
out.append("# История миграций базы данных")
out.append("")
out.append("> **Сгенерировано** `tools/export_migrations.py`. Перегенерация:")
out.append("> `.venv\\Scripts\\python.exe tools/export_migrations.py`.")
out.append(">")
out.append("> Схема эволюционирует **аддитивно**: новые колонки добавляются в `init_db()`")
out.append("> через `_ensure_column(...)` (проверяет `PRAGMA table_info` и делает")
out.append("> `ALTER TABLE ADD COLUMN`, если колонки нет). Повторный запуск безопасен.")
out.append("> Засевы данных (`ensure_*`/`seed_*`) идемпотентны и вызываются из `main.py`")
out.append("> при каждом старте.")
out.append("")

out.append("## 1. Колоночные миграции `_ensure_column`")
out.append("")
out.append(f"Всего вызовов: **{len(cols)}**; таблиц: **{len(by_table)}**.")
out.append("")
out.append("| Таблица | Колонка | Тип / значение по умолчанию | db.py |")
out.append("|---|---|---|---|")
for table in sorted(by_table):
    for col, typ, ln in sorted(by_table[table]):
        out.append(f"| `{table}` | `{col}` | `{typ}` | :{ln} |")
out.append("")

out.append("## 2. Идемпотентные засевы и миграции данных")
out.append("")
out.append("| Функция | Вызывается из main.py | Назначение (первая строка docstring) | db.py |")
out.append("|---|---|---|---|")
for name, ln, doc in sorted(seeders):
    called = "✅" if re.search(rf"\b{re.escape(name)}\b", main_src) else "—"
    out.append(f"| `{name}` | {called} | {doc or '—'} | :{ln} |")
out.append("")

out.append("## 3. Отдельные скрипты миграций")
out.append("")
for fn in sorted(os.listdir(ROOT)):
    if re.match(r"migrate_.*\.py$", fn):
        try:
            _t = ast.parse(open(os.path.join(ROOT, fn), encoding="utf-8").read())
            _d = (ast.get_docstring(_t) or "").strip().splitlines()
            _d = _d[0].strip() if _d else ""
        except Exception:
            _d = ""
        out.append(f"- `{fn}` — {_d or 'разовый скрипт миграции (запускается вручную).'}")
out.append("")

_target = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "MIGRATIONS.md")
_text = "\n".join(out) + "\n"
if _target == "-":
    sys.stdout.write(_text)
else:
    with open(_target, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(_text)
    print(f"written {rel(_target)} ({len(_text)} bytes, {len(out)} lines)")
