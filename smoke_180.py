# -*- coding: utf-8 -*-
"""Smoke 180 — турист у входа в Лабиринт + квота Древа за заход.

1. Турист: «Войти» показывает вход (не пускает), выдаёт «Леденец языков
   пламени» ×1 бесплатно — ровно один раз (повтор — «уже получал»).
2. Пилот: платный вход без сувенира (квота не тратится).
3. Квота Древа: tree_visits=1 → _roll_room больше не возвращает 'tree'.
"""
import asyncio
import os
import sys

os.environ["DATABASE_PATH"] = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "_test_smoke180.db")

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
        init_db, close_db, add_user, update_user, get_db, get_item_by_name,
        get_inventory_item, grant_fire_souvenir, grant_status,
        ensure_firelab_items, get_active_fire_lab_session,
        create_fire_lab_session, end_fire_lab_session, user_is_tourist,
    )
    from bot.handlers import fire_event as fe

    await init_db()
    conn = await db.get_db()
    await conn.execute("PRAGMA foreign_keys=OFF")
    for tbl in ("inventory", "user_fire_fish", "user_awards", "awards",
                "user_achievements", "user_recipes", "recipes", "activity_log",
                "fire_souvenirs", "fire_lab_sessions", "fire_lab_entries",
                "user_statuses", "statuses", "users", "items"):
        try:
            await conn.execute(f"DELETE FROM {tbl}")
            await conn.commit()
        except Exception:
            pass
    await conn.execute("PRAGMA foreign_keys=ON")
    await db.ensure_base_statuses()
    await db.ensure_achievements()
    await ensure_firelab_items()

    TOURIST = 180001
    PILOT = 180002
    await add_user(TOURIST, 'tr', 'Туристка', "")
    await add_user(PILOT, 'p', 'Пилот', "")
    await update_user(PILOT, nordmarks=500)
    # статус «Турист» (access_tag tourist) — как выдаёт регистрация
    cur = await conn.execute("SELECT id FROM statuses WHERE access_tag = 'tourist'")
    srow = await cur.fetchone()
    check("статус «Турист» существует", srow is not None)
    if srow:
        await grant_status(TOURIST, srow['id'], 0)
    check("tourist действительно турист", await user_is_tourist(TOURIST))
    check("pilot не турист", not await user_is_tourist(PILOT))

    print("\n1. Сувенир туристу: разово")
    candy = await get_item_by_name(
        getattr(config, "FIRE_LAB_CANDY_NAME", "Леденец языков пламени"))
    check("леденец в сиде предметов", candy is not None)
    fresh1 = await grant_fire_souvenir(TOURIST)
    check("первый визит: сувенир выдан", fresh1 is True)
    if candy:
        await db.add_inventory_item(TOURIST, candy['id'], 1)
    fresh2 = await grant_fire_souvenir(TOURIST)
    check("второй визит: уже не выдаётся", fresh2 is False)
    inv = await get_inventory_item(TOURIST, candy['id'])
    check("леденец в инвентаре туриста (1 шт.)",
          inv and int(inv['quantity'] or 0) == 1)

    print("\n2. Хендлер входа: турист — экран с сувениром, не вход")

    class FakeBot:
        last_text = None
        last_kb = None
        async def send_message(self, chat_id, text, **kw):
            FakeBot.last_text = text
            FakeBot.last_kb = kw.get('reply_markup')
            return type("M", (), {"message_id": 43,
                                  "chat": type("C", (), {"id": chat_id})()})()
        async def send_photo(self, *a, **kw):
            FakeBot.last_text = kw.get('caption') or (a[1] if len(a) > 1 else "")
            FakeBot.last_kb = kw.get('reply_markup')
            return type("M", (), {"message_id": 44,
                                  "chat": type("C", (), {"id": (a[0] or 0)})()})()
        async def delete_message(self, *a, **kw):
            return True
        async def edit_message_reply_markup(self, **kw):
            return True

    class FakeMsg:
        text = None
        kb = None
        chat = type("C", (), {"id": 180001})()
        message_id = 42
        bot = FakeBot()
        async def edit_text(self, t=None, reply_markup=None, **kw):
            self.text = t
            self.kb = reply_markup
            return True
        async def answer(self, *a, **kw):
            if a and isinstance(a[0], str):
                self.text = a[0]
            if kw.get('reply_markup'):
                self.kb = kw['reply_markup']
            return True

    class FakeCB:
        def __init__(self, uid, data):
            self.from_user = type("U", (), {"id": uid})()
            self.data = data
            self.message = FakeMsg()
            self.bot = FakeBot()
        async def answer(self, *a, **kw):
            return True

    # новый турист (без сувенира) смотрит вход
    TOURIST2 = 180003
    await add_user(TOURIST2, 'tr2', 'Турист Два', "")
    if srow:
        await grant_status(TOURIST2, srow['id'], 0)
    cb = FakeCB(TOURIST2, "fireevent:enter")
    await fe.fire_event_enter_cb(cb, None)
    txt = (FakeBot.last_text or "") + (cb.message.text or "")
    check("экран входа: текст праздника", "Пламенного Круговорота" in txt)
    check("туристу не пускают внутрь", "только для граждан Нордхайма и легионеров" in txt)
    check("сувенир в тексте", "Леденец" in txt)
    inv2 = await get_inventory_item(TOURIST2, candy['id'])
    check("и в инвентаре у второго туриста", inv2 and int(inv2['quantity'] or 0) == 1)

    print("\n3. Пилот: платный вход, сувенир не трогается")
    cb2 = FakeCB(PILOT, "fireevent:enter")
    await fe.fire_event_enter_cb(cb2, None)
    session = await get_active_fire_lab_session(PILOT)
    check("у пилота активная сессия лабиринта", session is not None)
    if session:
        await end_fire_lab_session(session['id'], 'left')
    check("пилоту не выдавался сувенир",
          await grant_fire_souvenir(PILOT) is True)  # сначала ни разу

    print("\n4. Квота Древа: за один заход — только один раз")
    sid = await create_fire_lab_session(PILOT, 100)
    session_stub = {
        'steps': 0, 'tree_visits': 1, 'well_visits': 0, 'chest_visits': 0,
        'boss_encounters': 0, 'blessing': 0, 'hp': 100, 'hp_max': 100,
    }
    got_tree = False
    history = []
    for i in range(300):
        history.append("L")
        res = await fe._roll_room(PILOT, session_stub, "L", history)
        if res == "tree":
            got_tree = True
            break
    check("после одного посещения Древо не бросается", not got_tree)
    session_stub['tree_visits'] = 0
    seen = set()
    for i in range(400):
        seen.add(await fe._roll_room(PILOT, session_stub, "L", history))
    check("с нулевым счётчиком Древо снова доступно", "tree" in seen)

    print(f"\nИТОГО: {passed} passed, {failed} failed")
    await close_db()
    if failed:
        sys.exit(1)


try:
    import random as rnd
    rnd.seed(180)
    asyncio.run(main())
except Exception:
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    try:
        os.remove(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "_test_smoke180.db"))
    except OSError:
        pass
