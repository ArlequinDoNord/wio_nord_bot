"""
Система прав доступа
"""

import sqlite3
from config import Config

# Определение ролей и их прав
ROLES = {
    'super_admin': {  # Хранитель}
        'can_manage_admins': True,
        'can_manage_shop': True,
        'can_manage_finance': True,
        'can_manage_users': True,
        'can_view_logs': True,
        'level': 100
    },
    'shop_admin': {  # Министр торговли
        'can_add_items': True,
        'can_edit_items': True,
        'can_delete_items': True,
        'can_manage_shop': True,
        'level': 50
    },
    'finance_admin': {  # Министр Финансов
        'can_add_currency': True,
        'can_remove_currency': True,
        'can_view_balances': True,
        'level': 50
    },
    'moderator': {  # МВД сотрудник
        'can_approve_reports': True,
        'can_view_reports': True,
        'level': 30
    }
}


def is_admin(telegram_id):
    """Проверка, является ли пользователь админом (любой роли)"""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    cur = conn.cursor()
    cur.execute('SELECT 1 FROM user_roles WHERE telegram_id = ?', (telegram_id,))
    result = cur.fetchone()
    conn.close()
    return result is not None


def has_permission(telegram_id, permission):
    """Проверка наличия конкретного права у пользователя"""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    cur = conn.cursor()

    cur.execute('SELECT role FROM user_roles WHERE telegram_id = ?', (telegram_id,))
    roles = cur.fetchall()
    conn.close()

    for role in roles:
        role_name = role[0]
        if role_name in ROLES and ROLES[role_name].get(permission, False):
            return True
    return False


def get_user_role(telegram_id):
    """Получить список ролей пользователя"""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    cur = conn.cursor()
    cur.execute('SELECT role FROM user_roles WHERE telegram_id = ?', (telegram_id,))
    roles = [row[0] for row in cur.fetchall()]
    conn.close()
    return roles if roles else ['user']


def add_role(admin_id, target_id, role):
    """Добавить роль пользователю (только для суперадмина)"""
    if not has_permission(admin_id, 'can_manage_admins'):
        return False, "У вас нет прав для выдачи ролей"

    conn = sqlite3.connect(Config.DATABASE_PATH)
    cur = conn.cursor()

    try:
        cur.execute('''
        INSERT INTO user_roles (telegram_id, role, granted_by)
        VALUES (?, ?, ?)
        ''', (target_id, role, admin_id))
        conn.commit()

        # Логируем действие
        log_action(admin_id, 'add_role', target_id, f'role={role}')

        return True, f"Роль {role} успешно выдана"
    except sqlite3.IntegrityError:
        return False, "Роль уже есть у пользователя"
    finally:
        conn.close()


def remove_role(admin_id, target_id, role):
    """Удалить роль у пользователя"""
    if not has_permission(admin_id, 'can_manage_admins'):
        return False, "У вас нет прав для удаления ролей"

    conn = sqlite3.connect(Config.DATABASE_PATH)
    cur = conn.cursor()

    cur.execute('''
    DELETE FROM user_roles WHERE telegram_id = ? AND role = ?
    ''', (target_id, role))
    conn.commit()
    conn.close()

    log_action(admin_id, 'remove_role', target_id, f'role={role}')
    return True, f"Роль {role} удалена"


def log_action(admin_id, action, target_id=None, details=None):
    """Логирование действий админов"""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    cur = conn.cursor()
    cur.execute('''
    INSERT INTO admin_logs (admin_id, action, target_id, details)
    VALUES (?, ?, ?, ?)
    ''', (admin_id, action, target_id, details))
    conn.commit()
    conn.close()