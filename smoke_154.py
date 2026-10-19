"""Smoke v0.34.0: Деловой квартал, Загородные территории, новое главное меню.

1) Главное меню (reply): порядок Профиль → 📝 Сдать отчёт → Инвентарь/Магазин →
   🏠 Жильё → Город → 📰 Новости → 🧱 Стена изречений → 👑 Админ-панель;
   «📝 Сдать отчёт» больше не зависит от флага is_pilot, админ-кнопка внизу.
2) utils.helpers.MAIN_MENU_TEXTS содержит все тексты клавиатуры (иначе FSM-формы
   ловят нажатия меню как ввод данных).
3) Город: три подменю-квартала первыми кнопками, «🧱 Стена изречений» и
   «🏠 Жильё» из города убраны, локации кварталов скрыты из общего списка,
   «Курс выживания» остался.
4) «💼 Деловой квартал»: библиотека, парк, ГосСМИ, доска контрактов, дом дуэлей,
   НИИ, городские склады — в порядке владельца + «🔙 В город»; экран рисуется.
5) «🌲 Загородные территории»: лес на окраине, железная копи + «🔙 В город»;
   экран рисуется.
6) Reply-кнопка «🏠 Жильё»: рекруту рисуется экран жилья, туристу — отказ.

Запуск: .venv\\Scripts\\python.exe smoke_154.py
"""
import asyncio
import os
import sys

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke154.db")
for _suffix in ("", "-wal", "-shm"):
    _p = _TEST_DB + _suffix
    if os.path.exists(_p):
        os.remove(_p)
os.environ["DATABASE_PATH"] = _TEST_DB
os.environ["ADMIN_IDS"] = "999154"

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(__file__))


class FakeBot:
    def __init__(self):
        self.sent = []
        self.edited = []

    async def send_message(self, chat_id, text, **kw):
        self.sent.append(("message", text, kw))
        return type("M", (), {"message_id": len(self.sent)})()

    async def send_photo(self, chat_id, photo, caption=None, **kw):
        self.sent.append(("photo", caption, kw))
        return type("M", (), {"message_id": len(self.sent)})()

    async def edit_message_reply_markup(self, chat_id, message_id, reply_markup=None):
        self.edited.append((chat_id, message_id, reply_markup))


class FakeMessage:
    def __init__(self, user_id, bot=None):
        self.from_user = type("U", (), {"id": user_id})()
        self.chat = type("C", (), {"id": user_id})()
        self.bot = bot
        self.sent = []

    async def answer(self, text=None, *a, **kw):
        self.sent.append(("answer", text, kw))

    async def answer_photo(self, photo=None, caption=None, *a, **kw):
        self.sent.append(("answer_photo", caption, kw))


class FakeCallback:
    def __init__(self, user_id, data="", message=None):
        self.from_user = type("U", (), {"id": user_id})()
        self.message = message or FakeMessage(user_id)
        self.data = data
        self.alerts = []

    async def answer(self, text=None, *a, **kw):
        self.alerts.append(text)


def markup_callbacks(markup):
    out = set()
    for row in getattr(markup, "inline_keyboard", []) or []:
        for btn in row:
            out.add(btn.callback_data)
    return out


def markup_texts(markup):
    return [b.text for row in getattr(markup, "inline_keyboard", []) or [] for b in row]


def reply_rows(markup):
    return [[b.text for b in row] for row in markup.keyboard]


def texts_of(msg):
    return [m[1] for m in msg.sent if m[1]]


async def run():
    from database.db import init_db, add_user, get_all_locations, ensure_base_statuses, get_status_by_tag, grant_status
    from keyboards.keyboards import (
        main_menu_keyboard, city_keyboard, business_quarter_keyboard,
        countryside_keyboard, BUSINESS_QUARTER_KEYS, COUNTRYSIDE_KEYS,
        QUARTER_HIDDEN_KEYS, LOCATION_BUTTON_EMOJI as EMOJI,
    )
    from utils.helpers import MAIN_MENU_TEXTS, is_main_menu_text
    from bot.handlers import locations as locs
    from bot.handlers import housing as H

    await init_db()
    await ensure_base_statuses()

    uid_pilot = 710001
    uid_tourist = 710002
    await add_user(uid_pilot, "pilot", "Пилот", "")
    await add_user(uid_tourist, "turi", "Турист", "")

    rec = await get_status_by_tag("recruit")
    if rec:
        await grant_status(uid_pilot, rec["id"], 0)

    passed = 0
    failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
        else:
            failed += 1
            print(f"  FAIL: {name}")

    # ── 1. Главное меню: порядок и состав ──
    kb = main_menu_keyboard(is_admin=True, is_pilot=True)
    rows = reply_rows(kb)
    expected = [
        ["Профиль"],
        ["📝 Сдать отчёт"],
        ["Инвентарь", "Магазин"],
        ["🏠 Жильё"],
        ["Город"],
        ["📰 Новости Нордхайма"],
        ["🧱 Стена изречений"],
        ["👑 Админ-панель"],
    ]
    check("порядок главного меню как у владельца", rows == expected)
    flat = [t for row in rows for t in row]
    admin_row = rows[-1]
    check("админ-кнопка в самом низу", admin_row == ["👑 Админ-панель"])
    check("«Сдать отчёт» на второй позиции", rows[1] == ["📝 Сдать отчёт"])
    check("«Жильё» есть в главном меню", "🏠 Жильё" in flat)
    check("«Новости» и «Стена» после «Города»",
          flat.index("Город") < flat.index("📰 Новости Нордхайма") < flat.index("🧱 Стена изречений"))
    kb_t = main_menu_keyboard(is_admin=False, is_pilot=False)
    t_rows = reply_rows(kb_t)
    check("у не-админа нет «Админ-панели»", all("Админ" not in t for r in t_rows for t in r))
    check("у туриста кнопка «Сдать отчёт» на месте (отказ — в хендлере)",
          [t for r in t_rows for t in r][1] == "📝 Сдать отчёт")

    # ── 2. MAIN_MENU_TEXTS покрывает клавиатуру ──
    for text in flat:
        check(f"MAIN_MENU_TEXTS содержит «{text}»", text in MAIN_MENU_TEXTS)
    check("is_main_menu_text(\"🏠 Жильё\")", is_main_menu_text("🏠 Жильё"))
    check("«Банк» по-прежнему не входит в меню", not is_main_menu_text("Банк"))

    # ── 3. Клавиатура города ──
    locs_list = await get_all_locations()
    ck = city_keyboard(is_pilot=True, locations=locs_list)
    cbs = markup_callbacks(ck)
    c_texts = markup_texts(ck)
    check("первая кнопка города — «💼 Деловой квартал»", c_texts[0] == "💼 Деловой квартал")
    check("в городе три подменю",
          {"city:business", "city:quarter", "city:countryside"} <= cbs)
    check("«🧱 Стена изречений» убрана из города", "wall:view" not in cbs)
    check("«🏠 Жильё» убрано из города", "housing:menu" not in cbs)
    for k in QUARTER_HIDDEN_KEYS:
        check(f"город: скрыта локация {k}", f"location:preview:{k}" not in cbs)
    check("«Курс выживания» остался в городе", "location:preview:kvp" in cbs)
    for k in BUSINESS_QUARTER_KEYS + COUNTRYSIDE_KEYS:
        check(f"у {k} есть эмодзи кнопки", k in EMOJI)

    # ── 4. Деловой квартал ──
    bq = business_quarter_keyboard()
    b_cbs = markup_callbacks(bq)
    b_texts = markup_texts(bq)
    expected_business = [
        "📚 Библиотека", "🌳 Городской парк", "📰 ГосСМИ",
        "📜 Доска контрактов", "🥊 Дом Дуэлей", "🔬 НИИ Северной Кибернетики",
        "📦 Городские склады",
    ]
    check("в Деловом квартале 7 зданий в порядке владельца",
          b_texts[:7] == expected_business)
    check("ключи Делового квартала совпадают",
          [t.split(":")[-1] for t in sorted(b_cbs) if t.startswith("location:preview:")]
          == sorted(BUSINESS_QUARTER_KEYS))
    check("в Деловом квартале есть «🔙 В город»", "city:menu" in b_cbs)
    check("в Деловом квартале нет админ-зданий и загорода",
          not ({"location:preview:bank", "location:preview:hq",
                "location:preview:forest"} & b_cbs))

    cb_b = FakeCallback(uid_pilot, data="city:business")
    await locs.city_business_quarter(cb_b)
    b_screen = "\n".join(texts_of(cb_b.message))
    check("экран Делового квартала рисуется", "ДЕЛОВОЙ КВАРТАЛ" in b_screen)
    check("в экране перечислены здания",
          "библиотека" in b_screen and "городские склады" in b_screen)

    # ── 5. Загородные территории ──
    cs = countryside_keyboard()
    c_cbs = markup_callbacks(cs)
    c_texts_sub = markup_texts(cs)
    check("в Загородных территориях 2 локации",
          c_texts_sub[:2] == ["🌲 Лес на окраине", "⛏️ Железная копи"])
    check("ключи Загородных территорий совпадают",
          {"location:preview:forest", "location:preview:mine"} <= c_cbs)
    check("в Загородных территориях есть «🔙 В город»", "city:menu" in c_cbs)

    cb_c = FakeCallback(uid_pilot, data="city:countryside")
    await locs.city_countryside(cb_c)
    c_screen = "\n".join(texts_of(cb_c.message))
    check("экран Загородных территорий рисуется", "ЗАГОРОДНЫЕ ТЕРРИТОРИИ" in c_screen)
    check("в экране есть лес и копи", "лес" in c_screen and "копей" in c_screen)

    # ── 6. Reply-кнопка «🏠 Жильё» ──
    bot_ok = FakeBot()
    msg_ok = FakeMessage(uid_pilot, bot=bot_ok)
    await H.housing_menu_reply(msg_ok)
    check("пилоту-рекруту рисуется экран жилья",
          bool(bot_ok.sent))
    check("первый экран жилья отправлен сообщением",
          bot_ok.sent and bot_ok.sent[0][0] in ("message", "photo"))
    check("первый экран жилья с кнопками",
          bool(bot_ok.sent) and bot_ok.sent[0][2].get("reply_markup") is not None)

    msg_t = FakeMessage(uid_tourist, bot=FakeBot())
    await H.housing_menu_reply(msg_t)
    denied = "\n".join(t for t in texts_of(msg_t) if t)
    check("туристу отказ", "Жильё доступно только рекрутам" in denied)

    print(f"\nSmoke 154: {passed} passed, {failed} failed")
    return failed


if __name__ == "__main__":
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        failed = loop.run_until_complete(run())
    finally:
        try:
            from database.db import close_db
            loop.run_until_complete(close_db())
        except Exception:
            pass
        loop.close()
    sys.exit(1 if failed else 0)
