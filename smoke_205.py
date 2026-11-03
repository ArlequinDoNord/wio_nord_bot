# -*- coding: utf-8 -*-
"""Smoke 205 — интерфейс штрафов: банк, админка, блокировка, оба языка.

1. Блокировка должника: текст на ru и en, пока есть неоплаченный штраф.
2. Банк: кнопка «Штрафы» есть на обоих языках.
3. Админка: кнопка «Штрафы» только при флаге супер-админа.
4. Оплата: коды результата для текстов (paid_full / paid_part / no_money).
5. Уведомления о списании переводятся по языку пилота (t_user).
"""
import asyncio
import sys

from tests_support import Checker, use_test_db

_TEST_DB = use_test_db(__file__, "smoke205")


async def main():
    check = Checker()

    import database.db as db
    from database.db import (init_db, close_db, add_user, update_user, set_user_lang,
                             create_fine, fines_block_text, pay_fine)
    from utils.i18n import t, t_user, use_lang
    from keyboards.keyboards import bank_keyboard, admin_panel_keyboard

    await init_db()
    U = 205001
    await add_user(U, "ui", "Штраф", "")
    await update_user(U, nordmarks=300)

    print("\n1. Блокировка должника")
    check("без штрафов — покупки открыты", await fines_block_text(U) is None)
    fid = await create_fine(U, 100, "тест", 1)
    use_lang("ru")
    ru = await fines_block_text(U)
    check("ru: текст блокировки на русском", ru and "неоплаченный штраф" in ru)
    use_lang("en")
    en = await fines_block_text(U)
    check("en: текст блокировки на английском", en and "unpaid fine" in en)
    use_lang("ru")

    print("\n2. Кнопка в банке")
    use_lang("ru")
    ru_btns = [b.text for row in bank_keyboard().inline_keyboard for b in row]
    check("ru: «⚖️ Штрафы» в банке", "⚖️ Штрафы" in ru_btns)
    use_lang("en")
    en_btns = [b.text for row in bank_keyboard().inline_keyboard for b in row]
    check("en: «⚖️ Fines» в банке", "⚖️ Fines" in en_btns)
    use_lang("ru")

    print("\n3. Кнопка в админ-панели только для супер-админа")
    check("без флага кнопки штрафов нет",
          "fines:menu" not in str(admin_panel_keyboard({})))
    check("с флагом кнопка есть",
          "fines:menu" in str(admin_panel_keyboard({"can_issue_fines": True})))

    print("\n4. Коды результата оплаты")
    big = await create_fine(U, 1000, "крупный", 1)
    ok, code, taken = await pay_fine(U, big, 500)
    check("больше баланса — no_money", not ok and code == "no_money")
    from database.db import cancel_fine
    await cancel_fine(big)
    ok, code, taken = await pay_fine(U, fid, 40)
    check("частичная — paid_part", ok and code == "paid_part" and taken == 40)
    ok, code, taken = await pay_fine(U, fid)
    check("остаток — paid_full", ok and code == "paid_full" and taken == 60)
    check("после полной оплаты блокировки нет", await fines_block_text(U) is None)

    print("\n5. Уведомления по языку пилота")
    fid2 = await create_fine(U, 50, "reason-x", 1)
    await set_user_lang(U, "en")
    msg_en = await t_user(U, "fine.charged", taken=5, left=45, reason="reason-x")
    check("en-пилот получает английское уведомление", "NM was taken" in msg_en)
    await set_user_lang(U, "ru")
    msg_ru = await t_user(U, "fine.charged", taken=5, left=45, reason="reason-x")
    check("ru-пилот получает русское уведомление", "списано 5 НМ" in msg_ru)

    failed = check.summary()
    await close_db()
    return failed


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
