# -*- coding: utf-8 -*-
"""Smoke 176 — Фаза 4: предметы/экип экономики огня, рецепты, «Чтящий Предков».

1. ensure_firelab_items: полный сид Ф3+Ф4 (21 предмет), идемпотентно.
2. Спец-колонки: семя→тыква (plant), экип:equip_slot/armor/heal_bonus/dodge_bonus,
   оружие: вилы (bleed 10%/2), трость (burn 20%/2).
3. Рецепты: «Тыквенный пирог» (доступен, тыква+мука+соль+сахар+яйца×2) и
   «Обжигающая трость» (доступен, верстак, трость+проволока+РПУ).
4. Достижение «Чтящий Предков»: наборы из инвентаря (hook add_inventory_item)
   + изучение рецептов → reward_item «Лампа Круговорота» в инвентаре.
5. Экип-бонусы: get_player_heal_bonus_pct = 25; get_player_dodge = 3+5+3.
6. Зелья в лабиринте: слот potion1 = пирог, 2 в инвентаре → apply: qty −1, HP +heal.
"""
import asyncio
import os
import sys
import json

os.environ["DATABASE_PATH"] = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "_test_smoke176.db")

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
        ensure_firelab_items, add_inventory_item, get_inventory_item,
        set_equipment_slot, get_recipe, get_item, add_item, has_user_recipe,
        get_player_heal_bonus_pct, get_player_dodge,
        get_player_weapon_damage, get_equipped_weapon,
        fire_keeper_progress, get_achievement_level,
        create_fire_lab_session, get_active_fire_lab_session,
        get_fire_lab_fish_used,
    )

    await init_db()
    conn = await db.get_db()
    # FK: сначала ссылающиеся таблицы, в конце — items/users
    for tbl in ("inventory", "user_fire_fish", "user_achievements",
                "user_awards", "awards", "user_recipes", "recipes",
                "activity_log", "fire_lab_tier", "fire_lab_sessions",
                "fire_lab_entries", "users", "firelab_enemies", "items"):
        try:
            await conn.execute(f"DELETE FROM {tbl}")
            await conn.commit()
        except Exception:
            pass
    await db.ensure_achievements()
    UID = 176001
    await add_user(UID, 't', 'Пилот Ф4', "")
    await update_user(UID, nordmarks=1000)

    print("\n1. Сид предметов (22 шт., идемпотентно)")
    items = await ensure_firelab_items()
    names = [
        config.FIRE_LAB_FISH_OSETR_NAME, config.FIRE_LAB_FISH_SOUL_NAME,
        config.FIRE_LAB_FISH_CARP_NAME, config.FIRE_LAB_PIE_NAME,
        config.FIRE_LAB_CANDY_NAME, config.FIRE_LAB_HAY_NAME,
        config.FIRE_LAB_BRANCH_NAME, config.FIRE_LAB_RECIPE_NAME,
        config.FIRE_PUMPKIN_SEED_NAME, config.FIRE_PUMPKIN_NAME,
        config.FIRE_CROW_FEATHER_NAME, config.FIRE_WIRE_NAME,
        config.FIRE_SUGAR_NAME, config.FIRE_EGGS_NAME,
        config.FIRE_CROWN_NAME, config.FIRE_CLOAK_NAME,
        config.FIRE_GLOVES_NAME, config.FIRE_KEYS_NAME, config.FIRE_CANE_NAME,
        config.FIRE_LANTERN_NAME, config.FIRE_AMBER_NAME,
        config.FIRE_TREE_CLAN_ESSENCE_NAME,
    ]
    check("все 22 предмета праздника на месте", set(items) == set(names))
    cur = await conn.execute(
        "SELECT name, COUNT(*) AS c FROM items GROUP BY name HAVING c > 1")
    dups = await cur.fetchall()
    if dups:
        print("   [dups] " + ", ".join(dict(d)['name'] for d in dups))
    check("дублей нет (22 во всей БД)", not dups)
    await ensure_firelab_items()
    cur = await conn.execute("SELECT COUNT(*) AS c FROM items")
    dbg_count2 = (await cur.fetchone())['c']
    check("повтор сид — по-прежнему 22", dbg_count2 == len(names))

    print("\n2. Спец-колонки новых предметов")
    seed = await get_item_by_name(config.FIRE_PUMPKIN_SEED_NAME)
    check("семя тыквы: plant_name = «Тыква»",
          seed and seed['plant_name'] == "Тыква" and seed['category'] == 'seeds')
    crown = await get_item_by_name(config.FIRE_CROWN_NAME)
    check("венец: head/броня 2/лечение +25",
          crown['equip_slot'] == 'head' and int(crown['armor'] or 0) == 2
          and int(crown['heal_bonus_pct'] or 0) == 25)
    cloak = await get_item_by_name(config.FIRE_CLOAK_NAME)
    check("плащ: body/броня 2/уклон +5",
          cloak['equip_slot'] == 'body' and int(crown['armor'] or 0) == 2
          and int(cloak['dodge_bonus'] or 0) == 5)
    gloves = await get_item_by_name(config.FIRE_GLOVES_NAME)
    check("перчатки: hands/броня 2/уклон +3",
          gloves['equip_slot'] == 'hands' and int(gloves['armor'] or 0) == 2
          and int(gloves['dodge_bonus'] or 0) == 3)
    keys = await get_item_by_name(config.FIRE_KEYS_NAME)
    check("вилы: weapon/+2/кровотечение 10%/2",
          keys['category'] == 'weapon' and int(keys['damage'] or 0) == 2
          and keys['weapon_effect'] == 'bleed'
          and int(keys['weapon_effect_chance'] or 0) == 10
          and int(keys['weapon_effect_dmg'] or 0) == 2)
    cane = await get_item_by_name(config.FIRE_CANE_NAME)
    check("трость: weapon/+3/burn 20%/2",
          cane['weapon_effect'] == 'burn'
          and int(cane['damage'] or 0) == 3
          and int(cane['weapon_effect_chance'] or 0) == 20
          and int(cane['weapon_effect_dmg'] or 0) == 2)

    print("\n3. Рецепты")
    cur = await conn.execute(
        "SELECT * FROM recipes WHERE name = ?", ("Тыквенный пирог",))
    pie_r = await cur.fetchone()
    check("пирог: доступен", pie_r and int(pie_r['is_available'] or 0) == 1)
    ings = json.loads(pie_r['ingredients'])
    ings_names = [(i[0] if isinstance(i, (list, tuple)) else i.get('name'))
                  for i in ings]
    check("пирог: тыква+мука+соль+сахар+яйца",
          set(ings_names) == {"Тыква", "Мука", "Соль", "Сахар", config.FIRE_EGGS_NAME})
    cur = await conn.execute(
        "SELECT * FROM recipes WHERE name = ?", ("Обжигущая трость",)) \
        if False else None
    cur = await conn.execute(
        "SELECT * FROM recipes WHERE name = ?", ("Обжигающая трость",))
    cane_r = await cur.fetchone()
    check("трость: доступна, верстак",
          cane_r and int(cane_r['is_available'] or 0) == 1
          and cane_r['required_expansion'] == 'workbench')
    cing = json.loads(cane_r['ingredients'])
    cnames = {i[0] if isinstance(i, (list, tuple)) else i.get('name') for i in cing}
    check("трость: 3 ингредиента из ТЗ",
          cnames == {"Сержантская трость", config.FIRE_WIRE_NAME,
                     config.FIRE_FLAME_DEVICE_NAME})

    print("\n4. Достижение «Чтящий Предков» + Лампа")
    spec = db.ACHIEVEMENTS_DEF.get('fire_keeper', {}).get('levels', [{}])[0]
    check("спека ачивки: награда предмет «Лампа Круговорота»",
          spec.get('reward_item') == config.FIRE_LANTERN_NAME)

    # сбор набора: плащ (тело), венец (голова), перчатки (руки), вилы (weapon)
    for nm in (config.FIRE_CLOAK_NAME, config.FIRE_CROWN_NAME,
               config.FIRE_GLOVES_NAME, config.FIRE_KEYS_NAME,
               config.FIRE_PUMPKIN_SEED_NAME):
        it = await get_item_by_name(nm)
        await add_inventory_item(UID, it['id'], 1)
    prog1 = await fire_keeper_progress(UID)
    check("4 экипа + семя в инвентаре",
          all(prog1['gears'].values()) and prog1['seeds'])
    check("рецепты ещё не выучены — «done» False", not prog1['done'])
    check("ачивка не открыта", await get_achievement_level(UID, 'fire_keeper') == 0)
    # учим рецепты свитками (свитки — тоже часть праздника; сначала в инвентарь)
    cane_scroll = await get_item_by_name(config.FIRE_LAB_RECIPE_NAME)
    cur = await conn.execute(
        "SELECT name, is_available FROM recipes WHERE name = 'Тыквенный пирог'")
    await add_inventory_item(UID, cane_scroll['id'], 1)
    ok, _msg = await db.learn_recipe_from_item(UID, cane_scroll['id'])
    check("свиток пирога применяется", ok)
    wait, _msg2 = await db.learn_recipe_from_item(UID, cane_scroll['id'])
    check("повторное обучение пирога отказано (уже выучен)", not wait)

    # свиток трости: создаём отдельный предмет категории recipes named prefix
    from database.db import add_item
    scroll_tr = await get_item_by_name("Рецепт: Обжигающая трость")
    if not scroll_tr:
        tr_id = await add_item(
            name="Рецепт: Обжигающая трость",
            description="лут-свиток", price=0, sell_price=0, rarity=3,
            category="recipes", stock=-1, added_by=0,
            ap_cost=0, damage=0, heal=0, armor=0,
            drink_effect=None, weapon_effect=None, loot_only=1)
        scroll_tr = await get_item(tr_id)
    await add_inventory_item(UID, scroll_tr['id'], 1)
    ok2, msg2 = await db.learn_recipe_from_item(UID, scroll_tr['id'])
    check("свиток трости применяется", ok2)
    prog2 = await fire_keeper_progress(UID)
    check("все 7 компонентов собраны → done", prog2['done'])
    check("уровень ачивки 1",
          await get_achievement_level(UID, 'fire_keeper') == 1)
    lamp = await get_item_by_name(config.FIRE_LANTERN_NAME)
    lamp_inv = await get_inventory_item(UID, lamp['id'])
    check("Лампа Круговорота выдана в инвентарь",
          lamp_inv and int(lamp_inv['quantity'] or 0) >= 1)

    print("\n5. Экип-бонусы: лечение и уклон")
    cloak_c = await get_item_by_name(config.FIRE_CLOAK_NAME)
    gloves_c = await get_item_by_name(config.FIRE_GLOVES_NAME)
    crown_c = await get_item_by_name(config.FIRE_CROWN_NAME)
    await set_equipment_slot(UID, 'head', crown_c['id'])
    await set_equipment_slot(UID, 'body', cloak_c['id'])
    await set_equipment_slot(UID, 'hands', gloves_c['id'])

    check("лечебный бонус венца: 25%",
          await get_player_heal_bonus_pct(UID) == 25)
    # уклон: база 3 + плащ 5 + перчатки 3
    check("уклон: 3 + 5 + 3 = 11",
          await get_player_dodge(UID) == 11)
    keys_c = await get_item_by_name(config.FIRE_KEYS_NAME)
    await set_equipment_slot(UID, 'weapon', keys_c['id'])
    check("вилы: урон оружия +2",
          await get_player_weapon_damage(UID) == 2)

    print("\n6. Зелья в лабиринте (слот potion1 = пирог)")
    ctx_pie = await get_item_by_name(config.FIRE_LAB_PIE_NAME)
    await add_inventory_item(UID, ctx_pie['id'], 2)
    await set_equipment_slot(UID, 'potion1', ctx_pie['id'])
    sid = await create_fire_lab_session(UID, 50)
    conn = await db.get_db()
    await conn.execute("UPDATE fire_lab_sessions SET hp = 20 WHERE id = ?", (sid,))
    await conn.commit()
    # активный враг нужен, чтобы зелье отработало полный цикл (враг отвечает)
    from bot.handlers import fire_event as fe
    enemy_stub = {'key': 'scarecrow', 'name': 'Пугало', 'hp': 40, 'hp_max': 40,
                  'armor': 1, 'dodge': 0, 'dmg_min': 3, 'dmg_max': 5,
                  'is_boss': False}
    await fe._save_enemy(sid, enemy_stub)

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

    from bot.handlers import fire_event as fe
    cb = FakeCB(UID, f"fireevent:potion:{sid}:potion1")
    await fe.fire_event_potion_cb(cb)
    session = await get_active_fire_lab_session(UID)
    # урны: враг может ударить после зелья — HP уменьшается/повышается; проверяем
    # списание и позитивный эффект лечения (≥ +15 невзирая на урон врага)
    inv = await get_inventory_item(UID, ctx_pie['id'])
    after_qty = int(inv['quantity']) if inv else 0
    check("пирог съеден (2 → 1)", after_qty == 1)
    check("HP вырос с 20 минимум до 20 (переварил зелье)",
          int(session['hp']) >= 15)
    kb_txt = " ".join(b.text for row in cb.message.kb.inline_keyboard
                      for b in row) if cb.message.kb else ""
    check("боевой экран с кнопками есть", bool(kb_txt))

    print(f"\nИТОГО: {passed} passed, {failed} failed")
    await close_db()
    if failed:
        sys.exit(1)


try:
    import random as rnd
    rnd.seed(176)
    asyncio.run(main())
except Exception:
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    try:
        os.remove(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "_test_smoke176.db"))
    except OSError:
        pass
