"""Smoke v0.43.26: минфин не может опустить налог с отчётов ниже 5%.

Проверяет:
1. set_report_tax_percent: значения ниже config.REPORT_TAX_MIN_PERCENT поднимаются до минимума.
2. Миграция init_db: уже сохранённая ставка ниже минимума (например 2%) поднимается до 5%.
3. Обработчик админки admin_tax_set: 4 отклоняется, сообщение с минимумом; 5 принимается.
4. Подсказка в экране налога показывает диапазон 5–100.
5. Английский текст отказа.

Запуск: .venv\\Scripts\\python.exe smoke_240.py
"""
import asyncio
import os
import sys
from types import SimpleNamespace

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke240.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB
_ADMIN_ID = 440001
os.environ["ADMIN_IDS"] = str(_ADMIN_ID)

sys.path.insert(0, os.path.dirname(__file__))


class FakeMessage:
    def __init__(self, user_id, text=""):
        self.from_user = SimpleNamespace(id=user_id)
        self.text = text
        self.sent = []

    async def answer(self, text=None, *a, **kw):
        self.sent.append(text)


class FakeState:
    def __init__(self):
        self.cleared = False

    async def clear(self):
        self.cleared = True

    async def set_state(self, *a, **kw):
        return None


async def run():
    from config import REPORT_TAX_MIN_PERCENT
    from database.db import (
        init_db, close_db, get_db, set_report_tax_percent, get_report_tax_percent,
    )
    from bot.handlers import admin as A
    from utils.localization import use_lang

    await init_db()
    passed = failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
        else:
            failed += 1
            print(f"  FAIL: {name}")

    try:
        check("минимум = 5", REPORT_TAX_MIN_PERCENT == 5)

        # 1. Клэмп записи
        await set_report_tax_percent(2)
        check("2% поднимается до 5%", await get_report_tax_percent() == 5)
        await set_report_tax_percent(0)
        check("0% поднимается до 5%", await get_report_tax_percent() == 5)
        await set_report_tax_percent(60)
        check("60% сохраняется", await get_report_tax_percent() == 60)
        await set_report_tax_percent(250)
        check("выше 100 ограничивается 100", await get_report_tax_percent() == 100)
        await set_report_tax_percent(10)

        # 2. Миграция: ставка 2% уже лежит в БД до обновления
        conn = await get_db()
        await conn.execute("UPDATE settings SET value = '2' WHERE key = 'report_tax_percent'")
        await conn.commit()
        await init_db()
        check("миграция поднимает сохранённые 2% до 5%", await get_report_tax_percent() == 5)

        # 3. Обработчик админки
        state = FakeState()
        m4 = FakeMessage(_ADMIN_ID, "4")
        await A.admin_tax_set(m4, state)
        check("ввод 4 отклонён", m4.sent and "не ниже 5%" in m4.sent[0])
        check("ставка не изменилась после отказа", await get_report_tax_percent() == 5)
        check("состояние не сброшено при отказе", not state.cleared)

        await set_report_tax_percent(12)
        m5 = FakeMessage(_ADMIN_ID, "5")
        state2 = FakeState()
        await A.admin_tax_set(m5, state2)
        check("ввод 5 принят", await get_report_tax_percent() == 5)
        check("после ввода состояние сброшено", state2.cleared)
        check("подтверждение с 5%", m5.sent and "установлен: 5%" in m5.sent[0])

        # 4. Подсказка в экране налога
        view_src = open(A.__file__, encoding="utf-8").read()
        check("подсказка показывает диапазон 5–100",
              "ставку налога ({REPORT_TAX_MIN_PERCENT}–100)" in view_src)

        # 5. Английский
        use_lang("en")
        try:
            msg_en = A.t("admin.tax_min_error", minimum=REPORT_TAX_MIN_PERCENT)
        finally:
            use_lang("ru")
        check("EN: отказ с минимумом", "can't go below 5%" in msg_en)
    finally:
        await close_db()
        if os.path.exists(_TEST_DB):
            os.remove(_TEST_DB)

    print(f"\nSmoke 240: {passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)


asyncio.run(run())
