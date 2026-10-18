from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from config import REPORT_ARCHIVE_PAGE
from database.db import (
    count_reports_all,
    get_reports_page,
    get_report_with_user,
    get_report_neighbors,
    get_pending_reports,
    created_at_msk,
    report_day_value_of,
)
from utils.permissions import can_enter_mvd
from bot.handlers.reports import report_card_text

router = Router()


def _mvd_menu_kb(count_all: int, count_pending: int) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=f"📦 Архив отчётов ({count_all})", callback_data="mvd:archive:0")],
        [InlineKeyboardButton(text=f"⏳ На проверке ({count_pending})", callback_data="admin:reports_pending")],
        [InlineKeyboardButton(text="🔙 В город", callback_data="city:menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.callback_query(F.data == "mvd:menu")
async def mvd_menu(callback: CallbackQuery):
    if not await can_enter_mvd(callback.from_user.id):
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return
    await callback.answer()
    total_all = await count_reports_all()
    pending = await get_pending_reports()
    text = (
        "🚔 ЗДАНИЕ МВД\n"
        "────────────────\n"
        "Архив всех сданных отчётов и очередь на проверку пилотской отчётности."
    )
    await callback.message.answer(text, reply_markup=_mvd_menu_kb(total_all, len(pending)))


@router.callback_query(F.data.startswith("mvd:archive:"))
async def mvd_archive_paginate(callback: CallbackQuery):
    await callback.answer()
    try:
        parts = callback.data.split(":")
        page = int(parts[-1])
    except (ValueError, IndexError):
        page = 0

    if not await can_enter_mvd(callback.from_user.id):
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return

    total = await count_reports_all()
    per_page = REPORT_ARCHIVE_PAGE
    total_pages = max(1, (total + per_page - 1) // per_page)
    page = max(0, min(page, total_pages - 1))
    offset = page * per_page
    items = await get_reports_page(offset, per_page)

    status_emoji = {"pending": "⏳", "approved": "✅", "rejected": "❌"}
    kb = []
    lines = []
    for r in items:
        emoji = status_emoji.get(r["status"], "❓")
        when = created_at_msk(r["created_at"]) or str(r["created_at"])[:16]
        day = report_day_value_of(r["created_at"])
        day_hint = f" (сутки {day[5:]})" if day else ""
        name = (r.get("callsign") or r.get("username") or r.get("first_name") or "Пилот")[:10]
        lines.append(f"{emoji} #{r['id']} · {name} · {r['troops_reported']}⚔️ · {when}{day_hint}")

    text = "📦 АРХИВ ОТЧЁТОВ\n────────────────\nВсего: {total}\n\n".format(total=total)
    text += "\n".join(lines)
    if total_pages > 1:
        text += f"\n\nСтраница {page + 1} из {total_pages}"

    for r in items:
        kb.append([InlineKeyboardButton(text=f"🔍 # {r['id']} — карточка", callback_data=f"mvd:arch:{r['id']}:{page}")])
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="◀️", callback_data=f"mvd:archive:{page - 1}"))
    nav.append(InlineKeyboardButton(text=f"{page + 1}/{total_pages}", callback_data="noop"))
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton(text="▶️", callback_data=f"mvd:archive:{page + 1}"))
    if nav:
        kb.append(nav)
    kb.append([InlineKeyboardButton(text="🚔 Здание МВД", callback_data="mvd:menu")])
    await callback.message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))


@router.callback_query(F.data.startswith("mvd:arch:"))
async def mvd_archive_card(callback: CallbackQuery):
    await callback.answer()
    try:
        parts = callback.data.split(":")
        if len(parts) == 4:
            _, _, rid_str, page_str = parts
            page = int(page_str)
            rid = int(rid_str)
        elif len(parts) == 3:
            _, _, rid_str = parts
            page = 0
            rid = int(rid_str)
        else:
            return
    except (ValueError, IndexError):
        return

    if not await can_enter_mvd(callback.from_user.id):
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return

    r = await get_report_with_user(rid)
    if not r:
        await callback.message.answer("❌ Отчёт не найден.")
        return

    text = report_card_text(r)
    prev_id, next_id = await get_report_neighbors(rid)
    nav_row = []
    if prev_id:
        nav_row.append(InlineKeyboardButton(text="◀️ Новее", callback_data=f"mvd:arch:{prev_id}:{page}"))
    if next_id:
        nav_row.append(InlineKeyboardButton(text="Старее ▶️", callback_data=f"mvd:arch:{next_id}:{page}"))
    kb_rows = []
    if nav_row:
        kb_rows.append(nav_row)
    kb_rows.append([InlineKeyboardButton(text="◀️ К архиву", callback_data=f"mvd:archive:{page}")])
    kb_rows.append([InlineKeyboardButton(text="🚔 Здание МВД", callback_data="mvd:menu")])
    kb = InlineKeyboardMarkup(inline_keyboard=kb_rows)

    photo = r['screenshot_file_id'] if 'screenshot_file_id' in r.keys() else None
    if photo:
        try:
            await callback.message.answer_photo(photo=photo, caption=text, reply_markup=kb)
            return
        except Exception:
            pass
    await callback.message.answer(text, reply_markup=kb)