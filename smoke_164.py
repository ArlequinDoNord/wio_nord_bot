"""Smoke 164 — Клан-холл, Фаза 4: кухня, крафтовый стол и душевые.

Проверяет:
1. Доступ к использованию расширений — только членам клана; пустой слот и
   не-крафтовое расширение отклоняются.
2. Гейт по уровню кланового расширения: рецепт выше уровня не крафтится,
   ОД и ингредиенты не списываются (и по кнопке, и в карточке рецепта).
3. Личный крафт: у двух членов клана свои ОД/ингредиенты/результат, чужой
   инвентарь не меняется.
4. Откаты: нехватка ингредиентов/ОД, сбой remove_ap — без списаний, сырьё
   возвращается, лок CRAFTING освобождается.
5. Душевые: +ОД и отрезвление по уровню, личный суточный кулдаун, общий с
   душевой в жилье.
6. Использование кухни/стола/душевых доступно во время `upgrading`
   (работы блокируют только установку/улучшение).
7. UI: кнопки использования внутри здания, список личных рецептов, карточка,
   экран душевых, результат крафта; лок CRAFTING не даёт двойной крафт.

Клан-холл закрыт флагом `config.CLAN_HALL_ENABLED`, поэтому тест включает его
явно до импорта хендлеров.

Запуск: .venv\\Scripts\\python.exe smoke_164.py
"""
import asyncio
import os
import sys

_TEST_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_test_smoke164.db")
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

    async def edit_message_reply_markup(self, chat_id=None, message_id=None,
                                        reply_markup=None, **kw):
        return None


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


def kb_texts(kb):
    if not kb:
        return []
    return [b.text for row in kb.inline_keyboard for b in row]


def has_alert(cb, needle):
    return any(t and needle in str(t) for t in cb.alerts)


def last_text(bot):
    for kind, _chat, text, _kb in reversed(bot.sent):
        if kind == "text":
            return text or ""
    return ""


async def main():
    import config
    config.DB_PATH = _TEST_DB
    config.CLAN_HALL_ENABLED = True
    import database.db as db
    db.DB_PATH = _TEST_DB
    from database.db import (
        add_clan_member,
        add_inventory_item,
        add_user,
        can_use_shower,
        choose_clan_upgrade,
        close_db,
        create_clan,
        ensure_clan_building,
        ensure_dungeon_shop_items,
        ensure_forest_items,
        ensure_life_items,
        ensure_recipes,
        get_clan_building,
        get_clan_expansion,
        get_db,
        get_inventory_item,
        get_item_by_name,
        get_recipes,
        get_user,
        init_db,
        install_clan_expansion,
        learn_recipe,
        seed_default_items,
        set_clan_building_built,
        set_clan_leader,
        set_housing_slot,
        set_player_housing,
        start_clan_upgrading,
        update_user,
    )
    from bot.handlers import clan_hall
    from bot.handlers import housing as hh
    import utils.crafting as crafting

    await init_db()
    await seed_default_items()
    await ensure_dungeon_shop_items()
    await ensure_life_items()
    await ensure_forest_items()
    await ensure_recipes()

    LEADER, MEMBER, MEMBER2, OUTSIDER = 164001, 164002, 164003, 164004
    for uid, nm in ((LEADER, "leader"), (MEMBER, "member"),
                    (MEMBER2, "member2"), (OUTSIDER, "outsider")):
        await add_user(uid, nm, nm.title(), "")
        await update_user(uid, ap=100)

    clan_id = await create_clan("clan", "Северный Бастион", "Описание", LEADER)
    await set_clan_leader(clan_id, LEADER)
    for uid in (LEADER, MEMBER, MEMBER2):
        await add_clan_member(clan_id, uid)

    await ensure_clan_building(clan_id)
    await set_clan_building_built(clan_id, "manor")
    for slot, et in ((1, "kitchen"), (2, "workbench"),
                     (3, "shower"), (4, "library")):
        ok, msg = await install_clan_expansion(clan_id, LEADER, slot, et)
        check(f"установлено расширение {et} в слот {slot}", ok is True)

    r1 = next((r for r in await get_recipes("kitchen", 1)
               if r["name"] == "Жареный опёнок"), None)
    r2 = next((r for r in await get_recipes("kitchen", 2)
               if r["name"] == "Жареный белый гриб"), None)
    rw = next((r for r in await get_recipes("workbench", 1)
               if r["name"] == "Комбинированная наживка"), None)
    check("нужные рецепты найдены", all((r1, r2, rw)))
    if not all((r1, r2, rw)):
        await close_db()
        print(f"\nSmoke 164: {PASS} passed, {FAIL} failed")
        sys.exit(1)

    for uid in (LEADER, MEMBER, MEMBER2):
        for r in (r1, r2, rw):
            await learn_recipe(uid, r["id"])

    names = ("Опёнок", "Соль", "Белый гриб", "Лапка паука", "Черви",
             "Жареный опёнок", "Комбинированная наживка")
    items = {n: await get_item_by_name(n) for n in names}
    check("все предметы для теста существуют", all(items.values()))

    async def qty(uid, name):
        it = items.get(name) or await get_item_by_name(name)
        if not it:
            return 0
        row = await get_inventory_item(uid, it["id"])
        return int(row["quantity"]) if row else 0

    async def ap(uid):
        return int((await get_user(uid))["ap"])

    # Личное сырьё: у каждого своё.
    for name, q in (("Опёнок", 2), ("Соль", 2), ("Белый гриб", 1),
                    ("Лапка паука", 1), ("Черви", 1)):
        await add_inventory_item(LEADER, items[name]["id"], q)
    for name, q in (("Опёнок", 2), ("Соль", 2), ("Белый гриб", 1)):
        await add_inventory_item(MEMBER, items[name]["id"], q)

    real_sleep = crafting.asyncio.sleep

    async def _nosleep(*a, **k):
        return None

    crafting.asyncio.sleep = _nosleep
    try:
        print("\n1. Конфиг душевых и UI внутри здания")
        check("CLAN_SHOWER_AP_BY_LEVEL: 25/50/75/100",
              config.CLAN_SHOWER_AP_BY_LEVEL == {1: 25, 2: 50, 3: 75, 4: 100})
        check("CLAN_SHOWER_SOBER_MINUTES: 60/120/180/240",
              config.CLAN_SHOWER_SOBER_MINUTES == {1: 60, 2: 120, 3: 180, 4: 240})

        cb_inside = FakeCallback(MEMBER, f"clanh:inside:{clan_id}")
        await clan_hall.clan_hall_inside_cb(cb_inside)
        inside_txt = cb_inside.message.text or ""
        inside_cbs = cbs(cb_inside.message.kb)
        check("внутри видны кухня, стол и душевые",
              "Кухня" in inside_txt and "Крафтовый стол" in inside_txt
              and "Душевые" in inside_txt)
        check("есть кнопки использования всех трёх расширений",
              f"clanh:use:{clan_id}:1" in inside_cbs
              and f"clanh:use:{clan_id}:2" in inside_cbs
              and f"clanh:use:{clan_id}:3" in inside_cbs)
        check("рядовой член не видит управление расширениями",
              f"clanh:expmanage:{clan_id}" not in inside_cbs)

        print("\n2. Доступ только членам клана")
        cb_out = FakeCallback(OUTSIDER, f"clanh:use:{clan_id}:1")
        await clan_hall.clan_hall_use_cb(cb_out)
        check("посторонний не может открыть кухню",
              has_alert(cb_out, "только членам"))
        cb_out_craft = FakeCallback(OUTSIDER, f"clanh:craft:{clan_id}:1:{r1['id']}")
        await clan_hall.clan_hall_craft_cb(cb_out_craft)
        check("посторонний не может крафтить",
              has_alert(cb_out_craft, "только членам"))
        cb_empty = FakeCallback(MEMBER, f"clanh:use:{clan_id}:5")
        await clan_hall.clan_hall_use_cb(cb_empty)
        check("пустой слот отклонён", has_alert(cb_empty, "нет расширения"))
        cb_lib = FakeCallback(MEMBER, f"clanh:use:{clan_id}:4")
        await clan_hall.clan_hall_use_cb(cb_lib)
        check("расширение следующей фазы (библиотека) пока не работает",
              has_alert(cb_lib, "пока не работает"))

        print("\n3. Экран кухни и список личных рецептов")
        cb_kitchen = FakeCallback(MEMBER, f"clanh:use:{clan_id}:1")
        await clan_hall.clan_hall_use_cb(cb_kitchen)
        kitchen_txt = cb_kitchen.message.text or ""
        kitchen_cbs = cbs(cb_kitchen.message.kb)
        check("на экране кухни подчёркнут личный крафт",
              "Крафт личный" in kitchen_txt)
        check("виден рецепт 1 уровня",
              f"clanh:recipe:{clan_id}:1:{r1['id']}" in kitchen_cbs)
        check("рецепт 2 уровня скрыт на кухне 1 ур.",
              f"clanh:recipe:{clan_id}:1:{r2['id']}" not in kitchen_cbs)
        check("рецепт 2 уровня показан как заблокированный",
              "нужно расширение выше" in kitchen_txt)

        cb_wb = FakeCallback(MEMBER, f"clanh:use:{clan_id}:2")
        await clan_hall.clan_hall_use_cb(cb_wb)
        check("на столе виден рецепт верстака",
              f"clanh:recipe:{clan_id}:2:{rw['id']}" in cbs(cb_wb.message.kb))

        print("\n4. Гейт уровня расширения (кухня 1 ур., рецепт 2 ур.)")
        ap0 = await ap(MEMBER)
        cb_gate_card = FakeCallback(MEMBER, f"clanh:recipe:{clan_id}:1:{r2['id']}")
        await clan_hall.clan_hall_recipe_cb(cb_gate_card)
        check("карточка рецепта выше уровня отклонена",
              has_alert(cb_gate_card, "выше уровня расширения"))
        cb_gate = FakeCallback(MEMBER, f"clanh:craft:{clan_id}:1:{r2['id']}")
        await clan_hall.clan_hall_craft_cb(cb_gate)
        check("крафт рецепта выше уровня отклонён",
              has_alert(cb_gate, "выше уровня расширения"))
        check("гейт: ОД не списаны", await ap(MEMBER) == ap0)
        check("гейт: ингредиенты не тронуты",
              await qty(MEMBER, "Белый гриб") == 1 and await qty(MEMBER, "Соль") == 2)
        check("гейт: CRAFTING свободен", MEMBER not in crafting.CRAFTING)

        print("\n5. Нехватка ингредиентов и ОД без списаний")
        cb_noing = FakeCallback(MEMBER2, f"clanh:craft:{clan_id}:1:{r1['id']}")
        await clan_hall.clan_hall_craft_cb(cb_noing)
        check("без ингредиентов: отказ «Нет …»",
              has_alert(cb_noing, "Нет «Опёнок»"))
        check("без ингредиентов: CRAFTING свободен",
              MEMBER2 not in crafting.CRAFTING)

        await add_inventory_item(MEMBER2, items["Опёнок"]["id"], 1)
        await add_inventory_item(MEMBER2, items["Соль"]["id"], 1)
        await update_user(MEMBER2, ap=0)
        cb_noap = FakeCallback(MEMBER2, f"clanh:craft:{clan_id}:1:{r1['id']}")
        await clan_hall.clan_hall_craft_cb(cb_noap)
        check("без ОД: отказ «Не хватает ОД»",
              has_alert(cb_noap, "Не хватает ОД"))
        check("без ОД: ингредиенты на месте",
              await qty(MEMBER2, "Опёнок") == 1 and await qty(MEMBER2, "Соль") == 1)
        await update_user(MEMBER2, ap=100)

        print("\n6. Откат при сбое remove_ap")
        ap_before = await ap(MEMBER)
        ing_before = (await qty(MEMBER, "Опёнок"), await qty(MEMBER, "Соль"))
        real_remove_ap = crafting.remove_ap

        async def _ap_deny(*a, **k):
            return False

        crafting.remove_ap = _ap_deny
        try:
            cb_rollback = FakeCallback(MEMBER, f"clanh:craft:{clan_id}:1:{r1['id']}")
            await clan_hall.clan_hall_craft_cb(cb_rollback)
        finally:
            crafting.remove_ap = real_remove_ap
        check("сбой remove_ap: «Не хватает ОД»",
              has_alert(cb_rollback, "Не хватает ОД"))
        check("сбой remove_ap: ОД не списаны", await ap(MEMBER) == ap_before)
        check("сбой remove_ap: сырьё возвращено",
              (await qty(MEMBER, "Опёнок"), await qty(MEMBER, "Соль")) == ing_before)
        check("сбой remove_ap: CRAFTING свободен", MEMBER not in crafting.CRAFTING)

        print("\n7. Личный крафт на кухне: у каждого свой результат")
        ap_m = await ap(MEMBER)
        cb_card = FakeCallback(MEMBER, f"clanh:recipe:{clan_id}:1:{r1['id']}")
        await clan_hall.clan_hall_recipe_cb(cb_card)
        check("карточка рецепта 1 ур. открыта",
              f"clanh:craft:{clan_id}:1:{r1['id']}" in cbs(cb_card.message.kb))

        bot_m = FakeBot()
        cb_m = FakeCallback(MEMBER, f"clanh:craft:{clan_id}:1:{r1['id']}", bot=bot_m)
        await clan_hall.clan_hall_craft_cb(cb_m)
        check("член клана: алерт «Начал готовить»",
              has_alert(cb_m, "Начал готовить"))
        check("член клана: итог «готово»", "готово" in last_text(bot_m))
        check("член клана: результат в своём инвентаре",
              await qty(MEMBER, "Жареный опёнок") == 1)
        check("член клана: ОД списаны (-5)", await ap(MEMBER) == ap_m - int(r1["ap_cost"]))
        check("лидер пока не получил чужой результат",
              await qty(LEADER, "Жареный опёнок") == 0)
        inv_food = await get_inventory_item(MEMBER, items["Жареный опёнок"]["id"])
        check("еда получила срок годности", bool(inv_food and inv_food["expires_at"]))
        check("после крафта CRAFTING свободен", MEMBER not in crafting.CRAFTING)

        ap_l = await ap(LEADER)
        bot_l = FakeBot()
        cb_l = FakeCallback(LEADER, f"clanh:craft:{clan_id}:1:{r1['id']}", bot=bot_l)
        await clan_hall.clan_hall_craft_cb(cb_l)
        check("лидер: свой результат в своём инвентаре",
              await qty(LEADER, "Жареный опёнок") == 1)
        check("лидер: ОД списаны со своего баланса", await ap(LEADER) == ap_l - int(r1["ap_cost"]))
        check("член клана не получил результат лидера",
              await qty(MEMBER, "Жареный опёнок") == 1)

        print("\n8. Крафтовый стол (верстак)")
        ap_w = await ap(LEADER)
        cb_w = FakeCallback(LEADER, f"clanh:craft:{clan_id}:2:{rw['id']}", bot=FakeBot())
        await clan_hall.clan_hall_craft_cb(cb_w)
        check("верстак: предмет в инвентаре лидера",
              await qty(LEADER, "Комбинированная наживка") == 1)
        check("верстак: ОД списаны", await ap(LEADER) == ap_w - int(rw["ap_cost"]))
        check("верстак: член клана не получил предмет",
              await qty(MEMBER, "Комбинированная наживка") == 0)

        print("\n9. Лок CRAFTING не даёт двойной крафт")
        ap_lock = await ap(LEADER)
        ing_lock = await qty(LEADER, "Опёнок")
        crafting.CRAFTING.add(LEADER)
        try:
            cb_lock = FakeCallback(LEADER, f"clanh:craft:{clan_id}:1:{r1['id']}")
            await clan_hall.clan_hall_craft_cb(cb_lock)
        finally:
            crafting.CRAFTING.discard(LEADER)
        check("двойной крафт отклонён", has_alert(cb_lock, "Уже готовишься"))
        check("двойной крафт: ОД и сырьё не тронуты",
              await ap(LEADER) == ap_lock and await qty(LEADER, "Опёнок") == ing_lock)

        print("\n10. Душевые: +ОД по уровню и суточный кулдаун")
        await update_user(MEMBER, ap=10)
        cb_shower = FakeCallback(MEMBER, f"clanh:use:{clan_id}:3")
        await clan_hall.clan_hall_use_cb(cb_shower)
        shower_txt = cb_shower.message.text or ""
        check("экран душевых: +25 ОД для 1 ур.", "+25 ОД" in shower_txt)
        check("экран душевых: −60 мин опьянения", "60 мин" in shower_txt)
        check("есть кнопка «Принять душ»",
              f"clanh:shower:{clan_id}:3" in cbs(cb_shower.message.kb))

        cb_use_sh = FakeCallback(MEMBER, f"clanh:shower:{clan_id}:3")
        await clan_hall.clan_hall_shower_cb(cb_use_sh)
        check("душ: +25 ОД", await ap(MEMBER) == 35)
        check("душ: алерт «Освежился»", has_alert(cb_use_sh, "Освежился"))
        check("душ: суточный кулдаун закрыт", not await can_use_shower(MEMBER))
        check("душ: после применения нет кнопки",
              f"clanh:shower:{clan_id}:3" not in cbs(cb_use_sh.message.kb))
        check("душ: экран пишет «уже мылся»",
              "уже мылся" in (cb_use_sh.message.text or ""))

        cb_again = FakeCallback(MEMBER, f"clanh:shower:{clan_id}:3")
        await clan_hall.clan_hall_shower_cb(cb_again)
        check("душ повторно: отказ", has_alert(cb_again, "уже мылся"))
        check("душ повторно: ОД не начислены", await ap(MEMBER) == 35)

        # Общий кулдаун с душевой в жилье.
        await set_player_housing(MEMBER, "apartment")
        await set_housing_slot(MEMBER, 0, "shower", 1)
        cb_home_sh = FakeCallback(MEMBER, data="housing:shower:0")
        await hh.housing_shower(cb_home_sh)
        check("жильё: общий кулдаун не даёт второй помывки",
              has_alert(cb_home_sh, "уже мылся"))
        check("жильё: ОД не начислены повторно", await ap(MEMBER) == 35)

        # Уровень 4: +100 ОД и −240 мин (проверяем именно маппинг уровня).
        conn = await get_db()
        await conn.execute(
            "UPDATE clan_expansions SET expansion_level = 4 "
            "WHERE clan_id = ? AND slot_index = 3", (clan_id,))
        await conn.commit()
        await update_user(LEADER, ap=0)
        cb_sh4_screen = FakeCallback(LEADER, f"clanh:use:{clan_id}:3")
        await clan_hall.clan_hall_use_cb(cb_sh4_screen)
        sh4_txt = cb_sh4_screen.message.text or ""
        check("душ 4 ур.: экран +100 ОД", "+100 ОД" in sh4_txt)
        check("душ 4 ур.: −240 мин в тексте", "240 мин" in sh4_txt)
        cb_sh4 = FakeCallback(LEADER, f"clanh:shower:{clan_id}:3")
        await clan_hall.clan_hall_shower_cb(cb_sh4)
        check("душ 4 ур.: +100 ОД", await ap(LEADER) == 100)
        check("душ 4 ур.: алерт +100 ОД", has_alert(cb_sh4, "+100 ОД"))
        await conn.execute(
            "UPDATE clan_expansions SET expansion_level = 1 "
            "WHERE clan_id = ? AND slot_index = 3", (clan_id,))
        await conn.commit()

        print("\n11. Использование во время upgrading")
        await choose_clan_upgrade(clan_id, LEADER)
        b = await get_clan_building(clan_id)
        check("здание переведено в upgrade_funding", b["status"] == "upgrade_funding")
        await start_clan_upgrading(
            clan_id, b["target_type"], b["required_json"] or "{}",
            int(b["price_nm"] or 0), "2099-01-01 00:00:00")
        b = await get_clan_building(clan_id)
        check("здание в статусе upgrading", b["status"] == "upgrading")

        cb_up_inside = FakeCallback(MEMBER2, f"clanh:inside:{clan_id}")
        await clan_hall.clan_hall_inside_cb(cb_up_inside)
        up_cbs = cbs(cb_up_inside.message.kb)
        check("во время работ кнопки использования остались",
              f"clanh:use:{clan_id}:1" in up_cbs
              and f"clanh:use:{clan_id}:3" in up_cbs)
        check("во время работ управления расширениями нет",
              f"clanh:expmanage:{clan_id}" not in up_cbs)

        ap_up = await ap(MEMBER2)
        bot_up = FakeBot()
        cb_up_craft = FakeCallback(MEMBER2, f"clanh:craft:{clan_id}:1:{r1['id']}",
                                   bot=bot_up)
        await clan_hall.clan_hall_craft_cb(cb_up_craft)
        check("во время upgrading крафт работает",
              has_alert(cb_up_craft, "Начал готовить")
              and await qty(MEMBER2, "Жареный опёнок") == 1)
        check("во время upgrading ОД списаны",
              await ap(MEMBER2) == ap_up - int(r1["ap_cost"]))

        await update_user(MEMBER2, ap=10)
        cb_up_sh = FakeCallback(MEMBER2, f"clanh:shower:{clan_id}:3")
        await clan_hall.clan_hall_shower_cb(cb_up_sh)
        check("во время upgrading душевые работают",
              await ap(MEMBER2) == 35 and has_alert(cb_up_sh, "Освежился"))

        # Возвращаем готовое здание для чистоты завершения теста.
        await set_clan_building_built(clan_id, "manor")
        check("здание снова built",
              (await get_clan_building(clan_id))["status"] == "built")

        print("\n12. Инварианты данных")
        exp = await get_clan_expansion(clan_id, 1)
        check("кухня осталась в слоте 1",
              exp is not None and exp["expansion_type"] == "kitchen")
        check("CRAFTING пуст после всех сценариев",
              not crafting.CRAFTING)
        check("расширения не списывали клановый склад (личный крафт)",
              await qty(LEADER, "Жареный опёнок") == 1)
    finally:
        crafting.asyncio.sleep = real_sleep
        await close_db()

    print(f"\nSmoke 164: {PASS} passed, {FAIL} failed")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except SystemExit:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        from database.db import close_db
        try:
            asyncio.run(close_db())
        except Exception:
            pass
        print(f"SMOKE ERROR: {e!r}")
        sys.exit(1)
