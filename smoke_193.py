# -*- coding: utf-8 -*-
"""Smoke 193 — источники праздничных рецептов.

1. Рецепт «Леденец из ягод» продаётся в праздничной лавке (обмен веток на свиток).
2. Свиток леденца выучивается, даже пока скрыт из магазина.
3. «Предания предков» не продаются: свитка в магазине нет и быть не может.
4. Тыквенный пирог — только с босса: в лавке его нет, в магазине скрыт.
"""
import asyncio
import os
import sys

os.environ["DATABASE_PATH"] = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "_test_smoke193.db")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def main():
    passed = failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
            print(f"  OK  {name}")
        else:
            failed += 1
            print(f"  FAIL {name}")

    db_file = os.environ["DATABASE_PATH"]
    if os.path.exists(db_file):
        os.remove(db_file)

    import config
    from database.db import (init_db, close_db, get_db, add_user, add_item, get_item_by_name,
                             ensure_firelab_items, ensure_forest_enemies,
                             ensure_recipe_shop_items, add_inventory_item, get_inventory_item,
                             learn_recipe_from_item, get_learned_recipes)
    from bot.handlers import fire_event as fe

    await init_db()
    await ensure_firelab_items()
    await ensure_forest_enemies()
    await ensure_recipe_shop_items()
    conn = await get_db()
    UID = 193001
    await add_user(UID, "t", "Пилот 193", "")

    print("\n1. Леденец из ягод — в лавке")
    offers = [fe._offer(i) for i in range(len(config.FIRE_EXCHANGE_OFFERS))]
    idx = next((i for i, o in enumerate(offers) if o[1] == "Рецепт: Леденец из ягод"), None)
    check("обмен на свиток леденца есть в лавке", idx is not None)
    check("курс: 15 сена + 15 веток",
          idx is not None and sorted(offers[idx][0]) == sorted(
              [(config.FIRE_LAB_HAY_NAME, 15), (config.FIRE_LAB_BRANCH_NAME, 15)]))
    scroll = await get_item_by_name("Рецепт: Леденец из ягод")
    check("свиток существует", scroll is not None)
    branch = await get_item_by_name(config.FIRE_LAB_BRANCH_NAME)
    hay = await get_item_by_name(config.FIRE_LAB_HAY_NAME)
    await add_inventory_item(UID, branch['id'], 15)
    await add_inventory_item(UID, hay['id'], 15)
    config.FIRE_EXCHANGE_ENABLED = True

    class FakeBot:
        async def send_message(self, chat_id, text, **kw):
            return type("M", (), {"message_id": 2, "chat": type("C", (), {"id": chat_id})()})()

        async def send_photo(self, chat_id, *a, **kw):
            return type("M", (), {"message_id": 3, "chat": type("C", (), {"id": chat_id})()})()

        async def delete_message(self, *a, **kw):
            return True

    class FakeMsg:
        chat = type("C", (), {"id": UID})()
        message_id = 1
        bot = FakeBot()

        async def answer(self, *a, **kw):
            return self

        async def edit_text(self, *a, **kw):
            return True

        async def edit_caption(self, *a, **kw):
            return True

        async def edit_media(self, *a, **kw):
            return True

        async def delete(self):
            return True

    class FakeCB:
        def __init__(self, data):
            self.from_user = type("U", (), {"id": UID})()
            self.data = data
            self.message = FakeMsg()

        async def answer(self, *a, **kw):
            return True

    try:
        await fe.fire_event_xchg_cb(FakeCB(f"fireevent:xchg:{idx}"))
    finally:
        config.FIRE_EXCHANGE_ENABLED = False
    got = await get_inventory_item(UID, scroll['id'])
    check("лавка выдала свиток леденца", got is not None and int(got['quantity']) == 1)
    left = await get_inventory_item(UID, branch['id'])
    left_hay = await get_inventory_item(UID, hay['id'])
    check("веток и сена списано по 15",
          (left is None or int(left['quantity']) == 0)
          and (left_hay is None or int(left_hay['quantity']) == 0))

    print("\n2. Свиток леденца выучивается при скрытом рецепте")
    ok, _ = await learn_recipe_from_item(UID, scroll['id'])
    check("обучение прошло", ok is True)
    learned = [r['name'] for r in await get_learned_recipes(UID)]
    check("леденец в выученных", "Леденец из ягод" in learned)

    print("\n3. Предания предков — не в магазине")
    await add_item(name="Рецепт: Предания предков", description="тест", price=1, sell_price=0,
                   rarity=1, category="recipes", stock=-1, added_by=0, ap_cost=0, damage=0, heal=0)
    await ensure_forest_enemies()  # старт: гасит свиток Преданий
    predki = await get_item_by_name("Рецепт: Предания предков")
    check("свиток Преданий скрыт при старте", predki is not None and predki['is_available'] == 0)
    off_names = [o[1] for o in offers]
    check("в лавке Преданий нет", "Рецепт: Предания предков" not in off_names)

    print("\n4. Тыквенный пирог — только с босса")
    pie = await get_item_by_name("Рецепт: Тыквенный пирог")
    check("свиток пирога скрыт из магазина", pie is not None and pie['is_available'] == 0)
    check("в лавке пирога-рецепта нет", "Рецепт: Тыквенный пирог" not in off_names)

    print(f"\nИТОГО: {passed} passed, {failed} failed")
    await close_db()
    return failed


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
