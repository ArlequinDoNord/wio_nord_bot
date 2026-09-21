"""Smoke v0.14.0: дымовая шашка в подземелье.

Проверяет:
1. Товар «Дымовая шашка» создаётся (consumable), идемпотентно.
2. item_fits_slot: шашка только в слот «smoke»; в слоты зелий не встаёт;
   обычные расходники в слот шашки не встают.
3. get_equipment_slot_items: с include_smoke=True возвращает слот шашки,
   без include — не возвращает.
4. escape_chance: с шашкой 95% (успех на броске 1–19, провал на 20),
   без шашки — база 25% при полном HP, 45% на грани смерти.
5. Боевые клавиатуры: у обычного врага есть кнопка «💨 Дымовая шашка»,
   у босса нет ни шашки, ни кнопки побега.
6. Применение шашки в бою: списывает предмет, увеличивает счётчик
   dungeon_smoke_uses и убегает от врага (успешный побег).
7. Лимит: больше DUNGEON_SMOKE_MAX (2) применений за забег нельзя —
   шашка не списывается.
8. От босса шашку применить нельзя: предмет не списывается.

Запуск: .venv\\Scripts\\python.exe smoke_066.py
"""
import asyncio
import os
import sys
from types import SimpleNamespace

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke066.db")
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


def markup_callbacks(markup):
    if not markup:
        return []
    return [b.callback_data for row in markup.inline_keyboard for b in row]


async def run():
    from database.db import (
        init_db, close_db, seed_default_items, seed_dungeon,
        ensure_dungeon_shop_items,
        add_user, get_item_by_name, get_inventory_item, add_inventory_item,
        set_equipment_slot, get_equipment, item_fits_slot,
        start_dungeon_run, get_active_run, update_run_hp,
        get_all_dungeons, get_dungeon_enemies,
    )
    from config import DUNGEON_SMOKE_MAX
    from bot.handlers import dungeon as DH
    from utils.combat import escape_chance, ESCAPE_BASE_CHANCE

    await init_db()
    await seed_default_items()
    await seed_dungeon()
    await ensure_dungeon_shop_items()

    uid = 999801
    await add_user(uid, "smoker", "Тест", "")

    passed = 0
    failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
        else:
            failed += 1
            print(f"  FAIL: {name}")

    # ── 1. Товар существует ──
    smoke = await get_item_by_name("Дымовая шашка")
    check("«Дымовая шашка» существует (consumable)",
          smoke is not None and smoke['category'] == 'consumable')
    potion = await get_item_by_name("Малая настойка здоровья")
    check("«Малая настойка здоровья» существует (контроль)",
          potion is not None and potion['category'] == 'consumable')

    # ── 2. item_fits_slot ──
    if smoke and potion:
        check("шашка подходит только в слот smoke",
              item_fits_slot(smoke, 'smoke') and not item_fits_slot(smoke, 'potion1')
              and not item_fits_slot(smoke, 'potion2') and not item_fits_slot(smoke, 'weapon'))
        check("обычный расходник в слот шашки не встаёт",
              not item_fits_slot(potion, 'smoke'))
        check("зелье по-прежнему ставится в слоты зелий",
              item_fits_slot(potion, 'potion1') and item_fits_slot(potion, 'potion2'))

    # ── 3. get_equipment_slot_items ──
    if smoke:
        await add_inventory_item(uid, smoke['id'], 3)
        await set_equipment_slot(uid, 'smoke', smoke['id'])
        full = await DH.get_equipment_slot_items(uid, include_smoke=True)
        plain = await DH.get_equipment_slot_items(uid)
        check("include_smoke=True показывает слот шашки",
              ('smoke',) in [s for s, _ in full] or any(s == 'smoke' for s, _ in full))
        check("без include_smoke шашки нет",
              not any(s == 'smoke' for s, _ in plain))

    # ── 4. escape_chance ──
    check("с шашкой бросок 1 -> успех", escape_chance(1.0, dice_roll=1, smoke_used=True))
    check("с шашкой бросок 19 -> успех", escape_chance(1.0, dice_roll=19, smoke_used=True))
    check("с шашкой бросок 20 -> провал", not escape_chance(1.0, dice_roll=20, smoke_used=True))
    check(f"без шашки полный HP: шанс {ESCAPE_BASE_CHANCE}% (бросок 5 -> успех)",
          escape_chance(1.0, dice_roll=5))
    check("без шашки полный HP: шанс 25% (бросок 6 -> провал)",
          not escape_chance(1.0, dice_roll=6))
    check("без шашки на грани смерти: шанс 45% (бросок 9 -> успех)",
          escape_chance(0.0, dice_roll=9))
    check("без шашки на грани смерти: шанс 45% (бросок 10 -> провал)",
          not escape_chance(0.0, dice_roll=10))

    # ── 5. Клавиатуры ──
    dng = (await get_all_dungeons(training=False))[0]
    enemies = await get_dungeon_enemies(dng['id'])
    foes = [e for e in enemies if not e['is_boss']]
    bosses = [e for e in enemies if e['is_boss']]
    check("есть обычный враг и босс", bool(foes) and bool(bosses))
    foe, boss = foes[0], bosses[0]

    slot_items = await DH.get_equipment_slot_items(uid, include_smoke=True)
    plain_slots = await DH.get_equipment_slot_items(uid)
    combat_kb = DH.dungeon_combat_keyboard(foe['id'], slot_items, step=7)
    combat_cbs = markup_callbacks(combat_kb)
    check("клавиатура обычного боя: кнопка «💨 Дымовая шашка»",
          "dungeon:use_slot:smoke:7" in combat_cbs)
    smoke_btn = [b for row in combat_kb.inline_keyboard for b in row
                 if b.callback_data == "dungeon:use_slot:smoke:7"]
    check("кнопка подписана «💨 Дымовая шашка» и содержит количество",
          smoke_btn and smoke_btn[0].text.startswith("💨 Дымовая шашка")
          and any(ch.isdigit() for ch in smoke_btn[0].text))

    boss_kb = DH.dungeon_boss_keyboard(boss['id'], plain_slots, step=7)
    boss_cbs = markup_callbacks(boss_kb)
    check("клавиатура босса: нет шашки", "dungeon:use_slot:smoke:7" not in boss_cbs)
    check("клавиатура босса: нет побега",
          not any(cb.startswith("dungeon:escape") for cb in boss_cbs))

    # ── 6. Применение шашки в бою (успешный побег) ──
    await start_dungeon_run(uid, dng['id'])
    inv_before = (await get_inventory_item(uid, smoke['id']))['quantity']
    st = FakeState(data={
        "current_enemy_id": foe['id'],
        "dungeon_step": 1,
        "dungeon_smoke_uses": 0,
    })

    orig_escape = DH.escape_chance
    DH.escape_chance = lambda hp, dice_roll=None, smoke_used=False: smoke_used
    try:
        cb = FakeCallback(uid, data="dungeon:use_slot:smoke:1")
        await DH.dungeon_use_slot(cb, st)
    finally:
        DH.escape_chance = orig_escape

    inv_after = (await get_inventory_item(uid, smoke['id']))['quantity']
    check("применение списывает 1 шашку", inv_after == inv_before - 1)
    check("счётчик dungeon_smoke_uses увеличен",
          st._data.get('dungeon_smoke_uses', 0) == 1)
    text = sent_text(cb.message)
    check("текст побега упоминает шашку и врага",
          "дымовую шашку" in text.lower() and foe['name'] in text and "успешно убежал" in text)
    succeed_markup = None
    for kind, a, kw in cb.message.sent:
        if kind == "answer" and kw.get('reply_markup'):
            succeed_markup = kw['reply_markup']
    check("после побега предложено продолжить путь",
          any(x.startswith("dungeon:continue")
              for x in markup_callbacks(succeed_markup)))

    # ── 7. Лимит 2 за забег ──
    await add_inventory_item(uid, smoke['id'], 2)
    await set_equipment_slot(uid, 'smoke', smoke['id'])
    st2 = FakeState(data={
        "current_enemy_id": foe['id'],
        "dungeon_step": 1,
        "dungeon_smoke_uses": DUNGEON_SMOKE_MAX,
    })
    inv_before2 = (await get_inventory_item(uid, smoke['id']))['quantity']
    cb2 = FakeCallback(uid, data="dungeon:use_slot:smoke:1")
    await DH.dungeon_use_slot(cb2, st2)
    inv_after2 = (await get_inventory_item(uid, smoke['id']))['quantity']
    check("лимит: при исчерпании шашка не списывается",
          inv_after2 == inv_before2)
    check("лимит: выводится объяснение",
          "не больше" in sent_text(cb2.message) or "Лимит" in sent_text(cb2.message))
    check("лимит: счётчик не вырос",
          st2._data.get('dungeon_smoke_uses', 0) == DUNGEON_SMOKE_MAX)

    # ── 8. От босса не убежать ──
    await start_dungeon_run(uid, dng['id'])
    inv_before3 = (await get_inventory_item(uid, smoke['id']))['quantity']
    st3 = FakeState(data={
        "current_enemy_id": boss['id'],
        "dungeon_step": 1,
        "dungeon_smoke_uses": 0,
    })
    cb3 = FakeCallback(uid, data="dungeon:use_slot:smoke:1")
    await DH.dungeon_use_slot(cb3, st3)
    inv_after3 = (await get_inventory_item(uid, smoke['id']))['quantity']
    check("от босса: шашка не списывается", inv_after3 == inv_before3)
    check("от босса: сообщение «От босса не убежать»",
          "От босса не убежать" in sent_text(cb3.message))

    # ── 9. Счётчик на кнопках зелий: обновляется после применения ──
    if potion:
        await add_inventory_item(uid, potion['id'], 2)
        await set_equipment_slot(uid, 'potion1', potion['id'])
        await start_dungeon_run(uid, dng['id'])
        run9 = await get_active_run(uid)
        await update_run_hp(run9['id'], 5)
        run9_low = await get_active_run(uid)
        st9 = FakeState(data={
            "current_enemy_id": foe['id'],
            "dungeon_step": 1,
            "dungeon_heal_uses": 0,
        })
        cb9 = FakeCallback(uid, data="dungeon:use_slot:potion1:1")
        await DH.dungeon_use_slot(cb9, st9)
        run9_after = await get_active_run(uid)
        final_markup = None
        for kind, a, kw in cb9.message.sent:
            if kind == "answer" and kw.get('reply_markup'):
                final_markup = kw['reply_markup']
        labels9 = [b.text for row in (final_markup.inline_keyboard if final_markup else [])
                   for b in row if b.callback_data.startswith("dungeon:use_slot:potion1")]
        check("истощение: зелье применилось (HP вырос)",
              run9_low['hp'] < run9_after['hp'])
        check("кнопка зелья показывает остаток x1 после применения",
              any("x1" in lbl and "Малая настойка" in lbl for lbl in labels9))

    await close_db()
    print(f"\nSmoke 066: {passed} passed, {failed} failed")
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