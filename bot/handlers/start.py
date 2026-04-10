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
    ["👤 Профиль", "❓ Помощь"]
]
main_menu_markup = ReplyKeyboardMarkup(MAIN_KEYBOARD, resize_keyboard=True)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start - без Markdown"""

    user = update.effective_user

    logger.info(f"Пользователь @{user.username} (ID: {user.id}) запустил бота")

    # Получаем или создаем пилота
    pilot = PilotRepository.get_or_create_pilot(
        telegram_id=user.id,
        username=user.username,
        full_name=user.full_name
    )

    # Приветственное сообщение БЕЗ Markdown разметки
    welcome_text = (
        "🛩 ДОБРО ПОЖАЛОВАТЬ В С.О.Д.Н.!\n\n"
        f"Пилот: {user.full_name}\n\n"
        "Вы - пилот ВВС Нордхайма.\n\n"
        "Основные команды:\n"
        "• /profile - Ваш профиль\n"
        "• /help - Помощь\n\n"
        "Игровая валюта:\n"
        "• Нордмарки - основная валюта (нет лимита)\n"
        "• Очки действия (AP) - лимит 150\n\n"
        "Удачи в небе!"
    )



    # Отправляем сообщение БЕЗ parse_mode
    await update.message.reply_text(
        welcome_text,
        reply_markup=main_menu_markup
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help - без Markdown"""

    help_text = (
        "🛩 WARPLANE Nord BOT - ПОМОЩЬ\n\n"
        "Основные команды:\n"
        "/start - Начать работу с ботом\n"
        "/profile - Ваш профиль и статистика\n"
        "/help - Это сообщение\n\n"
        "Игровая валюта:\n"
        "• Нордмарки - основная валюта, нет лимита\n"
        "• Очки действия (AP) - лимит 150\n\n"
        "Ранговая система:\n"
        "1. Рядовой (0 опыта)\n"
        "2. Капрал (100 опыта)\n"
        "3. Сержант (300 опыта)\n"
        "4. Лейтенант (600 опыта)\n"
        "5. Капитан (1000 опыта)\n\n"
        "❓ Если возникли вопросы:\n"
        "Свяжитесь с администраторами"
    )

    await update.message.reply_text(help_text)