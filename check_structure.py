import os
import sys

print("🔍 ПРОВЕРКА СТРУКТУРЫ ПРОЕКТА")
print("=" * 50)

# Проверяем наличие всех необходимых файлов
required_files = [
    "main.py",
    "config.py",
    ".env",
    "database/models.py",
    "database/repository.py",
    "bot/dispatcher.py",
    "bot/handlers/start.py",
    "bot/handlers/profile.py",
    "bot/handlers/shop.py",
]

print("\n📋 Проверка файлов:")
for file in required_files:
    if os.path.exists(file):
        print(f"✅ {file}")
    else:
        print(f"❌ {file}")

print("\n📁 Проверка импортов:")
try:
    from config import Config

    print("✅ config.py импортирован")

    from database.repository import PilotRepository, ShopRepository

    print("✅ repository.py импортирован")

    from bot.dispatcher import dispatcher

    print("✅ dispatcher.py импортирован")

    print("\n🎉 Все готово к запуску!")
except Exception as e:
    print(f"❌ Ошибка импорта: {e}")

print("=" * 50)
