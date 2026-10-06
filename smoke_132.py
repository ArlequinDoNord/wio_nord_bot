"""Smoke v0.22.9: заголовок «Улов» в инвентаре — суточный лимит выкупа рыбы.

Проверяет ветку `inventory_cat_cb` (`inventory:cat:__fish__`) от текущего состояния
`fish_sold_today`:
1. лимит НЕ исчерпан → в шапке строка «💵 Скупщик: … доступно сегодня»;
2. лимит исчерпан (sold == FISH_TREASURY_DAILY_LIMIT) → «🚫 Суточный лимит выкупа
   рыбы исчерпан», а не «доступно»-строка.

Регрессия v0.22.8: `if fish_sale_daily_left(user_id)` без `await` — тело корутины
всегда истинно, поэтому при исчерпании лимита шапка врала («доступно 0 НМ»),
плюс в логах висело RuntimeWarning «coroutine ... was never awaited».

Запуск: .venv\\Scripts\\python.exe smoke_132.py
"""
import asyncio
import os
import sys
from types import SimpleNamespace

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke132.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB

sys.path.insert(0, os.path.dirname(__file__))


class FakeTextMessage:
    def __init__(self, user_id):
        self.from_user = SimpleNamespace(id=user_id)
        self.chat = SimpleNamespace(id=user_id)
        self.photo = None
        self.edited = []

    async def edit_text(self, text, **kw):
        self.edited.append(text)
        return SimpleNamespace(message_id=1)

    async def answer(self, *a, **kw):
        pass

    async def __getattr__(self, name):
        async def _noop(*a, **kw):
            return None
        return _noop


class FakeCallback:
    def __init__(self, user_id, data, message=None):
        self.from_user = SimpleNamespace(id=user_id)
        self.message = message or FakeTextMessage(user_id)
        self.data = data
        self.alerts = []

    async def answer(self, text=None, *a, **kw):
        self.alerts.append(text)


async def run():
    from database.db import (
        init_db, close_db, seed_default_items, ensure_water_fish,
        ensure_dungeon_shop_items, ensure_life_items, ensure_forest_items,
        get_item_by_name, add_user, add_fish_catch, add_fish_sale_amount,
        fish_sold_today,
    )
    from config import FISH_TREASURY_DAILY_LIMIT
    from bot.handlers.inventory import inventory_cat_cb

    await init_db()
    await seed_default_items()
    await ensure_dungeon_shop_items()
    await ensure_life_items()
    await ensure_forest_items()
    await ensure_water_fish()

    uid = 442001
    await add_user(uid, "fisher", "Рыбак", "")

    passed = 0
    failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
        else:
            failed += 1
            print(f"  FAIL: {name}")

    sig = await get_item_by_name("Сиг")
    check("предмет «Сиг» существует", sig is not None)

    # ── 1. Лимит не исчерпан → «доступно сегодня» ──
    await add_fish_catch(uid, sig['id'], weight=1, kind="resource")
    msg1 = FakeTextMessage(uid)
    await inventory_cat_cb(FakeCallback(uid, "inventory:cat:__fish__", message=msg1))
    h1 = msg1.edited[-1] if msg1.edited else ""
    check("шапка «Улов» открылась", "Улов:" in h1)
    check("при остатке лимита — «доступно сегодня»",
          "доступно сегодня" in h1 and "Скупщик:" in h1)

    # ── 2. Лимит исчерпан → «исчерпан», а не «доступно» ──
    await add_fish_sale_amount(uid, FISH_TREASURY_DAILY_LIMIT + 1)
    check("счётчик продажи выставлен выше лимита",
          await fish_sold_today(uid) >= FISH_TREASURY_DAILY_LIMIT)
    msg2 = FakeTextMessage(uid)
    await inventory_cat_cb(FakeCallback(uid, "inventory:cat:__fish__", message=msg2))
    h2 = msg2.edited[-1] if msg2.edited else ""
    check("при исчерпании лимита — «Суточный лимит исчерпан»",
          "исчерпан" in h2)
    check("при исчерпании больше нет строки «доступно»",
          "доступно сегодня" not in h2)

    await close_db()
    print(f"\nSmoke 132: {passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    try:
        asyncio.run(run())
    except SystemExit:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        from database.db import close_db
        asyncio.run(close_db())
        print(f"SMOKE ERROR: {e!r}")
        sys.exit(1)
