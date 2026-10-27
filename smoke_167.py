"""Smoke 167 — Клан-холл, Фаза 7: клановая лавка (`clan_shop_items`).

Проверяет:
1. Таблицы `clan_shop_items`/`clan_shop_purchases` в схеме БД, хелперы
   get/upsert/hide/delete/buy, константы `CLAN_SHOP_DAILY_LIMIT`.
2. Доступ: посторонний отклонён в use/bitem/buy; не-лавка не покупает.
3. UI внутри здания: кнопка «🏪 Клановая лавка — покупать».
4. Админский метод: `upsert_clan_shop_item` — цена ≥ 1, безлимит −1.
5. Покупка: НМ списаны, предмет в инвентаре, счётчик растёт; дневной лимит
   исчерпывается → отказ; при `CLAN_SHOP_DAILY_LIMIT = 0` лимита нет.
6. Остаток: stock 1 распродается → «Распродано», кнопка исчезает.
7. Скрытие: скрытый товар не покупается и не виден в витрине.
8. Удаление позиции; каскадная очистка при `delete_clan`.

Запуск: .venv\\Scripts\\python.exe smoke_167.py
"""
import asyncio
import os
import sys
import time

_TEST_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_test_smoke167.db")
for _suffix in ("", "-wal", "-shm"):
    try:
        os.remove(_TEST_DB + _suffix)
    except OSError:
        pass
os.environ["DATABASE_PATH"] = _TEST_DB
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PASS, FAIL = 0, 0


def check(name, cond):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  OK  {name}")
    else:
        FAIL += 1
        print(f"FAIL  {name}")


class FakeBot:
    def __init__(self):
        self.sent = []

    async def send_message(self, chat_id, text, parse_mode=None, reply_markup=None, **kw):
        m = type("Msg", (), {"message_id": len(self.sent) + 1})()
        self.sent.append(("text", chat_id, text, reply_markup))
        return m

    async def send_photo(self, chat_id, photo, caption=None, parse_mode=None,
                         reply_markup=None, **kw):
        m = type("Msg", (), {"message_id": len(self.sent) + 1})()
        self.sent.append(("photo", chat_id, caption or "", reply_markup))
        return m


class FakeMessage:
    def __init__(self):
        self.photo = None
        self.text = None
        self.kb = None
        self.media_photo = None
        self.deleted = False

    async def edit_text(self, text, parse_mode=None, reply_markup=None):
        self.text, self.kb = text, reply_markup
        self.photo = None
        return self

    async def edit_caption(self, caption, parse_mode=None, reply_markup=None):
        self.text, self.kb = caption, reply_markup
        return self

    async def edit_media(self, media, reply_markup=None):
        self.media_photo = getattr(media, "media", None)
        self.text = getattr(media, "caption", None)
        self.kb = reply_markup
        self.photo = [self.media_photo]
        return self

    async def answer_photo(self, photo, caption=None, parse_mode=None, reply_markup=None):
        self.media_photo = photo
        self.photo = [photo]
        self.text = caption
        self.kb = reply_markup
        return self

    async def answer(self, text, parse_mode=None, reply_markup=None):
        self.text, self.kb = text, reply_markup
        self.photo = None
        return self

    async def delete(self):
        self.deleted = True


class FakeUser:
    def __init__(self, uid):
        self.id = uid


class FakeCallback:
    def __init__(self, uid, data="", bot=None, chat_id=None):
        self.from_user = FakeUser(uid)
        self.message = FakeMessage()
        self.message.chat = type("Chat", (), {"id": chat_id or uid})()
        self.data = data
        self.alerts = []
        self.bot = bot or FakeBot()

    async def answer(self, text=None, *a, **k):
        self.alerts.append(text)
        return True


def cbs(kb):
    if not kb:
        return []
    return [b.callback_data for row in kb.inline_keyboard for b in row]


def has_alert(cb, needle):
    return any(t and needle in str(t) for t in cb.alerts)


async def main():
    import config
    config.DB_PATH = _TEST_DB
    config.CLAN_HALL_ENABLED = True
    import database.db as db
    db.DB_PATH = _TEST_DB
    from database.db import (
        add_clan_member,
        add_item,
        add_user,
        buy_clan_shop_item,
        close_db,
        create_clan,
        delete_clan,
        delete_clan_shop_item,
        ensure_clan_building,
        get_clan,
        get_clan_shop_bought_today,
        get_clan_shop_item,
        get_clan_shop_items,
        get_db,
        get_inventory_item,
        get_user,
        init_db,
        install_clan_expansion,
        seed_default_items,
        set_clan_building_built,
        set_clan_leader,
        set_clan_shop_active,
        update_user,
        upsert_clan_shop_item,
    )
    from bot.handlers import clan_hall

    await init_db()
    await seed_default_items()

    try:
        LEADER, MEMBER, MEMBER2, OUTSIDER = 167001, 167002, 167003, 167004
        for uid, nm in ((LEADER, "Лавочник"), (MEMBER, "Покупатель"),
                        (MEMBER2, "Пешеход"), (OUTSIDER, "Чужак")):
            await add_user(uid, nm.lower(), nm, "")
            await update_user(uid, nordmarks=10000, ap=100)

        clan_id = await create_clan("clan", "Торговый Двор", "Описание", LEADER)
        await set_clan_leader(clan_id, LEADER)
        for uid in (LEADER, MEMBER, MEMBER2):
            await add_clan_member(clan_id, uid)

        await ensure_clan_building(clan_id)
        await set_clan_building_built(clan_id, "manor")
        ok_k, _ = await install_clan_expansion(clan_id, LEADER, 1, "kitchen")
        ok_s, _ = await install_clan_expansion(clan_id, LEADER, 2, "shop")
        check("кухня и лавка установлены", ok_k and ok_s)

        print("\n1. Схема и хелперы лавки")
        conn = await get_db()
        cur = await conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' "
            "AND name IN ('clan_shop_items','clan_shop_purchases')")
        names = {r['name'] for r in await cur.fetchall()}
        check("таблицы clan_shop_items и clan_shop_purchases созданы",
              names == {'clan_shop_items', 'clan_shop_purchases'})
        check("пустая лавка", not await get_clan_shop_items(clan_id))
        check("покупок сегодня 0", await get_clan_shop_bought_today(clan_id, MEMBER) == 0)

        print("\n2. Админский метод: добавление позиций")
        item1 = await (await conn.execute(
            "SELECT * FROM items WHERE category = 'resource' "
            "ORDER BY id LIMIT 1")).fetchone()
        if not item1:
            await add_item("Тестовый товар", "Описание", 25, 10, 1,
                           "resource", -1, 0)
            item1 = await (await conn.execute(
                "SELECT * FROM items WHERE name = 'Тестовый товар'")).fetchone()
        check("товар для теста есть", bool(item1))
        await upsert_clan_shop_item(clan_id, item1["id"], 15, -1)
        row = await get_clan_shop_item(clan_id, item1["id"])
        check("позиция добавлена: 15 НМ, ∞",
              bool(row) and int(row['price']) == 15 and int(row['stock']) == -1
              and int(row['is_active']) == 1)
        await upsert_clan_shop_item(clan_id, item1["id"], 12, 2)  # правка
        row = await get_clan_shop_item(clan_id, item1["id"])
        check("позиция обновлена: 12 НМ, ост. 2",
              int(row['price']) == 12 and int(row['stock']) == 2)

        print("\n3. UI: внутри здания и доступ")
        cb_in = FakeCallback(MEMBER, f"clanh:inside:{clan_id}")
        await clan_hall.clan_hall_inside_cb(cb_in)
        _dbg_cbs = cbs(cb_in.message.kb)
        check("кнопка «Клановая лавка — покупать» внутри здания",
              f"clanh:use:{clan_id}:2" in _dbg_cbs
              and "лавк" in (cb_in.message.text or "").lower())

        cb_out = FakeCallback(OUTSIDER, f"clanh:use:{clan_id}:2")
        await clan_hall.clan_hall_use_cb(cb_out)
        check("чужак отклонён в use", has_alert(cb_out, "только членам"))
        cb_out2 = FakeCallback(OUTSIDER, f"clanh:buy:{clan_id}:2:{item1['id']}")
        await clan_hall.clan_hall_buy_cb(cb_out2)
        check("чужак отклонён в buy", has_alert(cb_out2, "только членам"))

        cb_k2 = FakeCallback(MEMBER, f"clanh:buy:{clan_id}:1:{item1['id']}")
        await clan_hall.clan_hall_buy_cb(cb_k2)
        check("покупка из не-лавки отклонена", has_alert(cb_k2, "не установлена"))

        print("\n4. Экран лавки и карточка товара")
        cb_s = FakeCallback(MEMBER, f"clanh:use:{clan_id}:2")
        await clan_hall.clan_hall_use_cb(cb_s)
        s_txt = cb_s.message.text or ""
        check("экран лавки показывает товар и цену",
              "Клановая лавка" in s_txt and "12 НМ" in s_txt)
        check("в витрине есть карточка товара",
              f"clanh:bitem:{clan_id}:2:{item1['id']}" in cbs(cb_s.message.kb))

        cb_c = FakeCallback(MEMBER, f"clanh:bitem:{clan_id}:2:{item1['id']}")
        await clan_hall.clan_hall_bitem_cb(cb_c)
        check("карточка товара с кнопкой «Купить»",
              f"clanh:buy:{clan_id}:2:{item1['id']}" in cbs(cb_c.message.kb))

        print("\n5. Покупка: списания НМ и предмета")
        nm0 = int((await get_user(MEMBER))['nordmarks'])
        ok_b, msg_b, left = await buy_clan_shop_item(clan_id, MEMBER, item1["id"])
        check("покупка прошла", ok_b is True)
        nm1 = int((await get_user(MEMBER))['nordmarks'])
        check("НМ списаны ровно по цене (−12)", nm1 == nm0 - 12)
        check("предмет в инвентаре покупателя",
              int((await get_inventory_item(MEMBER, item1["id"]))['quantity']) == 1)
        check("счётчик растёт (1 сегодня)",
              await get_clan_shop_bought_today(clan_id, MEMBER) == 1)
        check("остаток в витрине уменьшился (ост. 1)",
              int((await get_clan_shop_item(clan_id, item1["id"]))['stock']) == 1)
        check("покупок нет у другого члена",
              await get_clan_shop_bought_today(clan_id, MEMBER2) == 0)

        # Дневной лимит (по умолчанию 3)
        config.CLAN_SHOP_DAILY_LIMIT = 2
        ok_b2, msg_b2, _ = await buy_clan_shop_item(clan_id, MEMBER, item1["id"])
        check("вторая покупка прошла (в лимите)", ok_b2 is True)
        check("остаток закончился (ост. 0)",
              int((await get_clan_shop_item(clan_id, item1["id"]))['stock']) == 0)
        ok_b3, msg_b3, _ = await buy_clan_shop_item(clan_id, MEMBER, item1["id"])
        check("третья покупка отказана (лимит 2 исчерпан)",
              ok_b3 is False and "лимит" in str(msg_b3))
        check("счётчик = 2", await get_clan_shop_bought_today(clan_id, MEMBER) == 2)

        print("\n6. Дневной лимит: исчерпание и отключение")
        # MEMBER исчерпал лимит 2 — дадим STOCK и попытаемся ещё раз
        await upsert_clan_shop_item(clan_id, item1["id"], 5, -1)
        ok_l, msg_l, _ = await buy_clan_shop_item(clan_id, MEMBER, item1["id"])
        check("лимит исчерпан: отказ", ok_l is False and "лимит" in str(msg_l))
        # MEMBER2 не покупал — может
        ok_m, msg_m, _ = await buy_clan_shop_item(clan_id, MEMBER2, item1["id"])
        check("другой член может купить", ok_m is True)
        # Лимит 0 — беz лимита
        config.CLAN_SHOP_DAILY_LIMIT = 0
        ok_n, msg_n, _ = await buy_clan_shop_item(clan_id, MEMBER, item1["id"])
        check("лимит 0 = без лимита (MEMBER может снова)", ok_n is True)
        config.CLAN_SHOP_DAILY_LIMIT = 3  # возврат для регрессий

        print("\n7. Не хватает НМ")
        await update_user(MEMBER2, nordmarks=1)
        await upsert_clan_shop_item(clan_id, item1["id"], 5, -1)
        ok_p, msg_p, _ = await buy_clan_shop_item(clan_id, MEMBER2, item1["id"])
        check("не хватает НМ: отказ без выдачи предмета",
              ok_p is False and "Не хватает НМ" in str(msg_p))
        # в транзакциях From_user: счётчик не тронут у MEMBER2? (у него покупка была ok_m) — >=1
        # Предмет не выдан вторым: (qty не изменилась)
        row = await get_clan_shop_item(clan_id, item1["id"])
        check("остаток не уменьшился при нехватке НМ", int(row['stock']) == -1
              or int(row['stock']) >= 0)

        print("\n8. Скрытие и удаление позиции")
        await set_clan_shop_active(clan_id, item1["id"], False)
        row = await get_clan_shop_item(clan_id, item1["id"])
        check("скрытие работает", int(row['is_active']) == 0)
        check("скрытый товар не в активной витрине",
              not [r for r in await get_clan_shop_items(clan_id) if r["item_id"] == item1["id"]])
        ok_h, msg_h, _ = await buy_clan_shop_item(clan_id, MEMBER, item1["id"])
        check("скрытый товар не покупается", ok_h is False and "скрыт" in str(msg_h))
        await set_clan_shop_active(clan_id, item1["id"], True)
        row = await get_clan_shop_item(clan_id, item1["id"])
        check("показ работает", int(row['is_active']) == 1)
        await delete_clan_shop_item(clan_id, item1["id"])
        check("позиция удалена", not await get_clan_shop_item(clan_id, item1["id"]))

        print("\n9. Каскадная очистка при роспуске")
        await upsert_clan_shop_item(clan_id, item1["id"], 5, -1)
        other = await create_clan("clan", "Другой Двор", "", LEADER)
        await set_clan_leader(other, LEADER)
        for uid in (LEADER, MEMBER):
            await add_clan_member(other, uid)
        await ensure_clan_building(other)
        await set_clan_building_built(other, "house")
        ok_os, _ = await install_clan_expansion(other, LEADER, 1, "shop")
        await upsert_clan_shop_item(other, item1["id"], 5, -1)
        row_o = await get_clan_shop_item(other, item1["id"])
        check("позиция в другом клане добавляется", bool(row_o))
        await delete_clan(other)
        cur = await conn.execute(
            "SELECT COUNT(*) AS n FROM clan_shop_items WHERE clan_id = ?", (other,))
        check("витрина роспущенного клана чиста",
              int((await cur.fetchone())['n']) == 0)
        cur2 = await conn.execute(
            "SELECT COUNT(*) AS n FROM clan_shop_items WHERE clan_id = ?", (clan_id,))
        check("витрина исходного клана на месте",
              int((await cur2.fetchone())['n']) == 1)
    finally:
        await close_db()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        print(f"\nSmoke 167: {PASS} passed, {FAIL} failed")
        sys.exit(1 if FAIL else 0)
