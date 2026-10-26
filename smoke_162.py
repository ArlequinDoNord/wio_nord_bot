"""Smoke 162 — Клан-холл, Фаза 2: апгрейд здания по варианту A.

Проверяет:
1. Цепочку уровней `house -> manor -> castle` (`next_clan_building_type`).
2. Выбор улучшения `choose_clan_upgrade` / `clanh:upgrade:`: только глава,
   только из `built`, снимок требований/цены целевого уровня, статус
   `upgrade_funding`; повторный выбор и выбор первого проекта во время сбора
   запрещены.
3. Отмену улучшения `cancel_clan_building` / `clanh:cancel:`: возврат в `built`,
   очистка `target_type`/снимка, фото и ресурсы сохраняются.
4. Сбор на улучшение: экран `upgrade_funding`, отказ при нехватке ресурсов/НМ,
   старт с ресурсами (`clanh:start:`) — списание ровно по норме целевого уровня,
   текущий `building_type` не меняется, статус `upgrading`, срок целевого уровня,
   уведомление членам клана.
5. Поведение во время работ: вход доступен, слоты/лимиты текущего уровня,
   расширения заблокированы, показывается заглушка стройки, кнопки улучшения нет.
6. Завершение по таймеру: `upgraded`, `building_type` = цель, `target_type` и
   снимок очищены, индивидуальное фото сброшено (дефолт уровня), идемпотентность.
7. Апгрейд без сбора ресурсов (`clanh:startfull:`) — двойная цена, склад не тронут.
8. Максимальный уровень (`castle`): улучшать больше нельзя, кнопки нет.

Клан-холл закрыт флагом `config.CLAN_HALL_ENABLED`, поэтому тест включает его
явно до импорта хендлеров.

Запуск: .venv\\Scripts\\python.exe smoke_162.py
"""
import asyncio
import json
import os
import sys
from datetime import datetime, timedelta, timezone

_TEST_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_test_smoke162.db")
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
        get_clan_building, ensure_clan_building,
        choose_clan_building, choose_clan_upgrade, cancel_clan_building,
        next_clan_building_type,
        get_clan_project_progress, start_clan_building_project,
        set_clan_building_built,
        resolve_clan_building, resolve_due_clan_buildings,
        set_clan_building_photo, get_clan_construction_photo,
        set_clan_construction_photo,
    )
    from bot.handlers import clan_hall

    await init_db()
    await ensure_logging_items()
    await ensure_mine_items()

    LEADER, MEMBER, OUTSIDER = 162001, 162002, 162003
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
    conn = await get_db()

    try:
        print("\n1. Цепочка уровней и выбор улучшения")
        check("house -> manor", next_clan_building_type("house") == "manor")
        check("manor -> castle", next_clan_building_type("manor") == "castle")
        check("castle — максимальный уровень", next_clan_building_type("castle") is None)
        check("неизвестный/пустой тип — нет цели",
              next_clan_building_type(None) is None
              and next_clan_building_type("palace") is None)

        # Готовый дом с индивидуальным фото
        await ensure_clan_building(clan_id)
        await set_clan_building_built(clan_id, "house")
        await set_clan_building_photo(clan_id, "file_id_house_photo")
        b = await get_clan_building(clan_id)
        check("подготовлен построенный дом с фото",
              b["status"] == "built" and b["building_type"] == "house"
              and b["building_photo_file_id"] == "file_id_house_photo")

        cb_member = FakeCallback(MEMBER, f"clanh:hall:{clan_id}")
        await clan_hall.clan_hall_cb(cb_member)
        check("рядовой член не видит кнопку улучшения",
              f"clanh:upgrade:{clan_id}" not in cbs(cb_member.message.kb))

        cb_leader = FakeCallback(LEADER, f"clanh:hall:{clan_id}")
        await clan_hall.clan_hall_cb(cb_leader)
        check("глава видит кнопку «Улучшить до поместья»",
              f"clanh:upgrade:{clan_id}" in cbs(cb_leader.message.kb)
              and any("Улучшить до" in t and "поместье" in t.lower()
                      for t in kb_texts(cb_leader.message.kb)))
        check("на экране готового дома индивидуальное фото",
              cb_leader.message.media_photo == "file_id_house_photo")

        ok_m, _ = await choose_clan_upgrade(clan_id, MEMBER)
        check("рядовой не может выбрать улучшение", ok_m is False)
        ok_p, _ = await choose_clan_upgrade(party_id, LEADER)
        check("партии улучшение недоступно", ok_p is False)
        ok_o, _ = await choose_clan_upgrade(clan_id, OUTSIDER)
        check("посторонний не может выбрать улучшение", ok_o is False)

        cb_up = FakeCallback(LEADER, f"clanh:upgrade:{clan_id}")
        await clan_hall.clan_hall_upgrade_cb(cb_up)
        b = await get_clan_building(clan_id)
        check("улучшение выбрано: статус upgrade_funding",
              b["status"] == "upgrade_funding")
        check("текущий уровень остался house, цель — manor",
              b["building_type"] == "house" and b["target_type"] == "manor")
        check("снимок цены — цена поместья (8000 НМ)", b["price_nm"] == 8000)
        check("снимок требований — требования поместья",
              json.loads(b["required_json"]) == {"Доска": 150, "Бревна": 60,
                                                 "Железная руда": 50})
        check("chosen_at переставлен на текущий момент", bool(b["chosen_at"]))

        ok_again, _ = await choose_clan_upgrade(clan_id, LEADER)
        check("повторно улучшение во время сбора не выбрать", ok_again is False)
        ok_build_same, _ = await choose_clan_building(clan_id, LEADER, "castle")
        check("выбор первого проекта во время улучшения запрещён",
              ok_build_same is False)

        print("\n2. Отмена улучшения")
        ok_cancel_m, _ = await cancel_clan_building(clan_id, MEMBER)
        check("рядовой не может отменить улучшение", ok_cancel_m is False)

        cb_cancel = FakeCallback(LEADER, f"clanh:cancel:{clan_id}")
        await clan_hall.clan_hall_cancel_cb(cb_cancel)
        b = await get_clan_building(clan_id)
        check("отмена возвращает в built, уровень прежний",
              b["status"] == "built" and b["building_type"] == "house")
        check("отмена очищает цель, снимок и цену",
              b["target_type"] is None and b["required_json"] is None
              and b["price_nm"] == 0)
        check("фото здания после отмены сохранилось",
              b["building_photo_file_id"] == "file_id_house_photo")

        # Снова выбираем улучшение для дальнейших проверок
        ok_re, _ = await choose_clan_upgrade(clan_id, LEADER)
        check("улучшение можно выбрать повторно", ok_re is True)

        print("\n3. Экран сбора на улучшение и старт с ресурсами")
        cb_fund = FakeCallback(LEADER, f"clanh:hall:{clan_id}")
        await clan_hall.clan_hall_cb(cb_fund)
        fund_txt = cb_fund.message.text or ""
        check("экран сбора подписан как улучшение",
              "Улучшение" in fund_txt and "Сбор ресурсов на улучшение" in fund_txt)
        check("на экране видны текущий и целевой уровни",
              "Дом Клана" in fund_txt and "Клановое поместье" in fund_txt)
        check("без полного комплекта кнопки старта нет",
              f"clanh:start:{clan_id}" not in cbs(cb_fund.message.kb))
        check("кнопка «без ресурсов» и отмена улучшения на месте",
              f"clanh:startfull:{clan_id}" in cbs(cb_fund.message.kb)
              and f"clanh:cancel:{clan_id}" in cbs(cb_fund.message.kb)
              and any("Отменить улучшение" in t for t in kb_texts(cb_fund.message.kb)))
        check("на экране видна двойная цена 16000 НМ",
              "16000 НМ" in fund_txt and "двойная цена" in fund_txt)

        prog, all_ok = await get_clan_project_progress(clan_id)
        check("прогресс пуст (0/150 досок)", all_ok is False and len(prog) == 3)
        ok_early, _, _ = await start_clan_building_project(clan_id, LEADER)
        check("старт улучшения без ресурсов отклонён", ok_early is False)

        # Ресурсов чуть меньше нормы
        await add_clan_storage(clan_id, plank["id"], 149)
        await add_clan_storage(clan_id, wood["id"], 60)
        await add_clan_storage(clan_id, ore["id"], 50)
        ok_short, _, _ = await start_clan_building_project(clan_id, LEADER)
        check("старт улучшения при нехватке 1 доски отклонён", ok_short is False)

        # Досыпаем до нормы + запас 5 по каждому ресурсу
        await add_clan_storage(clan_id, plank["id"], 6)   # 149 + 6 = 155
        await add_clan_storage(clan_id, wood["id"], 5)    # 65
        await add_clan_storage(clan_id, ore["id"], 5)     # 55
        _, all_ok2 = await get_clan_project_progress(clan_id)
        check("все ресурсы на улучшение собраны", all_ok2 is True)

        # НМ не хватает (у главы только стартовые 10)
        ok_no_nm, msg_no_nm, _ = await start_clan_building_project(clan_id, LEADER)
        check("старт без НМ у главы отклонён",
              ok_no_nm is False and "нордмарок" in msg_no_nm)

        await add_nordmarks(LEADER, 10000, "test", "на улучшение")
        nm_before = (await get_user(LEADER))["nordmarks"]
        bot = FakeBot()
        cb_start = FakeCallback(LEADER, f"clanh:start:{clan_id}", bot=bot)
        await clan_hall.clan_hall_start_cb(cb_start)
        b = await get_clan_building(clan_id)
        check("статус перешёл в upgrading", b["status"] == "upgrading")
        check("текущий уровень во время работ остался house",
              b["building_type"] == "house" and b["target_type"] == "manor")
        check("с главы списано ровно 8000 НМ",
              (await get_user(LEADER))["nordmarks"] == nm_before - 8000)
        check("ресурсы списаны ровно по норме (излишки 5/5/5)",
              await get_clan_storage_qty(clan_id, plank["id"]) == 5
              and await get_clan_storage_qty(clan_id, wood["id"]) == 5
              and await get_clan_storage_qty(clan_id, ore["id"]) == 5)
        tx_cur = await conn.execute(
            "SELECT * FROM transactions WHERE from_user = ? AND tx_type = 'clan_build' "
            "ORDER BY rowid DESC LIMIT 1", (LEADER,))
        tx_row = await tx_cur.fetchone()
        check("транзакция clan_build на 8000 с пометкой улучшения",
              tx_row is not None and tx_row["amount"] == 8000
              and "Улучшение" in (tx_row["description"] or ""))
        check("уведомление об улучшении ушло обоим членам клана",
              len(bot.sent) == 2 and {u for u, _ in bot.sent} == {LEADER, MEMBER}
              and all("Улучшение начато" in t for _, t in bot.sent))

        completes = datetime.strptime(str(b["completes_at"]), "%Y-%m-%d %H:%M:%S")
        now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
        delta_days = (completes - now_utc).total_seconds() / 86400
        check("поместье строится 4 дня", 3.9 <= delta_days <= 4.01)

        print("\n4. Поведение во время работ")
        await set_clan_construction_photo("file_id_construction_stub")
        check("заглушка стройки сохранена",
              await get_clan_construction_photo() == "file_id_construction_stub")
        photo_during = await clan_hall.resolve_clan_hall_photo(b)
        check("во время улучшения показывается заглушка стройки, а не фото дома",
              photo_during == "file_id_construction_stub")

        cb_hall_up = FakeCallback(LEADER, f"clanh:hall:{clan_id}")
        await clan_hall.clan_hall_cb(cb_hall_up)
        up_txt = cb_hall_up.message.text or ""
        check("на экране работ написано «Идёт улучшение» до поместья",
              "Идёт улучшение" in up_txt and "поместье" in up_txt.lower())
        check("кнопки улучшения во время работ нет",
              f"clanh:upgrade:{clan_id}" not in cbs(cb_hall_up.message.kb))

        cb_inside = FakeCallback(MEMBER, f"clanh:inside:{clan_id}")
        await clan_hall.clan_hall_inside_cb(cb_inside)
        inside_txt = cb_inside.message.text or ""
        check("вход во время улучшения доступен",
              not any("не построено" in (a or "") for a in cb_inside.alerts))
        check("внутри остаются слоты текущего уровня (2)",
              "Слоты расширений (2 шт." in inside_txt)
        check("внутри предупреждение о блокировке расширений",
              "Идёт улучшение" in inside_txt
              and "расширения нельзя" in inside_txt.lower())

        due0 = await resolve_due_clan_buildings()
        check("пока таймер не вышел — работ не завершаем", len(due0) == 0)

        print("\n5. Завершение улучшения и сброс фото")
        past = (datetime.now(timezone.utc) - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
        await conn.execute("UPDATE clan_buildings SET completes_at = ? WHERE clan_id = ?",
                           (past, clan_id))
        await conn.commit()

        due1 = await resolve_due_clan_buildings()
        check("resolve завершил улучшение событием upgraded",
              len(due1) == 1 and due1[0]["event"] == "upgraded"
              and due1[0]["building_type"] == "manor")
        due2 = await resolve_due_clan_buildings()
        check("повторный resolve идемпотентен", len(due2) == 0)

        b = await resolve_clan_building(clan_id)
        check("после улучшения статус built, тип manor",
              b["status"] == "built" and b["building_type"] == "manor")
        check("цель, снимок и цена очищены",
              b["target_type"] is None and b["required_json"] is None
              and b["price_nm"] == 0)
        check("индивидуальное фото дома сброшено",
              not (b["building_photo_file_id"] or "").strip())
        check("фото уровня по умолчанию отсутствует (дефолт картинки)",
              await clan_hall.resolve_clan_hall_photo(b) is None)

        cb_manor = FakeCallback(LEADER, f"clanh:hall:{clan_id}")
        await clan_hall.clan_hall_cb(cb_manor)
        check("на поместье глава видит улучшение до резиденции",
              f"clanh:upgrade:{clan_id}" in cbs(cb_manor.message.kb)
              and any("резиденц" in t.lower() for t in kb_texts(cb_manor.message.kb)))

        print("\n6. Улучшение без ресурсов и максимальный уровень")
        ok_castle, _ = await choose_clan_upgrade(clan_id, LEADER)
        check("выбрано улучшение поместья до резиденции", ok_castle is True)
        b = await get_clan_building(clan_id)
        check("цель — castle, цена 20000",
              b["target_type"] == "castle" and b["price_nm"] == 20000)

        # Отмена и повторный выбор — проверяем ветку для второго уровня
        ok_c2, _ = await cancel_clan_building(clan_id, LEADER)
        b = await get_clan_building(clan_id)
        check("отмена улучшения поместья возвращает в built manor",
              ok_c2 is True and b["status"] == "built"
              and b["building_type"] == "manor" and b["target_type"] is None)

        await choose_clan_upgrade(clan_id, LEADER)
        await add_nordmarks(LEADER, 50000, "test", "двойная оплата резиденции")
        nm_before2 = (await get_user(LEADER))["nordmarks"]
        plank_before2 = await get_clan_storage_qty(clan_id, plank["id"])
        bot2 = FakeBot()
        cb_full = FakeCallback(LEADER, f"clanh:startfull:{clan_id}", bot=bot2)
        await clan_hall.clan_hall_startfull_cb(cb_full)
        b = await get_clan_building(clan_id)
        check("без ресурсов: статус upgrading, тип manor, цель castle",
              b["status"] == "upgrading" and b["building_type"] == "manor"
              and b["target_type"] == "castle")
        check("без ресурсов: списана двойная цена 40000 НМ",
              (await get_user(LEADER))["nordmarks"] == nm_before2 - 40000)
        check("без ресурсов: склад клана не тронут",
              await get_clan_storage_qty(clan_id, plank["id"]) == plank_before2)
        check("уведомление об улучшении без ресурсов отправлено",
              len(bot2.sent) == 2
              and all("Улучшение начато без сбора ресурсов" in t for _, t in bot2.sent))

        past = (datetime.now(timezone.utc) - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
        await conn.execute("UPDATE clan_buildings SET completes_at = ? WHERE clan_id = ?",
                           (past, clan_id))
        await conn.commit()
        due3 = await resolve_due_clan_buildings()
        check("резиденция достроена событием upgraded",
              len(due3) == 1 and due3[0]["event"] == "upgraded"
              and due3[0]["building_type"] == "castle")
        b = await get_clan_building(clan_id)
        check("тип castle, фото и цель очищены",
              b["status"] == "built" and b["building_type"] == "castle"
              and b["target_type"] is None
              and not (b["building_photo_file_id"] or "").strip())

        ok_max, msg_max = await choose_clan_upgrade(clan_id, LEADER)
        check("с максимального уровня улучшать нельзя",
              ok_max is False and "максимального" in msg_max)
        cb_max = FakeCallback(LEADER, f"clanh:hall:{clan_id}")
        await clan_hall.clan_hall_cb(cb_max)
        check("на резиденции кнопки улучшения нет",
              f"clanh:upgrade:{clan_id}" not in cbs(cb_max.message.kb))
        check("в резиденции 7 слотов, 7-й резервный",
              "7. 🔒" in (clan_hall.build_hall_inside_text(
                  {"name": "Северный Бастион"}, {"building_type": "castle"}) or ""))

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
