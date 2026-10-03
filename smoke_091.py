"""Smoke v0.15.34 (обновлён под v0.22.0): суточный лимит оплаты отчётов, гард чатов,
настройка чата/топика.

Что проверяем:
  • суточный лимит оплаты (по умолчанию 4000) режет «всё накопленное», но НЕ режет
    поле «всего» (в регионе накапливаются десятки тысяч);
  • лимит режет ОДИН снимок суток, а не сумму отчётов (v0.22.0): каждый новый отчёт
    снова оплачивается, платится по последнему отчёту суток;
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
        set_allowed_chats, get_db, reject_report,
    )
    from utils import chat_guard
    from utils.notify import notify
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
        """Отчёт «за вчера»: часом раньше границы текущих суток (10:00 МСК)."""
        from datetime import timedelta, timezone
        from database.db import report_day_bounds
        start, _end = report_day_bounds()
        ts = (start - timedelta(hours=1)).astimezone(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        conn = await get_db()
        await conn.execute(
            "INSERT INTO reports (user_id, screenshot_file_id, troops_reported, total_troops, "
            "region, credited_troops, status, paid, created_at) "
            "VALUES (?, 'f', ?, ?, '0', ?, 'approved', 1, ?)",
            (uid, daily, total, daily, ts))
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

    # ── 4. Второй отчёт в тот же день: за сутки платят ОДИН раз ──
    # Кап 4000 режет ОДИН снимок (шаг 3), но платят сутки один раз: снимок за сутки
    # уже выплачен (4000), поэтому новый отчёт не добавляет сверху. Раньше лимит
    # «съедался» суммой отчётов, а теперь суммы не существует вовсе.
    rid2, credited2 = await add_report(U, "f", 5000, 60000, "0")
    check("второй отчёт дня не доплачивает сверх выплаченного снимка", credited2 == 0)
    # Пилот, которому за сутки ещё не платили, получает снимок целиком — кап режет
    # снимок, а не «остаток суток» после предыдущих выплат.
    U_CAP = 70009
    await add_user(U_CAP, "cap09", "Пилот", "Девять")
    _, credited_cap = await add_report(U_CAP, "f", 999999, 7045, "0")
    check("снимок под капом платится целиком, если сутки ещё не оплачены",
          credited_cap == 4000)

    # ── 5. «Всего» (остаток очков в регионе) не ограничивает выплату ──
    U2 = 70002
    await add_user(U2, "cap02", "Пилот", "Два")
    await _yesterday_report(U2, 4000, 20000)
    ctx = await report_payout_context(U2, 4000, 50000)
    check("заявка 4000 засчитывается вся", ctx['claim'] == 4000)
    check("но к выдаче 4000 (лимит)", ctx['payable'] == 4000)
    check("«всего» 50000 — только справочно", ctx['total_claim'] == 50000)
    rid3, credited3 = await add_report(U2, "f", 4000, 50000, "0")
    check("отчёт с «всего» 50000 принят как 4000", credited3 == 4000)
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

    # ── 7c. Несколько отчётов за сутки = снимок, не сумма ──
    # Реальный кейс: отчёт 21/4077, потом 11/4098 в тот же МСК-день. Пока сутки не
    # оплачены, каждый отчёт показывает, сколько пилот заработает за день (11).
    # Реальная выплата — последний снимок, то есть 11, а не 21 + 11 = 32.
    UA = 70010
    await add_user(UA, "acc", "Акк", "Умножает")
    _, c1 = await add_report(UA, "f", 21, 4077, "0")
    _, c2 = await add_report(UA, "f", 11, 4098, "0")
    check("история есть — второй отчёт дня доплачивается (11, не 0)", c2 == 11)
    check("за сутки начислено 32", c1 + c2 == 32)

    # Первая заявка дня без истории: дальше отчёты суммируются, а не отбрасываются.
    UB = 70011
    await add_user(UB, "acc2", "Акк", "Второй")
    _, b1 = await add_report(UB, "f", 21, 4077, "0")
    _, b2 = await add_report(UB, "f", 11, 4098, "0")
    check("без истории первый отчёт по заявке", b1 == 21)
    check("без истории второй отчёт дня тоже платится (было 0)", b2 == 11)

    # «Всего» не влияет на оплату: платится заявка «за сутки» последнего отчёта.
    UC = 70012
    await add_user(UC, "acc3", "Акк", "Третий")
    await _yesterday_report(UC, 4000, 4000)
    _, d1 = await add_report(UC, "f", 160, 4160, "0")
    _, d2 = await add_report(UC, "f", 200, 4360, "0")
    check("первый отчёт дня 160 → 160", d1 == 160)
    check("второй отчёт дня 200 → 200", d2 == 200)
    ctx_dup = await report_payout_context(UC, 200, 4360)
    check("повторная заявка оплачивается снова (200)", ctx_dup['payable'] == 200)
    check("assigned_today = сумма заявок суток, справочно (360)",
          ctx_dup['assigned_today'] == 360)
    _, d3 = await add_report(UC, "f", 50, 4410, "0")
    check("третий отчёт 50 засчитывается", d3 == 50)
    ctx_cap3 = await report_payout_context(UC, 100000, 1000000)
    check("суточный лимит 4000 всё ещё режет", ctx_cap3['payable'] <= 4000)

    # Уже принято за сутки видно в контексте (для показа пилоту).
    ctx_acc = await report_payout_context(UA, 5, 4103)
    check("assigned_today учитывает оба отчёта", ctx_acc['assigned_today'] == 32)

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
    check("разрешённый чат проходит (бот работает как в личке)", len(handled) == 2)

    # Чат оповещений: бот ТОЛЬКО отправляет туда оповещения, команды игнорирует
    news = FakeMessage(FakeChat(-100999, "supergroup"), text="привет")
    res = await guard(handler, news, {})
    check("чат оповещений: текст игнорируется", res is None and len(handled) == 2)
    check("чат оповещений: подсказки в свой чат не шлём", not news.answers)
    news_cmd = FakeMessage(FakeChat(-100999, "supergroup"), text="/start")
    res = await guard(handler, news_cmd, {})
    check("чат оповещений: команда не доходит до хендлера",
          res is None and len(handled) == 2)
    check("чат оповещений: на команду тоже тишина", not news_cmd.answers)
    class FakeNewsCb:
        def __init__(self, chat):
            self.message = FakeMessage(chat)
            self.data = "admin:menu"
            self.from_user = type("U", (), {"id": 1})()
    res = await guard(handler, FakeNewsCb(FakeChat(-100999, "supergroup")), {})
    check("чат оповещений: нажатие кнопки игнорируется", res is None and len(handled) == 2)

    # Чужой чат: обычный текст — тишина
    foreign = FakeMessage(FakeChat(-100777, "supergroup"), text="просто текст")
    res = await guard(handler, foreign, {})
    check("чужой чат: текст игнорируется", res is None and len(handled) == 2)
    check("чужой чат: подсказки на текст нет", not foreign.answers)

    # Чужой чат: команда — одна подсказка, и только раз в час
    cmd = FakeMessage(FakeChat(-100777, "supergroup"), text="/start")
    await guard(handler, cmd, {})
    check("чужой чат: команда не доходит до хендлера", len(handled) == 2)
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
    check("callback из чужого чата игнорируется", res is None and len(handled) == 2)

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
          res == "ok" and len(handled) == 3)
    check("/chatinfo не съедает лимит подсказок", not setup.answers)

    setup_cb = FakeCallbackQuery(
        FakeMessage(FakeChat(-100555, "supergroup"), user_id=admin_id),
        data="news:chat", user_id=admin_id)
    res = await guard(handler, setup_cb, {})
    check("кнопка сохранения чата проходит", res == "ok" and len(handled) == 4)

    # Обычный пилот в чужом чате — по-прежнему тишина
    fake_pilot = FakeMessage(FakeChat(-100666, "supergroup"), text="/chatinfo", user_id=user_id)
    res = await guard(handler, fake_pilot, {})
    check("чужой пилот: /chatinfo срезается, хендлер не вызван",
          res is None and len(handled) == 4)

    # Сохранение чата сразу сбрасывает кэш гарда — правила применяются без перезапуска
    await set_news_chat(-100555, 42)
    fresh = FakeMessage(FakeChat(-100555, "supergroup"), text="привет", user_id=user_id)
    res = await guard(handler, fresh, {})
    check("после сохранения чат оповещений — режим «только отправка»",
          res is None and len(handled) == 4)
    check("кэш гарда сброшен без перезапуска", chat_guard._cache["ts"] > 0)
    check("чат оповещений запомнен гардом", chat_guard._cache["news"] == -100555)

    # Даже если чат оповещений добавить в рабочие — он остаётся «только отправка»
    await set_allowed_chats([-100555])
    res = await guard(handler, fresh, {})
    check("чат оповещений в рабочем списке всё равно игнорирует команды",
          res is None and len(handled) == 4)

    # А вот другой чат из рабочего списка работает как в личке
    await set_allowed_chats([-100555, -100444])
    work = FakeMessage(FakeChat(-100444, "supergroup"), text="/start", user_id=user_id)
    res = await guard(handler, work, {})
    check("разрешённый чат работает полноценно", res == "ok" and len(handled) == 5)

    # Отправка оповещений бот делает сам — гард не мешает исходящим
    class FakeBot:
        def __init__(self):
            self.sent = []

        async def send_message(self, chat_id, text, message_thread_id=None):
            self.sent.append((chat_id, text, message_thread_id))

    fake_bot = FakeBot()
    await notify(fake_bot, "✅ Отчёт принят на 1 войск!", None)
    check("оповещение уходит в чат и топик",
          fake_bot.sent == [(-100555, "✅ Отчёт принят на 1 войск!", 42)])

    # ── 8. Тексты оповещений: похвала без цифр, награда общим текстом ──
    from utils.notify import (report_praise_text, notify_award, notify_report_praise,
                              praise_tier_for)
    check("отчёт 150 и ниже — без оповещения",
          report_praise_text("@vasya", 150) is None and report_praise_text("@vasya", 1) is None)
    m = report_praise_text("@vasya", 151)
    check("отчёт 151 — «высокое мастерство»",
          bool(m) and "высокое мастерство" in m and "@vasya" in m)
    m300 = report_praise_text("@vasya", 300)
    check("отчёт 300 — ещё мастерство, не Ас",
          bool(m300) and "мастерство" in m300 and "Аса" not in m300)
    ace = report_praise_text("@vasya", 301)
    check("отчёт 301 — «истинный Ас»", bool(ace) and "истинного Аса" in ace)
    check("в похвале нет точных цифр отчёта",
          all(str(n) not in (ace or "") for n in (301, 300, 150))
          and all(str(n) not in (m or "") for n in (151, 150)))
    check("уровень считается по сумме за сутки: 150→0, 151→1, 300→1, 301→2",
          (praise_tier_for(150), praise_tier_for(151), praise_tier_for(300),
           praise_tier_for(301)) == (0, 1, 1, 2))

    bot2 = FakeBot()
    await notify_award(bot2, {"username": "petr", "first_name": "Пётр", "user_id": 5},
                       "🏅 Значок Отваги", 5)
    check("награда: общий текст «награждён: <название>»",
          bot2.sent == [(-100555, "🎖️ @petr награждён: 🏅 Значок Отваги", 42)])
    bot3 = FakeBot()
    await notify_award(bot3, None, "", None)
    check("награда без названия не ломает текст",
          bot3.sent == [(-100555, "🎖️ пилот награждён: награда", 42)])

    # Похвала шлётся только при принятии: отклонение и «в очереди» её не порождают.
    # Уровень — от накопленной суммы за сутки, один уровень за сутки отправляется один раз.
    from database.db import reject_report, report_day_credited_total
    U6 = 70006
    await add_user(U6, "ace", "Ас", "Асов")
    rid6, credited6 = await add_report(U6, "f", 400, 400, "0")
    check("крупный отчёт ждёт одобрения", credited6 == 400)
    bot4 = FakeBot()
    await notify_report_praise(bot4, {"username": "ace", "first_name": "Ас", "user_id": U6}, U6)
    check("неодобренный отчёт похвалы не вызывает (в очереди)", not bot4.sent)
    paid = await approve_report(rid6, 0)
    bot5 = FakeBot()
    await notify_report_praise(bot5, {"username": "ace", "first_name": "Ас", "user_id": U6}, U6)
    check("принятый отчёт 400 → «истинный Ас»", bot5.sent ==
          [(-100555, "🏆 @ace проявляет характер истинного Аса!", 42)])
    bot5b = FakeBot()
    await notify_report_praise(bot5b, {"username": "ace", "first_name": "Ас", "user_id": U6}, U6)
    check("повтор того же уровня за сутки не дублируется", not bot5b.sent)
    rid7, _ = await add_report(U6, "f", 5, 405, "0")
    await reject_report(rid7, 0)
    bot6 = FakeBot()
    await notify_report_praise(bot6, {"username": "ace", "first_name": "Ас", "user_id": U6}, U6)
    check("отклонённый отчёт похвалы не вызывает", not bot6.sent)

    # За сутки считается последний принятый отчёт (v0.22.0), а не сумма: снимок
    # растёт 160 → 400, похвала растёт вместе с ним, как и выплата.
    U7 = 70013
    await add_user(U7, "sum", "Сум", "Накопитель")
    r1, _ = await add_report(U7, "f", 160, 4160, "0")
    await approve_report(r1, 0)
    check("за сутки 160", await report_day_credited_total(U7) == 160)
    b7 = FakeBot()
    await notify_report_praise(b7, {"username": "sum", "first_name": "Сум", "user_id": U7}, U7)
    check("160 за сутки → «высокое мастерство»", len(b7.sent) == 1
          and "мастерство" in b7.sent[0][1])
    r2, _ = await add_report(U7, "f", 400, 4560, "0")
    await approve_report(r2, 0)
    check("после нового снимка за сутки 400, не сумма 560",
          await report_day_credited_total(U7) == 400)
    b8 = FakeBot()
    await notify_report_praise(b8, {"username": "sum", "first_name": "Сум", "user_id": U7}, U7)
    check("снимок 400 за сутки → второе оповещение «истинный Ас»", len(b8.sent) == 1
          and "истинного Аса" in b8.sent[0][1])
    r3, _ = await add_report(U7, "f", 50, 4610, "0")
    await approve_report(r3, 0)
    b9 = FakeBot()
    await notify_report_praise(b9, {"username": "sum", "first_name": "Сум", "user_id": U7}, U7)
    check("снимок упал обратно — тишина", not b9.sent)

    # Ниже порога за сутки — молчим: считается последний снимок (40), а 100 + 40
    # больше не складываются в 140.
    U8 = 70014
    await add_user(U8, "quiet", "Тихий", "Молчун")
    q1, _ = await add_report(U8, "f", 100, 100, "0")
    await approve_report(q1, 0)
    q2, _ = await add_report(U8, "f", 40, 140, "0")
    await approve_report(q2, 0)
    b10 = FakeBot()
    await notify_report_praise(b10, {"username": "quiet", "first_name": "Тихий", "user_id": U8}, U8)
    check("40 за сутки (последний снимок) — без оповещения", not b10.sent)

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
