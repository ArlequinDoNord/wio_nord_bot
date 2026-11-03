# -*- coding: utf-8 -*-
"""Smoke 203 — благословение Древа Огня реально усиливает удар игрока.

1. Без благословения удар = базовый урон (фиксированный 10, броня врага 0).
2. После Древа (blessing=1) тот же удар = +15% (10 → 11) и +1 HP игроку.
3. Благословение держится до конца сессии: второй удар тоже усилен.
"""
import asyncio
import os
import sys

from tests_support import Checker, FakeCB, use_test_db

_TEST_DB = use_test_db(__file__, "smoke203")


async def main():
    check = Checker()

    import database.db as db
    import config
    from database.db import (init_db, close_db, add_user, update_user, create_fire_lab_session,
                             get_active_fire_lab_session, set_fire_lab_blessing, get_db)
    from bot.handlers import fire_event as fe
    from utils import combat_model

    await init_db()
    UID = 203001
    await add_user(UID, "bless", "Благословение", "")
    await update_user(UID, nordmarks=1000)

    async def fixed_stats(uid, *a, **kw):
        return {"hp_max": 100, "base_dmg": (10, 10), "weapon_damage": 0,
                "crit_chance": 0, "dodge": 0, "armor": 0}

    orig_stats = combat_model.pilot_combat_stats
    combat_model.pilot_combat_stats = fixed_stats
    try:
        async def hit(session_id, enemy_hp):
            enemy = {"key": "scarecrow", "name": "Пугало", "hp": enemy_hp, "hp_max": 200,
                     "armor": 0, "dodge": 0, "dmg_min": 0, "dmg_max": 0, "is_boss": False}
            await fe._save_enemy(session_id, enemy)
            cb = FakeCB(UID, f"fireevent:attack:{session_id}")
            await fe.fire_event_attack_cb(cb)
            after, _ = await fe._get_enemy_state(session_id)
            return enemy_hp - int(after["hp"]) if after else None

        print("\n1. Без благословения")
        sid = await create_fire_lab_session(UID, 100)
        conn = await get_db()
        await conn.execute("UPDATE fire_lab_sessions SET hp = 50 WHERE id = ?", (sid,))
        await conn.commit()
        dealt = await hit(sid, 200)
        check(f"базовый удар 10 (нанёс {dealt})", dealt == 10)

        print("\n2. С благословением Древа")
        sid2 = await create_fire_lab_session(UID, 100)
        await conn.execute("UPDATE fire_lab_sessions SET hp = 50 WHERE id = ?", (sid2,))
        await conn.commit()
        await set_fire_lab_blessing(sid2)
        session = await get_active_fire_lab_session(UID)
        check("флаг blessing стоит", int(session["blessing"] or 0) == 1)
        dealt2 = await hit(sid2, 200)
        expected = int(10 * (1 + config.FIRE_TREE_DMG_BONUS_PCT / 100.0))
        check(f"удар с благословением {expected} (нанёс {dealt2})", dealt2 == expected)
        cur = await conn.execute("SELECT hp FROM fire_lab_sessions WHERE id = ?", (sid2,))
        hp_after = int((await cur.fetchone())["hp"])
        check(f"регенерация +{config.FIRE_TREE_REGEN_HP} HP за удар (hp стало {hp_after})",
              hp_after >= 50 + config.FIRE_TREE_REGEN_HP)

        print("\n3. Второй удар в той же сессии тоже усилен")
        dealt3 = await hit(sid2, 200)
        check(f"второй удар {expected} (нанёс {dealt3})", dealt3 == expected)
    finally:
        combat_model.pilot_combat_stats = orig_stats

    failed = check.summary()
    await close_db()
    return failed


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
