# -*- coding: utf-8 -*-
"""Smoke 171 — Фаза 8 ч2: админ-менеджер картинок клан-холла.

1. Кнопка «🖼 Картинки клан-холла» в админ-панели (keyboards).
2. Роутер зарегистрирован в main.py (import + include + middleware цикл).
3. db: get_all_clan_buildings (join clans, только kind='clan').
4. Установка индивидуальной картинки здания работает во время стройки/сбора
   и не мешает статусу; видна (resolve) после built, не видна до.
5. FSM/хендлеры: clanhph:menu, clanhph:exp:<type>, clanhph:construction,
   clanhph:bclan:<id>; состояния wait_exp_photo/wait_building_photo.
6. Флаг CLAN_HALL_ENABLED остаётся False.
"""
import asyncio
import os
import sys

os.environ["DATABASE_PATH"] = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "_test_smoke171.db")

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
            print(f"  FAIL: {name}")

    import io
    import database.db as db
    import config
    from database.db import (
        init_db, add_user, create_clan, set_clan_leader, add_clan_member,
        ensure_clan_building, choose_clan_building, start_clan_building_project,
        set_clan_building_photo, set_clan_building_built, install_clan_expansion,
        get_all_clan_buildings, get_clan_building, close_db,
    )
    await init_db()

    print("\n0. Флаг включён (v0.39.8 — открытие клан-холла)")
    check("CLAN_HALL_ENABLED = True",
          getattr(config, "CLAN_HALL_ENABLED", False) is True)

    print("\n1. Админ-панель: кнопка")
    kb_src = io.open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  "keyboards", "keyboards.py"),
                     encoding='utf-8', errors='replace').read()
    check("кнопка «🖼 Картинки клан-холла» под can_manage_clans",
          'Картинки клан-холла' in kb_src and 'clanhph:menu' in kb_src
          and kb_src.find('Картинки клан-холла') > kb_src.find('can_manage_clans'))

    print("\n2. main.py: регистрация и middleware")
    main_src = io.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py"),
                       encoding='utf-8', errors='replace').read()
    check("import admin_clanphotos_router", 'admin_clanphotos_router' in main_src)
    check("include_router", 'include_router(admin_clanphotos_router)' in main_src)
    check("в middleware-цикле", 'admin_shop_clan_router, admin_clanphotos_router' in main_src)

    print("\n3. Модуль: хендлеры и FSM")
    mp = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      "bot", "handlers", "admin_clanphotos.py")
    mp_src = io.open(mp, encoding='utf-8', errors='replace').read()
    for cb in ('clanhph:menu', 'clanhph:exp:', 'clanhph:construction',
               'clanhph:buildings', 'clanhph:bclan:'):
        check(f"хендлер {cb}", cb in mp_src)
    check("FSM состояния", all(s in mp_src for s in
          ('wait_exp_photo', 'wait_building_photo', 'wait_construction_photo')))
    check("право can_manage_clans проверяется", 'can_manage_clans' in mp_src)

    print("\n4. db: get_all_clan_buildings")
    L = 171001
    await add_user(L, 'a', 'A', "")
    cid = await create_clan("clan", "TT", "Издание", L)
    await set_clan_leader(cid, L)
    await add_clan_member(cid, L)
    await ensure_clan_building(cid)
    ok, _ = await choose_clan_building(cid, L, 'manor')
    check("buildings: 1 при статусе funding",
          len(await get_all_clan_buildings()) == 1)

    print("\n5. Фото здания во время стройки → видно после built")
    b0 = await get_clan_building(cid)
    check("building_photo до установки пуст", not (b0.get('building_photo_file_id') or '').strip())
    await set_clan_building_photo(cid, 'file_building_future')
    b1 = await get_clan_building(cid)
    check("фото установлено при status funding",
          (b1.get('building_photo_file_id') or '').strip() == 'file_building_future')
    check("статус не изменился", b1['status'] == 'funding')

    from bot.handlers import clan_hall as ch
    # до built: resolve отдаёт заглушку (её нет → None), но НЕ будущую картинку
    b = await get_clan_building(cid)
    check("до built future-фото не отдаётся",
          await ch.resolve_clan_hall_photo(b) is None)
    # built — отдаётся
    await set_clan_building_built(cid, 'manor')
    b = await get_clan_building(cid)
    check("после built resolve = future-фото",
          await ch.resolve_clan_hall_photo(b) == 'file_building_future')

    print("\n6. Несколько кланов: только kind='clan'")
    parties = await create_clan("party", "TT", "Паттия", L)
    # second clan of same leader not possible → use foreign uid
    L2 = 171002
    await add_user(L2, 'b', 'B', "")
    cid2 = await create_clan("clan", "TT2", "Второй", L2)
    await set_clan_leader(cid2, L2)
    await add_clan_member(cid2, L2)
    await ensure_clan_building(cid2)
    check("get_all_clan_buildings = 2 клановых здания",
          len(await get_all_clan_buildings()) == 2)

    print(f"\nИТОГО: {passed} passed, {failed} failed")
    await close_db()
    if failed:
        sys.exit(1)


try:
    asyncio.run(main())
except Exception:
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    try:
        os.remove(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "_test_smoke171.db"))
    except OSError:
        pass
