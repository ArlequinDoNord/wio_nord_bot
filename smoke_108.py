"""Smoke v0.18.15: единый редактор врагов + мутировавший моллюск в водохранилище.

Проверяем:
  * таблицы forest_enemies / fishing_enemies, сиды кабана и моллюска;
  * общий CRUD врагов источника (правка полей, дропы, вкл/выкл, создание, удаление);
  * боевые параметры из БД (лес читает кабана из БД, а не из конфига);
  * шанс встречи и гарантия (enemy_encounter_hit);
  * независимый ролл дропов — жемчужина 2% реально выпадает (roll_enemy_drops);
  * предметы добычи моллюска + рецепт «Жареное мясо моллюска»;
  * опушка — отдельная картинка (фото локации леса её не подменяет).

Запуск: .venv\\Scripts\\python.exe smoke_108.py
"""
import asyncio
import os
import sys

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke108.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB

sys.path.insert(0, os.path.dirname(__file__))


async def run():
    from config import FOREST_BOAR_SEED
    from database.db import (
        init_db, close_db, get_db, add_user, get_user,
        ensure_forest_items, ensure_forest_mushrooms, ensure_recipes,
        ensure_forest_enemies, ensure_fishing_enemies, ensure_mollusk_items,
        get_source_enemies, get_source_enemy, get_source_enemy_by_key,
        update_source_enemy, delete_source_enemy, add_source_enemy,
        get_source_enemy_drops, set_source_enemy_drops, add_source_enemy_drop,
        remove_source_enemy_drop, get_fishing_spots,
        roll_enemy_drops, enemy_encounter_hit, ENEMY_SOURCE_TABLES,
        get_item_by_name, get_item, get_recipes,
        remove_ap_or_floor,
    )
    from bot.handlers.forest import (
        _boar, _boar_fallback, _roll_boar_loot_items, _glade_media, _glade_path,
    )
    from bot.handlers.dungeon import (
        MOLLUSK_BATTLE, purge_mollusk_battle, MOLLUSK_BATTLE_TTL,
        _mollusk_loot,
    )

    passed = failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
            print(f"  ok  {name}")
        else:
            failed += 1
            print(f"FAIL  {name}")

    print("Smoke 108: враги (лес + рыбалка) и мутировавший моллюск\n")
    await init_db()

    # ── 1. Таблицы и источники ──
    conn = await get_db()
    check("источники врагов: лес и рыбалка",
          set(ENEMY_SOURCE_TABLES) == {"forest", "fishing"})
    check("forest_enemies — таблица создана",
          bool(await conn.execute("SELECT name FROM sqlite_master "
                                  "WHERE type='table' AND name='forest_enemies'")))
    check("fishing_enemies — таблица создана",
          bool(await conn.execute("SELECT name FROM sqlite_master "
                                  "WHERE type='table' AND name='fishing_enemies'")))

    # ── 2. Сиды ──
    check("сид леса добавил кабана", await ensure_forest_enemies() is True)
    check("повторный сид леса — не дублирует", await ensure_forest_enemies() is False)
    check("сид рыбалки добавил моллюска", await ensure_fishing_enemies() is True)
    check("повторный сид рыбалки — не дублирует", await ensure_fishing_enemies() is False)

    boar = await get_source_enemy_by_key("forest", "boar")
    check("кабан в БД по ключу 'boar'", bool(boar))
    check("кабан: имя из сида", boar and boar['name'] == FOREST_BOAR_SEED["name"])
    check("кабан: HP из сида", boar and boar['hp'] == FOREST_BOAR_SEED["hp"])
    check("кабан: урон мин/макс из сида",
          boar and (boar['dmg_min'], boar['dmg_max'])
          == (FOREST_BOAR_SEED["dmg_min"], FOREST_BOAR_SEED["dmg_max"]))
    check("кабан: гарантия 1/12", boar and boar['pity_target'] == 12)
    check("кабан: шанс встречи ≈ 8.33%", boar and 8 < boar['chance'] < 9)
    check("кабан: включён", boar and boar['enabled'] == 1)

    mollusk = await get_source_enemy_by_key("fishing", "mollusk", "reservoir")
    check("моллюск в БД по ключу 'mollusk'", bool(mollusk))
    check("моллюск: spot = reservoir", mollusk and mollusk['spot'] == "reservoir")
    check("моллюск: шанс встречи 4%", mollusk and float(mollusk['chance']) == 4.0)
    check("моллюск: потеря 12 ОД", mollusk and mollusk['loss_ap'] == 12)
    check("моллюск: урон 5–9", mollusk and (mollusk['dmg_min'], mollusk['dmg_max']) == (5, 9))

    # ── 3. Дропы сида (сид врага сам досоздаёт предметы — порядок вызовов не важен) ──
    boar_drops = await get_source_enemy_drops("forest", boar['id'])
    names = set()
    for d in boar_drops:
        item = await get_item(d['item_id'])
        names.add(item['name'])
    check("кабан: 3 дропа из сида", len(boar_drops) == 3)
    check("кабан: дропы — мясо/шкура/клык",
          names == {"Мясо кабана", "Шкура кабана", "Клык кабана"})
    check("кабан: шанс мяса 50%", abs(boar_drops[0]['chance'] - 0.5) < 0.001)

    await ensure_mollusk_items()
    mollusk_drops = await get_source_enemy_drops("fishing", mollusk['id'])
    mnames = set()
    for d in mollusk_drops:
        item = await get_item(d['item_id'])
        mnames.add(item['name'])
    check("моллюск: дропы мясо + жемчужина", mnames == {"Мясо моллюска", "Жемчужина"})
    pearl_id = (await get_item_by_name("Жемчужина"))['id']
    pearl = next(d for d in mollusk_drops if d['item_id'] == pearl_id)
    check("жемчужина — очень редко (2%)", abs(pearl['chance'] - 0.02) < 0.001)
    check("сумма шансов дропов ≤ 100%", sum(d['chance'] for d in mollusk_drops) <= 1.0)

    # ── 4. Предметы моллюска ──
    for iname in ("Мясо моллюска", "Жемчужина", "Жареное мясо моллюска"):
        it = await get_item_by_name(iname)
        check(f"предмет «{iname}» создан", bool(it))
        check(f"«{iname}» вне магазина (is_available=0)",
              it and (await get_item(it['id']))['is_available'] == 0)
    pearl_item = await get_item_by_name("Жемчужина")
    check("жемчужина продаётся (sell_price > 0)", pearl_item['sell_price'] > 0)
    # Прямой лут врага — только с врага: вне магазина, вне рынка игроков, loot_only.
    for iname in ("Мясо моллюска", "Жемчужина", "Мясо кабана", "Шкура кабана", "Клык кабана"):
        full = await get_item((await get_item_by_name(iname))['id'])
        check(f"«{iname}» только лут: market_ok=0 и loot_only=1",
              full['market_ok'] == 0 and (full['loot_only'] or 0) == 1)
    fried_full = await get_item((await get_item_by_name("Жареное мясо моллюска"))['id'])
    check("жареное мясо моллюска (крафт) остаётся торгуемым", fried_full['market_ok'] == 1)
    fried = await get_item_by_name("Жареное мясо моллюска")
    check("жареное мясо лечит 26 HP", fried['heal'] == 26)
    await ensure_recipes()
    mollusk_recipes = [r for r in await get_recipes() if r['name'] == "Жареное мясо моллюска"]
    check("рецепт «Жареное мясо моллюска» есть", bool(mollusk_recipes))
    check("рецепт: кухня, ур. 2",
          bool(mollusk_recipes) and mollusk_recipes[0]['required_expansion'] == "kitchen"
          and mollusk_recipes[0]['required_level'] == 2)
    check("рецепт: результат — жареное мясо моллюска",
          bool(mollusk_recipes)
          and mollusk_recipes[0]['result_item_name'] == "Жареное мясо моллюска")

    # ── 5. CRUD врага ──
    new_id = await add_source_enemy("fishing", spot="reservoir", name="Тестовый моллюск",
                                    hp=10, dmg_min=1, dmg_max=2, dodge=5,
                                    chance=7.5, loss_ap=3, drops=[])
    check("создан враг рыбалки", bool(new_id))
    check("новый враг виден в списке",
          any(e['id'] == new_id for e in await get_source_enemies("fishing", "reservoir")))
    await update_source_enemy("fishing", new_id, hp=42, chance=9.0)
    updated = await get_source_enemy("fishing", new_id)
    check("правка HP и шанса", updated['hp'] == 42 and float(updated['chance']) == 9.0)
    check("правка помечает admin_tuned", updated['admin_tuned'] == 1)
    check("чужое поле игнорируется",
          await update_source_enemy("fishing", new_id, hp=1) is True
          and await update_source_enemy("fishing", new_id, sql="drop") is False)

    await add_source_enemy_drop("fishing", new_id, pearl_item['id'], 0.25, 2)
    drops = await get_source_enemy_drops("fishing", new_id)
    check("дроп добавлен (шанс 25%, ×2)",
          len(drops) == 1 and abs(drops[0]['chance'] - 0.25) < 0.001 and drops[0]['qty'] == 2)
    await add_source_enemy_drop("fishing", new_id, pearl_item['id'], 0.5, 1)
    drops = await get_source_enemy_drops("fishing", new_id)
    check("повторный дроп заменяет шанс, а не дублирует",
          len(drops) == 1 and abs(drops[0]['chance'] - 0.5) < 0.001)
    check("удаление дропа", await remove_source_enemy_drop("fishing", new_id, 0) is True)
    check("удаление несуществующего дропа — False",
          await remove_source_enemy_drop("fishing", new_id, 5) is False)
    await set_source_enemy_drops("fishing", new_id, [])
    check("список дропов очищен", await get_source_enemy_drops("fishing", new_id) == [])

    await update_source_enemy("fishing", new_id, enabled=0)
    check("выключенный враг не попадает в enabled_only",
          new_id not in {e['id'] for e in await get_source_enemies("fishing", "reservoir",
                                                                   enabled_only=True)})
    check("удаление врага", await delete_source_enemy("fishing", new_id) is True)
    check("удалённого врага нет", await get_source_enemy("fishing", new_id) is None)

    spots = await get_fishing_spots()
    check("список водоёмов с врагами: reservoir",
          [s['spot'] for s in spots] == ["reservoir"])
    check("в водоёме один враг", spots and spots[0]['c'] == 1)

    # ── 6. Лес читает параметры кабана из БД ──
    await ensure_forest_items()
    await ensure_forest_mushrooms()
    boar_db = await _boar()
    check("лес: кабан прочитан из БД", boar_db and boar_db.get('id') == boar['id'])
    check("лес: HP кабана из БД", boar_db['hp'] == boar['hp'])
    await update_source_enemy("forest", boar['id'], hp=55)
    boar_db2 = await _boar()
    check("лес: видна правка HP админом (30 → 55)", boar_db2['hp'] == 55)
    check("лес: фолбэк совпадает с конфигом",
          _boar_fallback()['hp'] == FOREST_BOAR_SEED['hp'])
    # опушка — отдельная картинка, фото локации (вход в лес) ей не подменяется
    photo_id, media_path = await _glade_media()
    check("опушка: фото локации (входа в лес) не используется", photo_id is None)
    check("опушка: берётся локальный файл", media_path == _glade_path())
    check("опушка: файл на диске", os.path.isfile(media_path))
    await update_source_enemy("forest", boar['id'], enabled=0)
    check("лес: выключенный кабан не встречается", await _boar() is None)
    await update_source_enemy("forest", boar['id'], enabled=1, hp=30)

    # ── 7. Шанс встречи и гарантия ──
    check("встреча: шанс 50% и бросок 10 → да", enemy_encounter_hit(50, 10))
    check("встреча: шанс 50% и бросок 90 → нет", not enemy_encounter_hit(50, 90))
    check("встреча: шанс 0% → никогда (без гарантии)", not enemy_encounter_hit(0, 0))
    check("гарантия: 11 попыток из 12 → встреча", enemy_encounter_hit(0, 99, 11, 12))
    check("гарантия: 3 попытки из 12 → обычно нет", not enemy_encounter_hit(0, 99, 3, 12))

    # ── 8. Ролл дропов: каждый дроп бросается независимо (как в данжах) ──
    check("ролл: шанс 30% — попал (0.1)", len(roll_enemy_drops([{"item_id": 1, "chance": 0.3}],
                                                                [0.1])) == 1)
    check("ролл: шанс 30% — не попал (0.5)",
          roll_enemy_drops([{"item_id": 1, "chance": 0.3}], [0.5]) == [])
    check("ролл: пустой список дропов", roll_enemy_drops([], []) == [])
    check("ролл: 100% — дроп выпал",
          len(roll_enemy_drops([{"item_id": 1, "chance": 1.0}], [0.99])) == 1)
    both = roll_enemy_drops([{"item_id": 1, "chance": 0.5}, {"item_id": 2, "chance": 0.2}],
                            [0.1, 0.1])
    check("ролл: оба дропа выпали одновременно", len(both) == 2)
    # ключевая проверка: жемчужина 2% достижима, а не затенена мясом 70%
    pearl_pick = roll_enemy_drops(mollusk_drops, [0.9, 0.01])
    check("ролл: жемчужина 2% достижима (мясо не сработало)", len(pearl_pick) == 1
          and pearl_pick[0]['item_id'] == pearl_id)
    check("ролл: оба дропа моллюска разом", len(roll_enemy_drops(mollusk_drops, [0.0, 0.0])) == 2)
    check("ролл: ни одного дропа", roll_enemy_drops(mollusk_drops, [0.99, 0.99]) == [])

    # _roll_boar_loot_items сам бросает кубики (в database.db.roll_enemy_drops),
    # поэтому подменяем random.random — иначе проверки флакуют (50/20/10%).
    # Значения выдаются по одному на бросок: мясо, шкура, клык.
    def _seq_factory(values):
        it = iter(list(values) + [0.99] * 10)

        def _next():
            return next(it)
        return _next

    from unittest.mock import patch
    with patch("random.random", _seq_factory([0.1, 0.9, 0.9])):
        looted = await _roll_boar_loot_items(boar_db)
    check("лес: добыча мяса (50%)", looted == ["Мясо кабана"])
    with patch("random.random", _seq_factory([0.6, 0.1, 0.9])):
        looted = await _roll_boar_loot_items(boar_db)
    check("лес: шкура (20%) достижима и не затенена мясом", looted == ["Шкура кабана"])
    with patch("random.random", _seq_factory([0.9, 0.9, 0.05])):
        looted = await _roll_boar_loot_items(boar_db)
    check("лес: клык (10%) достижим", looted == ["Клык кабана"])
    with patch("random.random", _seq_factory([0.1, 0.9, 0.01])):
        looted = await _roll_boar_loot_items(boar_db)
    check("лес: мясо и клык выпали разом", looted == ["Мясо кабана", "Клык кабана"])
    with patch("random.random", _seq_factory([0.99])):
        looted = await _roll_boar_loot_items(boar_db)
    check("лес: победа без добычи", looted == [])

    # ── 9. Бой моллюска: очистка зависших записей ──
    MOLLUSK_BATTLE[86001] = {"token": "1", "started_at": 0, "enemy": {}}
    purge_mollusk_battle()
    check("бой моллюска: старый бой снят по TTL", 86001 not in MOLLUSK_BATTLE)
    MOLLUSK_BATTLE[86002] = {"token": "2", "started_at": 10 ** 12, "enemy": {}}
    purge_mollusk_battle()
    check("бой моллюска: свежий бой жив", 86002 in MOLLUSK_BATTLE)
    check("TTL боя — 15 минут", MOLLUSK_BATTLE_TTL == 900)
    MOLLUSK_BATTLE.clear()

    # ── 10. Поражение моллюска: −12 ОД, но не ниже нуля ──
    await add_user(86010, "mollusk_loser", "Новичок", "")
    conn = await get_db()
    await conn.execute("UPDATE users SET ap = 30 WHERE user_id = 86010")
    await conn.commit()
    check("−12 ОД при 30 ОД", await remove_ap_or_floor(86010, 12) == 12)
    check("осталось 18 ОД", (await get_user(86010))['ap'] == 18)
    await conn.execute("UPDATE users SET ap = 5 WHERE user_id = 86010")
    await conn.commit()
    check("−12 ОД при 5 ОД: списано 5", await remove_ap_or_floor(86010, 12) == 5)
    check("ОД не ушли в минус", (await get_user(86010))['ap'] == 0)

    # ── 11. Победный лут моллюска: ролл идёт из database.db — без TypeError ──
    with patch("random.random", lambda: 0.1):
        loot_line = await _mollusk_loot(86010, mollusk)
    check("моллюск: победный лут не падает (мена в инвентарь)",
          isinstance(loot_line, str) and "Мясо моллюска" in loot_line)

    await close_db()
    print(f"\nSmoke 108: {passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    try:
        asyncio.run(run())
    except SystemExit:
        raise
    except Exception as e:
        import traceback
        from database.db import close_db
        traceback.print_exc()
        print(f"\nSMOKE ERROR: {type(e).__name__}: {e}")
        try:
            asyncio.run(close_db())
        except Exception:
            pass
        sys.exit(1)
