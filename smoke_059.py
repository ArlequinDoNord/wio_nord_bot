"""Smoke v0.13.10: два фикса.

1) dungeon_use_slot: callback «dungeon:use_slot:potion1:<step>» снова парсит
   слот как строку (а не int(enemy_id)) — расходник в бою применяется.
2) гонка заброса удочки: FISHING_CASTING занимается сразу до первого await,
   двойной тап не проходит проверку дважды.

Запуск: .venv\\Scripts\\python.exe smoke_059.py
"""
import asyncio
import os
import sys
from types import SimpleNamespace

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke059.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB

sys.path.insert(0, os.path.dirname(__file__))


class FakeBot:
    def __init__(self):
        self.calls = []
        self._next = 1000

    async def edit_message_media(self, *a, **kw):
        self.calls.append(("media", a))
        return SimpleNamespace(message_id=a[1] if len(a) > 1 else 0)

    async def edit_message_caption(self, *a, **kw):
        self.calls.append(("caption", a))
        return SimpleNamespace(message_id=a[1] if len(a) > 1 else 0)

    async def edit_message_text(self, *a, **kw):
        self.calls.append(("text", a))
        return SimpleNamespace(message_id=a[1] if len(a) > 1 else 0)

    async def delete_message(self, *a, **kw):
        self.calls.append(("delete", a))

    async def send_photo(self, *a, **kw):
        self._next += 1
        return SimpleNamespace(message_id=self._next)

    async def send_message(self, *a, **kw):
        self._next += 1
        return SimpleNamespace(message_id=self._next)


class FakeMessage:
    def __init__(self):
        self.sent = []
        self.chat = SimpleNamespace(id=1)
        self.message_id = 1
        self.photo = None
        self.bot = FakeBot()

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
    def __init__(self, user_id, data=""):
        self.from_user = SimpleNamespace(id=user_id)
        self.message = FakeMessage()
        self.data = data
        self.alerts = []

    async def answer(self, text=None, *a, **kw):
        self.alerts.append(text)


class FakeState:
    def __init__(self, state=None, data=None):
        self._state = state
        self._data = dict(data or {})

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


async def run():
    from database.db import (
        init_db, close_db, seed_default_items, seed_dungeon,
        ensure_dungeon_shop_items, ensure_dungeon_enemy_drops, ensure_life_items,
        ensure_dungeon_reservoir_items, ensure_water_fish, ensure_kvp_award,
        ensure_market_license_item, migrate_legacy_junk,
        add_user, get_item_by_name, add_inventory_item, set_equipment_slot,
        get_inventory_item, start_dungeon_run, get_active_run, update_run_hp,
        get_all_dungeons,
    )
    from bot.handlers import dungeon as dng
    from bot.handlers import fishing as fish
    from bot.handlers.fishing import FISHING_CASTING

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
    await migrate_legacy_junk()

    passed = 0
    failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
        else:
            failed += 1
            print(f"  FAIL: {name}")

    # ── 1. dungeon:use_slot с зельем не падает и лечит ──
    uid = 999410
    await add_user(uid, "tester", "Тест", "")
    potion = await get_item_by_name("Малая настойка здоровья")
    check("настойка существует", potion is not None)
    check("настойка: heal=20", potion is not None and (potion['heal'] or 0) == 20)
    await add_inventory_item(uid, potion['id'], 1)
    await set_equipment_slot(uid, "potion1", potion['id'])

    dungeon = (await get_all_dungeons(training=False))[0]
    await start_dungeon_run(uid, dungeon['id'])
    run = await get_active_run(uid)
    await update_run_hp(run['id'], 1)

    state = FakeState(state=dng.DungeonFSM.in_dungeon.state,
                      data={'dungeon_step': 0, 'current_enemy_id': None})
    cb = FakeCallback(uid, data="dungeon:use_slot:potion1:0")
    crashed = None
    try:
        await dng.dungeon_use_slot(cb, state)
    except Exception as e:
        crashed = e
    check("use_slot: без исключения (был ValueError)", crashed is None)
    if crashed is None:
        run2 = await get_active_run(uid)
        check("use_slot: HP вырос с 1", (run2['hp'] or 0) > 1)
        inv = await get_inventory_item(uid, potion['id'])
        check("use_slot: настойка списана",
              not inv or (inv['quantity'] or 0) == 0)
        check("use_slot: сообщение боя отправлено",
              any(m[0] == "answer" for m in cb.message.sent))
        applied = [m for m in cb.message.sent if m[0] == "answer" and m[1]]
        check("use_slot: текст содержит «применено»",
              any("применено" in str(m[1][0]) for m in cb.message.sent
                  if m[0] == "answer" and m[1]))

    # ── 2. гонка заброса: лок занимается до первого await ──
    uid2 = 999411
    token = "123456"
    fish.FISH_TOKEN[uid2] = token

    orig_get_active_run = fish.get_active_run

    async def slow_get_active_run(_uid):
        await asyncio.sleep(0)
        return None

    fish.get_active_run = slow_get_active_run
    try:
        cb1 = FakeCallback(uid2, data=f"fish:cast:{token}")
        cb2 = FakeCallback(uid2, data=f"fish:cast:{token}")
        await asyncio.gather(fish.fish_cast(cb1), fish.fish_cast(cb2))
    finally:
        fish.get_active_run = orig_get_active_run
        fish.FISH_TOKEN.pop(uid2, None)

    second_rejected = any(
        a and "уже закинул" in a for a in (cb1.alerts + cb2.alerts)
    )
    check("гонка: второй заброс отсечён локом", second_rejected)
    check("гонка: лок снят после завершения", uid2 not in FISHING_CASTING)

    # ── 3. выбор наживки по коду ('worms' / 'spider' / 'combined' / 'none') ──
    await add_user(uid2, "angler", "Рыбак", "")
    worms_it = await get_item_by_name(fish.WORMS_NAME)
    spider_it = await get_item_by_name(fish.SPIDER_LEG_NAME)
    comb_it = await get_item_by_name(fish.COMBINED_BAIT_NAME)
    await add_inventory_item(uid2, worms_it["id"], 2)
    await add_inventory_item(uid2, spider_it["id"], 1)
    await add_inventory_item(uid2, comb_it["id"], 1)

    b_sp, _ = await fish._resolve_bait(uid2, "spider")
    check("_resolve_bait('spider') выбирает Лапку паука при наличии Червей",
          b_sp == fish.SPIDER_LEG_NAME)
    b_cb, _ = await fish._resolve_bait(uid2, "combined")
    check("_resolve_bait('combined') выбирает Комбинированную наживку при наличии Червей",
          b_cb == fish.COMBINED_BAIT_NAME)
    b_wm, _ = await fish._resolve_bait(uid2, "worms")
    check("_resolve_bait('worms') выбирает Черви",
          b_wm == fish.WORMS_NAME)
    b_no, _ = await fish._resolve_bait(uid2, "none")
    check("_resolve_bait('none') возвращает None", b_no is None)

    # ── 4. «Проверить улов» на экране ожидания: окно без кнопок не остаётся ──
    wait_cbs = [b.callback_data for row in fish._wait_markup().inline_keyboard
                for b in row]
    check("экран ожидания озера: кнопка fish:recover", wait_cbs == ["fish:recover"])
    obs = fish.router.observers['callback_query']
    handler_names = {getattr(h.callback, '__name__', None) for h in obs.handlers}
    check("router: fish_recover_cb зарегистрирован", "fish_recover_cb" in handler_names)

    # пока заброс реально идёт — только предупреждение
    FISHING_CASTING.add(uid2)
    cb_rec = FakeCallback(uid2, data="fish:recover")
    await fish.fish_recover_cb(cb_rec)
    check("fish:recover: алерт во время заброса",
          any(a is not None for a in cb_rec.alerts))
    FISHING_CASTING.discard(uid2)

    # результат потерян (рестарт/OOM) — окно озера перерисовывается
    fish.FISH_MSG[uid2] = (1, 1)
    fish.FISH_TOKEN.pop(uid2, None)
    cb_rec2 = FakeCallback(uid2, data="fish:recover")
    await fish.fish_recover_cb(cb_rec2)
    check("fish:recover: окно озера перерисовано",
          bool(cb_rec2.message.bot.calls))
    check("fish:recover: выдан новый токен окна",
          bool(fish.FISH_TOKEN.get(uid2)))
    fish.FISH_MSG.pop(uid2, None)

    await close_db()
    print(f"\nSmoke 059: {passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    try:
        asyncio.run(run())
    except SystemExit:
        raise
    except Exception as e:
        from database.db import close_db
        asyncio.run(close_db())
        print(f"SMOKE ERROR: {e!r}")
        sys.exit(1)
