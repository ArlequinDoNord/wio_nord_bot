"""Smoke: Архив стены изречений (v0.18.4).

Механика (решение владельца): каждую неделю (пн 10:00 МСК, из суточного цикла)
стена проверяется: если изречений больше одной страницы (WALL_PAGE_SIZE=5) —
всё собирается в архив с периодом от первой до последней записи, стена
очищается. Если меньше или ровно страница — ничего не трогаем, проверка через
неделю; тогда архив одним периодом покроет несколько недель.

Что проверяем:
  • <= 1 страницы + новая неделя — архивации нет, стена не очищена;
  • > 1 страницы (7 записей за две недели) + новая неделя — архив создан,
    стена пуста, период и заголовок по датам/неделям;
  • копии изречений в архиве читаются постранично (как на стене);
  • повторный запуск на той же неделе — ничего не переархивирует.

Запуск: .venv\\Scripts\\python.exe smoke_098.py
"""
import asyncio
import os
import sys

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke098.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB

sys.path.insert(0, os.path.dirname(__file__))


class FakeMessage:
    def __init__(self, chat_id=1):
        self.chat = type("C", (), {"id": chat_id, "type": "private"})()
        self.text = None
        self.photo = None
        self.message_thread_id = None
        self.answers = []
        self.kwargs = []

    async def answer(self, text, **kwargs):
        self.answers.append(text)
        self.kwargs.append(kwargs)

    async def edit_text(self, text, **kwargs):
        self.answers.append(text)
        self.kwargs.append(kwargs)

    async def edit_caption(self, caption, **kwargs):
        self.answers.append(caption)
        self.kwargs.append(kwargs)

    @property
    def last(self):
        return self.answers[-1] if self.answers else ""

    def buttons(self):
        """Все callback_data из последней разметки."""
        markup = self.kwargs[-1].get('reply_markup') if self.kwargs else None
        if not markup:
            return []
        return [b.callback_data for row in markup.inline_keyboard for b in row]


class FakeCallbackQuery:
    def __init__(self, data, user_id):
        self.message = FakeMessage()
        self.data = data
        self.from_user = type("U", (), {"id": user_id})()
        self.answered = False

    async def answer(self, *a, **kw):
        self.answered = True


async def run():
    from database.db import (
        init_db, close_db, add_user, get_db, count_wall_posts,
        count_wall_archives, get_wall_archives, get_wall_archive,
        count_wall_archive_posts, get_wall_archive_posts,
        maybe_archive_wall_weekly, has_library_access,
        WALL_ARCHIVE_WEEK_SETTING_KEY, activate_library_card,
    )
    from bot.handlers.wall import _archive_allowed
    from config import WALL_PAGE_SIZE

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

    UID = 98001   # пилот-автор изречений
    VIEW = 98002  # посетитель архива (без билета)
    TICK = 98003  # владелец читательского билета
    await add_user(UID, "pilot", "Пилот", "")
    await add_user(VIEW, "viewer", "Зевака", "")
    await add_user(TICK, "reader", "Читатель", "")
    await activate_library_card(TICK, "basic", days=30)

    async def force_new_week():
        conn = await get_db()
        await conn.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (WALL_ARCHIVE_WEEK_SETTING_KEY, "2000-W00"))
        await conn.commit()

    async def add_post_raw(text, day):
        conn = await get_db()
        await conn.execute(
            "INSERT INTO wall_posts (user_id, text, created_day, tier, cost) "
            "VALUES (?, ?, ?, 0, 0)",
            (UID, text, day))
        await conn.commit()

    # ── 1. Доступ к архиву ──
    check("билет даёт доступ", await _archive_allowed(TICK) is True)
    check("без билета — нет доступа", await _archive_allowed(VIEW) is False)
    check("has_library_access у читателя", await has_library_access(TICK) is True)

    # ── 2. Меньше страницы — архивации нет, стена не очищается ──
    for i in range(3):
        await add_post_raw(f"Запись {i}", "2026-09-07")
    await force_new_week()
    res = await maybe_archive_wall_weekly()
    check("<= стр.: архивации нет", res is not None and res['archived'] is False)
    check("<= стр.: стена не очищена", await count_wall_posts() == 3)
    check("<= стр.: архив пуст", await count_wall_archives() == 0)

    # ── 3. Больше страницы за несколько недель — архив с периодом по датам ──
    for i in range(2):
        await add_post_raw(f"Поздняя {i}", "2026-09-21")   # 5 записей за неделю 37
    await add_post_raw("Пик", "2026-09-28")                 # 6-я — уже больше страницы
    await add_post_raw("Послед.", "2026-09-29")
    await force_new_week()
    res = await maybe_archive_wall_weekly()
    check("> стр.: архивация прошла", res is not None and res['archived'] is True)
    check("> стр.: заархивировано 7", res is not None and res['count'] == 7)
    check("> стр.: стена очищена", await count_wall_posts() == 0)
    check("архив содержит запись", await count_wall_archives() == 1)

    arch = (await get_wall_archives())[0]
    check("заголовок — период по датам (не одна неделя)",
          "09 — 29.09" in arch['title'] or "07.09 — 29.09" in arch['title'])
    check("период записан от первой до последней записи",
          arch['period_start'] == "2026-09-07" and arch['period_end'] == "2026-09-29")
    check("post_count совпадает", arch['post_count'] == 7)

    full = await get_wall_archive(arch['id'])
    check("get_wall_archive читает запись", full is not None and full['title'] == arch['title'])
    check("число изречений в архиве", await count_wall_archive_posts(arch['id']) == 7)

    # ── 4. Постраничное чтение копий ──
    p0 = await get_wall_archive_posts(arch['id'], 0, WALL_PAGE_SIZE)
    p1 = await get_wall_archive_posts(arch['id'], 1, WALL_PAGE_SIZE)
    check("первая страница полная", len(p0) == WALL_PAGE_SIZE)
    check("на второй странице остаток", len(p1) == 7 - WALL_PAGE_SIZE)
    check("копия хранит текст", any("Послед." in r['text'] for r in p0))

    # ── 5. Идемпотентность недели: повторный вызов в ту же неделю ──
    res2 = await maybe_archive_wall_weekly()
    check("на той же неделе не переархивирует", res2 is None)
    check("archive всё ещё один", await count_wall_archives() == 1)

    await close_db()
    print(f"\nSmoke 098: {passed} passed, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    async def _main():
        try:
            return await run()
        finally:
            from database.db import close_db
            await close_db()

    sys.exit(asyncio.run(_main()))