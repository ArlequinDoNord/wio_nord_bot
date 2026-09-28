"""Smoke: состав авиакрыла — командир набирает/убирает пилотов, заместитель.

Что проверяем:
  • командир берёт в своё крыло ТОЛЬКО свободных пилотов (занятые и чужие — отказ);
  • командир убирает пилота из своего крыла, но не может выбросить командира/заместителя;
  • заместителя назначает и снимает командир (или штаб), посторонний — нет;
  • заместитель может отдавать приказ своему крылу (роль wing_deputy даёт
    can_wing_commands) и НЕ может управлять составом;
  • пилот не может быть заместителем двух крыльев сразу.

Запуск: .venv\\Scripts\\python.exe smoke_092.py
"""
import asyncio
import os
import sys

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke092.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB

sys.path.insert(0, os.path.dirname(__file__))

from utils.wings import WINGS_SHORT  # noqa: E402

W1, W2 = list(WINGS_SHORT.keys())[0], list(WINGS_SHORT.keys())[1]


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
        init_db, close_db, add_user, get_user, set_wing,
        set_wing_commander, get_wing_commander, get_wing_commanders,
        get_wing_commander_by_user, set_wing_deputy, get_wing_deputy,
        get_wing_deputies, get_wing_deputy_by_user, get_wing_staff_wing,
        get_wing_staff_role, add_user_role, remove_user_role,
        count_unassigned_pilots, get_unassigned_pilots, get_wing_member_rows,
        count_wing_members,
    )
    from utils.permissions import has_permission, get_user_role
    from bot.handlers.hq import (
        hq_wing_take_cb, hq_wing_drop_cb, hq_wing_deputy_cb, hq_menu_show,
    )

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

    CMD = 90001   # командир 1-го крыла
    DEP = 90002   # заместитель
    P1 = 90003    # свободный пилот
    P2 = 90004    # свободный пилот
    OTHER = 90005  # командир 2-го крыла
    STRAFF = 90006  # штаб (super_admin не проверяем: ADMIN_IDS зависит от .env)

    for uid, name in ((CMD, "cmd"), (DEP, "dep"), (P1, "p1"), (P2, "p2"),
                      (OTHER, "other"), (STRAFF, "staff")):
        await add_user(uid, name, name.capitalize(), name.capitalize())

    # Командир 1-го и 2-го крыльев; в 1-м уже есть один пилот.
    await set_wing_commander(W1, CMD)
    await add_user_role(CMD, 'wing_commander', granted_by=STRAFF)
    await set_wing_commander(W2, OTHER)
    await add_user_role(OTHER, 'wing_commander', granted_by=STRAFF)
    await set_wing(P1, W1)

    # ── 1. Список свободных пилотов для набора ──
    free = await get_unassigned_pilots()
    free_ids = {u['user_id'] for u in free}
    check("свободные не включают пилота из крыла", P1 not in free_ids)
    check("свободные включают остальных", P2 in free_ids and CMD in free_ids)
    check("счётчик свободных совпадает", await count_unassigned_pilots() == len(free))

    # ── 2. Командир берёт свободного пилота ──
    cb = FakeCallbackQuery(f"hq:wingtake:do:{W1}:{P2}", CMD)
    await hq_wing_take_cb(cb)
    check("командир взял пилота в своё крыло", (await get_user(P2))['wing'] == W1)
    check("командиру ответили об успехе", "принят" in cb.message.last)

    # ── 3. Командир не может взять пилота, который уже в крыле ──
    cb = FakeCallbackQuery(f"hq:wingtake:do:{W1}:{P1}", CMD)
    await hq_wing_take_cb(cb)
    check("занятого пилота в список не берём", "уже в" in cb.message.last)
    check("чужое крыло не трогаем (P1 остался в 1-м)", (await get_user(P1))['wing'] == W1)

    # ── 4. Командир не может взять пилота из чужого крыла в своё ──
    await set_wing(OTHER, W2)
    cb = FakeCallbackQuery(f"hq:wingtake:do:{W1}:{OTHER}", CMD)
    await hq_wing_take_cb(cb)
    check("пилот чужого крыла не перехватывается", (await get_user(OTHER))['wing'] == W2)

    # ── 5. Подделка callback: чужое крыло в данных ──
    cb = FakeCallbackQuery(f"hq:wingtake:do:{W2}:{P1}", CMD)
    await hq_wing_take_cb(cb)
    check("поддельное крыло в callback игнорируется", (await get_user(P1))['wing'] == W1)

    # ── 6. Не-командир не управляет составом ──
    cb = FakeCallbackQuery(f"hq:wingtake:do:{W1}:{DEP}", P2)
    await hq_wing_take_cb(cb)
    check("пилот без должности не может набирать", "не командир" in cb.message.last)

    # ── 7. Убрать пилота из своего крыла ──
    cb = FakeCallbackQuery(f"hq:wingdrop:do:{W1}:{P2}", CMD)
    await hq_wing_drop_cb(cb)
    check("командир убрал пилота", not (await get_user(P2))['wing'])
    check("после удаления пилот снова свободен", P2 in {u['user_id'] for u in await get_unassigned_pilots()})
    check("состав крыла уменьшился", await count_wing_members(W1) == 1)
    rows = await get_wing_member_rows(W1)
    check("в составе крыла только свой пилот", [r['user_id'] for r in rows] == [P1])

    # ── 8. Командира и заместителя нельзя выбросить из своего крыла ──
    await set_wing(CMD, W1)
    cb = FakeCallbackQuery(f"hq:wingdrop:do:{W1}:{CMD}", CMD)
    await hq_wing_drop_cb(cb)
    check("командира из своего крыла не убрать", (await get_user(CMD))['wing'] == W1)
    check("и объяснили почему", "командир" in cb.message.last)

    # ── 9. Заместитель: назначение командиром ──
    cb = FakeCallbackQuery(f"hq:wingdep:{W1}:set:{P1}", CMD)
    await hq_wing_deputy_cb(cb)
    check("заместитель назначен", await get_wing_deputy(W1) == P1)
    check("заместитель в крыле", (await get_user(P1))['wing'] == W1)
    check("роль wing_deputy выдана", 'wing_deputy' in await get_user_role(P1))
    check("роль даёт право приказов", await has_permission(P1, 'can_wing_commands'))
    check("заместитель виден в словаре", (await get_wing_deputies()).get(W1) == P1)
    check("обратный поиск по пилоту", await get_wing_deputy_by_user(P1) == W1)
    check("должность заместителя", await get_wing_staff_role(P1) == 'deputy')
    check("крыло по пилоту", await get_wing_staff_wing(P1) == W1)

    cb = FakeCallbackQuery(f"hq:wingdep:{W1}:set:{P1}", CMD)
    await hq_wing_deputy_cb(cb)
    check("повторное назначение — отказ", "уже заместитель" in cb.message.last)

    cb = FakeCallbackQuery(f"hq:wingdep:{W1}:set:{CMD}", CMD)
    await hq_wing_deputy_cb(cb)
    check("командира нельзя сделать заместителем", "Командир и так" in cb.message.last)
    check("пост остался за прежним", await get_wing_deputy(W1) == P1)

    # ── 10. Заместитель не может назначать заместителей ──
    cb = FakeCallbackQuery(f"hq:wingdep:{W1}:set:{CMD}", P1)
    await hq_wing_deputy_cb(cb)
    check("заместитель не назначает заместителей", "только командир" in cb.message.last)
    check("и пост не сменился", await get_wing_deputy(W1) == P1)

    # ── 11. Посторонний не лезет в заместители ──
    cb = FakeCallbackQuery(f"hq:wingdep:{W1}", P2)
    await hq_wing_deputy_cb(cb)
    check("посторонний не видит экран заместителя", "только командир" in cb.message.last)

    # ── 12. Заместителем может быть только пилот своего крыла ──
    await set_wing(P2, W2)
    cb = FakeCallbackQuery(f"hq:wingdep:{W1}:set:{P2}", CMD)
    await hq_wing_deputy_cb(cb)
    check("пилот чужого крыла не becomes заместителем", await get_wing_deputy(W1) == P1)
    check("и объяснили почему", "этого крыла" in cb.message.last)

    # ── 13. Снятие заместителя ──
    cb = FakeCallbackQuery(f"hq:wingdep:{W1}:unset", CMD)
    await hq_wing_deputy_cb(cb)
    check("заместитель снят", await get_wing_deputy(W1) is None)
    check("роль снята", not 'wing_deputy' in await get_user_role(P1))
    check("пилот остался в крыле", (await get_user(P1))['wing'] == W1)
    check("прав больше нет", not await has_permission(P1, 'can_wing_commands'))

    # ── 14. Заместитель берётся из своего состава; перевод штабом снимает старый пост ──
    await hq_wing_deputy_cb(FakeCallbackQuery(f"hq:wingdep:{W1}:set:{P1}", CMD))
    check("заместитель 1-го крыла снова назначен", await get_wing_deputy(W1) == P1)
    await set_wing_commander(W2, OTHER)
    await set_wing(P1, W2)  # штаб перевёл пилота во 2-е крыло
    check("перевод через штаб", (await get_user(P1))['wing'] == W2)
    cb = FakeCallbackQuery(f"hq:wingdep:{W2}:set:{P1}", OTHER)
    await hq_wing_deputy_cb(cb)
    check("назначен заместителем 2-го крыла", await get_wing_deputy(W2) == P1)
    check("в 1-м крыле заместитель теперь не он",
          (await get_wing_deputies()).get(W1) is None)
    check("роль wing_deputy осталась одна", 'wing_deputy' in await get_user_role(P1))

    # ── 15. Меню штаба: у заместителя нет кнопок состава ──
    msg = FakeMessage()
    await hq_menu_show(msg, P1)  # сейчас заместитель 2-го крыла
    btns = msg.buttons()
    check("заместитель видит кнопку приказа", "hq:wingcmd_send" in btns)
    check("заместитель НЕ видит кнопки набора", "hq:wingtake:0" not in btns)
    check("заместитель НЕ видит кнопки увода", "hq:wingdrop:0" not in btns)
    check("заместитель НЕ видит кнопку состава ВВС", "hq:wing" not in btns)

    msg = FakeMessage()
    await hq_menu_show(msg, CMD)
    btns = msg.buttons()
    check("командир видит кнопки своего состава",
          "hq:wingtake:0" in btns and "hq:wingdrop:0" in btns)
    check("кнопка заместителя с его крылом", f"hq:wingdep:{W1}" in btns)

    # ── 16. Список пилота для выбора заместителя — только состав крыла ──
    await set_wing(P2, W1)
    cb = FakeCallbackQuery(f"hq:wingdep:{W1}:list:0", CMD)
    await hq_wing_deputy_cb(cb)
    check("экран выбора заместителя открылся", "Заместитель из состава" in str(cb.message.answers))

    await close_db()
    print(f"\nSmoke 092: {passed} passed, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    async def _main():
        try:
            return await run()
        finally:
            from database.db import close_db
            await close_db()

    sys.exit(asyncio.run(_main()))
