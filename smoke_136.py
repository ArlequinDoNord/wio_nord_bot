"""Smoke v0.22.18: ачивки (реген/super_rare/reward_item) и пропорциональный оклад.

Проверяем три фичи пакета:
  • water_fish.super_rare — флаг заводится create_water_fish, виден в пуле,
    переключается update_water_fish_field;
  • reward_item у ачивки «НИИ» 4 ур. — предмет по имени кладётся в инвентарь
    при достижении уровня; если предмета нет, ошибки нет;
  • pay_role_salary_on_revoke — пропорциональный оклад за дни месяца, защита от
    повторной выплаты и от доплаты после полной месячной (28-е).

Запуск: .venv\\Scripts\\python.exe smoke_136.py
"""
import asyncio
import calendar
import os
import shutil
import sys
import tempfile
from datetime import datetime, timedelta, timezone

WORK = tempfile.mkdtemp(prefix="sm136_")
os.environ["DATABASE_PATH"] = os.path.join(WORK, "t.db")
sys.path.insert(0, os.path.dirname(__file__))

from database import db as D
from utils.helpers import MOSCOW_TZ

FAILED = []


def check(name, cond):
    print(("  ok   " if cond else "  FAIL ") + name)
    if not cond:
        FAILED.append(name)


async def main():
    await D.init_db()
    await D.ensure_achievements()
    await D.ensure_water_fish()
    conn = await D.get_db()

    # --- super_rare ---
    ok, res = await D.create_water_fish(
        water="lake", name="Легендарный лосось", sell_price=99,
        day_weight=5, night_weight=5, super_rare=1)
    check("супер-редкая рыба создана", ok is True)
    if ok:
        pool = await D.get_water_fish_pool("lake")
        row = [r for r in pool if r["name"] == "Легендарный лосось"]
        check("флаг super_rare виден в пуле", bool(row) and row[0]["super_rare"] == 1)
        await D.update_water_fish_field(res["wf_id"], "super_rare", 0)
        pool = await D.get_water_fish_pool("lake")
        row = [r for r in pool if r["name"] == "Легендарный лосось"]
        check("флаг super_rare снимается", bool(row) and row[0]["super_rare"] == 0)

    # --- reward_item: предмета ещё нет — не падаем ---
    await conn.execute(
        "INSERT INTO users (user_id, username, first_name) VALUES (?,?,?)",
        (202, "b", "B"))
    try:
        for _ in range(60):
            await D.bump_achievement(202, "reports", 1)
        err = None
    except Exception as e:
        err = e
    check("уровень без созданного предмета не падает", err is None)
    inv2 = await D.get_inventory(202)
    check("инвентарь пуст (предмета не было)",
          not inv2 or "Рецепт высшего качества" not in [i["name"] for i in inv2])

    # --- reward_item: предмет создан — кладём в инвентарь ---
    await conn.execute(
        "INSERT INTO users (user_id, username, first_name) VALUES (?,?,?)",
        (201, "a", "A"))
    await D.add_item(name="Рецепт высшего качества", description="x",
                     price=0, sell_price=0, rarity=5, category="misc",
                     stock=-1, added_by=0)
    for _ in range(60):
        await D.bump_achievement(201, "reports", 1)
    check("НИИ достиг 4 уровня", await D.get_achievement_level(201, "reports") == 4)
    inv = await D.get_inventory(201)
    names = [i["name"] for i in inv] if inv else []
    check("предмет-награда попал в инвентарь", "Рецепт высшего качества" in names)

    # --- пропорциональный оклад ---
    await conn.execute(
        "INSERT INTO users (user_id, username, first_name) VALUES (?,?,?)",
        (301, "c", "C"))
    await D.add_user_role(301, "representative")  # 350 НМ/мес
    now = datetime.now(MOSCOW_TZ)
    total_days = calendar.monthrange(now.year, now.month)[1]
    start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    granted = max(start, now - timedelta(days=9))
    g_utc = granted.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    await conn.execute("UPDATE user_roles SET created_at = ? WHERE telegram_id = 301", (g_utc,))
    await conn.commit()
    served = max(1, (now.date() - granted.date()).days + 1)
    payout = await D.pay_role_salary_on_revoke(301, "representative")
    check("пропорциональный оклад начислен", bool(payout))
    if payout:
        check("дней отработано верно", payout["days"] == served)
        check("сумма пропорциональна", payout["amount"] == int(350 * served / total_days))
    check("повторная выплата не проходит",
          await D.pay_role_salary_on_revoke(301, "representative") is None)

    # Полный оклад за месяц (28-е) блокирует доплату.
    await conn.execute(
        "INSERT INTO users (user_id, username, first_name) VALUES (?,?,?)",
        (302, "d", "D"))
    await D.add_user_role(302, "journalist")
    month = now.strftime("%Y-%m")
    await conn.execute(
        "INSERT OR IGNORE INTO role_salary_paid (user_id, month, amount) VALUES (?,?,?)",
        (302, month, 70))
    await conn.commit()
    check("после полной выплаты доплаты нет",
          await D.pay_role_salary_on_revoke(302, "journalist") is None)

    # Должность без оклада не платит.
    await D.add_user_role(302, "clan_leader")
    check("роль без оклада не платит",
          await D.pay_role_salary_on_revoke(302, "clan_leader") is None)

    await D.close_db()
    shutil.rmtree(WORK, ignore_errors=True)
    total = len(FAILED)
    print("\nSmoke 136: " + ("all passed" if not total else f"{total} failed"))
    sys.exit(1 if FAILED else 0)


asyncio.run(main())
