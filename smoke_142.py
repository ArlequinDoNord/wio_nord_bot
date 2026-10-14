"""Smoke v0.26.0: статистика регионов в штабе ВВС + представитель видит любое формирование.

Проверяет перенос «Статистики регионов» из админ-меню в штаб ВВС и доступ к ней
командиров авиаформирований (can_wing_commands) и представителя/главкома
(can_send_orders), а также новую возможность представителя смотреть статистику
любого формирования — тем же экраном, что командир для своего крыла.

Сценарии:
  1. В админ-панели больше нет кнопки статистики регионов (остались «Отчёты»).
  2. Кнопки HQ-меню показываются по флагам (region_stats_ok / farm_all_ok).
  3. Командир: видит «Статистика регионов», не видит «Статистика формирований».
  4. Представитель/админ: видят и регионы, и статистику формирований.
  5. Посторонний пилот в штаб не входит; экраны ему закрыты.
  6. Экран регионов: текст, обновление пула, возврат в штаб.
  7. Представитель выбирает крыло и видит тот же экран, что командир для своего.

Запуск: .venv\\Scripts\\python.exe smoke_142.py
"""
import asyncio
import os
import sys
import tempfile
from datetime import timedelta, timezone
from types import SimpleNamespace

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

WORK = tempfile.mkdtemp(prefix="sm142_")
os.environ["DATABASE_PATH"] = os.path.join(WORK, "t.db")
_ADMIN_ID = 440001
os.environ["ADMIN_IDS"] = str(_ADMIN_ID)
sys.path.insert(0, os.path.dirname(__file__))

from database import db as D

FAILED = []


def check(name, cond):
    print(("  ok   " if cond else "  FAIL ") + name)
    if not cond:
        FAILED.append(name)


class FakeSender:
    def __init__(self):
        self.sent = []

    async def send_message(self, chat_id, text, **kw):
        self.sent.append((chat_id, text))
        return None


class FakeMessage:
    def __init__(self, user_id, bot=None, text=""):
        self.from_user = SimpleNamespace(id=user_id)
        self.bot = bot or FakeSender()
        self.text = text
        self.sent = []

    async def answer(self, *a, **kw):
        self.sent.append(("answer", a, kw))

    async def edit_text(self, *a, **kw):
        self.sent.append(("edit_text", a, kw))

    async def __getattr__(self, name):
        async def _noop(*a, **kw):
            return None
        return _noop


class FakeCallback:
    def __init__(self, user_id, data="", message=None):
        self.from_user = SimpleNamespace(id=user_id)
        self.message = message or FakeMessage(user_id)
        self.bot = self.message.bot
        self.data = data
        self.alerts = []

    async def answer(self, text=None, *a, **kw):
        self.alerts.append(text)


class FakeState:
    def __init__(self, state=None, data=None):
        self._state = state
        self._data = dict(data or {})

    async def get_state(self):
        return self._state

    async def set_state(self, s):
        self._state = s

    async def get_data(self):
        return dict(self._data)

    async def update_data(self, **kw):
        self._data.update(kw)

    async def clear(self):
        self._data.clear()
        self._state = None


def sent_text(msg):
    for kind, a, kw in msg.sent:
        if kind in ("answer", "edit_text") and a:
            return a[0]
    return ""


def markup_callbacks(markup):
    if not markup:
        return []
    return [b.callback_data for row in markup.inline_keyboard for b in row]


def last_markup(msg):
    mark = None
    for kind, a, kw in msg.sent:
        if kind in ("answer", "edit_text") and kw.get('reply_markup'):
            mark = kw['reply_markup']
    return mark


async def _insert(uid, troops, created_utc, status="approved", region="1"):
    conn = await D.get_db()
    await conn.execute(
        "INSERT INTO reports (user_id, screenshot_file_id, troops_reported, total_troops, "
        "region, credited_troops, status, paid, created_at) "
        "VALUES (?, 'f', ?, ?, ?, ?, ?, 1, ?)",
        (uid, troops, troops, region, troops, status, created_utc)
    )
    await conn.commit()


async def run():
    from database.db import (
        init_db, add_user, set_wing, set_wing_commander, add_user_role,
        recompute_region_stats, report_day_bounds,
    )
    from bot.handlers import hq as HQQ
    from keyboards.keyboards import admin_panel_keyboard

    await init_db()

    admin, cmd, rep, plain = _ADMIN_ID, 440010, 440020, 440030
    # Командир 1 АК и один подчинённый в крыле.
    await add_user(cmd, "cmdr", "Командир", "Тестов")
    await add_user(440011, "wing1", "Пилот", "Первый")
    await add_user(rep, "rep", "Представитель", "Тестов")
    await add_user(plain, "plain", "Гражданский", "Тестов")
    await set_wing(cmd, "1")
    await set_wing(440011, "1")
    await set_wing_commander("1", cmd)
    await add_user_role(cmd, 'wing_commander', granted_by=admin)
    await add_user_role(rep, 'representative', granted_by=admin)

    start, _end = report_day_bounds()
    prev_ts = (start - timedelta(hours=1)).astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    today_ts = (start + timedelta(hours=2)).astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    await _insert(440011, 300, prev_ts, region="1")
    await _insert(440011, 200, today_ts, region="1")
    await recompute_region_stats()

    # ── 1. Админ-панель: статистики регионов больше нет ──
    kb = admin_panel_keyboard({'can_view_reports': True, 'can_approve_reports': True})
    admin_cbs = markup_callbacks(kb)
    check("админ-меню: нет кнопки статистики регионов", "admin:region_stats" not in admin_cbs)
    check("админ-меню: «Отчёты» остались", "admin:reports" in admin_cbs)

    # ── 2. Клавиатура штаба: флаги ──
    m = HQQ.hq_menu_markup(region_stats_ok=True, farm_all_ok=True, wing_farm_ok=True)
    cbs = markup_callbacks(m)
    check("HQ-меню: кнопка регионов при флаге", "hq:region_stats" in cbs)
    check("HQ-меню: кнопка формирований при флаге", "hq:farms" in cbs)
    m0 = HQQ.hq_menu_markup()
    cbs0 = markup_callbacks(m0)
    check("HQ-меню: регионов нет без флага", "hq:region_stats" not in cbs0)
    check("HQ-меню: формирований нет без флага", "hq:farms" not in cbs0)

    # ── 3. Командир в штабе ──
    cb = FakeCallback(cmd, data="hq:menu", message=FakeMessage(cmd))
    await HQQ.hq_menu_cb(cb, FakeState())
    cmd_cbs = markup_callbacks(last_markup(cb.message))
    check("командир видит статистику регионов", "hq:region_stats" in cmd_cbs)
    check("командир НЕ видит статистику всех формирований", "hq:farms" not in cmd_cbs)
    check("командир видит приказ своему крылу", "hq:wingcmd_send" in cmd_cbs)

    # ── 4. Представитель и админ в штабе ──
    cb = FakeCallback(rep, data="hq:menu", message=FakeMessage(rep))
    await HQQ.hq_menu_cb(cb, FakeState())
    rep_cbs = markup_callbacks(last_markup(cb.message))
    check("представитель видит статистику регионов", "hq:region_stats" in rep_cbs)
    check("представитель видит статистику формирований", "hq:farms" in rep_cbs)

    cb = FakeCallback(admin, data="hq:menu", message=FakeMessage(admin))
    await HQQ.hq_menu_cb(cb, FakeState())
    adm_cbs = markup_callbacks(last_markup(cb.message))
    check("админ видит статистику регионов", "hq:region_stats" in adm_cbs)
    check("админ видит статистику формирований", "hq:farms" in adm_cbs)

    # ── 5. Посторонний — отказ в штабе ──
    cb = FakeCallback(plain, data="hq:menu", message=FakeMessage(plain))
    await HQQ.hq_menu_cb(cb, FakeState())
    check("посторонний в штаб не входит", "Нет доступа" in sent_text(cb.message))

    # ── 6. Экран статистики регионов ──
    cb = FakeCallback(cmd, data="hq:region_stats", message=FakeMessage(cmd))
    await HQQ.hq_region_stats_cb(cb)
    txt = sent_text(cb.message)
    reg_cbs = markup_callbacks(last_markup(cb.message))
    check("командир открыл статистику регионов",
          "СТАТИСТИКА ПО РЕГИОНАМ" in txt and "Регион 1" in txt)
    check("экран регионов: кнопка обновления пула", "hq:region_stats_refresh" in reg_cbs)
    check("экран регионов: возврат в штаб", "hq:menu" in reg_cbs)

    cb = FakeCallback(rep, data="hq:region_stats_refresh", message=FakeMessage(rep))
    await HQQ.hq_region_stats_refresh_cb(cb)
    check("обновление пула представителем прошло", "Пул обновлён" in sent_text(cb.message))

    cb = FakeCallback(plain, data="hq:region_stats", message=FakeMessage(plain))
    await HQQ.hq_region_stats_cb(cb)
    check("постороннему статистика регионов закрыта", "Нет доступа" in sent_text(cb.message))

    # ── 7. Статистика формирований у представителя ──
    cb = FakeCallback(rep, data="hq:farms", message=FakeMessage(rep))
    await HQQ.hq_farms_pick_cb(cb)
    pick_cbs = markup_callbacks(last_markup(cb.message))
    check("представитель получил выбор формирований",
          "hq:farms:1:0" in pick_cbs and "hq:menu" in pick_cbs)

    cb = FakeCallback(cmd, data="hq:farms", message=FakeMessage(cmd))
    await HQQ.hq_farms_pick_cb(cb)
    check("командиру выбор всех формирований закрыт", "Нет доступа" in sent_text(cb.message))

    cb = FakeCallback(cmd, data="hq:farms:2:0", message=FakeMessage(cmd))
    await HQQ.hq_farms_view_cb(cb)
    check("командиру статистика чужого крыла закрыта", "Нет доступа" in sent_text(cb.message))

    # Командир о своём крыле vs представитель о том же крыле — один экран.
    cb_cmd = FakeCallback(cmd, data="hq:wingfarm:0", message=FakeMessage(cmd))
    await HQQ.hq_wing_farm_cb(cb_cmd)
    txt_cmd = sent_text(cb_cmd.message)
    cb_rep = FakeCallback(rep, data="hq:farms:1:0", message=FakeMessage(rep))
    await HQQ.hq_farms_view_cb(cb_rep)
    txt_rep = sent_text(cb_rep.message)
    rep_view_cbs = markup_callbacks(last_markup(cb_rep.message))
    check("экран формирования содержит шапку и данные",
          "СОСТАВ БОЕВОГО ФОРМИРОВАНИЯ" in txt_rep and "Пилот" in txt_rep)
    check("представитель видит тот же экран, что командир", txt_cmd == txt_rep)
    check("экран формирования: пагинация + возврат",
          "hq:noop" in rep_view_cbs and "hq:farms" in rep_view_cbs)

    # Несуществующее формирование — экран не рисуется.
    cb_bad = FakeCallback(rep, data="hq:farms:9:0", message=FakeMessage(rep))
    await HQQ.hq_farms_view_cb(cb_bad)
    check("неизвестное формирование — без экрана", sent_text(cb_bad.message) == "")

    from database.db import close_db
    await close_db()
    import shutil
    shutil.rmtree(WORK, ignore_errors=True)
    print("\nSmoke 142: " + ("all passed" if not FAILED else f"{len(FAILED)} failed"))
    sys.exit(1 if FAILED else 0)


if __name__ == "__main__":
    async def _main():
        try:
            return await run()
        finally:
            from database.db import close_db
            await close_db()
            import shutil
            shutil.rmtree(WORK, ignore_errors=True)

    asyncio.run(_main())
