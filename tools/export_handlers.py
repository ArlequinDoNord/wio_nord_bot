"""Экспорт карты модулей-хендлеров и роутеров в HANDLERS.md.

Сканирует `bot/handlers/*.py` и `main.py`:
  * назначение модуля (первая строка docstring);
  * объявленные роутеры (`x = Router()`);
  * число хендлеров message/callback_query;
  * занятые ими неймспейсы `F.data` (==/startswith);
  * FSM-классы `StatesGroup`, объявленные в модуле;
  * порядок подключения роутеров в `main.py` (важен: раньше = выше приоритет).

Запуск:
    .venv\\Scripts\\python.exe tools/export_handlers.py [out.md]
По умолчанию пишет HANDLERS.md рядом с репозиторием.
"""
import ast
import os
import re
import sys
from collections import OrderedDict

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HANDLERS = os.path.join(ROOT, "bot", "handlers")


def rel(p):
    return os.path.relpath(p, ROOT).replace("\\", "/")


def first_doc(tree):
    d = ast.get_docstring(tree)
    if not d:
        return "—"
    return d.strip().splitlines()[0].strip()


def is_router_call(node):
    return (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            and node.func.id == "Router")


def decorator_router_name(dec):
    if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute) \
            and isinstance(dec.func.value, ast.Name) and dec.func.attr in ("message", "callback_query"):
        return dec.func.value.id, dec.func.attr
    return None, None


def data_tokens(dec, src):
    """callback_data-подобные литералы из фильтров F.data этого декоратора."""
    eq, pref = [], []
    for n in ast.walk(dec):
        if isinstance(n, ast.Compare) and isinstance(n.left, ast.Attribute) \
                and n.left.attr == "data":
            for op, comp in zip(n.ops, n.comparators):
                if isinstance(op, ast.Eq) and isinstance(comp, ast.Constant) \
                        and isinstance(comp.value, str):
                    eq.append(comp.value)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) \
                and n.func.attr == "startswith" and n.args \
                and isinstance(n.args[0], ast.Constant) and isinstance(n.args[0].value, str):
            pref.append(n.args[0].value)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) \
                and n.func.attr == "regexp" and n.args \
                and isinstance(n.args[0], ast.Constant) and isinstance(n.args[0].value, str):
            pref.append(n.args[0].value.lstrip("^"))
    return eq, pref


# ── Порядок роутеров из main.py ──
order = []                 # [(alias, module)]
alias_to_module = {}
main_src = open(os.path.join(ROOT, "main.py"), encoding="utf-8").read()
for m in re.finditer(r"from bot\.handlers\.(\w+) import router as (\w+)", main_src):
    alias_to_module[m.group(2)] = m.group(1)
for m in re.finditer(r"dp\.include_router\((\w+)\)", main_src):
    order.append((m.group(1), alias_to_module.get(m.group(1), "?")))
order_index = {mod: i for i, (_, mod) in enumerate(order)}

# ── Разбор модулей ──
info = OrderedDict()
for fn in sorted(os.listdir(HANDLERS)):
    if not fn.endswith(".py") or fn == "__init__.py":
        continue
    path = os.path.join(HANDLERS, fn)
    src = open(path, encoding="utf-8").read()
    tree = ast.parse(src, filename=path)
    mod = fn[:-3]

    routers = []
    for node in tree.body:
        if isinstance(node, ast.Assign) and is_router_call(node.value):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    routers.append(t.id)

    msgs = cbs = 0
    eq_set, pref_set = set(), set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for dec in node.decorator_list:
                rname, kind = decorator_router_name(dec)
                if kind == "message":
                    msgs += 1
                elif kind == "callback_query":
                    cbs += 1
                if rname is not None:
                    e, p = data_tokens(dec, src)
                    eq_set.update(e)
                    pref_set.update(p)

    states = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and any(
                (isinstance(b, ast.Name) and b.id == "StatesGroup")
                or (isinstance(b, ast.Attribute) and b.attr == "StatesGroup")
                for b in node.bases):
            states.append(node.name)

    namespaces = sorted({t.split(":", 1)[0] for t in (eq_set | pref_set)})

    info[mod] = dict(doc=first_doc(tree), routers=routers, msgs=msgs, cbs=cbs,
                     namespaces=namespaces, states=states,
                     exact=sorted(eq_set), prefix=sorted(pref_set))

# ── Вывод ──
out = []
out.append("# Карта модулей-хендлеров и роутеров")
out.append("")
out.append("> **Сгенерировано** `tools/export_handlers.py`. Перегенерация:")
out.append("> `.venv\\Scripts\\python.exe tools/export_handlers.py`.")
out.append(">")
out.append("> Порядок в таблице = порядок `dp.include_router(...)` в `main.py`.")
out.append("> **Чем раньше роутер подключён, тем выше приоритет его хендлеров** при")
out.append("> совпадении фильтров — это главный источник «мёртвых» хендлеров.")
out.append("")

out.append("## Порядок роутеров (main.py)")
out.append("")
out.append("| # | Роутер (alias) | Модуль |")
out.append("|---:|---|---|")
for i, (alias, mod) in enumerate(order):
    out.append(f"| {i + 1} | `{alias}` | `bot/handlers/{mod}.py` |")
out.append("")

out.append("## Сводка по модулям")
out.append("")
out.append("| Модуль | Назначение | Роутеры | msg | cb | Неймспейсы `F.data` | FSM-классы |")
out.append("|---|---|---:|---:|---:|---|---|")
def sort_key(mod):
    return (order_index.get(mod, 999), mod)
for mod in sorted(info, key=sort_key):
    d = info[mod]
    out.append("| `{m}.py` | {doc} | {r} | {msg} | {cb} | {ns} | {st} |".format(
        m=mod, doc=d["doc"],
        r=", ".join(f"`{x}`" for x in d["routers"]) or "—",
        msg=d["msgs"], cb=d["cbs"],
        ns=", ".join(f"`{n}:`" for n in d["namespaces"]) or "—",
        st=", ".join(f"`{s}`" for s in d["states"]) or "—",
    ))
out.append("")

out.append("## Детально по модулям (точные и префиксные ключи `F.data`)")
out.append("")
for mod in sorted(info, key=sort_key):
    d = info[mod]
    out.append(f"### `{mod}.py` — {d['doc']}")
    out.append("")
    out.append(f"- Роутеры: " + (", ".join(f"`{x}`" for x in d["routers"]) or "—"))
    out.append(f"- Хендлеры: message={d['msgs']}, callback_query={d['cbs']}")
    if d["states"]:
        out.append("- FSM: " + ", ".join(f"`{s}`" for s in d["states"]))
    if d["prefix"]:
        out.append("- `F.data.startswith`: " + ", ".join(f"`{p}`" for p in d["prefix"]))
    if d["exact"]:
        out.append("- `F.data ==`: " + ", ".join(f"`{e}`" for e in d["exact"]))
    out.append("")

_target = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "HANDLERS.md")
_text = "\n".join(out) + "\n"
if _target == "-":
    sys.stdout.write(_text)
else:
    with open(_target, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(_text)
    print(f"written {rel(_target)} ({len(_text)} bytes, {len(out)} lines)")
