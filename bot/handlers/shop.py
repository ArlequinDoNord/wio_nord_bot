"""
Обработчик команды /shop
"""

import logging
import sys
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from database.repository import ShopRepository

logger = logging.getLogger(__name__)


async def shop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /shop"""

    # Получаем все предметы из магазина
    items = ShopRepository.get_all_items()

    if not items:
        await update.message.reply_text("❌ Магазин временно пуст.")
        return

    # Формируем сообщение с категориями
    shop_text = "🛒 **Магазин снаряжения**\n"
    shop_text += "══════════════════\n\n"
    shop_text += "Выберите категорию:\n"

    # Категории товаров
    categories = {
        "⚔️ Оружие": [i for i in items if i[5] == 'weapon'],  # item_type
        "🩹 Расходники": [i for i in items if i[5] == 'consumable'],
        "🏠 Недвижимость": [i for i in items if i[5] == 'building'],
        "🎁 Прочее": [i for i in items if i[5] not in ['weapon', 'consumable', 'building']]
    }

    # Создаем кнопки категорий
    keyboard = []
    for category_name, category_items in categories.items():
        if category_items:  # Показываем только непустые категории
            keyboard.append([InlineKeyboardButton(
                f"{category_name} ({len(category_items)})",
                callback_data=f"shop_category_{category_name}"
            )])

    # Добавляем кнопку "Мои покупки"
    keyboard.append([InlineKeyboardButton("📦 Мои покупки", callback_data="my_purchases")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        shop_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )