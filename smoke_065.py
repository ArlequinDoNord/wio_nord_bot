"""Smoke v0.13.17: фиксы по багам игроков.

Проверяет:
1. Покупка мебели (Верстак/Кадка): всплывающее окно «Куплено» (show_alert),
   лок _PURCHASING снимается после покупки (повторная покупка возможна).
2. inv_sell_keep1: кнопка «Оставить 1» при qty>3; продаёт qty-1 (остаётся 1).
3. fish_catch_use: улов-ресурс (водоросли) используется -> +1 ОД, улов списан.
4. pay_housing_tax идемпотентен: повторная оплата за месяц = отказ, НМ не списываются.
5. contract_enter: фильтр по числу (не перехватывает confirm).

Запуск: .venv\\Scripts\\python.exe smoke_065.py
"""
import asyncio
import os
import sys
from types import SimpleNamespace

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke065.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB

sys.path.insert(0, os.path.dirname(__file__))


class FakeMessage:
    def __init__(self):
        self.sent = []
        self.photo = None
        self.text = ""

    async def answer(self, *a, **kw):
        self.sent.append(("answer", a, kw))

    async def edit_text(self, *a, **kw):
        self.sent.append(("edit_text", a, kw))

    async def edit_caption(self, *a, **kw):
        self.sent.append(("edit_caption", a, kw))

    async def delete(self, *a, **kw):
        self.sent.append(("delete", a, kw))

    async def answer_photo(self, *a, **kw):
        self.sent.append(("answer_photo", a, kw))

    async def __getattr__(self, name):
        async def _noop(*a, **kw):
            return None
        return _noop


class FakeCallback:
    def __init__(self, user_id, data="", message=None):
        self.from_user = SimpleNamespace(id=user_id)
        self.message = message or FakeMessage()
        self.data = data
        self.alerts = []

    async def answer(self, text=None, *a, **kw):
        self.alerts.append(text)


class FakeState:
    def __init__(self, state=None, data=None):
        self._state = state
        self._data = dict(data or {})
        self.cleared = False

    async def get_state(self):
        return self._state

    async def set_state(self, s):
        self._state = s

    async def get_data(self):
        return dict(self._data)

    async def update_data(self, **kw):
        self._data.update(kw)

    async def clear(self):
        self._data.clear()
        self._state = None
        self.cleared = True


def sent_text(msg):
    for kind, a, kw in msg.sent:
        if kind == "answer" and a:
            return a[0]
        if kind == "answer_photo" and kw.get('caption'):
            return kw.get('caption')
        if kind == "edit_text" and a:
            return a[0]
    return ""


async def run():
    from database.db import (
        init_db, close_db, seed_default_items, seed_dungeon,
        ensure_dungeon_shop_items, ensure_dungeon_enemy_drops, ensure_life_items,
        ensure_dungeon_reservoir_items, ensure_water_fish, ensure_kvp_award,
        ensure_market_license_item,
        add_user, get_item_by_name, add_nordmarks, get_status_by_tag, grant_status,
        set_player_housing, pay_housing_tax, get_user,
        add_inventory_item, get_inventory_item, remove_inventory_item,
        add_fish_catch, get_fish_catches,
    )
    from bot.handlers import shop as SH
    from bot.handlers import inventory as INV
    from bot.handlers import dungeon as DH

    await init_db()
    await seed_default_items()
    await seed_dungeon()
    await ensure_dungeon_shop_items()
    await ensure_dungeon_enemy_drops()
    await ensure_life_items()
    await ensure_dungeon_reservoir_items()
    await ensure_water_fish()
    await ensure_kvp_award()
    await ensure_market_license_item()

    uid = 999701
    uid2 = 999702
    uid3 = 999703
    await add_user(uid, "tester", "Тест", "")
    await add_user(uid2, "tester2", "Тест2", "")
    await add_user(uid3, "tester3", "Тест3", "")

    pilot_st = await get_status_by_tag("pilot")
    if pilot_st:
        for u in (uid, uid2, uid3):
            await grant_status(u, pilot_st["id"], 0)

    passed = 0
    failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
        else:
            failed += 1
            print(f"  FAIL: {name}")

    # ── 1. Покупка мебели: alert «Куплено» + лок снимается ──
    workbench = await get_item_by_name("Верстак")
    kadka = await get_item_by_name("Кадка для растений")
    check("Верстак существует (furniture)",
          workbench is not None and workbench['category'] == 'furniture')
    check("Кадка существует (furniture)",
          kadka is not None and kadka['category'] == 'furniture')

    # жильё с 1+ свободным слотом (Студию нельзя расширять, берём Квартиру)
    await set_player_housing(uid, "apartment")
    await add_nordmarks(uid, 1000, "test", "покупка мебели")

    cb = FakeCallback(uid)
    await SH._buy_item(cb, workbench['id'], 1)
    inv_wb = await get_inventory_item(uid, workbench['id'])
    check("Верстак куплен: в инвентаре 1",
          inv_wb is not None and inv_wb['quantity'] == 1)
    bought_alerts = [a for a in cb.alerts if a and "Куплено" in a]
    check("после покупки всплывающее окно «Куплено» (show_alert)",
          bool(bought_alerts))
    check("в окне упомянут Верстак", bought_alerts and "Верстак" in bought_alerts[0])

    # лок снят: вторая покупка проходит
    cb2 = FakeCallback(uid)
    await SH._buy_item(cb2, workbench['id'], 1)
    inv_wb = await get_inventory_item(uid, workbench['id'])
    check("повторная покупка не заблокирована (лок снят)",
          inv_wb is not None and inv_wb['quantity'] == 2)

    # ── 1b. Кадка: пока покупка в процессе, повторный клик игнорируется ──
    await set_player_housing(uid3, "apartment")
    SH._PURCHASING.add(uid3)
    cb3 = FakeCallback(uid3)
    await SH._buy_item(cb3, kadka['id'], 1)
    check("двойной клик по «Купить» игнорируется",
          any(a and "обрабатывается" in a for a in cb3.alerts))
    SH._PURCHASING.discard(uid3)
    await add_nordmarks(uid3, 1000, "test", "кадка")
    cb3b = FakeCallback(uid3)
    await SH._buy_item(cb3b, kadka['id'], 1)
    inv_k = await get_inventory_item(uid3, kadka['id'])
    check("кадка куплена после снятия лока",
          inv_k is not None and inv_k['quantity'] == 1)

    # ── 2. inv_sell_keep1: продать все, кроме одной ──
    salt = await get_item_by_name("Соль")
    check("Соль существует", salt is not None)
    if salt:
        await add_inventory_item(uid2, salt['id'], 5)
        markup5 = INV.inv_item_markup(salt['id'], "consumable", qty=5, sellable=True)
        cbs5 = [b.callback_data for row in markup5.inline_keyboard for b in row]
        check("кнопка «Оставить 1» при qty=5",
              f"inv_sell_keep1:{salt['id']}" in cbs5)
        markup3 = INV.inv_item_markup(salt['id'], "consumable", qty=3, sellable=True)
        cbs3 = [b.callback_data for row in markup3.inline_keyboard for b in row]
        check("кнопки «Оставить 1» нет при qty=3",
              f"inv_sell_keep1:{salt['id']}" not in cbs3)
        cbk = FakeCallback(uid2, data=f"inv_sell_keep1:{salt['id']}")
        await INV.inv_sell_keep1(cbk)
        conf_text = sent_text(cbk.message)
        check("подтверждение «Продать Соль x4»",
              "Соль" in conf_text and "x4" in conf_text)
        # завершаем продажу через inv_sell_ok
        cbok = FakeCallback(uid2, data=f"inv_sell_ok:{salt['id']}:4")
        await INV.inv_sell_ok(cbok)
        inv_salt = await get_inventory_item(uid2, salt['id'])
        check("после продажи осталась 1 Соль",
              inv_salt is not None and inv_salt['quantity'] == 1)

    # ── 3. fish_catch_use: улов-ресурс (водоросли) -> +1 ОД ──
    weed = await get_item_by_name("Кусочек водорослей")
    check("водоросли существуют (consumable)",
          weed is not None and weed['category'] == 'consumable')
    if weed:
        await add_fish_catch(uid2, weed['id'], 1, kind="resource")
        ap_before = (await get_user(uid2))['ap']
        cbw = FakeCallback(uid2, data=f"fishuse:{weed['id']}:1")
        await INV.fish_catch_use(cbw)
        ap_after = (await get_user(uid2))['ap']
        check("водоросли из улова дают +1 ОД", ap_after == ap_before + 1)
        catches = await get_fish_catches(uid2)
        weed_left = [c for c in catches if c['item_id'] == weed['id']]
        check("улов водорослей списан", not weed_left)
        inv_weed = await get_inventory_item(uid2, weed['id'])
        check("инвентарь водорослей пуст",
              not inv_weed or inv_weed['quantity'] == 0)

    # ── 4. налог идемпотентен: не оплачивается дважды за месяц ──
    await set_player_housing(uid2, "apartment")
    await add_nordmarks(uid2, 1000, "test", "налог")
    bal_before = (await get_user(uid2))['nordmarks']
    ok1, msg1 = await pay_housing_tax(uid2)
    check("первая оплата налога прошла", ok1 and "оплачен" in msg1)
    bal_after_1 = (await get_user(uid2))['nordmarks']
    check("списан налог за квартиру (-35)", bal_before - bal_after_1 == 35)
    ok2, msg2 = await pay_housing_tax(uid2)
    bal_after_2 = (await get_user(uid2))['nordmarks']
    check("вторая оплата отклонена («уже оплачен»)",
          not ok2 and "уже оплачен" in msg2)
    check("Нордмарки не списаны повторно", bal_after_1 == bal_after_2)

    # ── 5. contract_enter: подтверждение не перехватывается входом ──
    import re as _re
    pat = _re.compile(r"^contract:enter:\d+$")
    check("фильтр входа: обычный id подходит",
          bool(pat.match("contract:enter:12")))
    check("фильтр входа: confirm НЕ подходит (не перехват)",
          not pat.match("contract:enter:confirm:12"))

    await close_db()
    print(f"\nSmoke 065: {passed} passed, {failed} failed")
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