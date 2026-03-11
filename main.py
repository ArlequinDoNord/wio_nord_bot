print("===НордБОт для Wio===")
print("Project structure is ready!")
print("Virtual environment: OK")
print("Git repository: OK")
print("Next step: Create bot token with @BotFather")

"""
Главный файл для запуска Warplane RPG Telegram Bot
"""

import sys
import os
from bot.dispatcher import dispatcher
from database.models import init_db, test_connection


def main():
    """Основная функция запуска"""

    print("=" * 60)
    print("🛩 Warplane RPG Telegram Bot")
    print("=" * 60)

    # Проверяем базу данных
    print("\n📊 Проверка базы данных...")
    if not test_connection():
        print("❌ Ошибка подключения к базе данных")
        print("🔄 Пытаюсь пересоздать базу данных...")
        init_db()
        if not test_connection():
            print("❌ Критическая ошибка базы данных")
            return

    # Запуск бота
    print("\n🤖 Запуск бота...")
    try:
        dispatcher.run()
    except KeyboardInterrupt:
        print("\n👋 Бот остановлен пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()