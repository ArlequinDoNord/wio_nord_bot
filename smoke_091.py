"""Smoke v0.15.34: суточный лимит оплаты отчётов, гард чатов, настройка чата/топика.

Что проверяем:
  • суточный лимит оплаты (по умолчанию 4000) режет «всё накопленное», но НЕ режет
    поле «всего» (в регионе накапливаются десятки тысяч);
  • одобренные отчёты по-прежнему оплачиваются, просто не больше лимита за сутки;
  • гард чатов: вне лички и белого списка бот не отвечает, на команду — одна
    подсказка в час;
  • настройки чата/топика оповещений (get/set_news_chat) и белый список чатов.

Запуск: .venv\\Scripts\\python.exe smoke_091.py
"""
import asyncio
import os
import sys

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke091.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB

sys.path.insert(0, os.path.dirname(__file__))


class FakeChat:
    def __init__(self, chat_id, ctype="supergroup"):
        self.id = chat_id
        self.type = ctype


class FakeMessage:
    def __init__(self, chat, text=None, user_id=1):
        self.chat = chat
        self.text = text
        self.from_user = type("U", (), {"id": user_id})()
        self.message_thread_id = None
        self.answers = []
        self.answer_kwargs = []

    async def answer(self, text, **kwargs):
        self.answers.append(text)
        self.answer_kwargs.append(kwargs)


class FakeCallbackQuery:
    def __init__(self, message, data="", user_id=1):
        self.message = message
        self.data = data
        self.from_user = type("U", (), {"id": user_id})()
        self.answered = False

    async def answer(self, *a, **kw):
        self.answered = True


async def run():
    from database.db import (
        init_db, close_db, add_user, add_report, approve_report, payout_reports,
        report_payout_context, correct_report_numbers, get_report_daily_pay_cap,
        set_report_daily_pay_cap, get_news_chat, set_news_chat, get_allowed_chats,
        set_allowed_chats, get_db,
    )
    from utils import chat_guard
    from utils.permissions import get_user_role

    await init_db()
    passed = 0
    failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
        else:
            failed += 1
            print(f"  FAIL: {name}")

    async def _yesterday_report(uid, daily, total):
        conn = await get_db()
        await conn.execute(
            "INSERT INTO reports (user_id, screenshot_file_id, troops_reported, total_troops, "
            "region, credited_troops, status, paid, created_at) "
            "VALUES (?, 'f', ?, ?, '0', ?, 'approved', 1, datetime('now', '-1 day'))",
            (uid, daily, total, daily))
        await conn.commit()

    # ── 1. Лимит по умолчанию и настройка ──
    check("лимит по умолчанию 4000", await get_report_daily_pay_cap() == 4000)
    await set_report_daily_pay_cap(4000)
    check("лимит сохраняется в настройках", await get_report_daily_pay_cap() == 4000)

    # ── 2. Первый отчёт-«всё накопленное» режется лимитом (был кейс 999999) ──
    U = 70001
    await add_user(U, "cap01", "Пилот", "Один")
    rid, credited = await add_report(U, "f", 999999, 7045, "0")
    check("первый отчёт 999999 обрезан до лимита 4000", credited == 4000)
    ctx = await report_payout_context(U, 999999, 7045, exclude_id=rid)
    check("capped_by_limit выставлен", ctx['capped_by_limit'] is True)
    check("к выдаче 4000", ctx['payable'] == 4000)

    # ── 3. Одобрение платит, но не больше лимита ──
    amount = await approve_report(rid, 0)
    check("одобрение платит 4000, не 999999", amount == 4000)
    payouts = await payout_reports()
    paid = [p for p in payouts if p['user_id'] == U]
    check("выплата за сутки = 4000", paid and paid[0]['troops'] == 4000)

    # ── 4. Второй отчёт в тот же день: лимит уже исчерпан ──
    rid2, credited2 = await add_report(U, "f", 5000, 60000, "0")
    check("второй отчёт в тот же день — 0 (лимит исчерпан)", credited2 == 0)

    # ── 5. «Всего» лимитом не ограничивается (накопление 50000) ──
    U2 = 70002
    await add_user(U2, "cap02", "Пилот", "Два")
    await _yesterday_report(U2, 4000, 20000)
    ctx = await report_payout_context(U2, 4000, 50000)
    check("прирост 30000 считается", ctx['growth'] == 30000)
    check("но к выдаче 4000 (лимит)", ctx['payable'] == 4000)
    rid3, credited3 = await add_report(U2, "f", 4000, 50000, "0")
    check("отчёт с «всего» 50000 принят в базу как 4000", credited3 == 4000)
    conn = await get_db()
    cur = await conn.execute("SELECT total_troops FROM reports WHERE id = ?", (rid3,))
    row = await cur.fetchone()
    check("поле «всего» 50000 сохранено без изменений", row['total_troops'] == 50000)

    # ── 6. Лимит = 0 → без ограничения ──
    await set_report_daily_pay_cap(0)
    U3 = 70003
    await add_user(U3, "cap03", "Пилот", "Три")
    _, c = await add_report(U3, "f", 999999, 999999, "0")
    check("лимит 0 → платится вся заявка", c == 999999)
    await set_report_daily_pay_cap(4000)

    # ── 7. Правка цифр тоже уважает лимит ──
    U4 = 70004
    await add_user(U4, "cap04", "Пилот", "Четыре")
    rid4, _ = await add_report(U4, "f", 6000, 6000, "0")
    ctx4 = await correct_report_numbers(rid4, 6000, 6000, 1)
    check("правка: к выдаче обрезано лимитом 4000", ctx4['payable'] == 4000)
    check("правка: обрезание отмечено", ctx4['capped_by_limit'] is True)

    # ── 7b. Последний рубеж: одобрение тоже режет по лимиту ──
    # Отчёт с завышенной credited_troops, посчитанной ДО введения лимита.
    U5 = 70005
    await add_user(U5, "cap05", "Пилот", "Пять")
    conn = await get_db()
    cur = await conn.execute(
        "INSERT INTO reports (user_id, screenshot_file_id, troops_reported, total_troops, "
        "region, credited_troops, status, created_at) "
        "VALUES (?, 'f', 999999, 7045, '0', 999999, 'pending', datetime('now'))", (U5,))
    rid5 = cur.lastrowid
    await conn.commit()
    check("одобрение старого завышенного отчёта режется до лимита",
          await approve_report(rid5, 0) == 4000)
    row5 = await (await conn.execute(
        "SELECT credited_troops FROM reports WHERE id = ?", (rid5,))).fetchone()
    check("в базе тоже зафиксировано 4000", row5['credited_troops'] == 4000)

    # ── 8. Настройки чата/топика оповещений ──
    chat_id, topic = await get_news_chat()
    check("изначально чат не настроен (окружение пустое)", chat_id is None)
    await set_news_chat(-1001234567890, 42)
    chat_id, topic = await get_news_chat()
    check("чат сохранён", chat_id == -1001234567890)
    check("топик сохранён", topic == 42)
    await set_news_chat(-1001234567890, None)
    chat_id, topic = await get_news_chat()
    check("топик сброшен", topic is None)
    await set_news_chat(None, None)
    check("оповещения выключены", (await get_news_chat()) == (None, None))

    # ── 9. Белый список чатов ──
    await set_allowed_chats([-100111, -100222])
    check("белый список из 2 чатов", (await get_allowed_chats()) == [-100111, -100222])
    await set_allowed_chats([])
    check("список пуст", (await get_allowed_chats()) == [])

    # ── 10. Гард чатов: личка и список проходят, чужие — тишина ──
    await set_allowed_chats([-100111])
    await set_news_chat(-100999, None)
    chat_guard.reset_cache()

    handled = []

    async def handler(event, data):
        handled.append(event)
        return "ok"

    guard = chat_guard.ChatGuard()

    priv = FakeMessage(FakeChat(555, "private"), text="/start")
    check("личный чат проходит", await guard(handler, priv, {}) == "ok")
    check("хендлер вызван в личке", len(handled) == 1)

    allowed = FakeMessage(FakeChat(-100111, "supergroup"), text="/start")
    await guard(handler, allowed, {})
    check("разрешённый чат проходит", len(handled) == 2)

    news = FakeMessage(FakeChat(-100999, "supergroup"), text="привет")
    await guard(handler, news, {})
    check("чат оповещений проходит", len(handled) == 3)

    # Чужой чат: обычный текст — тишина
    foreign = FakeMessage(FakeChat(-100777, "supergroup"), text="просто текст")
    res = await guard(handler, foreign, {})
    check("чужой чат: текст игнорируется", res is None and len(handled) == 3)
    check("чужой чат: подсказки на текст нет", not foreign.answers)

    # Чужой чат: команда — одна подсказка, и только раз в час
    cmd = FakeMessage(FakeChat(-100777, "supergroup"), text="/start")
    await guard(handler, cmd, {})
    check("чужой чат: команда не доходит до хендлера", len(handled) == 3)
    check("чужой чат: подсказка отправлена", len(cmd.answers) == 1)
    check("в подсказке есть ник бота", "Nord_Wio_bot" in cmd.answers[0])

    cmd2 = FakeMessage(FakeChat(-100777, "supergroup"), text="/start")
    await guard(handler, cmd2, {})
    check("вторая команда подряд — без подсказки (лимит 1/час)", len(cmd2.answers) == 0)

    # Другой чужой чат — подсказка своя
    other = FakeMessage(FakeChat(-100888, "supergroup"), text="/help")
    await guard(handler, other, {})
    check("другой чат получает свою подсказку", len(other.answers) == 1)

    # Через час подсказка снова уходит
    chat_guard._hints[-100777] = chat_guard._hints[-100777] - chat_guard.HINT_INTERVAL - 1
    cmd3 = FakeMessage(FakeChat(-100777, "supergroup"), text="/start")
    await guard(handler, cmd3, {})
    check("после часа подсказка повторяется", len(cmd3.answers) == 1)

    # Callback в чужом чате — тишина
    class FakeEvent:
        def __init__(self, chat):
            self.message = FakeMessage(chat)
    cb = FakeEvent(FakeChat(-100777, "supergroup"))
    res = await guard(handler, cb, {})
    check("callback из чужого чата игнорируется", res is None and len(handled) == 3)

    # ── 6b. Настройка своего чата из самого чата: супер-админ проходит ──
    admin_id = 990001
    user_id = 990002
    await add_user(admin_id, "super", "Супер", "Админ")
    await add_user(user_id, "pilot", "Пилот", "Пилотов")
    conn = await get_db()
    await conn.execute(
        "INSERT OR IGNORE INTO user_roles (telegram_id, role, granted_by) VALUES (?, ?, ?)",
        (admin_id, "super_admin", admin_id))
    await conn.commit()
    check("супер-админ в тесте есть", "super_admin" in await get_user_role(admin_id))

    setup = FakeMessage(FakeChat(-100555, "supergroup"), text="/chatinfo", user_id=admin_id)
    res = await guard(handler, setup, {})
    check("/chatinfo супер-админа проходит даже вне белого списка",
          res == "ok" and len(handled) == 4)
    check("/chatinfo не съедает лимит подсказок", not setup.answers)

    setup_cb = FakeCallbackQuery(
        FakeMessage(FakeChat(-100555, "supergroup"), user_id=admin_id),
        data="news:chat", user_id=admin_id)
    res = await guard(handler, setup_cb, {})
    check("кнопка сохранения чата проходит", res == "ok" and len(handled) == 5)

    # Обычный пилот в чужом чате — по-прежнему тишина
    fake_pilot = FakeMessage(FakeChat(-100666, "supergroup"), text="/chatinfo", user_id=user_id)
    res = await guard(handler, fake_pilot, {})
    check("чужой пилот: /chatinfo срезается, хендлер не вызван",
          res is None and len(handled) == 5)

    # Сохранение чата сразу сбрасывает кэш гарда — чат начинает работать без перезапуска
    await set_news_chat(-100555, 42)
    fresh = FakeMessage(FakeChat(-100555, "supergroup"), text="привет", user_id=user_id)
    res = await guard(handler, fresh, {})
    check("после сохранения чат оповещений работает сразу", res == "ok" and len(handled) == 6)
    check("кэш гарда сброшен без перезапуска", chat_guard._cache["ts"] > 0)

    await close_db()
    print(f"\nSmoke 091: {passed} passed, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    async def _main():
        try:
            return await run()
        finally:
            from database.db import close_db
            await close_db()

    sys.exit(asyncio.run(_main()))
