"""Smoke v0.15.22: логирование переходов по локациям.

log_location_visit пишет в location_visits и увеличивает счётчик locations.visits.
get_location_visit_stats / get_location_visit_totals собирают агрегаты для админки.
Плюс проверки разводки: вызовы log_location_visit в точках входа (locations.py,
legacy city:* маршруты, housing, wall) и кнопка «Популярность локаций» (locstat:7).

Запуск: .venv\\Scripts\\python.exe smoke_081.py
"""
import asyncio
import os
import sys

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke081.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB

sys.path.insert(0, os.path.dirname(__file__))


async def run():
    from database.db import (
        init_db, close_db, add_user,
        log_location_visit, get_location_visit_stats,
        get_location_visit_totals, prune_location_visits, get_db,
    )

    await init_db()
    uid1, uid2 = 999081, 999082
    await add_user(uid1, "tester1", "Тест1", "")
    await add_user(uid2, "tester2", "Тест2", "")

    passed = 0
    failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
        else:
            failed += 1
            print(f"  FAIL: {name}")

    # ── 1. входы пишутся в location_visits + счётчик локации ──
    await log_location_visit(uid1, "park")
    await log_location_visit(uid1, "park")
    await log_location_visit(uid1, "park")
    await log_location_visit(uid2, "park")
    await log_location_visit(uid1, "bank")
    await log_location_visit(uid1, "wall")

    db = await get_db()
    cur = await db.execute("SELECT COUNT(*) AS c FROM location_visits")
    check("location_visits: 6 строк", (await cur.fetchone())['c'] == 6)

    cur = await db.execute("SELECT visits FROM locations WHERE key = 'park'")
    row = await cur.fetchone()
    check("locations.park.visits = 4", row and row['visits'] == 4)
    cur = await db.execute("SELECT visits FROM locations WHERE key = 'bank'")
    row = await cur.fetchone()
    check("locations.bank.visits = 1", row and row['visits'] == 1)

    # ── 2. агрегаты ──
    totals = await get_location_visit_totals(None)
    check("totals: 6 входов", totals and totals['visits'] == 6)
    check("totals: 2 игрока", totals and totals['players'] == 2)

    stats = await get_location_visit_stats(None)
    top = stats[0]
    check("топ = park (4 входа)", top and top['location_key'] == 'park' and top['visits'] == 4)
    check("park: 2 игрока", top and top['players'] == 2)
    names = [r['location_key'] for r in stats]
    check("wall участвует как аспект", "wall" in names)
    wall_row = next((r for r in stats if r['location_key'] == 'wall'), None)
    check("wall: имя = ключ (нет в locations)", wall_row and wall_row['name'] == 'wall')

    # ── 3. периодной фильтр ──
    day_stats = await get_location_visit_stats(1)
    check("за сегодня всё учтено", sum(r['visits'] for r in day_stats) == 6)

    # ── 4. прунинг: старая запись удаляется, свежие остаются ──
    await db.execute(
        "INSERT INTO location_visits (user_id, location_key, created_at) "
        "VALUES (?, ?, datetime('now', '-5 days'))", (uid1, "hq"))
    await db.commit()
    pruned = await prune_location_visits(3)
    check("prune(3): удалена старая запись", pruned == 1)
    after = await get_location_visit_totals(None)
    check("свежие записи остались", after and after['visits'] == 6)

    # ── 5. разводка по точкам входа ──
    def source_has(path, needle):
        with open(path, "r", encoding="utf-8") as f:
            return needle in f.read()

    root = os.path.dirname(__file__)
    check("locations.py: вызов log_location_visit", source_has(
        os.path.join(root, "bot", "handlers", "locations.py"), "log_location_visit("))
    for fname, needle in (
        ("pilots.py", 'log_location_visit(callback.from_user.id, "townhall")'),
        ("clans.py", 'log_location_visit(callback.from_user.id, "townhall")'),
        ("library.py", 'log_location_visit(callback.from_user.id, "library")'),
        ("dungeon.py", 'log_location_visit(callback.from_user.id, "contracts")'),
        ("housing.py", 'log_location_visit(uid, "housing")'),
        ("wall.py", 'log_location_visit(callback.from_user.id, "wall")'),
    ):
        check(f"{fname}: legacy/аспект логируется", source_has(
            os.path.join(root, "bot", "handlers", fname), needle))
    check("admin.py: хендлер locstat:", source_has(
        os.path.join(root, "bot", "handlers", "admin.py"), "locstat:"))
    check("admin.py: импорт статистики", source_has(
        os.path.join(root, "bot", "handlers", "admin.py"), "get_location_visit_stats"))
    check("keyboards.py: кнопка locstat:7", source_has(
        os.path.join(root, "keyboards", "keyboards.py"), "locstat:7"))

    await close_db()
    print(f"\nSmoke 081: {passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    try:
        asyncio.run(run())
    except SystemExit:
        raise
    except Exception as e:
        from database.db import close_db
        asyncio.run(close_db())
        print(f"SMOKE ERROR: {e!r}")
        sys.exit(1)