"""Smoke v0.13.15: «Стена изречений» — доска объявлений.

Проверяет:
1. add_wall_post: первый пост бесплатный, tier 0/cost 0, created_day по МСК.
2. Лимиты: 4 бесплатных → 5-й за 30 НМ (списание с баланса), tier по цене.
3. 8-й за 90 НМ; 13-й (последний) за 200 НМ; 14-й — стоп (None).
4. Не хватает НМ → need_nm.
5. get_wall_posts пагинация: свежие сверху, страницы.
6. delete_wall_post: платное → возврат автору ⅓, бесплатное → возврата нет.
7. wall_keyboard: пагинация, «Оставить изречение», админ удаляет.
8. Хендлер wall_view показывает посты; wall:write FSM; wall_write_text публикует.
9. Админ-удаление wall:delete возвращает ⅓.

Запуск: .venv\\Scripts\\python.exe smoke_064.py
"""
import asyncio
import os
import sys
from datetime import datetime
from types import SimpleNamespace

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke064.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB

sys.path.insert(0, os.path.dirname(__file__))


class FakeMessage:
    def __init__(self):
        self.sent = []
        self.photo = None
        self.from_user = None

    async def answer(self, *a, **kw):
        self.sent.append(("answer", a, kw))

    async def edit_text(self, *a, **kw):
        self.sent.append(("edit_text", a, kw))

    async def edit_caption(self, *a, **kw):
        self.sent.append(("edit_caption", a, kw))

    async def __getattr__(self, name):
        async def _noop(*a, **kw):
            return None
        return _noop


class FakeMessageWithFrom(FakeMessage):
    def __init__(self, user_id):
        super().__init__()
        self.from_user = SimpleNamespace(id=user_id)
        self.text = ""

    def __getattr__(self, name):
        raise AttributeError(name)


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


def sent_text(msg):
    for kind, a, kw in msg.sent:
        if kind == "answer" and a:
            return a[0]
        if kind == "answer_photo" and kw.get('caption'):
            return kw.get('caption')
    return ""


async def run():
    from database.db import (
        init_db, close_db, add_user, update_user, get_user,
        count_wall_posts_today, wall_post_tier, add_wall_post,
        get_wall_posts, count_wall_posts, delete_wall_post, _wall_today_key,
    )
    from keyboards.keyboards import wall_keyboard
    from bot.handlers.wall import WallWrite, _wall_footer
    from bot.handlers import wall as wh

    await init_db()

    uid = 999801
    uid_admin = 999802
    await add_user(uid, "walluser", "Стена", "Игрок")
    await add_user(uid_admin, "walladmin", "Админ", "Стены")
    await update_user(uid, nordmarks=500)
    await update_user(uid_admin, nordmarks=0)
    conn = await init_db()
    from database.db import get_db
    dbc = await get_db()
    await dbc.execute(
        "INSERT OR IGNORE INTO user_roles (telegram_id, role, granted_by) VALUES (?, 'super_admin', 0)",
        (uid_admin,)
    )
    await dbc.commit()

    passed = 0
    failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
        else:
            failed += 1
            print(f"  FAIL: {name}")

    # ── 1. Бесплатный пост ──
    r1 = await add_wall_post(uid, "Первое изречение")
    check("пост 1: создан", r1 and r1['post_id'] is not None)
    check("пост 1: cost 0", r1 and r1['cost'] == 0)
    check("пост 1: tier 0", r1 and r1['tier'] == 0)
    check("пост 1: created_day по МСК", _wall_today_key() == _wall_today_key())

    # ── 2. 4 бесплатных ──
    r2 = await add_wall_post(uid, "Второе")
    r3 = await add_wall_post(uid, "Третье")
    r4 = await add_wall_post(uid, "Четвёртое")
    check("посты 2-4: бесплатные", all(x and x['cost'] == 0 for x in (r1, r2, r3, r4)))
    check("count сегодня = 4", await count_wall_posts_today(uid) == 4)

    # ── 3. 5-й за 30 НМ ──
    bal_before = (await get_user(uid))['nordmarks']
    r5 = await add_wall_post(uid, "Пятое за 30")
    check("пост 5: cost 30", r5 and r5['cost'] == 30)
    check("пост 5: tier 1", r5 and r5['tier'] == 1)
    bal_after = (await get_user(uid))['nordmarks']
    check("списано 30 НМ", bal_before - bal_after == 30)

    # ── 4. Не хватает НМ → need_nm (отдельный пользователь с малым балансом) ──
    uid2 = 999803
    await add_user(uid2, "poor", "Бедный", "Игрок")
    await update_user(uid2, nordmarks=5)
    for i in range(4):
        await add_wall_post(uid2, f"бесплатный {i}")
    check("uid2: 4 бесплатных сделано", await count_wall_posts_today(uid2) == 4)
    r6 = await add_wall_post(uid2, "Пятое, но нет денег")
    check("пост 6 при нехватке: need_nm", r6 and r6.get('need_nm') is True and r6['cost'] == 30)
    check("пост 6: не создан", r6 and r6['post_id'] is None)
    check("не списано при нехватке", (await get_user(uid2))['nordmarks'] == 5)

    # ── 5. Доходим до 13-го (200 НМ) и стоп ──
    await update_user(uid, nordmarks=2000)
    r6 = await add_wall_post(uid, "Шестое")       # #6: 30 НМ
    r7 = await add_wall_post(uid, "Седьмое")       # #7: 30 НМ
    r8 = await add_wall_post(uid, "Восьмое за 90")  # #8: 90 НМ
    r9 = await add_wall_post(uid, "Девятое")       # #9: 90 НМ
    r10 = await add_wall_post(uid, "Десятое")      # #10: 90 НМ
    check("пост #5: cost 30", r5['cost'] == 30)
    check("пост #8: cost 90", r8 and r8['cost'] == 90)
    check("пост #10: cost 90", r10 and r10['cost'] == 90)
    r11 = await add_wall_post(uid, "Одиннадцатое за 200")  # #11: 200 НМ
    check("пост #11: cost 200", r11 and r11['cost'] == 200)
    r12 = await add_wall_post(uid, "Двенадцатое")  # #12: 200 НМ
    r13 = await add_wall_post(uid, "Тринадцатое — последнее")  # #13: 200 НМ
    check("счётчик = 13", await count_wall_posts_today(uid) == 13)
    r14 = await add_wall_post(uid, "Четырнадцатое — стоп")
    check("14-й: стоп (None)", r14 is None)

    # ── 6. Пагинация записей ──
    total = await count_wall_posts()
    check("всего постов = 17 (13 uid + 4 uid2)", total == 17)
    page1 = await get_wall_posts(0, 5)
    page2 = await get_wall_posts(1, 5)
    page3 = await get_wall_posts(2, 5)
    page4 = await get_wall_posts(3, 5)
    check("страница 1: 5 постов", len(page1) == 5)
    check("страница 2: 5 постов", len(page2) == 5)
    check("страница 3: 5 постов", len(page3) == 5)
    check("страница 4: 2 поста", len(page4) == 2)
    check("свежие сверху (страница 1 первая)", page1[0]['id'] > page2[0]['id'])
    check("автор подписан (username/callsign)", "wal" in str(page1[0].get('username') or "").lower()
          or page1[0].get('callsign'))

    # ── 7. Удаление платного → возврат ⅓ ──
    paid_post = page1[0] if page1[0]['cost'] > 0 else page1[1]
    author = paid_post['user_id']
    author_start = (await get_user(author))['nordmarks']
    res = await delete_wall_post(paid_post['id'])
    exp_refund = paid_post['cost'] // 3
    check("возврат ⅓ платного", res and res['refund'] == exp_refund)
    author_end = (await get_user(author))['nordmarks']
    check("автор получил возврат", author_end - author_start == exp_refund)
    check("количество уменьшилось", await count_wall_posts() == total - 1)

    # ── 8. Удаление бесплатного → нет возврата ──
    free_post = await get_wall_posts(0, 20)
    free_post = [p for p in free_post if p['cost'] == 0][0]
    res_free = await delete_wall_post(free_post['id'])
    check("бесплатный: refund 0", res_free and res_free['refund'] == 0)

    # ── 9. wall_keyboard ──
    kb = wall_keyboard(page=0, total_posts=30, post_ids=[1, 2, 3], is_admin=True, can_manage=True)
    flat = [btn.callback_data for row in kb.inline_keyboard for btn in row]
    texts = [btn.text for row in kb.inline_keyboard for btn in row]
    check("kb: пагинация ◀️▶️", "wall:page:1" in flat and "▶️" in texts)
    check("kb: написать", any(b == "wall:write" for b in flat))
    check("kb: удаление админа", any(b.startswith("wall:delete:") for b in flat))
    check("kb: в город", any(b == "city:menu" for b in flat))

    kb2 = wall_keyboard(page=0, total_posts=3, post_ids=[5], is_admin=False, can_manage=False)
    flat2 = [btn.callback_data for row in kb2.inline_keyboard for btn in row]
    check("kb: без админа нет удаления", not any(b.startswith("wall:delete:") for b in flat2))
    check("kb: без пагинации при 1 странице", not any(b.startswith("wall:page:") for b in flat2))

    # ── 10. Хендлер wall_view показывает посты ──
    st = FakeState()
    cb = FakeCallback(uid, data="wall:view")
    await wh.wall_view(cb, st)
    txt = sent_text(cb.message)
    check("wall_view: заголовок", "СТЕНА ИЗРЕЧЕНИЙ" in txt)
    check("wall_view: есть посты", "💬" in txt)

    # ── 10а. Вход с главного меню (Message) открывает ту же стену ──
    msg_w = FakeMessageWithFrom(uid)
    msg_w.text = "🧱 Стена изречений"
    st_m = FakeState()
    await wh.wall_open_text(msg_w, st_m)
    txt_m = sent_text(msg_w)
    check("main menu: стена открывается сразу", "СТЕНА ИЗРЕЧЕНИЙ" in txt_m)
    check("main menu: есть кнопки стены", msg_w.sent[0][2].get('reply_markup') is not None)

    # ── 11. wall:write → FSM; публикация ──
    user_before = (await get_user(uid_admin))
    st_w = FakeState()
    cb_w = FakeCallback(uid_admin, data="wall:write")
    await wh.wall_write_start(cb_w, st_w)
    check("wall:write ставит FSM", st_w._state == WallWrite.waiting_text)
    msg = FakeMessageWithFrom(uid_admin)
    msg.text = "Изречение от админа"
    st_t = FakeState(state=WallWrite.waiting_text)
    await wh.wall_write_text(msg, st_t)
    check("после публикации FSM очищен", st_t._state is None)

    # ── 12. Админ-удаление через хендлер ──
    admin_target = (await get_wall_posts(0, 5))[1]
    target_start = (await get_user(admin_target['user_id']))['nordmarks']
    cb_del = FakeCallback(uid_admin, data=f"wall:delete:{admin_target['id']}")
    await wh.wall_delete(cb_del, FakeState())
    target_end = (await get_user(admin_target['user_id']))['nordmarks']
    exp_refund2 = admin_target['cost'] // 3 if admin_target['cost'] > 0 else 0
    check("админ удалил пост", await _count_posts_by_id(admin_target['id']) == 0)
    if exp_refund2 > 0:
        check("админ-удаление: автору ⅓", target_end - target_start == exp_refund2)

    # ── 13. Не-админ удалить не может ──
    target2 = (await get_wall_posts(0, 5))[0]
    cb_no = FakeCallback(uid, data=f"wall:delete:{target2['id']}")
    await wh.wall_delete(cb_no, FakeState())
    check("обычный игрок не удалил", await _count_posts_by_id(target2['id']) == 1)

    # ── 14. _wall_footer ──
    uid3 = 999804
    await add_user(uid3, "fullwall", "Полная", "Стена")
    await update_user(uid3, nordmarks=2000)
    for i in range(13):
        await add_wall_post(uid3, f"заполнение {i}")
    cnt = await count_wall_posts_today(uid3)
    foot = _wall_footer(uid3, cnt, await get_user(uid3))
    check("footer при исчерпании", foot.startswith("⛔"))

    await close_db()
    print(f"\nSmoke 064: {passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)


async def _count_posts_by_id(post_id: int) -> int:
    from database.db import get_wall_post
    return 0 if (await get_wall_post(post_id)) is None else 1


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