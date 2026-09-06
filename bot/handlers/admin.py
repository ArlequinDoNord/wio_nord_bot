"""
Админ-панель: управление магазином, финансами, отчётами, ролями и логами.
Доступ разграничен по ролям (см. utils/permissions.py).
"""

from aiogram import Router, F
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
    get_treasury_balance, transfer_from_treasury,
    get_report_tax_percent, set_report_tax_percent,
)
from keyboards.keyboards import cancel_keyboard
from utils.permissions import (
    is_admin, has_permission, get_user_role,
    add_role, remove_role, ROLES, role_label, log_action,
)
from utils.helpers import plural_nordmark
from config import RARITY_LEVELS, RARITY_EMOJI, ITEM_CATEGORIES

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


# ============ УТИЛИТЫ ============

async def perm_flags(user_id: int) -> dict:
    perms = ["can_manage_shop", "can_manage_finance", "can_view_reports",
             "can_approve_reports", "can_manage_admins", "can_view_logs",
             "can_manage_statuses", "can_grant_statuses", "can_grant_troops"]
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
        "Выберите раздел. Доступные действия зависят от вашей роли:"
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
        "🛒 Добавление товара. Шаг 1/7\n\nВведи название товара (или /cancel):",
        reply_markup=cancel_keyboard()
    )


@router.message(AdminAddItem.name)
async def add_item_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await state.set_state(AdminAddItem.desc)
    await message.answer("Шаг 2/7 — Описание товара (или «-» если нет):",
                         reply_markup=cancel_keyboard())


@router.message(AdminAddItem.desc)
async def add_item_desc(message: Message, state: FSMContext):
    text = message.text.strip()
    await state.update_data(desc=None if text == "-" else text)
    await state.set_state(AdminAddItem.price)
    await message.answer("Шаг 3/7 — Цена в Нордмарках (целое число):",
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
    await message.answer(f"Шаг 4/7 — Цена продажи за {price}? Введи сумму (или «-» = половина):",
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
    await message.answer("Шаг 5/7 — Редкость:", reply_markup=rarity_choice_markup())


@router.callback_query(F.data.startswith("rar:"))
async def add_item_rarity(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    rarity = int(callback.data.split(":")[1])
    await state.update_data(rarity=rarity)
    await state.set_state(AdminAddItem.category)
    await callback.message.answer("Шаг 6/7 — Категория:", reply_markup=category_choice_markup())


@router.callback_query(F.data.startswith("cat:"))
async def add_item_category(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    category = callback.data.split(":")[1]
    await state.update_data(category=category)
    await state.set_state(AdminAddItem.stock)
    await callback.message.answer("Шаг 7/7 — Остаток на складе (или «-» = безлимит):",
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
    data = await state.get_data()
    admin_id = message.from_user.id

    item_id = await add_item(
        name=data['name'], description=data.get('desc'),
        price=data['price'], sell_price=data['sell_price'],
        rarity=data['rarity'], category=data['category'],
        stock=stock, added_by=admin_id,
    )
    await log_action(admin_id, 'add_item', None, f"item={data['name']} id={item_id}")
    await state.clear()
    await message.answer(
        f"✅ Товар добавлен!\n\n"
        f"«{data['name']}»\n"
        f"Цена: {data['price']} {plural_nordmark(data['price'])}\n"
        f"Продажа: {data['sell_price']} {plural_nordmark(data['sell_price'])}\n"
        f"Редкость: {RARITY_LEVELS.get(data['rarity'])}\n"
        f"Категория: {ITEM_CATEGORIES.get(data['category'], data['category'])}\n"
        f"Остаток: {'безлимит' if stock == -1 else stock}"
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
            [InlineKeyboardButton(text="Цену", callback_data="field:price")],
            [InlineKeyboardButton(text="Продажу", callback_data="field:sell_price")],
            [InlineKeyboardButton(text="Остаток", callback_data="field:stock")],
            [InlineKeyboardButton(text="Описание", callback_data="field:description")],
            [InlineKeyboardButton(text="🔒 Требуемый статус", callback_data="field:required_status")],
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
    elif field == "stock":
        value = -1 if text == "-" else int(text)
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
            [InlineKeyboardButton(text="🔙 В финансы", callback_data="admin:finance")],
        ])
    )


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
    await state.update_data(target_id=target['user_id'], target_name=target.get('first_name', ''))
    await state.set_state(AdminFinance.amount)
    await message.answer(f"Игрок: {target.get('first_name','')} (@{target.get('username','')})\nВведи сумму:",
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
    await state.update_data(target_id=target['user_id'], target_name=target.get('first_name',''))
    await state.set_state(AdminRoles.action)
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    role_names = [role_label(r) for r in await get_user_role(target['user_id'])]
    await message.answer(
        f"Игрок: {target.get('first_name','')}\nТекущие роли: {', '.join(role_names)}",
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
    await state.update_data(target_id=target['user_id'], target_name=target.get('first_name', ''))
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
        f"Игрок: {target.get('first_name','')}\nТекущие статусы: {have_names}\n\nВыбери статус:",
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
async def report_approve(callback: CallbackQuery):
    await callback.answer()
    report_id = int(callback.data.split(":")[1])
    if not await has_permission(callback.from_user.id, "can_approve_reports"):
        await callback.message.answer("❌ Нет прав.")
        return
    report = await get_report_safe(report_id)
    troops = report['troops_reported']
    tax_percent = await get_report_tax_percent()
    tax = int(troops * tax_percent / 100)
    earned = troops - tax
    await approve_report(report_id, callback.from_user.id, troops)
    await log_action(callback.from_user.id, 'approve_report', report['user_id'], f"report={report_id}")
    tax_line = f" (налог {tax_percent}%: −{tax} в казну)" if tax > 0 else ""
    await callback.message.answer(f"✅ Отчёт #{report_id} принят.\nНачислено: {troops} войск, {earned} НМ{tax_line}.")
    await show_pending_reports(callback.message)


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
async def rank_promote(callback: CallbackQuery):
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
