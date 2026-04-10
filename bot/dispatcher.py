"""
Модуль диспетчера бота - упрощенная версия для тестирования
"""

import logging
import sys
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ConversationHandler

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class BotDispatcher:
    def __init__(self):
        self.application = None
        self.bot_username = None

    async def post_init(self, application: Application):
        self.bot_username = application.bot.username
        Config.BOT_USERNAME = self.bot_username

        commands = [
            ("start", "🚀 Запустить бота"),
            ("profile", "👤 Мой профиль"),
            ("help", "❓ Помощь"),
        ]

        await application.bot.set_my_commands(commands)
        logger.info(f"✅ Бот @{self.bot_username} успешно запущен!")

    def setup_handlers(self):
        from bot.handlers import start, profile

        # Команды
        self.application.add_handler(CommandHandler("start", start.start_command))
        self.application.add_handler(CommandHandler("help", start.help_command))
        self.application.add_handler(CommandHandler("profile", profile.profile_command))

        # Обработчик текстовых кнопок
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_button_press))

        # Обработчик неизвестных команд
        self.application.add_handler(MessageHandler(filters.COMMAND, self.unknown_command))
        self.application.add_error_handler(self.error_handler)

        logger.info("✅ Все обработчики загружены")

    async def handle_button_press(self, update: Update, context):
        """Обработка нажатий на кнопки клавиатуры"""
        from bot.handlers import start, profile

        text = update.message.text

        if text == "👤 Профиль":
            await profile.profile_command(update, context)
        elif text == "❓ Помощь":
            await start.help_command(update, context)
        else:
            await update.message.reply_text("❌ Неизвестная команда. Используйте /help")

    async def unknown_command(self, update: Update, context):
        await update.message.reply_text(
            "❌ Неизвестная команда.\nИспользуйте /help для просмотра доступных команд."
        )

    async def error_handler(self, update: Update, context):
        logger.error(f"❌ Ошибка: {context.error}")

        if update and update.effective_message:
            await update.effective_message.reply_text(
                f"😔 Ошибка: {str(context.error)[:200]}"
            )

    def run(self):
        if not Config.BOT_TOKEN:
            logger.error("❌ BOT_TOKEN не найден!")
            return

        logger.info("🤖 Запуск бота...")
        logger.info(f"📁 База данных: {Config.DATABASE_PATH}")

        try:
            self.application = Application.builder() \
                .token(Config.BOT_TOKEN) \
                .post_init(self.post_init) \
                .build()

            self.setup_handlers()

            logger.info("🔄 Бот начинает polling...")
            self.application.run_polling(allowed_updates=Update.ALL_TYPES)

        except KeyboardInterrupt:
            logger.info("👋 Бот остановлен пользователем")
        except Exception as e:
            logger.error(f"❌ Критическая ошибка: {e}")
            raise


# Создаем экземпляр
dispatcher = BotDispatcher()