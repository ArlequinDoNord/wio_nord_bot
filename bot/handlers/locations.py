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
from utils.helpers import resolve_image

router = Router()


@router.callback_query(F.data.startswith("location:preview:"))
async def location_preview(callback: CallbackQuery):
    await callback.answer()
    key = callback.data.split(":", 2)[2]
    loc = await get_location_by_key(key)
    if not loc:
        await callback.message.answer("❌ Локация не найдена.")
        return

    access_label = await location_access_label(loc['access_mode'], loc['required_status'])
    text = (
        f"📍 {loc['name']}\n"
        f"────────────────\n"
        f"{loc['description'] or ''}\n\n"
        f"Доступ: {access_label}"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔑 Войти", callback_data=f"location:enter:{key}")],
        [InlineKeyboardButton(text="🔙 В город", callback_data="city:menu")],
    ])

    photo = None
    if 'preview_photo' in loc.keys() and loc['preview_photo']:
        candidate = resolve_image(loc['preview_photo'])
        if candidate and os.path.isfile(candidate):
            photo = candidate
    if photo:
        await callback.message.answer_photo(
            photo=FSInputFile(photo),
            caption=text,
            reply_markup=kb
        )
    else:
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

    # Передаём управление специфическому функционалу локации
    if key == "townhall":
        from bot.handlers.pilots import town_hall_menu
        await town_hall_menu(callback)
    elif key == "library":
        from bot.handlers.library import library_enter
        await library_enter(callback)
    else:
        await callback.message.answer(
            f"📍 {loc['name']}\nДоступ разрешён. Функционал этой локации ещё в разработке."
        )
