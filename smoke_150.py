"""Smoke v0.32.1: НИИ — до 2 скриншотов в обращении.

Проверяет:
1. БД: add_nii_report сохраняет оба фото; 1 фото → photo2_file_id пусто.
2. FSM-поток: текст → 1-е фото (подсказка «1/2») → 2-е фото → обращение принято.
3. Пропуск фото (кнопка «Без фото») → обращение без картинок.
4. Просмотр Хранителем: два фото → две отправки answer_photo; без фото → текст.

Запуск: .venv\\Scripts\\python.exe smoke_150.py
"""
import asyncio
import os
import sys
from types import SimpleNamespace

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke150.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB

sys.path.insert(0, os.path.dirname(__file__))


class Sender:
    async def send_message(self, *a, **kw):
        return SimpleNamespace(message_id=1)

    async def send_photo(self, *a, **kw):
        return SimpleNamespace(message_id=1)

    async def edit_message_text(self, *a, **kw):
        return SimpleNamespace(message_id=1)

    async def edit_message_media(self, *a, **kw):
        return SimpleNamespace(message_id=1)

    async def delete_message(self, *a, **kw):
        return None


class Msg:
    def __init__(self, uid, text=None, photo=None, bot=None):
        self.from_user = SimpleNamespace(id=uid)
        self.chat = SimpleNamespace(id=uid)
        self.message_id = 1
        self.bot = bot or Sender()
        self.text = text
        self.photo = photo
        self.captured = []
        self.photo_calls = []

    async def answer(self, text=None, *a, **kw):
        self.captured.append(text or "")
        return SimpleNamespace(message_id=len(self.captured))

    async def answer_photo(self, photo=None, caption=None, *a, **kw):
        self.photo_calls.append(photo)
        self.captured.append(caption or "")
        return SimpleNamespace(message_id=len(self.captured))

    async def __getattr__(self, name):
        async def _noop(*a, **kw):
            return None
        return _noop


class Callback:
    def __init__(self, uid, data="", message=None, bot=None):
        self.from_user = SimpleNamespace(id=uid)
        self.bot = bot or Sender()
        self.message = message or Msg(uid, bot=self.bot)
        self.data = data

    async def answer(self, *a, **kw):
        return None


class FakeState:
    def __init__(self):
        self.data = {}
        self.state = None

    async def get_data(self):
        return dict(self.data)

    async def update_data(self, **kw):
        self.data.update(kw)

    async def set_state(self, s):
        self.state = s

    async def clear(self):
        self.data = {}
        self.state = None


async def run():
    from database.db import (
        init_db, close_db, add_user, add_nii_report, get_nii_report,
        get_my_nii_reports,
    )
    from bot.handlers import nii

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

    # ── 1. БД: оба фото сохраняются ──
    uid = 492000
    await add_user(uid, "smoke150", "Смоук", "")
    rid = await add_nii_report(uid, "текст", "ph1", "ph2")
    row = await get_nii_report(rid)
    check("БД: первое фото сохранено", row["photo_file_id"] == "ph1")
    check("БД: второе фото сохранено", row["photo2_file_id"] == "ph2")

    rid_one = await add_nii_report(uid, "текст2", "phOnly", None)
    row_one = await get_nii_report(rid_one)
    check("БД: 1 фото → первое есть", row_one["photo_file_id"] == "phOnly")
    check("БД: 1 фото → второго нет", not row_one["photo2_file_id"])

    # ── 2. FSM-поток: текст → 1-е фото → 2-е фото ──
    uid_flow = 492050
    await add_user(uid_flow, "smoke150flow", "Смоук-Флоу", "")
    state = FakeState()
    msg = Msg(uid_flow, text="текст обращения")
    await nii.nii_write_text(msg, state)
    check("FSM: после текста фото пусто", state.data.get("photos") == [])
    check("FSM: подсказка про фото", any("Без фото" in c for c in msg.captured))

    msg1 = Msg(uid_flow, photo=[SimpleNamespace(file_id="phA")])
    await nii.nii_write_photo(msg1, state, Sender())
    check("FSM: 1-е фото сохранено", state.data.get("photos") == ["phA"])
    check("FSM: подсказка «1/2»", any("1/2" in c for c in msg1.captured))

    msg2 = Msg(uid_flow, photo=[SimpleNamespace(file_id="phB")])
    await nii.nii_write_photo(msg2, state, Sender())
    check("FSM: обращение принято", any("принято" in c for c in msg2.captured))

    my = await get_my_nii_reports(uid_flow)
    check("FSM: оба фото в БД",
          my and my[0]["photo_file_id"] == "phA" and my[0]["photo2_file_id"] == "phB")

    # ── 3. Пропуск фото («Без фото») ──
    uid_skip = 492100
    await add_user(uid_skip, "smoke150skip", "Смоук-Скип", "")
    s2 = FakeState()
    await nii.nii_write_text(Msg(uid_skip, text="без фото"), s2)
    cb = Callback(uid_skip, data="nii:no_photo", message=Msg(uid_skip))
    await nii.nii_photo_skip(cb, s2, Sender())
    my2 = await get_my_nii_reports(uid_skip)
    check("Пропуск: обращение без картинок",
          my2 and not my2[0]["photo_file_id"] and not my2[0]["photo2_file_id"])

    # ── 4. Просмотр: два фото → две отправки; без фото → текст ──
    async def _always_true(_uid):
        return True
    nii._nii_can_view_all = _always_true

    view_msg = Msg(uid)
    await nii.nii_view_report(Callback(uid, data=f"nii:view:{rid}", message=view_msg))
    check("Просмотр: отправлены оба фото", view_msg.photo_calls == ["ph1", "ph2"])

    rid_none = await add_nii_report(uid, "без картинок", None, None)
    view_msg2 = Msg(uid)
    await nii.nii_view_report(Callback(uid, data=f"nii:view:{rid_none}", message=view_msg2))
    check("Просмотр: без фото — нет answer_photo", view_msg2.photo_calls == [])
    check("Просмотр: без фото — отправлен текст", any(c for c in view_msg2.captured))

    await close_db()
    print(f"\nSmoke 150: {passed} passed, {failed} failed")
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
