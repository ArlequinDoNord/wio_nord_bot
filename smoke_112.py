"""Smoke 112 — три правки v0.18.19.

Проверяет:
   1. Лес: поиск на опушке 4 ОД, на поляне 5 ОД. Миграция в ensure_forest_zones
      поднимает цены со старых дефолтов (3→4, 4→5) и не трогает цену админа.
   2. Инвентарь: после продажи чек с двумя кнопками — «Продать ещё» (если
      предмет ещё есть) и «Вернуться в инвентарь»; «Продать ещё» продаёт
      ровно 1 шт. и остаётся в том же экране; занятый слотом предмет
      повторно не продаётся.
   3. Штаб: 4-й отряд называется «Polaris», и приказ командира собирается из
      свежего кэша wings, а не из устаревшей копии словаря (регресс «Буран»).
"""
import asyncio
import os
import re
import sys

_TEST_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_test_smoke112.db")
for _suffix in ("", "-wal", "-shm"):
    try:
        os.remove(_TEST_DB + _suffix)
    except OSError:
        pass
os.environ["DATABASE_PATH"] = _TEST_DB

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

PASS, FAIL = 0, 0


def check(name, cond):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  OK  {name}")
    else:
        FAIL += 1
        print(f"FAIL  {name}")


class CBMsg:
    def __init__(self):
        self.text = None
        self.markup = None

    async def edit_text(self, text, reply_markup=None, **kw):
        self.text = text
        self.markup = reply_markup
        return None

    async def answer(self, text=None, reply_markup=None, **kw):
        self.text = text
        self.markup = reply_markup
        return None

    async def answer_photo(self, *a, **kw):  # pragma: no cover
        return None

    async def edit_photo(self, *a, **kw):  # pragma: no cover
        return None


class CB:
    def __init__(self, data="x", uid=515151):
        self.data = data
        self.from_user = type("U", (), {})()
        self.from_user.id = uid
        self.message = CBMsg()

    async def answer(self, text=None, show_alert=False, reply_markup=None, **kw):
        if text:
            self.message.text = text
        return None


def buttons(markup):
    """Список (текст, callback_data) всех кнопок разметки."""
    out = []
    for row in (markup.inline_keyboard if markup else []):
        for b in row:
            out.append((b.text, b.callback_data))
    return out


async def main():
    import config
    DB_PATH = _TEST_DB
    config.DB_PATH = DB_PATH

    import database.db as db
    db.DB_PATH = DB_PATH
    from database.db import (
        init_db, close_db, add_user, add_inventory_item, get_inventory_item,
        get_user, ensure_forest_items, ensure_forest_mushrooms,
        get_forest_zone, update_forest_zone, load_wings_cache,
        set_equipment_slot, get_equipment,
    )

    await init_db()

    async def balance(uid):
        row = await get_user(uid)
        return (row["nordmarks"] if row else 0) or 0

    # ── 1. Цена поиска по зонам ─────────────────────────────────────────
    print("\n= 1. Цена поиска =")
    await ensure_forest_items()
    await ensure_forest_mushrooms()

    glade = await get_forest_zone("glade")
    clearing = await get_forest_zone("clearing")
    check("опушка: поиск 4 ОД", glade["ap_cost"] == 4)
    check("поляна: поиск 5 ОД", clearing["ap_cost"] == 5)
    check("поляна дороже опушки", clearing["ap_cost"] > glade["ap_cost"])
    check("запасная цена = 4 ОД", config.FOREST_AP_COST == 4)

    # Миграция: цена, выставленная админом, переживает повторный сид.
    await update_forest_zone("glade", ap_cost=7)
    await ensure_forest_mushrooms()
    check("цена админа (опушка 7 ОД) не перебита дефолтом",
          (await get_forest_zone("glade"))["ap_cost"] == 7)
    await update_forest_zone("clearing", ap_cost=5)

    # ── 2. Продажа из инвентаря ─────────────────────────────────────────
    print("\n= 2. Чек продажи =")
    import bot.handlers.inventory as inv_mod

    conn = await db.get_db()
    rows = await conn.execute("SELECT id, name, sell_price, stock, category FROM items "
                              "WHERE sell_price > 0 AND stock = -1 "
                              "AND category NOT IN ('consumable', 'fishing', 'weapon', "
                              "'equipment', 'license', 'status') ORDER BY id LIMIT 1")
    item = (await rows.fetchone())
    check("тестовый предмет найден", item is not None)
    if item is None:
        print("\n=== SMOKE 112: прерывание ===")
        return 1
    iid, iname, price = item["id"], item["name"], item["sell_price"]

    await add_user(515151, "testsell", "Тест", "Продавец")
    UID = 515151

    await add_inventory_item(UID, iid, 3, 0)
    inv = await get_inventory_item(UID, iid)
    check("предмет в инвентаре x3", inv and inv["quantity"] == 3)

    # Стек больше 1: inv_sell сначала просит подтверждение (кнопка inv_sell_ok).
    cb_pre = CB(f"inv_sell:{iid}")
    await inv_mod.inv_sell(cb_pre)
    check("стек > 1: спросили подтверждение",
          any(b[1].startswith(f"inv_sell_ok:{iid}")
              for b in buttons(cb_pre.message.markup)))
    check("и ничего не продали", (await get_inventory_item(UID, iid))["quantity"] == 3)

    before = await balance(UID)
    cb = CB(f"inv_sell_ok:{iid}:1")
    await inv_mod.inv_sell_ok(cb)
    check("продажа 1 шт. списана", (await get_inventory_item(UID, iid))["quantity"] == 2)
    check("НМ начислены", (await balance(UID)) - before == price)

    kb = buttons(cb.message.markup)
    check("чек с кнопкой «Продать ещё»",
          any(cb_data == f"inv_sellmore:{iid}" and "Продать ещё" in text
              for text, cb_data in kb))
    check("чек с кнопкой «Вернуться в инвентарь»",
          any(cb_data == "inventory:list" and "Вернуться в инвентарь" in text
              for text, cb_data in kb))
    check("чек показывает остаток", "Осталось в инвентаре: 2" in (cb.message.text or ""))

    # «Продать ещё» продаёт ровно 1 шт. и остаётся в этом же экране.
    cb2 = CB(f"inv_sellmore:{iid}")
    before = await balance(UID)
    await inv_mod.inv_sellmore(cb2)
    check("«Продать ещё» списал ещё 1 шт.",
          (await get_inventory_item(UID, iid))["quantity"] == 1)
    check("«Продать ещё» начислил цену 1 шт.",
          (await balance(UID)) - before == price)
    kb2 = buttons(cb2.message.markup)
    check("кнопка «Продать ещё» осталась",
          any(b[1] == f"inv_sellmore:{iid}" for b in kb2))
    check("остаток в чеке = 1 шт.", "Осталось в инвентаре: 1" in (cb2.message.text or ""))

    # Последний экземпляр: кнопки «Продать ещё» уже нет, но есть возврат.
    cb3 = CB(f"inv_sellmore:{iid}")
    await inv_mod.inv_sellmore(cb3)
    check("последний экземпляр продан", await get_inventory_item(UID, iid) is None)
    kb3 = buttons(cb3.message.markup)
    check("после последней продажи нет «Продать ещё»",
          not any(b[1] == f"inv_sellmore:{iid}" for b in kb3))
    check("но остался возврат в инвентарь",
          any(b[1] == "inventory:list" for b in kb3))

    # _sellable_left считает занятые слоты: надетый предмет продать нельзя.
    check("в пустом инвентаре продавать нечего", await inv_mod._sellable_left(UID, iid) == 0)
    await add_inventory_item(UID, iid, 2, 0)
    check("свободный стек продаётся", await inv_mod._sellable_left(UID, iid) == 2)
    first_slot = next(iter(db.EQUIPMENT_SLOT_LABELS))
    await set_equipment_slot(UID, first_slot, iid)
    check("1 шт. занято слотом → продаётся 1",
          await inv_mod._sellable_left(UID, iid) == 1)
    # Кнопка «Продать ещё» на таком стеке продаёт только свободный экземпляр.
    await add_inventory_item(UID, iid, 1, 0)
    before = await balance(UID)
    cb4 = CB(f"inv_sellmore:{iid}")
    await inv_mod.inv_sellmore(cb4)
    check("при занятом слоте продан только свободный штук",
          (await balance(UID)) - before == price)

    # ── 3. Штаб: 4-й отряд Polaris ──────────────────────────────────────
    print("\n= 3. Формирования =")
    from utils import wings as W

    conn = await db.get_db()
    w4 = await (await conn.execute(
        "SELECT callsign FROM wings WHERE key = '4'")).fetchone()
    check("сид 4-го отряда = Polaris", w4 and w4["callsign"] == "Polaris")
    check("в кэше Polaris", W.wing_label("4") == "❄️ 4 СО «Polaris» (спец отряд)")
    check("«Буран» больше не упоминается в wings.py",
          "Буран" not in open("utils/wings.py", encoding="utf-8").read())

    # Регресс: set_wings пересобирает словарь, импортированная копия устаревает.
    import bot.handlers.hq as hq
    check("hq.py не импортирует сам словарь WINGS",
          not hasattr(hq, "WINGS") and not hasattr(hq, "WINGS_SHORT"))
    await load_wings_cache()
    check("wing_label в hq даёт Polaris", hq.wing_label("4") == "❄️ 4 СО «Polaris» (спец отряд)")
    check("wing_short в hq даёт «❄️ 4 СО»", hq.wing_short("4") == "❄️ 4 СО")
    check("all_wings отдаёт свежие 4 метки", len(hq.all_wings()) == 4)
    check("all_wings тоже с Polaris", "Polaris" in hq.all_wings()["4"])

    # Переименование в БД сразу видно в приказе (без перезапуска бота).
    await conn.execute("UPDATE wings SET callsign = 'Буран' WHERE key = '4'")
    await conn.commit()
    await load_wings_cache()
    check("после правки БД приказ собирает новое имя",
          "Буран" in hq.wing_label("4"))
    await conn.execute("UPDATE wings SET callsign = 'Polaris' WHERE key = '4'")
    await conn.commit()
    await load_wings_cache()
    check("и обратно Polaris", "Polaris" in hq.wing_label("4"))

    # Текст приказа командира собирается через wing_label, без сырого WINGS.
    hq_src = open("bot/handlers/hq.py", encoding="utf-8").read()
    check("в hq.py нет обращений к сырому WINGS[",
          "WINGS[" not in hq_src and "WINGS.get(" not in hq_src)
    check("приказ использует wing_label", "wing_label(target)" in hq_src)

    await close_db()
    for suffix in ("", "-wal", "-shm"):
        try:
            os.remove(DB_PATH + suffix)
        except OSError:
            pass

    print(f"\n=== SMOKE 112: {PASS} passed, {FAIL} failed ===")
    return 1 if FAIL else 0


if __name__ == "__main__":
    code = 1
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        code = loop.run_until_complete(main())
        loop.run_until_complete(asyncio.sleep(0))
    finally:
        import asyncio as _a
        _loop = _a.new_event_loop()
        _a.set_event_loop(_loop)
        try:
            import database.db as _db
            if _db.db is not None:
                _loop.run_until_complete(_db.close_db())
        except Exception:
            pass
        _loop.close()
    sys.exit(code)
