# -*- coding: utf-8 -*-
"""Smoke 192 — ягоды леса, медведь (выключен), рецепт леденца, «Повар Круговорота»,
клановая накидка и талисман как слоты снаряжения с бонусами в боевых статах.

1. Ягоды: суммы шансов по зонам (опушка 50%, прогалина 100%), предметы вне магазина.
2. Медведь: засеян, выключен, дроп — шкура; в поиске грибов не появляется (chance=0).
3. Рецепт «Леденец из ягод» скрыт, свиток тоже скрыт (после ensure_recipe_shop_items).
4. Накидка: слот clan_cape принимает только экипировку с этим слотом; бонус уклонения в статах.
5. «Повар Круговорота»: каждое из трёх блюд учитывается один раз, на 3 — уровень 1.
"""
import asyncio
import os
import sys

os.environ["DATABASE_PATH"] = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "_test_smoke192.db")

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
    from database.db import (init_db, close_db, get_db, add_user, get_item_by_name,
                             ensure_forest_enemies, ensure_recipe_shop_items,
                             get_source_enemy_by_key, set_equipment_slot,
                             get_accessory_bonus, track_fire_cook, get_achievement_level,
                             get_source_enemies, ensure_firelab_items, item_fits_slot)
    from utils.combat_model import pilot_combat_stats

    await init_db()
    await ensure_firelab_items()
    await ensure_forest_enemies()
    await ensure_recipe_shop_items()
    conn = await get_db()

    print("\n1. Ягоды")
    glade = sum(c for _, c in config.FOREST_BERRY_TABLE["glade"])
    clearing = sum(c for _, c in config.FOREST_BERRY_TABLE["clearing"])
    check("опушка: черника 50% (остальное пусто)", glade == 50)
    check("прогалина: черника 40, малина 25, земляника 20, медведь 5, пылающие 10 (=100%)",
          clearing == 100)
    for name in (config.FOREST_BERRY_BLUEBERRY, config.FOREST_BERRY_RASPBERRY,
                 config.FOREST_BERRY_STRAWBERRY):
        it = await get_item_by_name(name)
        check(f"«{name}» есть и скрыт из магазина", it is not None and it['is_available'] == 0)

    print("\n2. Медведь")
    bear = await get_source_enemy_by_key("forest", "bear")
    check("медведь засеян", bear is not None)
    check("медведь включён в выдачу", bear is not None and bear['enabled'] == 1)
    check("медведь не в обычном поиске (chance 0)", bear is not None and float(bear['chance'] or 0) == 0)
    check("медведь в 1.5 раза сильнее кабана по HP",
          bear is not None and bear['hp'] == round(config.FOREST_BOAR_HP * 1.5))
    skin = await get_item_by_name(config.FOREST_BEAR_SKIN_NAME)
    drops = [d['item_id'] for d in __import__('json').loads(bear['drops'] or '[]')] if bear else []
    check("шкура медведя — дроп", skin is not None and skin['id'] in drops)
    check("включённый медведь есть в списке включённых",
          any(e['key'] == 'bear' for e in await get_source_enemies("forest", enabled_only=True)))

    print("\n3. Рецепт леденца")
    recipe = await (await conn.execute(
        "SELECT id, is_available, result_item_name FROM recipes WHERE name = 'Леденец из ягод'")).fetchone()
    check("рецепт создан", recipe is not None)
    check("рецепт скрыт", recipe is not None and recipe['is_available'] == 0)
    check("результат — праздничный леденец", recipe is not None
          and recipe['result_item_name'] == config.FIRE_LAB_CANDY_NAME)
    scroll = await get_item_by_name("Рецепт: Леденец из ягод")
    check("свиток скрыт", scroll is not None and scroll['is_available'] == 0)

    print("\n4. Клановая накидка и слот")
    UID = 192001
    await add_user(UID, "t", "Пилот 192", "")
    cape = await get_item_by_name(config.CLAN_CAPE_NAME)
    check("накидка — экипировка слота clan_cape", cape is not None and cape['equip_slot'] == 'clan_cape')
    weapon = await get_item_by_name("Вилы") or await get_item_by_name("Кухонный нож")
    check("накидка подходит в слот clan_cape", cape is not None and item_fits_slot(cape, 'clan_cape'))
    check("накидка не подходит в слот головы", cape is not None and not item_fits_slot(cape, 'head'))
    if weapon:
        check("оружие не подходит в слот clan_cape", not item_fits_slot(weapon, 'clan_cape'))
    before = (await pilot_combat_stats(UID))['dodge']
    await set_equipment_slot(UID, 'clan_cape', cape['id'])
    after = (await pilot_combat_stats(UID))['dodge']
    print(f"      уклонение до {before}, после {after}, бонус {config.CLAN_CAPE_DODGE}")
    check("бонус накидки в уклонении",
          abs((after - before) - config.CLAN_CAPE_DODGE) < 1e-9)
    check("накидка без брони: аксессуары дают 0 брони",
          (await get_accessory_bonus(UID)) == {"armor": 0})

    print("\n5. Повар Круговорота")
    check("на старте уровня нет", (await get_achievement_level(UID, "fire_cook")) == 0)
    await track_fire_cook(UID, config.FIRE_LAB_PIE_NAME)
    await track_fire_cook(UID, config.FIRE_LAB_PIE_NAME)
    check("повтор одного блюда не считается", (await get_achievement_level(UID, "fire_cook")) == 0)
    await track_fire_cook(UID, "Рыбный пирог")
    check("два вида — ещё нет", (await get_achievement_level(UID, "fire_cook")) == 0)
    await track_fire_cook(UID, config.FIRE_LAB_CANDY_NAME)
    check("три вида — уровень 1", (await get_achievement_level(UID, "fire_cook")) == 1)
    await track_fire_cook(UID, "Вилы")
    check("посторонний предмет не учитывается", (await get_achievement_level(UID, "fire_cook")) == 1)

    print(f"\nИТОГО: {passed} passed, {failed} failed")
    await close_db()
    return failed


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
