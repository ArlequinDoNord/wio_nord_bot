# -*- coding: utf-8 -*-
"""Smoke 202 — базовый английский интерфейс.

1. По умолчанию русский; t() без языка отдаёт русский текст.
2. Язык хранится в users.lang: новый пилот — ru, переключение сохраняется.
3. LangMiddleware выставляет язык пилота на время обработки.
4. Главное меню на английском содержит кнопки и переключатель языка.
5. Кнопки обоих языков понимают фильтры и FSM-защита (MAIN_MENU_TEXTS).
6. Подписи города и меню отчётов переведены.
"""
import asyncio
import os
import sys

from tests_support import Checker, use_test_db

_TEST_DB = use_test_db(__file__, "smoke202")


class _User:
    def __init__(self, uid):
        self.id = uid


async def main():
    check = Checker()

    import database.db as db
    from database.db import init_db, close_db, add_user, get_user, get_user_lang, set_user_lang
    from utils.i18n import (t, btn_labels, all_button_labels, use_lang, LangMiddleware,
                            current_lang)
    from utils.helpers import MAIN_MENU_TEXTS
    from keyboards.keyboards import main_menu_keyboard

    await init_db()
    UID = 202001
    await add_user(UID, "en_test", "Тест", "")

    print("\n1. Язык по умолчанию")
    check("новый пилот — ru", await get_user_lang(UID) == "ru")
    use_lang("ru")
    check("t() по умолчанию — русский", t("btn.profile") == "Профиль")
    check("неизвестный ключ возвращается как есть", t("no.such.key") == "no.such.key")

    print("\n2. Переключение сохраняется")
    await set_user_lang(UID, "en")
    check("после set — en", await get_user_lang(UID) == "en")
    try:
        await set_user_lang(UID, "de")
        check("неподдерживаемый язык отклоняется", False)
    except ValueError:
        check("неподдерживаемый язык отклоняется", True)
    check("язык не сломал существующие поля пилота",
          (await get_user(UID))["first_name"] == "Тест")

    print("\n3. LangMiddleware")
    seen = {}

    async def handler(event, data):
        seen["label"] = t("btn.profile")
        return seen["label"]

    mw = LangMiddleware()
    await mw.__call__(handler, object(), {"event_from_user": _User(UID)})
    check("для en-пилота обработчик видит English", seen["label"] == "Profile")
    await mw.__call__(handler, object(), {"event_from_user": _User(UID + 999)})
    check("неизвестный пользователь — русский", seen["label"] == "Профиль")
    check("после обработки язык вернулся к прежнему", current_lang() == "ru")

    print("\n4. Клавиатура главного меню")
    use_lang("en")
    kb = main_menu_keyboard(is_admin=True)
    labels = [b.text for row in kb.keyboard for b in row]
    check("кнопка «Profile»", "Profile" in labels)
    check("кнопка «City»", "City" in labels)
    check("переключатель «🌐 Русский» в англ. меню", "🌐 Русский" in labels)
    check("админ-кнопка переведена", "👑 Admin panel" in labels)
    use_lang("ru")
    labels_ru = [b.text for row in main_menu_keyboard().keyboard for b in row]
    check("русское меню не изменилось", "Профиль" in labels_ru and "🌐 English" in labels_ru)

    print("\n5. Фильтры и FSM-защита понимают обе надписи")
    check("btn_labels(profile) содержит оба языка",
          set(btn_labels("btn.profile")) == {"Профиль", "Profile"})
    check("«Profile» в MAIN_MENU_TEXTS", "Profile" in MAIN_MENU_TEXTS)
    check("«🌐 English» в MAIN_MENU_TEXTS", "🌐 English" in MAIN_MENU_TEXTS)
    check("все надписи входят в all_button_labels", "Inventory" in all_button_labels())

    print("\n6. Город и отчёты")
    use_lang("en")
    check("заголовок города по-английски", t("city.caption").startswith("🏰 City of Arkholm"))
    from bot.handlers.reports import _report_menu_text
    text = await _report_menu_text(UID)
    check("меню отчётов по-английски", text.startswith("📋 Report menu"))
    check("счётчик отчётов по-английски", "Reports left today" in text)
    use_lang("ru")
    check("меню отчётов по-русски", (await _report_menu_text(UID)).startswith("📋 Меню отчётов"))

    failed = check.summary()
    await close_db()
    return failed


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
