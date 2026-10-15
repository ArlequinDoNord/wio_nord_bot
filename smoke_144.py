"""Smoke 144 — починка записей с битой кодировкой (mojibake).

Проверяет repair_mojibake_entities() (database/db.py):
  1. Предмет с битым именем и корректным двойником → слияние: инвентарь
     переносится (количества суммируются, если есть оба), битая строка удаляется,
     корректный двойник остаётся.
  2. Предмет с битым именем без двойника → имя/описание чинятся на месте.
  3. Награда с битым именем и корректным двойником → user_awards переносятся,
     битая награда удаляется.
  4. Идемпотентность: повторный вызов ничего не меняет.
  5. Проверка _demojibake: корректный русский текст не «чинится» (нет ложных
     срабатываний).

Запуск: .venv\\Scripts\\python.exe smoke_144.py
"""
import asyncio
import os
import sys

_TEST_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_test_smoke144.db")
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


def moji(s: str) -> str:
    return s.encode("utf-8").decode("cp1251")


async def main():
    import config
    config.DB_PATH = _TEST_DB
    import database.db as db
    db.DB_PATH = _TEST_DB

    from database.db import (
        init_db, close_db, add_user, add_item, add_inventory_item,
        get_inventory_item, get_item_by_name, create_award, grant_award,
        get_all_awards, repair_mojibake_entities, _demojibake,
    )

    await init_db()

    print("\n1. _demojibake: корректный текст не трогаем")
    check("корректное имя → None", _demojibake("Буклет туриста") is None)
    check("пустое → None", _demojibake("") is None)
    check("ASCII → None", _demojibake("Booklet") is None)
    check("битый текст распознан", _demojibake(moji("Буклет туриста")) == "Буклет туриста")

    await add_user(144001, "u1", "U", "1")
    await add_user(144002, "u2", "U", "2")

    print("\n2. Слияние предмета-дубля (инвентарь суммируется)")
    good = await add_item(name="Буклет туриста", description="Печатная карта.",
                          price=1, sell_price=0, rarity=1, category="souvenirs",
                          stock=-1, added_by=0)
    good_item = await get_item_by_name("Буклет туриста")
    good_id = good_item["id"]
    await add_item(name=moji("Буклет туриста"), description=moji("Печатная карта."),
                   price=1, sell_price=0, rarity=1, category="souvenirs",
                   stock=-1, added_by=0)
    bad_item = await get_item_by_name(moji("Буклет туриста"))
    bad_id = bad_item["id"]
    check("корректный и битый предметы существуют", good_id and bad_id and good_id != bad_id)

    # u1 владеет и корректным (x2), и битым (x3) → должно стать x5.
    await add_inventory_item(144001, good_id, 2)
    await add_inventory_item(144001, bad_id, 3)
    # u2 владеет только битым (x1) → должен переехать на корректный.
    await add_inventory_item(144002, bad_id, 1)

    report = await repair_mojibake_entities()
    check("отчёт: слияние предмета засчитано", report["items_merged"] >= 1)
    check("битый предмет удалён", await get_item_by_name(moji("Буклет туриста")) is None)
    check("корректный предмет на месте", await get_item_by_name("Буклет туриста") is not None)
    inv1 = await get_inventory_item(144001, good_id)
    inv2 = await get_inventory_item(144002, good_id)
    check("u1: количества сложились (2+3=5)", inv1 and inv1["quantity"] == 5)
    check("u2: битый переехал на корректный (1)", inv2 and inv2["quantity"] == 1)

    print("\n3. Чиним на месте предмет без двойника")
    await add_item(name=moji("Уникальная вещь"), description=moji("Описание вещи."),
                   price=5, sell_price=1, rarity=1, category="misc",
                   stock=-1, added_by=0)
    report = await repair_mojibake_entities()
    check("отчёт: починка на месте засчитана", report["items_fixed"] >= 1)
    check("имя восстановлено", await get_item_by_name("Уникальная вещь") is not None)
    check("битого имени больше нет", await get_item_by_name(moji("Уникальная вещь")) is None)

    print("\n4. Слияние награды-дубля")
    ok1, aid_good = await create_award("Опытный турист", "Знак гостя.")
    await create_award(moji("Опытный турист"), moji("Знак гостя."))
    awards = await get_all_awards()
    aid_bad = next(a["id"] for a in awards if a["name"] == moji("Опытный турист"))
    await grant_award(144001, aid_bad)
    report = await repair_mojibake_entities()
    check("отчёт: слияние награды засчитано", report["awards_merged"] >= 1)
    names = [a["name"] for a in await get_all_awards()]
    check("битая награда удалена", moji("Опытный турист") not in names)
    check("корректная награда на месте", "Опытный турист" in names)
    from database.db import get_user_awards
    ua = await get_user_awards(144001)
    check("выдача переехала на корректную награду",
          any(a["award_id"] == aid_good for a in ua))

    print("\n5. Идемпотентность")
    again = await repair_mojibake_entities()
    check("повторный вызов ничего не меняет",
          all(v == 0 for v in again.values()))

    await close_db()
    print(f"\nSmoke 144: {PASS} passed, {FAIL} failed")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except SystemExit:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"SMOKE ERROR: {e}")
        sys.exit(2)
