"""
Админ-панель: управление магазином, финансами, отчётами, ролями и логами.
Доступ разграничен по ролям (см. utils/permissions.py).
"""

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.db import (
    add_item, delete_item, update_item, get_available_items,
    get_item, get_all_users, get_pending_reports, approve_report,
    reject_report, add_nordmarks, remove_nordmarks, add_ap, remove_ap,
    create_status, delete_status, get_all_statuses, get_status,
    grant_status, revoke_status, get_user_statuses,
    get_users_for_rank_promotion, promote_user_rank, get_user,
    recompute_region_stats, get_region_stats,
    get_daily_spent, add_daily_spent,
    get_treasury_balance, transfer_from_treasury, get_treasury_stats,
    get_report_tax_percent, set_report_tax_percent,
    get_sale_tax_percent, set_sale_tax_percent,
    get_salaried_users, get_user_salary, set_user_salary, pay_salaries,
    get_all_locations, get_location, create_location, update_location_access,
    location_access_label,
    create_award, get_all_awards, get_award, delete_award, grant_award,
    get_user_awards, revoke_award,
    log_activity, get_user_activity, clear_user_photo,
)
from keyboards.keyboards import cancel_keyboard
from utils.permissions import (
    is_admin, has_permission, get_user_role,
    add_role, remove_role, ROLES, role_label, log_action,
)
from utils.helpers import plural_nordmark
from config import RARITY_LEVELS, RARITY_EMOJI, ITEM_CATEGORIES, get_effective_rank, VERSION
from utils.notify import notify, player_display, NOTIFY_REPORT_MIN_TROOPS

router = Router()


# ============ FSM-СОСТОЯНИЯ ============

class AdminAddItem(StatesGroup):
    name = State()
    desc = State()
    price = State()
    sell_price = State()
    rarity = State()
    category = State()
    stock = State()
    stats = State()
    producer = State()
    producer_user = State()
    photo = State()


class AdminSaleTax(StatesGroup):
    percent = State()


class AdminEditItem(StatesGroup):
    item_id = State()
    field = State()
    value = State()


class AdminFinance(StatesGroup):
    target = State()
    currency = State()
    amount = State()


class AdminTreasury(StatesGroup):
    amount = State()
    target = State()


class AdminTax(StatesGroup):
    percent = State()


class AdminRoles(StatesGroup):
    target = State()
    action = State()
    role = State()


class AdminStatuses(StatesGroup):
    name = State()
    tag = State()
    level = State()
    desc = State()
    target = State()
    grant_action = State()
    status_pick = State()
    item_pick = State()
    item_status = State()


class AdminAwards(StatesGroup):
    name = State()
    desc = State()
    emoji = State()
    target = State()
    award_pick = State()
    comment = State()


class AdminStates(StatesGroup):
    target = State()
    action = State()
    state_key = State()
    minutes = State()


class AdminSalary(StatesGroup):
    target = State()
    amount = State()
    period = State()


class AdminLocation(StatesGroup):
    action = State()        # create / edit
    target_id = State()     # id локации для редактирования
    key = State()
    name = State()
    description = State()
    mode = State()
    req_status = State()
    blocking = State()
    preview = State()


# ============ УТИЛИТЫ ============

async def perm_flags(user_id: int) -> dict:
    perms = ["can_manage_shop", "can_manage_finance", "can_view_reports",
             "can_approve_reports", "can_manage_admins", "can_view_logs",
             "can_manage_statuses", "can_grant_statuses", "can_grant_troops",
             "can_manage_states", "can_manage_locations", "can_manage_salaries",
             "can_manage_awards", "can_grant_awards"]
    return {p: await has_permission(user_id, p) for p in perms}


async def find_user(text: str) -> dict:
    """Найти пользователя по @username или числовому telegram_id."""
    text = text.strip().lstrip("@")
    users = await get_all_users()
    if text.isdigit():
        for u in users:
            if str(u['user_id']) == text:
                return u
    for u in users:
        if u['username'] and u['username'].lower() == text.lower():
            return u
    return None


def rarity_choice_markup():
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    rows = []
    for key in RARITY_LEVELS:
        rows.append([InlineKeyboardButton(
            text=f"{RARITY_EMOJI[key]} {RARITY_LEVELS[key]}",
            callback_data=f"rar:{key}"
        )])
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def pilot_picker_markup(next_step: str):
    """Клавиатура выбора пилота из списка; next_step — куда переходить после выбора."""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    users = await get_all_users()
    rows = []
    if users:
        for u in users[:50]:
            label = u['first_name'] or u['username'] or str(u['user_id'])
            if u['username']:
                label += f" (@{u['username']})"
            rows.append([InlineKeyboardButton(
                text=label,
                callback_data=f"pickuser:{next_step}:{u['user_id']}"
            )])
    rows.append([InlineKeyboardButton(text="✍️ Ввести вручную", callback_data=f"pickuser:{next_step}:manual")])
    rows.append([InlineKeyboardButton(text="🔙 Отмена", callback_data="admin:menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


@router.callback_query(F.data.startswith("pickuser:"))
async def pickuser_cb(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    _, next_step, raw = callback.data.split(":", 2)
    if raw == "manual":
        await callback.message.answer(
            "Введи @username или числовой ID игрока:",
            reply_markup=cancel_keyboard()
        )
        return

    target = await get_user(int(raw))
    if not target:
        await callback.message.answer("❌ Игрок не найден.")
        return
    await state.update_data(target_id=target['user_id'], target_name=target['first_name'] if 'first_name' in target.keys() else '')
    await callback.message.answer(f"Игрок: {target['first_name'] if 'first_name' in target.keys() else ''} (@{target['username'] if 'username' in target.keys() else ''})")

    if next_step == "treasury_target":
        data = await state.get_data()
        amount = data['amount']
        await transfer_from_treasury(
            target['user_id'],
            amount,
            f"Выдача из казны админом #{callback.from_user.id}"
        )
        await log_action(callback.from_user.id, 'treasury', target['user_id'], f"give {amount}")
        await state.clear()
        await callback.message.answer(f"✅ Из казны выдано {amount} {plural_nordmark(amount)}.")
    elif next_step == "finance_amount":
        await state.set_state(AdminFinance.amount)
        await callback.message.answer("Введи сумму:", reply_markup=cancel_keyboard())
    elif next_step == "roles_action":
        await state.set_state(AdminRoles.action)
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        role_names = [role_label(r) for r in await get_user_role(target['user_id'])]
        await callback.message.answer(
            f"Текущие роли: {', '.join(role_names)}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Выдать роль", callback_data="rolop:add")],
                [InlineKeyboardButton(text="Снять роль", callback_data="rolop:remove")],
            ])
        )
    elif next_step == "status_pick":
        await state.set_state(AdminStatuses.status_pick)
        have = await get_user_statuses(target['user_id'])
        have_names = ", ".join(s['name'] for s in have) if have else "нет"
        statuses = await get_all_statuses()
        if not statuses:
            await callback.message.answer("❌ Сначала создай хотя бы один статус.")
            await state.clear()
            return
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        rows = []
        for s in statuses:
            rows.append([InlineKeyboardButton(text=f"{s['name']}", callback_data=f"st_pick:{s['id']}")])
        await callback.message.answer(
            f"Текущие статусы: {have_names}\n\nВыбери статус:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=rows)
        )
    elif next_step == "status_revoke":
        await state.set_state(AdminStatuses.status_pick)
        have = await get_user_statuses(target['user_id'])
        if not have:
            await callback.message.answer(f"У {target['first_name'] if 'first_name' in target.keys() else ''} нет статусов для снятия.")
            await state.clear()
            return
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        rows = []
        for s in have:
            mark = "✅ " if s['is_selected'] else ""
            rows.append([InlineKeyboardButton(text=f"{mark}Снять: {s['name']}", callback_data=f"st_rev:{s['id']}")])
        await callback.message.answer(
            f"У {target['first_name'] if 'first_name' in target.keys() else ''}: {', '.join(s['name'] for s in have)}\n\nВыбери статус для снятия:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=rows)
        )
    elif next_step == "awgrant":
        awards = await get_all_awards()
        if not awards:
            await callback.message.answer("❌ Сначала создай хотя бы одну награду.")
            await state.clear()
            return
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        rows = []
        for a in awards:
            emoji = a['emoji'] or '🏅'
            rows.append([InlineKeyboardButton(text=f"{emoji} {a['name']}",
                                              callback_data=f"aw_pick:{a['id']}")])
        await callback.message.answer(
            f"Текущие награды: {', '.join(g['name'] for g in await get_user_awards(target['user_id'])) or 'нет'}\n\nВыбери награду:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=rows)
        )
    elif next_step == "awrevoke":
        have = await get_user_awards(target['user_id'])
        if not have:
            await callback.message.answer(f"У {target['first_name'] if 'first_name' in target.keys() else ''} нет наград для снятия.")
            await state.clear()
            return
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        rows = []
        for grant in have:
            emoji = grant['emoji'] or '🏅'
            rows.append([InlineKeyboardButton(text=f"{emoji} Снять: {grant['name']}",
                                              callback_data=f"awr_grant:{grant['grant_id']}")])
        await callback.message.answer(
            f"У {target['first_name'] if 'first_name' in target.keys() else ''}: {', '.join(g['name'] for g in have)}\n\nВыбери награду для снятия:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=rows)
        )
    elif next_step == "state_target":
        await state.set_state(AdminStates.action)
        from utils.states import get_state_info
        info = await get_state_info(target['user_id'])
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        await callback.message.answer(
            f"🎭 Игрок: {target['first_name'] if 'first_name' in target.keys() else ''} (@{target['username'] if 'username' in target.keys() else ''})\n"
            f"Текущее состояние: {info['name']}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🎭 Наложить состояние", callback_data="st_op:set")],
                [InlineKeyboardButton(text="✨ Снять состояние", callback_data="st_op:clear")],
            ])
        )
    elif next_step == "salary_set":
        await state.set_state(AdminSalary.amount)
        cur = await get_user_salary(target['user_id'])
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        await callback.message.answer(
            f"💰 Назначение зарплаты\nИгрок: {target['first_name'] if 'first_name' in target.keys() else ''} "
            f"(@{target['username'] if 'username' in target.keys() else ''})\n"
            f"Текущая зарплата: {cur['salary']} {plural_nordmark(cur['salary'])} "
            f"(период {cur['salary_period_days']} дн.)\n\n"
            f"Введи сумму зарплаты за один период (цифрой). 0 — снять зарплату.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="❌ Отмена", callback_data="admin:salaries")],
            ])
        )
    elif next_step == "delphoto":
        from database.db import get_user_photo
        photo = await get_user_photo(target['user_id'])
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        if photo:
            await callback.message.answer(
                f"🗑 Удаление фото профиля\nИгрок: {target['first_name'] if 'first_name' in target.keys() else ''} "
                f"(@{target['username'] if 'username' in target.keys() else ''})\n\n"
                f"Подтверди удаление фото:",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="✅ Да, удалить", callback_data=f"confirm_del_photo:{target['user_id']}")],
                    [InlineKeyboardButton(text="❌ Отмена", callback_data="admin:menu")],
                ])
            )
        else:
            await callback.message.answer("📷 У этого игрока нет установленного фото.")
            await state.clear()
    elif next_step == "player_log":
        await state.clear()
        entries = await get_user_activity(target['user_id'], 80)
        if not entries:
            await callback.message.answer(
                f"📒 Лог игрока\nИгрок: {target['first_name'] if 'first_name' in target.keys() else ''} "
                f"(@{target['username'] if 'username' in target.keys() else ''})\n\n"
                f"Событий нет."
            )
            return
        lines = []
        for e in entries:
            dt = e['created_at'][:16] if e['created_at'] else ""
            details = e['details'] or ""
            lines.append(f"{dt} {details}")
        text = (
            f"📒 ЛОГ ИГРОКА\nИгрок: {target['first_name'] if 'first_name' in target.keys() else ''} "
            f"(@{target['username'] if 'username' in target.keys() else ''})\n"
            f"Последних событий: {len(entries)}\n\n" + "\n".join(lines)
        )
        await callback.message.answer(text[:4000])


def category_choice_markup():
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    rows = []
    for key, label in ITEM_CATEGORIES.items():
        rows.append([InlineKeyboardButton(text=f"{label}", callback_data=f"cat:{key}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ============ ВХОД В АДМИН-ПАНЕЛЬ ============

async def show_admin_panel(user_id: int, to_edit: CallbackQuery = None, to_msg: Message = None):
    from keyboards.keyboards import admin_panel_keyboard
    flags = await perm_flags(user_id)
    text = (
        "👑 АДМИН-ПАНЕЛЬ\n\n"
        "Выберите раздел. Доступные действия зависят от вашей роли:\n\n"
        f"Версия сборки: {VERSION}"
    )
    markup = admin_panel_keyboard(flags)
    if to_edit is not None:
        await to_edit.message.edit_text(text, reply_markup=markup)
    else:
        await to_msg.answer(text, reply_markup=markup)


@router.message(F.text == "👑 Админ-панель")
async def admin_panel(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id

    if not await is_admin(user_id):
        await message.answer("❌ У вас нет доступа к админ-панели.")
        return

    await show_admin_panel(user_id, to_msg=message)


@router.callback_query(F.data == "admin:menu")
async def admin_panel_cb(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    user_id = callback.from_user.id
    if not await is_admin(user_id):
        await callback.answer("❌ Нет доступа.", show_alert=True)
        return
    await show_admin_panel(user_id, to_edit=callback)


@router.callback_query(F.data == "admin:del_photo")
async def admin_del_photo_start(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_users"):
        await callback.message.answer("❌ Нет прав для удаления фото.")
        return
    await callback.message.answer(
        "🗑 Выбери пилота, у которого нужно удалить фото профиля:",
        reply_markup=await pilot_picker_markup("delphoto")
    )


@router.callback_query(F.data == "admin:player_log")
async def admin_player_log_start(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_view_logs"):
        await callback.message.answer("❌ Нет прав для просмотра логов.")
        return
    await callback.message.answer(
        "📒 Выбери игрока, чей лог взаимодействий показать:",
        reply_markup=await pilot_picker_markup("player_log")
    )


@router.callback_query(F.data.startswith("confirm_del_photo:"))
async def confirm_del_photo(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_users"):
        await callback.message.answer("❌ Нет прав для удаления фото.")
        return
    target_id = int(callback.data.split(":")[1])
    target = await get_user(target_id)
    if not target:
        await callback.message.answer("❌ Игрок не найден.")
        return
    await clear_user_photo(target_id)
    await log_action(callback.from_user.id, 'del_photo', target_id, "Удалено фото профиля")
    await log_activity(target_id, "photo_deleted", "Админ удалил фото профиля")
    await callback.message.answer(
        f"✅ Фото профиля удалено у {target['first_name'] if 'first_name' in target.keys() else ''}."
    )


# ============ УПРАВЛЕНИЕ МАГАЗИНОМ ============

@router.callback_query(F.data == "admin:shop")
async def admin_shop(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_shop"):
        await callback.message.answer("❌ Нет прав для управления магазином.")
        return

    from keyboards.keyboards import shop_admin_keyboard
    await callback.message.edit_text(
        "🛒 УПРАВЛЕНИЕ МАГАЗИНОМ\n\nВыберите действие:",
        reply_markup=shop_admin_keyboard()
    )


@router.callback_query(F.data == "shop_admin:add")
async def shop_admin_add(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_add_items"):
        await callback.message.answer("❌ Нет прав на добавление товаров.")
        return
    await state.set_state(AdminAddItem.name)
    await callback.message.answer(
        "🛒 Добавление товара. Шаг 1/9\n\nВведи название товара (или /cancel):",
        reply_markup=cancel_keyboard()
    )


@router.message(AdminAddItem.name)
async def add_item_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await state.set_state(AdminAddItem.desc)
    await message.answer("Шаг 2/9 — Описание товара (или «-» если нет):",
                         reply_markup=cancel_keyboard())


@router.message(AdminAddItem.desc)
async def add_item_desc(message: Message, state: FSMContext):
    text = message.text.strip()
    await state.update_data(desc=None if text == "-" else text)
    await state.set_state(AdminAddItem.price)
    await message.answer("Шаг 3/9 — Цена в Нордмарках (целое число):",
                         reply_markup=cancel_keyboard())


@router.message(AdminAddItem.price)
async def add_item_price(message: Message, state: FSMContext):
    try:
        price = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Введи целое число.")
        return
    if price < 0:
        await message.answer("❌ Цена не может быть отрицательной.")
        return
    await state.update_data(price=price)
    await state.set_state(AdminAddItem.sell_price)
    await message.answer(f"Шаг 4/9 — Цена продажи за {price}? Введи сумму (или «-» = половина):",
                         reply_markup=cancel_keyboard())


@router.message(AdminAddItem.sell_price)
async def add_item_sell_price(message: Message, state: FSMContext):
    data = await state.get_data()
    text = message.text.strip()
    if text == "-":
        sell_price = int(data['price'] / 2)
    else:
        try:
            sell_price = int(text)
        except ValueError:
            await message.answer("❌ Введи целое число или «-».")
            return
    await state.update_data(sell_price=sell_price)
    await state.set_state(AdminAddItem.rarity)
    await message.answer("Шаг 5/9 — Редкость:", reply_markup=rarity_choice_markup())


@router.callback_query(F.data.startswith("rar:"))
async def add_item_rarity(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    rarity = int(callback.data.split(":")[1])
    await state.update_data(rarity=rarity)
    await state.set_state(AdminAddItem.category)
    await callback.message.answer("Шаг 6/9 — Категория:", reply_markup=category_choice_markup())


@router.callback_query(F.data.startswith("cat:"))
async def add_item_category(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    category = callback.data.split(":")[1]
    await state.update_data(category=category)
    await state.set_state(AdminAddItem.stock)
    await callback.message.answer("Шаг 7/9 — Остаток на складе (или «-» = безлимит):",
                                  reply_markup=cancel_keyboard())


@router.message(AdminAddItem.stock)
async def add_item_stock(message: Message, state: FSMContext):
    text = message.text.strip()
    if text == "-":
        stock = -1
    else:
        try:
            stock = int(text)
        except ValueError:
            await message.answer("❌ Введи целое число или «-».")
            return
    await state.update_data(stock=stock)
    data = await state.get_data()
    cat = data.get('category')
    if cat == 'weapon':
        await state.set_state(AdminAddItem.stats)
        await message.answer("Шаг 8/9 — Урон оружия (число), 0 если нет:",
                             reply_markup=cancel_keyboard())
        return
    if cat == 'equipment':
        await state.set_state(AdminAddItem.stats)
        await message.answer("Шаг 8/9 — Защита снаряжения (число), 0 если нет:",
                             reply_markup=cancel_keyboard())
        return
    await _go_add_item_producer(message, state)


@router.message(AdminAddItem.stats, F.text.regexp(r"^\d+$"))
async def add_item_stats(message: Message, state: FSMContext):
    data = await state.get_data()
    value = int(message.text)
    if data.get('category') == 'weapon':
        await state.update_data(damage=value)
    else:
        await state.update_data(armor=value)
    await _go_add_item_producer(message, state)


@router.message(AdminAddItem.stats)
async def add_item_stats_bad(message: Message):
    await message.answer("❌ Введи число (0 — если не требуется). Или /cancel.")


async def _go_add_item_producer(message: Message, state: FSMContext):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    await state.set_state(AdminAddItem.producer)
    await message.answer(
        "Шаг 9/9 — Кто продаёт этот товар?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏛️ Гос. магазин", callback_data="prod:state")],
            [InlineKeyboardButton(text="👤 Игрок-продавец", callback_data="prod:player")],
        ])
    )


@router.callback_query(F.data.startswith("prod:"))
async def add_item_producer(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    choice = callback.data.split(":")[1]
    if choice == "player":
        await state.set_state(AdminAddItem.producer_user)
        await callback.message.answer(
            "Шаг 8/9 — Введи @username или ID игрока, который продаёт этот товар "
            "(выручка с налогом уйдёт ему):",
            reply_markup=cancel_keyboard()
        )
        return
    await state.update_data(produced_by=None)
    await state.set_state(AdminAddItem.photo)
    await callback.message.answer(
        "Шаг 9/9 — Загрузи фото товара (или «-» если без фото):",
        reply_markup=cancel_keyboard()
    )


@router.message(AdminAddItem.producer_user)
async def add_item_producer_user(message: Message, state: FSMContext):
    producer = await find_user(message.text)
    if not producer:
        await message.answer("❌ Игрок не найден. Попробуй @username или ID (или /cancel):")
        return
    await state.update_data(produced_by=producer['user_id'])
    await state.set_state(AdminAddItem.photo)
    await message.answer(
        "Шаг 9/9 — Загрузи фото товара (или «-» если без фото):",
        reply_markup=cancel_keyboard()
    )


@router.message(AdminAddItem.photo)
async def add_item_photo(message: Message, state: FSMContext):
    photo_file_id = None
    if message.photo:
        photo_file_id = message.photo[-1].file_id
    else:
        text = message.text.strip()
        if text not in ("-", "—"):
            await message.answer("❌ Отправь фото или «-»:")
            return
    await state.update_data(photo_file_id=photo_file_id)

    data = await state.get_data()
    admin_id = message.from_user.id
    stock = data['stock']

    item_id = await add_item(
        name=data['name'], description=data.get('desc'),
        price=data['price'], sell_price=data['sell_price'],
        rarity=data['rarity'], category=data['category'],
        stock=stock, added_by=admin_id,
        photo_file_id=data.get('photo_file_id'),
        produced_by=data.get('produced_by'),
        damage=data.get('damage', 0), armor=data.get('armor', 0),
    )
    await log_action(admin_id, 'add_item', data.get('produced_by'),
                     f"item={data['name']} id={item_id}")
    await state.clear()
    stats_line = ""
    if data.get('damage'):
        stats_line += f"\n⚔️ Урон: {data['damage']}"
    if data.get('armor'):
        stats_line += f"\n🛡️ Защита: {data['armor']}"
    await message.answer(
        f"✅ Товар добавлен!\n\n"
        f"«{data['name']}»\n"
        f"Цена: {data['price']} {plural_nordmark(data['price'])}\n"
        f"Продажа: {data['sell_price']} {plural_nordmark(data['sell_price'])}\n"
        f"Редкость: {RARITY_LEVELS.get(data['rarity'])}\n"
        f"Категория: {ITEM_CATEGORIES.get(data['category'], data['category'])}\n"
        f"Остаток: {'безлимит' if stock == -1 else stock}"
        f"{stats_line}"
    )


@router.callback_query(F.data == "shop_admin:delete")
async def shop_admin_delete(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_delete_items"):
        await callback.message.answer("❌ Нет прав на удаление товаров.")
        return
    items = await get_available_items()
    if not items:
        await callback.message.answer("В магазине пока нет товаров.")
        return

    rows = []
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    for it in items:
        rows.append([InlineKeyboardButton(
            text=f"{it['name']} ({it['price']} НМ)",
            callback_data=f"del_item:{it['id']}"
        )])
    rows.append([InlineKeyboardButton(text="🔙 Назад", callback_data="admin:shop")])
    await callback.message.edit_text(
        "Выберите товар для удаления:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows)
    )


@router.callback_query(F.data.startswith("del_item:"))
async def delete_item_cb(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_delete_items"):
        return
    item_id = int(callback.data.split(":")[1])
    item = await get_item(item_id)
    if not item:
        await callback.message.answer("Товар не найден.")
        return
    await delete_item(item_id)
    await log_action(callback.from_user.id, 'delete_item', None, f"item={item['name']} id={item_id}")
    await callback.message.answer(f"🗑 Товар «{item['name']}» удалён.")


@router.callback_query(F.data == "shop_admin:edit")
async def shop_admin_edit(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_edit_items"):
        await callback.message.answer("❌ Нет прав на изменение товаров.")
        return
    items = await get_available_items()
    if not items:
        await callback.message.answer("В магазине пока нет товаров.")
        return

    rows = []
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    for it in items:
        rows.append([InlineKeyboardButton(
            text=f"{it['name']}",
            callback_data=f"edit_item:{it['id']}"
        )])
    rows.append([InlineKeyboardButton(text="🔙 Назад", callback_data="admin:shop")])
    await callback.message.edit_text("Выберите товар для изменения:",
                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))


@router.callback_query(F.data.startswith("edit_item:"))
async def edit_item_pick(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    item_id = int(callback.data.split(":")[1])
    await state.update_data(item_id=item_id)
    await state.set_state(AdminEditItem.field)
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    await callback.message.edit_text(
        "Что изменить?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Название", callback_data="field:name")],
            [InlineKeyboardButton(text="Цену", callback_data="field:price")],
            [InlineKeyboardButton(text="Продажу", callback_data="field:sell_price")],
            [InlineKeyboardButton(text="Остаток", callback_data="field:stock")],
            [InlineKeyboardButton(text="Категория", callback_data="field:category")],
            [InlineKeyboardButton(text="Описание", callback_data="field:description")],
            [InlineKeyboardButton(text="⚔️ Урон (оружие)", callback_data="field:damage")],
            [InlineKeyboardButton(text="❤️ Лечение", callback_data="field:heal")],
            [InlineKeyboardButton(text="🛡️ Броня", callback_data="field:armor")],
            [InlineKeyboardButton(text="⚡ AP за использование", callback_data="field:ap_cost")],
            [InlineKeyboardButton(text="🔒 Требуемый статус", callback_data="field:required_status")],
            [InlineKeyboardButton(text="🚧 Вкл/выкл продажу", callback_data="field:is_available")],
        ])
    )


@router.callback_query(F.data.startswith("field:required_status"))
async def edit_item_field_status(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    statuses = await get_all_statuses()
    rows = []
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    for s in statuses:
        rows.append([InlineKeyboardButton(text=f"{s['name']}", callback_data=f"field_req:{s['id']}")])
    rows.append([InlineKeyboardButton(text="➖ Без статуса", callback_data="field_req:none")])
    await callback.message.edit_text(
        "Выбери статус, требуемый для покупки этого товара:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows)
    )


@router.callback_query(F.data.startswith("field_req:"))
async def edit_item_field_req(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    item_id = data['item_id']
    val = callback.data.split(":")[1]
    if val == "none":
        tag = None
    else:
        s = await get_status(int(val))
        tag = s['access_tag'] if s else None
    await update_item(item_id, required_status=tag)
    await log_action(callback.from_user.id, 'edit_item', None, f"item_id={item_id} required_status={tag}")
    await state.clear()
    await callback.message.answer("✅ Требуемый статус обновлён.")


@router.callback_query(F.data.startswith("field:"))
async def edit_item_field(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    field = callback.data.split(":")[1]
    await state.update_data(field=field)
    await state.set_state(AdminEditItem.value)
    await callback.message.answer("Введи новое значение (или «-» для очистки/безлимита):",
                                  reply_markup=cancel_keyboard())


@router.message(AdminEditItem.value)
async def edit_item_value(message: Message, state: FSMContext):
    text = message.text.strip()
    data = await state.get_data()
    field = data['field']
    item_id = data['item_id']

    if field in ("price", "sell_price"):
        if text == "-":
            await message.answer("❌ Цену/продажу нельзя очистить. Введи число:")
            return
        try:
            value = int(text)
        except ValueError:
            await message.answer("❌ Введи целое число:")
            return
    elif field in ("stock", "damage", "heal", "armor", "ap_cost", "is_available"):
        value = -1 if (text == "-" and field == "stock") else int(text)
    else:
        value = None if text == "-" else text

    await update_item(item_id, **{field: value})
    await log_action(message.from_user.id, 'edit_item', None, f"item_id={item_id} {field}={value}")
    await state.clear()
    await message.answer("✅ Изменения сохранены.")


# ============ ФИНАНСЫ ============

@router.callback_query(F.data == "admin:finance")
async def admin_finance(callback: CallbackQuery):
    await callback.answer()
    if not (await has_permission(callback.from_user.id, "can_manage_finance")
            or await has_permission(callback.from_user.id, "can_add_currency")
            or await has_permission(callback.from_user.id, "can_remove_currency")):
        await callback.message.answer("❌ Нет прав для управления финансами.")
        return
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    can_add = await has_permission(callback.from_user.id, "can_add_currency")
    can_remove = await has_permission(callback.from_user.id, "can_remove_currency")
    can_full = await has_permission(callback.from_user.id, "can_manage_finance")

    buttons = []
    if can_add:
        buttons.append([InlineKeyboardButton(text="Начислить НМ", callback_data="fin:nord:add")])
    if can_remove:
        buttons.append([InlineKeyboardButton(text="Списать НМ", callback_data="fin:nord:sub")])
    if can_full:
        buttons.append([InlineKeyboardButton(text="Начислить AP", callback_data="fin:ap:add")])
        buttons.append([InlineKeyboardButton(text="Списать AP", callback_data="fin:ap:sub")])
    if can_full:
        buttons.append([InlineKeyboardButton(text="🏛️ Казна", callback_data="admin:treasury")])
        buttons.append([InlineKeyboardButton(text="📊 Налог на отчёты", callback_data="admin:tax")])
        buttons.append([InlineKeyboardButton(text="📊 Налог на продажи", callback_data="admin:saletax")])
        buttons.append([InlineKeyboardButton(text="💰 Зарплаты", callback_data="admin:salaries")])
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="admin:menu")])

    await callback.message.edit_text(
        "💰 ФИНАНСЫ\n\nВыберите операцию:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )


@router.callback_query(F.data == "admin:treasury")
async def admin_treasury(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_finance"):
        await callback.message.answer("❌ Нет прав для управления казной.")
        return

    balance = await get_treasury_balance()
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    await callback.message.edit_text(
        f"🏛️ КАЗНА НОРДХАЙМА\n\n"
        f"Баланс: {balance} {plural_nordmark(balance)}\n\n"
        f"Налог с отчётов и пожертвования пополняют казну.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💸 Выдать из казны", callback_data="treasury:give")],
            [InlineKeyboardButton(text="📊 Статистика казны", callback_data="treasury:stats")],
            [InlineKeyboardButton(text="🔙 В финансы", callback_data="admin:finance")],
        ])
    )


@router.callback_query(F.data == "treasury:stats")
async def treasury_stats(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_finance"):
        await callback.message.answer("❌ Нет прав.")
        return
    stats = await get_treasury_stats()
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    lines = []
    lines.append(f"💰 Поступило: {stats['incoming_total']} {plural_nordmark(stats['incoming_total'])} ({stats['incoming_count']} оп.)")
    lines.append(f"💸 Выплачено: {stats['outgoing_total']} {plural_nordmark(stats['outgoing_total'])}")

    by_desc = stats['by_desc']
    if by_desc:
        lines.append("\n📥 Поступление по источникам:")
        for r in by_desc:
            d = r['description'] or "без описания"
            if len(d) > 40:
                d = d[:37] + "…"
            lines.append(f"  • {d}: +{r['total']} ({r['cnt']})")

    by_to = stats['by_to']
    if by_to:
        lines.append("\n📤 Выплаты по получателям:")
        for r in by_to:
            uname = await _uid_label(r['to_user'])
            lines.append(f"  • {uname}: −{r['total']} ({r['cnt']})")

    by_from = stats['by_from']
    if by_from:
        lines.append("\n📥 Пожертвования от игроков:")
        for r in by_from:
            uname = await _uid_label(r['from_user'])
            lines.append(f"  • {uname}: +{r['total']} ({r['cnt']})")

    text = "🏛️ СТАТИСТИКА КАЗНЫ\n\n" + "\n".join(lines)
    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 В казну", callback_data="admin:treasury")],
        ])
    )


async def _uid_label(user_id: int) -> str:
    u = await get_user(user_id)
    if u:
        return f"@{u['username']}" if u['username'] else (u['first_name'] or f"#{user_id}")
    return f"#{user_id}"


@router.callback_query(F.data == "treasury:give")
async def treasury_give(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_finance"):
        await callback.message.answer("❌ Нет прав.")
        return
    await state.set_state(AdminTreasury.amount)
    balance = await get_treasury_balance()
    await callback.message.answer(
        f"🏛️ Баланс казны: {balance} {plural_nordmark(balance)}\n"
        f"Введи сумму для выдачи:",
        reply_markup=cancel_keyboard()
    )


@router.message(AdminTreasury.amount)
async def treasury_amount(message: Message, state: FSMContext):
    try:
        amount = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Введи целое число.")
        return
    if amount <= 0:
        await message.answer("❌ Сумма должна быть больше нуля.")
        return

    balance = await get_treasury_balance()
    if amount > balance:
        await message.answer(f"❌ В казне недостаточно средств. Доступно: {balance} {plural_nordmark(balance)}.")
        return

    await state.update_data(amount=amount)
    await state.set_state(AdminTreasury.target)
    markup = await pilot_picker_markup("treasury_target")
    await message.answer("Кому выдать из казны?", reply_markup=markup)


@router.message(AdminTreasury.target)
async def treasury_target_manual(message: Message, state: FSMContext):
    target = await find_user(message.text)
    if not target:
        await message.answer("❌ Игрок не найден. Попробуй ещё раз (или /cancel):")
        return
    data = await state.get_data()
    amount = data['amount']
    await transfer_from_treasury(
        target['user_id'],
        amount,
        f"Выдача из казны админом #{message.from_user.id}"
    )
    await log_action(message.from_user.id, 'treasury', target['user_id'], f"give {amount}")
    await state.clear()
    await message.answer(f"✅ Из казны выдано {amount} {plural_nordmark(amount)}.")


@router.callback_query(F.data == "admin:tax")
async def admin_tax_view(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_finance"):
        await callback.message.answer("❌ Нет прав для управления налогом.")
        return
    current = await get_report_tax_percent()
    await state.set_state(AdminTax.percent)
    await callback.message.edit_text(
        f"📊 НАЛОГ НА ОТЧЁТЫ\n\n"
        f"Текущая ставка: {current}%\n\n"
        f"Введи новую ставку налога (0–100) для всех граждан:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 В финансы", callback_data="admin:finance")]
        ])
    )


@router.message(AdminTax.percent)
async def admin_tax_set(message: Message, state: FSMContext):
    try:
        percent = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Введи целое число от 0 до 100:")
        return
    if not 0 <= percent <= 100:
        await message.answer("❌ Ставка должна быть от 0 до 100:")
        return
    await set_report_tax_percent(percent)
    await log_action(message.from_user.id, 'set_tax', None, f"percent={percent}")
    await state.clear()
    await message.answer(
        f"✅ Налог на отчёты установлен: {percent}%.\n"
        f"Изменение действует сразу для всех граждан."
    )


@router.callback_query(F.data == "admin:saletax")
async def admin_saletax_view(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_finance"):
        await callback.message.answer("❌ Нет прав для управления налогом.")
        return
    current = await get_sale_tax_percent()
    await state.set_state(AdminSaleTax.percent)
    await callback.message.edit_text(
        f"📊 НАЛОГ НА ПРОДАЖИ\n\n"
        f"Текущая ставка: {current}%\n\n"
        f"С продаж товаров игроков в магазине берётся этот процент "
        f"(выручка продавцу приходит за вычетом налога).\n\n"
        f"Введи новую ставку (0–100):",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 В финансы", callback_data="admin:finance")]
        ])
    )


@router.message(AdminSaleTax.percent)
async def admin_saletax_set(message: Message, state: FSMContext):
    try:
        percent = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Введи целое число от 0 до 100:")
        return
    if not 0 <= percent <= 100:
        await message.answer("❌ Ставка должна быть от 0 до 100:")
        return
    await set_sale_tax_percent(percent)
    await log_action(message.from_user.id, 'set_sale_tax', None, f"percent={percent}")
    await state.clear()
    await message.answer(
        f"✅ Налог на продажи установлен: {percent}%.\n"
        f"Изменение действует сразу для всех товаров игроков."
    )


@router.callback_query(F.data == "fin:manual")
async def finance_manual(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(AdminFinance.target)
    await callback.message.answer(
        "Введи получателя: @username или numeric ID игрока:",
        reply_markup=cancel_keyboard()
    )


@router.callback_query(F.data.startswith("fin:"))
async def finance_pick(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    parts = callback.data.split(":")
    if len(parts) < 3:
        await callback.message.answer("❌ Некорректный вызов.")
        return
    currency = parts[1]
    action = parts[2]
    await state.update_data(currency=currency, action=action)
    await state.set_state(AdminFinance.target)

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    users = await get_all_users()
    rows = []
    if users:
        for u in users[:50]:
            label = u['first_name'] or u['username'] or str(u['user_id'])
            if u['username']:
                label += f" (@{u['username']})"
            rows.append([InlineKeyboardButton(text=label, callback_data=f"finuser:{u['user_id']}")])
    rows.append([InlineKeyboardButton(text="✍️ Ввести вручную", callback_data="fin:manual")])
    rows.append([InlineKeyboardButton(text="🔙 Отмена", callback_data="admin:menu")])

    await callback.message.answer(
        "Выбери пилота или введи @username/ID:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows)
    )


@router.callback_query(F.data.startswith("finuser:"))
async def finance_pick_user(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    user_id = int(callback.data.split(":")[1])
    target = await get_user(user_id)
    if not target:
        await callback.message.answer("❌ Игрок не найден.")
        return
    await state.update_data(target_id=target['user_id'], target_name=target['first_name'] if 'first_name' in target.keys() else '')
    await state.set_state(AdminFinance.amount)
    await callback.message.answer(
        f"Игрок: {target['first_name'] if 'first_name' in target.keys() else ''} (@{target['username'] if 'username' in target.keys() else ''})\nВведи сумму:",
        reply_markup=cancel_keyboard()
    )


@router.message(AdminFinance.target)
async def finance_target(message: Message, state: FSMContext):
    target = await find_user(message.text)
    if not target:
        await message.answer("❌ Игрок не найден. Попробуй ещё раз (или /cancel):")
        return
    await state.update_data(target_id=target['user_id'], target_name=target['first_name'] if 'first_name' in target.keys() else '')
    await state.set_state(AdminFinance.amount)
    await message.answer(f"Игрок: {target['first_name'] if 'first_name' in target.keys() else ''} (@{target['username'] if 'username' in target.keys() else ''})\nВведи сумму:",
                         reply_markup=cancel_keyboard())


@router.message(AdminFinance.amount)
async def finance_amount(message: Message, state: FSMContext):
    try:
        amount = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Введи целое число.")
        return
    if amount <= 0:
        await message.answer("❌ Сумма должна быть больше нуля.")
        return

    data = await state.get_data()
    target_id = data['target_id']
    currency = data['currency']
    action = data['action']
    admin = message.from_user.id

    if currency == "nord":
        if action == "add":
            # Суточный лимит начислений для Квестора (5000 НМ/день)
            roles = await get_user_role(admin)
            if "finance_helper" in roles:
                from datetime import date
                today = date.today().isoformat()
                spent = await get_daily_spent(admin, today)
                remaining = 5000 - spent
                if amount > remaining:
                    await message.answer(
                        f"❌ Превышен суточный лимит Квестора (5000 НМ).\n"
                        f"Доступно сегодня: {remaining} {plural_nordmark(remaining)}."
                    )
                    return
                await add_daily_spent(admin, today, amount)
            await add_nordmarks(target_id, amount, "admin", f"Начислено админом #{admin}")
            verb = "начислено"
        else:
            await remove_nordmarks(target_id, amount, "admin", f"Списано админом #{admin}")
            verb = "списано"
        unit = plural_nordmark(amount)
    else:
        if action == "add":
            await add_ap(target_id, amount)
            verb = "начислено"
        else:
            ok = await remove_ap(target_id, amount)
            if not ok:
                await message.answer("❌ У игрока недостаточно AP.")
                return
            verb = "списано"
        unit = "AP"

    await log_action(admin, 'finance', target_id, f"{currency} {action} {amount}")
    await state.clear()
    await message.answer(
        f"✅ Игроку {data['target_name']} {verb} {amount} {unit}."
    )


# ============ РОЛИ ============

@router.callback_query(F.data == "admin:roles")
async def admin_roles(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_admins"):
        await callback.message.answer("❌ Нет прав для управления ролями.")
        return
    await state.set_state(AdminRoles.target)
    markup = await pilot_picker_markup("roles_action")
    await callback.message.answer(
        "👑 УПРАВЛЕНИЕ РОЛЯМИ\n\nВыбери пилота:",
        reply_markup=markup
    )


@router.message(AdminRoles.target)
async def roles_target(message: Message, state: FSMContext):
    target = await find_user(message.text)
    if not target:
        await message.answer("❌ Игрок не найден. Попробуй ещё раз (или /cancel):")
        return
    await state.update_data(target_id=target['user_id'], target_name=target['first_name'] if 'first_name' in target.keys() else '')
    await state.set_state(AdminRoles.action)
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    role_names = [role_label(r) for r in await get_user_role(target['user_id'])]
    await message.answer(
        f"Игрок: {target['first_name'] if 'first_name' in target.keys() else ''}\nТекущие роли: {', '.join(role_names)}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Выдать роль", callback_data="rolop:add")],
            [InlineKeyboardButton(text="Снять роль", callback_data="rolop:remove")],
        ])
    )


@router.callback_query(F.data.startswith("rolop:"))
async def roles_action(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    action = callback.data.split(":")[1]
    await state.update_data(action=action)
    await state.set_state(AdminRoles.role)
    rows = []
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    for role_name, perms in ROLES.items():
        label = role_label(role_name)
        rows.append([InlineKeyboardButton(text=label, callback_data=f"role:{role_name}")])
    if action == "add":
        rows.pop(0)  # super_admin выдаём только через отдельную команду — защита
    await callback.message.edit_text(
        f"Выбери роль для {'выдачи' if action == 'add' else 'снятия'}:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows)
    )


@router.callback_query(F.data.startswith("role:"))
async def roles_apply(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    role = callback.data.split(":")[1]
    data = await state.get_data()
    target_id = data['target_id']
    admin = callback.from_user.id
    action = data['action']

    if role == "super_admin":
        await callback.message.answer("❌ Роль «Хранитель» защищена от выдачи через панель.")
        return

    if action == "add":
        ok, msg = await add_role(admin, target_id, role)
    else:
        ok, msg = await remove_role(admin, target_id, role)

    await state.clear()
    await callback.message.answer(("✅ " if ok else "❌ ") + msg)


# ============ СТАТУСЫ ============

@router.callback_query(F.data == "admin:statuses")
async def admin_statuses(callback: CallbackQuery):
    await callback.answer()
    if not (await has_permission(callback.from_user.id, "can_manage_statuses")
            or await has_permission(callback.from_user.id, "can_grant_statuses")):
        await callback.message.answer("❌ Нет прав для управления статусами.")
        return

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    rows = []
    if await has_permission(callback.from_user.id, "can_manage_statuses"):
        rows.append([InlineKeyboardButton(text="➕ Создать статус", callback_data="st:create")])
        rows.append([InlineKeyboardButton(text="❌ Удалить статус", callback_data="st:delete")])
    if await has_permission(callback.from_user.id, "can_grant_statuses") or \
       await has_permission(callback.from_user.id, "can_manage_statuses"):
        rows.append([InlineKeyboardButton(text="🎁 Выдать статус игроку", callback_data="st:grant")])
        rows.append([InlineKeyboardButton(text="🚫 Снять статус у игрока", callback_data="st:revoke")])
    rows.append([InlineKeyboardButton(text="📋 Список статусов", callback_data="st:list")])
    rows.append([InlineKeyboardButton(text="🔙 В меню", callback_data="admin:menu")])
    await callback.message.edit_text(
        "🎖️ УПРАВЛЕНИЕ СТАТУСАМИ\n\nВыбери действие:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows)
    )


@router.callback_query(F.data == "st:list")
async def statuses_list(callback: CallbackQuery):
    await callback.answer()
    statuses = await get_all_statuses()
    if not statuses:
        await callback.message.edit_text("Статусы пока не созданы.", reply_markup=None)
        return
    lines = ["🎖️ ВСЕ СТАТУСЫ:\n"]
    for s in statuses:
        tag = f" ({s['access_tag']})" if s['access_tag'] else ""
        lines.append(f"• {s['name']}{tag} — уровень {s['sort_order']}")
        if s['description']:
            lines.append(f"    — {s['description']}")
    from keyboards.keyboards import back_to_main
    await callback.message.edit_text("\n".join(lines), reply_markup=back_to_main())


@router.callback_query(F.data == "st:create")
async def status_create_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_statuses"):
        await callback.message.answer("❌ Нет прав.")
        return
    await state.set_state(AdminStatuses.name)
    await callback.message.answer(
        "🎖️ Создание статуса. Шаг 1/3\nВведи название (например: «Ветеран», «VIP»):",
        reply_markup=cancel_keyboard()
    )


@router.message(AdminStatuses.name)
async def status_create_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await state.set_state(AdminStatuses.tag)
    await message.answer(
        "Шаг 2/3 — Ключ доступа (латиницей, без пробелов, например v i p — напиши как VIP):\n"
        "Этот ключ используется, чтобы привязывать товары/здания. Или «-» если не нужен:",
        reply_markup=cancel_keyboard()
    )


@router.message(AdminStatuses.tag)
async def status_create_tag(message: Message, state: FSMContext):
    text = message.text.strip()
    if text == "-":
        await state.update_data(tag=None)
    else:
        tag = "".join(c for c in text if c.isalnum())
        await state.update_data(tag=tag or None)
    await state.set_state(AdminStatuses.level)
    await message.answer(
        "Шаг 3/4 — Уровень статуса (целое число от 0 до 20, макс. 20).\n"
        "Чем больше, тем сильнее статус. Уровень открывает весь доступ более слабых статусов.\n"
        "Базовый «Пилот» — 0, «Турист» — -10. Введи уровень (например: 5):",
        reply_markup=cancel_keyboard()
    )


@router.message(AdminStatuses.level)
async def status_create_level(message: Message, state: FSMContext):
    text = message.text.strip()
    try:
        sort_order = int(text)
    except ValueError:
        await message.answer("❌ Введи целое число (уровень статуса):")
        return
    if not 0 <= sort_order <= 20:
        await message.answer("❌ Уровень должен быть от 0 до 20 (макс. сейчас 20):")
        return
    await state.update_data(sort_order=sort_order)
    await state.set_state(AdminStatuses.desc)
    await message.answer("Шаг 4/4 — Описание (или «-» если нет):", reply_markup=cancel_keyboard())


@router.message(AdminStatuses.desc)
async def status_create_desc(message: Message, state: FSMContext):
    text = message.text.strip()
    data = await state.get_data()
    desc = None if text == "-" else text
    ok, res = await create_status(data['name'], data.get('tag'), desc, message.from_user.id,
                                  sort_order=data.get('sort_order', 0))
    await state.clear()
    if ok:
        await log_action(message.from_user.id, 'create_status', None,
                         f"status={data['name']} id={res} level={data.get('sort_order',0)}")
        await message.answer(f"✅ Статус «{data['name']}» создан (уровень {data.get('sort_order',0)})!")
    else:
        await message.answer(f"❌ {res}")


@router.callback_query(F.data == "st:delete")
async def status_delete_menu(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_statuses"):
        await callback.message.answer("❌ Нет прав.")
        return
    statuses = await get_all_statuses()
    if not statuses:
        await callback.message.answer("Статусы не созданы.")
        return
    rows = []
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    for s in statuses:
        rows.append([InlineKeyboardButton(text=f"Удалить: {s['name']}", callback_data=f"st_del:{s['id']}")])
    rows.append([InlineKeyboardButton(text="🔙 Назад", callback_data="admin:statuses")])
    await callback.message.edit_text("Выбери статус для удаления:",
                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))


@router.callback_query(F.data.startswith("st_del:"))
async def status_delete_cb(callback: CallbackQuery):
    await callback.answer()
    status_id = int(callback.data.split(":")[1])
    s = await get_status(status_id)
    await delete_status(status_id)
    await log_action(callback.from_user.id, 'delete_status', None, f"status_id={status_id}")
    await callback.message.answer(f"🗑 Статус «{s['name']}» удалён." if s else "Удалено.")


@router.callback_query(F.data == "st:grant")
async def status_grant_target(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(AdminStatuses.target)
    markup = await pilot_picker_markup("status_pick")
    await callback.message.answer("Выбери пилота для выдачи/снятия статуса:", reply_markup=markup)


@router.callback_query(F.data == "st:revoke")
async def status_revoke_target(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(AdminStatuses.target)
    markup = await pilot_picker_markup("status_revoke")
    await callback.message.answer("У кого снять статус? Выбери пилота:", reply_markup=markup)


@router.message(AdminStatuses.target)
async def status_grant_target_msg(message: Message, state: FSMContext):
    target = await find_user(message.text)
    if not target:
        await message.answer("❌ Игрок не найден. Попробуй ещё раз:")
        return
    await state.update_data(target_id=target['user_id'], target_name=target['first_name'] if 'first_name' in target.keys() else '')
    await state.set_state(AdminStatuses.status_pick)

    have = await get_user_statuses(target['user_id'])
    have_names = ", ".join(s['name'] for s in have) if have else "нет"

    statuses = await get_all_statuses()
    if not statuses:
        await message.answer("❌ Сначала создай хотя бы один статус.")
        await state.clear()
        return

    rows = []
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    for s in statuses:
        rows.append([InlineKeyboardButton(text=f"{s['name']}", callback_data=f"st_pick:{s['id']}")])
    await message.answer(
        f"Игрок: {target['first_name'] if 'first_name' in target.keys() else ''}\nТекущие статусы: {have_names}\n\nВыбери статус:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows)
    )


@router.callback_query(F.data.startswith("st_rev:"))
async def status_revoke_pick(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    status_id = int(callback.data.split(":")[1])
    data = await state.get_data()
    target_id = data.get('target_id')
    if not target_id:
        await callback.message.answer("❌ Сессия устарела, начни заново.")
        return
    s = await get_status(status_id)
    await revoke_status(target_id, status_id)
    await log_action(callback.from_user.id, 'revoke_status', target_id, f"status={s['name']}" if s else f"status_id={status_id}")
    await state.clear()
    await callback.message.answer(f"🚫 Статус «{s['name']}» снят с игрока." if s else "Статус снят.")


@router.callback_query(F.data.startswith("st_pick:"))
async def status_grant_pick(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    status_id = int(callback.data.split(":")[1])
    await state.update_data(status_id=status_id)
    await state.set_state(AdminStatuses.grant_action)
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    await callback.message.edit_text(
        "Что сделать?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Выдать статус", callback_data="st_op:grant")],
            [InlineKeyboardButton(text="Снять статус", callback_data="st_op:revoke")],
        ])
    )


@router.callback_query(F.data.startswith("st_op:"))
async def status_grant_apply(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    op = callback.data.split(":")[1]
    data = await state.get_data()
    target_id = data['target_id']
    status_id = data['status_id']
    s = await get_status(status_id)
    admin = callback.from_user.id

    if op == "grant":
        ok, msg = await grant_status(target_id, status_id, admin)
        await log_action(admin, 'grant_status', target_id, f"status={s['name']}")
    else:
        await revoke_status(target_id, status_id)
        ok, msg = True, "Статус снят"
        await log_action(admin, 'revoke_status', target_id, f"status={s['name']}")

    await state.clear()
    await callback.message.answer(("✅ " if ok else "❌ ") + msg)


# ============ НАГРАДЫ ============

@router.callback_query(F.data == "admin:awards")
async def admin_awards(callback: CallbackQuery):
    await callback.answer()
    if not (await has_permission(callback.from_user.id, "can_manage_awards")
            or await has_permission(callback.from_user.id, "can_grant_awards")):
        await callback.message.answer("❌ Нет прав для управления наградами.")
        return

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    rows = []
    if await has_permission(callback.from_user.id, "can_manage_awards"):
        rows.append([InlineKeyboardButton(text="➕ Создать награду", callback_data="aw:create")])
        rows.append([InlineKeyboardButton(text="❌ Удалить награду", callback_data="aw:delete")])
    if await has_permission(callback.from_user.id, "can_grant_awards") or \
       await has_permission(callback.from_user.id, "can_manage_awards"):
        rows.append([InlineKeyboardButton(text="🎁 Выдать награду игроку", callback_data="aw:grant")])
        rows.append([InlineKeyboardButton(text="🗑 Снять награду у игрока", callback_data="aw:revoke")])
    rows.append([InlineKeyboardButton(text="📋 Список наград", callback_data="aw:list")])
    rows.append([InlineKeyboardButton(text="🔙 В меню", callback_data="admin:menu")])
    await callback.message.edit_text(
        "🏅 УПРАВЛЕНИЕ НАГРАДАМИ\n\nВыбери действие:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows)
    )


@router.callback_query(F.data == "aw:list")
async def awards_list(callback: CallbackQuery):
    await callback.answer()
    awards = await get_all_awards()
    if not awards:
        await callback.message.edit_text("Награды пока не созданы.", reply_markup=None)
        return
    lines = ["🏅 ВСЕ НАГРАДЫ:\n"]
    for a in awards:
        emoji = a['emoji'] or '🏅'
        lines.append(f"{emoji} {a['name']}")
        if a['description']:
            lines.append(f"    — {a['description']}")
        lines.append("")
    from keyboards.keyboards import back_to_main
    await callback.message.edit_text("\n".join(lines), reply_markup=back_to_main())


@router.callback_query(F.data == "aw:create")
async def award_create_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_awards"):
        await callback.message.answer("❌ Нет прав.")
        return
    await state.set_state(AdminAwards.name)
    await callback.message.answer(
        "🏅 Создание награды. Шаг 1/3\nВведи название (например: «За отвагу», «Герой Нордхайма»):",
        reply_markup=cancel_keyboard()
    )


@router.message(AdminAwards.name)
async def award_create_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await state.set_state(AdminAwards.desc)
    await message.answer("Шаг 2/3 — Описание награды (или «-» если нет):",
                         reply_markup=cancel_keyboard())


@router.message(AdminAwards.desc)
async def award_create_desc(message: Message, state: FSMContext):
    text = message.text.strip()
    await state.update_data(desc=None if text == "-" else text)
    await state.set_state(AdminAwards.emoji)
    await message.answer("Шаг 3/3 — Эмодзи награды (один символ, например 🏅, ⭐, 🎖️). Или «-» для 🏅:",
                         reply_markup=cancel_keyboard())


@router.message(AdminAwards.emoji)
async def award_create_emoji(message: Message, state: FSMContext):
    text = message.text.strip()
    emoji = text if text and text != "-" else "🏅"
    data = await state.get_data()
    ok, res = await create_award(data['name'], data.get('desc'), emoji, message.from_user.id)
    await state.clear()
    if ok:
        await log_action(message.from_user.id, 'create_award', None,
                         f"award={data['name']} id={res}")
        await message.answer(f"✅ Награда «{emoji} {data['name']}» создана!")
    else:
        await message.answer(f"❌ {res}")


@router.callback_query(F.data == "aw:delete")
async def award_delete_menu(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_awards"):
        await callback.message.answer("❌ Нет прав.")
        return
    awards = await get_all_awards()
    if not awards:
        await callback.message.answer("Награды не созданы.")
        return
    rows = []
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    for a in awards:
        emoji = a['emoji'] or '🏅'
        rows.append([InlineKeyboardButton(text=f"Удалить: {emoji} {a['name']}",
                                          callback_data=f"aw_del:{a['id']}")])
    rows.append([InlineKeyboardButton(text="🔙 Назад", callback_data="admin:awards")])
    await callback.message.edit_text("Выбери награду для удаления:",
                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))


@router.callback_query(F.data.startswith("aw_del:"))
async def award_delete_cb(callback: CallbackQuery):
    await callback.answer()
    award_id = int(callback.data.split(":")[1])
    a = await get_award(award_id)
    await delete_award(award_id)
    await log_action(callback.from_user.id, 'delete_award', None, f"award_id={award_id}")
    await callback.message.answer(f"🗑 Награда «{a['name']}» удалена." if a else "Удалено.")


@router.callback_query(F.data == "aw:grant")
async def award_grant_target(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(AdminAwards.target)
    markup = await pilot_picker_markup("awgrant")
    await callback.message.answer("Кому выдать награду? Выбери пилота:", reply_markup=markup)


@router.message(AdminAwards.target)
async def award_grant_target_msg(message: Message, state: FSMContext):
    target = await find_user(message.text)
    if not target:
        await message.answer("❌ Игрок не найден. Попробуй ещё раз:")
        return
    await state.update_data(target_id=target['user_id'], target_name=target['first_name'] if 'first_name' in target.keys() else '')
    awards = await get_all_awards()
    if not awards:
        await message.answer("❌ Сначала создай хотя бы одну награду.")
        await state.clear()
        return
    rows = []
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    for a in awards:
        emoji = a['emoji'] or '🏅'
        rows.append([InlineKeyboardButton(text=f"{emoji} {a['name']}",
                                          callback_data=f"aw_pick:{a['id']}")])
    await message.answer(
        f"Игрок: {target['first_name'] if 'first_name' in target.keys() else ''}\n\nВыбери награду:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows)
    )


@router.callback_query(F.data.startswith("aw_pick:"))
async def award_grant_pick(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    award_id = int(callback.data.split(":")[1])
    await state.update_data(award_id=award_id)
    await state.set_state(AdminAwards.comment)
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    await callback.message.edit_text(
        "Напиши комментарий к награде (или «-» если без него):",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬜ Пропустить", callback_data="aw_comment:skip")],
            [InlineKeyboardButton(text="🔙 Отмена", callback_data="admin:awards")],
        ])
    )


@router.callback_query(F.data == "aw_comment:skip")
async def award_grant_skip(callback: CallbackQuery, state: FSMContext):
    await award_grant_finish(callback, state, None)


@router.message(AdminAwards.comment)
async def award_grant_comment(message: Message, state: FSMContext):
    text = message.text.strip()
    comment = None if text == "-" else text
    data = await state.get_data()
    target_id = data['target_id']
    award_id = data['award_id']
    a = await get_award(award_id)
    admin = message.from_user.id
    ok, msg = await grant_award(target_id, award_id, admin, comment)
    await log_action(admin, 'grant_award', target_id, f"award={a['name']}" if a else f"award_id={award_id}")
    await state.clear()
    await message.answer(("✅ " if ok else "❌ ") + msg)
    if ok and a:
        from utils.notify import notify as notify_group
        await notify_group(
            message.bot,
            f"🏅 {a['emoji'] or '🏅'} {a['name']} выдана игроку {data.get('target_name', '') or target_id}"
            + (f"\n💬 {comment}" if comment else ""),
            user_id=target_id
        )


async def award_grant_finish(callback: CallbackQuery, state: FSMContext, comment):
    data = await state.get_data()
    target_id = data.get('target_id')
    award_id = data.get('award_id')
    if not target_id or not award_id:
        await callback.message.answer("❌ Сессия устарела, начни заново.")
        await state.clear()
        return
    a = await get_award(award_id)
    ok, msg = await grant_award(target_id, award_id, callback.from_user.id, comment)
    await log_action(callback.from_user.id, 'grant_award', target_id,
                     f"award={a['name']}" if a else f"award_id={award_id}")
    await state.clear()
    await callback.message.answer(("✅ " if ok else "❌ ") + msg)
    if ok and a:
        from utils.notify import notify as notify_group
        await notify_group(
            callback.message.bot,
            f"🏅 {a['emoji'] or '🏅'} {a['name']} выдана игроку {data.get('target_name', '') or target_id}"
            + (f"\n💬 {comment}" if comment else ""),
            user_id=target_id
        )


@router.callback_query(F.data == "aw:revoke")
async def award_revoke_pick_user(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(AdminAwards.award_pick)
    markup = await pilot_picker_markup("awrevoke")
    await callback.message.answer("У кого снять награду? Выбери пилота:", reply_markup=markup)


@router.callback_query(F.data.startswith("awr_grant:"))
async def award_revoke_apply(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    grant_id = int(callback.data.split(":")[1])
    await revoke_award(grant_id)
    await log_action(callback.from_user.id, 'revoke_award', None, f"grant_id={grant_id}")
    await state.clear()
    await callback.message.answer("🗑 Награда снята.")


# ============ ОТЧЁТЫ ============

@router.callback_query(F.data == "admin:reports")
async def admin_reports(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_view_reports"):
        await callback.message.answer("❌ Нет прав для просмотра отчётов.")
        return
    await show_pending_reports(callback.message)


async def show_pending_reports(message):
    reports = await get_pending_reports()
    if not reports:
        await message.answer("✅ В очереди нет отчётов на проверку.")
        return

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    report = reports[0]
    buttons = []
    if await has_permission(message.chat.id, "can_approve_reports"):
        buttons.append([
            InlineKeyboardButton(text="✅ Принять", callback_data=f"rep_ok:{report['id']}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"rep_no:{report['id']}"),
        ])
    buttons.append([InlineKeyboardButton(text="Следующий ▶️", callback_data="rep:next")])

    caption = (
        f"📋 ОТЧЁТ #{report['id']}\n\n"
        f"Пилот: {report['first_name']} (@{report['username']})\n"
        f"Войск за сутки: {report['troops_reported']}\n"
        f"К оплате (дельта): {report['credited_troops'] if ('credited_troops' in report.keys() and report['credited_troops'] is not None) else report['troops_reported']}\n"
        f"Всего войск: {report['total_troops'] if 'total_troops' in report.keys() else '—'}\n"
        f"Регион: {report['region'] or '—'}\n"
        f"Время: {report['created_at'][:16] if report['created_at'] else '—'}\n\n"
        f"Проверьте скриншот и примите решение:"
    )

    if 'screenshot_file_id' in report.keys() and report['screenshot_file_id']:
        await message.answer_photo(
            photo=report['screenshot_file_id'],
            caption=caption,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
        )
    else:
        await message.answer(
            caption,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
        )


@router.callback_query(F.data.startswith("rep_ok:"))
async def report_approve(callback: CallbackQuery, bot: Bot):
    await callback.answer()
    report_id = int(callback.data.split(":")[1])
    if not await has_permission(callback.from_user.id, "can_approve_reports"):
        await callback.message.answer("❌ Нет прав.")
        return
    report = await get_report_safe(report_id)
    # Новые отчёты начисляют дельту (может быть 0); старые (без дельты, NULL) — всю заявку.
    if 'credited_troops' in report.keys() and report['credited_troops'] is not None:
        troops = report['credited_troops']
    else:
        troops = report['troops_reported']
    pilot = await get_user(report['user_id'])
    amount = await approve_report(report_id, callback.from_user.id, troops)
    await log_action(callback.from_user.id, 'approve_report', report['user_id'], f"report={report_id}")
    await callback.message.answer(
        f"✅ Отчёт #{report_id} принят.\n"
        f"⚔️ К начислению: {amount} войск (выплата раз в сутки — в начале следующих суток)."
    )
    await show_pending_reports(callback.message)

    if pilot and amount >= NOTIFY_REPORT_MIN_TROOPS:
        await notify(bot, f"⚡ Пилот {await player_display(pilot)} сдал отчёт на {amount} очков!", pilot['user_id'])


@router.callback_query(F.data.startswith("rep_no:"))
async def report_reject(callback: CallbackQuery):
    await callback.answer()
    report_id = int(callback.data.split(":")[1])
    if not await has_permission(callback.from_user.id, "can_approve_reports"):
        await callback.message.answer("❌ Нет прав.")
        return
    report = await get_report_safe(report_id)
    await reject_report(report_id, callback.from_user.id)
    await log_action(callback.from_user.id, 'reject_report', report['user_id'], f"report={report_id}")
    await callback.message.answer("❌ Отчёт отклонён.")
    await show_pending_reports(callback.message)


@router.callback_query(F.data == "rep:next")
async def report_next(callback: CallbackQuery):
    await callback.answer()
    await show_pending_reports(callback.message)


async def get_report_safe(report_id: int):
    reports = await get_pending_reports()
    for r in reports:
        if r['id'] == report_id:
            return r
    return {"id": report_id, "user_id": 0, "troops_reported": 0}


# ============ СТАТИСТИКА РЕГИОНОВ ============

@router.callback_query(F.data == "admin:region_stats")
async def admin_region_stats(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_view_reports"):
        await callback.message.answer("❌ Нет прав для просмотра статистики.")
        return
    await show_region_stats(callback.message, refreshed=False, to_edit=callback)


@router.callback_query(F.data == "admin:region_stats_refresh")
async def admin_region_stats_refresh(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_view_reports"):
        await callback.message.answer("❌ Нет прав для просмотра статистики.")
        return
    await recompute_region_stats()
    await show_region_stats(callback.message, refreshed=True, to_edit=callback)


async def show_region_stats(message, refreshed: bool = False, to_edit: CallbackQuery = None):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    stats = await get_region_stats()
    text = "📊 СТАТИСТИКА ПО РЕГИОНАМ\n\n"
    if refreshed:
        text += "🔄 Пул обновлён.\n\n"
    elif stats:
        text += f"🗓 Данные актуальны на {stats[0]['computed_at'][:16] if stats[0] and stats[0]['computed_at'] else '—'}\n\n"
    else:
        text += "Данные ещё не рассчитаны.\n\n"

    if stats:
        for s in stats:
            region_label = f"Регион {s['region']}"
            if s['region'] == "0":
                region_label += " (Столица)"
            text += (f"🌍 {region_label}\n"
                     f"   🪖 Войска за 24ч: {s['troops_24h']}\n"
                     f"   👤 Активные пилоты (3 дн): {s['active_pilots_72h']}\n\n")
    else:
        text += "Нет данных. Регионы появятся после одобренных отчётов."

    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Обновить пул", callback_data="admin:region_stats_refresh")],
        [InlineKeyboardButton(text="👈 Назад", callback_data="admin:menu")],
    ])
    if to_edit is not None:
        await to_edit.message.edit_text(text, reply_markup=markup)
    else:
        await message.answer(text, reply_markup=markup)


# ============ ПОВЫШЕНИЕ В ЗВАНИИ ============

@router.callback_query(F.data == "admin:ranks")
async def admin_ranks(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_grant_troops"):
        await callback.message.answer("❌ Нет прав.")
        return

    players = await get_users_for_rank_promotion()
    if not players:
        await callback.message.answer(
            "📋 Нет игроков, готовых к повышению в звании.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад", callback_data="admin:menu")]
            ])
        )
        return

    buttons = []
    for p in players[:10]:
        name = p['first_name'] or p['username'] or str(p['user_id'])
        buttons.append([
            InlineKeyboardButton(
                text=f"⭐ {name} — {p['troops']} войск → {p['next_rank']}",
                callback_data=f"rank_promote:{p['user_id']}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="admin:menu")])

    await callback.message.edit_text(
        "⭐ Повышение в звании\n\n"
        "Игроки, чьи войска соответствуют званию выше Лейтенанта:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )


@router.callback_query(F.data.startswith("rank_promote:"))
async def rank_promote(callback: CallbackQuery, bot: Bot):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_grant_troops"):
        await callback.message.answer("❌ Нет прав.")
        return

    user_id = int(callback.data.split(":")[1])
    user = await get_user(user_id)
    if not user:
        await callback.message.answer("❌ Игрок не найден.")
        return

    from config import RANKS
    troops = user['troops']
    next_rank = None
    for rank_name, required in RANKS:
        if rank_name in ("Рекрут", "Рядовой", "Капрал", "Сержант", "Лейтенант"):
            continue
        if troops >= required:
            next_rank = rank_name
        else:
            break

    if not next_rank:
        await callback.message.answer("❌ У игрока нет достаточного количества войск.")
        return

    await promote_user_rank(user_id, next_rank, callback.from_user.id)
    name = user['first_name'] or user['username'] or str(user_id)
    await callback.message.answer(
        f"✅ {name} повышен до звания «{next_rank}» ({troops} войск)."
    )
    await notify(bot, f"⭐ Пилот {await player_display(user)} получил звание «{next_rank}»!", user['user_id'])
    await admin_ranks(callback)


# ============ ЛОГИ ============

@router.callback_query(F.data == "admin:logs")
async def admin_logs(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_view_logs"):
        await callback.message.answer("❌ Нет прав для просмотра логов.")
        return

    from database.db import get_db
    db = await get_db()
    cursor = await db.execute(
        "SELECT * FROM admin_logs ORDER BY id DESC LIMIT 15"
    )
    rows = await cursor.fetchall()

    if not rows:
        await callback.message.answer("Логи пока пусты.")
        return

    lines = []
    for r in rows:
        lines.append(
            f"#{r['id']} [{r['created_at'][:16] if r['created_at'] else ''}]\n"
            f"админ {r['admin_id']}: {r['action']}"
            + (f" -> {r['target_id']}" if r['target_id'] else "")
            + (f" ({r['details']})" if r['details'] else "")
        )
    await callback.message.answer("🧾 ПОСЛЕДНИЕ ДЕЙСТВИЯ АДМИНОВ:\n\n" + "\n\n".join(lines))


# ============ ОТМЕНА ============

@router.callback_query(F.data == "noop")
async def noop(callback: CallbackQuery):
    await callback.answer()


@router.callback_query(F.data == "back:main")
async def back_main_cb(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer()
    from keyboards.keyboards import main_menu_keyboard
    await callback.message.answer("Главное меню:", reply_markup=main_menu_keyboard())


@router.callback_query(F.data == "cancel")
async def cancel_cb(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    from keyboards.keyboards import main_menu_keyboard
    await callback.message.answer("Действие отменено.", reply_markup=main_menu_keyboard())


@router.message(F.text == "/cancel")
async def cancel_text(message: Message, state: FSMContext):
    await state.clear()
    from keyboards.keyboards import main_menu_keyboard
    await message.answer("Действие отменено.", reply_markup=main_menu_keyboard())


# ============ СОСТОЯНИЯ ИГРОКОВ ============

@router.callback_query(F.data == "admin:states")
async def admin_states_menu(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_states"):
        await callback.message.answer("❌ Нет прав для управления состояниями.")
        return
    await state.set_state(AdminStates.target)
    markup = await pilot_picker_markup("state_target")
    await callback.message.answer(
        "🎭 УПРАВЛЕНИЕ СОСТОЯНИЯМИ\n\nВыбери пилота:",
        reply_markup=markup
    )


@router.message(AdminStates.target)
async def admin_states_target_text(message: Message, state: FSMContext):
    target = await find_user(message.text)
    if not target:
        await message.answer("❌ Игрок не найден. Попробуй ещё раз (или /cancel):")
        return
    await state.update_data(target_id=target['user_id'])
    await state.set_state(AdminStates.action)
    from utils.states import get_state_info
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    info = await get_state_info(target['user_id'])
    await message.answer(
        f"🎭 Игрок: {target['first_name'] if 'first_name' in target.keys() else ''} (@{target['username'] if 'username' in target.keys() else ''})\n"
        f"Текущее состояние: {info['name']}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🎭 Наложить состояние", callback_data="st_op:set")],
            [InlineKeyboardButton(text="✨ Снять состояние", callback_data="st_op:clear")],
        ])
    )


@router.callback_query(F.data.startswith("st_op:"))
async def admin_states_op(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    op = callback.data.split(":")[1]
    if op == "clear":
        data = await state.get_data()
        from utils.states import clear_state_of
        await clear_state_of(data['target_id'], callback.from_user.id, "снято админом")
        await state.clear()
        await callback.message.answer("✨ Состояние снято. Игрок снова в норме.")
        return

    await state.set_state(AdminStates.state_key)
    from utils.states import STATE_CONF, state_keys
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    rows = []
    for key in state_keys():
        conf = STATE_CONF[key]
        rows.append([InlineKeyboardButton(
            text=f"{conf['emoji']} {conf['title']} ({conf['default_minutes']} мин.)",
            callback_data=f"st_key:{key}"
        )])
    # Отдельная строка — «снять» прямо отсюда
    rows.append([InlineKeyboardButton(text="✨ Снять состояние", callback_data="st_op:clear")])
    await callback.message.edit_text(
        "🎭 Выбери состояние:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows)
    )


@router.callback_query(F.data.startswith("st_key:"))
async def admin_states_key(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    key = callback.data.split(":")[1]
    await state.update_data(state_key=key)
    from utils.states import STATE_CONF
    conf = STATE_CONF[key]
    await state.set_state(AdminStates.minutes)
    await callback.message.answer(
        f"{conf['emoji']} Устанавливается состояние «{conf['title']}».\n"
        f"Срок действия в минутах (по умолчанию {conf['default_minutes']}):",
        reply_markup=cancel_keyboard()
    )


@router.message(AdminStates.minutes, F.text.regexp(r"^\d+$"))
async def admin_states_minutes(message: Message, state: FSMContext):
    data = await state.get_data()
    from utils.states import STATE_CONF, apply_state_to
    minutes = int(message.text)
    if minutes <= 0:
        await message.answer("❌ Введи число больше 0 (или /cancel).")
        return
    conf = STATE_CONF[data['state_key']]
    await apply_state_to(
        data['target_id'], data['state_key'],
        caused_by=message.from_user.id,
        minutes=minutes,
        reason=f"наложено админом на {minutes} мин.",
    )
    await state.clear()
    await message.answer(
        f"✅ {conf['emoji']} Игроку выдано состояние «{conf['title']}» на {minutes} мин."
    )


@router.message(AdminStates.minutes)
async def admin_states_minutes_bad(message: Message):
    await message.answer("❌ Введи число цифрой (минуты). Или /cancel.")


@router.callback_query(F.data == "admin:salaries")
async def admin_salaries(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_salaries"):
        await callback.message.answer("❌ Нет прав для управления зарплатами.")
        return
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    balance = await get_treasury_balance()
    salaried = await get_salaried_users()
    lines = []
    lines.append(f"🏛️ ЗАРПЛАТЫ ПИЛОТОВ\n\nКазна: {balance} {plural_nordmark(balance)}\n")
    if salaried:
        lines.append("💼 Получатели (еженедельно, в воскресенье):")
        for u in salaried:
            name = u['first_name'] or u['username'] or f"#{u['user_id']}"
            line = f"  • {name} — {u['salary']} {plural_nordmark(u['salary'])}"
            if u['salary_debt']:
                line += f"  (долг {u['salary_debt']} {plural_nordmark(u['salary_debt'])})"
            lines.append(line)
    else:
        lines.append("Получателей пока нет.")
    lines.append("\nВыплата — один раз в неделю, в воскресенье.")
    await callback.message.edit_text(
        "\n".join(lines),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ Назначить/Изменить", callback_data="salary:choose")],
            [InlineKeyboardButton(text="💸 Выплатить сейчас", callback_data="salary:pay")],
            [InlineKeyboardButton(text="🔙 В финансы", callback_data="admin:finance")],
        ])
    )


@router.callback_query(F.data == "salary:choose")
async def salary_choose(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_salaries"):
        return
    markup = await pilot_picker_markup("salary_set")
    await callback.message.edit_text(
        "Выбери пилота, которому назначишь зарплату:",
        reply_markup=markup
    )


@router.callback_query(F.data == "salary:pay")
async def salary_pay(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_salaries"):
        return
    res = await pay_salaries()
    parts = []
    if res['paid']:
        parts.append(f"✅ Выплачено зарплат: {len(res['paid'])}")
        for uid, amt in res['paid']:
            u = await get_user(uid)
            name = (u['first_name'] if (u and 'first_name' in u.keys() and u['first_name'])
                    else (u['username'] if u else f"#{uid}"))
            parts.append(f"  • {name}: {amt} {plural_nordmark(amt)}")
    else:
        parts.append("ℹ️ Нет зарплат к выплате прямо сейчас.")
    if res['debt']:
        parts.append(
            f"\n⚠️ Задолженность (не хватило казны): {len(res['debt'])} "
            f"(всего {res['reserves']} {plural_nordmark(res['reserves'])}). "
            f"Долг копится и будет выплачен при пополнении."
        )
    await callback.message.edit_text("\n".join(parts))


@router.message(AdminSalary.amount)
async def admin_salary_amount(message: Message, state: FSMContext):
    text = message.text.strip()
    if text.lower() == "/cancel":
        await message.answer("Отменено.")
        await state.clear()
        return
    try:
        amount = int(text)
    except ValueError:
        await message.answer("❌ Введи сумму цифрой (или /cancel).")
        return
    if amount < 0:
        await message.answer("❌ Сумма не может быть отрицательной.")
        return
    data = await state.get_data()
    target_id = data.get('target_id')
    target_name = data.get('target_name', '')
    if not target_id:
        await message.answer("❌ Сессия не найдена, начни заново.")
        await state.clear()
        return
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    if amount == 0:
        await set_user_salary(target_id, 0, 7, message.from_user.id)
        await state.clear()
        await message.answer(f"✅ Зарплата снята с игрока: {target_name}.")
        return
    await state.update_data(amount=amount)
    await state.set_state(AdminSalary.period)
    await message.answer(
        f"💰 Сумма: {amount} {plural_nordmark(amount)}\n\n"
        f"Введи период выплаты в днях (по умолчанию 7):",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="7 дней", callback_data="salary_period:7")],
            [InlineKeyboardButton(text="30 дней", callback_data="salary_period:30")],
        ])
    )


@router.callback_query(AdminSalary.period, F.data.startswith("salary_period:"))
async def admin_salary_period_cb(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    period = int(callback.data.split(":")[1])
    data = await state.get_data()
    target_id = data.get('target_id')
    target_name = data.get('target_name', '')
    amount = data.get('amount')
    if not target_id or amount is None:
        await state.clear()
        await callback.message.answer("❌ Сессия не найдена, начни заново.")
        return
    await set_user_salary(target_id, amount, period, callback.from_user.id)
    await state.clear()
    await callback.message.edit_text(
        f"✅ Зарплата назначена: {target_name} — {amount} {plural_nordmark(amount)} / {period} дн."
    )


@router.message(AdminSalary.period)
async def admin_salary_period_text(message: Message, state: FSMContext):
    text = message.text.strip()
    try:
        period = int(text)
    except ValueError:
        await message.answer("❌ Введи период цифрой (дни) или выбери кнопку.")
        return
    if period <= 0:
        await message.answer("❌ Период должен быть больше 0.")
        return
    data = await state.get_data()
    target_id = data.get('target_id')
    target_name = data.get('target_name', '')
    amount = data.get('amount')
    if not target_id or amount is None:
        await state.clear()
        await message.answer("❌ Сессия не найдена, начни заново.")
        return
    await set_user_salary(target_id, amount, period, message.from_user.id)
    await state.clear()
    await message.answer(
        f"✅ Зарплата назначена: {target_name} — {amount} {plural_nordmark(amount)} / {period} дн."
    )

@router.callback_query(F.data == "admin:locations")
async def admin_locations(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        await callback.message.answer("❌ Нет прав для управления локациями.")
        return
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    locs = await get_all_locations()
    lines = ["📍 ЛОКАЦИИ ГОРОДА\n"]
    if locs:
        for l in locs:
            acc = await location_access_label(l['access_mode'], l['required_status'])
            lines.append(f"• {l['name']} — {acc}")
    else:
        lines.append("Локаций пока нет.")
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Создать локацию", callback_data="loc:create")],
        [InlineKeyboardButton(text="✏️ Редактировать доступ", callback_data="loc:edit_pick")],
        [InlineKeyboardButton(text="🔙 В меню", callback_data="admin:menu")],
    ])
    await callback.message.edit_text("\n".join(lines), reply_markup=kb)


@router.callback_query(F.data == "loc:create")
async def loc_create(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    await state.update_data(action="create")
    await state.set_state(AdminLocation.key)
    await callback.message.edit_text(
        "Создание локации. Шаг 1/7 — введи уникальный ключ локации латиницей\n"
        "(например: bar, market). Без пробелов:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data="admin:locations")]
        ])
    )


@router.callback_query(F.data == "loc:edit_pick")
async def loc_edit_pick(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    locs = await get_all_locations()
    if not locs:
        await callback.message.edit_text("Локаций пока нет. Сначала создай.")
        return
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    rows = [[InlineKeyboardButton(text=l['name'], callback_data=f"loc:edit:{l['id']}")] for l in locs]
    rows.append([InlineKeyboardButton(text="🔙 Назад", callback_data="admin:locations")])
    await callback.message.edit_text("Выбери локацию для редактирования доступа:",
                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))


@router.callback_query(F.data.startswith("loc:edit:"))
async def loc_edit(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    loc_id = int(callback.data.split(":")[2])
    loc = await get_location(loc_id)
    if not loc:
        await callback.message.answer("❌ Локация не найдена.")
        return
    acc = await location_access_label(loc['access_mode'], loc['required_status'])
    blocking = ", ".join(loc['blocking_states'] or "[]") or "нет"
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    await state.update_data(action="edit", target_id=loc_id)
    await callback.message.edit_text(
        f"✏️ {loc['name']} (доступ: {acc})\nБлокируют состояния: {blocking}\n\nЧто изменить?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🎚 Режим доступа", callback_data="loc:set_mode")],
            [InlineKeyboardButton(text="🗂 Требуемый статус", callback_data="loc:set_status")],
            [InlineKeyboardButton(text="🍺 Блокирующие состояния", callback_data="loc:set_blocking")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="loc:edit_pick")],
        ])
    )


@router.callback_query(F.data == "loc:set_mode")
async def loc_set_mode(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    await state.set_state(AdminLocation.mode)
    await callback.message.edit_text(
        "Выбери режим доступа:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🌐 Всем", callback_data="loc:mode:all")],
            [InlineKeyboardButton(text="📈 Статус и выше", callback_data="loc:mode:min")],
            [InlineKeyboardButton(text="🎯 Только конкретному", callback_data="loc:mode:exact")],
            [InlineKeyboardButton(text="🔙 Отмена", callback_data="admin:locations")],
        ])
    )


@router.callback_query(AdminLocation.mode, F.data.startswith("loc:mode:"))
async def loc_mode_chosen(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    mode = callback.data.split(":")[2]
    data = await state.get_data()
    loc_id = data.get('target_id')
    if data.get('action') == 'edit' and loc_id:
        await update_location_access(loc_id, access_mode=mode)
        await state.clear()
        await callback.message.edit_text(f"✅ Режим доступа: {mode}")
    else:
        await state.update_data(mode=mode)
        if mode == "all":
            await state.update_data(req_status=None)
            await AdminLocation.blocking.set()
            await callback.message.edit_text("Какие состояния блокируют вход?\n(через запятую, напр.: пьян)")
        else:
            await AdminLocation.req_status.set()
            await _loc_status_pick(callback, state)


@router.callback_query(AdminLocation.req_status, F.data.startswith("loc:req_status:"))
async def loc_req_status_chosen(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    tag = callback.data.split(":")[2]
    data = await state.get_data()
    if data.get('action') == 'edit' and data.get('target_id'):
        await update_location_access(data['target_id'], required_status=tag)
        await state.clear()
        await callback.message.edit_text(f"✅ Требуемый статус: {tag}")
    else:
        await state.update_data(req_status=tag)
        await AdminLocation.blocking.set()
        await callback.message.edit_text("Какие состояния блокируют вход?\n(через запятую, напр.: пьян, или отправь „нет“)")


@router.callback_query(AdminLocation.blocking, F.data.startswith("loc:blocking:"))
async def loc_blocking_chosen(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    val = callback.data.split(":", 2)[2]
    if val == "none":
        blocking = []
    else:
        blocking = [s.strip() for s in val.split(",") if s.strip()]
    if data.get('action') == 'edit' and data.get('target_id'):
        await update_location_access(data['target_id'], blocking_states=blocking)
        await state.clear()
        await callback.message.edit_text("✅ Блокирующие состояния обновлены.")
    else:
        await state.update_data(blocking=blocking)
        await _finish_loc_create(callback, state)


async def _loc_status_pick(callback, state):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    statuses = await get_all_statuses()
    rows = []
    for s in statuses:
        tag = s['access_tag'] or s['name']
        rows.append([InlineKeyboardButton(text=s['name'], callback_data=f"loc:req_status:{tag}")])
    rows.append([InlineKeyboardButton(text="🔙 Отмена", callback_data="admin:locations")])
    await callback.message.edit_text("Выбери требуемый статус:",
                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))


async def _finish_loc_create(callback, state):
    data = await state.get_data()
    mode = data.get('mode') or 'all'
    req = data.get('req_status')
    blocking = data.get('blocking') or []
    ok, err = await create_location(
        key=data['key'], name=data['name'], description=data.get('description'),
        access_mode=mode, required_status=req, blocking_states=blocking
    )
    await state.clear()
    if ok:
        await callback.message.edit_text(f"✅ Локация «{data['name']}» создана.")
    else:
        await callback.message.edit_text(f"❌ Ошибка создания: {err}")


# FSM: создание локации (шаги)
@router.message(AdminLocation.key)
async def loc_step_key(message: Message, state: FSMContext):
    key = message.text.strip().lower()
    if not key or not key.replace("_", "").isalnum():
        await message.answer("❌ Ключ — латиница/цифры/подчёркивание без пробелов.")
        return
    await state.update_data(key=key)
    await state.set_state(AdminLocation.name)
    await message.answer("Шаг 2/7 — название локации:")


@router.message(AdminLocation.name)
async def loc_step_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await state.set_state(AdminLocation.description)
    await message.answer("Шаг 3/7 — описание (или отправь «-»):")


@router.message(AdminLocation.description)
async def loc_step_desc(message: Message, state: FSMContext):
    text = message.text.strip()
    await state.update_data(description=None if text == "-" else text)
    await state.set_state(AdminLocation.mode)
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    await message.answer(
        "Шаг 4/7 — режим доступа:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🌐 Всем", callback_data="loc:mode:all")],
            [InlineKeyboardButton(text="📈 Статус и выше", callback_data="loc:mode:min")],
            [InlineKeyboardButton(text="🎯 Только конкретному", callback_data="loc:mode:exact")],
        ])
    )
