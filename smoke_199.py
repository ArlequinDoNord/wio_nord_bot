# -*- coding: utf-8 -*-
"""Smoke 199 — строка «Откуда получить» в карточке предмета «Хранилища».

1. Ягода леса из пула зоны → источник «ягоды леса — опушка/прогалина».
2. Дроп врага (шкура медведя) → источник «враг … — лес».
3. Ягода убрана из зоны → источников не осталось (строка не показывается).
4. Несуществующий предмет → пустой список.
5. Строка есть только в карточке хранилища (storage_item), а не в редакторе.
"""
import os
import sys

os.environ["DATABASE_PATH"] = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "_test_smoke199.db")
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
                             get_item_sources, get_berry_pool, remove_berry_from_zone,
                             get_source_enemy_by_key)

    await init_db()
    await ensure_forest_enemies()

    print("\n1. Ягода из пула зоны")
    berry = await get_item_by_name("Горсть черники")
    sources = await get_item_sources(berry["id"])
    check("черника: есть источник «ягоды леса — опушка»",
          any(s.startswith("ягоды леса — опушка леса") for s in sources))

    print("\n2. Дроп врага")
    skin = await get_item_by_name("Шкура медведя")
    sources = await get_item_sources(skin["id"])
    check("шкура медведя: источник — враг в лесу",
          any(s.startswith("враг «") and s.endswith("— лес") for s in sources))

    print("\n3. Ягода убрана из зоны")
    glade = await get_berry_pool("glade")
    ref = next(r["ref"] for r in glade if r["name"] == "Горсть черники")
    await remove_berry_from_zone("glade", ref)
    sources = await get_item_sources(berry["id"])
    check("черника без пула: источника «опушка» нет",
          not any("опушка леса" in s for s in sources))

    print("\n4. Несуществующий предмет")
    check("id 999999 → пустой список", await get_item_sources(999999) == [])

    print("\n5. Карточка хранилища содержит строку")
    import inspect
    from bot.handlers import admin
    src = inspect.getsource(admin.storage_item)
    check("storage_item вызывает get_item_sources", "get_item_sources(item_id)" in src)
    check("строка выводится с подписью", "📍 Откуда получить" in src)
    edit_src = inspect.getsource(admin.edit_item_photo)
    check("редактор предмета строку не выводит", "Откуда получить" not in edit_src)

    print(f"\nИТОГО: {passed} passed, {failed} failed")
    await close_db()
    return failed


if __name__ == "__main__":
    import asyncio
    sys.exit(asyncio.run(main()))
