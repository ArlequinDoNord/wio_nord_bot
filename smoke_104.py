"""Smoke v0.18.12: карточка награды в профиле.

Вкладка «🎖️ Награды» теперь открывает список, а по награде — карточку
(описание, бонусы, дата, картинка). Для этого get_user_awards должен отдавать
поле image награды. Проверяем:
  • update_award ставит картинку награды;
  • выданная награда читается со всеми полями карточки (image, emoji, бонусы);
  • картинка отданной награды видна в выборке (и очистка image работает).

Запуск: .venv\\Scripts\\python.exe smoke_104.py
"""
import asyncio
import os
import shutil
import sys
import tempfile

WORK = tempfile.mkdtemp(prefix="sm104_")
os.environ["DATABASE_PATH"] = os.path.join(WORK, "t.db")
sys.path.insert(0, os.path.dirname(__file__))

from database import db as D

CARD_FIELDS = ('grant_id', 'comment', 'granted_at', 'award_id', 'name',
               'description', 'emoji', 'image',
               'bonus_attack', 'bonus_defense', 'bonus_dodge', 'bonus_fishing',
               'bonus_hp', 'bonus_shop_discount', 'bonus_report_tax')


def check(name, cond):
    print(("  ok   " if cond else "  FAIL ") + name)
    if not cond:
        FAILED.append(name)


FAILED = []


async def main():
    await D.init_db()

    uid = 777
    await D.add_user(uid, "pilot", "Пилот", "Нордхайма")

    ok, award_id = await D.create_award(
        "Герой Нордхайма", "Выдаётся за выдающиеся заслуги.", "🏆", uid,
        bonus_attack=15, bonus_fishing=5)
    check("награда создана", ok is True)

    ok_img = await D.update_award(award_id, image="photo_award_1")
    check("картинка награды установлена", ok_img is True)

    await D.grant_award(uid, award_id, granted_by=uid, comment="За оборону стены")

    awards = await D.get_user_awards(uid)
    check("награда видна в списке", len(awards) == 1)
    if awards:
        a = awards[0]
        missing = [f for f in CARD_FIELDS if f not in a.keys()]
        check("у карточки есть все поля (включая image)", not missing)
        check("image награды в выборке", a['image'] == "photo_award_1")
        check("бонусы карточки на месте",
              a['bonus_attack'] == 15 and a['bonus_fishing'] == 5)
        check("эмодзи и имя", a['name'] == "Герой Нордхайма" and a['emoji'] == "🏆")
        check("комментарий выдачи", a['comment'] == "За оборону стены")

    # Очистка картинки — тоже через update_award.
    await D.update_award(award_id, image=None)
    awards2 = await D.get_user_awards(uid)
    check("image можно очистить",
          awards2 and (awards2[0].get('image') is None))

    await D.close_db()
    shutil.rmtree(WORK, ignore_errors=True)
    total = len(FAILED)
    print("\nSmoke 104: " + ("all passed" if not total else f"{total} failed"))
    sys.exit(1 if FAILED else 0)


asyncio.run(main())