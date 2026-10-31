# -*- coding: utf-8 -*-
"""Smoke 187 — праздничная лавка на входе в Лабиринт (подготовлена, выключена флагом).

1. FIRE_EXCHANGE_ENABLED = False: лавка закрыта, обмен не происходит.
2. При включении: 3 сена → 1 леденец; при нехватке предметы не меняются.
"""
import asyncio
import os
import sys

os.environ["DATABASE_PATH"] = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "_test_smoke187.db")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def main():
    passed = failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
            print(f"  OK  {name}")
        else:
            failed += 1
            print(f"  FAIL {name}")

    db_file = os.environ["DATABASE_PATH"]
    if os.path.exists(db_file):
        os.remove(db_file)
    import config
    import database.db as db
    from database.db import (init_db, close_db, get_db, add_user, update_user,
                             ensure_firelab_items, get_item_by_name,
                             add_inventory_item, get_inventory_item)
    from bot.handlers import fire_event as fe

    await init_db()
    conn = await get_db()
    for tbl in ("inventory", "users"):
        await conn.execute(f"DELETE FROM {tbl}")
        await conn.commit()
    await ensure_firelab_items()
    UID = 187001
    await add_user(UID, 't', 'Пилот 187', "")
    await update_user(UID, nordmarks=1000)
    hay = await get_item_by_name(config.FIRE_LAB_HAY_NAME)
    candy = await get_item_by_name(config.FIRE_LAB_CANDY_NAME)

    class FakeBot:
        async def send_message(self, chat_id, text, **kw):
            return type("M", (), {"message_id": 44, "chat": type("C", (), {"id": chat_id})()})()
        async def send_photo(self, chat_id, *a, **kw):
            return type("M", (), {"message_id": 45, "chat": type("C", (), {"id": chat_id})()})()
        async def delete_message(self, *a, **kw):
            return True

    class FakeMsg:
        chat = type("C", (), {"id": UID})()
        message_id = 42
        bot = FakeBot()
        async def answer(self, *a, **kw):
            return type("M", (), {"message_id": 43, "chat": type("C", (), {"id": UID})()})()
        async def edit_text(self, *a, **kw):
            return True
        async def edit_caption(self, *a, **kw):
            return True
        async def edit_media(self, *a, **kw):
            return True
        async def delete(self):
            return True

    class FakeCB:
        alerts = []
        def __init__(self, data):
            self.from_user = type("U", (), {"id": UID})()
            self.data = data
            self.message = FakeMsg()
        async def answer(self, text=None, show_alert=False, **kw):
            if show_alert and text:
                FakeCB.alerts.append(text)
            return True

    async def qty(item):
        inv = await get_inventory_item(UID, item['id'])
        return int(inv['quantity']) if inv else 0

    print("\n1. Лавка выключена флагом")
    config.FIRE_EXCHANGE_ENABLED = False
    await add_inventory_item(UID, hay['id'], 3)
    FakeCB.alerts.clear()
    await fe.fire_event_shop_cb(FakeCB("fireevent:shop"))
    check("лавка закрыта (alert)", any("не открыта" in a for a in FakeCB.alerts))
    await fe.fire_event_xchg_cb(FakeCB("fireevent:xchg:0"))
    check("обмен при выключенной лавке не происходит", await qty(hay) == 3 and await qty(candy) == 0)

    check("картинка лавки есть в менеджере «Картинки Круговорота»", "shop" in db.FIRE_PHOTO_KEYS)

    print("\n2. Лавка включена: обмен 3 сена → 1 леденец")
    config.FIRE_EXCHANGE_ENABLED = True
    try:
        await fe.fire_event_xchg_cb(FakeCB("fireevent:xchg:0"))
        check("3 сена → 1 леденец", await qty(hay) == 0 and await qty(candy) == 1)
        FakeCB.alerts.clear()
        await fe.fire_event_xchg_cb(FakeCB("fireevent:xchg:0"))
        check("без сена обмен отказан (alert)", any("Нужно" in a for a in FakeCB.alerts))
        check("леденцы не изменились", await qty(candy) == 1)
    finally:
        config.FIRE_EXCHANGE_ENABLED = False

    print(f"\nИТОГО: {passed} passed, {failed} failed")
    await close_db()
    return failed


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
