import sqlite3
from config import Config

# ВАШ TELEGRAM ID (тот что у @Simargl1)
YOUR_ID = 561309060

print(f"👑 Добавление суперадмина (ID: {YOUR_ID})...")

conn = sqlite3.connect(Config.DATABASE_PATH)
cur = conn.cursor()

# Проверяем существует ли таблица
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_roles'")
if not cur.fetchone():
    print("❌ Таблица user_roles не существует!")
    print("Добавьте в database/models.py таблицы и пересоздайте БД")
    conn.close()
    exit(1)

# Добавляем роль суперадмина
try:
    cur.execute('''
    INSERT OR REPLACE INTO user_roles (telegram_id, role, granted_by)
    VALUES (?, 'super_admin', ?)
    ''', (YOUR_ID, YOUR_ID))
    conn.commit()
    print(f"✅ Пользователь {YOUR_ID} назначен суперадмином!")
except Exception as e:
    print(f"❌ Ошибка: {e}")

# Проверяем
cur.execute("SELECT * FROM user_roles")
roles = cur.fetchall()
print("\n📋 Текущие роли в БД:")
for role in roles:
    print(f"   Telegram ID: {role[1]}, Роль: {role[2]}")

conn.close()
print("\n🎉 Теперь используйте /admin в боте!")