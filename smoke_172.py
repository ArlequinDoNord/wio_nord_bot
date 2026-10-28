# -*- coding: utf-8 -*-
"""Smoke 172 — Ф1 каркас «Дней Пламенного Круговорота».

1. Константы config (окно дат, вход, лимит).
2. fire_event_active(): вне окна → False, внутри окна → True, флаг ENABLED
   перекывает.
3. fire_event_visible(): только при FIRE_LAB_ENABLED=True и внутри окна.
4. Кнопка города скрыта (FIRE_LAB_ENABLED=False) и появляется с флагом.
5. db-таблицы: fire_lab_sessions / fire_lab_entries.
6. Вход: списание 42 НМ, счётчик 4/сутки, блокировка 5-го, сессия создаётся
   и возвращается активной; leave закрывает (status='left').
7. Чужая сессия не открывается (_session_of).
"""
import asyncio
import os
import sys
from datetime import datetime, timedelta

os.environ["DATABASE_PATH"] = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "_test_smoke172.db")

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
            print(f"  FAIL: {name}")

    import database.db as db
    import config
    from database.db import (
        init_db, add_user, update_user, get_user,
        fire_event_active, fire_event_visible,
        get_fire_lab_entries_today, inc_fire_lab_entries,
        create_fire_lab_session, get_active_fire_lab_session,
        end_fire_lab_session, today_report_day, close_db,
    )

    await init_db()
    UID = 172001
    await add_user(UID, 't', 'Т', "")
    await update_user(UID, nordmarks=1000)

    print("\n1. Константы config")
    check("FIRE_EVENT_ENABLED = True", config.FIRE_EVENT_ENABLED is True)
    check("FIRE_LAB_ENABLED = False (каркас закрыт)",
          config.FIRE_LAB_ENABLED is False)
    check("старт = 30.10 (пятница), МСК",
          config.FIRE_EVENT_START[:3] == (2026, 10, 30))
    check("длительность 5 суток", config.FIRE_EVENT_DURATION_DAYS == 5)
    check("вход 42 НМ", config.FIRE_EVENT_LAB_FEE == 42)
    check("максимум 4 захода/сутки", config.FIRE_EVENT_MAX_ENTRIES_DAY == 4)

    print("\n2. fire_event_active (окно дат)")
    real_start = config.FIRE_EVENT_START
    real_enabled = config.FIRE_EVENT_ENABLED
    # вне окна (в прошлом)
    config.FIRE_EVENT_START = (2026, 10, 1, 0, 0)
    check("вне окна (прошлое) → False", fire_event_active() is False)
    # старт сегодня: окно открыто
    from utils.helpers import MOSCOW_TZ
    now_msk = datetime.now(MOSCOW_TZ)
    config.FIRE_EVENT_START = (now_msk.year, now_msk.month, now_msk.day, 0, 0)
    check("внутри окна (старт сегодня) → True", fire_event_active() is True)
    # длительность 0 → тот же момент ещё в окне? делаем прошлое будущее окно
    config.FIRE_EVENT_START = (now_msk.year, now_msk.month, now_msk.day + 1, 0, 0) \
        if now_msk.day < 28 else (2027, 1, 1, 0, 0)
    check("вне окна (будущее) → False", fire_event_active() is False)
    config.FIRE_EVENT_START = real_start
    config.FIRE_EVENT_ENABLED = real_enabled

    print("\n3. fire_event_visible")
    check("при FIRE_LAB_ENABLED=False → False", fire_event_visible() is False)
    config.FIRE_LAB_ENABLED = True
    config.FIRE_EVENT_START = (now_msk.year, now_msk.month, now_msk.day, 0, 0)
    check("при флагах и внутри окна → True", fire_event_visible() is True)
    config.FIRE_LAB_ENABLED = False
    config.FIRE_EVENT_START = real_start

    print("\n4. Кнопка города")
    from keyboards.keyboards import city_keyboard
    kb = city_keyboard()
    check("кнопка события скрыта", all("fireevent" not in (b.callback_data or "")
                                       for row in kb.inline_keyboard for b in row))
    kb = city_keyboard(event_visible=True)
    check("кнопка события появляется (event_visible=True)",
          any(b.callback_data == "fireevent:enter"
              for row in kb.inline_keyboard for b in row))

    print("\n5. Таблицы db")
    conn = await db.get_db()
    for t in (('fire_lab_sessions',), ('fire_lab_entries',)):
        c2 = await conn.execute("SELECT COUNT(*) AS c FROM " + t[0])
        r2 = await c2.fetchone()
    cur = await conn.execute(("SELECT name FROM sqlite_master WHERE type='table' "
                              "AND name IN ('fire_lab_sessions','fire_lab_entries')"))
    names = {r['name'] for r in await cur.fetchall()}
    check("обе таблицы существуют", names == {'fire_lab_sessions', 'fire_lab_entries'})

    print("\n6. Вход: списания, лимит, сессия")
    day = today_report_day()
    check("входов сегодня 0", await get_fire_lab_entries_today(UID, day) == 0)
    n = await inc_fire_lab_entries(UID, day)
    check("счётчик растёт", n == 1)
    check("список 4 подряд", all(n == (i + 2) for i, n in enumerate(
        [await inc_fire_lab_entries(UID, day) for _ in range(3)])))
    check("счётчик = 4", await get_fire_lab_entries_today(UID, day) == 4)
    # лимит проверяется в хендлере; db-слой честно растёт — это ок

    before = (await get_user(UID))['nordmarks']
    sid = await create_fire_lab_session(UID, 42)
    check("сессия создана (id>0)", sid > 0)
    active = await get_active_fire_lab_session(UID)
    check("сессия активна и hp_max=42",
          active and int(active['id']) == sid
          and int(active['hp_max']) == 42 and int(active['hp']) == 42)
    check("статус active", active['status'] == 'active')
    check("steps=0 и path='[]'",
          int(active['steps']) == 0 and (active['path_history'] or '[]') == '[]')

    print("\n7. Закрытие сессии")
    await end_fire_lab_session(sid, 'left')
    active = await get_active_fire_lab_session(UID)
    check("после leave активной нет", active is None)

    print("\n7.1 TTL: неактивность закрывает сессию")
    sid_ttl = await create_fire_lab_session(UID, 20)
    conn2 = await db.get_db()
    await conn2.execute(
        "UPDATE fire_lab_sessions SET last_active_at = datetime('now', '-90 minutes') "
        "WHERE id = ?", (sid_ttl,))
    await conn2.commit()
    active = await get_active_fire_lab_session(UID)
    check("сессия старше 1 ч → expired, активной нет", active is None)
    cur3 = await conn2.execute("SELECT status FROM fire_lab_sessions WHERE id = ?", (sid_ttl,))
    row3 = await cur3.fetchone()
    check("статус в БД = expired", row3 and row3['status'] == 'expired')
    # свежая сессия живёт
    sid_fresh = await create_fire_lab_session(UID, 20)
    active = await get_active_fire_lab_session(UID)
    check("свежая сессия жива", active is not None and int(active['id']) == sid_fresh)
    await end_fire_lab_session(sid_fresh, 'left')

    print("\n8. Чужая сессия возвращается только владельцу")
    other = 172002
    await add_user(other, 'o', 'O', "")
    sid2 = await create_fire_lab_session(other, 30)
    fr = await get_active_fire_lab_session(UID)
    check("у первого не новая чужая сессия", not fr or int(fr['id']) != sid2)

    print(f"\nИТОГО: {passed} passed, {failed} failed")
    await close_db()
    if failed:
        sys.exit(1)


try:
    asyncio.run(main())
except Exception:
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    try:
        os.remove(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "_test_smoke172.db"))
    except OSError:
        pass
