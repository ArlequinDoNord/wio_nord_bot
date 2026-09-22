"""Smoke v0.15.2: фото комнат К.В.П. + «Состав ВВС».

Проверяет:
1. update_dungeon_photos сохраняет слоты photo_water/photo_rope (К.В.П.).
2. answer_enemy_or_course_photo: с картинкой врага — фото врага; без неё —
   входная картинка курса (fallback).
3. answer_obstacle_photo: water/rope — свои картинки препятствий; без них —
   входная картинка курса.
4. Админ-пикер данжа предлагает слоты «Вода» и «Верёвка».
5. hq:wing — сводка по крыльям; hq:wing:set — назначение крыла пилоту;
   кнопка «Состав ВВС» видна только при праве can_manage_wing.

Запуск: .venv\\Scripts\\python.exe smoke_070.py
"""
import asyncio
import os
import sys
from types import SimpleNamespace

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke070.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB

_ADMIN_ID = 420001
os.environ["ADMIN_IDS"] = str(_ADMIN_ID)

sys.path.insert(0, os.path.dirname(__file__))


class FakeMessage:
    def __init__(self, user_id, text="", message_id=100):
        self.from_user = SimpleNamespace(id=user_id)
        self.text = text
        self.message_id = message_id
        self.sent = []

    async def answer(self, *a, **kw):
        self.sent.append(("answer", a, kw))

    async def answer_photo(self, *a, **kw):
        self.sent.append(("answer_photo", a, kw))

    async def edit_text(self, *a, **kw):
        self.sent.append(("edit_text", a, kw))


class FakeCallback:
    def __init__(self, user_id, data="", message=None):
        self.from_user = SimpleNamespace(id=user_id)
        self.message = message or FakeMessage(user_id)
        self.data = data
        self.alerts = []

    async def answer(self, text=None, *a, **kw):
        self.alerts.append(text)


def sent_text(msg):
    for kind, a, kw in msg.sent:
        if kind in ("answer", "edit_text") and a:
            return a[0]
        if kind == "answer_photo" and kw.get('caption'):
            return kw.get('caption')
    return ""


def sent_photo(msg):
    for kind, a, kw in msg.sent:
        if kind == "answer_photo":
            return kw.get('photo')
    return None


def markup_callbacks(markup):
    if not markup:
        return []
    return [b.callback_data for row in markup.inline_keyboard for b in row]


async def run():
    from database.db import (
        init_db, close_db, add_user, get_user, seed_kvp, update_dungeon_photos,
        get_kvp_dungeon, DUNGEON_PHOTO_KEYS,
    )
    from bot.handlers.kvp import answer_enemy_or_course_photo, answer_obstacle_photo
    from bot.handlers.admin import _dungeon_photos_pick_send
    from bot.handlers.hq import (
        hq_wing_cb, hq_roster_pick, hq_pilot_cb, hq_wingset, hq_menu_markup,
    )

    await init_db()

    passed = 0
    failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
        else:
            failed += 1
            print(f"  FAIL: {name}")

    # ── 0. Базовые данные ──
    pilot = 420010
    await add_user(pilot, "nebo", "Пилот", "")
    admin = _ADMIN_ID
    await add_user(admin, "komand", "Командующий", "")

    dng_id = await seed_kvp()
    dng = await get_kvp_dungeon()
    check("данж К.В.П. создан", dng is not None and dng['id'] == dng_id)

    entrance = "AgACAg_ENTRANCE_070"
    water = "AgACAg_WATER_070"
    rope = "AgACAg_ROPE_070"

    # ── 1. update_dungeon_photos: слоты water/rope сохраняются ──
    ok = await update_dungeon_photos(dng_id, {"dawn": entrance})
    check("update входного слота", ok is True)
    dng = await get_kvp_dungeon()
    check("photo_dawn записан", dng['photo_dawn'] == entrance)

    ok = await update_dungeon_photos(dng_id, {"water": water, "rope": rope})
    check("update water/rope применился", ok is True)
    dng = await get_kvp_dungeon()
    check("photo_water записан", dng['photo_water'] == water)
    check("photo_rope записан", dng['photo_rope'] == rope)
    check("DUNGEON_PHOTO_KEYS содержит воду и верёвку",
          "water" in DUNGEON_PHOTO_KEYS and "rope" in DUNGEON_PHOTO_KEYS)

    # ── 2. Враг: своя картинка, иначе вход курса ──
    enemy_img = {"name": "Ефрейтор", "hp": 15, "attack": 2, "image": "AgACAg_ENEMY_070"}
    msg_em = FakeMessage(pilot)
    await answer_enemy_or_course_photo(msg_em, enemy_img, "Бой с фото врага")
    check("враг с картинкой — answer_photo с фото врага",
          sent_photo(msg_em) == enemy_img["image"])

    enemy_noimg = {"name": "Ефрейтор", "hp": 15, "attack": 2, "image": None}
    msg_ef = FakeMessage(pilot)
    await answer_enemy_or_course_photo(msg_ef, enemy_noimg, "Бой без картинки врага")
    check("враг без картинки — входная картинка курса (fallback)",
          sent_photo(msg_ef) == entrance)

    # ── 3. Препятствие: вода/верёвка своими картинками ──
    msg_w = FakeMessage(pilot)
    await answer_obstacle_photo(msg_w, "water", "Вброд")
    check("вода — answer_photo с photo_water", sent_photo(msg_w) == water)

    msg_r = FakeMessage(pilot)
    await answer_obstacle_photo(msg_r, "rope", "Переправа")
    check("верёвка — answer_photo с photo_rope", sent_photo(msg_r) == rope)

    await update_dungeon_photos(dng_id, {"rope": None})
    msg_r2 = FakeMessage(pilot)
    await answer_obstacle_photo(msg_r2, "rope", "Переправа без картинки")
    check("верёвка без своей картинки — вход курса (fallback)",
          sent_photo(msg_r2) == entrance)

    # ── 4. Админ-пикер данжа: слоты вода и верёвка ──
    cb_pick = FakeMessage(admin)
    await _dungeon_photos_pick_send(cb_pick, dng_id)
    callbacks = []
    for kind, a, kw in cb_pick.sent:
        if kind == "answer" and kw.get('reply_markup'):
            callbacks = markup_callbacks(kw['reply_markup'])
    check("пикер данжа предлагает слот Вода",
          "dungeon:photo_set:water" in callbacks)
    check("пикер данжа предлагает слот Верёвка",
          "dungeon:photo_set:rope" in callbacks)
    pick_text = sent_text(cb_pick)
    check("пикер данжа перечисляет заданные слоты",
          "Вода" in pick_text and "Верёвка" in pick_text)

    # ── 5. Штаб ВВС: состав ──
    pid2 = 420011
    pid3 = 420012
    await add_user(pid2, "sova", "Сова", "")
    await add_user(pid3, "ten", "Тень", "")

    # Назначение крыла (право can_manage_wing у админа есть).
    cb_set = FakeCallback(admin, data=f"hq:wing:set:{pid2}:2", message=FakeMessage(admin))
    await hq_wingset(cb_set)
    check("назначение крыла подтверждено", "Крыло пилота" in sent_text(cb_set.message))
    u2 = await get_user(pid2)
    check("крыло пилота сохранено в БД", u2['wing'] == "2")

    # Доступ без права — отказ.
    cb_deny = FakeCallback(pilot, data=f"hq:wing:set:{pid3}:1", message=FakeMessage(pilot))
    await hq_wingset(cb_deny)
    deny_txt = sent_text(cb_deny.message)
    check("без права can_manage_wing — отказ",
          "Нет доступа к составу ВВС" in deny_txt or "Нет доступа" in deny_txt)
    u3 = await get_user(pid3)
    check("отказ не изменил чужое крыло", u3['wing'] is None)

    # Сводка hq:wing.
    cb_wing = FakeCallback(admin, data="hq:wing", message=FakeMessage(admin))
    await hq_wing_cb(cb_wing)
    wing_txt = sent_text(cb_wing.message)
    check("сводка ВВС содержит «Полярные»", "Полярные" in wing_txt or "2 АК" in wing_txt)
    check("сводка считает безкрылых", "Без крыла" in wing_txt)

    # Список пилотов hq:roster — где наш пилот с меткой крыла.
    cb_list = FakeCallback(admin, data="hq:roster:0", message=FakeMessage(admin))
    await hq_roster_pick(cb_list)
    roster_buttons = []
    for kind, a, kw in cb_list.message.sent:
        if kind == "answer" and kw.get('reply_markup'):
            roster_buttons = markup_callbacks(kw['reply_markup'])
    check("в списке пилотов есть наш пилот", f"hq:pilot:{pid2}" in roster_buttons)
    check("кнопка пилота НЕ пересекается с пагинацией hq:roster",
          f"hq:pilot:{pid2}" not in [c for c in roster_buttons if c.startswith("hq:roster:")])
    check("в списке есть счётчик страниц", "hq:noop" in roster_buttons)

    # hq:pilot — экран выбора крыла (после выбора пилота).
    cb_rs = FakeCallback(admin, data=f"hq:pilot:{pid3}", message=FakeMessage(admin))
    await hq_pilot_cb(cb_rs)
    rs_buttons = []
    for kind, a, kw in cb_rs.message.sent:
        if kind == "answer" and kw.get('reply_markup'):
            rs_buttons = markup_callbacks(kw['reply_markup'])
    check("экран выбора крыла содержит три крыла",
          f"hq:wing:set:{pid3}:1" in rs_buttons and f"hq:wing:set:{pid3}:3" in rs_buttons)
    check("экран выбора крыла умеет снять крыло",
          f"hq:wing:set:{pid3}:none" in rs_buttons)

    # Кнопка «Состав ВВС» в меню штаба зависит от права.
    buttons_y = markup_callbacks(hq_menu_markup(True))
    buttons_n = markup_callbacks(hq_menu_markup(False))
    check("с правом — кнопка «Состав ВВС» есть", "hq:wing" in buttons_y)
    check("без права — кнопки «Состав ВВС» нет", "hq:wing" not in buttons_n)

    await close_db()
    print(f"\nSmoke 070: {passed} passed, {failed} failed")
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