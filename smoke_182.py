# -*- coding: utf-8 -*-
"""Smoke 182 — Колодец Огненного Круговорота: рыбалка как на озере.

1. Без удочки заброс не делается (alert), ОД и наживка не списываются.
2. Без выбранной наживки заброс не делается.
3. С удочкой и наживкой: списываются ОД (FISH_AP_COST) и 1 наживка, растёт fish_used.
"""
import asyncio
import os
import sys

os.environ["DATABASE_PATH"] = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "_test_smoke182.db")

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

    import database.db as db
    import config
    from database.db import (
        init_db, close_db, get_db, add_user, update_user, add_item, get_item_by_name,
        add_inventory_item, get_inventory_item, create_fire_lab_session,
    )
    from bot.handlers import fire_event as fe
    from bot.handlers import fishing as fs

    await init_db()
    conn = await get_db()
    for tbl in ("fire_lab_sessions", "inventory", "users"):
        try:
            await conn.execute(f"DELETE FROM {tbl}")
            await conn.commit()
        except Exception:
            pass
    UID = 182001
    await add_user(UID, 't', 'Пилот 182', "")
    await update_user(UID, nordmarks=1000, ap=50, ap_max=50, fishing_bait="worms")
    if not await get_item_by_name(fs.WORMS_NAME):
        await add_item(fs.WORMS_NAME, "тест", 5, 2, 1, "consumable", -1, 0)
    if not await get_item_by_name(fs.ROD_NAME):
        await add_item(fs.ROD_NAME, "тест", 50, 25, 1, "equipment", -1, 0)
    worms = await get_item_by_name(fs.WORMS_NAME)
    rod = await get_item_by_name(fs.ROD_NAME)
    config.FIRE_LAB_FISH_DELAY = (0, 0)

    class FakeMsg:
        chat = type("C", (), {"id": UID})()
        message_id = 42
        bot = None
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

    class FakeBot:
        async def send_message(self, chat_id, text, **kw):
            return type("M", (), {"message_id": 44, "chat": type("C", (), {"id": chat_id})()})()
        async def send_photo(self, chat_id, *a, **kw):
            return type("M", (), {"message_id": 45, "chat": type("C", (), {"id": chat_id})()})()
        async def delete_message(self, *a, **kw):
            return True

    FakeMsg.bot = FakeBot()

    class FakeCB:
        alerts = []
        def __init__(self, uid, data):
            self.from_user = type("U", (), {"id": uid})()
            self.data = data
            self.message = FakeMsg()
        async def answer(self, text=None, show_alert=False, **kw):
            if show_alert and text:
                FakeCB.alerts.append(text)
            return True

    sid = await create_fire_lab_session(UID, 50)

    print("\n1. Без удочки — заброс не делается")
    ap0 = int((await db.get_user(UID))['ap'])
    await add_inventory_item(UID, worms['id'], 3)
    await fe.fire_event_fishing_cb(FakeCB(UID, f"fireevent:fishing:{sid}"))
    check("без удочки ОД не списаны", int((await db.get_user(UID))['ap']) == ap0)
    check("без удочки alert о нужной удочке",
          any("удочка" in a.lower() for a in FakeCB.alerts))

    print("\n2. Без наживки — заброс разрешён (ОД тратятся, наживка не нужна)")
    await add_inventory_item(UID, rod['id'], 1)
    await update_user(UID, fishing_bait="none")
    FakeCB.alerts.clear()
    await fe.fire_event_fishing_cb(FakeCB(UID, f"fireevent:fishing:{sid}"))
    check("без наживки ОД списаны", int((await db.get_user(UID))['ap']) == ap0 - int(config.FISH_AP_COST))
    check("без наживки alert не показан", not FakeCB.alerts)

    print("\n3. С удочкой и наживкой — заброс списывает ОД и наживку")
    await update_user(UID, fishing_bait="worms")
    ap0 = int((await db.get_user(UID))['ap'])
    qty0 = int((await get_inventory_item(UID, worms['id']))['quantity'])
    await fe.fire_event_fishing_cb(FakeCB(UID, f"fireevent:fishing:{sid}"))
    ap1 = int((await db.get_user(UID))['ap'])
    check("ОД списаны на FISH_AP_COST", ap0 - ap1 == int(config.FISH_AP_COST))
    qty1 = int((await get_inventory_item(UID, worms['id']))['quantity'])
    check("наживка списана на 1", qty0 - qty1 == 1)
    session = await db.get_active_fire_lab_session(UID)
    check("обе попытки учтены в визите", int(session['fish_used'] or 0) == 2)

    print("\n4. Выбор наживки в колодце")
    await fe.fire_event_baitset_cb(FakeCB(UID, f"fireevent:baitset:{sid}:spider"))
    check("наживка сохранена из колодца", (await db.get_user(UID)).get('fishing_bait') == "spider")
    await fe.fire_event_baitset_cb(FakeCB(UID, f"fireevent:baitset:{sid}:auto"))
    check("«Авто» сохраняется пустой строкой", (await db.get_user(UID)).get('fishing_bait') == "")
    FakeCB.alerts.clear()
    await fe.fire_event_baitset_cb(FakeCB(UID, f"fireevent:baitset:{sid}:boom"))
    check("неизвестная наживка отклоняется", (await db.get_user(UID)).get('fishing_bait') == "")

    print(f"\nИТОГО: {passed} passed, {failed} failed")
    await close_db()
    return failed


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
