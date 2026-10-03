from aiogram import Router, F
from aiogram.types import (Message, CallbackQuery, ContentType,
                           InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.db import (
    get_user, update_user, get_user_statuses, get_selected_status, set_selected_status,
    user_has_status_tag, user_is_tourist, get_equipment, get_item, get_equipment_slot_items, get_user_awards,
    set_callsign, set_callsign_free_used, get_callsign_free_used, get_db,
)
from keyboards.keyboards import profile_keyboard, cancel_keyboard, main_menu_kb
from config import get_rank, get_effective_rank, get_next_rank, get_rank_index, RANKS, CALLSIGN_PRICE

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
    waiting_callsign = State()


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
        xp = user['xp_balance'] if 'xp_balance' in user.keys() and user['xp_balance'] else 0
        caption += f"⭐ Звание: {rank}\n"
        caption += f"💂 Войска (опыт звания): {user['troops']}\n"
        caption += f"✨ Опыт (накопительный): {xp}\n"
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
            reply_markup=profile_keyboard(notify, public, can_toggle, has_callsign=bool(user.get('callsign') and str(user.get('callsign')).strip()))
        )
    else:
        await out.answer(caption, reply_markup=profile_keyboard(notify, public, can_toggle, has_callsign=bool(user.get('callsign') and str(user.get('callsign')).strip())))


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


@router.callback_query(F.data == "profile")
async def profile_back(callback: CallbackQuery, state: FSMContext):
    """Кнопка «Отмена» и возврат в профиль из вложенных экранов."""
    await state.set_state(None)
    await callback.answer()
    await render_profile(callback.message, callback.from_user.id)


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
    # status_id приходит из callback_data, то есть от клиента, поэтому сверяем его
    # с реально выданными: иначе нажатие на устаревшую или подделанную кнопку
    # молча сбрасывало бы выбор (все is_selected → 0, а выбрать нечего), и игрок
    # получал «✅ Статус обновлён» вместо правды.
    if not any(s['id'] == status_id for s in await get_user_statuses(callback.from_user.id)):
        await callback.message.answer("❌ Этот статус тебе не выдан.")
        return
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
    if is_pilot:
        xp = user['xp_balance'] if 'xp_balance' in user.keys() and user['xp_balance'] else 0
        troops_line = f"Войска (опыт звания): {user['troops']}\n" f"Опыт (накопительный): {xp}\n"
    else:
        troops_line = ""

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

    await callback.message.answer(card, reply_markup=profile_keyboard(
        notify_enabled=bool(user.get('notify_enabled', 1)),
        profile_public=bool(user.get('profile_public', 1)),
        can_toggle_visibility=await user_has_status_tag(callback.from_user.id, "ace"),
        has_callsign=bool(user.get('callsign') and str(user.get('callsign')).strip()),
    ))


def _award_perks(a) -> list:
    """Человеческий список бонусов награды (строки «⚔️ +10%» и т.п.)."""
    perks = []
    if a['bonus_attack']:
        perks.append(f"⚔️ +{a['bonus_attack']}% атака")
    if a['bonus_defense']:
        perks.append(f"🛡 +{a['bonus_defense']}% защита")
    if a['bonus_dodge']:
        perks.append(f"💨 +{a['bonus_dodge']}% уклонение")
    if a['bonus_fishing']:
        perks.append(f"🎣 +{a['bonus_fishing']}% рыбалка")
    if a['bonus_hp']:
        perks.append(f"❤️ +{a['bonus_hp']} HP")
    if a['bonus_crit']:
        perks.append(f"💥 +{a['bonus_crit']}% крит")
    if a['bonus_shop_discount']:
        perks.append(f"💰 −{a['bonus_shop_discount']}% в магазине")
    if a['bonus_report_tax']:
        perks.append(f"🧾 налог −{a['bonus_report_tax']} п.п.")
    return perks


@router.callback_query(F.data == "profile:awards")
async def profile_awards(callback: CallbackQuery):
    """Список наград пилота: по каждой — кнопка перехода к карточке награды."""
    await callback.answer()
    awards = await get_user_awards(callback.from_user.id)
    if not awards:
        await callback.message.answer(
            "🎖️ У тебя пока нет наград.\n\n"
            "Награды выдаются админами за особые заслуги.",
            reply_markup=profile_keyboard()
        )
        return

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    lines = ["🎖️ ТВОИ НАГРАДЫ:\n"]
    rows = []
    for a in awards:
        emoji = a['emoji'] or '🏅'
        lines.append(f"{emoji} {a['name']}")
        rows.append([InlineKeyboardButton(
            text=f"{emoji} {a['name']}",
            callback_data=f"profile:award:{a['grant_id']}")])
    lines.append("\nНажми на награду, чтобы открыть её.")
    rows.append([InlineKeyboardButton(text="🏠 В профиль", callback_data="profile:open")])
    await callback.message.answer(
        "\n".join(lines),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows)
    )


@router.callback_query(F.data.startswith("profile:award:"))
async def profile_award_detail(callback: CallbackQuery):
    """Карточка награды: описание, бонусы, дата получения, картинка."""
    await callback.answer()
    try:
        grant_id = int(callback.data.split(":", 2)[2])
    except (ValueError, IndexError):
        return
    awards = await get_user_awards(callback.from_user.id)
    a = next((x for x in awards if x['grant_id'] == grant_id), None)
    if not a:
        await callback.message.answer("❌ Награда не найдена.")
        return

    emoji = a['emoji'] or '🏅'
    text = f"{emoji} {a['name']}\n────────────────\n"
    perks = _award_perks(a)
    if a['description']:
        text += f"\n{a['description']}\n"
    if perks:
        text += f"\nБонусы: {'; '.join(perks)}\n"
    text += f"\n📅 Получена: {a['granted_at']}"
    if a['comment']:
        text += f"\n💬 {a['comment']}"

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 К списку наград", callback_data="profile:awards")],
        [InlineKeyboardButton(text="🏠 В профиль", callback_data="profile:open")],
    ])
    if a['image']:
        try:
            await callback.message.answer_photo(a['image'], caption=text, reply_markup=markup)
            return
        except Exception:
            pass
    await callback.message.answer(text, reply_markup=markup)


@router.callback_query(F.data == "profile:open")
async def profile_open_cb(callback: CallbackQuery):
    """Возврат в профиль из вложенных меню."""
    await callback.answer()
    await render_profile(callback, callback.from_user.id)


@router.callback_query(F.data == "profile:callsign")
async def profile_callsign(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    await callback.answer()
    user = await get_user(user_id)
    has_callsign = bool(user and user.get('callsign') and str(user.get('callsign')).strip())
    free_used = await get_callsign_free_used(user_id)
    super_admin = await user_has_status_tag(user_id, "super_admin")

    kb_cancel = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Отмена", callback_data="profile")]])

    # Позывной ещё не установлен и бесплатная установка не использована.
    if not has_callsign and not free_used:
        await state.set_state(ProfileStates.waiting_callsign)
        await callback.message.answer(
            "Установить позывной\n\n"
            "Позывной — твой игровой ник, он виден в карточке пилота.\n"
            "Первая установка — один раз бесплатно.\n\n"
            "Введи желаемый позывной:",
            reply_markup=kb_cancel)
        return

    # Позывной есть, но игрок — суперадмин: смена бесплатная.
    if has_callsign and super_admin:
        await state.set_state(ProfileStates.waiting_callsign)
        await callback.message.answer(
            "Смена позывного\n\n"
            "У тебя уже есть позывной. По правам суперадмина смена — бесплатная.\n\n"
            "Введи новый позывной:",
            reply_markup=kb_cancel)
        return

    # Позывной есть и игрок не суперадмин: смена платная.
    if has_callsign:
        text = (
            "Смена позывного — платная\n\n"
            f"Стоимость: {CALLSIGN_PRICE} НМ\n"
            "Текущий позывной заменится новым.\n\n"
            "Оплатить и сменить?"
        )
    else:
        text = (
            "Смена позывного\n\n"
            f"Бесплатная установка уже использована. Смена стоит {CALLSIGN_PRICE} НМ.\n\n"
            "Оплатить и сменить?"
        )
    await callback.message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"Оплатить {CALLSIGN_PRICE} НМ",
                              callback_data="profile:callsign_buy")],
        [InlineKeyboardButton(text="Отмена", callback_data="profile")],
    ]))


@router.callback_query(F.data == "profile:callsign_cancel")
async def profile_callsign_cancel(callback: CallbackQuery, state: FSMContext):
    await state.set_state(None)
    await callback.answer("Отменено")
    await render_profile(callback.message, callback.from_user.id)


@router.message(ProfileStates.waiting_callsign)
async def profile_callsign_input(message: Message, state: FSMContext):
    user_id = message.from_user.id
    callsign = (message.text or "").strip()

    if len(callsign) > 32:
        await message.answer("Позывной не должен превышать 32 символа. Попробуй ещё раз:")
        return

    if len(callsign) < 2:
        await message.answer("Позывной должен быть не короче 2 символов. Попробуй ещё раз:")
        return

    user = await get_user(user_id)
    has_callsign = bool(user and user.get('callsign') and str(user.get('callsign')).strip())
    free_used = await get_callsign_free_used(user_id)
    super_admin = await user_has_status_tag(user_id, "super_admin")

    if not has_callsign and not free_used:
        await set_callsign(user_id, callsign)
        await set_callsign_free_used(user_id, 1)
        await state.finish()
        await message.answer(f"Позывной «{callsign}» установлен!")
        await render_profile(message, user_id)
        return

    if super_admin:
        await set_callsign(user_id, callsign)
        await state.finish()
        await message.answer(f"Позывной изменён на «{callsign}» (бесплатно, по правам суперадмина)")
        await render_profile(message, user_id)
        return

    # Бесплатная установка уже была — ввод без оплаты не принимаем.
    await state.set_state(None)
    await message.answer(
        f"Бесплатная установка уже использована — смена стоит {CALLSIGN_PRICE} НМ.\n\n"
        "Вернись в профиль и нажми «Сменить позывной», чтобы оплатить смену."
    )
    await render_profile(message, user_id)


@router.callback_query(F.data == "profile:callsign_buy")
async def profile_callsign_buy(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user = await get_user(user_id)
    if not user:
        await callback.answer("Сначала нажми /start", show_alert=True)
        return
    if user['nordmarks'] < CALLSIGN_PRICE:
        await callback.answer(f"❌ Недостаточно. Нужно {CALLSIGN_PRICE} НМ", show_alert=True)
        return

    from database.db import transfer_nordmarks, add_transaction
    await transfer_nordmarks(user_id, 0, CALLSIGN_PRICE, "callsign_change")
    await add_transaction(user_id, "callsign_change", -CALLSIGN_PRICE, "Смена позывного")

    # Позывной сбрасываем, чтобы ввод нового прошёл как первая установка.
    await set_callsign(user_id, None)
    await state.set_state(ProfileStates.waiting_callsign)
    await callback.answer(f"✅ Списано {CALLSIGN_PRICE} НМ")
    await callback.message.answer(
        f"Оплачено {CALLSIGN_PRICE} НМ.\nВведи новый позывной:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Отмена", callback_data="profile:callsign_cancel")],
        ]))
