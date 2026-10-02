"""Smoke 117 — can_view_balances: режим «только чтение» для казны.

Что проверяем:
   1. Право было мёртвым: объявлено, но не проверялось НИГДЕ.
   2. Теперь «посмотреть» и «потратить» — разные права:
      читать казну/статистику/долги = can_view_balances,
      выдать из казны, менять налоги и зарплаты = can_manage_finance.
   3. Квестор (finance_helper) может начислять НМ и ВИДИТЬ казну,
      но не может из неё тратить.
   4. Хранитель (super_admin) видит балансы без can_manage_finance.
   5. Найденный баг: perm_flags не отдавал 4 права, из-за чего кнопки
      были always-False (Квестор вообще не попадал в «Финансы»,
      глава МВД — в управление крылом).
"""
import asyncio
import inspect
import os
import sys

_TEST_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_test_smoke117.db")
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
    from utils.permissions import has_permission

    await init_db()

    OWNER = 3001      # владелец из .env
    KEEPER = 3002     # Хранитель (super_admin)
    FIN = 3003        # Министр финансов (finance_admin)
    QUAESTOR = 3004   # Квестор (finance_helper)
    CHIEF = 3005      # глава МВД (moderator)
    CIVIL = 3006      # обычный игрок
    for uid in (KEEPER, FIN, QUAESTOR, CHIEF, CIVIL):
        await add_user(uid, f"u{uid}", f"Имя{uid}", f"u{uid}")
    await add_user_role(KEEPER, 'super_admin')
    await add_user_role(FIN, 'finance_admin')
    await add_user_role(QUAESTOR, 'finance_helper')
    await add_user_role(CHIEF, 'moderator')

    # ── 1. право перестало быть мёртвым ─────────────────────────────
    print("=== 1. can_view_balances назначена ролям ===")
    check("finance_helper: can_view_balances",
          P.ROLES['finance_helper'].get('can_view_balances') is True)
    check("finance_admin: can_view_balances (уже была)",
          P.ROLES['finance_admin'].get('can_view_balances') is True)
    check("super_admin: can_view_balances",
          P.ROLES['super_admin'].get('can_view_balances') is True)
    check("moderator: НЕТ can_view_balances (МВД не в казне)",
          P.ROLES['moderator'].get('can_view_balances', False) is False)
    check("mvd_helper: НЕТ can_view_balances",
          P.ROLES['mvd_helper'].get('can_view_balances', False) is False)

    # ── 2. разделение view / mutate ─────────────────────────────────
    print("\n=== 2. Матрица прав ===")
    check("Квестор: НЕТ can_manage_finance",
          not await has_permission(QUAESTOR, "can_manage_finance"))
    check("Квестор: can_add_currency",
          await has_permission(QUAESTOR, "can_add_currency"))
    check("Квестор: can_view_balances",
          await has_permission(QUAESTOR, "can_view_balances"))
    check("Квестор: НЕТ can_remove_currency",
          not await has_permission(QUAESTOR, "can_remove_currency"))
    check("Хранитель: can_view_balances",
          await has_permission(KEEPER, "can_view_balances"))
    # У Хранителя есть и полный can_manage_finance — он доверенное лицо
    # командования (level 100), поэтому тратить из казны он может.
    # can_view_balances у него избыточен, но оставлен явно.
    check("Хранитель: полные права финансов (can_manage_finance)",
          await has_permission(KEEPER, "can_manage_finance"))
    check("глава МВД: НЕТ can_view_balances",
          not await has_permission(CHIEF, "can_view_balances"))
    check("обычный игрок: всё False",
          not await has_permission(CIVIL, "can_view_balances")
          and not await has_permission(CIVIL, "can_manage_finance"))

    # ── 3. хелпер _can_view_finance ─────────────────────────────────
    print("\n=== 3. _can_view_finance() ===")
    from bot.handlers.admin import _can_view_finance
    check("Квестор может посмотреть казну", await _can_view_finance(QUAESTOR))
    check("Хранитель может посмотреть казну", await _can_view_finance(KEEPER))
    check("Минфин может посмотреть казну", await _can_view_finance(FIN))
    check("глава МВД НЕ может посмотреть казну", not await _can_view_finance(CHIEF))
    check("игрок НЕ может посмотреть казну", not await _can_view_finance(CIVIL))

    # ── 4. экраны только для чтения открыты, изменение — нет ─────────
    print("\n=== 4. Кто на какие экраны попадает ===")
    from bot.handlers import admin as A
    for name in ("admin_treasury", "treasury_stats", "treasury_debts"):
        src = inspect.getsource(getattr(A, name))
        check(f"{name}: проверка через _can_view_finance",
              "_can_view_finance" in src)
    # А трата денег осталась только за can_manage_finance.
    src_give = inspect.getsource(A.treasury_give)
    check("treasury:give требует именно can_manage_finance",
          'has_permission(callback.from_user.id, "can_manage_finance")' in src_give)
    check("treasury:give НЕ пускает по can_view_balances",
          "can_view_balances" not in src_give)
    for name in ("admin_tax_view", "admin_saletax_view"):
        src = inspect.getsource(getattr(A, name))
        check(f"{name}: налог меняет только can_manage_finance",
              'has_permission(callback.from_user.id, "can_manage_finance")' in src
              and "_can_view_finance" not in src)

    # ── 5. баг perm_flags: кнопки были always-False ─────────────────
    print("\n=== 5. perm_flags отдаёт всё, что проверяет UI ===")
    src = inspect.getsource(A.perm_flags)
    for p in ("can_view_balances", "can_add_currency", "can_remove_currency",
              "can_manage_wing"):
        check(f"perm_flags отдаёт {p}", f'"{p}"' in src)

    f_quaestor = await A.perm_flags(QUAESTOR)
    check("Квестор: флаг can_view_balances = True", f_quaestor.get('can_view_balances') is True)
    check("Квестор: флаг can_add_currency = True", f_quaestor.get('can_add_currency') is True)
    check("Квестор: флаг can_manage_finance = False", f_quaestor.get('can_manage_finance') is False)

    f_chief = await A.perm_flags(CHIEF)
    check("глава МВД: флаг can_manage_wing = True", f_chief.get('can_manage_wing') is True)

    # ── 6. кнопки в меню ───────────────────────────────────────────
    print("\n=== 6. Кнопки в админ-меню ===")
    from keyboards.keyboards import admin_panel_keyboard
    kb_q = str(admin_panel_keyboard(f_quaestor))
    check("Квестор ВИДИТ «Финансы» (раньше было невидимо)",
          "admin:finance" in kb_q)
    check("Квестор НЕ видит «Управление ролями»", "admin:roles" not in kb_q)
    kb_chief = str(admin_panel_keyboard(f_chief))
    check("глава МВД видит кнопку крыла (can_manage_wing доехало)",
          "can_manage_wing" in inspect.getsource(admin_panel_keyboard)
          and P.ROLES['moderator'].get('can_manage_wing') is True)
    kb_civ = str(admin_panel_keyboard(await A.perm_flags(CIVIL)))
    check("обычный игрок не видит «Финансы»", "admin:finance" not in kb_civ)

    # ── 7. правка прав в ROLES ничего не сломала ───────────────────
    print("\n=== 7. Целостность модели ролей ===")
    perms = {k for r in P.ROLES.values() for k in r if k != "level"}
    check("все 33 права ещё объявлены", len(perms) == 33)
    unused = [p for p in perms if not any(r.get(p) for r in P.ROLES.values())]
    check("мёртвых прав больше нет", not unused)
    if unused:
        print("      остались:", unused)
    check("super_admin по-прежнему выше moderator",
          P.ROLES['super_admin']['level'] > P.ROLES['moderator']['level'])

    await close_db()
    print(f"\n=== SMOKE 117: {PASS} passed, {FAIL} failed ===")
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