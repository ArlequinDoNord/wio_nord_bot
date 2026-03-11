"""
Обработчики команд /start и /help
"""

import logging
import sys
import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes

# Добавляем путь к корневой папке
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from database.repository import PilotRepository

logger = logging.getLogger(__name__)

# Клавиатура главного меню
MAIN_KEYBOARD = [
    ["👤 Профиль", "🛒 Магазин"],
    ["🎒 Инвентарь", "📝 Отчет"],
    ["❓ Помощь"]
]
main_menu_markup = ReplyKeyboardMarkup(MAIN_KEYBOARD, resize_keyboard=True)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""

    user = update.effective_user

    logger.info(f"Пользователь @{user.username} (ID: {user.id}) запустил бота")

    # Получаем или создаем пилота
    pilot = PilotRepository.get_or_create_pilot(
        telegram_id=user.id,
        username=user.username,
        full_name=user.full_name
    )

    # Приветственное сообщение
    welcome_text = (
        f"🛩 **Добро пожаловать С.О.Д.Н., {user.full_name}!**\n\n"
        f"Вы - пилот ВВС Нордхайма.\n\n"
        f"📋 **Основные команды:**\n"
        f"• /profile - Ваш профиль\n"
        f"• /shop - Магазин снаряжения\n"
        f"• /inventory - Ваш инвентарь\n"
        f"• /new_report - Сдать боевой отчет\n"
        f"• /help - Помощь\n\n"
        f"💰 **Игровая валюта:**\n"
        f"• Нордмарки - основная валюта (нет лимита)\n"
        f"• Очки действия (AP) - лимит 150\n\n"
        f"Удачи в небе! 🎮"
    )

    await update.message.reply_text(
        welcome_text,
        reply_markup=main_menu_markup,
        parse_mode='Markdown'
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""

    help_text = (
        "🛩 **Warplane Nord Bot - Помощь**\n\n"

        "**📋 Основные команды:**\n"
        "/start - Начать работу с ботом\n"
        "/profile - Ваш профиль и статистика\n"
        "/shop - Магазин снаряжения\n"
        "/inventory - Ваш инвентарь\n"
        "/new_report - Сдать боевой отчет\n"
        "/help - Это сообщение\n\n"

        "**💰 Игровая валюта:**\n"
        "• **Нордмарки** - основная валюта, нет лимита\n"
        "• **Очки действия (AP)** - лимит 150, восстанавливаются со временем\n\n"

        "**📊 Ранговая система:**\n"
        "1. Рядовой (0 опыта)\n"
        "2. Капрал (100 опыта)\n"
        "3. Сержант (300 опыта)\n"
        "4. Лейтенант (600 опыта)\n"
        "5. Капитан (1000 опыта)\n\n"

        "**📝 Система отчетов:**\n"
        "• Сдавайте отчеты после боевых вылетов\n"
        "• Прикрепляйте скриншоты из игры\n"
        "• Получайте награды в валюте\n\n"

        "**🛒 Магазин:**\n"
        "• Покупайте снаряжение и имущество\n"
        "• Улучшайте своего пилота\n"
        "• Инвестируйте в недвижимость\n\n"

        "❓ **Если возникли вопросы:**\n"
        "Свяжитесь с администраторами через @BotFather"
    )

    await update.message.reply_text(
        help_text,
        parse_mode='Markdown'
    )