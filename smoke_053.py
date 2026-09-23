"""Запуск: venv python smoke_053.py"""
import asyncio
import time
import sys
import os

# Используем изолированную БД для тестов: свежая с каждого запуска
_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke053.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB

sys.path.insert(0, os.path.dirname(__file__))


async def run():
    from database.db import (
        init_db, get_db, close_db, seed_default_items, seed_dungeon,
        ensure_dungeon_shop_items, ensure_dungeon_enemy_drops, ensure_life_items,
        ensure_recipes, add_item, get_item_by_name,
        get_inventory_item, add_inventory_item, remove_inventory_item,
        get_inventory, get_ingredient_map, consume_ingredient,
        remove_fish_catches_by_name, add_fish_catch, get_fish_catches,
    )

    await init_db()
    await seed_default_items()
    await seed_dungeon()
    await ensure_dungeon_shop_items()
    await ensure_dungeon_enemy_drops()
    await ensure_life_items()
    await ensure_recipes()

    uid = 999901
    passed = 0
    failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
        else:
            failed += 1
            print(f"  FAIL: {name}")

    from database.db import add_user
    await add_user(uid, "tester", "Тест", "")
    await add_user(999902, "tester2", "Тест", "")

    # ── 1. get_ingredient_map: инвентарь + уловы ──
    sig = await get_item_by_name("Сиг")
    check("get_item_by_name(Sig)", sig is not None)

    await add_inventory_item(uid, sig["id"], 2)
    inv = await get_inventory_item(uid, sig["id"])
    check("inventory has 2 Сиг", inv and inv["quantity"] == 2)

    catches = await get_fish_catches(uid)
    check("no catches initially", len(catches) == 0)

    await add_fish_catch(uid, sig["id"], 1)  # weight=1
    await add_fish_catch(uid, sig["id"], 2)  # weight=2

    iamap = await get_ingredient_map(uid)
    check("ingredient_map Сиг = 2(inv) + 2(catch) = 4", iamap.get("Сиг") == 4)

    # ── 2. consume_ingredient: сначала инвентарь, потом уловы ──
    ok = await consume_ingredient(uid, "Сиг", 2)
    check("consume 2 Сиг from inventory", ok)

    inv = await get_inventory_item(uid, sig["id"])
    check("inventory depleted (quantity or gone)", not inv or inv["quantity"] == 0)

    iamap = await get_ingredient_map(uid)
    check("after consume 2: remaining 2 in catches", iamap.get("Сиг") == 2)

    ok = await consume_ingredient(uid, "Сиг", 1)
    check("consume 1 Сиг from catches", ok)

    iamap = await get_ingredient_map(uid)
    check("after consume 1: remaining 1", iamap.get("Сиг") == 1)

    ok = await consume_ingredient(uid, "Сиг", 1)
    check("consume last Сиг from catches", ok)

    iamap = await get_ingredient_map(uid)
    check("all Сиг consumed", iamap.get("Сиг", 0) == 0)

    ok = await consume_ingredient(uid, "Сиг", 1)
    check("consume Сиг when none -> False", not ok)

    # ── 3. remove_fish_catches_by_name ──
    await add_fish_catch(uid, sig["id"], 3)
    await add_fish_catch(uid, sig["id"], 1)
    ok = await remove_fish_catches_by_name(uid, "Сиг", 2)
    check("remove 2 Сиг catches", ok)
    catches = await get_fish_catches(uid)
    remaining = sum(1 for c in catches if c["name"] == "Сиг")
    check("0 Сиг catch remains", remaining == 0)

    ok = await remove_fish_catches_by_name(uid, "Сиг", 2)
    check("remove 2 Сиг when only 1 -> False", not ok)

    # ── 4. rename Кадка миграция ──
    conn = await get_db()
    await conn.execute(
        "INSERT INTO items (name, description, price, sell_price, rarity, category, "
        "stock, ap_cost, damage, heal, is_available, required_status) "
        "VALUES (?, '', 0, 0, 1, 'furniture', -1, 0, 0, 0, 1, '')",
        ("Кадка с растением",)
    )
    await conn.commit()
    await ensure_life_items()
    cursor = await conn.execute(
        "SELECT COUNT(*) as c FROM items WHERE name = 'Кадка с растением'"
    )
    old_count = (await cursor.fetchone())["c"]
    cursor = await conn.execute(
        "SELECT COUNT(*) as c FROM items WHERE name = 'Кадка для растений'"
    )
    new_count = (await cursor.fetchone())["c"]
    check("old name Кадка с растением count = 0", old_count == 0)
    check("new name Кадка для растений count >= 1", new_count >= 1)

    # ── 5. housing.city:menu ──
    from bot.handlers.housing import housing_menu
    import inspect
    src = inspect.getsource(housing_menu)
    check("city:menu in housing_menu", "city:menu" in src)

    # ── 6. fishing token guard ──
    from bot.handlers import fishing as F
    uid_f = 999902

    class FakeCb:
        def __init__(self, data_str, user_id):
            self.data = data_str
            self.from_user = type("U", (), {"id": user_id})()

        async def answer(self, text="", show_alert=False):
            pass

    # no token -> guard rejects
    cb = FakeCb("fish:cast:123456", uid_f)
    check("no token -> _fish_ok False", not await F._fish_ok(cb))

    F.FISH_TOKEN[uid_f] = "999999"
    cb = FakeCb("fish:cast:999999", uid_f)
    check("correct token -> _fish_ok True", await F._fish_ok(cb))

    cb = FakeCb("fish:cast:000000", uid_f)
    check("wrong token -> _fish_ok False", not await F._fish_ok(cb))

    cb = FakeCb("fish:bait:set:999999:worms", uid_f)
    check("bait:set with correct token", await F._fish_ok(cb))

    cb = FakeCb("fish:bait:set:000000:worms", uid_f)
    check("bait:set wrong token", not await F._fish_ok(cb))

    # deactivate clears token
    await F.deactivate_fishing(uid_f)
    cb = FakeCb("fish:cast:999999", uid_f)
    check("after deactivate -> _fish_ok False", not await F._fish_ok(cb))

    # ── 7. inventory categories import ──
    from bot.handlers.inventory import inv_categories_markup, FISH_ALL_KEY
    markup = inv_categories_markup([], [{"name":"Сиг","item_id":1,"weight":1,"rarity":1}])
    btn_texts = [b.text for row in markup.inline_keyboard for b in row]
    check("fish category present in markup", any("Улов" in t for t in btn_texts))

    # ── 8. семена: покупка и продажа через реального хендлера ──
    from database.db import add_nordmarks, get_available_items, get_status_by_tag, grant_status
    from bot.handlers import shop as SH

    pilot_st = await get_status_by_tag("pilot2")
    if pilot_st:
        await grant_status(uid, pilot_st["id"], 0)

    seed_item = await get_item_by_name("Яблочное семечко")
    check("seed item exists", seed_item is not None)
    check("seed is available", seed_item["is_available"] == 1)
    seed_id = seed_item["id"]

    class SeedCb:
        def __init__(self, uid):
            self.from_user = type("U", (), {"id": uid})()
            self.sent = []
            self.message = type("M", (), {
                "chat": type("C", (), {"id": uid})(),
                "photo": None,
            })()
            self.message.answer = self._answer
            self.message.edit_text = self._edit
            self.message.delete = self._delete
            self.message.answer_photo = self._answer_photo
            self.answered = []

        async def _answer(self, *a, **k):
            self.sent.append((a, k))

        async def _edit(self, text, reply_markup=None, **k):
            self.sent.append((text, reply_markup))

        async def _delete(self, *a, **k):
            self.sent.append(("DELETED", None))

        async def _answer_photo(self, *a, **k):
            self.sent.append(("PHOTO", a, k))

        async def answer(self, text="", show_alert=False):
            self.answered.append((text, show_alert))

    # покупка: даём деньги и вызываем _buy_item напрямую
    await add_nordmarks(uid, 1000, "test", "seed test")
    cb = SeedCb(uid)
    await SH._buy_item(cb, seed_id, 1)
    inv = await get_inventory_item(uid, seed_id)
    check("seed bought -> in inventory", inv and inv["quantity"] >= 1)
    check("buy success -> callback.answer() called", len(cb.answered) >= 1 and cb.answered[0][0] == "")
    cb2 = SeedCb(uid)
    await SH._buy_item(cb2, seed_id, 1)
    inv = await get_inventory_item(uid, seed_id)
    check("seed bought twice -> quantity 2", inv and inv["quantity"] == 2)

    # продажа: предмет есть -> продаётся
    from bot.handlers.inventory import _sell_item
    cb4 = SeedCb(uid)
    await _sell_item(cb4, seed_id, 1)
    check("sell success -> callback.answer() called", len(cb4.answered) >= 1 and cb4.answered[0][0] == "")
    inv = await get_inventory_item(uid, seed_id)
    check("seed sold -> quantity 1 remains", inv and inv["quantity"] == 1)

    # продажа стэка через подтверждение: регрессия v0.11.14 (распаковка split в inv_sell_ok)
    from bot.handlers.inventory import inv_sell, inv_sell_ok
    await add_inventory_item(uid, seed_id, 2)
    cb6 = SeedCb(uid)
    cb6.data = f"inv_sell:{seed_id}"
    await inv_sell(cb6)
    inv = await get_inventory_item(uid, seed_id)
    check("sell stack -> confirm shown, qty unchanged", inv and inv["quantity"] == 3 and any("Продать" in s[0] for s in cb6.sent))
    cb7 = SeedCb(uid)
    cb7.data = f"inv_sell_ok:{seed_id}:3"
    await inv_sell_ok(cb7)
    inv = await get_inventory_item(uid, seed_id)
    check("sell stack confirm -> all sold", inv is None or inv["quantity"] == 0)
    check("sell stack -> receipt sent", len(cb7.sent) >= 1 and any("продал" in s[0].lower() for s in cb7.sent))

    # продажа предмета, один экземпляр которого надет: продаются только лишние
    from database.db import set_equipment_slot, get_equipment
    from bot.handlers.inventory import _render_item_card
    cloak_id = await add_item("Плащ защища", "тест", 0, 60, 2, "equipment", -1, uid,
                              armor=2, equip_slot="body")
    await add_inventory_item(uid, cloak_id, 4)
    await set_equipment_slot(uid, "body", cloak_id)

    cardc = SeedCb(uid)
    await _render_item_card(cardc.message, uid, cloak_id)
    btn_texts = [b.text for row in cardc.sent[-1][1].inline_keyboard for b in row]
    check("card sell-all label (3) when 1 of 4 equipped",
          any("Продать всё (3)" in t for t in btn_texts) and
          not any(t.startswith("Продать всё") and " (4)" in t for t in btn_texts))

    cbx = SeedCb(uid)
    await _sell_item(cbx, cloak_id, 4)
    inv = await get_inventory_item(uid, cloak_id)
    check("sell all 4 with one equipped -> blocked, qty stays 4",
          inv and inv["quantity"] == 4 and any("используется" in a[0] for a in cbx.answered))

    cby = SeedCb(uid)
    await _sell_item(cby, cloak_id, 3)
    inv = await get_inventory_item(uid, cloak_id)
    eq = await get_equipment(uid)
    check("sell 3 of equipped stack -> 1 left, still equipped",
          inv and inv["quantity"] == 1 and eq.get("body") == cloak_id and
          not any("используется" in a[0] for a in cby.answered))

    cbz = SeedCb(uid)
    await _sell_item(cbz, cloak_id, 1)
    check("last equipped copy unsellable",
          any("используется" in a[0] for a in cbz.answered))

    # продажа без предмета -> alert (не проглатывается)
    await remove_inventory_item(uid, seed_id, 1)
    cb5 = SeedCb(uid)
    await _sell_item(cb5, seed_id, 1)
    check("sell none -> alert text set",
          len(cb5.answered) == 1 and cb5.answered[0][0] and cb5.answered[0][1] is True)
    check("sell none -> NO silent callback.answer()", not (cb5.answered and cb5.answered[0][0] == ""))

    # ===== Подземелья: колонки фото + update_dungeon_photos =====
    from database.db import get_all_dungeons, get_dungeon, update_dungeon_photos
    dgns = await get_all_dungeons()
    check("dungeons seeded", len(dgns) >= 1)
    dng_id = dgns[0]["id"]
    dng = await get_dungeon(dng_id)
    check("dungeon has photo columns", all(f"photo_{k}" in dng.keys() for k in ("dawn", "day", "sunset", "night")))
    check("dungeon photo slots initially empty", not any(dng[f"photo_{k}"] for k in ("dawn", "day", "sunset", "night")))
    ok = await update_dungeon_photos(dng_id, {"day": "FILE_DAY_123"})
    dng = await get_dungeon(dng_id)
    check("update_dungeon_photos day", ok and dng["photo_day"] == "FILE_DAY_123")
    check("update_dungeon_photos others unchanged", dng["photo_dawn"] is None and dng["photo_night"] is None)
    await update_dungeon_photos(dng_id, {"dawn": "FILE_DAWN_1", "sunset": None})
    dng = await get_dungeon(dng_id)
    check("update_dungeon_photos multi", dng["photo_dawn"] == "FILE_DAWN_1" and dng["photo_day"] == "FILE_DAY_123")
    ok = await update_dungeon_photos(dng_id, {"day": None})
    dng = await get_dungeon(dng_id)
    check("update_dungeon_photos clear day", ok and dng["photo_day"] is None)
    ok = await update_dungeon_photos(999999, {"day": "X"})
    check("update_dungeon_photos unknown id -> False", ok is False)

    # dungeon_entrance_photo: возвращает file_id текущего времени суток
    from bot.handlers.dungeon import dungeon_entrance_photo
    await update_dungeon_photos(dng_id, {"dawn": "PD", "day": "PD", "sunset": "PD", "night": "PD"})
    dng = await get_dungeon(dng_id)
    check("dungeon_entrance_photo returns file_id", bool(dungeon_entrance_photo(dng)))

    # ===== Банк: локация в городе + лимит туриста =====
    from database.db import user_is_tourist, get_all_locations
    from config import TOURIST_BALANCE_LIMIT
    check("TOURIST_BALANCE_LIMIT == 200", TOURIST_BALANCE_LIMIT == 200)
    locs = await get_all_locations()
    check("bank location seeded", any(l["key"] == "bank" for l in locs))
    bank_loc = next((l for l in locs if l["key"] == "bank"), None)
    check("bank location access for all", bank_loc and bank_loc["access_mode"] == "all")
    check("uid (pilot) not tourist", not await user_is_tourist(uid))
    tourist_st = await get_status_by_tag("tourist")
    if tourist_st:
        await grant_status(999902, tourist_st["id"], 0)
    check("uid_t (tourist) is tourist", await user_is_tourist(999902))
    from bot.handlers.bank import bank_menu_text
    ttext = await bank_menu_text(999902)
    check("bank_menu_text tourist shows limit", "200" in ttext and "🗺" in ttext)
    ptext = await bank_menu_text(uid)
    check("bank_menu_text pilot hides limit", "🗺" not in ptext)

    # ===== К.В.П.: тренировочный данж, предметы, награда, прогресс =====
    from database.db import (
        seed_kvp, ensure_kvp_items, ensure_kvp_award, get_kvp_dungeon,
        get_kvp_progress, increment_kvp_completions, mark_kvp_badge,
        mark_kvp_stick, user_has_award_name, grant_award,
        get_all_awards, get_all_dungeons,
    )
    kvp_dng_id = await seed_kvp()
    check("kvp dungeon seeded", kvp_dng_id is not None)
    kvp_dng = await get_kvp_dungeon()
    check("get_kvp_dungeon found", kvp_dng is not None)
    if kvp_dng:
        check("kvp dungeon is_training", kvp_dng["is_training"] == 1)

    combat_dngs = await get_all_dungeons(training=False)
    train_dngs = await get_all_dungeons(training=True)
    check("combat dungeons exclude training", all(not d["is_training"] for d in combat_dngs))
    check("training dungeons exist", len(train_dngs) >= 1)

    await ensure_kvp_items()
    stick = await get_item_by_name("Офицерский стек")
    check("Офицерский стек created", stick is not None)
    if stick:
        check("Офицерский стек weapon dmg=2", (stick["damage"] or 0) == 2)

    await ensure_kvp_award()
    awards = await get_all_awards()
    badge = next((a for a in awards if a["name"] == "Значок В.У.С.П."), None)
    check("Значок В.У.С.П. award created", badge is not None)

    prog = await get_kvp_progress(uid)
    check("kvp progress zeros", prog["completions"] == 0 and prog["badge_awarded"] == 0)
    await increment_kvp_completions(uid)
    prog = await get_kvp_progress(uid)
    check("kvp completions incremented", prog["completions"] == 1)
    await mark_kvp_badge(uid)
    prog = await get_kvp_progress(uid)
    check("kvp badge marked", prog["badge_awarded"] == 1)
    await mark_kvp_stick(uid)
    prog = await get_kvp_progress(uid)
    check("kvp stick marked", prog["stick_dropped"] == 1)

    if badge:
        granted, _ = await grant_award(uid, badge["id"], 0, "smoke")
        check("grant badge works", granted)
    check("user_has_award_name badge", await user_has_award_name(uid, "Значок В.У.С.П."))
    check("user_has_award_name other -> False", not await user_has_award_name(uid, "Нет такой"))

    # ===== Описание нашивки «Значок В.У.С.П.» =====
    badge = next((a for a in awards if a["name"] == "Значок В.У.С.П."), None)
    if badge:
        check("badge desc has +2% dmg", "+2% урона" in (badge["description"] or ""))
        check("badge desc has +3% dodge", "+3% уклонения" in (badge["description"] or ""))

    # ===== Админ-редактор врагов: правка + защита от стартовой синхронизации =====
    import json as _json
    from database.db import (
        get_floor_enemies, get_dungeon_enemies, get_enemy, update_enemy_fields,
    )
    combat_dngs = await get_all_dungeons(training=False)
    enemies_before = await get_dungeon_enemies(combat_dngs[0]["id"]) if combat_dngs else []
    rat = next((e for e in enemies_before if not e["is_boss"] and e["name"] == "Крыса"), None)
    check("editor: Крыса found", rat is not None)
    if rat:
        check("editor: set hp/dodge", await update_enemy_fields(rat["id"], hp=99, dodge=42))
        edited = await get_enemy(rat["id"])
        check("editor: hp=99 persisted", edited["hp"] == 99)
        check("editor: dodge=42 persisted", edited["dodge"] == 42)
        check("editor: admin_tuned=1", edited["admin_tuned"] == 1)
        # стартовая синхронизация НЕ должна перезаписать отредактированного врага
        await ensure_dungeon_enemy_drops()
        fresh = await get_enemy(rat["id"])
        check("editor: sync keeps hp=99", fresh["hp"] == 99)
        check("editor: sync keeps dodge=42", fresh["dodge"] == 42)
        check("editor: drops set", await update_enemy_fields(
            rat["id"], drops=[{"item": "Хвост крысы", "chance": 0.5, "qty": 2}]))
        fresh = await get_enemy(rat["id"])
        dropped = _json.loads(fresh["drops"]) if fresh["drops"] else []
        check("editor: drops stored", dropped and dropped[0]["item"] == "Хвост крысы"
              and dropped[0]["chance"] == 0.5 and dropped[0]["qty"] == 2)
        # К.В.П.: правка Ефрейтора и повторный seed_kvp не трогает его
        efreitor = next((e for e in await get_dungeon_enemies(kvp_dng_id)
                         if not e["is_boss"] and e["name"] == "Ефрейтор"), None)
        check("editor: Ефрейтор found", efreitor is not None)
        if efreitor:
            await update_enemy_fields(efreitor["id"], hp=77, dodge=33)
            await seed_kvp()
            fresh = await get_enemy(efreitor["id"])
            check("editor: kvp sync keeps hp=77", fresh["hp"] == 77)
            check("editor: kvp sync keeps dodge=33", fresh["dodge"] == 33)


    await close_db()

    # Очистка тестовой БД
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
    res = asyncio.run(run())
    sys.exit(1 if res else 0)