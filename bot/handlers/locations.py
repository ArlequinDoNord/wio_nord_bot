"""Универсальные локации города: превью (всем) + вход (по доступу).

Превью локации (картинка + описание) доступно всем, даже пьяным.
Вход в локацию проверяет статусный режим (all/min/exact) и блокирующие
состояния, а также специфичные условия самой локации (например,
читательский билет в Библиотеке).
"""

import os

from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from database.db import (
    get_location_by_key, can_enter_location, location_access_label,
    user_has_status_tag, log_location_visit,
)
from utils.helpers import resolve_image, time_of_day_key
from utils.permissions import has_permission, is_admin

router = Router()

# Специальные строки доступа для зданий со своим правилом (не статусом).
LOCATION_ACCESS_LINES = {
    "gossmi": "🎙 Вход: только сотрудники ГосСМИ (журналист / редактор)",
    "hq": "🎖 Вход: командование ВВС (приказы авиакрыльям)",
    "contracts": "📜 Вход: только пилоты (контракты на зачистку)",
}


@router.callback_query(F.data.startswith("location:preview:"))
async def location_preview(callback: CallbackQuery):
    await callback.answer()
    key = callback.data.split(":", 2)[2]
    loc = await get_location_by_key(key)
    if not loc:
        await callback.message.answer("❌ Локация не найдена.")
        return

    if key in LOCATION_ACCESS_LINES:
        access_line = LOCATION_ACCESS_LINES[key]
    else:
        access_label = await location_access_label(loc['access_mode'], loc['required_status'])
        access_line = f"Доступ: {access_label}"
    text = (
        f"📍 {loc['name']}\n"
        f"────────────────\n"
        f"{loc['description'] or ''}\n\n"
        f"{access_line}"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔑 Войти", callback_data=f"location:enter:{key}")],
        [InlineKeyboardButton(text="🔙 В город", callback_data="city:menu")],
    ])

    photo = None
    # Приоритет: file_id по текущему времени суток → asset-ключ (resolve_image) → единый file_id
    tod = time_of_day_key()
    keys = loc.keys()
    # К.В.П.: админ задаёт фото данжа через менеджер подземелий — они же показываются
    # и в превью города, и на меню курса, и внутри курса (одна и та же картинка).
    if key == "kvp":
        from bot.handlers.kvp import kvp_dungeon_photo
        kvp_photo = await kvp_dungeon_photo()
        if kvp_photo:
            photo = kvp_photo
    if not photo:
        for slot in (f"photo_{tod}", "photo_dawn", "photo_day", "photo_sunset", "photo_night"):
            if slot in keys and loc[slot]:
                photo = loc[slot]
                break
    if not photo and 'preview_photo' in keys and loc['preview_photo']:
        candidate = resolve_image(loc['preview_photo'])
        if os.path.isfile(candidate):
            photo = FSInputFile(candidate)
        elif not loc['preview_photo'].startswith("city/"):
            photo = loc['preview_photo']
    if not photo and key == "contracts":
        # Единая картинка доски контрактов (тот же файл, что и в меню контрактов).
        candidate = resolve_image("city/contracts_board")
        if os.path.isfile(candidate):
            photo = FSInputFile(candidate)
    if photo:
        try:
            await callback.message.answer_photo(
                photo=photo,
                caption=text,
                reply_markup=kb
            )
            return
        except Exception:
            pass
    await callback.message.answer(text, reply_markup=kb)


@router.callback_query(F.data.startswith("location:enter:"))
async def location_enter(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    key = callback.data.split(":", 2)[2]
    loc = await get_location_by_key(key)
    if not loc:
        await callback.message.answer("❌ Локация не найдена.")
        return

    if not await can_enter_location(callback.from_user.id, key):
        await callback.message.answer(
            f"⛔ Нет доступа в «{loc['name']}».\n"
            f"Убедись, что твой статус соответствует требованию и ты не в состоянии, "
            f"которое блокирует вход."
        )
        return

    # ГосСМИ: войти могут только сотрудники (журналист/редактор) и администрация.
    # Штаб ВВС: вход только командованию (приказы) и администрации.
    # Доска контрактов: вход только пилотам.
    # Кнопка «Войти» видна всем, но остальные получают предупреждение.
    if key == "gossmi":
        actor = callback.from_user.id
        if not (await is_admin(actor) or await has_permission(actor, "can_post_news")):
            await callback.message.answer(
                f"⛔ Вход в здание «{loc['name']}» — только для сотрудников медиацентра.\n\n"
                f"Обычным жителям Нордхайма внутрь попасть нельзя. Свежие выпуски "
                f"новостей читай в главном меню — «📰 Новости Нордхайма».",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 В город", callback_data="city:menu")]
                ])
            )
            return
    elif key == "hq":
        actor = callback.from_user.id
        if not (await is_admin(actor)
                or await has_permission(actor, "can_send_orders")
                or await has_permission(actor, "can_wing_commands")):
            await callback.message.answer(
                f"⛔ Вход в здание «{loc['name']}» — только для командования ВВС.\n\n"
                f"Здесь отдаются приказы авиакрыльям. Пилотам вход воспрещён.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 В город", callback_data="city:menu")]
                ])
            )
            return
    elif key == "contracts":
        if not await user_has_status_tag(callback.from_user.id, "pilot2"):
            await callback.message.answer(
                f"⛔ Вход на «{loc['name']}» — только для пилотов ВВС.\n\n"
                f"Контракты на зачистку подземелий выдаются действующим пилотам.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 В город", callback_data="city:menu")]
                ])
            )
            return

    # Логируем успешный вход в локацию (для анализа популярности аспектов игры)
    await log_location_visit(callback.from_user.id, key)

    # Передаём управление специфическому функционалу локации
    if key == "townhall":
        from bot.handlers.pilots import town_hall_menu
        await town_hall_menu(callback)
    elif key == "library":
        from bot.handlers.library import library_enter
        await library_enter(callback)
    elif key == "park":
        from bot.handlers.park import park_enter
        await park_enter(callback)
    elif key == "bank":
        from bot.handlers.bank import bank_menu_cb
        await bank_menu_cb(callback)
    elif key == "gossmi":
        from bot.handlers.news import news_tab
        await news_tab(callback.message, user_id=callback.from_user.id)
    elif key == "kvp":
        from bot.handlers.kvp import kvp_menu_cb
        await kvp_menu_cb(callback)
    elif key == "hq":
        from bot.handlers.hq import hq_menu_show
        await hq_menu_show(callback.message, callback.from_user.id)
    elif key == "contracts":
        from bot.handlers.dungeon import show_contracts
        await show_contracts(callback.message, callback.from_user.id, state)
    elif key == "nii":
        from bot.handlers.nii import nii_menu
        await nii_menu(callback)
