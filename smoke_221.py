# -*- coding: utf-8 -*-
"""Smoke 221 — смена позывного: деньги списываются только после ввода.

Регресс v0.43.16: в profile:callsign_buy оплата снималась сразу, позывной
стирался (set_callsign(user_id, None)), а ввод нового попадал в ветку
«бесплатная установка уже использована» — игрок терял и 500 НМ, и позывной.

1. Первая установка — бесплатно, без списаний.
2. Платная смена: после «Оплатить» деньги ещё целы, старый позывной на месте;
   списание и замена — только после ввода нового.
3. Отмена после «Оплатить» ничего не списывает.
4. Не хватило НМ к моменту ввода — отказ, позывной и баланс не меняются.
5. Без оплаты (free_used=1) ввод не принимается — старый позывной остаётся.
"""
import asyncio
import os
import sys
from types import SimpleNamespace

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke221.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB

sys.path.insert(0, os.path.dirname(__file__))


class FakeMessage:
    def __init__(self, text=""):
        self.text = text
        self.photo = None
        self.from_user = SimpleNamespace(id=1)
        self.sent = []

    async def answer(self, *a, **kw):
        self.sent.append((a, kw))

    async def answer_photo(self, *a, **kw):
        self.sent.append((a, kw))

    async def edit_text(self, *a, **kw):
        self.sent.append((a, kw))


class FakeCallback:
    def __init__(self, user_id, data=""):
        self.from_user = SimpleNamespace(id=user_id)
        self.message = FakeMessage()
        self.data = data
        self.answers = []

    async def answer(self, *a, **kw):
        self.answers.append((a, kw))
        return True


class FakeState:
    def __init__(self):
        self._state = None
        self._data = {}

    async def get_state(self):
        return self._state

    async def set_state(self, s):
        self._state = s

    async def get_data(self):
        return dict(self._data)

    async def update_data(self, **kw):
        self._data.update({k: v for k, v in kw.items() if v is not None})
        for k, v in kw.items():
            if v is None:
                self._data.pop(k, None)

    async def clear(self):
        self._data.clear()
        self._state = None


def _texts(msg):
    return " ".join(str(a[0]) for a in msg.sent if a)


def _buttons(msg):
    out = []
    for _a, kw in msg.sent:
        m = kw.get("reply_markup")
        if m:
            out += [b.callback_data for row in m.inline_keyboard for b in row]
    return out


async def run():
    import config
    from database.db import (init_db, close_db, add_user, update_user, get_user,
                             set_callsign, set_callsign_free_used, get_db)
    from bot.handlers import profile as prof

    await init_db()

    UID_FREE, UID_PAID, UID_CANCEL, UID_POOR, UID_NOFREE = (
        9992211, 9992212, 9992213, 9992214, 9992215)
    for uid, nick in ((UID_FREE, "Новичок"), (UID_PAID, "Старый"),
                      (UID_CANCEL, "Второй"), (UID_POOR, "Третий"),
                      (UID_NOFREE, "Четвёртый")):
        await add_user(uid, f"u{uid}", nick, "")
        await update_user(uid, nordmarks=1000)

    passed = failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
            print(f"  OK  {name}")
        else:
            failed += 1
            print(f"  FAIL: {name}")

    async def balance(uid):
        u = await get_user(uid)
        return u["nordmarks"]

    async def treasury():
        conn = await get_db()
        row = await (await conn.execute(
            "SELECT balance FROM treasury WHERE id = 1")).fetchone()
        return row["balance"] if row else 0

    async def pay_tx(uid):
        conn = await get_db()
        rows = await (await conn.execute(
            "SELECT id FROM transactions WHERE from_user = ? AND description = ?",
            (uid, "Смена позывного"))).fetchall()
        return len(rows)

    print("\n1. Первая установка — бесплатно")
    st = FakeState()
    cb = FakeCallback(UID_FREE, "profile:callsign")
    await prof.profile_callsign(cb, st)
    check("состояние ввода позывного", st._state == prof.ProfileStates.waiting_callsign.state)
    check("просит ввести позывной", "Введи желаемый позывной" in _texts(cb.message))
    msg = FakeMessage(text="Первый")
    msg.from_user = SimpleNamespace(id=UID_FREE)
    bal0 = await balance(UID_FREE)
    await prof.profile_callsign_input(msg, st)
    u = await get_user(UID_FREE)
    check("позывной установлен", u["callsign"] == "Первый")
    check("списаний нет", await balance(UID_FREE) == bal0)
    check("бесплатная установка отмечена", bool(u["callsign_free_used"]))

    print("\n2. Платная смена: списание после ввода")
    await set_callsign(UID_PAID, "Старый")
    await set_callsign_free_used(UID_PAID, 1)
    await update_user(UID_PAID, nordmarks=1000)
    bal0, tr0 = await balance(UID_PAID), await treasury()

    st = FakeState()
    cb = FakeCallback(UID_PAID, "profile:callsign")
    await prof.profile_callsign(cb, st)
    check("предлагает оплатить", "profile:callsign_buy" in _buttons(cb.message))
    check("цена в тексте", f"{config.CALLSIGN_PRICE} НМ" in _texts(cb.message))

    cb = FakeCallback(UID_PAID, "profile:callsign_buy")
    await prof.profile_callsign_buy(cb, st)
    check("после «Оплатить» деньги целы", await balance(UID_PAID) == bal0)
    check("после «Оплатить» старый позывной на месте",
          (await get_user(UID_PAID))["callsign"] == "Старый")
    check("оплата помечена в состоянии",
          st._data.get("callsign_pay_pending") == config.CALLSIGN_PRICE)
    check("списаний в казну ещё нет", await treasury() == tr0)

    msg = FakeMessage(text="Новый")
    msg.from_user = SimpleNamespace(id=UID_PAID)
    await prof.profile_callsign_input(msg, st)
    check("новый позывной установлен",
          (await get_user(UID_PAID))["callsign"] == "Новый")
    check("списано 500", await balance(UID_PAID) == bal0 - config.CALLSIGN_PRICE)
    check("казна пополнена", await treasury() == tr0 + config.CALLSIGN_PRICE)
    check("одна транзакция «Смена позывного»", await pay_tx(UID_PAID) == 1)
    check("состояние сброшено", st._state is None)

    print("\n3. Отмена после «Оплатить» ничего не списывает")
    await set_callsign(UID_CANCEL, "Второй")
    await set_callsign_free_used(UID_CANCEL, 1)
    await update_user(UID_CANCEL, nordmarks=800)
    bal0 = await balance(UID_CANCEL)
    st = FakeState()
    await prof.profile_callsign(FakeCallback(UID_CANCEL), st)
    await prof.profile_callsign_buy(FakeCallback(UID_CANCEL, "profile:callsign_buy"), st)
    await prof.profile_callsign_cancel(FakeCallback(UID_CANCEL, "profile:callsign_cancel"), st)
    check("баланс не изменился", await balance(UID_CANCEL) == bal0)
    check("позывной не изменился", (await get_user(UID_CANCEL))["callsign"] == "Второй")
    check("состояние сброшено", st._state is None)

    print("\n4. Не хватило НМ к моменту ввода")
    await set_callsign(UID_POOR, "Третий")
    await set_callsign_free_used(UID_POOR, 1)
    await update_user(UID_POOR, nordmarks=1000)
    tr0 = await treasury()
    st = FakeState()
    await prof.profile_callsign(FakeCallback(UID_POOR), st)
    await prof.profile_callsign_buy(FakeCallback(UID_POOR, "profile:callsign_buy"), st)
    await update_user(UID_POOR, nordmarks=100)
    msg = FakeMessage(text="Не пройдёт")
    msg.from_user = SimpleNamespace(id=UID_POOR)
    await prof.profile_callsign_input(msg, st)
    check("позывной не изменился", (await get_user(UID_POOR))["callsign"] == "Третий")
    check("баланс не списан", await balance(UID_POOR) == 100)
    check("казна не пополнена", await treasury() == tr0)
    check("сообщение о нехватке", "Недостаточно НМ" in _texts(msg))
    check("состояние сброшено", st._state is None)

    print("\n5. Ввод без оплаты не принимается")
    await set_callsign_free_used(UID_NOFREE, 1)
    await set_callsign(UID_NOFREE, None)
    st = FakeState()
    msg = FakeMessage(text="Без оплаты")
    msg.from_user = SimpleNamespace(id=UID_NOFREE)
    await prof.profile_callsign_input(msg, st)
    check("позывной не установлен", (await get_user(UID_NOFREE))["callsign"] is None)
    check("объясняет, что нужна оплата", "Бесплатная установка уже использована" in _texts(msg))

    await close_db()
    print(f"\nИТОГО: {passed} passed, {failed} failed")
    return failed


if __name__ == "__main__":
    sys.exit(1 if asyncio.run(run()) else 0)
