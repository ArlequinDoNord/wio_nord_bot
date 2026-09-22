"""Smoke v0.15.5: командир авиакрыла.

Проверяет:
1. Роль wing_commander с правом can_wing_commands; ROLE_LABELS.
2. БД wing_commanders; add_user_role/remove_user_role; get_wing_commander_by_user.
3. hq:wingcmd — сводка командиров; назначение/снятие меняет крыло и роль пилота.
4. hq:menu открывается командиру по can_wing_commands; меню — «Приказ своему крылу»,
   без «Состава ВВС» и общего «Отправить приказ».
5. Приказ командира: рассылка только своему крылу, подпись «ПРИКАЗ КОМАНДИРА
   <крыло>»; приказ штаба — «ПРИКАЗ ШТАБА ВВС» с подписью главнокомандующего.
6. Отказы: командир без can_manage_wing не входит в hq:wingcmd; пилот без прав.

Запуск: .venv\\Scripts\\python.exe smoke_071.py
"""
import asyncio
import os
import sys
from types import SimpleNamespace

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke071.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB

_ADMIN_ID = 430001
os.environ["ADMIN_IDS"] = str(_ADMIN_ID)

sys.path.insert(0, os.path.dirname(__file__))


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
        if kind == "answer_photo" and kw.get('caption'):
            return kw.get('caption')
    return ""


def markup_callbacks(markup):
    if not markup:
        return []
    return [b.callback_data for row in markup.inline_keyboard for b in row]


def last_reply_markup(msg):
    mark = None
    for kind, a, kw in msg.sent:
        if kind == "answer" and kw.get('reply_markup'):
            mark = kw['reply_markup']
    return mark


async def run():
    from database.db import (
        init_db, close_db, add_user, get_user, set_wing,
        set_wing_commander, get_wing_commander, get_wing_commanders,
        get_wing_commander_by_user, add_user_role, remove_user_role,
    )
    from utils.permissions import ROLES, ROLE_LABELS, has_permission
    from bot.handlers import hq as HQQ

    await init_db()

    admin = _ADMIN_ID
    cmd = 430010   # будущий командир 2 АК
    pilot_a = 430011  # пилот 1 АК
    pilot_b = 430012  # пилот 2 АК
    pilot_c = 430013  # пилот 3 АК
    for uid in (admin, cmd, pilot_a, pilot_b, pilot_c):
        await add_user(uid, "user%d" % uid, "Пилот%d" % uid, "")
    await set_wing(pilot_a, "1")
    await set_wing(pilot_b, "2")
    await set_wing(pilot_c, "3")

    passed = 0
    failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
        else:
            failed += 1
            print(f"  FAIL: {name}")

    # ── 1. Роль и право ──
    check("роль wing_commander с can_wing_commands",
          ROLES['wing_commander'].get('can_wing_commands'))
    check("ROLE_LABELS содержит «Командир авиакрыла»",
          ROLE_LABELS.get('wing_commander') == 'Командир авиакрыла')

    # ── 2. БД ──
    await set_wing_commander("2", cmd)
    await add_user_role(cmd, 'wing_commander', granted_by=admin)
    check("set_wing_commander сохранил командира", await get_wing_commander("2") == cmd)
    check("get_wing_commanders видят крыло 2",
          await get_wing_commanders() == {"2": cmd})
    check("get_wing_commander_by_user находит крыло",
          await get_wing_commander_by_user(cmd) == "2")
    check("командир проходит can_wing_commands",
          await has_permission(cmd, 'can_wing_commands'))
    check("командир не проходит can_send_orders",
          not await has_permission(cmd, 'can_send_orders'))
    check("командир НЕ видит состав ВВС (нет can_manage_wing)",
          not await has_permission(cmd, 'can_manage_wing'))
    await remove_user_role(cmd, 'wing_commander')
    check("remove_user_role снял право",
          not await has_permission(cmd, 'can_wing_commands'))
    await add_user_role(cmd, 'wing_commander', granted_by=admin)  # вернуть

    # ── 3. hq:wingcmd — сводка и доступа ──
    cb_summ = FakeCallback(admin, data="hq:wingcmd", message=FakeMessage(admin))
    await HQQ.hq_wingcmd_cb(cb_summ)
    summ_txt = sent_text(cb_summ.message)
    summ_buttons = markup_callbacks(last_reply_markup(cb_summ.message))
    check("сводка командиров открылась", "КОМАНДИРЫ КРЫЛЬЕВ" in summ_txt)
    check("в сводке есть назначение для всех крыльев",
          all(f"hq:wingcmd:pick:{w}:0" in summ_buttons for w in ("1", "2", "3")))
    check("в сводке есть снятие командира",
          "hq:wingcmd:unset:2" in summ_buttons)

    cb_deny = FakeCallback(pilot_a, data="hq:wingcmd", message=FakeMessage(pilot_a))
    await HQQ.hq_wingcmd_cb(cb_deny)
    check("пилот без can_manage_wing не видит командиров",
          "Нет доступа" in sent_text(cb_deny.message))

    # ── 4. Назначение через кнопку ──
    cb_assign = FakeCallback(admin, data=f"hq:wingcmd:assign:2:{pilot_b}",
                             message=FakeMessage(admin))
    await HQQ.hq_wingcmd_assign(cb_assign)
    check("назначение подтверждено",
          "Командир" in sent_text(cb_assign.message) and "2 АК" in sent_text(cb_assign.message))
    check("командир 2 АК сменился на pilot_b",
          await get_wing_commander("2") == pilot_b)
    check("новый командир получил роль",
          await has_permission(pilot_b, 'can_wing_commands'))
    check("пилоту назначено крыло через командирство",
          (await get_user(pilot_b)).get('wing') == "2")
    check("старый командир потерял роль",
          not await has_permission(cmd, 'can_wing_commands'))

    # Пикер выбора пилота для командира (страница 0).
    cb_pick = FakeCallback(admin, data="hq:wingcmd:pick:1:0", message=FakeMessage(admin))
    await HQQ.hq_wingcmd_pick(cb_pick)
    pk_buttons = markup_callbacks(last_reply_markup(cb_pick.message))
    check("в пикере есть кнопка назначения pilot_a",
          f"hq:wingcmd:assign:1:{pilot_a}" in pk_buttons)
    check("кнопки командира не пересекаются с hq:roster:",
          not any(b.startswith("hq:roster:") for b in pk_buttons))
    check("в пикере есть счётчик страниц", "hq:noop" in pk_buttons)

    # Снятие командира.
    cb_unset = FakeCallback(admin, data="hq:wingcmd:unset:2", message=FakeMessage(admin))
    await HQQ.hq_wingcmd_unset(cb_unset)
    check("снятие подтверждено", "снят" in sent_text(cb_unset.message))
    check("запись удалена", await get_wing_commander("2") is None)
    check("снятый командир потерял роль",
          not await has_permission(pilot_b, 'can_wing_commands'))

    # ── 5. Меню штаба ──
    # Командир: открывается только «Приказ своему крылу».
    cb_hq_cmd = FakeCallback(pilot_b, data="hq:menu", message=FakeMessage(pilot_b))
    st_hq = FakeState()
    # вернём роль командующего 2 АК
    await set_wing_commander("2", pilot_b)
    await add_user_role(pilot_b, 'wing_commander', granted_by=admin)
    await HQQ.hq_menu_cb(cb_hq_cmd, st_hq)
    cmd_buttons = markup_callbacks(last_reply_markup(cb_hq_cmd.message))
    check("командир открыл штаб", "ШТАБ ВВС" in sent_text(cb_hq_cmd.message))
    check("у командира есть «Приказ своему крылу»",
          "hq:wingcmd_send" in cmd_buttons)
    check("у командира НЕТ общего приказа", "hq:send" not in cmd_buttons)
    check("у командира НЕТ состава ВВС", "hq:wing" not in cmd_buttons)

    # Командование: «Отправить приказ» + состав, без приказа своего крыла.
    cb_hq_adm = FakeCallback(admin, data="hq:menu", message=FakeMessage(admin))
    st_adm = FakeState()
    await HQQ.hq_menu_cb(cb_hq_adm, st_adm)
    adm_buttons = markup_callbacks(last_reply_markup(cb_hq_adm.message))
    check("у командования есть «Отправить приказ»", "hq:send" in adm_buttons)
    check("у командования есть «Состав ВВС»", "hq:wing" in adm_buttons)
    check("у командования нет «Приказ своему крылу»",
          "hq:wingcmd_send" not in adm_buttons)

    # Пилот без прав — отказ.
    cb_hq_no = FakeCallback(pilot_c, data="hq:menu", message=FakeMessage(pilot_c))
    await HQQ.hq_menu_cb(cb_hq_no, FakeState())
    check("пилот без прав не входит в штаб",
          "Нет доступа" in sent_text(cb_hq_no.message))

    # ── 6. Приказ командира ──
    send_bot = FakeSender()
    cb_wc = FakeCallback(pilot_b, data="hq:wingcmd_send",
                         message=FakeMessage(pilot_b, bot=send_bot))
    st_wc = FakeState()
    await HQQ.hq_wingcmd_send_cb(cb_wc, st_wc)
    check("запрос текста приказа своему крылу",
          "Приказ для крыла" in sent_text(cb_wc.message) and "2 АК" in sent_text(cb_wc.message))
    check("state сохранил target=2", (await st_wc.get_data()).get('hq_target') == "2")

    msg_cmd = FakeMessage(pilot_b, bot=send_bot, text="Вылет всем в 20:00.")
    await HQQ.hq_order_text(msg_cmd, st_wc)
    cmd_uids = sorted({uid for uid, _ in send_bot.sent})
    check("приказ командира ушёл только своему крылу (pilot_b)",
          cmd_uids == [pilot_b])
    sent_bodies = [t for _, t in send_bot.sent]
    check("подпись «ПРИКАЗ КОМАНДИРА 2 АК»",
          all("ПРИКАЗ КОМАНДИРА" in t and "2 АК" in t for t in sent_bodies))
    check("подпись командира в тексте",
          all("Командир" in t for t in sent_bodies))
    check("подтверждение отправки", "отправлен 1 пилот" in sent_text(msg_cmd))

    # Приказ не уходит другим крыльям.
    check("приказ командира не задел другие крылья",
          all(uid == pilot_b for uid, _ in send_bot.sent))

    # ── 7. Командир не может отправить «всем» ──
    send_bot2 = FakeSender()
    st_wc2 = FakeState(data={"hq_target": "all"})
    await HQQ.hq_order_text(FakeMessage(pilot_b, bot=send_bot2, text="массовая!"), st_wc2)
    check("командир при испорченном target всё равно шлёт своему крылу",
          [uid for uid, _ in send_bot2.sent] == [pilot_b])

    # ── 8. Приказ штаба (командование) всё ещё «ПРИКАЗ ШТАБА ВВС» ──
    send_bot3 = FakeSender()
    st_target3 = FakeState(data={"hq_target": "2"})
    msg_staff = FakeMessage(admin, bot=send_bot3, text="Ждём в штабе.")
    await HQQ.hq_order_text(msg_staff, st_target3)
    check("приказ штаба ушёл пилотам 2 АК",
          sorted({uid for uid, _ in send_bot3.sent}) == [pilot_b])
    check("приказ штаба подписан по-старому",
          all("ПРИКАЗ ШТАБА ВВС" in t for _, t in send_bot3.sent))
    check("приказ штаба подписан главнокомандующим",
          all("Главнокомандующий ВВС" in t for _, t in send_bot3.sent))

    await close_db()
    print(f"\nSmoke 071: {passed} passed, {failed} failed")
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