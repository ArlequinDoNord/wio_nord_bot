"""Smoke 116 — приём в гражданство главой МВД + отчёты у Хранителя из роли.

Что проверяем:
   1. Гражданство — это статус с sort_order >= 1; ворота = «Рекрут»
      (access_tag='recruit', sort_order=1). «Турист» (-10) — не гражданин.
   2. Глава МВД (moderator) может выдать и снять ТОЛЬКО статус-ворота.
      Ни «Аса», ни «Хранителя», ни «Туриста» — даже себе.
   3. Хранитель (super_admin) выдаёт любой статус, и теперь у него есть
      can_view_reports / can_approve_reports (раньше были только у владельца
      из .env — выданный через панель Хранитель отчётов не видел).
   4. Раньше st:grant / st:revoke / st_pick: / st_rev: не проверяли права ВООБЩЕ.
      Теперь проверка есть на каждом шаге.
"""
import asyncio
import os
import sys

_TEST_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_test_smoke116.db")
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
    from database.db import (init_db, close_db, add_user, add_user_role,
                             create_status, get_status_by_tag, get_status,
                             grant_status, revoke_status, citizen_user_ids,
                             user_has_status_tag, get_all_statuses)
    import utils.permissions as P
    from utils.permissions import (can_grant_status, can_view_status_panel,
                                  is_citizen_gate_status)

    await init_db()

    KEEPER = 2001      # Хранитель (super_admin)
    CHIEF = 2002       # глава МВД (moderator)
    VICE = 2003        # вице-доминус (mvd_helper)
    TOURIST = 2004     # принимаемый в гражданство
    for uid in (KEEPER, CHIEF, VICE, TOURIST):
        await add_user(uid, f"u{uid}", f"Имя{uid}", f"u{uid}")
    await add_user_role(KEEPER, 'super_admin')
    await add_user_role(CHIEF, 'moderator')
    await add_user_role(VICE, 'mvd_helper')

    # Шкала статусов. Базовые статусы (включая «Рекрут» с тегом recruit и
    # sort_order=1) уже создаёт ensure_base_statuses при init_db — создавать
    # их повторно нельзя, будет отказ «такое название уже есть».
    s_tourist = await get_status_by_tag("tourist")
    s_recruit = await get_status_by_tag("recruit")
    s_pilot2 = await get_status_by_tag("pilot2")
    s_ace = await get_status_by_tag("ace")
    s_keeper = await get_status_by_tag("keeper")
    check("базовые статусы созданы ensure_base_statuses", all(
        s is not None for s in (s_tourist, s_recruit, s_pilot2, s_ace, s_keeper)))
    check("«Рекрут» из коробки: sort_order = 1", s_recruit['sort_order'] == 1)
    check("«Турист» из коробки: sort_order = -10", s_tourist['sort_order'] == -10)

    # ── 1. что такое ворота в гражданство ────────────────────────────
    print("=== 1. Статус-ворота в гражданство ===")
    check("ворота опознаются по access_tag='recruit'",
          is_citizen_gate_status(s_recruit))
    check("ворота опознаются по sort_order == 1",
          is_citizen_gate_status({"access_tag": None, "sort_order": 1}))
    check("«Турист» (-10) НЕ ворота", not is_citizen_gate_status(s_tourist))
    check("«Ас» (9) НЕ ворота", not is_citizen_gate_status(s_ace))
    check("«Хранитель» (100) НЕ ворота", not is_citizen_gate_status(s_keeper))
    check("«Пилот 2 класса» (2) НЕ ворота", not is_citizen_gate_status(s_pilot2))
    check("None не ворота", not is_citizen_gate_status(None))
    check("пустая строка не ворота", not is_citizen_gate_status(""))

    # ── 2. права в ролях ────────────────────────────────────────────
    print("\n=== 2. Права в ROLES ===")
    check("moderator: can_grant_citizen_status",
          P.ROLES['moderator'].get('can_grant_citizen_status') is True)
    check("super_admin: can_grant_citizen_status",
          P.ROLES['super_admin'].get('can_grant_citizen_status') is True)
    check("moderator НЕ может создавать/удалять статусы",
          P.ROLES['moderator'].get('can_manage_statuses', False) is False)
    check("mvd_helper: нет can_grant_citizen_status",
          P.ROLES['mvd_helper'].get('can_grant_citizen_status', False) is False)
    check("mvd_helper: нет can_manage_statuses",
          P.ROLES['mvd_helper'].get('can_manage_statuses', False) is False)
    check("super_admin: can_manage_statuses",
          P.ROLES['super_admin'].get('can_manage_statuses') is True)
    check("super_admin: can_grant_statuses (было недостижимо)",
          P.ROLES['super_admin'].get('can_grant_statuses') is True)
    check("super_admin: can_view_reports (было недостижимо для роли)",
          P.ROLES['super_admin'].get('can_view_reports') is True)
    check("super_admin: can_approve_reports",
          P.ROLES['super_admin'].get('can_approve_reports') is True)

    # ── 3. кто что может выдать ─────────────────────────────────────
    print("\n=== 3. Матрица can_grant_status ===")
    check("глава МВД: «Рекрут» = можно",
          await can_grant_status(CHIEF, s_recruit))
    for s, nm in ((s_tourist, "Турист"), (s_ace, "Ас"),
                  (s_keeper, "Хранитель"), (s_pilot2, "Пилот 2 класса")):
        check(f"глава МВД: «{nm}» = нельзя", not await can_grant_status(CHIEF, s))
    check("Хранитель: «Рекрут» = можно", await can_grant_status(KEEPER, s_recruit))
    check("Хранитель: «Ас» = можно", await can_grant_status(KEEPER, s_ace))
    check("Хранитель: «Хранитель» = можно", await can_grant_status(KEEPER, s_keeper))
    check("вице-доминус: «Рекрут» = нельзя",
          not await can_grant_status(VICE, s_recruit))
    check("турист (без роли): «Рекрут» = нельзя",
          not await can_grant_status(TOURIST, s_recruit))
    check("панель статусов: главе МВД видна",
          await can_view_status_panel(CHIEF))
    check("панель статусов: вице-доминусу НЕ видна",
          not await can_view_status_panel(VICE))
    check("панель статусов: Хранителю видна",
          await can_view_status_panel(KEEPER))

    # ── 4. приём в гражданство вживую ───────────────────────────────
    print("\n=== 4. Глава МВД принимает туриста в гражданство ===")
    await grant_status(TOURIST, s_tourist['id'], KEEPER)
    citizens = await citizen_user_ids()
    check("до приёма турист не гражданин", TOURIST not in citizens)
    check("у туриста есть статус «Турист»",
          await user_has_status_tag(TOURIST, "tourist"))
    check("нет «Рекрута» до приёма",
          not await user_has_status_tag(TOURIST, "recruit"))

    ok, _ = await grant_status(TOURIST, s_recruit['id'], CHIEF)
    check("глава МВД выдал «Рекрут»", ok)
    check("теперь у пилота есть «Рекрут»",
          await user_has_status_tag(TOURIST, "recruit"))
    check("турист стал гражданином", TOURIST in await citizen_user_ids())

    # ── 5. глава МВД не может выдать себе сильный статус ────────────
    print("\n=== 5. Глава МВД не может выдать себе сильный статус ===")
    for s, nm in ((s_ace, "Ас"), (s_keeper, "Хранитель")):
        check(f"право на «{nm}» у главы МВД отсутствует",
              not await can_grant_status(CHIEF, s))
    # Даже если подсунуть id в callback — проверка обязана отклонить.
    forged_ok = await can_grant_status(CHIEF, await get_status(s_ace['id']))
    check("подделка id «Аса» в st_pick: отклонена", not forged_ok)

    # ── 6. снятие гражданства ───────────────────────────────────────
    print("\n=== 6. Снятие гражданства главой МВД ===")
    check("глава МВД может снять «Рекрут»",
          await can_grant_status(CHIEF, await get_status(s_recruit['id'])))
    await revoke_status(TOURIST, s_recruit['id'])
    citizens = await citizen_user_ids()
    check("после снятия «Рекрута» пилот снова не гражданин",
          TOURIST not in citizens)
    check("«Турист» на месте, гражданство не снято полностью",
          await user_has_status_tag(TOURIST, "tourist"))

    # ── 7. UI: что видит глава МВД в списке выдачи ──────────────────
    print("\n=== 7. Список статусов в выдаче (по праву) ===")
    for actor, who in ((CHIEF, "глава МВД"), (KEEPER, "Хранитель")):
        visible = [s for s in await get_all_statuses()
                   if await can_grant_status(actor, s)]
        names = sorted(s['name'] for s in visible)
        if who == "глава МВД":
            check("глава МВД видит ровно один статус — «Рекрут»",
                  names == ["Рекрут"])
        else:
            check(f"Хранитель видит все {len(names)} статусов (не урезан)",
                  len(names) == len(await get_all_statuses()) and len(names) > 0)

    # ── 8. кнопка статусов в админ-меню ─────────────────────────────
    print("\n=== 8. Кнопка «Статусы» в админ-меню ===")
    from bot.handlers.admin import perm_flags
    from keyboards.keyboards import admin_panel_keyboard

    f_chief = await perm_flags(CHIEF)
    check("perm_flags(глава МВД) отдаёт can_grant_citizen_status",
          f_chief.get('can_grant_citizen_status') is True)
    check("глава МВД видит кнопку «Статусы»",
          "admin:statuses" in str(admin_panel_keyboard(f_chief)))
    f_vice = await perm_flags(VICE)
    check("вице-доминус НЕ видит кнопку «Статусы»",
          "admin:statuses" not in str(admin_panel_keyboard(f_vice)))

    f_keeper = await perm_flags(KEEPER)
    check("perm_flags(Хранитель) отдаёт can_view_reports",
          f_keeper.get('can_view_reports') is True)
    check("perm_flags(Хранитель) отдаёт can_approve_reports",
          f_keeper.get('can_approve_reports') is True)
    kb = admin_panel_keyboard(f_keeper)
    check("Хранитель из роли видит «Отчёты» в меню", "admin:reports" in str(kb))

    # ── 9. проверка прав на каждом шаге выдачи ──────────────────────
    print("\n=== 9. Права проверяются на каждом callback'е ===")
    import inspect
    from bot.handlers import admin as A
    for name in ("status_grant_target", "status_revoke_target",
                 "status_revoke_pick", "status_grant_pick", "status_grant_more"):
        fn = getattr(A, name)
        src = inspect.getsource(fn)
        check(f"{name}: есть проверка прав",
              "can_view_status_panel" in src or "can_grant_status" in src)
    # А выбор статуса — точка, где раньше не было НИКАКОЙ проверки.
    src_pick = inspect.getsource(A.status_grant_pick)
    check("st_pick: проверяет конкретный статус (can_grant_status)",
          "can_grant_status" in src_pick)
    src_rev = inspect.getsource(A.status_revoke_pick)
    check("st_rev: проверяет конкретный статус (can_grant_status)",
          "can_grant_status" in src_rev)

    # ── 10. «Рекрут» не выдаётся за звание автоматически ────────────
    print("\n=== 10. Автовыдача по званиям не трогает гражданство ===")
    from config import RANK_STATUS_TAGS
    check("тег recruit НЕ закреплён за званием",
          "recruit" not in RANK_STATUS_TAGS.values())

    await close_db()
    print(f"\n=== SMOKE 116: {PASS} passed, {FAIL} failed ===")
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
