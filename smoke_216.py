# -*- coding: utf-8 -*-
"""Smoke 216 — лес: кнопки после поиска и возврат из лесозаготовки.

1. После успешного поиска грибов на прогалине есть поиск ягод и переход на опушку.
2. После поиска ягод на прогалине есть переход на опушку (раньше — только город).
3. На опушке после грибов и ягод есть переход вглубь (если прогалина открыта).
4. Возврат из лесозаготовки открывает прогалину (а не опушку) и выдаёт новый токен.
5. Вход из города по-прежнему открывает опушку.
"""
import asyncio
import sys

from tests_support import Checker, use_test_db

_TEST_DB = use_test_db(__file__, "smoke216")


async def main():
    check = Checker()

    from database.db import init_db, close_db
    from bot.handlers import forest as fo
    from bot.handlers import logging_site as ls

    await init_db()

    TOKEN = "654321"

    def cbs(kb):
        return [b.callback_data for row in kb.inline_keyboard for b in row]

    def texts(kb):
        return [b.text for row in kb.inline_keyboard for b in row]

    orig_zone_open = fo._zone_open

    async def open_zone(area):
        return True

    try:
        fo._zone_open = open_zone

        print("\n1. Прогалина: после грибов")
        kb = await fo._result_markup(TOKEN, "clearing", 7001)
        check("поиск ягод есть", f"forest:berry:{TOKEN}:clearing" in cbs(kb))
        check("поиск грибов ещё есть", f"forest:cast:{TOKEN}:clearing" in cbs(kb))
        check("переход на опушку есть", f"forest:area:{TOKEN}:glade" in cbs(kb))
        check("лесозаготовка есть", "logsite:enter" in cbs(kb))
        check("в город есть", "city:menu" in cbs(kb))

        print("\n2. Прогалина: после ягод")
        kb2 = await fo._berry_markup(TOKEN, "clearing")
        check("переход на опушку есть", f"forest:area:{TOKEN}:glade" in cbs(kb2))
        check("грибы есть", f"forest:cast:{TOKEN}:clearing" in cbs(kb2))
        check("поиск ягод ещё есть", f"forest:berry:{TOKEN}:clearing" in cbs(kb2))

        print("\n3. Опушка: переход вглубь")
        kb3 = await fo._result_markup(TOKEN, "glade", 7001)
        check("«Углубиться» на опушке после грибов",
              f"forest:area:{TOKEN}:clearing" in cbs(kb3))
        kb4 = await fo._berry_markup(TOKEN, "glade")
        check("«Углубиться» на опушке после ягод",
              f"forest:area:{TOKEN}:clearing" in cbs(kb4))

        print("\n4. Возврат из лесозаготовки — на прогалину")
        opened = []

        async def fake_show_area(callback, area, prefix=""):
            opened.append((area, FakeCB.last_token(callback)))

        class FakeCB:
            _tok = None

            def __init__(self, uid):
                self.from_user = type("U", (), {"id": uid})()
                self.message = type("M", (), {"answer": self._answer})()

            async def answer(self, *a, **kw):
                return True

            async def _answer(self, *a, **kw):
                return True

            @staticmethod
            def last_token(callback):
                return fo.FOREST_TOKEN.get(callback.from_user.id)

        orig_show = fo._show_area
        fo._show_area = fake_show_area
        try:
            cb = FakeCB(7001)
            fo.FOREST_TOKEN[7001] = "old"
            await ls.logging_back(cb)
            check("возврат открывает прогалину", opened and opened[-1][0] == "clearing")
            check("возврат выдаёт новый токен", opened and opened[-1][1] not in (None, "old"))

            opened.clear()
            cb2 = FakeCB(7002)
            await fo.forest_menu_cb(cb2)
            check("вход из города открывает опушку", opened and opened[-1][0] == "glade")
        finally:
            fo._show_area = orig_show
    finally:
        fo._zone_open = orig_zone_open

    failed = check.summary()
    await close_db()
    return failed


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
