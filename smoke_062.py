"""Smoke v0.13.12: сброс «застрявшего» забега подземелья.

Проверяет:
1. start_dungeon_run пишет started_at (числовой epoch).
2. Свежий забег виден через get_active_run.
3. Протухший забег (> DUNGEON_RUN_STALE_SEC) автоматически завершается,
   лут и НМ переносятся, get_active_run возвращает None.
4. finalize_run_for переносит лут/НМ и делает забег неактивным.
5. Выход в город (show_city / city_menu_cb) завершает активный забег
   с переносом лута и чистит FSM подземелья.
6. КВП-забег (is_active) тоже сбрасывается тайм-аутом.

Запуск: .venv\\Scripts\\python.exe smoke_062.py
"""
import asyncio
import os
import sys
import time
from types import SimpleNamespace

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke062.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB

sys.path.insert(0, os.path.dirname(__file__))


class FakeMessage:
    def __init__(self):
        self.sent = []
        self.photo = None

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


async def run():
    from database.db import (
        init_db, close_db, seed_default_items, seed_dungeon, seed_kvp,
        ensure_dungeon_shop_items, ensure_dungeon_enemy_drops, ensure_life_items,
        ensure_dungeon_reservoir_items, ensure_water_fish, ensure_kvp_award,
        ensure_market_license_item, migrate_legacy_junk,
        add_user, get_user, get_item_by_name,
        start_dungeon_run, get_active_run, add_run_item, add_run_nordmarks,
        get_inventory_item, get_all_dungeons, finalize_run_for, end_run,
    )
    from config import DUNGEON_RUN_STALE_SEC
    from bot.handlers import start

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
    await migrate_legacy_junk()

    uid = 999501
    uid2 = 999502
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

    # ── 1. старт забега пишет started_at (числовой epoch) ──
    dungeon = (await get_all_dungeons(training=False))[0]
    await start_dungeon_run(uid, dungeon['id'])
    run = await get_active_run(uid)
    check("run создан", run is not None)
    check("started_at числовой epoch",
          isinstance(run.get('started_at'), (int, float)))

    # ── 2. свежий забег виден ──
    boot = await get_item_by_name("Старый сапог")
    check("сапог есть для теста", boot is not None)
    await add_run_nordmarks(run['id'], 60)
    await add_run_item(run['id'], boot['id'], 3)
    check("свежий забег активен", await get_active_run(uid) is not None)

    # ── 3. протухший забег завершается тайм-аутом ──
    from database.db import get_db
    dbs = await get_db()
    await dbs.execute(
        "UPDATE player_dungeon_run SET started_at = ? WHERE user_id = ?",
        (time.time() - DUNGEON_RUN_STALE_SEC - 300, uid)
    )
    n_before = (await get_user(uid))['nordmarks'] or 0
    check("протухший забег отдаёт None",
          await get_active_run(uid) is None)
    u_after = await get_user(uid)
    check("тайм-аут: +60 НМ перенесено",
          (u_after['nordmarks'] or 0) - n_before == 60)
    check("тайм-аут: сапоги в инвентаре",
          await get_inventory_item(uid, boot['id']) is not None)
    check("тайм-аут: повторный запрос None",
          await get_active_run(uid) is None)

    # ── 4. finalize_run_for — перенос и завершение ──
    await start_dungeon_run(uid2, dungeon['id'])
    run2 = await get_active_run(uid2)
    await add_run_nordmarks(run2['id'], 25)
    await add_run_item(run2['id'], boot['id'], 1)
    await finalize_run_for(uid2, run2['id'], "test_finalize",
                           "Тест финализации", loot_nm=25)
    check("finalize: забег неактивен", await get_active_run(uid2) is None)
    check("finalize: сапог в инвентаре",
          await get_inventory_item(uid2, boot['id']) is not None)
    n2 = (await get_user(uid2))['nordmarks'] or 0
    check("finalize: +25 НМ", n2 >= 25)

    # ── 5. выход в город завершает забег и чистит FSM ──
    await start_dungeon_run(uid, dungeon['id'])
    check("забег для теста города активен", await get_active_run(uid) is not None)
    msg = FakeMessage()
    msg.from_user = SimpleNamespace(id=uid)
    st = FakeState(state="dungeon:in_reservoir", data={'dungeon_step': 4})
    await start.show_city(msg, st)
    check("show_city: забег завершён", await get_active_run(uid) is None)
    check("show_city: FSM почищен", st.cleared)
    city_answers = [m for m in msg.sent if m[0] == "answer"]
    check("show_city: сообщение о завершении показано",
          any("забег завершён" in m[1][0] for m in city_answers))

    # ── 6. city_menu_cb — то же через колбэк ──
    await start_dungeon_run(uid, dungeon['id'])
    cb_msg = FakeMessage()
    cb = FakeCallback(uid, data="city:menu", message=cb_msg)
    st2 = FakeState(data={'dungeon_step': 2})
    await start.city_menu_cb(cb, st2)
    check("city_menu_cb: забег завершён", await get_active_run(uid) is None)
    check("city_menu_cb: FSM почищен", st2.cleared)

    # ── 7. КВП-забег тоже завершается тайм-аутом ──
    run_k = None
    try:
        from database.db import get_db, get_kvp_dungeon
        kvp_dng = await get_kvp_dungeon()
        if kvp_dng is not None:
            await start_dungeon_run(uid, kvp_dng['id'])
            run_k = await get_active_run(uid)
            if run_k:
                dbs2 = await get_db()
                await dbs2.execute(
                    "UPDATE player_dungeon_run SET started_at = ? WHERE user_id = ?",
                    (time.time() - DUNGEON_RUN_STALE_SEC - 60, uid)
                )
                check("КВП: протухший забег сброшен",
                      await get_active_run(uid) is None)
            else:
                check("КВП: run создан", False)
        else:
            check("КВП: данж есть (пропуск)", False)
    except Exception as e:
        check(f"КВП-ветка: {e!r}", False)

    if run_k:
        await end_run(run_k['id'], 0)

    await close_db()
    print(f"\nSmoke 062: {passed} passed, {failed} failed")
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