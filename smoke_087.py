"""Smoke v0.15.28: «только лут» — предметы-дроп не попадают в магазин.

Флаг items.loot_only=1 убирает предмет из витрин магазина (get_available_items
и visible_items), оставляя его доступным как дроп. В мастере добавления товара
появился шаг «Только лут?», в редакторе — тумблер field:loot_only. Заодно
проверяется фикс add_item_photo (NameError на weapon_effect больше не падает).

Запуск: .venv\\Scripts\\python.exe smoke_087.py
"""
import asyncio
import os
import sys

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke087.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB

sys.path.insert(0, os.path.dirname(__file__))


class _Attr:
    def __init__(self, **kw):
        self.__dict__.update(kw)


class _Msg:
    def __init__(self, text="-"):
        self.photo = None
        self.text = text
        self.from_user = _Attr(id=777)

    async def answer(self, *a, **k):
        pass


class _State:
    def __init__(self, data):
        self.data = data

    async def update_data(self, **kw):
        self.data.update(kw)

    async def get_data(self):
        return self.data

    async def clear(self):
        self.data = {}


async def run():
    from database.db import (
        init_db, close_db, add_item, get_available_items, get_all_items,
        get_item, update_item,
    )
    from bot.handlers.admin import add_item_photo
    from bot.handlers.shop import visible_items

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

    # ── 1. add_item с флагом loot_only ──
    loot_id = await add_item(
        "Дроп Сокровища", "трофей", 0, 5, 3, "resource", 0, 1,
        market_ok=0, loot_only=1,
    )
    shop_id = await add_item(
        "Обычный товар", "в витрине", 100, 50, 1, "resource", 10, 1,
        market_ok=0, loot_only=0,
    )
    shoptop_id = await add_item(
        "Товар витрины", "в витрине", 100, 50, 1, "resource", 10, 1,
        market_ok=0,
    )
    check("loot_only сохранён =1", (await get_item(loot_id)).get('loot_only') == 1)
    check("по умолчанию loot_only =0", (await get_item(shop_id)).get('loot_only') == 0)

    # ── 2. get_available_items скрывает лут ──
    avail_ids = [i['id'] for i in await get_available_items()]
    check("лут НЕ в get_available_items", loot_id not in avail_ids)
    check("обычный товар в get_available_items", shop_id in avail_ids)
    check("товар без флага тоже в списке", shoptop_id in avail_ids)
    check("лут есть в get_all_items (Хранилище)", loot_id in [i['id'] for i in await get_all_items()])

    # ── 3. visible_items скрывает лут даже для пилота ──
    from database.db import add_user, get_status_by_tag, grant_status
    await add_user(35001, "pilot001", "Пилот", "")
    s = await get_status_by_tag("pilot2")
    await grant_status(35001, s['id'])
    vis = {i['id'] for i in await visible_items(35001, await get_all_items())}
    check("visible_items: лута нет", loot_id not in vis)
    check("visible_items: обычный товар есть", shop_id in vis)
    check("visible_items: товар без флага есть", shoptop_id in vis)

    # ── 4. update_item переключает флаг ──
    await update_item(shop_id, loot_only=1)
    check("после включения лут скрыт из витрины",
          shop_id not in [i['id'] for i in await get_available_items()])
    await update_item(shop_id, loot_only=0)
    check("после выключения товар снова в витрине",
          shop_id in [i['id'] for i in await get_available_items()])

    # ── 5. add_item_photo не падает и передаёт loot_only (фикс NameError) ──
    from bot.handlers.admin import log_action as _real_log
    calls = {}

    async def _fake_add_item(**kw):
        calls.update(kw)
        return 99999

    async def _fake_log(*a, **k):
        pass

    import bot.handlers.admin as A
    orig_add, orig_log = A.add_item, A.log_action
    A.add_item, A.log_action = _fake_add_item, _fake_log
    try:
        data = {
            "name": "Фото-лут", "desc": "d", "price": 1, "sell_price": 1,
            "rarity": 1, "category": "weapon", "stock": 0,
            "weapon_effect": None, "weapon_effect_chance": 0, "weapon_effect_dmg": 0,
            "loot_only": 1,
        }
        await add_item_photo(_Msg("-"), _State(data))
        check("add_item_photo отработал (нет NameError)", True)
        check("add_item_photo передал loot_only=1", calls.get('loot_only') == 1)
        check("add_item_photo передал weapon_effect", 'weapon_effect' in calls)
        check("add_item_photo передал required_status", 'required_status' in calls)
    except Exception as e:
        check("add_item_photo отработал (нет NameError)", False)
        print(f"    {type(e).__name__}: {e}")
    finally:
        A.add_item, A.log_action = orig_add, orig_log

    # ── 6. Тексты висят в исходниках админки ──
    def source_has(path, needle):
        with open(path, "r", encoding="utf-8") as f:
            return needle in f.read()

    root = os.path.dirname(__file__)
    admin_src = os.path.join(root, "bot", "handlers", "admin.py")
    check("мастер: шаг «Только лут» есть", source_has(admin_src, "Шаг 11/13 — 🎯 Это предмет ТОЛЬКО для лута врагов?"))
    check("мастер: колбэк lootonly:", source_has(admin_src, "lootonly:yes"))
    check("меню правки: кнопка field:loot_only",
          source_has(admin_src, '"🎯 Только лут (вкл/выкл)", callback_data="field:loot_only"'))
    check("редактор: тумблер loot_only есть",
          source_has(admin_src, "field:loot_only")) 
    check("карточка хранилища: метка лута",
          source_has(admin_src, "🎯 только лут (в магазине нет)"))
    check("add_item_photo: weapon_effect=data.get",
          source_has(admin_src, "weapon_effect=data.get('weapon_effect')"))

    db_src = os.path.join(root, "database", "db.py")
    check("db.py: фильтр loot_only в get_available_items",
          source_has(db_src, "IFNULL(loot_only, 0) = 0"))
    check("db.py: миграция loot_only",
          source_has(db_src, '"items", "loot_only", "INTEGER DEFAULT 0"'))
    shop_src = os.path.join(root, "bot", "handlers", "shop.py")
    check("shop.py: visible_items пропускает лут",
          source_has(shop_src, "if it.get('loot_only'):"))

    await close_db()
    print(f"\nSmoke 087: {passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    asyncio.run(run())