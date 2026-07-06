"""
Обработчики команд /start и /help
"""

import logging
import sys
import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from database.repository import PilotRepository
from utils.permissions import is_admin

logger = logging.getLogger(__name__)

# Клавиатура главного меню (обычный игрок)
MAIN_KEYBOARD = [
    ["👤 Профиль", "🛒 Магазин"],
    ["❓ Помощь"]
]
main_menu_markup = ReplyKeyboardMarkup(MAIN_KEYBOARD, resize_keyboard=True)

# Клавиатура главного меню (администратор)
MAIN_KEYBOARD_ADMIN = [
    ["👤 Профиль", "🛒 Магазин"],
    ["👑 Админ-панель", "❓ Помощь"]
]
main_menu_markup_admin = ReplyKeyboardMarkup(MAIN_KEYBOARD_ADMIN, resize_keyboard=True)


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

    # === ВЫБОР КЛАВИАТУРЫ ===
    if is_admin(user.id):
        reply_markup = main_menu_markup_admin
        print(f"✅ Админ-клавиатура для ID {user.id}")
    else:
        reply_markup = main_menu_markup
        print(f"✅ Обычная клавиатура для ID {user.id}")

    # Приветственное сообщение
    welcome_text = (
        "🛩 ДОБРО ПОЖАЛОВАТЬ В Нордхайм!\n\n"
        f"Пилот: {user.full_name}\n\n"
        "Вы - пилот ВВС Норхайма.\n\n"
        "Основные команды:\n"
        "• /profile - Ваш профиль\n"
        "• /shop - Магазин\n"
        "• /help - Помощь\n\n"
        "Игровая валюта:\n"
        "• Нордмарки - основная валюта (нет лимита)\n"
        "• Очки действия (AP) - лимит 150\n\n"
        "Удачи в небе!"
    )

    # Отправляем сообщение с клавиатурой
    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""

    help_text = (
        "🛩 NordBOT - ПОМОЩЬ\n\n"
        "Основные команды:\n"
        "/start - Начать работу с ботом\n"
        "/profile - Ваш профиль и статистика\n"
        "/shop - Магазин\n"
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