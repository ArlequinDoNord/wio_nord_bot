"""Smoke 114 — регрессия v0.18.18: ввод не должен пропадать.

Что чиним:
   1. admin.py держал обработчик `@router.message(F.text.regexp(r"^\\d+$"))` —
      БЕЗ фильтра состояния. Роутер админа зарегистрирован раньше роутера
      отчётов, а в aiogram сработавший обработчик останавливает обработку
      события: любая цифра, введённая пилотом в сдаче отчёта, уходила в
      админский обработчик и там молча терялась. Отчёт зависал после фото.
   2. Обращение Представителя: правки нет, изменение = новое обращение
      (тратит лимит), удаление лимит не тратит.
   3. Лес: токен в callback с зоной (forest:area:TOKEN:ЗОНА) не должен
      считаться устаревшим окном.
"""
import asyncio
import os
import sys

_TEST_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_test_smoke114.db")
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


def state_of(cb):
    """Состояние фильтра: aiogram принимает и State, и StateFilter."""
    from aiogram.filters import StateFilter
    from aiogram.fsm.state import State
    if isinstance(cb, StateFilter):
        return cb.state
    if isinstance(cb, State):
        return cb
    return None


async def main():
    import config

    config.DB_PATH = _TEST_DB

    import database.db as db

    db.DB_PATH = _TEST_DB
    await db.init_db()

    # --- 1. ни один обработчик цифр не должен быть без состояния -----------
    print("\n[1] Обработчики ввода чисел привязаны к состояниям")
    from bot.handlers import admin as A

    rogue = []
    for h in A.router.message.handlers:
        has_state = any(state_of(f.callback) is not None for f in h.filters)
        if not has_state:
            name = getattr(h.callback, "__name__", "?")
            # точное совпадение с кнопкой меню — не перехватчик ввода
            rogue.append(name)

    target = next((h for h in A.router.message.handlers
                   if getattr(h.callback, "__name__", "") == "admin_forest_zone_value"), None)
    check("admin_forest_zone_value существует", target is not None)
    if target is not None:
        states = [state_of(f.callback) for f in target.filters
                  if state_of(f.callback) is not None]
        check("обработчик зоны леса привязан к AdminForest.zone_value",
              states == [A.AdminForest.zone_value])

    # ни в одном роутере не осталось «ловца» голых цифр без состояния
    import importlib
    import pkgutil

    import bot.handlers as bh

    catchers = []
    for _m in pkgutil.iter_modules(bh.__path__):
        try:
            mod = importlib.import_module(f"bot.handlers.{_m.name}")
        except Exception:
            continue
        router = getattr(mod, "router", None)
        if router is None or not hasattr(router, "message"):
            continue
        for h in router.message.handlers:
            has_state = any(state_of(f.callback) is not None for f in h.filters)
            if has_state:
                continue
            name = getattr(h.callback, "__name__", "?")
            # ловец: принимает ЛЮБОЕ сообщение из цифр
            try:
                if h.check.__self__ is not None:  # pragma: no cover
                    pass
            except Exception:
                pass
            catchers.append((_m.name, name))

    # проверяем напрямую: безсостоянийный хендлер не должен ловить «150».
    # Раньше админский ловец совпадал с любым текстом из цифр.
    import datetime as _dt

    from aiogram.types import Chat as _Chat
    from aiogram.types import Message as _Message

    def _msg(text):
        return _Message(
            message_id=1,
            date=_dt.datetime.now(_dt.timezone.utc),
            chat=_Chat(id=1, type="private"),
            text=text,
        )

    bad = []
    for mod_name, handler_name in catchers:
        mod = sys.modules[f"bot.handlers.{mod_name}"]
        h = next(x for x in mod.router.message.handlers
                 if getattr(x.callback, "__name__", "") == handler_name)
        matched = False
        for f in h.filters:
            try:
                res = f.check(_msg("150"))
            except Exception:
                res = False
            if res is not False:
                matched = True
                break
        if matched:
            bad.append(f"{mod_name}.{handler_name}")

    check("нет безсостоянийных обработчиков, ловящих ввод числа «150»", not bad)
    if bad:
        print("      перехватывают ввод:", bad)

    # --- 2. Обращение Представителя: нет правки, есть удаление ------------
    print("\n[2] Обращение Представителя: правки нет")
    from bot.handlers import representative as rep_mod

    class _Msg:
        def __init__(self, text=None, uid=1):
            self.text = text
            self.photo = None
            self.from_user = type("U", (), {"id": uid})()
            self.message = type("M", (), {"answers": [], "markup": None, "text": None})()
            self.bot = None

        async def answer(self, text=None, reply_markup=None, **kw):
            self.message.answers.append(text)
            self.message.text = text
            self.message.markup = reply_markup

        async def edit_text(self, text=None, reply_markup=None, **kw):
            self.message.text = text
            self.message.markup = reply_markup

        async def delete(self, **kw):
            return None

    class _CBMsg:
        def __init__(self):
            self.text = None
            self.markup = None
            self.answers = []
            self.photo = False

        async def answer(self, text=None, reply_markup=None, **kw):
            self.answers.append(text)
            self.text = text
            self.markup = reply_markup

        async def edit_text(self, text=None, reply_markup=None, **kw):
            self.text = text
            self.markup = reply_markup

        async def delete(self, **kw):
            return None

    class _CB:
        def __init__(self, data, uid=1):
            self.data = data
            self.from_user = type("U", (), {"id": uid})()
            self.message = _CBMsg()

        async def answer(self, *a, **kw):
            return None

    class _State:
        def __init__(self):
            self.data = {}
            self._s = None

        async def get_data(self):
            return self.data

        async def update_data(self, **kw):
            self.data.update(kw)

        async def set_state(self, s):
            self._s = s

        async def clear(self):
            self.data = {}
            self._s = None

    import utils.permissions as perms

    orig_has = perms.has_permission
    perms.has_permission = lambda uid, perm: asyncio.sleep(0, result=True)
    rep_mod.has_permission = perms.has_permission
    sent = []

    async def fake_notify(bot, text, *a, **kw):
        sent.append(text)

    rep_mod.notify = fake_notify

    uid = 777
    await db.add_user(uid, "rep114", "Р", "Аркхольм")
    await db.add_user(998, "other114", "О", "Ольховск")
    try:
        await db.add_rep_speech(uid, "Первое обращение")
        cb = _CB("rep:speech")
        await rep_mod.rep_speech_open(cb, _State())
        labels = [b.text for row in (cb.message.markup.inline_keyboard or [])
                  for b in row]
        check("в карточке обращения нет кнопки правки",
              not any("Изменить" in t for t in labels))
        check("в карточке обращения есть удаление",
              any("Удалить обращение" in t for t in labels))

        # изменение = новое обращение, лимит тратится
        st = _State()
        m = _Msg("Второе обращение", uid)
        await rep_mod.rep_speech_text(m, st, None)
        check("изменение создало новое обращение",
              (await db.get_latest_rep_speech())['text'] == "Второе обращение")
        check("изменение потратило лимит",
              await db.count_rep_speeches_today(uid) == 2)

        # удаление не тратит лимит
        latest = await db.get_latest_rep_speech()
        await db.delete_rep_speech(latest['id'])
        check("после удаления осталось предыдущее",
              (await db.get_latest_rep_speech())['text'] == "Первое обращение")
        check("удаление не тратило лимит",
              await db.count_rep_speeches_today(uid) == 1)

        # кнопка удаления чужого обращения не работает
        row = await db.get_latest_rep_speech()
        conn = await db.get_db()
        await conn.execute("UPDATE rep_speeches SET user_id = ? WHERE id = ?",
                           (998, row['id']))
        await conn.commit()
        cb2 = _CB("rep:speech:delete", uid)
        await rep_mod.rep_speech_delete(cb2, _State())
        check("чужое обращение удалить нельзя",
              "только своё" in (cb2.message.text or ""))
    finally:
        perms.has_permission = orig_has

    # --- 3. Лес: токен с зоной не считается устаревшим ---------------------
    print("\n[3] Лес: токен в callback с зоной")
    from bot.handlers import forest as F_

    check("токен леса извлекается из forest:area",
          F_._callback_token("forest:area:123456:glade") == "123456")
    check("токен леса извлекается из forest:cast",
          F_._callback_token("forest:cast:123456:clearing") == "123456")
    check("токен леса извлекается из forest:battle:hit",
          F_._callback_token("forest:battle:hit:123456") == "123456")
    check("токен леса извлекается из forest:battle:flee",
          F_._callback_token("forest:battle:flee:123456") == "123456")

    print(f"\n=== SMOKE 114: {PASS} passed, {FAIL} failed ===")

    return 1 if FAIL else 0


if __name__ == "__main__":
    code = 1
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        code = loop.run_until_complete(main())
    finally:
        _l = asyncio.new_event_loop()
        asyncio.set_event_loop(_l)
        try:
            import database.db as _db

            if _db.db is not None:
                _l.run_until_complete(_db.close_db())
        except Exception:
            pass
        _l.close()
    sys.exit(code)
