"""Голос Представителя — ежедневное обращение к городу.

Представитель (право can_address_city) пишет обращение в Ратуше: до
REP_SPEECH_MAX_LEN символов, не больше REP_SPEECH_PER_DAY в сутки по МСК. Текущее
обращение висит на заглавной картинке города под словами «Речь представителя», и
каждое новое обращение уходит оповещением в общий чат (тот же механизм, что у
новостей и наград). Опубликованное обращение можно править — правка не тратит
суточный лимит, но помечается.
"""

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import REP_SPEECH_MAX_LEN, REP_SPEECH_PER_DAY
from database.db import (
    add_rep_speech, update_rep_speech, get_latest_rep_speech, get_rep_speech,
    count_rep_speeches_today, log_activity,
)
from utils.helpers import is_main_menu_text, edit_message_safe
from utils.permissions import has_permission
from utils.notify import notify
from keyboards.keyboards import cancel_keyboard

router = Router()


class RepSpeech(StatesGroup):
    waiting_text = State()


def _footer(count_today: int) -> str:
    """Строка суточного лимита обращений."""
    left = max(0, REP_SPEECH_PER_DAY - count_today)
    if left == 0:
        return f"⛔ Сегодня все {REP_SPEECH_PER_DAY} обращения уже опубликованы. Новое — завтра."
    return f"📢 Сегодня можно опубликовать ещё {left} из {REP_SPEECH_PER_DAY}."


def speech_caption(speech, count_today: int = 0, is_speaker: bool = False) -> str:
    """Текст обращения для Ратуши: само обращение + кто и когда."""
    if not speech:
        base = "📢 РЕЧЬ ПРЕДСТАВИТЕЛЯ\n\nПредставитель ещё не обращался к городу."
    else:
        edited = " · ✏️ правлено" if speech['edited'] else ""
        when = (speech['created_at'] or '')[:10]
        base = (f"📢 РЕЧЬ ПРЕДСТАВИТЕЛЯ\n\n{speech['text']}\n\n"
                f"— Представитель · {when}{edited}")
    if is_speaker:
        base += f"\n\n{_footer(count_today)}"
    return base


async def _render_speech(callback: CallbackQuery, state: FSMContext, speech, is_speaker: bool,
                         cnt: int):
    buttons = []
    if is_speaker:
        buttons.append([InlineKeyboardButton(
            text="✏️ Изменить обращение", callback_data="rep:speech:edit")])
        buttons.append([InlineKeyboardButton(
            text="📢 Новое обращение", callback_data="rep:speech:write")])
    buttons.append([InlineKeyboardButton(text="🔙 В Ратушу", callback_data="city:pilots")])
    try:
        await state.clear()
    except Exception:
        pass
    await edit_message_safe(
        callback.message,
        speech_caption(speech, cnt, is_speaker),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )


@router.callback_query(F.data == "rep:speech")
async def rep_speech_open(callback: CallbackQuery, state: FSMContext):
    """Карточка «Обращение Представителя» в Ратуше. Писать может представитель
    (can_address_city), читать — любой, кто дошёл до Ратуши."""
    await callback.answer()
    uid = callback.from_user.id
    is_speaker = await has_permission(uid, "can_address_city")
    speech = await get_latest_rep_speech()
    cnt = await count_rep_speeches_today(uid) if is_speaker else 0
    await _render_speech(callback, state, speech, is_speaker, cnt)


@router.callback_query(F.data == "rep:speech:write")
async def rep_speech_write(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    uid = callback.from_user.id
    if not await has_permission(uid, "can_address_city"):
        await callback.message.answer("⛔ Обращаться к городу может только Представитель.")
        return
    cnt = await count_rep_speeches_today(uid)
    if cnt >= REP_SPEECH_PER_DAY:
        await callback.message.answer(f"❌ {_footer(cnt)}")
        return
    await state.set_state(RepSpeech.waiting_text)
    await callback.message.answer(
        f"📢 Напиши обращение к городу (до {REP_SPEECH_MAX_LEN} символов).\n"
        f"Оно появится на заглавной картинке города и в общем чате.\n\n{_footer(cnt)}",
        reply_markup=cancel_keyboard()
    )


@router.callback_query(F.data == "rep:speech:edit")
async def rep_speech_edit(callback: CallbackQuery, state: FSMContext):
    """Правка текущего обращения. Не тратит суточный лимит: правится уже
    опубликованное, а новое обращение не создаётся."""
    await callback.answer()
    uid = callback.from_user.id
    if not await has_permission(uid, "can_address_city"):
        await callback.message.answer("⛔ Обращаться к городу может только Представитель.")
        return
    speech = await get_latest_rep_speech()
    if not speech:
        await callback.message.answer("❌ Пока нечего править — опубликуй обращение.")
        return
    if speech['user_id'] != uid:
        await callback.message.answer("⛔ Править можно только своё обращение.")
        return
    await state.update_data(rep_edit_id=speech['id'])
    await state.set_state(RepSpeech.waiting_text)
    await callback.message.answer(
        f"✏️ Пришли исправленный текст обращения (до {REP_SPEECH_MAX_LEN} символов).\n"
        f"Сейчас:\n\n{speech['text']}",
        reply_markup=cancel_keyboard()
    )


def _validate(text: str) -> str | None:
    """Проверка текста обращения. Возвращает текст ошибки или None."""
    if not text:
        return "❌ Пустое обращение — напиши что-нибудь."
    if len(text) > REP_SPEECH_MAX_LEN:
        return (f"❌ Слишком длинно: {len(text)} символов, "
                f"а лимит {REP_SPEECH_MAX_LEN}. Сократи и пришли снова.")
    return None


async def _publish(bot: Bot, message: Message, state: FSMContext, text: str):
    """Публикация нового обращения: запись, показ и оповещение в общий чат."""
    uid = message.from_user.id
    speech_id = await add_rep_speech(uid, text)
    await state.clear()
    cnt = await count_rep_speeches_today(uid)
    await message.answer(
        f"✅ Обращение опубликовано!\n\n{speech_caption(await get_rep_speech(speech_id), cnt, True)}\n\n"
        f"Оно на заглавной картинке города и в общем чате.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✏️ Изменить обращение", callback_data="rep:speech:edit")],
            [InlineKeyboardButton(text="🔙 В Ратушу", callback_data="city:pilots")],
        ])
    )
    # Оповещение городу: обращение целиком, одним сообщением в общий чат.
    # user_id не передаём — это не личное событие игрока, а голос города, и
    # отписка от личных оповещений его не должна скрывать.
    await notify(bot, f"📢 РЕЧЬ ПРЕДСТАВИТЕЛЯ\n\n{text}")
    await log_activity(uid, "rep_speech", text[:60])


@router.message(RepSpeech.waiting_text, F.text, ~F.text.func(is_main_menu_text))
async def rep_speech_text(message: Message, state: FSMContext, bot: Bot):
    uid = message.from_user.id
    text = message.text.strip()
    err = _validate(text)
    if err:
        await message.answer(err)
        return
    data = await state.get_data()
    edit_id = data.get('rep_edit_id')
    if edit_id:
        speech = await get_rep_speech(edit_id)
        if not speech or speech['user_id'] != uid:
            await state.clear()
            await message.answer("❌ Нечего править. Опубликуй новое обращение.")
            return
        await update_rep_speech(edit_id, text)
        await state.clear()
        await message.answer(
            f"✏️ Обращение исправлено.\n\n{speech_caption(await get_rep_speech(edit_id), 0, True)}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 В Ратушу", callback_data="city:pilots")],
            ])
        )
        await notify(message.bot, f"📢 РЕЧЬ ПРЕДСТАВИТЕЛЯ (исправлено)\n\n{text}")
        await log_activity(uid, "rep_speech_edit", text[:60])
        return
    await _publish(message.bot, message, state, text)
