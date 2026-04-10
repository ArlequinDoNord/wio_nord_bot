"""
Репозиторий для работы с базой данных
"""

import sqlite3
from datetime import datetime
import sys
import os

# Добавляем путь к корневой папке
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config


class PilotRepository:
    """Репозиторий для работы с пилотами"""

    @staticmethod
    def save_pilot_photo(telegram_id, photo_file_id):
        """
        Сохранить file_id фото пилота
        Args:
            telegram_id: ID пользователя
            photo_file_id: file_id фото из Telegram
        """
        conn = sqlite3.connect(Config.DATABASE_PATH)
        cur = conn.cursor()

        cur.execute('''
        UPDATE pilots SET photo_file_id = ? WHERE telegram_id = ?''', (photo_file_id, telegram_id))
        conn.commit()
        conn.close()
        print(f"Фото сохранено для пилота {telegram_id}")

    @staticmethod
    def get_pilot_photo(telegram_id):
        """
        Получить file_id фото пилота

        Args:
            telegram_id: ID пользователя

        Returns:
            str: file_id фото или None
        """
        conn = sqlite3.connect(Config.DATABASE_PATH)
        cur = conn.cursor()

        cur.execute('SELECT photo_file_id FROM pilots WHERE telegram_id = ?', (telegram_id,))
        result = cur.fetchone()

        conn.close()
        return result[0] if result and result[0] else None

    @staticmethod
    def delete_pilot_photo(telegram_id):
        """
        Удалить фото пилота

        Args:
            telegram_id: ID пользователя
        """
        conn = sqlite3.connect(Config.DATABASE_PATH)
        cur = conn.cursor()

        cur.execute('''
            UPDATE pilots 
            SET photo_file_id = NULL 
            WHERE telegram_id = ?
            ''', (telegram_id,))

        conn.commit()
        conn.close()
        print(f"✅ Фото удалено для пилота {telegram_id}")

    @staticmethod
    def get_or_create_pilot(telegram_id, username=None, full_name=None):
        """
        Получить пилота по telegram_id или создать нового

        Args:
            telegram_id: ID пользователя в Telegram
            username: Username пользователя
            full_name: Полное имя пользователя

        Returns:
            tuple: Данные пилота
        """
        conn = sqlite3.connect(Config.DATABASE_PATH)
        cur = conn.cursor()

        # Проверяем, существует ли пилот
        cur.execute('SELECT * FROM pilots WHERE telegram_id = ?', (telegram_id,))
        pilot = cur.fetchone()

        if not pilot:
            # Создаем нового пилота
            current_time = datetime.now()
            cur.execute('''
            INSERT INTO pilots (telegram_id, username, full_name, registration_date, last_active)
            VALUES (?, ?, ?, ?, ?)
            ''', (telegram_id, username, full_name, current_time, current_time))
            conn.commit()

            # Получаем созданного пилота
            cur.execute('SELECT * FROM pilots WHERE telegram_id = ?', (telegram_id,))
            pilot = cur.fetchone()
            print(f"✅ Создан новый пилот: {full_name} (ID: {telegram_id})")
        else:
            # Обновляем время последнего визита
            cur.execute('''
            UPDATE pilots SET last_active = ? WHERE telegram_id = ?
            ''', (datetime.now(), telegram_id))
            conn.commit()

        conn.close()
        return pilot

    @staticmethod
    def get_pilot_profile(telegram_id):
        """
        Получить профиль пилота

        Args:
            telegram_id: ID пользователя в Telegram

        Returns:
            tuple: (full_name, rank, level, experience, nord_marks, action_points, registration_date, last_active)
        """
        conn = sqlite3.connect(Config.DATABASE_PATH)
        cur = conn.cursor()

        cur.execute('''
        SELECT 
            full_name, rank, level, experience,
            nord_marks, action_points,
            registration_date, last_active
        FROM pilots 
        WHERE telegram_id = ?
        ''', (telegram_id,))

        profile = cur.fetchone()
        conn.close()
        return profile

    @staticmethod
    def update_pilot_currency(telegram_id, nord_delta=0, ap_delta=0):
        """
        Обновить валюту пилота с проверкой лимитов

        Args:
            telegram_id: ID пользователя
            nord_delta: Изменение нордмарок (может быть отрицательным)
            ap_delta: Изменение очков действия (с проверкой лимита 150)

        Returns:
            tuple: (new_nord, new_ap)
        """
        conn = sqlite3.connect(Config.DATABASE_PATH)
        cur = conn.cursor()

        # Получаем текущие значения
        cur.execute(
            'SELECT nord_marks, action_points FROM pilots WHERE telegram_id = ?',
            (telegram_id,)
        )
        result = cur.fetchone()

        if not result:
            conn.close()
            return None, None

        nord_marks, action_points = result

        # Обновляем с проверкой лимитов
        new_nord = max(0, nord_marks + nord_delta)
        new_ap = max(0, min(150, action_points + ap_delta))  # Ограничение 150 AP

        cur.execute('''
        UPDATE pilots 
        SET nord_marks = ?, action_points = ?, last_active = ?
        WHERE telegram_id = ?
        ''', (new_nord, new_ap, datetime.now(), telegram_id))

        conn.commit()
        conn.close()

        return new_nord, new_ap

    @staticmethod
    def add_experience(telegram_id, exp_amount):
        """
        Добавить опыт пилоту и проверить повышение уровня

        Args:
            telegram_id: ID пользователя
            exp_amount: Количество опыта для добавления

        Returns:
            tuple: (new_level, leveled_up)
        """
        conn = sqlite3.connect(Config.DATABASE_PATH)
        cur = conn.cursor()

        # Получаем текущие значения
        cur.execute(
            'SELECT level, experience FROM pilots WHERE telegram_id = ?',
            (telegram_id,)
        )
        level, experience = cur.fetchone()

        # Добавляем опыт
        new_experience = experience + exp_amount

        # Проверяем повышение уровня (простая формула: уровень * 100)
        new_level = level
        while new_experience >= new_level * 100:
            new_experience -= new_level * 100
            new_level += 1

        leveled_up = new_level > level

        # Обновляем значения
        cur.execute('''
        UPDATE pilots 
        SET level = ?, experience = ?, last_active = ?
        WHERE telegram_id = ?
        ''', (new_level, new_experience, datetime.now(), telegram_id))

        conn.commit()
        conn.close()

        # Обновляем ранг на основе уровня
        if leveled_up:
            PilotRepository.update_rank(telegram_id, new_level)

        return new_level, leveled_up

    @staticmethod
    def update_rank(telegram_id, level):
        """
        Обновить ранг пилота на основе уровня

        Args:
            telegram_id: ID пользователя
            level: Текущий уровень
        """
        ranks = {
            1: "Рядовой",
            2: "Капрал",
            3: "Сержант",
            4: "Лейтенант",
            5: "Капитан",
            6: "Майор",
            7: "Подполковник",
            8: "Полковник",
            9: "Генерал-майор",
            10: "Генерал-лейтенант"
        }

        rank = ranks.get(level, f"Ас {level} уровня")

        conn = sqlite3.connect(Config.DATABASE_PATH)
        cur = conn.cursor()

        cur.execute('''
        UPDATE pilots SET rank = ? WHERE telegram_id = ?
        ''', (rank, telegram_id))

        conn.commit()
        conn.close()

    @staticmethod
    def get_pilot_stats(telegram_id):
        """
        Получить расширенную статистику пилота

        Args:
            telegram_id: ID пользователя в Telegram

        Returns:
            dict: Статистика пилота или None
        """
        conn = sqlite3.connect(Config.DATABASE_PATH)
        cur = conn.cursor()

        # Получаем ID пилота
        cur.execute('SELECT id FROM pilots WHERE telegram_id = ?', (telegram_id,))
        result = cur.fetchone()

        if not result:
            conn.close()
            return None

        pilot_db_id = result[0]

        # Считаем количество отчетов
        cur.execute('''
            SELECT 
                COUNT(*) as total_reports,
                SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) as approved_reports
            FROM reports 
            WHERE pilot_id = ?
            ''', (pilot_db_id,))

        reports_stats = cur.fetchone()
        total_reports = reports_stats[0] or 0
        approved_reports = reports_stats[1] or 0

        # Считаем предметы в инвентаре
        cur.execute('''
            SELECT COUNT(*), SUM(quantity) 
            FROM inventory 
            WHERE pilot_id = ?
            ''', (pilot_db_id,))

        inv_stats = cur.fetchone()
        unique_items = inv_stats[0] or 0
        total_items = inv_stats[1] or 0

        conn.close()

        return {
            'total_reports': total_reports,
            'approved_reports': approved_reports,
            'unique_items': unique_items,
            'total_items': total_items
        }

class ShopRepository:
    """Репозиторий для работы с магазином"""

    @staticmethod
    def get_all_items():
        """
        Получить все предметы магазина

        Returns:
            list: Список всех предметов
        """
        conn = sqlite3.connect(Config.DATABASE_PATH)
        cur = conn.cursor()

        cur.execute('SELECT * FROM items ORDER BY price_nord')
        items = cur.fetchall()
        conn.close()
        return items

    @staticmethod
    def get_item_by_id(item_id):
        """
        Получить предмет по ID

        Args:
            item_id: ID предмета

        Returns:
            tuple: Данные предмета или None
        """
        conn = sqlite3.connect(Config.DATABASE_PATH)
        cur = conn.cursor()

        cur.execute('SELECT * FROM items WHERE id = ?', (item_id,))
        item = cur.fetchone()
        conn.close()
        return item

    @staticmethod
    def buy_item(pilot_id, item_id, payment_type='nord'):
        """
        Купить предмет

        Args:
            pilot_id: ID пилота
            item_id: ID предмета
            payment_type: 'nord' или 'ap'

        Returns:
            tuple: (success, message)
        """
        conn = sqlite3.connect(Config.DATABASE_PATH)
        cur = conn.cursor()

        try:
            # Получаем информацию о предмете
            cur.execute('SELECT * FROM items WHERE id = ?', (item_id,))
            item = cur.fetchone()

            if not item:
                return False, "Предмет не найден"

            # Получаем информацию о пилоте
            cur.execute('SELECT id, nord_marks, action_points FROM pilots WHERE id = ?', (pilot_id,))
            pilot = cur.fetchone()

            if not pilot:
                return False, "Пилот не найден"

            pilot_db_id, nord_marks, action_points = pilot
            price_nord = item[3]  # price_nord
            price_ap = item[4]  # price_ap

            # Проверяем возможность покупки
            if payment_type == 'nord':
                if nord_marks < price_nord:
                    return False, f"Недостаточно нордмарок! Нужно: {price_nord}, есть: {nord_marks}"

                # Списываем нордмарки
                new_nord = nord_marks - price_nord
                cur.execute('UPDATE pilots SET nord_marks = ? WHERE id = ?', (new_nord, pilot_db_id))

            elif payment_type == 'ap':
                if action_points < price_ap:
                    return False, f"Недостаточно очков действия! Нужно: {price_ap}, есть: {action_points}"

                # Списываем AP
                new_ap = action_points - price_ap
                cur.execute('UPDATE pilots SET action_points = ? WHERE id = ?', (new_ap, pilot_db_id))

            # Добавляем предмет в инвентарь
            cur.execute('''
            INSERT INTO inventory (pilot_id, item_id, quantity)
            VALUES (?, ?, 1)
            ''', (pilot_db_id, item_id))

            conn.commit()
            return True, f"✅ Вы купили: {item[1]}"

        except Exception as e:
            conn.rollback()
            return False, f"Ошибка при покупке: {e}"

        finally:
            conn.close()


class InventoryRepository:
    """Репозиторий для работы с инвентарем"""

    @staticmethod
    def get_pilot_inventory(telegram_id):
        """
        Получить инвентарь пилота

        Args:
            telegram_id: ID пользователя в Telegram

        Returns:
            list: Список предметов в инвентаре
        """
        conn = sqlite3.connect(Config.DATABASE_PATH)
        cur = conn.cursor()

        cur.execute('''
        SELECT i.id, i.name, i.description, i.item_type, i.rarity, inv.quantity, inv.equipped
        FROM inventory inv
        JOIN items i ON inv.item_id = i.id
        JOIN pilots p ON inv.pilot_id = p.id
        WHERE p.telegram_id = ?
        ORDER BY i.item_type, i.name
        ''', (telegram_id,))

        inventory = cur.fetchall()
        conn.close()
        return inventory

    @staticmethod
    def use_item(inventory_id):
        """
        Использовать предмет (для расходников)

        Args:
            inventory_id: ID записи в инвентаре

        Returns:
            tuple: (success, message)
        """
        conn = sqlite3.connect(Config.DATABASE_PATH)
        cur = conn.cursor()

        try:
            # Получаем информацию о предмете
            cur.execute('''
            SELECT i.item_type, inv.quantity
            FROM inventory inv
            JOIN items i ON inv.item_id = i.id
            WHERE inv.id = ?
            ''', (inventory_id,))

            result = cur.fetchone()
            if not result:
                return False, "Предмет не найден"

            item_type, quantity = result

            if item_type != 'consumable':
                return False, "Этот предмет нельзя использовать"

            if quantity > 1:
                cur.execute('UPDATE inventory SET quantity = quantity - 1 WHERE id = ?', (inventory_id,))
            else:
                cur.execute('DELETE FROM inventory WHERE id = ?', (inventory_id,))

            conn.commit()
            return True, "Предмет использован"

        except Exception as e:
            conn.rollback()
            return False, f"Ошибка: {e}"

        finally:
            conn.close()


# Для проверки работоспособности
if __name__ == '__main__':
    print("🔍 Тестирование репозитория...")

    # Проверяем подключение
    try:
        conn = sqlite3.connect(Config.DATABASE_PATH)
        print("✅ Подключение к БД успешно")
        conn.close()

        # Проверяем методы
        print("📦 Доступные классы:")
        print(f"   - PilotRepository")
        print(f"   - ShopRepository")
        print(f"   - InventoryRepository")

    except Exception as e:
        print(f"❌ Ошибка: {e}")