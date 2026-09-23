from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ContentType
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.db import (
    get_user, update_user, get_user_statuses, get_selected_status, set_selected_status,
    user_has_status_tag, user_is_tourist, get_equipment, get_item, get_equipment_slot_items, get_user_awards,
)
from keyboards.keyboards import profile_keyboard, cancel_keyboard, main_menu_kb
from config import get_rank, get_effective_rank, get_next_rank, get_rank_index, RANKS

router = Router()


def _callsign(user) -> str:
    """Позывной пилота: введённый админом, иначе @username, иначе «—»."""
    if user.get('callsign'):
        return user['callsign']
    username = user.get('username')
    return f"@{username}" if username else "—"


def _pilot_name(user) -> str:
    """Имя пилота: @username, иначе позывной, иначе реальное имя."""
    username = (user.get('username') or '').strip()
    if username:
        return f"@{username}"
    if user.get('callsign'):
        return user['callsign']
    first = (user.get('first_name') or '').strip()
    last = (user.get('last_name') or '').strip()
    return (f"{first} {last}").strip() or "—"


class ProfileStates(StatesGroup):
    waiting_photo = State()
    waiting_about = State()


async def selected_status_label(user_id: int) -> str:
    sel = await get_selected_status(user_id)
    return sel['name'] if sel else "—"


async def _profile_caption(user_id: int, owner: bool = True):
    """Подпись профиля. owner=True — полный вид для владельца (с оповещениями и действием)."""
    user = await get_user(user_id)
    if not user:
        return None, None

    rank = get_effective_rank(user['troops'], user['promoted_rank'] if 'promoted_rank' in user.keys() else None)
    next_rank, next_troops = get_next_rank(user['troops'])
    is_pilot = not await user_is_tourist(user_id)

    photo = user['photo_file_id']

    caption = (
        f"🪪 Пилот: {_pilot_name(user)}\n"
        f"📡 Позывной: {_callsign(user)}\n"
    )
    if is_pilot:
        caption += f"⭐ Звание: {rank}\n"
        caption += f"💂 Войска: {user['troops']}\n"
        from utils.wings import wing_display
        caption += f"🪽 Авиакрыло: {wing_display(user.get('wing'))}\n"

    if is_pilot and user['troops'] < RANKS[-1][1]:
        current_idx = get_rank_index(user['troops'])
        current_min = RANKS[current_idx][1]
        needed = next_troops - current_min
        done = user['troops'] - current_min
        bar_len = 10
        filled = int(done / needed * bar_len) if needed > 0 else bar_len
        caption += f"До звания «{next_rank}»: [{'█' * filled}{'░' * (bar_len - filled)}] {done}/{needed}\n"

    status = await selected_status_label(user_id)
    notify = bool(user['notify_enabled'] if 'notify_enabled' in user.keys() else 1)
    public = bool(user['profile_public'] if 'profile_public' in user.keys() else 1)
    from utils.states import get_state_info, format_state_line
    state_line = format_state_line(await get_state_info(user_id))
    eq = await get_equipment(user_id)
    eq_lines = []
    if eq.get('weapon'):
        w = await get_item(eq['weapon'])
        if w:
            eq_lines.append(f"⚔️ Оружие: {w['name']} ({w['damage']} ур.)")
    armor_parts = [('head', 'Голова'), ('body', 'Тело'), ('hands', 'Руки'), ('legs', 'Ноги')]
    for slot, label in armor_parts:
        aid = eq.get(slot)
        if aid:
            a = await get_item(aid)
            if a:
                eq_lines.append(f"{label}: {a['name']} ({a['armor']} защ.)")

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
        + (f"{state_line}\n" if state_line else "❤️ Состояние: нормально\n")
        + f"🎖️ Статус: {status}\n"
    )
    from database.db import get_user_clan
    clan = await get_user_clan(user_id, 'clan')
    party = await get_user_clan(user_id, 'party')
    caption += f"🏰 Клан: {clan['name'] if clan else '—'}\n"
    caption += f"🏛 Партия: {party['name'] if party else '—'}\n"
    about = (user.get('about') or '').strip()
    if about:
        caption += f"📖 О себе: {about}\n"
    if owner:
        caption += f"🔔 Оповещения в группе: {'вкл' if notify else 'выкл'}\n"
        if await user_has_status_tag(user_id, "ace"):
            caption += f"👁 Профиль виден другим: {'да' if public else 'нет'}\n"
    caption += (
        "\nЭкипировка:\n" + "\n".join(f"  {l}" for l in eq_lines) + "\n\n"
    )
    if owner:
        caption += "👇 Выберите действие:"
    return caption, photo


async def render_profile(where, user_id: int):
    out = where.message if hasattr(where, 'message') else where
    caption, photo = await _profile_caption(user_id, owner=True)
    if caption is None:
        await out.answer("Сначала нажми /start")
        return

    user = await get_user(user_id)
    notify = bool(user['notify_enabled'] if 'notify_enabled' in user.keys() else 1)
    public = bool(user['profile_public'] if 'profile_public' in user.keys() else 1)
    can_toggle = await user_has_status_tag(user_id, "ace")

    if photo:
        await out.answer_photo(
            photo=photo,
            caption=caption,
            reply_markup=profile_keyboard(notify, public, can_toggle)
        )
    else:
        await out.answer(caption, reply_markup=profile_keyboard(notify, public, can_toggle))


async def render_other_profile(where, user_id: int):
    """Публичный профиль пилота при просмотре из Ратуши.

    Сторонний наблюдатель видит только: фотокарточку, имя и позывной, звание,
    статус и «О себе». Без войск, финансов, экипировки и состояния.
    """
    out = where.message if hasattr(where, 'message') else where
    user = await get_user(user_id)
    if not user:
        await out.answer("❌ Пилот не найден.")
        return

    name = _pilot_name(user)
    rank = get_effective_rank(user['troops'], user['promoted_rank'] if 'promoted_rank' in user.keys() else None)
    status = await selected_status_label(user_id)
    about = (user.get('about') or '').strip()

    caption = (
        f"🪪 Пилот: {name}\n"
        f"📡 Позывной: {_callsign(user)}\n"
        f"⭐ Звание: {rank}\n"
        f"🎖️ Статус: {status}\n"
    )
    if about:
        caption += f"\n📖 О себе: {about}\n"

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 К карточке пилота", callback_data=f"rathaus:{user_id}")]
    ])
    photo = user['photo_file_id'] if 'photo_file_id' in user.keys() else None
    if photo:
        await out.answer_photo(photo=photo, caption=caption, reply_markup=markup)
    else:
        await out.answer(caption, reply_markup=markup)


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
        reply_markup=await main_menu_kb(message.from_user.id)
    )


@router.callback_query(F.data == "profile:edit_about")
async def edit_about(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(ProfileStates.waiting_about)
    await callback.message.answer(
        "📖 Напиши «о себе» — до 70 символов. Нажми «Отмена», если передумаешь:",
        reply_markup=cancel_keyboard()
    )


@router.message(ProfileStates.waiting_about, F.text)
async def process_about(message: Message, state: FSMContext):
    text = message.text.strip()
    if text.lower() in ("/cancel", "отмена"):
        await state.clear()
        await message.answer("Отменено.", reply_markup=await main_menu_kb(message.from_user.id))
        return
    if len(text) > 70:
        await message.answer(
            f"❌ Слишком длинно — максимум 70 символов (сейчас {len(text)}). Напиши короче:"
        )
        return
    if text in ("-", "Пропустить"):
        text = ""
    await update_user(message.from_user.id, about=text)
    await state.clear()
    await message.answer("✅ «О себе» сохранено!", reply_markup=await main_menu_kb(message.from_user.id))


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


@router.callback_query(F.data == "profile:public_toggle")
async def public_toggle(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    is_vip = await user_has_status_tag(user_id, "ace")
    if not is_vip:
        await callback.message.answer(
            "👁 Переключение видимости профиля доступно только со статуса «Ас»."
        )
        return

    user = await get_user(user_id)
    current = bool(user['profile_public'] if 'profile_public' in user.keys() else 1)
    await update_user(user_id, profile_public=0 if current else 1)
    if current:
        await callback.message.answer("🔒 Профиль скрыт от других пилотов!")
    else:
        await callback.message.answer("👁 Профиль снова виден всем!")


@router.callback_query(F.data == "profile:pilot_card")
async def pilot_card(callback: CallbackQuery):
    await callback.answer()
    user = await get_user(callback.from_user.id)
    if not user:
        await callback.message.answer("Сначала нажми /start")
        return

    rank = get_effective_rank(user['troops'], user['promoted_rank'] if 'promoted_rank' in user.keys() else None)
    is_pilot = not await user_is_tourist(callback.from_user.id)
    status = await selected_status_label(callback.from_user.id)
    from utils.states import get_state_info, format_state_line
    state_line = format_state_line(await get_state_info(callback.from_user.id))

    rank_line = f"Звание: {rank}\n" if is_pilot else ""
    troops_line = f"Войска: {user['troops']}\n" if is_pilot else ""

    card = (
        f"═══════════════════════════\n"
        f"      🪖 КАРТОЧКА ПИЛОТА 🪖\n"
        f"═══════════════════════════\n\n"
        f"ШТАБНОЙ ОТДЕЛ НОРДХАЙМА\n"
        f"───────────────────────────\n"
        f"Имя: {_pilot_name(user)}\n"
        f"📡 Позывной: {_callsign(user)}\n"
        + rank_line
        + f"───────────────────────────\n"
        f"БОЕВАЯ СТАТИСТИКА\n"
        + troops_line
        + f"Статус: {status}\n"
        + (f"{state_line}\n" if state_line else "")
        + f"───────────────────────────\n"
        f"ФИНАНСЫ\n"
        f"Нордмарки: {user['nordmarks']}\n"
        f"Очки действия: {user['ap']}/{user['ap_max']}\n"
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
