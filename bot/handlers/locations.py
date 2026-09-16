"""Универсальные локации города: превью (всем) + вход (по доступу).

Превью локации (картинка + описание) доступно всем, даже пьяным.
Вход в локацию проверяет статусный режим (all/min/exact) и блокирующие
состояния, а также специфичные условия самой локации (например,
читательский билет в Библиотеке).
"""

import os

from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton

from database.db import get_location_by_key, can_enter_location, location_access_label
from utils.helpers import resolve_image, time_of_day_key
from utils.permissions import has_permission, is_admin

router = Router()


@router.callback_query(F.data.startswith("location:preview:"))
async def location_preview(callback: CallbackQuery):
    await callback.answer()
    key = callback.data.split(":", 2)[2]
    loc = await get_location_by_key(key)
    if not loc:
        await callback.message.answer("❌ Локация не найдена.")
        return

    if key == "gossmi":
        access_line = "🎙 Вход: только сотрудники ГосСМИ (журналист / редактор)"
    else:
        access_label = await location_access_label(loc['access_mode'], loc['required_status'])
        access_line = f"Доступ: {access_label}"
    text = (
        f"📍 {loc['name']}\n"
        f"────────────────\n"
        f"{loc['description'] or ''}\n\n"
        f"{access_line}"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔑 Войти", callback_data=f"location:enter:{key}")],
        [InlineKeyboardButton(text="🔙 В город", callback_data="city:menu")],
    ])

    photo = None
    # Приоритет: file_id по текущему времени суток → asset-ключ (resolve_image) → единый file_id
    tod = time_of_day_key()
    keys = loc.keys()
    for slot in (f"photo_{tod}", "photo_dawn", "photo_day", "photo_sunset", "photo_night"):
        if slot in keys and loc[slot]:
            photo = loc[slot]
            break
    if not photo and 'preview_photo' in keys and loc['preview_photo']:
        candidate = resolve_image(loc['preview_photo'])
        if os.path.isfile(candidate):
            photo = FSInputFile(candidate)
        elif not loc['preview_photo'].startswith("city/"):
            photo = loc['preview_photo']
    if photo:
        try:
            await callback.message.answer_photo(
                photo=photo,
                caption=text,
                reply_markup=kb
            )
            return
        except Exception:
            pass
    await callback.message.answer(text, reply_markup=kb)


@router.callback_query(F.data.startswith("location:enter:"))
async def location_enter(callback: CallbackQuery):
    await callback.answer()
    key = callback.data.split(":", 2)[2]
    loc = await get_location_by_key(key)
    if not loc:
        await callback.message.answer("❌ Локация не найдена.")
        return

    if not await can_enter_location(callback.from_user.id, key):
        await callback.message.answer(
            f"⛔ Нет доступа в «{loc['name']}».\n"
            f"Убедись, что твой статус соответствует требованию и ты не в состоянии, "
            f"которое блокирует вход."
        )
        return

    # ГосСМИ: войти могут только сотрудники (журналист/редактор) и администрация.
    # Кнопка «Войти» видна всем, но остальные получают предупреждение.
    if key == "gossmi":
        actor = callback.from_user.id
        if not (await is_admin(actor) or await has_permission(actor, "can_post_news")):
            await callback.message.answer(
                f"⛔ Вход в здание «{loc['name']}» — только для сотрудников медиацентра.\n\n"
                f"Обычным жителям Нордхайма внутрь попасть нельзя. Свежие выпуски "
                f"новостей читай в главном меню — «📰 Новости Нордхайма».",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 В город", callback_data="city:menu")]
                ])
            )
            return

    # Передаём управление специфическому функционалу локации
    if key == "townhall":
        from bot.handlers.pilots import town_hall_menu
        await town_hall_menu(callback)
    elif key == "library":
        from bot.handlers.library import library_enter
        await library_enter(callback)
    elif key == "park":
        from bot.handlers.park import park_enter
        await park_enter(callback)
    elif key == "bank":
        from bot.handlers.bank import bank_menu_cb
        await bank_menu_cb(callback)
    elif key == "gossmi":
        from bot.handlers.news import news_tab
        await news_tab(callback.message, user_id=callback.from_user.id)
    elif key == "kvp":
        from bot.handlers.kvp import kvp_menu_cb
        await kvp_menu_cb(callback)
