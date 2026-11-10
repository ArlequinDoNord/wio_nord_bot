# -*- coding: utf-8 -*-
"""Smoke 213 — единая градация редкости предметов (v0.43.10).

Шкала взята с предметов «Пламенного Круговорота»:
  r1 — базовое сырьё/еда, r2 — качественное, r3 — редкое (трофеи, событийная
  экипировка), r4 — шедевр, r5 — легендарное.

1. Сиды создают правильную редкость: шкура медведя r3, мухомор r2, грибной
   целебный порошок r2, паутина паука r2, мясо моллюска r2, лётный шлем r3.
2. Волчьи предметы (мясо/шкура/клык) выведены из игры: их нет в items и в
   FOREST_ENEMY_DROPS.
3. Миграция `ensure_item_rarity_unified` исправляет 14 аномалий в старой БД.
4. Миграция одноразовая: повторный запуск ничего не меняет и не перетирает
   ручную правку админа.
"""
import asyncio
import os
import sys

_TEST_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_test_smoke213.db")
os.environ["DATABASE_PATH"] = _TEST_DB

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Тест требует «чистой» БД: флаг миграции item_rarity_unified_v1 одноразовый,
# поэтому остаточный файл от прошлого прогона ломает проверки.
for _suffix in ("", "-wal", "-shm"):
    try:
        os.remove(_TEST_DB + _suffix)
    except OSError:
        pass


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

    import config
    from database.db import (
        init_db, close_db, get_db, add_item, get_item_by_name,
        seed_default_items, ensure_dungeon_shop_items, ensure_forest_items,
        ensure_forest_enemies, ensure_mollusk_items, ensure_item_rarity_unified,
        FOREST_ENEMY_DROPS, ITEM_RARITY_FIXES, RETIRED_ITEMS,
    )

    await init_db()
    await seed_default_items()
    await ensure_dungeon_shop_items()
    await ensure_forest_items()
    await ensure_forest_enemies()      # он же вызывает ensure_forest_berry_items
    await ensure_mollusk_items()

    print("\n1. Редкость в сидах")
    expected = {
        "Шкура медведя": 3,
        "Мухомор": 2,
        "Грибной целебный порошок": 2,
        "Паутина паука": 2,
        "Мясо моллюска": 2,
        "Лётный шлем": 3,
    }
    for name, rarity in expected.items():
        item = await get_item_by_name(name)
        check(f"«{name}» — редкость {rarity}",
              item is not None and int(item["rarity"]) == rarity)

    print("\n2. Волчьи предметы выведены из игры")
    for name in ("Мясо волка", "Шкура волка", "Клык волка"):
        check(f"«{name}» в RETIRED_ITEMS", name in RETIRED_ITEMS)
        check(f"«{name}» нет в items", await get_item_by_name(name) is None)
        check(f"«{name}» нет в FOREST_ENEMY_DROPS", name not in FOREST_ENEMY_DROPS)

    print("\n3. Миграция исправляет аномалии старой БД")
    conn = await get_db()
    # Предметы, которых нет в сидах (создавались админкой / старым кодом).
    legacy = (
        ("Кожаные перчатки пилота", 2),
        ('Походный Нож "Жалость"', 2),
        ("Испорченный муксун", 1),
        ("Испорченный сом", 1),
        ("Испорченный чир", 1),
        ("Испорченный налим", 1),
        ("Испорченный угорь", 1),
        ("Испорченный форель", 1),
    )
    for name, _ in legacy:
        if await get_item_by_name(name) is None:
            await add_item(name=name, description="legacy", price=10, sell_price=5,
                           rarity=5, category="resource", stock=-1, added_by=0)

    # Ломаем редкость у всех 14 целей миграции.
    for name, _ in ITEM_RARITY_FIXES:
        await conn.execute("UPDATE items SET rarity = 5 WHERE name = ?", (name,))
    await conn.commit()

    check("целей миграции ровно 14", len(ITEM_RARITY_FIXES) == 14)
    check("нет дублей в ITEM_RARITY_FIXES",
          len({n for n, _ in ITEM_RARITY_FIXES}) == len(ITEM_RARITY_FIXES))
    check("все целевые редкости в 1..5",
          all(1 <= r <= 5 for _, r in ITEM_RARITY_FIXES))

    changed = await ensure_item_rarity_unified()
    check("обновлено 14 записей", changed == 14)
    for name, rarity in ITEM_RARITY_FIXES:
        item = await get_item_by_name(name)
        check(f"«{name}» стало {rarity}", item is not None and int(item["rarity"]) == rarity)

    print("\n4. Миграция одноразовая и не перетирает ручные правки")
    await conn.execute("UPDATE items SET rarity = 1 WHERE name = 'Шкура медведя'")
    await conn.commit()
    again = await ensure_item_rarity_unified()
    check("повторный запуск — 0 изменений", again == 0)
    skin = await get_item_by_name("Шкура медведя")
    check("ручная правка сохранена (r1)", int(skin["rarity"]) == 1)
    third = await ensure_item_rarity_unified()
    check("третий запуск — 0 изменений", third == 0)

    print("\n5. purge_retired_items чистит витрины и городской склад (регресс FK)")
    from database.db import add_user, purge_retired_items

    uid = 213001
    await add_user(uid, "t", "Pilot 213", "")
    await add_item(name="T-Меч", description="legacy", price=10, sell_price=5,
                   rarity=1, category="equipment", stock=-1, added_by=0)
    sword = await get_item_by_name("T-Меч")
    await conn.execute("INSERT INTO city_storage (item_id, qty) VALUES (?, ?)",
                       (sword["id"], 3))
    await conn.execute(
        "INSERT INTO market_items (seller_id, item_id, price) VALUES (?, ?, ?)",
        (uid, sword["id"], 10))
    await conn.execute(
        "INSERT INTO market_fish (seller_id, item_id, weight, price, remaining_sec) "
        "VALUES (?, ?, 1, 10, 60)", (uid, sword["id"]))
    await conn.execute(
        "INSERT OR IGNORE INTO inventory (user_id, item_id, quantity) VALUES (?, ?, 1)",
        (uid, sword["id"]))
    await conn.commit()

    purged = await purge_retired_items()
    check("purge выполнился без FK-ошибки", purged is True)
    check("«T-Меч» удалён из items", await get_item_by_name("T-Меч") is None)
    for table in ("city_storage", "market_items", "market_fish", "inventory"):
        cur = await conn.execute(
            f"SELECT COUNT(*) AS n FROM {table} WHERE item_id = ?", (sword["id"],))
        check(f"{table}: ссылки очищены", (await cur.fetchone())["n"] == 0)

    await close_db()
    print(f"\nИТОГО: {passed} passed, {failed} failed")
    return failed


if __name__ == "__main__":
    sys.exit(1 if asyncio.run(main()) else 0)
