from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from database.db import add_user, get_user, ensure_base_status
from keyboards.keyboards import main_menu_keyboard
from utils.permissions import is_admin

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    user = message.from_user
    await add_user(user.id, user.username or "", user.first_name or "", user.last_name or "")
    await ensure_base_status(user.id)

    admin_flag = await is_admin(user.id)

    await message.answer(
        "```\n"
        "┌───────────────────────────────┐\n"
        "│ Н.О.Р.Д. v3.0 [ACTIVATED]    │\n"
        "│ Нордхаймский Органайзер       │\n"
        "│ Регистрации Действий          │\n"
        "└───────────────────────────────┘\n"
        "C:\\НОРД> boot_sequence_complete\n"
        ">> ДОСТУПНЫЕ ОПЕРАЦИИ:\n"
        "```",
        reply_markup=main_menu_keyboard(is_admin=admin_flag),
        parse_mode="Markdown"
    )


@router.message(F.text == "Город")
async def show_city(message: Message):
    from keyboards.keyboards import city_keyboard
    await message.answer("Город Аркхольм:", reply_markup=city_keyboard())
