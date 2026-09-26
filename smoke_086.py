"""Smoke v0.15.27: фикс отправки обращения в НИИ без фото.

Кнопка «Без фото» (callback `nii:no_photo`) передавала в _nii_finish объект
`callback.message`, а внутри текст обращения привязывался через
`message.from_user.id` — для callback-кнопки это ID бота, а не игрока.
Обращение сохранялось под ботом и не попадало в «Мои обращения» игрока.
Теперь user_id передаётся явно от смысла действия.

Запуск: .venv\\Scripts\\python.exe smoke_086.py
"""
import asyncio
import os
import sys
from types import SimpleNamespace

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke086.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB
os.environ["ADMIN_IDS"] = ""

sys.path.insert(0, os.path.dirname(__file__))


async def run():
    from database.db import (
        init_db, close_db, add_user, get_my_nii_reports, count_nii_reports_today, get_db,
    )
    from bot.handlers.nii import _nii_finish

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

    uid = 36001
    await add_user(uid, "t36001", "Т36001", "")

    # ── 1. _nii_finish через «Без фото» (callback.message, from_user = бот) ──
    answers = []

    async def fake_answer(text, *a, **kw):
        answers.append(text)

    message = SimpleNamespace(
        from_user=None,  # в aiogram для callback.message.from_user = бот, а не игрок
        chat=SimpleNamespace(id=uid),
        answer=fake_answer,
    )

    class FakeState:
        def __init__(self):
            self.data = {"text": "Просьба вернуть кнопку без фото"}

        async def get_data(self):
            return dict(self.data)

        async def clear(self):
            self.data = {}

    class FakeBot:
        async def send_message(self, *a, **kw):
            return None

    await _nii_finish(uid, message, FakeState(), FakeBot(), photo_file_id=None)

    check("player: есть подтверждение (принято)", any("принято" in a for a in answers))
    mine = await get_my_nii_reports(uid)
    check("обращение видно в «Мои обращения»", len(mine) == 1
          and mine[0]['text'] == "Просьба вернуть кнопку без фото")
    check("счётчик суток игрока = 1", await count_nii_reports_today(uid) == 1)

    conn = await get_db()
    cur = await conn.execute("SELECT user_id, text FROM nii_reports ORDER BY id")
    rows = await cur.fetchall()
    check("в БД user_id = игрок (не бот)", rows and rows[0]['user_id'] == uid)
    check("в БД ровно одна запись", len(rows) == 1)

    # ── 4. Разводка ──
    def source_has(path, needle):
        with open(path, "r", encoding="utf-8") as f:
            return needle in f.read()

    root = os.path.dirname(__file__)
    nii = os.path.join(root, "bot", "handlers", "nii.py")
    check("nii.py: user_id от callback.from_user.id", source_has(
        nii, "_nii_finish(callback.from_user.id, callback.message, state, bot"))
    check("nii.py: подпись _nii_finish(user_id, ...)", source_has(
        nii, "async def _nii_finish(user_id: int, message, state: FSMContext, bot: Bot, photo_file_id):"))
    check("nii.py: нет старого message.from_user.id", not source_has(
        nii, "user_id = message.from_user.id"))

    await close_db()
    print(f"\nSmoke 086: {passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    try:
        asyncio.run(run())
    except SystemExit:
        raise
    except Exception as e:
        from database.db import close_db
        asyncio.run(close_db())
        print(f"SMOKE ERROR: {e!r}")
        sys.exit(1)