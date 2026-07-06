"""
Модуль диспетчера бота - упрощенная версия для тестирования
"""

import logging
import sys
import os

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ConversationHandler

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config
from bot.handlers import admin

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
            ("shop", "🛒 Магазин"),
            ("help", "❓ Помощь"),
        ]

        await application.bot.set_my_commands(commands)
        logger.info(f"✅ Бот @{self.bot_username} успешно запущен!")
        logger.info(f"📋 Загружено {len(commands)} команд")

    def setup_handlers(self):
        from bot.handlers import start, profile, shop, admin
        from telegram.ext import ConversationHandler

        # Команды
        self.application.add_handler(CommandHandler("start", start.start_command))
        self.application.add_handler(CommandHandler("help", start.help_command))
        self.application.add_handler(CommandHandler("profile", profile.profile_command))
        self.application.add_handler(CommandHandler("shop", shop.shop_command))
        self.application.add_handler(CommandHandler("admin", admin.admin_command))

        # Обработчик текстовых кнопок
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_button_press))

        # Обработчики инлайн-кнопок для магазина
        self.application.add_handler(CallbackQueryHandler(self.shop_callback, pattern="^(cat_|item_|buy_|back_to_|my_purchases)"))

        # Админ-панель
        self.application.add_handler(CallbackQueryHandler(admin.admin_shop_menu, pattern="^admin_shop$"))
        self.application.add_handler(CallbackQueryHandler(admin.finance_menu, pattern="^admin_finance$"))
        self.application.add_handler(CallbackQueryHandler(admin.admin_command, pattern="^back_to_admin$"))

        # Обработчик неизвестных команд
        self.application.add_handler(MessageHandler(filters.COMMAND, self.unknown_command))
        self.application.add_error_handler(self.error_handler)

        logger.info("✅ Все обработчики загружены")

    async def shop_callback(self, update: Update, context):
        """Обработчик инлайн-кнопок магазина"""
        from bot.handlers import shop
        from database.repository import ShopRepository
        from bot.handlers.shop import CATEGORY_NAMES
        from bot.handlers.start import main_menu_markup, main_menu_markup_admin
        from utils.permissions import is_admin

        query = update.callback_query
        data = query.data
        await query.answer()

        try:
            if data.startswith("cat_"):
                category = data.replace("cat_", "")
                await shop.show_category(update, context, category)

            elif data.startswith("item_"):
               item_id = int(data.replace("item_", ""))
               await shop.show_item(update, context, item_id)

            elif data.startswith("buy_nord_"):
               item_id = int(data.replace("buy_nord_", ""))
               await shop.buy_item(update, context, item_id, 'nord')

            elif data.startswith("buy_ap_"):
               item_id = int(data.replace("buy_ap_", ""))
               await shop.buy_item(update, context, item_id, 'ap')

            elif data == "back_to_shop":
               items = ShopRepository.get_all_items()
               if not items:
                   await query.edit_message_text("❌ Магазин временно пуст.")
                   return

               categories = {}
               for item in items:
                   item_type = item[5]
                   if item_type not in categories:
                      categories[item_type] = []
                   categories[item_type].append(item)

               keyboard = []
               for cat_key, cat_items in categories.items():
                   cat_name = CATEGORY_NAMES.get(cat_key, cat_key)
                   keyboard.append([InlineKeyboardButton(f"{cat_name} ({len(cat_items)})", callback_data=f"cat_{cat_key}")])

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

                   await query.edit_message_text(shop_text, reply_markup=reply_markup, parse_mode='Markdown')

            elif data.startswith("back_to_cat_"):
               category = data.replace("back_to_cat_", "")
               await shop.show_category(update, context, category)

            elif data == "my_purchases":
               await shop.my_purchases(update, context)

            elif data == "back_to_menu":
               user_id = update.effective_user.id
               if is_admin(user_id):
                  reply_markup = main_menu_markup_admin
               else:
                  reply_markup = main_menu_markup

               await query.message.delete()
               await context.bot.send_message(
                  chat_id=update.effective_chat.id,
                  text="🏠 Главное меню\nИспользуйте кнопки ниже для навигации:",
                  reply_markup=reply_markup
               )

        except Exception as e:
            logger.error(f"Ошибка в shop_callback: {e}")
            await query.edit_message_text(f"❌ Ошибка: {str(e)[:100]}")

    async def handle_button_press(self, update: Update, context):
        """Обработка нажатий на кнопки клавиатуры"""
        from bot.handlers import start, profile, shop, admin

        text = update.message.text

        if text == "👤 Профиль":
            await profile.profile_command(update, context)
        elif text == "🛒 Магазин":
            await shop.shop_command(update, context)
        elif text == "👑 Админ-панель":
            await admin.admin_command(update, context)
        elif text == "❓ Помощь":
            await start.help_command(update, context)
        else:
            await update.message.reply_text("❌ Неизвестная команда. Используйте /help")

    async def unknown_command(self, update: Update, context):
        await update.message.reply_text("❌ Неизвестная команда.\nИспользуйте /help для просмотра доступных команд.")

    async def error_handler(self, update: Update, context):
        logger.error(f"❌ Ошибка: {context.error}")
        if update and update.effective_message:
            await update.effective_message.reply_text(f"😔 Ошибка: {str(context.error)[:200]}")

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


dispatcher = BotDispatcher()