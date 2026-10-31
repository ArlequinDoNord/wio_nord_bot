# -*- coding: utf-8 -*-
"""Smoke 181 — Лабиринт и состояния, слоты зелий, подтверждение при полном HP.

1. Вход в Лабиринт (place «firelab»): «пьян» и «очень пьян» блокируют, без состояний — нет.
2. Расходники в бою Лабиринта: «несварение», «очень пьян», «оглушён» блокируют
   (battle_state_block_message), без состояний — нет.
3. «пьян» (без «очень») расходники не блокирует — как и раньше.
4. Купленный расходник (жареный сиг) ставится в слот зелий и виден в Лабиринте.
5. Полный HP: зелье не списывается сразу, сначала подтверждение «Да/Нет».
"""
import asyncio
import os
import sys

os.environ["DATABASE_PATH"] = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "_test_smoke181.db")

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
        init_db, close_db, get_db, add_user, update_user, get_item_by_name,
        add_inventory_item, get_inventory_item, set_equipment_slot,
        create_fire_lab_session,
    )
    from utils.states import (
        apply_state_to, clear_state_of, is_place_blocked, consumables_blocked,
        get_state_info,
    )
    from bot.handlers.dungeon import battle_state_block_message
    from bot.handlers import fire_event as fe

    await init_db()
    conn = await get_db()
    for tbl in ("fire_lab_sessions", "fire_lab_entries", "inventory", "user_states", "users"):
        try:
            await conn.execute(f"DELETE FROM {tbl}")
            await conn.commit()
        except Exception:
            pass
    UID = 181001
    await add_user(UID, 't', 'Пилот 181', "")
    await update_user(UID, nordmarks=1000)

    print("\n1. Вход в Лабиринт")
    check("без состояний вход открыт", await is_place_blocked(UID, "firelab") is False)
    await apply_state_to(UID, "пьян", caused_by=UID, reason="тест")
    check("«пьян» блокирует вход в Лабиринт", await is_place_blocked(UID, "firelab") is True)
    await clear_state_of(UID, caused_by=UID, reason="тест")
    await apply_state_to(UID, "очень пьян", caused_by=UID, reason="тест")
    check("«очень пьян» блокирует вход в Лабиринт",
          await is_place_blocked(UID, "firelab") is True)
    await clear_state_of(UID, caused_by=UID, reason="тест")

    print("\n2. Расходники в бою Лабиринта")
    check("без состояний расходники открыты", await battle_state_block_message(UID) is None)
    for st in ("несварение", "очень пьян", "оглушён"):
        await apply_state_to(UID, st, caused_by=UID, reason="тест")
        blk = await battle_state_block_message(UID)
        check(f"«{st}» блокирует расходники", bool(blk))
        await clear_state_of(UID, caused_by=UID, reason="тест")

    print("\n3. «пьян» расходники не блокирует")
    await apply_state_to(UID, "пьян", caused_by=UID, reason="тест")
    check("«пьян» — расходники открыты", await battle_state_block_message(UID) is None)
    info = await get_state_info(UID)
    check("consumables_blocked для «пьян» пусто", consumables_blocked(info['names']) == [])
    await clear_state_of(UID, caused_by=UID, reason="тест")

    print("\n4. Жареный сиг в слоте зелий Лабиринта")
    fish = await get_item_by_name("Жареный сиг")
    if not fish:
        await db.add_item("Жареный сиг", "тест", 60, 30, 1, "consumable", -1, 0,
                          heal=15)
        fish = await get_item_by_name("Жареный сиг")
    await add_inventory_item(UID, fish['id'], 2)
    await set_equipment_slot(UID, "potion1", fish['id'])
    labels = await fe._potions_labels(UID)
    check("жареный сиг виден в слотах зелий Лабиринта",
          any(nm == "Жареный сиг" for _, nm, _ in labels))

    print("\n5. Полный HP: подтверждение перед зельем")
    sid = await create_fire_lab_session(UID, 50)
    await conn.execute("UPDATE fire_lab_sessions SET hp = hp_max WHERE id = ?", (sid,))
    await conn.commit()
    await fe._save_enemy(sid, {'key': 'scarecrow', 'name': 'Пугало', 'hp': 40, 'hp_max': 40,
                               'armor': 1, 'dodge': 0, 'dmg_min': 3, 'dmg_max': 5,
                               'is_boss': False})

    class FakeBot:
        async def send_message(self, chat_id, text, **kw):
            return type("M", (), {"message_id": 43,
                                  "chat": type("C", (), {"id": chat_id})()})()
        async def send_photo(self, chat_id, *a, **kw):
            return type("M", (), {"message_id": 44,
                                  "chat": type("C", (), {"id": chat_id})()})()
        async def delete_message(self, *a, **kw):
            return True
        async def edit_message_reply_markup(self, *a, **kw):
            return True

    class FakeMsg:
        sent = []
        chat = type("C", (), {"id": 181001})()
        message_id = 42
        bot = FakeBot()
        async def answer(self, text=None, reply_markup=None, **kw):
            FakeMsg.sent.append((text, reply_markup))
            return type("M", (), {"message_id": 43,
                                  "chat": type("C", (), {"id": 181001})()})()
        async def edit_text(self, text=None, reply_markup=None, **kw):
            return True
        async def edit_caption(self, *a, **kw):
            return True
        async def edit_media(self, *a, **kw):
            return True
        async def delete(self):
            return True

    class FakeCB:
        def __init__(self, uid, data):
            self.from_user = type("U", (), {"id": uid})()
            self.data = data
            self.message = FakeMsg()
        async def answer(self, *a, **kw):
            return True

    before = int((await get_inventory_item(UID, fish['id']))['quantity'])
    await fe.fire_event_potion_cb(FakeCB(UID, f"fireevent:potion:{sid}:potion1"))
    after = int((await get_inventory_item(UID, fish['id']))['quantity'])
    check("при полном HP зелье не списано сразу", after == before)
    kb = FakeMsg.sent[-1][1] if FakeMsg.sent else None
    cbs = [b.callback_data for row in (kb.inline_keyboard if kb else []) for b in row]
    check("появилось подтверждение «Да»",
          any(c == f"fireevent:potionok:{sid}:potion1" for c in cbs))
    await fe.fire_event_potion_ok_cb(FakeCB(UID, f"fireevent:potionok:{sid}:potion1"))
    final = int((await get_inventory_item(UID, fish['id']))['quantity'])
    check("после «Да» зелье списано (на 1)", final == before - 1)

    print("\n6. Праздничная картинка локации")
    orig_visible = db.fire_event_visible
    loc_stub = {"fire_photo": "FIRE_FILE_ID", "season_photos": None, "photo_day": "NORMAL_FILE_ID"}
    db.fire_event_visible = lambda: True
    check("праздник идёт → праздничная картинка", db.location_photo_for_tod(loc_stub, "summer", "day") == "FIRE_FILE_ID")
    db.fire_event_visible = lambda: False
    check("праздника нет → обычная картинка", db.location_photo_for_tod(loc_stub, "summer", "day") == "NORMAL_FILE_ID")
    db.fire_event_visible = orig_visible
    check("вход в лабиринт 32 НМ", config.FIRE_EVENT_LAB_FEE == 32)

    print("\n7. Праздничная картинка общего вида города")
    from bot.handlers import start as st
    await db.set_city_fire_photo("CITY_FIRE_FID")
    check("сохранено", await db.get_city_fire_photo() == "CITY_FIRE_FID")
    db.fire_event_visible = lambda: True
    check("праздник идёт → картинка города праздничная", await st._city_photo() == "CITY_FIRE_FID")
    db.fire_event_visible = lambda: False
    pic = await st._city_photo()
    check("праздника нет → обычная картинка Аркхольма", not isinstance(pic, str))
    db.fire_event_visible = orig_visible
    await db.set_city_fire_photo(None)
    check("очищено", await db.get_city_fire_photo() is None)

    print("\n8. Миграция колонки fire_lab_sessions.last_active_at на старой таблице")
    try:
        await conn.execute("ALTER TABLE fire_lab_sessions DROP COLUMN last_active_at")
        await conn.commit()
        dropped = True
    except Exception:
        dropped = False
    if dropped:
        await init_db()
        cur8 = await (await get_db()).execute("PRAGMA table_info(fire_lab_sessions)")
        cols = [r['name'] for r in await cur8.fetchall()]
        check("колонка возвращается миграцией", "last_active_at" in cols)
    else:
        check("SQLite без DROP COLUMN — пропуск", True)

    print(f"\nИТОГО: {passed} passed, {failed} failed")
    await close_db()
    return failed


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
