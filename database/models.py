import sqlite3
from datetime import datetime
import os
import sys

# Добавляем путь к корневой папке проекта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

def init_db():
    """Инициализация базы данных и создание таблиц"""
    # Создаем папку database если её нет
    print(f"📁 Путь к БД из конфига: {Config.DATABASE_PATH}")

    # Исправляем путь - убираем лишнее database/
    # Если мы в папке database, то путь должен быть просто "wnordbot.db"

    current_dir = os.path.basename(os.getcwd())
    if current_dir == "database":
        #Мы находимся в папке database, используем просто имя файла
        db_path = "wnordbot.db"
    else:
        #мы в корне проекта
        db_path = Config.DATABASE_PATH


    # Получаем абсолютный путь
    abs_db_path = os.path.abspath(db_path)
    print(f"📁 Абсолютный путь: {abs_db_path}")

    # Создаем папку для БД (только директорию, не весь путь)
    db_dir = os.path.dirname(abs_db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
        print(f"📁 Создана/проверена папка: {db_dir}")

    # Подключаемся к БД
    conn = sqlite3.connect(abs_db_path)
    cur = conn.cursor()

    # Включаем внешние ключи
    cur.execute("PRAGMA foreign_keys = ON")

    # 1. Таблица пилотов (основная сущность)
    print("📦 Создаем таблицу pilots...")
    cur.execute('''
    CREATE TABLE IF NOT EXISTS pilots (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       telegram_id INTEGER UNIQUE NOT NULL,
       username TEXT,
       full_name TEXT,
       rank TEXT DEFAULT 'Рекрут',
       level INTEGER DEFAULT 1,
       experience INTEGER DEFAULT 0,
       nord_marks INTEGER DEFAULT 0,
       action_points INTEGER DEFAULT 0,
       photo_file_id TEXT,
       registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 2. Таблица предметов магазина
    print("📦 Создаем таблицу items...")
    cur.execute('''
    CREATE TABLE IF NOT EXISTS items (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       name TEXT NOT NULL,
       description TEXT,
       price_nord INTEGER DEFAULT 0,
       price_ap INTEGER DEFAULT 0,
       item_type TEXT DEFAULT 'consumable',
       rarity TEXT DEFAULT 'common',
       image_path TEXT,
       effect_data TEXT 
    )
    ''')

    # 3.Таблица инвентаря
    print("📦 Создаем таблицу inventory...")
    cur.execute('''
    CREATE TABLE IF NOT EXISTS inventory (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       pilot_id INTEGER NOT NULL,
       item_id INTEGER NOT NULL,
       quantity INTEGER DEFAULT 1,
       equipped INTEGER DEFAULT 0,
       FOREIGN KEY (pilot_id) REFERENCES pilots (id), 
       FOREIGN KEY (item_id) REFERENCES users (id) 
    )
    ''')

    # 4. Таблица статусов (отчетов)
    cur.execute('''
    CREATE TABLE IF NOT EXISTS reports (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       pilot_id INTEGER NOT NULL,
       screenshot_file_id TEXT,
       answers TEXT,
       status TEXT DEFAULT 'pending',
       reward_nord INTEGER DEFAULT 0,
       reward_ap INTEGER DEFAULT 0,
       reward_issued BOOLEAN DEFAULT 0,
       submission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       review_date TIMESTAMP,
       reviewer_id INTEGER,
       FOREIGN KEY (pilot_id) REFERENCES pilots (id) 
    )
    ''')
    # 5. Таблица ролей пользователей
    cur.execute('''
    CREATE TABLE IF NOT EXISTS user_roles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER NOT NULL,
        role TEXT NOT NULL,  -- admin, shop_admin, finance_admin, moderator
        granted_by INTEGER,
        granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (telegram_id) REFERENCES pilots (telegram_id),
        UNIQUE(telegram_id, role)
    )
    ''')

    # 6. Таблица логов админ-действий
    cur.execute('''
    CREATE TABLE IF NOT EXISTS admin_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        admin_id INTEGER NOT NULL,
        action TEXT NOT NULL,
        target_id INTEGER,
        details TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 7. Таблица для временного хранения изображений товаров
    cur.execute('''
    CREATE TABLE IF NOT EXISTS temp_item_images (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        admin_id INTEGER NOT NULL,
        file_id TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()

    # Проверяем, есть ли уже предметы
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='items'")
    if cur.fetchone():
       cur.execute('SELECT COUNT(*) FROM items')
       count = cur.fetchone()[0]

       if count == 0:
       #5. Добавляем тестовые предметы в магазин
          print("📦 Добавляем тестовые предметы...")
          test_items =[
           ('Банка малинового джема', 'Востанавливает 20 единиц здоровья', 25, 0, 'consumable', 'common', None, '{"regen": 20}'),
           ('Пистолет P-08', 'Личное оружие для защиты', 200, 0, 'weapon', 'common', None, '{"damage": 15}'),
           ('Квартира в Берлине', 'Комфортное жилье для отдыха', 5000, 0, 'building', 'rare', None, '{"comfort": 30}'),
          ]

          cur.executemany('''
          INSERT INTO items (name, description, price_nord, price_ap, item_type, rarity, image_path, effect_date)
          VALUES (?, ?, ?, ?, ?, ?, ?, ?)
          ''', test_items)
          conn.commit()
          print(f" Добавлено {len(test_items)} тестовых предметов")


    conn.close()

    #Проверяем результат
    verify_db(abs_db_path)

def verify_db(db_path):
    """Проверка созданной БД"""
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        # Получаем список таблиц
        cur.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        tables = cur.fetchall()

        print("\n🔍 ПРОВЕРКА БАЗЫ ДАННЫХ:")
        print(f"📊 Найдены таблицы: {[t[0] for t in tables]}")

        # Проверяем каждую таблицу
        for table in tables:
            table_name = table[0]
            cur.execute(f'SELECT COUNT(*) FROM {table_name}')
            count = cur.fetchone()[0]
            print(f"   {table_name} : {count}")


            # Показываем структуру таблицы
            cur.execute(f"PRAGMA table_info({table_name})")
            columns = cur.fetchall()
            print(f"   Столбцы: {[col[1] for col in columns]}")
        conn.close()
        print(" БД успешно создана и проверена!")
        return True

    except Exception as e:
        print(f" Ошибка при проверке БД: {e}")
        return False


def test_connection():
    """
    Тестирование подключения к базе данных

    Returns:
        bool: True если подключение успешно, False если ошибка
    """
    try:
        # Проверяем существует ли файл БД
        if not os.path.exists(Config.DATABASE_PATH):
            print(f"❌ Файл БД не найден: {Config.DATABASE_PATH}")
            return False

        # Подключаемся к БД
        conn = sqlite3.connect(Config.DATABASE_PATH)
        cur = conn.cursor()

        # Проверяем наличие таблиц
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cur.fetchall()

        if not tables:
            print("❌ В базе данных нет таблиц")
            conn.close()
            return False

        # Проверяем основные таблицы
        required_tables = ['pilots', 'items', 'inventory', 'reports']
        existing_tables = [t[0] for t in tables]

        missing_tables = [t for t in required_tables if t not in existing_tables]

        if missing_tables:
            print(f"❌ Отсутствуют таблицы: {missing_tables}")
            conn.close()
            return False

        # Проверяем целостность каждой таблицы
        for table in required_tables:
            try:
                cur.execute(f'SELECT COUNT(*) FROM {table}')
                count = cur.fetchone()[0]
                print(f"✅ Таблица {table}: {count} записей")
            except Exception as e:
                print(f"❌ Ошибка в таблице {table}: {e}")
                conn.close()
                return False

        conn.close()
        print(f"✅ Подключение к БД успешно: {Config.DATABASE_PATH}")
        return True

    except Exception as e:
        print(f"❌ Ошибка подключения к БД: {e}")
        return False

if __name__ == '__main__':
    print("=" * 50)
    print(" Инициализация БАЗЫ ДАННЫХ")
    print("=" * 50)

    # Проверяем конфигурацию
    print(f"📁 Текущая папка: {os.getcwd()}")
    print(f"📁 Имя текущей папки: {os.path.basename(os.getcwd())}")

    # Создаем таблицы
    init_db()

    # Тестируем подключение
    print("\n🔍 ТЕСТ ПОДКЛЮЧЕНИЯ:")
    test_connection()

    print("=" * 50)