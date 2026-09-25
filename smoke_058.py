"""Smoke v0.13.4: подтверждение выхода из подземелья (dungeon:exit → confirm/cancel),
лок рыбалки в водохранилище (FISHING_CASTING): пока ждёшь улов — нельзя выйти,
продолжить путь или забросить повторно; общий лок с озером.

Запуск: .venv\\Scripts\\python.exe smoke_058.py
"""
import asyncio
import os
import sys
from types import SimpleNamespace

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke058.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB

sys.path.insert(0, os.path.dirname(__file__))


class FakeMessage:
    def __init__(self):
        self.sent = []

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
        add_user, get_user, get_item_by_name,
        start_dungeon_run, get_active_run, add_run_item, add_run_nordmarks,
        get_run_items, transfer_run_items_to_inventory,
        get_inventory_item, get_all_dungeons,
    )
    from bot.handlers import dungeon as dng
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

    uid = 999410
    uid2 = 999411
    await add_user(uid, "tester", "Тест", "")
    await add_user(uid2, "tester2", "Тест2", "")

    passed = 0
    failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
        else:
            failed += 1
            print(f"  FAIL: {name}")

    def cb_names():
        obs = dng.router.observers['callback_query']
        return {getattr(h.callback, '__name__', None) for h in obs.handlers}

    # ── 1. роутер зарегистрировал новые хендлеры ──
    for fn in ("dungeon_exit", "dungeon_exit_confirm", "dungeon_exit_cancel",
               "resv_cast", "resv_deeper", "dungeon_continue"):
        check(f"router: {fn} зарегистрирован", fn in cb_names())

    # ── 2. общий лок с озерной рыбалкой (тот же сет) ──
    check("FISHING_CASTING общий с fishing.py",
          dng.FISHING_CASTING is FISHING_CASTING)

    # ── 3. БД: забег + лут в run ──
    dungeon = (await get_all_dungeons(training=False))[0]
    await start_dungeon_run(uid, dungeon['id'])
    run = await get_active_run(uid)
    check("run активен (этаж 1, комната 0)",
          run is not None and run['floor'] == 1 and run['room_number'] == 0)
    # Комната 0 «уже прожита» (пустая, без наград): фиксируем в FSM, чтобы
    # отмена выхода не перебрасывала комнату и не доначисляла лут.
    state = FakeState()
    await state.update_data(dungeon_room_rolled=run['room_number'],
                            dungeon_room_type="empty", dungeon_room_nm=0)

    boot = await get_item_by_name("Старый сапог")
    check("сапог существует для теста лута", boot is not None)
    check("get_run_items сперва пуст", await get_run_items(run['id']) == [])
    await add_run_nordmarks(run['id'], 50)
    await add_run_item(run['id'], boot['id'], 2)
    ritems = await get_run_items(run['id'])
    check("run-лут: 2 сапога",
          len(ritems) == 1 and ritems[0]['name'] == "Старый сапог"
          and ritems[0]['quantity'] == 2)

    # ── 4. dungeon:exit → экран подтверждения ──
    cb = FakeCallback(uid, data="dungeon:exit")
    await dng.dungeon_exit(cb, state)
    ans = [m for m in cb.message.sent if m[0] == "answer"]
    check("показан экран подтверждения", len(ans) == 1)
    text = ans[0][1][0]
    check("текст: «Ты уверен…»", "уверен" in text)
    kb = ans[0][2].get('reply_markup')
    cbs = [b.callback_data for row in kb.inline_keyboard for b in row]
    check("кнопки ✅/↩️",
          "dungeon:exit:confirm" in cbs and "dungeon:exit:cancel" in cbs)
    check("забег жив пока ждём решения", await get_active_run(uid) is not None)

    # ── 5. cancel → возврат к экрану, забег не тронут ──
    cb2 = FakeCallback(uid, data="dungeon:exit:cancel")
    await dng.dungeon_exit_cancel(cb2, state)
    check("cancel: забег активен", await get_active_run(uid) is not None)
    redrawn = [m for m in cb2.message.sent if m[0] in ("answer", "answer_photo")]
    check("cancel: экран подземелья перерисован", bool(redrawn))

    # ── 6. confirm → лут и НМ перенесены, забег закрыт ──
    u_before = await get_user(uid)
    nm_before = u_before['nordmarks'] or 0
    cb3 = FakeCallback(uid, data="dungeon:exit:confirm")
    await dng.dungeon_exit_confirm(cb3, state)
    check("confirm: забег завершён", await get_active_run(uid) is None)
    inv_boot = await get_inventory_item(uid, boot['id'])
    check("confirm: сапоги в инвентаре",
          inv_boot is not None and inv_boot['quantity'] == 2)
    u_after = await get_user(uid)
    check("confirm: +50 НМ", (u_after['nordmarks'] or 0) - nm_before == 50)

    # ── 7. лок рыбалки: resv:deeper блокируется ──
    await start_dungeon_run(uid2, dungeon['id'])
    state4 = FakeState(state=dng.DungeonFSM.in_reservoir.state, data={'dungeon_step': 7})
    FISHING_CASTING.add(uid2)
    cb4 = FakeCallback(uid2, data="resv:deeper:7")
    await dng.resv_deeper(cb4, state4)
    check("resv_deeper: алерт пока рыбачишь",
          any(a is not None for a in cb4.alerts))
    check("resv_deeper: этаж остался 1", (await get_active_run(uid2))['floor'] == 1)

    # ── 8. лок рыбалки: dungeon:continue блокируется ──
    state5 = FakeState(state=dng.DungeonFSM.in_dungeon.state, data={'dungeon_step': 3})
    cb5 = FakeCallback(uid2, data="dungeon:continue:3")
    await dng.dungeon_continue(cb5, state5)
    check("dungeon_continue: алерт пока рыбачишь",
          any(a is not None for a in cb5.alerts))
    check("dungeon_continue: комната не продвинулась",
          (await get_active_run(uid2))['room_number'] == 0)

    # ── 9. лок рыбалки: dungeon:exit блокируется ──
    state6 = FakeState(state=dng.DungeonFSM.in_reservoir.state, data={'dungeon_step': 4})
    cb6 = FakeCallback(uid2, data="dungeon:exit")
    await dng.dungeon_exit(cb6, state6)
    check("dungeon_exit: алерт пока рыбачишь",
          any(a is not None for a in cb6.alerts))
    check("dungeon_exit: подтверждение не показано",
          not any(m[0] == "answer" for m in cb6.message.sent))
    check("dungeon_exit: забег жив", await get_active_run(uid2) is not None)

    # ── 10. лок рыбалки: повторный resv:cast блокируется ──
    state7 = FakeState(state=dng.DungeonFSM.in_reservoir.state, data={'dungeon_step': 9})
    cb7 = FakeCallback(uid2, data="resv:cast:9")
    await dng.resv_cast(cb7, state7)
    check("resv_cast: алерт повторного заброса",
          any(a is not None for a in cb7.alerts))
    check("resv_cast: сообщение не менялось",
          not any(m[0] in ("edit_text", "answer") for m in cb7.message.sent))

    FISHING_CASTING.discard(uid2)
    check("лок снят после discard",
          uid2 not in FISHING_CASTING)

    # ── 11. helper steps (FSM-защита от двойного клика) ──
    st = FakeState(data={})
    check("dungeon_current_step по умолчанию 0", await dng.dungeon_current_step(st) == 0)
    s1 = await dng.dungeon_new_step(st)
    s2 = await dng.dungeon_new_step(st)
    check("dungeon_new_step инкрементит", s1 == 1 and s2 == 2)

    await close_db()
    print(f"\nSmoke 058: {passed} passed, {failed} failed")
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