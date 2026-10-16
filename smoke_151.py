"""Smoke v0.32.1: админ-награды — разделены «Награды» и «Достижения».

Проблема: список наград включал десятки строк-уровней достижений, вывод
раздувался и `edit_text` падал на лимите Telegram (4096) — «список не
открывался». Теперь:
  * `get_all_awards(include_achievements=False)` — только ручные награды;
  * `get_achievement_awards()` — только строки ачивок;
  * меню `admin:awards` содержит кнопки `aw:list` и `aw:ach`;
  * выдача (`aw:grant`) после выбора пилота предлагает `aw_kind:reg/ach`.

Запуск: .venv\\Scripts\\python.exe smoke_151.py
"""
import asyncio
import os
import sys

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke151.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB

sys.path.insert(0, os.path.dirname(__file__))


class FakeMessage:
    def __init__(self, text=""):
        self.text = text
        self.sent = []

    async def answer(self, text=None, *a, **kw):
        self.sent.append(("answer", text, kw))

    async def edit_text(self, text=None, *a, **kw):
        self.sent.append(("edit_text", text, kw))


class FakeCallback:
    def __init__(self, user_id, data=""):
        self.from_user = type("U", (), {"id": user_id})()
        self.message = FakeMessage()
        self.data = data

    async def answer(self, *a, **kw):
        pass


class FakeState:
    def __init__(self, data=None):
        self._data = dict(data or {})

    async def get_data(self):
        return dict(self._data)

    async def update_data(self, **kw):
        self._data.update(kw)

    async def set_state(self, s):
        pass


def _buttons(msg):
    cbs = []
    for m in msg.sent:
        km = m[2].get("reply_markup") if m[2] else None
        if km is not None:
            cbs += [b.callback_data for row in km.inline_keyboard for b in row]
    return cbs


def _last_text(msg):
    for m in reversed(msg.sent):
        if m[1]:
            return m[1]
    return ""


async def run():
    from database.db import (
        init_db, close_db, add_user, create_award, ensure_achievements,
        get_all_awards, get_achievement_awards, ACHIEVEMENTS_DEF,
    )
    from bot.handlers import admin as adm

    await init_db()

    uid = 999151
    await add_user(uid, "admin151", "Админ", "")

    passed = 0
    failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
        else:
            failed += 1
            print(f"  FAIL: {name}")

    async def _perm(*a, **kw):
        return True

    adm.has_permission = _perm

    try:
        ok, reg_id = await create_award("Медаль Тест", "За тест", "🎖", uid)
        check("ручная награда создана", ok and reg_id)
        await ensure_achievements()

        regular = await get_all_awards(include_achievements=False)
        all_awards = await get_all_awards()
        ach = await get_achievement_awards()

        check("regular содержит ручную награду",
              any(a['id'] == reg_id for a in regular))
        check("regular без строк ачивок",
              all(a['achievement_key'] is None for a in regular))
        check("ach только строки ачивок",
              len(ach) > 0 and all(a['achievement_key'] for a in ach))
        check("ачивок больше, чем ручных", len(ach) > len(regular))
        check("default включает всё (совместимость)",
              len(all_awards) == len(regular) + len(ach))

        # ── меню разделов ──
        cb = FakeCallback(uid, "admin:awards")
        await adm.admin_awards(cb)
        cbs = _buttons(cb.message)
        check("меню: кнопка «Награды» (aw:list)", "aw:list" in cbs)
        check("меню: кнопка «Достижения» (aw:ach)", "aw:ach" in cbs)

        # ── список наград не раздувается достижениями ──
        cb2 = FakeCallback(uid, "aw:list")
        await adm.awards_list(cb2)
        txt = _last_text(cb2.message)
        check("aw:list: уложились в лимит Telegram", len(txt) <= 4096)
        check("aw:list: ручная награда показана", "Медаль Тест" in txt)
        ach_names = {lvl["name"] for s in ACHIEVEMENTS_DEF.values()
                     for lvl in s["levels"]}
        check("aw:list: без имён ачивок",
              not (set(txt.split("\n")) & {n for n in ach_names}))
        check("aw:list: кнопка назад к наградам",
              "admin:awards" in _buttons(cb2.message))

        # ── список достижений строится и укладывается в лимит ──
        cb3 = FakeCallback(uid, "aw:ach")
        await adm.achievements_list(cb3)
        txt3 = _last_text(cb3.message)
        check("aw:ach: заголовок", "ДОСТИЖЕНИЯ" in txt3)
        check("aw:ach: уложились в лимит Telegram", len(txt3) <= 4096)
        check("aw:ach: есть кнопка назад к наградам",
              "admin:awards" in _buttons(cb3.message))

        # ── выбор «награда / достижение» при выдаче ──
        st = FakeState({"target_id": uid})
        cbg = FakeCallback(uid, "aw_kind:reg")
        await adm.award_grant_kind(cbg, st)
        cbs_reg = _buttons(cbg.message)
        check("aw_kind:reg: список ручных наград",
              f"aw_pick:{reg_id}" in cbs_reg)

        check("aw_kind:reg: без имён ачивок в тексте",
              not any(n in _last_text(cbg.message) for n in ach_names))

        cba = FakeCallback(uid, "aw_kind:ach")
        await adm.award_grant_kind(cba, st)
        cbs_ach = _buttons(cba.message)
        check("aw_kind:ach: есть пики ачивок",
              sum(1 for c in cbs_ach if str(c).startswith("aw_pick:")) > 0)
        check("aw_kind:ach: заголовок про достижение",
              "достижение" in _last_text(cba.message).lower())

        # ── усечение длинного текста (страховка от лимита) ──
        long_txt = adm._fit_text("я" * 5000)
        check("_fit_text: обрезает до лимита", len(long_txt) <= 3800)
        check("_fit_text: короткий текст не трогает",
              adm._fit_text("ok") == "ok")

        # ── сброс состояния: без target_id показываем ошибку, не падаем ──
        cbx = FakeCallback(uid, "aw_kind:reg")
        await adm.award_grant_kind(cbx, FakeState({}))
        check("aw_kind без target_id: понятная ошибка",
              "Сессия" in _last_text(cbx.message) or
              any("Сессия" in str(m[1]) for m in cbx.message.sent))
    finally:
        await close_db()

    print(f"\nSmoke 151: {passed} passed, {failed} failed")
    return failed


if __name__ == "__main__":
    sys.exit(1 if asyncio.run(run()) else 0)
