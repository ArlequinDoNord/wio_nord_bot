"""Smoke: Штаб ВВС — в списки и крыло только гражданские (sort_order >= 1).

Баг (фидбек владельца 2026-09-28): в штабе в списках сидели туристы, и их
реально можно было взять в авиакрыло. Починено единым определением гражданства
(_citizens_sql в db.py): старший статус пилота от «Рекрута» (sort_order >= 1).

Что проверяем:
  • get_all_users(citizens_only=True) не отдаёт туристов, отдаёт гражданских;
  • get_unassigned_pilots(citizens_only=True) и count_unassigned_pilots —
    то же для «Взять пилота»;
  • сводка «Состав ВВС» (hq:wing) не считает туристов;
  • экран выбора «Взять пилота» (hq:wingtake:0) не показывает туриста;
  • hq:wingtake:do с туристом — отказ и users.wing НЕ пишется;
  • hq:wingtake:do с гражданином — успех (wing пишется);
  • пикер «выбрать пилота» (hq:roster) — туриста нет.

Запуск: .venv\\Scripts\\python.exe smoke_097.py
"""
import asyncio
import os
import sys

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke097.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB

sys.path.insert(0, os.path.dirname(__file__))

from utils.wings import WINGS_SHORT  # noqa: E402

W1 = list(WINGS_SHORT.keys())[0]


class FakeMessage:
    def __init__(self, chat_id=1):
        self.chat = type("C", (), {"id": chat_id, "type": "private"})()
        self.text = None
        self.message_thread_id = None
        self.answers = []
        self.kwargs = []

    async def answer(self, text, **kwargs):
        self.answers.append(text)
        self.kwargs.append(kwargs)

    async def edit_text(self, text, **kwargs):
        self.answers.append(text)
        self.kwargs.append(kwargs)

    @property
    def last(self):
        return self.answers[-1] if self.answers else ""

    def buttons(self):
        """Все callback_data из последней разметки."""
        markup = self.kwargs[-1].get('reply_markup') if self.kwargs else None
        if not markup:
            return []
        return [b.callback_data for row in markup.inline_keyboard for b in row]


class FakeCallbackQuery:
    def __init__(self, data, user_id):
        self.message = FakeMessage()
        self.data = data
        self.from_user = type("U", (), {"id": user_id})()
        self.answered = False

    async def answer(self, *a, **kw):
        self.answered = True


async def run():
    from database.db import (
        init_db, close_db, add_user, get_user,
        get_status_by_tag, grant_status, citizen_user_ids,
        get_all_users, get_unassigned_pilots, count_unassigned_pilots,
    )
    from bot.handlers.hq import hq_wing_take_cb, hq_wing_cb

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

    CMD = 97001   # командир 1-го крыла (гражданин)
    STAFF = 97002  # штаб с правом can_manage_wing (moderator)
    CIT = 97003   # гражданский свободный пилот
    TOUR = 97004  # турист без гражданства

    for uid, name in ((CMD, "cmd"), (STAFF, "staff"), (CIT, "cit"), (TOUR, "tour")):
        await add_user(uid, name, name.capitalize(), name.capitalize())

    # Гражданство (как в начальной выдаче статусов): Рекрут.
    recruit = await get_status_by_tag("recruit")
    for uid in (CMD, STAFF, CIT):
        await grant_status(uid, recruit['id'], 0)
    # Туристу — явный «Турист», чтобы фальшивого гражданства не было.
    tourist = await get_status_by_tag("tourist")
    await grant_status(TOUR, tourist['id'], 0)

    # Командир крыла и штаб.
    from database.db import add_user_role
    from database.db import set_wing_commander
    await set_wing_commander(W1, CMD)
    await add_user_role(CMD, 'wing_commander', granted_by=STAFF)
    await add_user_role(STAFF, 'moderator', granted_by=STAFF)

    # ── 1. citizen_user_ids() — единое определение гражданства ──
    citizens = await citizen_user_ids()
    check("турист не гражданин", TOUR not in citizens)
    check("гражданин в списке", CIT in citizens and CMD in citizens and STAFF in citizens)

    # ── 2. get_all_users(citizens_only=True) ──
    all_cit = await get_all_users(citizens_only=True)
    all_ids = {u['user_id'] for u in all_cit}
    check("сводка не включает туриста", TOUR not in all_ids)
    check("сводка включает гражданских", CIT in all_ids and CMD in all_ids)

    # ── 3. get_unassigned_pilots / count_unassigned_pilots — «Взять пилота» ──
    free = await get_unassigned_pilots(citizens_only=True)
    free_ids = {u['user_id'] for u in free}
    check("«взять пилота» не включает туриста", TOUR not in free_ids)
    check("«взять пилота» включает гражданина", CIT in free_ids)
    check("счётчик свободных совпадает",
          await count_unassigned_pilots(citizens_only=True) == len(free))

    # ── 4. Экран выбора «Взять пилота» (командир, hq:wingtake:0) ──
    cb = FakeCallbackQuery(f"hq:wingtake:0", CMD)
    await hq_wing_take_cb(cb)
    buttons = cb.message.buttons()
    check("в кнопках выбора НЕТ туриста",
          not any(f"{TOUR}" in b for b in buttons))
    check("в кнопках выбора ЕСТЬ гражданин",
          any(f"{CIT}" in b for b in buttons))

    # ── 5. hq:wingtake:do с туристом — отказ, wing не пишется ──
    cb = FakeCallbackQuery(f"hq:wingtake:do:{W1}:{TOUR}", CMD)
    await hq_wing_take_cb(cb)
    check("туристу отказано", "турист" in cb.message.last.lower())
    check("турист не попал в крыло", (await get_user(TOUR))['wing'] in (None, "", "none"))

    # ── 6. hq:wingtake:do с гражданином — успех ──
    cb = FakeCallbackQuery(f"hq:wingtake:do:{W1}:{CIT}", CMD)
    await hq_wing_take_cb(cb)
    check("гражданин принят в крыло", (await get_user(CIT))['wing'] == W1)
    check("ответ об успехе", "принят" in cb.message.last)

    # ── 7. Сводка «Состав ВВС» (штаб с can_manage_wing) не считает туриста ──
    cb = FakeCallbackQuery("hq:wing", STAFF)
    await hq_wing_cb(cb)
    text = str(cb.message.answers)
    check("турист не в сводке состава", f"{TOUR}" not in text)
    check("сводка открылась", "СОСТАВ ВВС" in text)
    check("пилот из крыла посчитан", f"{CIT}" not in text)  # в сводке имена не вяжутся в текст

    await close_db()
    print(f"\nSmoke 097: {passed} passed, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    async def _main():
        try:
            return await run()
        finally:
            from database.db import close_db
            await close_db()

    sys.exit(asyncio.run(_main()))