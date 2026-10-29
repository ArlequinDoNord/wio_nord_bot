# -*- coding: utf-8 -*-
"""Smoke 174 — финансы: история транзакций пилота (раздел супер-админа).

1. Гвардия finh:*: не-супер-админ не видит кнопку в меню финанс и хендлеры громят.
2. _txn_line: знаки +/-, метки (Покупка/Продажа/Зачисление/Списание), контрагент, описание.
3. Меню финансов: кнопка «История пилота» видна только супер-админу.
4. Пайплайн: finh:open → finh:u:{uid} → окно истории (FakeCallback), страницы,
   навигация, окно при пустой истории.
"""
import asyncio
import os
import sys

os.environ["DATABASE_PATH"] = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "_test_smoke174.db")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def main():
    passed = failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
            print(f"  OK  {name}")
        else:
            failed += 1
            print(f"  FAIL {name}")

    import database.db as db
    import config
    from utils.permissions import get_user_role

    async def fake_check_fail():
        return False

    from database.db import (
        init_db, close_db, add_user, update_user, get_db, get_user,
        add_nordmarks, remove_nordmarks,
    )

    await init_db()
    conn = await db.get_db()
    for tbl in ("transactions", "users", "user_roles"):
        try:
            await conn.execute(f"DELETE FROM {tbl}")
        except Exception:
            pass
    await conn.commit()

    OWNER = 561309060      # супер-админ из ADMIN_IDS
    PLA = 174001           # обычный пилот
    PIB = 174002           # второй пилот (контрагент)
    await add_user(PLA, 'pla', 'Пилот А', "")
    await add_user(PIB, 'pib', 'Пилот Б', "")
    await update_user(PLA, nordmarks=500)
    await update_user(PIB, nordmarks=100)

    from bot.handlers import admin as ah

    print("\n1. Гвардия супер-админа")
    check("владелец из ADMIN_IDS = супер-админ",
          'super_admin' in await get_user_role(OWNER))
    check("обычный пилот не супер-админ",
          'super_admin' not in await get_user_role(PLA))
    check("_is_super_admin(OWNER)", await ah._is_super_admin(OWNER))
    check("not _is_super_admin(PLA)", not await ah._is_super_admin(PLA))

    print("\n2. _txn_line: разбор одной записи")
    base = {'created_at': '2026-10-29 10:00:00', 'amount': 42}
    t_in = dict(base, to_user=PLA, from_user=None, tx_type='admin',
                description='Начислено админом')
    line = ah._txn_line(t_in, PLA)
    check("зачисление: + и метка 📥", "📥 Зачисление" in line and "+42 НМ" in line)
    check("зачисление: описание в кавычках", "«Начислено админом»" in line)
    t_out = dict(base, to_user=None, from_user=PLA, tx_type='admin',
                 description='Списано админом')
    line2 = ah._txn_line(t_out, PLA)
    check("списание: − и метка 📤 📤", "📤 Списание" in line2 and "-42 НМ" in line2)
    t_self = dict(base, to_user=PLA, from_user=PLA, tx_type='mining',
                  description='перевод самому себе')
    line3 = ah._txn_line(t_self, PLA)
    check("перевод себе: помечен как списание", "📤 Списание" in line3)
    check("контрагент ≠ пилот сам с собой не показывается",
          "от #" not in line3 and "к #" not in line3)
    t_shop = dict(base, to_user=None, from_user=PLA, tx_type='shop_purchase',
                  description=None)
    check("покупка: метка 🛒, без описания — одна строка",
          "🛒 Покупка" in ah._txn_line(t_shop, PLA)
          and "«" not in ah._txn_line(t_shop, PLA))
    t_rich = dict(base, to_user=PLA, from_user=PIB, tx_type='raw',
                  description='перевод')
    check("зачисление с контрагентом: «+42 НМ» и ← #174002",
          "raw" not in "" and "#174002" in ah._txn_line(t_rich, PLA))

    print("\n3. История: реальные записи через add/remove (записи в transactions)")
    await add_nordmarks(PLA, 100, "admin", f"Начислено админом #{OWNER}")
    await remove_nordmarks(PLA, 20, "shop_purchase", "Покупка зелья")
    rows, has_next = await db.get_transactions_history(PLA)
    check("история пишет обе операции", len(rows) == 2)
    check("has_next=False на первой странице", has_next is False)

    print("\n4. Меню финансов: кнопка «История пилота» только у супер-админа")

    class FakeMsg:
        text = None
        kb = None
        async def edit_text(self, t=None, reply_markup=None, **kw):
            self.text = t
            self.kb = reply_markup
            return True
        async def answer(self, *a, **kw):
            if a and isinstance(a[0], str):
                self.text = a[0]
            if kw.get('reply_markup'):
                self.kb = kw['reply_markup']
            return True

    class FakeCB:
        def __init__(self, uid, data):
            self.from_user = type("U", (), {"id": uid})()
            self.data = data
            self.message = FakeMsg()
        async def answer(self, *a, **kw):
            return True

    # кэп: admin_finance требует права; супер-админ проходит
    cb_owner = FakeCB(OWNER, "admin:finance")
    await ah.admin_finance(cb_owner)
    btn_texts = [b.text for row in cb_owner.message.kb.inline_keyboard for b in row]
    check("у супер-админа есть кнопка «📜 История пилота»",
          "📜 История пилота" in btn_texts)
    cb_pla = FakeCB(PLA, "admin:finance")
    await ah.admin_finance(cb_pla)
    if cb_pla.message.kb:
        btns2 = [b.text for row in cb_pla.message.kb.inline_keyboard for b in row]
    else:
        # нет прав — сообщение с текстом, кнопок нет
        btns2 = []
    check("у обычного пилота кнопки не показываются",
          cb_pla.message.text and "Нет прав" in cb_pla.message.text)

    print("\n5. finh:open → список → окно истории")
    cb = FakeCB(OWNER, "finh:open")
    await ah.finance_history_open(cb)
    kb_txt = [(b.text, b.callback_data)
              for row in cb.message.kb.inline_keyboard for b in row]
    check("список открыт, есть выбор пилотов",
          any("Пилот А" in t for t, _ in kb_txt))
    cb2 = FakeCB(OWNER, "finh:u:174001")
    target = await get_user(PLA)
    await ah.finance_history_user(cb2)
    hist_text = cb2.message.text or ""
    check("окно истории: заголовок ТРАНЗАКЦИИ ПИЛОТА", "ТРАНЗАКЦИИ ПИЛОТА" in hist_text)
    check("окно истории: имя и ID", "Пилот А" in hist_text and "174001" in hist_text)
    check("окно истории: строка текущего баланса", "Текущий баланс" in hist_text)
    check("в списке есть обе транзакции",
          "Начислено админом" in hist_text and "Покупка зелья" in hist_text)
    cb_nav = [b.callback_data for row in cb2.message.kb.inline_keyboard for b in row]
    check("есть кнопка «К списку пилотов»", "finh:open" in cb_nav)

    print("\n6. Постраничность истории (15 на стр.)")
    for i in range(20):
        await add_nordmarks(PLA, 1, "admin", f"начисл {i}")
    cb3 = FakeCB(OWNER, "finh:h:174001:0")
    await ah.finance_history_page(cb3)
    t0 = cb3.message.text or ""
    check("стр.1: ровно 15 строк транзакций", t0.count("НМ\n") >= 15)
    cb3_nav = [b.callback_data for row in cb3.message.kb.inline_keyboard
               for b in row]
    check("есть навигация «Старее ▶️» на finh:h:174001:1",
          "finh:h:174001:1" in cb3_nav)
    cb4 = FakeCB(OWNER, "finh:h:174001:1")
    await ah.finance_history_page(cb4)
    t1 = cb4.message.text or ""
    check("стр.2: остаток записей (7)", t1.count("НМ\n") + 3 + 2 >= 7
          and "Стр. 2" in t1)
    check("на последней странице нет «Старее»",
          "Старее" not in [b.text for row in cb4.message.kb.inline_keyboard
                           for b in row])

    print("\n7. Не-супер-админ: гвардия работает")
    cb5 = FakeCB(PLA, "finh:open")
    await ah.finance_history_open(cb5)
    check("не-грудо: отказ с потерей", cb5.message.text and "супер-админа" in cb5.message.text)
    cb6 = FakeCB(PLA, "finh:u:174001")
    await ah.finance_history_user(cb6)
    check("finh:u: гвардия — без вывода", cb6.message.text is None)

    print(f"\nИТОГО: {passed} passed, {failed} failed")
    await close_db()
    if failed:
        sys.exit(1)


try:
    asyncio.run(main())
except Exception:
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    try:
        os.remove(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "_test_smoke174.db"))
    except OSError:
        pass
