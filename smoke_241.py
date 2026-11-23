"""Smoke v0.43.27: здание КГБ и паспорта Нордхайма.

Проверяет:
1. Вход в здание: глава КГБ и Хранитель пускаются, обычный пилот — нет.
2. Выдача паспорта только главой КГБ (Хранитель — нет); кнопка есть только у главы.
3. Пошаговый ввод (FSM): фото/без фото, серия 4 цифры, номер 6 цифр, дата ДД.ММ.ГГГГ,
   пол кнопками, «сегодня», «нет» в особых приметах; ошибки ввода не сбивают шаг.
4. Занятый номер другого пилота отклоняется.
5. Выдача: паспорт в БД, предмет в инвентаре (категория «Документы»), уведомление пилоту.
6. Перевыдача заменяет данные и не дублирует предмет в инвентаре.
7. Профиль показывает серию и номер; карточка в инвентаре — паспорт.
8. Предмет не продаётся и не передаётся; показ на английском.

Запуск: .venv\\Scripts\\python.exe smoke_241.py
"""
import asyncio
import os
import sys
from types import SimpleNamespace

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke241.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB
_ADMIN_ID = 441001
os.environ["ADMIN_IDS"] = str(_ADMIN_ID)

sys.path.insert(0, os.path.dirname(__file__))

HEAD = 441010
PLAIN = 441011
TARGET = 441012
OTHER = 441013


class FakeMessage:
    def __init__(self, user_id, text=None, photo=None):
        self.from_user = SimpleNamespace(id=user_id)
        self.text = text
        self.photo = photo
        self.sent = []
        self.deleted = False

    async def answer(self, text=None, *a, **kw):
        self.sent.append(("text", text, kw))

    async def answer_photo(self, photo=None, caption=None, *a, **kw):
        self.sent.append(("photo", caption, kw))

    async def delete(self):
        self.deleted = True


class FakeCallback:
    def __init__(self, user_id, data="", message=None):
        self.from_user = SimpleNamespace(id=user_id)
        self.data = data
        self.message = message or FakeMessage(user_id)
        self.bot = FakeBot()

    async def answer(self, *a, **kw):
        return None


class FakeBot:
    def __init__(self):
        self.sent = []

    async def send_message(self, chat_id, text, **kw):
        self.sent.append((chat_id, text))


def texts(msg):
    return [item[1] for item in msg.sent if item[1]]


def buttons(msg):
    out = []
    for _, _, kw in msg.sent:
        markup = kw.get("reply_markup")
        if markup:
            for row in markup.inline_keyboard:
                out.extend((b.text, b.callback_data) for b in row)
    return out


async def run():
    from aiogram.fsm.context import FSMContext
    from aiogram.fsm.storage.base import StorageKey
    from aiogram.fsm.storage.memory import MemoryStorage

    from config import PASSPORT_ITEM_NAME
    from database.db import (
        init_db, close_db, add_user, add_user_role, get_status_by_tag, grant_status,
        get_passport, get_item_by_name, get_inventory_item, issue_passport, get_user,
        ensure_passport_item,
    )
    from bot.handlers import kgb as K
    from bot.handlers import profile as P
    from bot.handlers import inventory as INV
    from utils.permissions import can_enter_kgb, is_kgb_head
    from utils.passports import format_passport
    from utils.localization import t, use_lang
    from keyboards.keyboards import ADMIN_QUARTER_KEYS
    from bot.handlers.locations import LOCATION_ACCESS_LINES

    await init_db()
    await ensure_passport_item()
    passed = failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
        else:
            failed += 1
            print(f"  FAIL: {name}")

    storage = MemoryStorage()

    def state_for(uid):
        return FSMContext(storage=storage, key=StorageKey(bot_id=1, chat_id=uid, user_id=uid))

    try:
        for uid, name in ((_ADMIN_ID, "Хранитель"), (HEAD, "Глава"), (PLAIN, "Пилот"),
                          (TARGET, "Цель"), (OTHER, "Другой")):
            await add_user(uid, f"u{uid}", name, "")
        recruit = await get_status_by_tag("recruit")
        for uid in (HEAD, PLAIN, TARGET, OTHER):
            await grant_status(uid, recruit["id"], 0)
        await add_user_role(HEAD, "kgb_head", granted_by=_ADMIN_ID)

        # 1–2. Доступ
        check("глава КГБ входит", await can_enter_kgb(HEAD))
        check("Хранитель входит", await can_enter_kgb(_ADMIN_ID))
        check("обычный пилот не входит", not await can_enter_kgb(PLAIN))
        check("глава КГБ выдаёт паспорта", await is_kgb_head(HEAD))
        check("Хранитель НЕ выдаёт паспорта", not await is_kgb_head(_ADMIN_ID))

        cb_menu_head = FakeCallback(HEAD, "kgb:menu")
        await K.kgb_menu_cb(cb_menu_head)
        check("меню главы: есть «Выдать паспорт»",
              any(cb == "kgb:issue" for _, cb in buttons(cb_menu_head.message)))

        cb_menu_admin = FakeCallback(_ADMIN_ID, "kgb:menu")
        await K.kgb_menu_cb(cb_menu_admin)
        check("меню Хранителя: кнопки выдачи нет",
              not any(cb == "kgb:issue" for _, cb in buttons(cb_menu_admin.message)))

        cb_menu_plain = FakeCallback(PLAIN, "kgb:menu")
        await K.kgb_menu_cb(cb_menu_plain)
        check("пилоту — отказ входа", any(t("kgb.no_access") == x for x in texts(cb_menu_plain.message)))

        cb_issue_admin = FakeCallback(_ADMIN_ID, "kgb:issue", message=FakeMessage(_ADMIN_ID))
        await K.kgb_issue_start(cb_issue_admin, state_for(_ADMIN_ID))
        check("Хранитель не открывает выдачу", t("kgb.head_only") in texts(cb_issue_admin.message))

        # 3. Пошаговый ввод
        st = state_for(HEAD)
        cb_pick = FakeCallback(HEAD, "kgb:issue", message=FakeMessage(HEAD))
        await K.kgb_issue_start(cb_pick, st)
        check("список пилотов содержит цель",
              any(cb == f"kgb:user:{TARGET}" for _, cb in buttons(cb_pick.message)))

        cb_target = FakeCallback(HEAD, f"kgb:user:{TARGET}", message=FakeMessage(HEAD))
        await K.kgb_issue_target(cb_target, st)
        check("после выбора — шаг фото", await st.get_state() == K.KgbPassport.photo.state)

        cb_skip = FakeCallback(HEAD, "kgb:nophoto", message=FakeMessage(HEAD))
        await K.kgb_photo_skip(cb_skip, st)
        check("без фото — шаг серии", await st.get_state() == K.KgbPassport.series.state)

        await K.kgb_text_step(FakeMessage(HEAD, text="12"), st)
        check("серия «12» отклонена", await st.get_state() == K.KgbPassport.series.state)
        await K.kgb_text_step(FakeMessage(HEAD, text="1234"), st)
        check("серия 1234 принята", await st.get_state() == K.KgbPassport.number.state)

        await K.kgb_text_step(FakeMessage(HEAD, text="12345"), st)
        check("номер из 5 цифр отклонён", await st.get_state() == K.KgbPassport.number.state)

        # Занятый номер другого пилота
        await issue_passport(OTHER, {"series": "1234", "number": "999999", "full_name": "Другой",
                                     "position": "—", "rank": "—", "sex": "m",
                                     "marital_status": "—", "birth_date": "01.01.1990",
                                     "issue_date": "01.01.2026", "distinguishing_marks": "нет",
                                     "photo_file_id": None}, issued_by=HEAD)
        await K.kgb_text_step(FakeMessage(HEAD, text="2222"), st)
        await K.kgb_text_step(FakeMessage(HEAD, text="999999"), st)
        check("занятый номер отклонён", await st.get_state() == K.KgbPassport.number.state)
        await K.kgb_text_step(FakeMessage(HEAD, text="654321"), st)
        check("свободный номер принят", await st.get_state() == K.KgbPassport.full_name.state)

        await K.kgb_text_step(FakeMessage(HEAD, text="Иван Петров"), st)
        await K.kgb_text_step(FakeMessage(HEAD, text="Пилот авиакрыла"), st)
        await K.kgb_text_step(FakeMessage(HEAD, text="Сержант"), st)
        check("дойдён до пола", await st.get_state() == K.KgbPassport.sex.state)
        wrong_sex = FakeMessage(HEAD, text="мужчина")
        await K.kgb_sex_wrong(wrong_sex)
        check("текст вместо кнопки пола — повтор вопроса с кнопками",
              t("kgb.ask_sex") in texts(wrong_sex) and await st.get_state() == K.KgbPassport.sex.state)
        cb_sex = FakeCallback(HEAD, "kgb:sex:m", message=FakeMessage(HEAD))
        await K.kgb_sex_step(cb_sex, st)
        check("пол выбран кнопкой", await st.get_state() == K.KgbPassport.marital.state)

        await K.kgb_text_step(FakeMessage(HEAD, text="Холост"), st)
        await K.kgb_text_step(FakeMessage(HEAD, text="32.13.1990"), st)
        check("неверная дата отклонена", await st.get_state() == K.KgbPassport.birth.state)
        await K.kgb_text_step(FakeMessage(HEAD, text="05.03.1990"), st)
        await K.kgb_text_step(FakeMessage(HEAD, text="сегодня"), st)
        await K.kgb_text_step(FakeMessage(HEAD, text="нет"), st)
        check("после примет — карточка на подтверждение",
              await st.get_state() == K.KgbPassport.confirm.state)

        # 5. Выдача
        cb_ok = FakeCallback(HEAD, "kgb:confirm", message=FakeMessage(HEAD))
        await K.kgb_confirm(cb_ok, st)
        p = await get_passport(TARGET)
        check("паспорт сохранён", p is not None and p["series"] == "1234" and p["number"] == "654321")
        check("пол и дата рождения сохранены", p["sex"] == "m" and p["birth_date"] == "05.03.1990")
        check("дата выдачи «сегодня» подставлена", len(p["issue_date"]) == 10)
        check("issued_by — глава КГБ", int(p["issued_by"]) == HEAD)
        item = await get_item_by_name(PASSPORT_ITEM_NAME)
        inv = await get_inventory_item(TARGET, item["id"])
        check("предмет в инвентаре пилота, 1 шт.", inv is not None and inv["quantity"] == 1)
        check("категория предмета «documents»", item["category"] == "documents")
        check("пилот получил уведомление",
              any(chat == TARGET and "паспорт" in txt for chat, txt in cb_ok.bot.sent))
        check("состояние FSM очищено", await st.get_state() is None)

        # 6. Перевыдача
        st2 = state_for(HEAD)
        await K.kgb_issue_target(FakeCallback(HEAD, f"kgb:user:{TARGET}", message=FakeMessage(HEAD)), st2)
        cb_warn = FakeCallback(HEAD, "kgb:nophoto", message=FakeMessage(HEAD))
        await K.kgb_photo_skip(cb_warn, st2)
        for value in ("1234", "777777", "Иван", "Пилот", "Сержант"):
            await K.kgb_text_step(FakeMessage(HEAD, text=value), st2)
        await K.kgb_sex_step(FakeCallback(HEAD, "kgb:sex:f", message=FakeMessage(HEAD)), st2)
        for value in ("Замужем", "01.01.1995", "01.01.2026", "шрам"):
            await K.kgb_text_step(FakeMessage(HEAD, text=value), st2)
        await K.kgb_confirm(FakeCallback(HEAD, "kgb:confirm", message=FakeMessage(HEAD)), st2)
        p2 = await get_passport(TARGET)
        check("перевыдача заменила номер", p2["number"] == "777777" and p2["sex"] == "f")
        inv2 = await get_inventory_item(TARGET, item["id"])
        check("перевыдача не дублирует предмет", inv2["quantity"] == 1)

        # 7. Профиль и инвентарь
        caption, _ = await P._profile_caption(TARGET)
        check("профиль: серия и номер", "1234" in caption and "777777" in caption)
        check("профиль без паспорта: строка «не выдан»",
              "не выдан" in (await P._profile_caption(PLAIN))[0])
        card_msg = FakeMessage(TARGET)
        await K.render_passport_card(card_msg, TARGET)
        check("карточка паспорта в инвентаре", any("1234" in (c or "") for _, c, _ in card_msg.sent))
        check("в карточке — особые приметы", any("шрам" in (c or "") for _, c, _ in card_msg.sent))
        from database.db import get_inventory
        inv_items = await get_inventory(TARGET)
        menu_kb = INV.inv_categories_markup(inv_items, [])
        check("меню инвентаря: раздел «Документы»",
              any(b.callback_data == "inventory:cat:documents"
                  for row in menu_kb.inline_keyboard for b in row))
        open_msg = FakeMessage(TARGET)
        await INV._render_item_card(open_msg, TARGET, item["id"])
        check("открытие паспорта из инвентаря — карточка паспорта",
              any("1234" in (c or "") for _, c, _ in open_msg.sent))

        # 8. Непродаваемость, непередаваемость, английский
        check("предмет не продаётся (цена продажи 0)", int(item["sell_price"] or 0) == 0)
        check("предмет скрыт из магазина", int(item["is_available"] or 0) == 0)
        from database.db import UNTRANSFERABLE_ITEMS
        check("предмет нельзя передать", PASSPORT_ITEM_NAME in UNTRANSFERABLE_ITEMS)
        check("формат карточки: серия из текста формата",
              "Серия: 1234" in format_passport(p))

        check("паспорт — категория «Документы»", "documents" in INV.INV_CATEGORIES)
        check("квартал содержит КГБ", "kgb" in ADMIN_QUARTER_KEYS)
        from database.db import get_all_locations
        check("КГБ в редакторе локаций (картинки по времени суток и сезонам)",
              any(l["key"] == "kgb" for l in await get_all_locations()))
        check("вход в КГБ описан строкой доступа", "kgb" in LOCATION_ACCESS_LINES)

        use_lang("en")
        try:
            check("EN: заголовок карточки", t("kgb.card_title") == "🛂 NORDHEIM PASSPORT")
            check("EN: строка профиля", "Passport: series 1234" in t(
                "profile.passport", series="1234", number="777777"))
        finally:
            use_lang("ru")
    finally:
        await close_db()
        if os.path.exists(_TEST_DB):
            os.remove(_TEST_DB)

    print(f"\nSmoke 241: {passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)


asyncio.run(run())
