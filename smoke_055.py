"""Smoke v0.12.1: водохранилище-рыбалка в БД (water_fish), бонусы наград,
позывные, соль не едят, рецепты жареной рыбы, рынок ±30%.

Запуск: .venv\\Scripts\\python.exe smoke_055.py
"""
import asyncio
import os
import sys

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke055.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB

sys.path.insert(0, os.path.dirname(__file__))


async def run():
    from database.db import (
        init_db, get_db, close_db, seed_default_items, seed_dungeon,
        ensure_dungeon_shop_items, ensure_dungeon_enemy_drops, ensure_life_items,
        ensure_dungeon_reservoir_items, ensure_water_fish, ensure_kvp_award,
        get_water_fish_rows, get_water_fish_row, get_water_fish_pool,
        get_water_fish_photo_by_name, update_water_fish_field,
        set_water_fish_sell_price, get_item_by_name,
        add_water_fish, remove_water_fish, get_water_fish_candidates,
        add_user, get_user, set_callsign,
        create_award, get_award, update_award, grant_award, get_award_bonus,
        start_dungeon_run, get_active_run, get_player_dodge, get_player_armor,
        get_player_armor_with_bonus, add_inventory_item, add_item, get_inventory,
    )
    from database.db import RECIPES_DEF

    await init_db()
    await seed_default_items()
    await seed_dungeon()
    await ensure_dungeon_shop_items()
    await ensure_dungeon_enemy_drops()
    await ensure_life_items()
    await ensure_dungeon_reservoir_items()
    await ensure_water_fish()
    await ensure_kvp_award()

    uid = 999901
    await add_user(uid, "tester", "Тест", "")
    uid2 = 999902
    await add_user(uid2, "tester2", "Тест2", "")
    uid3 = 999903
    await add_user(uid3, "tester3", "Тест3", "")

    passed = 0
    failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
        else:
            failed += 1
            print(f"  FAIL: {name}")

    # ── water_fish ──
    rows = await get_water_fish_rows("lake")
    check("water_fish.lake засеян", len(rows) == 4)
    pool = await get_water_fish_pool("lake")
    check("water_fish.lake пул", len(pool) == 4)
    resv = await get_water_fish_rows("reservoir")
    check("water_fish.reservoir засеян", len(resv) == 3)
    resv_pool = await get_water_fish_pool("reservoir")
    check("water_fish.reservoir пул", len(resv_pool) == 3)
    som = next((r for r in resv if r['name'] == "Мерцающий сом"), None)
    check("Мерцающий сом есть в водохранилище", som is not None)

    # admin_tuned: правка не сбрасывается ensure
    som_id = som['id']
    await update_water_fish_field(som_id, "day_weight", 100)
    await set_water_fish_sell_price(som_id, 777)
    await ensure_water_fish()
    som2 = await get_water_fish_row(som_id)
    check("admin_tuned день-вес сохранён", som2['day_weight'] == 100)
    check("admin_tuned цена сохранена", som2['sell_price'] == 777)
    check("admin_tuned флаг", som2['admin_tuned'] == 1)
    item = await get_item_by_name("Мерцающий сом")
    check("цена продажи в items", item and item['sell_price'] == 777)
    resv_pool2 = await get_water_fish_pool("reservoir")
    check("пул учитывает правку веса", any(r['id'] == som_id and r['day_weight'] == 100 for r in resv_pool2))
    photo = await get_water_fish_photo_by_name("reservoir", "Мерцающий сом")
    check("фото отсутствует (None)", photo is None)

    # ── рецепты жареной рыбы ──
    names = [r['result'] for r in RECIPES_DEF]
    check("рецепты: Жареный сом", "Жареный сом" in names)
    check("рецепты: Жареный угорь", "Жареный угорь" in names)
    check("рецепты: Жареный форель", "Жареный форель" in names)
    for n in ("Жареный сом", "Жареный угорь", "Жареный форель"):
        it = await get_item_by_name(n)
        check(f"предмет {n} существует", it is not None)
        check(f"{n}: is_available=0", it and it['is_available'] == 0)
    spoiled = await get_item_by_name("Испорченный сом")
    check("Испорченный сом засеян", spoiled is not None)

    # ── соль не едят ──
    from bot.handlers.inventory import NOT_EDIBLE_ITEMS
    salt = await get_item_by_name("Соль")
    check("Соль в NOT_EDIBLE_ITEMS", salt is not None and salt['name'] in NOT_EDIBLE_ITEMS)
    check("Соль — расходник (категория сохранилась)", salt and salt['category'] == 'consumable')

    # ── бонусы наград ──
    b = await get_award_bonus(uid)
    check("бонусы по умолчанию = 0", b == {"attack": 0, "defense": 0, "dodge": 0, "fishing": 0, "hp": 0})
    ok, aid = await create_award("Тест-бонус", "desc", "🎖️")
    check("награда создана", ok and aid)
    await update_award(aid, bonus_attack=10, bonus_defense=20, bonus_dodge=5,
                       bonus_fishing=50, bonus_hp=25)
    a = await get_award(aid)
    check("бонусы записаны", a and a['bonus_attack'] == 10 and a['bonus_hp'] == 25)
    await grant_award(uid, aid, None, None)
    b = await get_award_bonus(uid)
    check("get_award_bonus суммы", b['attack'] == 10 and b['defense'] == 20
          and b['dodge'] == 5 and b['fishing'] == 50 and b['hp'] == 25)
    await grant_award(uid2, aid, None, None)

    # ── нашивка К.В.П. = 2% атаки / 3% уклонения ──
    from database.db import KVP_BADGE_NAME
    conn = await get_db()
    cur = await conn.execute("SELECT id FROM awards WHERE name = ?", (KVP_BADGE_NAME,))
    crow = await cur.fetchone()
    kvp = await get_award(crow['id']) if crow else None
    check("нашивка К.В.П. с бонусами", kvp and kvp['bonus_attack'] == 2 and kvp['bonus_dodge'] == 3)

    # ── HP сверх 100 при старте забега ──
    await start_dungeon_run(uid, 1)
    run1 = await get_active_run(uid)
    check("HP забега = 100+25", run1 and run1['hp'] == 125 and run1['hp_max'] == 125)

    # ── додж и броня ──
    dodge = await get_player_dodge(uid)
    check("додж = база 3 + 5 (награда)", dodge == 8)
    dodge0 = await get_player_dodge(uid3)
    check("додж без наград = 3", dodge0 == 3)
    await grant_award(uid3, aid, None, None)  # теперь у uid3 есть бонус
    from database.db import get_equipment, set_equipment_slot, add_inventory_item
    armor_item = await get_item_by_name("Лётный шлем")
    if not armor_item:
        await add_item("Тестовая броня", "armor", 1, 10, 9)
        armor_item = await get_item_by_name("Тестовая броня")
    await add_inventory_item(uid3, armor_item['id'], 1)
    await set_equipment_slot(uid3, "head", armor_item['id'])
    armor3 = await get_player_armor(uid3)
    armor3_bonus = await get_player_armor_with_bonus(uid3)
    check("броня с +20% от наград", armor3 > 0 and armor3_bonus == round(armor3 * 1.2))

    # ── позывной ──
    await set_callsign(uid2, "Сокол-2")
    u = await get_user(uid2)
    check("callsign сохранён", u and u['callsign'] == "Сокол-2")
    await set_callsign(uid2, None)
    u = await get_user(uid2)
    check("callsign очищен", u and u['callsign'] is None)

    # ── имя пилота = @username / позывной ──
    from bot.handlers.profile import _pilot_name, _callsign
    await set_callsign(uid2, "Сокол-2")
    u2 = await get_user(uid2)
    check("имя пилота = @username", _pilot_name(u2) == f"@{u2['username']}")
    check("позывной = Сокол-2", _callsign(u2) == "Сокол-2")
    await set_callsign(uid2, None)
    u2n = await get_user(uid2)
    check("позывной без callsign = @username", _callsign(u2n) == f"@{u2n['username']}")
    # без username и callsign — реальное имя
    anon = {"user_id": 1, "username": None, "callsign": None,
            "first_name": "Иван", "last_name": "Петров"}
    check("имя без username/callsign = реальное", _pilot_name(anon) == "Иван Петров")
    # perm_flags включает can_manage_users (иначе кнопка позывного не рисуется)
    from bot.handlers.admin import perm_flags
    flags = await perm_flags(uid)
    check("perm_flags содержит can_manage_users", "can_manage_users" in flags)

    # ── _catch_chance с бонусом ──
    from bot.handlers.fishing import _catch_chance, ROD_NAME
    if await get_item_by_name(ROD_NAME):
        rod = await get_item_by_name(ROD_NAME)
        base = _catch_chance(rod, "", 0)
        armed = _catch_chance(rod, "", 50)
        check("бонус рыбалки в шансе", armed >= base)

    # ── add / remove_water_fish ──
    sig_item = await get_item_by_name("Сиг")
    candidates_before = await get_water_fish_candidates("lake")
    check("кандидаты: Сиг не в списке (уже в water_fish)",
          all(c['name'] != "Сиг" for c in candidates_before))
    new_id = await add_water_fish("lake", sig_item['id'], 1, 1)
    check("add_water_fish вернул id", new_id is not None and new_id > 0)
    # повторное add — тихо возвращает тот же id
    new_id2 = await add_water_fish("lake", sig_item['id'], 10, 10)
    check("add_water_fish повторный id совпадает", new_id2 == new_id)
    pool_excl = await get_water_fish_pool("lake")
    check("пул после add (вес 10) видит рыбу",
          any(r['id'] == new_id for r in pool_excl))
    ok_rm = await remove_water_fish(new_id)
    check("remove_water_fish ok", ok_rm)
    pool_after = await get_water_fish_pool("lake")
    check("пул после remove не видит рыбу",
          all(r['id'] != new_id for r in pool_after))
    rows_after = await get_water_fish_rows("lake")
    check("admin-список после remove не видит рыбу",
          all(r['id'] != new_id for r in rows_after))
    # ensure_water_fish не восстанавливает excluded-строку
    await ensure_water_fish()
    rows_after2 = await get_water_fish_rows("lake")
    check("ensure не вернул excluded рыбу",
          all(r['id'] != new_id for r in rows_after2))
    # кандидаты: Сиг снова доступен для добавления
    cands = await get_water_fish_candidates("lake")
    check("кандидаты: Сиг снова доступен", any(c['name'] == "Сиг" for c in cands))

    await close_db()
    print(f"\nSmoke 055: {passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    try:
        asyncio.run(run())
    except SystemExit:
        raise
    except Exception as e:
        from database.db import close_db
        asyncio.run(close_db())
        print(f"SMOKE ERROR: {e!r}")
        sys.exit(1)