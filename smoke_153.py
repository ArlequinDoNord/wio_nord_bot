"""Smoke v0.33.0: Здание МВД + Административный квартал.

1) Локация `mvd` засеяна (всем видно превью, вход по ролям/статусу), строка
   доступа и эмодзи кнопки.
2) Доступ `can_enter_mvd`: МВД (moderator), вице-доминус (mvd_helper),
   Представитель, Хранитель (super_admin) и владелец (.env) + статус keeper.
   Обычного пилота и туриста не пускают.
3) Вход через location_enter отсекает посторонних, а допущенных ведёт в меню МВД.
4) Архив: count_reports_all / get_reports_page (порядок + постранично),
   get_report_with_user; карточка отчёта с фото.
5) Меню города: 4 админ-здания вынесены в «Административный квартал»; подменю
   квартала ведёт в их превью.
6) «Мои отчёты» пагинированы, карточка видна владельцу и проверяющим МВД,
   посторонним — нет.

Запуск: .venv\\Scripts\\python.exe smoke_153.py
"""
import asyncio
import os
import sys

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke153.db")
for _suffix in ("", "-wal", "-shm"):
    _p = _TEST_DB + _suffix
    if os.path.exists(_p):
        os.remove(_p)
os.environ["DATABASE_PATH"] = _TEST_DB
os.environ["ADMIN_IDS"] = "999153"

sys.path.insert(0, os.path.dirname(__file__))


class FakeMessage:
    def __init__(self, user_id, bot=None):
        self.from_user = type("U", (), {"id": user_id})()
        self.chat = type("C", (), {"id": user_id})()
        self.message_id = 1
        self.bot = bot
        self.sent = []

    async def answer(self, text=None, *a, **kw):
        self.sent.append(("answer", text, kw))

    async def answer_photo(self, photo=None, caption=None, *a, **kw):
        self.sent.append(("answer_photo", caption, kw))

    async def edit_text(self, text=None, *a, **kw):
        self.sent.append(("edit_text", text, kw))

    async def __getattr__(self, name):
        async def _noop(*a, **kw):
            return None
        return _noop


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


def last_markup(cb):
    for m in reversed(cb.message.sent):
        if m[2].get("reply_markup"):
            return m[2]["reply_markup"]
    return None


def texts_of(cb):
    return [m[1] for m in cb.message.sent if m[1]]


def photos_of(cb):
    return [m[1] for m in cb.message.sent if m[0] == "answer_photo"]


async def run():
    from aiogram.fsm.context import FSMContext
    from aiogram.fsm.storage.memory import MemoryStorage

    from database.db import (
        init_db, close_db, seed_default_items, add_user, add_report, get_db,
        count_reports_all, get_reports_page, get_report_with_user,
        get_all_locations, get_location_by_key, ensure_base_statuses,
        get_status_by_tag, grant_status,
    )
    from utils.permissions import can_enter_mvd
    from keyboards.keyboards import (
        city_keyboard, admin_quarter_keyboard, ADMIN_QUARTER_KEYS,
        BUSINESS_QUARTER_KEYS, COUNTRYSIDE_KEYS, LOCATION_BUTTON_EMOJI,
    )
    from bot.handlers import locations as locs
    from bot.handlers import mvd as mvdh
    from bot.handlers import reports as rep
    import config

    await init_db()
    await seed_default_items()
    await ensure_base_statuses()

    passed = 0
    failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
        else:
            failed += 1
            print(f"  FAIL: {name}")

    conn = await get_db()

    async def set_role(uid, role):
        await conn.execute(
            "INSERT OR IGNORE INTO user_roles (telegram_id, role, granted_by) VALUES (?, ?, ?)",
            (uid, role, 999153))
        await conn.commit()

    owner = 999153
    mod = 999154
    helper = 999155
    wing = 999156
    keeper_u = 999157
    pilot = 999158
    tourist = 999159
    reporter = 999160
    for u in (mod, helper, wing, keeper_u, pilot, tourist, reporter):
        await add_user(u, f"u{u}", f"Пилот{u}", "")

    await set_role(mod, "moderator")
    await set_role(helper, "mvd_helper")
    await set_role(wing, "representative")
    await set_role(reporter, "journalist")  # чужая роль — в МВД не должна пускать

    keeper_status = await get_status_by_tag("keeper")
    await grant_status(keeper_u, keeper_status['id'], owner)

    try:
        # ── 1. локация mvd ───────────────────────────────────────────────────
        mvd_loc = await get_location_by_key("mvd")
        check("локация mvd засеяна", mvd_loc is not None)
        check("mvd: доступ 'all' (гейт в коде, не в статусе)",
              mvd_loc and mvd_loc['access_mode'] == "all")
        check("mvd: картинка входа city/mvd",
              mvd_loc and mvd_loc['preview_photo'] == "city/mvd")
        check("mvd: есть в списке локаций",
              any(l['key'] == "mvd" for l in await get_all_locations()))
        check("mvd: своя строка доступа",
              "МВД" in locs.LOCATION_ACCESS_LINES.get("mvd", ""))
        check("mvd: эмодзи кнопки 🚔", LOCATION_BUTTON_EMOJI.get("mvd") == "🚔")
        check("REPORT_ARCHIVE_PAGE = 8", config.REPORT_ARCHIVE_PAGE == 8)

        # ── 2. матрица доступа can_enter_mvd ─────────────────────────────────
        check("владелец (.env ADMIN_IDS) входит", await can_enter_mvd(owner))
        check("МВД (moderator) входит", await can_enter_mvd(mod))
        check("вице-доминус (mvd_helper) входит", await can_enter_mvd(helper))
        check("Представитель входит", await can_enter_mvd(wing))
        check("Хранитель (status keeper) входит", await can_enter_mvd(keeper_u))
        check("обычного пилота не пускают", not await can_enter_mvd(pilot))
        check("туриста не пускают", not await can_enter_mvd(tourist))
        check("чужая роль (журналист) не пускает", not await can_enter_mvd(reporter))

        # ── 2b. превью локации (кнопка видна всем) ──────────────────────────
        cb_prev = FakeCallback(pilot, data="location:preview:mvd")
        await locs.location_preview(cb_prev)
        prev_text = "\n".join(texts_of(cb_prev))
        check("превью МВД: видно всем", "Здание МВД" in prev_text)
        check("превью МВД: строка доступа «МВД»", "МВД" in prev_text)

        # ── 3. вход через location_enter ─────────────────────────────────────
        st = FSMContext(MemoryStorage(), key=("t", pilot))
        cb_deny = FakeCallback(pilot, data="location:enter:mvd")
        await locs.location_enter(cb_deny, st)
        check("постороннему вход закрыт",
              any("только для сотрудников МВД" in (t or "") for t in texts_of(cb_deny)))

        st2 = FSMContext(MemoryStorage(), key=("t", mod))
        cb_ok = FakeCallback(mod, data="location:enter:mvd")
        await locs.location_enter(cb_ok, st2)
        check("допущенного ведут в меню МВД",
              any("ЗДАНИЕ МВД" in (t or "") for t in texts_of(cb_ok)))

        # ── 4. архив отчётов ─────────────────────────────────────────────────
        ids = []
        for i in range(10):
            rid, _ = await add_report(reporter, f"file_{i}", 100 + i, 500 + i, "3")
            ids.append(rid)
        check("count_reports_all = 10", await count_reports_all() == 10)

        page0 = await get_reports_page(0, 8)
        page1 = await get_reports_page(8, 8)
        check("страница 0: ровно 8", len(page0) == 8)
        check("страница 1: остаток 2", len(page1) == 2)
        check("порядок — новые сверху (id DESC)",
              [r['id'] for r in page0][0] == max(ids))
        check("в странице есть автор из JOIN users",
              page0[0]['first_name'] == f"Пилот{reporter}")

        one = await get_report_with_user(ids[0])
        check("get_report_with_user отдаёт отчёт + автора",
              one and one['id'] == ids[0] and 'first_name' in one)

        # ── 5. квартира: клавиатура города ───────────────────────────────────
        locs_list = await get_all_locations()
        city_cbs = markup_callbacks(city_keyboard(is_pilot=True, locations=locs_list))
        for k in ADMIN_QUARTER_KEYS:
            check(f"город: нет кнопки location:preview:{k}",
                  f"location:preview:{k}" not in city_cbs)
        check("город: есть кнопка квартала city:quarter", "city:quarter" in city_cbs)
        for k in BUSINESS_QUARTER_KEYS + COUNTRYSIDE_KEYS:
            check(f"город: нет кнопки location:preview:{k} (подменю, v0.34)",
                  f"location:preview:{k}" not in city_cbs)
        check("город: kvp остался в общем списке",
              "location:preview:kvp" in city_cbs)
        check("город: стена и жильё убраны (v0.34)",
              "wall:view" not in city_cbs and "housing:menu" not in city_cbs)
        check("город: кнопки «Деловой квартал» и «Загородные территории»",
              "city:business" in city_cbs and "city:countryside" in city_cbs)

        q_cbs = markup_callbacks(admin_quarter_keyboard())
        check("квартал: 4 здания (Банк, Ратуша, Штаб, МВД)",
              {"location:preview:bank", "location:preview:townhall",
               "location:preview:hq", "location:preview:mvd"} <= q_cbs)
        check("квартал: кнопка «В город»", "city:menu" in q_cbs)
        check("квартал: в подменю нет обычных локаций",
              "location:preview:park" not in q_cbs)

        cb_q = FakeCallback(pilot, data="city:quarter")
        await locs.city_admin_quarter(cb_q)
        check("экран квартала рисуется",
              any("АДМИНИСТРАТИВНЫЙ КВАРТАЛ" in (t or "") for t in texts_of(cb_q)))

        # ── 6. меню МВД и архив-экран ────────────────────────────────────────
        cb_menu = FakeCallback(mod, data="mvd:menu")
        await mvdh.mvd_menu(cb_menu)
        menu_cbs = markup_callbacks(last_markup(cb_menu))
        check("меню МВД: кнопка архива", "mvd:archive:0" in menu_cbs)
        check("меню МВД: кнопка очереди проверки", "admin:reports_pending" in menu_cbs)

        cb_menu_deny = FakeCallback(pilot, data="mvd:menu")
        await mvdh.mvd_menu(cb_menu_deny)
        check("меню МВД: постороннему отказ, экран не рисуется",
              not texts_of(cb_menu_deny))

        cb_arch = FakeCallback(mod, data="mvd:archive:0")
        await mvdh.mvd_archive_paginate(cb_arch)
        arch_text = "\n".join(texts_of(cb_arch))
        check("архив: заголовок", "АРХИВ ОТЧЁТОВ" in arch_text)
        check("архив: счётчик всех", "Всего: 10" in arch_text)
        arch_cbs = markup_callbacks(last_markup(cb_arch))
        check("архив: кнопки карточек",
              any(str(c).startswith("mvd:arch:") for c in arch_cbs))
        check("архив: переход на 2-ю страницу", "mvd:archive:1" in arch_cbs)

        cb_arch1 = FakeCallback(mod, data="mvd:archive:1")
        await mvdh.mvd_archive_paginate(cb_arch1)
        check("архив: 2-я страница помечена", "Страница 2 из 2" in "\n".join(texts_of(cb_arch1)))

        cb_card = FakeCallback(mod, data=f"mvd:arch:{ids[-1]}:0")
        await mvdh.mvd_archive_card(cb_card)
        check("карточка архива: фото с отчётом", bool(photos_of(cb_card)))
        check("карточка архива: подпись с номером",
              any("Отчёт №" in (c or "") for c in photos_of(cb_card)))
        check("карточка архива: статус виден",
              any("Статус:" in (c or "") for c in photos_of(cb_card)))

        cb_mid = FakeCallback(mod, data=f"mvd:arch:{ids[5]}:0")
        await mvdh.mvd_archive_card(cb_mid)
        mid_nav = {c for c in markup_callbacks(last_markup(cb_mid))
                   if c and c.startswith("mvd:arch:")}
        check("карточка: навигация «новее/старее» по обоим направлениям",
              len(mid_nav) == 2)
        check("карточка: ссылка «К архиву» ведёт на ту же страницу",
              "mvd:archive:0" in markup_callbacks(last_markup(cb_mid)))
        check("карточка: у крайнего (новейшего) отчёта нет «Новее»",
              len({c for c in markup_callbacks(last_markup(cb_card))
                   if c and c.startswith("mvd:arch:")}) == 1)

        # ── 7. «Мои отчёты» ──────────────────────────────────────────────────
        cb_my = FakeCallback(reporter, data="report:my_reports")
        await rep.report_my_reports_redirect(cb_my)
        my_text = "\n".join(texts_of(cb_my))
        check("мои отчёты: заголовок", "Твои отчёты" in my_text)
        check("мои отчёты: 2 страницы при 10 отчётах", "Страница 1 из 2" in my_text)
        my_cbs = markup_callbacks(last_markup(cb_my))
        check("мои отчёты: кнопка карточки",
              any(str(c).startswith("report:view:") for c in my_cbs))
        check("мои отчёты: переход вперёд", "report:my:1" in my_cbs)

        cb_my2 = FakeCallback(reporter, data="report:my:1")
        await rep.report_my_paginate(cb_my2)
        check("мои отчёты: 2-я страница помечена", "Страница 2 из 2" in "\n".join(texts_of(cb_my2)))

        cb_own = FakeCallback(reporter, data=f"report:view:{ids[0]}:0")
        await rep.report_view_card(cb_own)
        check("карточка владельца: фото", bool(photos_of(cb_own)))

        cb_foreign = FakeCallback(pilot, data=f"report:view:{ids[0]}:0")
        await rep.report_view_card(cb_foreign)
        check("чужая карточка недоступна пилоту",
              any("Нет доступа" in (t or "") for t in texts_of(cb_foreign)))

        cb_mvd_card = FakeCallback(mod, data=f"report:view:{ids[0]}:0")
        await rep.report_view_card(cb_mvd_card)
        check("МВД видит карточку пилота", bool(photos_of(cb_mvd_card)))

        # ── 8. индекс reports ────────────────────────────────────────────────
        cur = await conn.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND name='idx_reports_created'")
        check("индекс idx_reports_created создан", (await cur.fetchone()) is not None)
    finally:
        await close_db()

    print(f"\nSmoke 153: {passed} passed, {failed} failed")
    return failed


if __name__ == "__main__":
    sys.exit(1 if asyncio.run(run()) else 0)
