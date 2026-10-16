"""Городские склады: накопление выкупленных казной ресурсов.

Все проданные единицы ресурсов (`category == 'resource'`) не пропадают «в
никуда», а оседают на городском складе — сколько чего лежит (руда, самоцветы,
грибы, находки с рыбалки, трофеи). Позже склад задействуется для строительства
(см. блок «Производственные здания»).

Локация города `storage` («Городские склады»): вход с «Пилота 1 класса».
Экран — таблица накопленных ресурсов; пополняется в точке продажи ресурса
в казну (`bot/handlers/inventory.py::_sell_item`).
"""

import os

from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database.db import get_location_by_key, location_storage_photo, get_city_storage
from utils.helpers import resolve_image_seasonal

router = Router()

STORAGE_FALLBACK_PHOTO = "city/storage"

# Эмодзи по категории предмета (склад пока наполняется только ресурсами).
STORAGE_EMOJI = {
    "resource": "⛏️",
    "fishing": "🎣",
}


def _storage_markup() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Обновить", callback_data="storage:menu")],
        [InlineKeyboardButton(text="🔙 В город", callback_data="city:menu")],
    ])


def build_storage_text(rows) -> str:
    """Таблица содержимого склада: строка на ресурс + итог."""
    lines = ["📦 ГОРОДСКИЕ СКЛАДЫ", "────────────────"]
    if not rows:
        lines.append("Склады пусты.")
        lines.append("")
        lines.append("Продай добытые ресурсы казне — выкупленное осядет здесь "
                     "и пойдёт на нужды города.")
        return "\n".join(lines)
    total = 0
    for r in rows:
        qty = r['qty'] or 0
        total += qty
        emoji = STORAGE_EMOJI.get(r['category'], "📦")
        lines.append(f"{emoji} {r['name']} — {qty}")
    lines.append("────────────────")
    lines.append(f"Всего единиц: {total}")
    return "\n".join(lines)


async def _storage_media():
    """Своя картинка зала склада (из админки) → локальный сезонный файл."""
    loc = await get_location_by_key("storage")
    if loc:
        photo_id = location_storage_photo(loc)
        if photo_id:
            return photo_id, None
    path = resolve_image_seasonal(STORAGE_FALLBACK_PHOTO)
    return None, (path if os.path.isfile(path) else None)


async def storage_menu(callback: CallbackQuery):
    """Экран склада: вызывается при входе в локацию «Городские склады»."""
    rows = await get_city_storage()
    text = build_storage_text(rows)
    photo_id, media_path = await _storage_media()
    if photo_id or media_path:
        try:
            await callback.message.answer_photo(
                photo=photo_id or FSInputFile(media_path),
                caption=text,
                reply_markup=_storage_markup(),
            )
            return
        except Exception:
            pass
    await callback.message.answer(text, reply_markup=_storage_markup())


@router.callback_query(F.data == "storage:menu")
async def storage_refresh(callback: CallbackQuery):
    await callback.answer()
    await storage_menu(callback)
