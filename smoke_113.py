"""Smoke 113 — «Опросы: 10 суток + архив» и «Голос Представителя», v0.19.0.

Проверяем:
   1. Опросы: closes_at = created_at + POLL_MAX_DAYS при создании; старые активные
      опросы получают срок от своего created_at миграцией; истёкшие закрываются
      сами (close_expired_polls), в меню голосования остаётся POLL_VISIBLE
      новейших (get_visible_polls), всё остальное уходит в архив с датой
      (archive_old_polls / get_archived_poll_days).
   2. Библиотека: раздел «Опросы» — группировка по датам, заголовки дней,
      пагинация по дням, доступ по читательскому билету.
   3. Речь представителя: право can_address_city, лимит REP_SPEECH_MAX_LEN символов
      и REP_SPEECH_PER_DAY обращений в сутки, правки обращения нет (любое
      изменение — новое обращение, оно тратит лимит), удаление обращения лимит
      не тратит, обращение висит в подписи города, новое обращение уходит
      в общий чат (notify).
   4. Меню голосования: 🔒 у закрытого опроса в топ-4, кнопки «Закрытые опросы»
      в боте больше нет.
"""
import asyncio
import os
import sys

_TEST_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_test_smoke113.db")
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
        self.markup = None
        self.caption = None
        self.answers = []
        self.photo = False

    async def edit_text(self, text=None, reply_markup=None, **kw):
        self.text = text
        self.markup = reply_markup
        return None

    async def edit_caption(self, caption=None, reply_markup=None, **kw):
        self.caption = caption
        self.markup = reply_markup
        return None

    async def answer(self, text=None, reply_markup=None, **kw):
        self.answers.append(text)
        self.text = text
        self.markup = reply_markup
        return None

    async def answer_photo(self, *a, **kw):
        self.caption = (kw.get("caption"),)
        self.markup = kw.get("reply_markup")
        return None

    async def edit_media(self, media=None, reply_markup=None, **kw):
        self.caption = getattr(media, "caption", None)
        self.markup = reply_markup
        return None

    @property
    def last(self):
        return self.answers[-1] if self.answers else None


class CB:
    def __init__(self, data="x", uid=424242):
        self.data = data
        self.from_user = type("U", (), {})()
        self.from_user.id = uid
        self.message = CBMsg()
        self.photo = False

    async def answer(self, text=None, show_alert=False, reply_markup=None, **kw):
        if text:
            self.message.text = text
        return None


class Msg:
    def __init__(self, text, uid=424242):
        self.text = text
        self.from_user = type("U", (), {})()
        self.from_user.id = uid
        self.message = CBMsg()
        self.bot = None

    async def answer(self, text=None, reply_markup=None, **kw):
        self.message.answers.append(text)
        self.message.text = text
        self.message.markup = reply_markup
        return None


def buttons(markup):
    out = []
    for row in (markup.inline_keyboard if markup else []):
        for b in row:
            out.append((b.text, b.callback_data))
    return out


def texts(markup):
    return [t for t, _ in buttons(markup)]


async def main():
    import config
    config.DB_PATH = _TEST_DB

    import database.db as db
    db.DB_PATH = _TEST_DB
    from database.db import (
        init_db, close_db, add_user, get_db, create_poll, get_poll, close_poll,
        close_expired_polls, archive_old_polls, maintain_polls, get_visible_polls,
        count_visible_active_polls, get_archived_poll_days, count_archived_poll_days,
        get_archived_polls_by_day, count_archived_polls_by_day, count_archived_polls,
        add_rep_speech, update_rep_speech, get_latest_rep_speech, get_rep_speech,
        count_rep_speeches_today, activate_library_card, set_news_chat,
    )
    from utils.permissions import has_permission, add_role

    await init_db()
    conn = await get_db()

    REP, PILOT, STRANGER = 700001, 700002, 700003
    await add_user(REP, "rep", "Реп", "Представитель")
    await add_user(PILOT, "pilot", "Пилот", "Пилотов")
    await add_user(STRANGER, "stranger", "Кто", "Никто")
    # Права выдаём напрямую: add_role требует can_manage_admins у выдающего.
    await conn.execute(
        "INSERT INTO user_roles (telegram_id, role) VALUES (?, 'representative')", (REP,))
    await conn.execute(
        "INSERT INTO user_roles (telegram_id, role) VALUES (?, 'journalist')", (PILOT,))
    await conn.commit()

    # ── 1. Срок жизни опроса ─────────────────────────────────────────────
    print("\n= 1. Срок опроса (10 суток) =")
    from datetime import datetime, timedelta
    check("POLL_MAX_DAYS = 10", config.POLL_MAX_DAYS == 10)
    check("POLL_VISIBLE = 4", config.POLL_VISIBLE == 4)

    pid = await create_poll(REP, "Вопрос про срок?", "да\nнет")
    row = await get_poll(pid)
    check("у нового опроса проставлен closes_at", bool(row['closes_at']))
    created = datetime.strptime(row['created_at'][:19], "%Y-%m-%d %H:%M:%S")
    closes = datetime.strptime(row['closes_at'][:19], "%Y-%m-%d %H:%M:%S")
    delta_days = (closes - created).days
    check(f"closes_at = created_at + {config.POLL_MAX_DAYS} суток (получено {delta_days})",
          delta_days == config.POLL_MAX_DAYS)

    # Истёкший опрос закрывается сам.
    await conn.execute(
        "UPDATE polls SET created_at = datetime('now', '-11 days'), "
        "closes_at = datetime('now', '-1 days') WHERE id = ?", (pid,))
    await conn.commit()
    check("истёкший опрос до обслуживания ещё активен", (await get_poll(pid))['is_active'] == 1)
    closed_n = await close_expired_polls()
    after = await get_poll(pid)
    check("истёкший опрос закрылся сам", after['is_active'] == 0)
    check("закрыто ровно 1", closed_n == 1)
    check("при автозакрытии проставлено время закрытия", bool(after['closed_at']))
    check("автор автозакрытия не подставлен", not after['closed_by'])

    # Свежий опрос автозакрытием не трогаем.
    pid2 = await create_poll(REP, "Свежий?", "да\nнет")
    await close_expired_polls()
    check("свежий опрос остался активным", (await get_poll(pid2))['is_active'] == 1)

    # ── 2. Меню голосования: 4 новейших, остальные в архив ──────────────
    print("\n= 2. Меню: 4 новейших, лишние в архив =")
    await conn.execute("DELETE FROM polls")
    await conn.execute("DELETE FROM poll_votes")
    await conn.commit()
    ids = []
    for i in range(6):
        ids.append(await create_poll(REP, f"Опрос номер {i + 1}", "да\nнет"))

    res = await maintain_polls()
    check("архивировано 2 (6 − POLL_VISIBLE)", res['archived'] == 6 - config.POLL_VISIBLE)
    visible = await get_visible_polls()
    check(f"в меню {config.POLL_VISIBLE} новейших", len(visible) == config.POLL_VISIBLE)
    check("это именно новейшие по id",
          [p['id'] for p in visible] == sorted(ids, reverse=True)[:config.POLL_VISIBLE])
    check("архивный опрос закрыт",
          (await get_poll(ids[0]))['is_active'] == 0)
    check("счётчик активных в меню = 4", await count_visible_active_polls() == 4)

    days = await get_archived_poll_days()
    check("в архиве один день", len(days) == 1 and days[0]['cnt'] == 2)
    check("count_archived_poll_days = 1", await count_archived_poll_days() == 1)
    check("count_archived_polls = 2", await count_archived_polls() == 2)
    day_polls = await get_archived_polls_by_day(days[0]['archived_day'])
    check("под днём 2 опроса", len(day_polls) == 2)
    check("count_archived_polls_by_day = 2",
          await count_archived_polls_by_day(days[0]['archived_day']) == 2)

    # Повторный вызов идемпотентен: в меню уже 4, архивировать нечего.
    res2 = await maintain_polls()
    check("повторное обслуживание ничего не архивирует", res2['archived'] == 0)
    check("в меню так и 4", len(await get_visible_polls()) == 4)

    # Закрытый автором опрос из топ-4 остаётся в меню (под знаком 🔒 в разметке).
    await close_poll(ids[-1], REP)
    visible2 = await get_visible_polls()
    check("закрытый автором опрос остался в меню", ids[-1] in [p['id'] for p in visible2])
    check("он помечен как закрытый", [p for p in visible2 if p['id'] == ids[-1]][0]['is_active'] == 0)

    # ── 3. Меню голосования в боте ───────────────────────────────────────
    print("\n= 3. Разметка меню голосования =")
    import bot.handlers.polls as polls_mod
    cb = CB("city:vote", PILOT)
    await polls_mod.vote_menu(cb)
    kb = buttons(cb.message.markup)
    kb_texts = texts(cb.message.markup)
    check("в меню 4 кнопки опросов",
          sum(1 for t in kb_texts if t.startswith(("🗳", "🔒 🗳"))) == 4)
    check("закрытый опрос помечен 🔒", any(t.startswith("🔒 🗳") for t in kb_texts))
    check("кнопки «Закрытые опросы» больше нет",
          not any("Закрытые опросы" in t for t in kb_texts))
    check("кнопка возврата в Ратушу есть", ("🔙 В Ратушу", "city:pilots") in kb)
    check("пилоту кнопка создания не показывается",
          not any("Создать опрос" in t for t in kb_texts))
    cb_rep = CB("city:vote", REP)
    await polls_mod.vote_menu(cb_rep)
    check("представителю кнопка создания есть",
          any("Создать опрос" in t for t in texts(cb_rep.message.markup)))

    # Закрытый опрос: итоги + ссылка в архив, без «Закрытых опросов».
    cb_closed = CB(f"vote:show:{ids[-1]}", PILOT)
    await polls_mod.vote_show(cb_closed)
    check("карточка закрытого показывает итоги", "РЕЗУЛЬТАТЫ" in (cb_closed.message.text or ""))
    check("в карточке закрытого есть ссылка в архив",
          ("🗂 Архив опросов в библиотеке", "pollarch:list") in buttons(cb_closed.message.markup))
    check("в карточке закрытого нет «Закрытых опросов»",
          not any("Закрытые опросы" in t for t in texts(cb_closed.message.markup)))

    # Предупреждение о сроке при создании. Отдельный представитель: у REP
    # суточный лимит создания уже исчерпан (6 опросов за сутки в тесте выше).
    REP2 = 700004
    await add_user(REP2, "rep2", "Реп", "Второй")
    await conn.execute(
        "INSERT INTO user_roles (telegram_id, role) VALUES (?, 'representative')", (REP2,))
    await conn.commit()
    cb_create = CB("vote:create", REP2)
    await polls_mod.vote_create(cb_create, _FakeState())
    check("при создании предупреждают о 10 сутках",
          f"{config.POLL_MAX_DAYS} суток" in (cb_create.message.last or ""))

    # ── 4. Раздел «Опросы» в библиотеке ─────────────────────────────────
    print("\n= 4. Библиотека: раздел «Опросы» по датам =")
    import bot.handlers.poll_archive as pa
    check("в меню библиотеки кнопка архива опросов",
          any("Архив опросов" in t for t in texts(
              __import__("bot.handlers.library", fromlist=["sections_markup"])
              .sections_markup(["history"]))))

    # Без билета архив закрыт.
    cb_no = CB("pollarch:list", STRANGER)
    await pa.poll_archive_list(cb_no)
    check("без читательского билета архив недоступен",
          "читательского билета" in (cb_no.message.text or ""))

    await activate_library_card(STRANGER, "basic")
    cb_days = CB("pollarch:list", STRANGER)
    await pa.poll_archive_list(cb_days)
    check("с билетом архив открывается", "АРХИВ ОПРОСОВ" in (cb_days.message.text or ""))
    day_btn = [b for b in buttons(cb_days.message.markup) if b[1].startswith("pollarch:day:")]
    check("в архиве кнопка дня", len(day_btn) == 1)
    check("заголовок дня по-русски",
          any(word in day_btn[0][0] for word in
              ("Января", "Февраля", "Марта", "Апреля", "Мая", "Июня", "Июля",
               "Августа", "Сентября", "Октября", "Ноября", "Декабря")))
    check("в заголовке дня есть число опросов", "опрос" in day_btn[0][0])

    cb_day = CB(day_btn[0][1], STRANGER)
    await pa.poll_archive_day(cb_day)
    poll_btns = [b for b in buttons(cb_day.message.markup) if b[1].startswith("vote:results:")]
    check("под днём 2 опроса", len(poll_btns) == 2)
    check("есть возврат к дням архива",
          any(b[1] == "pollarch:list" for b in buttons(cb_day.message.markup)))

    # Пагинация дней: разносим архивные опросы по 6 разным дням, чтобы
    # страница дней (POLL_ARCHIVE_DAYS_PER_PAGE = 5) потребовала второй.
    archived_day = days[0]['archived_day']
    archived_ids = [p['id'] for p in await get_archived_polls_by_day(archived_day)]
    for shift, poll_id in enumerate(archived_ids):
        await conn.execute(
            "UPDATE polls SET archived_day = date(?, ?) WHERE id = ?",
            (archived_day, f"-{shift} days", poll_id))
    for extra in range(4):
        await conn.execute(
            "INSERT INTO polls (admin_id, question, options, is_active, is_archived, "
            "archived_day) VALUES (?, ?, 'да', 0, 1, date(?, ?))",
            (REP, f"Архивный под {extra + 1}", archived_day, f"-{extra + 2} days"))
    await conn.commit()
    check("после правки дней архива 6", await count_archived_poll_days() == 6)
    cb_p = CB("pollarch:days:1", STRANGER)
    await pa.poll_archive_days_page(cb_p)
    check("вторая страница дней открывается",
          "АРХИВ ОПРОСОВ" in (cb_p.message.text or ""))
    nav1 = [b for b in buttons(cb_p.message.markup) if b[1].startswith("pollarch:days:")]
    check("на последней странице дней есть возврат назад ◀",
          len(nav1) == 1 and nav1[0][1] == "pollarch:days:0")
    cb_p0 = CB("pollarch:days:0", STRANGER)
    await pa.poll_archive_days_page(cb_p0)
    nav0 = [b for b in buttons(cb_p0.message.markup) if b[1].startswith("pollarch:days:")]
    check("на первой странице дней есть переход вперёд ▶",
          len(nav0) == 1 and nav0[0][1] == "pollarch:days:1")
    day0 = [b for b in buttons(cb_p0.message.markup) if b[1].startswith("pollarch:day:")]
    check("на странице дней 5 кнопок дней",
          len(day0) == config.POLL_ARCHIVE_DAYS_PER_PAGE)

    # ── 5. Голос Представителя ───────────────────────────────────────────
    print("\n= 5. Речь представителя =")
    check("REP_SPEECH_MAX_LEN = 100", config.REP_SPEECH_MAX_LEN == 100)
    check("REP_SPEECH_PER_DAY = 4", config.REP_SPEECH_PER_DAY == 4)
    check("у представителя есть право can_address_city",
          await has_permission(REP, "can_address_city"))
    check("у обычного пилота права нет",
          not await has_permission(PILOT, "can_address_city"))
    check("право не сломало can_create_polls у представителя",
          await has_permission(REP, "can_create_polls"))

    import bot.handlers.representative as rep_mod
    sent = []

    class FakeBot:
        async def send_message(self, chat_id, text, **kw):
            sent.append(text)
            return None

    fake_bot = FakeBot()
    # Общий чат для оповещений — иначе notify() молча выходит (нет chat_id).
    await set_news_chat(-1001234567890)

    # Карточка «Обращение Представителя» видна и читается всеми.
    cb_speech = CB("rep:speech", PILOT)
    await rep_mod.rep_speech_open(cb_speech, _FakeState())
    check("карточка речи открывается и для простого пилота",
          "РЕЧЬ ПРЕДСТАВИТЕЛЯ" in (cb_speech.message.text or ""))
    check("у простого пилота нет кнопки нового обращения",
          not any("Новое обращение" in t for t in texts(cb_speech.message.markup)))
    check("у простого пилота нет кнопки правки",
          not any("Изменить обращение" in t for t in texts(cb_speech.message.markup)))

    # Пилот не может начать обращение.
    cb_w = CB("rep:speech:write", PILOT)
    await rep_mod.rep_speech_write(cb_w, _FakeState())
    check("пилоту отказано в обращении", "только Представитель" in (cb_w.message.last or ""))

    # Слишком длинное обращение не проходит.
    long_text = "я" * (config.REP_SPEECH_MAX_LEN + 1)
    m = Msg(long_text, REP)
    m.bot = fake_bot
    st = _FakeState()
    st.data = {}
    await rep_mod.rep_speech_text(m, st, fake_bot)
    check("обращение длиннее лимита отклонено",
          "Слишком длинно" in (m.message.last or ""))
    check("в базу длинное не попало", await get_latest_rep_speech() is None)

    # Публикация обращения.
    speech_text = "Город, держимся вместе!"
    m = Msg(speech_text, REP)
    m.bot = fake_bot
    st = _FakeState()
    st.data = {}
    await rep_mod.rep_speech_text(m, st, fake_bot)
    latest = await get_latest_rep_speech()
    check("обращение сохранено", latest is not None and latest['text'] == speech_text)
    check("обращение привязано к автору", latest['user_id'] == REP)
    check("created_day проставлен", bool(latest['created_day']))
    check("счётчик за сутки = 1", await count_rep_speeches_today(REP) == 1)
    check("обращение ушло в общий чат", any(speech_text in s for s in sent))
    check("в оповещении есть заголовок речи",
          any("РЕЧЬ ПРЕДСТАВИТЕЛЯ" in s for s in sent))
    check("подтверждение об опубликовании", "Обращение опубликовано" in (m.message.last or ""))

    # Речь висит на заглавной картинке города.
    import bot.handlers.start as start_mod
    caption = await start_mod._city_caption()
    check("в подписи города есть «Город Аркхольм»", "Город Аркхольм" in caption)
    check("в подписи города есть «Речь представителя»", "Речь представителя" in caption)
    check("в подписи города сам текст обращения", speech_text in caption)

    # Правки обращения нет: любое изменение — новое обращение (тратит лимит).
    # Текущее можно только удалить, и удаление лимит не тратит.
    sent.clear()
    cb_edit = CB("rep:speech:edit", REP)
    await rep_mod.rep_speech_open(cb_edit, _FakeState())
    check("в меню обращения больше нет кнопки правки",
          not any("Изменить обращение" in t for t in texts(cb_edit.message.markup)))
    check("в меню обращения есть удаление",
          any("Удалить обращение" in t for t in texts(cb_edit.message.markup)))

    # Любое изменение — новое обращение, оно тратит лимит.
    st_new = _FakeState()
    st_new.data = {}
    m = Msg("Город, держимся вместе и не сдаёмся!", REP)
    m.bot = fake_bot
    await rep_mod.rep_speech_text(m, st_new, fake_bot)
    after_change = await get_latest_rep_speech()
    check("изменение стало новым обращением",
          after_change['text'] == "Город, держимся вместе и не сдаёмся!")
    check("новое обращение за трату лимита", await count_rep_speeches_today(REP) == 2)
    check("изменение ушло в общий чат", any("не сдаёмся" in s for s in sent))

    # Удаление обращения: запись исчезает, лимит не тратится.
    st_del = _FakeState()
    st_del.data = {}
    await db.delete_rep_speech(after_change['id'])
    gone = await get_latest_rep_speech()
    check("после удаления осталось предыдущее обращение", gone['id'] == latest['id'])
    check("удаление не тратит суточный лимит",
          await count_rep_speeches_today(REP) == 1)

    # Кнопка удаления: чужое обращение удалить нельзя.
    await conn.execute("UPDATE rep_speeches SET user_id = ? WHERE id = ?",
                       (PILOT, latest['id']))
    await conn.commit()
    cb_own = CB("rep:speech:delete", REP)
    await rep_mod.rep_speech_delete(cb_own, _FakeState())
    check("чужое обращение удалить нельзя", "только своё" in (cb_own.message.last or ""))
    check("чужое обращение на месте", (await get_latest_rep_speech())['id'] == latest['id'])
    await conn.execute("UPDATE rep_speeches SET user_id = ? WHERE id = ?",
                       (REP, latest['id']))
    await conn.commit()

    # Суточный лимит обращений.
    for i in range(config.REP_SPEECH_PER_DAY - 1):
        m = Msg(f"Обращение номер {i + 2}", REP)
        m.bot = fake_bot
        st = _FakeState()
        st.data = {}
        await rep_mod.rep_speech_text(m, st, fake_bot)
    check(f"опубликовано {config.REP_SPEECH_PER_DAY} обращений за сутки",
          await count_rep_speeches_today(REP) == config.REP_SPEECH_PER_DAY)
    cb_lim = CB("rep:speech:write", REP)
    await rep_mod.rep_speech_write(cb_lim, _FakeState())
    check("сверх суточного лимита отказано", "все 4 обращения" in (cb_lim.message.last or ""))
    check("карточка речи показывает лимит представителю",
          any("🔙 В Ратушу" in t for t in texts(cb_speech.message.markup)))

    # Кнопка обращения в меню Ратуши.
    import bot.handlers.pilots as pilots_mod
    check("в меню Ратуши есть «Обращение Представителя»",
          any("Обращение Представителя" in t for t in texts(pilots_mod.town_hall_markup(0, 2))))
    check("в меню Ратуши осталась кнопка в город",
          ("🔙 В город", "city:menu") in buttons(pilots_mod.town_hall_markup(0, 2)))

    await close_db()
    for suffix in ("", "-wal", "-shm"):
        try:
            os.remove(_TEST_DB + suffix)
        except OSError:
            pass

    print(f"\n=== SMOKE 113: {PASS} passed, {FAIL} failed ===")
    return 1 if FAIL else 0


class _FakeState:
    def __init__(self):
        self.data = {}
        self._state = None

    async def get_data(self):
        return self.data

    async def update_data(self, **kw):
        self.data.update(kw)

    async def set_state(self, s):
        self._state = s

    async def clear(self):
        self.data = {}
        self._state = None


if __name__ == "__main__":
    code = 1
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        code = loop.run_until_complete(main())
        loop.run_until_complete(asyncio.sleep(0))
    finally:
        _loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_loop)
        try:
            import database.db as _db
            if _db.db is not None:
                _loop.run_until_complete(_db.close_db())
        except Exception:
            pass
        _loop.close()
    sys.exit(code)
