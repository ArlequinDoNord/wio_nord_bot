"""Smoke v0.15.7: рецепт «Пара сапог» на верстаке.

Проверяет:
1. ensure_life_items создаёт «Клей» и «Набор игл» (лавка) и «Пара сапог»
   (экипировка, броня 2, слот legs, в магазине скрыта — только через верстак).
2. ensure_recipes добавляет рецепт на верстак: 2×«Старый сапог» + «Паутина паука»
   + «Клей» + «Набор игл» → «Пара сапог». На кухню рецепт не попадает.
3. Уловы (сапоги в «Улове» kind=resource) видны рецептами и списываются
   consume_ingredient (сначала инвентарь, затем улов).
4. Карточка рецепта: показывает количество ингредиентов и «🏭 Готовить»,
   при нехватке — «⚠️ Нет ингредиентов!» и без кнопки Готовить.

Запуск: .venv\\Scripts\\python.exe smoke_072.py
"""
import asyncio
import os
import sys
from types import SimpleNamespace

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke072.db")
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


def markup_callbacks(markup):
    if not markup:
        return []
    return [b.callback_data for row in markup.inline_keyboard for b in row]


def last_bot_send(bot):
    if not bot.sent:
        return "", None
    _, _chat, text, markup = bot.sent[-1]
    return text or "", markup


async def run():
    from database.db import (
        init_db, close_db, seed_default_items, seed_dungeon,
        ensure_dungeon_shop_items, ensure_dungeon_enemy_drops, ensure_life_items,
        ensure_dungeon_reservoir_items, ensure_water_fish,
        ensure_recipes,
        get_item_by_name, get_available_items, get_recipes, get_recipe,
        get_ingredient_map, consume_ingredient, add_fish_catch, get_fish_catches,
        add_inventory_item, remove_inventory_item,
        set_player_housing, set_housing_slot, add_user,
    )
    from bot.handlers.housing import housing_recipe

    await init_db()
    await seed_default_items()
    await seed_dungeon()
    await ensure_dungeon_shop_items()
    await ensure_dungeon_enemy_drops()
    await ensure_life_items()
    await ensure_dungeon_reservoir_items()
    await ensure_water_fish()
    await ensure_recipes()

    uid = 440001
    await add_user(uid, "sapog", "Сапожник", "")

    passed = 0
    failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
        else:
            failed += 1
            print(f"  FAIL: {name}")

    # ── 1. Предметы ──
    glue = await get_item_by_name("Клей")
    needles = await get_item_by_name("Набор игл")
    boots = await get_item_by_name("Пара сапог")
    old_boot = await get_item_by_name("Старый сапог")
    web = await get_item_by_name("Паутина паука")
    check("Клей создан и продаётся в лавке",
          glue is not None and glue['category'] == 'consumable')
    check("Набор игл создан и продаётся в лавке",
          needles is not None and needles['category'] == 'resource')
    check("Пара сапог — экипировка", boots is not None and boots['category'] == 'equipment')
    check("Пара сапог: Броня 2", boots is not None and boots['armor'] == 2)
    check("Пара сапог: слот Ноги", boots is not None and boots['equip_slot'] == 'legs')
    check("Пара сапог не висит в магазине (только верстак)",
          boots is not None and boots['is_available'] == 0
          and boots['name'] not in {i['name'] for i in await get_available_items()})
    check("Клей и Набор игл доступны для покупки",
          glue is not None and needles is not None
          and glue['name'] in {i['name'] for i in await get_available_items()}
          and needles['name'] in {i['name'] for i in await get_available_items()})
    check("базовые ингредиенты на месте (Старый сапог, Паутина паука)",
          old_boot is not None and web is not None)

    # ── 2. Рецепт ──
    bench_recipes = await get_recipes("workbench", 1)
    r = next((x for x in bench_recipes if x['name'] == "Пара сапог"), None)
    check("рецепт «Пара сапог» есть на верстаке 1 ур.", r is not None)
    if r:
        ing = [tuple(x) for x in __import__('json').loads(r['ingredients'] or "[]")]
        check("состав рецепта: 2×сапог + паутина + клей + иглы",
              set(ing) == {("Старый сапог", 2), ("Паутина паука", 1),
                           ("Клей", 1), ("Набор игл", 1)})
        check("результат «Пара сапог» ×1, 6 ОД",
              r['result_item_name'] == "Пара сапог" and r['result_quantity'] == 1
              and r['ap_cost'] == 6)
        check("на кухню рецепт не попадает",
              not any(x['name'] == "Пара сапог" for x in await get_recipes("kitchen", 3)))

    # ── 3. Уловы сапог видит рецепт и списывает ──
    # Положили 3 сапога в «Улов» (как с рыбалки) + инвентарь: паутина/клей/иглы.
    for _ in range(3):
        await add_fish_catch(uid, old_boot['id'], weight=1, kind="resource")
    for item, qty in ((web, 1), (glue, 1), (needles, 1)):
        await add_inventory_item(uid, item['id'], qty)

    imap = await get_ingredient_map(uid)
    check("улов: сапоги видно рецепту (3 шт)",
          imap.get("Старый сапог") == 3)
    check("инвентарь: паутина/клей/иглы видно рецепту",
          imap.get("Паутина паука") == 1 and imap.get("Клей") == 1
          and imap.get("Набор игл") == 1)

    check("consume_ingredient списал 2 сапога из улова",
          await consume_ingredient(uid, "Старый сапог", 2))
    imap2 = await get_ingredient_map(uid)
    check("после списания остался 1 сапог",
          imap2.get("Старый сапог", 0) == 1 and len(await get_fish_catches(uid)) == 1)
    check("consume_ingredient списал клей из инвентаря",
          await consume_ingredient(uid, "Клей", 1)
          and imap2.get("Клей", 0) == 1)

    # ── 4. Карточка рецепта в Верстаке ──
    await set_player_housing(uid, "apartment")
    await set_housing_slot(uid, 0, "workbench", 1)
    # Полный набор для крафта: 2 сапога (в улове остался 1 → добавим ещё 1)
    await add_fish_catch(uid, old_boot['id'], weight=1, kind="resource")
    await add_inventory_item(uid, glue['id'], 1)

    rid = r['id'] if r else 99999
    bot_full = FakeSender()
    cb_full = FakeCallback(uid, data=f"housing:recipe:0:{rid}", bot=bot_full)
    await housing_recipe(cb_full)
    card_txt, card_kb = last_bot_send(bot_full)
    check("карточка рецепта открыта", "Пара сапог" in card_txt and "Ингредиенты" in card_txt)
    check("в карточке виден состав", "Старый сапог" in card_txt
          and "Паутина паука" in card_txt and "Клей" in card_txt
          and "Набор игл" in card_txt)
    check("есть кнопка «Готовить»",
          any(c.startswith("housing:craft:") for c in markup_callbacks(card_kb)))

    # Нехватка ингредиентов → «Нет ингредиентов!» и без кнопки.
    await consume_ingredient(uid, "Старый сапог", 2)
    await consume_ingredient(uid, "Паутина паука", 1)
    bot_deny = FakeSender()
    cb_deny = FakeCallback(uid, data=f"housing:recipe:0:{rid}", bot=bot_deny)
    await housing_recipe(cb_deny)
    deny_txt, deny_kb = last_bot_send(bot_deny)
    check("при нехватке — нет кнопки Готовить",
          "Нет ингредиентов" in deny_txt
          and not any(c.startswith("housing:craft:") for c in markup_callbacks(deny_kb)))

    await close_db()
    print(f"\nSmoke 072: {passed} passed, {failed} failed")
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