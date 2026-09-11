"""Городской парк Аркхольма: озеро (статика) и аллея статуй с перелистыванием.

Статуи добавляются/удаляются админом (право can_manage_locations — супер-админ,
с заделом на выдачу этого права другим ролям). У статуи можно задать картинки
по времени суток (рассвет/день/закат/ночь); недостающие заменяются дневной,
затем любой другой.
"""

import os

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile, InputMediaPhoto
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.db import (
    get_park_statues, get_park_statue, add_park_statue, delete_park_statue,
    update_park_statue,
    can_enter_location, PARK_TOD_KEYS,
)
from keyboards.keyboards import cancel_keyboard
from utils.permissions import has_permission, log_action
from utils.helpers import resolve_image, time_of_day_key, edit_message_safe, is_main_menu_text

router = Router()

PARK_PHOTO = "city/park"

TOD_LABEL = {
    "dawn": "🌅 Рассвет",
    "day": "☀️ День",
    "sunset": "🌇 Закат",
    "night": "🌙 Ночь",
}


class AdminStatue(StatesGroup):
    name = State()
    description = State()
    image_dawn = State()
    image_day = State()
    image_sunset = State()
    image_night = State()


def park_photo() -> FSInputFile:
    path = resolve_image(PARK_PHOTO)
    if not os.path.isfile(path):
        path = resolve_image("city/arkholm")
    return FSInputFile(path)


def statue_image(statue: dict) -> str | None:
    """Выбирает картинку статуи под текущее время суток с фолбэками."""
    current = time_of_day_key()
    candidates = list(dict.fromkeys([current, "day"] + list(PARK_TOD_KEYS)))
    for key in candidates:
        val = statue.get(f"image_{key}")
        if val:
            return val
    return None


async def _show(message, media, caption, kb):
    """Фото-сообщение: либо переписываем существующее, либо отвечаем новым."""
    if message.photo:
        await message.edit_media(media=InputMediaPhoto(media=media, caption=caption), reply_markup=kb)
    else:
        await message.answer_photo(photo=media, caption=caption, reply_markup=kb)


def park_menu_markup(is_manager: bool):
    rows = [
        [InlineKeyboardButton(text="🗿 Аллея статуй", callback_data="park:statues")],
        [InlineKeyboardButton(text="🌊 Озеро", callback_data="park:lake")],
    ]
    if is_manager:
        rows.append([InlineKeyboardButton(text="🛠 Управление статуями", callback_data="park:admin")])
    rows.append([InlineKeyboardButton(text="🔙 В город", callback_data="city:menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def park_enter(callback: CallbackQuery):
    """Точка входа из locations.py (маршрут location:enter:park)."""
    is_manager = await has_permission(callback.from_user.id, "can_manage_locations")
    caption = (
        "🌳 ГОРОДСКОЙ ПАРК АРКХОЛЬМА\n\n"
        "Тенистые аллеи, пруд и тишина вместо шума цеха.\n"
        "Парк открыт для всех — и для пилотов, и для туристов."
    )
    await _show(callback.message, park_photo(), caption, park_menu_markup(is_manager))


@router.callback_query(F.data == "park:menu")
async def park_menu_cb(callback: CallbackQuery):
    await callback.answer()
    await park_enter(callback)


@router.callback_query(F.data == "park:lake")
async def park_lake(callback: CallbackQuery):
    from bot.handlers.fishing import fishing_lake_menu
    await fishing_lake_menu(callback)


# ============ АЛЛЕЯ СТАТУЙ ============

def statue_browse_markup(total: int, idx: int):
    rows = []
    nav = []
    if total > 1 and idx > 0:
        nav.append(InlineKeyboardButton(text="◀️", callback_data=f"park:statue:{idx - 1}"))
    nav.append(InlineKeyboardButton(text=f"{idx + 1}/{total}", callback_data="noop"))
    if total > 1 and idx < total - 1:
        nav.append(InlineKeyboardButton(text="▶️", callback_data=f"park:statue:{idx + 1}"))
    if nav:
        rows.append(nav)
    rows.append([InlineKeyboardButton(text="🔙 В парк", callback_data="park:menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def _show_statue(message, statue: dict, idx: int, total: int):
    text = f"🗿 {statue['name']}\n"
    if statue.get('description'):
        text += f"\n{statue['description']}\n"
    image = statue_image(statue)
    kb = statue_browse_markup(total, idx)
    if image:
        await _show(message, image, text, kb)
    else:
        await edit_message_safe(message, text, kb)


@router.callback_query(F.data == "park:statues")
async def park_statues(callback: CallbackQuery):
    await callback.answer()
    statues = await get_park_statues()
    if not statues:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 В парк", callback_data="park:menu")]
        ])
        caption = "🗿 АЛЛЕЯ СТАТУЙ\n\nПока пусто. Статуи появятся позже."
        await _show(callback.message, park_photo(), caption, kb)
        return
    await _show_statue(callback.message, statues[0], 0, len(statues))


@router.callback_query(F.data.startswith("park:statue:"))
async def park_statue_nav(callback: CallbackQuery):
    await callback.answer()
    try:
        idx = int(callback.data.split(":", 2)[2])
    except ValueError:
        return
    statues = await get_park_statues()
    if not statues:
        return
    idx = max(0, min(idx, len(statues) - 1))
    await _show_statue(callback.message, statues[idx], idx, len(statues))


# ============ УПРАВЛЕНИЕ СТАТУЯМИ (админ) ============

@router.callback_query(F.data == "park:admin")
async def park_admin(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        await callback.message.answer("❌ Нет прав для управления статуями.")
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить статую", callback_data="park:admin:add")],
        [InlineKeyboardButton(text="✏️ Изменить статую", callback_data="park:admin:editlist")],
        [InlineKeyboardButton(text="🗑️ Удалить статую", callback_data="park:admin:list")],
        [InlineKeyboardButton(text="🔙 В парк", callback_data="park:menu")],
    ])
    await callback.message.answer("🛠 УПРАВЛЕНИЕ СТАТУЯМИ\n\nВыбери действие:", reply_markup=kb)


@router.callback_query(F.data == "park:admin:add")
async def statue_add_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    await state.set_state(AdminStatue.name)
    await callback.message.answer("🗿 Введи название статуи:", reply_markup=cancel_keyboard())


@router.message(AdminStatue.name, F.text, ~F.text.func(is_main_menu_text))
async def statue_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await state.set_state(AdminStatue.description)
    await message.answer("📝 Введи описание статуи:", reply_markup=cancel_keyboard())


@router.message(AdminStatue.description, ~F.text.func(is_main_menu_text))
async def statue_description(message: Message, state: FSMContext):
    await state.update_data(description=(message.text or "").strip())
    await state.set_state(AdminStatue.image_day)
    await _ask_statue_image(message, "day", required=True)


async def _ask_statue_image(message, key: str, required: bool = False):
    if required:
        text = f"🖼️ Пришли фото статуи для времени суток «{TOD_LABEL[key]}» (обязательно):"
    else:
        text = (f"🖼️ Пришли фото статуи для времени суток «{TOD_LABEL[key]}»\n"
                f"или отправь «—», чтобы пропустить:")
    await message.answer(text, reply_markup=cancel_keyboard())


async def _collect_statue_image(message, state, key: str, required: bool = False):
    if message.photo:
        file_id = message.photo[-1].file_id
    elif message.text and message.text.strip() == "—" and not required:
        file_id = None
    else:
        if required:
            await message.answer("❌ Пришли фото статуи (картинку):", reply_markup=cancel_keyboard())
        else:
            await message.answer("❌ Пришли фото или «—» для пропуска:", reply_markup=cancel_keyboard())
        return False
    await state.update_data(**{f"image_{key}": file_id})
    return True


@router.message(AdminStatue.image_day, ~F.text.func(is_main_menu_text))
async def statue_img_day(message: Message, state: FSMContext):
    if not await _collect_statue_image(message, state, "day", required=True):
        return
    await state.set_state(AdminStatue.image_dawn)
    await _ask_statue_image(message, "dawn")


@router.message(AdminStatue.image_dawn, ~F.text.func(is_main_menu_text))
async def statue_img_dawn(message: Message, state: FSMContext):
    if not await _collect_statue_image(message, state, "dawn"):
        return
    await state.set_state(AdminStatue.image_sunset)
    await _ask_statue_image(message, "sunset")


@router.message(AdminStatue.image_sunset, ~F.text.func(is_main_menu_text))
async def statue_img_sunset(message: Message, state: FSMContext):
    if not await _collect_statue_image(message, state, "sunset"):
        return
    await state.set_state(AdminStatue.image_night)
    await _ask_statue_image(message, "night")


@router.message(AdminStatue.image_night, ~F.text.func(is_main_menu_text))
async def statue_img_night(message: Message, state: FSMContext):
    if not await _collect_statue_image(message, state, "night"):
        return
    data = await state.get_data()
    await add_park_statue(
        name=data['name'],
        description=data['description'],
        images={k: data.get(f"image_{k}") for k in PARK_TOD_KEYS},
        created_by=message.from_user.id,
    )
    await log_action(message.from_user.id, 'add_statue', None, data['name'])
    await state.clear()
    await message.answer(f"✅ Статуя «{data['name']}» добавлена в парк.")


@router.callback_query(F.data == "park:admin:list")
async def statue_admin_list(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    statues = await get_park_statues()
    if not statues:
        await callback.message.answer("Пока нет ни одной статуи.")
        return
    rows = [[InlineKeyboardButton(text=f"🗑 {s['name']}", callback_data=f"park:admin:del:{s['id']}")] for s in statues]
    rows.append([InlineKeyboardButton(text="🔙 Назад", callback_data="park:admin")])
    await edit_message_safe(callback.message, "Выбери статую для удаления:", InlineKeyboardMarkup(inline_keyboard=rows))


@router.callback_query(F.data.startswith("park:admin:del:"))
async def statue_admin_del_confirm(callback: CallbackQuery):
    await callback.answer()
    try:
        statue_id = int(callback.data.split(":", 3)[3])
    except ValueError:
        return
    statue = await get_park_statue(statue_id)
    if not statue:
        await callback.message.answer("❌ Статуя не найдена.")
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Да, удалить", callback_data=f"park:admin:delyes:{statue_id}")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="park:admin:list")],
    ])
    await edit_message_safe(callback.message, f"Удалить статую «{statue['name']}»?", kb)


@router.callback_query(F.data.startswith("park:admin:delyes:"))
async def statue_admin_delete(callback: CallbackQuery):
    await callback.answer()
    try:
        statue_id = int(callback.data.split(":", 3)[3])
    except ValueError:
        return
    statue = await get_park_statue(statue_id)
    if not statue:
        await callback.message.answer("❌ Статуя не найдена.")
        return
    await delete_park_statue(statue_id)
    await log_action(callback.from_user.id, 'delete_statue', None, statue['name'])
    await callback.message.answer(f"🗑️ Статуя «{statue['name']}» удалена из парка.")


# ============ ИЗМЕНЕНИЕ СТАТУИ (админ) ============

class AdminStatueEdit(StatesGroup):
    field = State()
    value = State()


async def _statue_edit_fields_menu(callback: CallbackQuery, statue: dict):
    """Inline-меню выбора поля статуи для редактирования."""
    def flabel(key, current):
        short = ""
        if key == "description":
            short = (current or "—")[:40]
        else:
            short = "есть" if current else "—"
        return f"{TOD_LABEL.get(key, key)}: «{short}»"

    rows = [
        [InlineKeyboardButton(
            f"📝 Описание: «{(statue.get('description') or '—')[:40]}»",
            callback_data=f"park:adminedit:f:{statue['id']}:description",
        )],
    ]
    for key in PARK_TOD_KEYS:
        rows.append([InlineKeyboardButton(
            flabel(key, statue.get(f"image_{key}")),
            callback_data=f"park:adminedit:f:{statue['id']}:{key}",
        )])
    rows.append([InlineKeyboardButton(text="✅ Готово", callback_data="park:admin")])
    await callback.message.edit_text(
        f"✏️ Редактирование статуи «{statue['name']}»\nВыбери поле для изменения:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows)
    )


@router.callback_query(F.data == "park:admin:editlist")
async def statue_admin_edit_list(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    statues = await get_park_statues()
    if not statues:
        await callback.message.answer("Пока нет ни одной статуи.")
        return
    rows = [[InlineKeyboardButton(text=f"✏️ {s['name']}", callback_data=f"park:admin:edit:{s['id']}")] for s in statues]
    rows.append([InlineKeyboardButton(text="🔙 Назад", callback_data="park:admin")])
    await edit_message_safe(callback.message, "Выбери статую для редактирования:",
                            InlineKeyboardMarkup(inline_keyboard=rows))


@router.callback_query(F.data.startswith("park:admin:edit:"))
async def statue_admin_edit_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    try:
        statue_id = int(callback.data.split(":", 3)[3])
    except ValueError:
        return
    statue = await get_park_statue(statue_id)
    if not statue:
        await callback.message.answer("❌ Статуя не найдена.")
        return
    await state.update_data(statue_id=statue_id, field=None)
    await state.set_state(AdminStatueEdit.field)
    await _statue_edit_fields_menu(callback, statue)


@router.callback_query(F.data.startswith("park:adminedit:f:"))
async def statue_admin_edit_field(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    _, _, _, statue_s, field = callback.data.split(":", 4)
    await state.update_data(field=field)
    await state.set_state(AdminStatueEdit.value)
    if field == 'description':
        await callback.message.edit_text(
            "📝 Введи новое описание статуи:", reply_markup=cancel_keyboard()
        )
    else:
        await callback.message.edit_text(
            f"🖼️ Пришли фото статуи для «{TOD_LABEL.get(field, field)}»\n"
            f"или отправь «—», чтобы оставить без изменений:",
            reply_markup=cancel_keyboard()
        )


@router.message(AdminStatueEdit.value, ~F.text.func(is_main_menu_text))
async def statue_admin_edit_value(message: Message, state: FSMContext):
    data = await state.get_data()
    statue_id = data.get('statue_id')
    field = data.get('field')
    if not statue_id or not field:
        await state.clear()
        return
    if field == 'description':
        await update_park_statue(statue_id, description=(message.text or "").strip())
    else:
        if not (message.photo or (message.text and message.text.strip() == "—")):
            await message.answer("❌ Пришли фото или «—» чтобы оставить как есть.", reply_markup=cancel_keyboard())
            return
        if message.text and message.text.strip() == "—":
            # «—» без изменений
            pass
        else:
            file_id = message.photo[-1].file_id
            await update_park_statue(statue_id, **{field: file_id})

    statue = await get_park_statue(statue_id)
    await message.answer("✅ Сохранено.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Ещё изменений", callback_data=f"park:admin:edit:{statue_id}")],
        [InlineKeyboardButton(text="✅ Готово", callback_data="park:admin")],
    ]))
    await state.set_state(AdminStatueEdit.field)