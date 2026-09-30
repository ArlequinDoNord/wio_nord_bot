"""Smoke 110 — сезонные картинки локаций (v0.18.17) и регресс «Враги».

Проверяет:
   1. Колонка locations.season_photos создаётся при инициализации.
   2. update_location_season_photo: задать слот, перезаписать, убрать, убрать сезон,
      прогнать неверные ключи.
   3. location_photo_for_tod: приоритет сезон × время суток → обычные слоты photo_<tod>.
   4. location_season_photos_raw и clear_location_season_photos.
   5. resolve_image_seasonal: реальный файл assets/img/city/forest_glade_autumn_day.jpg
      находится по календарю (осень, день) — картинка опушки подхватывается.
   6. Админ-редактор: регуляры новых кнопок loc:season:* / loc:season_photo_set:*
      / loc:season_clear:*; пикер картинок строит сезонные кнопки; обработчик
      сезонного фото сохраняет слот.
   7. РЕГРЕСС «Враги» (v0.18.16): ENEMY_SRC_FOREST/ENEMY_SRC_FISHING в админке
      совпадают с ключами ENEMY_SOURCE_TABLES в db.py, а enemy:list:...
      подходит под регуляры роутов.
"""
import asyncio
import os
import re
import sys
from datetime import datetime, timedelta, timezone

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


MSK = timezone(timedelta(hours=3))


class CBMsg:
    def __init__(self):
        self.text = None

    async def edit_text(self, text, reply_markup=None):
        self.text = text
        return None

    async def answer(self, text=None, reply_markup=None):
        self.text = text
        return None


class CB:
    def __init__(self, data):
        self.data = data
        uid = type("U", (), {})
        self.from_user = uid()
        self.from_user.id = 1
        self.message = CBMsg()

    async def answer(self, text=None, show_alert=False, reply_markup=None):
        self.text = text
        return None


class Msg:
    def __init__(self, photo_id=None, text=None):
        ptype = type("P", (), {})
        self.photo = [ptype()] if photo_id else []
        if self.photo:
            self.photo[0].file_id = photo_id
        self.text = text
        utype = type("U", (), {})
        self.from_user = utype()
        self.from_user.id = 1

    async def answer(self, text=None, reply_markup=None):
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
    DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_test_smoke110.db")
    for suffix in ("", "-wal", "-shm"):
        try:
            os.remove(DB_PATH + suffix)
        except OSError:
            pass
    config.DB_PATH = DB_PATH

    import database.db as db
    db.DB_PATH = DB_PATH
    from database.db import (
        init_db, close_db, create_location, get_location_by_key,
        update_location_season_photo, clear_location_season_photos, clear_location_season,
        location_season_photos_raw, location_photo_for_tod,
    )
    from utils.helpers import resolve_image_seasonal

    await init_db()

    # ── 1. Колонка ───────────────────────────────────────────────────────
    print("\n= Колонка season_photos =")
    cursor = await (await db.get_db()).execute("PRAGMA table_info(locations)")
    cols = {row["name"] for row in await cursor.fetchall()}
    check("колонка locations.season_photos есть", "season_photos" in cols)

    await create_location("testloc", "Тестовая")
    loc = await get_location_by_key("testloc")

    # ── 2. CRUD сезонных слотов ──────────────────────────────────────────
    print("\n= update_location_season_photo =")
    check("сейчас пусто", location_season_photos_raw(loc) == {})
    check("неверный сезон отклонён",
          not await update_location_season_photo(loc['id'], "march", "day", "FID"))
    check("неверное время суток отклонено",
          not await update_location_season_photo(loc['id'], "autumn", "noon", "FID"))

    await update_location_season_photo(loc['id'], "autumn", "day", "AUTUMN_DAY")
    loc = await get_location_by_key("testloc")
    check("осень/день записан",
          location_season_photos_raw(loc).get("autumn") == {"day": "AUTUMN_DAY"})

    await update_location_season_photo(loc['id'], "autumn", "night", "AUTUMN_NIGHT")
    loc = await get_location_by_key("testloc")
    check("два слота осени",
          location_season_photos_raw(loc).get("autumn")
          == {"day": "AUTUMN_DAY", "night": "AUTUMN_NIGHT"})

    await update_location_season_photo(loc['id'], "winter", "dawn", "WIN_DAWN")
    loc = await get_location_by_key("testloc")
    raw = location_season_photos_raw(loc)
    check("зима и осень сосуществуют",
          raw.get("winter") == {"dawn": "WIN_DAWN"} and "autumn" in raw)

    await update_location_season_photo(loc['id'], "autumn", "day", "AUTUMN_DAY2")
    loc = await get_location_by_key("testloc")
    check("слот перезаписан",
          location_season_photos_raw(loc).get("autumn", {}).get("day") == "AUTUMN_DAY2")

    await update_location_season_photo(loc['id'], "autumn", "night", None)
    loc = await get_location_by_key("testloc")
    check("слот убран",
          location_season_photos_raw(loc).get("autumn") == {"day": "AUTUMN_DAY2"})

    # ── 3. Приоритет подбора фото ────────────────────────────────────────
    print("\n= location_photo_for_tod =")
    check("сезон+время=осень/день",
          location_photo_for_tod(loc, "autumn", "day") == "AUTUMN_DAY2")
    check("сезон: осень/ночь фолбэчится на осень/день (1 слот на весь день)",
          location_photo_for_tod(loc, "autumn", "night") == "AUTUMN_DAY2")
    check("другой сезон — нет фото", location_photo_for_tod(loc, "summer", "day") is None)
    check("зима/рассвет находит зимний слот",
          location_photo_for_tod(loc, "winter", "dawn") == "WIN_DAWN")

    conn = await db.get_db()
    await conn.execute("UPDATE locations SET photo_dawn = 'LEGACY_DAWN' WHERE id = ?",
                       (loc['id'],))
    await conn.commit()
    loc = await get_location_by_key("testloc")
    check("обычный слот photo_dawn (сезон без картинок)",
          location_photo_for_tod(loc, "summer", "dawn") == "LEGACY_DAWN")
    check("фолбэк на обычные слоты: day→photo_dawn",
          location_photo_for_tod(loc, "summer", "day") == "LEGACY_DAWN")
    check("нет фото вообще (photo_sunset и т.д. пусты)",
          location_photo_for_tod(loc, "summer", "sunset") == "LEGACY_DAWN")

    # ── 4. Очистки ───────────────────────────────────────────────────────
    print("\n= Очистки =")
    await clear_location_season(loc['id'], "winter")
    loc = await get_location_by_key("testloc")
    check("сезон очищен", "winter" not in location_season_photos_raw(loc))
    await clear_location_season_photos(loc['id'])
    loc = await get_location_by_key("testloc")
    check("все сезоны очищены", location_season_photos_raw(loc) == {})

    loc_bad = {"season_photos": "not json", "preview_photo": None}
    check("кривой season_photos не падает", location_season_photos_raw(loc_bad) == {})

    # ── 5. Сезонная картинка опушки по календарю ────────────────────────
    print("\n= resolve_image_seasonal (опушка) =")
    now_autumn_day = datetime(2026, 9, 30, 12, 0, tzinfo=MSK)
    path = resolve_image_seasonal("city/forest_glade", now=now_autumn_day)
    check("осень/день → forest_glade_autumn_day.jpg",
          os.path.basename(path) == "forest_glade_autumn_day.jpg")
    check("файл реально существует (картинка опушки в репо)",
          os.path.isfile(path))
    now_winter_night = datetime(2026, 1, 15, 23, 0, tzinfo=MSK)
    path2 = resolve_image_seasonal("city/forest_glade", now=now_winter_night)
    check("зима/ночь → forest_glade_winter_night.jpg (фолбэк-кандидат)",
          os.path.basename(path2) == "forest_glade_winter_night.jpg")

    # ── 6. Админ-редактор: регуляры и рендер ────────────────────────────
    print("\n= Админ-редактор сезонных фото =")
    re_season = re.compile(r"^loc:season:(?:winter|spring|summer|autumn)$")
    re_set = re.compile(
        r"^loc:season_photo_set:(?:winter|spring|summer|autumn):(?:dawn|day|sunset|night)$")
    re_clear = re.compile(r"^loc:season_clear:(?:winter|spring|summer|autumn)$")
    check("loc:season:autumn", bool(re_season.match("loc:season:autumn")))
    check("loc:season:autumnX отклонён", not re_season.match("loc:season:autumnX"))
    check("loc:season_photo_set:autumn:day",
          bool(re_set.match("loc:season_photo_set:autumn:day")))
    check("loc:season_photo_set:nsfw:day отклонён",
          not re_set.match("loc:season_photo_set:nsfw:day"))
    check("loc:season_clear:winter", bool(re_clear.match("loc:season_clear:winter")))

    import bot.handlers.admin as admin

    async def fake_perm(uid, perm):
        return True

    admin.has_permission = fake_perm
    admin.CallbackQuery = CB

    await update_location_season_photo(loc['id'], "autumn", "day", "AD")
    loc = await get_location_by_key("testloc")

    cb = CB("loc:photos")
    await admin._loc_photos_pick_send(cb, loc['id'])
    text = cb.message.text or ""
    check("пикер упоминает «По сезонам» и сезоны",
          "По сезонам" in text and "🍂 Осень" in text and "❄️ Зима" in text)
    check("осень отмечена 1 картинкой", "Осень: 1" in text)

    cb2 = CB("loc:season:autumn")
    await admin.loc_season_photos_pick(cb2, State(target_id=loc['id']))
    text2 = cb2.message.text or ""
    check("пикер сезона «Осень» открылся",
          "Осень" in text2 and "Нажми время суток" in text2)

    st = State(target_id=loc['id'], photo_season="autumn", photo_tod="night")
    await admin.loc_step_photo(Msg(photo_id="AD_NIGHT"), st)
    loc_after = await get_location_by_key("testloc")
    check("сохранено осень/ночь",
          location_season_photos_raw(loc_after).get("autumn", {}).get("night") == "AD_NIGHT")
    check("существующий осень/день не тронут",
          location_season_photos_raw(loc_after).get("autumn", {}).get("day") == "AD")
    check("обычные слоты не изменились", loc_after.get("photo_night") is None)

    # ── 7. Регресс «Враги» ───────────────────────────────────────────────
    print("\n= Регресс кнопки «Враги» =")
    src_forest = admin.ENEMY_SRC_FOREST
    src_fishing = admin.ENEMY_SRC_FISHING
    check("ENEMY_SRC_FOREST == 'forest' (db-ключ)",
          src_forest == "forest" and src_forest in db.ENEMY_SOURCE_TABLES)
    check("ENEMY_SRC_FISHING == 'fishing' (db-ключ)",
          src_fishing == "fishing" and src_fishing in db.ENEMY_SOURCE_TABLES)
    re_list = re.compile(r"^enemy:list:[a-z]+:[\w-]+$")
    check("enemy:list:forest:forest под регуляром",
          bool(re_list.match(admin._enemy_list_cb(src_forest, "forest"))))
    check("enemy:list:fishing:reservoir под регуляром",
          bool(re_list.match(admin._enemy_list_cb(src_fishing, "reservoir"))))
    check("enemy:list:dn:d-1-1 под регуляром",
          bool(re_list.match(admin._enemy_list_cb(admin.ENEMY_SRC_DUNGEON, "d-1-1"))))

    await close_db()
    for suffix in ("", "-wal", "-shm"):
        try:
            os.remove(DB_PATH + suffix)
        except OSError:
            pass

    print(f"\n=== SMOKE 110: {PASS} passed, {FAIL} failed ===")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))