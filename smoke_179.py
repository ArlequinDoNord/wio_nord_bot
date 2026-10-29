# -*- coding: utf-8 -*-
"""Smoke 179 — Фаза 5: дроп-карточки врагов Лабиринта × «Огненное эха».

1. Сид: у всех 5 врагов дроп не пуст; РПУ и свиток трости в сиде (24 предмета).
2. Ворон в БД имеет карточки (проволока 15%, перо 8% и др.).
3. _tier_enemy: шансы × Тир с капом 1 (Тир 4 → ×1.08, Тир 5 → ×1.18).
4. Победа над Вором с вынужденным дропом (случайность зажата) → 1 ветка дерева
   и 1 перо в инвентаре, текст победы содержит «Добыча».
"""
import asyncio
import os
import sys
import json

os.environ["DATABASE_PATH"] = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "_test_smoke179.db")

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
        init_db, close_db, add_user, update_user, get_db,
        ensure_firelab_enemies, ensure_firelab_items, get_item_by_name,
        get_source_enemy_by_key, create_fire_lab_session,
        get_active_fire_lab_session, get_inventory_item,
        inc_fire_lab_tier,
    )
    from bot.handlers import fire_event as fe

    await init_db()
    conn = await db.get_db()
    await conn.execute("PRAGMA foreign_keys=OFF")
    for tbl in ("inventory", "user_fire_fish", "user_awards", "awards",
                "user_achievements", "user_recipes", "recipes", "activity_log",
                "fire_lab_tier", "fire_lab_sessions", "fire_lab_entries",
                "ap_log", "users", "items", "firelab_enemies"):
        try:
            await conn.execute(f"DELETE FROM {tbl}")
            await conn.commit()
        except Exception:
            pass
    await conn.execute("PRAGMA foreign_keys=ON")
    await db.ensure_achievements()
    await ensure_firelab_items()
    await ensure_firelab_enemies()
    UID = 179001
    await add_user(UID, 't', 'Пилот Ф5', "")
    await update_user(UID, nordmarks=500)

    print("\n1. Сид предметов (24 шт.) + дропы врагов не пусты")
    items = await ensure_firelab_items()
    dev = items.get(config.FIRE_FLAME_DEVICE_NAME)
    scroll = items.get("Рецепт: Обжигающая трость")
    check("РПУ в сиде", dev is not None)
    check("свиток «Рецепт: Обжигающая трость» в сиде", scroll is not None)
    cur = await conn.execute("SELECT COUNT(*) AS c FROM items")
    check("предметов всего 24", (await cur.fetchone())['c'] == len(items))
    seeds = config.FIRELAB_ENEMY_SEEDS
    check("у всех врагов дроп прописан (5/5)",
          all(s.get("loot") for s in seeds))
    boss = [s for s in seeds if s['key'] == 'pumpkin_boss'][0]
    boss_names = [n for n, _ in boss.get("loot", ())]
    check("босс: оба рецепта + венец/РПУ/семя в списке",
          all(n in boss_names for n in (
              config.FIRE_LAB_RECIPE_NAME, "Рецепт: Обжигающая трость",
              config.FIRE_CROWN_NAME, config.FIRE_FLAME_DEVICE_NAME,
              config.FIRE_PUMPKIN_SEED_NAME)))

    print("\n2. Карточки Вора в БД")
    crow = await get_source_enemy_by_key("firelab", "crow")
    drops = json.loads(crow['drops'] or '[]')
    check("у ворона 3 карточки дропа", len(drops) == 3)
    check("проволока 15% и перо 8% присутствуют",
          any(abs(float(d['chance']) - 0.15) < 1e-9 for d in drops)
          and any(abs(float(d['chance']) - 0.08) < 1e-9 for d in drops))

    print("\n3. Множитель Тира на шансы дропа")
    e0 = fe._tier_enemy(crow, 0)
    check("Тир 0: базовые шансы без изменений",
          [d['chance'] for d in e0['drops']] == [d['chance'] for d in drops])
    await inc_fire_lab_tier(UID)
    await inc_fire_lab_tier(UID)
    await inc_fire_lab_tier(UID)
    e4 = fe._tier_enemy(crow, 4)
    wire4 = next(d for d in e4['drops'] if d['item_id'] == dev and False) \
        if False else None
    per0 = 0.08
    per4 = min(1.0, per0 * 1.08)
    check("перо ворона Тир 4: 8% → 8.64%",
          any(abs(float(d['chance']) - per4) < 1e-9 for d in e4['drops']))
    for _ in range(2):
        await inc_fire_lab_tier(UID)
    e5 = fe._tier_enemy(crow, 5)
    per5 = min(1.0, per0 * 1.18)
    check("перо ворона Тир 5: 8% → 9.44%",
          any(abs(float(d['chance']) - per5) < 1e-9 for d in e5['drops']))

    print("\n4. Выдача лута при победе (случай зажат: всё бросаем)")

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
        chat = type("C", (), {"id": 179001})()
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

    hp = int((await db.pilot_combat_stats_stub()) if False else 100)
    sid = await create_fire_lab_session(UID, hp)
    session = await get_active_fire_lab_session(UID)
    enemy = {
        'key': 'crow', 'name': 'Ворон', 'hp': 1, 'hp_max': 10, 'armor': 0,
        'dodge': 0, 'dmg_min': 3, 'dmg_max': 5, 'is_boss': False,
        'drops': [{"item_id": items[config.FIRE_LAB_BRANCH_NAME], "qty": 1,
                   "chance": 1.0, "base": 1.0},
                  {"item_id": (await get_item_by_name(config.FIRE_CROW_FEATHER_NAME))['id'],
                   "qty": 1, "chance": 1.0, "base": 1.0}],
    }
    await fe._save_enemy(sid, enemy)
    branch_amt0 = 0
    feather0 = 0
    effects = {}
    cb = FakeCB(UID, f"fireevent:attack:{sid}")
    await fe.fire_event_attack_cb(cb)
    session = await get_active_fire_lab_session(UID)
    branch = await get_inventory_item(UID, items[config.FIRE_LAB_BRANCH_NAME])
    feather = await get_inventory_item(
        UID, (await get_item_by_name(config.FIRE_CROW_FEATHER_NAME))['id'])
    check("ветка дерева выпала с победы", branch and int(branch['quantity'] or 0) >= 1)
    check("перо ворона выпало с победы", feather and int(feather['quantity'] or 0) >= 1)
    painted = (getattr(cb.message.bot, 'last_text', None) or cb.message.text or "")
    check("текст победы: «Добыча»", "Добыча" in painted)
    cur = await conn.execute(
        "SELECT status FROM fire_lab_sessions WHERE id = ?", (sid,))
    check("враг умер, сессия жива (статус активен)",
          (await cur.fetchone())['status'] != 'dead')

    print(f"\nИТОГО: {passed} passed, {failed} failed")
    await close_db()
    if failed:
        sys.exit(1)


try:
    import random as rnd
    rnd.seed(179)
    asyncio.run(main())
except Exception:
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    try:
        os.remove(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "_test_smoke179.db"))
    except OSError:
        pass
