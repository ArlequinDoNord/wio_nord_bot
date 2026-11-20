# -*- coding: utf-8 -*-
"""Smoke 237 — меню контрактов на поставку подключено к рынку.

- модуль меню импортируется, роутер подключён в main.py;
- на странице рынка есть кнопка «📜 Контракты на поставку» (mkt:contracts);
- на других категориях её нет;
- в меню есть обработчики выставления, закрытия, отмены, «мои контракты».

Прогон: .\\.venv\\Scripts\\python.exe smoke_237.py
"""
import asyncio
import os
import sys

_TEST_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_test_smoke237.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

passed = failed = 0


def check(name, cond):
    global passed, failed
    if cond:
        passed += 1
        print(f"  OK  {name}")
    else:
        failed += 1
        print(f"  FAIL: {name}")


async def run():
    from database.db import init_db, close_db
    await init_db()
    try:
        from bot.handlers import market_contracts as MH
        from bot.handlers import shop as S
        check("роутер меню контрактов есть", MH.router is not None)

        print("\n1. Кнопка на странице рынка")
        kb_market = await S.items_page_markup([], "market", 0, user_id=1)
        cbs = [b.callback_data for row in kb_market.inline_keyboard for b in row]
        check("на рынке есть mkt:contracts", "mkt:contracts" in cbs)
        kb_other = await S.items_page_markup([], "food", 0, user_id=1)
        cbs_o = [b.callback_data for row in kb_other.inline_keyboard for b in row]
        check("в других категориях кнопки нет", "mkt:contracts" not in cbs_o)

        print("\n2. Обработчики меню")
        names = {h.callback.__name__ for h in MH.router.callback_query.handlers}
        for n in ("contracts_menu", "contracts_mine", "contract_view", "contract_close",
                  "contract_cancel", "contract_new", "contract_pick", "contract_confirm"):
            check(f"обработчик {n}", n in names)
    finally:
        await close_db()


if __name__ == "__main__":
    asyncio.run(run())
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
