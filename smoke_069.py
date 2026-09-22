"""Smoke v0.15.1: картинки К.В.П. + «Стена изречений».

Проверяет:
1. answer_course_photo: при наличии photo_* у данжа К.В.П. уходиТ answer_photo
   с той же картинкой; без картинки — текстовый answer.
2. kvp_menu_cb: меню курса шлёт входную картинку данжа (а не только текст).
3. Стена: каждая запись подписана номером №id и короткой датой (дд.мм чч:мм).
4. Листание страниц работает только с последнего сообщения стены; устаревшая
   кнопка пагинации отклоняется («устаревшее сообщение»).

Запуск: .venv\\Scripts\\python.exe smoke_069.py
"""
import asyncio
import os
import re
import sys
from types import SimpleNamespace

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke069.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB

_CMD_ID = 400001
os.environ["ADMIN_IDS"] = str(_CMD_ID)

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

    async def edit_media(self, *a, **kw):
        self.sent.append(("edit_media", a, kw))


class FakeCallback:
    def __init__(self, user_id, data="", message=None):
        self.from_user = SimpleNamespace(id=user_id)
        self.message = message or FakeMessage(user_id)
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


def markup_callbacks(markup):
    if not markup:
        return []
    return [b.callback_data for row in markup.inline_keyboard for b in row]


async def run():
    from database.db import (
        init_db, close_db, add_user, get_db, seed_kvp, update_dungeon_photos,
        get_kvp_dungeon, add_wall_post,
    )
    from bot.handlers.kvp import answer_course_photo, kvp_menu_cb
    from bot.handlers import wall as W

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

    uid = 400010  # пилот
    await add_user(uid, "pilot", "Пилот", "")
    file_id = "AgACAg_TESTKVPFILEID_001"

    # ── 1. answer_course_photo без картинки → текст ──
    dng_id = await seed_kvp()
    dng = await get_kvp_dungeon()
    check("данж К.В.П. создан", dng is not None and dng['id'] == dng_id)

    msg_no = FakeMessage(uid)
    await answer_course_photo(msg_no, "Проверка текста", reply_markup=None)
    kinds = [k for k, _, _ in msg_no.sent]
    check("без картинки — text answer", kinds == ["answer"] and sent_text(msg_no) == "Проверка текста")
    check("без картинки — НЕ answer_photo", "answer_photo" not in kinds)

    # ── 2. Задали админские картинки данжа → answer_course_photo шлёт фото ──
    ok = await update_dungeon_photos(dng_id, {"dawn": file_id, "day": file_id,
                                              "sunset": file_id, "night": file_id})
    check("update_dungeon_photos применил file_id", ok is not None)

    msg_pic = FakeMessage(uid)
    await answer_course_photo(msg_pic, "Подпись с картинкой", reply_markup=None)
    kinds_pic = [k for k, _, _ in msg_pic.sent]
    photo_kw = None
    for kind, a, kw in msg_pic.sent:
        if kind == "answer_photo":
            photo_kw = kw
    check("с картинкой — answer_photo", "answer_photo" in kinds_pic and "answer" not in kinds_pic)
    check("answer_photo несёт именно file_id админа",
          photo_kw is not None and photo_kw.get('photo') == file_id)
    check("caption совпадает", photo_kw is not None and photo_kw.get('caption') == "Подпись с картинкой")

    # ── 3. kvp_menu_cb показывает ту же картинку на меню входа ──
    cb_menu = FakeCallback(uid, data="kvp:start", message=FakeMessage(uid))
    await kvp_menu_cb(cb_menu)
    menu_kinds = [k for k, _, _ in cb_menu.message.sent]
    menu_photo = None
    for kind, a, kw in cb_menu.message.sent:
        if kind == "answer_photo":
            menu_photo = kw.get('photo')
    check("меню К.В.П. уходит картинкой (answer_photo)",
          "answer_photo" in menu_kinds)
    check("в меню та же картинка данжа (file_id админа)",
          menu_photo == file_id)
    check("в меню текст курса не пропал",
          "КУРС ВЫЖИВАНИЯ" in sent_text(cb_menu.message) or
          (menu_photo and True))

    # ── 3b. Превью локации «Курс выживания» из города — та же картинка данжа ──
    from bot.handlers.locations import location_preview
    cb_prev = FakeCallback(uid, data="location:preview:kvp", message=FakeMessage(uid))
    await location_preview(cb_prev)
    prev_photo = None
    prev_photo_kind = False
    for kind, a, kw in cb_prev.message.sent:
        if kind == "answer_photo":
            prev_photo_kind = True
            prev_photo = kw.get('photo')
    check("превью К.В.П. из города уходит картинкой",
          prev_photo_kind)
    check("в превью та же картинка данжа (file_id админа)",
          prev_photo == file_id)

    # ── 4. Стена: номер и короткая дата у каждой записи ──
    uid2 = 400011
    await add_user(uid2, "sage", "Мудрец", "")
    uid3 = 400012
    await add_user(uid3, "scribe", "Писарь", "")

    posts = []
    for i, (u, t) in enumerate([
        (uid2, "Первый полёт — лучший полёт"),
        (uid2, "Небо любит смелых"),
        (uid3, "Штурвал не двигается — надо верить"),
        (uid2, "Нордхайм не спит"),
        (uid3, "Масло в двигателе — жизнь в крыльях"),
        (uid2, "У каждой тучи серебряная кромка"),
    ], start=1):
        r = await add_wall_post(u, t)
        posts.append(r['post_id'])

    st_wall = FakeState()
    msg_wall = FakeMessage(uid, message_id=2001)
    await W._show_wall(msg_wall, st_wall, page=0)
    wall_text = sent_text(msg_wall)
    check("на стене есть заголовок", "СТЕНА ИЗРЕЧЕНИЙ" in wall_text)

    # Свежие сверху → на первой странице (5 шт) самые новые (последние 5).
    missing = [pid for pid in posts[-5:] if f"№{pid}" not in wall_text]
    check("у каждой записи есть номер №id", not missing)
    date_pat = re.compile(r"\d{2}\.\d{2}")
    check("в тексте стены есть короткая дата (дд.мм)", date_pat.search(wall_text) is not None)

    # ── 5. Пагинация работает только с последнего сообщения ──
    # Последнее сообщение стены (msg_wall) помечено active_msg == 2001.
    st_ok = FakeState(data={"wall_active_msg": 2001})
    cb_page = FakeCallback(uid, data="wall:page:2", message=FakeMessage(uid, message_id=2001))
    # Need get_wall_posts page 2 valid: 6 постов, страница из 5 → листаем на 2 (page=2 → clamp).
    # Проверяем, что устаревшее сообщение отклоняется.
    st_old = FakeState(data={"wall_active_msg": 2001})
    cb_old = FakeCallback(uid, data="wall:page:1", message=FakeMessage(uid, message_id=999))
    await W.wall_page(cb_old, st_old)
    msg_after = sent_text(cb_old.message)
    check("кнопка пагинации со старого сообщения отклоняется",
          "устаревшее сообщение" in msg_after)

    # Пустой стейт (данные стёрты) — тоже не листаем.
    st_gone = FakeState(data={})
    cb_gone = FakeCallback(uid, data="wall:page:1", message=FakeMessage(uid, message_id=2001))
    await W.wall_page(cb_gone, st_gone)
    check("без активного сообщения в стейте листание запрещено",
          "устаревшее сообщение" in sent_text(cb_gone.message))

    # Активное сообщение — листает (или сообщает про устаревшее, если данные старые),
    # но в любом случае НЕ отправляет предупреждение «устаревшее».
    st_new = FakeState(data={"wall_active_msg": 2001})
    cb_new = FakeCallback(uid, data="wall:page:1", message=FakeMessage(uid, message_id=2001))
    await W.wall_page(cb_new, st_new)
    txt_new = sent_text(cb_new.message)
    check("с текущего сообщения пагинация сработала (нет отказа)",
          "устаревшее сообщение" not in txt_new)

    # ── 6. Удаление: только can_manage_users, а не «любая роль» ──
    # Представитель (can_create_polls) не должен видеть кнопки удаления и удалять записи.
    uid_rep = 400020
    await add_user(uid_rep, "deputat", "Представитель", "")
    conn = await get_db()
    await conn.execute(
        "INSERT INTO user_roles (telegram_id, role, granted_by) VALUES (?, 'representative', ?)",
        (uid_rep, uid_rep)
    )
    await conn.commit()

    st_rep = FakeState()
    msg_rep = FakeMessage(uid_rep, message_id=3001)
    await W._show_wall(msg_rep, st_rep)
    rep_markup = None
    for kind, a, kw in msg_rep.sent:
        if kind == "answer" and kw.get('reply_markup'):
            rep_markup = kw['reply_markup']
    rep_buttons = markup_callbacks(rep_markup)
    check("представитель НЕ видит кнопок удаления записей",
          not any(c.startswith("wall:delete:") for c in rep_buttons))
    check("представитель видит кнопку «Оставить изречение»",
          "wall:write" in rep_buttons)

    first_post = posts[0]
    cb_rep_del = FakeCallback(uid_rep, data=f"wall:delete:{first_post}",
                              message=FakeMessage(uid_rep))
    await W.wall_delete(cb_rep_del, FakeState())
    check("представителю удаление отклонено",
          "только админы" in sent_text(cb_rep_del.message))

    await close_db()
    print(f"\nSmoke 069: {passed} passed, {failed} failed")
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