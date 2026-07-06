import sqlite3
from config import Config

print("🔍 Проверка прав администратора...")

conn = sqlite3.connect(Config.DATABASE_PATH)
cur = conn.cursor()

# Проверяем таблицу
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_roles'")
if not cur.fetchone():
    print("❌ Таблица user_roles не существует!")
    print("Сначала добавьте таблицы в database/models.py и пересоздайте БД")
    conn.close()
    exit(1)

# Проверяем есть ли записи
cur.execute("SELECT * FROM user_roles")
roles = cur.fetchall()

if not roles:
    print("❌ В таблице user_roles нет записей!")
    print("Никто не имеет прав администратора")
else:
    print("📋 Текущие роли:")
    for role in roles:
        print(f"   Telegram ID: {role[1]}, Роль: {role[2]}")

conn.close()