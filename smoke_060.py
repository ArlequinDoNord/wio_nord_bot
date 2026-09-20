"""Smoke v0.13.11: админ-редактор наград — кнопки «✏️ Редактировать» снова
работают.

1) callback «aw_ei:<id>:<field>» парсился в 4 переменные (split(":", 3)) —
   ValueError: not enough values to unpack (expected 4, got 3), кнопка «падала».
   Теперь split(":", 2).
2) карточка награды строилась без импорта InlineKeyboardButton —
   NameError при построении «Продолжить редактировать»; импорт добавлен
   наверх модуля.

Запуск: .venv\\Scripts\\python.exe smoke_060.py
"""
import asyncio
import os
import sys
from types import SimpleNamespace

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke060.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB

sys.path.insert(0, os.path.dirname(__file__))


class FakeMessage:
    def __init__(self, text=""):
        self.sent = []
        self.text = text
        self.message_id = 1
        self.from_user = SimpleNamespace(id=1)
        self.photo = None

    async def answer(self, *a, **kw):
        self.sent.append(("answer", a, kw))

    async def answer_photo(self, *a, **kw):
        self.sent.append(("answer_photo", a, kw))

    async def edit_text(self, *a, **kw):
        self.sent.append(("edit_text", a, kw))

    async def edit_caption(self, *a, **kw):
        self.sent.append(("edit_caption", a, kw))

    async def edit_media(self, *a, **kw):
        self.sent.append(("edit_media", a, kw))


class FakeCallback:
    def __init__(self, user_id, data=""):
        self.from_user = SimpleNamespace(id=user_id)
        self.message = FakeMessage()
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


async def run():
    from database.db import (
        init_db, close_db, seed_default_items,
        create_award, get_all_awards, get_award,
        update_award, add_user,
    )
    from bot.handlers import admin as adm

    await init_db()
    await seed_default_items()

    uid = 999410
    await add_user(uid, "admin", "Админ", "")

    passed = 0
    failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
        else:
            failed += 1
            print(f"  FAIL: {name}")

    # права для хендлеров
    orig_perm = adm.has_permission

    async def _perm(_u, _p):
        return True

    adm.has_permission = _perm
    try:
        ok, aid = await create_award("За отвагу", "Проявил мужество", "🎖️", uid)
        check("награда создана", ok and aid)
        award = await get_award(aid)
        check("награда читается", award is not None and award['name'] == "За отвагу")
        check("картинки нет", not award['image'])

        # ── 1. карточка: меню редактирования строится и содержит кнопки полей ──
        cb = FakeCallback(uid, data=f"aw_edit:{aid}")
        crashed = None
        try:
            await adm.award_edit_open(cb)
        except Exception as e:
            crashed = e
        check("aw_edit: без исключения (NameError был)", crashed is None)
        cbs = []
        if crashed is None:
            for m in cb.message.sent:
                if m[0] in ("edit_text", "edit_media") and m[2] and 'reply_markup' in m[2]:
                    kb = m[2]['reply_markup']
                    cbs = [b.callback_data for row in kb.inline_keyboard for b in row]
        check("aw_edit: кнопка «🖼 Картинка» есть", f"aw_ei:{aid}:image" in cbs)
        check("aw_edit: кнопка бонуса атаки есть", f"aw_ei:{aid}:bonus_attack" in cbs)

        # ── 2. выбор поля: aw_ei:<id>:image не падает (ValueError был) ──
        state = FakeState()
        cb2 = FakeCallback(uid, data=f"aw_ei:{aid}:image")
        crashed2 = None
        try:
            await adm.award_edit_field_pick(cb2, state)
        except Exception as e:
            crashed2 = e
        check("aw_ei: без исключения (unpack был)", crashed2 is None)
        data = state._data
        check("aw_ei: запоминает награду", data.get('edit_award_id') == aid)
        check("aw_ei: запоминает поле", data.get('edit_field') == "image")
        check("aw_ei: просит фото",
              any(m[0] == "answer" and m[1] and "фото" in str(m[1][0])
                  for m in cb2.message.sent))

        # ── 3. ввод значения: «-» убирает картинку (заодно проверка кнопки
        #    «Продолжить редактировать» без NameError) ──
        state2 = FakeState(state=adm.AdminAwards.edit_value.state,
                           data={'edit_award_id': aid, 'edit_field': 'image'})
        msg = FakeMessage(text="-")
        crashed3 = None
        try:
            await adm.award_edit_value(msg, state2)
        except Exception as e:
            crashed3 = e
        check("edit_value: без исключения (NameError был)", crashed3 is None)
        check("edit_value: картинка очищена", not (await get_award(aid))['image'])
        cbs3 = []
        for m in msg.sent:
            if m[0] == "answer" and m[2] and 'reply_markup' in m[2]:
                kb = m[2]['reply_markup']
                cbs3 = [b.callback_data for row in kb.inline_keyboard for b in row]
        check("edit_value: кнопка «Продолжить редактировать»",
              f"aw_edit:{aid}" in cbs3)

        # ── 4. числовой бонус применяется ──
        state3 = FakeState(state=adm.AdminAwards.edit_value.state,
                           data={'edit_award_id': aid, 'edit_field': 'bonus_attack'})
        msg2 = FakeMessage(text="7")
        await adm.award_edit_value(msg2, state3)
        check("edit_value: бонус атаки = 7",
              (await get_award(aid))['bonus_attack'] == 7)
    finally:
        adm.has_permission = orig_perm

    await close_db()
    print(f"\nSmoke 060: {passed} passed, {failed} failed")
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