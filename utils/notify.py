"""Оповещения об игровых событиях в общую группу (NEWS_CHAT_ID).

Каждого игрока можно исключить из оповещений (флаг notify_enabled),
переключаемый в профиле — доступно со статуса «Ветеран» и выше.
"""

from aiogram import Bot

from config import NEWS_CHAT_ID
from database.db import get_user

# Отчёты с таким количеством очков (и выше) обязательно публикуются после одобрения
NOTIFY_REPORT_MIN_TROOPS = 300


async def player_display(user) -> str:
    """Имя или позывной пилота для красивой подписи."""
    if user and user.get('username'):
        return f"@{user['username']}"
    name = ((user or {}).get('first_name') or '').strip()
    if name:
        return name
    return f"#{user.get('user_id')}" if user else "пилот"


async def notifications_enabled(user_id: int) -> bool:
    user = await get_user(user_id)
    if not user:
        return True
    return bool(user.get('notify_enabled', 1))


async def notify(bot: Bot, text: str, user_id: int = None):
    """Отправить игровое оповещение в группу.

    Если пользователь отключил оповещения о себе — сообщение не отправляется.
    """
    if not NEWS_CHAT_ID:
        return
    if user_id is not None and not await notifications_enabled(user_id):
        return
    try:
        await bot.send_message(NEWS_CHAT_ID, text)
    except Exception:
        pass