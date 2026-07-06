"""
Обработчик команды /shop
"""

import logging
import sys
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from database.repository import ShopRepository, PilotRepository

logger = logging.getLogger(__name__)

# Словарь с названиями категорий на русском
CATEGORY_NAMES = {
    'weapon': '⚔️ Оружие',
    'consumable': '🩹 Расходники',
    'building': '🏠 Недвижимость',
    'equipment': '🎒 Снаряжение'
}

# Обратные названия для callback
CATEGORY_CALLBACK = {
    'weapon': 'weapon',
    'consumable': 'consumable',
    'building': 'building',
    'equipment': 'equipment'
}


async def shop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /shop - показать категории"""

    # Получаем все предметы
    items = ShopRepository.get_all_items()

    if not items:
        await update.message.reply_text("❌ Магазин временно пуст.")
        return

    # Группируем по категориям
    categories = {}
    for item in items:
        item_type = item[5]  # item_type
        if item_type not in categories:
            categories[item_type] = []
        categories[item_type].append(item)

    # Создаем клавиатуру с категориями
    keyboard = []
    for cat_key, cat_items in categories.items():
        cat_name = CATEGORY_NAMES.get(cat_key, cat_key)
        keyboard.append([InlineKeyboardButton(f"{cat_name} ({len(cat_items)})", callback_data=f"cat_{cat_key}")])

    # Добавляем кнопку "Мои покупки"
    keyboard.append([InlineKeyboardButton("📦 Мои покупки", callback_data="my_purchases")])
    keyboard.append([InlineKeyboardButton("🔙 Назад в меню", callback_data="back_to_menu")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    shop_text = (
        "🛒 **МАГАЗИН**\n"
        "═══════════════\n\n"
        "Добро пожаловать в магазин!\n"
        "Выберите категорию товаров:\n\n"
        "💰 Оплата:\n"
        "• ✈️ Нордмарки - основная валюта\n"
        "• ⚡️ Очки действия (AP) - ограничены 150"
    )

    await update.message.reply_text(shop_text, reply_markup=reply_markup, parse_mode='Markdown')


async def show_category(update: Update, context: ContextTypes.DEFAULT_TYPE, category: str):
    """Показать предметы в категории"""

    query = update.callback_query
    await query.answer()

    items = ShopRepository.get_items_by_category(category)

    if not items:
        await query.edit_message_text(f"❌ В категории {CATEGORY_NAMES.get(category, category)} пока нет товаров.")
        return

    # Создаем кнопки для каждого предмета
    keyboard = []
    for item in items:
        item_id = item[0]
        item_name = item[1]
        price_nord = item[3]
        price_ap = item[4]

        # Отображаем цены
        price_text = f"💰 {price_nord} ✈️"
        if price_ap > 0:
            price_text += f" | ⚡️ {price_ap}"

        keyboard.append([InlineKeyboardButton(f"{item_name} - {price_text}", callback_data=f"item_{item_id}")])

    keyboard.append([InlineKeyboardButton("🔙 Назад к категориям", callback_data="back_to_shop")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        f"📦 **{CATEGORY_NAMES.get(category, category)}**\n"
        f"═══════════════\n\n"
        f"Выберите предмет для покупки:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


async def show_item(update: Update, context: ContextTypes.DEFAULT_TYPE, item_id: int):
    """Показать информацию о предмете и предложить купить"""

    query = update.callback_query
    await query.answer()

    item = ShopRepository.get_item_by_id(item_id)

    if not item:
        await query.edit_message_text("❌ Предмет не найден")
        return

    item_id, name, description, price_nord, price_ap, item_type, rarity, image_path, effect_data = item

    # Описание
    desc_text = description if description else "Нет описания"

    # Редкость
    rarity_emojis = {
        'common': '⚪',
        'uncommon': '🟢',
        'rare': '🔵',
        'epic': '🟣',
        'legendary': '🟠'
    }
    rarity_emoji = rarity_emojis.get(rarity, '⚪')

    # Категория
    category_name = CATEGORY_NAMES.get(item_type, item_type)

    item_text = (
        f"**{name}**\n"
        f"═══════════════\n"
        f"{rarity_emoji} Редкость: {rarity}\n"
        f"📦 Тип: {category_name}\n\n"
        f"📝 **Описание:**\n{desc_text}\n\n"
        f"💰 **Цена:**\n"
        f"• ✈️ Нордмарки: {price_nord}\n"
    )

    if price_ap > 0:
        item_text += f"• ⚡️ Очки действия: {price_ap}\n"

    # Создаем кнопки покупки
    keyboard = []

    if price_nord > 0:
        keyboard.append([InlineKeyboardButton(f"Купить за {price_nord} ✈️", callback_data=f"buy_nord_{item_id}")])

    if price_ap > 0:
        keyboard.append([InlineKeyboardButton(f"Купить за {price_ap} ⚡️", callback_data=f"buy_ap_{item_id}")])

    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data=f"back_to_cat_{item_type}")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(item_text, reply_markup=reply_markup, parse_mode='Markdown')


async def buy_item(update: Update, context: ContextTypes.DEFAULT_TYPE, item_id: int, payment_type: str):
    """Обработка покупки предмета"""

    query = update.callback_query
    await query.answer()

    user = update.effective_user

    # Покупаем предмет
    success, message, item_name = ShopRepository.buy_item(user.id, item_id, payment_type)

    if success:
        # Обновляем сообщение с подтверждением
        keyboard = [[InlineKeyboardButton("🔙 Продолжить покупки", callback_data="back_to_shop")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"{message}\n\n"
            f"Предмет добавлен в ваш инвентарь!\n"
            f"Используйте /inventory чтобы посмотреть все вещи.",
            reply_markup=reply_markup
        )
    else:
        # Ошибка при покупке
        keyboard = [[InlineKeyboardButton("🔙 Назад в магазин", callback_data="back_to_shop")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"❌ {message}",
            reply_markup=reply_markup
        )


async def my_purchases(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать мои покупки (инвентарь)"""

    query = update.callback_query
    await query.answer()

    from database.repository import InventoryRepository

    user = update.effective_user
    inventory = InventoryRepository.get_pilot_inventory(user.id)

    if not inventory:
        # Исправлено: используем query.edit_message_text вместо query.message.reply_text
        keyboard = [[InlineKeyboardButton("🔙 В магазин", callback_data="back_to_shop")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            "📦 **Мои покупки**\n\n"
            "У вас пока нет предметов.\n"
            "Посетите магазин чтобы купить что-нибудь!",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return

    text = "📦 **МОЙ ИНВЕНТАРЬ**\n═══════════════\n\n"

    for item in inventory:
        item_id, name, description, item_type, rarity, quantity = item[:6]
        rarity_emojis = {'common': '⚪', 'uncommon': '🟢', 'rare': '🔵', 'epic': '🟣', 'legendary': '🟠'}
        rarity_emoji = rarity_emojis.get(rarity, '⚪')

        text += f"{rarity_emoji} **{name}** x{quantity}\n"
        if description:
            text += f"   _{description[:50]}_\n"
        text += "\n"

    keyboard = [[InlineKeyboardButton("🔙 В магазин", callback_data="back_to_shop")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')