"""
Админ-панель: управление магазином, финансами, отчётами, ролями и логами.
Доступ разграничен по ролям (см. utils/permissions.py).
"""

import json

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.db import (
    add_item, delete_item, update_item, get_available_items, get_all_items,
    get_item, get_all_users, get_pending_reports, approve_report,
    reject_report, add_nordmarks, remove_nordmarks, add_ap, remove_ap,
    create_status, delete_status, get_all_statuses, get_status,
    grant_status, revoke_status, get_user_statuses,
    get_users_for_rank_promotion, promote_user_rank, get_user,
    recompute_region_stats, get_region_stats,
    get_daily_spent, add_daily_spent,
    get_treasury_balance, transfer_from_treasury, get_treasury_stats,
    get_report_tax_percent, set_report_tax_percent,
    get_sale_tax_percent, set_sale_tax_percent,
    get_special_dept_code, set_special_dept_code,
    get_salaried_users, get_user_salary, set_user_salary, pay_salaries,
    get_treasury_debts,
    get_all_locations, get_location, create_location, update_location_access,
    update_location_content, update_location_photos, location_access_label,
    get_all_dungeons, get_dungeon, update_dungeon_photos, DUNGEON_PHOTO_KEYS,
    get_dungeon_enemies, get_enemy, update_enemy_fields,
    get_enemy_drops, set_enemy_drops, add_enemy_drop, remove_enemy_drop,
    get_item_by_name,
    create_award, get_all_awards, get_award, delete_award, grant_award,
    update_award, get_user_awards, revoke_award,
    get_water_fish_rows, get_water_fish_row, update_water_fish_field,
    set_water_fish_sell_price, add_water_fish, remove_water_fish,
    get_water_fish_candidates, WATER_LABELS, set_callsign, set_wing,
    get_water_junk_rows, update_water_junk, JUNK_EMOJI,
    log_activity, get_user_activity, clear_user_photo,
    get_recent_activity, get_activity_like,
)
from keyboards.keyboards import cancel_keyboard
from utils.permissions import (
    is_admin, has_permission, get_user_role,
    add_role, remove_role, ROLES, role_label, log_action,
)
from utils.helpers import plural_nordmark
from config import RARITY_LEVELS, RARITY_EMOJI, ITEM_CATEGORIES, get_effective_rank, VERSION, DRINK_EFFECT_LABELS
from utils.notify import notify, player_display, NOTIFY_REPORT_MIN_TROOPS

router = Router()


# ============ FSM-СОСТОЯНИЯ ============

class AdminAddItem(StatesGroup):
    name = State()
    desc = State()
    price = State()
    sell_price = State()
    rarity = State()
    category = State()
    drink = State()
    plant_name = State()
    stock = State()
    stats = State()
    equip_slot = State()
    weapon_effect = State()
    weapon_effect_chance = State()
    weapon_effect_dmg = State()
    producer = State()
    producer_user = State()
    market = State()
    photo = State()


class AdminSaleTax(StatesGroup):
    percent = State()


class AdminSpecialCode(StatesGroup):
    code = State()


class AdminEditItem(StatesGroup):
    item_id = State()
    field = State()
    value = State()
    photo = State()


class AdminFinance(StatesGroup):
    target = State()
    currency = State()
    amount = State()


class AdminTreasury(StatesGroup):
    amount = State()
    target = State()


class AdminStorageRestock(StatesGroup):
    # Возврат предмета из Хранилища в магазин
    amount = State()


class AdminTax(StatesGroup):
    percent = State()


class AdminRoles(StatesGroup):
    target = State()
    action = State()
    role = State()


class AdminStatuses(StatesGroup):
    name = State()
    tag = State()
    level = State()
    desc = State()
    target = State()
    grant_action = State()
    status_pick = State()
    item_pick = State()
    item_status = State()


class AdminAwards(StatesGroup):
    name = State()
    desc = State()
    emoji = State()
    target = State()
    award_pick = State()
    comment = State()
    edit_value = State()


class AdminFishing(StatesGroup):
    """Редактор пулов рыбалки по водоёмам (веса, фото, цена продажи)."""
    water = State()
    wf_id = State()
    value = State()


class AdminCallsign(StatesGroup):
    target = State()
    value = State()


class AdminWing(StatesGroup):
    target = State()
    value = State()


class AdminStates(StatesGroup):
    target = State()
    action = State()
    state_key = State()
    minutes = State()


class AdminPlayerLog(StatesGroup):
    """Ручной ввод @username/ID для просмотра лога игрока."""
    target = State()


class AdminSalary(StatesGroup):
    target = State()
    amount = State()
    period = State()


class AdminLocation(StatesGroup):
    action = State()        # create / edit
    target_id = State()     # id локации для редактирования
    key = State()
    name = State()
    set_name = State()      # редактирование названия существующей локации
    description = State()
    mode = State()
    req_status = State()
    blocking = State()
    preview = State()


class AdminDungeon(StatesGroup):
    """Редактирование подземелья: входная картинка по времени суток; правка врагов."""
    target_id = State()
    photo_tod = State()
    enemy_id = State()       # выбранный враг
    enemy_field = State()    # поле врага, которое правим
    enemy_value = State()    # ждём новое значение поля врага
    drop_chance = State()    # ждём шанс дропа (%, 1–100)
    drop_qty = State()       # ждём кол-во дропа (1 и более)
    drop_item_photo = State()  # ждём фото предмета дропа
    drop_item_desc = State()   # ждём описание предмета дропа
    drop_item_field = State()  # выбранная характеристика предмета
    drop_item_value = State()  # ждём значение характеристики предмета
    pending_enemy_id = State()  # враг, которому назначаем только что созданный предмет


# ============ УТИЛИТЫ ============

async def perm_flags(user_id: int) -> dict:
    perms = ["can_manage_shop", "can_manage_finance", "can_view_reports",
             "can_approve_reports", "can_manage_admins", "can_view_logs",
             "can_manage_statuses", "can_grant_statuses", "can_grant_troops",
             "can_manage_states", "can_manage_locations", "can_manage_salaries",
             "can_manage_awards", "can_grant_awards", "can_manage_storage",
             "can_manage_users"]
    return {p: await has_permission(user_id, p) for p in perms}


async def find_user(text: str) -> dict:
    """Найти пользователя по @username, числовому telegram_id или имени (first_name)."""
    text = text.strip().lstrip("@")
    users = await get_all_users()
    if text.isdigit():
        for u in users:
            if str(u['user_id']) == text:
                return u
    low = text.lower()
    exact = [u for u in users if u['username'] and u['username'].lower() == low]
    if exact:
        return exact[0]
    names = [u for u in users if u['first_name'] and u['first_name'].lower() == low]
    if len(names) == 1:
        return names[0]
    if len(names) > 1:
        return None  # неоднозначно — пусть уточнят
    return None


def rarity_choice_markup():
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    rows = []
    for key in RARITY_LEVELS:
        rows.append([InlineKeyboardButton(
            text=f"{RARITY_EMOJI[key]} {RARITY_LEVELS[key]}",
            callback_data=f"rar:{key}"
        )])
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def pilot_picker_markup(next_step: str):
    """Клавиатура выбора пилота из списка; next_step — куда переходить после выбора."""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    users = await get_all_users()
    rows = []
    if users:
        for u in users[:50]:
            label = u['first_name'] or u['username'] or str(u['user_id'])
            if u['username']:
                label += f" (@{u['username']})"
            rows.append([InlineKeyboardButton(
                text=label,
                callback_data=f"pickuser:{next_step}:{u['user_id']}"
            )])
    rows.append([InlineKeyboardButton(text="✍️ Ввести вручную", callback_data=f"pickuser:{next_step}:manual")])
    rows.append([InlineKeyboardButton(text="🔙 Отмена", callback_data="admin:menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


@router.callback_query(F.data.startswith("pickuser:"))
async def pickuser_cb(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    _, next_step, raw = callback.data.split(":", 2)
    if raw == "manual":
        await callback.message.answer(
            "Введи @username или числовой ID игрока:",
            reply_markup=cancel_keyboard()
        )
        return

    target = await get_user(int(raw))
    if not target:
        await callback.message.answer("❌ Игрок не найден.")
        return
    await state.update_data(target_id=target['user_id'], target_name=target['first_name'] if 'first_name' in target.keys() else '')
    await callback.message.answer(f"Игрок: {target['first_name'] if 'first_name' in target.keys() else ''} (@{target['username'] if 'username' in target.keys() else ''})")

    if next_step == "treasury_target":
        data = await state.get_data()
        amount = data['amount']
        await transfer_from_treasury(
            target['user_id'],
            amount,
            f"Выдача из казны админом #{callback.from_user.id}"
        )
        await log_action(callback.from_user.id, 'treasury', target['user_id'], f"give {amount}")
        await state.clear()
        await callback.message.answer(f"✅ Из казны выдано {amount} {plural_nordmark(amount)}.")
    elif next_step == "finance_amount":
        await state.set_state(AdminFinance.amount)
        await callback.message.answer("Введи сумму:", reply_markup=cancel_keyboard())
    elif next_step == "roles_action":
        await state.set_state(AdminRoles.action)
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        role_names = [role_label(r) for r in await get_user_role(target['user_id'])]
        await callback.message.answer(
            f"Текущие роли: {', '.join(role_names)}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Выдать роль", callback_data="rolop:add")],
                [InlineKeyboardButton(text="Снять роль", callback_data="rolop:remove")],
            ])
        )
    elif next_step == "status_pick":
        await state.set_state(AdminStatuses.status_pick)
        have = await get_user_statuses(target['user_id'])
        have_names = ", ".join(s['name'] for s in have) if have else "нет"
        statuses = await get_all_statuses()
        if not statuses:
            await callback.message.answer("❌ Сначала создай хотя бы один статус.")
            await state.clear()
            return
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        rows = []
        for s in statuses:
            rows.append([InlineKeyboardButton(text=f"{s['name']}", callback_data=f"st_pick:{s['id']}")])
        await callback.message.answer(
            f"Текущие статусы: {have_names}\n\nВыбери статус:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=rows)
        )
    elif next_step == "status_revoke":
        await state.set_state(AdminStatuses.status_pick)
        have = await get_user_statuses(target['user_id'])
        if not have:
            await callback.message.answer(f"У {target['first_name'] if 'first_name' in target.keys() else ''} нет статусов для снятия.")
            await state.clear()
            return
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        rows = []
        for s in have:
            mark = "✅ " if s['is_selected'] else ""
            rows.append([InlineKeyboardButton(text=f"{mark}Снять: {s['name']}", callback_data=f"st_rev:{s['id']}")])
        await callback.message.answer(
            f"У {target['first_name'] if 'first_name' in target.keys() else ''}: {', '.join(s['name'] for s in have)}\n\nВыбери статус для снятия:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=rows)
        )
    elif next_step == "awgrant":
        awards = await get_all_awards()
        if not awards:
            await callback.message.answer("❌ Сначала создай хотя бы одну награду.")
            await state.clear()
            return
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        rows = []
        for a in awards:
            emoji = a['emoji'] or '🏅'
            rows.append([InlineKeyboardButton(text=f"{emoji} {a['name']}",
                                              callback_data=f"aw_pick:{a['id']}")])
        await callback.message.answer(
            f"Текущие награды: {', '.join(g['name'] for g in await get_user_awards(target['user_id'])) or 'нет'}\n\nВыбери награду:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=rows)
        )
    elif next_step == "awrevoke":
        have = await get_user_awards(target['user_id'])
        if not have:
            await callback.message.answer(f"У {target['first_name'] if 'first_name' in target.keys() else ''} нет наград для снятия.")
            await state.clear()
            return
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        rows = []
        for grant in have:
            emoji = grant['emoji'] or '🏅'
            rows.append([InlineKeyboardButton(text=f"{emoji} Снять: {grant['name']}",
                                              callback_data=f"awr_grant:{grant['grant_id']}")])
        await callback.message.answer(
            f"У {target['first_name'] if 'first_name' in target.keys() else ''}: {', '.join(g['name'] for g in have)}\n\nВыбери награду для снятия:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=rows)
        )
    elif next_step == "state_target":
        await state.set_state(AdminStates.action)
        from utils.states import get_state_info
        info = await get_state_info(target['user_id'])
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        await callback.message.answer(
            f"🎭 Игрок: {target['first_name'] if 'first_name' in target.keys() else ''} (@{target['username'] if 'username' in target.keys() else ''})\n"
            f"Текущее состояние: {info['name']}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🎭 Наложить состояние", callback_data="st_op:set")],
                [InlineKeyboardButton(text="✨ Снять состояние", callback_data="st_op:clear")],
            ])
        )
    elif next_step == "salary_set":
        await state.set_state(AdminSalary.amount)
        cur = await get_user_salary(target['user_id'])
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        await callback.message.answer(
            f"💰 Назначение зарплаты\nИгрок: {target['first_name'] if 'first_name' in target.keys() else ''} "
            f"(@{target['username'] if 'username' in target.keys() else ''})\n"
            f"Текущая зарплата: {cur['salary']} {plural_nordmark(cur['salary'])} "
            f"(период {cur['salary_period_days']} дн.)\n\n"
            f"Введи сумму зарплаты за один период (цифрой). 0 — снять зарплату.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="❌ Отмена", callback_data="admin:salaries")],
            ])
        )
    elif next_step == "callsign":
        await state.update_data(callsign_target_id=target['user_id'])
        await state.set_state(AdminCallsign.value)
        cur = target.get('callsign') or '—'
        await callback.message.answer(
            f"📡 Установка позывного\nИгрок: {target['first_name'] if 'first_name' in target.keys() else ''} "
            f"(@{target['username'] if 'username' in target.keys() else ''})\n"
            f"Текущий позывной: {cur}\n\nВведи новый позывной (или «-» чтобы убрать):",
            reply_markup=cancel_keyboard()
        )
    elif next_step == "wing":
        from utils.wings import WINGS
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        await state.set_state(AdminWing.value)
        cur_wing = (target.get('wing') or '') if 'wing' in target.keys() else ''
        cur_label = WINGS.get(cur_wing, '🚫 нет крыла')
        rows = [[InlineKeyboardButton(text=label, callback_data=f"wing_set:{key}")]
                for key, label in WINGS.items()]
        rows.append([InlineKeyboardButton(text="🚫 Снять крыло", callback_data="wing_set:none")])
        rows.append([InlineKeyboardButton(text="🔙 Отмена", callback_data="admin:menu")])
        await callback.message.answer(
            f"🪽 Установка авиакрыла\nИгрок: {target['first_name'] if 'first_name' in target.keys() else ''} "
            f"(@{target['username'] if 'username' in target.keys() else ''})\n"
            f"Текущее крыло: {cur_label}\n\nВыбери авиакрыло:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=rows)
        )
    elif next_step == "delphoto":
        from database.db import get_user_photo
        photo = await get_user_photo(target['user_id'])
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        if photo:
            await callback.message.answer(
                f"🗑 Удаление фото профиля\nИгрок: {target['first_name'] if 'first_name' in target.keys() else ''} "
                f"(@{target['username'] if 'username' in target.keys() else ''})\n\n"
                f"Подтверди удаление фото:",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="✅ Да, удалить", callback_data=f"confirm_del_photo:{target['user_id']}")],
                    [InlineKeyboardButton(text="❌ Отмена", callback_data="admin:menu")],
                ])
            )
        else:
            await callback.message.answer("📷 У этого игрока нет установленного фото.")
            await state.clear()
    elif next_step == "player_log":
        await show_player_log(callback.message, target, state)


async def show_player_log(msg, target: dict, state: FSMContext):
    """Показать лог взаимодействий игрока. msg — Message или CallbackQuery.message."""
    await state.clear()
    entries = await get_user_activity(target['user_id'], 80)
    name = target.get('first_name') or ''
    username = target.get('username') or ''
    if not entries:
        await msg.answer(
            f"📒 Лог игрока\nИгрок: {name} "
            f"(@{username if username else ''})\n\n"
            f"Событий нет."
        )
        return
    lines = []
    for e in entries:
        dt = e['created_at'][:16] if e['created_at'] else ""
        details = e['details'] or ""
        lines.append(f"{dt} {details}")
    text = (
        f"📒 ЛОГ ИГРОКА\nИгрок: {name} "
        f"(@{username if username else ''})\n"
        f"Последних событий: {len(entries)}\n\n" + "\n".join(lines)
    )
    await msg.answer(text[:4000])


@router.message(AdminPlayerLog.target)
async def admin_player_log_manual_msg(message: Message, state: FSMContext):
    if not await has_permission(message.from_user.id, "can_view_logs"):
        await message.answer("❌ Нет прав для просмотра логов.")
        await state.clear()
        return
    target = await find_user(message.text)
    if not target:
        await message.answer("❌ Игрок не найден по этому имени/тегу/id. Попробуй ещё раз:")
        return
    await show_player_log(message, target, state)


def category_choice_markup():
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    rows = []
    for key, label in ITEM_CATEGORIES.items():
        if key == "market":
            continue  # витрина «Рынок» собирается из офферов игроков, а не обычных товаров
        rows.append([InlineKeyboardButton(text=f"{label}", callback_data=f"cat:{key}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def drink_choice_markup(edit_mode: bool = False):
    """Меню выбора типа напитка (для добавления и правки товара).

    prefix 'drinksel:' — при добавлении (переводит на следующий шаг),
    'editset:drink:' — при правке существующего товара.
    """
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    p = "editset:drink:" if edit_mode else "drinksel:"
    choice = [
        ("❌ Не напиток", "none"),
        ("🍺 Слабоалкогольный (пиво)", "alcohol_weak"),
        ("🥃 Крепкий алкоголь (водка)", "alcohol_strong"),
        ("🤢 С несварением", "indigestion"),
        ("🥵 С истощением", "exhaustion"),
        ("⚠️ Несварение + истощение", "indigestion_exhaustion"),
        ("🥤 Безалкогольный, без эффекта", "none"),
    ]
    rows = [[InlineKeyboardButton(text=text, callback_data=f"{p}{key}")] for text, key in choice]
    return InlineKeyboardMarkup(inline_keyboard=rows)


# Особые эффекты оружия (в бою подземелья, v0.14.3). v0.15.18: + «stun» —
# штраф к точности врага на пару ходов (шанс промаха = weapon_effect_dmg %).
WEAPON_EFFECT_LABELS = {
    "poison": "☠️ Отравление",
    "bleed": "🩸 Кровотечение",
    "frostbite": "🧊 Обморожение",
    "stun": "💫 Оглушение",
}
WEAPON_EFFECT_HINT = {
    "poison": "враг теряет урон от яда каждый ход",
    "bleed": "враг истекает кровью каждый ход",
    "frostbite": "мороз сковывает врага, урон каждый ход",
    "stun": "враг дезориентирован: его точность падает на пару ходов",
}


def weapon_effect_choice_markup(prefix: str = "weff:"):
    """Меню выбора особого эффекта оружия.

    prefix 'weff:' — в мастере добавления товара (идёт на ввод шанса),
    'editset:weff:' — при правке существующего товара (сразу применяет).
    """
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    rows = []
    for key, label in WEAPON_EFFECT_LABELS.items():
        rows.append([InlineKeyboardButton(text=label, callback_data=f"{prefix}{key}")])
    rows.append([InlineKeyboardButton(text="🚫 Без эффекта", callback_data=f"{prefix}none")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ============ ВХОД В АДМИН-ПАНЕЛЬ ============

async def show_admin_panel(user_id: int, to_edit: CallbackQuery = None, to_msg: Message = None):
    from keyboards.keyboards import admin_panel_keyboard
    flags = await perm_flags(user_id)
    text = (
        "👑 АДМИН-ПАНЕЛЬ\n\n"
        "Выберите раздел. Доступные действия зависят от вашей роли:\n\n"
        f"Версия сборки: {VERSION}"
    )
    markup = admin_panel_keyboard(flags)
    if to_edit is not None:
        await to_edit.message.edit_text(text, reply_markup=markup)
    else:
        await to_msg.answer(text, reply_markup=markup)


@router.message(F.text == "👑 Админ-панель")
async def admin_panel(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id

    if not await is_admin(user_id):
        await message.answer("❌ У вас нет доступа к админ-панели.")
        return

    await show_admin_panel(user_id, to_msg=message)


@router.callback_query(F.data == "admin:menu")
async def admin_panel_cb(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    user_id = callback.from_user.id
    if not await is_admin(user_id):
        await callback.answer("❌ Нет доступа.", show_alert=True)
        return
    await show_admin_panel(user_id, to_edit=callback)


@router.callback_query(F.data == "admin:del_photo")
async def admin_del_photo_start(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_users"):
        await callback.message.answer("❌ Нет прав для удаления фото.")
        return
    await callback.message.answer(
        "🗑 Выбери пилота, у которого нужно удалить фото профиля:",
        reply_markup=await pilot_picker_markup("delphoto")
    )


@router.callback_query(F.data == "admin:player_log")
async def admin_player_log_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_view_logs"):
        await callback.message.answer("❌ Нет прав для просмотра логов.")
        return
    await state.set_state(AdminPlayerLog.target)
    await callback.message.answer(
        "📒 Выбери игрока, чей лог взаимодействий показать:\n\n"
        "Или введи @username, имя или ID игрока прямо в чат:",
        reply_markup=await pilot_picker_markup("player_log")
    )


@router.callback_query(F.data == "admin:callsign")
async def admin_callsign_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_users"):
        await callback.message.answer("❌ Нет прав для установки позывного.")
        return
    await state.set_state(AdminCallsign.target)
    await callback.message.answer(
        "📡 Кому установить позывной? Выбери пилота:",
        reply_markup=await pilot_picker_markup("callsign")
    )


@router.callback_query(F.data == "admin:wing")
async def admin_wing_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_wing"):
        await callback.message.answer("❌ Нет прав для управления авиакрыльями.")
        return
    await state.set_state(AdminWing.target)
    await callback.message.answer(
        "🪽 Кому установить авиакрыло? Выбери пилота:",
        reply_markup=await pilot_picker_markup("wing")
    )


@router.message(AdminCallsign.target)
async def admin_callsign_target_msg(message: Message, state: FSMContext):
    if not await has_permission(message.from_user.id, "can_manage_users"):
        await message.answer("❌ Нет прав для установки позывного.")
        await state.clear()
        return
    target = await find_user(message.text)
    if not target:
        await message.answer("❌ Игрок не найден. Попробуй ещё раз:")
        return
    await state.update_data(callsign_target_id=target['user_id'])
    await state.set_state(AdminCallsign.value)
    cur = target.get('callsign') or '—'
    await message.answer(
        f"📡 Игрок: {target['first_name'] if 'first_name' in target.keys() else ''} "
        f"(@{target['username'] if 'username' in target.keys() else ''})\n"
        f"Текущий позывной: {cur}\n\nВведи новый позывной (или «-» чтобы убрать):",
        reply_markup=cancel_keyboard()
    )


@router.message(AdminCallsign.value)
async def admin_callsign_value_msg(message: Message, state: FSMContext):
    if not await has_permission(message.from_user.id, "can_manage_users"):
        await message.answer("❌ Нет прав для установки позывного.")
        await state.clear()
        return
    data = await state.get_data()
    target_id = data.get('callsign_target_id')
    if not target_id:
        await state.clear()
        await message.answer("❌ Сессия устарела, начни заново.")
        return
    text = message.text.strip()
    value = None if text in ("", "-") else text[:64]
    await set_callsign(target_id, value)
    await log_action(message.from_user.id, 'set_callsign', target_id, f"callsign={value or None}")
    await state.clear()
    u = await get_user(target_id)
    name = u['first_name'] if u and 'first_name' in u.keys() else target_id
    await message.answer(f"✅ Позывной «{value or '—'}» установлен для {name}.")


@router.callback_query(F.data.startswith("wing_set:"))
async def admin_wing_set_cb(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_wing"):
        await callback.message.answer("❌ Нет прав для управления авиакрыльями.")
        await state.clear()
        return
    _, raw = callback.data.split(":", 1)
    value = None if raw == "none" else raw
    data = await state.get_data()
    target_id = data.get('target_id')
    if not target_id:
        await state.clear()
        await callback.message.answer("❌ Сессия устарела, начни заново.")
        return
    await set_wing(target_id, value)
    from utils.wings import WINGS
    label = "🚫 снято крыло" if value is None else WINGS.get(value, "неизвестное крыло")
    await log_action(callback.from_user.id, 'set_wing', target_id, f"wing={value or None}")
    await state.clear()
    u = await get_user(target_id)
    name = u['first_name'] if u and 'first_name' in u.keys() else target_id
    await callback.message.answer(f"✅ {name}: авиакрыло — {label}.")


@router.callback_query(F.data.startswith("confirm_del_photo:"))
async def confirm_del_photo(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_users"):
        await callback.message.answer("❌ Нет прав для удаления фото.")
        return
    target_id = int(callback.data.split(":")[1])
    target = await get_user(target_id)
    if not target:
        await callback.message.answer("❌ Игрок не найден.")
        return
    await clear_user_photo(target_id)
    await log_action(callback.from_user.id, 'del_photo', target_id, "Удалено фото профиля")
    await log_activity(target_id, "photo_deleted", "Админ удалил фото профиля")
    await callback.message.answer(
        f"✅ Фото профиля удалено у {target['first_name'] if 'first_name' in target.keys() else ''}."
    )


# ============ УПРАВЛЕНИЕ МАГАЗИНОМ ============

@router.callback_query(F.data == "admin:shop")
async def admin_shop(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_shop"):
        await callback.message.answer("❌ Нет прав для управления магазином.")
        return

    from keyboards.keyboards import shop_admin_keyboard
    await callback.message.edit_text(
        "🛒 УПРАВЛЕНИЕ МАГАЗИНОМ\n\nВыберите действие:",
        reply_markup=shop_admin_keyboard()
    )


# ============ ХРАНИЛИЩЕ (только супер-админ) ============
# Здесь лежат ВСЕ предметы, когда-либо добавленные в бот — и распроданные,
# и скрытые. Это позволяет вернуть в магазин предмет без обращения к разработчику.

STORAGE_PER_PAGE = 10


def _storage_pages(total: int):
    return max(1, (total + STORAGE_PER_PAGE - 1) // STORAGE_PER_PAGE)


def storage_markup(items, page: int = 0):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    total = len(items)
    pages = _storage_pages(total)
    page = max(0, min(page, pages - 1))
    start = page * STORAGE_PER_PAGE
    chunk = items[start:start + STORAGE_PER_PAGE]

    rows = []
    for it in chunk:
        if it['is_available']:
            status = "🟢" if it['stock'] != 0 else "🟡"
            marker = f"{status} {it['name']} (ост. {it['stock']})"
        else:
            marker = f"🔴 {it['name']} — скрыт"
        rows.append([InlineKeyboardButton(
            text=marker,
            callback_data=f"storage:item:{it['id']}"
        )])

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="◀️", callback_data=f"storage:page:{page-1}"))
    nav.append(InlineKeyboardButton(text=f"{page+1}/{pages}", callback_data="storage:noop"))
    if page < pages - 1:
        nav.append(InlineKeyboardButton(text="▶️", callback_data=f"storage:page:{page+1}"))
    if nav:
        rows.append(nav)

    rows.append([InlineKeyboardButton(text="🔙 Админ-панель", callback_data="admin:menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


@router.callback_query(F.data == "admin:storage")
async def admin_storage(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_storage"):
        await callback.message.answer("❌ Раздел доступен только Хранителю.")
        return
    items = await get_all_items()
    if not items:
        await callback.message.edit_text("📦 Хранилище пусто.", reply_markup=storage_markup([]))
        return
    text = (f"📦 ХРАНИЛИЩЕ НОРДХАЙМА\n"
            f"Всего позиций: {len(items)}\n\n"
            f"🟢 — в продаже, 🟡 — почти распродан, 🔴 — скрыт. "
            f"Нажми на предмет, чтобы вернуть его в магазин.")
    await callback.message.edit_text(text, reply_markup=storage_markup(items))


@router.callback_query(F.data == "storage:noop")
async def storage_noop(callback: CallbackQuery):
    await callback.answer()


@router.callback_query(F.data.startswith("storage:page:"))
async def storage_page(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_storage"):
        return
    page = int(callback.data.split(":")[2])
    items = await get_all_items()
    await callback.message.edit_text(
        "📦 ХРАНИЛИЩЕ НОРДХАЙМА\n\n"
        "🟢 — в продаже, 🟡 — почти распродан, 🔴 — скрыт. "
        "Нажми на предмет, чтобы вернуть его в магазин.",
        reply_markup=storage_markup(items, page)
    )


@router.callback_query(F.data.startswith("storage:item:"))
async def storage_item(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_storage"):
        return
    item_id = int(callback.data.split(":")[2])
    item = await get_item(item_id)
    if not item:
        await callback.message.edit_text("❌ Предмет не найден.", reply_markup=storage_markup([]))
        return

    cat = ITEM_CATEGORIES.get(item['category'], item['category'])
    stock_text = "безлимит" if item['stock'] == -1 else str(item['stock'])
    status = ("🟢 в продаже" if item['is_available'] and item['stock'] != 0
              else "🟡 почти распродан" if item['is_available'] else "🔴 скрыт")

    text = (
        f"📦 *{item['name']}*\n"
        f"──────────────\n"
        f"Категория: {cat}\n"
        f"Редкость: {RARITY_LEVELS.get(item['rarity'], item['rarity'])}\n"
        f"Цена: {item['price']} {plural_nordmark(item['price'])}\n"
        f"Продажа: {item['sell_price']} {plural_nordmark(item['sell_price'])}\n"
        f"Остаток: {stock_text}\n"
        f"Статус: {status}\n"
    )
    if item.get('description'):
        text += f"📝 {item['description']}\n"
    if item.get('housing_type') or item.get('housing_slots'):
        hline = ""
        if item.get('housing_type'):
            hline += f"тип «{item['housing_type']}»"
        if item.get('housing_slots'):
            hline += (f"{', ' if hline else ''}слотов {item['housing_slots']}")
        text += f"\n🏠 Жильё: {hline}\n"

    rows = []
    if not item['is_available'] or item['stock'] == 0:
        if item['stock'] == 0:
            text += "\n⚠️ Предмет распродан. Верни его в магазин, указав количество."
        else:
            text += "\n⚠️ Предмет скрыт. Верни его в магазин, указав количество."
        rows.append([InlineKeyboardButton(text="➕ Вернуть в магазин", callback_data=f"storage:restock:{item_id}")])
    rows.append([InlineKeyboardButton(text="✏️ Редактировать (покупка: цена/фото/описание)",
                                      callback_data=f"edit_item:{item_id}")])
    rows.append([InlineKeyboardButton(text="🔙 К списку", callback_data="admin:storage")])
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    await callback.message.edit_text(text, reply_markup=kb)


@router.callback_query(F.data.startswith("storage:restock:"))
async def storage_restock(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_storage"):
        return
    item_id = int(callback.data.split(":")[2])
    item = await get_item(item_id)
    if not item:
        await callback.message.edit_text("❌ Предмет не найден.", reply_markup=storage_markup([]))
        return
    await state.update_data(storage_item_id=item_id)
    await state.set_state(AdminStorageRestock.amount)
    await callback.message.edit_text(
        f"📦 «{item['name']}» — сколько единиц вернуть в магазин?\n"
        f"Введи число (например 100) или «-» для безлимита.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Отмена", callback_data="admin:storage")]
        ])
    )


@router.message(AdminStorageRestock.amount)
async def storage_restock_amount(message: Message, state: FSMContext):
    if not await has_permission(message.from_user.id, "can_manage_storage"):
        await state.clear()
        await message.answer("❌ Нет прав.")
        return
    text = message.text.strip()
    if text == "-":
        stock = -1
    else:
        try:
            stock = int(text)
        except ValueError:
            await message.answer("❌ Введи целое число или «-»:")
            return
        if stock < 0:
            await message.answer("❌ Количество не может быть отрицательным:")
            return

    data = await state.get_data()
    item_id = data.get('storage_item_id')
    if not item_id:
        await state.clear()
        await message.answer("❌ Сессия устарела. Зайди в Хранилище заново.")
        return
    item = await get_item(item_id)
    if not item:
        await state.clear()
        await message.answer("❌ Предмет не найден.")
        return

    await update_item(item_id, stock=stock, is_available=1)
    await log_action(message.from_user.id, 'storage_restock', None,
                     f"item={item['name']} id={item_id} stock={stock}")
    await state.clear()
    await message.answer(
        f"✅ «{item['name']}» возвращён в магазин!\n"
        f"Остаток: {'безлимит' if stock == -1 else stock}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📦 В Хранилище", callback_data="admin:storage")]
        ])
    )


@router.callback_query(F.data == "shop_admin:add")
async def shop_admin_add(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_add_items"):
        await callback.message.answer("❌ Нет прав на добавление товаров.")
        return
    await state.set_state(AdminAddItem.name)
    await callback.message.answer(
        "🛒 Добавление товара. Шаг 1/9\n\nВведи название товара (или /cancel):",
        reply_markup=cancel_keyboard()
    )


@router.message(AdminAddItem.name)
async def add_item_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await state.set_state(AdminAddItem.desc)
    await message.answer("Шаг 2/9 — Описание товара (или «-» если нет):",
                         reply_markup=cancel_keyboard())


@router.message(AdminAddItem.desc)
async def add_item_desc(message: Message, state: FSMContext):
    text = message.text.strip()
    await state.update_data(desc=None if text == "-" else text)
    await state.set_state(AdminAddItem.price)
    await message.answer("Шаг 3/9 — Цена в Нордмарках (целое число):",
                         reply_markup=cancel_keyboard())


@router.message(AdminAddItem.price)
async def add_item_price(message: Message, state: FSMContext):
    try:
        price = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Введи целое число.")
        return
    if price < 0:
        await message.answer("❌ Цена не может быть отрицательной.")
        return
    await state.update_data(price=price)
    await state.set_state(AdminAddItem.sell_price)
    await message.answer(f"Шаг 4/9 — Цена продажи за {price}? Введи сумму (или «-» = половина):",
                         reply_markup=cancel_keyboard())


@router.message(AdminAddItem.sell_price)
async def add_item_sell_price(message: Message, state: FSMContext):
    data = await state.get_data()
    text = message.text.strip()
    if text == "-":
        sell_price = int(data['price'] / 2)
    else:
        try:
            sell_price = int(text)
        except ValueError:
            await message.answer("❌ Введи целое число или «-».")
            return
    await state.update_data(sell_price=sell_price)
    await state.set_state(AdminAddItem.rarity)
    await message.answer("Шаг 5/9 — Редкость:", reply_markup=rarity_choice_markup())


@router.callback_query(F.data.startswith("rar:"))
async def add_item_rarity(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    rarity = int(callback.data.split(":")[1])
    await state.update_data(rarity=rarity)
    await state.set_state(AdminAddItem.category)
    await callback.message.answer("Шаг 6/9 — Категория:", reply_markup=category_choice_markup())


@router.callback_query(F.data.startswith("cat:"))
async def add_item_category(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    category = callback.data.split(":")[1]
    await state.update_data(category=category)
    if category == 'seeds':
        # Семечку нужно имя выросшего растения: в кадке показывается растение,
        # а не семечко-товар (например «Яблочное семечко» → «Яблоня»).
        await state.set_state(AdminAddItem.plant_name)
        await callback.message.answer(
            "🌱 Это семечко — дополнительный шаг.\n\n"
            "Как будет называться растение в кадке после посадки?\n"
            "Например: «Яблочное семечко» → «Яблоня».\n\n"
            "Введи название растения (или «-» = называть как семечко):",
            reply_markup=cancel_keyboard()
        )
        return
    if category == 'consumable':
        # Напитку нужен тип действия на состояние; остальные расходники идут дальше.
        await state.set_state(AdminAddItem.drink)
        await callback.message.answer(
            "Напиток или обычный расходник?\n\n"
            "Напитки пьются где угодно (в бою — кнопкой слота): "
            "алкоголь даёт состояния «пьян»/«очень пьян», "
            "безалкогольные могут вызывать несварение или истощение.",
            reply_markup=drink_choice_markup()
        )
        return
    await state.set_state(AdminAddItem.stock)
    await callback.message.answer("Шаг 7/9 — Остаток на складе (или «-» = безлимит):",
                                  reply_markup=cancel_keyboard())


@router.callback_query(F.data.startswith("drinksel:"))
async def add_item_drink_choice(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    effect = callback.data.split(":", 1)[1]
    await state.update_data(drink_effect=None if effect in ("none", "") else effect)
    await state.set_state(AdminAddItem.stock)
    await callback.message.answer("Шаг 7/9 — Остаток на складе (или «-» = безлимит):",
                                  reply_markup=cancel_keyboard())


@router.message(AdminAddItem.plant_name)
async def add_item_plant_name(message: Message, state: FSMContext):
    text = message.text.strip()
    await state.update_data(plant_name=None if text in ("-", "—") else text)
    await state.set_state(AdminAddItem.stock)
    await message.answer("Шаг 7/9 — Остаток на складе (или «-» = безлимит):",
                         reply_markup=cancel_keyboard())


@router.message(AdminAddItem.stock)
async def add_item_stock(message: Message, state: FSMContext):
    text = message.text.strip()
    if text == "-":
        stock = -1
    else:
        try:
            stock = int(text)
        except ValueError:
            await message.answer("❌ Введи целое число или «-».")
            return
    await state.update_data(stock=stock)
    data = await state.get_data()
    cat = data.get('category')
    if cat == 'weapon':
        await state.set_state(AdminAddItem.stats)
        await message.answer("Шаг 8/9 — Урон оружия (число), 0 если нет:",
                             reply_markup=cancel_keyboard())
        return
    if cat == 'equipment':
        await state.set_state(AdminAddItem.stats)
        await message.answer("Шаг 8/9 — Защита снаряжения (число), 0 если нет:",
                             reply_markup=cancel_keyboard())
        return
    await _go_add_item_producer(message, state)


@router.message(AdminAddItem.stats, F.text.regexp(r"^\d+$"))
async def add_item_stats(message: Message, state: FSMContext):
    data = await state.get_data()
    value = int(message.text)
    if data.get('category') == 'weapon':
        await state.update_data(damage=value)
        await state.set_state(AdminAddItem.weapon_effect)
        await message.answer(
            "Шаг 8/9 — Особый эффект оружия при попадании?\n"
            "Отравление/кровотечение/обморожение бьют врага каждый ход, "
            "оглушение — сбивает его точность на пару ходов.",
            reply_markup=weapon_effect_choice_markup()
        )
        return
    else:
        await state.update_data(armor=value)
        if value > 0:
            from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
            await state.set_state(AdminAddItem.equip_slot)
            await message.answer(
                "Шаг 8/9 — На какую часть тела надевается?",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🪖 Голова", callback_data="eqpart:head")],
                    [InlineKeyboardButton(text="🦺 Тело", callback_data="eqpart:body")],
                    [InlineKeyboardButton(text="🧤 Руки", callback_data="eqpart:hands")],
                    [InlineKeyboardButton(text="🥾 Ноги", callback_data="eqpart:legs")],
                ])
            )
        else:
            await _go_add_item_producer(message, state)


@router.callback_query(F.data.startswith("eqpart:"))
async def add_item_equip_slot(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    slot = callback.data.split(":", 1)[1]
    await state.update_data(equip_slot=slot)
    await _go_add_item_producer(callback.message, state)


@router.message(AdminAddItem.stats)
async def add_item_stats_bad(message: Message):
    await message.answer("❌ Введи число (0 — если не требуется). Или /cancel.")


@router.callback_query(F.data.startswith("weff:"))
async def add_item_weapon_effect_cb(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    eff = callback.data.split(":", 1)[1]
    if eff == "none":
        await state.update_data(weapon_effect=None, weapon_effect_chance=0, weapon_effect_dmg=0)
        await _go_add_item_producer(callback.message, state)
        return
    await state.update_data(weapon_effect=eff)
    await state.set_state(AdminAddItem.weapon_effect_chance)
    await callback.message.answer(
        f"Шаг 8/9 — Шанс, что «{WEAPON_EFFECT_LABELS[eff]}» сработает "
        f"при попадании, % (0–100):",
        reply_markup=cancel_keyboard()
    )


@router.message(AdminAddItem.weapon_effect_chance)
async def add_item_weapon_effect_chance(message: Message, state: FSMContext):
    try:
        v = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Введи целое число (0–100):", reply_markup=cancel_keyboard())
        return
    if not 0 <= v <= 100:
        await message.answer("❌ Шанс от 0 до 100:", reply_markup=cancel_keyboard())
        return
    await state.update_data(weapon_effect_chance=v)
    data = await state.get_data()
    is_stun = data.get('weapon_effect') == 'stun'
    await state.set_state(AdminAddItem.weapon_effect_dmg)
    if is_stun:
        await message.answer(
            "Шаг 8/9 — Штраф к точности врага, % (шанс врага промахнуться "
            "на 2 хода, 0–100):",
            reply_markup=cancel_keyboard())
    else:
        await message.answer("Шаг 8/9 — Урон эффекта за каждый ход (целое число):",
                             reply_markup=cancel_keyboard())


@router.message(AdminAddItem.weapon_effect_dmg)
async def add_item_weapon_effect_dmg(message: Message, state: FSMContext):
    try:
        v = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Введи целое число:", reply_markup=cancel_keyboard())
        return
    if v < 0:
        await message.answer("❌ Урон не может быть отрицательным:", reply_markup=cancel_keyboard())
        return
    await state.update_data(weapon_effect_dmg=v)
    await _go_add_item_producer(message, state)


async def _go_add_item_producer(message: Message, state: FSMContext):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    await state.set_state(AdminAddItem.producer)
    await message.answer(
        "Шаг 9/9 — Кто продаёт этот товар?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏛️ Гос. магазин", callback_data="prod:state")],
            [InlineKeyboardButton(text="👤 Игрок-продавец", callback_data="prod:player")],
        ])
    )


@router.callback_query(F.data.startswith("prod:"))
async def add_item_producer(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    choice = callback.data.split(":")[1]
    if choice == "player":
        await state.set_state(AdminAddItem.producer_user)
        await callback.message.answer(
            "Шаг 8/10 — Введи @username или ID игрока, который продаёт этот товар "
            "(выручка с налогом уйдёт ему):",
            reply_markup=cancel_keyboard()
        )
        return
    await state.update_data(produced_by=None)
    await _go_add_item_market(callback.message, state)


@router.message(AdminAddItem.producer_user)
async def add_item_producer_user(message: Message, state: FSMContext):
    producer = await find_user(message.text)
    if not producer:
        await message.answer("❌ Игрок не найден. Попробуй @username или ID (или /cancel):")
        return
    await state.update_data(produced_by=producer['user_id'])
    await _go_add_item_market(message, state)


async def _go_add_item_market(message: Message, state: FSMContext):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    await state.set_state(AdminAddItem.market)
    await message.answer(
        "Шаг 9/10 — Можно ли продавать этот предмет на РЫНКЕ "
        "(другие игроки смогут покупать его с витрины)?\n"
        "Если нет — предмет продаётся только скупщику.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏪 Да, можно на рынок", callback_data="marketok:yes")],
            [InlineKeyboardButton(text="💵 Нет, только скупщику", callback_data="marketok:no")],
        ])
    )


@router.callback_query(F.data.startswith("marketok:"))
async def add_item_market_choice(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    choice = callback.data.split(":")[1]
    await state.update_data(market_ok=1 if choice == "yes" else 0)
    await state.set_state(AdminAddItem.photo)
    await callback.message.answer(
        "Шаг 10/10 — Загрузи фото товара (или «-» если без фото):",
        reply_markup=cancel_keyboard()
    )


@router.message(AdminAddItem.photo)
async def add_item_photo(message: Message, state: FSMContext):
    photo_file_id = None
    if message.photo:
        photo_file_id = message.photo[-1].file_id
    else:
        text = message.text.strip()
        if text not in ("-", "—"):
            await message.answer("❌ Отправь фото или «-»:")
            return
    await state.update_data(photo_file_id=photo_file_id)

    data = await state.get_data()
    admin_id = message.from_user.id
    stock = data['stock']

    item_id = await add_item(
        name=data['name'], description=data.get('desc'),
        price=data['price'], sell_price=data['sell_price'],
        rarity=data['rarity'], category=data['category'],
        stock=stock, added_by=admin_id,
        photo_file_id=data.get('photo_file_id'),
        produced_by=data.get('produced_by'),
        damage=data.get('damage', 0), armor=data.get('armor', 0),
        heal=data.get('heal', 0), drink_effect=data.get('drink_effect'),
        equip_slot=data.get('equip_slot'),
        market_ok=data.get('market_ok', 0),
        plant_name=data.get('plant_name'),
        weapon_effect=data.get('weapon_effect'),
        weapon_effect_chance=data.get('weapon_effect_chance', 0),
        weapon_effect_dmg=data.get('weapon_effect_dmg', 0),
    )
    await log_action(admin_id, 'add_item', data.get('produced_by'),
                     f"item={data['name']} id={item_id}")
    await state.clear()

    # Если мастер запущен из менеджера дропов — предмет создан как дроп врага:
    # сразу просим шанс выпадения и добавляем в дроп-лист врага.
    pending_enemy = data.get('pending_enemy_id')
    if pending_enemy:
        enemy = await get_enemy(int(pending_enemy))
        await state.update_data(enemy_id=int(pending_enemy), drop_item_id=item_id,
                                drop_index=None, pending_enemy_id=None)
        await state.set_state(AdminDungeon.drop_chance)
        await message.answer(
            f"✅ Предмет «{data['name']}» создан.\n\n"
            f"💼 Добавляем его в дропы «{enemy['name'] if enemy else '?»'}.\n"
            f"Введи шанс выпадения, % (1–100):",
            reply_markup=cancel_keyboard(),
        )
        return
    stats_line = ""
    if data.get('damage'):
        stats_line += f"\n⚔️ Урон: {data['damage']}"
    if data.get('armor'):
        stats_line += f"\n🛡️ Защита: {data['armor']}"
    if data.get('equip_slot'):
        part_label = {"head": "Голова", "body": "Тело", "hands": "Руки", "legs": "Ноги"}.get(
            data['equip_slot'], data['equip_slot'])
        stats_line += f"\n🪖 Надевается: {part_label}"
    if data.get('category') == 'seeds':
        pn = data.get('plant_name')
        stats_line += f"\n🌳 Растение в кадке: «{pn}»" if pn else "\n🌳 Растение называется как семечко"
    if data.get('weapon_effect'):
        weff = data['weapon_effect']
        stats_line += (f"\n☠️ Эффект: {WEAPON_EFFECT_LABELS.get(weff, weff)}"
                       f" | шанс {data.get('weapon_effect_chance', 0)}%")
        if weff == 'stun':
            stats_line += f" | штраф точности врага −{data.get('weapon_effect_dmg', 0)}% (2 хода)"
        else:
            stats_line += f" | −{data.get('weapon_effect_dmg', 0)} HP/ход"
    await message.answer(
        f"✅ Товар добавлен!\n\n"
        f"«{data['name']}»\n"
        f"Цена: {data['price']} {plural_nordmark(data['price'])}\n"
        f"Продажа: {data['sell_price']} {plural_nordmark(data['sell_price'])}\n"
        f"Редкость: {RARITY_LEVELS.get(data['rarity'])}\n"
        f"Категория: {ITEM_CATEGORIES.get(data['category'], data['category'])}\n"
        f"Остаток: {'безлимит' if stock == -1 else stock}"
        f"\n🏪 Рынок: {'можно продавать' if data.get('market_ok') else 'только скупщик'}"
        f"{stats_line}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ Добавить ещё товар", callback_data="shop_admin:add")],
            [InlineKeyboardButton(text="🔙 К меню управления магазином", callback_data="admin:shop")],
        ])
    )


@router.callback_query(F.data == "shop_admin:delete")
async def shop_admin_delete(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_delete_items"):
        await callback.message.answer("❌ Нет прав на удаление товаров.")
        return
    items = await get_available_items()
    if not items:
        await callback.message.answer("В магазине пока нет товаров.")
        return

    rows = []
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    for it in items:
        rows.append([InlineKeyboardButton(
            text=f"{it['name']} ({it['price']} НМ)",
            callback_data=f"del_item:{it['id']}"
        )])
    rows.append([InlineKeyboardButton(text="🔙 Назад", callback_data="admin:shop")])
    await callback.message.edit_text(
        "Выберите товар для удаления:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows)
    )


@router.callback_query(F.data.startswith("del_item:"))
async def delete_item_cb(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_delete_items"):
        return
    item_id = int(callback.data.split(":")[1])
    item = await get_item(item_id)
    if not item:
        await callback.message.answer("Товар не найден.")
        return
    await delete_item(item_id)
    await log_action(callback.from_user.id, 'delete_item', None, f"item={item['name']} id={item_id}")
    await callback.message.answer(f"🗑 Товар «{item['name']}» удалён.")


@router.callback_query(F.data == "shop_admin:edit")
async def shop_admin_edit(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_edit_items"):
        await callback.message.answer("❌ Нет прав на изменение товаров.")
        return
    items = await get_available_items()
    if not items:
        await callback.message.answer("В магазине пока нет товаров.")
        return

    rows = []
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    for it in items:
        rows.append([InlineKeyboardButton(
            text=f"{it['name']}",
            callback_data=f"edit_item:{it['id']}"
        )])
    rows.append([InlineKeyboardButton(text="🔙 Назад", callback_data="admin:shop")])
    await callback.message.edit_text("Выберите товар для изменения:",
                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))


@router.callback_query(F.data.startswith("edit_item:"))
async def edit_item_pick(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    item_id = int(callback.data.split(":")[1])
    await state.update_data(item_id=item_id)
    await state.set_state(AdminEditItem.field)
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    await callback.message.edit_text(
        "Что изменить?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Название", callback_data="field:name")],
            [InlineKeyboardButton(text="Цену", callback_data="field:price")],
            [InlineKeyboardButton(text="Продажу", callback_data="field:sell_price")],
            [InlineKeyboardButton(text="Остаток", callback_data="field:stock")],
            [InlineKeyboardButton(text="Категория", callback_data="field:category")],
            [InlineKeyboardButton(text="Описание", callback_data="field:description")],
            [InlineKeyboardButton(text="⚔️ Урон (оружие)", callback_data="field:damage")],
            [InlineKeyboardButton(text="☠️ Эффект оружия", callback_data="field:weapon_effect")],
            [InlineKeyboardButton(text="☠️ Шанс эффекта (%)", callback_data="field:weapon_effect_chance")],
            [InlineKeyboardButton(text="☠️ Урон эффекта/ход", callback_data="field:weapon_effect_dmg")],
            [InlineKeyboardButton(text="❤️ Лечение", callback_data="field:heal")],
            [InlineKeyboardButton(text="🛡️ Броня", callback_data="field:armor")],
            [InlineKeyboardButton(text="⚡ AP за использование", callback_data="field:ap_cost")],
            [InlineKeyboardButton(text="🔒 Требуемый статус", callback_data="field:required_status")],
            [InlineKeyboardButton(text="🖼 Картинка", callback_data="field:photo")],
            [InlineKeyboardButton(text="🍺 Тип напитка (действие)", callback_data="field:drink")],
            [InlineKeyboardButton(text="🌳 Растение в кадке (семечко)", callback_data="field:plant_name")],
            [InlineKeyboardButton(text="🏪 Рынок (вкл/выкл)", callback_data="field:market_ok")],
            [InlineKeyboardButton(text="🚧 Вкл/выкл продажу", callback_data="field:is_available")],
            [InlineKeyboardButton(text="🔆 Редкость", callback_data="field:rarity")],
            [InlineKeyboardButton(text="🏠 Тип жилья (дом)", callback_data="field:housing_type")],
            [InlineKeyboardButton(text="🏠 Слотов жилья", callback_data="field:housing_slots")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="shop_admin:edit")],
        ])
    )


@router.callback_query(F.data.startswith("field:required_status"))
async def edit_item_field_status(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    statuses = await get_all_statuses()
    rows = []
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    for s in statuses:
        rows.append([InlineKeyboardButton(text=f"{s['name']}", callback_data=f"field_req:{s['id']}")])
    rows.append([InlineKeyboardButton(text="➖ Без статуса", callback_data="field_req:none")])
    data = await state.get_data()
    item_id = data.get('item_id')
    if item_id:
        rows.append([InlineKeyboardButton(text="🔙 Назад", callback_data=f"edit_item:{item_id}")])
    await callback.message.edit_text(
        "Выбери статус, требуемый для покупки этого товара:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows)
    )


@router.callback_query(F.data.startswith("field_req:"))
async def edit_item_field_req(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    item_id = data['item_id']
    val = callback.data.split(":")[1]
    if val == "none":
        tag = None
    else:
        s = await get_status(int(val))
        tag = s['access_tag'] if s else None
    await update_item(item_id, required_status=tag)
    await log_action(callback.from_user.id, 'edit_item', None, f"item_id={item_id} required_status={tag}")
    await state.clear()
    await callback.message.answer("✅ Требуемый статус обновлён.")


@router.callback_query(F.data == "field:photo")
async def edit_item_field_photo(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(AdminEditItem.photo)
    await callback.message.answer(
        "🖼 Отправь фото товара (или «-», чтобы убрать картинку).",
        reply_markup=cancel_keyboard())


@router.callback_query(F.data == "field:weapon_effect")
async def edit_item_field_weapon_effect(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text(
        "☠️ Выбери особый эффект оружия при попадании:\n"
        "При «Без эффекта» шанс и урон эффекта обнуляются.",
        reply_markup=weapon_effect_choice_markup(prefix="editset:weff:")
    )


@router.callback_query(F.data.startswith("editset:weff:"))
async def edit_item_set_weapon_effect(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    item_id = data['item_id']
    eff = callback.data.split(":", 2)[2]
    if eff in WEAPON_EFFECT_LABELS:
        await update_item(item_id, weapon_effect=eff)
        label = WEAPON_EFFECT_LABELS[eff]
    else:
        await update_item(item_id, weapon_effect=None, weapon_effect_chance=0, weapon_effect_dmg=0)
        label = "🚫 Без эффекта"
    await log_action(callback.from_user.id, 'edit_item', None,
                     f"item_id={item_id} weapon_effect={eff}")
    await state.clear()
    await callback.message.answer(f"✅ Эффект оружия обновлён: {label}")


@router.message(AdminEditItem.photo)
async def edit_item_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    item_id = data.get('item_id')
    item = await get_item(item_id)
    if not item:
        await state.clear()
        await message.answer("❌ Товар не найден.")
        return
    if message.text and message.text.strip() == "-":
        await update_item(item_id, photo_file_id=None)
        await log_action(message.from_user.id, 'edit_item', None, f"item_id={item_id} photo cleared")
        await state.clear()
        await message.answer("✅ Картинка убрана.")
        return
    if not message.photo:
        await message.answer("❌ Отправь именно фото (или «-» для очистки).")
        return
    file_id = message.photo[-1].file_id
    await update_item(item_id, photo_file_id=file_id)
    await log_action(message.from_user.id, 'edit_item', None, f"item_id={item_id} photo updated")
    await state.clear()
    await message.answer(f"✅ Картинка товара «{item['name']}» обновлена.")


@router.callback_query(F.data == "field:drink")
async def edit_item_field_drink(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    from utils.helpers import row_get
    data = await state.get_data()
    item_id = data.get('item_id')
    item = await get_item(item_id) if item_id else None
    cur = row_get(item, 'drink_effect') if item else None
    cur_label = (DRINK_EFFECT_LABELS.get(cur) if cur in DRINK_EFFECT_LABELS else
                 ("🥤 не напиток" if not cur else cur))
    markup = drink_choice_markup(edit_mode=True)
    from aiogram.types import InlineKeyboardButton
    item_id = data.get('item_id')
    if item_id:
        markup.inline_keyboard.append(
            [InlineKeyboardButton(text="🔙 Назад", callback_data=f"edit_item:{item_id}")]
        )
    await callback.message.answer(
        f"🍺 Текущий тип напитка у «{item['name'] if item else 'товар'}»: {cur_label}.\n\n"
        f"Выбери новое действие:",
        reply_markup=markup)


@router.callback_query(F.data.startswith("editset:drink:"))
async def edit_item_set_drink(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    from utils.helpers import row_get
    effect = callback.data.split(":")[2]
    data = await state.get_data()
    item_id = data.get('item_id')
    item = await get_item(item_id)
    if not item:
        await state.clear()
        await callback.message.answer("❌ Товар не найден.")
        return
    new_effect = None if effect in ("none", "") else effect
    await update_item(item_id, drink_effect=new_effect)
    label = DRINK_EFFECT_LABELS.get(new_effect) if new_effect in DRINK_EFFECT_LABELS else "не напиток"
    await log_action(callback.from_user.id, 'edit_item', None,
                     f"item_id={item_id} drink_effect={new_effect}")
    await state.clear()
    await callback.message.answer(f"✅ Тип напитка «{item['name']}» установлен: {label}.")


@router.callback_query(F.data == "field:market_ok")
async def edit_item_field_market_toggle(callback: CallbackQuery, state: FSMContext):
    """Вкл/выкл флага «можно продавать на рынке» без ввода текста."""
    await callback.answer()
    data = await state.get_data()
    item_id = data.get('item_id')
    item = await get_item(item_id) if item_id else None
    if not item:
        await state.clear()
        await callback.message.answer("❌ Товар не найден.")
        return
    new_val = 0 if item.get('market_ok') else 1
    await update_item(item_id, market_ok=new_val)
    await log_action(callback.from_user.id, 'edit_item', None,
                     f"item_id={item_id} market_ok={new_val}")
    label = "можно продавать" if new_val else "только скупщик"
    await callback.message.answer(f"✅ «{item['name']}»: 🏪 Рынок → {label}.")
    await state.clear()


@router.callback_query(F.data.startswith("field:"))
async def edit_item_field(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    field = callback.data.split(":")[1]
    await state.update_data(field=field)
    await state.set_state(AdminEditItem.value)
    await callback.message.answer("Введи новое значение (или «-» для очистки/безлимита):",
                                  reply_markup=cancel_keyboard())


@router.message(AdminEditItem.value)
async def edit_item_value(message: Message, state: FSMContext):
    text = message.text.strip()
    data = await state.get_data()
    field = data['field']
    item_id = data['item_id']

    if field in ("price", "sell_price"):
        if text == "-":
            await message.answer("❌ Цену/продажу нельзя очистить. Введи число:")
            return
        try:
            value = int(text)
        except ValueError:
            await message.answer("❌ Введи целое число:")
            return
    elif field in ("stock", "damage", "heal", "armor", "ap_cost", "is_available",
                   "weapon_effect_chance", "weapon_effect_dmg", "rarity",
                   "housing_slots"):
        if field == "housing_slots" and text == "-":
            value = None
        else:
            value = -1 if (text == "-" and field == "stock") else int(text)
        if field in ("weapon_effect_chance", "weapon_effect_dmg") and text == "-":
            value = 0
    else:
        value = None if text == "-" else text

    if field == "weapon_effect_chance":
        if not 0 <= value <= 100:
            await message.answer("❌ Шанс эффекта от 0 до 100:", reply_markup=cancel_keyboard())
            return
    if field == "weapon_effect_dmg":
        if value < 0:
            await message.answer("❌ Урон эффекта не может быть отрицательным:", reply_markup=cancel_keyboard())
            return
    if field == "rarity":
        if not 1 <= value <= 5:
            await message.answer("❌ Редкость от 1 до 5:", reply_markup=cancel_keyboard())
            return
    if field == "housing_slots" and value is not None and value < 0:
        await message.answer("❌ Слотов не может быть отрицательным:", reply_markup=cancel_keyboard())
        return

    await update_item(item_id, **{field: value})
    await log_action(message.from_user.id, 'edit_item', None, f"item_id={item_id} {field}={value}")
    await state.clear()
    await message.answer("✅ Изменения сохранены.")


# ============ ФИНАНСЫ ============

@router.callback_query(F.data == "admin:finance")
async def admin_finance(callback: CallbackQuery):
    await callback.answer()
    if not (await has_permission(callback.from_user.id, "can_manage_finance")
            or await has_permission(callback.from_user.id, "can_add_currency")
            or await has_permission(callback.from_user.id, "can_remove_currency")):
        await callback.message.answer("❌ Нет прав для управления финансами.")
        return
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    can_add = await has_permission(callback.from_user.id, "can_add_currency")
    can_remove = await has_permission(callback.from_user.id, "can_remove_currency")
    can_full = await has_permission(callback.from_user.id, "can_manage_finance")

    buttons = []
    if can_add:
        buttons.append([InlineKeyboardButton(text="Начислить НМ", callback_data="fin:nord:add")])
    if can_remove:
        buttons.append([InlineKeyboardButton(text="Списать НМ", callback_data="fin:nord:sub")])
    if can_full:
        buttons.append([InlineKeyboardButton(text="Начислить AP", callback_data="fin:ap:add")])
        buttons.append([InlineKeyboardButton(text="Списать AP", callback_data="fin:ap:sub")])
    if can_full:
        buttons.append([InlineKeyboardButton(text="🏛️ Казна", callback_data="admin:treasury")])
        buttons.append([InlineKeyboardButton(text="📊 Налог на отчёты", callback_data="admin:tax")])
        buttons.append([InlineKeyboardButton(text="📊 Налог на продажи", callback_data="admin:saletax")])
        buttons.append([InlineKeyboardButton(text="💰 Зарплаты", callback_data="admin:salaries")])
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="admin:menu")])

    await callback.message.edit_text(
        "💰 ФИНАНСЫ\n\nВыберите операцию:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )


@router.callback_query(F.data == "admin:treasury")
async def admin_treasury(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_finance"):
        await callback.message.answer("❌ Нет прав для управления казной.")
        return

    balance = await get_treasury_balance()
    debts = await get_treasury_debts()
    warn = ""
    if debts['total_debt'] > 0 or debts['shortfall'] > 0:
        if debts['total_debt']:
            warn += f"\n⚠️ Накопленный долг по зарплатам: {debts['total_debt']} {plural_nordmark(debts['total_debt'])}"
        if debts['shortfall']:
            warn += f"\n⚠️ На следующую выплату не хватает: {debts['shortfall']} {plural_nordmark(debts['shortfall'])}"
        warn += "\nПодробнее — в «Долги по выплатам»."
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    await callback.message.edit_text(
        f"🏛️ КАЗНА НОРДХАЙМА\n\n"
        f"Баланс: {balance} {plural_nordmark(balance)}"
        f"{warn}\n\n"
        f"Налог с отчётов и пожертвования пополняют казну.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💸 Выдать из казны", callback_data="treasury:give")],
            [InlineKeyboardButton(text="📊 Статистика казны", callback_data="treasury:stats")],
            [InlineKeyboardButton(text="📋 Долги по выплатам", callback_data="treasury:debts")],
            [InlineKeyboardButton(text="🔙 В финансы", callback_data="admin:finance")],
        ])
    )


@router.callback_query(F.data == "treasury:debts")
async def treasury_debts(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_finance"):
        await callback.message.answer("❌ Нет прав для управления казной.")
        return
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    debts = await get_treasury_debts()
    lines = []
    lines.append("🏛️ ДОЛГИ КАЗНЫ\n")
    lines.append(f"Баланс: {debts['balance']} {plural_nordmark(debts['balance'])}")

    if debts['total_debt'] > 0:
        lines.append(f"\n⚠️ Накопленный долг по зарплатам "
                     f"(казны не хватило на момент выплат):\n"
                     f"ИТОГО: {debts['total_debt']} {plural_nordmark(debts['total_debt'])}")
        for d in debts['debtors']:
            name = d['first_name'] or d['username'] or f"#{d['user_id']}"
            line = f"  • {name} — долг {d['salary_debt']} {plural_nordmark(d['salary_debt'])}"
            if d['salary']:
                line += f" (ставка {d['salary']}/{d['salary_period_days']} дн.)"
            if d['last_salary_date']:
                line += f" — посл. выплата {str(d['last_salary_date'])[:10]}"
            lines.append(line)
    else:
        lines.append("\nДолгов по зарплатам нет — все выплаты проходили полностью.")

    if debts['salaried_count']:
        lines.append(f"\nПрогноз на следующую выплату:\n"
                     f"Нужно: {debts['next_pay_need']} {plural_nordmark(debts['next_pay_need'])} "
                     f"({debts['salaried_count']} получателей)")
        if debts['shortfall'] > 0:
            lines.append(f"❗ Не хватит: {debts['shortfall']} "
                         f"{plural_nordmark(debts['shortfall'])} — часть уйдёт в долг")
        else:
            lines.append("✅ Средств достаточно.")
    else:
        lines.append("\nЗарплаты никому не назначены.")

    await callback.message.edit_text(
        "\n".join(lines),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 В казну", callback_data="admin:treasury")],
        ])
    )


@router.callback_query(F.data == "treasury:stats")
async def treasury_stats(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_finance"):
        await callback.message.answer("❌ Нет прав.")
        return
    stats = await get_treasury_stats()
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    lines = []
    lines.append(f"💰 Поступило: {stats['incoming_total']} {plural_nordmark(stats['incoming_total'])} ({stats['incoming_count']} оп.)")
    lines.append(f"💸 Выплачено: {stats['outgoing_total']} {plural_nordmark(stats['outgoing_total'])}")

    by_desc = stats['by_desc']
    if by_desc:
        lines.append("\n📥 Поступление по источникам:")
        for r in by_desc:
            d = r['description'] or "без описания"
            if len(d) > 40:
                d = d[:37] + "…"
            lines.append(f"  • {d}: +{r['total']} ({r['cnt']})")

    by_to = stats['by_to']
    if by_to:
        lines.append("\n📤 Выплаты по получателям:")
        for r in by_to:
            uname = await _uid_label(r['to_user'])
            lines.append(f"  • {uname}: −{r['total']} ({r['cnt']})")

    by_from = stats['by_from']
    if by_from:
        lines.append("\n📥 Пожертвования от игроков:")
        for r in by_from:
            uname = await _uid_label(r['from_user'])
            lines.append(f"  • {uname}: +{r['total']} ({r['cnt']})")

    text = "🏛️ СТАТИСТИКА КАЗНЫ\n\n" + "\n".join(lines)
    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 В казну", callback_data="admin:treasury")],
        ])
    )


async def _uid_label(user_id: int) -> str:
    u = await get_user(user_id)
    if u:
        return f"@{u['username']}" if u['username'] else (u['first_name'] or f"#{user_id}")
    return f"#{user_id}"


@router.callback_query(F.data == "treasury:give")
async def treasury_give(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_finance"):
        await callback.message.answer("❌ Нет прав.")
        return
    await state.set_state(AdminTreasury.amount)
    balance = await get_treasury_balance()
    await callback.message.answer(
        f"🏛️ Баланс казны: {balance} {plural_nordmark(balance)}\n"
        f"Введи сумму для выдачи:",
        reply_markup=cancel_keyboard()
    )


@router.message(AdminTreasury.amount)
async def treasury_amount(message: Message, state: FSMContext):
    try:
        amount = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Введи целое число.")
        return
    if amount <= 0:
        await message.answer("❌ Сумма должна быть больше нуля.")
        return

    balance = await get_treasury_balance()
    if amount > balance:
        await message.answer(f"❌ В казне недостаточно средств. Доступно: {balance} {plural_nordmark(balance)}.")
        return

    await state.update_data(amount=amount)
    await state.set_state(AdminTreasury.target)
    markup = await pilot_picker_markup("treasury_target")
    await message.answer("Кому выдать из казны?", reply_markup=markup)


@router.message(AdminTreasury.target)
async def treasury_target_manual(message: Message, state: FSMContext):
    target = await find_user(message.text)
    if not target:
        await message.answer("❌ Игрок не найден. Попробуй ещё раз (или /cancel):")
        return
    data = await state.get_data()
    amount = data['amount']
    await transfer_from_treasury(
        target['user_id'],
        amount,
        f"Выдача из казны админом #{message.from_user.id}"
    )
    await log_action(message.from_user.id, 'treasury', target['user_id'], f"give {amount}")
    await state.clear()
    await message.answer(f"✅ Из казны выдано {amount} {plural_nordmark(amount)}.")


@router.callback_query(F.data == "admin:tax")
async def admin_tax_view(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_finance"):
        await callback.message.answer("❌ Нет прав для управления налогом.")
        return
    current = await get_report_tax_percent()
    await state.set_state(AdminTax.percent)
    await callback.message.edit_text(
        f"📊 НАЛОГ НА ОТЧЁТЫ\n\n"
        f"Текущая ставка: {current}%\n\n"
        f"Введи новую ставку налога (0–100) для всех граждан:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 В финансы", callback_data="admin:finance")]
        ])
    )


@router.message(AdminTax.percent)
async def admin_tax_set(message: Message, state: FSMContext):
    try:
        percent = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Введи целое число от 0 до 100:")
        return
    if not 0 <= percent <= 100:
        await message.answer("❌ Ставка должна быть от 0 до 100:")
        return
    await set_report_tax_percent(percent)
    await log_action(message.from_user.id, 'set_tax', None, f"percent={percent}")
    await state.clear()
    await message.answer(
        f"✅ Налог на отчёты установлен: {percent}%.\n"
        f"Изменение действует сразу для всех граждан."
    )


@router.callback_query(F.data == "admin:saletax")
async def admin_saletax_view(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_finance"):
        await callback.message.answer("❌ Нет прав для управления налогом.")
        return
    current = await get_sale_tax_percent()
    await state.set_state(AdminSaleTax.percent)
    await callback.message.edit_text(
        f"📊 НАЛОГ НА ПРОДАЖИ\n\n"
        f"Текущая ставка: {current}%\n\n"
        f"С продаж товаров игроков в магазине берётся этот процент "
        f"(выручка продавцу приходит за вычетом налога).\n\n"
        f"Введи новую ставку (0–100):",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 В финансы", callback_data="admin:finance")]
        ])
    )


@router.message(AdminSaleTax.percent)
async def admin_saletax_set(message: Message, state: FSMContext):
    try:
        percent = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Введи целое число от 0 до 100:")
        return
    if not 0 <= percent <= 100:
        await message.answer("❌ Ставка должна быть от 0 до 100:")
        return
    await set_sale_tax_percent(percent)
    await log_action(message.from_user.id, 'set_sale_tax', None, f"percent={percent}")
    await state.clear()
    await message.answer(
        f"✅ Налог на продажи установлен: {percent}%.\n"
        f"Изменение действует сразу для всех товаров игроков."
    )


# ============ СПЕЦ-ОТДЕЛ (КОД ДОСТУПА) ============

@router.callback_query(F.data == "shop_admin:special_code")
async def admin_special_code_view(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_shop"):
        await callback.message.answer("❌ Нет прав для управления магазином.")
        return
    current = await get_special_dept_code()
    current_text = current if current else "не задан (отдел закрыт)"
    await state.set_state(AdminSpecialCode.code)
    await callback.message.edit_text(
        f"🔐 КОД СПЕЦ-ОТДЕЛА\n\n"
        f"Текущий код: {current_text}\n\n"
        f"Спец-отдел — закрытая секция магазина. Покупать товары из неё могут "
        f"только те, кто знает код (4–8 цифр). После 3 неверных попыток покупки "
        f"блокируются на 24 часа.\n\n"
        f"Введи новый код (4–8 цифр) или «-» чтобы закрыть отдел:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 В управление магазином", callback_data="admin:shop")]
        ])
    )


@router.message(AdminSpecialCode.code)
async def admin_special_code_set(message: Message, state: FSMContext):
    text = message.text.strip()
    if text == "-":
        await set_special_dept_code("")
        await log_action(message.from_user.id, 'set_special_dept_code', None, f"closed")
        await state.clear()
        await message.answer("🔐 Спец-отдел закрыт. Товары из него больше нельзя купить.")
        return
    if not text.isdigit() or not (4 <= len(text) <= 8):
        await message.answer("❌ Код должен содержать 4–8 цифр. Повтори ввод:")
        return
    await set_special_dept_code(text)
    await log_action(message.from_user.id, 'set_special_dept_code', None, f"set")
    await state.clear()
    await message.answer(
        f"🔐 Код спец-отдела установлен: {text}.\n"
        f"Покупатели будут вводить его при покупке из спец-отдела."
    )


@router.callback_query(F.data == "fin:manual")
async def finance_manual(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(AdminFinance.target)
    await callback.message.answer(
        "Введи получателя: @username или numeric ID игрока:",
        reply_markup=cancel_keyboard()
    )


@router.callback_query(F.data.startswith("fin:"))
async def finance_pick(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    parts = callback.data.split(":")
    if len(parts) < 3:
        await callback.message.answer("❌ Некорректный вызов.")
        return
    currency = parts[1]
    action = parts[2]
    await state.update_data(currency=currency, action=action)
    await state.set_state(AdminFinance.target)

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    users = await get_all_users()
    rows = []
    if users:
        for u in users[:50]:
            label = u['first_name'] or u['username'] or str(u['user_id'])
            if u['username']:
                label += f" (@{u['username']})"
            rows.append([InlineKeyboardButton(text=label, callback_data=f"finuser:{u['user_id']}")])
    rows.append([InlineKeyboardButton(text="✍️ Ввести вручную", callback_data="fin:manual")])
    rows.append([InlineKeyboardButton(text="🔙 Отмена", callback_data="admin:menu")])

    await callback.message.answer(
        "Выбери пилота или введи @username/ID:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows)
    )


@router.callback_query(F.data.startswith("finuser:"))
async def finance_pick_user(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    user_id = int(callback.data.split(":")[1])
    target = await get_user(user_id)
    if not target:
        await callback.message.answer("❌ Игрок не найден.")
        return
    data = await state.get_data()
    await state.update_data(target_id=target['user_id'], target_name=target['first_name'] if 'first_name' in target.keys() else '')
    await state.set_state(AdminFinance.amount)
    await callback.message.answer(
        _finance_target_line(target, data.get('currency', 'nord'), data.get('action', 'add')),
        reply_markup=cancel_keyboard()
    )


def _finance_target_line(target: dict, currency: str, action: str) -> str:
    """Строка выбора пилота для начисления/списания: имя + текущий баланс валюты."""
    name = (target.get('first_name') or '')
    username = (target.get('username') or '')
    label = f"{name} (@{username})" if username else (name or f"#{target.get('user_id')}")
    direction = "начислить" if action == "add" else "списать"
    if currency == "nord":
        bal = int(target.get('nordmarks') or 0)
        bal_line = f"💰 Текущий баланс: {bal} {plural_nordmark(bal)}"
    else:
        bal = int(target.get('ap') or 0)
        bal_line = f"⚡ Текущий AP: {bal}"
    troops = int(target.get('troops') or 0)
    text = (
        f"Игрок: {label}\n"
        f"{bal_line}\n"
        f"⚔️ Войска: {troops}\n"
        f"──────────────\n"
        f"Введи сумму для {direction}:"
    )
    return text


@router.message(AdminFinance.target)
async def finance_target(message: Message, state: FSMContext):
    target = await find_user(message.text)
    if not target:
        await message.answer("❌ Игрок не найден. Попробуй ещё раз (или /cancel):")
        return
    data = await state.get_data()
    await state.update_data(target_id=target['user_id'], target_name=target['first_name'] if 'first_name' in target.keys() else '')
    await state.set_state(AdminFinance.amount)
    await message.answer(
        _finance_target_line(target, data.get('currency', 'nord'), data.get('action', 'add')),
        reply_markup=cancel_keyboard()
    )


@router.message(AdminFinance.amount)
async def finance_amount(message: Message, state: FSMContext):
    try:
        amount = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Введи целое число.")
        return
    if amount <= 0:
        await message.answer("❌ Сумма должна быть больше нуля.")
        return

    data = await state.get_data()
    target_id = data['target_id']
    currency = data['currency']
    action = data['action']
    admin = message.from_user.id

    if currency == "nord":
        if action == "add":
            # Суточный лимит начислений для Квестора (5000 НМ/день)
            roles = await get_user_role(admin)
            if "finance_helper" in roles:
                from datetime import date
                today = date.today().isoformat()
                spent = await get_daily_spent(admin, today)
                remaining = 5000 - spent
                if amount > remaining:
                    await message.answer(
                        f"❌ Превышен суточный лимит Квестора (5000 НМ).\n"
                        f"Доступно сегодня: {remaining} {plural_nordmark(remaining)}."
                    )
                    return
                await add_daily_spent(admin, today, amount)
            await add_nordmarks(target_id, amount, "admin", f"Начислено админом #{admin}")
            verb = "начислено"
        else:
            await remove_nordmarks(target_id, amount, "admin", f"Списано админом #{admin}")
            verb = "списано"
        unit = plural_nordmark(amount)
    else:
        if action == "add":
            await add_ap(target_id, amount, reason=f"начисление админом #{admin}")
            verb = "начислено"
        else:
            ok = await remove_ap(target_id, amount, reason=f"списание админом #{admin}")
            if not ok:
                await message.answer("❌ У игрока недостаточно AP.")
                return
            verb = "списано"
        unit = "AP"

    await log_action(admin, 'finance', target_id, f"{currency} {action} {amount}")
    await state.clear()
    await message.answer(
        f"✅ Игроку {data['target_name']} {verb} {amount} {unit}."
    )


# ============ РОЛИ ============

@router.callback_query(F.data == "admin:roles")
async def admin_roles(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_admins"):
        await callback.message.answer("❌ Нет прав для управления ролями.")
        return
    await state.set_state(AdminRoles.target)
    markup = await pilot_picker_markup("roles_action")
    await callback.message.answer(
        "👑 УПРАВЛЕНИЕ РОЛЯМИ\n\nВыбери пилота:",
        reply_markup=markup
    )


@router.message(AdminRoles.target)
async def roles_target(message: Message, state: FSMContext):
    target = await find_user(message.text)
    if not target:
        await message.answer("❌ Игрок не найден. Попробуй ещё раз (или /cancel):")
        return
    await state.update_data(target_id=target['user_id'], target_name=target['first_name'] if 'first_name' in target.keys() else '')
    await state.set_state(AdminRoles.action)
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    role_names = [role_label(r) for r in await get_user_role(target['user_id'])]
    await message.answer(
        f"Игрок: {target['first_name'] if 'first_name' in target.keys() else ''}\nТекущие роли: {', '.join(role_names)}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Выдать роль", callback_data="rolop:add")],
            [InlineKeyboardButton(text="Снять роль", callback_data="rolop:remove")],
        ])
    )


@router.callback_query(F.data.startswith("rolop:"))
async def roles_action(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    action = callback.data.split(":")[1]
    data = await state.get_data()
    await state.update_data(action=action)
    await state.set_state(AdminRoles.role)
    rows = []
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    if action == "add":
        # Выдача: весь список, кроме super_admin (выдаётся только командой — защита).
        for role_name in ROLES:
            if role_name == "super_admin":
                continue
            rows.append([InlineKeyboardButton(text=role_label(role_name), callback_data=f"role:{role_name}")])
        prompt = "Выбери роль для выдачи:"
    else:
        # Снятие: только роли, выданные этому игроку (не весь список).
        user_roles = await get_user_role(data['target_id'])
        for role_name in ROLES:
            if role_name in user_roles:
                rows.append([InlineKeyboardButton(text=role_label(role_name), callback_data=f"role:{role_name}")])
        if not rows:
            await state.clear()
            from keyboards.keyboards import back_to_main
            await callback.message.edit_text(
                "У этого игрока нет ролей для снятия.",
                reply_markup=back_to_main()
            )
            return
        prompt = "Выбери роль для снятия:"
    await callback.message.edit_text(
        prompt,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows)
    )


@router.callback_query(F.data.startswith("role:"))
async def roles_apply(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    role = callback.data.split(":")[1]
    data = await state.get_data()
    target_id = data['target_id']
    admin = callback.from_user.id
    action = data['action']

    if role == "super_admin":
        await callback.message.answer("❌ Роль «Хранитель» защищена от выдачи через панель.")
        return

    if action == "add":
        ok, msg = await add_role(admin, target_id, role)
    else:
        ok, msg = await remove_role(admin, target_id, role)

    await state.clear()
    await callback.message.answer(("✅ " if ok else "❌ ") + msg)


# ============ СТАТУСЫ ============

@router.callback_query(F.data == "admin:statuses")
async def admin_statuses(callback: CallbackQuery):
    await callback.answer()
    if not (await has_permission(callback.from_user.id, "can_manage_statuses")
            or await has_permission(callback.from_user.id, "can_grant_statuses")):
        await callback.message.answer("❌ Нет прав для управления статусами.")
        return

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    rows = []
    if await has_permission(callback.from_user.id, "can_manage_statuses"):
        rows.append([InlineKeyboardButton(text="➕ Создать статус", callback_data="st:create")])
        rows.append([InlineKeyboardButton(text="❌ Удалить статус", callback_data="st:delete")])
    if await has_permission(callback.from_user.id, "can_grant_statuses") or \
       await has_permission(callback.from_user.id, "can_manage_statuses"):
        rows.append([InlineKeyboardButton(text="🎁 Выдать статус игроку", callback_data="st:grant")])
        rows.append([InlineKeyboardButton(text="🚫 Снять статус у игрока", callback_data="st:revoke")])
    rows.append([InlineKeyboardButton(text="📋 Список статусов", callback_data="st:list")])
    rows.append([InlineKeyboardButton(text="🔙 В меню", callback_data="admin:menu")])
    await callback.message.edit_text(
        "🎖️ УПРАВЛЕНИЕ СТАТУСАМИ\n\nВыбери действие:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows)
    )


@router.callback_query(F.data == "st:list")
async def statuses_list(callback: CallbackQuery):
    await callback.answer()
    statuses = await get_all_statuses()
    if not statuses:
        await callback.message.edit_text("Статусы пока не созданы.", reply_markup=None)
        return
    lines = ["🎖️ ВСЕ СТАТУСЫ:\n"]
    for s in statuses:
        tag = f" ({s['access_tag']})" if s['access_tag'] else ""
        lines.append(f"• {s['name']}{tag} — уровень {s['sort_order']}")
        if s['description']:
            lines.append(f"    — {s['description']}")
    from keyboards.keyboards import back_to_main
    await callback.message.edit_text("\n".join(lines), reply_markup=back_to_main())


@router.callback_query(F.data == "st:create")
async def status_create_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_statuses"):
        await callback.message.answer("❌ Нет прав.")
        return
    await state.set_state(AdminStatuses.name)
    await callback.message.answer(
        "🎖️ Создание статуса. Шаг 1/3\nВведи название (например: «Ветеран», «VIP»):",
        reply_markup=cancel_keyboard()
    )


@router.message(AdminStatuses.name)
async def status_create_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await state.set_state(AdminStatuses.tag)
    await message.answer(
        "Шаг 2/3 — Ключ доступа (латиницей, без пробелов, например v i p — напиши как VIP):\n"
        "Этот ключ используется, чтобы привязывать товары/здания. Или «-» если не нужен:",
        reply_markup=cancel_keyboard()
    )


@router.message(AdminStatuses.tag)
async def status_create_tag(message: Message, state: FSMContext):
    text = message.text.strip()
    if text == "-":
        await state.update_data(tag=None)
    else:
        tag = "".join(c for c in text if c.isalnum())
        await state.update_data(tag=tag or None)
    await state.set_state(AdminStatuses.level)
    await message.answer(
        "Шаг 3/4 — Уровень статуса (целое число от 0 до 20, макс. 20).\n"
        "Чем больше, тем сильнее статус. Уровень открывает весь доступ более слабых статусов.\n"
        "Базовый «Пилот» — 0, «Турист» — -10. Введи уровень (например: 5):",
        reply_markup=cancel_keyboard()
    )


@router.message(AdminStatuses.level)
async def status_create_level(message: Message, state: FSMContext):
    text = message.text.strip()
    try:
        sort_order = int(text)
    except ValueError:
        await message.answer("❌ Введи целое число (уровень статуса):")
        return
    if not 0 <= sort_order <= 20:
        await message.answer("❌ Уровень должен быть от 0 до 20 (макс. сейчас 20):")
        return
    await state.update_data(sort_order=sort_order)
    await state.set_state(AdminStatuses.desc)
    await message.answer("Шаг 4/4 — Описание (или «-» если нет):", reply_markup=cancel_keyboard())


@router.message(AdminStatuses.desc)
async def status_create_desc(message: Message, state: FSMContext):
    text = message.text.strip()
    data = await state.get_data()
    desc = None if text == "-" else text
    ok, res = await create_status(data['name'], data.get('tag'), desc, message.from_user.id,
                                  sort_order=data.get('sort_order', 0))
    await state.clear()
    if ok:
        await log_action(message.from_user.id, 'create_status', None,
                         f"status={data['name']} id={res} level={data.get('sort_order',0)}")
        await message.answer(f"✅ Статус «{data['name']}» создан (уровень {data.get('sort_order',0)})!")
    else:
        await message.answer(f"❌ {res}")


@router.callback_query(F.data == "st:delete")
async def status_delete_menu(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_statuses"):
        await callback.message.answer("❌ Нет прав.")
        return
    statuses = await get_all_statuses()
    if not statuses:
        await callback.message.answer("Статусы не созданы.")
        return
    rows = []
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    for s in statuses:
        rows.append([InlineKeyboardButton(text=f"Удалить: {s['name']}", callback_data=f"st_del:{s['id']}")])
    rows.append([InlineKeyboardButton(text="🔙 Назад", callback_data="admin:statuses")])
    await callback.message.edit_text("Выбери статус для удаления:",
                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))


@router.callback_query(F.data.startswith("st_del:"))
async def status_delete_cb(callback: CallbackQuery):
    await callback.answer()
    status_id = int(callback.data.split(":")[1])
    s = await get_status(status_id)
    await delete_status(status_id)
    await log_action(callback.from_user.id, 'delete_status', None, f"status_id={status_id}")
    await callback.message.answer(f"🗑 Статус «{s['name']}» удалён." if s else "Удалено.")


@router.callback_query(F.data == "st:grant")
async def status_grant_target(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(AdminStatuses.target)
    markup = await pilot_picker_markup("status_pick")
    await callback.message.answer("Выбери пилота для выдачи/снятия статуса:", reply_markup=markup)


@router.callback_query(F.data == "st:revoke")
async def status_revoke_target(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(AdminStatuses.target)
    markup = await pilot_picker_markup("status_revoke")
    await callback.message.answer("У кого снять статус? Выбери пилота:", reply_markup=markup)


@router.message(AdminStatuses.target)
async def status_grant_target_msg(message: Message, state: FSMContext):
    target = await find_user(message.text)
    if not target:
        await message.answer("❌ Игрок не найден. Попробуй ещё раз:")
        return
    await state.update_data(target_id=target['user_id'], target_name=target['first_name'] if 'first_name' in target.keys() else '')
    await state.set_state(AdminStatuses.status_pick)

    have = await get_user_statuses(target['user_id'])
    have_names = ", ".join(s['name'] for s in have) if have else "нет"

    statuses = await get_all_statuses()
    if not statuses:
        await message.answer("❌ Сначала создай хотя бы один статус.")
        await state.clear()
        return

    rows = []
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    for s in statuses:
        rows.append([InlineKeyboardButton(text=f"{s['name']}", callback_data=f"st_pick:{s['id']}")])
    await message.answer(
        f"Игрок: {target['first_name'] if 'first_name' in target.keys() else ''}\nТекущие статусы: {have_names}\n\nВыбери статус:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows)
    )


@router.callback_query(F.data.startswith("st_rev:"))
async def status_revoke_pick(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    status_id = int(callback.data.split(":")[1])
    data = await state.get_data()
    target_id = data.get('target_id')
    if not target_id:
        await callback.message.answer("❌ Сессия устарела, начни заново.")
        return
    s = await get_status(status_id)
    await revoke_status(target_id, status_id)
    await log_action(callback.from_user.id, 'revoke_status', target_id, f"status={s['name']}" if s else f"status_id={status_id}")
    await state.clear()
    await callback.message.answer(f"🚫 Статус «{s['name']}» снят с игрока." if s else "Статус снят.")


@router.callback_query(F.data.startswith("st_pick:"))
async def status_grant_pick(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    status_id = int(callback.data.split(":")[1])
    await state.update_data(status_id=status_id)
    await state.set_state(AdminStatuses.grant_action)
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    await callback.message.edit_text(
        "Что сделать?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Выдать статус", callback_data="st_op:grant")],
            [InlineKeyboardButton(text="Снять статус", callback_data="st_op:revoke")],
        ])
    )


@router.callback_query(F.data.startswith("st_op:"))
async def status_grant_apply(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    op = callback.data.split(":")[1]
    data = await state.get_data()
    target_id = data['target_id']
    status_id = data['status_id']
    s = await get_status(status_id)
    admin = callback.from_user.id

    if op == "grant":
        ok, msg = await grant_status(target_id, status_id, admin)
        await log_action(admin, 'grant_status', target_id, f"status={s['name']}")
    else:
        await revoke_status(target_id, status_id)
        ok, msg = True, "Статус снят"
        await log_action(admin, 'revoke_status', target_id, f"status={s['name']}")

    await state.clear()
    await callback.message.answer(("✅ " if ok else "❌ ") + msg)


# ============ НАГРАДЫ ============

@router.callback_query(F.data == "admin:awards")
async def admin_awards(callback: CallbackQuery):
    await callback.answer()
    if not (await has_permission(callback.from_user.id, "can_manage_awards")
            or await has_permission(callback.from_user.id, "can_grant_awards")):
        await callback.message.answer("❌ Нет прав для управления наградами.")
        return

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    rows = []
    if await has_permission(callback.from_user.id, "can_manage_awards"):
        rows.append([InlineKeyboardButton(text="➕ Создать награду", callback_data="aw:create")])
        rows.append([InlineKeyboardButton(text="✏️ Редактировать награду", callback_data="aw:edit")])
        rows.append([InlineKeyboardButton(text="❌ Удалить награду", callback_data="aw:delete")])
    if await has_permission(callback.from_user.id, "can_grant_awards") or \
       await has_permission(callback.from_user.id, "can_manage_awards"):
        rows.append([InlineKeyboardButton(text="🎁 Выдать награду игроку", callback_data="aw:grant")])
        rows.append([InlineKeyboardButton(text="🗑 Снять награду у игрока", callback_data="aw:revoke")])
    rows.append([InlineKeyboardButton(text="📋 Список наград", callback_data="aw:list")])
    rows.append([InlineKeyboardButton(text="🔙 В меню", callback_data="admin:menu")])
    await callback.message.edit_text(
        "🏅 УПРАВЛЕНИЕ НАГРАДАМИ\n\nВыбери действие:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows)
    )


@router.callback_query(F.data == "aw:list")
async def awards_list(callback: CallbackQuery):
    await callback.answer()
    awards = await get_all_awards()
    if not awards:
        await callback.message.edit_text("Награды пока не созданы.", reply_markup=None)
        return
    lines = ["🏅 ВСЕ НАГРАДЫ:\n"]
    for a in awards:
        emoji = a['emoji'] or '🏅'
        lines.append(f"{emoji} {a['name']}")
        if a['description']:
            lines.append(f"    — {a['description']}")
        lines.append("")
    from keyboards.keyboards import back_to_main
    await callback.message.edit_text("\n".join(lines), reply_markup=back_to_main())


@router.callback_query(F.data == "aw:create")
async def award_create_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_awards"):
        await callback.message.answer("❌ Нет прав.")
        return
    await state.set_state(AdminAwards.name)
    await callback.message.answer(
        "🏅 Создание награды. Шаг 1/3\nВведи название (например: «За отвагу», «Герой Нордхайма»):",
        reply_markup=cancel_keyboard()
    )


@router.message(AdminAwards.name)
async def award_create_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await state.set_state(AdminAwards.desc)
    await message.answer("Шаг 2/3 — Описание награды (или «-» если нет):",
                         reply_markup=cancel_keyboard())


@router.message(AdminAwards.desc)
async def award_create_desc(message: Message, state: FSMContext):
    text = message.text.strip()
    await state.update_data(desc=None if text == "-" else text)
    await state.set_state(AdminAwards.emoji)
    await message.answer("Шаг 3/3 — Эмодзи награды (один символ, например 🏅, ⭐, 🎖️). Или «-» для 🏅:",
                         reply_markup=cancel_keyboard())


@router.message(AdminAwards.emoji)
async def award_create_emoji(message: Message, state: FSMContext):
    text = message.text.strip()
    emoji = text if text and text != "-" else "🏅"
    data = await state.get_data()
    ok, res = await create_award(data['name'], data.get('desc'), emoji, message.from_user.id)
    await state.clear()
    if ok:
        await log_action(message.from_user.id, 'create_award', None,
                         f"award={data['name']} id={res}")
        await message.answer(f"✅ Награда «{emoji} {data['name']}» создана!")
    else:
        await message.answer(f"❌ {res}")


@router.callback_query(F.data == "aw:delete")
async def award_delete_menu(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_awards"):
        await callback.message.answer("❌ Нет прав.")
        return
    awards = await get_all_awards()
    if not awards:
        await callback.message.answer("Награды не созданы.")
        return
    rows = []
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    for a in awards:
        emoji = a['emoji'] or '🏅'
        rows.append([InlineKeyboardButton(text=f"Удалить: {emoji} {a['name']}",
                                          callback_data=f"aw_del:{a['id']}")])
    rows.append([InlineKeyboardButton(text="🔙 Назад", callback_data="admin:awards")])
    await callback.message.edit_text("Выбери награду для удаления:",
                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))


@router.callback_query(F.data.startswith("aw_del:"))
async def award_delete_cb(callback: CallbackQuery):
    await callback.answer()
    award_id = int(callback.data.split(":")[1])
    a = await get_award(award_id)
    await delete_award(award_id)
    await log_action(callback.from_user.id, 'delete_award', None, f"award_id={award_id}")
    await callback.message.answer(f"🗑 Награда «{a['name']}» удалена." if a else "Удалено.")


AWARD_EDIT_FIELDS = {
    "description": "📝 Описание",
    "image": "🖼 Картинка",
    "bonus_attack": "⚔️ Атака, %",
    "bonus_defense": "🛡️ Защита, %",
    "bonus_dodge": "💨 Уклонение, %",
    "bonus_fishing": "🎣 Рыбалка, %",
    "bonus_hp": "❤️ HP сверх 100",
}

AWARD_EDIT_PROMPTS = {
    "description": "Введи новое описание награды (или «-» чтобы очистить):",
    "image": "Пришли фото награды (или «-» чтобы убрать картинку):",
    "bonus_attack": "Введи бонус атаки в % (целое число, например 5 или 0):",
    "bonus_defense": "Введи бонус защиты в % (целое число):",
    "bonus_dodge": "Введи бонус уклонения в % (целое число):",
    "bonus_fishing": "Введи бонус шанса рыбалки в % (целое число):",
    "bonus_hp": "Введи бонус HP сверх базовых 100 (целое число):",
}


def _award_edit_card(award) -> str:
    if not award:
        return "❌ Награда не найдена."
    emoji = award['emoji'] or '🏅'
    lines = [
        f"{emoji} {award['name']} (id {award['id']})\n",
        f"📝 {award['description'] or '—'}",
        f"🖼 Картинка: {'есть' if award['image'] else 'нет'}",
        "",
        "Бонусы (в %):",
        f"⚔️ Атака: {award['bonus_attack'] or 0}",
        f"🛡️ Защита: {award['bonus_defense'] or 0}",
        f"💨 Уклонение: {award['bonus_dodge'] or 0}",
        f"🎣 Рыбалка: {award['bonus_fishing'] or 0}",
        f"❤️ HP: {award['bonus_hp'] or 0}",
    ]
    return "\n".join(lines)


async def _award_edit_menu(message, award):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
    aid = award['id']
    rows = [
        [InlineKeyboardButton(text="🔁 Обновить", callback_data=f"aw_edit:{aid}")],
    ]
    for field, label in AWARD_EDIT_FIELDS.items():
        rows.append([InlineKeyboardButton(text=label, callback_data=f"aw_ei:{aid}:{field}")])
    rows.append([InlineKeyboardButton(text="🔙 К списку", callback_data="aw:edit")])
    rows.append([InlineKeyboardButton(text="🔙 В меню", callback_data="admin:awards")])
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    if award['image']:
        try:
            if getattr(message, 'message', None):
                await message.message.edit_media(
                    InputMediaPhoto(media=award['image'], caption=_award_edit_card(award)),
                    reply_markup=markup
                )
            else:
                await message.edit_media(
                    InputMediaPhoto(media=award['image'], caption=_award_edit_card(award)),
                    reply_markup=markup
                )
            return
        except Exception:
            pass
    if getattr(message, 'message', None):
        await message.message.edit_text(_award_edit_card(award), reply_markup=markup)
    else:
        await message.edit_text(_award_edit_card(award), reply_markup=markup)


@router.callback_query(F.data == "aw:edit")
async def award_edit_list(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_awards"):
        await callback.message.answer("❌ Нет прав.")
        return
    awards = await get_all_awards()
    if not awards:
        await callback.message.answer("Награды не созданы.")
        return
    rows = []
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    for a in awards:
        emoji = a['emoji'] or '🏅'
        rows.append([InlineKeyboardButton(text=f"{emoji} {a['name']}", callback_data=f"aw_edit:{a['id']}")])
    rows.append([InlineKeyboardButton(text="🔙 В меню", callback_data="admin:awards")])
    await callback.message.edit_text("Выбери награду для редактирования:",
                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))


@router.callback_query(F.data.startswith("aw_edit:"))
async def award_edit_open(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_awards"):
        await callback.message.answer("❌ Нет прав.")
        return
    award_id = int(callback.data.split(":")[1])
    award = await get_award(award_id)
    await _award_edit_menu(callback.message, award)


@router.callback_query(F.data.startswith("aw_ei:"))
async def award_edit_field_pick(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_awards"):
        await callback.message.answer("❌ Нет прав.")
        return
    _, award_id, field = callback.data.split(":", 2)
    if field not in AWARD_EDIT_FIELDS:
        return
    await state.update_data(edit_award_id=int(award_id), edit_field=field)
    await state.set_state(AdminAwards.edit_value)
    await callback.message.answer(AWARD_EDIT_PROMPTS[field], reply_markup=cancel_keyboard())


@router.message(AdminAwards.edit_value)
async def award_edit_value(message: Message, state: FSMContext):
    if not await has_permission(message.from_user.id, "can_manage_awards"):
        await message.answer("❌ Нет прав.")
        await state.clear()
        return
    data = await state.get_data()
    award_id = data.get('edit_award_id')
    field = data.get('edit_field')
    if not award_id or field not in AWARD_EDIT_FIELDS:
        await state.clear()
        await message.answer("❌ Сессия устарела, начни заново.")
        return
    text = (message.text or "").strip()
    value = None
    if field == "image":
        if message.photo:
            value = message.photo[-1].file_id
        elif text in ("-", ""):
            value = None
        else:
            await message.answer("❌ Пришли именно фото, либо «-» чтобы убрать картинку:")
            return
    elif field == "description":
        if text and text != "-":
            value = text[:300]
        else:
            value = None
    else:
        if text in ("-", ""):
            value = None
        else:
            try:
                parsed = int(text)
            except ValueError:
                await message.answer("❌ Введи целое число (например 5) или «-» для нуля:")
                return
            value = max(-100, min(1000, parsed))
    await update_award(award_id, **{field: value})
    await log_action(message.from_user.id, 'edit_award', None,
                     f"award_id={award_id} field={field} value={value}")
    await state.clear()
    award = await get_award(award_id)
    await message.answer(
        f"✅ {AWARD_EDIT_FIELDS[field]} награды обновлён.\n\n{_award_edit_card(award)}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="🔁 Продолжить редактировать",
                                 callback_data=f"aw_edit:{award_id}")
        ]])
    )


@router.callback_query(F.data == "aw:grant")
async def award_grant_target(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(AdminAwards.target)
    markup = await pilot_picker_markup("awgrant")
    await callback.message.answer("Кому выдать награду? Выбери пилота:", reply_markup=markup)


@router.message(AdminAwards.target)
async def award_grant_target_msg(message: Message, state: FSMContext):
    target = await find_user(message.text)
    if not target:
        await message.answer("❌ Игрок не найден. Попробуй ещё раз:")
        return
    await state.update_data(target_id=target['user_id'], target_name=target['first_name'] if 'first_name' in target.keys() else '')
    awards = await get_all_awards()
    if not awards:
        await message.answer("❌ Сначала создай хотя бы одну награду.")
        await state.clear()
        return
    rows = []
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    for a in awards:
        emoji = a['emoji'] or '🏅'
        rows.append([InlineKeyboardButton(text=f"{emoji} {a['name']}",
                                          callback_data=f"aw_pick:{a['id']}")])
    await message.answer(
        f"Игрок: {target['first_name'] if 'first_name' in target.keys() else ''}\n\nВыбери награду:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows)
    )


@router.callback_query(F.data.startswith("aw_pick:"))
async def award_grant_pick(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    award_id = int(callback.data.split(":")[1])
    await state.update_data(award_id=award_id)
    await state.set_state(AdminAwards.comment)
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    await callback.message.edit_text(
        "Напиши комментарий к награде (или «-» если без него):",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬜ Пропустить", callback_data="aw_comment:skip")],
            [InlineKeyboardButton(text="🔙 Отмена", callback_data="admin:awards")],
        ])
    )


@router.callback_query(F.data == "aw_comment:skip")
async def award_grant_skip(callback: CallbackQuery, state: FSMContext):
    await award_grant_finish(callback, state, None)


@router.message(AdminAwards.comment)
async def award_grant_comment(message: Message, state: FSMContext):
    text = message.text.strip()
    comment = None if text == "-" else text
    data = await state.get_data()
    target_id = data['target_id']
    award_id = data['award_id']
    a = await get_award(award_id)
    admin = message.from_user.id
    ok, msg = await grant_award(target_id, award_id, admin, comment)
    await log_action(admin, 'grant_award', target_id, f"award={a['name']}" if a else f"award_id={award_id}")
    await state.clear()
    await message.answer(("✅ " if ok else "❌ ") + msg)
    if ok and a:
        from utils.notify import notify as notify_group
        await notify_group(
            message.bot,
            f"🏅 {a['emoji'] or '🏅'} {a['name']} выдана игроку {data.get('target_name', '') or target_id}"
            + (f"\n💬 {comment}" if comment else ""),
            user_id=target_id
        )


async def award_grant_finish(callback: CallbackQuery, state: FSMContext, comment):
    data = await state.get_data()
    target_id = data.get('target_id')
    award_id = data.get('award_id')
    if not target_id or not award_id:
        await callback.message.answer("❌ Сессия устарела, начни заново.")
        await state.clear()
        return
    a = await get_award(award_id)
    ok, msg = await grant_award(target_id, award_id, callback.from_user.id, comment)
    await log_action(callback.from_user.id, 'grant_award', target_id,
                     f"award={a['name']}" if a else f"award_id={award_id}")
    await state.clear()
    await callback.message.answer(("✅ " if ok else "❌ ") + msg)
    if ok and a:
        from utils.notify import notify as notify_group
        await notify_group(
            callback.message.bot,
            f"🏅 {a['emoji'] or '🏅'} {a['name']} выдана игроку {data.get('target_name', '') or target_id}"
            + (f"\n💬 {comment}" if comment else ""),
            user_id=target_id
        )


@router.callback_query(F.data == "aw:revoke")
async def award_revoke_pick_user(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(AdminAwards.award_pick)
    markup = await pilot_picker_markup("awrevoke")
    await callback.message.answer("У кого снять награду? Выбери пилота:", reply_markup=markup)


@router.callback_query(F.data.startswith("awr_grant:"))
async def award_revoke_apply(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    grant_id = int(callback.data.split(":")[1])
    await revoke_award(grant_id)
    await log_action(callback.from_user.id, 'revoke_award', None, f"grant_id={grant_id}")
    await state.clear()
    await callback.message.answer("🗑 Награда снята.")


# ============ ОТЧЁТЫ ============

@router.callback_query(F.data == "admin:reports")
async def admin_reports(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_view_reports"):
        await callback.message.answer("❌ Нет прав для просмотра отчётов.")
        return
    await show_pending_reports(callback.message)


async def show_pending_reports(message):
    reports = await get_pending_reports()
    if not reports:
        await message.answer("✅ В очереди нет отчётов на проверку.")
        return

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    report = reports[0]
    buttons = []
    if await has_permission(message.chat.id, "can_approve_reports"):
        buttons.append([
            InlineKeyboardButton(text="✅ Принять", callback_data=f"rep_ok:{report['id']}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"rep_no:{report['id']}"),
        ])
    buttons.append([InlineKeyboardButton(text="Следующий ▶️", callback_data="rep:next")])

    caption = (
        f"📋 ОТЧЁТ #{report['id']}\n\n"
        f"Пилот: {report['first_name']} (@{report['username']})\n"
        f"Войск за сутки: {report['troops_reported']}\n"
        f"К оплате (дельта): {report['credited_troops'] if ('credited_troops' in report.keys() and report['credited_troops'] is not None) else report['troops_reported']}\n"
        f"Всего войск: {report['total_troops'] if 'total_troops' in report.keys() else '—'}\n"
        f"Регион: {report['region'] or '—'}\n"
        f"Время: {report['created_at'][:16] if report['created_at'] else '—'}\n\n"
        f"Проверьте скриншот и примите решение:"
    )

    if 'screenshot_file_id' in report.keys() and report['screenshot_file_id']:
        await message.answer_photo(
            photo=report['screenshot_file_id'],
            caption=caption,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
        )
    else:
        await message.answer(
            caption,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
        )


@router.callback_query(F.data.startswith("rep_ok:"))
async def report_approve(callback: CallbackQuery, bot: Bot):
    await callback.answer()
    report_id = int(callback.data.split(":")[1])
    if not await has_permission(callback.from_user.id, "can_approve_reports"):
        await callback.message.answer("❌ Нет прав.")
        return
    report = await get_report_safe(report_id)
    # Новые отчёты начисляют дельту (может быть 0); старые (без дельты, NULL) — всю заявку.
    if 'credited_troops' in report.keys() and report['credited_troops'] is not None:
        troops = report['credited_troops']
    else:
        troops = report['troops_reported']
    pilot = await get_user(report['user_id'])
    amount = await approve_report(report_id, callback.from_user.id, troops)
    await log_action(callback.from_user.id, 'approve_report', report['user_id'], f"report={report_id}")
    await callback.message.answer(
        f"✅ Отчёт #{report_id} принят.\n"
        f"⚔️ К начислению: {amount} войск (выплата раз в сутки — в начале следующих суток)."
    )
    await show_pending_reports(callback.message)

    if pilot and amount >= NOTIFY_REPORT_MIN_TROOPS:
        await notify(bot, f"⚡ Пилот {await player_display(pilot)} сдал отчёт на {amount} очков!", pilot['user_id'])


@router.callback_query(F.data.startswith("rep_no:"))
async def report_reject(callback: CallbackQuery):
    await callback.answer()
    report_id = int(callback.data.split(":")[1])
    if not await has_permission(callback.from_user.id, "can_approve_reports"):
        await callback.message.answer("❌ Нет прав.")
        return
    report = await get_report_safe(report_id)
    await reject_report(report_id, callback.from_user.id)
    await log_action(callback.from_user.id, 'reject_report', report['user_id'], f"report={report_id}")
    await callback.message.answer("❌ Отчёт отклонён.")
    await show_pending_reports(callback.message)


@router.callback_query(F.data == "rep:next")
async def report_next(callback: CallbackQuery):
    await callback.answer()
    await show_pending_reports(callback.message)


async def get_report_safe(report_id: int):
    reports = await get_pending_reports()
    for r in reports:
        if r['id'] == report_id:
            return r
    return {"id": report_id, "user_id": 0, "troops_reported": 0}


# ============ СТАТИСТИКА РЕГИОНОВ ============

@router.callback_query(F.data == "admin:region_stats")
async def admin_region_stats(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_view_reports"):
        await callback.message.answer("❌ Нет прав для просмотра статистики.")
        return
    await show_region_stats(callback.message, refreshed=False, to_edit=callback)


@router.callback_query(F.data == "admin:region_stats_refresh")
async def admin_region_stats_refresh(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_view_reports"):
        await callback.message.answer("❌ Нет прав для просмотра статистики.")
        return
    await recompute_region_stats()
    await show_region_stats(callback.message, refreshed=True, to_edit=callback)


async def show_region_stats(message, refreshed: bool = False, to_edit: CallbackQuery = None):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    stats = await get_region_stats()
    text = "📊 СТАТИСТИКА ПО РЕГИОНАМ\n\n"
    if refreshed:
        text += "🔄 Пул обновлён.\n\n"
    elif stats:
        text += f"🗓 Данные актуальны на {stats[0]['computed_at'][:16] if stats[0] and stats[0]['computed_at'] else '—'}\n\n"
    else:
        text += "Данные ещё не рассчитаны.\n\n"

    if stats:
        for s in stats:
            region_label = f"Регион {s['region']}"
            if s['region'] == "0":
                region_label += " (Столица)"
            text += (f"🌍 {region_label}\n"
                     f"   🪖 Войска за 24ч: {s['troops_24h']}\n"
                     f"   👤 Активные пилоты (3 дн): {s['active_pilots_72h']}\n\n")
    else:
        text += "Нет данных. Регионы появятся после одобренных отчётов."

    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Обновить пул", callback_data="admin:region_stats_refresh")],
        [InlineKeyboardButton(text="👈 Назад", callback_data="admin:menu")],
    ])
    if to_edit is not None:
        await to_edit.message.edit_text(text, reply_markup=markup)
    else:
        await message.answer(text, reply_markup=markup)


# ============ ПОВЫШЕНИЕ В ЗВАНИИ ============

@router.callback_query(F.data == "admin:ranks")
async def admin_ranks(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_grant_troops"):
        await callback.message.answer("❌ Нет прав.")
        return

    players = await get_users_for_rank_promotion()
    if not players:
        await callback.message.answer(
            "📋 Нет игроков, готовых к повышению в звании.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад", callback_data="admin:menu")]
            ])
        )
        return

    buttons = []
    for p in players[:10]:
        name = p['first_name'] or p['username'] or str(p['user_id'])
        buttons.append([
            InlineKeyboardButton(
                text=f"⭐ {name} — {p['troops']} войск → {p['next_rank']}",
                callback_data=f"rank_promote:{p['user_id']}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="admin:menu")])

    await callback.message.edit_text(
        "⭐ Повышение в звании\n\n"
        "Игроки, чьи войска соответствуют званию выше Лейтенанта:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )


@router.callback_query(F.data.startswith("rank_promote:"))
async def rank_promote(callback: CallbackQuery, bot: Bot):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_grant_troops"):
        await callback.message.answer("❌ Нет прав.")
        return

    user_id = int(callback.data.split(":")[1])
    user = await get_user(user_id)
    if not user:
        await callback.message.answer("❌ Игрок не найден.")
        return

    from config import RANKS
    troops = user['troops']
    next_rank = None
    for rank_name, required in RANKS:
        if rank_name in ("Рекрут", "Рядовой", "Капрал", "Сержант", "Лейтенант"):
            continue
        if troops >= required:
            next_rank = rank_name
        else:
            break

    if not next_rank:
        await callback.message.answer("❌ У игрока нет достаточного количества войск.")
        return

    await promote_user_rank(user_id, next_rank, callback.from_user.id)
    name = user['first_name'] or user['username'] or str(user_id)
    await callback.message.answer(
        f"✅ {name} повышен до звания «{next_rank}» ({troops} войск)."
    )
    await notify(bot, f"⭐ Пилот {await player_display(user)} получил звание «{next_rank}»!", user['user_id'])
    await admin_ranks(callback)


# ============ ЛОГИ ============

@router.callback_query(F.data == "admin:logs")
async def admin_logs(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_view_logs"):
        await callback.message.answer("❌ Нет прав для просмотра логов.")
        return

    from database.db import get_db
    db = await get_db()
    cursor = await db.execute(
        "SELECT * FROM admin_logs ORDER BY id DESC LIMIT 15"
    )
    rows = await cursor.fetchall()

    if not rows:
        await callback.message.answer("Логи пока пусты.")
        return

    lines = []
    for r in rows:
        lines.append(
            f"#{r['id']} [{r['created_at'][:16] if r['created_at'] else ''}]\n"
            f"админ {r['admin_id']}: {r['action']}"
            + (f" -> {r['target_id']}" if r['target_id'] else "")
            + (f" ({r['details']})" if r['details'] else "")
        )
    await callback.message.answer("🧾 ПОСЛЕДНИЕ ДЕЙСТВИЯ АДМИНОВ:\n\n" + "\n\n".join(lines))


# ============ ОБЩИЙ ПОТОК АКТИВНОСТИ ============

ACTIVITY_FILTERS = {
    "all": ("Все", None),
    "shop": ("🛒 Покупки", "shop_purchase"),
    "sale": ("💰 Продажи", "shop_sale"),
    "fishing": ("🎣 Рыбалка", "fishing"),
    "dungeon": ("⛏ Данж", "dungeon%"),
    "kvp": ("🎖 КВП", "kvp%"),
    "trade": ("🔁 Обмен", "trade%"),
    "bank": ("🏦 Банк", "bank%"),
    "other": ("📦 Прочее", "other"),
}

ACTIVITY_OTHER_PATTERN = None
ACTIVITY_EXCLUDED = ("shop_purchase", "shop_sale", "fishing", "dungeon",
                     "kvp", "trade", "bank", "housing", "report", "equip",
                     "unequip", "item_use", "treasury_donate")


def _activity_markup(current: str = "all"):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    rows = []
    for key, (label, _) in ACTIVITY_FILTERS.items():
        mark = "•" if key == current else ""
        rows.append([InlineKeyboardButton(text=f"{mark}{label}", callback_data=f"act:{key}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _activity_lines(rows) -> str:
    out = []
    for e in rows:
        dt = e['created_at'][:16] if e['created_at'] else ""
        name = e['first_name'] or ""
        tag = f" @{e['username']}" if e['username'] else ""
        label = ""
        for key, (l, pat) in ACTIVITY_FILTERS.items():
            if key == "all" or key == "other":
                continue
            if pat and (e['action'] == pat or (pat.endswith('%') and e['action'].startswith(pat[:-1]))):
                label = l
                break
        out.append(f"[{dt}] {name}{tag} — {e['action']} {label}\n   {e['details'] or ''}")
    return "\n".join(out)


@router.callback_query(F.data.startswith("act:"))
async def admin_activity(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_view_logs"):
        await callback.message.answer("❌ Нет прав для просмотра логов.")
        return
    key = callback.data.split(":", 1)[1]
    if key not in ACTIVITY_FILTERS:
        key = "all"
    label, pat = ACTIVITY_FILTERS[key]
    rows = []
    if key == "all":
        rows = await get_recent_activity(30)
    elif key == "other":
        rows = await _activity_other()
    elif pat and pat.endswith('%'):
        rows = await get_activity_like(pat, 30)
    elif pat:
        rows = await get_activity_by_action(pat, 30)
    if not rows:
        await callback.message.answer(
            f"📊 АКТИВНОСТЬ ИГРОКОВ — {label}\n\n(пока пусто)",
            reply_markup=_activity_markup(key),
        )
        return
    text = f"📊 АКТИВНОСТЬ ИГРОКОВ — {label}\n\n" + _activity_lines(rows)
    await callback.message.answer(text[:4000], reply_markup=_activity_markup(key))


async def _activity_other():
    from database.db import get_db
    db = await get_db()
    ph = ",".join("?" for _ in ACTIVITY_EXCLUDED)
    cursor = await db.execute(
        f"SELECT a.id, a.user_id, a.action, a.details, a.created_at, "
        f"u.username, u.first_name "
        f"FROM activity_log a LEFT JOIN users u ON u.user_id = a.user_id "
        f"WHERE a.action NOT IN ({ph}) "
        f"AND a.action NOT LIKE 'dungeon%' AND a.action NOT LIKE 'kvp%' "
        f"AND a.action NOT LIKE 'trade%' AND a.action NOT LIKE 'bank%' "
        f"ORDER BY a.id DESC LIMIT 30",
        ACTIVITY_EXCLUDED
    )
    return await cursor.fetchall()


# ============ ОТМЕНА ============

@router.callback_query(F.data == "noop")
async def noop(callback: CallbackQuery):
    await callback.answer()


@router.callback_query(F.data == "back:main")
async def back_main_cb(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer()
    from keyboards.keyboards import main_menu_kb
    await callback.message.answer("Главное меню:", reply_markup=await main_menu_kb(callback.from_user.id))


@router.callback_query(F.data == "cancel")
async def cancel_cb(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    from keyboards.keyboards import main_menu_kb
    await callback.message.answer("Действие отменено.", reply_markup=await main_menu_kb(callback.from_user.id))


@router.message(F.text == "/cancel")
async def cancel_text(message: Message, state: FSMContext):
    await state.clear()
    from keyboards.keyboards import main_menu_kb
    await message.answer("Действие отменено.", reply_markup=await main_menu_kb(message.from_user.id))


# ============ СОСТОЯНИЯ ИГРОКОВ ============

@router.callback_query(F.data == "admin:states")
async def admin_states_menu(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_states"):
        await callback.message.answer("❌ Нет прав для управления состояниями.")
        return
    await state.set_state(AdminStates.target)
    markup = await pilot_picker_markup("state_target")
    await callback.message.answer(
        "🎭 УПРАВЛЕНИЕ СОСТОЯНИЯМИ\n\nВыбери пилота:",
        reply_markup=markup
    )


@router.message(AdminStates.target)
async def admin_states_target_text(message: Message, state: FSMContext):
    target = await find_user(message.text)
    if not target:
        await message.answer("❌ Игрок не найден. Попробуй ещё раз (или /cancel):")
        return
    await state.update_data(target_id=target['user_id'])
    await state.set_state(AdminStates.action)
    from utils.states import get_state_info
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    info = await get_state_info(target['user_id'])
    await message.answer(
        f"🎭 Игрок: {target['first_name'] if 'first_name' in target.keys() else ''} (@{target['username'] if 'username' in target.keys() else ''})\n"
        f"Текущее состояние: {info['name']}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🎭 Наложить состояние", callback_data="st_op:set")],
            [InlineKeyboardButton(text="✨ Снять состояние", callback_data="st_op:clear")],
        ])
    )


@router.callback_query(F.data.startswith("st_op:"))
async def admin_states_op(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    op = callback.data.split(":")[1]
    if op == "clear":
        data = await state.get_data()
        from utils.states import clear_state_of
        await clear_state_of(data['target_id'], caused_by=callback.from_user.id, reason="снято админом")
        await state.clear()
        await callback.message.answer("✨ Состояние снято. Игрок снова в норме.")
        return

    await state.set_state(AdminStates.state_key)
    from utils.states import STATE_CONF, state_keys
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    rows = []
    for key in state_keys():
        conf = STATE_CONF[key]
        rows.append([InlineKeyboardButton(
            text=f"{conf['emoji']} {conf['title']} ({conf['default_minutes']} мин.)",
            callback_data=f"st_key:{key}"
        )])
    # Отдельная строка — «снять» прямо отсюда
    rows.append([InlineKeyboardButton(text="✨ Снять состояние", callback_data="st_op:clear")])
    await callback.message.edit_text(
        "🎭 Выбери состояние:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows)
    )


@router.callback_query(F.data.startswith("st_key:"))
async def admin_states_key(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    key = callback.data.split(":")[1]
    await state.update_data(state_key=key)
    from utils.states import STATE_CONF
    conf = STATE_CONF[key]
    await state.set_state(AdminStates.minutes)
    await callback.message.answer(
        f"{conf['emoji']} Устанавливается состояние «{conf['title']}».\n"
        f"Срок действия в минутах (по умолчанию {conf['default_minutes']}):",
        reply_markup=cancel_keyboard()
    )


@router.message(AdminStates.minutes, F.text.regexp(r"^\d+$"))
async def admin_states_minutes(message: Message, state: FSMContext):
    data = await state.get_data()
    from utils.states import STATE_CONF, apply_state_to
    minutes = int(message.text)
    if minutes <= 0:
        await message.answer("❌ Введи число больше 0 (или /cancel).")
        return
    conf = STATE_CONF[data['state_key']]
    await apply_state_to(
        data['target_id'], data['state_key'],
        caused_by=message.from_user.id,
        minutes=minutes,
        reason=f"наложено админом на {minutes} мин.",
    )
    await state.clear()
    await message.answer(
        f"✅ {conf['emoji']} Игроку выдано состояние «{conf['title']}» на {minutes} мин."
    )


@router.message(AdminStates.minutes)
async def admin_states_minutes_bad(message: Message):
    await message.answer("❌ Введи число цифрой (минуты). Или /cancel.")


@router.callback_query(F.data == "admin:salaries")
async def admin_salaries(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_salaries"):
        await callback.message.answer("❌ Нет прав для управления зарплатами.")
        return
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    balance = await get_treasury_balance()
    salaried = await get_salaried_users()
    lines = []
    lines.append(f"🏛️ ЗАРПЛАТЫ ПИЛОТОВ\n\nКазна: {balance} {plural_nordmark(balance)}\n")
    if salaried:
        lines.append("💼 Получатели (еженедельно, в воскресенье):")
        for u in salaried:
            name = u['first_name'] or u['username'] or f"#{u['user_id']}"
            line = f"  • {name} — {u['salary']} {plural_nordmark(u['salary'])}"
            if u['salary_debt']:
                line += f"  (долг {u['salary_debt']} {plural_nordmark(u['salary_debt'])})"
            lines.append(line)
    else:
        lines.append("Получателей пока нет.")
    debts = await get_treasury_debts()
    if debts['total_debt']:
        lines.append(f"\n⚠️ Накопленный долг: {debts['total_debt']} "
                     f"{plural_nordmark(debts['total_debt'])}")
    if debts['shortfall']:
        lines.append(f"💡 На следующую выплату не хватает: {debts['shortfall']} "
                     f"{plural_nordmark(debts['shortfall'])}")
    lines.append("\nВыплата — один раз в неделю, в воскресенье.")
    await callback.message.edit_text(
        "\n".join(lines),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ Назначить/Изменить", callback_data="salary:choose")],
            [InlineKeyboardButton(text="💸 Выплатить сейчас", callback_data="salary:pay")],
            [InlineKeyboardButton(text="🔙 В финансы", callback_data="admin:finance")],
        ])
    )


@router.callback_query(F.data == "salary:choose")
async def salary_choose(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_salaries"):
        return
    markup = await pilot_picker_markup("salary_set")
    await callback.message.edit_text(
        "Выбери пилота, которому назначишь зарплату:",
        reply_markup=markup
    )


@router.callback_query(F.data == "salary:pay")
async def salary_pay(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_salaries"):
        return
    res = await pay_salaries()
    parts = []
    if res['paid']:
        parts.append(f"✅ Выплачено зарплат: {len(res['paid'])}")
        for uid, amt in res['paid']:
            u = await get_user(uid)
            name = (u['first_name'] if (u and 'first_name' in u.keys() and u['first_name'])
                    else (u['username'] if u else f"#{uid}"))
            parts.append(f"  • {name}: {amt} {plural_nordmark(amt)}")
    else:
        parts.append("ℹ️ Нет зарплат к выплате прямо сейчас.")
    if res['debt']:
        parts.append(
            f"\n⚠️ Задолженность (не хватило казны): {len(res['debt'])} "
            f"(всего {res['reserves']} {plural_nordmark(res['reserves'])}). "
            f"Долг копится и будет выплачен при пополнении."
        )
    await callback.message.edit_text("\n".join(parts))


@router.message(AdminSalary.amount)
async def admin_salary_amount(message: Message, state: FSMContext):
    text = message.text.strip()
    if text.lower() == "/cancel":
        await message.answer("Отменено.")
        await state.clear()
        return
    try:
        amount = int(text)
    except ValueError:
        await message.answer("❌ Введи сумму цифрой (или /cancel).")
        return
    if amount < 0:
        await message.answer("❌ Сумма не может быть отрицательной.")
        return
    data = await state.get_data()
    target_id = data.get('target_id')
    target_name = data.get('target_name', '')
    if not target_id:
        await message.answer("❌ Сессия не найдена, начни заново.")
        await state.clear()
        return
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    if amount == 0:
        await set_user_salary(target_id, 0, 7, message.from_user.id)
        await state.clear()
        await message.answer(f"✅ Зарплата снята с игрока: {target_name}.")
        return
    await state.update_data(amount=amount)
    await state.set_state(AdminSalary.period)
    await message.answer(
        f"💰 Сумма: {amount} {plural_nordmark(amount)}\n\n"
        f"Введи период выплаты в днях (по умолчанию 7):",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="7 дней", callback_data="salary_period:7")],
            [InlineKeyboardButton(text="30 дней", callback_data="salary_period:30")],
        ])
    )


@router.callback_query(AdminSalary.period, F.data.startswith("salary_period:"))
async def admin_salary_period_cb(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    period = int(callback.data.split(":")[1])
    data = await state.get_data()
    target_id = data.get('target_id')
    target_name = data.get('target_name', '')
    amount = data.get('amount')
    if not target_id or amount is None:
        await state.clear()
        await callback.message.answer("❌ Сессия не найдена, начни заново.")
        return
    await set_user_salary(target_id, amount, period, callback.from_user.id)
    await state.clear()
    await callback.message.edit_text(
        f"✅ Зарплата назначена: {target_name} — {amount} {plural_nordmark(amount)} / {period} дн."
    )


@router.message(AdminSalary.period)
async def admin_salary_period_text(message: Message, state: FSMContext):
    text = message.text.strip()
    try:
        period = int(text)
    except ValueError:
        await message.answer("❌ Введи период цифрой (дни) или выбери кнопку.")
        return
    if period <= 0:
        await message.answer("❌ Период должен быть больше 0.")
        return
    data = await state.get_data()
    target_id = data.get('target_id')
    target_name = data.get('target_name', '')
    amount = data.get('amount')
    if not target_id or amount is None:
        await state.clear()
        await message.answer("❌ Сессия не найдена, начни заново.")
        return
    await set_user_salary(target_id, amount, period, message.from_user.id)
    await state.clear()
    await message.answer(
        f"✅ Зарплата назначена: {target_name} — {amount} {plural_nordmark(amount)} / {period} дн."
    )

@router.callback_query(F.data == "admin:locations")
async def admin_locations(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        await callback.message.answer("❌ Нет прав для управления локациями.")
        return
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    locs = await get_all_locations()
    lines = ["📍 ЛОКАЦИИ ГОРОДА\n"]
    if locs:
        for l in locs:
            acc = await location_access_label(l['access_mode'], l['required_status'])
            lines.append(f"• {l['name']} — {acc}")
    else:
        lines.append("Локаций пока нет.")
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Создать локацию", callback_data="loc:create")],
        [InlineKeyboardButton(text="✏️ Редактировать доступ", callback_data="loc:edit_pick")],
        [InlineKeyboardButton(text="🏛 Редактировать здание", callback_data="loc:building_pick")],
        [InlineKeyboardButton(text="🔙 В меню", callback_data="admin:menu")],
    ])
    await callback.message.edit_text("\n".join(lines), reply_markup=kb)


@router.callback_query(F.data == "admin:dungeons")
async def admin_dungeons(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        await callback.message.answer("❌ Нет прав для управления подземельями.")
        return
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    dungeons = await get_all_dungeons()
    lines = ["🏰 ПОДЗЕМЕЛЬЯ\n"]
    rows = []
    if dungeons:
        for d in dungeons:
            lines.append(f"• {d['name']} — Этажей: {d['floors_count']}")
            rows.append([InlineKeyboardButton(text=f"🏚 {d['name']}", callback_data=f"dungeon:edit:{d['id']}")])
    else:
        lines.append("Подземелий пока нет.")
    rows.append([InlineKeyboardButton(text="🔙 В меню", callback_data="admin:menu")])
    await callback.message.edit_text("\n".join(lines), reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))


@router.callback_query(F.data.startswith("dungeon:edit:"))
async def dungeon_edit(callback: CallbackQuery, state: FSMContext):
    """Редактирование подземелья: входная картинка по времени суток."""
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    dungeon_id = int(callback.data.split(":")[2])
    dng = await get_dungeon(dungeon_id)
    if not dng:
        await callback.message.answer("❌ Подземелье не найдено.")
        return
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    await state.update_data(target_id=dungeon_id)
    await callback.message.edit_text(
        f"🏰 {dng['name']}\nЧто изменить во входе?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🖼 Картинки (вход + комнаты)", callback_data="dungeon:photos")],
            [InlineKeyboardButton(text="👾 Враги (HP/АТК/уклонение/яд/дропы)", callback_data="dungeon:enemies")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="admin:dungeons")],
        ])
    )


def _dungeon_photo_slots_text(dng):
    keys = dng.keys()
    filled = [DUNGEON_PHOTO_LABEL[k] for k in DUNGEON_PHOTO_KEYS
              if f"photo_{k}" in keys and dng[f"photo_{k}"]]
    return filled or ["нет"]


async def _dungeon_photos_pick_send(source, dungeon_id: int):
    """Показывает пикер картинок входа подземелья; source — CallbackQuery или Message."""
    dng = await get_dungeon(dungeon_id)
    if not dng:
        if isinstance(source, CallbackQuery):
            await source.message.edit_text("❌ Подземелье не найдено.")
        else:
            await source.answer("❌ Подземелье не найдено.")
        return
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keys = dng.keys()
    rows = []
    for k in DUNGEON_PHOTO_KEYS:
        mark = "✅" if f"photo_{k}" in keys and dng[f"photo_{k}"] else "—"
        rows.append([InlineKeyboardButton(
            text=f"{mark} {DUNGEON_PHOTO_LABEL[k]}",
            callback_data=f"dungeon:photo_set:{k}",
        )])
    rows.append([InlineKeyboardButton(text="🚫 Убрать все", callback_data="dungeon:photos:clear")])
    rows.append([InlineKeyboardButton(text="🔙 Назад", callback_data="dungeon:edit:" + str(dungeon_id))])
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    text = (
        f"🖼 Картинки «{dng['name']}».\n"
        f"Задано: {', '.join(_dungeon_photo_slots_text(dng))}\n\n"
        f"Слоты «🌊 Вода» и «🪢 Верёвка» — комнаты-препятствия К.В.П.\n"
        f"Нажми слот и отправь фото (или «-» чтобы убрать):"
    )
    if isinstance(source, CallbackQuery):
        await source.message.edit_text(text, reply_markup=kb)
    else:
        await source.answer(text, reply_markup=kb)


@router.callback_query(F.data == "dungeon:photos")
async def dungeon_photos_pick(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    data = await state.get_data()
    await _dungeon_photos_pick_send(callback, data['target_id'])


@router.callback_query(F.data.startswith("dungeon:photo_set:"))
async def dungeon_photo_set(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    tod = callback.data.split(":")[2]
    if tod not in DUNGEON_PHOTO_KEYS:
        return
    data = await state.get_data()
    await state.update_data(photo_tod=tod)
    await state.set_state(AdminDungeon.photo_tod)
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    await callback.message.answer(
        f"🖼 Отправь фото для «{DUNGEON_PHOTO_LABEL[tod]}» (или «-» для очистки этого слота).",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data="dungeon:photos")]
        ])
    )


@router.callback_query(F.data == "dungeon:photos:clear")
async def dungeon_photos_clear(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    data = await state.get_data()
    await update_dungeon_photos(data['target_id'], {k: None for k in DUNGEON_PHOTO_KEYS})
    await _dungeon_photos_pick_send(callback, data['target_id'])


@router.message(AdminDungeon.photo_tod)
async def dungeon_step_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    dungeon_id = data.get('target_id')
    if not dungeon_id:
        await state.clear()
        await message.answer("❌ Ошибка: нет подземелья в сессии.")
        return
    dng = await get_dungeon(dungeon_id)
    if not dng:
        await state.clear()
        await message.answer("❌ Подземелье не найдено.")
        return
    if message.photo:
        file_id = message.photo[-1].file_id
    elif message.text and message.text.strip() in ("-", "—"):
        file_id = None
    else:
        await message.answer("❌ Отправь именно фото (или «-» для очистки).")
        return
    photo_tod = data.get('photo_tod')
    if photo_tod and photo_tod in DUNGEON_PHOTO_KEYS:
        await update_dungeon_photos(dungeon_id, {photo_tod: file_id})
        await log_action(message.from_user.id, 'edit_dungeon', None,
                         f"dungeon_id={dungeon_id} photo_{photo_tod}={'file_id' if file_id else 'cleared'}")
        await state.update_data(photo_tod=None)
        await _dungeon_photos_pick_send(message, dungeon_id)
        return
    await state.clear()
    await message.answer("✅ Картинка входа подземелья обновлена.")


# ============ АДМИН: РЕДАКТОР ВРАГОВ ПОДЗЕМЕЛИЙ ============

ENEMY_FIELD_LABELS = {
    "hp": "💙 HP",
    "attack": "⚔️ АТК",
    "dodge": "💨 УКЛ (%)",
    "poison_chance": "☠️ Шанс яда (%)",
    "poison_dmg": "☠️ Урон яда (HP/ход)",
    "reward_nm": "💰 Награда (НМ)",
    "drops": "💼 Дропы",
    "description": "📝 Описание",
    "image": "🖼 Картинка",
}

ENEMY_INPUT_PROMPTS = {
    "hp": "Введи HP врага (целое число ≥ 0):",
    "attack": "Введи АТК врага (целое число ≥ 0):",
    "dodge": "Введи уклонение врага, % (0–100):",
    "poison_chance": "Введи шанс яда при попадании, % (0–100; 0 = нет):",
    "poison_dmg": "Введи урон яда за ход, HP (целое число ≥ 0):",
    "reward_nm": "Введи награду за победу, Нордмарок (целое число ≥ 0):",
    "drops": "Введи дропы — по одному на строку:\n"
             "Название | шанс % | кол-во\n\n"
             "Например:\n"
             "Хвост крысы | 15 | 1\n"
             "Осколок кристалла | 5 | 1\n\n"
             "«-» — убрать все дропы.\n\n"
             "💡 Удобнее пользоваться меню «💼 Дропы» в карточке врага — "
             "там можно добавлять предметы из игры или создавать новые.",
    "description": "Введи описание врага (или «-» чтобы очистить):",
    "image": "Отправь фото врага (Telegram-фото). Или «-» чтобы убрать картинку:",
}


def _parse_drops_text(text: str):
    """Разбирает текст дропов («Название | шанс% | кол-во»). На ошибку — None."""
    drops = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 2:
            return None
        name = parts[0]
        if not name:
            return None
        try:
            chance = int(parts[1].replace("%", ""))
        except ValueError:
            return None
        if not (0 <= chance <= 100):
            return None
        qty = 1
        if len(parts) > 2:
            try:
                qty = int(parts[2])
            except ValueError:
                return None
            if qty < 1:
                return None
        drops.append({"item": name, "chance": chance / 100.0, "qty": qty})
    return drops or []


async def _enemy_card_send(source, enemy_id: int, edit: bool = False):
    """Карточка врага с кнопками правки; source — CallbackQuery или Message."""
    enemy = await get_enemy(enemy_id)
    if not enemy:
        if hasattr(source, 'message'):
            await source.message.answer("❌ Враг не найден.")
        else:
            await source.answer("❌ Враг не найден.")
        return
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    drops = []
    if enemy.get('drops'):
        try:
            drops = json.loads(enemy['drops'])
        except (json.JSONDecodeError, TypeError):
            drops = []
    drop_lines = []
    if drops:
        for n, d in enumerate(drops):
            ch = d.get('chance', 0)
            ch_pct = f"{int(ch * 100)}%" if ch <= 1 else f"{int(ch)}%"
            qty = d.get('qty', 1)
            if d.get('item_id'):
                it = await get_item(int(d['item_id']))
                item_label = it['name'] if it else f"#{d['item_id']}"
            else:
                item_label = d.get('item', '?')
            drop_lines.append(f"   {n + 1}. {item_label} — {ch_pct}" +
                              (f" ×{qty}" if qty != 1 else ""))
    else:
        drop_lines.append("   — дропов нет")

    if enemy.get('poison_chance') and enemy.get('poison_dmg'):
        poison_line = (f"☠️ Яд: шанс {enemy['poison_chance']}%, "
                       f"урон −{enemy['poison_dmg']} HP/ход")
    else:
        poison_line = "☠️ Яда нет"

    photo_state = "есть" if enemy.get('image') else "нет"
    desc_line = f"📝 {enemy['description']}" if enemy.get('description') else "📝 описания нет"

    text = (
        f"👾 {enemy['name']}{'  👑 БОСС' if enemy.get('is_boss') else ''}\n"
        f"──────────────\n"
        f"💙 HP: {enemy['hp']}\n"
        f"⚔️ АТК: {enemy['attack']}\n"
        f"💨 УКЛ: {enemy.get('dodge', 0)}%\n"
        f"{poison_line}\n"
        f"💰 Награда: {enemy.get('reward_nm', 0)} НМ\n"
        f"🖼 Картинка: {photo_state}\n"
        f"{desc_line}\n"
        f"💼 Дропы:\n" + "\n".join(drop_lines) +
        f"\n\n⚠️ После правки стартовая синхронизация больше не перезапишет "
        f"характеристики этого врага.\nЧто изменить?"
    )

    rows = [
        [InlineKeyboardButton(text="💙 HP", callback_data="enemy_field:hp")],
        [InlineKeyboardButton(text="⚔️ АТК", callback_data="enemy_field:attack")],
        [InlineKeyboardButton(text="💨 УКЛ (%)", callback_data="enemy_field:dodge")],
        [InlineKeyboardButton(text="☠️ Шанс яда", callback_data="enemy_field:poison_chance")],
        [InlineKeyboardButton(text="☠️ Урон яда (HP/ход)", callback_data="enemy_field:poison_dmg")],
        [InlineKeyboardButton(text="💰 Награда (НМ)", callback_data="enemy_field:reward_nm")],
        [InlineKeyboardButton(text="📝 Описание", callback_data="enemy_field:description")],
        [InlineKeyboardButton(text="🖼 Картинка", callback_data="enemy_field:image")],
        [InlineKeyboardButton(text="💼 Дропы", callback_data=f"enemy_drops:{enemy_id}")],
        [InlineKeyboardButton(text="🔙 К списку врагов", callback_data="dungeon:enemies")],
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)

    if edit and hasattr(source, 'message'):
        try:
            await source.message.edit_text(text, reply_markup=kb)
            return
        except Exception:
            pass
    if hasattr(source, 'message'):
        await source.message.answer(text, reply_markup=kb)
    else:
        await source.answer(text, reply_markup=kb)


@router.callback_query(F.data == "dungeon:enemies")
async def dungeon_enemies_list(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    data = await state.get_data()
    dungeon_id = data.get('target_id')
    dng = await get_dungeon(dungeon_id) if dungeon_id else None
    if not dng:
        await callback.message.answer("❌ Подземелье не найдено.")
        return
    enemies = await get_dungeon_enemies(dungeon_id)
    lines = [f"👾 ВРАГИ «{dng['name']}»\n"]
    rows = []
    if enemies:
        for e in enemies:
            boss_mark = "👑 " if e.get('is_boss') else ""
            lines.append(f"• {boss_mark}{e['name']} — HP {e['hp']}, "
                         f"АТК {e['attack']}, УКЛ {e.get('dodge', 0)}%")
            rows.append([InlineKeyboardButton(
                text=f"{boss_mark}{e['name']}",
                callback_data=f"dungeon:enemy:{e['id']}",
            )])
    else:
        lines.append("Врагов пока нет.")
    lines.append("\nНажми на врага, чтобы настроить.")
    rows.append([InlineKeyboardButton(text="🔙 Назад", callback_data=f"dungeon:edit:{dungeon_id}")])
    await callback.message.edit_text("\n".join(lines),
                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))


@router.callback_query(F.data.startswith("dungeon:enemy:"))
async def dungeon_enemy_view(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    try:
        enemy_id = int(callback.data.split(":")[2])
    except (ValueError, IndexError):
        return
    await state.update_data(enemy_id=enemy_id)
    await _enemy_card_send(callback, enemy_id, edit=True)


@router.callback_query(F.data.startswith("enemy_field:"))
async def dungeon_enemy_field_pick(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    field = callback.data.split(":")[1]
    if field not in ENEMY_FIELD_LABELS:
        return
    data = await state.get_data()
    if not data.get('enemy_id'):
        await callback.message.answer("❌ Враг не выбран. Открой карточку врага заново.")
        return
    await state.update_data(enemy_field=field)
    await state.set_state(AdminDungeon.enemy_value)
    await callback.message.answer(ENEMY_INPUT_PROMPTS[field], reply_markup=cancel_keyboard())


@router.message(AdminDungeon.enemy_value)
async def dungeon_enemy_value(message: Message, state: FSMContext):
    data = await state.get_data()
    enemy_id = data.get('enemy_id')
    field = data.get('enemy_field')
    enemy = await get_enemy(enemy_id) if enemy_id else None
    if not enemy:
        await state.clear()
        await message.answer("❌ Враг не найден. Начни заново: админ → подземелья → враги.")
        return
    if field not in ENEMY_FIELD_LABELS:
        await state.clear()
        await message.answer("❌ Поле не распознано. Начни заново.")
        return

    text = (message.text or "").strip()
    parsed = None

    # Картинка: принимаем только фото (или «-» для очистки).
    if field == "image":
        if message.photo:
            parsed = message.photo[-1].file_id
        elif text in ("-", "—"):
            parsed = None
        else:
            await message.answer(f"❌ Отправь именно фото (или «-» для очистки).\n"
                                 f"{ENEMY_INPUT_PROMPTS[field]}",
                                 reply_markup=cancel_keyboard())
            return
        await update_enemy_fields(enemy_id, image=parsed)
        await log_action(message.from_user.id, 'edit_enemy', None,
                         f"enemy_id={enemy_id} image={'file_id' if parsed else 'cleared'}")
        await state.clear()
        await message.answer(f"✅ «{enemy['name']}»: 🖼 Картинка {'обновлена' if parsed else 'убрана'}.")
        await _enemy_card_send(message, enemy_id)
        return

    if field == "description":
        parsed = None if text in ("-", "—") else text
        await update_enemy_fields(enemy_id, description=parsed)
        await log_action(message.from_user.id, 'edit_enemy', None,
                         f"enemy_id={enemy_id} description={'cleared' if parsed is None else parsed[:200]}")
        await state.clear()
        await message.answer(f"✅ «{enemy['name']}»: 📝 Описание "
                             + ("очищено." if parsed is None else "обновлено."))
        await _enemy_card_send(message, enemy_id)
        return

    if field in ("hp", "attack", "poison_dmg", "reward_nm"):
        if text.isdigit():
            parsed = int(text)
    elif field in ("dodge", "poison_chance"):
        if text.isdigit():
            parsed = int(text)
    elif field == "drops":
        if text == "-":
            parsed = []
        else:
            parsed = _parse_drops_text(text)

    if field in ("hp", "attack", "poison_dmg", "reward_nm"):
        valid = parsed is not None and parsed >= 0
    elif field in ("dodge", "poison_chance"):
        valid = parsed is not None and 0 <= parsed <= 100
    else:
        valid = parsed is not None

    if not valid:
        await message.answer(f"❌ Неверный формат.\n{ENEMY_INPUT_PROMPTS[field]}",
                             reply_markup=cancel_keyboard())
        return

    await update_enemy_fields(enemy_id, **{field: parsed})
    await log_action(message.from_user.id, 'edit_enemy', None,
                     f"enemy_id={enemy_id} {field}={parsed}")
    await state.clear()

    if field == "drops":
        label = f"{len(parsed)} позиция(и)"
    elif field in ("dodge", "poison_chance"):
        label = f"{parsed}%"
    elif field == "poison_dmg":
        label = f"{parsed} HP/ход"
    elif field == "reward_nm":
        label = f"{parsed} НМ"
    else:
        label = str(parsed)

    await message.answer(f"✅ «{enemy['name']}»: {ENEMY_FIELD_LABELS[field]} = {label}.")
    await _enemy_card_send(message, enemy_id)


# ============ АДМИН: МЕНЕДЖЕР ДРОПОВ ВРАГА ============

DROPS_PER_PAGE = 8


async def _drop_label(d: dict) -> str:
    """Человечный заголовок дропа: имя предмета (или «#id») + шанс + кол-во."""
    if d.get('item_id'):
        it = await get_item(int(d['item_id']))
        label = it['name'] if it else f"#{d['item_id']}"
    else:
        label = d.get('item', '?')
    ch = d.get('chance', 0)
    ch_pct = f"{int(ch * 100)}%" if ch <= 1 else f"{int(ch)}%"
    qty = d.get('qty', 1)
    return f"{label} — {ch_pct}" + (f" ×{qty}" if qty != 1 else ""), label, ch_pct, qty


async def _drop_item_for(enemy_id: int, idx: int):
    """Возвращает (drops, drop, item) для дропа врага по индексу.

    Пропуски: drops — None, если враг/список недоступны; item — None, если
    предмет не найден (дроп по имени или битый item_id).
    """
    drops = await get_enemy_drops(enemy_id)
    if not drops or not 0 <= idx < len(drops):
        return None, None, None
    d = drops[idx]
    item = None
    if d.get('item_id'):
        item = await get_item(int(d['item_id']))
    if not item and d.get('item'):
        item = await get_item_by_name(d['item'])
    return drops, d, item


async def _drops_manager_send(source, enemy_id: int):
    """Экран менеджера дропов врага; source — CallbackQuery или Message."""
    enemy = await get_enemy(enemy_id)
    if not enemy:
        await source.answer("❌ Враг не найден.")
        return
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    drops = await get_enemy_drops(enemy_id)
    lines = [f"💼 ДРОПЫ «{enemy['name']}»\n"]
    rows = []
    if drops:
        for n, d in enumerate(drops):
            label, *_ = await _drop_label(d)
            lines.append(f"{n + 1}. {label}")
            rows.append([InlineKeyboardButton(
                text=f"⚙️ {n + 1}. {label}",
                callback_data=f"eddrop:{enemy_id}:{n}",
            )])
    else:
        lines.append("Дропов пока нет.")
    lines.append("\nДобавь предметы из игры или создай новый — он будет падать с врага.")
    rows.append([InlineKeyboardButton(text="➕ Предмет из игры",
                                      callback_data=f"editem_pick:{enemy_id}:0")])
    rows.append([InlineKeyboardButton(text="➕ Создать новый предмет",
                                      callback_data=f"editem_new:{enemy_id}")])
    rows.append([InlineKeyboardButton(text="🔙 В карточку врага",
                                      callback_data=f"dungeon:enemy:{enemy_id}")])
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    if hasattr(source, 'message') and source.message is not None:
        try:
            await source.message.edit_text("\n".join(lines), reply_markup=kb)
            return
        except Exception:
            pass
    if hasattr(source, 'message'):
        await source.message.answer("\n".join(lines), reply_markup=kb)
    else:
        await source.answer("\n".join(lines), reply_markup=kb)


@router.callback_query(F.data.startswith("enemy_drops:"))
async def enemy_drops_manager(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    try:
        enemy_id = int(callback.data.split(":")[1])
    except (ValueError, IndexError):
        return
    await state.update_data(enemy_id=enemy_id)
    await _drops_manager_send(callback, enemy_id)


@router.callback_query(F.data.startswith("editem_pick:"))
async def enemy_drop_pick_items(callback: CallbackQuery, state: FSMContext):
    """Выбор предмета из существующих в игре (постранично)."""
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    try:
        _, _, enemy_id_s, page_s = callback.data.split(":")
        enemy_id, page = int(enemy_id_s), int(page_s)
    except ValueError:
        return
    enemy = await get_enemy(enemy_id)
    if not enemy:
        await callback.message.answer("❌ Враг не найден.")
        return
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    all_items = await get_all_items()
    pages = max(1, (len(all_items) + DROPS_PER_PAGE - 1) // DROPS_PER_PAGE)
    page = max(0, min(page, pages - 1))
    chunk = all_items[page * DROPS_PER_PAGE:(page + 1) * DROPS_PER_PAGE]
    rows = []
    for it in chunk:
        emoji = RARITY_EMOJI.get(it['rarity'], "❔")
        cat = ITEM_CATEGORIES.get(it['category'], it['category'])
        rows.append([InlineKeyboardButton(
            text=f"{emoji} {it['name']} — {cat}",
            callback_data=f"editem_add:{enemy_id}:{it['id']}",
        )])
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="◀️", callback_data=f"editem_pick:{enemy_id}:{page - 1}"))
    nav.append(InlineKeyboardButton(text=f"{page + 1}/{pages}", callback_data="noop"))
    if page < pages - 1:
        nav.append(InlineKeyboardButton(text="▶️", callback_data=f"editem_pick:{enemy_id}:{page + 1}"))
    if nav:
        rows.append(nav)
    rows.append([InlineKeyboardButton(text="➕ Создать новый предмет",
                                      callback_data=f"editem_new:{enemy_id}")])
    rows.append([InlineKeyboardButton(text="🔙 К дропам", callback_data=f"enemy_drops:{enemy_id}")])
    await callback.message.edit_text(
        f"💼 ДРОПЫ «{enemy['name']}» → выбери предмет из игры:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows),
    )


@router.callback_query(F.data.startswith("editem_add:"))
async def enemy_drop_pick_item(callback: CallbackQuery, state: FSMContext):
    """Выбран предмет из игры: просим шанс выпадения."""
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    try:
        _, _, enemy_id_s, item_id_s = callback.data.split(":")
        enemy_id, item_id = int(enemy_id_s), int(item_id_s)
    except ValueError:
        return
    item = await get_item(item_id)
    enemy = await get_enemy(enemy_id)
    if not item or not enemy:
        await callback.message.answer("❌ Предмет или враг не найдены.")
        return
    await state.update_data(enemy_id=enemy_id, drop_item_id=item_id, drop_index=None)
    await state.set_state(AdminDungeon.drop_chance)
    await callback.message.answer(
        f"💼 Дроп «{item['name']}» у врага «{enemy['name']}».\n"
        f"Введи шанс выпадения, % (1–100):",
        reply_markup=cancel_keyboard(),
    )


@router.callback_query(F.data.startswith("editem_new:"))
async def enemy_drop_new_item(callback: CallbackQuery, state: FSMContext):
    """Создание нового предмета (полный мастер, как в магазине) для дропа врага."""
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    try:
        enemy_id = int(callback.data.split(":")[1])
    except (ValueError, IndexError):
        return
    enemy = await get_enemy(enemy_id)
    if not enemy:
        await callback.message.answer("❌ Враг не найден.")
        return
    await state.update_data(pending_enemy_id=enemy_id, pending_enemy_name=enemy['name'])
    await state.set_state(AdminAddItem.name)
    await callback.message.answer(
        f"💼 Создание предмета-дропа для врага «{enemy['name']}».\n\n"
        f"🛒 Шаг 1/10 — Введи название предмета (или /cancel):",
        reply_markup=cancel_keyboard(),
    )


@router.callback_query(F.data.startswith("eddrop:"))
async def enemy_drop_edit_menu(callback: CallbackQuery, state: FSMContext):
    """Подменю правки конкретного дропа (шанс / кол-во / предмет / удалить)."""
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    try:
        _, enemy_id_s, idx_s = callback.data.split(":")
        enemy_id, idx = int(enemy_id_s), int(idx_s)
    except ValueError:
        return
    enemy = await get_enemy(enemy_id)
    drops = await get_enemy_drops(enemy_id)
    if not enemy or not 0 <= idx < len(drops):
        await callback.message.answer("❌ Дроп не найден (список изменился).")
        return
    drops, d, item = await _drop_item_for(enemy_id, idx)
    if not drops or not 0 <= idx < len(drops):
        await callback.message.answer("❌ Дроп не найден.")
        return
    label, _, ch_pct, qty = await _drop_label(drops[idx])
    item_name = f"«{item['name']}»" if item else "—"
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"🎲 Шанс: {ch_pct}", callback_data=f"eddrop_set_ch:{enemy_id}:{idx}")],
        [InlineKeyboardButton(text=f"🔢 Кол-во: {qty}", callback_data=f"eddrop_set_q:{enemy_id}:{idx}")],
        [InlineKeyboardButton(text="🖼 Картинка предмета", callback_data=f"eddrop_photo:{enemy_id}:{idx}")],
        [InlineKeyboardButton(text="📜 Описание предмета", callback_data=f"eddrop_desc:{enemy_id}:{idx}")],
        [InlineKeyboardButton(text="⚙️ Характеристики предмета", callback_data=f"eddrop_stats:{enemy_id}:{idx}")],
        [InlineKeyboardButton(text="🗑 Удалить из дропов", callback_data=f"eddrop_del:{enemy_id}:{idx}")],
        [InlineKeyboardButton(text="🔙 К дропам", callback_data=f"enemy_drops:{enemy_id}")],
    ])
    await callback.message.edit_text(
        f"💼 Дроп: {label}\n"
        f"📦 Предмет: {item_name}\n"
        f"──────────────\n"
        f"Что изменить?",
        reply_markup=kb,
    )


@router.callback_query(F.data.startswith("eddrop_set_ch:"))
async def enemy_drop_set_chance(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    try:
        _, enemy_id_s, idx_s = callback.data.split(":")
        enemy_id, idx = int(enemy_id_s), int(idx_s)
    except ValueError:
        return
    await state.update_data(enemy_id=enemy_id, drop_index=idx, drop_item_id=None)
    await state.set_state(AdminDungeon.drop_chance)
    await callback.message.answer("🎲 Введи новый шанс выпадения, % (1–100):",
                                  reply_markup=cancel_keyboard())


@router.callback_query(F.data.startswith("eddrop_set_q:"))
async def enemy_drop_set_qty(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    try:
        _, enemy_id_s, idx_s = callback.data.split(":")
        enemy_id, idx = int(enemy_id_s), int(idx_s)
    except ValueError:
        return
    await state.update_data(enemy_id=enemy_id, drop_index=idx)
    await state.set_state(AdminDungeon.drop_qty)
    await callback.message.answer("🔢 Введи новое кол-во (целое число ≥ 1):",
                                  reply_markup=cancel_keyboard())


@router.callback_query(F.data.startswith("eddrop_del:"))
async def enemy_drop_delete(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    try:
        _, enemy_id_s, idx_s = callback.data.split(":")
        enemy_id, idx = int(enemy_id_s), int(idx_s)
    except ValueError:
        return
    if await remove_enemy_drop(enemy_id, idx):
        await log_action(callback.from_user.id, 'edit_enemy', None,
                         f"enemy_id={enemy_id} drop_{idx} removed")
    await _drops_manager_send(callback, enemy_id)


# ---------- Правка самого предмета дропа (картинка / описание / характеристики) ----------

@router.callback_query(F.data.startswith("eddrop_photo:"))
async def enemy_drop_item_photo(callback: CallbackQuery, state: FSMContext):
    """Запрос нового фото предмета дропа."""
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    try:
        _, enemy_id_s, idx_s = callback.data.split(":")
        enemy_id, idx = int(enemy_id_s), int(idx_s)
    except ValueError:
        return
    drops, _, item = await _drop_item_for(enemy_id, idx)
    if not drops or not item:
        await callback.message.answer("❌ Предмет дропа не найден. Удали дроп и добавь заново.")
        return
    await state.update_data(enemy_id=enemy_id, drop_index=idx)
    await state.set_state(AdminDungeon.drop_item_photo)
    await callback.message.answer(
        f"🖼 Фото предмета «{item['name']}» (сейчас: "
        f"{'есть' if item.get('photo_file_id') else 'нет'}).\n"
        f"Отправь фото — или «-», чтобы убрать картинку:",
        reply_markup=cancel_keyboard())


@router.message(AdminDungeon.drop_item_photo)
async def enemy_drop_item_photo_value(message: Message, state: FSMContext):
    data = await state.get_data()
    enemy_id = data.get('enemy_id')
    idx = data.get('drop_index')
    drops, _, item = await _drop_item_for(enemy_id, idx)
    if not drops or not item:
        await state.clear()
        await message.answer("❌ Предмет дропа не найден. Начни заново.")
        return
    text = (message.text or "").strip()
    if message.photo:
        parsed = message.photo[-1].file_id
    elif text in ("-", "—"):
        parsed = None
    else:
        await message.answer(
            f"❌ Отправь именно фото предмета «{item['name']}» (или «-» для очистки):",
            reply_markup=cancel_keyboard())
        return
    await update_item(item['id'], photo_file_id=parsed)
    await log_action(message.from_user.id, 'edit_item', None,
                     f"item_id={item['id']} photo={'file_id' if parsed else 'cleared'} "
                     f"(drop of enemy_id={enemy_id})")
    await state.clear()
    await message.answer(f"✅ Предмет «{item['name']}»: 🖼 Картинка "
                         + ("обновлена." if parsed else "убрана."))
    await _drops_manager_send(message, enemy_id)


@router.callback_query(F.data.startswith("eddrop_desc:"))
async def enemy_drop_item_desc(callback: CallbackQuery, state: FSMContext):
    """Запрос нового описания предмета дропа."""
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    try:
        _, enemy_id_s, idx_s = callback.data.split(":")
        enemy_id, idx = int(enemy_id_s), int(idx_s)
    except ValueError:
        return
    drops, _, item = await _drop_item_for(enemy_id, idx)
    if not drops or not item:
        await callback.message.answer("❌ Предмет дропа не найден. Удали дроп и добавь заново.")
        return
    await state.update_data(enemy_id=enemy_id, drop_index=idx)
    await state.set_state(AdminDungeon.drop_item_desc)
    await callback.message.answer(
        f"📜 Описание предмета «{item['name']}»:\n"
        f"Сейчас: {item.get('description') or '—'}\n\n"
        f"Введи новый текст (или «-», чтобы очистить):",
        reply_markup=cancel_keyboard())


@router.message(AdminDungeon.drop_item_desc)
async def enemy_drop_item_desc_value(message: Message, state: FSMContext):
    data = await state.get_data()
    enemy_id = data.get('enemy_id')
    idx = data.get('drop_index')
    drops, _, item = await _drop_item_for(enemy_id, idx)
    if not drops or not item:
        await state.clear()
        await message.answer("❌ Предмет дропа не найден. Начни заново.")
        return
    text = (message.text or "").strip()
    parsed = None if text in ("-", "—") else text
    await update_item(item['id'], description=parsed)
    await log_action(message.from_user.id, 'edit_item', None,
                     f"item_id={item['id']} description={'cleared' if parsed is None else parsed[:200]} "
                     f"(drop of enemy_id={enemy_id})")
    await state.clear()
    await message.answer(f"✅ Предмет «{item['name']}»: 📝 Описание "
                         + ("очищено." if parsed is None else "обновлено."))
    await _drops_manager_send(message, enemy_id)


DROP_ITEM_STAT_LABELS = {
    "damage": "⚔️ Урон",
    "heal": "❤️ Лечение",
    "armor": "🛡️ Броня",
    "ap_cost": "⚡ AP за использование",
    "weapon_effect_chance": "☠️ Шанс эффекта (%)",
    "weapon_effect_dmg": "☠️ Урон эффекта/ход",
}


@router.callback_query(F.data.startswith("eddrop_stats:"))
async def enemy_drop_item_stats_menu(callback: CallbackQuery, state: FSMContext):
    """Подменю выбора характеристики предмета дропа."""
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    try:
        _, enemy_id_s, idx_s = callback.data.split(":")
        enemy_id, idx = int(enemy_id_s), int(idx_s)
    except ValueError:
        return
    drops, _, item = await _drop_item_for(enemy_id, idx)
    if not drops or not item:
        await callback.message.answer("❌ Предмет дропа не найден. Удали дроп и добавь заново.")
        return
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    rows = []
    weff = item.get('weapon_effect')
    weff_label = WEAPON_EFFECT_LABELS.get(weff, "🚫 Без эффекта")
    rows.append([InlineKeyboardButton(
        text=f"☠️ Эффект оружия: {weff_label}",
        callback_data=f"eddrop_weff:{enemy_id}:{idx}",
    )])
    for field, label in DROP_ITEM_STAT_LABELS.items():
        cur = item.get(field) or 0
        rows.append([InlineKeyboardButton(
            text=f"{label}: {cur}",
            callback_data=f"eddrop_stat:{enemy_id}:{idx}:{field}",
        )])
    rows.append([InlineKeyboardButton(text="🔙 К дропу", callback_data=f"eddrop:{enemy_id}:{idx}")])
    states = " | ".join(f"{label}: {item.get(f) or 0}" for f, label in DROP_ITEM_STAT_LABELS.items())
    states += f" | Эффект: {weff_label}"
    await callback.message.edit_text(
        f"⚙️ Характеристики предмета «{item['name']}».\n"
        f"Текущие значения: {states}\n\n"
        f"Что изменить?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))


@router.callback_query(F.data.startswith("eddrop_stat:"))
async def enemy_drop_item_stat_pick(callback: CallbackQuery, state: FSMContext):
    """Выбрана характеристика предмета дропа — просим новое значение."""
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    try:
        _, enemy_id_s, idx_s, field = callback.data.split(":")
        enemy_id, idx = int(enemy_id_s), int(idx_s)
    except ValueError:
        return
    if field not in DROP_ITEM_STAT_LABELS:
        return
    drops, _, item = await _drop_item_for(enemy_id, idx)
    if not drops or not item:
        await callback.message.answer("❌ Предмет дропа не найден. Удали дроп и добавь заново.")
        return
    cur = item.get(field) or 0
    await state.update_data(enemy_id=enemy_id, drop_index=idx, drop_item_field=field)
    await state.set_state(AdminDungeon.drop_item_value)
    prompt = (f"{DROP_ITEM_STAT_LABELS[field]} предмета «{item['name']}».\n"
              f"Сейчас: {cur}.\n\n")
    if field == "weapon_effect_chance":
        prompt += "Введи шанс срабатывания при попадании, % (0–100; «-» = 0):"
    else:
        prompt += "Введи новое значение (целое число ≥ 0; «-» = 0):"
    await callback.message.answer(prompt, reply_markup=cancel_keyboard())


@router.message(AdminDungeon.drop_item_value)
async def enemy_drop_item_stat_value(message: Message, state: FSMContext):
    data = await state.get_data()
    enemy_id = data.get('enemy_id')
    idx = data.get('drop_index')
    field = data.get('drop_item_field')
    drops, _, item = await _drop_item_for(enemy_id, idx)
    if not drops or not item or field not in DROP_ITEM_STAT_LABELS:
        await state.clear()
        await message.answer("❌ Предмет дропа не найден. Начни заново.")
        return
    text = (message.text or "").strip()
    if text in ("-", "—"):
        parsed = 0
    elif text.isdigit():
        parsed = int(text)
    else:
        await message.answer(
            f"❌ Введи целое число ≥ 0 для {DROP_ITEM_STAT_LABELS[field]}"
            f" («{item['name']}»):",
            reply_markup=cancel_keyboard())
        return
    if field == "weapon_effect_chance" and not 0 <= parsed <= 100:
        await message.answer(f"❌ Шанс от 0 до 100 («{item['name']}»):",
                             reply_markup=cancel_keyboard())
        return
    await update_item(item['id'], **{field: parsed})
    await log_action(message.from_user.id, 'edit_item', None,
                     f"item_id={item['id']} {field}={parsed} (drop of enemy_id={enemy_id})")
    await state.clear()
    await message.answer(f"✅ Предмет «{item['name']}»: {DROP_ITEM_STAT_LABELS[field]} = {parsed}.")
    await _drops_manager_send(message, enemy_id)


@router.callback_query(F.data.startswith("eddrop_weff:"))
async def enemy_drop_item_weff_menu(callback: CallbackQuery, state: FSMContext):
    """Меню выбора особого эффекта оружия для предмета дропа."""
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    try:
        _, enemy_id_s, idx_s = callback.data.split(":")
        enemy_id, idx = int(enemy_id_s), int(idx_s)
    except ValueError:
        return
    drops, _, item = await _drop_item_for(enemy_id, idx)
    if not drops or not item:
        await callback.message.answer("❌ Предмет дропа не найден. Удали дроп и добавь заново.")
        return
    await callback.message.edit_text(
        f"☠️ Эффект оружия предмета «{item['name']}»:\n"
        f"При «Без эффекта» шанс и урон эффекта обнуляются.",
        reply_markup=weapon_effect_choice_markup(prefix=f"eddrop_weff_set:{enemy_id}:{idx}:")
    )


@router.callback_query(F.data.startswith("eddrop_weff_set:"))
async def enemy_drop_item_weff_set(callback: CallbackQuery, state: FSMContext):
    """Выбран тип эффекта оружия для предмета дропа — применяем сразу."""
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    try:
        _, enemy_id_s, idx_s, eff = callback.data.split(":")
        enemy_id, idx = int(enemy_id_s), int(idx_s)
    except ValueError:
        return
    if eff not in WEAPON_EFFECT_LABELS and eff != "none":
        return
    drops, _, item = await _drop_item_for(enemy_id, idx)
    if not drops or not item:
        await callback.message.answer("❌ Предмет дропа не найден. Удали дроп и добавь заново.")
        return
    if eff == "none":
        await update_item(item['id'], weapon_effect=None, weapon_effect_chance=0, weapon_effect_dmg=0)
        label = "🚫 Без эффекта"
    else:
        await update_item(item['id'], weapon_effect=eff)
        label = WEAPON_EFFECT_LABELS[eff]
    await log_action(callback.from_user.id, 'edit_item', None,
                     f"item_id={item['id']} weapon_effect={eff} (drop of enemy_id={enemy_id})")
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    await callback.message.edit_text(
        f"✅ Эффект оружия «{item['name']}»: {label}.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⚙️ Характеристики", callback_data=f"eddrop_stats:{enemy_id}:{idx}")],
            [InlineKeyboardButton(text="🔙 К дропу", callback_data=f"eddrop:{enemy_id}:{idx}")],
        ])
    )


@router.message(AdminDungeon.drop_chance)
async def enemy_drop_chance_value(message: Message, state: FSMContext):
    data = await state.get_data()
    text = (message.text or "").strip()
    if not text.isdigit() or not (1 <= int(text) <= 100):
        await message.answer("❌ Введи целое число от 1 до 100 (шанс в %):",
                             reply_markup=cancel_keyboard())
        return
    chance = int(text) / 100.0
    await state.update_data(drop_chance=chance)
    await state.set_state(AdminDungeon.drop_qty)
    await message.answer("🔢 Введи кол-во за выпадение (целое число ≥ 1):",
                         reply_markup=cancel_keyboard())


@router.message(AdminDungeon.drop_qty)
async def enemy_drop_qty_value(message: Message, state: FSMContext):
    data = await state.get_data()
    text = (message.text or "").strip()
    if not text.isdigit() or int(text) < 1:
        await message.answer("❌ Введи целое число ≥ 1:", reply_markup=cancel_keyboard())
        return
    qty = int(text)
    enemy_id = data.get('enemy_id')
    enemy = await get_enemy(enemy_id) if enemy_id else None
    if not enemy:
        await state.clear()
        await message.answer("❌ Враг не найден. Начни заново.")
        return
    chance = data.get('drop_chance', 0.1)
    idx = data.get('drop_index')
    if idx is not None:
        drops = await get_enemy_drops(enemy_id)
        if 0 <= idx < len(drops):
            drops[idx]['chance'] = chance
            drops[idx]['qty'] = qty
            await set_enemy_drops(enemy_id, drops)
    else:
        item_id = data.get('drop_item_id')
        if not item_id:
            await state.clear()
            await message.answer("❌ Предмет дропа не выбран. Начни заново.")
            return
        await add_enemy_drop(enemy_id, int(item_id), chance, qty)
    await log_action(message.from_user.id, 'edit_enemy', None,
                     f"enemy_id={enemy_id} drop chance={int(chance * 100)}% qty={qty}")
    await state.update_data(drop_chance=None, drop_qty=None, drop_index=None, drop_item_id=None)
    await state.set_state(None)
    await message.answer("✅ Дроп обновлён.")
    await _drops_manager_send(message, enemy_id)


# ============ АДМИН: РЕДАКТОР РЫБАЛКИ (пулы по водоёмам) ============

FISHING_FIELD_LABELS = {
    "day_weight": "☀️ Вес дня",
    "night_weight": "🌙 Вес ночи",
    "photo": "🖼 Фото рыбы",
    "sell_price": "💰 Цена продажи (НМ)",
}

FISHING_INPUT_PROMPTS = {
    "day_weight": "Введи относительный вес рыбы днём (целое число ≥ 0; 0 = не водится днём):",
    "night_weight": "Введи относительный вес рыбы ночью (целое число ≥ 0; 0 = не водится ночью):",
    "photo": "Отправь фото рыбы (Telegram-фото). Или отправь «-», чтобы убрать фото:",
    "sell_price": "Введи цену продажи рыбы скупщику, Нордмарок (целое число ≥ 0):",
}


async def _admin_fishing_card(source, wf_id: int, prefix: str = ""):
    """Карточка рыбы в водоёме с кнопками правки."""
    fish = await get_water_fish_row(wf_id)
    if not fish:
        await source.answer("❌ Рыба не найдена.")
        return
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    photo_state = "есть" if fish.get('photo_file_id') else "нет"
    kind = fish.get('kind') or 'fish'
    kind_label = "🐟 Рыба" if kind == "fish" else "📦 Ресурс (находка)"
    market_label = "✅ Можно" if fish.get('market_ok') else "🔒 Только скупщику"
    text = (
        f"{prefix}🐟 {fish['name']}\n"
        f"──────────────\n"
        f"{kind_label}\n"
        f"☀️ Вес дня: {fish['day_weight']}\n"
        f"🌙 Вес ночи: {fish['night_weight']}\n"
        f"🖼 Фото: {photo_state}\n"
        f"💰 Продажа: {fish['sell_price']} НМ\n"
        f"🏪 Рынок: {market_label}\n\n"
        f"⚠️ После правки стартовая синхронизация больше не перезапишет "
        f"настройки этой рыбы в водоёме.\nЧто изменить?"
    )
    rows = [
        [InlineKeyboardButton(
            text=f"🧬 Тип: {'Рыба' if kind == 'fish' else 'Ресурс'} →",
            callback_data=f"fishing:kind:{wf_id}"),
         InlineKeyboardButton(
            text=f"🏪 Рынок: {'✅' if fish.get('market_ok') else '🔒'} →",
            callback_data=f"fishing:market:{wf_id}")],
        [InlineKeyboardButton(text="☀️ Вес дня", callback_data="fishing_field:day_weight")],
        [InlineKeyboardButton(text="🌙 Вес ночи", callback_data="fishing_field:night_weight")],
        [InlineKeyboardButton(text="🖼 Фото рыбы", callback_data="fishing_field:photo")],
        [InlineKeyboardButton(text="💰 Цена продажи", callback_data="fishing_field:sell_price")],
        [InlineKeyboardButton(text="🗑 Удалить из водоёма", callback_data=f"fishing:del:{wf_id}")],
        [InlineKeyboardButton(text="🔙 К списку рыб", callback_data=f"fishing:water:{fish['water']}")],
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    if hasattr(source, 'message') and source.message is not None:
        await source.message.edit_text(text, reply_markup=markup)
    else:
        await source.answer(text, reply_markup=markup)


@router.callback_query(F.data.startswith("fishing:junk:"))
async def admin_fishing_junk(callback: CallbackQuery, state: FSMContext):
    """Находки со дна (мусор без наживки): шанс выпадения и картинка на водоём."""
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    water = callback.data.split(":", 2)[2]
    if water not in WATER_LABELS:
        return
    await state.clear()
    await state.update_data(water=water)
    await _admin_fishing_junk_card(callback, water)


async def _admin_fishing_junk_card(source, water: str, prefix: str = ""):
    """Карточка находок со дна: шансы и фото водорослей/сапога на этот водоём."""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    rows = await get_water_junk_rows(water)
    lines = [
        f"{prefix}🗑 НАХОДКИ СО ДНА",
        f"🐟 {WATER_LABELS[water]}\n",
        "Без наживки рыба НЕ клюёт: со дна поднимается только мусор.",
        "Шанс и картинка настраиваются на этот водоём:\n",
    ]
    buttons = []
    for r in rows:
        name = r['name']
        chance = r['chance'] or 0
        photo_state = "есть" if r.get('photo_file_id') else "нет"
        emo = JUNK_EMOJI.get(name, "🗑")
        lines.append(f"{emo} {name} — шанс {chance}%, фото: {photo_state}")
        buttons.append([
            InlineKeyboardButton(
                text=f"{emo} 🎲 Шанс выпадения",
                callback_data=f"fishing_j:chance:{water}:{name}"),
            InlineKeyboardButton(
                text=f"{emo} 🖼 Фото",
                callback_data=f"fishing_j:photo:{water}:{name}"),
        ])
    if not rows:
        lines.append("Записей пока нет.")
    buttons.append([InlineKeyboardButton(text="🔙 К списку рыб",
                                         callback_data=f"fishing:water:{water}")])
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    if hasattr(source, 'message') and source.message is not None:
        await source.message.edit_text("\n".join(lines), reply_markup=markup)
    else:
        await source.answer("\n".join(lines), reply_markup=markup)


@router.callback_query(F.data.startswith("fishing_j:"))
async def admin_fishing_junk_field_pick(callback: CallbackQuery, state: FSMContext):
    """Выбор поля находки: шанс % или фото."""
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    parts = callback.data.split(":", 3)
    if len(parts) != 4:
        return
    jfield, water, jname = parts[1], parts[2], parts[3]
    if jfield not in ("chance", "photo") or water not in WATER_LABELS:
        return
    await state.update_data(water=water, jfield=jfield, jname=jname)
    await state.set_state(AdminFishing.value)
    if jfield == "chance":
        prompt = ("🎲 Введи шанс выпадения в % (целое число 0–100; "
                  "0 = находка не выпадает).\nДефолт: водоросли 15%, сапог 2%.")
    else:
        prompt = f"🖼 Отправь фото находки «{jname}» (Telegram-фото). Или «-», чтобы убрать фото:"
    await callback.message.answer(prompt, reply_markup=cancel_keyboard())


@router.callback_query(F.data == "admin:fishing")
async def admin_fishing_menu(callback: CallbackQuery, state: FSMContext):
    """Меню редактора рыбалки: выбор водоёма."""
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    rows = [
        [InlineKeyboardButton(text="🌊 Озеро в парке", callback_data="fishing:water:lake")],
        [InlineKeyboardButton(text="🌊 Подземное водохранилище", callback_data="fishing:water:reservoir")],
        [InlineKeyboardButton(text="🔙 В админ-панель", callback_data="admin:menu")],
    ]
    await callback.message.edit_text(
        "🐟 РЕДАКТОР РЫБАЛКИ\n\nУ каждого водоёма свой список рыбы: "
        "веса по времени суток, фото и цена продажи. Выбери водоём:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows)
    )


@router.callback_query(F.data.startswith("fishing:water:"))
async def admin_fishing_water(callback: CallbackQuery, state: FSMContext):
    """Список рыбы выбранного водоёма."""
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    water = callback.data.split(":")[2]
    if water not in WATER_LABELS:
        return
    await state.clear()
    await state.update_data(water=water)
    await _admin_fishing_water_list(callback, water)


async def _admin_fishing_water_list(callback: CallbackQuery, water: str, prefix: str = ""):
    """Меню водоёма: список рыбы + кнопки «Добавить рыбу» и возврата."""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    fishes = await get_water_fish_rows(water)
    lines = [f"{prefix}🐟 {WATER_LABELS[water]}\n"]
    rows = []
    if fishes:
        for f in fishes:
            kind_mark = "📦" if (f.get('kind') or 'fish') == "resource" else "🐟"
            lines.append(f"• {kind_mark} {f['name']} — день {f['day_weight']}, "
                         f"ночь {f['night_weight']}, продажа {f['sell_price']} НМ")
            rows.append([InlineKeyboardButton(text=f["name"], callback_data=f"fishing:fish:{f['id']}")])
    else:
        lines.append("Рыб в этом водоёме пока нет.")
    lines.append("\n🐟 — рыба, 📦 — ресурс (находка).")
    rows.append([InlineKeyboardButton(text="➕ Добавить рыбу", callback_data=f"fishing:addlist:{water}")])
    rows.append([InlineKeyboardButton(text="🗑 Находки со дна (шанс и фото)",
                                      callback_data=f"fishing:junk:{water}")])
    rows.append([InlineKeyboardButton(text="🔙 К водоёмам", callback_data="admin:fishing")])
    await callback.message.edit_text("\n".join(lines),
                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))


@router.callback_query(F.data.startswith("fishing:fish:"))
async def admin_fishing_fish(callback: CallbackQuery, state: FSMContext):
    """Карточка рыбы с кнопками правки."""
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    try:
        wf_id = int(callback.data.split(":")[2])
    except (ValueError, IndexError):
        return
    await state.update_data(wf_id=wf_id)
    await _admin_fishing_card(callback, wf_id)


@router.callback_query(F.data.startswith("fishing:kind:"))
async def admin_fishing_kind(callback: CallbackQuery, state: FSMContext):
    """Переключает тип записи водоёма: рыба ⇄ ресурс (находка)."""
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    try:
        wf_id = int(callback.data.split(":", 2)[2])
    except (ValueError, IndexError):
        return
    fish = await get_water_fish_row(wf_id)
    if not fish:
        await callback.message.answer("❌ Рыба не найдена.")
        return
    new_kind = "resource" if (fish.get('kind') or 'fish') == "fish" else "fish"
    await update_water_fish_field(wf_id, "kind", new_kind)
    await log_action(callback.from_user.id, 'edit_fishing', None,
                     f"wf_id={wf_id} kind={new_kind}")
    await state.update_data(wf_id=wf_id)
    await _admin_fishing_card(callback, wf_id)


@router.callback_query(F.data.startswith("fishing:market:"))
async def admin_fishing_market(callback: CallbackQuery, state: FSMContext):
    """Переключает, можно ли этот улов выставлять на рынок (items.market_ok)."""
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    try:
        wf_id = int(callback.data.split(":", 2)[2])
    except (ValueError, IndexError):
        return
    fish = await get_water_fish_row(wf_id)
    if not fish:
        await callback.message.answer("❌ Улов не найден.")
        return
    new_val = 0 if fish.get('market_ok') else 1
    await update_item(fish['item_id'], market_ok=new_val)
    await log_action(callback.from_user.id, 'edit_fishing', None,
                     f"wf_id={wf_id} market_ok={new_val}")
    await state.update_data(wf_id=wf_id)
    await _admin_fishing_card(callback, wf_id)


@router.callback_query(F.data.startswith("fishing:addlist:"))
async def admin_fishing_add_list(callback: CallbackQuery, state: FSMContext):
    """Выбор рыбы для добавления в водоём."""
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    water = callback.data.split(":", 2)[2]
    if water not in WATER_LABELS:
        return
    await state.update_data(water=water)

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    candidates = await get_water_fish_candidates(water)
    lines = [f"➕ Добавление рыбы\n🐟 {WATER_LABELS[water]}\n"]
    rows = []
    if candidates:
        for c in candidates:
            rows.append([InlineKeyboardButton(
                text=f"{c['name']} (продажа {c['sell_price']} НМ)",
                callback_data=f"fishing:addfish:{water}:{c['id']}",
            )])
    else:
        lines.append("Все доступные рыбы и находки уже добавлены в этот водоём.")
    lines.append("\nДобавится с весом 1/1 — потом настроишь веса, фото, цену и тип "
                 "(рыба/ресурс).")
    rows.append([InlineKeyboardButton(text="🔙 К списку рыб", callback_data=f"fishing:water:{water}")])
    await callback.message.edit_text("\n".join(lines),
                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))


@router.callback_query(F.data.startswith("fishing:addfish:"))
async def admin_fishing_add(callback: CallbackQuery, state: FSMContext):
    """Добавляет рыбу в водоём и сразу показывает её карточку."""
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    try:
        water, item_id = callback.data.split(":", 2)[2].split(":")
        item_id = int(item_id)
    except ValueError:
        return
    if water not in WATER_LABELS:
        return
    wf_id = await add_water_fish(water, item_id, 1, 1)
    fish = await get_water_fish_row(wf_id) if wf_id else None
    if not fish:
        await callback.message.answer("❌ Не удалось добавить рыбу.")
        return
    await state.update_data(water=water, wf_id=wf_id)
    await _admin_fishing_card(callback, wf_id,
                              prefix=f"✅ «{fish['name']}» добавлена в водоём.\n\n")


@router.callback_query(F.data.startswith("fishing:del:"))
async def admin_fishing_del(callback: CallbackQuery, state: FSMContext):
    """Убирает рыбу из водоёма и возвращает в меню водоёма."""
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    try:
        wf_id = int(callback.data.split(":", 2)[2])
    except (ValueError, IndexError):
        return
    fish = await get_water_fish_row(wf_id)
    if not fish:
        await callback.message.answer("❌ Рыба не найдена.")
        return
    removed = await remove_water_fish(wf_id)
    await log_action(callback.from_user.id, 'edit_fishing', None,
                     f"wf_id={wf_id} removed={removed}")
    await state.clear()
    await state.update_data(water=fish['water'])
    await _admin_fishing_water_list(
        callback, fish['water'],
        prefix=f"🗑 «{fish['name']}» убрана из водоёма.\n\n",
    )


@router.callback_query(F.data.startswith("fishing_field:"))
async def admin_fishing_field_pick(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    field = callback.data.split(":")[1]
    if field not in FISHING_FIELD_LABELS:
        return
    data = await state.get_data()
    if not data.get('wf_id'):
        await callback.message.answer("❌ Рыба не выбрана. Открой карточку рыбы заново.")
        return
    await state.update_data(field=field)
    await state.set_state(AdminFishing.value)
    await callback.message.answer(FISHING_INPUT_PROMPTS[field], reply_markup=cancel_keyboard())


@router.message(AdminFishing.value)
async def admin_fishing_value(message: Message, state: FSMContext):
    data = await state.get_data()
    jfield = data.get('jfield')
    jname = data.get('jname')
    jwater = data.get('water')

    # ── Находки со дна (мусор): шанс % или фото ──
    if jfield:
        if jfield == "chance":
            text = (message.text or "").strip()
            parsed = int(text) if text.isdigit() else None
            if parsed is None or not (0 <= parsed <= 100):
                await message.answer("❌ Ожидаю целое число от 0 до 100 (0 = не выпадает).",
                                     reply_markup=cancel_keyboard())
                return
            label = f"{parsed}%" if parsed > 0 else "не выпадает"
        else:
            if (message.text or "").strip() == "-":
                parsed = None
                label = "убрано"
            elif message.photo:
                parsed = message.photo[-1].file_id
                label = "обновлено"
            else:
                await message.answer("❌ Отправь именно фото (или «-» для очистки).",
                                     reply_markup=cancel_keyboard())
                return
        await update_water_junk(jwater, jname, "photo_file_id" if jfield == "photo" else "chance",
                                parsed)
        await log_action(message.from_user.id, 'edit_fishing', None,
                         f"junk {jwater} {jname} {jfield}={parsed}")
        await state.clear()
        await state.update_data(water=jwater)
        await _admin_fishing_junk_card(
            message, jwater,
            prefix=f"✅ «{jname}»: {jfield} = {label}.\n\n")
        return

    # ── Рыба/ресурс в водоёме (веса, фото, цена) ──
    wf_id = data.get('wf_id')
    field = data.get('field')
    fish = await get_water_fish_row(wf_id) if wf_id else None
    if not fish:
        await state.clear()
        await message.answer("❌ Рыба не найдена. Начни заново: админ → рыбалка → водоём.")
        return
    if field not in FISHING_FIELD_LABELS:
        await state.clear()
        await message.answer("❌ Поле не распознано. Начни заново.")
        return

    if field in ("day_weight", "night_weight", "sell_price"):
        text = (message.text or "").strip()
        parsed = int(text) if text.isdigit() else None
        if parsed is None or parsed < 0:
            await message.answer(f"❌ Ожидаю целое число ≥ 0.\n{FISHING_INPUT_PROMPTS[field]}",
                                 reply_markup=cancel_keyboard())
            return
        if field == "sell_price":
            await set_water_fish_sell_price(wf_id, parsed)
        else:
            await update_water_fish_field(wf_id, field, parsed)
        label = f"{parsed} НМ" if field == "sell_price" else str(parsed)
    else:  # photo
        if (message.text or "").strip() == "-":
            parsed = None
        elif message.photo:
            parsed = message.photo[-1].file_id
        else:
            await message.answer("❌ Отправь именно фото (или «-» для очистки).",
                                 reply_markup=cancel_keyboard())
            return
        await update_water_fish_field(wf_id, "photo_file_id", parsed)
        label = "убрано" if parsed is None else "обновлено"

    await log_action(message.from_user.id, 'edit_fishing', None,
                     f"wf_id={wf_id} {field}={parsed}")
    await state.clear()
    await state.update_data(water=fish['water'], wf_id=wf_id)
    await _admin_fishing_card(
        message, wf_id,
        prefix=f"✅ «{fish['name']}»: {FISHING_FIELD_LABELS[field]} = {label}.\n\n",
    )


@router.callback_query(F.data == "loc:create")
async def loc_create(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    await state.update_data(action="create")
    await state.set_state(AdminLocation.key)
    await callback.message.edit_text(
        "Создание локации. Шаг 1/7 — введи уникальный ключ локации латиницей\n"
        "(например: bar, market). Без пробелов:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data="admin:locations")]
        ])
    )


@router.callback_query(F.data == "loc:edit_pick")
async def loc_edit_pick(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    locs = await get_all_locations()
    if not locs:
        await callback.message.edit_text("Локаций пока нет. Сначала создай.")
        return
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    rows = [[InlineKeyboardButton(text=l['name'], callback_data=f"loc:edit:{l['id']}")] for l in locs]
    rows.append([InlineKeyboardButton(text="🔙 Назад", callback_data="admin:locations")])
    await callback.message.edit_text("Выбери локацию для редактирования доступа:",
                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))


@router.callback_query(F.data == "loc:building_pick")
async def loc_building_pick(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    locs = await get_all_locations()
    if not locs:
        await callback.message.edit_text("Локаций пока нет. Сначала создай.")
        return
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    rows = [[InlineKeyboardButton(text=l['name'], callback_data=f"loc:building:{l['id']}")] for l in locs]
    rows.append([InlineKeyboardButton(text="🔙 Назад", callback_data="admin:locations")])
    await callback.message.edit_text("Выбери здание для редактирования (название/описание/картинка):",
                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))


@router.callback_query(F.data.startswith("loc:edit:"))
async def loc_edit(callback: CallbackQuery, state: FSMContext):
    """Редактирование ДОСТУПА к локации (режим / статус / блокирующие состояния)."""
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    loc_id = int(callback.data.split(":")[2])
    loc = await get_location(loc_id)
    if not loc:
        await callback.message.answer("❌ Локация не найдена.")
        return
    acc = await location_access_label(loc['access_mode'], loc['required_status'])
    blocking = ", ".join(json.loads(loc['blocking_states'] or '[]')) or "нет"
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    await state.update_data(action="edit", target_id=loc_id)
    await callback.message.edit_text(
        f"✏️ {loc['name']} (доступ: {acc})\nБлокируют состояния: {blocking}\n\nЧто изменить?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🎚 Режим доступа", callback_data="loc:set_mode")],
            [InlineKeyboardButton(text="🗂 Требуемый статус", callback_data="loc:set_status")],
            [InlineKeyboardButton(text="🍺 Блокирующие состояния", callback_data="loc:set_blocking")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="loc:edit_pick")],
        ])
    )


@router.callback_query(F.data.startswith("loc:building:"))
async def loc_building_edit(callback: CallbackQuery, state: FSMContext):
    """Редактирование ЗДАНИЯ: название / описание / картинка."""
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    loc_id = int(callback.data.split(":")[2])
    loc = await get_location(loc_id)
    if not loc:
        await callback.message.answer("❌ Локация не найдена.")
        return
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    await state.update_data(action="edit", target_id=loc_id)
    await callback.message.edit_text(
        f"🏛 {loc['name']}\nЧто изменить в здании?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✏️ Название", callback_data="loc:set_name")],
            [InlineKeyboardButton(text="📝 Описание", callback_data="loc:set_desc")],
            [InlineKeyboardButton(text="🖼 Картинки (время суток)", callback_data="loc:photos")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="loc:building_pick")],
        ])
    )


@router.callback_query(F.data == "loc:set_mode")
async def loc_set_mode(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    await state.set_state(AdminLocation.mode)
    await callback.message.edit_text(
        "Выбери режим доступа:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🌐 Всем", callback_data="loc:mode:all")],
            [InlineKeyboardButton(text="📈 Статус и выше", callback_data="loc:mode:min")],
            [InlineKeyboardButton(text="🎯 Только конкретному", callback_data="loc:mode:exact")],
            [InlineKeyboardButton(text="🔙 Отмена", callback_data="admin:locations")],
        ])
    )


@router.callback_query(AdminLocation.mode, F.data.startswith("loc:mode:"))
async def loc_mode_chosen(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    mode = callback.data.split(":")[2]
    data = await state.get_data()
    loc_id = data.get('target_id')
    if data.get('action') == 'edit' and loc_id:
        if mode == "all":
            await update_location_access(loc_id, access_mode="all", required_status=None)
            await state.clear()
            await callback.message.edit_text("✅ Режим доступа: 🌐 Всем")
        else:
            # min/exact — сначала выбрать требуемый статус
            await state.update_data(mode=mode)
            await state.set_state(AdminLocation.req_status)
            await _loc_status_pick(callback, state)
    else:
        await state.update_data(mode=mode)
        if mode == "all":
            await state.update_data(req_status=None)
            await state.set_state(AdminLocation.blocking)
            await _loc_blocking_pick(callback, state)
        else:
            await state.set_state(AdminLocation.req_status)
            await _loc_status_pick(callback, state)


@router.callback_query(F.data == "loc:set_status")
async def loc_set_status(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    await state.set_state(AdminLocation.req_status)
    await _loc_status_pick(callback, state)


@router.callback_query(AdminLocation.req_status, F.data.startswith("loc:req_status:"))
async def loc_req_status_chosen(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    tag = callback.data.split(":")[2]
    data = await state.get_data()
    loc_id = data.get('target_id')
    if data.get('action') == 'edit' and loc_id:
        mode = data.get('mode')
        await update_location_access(loc_id,
                                     access_mode=mode if mode in ("min", "exact") else None,
                                     required_status=tag)
        await state.clear()
        await callback.message.edit_text(f"✅ Требуемый статус: {tag}")
    else:
        await state.update_data(req_status=tag)
        await state.set_state(AdminLocation.blocking)
        await _loc_blocking_pick(callback, state)


@router.callback_query(F.data == "loc:set_blocking")
async def loc_set_blocking(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    data = await state.get_data()
    loc = await get_location(data.get('target_id'))
    if not loc:
        await callback.message.answer("❌ Локация не найдена.")
        return
    current = json.loads(loc['blocking_states'] or '[]')
    await state.update_data(pending_blocking=list(current))
    await state.set_state(AdminLocation.blocking)
    await _loc_blocking_pick(callback, state)


@router.callback_query(AdminLocation.blocking, F.data.startswith("loc:blocking:"))
async def loc_blocking_chosen(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    action = callback.data.split(":", 2)[2]
    if action.startswith("toggle:"):
        key = action.split(":", 1)[1]
        sel = list(data.get('pending_blocking') or [])
        if key in sel:
            sel.remove(key)
        else:
            sel.append(key)
        await state.update_data(pending_blocking=sel)
        await _loc_blocking_pick(callback, state)
        return
    if action == "none":
        blocking = []
    elif action == "done":
        blocking = list(data.get('pending_blocking') or [])
    else:
        blocking = [s.strip() for s in action.split(",") if s.strip()]
    if data.get('action') == 'edit' and data.get('target_id'):
        await update_location_access(data['target_id'], blocking_states=blocking)
        await state.clear()
        await callback.message.edit_text("✅ Блокирующие состояния обновлены.")
    else:
        await state.update_data(blocking=blocking)
        await _finish_loc_create(callback, state)


async def _loc_status_pick(callback, state):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    statuses = await get_all_statuses()
    rows = []
    for s in statuses:
        tag = s['access_tag'] or s['name']
        rows.append([InlineKeyboardButton(text=s['name'], callback_data=f"loc:req_status:{tag}")])
    rows.append([InlineKeyboardButton(text="🔙 Отмена", callback_data="admin:locations")])
    await callback.message.edit_text("Выбери требуемый статус:",
                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))


async def _loc_blocking_pick(callback, state):
    """Инлайн-выбор блокирующих состояний (мультиселект): toggle + готово."""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    from utils.states import state_keys
    data = await state.get_data()
    sel = data.get('pending_blocking') or []
    rows = []
    for k in state_keys():
        mark = "✅" if k in sel else "✔️"
        rows.append([InlineKeyboardButton(text=f"{mark} {k}", callback_data=f"loc:blocking:toggle:{k}")])
    rows.append([
        InlineKeyboardButton(text="✅ Готово", callback_data="loc:blocking:done"),
        InlineKeyboardButton(text="🚫 Ничего", callback_data="loc:blocking:none"),
    ])
    rows.append([InlineKeyboardButton(text="🔙 Отмена", callback_data="admin:locations")])
    if data.get('action') == 'edit' and data.get('target_id'):
        await callback.message.edit_text(
            "Выбери состояния, которые блокируют вход (можно несколько):",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))
    else:
        await callback.message.edit_text(
            "Какие состояния блокируют вход? (можно несколько):",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))


async def _finish_loc_create(callback, state):
    data = await state.get_data()
    mode = data.get('mode') or 'all'
    req = data.get('req_status')
    blocking = data.get('blocking') or []
    ok, err = await create_location(
        key=data['key'], name=data['name'], description=data.get('description'),
        access_mode=mode, required_status=req, blocking_states=blocking
    )
    await state.clear()
    if ok:
        await callback.message.edit_text(f"✅ Локация «{data['name']}» создана.")
    else:
        await callback.message.edit_text(f"❌ Ошибка создания: {err}")


# FSM: создание локации (шаги)
@router.message(AdminLocation.key)
async def loc_step_key(message: Message, state: FSMContext):
    key = message.text.strip().lower()
    if not key or not key.replace("_", "").isalnum():
        await message.answer("❌ Ключ — латиница/цифры/подчёркивание без пробелов.")
        return
    await state.update_data(key=key)
    await state.set_state(AdminLocation.name)
    await message.answer("Шаг 2/7 — название локации:")


@router.message(AdminLocation.name)
async def loc_step_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await state.set_state(AdminLocation.description)
    await message.answer("Шаг 3/7 — описание (или отправь «-»):")


@router.callback_query(F.data == "loc:set_name")
async def loc_set_name(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    data = await state.get_data()
    loc = await get_location(data.get('target_id'))
    if not loc:
        await callback.message.answer("❌ Локация не найдена.")
        return
    await state.set_state(AdminLocation.set_name)
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    await callback.message.edit_text(
        f"✏️ Название «{loc['name']}».\n\nОтправь новое название здания:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data=f"loc:building:{loc['id']}")]
        ])
    )


@router.message(AdminLocation.set_name)
async def loc_step_set_name(message: Message, state: FSMContext):
    text = message.text.strip()
    if not text or len(text) > 60:
        await message.answer("❌ Название должно быть от 1 до 60 символов.")
        return
    data = await state.get_data()
    if data.get('action') == 'edit' and data.get('target_id'):
        await update_location_content(data['target_id'], name=text)
        await log_action(message.from_user.id, 'edit_location', data['target_id'],
                         f"name={text[:200]}")
        await state.clear()
        await message.answer("✅ Название локации обновлено.")
    else:
        await state.update_data(name=text)
        await state.set_state(AdminLocation.description)
        await message.answer("Шаг 3/7 — описание (или отправь «-»):")


@router.callback_query(F.data == "loc:set_desc")
async def loc_set_desc(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    data = await state.get_data()
    loc = await get_location(data.get('target_id'))
    if not loc:
        await callback.message.answer("❌ Локация не найдена.")
        return
    await state.set_state(AdminLocation.description)
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    await callback.message.edit_text(
        f"📝 Описание «{loc['name']}».\n\nОтправь новый текст (или «-», чтобы очистить):",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data=f"loc:building:{loc['id']}")]
        ])
    )


TOD_KEYS = ("dawn", "day", "sunset", "night")
TOD_LABEL = {"dawn": "🌅 Рассвет", "day": "☀️ День", "sunset": "🌇 Закат", "night": "🌙 Ночь"}
# Слоты картинок подземелья: вход по времени суток + комнаты-препятствия К.В.П.
DUNGEON_PHOTO_LABEL = {
    "dawn": "🌅 Рассвет", "day": "☀️ День", "sunset": "🌇 Закат", "night": "🌙 Ночь",
    "water": "🌊 Вода", "rope": "🪢 Верёвка",
}


def _loc_photo_slots_text(loc):
    keys = loc.keys()
    filled = [TOD_LABEL[k] for k in TOD_KEYS
              if f"photo_{k}" in keys and loc[f"photo_{k}"]]
    return filled or ["нет"]


async def _loc_photos_pick_send(source, loc_id: int):
    """Показать пикер 4 картинок здания (source может быть CallbackQuery или Message)."""
    loc = await get_location(loc_id)
    if not loc:
        if isinstance(source, CallbackQuery):
            await source.message.edit_text("❌ Локация не найдена.")
        else:
            await source.answer("❌ Локация не найдена.")
        return
    filled = _loc_photo_slots_text(loc)
    keys = loc.keys()
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    rows = []
    for k in TOD_KEYS:
        mark = "✅" if f"photo_{k}" in keys and loc[f"photo_{k}"] else "—"
        rows.append([InlineKeyboardButton(
            text=f"{mark} {TOD_LABEL[k]}",
            callback_data=f"loc:photo_set:{k}"
        )])
    rows.append([InlineKeyboardButton(text="🚫 Убрать все", callback_data="loc:photos:clear")])
    rows.append([InlineKeyboardButton(text="🔙 Назад", callback_data="loc:building_pick")])
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    text = (
        f"🖼 Картинки «{loc['name']}».\n"
        f"Задано: {', '.join(filled)}\n\n"
        f"Нажми время суток и отправь фото (или «-» чтобы убрать):"
    )
    if isinstance(source, CallbackQuery):
        await source.message.edit_text(text, reply_markup=kb)
    else:
        await source.answer(text, reply_markup=kb)


@router.callback_query(F.data == "loc:photos")
async def loc_photos_pick(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    data = await state.get_data()
    await _loc_photos_pick_send(callback, data['target_id'])


@router.message(AdminLocation.description)
async def loc_step_desc(message: Message, state: FSMContext):
    text = message.text.strip()
    data = await state.get_data()
    if data.get('action') == 'edit' and data.get('target_id'):
        await update_location_content(data['target_id'], description=None if text == "-" else text)
        await log_action(message.from_user.id, 'edit_location', data['target_id'],
                         f"description={text[:200] if text != '-' else 'cleared'}")
        await state.clear()
        await message.answer("✅ Описание локации обновлено.")
        return
    await state.update_data(description=None if text == "-" else text)
    await state.set_state(AdminLocation.mode)
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    await message.answer(
        "Шаг 4/7 — режим доступа:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🌐 Всем", callback_data="loc:mode:all")],
            [InlineKeyboardButton(text="📈 Статус и выше", callback_data="loc:mode:min")],
            [InlineKeyboardButton(text="🎯 Только конкретному", callback_data="loc:mode:exact")],
        ])
    )


@router.callback_query(F.data.startswith("loc:photo_set:"))
async def loc_photo_set(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    tod = callback.data.split(":")[2]
    if tod not in TOD_KEYS:
        return
    data = await state.get_data()
    loc_id = data.get('target_id')
    if not loc_id:
        return
    await state.set_state(AdminLocation.preview)
    await state.update_data(photo_tod=tod)
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    await callback.message.edit_text(
        f"🖼 {TOD_LABEL[tod]}.\n\nОтправь фото (или «-» чтобы убрать для этого времени):",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data="loc:photos")]
        ])
    )


@router.callback_query(F.data == "loc:photos:clear")
async def loc_photos_clear(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    data = await state.get_data()
    loc_id = data.get('target_id')
    if not loc_id:
        return
    await update_location_photos(loc_id, {k: None for k in TOD_KEYS})
    await _loc_photos_pick_send(callback, loc_id)


@router.message(AdminLocation.preview)
async def loc_step_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    loc_id = data.get('target_id')
    if not loc_id:
        await state.clear()
        await message.answer("❌ Ошибка: нет локации в сессии.")
        return
    loc = await get_location(loc_id)
    if not loc:
        await state.clear()
        await message.answer("❌ Локация не найдена.")
        return
    if message.photo:
        file_id = message.photo[-1].file_id
    elif message.text and message.text.strip() in ("-", "—"):
        file_id = None
    else:
        await message.answer("❌ Отправь именно фото (или «-» для очистки).")
        return
    photo_tod = data.get('photo_tod')
    if photo_tod and photo_tod in TOD_KEYS:
        await update_location_photos(loc_id, {photo_tod: file_id})
        await log_action(message.from_user.id, 'edit_location', loc_id,
                         f"photo_{photo_tod}={'file_id' if file_id else 'cleared'}")
        await _loc_photos_pick_send(message, loc_id)
        return
    await update_location_content(loc_id, preview_photo=file_id)
    await log_action(message.from_user.id, 'edit_location', loc_id,
                     f"preview_photo={'file_id' if file_id else 'cleared'}")
    await state.clear()
    await message.answer("✅ Картинка локации обновлена.")
