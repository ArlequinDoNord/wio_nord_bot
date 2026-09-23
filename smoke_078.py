"""Smoke v0.15.16: «Штаб ВВС» и «Доска контрактов» — редактируемые локации города.

Проверяет:
1. Сид: локации hq и contracts созданы (name/access), есть в get_all_locations.
2. city_keyboard: кнопки локаций «🎖️ Штаб ВВС» и «📜 Доска контрактов» (всем),
   жёстких кнопок hq:menu/contracts:list в городе больше нет; Стена и Жильё остались.
3. Превью: строка доступа для штаба (командование) и доски (только пилоты).
4. Вход «Штаб ВВС»: без права — отказ; с правом (модератор) — меню штаба.
5. Вход «Доска контрактов»: туристу — отказ; пилоту — список контрактов.

Запуск: .venv\\Scripts\\python.exe smoke_078.py
"""
import asyncio
import os
import sys
from types import SimpleNamespace

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke078.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB

# Админ-аккаунт не участвует в тестах входа (проверяем именно права роли).
os.environ["ADMIN_IDS"] = str(999999)

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


def markup_callbacks(markup):
    if not markup:
        return []
    return [b.callback_data for row in markup.inline_keyboard for b in row]


def markup_button_texts(markup):
    if not markup:
        return []
    return [b.text for row in markup.inline_keyboard for b in row]


async def run():
    from database.db import (
        init_db, close_db, add_user, get_db, get_location_by_key,
        get_all_locations, get_status_by_tag, grant_status, seed_dungeon,
    )
    from keyboards.keyboards import city_keyboard, cancel_keyboard
    from bot.handlers import locations as LOC

    await init_db()
    await seed_dungeon()

    uid_tourist = 700001
    uid_pilot = 700002
    uid_mod = 700003

    await add_user(uid_tourist, "turi", "Турист", "")
    await add_user(uid_pilot, "pilot", "Пилот", "")
    await add_user(uid_mod, "moder", "Модератор", "")

    pilot_st = await get_status_by_tag("pilot")
    if pilot_st:
        await grant_status(uid_pilot, pilot_st["id"], 0)

    conn = await get_db()
    await conn.execute("INSERT OR IGNORE INTO user_roles (telegram_id, role, granted_by) VALUES (?, 'moderator', ?)",
                       (uid_mod, 999999))
    await conn.commit()

    passed = 0
    failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
        else:
            failed += 1
            print(f"  FAIL: {name}")

    # ── 1. Сид локаций hq / contracts ──
    hq = await get_location_by_key("hq")
    contracts = await get_location_by_key("contracts")
    check("локация hq создана сидом", hq is not None and hq['name'] == "Штаб ВВС")
    check("локация contracts создана сидом",
          contracts is not None and contracts['name'] == "Доска контрактов")
    check("у hq дефолтный preview city/hq", hq and hq.get('preview_photo') == "city/hq")
    check("у contracts дефолтный preview city/contracts",
          contracts and contracts.get('preview_photo') == "city/contracts")
    keys = [l['key'] for l in await get_all_locations()]
    check("get_all_locations содержит hq и contracts", "hq" in keys and "contracts" in keys)

    # ── 2. Клавиатура города ──
    locs = [{"key": "hq", "name": "Штаб ВВС"}, {"key": "contracts", "name": "Доска контрактов"}]
    ck = city_keyboard(is_pilot=True, locations=locs)
    cbs = markup_callbacks(ck)
    texts = markup_button_texts(ck)
    check("кнопка «🎖️ Штаб ВВС» в городе", "location:preview:hq" in cbs
          and any("Штаб ВВС" in t for t in texts))
    check("кнопка «📜 Доска контрактов» в городе", "location:preview:contracts" in cbs
          and any("Доска контрактов" in t for t in texts))
    check("жёстких кнопок hq:menu/contracts:list нет", "hq:menu" not in cbs
          and "contracts:list" not in cbs)
    check("Стена изречений и Жильё остались", "wall:view" in cbs and "housing:menu" in cbs)
    ck_t = city_keyboard(is_pilot=False, locations=locs)
    cbs_t = markup_callbacks(ck_t)
    check("локации видны даже туристу", "location:preview:hq" in cbs_t
          and "location:preview:contracts" in cbs_t
          and "housing:menu" not in cbs_t)

    # ── 3. Превью: строка доступа ──
    cb_prev = FakeCallback(uid_tourist, data="location:preview:hq",
                           message=FakeMessage(uid_tourist))
    await LOC.location_preview(cb_prev)
    check("превью штаба: вход командование",
          "командование ВВС" in sent_text(cb_prev.message))
    cb_prev2 = FakeCallback(uid_tourist, data="location:preview:contracts",
                            message=FakeMessage(uid_tourist))
    await LOC.location_preview(cb_prev2)
    check("превью доски: вход только пилоты",
          "только пилоты" in sent_text(cb_prev2.message))

    # ── 4. Вход в «Штаб ВВС» ──
    cb_no = FakeCallback(uid_pilot, data="location:enter:hq",
                         message=FakeMessage(uid_pilot))
    await LOC.location_enter(cb_no, FakeState())
    check("пилот без права не входит в штаб", "только для командования" in sent_text(cb_no.message))

    cb_mod = FakeCallback(uid_mod, data="location:enter:hq",
                          message=FakeMessage(uid_mod))
    await LOC.location_enter(cb_mod, FakeState())
    check("модератор входит в штаб через локацию", "ШТАБ ВВС" in sent_text(cb_mod.message))

    # ── 5. Вход на «Доску контрактов» ──
    cb_tour = FakeCallback(uid_tourist, data="location:enter:contracts",
                           message=FakeMessage(uid_tourist))
    await LOC.location_enter(cb_tour, FakeState())
    check("турист не входит на доску контрактов",
          "только для пилотов" in sent_text(cb_tour.message))

    cb_pilot = FakeCallback(uid_pilot, data="location:enter:contracts",
                            message=FakeMessage(uid_pilot))
    await LOC.location_enter(cb_pilot, FakeState())
    check("пилот видит доску контрактов",
          "ДОСКА КОНТРАКТОВ" in sent_text(cb_pilot.message))

    await close_db()
    print(f"\nSmoke 078: {passed} passed, {failed} failed")
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