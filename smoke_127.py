"""Smoke: аудит маршрутизации inline-кнопок (callback_data).

Проверяет, что ни один callback не обрабатывается хендлерами из двух разных
модулей. В aiogram первый подошедший хендлер выигрывает, поэтому широкий
фильтр в одном роутере может «съесть» чужое пространство имён.

Найденный этим тестом баг (v0.22.5 -> v0.22.6):
  bot/handlers/admin.py: @router.callback_query(F.data.startswith("news:"))
  перехватывал ВСЕ новостные кнопки, т.к. admin_router подключён раньше
  news_router (main.py: include_router(admin_router) до include_router(news_router)).
  - `news:view:<id>` (открыть новость) -> вместо новости печаталось
    «✅ Оповещения будут идти в чат <id>» из админского обработчика;
  - `news:tab`, `news:write`, `news:archive`, ... -> IndexError в
    int(rest[0]), т.е. кнопка молча ничего не делала.

Как работает:
1. Корпус кандидатов — все литералы `callback_data=` во всех *.py репозитория
   (f-строки подставляются несколькими вариантами: цифры, буквы, id чата).
2. Хендлеры берутся из реальных `router.callback_query.handlers` всех модулей
   bot/handlers/*.py, фильтры исполняются настоящими объектами aiogram.
3. Для каждого кандидата считается, из скольких РАЗНЫХ модулей есть матчащий
   хендлер. >=2 -> это коллизия, тест падает.
4. Отдельно жёстко проверяется пространство имён `news:` (регрессия бага).

Ограничение (осознанное): кандидаты собираются только из литералов
`callback_data=`; кнопки, собираемые через переменные/хелперы, статически не
перечисляются (добавлены только известные шаблоны в EXTRA_TEMPLATES).
Нулевые совпадения (кнопка без хендлера) — не ошибка этого теста.

Запуск: .venv\\Scripts\\python.exe smoke_127.py
"""
import asyncio
import importlib
import inspect
import os
import pathlib
import re
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

_ROOT = pathlib.Path(__file__).resolve().parent
_TEST_DB = str(_ROOT / "_test_smoke127.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB

sys.path.insert(0, str(_ROOT))

# Кнопки, собираемые хелперами (статически не видны в callback_data=).
EXTRA_TEMPLATES = [
    "enemy:list:{src}:{loc}",
]

VARIANTS = ("1", "x", "-1001234567890", "d-1-2")

# Пространство имён news: (callback -> модуль-владелец).
NEWS_EXPECTED = {
    "news:tab": "news",
    "news:view:1": "news",
    "news:archive": "news",
    "news:arch:1": "news",
    "news:write": "news",
    "news:no_photo": "news",
    "news:edit:1": "news",
    "news:del:1": "news",
    "news:delconf:1": "news",
    "news:off": "admin",
    "news:chat:-1001234567890:0": "admin",
    "news:topic:-1001234567890:5": "admin",
    "news:allow:-1001234567890": "admin",
    "news:disallow:-1001234567890": "admin",
}

_CB_RE = re.compile(r'callback_data\s*=\s*f?"([^"]*)"')
_PLACEHOLDER_RE = re.compile(r"\{[^{}]*\}")


class _FakeEvent:
    __slots__ = ("data",)

    def __init__(self, data):
        self.data = data


def collect_candidates():
    out = set()
    for py in _ROOT.rglob("*.py"):
        parts = py.relative_to(_ROOT).parts
        if parts[0] in (".venv", ".git", "venv", "__pycache__") or py == pathlib.Path(__file__).resolve():
            continue
        text = py.read_text(encoding="utf-8", errors="replace")
        for raw in _CB_RE.findall(text):
            base = raw
            if not _PLACEHOLDER_RE.search(base):
                if base and len(base.encode()) <= 64:
                    out.add(base)
                continue
            fields = _PLACEHOLDER_RE.findall(base)
            skeleton = _PLACEHOLDER_RE.sub("\x00", base)
            for variant in VARIANTS:
                cand = skeleton
                for field in fields:
                    cand = cand.replace("\x00", variant, 1)
                if cand and len(cand.encode()) <= 64:
                    out.add(cand)
    for tmpl in EXTRA_TEMPLATES:
        skeleton = _PLACEHOLDER_RE.sub("\x00", tmpl)
        for variant in VARIANTS:
            cand = skeleton
            for _ in _PLACEHOLDER_RE.findall(tmpl):
                cand = cand.replace("\x00", variant, 1)
            if cand and len(cand.encode()) <= 64:
                out.add(cand)
    return sorted(out)


def load_modules():
    handlers_dir = _ROOT / "bot" / "handlers"
    names = sorted(p.stem for p in handlers_dir.glob("*.py") if p.stem != "__init__")
    routers = {}
    for name in names:
        mod = importlib.import_module(f"bot.handlers.{name}")
        routers[name] = getattr(mod, "router", None)
    return routers


def collect_handlers(routers):
    entries = []
    for module, router in routers.items():
        if router is None:
            continue
        for handler in router.callback_query.handlers:
            entries.append((module, handler))
    return entries


async def filter_matches(filter_obj, data):
    try:
        res = filter_obj.callback(_FakeEvent(data))
        if inspect.isawaitable(res):
            res = await res
        return bool(res)
    except Exception:
        return False


async def handler_matches(handler, data):
    for filter_obj in handler.filters:
        if not await filter_matches(filter_obj, data):
            return False
    return True


def main_order():
    text = (_ROOT / "main.py").read_text(encoding="utf-8", errors="replace")
    imports = {alias: module for module, alias in re.findall(
        r"from\s+bot\.handlers\.(\w+)\s+import\s+router\s+as\s+(\w+)", text)}
    order = []
    for alias in re.findall(r"include_router\((\w+)\)", text):
        module = imports.get(alias)
        if module and module not in order:
            order.append(module)
    return order


async def run():
    candidates = collect_candidates()
    routers = load_modules()
    entries = collect_handlers(routers)
    order = main_order()

    print(f"Кандидатов callback_data: {len(candidates)}")
    print(f"Модулей с callback_query: {len(routers)}")
    print(f"Хендлеров callback_query: {len(entries)}")
    print(f"Порядок include_router в main.py: {len(order)} роутеров")
    print()

    passed = 0
    failed = 0

    def ok(msg):
        nonlocal passed
        passed += 1
        print(f"  OK   {msg}")

    def fail(msg):
        nonlocal failed
        failed += 1
        print(f"  FAIL {msg}")

    print("1. Коллизии: кандидат матчится хендлерами из 2+ модулей")
    collisions = []
    for data in candidates:
        modules = {}
        for module, handler in entries:
            if await handler_matches(handler, data):
                modules.setdefault(module, []).append(handler.callback.__name__)
        if len(modules) > 1:
            collisions.append((data, modules))
    if collisions:
        for data, modules in collisions:
            detail = "; ".join(
                f"{m}: {', '.join(sorted(set(names)))}" for m, names in sorted(modules.items()))
            fail(f"{data!r} -> {detail}")
    else:
        ok(f"коллизий нет среди {len(candidates)} кандидатов")

    print()
    print("2. Регрессия news: (владелец каждого callback)")
    matched_by_module = {}
    for data, expected in NEWS_EXPECTED.items():
        modules = {}
        for module, handler in entries:
            if await handler_matches(handler, data):
                modules.setdefault(module, []).append(handler.callback.__name__)
        matched_by_module[data] = modules
        if set(modules) != {expected}:
            got = ", ".join(sorted(modules)) or "ни одного"
            fail(f"{data!r}: ожидался {expected}, матчит {got}")
        else:
            ok(f"{data!r} -> {expected}:{modules[expected][0]}")

    print()
    print("3. Админский обработчик не забирает публичные новости")
    admin_handlers = {h.callback.__name__: h for m, h in entries if m == "admin"}
    news_chat = admin_handlers.get("admin_news_chat")
    if news_chat is None:
        fail("не найден хендлер admin.admin_news_chat")
    else:
        for data in ("news:tab", "news:view:1", "news:archive", "news:write",
                     "news:edit:1", "news:del:1", "news:delconf:1", "news:arch:1"):
            if await handler_matches(news_chat, data):
                fail(f"admin_news_chat всё ещё ловит {data!r}")
            else:
                ok(f"admin_news_chat не ловит {data!r}")
        for data in ("news:off", "news:chat:-1001234567890:0", "news:topic:-1001234567890:5",
                     "news:allow:-1001234567890", "news:disallow:-1001234567890"):
            if not await handler_matches(news_chat, data):
                fail(f"admin_news_chat перестал ловить свою кнопку {data!r}")
            else:
                ok(f"admin_news_chat ловит свою кнопку {data!r}")

    print()
    print("4. Порядок роутеров: admin/news не перепутаны, все импорты найдены")
    if "admin" in order and "news" in order:
        if order.index("admin") < order.index("news"):
            ok(f"admin_router ({order.index('admin')}) раньше news_router ({order.index('news')}) "
               f"— порядок из main.py, разведение префиксов обязательно")
        else:
            ok(f"news_router ({order.index('news')}) раньше admin_router ({order.index('admin')})")
    else:
        fail(f"не найден admin/news в порядке include_router: {order}")
    missing = [n for n in routers if routers[n] is not None and n not in order]
    if missing:
        fail(f"модули без include_router в main.py: {sorted(missing)}")
    else:
        ok(f"все {len([n for n in routers if routers[n] is not None])} модулей подключены в main.py")

    print()
    print(f"ИТОГО: {passed} OK, {failed} FAIL")
    return failed


if __name__ == "__main__":
    fails = asyncio.run(run())
    sys.exit(1 if fails else 0)
