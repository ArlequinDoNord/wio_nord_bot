"""Smoke v0.22.9: тех-долг крафта — проверка уровня расширения и возврат ОД.

Проверяет:
1. Меню рецептов кухни фильтруется по уровню (2 ур. не виден на 1 ур. кухне).
2. Действие крафта перепроверяет уровень расширения: устаревшая кнопка
   «housing:craft» с рецептом 2 ур. на кухне 1 ур. отклоняется, ОД и
   ингредиенты не списываются.
3. ОД не теряются: при нехватке ОД (remove_ap вернул False) уже списанные
   ингредиенты возвращаются в инвентарь.
4. Регрессия счастливого пути: успешный крафт даёт предмет, списывает ОД и
   ингредиенты, отпускает CRAFTING (ожидание анимации отключено подменой
   asyncio.sleep).

Запуск: .venv\\Scripts\\python.exe smoke_131.py
"""
import asyncio
import os
import sys
from types import SimpleNamespace

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke131.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB

sys.path.insert(0, os.path.dirname(__file__))


class FakeSender:
    def __init__(self):
        self.sent = []

    async def send_message(self, chat_id, text, reply_markup=None, **kw):
        m = SimpleNamespace(message_id=len(self.sent) + 1)
        self.sent.append(("text", chat_id, text, reply_markup))
        return m

    async def send_photo(self, chat_id, photo, caption=None, reply_markup=None, **kw):
        m = SimpleNamespace(message_id=len(self.sent) + 1)
        self.sent.append(("photo", chat_id, caption or "", reply_markup))
        return m


class FakeMessage:
    def __init__(self, user_id, bot=None):
        self.from_user = SimpleNamespace(id=user_id)
        self.chat = SimpleNamespace(id=user_id)
        self.bot = bot or FakeSender()
        self.sent = []

    async def answer(self, *a, **kw):
        self.sent.append(("answer", a, kw))

    async def __getattr__(self, name):
        async def _noop(*a, **kw):
            return None
        return _noop


class FakeCallback:
    def __init__(self, user_id, data="", message=None, bot=None):
        self.from_user = SimpleNamespace(id=user_id)
        self.bot = bot or FakeSender()
        self.message = message or FakeMessage(user_id, self.bot)
        self.data = data
        self.alerts = []

    async def answer(self, text=None, *a, **kw):
        self.alerts.append(text)


def last_bot_send(bot):
    if not bot.sent:
        return "", None
    _, _chat, text, markup = bot.sent[-1]
    return text or "", markup


async def run():
    from database.db import (
        init_db, close_db, seed_default_items, ensure_recipes,
        ensure_life_items, ensure_dungeon_shop_items, ensure_forest_items,
        get_user, get_recipes, get_ingredient_map,
        get_item_by_name, add_inventory_item, get_inventory,
        set_player_housing, set_housing_slot, add_user, learn_recipe,
    )
    from bot.handlers import housing as hh
    import utils.crafting as crafting

    await init_db()
    await seed_default_items()
    await ensure_dungeon_shop_items()
    await ensure_life_items()
    await ensure_forest_items()
    await ensure_recipes()

    uid = 441001
    await add_user(uid, "craft1", "Крафтер", "")
    await set_player_housing(uid, "apartment")
    await set_housing_slot(uid, 0, "kitchen", 1)

    passed = 0
    failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
        else:
            failed += 1
            print(f"  FAIL: {name}")

    # ── Рецепты и предметы ──
    rec_lvl2 = next((x for x in await get_recipes("kitchen", 2)
                     if x['name'] == "Жареный белый гриб"), None)
    rec_lvl1_names = {x['name'] for x in await get_recipes("kitchen", 1)}
    check("рецепт «Жареный белый гриб» есть на кухне 2 ур.",
          rec_lvl2 is not None)
    check("на кухне 1 ур. его нет (список фильтруется по уровню)",
          rec_lvl2 is not None and rec_lvl2['name'] not in rec_lvl1_names)

    tincture = next((x for x in await get_recipes("kitchen", 3)
                     if x['name'] == "Малая настойка здоровья"), None)
    check("рецепт «Малая настойка здоровья» есть на кухне 2+ ур.",
          tincture is not None)

    items_needed = {
        n: await get_item_by_name(n)
        for n in ("Белый гриб", "Соль", "Бутылка чистой воды", "Осколок кристалла")
    }
    for name, it in items_needed.items():
        check(f"предмет «{name}» существует", it is not None)

    if not rec_lvl2 or not tincture or not all(items_needed.values()):
        await close_db()
        print(f"\nSmoke 131: {passed} passed, {failed} failed")
        sys.exit(1 if failed else 0)

    # ── Учим оба рецепта ──
    await learn_recipe(uid, rec_lvl2['id'])
    await learn_recipe(uid, tincture['id'])

    ap0 = (await get_user(uid))["ap"]

    # ── 1. Уровневый барьер: кухня 1 ур. + рецепт 2 ур. ──
    await add_inventory_item(uid, items_needed["Белый гриб"]["id"], 1)
    await add_inventory_item(uid, items_needed["Соль"]["id"], 1)

    bot_guard = FakeSender()
    cb_guard = FakeCallback(uid, data=f"housing:craft:0:{rec_lvl2['id']}", bot=bot_guard)
    await hh.housing_craft(cb_guard)
    check("кухня 1 ур.: рецепт 2 ур. отклонён", any(
        t and "выше уровня расширения" in t for t in cb_guard.alerts))
    check("кухня 1 ур.: сообщений о старте не было", not bot_guard.sent)
    imap_guard = await get_ingredient_map(uid)
    check("кухня 1 ур.: ОД не списаны",
          (await get_user(uid))["ap"] == ap0)
    check("кухня 1 ур.: ингредиенты на месте",
          imap_guard.get("Белый гриб", 0) == 1 and imap_guard.get("Соль", 0) == 1)
    check("кухня 1 ур.: CRAFTING свободен", uid not in hh.CRAFTING)

    # ── 2. Кухня 2 ур., но remove_ap падает → возврат сырья ──
    await set_housing_slot(uid, 0, "kitchen", 2)
    await add_inventory_item(uid, items_needed["Бутылка чистой воды"]["id"], 1)
    await add_inventory_item(uid, items_needed["Осколок кристалла"]["id"], 1)

    real_remove_ap = crafting.remove_ap

    async def _ap_deny(*a, **k):
        return False

    crafting.remove_ap = _ap_deny
    try:
        cb_refund = FakeCallback(uid, data=f"housing:craft:0:{tincture['id']}")
        await hh.housing_craft(cb_refund)
    finally:
        crafting.remove_ap = real_remove_ap
    check("нехватка ОД: алерт «Не хватает ОД!»", any(
        t and "Не хватает ОД" in t for t in cb_refund.alerts))
    imap_refund = await get_ingredient_map(uid)
    check("нехватка ОД: ОД не списаны",
          (await get_user(uid))["ap"] == ap0)
    check("нехватка ОД: сырьё возвращено в инвентарь",
          imap_refund.get("Бутылка чистой воды", 0) == 1
          and imap_refund.get("Осколок кристалла", 0) == 1)
    check("нехватка ОД: CRAFTING свободен", uid not in hh.CRAFTING)

    # ── 3. Регрессия: счастливый путь (анимация выключена) ──
    # Сырьё уже возвращено предыдущим тестом отката ОД (вода/осколок по 1 шт.).

    real_sleep = crafting.asyncio.sleep

    async def _nosleep(*a, **k):
        return None

    crafting.asyncio.sleep = _nosleep
    try:
        bot_ok = FakeSender()
        cb_ok = FakeCallback(uid, data=f"housing:craft:0:{tincture['id']}", bot=bot_ok)
        await hh.housing_craft(cb_ok)
    finally:
        crafting.asyncio.sleep = real_sleep
    ok_txt, _ = last_bot_send(bot_ok)
    check("счастливый путь: алерт «Начал готовить!»", any(
        t and "Начал готовить" in t for t in cb_ok.alerts))
    check("счастливый путь: итоговое сообщение про «готово»", "готово" in ok_txt)
    imap_ok = await get_ingredient_map(uid)
    check("счастливый путь: ингредиенты списаны",
          imap_ok.get("Бутылка чистой воды", 0) == 0
          and imap_ok.get("Осколок кристалла", 0) == 0)
    tincture_item = await get_item_by_name("Малая настойка здоровья")
    inv_ok = await get_inventory(uid)
    tincture_qty = next(
        (i["quantity"] for i in inv_ok if i["id"] == tincture_item["id"]), 0)
    check("счастливый путь: результат в инвентаре", tincture_qty >= 1)
    check("счастливый путь: ОД списаны (−10)",
          (await get_user(uid))["ap"] == ap0 - int(tincture['ap_cost']))
    check("счастливый путь: CRAFTING свободен", uid not in hh.CRAFTING)

    # ── 5. Переработка грибов на кухне без рецепта (1 ОД за гриб) ─────────
    from database.db import ensure_forest_items
    from utils.crafting import (
        MUSHROOM_HEAL_POWDER_NAME, MUSHROOM_ESSENCE_NAME,
        MUSHROOM_POISON_POWDER_NAME, MUSHROOM_POWDER_SPECS,
        MUSHROOM_PROCESS_AP_COST, CraftError, process_mushrooms,
    )
    await ensure_forest_items()
    hp_item = await get_item_by_name(MUSHROOM_HEAL_POWDER_NAME)
    ess_item = await get_item_by_name(MUSHROOM_ESSENCE_NAME)
    pp_item = await get_item_by_name(MUSHROOM_POISON_POWDER_NAME)
    check("предмет «Грибной целебный порошок» создан (resource, скрыт из лавки)",
          bool(hp_item) and hp_item["category"] == "resource"
          and hp_item["is_available"] == 0 and hp_item["market_ok"] == 1)
    check("предмет «Грибная эссенция» создан (resource, скрыт из лавки)",
          bool(ess_item) and ess_item["category"] == "resource"
          and ess_item["is_available"] == 0 and ess_item["market_ok"] == 1)
    check("предмет «Ядовитый грибной порошок» создан (resource, скрыт из лавки)",
          bool(pp_item) and pp_item["category"] == "resource"
          and pp_item["is_available"] == 0 and pp_item["market_ok"] == 1)

    check("MUSHROOM_PROCESS_AP_COST == 1", MUSHROOM_PROCESS_AP_COST == 1)
    check("Гиропор: 3–4 порошка и 8% шанс эссенции",
          MUSHROOM_POWDER_SPECS["Гиропор"]["min"] == 3
          and MUSHROOM_POWDER_SPECS["Гиропор"]["max"] == 4
          and MUSHROOM_POWDER_SPECS["Гиропор"]["essence_chance"] == 8)
    check("Ежовик: 4–5 порошка и 17% шанс эссенции",
          MUSHROOM_POWDER_SPECS["Ежовик гребенчатый"]["min"] == 4
          and MUSHROOM_POWDER_SPECS["Ежовик гребенчатый"]["max"] == 5
          and MUSHROOM_POWDER_SPECS["Ежовик гребенчатый"]["essence_chance"] == 17)
    check("Мухомор и Бледная поганка дают ядовитый порошок",
          MUSHROOM_POWDER_SPECS["Мухомор"]["powder"] == MUSHROOM_POISON_POWDER_NAME
          and MUSHROOM_POWDER_SPECS["Бледная поганка"]["powder"] == MUSHROOM_POISON_POWDER_NAME)

    # Кнопка переработки грибов на экране кухни
    def _m_cbs(rm):
        if not rm or not getattr(rm, "inline_keyboard", None):
            return []
        return [b.callback_data for row in rm.inline_keyboard for b in row]

    cb_room = FakeCallback(uid, "housing:room:0")
    await hh.housing_room(cb_room)
    _, _, _, rm_room = cb_room.bot.sent[-1]
    check("экран кухни: есть кнопка housing:mushrooms:0",
          "housing:mushrooms:0" in _m_cbs(rm_room))

    openok = await get_item_by_name("Опёнок")
    ejovik = await get_item_by_name("Ежовик гребенчатый")
    muhomor = await get_item_by_name("Мухомор")
    await add_inventory_item(uid, openok["id"], 3)
    await add_inventory_item(uid, ejovik["id"], 4)
    await add_inventory_item(uid, muhomor["id"], 2)
    conn = await hh.get_db() if hasattr(hh, "get_db") else await (__import__("database.db", fromlist=["get_db"]).get_db())
    await conn.execute("UPDATE users SET ap = 2 WHERE user_id = ?", (uid,))
    await conn.commit()

    # Экран переработки показывает грибы и кнопки «1 шт.» и «Все»
    cb_mush = FakeCallback(uid, "housing:mushrooms:0")
    await hh.housing_kitchen_mushrooms(cb_mush)
    _, _, txt_mush, rm_mush = cb_mush.bot.sent[-1]
    mush_cbs = _m_cbs(rm_mush)
    check("переработка: показаны Опёнок, Ежовик, Мухомор",
          "Опёнок" in txt_mush and "Ежовик" in txt_mush and "Мухомор" in txt_mush)
    check("переработка: кнопки 1 шт. и Все для Опёнка",
          f"housing:mushproc:0:{openok['id']}:1" in mush_cbs
          and f"housing:mushproc:0:{openok['id']}:all" in mush_cbs)

    # Недостаточно ОД для «Все ×3» (нужно 3 ОД, а есть 2 ОД)
    cb_all_fail = FakeCallback(uid, f"housing:mushproc:0:{openok['id']}:all")
    await hh.housing_kitchen_mushproc(cb_all_fail)
    check("переработка всех при нехватке ОД: алерт об ОД",
          any("Не хватает ОД" in (a or "") for a in cb_all_fail.alerts))
    inv_after_fail = await get_ingredient_map(uid)
    check("переработка при нехватке ОД: грибы и ОД целы",
          inv_after_fail.get("Опёнок", 0) == 3 and (await get_user(uid))["ap"] == 2)

    # Переработка 1 шт. Опёнка (−1 ОД → 1–2 целебного порошка)
    cb_one = FakeCallback(uid, f"housing:mushproc:0:{openok['id']}:1")
    await hh.housing_kitchen_mushproc(cb_one)
    inv_after_one = await get_ingredient_map(uid)
    p_got = inv_after_one.get(MUSHROOM_HEAL_POWDER_NAME, 0)
    check("переработка 1 Опёнка: осталось 2 гриба, ОД = 1, порошок 1–2",
          inv_after_one.get("Опёнок", 0) == 2
          and (await get_user(uid))["ap"] == 1
          and 1 <= p_got <= 2)

    # Переработка всех Ежовиков с детерминированным RNG (выпадает и эссенция)
    await conn.execute("UPDATE users SET ap = 20 WHERE user_id = ?", (uid,))
    await conn.commit()

    class _FixedRng:
        def randint(self, a, b):
            return b

        def random(self):
            return 0.05  # 5% < 17% → эссенция выпадает на каждом грибе

    out_ej = await process_mushrooms(uid, ejovik["id"], mode="all", rng=_FixedRng())
    inv_after_ej = await get_ingredient_map(uid)
    check("переработка всех 4 Ежовиков: 4×5=20 порошка и 4 эссенции",
          out_ej["processed_count"] == 4
          and out_ej["powder_qty"] == 20
          and out_ej["essence_qty"] == 4
          and inv_after_ej.get(MUSHROOM_ESSENCE_NAME, 0) == 4)

    # Переработка всех Мухоморов → ядовитый порошок
    cb_tox = FakeCallback(uid, f"housing:mushproc:0:{muhomor['id']}:all")
    await hh.housing_kitchen_mushproc(cb_tox)
    inv_after_tox = await get_ingredient_map(uid)
    check("переработка 2 Мухоморов: 0 Мухоморов, 2–4 ядовитого порошка",
          inv_after_tox.get("Мухомор", 0) == 0
          and 2 <= inv_after_tox.get(MUSHROOM_POISON_POWDER_NAME, 0) <= 4)

    # Продажа порошка скупщику: не появляется в магазине (is_available=0), но
    # сохраняется на городском складе (city_storage)
    from bot.handlers import inventory as inv_mod
    from database.db import get_city_storage
    cb_sell = FakeCallback(uid, f"inv_sell_ok:{hp_item['id']}:2")
    await inv_mod.inv_sell_ok(cb_sell)
    hp_fresh = await get_item_by_name(MUSHROOM_HEAL_POWDER_NAME)
    cs_rows = await get_city_storage()
    cs_hp = next((r for r in cs_rows if r["item_id"] == hp_item["id"]), None)
    check("после продажи скупщику порошок скрыт из магазина (is_available=0)",
          hp_fresh["is_available"] == 0 and hp_fresh["stock"] == -1)
    check("после продажи скупщику порошок лёг на городской склад (city_storage)",
          cs_hp is not None and cs_hp["qty"] >= 2)

    await close_db()
    print(f"\nSmoke 131: {passed} passed, {failed} failed")
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