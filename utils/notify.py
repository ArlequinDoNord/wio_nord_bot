"""Оповещения об игровых событиях в общую группу (NEWS_CHAT_ID).

Каждого игрока можно исключить из оповещений (флаг notify_enabled),
переключаемый в профиле — доступно со статуса «Ветеран» и выше.
"""

from aiogram import Bot

from database.db import get_db, get_user, get_news_chat
from config import ADMIN_IDS

# Отчёты с таким количеством очков (и выше) обязательно публикуются после одобрения
NOTIFY_REPORT_MIN_TROOPS = 300


async def player_display(user) -> str:
    """Имя или позывной пилота для красивой подписи."""
    if user is None:
        return "пилот"
    keys = user.keys() if hasattr(user, 'keys') else []
    try:
        username = user['username'] if 'username' in keys else None
    except (KeyError, IndexError):
        username = None
    if username:
        return f"@{username}"
    try:
        name = (user['first_name'] if 'first_name' in keys else '') or ''
    except (KeyError, IndexError):
        name = ''
    name = name.strip()
    if name:
        return name
    try:
        uid = user['user_id'] if 'user_id' in keys else None
    except (KeyError, IndexError):
        uid = None
    return f"#{uid}" if uid is not None else "пилот"


async def notifications_enabled(user_id: int) -> bool:
    user = await get_user(user_id)
    if not user:
        return True
    return bool(user['notify_enabled'] if 'notify_enabled' in user.keys() else 1)


async def notify(bot: Bot, text: str, user_id: int = None):
    """Отправить игровое оповещение в общую группу (или в её топик).

    Куда именно — настройка «news_chat_id» + «news_topic_id» (см. get_news_chat):
    для супергруппы с форумом бот пишет в конкретный топик, иначе — в общий чат.

    Если пользователь отключил оповещения о себе — сообщение не отправляется.
    Ошибка отправки пишется в журнал (handle_error), а не проглатывается молча:
    иначе «нет оповещений» и «бот не имеет прав в чате» выглядят одинаково.
    """
    chat_id, topic_id = await get_news_chat()
    if not chat_id:
        return
    if user_id is not None and not await notifications_enabled(user_id):
        return
    try:
        await bot.send_message(chat_id, text, message_thread_id=topic_id)
    except Exception as e:
        from database.db import log_activity
        await log_activity(None, 'notify_failed', f"chat={chat_id} topic={topic_id}: {e}")


async def treasury_staff_ids() -> list:
    """Telegram-id суперадминов и минфина (для уведомлений о казне)."""
    ids = set(ADMIN_IDS)
    db = await get_db()
    cursor = await db.execute(
        "SELECT DISTINCT telegram_id FROM user_roles WHERE role = 'finance_admin'"
    )
    for row in await cursor.fetchall():
        ids.add(row['telegram_id'])
    return list(ids)


async def notify_treasury_shortage(bot: Bot, total_shortage: int, details: list):
    """Сообщить суперадмину и минфину о нехватке казны на зарплаты.

    details — список кортежей (user_id, amount_owed) тех, кому не хватило.
    """
    if total_shortage <= 0 or not details:
        return
    lines = [
        f"⚠️ НЕХВАТКА КАЗНЫ НА ЗАРПЛАТЫ\n"
        f"Не хватило суммарно: {total_shortage} НМ\n"
        f"Задолженность копится и будет выплачена, когда появятся средства.\n"
        f"\nДолжники:"
    ]
    for uid, amt in details[:15]:
        u = await get_user(uid)
        name = await player_display(u)
        lines.append(f"  • {name}: {amt} НМ")
    if len(details) > 15:
        lines.append(f"  … и ещё {len(details) - 15} пилотов")
    text = "\n".join(lines)
    for tg_id in await treasury_staff_ids():
        try:
            await bot.send_message(tg_id, text)
        except Exception:
            pass