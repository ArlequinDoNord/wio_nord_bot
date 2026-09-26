"""Smoke v0.15.26: туристам закрыты рыбалка и рынок.

Турист не может рыбачить (блок входа на озеро и заброса), прогулка по парку
остаётся; категория «Рынок» не показывается туристу в магазине, выкладка на
рынок (предметы и улов) для туристов невозможна.

Запуск: .venv\\Scripts\\python.exe smoke_085.py
"""
import asyncio
import os
import sys

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke085.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB

sys.path.insert(0, os.path.dirname(__file__))


async def run():
    from database.db import (
        init_db, close_db, add_user, get_status_by_tag, grant_status,
        user_is_tourist, add_item, get_item_by_name, add_fish_offer,
        place_item_offer,
    )
    from bot.handlers.shop import market_offer_items

    await init_db()
    passed = 0
    failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
        else:
            failed += 1
            print(f"  FAIL: {name}")

    # ── 1. user_is_tourist ──
    async def mk(uid, tag):
        await add_user(uid, f"t{uid}", f"Т{uid}", "")
        if tag:
            s = await get_status_by_tag(tag)
            await grant_status(uid, s['id'])

    await mk(35001, "tourist")
    await mk(35002, "recruit")
    await mk(35003, None)
    check("турист → user_is_tourist True", await user_is_tourist(35001) is True)
    check("рекрут → user_is_tourist False", await user_is_tourist(35002) is False)
    check("без статусов → user_is_tourist False", await user_is_tourist(35003) is False)

    # ── 2. Рынок: витрина реально наполняется офферами ──
    await add_item("Сгущёнка", "рыночный товар", 30, 15, 1, "resource", 10, 1, market_ok=1)
    rod = await add_item("Удочка из орешника", "рыбалка", 40, 20, 1, "fishing", 10, 1, market_ok=1)
    sgu = await get_item_by_name("Сгущёнка")
    await add_fish_offer(35002, rod, 120, 30, 3600, base_price=20)
    await place_item_offer(35002, sgu['id'], 30)

    offers = await market_offer_items()
    kinds = sorted(o.get("__offer_type__") for o in offers)
    check("market_offer_items: и рыба, и предмет", kinds == ["fish", "item"])

    # ── 3. Гейт в магазине: категория «Рынок» только не туристам ──
    async def market_visible(uid):
        return bool(await market_offer_items()) and not await user_is_tourist(uid)

    check("турист: рынок скрыт", await market_visible(35001) is False)
    check("рекрут: рынок виден", await market_visible(35002) is True)

    # ── 4. Разводка гейтов в обработчиках ──
    def source_has(path, needle):
        with open(path, "r", encoding="utf-8") as f:
            return needle in f.read()

    root = os.path.dirname(__file__)
    fish = os.path.join(root, "bot", "handlers", "fishing.py")
    shop = os.path.join(root, "bot", "handlers", "shop.py")
    inv = os.path.join(root, "bot", "handlers", "inventory.py")
    check("fishing.py: блок туриста в fishing_lake_menu", source_has(
        fish, "if await user_is_tourist(callback.from_user.id):"))
    check("fishing.py: блок туриста в fish_cast", source_has(
        fish, "if await user_is_tourist(user_id):"))
    check("fishing.py: озеро входит в список готовых окон (парк)", source_has(
        fish, "Рыбалка — только для пилотов"))
    check("shop.py: shop_menu не считает рынок туристам", source_has(
        shop, "if padder and not is_tourist:"))
    check("shop.py: shop_catalog не считает рынок туристам", source_has(
        shop, "padder and not is_tourist"))
    check("shop.py: shop_category блокирует рынок туристу", source_has(
        shop, "Рынок — только для пилотов"))
    check("inventory.py: карточка предмета без рынка туристу", source_has(
        inv, "not await user_is_tourist(user_id)"))
    check("inventory.py: улов без рынка туристу", source_has(
        inv, "bool(item.get('market_ok')) and not await user_is_tourist(user_id)"))
    check("inventory.py: itemmarket гейт туриста", source_has(
        inv, "item_market_set_price") and source_has(inv, "Рынок — только для пилотов"))
    check("inventory.py: fishmarket гейт туриста", source_has(
        inv, "fish_market_set_price") and source_has(inv, "Рынок — только для пилотов"))

    await close_db()
    print(f"\nSmoke 085: {passed} passed, {failed} failed")
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