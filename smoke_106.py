"""Smoke v0.18.13: денежные премии наград — из казны, никогда из воздуха.

Проверяем слой БД (database/db):
  • миграция: колонки awards.reward_nm / awards.monthly_nm и таблица
    award_monthly_paid создаются;
  • grant_award с разовой премией платит ИЗ КАЗНЫ (транзакция award,
    from_user = TREASURY_ID), игрок получает на счёт;
  • пустая казна → премия в salary_debt (долг казны перед игроком);
  • награда без премии ничего не платит;
  • pay_award_monthly платит 1-го числа каждому владельцу, второй вызов
    за тот же месяц не дублирует выплату;
  • нехватка казны в месячной выплате тоже уходит в долг.

Запуск: .venv\\Scripts\\python.exe smoke_106.py
"""
import asyncio
import os
import shutil
import sys
import tempfile

WORK = tempfile.mkdtemp(prefix="sm106_")
os.environ["DATABASE_PATH"] = os.path.join(WORK, "t.db")
sys.path.insert(0, os.path.dirname(__file__))

from database import db as D


def check(name, cond):
    print(("  ok   " if cond else "  FAIL ") + name)
    if not cond:
        FAILED.append(name)


FAILED = []


async def columns_exist(conn, table, cols):
    cur = await conn.execute(f"PRAGMA table_info({table})")
    existing = {row['name'] for row in await cur.fetchall()}
    return cols.issubset(existing)


async def main():
    await D.init_db()
    conn = await D.get_db()

    check("миграция: rewards_nm/monthly_nm у awards",
          await columns_exist(conn, "awards", {"reward_nm", "monthly_nm"}))
    cur = await conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='award_monthly_paid'")
    check("таблица award_monthly_paid создана", bool(await cur.fetchone()))

    # ── 1. Награда с разовой премией из казны ───────────────────────────────
    ok, award_id = await D.create_award(
        "Серебряная звезда", "За подвиг", "⭐",
        created_by=1, reward_nm=50)
    check("награда создана", ok is True)
    await D.add_treasury(100, "тест: казна")

    uid = 701
    await D.add_user(uid, "hero", "Герой", "Первый")
    ok, msg = await D.grant_award(uid, award_id, granted_by=1, comment="тест")
    check("награда выдана", ok is True and "50" in msg)
    user = await D.get_user(uid)
    check("игрок получил 50 НМ (было 10, налоги не затронуты)",
          user['nordmarks'] == 10 + 50)
    check("казна уменьшилась на 50", await D.get_treasury_balance() == 50)
    cur = await conn.execute(
        "SELECT from_user, to_user, amount FROM transactions "
        "WHERE tx_type = 'award' ORDER BY id DESC LIMIT 1")
    tx = await cur.fetchone()
    check("транзакция: из казны (TREASURY_ID) 50 НМ",
          tx and tx['from_user'] == D.TREASURY_ID
          and tx['to_user'] == uid and tx['amount'] == 50)

    # ── 2. Пустая казна → премия в долг ─────────────────────────────────────
    uid2 = 702
    await D.add_user(uid2, "poor", "Бедняк", "Второй")
    # Дренируем казну до нуля (в шаге 1 осталось 50).
    await conn.execute("UPDATE treasury SET balance = 0 WHERE id = 1")
    await conn.commit()
    await D.grant_award(uid2, award_id, granted_by=1, comment="без казны")
    row = await (await conn.execute(
        "SELECT salary_debt FROM users WHERE user_id = ?", (uid2,))).fetchone()
    check("пустая казна: премия ушла в долг казны",
          row and row['salary_debt'] == 50)
    user2 = await D.get_user(uid2)
    check("игрок без казны денег не получил (счёт не тронут)",
          user2['nordmarks'] == 10)

    # ── 3. Награда без премии — ничего не платит ────────────────────────────
    ok3, award3 = await D.create_award("Почётный знак", "За флаг", "🚩",
                                       created_by=1)
    uid3 = 703
    await D.add_user(uid3, "flag", "Флагоносец", "Третий")
    await D.add_treasury(100, "тест: снова казна")
    await D.grant_award(uid3, award3, granted_by=1)
    cur = await conn.execute(
        "SELECT COUNT(*) AS n FROM transactions WHERE to_user = ? AND tx_type = 'award'",
        (uid3,))
    check("награда без премии не платит", (await cur.fetchone())['n'] == 0)
    check("казна не тратилась", await D.get_treasury_balance() == 100)

    # ── 4. Ежемесячные наградные ────────────────────────────────────────────
    ok4, monthly_award = await D.create_award(
        "Ветеран флота", "Почётная пенсия", "⚓",
        created_by=1, monthly_nm=30)
    uid4a, uid4b = 704, 705
    await D.add_user(uid4a, "vet1", "Ветеран", "Первый")
    await D.add_user(uid4b, "vet2", "Ветеран", "Второй")
    for u in (uid4a, uid4b):
        await D.grant_award(u, monthly_award, granted_by=1)
    m1 = await D.pay_award_monthly()
    check("месячная выплата прошла обоим",
          len(m1['paid']) == 2 and len(m1['debt']) == 0)
    check("казна после двух месячных −60 (40 осталось)",
          await D.get_treasury_balance() == 40)
    m2 = await D.pay_award_monthly()
    check("повторный вызов за тот же месяц не дублирует",
          len(m2['paid']) == 0 and len(m2['debt']) == 0)
    check("казна не меняется после дубля",
          await D.get_treasury_balance() == 40)
    cur = await conn.execute(
        "SELECT COUNT(*) AS n FROM award_monthly_paid")
    check("в табеле 2 записи, не 4", (await cur.fetchone())['n'] == 2)

    # ── 5. Месячная выплата при пустой казне → долг ─────────────────────────
    uid5 = 706
    await D.add_user(uid5, "vet3", "Ветеран", "Третий")
    await D.grant_award(uid5, monthly_award, granted_by=1)
    # Дренируем казну до нуля (убираем остаток вручную).
    await conn.execute("UPDATE treasury SET balance = 0 WHERE id = 1")
    await conn.commit()
    m3 = await D.pay_award_monthly()
    check("месячная без казны: в долг, без начисления",
          len(m3['paid']) == 0 and len(m3['debt']) == 1)
    row = await (await conn.execute(
        "SELECT salary_debt FROM users WHERE user_id = ?", (uid5,))).fetchone()
    check("долг за месяц зафиксирован", row and row['salary_debt'] == 30)
    cur = await conn.execute(
        "SELECT COUNT(*) AS n FROM award_monthly_paid WHERE user_id = ?", (uid5,))
    check("месяц отмечен в табеле даже при долге",
          (await cur.fetchone())['n'] == 1)

    await D.close_db()
    shutil.rmtree(WORK, ignore_errors=True)
    total = len(FAILED)
    print("\nSmoke 106: " + ("all passed" if not total else f"{total} failed"))
    sys.exit(1 if FAILED else 0)


asyncio.run(main())