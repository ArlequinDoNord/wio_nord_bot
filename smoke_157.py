"""Smoke v0.38.0: единая система эффектов при ударе врага.

Проверяет:
1. Реестр ON_HIT_EFFECTS / ON_HIT_KIND_ORDER / ON_HIT_STATE_ROUNDS (config).
2. Ядро utils/onhit.py: parse, roll, apply, tick_dots, end_round,
   has_dot/frostbite/heal_multiplier/active_line, battle_state_keys,
   consumables_blocked_by_battle, register/unregister.
3. STATE_CONF: «оглушён»/«ослеплён» (enemy_appliable, crit_mult,
   blocks_consumables); battle_state_multipliers; enemy_appliable_states().
4. pilot_combat_stats(user_id, battle_states): атака/крит/уклонение ниже.
5. DB: колонка on_hit_effects во всех 5 таблицах врагов; get/set-хелперы
   (данж + источники); admin_tuned=1 при правке; миграция legacy → JSON.
6. Сиды: волк — кровотечение 30%/3, змея — яд 30%/2, неясыть — «ослеплён».
7. process_item_use: оглушение блокирует расходники (ACTIVE-реестр).
8. Админ: общий редактор (_onhit_*), legacy-поля убраны, колбэки на месте.
9. Боевые хендлеры (лес/лесозаготовка/копь/данж) используют onhit
   (register/tick/proc/end_round/unregister).

Запуск: .venv\\Scripts\\python.exe smoke_157.py
"""
import asyncio
import inspect
import json
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke157.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB

sys.path.insert(0, os.path.dirname(__file__))


async def run():
    from config import (
        ON_HIT_EFFECTS, ON_HIT_KIND_ORDER, ON_HIT_STATE_ROUNDS,
        FOREST_WHITE_WOLF_BLEED_CHANCE, FOREST_WHITE_WOLF_BLEED_DMG,
        LOGGING_SNAKE_POISON_CHANCE, LOGGING_SNAKE_POISON_DMG,
        LOGGING_OWL_BLIND_ROUNDS,
    )
    from utils import onhit
    from utils.states import (
        STATE_CONF, battle_state_multipliers, enemy_appliable_states,
    )
    from utils.combat_model import pilot_combat_stats
    from database.db import (
        init_db, close_db, seed_default_items, seed_dungeon,
        ensure_base_statuses,
        ensure_forest_enemies, ensure_logging_enemies, get_db,
        add_user, get_user, get_item_by_name, get_items_by_category,
        add_inventory_item, process_item_use,
        get_source_enemy_by_key, get_source_enemy,
        get_enemy_on_hit_effects, set_enemy_on_hit_effects,
        get_source_enemy_on_hit_effects, set_source_enemy_on_hit_effects,
        get_all_dungeons, get_dungeon_enemies,
        _migrate_enemy_on_hit_effects,
    )

    await init_db()
    await seed_default_items()
    await seed_dungeon()
    await ensure_base_statuses()
    await ensure_forest_enemies()
    await ensure_logging_enemies()

    passed = 0
    failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
        else:
            failed += 1
            print(f"  FAIL: {name}")

    # ── 1. Реестр эффектов (config) ──
    check("реестр: 5 видов эффектов",
          set(ON_HIT_EFFECTS) == {"bleed", "poison", "frostbite", "state", "lifesteal"})
    check("порядок KIND_ORDER", tuple(ON_HIT_KIND_ORDER)
          == ("bleed", "poison", "frostbite", "state", "lifesteal"))
    check("state-ходы: оглушён 3, ослеплён 4",
          ON_HIT_STATE_ROUNDS.get("оглушён") == 3
          and ON_HIT_STATE_ROUNDS.get("ослеплён") == 4)
    check("frostbite default_rounds = 4",
          ON_HIT_EFFECTS["frostbite"].get("default_rounds") == 4)

    # ── 2. Ядро onhit ──
    check("parse: валидный JSON",
          onhit.parse_on_hit_effects('[{"kind":"bleed","chance":30,"dmg":3}]')
          == [{"kind": "bleed", "chance": 30, "dmg": 3}])
    check("parse: None/мусор → []",
          onhit.parse_on_hit_effects(None) == []
          and onhit.parse_on_hit_effects("не json") == []
          and onhit.parse_on_hit_effects('{"kind":"bleed"}') == [])
    check("parse: неизвестный kind отфильтрован",
          onhit.parse_on_hit_effects('[{"kind":"xxx","chance":10}]') == [])

    saved_ri = onhit.random.randint
    onhit.random.randint = lambda a, b: 1  # прок всегда проходит
    try:
        procs = onhit.roll_procs([{"kind": "bleed", "chance": 100, "dmg": 3}])
        check("roll: bleed проходит", procs == [{"kind": "bleed", "dmg": 3}])
        procs = onhit.roll_procs([{"kind": "state", "key": "оглушён",
                                   "chance": 100}])
        check("roll: state добирает rounds из ON_HIT_STATE_ROUNDS",
              procs == [{"kind": "state", "key": "оглушён", "rounds": 3}])
        procs = onhit.roll_procs([{"kind": "frostbite", "chance": 100}])
        check("roll: frostbite добирает default_rounds",
              procs == [{"kind": "frostbite", "rounds": 4}])
        store = {}
        lines = onhit.apply_procs(999001, store, [
            {"kind": "bleed", "dmg": 3},
            {"kind": "poison", "dmg": 2},
            {"kind": "frostbite", "rounds": 4},
            {"kind": "state", "key": "оглушён", "rounds": 3},
        ], enemy_name="Тестовый враг")
        check("apply: все 4 эффекта в store",
              set(store["on_hit"]) == {"bleed", "poison", "frostbite", "оглушён"})
        check("apply: 4 фразы", len(lines) == 4)
        check("apply: юзер в ACTIVE", onhit.ACTIVE.get(999001) is store)
        dmg, dot_lines = onhit.tick_dots(store)
        check("tick: bleed+poison = 5 HP", dmg == 5 and len(dot_lines) == 2)
        check("has_dot: bleed/poison есть", onhit.has_dot(store, "bleed")
              and onhit.has_dot(store, "poison"))
        check("frostbite_active + heal ×0.5",
              onhit.frostbite_active(store) and onhit.heal_multiplier(store) == 0.5)
        check("battle_state_keys: оглушён", onhit.battle_state_keys(store) == ["оглушён"])
        check("active_line: кровотечение и оглушение",
              "Кровотечение" in onhit.active_line(store)
              and "Оглушён" in onhit.active_line(store))
        block_msg = onhit.consumables_blocked_by_battle(999001) or ""
        check("block расходников: оглушён",
              "Оглушён" in block_msg or "оглушён" in block_msg)
        del store["on_hit"]["оглушён"]
        check("после спада оглушения расходники не блокируются",
              onhit.consumables_blocked_by_battle(999001) is None)
        # Обморожение спадает по rounds_left
        store["on_hit"]["frostbite"] = {"rounds_left": 1}
        gone = onhit.end_round(store)
        check("end_round: frostbite удалён при 0",
              not onhit.frostbite_active(store)
              and any("прошло" in l for l in gone))
        onhit.unregister(999001)
        check("unregister снял из ACTIVE", 999001 not in onhit.ACTIVE)
    finally:
        onhit.random.randint = saved_ri

    # ── 3. STATE_CONF и модификаторы ──
    stun = STATE_CONF.get("оглушён")
    blind = STATE_CONF.get("ослеплён")
    check("оглушён: enemy_appliable", stun and stun.get("enemy_appliable") is True)
    check("оглушён: crit_mult 0.5", stun and abs(stun["crit_mult"] - 0.5) < 1e-9)
    check("оглушён: блок расходников", stun and stun.get("blocks_consumables") is True)
    check("ослеплён: enemy_appliable", blind and blind.get("enemy_appliable") is True)
    appliable = enemy_appliable_states()
    check("пул для врагов: оглушён+ослеплён",
          set(appliable) == {"оглушён", "ослеплён"})
    m = battle_state_multipliers(["оглушён"])
    check("battle multipliers: атака 0.7, крит 0.5, уклон 0.5",
          abs(m["attack_mult"] - 0.7) < 1e-9 and abs(m["crit_mult"] - 0.5) < 1e-9
          and abs(m["dodge_mult"] - 0.5) < 1e-9)

    # ── 4. pilot_combat_stats с состояниями боя ──
    uid = 571001
    await add_user(uid, "onhit1", "Испытатель", "")
    base = await pilot_combat_stats(uid)
    stunned = await pilot_combat_stats(uid, ["оглушён"])
    check("stats: атака ниже с оглушением",
          stunned["attack_mult"] < base["attack_mult"])
    check("stats: крит ниже с оглушением",
          stunned["crit_chance"] <= base["crit_chance"] * 0.5 + 1e-9)
    check("stats: уклонение ниже с оглушением",
          stunned["dodge"] < base["dodge"])

    # ── 5. DB: колонки, хелперы, миграция ──
    conn = await get_db()
    for table in ("dungeon_enemies", "forest_enemies", "fishing_enemies",
                  "mine_enemies", "logging_enemies"):
        cursor = await conn.execute(f"PRAGMA table_info({table})")
        cols = {r["name"] for r in await cursor.fetchall()}
        check(f"колонка on_hit_effects в {table}", "on_hit_effects" in cols)

    wolf = await get_source_enemy_by_key("forest", "white_wolf")
    check("волк: get хелпер видит кровотечение 30/3",
          any(e.get("kind") == "bleed"
              and int(e.get("chance") or 0) == FOREST_WHITE_WOLF_BLEED_CHANCE
              and int(e.get("dmg") or 0) == FOREST_WHITE_WOLF_BLEED_DMG
              for e in await get_source_enemy_on_hit_effects("forest", wolf["id"])))
    await set_source_enemy_on_hit_effects("forest", wolf["id"],
                                          [{"kind": "bleed", "chance": 10, "dmg": 1}])
    wolf_after = await get_source_enemy("forest", wolf["id"])
    check("волк: set сохранил JSON + admin_tuned=1",
          wolf_after["admin_tuned"] == 1
          and json.loads(wolf_after["on_hit_effects" or ""] or "[]")
          == [{"kind": "bleed", "chance": 10, "dmg": 1}])

    snake = await get_source_enemy_by_key("logging", "snake", spot="logging")
    check("змея: get хелпер видит яд 30/2",
          any(e.get("kind") == "poison"
              and int(e.get("chance") or 0) == LOGGING_SNAKE_POISON_CHANCE
              and int(e.get("dmg") or 0) == LOGGING_SNAKE_POISON_DMG
              for e in await get_source_enemy_on_hit_effects("logging", snake["id"])))
    owl = await get_source_enemy_by_key("logging", "owl", spot="logging")
    check("неясыть: ослепление 30% / 4 хода",
          any(e.get("kind") == "state" and e.get("key") == "ослеплён"
              and int(e.get("chance") or 0) == 30
              and int(e.get("rounds") or 0) == LOGGING_OWL_BLIND_ROUNDS
              for e in await get_source_enemy_on_hit_effects("logging", owl["id"])))

    dungeons = [d for d in await get_all_dungeons(training=False)]
    check("данж посеян", bool(dungeons))
    dungeon_enemies = await get_dungeon_enemies(dungeons[0]["id"])
    check("данж: у врагов есть on_hit_effects в строках",
          bool(dungeon_enemies) and all("on_hit_effects" in e
                                        for e in dungeon_enemies))
    d_id = dungeon_enemies[0]["id"]
    saved_eff = await get_enemy_on_hit_effects(d_id)
    await set_enemy_on_hit_effects(d_id, [{"kind": "frostbite", "chance": 25,
                                           "rounds": 4}])
    check("данж: set/get хелперы",
          await get_enemy_on_hit_effects(d_id)
          == [{"kind": "frostbite", "chance": 25, "rounds": 4}])
    await set_enemy_on_hit_effects(d_id, saved_eff)

    # Миграция legacy → JSON: строка с bleed_* и без on_hit_effects.
    cursor = await conn.execute(
        "INSERT INTO forest_enemies (key, spot, name, hp, dmg_min, dmg_max, "
        "bleed_chance, bleed_dmg, chance, pity_target, enabled, on_hit_effects) "
        "VALUES ('legacy_test', 'forest', 'Тестовый', 10, 1, 1, 40, 5, "
        "0, 0, 1, NULL)")
    await conn.commit()
    cursor = await conn.execute(
        "SELECT id FROM forest_enemies WHERE key = 'legacy_test'")
    legacy_id = (await cursor.fetchone())["id"]
    await _migrate_enemy_on_hit_effects()
    migrated = await get_source_enemy("forest", legacy_id)
    check("миграция: legacy bleed → JSON 40%/5",
          json.loads(migrated["on_hit_effects"] or "[]")
          == [{"kind": "bleed", "chance": 40, "dmg": 5}])
    check("миграция: идемпотентна",
          await _migrate_enemy_on_hit_effects() is None
          and json.loads((await get_source_enemy("forest", legacy_id))
                         ["on_hit_effects"] or "[]")
          == [{"kind": "bleed", "chance": 40, "dmg": 5}])
    await conn.execute("DELETE FROM forest_enemies WHERE id = ?", (legacy_id,))
    await conn.commit()

    # ── 7. process_item_use: блок расходников при оглушении ──
    consumables = await get_items_by_category("consumable")
    if consumables:
        potion = consumables[0]
        await add_inventory_item(uid, potion["id"], 1)
        onhit.register(uid, store := {"on_hit": {"оглушён": {"rounds_left": 2}}})
        ok, msg = await process_item_use(uid, potion["id"])
        check("расходник заблокирован оглушением",
              ok is False and "глуш" in (msg or "").lower())
        onhit.unregister(uid)
        ok2, msg2 = await process_item_use(uid, potion["id"])
        check("после unregister расходник доступен (не боевой блок)",
              "оглушён" not in (msg2 or ""))
    else:
        check("нашёлся consumable-предмет", False)

    # ── 8. Админ: общий редактор ──
    from bot.handlers import admin
    check("админ: _onhit_parse_params есть",
          hasattr(admin, "_onhit_parse_params"))
    check("админ: парсер «30 3»",
          admin._onhit_parse_params("30 3", "bleed")
          == {"kind": "bleed", "chance": 30, "dmg": 3})
    check("админ: парсер «15 4» для frostbite",
          admin._onhit_parse_params("15 4", "frostbite")
          == {"kind": "frostbite", "chance": 15, "rounds": 4})
    check("админ: парсер отклоняет мусор",
          admin._onhit_parse_params("abc", "bleed") is None
          and admin._onhit_parse_params("150 3", "bleed") is None)
    check("админ: _onhat_merge нет ошибки имени", hasattr(admin, "_onhit_merge"))
    merged = admin._onhit_merge(
        [{"kind": "bleed", "chance": 30, "dmg": 3}],
        {"kind": "state", "key": "оглушён", "chance": 20, "rounds": 3})
    check("админ: merge добавляет второй эффект", len(merged) == 2)
    merged2 = admin._onhit_merge(merged,
                                 {"kind": "bleed", "chance": 10, "dmg": 1})
    check("админ: merge заменяет того же kind", len(merged2) == 2
          and merged2[0]["chance"] == 10)
    check("админ: legacy-поля убраны из ENEMY_FIELDS",
          "bleed_chance" not in admin.ENEMY_FIELDS
          and "bleed_dmg" not in admin.ENEMY_FIELDS
          and "poison_chance" not in admin.ENEMY_FIELD_LABELS
          and "poison_dmg" not in admin.ENEMY_FIELD_LABELS)
    admin_src = inspect.getsource(admin)
    check("админ: колбэки редактора на месте",
          "enemy:effects:" in admin_src and "enemy:fx:src:" in admin_src
          and "enemy:fx:tog:" in admin_src and "enemy:fxt:" in admin_src)
    check("админ: FSM-состояния onhit_value",
          hasattr(admin.AdminDungeon, "onhit_value")
          and hasattr(admin.AdminEnemy, "onhit_value"))

    # ── 9. Боевые хендлеры подключены к onhit ──
    from bot.handlers import forest, dungeon, mine, logging_site
    for mod, name in ((forest, "forest"), (dungeon, "dungeon"),
                      (mine, "mine"), (logging_site, "logging")):
        src = inspect.getsource(mod)
        check(f"{name}: импортирует onhit", "from utils import onhit" in src
              or "import utils.onhit" in src)
        check(f"{name}: unregister при исходе боя", "onhit.unregister" in src)
    check("logging: tick_dots в хите", "onhit.tick_dots"
          in inspect.getsource(logging_site.logging_battle_hit))
    check("forest: tick_dots в хите", "onhit.tick_dots"
          in inspect.getsource(forest.forest_battle_hit))

    await close_db()
    print(f"\nSmoke 157: {passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    try:
        asyncio.run(run())
    except SystemExit:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        from database.db import close_db
        asyncio.run(close_db())
        print(f"SMOKE ERROR: {e!r}")
        sys.exit(1)
