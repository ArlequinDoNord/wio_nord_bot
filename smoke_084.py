"""Smoke v0.15.25: новые звания + авто-статусы вместе со званием.

Новая шкала RANKS (16 ступеней, до «Генерал Армии» 60000), авто-звания до
«Старший Лейтенант» (4040), выше — только назначением админа (свободный выбор
без порога очков); статусы (pilot2/pilot1/veteran/master_pilot/ace) выдаются
автоматически вместе со званием — при начислении войск (payout_reports), при
админ-назначении (promote_user_rank) и разовым бэкфиллом. С v0.18.14 выдача
кумулятивная: положены статусы за текущее звание и за все пройденные ступени.

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
        set_report_daily_pay_cap,
        get_users_for_rank_promotion,
        get_status_by_tag, grant_status,
    )

    await init_db()
    passed = 0
    failed = 0

    def check(name, cond, extra=""):
        nonlocal passed, failed
        if cond:
            passed += 1
        else:
            failed += 1
            print(f"  FAIL: {name}{(' — ' + str(extra)) if extra else ''}")

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

    # ── 3b. Кумулятивная выдача: пройденные ступени не теряются ──
    u_cum = await mk(34010, 900)    # Сержант: прошёл Ефрейтора, до Ст.Сержанта далеко
    u_cum2 = await mk(34011, 1700)  # Ст.Сержант: положены обе пилотские ступени
    granted = await backfill_rank_statuses()
    check("Сержант (900) → Пилот 2 класса (pilot2)", await has_tag(u_cum, "pilot2"))
    check("Сержант (900) НЕ Пилот 1 класса", not await has_tag(u_cum, "pilot1"))
    check("Ст.Сержант (1700) → pilot2 и pilot1",
          await has_tag(u_cum2, "pilot2") and await has_tag(u_cum2, "pilot1"))
    check("кумулятивный бэкфилл: выбрано 2 игрока", granted == 2)

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
    # Суточный лимит оплаты (v0.15.34) по умолчанию 4000, поэтому для проверки
    # начисления 4040 лимит временно снимаем; ниже отдельная проверка, что лимит режет.
    await set_report_daily_pay_cap(0)
    u_po = await mk(34005, 0)
    rid, _ = await add_report(u_po, "f", 4040)
    credited = await approve_report(rid, 0, 4040)
    check("отчёт одобрен на 4040", credited == 4040)
    await payout_reports()
    u_po_row = await get_user(u_po)
    check("payout: войска 4040", u_po_row and u_po_row['troops'] == 4040)
    check("payout: авто-выдан Ветеран (veteran) и выбран",
          await has_tag(u_po, "veteran") and await sel_tag(u_po) == "veteran")

    # Лимит по умолчанию (4000) режет «всё накопленное» в первом отчёте
    await set_report_daily_pay_cap(4000)
    u_cap = await mk(34008, 0)
    rid_cap, credited_cap = await add_report(u_cap, "f", 999999, 7045)
    check("суточный лимит 4000: первый отчёт 999999 → 4000", credited_cap == 4000)
    check("одобренный отчёт в пределах лимита платится полностью",
          await approve_report(rid_cap, 0) == 4000)
    await payout_reports()
    u_cap_row = await get_user(u_cap)
    check("payout по лимиту: 4000", u_cap_row and u_cap_row['troops'] == 4000)

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

    # ── 9. Боевой урон по статусу (RANK_DAMAGE_TIERS) ──
    from config import PILOT_NO_WEAPON_DMG, RANK_DAMAGE_TIERS
    from database.db import get_pilot_base_damage

    # Урон считается ПО ЗВАНИЮ, а не по выданным статусам: у Хранителя
    # (sort_order 100) user_has_status_tag считает «есть» любой статус.

    # u_vet = 4040 войск → «Старший Лейтенант» → veteran (2–4).
    check("урон по званию «Ст. Лейтенант» = (2, 4)",
          await get_pilot_base_damage(u_vet) == (2, 4),
          await get_pilot_base_damage(u_vet))
    # u_p1 = 1500 → «Старший Сержант» → pilot1 (1–3).
    check("урон по званию «Ст. Сержант» = (1, 3)",
          await get_pilot_base_damage(u_p1) == (1, 3),
          await get_pilot_base_damage(u_p1))

    # Повышение админом пересчитывает урон сразу.
    await promote_user_rank(u_vet, "Полковник", 1)
    check("после повышения до Полковника урон = (4, 8)",
          await get_pilot_base_damage(u_vet) == (4, 8),
          await get_pilot_base_damage(u_vet))

    # Хранитель бьёт по своему званию: статус «Хранитель» не даёт бонуса.
    keeper = await get_status_by_tag("keeper")
    await grant_status(u_vet, keeper['id'], 1)
    check("хранитель с званием Полковника всё равно бьёт (4, 8)",
          await get_pilot_base_damage(u_vet) == (4, 8),
          await get_pilot_base_damage(u_vet))
    check("в таблице урона нет keeper", "keeper" not in RANK_DAMAGE_TIERS)

    # Турист (ещё без звания) — почти безвреден.
    u_t = await mk(34050, 0)
    tourist = await get_status_by_tag("tourist")
    await grant_status(u_t, tourist['id'], 1)
    check("турист → (0, 1)",
          await get_pilot_base_damage(u_t) == (0, 1),
          await get_pilot_base_damage(u_t))
    check("без звания урон = запасные (1, 1)",
          await get_pilot_base_damage(await mk(34051, 0)) == (1, 1))
    check("запасной урон = (1, 1)", tuple(PILOT_NO_WEAPON_DMG) == (1, 1))

    # Промежуточные звания без статуса тянутся к предыдущей ступени урона.
    # Выше «Ст. Лейтенанта» авто-звание не растёт (get_effective_rank капнет),
    # поэтому по войскам дальше не прыгнуть — только через promote_user_rank.
    for troops, expected, label in ((100, (1, 1), "Рядовой"),
                                    (350, (1, 2), "Ефрейтор"),
                                    (500, (1, 2), "Капрал"),
                                    (850, (1, 2), "Сержант"),
                                    (1500, (1, 3), "Ст. Сержант"),
                                    (2500, (1, 3), "Лейтенант"),
                                    (6000, (2, 4), "Капитан"),
                                    (22000, (2, 4), "Генерал-майор (капнет)")):
        u_x = await mk(34060 + troops, troops)
        check(f"{label} ({troops} войск) → {expected[0]}–{expected[1]}",
              await get_pilot_base_damage(u_x) == expected,
              await get_pilot_base_damage(u_x))

    # Генералы получают максимум только через админское повышение.
    for rank, expected in (("Подполковник", (3, 5)), ("Майор", (3, 5)),
                           ("Генерал Армии", (4, 8))):
        u_y = await mk(34100 + len(rank), 11000)
        await promote_user_rank(u_y, rank, 1)
        check(f"админское звание «{rank}» → {expected[0]}–{expected[1]}",
              await get_pilot_base_damage(u_y) == expected,
              await get_pilot_base_damage(u_y))
    check("в таблице урона нет keeper", "keeper" not in RANK_DAMAGE_TIERS)
    check("запасной урон без статусов = (1, 1)",
          tuple(PILOT_NO_WEAPON_DMG) == (1, 1))

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