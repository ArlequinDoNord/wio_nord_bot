"""
Обработчик команды /profile
"""

import logging
import sys
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from database.repository import PilotRepository

logger = logging.getLogger(__name__)


async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /profile"""

    user = update.effective_user

    # Получаем профиль пилота
    profile = PilotRepository.get_pilot_profile(user.id)

    if not profile:
        await update.message.reply_text(
            "❌ Профиль не найден. Используйте /start для регистрации."
        )
        return

    full_name, rank, level, experience, nord_marks, action_points, reg_date, last_active = profile

    # Рассчитываем прогресс до следующего уровня
    next_level_exp = level * 100  # Простая формула: 100, 200, 300...
    exp_progress = min(100, int((experience / next_level_exp) * 100))
    progress_bar = "█" * (exp_progress // 10) + "░" * (10 - (exp_progress // 10))

    # Формируем сообщение профиля
    profile_text = (
        f"👤 **Личная карточка пилота**\n"
        f"═══════════════════════\n\n"
        f"**Имя:** {full_name}\n"
        f"**Ранг:** {rank}\n"
        f"**Уровень:** {level}\n\n"

        f"📊 **Прогресс:**\n"
        f"Опыт: {experience}/{next_level_exp}\n"
        f"`[{progress_bar}]` {exp_progress}%\n\n"

        f"💰 **Финансы:**\n"
        f"• Нордмарки: **{nord_marks}** ✈️\n"
        f"• Очки действия: **{action_points}/150** ⚡️\n\n"

        f"📅 **Дата регистрации:** {reg_date[:10]}\n"
        f"🕐 **Последний визит:** {last_active[:16]}"
    )

    # Создаем инлайн-кнопки
    keyboard = [
        [InlineKeyboardButton("📦 Инвентарь", callback_data="inventory_view")],
        [InlineKeyboardButton("🏆 Достижения", callback_data="achievements")],
        [InlineKeyboardButton("📊 Статистика", callback_data="statistics")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        profile_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )