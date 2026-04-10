"""
Обработчик для установки фото пилота
"""

import logging
import sys
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from database.repository import PilotRepository

logger = logging.getLogger(__name__)

# Состояния для диалога
WAITING_PHOTO = 1


async def setphoto_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для установки фото пилота"""

    keyboard = [
        [InlineKeyboardButton("❌ Отмена", callback_data="cancel_photo")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "📸 **Установка фото пилота**\n\n"
        "Отправьте мне фото, которое станет изображением вашего пилота.\n"
        "Фото будет видно в вашей карточке профиля.\n\n"
        "✨ **Советы:**\n"
        "• Используйте портретное фото\n"
        "• Лучше всего подойдут фото в анфас\n"
        "• Можно использовать фото вашего самолета\n\n"
        "_Просто отправьте фото как обычное сообщение_",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

    return WAITING_PHOTO


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик получения фото"""

    user = update.effective_user

    # Получаем фото максимального размера
    photo = update.message.photo[-1]
    file_id = photo.file_id

    # Сохраняем в базу данных
    PilotRepository.save_pilot_photo(user.id, file_id)

    # Создаем клавиатуру для действий
    keyboard = [
        [InlineKeyboardButton("👤 Посмотреть профиль", callback_data="view_profile")],
        [InlineKeyboardButton("🔄 Заменить фото", callback_data="change_photo")],
        [InlineKeyboardButton("❌ Удалить фото", callback_data="delete_photo")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "✅ **Фото успешно установлено!**\n\n"
        "Теперь оно будет отображаться в вашей карточке пилота.\n"
        "Используйте /profile чтобы увидеть результат.",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

    return ConversationHandler.END


async def cancel_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена установки фото"""

    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "❌ Установка фото отменена.\n"
        "Вы можете установить фото позже командой /setphoto"
    )

    return ConversationHandler.END


async def photo_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик инлайн-кнопок для фото"""

    query = update.callback_query
    await query.answer()

    user = query.from_user

    if query.data == "view_profile":
        # Перенаправляем на профиль
        await query.message.delete()
        from bot.handlers.profile import profile_command
        await profile_command(update, context)

    elif query.data == "change_photo":
        await query.edit_message_text(
            "📸 Отправьте новое фото для вашего пилота:"
        )
        return WAITING_PHOTO

    elif query.data == "delete_photo":
        # Удаляем фото
        PilotRepository.delete_pilot_photo(user.id)

        keyboard = [
            [InlineKeyboardButton("👤 Посмотреть профиль", callback_data="view_profile")],
            [InlineKeyboardButton("📸 Установить новое", callback_data="change_photo")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            "✅ Фото удалено.\n"
            "Теперь в вашем профиле будет отображаться только текст.",
            reply_markup=reply_markup
        )