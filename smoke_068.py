"""Smoke v0.15.0: авиакрылья ВВС.

Проверяет:
1. Колонка users.wing создана миграцией.
2. set_wing / get_user.wing; get_wing_members (по крылу и по всем крыльям).
3. Профиль пилота: строка «Авиакрыло» и правильная метка крыла.
4. Права: can_manage_wing / can_send_orders у super_admin и moderator.
5. Admin-панель: кнопка «🪽 Авиакрылья» по флагу can_manage_wing.
   Мастер выдачи: pickuser → wing; wing_set применяет крыло пилоту.
6. Штаб ВВС: кнопка города по can_send_orders; hq:menu требует право;
   hq:order:all рассылает всем состоящим в крыльях; hq:order:2 — только 2 АК.

Запуск: .venv\\Scripts\\python.exe smoke_068.py
"""
import asyncio
import os
import sys
from types import SimpleNamespace

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke068.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB

# Командование (суперадмин) — проходит все права напрямую.
_CMD_ID = 400001
os.environ["ADMIN_IDS"] = str(_CMD_ID)

sys.path.insert(0, os.path.dirname(__file__))


class FakeSender:
    """Мини-бот: запоминает отправленные личные сообщения (приказы штаба)."""
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
        self.photo = None
        self.sent = []

    async def answer(self, *a, **kw):
        self.sent.append(("answer", a, kw))

    async def edit_text(self, *a, **kw):
        self.sent.append(("edit_text", a, kw))

    async def edit_media(self, *a, **kw):
        self.sent.append(("edit_media", a, kw))

    async def answer_photo(self, *a, **kw):
        self.sent.append(("answer_photo", a, kw))

    async def __getattr__(self, name):
        async def _noop(*a, **kw):
            return None
        return _noop


class FakeCallback:
    def __init__(self, user_id, data="", message=None):
        self.from_user = SimpleNamespace(id=user_id)
        self.message = message or FakeMessage(user_id)
        self.data = data
        self.alerts = []

    async def answer(self, text=None, *a, **kw):
        self.alerts.append(text)


class FakeState:
    def __init__(self, state=None, data=None):
        self._state = state
        self._data = dict(data or {})
        self.cleared = False

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
        self.cleared = True


def sent_text(msg):
    for kind, a, kw in msg.sent:
        if kind == "answer" and a:
            return a[0]
        if kind == "answer_photo" and kw.get('caption'):
            return kw.get('caption')
        if kind == "edit_text" and a:
            return a[0]
    return ""


def last_sent_text(msg):
    text = ""
    for kind, a, kw in msg.sent:
        if kind == "answer" and a:
            text = a[0]
        if kind == "answer_photo" and kw.get('caption'):
            text = kw.get('caption')
    return text


def markup_callbacks(markup):
    if not markup:
        return []
    return [b.callback_data for row in markup.inline_keyboard for b in row]


async def run():
    from database.db import (
        init_db, close_db, add_user, get_user, get_db, set_wing, get_wing_members,
        get_status_by_tag, grant_status,
    )
    from utils.wings import WINGS, wing_label, wing_display
    from utils.permissions import ROLES, has_permission
    from keyboards.keyboards import city_keyboard, admin_panel_keyboard
    from bot.handlers import profile as PF
    from bot.handlers import admin as AM
    from bot.handlers import hq as HQQ

    await init_db()

    uid1 = 400010  # пилот в 1 АК
    uid2 = 400011  # пилот во 2 АК
    uid3 = 400012  # пилот без крыла
    await add_user(uid1, "wolf", "Волк", "")
    await add_user(uid2, "owl", "Сова", "")
    await add_user(uid3, "anon", "Анон", "")

    passed = 0
    failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
        else:
            failed += 1
            print(f"  FAIL: {name}")

    # ── 1. Колонка users.wing ──
    conn = await get_db()
    cur = await conn.execute("PRAGMA table_info(users)")
    cols = [r['name'] for r in await cur.fetchall()]
    check("колонка users.wing создана", "wing" in cols)

    # ── 2. set_wing / get_user.wing / get_wing_members ──
    check("изначально wing = None", (await get_user(uid1)).get('wing') is None)
    await set_wing(uid1, "1")
    await set_wing(uid2, "2")
    check("set_wing(uid1, '1') сохранён", (await get_user(uid1)).get('wing') == "1")
    check("set_wing(uid2, '2') сохранён", (await get_user(uid2)).get('wing') == "2")
    check("пилот без крыла остаётся None", (await get_user(uid3)).get('wing') is None)
    check("get_wing_members('1') = [uid1]",
          set(await get_wing_members("1")) == {uid1})
    check("get_wing_members('2') = [uid2]",
          set(await get_wing_members("2")) == {uid2})
    check("get_wing_members() (все крылья) = [uid1, uid2]",
          set(await get_wing_members()) == {uid1, uid2})
    await set_wing(uid1, None)
    check("set_wing(uid1, None) снимает крыло",
          (await get_user(uid1)).get('wing') is None)
    await set_wing(uid1, "1")  # вернуть для дальше

    # ── 3. Профиль: строка «Авиакрыло» ──
    pilot_st = await get_status_by_tag("pilot")
    if pilot_st:
        await grant_status(uid2, pilot_st["id"], 0)
        await grant_status(uid3, pilot_st["id"], 0)
    cap, _ = await PF._profile_caption(uid2, owner=True)
    check("в профиле есть строка «Авиакрыло»", cap is not None and "Авиакрыло" in cap)
    check("в профиле метка крыла 2 АК", cap is not None and "Полярные Совы" in cap)
    cap3, _ = await PF._profile_caption(uid3, owner=True)
    check("у пилота без крыла строка «— не назначено»",
          cap3 is not None and "не назначено" in cap3)
    check("метки крыльев: 4 штуки и полные названия",
          wing_label("1") == "🐺 1 АК «Небесные Волки»"
          and wing_label("2") == "🦉 2 АК «Полярные Совы»"
          and wing_label("3") == "🌑 3 АК «Тени Нордхама»"
          and wing_label("4") == "❄️ 4 СО «Буран» (спец отряд)"
          and wing_display(None) == "— не назначено"
          and set(WINGS.keys()) == {"1", "2", "3", "4"})

    # ── 4. Права ──
    check("super_admin: can_manage_wing", ROLES['super_admin'].get('can_manage_wing'))
    check("super_admin: can_send_orders", ROLES['super_admin'].get('can_send_orders'))
    check("moderator: can_manage_wing", ROLES['moderator'].get('can_manage_wing'))
    check("moderator: can_send_orders", ROLES['moderator'].get('can_send_orders'))
    check("суперадмин (ADMIN_IDS) проходит can_send_orders",
          await has_permission(_CMD_ID, 'can_send_orders'))
    await conn.execute(
        "INSERT INTO user_roles (telegram_id, role, granted_by) VALUES (?, 'moderator', ?)",
        (uid3, _CMD_ID))
    await conn.commit()
    check("moderator проходит can_manage_wing и can_send_orders",
          await has_permission(uid3, 'can_manage_wing')
          and await has_permission(uid3, 'can_send_orders'))
    check("обычный пилот НЕ проходит can_send_orders",
          not await has_permission(uid1, 'can_send_orders'))

    # ── 5. Админ-панель + мастер выдачи ──
    kb = admin_panel_keyboard({'can_manage_wing': True})
    cbs = markup_callbacks(kb)
    check("в админ-панели кнопка «Авиакрылья»",
          "admin:wing" in cbs)
    kb_no = admin_panel_keyboard({})
    check("без can_manage_wing кнопки авиакрылий нет",
          "admin:wing" not in markup_callbacks(kb_no))

    st = FakeState(data={"target_id": uid2, "target_name": "Сова"})
    cb = FakeCallback(_CMD_ID, data=f"pickuser:wing:{uid2}", message=FakeMessage(_CMD_ID))
    await AM.pickuser_cb(cb, st)
    wing_menu_text = last_sent_text(cb.message)
    last_markup = None
    for kind, a, kw in cb.message.sent:
        if kw.get('reply_markup'):
            last_markup = kw['reply_markup']
    check("после выбора пилота открылось меню крыльев",
          "Установка авиакрыла" in wing_menu_text)
    check("в меню крыльев все 3 крыла + снятие",
          {"wing_set:1", "wing_set:2", "wing_set:3", "wing_set:none"}
          .issubset(set(markup_callbacks(last_markup))))

    st2 = FakeState(data={"target_id": uid2, "target_name": "Сова"})
    cb2 = FakeCallback(_CMD_ID, data="wing_set:2", message=FakeMessage(_CMD_ID))
    await AM.admin_wing_set_cb(cb2, st2)
    check("wing_set:2 назначил крыло 2 пилоту uid2",
          (await get_user(uid2)).get('wing') == "2")
    check("после назначения — подтверждение",
          "Авиакрыло" in sent_text(cb2.message) or "авиакрыло" in sent_text(cb2.message))

    await conn.execute("DELETE FROM user_roles WHERE telegram_id = ?", (uid3,))
    await conn.commit()

    # ── 6. Штаб ВВС ──
    ck = city_keyboard(is_pilot=False, locations=[], can_send_orders=True)
    check("в городе кнопка «Штаб ВВС» у командования",
          "hq:menu" in markup_callbacks(ck))
    ck_no = city_keyboard(is_pilot=False, locations=[], can_send_orders=False)
    check("без can_send_orders кнопки штаба нет",
          "hq:menu" not in markup_callbacks(ck_no))

    # Вход в штаб без права — отказ.
    st_no = FakeState()
    cb_no = FakeCallback(uid1, data="hq:menu", message=FakeMessage(uid1))
    await HQQ.hq_menu_cb(cb_no, st_no)
    check("пилот без права не входит в штаб",
          "Нет доступа" in sent_text(cb_no.message))

    # Командование входит в штаб, выбирает «Всем авиакрыльям».
    send_bot = FakeSender()
    st_hq = FakeState()
    cb_hq = FakeCallback(_CMD_ID, data="hq:menu", message=FakeMessage(_CMD_ID, bot=send_bot))
    await HQQ.hq_menu_cb(cb_hq, st_hq)
    check("командование открыло штаб", "ШТАБ ВВС" in sent_text(cb_hq.message))

    cb_target = FakeCallback(_CMD_ID, data="hq:order:all", message=FakeMessage(_CMD_ID, bot=send_bot))
    st_target = FakeState()
    await HQQ.hq_order_start(cb_target, st_target)
    tx = sent_text(cb_target.message)
    check("запрос текста приказа для всех крыльев",
          "Введи текст приказа" in tx and "все авиакрылья" in tx)

    msg_all = FakeMessage(_CMD_ID, bot=send_bot, text="Всем на взлёт!")
    await HQQ.hq_order_text(msg_all, st_target)
    sent_uids = sorted({uid for uid, _ in send_bot.sent})
    check("приказ «всем» ушёл пилотам крыльев (uid1, uid2)",
          set(sent_uids) == {uid1, uid2})
    check("приказ «всем» не ушёл пилоту без крыла", uid3 not in sent_uids)
    check("текст приказа содержит заголовок штаба",
          all("ПРИКАЗ ШТАБА ВВС" in t for _, t in send_bot.sent))
    check("подтверждение с количеством адресатов",
          "отправлен 2 пилота" in sent_text(msg_all))

    # Приказ конкретному крылу (2 АК).
    send_bot2 = FakeSender()
    st_target2 = FakeState(data={})
    cb_w2 = FakeCallback(_CMD_ID, data="hq:order:2", message=FakeMessage(_CMD_ID, bot=send_bot2))
    await HQQ.hq_order_start(cb_w2, st_target2)
    msg_w2 = FakeMessage(_CMD_ID, bot=send_bot2, text="Вылет в 18:00.")
    await HQQ.hq_order_text(msg_w2, st_target2)
    check("приказ 2 АК ушёл только uid2",
          [uid for uid, _ in send_bot2.sent] == [uid2])
    check("подтверждение «1 пилоту»",
          "отправлен 1 пилот" in sent_text(msg_w2))

    await close_db()
    print(f"\nSmoke 068: {passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    try:
        asyncio.run(run())
    except SystemExit:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        from database.db import close_db
        asyncio.run(close_db())
        print(f"SMOKE ERROR: {e!r}")
        sys.exit(1)