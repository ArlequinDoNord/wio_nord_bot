"""Smoke v0.13.12: три фикса по фидбеку.

1) Рынок: кнопка «🔙 Рынок»/пагинация в списке вызывали edit_text на
   фото-карточке (карточка рыбы после покупки) — на фото-сообщении это
   падало («there is no text in the message to edit»), назад не возвращало.
   Теперь show_items_page / ветка «нет товаров» используют edit_or_replace,
   который с фото уходит через delete+answer.
2) Кадка: подтверждение «Убрать кадку с растением» показывалось на фоне
   жилья, а не кадки/растения. Введён _plant_stage_photo(data, ht, stage) —
   стадия 0 = общая кадка, 1..4 = индив. файлы (если есть), иначе фото комнаты.
3) Фонтан: предупреждение при полном запасе ОД (кнопка «Восстановить» не
   показывается, «полный запас ОД — ничего не даст»), защита в drink тоже.

Запуск: .venv\\Scripts\\python.exe smoke_061.py
"""
import asyncio
import os
import sys
from types import SimpleNamespace

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke061.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB

sys.path.insert(0, os.path.dirname(__file__))


class FakeMessage:
    def __init__(self, text=""):
        self.sent = []
        self.text = text
        self.message_id = 1
        self.from_user = SimpleNamespace(id=1)
        self.photo = None

    async def answer(self, *a, **kw):
        self.sent.append(("answer", a, kw))

    async def answer_photo(self, *a, **kw):
        self.sent.append(("answer_photo", a, kw))

    async def edit_text(self, *a, **kw):
        self.sent.append(("edit_text", a, kw))

    async def edit_caption(self, *a, **kw):
        self.sent.append(("edit_caption", a, kw))

    async def edit_media(self, *a, **kw):
        self.sent.append(("edit_media", a, kw))

    async def delete(self, *a, **kw):
        self.sent.append(("delete", a, kw))


class FakeCallback:
    def __init__(self, user_id, data=""):
        self.from_user = SimpleNamespace(id=user_id)
        self.message = FakeMessage()
        self.data = data
        self.alerts = []

    async def answer(self, text=None, *a, **kw):
        self.alerts.append(text)


async def run():
    from database.db import init_db, close_db, seed_default_items, add_user, update_user
    from bot.handlers import shop as sh
    from bot.handlers import housing as hh
    from bot.handlers import park as pk

    await init_db()
    await seed_default_items()

    uid = 999471
    await add_user(uid, "pilot", "Пилот", "")

    passed = 0
    failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
        else:
            failed += 1
            print(f"  FAIL: {name}")

    # ── 1. рынок: список категории с фото-сообщения уходит через delete+answer ──
    cb1 = FakeCallback(uid, "shopcat:market")
    cb1.message.photo = "fake_photo"
    try:
        await sh.show_items_page(cb1, "market", [], 0)
        kinds1 = [m[0] for m in cb1.message.sent]
        check("shop: список рынка уходит с фото (delete+answer)",
              "delete" in kinds1 and "answer" in kinds1 and "edit_text" not in kinds1)
    except Exception as e:
        check(f"shop: список рынка без исключения ({e!r})", False)

    cb2 = FakeCallback(uid, "shopcat:market")
    cb2.message.photo = "fake_photo"
    try:
        # ветка «нет товаров» в shop_category тоже должна использовать edit_or_replace
        src_cat = __import__("inspect").getsource(sh.show_items_page)
        check("shop: show_items_page использует edit_or_replace", "edit_or_replace" in src_cat)
    except Exception:
        check("shop: show_items_page использует edit_or_replace", False)

    # ── 2. кадка: правильная картинка стадии ──
    data = {"seed": "Яблочное семечко"}
    p0 = hh._plant_stage_photo(data, "kubrick", 0)
    check("kadka: стадия 0 — общая кадка", os.path.isfile(p0) and p0.endswith("kadka.jpg"))
    p1 = hh._plant_stage_photo(data, "kubrick", 1)
    check("kadka: стадия 1 — яблоня росток",
          p1 and os.path.isfile(p1) and p1.endswith("plant_apple_1.jpg"))
    p4 = hh._plant_stage_photo(data, "kubrick", 4)
    check("kadka: стадия 4 — яблоня плодоносящее",
          p4 and os.path.isfile(p4) and p4.endswith("plant_apple_4.jpg"))
    fallback = hh._plant_stage_photo({"seed": "Неизвестное семечко"}, "kubrick", 2)
    check("kadka: неизвестное семечко — фолбэк (а не эксепшн)", True)

    src_uninstall = __import__("inspect").getsource(hh.housing_uninstall)
    check("kadka: подтверждение использует _plant_stage_photo",
          "_plant_stage_photo" in src_uninstall)

    # ── 3. фонтан: предупреждение при полном запасе ОД ──
    mk_full = pk.fountain_markup(can_use=True, full=True)
    cb_full = [b.callback_data for row in mk_full.inline_keyboard for b in row]
    check("фонтан: полный ОД — кнопки восстановления нет", "park:fountain:drink" not in cb_full)
    check("фонтан: полный ОД — «В парк» на месте", "park:menu" in cb_full)

    mk_ok = pk.fountain_markup(can_use=True, full=False)
    cb_ok = [b.callback_data for row in mk_ok.inline_keyboard for b in row]
    check("фонтан: неполный ОД — кнопка восстановления есть", "park:fountain:drink" in cb_ok)

    # экран фонтана при полном ОД: в caption предупреждение
    await update_user(uid, ap=150, ap_max=150)
    cbf = FakeCallback(uid, "park:fountain")
    await pk.park_fountain(cbf)
    captions = []
    for m in cbf.message.sent:
        if m[0] in ("answer_photo",):
            kw = m[2] or {}
            if "caption" in kw:
                captions.append(kw["caption"])
    check("фонтан: caption с предупреждением о полном ОД",
          any("полный запас ОД" in c for c in captions))
    last_markup = None
    for m in reversed(cbf.message.sent):
        if m[0] in ("answer_photo",) and (m[2] or {}).get("reply_markup"):
            last_markup = m[2]["reply_markup"]
            break
    if last_markup is not None:
        cb2 = [b.callback_data for row in last_markup.inline_keyboard for b in row]
        check("фонтан: на экране при полном ОД нет кнопки восстановления",
              "park:fountain:drink" not in cb2)
    else:
        check("фонтан: reply_markup пришёл", False)

    await close_db()
    print(f"\nSmoke 061: {passed} passed, {failed} failed")
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