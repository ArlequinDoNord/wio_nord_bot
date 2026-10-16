"""Smoke v0.32.1: городские склады — выкупленные казной ресурсы копятся.

1) Таблица `city_storage` и хелперы `add_city_storage`/`get_city_storage`:
   накопление, no-op при qty<=0, соединение с именем предмета.
2) Продажа ресурса (`category == 'resource'`) кладёт единицы на склад;
   продажа не-ресурса склад не пополняет.
3) Локация `storage` засеяна (вход с «Пилота 1 класса»), строка доступа в
   превью, туриста не пускают, пилота — пускают.
4) Колонка `locations.storage_photo` + кнопка «Зал склада» в админ-редакторе.
5) Экран склада (`build_storage_text`, `storage_menu`) рисуется без падений.

Запуск: .venv\\Scripts\\python.exe smoke_152.py
"""
import asyncio
import os
import sys

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke152.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB

sys.path.insert(0, os.path.dirname(__file__))


class FakeMessage:
    def __init__(self, user_id, bot=None):
        self.from_user = type("U", (), {"id": user_id})()
        self.chat = type("C", (), {"id": user_id})()
        self.message_id = 1
        self.bot = bot
        self.sent = []

    async def answer(self, text=None, *a, **kw):
        self.sent.append(("answer", text, kw))

    async def answer_photo(self, photo=None, caption=None, *a, **kw):
        self.sent.append(("answer_photo", caption, kw))

    async def edit_text(self, text=None, *a, **kw):
        self.sent.append(("edit_text", text, kw))

    async def __getattr__(self, name):
        async def _noop(*a, **kw):
            return None
        return _noop


class FakeCallback:
    def __init__(self, user_id, data="", message=None):
        self.from_user = type("U", (), {"id": user_id})()
        self.message = message or FakeMessage(user_id)
        self.data = data
        self.alerts = []

    async def answer(self, text=None, *a, **kw):
        self.alerts.append(text)


def markup_callbacks(markup):
    out = set()
    for row in getattr(markup, "inline_keyboard", []) or []:
        for btn in row:
            out.add(btn.callback_data)
    return out


def texts_of(cb):
    return [m[1] for m in cb.message.sent if m[1]]


async def run():
    from database.db import (
        init_db, close_db, seed_default_items, add_user, add_item,
        add_inventory_item, add_city_storage, get_city_storage,
        get_location_by_key, get_all_locations, can_enter_location,
        ensure_base_statuses, get_status_by_tag, grant_status,
        location_storage_photo, update_location_storage_photo,
    )
    from bot.handlers.inventory import _sell_item
    from bot.handlers import locations as locs
    from bot.handlers import admin as adm
    from bot.handlers.storage import build_storage_text, storage_menu

    await init_db()
    await seed_default_items()

    passed = 0
    failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
        else:
            failed += 1
            print(f"  FAIL: {name}")

    uid = 999152
    await add_user(uid, "tester152", "Тест", "")

    try:
        # ── 1. хелперы склада ──
        res_id = await add_item("Ресурс-тест", "руда", 40, 20, 1, "resource", -1, uid)
        check("ресурс создан", bool(res_id))

        await add_city_storage(res_id, 5)
        row = next((r for r in await get_city_storage() if r['item_id'] == res_id), None)
        check("склад: запись добавлена", row is not None and row['qty'] == 5)
        check("склад: имя предмета в выборке", row['name'] == "Ресурс-тест")
        await add_city_storage(res_id, 3)
        row = next((r for r in await get_city_storage() if r['item_id'] == res_id), None)
        check("склад: накопительно (5+3=8)", row['qty'] == 8)

        await add_city_storage(res_id, 0)
        await add_city_storage(res_id, -5)
        row = next((r for r in await get_city_storage() if r['item_id'] == res_id), None)
        check("склад: qty<=0 не меняет остаток", row['qty'] == 8)

        # ── 2. продажа ресурса пополняет склад ──
        uid2 = 9991521
        await add_user(uid2, "seller", "Селянин", "")
        res2 = await add_item("Железо-тест", "руда", 40, 20, 1, "resource", -1, uid2)
        cons2 = await add_item("Зелье-тест", "пойло", 10, 5, 1, "consumable", -1, uid2)
        await add_inventory_item(uid2, res2, 5)
        await add_inventory_item(uid2, cons2, 5)

        await _sell_item(FakeCallback(uid2), res2, 3)
        row = next((r for r in await get_city_storage() if r['item_id'] == res2), None)
        check("продажа ресурса x3 -> на складе 3", row is not None and row['qty'] == 3)

        await _sell_item(FakeCallback(uid2), res2, 2)
        row = next((r for r in await get_city_storage() if r['item_id'] == res2), None)
        check("продажа ресурса ещё x2 -> на складе 5", row['qty'] == 5)

        await _sell_item(FakeCallback(uid2), cons2, 2)
        check("продажа не-ресурса склад не пополняет",
              not any(r['item_id'] == cons2 for r in await get_city_storage()))

        # ── 3. локация и доступ ──
        store_loc = await get_location_by_key("storage")
        check("локация storage засеяна", store_loc is not None)
        check("storage: режим min/pilot1",
              store_loc['access_mode'] == "min"
              and store_loc['required_status'] == "pilot1")
        check("storage: картинка входа city/storage",
              store_loc['preview_photo'] == "city/storage")
        check("storage: есть в списке локаций города",
              any(l['key'] == "storage" for l in await get_all_locations()))
        check("storage: своя строка доступа",
              "Пилота 1 класса" in locs.LOCATION_ACCESS_LINES.get("storage", ""))

        await ensure_base_statuses()
        tourist_id = 9991522
        await add_user(tourist_id, "touristx", "Тур", "")
        pilot_id = 9991523
        await add_user(pilot_id, "pilotx", "Пилот", "")
        await grant_status(pilot_id, (await get_status_by_tag("pilot1"))['id'])
        check("туриста в склады не пускают",
              not await can_enter_location(tourist_id, "storage"))
        check("пилота 1 класса пускают",
              await can_enter_location(pilot_id, "storage"))

        cb_prev = FakeCallback(tourist_id, data="location:preview:storage")
        await locs.location_preview(cb_prev)
        check("превью storage: строка «Пилота 1 класса»",
              any("Пилота 1 класса" in (t or "") for t in texts_of(cb_prev)))

        # ── 4. картинка зала склада ──
        check("storage_photo: колонка читается", location_storage_photo(store_loc) is None)
        await update_location_storage_photo(store_loc['id'], "file_abc")
        check("storage_photo: сохранение",
              location_storage_photo(await get_location_by_key("storage")) == "file_abc")
        await update_location_storage_photo(store_loc['id'], None)
        check("storage_photo: очистка",
              location_storage_photo(await get_location_by_key("storage")) is None)

        cb_pick = FakeCallback(uid)
        await adm._loc_photos_pick_send(cb_pick.message, store_loc['id'])
        cbs = set()
        for m in cb_pick.message.sent:
            if m[2].get("reply_markup"):
                cbs |= markup_callbacks(m[2]["reply_markup"])
        check("админ: кнопка «Зал склада» (loc:storage_set)", "loc:storage_set" in cbs)
        check("админ: у storage нет кнопки «Опушка/Прогалина»",
              "loc:glade_set" not in cbs and "loc:clearing_set" not in cbs)

        # ── 5. экран склада ──
        text = build_storage_text(await get_city_storage())
        check("экран: заголовок", "ГОРОДСКИЕ СКЛАДЫ" in text)
        check("экран: показывает проданный ресурс", "Железо-тест" in text)
        check("экран: итог", "Всего единиц:" in text)
        check("экран: пустой склад — подсказка", "Склады пусты" in build_storage_text([]))

        cb_store = FakeCallback(pilot_id)
        await storage_menu(cb_store)
        joined = "\n".join(texts_of(cb_store))
        check("storage_menu: рисует и не падает",
              ("СКЛАДЫ" in text) or ("Склады пусты" in text))
    finally:
        await close_db()

    print(f"\nSmoke 152: {passed} passed, {failed} failed")
    return failed


if __name__ == "__main__":
    sys.exit(1 if asyncio.run(run()) else 0)
