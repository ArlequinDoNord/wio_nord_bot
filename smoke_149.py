"""Smoke v0.32.1: открытые локации — без лишней подписи «Доступ: 🌐 Всем».

Проверяет:
1. Чистую логику `location_access_label` (all/пусто → «🌐 Всем», min/exact — своё).
2. Превью открытой локации (Ратуша) — в тексте НЕТ строки «Доступ:».
3. Превью закрытой локации (Железная копь, min/pilot1) — строка доступа есть.
4. Локации со своим правилом (Штаб ВВС, LOCATION_ACCESS_LINES) — строка доступа есть.

Запуск: .venv\\Scripts\\python.exe smoke_149.py
"""
import asyncio
import os
import sys
from types import SimpleNamespace

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke149.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB

sys.path.insert(0, os.path.dirname(__file__))


class Sender:
    def __init__(self):
        self.sent = []

    async def send_message(self, *a, **kw):
        return SimpleNamespace(message_id=1)

    async def send_photo(self, *a, **kw):
        return SimpleNamespace(message_id=1)

    async def edit_message_text(self, *a, **kw):
        return SimpleNamespace(message_id=1)

    async def edit_message_media(self, *a, **kw):
        return SimpleNamespace(message_id=1)

    async def edit_message_reply_markup(self, *a, **kw):
        return None

    async def delete_message(self, *a, **kw):
        return None


class Msg:
    """Ловим и текст (answer), и подпись фото (answer_photo)."""

    def __init__(self, uid, bot=None):
        self.from_user = SimpleNamespace(id=uid)
        self.chat = SimpleNamespace(id=uid)
        self.message_id = 1
        self.bot = bot or Sender()
        self.captured = []

    async def answer(self, text=None, *a, **kw):
        self.captured.append(text or "")
        return SimpleNamespace(message_id=len(self.captured))

    async def answer_photo(self, photo=None, caption=None, *a, **kw):
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
        self.message = message or Msg(uid, self.bot)
        self.data = data

    async def answer(self, *a, **kw):
        return None


async def run():
    from database.db import (
        init_db, close_db, add_user, get_location_by_key, location_access_label,
    )
    from bot.handlers import locations as loc
    from bot.handlers.locations import LOCATION_ACCESS_LINES

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

    async def preview_text(uid, key):
        msg = Msg(uid)
        cb = Callback(uid, data=f"location:preview:{key}", message=msg)
        await loc.location_preview(cb)
        return "\n".join(msg.captured)

    # ── 1. Чистая логика ──
    check("all → 🌐 Всем", await location_access_label("all", None) == "🌐 Всем")
    check("пусто → 🌐 Всем", await location_access_label("", None) == "🌐 Всем")
    check("min → 📈 X и выше",
          await location_access_label("min", "pilot1") == "📈 pilot1 и выше")
    check("exact → 🎯 Только: X",
          await location_access_label("exact", "Хранитель") == "🎯 Только: Хранитель")

    uid = 491000
    await add_user(uid, "smoke149", "Смоук", "")

    # ── 2. Открытая локация — без подписи доступа ──
    town = await get_location_by_key("townhall")
    check("Ратуша — режим all", town and town["access_mode"] == "all")
    txt = await preview_text(uid, "townhall")
    check("превью Ратуши: «Доступ:» отсутствует", "Доступ:" not in txt)
    check("превью Ратуши: нет «🌐 Всем»", "🌐 Всем" not in txt)
    check("превью Ратуши: имя локации на месте", "Ратуша" in txt)

    # ── 3. Закрытая локация со «стандартным» правилом — подпись есть ──
    # В сиде все min-локации имеют свою строку в LOCATION_ACCESS_LINES, поэтому
    # заводим временную локацию с режимом min, чтобы проверить общую ветку.
    from database.db import get_db, get_location_by_key as get_loc
    conn = await get_db()
    await conn.execute(
        "INSERT INTO locations (key, name, description, access_mode, required_status, "
        "blocking_states, preview_photo) VALUES ('smoke_min', 'Тест-мин', 'тест', "
        "'min', 'pilot1', '[]', NULL)")
    await conn.commit()
    try:
        txt = await preview_text(uid, "smoke_min")
        check("превью min-локации: строка «Доступ: 📈 pilot1 и выше»",
              "Доступ: 📈 pilot1 и выше" in txt)
    finally:
        await conn.execute("DELETE FROM locations WHERE key = 'smoke_min'")
        await conn.commit()

    # Копь использует свою строку из LOCATION_ACCESS_LINES
    mine = await get_location_by_key("mine")
    check("Копь — режим min/pilot1",
          mine and mine["access_mode"] == "min" and mine["required_status"] == "pilot1")
    txt = await preview_text(uid, "mine")
    check("превью Копи: своя строка доступа",
          LOCATION_ACCESS_LINES["mine"] in txt)

    # ── 4. Локации со своим правилом — строка доступа есть ──
    hq = await get_location_by_key("hq")
    check("Штаб ВВС в LOCATION_ACCESS_LINES", "hq" in LOCATION_ACCESS_LINES)
    txt = await preview_text(uid, "hq")
    check("превью Штаба: своя строка доступа",
          LOCATION_ACCESS_LINES["hq"] in txt)

    await close_db()
    print(f"\nSmoke 149: {passed} passed, {failed} failed")
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
