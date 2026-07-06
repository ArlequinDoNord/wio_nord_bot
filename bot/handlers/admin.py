"""
Админ-панель для управления ботом
"""

import sys
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from database.repository import ShopRepository, PilotRepository
from utils.permissions import is_admin, has_permission, get_user_role, add_role, remove_role
from config import Config

# Состояния для ConversationHandler
WAITING_ITEM_NAME = 1
WAITING_ITEM_DESC = 2
WAITING_ITEM_PRICE_NORD = 3
WAITING_ITEM_PRICE_AP = 4
WAITING_ITEM_TYPE = 5
WAITING_ITEM_RARITY = 6
WAITING_ITEM_PHOTO = 7
WAITING_TARGET_USER = 8
WAITING_CURRENCY_AMOUNT = 9


async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Главное меню администрирования"""
    user_id = update.effective_user.id

    if not is_admin(user_id):
        await update.message.reply_text("❌ У вас нет доступа к админ-панели")
        return

    roles = get_user_role(user_id)
    role_text = ", ".join(roles)

    keyboard = []

    # Кнопки в зависимости от прав
    if has_permission(user_id, 'can_manage_shop'):
        keyboard.append([InlineKeyboardButton("🛒 Управление товарами", callback_data="admin_shop")])

    if has_permission(user_id, 'can_manage_finance'):
        keyboard.append([InlineKeyboardButton("💰 Управление финансами", callback_data="admin_finance")])

    if has_permission(user_id, 'can_manage_admins'):
        keyboard.append([InlineKeyboardButton("👑 Управление админами", callback_data="admin_admins")])

    if has_permission(user_id, 'can_view_logs'):
        keyboard.append([InlineKeyboardButton("📋 Логи действий", callback_data="admin_logs")])

    keyboard.append([InlineKeyboardButton("🔙 В главное меню", callback_data="back_to_menu")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    admin_text = (
        f"👑 **Админ-панель**\n"
        f"═══════════════\n\n"
        f"Ваши роли: {role_text}\n\n"
        f"Выберите действие:"
    )

    await update.message.reply_text(admin_text, reply_markup=reply_markup)


async def admin_shop_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Меню управления магазином"""
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("➕ Добавить товар", callback_data="add_item")],
        [InlineKeyboardButton("📋 Список товаров", callback_data="list_items")],
        [InlineKeyboardButton("✏️ Редактировать товар", callback_data="edit_item")],
        [InlineKeyboardButton("🗑 Удалить товар", callback_data="delete_item")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_to_admin")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "🛒 **Управление магазином**\n\n"
        "Выберите действие:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


async def add_item_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало добавления товара"""
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "➕ **Добавление нового товара**\n\n"
        "Введите название товара:"
    )
    return WAITING_ITEM_NAME


async def add_item_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение названия товара"""
    context.user_data['new_item'] = {'name': update.message.text}
    await update.message.reply_text("📝 Введите описание товара:")
    return WAITING_ITEM_DESC


async def add_item_desc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение описания товара"""
    context.user_data['new_item']['description'] = update.message.text
    await update.message.reply_text("💰 Введите цену в Нордмарках (число):")
    return WAITING_ITEM_PRICE_NORD


async def add_item_price_nord(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение цены в Нордмарках"""
    try:
        price = int(update.message.text)
        context.user_data['new_item']['price_nord'] = price
        await update.message.reply_text("⚡️ Введите цену в Очках действия (AP, число, 0 если бесплатно):")
        return WAITING_ITEM_PRICE_AP
    except ValueError:
        await update.message.reply_text("❌ Введите число!")
        return WAITING_ITEM_PRICE_NORD


async def add_item_price_ap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение цены в AP"""
    try:
        price = int(update.message.text)
        context.user_data['new_item']['price_ap'] = price

        keyboard = [
            [InlineKeyboardButton("⚔️ Оружие", callback_data="type_weapon")],
            [InlineKeyboardButton("🩹 Расходник", callback_data="type_consumable")],
            [InlineKeyboardButton("🏠 Недвижимость", callback_data="type_building")],
            [InlineKeyboardButton("🎒 Снаряжение", callback_data="type_equipment")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "📦 Выберите тип товара:",
            reply_markup=reply_markup
        )
        return WAITING_ITEM_TYPE
    except ValueError:
        await update.message.reply_text("❌ Введите число!")
        return WAITING_ITEM_PRICE_AP


async def add_item_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение типа товара"""
    query = update.callback_query
    await query.answer()

    item_type = query.data.replace("type_", "")
    context.user_data['new_item']['item_type'] = item_type

    keyboard = [
        [InlineKeyboardButton("⚪ Обычный", callback_data="rarity_common")],
        [InlineKeyboardButton("🟢 Необычный", callback_data="rarity_uncommon")],
        [InlineKeyboardButton("🔵 Редкий", callback_data="rarity_rare")],
        [InlineKeyboardButton("🟣 Эпический", callback_data="rarity_epic")],
        [InlineKeyboardButton("🟠 Легендарный", callback_data="rarity_legendary")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "✨ Выберите редкость товара:",
        reply_markup=reply_markup
    )
    return WAITING_ITEM_RARITY


async def add_item_rarity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение редкости товара"""
    query = update.callback_query
    await query.answer()

    rarity = query.data.replace("rarity_", "")
    context.user_data['new_item']['rarity'] = rarity

    await query.edit_message_text(
        "🖼 Теперь отправьте фото товара\n"
        "(или отправьте /skip чтобы пропустить)"
    )
    return WAITING_ITEM_PHOTO


async def add_item_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение фото товара"""
    if update.message.photo:
        photo_file_id = update.message.photo[-1].file_id
        context.user_data['new_item']['image_path'] = photo_file_id
    else:
        context.user_data['new_item']['image_path'] = None

    # Сохраняем товар в БД
    item = context.user_data['new_item']

    conn = sqlite3.connect(Config.DATABASE_PATH)
    cur = conn.cursor()

    cur.execute('''
    INSERT INTO items (name, description, price_nord, price_ap, item_type, rarity, image_path, effect_data)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (item['name'], item['description'], item['price_nord'], item['price_ap'],
          item['item_type'], item['rarity'], item.get('image_path'), '{}'))

    conn.commit()
    item_id = cur.lastrowid
    conn.close()

    # Логируем
    from utils.permissions import log_action
    log_action(update.effective_user.id, 'add_item', item_id, f'name={item["name"]}')

    await update.message.reply_text(
        f"✅ Товар **{item['name']}** успешно добавлен!\n"
        f"ID товара: {item_id}",
        parse_mode='Markdown'
    )

    context.user_data.pop('new_item', None)
    return ConversationHandler.END


async def skip_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Пропуск добавления фото"""
    context.user_data['new_item']['image_path'] = None

    # Сохраняем товар
    item = context.user_data['new_item']

    conn = sqlite3.connect(Config.DATABASE_PATH)
    cur = conn.cursor()

    cur.execute('''
    INSERT INTO items (name, description, price_nord, price_ap, item_type, rarity, image_path, effect_data)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (item['name'], item['description'], item['price_nord'], item['price_ap'],
          item['item_type'], item['rarity'], None, '{}'))

    conn.commit()
    item_id = cur.lastrowid
    conn.close()

    from utils.permissions import log_action
    log_action(update.effective_user.id, 'add_item', item_id, f'name={item["name"]}')

    await update.message.reply_text(
        f"✅ Товар **{item['name']}** успешно добавлен без фото!\n"
        f"ID товара: {item_id}",
        parse_mode='Markdown'
    )

    context.user_data.pop('new_item', None)
    return ConversationHandler.END


async def finance_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Меню управления финансами"""
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("➕ Начислить валюту", callback_data="add_currency")],
        [InlineKeyboardButton("➖ Списать валюту", callback_data="remove_currency")],
        [InlineKeyboardButton("📊 Баланс игрока", callback_data="check_balance")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_to_admin")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "💰 **Управление финансами**\n\n"
        "Выберите действие:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


async def add_currency_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало начисления валюты"""
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "💰 **Начисление валюты**\n\n"
        "Введите Telegram ID пользователя:"
    )
    return WAITING_TARGET_USER


async def get_target_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение ID пользователя"""
    try:
        target_id = int(update.message.text)
        context.user_data['target_id'] = target_id

        await update.message.reply_text(
            "Введите сумму Нордмарок для начисления\n"
            "(можно отрицательное для списания):"
        )
        return WAITING_CURRENCY_AMOUNT
    except ValueError:
        await update.message.reply_text("❌ Введите корректный Telegram ID (число)")
        return WAITING_TARGET_USER


async def process_currency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начисление/списание валюты"""
    try:
        amount = int(update.message.text)
        target_id = context.user_data['target_id']
        admin_id = update.effective_user.id

        new_nord, new_ap = PilotRepository.update_pilot_currency(target_id, amount, 0)

        if new_nord is None:
            await update.message.reply_text("❌ Пользователь не найден")
            return ConversationHandler.END

        from utils.permissions import log_action
        log_action(admin_id, 'add_currency', target_id, f'amount={amount}')

        await update.message.reply_text(
            f"✅ Операция выполнена!\n"
            f"Пользователь ID: {target_id}\n"
            f"Новый баланс Нордмарок: {new_nord}"
        )

        # Уведомляем пользователя
        try:
            await context.bot.send_message(
                target_id,
                f"💰 Администратор {'начислил' if amount > 0 else 'списал'} {abs(amount)} Нордмарок.\n"
                f"Ваш баланс: {new_nord} ✈️"
            )
        except:
            pass

        context.user_data.pop('target_id', None)
        return ConversationHandler.END

    except ValueError:
        await update.message.reply_text("❌ Введите число")
        return WAITING_CURRENCY_AMOUNT


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена операции"""
    context.user_data.clear()
    await update.message.reply_text("❌ Операция отменена")
    return ConversationHandler.END