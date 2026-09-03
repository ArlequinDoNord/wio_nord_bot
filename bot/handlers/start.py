from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from database.db import add_user, get_user
from keyboards.keyboards import main_menu_keyboard
from utils.permissions import is_admin

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    user = message.from_user
    await add_user(user.id, user.username or "", user.first_name or "", user.last_name or "")

    admin_flag = await is_admin(user.id)

    await message.answer(
        f"Добро пожаловать в Нордхайм, {user.first_name}!\n\n"
        "Ты — пилот в мире воздушных боёв.\n"
        "Получай войск за отчёты, покупай снаряжение,\n"
        "прокачивайся и сражайся!\n\n"
        "Используй меню ниже для навигации:",
        reply_markup=main_menu_keyboard(is_admin=admin_flag)
    )


@router.message(F.text == "Город")
async def show_city(message: Message):
    await message.answer("Город Аркхольм:")
