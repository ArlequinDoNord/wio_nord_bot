import sqlite3
from config import Config

print("🔧 Добавляем тестовые предметы в магазин...")

conn = sqlite3.connect(Config.DATABASE_PATH)
cur = conn.cursor()

# Проверяем, есть ли уже предметы
cur.execute('SELECT COUNT(*) FROM items')
count = cur.fetchone()[0]

if count > 0:
    print(f"✅ В магазине уже есть {count} предметов")
else:
    # Добавляем тестовые предметы
    test_items = [
        ('Медаль "За отвагу"', 'Повышает уважение среди пилотов', 50, 0, 'consumable', 'uncommon', None,
         '{"prestige": 5}'),
        ('Ремонтный набор', 'Восстанавливает 50% прочности самолета', 100, 10, 'consumable', 'common', None,
         '{"repair": 50}'),
        ('Пистолет P-08', 'Личное оружие для защиты', 200, 0, 'weapon', 'common', None, '{"damage": 15}'),
        ('Квартира в Берлине', 'Комфортное жилье для отдыха', 5000, 0, 'building', 'rare', None, '{"comfort": 30}'),
        ('Аптечка', 'Восстанавливает здоровье', 75, 5, 'consumable', 'common', None, '{"heal": 30}'),
        ('Бомбардировщик Ju-87', 'Пикирующий бомбардировщик', 10000, 50, 'equipment', 'epic', None, '{"damage": 100}'),
    ]

    cur.executemany('''
    INSERT INTO items (name, description, price_nord, price_ap, item_type, rarity, image_path, effect_data)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', test_items)

    conn.commit()
    print(f"✅ Добавлено {len(test_items)} тестовых предметов")

# Показываем что добавилось
cur.execute('SELECT id, name, price_nord, item_type FROM items')
items = cur.fetchall()

print("\n📦 Текущие предметы в магазине:")
for item in items:
    print(f"   {item[0]}. {item[1]} - {item[2]} ✈️ ({item[3]})")

conn.close()
print("\n✅ Готово! Теперь магазин должен работать.")