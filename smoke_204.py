# -*- coding: utf-8 -*-
"""Smoke 204 — денежные штрафы: баланс не уходит в минус, суточные 10%, оплата, отмена.

1. remove_nordmarks не уводит баланс в минус (списывает не больше остатка).
2. Суточное списание: 10% от исходной суммы, не больше остатка.
3. Нехватка: если баланса меньше полного 10%, в этот день ничего не списывается.
4. Повтор в тот же игровой день не списывает второй раз.
5. Оплата пилотом частично и полностью; закрытый штраф не активен.
6. Отмена админом снимает штраф.
"""
import asyncio
import sys

from tests_support import Checker, use_test_db

_TEST_DB = use_test_db(__file__, "smoke204")


async def main():
    check = Checker()

    import database.db as db
    from database.db import (init_db, close_db, add_user, update_user, get_user,
                             remove_nordmarks, create_fine, get_active_fines,
                             process_fines_daily, pay_fine, cancel_fine, has_unpaid_fines,
                             fine_charge_base)

    await init_db()
    A, B, C, D = 204001, 204002, 204003, 204004
    for uid in (A, B, C, D):
        await add_user(uid, f"f{uid}", "Ф", "")
    await update_user(A, nordmarks=500)
    await update_user(B, nordmarks=5)
    await update_user(C, nordmarks=1000)

    print("\n1. Баланс не уходит в минус")
    taken = await remove_nordmarks(B, 50, "test", "проверка")
    check("списано не больше баланса (5 из 50)", taken == 5)
    check("баланс = 0, не отрицательный", int((await get_user(B))["nordmarks"]) == 0)
    check("нулевой баланс — ничего не списано", await remove_nordmarks(B, 10, "test") == 0)
    await update_user(B, nordmarks=5)

    print("\n2. Суточное списание: 10% от исходной суммы")
    check("база 10% от 200 = 20", fine_charge_base(200) == 20)
    check("база округляется вверх (5 → 1)", fine_charge_base(5) == 1)
    fid = await create_fine(A, 200, "опоздание с отчётом", 1)
    check("штраф создан и активен", len(await get_active_fines(A)) == 1)
    ev = await process_fines_daily("2026-11-03")
    row = [e for e in ev if e["fine_id"] == fid]
    check("списано 20 (10% от 200)", row and row[0]["taken"] == 20)
    check("остаток 180", row and row[0]["left"] == 180)
    check("баланс 480", int((await get_user(A))["nordmarks"]) == 480)

    print("\n3. Нехватка: баланс меньше 10% — ждём")
    fid_b = await create_fine(B, 200, "нарушение", 1)
    ev = await process_fines_daily("2026-11-03")
    check("у B (5 НМ) ничего не списано", not [e for e in ev if e["fine_id"] == fid_b])
    check("баланс B не тронут", int((await get_user(B))["nordmarks"]) == 5)
    check("штраф B остался активным", await has_unpaid_fines(B))

    print("\n4. Повтор в тот же игровой день не списывает второй раз")
    ev = await process_fines_daily("2026-11-03")
    check("повтор за день — пусто", not [e for e in ev if e["fine_id"] == fid])

    print("\n5. Оплата пилотом")
    ok, msg, paid = await pay_fine(A, fid, 30)
    check("частичная оплата 30", ok and paid == 30)
    check("остаток 150", (await get_active_fines(A))[0]["amount_left"] == 150)
    ok, msg, paid = await pay_fine(A, fid)
    check("полная оплата остатка", ok and paid == 150)
    check("после полной оплаты активных нет", not await has_unpaid_fines(A))
    ok, msg, paid = await pay_fine(A, fid)
    check("повторная оплата закрытого — отказ", not ok)
    check("оплата не больше баланса", (await pay_fine(B, fid_b, 999))[0] is False)

    print("\n6. Отмена админом")
    fid_c = await create_fine(C, 100, "ошибка", 1)
    check("отмена активного", await cancel_fine(fid_c))
    check("после отмены штраф не активен", not await has_unpaid_fines(C))
    check("повторная отмена — отказ", not await cancel_fine(fid_c))

    failed = check.summary()
    await close_db()
    return failed


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
