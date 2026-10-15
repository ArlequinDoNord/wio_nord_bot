"""Smoke 145 — клавиатура после создания клана/партии.

После создания объединения бот раньше просто писал «создан!» без кнопок: чтобы
завести ещё одно, приходилось заново проходить весь путь от раздела. Теперь в
ответе есть две кнопки: «Создать ещё один клан / ещё одну партию» (callback
`clans:create:<kind>`) и «Вернуться в раздел партий и кланов» (`city:clans`).

Проверяет:
1. `_after_create_markup("clan")` / `("party")`: две строки — «создать ещё» с
   правильным callback и «вернуться в раздел» → `city:clans`.
2. `_create_clan_finish` возвращает (текст, клавиатуру) и реально создаёт клан
   (с клавиатурой после-создания).
3. Обработчики фото/пропуска передают reply_markup=kb.
4. Кнопка «вернуться» ведёт на существующий обработчик `city:clans`.

Запуск: .venv\\Scripts\\python.exe smoke_145.py
"""
import asyncio
import os
import re
import sys

_TEST_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_test_smoke145.db")
for _suffix in ("", "-wal", "-shm"):
    try:
        os.remove(_TEST_DB + _suffix)
    except OSError:
        pass
os.environ["DATABASE_PATH"] = _TEST_DB
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

PASS, FAIL = 0, 0


def check(name, cond):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  OK  {name}")
    else:
        FAIL += 1
        print(f"FAIL  {name}")


class FakeState:
    def __init__(self, data):
        self._data = data
        self.cleared = False

    async def get_data(self):
        return dict(self._data)

    async def clear(self):
        self.cleared = True
        self._data = {}


def _buttons(markup):
    return [(b.text, b.callback_data) for row in markup.inline_keyboard for b in row]


async def main():
    import config
    config.DB_PATH = _TEST_DB
    import database.db as db
    db.DB_PATH = _TEST_DB
    from database.db import init_db, close_db, add_user, get_clans
    from bot.handlers import clans

    await init_db()
    await add_user(145001, "u1", "U", "1")

    print("\n1. Клавиатура после-создания")
    kb_clan = clans._after_create_markup("clan")
    btns = _buttons(kb_clan)
    texts = [t for t, _ in btns]
    cbs = [c for _, c in btns]
    check("клан: две кнопки", len(btns) == 2)
    check("клан: кнопка «создать ещё один клан»", any("ещё один клан" in t for t in texts))
    check("клан: callback clans:create:clan", "clans:create:clan" in cbs)
    check("клан: кнопка «вернуться в раздел»", any("Вернуться в раздел" in t for t in texts))
    check("клан: callback city:clans", "city:clans" in cbs)

    kb_party = clans._after_create_markup("party")
    btns_p = _buttons(kb_party)
    texts_p = [t for t, _ in btns_p]
    cbs_p = [c for _, c in btns_p]
    check("партия: кнопка «создать ещё одну партию»", any("ещё одну партию" in t for t in texts_p))
    check("партия: callback clans:create:party", "clans:create:party" in cbs_p)
    check("партия: callback city:clans", "city:clans" in cbs_p)

    print("\n2. _create_clan_finish: создаёт клан и отдаёт клавиатуру")
    state = FakeState({"clans_kind": "clan", "clans_name": "Тестовая",
                       "clans_desc": "Описание."})
    text, kb = await clans._create_clan_finish(state, 145001)
    check("возвращает текст и клавиатуру", isinstance(text, str) and kb is not None)
    check("текст сообщает о создании", "создан!" in text and "Тестовая" in text)
    check("FSM очищен", state.cleared)
    check("кнопки после-создания приложены",
          "clans:create:clan" in [c for _, c in _buttons(kb)])
    joined = await get_clans("clan")
    check("клан реально создан",
          any(c["name"] == "Тестовая" and c["created_by"] == 145001 for c in joined))

    print("\n3. Обработчики передают reply_markup")
    path = os.path.join("bot", "handlers", "clans.py")
    src = open(path, encoding="utf-8").read()

    def body(name):
        m = re.search(rf"async def {re.escape(name)}\b.*?(?=\n@router|\nasync def |\ndef )",
                      src, re.DOTALL)
        return m.group(0) if m else ""

    photo = body("clan_create_photo")
    skip = body("clan_create_skip")
    check("фото-обработчик: text/kb и reply_markup=kb",
          "text, kb = await _create_clan_finish" in photo and "reply_markup=kb" in photo)
    check("skip-обработчик: text/kb и reply_markup=kb",
          "text, kb = await _create_clan_finish" in skip and "reply_markup=kb" in skip)
    check("обработчик city:clans существует",
          re.search(r'F\.data == "city:clans"', src) is not None)

    await close_db()
    print(f"\nSmoke 145: {PASS} passed, {FAIL} failed")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except SystemExit:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"SMOKE ERROR: {e}")
        sys.exit(2)
