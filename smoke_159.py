"""Smoke 159 — Клан-холл, Фаза 1: выбор проекта, сбор ресурсов, стройка, фото, таймер, вход.

Проверяет:
1. Таблица `clan_buildings` (включая `building_photo_file_id`) и ленивое создание `ensure_clan_building`.
2. Права `can_manage_clan_hall` / `can_withdraw_clan_storage` / `can_harvest_clan_garden`
   (только глава клана `kind='clan'`, партиям — нет).
3. Карточка клана: кнопка «🏰 Здание клана» у члена клана есть, у постороннего и у партии — нет.
4. Выбор проекта здания (`choose_clan_building` / `clanh:choose:`):
   снимок `required_json` и `price_nm`, смена до первого вклада, блокировка смены после вклада,
   отмена `cancel_clan_building` (`clanh:cancel:`) возвращает в `choosing`, сохраняя ресурсы на складе.
5. Старт строительства (`start_clan_building_project` / `clanh:start:`):
   отказ при нехватке ресурсов или НМ; при успехе списываются ровно требуемые ресурсы
   (излишки остаются на складе) и НМ главы (транзакция `clan_build`), рассылается уведомление.
6. Картинки: во время `building` используется общая заглушка стройки (`clan_construction_photo`),
   после постройки (`built`) — индивидуальное фото здания клана (`building_photo_file_id`).
7. Завершение по таймеру (`resolve_clan_building` / `resolve_due_clan_buildings`), идемпотентность,
   вход внутрь (`clanh:inside:`) до и после постройки, резервный 7-й слот Замка.
8. Очистка `clan_buildings` при `delete_clan`.

Запуск: .venv\\Scripts\\python.exe smoke_159.py
"""
import asyncio
import json
import os
import sys
from datetime import datetime, timedelta, timezone

_TEST_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_test_smoke159.db")
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


async def main():
    import config
    config.DB_PATH = _TEST_DB
    import database.db as db
    db.DB_PATH = _TEST_DB
    from database.db import (
        init_db, close_db, get_db, add_user, get_user, add_nordmarks,
        create_clan, add_clan_member, set_clan_leader, delete_clan,
        ensure_logging_items, ensure_mine_items, get_item_by_name,
        add_inventory_item, add_clan_storage, get_clan_storage_qty,
        donate_to_clan_storage,
        can_manage_clan_hall, can_withdraw_clan_storage, can_harvest_clan_garden,
        get_clan_building, ensure_clan_building,
        choose_clan_building, cancel_clan_building,
        get_clan_project_progress, start_clan_building_project,
        resolve_clan_building, resolve_due_clan_buildings,
        set_clan_building_photo, get_clan_construction_photo, set_clan_construction_photo,
    )
    from bot.handlers import clan_hall, clans

    await init_db()
    await ensure_logging_items()
    await ensure_mine_items()

    LEADER, MEMBER, OUTSIDER = 159001, 159002, 159003
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
    wood = await get_item_by_name("Бревна")
    ore = await get_item_by_name("Железная руда")

    try:
        print("\n1. Таблица clan_buildings и права доступа")
        conn = await get_db()
        cur = await conn.execute("PRAGMA table_info(clan_buildings)")
        cols = {r["name"] for r in await cur.fetchall()}
        check("clan_buildings создана со всеми колонками",
              {"clan_id", "building_type", "target_type", "status",
               "required_json", "price_nm", "building_photo_file_id"}.issubset(cols))

        b0 = await ensure_clan_building(clan_id)
        check("ленивое создание со статусом choosing",
              b0 is not None and b0["status"] == "choosing" and b0["building_type"] is None)

        check("глава может управлять холлом", await can_manage_clan_hall(clan_id, LEADER) is True)
        check("рядовой член не может управлять холлом", await can_manage_clan_hall(clan_id, MEMBER) is False)
        check("посторонний не может управлять холлом", await can_manage_clan_hall(clan_id, OUTSIDER) is False)
        check("партии холл недоступен", await can_manage_clan_hall(party_id, LEADER) is False)
        check("заглушки withdraw/harvest работают",
              await can_withdraw_clan_storage(clan_id, LEADER) is True
              and await can_harvest_clan_garden(clan_id, MEMBER) is False)

        print("\n2. Кнопка «Здание клана» в карточке клана")
        cb_view = FakeCallback(MEMBER, f"clans:view:{clan_id}")
        await clans.clan_view_cb(cb_view)
        check("член клана видит кнопку Здание клана",
              f"clanh:hall:{clan_id}" in cbs(cb_view.message.kb))

        cb_out = FakeCallback(OUTSIDER, f"clans:view:{clan_id}")
        await clans.clan_view_cb(cb_out)
        check("посторонний не видит кнопку Здание клана",
              f"clanh:hall:{clan_id}" not in cbs(cb_out.message.kb))

        cb_party = FakeCallback(LEADER, f"clans:view:{party_id}")
        await clans.clan_view_cb(cb_party)
        check("в карточке партии нет кнопки Здание клана",
              f"clanh:hall:{party_id}" not in cbs(cb_party.message.kb))

        print("\n3. Экран выбора проекта и смена/отмена выбора")
        cb_hall_m = FakeCallback(MEMBER, f"clanh:hall:{clan_id}")
        await clan_hall.clan_hall_cb(cb_hall_m)
        check("рядовой видит экран choosing без кнопок выбора",
              "Здание клана" in (cb_hall_m.message.text or "")
              and not any(x.startswith("clanh:choose:") for x in cbs(cb_hall_m.message.kb)))

        cb_hall_l = FakeCallback(LEADER, f"clanh:hall:{clan_id}")
        await clan_hall.clan_hall_cb(cb_hall_l)
        check("глава видит 3 кнопки выбора типа здания",
              f"clanh:choose:{clan_id}:house" in cbs(cb_hall_l.message.kb)
              and f"clanh:choose:{clan_id}:manor" in cbs(cb_hall_l.message.kb)
              and f"clanh:choose:{clan_id}:castle" in cbs(cb_hall_l.message.kb))

        ok_m, _ = await choose_clan_building(clan_id, MEMBER, "house")
        check("рядовой не может выбрать проект", ok_m is False)
        ok_bad, _ = await choose_clan_building(clan_id, LEADER, "palace")
        check("неизвестный тип отклоняется", ok_bad is False)

        cb_ch = FakeCallback(LEADER, f"clanh:choose:{clan_id}:manor")
        await clan_hall.clan_hall_choose_cb(cb_ch)
        b_manor = await get_clan_building(clan_id)
        check("выбор поместья переводит в funding",
              b_manor["status"] == "funding" and b_manor["building_type"] == "manor"
              and b_manor["price_nm"] == 8000)

        # Пока нет вкладов после chosen_at, можно перевыбрать напрямую
        ok_re, _ = await choose_clan_building(clan_id, LEADER, "house")
        b_house = await get_clan_building(clan_id)
        check("смена типа до первого вклада разрешена",
              ok_re is True and b_house["building_type"] == "house" and b_house["price_nm"] == 3000)
        snap = json.loads(b_house["required_json"])
        check("снимок требований Дома сохранён",
              snap == {"Доска": 60, "Бревна": 20, "Железная руда": 15})

        # Вносим вклад — прямая смена блокируется, но отмена возвращает в choosing, сохраняя склад
        await add_inventory_item(MEMBER, plank["id"], 5)
        await donate_to_clan_storage(clan_id, MEMBER, plank["id"], 5)
        ok_blocked, _ = await choose_clan_building(clan_id, LEADER, "castle")
        check("прямая смена после вклада заблокирована", ok_blocked is False)

        cb_cancel = FakeCallback(LEADER, f"clanh:cancel:{clan_id}")
        await clan_hall.clan_hall_cancel_cb(cb_cancel)
        b_after_cancel = await get_clan_building(clan_id)
        check("отмена возвращает статус в choosing", b_after_cancel["status"] == "choosing")
        check("ресурсы после отмены остались на складе (5 досок)",
              await get_clan_storage_qty(clan_id, plank["id"]) == 5)

        # Снова выбираем Дом Клана
        await choose_clan_building(clan_id, LEADER, "house")

        print("\n4. Прогресс сбора и старт строительства")
        prog, all_ok = await get_clan_project_progress(clan_id)
        check("прогресс неполный (5/60 досок)", all_ok is False and len(prog) == 3)

        ok_start_early, _, _ = await start_clan_building_project(clan_id, LEADER)
        check("старт без ресурсов отклонён", ok_start_early is False)

        # Кладём ресурсы с запасом (75 досок при норме 60, 25 брёвен при 20, 20 руды при 15)
        await add_clan_storage(clan_id, plank["id"], 70)  # 5 + 70 = 75
        await add_clan_storage(clan_id, wood["id"], 25)
        await add_clan_storage(clan_id, ore["id"], 20)
        _, all_ok2 = await get_clan_project_progress(clan_id)
        check("все ресурсы собраны", all_ok2 is True)

        # Но у лидера 0 НМ
        ok_no_nm, msg_no_nm, _ = await start_clan_building_project(clan_id, LEADER)
        check("старт без НМ у главы отклонён", ok_no_nm is False and "нордмарок" in msg_no_nm)

        # Начисляем лидеру 5000 НМ (с начальными 10 НМ = 5010) и запускаем через хендлер
        await add_nordmarks(LEADER, 5000, "test", "на стройку")
        before_nm = (await get_user(LEADER))["nordmarks"]
        bot = FakeBot()
        cb_start = FakeCallback(LEADER, f"clanh:start:{clan_id}", bot=bot)
        await clan_hall.clan_hall_start_cb(cb_start)

        b_building = await get_clan_building(clan_id)
        check("статус перешёл в building", b_building["status"] == "building")
        check("таймер completes_at установлен", bool(b_building["completes_at"]))
        check("излишки досок остались на складе (75-60=15)",
              await get_clan_storage_qty(clan_id, plank["id"]) == 15)
        check("излишки брёвен остались на складе (25-20=5)",
              await get_clan_storage_qty(clan_id, wood["id"]) == 5)
        check("излишки руды остались на складе (20-15=5)",
              await get_clan_storage_qty(clan_id, ore["id"]) == 5)
        leader_row = await get_user(LEADER)
        check("с лидера списано ровно 3000 НМ", leader_row["nordmarks"] == before_nm - 3000)
        tx_cur = await conn.execute(
            "SELECT * FROM transactions WHERE from_user = ? AND tx_type = 'clan_build'",
            (LEADER,))
        tx_row = await tx_cur.fetchone()
        check("транзакция clan_build записана", tx_row is not None and tx_row["amount"] == 3000)
        check("уведомление о старте стройки отправлено обоим членам клана",
              len(bot.sent) == 2 and {u for u, _ in bot.sent} == {LEADER, MEMBER})

        print("\n5. Заглушка стройки и индивидуальное фото готового здания")
        await set_clan_construction_photo("file_id_construction_stub")
        await set_clan_building_photo(clan_id, "file_id_custom_clan_castle")
        check("заглушка стройки сохранена в settings",
              await get_clan_construction_photo() == "file_id_construction_stub")
        b_building = await get_clan_building(clan_id)
        photo_during_build = await clan_hall.resolve_clan_hall_photo(b_building)
        check("во время стройки отдаётся заглушка стройки, а не фото готового здания",
              photo_during_build == "file_id_construction_stub")

        cb_inside_early = FakeCallback(MEMBER, f"clanh:inside:{clan_id}")
        await clan_hall.clan_hall_inside_cb(cb_inside_early)
        check("вход внутрь во время первого строительства запрещён",
              cb_inside_early.alerts and "не построено" in (cb_inside_early.alerts[-1] or ""))

        print("\n6. Завершение стройки по таймеру и вход внутрь")
        # Пока срок в будущем — resolve_due_clan_buildings ничего не трогает
        due0 = await resolve_due_clan_buildings()
        check("пока таймер не вышел — стройка активна", len(due0) == 0)

        # Сдвигаем completes_at в прошлое
        past = (datetime.now(timezone.utc) - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
        await conn.execute("UPDATE clan_buildings SET completes_at = ? WHERE clan_id = ?",
                           (past, clan_id))
        await conn.commit()

        due1 = await resolve_due_clan_buildings()
        check("resolve_due_clan_buildings завершил стройку",
              len(due1) == 1 and due1[0]["clan_id"] == clan_id
              and due1[0]["event"] == "built" and due1[0]["building_type"] == "house")
        due2 = await resolve_due_clan_buildings()
        check("повторный вызов resolve_due_clan_buildings идемпотентен", len(due2) == 0)

        b_built = await resolve_clan_building(clan_id)
        check("статус built, тип house",
              b_built["status"] == "built" and b_built["building_type"] == "house")
        photo_when_built = await clan_hall.resolve_clan_hall_photo(b_built)
        check("после постройки отдаётся индивидуальное фото здания клана",
              photo_when_built == "file_id_custom_clan_castle")

        cb_hall_built = FakeCallback(MEMBER, f"clanh:hall:{clan_id}")
        await clan_hall.clan_hall_cb(cb_hall_built)
        check("на экране построенного здания есть кнопка входа и индивидуальное фото",
              f"clanh:inside:{clan_id}" in cbs(cb_hall_built.message.kb)
              and cb_hall_built.message.media_photo == "file_id_custom_clan_castle")

        cb_inside = FakeCallback(MEMBER, f"clanh:inside:{clan_id}")
        await clan_hall.clan_hall_inside_cb(cb_inside)
        check("вход внутрь Дома Клана показывает 2 слота расширений",
              "Слоты расширений (2 шт." in (cb_inside.message.text or "")
              and "1." in (cb_inside.message.text or "")
              and "2." in (cb_inside.message.text or ""))

        # Проверим текст Замка (7-й резервный слот)
        txt_castle = clan_hall.build_hall_inside_text(
            {"name": "Северный Бастион"}, {"building_type": "castle"}
        )
        check("7-й слот Замка помечен как резервный", "7. 🔒" in txt_castle and "Резервный слот" in txt_castle)

        print("\n7. Очистка при роспуске клана")
        await delete_clan(clan_id)
        check("clan_buildings очищена при delete_clan",
              await get_clan_building(clan_id) is None)

    finally:
        await close_db()
        for _suffix in ("", "-wal", "-shm"):
            try:
                os.remove(_TEST_DB + _suffix)
            except OSError:
                pass

    print(f"\nИТОГО: {PASS} passed, {FAIL} failed")
    if FAIL:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
