"""Smoke v0.13.3: весь улов рыбалки в fish_catches (kind: fish/resource),
ресурсы-находки без срока годности; тип и рынок в админке водоёма;
находки «Использовать»; дефолт market_ok=1 для рыбы; миграция легаси-мусора.

Запуск: .venv\\Scripts\\python.exe smoke_057.py
"""
import asyncio
import os
import sys

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke057.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB

sys.path.insert(0, os.path.dirname(__file__))


async def run():
    from database.db import (
        init_db, close_db, seed_default_items, seed_dungeon,
        ensure_dungeon_shop_items, ensure_dungeon_enemy_drops, ensure_life_items,
        ensure_dungeon_reservoir_items, ensure_water_fish, ensure_kvp_award,
        ensure_market_license_item, migrate_legacy_junk,
        add_user, get_item, get_item_by_name,
        add_fish_catch, get_fish_catches, get_db,
        update_water_fish_field, get_water_fish_kind, get_water_fish_candidates,
        get_water_fish_row, add_water_fish,
        add_inventory_item, get_inventory_item,
    )
    from bot.handlers.inventory import _fish_groups, inv_list_markup

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

    uid = 999904
    uid2 = 999905
    await add_user(uid, "tester", "Тест", "")
    await add_user(uid2, "tester2", "Тест2", "")

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

    # ── 1. колонки kind в fish_catches и water_fish ──
    for table in ("fish_catches", "water_fish"):
        cols = [r['name'] for r in await (await conn.execute(
            f"PRAGMA table_info({table})")).fetchall()]
        check(f"{table}.kind есть", "kind" in cols)

    # ── 2. улов ресурса: без срока годности ──
    boot = await get_item_by_name("Старый сапог")
    weed = await get_item_by_name("Кусочек водорослей")
    sig = await get_item_by_name("Сиг")
    check("сапог существует (категория resource)", boot is not None
          and boot['category'] == 'resource')
    check("водоросли — расходник +1 ОД", weed is not None
          and weed['category'] == 'consumable' and weed['ap_cost'] == 1)
    check("сиг существует (категория fishing)", sig is not None
          and sig['category'] == 'fishing')

    boot_cid = await add_fish_catch(uid, boot['id'], 1, kind="resource")
    weed_cid = await add_fish_catch(uid, weed['id'], 1, kind="resource")
    sig_cid = await add_fish_catch(uid, sig['id'], 1)  # kind по умолчанию = fish
    row_boot = await (await conn.execute(
        "SELECT expires_at, kind FROM fish_catches WHERE id = ?", (boot_cid,))).fetchone()
    row_sig = await (await conn.execute(
        "SELECT expires_at, kind FROM fish_catches WHERE id = ?", (sig_cid,))).fetchone()
    check("ресурс: kind=resource, expires NULL",
          row_boot['kind'] == 'resource' and row_boot['expires_at'] is None)
    check("рыба: kind=fish, expires задан",
          row_sig['kind'] == 'fish' and row_sig['expires_at'] is not None)

    catches = await get_fish_catches(uid)
    c = next((x for x in catches if x['id'] == boot_cid), None)
    check("get_fish_catches отдаёт kind ресурса",
          c is not None and c['kind'] == 'resource' and c['remaining_sec'] == 0)
    c2 = next((x for x in catches if x['id'] == sig_cid), None)
    check("get_fish_catches: у рыбы считает свежесть",
          c2 is not None and c2['kind'] == 'fish' and c2['remaining_sec'] > 0)

    # ── 3. дефолт market_ok=1 для рыбы (разовая миграция v0.13.3) ──
    sig_ok = await get_item(sig['id'])
    boot_ok = await get_item(boot['id'])
    check("миграция: рыба market_ok=1", sig_ok is not None and sig_ok['market_ok'] == 1)
    check("миграция: сапог market_ok=0", boot_ok is not None and boot_ok['market_ok'] == 0)
    marker = await (await conn.execute(
        "SELECT value FROM settings WHERE key = 'mig_v0133_fish_market_ok'")).fetchone()
    check("маркер миграции записан", marker is not None)

    # ── 4. тип в админке водоёма ──
    wfsig = await (await conn.execute(
        "SELECT wf.id FROM water_fish wf JOIN items i ON i.id = wf.item_id "
        "WHERE wf.water = 'lake' AND i.name = 'Сиг'")).fetchone()
    check("Сиг есть в озере", wfsig is not None)
    if wfsig:
        check("get_water_fish_kind = fish",
              await get_water_fish_kind("lake", "Сиг") == 'fish')
        ok = await update_water_fish_field(wfsig['id'], "kind", "resource")
        check("update_water_fish_field kind/resource ok", ok)
        row = await get_water_fish_row(wfsig['id'])
        check("water_fish.kind = resource", row is not None and row['kind'] == 'resource')
        check("get_water_fish_kind после смены",
              await get_water_fish_kind("lake", "Сиг") == 'resource')
        await update_water_fish_field(wfsig['id'], "kind", "fish")
        check("вернул kind=fish", await get_water_fish_kind("lake", "Сиг") == 'fish')

    # ── 5. кандидаты «Добавить» включают находки (resource/consumable) ──
    cands = await get_water_fish_candidates("reservoir")
    cand_names = [c['name'] for c in cands]
    check("в кандидатах есть находки",
          any("сапог" in n for n in cand_names) or boot['name'] in cand_names)

    # ── 6. миграция легаси-мусора: инвентарь → улов ──
    await add_inventory_item(uid2, boot['id'], 2)
    await add_inventory_item(uid2, weed['id'], 1)
    inv_boot = await get_inventory_item(uid2, boot['id'])
    check("сапог лежит в инвентаре (легаси)", inv_boot is not None and inv_boot['quantity'] == 2)
    moved = await migrate_legacy_junk()
    check("migrate_legacy_junk перенёс 3 копии", moved == 3)
    check("инвентарь сапога пуст",
          await get_inventory_item(uid2, boot['id']) is None)
    check("инвентарь водорослей пуст",
          await get_inventory_item(uid2, weed['id']) is None)
    migrated = [c for c in await get_fish_catches(uid2)
                if c['item_id'] == boot['id'] and (c.get('kind') or '') == 'resource']
    check("в улове 2 сапога kind=resource без срока",
          len(migrated) == 2 and migrated[0]['remaining_sec'] == 0)

    # ── 7. группа улова и кнопки списка (fishcatch) ──
    groups = _fish_groups(await get_fish_catches(uid))
    boot_key = (boot['id'], 1)
    sig_keys = [k for k in groups if k[0] == sig['id']]
    check("группа сапога kind=resource", groups[boot_key]['kind'] == 'resource')
    check("группа сига kind=fish", bool(sig_keys) and groups[sig_keys[0]]['kind'] == 'fish')
    kb = inv_list_markup(await _test_inv(), catches=await get_fish_catches(uid),
                         back_cb="inventory:list", back_label="🔙")
    texts = [b.text for row in kb.inline_keyboard for b in row]
    cbs = [b.callback_data for row in kb.inline_keyboard for b in row]
    check("сапог в списке улова без веса",
          any(t.endswith(f"{boot['name']} x1") and "—" not in t for t in texts))
    check("кнопка fishcatch для сапога",
          f"fishcatch:{boot['id']}:1" in cbs)

    await close_db()
    print(f"\nSmoke 057: {passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)


async def _test_inv():
    return []


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