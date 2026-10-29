# -*- coding: utf-8 -*-
"""Smoke 175 — Фаза 3: особые комнаты (Колодец/Древо/Сундук), рыбалка, тиры.

1. ensure_firelab_items: Ф3-предметы (8) + сид Ф4 расширил таблицу; рецепт
   «Тыквенный пирог» с v0.41.2 доступен (состав в менеджере рецептов).
2. Колонки визитов: bump well/tree/chest; вход в Колодец сбрасывает fish_used.
3. Fishing: лимит 6 попыток/визит; поклёвки/промахи по сидиру; UNIQUE отметок
   видов; мини-ачивка «Рыбак древних» (уровень 1, threshold 3).
4. Древо: blessing ставится, экран содержит бонус.
5. Сундук: лут по сидеру — НМ или предмет (таблица валидна).
6. Финиш 25 комнат: статус finished, Тир +1, текст «Огненное эхо усилилось».
"""
import asyncio
import os
import sys

os.environ["DATABASE_PATH"] = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "_test_smoke175.db")

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
        init_db, close_db, add_user, update_user, get_active_fire_lab_session,
        create_fire_lab_session, get_db, get_user,
        bump_fire_lab_room_visit, set_fire_lab_blessing,
        get_fire_lab_fish_used, inc_fire_lab_fish_used,
        mark_fire_fish_caught, count_fire_fish_kinds,
        ensure_firelab_items, get_item_by_name, set_achievement_progress,
        get_achievement_level, end_fire_lab_session, get_fire_lab_tier,
    )
    from bot.handlers import fire_event as fe

    await init_db()
    conn = await db.get_db()
    for tbl in ("fire_lab_tier", "fire_lab_sessions", "fire_lab_entries",
                "users", "firelab_enemies", "user_fire_fish", "items",
                "recipes", "user_achievements", "inventory", "awards"):
        try:
            await conn.execute(f"DELETE FROM {tbl}")
        except Exception:
            pass
    await conn.commit()
    UID = 175001
    await add_user(UID, 't', 'Пилот Ф3', "")
    await update_user(UID, nordmarks=1000)

    print("\n1. Сид предметов Круговорота (Ф3 8 шт + Ф4 расширил сид)")
    items = await ensure_firelab_items()
    check("Ф3-предметы на месте (8 шт.)",
          all(k in items for k in (
              config.FIRE_LAB_FISH_OSETR_NAME, config.FIRE_LAB_FISH_SOUL_NAME,
              config.FIRE_LAB_FISH_CARP_NAME, config.FIRE_LAB_PIE_NAME,
              config.FIRE_LAB_CANDY_NAME, config.FIRE_LAB_HAY_NAME,
              config.FIRE_LAB_BRANCH_NAME, config.FIRE_LAB_RECIPE_NAME)))
    cur = await conn.execute(
        "SELECT COUNT(*) AS c FROM items WHERE name IN ("
        + ",".join("?" * len(items)) + ")",
        tuple(items))
    check("дублей предметов нет (строк = ключей)",
          (await cur.fetchone())['c'] == len(items))
    cur = await conn.execute(
        "SELECT is_available FROM recipes WHERE name = ?", ("Тыквенный пирог",))
    row = await cur.fetchone()
    check("рецепт «Тыквенный пирог» есть (v0.41.2: доступен, состав — ТФ4)",
          row and int(row['is_available'] or 0) == 1)
    items2 = await ensure_firelab_items()
    check("повтор ensure — идемпотентно (те же ключи)", set(items2) == set(items))

    print("\n2. Попробки рыбалки и отметки видов")
    sid = await create_fire_lab_session(UID, 50)
    used0 = await get_fire_lab_fish_used(sid)
    check("рыбалка начально 0 попыток", used0 == 0)
    for i in range(6):
        used = await inc_fire_lab_fish_used(sid)
        check(f"попытка {i + 1}/6 зачлась", used == i + 1)
    check("7-я попытка не зачлась (лимит)", await inc_fire_lab_fish_used(sid) == 0)

    fish_items = []
    for fname in (config.FIRE_LAB_FISH_OSETR_NAME, config.FIRE_LAB_FISH_SOUL_NAME,
                  config.FIRE_LAB_FISH_CARP_NAME):
        fish_items.append((await get_item_by_name(fname))['id'])
    check("осетр новый вид", await mark_fire_fish_caught(UID, fish_items[0]))
    check("осетр повторно — не new", not await mark_fire_fish_caught(UID, fish_items[0]))
    check("душа новый вид", await mark_fire_fish_caught(UID, fish_items[1]))
    check("видов 2", await count_fire_fish_kinds(UID) == 2)

    print("\n3. Мини-ачивка «Рыбак древних» (все 3 рыбы)")
    await db.ensure_achievements()
    await mark_fire_fish_caught(UID, fish_items[2])
    kinds = await count_fire_fish_kinds(UID)
    check("видов 3", kinds == 3)
    lvl, _n, prev = await set_achievement_progress(
        UID, getattr(config, "FIRE_FISHER_ACH_KEY", "fire_fisher"), kinds)
    check("уровень 1 достигнут", lvl == 1)
    check("название уровня = «Рыбак древних»", _n == "Рыбак древних")
    check("уровень ачивки в БД = 1",
          await get_achievement_level(UID, "fire_fisher") == 1)
    cur = await conn.execute(
        "SELECT reward_nm FROM awards WHERE name = ?", ("Рыбак древних",))
    row = await cur.fetchone()
    check("награда seeded с премией 150", row and int(row['reward_nm'] or 0) == 150)

    print("\n4. Колодец: полное лечение + сброс попыток")

    class FakeMsg:
        text = None
        kb = None
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
        async def answer(self, *a, **kw):
            return True

    sid2 = await create_fire_lab_session(UID, 50)
    conn = await db.get_db()
    await conn.execute("UPDATE fire_lab_sessions SET hp = 7 WHERE id = ?", (sid2,))
    await conn.commit()
    # выработать попытки до лимита, потом снова войти в Колодец
    for _ in range(6):
        await inc_fire_lab_fish_used(sid2)
    cb = FakeCB(UID, f"fireevent:cont:{sid2}")
    session = await get_active_fire_lab_session(UID)
    await fe._enter_well(cb, session, sid2)
    session = await get_active_fire_lab_session(UID)
    check("колодец полечил до hp_max", int(session['hp']) == int(session['hp_max']))
    check("колодец сбросил попытки рыбалки",
          await get_fire_lab_fish_used(sid2) == 0)
    check("визит в колодец засчитан", int(session['well_visits'] or 0) == 1)
    check("экран колодца показан", "КОЛОДЕЦ" in (cb.message.text or ""))

    print("\n5. Древо Огня: благословение на сессию")
    cb_tree = FakeCB(UID, f"fireevent:cont:{sid2}")
    session = await get_active_fire_lab_session(UID)
    await fe._enter_tree(cb_tree, session, sid2)
    session = await get_active_fire_lab_session(UID)
    check("blessing = 1 после Древа", int(session['blessing'] or 0) == 1)
    check("визит в Древо засчитан", int(session['tree_visits'] or 0) == 1)
    check("экран Древа: +15% урона", "+15%" in (cb_tree.message.text or ""))
    # Древо второй раз blessing не ломает (квота 1 уже посчитана)
    await fe._enter_tree(FakeCB(UID, f"fireevent:cont:{sid2}"),
                         session, sid2)
    session = await get_active_fire_lab_session(UID)
    check("blessing остаётся 1", int(session['blessing'] or 0) == 1)
    check("визитов в Древо 2 (квота уже учтена броском)",
          int(session['tree_visits'] or 0) == 2)

    print("\n6. Сундук: лут по сиду")
    random_seed_values = [0.0, 0.99]
    saved_choices = __import__("random").choices

    def scripted_choices(vals, weights=None, **kw):
        v = vals[0] if len(vals) == 1 else vals
        arg = vals if isinstance(vals, list) else v
        # прокидываем остальное как есть; сами значения подставим ниже
        return [vals[0]]

    import random as rnd
    def fake_choices(pop, weights=None, k=1):
        return [scripted_loot_key]
    scripted_loot_key = "nm"
    rnd.choices = fake_choices
    cb_chest = FakeCB(UID, f"fireevent:cont:{sid2}")
    session = await get_active_fire_lab_session(UID)
    before_nm = int((await get_user(UID))['nordmarks'])
    await fe._enter_chest(cb_chest, session, sid2)
    session = await get_active_fire_lab_session(UID)
    after_nm = int((await get_user(UID))['nordmarks'])
    check("нм-дроп зачислен (>= 30, <= 60)",
          30 <= after_nm - before_nm <= 60)
    check("визит в сундук засчитан", int(session['chest_visits'] or 0) == 1)
    scripted_loot_key = config.FIRE_LAB_CANDY_NAME
    cb_chest2 = FakeCB(UID, f"fireevent:cont:{sid2}")
    await fe._enter_chest(cb_chest2, session, sid2)
    conn2 = await db.get_db()
    cur = await conn2.execute(
        "SELECT quantity FROM inventory WHERE item_id = ? AND user_id = ?",
        (items.get(config.FIRE_LAB_CANDY_NAME) or 0, UID))
    row = await cur.fetchone()
    check("леденец из сундука в инвентаре", row and int(row['quantity'] or 0) >= 1)
    check("экран сундука: «СУНДУК СОКРОВИЩ»",
          "СУНДУК СОКРОВИЩ" in (cb_chest2.message.text or ""))
    rnd.choices = saved_choices

    print("\n7. Финиш 25 комнат: статус finished + Тир +1")
    await end_fire_lab_session(sid2, 'left')
    sid3 = await create_fire_lab_session(UID, 50)
    conn = await db.get_db()
    await conn.execute("UPDATE fire_lab_sessions SET steps = 24 WHERE id = ?", (sid3,))
    await conn.commit()
    tier_before = await get_fire_lab_tier(UID)
    step_cb = FakeCB(UID, f"fireevent:step:{sid3}:L")
    await fe.fire_event_step_cb(step_cb)
    cur = await conn.execute(
        "SELECT status FROM fire_lab_sessions WHERE id = ?", (sid3,))
    check("сессия закрылась finished", (await cur.fetchone())['status'] == 'finished')
    check("Тир вырос на 1",
          await get_fire_lab_tier(UID) == tier_before + 1)
    check("текст: «Огненное эхо усил илось» в экране финала",
          "Огненное эхо усилилось" in (step_cb.message.text or ""))

    print(f"\nИТОГО: {passed} passed, {failed} failed")
    await close_db()
    if failed:
        sys.exit(1)


try:
    import random as rnd
    rnd.seed(175)
    asyncio.run(main())
except Exception:
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    try:
        os.remove(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "_test_smoke175.db"))
    except OSError:
        pass
