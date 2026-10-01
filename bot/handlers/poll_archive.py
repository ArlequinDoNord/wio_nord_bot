"""Архив опросов Ратуши — раздел библиотеки «Опросы».

В архив уходит всё, что не поместилось в меню голосования: там висят только
POLL_VISIBLE новейших опросов, остальные (5-е и старше) помечаются is_archived с
датой archived_day. По этой дате записи собираются по дням — «нумерация по датам»,
как в летописи: заголовок дня, под ним опросы этого дня.

Попасть сюда можно из Библиотеки (кнопка «🗳 Архив опросов Ратуши»), из карточки
закрытого опроса и из результатов архивного опроса.
"""

from datetime import datetime

from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from database.db import (
    has_library_access, count_archived_poll_days, get_archived_poll_days,
    count_archived_polls_by_day, get_archived_polls_by_day, count_archived_polls,
)
from config import POLL_ARCHIVE_DAYS_PER_PAGE, POLL_ARCHIVE_PER_DAY
from utils.permissions import is_admin, has_permission
from utils.helpers import edit_message_safe

router = Router()

# Месяцы для заголовков дней архива — по-русски, как в заголовках архива стены.
_MONTHS = {
    1: "Января", 2: "Февраля", 3: "Марта", 4: "Апреля", 5: "Мая", 6: "Июня",
    7: "Июля", 8: "Августа", 9: "Сентября", 10: "Октября", 11: "Ноября", 12: "Декабря",
}

_ARCHIVE_DENIED = (
    "🗳 Архив опросов доступен владельцам читательского билета "
    "(Библиотека, раздел «Читательские билеты» в Магазине)."
)


async def _archive_allowed(user_id: int) -> bool:
    """Доступ к архиву опросов — как к архиву новостей: админы, сотрудники ГосСМИ
    и читатели с билетом. Само голосование при этом открыто всем пилотам."""
    if await is_admin(user_id):
        return True
    if await has_permission(user_id, "can_post_news"):
        return True
    return await has_library_access(user_id)


def _day_label(day: str) -> str:
    """'2026-10-11' → '11 октября 2026'. Неразобранная дата — возвращаем как есть."""
    try:
        dt = datetime.strptime(day[:10], "%Y-%m-%d")
    except (TypeError, ValueError):
        return day or "без даты"
    return f"{dt.day} {_MONTHS.get(dt.month, dt.month)} {dt.year}"


def _plural_polls(n: int) -> str:
    """«1 опрос» / «2 опроса» / «5 опросов»."""
    n = abs(int(n))
    if n % 10 == 1 and n % 100 != 11:
        return f"{n} опрос"
    if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14:
        return f"{n} опроса"
    return f"{n} опросов"


def _days_markup(days, page: int, total_days: int):
    """Список дней архива: заголовок-день + пагинация по дням."""
    pages = max(1, (total_days + POLL_ARCHIVE_DAYS_PER_PAGE - 1) // POLL_ARCHIVE_DAYS_PER_PAGE)
    page = max(0, min(page, pages - 1))
    rows = []
    for d in days:
        n = d['cnt'] or 0
        rows.append([InlineKeyboardButton(
            text=f"📅 {_day_label(d['archived_day'])} · {_plural_polls(n)}",
            callback_data=f"pollarch:day:{d['archived_day']}"
        )])
    if pages > 1:
        nav = []
        if page > 0:
            nav.append(InlineKeyboardButton(text="◀️", callback_data=f"pollarch:days:{page - 1}"))
        nav.append(InlineKeyboardButton(text=f"{page + 1}/{pages}", callback_data="noop"))
        if page < pages - 1:
            nav.append(InlineKeyboardButton(text="▶️", callback_data=f"pollarch:days:{page + 1}"))
        rows.append(nav)
    rows.append([InlineKeyboardButton(text="🔙 В библиотеку", callback_data="lib:menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _day_polls_markup(polls, day: str, page: int, total_polls: int):
    """Опросы одного дня: кнопки на опрос (ведёт на результаты) + пагинация."""
    pages = max(1, (total_polls + POLL_ARCHIVE_PER_DAY - 1) // POLL_ARCHIVE_PER_DAY)
    page = max(0, min(page, pages - 1))
    rows = []
    for p in polls:
        question = p['question']
        short = question if len(question) <= 40 else question[:37] + "…"
        rows.append([InlineKeyboardButton(
            text=f"🔒 {short}", callback_data=f"vote:results:{p['id']}")])
    if pages > 1:
        nav = []
        if page > 0:
            nav.append(InlineKeyboardButton(
                text="◀️", callback_data=f"pollarch:day:{day}:{page - 1}"))
        nav.append(InlineKeyboardButton(text=f"{page + 1}/{pages}", callback_data="noop"))
        if page < pages - 1:
            nav.append(InlineKeyboardButton(
                text="▶️", callback_data=f"pollarch:day:{day}:{page + 1}"))
        rows.append(nav)
    rows.append([InlineKeyboardButton(text="🔙 К дням архива", callback_data="pollarch:list")])
    rows.append([InlineKeyboardButton(text="🔙 В библиотеку", callback_data="lib:menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def _denied(callback: CallbackQuery):
    await edit_message_safe(
        callback.message, _ARCHIVE_DENIED,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 В библиотеку", callback_data="lib:menu")]
        ])
    )


@router.callback_query(F.data == "pollarch:list")
async def poll_archive_list(callback: CallbackQuery):
    await callback.answer()
    if not await _archive_allowed(callback.from_user.id):
        await _denied(callback)
        return
    total_days = await count_archived_poll_days()
    if not total_days:
        await edit_message_safe(
            callback.message,
            "🗳 АРХИВ ОПРОСОВ РАТУШИ\n\n"
            "Пока пуст. В меню голосования висит только 4 новейших опроса — "
            "всё, что старше, попадает сюда, по датам.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 В библиотеку", callback_data="lib:menu")]
            ])
        )
        return
    total_polls = await count_archived_polls()
    days = await get_archived_poll_days(0, POLL_ARCHIVE_DAYS_PER_PAGE)
    await edit_message_safe(
        callback.message,
        f"🗳 АРХИВ ОПРОСОВ РАТУШИ\n"
        f"Всего {_plural_polls(total_polls)} за {total_days} дн.\n\n"
        f"Выбери день:",
        _days_markup(days, 0, total_days)
    )


@router.callback_query(F.data.regexp(r"^pollarch:days:\d+$"))
async def poll_archive_days_page(callback: CallbackQuery):
    await callback.answer()
    if not await _archive_allowed(callback.from_user.id):
        await _denied(callback)
        return
    page = int(callback.data.split(":")[2])
    total_days = await count_archived_poll_days()
    days = await get_archived_poll_days(page, POLL_ARCHIVE_DAYS_PER_PAGE)
    if not days:
        await poll_archive_list(callback)
        return
    total_polls = await count_archived_polls()
    await edit_message_safe(
        callback.message,
        f"🗳 АРХИВ ОПРОСОВ РАТУШИ\n"
        f"Всего {_plural_polls(total_polls)} за {total_days} дн.\n\n"
        f"Выбери день:",
        _days_markup(days, page, total_days)
    )


@router.callback_query(F.data.regexp(r"^pollarch:day:\d{4}-\d{2}-\d{2}(?::\d+)?$"))
async def poll_archive_day(callback: CallbackQuery):
    await callback.answer()
    if not await _archive_allowed(callback.from_user.id):
        await _denied(callback)
        return
    parts = callback.data.split(":")
    day = parts[2]
    page = int(parts[3]) if len(parts) > 3 else 0
    total = await count_archived_polls_by_day(day)
    if not total:
        await edit_message_safe(
            callback.message,
            f"🗳 {_day_label(day)}\n\nЗа этот день опросов в архиве нет.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 К дням архива", callback_data="pollarch:list")]
            ])
        )
        return
    polls = await get_archived_polls_by_day(day, page, POLL_ARCHIVE_PER_DAY)
    await edit_message_safe(
        callback.message,
        f"🗳 АРХИВ ОПРОСОВ — {_day_label(day)}\n"
        f"Выбери опрос, чтобы посмотреть итоги:",
        _day_polls_markup(polls, day, page, total)
    )
