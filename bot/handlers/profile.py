from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ContentType
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.db import (
    get_user, update_user, get_user_statuses, get_selected_status, set_selected_status,
)
from keyboards.keyboards import profile_keyboard, cancel_keyboard, main_menu_keyboard
from config import get_rank, get_effective_rank, get_next_rank, get_rank_index, RANKS

router = Router()


class ProfileStates(StatesGroup):
    waiting_photo = State()


async def selected_status_label(user_id: int) -> str:
    sel = await get_selected_status(user_id)
    return sel['name'] if sel else "—"


@router.message(F.text == "Профиль")
async def show_profile(message: Message):
    user = await get_user(message.from_user.id)
    if not user:
        await message.answer("Сначала нажми /start")
        return

    rank = get_effective_rank(user['troops'], user['promoted_rank'] if 'promoted_rank' in user.keys() else None)
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

    status = await selected_status_label(message.from_user.id)
    caption += (
        f"💰 Нордмарки: {user['nordmarks']}\n"
        f"⚡ Очки действия: {user['ap']}/{user['ap_max']}\n"
        f"❤️ Состояние: {user['state']}\n"
        f"🎖️ Статус: {status}\n\n"
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


@router.callback_query(F.data == "profile:choose_status")
async def choose_status(callback: CallbackQuery):
    await callback.answer()
    statuses = await get_user_statuses(callback.from_user.id)
    if not statuses:
        await callback.message.answer(
            "🎖️ У тебя пока нет статусов. Их выдают админы (например, МВД за заслуги)."
        )
        return

    rows = []
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    for s in statuses:
        mark = "✅ " if s['is_selected'] else ""
        rows.append([InlineKeyboardButton(
            text=f"{mark}{s['name']}",
            callback_data=f"prof_sel_status:{s['id']}"
        )])
    rows.append([InlineKeyboardButton(text="🔙 В профиль", callback_data="prof:back")])
    await callback.message.answer(
        "🎖️ Выбери, какой статус отображать в профиле:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows)
    )


@router.callback_query(F.data.startswith("prof_sel_status:"))
async def select_status_cb(callback: CallbackQuery):
    await callback.answer()
    status_id = int(callback.data.split(":")[1])
    await set_selected_status(callback.from_user.id, status_id)
    await callback.message.answer("✅ Статус обновлён в профиле!")


@router.callback_query(F.data == "prof:back")
async def prof_back(callback: CallbackQuery):
    await callback.answer()
    await callback.message.delete()
    await callback.message.answer("👇 Нажми «Профиль» в меню, чтобы открыть профиль.")


@router.callback_query(F.data == "profile:pilot_card")
async def pilot_card(callback: CallbackQuery):
    await callback.answer()
    user = await get_user(callback.from_user.id)
    if not user:
        await callback.message.answer("Сначала нажми /start")
        return

    rank = get_effective_rank(user['troops'], user['promoted_rank'] if 'promoted_rank' in user.keys() else None)
    status = await selected_status_label(callback.from_user.id)

    card = (
        f"═══════════════════════════\n"
        f"      🪖 КАРТОЧКА ПИЛОТА 🪖\n"
        f"═══════════════════════════\n\n"
        f"ШТАБНОЙ ОТДЕЛ НОРДХАЙМА\n"
        f"───────────────────────────\n"
        f"Имя: {user['first_name']} {user['last_name'] or ''}\n"
        f"Позывной: @{user['username']}\n"
        f"Звание: {rank}\n"
        f"───────────────────────────\n"
        f"БОЕВАЯ СТАТИСТИКА\n"
        f"Войска: {user['troops']}\n"
        f"Статус: {status}\n"
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
