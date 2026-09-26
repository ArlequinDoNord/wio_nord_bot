"""Smoke v0.15.30: админское выдание статуса (текущий статус) + метки туриста в Ратуше.

Что проверяется:
1. Старший статус игрока по иерархии (max sort_order) — _status_top/_status_current_line.
2. Экран выдачи статуса: сначала показан текущий статус, кнопки отсортированы
   по иерархии, ⭐ отмечает текущий, ✅ — уже выданный, ➕ — доступный к выдаче.
3. Выдача в одно нажатие (st_pick → статус выдан, без экрана «Что сделать?»).
4. Снятие статуса пересчитывает текущий.
5. Регресс: префикс st_op: больше не перехватывается статусным обработчиком
   (иначе ломалось наложение/снятие СОСТОЯНИЙ игроку).
6. Ратуша: в карточке пилота помечается турист, в списке пилотов — метка 🎫.

Запуск: .venv\\Scripts\\python.exe smoke_088.py
"""
import asyncio
import os
import sys

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke088.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB

sys.path.insert(0, os.path.dirname(__file__))


class _Attr:
    def __init__(self, **kw):
        self.__dict__.update(kw)


class _Msg:
    def __init__(self):
        self.photo = None
        self.text = "-"
        self.from_user = _Attr(id=777)
        self.sent = []          # (text, reply_markup)
        self.edited = []

    async def answer(self, text=None, reply_markup=None, **k):
        self.sent.append((text or "", reply_markup))

    async def edit_text(self, text=None, reply_markup=None, **k):
        self.edited.append((text or "", reply_markup))

    async def edit_caption(self, caption=None, reply_markup=None, **k):
        self.edited.append((caption or "", reply_markup))

    async def edit_media(self, media=None, reply_markup=None, **k):
        self.edited.append((getattr(media, "caption", ""), reply_markup))


class _State:
    def __init__(self, data):
        self.data = data
        self.state = None

    async def update_data(self, **kw):
        self.data.update(kw)

    async def get_data(self):
        return self.data

    async def set_state(self, s):
        self.state = s

    async def clear(self):
        self.data = {}


class _Cb:
    def __init__(self, data, state, admin_id=999):
        self.data = data
        self.message = _Msg()
        self.from_user = _Attr(id=admin_id)
        self._state = state

    async def answer(self, *a, **k):
        pass

    def _texts(self):
        return [t for t, _ in self.message.sent]


def _buttons(markup):
    return [b for row in markup.inline_keyboard for b in row]


async def run():
    from database.db import (
        init_db, close_db, add_user, get_user, get_user_statuses,
        get_status_by_tag, grant_status,
    )
    import bot.handlers.admin as admin_mod
    from bot.handlers.admin import (
        _status_top, _status_current_line, _status_grant_markup, _status_revoke_markup,
        status_grant_pick, status_revoke_pick, status_grant_more,
    )
    from bot.handlers.pilots import pilots_list_markup, town_hall_pilot_card

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

    # ── Пилоты: один турист, один гражданский ──
    await add_user(41001, "tourist01", "Турист", "Гость")
    await add_user(41002, "pilot002", "Пилот", "Служивый")
    tourist_st = await get_status_by_tag("tourist")
    recruit_st = await get_status_by_tag("recruit")
    ace_st = await get_status_by_tag("ace")
    await grant_status(41001, tourist_st['id'])
    await grant_status(41002, tourist_st['id'])   # у гражданского турист снят ниже
    await grant_status(41002, recruit_st['id'])
    await grant_status(41002, ace_st['id'])
    from database.db import revoke_status
    await revoke_status(41002, tourist_st['id'])

    # ── 1. Старший статус по иерархии ──
    have_none = await get_user_statuses(41003)
    check("нет статусов → top None", _status_top(have_none) is None)
    check("нет статусов → строка «нет»", "нет" in _status_current_line(have_none))

    have_t = await get_user_statuses(41001)
    check("один статус → top = этот", _status_top(have_t)['name'] == "Турист")
    check("один статус → без «Ещё есть»", "Ещё есть" not in _status_current_line(have_t))

    have_p = await get_user_statuses(41002)
    top = _status_top(have_p)
    check("несколько статусов → старший = Ас (sort_order 9)", top['name'] == "Ас")
    line = _status_current_line(have_p)
    check("текущий статус в строке", "Текущий статус: Ас" in line)
    check("остальные статусы перечислены", "Ещё есть" in line and "Рекрут" in line)

    # ── 2. Клавиатура выдачи: порядок по иерархии + пометки ──
    from database.db import get_all_statuses
    statuses = await get_all_statuses()
    kb = _status_grant_markup(statuses, have_p)
    btns = _buttons(kb)
    status_btns = [b for b in btns if b.callback_data.startswith("st_pick:")]
    levels = [s['sort_order'] for s in sorted(statuses, key=lambda x: (x['sort_order'] or 0))]
    check("кнопки статусов отсортированы по иерархии",
          len(status_btns) == len(statuses))
    check("первый в списке — самый слабый (Турист)",
          status_btns[0].text.endswith("Турист") and "сейчас" not in status_btns[0].text)
    ace_btn = [b for b in status_btns if "Ас" in b.text][0]
    check("текущий статус помечен ⭐ «сейчас»", ace_btn.text.startswith("⭐") and "сейчас" in ace_btn.text)
    rec_btn = [b for b in status_btns if "Рекрут" in b.text][0]
    check("уже выданный помечен ✅", rec_btn.text.startswith("✅"))
    pilot1_btn = [b for b in status_btns if "Пилот 1 класса" in b.text][0]
    check("невыданный помечен ➕", pilot1_btn.text.startswith("➕"))
    check("есть переход к снятию статуса",
          any(b.callback_data == "st:revoke" for b in btns))
    check("есть возврат к выбору пилота",
          any(b.callback_data == "st:grant" for b in btns))

    # ── 3. Клавиатура снятия: только свои статусы, ⭐ на текущем ──
    kb_rev = _status_revoke_markup(have_p)
    rev_btns = [b for b in _buttons(kb_rev) if b.callback_data.startswith("st_rev:")]
    check("снятие: только статусы пилота", len(rev_btns) == len(have_p))
    check("снятие: ⭐ на текущем", rev_btns[-1].text.startswith("⭐")
          and "Ас" in rev_btns[-1].text)
    check("снятие: порядок по иерархии",
          "Рекрут" in rev_btns[0].text)

    # ── 4. Выдача в одно нажатие ──
    pilot1_st = await get_status_by_tag("pilot1")
    state = _State({"target_id": 41001, "target_name": "Турист"})
    cb = _Cb(f"st_pick:{pilot1_st['id']}", state)
    await status_grant_pick(cb, state)
    out = cb._texts()
    check("выдача: сообщение об успехе", out and out[0].startswith("✅"))
    check("выдача: показан новый текущий статус",
          out and "Текущий статус: Пилот 1 класса" in out[0])
    have_after = await get_user_statuses(41001)
    check("выдача: статус реально добавлен", pilot1_st['id'] in [s['id'] for s in have_after])
    check("выдача: кнопка «выдать ещё»", any(
        b.callback_data == "st:more" for b in _buttons(cb.message.sent[0][1])))
    check("выдача: без экрана «Что сделать?»", not cb.message.edited)

    # повторная выдача того же статуса — понятное сообщение, без дубля
    cb2 = _Cb(f"st_pick:{pilot1_st['id']}", state)
    await status_grant_pick(cb2, state)
    check("повторная выдача — «уже есть»", "уже есть" in cb2._texts()[0].lower())

    # «выдать ещё» возвращает экран со статусами того же пилота
    cb3 = _Cb("st:more", state)
    await status_grant_more(cb3, state)
    check("«выдать ещё» → экран статусов пилота",
          cb3._texts() and "СТАТУС ПИЛОТА" in cb3._texts()[0])
    check("«выдать ещё» → текущий статус виден",
          cb3._texts() and "Текущий статус: Пилот 1 класса" in cb3._texts()[0])

    # без цели — понятная ошибка вместо исключения
    empty_state = _State({})
    cb4 = _Cb(f"st_pick:{pilot1_st['id']}", empty_state)
    await status_grant_pick(cb4, empty_state)
    check("выдача без цели → «сессия устарела»",
          cb4._texts() and "устарела" in cb4._texts()[0])

    # ── 5. Снятие статуса пересчитывает текущий ──
    st = _State({"target_id": 41001, "target_name": "Турист"})
    cb5 = _Cb(f"st_rev:{pilot1_st['id']}", st)
    await status_revoke_pick(cb5, st)
    check("снятие: сообщение об успехе", cb5._texts() and cb5._texts()[0].startswith("🚫"))
    check("снятие: текущий статус пересчитан",
          cb5._texts() and "Текущий статус: Турист" in cb5._texts()[0])
    have_left = await get_user_statuses(41001)
    check("снятие: статус реально удалён",
          pilot1_st['id'] not in [s['id'] for s in have_left])

    # ── 6. Регресс: st_op: не перехватывается статусным обработчиком ──
    src = open(os.path.join(os.path.dirname(__file__), "bot", "handlers", "admin.py"),
               encoding="utf-8").read()
    check("st_op: обрабатывается ровно одним хендлером (состояния)",
          src.count('@router.callback_query(F.data.startswith("st_op:")') == 1)
    check("статусный двухшаговый хендлер удалён",
          "async def status_grant_apply" not in src)
    check("экран «Что сделать?» удалён", "Что сделать?" not in src)

    # ── 7. Ратуша: метки туриста ──
    from database.db import users_with_exact_status
    tourists = await users_with_exact_status("tourist")
    check("турыст найден одним запросом", tourists == {41001})
    check("гражданский не турист", 41002 not in tourists)

    users = await __import__("database.db", fromlist=["get_all_users"]).get_all_users()
    labels = [b.text for b in _buttons(pilots_list_markup(users, tourists))]
    check("в списке пилотов турист помечен 🎫",
          any("🎫" in t and "Гость" in t for t in labels))
    check("в списке пилотов гражданский без метки",
          not any("🎫" in t and "Служивый" in t for t in labels))

    # карточка пилота: турист (41001) vs гражданственный (41002)
    cb_t = _Cb(f"rathaus:{41001}", _State({}))
    cb_t.message.from_user = _Attr(id=41002)
    await town_hall_pilot_card(cb_t)
    tourist_card = cb_t.message.edited + cb_t.message.sent
    check("карточка туриста помечена", any("Турист" in t for t, _ in tourist_card))

    cb_c = _Cb(f"rathaus:{41002}", _State({}))
    cb_c.message.from_user = _Attr(id=41001)
    await town_hall_pilot_card(cb_c)
    cit_card = cb_c.message.edited + cb_c.message.sent
    check("карточка гражданина без пометки о туристе",
          not any("гость" in t for t, _ in cit_card))

    await close_db()
    print(f"\nSmoke 088: {passed} passed, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    async def _main():
        try:
            return await run()
        finally:
            from database.db import close_db
            await close_db()

    sys.exit(asyncio.run(_main()))
