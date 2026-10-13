"""Smoke v0.23.9: два фикса навигации/инфраструктуры.

Фикс 1: из `utils.helpers.MAIN_MENU_TEXTS` убран рудимент «Банк» (кнопки «Банк»
в reply-меню нет — банк открывается через «Город»). Раньше `is_main_menu_text`
считал вводом-навигацией слово, которого нет ни на одной кнопке, и FSM-формы
молча отбрасывали его как данные (например, вариант опроса «Банк»).

Фикс 2: `tourist_booklet_router` подключён (`include_router`), но не входил в
цикл навешивания middleware в `main.py`. На его callback-кнопках не работали
ChatGuard / FishingActiveLock / ActivityTracker. Теперь входит — и тест
проверяет, что КАЖДЫЙ подключённый роутер охвачен middleware-циклом.

Проверяет:
1. «Банк» отсутствует в MAIN_MENU_TEXTS и is_main_menu_text("Банк") == False.
2. Остальные реальные кнопки меню по-прежнему распознаются.
3. tourist_booklet_router присутствует в кортеже middleware-цикла main.py.
4. Множество роутеров из include_router ⊆ множеству роутеров middleware-цикла.

Запуск: .venv\\Scripts\\python.exe smoke_140.py
"""
import os
import re
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(__file__))

_ROOT = os.path.dirname(os.path.abspath(__file__))


def run():
    from utils.helpers import MAIN_MENU_TEXTS, is_main_menu_text

    passed = 0
    failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
            print(f"  ok   {name}")
        else:
            failed += 1
            print(f"  FAIL {name}")

    # ── 1-2. Рудимент «Банк» убран, реальные кнопки распознаются ──
    check("«Банк» отсутствует в MAIN_MENU_TEXTS", "Банк" not in MAIN_MENU_TEXTS)
    check("is_main_menu_text(\"Банк\") == False", is_main_menu_text("Банк") is False)
    for text in ("Профиль", "Инвентарь", "Магазин", "Город",
                 "📝 Сдать отчёт", "👑 Админ-панель", "🧱 Стена изречений"):
        check(f"«{text}» распознаётся как главное меню", is_main_menu_text(text))
    check("произвольный текст не распознаётся", not is_main_menu_text("привет"))

    # ── 3-4. Middleware-цикл покрывает все include_router ──
    src = open(os.path.join(_ROOT, "main.py"), encoding="utf-8").read()

    included = set(re.findall(r"include_router\((\w+)\)", src))
    m = re.search(r"for r in \((.*?)\):", src, re.DOTALL)
    check("в main.py найден цикл `for r in (...)`", m is not None)
    loop_routers = set(re.findall(r"\b(\w+_router)\b", m.group(1))) if m else set()

    check("tourist_booklet_router входит в middleware-цикл",
          "tourist_booklet_router" in loop_routers)
    missing = included - loop_routers
    check(f"все {len(included)} подключённых роутеров покрыты middleware (нет {sorted(missing)})",
          not missing)

    print(f"\n{passed} passed, {failed} failed")
    return failed


if __name__ == "__main__":
    sys.exit(1 if run() else 0)
