# -*- coding: utf-8 -*-
import asyncio, os, sys
os.environ["DATABASE_PATH"] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_dbg_tier.db")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def main():
    import database.db as db
    from database.db import init_db, add_user, inc_fire_lab_tier, get_fire_lab_tier, close_db
    await init_db()
    print("tier0:", await get_fire_lab_tier(999777))
    t = await inc_fire_lab_tier(999777)
    print("after inc:", t)
    t2 = await inc_fire_lab_tier(999777)
    print("after inc2:", t2)
    conn = await db.get_db()
    cur = await conn.execute("SELECT * FROM fire_lab_tier WHERE user_id = ?", (999777,))
    print("row:", dict(await cur.fetchone()))
    await close_db()

asyncio.run(main())
