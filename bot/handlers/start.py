import os

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from database.db import (add_user, get_user, ensure_base_status, user_has_status_tag,
                         get_all_locations, get_active_run, finalize_run_for)
from keyboards.keyboards import main_menu_keyboard, city_keyboard
from utils.permissions import is_admin, has_permission
from utils.helpers import resolve_image
from config import VERSION, VERSION_NOTES

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
        "Версия сборки: "
        f"{VERSION}\n\n"
        ">> Что нового:\n"
        f"{VERSION_NOTES}\n"
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


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "📚 СПРАВОЧНИК Н.О.Р.Д.\n"
        "Нордхаймский Органайзер Регистрации Действий\n\n"
        "⚙️ КОМАНДЫ:\n"
        "/start — вход в систему и главное меню\n"
        "/profile — твой профиль (звание, войска, валюта, экипировка)\n"
        "/shop — магазин товаров\n"
        "/help — этот справочник\n\n"
        "🗺️ ИГРА ИДЁТ ЧЕРЕЗ ГЛАВНОЕ МЕНЮ:\n"
        "Профиль — данные пилота, звание, статус, экипировка\n"
        "Инвентарь — твои предметы, передача и использование\n"
        "Магазин — покупка товаров за Нордмарки и ОД\n"
        "Город — локации: Ратуша, Библиотека, Банк (счета, переводы, казна) и другие\n"
        "📝 Сдать отчёт — отчёт о войсках (только для Пилота)\n\n"
        "👑 Админ-панель — управление (для администраторов)\n\n"
        "Туристам доступен ограниченный функционал. Статус «Пилот» выдаётся администраторами после проверки."
    )


@router.message(F.text == "Город")
async def show_city(message: Message, state: FSMContext):
    left_note = await _abandon_active_run_if_left(message.from_user.id, state)
    city_view = resolve_image("city/arkholm")
    is_here_pilot = await user_has_status_tag(message.from_user.id, "pilot")
    locations = await get_all_locations()
    can_orders = (await has_permission(message.from_user.id, "can_send_orders")
                  or await has_permission(message.from_user.id, "can_wing_commands"))
    if left_note:
        await message.answer(left_note)
    await message.answer_photo(
        photo=FSInputFile(city_view),
        caption="🏰 Город Аркхольм:",
        reply_markup=city_keyboard(is_pilot=is_here_pilot, locations=locations,
                                   can_send_orders=can_orders)
    )


async def _abandon_active_run_if_left(user_id: int, state: FSMContext) -> str | None:
    """Если пилот зашёл в город из подземелья — забег завершается:
    лут переносится в инвентарь, FSM подземелья сбрасывается.
    Возвращает текст о вынесенном луте (или None, если забега не было)."""
    run = await get_active_run(user_id)
    if run is None:
        return None
    items, loot_nm = await finalize_run_for(user_id, run['id'], "dungeon_left_to_city",
                                            "Покинул подземелье, уйдя в город",
                                            loot_nm=run.get('loot_nm') or 0)
    try:
        await state.clear()
    except Exception:
        pass
    parts = []
    if loot_nm:
        parts.append(f"💰 {loot_nm} Нордмарок")
    for name, qty in items or []:
        parts.append(f"🎁 {name} x{qty}")
    if parts:
        return "⚙️ Ты вышел из подземелья — забег завершён. Вынесено:\n" + "\n".join(parts)
    return "⚙️ Ты вышел из подземелья — забег завершён."


@router.callback_query(F.data == "city:menu")
async def city_menu_cb(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    left_note = await _abandon_active_run_if_left(callback.from_user.id, state)
    city_view = resolve_image("city/arkholm")
    is_here_pilot = await user_has_status_tag(callback.from_user.id, "pilot")
    locations = await get_all_locations()
    can_orders = (await has_permission(callback.from_user.id, "can_send_orders")
                  or await has_permission(callback.from_user.id, "can_wing_commands"))
    if left_note:
        await callback.message.answer(left_note)
    if callback.message.photo:
        from aiogram.types import InputMediaPhoto
        await callback.message.edit_media(
            media=InputMediaPhoto(media=FSInputFile(city_view), caption="🏰 Город Аркхольм:"),
            reply_markup=city_keyboard(is_pilot=is_here_pilot, locations=locations,
                                       can_send_orders=can_orders)
        )
    else:
        await callback.message.answer_photo(
            photo=FSInputFile(city_view),
            caption="🏰 Город Аркхольм:",
            reply_markup=city_keyboard(is_pilot=is_here_pilot, locations=locations,
                                       can_send_orders=can_orders)
        )
