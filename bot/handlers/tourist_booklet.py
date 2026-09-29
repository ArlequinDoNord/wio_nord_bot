"""Буклет туриста: чек-лист городских локаций и разовая награда.

Купить («Буклет туриста», категория сувениров, 1 НМ) можно любому игроку — и
туристу, и гражданину. Просмотр превью локации (location:preview) отмечает её в
буклете; собрав все 9, игрок получает значок «Опытный турист» и 20 НМ один раз.
"""

from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from database.db import (
    get_booklet_visits, is_booklet_claimed, get_locations_by_keys,
    claim_booklet_reward,
)
from config import (
    TOURIST_BOOKLET_NAME, TOURIST_BOOKLET_AWARD, TOURIST_BOOKLET_AWARD_EMOJI,
    TOURIST_BOOKLET_LOCATIONS, TOURIST_BOOKLET_REWARD_NM,
)
from utils.helpers import edit_or_replace

router = Router()


async def _booklet_payload(user_id: int) -> str:
    """Текст буклета: список локаций с галочками и счётчик."""
    visits = await get_booklet_visits(user_id)
    claimed = await is_booklet_claimed(user_id)
    names = await get_locations_by_keys(TOURIST_BOOKLET_LOCATIONS)

    lines = [f"🧭 {TOURIST_BOOKLET_NAME}", ""]
    if claimed:
        lines.append("Награда за путешествие по Нордхайму уже получена 🎉")
        lines.append("")
    lines.append("Просматривай превью городских локаций (через «🏙 Город») — "
                 "и они будут отмечаться здесь:")
    lines.append("")
    for key in TOURIST_BOOKLET_LOCATIONS:
        name = names.get(key) or key
        mark = "✅" if key in visits else "⬜"
        lines.append(f"{mark} {name}")
    lines.append("")
    lines.append(f"Отмечено: {len(visits)} из {len(TOURIST_BOOKLET_LOCATIONS)}")
    return "\n".join(lines)


async def show_booklet_menu(obj, user_id: int):
    """Показывает панель буклета (новое сообщение или правка существующего)."""
    text = await _booklet_payload(user_id)
    claimed = await is_booklet_claimed(user_id)
    rows = []
    if not claimed:
        rows.append([InlineKeyboardButton(
            text=f"🎁 Получить награду: значок «{TOURIST_BOOKLET_AWARD}» + "
                 f"{TOURIST_BOOKLET_REWARD_NM} НМ",
            callback_data="booklet:claim")])
    rows.append([InlineKeyboardButton(text="🏙 В город", callback_data="city:menu")])
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    try:
        await edit_or_replace(obj, text, markup)
    except Exception:
        # Несколько асинхронных открытий подряд — уже заменено, молчим.
        pass


@router.callback_query(F.data == "booklet:menu")
async def booklet_menu_cb(callback: CallbackQuery):
    await callback.answer()
    await show_booklet_menu(callback.message, callback.from_user.id)


@router.callback_query(F.data == "booklet:claim")
async def booklet_claim_cb(callback: CallbackQuery):
    await callback.answer()
    ok, msg = await claim_booklet_reward(callback.from_user.id)
    if not ok:
        await callback.answer(f"❌ {msg}", show_alert=True)
        return
    await callback.message.answer(f"✅ {msg}")
    await show_booklet_menu(callback.message, callback.from_user.id)