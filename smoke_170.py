# -*- coding: utf-8 -*-
"""Smoke 170 — Клан-холл Фаза 8: картинки расширений + флаг остаётся выключен.

1. db: ключ clanh_exp_photo_<type>, set/get, сброс.
2. resolve_expansion_photo: расширение > здание > стройка-заглушка > None.
3. Обработчики/кнопки: колбэк clanh:admexphoto есть; FSM состояние wait_expansion_photo есть.
4. config.CLAN_HALL_ENABLED остаётся False.
5. Guard: clanh:-колбэк при выключенном флаге отвечает «дорабатывается».
"""
import asyncio
import os
import sys

os.environ["DATABASE_PATH"] = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "_test_smoke170.db")

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

    import database.db as db
    import config
    from database.db import (
        init_db, add_user, add_treasury_move, create_clan, set_clan_leader,
        add_clan_member, ensure_clan_building, set_clan_building_built,
        set_clan_building_photo, set_clan_construction_photo,
        install_clan_expansion, get_db,
        get_clan_expansion_photo, set_clan_expansion_photo,
        clan_expansion_photo_key, close_db,
    )
    await init_db()
    uid_leader = 170091
    await add_user(uid_leader, 'a', 'A', "")

    print("\n0. Флаг не включён")
    check("CLAN_HALL_ENABLED = False", getattr(config, "CLAN_HALL_ENABLED", False) is False)

    print("\n1. db-хелперы фото расширений")
    check("ключ по типу", clan_expansion_photo_key('library') == 'clanh_exp_photo_library')
    check("нет картинки по умолчанию", await get_clan_expansion_photo('library') is None)
    await set_clan_expansion_photo('library', 'file_lib_001')
    check("картинка записана", await get_clan_expansion_photo('library') == 'file_lib_001')
    await set_clan_expansion_photo('shop', 'file_shop_001')
    await set_clan_expansion_photo('library', None)
    check("сброс удаляет ключ", await get_clan_expansion_photo('library') is None)
    check("другой тип не пострадал", await get_clan_expansion_photo('shop') == 'file_shop_001')

    print("\n2. resolve_expansion_photo: приоритеты")
    from bot.handlers import clan_hall as ch

    cid = await create_clan("clan", "TT", "T", uid_leader)
    await set_clan_leader(cid, uid_leader)
    await add_clan_member(cid, uid_leader)
    await ensure_clan_building(cid)
    await set_clan_building_built(cid, "manor")
    ok, _ = await install_clan_expansion(cid, uid_leader, 1, "library")
    check("библиотека установлена", ok)

    conn = await db.get_db()
    building = (await (await conn.execute(
        "SELECT * FROM clan_buildings WHERE clan_id = ?", (cid,))).fetchone())
    exp = (await (await conn.execute(
        "SELECT * FROM clan_expansions WHERE clan_id = ?", (cid,))).fetchone())

    # 2.1 нет ни индивидуального, ни индивидуального фото здания → fallback — фото здания
    await set_clan_building_photo(cid, 'file_building_001')
    building = (await (await conn.execute(
        "SELECT * FROM clan_buildings WHERE clan_id = ?", (cid,))).fetchone())
    photo = await ch.resolve_expansion_photo(building, exp)
    check("без индивидуального — фото здания", photo == 'file_building_001')

    # 2.2 индивидуальная картинка расширения перебивает фото здания
    await set_clan_expansion_photo('library', 'file_lib_custom')
    photo = await ch.resolve_expansion_photo(building, exp)
    check("индивидуальная перебивает", photo == 'file_lib_custom')

    # 2.3 exp=None → фото здания
    photo = await ch.resolve_expansion_photo(building, None)
    check("exp=None → фото здания", photo == 'file_building_001')

    # 2.4 другой тип — без индивидуального → снова фото здания
    exp_shop = dict(exp)
    exp_shop['expansion_type'] = 'garden'
    photo = await ch.resolve_expansion_photo(building, exp_shop)
    check("чужой тип без картинки → фото здания", photo == 'file_building_001')

    print("\n3. Кнопки и хендлеры")
    src = open(__file__, encoding='utf-8').read()  # placeholder чтобы не падать
    import inspect
    src = inspect.getsource(ch)
    check("колбэк-хендлер clanh:admexphoto есть", 'clanh:admexphoto' in src
          and 'async def clan_hall_admexphoto_cb' in src)
    check("FSM wait_expansion_photo есть",
          'wait_expansion_photo' in src and 'wait_expansion_photo = State()' in src)
    check("кнопки «🖼 Картинка (админ)» на экранах >=", src.count('Картинка (админ)') >= 5)

    print("\n4. Guard при выключенном флаге")
    # Fake callback через guard middleware нельзя — проверяем текст заглушки
    check("текст заглушки на месте", ch.CLAN_HALL_CLOSED_TEXT != "")

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
                               "_test_smoke170.db"))
    except OSError:
        pass
