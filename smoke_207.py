# -*- coding: utf-8 -*-
"""Smoke 207 — подтверждение продажи привязано к полю редкости.

1. Вилы имеют редкость 3 (Редкий) после сида и миграции.
2. Продажа предмета редкости 3+ сначала ведёт на второй шаг подтверждения.
3. Продажа обычного предмета (редкость 1) — сразу на финальное «да».
4. Второй шаг показывает предупреждение и ведёт на продажу.
"""
import asyncio
import sys

from tests_support import Checker, FakeCB, use_test_db

_TEST_DB = use_test_db(__file__, "smoke207")


async def main():
    check = Checker()

    import config
    import database.db as db
    from database.db import (init_db, close_db, add_user, update_user, get_item_by_name,
                             add_inventory_item, ensure_firelab_items)
    from bot.handlers import inventory as inv

    await init_db()
    await ensure_firelab_items()
    U = 207001
    await add_user(U, "sell", "Продажа", "")
    await update_user(U, nordmarks=100)

    print("\n1. Редкость вил")
    keys = await get_item_by_name(config.FIRE_KEYS_NAME)
    check("вилы — редкость 3", keys is not None and int(keys["rarity"]) == 3)

    print("\n2. Редкий предмет: первый шаг ведёт на второе подтверждение")
    await add_inventory_item(U, keys["id"], 1)
    cb = FakeCB(U, f"invsell:{keys['id']}")
    await inv._sell_confirm(cb, keys["id"], 1)
    buttons = [b.callback_data for row in cb.message.kb.inline_keyboard for b in row]
    check("кнопка «Да» ведёт на inv_sell_ask", f"inv_sell_ask:{keys['id']}:1" in buttons)

    cb2 = FakeCB(U, f"inv_sell_ask:{keys['id']}:1")
    await inv.inv_sell_ask(cb2)
    text = cb2.message.text or ""
    check("второй шаг с предупреждением о редкости", "Редкий" in text and "не вернуть" in text)
    final = [b.callback_data for row in cb2.message.kb.inline_keyboard for b in row]
    check("финальная кнопка продаёт", f"inv_sell_ok:{keys['id']}:1" in final)

    print("\n3. Обычный предмет: сразу финальное «да»")
    hay = await get_item_by_name(config.FIRE_LAB_HAY_NAME)
    await add_inventory_item(U, hay["id"], 1)
    cb3 = FakeCB(U, f"invsell:{hay['id']}")
    await inv._sell_confirm(cb3, hay["id"], 1)
    btns = [b.callback_data for row in cb3.message.kb.inline_keyboard for b in row]
    check("обычный предмет: кнопка ведёт сразу на продажу",
          f"inv_sell_ok:{hay['id']}:1" in btns)

    print("\n4. Порог из конфига")
    check("порог продажи с подтверждением = 3", config.SALE_CONFIRM_MIN_RARITY == 3)

    failed = check.summary()
    await close_db()
    return failed


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
