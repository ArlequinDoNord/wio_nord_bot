"""Smoke v0.30.0: жильё — расширение «Душевая».

Проверяет:
1. Сид предметов «Душевая» (ур. 1) и «Ванная с душем» (ур. 2), категория furniture.
2. Карты расширения: FURNITURE_BY_EXPANSION/ITEM, EXPANSION_LABELS, иконка/имя,
   SHOWER_AP_BY_LEVEL = {1: 25, 2: 50}.
3. Экран комнаты душевой даёт кнопку «Принять душ» и показывает +25 ОД.
4. Применение: +25 ОД, отметка суток; повторно в тот же день — отказ, ОД не растут.
5. Смена игровых суток открывает лимит снова (can_use_shower).
6. daily_ap_recovery обнуляет shower_used_today при смене суток.
7. Апгрейд: установка «Ванной с душем» заменяет «Душевую» (возврат в инвентарь),
   слот повышается до 2 ур.; применение даёт +50 ОД.
8. Душ/ванна сокращают опьянение: душевая −60 мин, ванная −180 мин («пьян» и
   «очень пьян»); короткое опьянение снимается полностью.

Запуск: .venv\\Scripts\\python.exe smoke_147.py
"""
import asyncio
import os
import sys
from types import SimpleNamespace

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke147.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB

sys.path.insert(0, os.path.dirname(__file__))


class FakeSender:
    def __init__(self):
        self.sent = []

    async def send_message(self, chat_id, text, reply_markup=None, **kw):
        m = SimpleNamespace(message_id=len(self.sent) + 1)
        self.sent.append(("text", chat_id, text, reply_markup))
        return m

    async def send_photo(self, chat_id, photo, caption=None, reply_markup=None, **kw):
        m = SimpleNamespace(message_id=len(self.sent) + 1)
        self.sent.append(("photo", chat_id, caption or "", reply_markup))
        return m


class FakeMessage:
    def __init__(self, user_id, bot=None):
        self.from_user = SimpleNamespace(id=user_id)
        self.chat = SimpleNamespace(id=user_id)
        self.bot = bot or FakeSender()
        self.sent = []

    async def answer(self, *a, **kw):
        self.sent.append(("answer", a, kw))

    async def __getattr__(self, name):
        async def _noop(*a, **kw):
            return None
        return _noop


class FakeCallback:
    def __init__(self, user_id, data="", message=None, bot=None):
        self.from_user = SimpleNamespace(id=user_id)
        self.bot = bot or FakeSender()
        self.message = message or FakeMessage(user_id, self.bot)
        self.data = data
        self.alerts = []

    async def answer(self, text=None, *a, **kw):
        self.alerts.append(text)


def markup_callbacks(markup):
    if not markup:
        return set()
    out = set()
    for row in getattr(markup, "inline_keyboard", []):
        for btn in row:
            out.add(btn.callback_data)
    return out


def last_bot_send(bot):
    if not bot.sent:
        return "", None
    _, _chat, text, markup = bot.sent[-1]
    return text or "", markup


async def run():
    from database.db import (
        init_db, close_db, seed_default_items, ensure_life_items,
        get_user, get_item_by_name, add_inventory_item, get_inventory,
        set_player_housing, set_housing_slot, get_housing_slots, add_user,
        update_user, can_use_shower, today_report_day, daily_ap_recovery,
    )
    from bot.handlers import housing as hh

    await init_db()
    await seed_default_items()
    await ensure_life_items()

    passed = 0
    failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
        else:
            failed += 1
            print(f"  FAIL: {name}")

    async def inv_qty(uid, name):
        it = await get_item_by_name(name)
        if not it:
            return 0
        inv = await get_inventory(uid)
        return next((i["quantity"] for i in inv if i["id"] == it["id"]), 0)

    # ── 1. Предметы ──
    shower = await get_item_by_name("Душевая")
    bath = await get_item_by_name("Ванная с душем")
    check("предмет «Душевая» есть", shower is not None)
    check("предмет «Ванная с душем» есть", bath is not None)
    check("«Душевая» — мебель", shower is not None and shower["category"] == "furniture")
    check("«Ванная с душем» — мебель", bath is not None and bath["category"] == "furniture")

    # ── 2. Карты и константы ──
    check("FURNITURE_BY_EXPANSION[shower,1]",
          hh.FURNITURE_BY_EXPANSION.get(("shower", 1)) == "Душевая")
    check("FURNITURE_BY_EXPANSION[shower,2]",
          hh.FURNITURE_BY_EXPANSION.get(("shower", 2)) == "Ванная с душем")
    check("FURNITURE_BY_ITEM[Душевая]",
          hh.FURNITURE_BY_ITEM.get("Душевая") == ("shower", 1))
    check("EXPANSION_LABELS[shower] есть", "shower" in hh.EXPANSION_LABELS)
    check("_slot_icon(shower) = 🚿", hh._slot_icon("shower") == "🚿")
    check("_slot_name душевая ур.1",
          hh._slot_name({"expansion_type": "shower", "expansion_level": 1}) == "Душевая")
    check("_slot_name душевая ур.2",
          hh._slot_name({"expansion_type": "shower", "expansion_level": 2}) == "Ванная с душем")
    check("SHOWER_AP_BY_LEVEL", hh.SHOWER_AP_BY_LEVEL == {1: 25, 2: 50})
    check("SHOWER_SOBER_MINUTES", hh.SHOWER_SOBER_MINUTES == {1: 60, 2: 180})

    if not shower or not bath:
        await close_db()
        print(f"\nSmoke 147: {passed} passed, {failed} failed")
        sys.exit(1)

    # ── 3. Экран комнаты ──
    uid = 471001
    await add_user(uid, "bather", "Купальщик", "")
    await update_user(uid, ap=10)
    await set_player_housing(uid, "apartment")
    await set_housing_slot(uid, 0, "shower", 1)

    bot_room = FakeSender()
    cb_room = FakeCallback(uid, data="housing:room:0", bot=bot_room)
    await hh.housing_room(cb_room)
    room_txt, room_kb = last_bot_send(bot_room)
    room_cbs = markup_callbacks(room_kb)
    check("экран душевой: кнопка «Принять душ»",
          "housing:shower:0" in room_cbs)
    check("экран душевой: упоминается +25 ОД", "+25 ОД" in room_txt)
    check("экран душевой: подсказка про опьянение", "60 мин" in room_txt)

    # ── 4. Применение и суточный лимит ──
    ap0 = (await get_user(uid))["ap"]
    bot_use = FakeSender()
    cb_use = FakeCallback(uid, data="housing:shower:0", bot=bot_use)
    await hh.housing_shower(cb_use)
    ap1 = (await get_user(uid))["ap"]
    check("применение: +25 ОД", ap1 == ap0 + 25)
    check("применение: алерт про освежение", any(
        t and "Освежился" in t for t in cb_use.alerts))
    check("применение: can_use_shower = False", not await can_use_shower(uid))
    use_txt, use_kb = last_bot_send(bot_use)
    check("после применения: нет кнопки душа",
          "housing:shower:0" not in markup_callbacks(use_kb))
    check("после применения: «уже мылся»", "уже мылся" in use_txt)

    # повторно в тот же день
    cb_again = FakeCallback(uid, data="housing:shower:0", bot=FakeSender())
    await hh.housing_shower(cb_again)
    check("повторно: отказ", any(t and "уже мылся" in t for t in cb_again.alerts))
    check("повторно: ОД не изменились", (await get_user(uid))["ap"] == ap1)

    # ── 5. Смена суток открывает лимит ──
    await update_user(uid, shower_used_day="2000-01-01")
    check("прошлые сутки → can_use_shower = True", await can_use_shower(uid))

    # ── 6. daily_ap_recovery обнуляет счётчик при смене суток ──
    uid2 = 471002
    await add_user(uid2, "bather2", "Купальщик2", "")
    await update_user(uid2, ap=5, shower_used_day="2000-01-01", shower_used_today=1,
                      ap_recovery_day="2000-01-01")
    await daily_ap_recovery()
    u2 = await get_user(uid2)
    check("ночной цикл: shower_used_today обнулён", (u2.get("shower_used_today") or 0) == 0)
    check("ночной цикл: shower_used_day = сегодня",
          u2.get("shower_used_day") == today_report_day())

    # ── 7. Апгрейд: ванна заменяет душевую ──
    uid3 = 471003
    await add_user(uid3, "upgrader", "Апгрейдер", "")
    await update_user(uid3, ap=10)
    await set_player_housing(uid3, "apartment")
    await set_housing_slot(uid3, 0, "shower", 1)
    # важно: НЕ вызываем increment_housing_expansions → перепланировка бесплатна
    await add_inventory_item(uid3, bath["id"], 1)

    bot_up = FakeSender()
    cb_up = FakeCallback(uid3, data=f"housing:install_item:0:{bath['id']}", bot=bot_up)
    await hh.housing_install_item(cb_up)
    slots3 = await get_housing_slots(uid3)
    s3 = slots3.get(0, {})
    check("апгрейд: тип остался shower", s3.get("expansion_type") == "shower")
    check("апгрейд: уровень стал 2", int(s3.get("expansion_level") or 0) == 2)
    check("апгрейд: «Душевая» вернулась в инвентарь",
          await inv_qty(uid3, "Душевая") >= 1)
    check("апгрейд: «Ванная с душем» ушла из инвентаря",
          await inv_qty(uid3, "Ванная с душем") == 0)

    ap3 = (await get_user(uid3))["ap"]
    cb_bath = FakeCallback(uid3, data="housing:shower:0", bot=FakeSender())
    await hh.housing_shower(cb_bath)
    check("ванна: +50 ОД", (await get_user(uid3))["ap"] == ap3 + 50)

    # ── 8. Душ и ванна сокращают опьянение ──
    from utils.states import apply_state_to, get_state_info

    async def drunk_left(user_id, key):
        info = await get_state_info(user_id)
        return next((s["minutes_left"] for s in info["states"] if s["key"] == key), None)

    uid4 = 471004
    await add_user(uid4, "drunk1", "Пьяный1", "")
    await update_user(uid4, ap=10)
    await set_player_housing(uid4, "apartment")
    await set_housing_slot(uid4, 0, "shower", 1)
    await apply_state_to(uid4, "пьян", minutes=120)
    cb4 = FakeCallback(uid4, data="housing:shower:0", bot=FakeSender())
    await hh.housing_shower(cb4)
    left4 = await drunk_left(uid4, "пьян")
    check("душевая: «пьян» 120 → ~60 мин",
          left4 is not None and 58 <= left4 <= 60)
    check("душевая: алерт про −60 мин",
          any(t and "−60 мин" in t for t in cb4.alerts))

    uid5 = 471005
    await add_user(uid5, "drunk2", "Пьяный2", "")
    await update_user(uid5, ap=10)
    await set_player_housing(uid5, "apartment")
    await set_housing_slot(uid5, 0, "shower", 2)
    await apply_state_to(uid5, "очень пьян", minutes=360)
    cb5 = FakeCallback(uid5, data="housing:shower:0", bot=FakeSender())
    await hh.housing_shower(cb5)
    left5 = await drunk_left(uid5, "очень пьян")
    check("ванна: «очень пьян» 360 → ~180 мин",
          left5 is not None and 178 <= left5 <= 180)
    check("ванна: алерт про −180 мин",
          any(t and "−180 мин" in t for t in cb5.alerts))

    uid6 = 471006
    await add_user(uid6, "drunk3", "Пьяный3", "")
    await update_user(uid6, ap=10)
    await set_player_housing(uid6, "apartment")
    await set_housing_slot(uid6, 0, "shower", 1)
    await apply_state_to(uid6, "пьян", minutes=30)
    cb6 = FakeCallback(uid6, data="housing:shower:0", bot=FakeSender())
    await hh.housing_shower(cb6)
    check("душевая: короткое опьянение снято полностью",
          await drunk_left(uid6, "пьян") is None)
    check("душевая: алерт «совсем трезв»",
          any(t and "совсем трезв" in t for t in cb6.alerts))

    await close_db()
    print(f"\nSmoke 147: {passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    try:
        asyncio.run(run())
    except SystemExit:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        from database.db import close_db
        asyncio.run(close_db())
        print(f"SMOKE ERROR: {e!r}")
        sys.exit(1)
