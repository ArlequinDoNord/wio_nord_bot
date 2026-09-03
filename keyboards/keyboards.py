from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def main_menu_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Профиль")],
            [KeyboardButton(text="Инвентарь"), KeyboardButton(text="Магазин")],
            [KeyboardButton(text="Банк"), KeyboardButton(text="Город")],
        ],
        resize_keyboard=True
    )


def profile_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Изменить фото", callback_data="profile:set_photo")],
        [InlineKeyboardButton(text="Изменить статус", callback_data="profile:set_status")],
        [InlineKeyboardButton(text="Карточка пилота", callback_data="profile:pilot_card")],
    ])


def shop_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Каталог", callback_data="shop:catalog")],
        [InlineKeyboardButton(text="Мои покупки", callback_data="shop:my_purchases")],
        [InlineKeyboardButton(text="Продать товар", callback_data="shop:sell")],
    ])


def shop_admin_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Добавить товар", callback_data="shop_admin:add")],
        [InlineKeyboardButton(text="Удалить товар", callback_data="shop_admin:delete")],
        [InlineKeyboardButton(text="Изменить цену", callback_data="shop_admin:edit_price")],
        [InlineKeyboardButton(text="Изменить остаток", callback_data="shop_admin:edit_stock")],
    ])


def bank_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Мой баланс", callback_data="bank:balance")],
        [InlineKeyboardButton(text="Перевести", callback_data="bank:transfer")],
        [InlineKeyboardButton(text="История транзакций", callback_data="bank:history")],
    ])


def inventory_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Использовать", callback_data="inv:use")],
        [InlineKeyboardButton(text="Предложить обмен", callback_data="inv:trade")],
    ])


def trade_keyboard(trade_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Принять", callback_data=f"trade:accept:{trade_id}"),
            InlineKeyboardButton(text="Отклонить", callback_data=f"trade:decline:{trade_id}")
        ]
    ])


def back_to_main():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Назад", callback_data="back:main")]
    ])


def cancel_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Отмена", callback_data="cancel")]
    ])


def interaction_keyboard(user_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Помочь", callback_data=f"interact:help:{user_id}")],
        [InlineKeyboardButton(text="Похвалить", callback_data=f"interact:praise:{user_id}")],
        [InlineKeyboardButton(text="Поддержать", callback_data=f"interact:support:{user_id}")],
        [InlineKeyboardButton(text="Вызвать на дуэль", callback_data=f"interact:duel:{user_id}")],
    ])


def city_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Пилоты", callback_data="city:pilots")],
        [InlineKeyboardButton(text="Голосование", callback_data="city:vote")],
        [InlineKeyboardButton(text="Подземелье", callback_data="city:dungeon")],
    ])


def pagination_keyboard(items: list, page: int, per_page: int, callback_prefix: str):
    total_pages = max(1, (len(items) + per_page - 1) // per_page)
    page = max(0, min(page, total_pages - 1))
    start = page * per_page
    end = start + per_page
    current_items = items[start:end]

    buttons = []
    for item in current_items:
        rarity = item.get('rarity', 1) if hasattr(item, 'get') else 1
        buttons.append([InlineKeyboardButton(
            text=f"{item['name']} - {item['price']} НМ",
            callback_data=f"{callback_prefix}:item:{item['id']}"
        )])

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="◀️", callback_data=f"{callback_prefix}:page:{page-1}"))
    nav.append(InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="noop"))
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton(text="▶️", callback_data=f"{callback_prefix}:page:{page+1}"))
    if nav:
        buttons.append(nav)

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def confirm_keyboard(action: str, target_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Да", callback_data=f"confirm:{action}:{target_id}"),
            InlineKeyboardButton(text="Нет", callback_data="cancel")
        ]
    ])


def admin_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Управление магазином")],
            [KeyboardButton(text="Начислить НМ"), KeyboardButton(text="Отчёты на проверку")],
            [KeyboardButton(text="Управление пользователями")],
            [KeyboardButton(text="Назад")],
        ],
        resize_keyboard=True
    )


def dungeon_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚔️ Сражаться", callback_data="dungeon:fight")],
        [InlineKeyboardButton(text="📦 Инвентарь", callback_data="dungeon:inventory")],
        [InlineKeyboardButton(text="🏠 Назад", callback_data="back:main")],
    ])


def production_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Мои здания", callback_data="prod:my_buildings")],
        [InlineKeyboardButton(text="Купить здание", callback_data="prod:buy_building")],
        [InlineKeyboardButton(text="Производство", callback_data="prod:start")],
        [InlineKeyboardButton(text="Назад", callback_data="back:main")],
    ])


def report_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Сдать отчёт", callback_data="report:submit")],
        [InlineKeyboardButton(text="Мои отчёты", callback_data="report:my_reports")],
        [InlineKeyboardButton(text="Назад", callback_data="back:main")],
    ])
