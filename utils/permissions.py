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
        'can_grant_troops': True,
        'can_manage_library': True,
        'can_create_polls': True,
        'can_address_city': True,
        'can_manage_states': True,
        'can_manage_salaries': True,
        'can_manage_locations': True,
        'can_manage_awards': True,
        'can_grant_awards': True,
        'can_manage_storage': True,
        'can_post_news': True,
        'can_manage_news': True,
        'can_manage_wing': True,
        'can_send_orders': True,
        'can_manage_clans': True,
        'can_assign_mvd_helper': True,
        # Хранитель из роли (а не из .env) должен видеть отчёты наравне с владельцем.
        'can_view_reports': True,
        'can_approve_reports': True,
        # Право на выдачу статуса, закреплённое за владельцем.
        'can_grant_statuses': True,
        # Супер-админ выше главы МВД, поэтому право на ворота в гражданство
        # у него тоже есть (can_grant_statuses выше по списку уже покрывает
        # любой статус, но флаг нужен для согласованности с moderator).
        'can_grant_citizen_status': True,
        # Сейчас избыточно: у Хранителя уже есть can_manage_finance, который
        # подразумевает и просмотр. Оставлено явно — чтобы возможность видеть
        # казну не исчезла, если владелец уберёт у Хранителя полные права.
        'can_view_balances': True,
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
        'can_manage_finance': True,
        'can_add_currency': True,
        'can_remove_currency': True,
        'can_view_balances': True,
        'level': 50
    },
    'finance_helper': {  # Квестор (Quaestor) — помощник Минфина
        'can_add_currency': True,
        # Начислять деньги, не видя их, бессмысленно — поэтому доступ к
        # просмотру казны. Тратить из неё всё равно нельзя: это отдельное
        # право can_manage_finance, которого у Квестора нет.
        'can_view_balances': True,
        'level': 20
    },
    'moderator': {  # МВД сотрудник / глава МВД
        'can_approve_reports': True,
        'can_view_reports': True,
        'can_grant_troops': True,
        'can_manage_wing': True,
        'can_send_orders': True,
        # Глава МВД сам назначает и снимает вице-доминуса (помощника).
        # Другие роли через can_manage_admins ему не доступны.
        'can_assign_mvd_helper': True,
        # Приём в гражданство: глава МВД выдаёт и снимает статус-ворота
        # («Рекрут», sort_order = 1). Остальные статусы — только владелец.
        'can_grant_citizen_status': True,
        'level': 30
    },
    'wing_commander': {  # Командир авиакрыла
        'can_wing_commands': True,
        'level': 60
    },
    'wing_deputy': {  # Заместитель командира авиакрыла
        'can_wing_commands': True,
        'level': 40
    },
    'mvd_helper': {  # Вице-доминус (Vicedominus) — помощник МВД
        'can_approve_reports': True,
        'can_view_reports': True,
        'level': 20
    },
    'librarian': {  # Библиотекарь — управление книгами библиотеки
        'can_manage_library': True,
        'level': 40
    },
    'representative': {  # Представитель = Главнокомандующий ВВС: опросы (2 в сутки),
        # речь городу (4 в сутки) и приказы штаба всем авиакрыльям сразу.
        'can_create_polls': True,
        'can_address_city': True,
        'can_send_orders': True,
        'level': 15
    },
    'journalist': {  # Журналист ГосСМИ — пишет новости (лимит 2 в сутки)
        'can_post_news': True,
        'level': 20
    },
    'editor': {  # Редактор ГосСМИ — новости, редактирование/удаление выпусков
        'can_post_news': True,
        'can_manage_news': True,
        'level': 40
    },
    'clan_leader': {  # Глава клана/партии — управляет только своим объединением
        'level': 60
    }
}

# Красивые названия ролей
ROLE_LABELS = {
    'super_admin': 'Хранитель',
    'shop_admin': 'Министр торговли',
    'finance_admin': 'Министр финансов',
    'finance_helper': 'Квестор',
    'moderator': 'МВД',
    'wing_commander': 'Командир авиакрыла',
    'wing_deputy': 'Заместитель командира авиакрыла',
    'mvd_helper': 'Вице-доминус',
    'librarian': 'Библиотекарь',
    'representative': 'Представитель',
    'journalist': 'Журналист ГосСМИ',
    'editor': 'Редактор ГосСМИ',
    'clan_leader': 'Глава клана/партии',
}


def role_label(role: str) -> str:
    return ROLE_LABELS.get(role, role)


# Статус-ворота в гражданство: он делает пилота гражданином, потому что
# гражданство в коде — это «старший статус с sort_order >= 1» (db._citizens_sql).
# «Турист» = -10 (не гражданин), «Рекрут» = 1 (гражданин). Право
# can_grant_citizen_status ограничено именно этим статусом и ничего больше.
CITIZEN_GATE_SORT_ORDER = 1
CITIZEN_GATE_TAG = "recruit"


def is_citizen_gate_status(status) -> bool:
    """Является ли строка статуса воротами в гражданство."""
    if not status:
        return False
    try:
        keys = status.keys()
    except AttributeError:
        return False
    if "access_tag" in keys and status["access_tag"] == CITIZEN_GATE_TAG:
        return True
    if "sort_order" in keys:
        return (status["sort_order"] or 0) == CITIZEN_GATE_SORT_ORDER
    return False


async def can_grant_status(actor_id: int, status) -> bool:
    """Может ли actor_id выдать/снять именно этот статус.

    Полный доступ (can_manage_statuses — создание/удаление/выдача любого
    статуса, либо can_grant_statuses) остаётся за владельцем. Глава МВД
    (can_grant_citizen_status) — только статус-ворота в гражданство, то есть
    может принять туриста в гражданство, но не может выдать «Аса» или
    «Хранителя» даже себе.
    """
    if await has_permission(actor_id, 'can_manage_statuses'):
        return True
    if await has_permission(actor_id, 'can_grant_statuses'):
        return True
    if await has_permission(actor_id, 'can_grant_citizen_status'):
        return is_citizen_gate_status(status)
    return False


async def can_view_status_panel(actor_id: int) -> bool:
    """Видно ли меню управления статусами (список — всем, кто сюда допущен)."""
    return (await has_permission(actor_id, 'can_manage_statuses')
            or await has_permission(actor_id, 'can_grant_statuses')
            or await has_permission(actor_id, 'can_grant_citizen_status'))


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


# Роли, которые умеет назначать не только суперадмин, а профильный руководитель.
DELEGABLE_ROLES = {
    'mvd_helper': 'can_assign_mvd_helper',   # глава МВД назначает вице-доминуса
}


async def can_assign_role(admin_id: int, role: str) -> bool:
    """Может ли admin_id выдать/снять роль role.

    Полный доступ — у can_manage_admins (Хранитель). Точечный доступ есть у
    профильных руководителей: глава МВД (moderator) может назначать и снимать
    только вице-доминуса, и больше ничего.
    """
    if await has_permission(admin_id, 'can_manage_admins'):
        return True
    needed = DELEGABLE_ROLES.get(role)
    return bool(needed) and await has_permission(admin_id, needed)


async def add_role(admin_id: int, target_id: int, role: str):
    """Добавить роль пользователю (суперадмин — любую, глава МВД — вице-доминуса)"""
    if not await can_assign_role(admin_id, role):
        if role in DELEGABLE_ROLES:
            return False, "У вас нет прав для выдачи этой роли"
        return False, "У вас нет прав для выдачи ролей"

    if role not in ROLES:
        return False, "Неизвестная роль"
    if role == 'super_admin':
        return False, "Роль «Хранитель» выдаётся только командой"

    db = await get_db()
    try:
        await db.execute(
            "INSERT INTO user_roles (telegram_id, role, granted_by) VALUES (?, ?, ?)",
            (target_id, role, admin_id)
        )
        await db.commit()
        await log_action(admin_id, 'add_role', target_id, f'role={role}')
        return True, f"Роль {role_label(role)} успешно выдана"
    except Exception:
        return False, "Роль уже есть у пользователя или ошибка базы данных"


async def remove_role(admin_id: int, target_id: int, role: str):
    """Удалить роль у пользователя (суперадмин — любую, глава МВД — вице-доминуса)"""
    if not await can_assign_role(admin_id, role):
        if role in DELEGABLE_ROLES:
            return False, "У вас нет прав для снятия этой роли"
        return False, "У вас нет прав для удаления ролей"

    db = await get_db()
    await db.execute(
        "DELETE FROM user_roles WHERE telegram_id = ? AND role = ?",
        (target_id, role)
    )
    await db.commit()
    await log_action(admin_id, 'remove_role', target_id, f'role={role}')
    return True, f"Роль {role_label(role)} удалена"


async def log_action(admin_id: int, action: str, target_id: int = None, details: str = None):
    """Логирование действий админов"""
    db = await get_db()
    await db.execute(
        "INSERT INTO admin_logs (admin_id, action, target_id, details) VALUES (?, ?, ?, ?)",
        (admin_id, action, target_id, details)
    )
    await db.commit()
