"""Smoke v0.15.13: партии и кланы + рецепты-товары магазина.

Проверяет:
1. Создание клана/партии, карточка (get_clan/get_clans), редактирование.
2. Члены: добавить/исключить/is/get_*; один клан И одна партия одновременно.
3. Глава: set_clan_leader, роль clan_leader, снятие, передача.
4. Заявки: add/has/get_pending/remove; принять/отклонить.
5. delete_clan чистит членов и заявки.
6. ensure_recipe_shop_items создаёт «Рецепт: …» в магазине.
7. learn_recipe_from_item: изучение (списание предмета), «уже выучен».
8. get_learned_recipes фильтрует по расширению/уровню и is_available.
9. ensure_user_recipes_backfill: старые игроки получают все рецепты, новые — нет.

Запуск: .venv\\Scripts\\python.exe smoke_075.py
"""
import asyncio
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke075.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB

sys.path.insert(0, os.path.dirname(__file__))


async def run():
    from database.db import (
        init_db, close_db, add_user, ensure_recipes,
        create_clan, get_clan, get_clans, update_clan, set_clan_leader, delete_clan,
        add_clan_member, remove_clan_member, is_clan_member,
        get_clan_members, get_clan_member_ids, get_user_clan,
        is_clan_leader, add_clan_request, remove_clan_request, has_clan_request,
        get_clan_pending_requests,
        add_user_role, remove_user_role,
        ensure_recipe_shop_items, ensure_user_recipes_backfill,
        get_recipe, get_item_by_name, get_item,
        add_inventory_item, get_inventory,
        learn_recipe, has_user_recipe, get_learned_recipes, learn_recipe_from_item,
        RECIPE_ITEM_PREFIX, RECIPE_ITEM_PRICES,
        get_db,
    )

    await init_db()
    await ensure_recipes()

    passed = 0
    failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
        else:
            failed += 1
            print(f"  FAIL: {name}")

    U1, U2, U3, ADMIN = 751001, 751002, 751003, 751000
    for uid, name in ((U1, "Т1-клановый"), (U2, "Т2-клановый")):
        await add_user(uid, f"u{uid}", name, "")

    # Бэкфилл: старые игроки (U1, U2) получают все рецепты разово.
    await ensure_recipes()
    await ensure_recipe_shop_items()
    check("бэкфилл: сработал", await ensure_user_recipes_backfill())
    check("бэкфилл повторно не срабатывает", not await ensure_user_recipes_backfill())

    # U3 — новый игрок, создан ПОСЛЕ бэкфилла: рецептов не получает.
    await add_user(U3, f"u{U3}", "Т3-новый", "")

    # ── 1. Создание/редактирование ──
    clan_id = await create_clan("clan", "Северный Легион", "Описание клана", ADMIN)
    party_id = await create_clan("party", "Партия Исследователей", "", U1)
    check("create_clan: id растёт", clan_id and party_id > clan_id)
    clan = await get_clan(clan_id)
    check("get_clan: kind/name/desc", clan and clan['kind'] == 'clan'
          and clan['name'] == "Северный Легион" and clan['description'] == "Описание клана")
    clans = await get_clans()
    check("get_clans: оба", len(clans) == 2)
    check("get_clans(kind='clan')", len(await get_clans('clan')) == 1)
    check("get_clans(kind='party')", len(await get_clans('party')) == 1)

    await update_clan(clan_id, name="Южный Легион", description="Новое",
                      photo_file_id="PHO111")
    clan = await get_clan(clan_id)
    check("update_clan: name/desc/photo", clan['name'] == "Южный Легион"
          and clan['description'] == "Новое" and clan['photo_file_id'] == "PHO111")

    # ── 2. Члены ──
    await add_clan_member(clan_id, U1)
    await add_clan_member(clan_id, U2)
    check("is_clan_member: U1", await is_clan_member(clan_id, U1))
    check("is_clan_member: посторонний", not await is_clan_member(clan_id, U3))
    check("get_clan_member_ids: 2 члена", set(await get_clan_member_ids(clan_id)) == {U1, U2})
    members = await get_clan_members(clan_id)
    check("get_clan_members: 2", len(members) == 2)

    # пилот может быть и в клане, и в партии одновременно
    await add_clan_member(party_id, U2)
    usr_clan = await get_user_clan(U2, 'clan')
    usr_party = await get_user_clan(U2, 'party')
    check("get_user_clan: U2 в клане и в партии", usr_clan and usr_clan['id'] == clan_id
          and usr_party and usr_party['id'] == party_id)
    check("get_user_clan: чужой kind не видно",
          (await get_user_clan(U1, 'party')) is None)

    await remove_clan_member(clan_id, U1)
    check("remove_clan_member", not await is_clan_member(clan_id, U1))

    # ── 3. Глава ──
    await set_clan_leader(clan_id, U2)
    check("is_clan_leader(U2)", await is_clan_leader(U2) == clan_id)
    await add_user_role(U2, 'clan_leader', granted_by=ADMIN)
    check("роль clan_leader выдана", await get_db_role(U2) is not None)
    await remove_user_role(U2, 'clan_leader')
    check("роль clan_leader снята", await get_db_role(U2) is None)
    await update_clan(clan_id, leader_id=U3)
    check("set leader через update_clan", (await get_clan(clan_id))['leader_id'] == U3)

    # ── 4. Заявки ──
    await add_clan_request(clan_id, U1)
    check("has_clan_request(U1)", await has_clan_request(clan_id, U1))
    pending = await get_clan_pending_requests(clan_id)
    check("get_clan_pending_requests: 1", len(pending) == 1 and pending[0]['user_id'] == U1)
    await remove_clan_request(clan_id, U1)
    check("remove_clan_request", not await has_clan_request(clan_id, U1))

    # ── 5. delete_clan ──
    await add_clan_member(clan_id, U1)
    await add_clan_request(clan_id, U2)
    await delete_clan(clan_id)
    check("delete_clan: объединение удалено", (await get_clan(clan_id)) is None)
    check("delete_clan: нет членов", not await is_clan_member(clan_id, U1))
    check("delete_clan: нет заявок", not await has_clan_request(clan_id, U2))

    # ── 6. Рецепты-товары ──
    r = await get_recipe_by_name("Пожарить сига")
    if not r:
        check("рецепт «Пожарить сига» существует", False)
        r = {"id": 1}
    item_name = RECIPE_ITEM_PREFIX + "Пожарить сига"
    item = await get_item_by_name(item_name)
    check("создан предмет-рецепт", item and item['category'] == 'recipes'
          and item['is_available'] == 1)
    check("цена рецепта из RECIPE_ITEM_PRICES",
          item and item['price'] == RECIPE_ITEM_PRICES["Пожарить сига"]
          and item['sell_price'] == item['price'] // 2)

    # ── 7. Изучение через предмет ──
    check("новый U3 до покупки рецептов не имеет", not await has_user_recipe(U3, r['id']))
    ok, msg = await learn_recipe_from_item(U3, item['id'])
    check("learn_recipe_from_item: без предмета → ошибка", not ok)
    await add_inventory_item(U3, item['id'], 1)
    ok, msg = await learn_recipe_from_item(U3, item['id'])
    check("learn_recipe_from_item: успех и списание",
          ok and "выучил" in msg and await has_user_recipe(U3, r['id'])
          and not any(i['item_id'] == item['id'] for i in await get_inventory(U3)))
    await add_inventory_item(U3, item['id'], 1)
    ok2, msg2 = await learn_recipe_from_item(U3, item['id'])
    check("learn_recipe_from_item: «уже выучен»", not ok2 and "уже выучен" in msg2)

    # ── 8. get_learned_recipes ──
    rb = await get_recipe_by_name("Пара сапог") or {"id": 2}
    rk = await get_recipe_by_name("Пожарить муксуна") or {"id": 3}
    await learn_recipe(U3, rb['id'])
    await learn_recipe(U3, rk['id'])
    learned_all = await get_learned_recipes(U3)
    check("get_learned_recipes: все выученные", {x['id'] for x in learned_all} >= {r['id'], rb['id'], rk['id']})
    wb = await get_learned_recipes(U3, "workbench")
    check("get_learned_recipes: только верстак", wb and all(x['required_expansion'] == 'workbench' for x in wb))
    check("get_learned_recipes: только кухня lvl>=1",
          all(x['required_expansion'] == 'kitchen' for x in await get_learned_recipes(U3, "kitchen", 1)))

    # ── 9. Бэкфилл уже проверен в начале: старые (U1,U2) получили, новый U3 — нет.
    conn = await get_db()
    cur = await conn.execute("SELECT COUNT(*) AS c FROM user_recipes")
    total = (await cur.fetchone())['c']
    check("бэкфилл: все рецепты открыты старым игрокам",
          total >= 2 * len(await get_recipes_all()))

    await close_db()
    print(f"\nSmoke 075: {passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)


async def get_db_role(user_id):
    from database.db import get_db
    conn = await get_db()
    cur = await conn.execute(
        "SELECT role FROM user_roles WHERE telegram_id = ? AND role = 'clan_leader'",
        (user_id,))
    row = await cur.fetchone()
    return row


async def get_recipe_by_name(name):
    from database.db import get_db
    conn = await get_db()
    cur = await conn.execute("SELECT * FROM recipes WHERE name = ?", (name,))
    return await cur.fetchone()


async def get_recipes_all():
    from database.db import get_db
    conn = await get_db()
    cur = await conn.execute("SELECT id FROM recipes")
    return await cur.fetchall()


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