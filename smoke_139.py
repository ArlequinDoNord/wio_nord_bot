"""Smoke v0.23.8: ХРАНИЛИЩЕ — кнопки категорий снова открываются.

Регресс: `storage_markup` обращался к несуществующей колонке `it['is_hidden']`
(в таблице `items` есть только `is_available`), из-за чего ЛЮБАЯ категория
падала с `KeyError: 'is_hidden'` и «в них нельзя было зайти».

Проверяет:
1. `storage_markup` строится без ошибок для всех категорий и для «Все предметы».
2. У непустой категории есть хотя бы одна кнопка-предмет, у пустой — нет.
3. Скрытый предмет (is_available=0) помечается «🔴 … снят с продажи»,
   рыночный (market_ok=1) — с пометкой 🏪.
4. Предмет в продаже (is_available=1) помечается «🟢/🟡 ... (ост. N)».
5. Loot-only предмет помечается «🎯 ... только лут».
6. Пагинация: больших категорий достаточно, чтобы появились ◀️/▶️.
7. Переданные callback_data категорий совпадают с теми, что ловит хендлер
   (`storage:cat:<key>:page:<n>`).

Запуск: .venv\\Scripts\\python.exe smoke_139.py
"""
import asyncio
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke139.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB

sys.path.insert(0, os.path.dirname(__file__))


def _texts(markup):
    return [b.text for row in markup.inline_keyboard for b in row]


def _callbacks(markup):
    return [b.callback_data for row in markup.inline_keyboard for b in row]


async def run():
    from config import ITEM_CATEGORIES
    from database.db import (
        init_db, close_db, add_item, update_item, get_item,
        get_items_by_category, get_all_items, count_items_by_category,
    )
    from bot.handlers.admin import storage_markup, storage_main_markup

    await init_db()

    await add_item(name="__smoke139_seed_weapon__", description="", price=1,
                   sell_price=0, rarity=1, category="weapon",
                   stock=3, added_by=0)

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

    # ── 1. Главный экран: категории с их callback_data ──
    counts = await count_items_by_category()
    main = storage_main_markup(counts)
    cat_cbs = [c for c in _callbacks(main) if c and c.startswith("storage:cat:")]
    check("главный экран содержит кнопки категорий", len(cat_cbs) > 0)
    check("все callback категорий формата storage:cat:<key>:page:0",
          all(c.endswith(":page:0") and len(c.split(":")) == 5 for c in cat_cbs))

    # ── 2. Каждая категория строится без KeyError ──
    keys = list(ITEM_CATEGORIES.keys()) + ["all"]
    built_ok = 0
    mismatch = 0
    for key in keys:
        try:
            items = await get_items_by_category(key)
            mk = storage_markup(items, page=0, cat_key=key)
            built_ok += 1
            # callback_data пагинации должен нести тот же ключ категории
            for cb in _callbacks(mk):
                if cb and cb.startswith("storage:cat:"):
                    parts = cb.split(":")
                    if len(parts) != 5 or parts[2] != key:
                        mismatch += 1
        except Exception as e:  # noqa: BLE001
            print(f"  !! {key}: {type(e).__name__}: {e}")
    check(f"все {len(keys)} категорий строятся без ошибок", built_ok == len(keys))
    check("пагинация сохраняет ключ категории", mismatch == 0)

    # ── 3. Непустая категория → есть предмет; пустая → нет ──
    nonempty_key = None
    for key in keys:
        if key == "all":
            continue
        items = await get_items_by_category(key)
        mk = storage_markup(items, cat_key=key)
        item_btns = [c for c in _callbacks(mk) if c and c.startswith("storage:item:")]
        if items:
            if nonempty_key is None:
                nonempty_key = key
            check(f"категория «{key}»: {len(item_btns)} кнопок-предметов == {len(items)}",
                  len(item_btns) == len(items))
        else:
            check(f"пустая категория «{key}»: кнопок-предметов нет", len(item_btns) == 0)
    check("есть хотя бы одна непустая категория", nonempty_key is not None)

    # ── 4-6. Спец-маркеры на синтетических предметах ──
    hidden_id = await add_item(name="__smoke139_hidden__", description="", price=1,
                               sell_price=0, rarity=1, category="special",
                               stock=5, added_by=0)
    await update_item(hidden_id, is_available=0)
    shown_id = await add_item(name="__smoke139_shown__", description="", price=1,
                              sell_price=0, rarity=1, category="special",
                              stock=7, added_by=0)
    loot_id = await add_item(name="__smoke139_loot__", description="", price=1,
                             sell_price=0, rarity=1, category="special",
                             stock=-1, added_by=0)
    await update_item(loot_id, loot_only=1, market_ok=0, is_available=0)

    special = await get_items_by_category("special")
    mk = storage_markup(special, cat_key="special")
    joined = "\n".join(_texts(mk))

    check("скрытый помечен 🔴 … снят с продажи",
          f"🔴 __smoke139_hidden__ — снят с продажи" in joined)
    check("в продаже помечен 🟢 … (ост. 7)", "🟢 __smoke139_shown__ (ост. 7)" in joined)
    check("loot-only помечен 🎯 … только лут", "🎯 __smoke139_loot__ — только лут" in joined)
    # рыночный: создаём предмет с market_ok=1 и проверяем 🏪 в его строке
    market_item = await add_item(name="__smoke139_market__", description="", price=1,
                                 sell_price=1, rarity=1, category="special",
                                 stock=3, added_by=0, market_ok=1)
    special2 = await get_items_by_category("special")
    mk2 = storage_markup(special2, cat_key="special")
    joined2 = "\n".join(_texts(mk2))
    check("рыночный предмет помечен 🏪",
          f"🏪" in joined2
          and "__smoke139_market__" in joined2)
    check("скрытый предмет в наборе кнопок",
          f"storage:item:{hidden_id}" in _callbacks(mk))

    # ── 7. Пагинация на большой категории ──
    for i in range(25):
        await add_item(name=f"__smoke139_bulk_{i}__", description="", price=1,
                       sell_price=0, rarity=1, category="special",
                       stock=1, added_by=0)
    bulk = await get_items_by_category("special")
    mk0 = storage_markup(bulk, page=0, cat_key="special")
    cbs0 = _callbacks(mk0)
    check("на первой странице есть ▶️", any(c and c.endswith(":page:1") for c in cbs0))
    check("на первой странице нет ◀️", not any(c and c.endswith(":page:-1") for c in cbs0))
    mk1 = storage_markup(bulk, page=1, cat_key="special")
    cbs1 = _callbacks(mk1)
    check("на второй странице есть ◀️", any(c and c.endswith(":page:0") for c in cbs1))

    # ── 8. Пустой список (например, «предмет не найден») ──
    empty_mk = storage_markup([])
    check("пустой список → только навигация, без ошибок",
          storage_markup([]) is not None and len(_callbacks(empty_mk)) >= 1)

    await close_db()

    print(f"\n{passed} passed, {failed} failed")
    return failed


if __name__ == "__main__":
    sys.exit(1 if asyncio.run(run()) else 0)
