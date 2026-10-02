"""Smoke 115 — делегирование роли вице-доминуса.

Проверяем, что помощника главы МВД (mvd_helper / «Вице-доминус») может
назначать и снимать глава МВД (moderator) и Хранитель (super_admin), а любой
другой ролью глава МВД по-прежнему управлять не может — это остаётся за
Хранителем. Плюс контроль, что в админ-меню глава МВД видит кнопку ролей, а
вице-доминус — нет.
"""
import asyncio
import os
import sys

_TEST_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_test_smoke115.db")
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


async def main():
    import config

    config.DB_PATH = _TEST_DB
    from database.db import init_db, close_db, add_user, add_user_role
    import utils.permissions as P
    from utils.permissions import get_user_role
    from keyboards.keyboards import admin_panel_keyboard

    await init_db()

    ALL_PERMS = {p for r in P.ROLES.values() for p in r if p.startswith('can_')}
    check("все права ролей собраны для проверки меню", len(ALL_PERMS) > 20)

    KEEPER = 1001      # Хранитель (super_admin)
    CHIEF = 1002       # глава МВД (moderator)
    VICE = 1003        # вице-доминус (mvd_helper)
    PILOT = 1004       # обычный пилот
    for uid in (KEEPER, CHIEF, VICE, PILOT):
        await add_user(uid, f"p{uid}", None, f"pilot{uid}")
    # Роли выдаём напрямую в БД (add_user_role — низкоуровневая функция,
    # в обход проверки прав, которой пользуется админка).
    await add_user_role(KEEPER, 'super_admin')
    await add_user_role(CHIEF, 'moderator')
    await add_user_role(VICE, 'mvd_helper')
    check("роли в тестовой БД расставлены",
          'moderator' in await get_user_role(CHIEF)
          and 'mvd_helper' in await get_user_role(VICE))

    # ── 1. объявление прав ───────────────────────────────────────────
    print("=== 1. Права в ROLES ===")
    check("moderator может назначать вице-доминуса",
          P.ROLES['moderator'].get('can_assign_mvd_helper') is True)
    check("super_admin может назначать вице-доминуса",
          P.ROLES['super_admin'].get('can_assign_mvd_helper') is True)
    check("mvd_helper не может назначать роли (нет can_assign_mvd_helper)",
          P.ROLES['mvd_helper'].get('can_assign_mvd_helper', False) is False)
    check("mvd_helper не может управлять админами",
          P.ROLES['mvd_helper'].get('can_manage_admins', False) is False)
    check("вице-доминус объявлен делегируемым",
          'mvd_helper' in P.DELEGABLE_ROLES)
    check("делегируемая роль требует именно can_assign_mvd_helper",
          P.DELEGABLE_ROLES.get('mvd_helper') == 'can_assign_mvd_helper')
    check("у moderator НЕТ can_manage_admins",
          P.ROLES['moderator'].get('can_manage_admins', False) is False)

    # ── 2. глава МВД назначает вице-доминуса ─────────────────────────
    print("\n=== 2. Глава МВД назначает и снимает вице-доминуса ===")
    check("can_assign_role(глава МВД, mvd_helper) = True",
          await P.can_assign_role(CHIEF, 'mvd_helper'))
    # Цель — отдельный пилот: у VICE роль уже стоит как исходное состояние.
    ok, msg = await P.add_role(CHIEF, PILOT, 'mvd_helper')
    check("глава МВД выдал mvd_helper", ok)
    check("роль mvd_helper у помощника есть",
          'mvd_helper' in await get_user_role(PILOT))
    check("сообщение содержит название роли", 'Вице' in msg)
    check("повторная выдача отклонена (роль уже есть)",
          (await P.add_role(CHIEF, PILOT, 'mvd_helper'))[0] is False)

    ok, _ = await P.remove_role(CHIEF, PILOT, 'mvd_helper')
    check("глава МВД снял mvd_helper", ok)
    check("роль действительно убрана",
          'mvd_helper' not in await get_user_role(PILOT))

    # ── 3. глава МВД НЕ назначает другие роли ────────────────────────
    print("\n=== 3. Глава МВД не может трогать чужие роли ===")
    for role in ('super_admin', 'moderator', 'finance_admin', 'librarian',
                 'wing_commander', 'shop_admin', 'journalist', 'editor',
                 'clan_leader', 'representative'):
        check(f"can_assign_role(глава МВД, {role}) = False",
              not await P.can_assign_role(CHIEF, role))
    ok, _ = await P.add_role(CHIEF, PILOT, 'finance_admin')
    check("глава МВД НЕ выдал finance_admin", not ok)
    check("finance_admin не достался пилоту",
          'finance_admin' not in await get_user_role(PILOT))
    ok, _ = await P.add_role(CHIEF, PILOT, 'super_admin')
    check("глава МВД НЕ выдал Хранителя", not ok)

    # ── 4. вице-доминус и пилот не назначают ничего ───────────────────
    print("\n=== 4. Помощник и пилот не управляют ролями ===")
    for actor, who in ((VICE, 'вице-доминус'), (PILOT, 'пилот')):
        check(f"{who}: не может выдать mvd_helper",
              not await P.can_assign_role(actor, 'mvd_helper'))
        check(f"{who}: не может выдать finance_admin",
              not await P.can_assign_role(actor, 'finance_admin'))
        ok, _ = await P.add_role(actor, PILOT, 'mvd_helper')
        check(f"{who}: add_role(mvd_helper) отклонено", not ok)

    # ── 5. Хранитель может всё ───────────────────────────────────────
    print("\n=== 5. Хранитель управляет всеми ролями ===")
    for role in ('mvd_helper', 'finance_admin', 'librarian', 'wing_commander',
                 'moderator', 'shop_admin', 'clan_leader'):
        check(f"can_assign_role(Хранитель, {role}) = True",
              await P.can_assign_role(KEEPER, role))
    ok, _ = await P.add_role(KEEPER, PILOT, 'librarian')
    check("Хранитель выдал librarian", ok)
    check("librarian у пилота есть", 'librarian' in await get_user_role(PILOT))
    ok, _ = await P.remove_role(KEEPER, PILOT, 'librarian')
    check("Хранитель снял librarian", ok)
    check("Хранитель может снять вице-доминуса",
          await P.can_assign_role(KEEPER, 'mvd_helper'))
    ok, _ = await P.add_role(KEEPER, PILOT, 'super_admin')
    check("Хранитель тоже НЕ выдаёт Хранителя через панель", not ok)

    # ── 6. неизвестная роль отклоняется даже Хранителем ───────────────
    print("\n=== 6. Защита от неизвестных ролей ===")
    ok, msg = await P.add_role(KEEPER, PILOT, 'not_a_role')
    check("неизвестная роль отклонена", not ok)
    check("в тексте ошибки есть 'неизвестная' или 'Неизвестная'",
          'неизвестн' in msg.lower())

    # ── 7. кнопка в админ-меню ───────────────────────────────────────
    print("\n=== 7. Кнопка «Управление ролями» в админ-меню ===")
    # Флаги главы МВД = его собственные права (perm_flags отдаёт по белому списку).
    chief_flags = {p: (p in P.ROLES['moderator']) for p in ALL_PERMS}
    kb = admin_panel_keyboard(chief_flags)
    check("глава МВД видит кнопку «Управление ролями»",
          "admin:roles" in str(kb))
    check("глава МВД НЕ видит «Финансы» (нет can_manage_finance)",
          "admin:finance" not in str(kb))
    check("глава МВД видит «Отчёты» (can_view_reports)",
          "admin:reports" in str(kb))
    check("глава МВД видит «Повышение в звании» (can_grant_troops)",
          "admin:ranks" in str(kb))
    check("глава МВД НЕ видит «Управление магазином»",
          "admin:shop" not in str(kb))
    check("глава МВД НЕ видит «Локации» (can_manage_locations)",
          "admin:locations" not in str(kb))

    vice_flags = {p: (p in P.ROLES['mvd_helper']) for p in ALL_PERMS}
    kb = admin_panel_keyboard(vice_flags)
    check("вице-доминус без can_assign_mvd_helper НЕ видит кнопку ролей",
          "admin:roles" not in str(kb))
    check("вице-доминус видит «Отчёты» (can_view_reports)",
          "admin:reports" in str(kb))
    check("вице-доминус НЕ видит «Повышение в звании»",
          "admin:ranks" not in str(kb))
    check("вице-доминус НЕ видит «Локации»",
          "admin:locations" not in str(kb))

    # ── 8. perm_flags подтягивает новое право ─────────────────────────
    print("\n=== 8. perm_flags отдаёт новое право в меню ===")
    from bot.handlers.admin import perm_flags
    f_chief = await perm_flags(CHIEF)
    check("perm_flags(глава МВД)['can_assign_mvd_helper'] = True",
          f_chief.get('can_assign_mvd_helper') is True)
    f_vice = await perm_flags(VICE)
    check("perm_flags(вице-доминус)['can_assign_mvd_helper'] = False",
          f_vice.get('can_assign_mvd_helper') is False)

    await close_db()
    print(f"\n=== SMOKE 115: {PASS} passed, {FAIL} failed ===")
    return 1 if FAIL else 0


if __name__ == "__main__":
    code = 1
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        code = loop.run_until_complete(main())
    finally:
        _l = asyncio.new_event_loop()
        asyncio.set_event_loop(_l)
        try:
            import database.db as _db

            if _db.db is not None:
                _l.run_until_complete(_db.close_db())
        except Exception:
            pass
        _l.close()
    sys.exit(code)
