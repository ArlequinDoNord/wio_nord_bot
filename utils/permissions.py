"""
Система прав доступа (роли)
Работает с БД через aiosqlite и Config из config.py
"""

from config import ADMIN_IDS
from database.db import get_db

# Определение ролей и их прав
ROLES = {
    'super_admin': {  # Хранитель
        'can_manage_admins': True,
        'can_manage_shop': True,
        'can_manage_finance': True,
        'can_manage_users': True,
        'can_view_logs': True,
        'can_manage_statuses': True,
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
        'can_grant_statuses': True,
        'level': 30
    }
}


async def is_admin(telegram_id: int) -> bool:
    """Является ли пользователь админом (главный админ из .env или по ролям)"""
    if telegram_id in ADMIN_IDS:
        return True
    db = await get_db()
    cursor = await db.execute("SELECT 1 FROM user_roles WHERE telegram_id = ?", (telegram_id,))
    return await cursor.fetchone() is not None


async def has_permission(telegram_id: int, permission: str) -> bool:
    """Проверка наличия конкретного права у пользователя"""
    if telegram_id in ADMIN_IDS:
        return True

    db = await get_db()
    cursor = await db.execute("SELECT role FROM user_roles WHERE telegram_id = ?", (telegram_id,))
    rows = await cursor.fetchall()

    for role in rows:
        role_name = role['role']
        if role_name in ROLES and ROLES[role_name].get(permission, False):
            return True
    return False


async def get_user_role(telegram_id: int) -> list:
    """Получить список ролей пользователя"""
    if telegram_id in ADMIN_IDS:
        return ['super_admin']

    db = await get_db()
    cursor = await db.execute("SELECT role FROM user_roles WHERE telegram_id = ?", (telegram_id,))
    roles = [row['role'] for row in await cursor.fetchall()]
    return roles if roles else ['user']


async def add_role(admin_id: int, target_id: int, role: str):
    """Добавить роль пользователю (только для суперадмина)"""
    if not await has_permission(admin_id, 'can_manage_admins'):
        return False, "У вас нет прав для выдачи ролей"

    db = await get_db()
    try:
        await db.execute(
            "INSERT INTO user_roles (telegram_id, role, granted_by) VALUES (?, ?, ?)",
            (target_id, role, admin_id)
        )
        await db.commit()
        await log_action(admin_id, 'add_role', target_id, f'role={role}')
        return True, f"Роль {role} успешно выдана"
    except Exception:
        return False, "Роль уже есть у пользователя или ошибка базы данных"


async def remove_role(admin_id: int, target_id: int, role: str):
    """Удалить роль у пользователя"""
    if not await has_permission(admin_id, 'can_manage_admins'):
        return False, "У вас нет прав для удаления ролей"

    db = await get_db()
    await db.execute(
        "DELETE FROM user_roles WHERE telegram_id = ? AND role = ?",
        (target_id, role)
    )
    await db.commit()
    await log_action(admin_id, 'remove_role', target_id, f'role={role}')
    return True, f"Роль {role} удалена"


async def log_action(admin_id: int, action: str, target_id: int = None, details: str = None):
    """Логирование действий админов"""
    db = await get_db()
    await db.execute(
        "INSERT INTO admin_logs (admin_id, action, target_id, details) VALUES (?, ?, ?, ?)",
        (admin_id, action, target_id, details)
    )
    await db.commit()
