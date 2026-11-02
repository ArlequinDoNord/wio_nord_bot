# -*- coding: utf-8 -*-
"""Smoke 197 — редактор ягод леса по зонам (как грибы).

1. Пул засеян из таблицы: опушка — черника 50%; прогалина — 5 позиций (с медведем).
2. Медведь включён один раз миграцией и отображается как «Медведь».
3. Шанс правится (admin_tuned), добавляется ресурс, убирается позиция.
4. Новая ягода создаётся скрытой, с ценой продажи, и попадает в пул зоны.
5. Повтор засева не перезаписывает правки админа.
"""
import asyncio
import os
import sys

os.environ["DATABASE_PATH"] = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "_test_smoke197.db")

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
    from database.db import (init_db, close_db, get_item_by_name, ensure_forest_enemies,
                             get_berry_pool, set_berry_chance, add_berry_to_zone,
                             remove_berry_from_zone, create_berry_item, berry_zone_total,
                             get_berry_candidates)

    await init_db()
    await ensure_forest_enemies()

    print("\n1. Засев пула из таблицы")
    glade = await get_berry_pool("glade")
    check("опушка: одна позиция — черника 50%",
          len(glade) == 1 and glade[0]["name"] == "Горсть черники" and glade[0]["chance"] == 50)
    clearing = await get_berry_pool("clearing")
    names = {r["name"]: r["chance"] for r in clearing}
    check("прогалина: 5 позиций", len(clearing) == 5)
    check("прогалина: медведь 5%", names.get("Медведь") == 5)
    check("прогалина: пламенные ягоды 10%", names.get("Горсть Пылающих ягод") == 10)
    check("прогалина: сумма 100%", await berry_zone_total("clearing") == 100)

    print("\n2. Медведь включён")
    bear = await db.get_source_enemy_by_key("forest", "bear")
    check("медведь включён миграцией", bear is not None and bear["enabled"] == 1)

    print("\n3. Правка шанса, добавление, удаление")
    await set_berry_chance("glade", glade[0]["ref"], 40)
    glade = await get_berry_pool("glade")
    check("шанс черники на опушке стал 40%", glade[0]["chance"] == 40)
    cands = await get_berry_candidates("glade")
    check("в списке для добавления нет уже существующих",
          all(c["name"] != "Горсть черники" for c in cands))
    raspberry = await get_item_by_name("Горсть малины")
    await add_berry_to_zone("glade", raspberry["id"], 15)
    names = {r["name"]: r["chance"] for r in await get_berry_pool("glade")}
    check("малина добавлена на опушку 15%", names.get("Горсть малины") == 15)
    await remove_berry_from_zone("glade", f"item:{raspberry['id']}")
    check("малина убрана с опушки",
          "Горсть малины" not in {r["name"] for r in await get_berry_pool("glade")})

    print("\n4. Создание новой ягоды")
    fid = await create_berry_item("glade", "Горсть брусники", 7, 12, added_by=1)
    check("ягода создана", fid > 0)
    item = await get_item_by_name("Горсть брусники")
    check("скрыта из магазина, не на рынке",
          item is not None and item["is_available"] == 0 and item["market_ok"] == 0)
    check("цена продажи задана", item is not None and item["sell_price"] == 7)
    check("попала в пул опушки 12%",
          {r["name"]: r["chance"] for r in await get_berry_pool("glade")}.get("Горсть брусники") == 12)
    check("повтор создания отказан", await create_berry_item("glade", "Горсть брусники", 7, 12) == 0)

    print("\n5. Повторный засев не трогает правки админа")
    await ensure_forest_enemies()
    glade = await get_berry_pool("glade")
    check("шанс черники остался 40%", next(r for r in glade if r["name"] == "Горсть черники")["chance"] == 40)
    conn = await db.get_db()
    await conn.execute("UPDATE forest_enemies SET enabled = 0 WHERE key = 'bear'")
    await conn.commit()
    await ensure_forest_enemies()
    bear = await db.get_source_enemy_by_key("forest", "bear")
    check("выключенный админом медведь не включается обратно", bear is not None and bear["enabled"] == 0)

    print(f"\nИТОГО: {passed} passed, {failed} failed")
    await close_db()
    return failed


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
