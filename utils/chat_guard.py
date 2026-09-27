"""Ограничение работы бота по чатам.

Бота постоянно добавляют в посторонние группы и там вызывают команды: он отвечал
меню с кнопками прямо в общем чате. Теперь вне личных сообщений бот работает только
в разрешённых чатах (настраивается), а в чужих группах не отвечает ничего, кроме
короткой подсказки «работаю в личке» — и то не чаще раза в час на чат, чтобы не
засорять чат.

Белый список:
  • личные сообщения — всегда разрешены;
  • чат оповещений (news_chat_id) и чаты из настройки allowed_chats.
"""

import time

from aiogram import BaseMiddleware

from database.db import get_allowed_chats, get_news_chat

HINT = ("🤖 Н.О.Р.Д. работает только в личных сообщениях и в своей группе.\n"
        "Напишите мне в личку: @Nord_Wio_bot")
HINT_INTERVAL = 3600  # не чаще раза в час на один чат

# chat_id -> время последней подсказки
_hints: dict[int, float] = {}

# Кэш белого списка, чтобы не ходить в БД на каждое обновление.
_cache: dict = {"ts": 0.0, "ids": set()}


def _event_chat(event):
    chat = getattr(event, "chat", None)
    if chat is not None:
        return chat
    msg = getattr(event, "message", None)
    return getattr(msg, "chat", None) if msg is not None else None


def _is_command(event) -> bool:
    text = getattr(event, "text", None)
    return bool(text and text.startswith("/"))


async def allowed_chat_ids() -> set:
    now = time.monotonic()
    if now - _cache["ts"] > 30:
        ids = set(await get_allowed_chats())
        news_chat, _ = await get_news_chat()
        if news_chat:
            ids.add(int(news_chat))
        _cache["ids"] = ids
        _cache["ts"] = now
    return _cache["ids"]


def reset_cache():
    _cache["ts"] = 0.0
    _cache["ids"] = set()
    _hints.clear()


def _hint_target(event):
    """Объект, которым можно ответить: сама сообщения или её callback-сообщение."""
    if hasattr(event, "answer"):
        return event
    msg = getattr(event, "message", None)
    if msg is not None and hasattr(msg, "answer"):
        return msg
    return None


class ChatGuard(BaseMiddleware):
    """Пропускает обновления из лички и разрешённых чатов, остальное — тишина."""

    async def __call__(self, handler, event, data):
        chat = _event_chat(event)
        if chat is None:
            return await handler(event, data)
        if chat.type == "private":
            return await handler(event, data)
        if chat.id in await allowed_chat_ids():
            return await handler(event, data)

        # Чужой чат: не выполняем хендлер. На команду отвечаем подсказкой (раз в час).
        if _is_command(event):
            last = _hints.get(chat.id, 0)
            if time.monotonic() - last >= HINT_INTERVAL:
                _hints[chat.id] = time.monotonic()
                target = _hint_target(event)
                if target is not None:
                    try:
                        await target.answer(HINT)
                    except Exception:
                        pass
        return None
