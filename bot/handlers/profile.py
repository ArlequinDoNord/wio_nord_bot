from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ContentType
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.db import get_user, update_user
from keyboards.keyboards import profile_keyboard, cancel_keyboard, main_menu_keyboard
from config import get_rank, get_next_rank, get_rank_index, RANKS

router = Router()


class ProfileStates(StatesGroup):
    waiting_photo = State()
    waiting_status = State()


@router.message(F.text == "Профиль")
async def show_profile(message: Message):
    user = await get_user(message.from_user.id)
    if not user:
        await message.answer("Сначала нажми /start")
        return

    rank = get_rank(user['troops'])
    next_rank, next_troops = get_next_rank(user['troops'])

    photo = user['photo_file_id']

    caption = (
        f"🪪 Пилот: {user['first_name']} {user['last_name'] or ''}\n"
        f"Позывной: @{user['username']}\n"
        f"⭐ Звание: {rank}\n"
        f"💂 Войска: {user['troops']}\n"
    )

    if user['troops'] < RANKS[-1][1]:
        current_idx = get_rank_index(user['troops'])
        current_min = RANKS[current_idx][1]
        needed = next_troops - current_min
        done = user['troops'] - current_min
        bar_len = 10
        filled = int(done / needed * bar_len) if needed > 0 else bar_len
        caption += f"До звания «{next_rank}»: [{'█' * filled}{'░' * (bar_len - filled)}] {done}/{needed}\n"

    caption += (
        f"💰 Нордмарки: {user['nordmarks']}\n"
        f"⚡ Очки действия: {user['ap']}/{user['ap_max']}\n"
        f"❤️ Состояние: {user['state']}\n"
        f"📝 Статус: {user['status_text']}\n\n"
        f"👇 Выберите действие:"
    )

    if photo:
        await message.answer_photo(
            photo=photo,
            caption=caption,
            reply_markup=profile_keyboard()
        )
    else:
        await message.answer(caption, reply_markup=profile_keyboard())


@router.callback_query(F.data == "profile:set_photo")
async def set_photo(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(ProfileStates.waiting_photo)
    await callback.message.answer(
        "📸 Отправь новое фото. Нажми «Отмена» если передумаешь:",
        reply_markup=cancel_keyboard()
    )


@router.message(ProfileStates.waiting_photo, F.content_type == ContentType.PHOTO)
async def process_photo(message: Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    await update_user(message.from_user.id, photo_file_id=photo_id)
    await state.clear()
    await message.answer(
        "✅ Фото профиля обновлено!",
        reply_markup=main_menu_keyboard()
    )


@router.callback_query(F.data == "profile:set_status")
async def set_status(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(ProfileStates.waiting_status)
    await callback.message.answer(
        "📝 Напиши новый статус (например: «В бою», «На задании», «Отдыхаю»):",
        reply_markup=cancel_keyboard()
    )


@router.message(ProfileStates.waiting_status)
async def process_status(message: Message, state: FSMContext):
    if message.content_type != ContentType.TEXT:
        await message.answer("Отправь текстовое сообщение")
        return
    status_text = message.text.strip()
    if len(status_text) > 60:
        await message.answer("Статус слишком длинный (макс. 60 символов)")
        return
    await update_user(message.from_user.id, status_text=status_text)
    await state.clear()
    await message.answer(
        "✅ Статус обновлён!",
        reply_markup=main_menu_keyboard()
    )


@router.callback_query(F.data == "profile:pilot_card")
async def pilot_card(callback: CallbackQuery):
    await callback.answer()
    user = await get_user(callback.from_user.id)
    if not user:
        await callback.message.answer("Сначала нажми /start")
        return

    rank = get_rank(user['troops'])

    card = (
        f"═══════════════════════════\n"
        f"      🪖 КАРТОЧКА ПИЛОТА 🪖\n"
        f"═══════════════════════════\n\n"
        f"ШТАБНОЙ ОТДЕЛ НОРДМАРКА\n"
        f"───────────────────────────\n"
        f"Имя: {user['first_name']} {user['last_name'] or ''}\n"
        f"Позывной: @{user['username']}\n"
        f"Звание: {rank}\n"
        f"───────────────────────────\n"
        f"БОЕВАЯ СТАТИСТИКА\n"
        f"Войска: {user['troops']}\n"
        f"Статус: {user['status_text']}\n"
        f"───────────────────────────\n"
        f"ФИНАНСЫ\n"
        f"Нордмарки: {user['nordmarks']}\n"
        f"Очки действия: {user['ap']}/{user['ap_max']}\n"
        f"Состояние: {user['state']}\n"
        f"═══════════════════════════\n"
        f"Выдан: {user['created_at'] if 'created_at' in user.keys() else '—'}\n"
        f"═══════════════════════════"
    )

    await callback.message.answer(card, reply_markup=profile_keyboard())
