"""Smoke 158 — клановый склад (первый блок «Клан-холла»).

Проверяет:
1. Таблицы `clan_storage` и `clan_build_contrib` создаются `init_db()`.
2. `add_clan_storage` / `get_clan_storage` / `get_clan_storage_qty`:
   накопление, нулевые строки не показываются, отрицательный остаток режется.
3. `donate_to_clan_storage`: перенос из личного инвентаря на склад, журнал
   вкладов, запрет не-ресурсов, нулевых/отрицательных и нехватки.
4. `take_clan_storage`: списание при достатке, отказ при нехватке.
5. `delete_clan` чистит склад и журнал.
6. Хендлеры: экран склада, выбор ресурса, экран вклада, «+1/Всё»,
   текст вкладов, отказ не-члену клана.
7. В карточке клана у члена есть кнопка «Склад клана», у постороннего — нет.
   Склад живёт в клан-холле, поэтому тест включает `config.CLAN_HALL_ENABLED`.

Запуск: .venv\\Scripts\\python.exe smoke_158.py
"""
import asyncio
import os
import sys

_TEST_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_test_smoke158.db")
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


class FakeMessage:
    def __init__(self):
        self.photo = None
        self.text = None
        self.kb = None
        self.deleted = False

    async def edit_text(self, text, parse_mode=None, reply_markup=None):
        self.text, self.kb = text, reply_markup

    async def edit_caption(self, caption, parse_mode=None, reply_markup=None):
        self.text, self.kb = caption, reply_markup

    async def answer(self, text, parse_mode=None, reply_markup=None):
        self.text, self.kb = text, reply_markup
        return self

    async def delete(self):
        self.deleted = True


class FakeUser:
    def __init__(self, uid):
        self.id = uid


class FakeCallback:
    def __init__(self, uid, data=""):
        self.from_user = FakeUser(uid)
        self.message = FakeMessage()
        self.data = data
        self.alerts = []

    async def answer(self, text=None, *a, **k):
        self.alerts.append(text)
        return True


def cbs(kb):
    return [b.callback_data for row in kb.inline_keyboard for b in row]


async def main():
    import config
    config.DB_PATH = _TEST_DB
    # Склад клана живёт в клан-холле и скрыт общим флагом — для тестов включаем.
    config.CLAN_HALL_ENABLED = True
    import database.db as db
    db.DB_PATH = _TEST_DB
    from database.db import (
        init_db, close_db, get_db, add_user, add_item, create_clan,
        add_clan_member, set_clan_leader, delete_clan,
        add_inventory_item, get_inventory_item,
        add_clan_storage, get_clan_storage, get_clan_storage_qty,
        take_clan_storage, donate_to_clan_storage, get_clan_contributions,
    )
    from bot.handlers import clan_hall, clans

    await init_db()

    LEADER, MEMBER, OUTSIDER = 158001, 158002, 158003
    for uid, nm in ((LEADER, "leader"), (MEMBER, "member"), (OUTSIDER, "outsider")):
        await add_user(uid, nm, nm.title(), "")

    clan_id = await create_clan("clan", "Тестовый клан", "", LEADER)
    await set_clan_leader(clan_id, LEADER)
    await add_clan_member(clan_id, LEADER)
    await add_clan_member(clan_id, MEMBER)
    party_id = await create_clan("party", "Тестовая партия", "", LEADER)
    await add_clan_member(party_id, LEADER)

    wood = await add_item("Доска-158", "тест", 34, 17, 1, "resource", -1, LEADER)
    ore = await add_item("Руда-158", "тест", 40, 20, 1, "resource", -1, LEADER)
    potion = await add_item("Зелье-158", "тест", 50, 25, 1, "consumable", -1, LEADER)

    try:
        print("\n1. Таблицы и хелперы склада")
        conn = await get_db()
        cur = await conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' "
            "AND name IN ('clan_storage','clan_build_contrib')")
        tables = {r['name'] for r in await cur.fetchall()}
        check("обе таблицы созданы", tables == {"clan_storage", "clan_build_contrib"})

        await add_clan_storage(clan_id, wood, 5)
        check("накопление", await get_clan_storage_qty(clan_id, wood) == 5)
        check("get_clan_storage отдаёт имя", any(
            r['item_id'] == wood and r['name'] == "Доска-158"
            for r in await get_clan_storage(clan_id)))
        await add_clan_storage(clan_id, wood, 3)
        check("накопительно (5+3=8)", await get_clan_storage_qty(clan_id, wood) == 8)
        await add_clan_storage(clan_id, wood, -20)
        check("отрицательный остаток режется до 0",
              await get_clan_storage_qty(clan_id, wood) == 0)
        check("нулевые строки не показываются",
              not any(r['item_id'] == wood for r in await get_clan_storage(clan_id)))
        await add_clan_storage(clan_id, wood, 0)
        check("нулевая дельта — no-op", await get_clan_storage_qty(clan_id, wood) == 0)

        print("\n2. Пожертвования из инвентаря")
        await add_inventory_item(MEMBER, wood, 10)
        ok = await donate_to_clan_storage(clan_id, MEMBER, wood, 4)
        inv = await get_inventory_item(MEMBER, wood)
        check("вклад прошёл", ok is True)
        check("склад пополнен на 4", await get_clan_storage_qty(clan_id, wood) == 4)
        check("инвентарь уменьшен (10-4=6)", inv and inv['quantity'] == 6)
        contrib = await get_clan_contributions(clan_id)
        check("вклад записан в журнал",
              len(contrib) == 1 and contrib[0]['user_id'] == MEMBER
              and contrib[0]['qty'] == 4 and contrib[0]['item_name'] == "Доска-158")

        ok = await donate_to_clan_storage(clan_id, MEMBER, wood, 6)
        check("второй вклад на всё", ok is True)
        check("строка инвентаря удалена", await get_inventory_item(MEMBER, wood) is None)
        check("склад 10", await get_clan_storage_qty(clan_id, wood) == 10)

        before = await get_clan_storage_qty(clan_id, wood)
        ok = await donate_to_clan_storage(clan_id, MEMBER, wood, 1)
        check("нехватка в инвентаре — отказ",
              ok is False and await get_clan_storage_qty(clan_id, wood) == before)

        await add_inventory_item(MEMBER, ore, 5)
        check("нулевой вклад — отказ",
              await donate_to_clan_storage(clan_id, MEMBER, ore, 0) is False)
        check("отрицательный вклад — отказ",
              await donate_to_clan_storage(clan_id, MEMBER, ore, -3) is False)

        await add_inventory_item(MEMBER, potion, 3)
        check("не-ресурс — отказ",
              await donate_to_clan_storage(clan_id, MEMBER, potion, 1) is False)
        check("не-ресурс не попал на склад",
              await get_clan_storage_qty(clan_id, potion) == 0)
        check("не-ресурс не списан из инвентаря",
              (await get_inventory_item(MEMBER, potion))['quantity'] == 3)

        print("\n3. Списание со склада")
        check("списание 3 из 10", await take_clan_storage(clan_id, wood, 3) is True
              and await get_clan_storage_qty(clan_id, wood) == 7)
        check("списание больше остатка — отказ",
              await take_clan_storage(clan_id, wood, 100) is False
              and await get_clan_storage_qty(clan_id, wood) == 7)
        check("списание нуля — отказ", await take_clan_storage(clan_id, wood, 0) is False)

        print("\n4. Журнал вкладов")
        text = clan_hall.build_contrib_text(
            await db.get_clan(clan_id), await get_clan_contributions(clan_id))
        check("в тексте журнала есть имя вкладчика", "Member" in text)
        check("в тексте журнала есть предмет и количество",
              "Доска-158" in text and "× 4" in text)
        empty_text = clan_hall.build_contrib_text(
            await db.get_clan(clan_id), [])
        check("пустой журнал — понятный текст", "Пока никто" in empty_text)

        print("\n5. Экраны хендлера")
        clan = await db.get_clan(clan_id)
        storage_text = clan_hall.build_clan_storage_text(
            clan, await get_clan_storage(clan_id))
        check("экран склада: название клана", "Тестовый клан" in storage_text)
        check("экран склада: строка ресурса", "Доска-158" in storage_text)
        check("экран склада: итог единиц", "Всего единиц: <b>7</b>" in storage_text)
        empty_storage = clan_hall.build_clan_storage_text(clan, [])
        check("пустой склад: подсказка", "Склад пуст" in empty_storage)

        cb = FakeCallback(MEMBER, f"clanh:storage:{clan_id}")
        await clan_hall.clan_storage_cb(cb)
        c = cbs(cb.message.kb)
        check("склад: кнопка вклада", f"clanh:donate:{clan_id}" in c)
        check("склад: кнопка журнала", f"clanh:log:{clan_id}" in c)
        check("склад: возврат в клан", f"clans:view:{clan_id}" in c)

        cb = FakeCallback(MEMBER, f"clanh:donate:{clan_id}")
        await clan_hall.clan_donate_cb(cb)
        c = cbs(cb.message.kb)
        check("выбор ресурса: есть руда", f"clanh:item:{clan_id}:{ore}" in c)
        check("выбор ресурса: нет не-ресурса",
              f"clanh:item:{clan_id}:{potion}" not in c)
        check("выбор ресурса: возврат к складу", f"clanh:storage:{clan_id}" in c)

        cb = FakeCallback(MEMBER, f"clanh:item:{clan_id}:{ore}")
        await clan_hall.clan_donate_item_cb(cb)
        c = cbs(cb.message.kb)
        check("экран предмета: +1", f"clanh:give:{clan_id}:{ore}:1" in c)
        check("экран предмета: всё", f"clanh:give:{clan_id}:{ore}:all" in c)
        check("экран предмета: видно остаток", "У тебя: <b>5</b>" in cb.message.text)

        cb = FakeCallback(MEMBER, f"clanh:give:{clan_id}:{ore}:all")
        await clan_hall.clan_donate_give_cb(cb)
        check("give all: склад пополнен", await get_clan_storage_qty(clan_id, ore) == 5)
        check("give all: инвентарь пуст",
              await get_inventory_item(MEMBER, ore) is None)
        check("give all: alert об успехе",
              any(a and "Внесено" in a for a in cb.alerts))
        c = cbs(cb.message.kb)
        check("после нуля — возврат к выбору ресурса",
              f"clanh:storage:{clan_id}" in c)

        print("\n6. Доступ")
        cb = FakeCallback(OUTSIDER, f"clanh:storage:{clan_id}")
        await clan_hall.clan_storage_cb(cb)
        check("посторонний не видит склад",
              cb.message.kb is None and any(
                  a and "только членам" in a for a in cb.alerts))

        cb = FakeCallback(LEADER, f"clanh:storage:{party_id}")
        await clan_hall.clan_storage_cb(cb)
        check("у партии кланового склада нет",
              cb.message.kb is None and any(
                  a and "не найден" in a for a in cb.alerts))

        print("\n7. Кнопка в карточке клана")
        cb = FakeCallback(MEMBER, f"clans:view:{clan_id}")
        await clans.clan_view_cb(cb)
        check("член клана видит «Склад клана»",
              f"clanh:storage:{clan_id}" in cbs(cb.message.kb))

        cb = FakeCallback(OUTSIDER, f"clans:view:{clan_id}")
        await clans.clan_view_cb(cb)
        check("посторонний не видит склад",
              f"clanh:storage:{clan_id}" not in cbs(cb.message.kb))

        print("\n8. Роспуск клана")
        await delete_clan(clan_id)
        check("склад удалён", await get_clan_storage(clan_id) == [])
        check("журнал удалён", await get_clan_contributions(clan_id) == [])
        conn = await get_db()
        cur = await conn.execute(
            "SELECT COUNT(*) AS n FROM clan_storage WHERE clan_id = ?", (clan_id,))
        check("строк склада в БД нет", (await cur.fetchone())['n'] == 0)
    finally:
        await close_db()

    print(f"\nИТОГО: {PASS} passed, {FAIL} failed")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
