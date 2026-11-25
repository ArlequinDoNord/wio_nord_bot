"""Smoke v0.43.32: история перевыдачи паспортов КГБ и архив.

Проверяет:
1. Первая выдача истории не создаёт.
2. Перевыдача кладёт в passport_history только серию, номер и дату выдачи старого паспорта.
3. get_passport_map отмечает пилотов с паспортом; get_passport_archive — все текущие паспорта.
4. Ключи архива и отметок есть в ru и en.
5. Список пилотов с отметкой показывает серию у пилота с паспортом.

Запуск: .venv\\Scripts\\python.exe smoke_246.py
"""
import asyncio
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke246.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB
os.environ["ADMIN_IDS"] = "446001"

sys.path.insert(0, os.path.dirname(__file__))

HEAD, P1, P2, P3 = 883001, 883002, 883003, 883004


def passport(series, number, issue_date, name):
    return {
        "series": series, "number": number, "full_name": name, "position": "Пилот",
        "rank": "Рядовой", "sex": "m", "marital_status": "нет", "birth_date": "01.01.1990",
        "issue_date": issue_date, "distinguishing_marks": "нет", "photo_file_id": None,
    }


async def run():
    from database.db import (init_db, close_db, add_user, get_passport, issue_passport,
                             get_passport_history, get_passport_map, get_passport_archive,
                             get_db)
    from utils.localization import STRINGS

    await init_db()
    passed = failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
        else:
            failed += 1
            print(f"  FAIL: {name}")

    try:
        for uid in (HEAD, P1, P2, P3):
            await add_user(uid, f"kgbh{uid}", "Пилот", f"N{uid}")

        # 1. Первая выдача — истории нет
        await issue_passport(P1, passport("1111", "100001", "01.01.2026", "Первый"), HEAD)
        check("первая выдача не создаёт историю", await get_passport_history(P1) == [])

        # 2. Перевыдача — старый паспорт в истории (серия, номер, дата)
        await issue_passport(P1, passport("2222", "100002", "05.02.2026", "Первый"), HEAD)
        hist = await get_passport_history(P1)
        check("перевыдача пишет одну запись в историю", len(hist) == 1)
        check("в истории старая серия", hist and hist[0]["series"] == "1111")
        check("в истории старый номер", hist and hist[0]["number"] == "100001")
        check("в истории старая дата выдачи", hist and hist[0]["issue_date"] == "01.01.2026")
        conn = await get_db()
        cols = [r["name"] for r in await (await conn.execute("PRAGMA table_info(passport_history)")).fetchall()]
        check("в истории нет ФИО/должности/фото (только серия, номер, дата)",
              not any(c in cols for c in ("full_name", "position", "rank", "photo_file_id")))
        cur = await get_passport(P1)
        check("текущий паспорт — новый", cur["series"] == "2222")

        # 3. Отметки и архив
        await issue_passport(P2, passport("3333", "100003", "10.02.2026", "Второй"), HEAD)
        pmap = await get_passport_map()
        check("в отметках есть пилот с паспортом", P1 in pmap and P2 in pmap)
        check("в отметках нет пилота без паспорта", P3 not in pmap)
        check("серия в отметках правильная", pmap[P2]["series"] == "3333")
        archive = await get_passport_archive()
        uids = [r["user_id"] for r in archive]
        check("архив содержит текущие паспорта", P1 in uids and P2 in uids and P3 not in uids)
        check("в архиве только одна строка на пилота", len(uids) == len(set(uids)))

        # 4. Тексты ru/en
        keys = ("kgb.btn_archive", "kgb.has_passport_mark", "kgb.archive_title",
                "kgb.archive_empty", "kgb.archive_card", "kgb.archive_history_head",
                "kgb.archive_history_line", "kgb.archive_no_history")
        check("все ключи архива есть в ru и en",
              all(k in STRINGS and "ru" in STRINGS[k] and "en" in STRINGS[k] for k in keys))

        # 5. Отметка серии в подписи
        from utils.localization import t
        check("ru: отметка с серией", t("kgb.has_passport_mark", series="2222") == "✅ 2222")

        # 6. Доступ к архиву: владелец (ADMIN_IDS) да, обычный пилот нет
        from bot.handlers.kgb import can_see_passport_archive
        check("владелец видит архив", await can_see_passport_archive(446001) is True)
        check("обычный пилот архив не видит", await can_see_passport_archive(P1) is False)
    finally:
        await close_db()
        if os.path.exists(_TEST_DB):
            os.remove(_TEST_DB)

    print(f"\nSmoke 246: {passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)


asyncio.run(run())
