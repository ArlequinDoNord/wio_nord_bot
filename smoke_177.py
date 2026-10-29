# -*- coding: utf-8 -*-
"""Smoke 177 — Ф4б: Лампа Круговорота в личном жильё (генератор, вне праздника).

1. Лампа — мебель (FURNITURE_BY_EXPANSION mapping существует).
2. Установка в слот → has_lantern_installed = True; таймер янтаря стартует.
3. 🧘 Медитация: раз в сутки +20 ОД (повтор в тот же день — 0, не сливается
   с душевым кулдауном).
4. 🪵 Пламя Памяти: задолжавший таймер — янтарь в инвентарь (+1), таймер
   сдвинулся на 7 суток вперёд; до срока — 0.
5. Экран комнаты Лампы рисуется через FakeCB (медитация кнопка/текст).
6. get_lantern_owners(): пилот с Лампой в списке.
"""
import asyncio
import os
import sys
import time

os.environ["DATABASE_PATH"] = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "_test_smoke177.db")

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
        add_inventory_item, ensure_firelab_items, set_housing_slot,
        get_housing_slots, has_lantern_installed, can_meditate_lantern,
        use_lantern_meditation, set_lantern_amber_next, get_lantern_amber_at,
        grant_lantern_amber_if_due, get_inventory_item, get_lantern_owners,
        get_user, can_use_shower, get_player_housing,
    )
    from bot.handlers import housing as hh

    await init_db()
    conn = await db.get_db()
    # Чистим под FK, чтобы не упираться в связи (старые проги могли оставить хвосты).
    await conn.execute("PRAGMA foreign_keys=OFF")
    for tbl in ("inventory", "user_fire_fish", "user_awards", "awards",
                "user_achievements", "user_recipes", "recipes",
                "activity_log", "housing_slots", "player_housing",
                "fire_lab_sessions", "fire_lab_entries", "ap_log", "users", "items"):
        try:
            await conn.execute(f"DELETE FROM {tbl}")
            await conn.commit()
        except Exception:
            pass
    await conn.execute("PRAGMA foreign_keys=ON")
    await db.ensure_achievements()
    UID = 177001
    await add_user(UID, 't', 'Пилот Лампы', "")
    await update_user(UID, nordmarks=1000, ap=10, ap_max=100)
    items = await ensure_firelab_items()

    print("\n1. Лампа — мебель для жилья")
    from bot.handlers.housing import FURNITURE_BY_EXPANSION
    check("mapping ('lantern', 1) → «Лампа Круговорота»",
          FURNITURE_BY_EXPANSION.get(("lantern", 1)) == config.FIRE_LANTERN_NAME)
    lamp = await get_item_by_name(config.FIRE_LANTERN_NAME)
    check(" item лампы: category furniture",
          lamp and lamp['category'] == 'furniture')

    print("\n2. Установка в слот жилья")
    await add_inventory_item(UID, lamp['id'], 1)
    await get_player_housing(UID)          # создаёт муниципальную квартиру
    await set_housing_slot(UID, 0, "lantern", 1)
    check("Лампа установлена (has_lantern_installed)",
          await has_lantern_installed(UID))
    ts0 = await get_lantern_amber_at(UID)
    check("таймер янтаря ещё не запущен без хука", ts0 is None)

    print("\n3. Медитация: раз в сутки, не мешает душевной")
    gained = await use_lantern_meditation(UID)
    check(f"первая медитация +{gained} ОД", gained == 20)
    user = await get_user(UID)
    check("ОД реально вырос", int(user['ap'] or 0) >= 30)
    check("повторная медитация сегодня — 0",
          await use_lantern_meditation(UID) == 0)
    check("душевая независима (can_use_shower True после медитации)",
          await can_use_shower(UID))

    print("\n4. Пламя Памяти: генерация по таймеру")
    # чуть не дошедший до второго янтаря: 7 суток − 30 сек назад → ровно 1 шт.
    await set_lantern_amber_next(UID, time.time() - (7 * 86400 - 30))
    amber_name = config.FIRE_AMBER_NAME
    amber = await get_item_by_name(amber_name)
    check("предмет «Пламя Памяти» в сиде", amber is not None)
    granted = await grant_lantern_amber_if_due(UID)
    check("янтарь начислен (+1 шт.)", granted == 1)
    inv = await get_inventory_item(UID, amber['id'])
    check("янтарь в инвентаре", inv and int(inv['quantity'] or 0) >= 1)
    ts_next = await get_lantern_amber_at(UID)
    days_left = (float(ts_next) - time.time()) / 86400
    check(f"таймер сдвинут на следующий период (остаток {days_left:.3f} сут.)",
          0 <= days_left < 0.02)
    check("до срока — больше не выдаёт",
          await grant_lantern_amber_if_due(UID) == 0)
    check("не выдаёт второй янтарь тем же днём (совпадает таймер)",
          (await get_inventory_item(UID, amber['id']))['quantity'] == 1)
    # контроль константы: раз в 7 суток
    check("период янтаря = 7 суток (FIRE_LANTERN_AMBER_DAYS)",
          int(getattr(config, "FIRE_LANTERN_AMBER_DAYS", 5)) == 7)

    print("\n5. Экран комнаты Лампы (FakeCB)")

    class FakeMsg:
        text = None
        kb = None
        chat = type("C", (), {"id": 177001})()
        message_id = 42

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

    class FakeBot:
        last_text = None
        last_kb = None

        async def send_message(self, chat_id, text, **kw):
            FakeBot.last_text = text
            FakeBot.last_kb = kw.get("reply_markup")
            return type("M", (), {"message_id": 43,
                                  "chat": type("C", (), {"id": chat_id})()})()

        async def send_photo(self, *a, **kw):
            FakeBot.last_text = kw.get("caption") or (a[1] if len(a) > 1 else "")
            FakeBot.last_kb = kw.get("reply_markup")
            return type("M", (), {"message_id": 44,
                                  "chat": type("C", (), {"id": (a[0] or 0)})()})()

        async def edit_message_reply_markup(self, **kw):
            return True

    class FakeCB:
        def __init__(self, uid, data):
            self.from_user = type("U", (), {"id": uid})()
            self.data = data
            self.message = FakeMsg()
            self.bot = FakeBot()
        async def answer(self, *a, **kw):
            return True

    slots = await get_housing_slots(UID)
    slot = slots.get(0)
    ht = (await get_player_housing(UID))["housing_type"]
    # сброс: чтобы кнопка медитации была активна (ранее медитировали в тесте)
    await db.update_user(UID, lantern_medit_day=None)
    cb = FakeCB(UID, "housing:room:0")
    await hh._room_lantern(cb, UID, 0, slot, ht)
    txt = (FakeBot.last_text or "") + (cb.message.text or "")
    check("заголовок «Лампа Круговорота»", "Лампа Круговорота" in txt)
    check("упоминание медитации", "медитация" in txt.lower())
    check("янтарь с датой", "Пламя Памяти" in txt)
    kb_txt = " ".join(b.text for row in (FakeBot.last_kb or cb.message.kb).inline_keyboard
                      for b in row) if (FakeBot.last_kb or cb.message.kb) else ""
    check("кнопка медитации", "Медитировать" in kb_txt)

    print("\n6. Список владельцев Лампы")
    owners = await get_lantern_owners()
    check("пилот с Лампой в списке владельцев", UID in owners)

    print(f"\nИТОГО: {passed} passed, {failed} failed")
    await close_db()
    if failed:
        sys.exit(1)


try:
    asyncio.run(main())
except Exception:
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    try:
        os.remove(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "_test_smoke177.db"))
    except OSError:
        pass
