"""Smoke v0.15.25: новые звания + авто-статусы вместе со званием.

Новая шкала RANKS (16 ступеней, до «Генерал Армии» 60000), авто-звания до
«Старший Лейтенант» (4040), выше — только назначением админа (свободный выбор
без порога очков); статусы (pilot2/pilot1/veteran/master_pilot/ace) выдаются
автоматически вместе со званием — при начислении войск (payout_reports), при
админ-назначении (promote_user_rank) и разовым бэкфиллом.

Запуск: .venv\\Scripts\\python.exe smoke_084.py
"""
import asyncio
import os
import sys

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke084.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB

sys.path.insert(0, os.path.dirname(__file__))


async def run():
    from config import (RANKS, AUTO_RANK_NAMES, RANK_STATUS_TAGS,
                        MAX_SELF_RANK_TROOPS, get_rank, get_effective_rank)
    from utils.formatters import get_rank_emoji
    from database.db import (
        init_db, close_db, add_user, get_db, get_user,
        backfill_rank_statuses, promote_user_rank, grant_status_for_rank,
        get_user_statuses, get_selected_status,
        add_report, approve_report, payout_reports,
        get_users_for_rank_promotion,
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

    # ── 1. Новая шкала RANKS ──
    check("RANKS: 16 ступеней", len(RANKS) == 16)
    check("Рядовой 100, Ефрейтор 350, Капрал 500", RANKS[1:4] ==
          [("Рядовой", 100), ("Ефрейтор", 350), ("Капрал", 500)])
    check("Сержант 850, СтСержант 1500, Лейтенант 2500", RANKS[4:7] ==
          [("Сержант", 850), ("Старший Сержант", 1500), ("Лейтенант", 2500)])
    check("Ст.Лейтенант 4040, Капитан 6000, Майор 8500", RANKS[7:10] ==
          [("Старший Лейтенант", 4040), ("Капитан", 6000), ("Майор", 8500)])
    check("Полковник 15000, Генерал-полковник 45000, Генерал Армии 60000",
          RANKS[11] == ("Полковник", 15000)
          and RANKS[14] == ("Генерал-полковник", 45000)
          and RANKS[-1] == ("Генерал Армии", 60000))
    check("AUTO_RANK_NAMES: 8 ступеней до Ст.Лейтенанта",
          len(AUTO_RANK_NAMES) == 8 and AUTO_RANK_NAMES[-1] == "Старший Лейтенант")
    check("MAX_SELF_RANK_TROOPS = 4040", MAX_SELF_RANK_TROOPS == 4040)
    check("RANK_STATUS_TAGS: 5 привязок", RANK_STATUS_TAGS == {
        "Ефрейтор": "pilot2", "Старший Сержант": "pilot1",
        "Старший Лейтенант": "veteran", "Майор": "master_pilot",
        "Полковник": "ace"})

    # ── 2. get_rank / get_effective_rank ──
    check("get_rank(349)=Рядовой, (350)=Ефрейтор", get_rank(349) == "Рядовой"
          and get_rank(350) == "Ефрейтор")
    check("get_rank(1500)=Ст.Сержант, (4040)=Ст.Лейтенант", get_rank(1500) == "Старший Сержант"
          and get_rank(4040) == "Старший Лейтенант")
    check("get_rank(60000)=Генерал Армии", get_rank(60000) == "Генерал Армии")
    check("get_effective_rank: кэп на Ст.Лейтенант без админ-звания",
          get_effective_rank(6000) == "Старший Лейтенант")
    check("get_effective_rank(6000,'Капитан')=Капитан", get_effective_rank(6000, "Капитан") == "Капитан")
    check("get_effective_rank(849)=Капрал, (850)=Сержант", get_effective_rank(849) == "Капрал"
          and get_effective_rank(850) == "Сержант")

    # ── 3. Бэкфилл по текущим войскам ──
    async def mk(uid, troops):
        await add_user(uid, f"r{uid}", f"R{uid}", "")
        conn = await get_db()
        await conn.execute("UPDATE users SET troops = ? WHERE user_id = ?", (troops, uid))
        await conn.commit()
        return uid

    async def has_tag(uid, tag):
        sts = await get_user_statuses(uid)
        return any(s['access_tag'] == tag for s in sts)

    async def sel_tag(uid):
        s = await get_selected_status(uid)
        return (s or {}).get('access_tag')

    u_p2 = await mk(34001, 350)
    u_p1 = await mk(34002, 1500)
    u_vet = await mk(34003, 4040)
    u_none = await mk(34004, 100)

    granted = await backfill_rank_statuses()
    check("бэкфилл: выдано 3 статуса", granted == 3)
    check("350 → Пилот 2 класса (pilot2)", await has_tag(u_p2, "pilot2"))
    check("pilot2 стал выбранным", await sel_tag(u_p2) == "pilot2")
    check("1500 → Пилот 1 класса (pilot1)", await has_tag(u_p1, "pilot1"))
    check("4040 → Ветеран (veteran)", await has_tag(u_vet, "veteran"))
    check("100 → званий-статусов НЕТ", not await has_tag(u_none, "pilot2")
          and not await has_tag(u_none, "pilot1") and not await has_tag(u_none, "veteran"))
    check("бэкфилл идемпотентен (повтор = 0)", await backfill_rank_statuses() == 0)

    # ── 4. Свободное назначение звания админом (без порога очков) ──
    await promote_user_rank(u_none, "Майор", 1)
    u = await get_user(u_none)
    check("админ: Майор при 100 войск (без порога)", u and u['promoted_rank'] == "Майор")
    check("Майор → Мастер-пилот (master_pilot)", await has_tag(u_none, "master_pilot"))
    check("master_pilot стал выбранным", await sel_tag(u_none) == "master_pilot")

    await promote_user_rank(u_none, "Полковник", 1)
    u = await get_user(u_none)
    check("админ: повышение до Полковника", u and u['promoted_rank'] == "Полковник")
    check("Полковник → Ас (ace) выбран", await has_tag(u_none, "ace")
          and await sel_tag(u_none) == "ace")
    check("master_pilot при этом сохранён", await has_tag(u_none, "master_pilot"))

    await promote_user_rank(u_p2, "Капитан", 1)
    check("Капитан: звание без привязки статуса",
          (await get_user(u_p2))['promoted_rank'] == "Капитан")

    # ── 5. Начисление войск через отчёты → авто-статус ──
    u_po = await mk(34005, 0)
    rid, _ = await add_report(u_po, "f", 4040)
    credited = await approve_report(rid, 0, 4040)
    check("отчёт одобрен на 4040", credited == 4040)
    await payout_reports()
    u_po_row = await get_user(u_po)
    check("payout: войска 4040", u_po_row and u_po_row['troops'] == 4040)
    check("payout: авто-выдан Ветеран (veteran) и выбран",
          await has_tag(u_po, "veteran") and await sel_tag(u_po) == "veteran")

    # ── 6. Список кандидатов на админское звание ──
    await mk(34006, 6000)
    await mk(34007, 15000)
    cands = await get_users_for_rank_promotion()
    cand_by_uid = {c['user_id']: c for c in cands}
    check("6000 без звания → кандидат, next=Капитан",
          cand_by_uid.get(34006, {}).get('next_rank') == "Капитан")
    check("15000 без звания → кандидат, next=Полковник",
          cand_by_uid.get(34007, {}).get('next_rank') == "Полковник")
    check("4040 (Ст.Лейтенант) НЕ кандидат", 34003 not in cand_by_uid)
    check("назначенные админом исключены", 34004 not in cand_by_uid and 34002 not in cand_by_uid)

    # ── 7. Эмодзи новых званий ──
    check("эмодзи Ефрейтора не дефолт", get_rank_emoji("Ефрейтор") != "👤")
    check("эмодзи Ст.Лейтенанта (📯)", "📯" in get_rank_emoji("Старший Лейтенант"))
    check("эмодзи Генерал Армии не дефолт", get_rank_emoji("Генерал Армии") != "👤")

    # ── 8. grant_status_for_rank двойной вызов ──
    check("повторная выдача того же статуса → None",
          await grant_status_for_rank(u_p2, "Капитан") is None
          and await grant_status_for_rank(34099, "Майор") is None)

    await close_db()
    print(f"\nSmoke 084: {passed} passed, {failed} failed")
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