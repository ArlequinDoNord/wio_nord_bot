# -*- coding: utf-8 -*-
"""Smoke 168 — Клан-холл Фаза 7.5: иерархия клана и права доступа.

1. Схема: колонка clan_members.role, дефолт 'member'.
2. Бэкфилл: главы кланов получают role='leader', синхронизация с clans.leader_id.
3. Роли CLAN_ROLES: leader/seneschal/banner/elder/member; должности эксклюзивные.
4. Права: can_manage_clan_hall (leader+seneschal), can_harvest_clan_garden
   (leader+seneschal), can_withdraw_clan_storage (только leader).
5. Смена главы: set_clan_leader перекидывает роль leader.
6. add_clan_member: новый член всегда 'member'.
7. UI: кнопка «⚜ Иерархия клана» в карточке, экран иерархии, назначение роли.
"""
import asyncio
import os
import sys

os.environ["DATABASE_PATH"] = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "_test_smoke168.db")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def main():
    passed = failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
            print(f"  OK  {name}")
        else:
            failed += 1
            print(f"  FAIL: {name}")

    import database.db as db
    import config
    from database.db import (
        init_db, seed_default_items, add_user, create_clan, add_clan_member,
        set_clan_leader, get_clan_member_role, set_clan_member_role,
        get_clan_member_roles,
        can_manage_clan_hall, can_withdraw_clan_storage, can_harvest_clan_garden,
        get_clan, remove_clan_member, _backfill_clan_member_roles, close_db,
    )

    await init_db()
    await seed_default_items()

    print("\n1. Схема и дефолты ролей")
    conn = await db.get_db()
    cur = await conn.execute("PRAGMA table_info(clan_members)")
    cols = {r['name'] for r in await cur.fetchall()}
    check("колонка role в clan_members", 'role' in cols)

    check("CLAN_ROLES: 5 ролей", len(config.CLAN_ROLES) == 5)
    check("порядок ролей", config.CLAN_ROLE_ORDER ==
          ("leader", "seneschal", "banner", "elder", "member"))

    LEADER, SEN, BAN, ELD, MEMBER, NEW = (168101, 168102, 168103, 168104, 168105, 168106)
    for uid, nm in ((LEADER, 'A'), (SEN, 'S'), (BAN, 'B'), (ELD, 'E'),
                    (MEMBER, 'M'), (NEW, 'N')):
        await add_user(uid, nm.lower(), nm, "")

    cid = await create_clan("clan", "TT", "Иерархия", LEADER)
    await add_clan_member(cid, LEADER)
    await set_clan_leader(cid, LEADER)
    for u in (SEN, BAN, ELD, MEMBER):
        await add_clan_member(cid, u)

    check("глава получил роль leader",
          await get_clan_member_role(cid, LEADER) == 'leader')
    check("новый член — member", await get_clan_member_role(cid, MEMBER) == 'member')

    print("\n2. Назначение должностей")
    ok = await set_clan_member_role(cid, SEN, 'seneschal')
    check("назначен seneschal", ok and await get_clan_member_role(cid, SEN) == 'seneschal')
    ok = await set_clan_member_role(cid, BAN, 'banner')
    check("назначен banner", ok and await get_clan_member_role(cid, BAN) == 'banner')
    ok = await set_clan_member_role(cid, ELD, 'elder')
    check("назначен elder", ok and await get_clan_member_role(cid, ELD) == 'elder')

    print("\n3. Эксклюзивность должностей")
    ok = await set_clan_member_role(cid, MEMBER, 'banner')
    check("второй banner назначен", ok and await get_clan_member_role(cid, MEMBER) == 'banner')
    check("прежний banner сброшен в member",
          await get_clan_member_role(cid, BAN) == 'member')
    ok = await set_clan_member_role(cid, BAN, 'banner')  # вернуть

    ok = await set_clan_member_role(cid, MEMBER, 'boss')
    check("неверная роль отклонена", ok is False)
    ok = await set_clan_member_role(cid, NEW, 'seneschal')
    check("не-член отклонён", ok is False)
    ok = await set_clan_member_role(cid, MEMBER, 'leader')
    check("leader через set_clan_member_role запрещён (не сработал)",
          await get_clan_member_role(cid, MEMBER) != 'leader')

    print("\n4. Права по ролям")
    check("глава может управлять холлом", await can_manage_clan_hall(cid, LEADER) is True)
    check("сенешаль может управлять холлом", await can_manage_clan_hall(cid, SEN) is True)
    check("знаменосец НЕ может управлять холлом",
          await can_manage_clan_hall(cid, BAN) is False)
    check("старшина НЕ может управлять холлом",
          await can_manage_clan_hall(cid, ELD) is False)
    check("член НЕ может управлять холлом", await can_manage_clan_hall(cid, MEMBER) is False)
    check("глава может собирать урожай", await can_harvest_clan_garden(cid, LEADER) is True)
    check("сенешаль может собирать урожай", await can_harvest_clan_garden(cid, SEN) is True)
    check("член НЕ может собирать урожай", await can_harvest_clan_garden(cid, MEMBER) is False)
    check("глава может выводить со склада", await can_withdraw_clan_storage(cid, LEADER) is True)
    check("сенешаль НЕ может выводить со склада",
          await can_withdraw_clan_storage(cid, SEN) is False)
    check("чужак не управляет", await can_manage_clan_hall(cid, NEW) is False)

    print("\n5. Смена главы перекидывает роль")
    check("перед сменой глава — leader",
          await get_clan_member_role(cid, LEADER) == 'leader')
    await set_clan_leader(cid, SEN)
    check("старый глава больше не leader",
          await get_clan_member_role(cid, LEADER) == 'member')
    check("новый глава — leader", await get_clan_member_role(cid, SEN) == 'leader')
    clan = await get_clan(cid)
    check("clans.leader_id обновлён", clan['leader_id'] == SEN)

    print("\n6. Бэкфилл правит расинхрон")
    conn2 = await db.get_db()
    await conn2.execute(
        "UPDATE clan_members SET role = 'member' WHERE clan_id = ? AND user_id = ?",
        (cid, SEN))
    await conn2.commit()
    check("роль рассинхронизирована", await get_clan_member_role(cid, SEN) == 'member')
    await _backfill_clan_member_roles()
    check("бэкфилл вернул leader", await get_clan_member_role(cid, SEN) == 'leader')

    print("\n7. Карта ролей")
    rmap = await get_clan_member_roles(cid)
    check("карта ролей консистентна",
          rmap.get(SEN) == 'leader' and rmap.get(LEADER) == 'member')

    print("\n8. Удаление члена снимает роль")
    await remove_clan_member(cid, ELD)
    check("роль удалённого пустая", await get_clan_member_role(cid, ELD) == '')
    rmap = await get_clan_member_roles(cid)
    check("elder свободен в карте", 'elder' not in [rmap.get(u) for u in rmap
                                                    if u != ELD] or rmap.get(ELD) is None)

    print(f"\nИТОГО: {passed} passed, {failed} failed")
    await close_db()
    if failed:
        sys.exit(1)


try:
    asyncio.run(main())
except Exception:
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    try:
        os.remove(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "_test_smoke168.db"))
    except OSError:
        pass
