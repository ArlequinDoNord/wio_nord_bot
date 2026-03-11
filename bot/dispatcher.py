"""
Модуль диспетчера бота - отвечает за настройку и запуск бота
"""

import logging
import sys
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler

# Добавляем путь к корневой папке проекта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class BotDispatcher:
    """Класс для управления ботом"""

    def __init__(self):
        self.application = None
        self.bot_username = None

    async def post_init(self, application: Application):
        """Выполняется после инициализации бота"""
        self.bot_username = application.bot.username
        Config.BOT_USERNAME = self.bot_username

        # Устанавливаем команды бота
        commands = [
            ("start", "🚀 Запустить бота"),
            ("profile", "👤 Мой профиль"),
            ("shop", "🛒 Магазин"),
            ("inventory", "🎒 Инвентарь"),
            ("new_report", "📝 Сдать отчет"),
            ("help", "❓ Помощь"),
        ]

        await application.bot.set_my_commands(commands)
        logger.info(f"✅ Бот @{self.bot_username} успешно запущен!")
        logger.info(f"📋 Загружено {len(commands)} команд")

    def setup_handlers(self):
        """Настройка всех обработчиков команд"""

        # Импортируем обработчики
        from bot.handlers import start, profile, shop

        # Команды
        self.application.add_handler(CommandHandler("start", start.start_command))
        self.application.add_handler(CommandHandler("help", start.help_command))
        self.application.add_handler(CommandHandler("profile", profile.profile_command))
        self.application.add_handler(CommandHandler("shop", shop.shop_command))

        # Обработчик неизвестных команд
        self.application.add_handler(MessageHandler(filters.COMMAND, self.unknown_command))

        # Обработчик ошибок
        self.application.add_error_handler(self.error_handler)

        logger.info("✅ Все обработчики загружены")

    async def unknown_command(self, update: Update, context):
        """Обработка неизвестных команд"""
        await update.message.reply_text(
            "❌ Неизвестная команда.\n"
            "Используйте /help для просмотра доступных команд."
        )

    async def error_handler(self, update: Update, context):
        """Обработчик ошибок"""
        logger.error(f"❌ Ошибка: {context.error}")

        if update and update.effective_message:
            await update.effective_message.reply_text(
                "😔 Произошла внутренняя ошибка. Администраторы уже уведомлены."
            )

    def run(self):
        """Запуск бота"""
        # Проверяем наличие токена
        if not Config.BOT_TOKEN:
            logger.error("❌ BOT_TOKEN не найден! Проверьте файл .env")
            return

        logger.info("🤖 Запуск бота...")
        logger.info(f"📁 База данных: {Config.DATABASE_PATH}")

        try:
            # Создаем приложение
            self.application = Application.builder() \
                .token(Config.BOT_TOKEN) \
                .post_init(self.post_init) \
                .build()

            # Настраиваем обработчики
            self.setup_handlers()

            # Запускаем бота
            logger.info("🔄 Бот начинает polling...")
            self.application.run_polling(allowed_updates=Update.ALL_TYPES)

        except KeyboardInterrupt:
            logger.info("👋 Бот остановлен пользователем")
        except Exception as e:
            logger.error(f"❌ Критическая ошибка: {e}")
            raise


# СОЗДАЕМ ЭКЗЕМПЛЯР ДЛЯ ИМПОРТА - ЭТО ВАЖНО!
dispatcher = BotDispatcher()

# Также экспортируем класс на случай если нужен будет доступ
__all__ = ['BotDispatcher', 'dispatcher']