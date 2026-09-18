"""Smoke v0.13.2: рынок обычных предметов (market_items, market_ok), менеджер дропов
врагов (item_id), описание/картинка врага через админку, категория «🎪 Рынок».

Запуск: .venv\\Scripts\\python.exe smoke_056.py
"""
import asyncio
import json
import os
import sys

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke056.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB

sys.path.insert(0, os.path.dirname(__file__))


async def run():
    from database.db import (
        init_db, close_db, seed_default_items, seed_dungeon,
        ensure_dungeon_shop_items, ensure_dungeon_enemy_drops, ensure_life_items,
        ensure_dungeon_reservoir_items, ensure_water_fish, ensure_kvp_award,
        ensure_market_license_item,
        add_user, get_user, add_item, get_item, get_item_by_name,
        place_item_offer, get_item_offers, get_item_offer, remove_item_offer,
        get_market_slots_info, count_user_market_offers,
        get_all_dungeons, get_dungeon_enemies, get_enemy, update_enemy_fields,
        get_enemy_drops, set_enemy_drops, add_enemy_drop, remove_enemy_drop,
        ENEMY_EDITABLE_FIELDS,
        start_dungeon_run, get_active_run,
    )
    from config import ITEM_CATEGORIES, MARKET_BASE_SLOTS
    from bot.handlers.admin import category_choice_markup
    from bot.handlers.shop import CATEGORIES, market_offer_items
    from bot.handlers.dungeon import roll_enemy_drops

    await init_db()
    await seed_default_items()
    await seed_dungeon()
    await ensure_dungeon_shop_items()
    await ensure_dungeon_enemy_drops()
    await ensure_life_items()
    await ensure_dungeon_reservoir_items()
    await ensure_water_fish()
    await ensure_kvp_award()
    await ensure_market_license_item()

    uid = 999901
    uid2 = 999902
    uid3 = 999903
    await add_user(uid, "tester", "Тест", "")
    await add_user(uid2, "tester2", "Тест2", "")
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

    # ── 1. items.market_ok ──
    item_a_id = await add_item(
        name="Рыночный артефакт", description="тест", price=200, sell_price=100,
        rarity=2, category="special", stock=-1, added_by=uid, market_ok=1)
    item_b_id = await add_item(
        name="Только скупщику", description="тест", price=50, sell_price=20,
        rarity=1, category="resource", stock=-1, added_by=uid)
    a = await get_item(item_a_id)
    b = await get_item(item_b_id)
    check("items.market_ok=1 для разрешённого", a is not None and a['market_ok'] == 1)
    check("items.market_ok=0 по умолчанию", b is not None and b['market_ok'] == 0)
    check("ENEMY_EDITABLE_FIELDS: description", "description" in ENEMY_EDITABLE_FIELDS)
    check("ENEMY_EDITABLE_FIELDS: image", "image" in ENEMY_EDITABLE_FIELDS)

    # ── 2. market_items офферы ──
    offer_id = await place_item_offer(uid, item_a_id, 130)
    check("place_item_offer вернул id", offer_id is not None and offer_id > 0)
    offs = await get_item_offers()
    check("get_item_offers нашёл оффер", len(offs) == 1 and offs[0]['name'] == "Рыночный артефакт")
    check("get_item_offers JOIN sell_price", offs and 'sell_price' in offs[0].keys())
    one = await get_item_offer(offer_id)
    check("get_item_offer: price 130", one is not None and one['price'] == 130)
    check("count_user_market_offers = 1", await count_user_market_offers(uid) == 1)
    slots = await get_market_slots_info(uid)
    check("slots: active_count = 1", slots['active_count'] == 1)
    check("slots: total = базовые", slots['total_slots'] == MARKET_BASE_SLOTS)
    check("remove_item_offer ok", await remove_item_offer(offer_id) is True)
    check("get_item_offer после удаления None", await get_item_offer(offer_id) is None)
    check("count_user_market_offers = 0", await count_user_market_offers(uid) == 0)

    # Лента «Рынок» видит предметный оффер
    await place_item_offer(uid, item_a_id, 115)
    mkt = await market_offer_items()
    check("market_offer_items видит предмет",
          any(i.get("__offer_type__") == "item" and i["name"] == "Рыночный артефакт"
              for i in mkt))
    check("рынок в CATEGORIES магазина", "market" in CATEGORIES)
    check("рынок в ITEM_CATEGORIES", ITEM_CATEGORIES.get("market") == "🎪 Рынок")
    # Админский выбор категории не предлагает «Рынок» (это витрина офферов, не категория товаров)
    mk = category_choice_markup()
    cat_cb = [b.callback_data for row in mk.inline_keyboard for b in row]
    check("мастер товара не предлагает cat:market", "cat:market" not in cat_cb)

    # ── 3. редактор врагов: описание + картинка ──
    combat_dngs = await get_all_dungeons(training=False)
    check("есть боевой данж", len(combat_dngs) > 0)
    dng_id = combat_dngs[0]['id']
    enemies = await get_dungeon_enemies(dng_id)
    rat = next((e for e in enemies if not e["is_boss"]), None)
    check("враг найден", rat is not None)
    if rat:
        rid = rat['id']
        check("update_enemy_fields description/image",
              await update_enemy_fields(rid, description="Хранитель подвала", image="AgAAfakefileid"))
        edited = await get_enemy(rid)
        check("description сохранён", edited['description'] == "Хранитель подвала")
        check("image сохранён (file_id)", edited['image'] == "AgAAfakefileid")
        check("admin_tuned поднят", edited['admin_tuned'] == 1)
        await ensure_dungeon_enemy_drops()
        synced = await get_enemy(rid)
        check("sync не перезаписал описание", synced['description'] == "Хранитель подвала")
        check("sync не перезаписал картинку", synced['image'] == "AgAAfakefileid")

    # ── 4. менеджер дропов (item_id, шанс, кол-во) ──
    if rat:
        rid = rat['id']
        base = await get_enemy_drops(rid)
        check("get_enemy_drops список", isinstance(base, list))
        await add_enemy_drop(rid, item_a_id, 0.5, 2)
        drops = await get_enemy_drops(rid)
        check("add_enemy_drop добавил item_id",
              any(d.get('item_id') == item_a_id and d['chance'] == 0.5 and d['qty'] == 2
                  for d in drops))
        before = len(drops)
        await add_enemy_drop(rid, item_a_id, 0.7, 3)  # тот же item_id → замена
        drops2 = await get_enemy_drops(rid)
        check("add_enemy_drop заменил существующий",
              len(drops2) == before and
              any(d.get('item_id') == item_a_id and d['chance'] == 0.7 and d['qty'] == 3
                  for d in drops2))
        idx = next(i for i, d in enumerate(drops2) if d.get('item_id') == item_a_id)
        check("remove_enemy_drop ok", await remove_enemy_drop(rid, idx) is True)
        check("remove_enemy_drop удалил",
              all(d.get('item_id') != item_a_id for d in await get_enemy_drops(rid)))

    # ── 5. roll_enemy_drops: item_id и фолбэк на имя ──
    if rat:
        rid = rat['id']
        await start_dungeon_run(uid2, dng_id)
        run2 = await get_active_run(uid2)
        check("забег uid2 создан", run2 is not None)
        await set_enemy_drops(rid, [{"item_id": item_a_id, "chance": 1.0, "qty": 2}])
        rolled = await roll_enemy_drops(run2['id'], await get_enemy(rid))
        check("roll по item_id вернул предмет",
              any(name == "Рыночный артефакт" and qty == 2 for name, qty in rolled))

        await start_dungeon_run(uid3, dng_id)
        run3 = await get_active_run(uid3)
        check("забег uid3 создан", run3 is not None)
        sig = await get_item_by_name("Сиг")
        check("Сиг существует для фолбэка", sig is not None)
        await set_enemy_drops(rid, [{"item": "Сиг", "chance": 1.0, "qty": 1}])
        rolled3 = await roll_enemy_drops(run3['id'], await get_enemy(rid))
        check("roll по имени (фолбэк)",
              any(name == "Сиг" and qty == 1 for name, qty in rolled3))

    await close_db()
    print(f"\nSmoke 056: {passed} passed, {failed} failed")
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