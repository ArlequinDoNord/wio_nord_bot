# -*- coding: utf-8 -*-
"""Smoke 185 — лут врагов Огненного Лабиринта.

1. Враг с пустым списком дропов (создан раньше предметов) получает дропы из сида.
2. Враг, которого настроил админ (admin_tuned=1), не перезаписывается.
"""
import asyncio
import json
import os
import sys

os.environ["DATABASE_PATH"] = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "_test_smoke185.db")

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

    import database.db as db
    from database.db import init_db, close_db, get_db, ensure_firelab_items, ensure_firelab_enemies

    await init_db()
    conn = await get_db()
    for tbl in ("firelab_enemies",):
        await conn.execute(f"DELETE FROM {tbl}")
        await conn.commit()
    await ensure_firelab_items()
    await ensure_firelab_enemies()

    print("\n1. Пустой лут досеивается из сида")
    await conn.execute("UPDATE firelab_enemies SET drops = '[]', admin_tuned = 0 WHERE key = 'scarecrow'")
    await conn.commit()
    await ensure_firelab_enemies()
    cur = await conn.execute("SELECT drops FROM firelab_enemies WHERE key = 'scarecrow'")
    drops = json.loads((await cur.fetchone())['drops'] or '[]')
    check("у пугала появились дропы", len(drops) > 0)

    print("\n2. Список, заданный админом, не перезаписывается")
    custom = json.dumps([{"item_id": 1, "chance": 0.5, "qty": 1}])
    await conn.execute("UPDATE firelab_enemies SET drops = ?, admin_tuned = 1 WHERE key = 'crow'", (custom,))
    await conn.commit()
    await ensure_firelab_enemies()
    cur = await conn.execute("SELECT drops FROM firelab_enemies WHERE key = 'crow'")
    check("дропы ворона остаются как задал админ",
          json.loads((await cur.fetchone())['drops'] or '[]') == json.loads(custom))

    print(f"\nИТОГО: {passed} passed, {failed} failed")
    await close_db()
    return failed


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
