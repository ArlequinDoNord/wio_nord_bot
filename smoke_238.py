"""Smoke v0.43.25: метка ⚪ неактивных пилотов в Резерве ВВС.

Проверяет:
1. users.last_active попадает в выборки штаба/админки.
2. is_stale_reserve_pilot: >7 суток, last_active=0, граница 7 суток,
   пилот крыла не помечается.
3. Сводка «Состав ВВС» показывает «Резерв: N (⚪ M ...)».
4. Пикер штаба «Взять пилота» и админ-пикер помечают только неактивный
   Резерв и добавляют легенду.

Запуск: .venv\\Scripts\\python.exe smoke_238.py
"""
import asyncio
import os
import sys
import time
from types import SimpleNamespace

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke238.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB

_ADMIN_ID = 438001
os.environ["ADMIN_IDS"] = str(_ADMIN_ID)

sys.path.insert(0, os.path.dirname(__file__))


class FakeMessage:
    def __init__(self, user_id, message_id=100):
        self.from_user = SimpleNamespace(id=user_id)
        self.message_id = message_id
        self.sent = []

    async def answer(self, *a, **kw):
        self.sent.append(("answer", a, kw))

    async def edit_text(self, *a, **kw):
        self.sent.append(("edit_text", a, kw))


class FakeCallback:
    def __init__(self, user_id, data="", message=None):
        self.from_user = SimpleNamespace(id=user_id)
        self.message = message or FakeMessage(user_id)
        self.data = data
        self.alerts = []

    async def answer(self, text=None, *a, **kw):
        self.alerts.append(text)


def sent_text(msg):
    for kind, a, kw in msg.sent:
        if kind in ("answer", "edit_text") and a:
            return a[0]
    return ""


def button_pairs(msg):
    out = []
    for kind, a, kw in msg.sent:
        if kind == "answer" and kw.get("reply_markup"):
            for row in kw["reply_markup"].inline_keyboard:
                out.extend((b.text, b.callback_data) for b in row)
    return out


async def run():
    from config import RESERVE_STALE_DAYS, RESERVE_STALE_ICON
    from database.db import (
        init_db, close_db, add_user, get_db, get_status_by_tag, grant_status,
        get_all_users, get_unassigned_pilots, set_wing,
        is_stale_reserve_pilot,
    )
    from bot.handlers.hq import hq_wing_cb, _pilot_picker
    from bot.handlers.admin import pilot_picker_markup

    await init_db()
    passed = failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
        else:
            failed += 1
            print(f"  FAIL: {name}")

    now = time.time()
    day = 86400
    admin = _ADMIN_ID
    stale = 438010        # 8 суток назад
    fresh = 438011        # 1 сутки назад
    never = 438012        # last_active = 0
    border = 438013       # ровно 7 суток — ещё не помечаем
    in_wing = 438014      # неактивный, но состоит в крыле

    try:
        for uid, name in ((admin, "Штаб"), (stale, "Старый"), (fresh, "Свежий"),
                          (never, "Новичок"), (border, "Граница"), (in_wing, "Крыло")):
            await add_user(uid, f"u{uid}", name, "")
        recruit = await get_status_by_tag("recruit")
        for uid in (admin, stale, fresh, never, border, in_wing):
            await grant_status(uid, recruit["id"], 0)
        await set_wing(in_wing, "2")

        conn = await get_db()
        for uid, last in ((stale, now - 8 * day), (fresh, now - day),
                          (never, 0), (border, now - RESERVE_STALE_DAYS * day + 3600),
                          (in_wing, now - 30 * day), (admin, now)):
            await conn.execute("UPDATE users SET last_active = ? WHERE user_id = ?", (last, uid))
        await conn.commit()

        # 1. last_active в выборках
        all_rows = {u["user_id"]: u for u in await get_all_users()}
        free_rows = {u["user_id"]: u for u in await get_unassigned_pilots()}
        check("get_all_users возвращает last_active",
              all(stale in all_rows and "last_active" in all_rows[stale].keys()
                  for _ in (0,)))
        check("get_unassigned_pilots возвращает last_active",
              "last_active" in free_rows[stale].keys())
        check("not in reserve -> not a stale reserve pilot",
              not is_stale_reserve_pilot(all_rows[in_wing], now=now))
        check("stale > 7 days", is_stale_reserve_pilot(all_rows[stale], now=now))
        check("fresh < 7 days", not is_stale_reserve_pilot(all_rows[fresh], now=now))
        check("last_active=0 is stale", is_stale_reserve_pilot(all_rows[never], now=now))
        check("exactly 7 days is not stale",
              not is_stale_reserve_pilot(all_rows[border], now=now))

        # 3. Сводка штаба
        cb = FakeCallback(admin, data="hq:wing", message=FakeMessage(admin))
        await hq_wing_cb(cb)
        wing_txt = sent_text(cb.message)
        check("сводка: Резерв: 5 (два неактивных)",
              "Резерв: 5" in wing_txt and f"{RESERVE_STALE_ICON} 2" in wing_txt)
        check("сводка: легенда про неделю", "не заходили больше недели" in wing_txt)

        # 4. Пикер штаба (командир берёт из Резерва)
        free = await get_unassigned_pilots(citizens_only=True)
        cb2 = FakeCallback(admin, data="hq:wingtake:0", message=FakeMessage(admin))
        await _pilot_picker(cb2, 0, page_base="hq:wingtake:",
                            assign_prefix="hq:wingtake:do:2",
                            back="hq:menu", caption="Кого взять", users=free)
        pairs = button_pairs(cb2.message)
        picker_caption = sent_text(cb2.message)
        stale_btn = [text for text, data in pairs if data == f"hq:wingtake:do:2:{stale}"]
        fresh_btn = [text for text, data in pairs if data == f"hq:wingtake:do:2:{fresh}"]
        check("пикер штаба: ⚪ у неактивного", bool(stale_btn) and RESERVE_STALE_ICON in stale_btn[0])
        check("пикер штаба: нет ⚪ у активного", bool(fresh_btn) and RESERVE_STALE_ICON not in fresh_btn[0])
        check("пикер штаба: легенда", "больше недели" in picker_caption)

        # 4b. Админ-пикер
        markup = await pilot_picker_markup("wing")
        admin_texts = [b.text for row in markup.inline_keyboard for b in row]
        stale_label = [x for x in admin_texts if "Старый" in x]
        fresh_label = [x for x in admin_texts if "Свежий" in x]
        wing_label_row = [x for x in admin_texts if "Крыло" in x]
        check("админ-пикер: ⚪ у неактивного",
              bool(stale_label) and RESERVE_STALE_ICON in stale_label[0])
        check("админ-пикер: нет ⚪ у активного",
              bool(fresh_label) and RESERVE_STALE_ICON not in fresh_label[0])
        check("админ-пикер: нет ⚪ у пилота крыла",
              bool(wing_label_row) and all(RESERVE_STALE_ICON not in x for x in wing_label_row))
        check("админ-пикер: легенда",
              any("больше недели" in x for x in admin_texts))

        # 5. Оба языка
        from utils.localization import t, use_lang
        use_lang("en")
        check("EN: строка резерва", t("hq.reserve_line", total=5) == "Reserve: 5")
        check("EN: легенда", "over a week" in t("hq.stale_legend", icon=RESERVE_STALE_ICON))
        use_lang("ru")
    finally:
        await close_db()

    print(f"\nSmoke 238: {passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)


asyncio.run(run())
