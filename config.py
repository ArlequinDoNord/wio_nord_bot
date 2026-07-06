import os
from dotenv import load_dotenv
#Загружаем переменные из .env
load_dotenv()

class Config:
    #Основной токен бота
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    # ID администраторов (преобразуем строку в список чисел)
    ADMIN_IDS_STR = os.getenv("ADMIN_IDS","")
    ADMIN_IDS = [int(id.strip()) for id in ADMIN_IDS_STR.split(',') if id.strip()]
    # 🆕 Задержка между запросами к Telegram (избегает флуда)
    REQUEST_DELAY = 0.5  # полсекунды между запросами
    # Путь к базе данных
    DATABASE_PATH = os.getenv("DATABASE_PATH",'database\wnordbot.db')
    #Настройка бота
    BOT_USERNAME = None #будет установлено при запуске

    #Проверка наличия токена
    @classmethod
    def validate(cls):
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN не найден в .env файле!")
        if not cls.ADMIN_IDS:
            print("Внимание: ADMIN_IDS не указаны в .env")
        print(f"Конфигурация загружена")
        print(f" DATABASE_PATH = {cls.DATABASE_PATH}")
#Проверяем конфигурацию при импорте
Config.validate()