import sqlite3
from config import Config

print("🔧 Добавляем колонку photo_file_id в таблицу pilots...")

conn = sqlite3.connect(Config.DATABASE_PATH)
cur = conn.cursor()

try:
    # Добавляем колонку
    cur.execute('ALTER TABLE pilots ADD COLUMN photo_file_id TEXT')
    print("✅ Колонка photo_file_id добавлена")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("✅ Колонка photo_file_id уже существует")
    else:
        print(f"❌ Ошибка: {e}")

# Проверяем структуру таблицы
cur.execute('PRAGMA table_info(pilots)')
columns = cur.fetchall()
print("\n📊 Текущие колонки в таблице pilots:")
for col in columns:
    print(f"   {col[1]} ({col[2]})")

conn.commit()
conn.close()
print("\n✅ Готово!")