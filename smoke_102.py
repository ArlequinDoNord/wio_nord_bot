"""Smoke v0.18.10: награды открываются в профиле.

Раньше get_user_awards не выбирал бонусные колонки награды, а обработчик
«Мои награды» (bot/handlers/profile.py: profile_awards) их читает
(bonus_attack, bonus_defense, ...) — нажатие на «🎖️ Награды» падало с KeyError,
и значок «Опытный турист» нельзя было посмотреть. Проверяем слой БД:
  • get_user_awards возвращает все бонусные поля, которые читает профиль;
  • значения бонусов совпадают;
  • значок буклета (с нулевыми бонусами) тоже читается.

Запуск: .venv\\Scripts\\python.exe smoke_102.py
"""
import asyncio
import os
import shutil
import sys
import tempfile

WORK = tempfile.mkdtemp(prefix="sm102_")
os.environ["DATABASE_PATH"] = os.path.join(WORK, "t.db")
sys.path.insert(0, os.path.dirname(__file__))

from database import db as D
from config import TOURIST_BOOKLET_AWARD, TOURIST_BOOKLET_LOCATIONS

HANDLER_FIELDS = ('bonus_attack', 'bonus_defense', 'bonus_dodge', 'bonus_fishing',
                  'bonus_hp', 'bonus_shop_discount', 'bonus_report_tax')


def check(name, cond):
    print(("  ok   " if cond else "  FAIL ") + name)
    if not cond:
        FAILED.append(name)


FAILED = []


async def main():
    await D.init_db()
    conn = await D.get_db()

    uid = 777
    await D.add_user(uid, "pilot", "Пилот", "Нордхайма")

    ok, award_id = await D.create_award(
        "За отвагу", "Морозно и не умирается", "🏅", uid,
        bonus_attack=10, bonus_defense=5, bonus_dodge=2, bonus_fishing=7,
        bonus_hp=3, bonus_shop_discount=8, bonus_report_tax=2)
    check("награда создана", ok is True)
    if ok:
        await D.grant_award(uid, award_id, granted_by=uid, comment="тест")

    awards = await D.get_user_awards(uid)
    check("выданная награда видна в get_user_awards", len(awards) == 1)
    if awards:
        a = awards[0]
        check("эмодзи награды в выборке", a['emoji'] == '🏅')
        missing = [f for f in HANDLER_FIELDS if f not in a.keys()]
        check("профилю доступны все бонусные поля", not missing)
        got = tuple(a[f] for f in HANDLER_FIELDS)
        check("значения бонусов совпадают",
              got == (10, 5, 2, 7, 3, 8, 2))
        grant_keys = ('grant_id', 'comment', 'granted_at', 'award_id',
                      'name', 'description', 'emoji')
        missing2 = [f for f in grant_keys if f not in a.keys()]
        check("основные поля выдачи на месте", not missing2)

    # Значок буклета: нулевые бонусы тоже должны читаться профилем.
    await D.ensure_tourist_booklet()
    booklet = await D.get_booklet_item()
    await D.add_inventory_item(uid, booklet['id'], 1)
    for key in TOURIST_BOOKLET_LOCATIONS:
        await D.mark_booklet_visit(uid, key)
    ok2, _msg = await D.claim_booklet_reward(uid)
    check("значок буклета выдан", ok2 is True)

    awards2 = await D.get_user_awards(uid)
    tourist = [a for a in awards2 if a['name'] == TOURIST_BOOKLET_AWARD]
    check("значок буклета в списке наград", len(tourist) == 1)
    if tourist:
        missing = [f for f in HANDLER_FIELDS if f not in tourist[0].keys()]
        check("у значка читаются все бонусные поля", not missing)
        check("у значка нулевые бонусы",
              all(not tourist[0][f] for f in HANDLER_FIELDS))

    await D.close_db()
    shutil.rmtree(WORK, ignore_errors=True)
    total = len(FAILED)
    print("\nSmoke 102: " + ("all passed" if not total else f"{total} failed"))
    sys.exit(1 if FAILED else 0)


asyncio.run(main())