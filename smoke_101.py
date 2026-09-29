"""Smoke v0.18.9: буклет туриста.

Предмет из сувенирной категории (1 НМ) + знак «Опытный турист» + 20 НМ.
Проверяем слой БД (database/db.ensure_tourist_booklet, mark_booklet_visit,
get_booklet_visits, claim_booklet_reward):
  • предмет создаётся в сувенирке по цене 1, не продаётся;
  • награда создаётся;
  • локации отмечаются ТОЛЬКО при наличии буклета (ретроспективы нет);
  • лишние/небуклетные ключи не считаются;
  • награда один раз на аккаунт: повторная выдача отбивается.

Запуск: .venv\\Scripts\\python.exe smoke_101.py
"""
import asyncio
import os
import shutil
import sys
import tempfile

WORK = tempfile.mkdtemp(prefix="sm101_")
os.environ["DATABASE_PATH"] = os.path.join(WORK, "t.db")
sys.path.insert(0, os.path.dirname(__file__))

from database import db as D
from config import (TOURIST_BOOKLET_NAME, TOURIST_BOOKLET_PRICE,
                    TOURIST_BOOKLET_AWARD, TOURIST_BOOKLET_LOCATIONS,
                    TOURIST_BOOKLET_REWARD_NM)


def check(name, cond):
    print(("  ok   " if cond else "  FAIL ") + name)
    if not cond:
        FAILED.append(name)


FAILED = []


async def main():
    await D.init_db()
    conn = await D.get_db()
    await D.seed_locations(conn)
    await D.ensure_tourist_booklet()

    item = await D.get_booklet_item()
    check("предмет «Буклет туриста» создан", item is not None)
    if item:
        check("буклет в категории сувениров", item['category'] == 'souvenirs')
        check("буклет стоит 1 НМ", item['price'] == TOURIST_BOOKLET_PRICE)
        check("буклет не продаётся (sell_price = 0)", item['sell_price'] == 0)

    cur = await conn.execute("SELECT name FROM awards WHERE name = ?",
                             (TOURIST_BOOKLET_AWARD,))
    check("награда «Опытный турист» создана", bool(await cur.fetchone()))

    uid = 777
    await D.add_user(uid, "guest", "Гость", "Нордхайма")

    # Без буклета превью локаций не отмечаются (никакой ретроспективы).
    await D.mark_booklet_visit(uid, "townhall")
    await D.mark_booklet_visit(uid, "library")
    check("до покупки буклета посещения не пишутся",
          await D.get_booklet_visits(uid) == set())

    await D.add_inventory_item(uid, item['id'], 1)
    check("has_booklet: True после покупки", await D.has_booklet(uid) is True)

    # Отмечаем все 9 локаций буклета.
    for key in TOURIST_BOOKLET_LOCATIONS:
        await D.mark_booklet_visit(uid, key)
    visits = await D.get_booklet_visits(uid)
    check("все 9 локаций отмечены",
          visits == set(TOURIST_BOOKLET_LOCATIONS))

    # Небуклетный ключ не должен считаться.
    await D.mark_booklet_visit(uid, "wall")
    check("небуклетная локация не считается",
          await D.get_booklet_visits(uid) == set(TOURIST_BOOKLET_LOCATIONS))

    check("награда ещё не получена", await D.is_booklet_claimed(uid) is False)

    ok, _msg = await D.claim_booklet_reward(uid)
    check("награда получена", ok is True)

    user = await D.get_user(uid)
    check("+20 НМ начислены",
          user['nordmarks'] == 10 + TOURIST_BOOKLET_REWARD_NM)

    cur = await conn.execute(
        "SELECT COUNT(*) AS n FROM transactions WHERE to_user = ? AND tx_type = 'booklet'",
        (uid,))
    row = await cur.fetchone()
    check("в бане записана транзакция награды", row['n'] == 1)

    cur = await conn.execute(
        "SELECT COUNT(*) AS n FROM user_awards ua "
        "JOIN awards a ON ua.award_id = a.id WHERE a.name = ?",
        (TOURIST_BOOKLET_AWARD,))
    row = await cur.fetchone()
    check("значок выдан один раз", row['n'] == 1)

    check("после выдачи отмечено как получено",
          await D.is_booklet_claimed(uid) is True)
    ok2, msg2 = await D.claim_booklet_reward(uid)
    check("повторная выдача отбивается", ok2 is False and "получена" in msg2)

    # Частичный прогресс: награда недоступна.
    uid2 = 778
    await D.add_user(uid2, "guest2", "Гость", "Второй")
    await D.add_inventory_item(uid2, item['id'], 1)
    await D.mark_booklet_visit(uid2, "townhall")
    ok3, msg3 = await D.claim_booklet_reward(uid2)
    check("при неполном прогрессе награда недоступна",
          ok3 is False and "не все" in msg3)

    await D.close_db()
    shutil.rmtree(WORK, ignore_errors=True)
    total = len(FAILED)
    print("\nSmoke 101: " + ("all passed" if not total else f"{total} failed"))
    sys.exit(1 if FAILED else 0)


asyncio.run(main())