"""Smoke 165 — Клан-холл, Фаза 5: клановый сад (`clan_garden`).

Проверяет:
1. Конфиг `CLAN_GARDEN_PLOTS = {1: 2, 2: 3, 3: 4, 4: 6}`, `clan_garden_plots`,
   таблица `clan_garden` в схеме БД.
2. Доступ: посторонний не может открыть сад, список семян, посадить или собрать
   урожай; не-сад отклоняется во всех колбэках сада.
3. UI внутри здания (`clanh:inside`): кнопка «🌱 Сад (ур. N) — грядки».
4. Гейт числа грядок по уровню расширения (2/3/4/6): грядка выше лимита
   отклоняется и в UI, и в `plant_clan_seed`.
5. Посадка любым членом клана: семя списывается из личного инвентаря сажающего,
   `planted_by` запоминает автора, занятая грядка и не-семечко отклоняются
   без списаний.
6. Рост и плодоношение (`clan_plot_info`): стадии 0→4, накопление плодов до 5.
7. Сбор урожая только главой клана (`can_harvest_clan_garden`): рядовой член
   получает отказ, глава собирает плоды с одной грядки (`clanh:harvest`) и со
   всех сразу (`clanh:harvestall`) напрямую в `clan_storage` (не в личный
   инвентарь); повторный сбор сразу после сбора отклонён.
8. Апгрейд сада 1→4 сохраняет посаженные растения и открывает новые грядки.
9. Сад продолжает работать во время `upgrading` здания.
10. Каскадная очистка `clan_garden` при `delete_clan` и инварианты БД.

Запуск: .venv\\Scripts\\python.exe smoke_165.py
"""
import asyncio
import os
import sys
import time

_TEST_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_test_smoke165.db")
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
        add_clan_storage,
        add_inventory_item,
        add_user,
        can_harvest_clan_garden,
        choose_clan_upgrade,
        clan_garden_plots,
        clan_plot_info,
        close_db,
        create_clan,
        delete_clan,
        ensure_clan_building,
        ensure_dungeon_shop_items,
        ensure_forest_items,
        ensure_life_items,
        ensure_logging_items,
        ensure_mine_items,
        get_clan_garden,
        get_clan_storage_qty,
        get_db,
        get_inventory_item,
        get_item_by_name,
        init_db,
        install_clan_expansion,
        seed_default_items,
        set_clan_building_built,
        set_clan_leader,
        start_clan_building_project,
        update_user,
        upgrade_clan_expansion,
    )
    from bot.handlers import clan_hall

    await init_db()
    await seed_default_items()
    await ensure_dungeon_shop_items()
    await ensure_life_items()
    await ensure_forest_items()
    await ensure_logging_items()
    await ensure_mine_items()

    try:
        LEADER, MEMBER, MEMBER2, OUTSIDER = 165001, 165002, 165003, 165004
        for uid, nm in ((LEADER, "Ярл"), (MEMBER, "Садовник"),
                        (MEMBER2, "Дозорный"), (OUTSIDER, "Чужак")):
            await add_user(uid, nm.lower(), nm, "")
            await update_user(uid, nordmarks=100000, ap=100)

        clan_id = await create_clan("clan", "Яблоневый Двор", "Описание", LEADER)
        await set_clan_leader(clan_id, LEADER)
        for uid in (LEADER, MEMBER, MEMBER2):
            await add_clan_member(clan_id, uid)

        await ensure_clan_building(clan_id)
        await set_clan_building_built(clan_id, "manor")
        ok_g, _ = await install_clan_expansion(clan_id, LEADER, 1, "garden")
        ok_k, _ = await install_clan_expansion(clan_id, LEADER, 2, "kitchen")
        check("сад и кухня установлены в слоты 1 и 2", ok_g and ok_k)

        seed_item = await get_item_by_name("Яблочное семечко")
        apple_item = await get_item_by_name("Яблоко")
        board_item = await get_item_by_name("Доска")
        ore_item = await get_item_by_name("Железная руда")
        check("предметы семечка, яблока, доски и руды найдены",
              all((seed_item, apple_item, board_item, ore_item)))

        async def inv_qty(uid, item):
            row = await get_inventory_item(uid, item["id"])
            return int(row["quantity"]) if row else 0

        print("\n1. Конфиг сада и таблица clan_garden")
        check("CLAN_GARDEN_PLOTS = {1: 2, 2: 3, 3: 4, 4: 6}",
              config.CLAN_GARDEN_PLOTS == {1: 2, 2: 3, 3: 4, 4: 6})
        check("clan_garden_plots(1..4) = 2, 3, 4, 6",
              [clan_garden_plots(i) for i in (1, 2, 3, 4)] == [2, 3, 4, 6])
        conn = await get_db()
        cur = await conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='clan_garden'")
        check("таблица clan_garden создана", (await cur.fetchone()) is not None)
        check("can_harvest_clan_garden: глава True, член False, чужак False",
              await can_harvest_clan_garden(clan_id, LEADER) is True
              and await can_harvest_clan_garden(clan_id, MEMBER) is False
              and await can_harvest_clan_garden(clan_id, OUTSIDER) is False)

        print("\n2. Внутри здания и контроль доступа")
        cb_in = FakeCallback(MEMBER, f"clanh:inside:{clan_id}")
        await clan_hall.clan_hall_inside_cb(cb_in)
        in_txt = cb_in.message.text or ""
        in_cbs = cbs(cb_in.message.kb)
        check("внутри здания виден Сад и кнопка грядок",
              "Сад" in in_txt and f"clanh:use:{clan_id}:1" in in_cbs)

        for label, fn, data in (
            ("use", clan_hall.clan_hall_use_cb, f"clanh:use:{clan_id}:1"),
            ("plantlist", clan_hall.clan_hall_plantlist_cb, f"clanh:plantlist:{clan_id}:1:1"),
            ("plant", clan_hall.clan_hall_plant_cb, f"clanh:plant:{clan_id}:1:1:{seed_item['id']}"),
            ("harvest", clan_hall.clan_hall_harvest_cb, f"clanh:harvest:{clan_id}:1:1"),
            ("harvestall", clan_hall.clan_hall_harvestall_cb, f"clanh:harvestall:{clan_id}:1"),
        ):
            cb_out = FakeCallback(OUTSIDER, data)
            await fn(cb_out)
            check(f"чужак отклонён в {label}", has_alert(cb_out, "только членам"))

        for label, fn, data in (
            ("plantlist на кухне", clan_hall.clan_hall_plantlist_cb, f"clanh:plantlist:{clan_id}:2:1"),
            ("plant на кухне", clan_hall.clan_hall_plant_cb, f"clanh:plant:{clan_id}:2:1:{seed_item['id']}"),
            ("harvest на кухне", clan_hall.clan_hall_harvest_cb, f"clanh:harvest:{clan_id}:2:1"),
            ("harvestall на кухне", clan_hall.clan_hall_harvestall_cb, f"clanh:harvestall:{clan_id}:2"),
        ):
            cb_wrong = FakeCallback(LEADER, data)
            await fn(cb_wrong)
            check(f"не-сад отклонён: {label}", has_alert(cb_wrong, "нет сада"))

        print("\n3. Экран пустого сада 1 ур. (2 грядки) и список семян")
        cb_g = FakeCallback(MEMBER, f"clanh:use:{clan_id}:1")
        await clan_hall.clan_hall_use_cb(cb_g)
        g_txt = cb_g.message.text or ""
        g_cbs = cbs(cb_g.message.kb)
        check("экран сада 1 ур. показывает 2 грядки",
              "Грядок: <b>2</b>" in g_txt and "Пустая грядка" in g_txt)
        check("кнопки посадки на грядки 1 и 2 есть, а 3 — нет",
              f"clanh:plantlist:{clan_id}:1:1" in g_cbs
              and f"clanh:plantlist:{clan_id}:1:2" in g_cbs
              and f"clanh:plantlist:{clan_id}:1:3" not in g_cbs)

        cb_pl_empty = FakeCallback(MEMBER, f"clanh:plantlist:{clan_id}:1:1")
        await clan_hall.clan_hall_plantlist_cb(cb_pl_empty)
        check("список семян без семян в инвентаре пишет «нет семян»",
              "нет семян" in (cb_pl_empty.message.text or ""))

        cb_pl_oob = FakeCallback(MEMBER, f"clanh:plantlist:{clan_id}:1:3")
        await clan_hall.clan_hall_plantlist_cb(cb_pl_oob)
        check("грядка 3 на 1 ур. сада отклонена в plantlist",
              has_alert(cb_pl_oob, "Такой грядки"))

        print("\n4. Посадка семечка любым членом и проверки отказов")
        await add_inventory_item(MEMBER, board_item["id"], 1)
        cb_notseed = FakeCallback(
            MEMBER, f"clanh:plant:{clan_id}:1:1:{board_item['id']}")
        await clan_hall.clan_hall_plant_cb(cb_notseed)
        check("не-семечко отклонено", has_alert(cb_notseed, "не семечко"))
        check("доска не списана", await inv_qty(MEMBER, board_item) == 1)

        cb_noseed = FakeCallback(
            MEMBER, f"clanh:plant:{clan_id}:1:1:{seed_item['id']}")
        await clan_hall.clan_hall_plant_cb(cb_noseed)
        check("посадка без семечка в инвентаре отклонена",
              has_alert(cb_noseed, "нет в инвентаре"))

        await add_inventory_item(MEMBER, seed_item["id"], 2)
        await add_inventory_item(MEMBER2, seed_item["id"], 1)

        cb_pl = FakeCallback(MEMBER, f"clanh:plantlist:{clan_id}:1:1")
        await clan_hall.clan_hall_plantlist_cb(cb_pl)
        check("в списке семян появилась кнопка посадки яблочного семечка",
              f"clanh:plant:{clan_id}:1:1:{seed_item['id']}" in cbs(cb_pl.message.kb))

        cb_oob_plant = FakeCallback(
            MEMBER, f"clanh:plant:{clan_id}:1:3:{seed_item['id']}")
        await clan_hall.clan_hall_plant_cb(cb_oob_plant)
        check("посадка на грядку 3 при лимите 2 отклонена",
              has_alert(cb_oob_plant, "Такой грядки"))
        check("семечко при отказе по лимиту не списано",
              await inv_qty(MEMBER, seed_item) == 2)

        cb_plant1 = FakeCallback(
            MEMBER, f"clanh:plant:{clan_id}:1:1:{seed_item['id']}")
        await clan_hall.clan_hall_plant_cb(cb_plant1)
        check("рядовой член посадил семечко на грядку 1",
              has_alert(cb_plant1, "На грядку 1 посажено"))
        check("семечко списано из личного инвентаря сажающего (2 -> 1)",
              await inv_qty(MEMBER, seed_item) == 1)

        garden = await get_clan_garden(clan_id)
        check("в clan_garden появилась грядка 1 с planted_by=MEMBER и Яблоней",
              1 in garden
              and int(garden[1]["planted_by"]) == MEMBER
              and garden[1]["plant_name"] == "Яблоня")
        check("на экране сада видно растение «Яблоня» и имя автора «Садовник»",
              "Яблоня" in (cb_plant1.message.text or "")
              and "Садовник" in (cb_plant1.message.text or ""))

        cb_dup = FakeCallback(
            MEMBER2, f"clanh:plant:{clan_id}:1:1:{seed_item['id']}")
        await clan_hall.clan_hall_plant_cb(cb_dup)
        check("повторная посадка на занятую грядку отклонена",
              has_alert(cb_dup, "уже занята"))
        check("семечко второго игрока не списано",
              await inv_qty(MEMBER2, seed_item) == 1)

        cb_pl_busy = FakeCallback(MEMBER2, f"clanh:plantlist:{clan_id}:1:1")
        await clan_hall.clan_hall_plantlist_cb(cb_pl_busy)
        check("plantlist на занятую грядку тоже сообщает «уже занята»",
              has_alert(cb_pl_busy, "уже занята"))

        cb_plant2 = FakeCallback(
            MEMBER2, f"clanh:plant:{clan_id}:1:2:{seed_item['id']}")
        await clan_hall.clan_hall_plant_cb(cb_plant2)
        check("второй член посадил семечко на грядку 2",
              has_alert(cb_plant2, "На грядку 2 посажено"))
        check("у второго члена списано семечко (1 -> 0)",
              await inv_qty(MEMBER2, seed_item) == 0)

        print("\n5. Рост растений и защита сбора только для главы")
        cb_early = FakeCallback(LEADER, f"clanh:harvest:{clan_id}:1:1")
        await clan_hall.clan_hall_harvest_cb(cb_early)
        check("сбор на стадии Семя отклонён («Плодов ещё нет»)",
              has_alert(cb_early, "Плодов ещё нет"))

        cb_early_all = FakeCallback(LEADER, f"clanh:harvestall:{clan_id}:1")
        await clan_hall.clan_hall_harvestall_cb(cb_early_all)
        check("harvestall без спелых плодов отклонён",
              has_alert(cb_early_all, "Спелых плодов для сбора пока нет"))

        # Сдвигаем грядку 1 на 36 суток назад (30 сут. до плодоношения + 6 сут. = 3 плода),
        # грядку 2 — на 50 суток назад (потолок 5 плодов).
        now = time.time()
        await conn.execute(
            "UPDATE clan_garden SET stage_started_at = ? WHERE clan_id = ? AND plot_index = 1",
            (now - 36 * 86400 - 60, clan_id))
        await conn.execute(
            "UPDATE clan_garden SET stage_started_at = ? WHERE clan_id = ? AND plot_index = 2",
            (now - 50 * 86400 - 60, clan_id))
        await conn.commit()

        garden = await get_clan_garden(clan_id)
        info1 = clan_plot_info(garden[1], now)
        info2 = clan_plot_info(garden[2], now)
        check("грядка 1 созрела: стадия 4, 3 плода",
              info1["stage"] == 4 and info1["fruits"] == 3)
        check("грядка 2 созрела до потолка: стадия 4, 5 плодов",
              info2["stage"] == 4 and info2["fruits"] == 5)

        cb_mem_view = FakeCallback(MEMBER, f"clanh:use:{clan_id}:1")
        await clan_hall.clan_hall_use_cb(cb_mem_view)
        mem_cbs = cbs(cb_mem_view.message.kb)
        check("рядовой член видит плоды в тексте, но НЕ видит кнопок сбора",
              "плодов: 3/5" in (cb_mem_view.message.text or "")
              and f"clanh:harvest:{clan_id}:1:1" not in mem_cbs
              and f"clanh:harvestall:{clan_id}:1" not in mem_cbs)

        cb_mem_h = FakeCallback(MEMBER, f"clanh:harvest:{clan_id}:1:1")
        await clan_hall.clan_hall_harvest_cb(cb_mem_h)
        check("рядовой член не может собрать грядку",
              has_alert(cb_mem_h, "только глава клана"))

        cb_mem_ha = FakeCallback(MEMBER, f"clanh:harvestall:{clan_id}:1")
        await clan_hall.clan_hall_harvestall_cb(cb_mem_ha)
        check("рядовой член не может нажать «собрать весь урожай»",
              has_alert(cb_mem_ha, "только глава клана"))
        check("склад клана пока без яблок",
              await get_clan_storage_qty(clan_id, apple_item["id"]) == 0)

        print("\n6. Сбор урожая главой в клановый склад")
        cb_lead_view = FakeCallback(LEADER, f"clanh:use:{clan_id}:1")
        await clan_hall.clan_hall_use_cb(cb_lead_view)
        lead_cbs = cbs(cb_lead_view.message.kb)
        check("глава видит кнопки сбора по грядкам и «Собрать весь урожай»",
              f"clanh:harvest:{clan_id}:1:1" in lead_cbs
              and f"clanh:harvest:{clan_id}:1:2" in lead_cbs
              and f"clanh:harvestall:{clan_id}:1" in lead_cbs)

        cb_h1 = FakeCallback(LEADER, f"clanh:harvest:{clan_id}:1:1")
        await clan_hall.clan_hall_harvest_cb(cb_h1)
        check("глава собрал 3 яблока с грядки 1",
              has_alert(cb_h1, "Яблоко ×3"))
        check("яблоки поступили в clan_storage (3 шт.)",
              await get_clan_storage_qty(clan_id, apple_item["id"]) == 3)
        check("в личный инвентарь главы яблоки НЕ попали",
              await inv_qty(LEADER, apple_item) == 0)

        cb_h1_again = FakeCallback(LEADER, f"clanh:harvest:{clan_id}:1:1")
        await clan_hall.clan_hall_harvest_cb(cb_h1_again)
        check("повторный сбор с грядки 1 сразу после сбора отклонён",
              has_alert(cb_h1_again, "Плодов ещё нет"))
        check("количество яблок на складе не задвоилось (осталось 3)",
              await get_clan_storage_qty(clan_id, apple_item["id"]) == 3)

        # Дозреваем грядку 1 ещё на 2 суток (1 яблоко) и собираем всё разом (1 + 5 = 6).
        await conn.execute(
            "UPDATE clan_garden SET last_harvest_at = ? WHERE clan_id = ? AND plot_index = 1",
            (time.time() - 2 * 86400 - 30, clan_id))
        await conn.commit()

        cb_ha = FakeCallback(LEADER, f"clanh:harvestall:{clan_id}:1")
        await clan_hall.clan_hall_harvestall_cb(cb_ha)
        check("«Собрать весь урожай» собрал 6 яблок с обеих грядок",
              has_alert(cb_ha, "Яблоко ×6"))
        check("на складе клана теперь 9 яблок (3 + 6)",
              await get_clan_storage_qty(clan_id, apple_item["id"]) == 9)

        print("\n7. Улучшение сада (ур. 1 -> 4) и работа во время upgrading")
        await set_clan_building_built(clan_id, "castle")
        await add_clan_storage(clan_id, board_item["id"], 500)
        await add_clan_storage(clan_id, ore_item["id"], 500)
        for target_lvl, expected_plots in ((2, 3), (3, 4), (4, 6)):
            ok_up, msg_up = await upgrade_clan_expansion(clan_id, LEADER, 1)
            check(f"сад улучшен до {target_lvl} ур. ({expected_plots} грядок): {msg_up}",
                  ok_up is True)

        cb_g4 = FakeCallback(MEMBER, f"clanh:use:{clan_id}:1")
        await clan_hall.clan_hall_use_cb(cb_g4)
        g4_cbs = cbs(cb_g4.message.kb)
        check("на 4 ур. сада грядки 1–2 сохранены, а грядки 3–6 открыты для посадки",
              f"clanh:plantlist:{clan_id}:1:3" in g4_cbs
              and f"clanh:plantlist:{clan_id}:1:6" in g4_cbs
              and f"clanh:plantlist:{clan_id}:1:7" not in g4_cbs)

        # Переводим здание обратно в manor -> upgrading до castle и проверяем работу сада.
        await set_clan_building_built(clan_id, "manor")
        ok_ch, _ = await choose_clan_upgrade(clan_id, LEADER)
        ok_st, _, _ = await start_clan_building_project(clan_id, LEADER, skip_resources=True)
        check("здание переведено в upgrading", ok_ch and ok_st)

        cb_up_plant = FakeCallback(
            MEMBER, f"clanh:plant:{clan_id}:1:6:{seed_item['id']}")
        await clan_hall.clan_hall_plant_cb(cb_up_plant)
        check("во время upgrading здания можно сажать на грядку 6",
              has_alert(cb_up_plant, "На грядку 6 посажено"))

        await conn.execute(
            "UPDATE clan_garden SET stage_started_at = ? WHERE clan_id = ? AND plot_index = 6",
            (time.time() - 32 * 86400 - 60, clan_id))
        await conn.commit()

        cb_up_harv = FakeCallback(LEADER, f"clanh:harvest:{clan_id}:1:6")
        await clan_hall.clan_hall_harvest_cb(cb_up_harv)
        check("во время upgrading здания глава может собирать урожай",
              has_alert(cb_up_harv, "Яблоко ×1"))
        check("урожай во время upgrading поступил на склад (10 шт.)",
              await get_clan_storage_qty(clan_id, apple_item["id"]) == 10)

        print("\n8. Очистка clan_garden при роспуске клана и инварианты БД")
        await delete_clan(clan_id)
        check("после delete_clan грядок клана не осталось",
              await get_clan_garden(clan_id) == {})

        cur = await conn.execute(
            "SELECT COUNT(*) AS c FROM inventory WHERE quantity < 0")
        check("инвариант: нет отрицательных остатков в inventory",
              int((await cur.fetchone())["c"]) == 0)
        cur = await conn.execute(
            "SELECT COUNT(*) AS c FROM clan_storage WHERE qty < 0")
        check("инвариант: нет отрицательных остатков в clan_storage",
              int((await cur.fetchone())["c"]) == 0)
    finally:
        await close_db()
        for _suffix in ("", "-wal", "-shm"):
            try:
                os.remove(_TEST_DB + _suffix)
            except OSError:
                pass

    print(f"\nSmoke 165: {PASS} passed, {FAIL} failed")
    if FAIL:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
