"""Команда /changelog — «что нового» в боте.

Релизное оповещение в общем чате короткое (версия + суть), а за подробностями
пилоты приходят сюда: конфиг держит заметки текущего и предыдущего релиза —
ровно два блока, без простыни из трёх-четырёх сборок.

Отдельный модуль, а не start.py: там smoke_093 запрещает полный текст заметок
и PREV_VERSION в приветствии (там остаётся тизер первой фразы).
"""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from config import VERSION, VERSION_NOTES, PREV_VERSION, PREV_VERSION_NOTES

router = Router()


@router.message(Command("changelog"))
async def cmd_changelog(message: Message):
    notes = " ".join(str(VERSION_NOTES or "").split())
    prev = " ".join(str(PREV_VERSION_NOTES or "").split())
    text = (
        "📄 ЧТО НОВОГО В Н.О.Р.Д.\n\n"
        f"▶️ Сборка v{VERSION}:\n{notes}\n\n"
        f"▫️ Предыдущая сборка v{PREV_VERSION}:\n{prev}"
    )
    await message.answer(text)
