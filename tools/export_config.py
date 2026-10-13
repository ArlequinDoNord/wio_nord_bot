"""Экспорт справочника констант config.py в CONFIG_REFERENCE.md.

Модульные присваивания группируются по СЕКЦИЯМ — комментариям-разделителям
вида `# ── Название ──`. Для каждой константы выводятся значение (компактно,
длинные значения усекаются) и inline-комментарий.

Запуск:
    .venv\\Scripts\\python.exe tools/export_config.py [out.md]
"""
import ast
import os
import re
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = os.path.join(ROOT, "config.py")


def rel(p):
    return os.path.relpath(p, ROOT).replace("\\", "/")


src = open(CONFIG, encoding="utf-8").read()
lines = src.splitlines()
tree = ast.parse(src, filename=CONFIG)

SEC_RE = re.compile(r"#\s*(?:──+\s*)?(.+?)\s*(?:──+)?\s*$")


def section_of(lineno):
    """Ближайший выше комментарий-разделитель."""
    for i in range(lineno - 2, -1, -1):
        s = lines[i].strip()
        if s.startswith("#") and ("──" in s or s.startswith("# ====")):
            m = SEC_RE.match(s)
            if m:
                return m.group(1).strip(" —-=")
        if not s.startswith("#") and s:
            break
    return "Без раздела"


def trailing_comment(lineno):
    line = lines[lineno - 1]
    # комментарий после кода (грубо, без учёта строк)
    idx = line.find("#")
    while idx != -1:
        if line[:idx].count('"') % 2 == 0 and line[:idx].count("'") % 2 == 0:
            return line[idx + 1:].strip()
        idx = line.find("#", idx + 1)
    return ""


def render(node):
    try:
        s = ast.unparse(node)
    except Exception:
        return "—"
    s = re.sub(r"\s+", " ", s)
    if len(s) > 200:
        s = s[:197] + "…"
    return s


sections = {}
order = []
for node in tree.body:
    if isinstance(node, ast.Assign):
        names = [t.id for t in node.targets if isinstance(t, ast.Name)]
        if not names:
            continue
        sec = section_of(node.lineno)
        if sec not in sections:
            sections[sec] = []
            order.append(sec)
        sections[sec].append((names[0], render(node.value), trailing_comment(node.lineno),
                              getattr(node.value, "lineno", node.lineno)))
    elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
        sec = section_of(node.lineno)
        if sec not in sections:
            sections[sec] = []
            order.append(sec)
        sections[sec].append((node.target.id, render(node.value) if node.value else "—",
                              trailing_comment(node.lineno), node.lineno))

out = []
out.append("# Справочник констант `config.py`")
out.append("")
out.append("> **Сгенерировано** `tools/export_config.py`. Перегенерация:")
out.append("> `.venv\\Scripts\\python.exe tools/export_config.py`.")
out.append(">")
out.append("> Все модульные константы `config.py`, сгруппированные по секциям")
out.append("> (комментариям-разделителям `# ── … ──`). Длинные значения усечены `…`;")
out.append("> точное значение — в `config.py` по строке из первой колонки.")
out.append("")
total = sum(len(v) for v in sections.values())
out.append(f"Всего констант: **{total}**; разделов: **{len(order)}**.")
out.append("")
for sec in order:
    out.append(f"## {sec}")
    out.append("")
    out.append("| Константа | Значение | Комментарий | config.py |")
    out.append("|---|---|---|---|")
    for name, val, cmt, ln in sections[sec]:
        val = val.replace("|", "\\|")
        cmt = (cmt or "").replace("|", "\\|")
        out.append(f"| `{name}` | `{val}` | {cmt} | :{ln} |")
    out.append("")

_target = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "CONFIG_REFERENCE.md")
_text = "\n".join(out) + "\n"
if _target == "-":
    sys.stdout.write(_text)
else:
    with open(_target, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(_text)
    print(f"written {rel(_target)} ({len(_text)} bytes, {len(out)} lines)")
