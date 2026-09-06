import os

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from database.db import add_user, get_user, ensure_base_status, user_has_status_tag
from keyboards.keyboards import main_menu_keyboard, city_keyboard
from utils.permissions import is_admin
from utils.helpers import resolve_image

router = Router()

WELCOME_PHOTO = "assets/img/ui/boot.jpg"
BOT_START_URL = "https://t.me/Nord_Wio_bot?start=nord"


@router.message(CommandStart())
async def cmd_start(message: Message):
    user = message.from_user
    await add_user(user.id, user.username or "", user.first_name or "", user.last_name or "")
    await ensure_base_status(user.id)

    admin_flag = await is_admin(user.id)
    pilot_flag = await user_has_status_tag(user.id, "pilot")

    welcome_text = (
        "```\n"
        "┌───────────────────────────────┐\n"
        "│ Н.О.Р.Д. v3.0 [ACTIVATED]    │\n"
        "│ Нордхаймский Органайзер       │\n"
        "│ Регистрации Действий          │\n"
        "└───────────────────────────────┘\n"
        "C:\\НОРД> boot_sequence_complete\n"
        ">> ДОСТУПНЫЕ ОПЕРАЦИИ:\n"
        "```"
    )

    start_markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚡ Запустить Н.О.Р.Д.", url=BOT_START_URL)],
    ])

    if os.path.isfile(WELCOME_PHOTO):
        await message.answer_photo(
            photo=FSInputFile(WELCOME_PHOTO),
            caption=welcome_text,
            reply_markup=start_markup,
            parse_mode="Markdown"
        )
    else:
        await message.answer(welcome_text, reply_markup=start_markup, parse_mode="Markdown")

    await message.answer("Выберите действие:", reply_markup=main_menu_keyboard(is_admin=admin_flag, is_pilot=pilot_flag))


@router.message(F.text == "Город")
async def show_city(message: Message):
    city_view = resolve_image("city/arkholm")
    is_here_pilot = await user_has_status_tag(message.from_user.id, "pilot")
    await message.answer_photo(
        photo=FSInputFile(city_view),
        caption="🏰 Город Аркхольм:",
        reply_markup=city_keyboard(is_pilot=is_here_pilot)
    )


@router.callback_query(F.data == "city:menu")
async def city_menu_cb(callback: CallbackQuery):
    await callback.answer()
    city_view = resolve_image("city/arkholm")
    is_here_pilot = await user_has_status_tag(callback.from_user.id, "pilot")
    if callback.message.photo:
        from aiogram.types import InputMediaPhoto
        await callback.message.edit_media(
            media=InputMediaPhoto(media=FSInputFile(city_view), caption="🏰 Город Аркхольм:"),
            reply_markup=city_keyboard(is_pilot=is_here_pilot)
        )
    else:
        await callback.message.answer_photo(
            photo=FSInputFile(city_view),
            caption="🏰 Город Аркхольм:",
            reply_markup=city_keyboard(is_pilot=is_here_pilot)
        )
