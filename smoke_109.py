"""Smoke 109 — отчётные сутки отчёта, loot-only добыча врагов, силы пилота в регионе.

Проверяет:
  1. report_day_label_for: подпись суток КОНКРЕТНОГО отчёта (отчёт до 10:00 МСК
     относится к прошлым суткам, а не к текущим).
  2. created_at_msk: время сдачи в МСК, а не сырой UTC.
  3. report_payout_context(cycle_day=...) считает лимит и подписывает сутки отчёта.
  4. correct_report_numbers и approve_report считают по суткам самого отчёта.
  5. Лут кабана и моллюска: is_available=0, market_ok=0, loot_only=1.
  6. wing_members_report_farms отдаёт region_troops — «всего» пилота в регионе.
"""
import asyncio
import os
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

PASS, FAIL = 0, 0


def check(name, cond):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  OK  {name}")
    else:
        FAIL += 1
        print(f"FAIL  {name}")


MSK = timezone(timedelta(hours=3))


async def main():
    global DB_PATH
    import config
    from config import (
        REPORT_DAY_START_HOUR, REPORT_DAY_START_MINUTE,
        MOLLUSK_ENEMY_DROPS,
    )
    from database.db import FOREST_ENEMY_DROPS
    DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_test_smoke109.db")
    for suffix in ("", "-wal", "-shm"):
        try:
            os.remove(DB_PATH + suffix)
        except OSError:
            pass
    config.DB_PATH = DB_PATH

    import database.db as db
    db.DB_PATH = DB_PATH
    from database.db import (
        init_db, close_db, add_user, add_report, approve_report, correct_report_numbers,
        get_db, report_day_label_for, report_day_label, report_day_value_of,
        created_at_msk, today_report_day, report_payout_context,
        ensure_forest_items, ensure_mollusk_items, ensure_forest_enemies,
        ensure_fishing_enemies, wing_members_report_farms,
    )

    await init_db()

    # ── 1. Подписи суток ──────────────────────────────────────────────────
    print("\n= Подписи отчётных суток =")
    check("REPORT_DAY_START = 10:00", (REPORT_DAY_START_HOUR, REPORT_DAY_START_MINUTE) == (10, 0))
    lbl = report_day_label_for("2026-09-29")
    check(f"сутки 29.09 = {lbl}", lbl == "29.09 10:00 — 30.09 10:00")
    lbl_next = report_day_label_for("2026-09-30")
    check(f"сутки 30.09 = {lbl_next}", lbl_next == "30.09 10:00 — 01.10 10:00")
    check("отчёт за 29.09 и за 30.09 — разные сутки", lbl != lbl_next)
    check("report_day_label(-1) — предыдущие сутки",
          report_day_label(-1) == report_day_label_for(today_report_day())
          or report_day_label(-1) != report_day_label(0))

    # Граница: отчёт, сданный в 08:40 МСК 30.09, относится к суткам 29.09.
    created_0840 = "2026-09-30 05:40:00"   # 08:40 МСК = 05:40 UTC
    day_0840 = report_day_value_of(created_0840)
    check(f"08:40 МСК 30.09 → сутки {day_0840}", day_0840 == "2026-09-29")
    check("подпись этих суток — 29.09, а не 30.09",
          report_day_label_for(day_0840) == "29.09 10:00 — 30.09 10:00")

    # Граница: ровно в 10:00 МСК отчёт уже за новые сутки.
    day_1000 = report_day_value_of("2026-09-30 07:00:00")   # 10:00 МСК
    check(f"10:00 МСК 30.09 → сутки {day_1000}", day_1000 == "2026-09-30")

    # ── 2. Время сдачи в МСК ──────────────────────────────────────────────
    print("\n= Время сдачи =")
    check("05:40 UTC → 30.09 08:40 МСК", created_at_msk(created_0840) == "30.09 08:40")
    check("07:00 UTC → 30.09 10:00 МСК", created_at_msk("2026-09-30 07:00:00") == "30.09 10:00")
    check("пустое время не падает", created_at_msk(None) == "—" and created_at_msk("") == "—")

    # ── 3. Отчёт из прошлых суток: лимит и подпись ────────────────────────
    print("\n= Отчёт из прошлых суток =")
    UA = 500001
    await add_user(UA, "alpha", "Alpha", "Пилот")

    prev_day = today_report_day()
    # Создаём отчёт «из прошлых суток»: сутки минус один от текущих.
    old_day = (datetime.strptime(prev_day, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
    # Сдача внутри суток old_day: 11:40 МСК = 08:40 UTC того же дня (окно 10:00→10:00).
    old_created = datetime.strptime(old_day, "%Y-%m-%d").replace(
        hour=8, minute=40).strftime("%Y-%m-%d %H:%M:%S")
    check(f"подставленное created_at → сутки {report_day_value_of(old_created)}",
          report_day_value_of(old_created) == old_day)

    conn = await get_db()
    rid_old, _ = await add_report(UA, "shot", 500, 5000, "7")
    await conn.execute("UPDATE reports SET created_at = ? WHERE id = ?",
                       (old_created, rid_old))
    await conn.commit()

    # Сегодняшний отчёт того же пилота съедает лимит ТЕКУЩИХ суток.
    rid_today, credited_today = await add_report(UA, "shot", 900, 5900, "7")
    check("сегодняшний отчёт оплачен по лимиту текущих суток", credited_today == 900)

    ctx_old = await report_payout_context(UA, 800, 6000, exclude_id=rid_old,
                                          cycle_day=old_day)
    check(f"подпись суток отчёта: {ctx_old['day_label']}",
          ctx_old['day_label'] == report_day_label_for(old_day))
    check("лимит считается по суткам отчёта, а не сегодняшним (assigned_today=0)",
          ctx_old["assigned_today"] == 0)
    ctx_now = await report_payout_context(UA, 800, 6000, exclude_id=rid_old)
    check("без cycle_day подпись — текущие сутки", ctx_now["day_label"] == report_day_label())

    # ── 4. correct_report_numbers: сутки и лимит по отчёту ────────────────
    print("\n= Правка цифр =")
    fix = await correct_report_numbers(rid_old, 700, 6100)
    check("правка не сломалась", not fix.get("error"))
    check(f"подпись суток при правке: {fix['day_label']}",
          fix["day_label"] == report_day_label_for(old_day))
    check("лимит при правке — по суткам отчёта", fix["assigned_today"] == 0)

    # ── 5. Лут врагов — только с врагов ──────────────────────────────────
    print("\n= Лут только с врагов =")
    await ensure_forest_items()
    await ensure_mollusk_items()
    await ensure_forest_enemies()
    await ensure_fishing_enemies()
    conn = await get_db()
    for name in FOREST_ENEMY_DROPS + MOLLUSK_ENEMY_DROPS:
        row = await (await conn.execute(
            "SELECT is_available, market_ok, IFNULL(loot_only, 0) AS lo "
            "FROM items WHERE name = ?", (name,))).fetchone()
        ok = row is not None and row['is_available'] == 0 and row['market_ok'] == 0 and row['lo'] == 1
        check(f"{name}: вне магазина, вне рынка, loot_only", ok)

    from database.db import get_available_items
    shop_names = {i['name'] for i in await get_available_items()}
    check("ни один лут врага не в магазине",
          not (set(FOREST_ENEMY_DROPS) | set(MOLLUSK_ENEMY_DROPS)) & shop_names)

    # Крафт/готовые блюда остаются торгуемыми.
    for name in ("Жареное мясо кабана", "Жареное мясо моллюска"):
        row = await (await conn.execute(
            "SELECT market_ok FROM items WHERE name = ?", (name,))).fetchone()
        check(f"{name} (крафт) остаётся на рынке", row is not None and row['market_ok'] == 1)

    # Идемпотентность: повторный seed не возвращает дроп в продажу.
    await conn.execute("UPDATE items SET market_ok = 1, is_available = 1 WHERE name = ?",
                       (FOREST_ENEMY_DROPS[0],))
    await conn.commit()
    await ensure_forest_items()
    row = await (await conn.execute(
        "SELECT is_available, market_ok, IFNULL(loot_only, 0) AS lo FROM items WHERE name = ?",
        (FOREST_ENEMY_DROPS[0],))).fetchone()
    check("повторный seed чинит лут обратно в loot-only",
          row['is_available'] == 0 and row['market_ok'] == 0 and row['lo'] == 1)

    # ── 6. Шанс находки гриба ───────────────────────────────────────────
    print("\n= Шанс находки гриба =")
    from bot.handlers.forest import pick_forest_mushroom, FOREST_EMPTY_CHANCE
    from database.db import FOREST_DEFAULTS
    check("пусто 10% → находка 90%", FOREST_EMPTY_CHANCE == 10)
    pool = [{"name": n, "chance": c} for n, c, _k in FOREST_DEFAULTS]
    check("пул из конфига не пуст", len(pool) >= 5)
    found = sum(1 for i in range(1000)
                if pick_forest_mushroom(pool, i / 10.0) is not None)
    check(f"находка ровно 90% (из 1000 бросков: {found})", found == 900)
    # Веса нормируются: завышенные веса не обрезают хвост пула.
    fat = [{"name": "A", "chance": 500}, {"name": "B", "chance": 500},
           {"name": "Хвост", "chance": 1}]
    last = pick_forest_mushroom(fat, 99.999)
    check("хвост пула не обрезан даже при завышенных весах",
          last is not None and last["name"] == "Хвост")
    check("пусто отрезано до начала пула",
          pick_forest_mushroom(fat, 0.0) is None and pick_forest_mushroom(fat, 9.99) is None)
    check("первый гриб начинается ровно после «пусто»",
          (pick_forest_mushroom(fat, 10.0) or {}).get("name") == "A")
    check("пустой пул не падает", pick_forest_mushroom([], 50.0) is None)
    check("веса нуля = пусто", pick_forest_mushroom([{"name": "A", "chance": 0}], 50.0) is None)

    # ── 7. Силы пилота в регионе для командира ───────────────────────────
    print("\n= Состав формирования =")
    await conn.execute("UPDATE users SET wing = 'red' WHERE user_id = ?", (UA,))
    await conn.commit()
    await approve_report(rid_old, 1)
    await approve_report(rid_today, 1)
    members = await wing_members_report_farms("red")
    me = next((m for m in members if m['user_id'] == UA), None)
    check("пилот найден в крыле", me is not None)
    check(f"регион пилота: {me['region'] if me else None}", me and me['region'] == "7")
    # «Всего» последнего принятого отчёта: у пилота их два (6100 за прошлые сутки
    # и 5900 за текущие), в силы региона идёт более свежий — 5900.
    check(f"region_troops = {me['region_troops'] if me else None}",
          me and me["region_troops"] == 5900)
    check("сумма за прошлые сутки по крылу не пустая", me and me['prev_farm'] >= 0)

    await close_db()
    for suffix in ("", "-wal", "-shm"):
        try:
            os.remove(DB_PATH + suffix)
        except OSError:
            pass

    print(f"\n=== SMOKE 109: {PASS} passed, {FAIL} failed ===")
    return 1 if FAIL else 0


if __name__ == "__main__":
    async def _run():
        try:
            return await main()
        finally:
            # Без закрытия соединения процесс с aiosqlite виснет на выходе.
            try:
                from database.db import close_db
                await close_db()
            except Exception:
                pass
            try:
                import config
                for suffix in ("", "-wal", "-shm"):
                    os.remove(config.DB_PATH + suffix)
            except OSError:
                pass

    sys.exit(asyncio.run(_run()))
