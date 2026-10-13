"""Экспорт индекса smoke-тестов в SMOKE_INDEX.md.

Для каждого `smoke_NNN.py` берёт первую строку docstring (что проверяет),
версию из docstring (если указана) и число вызовов `check(...)`.

Запуск:
    .venv\\Scripts\\python.exe tools/export_smokes.py [out.md]
"""
import ast
import os
import re
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def rel(p):
    return os.path.relpath(p, ROOT).replace("\\", "/")


def num(fn):
    m = re.search(r"smoke_(\d+)\.py$", fn)
    return int(m.group(1)) if m else 0


rows = []
for fn in sorted(os.listdir(ROOT)):
    if not re.match(r"smoke_\d+\.py$", fn):
        continue
    path = os.path.join(ROOT, fn)
    src = open(path, encoding="utf-8").read()
    try:
        tree = ast.parse(src, filename=path)
        doc = (ast.get_docstring(tree) or "").strip()
    except SyntaxError as e:
        doc = f"[syntax error: {e}]"
    first = next((ln.strip() for ln in doc.splitlines()
                  if ln.strip() and not ln.strip().lower().startswith("запуск")), "—")
    ver_m = re.search(r"v(\d+\.\d+\.\d+)", first)
    ver = ver_m.group(1) if ver_m else ""
    checks = len(re.findall(r"\bcheck\s*\(", src))
    rows.append((num(fn), fn, ver, first, checks))

out = []
out.append("# Индекс smoke-тестов")
out.append("")
out.append("> **Сгенерировано** `tools/export_smokes.py`. Перегенерация:")
out.append("> `.venv\\Scripts\\python.exe tools/export_smokes.py`.")
out.append(">")
out.append("> Запуск всех: `tools/run_smokes.py`. Каждый тест автономен (свой временный")
out.append("> `_test_smokeNNN.db`). Колонка «Проверок» — число вызовов `check(...)`.")
out.append("")
out.append(f"Всего тестов: **{len(rows)}**.")
out.append("")
out.append("| # | Файл | Версия | Что проверяет (первая строка docstring) | Проверок |")
out.append("|---:|---|---|---|---:|")
for n, fn, ver, first, checks in rows:
    out.append(f"| {n} | `{fn}` | {ver or '—'} | {first} | {checks} |")
out.append("")

_target = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "SMOKE_INDEX.md")
_text = "\n".join(out) + "\n"
if _target == "-":
    sys.stdout.write(_text)
else:
    with open(_target, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(_text)
    print(f"written {rel(_target)} ({len(_text)} bytes, {len(out)} lines)")
