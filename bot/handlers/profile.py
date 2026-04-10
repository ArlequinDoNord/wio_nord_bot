"""
Обработчик команды /profile - упрощенная версия
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from database.repository import PilotRepository


async def profile_command(update, context):
    """Упрощенная версия профиля"""

    user = update.effective_user

    try:
        profile = PilotRepository.get_pilot_profile(user.id)

        if not profile:
            await update.message.reply_text("❌ Профиль не найден. Используйте /start")
            return

        full_name, rank, level, experience, nord_marks, action_points, reg_date, last_active = profile[:8]

        # Получаем статистику
        stats = PilotRepository.get_pilot_stats(user.id)

        text = f"👤 ПРОФИЛЬ ПИЛОТА\n"
        text += f"{'=' * 25}\n\n"
        text += f"Имя: {full_name}\n"
        text += f"Ранг: {rank}\n"
        text += f"Уровень: {level}\n"
        text += f"Опыт: {experience}\n\n"
        text += f"💰 Нордмарки: {nord_marks}\n"
        text += f"⚡ Очки действия: {action_points}/150\n\n"
        text += f"📦 Предметов: {stats['total_items'] if stats else 0}\n"
        text += f"📝 Отчетов: {stats['total_reports'] if stats else 0}\n"
        text += f"✅ Принято: {stats['approved_reports'] if stats else 0}\n"

        await update.message.reply_text(text)

    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)[:200]}")