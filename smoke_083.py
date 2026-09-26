"""Smoke v0.15.24: статус доступа предметов (покупка/использование) и витрина магазина.

add_item принимает required_status; user_status_visibility_top возвращает границу
«текущий статус + одна ступень иерархии»; visible_items скрывает товары, требующие
статус на две ступени выше текущего и дальше (мотивация + «сюрприз» новинок),
туристы видят только сувениры.

Запуск: .venv\\Scripts\\python.exe smoke_083.py
"""
import asyncio
import os
import sys

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke083.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB

sys.path.insert(0, os.path.dirname(__file__))


async def run():
    from database.db import (
        init_db, close_db, add_user, add_item, get_item,
        grant_status, get_status_by_tag, user_status_visibility_top,
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

    # ── 1. add_item с required_status и без ──
    i_r = await add_item("Паёк Ветерана", "требует veteran", 100, 50, 1,
                         "consumable", 10, 1, heal=20, required_status="veteran")
    i_n = await add_item("Ремень", "без требований", 10, 5, 1,
                         "resource", 10, 1)
    row_r = await get_item(i_r)
    row_n = await get_item(i_n)
    check("add_item: required_status='veteran' сохранён", row_r and row_r['required_status'] == "veteran")
    check("add_item: по умолчанию None", row_n and row_n['required_status'] is None)

    # ── 2. user_status_visibility_top по лестнице статусов ──
    async def mk(uid, tag):
        await add_user(uid, f"t{uid}", f"Т{uid}", "")
        s = await get_status_by_tag(tag)
        await grant_status(uid, s['id'])
        return s

    uid_tourist = await mk(33001, "tourist")
    uid_recruit = await mk(33002, "recruit")
    uid_p2 = await mk(33003, "pilot2")
    uid_p1 = await mk(33004, "pilot1")
    uid_vet = await mk(33005, "veteran")
    uid_ace = await mk(33006, "ace")
    await add_user(33009, "nostatus", "Без статусов", "")

    check("турист → граница рекрут(1)", await user_status_visibility_top(33001) == 1)
    check("рекрут → граница pilot2(2)", await user_status_visibility_top(33002) == 2)
    check("pilot2 → граница pilot1(3)", await user_status_visibility_top(33003) == 3)
    check("pilot1 → граница veteran(5)", await user_status_visibility_top(33004) == 5)
    check("veteran → граница master_pilot(6)", await user_status_visibility_top(33005) == 6)
    check("ace → граница keeper(100)", await user_status_visibility_top(33006) == 100)
    check("нет статусов → None", await user_status_visibility_top(33009) is None)
    top_keeper = await mk(33007, "keeper")
    check("keeper → граница = его же уровень (вся витрина)", await user_status_visibility_top(33007) == top_keeper['sort_order'])

    # Товары на все ступени иерархии
    async def add_req(name, tag):
        return await add_item(name, "статусный", 10, 5, 1, "resource", 10, 1,
                              required_status=tag)

    ids = {
        None: i_n,
        "recruit": await add_req("Т-рекрут", "recruit"),
        "pilot2": await add_req("Т-pilot2", "pilot2"),
        "pilot1": await add_req("Т-pilot1", "pilot1"),
        "veteran": await add_req("Т-veteran", "veteran"),
        "master_pilot": await add_req("Т-master", "master_pilot"),
        "ace": await add_req("Т-ace", "ace"),
    }
    souv = await add_item("Сувенир Норда", "для всех", 5, 2, 1, "souvenirs", 10, 1)

    # ── 3. витрина магазина (бот.handlers.shop.visible_items) ──
    from bot.handlers.shop import visible_items
    items = [await get_item(i) for i in list(ids.values()) + [souv]]

    names = [x['name'] for x in await visible_items(33003, items)]  # игрок pilot2
    check("pilot2 видит без статуса", "Ремень" in names)
    check("pilot2 видит рекрута", "Т-рекрут" in names)
    check("pilot2 видит свой pilot2", "Т-pilot2" in names)
    check("pilot2 видит СЛЕДУЮЩИЙ pilot1", "Т-pilot1" in names)
    check("pilot2 НЕ видит veteran (+2 ступени)", "Т-veteran" not in names)
    check("pilot2 НЕ видит master_pilot", "Т-master" not in names)
    check("pilot2 НЕ видит ace", "Т-ace" not in names)
    check("пilot2 видит сувенир", "Сувенир Норда" in names)

    names_t = [x['name'] for x in await visible_items(33001, items)]  # турист
    check("турист видит только сувенир", names_t == ["Сувенир Норда"])

    names_k = [x['name'] for x in await visible_items(33007, items)]  # keeper
    check("keeper видит всю витрину (включая ace)", "Т-ace" in names_k and "Т-veteran" in names_k)

    names_n = [x['name'] for x in await visible_items(33009, items)]  # без статусов
    check("без статусов: виден товар без требований", "Ремень" in names_n)
    check("без статусов: скрыты все статусные", "Т-pilot2" not in names_n and "Т-recruit" not in names_n)

    # ── 4. разводка ──
    def source_has(path, needle):
        with open(path, "r", encoding="utf-8") as f:
            return needle in f.read()

    root = os.path.dirname(__file__)
    admin = os.path.join(root, "bot", "handlers", "admin.py")
    dbmod = os.path.join(root, "database", "db.py")
    check("db.py: helper user_status_visibility_top", source_has(
        dbmod, "def user_status_visibility_top("))
    check("admin.py: шаг addreq:", source_has(admin, 'F.data.startswith("addreq:")'))
    check("admin.py: required_status передаётся в add_item", source_has(
        admin, "required_status=data.get('required_status')"))
    check("admin.py: кнопка статус доступа в меню изменения", source_has(
        admin, "Статус доступа (покупка/использование)"))

    await close_db()
    print(f"\nSmoke 083: {passed} passed, {failed} failed")
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