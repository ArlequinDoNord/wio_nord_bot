# -*- coding: utf-8 -*-
"""Smoke 214 — банк: кнопка «История транзакций» (bank:history) отвечает экраном.

Регресс: в bot/handlers/bank.py цикл `for t in txns` перекрывал функцию t() i18n,
после цикла t("bank.back") падал с TypeError, и сообщение не отправлялось
(пилоты видели «кнопка не нажимается»).

1. Пустая история → текст «Пока нет транзакций», без исключения.
2. 3 транзакции → экран истории, строки записей, кнопка «🔙 В банк».
3. 20 транзакций: стр.1 → кнопка «Старее ▶️», без «Новее»; стр.2 → «⬅️ Новее».
4. Английский язык: та же навигация переводится (ContextVar lang=en).
"""
import asyncio
import os
import sys

os.environ["DATABASE_PATH"] = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "_test_smoke214.db")

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
            print(f"  FAIL {name}")

    import database.db as db
    from database.db import init_db, add_user, get_db, add_nordmarks, close_db
    from bot.handlers import bank as bh
    from utils.i18n import _current

    await init_db()
    conn = await get_db()
    for tbl in ("transactions", "users"):
        await conn.execute(f"DELETE FROM {tbl}")
    await conn.commit()

    UID = 214001
    await add_user(UID, 'h', 'Гость Банка', "")

    class FakeMsg:
        def __init__(self):
            self.sent = []

        async def answer(self, text=None, reply_markup=None, **kw):
            self.sent.append((text, reply_markup))
            return True

    class FakeCB:
        def __init__(self, uid, data):
            self.from_user = type("U", (), {"id": uid})()
            self.data = data
            self.message = FakeMsg()

        async def answer(self, *a, **kw):
            return True

    def buttons(markup):
        return [b.text for row in markup.inline_keyboard for b in row]

    print("\n1. Пустая история")
    cb0 = FakeCB(UID, "bank:history")
    await bh.bank_history(cb0)
    check("пустая история: ответ отправлен", len(cb0.message.sent) == 1)
    check("пустая история: текст «Пока нет транзакций»",
          cb0.message.sent and "Пока нет транзакций" in cb0.message.sent[0][0])

    print("\n2. 3 транзакции → экран истории")
    for i in range(3):
        await add_nordmarks(UID, 10, "admin", f"начисл {i}")
    cb1 = FakeCB(UID, "bank:history")
    await bh.bank_history(cb1)
    check("экран истории отправлен", len(cb1.message.sent) == 1)
    text1, kb1 = cb1.message.sent[0]
    check("заголовок «История транзакций (стр. 1)»", "История транзакций (стр. 1)" in text1)
    check("строки записей выведены", text1.count("НМ") == 3)
    check("есть кнопка «В банк»", "🔙 В банк" in buttons(kb1))
    check("одна страница: нет «Старее»", "Старее ▶️" not in buttons(kb1))

    print("\n3. 20 транзакций: листание")
    for i in range(17):
        await add_nordmarks(UID, 1, "admin", f"доп {i}")
    cb2 = FakeCB(UID, "bank:history:1")
    await bh.bank_history(cb2)
    text2, kb2 = cb2.message.sent[0]
    b2 = buttons(kb2)
    check("стр.2 (индекс 1): «⬅️ Новее»", "⬅️ Новее" in b2)
    check("стр.2: «Старее» отсутствует (это последняя)", "Старее ▶️" not in b2)
    check("стр.2: заголовок со страницей 2", "(стр. 2)" in text2)

    cb3 = FakeCB(UID, "bank:history:0")
    await bh.bank_history(cb3)
    b3 = buttons(cb3.message.sent[0][1])
    check("стр.1: «Старее ▶️» есть (20 записей → 2 стр.)", "Старее ▶️" in b3)
    check("стр.1: «Новее» нет", "⬅️ Новее" not in b3)

    print("\n4. Английский интерфейс")
    token = _current.set("en")
    try:
        cb4 = FakeCB(UID, "bank:history:0")
        await bh.bank_history(cb4)
        b4 = buttons(cb4.message.sent[0][1])
        check("en: «Older ▶️» на первой странице", "Older ▶️" in b4)
        check("en: «Back to bank»", "🔙 Back to bank" in b4)
        check("en: заголовок английский", "Transaction history" in cb4.message.sent[0][0])
    finally:
        _current.reset(token)

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
                               "_test_smoke214.db"))
    except OSError:
        pass
