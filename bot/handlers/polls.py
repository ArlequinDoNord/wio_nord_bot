"""Голосование: показ активных опросов, участие в них и создание новых (суперадмин)."""

from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.db import (
    get_active_polls, get_poll, get_poll_results, get_poll_vote_option,
    user_voted, vote_poll, create_poll, close_poll, user_has_status_tag,
)
from config import ADMIN_IDS

router = Router()


class PollCreate(StatesGroup):
    question = State()
    options = State()


async def _require_pilot(callback: CallbackQuery) -> bool:
    if await user_has_status_tag(callback.from_user.id, "pilot"):
        return True
    await callback.answer("⛔ Голосовать могут только пилоты.", show_alert=True)
    return False


@router.callback_query(F.data == "city:vote")
async def vote_menu(callback: CallbackQuery):
    await callback.answer()
    if not await _require_pilot(callback):
        return
    polls = await get_active_polls()

    buttons = []
    for p in polls:
        question = p['question']
        short = question if len(question) <= 40 else question[:37] + "…"
        buttons.append([InlineKeyboardButton(text=f"🗳️ {short}", callback_data=f"vote:show:{p['id']}")])

    if callback.from_user.id in ADMIN_IDS:
        buttons.append([InlineKeyboardButton(text="➕ Создать опрос", callback_data="vote:create")])

    buttons.append([InlineKeyboardButton(text="🔙 В город", callback_data="city:menu")])

    if polls:
        text = "🗳️ ГОЛОСОВАНИЕ\n\nАктивные опросы — выбери, чтобы проголосовать:"
    else:
        text = "🗳️ ГОЛОСОВАНИЕ\n\nСейчас нет активных опросов."

    if callback.message.photo:
        await callback.message.edit_caption(caption=text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    else:
        await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))


@router.callback_query(F.data.startswith("vote:show:"))
async def vote_show(callback: CallbackQuery):
    await callback.answer()
    if not await _require_pilot(callback):
        return
    poll_id = int(callback.data.split(":")[2])
    poll = await get_poll(poll_id)
    if not poll or not poll['is_active']:
        await callback.message.answer("❌ Опрос не найден или закрыт.")
        return

    options = [o for o in poll['options'].split("\n") if o.strip()]
    already = await user_voted(poll_id, callback.from_user.id)

    buttons = []
    for i, option in enumerate(options):
        prefix = ""
        if already:
            my = await get_poll_vote_option(poll_id, callback.from_user.id)
            prefix = "✅ " if my == i else "🔘 "
        buttons.append([InlineKeyboardButton(
            text=f"{prefix}{option}",
            callback_data=f"vote:cast:{poll_id}:{i}"
        )])

    if not already:
        buttons.append([InlineKeyboardButton(text="🔙 К опросам", callback_data="city:vote")])
    else:
        buttons.append([InlineKeyboardButton(text="📊 Результаты", callback_data=f"vote:results:{poll_id}")])
        buttons.append([InlineKeyboardButton(text="🔙 К опросам", callback_data="city:vote")])

    text = (
        f"🗳️ {poll['question']}\n\n"
        + ("Выбери вариант:" if not already else "Ты уже проголосовал. Варианты:")
    )
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))


@router.callback_query(F.data.startswith("vote:cast:"))
async def vote_cast(callback: CallbackQuery):
    await callback.answer()
    if not await _require_pilot(callback):
        return
    parts = callback.data.split(":")
    poll_id, option_index = int(parts[2]), int(parts[3])
    poll = await get_poll(poll_id)
    if not poll or not poll['is_active']:
        await callback.message.answer("❌ Опрос не найден или закрыт.")
        return

    ok = await vote_poll(poll_id, callback.from_user.id, option_index)
    if not ok:
        await callback.message.answer("⚠️ Ты уже голосовал в этом опросе.")
        return

    await callback.message.answer("✅ Голос учтён!")
    await callback.answer()
    await vote_show(callback)


@router.callback_query(F.data.startswith("vote:results:"))
async def vote_results(callback: CallbackQuery):
    await callback.answer()
    poll_id = int(callback.data.split(":")[2])
    poll = await get_poll(poll_id)
    if not poll:
        await callback.message.answer("❌ Опрос не найден.")
        return

    options = [o for o in poll['options'].split("\n") if o.strip()]
    results = await get_poll_results(poll_id)
    counts = {r['option_index']: r['cnt'] for r in results}
    total = sum(counts.values())

    lines = []
    for i, option in enumerate(options):
        cnt = counts.get(i, 0)
        pct = round(cnt / total * 100) if total else 0
        bar = "█" * (pct // 10) + "░" * (10 - pct // 10) if total else "░" * 10
        lines.append(f"{option}\n  {bar} {cnt} ({pct}%)")

    text = (
        f"📊 РЕЗУЛЬТАТЫ\n"
        f"🗳️ {poll['question']}\n\n"
        f"Всего голосов: {total}\n\n" + "\n".join(lines)
    )
    buttons = [[InlineKeyboardButton(text="🔙 К опросам", callback_data="city:vote")]]
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))


@router.callback_query(F.data == "vote:create")
async def vote_create(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if callback.from_user.id not in ADMIN_IDS:
        await callback.message.answer("⛔ У тебя нет прав создавать опросы.")
        return
    await state.set_state(PollCreate.question)
    await callback.message.answer(
        "📝 Введи вопрос для опроса (например: «Какой новый данж хотите?»)\n"
        "Отмена — /cancel"
    )


@router.message(PollCreate.question, F.text)
async def poll_question_handler(message, state: FSMContext):
    await state.update_data(question=message.text.strip())
    await state.set_state(PollCreate.options)
    await message.answer(
        "📝 Теперь введи варианты ответов, каждый с новой строки (от 2 до 10):"
    )


@router.message(PollCreate.options, F.text)
async def poll_options_handler(message, state: FSMContext):
    options = [o.strip() for o in message.text.split("\n") if o.strip()]
    if len(options) < 2 or len(options) > 10:
        await message.answer("⚠️ Нужно от 2 до 10 вариантов. Попробуй ещё раз:")
        return

    data = await state.get_data()
    poll_id = await create_poll(message.from_user.id, data['question'], "\n".join(options))
    await state.clear()
    await message.answer(
        f"✅ Опрос создан!\n\n🗳️ {data['question']}\n\n{chr(10).join(f'{i+1}. {o}' for i, o in enumerate(options))}"
    )


@router.callback_query(F.data == "vote:close")
async def vote_close(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("Закрытие опросов планируется позже. Нажми «Создать опрос», если нужно новое голосование.")