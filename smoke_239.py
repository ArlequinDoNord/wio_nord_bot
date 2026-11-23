"""Smoke v0.43.26: кнопка «Налоги и ставки» в Нордбанке.

Проверяет:
1. В клавиатуре банка есть кнопка bank:taxes.
2. Текст сводки показывает текущие ставки из БД: отчёты, продажи, контракты,
   налог на жильё (нулевые — как «без налога»).
3. Личная ставка с отчётов появляется, только если она отличается от базовой
   (скидка наградами), и не опускается ниже AWARD_MIN_REPORT_TAX.
4. Английский интерфейс: строки берутся из t() с en-вариантом.
5. Незарегистрированному кнопка ничего не отправляет.

Запуск: .venv\\Scripts\\python.exe smoke_239.py
"""
import asyncio
import os
import sys
from types import SimpleNamespace

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke239.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB
os.environ["ADMIN_IDS"] = "439001"

sys.path.insert(0, os.path.dirname(__file__))


class FakeMessage:
    def __init__(self, user_id, message_id=100):
        self.from_user = SimpleNamespace(id=user_id)
        self.message_id = message_id
        self.sent = []

    async def answer(self, *a, **kw):
        self.sent.append((a, kw))


class FakeCallback:
    def __init__(self, user_id, data="", message=None):
        self.from_user = SimpleNamespace(id=user_id)
        self.message = message or FakeMessage(user_id)
        self.data = data

    async def answer(self, text=None, *a, **kw):
        return None


def sent_text(msg):
    return msg.sent[-1][0][0] if msg.sent else ""


async def run():
    from keyboards.keyboards import bank_keyboard
    from database.db import (
        init_db, close_db, add_user, set_report_tax_percent, set_sale_tax_percent,
    )
    from bot.handlers import bank as B
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

    uid = 439010
    try:
        await add_user(uid, "taxes_user", "Налоговик", "")
        await set_report_tax_percent(10)
        await set_sale_tax_percent(15)

        # 1. Кнопка в клавиатуре банка
        cbs = [b.callback_data for row in bank_keyboard().inline_keyboard for b in row]
        check("кнопка bank:taxes в клавиатуре банка", "bank:taxes" in cbs)

        # 2. Сводка с текущими ставками
        text = await B.bank_taxes_text(uid)
        check("отчёты: базовая ставка 10%", "Налог с отчётов: 10%" in text)
        check("продажи: 15%", "Налог с продаж: 15%" in text)
        check("контракты: 12%", "Налог с контракта на поставку: 12%" in text)
        check("жильё: студия 20 НМ", "Студия: 20 НМ" in text)
        check("жильё: особняк 100 НМ", "Особняк: 100 НМ" in text)
        check("жильё: кубрик без налога", "Кубрик: без налога" in text)
        check("без личной скидки строки нет", "Твоя ставка" not in text)

        # 3. Личная ставка (скидка наградами)
        async def personal_5(_uid):
            return 5
        original = B.report_tax_percent_for
        B.report_tax_percent_for = personal_5
        try:
            text_pers = await B.bank_taxes_text(uid)
        finally:
            B.report_tax_percent_for = original
        check("личная ставка 5% показана", "Твоя ставка с отчётов: 5%" in text_pers)
        check("минимум по наградам упомянут",
              f"не ниже {B.AWARD_MIN_REPORT_TAX}%" in text_pers)

        # 4. Английский интерфейс
        use_lang("en")
        try:
            text_en = await B.bank_taxes_text(uid)
        finally:
            use_lang("ru")
        check("EN: заголовок", "TAX RATES" in text_en)
        check("EN: отчёты 10%", "Report tax: 10%" in text_en)
        check("EN: продажи 15%", "Sales tax: 15%" in text_en)
        check("EN: жильё в NM (название из БД остаётся русским)", "Студия: 20 NM" in text_en)
        check("EN: без налога", "Кубрик: no tax" in text_en)

        # 5. Обработчик: зарегистрированный получает сводку с кнопкой назад
        cb = FakeCallback(uid, data="bank:taxes", message=FakeMessage(uid))
        await B.bank_taxes(cb)
        check("обработчик отправил сводку", "СТАВКИ НАЛОГОВ" in sent_text(cb.message))
        kw = cb.message.sent[-1][1]
        back = [b.callback_data for row in kw["reply_markup"].inline_keyboard for b in row]
        check("есть кнопка назад в банк", back == ["bank:menu"])

        # Незарегистрированный — тишина
        ghost = FakeCallback(439999, data="bank:taxes", message=FakeMessage(439999))
        await B.bank_taxes(ghost)
        check("незарегистрированному ничего не отправлено", not ghost.message.sent)
    finally:
        await close_db()
        if os.path.exists(_TEST_DB):
            os.remove(_TEST_DB)

    print(f"\nSmoke 239: {passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)


asyncio.run(run())
