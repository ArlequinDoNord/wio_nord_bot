"""Партии и кланы: реестр из Ратуши.

Создание, редактирование (название/описание/картинка), назначение главы и прямое
добавление членов — только суперадмин (can_manage_clans). Глава (роль clan_leader)
управляет только своим объединением: принимает/отклоняет заявки, исключает членов,
шлёт сообщения членам. Обычный пилот подаёт заявку кнопкой «Вступить» на карточке.

Пилот может состоять одновременно в одном клане И в одной партии (kind).
"""

import os

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.db import (
    get_user, get_all_users, get_clan, get_clans, create_clan, update_clan,
    delete_clan, get_clan_members, get_clan_member_ids, get_clan_pending_requests,
    is_clan_member, add_clan_member, remove_clan_member, get_user_clan,
    is_clan_leader, add_clan_request, remove_clan_request, has_clan_request,
    add_user_role, remove_user_role, log_location_visit,
    KIND_LABELS,
)
from utils.permissions import has_permission, log_action
from utils.notify import player_display

router = Router()

PAGE_SIZE = 10

KIND_EMOJI = {"clan": "🏰", "party": "🏛"}


class ClansCreate(StatesGroup):
    kind = State()
    wait_name = State()
    wait_desc = State()


class ClansEdit(StatesGroup):
    field = State()
    wait_value = State()


class ClansMessage(StatesGroup):
    wait_text = State()


def _type_label(clan) -> str:
    kind = clan.get('kind') if hasattr(clan, 'get') else 'clan'
    return KIND_LABELS.get(kind, kind)


def _redraw(callback: CallbackQuery, text: str, kb: InlineKeyboardMarkup, photo=None):
    """Перерисовка сообщения (учёт photo-каталога и медиа-сообщений)."""
    if photo:
        if callback.message.photo:
            from aiogram.types import InputMediaPhoto
            media = photo if isinstance(photo, str) else photo
            return callback.message.edit_media(
                media=InputMediaPhoto(media=media, caption=text, parse_mode="HTML"),
                reply_markup=kb,
            )
        return callback.message.answer_photo(photo=photo, caption=text,
                                             parse_mode="HTML", reply_markup=kb)
    if callback.message.photo:
        return callback.message.edit_caption(caption=text, parse_mode="HTML", reply_markup=kb)
    return callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)


async def _send_ok(uid: int, bot, text: str) -> bool:
    try:
        await bot.send_message(uid, text)
        return True
    except Exception:
        return False


# ----- Список кланов и партий -----

@router.callback_query(F.data == "city:clans")
async def clans_list_cb(callback: CallbackQuery):
    await callback.answer()
    from database.db import can_enter_location
    if not await can_enter_location(callback.from_user.id, "townhall"):
        await callback.message.answer("🍺 Ты пьян! В Ратушу не пускают. Протрезвей сначала.")
        return
    await log_location_visit(callback.from_user.id, "townhall")
    await _show_clans_list(callback)


async def _show_clans_list(callback: CallbackQuery):
    clans = await get_clans()
    lines = ["⚜️ ПАРТИИ И КЛАНЫ\n"]
    clans_kb = []
    by_kind = {"clan": [], "party": []}
    for c in clans:
        kind = c['kind']
        if kind in by_kind:
            by_kind[kind].append(c)
    for kind in ("clan", "party"):
        label = KIND_LABELS.get(kind, kind)
        items = by_kind[kind]
        if not items:
            lines.append(f"{KIND_EMOJI[kind]} {label.title()}ы: пока пусто")
        else:
            lines.append(f"{KIND_EMOJI[kind]} {label.title()}ы:")
        for c in items:
            members = len(await get_clan_member_ids(c['id']))
            leader = ""
            if c['leader_id']:
                lu = await get_user(c['leader_id'])
                leader = f" — 👑 {await player_display(lu)}" if lu else ""
            lines.append(f"  • {c['name']} ({members}){leader}")
            clans_kb.append([InlineKeyboardButton(
                text=f"{KIND_EMOJI[kind]} {c['name']} ({members})",
                callback_data=f"clans:view:{c['id']}")])
    if await has_permission(callback.from_user.id, "can_manage_clans"):
        clans_kb.append([
            InlineKeyboardButton(text="🏰 Создать клан", callback_data="clans:create:clan"),
            InlineKeyboardButton(text="🏛 Создать партию", callback_data="clans:create:party"),
        ])
    clans_kb.append([InlineKeyboardButton(text="🔙 В Ратушу", callback_data="city:pilots")])
    await _redraw(callback, "\n".join(lines), InlineKeyboardMarkup(inline_keyboard=clans_kb))


# ----- Карточка объединения -----

@router.callback_query(F.data.startswith("clans:view:"))
async def clan_view_cb(callback: CallbackQuery):
    await callback.answer()
    clan = await get_clan(int(callback.data.split(":")[2]))
    if not clan:
        await callback.message.answer("❌ Объединение не найдено.")
        return
    uid = callback.from_user.id
    members = await get_clan_member_ids(clan['id'])
    lines = [
        f"{KIND_EMOJI.get(clan['kind'], '📌')} {_type_label(clan).title()} «{clan['name']}»\n",
        f"👥 Членов: {len(members)}",
    ]
    if clan['leader_id']:
        lu = await get_user(clan['leader_id'])
        lines.append(f"👑 Глава: {await player_display(lu) if lu else '#' + str(clan['leader_id'])}")
    desc = (clan.get('description') or '').strip()
    if desc:
        lines.append(f"📖 {desc}")

    can_admin = await has_permission(uid, "can_manage_clans")
    is_leader = clan['leader_id'] == uid
    is_member = uid in members

    lines.append("\nСостав:")
    m_users = await get_clan_members(clan['id'])
    if not m_users:
        lines.append("  — пока никого —")
    else:
        for i, mu in enumerate(m_users[:15], 1):
            tag = " 👑" if mu['user_id'] == clan['leader_id'] else ""
            lines.append(f"  {i}. {await player_display(mu)}{tag}")
        if len(m_users) > 15:
            lines.append(f"  … и ещё {len(m_users) - 15}")

    kb = []
    if is_member:
        if not is_leader:
            kb.append([InlineKeyboardButton(text="🚪 Выйти", callback_data=f"clans:leave:{clan['id']}")])
        else:
            kb.append([InlineKeyboardButton(text="⚙️ Управление", callback_data=f"clans:manage:{clan['id']}")])
    else:
        if await has_clan_request(clan['id'], uid):
            kb.append([InlineKeyboardButton(text="⏳ Заявка отправлена — отозвать", callback_data=f"clans:cancel:{clan['id']}")])
        else:
            kb.append([InlineKeyboardButton(text="📨 Вступить", callback_data=f"clans:join:{clan['id']}")])
    if is_leader or can_admin:
        kb.append([InlineKeyboardButton(text="⚙️ Управление", callback_data=f"clans:manage:{clan['id']}")])
    kb.append([InlineKeyboardButton(text="🔙 К списку", callback_data="city:clans")])
    await _redraw(callback, "\n".join(lines), InlineKeyboardMarkup(inline_keyboard=kb),
                  photo=clan.get('photo_file_id'))


# ----- Заявка на вступление / выход -----

@router.callback_query(F.data.startswith("clans:join:"))
async def clan_join_cb(callback: CallbackQuery):
    await callback.answer()
    clan = await get_clan(int(callback.data.split(":")[2]))
    if not clan:
        await callback.message.answer("❌ Объединение не найдено.")
        return
    uid = callback.from_user.id
    if await is_clan_member(clan['id'], uid):
        await callback.message.answer("ℹ️ Ты уже состоишь в этом объединении.")
        return
    existing = await get_user_clan(uid, clan['kind'])
    if existing:
        await callback.message.answer(
            f"ℹ️ Ты уже состоишь в {_type_label(existing)} «{existing['name']}». "
            f"Выйди, чтобы подать заявку в другое.")
        return
    await add_clan_request(clan['id'], uid)
    msg = f"📨 Заявка на вступление в {_type_label(clan)} «{clan['name']}» отправлена главе."
    await _send_ok(uid, callback.bot, msg)
    if clan['leader_id']:
        leader_lines = [
            f"📨 Новая заявка на вступление!\n",
            f"{KIND_EMOJI.get(clan['kind'], '📌')} {_type_label(clan).title()} «{clan['name']}»\n",
            f"Пилот: {await player_display(await get_user(uid))}",
        ]
        kbb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Принять", callback_data=f"clans:reqok:{clan['id']}:{uid}"),
             InlineKeyboardButton(text="❌ Отклонить", callback_data=f"clans:reqno:{clan['id']}:{uid}")],
        ])
        try:
            await callback.bot.send_message(clan['leader_id'], "\n".join(leader_lines), reply_markup=kbb)
        except Exception:
            pass
    await _show_clans_list(callback)


@router.callback_query(F.data.startswith("clans:cancel:"))
async def clan_join_cancel_cb(callback: CallbackQuery):
    await callback.answer()
    clan = await get_clan(int(callback.data.split(":")[2]))
    if not clan:
        return
    await remove_clan_request(clan['id'], callback.from_user.id)
    await _show_clans_list(callback)


@router.callback_query(F.data.startswith("clans:leave:"))
async def clan_leave_cb(callback: CallbackQuery):
    await callback.answer()
    clan = await get_clan(int(callback.data.split(":")[2]))
    if not clan:
        return
    uid = callback.from_user.id
    if clan['leader_id'] == uid:
        await callback.message.answer(
            "❌ Ты глава. Выйти из объединения нельзя — пусть суперадмин передаст руководство "
            "другому пилоту («Назначить главу»), и тогда ты сможешь выйти.")
        return
    await remove_clan_member(clan['id'], uid)
    await callback.message.answer(f"🚪 Ты вышел из {_type_label(clan)} «{clan['name']}».")
    await _show_clans_list(callback)


# ----- Принять / отклонить заявку -----

async def _can_manage(callback: CallbackQuery, clan) -> bool:
    if not clan:
        return False
    if await has_permission(callback.from_user.id, "can_manage_clans"):
        return True
    return clan['leader_id'] == callback.from_user.id


@router.callback_query(F.data.startswith("clans:reqok:"))
async def clan_request_ok_cb(callback: CallbackQuery):
    await callback.answer()
    parts = callback.data.split(":")
    clan = await get_clan(int(parts[2]))
    uid = int(parts[3])
    if not await _can_manage(callback, clan):
        await callback.message.answer("❌ Это может сделать только глава или суперадмин.")
        return
    target_kind = clan['kind']
    existing = await get_user_clan(uid, target_kind)
    if existing and existing['id'] != clan['id']:
        await callback.message.answer(
            f"ℹ️ Пилот уже состоит в {_type_label(existing)} «{existing['name']}» — заявка отклонена.")
        await remove_clan_request(clan['id'], uid)
        return
    await add_clan_member(clan['id'], uid)
    await log_action(callback.from_user.id, 'clan_accept_request',
                     uid, f"clan_id={clan['id']}")
    await _send_ok(uid, callback.bot,
                   f"✅ Твою заявку приняли! Ты вступил в {_type_label(clan)} «{clan['name']}».")
    await _show_clans_list(callback)


@router.callback_query(F.data.startswith("clans:reqno:"))
async def clan_request_no_cb(callback: CallbackQuery):
    await callback.answer()
    parts = callback.data.split(":")
    clan = await get_clan(int(parts[2]))
    uid = int(parts[3])
    if not await _can_manage(callback, clan):
        await callback.message.answer("❌ Это может сделать только глава или суперадмин.")
        return
    await remove_clan_request(clan['id'], uid)
    await _send_ok(uid, callback.bot,
                   f"❌ Твою заявку в {_type_label(clan)} «{clan['name']}» отклонили.")
    await _show_clans_list(callback)


# ----- Управление (глава / суперадмин) -----

@router.callback_query(F.data.startswith("clans:manage:"))
async def clan_manage_cb(callback: CallbackQuery):
    await callback.answer()
    clan = await get_clan(int(callback.data.split(":")[2]))
    if not await _can_manage(callback, clan):
        await callback.message.answer("❌ Это может сделать только глава или суперадмин.")
        return
    await _show_manage(callback, clan)


async def _show_manage(callback: CallbackQuery, clan):
    uid = callback.from_user.id
    can_admin = await has_permission(uid, "can_manage_clans")
    members = await get_clan_members(clan['id'])
    requests = await get_clan_pending_requests(clan['id'])

    lines = [f"⚙️ УПРАВЛЕНИЕ — {_type_label(clan).title()} «{clan['name']}»\n"]
    lines.append(f"👥 Члены ({len(members)}):")
    for mu in members:
        tag = " 👑" if mu['user_id'] == clan['leader_id'] else ""
        lines.append(f"  • {await player_display(mu)}{tag}")
    if not members:
        lines.append("  — пока никого —")
    if requests:
        lines.append(f"\n📨 Заявки ({len(requests)}):")
        for ru in requests:
            lines.append(f"  • {await player_display(ru)}")

    kb = []
    for ru in requests:
        kb.append([InlineKeyboardButton(
            text=f"✅ {await player_display(ru)}",
            callback_data=f"clans:reqok:{clan['id']}:{ru['user_id']}")])
        kb.append([InlineKeyboardButton(
            text=f"❌ Отклонить: {await player_display(ru)}",
            callback_data=f"clans:reqno:{clan['id']}:{ru['user_id']}")])
    for mu in members:
        if mu['user_id'] == clan['leader_id']:
            continue
        kb.append([InlineKeyboardButton(
            text=f"🚫 Исключить: {await player_display(mu)}",
            callback_data=f"clans:kick:{clan['id']}:{mu['user_id']}")])
    kb.append([InlineKeyboardButton(text="📢 Сообщение членам", callback_data=f"clans:msg:{clan['id']}")])
    if can_admin:
        kb.append([InlineKeyboardButton(text="📨 Добавить члена", callback_data=f"clans:add:{clan['id']}:0")])
        kb.append([InlineKeyboardButton(text="👑 Назначить главу", callback_data=f"clans:leader:{clan['id']}:0")])
        if clan['leader_id']:
            kb.append([InlineKeyboardButton(text="👑 Снять главу", callback_data=f"clans:leaderunset:{clan['id']}")])
        kb.append([InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"clans:edit:{clan['id']}")])
        kb.append([InlineKeyboardButton(text="🗑 Удалить объединение", callback_data=f"clans:del:{clan['id']}")])
    kb.append([InlineKeyboardButton(text="🔙 К карточке", callback_data=f"clans:view:{clan['id']}")])
    await _redraw(callback, "\n".join(lines), InlineKeyboardMarkup(inline_keyboard=kb))


# ----- Исключение члена -----

@router.callback_query(F.data.startswith("clans:kick:"))
async def clan_kick_cb(callback: CallbackQuery):
    await callback.answer()
    parts = callback.data.split(":")
    clan = await get_clan(int(parts[2]))
    uid = int(parts[3])
    if not await _can_manage(callback, clan):
        await callback.message.answer("❌ Это может сделать только глава или суперадмин.")
        return
    if clan['leader_id'] == uid:
        await callback.message.answer("❌ Нельзя исключить главу через эту кнопку — сначала «Снять главу».")
        return
    await remove_clan_member(clan['id'], uid)
    await log_action(callback.from_user.id, 'clan_kick', uid, f"clan_id={clan['id']}")
    await _send_ok(uid, callback.bot,
                   f"🚫 Тебя исключили из {_type_label(clan)} «{clan['name']}».")
    await _show_manage(callback, clan)


# ----- Пикер пилотов (добавление / глава) -----

async def _pilot_picker(callback: CallbackQuery, clan, page: int, assign_prefix: str,
                        page_base: str, caption: str):
    users = sorted(await get_all_users(), key=lambda u: u['user_id'])
    total = len(users)
    pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    page = max(0, min(page, pages - 1))
    chunk = users[page * PAGE_SIZE:(page + 1) * PAGE_SIZE]
    rows = []
    for u in chunk:
        rows.append([InlineKeyboardButton(
            text=await player_display(u),
            callback_data=f"{assign_prefix}:{clan['id']}:{u['user_id']}")])
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="⬅️", callback_data=f"{page_base}{page - 1}"))
    nav.append(InlineKeyboardButton(text=f"{page + 1}/{pages}", callback_data="clans:noop"))
    if page < pages - 1:
        nav.append(InlineKeyboardButton(text="➡️", callback_data=f"{page_base}{page + 1}"))
    if nav:
        rows.append(nav)
    rows.append([InlineKeyboardButton(text="🔙 Назад", callback_data=f"clans:manage:{clan['id']}")])
    await _redraw(callback, f"{caption} ({total} всего):", InlineKeyboardMarkup(inline_keyboard=rows))


@router.callback_query(F.data == "clans:noop")
async def clans_noop(callback: CallbackQuery):
    await callback.answer()


@router.callback_query(F.data.startswith("clans:add:"))
async def clan_add_pick_cb(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_clans"):
        return
    parts = callback.data.split(":")
    clan = await get_clan(int(parts[2]))
    if not clan:
        return
    try:
        page = int(parts[3]) if len(parts) >= 4 else 0
    except ValueError:
        page = 0
    await _pilot_picker(callback, clan, page, "clans:addset", f"clans:add:{clan['id']}:",
                        "📨 Выбери пилота для добавления")


@router.callback_query(F.data.startswith("clans:addset:"))
async def clan_add_set_cb(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_clans"):
        return
    parts = callback.data.split(":")
    clan = await get_clan(int(parts[2]))
    uid = int(parts[3])
    if not clan:
        return
    existing = await get_user_clan(uid, clan['kind'])
    if existing and existing['id'] != clan['id']:
        await callback.message.answer(
            f"ℹ️ Пилот уже состоит в {_type_label(existing)} «{existing['name']}».")
        return
    await add_clan_member(clan['id'], uid)
    await remove_clan_request(clan['id'], uid)
    await log_action(callback.from_user.id, 'clan_add_member', uid, f"clan_id={clan['id']}")
    u = await get_user(uid)
    await callback.message.answer(
        f"✅ {await player_display(u) if u else uid} добавлен в {_type_label(clan)} «{clan['name']}».")
    await _show_manage(callback, clan)


@router.callback_query(F.data.startswith("clans:leader:"))
async def clan_leader_pick_cb(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_clans"):
        return
    parts = callback.data.split(":")
    clan = await get_clan(int(parts[2]))
    if not clan:
        return
    try:
        page = int(parts[3]) if len(parts) >= 4 else 0
    except ValueError:
        page = 0
    await _pilot_picker(callback, clan, page, "clans:leaderset", f"clans:leader:{clan['id']}:",
                        "👑 Выбери нового главу")


@router.callback_query(F.data.startswith("clans:leaderset:"))
async def clan_leader_set_cb(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_clans"):
        return
    parts = callback.data.split(":")
    clan = await get_clan(int(parts[2]))
    uid = int(parts[3])
    if not clan:
        return
    old_leader = clan['leader_id']
    if old_leader and old_leader != uid:
        await remove_user_role(old_leader, 'clan_leader')
    await remove_clan_request(clan['id'], uid)
    await add_clan_member(clan['id'], uid)
    await update_clan(clan['id'], leader_id=uid)
    await add_user_role(uid, 'clan_leader', granted_by=callback.from_user.id)
    await log_action(callback.from_user.id, 'clan_set_leader', uid, f"clan_id={clan['id']}")
    u = await get_user(uid)
    await callback.message.answer(
        f"👑 Глава {_type_label(clan)} «{clan['name']}» — {await player_display(u) if u else uid}.")
    await _show_manage(callback, clan)


@router.callback_query(F.data.startswith("clans:leaderunset:"))
async def clan_leader_unset_cb(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_clans"):
        return
    parts = callback.data.split(":")
    clan = await get_clan(int(parts[2]))
    if not clan:
        return
    old = clan['leader_id']
    if not old:
        await callback.message.answer("ℹ️ У объединения уже нет главы.")
        return
    await update_clan(clan['id'], leader_id=None)
    await remove_user_role(old, 'clan_leader')
    await log_action(callback.from_user.id, 'clan_unset_leader', old, f"clan_id={clan['id']}")
    await callback.message.answer(f"👑 Глава снят с {_type_label(clan)} «{clan['name']}».")
    await _show_manage(callback, clan)


# ----- Создание (суперадмин) -----

@router.callback_query(F.data.startswith("clans:create:"))
async def clan_create_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_clans"):
        await callback.message.answer("❌ Создавать может только суперадмин.")
        return
    kind = callback.data.split(":")[2]
    if kind not in ("clan", "party"):
        return
    await state.update_data(clans_kind=kind)
    await state.set_state(ClansCreate.wait_name)
    await callback.message.answer(
        f"{KIND_EMOJI[kind]} Создание {KIND_LABELS[kind]}а.\n\nВведи название:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data="city:clans")]]))


@router.message(ClansCreate.wait_name)
async def clan_create_name(message: Message, state: FSMContext):
    name = (message.text or "").strip()
    if not name or len(name) > 60:
        await message.answer("❌ Название не может быть пустым и не длиннее 60 символов:")
        return
    data = await state.get_data()
    await state.update_data(clans_name=name)
    await state.set_state(ClansCreate.wait_desc)
    await message.answer(
        f"📖 Описание для «{name}» (или «-» — без описания):",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data="city:clans")]]))


@router.message(ClansCreate.wait_desc)
async def clan_create_desc(message: Message, state: FSMContext):
    desc = (message.text or "").strip()
    if desc == "-":
        desc = ""
    data = await state.get_data()
    kind = data.get('clans_kind', 'clan')
    name = data.get('clans_name', 'Без названия')
    if desc and len(desc) > 500:
        await message.answer("❌ Описание не длиннее 500 символов:")
        return
    clan_id = await create_clan(kind, name, desc, message.from_user.id)
    await log_action(message.from_user.id, 'clan_create', clan_id, f"kind={kind}, name={name}")
    await state.clear()
    await message.answer(
        f"✅ {KIND_EMOJI[kind]} {KIND_LABELS[kind].title()} «{name}» создан!\n"
        f"Дальше: назначь главу и добавь первых членов.")


# ----- Редактирование (суперадмин) -----

@router.callback_query(F.data.startswith("clans:edit:"))
async def clan_edit_menu_cb(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_clans"):
        return
    clan = await get_clan(int(callback.data.split(":")[2]))
    if not clan:
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Название", callback_data=f"clans:editf:{clan['id']}:name")],
        [InlineKeyboardButton(text="📖 Описание", callback_data=f"clans:editf:{clan['id']}:desc")],
        [InlineKeyboardButton(text="🖼 Картинка", callback_data=f"clans:editf:{clan['id']}:photo")],
        [InlineKeyboardButton(text="❌ Убрать картинку", callback_data=f"clans:editf:{clan['id']}:nophoto")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data=f"clans:manage:{clan['id']}")],
    ])
    await _redraw(callback, f"✏️ ЧТО ПРАВИМ В «{clan['name']}»?", kb, photo=clan.get('photo_file_id'))


@router.callback_query(F.data.startswith("clans:editf:"))
async def clan_edit_field_cb(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_clans"):
        return
    parts = callback.data.split(":")
    clan_id = int(parts[2])
    field = parts[3]
    if field == "nophoto":
        await update_clan(clan_id, photo_file_id=None)
        await callback.message.answer("✅ Картинка убрана.")
        clan = await get_clan(clan_id)
        await _redraw(callback, f"✏️ ЧТО ПРАВИМ В «{clan['name']}»?", InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✏️ Название", callback_data=f"clans:editf:{clan_id}:name")],
            [InlineKeyboardButton(text="📖 Описание", callback_data=f"clans:editf:{clan_id}:desc")],
            [InlineKeyboardButton(text="🖼 Картинка", callback_data=f"clans:editf:{clan_id}:photo")],
            [InlineKeyboardButton(text="❌ Убрать картинку", callback_data=f"clans:editf:{clan_id}:nophoto")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data=f"clans:manage:{clan_id}")],
        ]))
        return
    await state.update_data(clans_clan_id=clan_id, clans_field=field)
    await state.set_state(ClansEdit.wait_value)
    labels = {"name": "название", "desc": "описание", "photo": "картинка (пришли фото)"}
    await callback.message.answer(f"Введи новое {labels.get(field, field)}:")


@router.message(ClansEdit.wait_value, F.photo)
async def clan_edit_finish_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    clan_id = int(data.get('clans_clan_id') or 0)
    clan = await get_clan(clan_id)
    if not clan:
        await state.clear()
        return
    await update_clan(clan_id, photo_file_id=message.photo[-1].file_id)
    await log_action(message.from_user.id, 'clan_edit_photo', clan_id)
    await state.clear()
    await message.answer(f"✅ Картинка «{clan['name']}» обновлена.")


@router.message(ClansEdit.wait_value)
async def clan_edit_finish_text(message: Message, state: FSMContext):
    data = await state.get_data()
    clan_id = int(data.get('clans_clan_id') or 0)
    field = data.get('clans_field')
    clan = await get_clan(clan_id)
    if not clan:
        await state.clear()
        return
    value = (message.text or "").strip()
    if field == 'photo':
        await message.answer("❌ Для картинки пришли фото сообщением.")
        return
    if field == 'name':
        if not value or len(value) > 60:
            await message.answer("❌ Название не длиннее 60 символов:")
            return
        await update_clan(clan_id, name=value)
    elif field == 'desc':
        if len(value) > 500:
            await message.answer("❌ Описание не длиннее 500 символов:")
            return
        await update_clan(clan_id, description=value)
    await log_action(message.from_user.id, f'clan_edit_{field}', clan_id)
    await state.clear()
    await message.answer(f"✅ {field.title()} обновлено.")


# ----- Сообщение членам -----

@router.callback_query(F.data.startswith("clans:msg:"))
async def clan_msg_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    clan = await get_clan(int(callback.data.split(":")[2]))
    if not await _can_manage(callback, clan):
        await callback.message.answer("❌ Это может сделать только глава или суперадмин.")
        return
    await state.update_data(clans_msg_id=clan['id'])
    await state.set_state(ClansMessage.wait_text)
    await callback.message.answer(
        f"📢 Сообщение членам {_type_label(clan)} «{clan['name']}».\n\nВведи текст рассылки:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data=f"clans:manage:{clan['id']}")]]))


@router.message(ClansMessage.wait_text)
async def clan_msg_send(message: Message, state: FSMContext):
    data = await state.get_data()
    clan_id = int(data.get('clans_msg_id') or 0)
    clan = await get_clan(clan_id)
    if not clan:
        await state.clear()
        return
    text = (message.text or "").strip()
    if not text:
        await message.answer("❌ Сообщение не может быть пустым:")
        return
    sender = await player_display(message.from_user)
    members = await get_clan_member_ids(clan_id)
    sent = 0
    for uid in members:
        if uid == message.from_user.id:
            continue
        if await _send_ok(uid, message.bot,
                          f"📢 Сообщение от руководства {_type_label(clan)} «{clan['name']}»:\n\n{text}\n\n— {sender}"):
            sent += 1
    await state.clear()
    await log_action(message.from_user.id, 'clan_message', clan_id,
                     f"sent={sent}, text={text[:200]}")
    noun = "пилоту" if sent == 1 else ("пилотам" if sent else "никому")
    await message.answer(f"✅ Сообщение отправлено {sent} {noun} из {len(members) - 1} членов.")


# ----- Удаление (суперадмин) -----

@router.callback_query(F.data.startswith("clans:del:"))
async def clan_delete_cb(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_clans"):
        return
    clan = await get_clan(int(callback.data.split(":")[2]))
    if not clan:
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Да, удалить", callback_data=f"clans:delyes:{clan['id']}")],
        [InlineKeyboardButton(text="↩️ Нет, отмена", callback_data=f"clans:manage:{clan['id']}")],
    ])
    await callback.message.answer(
        f"🗑 Точно удалить {_type_label(clan)} «{clan['name']}»? "
        f"Удалятся все члены и заявки.", reply_markup=kb)


@router.callback_query(F.data.startswith("clans:delyes:"))
async def clan_delete_yes_cb(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_clans"):
        return
    clan_id = int(callback.data.split(":")[2])
    clan = await get_clan(clan_id)
    if not clan:
        return
    if clan['leader_id']:
        await remove_user_role(clan['leader_id'], 'clan_leader')
    await delete_clan(clan_id)
    await log_action(callback.from_user.id, 'clan_delete', clan_id, clan['name'])
    await callback.message.answer(f"🗑 {_type_label(clan).title()} «{clan['name']}» удалён.")
    await _show_clans_list(callback)