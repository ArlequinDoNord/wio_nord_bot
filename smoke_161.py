"""Smoke 161: клан-холл выключен, кнопка клана в профиле, душ сбивает опьянение.

Проверяет:
1. `config.CLAN_HALL_ENABLED` есть в конфиге (фича включена с v0.39.8).
2. Карточка клана при выключенном холле не показывает кнопок `clanh:` (ни здание,
   ни склад); при включённом — показывает.
3. Guard-мидлварь `clan_hall.clan_hall_guard`: при False не пускает дальше и
   отвечает заглушкой, при True — вызывает хендлер.
4. Профиль пилота: у члена клана есть кнопка `clans:view:<id>` с названием клана;
   у пилота без клана такой кнопки нет.
5. `utils.states.reduce_state_minutes`: укорачивает «пьян»/«очень пьян», снимает
   состояние при остатке ≤ сокращения и не трогает другие состояния.

Запуск: .venv\\Scripts\\python.exe smoke_161.py
"""
import asyncio
import os
import sys
from types import SimpleNamespace

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

_TEST_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_test_smoke161.db")
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


class FakeBot:
    def __init__(self):
        self.sent = []

    async def send_message(self, chat_id, text, parse_mode=None, reply_markup=None):
        self.sent.append((chat_id, text))
        return True


class FakeMessage:
    def __init__(self):
        self.photo = None
        self.text = None
        self.kb = None
        self.sent = []

    async def edit_text(self, text, parse_mode=None, reply_markup=None):
        self.text, self.kb = text, reply_markup
        return self

    async def edit_caption(self, caption, parse_mode=None, reply_markup=None):
        self.text, self.kb = caption, reply_markup
        return self

    async def edit_media(self, media, reply_markup=None):
        self.text = getattr(media, "caption", None)
        self.kb = reply_markup
        self.photo = [getattr(media, "media", None)]
        return self

    async def answer_photo(self, photo, caption=None, parse_mode=None, reply_markup=None):
        self.photo = [photo]
        self.text = caption
        self.kb = reply_markup
        return self

    async def answer(self, text, parse_mode=None, reply_markup=None):
        self.text = text
        self.kb = reply_markup
        return self


class FakeCallback:
    def __init__(self, uid, data="", bot=None):
        self.from_user = SimpleNamespace(id=uid)
        self.message = FakeMessage()
        self.data = data
        self.alerts = []
        self.bot = bot or FakeBot()

    async def answer(self, text=None, *a, **k):
        self.alerts.append(text)
        return True


def cbs(kb):
    if not kb:
        return []
    return [b.callback_data for row in kb.inline_keyboard for b in row]


def kb_texts(kb):
    if not kb:
        return []
    return [b.text for row in kb.inline_keyboard for b in row]


async def main():
    import config
    config.DB_PATH = _TEST_DB
    check("CLAN_HALL_ENABLEDесть в конфиге (с v0.39.8 включён)",
          getattr(config, "CLAN_HALL_ENABLED", None) in (True, False))
    config.CLAN_HALL_ENABLED = False

    import database.db as db
    db.DB_PATH = _TEST_DB
    from database.db import (
        init_db, close_db, add_user, create_clan, add_clan_member, set_clan_leader,
        get_user_clan,
    )
    from bot.handlers import clan_hall, clans
    from bot.handlers import profile as prof
    from utils.states import apply_state_to, get_state_info, reduce_state_minutes

    await init_db()
    try:
        LEADER, MEMBER, LONER = 161001, 161002, 161003
        for uid, nm in ((LEADER, "leader161"), (MEMBER, "member161"), (LONER, "loner161")):
            await add_user(uid, nm, nm.title(), "")

        clan_id = await create_clan("clan", "Полярная Звезда", "Тестовый клан", LEADER)
        await set_clan_leader(clan_id, LEADER)
        await add_clan_member(clan_id, LEADER)
        await add_clan_member(clan_id, MEMBER)

        # ── 1-2. Карточка клана при выключенном/включённом холле ──
        cb_view = FakeCallback(MEMBER, f"clans:view:{clan_id}")
        await clans.clan_view_cb(cb_view)
        view_cbs = cbs(cb_view.message.kb)
        check("холл выключен: нет кнопки «Здание клана»",
              f"clanh:hall:{clan_id}" not in view_cbs)
        check("холл выключен: нет кнопки «Склад клана»",
              f"clanh:storage:{clan_id}" not in view_cbs)
        check("холл выключен: ни одного callbacks clanh:",
              not any(x.startswith("clanh:") for x in view_cbs))

        config.CLAN_HALL_ENABLED = True
        cb_view_on = FakeCallback(MEMBER, f"clans:view:{clan_id}")
        await clans.clan_view_cb(cb_view_on)
        view_on = cbs(cb_view_on.message.kb)
        check("холл включён: кнопка «Здание клана» есть",
              f"clanh:hall:{clan_id}" in view_on)
        check("холл включён: кнопка «Склад клана» есть",
              f"clanh:storage:{clan_id}" in view_on)
        config.CLAN_HALL_ENABLED = False

        # ── 3. Guard-мидлварь ──
        called = []

        async def _handler(event, data):
            called.append(True)
            return "handled"

        cb_old = FakeCallback(MEMBER, f"clanh:hall:{clan_id}")
        res = await clan_hall.clan_hall_guard(_handler, cb_old, {})
        check("guard выключен: хендлер не вызван", res is None and not called)
        check("guard выключен: игроку показана заглушка",
              any(t and "дорабатывается" in t for t in cb_old.alerts))

        config.CLAN_HALL_ENABLED = True
        res_on = await clan_hall.clan_hall_guard(_handler, cb_old, {})
        check("guard включён: хендлер вызван", res_on == "handled" and called)
        config.CLAN_HALL_ENABLED = False

        # ── 4. Кнопка клана в профиле ──
        msg = FakeMessage()
        await prof.render_profile(msg, MEMBER)
        prof_cbs = cbs(msg.kb)
        check("профиль: кнопка перехода в карточку клана",
              f"clans:view:{clan_id}" in prof_cbs)
        check("профиль: на кнопке название клана",
              any("Полярная Звезда" in (t or "") for t in kb_texts(msg.kb)))

        msg_loner = FakeMessage()
        await prof.render_profile(msg_loner, LONER)
        check("профиль без клана: нет кнопки clans:view:",
              not any(x.startswith("clans:view:") for x in cbs(msg_loner.kb)))

        # ── 5. Сокращение таймера опьянения ──
        state_uid = 161010
        await add_user(state_uid, "drunk161", "Drunk161", "")
        check("get_user_clan видит клан", (await get_user_clan(MEMBER, "clan")) is not None)

        await apply_state_to(state_uid, "пьян", minutes=120)
        changes = await reduce_state_minutes(state_uid, ("пьян",), 60, reason="тест")
        info = await get_state_info(state_uid)
        left = next((s["minutes_left"] for s in info["states"] if s["key"] == "пьян"), None)
        check("reduce: изменения вернулись",
              len(changes) == 1 and 118 <= changes[0]["before"] <= 120)
        check("reduce: «пьян» 120 → ~60 мин", left is not None and 58 <= left <= 60)

        changes2 = await reduce_state_minutes(state_uid, ("пьян",), 999)
        info2 = await get_state_info(state_uid)
        check("reduce: остаток ≤ сокращения снимает состояние",
              not any(s["key"] == "пьян" for s in info2["states"]))
        check("reduce: изменение помечено removed",
              changes2 and changes2[0]["removed"] is True)

        await apply_state_to(state_uid, "истощён", minutes=2880)
        await apply_state_to(state_uid, "очень пьян", minutes=360)
        await reduce_state_minutes(state_uid, ("пьян", "очень пьян"), 180)
        info3 = await get_state_info(state_uid)
        very_left = next((s["minutes_left"] for s in info3["states"]
                          if s["key"] == "очень пьян"), None)
        check("reduce: «очень пьян» 360 → ~180 мин",
              very_left is not None and 178 <= very_left <= 180)
        check("reduce: «истощён» не тронут",
              any(s["key"] == "истощён" for s in info3["states"]))
        check("reduce: пустой список состояний — no-op",
              await reduce_state_minutes(state_uid, (), 60) == [])
    finally:
        await close_db()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except SystemExit:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        from database.db import close_db
        asyncio.run(close_db())
        print(f"SMOKE ERROR: {e!r}")
        sys.exit(1)

    print(f"\nSmoke 161: {PASS} passed, {FAIL} failed")
    sys.exit(1 if FAIL else 0)
