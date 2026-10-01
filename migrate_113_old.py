"""Миграция 0.19.0 поверх БД со старой схемой polls (без closes_at/is_archived).

Это сценарий прода: init_db() должен добавить колонки, создать rep_speeches,
проставить closes_at активным опросам и НЕ потерять существующие данные.
"""
import asyncio
import os
import sqlite3
import sys

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_oldmig113.db")
for suffix in ("", "-wal", "-shm"):
    try:
        os.remove(DB + suffix)
    except OSError:
        pass

FAILED = 0


def check(name, ok):
    global FAILED
    print(("  OK  " if ok else "FAIL  ") + name)
    if not ok:
        FAILED += 1


# Старая схема polls — как в v0.18.19, без новых колонок.
con = sqlite3.connect(DB)
con.executescript("""
CREATE TABLE polls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_id INTEGER NOT NULL,
    question TEXT NOT NULL,
    options TEXT NOT NULL,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP,
    closed_by INTEGER
);
INSERT INTO polls (admin_id, question, options, is_active, created_at)
VALUES (700001, 'Старый опрос один', 'да\nнет', 1, '2020-01-01 00:00:00');
INSERT INTO polls (admin_id, question, options, is_active, created_at, closed_at, closed_by)
VALUES (700001, 'Старый опрос два (закрыт)', 'да\nнет', 0, '2020-01-02 00:00:00', '2020-01-03 00:00:00', 700001);
""")
con.commit()
con.close()

os.environ["DATABASE_PATH"] = DB
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db import init_db, get_db, close_db, maintain_polls, get_visible_polls


async def main():
    await init_db()
    conn = await get_db()

    cur = await conn.execute("PRAGMA table_info(polls)")
    cols = {r['name'] for r in await cur.fetchall()}
    for c in ("closes_at", "is_archived", "archived_day"):
        check(f"добавлена polls.{c}", c in cols)

    cur = await conn.execute("SELECT * FROM polls ORDER BY id")
    rows = await cur.fetchall()
    check("старые опросы на месте", len(rows) == 2)
    check("вопросы не потеряны",
          {r['question'] for r in rows} == {'Старый опрос один', 'Старый опрос два (закрыт)'})
    check("активному старому опросу проставлен closes_at", bool(rows[0]['closes_at']))
    check("is_archived по умолчанию 0", rows[0]['is_archived'] == 0)
    check("закрытый старый опрос не получил closes_at", not rows[1]['closes_at'])

    cur = await conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='rep_speeches'")
    check("rep_speeches создана", await cur.fetchone() is not None)

    # Древние опросы 2020 года закрываются по сроку, но пока их меньше
    # POLL_VISIBLE (4), в меню они остаются — как и задумано: архив начинается
    # с 5-го опроса.
    res = await maintain_polls()
    check("старый опрос закрылся по сроку", res['closed'] >= 1)
    check("при 2 опросах архив ещё пуст", res['archived'] == 0)
    visible = await get_visible_polls()
    check("в меню оба закрытых старых опроса", len(visible) == 2)
    check("в меню все закрыты", all(not p['is_active'] for p in visible))

    cur = await conn.execute("SELECT archived_day FROM polls ORDER BY id")
    arch = await cur.fetchall()
    check("пока archived_day пуст", all(not r['archived_day'] for r in arch))

    # Добиваем до 5 опросов: самый старый (2020 год) должен уйти в архив.
    for i in range(3):
        await conn.execute(
            "INSERT INTO polls (admin_id, question, options, is_active, created_at) "
            "VALUES (700001, ?, 'да\nнет', 1, datetime('now'))", (f'Свежий {i}',))
    await conn.commit()
    res = await maintain_polls()
    check("лишние опросы ушли в архив", res['archived'] == 1)

    visible = await get_visible_polls()
    check("в меню осталось 4 новейших", len(visible) == 4)
    check("в архив ушёл самый старый по id",
          not any(p['question'] == 'Старый опрос один' for p in visible))
    check("второй старый (id=2) остался в меню",
          any(p['question'] == 'Старый опрос два (закрыт)' for p in visible))
    check("свежие опросы в меню активны",
          all(p['is_active'] for p in visible
              if p['question'].startswith('Свежий')))

    cur = await conn.execute(
        "SELECT question, archived_day, is_active FROM polls "
        "WHERE COALESCE(is_archived, 0) = 1")
    ar = await cur.fetchall()
    check("в архиве ровно один опрос", len(ar) == 1)
    check("архивный опрос помечен is_active=0", all(r['is_active'] == 0 for r in ar))
    check("архивный опрос получил archived_day", all(r['archived_day'] for r in ar))

    # Повторный прогон обслуживания не должен ломать данные.
    res2 = await maintain_polls()
    check("повторное обслуживание идемпотентно", res2['closed'] == 0 and res2['archived'] == 0)


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
    print(f"\n=== OLD-SCHEMA MIGRATION 113: {'OK' if code == 0 and FAILED == 0 else str(FAILED) + ' FAILED'} ===")
    sys.exit(code or (1 if FAILED else 0))
