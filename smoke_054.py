"""Smoke v0.12.0: расширение «Крысиного Подвала» (2 этажа, боссы, статусы, водохранилище).

Запуск: venv python smoke_054.py
"""
import asyncio
import json
import os
import sys

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke054.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB

sys.path.insert(0, os.path.dirname(__file__))


async def run():
    from database.db import (
        init_db, get_db, close_db, seed_default_items, seed_dungeon,
        ensure_dungeon_shop_items, ensure_dungeon_enemy_drops, ensure_life_items,
        ensure_dungeon_reservoir_items, get_all_dungeons, get_dungeon,
        get_dungeon_rooms_map, get_floor_enemies, get_dungeon_enemies,
        get_item_by_name, get_equipment_slot_items, get_equipment,
        set_equipment_slot, get_active_run, start_dungeon_run, advance_floor,
        get_item, get_inventory, item_fits_slot, add_inventory_item,
        add_user, add_item,
    )

    await init_db()
    await seed_default_items()
    await seed_dungeon()
    await ensure_dungeon_shop_items()
    await ensure_dungeon_enemy_drops()
    await ensure_life_items()
    await ensure_dungeon_reservoir_items()

    uid = 999901
    await add_user(uid, "tester", "Тест", "")

    passed = 0
    failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
        else:
            failed += 1
            print(f"  FAIL: {name}")

    conn = await get_db()

    # ── 1. Миграции колонок ──
    async def has_column(table, col):
        cur = await conn.execute(f"PRAGMA table_info({table})")
        rows = await cur.fetchall()
        return any(r["name"] == col for r in rows)

    check("col dungeon_enemies.bleed_chance", await has_column("dungeon_enemies", "bleed_chance"))
    check("col dungeon_enemies.bleed_dmg", await has_column("dungeon_enemies", "bleed_dmg"))
    check("col dungeon_enemies.frostbite_chance", await has_column("dungeon_enemies", "frostbite_chance"))
    check("col dungeon_enemies.description", await has_column("dungeon_enemies", "description"))
    check("col items.cure_frostbite", await has_column("items", "cure_frostbite"))
    check("col dungeons.rooms_map", await has_column("dungeons", "rooms_map"))

    # ── 2. Данж: 2 этажа, rooms_map ──
    dgns = await get_all_dungeons(training=False)
    check("seed dungeon exists", len(dgns) >= 1)
    dng_id = dgns[0]["id"]

    rooms_map = await get_dungeon_rooms_map(dng_id)
    check("rooms_map == [9, 8]", rooms_map == [9, 8])
    check("dungeon floors_count == 2", dgns[0]["floors_count"] == 2)

    f1 = await get_floor_enemies(dng_id, 1)
    f2 = await get_floor_enemies(dng_id, 2)
    check("floor1 enemies: 4 (3 комнатных + капитан)", len(f1) == 4)
    check("floor2 enemies: 4 (3 комнатных + король)", len(f2) == 4)

    cap = next((e for e in f1 if e["is_boss"]), None)
    king = next((e for e in f2 if e["is_boss"]), None)
    check("boss floor1 = Крысиный капитан", cap and cap["name"] == "Крысиный капитан")
    check("boss floor2 = Король крыс", king and king["name"] == "Король крыс")

    names_f2 = {e["name"] for e in f2}
    check("new enemy Прислужник короля", "Прислужник короля" in names_f2)
    check("new enemy Чумная крыса", "Чумная крыса" in names_f2)
    check("new enemy Морозный паук", "Морозный паук" in names_f2)

    fus = next((e for e in f2 if e["name"] == "Прислужник короля"), None)
    check("Прислужник короля: bleed_chance=25", fus and fus["bleed_chance"] == 25)
    check("Прислужник короля: bleed_dmg=3", fus and fus["bleed_dmg"] == 3)
    chum = next((e for e in f2 if e["name"] == "Чумная крыса"), None)
    check("Чумная крыса: poison_chance=20", chum and chum["poison_chance"] == 20)
    check("Чумная крыса: bleed_chance=35", chum and chum["bleed_chance"] == 35)
    frost = next((e for e in f2 if e["name"] == "Морозный паук"), None)
    check("Морозный паук: frostbite_chance=35", frost and frost["frostbite_chance"] == 35)

    check("капитан description задан", bool(cap and cap["description"]))
    check("король description задан", bool(king and king["description"]))
    check("король: reward_nm=20", king and king["reward_nm"] == 20)

    # ── 3. Предметы водохранилища ──
    for f in ("Мерцающий сом", "Искрящийся угорь", "Светящаяся форель"):
        it = await get_item_by_name(f)
        check(f"{f} существует", it is not None)
        check(f"{f} скрыт из магазина", it and it["is_available"] == 0)
        check(f"{f} категория fishing", it and it["category"] == "fishing")

    vk = await get_item_by_name("Огненная вода (водка)")
    check("водка существует", vk is not None)
    check("водка: cure_frostbite=1", vk and vk["cure_frostbite"] == 1)
    check("водка: heal=10", vk and (vk["heal"] or 0) == 10)
    check("водка: drink_effect=alcohol_strong", vk and vk["drink_effect"] == "alcohol_strong")
    mors = await get_item_by_name("Горячий ягодный морс")
    check("морс существует", mors is not None)
    check("морс: cure_frostbite=1", mors and mors["cure_frostbite"] == 1)
    check("морс: heal=10", mors and (mors["heal"] or 0) == 10)

    for t in ("Кусочек королевского сыра", "Коготь чумной крысы",
              "Сосулька-паутина", "Метка Короля крыс"):
        check(f"трофей 2 этажа: {t}", await get_item_by_name(t) is not None)

    # ── 4. get_equipment_slot_items несёт cure_frostbite ──
    # Водка подходит в слот: consumable.
    check("item_fits_slot consumable->potion1",
          item_fits_slot({"category": "consumable"}, "potion1"))
    check("item_fits_slot weapon->potion1 False",
          not item_fits_slot({"category": "weapon"}, "potion1"))
    await add_inventory_item(uid, mors["id"], 2)
    await set_equipment_slot(uid, "potion1", mors["id"])
    slot_items = await get_equipment_slot_items(uid)
    check("slot item содержит cure_frostbite",
          any("cure_frostbite" in r.keys() for _, r in slot_items))

    # ── 5. advance_floor: сброс комнат ──
    await start_dungeon_run(uid, dng_id)
    run = await get_active_run(uid)
    check("run стартовал: floor=1 room=0", run and run["floor"] == 1 and run["room_number"] == 0)
    await advance_floor(run["id"], 2)
    run = await get_active_run(uid)
    check("advance_floor -> floor=2 room=0", run and run["floor"] == 2 and run["room_number"] == 0)

    # ── 6. rooms_map фолбэк для старого данжа без колонки ──
    cur = await conn.execute(
        "INSERT INTO dungeons (name, floors_count, rooms_per_floor, is_training) "
        "VALUES ('Старый', 1, 10, 0)")
    old_id = cur.lastrowid
    await conn.commit()
    check("fallback rooms_map -> [10]", await get_dungeon_rooms_map(old_id) == [10])

    # ── 7. Админ-редактор: статусные поля врагов ──
    from database.db import get_enemy, update_enemy_fields
    frost = await get_enemy(frost["id"])
    if frost:
        await update_enemy_fields(frost["id"], frostbite_chance=50, bleed_dmg=1, hp=27)
        fresh = await get_enemy(frost["id"])
        check("editor: frostbite_chance=50 persisted", fresh["frostbite_chance"] == 50)
        check("editor: admin_tuned=1", fresh["admin_tuned"] == 1)
        await ensure_dungeon_enemy_drops()
        fresh = await get_enemy(frost["id"])
        check("editor: sync сохраняет frostbite_chance=50", fresh["frostbite_chance"] == 50)
        check("editor: sync сохраняет hp=27", fresh["hp"] == 27)
        check("editor: sync обновляет description (floor всегда)",
              bool(fresh["description"]))

    # ── 8. get_dungeon_rooms_map на свежем данже после sync ──
    await ensure_dungeon_enemy_drops()
    check("rooms_map после sync: [9,8]", await get_dungeon_rooms_map(dng_id) == [9, 8])
    dng = await get_dungeon(dng_id)
    check("rooms_map JSON сохранён", json.loads(dng["rooms_map"]) == [9, 8])

    await close_db()
    try:
        os.remove(os.environ["DATABASE_PATH"])
    except OSError:
        pass

    print(f"\n{'='*40}")
    print(f"  PASSED: {passed}   FAILED: {failed}")
    print(f"{'='*40}")
    with open(os.path.join(os.path.dirname(__file__), "_smoke_result.txt"), "w", encoding="utf-8") as f:
        f.write(f"PASSED: {passed}   FAILED: {failed}\n")
    return failed


if __name__ == "__main__":
    code = 0
    try:
        res = asyncio.run(run())
        code = 1 if res else 0
    except Exception:
        import traceback
        traceback.print_exc()
        code = 2
    finally:
        sys.stdout.flush()
        sys.stderr.flush()
    os._exit(code)