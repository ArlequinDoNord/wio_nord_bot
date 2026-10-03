"""
Админ-панель: управление магазином, финансами, отчётами, ролями и логами.
Доступ разграничен по ролям (см. utils/permissions.py).
"""

import json

from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.db import (
    add_item, delete_item, delete_item_completely, update_item, get_available_items, get_all_items,
    get_item, get_all_users, get_pending_reports, approve_report, correct_report_numbers,
    reject_report, add_nordmarks, remove_nordmarks,
    get_approved_reports, count_approved_reports, report_day_value_of, report_tax_percent_for,
    report_day_label_for, created_at_msk,
    create_status, delete_status, get_all_statuses, get_status,
    grant_status, revoke_status, get_user_statuses, citizen_user_ids,
    get_status_by_tag, is_legioner, set_legioner, LEGIONER_ACCESS_TAG,
    get_users_for_rank_promotion, promote_user_rank, get_user,
    recompute_region_stats, get_region_stats,
    get_daily_spent, add_daily_spent,
    get_treasury_balance, transfer_from_treasury, get_treasury_stats,
    get_report_tax_percent, set_report_tax_percent,
    get_report_auto_approve_troops, set_report_auto_approve_troops,
    get_report_daily_pay_cap, set_report_daily_pay_cap,
        get_news_chat, set_news_chat, get_allowed_chats, set_allowed_chats,
    get_sale_tax_percent, set_sale_tax_percent,
    get_special_dept_code, set_special_dept_code,
    get_salaried_users, get_user_salary, set_user_salary, pay_salaries,
    get_treasury_debts,
    get_all_locations, get_location, create_location, update_location_access,
    update_location_content, update_location_photos, location_access_label,
    update_location_season_photo, clear_location_season_photos, clear_location_season,
    location_season_photos_raw, LOCATION_SEASONS,
    location_glade_photo, update_location_glade_photo,
    location_clearing_photo, update_location_clearing_photo,
    get_all_dungeons, get_dungeon, update_dungeon_photos, DUNGEON_PHOTO_KEYS,
    get_dungeon_enemies, get_enemy, update_enemy_fields, get_floor_enemies,
    get_enemy_drops, set_enemy_drops, add_enemy_drop, remove_enemy_drop,
    get_source_enemies, get_source_enemy, update_source_enemy, delete_source_enemy,
    get_source_enemy_drops, set_source_enemy_drops, add_source_enemy_drop,
    remove_source_enemy_drop, add_source_enemy, get_fishing_spots,
    get_item_by_name,
    create_award, get_all_awards, get_award, delete_award, grant_award,
    update_award, get_user_awards, revoke_award, MAX_CRIT_CHANCE,
    get_water_fish_rows, get_water_fish_row, update_water_fish_field,
    set_water_fish_sell_price, add_water_fish, remove_water_fish,
    create_water_fish,
    get_water_fish_candidates, WATER_LABELS, set_callsign, set_wing,
    get_water_junk_rows, update_water_junk, JUNK_EMOJI,
    get_forest_mushroom_rows, get_forest_mushroom_row, update_forest_mushroom_field,
    set_forest_mushroom_sell_price, add_forest_mushroom, remove_forest_mushroom,
    create_forest_mushroom, get_forest_mushroom_candidates,
    get_forest_zones, get_forest_zone, update_forest_zone,
    get_forest_setting, set_forest_setting,
    get_forest_zone_pool, get_forest_zone_candidates,
    add_forest_mushroom_to_zone, remove_forest_mushroom_from_zone,
    set_forest_zone_chance, FOREST_AREAS,
    log_activity, get_user_activity, clear_user_photo,
    get_recent_activity, get_activity_like, get_activity_by_action,
    get_location_visit_stats, get_location_visit_totals,
)
from keyboards.keyboards import cancel_keyboard
from utils.permissions import (
    is_admin, has_permission, get_user_role,
    add_role, remove_role, ROLES, role_label, log_action, DELEGABLE_ROLES,
    can_grant_status, can_view_status_panel, is_citizen_gate_status,
)
from utils.helpers import plural_nordmark
from config import RARITY_LEVELS, RARITY_EMOJI, ITEM_CATEGORIES, get_effective_rank, VERSION, DRINK_EFFECT_LABELS, AWARD_MAX_SHOP_DISCOUNT, AWARD_MIN_REPORT_TAX
from utils.notify import notify, player_display, notify_award, notify_report_praise

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
    loot = State()
    status = State()
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


class AdminStorageDelete(StatesGroup):
    # Удаление предмета из игры насовсем: подтверждение вводом названия
    confirm = State()


class AdminTax(StatesGroup):
    percent = State()


class AdminReportAutoApprove(StatesGroup):
    value = State()


class AdminReportPayCap(StatesGroup):
    value = State()


class AdminReportFix(StatesGroup):
    # Правка цифр отчёта (только супер-админ): сутки → всего → применение
    daily = State()
    total = State()


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
    bonus = State()
    preview = State()
    target = State()
    award_pick = State()
    comment = State()
    edit_value = State()


class AdminFishing(StatesGroup):
    """Редактор пулов рыбалки по водоёмам (веса, фото, цена продажи)."""
    water = State()
    wf_id = State()
    value = State()
    c_name = State()          # мастер создания рыбы: название
    c_desc = State()          # описание (опционально)
    c_sell_price = State()    # цена продажи скупщику
    c_day_weight = State()    # вес днём
    c_night_weight = State()  # вес ночью
    c_photo = State()         # фото


class AdminForest(StatesGroup):
    """Редактор грибов леса (шанс, тип, фото, цена продажи)."""
    f_id = State()
    field = State()
    value = State()
    c_name = State()          # мастер создания гриба: название
    c_desc = State()          # описание (опционально)
    c_sell_price = State()    # цена продажи скупщику
    c_chance = State()        # шанс выпадения в пуле %
    c_kind = State()          # тип: съедобный / ядовитый
    c_photo = State()         # фото
    zone_value = State()      # ввод числа в настройках зоны / веса гриба в зоне


class AdminEnemy(StatesGroup):
    """Единый редактор врагов (лес, рыбалка): правка полей, дропы, создание."""
    field = State()          # ввод значения поля карточки
    photo = State()          # загрузка фото врага
    drop_chance = State()    # шанс дропа, %
    drop_qty = State()       # количество дропа
    c_name = State()         # мастер: название
    c_hp = State()           # мастер: HP
    c_dmg = State()          # мастер: урон мин-макс
    c_dodge = State()        # мастер: уклонение %
    c_chance = State()       # мастер: шанс встречи %
    c_loss_ap = State()      # мастер: потеря ОД при поражении


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
             "can_manage_users", "can_assign_mvd_helper",
             "can_grant_citizen_status",
             # Без этих четырёх UI отдавал always-False, и кнопки были
             # невидимы: Квестор не мог попасть в «Финансы» вообще,
             # а глава МВД — в управление крылом.
             "can_view_balances", "can_add_currency", "can_remove_currency",
             "can_manage_wing"]
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


async def pilot_picker_markup(next_step: str, mark_tourists: bool = False, tourists_top: bool = False, page: int = 1, per_page: int = 10):
    """Клавиатура выбора пилота из списка; next_step — куда переходить после выбора.

    mark_tourists — помечать 🎫 тех, у кого ещё нет гражданства (меню статусов:
    суперадмину сразу видно, кому гражданство ещё выдавать, вместо поиска по списку).
    tourists_top — ставить туристов (без гражданства) в самом верху списка.
    page, per_page — пагинация (по умолчанию 10 на страницу, как запрошено 8–10).
    """
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    users = await get_all_users()
    # 🎫 — тот же бейдж, что в списке пилотов Ратуши (bot/handlers/pilots.py).
    citizens = (await citizen_user_ids()) if (mark_tourists or tourists_top) else None
    rows = []
    if users:
        # Сортировка: туристы вверху, если запрошено
        items = list(users)
        if tourists_top and citizens is not None:
            def key(u):
                is_tourist = u['user_id'] not in citizens
                return (0 if is_tourist else 1, (u['first_name'] or u['username'] or '').lower())
            items.sort(key=key)
        elif not tourists_top:
            # базовая сортировка по имени для консистентности
            items.sort(key=lambda u: (u['first_name'] or u['username'] or '').lower())
        else:
            items.sort(key=lambda u: (u['first_name'] or u['username'] or '').lower())
        # пагинация
        total = len(items)
        page = max(1, page)
        per_page = max(8, min(10, per_page))  # 8–10
        start = (page - 1) * per_page
        end = start + per_page
        for u in items[start:end]:
            label = u['first_name'] or u['username'] or str(u['user_id'])
            if u['username']:
                label += f" (@{u['username']})"
            if citizens is not None and u['user_id'] not in citizens:
                label += " 🎫"
            rows.append([InlineKeyboardButton(
                text=label,
                callback_data=f"pickuser:{next_step}:{u['user_id']}"
            )])
        # навигация
        nav = []
        if page > 1:
            nav.append(InlineKeyboardButton(text="◀️ Назад", callback_data=f"pickuser:{next_step}:page:{page-1}"))
        if end < total:
            nav.append(InlineKeyboardButton(text="Вперёд ▶️", callback_data=f"pickuser:{next_step}:page:{page+1}"))
        if nav:
            rows.append(nav)
    rows.append([InlineKeyboardButton(text="✍️ Ввести вручную", callback_data=f"pickuser:{next_step}:manual")])
    rows.append([InlineKeyboardButton(text="🔙 Отмена", callback_data="admin:menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


@router.callback_query(F.data.startswith("pickuser:"))
async def pickuser_cb(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    parts = callback.data.split(":")
    if len(parts) < 3:
        return
    _, next_step = parts[0], parts[1]
    raw = ":".join(parts[2:]) if len(parts) > 2 else ""
    # пагинация
    if raw.startswith("page"):
        try:
            _, p = raw.split(":")
            page = int(p)
        except Exception:
            page = 1
        # определить флаги для данного next_step (status_pick нужно tourists_top)
        tourists_top = (next_step == "status_pick")
        mark_tourists = tourists_top or (next_step == "status_revoke")
        markup = await pilot_picker_markup(next_step, mark_tourists=mark_tourists, tourists_top=tourists_top, page=page)
        try:
            await callback.message.edit_reply_markup(reply_markup=markup)
        except Exception:
            await callback.message.answer("Выбери пилота:", reply_markup=markup)
        return
    if raw == "manual":
        await callback.message.answer(
            "Введи @username или числовой ID игрока:",
            reply_markup=cancel_keyboard()
        )
        return
    try:
        uid = int(raw)
    except Exception:
        return
    target = await get_user(uid)
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
        if not await can_view_status_panel(callback.from_user.id):
            await callback.message.answer("❌ Нет прав для выдачи статусов.")
            await state.clear()
            return
        await state.set_state(AdminStatuses.status_pick)
        await _send_status_picker(callback.message, target, callback.from_user.id)
    elif next_step == "status_revoke":
        have = await get_user_statuses(target['user_id'])
        have = [s for s in have if await can_grant_status(callback.from_user.id, s)]
        if not have:
            await callback.message.answer(f"У {target['first_name'] if 'first_name' in target.keys() else ''} нет статусов для снятия.")
            await state.clear()
            return
        await state.set_state(AdminStatuses.status_pick)
        await callback.message.answer(
            f"🚫 СНЯТИЕ СТАТУСА\n\n👤 {target['first_name'] if 'first_name' in target.keys() else ''}\n\n"
            f"{_status_current_line(have)}\n\nВыбери статус для снятия (⭐ — текущий):",
            reply_markup=_status_revoke_markup(have)
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
    if item.get('loot_only'):
        status = "🎯 только лут (в магазине нет)"
    else:
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
    if item.get('loot_only'):
        text += "\n🎯 Предмет — только лут: в магазине не продаётся, существует лишь как дроп."
    elif not item['is_available'] or item['stock'] == 0:
        if item['stock'] == 0:
            text += "\n⚠️ Предмет распродан. Верни его в магазин, указав количество."
        else:
            text += "\n⚠️ Предмет скрыт. Верни его в магазин, указав количество."
        rows.append([InlineKeyboardButton(text="➕ Вернуть в магазин", callback_data=f"storage:restock:{item_id}")])
    rows.append([InlineKeyboardButton(text="✏️ Редактировать (покупка: цена/фото/описание)",
                                      callback_data=f"edit_item:{item_id}")])
    rows.append([InlineKeyboardButton(text="🗑 Удалить из игры насовсем",
                                      callback_data=f"storage:purge:{item_id}")])
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
    cur_stock = item.get('stock')
    cur_text = "безлимит" if cur_stock == -1 else str(cur_stock)
    await callback.message.edit_text(
        f"📦 «{item['name']}» — сколько единиц вернуть в магазин?\n"
        f"Сейчас на складе: {cur_text}.\n\n"
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


@router.callback_query(F.data.startswith("storage:purge:"))
async def storage_purge(callback: CallbackQuery, state: FSMContext):
    """Удаление предмета из игры насовсем: запрос подтверждения вводом названия."""
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_storage"):
        return
    try:
        item_id = int(callback.data.split(":")[2])
    except (ValueError, IndexError):
        return
    item = await get_item(item_id)
    if not item:
        await callback.message.edit_text("❌ Предмет не найден.", reply_markup=storage_markup([]))
        return
    await state.update_data(storage_purge_id=item_id)
    await state.set_state(AdminStorageDelete.confirm)
    await callback.message.edit_text(
        f"🗑 Удалить «{item['name']}» из игры насовсем?\n\n"
        f"⚠️ Предмет пропадёт отовсюду: из Хранилища, магазина, инвентарей "
        f"игроков, снаряжения, дропов врагов, уловов рыбы и лотов рынка. "
        f"Восстановить его будет нельзя.\n\n"
        f"Для подтверждения введи точное название предмета:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Отмена", callback_data="admin:storage")]
        ])
    )


@router.message(AdminStorageDelete.confirm)
async def storage_purge_confirm(message: Message, state: FSMContext):
    if not await has_permission(message.from_user.id, "can_manage_storage"):
        await state.clear()
        await message.answer("❌ Нет прав.")
        return
    data = await state.get_data()
    item_id = data.get('storage_purge_id')
    if not item_id:
        await state.clear()
        await message.answer("❌ Сессия устарела. Зайди в Хранилище заново.")
        return
    item = await get_item(item_id)
    if not item:
        await state.clear()
        await message.answer("❌ Предмет не найден.")
        return
    if (message.text or "").strip() != item['name']:
        await message.answer(
            f"❌ Название не совпало. Удаление отменено.\n"
            f"Ожидалось: «{item['name']}»",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📦 В Хранилище", callback_data="admin:storage")]
            ])
        )
        await state.clear()
        return

    report = await delete_item_completely(item_id)
    await log_action(message.from_user.id, 'delete_item', None,
                     f"item={item['name']} id={item_id} full_delete report={report}")
    await state.clear()
    lines = [f"🗑 Предмет «{item['name']}» удалён из игры насовсем."]
    touched = {k: v for k, v in report.items() if v}
    if touched:
        lines.append("Удалено/очищено ссылок:")
        for table, n in sorted(touched.items(), key=lambda x: -x[1]):
            lines.append(f"• {table}: {n}")
    else:
        lines.append("Ссылок на него не было.")
    await message.answer("\n".join(lines),
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                             [InlineKeyboardButton(text="📦 В Хранилище", callback_data="admin:storage")]
                         ]))


@router.callback_query(F.data == "shop_admin:add")
async def shop_admin_add(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_add_items"):
        await callback.message.answer("❌ Нет прав на добавление товаров.")
        return
    await state.set_state(AdminAddItem.name)
    await callback.message.answer(
        "🛒 Добавление товара. Шаг 1/12\n\nВведи название товара (или /cancel):",
        reply_markup=cancel_keyboard()
    )


@router.message(AdminAddItem.name)
async def add_item_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await state.set_state(AdminAddItem.desc)
    await message.answer("Шаг 2/12 — Описание товара (или «-» если нет):",
                         reply_markup=cancel_keyboard())


@router.message(AdminAddItem.desc)
async def add_item_desc(message: Message, state: FSMContext):
    text = message.text.strip()
    await state.update_data(desc=None if text == "-" else text)
    await state.set_state(AdminAddItem.price)
    await message.answer("Шаг 3/12 — Цена в Нордмарках (целое число):",
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
    await message.answer(f"Шаг 4/12 — Цена продажи за {price}? Введи сумму (или «-» = половина):",
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
    await message.answer("Шаг 5/12 — Редкость:", reply_markup=rarity_choice_markup())


@router.callback_query(F.data.startswith("rar:"))
async def add_item_rarity(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    rarity = int(callback.data.split(":")[1])
    await state.update_data(rarity=rarity)
    await state.set_state(AdminAddItem.category)
    await callback.message.answer("Шаг 6/12 — Категория:", reply_markup=category_choice_markup())


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
    await callback.message.answer("Шаг 7/12 — Остаток на складе (или «-» = безлимит):",
                                  reply_markup=cancel_keyboard())


@router.callback_query(F.data.startswith("drinksel:"))
async def add_item_drink_choice(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    effect = callback.data.split(":", 1)[1]
    await state.update_data(drink_effect=None if effect in ("none", "") else effect)
    await state.set_state(AdminAddItem.stock)
    await callback.message.answer("Шаг 7/12 — Остаток на складе (или «-» = безлимит):",
                                  reply_markup=cancel_keyboard())


@router.message(AdminAddItem.plant_name)
async def add_item_plant_name(message: Message, state: FSMContext):
    text = message.text.strip()
    await state.update_data(plant_name=None if text in ("-", "—") else text)
    await state.set_state(AdminAddItem.stock)
    await message.answer("Шаг 7/12 — Остаток на складе (или «-» = безлимит):",
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
        await message.answer("Шаг 8/12 — Урон оружия (число), 0 если нет:",
                             reply_markup=cancel_keyboard())
        return
    if cat == 'equipment':
        await state.set_state(AdminAddItem.stats)
        await message.answer("Шаг 8/12 — Защита снаряжения (число), 0 если нет:",
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
            "Шаг 8/12 — Особый эффект оружия при попадании?\n"
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
                "Шаг 8/12 — На какую часть тела надевается?",
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
        f"Шаг 8/13 — Шанс, что «{WEAPON_EFFECT_LABELS[eff]}» сработает "
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
            "Шаг 8/13 — Штраф к точности врага, % (шанс врага промахнуться "
            "на 2 хода, 0–100):",
            reply_markup=cancel_keyboard())
    else:
        await message.answer("Шаг 8/13 — Урон эффекта за каждый ход (целое число):",
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
        "Шаг 9/13 — Кто продаёт этот товар?",
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
            "Шаг 9/13 (подшаг) — Введи @username или ID игрока, который продаёт этот товар "
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
        "Шаг 10/13 — Можно ли продавать этот предмет на РЫНКЕ "
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
    await _go_add_item_loot(callback.message, state)


async def _go_add_item_loot(message: Message, state: FSMContext):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    await state.set_state(AdminAddItem.loot)
    await message.answer(
        "Шаг 11/13 — 🎯 Это предмет ТОЛЬКО для лута врагов?\n"
        "Такие предметы не появляются в магазине вообще: они существуют "
        "лишь как дроп подземелий и выпадают игрокам.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🎯 Да, только лут", callback_data="lootonly:yes")],
            [InlineKeyboardButton(text="🏪 Нет, будет в магазине", callback_data="lootonly:no")],
        ])
    )


@router.callback_query(F.data.startswith("lootonly:"))
async def add_item_loot_choice(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    choice = callback.data.split(":")[1]
    await state.update_data(loot_only=1 if choice == "yes" else 0)
    await _go_add_item_status(callback.message, state)


async def _go_add_item_status(message: Message, state: FSMContext):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    statuses = await get_all_statuses()
    rows = []
    for s in statuses:
        rows.append([InlineKeyboardButton(
            text=f"🔓 {s['name']}", callback_data=f"addreq:{s['id']}")])
    rows.append([InlineKeyboardButton(text="➖ Без статуса", callback_data="addreq:none")])
    await state.set_state(AdminAddItem.status)
    await message.answer(
        "Шаг 12/13 — С какого статуса предмет доступен к покупке и использованию?\n"
        "В магазине он станет виден, когда игрок дойдёт до этого статуса "
        "(и на одну ступень раньше — как «цель»).",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows)
    )


@router.callback_query(F.data.startswith("addreq:"))
async def add_item_status_cb(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    val = callback.data.split(":")[1]
    if val == "none":
        tag = None
    else:
        s = await get_status(int(val))
        tag = s['access_tag'] if s else None
    await state.update_data(required_status=tag)
    await state.set_state(AdminAddItem.photo)
    await callback.message.answer(
        "Шаг 13/13 — Загрузи фото товара (или «-» если без фото):",
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
        required_status=data.get('required_status'),
        loot_only=data.get('loot_only', 0),
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
        f"\n🎯 Только лут: {'да (в магазине нет)' if data.get('loot_only') else 'нет'}"

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

    await _shop_cat_picker(callback.message, "del")


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


@router.callback_query(F.data == "del_item:back")
async def delete_item_back(callback: CallbackQuery):
    await callback.answer()
    await _shop_cat_picker(callback.message, "del")


async def _shop_cat_picker(message, mode: str):
    """Выбор раздела (категории) товара — как каталог в магазине. mode: edit|del."""
    items = await get_available_items()
    counts = {}
    for it in items or []:
        counts[it['category']] = counts.get(it['category'], 0) + 1
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    rows = []
    for key, cnt in sorted(counts.items(), key=lambda kv: -(kv[1] or 0)):
        label = ITEM_CATEGORIES.get(key, key)
        rows.append([InlineKeyboardButton(
            text=f"{label} ({cnt})",
            callback_data=f"shop_{mode}:cat:{key}:0")])
    if not rows:
        await message.edit_text("В магазине пока нет товаров.")
        return
    rows.append([InlineKeyboardButton(text="🔙 Назад", callback_data="admin:shop")])
    title = ("Выбери раздел для изменения товара:" if mode == "edit"
             else "Выбери раздел для удаления товара:")
    await message.edit_text(title, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))


async def _shop_cat_page(message, mode: str, category: str, page: int):
    """Список товаров внутри раздела, по 10 на страницу."""
    items = await get_available_items(category=category)
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    PER_I = 10
    items = items or []
    total = len(items)
    if total == 0:
        await _shop_cat_picker(message, mode)
        return
    pages = max(1, (total + PER_I - 1) // PER_I)
    page = max(0, min(page, pages - 1))
    start = page * PER_I
    chunk = items[start:start + PER_I]

    rows = []
    for it in chunk:
        if mode == "edit":
            rows.append([InlineKeyboardButton(text=it['name'],
                                              callback_data=f"edit_item:{it['id']}")])
        else:
            rows.append([InlineKeyboardButton(text=f"{it['name']} ({it['price']} НМ)",
                                              callback_data=f"del_item:{it['id']}")])
    nav = [InlineKeyboardButton(text=f"Стр. {page + 1}/{pages}", callback_data="noop")]
    if page > 0:
        nav.insert(0, InlineKeyboardButton(text="◀️", callback_data=f"shop_{mode}:cat:{category}:{page - 1}"))
    if page < pages - 1:
        nav.append(InlineKeyboardButton(text="▶️", callback_data=f"shop_{mode}:cat:{category}:{page + 1}"))
    rows.append(nav)
    rows.append([InlineKeyboardButton(text="🔙 К разделам", callback_data=f"shop_{mode}:cats")])
    label = ITEM_CATEGORIES.get(category, category)
    await message.edit_text(
        f"Раздел: {label} — товаров: {total}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))


@router.callback_query(F.data.startswith("shop_edit:cat:"))
async def shop_edit_cat_page_cb(callback: CallbackQuery):
    await callback.answer()
    parts = callback.data.split(":")
    cat = parts[2] if len(parts) > 2 else ""
    page = int(parts[3] or 0) if len(parts) > 3 else 0
    await _shop_cat_page(callback.message, "edit", cat, page)


@router.callback_query(F.data == "shop_edit:cats")
async def shop_edit_cats_cb(callback: CallbackQuery):
    await callback.answer()
    await _shop_cat_picker(callback.message, "edit")


@router.callback_query(F.data.startswith("shop_del:cat:"))
async def shop_del_cat_page_cb(callback: CallbackQuery):
    await callback.answer()
    parts = callback.data.split(":")
    cat = parts[2] if len(parts) > 2 else ""
    page = int(parts[3] or 0) if len(parts) > 3 else 0
    await _shop_cat_page(callback.message, "del", cat, page)


@router.callback_query(F.data == "shop_del:cats")
async def shop_del_cats_cb(callback: CallbackQuery):
    await callback.answer()
    await _shop_cat_picker(callback.message, "del")


@router.callback_query(F.data == "shop_admin:edit")
async def shop_admin_edit(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_edit_items"):
        await callback.message.answer("❌ Нет прав на изменение товаров.")
        return
    await _shop_cat_picker(callback.message, "edit")


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
            [InlineKeyboardButton(text="♻ Регенерация % (от лечения)", callback_data="field:regen")],
            [InlineKeyboardButton(text="🛡️ Броня", callback_data="field:armor")],
            [InlineKeyboardButton(text="⚡ AP за использование", callback_data="field:ap_cost")],
            [InlineKeyboardButton(text="🔒 Статус доступа (покупка/использование)", callback_data="field:required_status")],
            [InlineKeyboardButton(text="🖼 Картинка", callback_data="field:photo")],
            [InlineKeyboardButton(text="🍺 Тип напитка (действие)", callback_data="field:drink")],
            [InlineKeyboardButton(text="🌳 Растение в кадке (семечко)", callback_data="field:plant_name")],
            [InlineKeyboardButton(text="🏪 Рынок (вкл/выкл)", callback_data="field:market_ok")],
            [InlineKeyboardButton(text="🎯 Только лут (вкл/выкл)", callback_data="field:loot_only")],
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
    item = await get_item(item_id) if item_id else None
    if item:
        rows.append([InlineKeyboardButton(text="🔙 Назад", callback_data=f"edit_item:{item_id}")])
    cur_tag = item.get('required_status') if item else None
    cur_label = "— нет"
    if cur_tag:
        for s in statuses:
            if s.get('access_tag') == cur_tag:
                cur_label = f"{s['name']} ({s.get('access_tag')})"
                break
        else:
            cur_label = cur_tag
    await callback.message.edit_text(
        f"🔒 Статус доступа «{item['name'] if item else 'товар'}».\n"
        f"Сейчас: {cur_label}.\n\n"
        f"С какого статуса предмет доступен к покупке и использованию?\n"
        f"В магазине он станет виден, когда игрок дойдёт до этого статуса "
        f"(и на одну ступень раньше — как «цель»).",
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
    data = await state.get_data()
    item = await get_item(data.get('item_id')) if data.get('item_id') else None
    await state.set_state(AdminEditItem.photo)
    name = item['name'] if item else 'товар'
    has_photo = bool(item and item.get('photo_file_id'))
    text = (f"🖼 Фото товара «{name}» (сейчас: {'есть' if has_photo else 'нет'}).\n"
            f"Отправь новое фото — или «-», чтобы убрать картинку:")
    if has_photo:
        try:
            await callback.message.answer_photo(
                item['photo_file_id'], caption=text, reply_markup=cancel_keyboard())
            return
        except Exception:
            pass
    await callback.message.answer(text, reply_markup=cancel_keyboard())


@router.callback_query(F.data == "field:weapon_effect")
async def edit_item_field_weapon_effect(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    item = await get_item(data.get('item_id')) if data.get('item_id') else None
    cur = item.get('weapon_effect') if item else None
    cur_label = WEAPON_EFFECT_LABELS.get(cur, "🚫 Без эффекта") if cur else "🚫 Без эффекта"
    head = (f"☠️ Эффект оружия у «{item['name'] if item else 'товар'}»:\n"
            f"Сейчас: {cur_label}.\n\n")
    await callback.message.edit_text(
        head + "Выбери особый эффект оружия при попадании:\n"
        f"При «Без эффекта» шанс и урон эффекта обнуляются.",
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


@router.callback_query(F.data == "field:loot_only")
async def edit_item_field_loot_toggle(callback: CallbackQuery, state: FSMContext):
    """Вкл/выкл флага «только лут» (предмет не продаётся в магазине)."""
    await callback.answer()
    data = await state.get_data()
    item_id = data.get('item_id')
    item = await get_item(item_id) if item_id else None
    if not item:
        await state.clear()
        await callback.message.answer("❌ Товар не найден.")
        return
    new_val = 0 if item.get('loot_only') else 1
    await update_item(item_id, loot_only=new_val)
    await log_action(callback.from_user.id, 'edit_item', None,
                     f"item_id={item_id} loot_only={new_val}")
    label = "только лут (в магазине нет)" if new_val else "продаётся в магазине"
    await callback.message.answer(f"✅ «{item['name']}»: 🎯 Только лут → {label}.")
    await state.clear()


EDIT_ITEM_FIELD_LABELS = {
    "name": "Название",
    "price": "Цена",
    "sell_price": "Цена продажи",
    "stock": "Остаток",
    "category": "Категория",
    "description": "Описание",
    "damage": "⚔️ Урон (оружие)",
    "weapon_effect_chance": "☠️ Шанс эффекта (%)",
    "weapon_effect_dmg": "☠️ Урон эффекта/ход",
    "heal": "❤️ Лечение",
    "regen": "♻ Регенерация % (от лечения)",
    "armor": "🛡️ Броня",
    "crit_chance": "💥 Шанс крита, %",
    "crit_mult": "💥 Множитель крита (0 = не менять базовый ×1.4)",
    "ap_cost": "⚡ AP за использование",
    "plant_name": "🌳 Растение в кадке (семечко)",
    "loot_only": "🎯 Только лут (вкл/выкл)",
    "is_available": "Продажа (вкл/выкл)",
    "rarity": "🔆 Редкость",
    "housing_type": "🏠 Тип жилья (дом)",
    "housing_slots": "🏠 Слотов жилья",
}


def _item_field_current_value(item, field):
    val = item.get(field)
    if field == "stock":
        return "безлимит" if val is None or val == -1 else str(val)
    if field == "is_available":
        return "✅ в продаже" if val else "🚫 снят с продажи"
    if field == "loot_only":
        return "🎯 только лут" if val else "в магазине"
    if field == "regen":
        return "выкл (0)" if not val else f"{val}% от лечения (затухает за 3 хода)"
    if field in ("rarity", "housing_slots"):
        return "—" if val is None else str(val)
    if field in ("description", "plant_name", "housing_type"):
        return (val or "—")
    if val is None:
        return None
    return str(val)


@router.callback_query(F.data.startswith("field:"))
async def edit_item_field(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    field = callback.data.split(":")[1]
    data = await state.get_data()
    item = await get_item(data.get('item_id')) if data.get('item_id') else None
    if not item:
        await state.clear()
        await callback.message.answer("❌ Товар не найден.")
        return
    label = EDIT_ITEM_FIELD_LABELS.get(field)
    current = _item_field_current_value(item, field)
    await state.update_data(field=field)
    await state.set_state(AdminEditItem.value)
    if label and current is not None:
        head = (f"✏️ {label} товара «{item['name']}».\n"
                f"Сейчас: {current}.\n\n")
    else:
        head = f"✏️ Товар «{item['name']}».\n\n"
    await callback.message.answer(head + "Введи новое значение (или «-» для очистки/безлимита):",
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
                   "housing_slots", "regen"):
        if field == "housing_slots" and text == "-":
            value = None
        elif text == "-" and field in ("stock", "weapon_effect_chance",
                                      "weapon_effect_dmg", "regen"):
            value = -1 if field == "stock" else 0
        else:
            value = int(text)
    else:
        value = None if text == "-" else text

    if field == "weapon_effect_chance":
        if not 0 <= value <= 100:
            await message.answer("❌ Шанс эффекта от 0 до 100:", reply_markup=cancel_keyboard())
            return
    if field == "regen":
        if not 0 <= value <= 100:
            await message.answer("❌ Регенерация от 0 до 100 (рекомендуется 40):",
                                 reply_markup=cancel_keyboard())
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

async def _can_view_finance(actor_id: int) -> bool:
    """Посмотреть казну и статистику — без права тратить.

    can_view_balances — режим «только чтение»: видно баланс, долги и статистику,
    но кнопки выдачи нет, а сам treasury:give всё равно спрашивает
    can_manage_finance. can_manage_finance подразумевает и просмотр.
    """
    return (await has_permission(actor_id, "can_manage_finance")
            or await has_permission(actor_id, "can_view_balances"))


@router.callback_query(F.data == "admin:finance")
async def admin_finance(callback: CallbackQuery):
    await callback.answer()
    if not (await _can_view_finance(callback.from_user.id)
            or await has_permission(callback.from_user.id, "can_add_currency")
            or await has_permission(callback.from_user.id, "can_remove_currency")):
        await callback.message.answer("❌ Нет прав для работы с финансами.")
        return
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    can_add = await has_permission(callback.from_user.id, "can_add_currency")
    can_remove = await has_permission(callback.from_user.id, "can_remove_currency")
    can_full = await has_permission(callback.from_user.id, "can_manage_finance")
    can_look = await has_permission(callback.from_user.id, "can_view_balances")

    buttons = []
    if can_add:
        buttons.append([InlineKeyboardButton(text="Начислить НМ", callback_data="fin:nord:add")])
    if can_remove:
        buttons.append([InlineKeyboardButton(text="Списать НМ", callback_data="fin:nord:sub")])
    if can_full:
        buttons.append([InlineKeyboardButton(text="🏛️ Казна", callback_data="admin:treasury")])
        buttons.append([InlineKeyboardButton(text="📊 Налог на отчёты", callback_data="admin:tax")])
        buttons.append([InlineKeyboardButton(text="📊 Налог на продажи", callback_data="admin:saletax")])
        buttons.append([InlineKeyboardButton(text="💰 Зарплаты", callback_data="admin:salaries")])
    elif can_look:
        # Казна доступна только на чтение: кнопки выдачи внутри не будет.
        buttons.append([InlineKeyboardButton(text="🏛️ Казна (только просмотр)", callback_data="admin:treasury")])
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="admin:menu")])

    title = "💰 ФИНАНСЫ\n\nВыберите операцию:"
    if not can_full:
        title = ("💰 ФИНАНСЫ\n\n"
                 "Вам доступно начисление и просмотр казны. "
                 "Тратить из казны и менять налоги может только владелец.")
    await callback.message.edit_text(
        title,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )


@router.callback_query(F.data == "admin:treasury")
async def admin_treasury(callback: CallbackQuery):
    await callback.answer()
    if not await _can_view_finance(callback.from_user.id):
        await callback.message.answer("❌ Нет прав для просмотра казны.")
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
    can_spend = await has_permission(callback.from_user.id, "can_manage_finance")
    rows = []
    if can_spend:
        rows.append([InlineKeyboardButton(text="💸 Выдать из казны", callback_data="treasury:give")])
    rows.append([InlineKeyboardButton(text="📊 Статистика казны", callback_data="treasury:stats")])
    rows.append([InlineKeyboardButton(text="📋 Долги по выплатам", callback_data="treasury:debts")])
    rows.append([InlineKeyboardButton(text="🔙 В финансы", callback_data="admin:finance")])
    await callback.message.edit_text(
        f"🏛️ КАЗНА НОРДХАЙМА\n\n"
        f"Баланс: {balance} {plural_nordmark(balance)}"
        f"{warn}\n\n"
        f"Налог с отчётов и пожертвования пополняют казну.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows)
    )


@router.callback_query(F.data == "treasury:debts")
async def treasury_debts(callback: CallbackQuery):
    await callback.answer()
    if not await _can_view_finance(callback.from_user.id):
        await callback.message.answer("❌ Нет прав для просмотра казны.")
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
    if not await _can_view_finance(callback.from_user.id):
        await callback.message.answer("❌ Нет прав для просмотра казны.")
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
        # ОД (AP) из меню финансов убраны намеренно: они восстанавливаются
        # сами и выдаются только через механики игры.
        await message.answer("❌ Эта операция недоступна.")
        await state.clear()
        return

    await log_action(admin, 'finance', target_id, f"{currency} {action} {amount}")
    await state.clear()
    await message.answer(
        f"✅ Игроку {data['target_name']} {verb} {amount} {unit}."
    )


# ============ РОЛИ ============

async def _delegable_roles(admin_id: int) -> list:
    """Роли, которые admin_id может назначить/снять помимо полного доступа."""
    out = []
    for role, perm in DELEGABLE_ROLES.items():
        if await has_permission(admin_id, perm):
            out.append(role)
    return out


@router.callback_query(F.data == "admin:roles")
async def admin_roles(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    # Полный доступ — только Хранитель. Глава МВД видит панель, но внутри ему
    # доступна единственная роль — вице-доминус (его помощник).
    full = await has_permission(callback.from_user.id, "can_manage_admins")
    deleg = await _delegable_roles(callback.from_user.id)
    if not full and not deleg:
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
    from keyboards.keyboards import back_to_main
    full = await has_permission(callback.from_user.id, "can_manage_admins")
    deleg = await _delegable_roles(callback.from_user.id)
    if action == "add":
        # Выдача: полный доступ — весь список, кроме super_admin (выдаётся только
        # командой — защита). Глава МВД видит лишь те роли, которые ему делегированы.
        source = ROLES.keys() if full else deleg
        for role_name in source:
            if role_name == "super_admin":
                continue
            rows.append([InlineKeyboardButton(text=role_label(role_name), callback_data=f"role:{role_name}")])
        if not rows:
            await state.clear()
            await callback.message.edit_text(
                "Нет ролей, которые тебе доступны для выдачи.",
                reply_markup=back_to_main()
            )
            return
        prompt = "Выбери роль для выдачи:"
    else:
        # Снятие: только роли, выданные этому игроку (не весь список).
        user_roles = await get_user_role(data['target_id'])
        allowed = set(ROLES.keys()) if full else set(deleg)
        for role_name in ROLES:
            if role_name in user_roles and role_name in allowed:
                rows.append([InlineKeyboardButton(text=role_label(role_name), callback_data=f"role:{role_name}")])
        if not rows:
            await state.clear()
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


# ============ ОПОВЕЩЕНИЯ: ЧАТ И ТОПИК ============

@router.message(Command("chatinfo"))
async def admin_chatinfo(message: Message):
    """Показать параметры текущего чата (супер-админ).

    Нужно, чтобы настроить оповещения в конкретный топик супергруппы: отправьте
    эту команду прямо в нужной теме — бот покажет id чата и id топика, а кнопками
    можно сразу сохранить их как чат/топик оповещений.
    """
    if 'super_admin' not in await get_user_role(message.from_user.id):
        await message.answer("❌ Команда только для супер-админа.")
        return
    chat = message.chat
    thread = getattr(message, "message_thread_id", None)
    cur_chat, cur_topic = await get_news_chat()
    lines = [
        "📍 ПАРАМЕТРЫ ЭТОГО ЧАТА\n",
        f"chat_id: <code>{chat.id}</code>",
        f"тип: <code>{chat.type}</code>",
        f"топик (message_thread_id): <code>{thread if thread else '— (общий раздел)'}</code>",
        f"forum: <code>{getattr(chat, 'is_forum', '—')}</code>",
        "",
        "Сейчас оповещения идут: "
        + (f"чат <code>{cur_chat}</code>, топик <code>{cur_topic if cur_topic else '— общий раздел'}</code>"
           if cur_chat else "<b>никуда — чат не настроен</b>"),
    ]
    rows = []
    if chat.type in ("supergroup", "channel"):
        rows.append([InlineKeyboardButton(
            text="📌 Сделать этот чат чатом оповещений",
            callback_data=f"news:chat:{chat.id}:{thread or 0}")])
    if thread:
        rows.append([InlineKeyboardButton(
            text="🧵 Топик для оповещений (этот чат)",
            callback_data=f"news:topic:{chat.id}:{thread}")])
    if cur_chat:
        rows.append([InlineKeyboardButton(
            text="♻️ Без топика (общий раздел чата)",
            callback_data=f"news:topic:{cur_chat}:0")])
    if rows:
        rows.append([InlineKeyboardButton(
            text="🔕 Выключить оповещения", callback_data="news:off")])
    if chat.type != "private":
        # Рабочий чат: бот отвечает и показывает меню, как в личке.
        # (Чат оповещений всегда остаётся «только для исходящих оповещений».)
        if chat.id in await get_allowed_chats():
            rows.append([InlineKeyboardButton(
                text="🚫 Запретить работу бота в этом чате",
                callback_data=f"news:disallow:{chat.id}")])
        else:
            rows.append([InlineKeyboardButton(
                text="➕ Разрешить работу бота в этом чате",
                callback_data=f"news:allow:{chat.id}")])
    await message.answer("\n".join(lines),
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=rows) if rows else None)


@router.callback_query(F.data.startswith("news:"))
async def admin_news_chat(callback: CallbackQuery):
    await callback.answer()
    if 'super_admin' not in await get_user_role(callback.from_user.id):
        await callback.message.answer("❌ Настройка оповещений только для супер-админа.")
        return
    _, action, *rest = callback.data.split(":")
    if action == "off":
        await set_news_chat(None, None)
        from utils.chat_guard import reset_cache
        reset_cache()
        await log_action(callback.from_user.id, 'set_news_chat', None, 'disabled')
        await callback.message.answer("🔕 Игровые оповещения выключены.")
        return
    chat_id = int(rest[0])
    thread = int(rest[1]) if len(rest) > 1 and rest[1] != "0" else None
    if action in ("allow", "disallow"):
        cur_allowed = await get_allowed_chats()
        if action == "allow":
            if chat_id not in cur_allowed:
                cur_allowed.append(chat_id)
            await set_allowed_chats(cur_allowed)
            from utils.chat_guard import reset_cache
            reset_cache()
            await log_action(callback.from_user.id, 'set_news_chat', None,
                             f"allow_chat={chat_id}")
            extra = ""
            cur_news, _ = await get_news_chat()
            if cur_news and int(cur_news) == chat_id:
                extra = ("\n⚠️ Это же чат оповещений: бот туда только отправляет "
                         "оповещения, команды игроков по-прежнему игнорирует. "
                         "Для рабочего чата возьмите другую группу/топик.")
            await callback.message.answer(
                f"✅ Бот работает в чате <code>{chat_id}</code> как в личке.{extra}")
            return
        await set_allowed_chats([c for c in cur_allowed if c != chat_id])
        from utils.chat_guard import reset_cache
        reset_cache()
        await log_action(callback.from_user.id, 'set_news_chat', None,
                         f"disallow_chat={chat_id}")
        await callback.message.answer(
            f"🚫 Бот больше не обслуживает команды в чате <code>{chat_id}</code>.\n"
            f"Оповещения в него приходят по-прежнему, если он настроен как чат оповещений.")
        return
    if action == "chat":
        await set_news_chat(chat_id, thread)
    elif action == "topic":
        await set_news_chat(chat_id, thread)
    from utils.chat_guard import reset_cache
    reset_cache()
    await log_action(callback.from_user.id, 'set_news_chat', None,
                     f"chat={chat_id} topic={thread}")
    where = f"топик <code>{thread}</code>" if thread else "общий раздел чата"
    await callback.message.answer(f"✅ Оповещения будут идти в чат <code>{chat_id}</code>, {where}.")


# ============ СТАТУСЫ ============

@router.callback_query(F.data == "admin:statuses")
async def admin_statuses(callback: CallbackQuery):
    await callback.answer()
    can_manage = await has_permission(callback.from_user.id, "can_manage_statuses")
    can_grant = await has_permission(callback.from_user.id, "can_grant_statuses")
    can_citizen = await has_permission(callback.from_user.id, "can_grant_citizen_status")
    if not (can_manage or can_grant or can_citizen):
        await callback.message.answer("❌ Нет прав для управления статусами.")
        return

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    rows = []
    if can_manage:
        rows.append([InlineKeyboardButton(text="➕ Создать статус", callback_data="st:create")])
        rows.append([InlineKeyboardButton(text="❌ Удалить статус", callback_data="st:delete")])
    if can_manage or can_grant:
        rows.append([InlineKeyboardButton(text="🎁 Выдать статус игроку", callback_data="st:grant")])
        rows.append([InlineKeyboardButton(text="🚫 Снять статус у игрока", callback_data="st:revoke")])
    elif can_citizen:
        # Глава МВД принимает в гражданство и снимает гражданство — тот же вход,
        # но дальше ему показывается только статус-ворота («Рекрут»).
        rows.append([InlineKeyboardButton(text="🎫 Принять в гражданство", callback_data="st:grant")])
        rows.append([InlineKeyboardButton(text="🚫 Снять гражданство", callback_data="st:revoke")])
    rows.append([InlineKeyboardButton(text="📋 Список статусов", callback_data="st:list")])
    rows.append([InlineKeyboardButton(text="🔙 В меню", callback_data="admin:menu")])
    title = "🎖️ УПРАВЛЕНИЕ СТАТУСАМИ\n\nВыбери действие:"
    if can_citizen and not can_manage and not can_grant:
        title = ("🎖️ ПРИЁМ В ГРАЖДАНСТВО\n\n"
                 "Ты можешь выдать и снять статус «Рекрут» — он открывает "
                 "гражданство Нордхайма. Остальные статусы выдаёт владелец.\n\n"
                 "Выбери действие:")
    await callback.message.edit_text(
        title,
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


def _status_top(have):
    """Старший статус пилота по иерархии (наибольший sort_order)."""
    if not have:
        return None
    return max(have, key=lambda s: (s['sort_order'] or 0, s['id'] or 0))


def _status_current_line(have) -> str:
    """Строка «текущий статус» — старший в иерархии + остальные имеющиеся."""
    top = _status_top(have)
    if not top:
        return "⭐ Текущий статус: нет (статусы не выданы)"
    rest = [s['name'] for s in have if s['id'] != top['id']]
    line = f"⭐ Текущий статус: {top['name']} (уровень {top['sort_order']})"
    if rest:
        line += f"\n📋 Ещё есть: {', '.join(rest)}"
    return line


def _status_grant_markup(statuses, have, legioner: bool = False):
    """Клавиатура выдачи: ⭐ текущий, ✅ уже есть, ➕ выдать. Порядок — по иерархии."""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    top = _status_top(have)
    have_ids = {s['id'] for s in have}
    rows = []
    for s in sorted(statuses, key=lambda x: (x['sort_order'] or 0, x['id'] or 0)):
        # Легионера фильтруем ЗДЕСЬ, а не только в вызывающем коде: иначе кнопка
        # «➕ 🦅 Легионер» всё равно рисуется и нажатие уходит в отказ. Общая выдача
        # ставит только строку user_statuses, без флага users.legioner — получился бы
        # легионер без кепа и без запрета голосовать. Настоящая выдача — st:legioner.
        if s.get('access_tag') == LEGIONER_ACCESS_TAG:
            continue
        if top and s['id'] == top['id']:
            text = f"⭐ {s['name']} — сейчас"
        elif s['id'] in have_ids:
            text = f"✅ {s['name']} — уже есть"
        else:
            text = f"➕ {s['name']}"
        rows.append([InlineKeyboardButton(text=text, callback_data=f"st_pick:{s['id']}")])
    # Легионер выдаётся отдельной кнопкой (вариант А), а не через общий список:
    # он не ступень карьеры, а роль с пониженными правами, и ставится вместе
    # с флагом users.legioner — иначе кеп и голосование не заработают.
    if legioner is not None:
        rows.append([InlineKeyboardButton(
            text=("🦅 Снять легионерский флаг" if legioner
                  else "🦅 Сделать легионером"),
            callback_data="st:legioner")])
    rows.append([InlineKeyboardButton(text="🚫 Снять статус этому пилоту", callback_data="st:revoke")])
    rows.append([InlineKeyboardButton(text="🔙 Выбрать другого пилота", callback_data="st:grant")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _status_revoke_markup(have):
    """Клавиатура снятия: только статусы пилота, ⭐ отмечает текущий."""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    top = _status_top(have)
    rows = []
    for s in sorted(have, key=lambda x: (x['sort_order'] or 0, x['id'] or 0)):
        mark = "⭐ " if top and s['id'] == top['id'] else ""
        rows.append([InlineKeyboardButton(text=f"{mark}Снять: {s['name']}",
                                          callback_data=f"st_rev:{s['id']}")])
    rows.append([InlineKeyboardButton(text="🔙 Выбрать другого пилота", callback_data="st:revoke")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def _send_status_picker(chat, target, actor_id: int):
    """Экран выдачи статуса: сначала текущий статус пилота, затем выбор статуса.

    actor_id — кто нажал кнопку (у chat.from_user брать нельзя: у сообщения с
    кнопкой from_user — это автор сообщения, а не нажавший).
    """
    statuses = await get_all_statuses()
    if not statuses:
        await chat.answer("❌ Сначала создай хотя бы один статус.")
        return False
    # Актёр видит только те статусы, которые ему разрешено выдать. Глава МВД
    # тут видит ровно «Рекрут» — ворота в гражданство.
    statuses = [s for s in statuses if await can_grant_status(actor_id, s)]
    # Отдельная кнопка Легионера нужна только тем, кто вправе его выдать.
    can_legioner = await can_grant_status(
        actor_id, await get_status_by_tag(LEGIONER_ACCESS_TAG))
    if not statuses and not can_legioner:
        await chat.answer("❌ Нет статусов, которые тебе доступны для выдачи.")
        return False
    # Легионера из общего списка убирает сама _status_grant_markup — правило
    # «легионер только через st:legioner» держится в одном месте.
    have = await get_user_statuses(target['user_id'])
    who = (target['first_name'] if 'first_name' in target.keys() else '') or str(target['user_id'])
    if target['username']:
        who += f" (@{target['username']})"
    # 🎫 — гражданства ещё нет: сразу видно прямо на экране статуса.
    # Без parse_mode (в админке он не задан) — поэтому без **жирного**.
    # Про Штаб ВВС здесь ничего не обещаем: фильтр пилотов по гражданству
    # ещё не сделан (пункт в PLAN.md), текст должен быть правдой.
    no_cit = target['user_id'] not in await citizen_user_ids()
    warn = ("🎫 Турист: гражданства Нордхайма пока нет.\n"
            "Гражданство — это статус от «Рекрута» и выше.\n\n") if no_cit else ''
    leg = await is_legioner(target['user_id'])
    leg_note = ("\n🦅 Пилот — легионер: доступы не выше Ветерана, голосовать нельзя.\n"
                if leg else "")
    text = (
        "🎖 СТАТУС ПИЛОТА\n\n"
        f"👤 {who}\n"
        f"🆔 {target['user_id']}\n\n"
        f"{warn}"
        f"{_status_current_line(have)}\n\n"
        f"{leg_note}"
        "Выбери статус для выдачи. Список снизу вверх — от слабого к сильному."
    )
    await chat.answer(
        text,
        reply_markup=_status_grant_markup(
            statuses, have, legioner=leg if can_legioner else None))
    return True


@router.callback_query(F.data == "st:legioner")
async def status_legioner_toggle(callback: CallbackQuery, state: FSMContext):
    """Вариант А выдачи Легионера: одна кнопка ставит и снимает флаг.

    Флаг (users.legioner) — это права: кеп доступа «не выше Ветерана» и запрет
    голосования. Строка статуса «🦅 Легионер» — это отображение: именно она
    появляется в меню выбора статуса, чтобы игрок сам поставил её себе. Поэтому
    кнопка делает оба действия разом — иначе получится легионер без прав или
    статус без кепа.
    """
    await callback.answer()
    if not await can_view_status_panel(callback.from_user.id):
        await callback.message.answer("❌ Нет прав для выдачи статусов.")
        return
    st = await get_status_by_tag(LEGIONER_ACCESS_TAG)
    if not st:
        await callback.message.answer("❌ Статус «Легионер» не найден в базе.")
        return
    if not await can_grant_status(callback.from_user.id, st):
        await callback.message.answer("❌ Этот статус тебе выдавать нельзя.")
        return
    data = await state.get_data()
    target_id = data.get('target_id')
    if not target_id:
        await callback.message.answer("❌ Сессия устарела, начни заново.")
        return
    name = data.get('target_name') or str(target_id)
    was = await is_legioner(target_id)
    if was:
        await set_legioner(target_id, False)
        await revoke_status(target_id, st['id'])
        await log_action(callback.from_user.id, 'revoke_legioner', target_id)
        text = f"🦅 Снят легионерский статус: {name}"
    else:
        await set_legioner(target_id, True)
        granted, why = await grant_status(target_id, st['id'], callback.from_user.id)
        if not granted:
            # Флаг уже стоит, но прав на строку статуса нет — честно откатываем,
            # иначе пилот останется «легионером без статуса», т.е. без кепа.
            await set_legioner(target_id, False)
            await callback.message.answer(f"❌ Статус не выдан: {why}")
            return
        await log_action(callback.from_user.id, 'grant_legioner', target_id)
        text = (f"🦅 Пилот — легионер: {name}\n"
                "Доступы не выше Ветерана, голосовать нельзя.\n"
                "Статус «🦅 Легионер» игрок выбирает себе сам в профиле.")
    have = await get_user_statuses(target_id)
    target = await find_user(str(target_id))
    await _send_status_picker(callback.message, target or {'user_id': target_id},
                              callback.from_user.id)
    await callback.message.answer(f"{text}\n\n{_status_current_line(have)}")


@router.callback_query(F.data == "st:grant")
async def status_grant_target(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await can_view_status_panel(callback.from_user.id):
        await callback.message.answer("❌ Нет прав для выдачи статусов.")
        return
    await state.set_state(AdminStatuses.target)
    markup = await pilot_picker_markup("status_pick", mark_tourists=True, tourists_top=True)
    await callback.message.answer(
        "Выбери пилота для выдачи статуса:\n"
        "🎫 — ещё турист, гражданства Нордхайма нет "
        "(гражданство = статус от «Рекрута» и выше).",
        reply_markup=markup)


@router.message(AdminStatuses.target)
async def status_grant_target_msg(message: Message, state: FSMContext):
    if not await can_view_status_panel(message.from_user.id):
        await message.answer("❌ Нет прав для выдачи статусов.")
        await state.clear()
        return
    target = await find_user(message.text)
    if not target:
        await message.answer("❌ Игрок не найден. Попробуй ещё раз:")
        return
    await state.update_data(target_id=target['user_id'],
                            target_name=target['first_name'] if 'first_name' in target.keys() else '')
    await state.set_state(AdminStatuses.status_pick)
    await _send_status_picker(message, target, message.from_user.id)


@router.callback_query(F.data.startswith("st_rev:"))
async def status_revoke_pick(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await can_view_status_panel(callback.from_user.id):
        await callback.message.answer("❌ Нет прав для снятия статусов.")
        return
    status_id = int(callback.data.split(":")[1])
    data = await state.get_data()
    target_id = data.get('target_id')
    if not target_id:
        await callback.message.answer("❌ Сессия устарела, начни заново.")
        return
    s = await get_status(status_id)
    if not await can_grant_status(callback.from_user.id, s):
        await callback.message.answer(
            "❌ Этот статус тебе выдавать/снимать нельзя.")
        return
    # Страховка от подделанного callback_data: Легионер выдаётся только через
    # st:legioner, где флаг users.legioner ставится вместе со строкой статуса.
    # Через st_pick он получил бы только строку — то есть отображение без прав.
    if s and s['access_tag'] == LEGIONER_ACCESS_TAG:
        await callback.message.answer(
            "❌ Легионера выдают отдельной кнопкой «🦅 Сделать легионером» — "
            "она ставит флаг и статус разом.")
        return
    await revoke_status(target_id, status_id)
    await log_action(callback.from_user.id, 'revoke_status', target_id, f"status={s['name']}" if s else f"status_id={status_id}")
    have = await get_user_statuses(target_id)
    name = data.get('target_name') or str(target_id)
    await state.clear()
    await callback.message.answer(
        f"🚫 Статус «{s['name'] if s else status_id}» снят: {name}\n\n{_status_current_line(have)}"
    )


@router.callback_query(F.data == "st:revoke")
async def status_revoke_target(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await can_view_status_panel(callback.from_user.id):
        await callback.message.answer("❌ Нет прав для снятия статусов.")
        return
    data = await state.get_data()
    target_id = data.get('target_id')
    if not target_id:
        await state.set_state(AdminStatuses.target)
        markup = await pilot_picker_markup("status_revoke", mark_tourists=True)
        await callback.message.answer(
            "У кого снять статус? Выбери пилота (🎫 — ещё без гражданства):",
            reply_markup=markup)
        return
    target = await get_user(target_id)
    if not target:
        await callback.message.answer("❌ Пилот не найден.")
        return
    have = await get_user_statuses(target_id)
    # Глава МВД снимает только гражданство (статус-ворота), не любой статус.
    have = [s for s in have if await can_grant_status(callback.from_user.id, s)]
    if not have:
        who = (target['first_name'] if 'first_name' in target.keys() else '') or str(target_id)
        await callback.message.answer(
            f"У {who} нет статусов, которые тебе доступно снять.")
        return
    who = (target['first_name'] if 'first_name' in target.keys() else '') or str(target_id)
    await callback.message.answer(
        f"🚫 СНЯТИЕ СТАТУСА\n\n👤 {who}\n\n{_status_current_line(have)}\n\n"
        "Выбери статус для снятия (⭐ — текущий):",
        reply_markup=_status_revoke_markup(have)
    )


@router.callback_query(F.data.startswith("st_pick:"))
async def status_grant_pick(callback: CallbackQuery, state: FSMContext):
    """Выдача статуса с одного нажатия: кнопка статуса → статус выдан."""
    await callback.answer()
    if not await can_view_status_panel(callback.from_user.id):
        await callback.message.answer("❌ Нет прав для выдачи статусов.")
        return
    status_id = int(callback.data.split(":")[1])
    data = await state.get_data()
    target_id = data.get('target_id')
    if not target_id:
        await callback.message.answer("❌ Сессия устарела, начни заново.")
        return
    s = await get_status(status_id)
    if not await can_grant_status(callback.from_user.id, s):
        await callback.message.answer(
            "❌ Этот статус тебе выдавать нельзя. Обратись к владельцу.")
        return
    name = data.get('target_name') or str(target_id)
    ok, msg = await grant_status(target_id, status_id, callback.from_user.id)
    if ok:
        await log_action(callback.from_user.id, 'grant_status', target_id,
                         f"status={s['name'] if s else status_id}")
    have = await get_user_statuses(target_id)
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    await callback.message.answer(
        f"{'✅' if ok else 'ℹ️'} {msg}: {name}\n"
        f"Статус: «{s['name'] if s else status_id}»\n\n"
        f"{_status_current_line(have)}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🎖 Выдать ещё", callback_data="st:more")],
            [InlineKeyboardButton(text="🔙 В управление статусами", callback_data="admin:statuses")],
        ])
    )


@router.callback_query(F.data == "st:more")
async def status_grant_more(callback: CallbackQuery, state: FSMContext):
    """Вернуться к списку статусов того же пилота (выдать несколько подряд)."""
    await callback.answer()
    if not await can_view_status_panel(callback.from_user.id):
        await callback.message.answer("❌ Нет прав для выдачи статусов.")
        return
    data = await state.get_data()
    target_id = data.get('target_id')
    target = await get_user(target_id) if target_id else None
    if not target:
        await callback.message.answer("❌ Сессия устарела, начни заново.")
        return
    await state.set_state(AdminStatuses.status_pick)
    await _send_status_picker(callback.message, target, callback.from_user.id)


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
    await state.update_data(bonuses={})
    await state.set_state(AdminAwards.name)
    await callback.message.answer(
        "🏅 Создание награды. Шаг 1 — название (например: «За отвагу», «Герой Нордхайма»).\n"
        f"Бонусы задашь далее, в конце покажу превью:",
        reply_markup=cancel_keyboard()
    )


def _award_bonus_total_steps() -> int:
    return 1 + 1 + 1 + len(AWARD_CREATE_BONUS_STEPS) + 1


def _award_bonus_step_no(idx: int) -> str:
    return f"Шаг {2 + idx} из {_award_bonus_total_steps()}"


async def _award_ask_bonus(message, state, idx: int):
    """Спрашиваем idx-ый бонус (по порядку AWARD_CREATE_BONUS_STEPS)."""
    if idx >= len(AWARD_CREATE_BONUS_STEPS):
        # бонусы кончились — показываем превью
        data = await state.get_data()
        draft = {
            "name": data["name"], "description": data.get("desc"), "emoji": data["emoji"],
            "id": 0, "image": None,
            **{"bonus_attack": 0, "bonus_defense": 0, "bonus_dodge": 0, "bonus_fishing": 0,
               "bonus_hp": 0, "bonus_crit": 0, "bonus_shop_discount": 0,
               "bonus_report_tax": 0,
               "reward_nm": 0, "monthly_nm": 0},
            **data.get("bonuses", {}),
        }
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Создать награду", callback_data="aw_confirm")],
            [InlineKeyboardButton(text="↩️ Заново", callback_data="aw:create")],
            [InlineKeyboardButton(text="🔙 Отмена", callback_data="admin:awards")],
        ])
        await state.set_state(AdminAwards.preview)
        await message.answer(
            "🏅 Превью награды — проверь и подтверди:\n\n" +
            "\n".join(_award_summary_lines(draft)) +
            "\n\nЭмодзи: " + (draft["emoji"] or "🏅") + " · Название: " + draft["name"],
            reply_markup=kb
        )
        return
    field, label = AWARD_CREATE_BONUS_STEPS[idx]
    data = await state.get_data()
    current = data.get("bonuses", {}).get(field, 0)
    await state.update_data(create_bonus_idx=idx)
    await state.set_state(AdminAwards.bonus)
    await message.answer(
        f"{_award_bonus_step_no(idx)} — {label}\n"
        f"Введи целое число (текущее: {current}). 0 или «-» — пропустить.",
        reply_markup=cancel_keyboard()
    )


@router.message(AdminAwards.name)
async def award_create_name(message: Message, state: FSMContext):
    title = message.text.strip()
    if not title:
        await message.answer("Название не может быть пустым.")
        return
    await state.update_data(name=title)
    await state.set_state(AdminAwards.desc)
    await message.answer(
        f"{_award_bonus_step_no(-1)} — Описание награды (или «-» если нет):",
        reply_markup=cancel_keyboard()
    )


@router.message(AdminAwards.desc)
async def award_create_desc(message: Message, state: FSMContext):
    text = message.text.strip()
    await state.update_data(desc=None if text == "-" else text)
    await state.set_state(AdminAwards.emoji)
    await message.answer(
        f"{_award_bonus_step_no(0)} — Эмодзи награды (один символ, например 🏅, ⭐, 🎖️). Или «-» для 🏅:",
        reply_markup=cancel_keyboard()
    )


@router.message(AdminAwards.emoji)
async def award_create_emoji(message: Message, state: FSMContext):
    text = message.text.strip()
    emoji = text if text and text != "-" else "🏅"
    await state.update_data(emoji=emoji[:1])
    await _award_ask_bonus(message, state, 0)


@router.message(AdminAwards.bonus)
async def award_create_bonus(message: Message, state: FSMContext):
    text = message.text.strip()
    if text != "-":
        try:
            value = max(0, int(float(text)))
        except ValueError:
            await message.answer("Введи целое число или «-» чтобы пропустить.",
                                 reply_markup=cancel_keyboard())
            return
    else:
        value = 0
    data = await state.get_data()
    idx = data.get("create_bonus_idx", 0)
    field = AWARD_CREATE_BONUS_STEPS[idx][0]
    bonuses = dict(data.get("bonuses", {}))
    bonuses[field] = value
    await state.update_data(bonuses=bonuses)
    await _award_ask_bonus(message, state, idx + 1)


@router.callback_query(F.data == "aw_confirm")
async def award_create_confirm(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_awards"):
        await callback.message.answer("❌ Нет прав.")
        return
    data = await state.get_data()
    await state.clear()
    name, desc = data.get("name"), data.get("desc")
    emoji = data.get("emoji") or "🏅"
    bonuses = data.get("bonuses", {})
    ok, res = await create_award(name, desc, emoji, callback.from_user.id, **bonuses)
    if ok:
        await log_action(callback.from_user.id, 'create_award', None,
                         f"award={name} id={res} bonuses={bonuses}")
        try:
            await callback.message.delete()
        except Exception:
            pass
        await callback.message.answer(f"✅ Награда «{emoji} {name}» создана с бонусами.")
    else:
        await callback.message.answer(f"❌ {res}")


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
    "bonus_crit": "💥 Крит, %",
    "bonus_shop_discount": "💰 Скидка в магазине, %",
    "bonus_report_tax": "🧾 Снижение налога с отчёта, п.п.",
    "reward_nm": "🎁 Разовая премия, НМ (из казны)",
    "monthly_nm": "📅 Ежемесячная премия, НМ (из казны)",
}

AWARD_EDIT_PROMPTS = {
    "description": "Введи новое описание награды (или «-» чтобы очистить):",
    "image": "Пришли фото награды (или «-» чтобы убрать картинку):",
    "bonus_attack": "Введи бонус атаки в % (целое число, например 5 или 0):",
    "bonus_defense": "Введи бонус защиты в % (целое число):",
    "bonus_dodge": "Введи бонус уклонения в % (целое число):",
    "bonus_fishing": "Введи бонус шанса рыбалки в % (целое число):",
    "bonus_hp": "Введи бонус HP сверх базовых 100 (целое число):",
    "bonus_crit": (
        "💥 Введи бонус к шансу КРИТИЧЕСКОГО УДАРА в % (целое число, 0 — без бонуса).\n"
        "Складывается с базовым шансом по званию и с бонусом от снаряжения.\n"
        f"Суммарный шанс ограничен {MAX_CRIT_CHANCE}% — выше делать бессмысленно.\n"
        "Множитель урона при крите у пилота ×1.4 и меняется только снаряжением:"),
    "bonus_shop_discount": (
        "Введи скидку в магазине в % (целое число, 0 — без скидки). "
        f"Действует на все товары, включая оружие и Спец-отдел. Потолок — {AWARD_MAX_SHOP_DISCOUNT}% "
        "даже если несколько наград складываются:"),
    "bonus_report_tax": (
        "Введи снижение налога с отчёта в процентных пунктах (целое число, 0 — без снижения).\n"
        "Например, при общей ставке 15% и снижении 5 будет 10%.\n"
        f"Ниже {AWARD_MIN_REPORT_TAX}% не опускается даже с несколькими наградами:"),
    "reward_nm": (
        "💵 Введи РАЗОВУЮ премию за награду в НМ (целое число, 0 — без премии).\n"
        "Выплачивается при выдаче награды и только ИЗ КАЗНЫ — если казны нет, "
        "сумма встанет в зарплатный долг игрока:"),
    "monthly_nm": (
        "📅 Введи ЕЖЕМЕСЯЧНУЮ премию в НМ (целое число, 0 — без премии).\n"
        "Выплачивается 1-го числа каждому владельцу награды, только из казны "
        "(нехватка — в долг):"),
}


def _award_bonus_summary(award) -> str:
    """Человеческое описание бонусов награды одной строкой — для списков и превью."""
    parts = []
    simple = [
        ("bonus_attack", "⚔️{v}%"), ("bonus_defense", "🛡{v}%"),
        ("bonus_dodge", "💨{v}%"), ("bonus_fishing", "🎣{v}%"),
        ("bonus_hp", "❤️+{v}"),
    ]
    for col, fmt in simple:
        v = award[col] or 0
        if v:
            parts.append(fmt.format(v=v))
    disc = award['bonus_shop_discount'] or 0
    if disc:
        parts.append(f"💰скидка {min(disc, AWARD_MAX_SHOP_DISCOUNT)}%" if disc <= AWARD_MAX_SHOP_DISCOUNT
                     else f"💰скидка {AWARD_MAX_SHOP_DISCOUNT}% (потолок)")
    tax = award['bonus_report_tax'] or 0
    if tax:
        parts.append(f"🧾налог −{tax} п.п.")
    if award.get('reward_nm') or 0:
        parts.append(f"💵+{award['reward_nm']} НМ")
    if award.get('monthly_nm') or 0:
        parts.append(f"📅+{award['monthly_nm']} НМ/мес из казны")
    return ", ".join(parts) if parts else "без бонусов"


AWARD_CREATE_BONUS_STEPS = [
    ("bonus_attack", "⚔️ Бонус атаки, %"),
    ("bonus_defense", "🛡️ Бонус защиты, %"),
    ("bonus_dodge", "💨 Бонус уклонения, %"),
    ("bonus_fishing", "🎣 Бонус рыбалки, %"),
    ("bonus_hp", "❤️ Бонус HP (сверх 100)"),
    ("bonus_crit", "💥 Бонус крита, % (шанс критического удара в бою)"),
    ("bonus_shop_discount", "💰 Скидка в магазине, % (потолок 40% с учётом всех наград)"),
    ("bonus_report_tax", "🧾 Снижение налога с отчёта, п.п. (например −5 → 10% при ставке 15%)"),
    ("reward_nm", "💵 Разовая премия, НМ (выплачивается из казны при выдаче)"),
    ("monthly_nm", "📅 Ежемесячная премия, НМ (выплачивается из казны 1-го числа)"),
]


def _award_summary_lines(award) -> list:
    """Бонусные строки для карточки: совпадают с полями редактирования."""
    return [
        "Бонусы (в %):",
        f"⚔️ Атака: {award.get('bonus_attack') or 0}",
        f"🛡️ Защита: {award.get('bonus_defense') or 0}",
        f"💨 Уклонение: {award.get('bonus_dodge') or 0}",
        f"🎣 Рыбалка: {award.get('bonus_fishing') or 0}",
        f"❤️ HP: {award.get('bonus_hp') or 0}",
        f"💥 Крит: {award.get('bonus_crit') or 0}",
        f"💰 Скидка в магазине: {award.get('bonus_shop_discount') or 0}%",
        f"🧾 Снижение налога с отчёта: −{award.get('bonus_report_tax') or 0} п.п.",
        "Деньги (из казны):",
        f"💵 Разовая премия: {award.get('reward_nm') or 0} НМ",
        f"📅 Ежемесячная премия: {award.get('monthly_nm') or 0} НМ",
    ]


def _award_edit_card(award) -> str:
    if not award:
        return "❌ Награда не найдена."
    emoji = award['emoji'] or '🏅'
    lines = [
        f"{emoji} {award['name']} (id {award['id']})\n",
        f"📝 {award['description'] or '—'}",
        f"🖼 Картинка: {'есть' if award['image'] else 'нет'}",
        "",
    ] + _award_summary_lines(award)
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
    award = await get_award(int(award_id))
    prompt = AWARD_EDIT_PROMPTS[field]
    if award:
        cur = award.get(field)
        if field == "description":
            cur_text = (cur or "—")
        elif field == "image":
            cur_text = f"{'есть картинка' if cur else 'нет картинки'}"
        else:
            cur_text = ("—" if cur is None else str(cur))
        prompt = (f"{AWARD_EDIT_FIELDS[field]} награды «{award['name']}».\n"
                  f"Сейчас: {cur_text}.\n\n{prompt}")
    if field == "image" and award and award.get('image'):
        try:
            await callback.message.answer_photo(
                award['image'], caption=prompt, reply_markup=cancel_keyboard())
            return
        except Exception:
            pass
    await callback.message.answer(prompt, reply_markup=cancel_keyboard())


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
            if field in ("reward_nm", "monthly_nm"):
                value = max(0, min(1000000, parsed))
            else:
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
        target = await get_user(target_id)
        await notify_award(message.bot, target, f"{a['emoji'] or '🏅'} {a['name']}", target_id)


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
        target = await get_user(target_id)
        await notify_award(callback.message.bot, target,
                           f"{a['emoji'] or '🏅'} {a['name']}", target_id)


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
    await show_reports_menu(callback.message)


@router.callback_query(F.data == "admin:reports_pending")
async def admin_reports_pending(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_view_reports"):
        await callback.message.answer("❌ Нет прав для просмотра отчётов.")
        return
    await show_pending_reports(callback.message)


async def show_reports_menu(message):
    """Вкладка «Отчёты»: пункты «на проверку» и «принятые»."""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    pending = await get_pending_reports()
    approved_total = await count_approved_reports()
    unpaid = await count_approved_reports(unpaid_only=True)
    text = (
        "📋 ОТЧЁТЫ\n\n"
        f"• 🕵️ На проверке: {len(pending)}\n"
        f"• ✅ Принятые: {approved_total} (не оплачено: {unpaid})\n\n"
        "Выбери пункт:"
    )
    buttons = [
        [InlineKeyboardButton(
            text=f"🕵️ Отчёты на проверку · {len(pending)}",
            callback_data="admin:reports_pending")],
        [InlineKeyboardButton(
            text=f"✅ Принятые отчёты · {approved_total}",
            callback_data="admin:reports_done")],
    ]
    if 'super_admin' in await get_user_role(message.chat.id):
        buttons.append([
            InlineKeyboardButton(text="⚙️ Порог автопроверки",
                                 callback_data="rep:auto_approve_edit"),
            InlineKeyboardButton(text="🚦 Потолок за сутки",
                                 callback_data="rep:pay_cap_edit"),
        ])
    buttons.append([InlineKeyboardButton(text="🔙 В меню", callback_data="back:main")])
    await message.answer(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )


@router.callback_query(F.data == "admin:reports_done")
async def admin_reports_done(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_view_reports"):
        await callback.message.answer("❌ Нет прав для просмотра отчётов.")
        return
    await show_approved_reports(callback.message)


async def show_approved_reports(message):
    """Список принятых отчётов с меткой «оплачен / не оплачен»."""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    reports = await get_approved_reports(20)
    pending = await get_pending_reports()
    unpaid = await count_approved_reports(unpaid_only=True)
    text = "✅ ПРИНЯТЫЕ ОТЧЁТЫ\n"
    if not reports:
        text += "\nПока нет ни одного принятого отчёта."
    else:
        text += (
            f"\nПоследние {len(reports)} (из них ещё не оплачено: {unpaid}).\n"
            f"Отчёты за текущие сутки оплачиваются в 10:00 МСК; отчёт за прошлые "
            f"сутки, одобренный после его 10:00, — сразу при одобрении.\n\n"
        )
        for r in reports:
            credited = r['credited_troops'] if r['credited_troops'] is not None else r['troops_reported']
            paid = "✅ оплачен" if r['paid'] else "⏳ не оплачен"
            when = (r['created_at'] or '')[:16]
            text += (
                f"#{r['id']} · {r['first_name']} (@{r['username']}) · "
                f"{credited} ⚔️ · {paid} · {when}\n"
            )
    buttons = [
        [InlineKeyboardButton(
            text=f"🕵️ Отчёты на проверку · {len(pending)}",
            callback_data="admin:reports_pending")],
        [InlineKeyboardButton(text="🔙 К списку отчётов", callback_data="admin:reports")],
    ]
    await message.answer(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )


@router.callback_query(F.data == "rep:auto_approve_edit")
async def report_auto_approve_edit_cb(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if 'super_admin' not in await get_user_role(callback.from_user.id):
        await callback.message.answer("❌ Только супер-админ может менять порог автопроверки.")
        return
    current = await get_report_auto_approve_troops()
    await state.set_state(AdminReportAutoApprove.value)
    await callback.message.edit_text(
        f"⚙️ ПОРОГ АВТОПРОВЕРКИ ОТЧЁТОВ\n\n"
        f"Сейчас: отчёты до <b>{current}</b> войск за сутки принимаются автоматически.\n"
        f"Отчёты с бо́льшим числом уходят на проверку.\n\n"
        f"Введи новое значение (целое число от 0 до 1 000 000):",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 К отчётам", callback_data="admin:reports")]
        ])
    )


@router.message(AdminReportAutoApprove.value)
async def report_auto_approve_edit_value(message: Message, state: FSMContext):
    try:
        value = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Введи целое число от 0 до 1 000 000:")
        return
    if not 0 <= value <= 1000000:
        await message.answer("❌ Значение должно быть от 0 до 1 000 000:")
        return
    await set_report_auto_approve_troops(value)
    await log_action(message.from_user.id, 'set_report_auto_approve', None, f"value={value}")
    await state.clear()
    await message.answer(
        f"✅ Порог автопроверки установлен: {value} войск за сутки.\n"
        f"Отчёты до {value} теперь принимаются автоматически."
    )
    await show_pending_reports(message)


@router.callback_query(F.data == "rep:pay_cap_edit")
async def report_pay_cap_edit_cb(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if 'super_admin' not in await get_user_role(callback.from_user.id):
        await callback.message.answer("❌ Только супер-админ меняет суточный лимит оплаты.")
        return
    current = await get_report_daily_pay_cap()
    await state.set_state(AdminReportPayCap.value)
    await callback.message.edit_text(
        f"🚦 СУТОЧНЫЙ ЛИМИТ ОПЛАТЫ ОТЧЁТОВ\n\n"
        f"Сейчас: за одни сутки начисляется не больше <b>{current if current else '— (без ограничения)'}</b> "
        f"войск суммарно по всем отчётам пилота.\n"
        f"Лимит режет «всё накопленное», вписанное в «за сутки».\n"
        f"Значение «всего» лимитом не ограничивается.\n\n"
        f"Введи новое значение (0 — без ограничения, до 10 000 000):",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 К отчётам", callback_data="admin:reports")]
        ])
    )


@router.message(AdminReportPayCap.value)
async def report_pay_cap_edit_value(message: Message, state: FSMContext):
    raw = message.text.strip().replace(" ", "").replace("\u00a0", "")
    if not raw.isdigit():
        await message.answer("❌ Введи целое число (0 — без ограничения):")
        return
    value = int(raw)
    if value > 10000000:
        await message.answer("❌ Значение должно быть от 0 до 10 000 000:")
        return
    await set_report_daily_pay_cap(value)
    await log_action(message.from_user.id, 'set_report_pay_cap', None, f"value={value}")
    await state.clear()
    await message.answer(
        f"✅ Суточный лимит оплаты: {value if value else 'без ограничения'}.\n"
        f"За сутки начисляется не больше {value} войск — лимит режет один снимок "
        f"(последний отчёт суток), а не сумму отчётов."
    )
    await show_pending_reports(message)


async def _report_payout_block(report) -> str:
    """Блок оплаты для карточки отчёта.

    Платится «за сутки» из ПОСЛЕДНЕГО отчёта этих суток (см. report_payout_context),
    поэтому для непоследнего отчёта блок прямо говорит, что он перекрыт свежим
    снимком и денег не приносит. «Всего» и регион — справочные данные для
    статистики, на оплату не влияют.

    Сутки берём по САМОМУ отчёту (его created_at), а не по текущим: отчёт, сданный
    до 10:00 МСК, относится к ПРЕДЫДУЩИМ суткам, и надпись про текущие сутки сбивала
    с толку при проверке."""
    from database.db import report_payout_context, _report_cycle_day_of
    total_claim = report['total_troops'] if 'total_troops' in report.keys() else 0
    ctx = await report_payout_context(
        report['user_id'], report['troops_reported'], total_claim, exclude_id=report['id'],
        cycle_day=_report_cycle_day_of(report.get('created_at')))
    lines = [
        f"⚔️ Заявка за сутки: {ctx['claim']}",
        f"💰 К выдаче: {ctx['payable']}",
        f"🗓 Сутки отчёта: {ctx['day_label']}",
    ]
    if ctx.get("superseded"):
        lines.append(
            "🚫 Не последний отчёт этих суток — оплату даёт более свежий снимок. "
            "Одобрить можно (останется в статистике), но платить здесь нечего.")
    if total_claim:
        lines.append(f"🗺 В регионе накоплено (статистика): {total_claim}")
    if ctx.get("capped_by_limit"):
        lines.append(f"🚦 Обрезано суточным лимитом ({ctx['cap']})")
    if ctx["assigned_today"]:
        lines.append(f"📋 Сумма заявок за эти сутки (справочно): {ctx['assigned_today']}")
    if ctx.get("already_paid"):
        lines.append(f"✅ Уже выплачено за эти сутки: {ctx['already_paid']}")
    return "\n".join(lines)


async def show_pending_reports(message, start: int = 0):
    """Карточка отчёта на проверке.

    start — позиция в очереди (0-based). Раньше кнопка «Следующий» просто
    перерисовывала ту же карточку первого отчёта, поэтому листать очередь было
    нельзя. Теперь позиция едет в callback_data («rep:nav:<N>»), а счётчик
    «📌 2 из 5» виден в тексте карточки."""
    reports = await get_pending_reports()
    if not reports:
        text = "✅ В очереди нет отчётов на проверку."
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        _back = [InlineKeyboardButton(text="📋 К списку отчётов", callback_data="admin:reports")]
        if 'super_admin' in await get_user_role(message.chat.id):
            limit = await get_report_auto_approve_troops()
            cap = await get_report_daily_pay_cap()
            text += (f"\n\n⚙️ Порог автопроверки: отчёты до {limit} войск за сутки — автоматически."
                     f"\n🚦 Суточный лимит оплаты: {cap if cap else 'нет'} (0 = без ограничения).")
            await message.answer(
                text,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(text="⚙️ Изменить порог",
                                             callback_data="rep:auto_approve_edit"),
                        InlineKeyboardButton(text="🚦 Потолок за сутки",
                                             callback_data="rep:pay_cap_edit"),
                    ],
                    _back,
                ])
            )
        else:
            await message.answer(
                text,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[_back])
            )
        return

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    idx = start % len(reports) if reports else 0
    report = reports[idx]
    buttons = []
    if await has_permission(message.chat.id, "can_approve_reports"):
        buttons.append([
            InlineKeyboardButton(text="✅ Принять", callback_data=f"rep_ok:{report['id']}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"rep_no:{report['id']}"),
        ])
    if len(reports) > 1:
        buttons.append([
            InlineKeyboardButton(text="◀️ Назад", callback_data=f"rep:nav:{(idx - 1) % len(reports)}"),
            InlineKeyboardButton(text="Следующий ▶️", callback_data=f"rep:nav:{(idx + 1) % len(reports)}"),
        ])
    buttons.append([InlineKeyboardButton(text="📋 К списку отчётов", callback_data="admin:reports")])
    # Супер-админ: исправить цифры отчёта (пилоты путают «за сутки» и «всего»).
    is_super = 'super_admin' in await get_user_role(message.chat.id)
    if is_super and await has_permission(message.chat.id, "can_approve_reports"):
        buttons.append([InlineKeyboardButton(
            text="✏️ Поправить цифры и принять",
            callback_data=f"rep_fix:{report['id']}")])
    # Супер-админ: порог автопроверки и суточный лимит оплаты отчётов.
    if is_super:
        limit = await get_report_auto_approve_troops()
        cap = await get_report_daily_pay_cap()
        buttons.append([
            InlineKeyboardButton(text=f"⚙️ Порог автопроверки: {limit}",
                                 callback_data="rep:auto_approve_edit"),
            InlineKeyboardButton(text=f"🚦 Потолок за сутки: {cap if cap else 'нет'}",
                                 callback_data="rep:pay_cap_edit"),
        ])

    pilot_line = f"Пилот: {report['first_name']} (@{report['username']})"
    callsign = report.get('callsign') if isinstance(report, dict) else None
    if not callsign and hasattr(report, 'keys'):
        callsign = report['callsign'] if 'callsign' in report.keys() else None
    if callsign:
        pilot_line += f" · Позывной: {callsign}"
    caption = (
        f"📋 ОТЧЁТ #{report['id']}"
        + (f"  ·  📌 {idx + 1} из {len(reports)} в очереди\n" if len(reports) > 1 else "\n")
        + f"\n"
        + pilot_line + "\n"
        + f"Войск за сутки (заявка): {report['troops_reported']}\n"
        + f"Всего войск (на счётчике пилота): {report['total_troops'] if 'total_troops' in report.keys() else '—'}\n"
        + f"{await _report_payout_block(report)}\n"
        + f"Регион: {report['region'] or '—'} (для статистики сил)\n"
        + f"Сдано: {created_at_msk(report['created_at']) if report['created_at'] else '—'} МСК\n\n"
        + f"Проверьте скриншот и примите решение:"
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


_KEEP_VALUES = ("-", "—", "без", "безизменений", "оставить", "безизменений")


def _report_fix_parse(text: str):
    """Разбор числа от супер-админа. None — «оставить как есть»."""
    t = text.strip().replace(" ", "").replace("\u00a0", "").lower()
    if t in _KEEP_VALUES:
        return None
    if t.isdigit():
        return int(t)
    return False  # мусор


@router.callback_query(F.data.startswith("rep_fix:"))
async def report_fix_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if 'super_admin' not in await get_user_role(callback.from_user.id):
        await callback.message.answer("❌ Править цифры отчёта может только супер-админ.")
        return
    if not await has_permission(callback.from_user.id, "can_approve_reports"):
        await callback.message.answer("❌ Нет прав на рассмотрение отчётов.")
        return
    report_id = int(callback.data.split(":")[1])
    report = await get_report_safe(report_id)
    if not report or report.get('user_id') == 0:
        await callback.message.answer("❌ Отчёт не найден в очереди.")
        return
    old_total = report['total_troops'] if 'total_troops' in report.keys() else None
    await state.update_data(fix_report_id=report_id, fix_old_daily=report['troops_reported'],
                            fix_old_total=old_total)
    await state.set_state(AdminReportFix.daily)
    await callback.message.answer(
        f"✏️ ПРАВКА ОТЧЁТА #{report_id}\n\n"
        f"Сейчас указано:\n"
        f"• за сутки: <b>{report['troops_reported']}</b>\n"
        f"• всего: <b>{old_total if old_total is not None else '—'}</b>\n\n"
        f"Введи ПРАВИЛЬНОЕ число войск за сегодняшние сутки — только то, что набежало "
        f"сегодня. Оставить как есть — отправь <code>-</code>:",
        reply_markup=cancel_keyboard()
    )


@router.message(AdminReportFix.daily)
async def report_fix_daily(message: Message, state: FSMContext):
    data = await state.get_data()
    report_id = data.get('fix_report_id')
    if not report_id:
        await state.clear()
        await message.answer("❌ Сессия правки сброшена, начни заново.")
        return
    daily = _report_fix_parse(message.text)
    if daily is False:
        await message.answer("❌ Введи целое число (или «-», чтобы оставить как есть):")
        return
    if daily is None:
        daily = data.get('fix_old_daily') or 0
    await state.update_data(fix_daily=daily)
    await state.set_state(AdminReportFix.total)
    old_total = data.get('fix_old_total')
    await message.answer(
        f"Принято: за сутки <b>{daily}</b>.\n\n"
        f"Теперь введи ПРАВИЛЬНОЕ значение «всего» — сколько очков у пилота набежало "
        f"ВСЕГО на данный момент. На выплату это число не влияет: оно идёт в "
        f"статистику сил по региону.\n"
        f"Сейчас указано: {old_total if old_total is not None else '—'}\n"
        f"Оставить как есть — отправь <code>-</code>:",
        reply_markup=cancel_keyboard()
    )


@router.message(AdminReportFix.total)
async def report_fix_total(message: Message, state: FSMContext):
    data = await state.get_data()
    report_id = data.get('fix_report_id')
    daily = data.get('fix_daily')
    if not report_id or daily is None:
        await state.clear()
        await message.answer("❌ Сессия правки сброшена, начни заново.")
        return
    total = _report_fix_parse(message.text)
    if total is False:
        await message.answer("❌ Введи целое число (или «-», чтобы оставить как есть):")
        return
    if total is None:
        total = data.get('fix_old_total')
    if total is None:
        await message.answer("❌ Введи значение «всего» числом:")
        return

    ctx = await correct_report_numbers(report_id, daily, total, message.from_user.id)
    if ctx.get('error'):
        await state.clear()
        await message.answer(f"❌ {ctx['error']}")
        await show_pending_reports(message)
        return

    old_daily = data.get('fix_old_daily')
    old_total = data.get('fix_old_total')
    await log_action(
        message.from_user.id, 'correct_report', None,
        f"report={report_id} было: сутки {old_daily}, всего {old_total} | "
        f"стало: сутки {daily}, всего {total} | к выдаче {ctx['payable']}")

    payout = (f"⚔️ Заявка за сутки: {ctx['claim']}\n"
              f"💰 К выдаче: <b>{ctx['payable']}</b>\n"
              f"🗓 Сутки: {ctx['day_label']}")
    note = ""
    if ctx.get("superseded"):
        note = ("\n\n🚫 Не последний отчёт этих суток: оплату даёт более свежий "
                "снимок, поэтому к выдаче 0. Цифры исправлены в статистике.")
    elif ctx["capped_by_limit"]:
        note = f"\n\n🚦 Обрезано суточным лимитом ({ctx['cap']} войск)"

    await state.clear()
    back_pos = await _queue_index_of(report_id)
    await message.answer(
        f"✏️ Цифры отчёта #{report_id} исправлены\n\n"
        f"было: за сутки {old_daily}, всего {old_total}\n"
        f"стало: за сутки <b>{daily}</b>, всего <b>{total}</b>\n\n"
        f"{payout}{note}\n\nОтчёт пока не одобрен — подтверди решение:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Принять", callback_data=f"rep_ok:{report_id}"),
                InlineKeyboardButton(text="❌ Отклонить", callback_data=f"rep_no:{report_id}"),
            ],
            [InlineKeyboardButton(text="🔙 К отчётам", callback_data=f"rep:nav:{back_pos}")],
        ])
    )


@router.callback_query(F.data.startswith("rep_ok:"))
async def report_approve(callback: CallbackQuery, bot: Bot):
    await callback.answer()
    report_id = int(callback.data.split(":")[1])
    if not await has_permission(callback.from_user.id, "can_approve_reports"):
        await callback.message.answer("❌ Нет прав.")
        return
    report = await get_report_safe(report_id)
    queue_pos = await _queue_index_of(report_id)
    # Сумма пересчитывается в approve_report по текущему остатку суточного лимита
    # (отчёт мог провисеть, пока пилот сдавал другие за эти же сутки).
    pilot = await get_user(report['user_id'])
    amount = await approve_report(report_id, callback.from_user.id)
    await log_action(callback.from_user.id, 'approve_report', report['user_id'], f"report={report_id}")

    # Мгновенная оплата: отчёт был за прошлые сутки, его 10:00 уже прошло → деньги
    # ушли сразу при одобрении (видно по paid=1 уже после approve_report).
    report_after = await get_report_safe(report_id)
    # Сутки САМОГО отчёта: у отчёта, сданного до 10:00, они прошлые, даже если
    # админ смотрит очередь уже после утреннего цикла.
    own_day = report_day_value_of(report.get('created_at'))
    own_label = report_day_label_for(own_day) if own_day else "—"
    if amount > 0 and report_after.get('paid'):
        tax_percent = await report_tax_percent_for(pilot['user_id'])
        tax = int(amount * tax_percent / 100)
        u = await get_user(pilot['user_id'])
        try:
            await bot.send_message(
                pilot['user_id'],
                "💰 ОПЛАТА ЗА ОТЧЁТЫ\n\n"
                f"Отчёт #{report_id} (за прошлые сутки) одобрен после утреннего цикла и оплачен сразу.\n"
                f"🗓 Сутки отчёта: {own_label}\n"
                f"⚔️ Войска: +{amount}\n✨ Опыт (накопительный): +{amount} "
                f"(всего {u['xp_balance']}, без налога)\n"
                f"💰 Нордмарки: +{amount - tax} (налог {tax} НМ в казну)\n"
                f"──────────────\nИтого у тебя: {u['troops']} войск, {u['nordmarks']} нордмарок"
            )
        except Exception:
            pass
        await callback.message.answer(
            f"✅ Отчёт #{report_id} принят и оплачен сразу (отчёт за прошлые сутки).\n"
            f"🗓 Сутки отчёта: {own_label}\n"
            f"⚔️ Начислено: {amount} войск — пилот уведомлён в личке."
        )
    else:
        _zero_note = ""
        if amount <= 0:
            _zero_note = ("\nℹ️ К выдаче 0: этот отчёт перекрыт более свежим снимком "
                          "за эти же сутки — оплату получит последний отчёт.")
        await callback.message.answer(
            f"✅ Отчёт #{report_id} принят.\n"
            f"🗓 Сутки отчёта: {own_label}\n"
            f"⚔️ К начислению: {amount} войск и столько же опыта "
            f"(выплата в 10:00 МСК — в начале новых суток)."
            + _zero_note
        )
    await show_pending_reports(callback.message, start=queue_pos)

    # В общий чат — только похвала по накопленной сумме за сутки, без точных цифр.
    # День фиксируем по САМОМУ отчёту: его одобряют часто на следующих сутках
    # (пилоты сдают ночью), иначе «сегодняшняя» сумма была бы пустой, и похвала
    # за честно нафармленный день терялась бы.
    if pilot:
        from utils.notify import notify_report_praise
        await notify_report_praise(
            bot, pilot, pilot['user_id'],
            day=report_day_value_of(report.get('created_at')))


@router.callback_query(F.data.startswith("rep_no:"))
async def report_reject(callback: CallbackQuery):
    await callback.answer()
    report_id = int(callback.data.split(":")[1])
    if not await has_permission(callback.from_user.id, "can_approve_reports"):
        await callback.message.answer("❌ Нет прав.")
        return
    report = await get_report_safe(report_id)
    queue_pos = await _queue_index_of(report_id)
    await reject_report(report_id, callback.from_user.id)
    await log_action(callback.from_user.id, 'reject_report', report['user_id'], f"report={report_id}")
    await callback.message.answer("❌ Отчёт отклонён.")
    await show_pending_reports(callback.message, start=queue_pos)


@router.callback_query(F.data.startswith("rep:nav:"))
async def report_nav(callback: CallbackQuery):
    """Листание очереди: «◀️ Назад» / «Следующий ▶️» с позицией в callback_data."""
    await callback.answer()
    try:
        start = int(callback.data.split(":")[2])
    except (ValueError, IndexError):
        start = 0
    await show_pending_reports(callback.message, start=start)


@router.callback_query(F.data == "rep:next")
async def report_next(callback: CallbackQuery):
    await callback.answer()
    await show_pending_reports(callback.message)


async def _queue_index_of(report_id: int) -> int:
    """Позиция отчёта в очереди на проверке (0-based); 0, если не найден.

    После «Принять»/«Отклонить» отчёт уходит из очереди, и на его месте
    оказывается следующий — поэтому показываем отчёт по той же позиции."""
    for i, r in enumerate(await get_pending_reports()):
        if r['id'] == report_id:
            return i
    return 0


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
        text += ("🪖 Силы — сумма показаний «всего» пилотов региона из их последних отчётов.\n"
                 "👤 Пилотов — кто сейчас в регионе. Переезд меняет оба показателя.\n\n")
        for s in stats:
            region_label = f"Регион {s['region']}"
            if s['region'] == "0":
                region_label += " (Столица)"
            text += (f"🌍 {region_label}\n"
                     f"   🪖 Силы: {s['troops_24h']}\n"
                     f"   👤 Пилотов: {s['active_pilots_72h']}\n\n")
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
        "Игроки, чьи войска достаточны для админского звания\n"
        "(выше «Старшего Лейтенанта»). Звание выбирает админ:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )


@router.callback_query(F.data.startswith("rank_promote:"))
async def rank_promote(callback: CallbackQuery):
    """Показать админу список админских званий для свободного выбора."""
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_grant_troops"):
        await callback.message.answer("❌ Нет прав.")
        return

    user_id = int(callback.data.split(":")[1])
    await show_rank_picker(callback, user_id)


async def show_rank_picker(callback: CallbackQuery, user_id: int):
    from config import RANKS, AUTO_RANK_NAMES
    user = await get_user(user_id)
    if not user:
        await callback.message.answer("❌ Игрок не найден.")
        return

    troops = user['troops']
    name = user['first_name'] or user['username'] or str(user_id)
    buttons = []
    for idx, (rank_name, required) in enumerate(RANKS):
        if rank_name in AUTO_RANK_NAMES:
            continue
        mark = "✅" if troops >= required else "➖"
        buttons.append([
            InlineKeyboardButton(
                text=f"{mark} {rank_name} ({required} войск)",
                callback_data=f"rank_pick:{user_id}:{idx}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="admin:ranks")])

    await callback.message.edit_text(
        f"⭐ Повышение: {name} ({troops} войск)\n\n"
        "Выбери звание. ✅ — доступно по войскам, ➖ — свободным решением админа:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )


@router.callback_query(F.data.startswith("rank_pick:"))
async def rank_pick(callback: CallbackQuery, bot: Bot):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_grant_troops"):
        await callback.message.answer("❌ Нет прав.")
        return

    parts = callback.data.split(":")
    user_id = int(parts[1])
    idx = int(parts[2])
    from config import RANKS, AUTO_RANK_NAMES
    if idx < 0 or idx >= len(RANKS) or RANKS[idx][0] in AUTO_RANK_NAMES:
        await callback.message.answer("❌ Неверное звание.")
        return
    rank_name, required = RANKS[idx]

    user = await get_user(user_id)
    if not user:
        await callback.message.answer("❌ Игрок не найден.")
        return

    await promote_user_rank(user_id, rank_name, callback.from_user.id)
    name = user['first_name'] or user['username'] or str(user_id)
    await callback.message.answer(
        f"✅ {name} повышен до звания «{rank_name}» "
        f"({user['troops']} войск, порог {required})."
    )
    await notify(bot, f"⭐ Пилот {await player_display(user)} получил звание «{rank_name}»!", user['user_id'])
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


# ============ ПОПУЛЯРНОСТЬ ЛОКАЦИЙ ============

LOC_STAT_PERIODS = {"1": "Сегодня", "7": "7 дней", "30": "30 дней", "all": "Всё время"}


def _loc_stat_markup(current: str = "7"):
    rows = []
    for key, label in LOC_STAT_PERIODS.items():
        mark = "•" if key == current else ""
        rows.append([InlineKeyboardButton(text=f"{mark}{label}", callback_data=f"locstat:{key}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


@router.callback_query(F.data.startswith("locstat:"))
async def admin_loc_stats(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_view_logs"):
        await callback.message.answer("❌ Нет прав для просмотра статистики.")
        return
    days = callback.data.split(":", 1)[1]
    if days not in LOC_STAT_PERIODS:
        days = "7"
    days_int = None if days == "all" else int(days)

    totals = await get_location_visit_totals(days_int)
    rows = await get_location_visit_stats(days_int)
    label = LOC_STAT_PERIODS[days]
    total = totals['visits'] if totals else 0

    if not total:
        text = (f"📈 ПОПУЛЯРНОСТЬ ЛОКАЦИЙ — {label}\n\n"
                "Данных пока нет. Сбор начинается сразу после включения логирования "
                "переходов: каждый успешный вход в здание/аспект пишется в БД.")
    else:
        lines = []
        for i, r in enumerate(rows, 1):
            share = r['visits'] * 100 / total
            lines.append(f"{i}. {r['name']} — {r['visits']} входов ({share:.0f}%), "
                         f"игроков {r['players']}")
        text = (f"📈 ПОПУЛЯРНОСТЬ ЛОКАЦИЙ — {label}\n\n"
                f"Всего входов: {total}, разных игроков: {totals['players']}\n\n"
                + "\n".join(lines))
    await callback.message.answer(text, reply_markup=_loc_stat_markup(days))


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
    dng = await get_dungeon(data.get('target_id')) if data.get('target_id') else None
    has_photo = bool(dng and dng.get(f"photo_{tod}"))
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="dungeon:photos")]
    ])
    if has_photo:
        try:
            await callback.message.answer_photo(
                dng[f"photo_{tod}"],
                caption=(f"🖼 Сейчас на «{DUNGEON_PHOTO_LABEL[tod]}» есть картинка.\n"
                         f"Отправь новую фото (или «-» для очистки этого слота):"),
                reply_markup=kb)
            return
        except Exception:
            pass
    await callback.message.answer(
        f"🖼 «{DUNGEON_PHOTO_LABEL[tod]}» подземелья «{dng['name'] if dng else ''}» "
        f"(сейчас: {'есть картинка' if has_photo else 'нет'}).\n"
        f"Отправь фото (или «-» для очистки этого слота):",
        reply_markup=kb
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
    enemy = await get_enemy(data.get('enemy_id'))
    prompt = ENEMY_INPUT_PROMPTS[field]
    if enemy:
        cur = enemy.get(field)
        if field == "image":
            cur_text = f"{'есть картинка' if cur else 'нет картинки'}"
        elif field == "description":
            cur_text = (cur or "—")
        elif field == "drops":
            cur_text = (f"{len(cur or [])} записей" if cur else "—")
        else:
            cur_text = ("—" if cur is None else str(cur))
        prompt = (f"{ENEMY_FIELD_LABELS[field]} врага «{enemy['name']}».\n"
                  f"Сейчас: {cur_text}.\n\n{prompt}")
    if field == "image" and enemy and enemy.get('image'):
        try:
            await callback.message.answer_photo(
                enemy['image'], caption=prompt, reply_markup=cancel_keyboard())
            return
        except Exception:
            pass
    await callback.message.answer(prompt, reply_markup=cancel_keyboard())


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
    enemy = await get_enemy(enemy_id)
    drops, _, item = await _drop_item_for(enemy_id, idx)
    ch = drops[idx].get('chance', 0) if drops and 0 <= idx < len(drops) else 0
    cur_chance = int(ch * 100) if ch <= 1 else int(ch)
    item_name = f"«{item['name']}»" if item else "дроп"
    await callback.message.answer(
        f"🎲 Шанс дропа {item_name} у врага «{enemy['name'] if enemy else ''}».\n"
        f"Сейчас: {cur_chance}%.\n\nВведи новый шанс выпадения, % (1–100):",
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
    enemy = await get_enemy(enemy_id)
    drops, _, item = await _drop_item_for(enemy_id, idx)
    cur_qty = drops[idx].get('qty', 1) if drops and 0 <= idx < len(drops) else 1
    item_name = f"«{item['name']}»" if item else "дроп"
    await callback.message.answer(
        f"🔢 Кол-во дропа {item_name} у врага «{enemy['name'] if enemy else ''}».\n"
        f"Сейчас: {cur_qty}.\n\nВведи новое кол-во (целое число ≥ 1):",
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
    rows = await get_water_junk_rows(water)
    cur_row = next((r for r in rows if r['name'] == jname), None)
    cur_chance = (cur_row or {}).get('chance')
    cur_photo = (cur_row or {}).get('photo_file_id')
    if jfield == "chance":
        prompt = (f"🎲 Шанс находки «{jname}» ({WATER_LABELS[water]}).\n"
                  f"Сейчас: {cur_chance or 0}%.\n\n"
                  f"Введи новый шанс выпадения в % (целое число 0–100; "
                  f"0 = находка не выпадает).\nДефолт: водоросли 15%, сапог 2%.")
    else:
        prompt = (f"🖼 Фото находки «{jname}» ({WATER_LABELS[water]}); "
                  f"сейчас: {'есть' if cur_photo else 'нет'}.\n"
                  f"Отправь фото находки — или «-», чтобы убрать фотографию:")
        if cur_photo:
            try:
                await callback.message.answer_photo(
                    cur_photo, caption=prompt, reply_markup=cancel_keyboard())
                return
            except Exception:
                pass
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
    rows.append([InlineKeyboardButton(text="➕ Добавить из списка", callback_data=f"fishing:addlist:{water}")])
    rows.append([InlineKeyboardButton(text="✨ Создать новую рыбу", callback_data=f"fishing:new:{water}")])
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


@router.callback_query(F.data.startswith("fishing:new:"))
async def admin_fishing_new(callback: CallbackQuery, state: FSMContext):
    """Мастер создания новой рыбы прямо в водоёме: название → описание →
    цена продажи → вес дня → вес ночи → фото."""
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    water = callback.data.split(":", 2)[2]
    if water not in WATER_LABELS:
        return
    await state.clear()
    await state.update_data(water=water)
    await state.set_state(AdminFishing.c_name)
    await callback.message.answer(
        f"✨ Создание рыбы\n🐟 {WATER_LABELS[water]}\n\n"
        f"Шаг 1/6 — Название рыбы (например «Карась»):",
        reply_markup=cancel_keyboard()
    )


@router.message(AdminFishing.c_name)
async def admin_fishing_new_name(message: Message, state: FSMContext):
    name = (message.text or "").strip()
    if not name:
        await message.answer("❌ Введи название рыбы.", reply_markup=cancel_keyboard())
        return
    if len(name) > 60:
        await message.answer("❌ Слишком длинное название — максимум 60 символов.",
                             reply_markup=cancel_keyboard())
        return
    await state.update_data(c_name=name)
    await state.set_state(AdminFishing.c_desc)
    await message.answer("Шаг 2/6 — Описание рыбы (или «-» если нет):",
                         reply_markup=cancel_keyboard())


@router.message(AdminFishing.c_desc)
async def admin_fishing_new_desc(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    await state.update_data(c_desc=None if text in ("-", "—") else text[:300])
    await state.set_state(AdminFishing.c_sell_price)
    await message.answer("Шаг 3/6 — Цена продажи скупщику, Нордмарок (целое число ≥ 0):",
                         reply_markup=cancel_keyboard())


@router.message(AdminFishing.c_sell_price)
async def admin_fishing_new_sell_price(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    parsed = int(text) if text.isdigit() else None
    if parsed is None or parsed < 0:
        await message.answer("❌ Введи целое число ≥ 0.",
                             reply_markup=cancel_keyboard())
        return
    await state.update_data(c_sell_price=parsed)
    await state.set_state(AdminFishing.c_day_weight)
    await message.answer(
        "Шаг 4/6 — Относительный вес рыбы днём (целое число ≥ 0; 0 = не водится днём):",
        reply_markup=cancel_keyboard()
    )


@router.message(AdminFishing.c_day_weight)
async def admin_fishing_new_day_weight(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    parsed = int(text) if text.isdigit() else None
    if parsed is None or parsed < 0:
        await message.answer("❌ Введи целое число ≥ 0.",
                             reply_markup=cancel_keyboard())
        return
    await state.update_data(c_day_weight=parsed)
    await state.set_state(AdminFishing.c_night_weight)
    await message.answer(
        "Шаг 5/6 — Относительный вес рыбы ночью (целое число ≥ 0; 0 = не водится ночью):",
        reply_markup=cancel_keyboard()
    )


@router.message(AdminFishing.c_night_weight)
async def admin_fishing_new_night_weight(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    parsed = int(text) if text.isdigit() else None
    if parsed is None or parsed < 0:
        await message.answer("❌ Введи целое число ≥ 0.",
                             reply_markup=cancel_keyboard())
        return
    await state.update_data(c_night_weight=parsed)
    await state.set_state(AdminFishing.c_photo)
    await message.answer(
        "Шаг 6/6 — Пришли фото рыбы (Telegram-фото) или «-», если фото нет:",
        reply_markup=cancel_keyboard()
    )


@router.message(AdminFishing.c_photo)
async def admin_fishing_new_photo(message: Message, state: FSMContext):
    photo_file_id = None
    if message.photo:
        photo_file_id = message.photo[-1].file_id
    else:
        text = (message.text or "").strip()
        if text not in ("-", "—"):
            await message.answer("❌ Отправь именно фото (или «-» без фото).",
                                 reply_markup=cancel_keyboard())
            return
    data = await state.get_data()
    water = data.get('water')
    if water not in WATER_LABELS:
        await state.clear()
        await message.answer("❌ Водоём не распознан. Начни заново.")
        return
    day_w = int(data.get('c_day_weight', 1))
    night_w = int(data.get('c_night_weight', 1))
    sell_price = int(data.get('c_sell_price', 0))
    ok, res = await create_water_fish(
        water=water, name=data['c_name'], sell_price=sell_price,
        day_weight=day_w, night_weight=night_w,
        description=data.get('c_desc'),
        photo_file_id=photo_file_id,
        added_by=message.from_user.id,
    )
    if not ok:
        await message.answer(f"❌ {res}", reply_markup=cancel_keyboard())
        return
    wf_id = res['wf_id']
    await log_action(message.from_user.id, 'edit_fishing', None,
                     f"created water={water} item_id={res['item_id']} "
                     f"sell={sell_price} day={day_w} night={night_w} "
                     f"photo={'yes' if photo_file_id else 'no'}")
    await state.clear()
    await state.update_data(water=water, wf_id=wf_id)
    await _admin_fishing_card(
        message, wf_id,
        prefix=f"✅ Рыба «{data['c_name']}» создана в водоёме.\n\n")


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
    fish = await get_water_fish_row(data.get('wf_id')) if data.get('wf_id') else None
    prompt = FISHING_INPUT_PROMPTS[field]
    if fish:
        cur = fish.get({
            "day_weight": "day_weight",
            "night_weight": "night_weight",
            "sell_price": "sell_price",
            "photo": "photo_file_id",
        }.get(field, field))
        if field == "photo":
            cur_text = f"{'есть картинка' if cur else 'нет картинки'}"
        else:
            cur_text = ("—" if cur is None else str(cur))
        prompt = (f"{FISHING_FIELD_LABELS[field]} рыбы «{fish['name']}».\n"
                  f"Сейчас: {cur_text}.\n\n{prompt}")
    if field == "photo" and fish and fish.get('photo_file_id'):
        try:
            await callback.message.answer_photo(
                fish['photo_file_id'], caption=prompt, reply_markup=cancel_keyboard())
            return
        except Exception:
            pass
    await callback.message.answer(prompt, reply_markup=cancel_keyboard())


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


# ============ ГРИБЫ ЛЕСА (админ-редактор) ============

FOREST_FIELD_LABELS = {
    "chance": "🎲 Вес в пуле",
    "photo": "🖼 Фото гриба",
    "sell_price": "💰 Цена продажи (НМ)",
}

FOREST_INPUT_PROMPTS = {
    "chance": ("Введи вес гриба в пуле леса (целое число 0–100). Это не процент: "
               "все веса делят между собой 90% находки, 0 = гриб не выпадает:"),
    "photo": "Отправь фото гриба (Telegram-фото). Или отправь «-», чтобы убрать фото:",
    "sell_price": "Введи цену продажи гриба скупщику, Нордмарок (целое число ≥ 0):",
}


async def _admin_forest_card(source, f_id: int, prefix: str = ""):
    """Карточка гриба леса с кнопками правки."""
    shroom = await get_forest_mushroom_row(f_id)
    if not shroom:
        await source.answer("❌ Гриб не найден.")
        return
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    photo_state = "есть" if shroom.get('photo_file_id') else "нет"
    kind = shroom.get('kind') or 'edible'
    kind_label = "🍄 Съедобный" if kind == "edible" else "☠ Ядовитый"
    market_label = "✅ Можно" if shroom.get('market_ok') else "🔒 Только скупщику"
    heal_line = f"❤️ Лечение сырым: {shroom['heal']}" if shroom.get('heal') else "❤️ Сырым не лечит"
    text = (
        f"{prefix}🍄 {shroom['name']}\n"
        f"──────────────\n"
        f"{kind_label}\n"
        f"🎲 Вес в пуле: {shroom['chance']} (веса делят 90% находки)\n"
        f"🖼 Фото: {photo_state}\n"
        f"💰 Продажа: {shroom['sell_price']} НМ\n"
        f"🏪 Рынок: {market_label}\n"
        f"{heal_line}\n\n"
        f"⚠️ После правки стартовая синхронизация больше не перезапишет "
        f"настройки этого гриба.\nЧто изменить?"
    )
    rows = [
        [InlineKeyboardButton(
            text=f"🧬 Тип: {'Съедобный' if kind == 'edible' else 'Ядовитый'} →",
            callback_data=f"forest:kind:{f_id}"),
         InlineKeyboardButton(
            text=f"🏪 Рынок: {'✅' if shroom.get('market_ok') else '🔒'} →",
            callback_data=f"forest:market:{f_id}")],
        [InlineKeyboardButton(text="🎲 Шанс выпадения", callback_data="forest_field:chance")],
        [InlineKeyboardButton(text="🖼 Фото гриба", callback_data="forest_field:photo")],
        [InlineKeyboardButton(text="💰 Цена продажи", callback_data="forest_field:sell_price")],
        [InlineKeyboardButton(text="🗑 Убрать из леса", callback_data=f"forest:del:{f_id}")],
        [InlineKeyboardButton(text="🔙 К списку грибов", callback_data="admin:forest")],
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    if hasattr(source, 'message') and source.message is not None:
        await source.message.edit_text(text, reply_markup=markup)
    else:
        await source.answer(text, reply_markup=markup)


@router.callback_query(F.data == "admin:forest")
async def admin_forest_menu(callback: CallbackQuery, state: FSMContext):
    """Меню редактора леса: выбор зоны (опушка / лесная поляна)."""
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    await state.clear()
    text, markup = await _admin_forest_zones_view(callback.message)
    await callback.message.edit_text(text, reply_markup=markup)

@router.callback_query(F.data.regexp(r"^forest:zone:(glade|clearing)$"))
async def admin_forest_zone(callback: CallbackQuery, state: FSMContext):
    """Зона леса: её грибы и настройки."""
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    await state.clear()
    text, markup = await _forest_zone_view(callback.message, callback.data.split(":")[2])
    await callback.message.edit_text(text, reply_markup=markup)


async def _forest_zone_view(message, area: str) -> tuple:
    """Текст и клавиатура зоны леса (общий вид для меню и перерисовок)."""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    zone = await get_forest_zone(area)
    pool = await get_forest_zone_pool(area)
    emoji = "🌿" if area == "glade" else "🌲"
    title = zone.get("title") or area
    lines = [f"{emoji} {title.upper()}\n"]
    lines.append(
        f"Открыта: {'да' if zone.get('enabled') else 'нет'} · "
        f"поиск: {zone.get('ap_cost')} ОД · "
        f"туристы: {'да' if zone.get('allow_tourists') else 'нет'}"
    )
    if zone.get("boar_enabled"):
        lines.append(
            f"Кабан: вкл · шанс {zone.get('boar_chance') or '— как у кабана'}% · "
            f"гарантия раз в {zone.get('boar_every') or '— как у кабана'} попыток"
        )
    else:
        lines.append("Кабан: выключен")
    rows = []
    if pool:
        lines.append("\nГрибы зоны: числа — ВЕСА (делятся между собой, 10% — «пусто»).\n")
        for s in pool:
            kind_mark = "🍄" if (s.get('kind') or 'edible') == "edible" else "☠"
            lines.append(f"• {kind_mark} {s['name']} — вес {s['chance']}, "
                         f"продажа {s['sell_price']} НМ")
            rows.append([
                InlineKeyboardButton(
                    text=f"{kind_mark} {s['name']}",
                    callback_data=f"forest:card:{s['id']}"),
                InlineKeyboardButton(
                    text=f"⚖️ {s['chance']}",
                    callback_data=f"forest:zchance:{area}:{s['mushroom_id']}"),
                InlineKeyboardButton(
                    text="➖", callback_data=f"forest:zdel:{area}:{s['mushroom_id']}"),
            ])
    else:
        lines.append("\nВ этой зоне пока нет грибов.")

    rows.append([InlineKeyboardButton(
        text="➕ Добавить гриб в зону", callback_data=f"forest:zaddlist:{area}")])
    rows.append([InlineKeyboardButton(
        text="✨ Создать новый гриб", callback_data="forest:new")])
    rows.append([
        InlineKeyboardButton(text="🔄 Открытость", callback_data=f"forest:zset:{area}:enabled"),
        InlineKeyboardButton(text="⚡ Цена поиска", callback_data=f"forest:zset:{area}:ap_cost"),
    ])
    rows.append([
        InlineKeyboardButton(text="🧳 Туристы", callback_data=f"forest:zset:{area}:allow_tourists"),
        InlineKeyboardButton(text="🐗 Кабан", callback_data=f"forest:zset:{area}:boar_enabled"),
    ])
    if zone.get("boar_enabled"):
        rows.append([
            InlineKeyboardButton(text="🎲 Шанс кабана", callback_data=f"forest:zset:{area}:boar_chance"),
            InlineKeyboardButton(text="🔁 Гарантия", callback_data=f"forest:zset:{area}:boar_every"),
        ])
    rows.append([InlineKeyboardButton(text="⬅️ К зонам леса", callback_data="admin:forest")])
    return "\n".join(lines), InlineKeyboardMarkup(inline_keyboard=rows)


@router.callback_query(F.data.regexp(r"^forest:zchance:(glade|clearing):\d+$"))
async def admin_forest_zone_chance(callback: CallbackQuery, state: FSMContext):
    """Ввод веса гриба в зоне."""
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    _, _, area, f_id = callback.data.split(":")
    await state.update_data(forest_zone_chance=(area, int(f_id)))
    await state.set_state(AdminForest.zone_value)
    await callback.message.answer(
        f"⚖️ Новый ВЕС гриба в зоне (числа — веса, «пусто» остаётся 10%).\n"
        f"0 = убрать гриба из этой зоны.\n\nВведи число:"
    )


@router.callback_query(F.data.regexp(r"^forest:zdel:(glade|clearing):\d+$"))
async def admin_forest_zone_del(callback: CallbackQuery, state: FSMContext):
    """Убрать гриба из зоны (сам гриб остаётся в каталоге)."""
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    _, _, area, f_id = callback.data.split(":")
    await remove_forest_mushroom_from_zone(area, int(f_id))
    text, markup = await _forest_zone_view(callback.message, area)
    await callback.message.edit_text(text, reply_markup=markup)


@router.callback_query(F.data.regexp(r"^forest:zaddlist:(glade|clearing)$"))
async def admin_forest_zone_add_list(callback: CallbackQuery, state: FSMContext):
    """Список грибов каталога, которых ещё нет в этой зоне."""
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    area = callback.data.split(":")[2]
    await state.clear()
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    candidates = await get_forest_zone_candidates(area)
    if not candidates:
        await callback.message.answer(
            "➕ Все грибы каталога уже в этой зоне.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 К зоне", callback_data=f"forest:zone:{area}")]]))
        return
    rows = []
    for c in candidates:
        kind_mark = "🍄" if (c.get('kind') or 'edible') == "edible" else "☠"
        rows.append([InlineKeyboardButton(
            text=f"{kind_mark} {c['name']} ({c['sell_price']} НМ)",
            callback_data=f"forest:zadd:{area}:{c['mushroom_id']}")])
    rows.append([InlineKeyboardButton(text="🔙 К зоне", callback_data=f"forest:zone:{area}")])
    await callback.message.answer(
        "➕ Выбери гриб для зоны:", reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))


@router.callback_query(F.data.regexp(r"^forest:zadd:(glade|clearing):\d+$"))
async def admin_forest_zone_add(callback: CallbackQuery, state: FSMContext):
    """Добавить гриба в зону с дефолтным весом."""
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    _, _, area, f_id = callback.data.split(":")
    await add_forest_mushroom_to_zone(area, int(f_id))
    text, markup = await _forest_zone_view(callback.message, area)
    await callback.message.edit_text(text, reply_markup=markup)


@router.callback_query(F.data.regexp(r"^forest:zset:(glade|clearing):(\w+)$"))
async def admin_forest_zone_set_pick(callback: CallbackQuery, state: FSMContext):
    """Ввод настройки зоны (число или 0/1 для переключателя)."""
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    _, _, area, field = callback.data.split(":")
    zone = await get_forest_zone(area)
    hint = {
        "enabled": "1 — зона открыта, 0 — закрыта:",
        "ap_cost": "Сколько ОД стоит поиск в зоне:",
        "allow_tourists": "Пускать ли туристов в зону? 1 — да, 0 — нет:",
        "boar_enabled": "Включить ли кабана в зоне? 1 — да, 0 — нет:",
        "boar_chance": "Шанс встречи с кабаном в % (0 = как у кабана в «⚔️ Враги»):",
        "boar_every": "Гарантия: кабан не чаще раза на N попыток (0 = как у кабана):",
    }.get(field, "Новое значение:")
    await state.update_data(forest_zone_field=(area, field))
    await state.set_state(AdminForest.zone_value)
    await callback.message.answer(
        f"⚙️ {hint}\n\nТекущее значение: {zone.get(field)}\nВведи новое:")


@router.callback_query(F.data == "forest:zset:sold_daily_limit")
async def admin_forest_limit_set(callback: CallbackQuery, state: FSMContext):
    """Ввод суточного лимита выкупа грибов казной."""
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    current = await get_forest_setting("sold_daily_limit", "250")
    await state.update_data(forest_zone_field=("__settings__", "sold_daily_limit"))
    await state.set_state(AdminForest.zone_value)
    await callback.message.answer(
        f"🧺 Сколько НМ казна выкупает грибов за сутки на игрока?\n"
        f"Текущее значение: {current}\n\nВведи число:")


@router.message(AdminForest.zone_value, F.text.regexp(r"^\d+$"))
async def admin_forest_zone_value(message: Message, state: FSMContext):
    """Приём значения настройки зоны / веса гриба в зоне.

    Обработчик обязательно привязан к состоянию AdminForest.zone_value.
    Раньше он висел на голом «сообщение из цифр» без состояния, а роутер
    админа зарегистрирован раньше роутера отчётов: любая цифра, которую
    пилот вводил в сдаче отчёта, уходила сюда и тихо проглатывалась —
    отчёт зависал после фото. Роутер админа без фильтра по правам, поэтому
    страдали все, не только админы.
    """
    data = await state.get_data()
    zone_field = data.get("forest_zone_field")
    zone_chance = data.get("forest_zone_chance")
    if not zone_field and not zone_chance:
        await state.clear()
        return
    try:
        value = int(message.text.strip())
    except (TypeError, ValueError):
        await message.answer("Нужно целое число. Попробуй ещё раз.")
        return

    if zone_chance:
        area, f_id = zone_chance
        if value <= 0:
            await remove_forest_mushroom_from_zone(area, f_id)
            answer = "➖ Гриб убран из зоны."
        else:
            await set_forest_zone_chance(area, f_id, value)
            answer = f"✅ Вес гриба в зоне: {value}."
        await state.clear()
        await message.answer(answer)
        text, markup = await _forest_zone_view(message, area)
        await message.answer(text, reply_markup=markup)
        return

    area, field = zone_field
    if area == "__settings__":
        await set_forest_setting("sold_daily_limit", value)
        await state.clear()
        await message.answer(f"✅ Казна будет выкупать грибы до {value} НМ в сутки.")
        await _admin_forest_zones_view(message)
        return
    await update_forest_zone(area, **{field: value})
    await state.clear()
    label = FOREST_ZONE_FIELDS_LABELS.get(field, field)
    await message.answer(f"✅ {label}: {value}")
    text, markup = await _forest_zone_view(message, area)
    await message.answer(text, reply_markup=markup)


async def _admin_forest_zones_view(message) -> tuple:
    """Текст и клавиатура списка зон леса (общий вид для меню и перерисовок)."""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    zones = await get_forest_zones()
    lines = ["🌲 ЛЕС: ЗОНЫ И ГРИБЫ\n"]
    rows = []
    for area in FOREST_AREAS:
        zone = zones.get(area) or {}
        emoji = "🌿" if area == "glade" else "🌲"
        title = zone.get("title") or area
        mark = "✅" if zone.get("enabled") else "⛔"
        boar = "🐗 кабан" if zone.get("boar_enabled") else "без кабана"
        tour = "туристы ✅" if zone.get("allow_tourists") else "туристы ⛔"
        lines.append(f"{mark} {emoji} {title} — поиск {zone.get('ap_cost')} ОД, {boar}, {tour}")
        rows.append([InlineKeyboardButton(
            text=f"{emoji} {title}", callback_data=f"forest:zone:{area}")])
    limit = await get_forest_setting("sold_daily_limit", "250")
    lines.append(f"\n🧺 Казна выкупает грибы до {limit} НМ в сутки (на игрока).")
    rows.append([InlineKeyboardButton(
        text="🧺 Лимит выкупа казны", callback_data="forest:zset:sold_daily_limit")])
    rows.append([InlineKeyboardButton(text="🔙 В админ-панель", callback_data="admin:menu")])
    return "\n".join(lines), InlineKeyboardMarkup(inline_keyboard=rows)


FOREST_ZONE_FIELDS_LABELS = {
    "enabled": "Зона открыта",
    "ap_cost": "Цена поиска, ОД",
    "allow_tourists": "Туристы допущены",
    "boar_enabled": "Кабан",
    "boar_chance": "Шанс кабана, %",
    "boar_every": "Гарантия кабана",
}


@router.callback_query(F.data.startswith("forest:card:"))
async def admin_forest_card(callback: CallbackQuery, state: FSMContext):
    """Карточка гриба с кнопками правки."""
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    try:
        f_id = int(callback.data.split(":", 2)[2])
    except (ValueError, IndexError):
        return
    await state.update_data(f_id=f_id)
    await _admin_forest_card(callback, f_id)


@router.callback_query(F.data.startswith("forest:kind:"))
async def admin_forest_kind(callback: CallbackQuery, state: FSMContext):
    """Переключает тип гриба: съедобный ⇄ ядовитый."""
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    try:
        f_id = int(callback.data.split(":", 2)[2])
    except (ValueError, IndexError):
        return
    shroom = await get_forest_mushroom_row(f_id)
    if not shroom:
        await callback.message.answer("❌ Гриб не найден.")
        return
    new_kind = "toxic" if (shroom.get('kind') or 'edible') == "edible" else "edible"
    await update_forest_mushroom_field(f_id, "kind", new_kind)
    await log_action(callback.from_user.id, 'edit_forest', None,
                     f"f_id={f_id} kind={new_kind}")
    note = ("☠ Гриб стал ядовитым: его нельзя есть (категория «ресурс»)."
            if new_kind == "toxic" else
            "🍄 Гриб стал съедобным (категория «расходник»).")
    await state.update_data(f_id=f_id)
    await _admin_forest_card(callback, f_id, prefix=f"✅ {note}\n\n")


@router.callback_query(F.data.startswith("forest:market:"))
async def admin_forest_market(callback: CallbackQuery, state: FSMContext):
    """Переключает, можно ли этот гриб выставлять на рынок (items.market_ok)."""
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    try:
        f_id = int(callback.data.split(":", 2)[2])
    except (ValueError, IndexError):
        return
    shroom = await get_forest_mushroom_row(f_id)
    if not shroom:
        await callback.message.answer("❌ Гриб не найден.")
        return
    new_val = 0 if shroom.get('market_ok') else 1
    await update_item(shroom['item_id'], market_ok=new_val)
    await log_action(callback.from_user.id, 'edit_forest', None,
                     f"f_id={f_id} market_ok={new_val}")
    await state.update_data(f_id=f_id)
    await _admin_forest_card(callback, f_id)


@router.callback_query(F.data == "forest:addlist")
async def admin_forest_add_list(callback: CallbackQuery, state: FSMContext):
    """Выбор расходника/ресурса для добавления в пул леса."""
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    await state.update_data(add_forest_active=True)
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    candidates = await get_forest_mushroom_candidates()
    lines = ["➕ Добавление гриба\n🍄 Пусть лес будет богаче!\n"]
    rows = []
    if candidates:
        for c in candidates:
            rows.append([InlineKeyboardButton(
                text=f"{c['name']} (продажа {c['sell_price']} НМ)",
                callback_data=f"forest:add:{c['id']}",
            )])
    else:
        lines.append("Все подходящие расходники/ресурсы уже в пуле леса.")
    lines.append("\nДобавится в пул с весом 10 — потом настроишь вес, фото, цену и тип.")
    rows.append([InlineKeyboardButton(text="🔙 К списку грибов", callback_data="admin:forest")])
    await callback.message.edit_text(
        "\n".join(lines), reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))


@router.callback_query(F.data.startswith("forest:add:"))
async def admin_forest_add(callback: CallbackQuery, state: FSMContext):
    """Добавляет расходник/ресурс в пул леса и открывает его карточку."""
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    try:
        item_id = int(callback.data.split(":", 2)[2])
    except (ValueError, IndexError):
        return
    f_id = await add_forest_mushroom(item_id, 10)
    shroom = await get_forest_mushroom_row(f_id) if f_id else None
    if not shroom:
        await callback.message.answer("❌ Не удалось добавить гриб.")
        return
    await state.update_data(f_id=f_id)
    await _admin_forest_card(callback, f_id, prefix=f"✅ «{shroom['name']}» добавлен в пул леса.\n\n")


@router.callback_query(F.data.startswith("forest:del:"))
async def admin_forest_del(callback: CallbackQuery, state: FSMContext):
    """Убирает гриб из пула леса и возвращает в список."""
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    try:
        f_id = int(callback.data.split(":", 2)[2])
    except (ValueError, IndexError):
        return
    shroom = await get_forest_mushroom_row(f_id)
    if not shroom:
        await callback.message.answer("❌ Гриб не найден.")
        return
    removed = await remove_forest_mushroom(f_id)
    await log_action(callback.from_user.id, 'edit_forest', None,
                     f"f_id={f_id} removed={removed}")
    await state.clear()
    await admin_forest_menu(callback, state)


@router.callback_query(F.data.startswith("forest_field:"))
async def admin_forest_field_pick(callback: CallbackQuery, state: FSMContext):
    """Выбор поля гриба для правки: шанс / фото / цена."""
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    field = callback.data.split(":")[1]
    if field not in FOREST_FIELD_LABELS:
        return
    data = await state.get_data()
    if not data.get('f_id'):
        await callback.message.answer("❌ Гриб не выбран. Открой карточку гриба заново.")
        return
    await state.update_data(field=field)
    await state.set_state(AdminForest.value)
    shroom = await get_forest_mushroom_row(data.get('f_id')) if data.get('f_id') else None
    prompt = FOREST_INPUT_PROMPTS[field]
    if shroom:
        cur = shroom.get({
            "chance": "chance",
            "sell_price": "sell_price",
            "photo": "photo_file_id",
        }.get(field, field))
        if field == "photo":
            cur_text = f"{'есть картинка' if cur else 'нет картинки'}"
        else:
            cur_text = ("—" if cur is None else str(cur))
        prompt = (f"{FOREST_FIELD_LABELS[field]} гриба «{shroom['name']}».\n"
                  f"Сейчас: {cur_text}.\n\n{prompt}")
    if field == "photo" and shroom and shroom.get('photo_file_id'):
        try:
            await callback.message.answer_photo(
                shroom['photo_file_id'], caption=prompt, reply_markup=cancel_keyboard())
            return
        except Exception:
            pass
    await callback.message.answer(prompt, reply_markup=cancel_keyboard())


@router.message(AdminForest.value)
async def admin_forest_value(message: Message, state: FSMContext):
    """Значение поля гриба: шанс % / цена / фото."""
    data = await state.get_data()
    f_id = data.get('f_id')
    field = data.get('field')
    shroom = await get_forest_mushroom_row(f_id) if f_id else None
    if not shroom or field not in FOREST_FIELD_LABELS:
        await state.clear()
        await message.answer("❌ Гриб/поле не распознаны. Начни заново: админ → Грибы леса.")
        return

    if field in ("chance", "sell_price"):
        text = (message.text or "").strip()
        parsed = int(text) if text.isdigit() else None
        if parsed is None or parsed < 0:
            await message.answer(f"❌ Ожидаю целое число ≥ 0.\n{FOREST_INPUT_PROMPTS[field]}",
                                 reply_markup=cancel_keyboard())
            return
        if field == "chance":
            if parsed > 100:
                await message.answer("❌ Вес — от 0 до 100.",
                                     reply_markup=cancel_keyboard())
                return
            await update_forest_mushroom_field(f_id, "chance", parsed)
        else:
            await set_forest_mushroom_sell_price(f_id, parsed)
        label = f"{parsed} НМ" if field == "sell_price" else (f"вес {parsed}" if parsed > 0 else "не выпадает")
    else:  # photo
        if (message.text or "").strip() == "-":
            parsed = None
        elif message.photo:
            parsed = message.photo[-1].file_id
        else:
            await message.answer("❌ Отправь именно фото (или «-» для очистки).",
                                 reply_markup=cancel_keyboard())
            return
        await update_forest_mushroom_field(f_id, "photo_file_id", parsed)
        label = "убрано" if parsed is None else "обновлено"

    await log_action(message.from_user.id, 'edit_forest', None,
                     f"f_id={f_id} {field}={parsed}")
    await state.clear()
    await _admin_forest_card(
        message, f_id,
        prefix=f"✅ «{shroom['name']}»: {FOREST_FIELD_LABELS[field]} = {label}.\n\n",
    )


@router.callback_query(F.data == "forest:new")
async def admin_forest_new(callback: CallbackQuery, state: FSMContext):
    """Мастер создания нового гриба: название → описание → цена → вес →
    тип → фото."""
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    await state.clear()
    await state.set_state(AdminForest.c_name)
    await callback.message.answer(
        "✨ Создание гриба леса\n🍄 Пул леса пополнится новым грибом.\n\n"
        "Шаг 1/6 — Название гриба (например «Сыроежка»):",
        reply_markup=cancel_keyboard()
    )


@router.message(AdminForest.c_name)
async def admin_forest_new_name(message: Message, state: FSMContext):
    name = (message.text or "").strip()
    if not name:
        await message.answer("❌ Введи название гриба.", reply_markup=cancel_keyboard())
        return
    if len(name) > 60:
        await message.answer("❌ Слишком длинное название — максимум 60 символов.",
                             reply_markup=cancel_keyboard())
        return
    await state.update_data(c_name=name)
    await state.set_state(AdminForest.c_desc)
    await message.answer("Шаг 2/6 — Описание гриба (или «-» если нет):",
                         reply_markup=cancel_keyboard())


@router.message(AdminForest.c_desc)
async def admin_forest_new_desc(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    await state.update_data(c_desc=None if text in ("-", "—") else text[:300])
    await state.set_state(AdminForest.c_sell_price)
    await message.answer("Шаг 3/6 — Цена продажи скупщику, Нордмарок (целое число ≥ 0):",
                         reply_markup=cancel_keyboard())


@router.message(AdminForest.c_sell_price)
async def admin_forest_new_sell_price(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    parsed = int(text) if text.isdigit() else None
    if parsed is None or parsed < 0:
        await message.answer("❌ Введи целое число ≥ 0.", reply_markup=cancel_keyboard())
        return
    await state.update_data(c_sell_price=parsed)
    await state.set_state(AdminForest.c_chance)
    await message.answer(
        "Шаг 4/6 — Вес гриба в пуле леса (целое число 0–100; 0 = не выпадает).\n"
        "Это не процент: все веса делят между собой 90% находки.",
        reply_markup=cancel_keyboard()
    )


@router.message(AdminForest.c_chance)
async def admin_forest_new_chance(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    parsed = int(text) if text.isdigit() else None
    if parsed is None or parsed < 0 or parsed > 100:
        await message.answer("❌ Введи целое число от 0 до 100.",
                             reply_markup=cancel_keyboard())
        return
    await state.update_data(c_chance=parsed)
    await state.set_state(AdminForest.c_kind)
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    await message.answer(
        "Шаг 5/6 — Тип гриба:\n"
        "🍄 Съедобный — распяется расходником (сырым лечит в бою).\n"
        "☠ Ядовитый — ресурс (есть нельзя).",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🍄 Съедобный", callback_data="forest:new_kind:edible")],
            [InlineKeyboardButton(text="☠ Ядовитый", callback_data="forest:new_kind:toxic")],
            [InlineKeyboardButton(text="✖️ Отмена", callback_data="back:to_main")],
        ])
    )


@router.callback_query(F.data.startswith("forest:new_kind:"))
async def admin_forest_new_kind(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    kind = callback.data.split(":", 2)[2]
    if kind not in ("edible", "toxic"):
        return
    await state.update_data(c_kind=kind)
    await state.set_state(AdminForest.c_photo)
    await callback.message.answer(
        "Шаг 6/6 — Пришли фото гриба (Telegram-фото) или «-», если фото нет:",
        reply_markup=cancel_keyboard()
    )


@router.message(AdminForest.c_photo)
async def admin_forest_new_photo(message: Message, state: FSMContext):
    photo_file_id = None
    if message.photo:
        photo_file_id = message.photo[-1].file_id
    else:
        text = (message.text or "").strip()
        if text not in ("-", "—"):
            await message.answer("❌ Отправь именно фото (или «-» без фото).",
                                 reply_markup=cancel_keyboard())
            return
    data = await state.get_data()
    sell_price = int(data.get('c_sell_price', 0))
    chance = int(data.get('c_chance', 10))
    kind = data.get('c_kind', 'edible')
    ok, res = await create_forest_mushroom(
        name=data['c_name'],
        description=data.get('c_desc'),
        sell_price=sell_price,
        chance=chance,
        kind=kind,
        photo_file_id=photo_file_id,
        added_by=message.from_user.id,
    )
    if not ok:
        await message.answer(f"❌ {res}", reply_markup=cancel_keyboard())
        return
    f_id = res['f_id']
    await log_action(message.from_user.id, 'edit_forest', None,
                     f"created item_id={res['item_id']} f_id={f_id} sell={sell_price} "
                     f"chance={chance} kind={kind} photo={'yes' if photo_file_id else 'no'}")
    await state.clear()
    await state.update_data(f_id=f_id)
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    if photo_file_id:
        try:
            await message.answer_photo(
                photo_file_id,
                caption=f"✅ Гриб «{data['c_name']}» создан в пуле леса.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="Открыть карточку", callback_data=f"forest:card:{f_id}")],
                ]))
            return
        except Exception:
            pass
    await _admin_forest_card(
        message, f_id,
        prefix=f"✅ Гриб «{data['c_name']}» создан в пуле леса.\n\n")


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
    cur_desc = loc.get('description') or '—'
    await callback.message.edit_text(
        f"📝 Описание «{loc['name']}».\n"
        f"Сейчас: {cur_desc}\n\n"
        f"Отправь новый текст (или «-», чтобы очистить):",
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
# Сезоны картинок локаций (совпадают с LOCATION_SEASONS в database/db.py).
LOCATION_SEASON_LABEL = {
    "winter": "❄️ Зима", "spring": "🌱 Весна", "summer": "☀️ Лето", "autumn": "🍂 Осень",
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
    seasons = location_season_photos_raw(loc)
    keys = loc.keys()
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    rows = []
    for k in TOD_KEYS:
        mark = "✅" if f"photo_{k}" in keys and loc[f"photo_{k}"] else "—"
        rows.append([InlineKeyboardButton(
            text=f"{mark} {TOD_LABEL[k]}",
            callback_data=f"loc:photo_set:{k}"
        )])
    for season in LOCATION_SEASONS:
        count = len([v for v in (seasons.get(season) or {}).values() if v])
        rows.append([InlineKeyboardButton(
            text=f"{count}/4 {LOCATION_SEASON_LABEL[season]}" if count else f"— {LOCATION_SEASON_LABEL[season]}",
            callback_data=f"loc:season:{season}"
        )])
    rows.append([InlineKeyboardButton(text="🚫 Убрать все (без сезона)", callback_data="loc:photos:clear")])
    rows.append([InlineKeyboardButton(text="🍂 Убрать все сезонные", callback_data="loc:photos:clear_seasons")])
    # Опушка леса — самостоятельная картинка (место сбора грибов), намеренно
    # не картинка входа: задаётся отдельной кнопкой.
    glade_line = ""
    if loc.get("key") == "forest":
        has_glade = bool(location_glade_photo(loc))
        has_clearing = bool(location_clearing_photo(loc))
        rows.append([InlineKeyboardButton(
            text=f"{'✅' if has_glade else '—'} 🌿 Опушка (сбор грибов)",
            callback_data="loc:glade_set")])
        rows.append([InlineKeyboardButton(
            text=f"{'✅' if has_clearing else '—'} 🌲 Прогалина (вглубь леса)",
            callback_data="loc:clearing_set")])
        glade_line = (
            f"Опушка: {'своя картинка' if has_glade else 'локальный файл по сезону'}\n"
            f"Прогалина: {'своя картинка' if has_clearing else 'локальный файл по сезону'}\n"
        )
    rows.append([InlineKeyboardButton(text="🔙 Назад", callback_data="loc:building_pick")])
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    season_line = " | ".join(
        f"{LOCATION_SEASON_LABEL[s]}: {len([v for v in (seasons.get(s) or {}).values() if v])}"
        for s in LOCATION_SEASONS)
    text = (
        f"🖼 Картинки «{loc['name']}».\n"
        f"Без сезона: {', '.join(filled)}\n"
        f"По сезонам: {season_line}\n"
        f"{glade_line}"
        f"\n"
        f"🌄 Без сезона — показывается всегда.\n"
        f"🍂 По сезонам — сменяются сами по календарю (зима/весна/лето/осень), "
        f"внутри сезона — по времени суток.\n"
        f"Нажми слот и отправь фото (или «-» чтобы убрать):"
    )
    if isinstance(source, CallbackQuery):
        await source.message.edit_text(text, reply_markup=kb)
    else:
        await source.answer(text, reply_markup=kb)


async def _loc_season_photos_pick_send(source, loc_id: int, season: str):
    """Пикер картинок времени суток для конкретного сезона локации."""
    loc = await get_location(loc_id)
    if not loc:
        if isinstance(source, CallbackQuery):
            await source.message.edit_text("❌ Локация не найдена.")
        else:
            await source.answer("❌ Локация не найдена.")
        return
    slots = location_season_photos_raw(loc).get(season) or {}
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    rows = []
    for k in TOD_KEYS:
        mark = "✅" if slots.get(k) else "—"
        rows.append([InlineKeyboardButton(
            text=f"{mark} {TOD_LABEL[k]}",
            callback_data=f"loc:season_photo_set:{season}:{k}"
        )])
    rows.append([InlineKeyboardButton(text="🚫 Убрать сезон", callback_data=f"loc:season_clear:{season}")])
    rows.append([InlineKeyboardButton(text="🔙 Назад", callback_data="loc:photos")])
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    text = (
        f"🍂 {LOCATION_SEASON_LABEL[season]} «{loc['name']}».\n"
        f"Эти картинки включатся сами, когда наступит время года.\n\n"
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
    await state.update_data(photo_season=None, photo_kind=None)


@router.callback_query(F.data.regexp(r"^loc:season:(winter|spring|summer|autumn)$"))
async def loc_season_photos_pick(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    data = await state.get_data()
    loc_id = data.get('target_id')
    if not loc_id:
        return
    season = callback.data.split(":")[2]
    await _loc_season_photos_pick_send(callback, loc_id, season)


@router.callback_query(F.data == "loc:photos:clear_seasons")
async def loc_photos_clear_seasons(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    data = await state.get_data()
    loc_id = data.get('target_id')
    if not loc_id:
        return
    await clear_location_season_photos(loc_id)
    await _loc_photos_pick_send(callback, loc_id)


@router.callback_query(F.data.regexp(r"^loc:season_clear:(winter|spring|summer|autumn)$"))
async def loc_season_clear(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    data = await state.get_data()
    loc_id = data.get('target_id')
    if not loc_id:
        return
    season = callback.data.split(":")[2]
    await clear_location_season(loc_id, season)
    await _loc_season_photos_pick_send(callback, loc_id, season)


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


@router.callback_query(F.data == "loc:glade_set")
async def loc_glade_set(callback: CallbackQuery, state: FSMContext):
    """Запрос картинки опушки леса — отдельной от картинки входа."""
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    data = await state.get_data()
    loc_id = data.get('target_id')
    if not loc_id:
        return
    loc = await get_location(loc_id)
    if not loc or loc.get("key") != "forest":
        await callback.message.edit_text("❌ Опушка есть только у локации «Лес на окраине».")
        return
    await state.set_state(AdminLocation.preview)
    await state.update_data(photo_kind="glade", photo_tod=None, photo_season=None)
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="loc:photos")]
    ])
    has_photo = bool(location_glade_photo(loc))
    caption = (f"🌲 Опушка «Лес на окраине» — сейчас есть картинка.\n"
               f"Отправь новую (или «-» чтобы убрать и вернуть локальный файл по сезону):")
    if has_photo:
        try:
            await callback.message.answer_photo(
                location_glade_photo(loc), caption=caption, reply_markup=kb)
            return
        except Exception:
            pass
    await callback.message.edit_text(
        f"🌲 Опушка «{loc['name']}» "
        f"(сейчас: {'своя картинка' if has_photo else 'локальный файл по сезону'}).\n"
        f"Отправь фото (или «-» чтобы убрать):",
        reply_markup=kb
    )


@router.callback_query(F.data == "loc:glade_clear")
async def loc_glade_clear(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    data = await state.get_data()
    loc_id = data.get('target_id')
    if not loc_id:
        return
    await update_location_glade_photo(loc_id, None)
    await _loc_photos_pick_send(callback, loc_id)


@router.callback_query(F.data == "loc:clearing_set")
async def loc_clearing_set(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    data = await state.get_data()
    loc_id = data.get('target_id')
    if not loc_id:
        return
    loc = await get_location(loc_id)
    if not loc or loc.get("key") != "forest":
        await callback.message.edit_text("❌ Прогалина есть только у локации «Лес на окраине».")
        return
    await state.set_state(AdminLocation.preview)
    await state.update_data(photo_kind="clearing", photo_tod=None, photo_season=None)
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="loc:photos")]
    ])
    has_photo = bool(location_clearing_photo(loc))
    caption = (f"🌲 Прогалина (лес на окраине) — сейчас есть картинка.\n"
               f"Отправь новую (или «-» чтобы убрать и вернуть локальный файл по сезону):")
    if has_photo:
        try:
            await callback.message.answer_photo(
                location_clearing_photo(loc), caption=caption, reply_markup=kb)
            return
        except Exception:
            pass
    await callback.message.edit_text(
        f"🌲 Прогалина «{loc['name']}» "
        f"(сейчас: {'своя картинка' if has_photo else 'локальный файл по сезону'}).\n"
        f"Отправь фото (или «-» чтобы убрать):",
        reply_markup=kb
    )


@router.callback_query(F.data == "loc:clearing_clear")
async def loc_clearing_clear(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    data = await state.get_data()
    loc_id = data.get('target_id')
    if not loc_id:
        return
    await update_location_clearing_photo(loc_id, None)
    await _loc_photos_pick_send(callback, loc_id)


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
    await state.update_data(photo_tod=tod, photo_season=None, photo_kind=None)
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    loc = await get_location(loc_id)
    has_photo = bool(loc and loc.get(f"photo_{tod}"))
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="loc:photos")]
    ])
    caption = (f"🖼 {TOD_LABEL[tod]} локации «{loc['name'] if loc else ''}» — сейчас есть картинка.\n"
               f"Отправь новую фото (или «-» чтобы убрать для этого времени):")
    if has_photo:
        try:
            await callback.message.answer_photo(
                loc[f"photo_{tod}"], caption=caption, reply_markup=kb)
            return
        except Exception:
            pass
    await callback.message.edit_text(
        f"🖼 {TOD_LABEL[tod]} локации «{loc['name'] if loc else ''}» "
        f"(сейчас: {'есть картинка' if has_photo else 'нет'}).\n"
        f"Отправь фото (или «-» чтобы убрать для этого времени):",
        reply_markup=kb
    )


@router.callback_query(F.data.regexp(
    r"^loc:season_photo_set:(winter|spring|summer|autumn):(dawn|day|sunset|night)$"
))
async def loc_season_photo_set(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    parts = callback.data.split(":")
    season, tod = parts[2], parts[3]
    data = await state.get_data()
    loc_id = data.get('target_id')
    if not loc_id:
        return
    await state.set_state(AdminLocation.preview)
    await state.update_data(photo_season=season, photo_tod=tod)
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    loc = await get_location(loc_id)
    slots = (location_season_photos_raw(loc) or {}).get(season) or {}
    has_photo = bool(slots.get(tod))
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data=f"loc:season:{season}")]
    ])
    caption = (f"🖼 {LOCATION_SEASON_LABEL[season]} · {TOD_LABEL[tod]} "
               f"локации «{loc['name'] if loc else ''}» — сейчас есть картинка.\n"
               f"Отправь новую фото (или «-» чтобы убрать для этого времени):")
    if has_photo:
        try:
            await callback.message.answer_photo(
                slots[tod], caption=caption, reply_markup=kb)
            return
        except Exception:
            pass
    await callback.message.edit_text(
        f"🖼 {LOCATION_SEASON_LABEL[season]} · {TOD_LABEL[tod]} локации "
        f"«{loc['name'] if loc else ''}» "
        f"(сейчас: {'есть картинка' if has_photo else 'нет'}).\n"
        f"Отправь фото (или «-» чтобы убрать для этого времени):",
        reply_markup=kb
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
    photo_season = data.get('photo_season')
    photo_tod = data.get('photo_tod')
    # v0.18.18: слот «Опушка» — своя картинка, сезон/время тут не участвуют.
    if data.get('photo_kind') == 'glade':
        await update_location_glade_photo(loc_id, file_id)
        await log_action(message.from_user.id, 'edit_location', loc_id,
                         f"glade_photo={'file_id' if file_id else 'cleared'}")
        await state.clear()
        await _loc_photos_pick_send(message, loc_id)
        return
    if data.get('photo_kind') == 'clearing':
        await update_location_clearing_photo(loc_id, file_id)
        await log_action(message.from_user.id, 'edit_location', loc_id,
                         f"clearing_photo={'file_id' if file_id else 'cleared'}")
        await state.clear()
        await _loc_photos_pick_send(message, loc_id)
        return
    if photo_season in LOCATION_SEASONS and photo_tod and photo_tod in TOD_KEYS:
        await update_location_season_photo(loc_id, photo_season, photo_tod, file_id)
        await log_action(message.from_user.id, 'edit_location', loc_id,
                         f"season_{photo_season}_photo_{photo_tod}="
                         f"{'file_id' if file_id else 'cleared'}")
        await _loc_season_photos_pick_send(message, loc_id, photo_season)
        return
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


# ============================================================================
# ВРАГИ: ЕДИНЫЙ РЕДАКТОР (данж + лес + рыбалка)
# ============================================================================
# Все враги игры собраны в одном разделе админки. Список источников и этажей
# строится динамически: новый данж или новый этаж появляются сами (floors_count),
# ничего дописывать в коде не нужно.
#
#   src = 'dn' — подземелье (loc = d-<dungeon_id>-<floor>), правится существующим
#          редактором врагов данжа (dungeon:enemy:<id> + enemy_field:*);
#   src = 'forest'  — лес      (loc = forest);
#   src = 'fishing' — рыбалка  (loc = <водоём>, напр. reservoir).
# Для леса и рыбалки — своя карточка на общих функциях forest_enemies /
# fishing_enemies (см. database/db.py), с полями и дропами в одном формате.
# Значения src для леса/рыбалки совпадают с ключами ENEMY_SOURCE_TABLES в db.py.

ENEMY_SRC_FOREST = 'forest'
ENEMY_SRC_FISHING = 'fishing'
ENEMY_SRC_DUNGEON = 'dn'

# Человеческие названия источников.
ENEMY_SOURCE_TITLES = {
    ENEMY_SRC_DUNGEON: "🏰 Подземелье",
    ENEMY_SRC_FOREST: "🌲 Лес на окраине",
    ENEMY_SRC_FISHING: "🎣 Рыбалка",
}

# Названия водоёмов рыбалки для меню.
FISHING_SPOT_TITLES = {
    "lake": "🏞 Озеро",
    "reservoir": "🌊 Подземное водохранилище",
}

# Поля карточки врага леса/рыбалки: ключ → (подпись, промпт, тип).
#   int — целое ≥ 0, percent — 0–100, float1 — число с одним знаком (шанс),
#   text — строка, dash — можно «-» чтобы очистить.
ENEMY_FIELDS = {
    "hp": ("❤️ HP", "Введи HP врага (целое число ≥ 1):", "int"),
    "dmg_min": ("🗡 Урон (мин)", "Введи минимальный урон врага (целое ≥ 0):", "int"),
    "dmg_max": ("🗡 Урон (макс)", "Введи максимальный урон врага (целое ≥ 0):", "int"),
    "dodge": ("💨 Уклонение", "Введи шанс уклонения врага, % (0–100):", "percent"),
    "chance": ("🎲 Шанс встречи", "Введи шанс встречи с врагом на одну попытку, % (0–100; 0 = выключить):", "percent"),
    "pity_target": ("🧿 Гарантия", "Введи, через сколько попыток встреча гарантирована (0 = без гарантии):", "int"),
    "loss_ap": ("⚡ Потеря ОД", "Введи, сколько ОД теряет игрок при поражении (целое ≥ 0):", "int"),
    "reward_nm": ("💰 Награда НМ", "Введи награду за победу, Нордмарок (целое ≥ 0):", "int"),
    "description": ("📝 Описание", "Введи описание врага (текст, до 400 символов). Или «-» чтобы очистить:", "dash"),
    "photo_key": ("🖼 Ключ картинки", "Введи локальный ключ картинки врага, например city/mollusk "
                                      "(файлы city/mollusk_day.jpg / _night.jpg). Или «-» чтобы убрать:", "dash"),
}


def _enemy_loc_title(src: str, loc: str) -> str:
    """Заголовок локации врага для карточек и меню."""
    if src == ENEMY_SRC_DUNGEON:
        parts = loc.split("-")  # d-<dungeon_id>-<floor>
        if len(parts) == 3:
            return f"{ENEMY_SOURCE_TITLES[ENEMY_SRC_DUNGEON]}, этаж {parts[2]}"
        return ENEMY_SOURCE_TITLES[ENEMY_SRC_DUNGEON]
    if src == ENEMY_SRC_FOREST:
        return ENEMY_SOURCE_TITLES[ENEMY_SRC_FOREST]
    return FISHING_SPOT_TITLES.get(loc, f"🎣 Рыбалка: {loc}")


def _enemy_list_cb(src: str, loc: str) -> str:
    return f"enemy:list:{src}:{loc}"


async def _admin_enemies_root(callback: CallbackQuery):
    """Корень единого редактора врагов: данжи + лес + рыбалка."""
    lines = [
        "⚔️ ВРАГИ\n\n",
        "Все враги игры в одном месте. Список данжей, их этажей и водоёмов "
        "собирается автоматически — новые появятся сами.",
    ]
    rows = []
    dungeons = await get_all_dungeons(training=False)
    for d in dungeons:
        floors = int(d.get('floors_count') or 1)
        lines.append(f"\n🏰 {d['name']} — этажей: {floors}")
        rows.append([InlineKeyboardButton(
            text=f"🏰 {d['name']}",
            callback_data=f"enemy:dn:{d['id']}")])
    forest_enemies = await get_source_enemies(ENEMY_SRC_FOREST)
    lines.append(f"\n🌲 Лес на окраине — врагов: {len(forest_enemies)}")
    rows.append([InlineKeyboardButton(
        text="🌲 Лес на окраине",
        callback_data=_enemy_list_cb(ENEMY_SRC_FOREST, 'forest'))])
    spots = await get_fishing_spots()
    lines.append(f"\n🎣 Рыбалка — водоёмов с врагами: {len(spots)}")
    rows.append([InlineKeyboardButton(
        text="🎣 Рыбалка",
        callback_data=f"enemy:fi")])
    rows.append([InlineKeyboardButton(text="🔙 В админ-панель", callback_data="admin:menu")])
    await callback.message.edit_text("".join(lines),
                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))


@router.callback_query(F.data == "admin:enemies")
async def admin_enemies_menu(callback: CallbackQuery, state: FSMContext):
    """Вход в единый редактор врагов."""
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    await state.clear()
    await _admin_enemies_root(callback)


@router.callback_query(F.data.regexp(r"^enemy:dn:\d+$"))
async def admin_enemies_dungeon_floors(callback: CallbackQuery, state: FSMContext):
    """Этажи данжа — список строится по floors_count, новые этажи появятся сами."""
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    try:
        dungeon_id = int(callback.data.split(":")[2])
    except (ValueError, IndexError):
        return
    dng = await get_dungeon(dungeon_id)
    if not dng:
        await callback.message.answer("❌ Подземелье не найдено.")
        return
    floors = int(dng.get('floors_count') or 1)
    lines = [f"🏰 {dng['name']}\n\nЭтажи: {floors}. Выбери этаж — увидишь его врагов.\n"]
    rows = []
    for floor in range(1, floors + 1):
        enemies = await get_floor_enemies(dungeon_id, floor)
        lines.append(f"• Этаж {floor} — врагов: {len(enemies)}")
        rows.append([InlineKeyboardButton(
            text=f"Этаж {floor} — врагов: {len(enemies)}",
            callback_data=_enemy_list_cb(ENEMY_SRC_DUNGEON, f"d-{dungeon_id}-{floor}"))])
    rows.append([InlineKeyboardButton(text="🔙 К врагам", callback_data="admin:enemies")])
    await callback.message.edit_text("\n".join(lines),
                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))


@router.callback_query(F.data == "enemy:fi")
async def admin_enemies_fishing_spots(callback: CallbackQuery, state: FSMContext):
    """Водоёмы рыбалки, где есть враги."""
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    spots = await get_fishing_spots()
    lines = ["🎣 РЫБАЛКА\n\nВодоёмы, в которых ловится не только рыба:\n"]
    rows = []
    for spot in spots:
        title = FISHING_SPOT_TITLES.get(spot['spot'], spot['spot'])
        lines.append(f"• {title} — врагов: {spot['c']}")
        rows.append([InlineKeyboardButton(
            text=f"{title} — {spot['c']}",
            callback_data=_enemy_list_cb(ENEMY_SRC_FISHING, spot['spot']))])
    rows.append([InlineKeyboardButton(text="🔙 К врагам", callback_data="admin:enemies")])
    await callback.message.edit_text("\n".join(lines),
                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))


@router.callback_query(F.data.regexp(r"^enemy:list:[a-z]+:[\w-]+$"))
async def admin_enemies_list(callback: CallbackQuery, state: FSMContext):
    """Список врагов источника/локации."""
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    _, _, src, loc = callback.data.split(":", 3)
    rows = []
    lines = [f"⚔️ {_enemy_loc_title(src, loc)}\n"]
    if src == ENEMY_SRC_DUNGEON:
        parts = loc.split("-")
        dungeon_id, floor = int(parts[1]), int(parts[2])
        enemies = await get_floor_enemies(dungeon_id, floor)
        for e in enemies:
            boss = "👑 " if e.get('is_boss') else ""
            lines.append(f"• {boss}{e['name']} — HP {e['hp']}, АТК {e['attack']}, "
                         f"УКЛ {e.get('dodge', 0)}%")
            rows.append([InlineKeyboardButton(
                text=f"{boss}{e['name']}",
                callback_data=f"enemy:dcard:{src}:{loc}:{e['id']}")])
    else:
        enemies = await get_source_enemies(src, spot=(None if src == ENEMY_SRC_FOREST else loc))
        for e in enemies:
            mark = "" if e.get('enabled', 1) else "⛔ "
            lines.append(f"• {mark}{e['name']} — HP {e['hp']}, урон {e['dmg_min']}–{e['dmg_max']}, "
                         f"встреча {e['chance']}%")
            rows.append([InlineKeyboardButton(
                text=f"{mark}{e['name']}",
                callback_data=f"enemy:card:{src}:{loc}:{e['id']}")])
    if not enemies:
        lines.append("\nВрагов пока нет. Можно добавить.")
    lines.append("\nНажми на врага, чтобы настроить его.")
    rows.append([InlineKeyboardButton(text="➕ Добавить врага",
                                      callback_data=f"enemy:new:{src}:{loc}")])
    back = ("enemy:fi" if src == ENEMY_SRC_FISHING
            else f"enemy:dn:{loc.split('-')[1]}" if src == ENEMY_SRC_DUNGEON
            else "admin:enemies")
    rows.append([InlineKeyboardButton(text="🔙 Назад", callback_data=back)])
    await callback.message.edit_text("\n".join(lines),
                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))


@router.callback_query(F.data.regexp(r"^enemy:dcard:"))
async def admin_enemies_dungeon_card(callback: CallbackQuery, state: FSMContext):
    """Карточка врага данжа — открываем существующий редактор (он и так полный)."""
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    _, _, src, loc, enemy_id = callback.data.split(":", 4)
    await state.update_data(enemy_id=int(enemy_id))
    await _enemy_card_send(callback, int(enemy_id))


async def _source_enemy_send(target, src: str, loc: str, enemy_id: int, edit: bool = True):
    """Карточка врага леса/рыбалки с кнопками правки."""
    from aiogram.types import InlineKeyboardMarkup as _KB, InlineKeyboardButton as _B
    enemy = await get_source_enemy(src, enemy_id)
    if not enemy:
        await target.answer("❌ Враг не найден.")
        return
    drops = await get_source_enemy_drops(src, enemy_id)
    enabled = enemy.get('enabled', 1)
    text = (
        f"⚔️ {enemy['name']}\n"
        f"📍 {_enemy_loc_title(src, loc)}\n"
        f"──────────────\n"
        f"{'✅ Встречается' if enabled else '⛔ Выключен (не встречается)'}\n"
        f"❤️ HP: {enemy['hp']}\n"
        f"🗡 Урон: {enemy['dmg_min']}–{enemy['dmg_max']}\n"
        f"💨 Уклонение: {enemy['dodge']}%\n"

        f"🎲 Шанс встречи: {enemy['chance']}% (за попытку)\n"
        f"🧿 Гарантия: раз в {enemy['pity_target'] or '—'} попыток\n"
        f"⚡ Потеря ОД при поражении: {enemy['loss_ap']}\n"
        f"💰 Награда: {enemy['reward_nm']} НМ\n"
        f"💼 Дропы: {len(drops)}\n"
        f"🖼 Фото: {'есть' if enemy.get('image') else (enemy.get('photo_key') or 'нет')}\n\n"
        f"{enemy.get('description') or ''}\n\n"
        f"Что изменить?"
    )
    base = f"enemy:card:{src}:{loc}:{enemy_id}"
    rows = [
        [_B(text="❤️ HP", callback_data=f"enemy:fld:{src}:{loc}:{enemy_id}:hp"),
         _B(text="🗡 Урон", callback_data=f"enemy:fld:{src}:{loc}:{enemy_id}:dmg_min")],
        [_B(text="🗡 Урон макс", callback_data=f"enemy:fld:{src}:{loc}:{enemy_id}:dmg_max"),
         _B(text="💨 Уклонение", callback_data=f"enemy:fld:{src}:{loc}:{enemy_id}:dodge")],
        [_B(text="🎲 Шанс встречи", callback_data=f"enemy:fld:{src}:{loc}:{enemy_id}:chance"),
         _B(text="🧿 Гарантия", callback_data=f"enemy:fld:{src}:{loc}:{enemy_id}:pity_target")],
        [_B(text="⚡ Потеря ОД", callback_data=f"enemy:fld:{src}:{loc}:{enemy_id}:loss_ap"),
         _B(text="💰 Награда НМ", callback_data=f"enemy:fld:{src}:{loc}:{enemy_id}:reward_nm")],
        [_B(text="💼 Дропы", callback_data=f"enemy:drops:{src}:{loc}:{enemy_id}")],
        [_B(text="🖼 Фото", callback_data=f"enemy:photo:{src}:{loc}:{enemy_id}"),
         _B(text="🔑 Ключ картинки", callback_data=f"enemy:fld:{src}:{loc}:{enemy_id}:photo_key")],
        [_B(text="📝 Описание", callback_data=f"enemy:fld:{src}:{loc}:{enemy_id}:description")],
        [_B(text="⛔ Включить/выключить" if enabled else "✅ Включить",
              callback_data=f"enemy:tog:{src}:{loc}:{enemy_id}")],
        [_B(text="🗑 Удалить врага", callback_data=f"enemy:del:{src}:{loc}:{enemy_id}")],
        [_B(text="🔙 К списку", callback_data=_enemy_list_cb(src, loc))],
    ]
    kb = _KB(inline_keyboard=rows)
    if edit and hasattr(target, 'message') and target.message is not None:
        await target.message.edit_text(text, reply_markup=kb)
    else:
        await target.answer(text, reply_markup=kb)


@router.callback_query(F.data.regexp(r"^enemy:card:"))
async def admin_enemies_card(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    _, _, src, loc, enemy_id = callback.data.split(":", 4)
    await state.update_data(enemy_src=src, enemy_loc=loc, enemy_id=int(enemy_id))
    await _source_enemy_send(callback, src, loc, int(enemy_id))


@router.callback_query(F.data.regexp(r"^enemy:fld:"))
async def admin_enemies_field_pick(callback: CallbackQuery, state: FSMContext):
    """Запрос нового значения поля карточки."""
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    _, _, src, loc, enemy_id, field = callback.data.split(":", 5)
    if field not in ENEMY_FIELDS:
        return
    await state.update_data(enemy_src=src, enemy_loc=loc, enemy_id=int(enemy_id),
                            enemy_field=field)
    await state.set_state(AdminEnemy.field)
    await callback.message.answer(f"{ENEMY_FIELDS[field][0]} — {ENEMY_FIELDS[field][1]}",
                                  reply_markup=cancel_keyboard())


@router.message(AdminEnemy.field)
async def admin_enemies_field_value(message: Message, state: FSMContext):
    """Применяем введённое значение к полю врага."""
    data = await state.get_data()
    src, loc, enemy_id, field = (data.get('enemy_src'), data.get('enemy_loc'),
                                 data.get('enemy_id'), data.get('enemy_field'))
    enemy = await get_source_enemy(src, enemy_id) if src and enemy_id else None
    if not enemy:
        await state.clear()
        await message.answer("❌ Враг не найден. Открой карточку заново.")
        return
    if field not in ENEMY_FIELDS:
        await state.clear()
        await message.answer("❌ Поле не распознано. Открой карточку заново.")
        return
    kind = ENEMY_FIELDS[field][2]
    text = (message.text or "").strip()

    parsed = None
    if kind == "int":
        if text.isdigit():
            parsed = int(text)
    elif kind == "percent":
        if text.isdigit():
            parsed = int(text)
    elif kind == "dash":
        parsed = None if text in ("-", "—") else text[:400]

    valid = parsed is not None and (kind != "percent" or parsed <= 100)
    if valid and field in ("hp", "player_dmg_min", "player_dmg_max") and parsed < 1:
        valid = False
    if not valid:
        await message.answer(f"❌ Неверный формат.\n{ENEMY_FIELDS[field][1]}",
                             reply_markup=cancel_keyboard())
        return

    await update_source_enemy(src, enemy_id, **{field: parsed})
    await log_action(message.from_user.id, 'edit_enemy', None,
                     f"src={src} id={enemy_id} {field}={parsed}")
    await state.clear()
    await message.answer(f"✅ {enemy['name']}: {ENEMY_FIELDS[field][0]} = {parsed}.")
    await _source_enemy_send(message, src, loc, enemy_id, edit=False)


@router.callback_query(F.data.regexp(r"^enemy:photo:"))
async def admin_enemies_photo_pick(callback: CallbackQuery, state: FSMContext):
    """Загрузка фото врага (или «-» чтобы убрать)."""
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    _, _, src, loc, enemy_id = callback.data.split(":", 4)
    await state.update_data(enemy_src=src, enemy_loc=loc, enemy_id=int(enemy_id))
    await state.set_state(AdminEnemy.photo)
    await callback.message.answer("Отправь фото врага (Telegram-фото). Или «-», чтобы убрать фото.",
                                  reply_markup=cancel_keyboard())


@router.message(AdminEnemy.photo)
async def admin_enemies_photo_value(message: Message, state: FSMContext):
    data = await state.get_data()
    src, loc, enemy_id = data.get('enemy_src'), data.get('enemy_loc'), data.get('enemy_id')
    enemy = await get_source_enemy(src, enemy_id) if src and enemy_id else None
    if not enemy:
        await state.clear()
        await message.answer("❌ Враг не найден.")
        return
    if message.photo:
        file_id = message.photo[-1].file_id
    elif (message.text or "").strip() in ("-", "—"):
        file_id = None
    else:
        await message.answer("❌ Пришли фото или «-».")
        return
    await update_source_enemy(src, enemy_id, image=file_id)
    await log_action(message.from_user.id, 'edit_enemy', None,
                     f"src={src} id={enemy_id} image={'file_id' if file_id else 'cleared'}")
    await state.clear()
    await message.answer(f"✅ «{enemy['name']}»: фото {'обновлено' if file_id else 'убрано'}.")
    await _source_enemy_send(message, src, loc, enemy_id, edit=False)


@router.callback_query(F.data.regexp(r"^enemy:tog:"))
async def admin_enemies_toggle(callback: CallbackQuery, state: FSMContext):
    """Включить/выключить врага (выключенный не встречается в игре)."""
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    _, _, src, loc, enemy_id = callback.data.split(":", 4)
    enemy_id = int(enemy_id)
    enemy = await get_source_enemy(src, enemy_id)
    if not enemy:
        await callback.message.answer("❌ Враг не найден.")
        return
    new_enabled = 0 if enemy.get('enabled', 1) else 1
    await update_source_enemy(src, enemy_id, enabled=new_enabled)
    await log_action(callback.from_user.id, 'edit_enemy', None,
                     f"src={src} id={enemy_id} enabled={new_enabled}")
    await _source_enemy_send(callback, src, loc, enemy_id)


@router.callback_query(F.data.regexp(r"^enemy:del:"))
async def admin_enemies_delete(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    _, _, src, loc, enemy_id = callback.data.split(":", 4)
    enemy_id = int(enemy_id)
    enemy = await get_source_enemy(src, enemy_id)
    if not enemy:
        await callback.message.answer("❌ Враг не найден.")
        return
    await delete_source_enemy(src, enemy_id)
    await log_action(callback.from_user.id, 'edit_enemy', None,
                     f"src={src} id={enemy_id} deleted={enemy['name']}")
    lines = [f"🗑 Враг «{enemy['name']}» удалён из {_enemy_loc_title(src, loc)}."]
    rows = [[InlineKeyboardButton(text="🔙 К списку", callback_data=_enemy_list_cb(src, loc))]]
    await callback.message.edit_text("\n".join(lines),
                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))


# ---------- дропы врага леса/рыбалки ----------

@router.callback_query(F.data.regexp(r"^enemy:drops:"))
async def admin_enemies_drops(callback: CallbackQuery, state: FSMContext):
    """Экран дропов врага леса/рыбалки."""
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    _, _, src, loc, enemy_id = callback.data.split(":", 4)
    enemy_id = int(enemy_id)
    enemy = await get_source_enemy(src, enemy_id)
    if not enemy:
        await callback.message.answer("❌ Враг не найден.")
        return
    drops = await get_source_enemy_drops(src, enemy_id)
    lines = [f"💼 ДРОПЫ «{enemy['name']}»\n"]
    rows = []
    for idx, d in enumerate(drops):
        item = await get_item(d['item_id']) if d.get('item_id') else None
        name = item['name'] if item else (d.get('item') or '?')
        ch = d.get('chance', 0)
        ch_pct = f"{int(ch * 100)}%" if ch <= 1 else f"{int(ch)}%"
        qty = d.get('qty', 1)
        label = f"{name} — {ch_pct}" + (f" ×{qty}" if qty != 1 else "")
        lines.append(f"{idx + 1}. {label}")
        rows.append([InlineKeyboardButton(text=f"🗑 {idx + 1}. {label}",
                                          callback_data=f"enemy:dropdel:{src}:{loc}:{enemy_id}:{idx}")])
    if not drops:
        lines.append("Дропов пока нет.")
    lines.append("\nШансы независимые: каждый предмет проверяется отдельно, поэтому "
                 "за одну победу может выпасть сразу несколько. Пусто — когда не выпал ни один.")
    rows.append([InlineKeyboardButton(text="➕ Добавить предмет",
                                      callback_data=f"enemy:dropitem:{src}:{loc}:{enemy_id}:0")])
    rows.append([InlineKeyboardButton(text="🔙 В карточку врага",
                                      callback_data=f"enemy:card:{src}:{loc}:{enemy_id}")])
    await callback.message.edit_text("\n".join(lines),
                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))


@router.callback_query(F.data.regexp(r"^enemy:dropdel:"))
async def admin_enemies_drop_del(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    _, _, src, loc, enemy_id, idx = callback.data.split(":", 5)
    await remove_source_enemy_drop(src, int(enemy_id), int(idx))
    await log_action(callback.from_user.id, 'edit_enemy', None,
                     f"src={src} id={enemy_id} drop_removed={idx}")
    await admin_enemies_drops(callback, state)


@router.callback_query(F.data.regexp(r"^enemy:dropitem:"))
async def admin_enemies_drop_pick(callback: CallbackQuery, state: FSMContext):
    """Постраничный выбор предмета из игры для дропа."""
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    _, _, src, loc, enemy_id, page = callback.data.split(":", 5)
    page = int(page)
    enemy_id = int(enemy_id)
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
            callback_data=f"enemy:dropadd:{src}:{loc}:{enemy_id}:{it['id']}")])
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="◀️",
                                        callback_data=f"enemy:dropitem:{src}:{loc}:{enemy_id}:{page - 1}"))
    nav.append(InlineKeyboardButton(text=f"{page + 1}/{pages}", callback_data="noop"))
    if page < pages - 1:
        nav.append(InlineKeyboardButton(text="▶️",
                                        callback_data=f"enemy:dropitem:{src}:{loc}:{enemy_id}:{page + 1}"))
    rows.append(nav)
    rows.append([InlineKeyboardButton(text="🔙 К дропам",
                                      callback_data=f"enemy:drops:{src}:{loc}:{enemy_id}")])
    await callback.message.edit_text("Выбери предмет из игры для дропа:",
                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))


@router.callback_query(F.data.regexp(r"^enemy:dropadd:"))
async def admin_enemies_drop_add_pick(callback: CallbackQuery, state: FSMContext):
    """Выбран предмет — спрашиваем шанс."""
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    _, _, src, loc, enemy_id, item_id = callback.data.split(":", 5)
    await state.update_data(enemy_src=src, enemy_loc=loc, enemy_id=int(enemy_id),
                            drop_item_id=int(item_id))
    await state.set_state(AdminEnemy.drop_chance)
    await callback.message.answer("Введи шанс выпадения, % (1–100):",
                                  reply_markup=cancel_keyboard())


@router.message(AdminEnemy.drop_chance)
async def admin_enemies_drop_chance_value(message: Message, state: FSMContext):
    data = await state.get_data()
    src, loc, enemy_id = data.get('enemy_src'), data.get('enemy_loc'), data.get('enemy_id')
    item_id = data.get('drop_item_id')
    text = (message.text or "").strip()
    if not text.isdigit() or not 1 <= int(text) <= 100:
        await message.answer("❌ Нужно целое число 1–100.", reply_markup=cancel_keyboard())
        return
    await state.update_data(drop_chance=int(text))
    await state.set_state(AdminEnemy.drop_qty)
    await message.answer("Сколько выпадает? (целое ≥ 1, по умолчанию 1 — пришли 1):",
                         reply_markup=cancel_keyboard())


@router.message(AdminEnemy.drop_qty)
async def admin_enemies_drop_qty_value(message: Message, state: FSMContext):
    data = await state.get_data()
    src, loc, enemy_id = data.get('enemy_src'), data.get('enemy_loc'), data.get('enemy_id')
    item_id, chance = data.get('drop_item_id'), int(data.get('drop_chance') or 100)
    text = (message.text or "").strip()
    qty = int(text) if text.isdigit() and int(text) >= 1 else 1
    await add_source_enemy_drop(src, enemy_id, item_id, chance / 100.0, qty)
    await log_action(message.from_user.id, 'edit_enemy', None,
                     f"src={src} id={enemy_id} drop_item={item_id} chance={chance}% qty={qty}")
    await state.clear()
    item = await get_item(item_id)
    await message.answer(f"✅ Добавлен дроп: {item['name'] if item else item_id} — {chance}%"
                         + (f" ×{qty}" if qty != 1 else "") + ".")
    rows = [[InlineKeyboardButton(text="🔙 К дропам", callback_data=f"enemy:drops:{src}:{loc}:{enemy_id}")]]
    await message.answer("Что дальше?", reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))


# ---------- создание врага (лес/рыбалка) ----------

@router.callback_query(F.data.regexp(r"^enemy:new:"))
async def admin_enemies_new(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_locations"):
        return
    _, _, src, loc = callback.data.split(":", 3)
    await state.update_data(enemy_src=src, enemy_loc=loc)
    await state.set_state(AdminEnemy.c_name)
    await callback.message.answer("Введи название нового врага:", reply_markup=cancel_keyboard())


@router.message(AdminEnemy.c_name)
async def admin_enemies_new_name(message: Message, state: FSMContext):
    name = (message.text or "").strip()
    if not name:
        await message.answer("❌ Название не может быть пустым.")
        return
    await state.update_data(new_name=name[:64])
    await state.set_state(AdminEnemy.c_hp)
    await message.answer("Введи HP врага (целое ≥ 1):", reply_markup=cancel_keyboard())


@router.message(AdminEnemy.c_hp)
async def admin_enemies_new_hp(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    if not text.isdigit() or int(text) < 1:
        await message.answer("❌ Нужно целое число ≥ 1.")
        return
    await state.update_data(new_hp=int(text))
    await state.set_state(AdminEnemy.c_dmg)
    await message.answer("Введи урон врага в виде «мин-макс», например 5-9:", reply_markup=cancel_keyboard())


@router.message(AdminEnemy.c_dmg)
async def admin_enemies_new_dmg(message: Message, state: FSMContext):
    text = (message.text or "").replace("–", "-").replace("—", "-").strip()
    parts = text.split("-")
    try:
        dmg_min = int(parts[0])
        dmg_max = int(parts[1]) if len(parts) > 1 else dmg_min
    except (ValueError, IndexError):
        await message.answer("❌ Формат: «5-9» (два числа через дефис).")
        return
    if dmg_min < 0 or dmg_max < dmg_min:
        await message.answer("❌ Максимум должен быть не меньше минимума.")
        return
    await state.update_data(new_dmg_min=dmg_min, new_dmg_max=dmg_max)
    await state.set_state(AdminEnemy.c_dodge)
    await message.answer("Введи шанс уклонения, % (0–100):", reply_markup=cancel_keyboard())


@router.message(AdminEnemy.c_dodge)
async def admin_enemies_new_dodge(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    if not text.isdigit() or int(text) > 100:
        await message.answer("❌ Нужно целое 0–100.")
        return
    await state.update_data(new_dodge=int(text))
    await state.set_state(AdminEnemy.c_chance)
    await message.answer("Введи шанс встречи с врагом на попытку, % (например 5):",
                         reply_markup=cancel_keyboard())


@router.message(AdminEnemy.c_chance)
async def admin_enemies_new_chance(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    if not text.isdigit() or int(text) > 100:
        await message.answer("❌ Нужно целое 0–100.")
        return
    await state.update_data(new_chance=int(text))
    await state.set_state(AdminEnemy.c_loss_ap)
    await message.answer("Введи, сколько ОД теряет игрок при поражении (целое ≥ 0):",
                         reply_markup=cancel_keyboard())


@router.message(AdminEnemy.c_loss_ap)
async def admin_enemies_new_done(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    if not text.isdigit():
        await message.answer("❌ Нужно целое ≥ 0.")
        return
    data = await state.get_data()
    src, loc = data.get('enemy_src'), data.get('enemy_loc')
    enemy_id = await add_source_enemy(
        src, spot=(loc if src == ENEMY_SRC_FISHING else 'forest'),
        name=data.get('new_name'), hp=data.get('new_hp'),
        dmg_min=data.get('new_dmg_min'), dmg_max=data.get('new_dmg_max'),
        dodge=data.get('new_dodge'), player_dmg_min=5, player_dmg_max=10,
        loss_ap=int(text), chance=float(data.get('new_chance') or 0),
        pity_target=0, reward_nm=0, drops=[], description=None,
        photo_key=None, enabled=1)
    await log_action(message.from_user.id, 'add_enemy', None, f"src={src} id={enemy_id}")
    await state.clear()
    await message.answer(f"✅ Враг «{data.get('new_name')}» добавлен. Настрой его дропы и фото.")
    await _source_enemy_send(message, src, loc, enemy_id, edit=False)