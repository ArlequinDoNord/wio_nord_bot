"""Smoke v0.13.14: «Контракты от Штаба ВС» — выбор подземелья из списка.

Проверяет:
1. contracts_list отдаёт список боевых подземелий (каждое = контракт).
2. contract_pick показывает карточку: этажи, сложность, награда, стоимость входа.
3. contract_enter без контрактов — вежливый отказ «Купи его в магазине».
4. contract_enter с контрактом и AP — окно подтверждения списков.
5. contract_enter_confirm списывает контракт + 30 ОД и начинает забег в выбранный данж.
6. legacy city:dungeon переадресует на contracts_list (старые кнопки живы).

Запуск: .venv\\Scripts\\python.exe smoke_063.py
"""
import asyncio
import os
import sys
from types import SimpleNamespace

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke063.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB

sys.path.insert(0, os.path.dirname(__file__))


class FakeMessage:
    def __init__(self):
        self.sent = []
        self.photo = None
        self.from_user = None

    async def answer(self, *a, **kw):
        self.sent.append(("answer", a, kw))

    async def answer_photo(self, *a, **kw):
        self.sent.append(("answer_photo", a, kw))

    async def edit_text(self, *a, **kw):
        self.sent.append(("edit_text", a, kw))

    async def edit_caption(self, *a, **kw):
        self.sent.append(("edit_caption", a, kw))

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
    return ""


async def run():
    from database.db import (
        init_db, close_db, seed_default_items, seed_dungeon, seed_kvp,
        ensure_dungeon_shop_items, ensure_dungeon_enemy_drops, ensure_life_items,
        ensure_dungeon_reservoir_items, ensure_water_fish, ensure_kvp_award,
        ensure_market_license_item,
        add_user, get_item_by_name, get_all_dungeons, get_dungeon_enemies,
        add_inventory_item, get_inventory_item, get_active_run, update_user,
    )
    from bot.handlers import dungeon as dh

    await init_db()
    await seed_default_items()
    await seed_dungeon()
    await seed_kvp()
    await ensure_dungeon_shop_items()
    await ensure_dungeon_enemy_drops()
    await ensure_life_items()
    await ensure_dungeon_reservoir_items()
    await ensure_water_fish()
    await ensure_kvp_award()
    await ensure_market_license_item()

    uid = 999601
    uid2 = 999602
    await add_user(uid, "tester", "Тест", "")
    await add_user(uid2, "tester2", "Тест2", "")

    dungeons = await get_all_dungeons(training=False)
    if not dungeons:
        print("SMOKE ERROR: нет боевых подземелий")
        await close_db()
        sys.exit(1)
    dng = dungeons[0]

    passed = 0
    failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
        else:
            failed += 1
            print(f"  FAIL: {name}")

    # ── 1. contracts_list: список контрактов ──
    st = FakeState()
    cb = FakeCallback(uid, data="contracts:list")
    await dh.contracts_list(cb, st)
    txt = sent_text(cb.message)
    check("contracts_list: название данжа в списке", dng['name'] in txt)
    check("contracts_list: упомянута цена входа ОД", "30" in txt)
    callbacks = [m[2] for m in cb.message.sent
                 if len(m) > 2 and m[2].get('reply_markup') is not None]
    buttons = []
    if callbacks:
        for row in callbacks[0]['reply_markup'].inline_keyboard:
            buttons.extend(btn.callback_data for btn in row)
    check("contracts_list: есть кнопка «выбрать данж»",
          any(b == f"contract:pick:{dng['id']}" for b in buttons))

    # ── 2. contract_pick: карточка контракта ──
    st2 = FakeState()
    cb2 = FakeCallback(uid, data=f"contract:pick:{dng['id']}")
    await dh.contract_pick(cb2, st2)
    txt2 = sent_text(cb2.message)
    caps = [m[2].get('caption') for m in cb2.message.sent
            if len(m) > 2 and m[2].get('caption') is not None]
    card_text = (txt2 or (caps[0] if caps else ""))
    check("contract_pick: название контракта", dng['name'] in card_text)
    check("contract_pick: этажи в карточке", "Этажей" in card_text)
    check("contract_pick: сложность звёздами", "★" in card_text)
    check("contract_pick: награда НМ", "Награда" in card_text)
    enemies = await get_dungeon_enemies(dng['id'])
    reward = sum(e['reward_nm'] or 0 for e in enemies)
    check("contract_pick: награда = сумме reward врагов", str(reward) in card_text)

    # ── 3. contract_enter без контрактов → отказ ──
    st3 = FakeState()
    cb3 = FakeCallback(uid, data=f"contract:enter:{dng['id']}")
    await dh.contract_enter(cb3, st3)
    txt3 = sent_text(cb3.message)
    check("contract_enter без контракта: отказ", "Купи его в магазине" in txt3)

    # ── 4. contract_enter с контрактом и AP → подтверждение ──
    contract_item = await get_item_by_name("Контракт на зачистку")
    check("контракт-слот есть", contract_item is not None)
    await add_inventory_item(uid2, contract_item['id'], 2)
    await update_user(uid2, ap=80)
    st4 = FakeState()
    cb4 = FakeCallback(uid2, data=f"contract:enter:{dng['id']}")
    await dh.contract_enter(cb4, st4)
    txt4 = sent_text(cb4.message)
    check("contract_enter: подтверждение", "БУДУТ СПИСАНЫ" in txt4)
    check("contract_enter: упомянут контракт", "Контракт на зачистку" in txt4)
    check("contract_enter: state confirm_enter",
          st4._state == dh.DungeonFSM.confirm_enter)

    # ── 5. contract_enter_confirm: списание + вход ──
    st5 = FakeState()
    cb5 = FakeCallback(uid2, data=f"contract:enter:confirm:{dng['id']}")
    await dh.contract_enter_confirm(cb5, st5)
    txt5 = sent_text(cb5.message)
    check("enter_confirm: контракт списан",
          await get_inventory_item(uid2, contract_item['id']) is None
          or (await get_inventory_item(uid2, contract_item['id']))['quantity'] == 1)
    run = await get_active_run(uid2)
    check("enter_confirm: забег создан", run is not None)
    check("enter_confirm: забег в выбранный данж",
          run and run['dungeon_id'] == dng['id'])
    check("enter_confirm: ОД списаны", (await get_user_ap(uid2)) == 50)
    check("enter_confirm: сообщение о входе", "Контракт использован" in txt5)
    check("enter_confirm: FSM in_dungeon", st5._state == dh.DungeonFSM.in_dungeon)

    # ── 6. legacy city:dungeon → contracts_list ──
    from database.db import end_run
    if run:
        await end_run(run['id'], 0)
    st6 = FakeState()
    cb6 = FakeCallback(uid, data="city:dungeon")
    await dh.dungeon_entry_legacy(cb6, st6)
    txt6 = sent_text(cb6.message)
    check("legacy city:dungeon: список контрактов", dng['name'] in txt6)

    await close_db()
    print(f"\nSmoke 063: {passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)


async def get_user_ap(user_id):
    from database.db import get_user
    u = await get_user(user_id)
    return u['ap'] if u else None


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