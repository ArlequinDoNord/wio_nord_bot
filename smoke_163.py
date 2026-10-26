"""Smoke 163 — Клан-холл, Фаза 3: слоты расширений.

Проверяет:
1. Конфиг/лимиты: слоты house=2, manor=4, castle=6 (7-й — резерв),
   максимальный уровень 2/2/4.
2. Схему `clan_expansions` (PK, уникальный индекс по типу) и очистку при
   роспуске клана.
3. Установку: только глава, только в `built`, бесплатно (НМ и склад не
   тратятся), неизвестный тип/занятый слот/повтор типа/лимит слотов/резерв.
4. Улучшение: только глава, мгновенно, точное списание НМ и ресурсов,
   излишки склада сохраняются, транзакция `clan_expansion`, лимит уровня по
   типу здания, отказы при нехватке НМ/ресурсов без списаний.
5. Блокировку установки/улучшения во время `funding`/`building`/`upgrading`;
   уже установленные расширения при этом доступны (читаются).
6. UI: список слотов внутри здания, кнопка управления только у главы и только
   в `built`, экран управления/выбора типа, исключение установленных типов.
7. Резервный 7-й слот резиденции не предлагается и не устанавливается.

Клан-холл закрыт флагом `config.CLAN_HALL_ENABLED`, поэтому тест включает его
явно до импорта хендлеров.

Запуск: .venv\\Scripts\\python.exe smoke_163.py
"""
import asyncio
import os
import sys

_TEST_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_test_smoke163.db")
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


class FakeBot:
    def __init__(self):
        self.sent = []

    async def send_message(self, chat_id, text, parse_mode=None, reply_markup=None):
        self.sent.append((chat_id, text))
        return True


class FakeMessage:
    def __init__(self):
        self.photo = None
        self.text = None
        self.kb = None
        self.deleted = False
        self.media_photo = None

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
    def __init__(self, uid, data="", bot=None):
        self.from_user = FakeUser(uid)
        self.message = FakeMessage()
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


def kb_texts(kb):
    if not kb:
        return []
    return [b.text for row in kb.inline_keyboard for b in row]


async def main():
    import config
    config.DB_PATH = _TEST_DB
    config.CLAN_HALL_ENABLED = True
    import database.db as db
    db.DB_PATH = _TEST_DB
    from database.db import (
        init_db, close_db, get_db, add_user, get_user, add_nordmarks,
        create_clan, add_clan_member, set_clan_leader, delete_clan,
        ensure_logging_items, ensure_mine_items, get_item_by_name,
        add_clan_storage, get_clan_storage_qty,
        ensure_clan_building, get_clan_building, set_clan_building_built,
        start_clan_building, choose_clan_upgrade, cancel_clan_building,
        clan_expansion_slots, clan_expansion_max_level,
        get_clan_expansions, get_clan_expansion,
        install_clan_expansion, upgrade_clan_expansion,
    )
    from bot.handlers import clan_hall

    await init_db()
    await ensure_logging_items()
    await ensure_mine_items()

    LEADER, MEMBER, OUTSIDER = 163001, 163002, 163003
    for uid, nm in ((LEADER, "leader"), (MEMBER, "member"), (OUTSIDER, "outsider")):
        await add_user(uid, nm, nm.title(), "")

    clan_id = await create_clan("clan", "Северный Бастион", "Описание", LEADER)
    await set_clan_leader(clan_id, LEADER)
    await add_clan_member(clan_id, LEADER)
    await add_clan_member(clan_id, MEMBER)

    party_id = await create_clan("party", "Северная Партия", "Партия", LEADER)
    await set_clan_leader(party_id, LEADER)
    await add_clan_member(party_id, LEADER)

    plank = await get_item_by_name("Доска")
    ore = await get_item_by_name("Железная руда")
    conn = await get_db()

    try:
        print("\n1. Лимиты слотов и уровней")
        check("house: 2 слота, макс. уровень 2",
              clan_expansion_slots("house") == 2
              and clan_expansion_max_level("house") == 2)
        check("manor: 4 слота, макс. уровень 2",
              clan_expansion_slots("manor") == 4
              and clan_expansion_max_level("manor") == 2)
        check("castle: 6 слотов (7-й резерв), макс. уровень 4",
              clan_expansion_slots("castle") == 6
              and clan_expansion_max_level("castle") == 4)
        check("неизвестный тип: 0 слотов",
              clan_expansion_slots(None) == 0
              and clan_expansion_slots("palace") == 0)

        print("\n2. Схема clan_expansions")
        cur = await conn.execute("PRAGMA table_info(clan_expansions)")
        cols = {r["name"] for r in await cur.fetchall()}
        check("колонки таблицы на месте",
              {"clan_id", "slot_index", "expansion_type",
               "expansion_level", "installed_at"} <= cols)
        cur = await conn.execute("PRAGMA index_list(clan_expansions)")
        idx = await cur.fetchall()
        check("уникальный индекс по (clan_id, expansion_type) есть",
              any(r["unique"] for r in idx))
        has_type_unique = False
        for r in idx:
            if not r["unique"]:
                continue
            cur = await conn.execute(f"PRAGMA index_info('{r['name']}')")
            icols = [x["name"] for x in await cur.fetchall()]
            if icols == ["clan_id", "expansion_type"]:
                has_type_unique = True
        check("индекс действительно по clan_id + expansion_type", has_type_unique)

        print("\n3. Установка в Доме Клана (2 слота)")
        await ensure_clan_building(clan_id)
        await set_clan_building_built(clan_id, "house")
        await add_clan_storage(clan_id, plank["id"], 30)
        await add_clan_storage(clan_id, ore["id"], 15)
        await add_nordmarks(LEADER, 2000, "test", "на расширения")
        nm_before = int((await get_user(LEADER))["nordmarks"])
        plank_before = await get_clan_storage_qty(clan_id, plank["id"])
        ore_before = await get_clan_storage_qty(clan_id, ore["id"])

        ok, msg = await install_clan_expansion(clan_id, MEMBER, 1, "kitchen")
        check("рядовой член не может устанавливать",
              ok is False and "глава" in msg)
        ok, msg = await install_clan_expansion(clan_id, OUTSIDER, 1, "kitchen")
        check("посторонний не может устанавливать", ok is False)
        ok, msg = await install_clan_expansion(party_id, LEADER, 1, "kitchen")
        check("партия не может устанавливать", ok is False)
        ok, msg = await install_clan_expansion(clan_id, LEADER, 1, "palace")
        check("неизвестный тип расширения отклонён",
              ok is False and "Неизвестный" in msg)
        ok, msg = await install_clan_expansion(clan_id, LEADER, 3, "kitchen")
        check("слот вне лимита дома отклонён", ok is False and "2" in msg)

        ok, msg = await install_clan_expansion(clan_id, LEADER, 1, "kitchen")
        exp = await get_clan_expansion(clan_id, 1)
        check("установка кухни в слот 1 успешна",
              ok is True and exp is not None
              and exp["expansion_type"] == "kitchen"
              and int(exp["expansion_level"]) == 1)
        check("установка бесплатна: НМ и склад не изменились",
              int((await get_user(LEADER))["nordmarks"]) == nm_before
              and await get_clan_storage_qty(clan_id, plank["id"]) == plank_before
              and await get_clan_storage_qty(clan_id, ore["id"]) == ore_before)
        ok, msg = await install_clan_expansion(clan_id, LEADER, 2, "kitchen")
        check("повтор типа в другом слоте запрещён",
              ok is False and "уже установлено" in msg)
        ok, msg = await install_clan_expansion(clan_id, LEADER, 1, "workbench")
        check("занятый слот отклонён", ok is False and "занят" in msg)
        ok, msg = await install_clan_expansion(clan_id, LEADER, 2, "workbench")
        check("второй слот дома занят верстаком", ok is True)
        ok, msg = await install_clan_expansion(clan_id, LEADER, 2, "shower")
        check("третий слот дома невозможен", ok is False)

        print("\n4. UI управления расширениями")
        cb_inside = FakeCallback(LEADER, f"clanh:inside:{clan_id}")
        await clan_hall.clan_hall_inside_cb(cb_inside)
        check("внутри дома видна установленная кухня и верстак",
              "Кухня" in (cb_inside.message.text or "")
              and "Крафтовый стол" in (cb_inside.message.text or ""))
        check("глава видит кнопку управления расширениями",
              f"clanh:expmanage:{clan_id}" in cbs(cb_inside.message.kb))
        cb_inside_m = FakeCallback(MEMBER, f"clanh:inside:{clan_id}")
        await clan_hall.clan_hall_inside_cb(cb_inside_m)
        check("рядовой не видит кнопку управления",
              f"clanh:expmanage:{clan_id}" not in cbs(cb_inside_m.message.kb))

        cb_member_manage = FakeCallback(MEMBER, f"clanh:expmanage:{clan_id}")
        await clan_hall.clan_hall_expmanage_cb(cb_member_manage)
        check("рядовой не может открыть управление",
              any("глава" in str(a) for a in cb_member_manage.alerts))

        cb_manage = FakeCallback(LEADER, f"clanh:expmanage:{clan_id}")
        await clan_hall.clan_hall_expmanage_cb(cb_manage)
        check("на экране управления видны оба расширения",
              "Кухня" in (cb_manage.message.text or "")
              and "Крафтовый стол" in (cb_manage.message.text or ""))
        check("есть кнопки улучшения расширений",
              f"clanh:expup:{clan_id}:1" in cbs(cb_manage.message.kb))
        check("пустых слотов в доме нет — нет кнопок выбора",
              not any(c.startswith(f"clanh:expchoose:{clan_id}")
                      for c in cbs(cb_manage.message.kb)))

        print("\n5. Улучшение: точное списание")
        ok, msg = await upgrade_clan_expansion(clan_id, MEMBER, 1)
        check("рядовой не может улучшать", ok is False)
        ok, msg = await upgrade_clan_expansion(clan_id, LEADER, 1)
        exp = await get_clan_expansion(clan_id, 1)
        check("кухня улучшена до 2 уровня",
              ok is True and int(exp["expansion_level"]) == 2)
        check("списано 1500 НМ с главы",
              int((await get_user(LEADER))["nordmarks"]) == nm_before - 1500)
        check("списано ровно 20 досок (излишек сохранён)",
              await get_clan_storage_qty(clan_id, plank["id"]) == 10)
        check("списано ровно 10 руды (излишек сохранён)",
              await get_clan_storage_qty(clan_id, ore["id"]) == 5)
        cur = await conn.execute(
            "SELECT * FROM transactions WHERE tx_type = 'clan_expansion' "
            "ORDER BY id DESC LIMIT 1")
        tx = await cur.fetchone()
        check("транзакция clan_expansion на 1500 НМ",
              tx is not None and int(tx["amount"]) == 1500
              and int(tx["from_user"]) == LEADER)
        check("в описании транзакции название расширения",
              tx is not None and "Кухня" in (tx["description"] or ""))

        ok, msg = await upgrade_clan_expansion(clan_id, LEADER, 1)
        check("на доме максимальный уровень расширения — 2",
              ok is False and "максимальный" in msg.lower())
        # Добираем ресурсы до нормы верстака, чтобы проверить именно нехватку НМ
        await add_clan_storage(clan_id, plank["id"], 10)
        await add_clan_storage(clan_id, ore["id"], 5)
        nm_after = int((await get_user(LEADER))["nordmarks"])
        plank_after = await get_clan_storage_qty(clan_id, plank["id"])
        ore_after = await get_clan_storage_qty(clan_id, ore["id"])
        ok, msg = await upgrade_clan_expansion(clan_id, LEADER, 2)
        check("нехватка НМ: верстак не улучшен",
              ok is False and "Недостаточно нордмарок" in msg)
        check("при нехватке НМ склад не тронут",
              await get_clan_storage_qty(clan_id, plank["id"]) == plank_after
              and await get_clan_storage_qty(clan_id, ore["id"]) == ore_after
              and int((await get_user(LEADER))["nordmarks"]) == nm_after)
        ok, msg = await upgrade_clan_expansion(clan_id, LEADER, 9)
        check("улучшение пустого слота отклонено", ok is False)

        print("\n6. Блокировка во время работ")
        await choose_clan_upgrade(clan_id, LEADER)
        b = await get_clan_building(clan_id)
        check("дом переведён в upgrade_funding", b["status"] == "upgrade_funding")
        ok_i, msg_i = await install_clan_expansion(clan_id, LEADER, 1, "shower")
        ok_u, msg_u = await upgrade_clan_expansion(clan_id, LEADER, 1)
        check("во время upgrade_funding установка запрещена",
              ok_i is False and "готовом" in msg_i)
        check("во время upgrade_funding улучшение запрещено",
              ok_u is False and "готовом" in msg_u)
        check("установленные расширения по-прежнему читаются",
              len(await get_clan_expansions(clan_id)) == 2)
        cb_inside_up = FakeCallback(LEADER, f"clanh:inside:{clan_id}")
        await clan_hall.clan_hall_inside_cb(cb_inside_up)
        check("во время апгрейда кнопки управления нет",
              f"clanh:expmanage:{clan_id}" not in cbs(cb_inside_up.message.kb))
        await cancel_clan_building(clan_id, LEADER)

        await start_clan_building(clan_id, "2099-01-01 00:00:00")
        ok_i, msg_i = await install_clan_expansion(clan_id, LEADER, 1, "shower")
        check("во время building установка запрещена",
              ok_i is False and "готовом" in msg_i)
        await set_clan_building_built(clan_id, "house")

        print("\n7. Поместье: 4 слота")
        await set_clan_building_built(clan_id, "manor")
        ok1, _ = await install_clan_expansion(clan_id, LEADER, 3, "shower")
        ok2, _ = await install_clan_expansion(clan_id, LEADER, 4, "garden")
        check("в поместье доступны 3-й и 4-й слоты", ok1 is True and ok2 is True)
        ok3, msg3 = await install_clan_expansion(clan_id, LEADER, 5, "library")
        check("5-й слот поместья недоступен",
              ok3 is False and "4" in msg3)

        print("\n8. Резиденция: 6 слотов и 7-й резерв")
        await set_clan_building_built(clan_id, "castle")
        ok5, _ = await install_clan_expansion(clan_id, LEADER, 5, "library")
        ok6, _ = await install_clan_expansion(clan_id, LEADER, 6, "shop")
        check("в резиденции доступны 5-й и 6-й слоты", ok5 is True and ok6 is True)
        ok7, msg7 = await install_clan_expansion(clan_id, LEADER, 7, "kitchen")
        check("7-й слот — резерв, установка запрещена",
              ok7 is False and "резерв" in msg7.lower())
        txt = clan_hall.build_hall_inside_text(
            {"name": "Северный Бастион"}, {"building_type": "castle"})
        check("7-й слот помечен резервным в тексте", "7. 🔒" in txt)
        cb_castle = FakeCallback(LEADER, f"clanh:expmanage:{clan_id}")
        await clan_hall.clan_hall_expmanage_cb(cb_castle)
        check("на экране управления резиденцией виден резерв",
              "Резервный слот" in (cb_castle.message.text or ""))
        check("нет кнопки выбора для резервного слота",
              f"clanh:expchoose:{clan_id}:7" not in cbs(cb_castle.message.kb))

        print("\n9. Выбор типа исключает установленные")
        cb_choose = FakeCallback(LEADER, f"clanh:expchoose:{clan_id}:1")
        await clan_hall.clan_hall_expchoose_cb(cb_choose)
        check("занятый слот не открывает выбор",
              any("занят" in str(a) for a in cb_choose.alerts))
        # Освободим слот 2 и попробуем экран выбора
        await conn.execute(
            "DELETE FROM clan_expansions WHERE clan_id = ? AND slot_index = 2",
            (clan_id,))
        await conn.commit()
        cb_choose2 = FakeCallback(LEADER, f"clanh:expchoose:{clan_id}:2")
        await clan_hall.clan_hall_expchoose_cb(cb_choose2)
        choose_cbs = cbs(cb_choose2.message.kb)
        check("экран выбора открыт для пустого слота",
              f"clanh:expinstall:{clan_id}:2:workbench" in choose_cbs)
        check("установленная кухня не предлагается",
              f"clanh:expinstall:{clan_id}:2:kitchen" not in choose_cbs)
        cb_install = FakeCallback(LEADER, f"clanh:expinstall:{clan_id}:2:workbench")
        await clan_hall.clan_hall_expinstall_cb(cb_install)
        exp2 = await get_clan_expansion(clan_id, 2)
        check("установка через колбэк работает",
              exp2 is not None and exp2["expansion_type"] == "workbench")

        print("\n10. Резиденция: максимальный уровень 4")
        await add_clan_storage(clan_id, plank["id"], 200)
        await add_clan_storage(clan_id, ore["id"], 100)
        await add_nordmarks(LEADER, 20000, "test", "на улучшения")
        ok3, msg3 = await upgrade_clan_expansion(clan_id, LEADER, 1)
        ok4, msg4 = await upgrade_clan_expansion(clan_id, LEADER, 1)
        exp = await get_clan_expansion(clan_id, 1)
        check("кухня улучшена до 3 и 4 уровня",
              ok3 is True and ok4 is True
              and int(exp["expansion_level"]) == 4)
        ok5, msg5 = await upgrade_clan_expansion(clan_id, LEADER, 1)
        check("на резиденции максимум 4 уровня",
              ok5 is False and "максимальный" in msg5.lower())
        cb_max = FakeCallback(LEADER, f"clanh:expmanage:{clan_id}")
        await clan_hall.clan_hall_expmanage_cb(cb_max)
        check("для максимального расширения нет кнопки улучшения",
              f"clanh:expup:{clan_id}:1" not in cbs(cb_max.message.kb))

        print("\n11. Очистка при роспуске клана")
        check("перед удалением расширения есть",
              len(await get_clan_expansions(clan_id)) == 6)
        await delete_clan(clan_id)
        check("clan_expansions очищена при delete_clan",
              len(await get_clan_expansions(clan_id)) == 0)
        check("clan_buildings очищена при delete_clan",
              await get_clan_building(clan_id) is None)

    finally:
        await close_db()
        for _suffix in ("", "-wal", "-shm"):
            try:
                os.remove(_TEST_DB + _suffix)
            except OSError:
                pass

    print(f"\nИтого: {PASS} OK, {FAIL} FAIL")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
