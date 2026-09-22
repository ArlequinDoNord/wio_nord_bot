"""Smoke v0.15.8: админ-управление находками со дна (водоросли/сапог).

Проверяет:
1. ensure_water_fish сидит water_junk: по 2 записи на водоём с дефолтными шансами
   (водоросли 15%, сапог 2%).
2. update_water_junk правит шанс и фото; повторный сид не перезаписывает правки
   (admin_tuned).
3. _pick_junk(water) берёт шансы из БД по водоёму: 100%/0% — детерминированно.
4. junk_hint показывает актуальные проценты водоёма.
5. Админ-карточка «Находки со дна» (fishing:junk), пикеры полей и ввод
   шанса/фото через состояние (AdminFishing.value).

Запуск: .venv\\Scripts\\python.exe smoke_073.py
"""
import asyncio
import os
import sys
from types import SimpleNamespace

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke073.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB

_ADMIN_ID = 730001
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
        self.photo = None
        self.message = None
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


def last_reply_markup(msg):
    mark = None
    for kind, a, kw in msg.sent:
        if kw.get('reply_markup'):
            mark = kw['reply_markup']
    return mark


def markup_callbacks(markup):
    if not markup:
        return []
    return [b.callback_data for row in markup.inline_keyboard for b in row]


async def run():
    from database.db import (
        init_db, close_db, ensure_life_items, ensure_water_fish,
        get_water_junk_rows, get_water_junk_map, update_water_junk,
    )
    from bot.handlers.fishing import _pick_junk, junk_hint, junk_photo

    await init_db()
    await ensure_life_items()
    await ensure_water_fish()

    passed = 0
    failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
        else:
            failed += 1
            print(f"  FAIL: {name}")

    # ── 1. Сид дефолтов ──
    l_rows = await get_water_junk_rows("lake")
    r_rows = await get_water_junk_rows("reservoir")
    check("озеро: 2 находки", len(l_rows) == 2)
    check("водохранилище: 2 находки", len(r_rows) == 2)
    l_map = await get_water_junk_map("lake")
    check("шансы по умолчанию: водоросли 15%, сапог 2%",
          l_map.get("Кусочек водорослей", {}).get("chance") == 15
          and l_map.get("Старый сапог", {}).get("chance") == 2)
    check("фото пока нет",
          l_map.get("Кусочек водорослей", {}).get("photo_file_id") is None
          and l_map.get("Старый сапог", {}).get("photo_file_id") is None)

    # ── 2. Правка шанса + фото; сид не откатывает ──
    await update_water_junk("lake", "Старый сапог", "chance", 100)
    await update_water_junk("lake", "Кусочек водорослей", "chance", 0)
    await update_water_junk("lake", "Кусочек водорослей", "photo_file_id", "FID_SEAWEED")
    l_map = await get_water_junk_map("lake")
    check("шанс изменён: сапог 100%",
          l_map.get("Старый сапог", {}).get("chance") == 100)
    check("шанс изменён: водоросли 0%",
          l_map.get("Кусочек водорослей", {}).get("chance") == 0)
    check("фото прикреплено",
          l_map.get("Кусочек водорослей", {}).get("photo_file_id") == "FID_SEAWEED")
    # повторный сид не должен сбросить правки админа
    await ensure_water_fish()
    l_map = await get_water_junk_map("lake")
    check("повторный сид не откатывает шанс сапога",
          l_map.get("Старый сапог", {}).get("chance") == 100)
    check("водохранилище не задето правкой озера",
          (await get_water_junk_map("reservoir")).get("Старый сапог", {}).get("chance") == 2)

    # ── 3. _pick_junk по БД, детерминированно ──
    junk_ok = True
    for _ in range(20):
        if await _pick_junk("lake") != "Старый сапог":
            junk_ok = False
            break
    check("сапог 100% → всегда сапог", junk_ok)

    await update_water_junk("lake", "Старый сапог", "chance", 0)
    await update_water_junk("lake", "Кусочек водорослей", "chance", 100)
    junk_ok = True
    for _ in range(20):
        if await _pick_junk("lake") != "Кусочек водорослей":
            junk_ok = False
            break
    check("водоросли 100% → всегда водоросли", junk_ok)

    await update_water_junk("lake", "Кусочек водорослей", "chance", 0)
    check("всё 0% → пусто", await _pick_junk("lake") is None)
    # водохранилище — дефолт, оба шанса ненулевые: проверяем формат результата.
    resv_ok = True
    for _ in range(10):
        if await _pick_junk("reservoir") not in ("Кусочек водорослей", "Старый сапог", None):
            resv_ok = False
            break
    check("reservoir: результат либо находка, либо None", resv_ok)

    # ── 4. Подсказка с актуальными шансами ──
    hint = await junk_hint("lake")
    check("подсказка озера актуальна",
          "(водоросли 0%, сапог 0%)" in hint)
    hint2 = await junk_hint("reservoir")
    check("подсказка водохранилища дефолтна",
          "(водоросли 15%" in hint2 and "сапог 2%" in hint2)
    check("junk_photo отдаёт file_id", await junk_photo("lake", "Кусочек водорослей") == "FID_SEAWEED")

    # ── 5. Админ-карточка находок ──
    from bot.handlers.admin import (
        admin_fishing_junk, admin_fishing_junk_field_pick, admin_fishing_value,
    )
    state = FakeState()
    cb = FakeCallback(_ADMIN_ID, data="fishing:junk:lake",
                      message=FakeMessage(_ADMIN_ID))
    await admin_fishing_junk(cb, state)
    card_txt = sent_text(cb.message)
    card_kb = last_reply_markup(cb.message)
    check("карточка открыта", "НАХОДКИ СО ДНА" in card_txt)
    check("в карточке обе находки с шансами",
          "Кусочек водорослей" in card_txt and "Старый сапог" in card_txt
          and "шанс 0%" in card_txt and "фото: есть" in card_txt)
    cb_list = markup_callbacks(card_kb)
    check("кнопки шанса/фото на каждую находку",
          "fishing_j:chance:lake:Старый сапог" in cb_list
          and "fishing_j:photo:lake:Старый сапог" in cb_list
          and "fishing_j:chance:lake:Кусочек водорослей" in cb_list)
    check("назад к списку рыб", "fishing:water:lake" in cb_list)

    # ── 6. Пикер поля → ввод значения (шанс) ──
    cb_pick = FakeCallback(_ADMIN_ID, data="fishing_j:chance:lake:Старый сапог",
                           message=FakeMessage(_ADMIN_ID))
    await admin_fishing_junk_field_pick(cb_pick, state)
    p_txt = sent_text(cb_pick.message)
    check("запрос шанса", "шанс выпадения в %" in p_txt)
    st_data = await state.get_data()
    check("состояние: jfield/jname/water",
          st_data.get('jfield') == 'chance' and st_data.get('jname') == "Старый сапог"
          and st_data.get('water') == 'lake')

    msg_chance = FakeMessage(_ADMIN_ID, text="8")
    await admin_fishing_value(msg_chance, state)
    check("шанс 8 записан",
          (await get_water_junk_map("lake")).get("Старый сапог", {}).get("chance") == 8)
    check("карточка перерисована после шанса",
          "шанс 8%" in sent_text(msg_chance))

    # ── 7. Ввод фото (+ file_id) и очистка «-» ──
    cb_pick2 = FakeCallback(_ADMIN_ID, data="fishing_j:photo:lake:Старый сапог",
                            message=FakeMessage(_ADMIN_ID))
    await admin_fishing_junk_field_pick(cb_pick2, state)
    p2_txt = sent_text(cb_pick2.message)
    check("запрос фото", "Отправь фото находки" in p2_txt)

    msg_photo = FakeMessage(_ADMIN_ID)
    msg_photo.photo = [SimpleNamespace(file_id="FID_BOOT")]
    await admin_fishing_value(msg_photo, state)
    check("фото сапога записано",
          (await get_water_junk_map("lake")).get("Старый сапог", {}).get("photo_file_id") == "FID_BOOT")

    cb_pick3 = FakeCallback(_ADMIN_ID, data="fishing_j:photo:lake:Старый сапог",
                            message=FakeMessage(_ADMIN_ID))
    await admin_fishing_junk_field_pick(cb_pick3, state)
    msg_clear = FakeMessage(_ADMIN_ID, text="-")
    await admin_fishing_value(msg_clear, state)
    check("минус = фото убрано",
          (await get_water_junk_map("lake")).get("Старый сапог", {}).get("photo_file_id") is None)

    await close_db()
    print(f"\nSmoke 073: {passed} passed, {failed} failed")
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