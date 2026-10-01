"""Ратуша: общественный центр города — голосование, пилоты, партии, речь представителя."""

import os

from datetime import datetime

from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton

from database.db import (get_all_users, get_user, can_enter_location, count_visible_active_polls,
                         maintain_polls,
                         get_user_voted_polls_count, log_location_visit,
                         user_is_tourist, users_with_top_status_tag)
from config import get_effective_rank
from utils.helpers import resolve_image, MOSCOW_TZ

router = Router()


def town_hall_markup(voted: int = 0, active: int = 0) -> InlineKeyboardMarkup:
    """Главное меню Ратуши: разделы. voted/active — счётчик «Голосования и опросы»
    (участие/активные). «Обращение Представителя» видно всем: прочитать обращение
    может любой гость Ратуши, а писать и править — только представитель."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"🗳️ Голосование и опросы {voted}/{active}", callback_data="city:vote")],
        [InlineKeyboardButton(text="🪖 Пилоты города", callback_data="city:pilots:list")],
        [InlineKeyboardButton(text="⚜️ Партии и кланы", callback_data="city:clans")],
        [InlineKeyboardButton(text="📢 Обращение Представителя", callback_data="rep:speech")],
        [InlineKeyboardButton(text="🔙 В город", callback_data="city:menu")],
    ])


PILOTS_PER_PAGE = 12


def pilots_list_markup(users, tourists=frozenset(), page: int = 0,
                       pages: int = 1) -> InlineKeyboardMarkup:
    """Список пилотов страницей: туристы (🎫) вверху, ниже — граждане."""
    buttons = []
    for u in users:
        name = (u['first_name'] + " " + (u['last_name'] or "")).strip()
        # 🎫 — пилот пока турист (гость): гражданства Нордхайма ещё нет.
        if u['user_id'] in tourists:
            name += " 🎫"
        buttons.append([InlineKeyboardButton(
            text=f"🪖 {name}",
            callback_data=f"rathaus:{u['user_id']}"
        )])
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="⬅️", callback_data=f"city:pilots:list:{page - 1}"))
    nav.append(InlineKeyboardButton(text=f"Стр. {page + 1}/{pages}", callback_data="noop"))
    if page < pages - 1:
        nav.append(InlineKeyboardButton(text="➡️", callback_data=f"city:pilots:list:{page + 1}"))
    if nav:
        buttons.append(nav)
    buttons.append([InlineKeyboardButton(text="🔙 В Ратушу", callback_data="city:pilots")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def _pilots_sorted(users, tourists) -> list:
    """Туристы (гости) всегда в начале списка; внутри групп — по алфавиту."""
    return sorted(
        users,
        key=lambda u: (u['user_id'] not in tourists, (u['first_name'] or "").lower())
    )


async def _show_hall(callback: CallbackQuery):
    """Показать главное меню Ратуши (переписывает текущее сообщение)."""
    hall_view = resolve_image("city/rathaus")
    clock = datetime.now(MOSCOW_TZ).strftime("%H:%M")
    caption = (
        "🏛️ РАТУША НОРДХАЙМА\n\n"
        "Здесь собираются пилоты, проходят голосования и решаются вопросы города.\n\n"
        f"🕰 На башенных часах сейчас {clock}."
    )
    voted = await get_user_voted_polls_count(callback.from_user.id)
    # Счётчик на кнопке голосования должен совпадать с меню (там максимум
    # POLL_VISIBLE новейших), поэтому обслуживаем опросы и здесь лениво.
    await maintain_polls()
    active = await count_visible_active_polls()
    if os.path.isfile(hall_view):
        if callback.message.photo:
            from aiogram.types import InputMediaPhoto
            await callback.message.edit_media(
                media=InputMediaPhoto(media=FSInputFile(hall_view), caption=caption),
                reply_markup=town_hall_markup(voted, active)
            )
        else:
            await callback.message.answer_photo(
                photo=FSInputFile(hall_view),
                caption=caption,
                reply_markup=town_hall_markup(voted, active)
            )
    else:
        await callback.message.edit_text(caption, reply_markup=town_hall_markup(voted, active))


@router.callback_query(F.data == "city:pilots")
async def town_hall_menu(callback: CallbackQuery):
    await callback.answer()
    if not await can_enter_location(callback.from_user.id, "townhall"):
        await callback.message.answer("🍺 Ты пьян! В Ратушу не пускают. Протрезвей сначала.")
        return
    await log_location_visit(callback.from_user.id, "townhall")
    await _show_hall(callback)


async def _render_hall_context(callback: CallbackQuery, caption: str, markup: InlineKeyboardMarkup):
    """Переписать сообщение с контекстом Ратуши. Если текущее сообщение — с фото
    (например, аватар профиля другого пилота), фото заменяется на вид Ратуши,
    чтобы чужой аватар не «наезжал» на карточку/список следующего пилота."""
    hall_view = resolve_image("city/rathaus")
    if callback.message.photo and os.path.isfile(hall_view):
        from aiogram.types import InputMediaPhoto
        await callback.message.edit_media(
            media=InputMediaPhoto(media=FSInputFile(hall_view), caption=caption),
            reply_markup=markup,
        )
    elif callback.message.photo:
        await callback.message.edit_caption(caption=caption, reply_markup=markup)
    else:
        await callback.message.edit_text(caption, reply_markup=markup)


@router.callback_query(F.data == "city:pilots:list")
async def town_hall_pilots_list(callback: CallbackQuery):
    await callback.answer()
    await _pilots_list_page(callback, 0)


@router.callback_query(F.data.startswith("city:pilots:list:"))
async def town_hall_pilots_page(callback: CallbackQuery):
    await callback.answer()
    try:
        page = int(callback.data.split(":")[3])
    except (ValueError, IndexError):
        page = 0
    await _pilots_list_page(callback, page)


async def _pilots_list_page(callback: CallbackQuery, page: int):
    users = await get_all_users()
    if not users:
        text = "🪖 ПИЛОТЫ ГОРОДА\n\nПока никого нет — загляни позже!"
        await _render_hall_context(
            callback, text,
            InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 В Ратушу", callback_data="city:pilots")]
            ])
        )
        return

    tourists = await users_with_top_status_tag("tourist")
    users = _pilots_sorted(users, tourists)
    total = len(users)
    pages = max(1, (total + PILOTS_PER_PAGE - 1) // PILOTS_PER_PAGE)
    page = max(0, min(page, pages - 1))
    chunk = users[page * PILOTS_PER_PAGE:(page + 1) * PILOTS_PER_PAGE]

    header = ["🪖 ПИЛОТЫ ГОРОДА"]
    if tourists:
        header.append("")
        header.append("Туристы (🎫) — в начале списка, ниже граждане.")
    header.append("")
    header.append("🎫 — ещё турист (гость): гражданства Нордхайма пока нет.")
    await _render_hall_context(callback, "\n".join(header),
                               pilots_list_markup(chunk, tourists, page, pages))


@router.callback_query(F.data.startswith("rathaus:"))
async def town_hall_pilot_card(callback: CallbackQuery):
    user_id = int(callback.data.split(":")[1])
    user = await get_user(user_id)
    if not user:
        await callback.message.answer("❌ Пилот не найден.")
        return

    name = (user['first_name'] + " " + (user['last_name'] or "")).strip()
    rank = get_effective_rank(user['troops'], user['promoted_rank'] if 'promoted_rank' in user.keys() else None)

    # Краткая карточка: только имя и звание. Фото, позывной, статус и «О себе» —
    # в полном профиле («👤 Открыть профиль»).
    text = (
        f"🪖 {name}\n"
        f"────────────────\n"
        f"⭐ Звание: {rank}\n"
    )

    # Пилот-турист (гость): старший статус — «Турист», гражданства пока нет.
    if await user_is_tourist(user_id):
        text += "🎫 Статус: Турист — гость, гражданства Нордхайма пока нет\n"

    # Видимость профиля: если владелец скрыл его (VIP-настройка) — кнопка открытия не показывается.
    public = bool(user['profile_public'] if 'profile_public' in user.keys() else 1)
    buttons = []
    if public:
        buttons.append([InlineKeyboardButton(
            text="👤 Открыть профиль",
            callback_data=f"rathaus_prof:{user_id}"
        )])
    else:
        text += f"\n🔒 Профиль скрыт владельцем.\n"
    buttons.append([InlineKeyboardButton(text="🔙 К пилотам", callback_data="city:pilots:list")])
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)

    await _render_hall_context(callback, text, markup)


@router.callback_query(F.data.startswith("rathaus_prof:"))
async def town_hall_open_profile(callback: CallbackQuery):
    await callback.answer()
    user_id = int(callback.data.split(":")[1])
    user = await get_user(user_id)
    if not user:
        await callback.message.answer("❌ Пилот не найден.")
        return

    if not bool(user['profile_public'] if 'profile_public' in user.keys() else 1):
        await callback.message.answer("🔒 Пилот скрыл свой профиль.")
        return

    from .profile import render_other_profile
    await render_other_profile(callback.message, user_id)