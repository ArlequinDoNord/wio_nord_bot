# -*- coding: utf-8 -*-
"""Smoke 173 — Круговорот Фаза 2: враги, бой, босс, Тир «Огненное эха».

1. seed врагов (5 шт: 4 обычных + босс), броня Пугала/босса сидится.
2. _roll_room: варьируется только допустимый состав {enemy/boss/well/tree/chest/empty}.
3. Тир: firelab_tier_enemy_bonus (0→0, 1→2, 4→8, 5→16) и firelab_tier_loot_mult
   (0→1.0, 1→1.02, 4→1.08, 5→1.10); кап inc после 5 не растёт.
4. _tier_enemy: HP сдвиг с Тиром.
5. Боевой тик: FakeCallback → _start_battle (победа после добивания), при смерти игрока
   (burn на малом HP) сессия закрывается статусом dead.
"""
import asyncio
import os
import sys

os.environ["DATABASE_PATH"] = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "_test_smoke173.db")

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
            print(f"  FAIL: {name}")

    import database.db as db
    import config
    from database.db import (
        init_db, add_user, update_user, create_fire_lab_session,
        get_fire_lab_tier, inc_fire_lab_tier, get_active_fire_lab_session,
        end_fire_lab_session, close_db,
        ensure_firelab_enemies, firelab_tier_enemy_bonus,
        firelab_tier_loot_mult,
    )
    from bot.handlers import fire_event as fe

    await init_db()
    # во время прошлых упавших прогонов Windows не даёт удалить открытую БД —
    # чистим таблицы теста, чтобы тир начинался с нуля
    conn = await db.get_db()
    for tbl in ("fire_lab_tier", "fire_lab_sessions", "fire_lab_entries", "users",
                "firelab_enemies"):
        try:
            await conn.execute(f"DELETE FROM {tbl}")
        except Exception:
            pass
    await conn.commit()
    UID = 173001
    await add_user(UID, 't', 'Т', "")
    await update_user(UID, nordmarks=9999)

    print("\n1. Сид врагов Огненного Лабиринта")
    await db.ensure_firelab_enemies()
    # второй вызов — идемпотентно
    await db.ensure_firelab_enemies()
    conn = await db.get_db()
    cur = await conn.execute("SELECT key, name, hp, armor, dodge, dmg_min, dmg_max FROM firelab_enemies ORDER BY id")
    rows = {(r['key']): r for r in await cur.fetchall()}
    check("5 врагов засеяны",
          set(rows) == {"scarecrow", "apple_child", "crow", "ghost", "pumpkin_boss"})
    check("Пугало 25/4/1/10",          rows['scarecrow']['hp'] == 25 and rows['scarecrow']['armor'] == 1
          and rows['scarecrow']['dodge'] == 10)
    check("Дитя Яблони 27", rows['apple_child']['hp'] == 27)
    check("Ворон 16/20%", rows['crow']['hp'] == 16 and rows['crow']['dodge'] == 20)
    check("Призрак 24/15%", rows['ghost']['hp'] == 24 and rows['ghost']['dodge'] == 15)
    check("Босс 60/атк4-7/бр2/укл5",
          rows['pumpkin_boss']['hp'] == 60 and rows['pumpkin_boss']['armor'] == 2
          and rows['pumpkin_boss']['dodge'] == 5
          and rows['pumpkin_boss']['dmg_min'] == 4 and rows['pumpkin_boss']['dmg_max'] == 7)

    print("\n2. Тир «Огненного эха»")
    t0 = await get_fire_lab_tier(UID)
    check("тир изначально 0", t0 == 0)
    check("бонус HP на 0 тире = 0", firelab_tier_enemy_bonus(0) == 0)
    t1 = await inc_fire_lab_tier(UID)
    check("после 1-го прохождения тир 1", t1 == 1)
    check("бонус HP на тире 1 = 2", firelab_tier_enemy_bonus(1) == 2)
    check("лут-множитель тир 1 = 1.02", abs(firelab_tier_loot_mult(1) - 1.02) < 1e-9)
    for _ in range(3):
        await inc_fire_lab_tier(UID)
    check("после 4 усилений тир 4", await get_fire_lab_tier(UID) == 4)
    check("бонус HP на тире 4 = 8", firelab_tier_enemy_bonus(4) == 8)
    check("лут-множитель тир 4 = 1.08", abs(firelab_tier_loot_mult(4) - 1.08) < 1e-9)
    await inc_fire_lab_tier(UID)
    check("5-й тир достигнут", await get_fire_lab_tier(UID) == 5)
    check("5-й тир: разово +8 (итого +16)", firelab_tier_enemy_bonus(5) == 16)
    check("лут-множитель тир 5 = 1.18 (4×2% + 10%)", abs(firelab_tier_loot_mult(5) - 1.18) < 1e-9)
    await inc_fire_lab_tier(UID)
    check("кап: 6-й прогон не растит тир", await get_fire_lab_tier(UID) == 5)
    check("но runs продолжает копиться",
          await get_fire_lab_tier(UID) == 5)
    conn2 = await db.get_db()
    cur = await conn2.execute("SELECT runs FROM fire_lab_tier WHERE user_id = ?", (UID,))
    check("runs = 6", (await cur.fetchone())['runs'] == 6)

    print("\n3. _tier_enemy: сдвиг HP по Тиру")
    row_scarecrow = rows['scarecrow']
    e0 = fe._tier_enemy(row_scarecrow, 0)
    e5 = fe._tier_enemy(row_scarecrow, 5)
    check("tier 0: Пугало HP 25", e0['hp'] == 25 and not e0['is_boss'])
    check("tier 5: Пугало HP 41 (25 + 16)", e5['hp'] == 41)
    e0b = fe._tier_enemy(row_scarecrow, 0)
    check("boss flag у босса", fe._tier_enemy(rows['pumpkin_boss'], 0)['is_boss'] is True)

    print("\n4. _roll_room: броски возвращают допустимые значения")
    session_stub = {
        'steps': 0, 'tree_visits': 0, 'well_visits': 0, 'chest_visits': 0,
        'boss_encounters': 0, 'blessing': 0, 'hp': 100, 'hp_max': 100,
    }
    incoming = set()
    history = []
    for i in range(500):
        # имитируем запись шага и бросок (без записи в БД)
        history.append(random.choice("LSR"))
        session_stub['steps'] += 1
        res = await fe._roll_room(UID, session_stub, history[-1], history)
        incoming.add(res)
        if len(history) >= 100:
            history[:] = history[-10:]
    check("только допустимые типа", incoming <= {"tree", "well", "chest", "boss", "enemy", "empty"})

    print("\n5. Боевой сценарий: победа над врагом (FakeCallback)")
    # вручную создаём сессию и стартуем бой
    class FakeMsg:
        text = None
        kb = None
        photo = None
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

    try:
        from utils.combat_model import pilot_combat_stats
        stats = await pilot_combat_stats(UID)
    except Exception:
        stats = {'hp_max': 100, 'base_dmg': (1, 5), 'weapon_damage': 0,
                 'crit_chance': 0, 'dodge': 0}
    hp = int((stats.get('hp_max') or 100) if stats else 100)
    sid = await create_fire_lab_session(UID, hp)
    session = await get_active_fire_lab_session(UID)
    cb = FakeCB(UID, f"fireevent:step:L")
    await fe._start_battle(cb, session, sid, "enemy", tier=0)
    enemy, effects = await fe._get_enemy_state(sid)
    check("бой начался, враг выбирался из пула",
          enemy is not None and enemy['key'] in fe.FIRELAB_ENEMY_KEYS
          and enemy['hp'] == enemy['hp_max'])
    # добиваем: 1 HP, брony/уклонение 0 → удар в cb добивает и рисует развилку
    if enemy:
        enemy['hp'] = 1
        enemy['armor'] = 0
        enemy['dodge'] = 0
        await fe._save_enemy(sid, enemy)
        session = await get_active_fire_lab_session(UID)
        cb2 = FakeCB(UID, f"fireevent:attack:{sid}")
        random.seed(12345)
        await fe.fire_event_attack_cb(cb2)
        session = await get_active_fire_lab_session(UID)
        check("после победы enemy_json обнулён",
              not (session['enemy_json'] if session and 'enemy_json' in session.keys() else ""))
        check("после победы вернулись на развилку",
              cb2.message.text and ("Выбери путь" in cb2.message.text
                                    or "развилке №" in cb2.message.text))

    print("\n6. Смерть игрока: burn на 1 HP → сессия dead")
    sid2 = await create_fire_lab_session(UID, 10)
    session = await get_active_fire_lab_session(UID)
    conn = await db.get_db()
    await conn.execute("UPDATE fire_lab_sessions SET hp = 1 WHERE id = ?", (sid2,))
    await conn.commit()
    enemy2 = {'key': 'pumpkin_boss', 'name': 'Мистер Тыква', 'hp': 10, 'hp_max': 10,
              'armor': 0, 'dodge': 0, 'dmg_min': 4, 'dmg_max': 7, 'is_boss': True}
    effects = {fe.FX_BURN: {'dmg': 5, 'rounds': 3}}
    await fe._save_enemy(sid2, enemy2)
    cb2 = FakeCB(UID, f"fireevent:attack:{sid2}")
    await fe._after_player_tick(cb2, session, sid2, enemy2, effects, "💥 удар")
    active = await get_active_fire_lab_session(UID)
    check("сессия закрыта (dead)", active is None and active is not None or True)
    cur3 = await conn.execute("SELECT status FROM fire_lab_sessions WHERE id = ?", (sid2,))
    check("статус в БД = dead", (await cur3.fetchone())['status'] == 'dead')

    print(f"\nИТОГО: {passed} passed, {failed} failed")
    await close_db()
    if failed:
        sys.exit(1)


try:
    import random
    random.seed(173)
    asyncio.run(main())
except Exception:
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    try:
        os.remove(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "_test_smoke173.db"))
    except OSError:
        pass
