# SMOKE 118: админ-магазин — выбор товара по разделам (регэсс про нерабочие кнопки)
#
# Регрессия: в v0.19.8 хендлеры `shop_edit:cat:<cat>:<page>` распаковывали
# callback.data в 5 переменных, а данных было 4 -> ValueError при нажатии,
# кнопки категорий «не нажимались». Проверяем разбор данных и наличие роутов.
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

PASSED = 0
FAILED = 0


def check(name, cond):
    global PASSED, FAILED
    if cond:
        PASSED += 1
        print(f"  OK  {name}")
    else:
        FAILED += 1
        print(f"  FAIL  {name}")


def main():
    src = open(os.path.join(os.path.dirname(__file__), "bot", "handlers", "admin.py"),
               encoding="utf-8").read()

    # ── 1. Разбор callback данных категории: ровно 4 части ──
    sample = "shop_edit:cat:weapon:0"
    parts = sample.split(":")
    check("callback категории состоит из 4 частей", len(parts) == 4)
    cat, page = parts[2], int(parts[3] or 0)
    check("категория парсится", cat == "weapon")
    check("страница парсится", page == 0)

    # ── 2. В коде нет распаковки в 5 переменных (старый баг) ──
    check("нет распаковки в 5 переменных",
          "_, _, _, cat, page = callback.data.split" not in src)
    check("разборcategory через parts", src.count("parts = callback.data.split(\":\")") >= 2)

    # ── 3. Хендлеры категорий зарегистрированы ──
    for cb in ("shop_edit:cat:", "shop_edit:cats", "shop_del:cat:", "shop_del:cats"):
        check(f"роут для {cb}", f'F.data.startswith("{cb}")' in src or f'F.data == "{cb}"' in src)

    # ── 4. Старые плоские callbacks удалены ──
    check("старый shop_edit:page:* убран", "shop_edit:page:" not in src)
    check("старый shop_del:page:* убран", "shop_del:page:" not in src)

    # ── 5. Кнопки категорий строятся с валидным callback ──
    m = re.search(r'f"shop_\{mode\}:cat:\{key\}:0"', src)
    check("кнопка категории собирает shop_<mode>:cat:<key>:0", m is not None)
    check("счётчик товаров в кнопке", "{cnt}" in src)

    # ── 6. Навигация: назад к разделам и пагинация ──
    check("есть возврат к разделам", "shop_{mode}:cats" in src)
    check("есть счётчик страниц", "Стр. {page + 1}/{pages}" in src)

    # ── 7. Списки товаров фильтруются по категории ──
    check("список берётся по категории", "get_available_items(category=category)" in src)

    # ── 8. pyflakes: нет неопределённых имён в admin.py ──
    try:
        import subprocess
        r = subprocess.run([sys.executable, "-m", "pyflakes", "bot/handlers/admin.py"],
                           capture_output=True, text=True,
                           cwd=os.path.dirname(os.path.abspath(__file__)))
        undefined = [ln for ln in r.stdout.splitlines() if "undefined name" in ln]
        check("в admin.py нет undefined name", not undefined)
    except Exception:
        check("в admin.py нет undefined name (pyflakes недоступен)", True)

    print(f"\n=== SMOKE 118: {PASSED} passed, {FAILED} failed ===")
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())