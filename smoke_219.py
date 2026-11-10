# -*- coding: utf-8 -*-
"""Smoke 219 — админ-мастер создания награды: шаг с картинкой и выбор после создания.

1. Шаги: название → описание → эмодзи → картинка → бонусы (10) → превью. Всего 14 шагов.
2. Фото на шаге картинки сохраняется и попадает в превью (фото + «Картинка: есть»).
3. «-» на шаге картинки — награда без картинки; текст вместо фото — повтор вопроса.
4. После создания: картинка сохранена в награде, есть кнопки «Создать ещё одну»
   (aw:create) и «К меню наград» (admin:awards).
"""
import asyncio
import os
import sys
from types import SimpleNamespace

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke219.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB

sys.path.insert(0, os.path.dirname(__file__))


class FakeMessage:
    def __init__(self, text="", photo=None):
        self.sent = []
        self.text = text
        self.photo = photo
        self.from_user = SimpleNamespace(id=1)

    async def answer(self, *a, **kw):
        self.sent.append(("answer", a, kw))

    async def answer_photo(self, *a, **kw):
        self.sent.append(("answer_photo", a, kw))

    async def delete(self):
        pass


class FakeCallback:
    def __init__(self, user_id, data=""):
        self.from_user = SimpleNamespace(id=user_id)
        self.message = FakeMessage()
        self.data = data

    async def answer(self, *a, **kw):
        return True


class FakeState:
    def __init__(self):
        self._state = None
        self._data = {}

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


def _kb_callbacks(kw):
    markup = kw.get("reply_markup")
    if not markup:
        return []
    return [b.callback_data for row in markup.inline_keyboard for b in row]


async def run():
    from database.db import init_db, close_db, add_user, get_award, get_all_awards
    from bot.handlers import admin as adm

    await init_db()
    uid = 999419
    await add_user(uid, "admin", "Админ", "")

    passed = failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
            print(f"  OK  {name}")
        else:
            failed += 1
            print(f"  FAIL: {name}")

    async def _perm(_u, _p):
        return True

    adm.has_permission = _perm
    PHOTO_ID = "AgACAgTESTPHOTO"
    photo_msg = lambda: FakeMessage(photo=[SimpleNamespace(file_id="small"),
                                            SimpleNamespace(file_id=PHOTO_ID)])

    print("\n1. Шаги и картинка")
    st = FakeState()
    msg_cb = FakeCallback(uid, "aw:create")
    await adm.award_create_start(msg_cb, st)
    check("старт: состояние name", st._state == adm.AdminAwards.name.state)

    await adm.award_create_name(FakeMessage(text="Тестовая медаль"), st)
    await adm.award_create_desc(FakeMessage(text="Описание"), st)
    await adm.award_create_emoji(FakeMessage(text="🎖️"), st)
    check("после эмодзи: состояние картинки", st._state == adm.AdminAwards.image.state)

    await adm.award_create_image(photo_msg(), st)
    check("фото сохранено в черновике", st._data.get("image") == PHOTO_ID)
    check("после картинки: состояние бонусов", st._state == adm.AdminAwards.bonus.state)
    check("всего шагов 14", adm._award_bonus_total_steps() == 14)
    check("первый бонус — «Шаг 5 из 14»", "Шаг 5 из 14" in str(await _capture_prompt(adm, st, 0)))

    print("\n2. Бонусы и превью")
    last = None
    for _ in range(len(adm.AWARD_CREATE_BONUS_STEPS)):
        last = FakeMessage(text="0")
        await adm.award_create_bonus(last, st)
    check("после бонусов: превью", st._state == adm.AdminAwards.preview.state)
    check("превью отправлено фото картинки",
          any(kind == "answer_photo" for kind, _a, _kw in last.sent))
    check("в превью «Картинка: есть»",
          any("Картинка: есть" in str(a) for _k, a, _kw in last.sent))

    pv = FakeCallback(uid, "aw_confirm")
    await adm.award_create_confirm(pv, st)
    created = [a for a in (await get_all_awards(include_achievements=False))
               if a["name"] == "Тестовая медаль"]
    check("награда создана", len(created) == 1)
    if created:
        aw = await get_award(created[0]["id"])
        check("картинка сохранена в награде", aw["image"] == PHOTO_ID)
        check("описание сохранено", aw["description"] == "Описание")

    kbs = [kw for kind, a, kw in pv.message.sent if kind == "answer"]
    cbs = _kb_callbacks(kbs[-1]) if kbs else []
    check("после создания: «Создать ещё одну»", "aw:create" in cbs)
    check("после создания: «К меню наград»", "admin:awards" in cbs)

    print("\n3. Без картинки («-») и ввод текста вместо фото")
    st2 = FakeState()
    await adm.award_create_start(FakeCallback(uid, "aw:create"), st2)
    await adm.award_create_name(FakeMessage(text="Без картинки"), st2)
    await adm.award_create_desc(FakeMessage(text="-"), st2)
    await adm.award_create_emoji(FakeMessage(text="-"), st2)
    bad = FakeMessage(text="это не фото")
    await adm.award_create_image(bad, st2)
    check("текст вместо фото — остаёмся на шаге картинки",
          st2._state == adm.AdminAwards.image.state)
    check("текст вместо фото — ответ с подсказкой", bad.sent and "Пришли фото" in bad.sent[0][1][0])
    await adm.award_create_image(FakeMessage(text="-"), st2)
    check("«-» — без картинки, переход к бонусам",
          st2._state == adm.AdminAwards.bonus.state and st2._data.get("image") is None)
    for _ in range(len(adm.AWARD_CREATE_BONUS_STEPS)):
        await adm.award_create_bonus(FakeMessage(text="-"), st2)
    await adm.award_create_confirm(FakeCallback(uid, "aw_confirm"), st2)
    created2 = [a for a in (await get_all_awards(include_achievements=False))
                if a["name"] == "Без картинки"]
    check("награда без картинки создана", len(created2) == 1)
    if created2:
        check("картинки у неё нет", (await get_award(created2[0]["id"]))["image"] in (None, ""))

    await close_db()
    print(f"\nИТОГО: {passed} passed, {failed} failed")
    return failed


async def _capture_prompt(adm, st, idx):
    fm = FakeMessage()
    await adm._award_ask_bonus(fm, st, idx)
    return [a[0] if a else "" for _k, a, _kw in fm.sent]


if __name__ == "__main__":
    sys.exit(1 if asyncio.run(run()) else 0)
