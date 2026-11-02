# -*- coding: utf-8 -*-
"""Smoke 195 — два бага: быстрые нажатия курса и удочка вне колодца.

1. Курс выживания: нажатия одного игрока выполняются по одному (без параллели),
   разные игроки не мешают друг другу.
2. Удочка Колодца: вне колодца (well_open=0) отказывает, в колодце (well_open=1) — нет.
   Шаг дальше по лабиринту сбрасывает флаг.
"""
import asyncio
import os
import sys

os.environ["DATABASE_PATH"] = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "_test_smoke195.db")

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

    from database.db import init_db, close_db, add_user, create_fire_lab_session, get_db
    from bot.handlers import kvp
    from bot.handlers import fire_event as fe

    await init_db()

    print("\n1. Курс: нажатия одного игрока идут по очереди")
    running = {"now": 0, "max": 0}

    async def slow_handler(callback, *args, **kwargs):
        running["now"] += 1
        running["max"] = max(running["max"], running["now"])
        await asyncio.sleep(0.01)
        running["now"] -= 1
        return "ok"

    class CB:
        def __init__(self, uid):
            self.from_user = type("U", (), {"id": uid})()

    wrapped = kvp._kvp_serial(slow_handler)
    results = await asyncio.gather(*[wrapped(CB(7001)) for _ in range(5)])
    check("5 быстрых нажатий одного игрока: параллели нет", running["max"] == 1)
    check("все 5 нажатий обработаны", results == ["ok"] * 5)
    running["now"] = running["max"] = 0
    await asyncio.gather(wrapped(CB(7001)), wrapped(CB(7002)))
    check("разные игроки не ждут друг друга", running["max"] == 2)

    print("\n2. Удочка Колодца только в колодце")
    UID = 195001
    await add_user(UID, "t", "Пилот 195", "")
    sid = await create_fire_lab_session(UID, 50)
    conn = await get_db()

    class FakeMsg:
        chat = type("C", (), {"id": UID})()
        message_id = 1

        async def answer(self, *a, **kw):
            return self

        async def edit_text(self, *a, **kw):
            return True

        async def delete(self):
            return True

    class FakeCB:
        alerts = []

        def __init__(self, data):
            self.from_user = type("U", (), {"id": UID})()
            self.data = data
            self.message = FakeMsg()

        async def answer(self, text=None, show_alert=False, **kw):
            if show_alert and text:
                FakeCB.alerts.append(text)
            return True

    await conn.execute("UPDATE fire_lab_sessions SET well_open = 0 WHERE id = ?", (sid,))
    await conn.commit()
    FakeCB.alerts.clear()
    await fe.fire_event_fishing_cb(FakeCB(f"fireevent:fishing:{sid}"))
    check("вне колодца удочка отказана",
          any("остался позади" in a for a in FakeCB.alerts))

    await conn.execute("UPDATE fire_lab_sessions SET well_open = 1 WHERE id = ?", (sid,))
    await conn.commit()
    FakeCB.alerts.clear()
    await fe.fire_event_fishing_cb(FakeCB(f"fireevent:fishing:{sid}"))
    check("в колодце не отказывает по месту",
          not any("остался позади" in a for a in FakeCB.alerts))

    from database.db import bump_fire_lab_room_visit
    await bump_fire_lab_room_visit(sid, "tree")
    cur = await conn.execute("SELECT well_open FROM fire_lab_sessions WHERE id = ?", (sid,))
    check("вход в древо закрывает колодец", int((await cur.fetchone())['well_open']) == 0)

    print(f"\nИТОГО: {passed} passed, {failed} failed")
    await close_db()
    return failed


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
