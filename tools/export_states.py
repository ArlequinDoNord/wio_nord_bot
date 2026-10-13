"""Экспорт карты FSM-состояний и callback-неймспейсов бота в Markdown.

Сканирует `bot/` через `ast`:
  * классы `StatesGroup` и их `State()`-поля (в порядке объявления);
  * где состояние ставится (`state.set_state(Cls.field)`) и где по нему
    фильтруются хендлеры (`@router.message(Cls.field)`, `StateFilter(...)`);
  * реестр `callback_data`: фабрики кнопок и фильтры `F.data ==` /
    `F.data.startswith` — чтобы ловить конфликты меню.

Запуск:
    .venv\\Scripts\\python.exe tools/export_states.py > FSM_STATES.md

Скрипт ничего не меняет в БД и не требует токен; вывод — Markdown в stdout.
"""
import ast
import os
import sys
from collections import OrderedDict, defaultdict

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOT = os.path.join(ROOT, "bot")


def iter_py(root):
    for dp, _, fns in os.walk(root):
        if "__pycache__" in dp:
            continue
        for fn in sorted(fns):
            if fn.endswith(".py"):
                yield os.path.join(dp, fn)


def rel(path):
    return os.path.relpath(path, ROOT).replace("\\", "/")


def source_lines(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read().splitlines()


def is_states_group(base):
    if isinstance(base, ast.Name):
        return base.id == "StatesGroup"
    if isinstance(base, ast.Attribute):
        return base.attr == "StatesGroup"
    return False


def attr_refs(node, known):
    """Множество (класс, поле) для узлов вида `Cls.field`, где Cls в known."""
    out = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id in known:
            out.add((n.value.id, n.attr))
    return out


# ── Проход 1: классы состояний ──
classes = OrderedDict()          # (module, class) -> [state, ...]
for path in iter_py(BOT):
    try:
        tree = ast.parse(open(path, encoding="utf-8").read(), filename=path)
    except SyntaxError as e:
        print(f"<!-- syntax error {rel(path)}: {e} -->")
        continue
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and any(is_states_group(b) for b in node.bases):
            states = []
            for stmt in node.body:
                if (isinstance(stmt, ast.Assign) and isinstance(stmt.value, ast.Call)
                        and getattr(stmt.value.func, "id", None) == "State"):
                    for t in stmt.targets:
                        if isinstance(t, ast.Name):
                            states.append(t.id)
            classes[(rel(path), node.name)] = states

known_classes = {cls for (_, cls) in classes}


class UsageVisitor(ast.NodeVisitor):
    def __init__(self, module, lines):
        self.module = module
        self.lines = lines
        self.stack = []
        self.sets = defaultdict(list)      # (cls, field) -> [ref]
        self.handles = defaultdict(list)   # (cls, field) -> [ref]

    def _here(self, lineno):
        return f"`{self.module}:{lineno}`"

    def visit_FunctionDef(self, node):
        self._fn(node)

    def visit_AsyncFunctionDef(self, node):
        self._fn(node)

    def _fn(self, node):
        for dec in node.decorator_list:
            for ref in attr_refs(dec, known_classes):
                self.handles[ref].append(f"`{self.module}:{node.lineno}` `{node.name}`")
        self.stack.append(node.name)
        self.generic_visit(node)
        self.stack.pop()

    def visit_Call(self, node):
        f = node.func
        if (isinstance(f, ast.Attribute) and f.attr == "set_state"
                and node.args and isinstance(node.args[0], ast.Attribute)):
            a = node.args[0]
            if isinstance(a.value, ast.Name) and a.value.id in known_classes:
                fn = self.stack[-1] if self.stack else "?"
                self.sets[(a.value.id, a.attr)].append(f"`{self.module}:{node.lineno}` `{fn}`")
        self.generic_visit(node)


class CbVisitor(ast.NodeVisitor):
    """Собирает callback_data-фабрики и фильтры F.data."""

    def __init__(self, module, lines):
        self.module = module
        self.lines = lines
        self.created = defaultdict(list)   # callback string -> [ref]
        self.eq_filters = defaultdict(list)
        self.prefix_filters = defaultdict(list)

    def _here(self, lineno):
        return f"`{self.module}:{lineno}`"

    def visit_Call(self, node):
        for kw in node.keywords:
            if kw.arg == "callback_data" and isinstance(kw.value, ast.Constant) \
                    and isinstance(kw.value.value, str):
                self.created[kw.value.value].append(self._here(node.lineno))
        # F.data.startswith("...")
        f = node.func
        if isinstance(f, ast.Attribute) and f.attr == "startswith" and node.args \
                and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
            self.prefix_filters[node.args[0].value].append(self._here(node.lineno))
        self.generic_visit(node)

    def visit_Compare(self, node):
        left = node.left
        if isinstance(left, ast.Attribute) and left.attr == "data":
            for op, comp in zip(node.ops, node.comparators):
                if isinstance(op, ast.Eq) and isinstance(comp, ast.Constant) \
                        and isinstance(comp.value, str):
                    self.eq_filters[comp.value].append(self._here(node.lineno))
        self.generic_visit(node)


all_sets = defaultdict(list)
all_handles = defaultdict(list)
cb_created = defaultdict(list)
cb_eq = defaultdict(list)
cb_prefix = defaultdict(list)

for path in iter_py(BOT):
    try:
        tree = ast.parse(open(path, encoding="utf-8").read(), filename=path)
    except SyntaxError:
        continue
    lines = source_lines(path)
    uv = UsageVisitor(rel(path), lines)
    uv.visit(tree)
    for k, v in uv.sets.items():
        all_sets[k].extend(v)
    for k, v in uv.handles.items():
        all_handles[k].extend(v)

    cv = CbVisitor(rel(path), lines)
    cv.visit(tree)
    for k, v in cv.created.items():
        cb_created[k].extend(v)
    for k, v in cv.eq_filters.items():
        cb_eq[k].extend(v)
    for k, v in cv.prefix_filters.items():
        cb_prefix[k].extend(v)

# ── Вывод ──
out = []
out.append("# Карта FSM-состояний и callback-неймспейсов N.O.R.D.")
out.append("")
out.append("> **Сгенерировано** `tools/export_states.py`. Не редактировать вручную —")
out.append("> правь код и перегенерируй: `.venv\\Scripts\\python.exe tools/export_states.py`.")
out.append(">")
out.append("> Назначение: единый обзор всех `StatesGroup`, где они ставятся и где ловятся,")
out.append("> а также реестр `callback_data` — чтобы не допускать конфликтов меню/хендлеров.")
out.append("")
out.append(f"Всего классов состояний: **{len(classes)}**; "
           f"полей-состояний: **{sum(len(v) for v in classes.values())}**; "
           f"уникальных `callback_data`: **{len(cb_created)}**.")
out.append("")

out.append("## 1. Классы состояний по модулям")
out.append("")
for (module, cls), states in classes.items():
    out.append(f"### `{cls}` — `{module}`")
    out.append("")
    out.append("| Состояние | Ставится (`set_state`) | Ловится (хендлер) |")
    out.append("|---|---|---|")
    for st in states:
        sets = all_sets.get((cls, st), [])
        handles = all_handles.get((cls, st), [])
        s = "<br>".join(sets) if sets else "—"
        h = "<br>".join(handles) if handles else "—"
        out.append(f"| `{st}` | {s} | {h} |")
    out.append("")

unset = sorted(k for k in all_sets if k not in {(c, s) for (_, c), ss in classes.items() for s in ss})
unhandled = sorted(k for k in all_handles
                   if k not in {(c, s) for (_, c), ss in classes.items() for s in ss})
if unset or unhandled:
    out.append("### ⚠️ Ссылки на состояния, которых нет в классах (опечатки/удалённое)")
    out.append("")
    for k in unset:
        out.append(f"- set_state `{k[0]}.{k[1]}`: " + "; ".join(all_sets[k]))
    for k in unhandled:
        out.append(f"- handler `{k[0]}.{k[1]}`: " + "; ".join(all_handles[k]))
    out.append("")

out.append("## 2. Реестр callback_data по неймспейсам")
out.append("")
out.append("Все ключи, встречающиеся в фабриках кнопок (`callback_data=`), сгруппированы")
out.append("по неймспейсу (текст до первого `:`). Это «занятые» префиксы: новый ключ")
out.append("с таким же префиксом должен учитывать уже существующие фильтры (раздел 3).")
out.append("")
by_ns = defaultdict(set)
for cb in cb_created:
    by_ns[cb.split(":", 1)[0]].add(cb)
out.append("| Неймспейс | Ключей | callback_data |")
out.append("|---|---:|---|")
for ns in sorted(by_ns):
    keys = sorted(by_ns[ns])
    out.append(f"| `{ns}:` | {len(keys)} | " + ", ".join(f"`{k}`" for k in keys) + " |")
out.append("")

out.append("## 3. Фильтры хендлеров `F.data`")
out.append("")
out.append("### Точное совпадение (`F.data == \"...\"`)")
out.append("")
for cb in sorted(cb_eq):
    out.append(f"- `{cb}`: " + "; ".join(cb_eq[cb]))
out.append("")
out.append("### По префиксу (`F.data.startswith(\"...\")`)")
out.append("")
for p in sorted(cb_prefix):
    out.append(f"- `{p}`: " + "; ".join(cb_prefix[p]))
out.append("")

# ── Конфликты: один callback обрабатывается более чем одним точным фильтром ──
dup = {cb: refs for cb, refs in cb_eq.items() if len(refs) > 1}
out.append("## 4. ⚠️ Возможные конфликты")
out.append("")
if dup:
    out.append("**Один `callback_data` ловится несколькими `F.data ==`-хендлерами**")
    out.append("(побеждает зарегистрированный раньше — второй код мёртв):")
    out.append("")
    for cb in sorted(dup):
        out.append(f"- `{cb}`:")
        for r in dup[cb]:
            out.append(f"    - {r}")
else:
    out.append("- Дублей точных `F.data ==` фильтров не найдено.")
out.append("")

# Префиксные фильтры, пересекающиеся с точными (префикс поймает и точный ключ)
overlaps = []
for p, prefs in cb_prefix.items():
    for cb in cb_created:
        if cb.startswith(p) and cb_eq.get(cb):
            overlaps.append((p, cb, prefs, cb_eq[cb]))
if overlaps:
    out.append("**Префиксный фильтр перекрывает точный ключ** (проверь порядок регистрации):")
    out.append("")
    for p, cb, prefs, eq in overlaps:
        out.append(f"- `startswith(\"{p}\")` ⇄ `== \"{cb}\"`")
    out.append("")

_target = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "FSM_STATES.md")
_text = "\n".join(out) + "\n"
if _target == "-":
    sys.stdout.write(_text)
else:
    with open(_target, "w", encoding="utf-8", newline="\n") as _fh:
        _fh.write(_text)
    print(f"written {rel(_target)} ({len(_text)} bytes, {len(out)} lines)")