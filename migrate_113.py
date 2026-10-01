"""Проверка миграций 0.19.0 на чистой БД: колонки polls, таблица rep_speeches."""
import asyncio
import os
import sys
import tempfile

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_mig190.db")
for suffix in ("", "-wal", "-shm"):
    try:
        os.remove(DB + suffix)
    except OSError:
        pass
os.environ["DATABASE_PATH"] = DB

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db import (init_db, get_db, close_db, create_poll, add_rep_speech,
                         get_latest_rep_speech, maintain_polls, get_visible_polls)
from utils.permissions import has_permission

FAILED = 0


def check(name, ok):
    global FAILED
    print(("  OK  " if ok else "FAIL  ") + name)
    if not ok:
        FAILED += 1


async def main():
    await init_db()
    conn = await get_db()

    cur = await conn.execute("PRAGMA table_info(polls)")
    cols = {r['name'] for r in await cur.fetchall()}
    check("polls.closes_at", "closes_at" in cols)
    check("polls.is_archived", "is_archived" in cols)
    check("polls.archived_day", "archived_day" in cols)

    cur = await conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='rep_speeches'")
    check("таблица rep_speeches", await cur.fetchone() is not None)

    # Миграция должна быть идемпотентной: повторный init_db() не падает.
    await init_db()
    check("повторный init_db() не падает", True)
    cur = await conn.execute("PRAGMA table_info(rep_speeches)")
    rcols = {r['name'] for r in await cur.fetchall()}
    for c in ("user_id", "text", "created_at", "created_day", "edited"):
        check(f"rep_speeches.{c}", c in rcols)

    await conn.execute(
        "INSERT INTO users (user_id, username, callsign, first_name) "
        "VALUES (700001, 'rep', 'КРЫША', 'Рад')")
    await conn.commit()

    pid = await create_poll(700001, "Чистая миграция", "да\nнет")
    poll = await get_visible_polls()
    check("опрос создался на чистой БД", len(poll) == 1 and poll[0]['id'] == pid)
    check("closes_at проставлен", bool(poll[0]['closes_at']))

    sid = await add_rep_speech(700001, "Обращение с чистой БД")
    latest = await get_latest_rep_speech()
    check("обращение сохранилось", latest is not None and latest['id'] == sid)
    check("callsign представителя подтянут", latest and latest['callsign'] == 'КРЫША')

    res = await maintain_polls()
    check("maintain_polls на чистой БД отработал", "closed" in res and "archived" in res)

    # Права ролей: can_address_city есть у representative и super_admin.
    await conn.execute(
        "INSERT OR IGNORE INTO user_roles (telegram_id, role) VALUES (700001, 'representative')")
    await conn.commit()
    check("у представителя есть can_address_city",
          await has_permission(700001, "can_address_city"))
    check("у случайного пилота нет can_address_city",
          not await has_permission(700002, "can_address_city"))


if __name__ == "__main__":
    code = 0
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        code = loop.run_until_complete(main()) or 0
    except Exception:
        import traceback
        traceback.print_exc()
        code = 1
    finally:
        # aiosqlite держит фоновый поток: без явного close_db процесс не завершится.
        try:
            loop.run_until_complete(close_db())
        except Exception:
            pass
        loop.close()
    for suffix in ("", "-wal", "-shm"):
        try:
            os.remove(DB + suffix)
        except OSError:
            pass
    print(f"\n=== MIGRATION 113: {'OK' if code == 0 and FAILED == 0 else str(FAILED) + ' FAILED'} ===")
    sys.exit(code or (1 if FAILED else 0))
