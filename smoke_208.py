# -*- coding: utf-8 -*-
"""Smoke 208 — после поиска ягод на опушке есть кнопка «Углубиться в лес».

1. Опушка, прогалина открыта: кнопка «Углубиться в лес» ведёт в прогалину.
2. Опушка, прогалина закрыта: кнопки нет, остаётся возврат в город.
3. Прогалина: кнопки «Углубиться» нет (она и так глубже), есть лесозаготовка.
4. В кнопках всегда есть «В город» и поиск ягод ещё.
"""
import asyncio
import sys

from tests_support import Checker, use_test_db

_TEST_DB = use_test_db(__file__, "smoke208")


async def main():
    check = Checker()

    import database.db as db
    from database.db import init_db, close_db
    from bot.handlers import forest as fo

    await init_db()
    TOKEN = "123"

    def cbs(kb):
        return [b.callback_data for row in kb.inline_keyboard for b in row]

    print("\n1. Опушка, прогалина открыта")
    orig = fo._zone_open

    async def open_zone(area):
        return True

    async def closed_zone(area):
        return False

    try:
        fo._zone_open = open_zone
        kb = await fo._berry_markup(TOKEN, "glade")
        check("кнопка «Углубиться в лес» есть",
              f"forest:area:{TOKEN}:clearing" in cbs(kb))
        check("возврат в город есть", "city:menu" in cbs(kb))
        check("поиск ягод ещё есть", f"forest:berry:{TOKEN}:glade" in cbs(kb))

        print("\n2. Опушка, прогалина закрыта")
        fo._zone_open = closed_zone
        kb2 = await fo._berry_markup(TOKEN, "glade")
        check("кнопки «Углубиться» нет", f"forest:area:{TOKEN}:clearing" not in cbs(kb2))
        check("возврат в город остался", "city:menu" in cbs(kb2))

        print("\n3. Прогалина")
        fo._zone_open = open_zone
        kb3 = await fo._berry_markup(TOKEN, "clearing")
        check("на прогалине кнопки «Углубиться» нет",
              f"forest:area:{TOKEN}:clearing" not in cbs(kb3))
        check("на прогалине есть лесозаготовка", "logsite:enter" in cbs(kb3))
    finally:
        fo._zone_open = orig

    failed = check.summary()
    await close_db()
    return failed


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
