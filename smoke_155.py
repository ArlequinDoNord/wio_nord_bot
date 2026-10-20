"""Smoke v0.36.0: рынок — снятие своего объявления с продажи.

1) Лента «Рынок» помечает свои объявления «👤 твоё» — иначе кнопку снятия
   в чужом потоке объявлений не найти.
2) Карточка своего объявления (предмет и улов) даёт кнопку «🔕 Снять с
   продажи» вместо «💰 Купить», чужое объявление по-прежнему покупается.
3) Снятие предмета: объявление удалено, штука вернулась в инвентарь, слот
   освободился.
4) Снятие улова: объявление удалено, улов вернулся в «Улов» с той же
   замороженной свежестью (находка-ресурс возвращается без срока порчи).
5) Снять чужое объявление нельзя; уже снятое — «объявления уже нет».
6) Выкуп собственного объявления по-прежнему запрещён (баланс и слот не тронуты).

Запуск: .venv\\Scripts\\python.exe smoke_155.py
"""
import asyncio
import os
import sys
import time
from types import SimpleNamespace

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke155.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB

sys.path.insert(0, os.path.dirname(__file__))


class _Msg:
    def __init__(self, photo=None):
        self.photo = photo
        self.edits = []
        self.answers = []
        self.deleted = False

    async def edit_text(self, text, reply_markup=None):
        self.edits.append((text, reply_markup))
        return True

    async def answer(self, text, reply_markup=None):
        self.answers.append((text, reply_markup))

    async def delete(self):
        self.deleted = True


class _CB:
    def __init__(self, uid, data="", msg=None):
        self.from_user = SimpleNamespace(id=uid)
        self.data = data
        self.message = msg if msg is not None else _Msg()
        self.alerts = []

    async def answer(self, text=None, show_alert=False, **kw):
        self.alerts.append((text, show_alert))


def cbs(kb):
    if kb is None:
        return []
    return [b.callback_data for row in kb.inline_keyboard for b in row]


async def run():
    from database.db import (
        init_db, close_db, add_user, get_user, add_item, add_inventory_item,
        get_inventory_item, remove_inventory_item,
        place_item_offer, get_item_offer, get_item_offers,
        add_fish_offer, get_fish_offer, add_fish_catch, take_fish_catch,
        get_fish_catches, count_user_market_offers,
    )
    from bot.handlers.shop import (
        fish_offer_view, item_offer_view, _cancel_offer, item_buy, fish_buy,
        market_offer_items, items_page_markup,
    )

    await init_db()

    uid = 999951
    other = 999952
    await add_user(uid, "tester", "Тест", "")
    await add_user(other, "tester2", "Тест2", "")

    passed = 0
    failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
        else:
            failed += 1
            print(f"  FAIL: {name}")

    # ── 1. предмет: карточка своего и чужого объявления ──
    item_id = await add_item(
        name="Тестовый артефакт рынка", description="тест", price=200,
        sell_price=100, rarity=2, category="special", stock=-1,
        added_by=uid, market_ok=1)
    await add_inventory_item(uid, item_id, 1)
    await remove_inventory_item(uid, item_id, 1)   # как при выкладке
    offer_id = await place_item_offer(uid, item_id, 130)
    check("предмет: объявление выставлено", await get_item_offer(offer_id) is not None)
    check("предмет: слот занят", await count_user_market_offers(uid) == 1)

    # лента «Рынок» помечает свои объявления — иначе кнопку снятия не найти
    mkt = await market_offer_items()
    own_list = await items_page_markup(mkt, "market", 0, uid)
    other_list = await items_page_markup(mkt, "market", 0, other)
    own_texts = [b.text for row in own_list.inline_keyboard for b in row]
    other_texts = [b.text for row in other_list.inline_keyboard for b in row]
    check("лента: своё объявление помечено «👤 твоё»",
          any("👤 твоё" in t for t in own_texts))
    check("лента: чужое объявление без пометки",
          not any("👤 твоё" in t for t in other_texts))

    own = _CB(uid, f"itemoffer:{offer_id}")
    await item_offer_view(own)
    own_kb = cbs(own.message.edits[-1][1]) if own.message.edits else []
    check("своя карточка: есть «Снять с продажи»",
          any(c.startswith("offercancel:item:") for c in own_kb))
    check("своя карточка: нет кнопки покупки",
          not any(c.startswith("itembuy:") for c in own_kb))
    check("своя карточка: про подпись владельца",
          "Это твоё объявление" in own.message.edits[-1][0])

    foreign = _CB(other, f"itemoffer:{offer_id}")
    await item_offer_view(foreign)
    foreign_kb = cbs(foreign.message.edits[-1][1]) if foreign.message.edits else []
    check("чужая карточка: есть кнопка покупки",
          any(c.startswith("itembuy:") for c in foreign_kb))
    check("чужая карточка: нет кнопки снятия",
          not any(c.startswith("offercancel:") for c in foreign_kb))

    # ── 2. выкуп самого себя запрещён ──
    bal_before = (await get_user(uid))['nordmarks']
    await item_buy(_CB(uid, f"itembuy:{offer_id}"))
    check("выкуп себя: объявление осталось", await get_item_offer(offer_id) is not None)
    check("выкуп себя: баланс не тронут",
          (await get_user(uid))['nordmarks'] == bal_before)

    # ── 3. чужое объявление снять нельзя ──
    other_cb = _CB(other, f"offercancel:item:{offer_id}")
    await _cancel_offer(other_cb, "item", offer_id)
    check("чужое снятие: объявление осталось", await get_item_offer(offer_id) is not None)
    check("чужое снятие: отказ в алерте",
          any("только своё" in (a[0] or "") and a[1] for a in other_cb.alerts))
    check("чужое снятие: предмет не вернулся владельцу",
          (await get_inventory_item(uid, item_id)) is None)

    # ── 4. своё снятие: предмет возвращается ──
    msg = _Msg()
    await _cancel_offer(_CB(uid, f"offercancel:item:{offer_id}", msg), "item", offer_id)
    check("снятие предмета: объявления больше нет",
          await get_item_offer(offer_id) is None)
    inv = await get_inventory_item(uid, item_id)
    check("снятие предмета: штука в инвентаре", inv is not None and inv['quantity'] == 1)
    check("снятие предмета: слот свободен", await count_user_market_offers(uid) == 0)
    check("снятие предмета: подтверждение", "снят с продажы" in msg.edits[-1][0])
    kb = cbs(msg.edits[-1][1])
    check("снятие предмета: кнопка к предмету",
          f"invitem:{item_id}" in kb)
    check("снятие предмета: кнопка в рынок", "shopcat:market" in kb)
    check("снятие предмета: нет в ленте рынка",
          not any(i["id"] == offer_id for i in await market_offer_items()))

    # повторное снятие — объявления уже нет
    again = _CB(uid)
    await _cancel_offer(again, "item", offer_id)
    check("повторное снятие: «объявления уже нет»",
          any("уже нет" in (a[0] or "") for a in again.alerts))

    # ── 5. улов (рыба): возврат с замороженной свежестью ──
    fish_id = await add_item(
        name="Тестовый сиг рынка", description="тест", price=90,
        sell_price=60, rarity=1, category="fishing", stock=-1,
        added_by=uid, market_ok=1)
    weight = 1500
    await add_fish_catch(uid, fish_id, weight, kind="fish")
    taken = await take_fish_catch(uid, fish_id, weight)
    check("улов: забран для выкладки", taken is not None)
    now = int(time.time())
    rem = max(1, int(float(taken['expires_at'])) - now)
    f_offer_id = await add_fish_offer(uid, fish_id, weight, 90, rem, base_price=80)
    check("улов: объявление выставлено", await get_fish_offer(f_offer_id) is not None)

    f_own = _CB(uid, f"fishoffer:{f_offer_id}")
    await fish_offer_view(f_own)
    f_kb = cbs(f_own.message.edits[-1][1]) if f_own.message.edits else []
    check("своя карточка улова: есть «Снять с продажи»",
          any(c.startswith("offercancel:fish:") for c in f_kb))
    check("своя карточка улова: нет кнопки покупки",
          not any(c.startswith("fishbuy:") for c in f_kb))

    f_msg = _Msg()
    await _cancel_offer(_CB(uid, f"offercancel:fish:{f_offer_id}", f_msg),
                        "fish", f_offer_id)
    check("снятие улова: объявления больше нет",
          await get_fish_offer(f_offer_id) is None)
    back = await get_fish_catches(uid)
    mine = [c for c in back if c['item_id'] == fish_id and c['weight'] == weight]
    check("снятие улова: улов вернулся", len(mine) == 1)
    if mine:
        check("снятие улова: свежесть не потеряна (≤2 с удержания)",
              mine[0]['remaining_sec'] <= rem and mine[0]['remaining_sec'] > rem - 6)
        check("снятие улова: вид «рыба»", mine[0]['kind'] == 'fish')
        check("снятие улова: срок не None", mine[0]['expires_at'] is not None)
    check("снятие улова: подтверждение", "снят с продажы" in f_msg.edits[-1][0])
    check("снятие улова: кнопка к улову",
          f"fishcatch:{fish_id}:{weight}" in cbs(f_msg.edits[-1][1]))

    # ── 6. находка-ресурс: возвращается без срока порчи ──
    res_id = await add_item(
        name="Тестовая находка рынка", description="тест", price=60,
        sell_price=30, rarity=1, category="resource", stock=-1,
        added_by=uid, market_ok=1)
    await add_fish_catch(uid, res_id, 1, kind="resource")
    r_taken = await take_fish_catch(uid, res_id, 1)
    check("находка: забрана для выкладки", r_taken is not None)
    r_offer_id = await add_fish_offer(uid, res_id, 1, 45, 3600, base_price=40)
    await _cancel_offer(_CB(uid, f"offercancel:fish:{r_offer_id}"), "fish", r_offer_id)
    check("снятие находки: объявления больше нет",
          await get_fish_offer(r_offer_id) is None)
    r_back = await get_fish_catches(uid)
    r_mine = [c for c in r_back if c['item_id'] == res_id]
    check("снятие находки: вернулась в «Улов»", len(r_mine) == 1)
    if r_mine:
        check("снятие находки: не портится", r_mine[0]['expires_at'] is None)
        check("снятие находки: вид «resource»", r_mine[0]['kind'] == 'resource')

    # выкуп улова у себя тоже запрещён — объявление остаётся, потом снимается
    fid2 = await add_fish_offer(uid, fish_id, weight, 95, rem, base_price=80)
    await fish_buy(_CB(uid, f"fishbuy:{fid2}"))
    check("выкуп своего улова запрещён: объявление осталось",
          await get_fish_offer(fid2) is not None)
    await _cancel_offer(_CB(uid, f"offercancel:fish:{fid2}"), "fish", fid2)
    check("после снятия слот улова свободен",
          await get_fish_offer(fid2) is None)
    check("итог: все свои объявления сняты",
          await count_user_market_offers(uid) == 0)

    await close_db()
    print(f"\nSmoke 155: {passed} passed, {failed} failed")
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
        sys.exit(1)
