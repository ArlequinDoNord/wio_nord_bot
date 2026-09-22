from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def main_menu_keyboard(is_admin: bool = False, is_pilot: bool = True):
    keyboard = [
        [KeyboardButton(text="Профиль")],
        [KeyboardButton(text="Инвентарь"), KeyboardButton(text="Магазин")],
        [KeyboardButton(text="Город")],
        [KeyboardButton(text="📰 Новости Нордхайма")],
        [KeyboardButton(text="🧱 Стена изречений")],
    ]
    if is_pilot:
        keyboard.append([KeyboardButton(text="📝 Сдать отчёт")])
    if is_admin:
        keyboard.append([KeyboardButton(text="👑 Админ-панель")])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


async def main_menu_kb(user_id: int):
    """Reply-клавиатура главного меню с АКТУАЛЬНЫМИ флагами админа/пилота.

    Все обработчики («В меню», «Отмена», завершения FSM) должны перерисовывать
    главное меню именно через эту функцию, иначе у админа пропадает кнопка
    «👑 Админ-панель» после навигации (флаг пересчитывается каждый раз).
    """
    from utils.permissions import is_admin
    from database.db import user_has_status_tag
    admin_flag = await is_admin(user_id)
    pilot_flag = await user_has_status_tag(user_id, "pilot")
    return main_menu_keyboard(is_admin=admin_flag, is_pilot=pilot_flag)


def admin_panel_keyboard(permissions: dict):
    buttons = []
    if permissions.get('can_manage_shop'):
        buttons.append([InlineKeyboardButton(text="🛒 Управление магазином", callback_data="admin:shop")])
    if permissions.get('can_manage_finance') or permissions.get('can_add_currency') or permissions.get('can_remove_currency'):
        buttons.append([InlineKeyboardButton(text="💰 Финансы", callback_data="admin:finance")])
    if permissions.get('can_view_reports') or permissions.get('can_approve_reports'):
        buttons.append([InlineKeyboardButton(text="📋 Отчёты на проверку", callback_data="admin:reports")])
        buttons.append([InlineKeyboardButton(text="📊 Статистика регионов", callback_data="admin:region_stats")])
    if permissions.get('can_manage_admins'):
        buttons.append([InlineKeyboardButton(text="👑 Управление ролями", callback_data="admin:roles")])
    if permissions.get('can_manage_statuses') or permissions.get('can_grant_statuses'):
        buttons.append([InlineKeyboardButton(text="🎖️ Статусы", callback_data="admin:statuses")])
    if permissions.get('can_grant_troops'):
        buttons.append([InlineKeyboardButton(text="⭐ Повышение в звании", callback_data="admin:ranks")])
    if permissions.get('can_manage_states'):
        buttons.append([InlineKeyboardButton(text="🎭 Состояния", callback_data="admin:states")])
    if permissions.get('can_manage_awards') or permissions.get('can_grant_awards'):
        buttons.append([InlineKeyboardButton(text="🏅 Награды", callback_data="admin:awards")])
    if permissions.get('can_manage_locations'):
        buttons.append([InlineKeyboardButton(text="📍 Локации", callback_data="admin:locations")])
        buttons.append([InlineKeyboardButton(text="🏰 Подземелья", callback_data="admin:dungeons")])
        buttons.append([InlineKeyboardButton(text="🐟 Рыбалка", callback_data="admin:fishing")])
    if permissions.get('can_view_logs'):
        buttons.append([InlineKeyboardButton(text="🧾 Логи действий", callback_data="admin:logs")])
        buttons.append([InlineKeyboardButton(text="📒 Лог игрока", callback_data="admin:player_log")])
        buttons.append([InlineKeyboardButton(text="📊 Активность игроков", callback_data="act:all")])
    if permissions.get('can_manage_users'):
        buttons.append([InlineKeyboardButton(text="🗑 Удалить фото пилота", callback_data="admin:del_photo")])
        buttons.append([InlineKeyboardButton(text="📡 Установить позывной", callback_data="admin:callsign")])
    if permissions.get('can_manage_wing'):
        buttons.append([InlineKeyboardButton(text="🪽 Авиакрылья", callback_data="admin:wing")])
    if permissions.get('can_manage_storage'):
        buttons.append([InlineKeyboardButton(text="📦 Хранилище", callback_data="admin:storage")])
    buttons.append([InlineKeyboardButton(text="🔙 В меню", callback_data="back:main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def profile_keyboard(notify_enabled: bool = True, profile_public: bool = True, can_toggle_visibility: bool = False):
    rows = [
        [InlineKeyboardButton(text="Изменить фото", callback_data="profile:set_photo")],
        [InlineKeyboardButton(text="Выбрать статус", callback_data="profile:choose_status")],
        [InlineKeyboardButton(text="📖 О себе", callback_data="profile:edit_about")],
        [InlineKeyboardButton(text="🎖️ Награды", callback_data="profile:awards")],
        [InlineKeyboardButton(text="Карточка пилота", callback_data="profile:pilot_card")],
        [InlineKeyboardButton(
            text="🔔 Оповещения: вкл" if notify_enabled else "🔕 Оповещения: выкл",
            callback_data="profile:notify_toggle"
        )],
    ]
    if can_toggle_visibility:
        rows.append([InlineKeyboardButton(
            text="👁 Профиль виден: всем" if profile_public else "🔒 Профиль скрыт",
            callback_data="profile:public_toggle"
        )])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def shop_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Каталог", callback_data="shop:catalog")],
        [InlineKeyboardButton(text="Мои покупки", callback_data="shop:my_purchases")],
        [InlineKeyboardButton(text="Продать товар", callback_data="shop:sell")],
    ])


def shop_catalog_keyboard(available: dict):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    rows = []
    for key, count in available.items():
        from config import ITEM_CATEGORIES
        label = ITEM_CATEGORIES.get(key, key)
        rows.append([InlineKeyboardButton(text=f"{label} ({count})", callback_data=f"shopcat:{key}")])
    rows.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def item_card_keyboard(item_id: int, price_nord: int, can_buy_nord: bool = True):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    buttons = []
    if price_nord > 0 and can_buy_nord:
        buttons.append([InlineKeyboardButton(text=f"💰 Купить за {price_nord}", callback_data=f"buy_nord:{item_id}")])
    buttons.append([InlineKeyboardButton(text="🔙 В каталог", callback_data="shop:catalog")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def shop_admin_keyboard():
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Добавить товар", callback_data="shop_admin:add")],
        [InlineKeyboardButton(text="Удалить товар", callback_data="shop_admin:delete")],
        [InlineKeyboardButton(text="Изменить товар", callback_data="shop_admin:edit")],
        [InlineKeyboardButton(text="🔐 Код спец-отдела", callback_data="shop_admin:special_code")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin:menu")],
    ])


def bank_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Мой баланс", callback_data="bank:balance")],
        [InlineKeyboardButton(text="Перевести", callback_data="bank:transfer")],
        [InlineKeyboardButton(text="🏛️ В казну", callback_data="bank:treasury")],
        [InlineKeyboardButton(text="История транзакций", callback_data="bank:history")],
        [InlineKeyboardButton(text="🔙 В город", callback_data="city:menu")],
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


def city_keyboard(is_pilot: bool = True, locations: list = None, can_send_orders: bool = False):
    buttons = []
    for loc in (locations or []):
        buttons.append([InlineKeyboardButton(
            text=f"📍 {loc['name']}",
            callback_data=f"location:preview:{loc['key']}"
        )])
    buttons.append([InlineKeyboardButton(text="🧱 Стена изречений", callback_data="wall:view")])
    if can_send_orders:
        buttons.append([InlineKeyboardButton(text="🎖️ Штаб ВВС", callback_data="hq:menu")])
    if is_pilot:
        buttons.append([InlineKeyboardButton(text="📜 Контракты от Штаба ВС", callback_data="contracts:list")])
        buttons.append([InlineKeyboardButton(text="🏠 Жильё", callback_data="housing:menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


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


def wall_keyboard(page: int = 0, total_posts: int = 0, post_ids: list = None,
                  is_admin: bool = False, can_manage: bool = False):
    """Клавиатура «Стены изречений»: пагинация, «Оставить изречение», вход в город.

    Для админов под каждым постом — кнопка удаления (с возвратом автору).
    """
    from config import WALL_PAGE_SIZE
    total_pages = max(1, (total_posts + WALL_PAGE_SIZE - 1) // WALL_PAGE_SIZE)
    page = max(0, min(page, total_pages - 1))

    buttons = []
    for pid in (post_ids or []):
        if is_admin or can_manage:
            buttons.append([InlineKeyboardButton(
                text=f"🗑 Удалить #{pid}",
                callback_data=f"wall:delete:{pid}"
            )])
    if total_pages > 1:
        nav = []
        if page > 0:
            nav.append(InlineKeyboardButton(text="◀️", callback_data=f"wall:page:{page-1}"))
        nav.append(InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="noop"))
        if page < total_pages - 1:
            nav.append(InlineKeyboardButton(text="▶️", callback_data=f"wall:page:{page+1}"))
        if nav:
            buttons.append(nav)
    buttons.append([InlineKeyboardButton(text="✍️ Оставить изречение", callback_data="wall:write")])
    buttons.append([InlineKeyboardButton(text="🏠 В меню города", callback_data="city:menu")])
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
