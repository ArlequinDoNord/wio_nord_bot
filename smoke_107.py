"""Smoke v0.18.13 (часть 2): редактор формирований ВВС + ретро-балансировка казны.

Слой БД (database/db) + кэш utils.wings:
  • при init_db таблица wings заполняется 4 legacy-формированиями, кэш меток
    пересобирается из БД (ключи '1'..'4' сохранены);
  • create_wing: валидация формата «число + две заглавные буквы», дубликаты
    отвергаются, новые формирования сразу видны в кэше WINGS;
  • update_wing меняет полное название / позывной / эмодзи;
  • delete_wing запрещён, пока в формировании есть пилоты;
  • ретро-балансировка: старые выплаты значков (booklet, from_user IS NULL)
    помечаются исходящими из казны, баланс казны уменьшается, повтор — no-op.

Запуск: .venv\\Scripts\\python.exe smoke_107.py
"""
import asyncio
import os
import shutil
import sys
import tempfile

WORK = tempfile.mkdtemp(prefix="sm107_")
os.environ["DATABASE_PATH"] = os.path.join(WORK, "t.db")
sys.path.insert(0, os.path.dirname(__file__))

from database import db as D
from utils import wings as W


def check(name, cond):
    print(("  ok   " if cond else "  FAIL ") + name)
    if not cond:
        FAILED.append(name)


FAILED = []


async def main():
    await D.init_db()
    conn = await D.get_db()

    # ── 1. Сид legacy-формирований + кэш из БД ──────────────────────────────
    cur = await conn.execute("SELECT COUNT(*) AS n FROM wings")
    check("в wings 4 legacy-формирования", (await cur.fetchone())['n'] == 4)
    check("ключи legacy сохранены ('1'..'4'), метка по шаблону",
          W.WINGS_SHORT.get('1') == '🐺 1 АК')
    check("полная метка с позывным", W.WINGS.get('1') == '🐺 1 АК «Небесные Волки»')
    cur = await conn.execute(
        "SELECT key, num, abbr FROM wings WHERE key = '4'")
    row = await cur.fetchone()
    check("legacy 4: число и аббревиатура раздельно", row['num'] == '4' and row['abbr'] == 'СО')

    # ── 2. Валидация формата нового формирования ────────────────────────────
    ok, _ = await D.create_wing("abc", "ИШ", "Истребители", "Шторм", "⚡")
    check("число не из цифр — отклонено", ok is False)
    ok, _ = await D.create_wing("5", "И", "Истребители", "Шторм", "⚡")
    check("аббревиатура в одну букву — отклонено", ok is False)
    ok, _ = await D.create_wing("5", "ИШБ", "Истребители", "Шторм", "⚡")
    check("аббревиатура в три буквы — отклонено", ok is False)
    ok, msg = await D.create_wing("5", "иш", "Истребители Шторма", "Шторм", "⚡")
    check("валидное «5 ИШ» создано (аббревиатура поднята в верхний регистр)",
          ok is True and "5 ИШ" in msg)
    check("новое формирование сразу в кэше WINGS_SHORT",
          W.WINGS_SHORT.get('5 ИШ') == '⚡ 5 ИШ')
    check("полная метка нового: число + буквы + позывной",
          W.WINGS.get('5 ИШ') == '⚡ 5 ИШ «Шторм»')
    ok, msg = await D.create_wing("5", "ИШ", "Дубль", "Дубль", "✨")
    check("дубликат «5 ИШ» отклонён", ok is False)

    # ── 3. Редактирование ───────────────────────────────────────────────────
    await D.update_wing("5 ИШ", name="Истребители Шторма и Молнии", callsign="Гроза", emoji="🌩")
    check("после редактирования метка обновлена",
          W.WINGS.get('5 ИШ') == '🌩 5 ИШ «Гроза»')
    row = await D.get_wing_row("5 ИШ")
    check("в БД записано полное название",
          row and "Молнии" in row['name'])

    # ── 4. Удаление: занятое формирование не удаляется ──────────────────────
    uid = 801
    await D.add_user(uid, "stormpilot", "Штурм", "Первый")
    await D.set_wing(uid, "5 ИШ")
    ok, msg = await D.delete_wing("5 ИШ")
    check("удаление занятого формирования заблокировано", ok is False)
    await D.set_wing(uid, None)
    ok, msg = await D.delete_wing("5 ИШ")
    check("после перевода пилотов формирование удалено", ok is True)
    check("удалённое исчезло из кэша", "5 ИШ" not in W.WINGS)

    # ── 5. Ретро-балансировка казны за старые значки ────────────────────────
    uid_book = 802
    await D.add_user(uid_book, "oldcustomer", "Турист", "Старый")
    await D.add_treasury(100, "тест: казна")
    # Старая выплата значка «Опытный турист» — «из воздуха» (from_user = NULL).
    await conn.execute(
        "INSERT INTO transactions (to_user, amount, tx_type, description) "
        "VALUES (?, 20, 'booklet', 'Значок «Опытный турист»')", (uid_book,))
    await D._balance_legacy_booklet_payouts()
    cur = await conn.execute(
        "SELECT from_user FROM transactions WHERE tx_type = 'booklet' "
        "AND to_user = ?", (uid_book,))
    check("старая выплата помечена исходящей из казны",
          (await cur.fetchone())['from_user'] == D.TREASURY_ID)
    check("казна списала 20 НМ задним числом",
          await D.get_treasury_balance() == 80)
    await D._balance_legacy_booklet_payouts()
    check("повторный прогон — no-op (казна не уменьшается дальше)",
          await D.get_treasury_balance() == 80)

    await D.close_db()
    shutil.rmtree(WORK, ignore_errors=True)
    total = len(FAILED)
    print("\nSmoke 107: " + ("all passed" if not total else f"{total} failed"))
    sys.exit(1 if FAILED else 0)


asyncio.run(main())