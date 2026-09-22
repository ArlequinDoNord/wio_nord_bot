"""Smoke v0.15.9: аудит ОД (ap_log) + суточное восстановление раз в сутки + блок
расходников в бою при состояниях.

Проверяет:
1. add_ap/remove_ap пишут ap_log с reason (before/after честные).
2. Потолок: ap_max; при «истощён» — 90.
3. daily_ap_recovery срабатывает раз в сутки (guard ap_recovery_day):
   сегодня + рестарт → повторного начисления нет; смена суток → +100 ОД и лог.
4. «Истощён»: +75 ОД, потолок 90.
5. battle_state_block_message: «несварение» и «очень пьян» блокируют применение
   предметов в бою, нормальное состояние — нет.

Запуск: .venv\\Scripts\\python.exe smoke_074.py
"""
import asyncio
import os
import sys
from datetime import datetime, timedelta

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke074.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB

sys.path.insert(0, os.path.dirname(__file__))


async def run():
    from database.db import (
        init_db, close_db, add_user, add_ap, remove_ap, daily_ap_recovery,
        get_user, update_user, set_user_state, remove_user_state,
    )

    await init_db()

    passed = 0
    failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
        else:
            failed += 1
            print(f"  FAIL: {name}")

    U1 = 740001
    U2 = 740002
    U3 = 740003   # для «очень пьян»
    for uid, name in ((U1, "Т1"), (U2, "Т2"), (U3, "Т3")):
        await add_user(uid, f"u{uid}", name, "")

    def today():
        return datetime.utcnow().strftime("%Y-%m-%d")

    def yesterday():
        return (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")

    async def ap_log_rows(uid, limit=10):
        from database.db import get_db
        conn = await get_db()
        cur = await conn.execute(
            "SELECT id, delta, ap_before, ap_after, reason FROM ap_log "
            "WHERE user_id = ? ORDER BY id DESC LIMIT ?", (uid, limit))
        return await cur.fetchall()

    # ── 1. add_ap/remove_ap с reason и запись в ap_log ──
    await update_user(U1, ap=0)
    await add_ap(U1, 30, "тест: начисление")
    u = await get_user(U1)
    check("add_ap +30", u['ap'] == 30)
    log = await ap_log_rows(U1)
    check("ap_log: delta=30 before=0 after=30 reason",
          log and log[0]['delta'] == 30 and log[0]['ap_before'] == 0
          and log[0]['ap_after'] == 30 and log[0]['reason'] == "тест: начисление")

    await remove_ap(U1, 10, "тест: расход")
    u = await get_user(U1)
    check("remove_ap −10", u['ap'] == 20)
    log = await ap_log_rows(U1)
    check("ap_log: delta=−10 before=30 after=20",
          log and log[0]['delta'] == -10 and log[0]['ap_before'] == 30
          and log[0]['ap_after'] == 20)

    check("remove_ap не даёт уйти в минус",
          not await remove_ap(U1, 999, "тест"))

    # ── 2. Потолок ap_max и истощён 90 ──
    await update_user(U1, ap=140)
    await add_ap(U1, 100, "тест: поверх потолка")
    u = await get_user(U1)
    check("потолок ap_max=150", u['ap'] == 150)

    await set_user_state(U2, "истощён", 2880, U2, "тест")
    await update_user(U2, ap=80)
    await add_ap(U2, 100, "тест: истощён")
    u2 = await get_user(U2)
    check("истощён: потолок 90", u2['ap'] == 90)
    log2 = await ap_log_rows(U2)
    check("истощён: начислено только 10 (80→90)", log2 and log2[0]['delta'] == 10)
    await remove_user_state(U2, "истощён", U2, "снято в тесте")

    # ── 3. daily_ap_recovery: раз в сутки ──
    await update_user(U1, ap=5, ap_recovery_day=today())
    await daily_ap_recovery()
    u = await get_user(U1)
    check("восстановление не сработало повторно в те же сутки", u['ap'] == 5)

    await update_user(U1, ap=10, ap_recovery_day=yesterday())
    before = len(await ap_log_rows(U1, limit=100))
    await daily_ap_recovery()
    u = await get_user(U1)
    check("смена суток: +100 ОД (10→110)", u['ap'] == 110)
    u = await get_user(U1)
    check("ap_recovery_day = сегодня", u['ap_recovery_day'] == today())
    log = await ap_log_rows(U1, limit=100)
    check("суточное восстановление залогировано",
          any(r['reason'].startswith("суточное восстановление ОД") and r['delta'] == 100
              for r in log) and len(log) > before)

    # повторный вызов в те же сутки после похода → без изменений
    await update_user(U1, ap=50)
    await daily_ap_recovery()
    u = await get_user(U1)
    check("повторный вызов не начисляет повторно", u['ap'] == 50)

    # ── 4. истощён: +75, потолок 90 ──
    await set_user_state(U2, "истощён", 2880, U2, "тест")
    await update_user(U2, ap=20, ap_recovery_day=yesterday())
    await daily_ap_recovery()
    u2 = await get_user(U2)
    check("истощён: 20→90 (+75, потолок 90)", u2['ap'] == 90)
    check("истощён: ap_recovery_day = сегодня", u2['ap_recovery_day'] == today())

    # ── 5. Блок расходников в бою при состояниях ──
    from bot.handlers.dungeon import battle_state_block_message
    blk = await battle_state_block_message(U2)   # истощён не блокирует расходники
    check("истощён не блокирует расходники в бою", blk is None)

    await set_user_state(U1, "несварение", 1440, U1, "тест")
    blk = await battle_state_block_message(U1)
    check("несварение: блок в бою", blk is not None and "Несварение" in blk)

    await set_user_state(U3, "очень пьян", 360, U3, "тест")
    blk3 = await battle_state_block_message(U3)
    check("очень пьян: блок в бою", blk3 is not None and "слишком пьян" in blk3)

    blkN = await battle_state_block_message(740999)
    check("несуществующий игрок: нет блока", blkN is None)

    await close_db()
    print(f"\nSmoke 074: {passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    try:
        asyncio.run(run())
    except SystemExit:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        from database.db import close_db
        asyncio.run(close_db())
        print(f"SMOKE ERROR: {e!r}")
        sys.exit(1)