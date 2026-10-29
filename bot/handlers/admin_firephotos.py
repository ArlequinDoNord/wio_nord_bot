# -*- coding: utf-8 -*-
"""Админ-менеджер картинок праздника «Пламенный Круговорот».

file_id-картинки хранятся в `settings` (ключи `fire_photo:*`, db helpers).
Привязки: entry (вход в Лабиринт), fork (комната-развилка), well (Колодец),
tree (Древо Огня), chest (Сундук). Глобально на всех пилотов.
"""

import database.db as db
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.keyboards import cancel_keyboard
from utils.permissions import has_permission

router = Router()


def _escape(text: str | None) -> str:
    return (text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class FirePhotosAdmin(StatesGroup):
    wait_photo = State()


async def _require(cb_or_msg) -> bool:
    """can_manage_locations — тот же гейт, что у редактора картинок локаций."""
    uid = getattr(cb_or_msg, "from_user", None)
    uid = uid.id if uid else cb_or_msg.from_user.id
    return await has_permission(uid, "can_manage_locations")


def _mark(ok: bool) -> str:
    return "✅" if ok else "▫️"


async def _menu_screen(source) -> None:
    keys = db.FIRE_PHOTO_KEYS
    labels = db.FIRE_PHOTO_LABELS
    lines = ["🪔 <b>Картинки Огненного Круговорота</b>", ""]
    rows = []
    filled = 0
    for key in keys:
        has = bool(await db.get_fire_photo(key))
        filled += int(has)
        lines.append(f"{_mark(has)} {labels[key]}")
        rows.append([InlineKeyboardButton(
            text=f"{_mark(has)} {labels[key]}",
            callback_data=f"fireph:set:{key}")])
    lines.append("")
    lines.append(f"Заполнено: {filled}/{len(keys)}.")
    lines.append("Отправь фото (или «-» чтобы убрать). Файлы в assets/img "
                 "используются сами, если photo нет.")
    rows.append([InlineKeyboardButton(text="🔙 В админ-панель",
                                      callback_data="admin:menu")])
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    text = _escape("\n".join(lines))
    if hasattr(source, "message") and getattr(source, "message", None) is not None:
        try:
            await source.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
            return
        except Exception:
            pass
    if hasattr(source, "message"):
        await source.message.answer(text, reply_markup=kb, parse_mode="HTML")
    else:
        await source.answer(text, reply_markup=kb, parse_mode="HTML")


@router.callback_query(F.data == "fireph:menu")
async def fire_photo_menu_cb(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    if not await _require(cb):
        return
    await state.clear()
    await _menu_screen(cb)


@router.callback_query(F.data.startswith("fireph:set:"))
async def fire_photo_pick_cb(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    if not await _require(cb):
        return
    key = cb.data.split(":")[2]
    if key not in db.FIRE_PHOTO_KEYS:
        await cb.message.answer("❌ Неизвестная точка праздника.")
        return
    await state.update_data(fireph=key)
    await state.set_state(FirePhotosAdmin.wait_photo)
    label = db.FIRE_PHOTO_LABELS.get(key, key)
    current = await db.get_fire_photo(key)
    await cb.message.answer(
        f"🖼 Картинка «{label}»\n"
        f"Сейчас: {'есть' if current else 'нет'}.\n\n"
        "Отправь фото — станет картинкой этой точки для всех пилотов.\n"
        "«-» — убрать картинку.",
        reply_markup=cancel_keyboard())


@router.message(FirePhotosAdmin.wait_photo)
async def fire_photo_save(message: Message, state: FSMContext):
    if not await _require(message):
        await state.clear()
        return
    data = await state.get_data()
    key = data.get("fireph")
    if key not in db.FIRE_PHOTO_KEYS:
        await state.clear()
        await message.answer("❌ Точка праздника не распознана. Начни заново: "
                             "админ → Картинки Круговорота.")
        return
    label = db.FIRE_PHOTO_LABELS.get(key, key)
    if message.photo:
        await db.set_fire_photo(key, message.photo[-1].file_id)
        await state.clear()
        await message.answer(f"✅ Картинка «{label}» сохранена (глобально).")
        await _menu_screen(message)
        return
    text_in = (message.text or "").strip()
    if text_in == "-":
        await db.set_fire_photo(key, None)
        await state.clear()
        await message.answer(f"✅ Картинка «{label}» удалена.")
        await _menu_screen(message)
        return
    await state.clear()
    await message.answer("❌ Нужно фото (или «-» чтобы убрать). Открой заново: "
                         "админ → Картинки Круговорота.")
