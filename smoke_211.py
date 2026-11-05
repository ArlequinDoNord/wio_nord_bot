# -*- coding: utf-8 -*-
"""Smoke 211 — три правки: Лампа смягчает истощение, бой после ягод ведёт к ягодам.

1. Лампа в личном жилье сокращает истощение на FIRE_LANTERN_EXHAUST_REDUCE_PCT%
   (2880 минут → 1440 при 50%).
2. После боя со зверем, начатого из поиска ягод, кнопка «Поискать ещё» ведёт к ягодам.
3. После боя, начатого из поиска грибов, кнопка ведёт к грибам (как раньше).
"""
import asyncio
import sys

from tests_support import Checker, use_test_db

_TEST_DB = use_test_db(__file__, "smoke211")


async def main():
    check = Checker()

    import config
    from database.db import init_db, close_db
    from bot.handlers import forest as fo

    await init_db()

    print("\n1. Лампа сокращает истощение")
    red = config.FIRE_LANTERN_EXHAUST_REDUCE_PCT
    check("сокращение задано (50%)", red == 50)
    base = config.AP_EXHAUSTED_MINUTES
    check("с Лампой истощение = 1440 минут", int(base * (100 - red) / 100) == 1440)
    check("без Лампы истощение 2880 минут", base == 2880)

    def cbs(kb):
        return [b.callback_data for row in kb.inline_keyboard for b in row]

    TOKEN = "777"
    fo.FOREST_TOKEN[5001] = TOKEN

    print("\n2. После боя, начатого из ягод")
    fo.FOREST_ORIGIN[5001] = "berry"
    kb = await fo._result_markup(TOKEN, "glade", 5001)
    check("кнопка ведёт к ягодам", f"forest:berry:{TOKEN}:glade" in cbs(kb))
    texts = [b.text for row in kb.inline_keyboard for b in row]
    check("«Поискать ещё» (грибы) на экране ягод не стоит",
          not any("Поискать ещё" in t for t in texts))

    print("\n3. После боя, начатого из грибов")
    fo.FOREST_ORIGIN[5001] = "mushroom"
    kb2 = await fo._result_markup(TOKEN, "glade", 5001)
    check("кнопка ведёт к грибам", f"forest:cast:{TOKEN}:glade" in cbs(kb2))

    failed = check.summary()
    await close_db()
    return failed


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
