import sqlite3
from config import Config

# ID вашего Telegram (главный админ)
SUPER_ADMIN_ID = 561309060  # Ваш ID

print("👑 Настройка суперадмина...")

conn = sqlite3.connect(Config.DATABASE_PATH)
cur = conn.cursor()

# Добавляем роль суперадмина
cur.execute('''
INSERT OR REPLACE INTO user_roles (telegram_id, role, granted_by)
VALUES (?, 'super_admin', ?)
''', (SUPER_ADMIN_ID, SUPER_ADMIN_ID))

conn.commit()
conn.close()

print(f"✅ Пользователь {SUPER_ADMIN_ID} назначен суперадмином")