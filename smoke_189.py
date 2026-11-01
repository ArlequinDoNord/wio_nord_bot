# -*- coding: utf-8 -*-
"""Smoke 189 — редактор находок со дна по водоёмам.

1. Засев один раз: удалённая админом находка не возвращается при повторном старте.
2. Добавление из пула и создание новой находки (с дубликатами).
3. Выпадение: по шансам водоёма, пустой водоём — None, подсказка без фолбэка.
4. Водохранилище не затронуто правками озера.
"""
import asyncio
import os
import sys

os.environ["DATABASE_PATH"] = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "_test_smoke189.db")

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

    import database.db as db
    from database.db import (init_db, close_db, add_item, get_item_by_name,
                             ensure_water_fish, get_water_junk_rows, get_water_junk_map,
                             get_junk_pool, get_water_junk_row, add_water_junk,
                             remove_water_junk, create_water_junk, update_water_junk)
    from bot.handlers.fishing import _pick_junk, junk_hint

    await init_db()
    await ensure_water_fish()

    print("\n1. Засев один раз")
    lake = await get_water_junk_rows("lake")
    check("озеро засеяно 2 находками", len(lake) == 2)
    boot = next(r for r in lake if r['name'] == "Старый сапог")
    check("удаление сапога", await remove_water_junk(boot['id']))
    await ensure_water_fish()
    names = [r['name'] for r in await get_water_junk_rows("lake")]
    check("после повторного старта сапог не вернулся", "Старый сапог" not in names)
    check("водоросли на месте", "Кусочек водорослей" in names)

    print("\n2. Добавление из пула и создание")
    await add_item(name="Тест-банка", description="x", price=0, sell_price=7, rarity=1,
                   category="resource", stock=-1, added_by=0, ap_cost=0, damage=0, heal=0)
    pool = [r['name'] for r in await get_junk_pool("lake")]
    check("ресурс попадает в пул", "Тест-банка" in pool)
    check("уже существующая находка не в пуле", "Кусочек водорослей" not in pool)
    jid = await add_water_junk("lake", "Тест-банка", 50)
    check("добавлено из пула", jid > 0)
    check("повторное добавление отказано", await add_water_junk("lake", "Тест-банка", 50) == 0)
    check("из пула исчезло", "Тест-банка" not in [r['name'] for r in await get_junk_pool("lake")])
    cid = await create_water_junk("lake", "Тест-ботинок", 3, 30, description="старый",
                                  added_by=0)
    check("создано новое", cid > 0)
    check("дубликат создания отказан",
          await create_water_junk("lake", "Тест-ботинок", 3, 30) == 0)
    item = await get_item_by_name("Тест-ботинок")
    check("новый предмет скрыт из магазина", item is not None and item['is_available'] == 0)
    check("новый предмет — ресурс", item is not None and item['category'] == "resource")
    from bot.handlers.fishing import junk_photo
    conn = await db.get_db()
    await conn.execute("UPDATE items SET photo_file_id = 'FID_ITEM' WHERE name = 'Тест-ботинок'")
    await conn.commit()
    check("без своего фото — картинка предмета из хранилища",
          await junk_photo("lake", "Тест-ботинок") == "FID_ITEM")
    fid = await create_water_junk("lake", "Тест-склянка", 2, 10, photo_file_id="FID_GLASS")
    check("создано с фото", fid > 0)
    check("фото на находке водоёма",
          (await get_water_junk_map("lake")).get("Тест-склянка", {}).get("photo_file_id") == "FID_GLASS")
    check("фото попало в предмет хранилища",
          (await get_item_by_name("Тест-склянка"))['photo_file_id'] == "FID_GLASS")
    check("junk_photo отдаёт фото водоёма", await junk_photo("lake", "Тест-склянка") == "FID_GLASS")

    print("\n3. Выпадение по шансам водоёма")
    # Кусочек водорослей остаётся с 15%, Тест-банка 50%, Тест-ботинок 30%
    counts = {}
    for _ in range(300):
        r = await _pick_junk("lake")
        counts[r] = counts.get(r, 0) + 1
    check("выпадают только находки водоёма (или None)",
          set(counts) <= {"Кусочек водорослей", "Тест-банка", "Тест-ботинок", "Тест-склянка", None})
    check("Тест-банка (50%) выпадает чаще Тест-ботинка (30%)",
          counts.get("Тест-банка", 0) > counts.get("Тест-ботинок", 0))
    hint = await junk_hint("lake")
    check("подсказка перечисляет все находки", "Тест-банка 50%" in hint and "Тест-ботинок 30%" in hint)

    for row in await get_water_junk_rows("lake"):
        await remove_water_junk(row['id'])
    empty_ok = True
    for _ in range(20):
        if await _pick_junk("lake") is not None:
            empty_ok = False
    check("пустой водоём: выпадения нет", empty_ok)
    check("пустой водоём: подсказка", await junk_hint("lake") == "(находок со дна нет)")
    check("пустой водоём: карта пуста", await get_water_junk_map("lake") == {})

    print("\n4. Водохранилище не затронуто")
    resv = await get_water_junk_rows("reservoir")
    check("водохранилище сохранило 2 находки", len(resv) == 2)
    check("правки озера не задели водохранилище",
          (await get_water_junk_map("reservoir")).get("Старый сапог", {}).get("chance") == 2)

    print(f"\nИТОГО: {passed} passed, {failed} failed")
    await close_db()
    return failed


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
