from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ContentType
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.db import (
    get_user, update_user, get_user_statuses, get_selected_status, set_selected_status,
    user_has_status_tag, get_equipment, get_item, get_equipment_slot_items, get_user_awards,
)
from keyboards.keyboards import profile_keyboard, cancel_keyboard, main_menu_keyboard
from config import get_rank, get_effective_rank, get_next_rank, get_rank_index, RANKS

router = Router()


class ProfileStates(StatesGroup):
    waiting_photo = State()


async def selected_status_label(user_id: int) -> str:
    sel = await get_selected_status(user_id)
    return sel['name'] if sel else "—"


async def render_profile(where, user_id: int):
    out = where.message if hasattr(where, 'message') else where
    user = await get_user(user_id)
    if not user:
        await out.answer("Сначала нажми /start")
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

    status = await selected_status_label(user_id)
    notify = bool(user['notify_enabled'] if 'notify_enabled' in user.keys() else 1)
    from utils.states import get_state_info, format_state_line
    state_line = format_state_line(await get_state_info(user_id))
    eq = await get_equipment(user_id)
    eq_lines = []
    if eq.get('weapon'):
        w = await get_item(eq['weapon'])
        if w:
            eq_lines.append(f"⚔️ Оружие: {w['name']} ({w['damage']} ур.)")
    if eq.get('armor'):
        a = await get_item(eq['armor'])
        if a:
            eq_lines.append(f"🛡️ Броня: {a['name']} ({a['armor']} защ.)")

    slot_by_name = {}
    for s, r in await get_equipment_slot_items(user_id):
        slot_by_name[s] = r
    slot_labels = {'potion1': 'Слот 1', 'potion2': 'Слот 2'}
    for s in ('potion1', 'potion2'):
        if s in slot_by_name:
            r = slot_by_name[s]
            if r['cure_poison']:
                eq_lines.append(f"⚗️ {slot_labels[s]}: {r['name']}")
            else:
                eq_lines.append(f"💊 {slot_labels[s]}: {r['name']}")

    if not eq_lines:
        eq_lines.append("— пусто —")
    caption += (
        f"💰 Нордмарки: {user['nordmarks']}\n"
        f"⚡ Очки действия: {user['ap']}/{user['ap_max']}\n"
        f"❤️ Состояние: {user['state']}\n"
        + (f"{state_line}\n" if state_line else "")
        + f"🎖️ Статус: {status}\n"
        + f"🔔 Оповещения в группе: {'вкл' if notify else 'выкл'}\n\n"
        + "Экипировка:\n" + "\n".join(f"  {l}" for l in eq_lines) + "\n\n"
        + f"👇 Выберите действие:"
    )

    if photo:
        await out.answer_photo(
            photo=photo,
            caption=caption,
            reply_markup=profile_keyboard(notify)
        )
    else:
        await out.answer(caption, reply_markup=profile_keyboard(notify))


@router.message(Command("profile"))
async def profile_cmd(message: Message):
    await render_profile(message, message.from_user.id)


@router.message(F.text == "Профиль")
async def show_profile(message: Message):
    await render_profile(message, message.from_user.id)


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


@router.callback_query(F.data == "profile:notify_toggle")
async def notify_toggle(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    is_veteran = await user_has_status_tag(user_id, "veteran")
    if not is_veteran:
        await callback.message.answer(
            "🔕 Отключение оповещений доступно только со статуса «Ветеран» и выше."
        )
        return

    user = await get_user(user_id)
    current = bool(user['notify_enabled'] if 'notify_enabled' in user.keys() else 1)
    await update_user(user_id, notify_enabled=0 if current else 1)
    if current:
        await callback.message.answer("✅ Отключил оповещение о своих действиях!")
    else:
        await callback.message.answer("✅ Оповещения снова включены!")


@router.callback_query(F.data == "profile:pilot_card")
async def pilot_card(callback: CallbackQuery):
    await callback.answer()
    user = await get_user(callback.from_user.id)
    if not user:
        await callback.message.answer("Сначала нажми /start")
        return

    rank = get_effective_rank(user['troops'], user['promoted_rank'] if 'promoted_rank' in user.keys() else None)
    status = await selected_status_label(callback.from_user.id)
    from utils.states import get_state_info, format_state_line
    state_line = format_state_line(await get_state_info(callback.from_user.id))

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
        + (f"{state_line}\n" if state_line else "")
        + f"───────────────────────────\n"
        f"ФИНАНСЫ\n"
        f"Нордмарки: {user['nordmarks']}\n"
        f"Очки действия: {user['ap']}/{user['ap_max']}\n"
        f"Состояние: {user['state']}\n"
        f"═══════════════════════════\n"
        f"Выдан: {user['created_at'] if 'created_at' in user.keys() else '—'}\n"
        f"═══════════════════════════"
    )

    await callback.message.answer(card, reply_markup=profile_keyboard())


@router.callback_query(F.data == "profile:awards")
async def profile_awards(callback: CallbackQuery):
    await callback.answer()
    awards = await get_user_awards(callback.from_user.id)
    if not awards:
        await callback.message.answer(
            "🎖️ У тебя пока нет наград.\n\n"
            "Награды выдаются админами за особые заслуги.",
            reply_markup=profile_keyboard()
        )
        return

    lines = ["🎖️ ТВОИ НАГРАДЫ:\n"]
    for a in awards:
        emoji = a['emoji'] or '🏅'
        lines.append(f"{emoji} {a['name']}")
        if a['description']:
            lines.append(f"   — {a['description']}")
        lines.append(f"   📅 {a['granted_at']}")
        if a['comment']:
            lines.append(f"   💬 {a['comment']}")
        lines.append("")
    await callback.message.answer(
        "\n".join(lines),
        reply_markup=profile_keyboard()
    )
