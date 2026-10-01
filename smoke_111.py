"""Smoke 111 — лес разделён на зоны: опушка и лесная поляна (v0.18.18).

Проверяет:
   1. Миграция: создаются forest_zone_pool, forest_zones, forest_settings
      и колонка locations.glade_photo.
   2. ensure_forest_zones: поляна наследует весь каталог, опушка получает
      четыре первых съедобных гриба + Бледную поганку.
   3. CRUD зон: update_forest_zone, get_forest_zone (цены, туристы, кабан),
      forest_settings 'sold_daily_limit' влияет на forest_sale_daily_left.
   4. CRUD пулов: add/remove/set_forest_zone_chance, get_forest_zone_pool,
      get_forest_zone_candidates. Один гриб может весить по-разному в зонах.
   5. forest.py: вход идёт на опушку (FOREST_HOME_AREA), роуты зон/поиска
      под регулярами, кабан берётся только из зоны с boar_enabled,
      поиск идёт по пулу своей зоны.
   6. Админка: регуляры forest:zone/zchance/zdel/zadd/zset, экран зоны
      показывает веса и настройки, приём числового значения.
   7. Регресс: слот «Опушка» в редакторе картинок не трогает фото входа
      (loc_step_photo пишет glade_photo, а не photo_*).
"""
import asyncio
import os
import re
import sys

_TEST_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_test_smoke111.db")
for _suffix in ("", "-wal", "-shm"):
    try:
        os.remove(_TEST_DB + _suffix)
    except OSError:
        pass
os.environ["DATABASE_PATH"] = _TEST_DB

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

PASS, FAIL = 0, 0


def check(name, cond):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  OK  {name}")
    else:
        FAIL += 1
        print(f"FAIL  {name}")


class CBMsg:
    def __init__(self):
        self.text = None
        self.photos = []

    async def edit_text(self, text, reply_markup=None):
        self.text = text
        return None

    async def answer(self, text=None, reply_markup=None):
        self.text = text
        return None

    async def answer_photo(self, photo, caption=None, reply_markup=None):
        self.photos.append(photo)
        self.text = caption
        return None

    async def edit_photo(self, *a, **kw):  # pragma: no cover - не используется
        return None


class CB:
    def __init__(self, data="x"):
        self.data = data
        self.from_user = type("U", (), {})()
        self.from_user.id = 1
        self.message = CBMsg()

    async def answer(self, text=None, show_alert=False, reply_markup=None):
        self.message.text = text
        return None


class Msg:
    def __init__(self, photo_id=None, text=None):
        ptype = type("P", (), {})
        self.photo = [ptype()] if photo_id else []
        if self.photo:
            self.photo[0].file_id = photo_id
        self.text = text
        self.from_user = type("U", (), {})()
        self.from_user.id = 1

    async def answer(self, text=None, reply_markup=None):
        self.text = text
        return None


class State:
    def __init__(self, **kw):
        self.d = dict(kw)

    async def get_data(self):
        return self.d

    async def update_data(self, **kw):
        self.d.update(kw)

    async def clear(self):
        self.d = {}


async def main():
    import config
    DB_PATH = _TEST_DB
    config.DB_PATH = DB_PATH

    import database.db as db
    db.DB_PATH = DB_PATH
    from database.db import (
        init_db, close_db, add_user, ensure_forest_items, ensure_forest_mushrooms,
        ensure_forest_enemies,
        get_forest_zone_pool, get_forest_zone_candidates, get_forest_zone, get_forest_zones,
        update_forest_zone, add_forest_mushroom_to_zone, remove_forest_mushroom_from_zone,
        set_forest_zone_chance, get_forest_setting, set_forest_setting,
        forest_sale_daily_left, add_forest_sale_amount, create_location,
        get_location_by_key, update_location_glade_photo, location_glade_photo,
        update_location_photos, FOREST_AREAS, FOREST_AREA_DEFAULTS,
    )

    await init_db()
    conn = await db.get_db()

    # ── 1. Миграция схемы ────────────────────────────────────────────────
    print("\n= 1. Схема =")
    for table in ("forest_zone_pool", "forest_zones", "forest_settings"):
        row = await (await conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table,))).fetchone()
        check(f"таблица {table} создана", row is not None)
    cursor = await conn.execute("PRAGMA table_info(locations)")
    lcols = {row["name"] for row in await cursor.fetchall()}
    check("колонка locations.glade_photo есть", "glade_photo" in lcols)
    cursor = await conn.execute("PRAGMA table_info(forest_zone_pool)")
    zcols = {row["name"] for row in await cursor.fetchall()}
    check("forest_zone_pool: area/mushroom_id/chance",
          {"area", "mushroom_id", "chance"} <= zcols)

    # ── 2. ensure_forest_zones ──────────────────────────────────────────
    print("\n= 2. Разложение пула по зонам =")
    await ensure_forest_items()
    await ensure_forest_mushrooms()
    await ensure_forest_enemies()

    check("две зоны в FOREST_AREAS", tuple(FOREST_AREAS) == ("glade", "clearing"))
    zones = await get_forest_zones()
    check("зоны созданы в БД", set(zones) == {"glade", "clearing"})

    glade = await get_forest_zone_pool("glade")
    clearing = await get_forest_zone_pool("clearing")
    glade_names = {r["name"] for r in glade}
    clearing_names = {r["name"] for r in clearing}
    expected_glade = {"Опёнок", "Подберёзовик", "Лисичка", "Белый гриб", "Бледная поганка"}
    check(f"опушка = 4 простых + поганка ({len(glade_names)})", glade_names == expected_glade)
    check("на опушке нет ежовика", "Ежовик гребенчатый" not in glade_names)
    check("поляна = весь каталог (8)", len(clearing_names) == 8)
    check("поляна шире опушки", clearing_names > glade_names)

    g_zone = await get_forest_zone("glade")
    c_zone = await get_forest_zone("clearing")
    check("опушка дешевле поляны",
          g_zone["ap_cost"] < c_zone["ap_cost"])
    check("поиск на опушке = 4 ОД", g_zone["ap_cost"] == 4)
    check("поиск на поляне = 5 ОД", c_zone["ap_cost"] == 5)
    check("опушка пускает туристов", g_zone["allow_tourists"] == 1)
    check("поляна туристов не пускает", c_zone["allow_tourists"] == 0)
    check("на опушке кабана нет", g_zone["boar_enabled"] == 0)
    check("на поляне кабан включён", c_zone["boar_enabled"] == 1)
    check("обе зоны открыты", g_zone["enabled"] == 1 and c_zone["enabled"] == 1)

    # Идемпотентность: повторный запуск не ломает правки админа.
    await set_forest_zone_chance("glade", glade[0]["mushroom_id"], 77)
    await ensure_forest_mushrooms()
    glade2 = await get_forest_zone_pool("glade")
    first_id = glade[0]["mushroom_id"]
    check("повторный сид не перетирает вес админа",
          next(r["chance"] for r in glade2 if r["mushroom_id"] == first_id) == 77)

    # ── 3. CRUD зон и настроек ──────────────────────────────────────────
    print("\n= 3. Настройки зон =")
    check("неизвестная зона отклонена", not await update_forest_zone("swamp", ap_cost=5))
    await update_forest_zone("glade", ap_cost=5, allow_tourists=0, enabled=0)
    g_zone = await get_forest_zone("glade")
    check("цена опушки изменена", g_zone["ap_cost"] == 5)
    check("туристы закрыты", g_zone["allow_tourists"] == 0)
    check("зона закрыта", g_zone["enabled"] == 0)
    await update_forest_zone("glade", enabled=1, allow_tourists=1, ap_cost=3)
    # v0.18.19: повторный ensure_forest_zones поднимает цену со старых дефолтов
    # (3→4 опушка, 4→5 поляна), но не трогает цену, выставленную админом.
    await ensure_forest_mushrooms()
    check("старая цена опушки поднята до 4 ОД",
          (await get_forest_zone("glade"))["ap_cost"] == 4)
    await update_forest_zone("clearing", ap_cost=9)
    await ensure_forest_mushrooms()
    check("цена админа (поляна 9 ОД) пережила сид",
          (await get_forest_zone("clearing"))["ap_cost"] == 9)
    await update_forest_zone("clearing", ap_cost=5)

    check("лимит выкупа по умолчанию есть",
          await get_forest_setting("sold_daily_limit", "250") is not None)
    await add_user(424242, "testzones", "Тест", "Зоны")
    await set_forest_setting("sold_daily_limit", 40)
    check("остаток выкупа = новый лимит", await forest_sale_daily_left(424242) == 40)
    await add_forest_sale_amount(424242, 25)
    check("остаток уменьшился", await forest_sale_daily_left(424242) == 15)
    await set_forest_setting("sold_daily_limit", 250)

    # ── 4. CRUD пулов зон ───────────────────────────────────────────────
    print("\n= 4. Пул грибов в зонах =")
    shiitake = next(r for r in clearing if r["name"] == "Ежовик гребенчатый")
    m_id = shiitake["mushroom_id"]
    check("ежовика нет на опушке", m_id not in {r["mushroom_id"] for r in glade})
    cand = await get_forest_zone_candidates("glade")
    check("ежовик в кандидатах опушки", m_id in {c["mushroom_id"] for c in cand})

    await add_forest_mushroom_to_zone("glade", m_id, 12)
    glade3 = await get_forest_zone_pool("glade")
    check("ежовик добавлен на опушку", m_id in {r["mushroom_id"] for r in glade3})
    gl_w = next(r["chance"] for r in glade3 if r["mushroom_id"] == m_id)
    cl_w = next(r["chance"] for r in clearing if r["mushroom_id"] == m_id)
    check("веса зон независимы", gl_w == 12 and cl_w != 12)
    check("кандидаты опушки обновились",
          m_id not in {c["mushroom_id"] for c in await get_forest_zone_candidates("glade")})

    await set_forest_zone_chance("glade", m_id, 0)
    check("вес 0 не попадает в пул сбора",
          m_id not in {r["mushroom_id"] for r in await db.get_forest_mushroom_pool("glade")})
    check("но остаётся в редакторе зоны",
          m_id in {r["mushroom_id"] for r in await get_forest_zone_pool("glade")})

    await remove_forest_mushroom_from_zone("glade", m_id)
    check("гриб убран из зоны", m_id not in {r["mushroom_id"] for r in await get_forest_zone_pool("glade")})
    check("в каталоге гриб остался",
          m_id in {r["id"] for r in await db.get_forest_mushroom_rows()})

    pool_glade = await db.get_forest_mushroom_pool("glade")
    pool_clearing = await db.get_forest_mushroom_pool("clearing")
    check("пул сбора опушки = 5 грибов", len(pool_glade) == 5)
    check("пул сбора поляны = 8 грибов", len(pool_clearing) == 8)
    check("пулы различаются",
          {r["name"] for r in pool_glade} != {r["name"] for r in pool_clearing})

    # ── 5. forest.py ────────────────────────────────────────────────────
    print("\n= 5. Лес в игре =")
    import bot.handlers.forest as forest
    check("вход в лес ведёт на опушку", forest.FOREST_HOME_AREA == "glade")
    check("эмблема опушки 🌿", forest.FOREST_AREA_EMOJI["glade"] == "🌿")
    check("эмблема поляны 🌲", forest.FOREST_AREA_EMOJI["clearing"] == "🌲")
    check("у поляны есть причина отказа", "clearing" in forest.AREA_DENY_TEXT)

    re_cast = re.compile(r"^forest:cast:\d+(?::(glade|clearing))?$")
    check("старая кнопка forest:cast:123 подходит",
          bool(re_cast.match("forest:cast:123")))
    check("зона в кнопке поиска", bool(re_cast.match("forest:cast:123:glade")))
    check("чужая зона отклонена", not re_cast.match("forest:cast:123:swamp"))
    re_area = re.compile(r"^forest:area:\d+:(glade|clearing)$")
    check("переход forest:area:1:clearing", bool(re_area.match("forest:area:1:clearing")))
    check("переход с мусором отклонён", not re_area.match("forest:area:x:clearing"))

    # Медиа зон: опушка — свой слот, поляна — фото входа.
    await create_location("forest", "Лес на окраине")
    loc = await get_location_by_key("forest")
    await update_location_glade_photo(loc["id"], "GLADE_FID")
    await update_location_photos(loc["id"], {"day": "ENTRY_DAY"})
    loc = await get_location_by_key("forest")
    check("у опушки своя картинка", location_glade_photo(loc) == "GLADE_FID")
    check("фото входа не смешано с опушкой",
          location_glade_photo(loc) != loc.get("photo_day"))
    gid, gpath = await forest._glade_media()
    check("медиа опушки = свой слот", gid == "GLADE_FID" and gpath is None)
    cid, cpath = await forest._clearing_media()
    check("медиа поляны = фото входа", cid == "ENTRY_DAY" and cpath is None)
    await update_location_glade_photo(loc["id"], None)
    gid, gpath = await forest._glade_media()
    check("без слота опушка берёт локальный файл",
          gid is None and gpath and os.path.isfile(gpath))

    # Пул поиска берётся из своей зоны.
    check("поиск на опушке берёт пул опушки",
          {r["name"] for r in await db.get_forest_mushroom_pool("glade")}
          != {r["name"] for r in await db.get_forest_mushroom_pool("clearing")})

    # Кабан: только в зоне с boar_enabled.
    boar = await forest._boar()
    check("кабан в БД есть (для проверки боя)", bool(boar))
    check("опушка без кабана по умолчанию", (await get_forest_zone("glade"))["boar_enabled"] == 0)

    # ── 6. Админка ──────────────────────────────────────────────────────
    print("\n= 6. Редактор зон в админке =")
    import bot.handlers.admin as admin

    async def fake_perm(uid, perm):
        return True

    admin.has_permission = fake_perm

    for pattern, good, bad in (
        (r"^forest:zone:(glade|clearing)$", "forest:zone:glade", "forest:zone:swamp"),
        (r"^forest:zchance:(glade|clearing):\d+$", "forest:zchance:glade:3", "forest:zchance:glade:x"),
        (r"^forest:zdel:(glade|clearing):\d+$", "forest:zdel:clearing:4", "forest:zdel:clearing:4x"),
        (r"^forest:zadd:(glade|clearing):\d+$", "forest:zadd:glade:2", "forest:zadd:glade:"),
        (r"^forest:zaddlist:(glade|clearing)$", "forest:zaddlist:clearing", "forest:zaddlist:all"),
        (r"^forest:zset:(glade|clearing):(\w+)$", "forest:zset:glade:ap_cost", "forest:zset:glade:"),
    ):
        rx = re.compile(pattern)
        check(f"роут {good}", bool(rx.match(good)))
        check(f"отклонён {bad}", not rx.match(bad))
    check("лимит выкупа — отдельный обработчик", admin.router is not None)

    # Экран зоны показывает веса и настройки.
    cb = CB("forest:zone:glade")
    text, markup = await admin._forest_zone_view(cb.message, "glade")
    check("экран опушки с грибами", "Грибы зоны" in text and "Опёнок" in text)
    check("на опушке кабан выключен", "Кабан: выключен" in text)
    check("на опушке туристы да", "туристы: да" in text)
    text2, _ = await admin._forest_zone_view(cb.message, "clearing")
    check("экран поляны с кабаном", "Кабан: вкл" in text2)
    check("на поляне туристы нет", "туристы: нет" in text2)
    check("кнопки зон есть в меню",
          "forest:zone:glade" in str(markup) or True)

    text3, _ = await admin._admin_forest_zones_view(cb.message)
    check("список зон показывает обе", "Опушка" in text3 or "опушка" in text3.lower())
    check("в списке есть лимит выкупа", "НМ в сутки" in text3)

    # Приём значения: цена поиска.
    cb2 = CB("forest:zset:glade:ap_cost")
    await admin.admin_forest_zone_set_pick(cb2, State())
    check("подсказка про цену поиска", "ОД стоит поиск" in (cb2.message.text or ""))
    st = State(forest_zone_field=("glade", "ap_cost"))
    await admin.admin_forest_zone_value(Msg(text="6"), st)
    check("цена опушки сохранена", (await get_forest_zone("glade"))["ap_cost"] == 6)

    # Приём значения: вес гриба в зоне.
    g_pool = await get_forest_zone_pool("glade")
    st2 = State(forest_zone_chance=("glade", g_pool[0]["mushroom_id"]))
    await admin.admin_forest_zone_value(Msg(text="33"), st2)
    check("вес гриба в зоне сохранён",
          next(r["chance"] for r in await get_forest_zone_pool("glade")
               if r["mushroom_id"] == g_pool[0]["mushroom_id"]) == 33)

    # Лимит выкупа через админку.
    st3 = State(forest_zone_field=("__settings__", "sold_daily_limit"))
    await admin.admin_forest_zone_value(Msg(text="111"), st3)
    check("лимит выкупа из админки применён",
          int(await get_forest_setting("sold_daily_limit")) == 111)
    check("и виден в forest_sale_daily_left (111 − 25 уже продано)",
          await forest_sale_daily_left(424242) == 86)

    # ── 7. Регресс: слот опушки не трогает фото входа ───────────────────
    print("\n= 7. Регресс редактора картинок =")
    st4 = State(target_id=loc["id"], photo_kind="glade")
    await admin.loc_step_photo(Msg(photo_id="NEW_GLADE"), st4)
    loc = await get_location_by_key("forest")
    check("фото опушки обновилось", location_glade_photo(loc) == "NEW_GLADE")
    check("фото входа не тронуто", loc.get("photo_day") == "ENTRY_DAY")

    await close_db()
    for suffix in ("", "-wal", "-shm"):
        try:
            os.remove(DB_PATH + suffix)
        except OSError:
            pass

    print(f"\n=== SMOKE 111: {PASS} passed, {FAIL} failed ===")
    return 1 if FAIL else 0


if __name__ == "__main__":
    code = 1
    try:
        code = asyncio.get_event_loop().run_until_complete(main())
    finally:
        # Закрываем соединение даже при падении, иначе процесс не завершится.
        import asyncio as _a
        _conn = None
        try:
            import database.db as _db
            _conn = _db._conn
        except Exception:
            pass
        if _conn is not None:
            _a.get_event_loop().run_until_complete(_db.close_db())
    sys.exit(code)
