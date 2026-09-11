"""Ратуша: общественный центр города — разделы «Голосование» и «Пилоты города»."""

import os

from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton

from database.db import get_all_users, get_user, get_selected_status, can_enter_location
from config import get_effective_rank
from utils.helpers import resolve_image

router = Router()


def town_hall_markup() -> InlineKeyboardMarkup:
    """Главное меню Ратуши: разделы."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🗳️ Голосование и опросы", callback_data="city:vote")],
        [InlineKeyboardButton(text="🪖 Пилоты города", callback_data="city:pilots:list")],
        [InlineKeyboardButton(text="🔙 В город", callback_data="city:menu")],
    ])


def pilots_list_markup(users) -> InlineKeyboardMarkup:
    buttons = []
    for u in users:
        name = (u['first_name'] + " " + (u['last_name'] or "")).strip()
        buttons.append([InlineKeyboardButton(
            text=f"🪖 {name}",
            callback_data=f"rathaus:{u['user_id']}"
        )])
    buttons.append([InlineKeyboardButton(text="🔙 В Ратушу", callback_data="city:pilots")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def _show_hall(callback: CallbackQuery):
    """Показать главное меню Ратуши (переписывает текущее сообщение)."""
    hall_view = resolve_image("city/rathaus")
    caption = "🏛️ РАТУША НОРДХАЙМА\n\nЗдесь собираются пилоты, проходят голосования и решаются вопросы города."
    if os.path.isfile(hall_view):
        if callback.message.photo:
            from aiogram.types import InputMediaPhoto
            await callback.message.edit_media(
                media=InputMediaPhoto(media=FSInputFile(hall_view), caption=caption),
                reply_markup=town_hall_markup()
            )
        else:
            await callback.message.answer_photo(
                photo=FSInputFile(hall_view),
                caption=caption,
                reply_markup=town_hall_markup()
            )
    else:
        await callback.message.edit_text(caption, reply_markup=town_hall_markup())


@router.callback_query(F.data == "city:pilots")
async def town_hall_menu(callback: CallbackQuery):
    await callback.answer()
    if not await can_enter_location(callback.from_user.id, "townhall"):
        await callback.message.answer("🍺 Ты пьян! В Ратушу не пускают. Протрезвей сначала.")
        return
    await _show_hall(callback)


@router.callback_query(F.data == "city:pilots:list")
async def town_hall_pilots_list(callback: CallbackQuery):
    await callback.answer()
    users = await get_all_users()
    if not users:
        text = "🪖 ПИЛОТЫ ГОРОДА\n\nПока никого нет — загляни позже!"
        if callback.message.photo:
            await callback.message.edit_caption(
                caption=text,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 В Ратушу", callback_data="city:pilots")]
                ])
            )
        else:
            await callback.message.edit_text(
                text,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 В Ратушу", callback_data="city:pilots")]
                ])
            )
        return

    users = sorted(users, key=lambda u: (u['first_name'] or "").lower())
    text = "🪖 ПИЛОТЫ ГОРОДА (по алфавиту):"
    if callback.message.photo:
        await callback.message.edit_caption(caption=text, reply_markup=pilots_list_markup(users))
    else:
        await callback.message.edit_text(text, reply_markup=pilots_list_markup(users))


@router.callback_query(F.data.startswith("rathaus:"))
async def town_hall_pilot_card(callback: CallbackQuery):
    await callback.answer()
    user_id = int(callback.data.split(":")[1])
    user = await get_user(user_id)
    if not user:
        await callback.message.answer("❌ Пилот не найден.")
        return

    name = (user['first_name'] + " " + (user['last_name'] or "")).strip()
    rank = get_effective_rank(user['troops'], user['promoted_rank'] if 'promoted_rank' in user.keys() else None)
    selected = await get_selected_status(user_id)
    status = selected['name'] if selected else "—"

    text = (
        f"🪖 {name}\n"
        f"────────────────\n"
        f"Позывной: @{user['username'] or '—'}\n"
        f"⭐ Звание: {rank}\n"
        f"🎖️ Статус: {status}\n"
    )

    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 К пилотам", callback_data="city:pilots:list")]
    ])
    if callback.message.photo:
        await callback.message.edit_caption(caption=text, reply_markup=markup)
    else:
        await callback.message.edit_text(text, reply_markup=markup)