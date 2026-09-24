import os
import random
import json
import asyncio
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from database.db import (
    get_all_dungeons, get_dungeon, get_dungeon_rooms_map, get_floor_enemies,
    get_dungeon_enemies,
    start_dungeon_run, get_active_run, update_run_hp, advance_room, advance_floor,
    end_run, add_run_item, add_run_nordmarks,
    get_run_items, clear_run_items, get_user, add_nordmarks, remove_nordmarks, remove_ap, get_db,
    get_player_weapon_damage, get_user_potions, get_item_by_name, remove_inventory_item,
    get_equipped_weapon,
    get_user_contract_count, get_player_dodge, add_inventory_item,
    get_inventory_item, clear_equipment_slot,
    transfer_run_items_to_inventory, get_equipment_slot_items, log_activity,
    get_award_bonus, get_player_armor_with_bonus,
    get_inventory, get_equipment, set_equipment_slot, get_item,
    item_fits_slot, EQUIPMENT_SLOT_LABELS, SMOKE_ITEM_NAME,
    update_user, get_fish_catches, add_fish_catch,
    get_water_fish_pool, get_water_fish_photo_by_name, get_water_fish_kind,
)
from utils.combat import (
    calculate_attack, calculate_enemy_damage, roll_dodge,
    escape_chance, calculate_escape_damage, room_type_roll, resource_amount,
    _hp_bar,
)
from utils.helpers import (
    time_of_day_key, edit_or_replace, resolve_image,
    plural_nordmark, fish_weight_tier, fish_sell_price, item_local_photo,
)
from bot.handlers.fishing import (
    WORMS_NAME, SPIDER_LEG_NAME, COMBINED_BAIT_NAME,
    BAIT_BONUS, ROD_BONUS_PER_RANK,
    _rod_for, _resolve_bait, _bait_label, _bait_line,
    _catch_chance, _roll_fish_weight, _pick_junk,
    junk_hint, junk_photo,
    FISHING_CASTING,
)
from utils.notify import notify, player_display
from config import (
    DUNGEON_HEAL_SOFT_LIMIT, DUNGEON_HEAL_HARD_LIMIT,
    DUNGEON_HEAL_SOFT_MULT, DUNGEON_HEAL_HARD_MULT,
    DUNGEON_SMOKE_MAX,
    FISH_AP_COST,
)


def heal_limit_mult(uses: int) -> float:
    """Множитель эффективности лечения: после 6-7 применений — -1/3, после 10 — -1/2."""
    if uses >= DUNGEON_HEAL_HARD_LIMIT:
        return DUNGEON_HEAL_HARD_MULT
    if uses >= DUNGEON_HEAL_SOFT_LIMIT:
        return DUNGEON_HEAL_SOFT_MULT
    return 1.0


def heal_limit_note(uses: int) -> str:
    if uses >= DUNGEON_HEAL_HARD_LIMIT:
        return f"\n⚠️ Лекарства почти не действуют: эффективность −1/2 (применено: {uses})."
    if uses >= DUNGEON_HEAL_SOFT_LIMIT:
        return f"\n⚠️ Лекарства действуют хуже: эффективность −1/3 (применено: {uses})."
    return ""


class DungeonFSM(StatesGroup):
    in_dungeon = State()
    in_combat = State()
    in_boss = State()
    confirm_enter = State()
    in_reservoir = State()


router = Router()


async def _log_stale(callback, context: str):
    """Записать факт нажатия устаревшей кнопки в лог активности (для разбора проблем)."""
    try:
        await log_activity(callback.from_user.id, "stale_button", context)
    except Exception:
        pass


# Кровотечение: урон каждый ход, спадает через BLEED_TICKS_MAX ходов.
BLEED_TICKS_MAX = 3
# Обморожение: лечение ×FROSTBITE_HEAL_MULT, само проходит через FROSTBITE_TURNS
# ходов игрока либо сразу от напитка с cure_frostbite.
FROSTBITE_TURNS = 4
FROSTBITE_HEAL_MULT = 0.5
FROSTBITE_CURE_HINT = "Снять: «Огненная вода (водка)» или «Горячий ягодный морс»."

# Особые эффекты оружия (DoT на врага, v0.14.3): накладываются при попадании
# с шансом weapon_effect_chance, бьют врага weapon_effect_dmg каждый ход игрока
# и сами спадают через WEAPON_DOT_TICKS ходов.
WEAPON_DOT_TICKS = 3
# «Оглушение» (v0.15.18): при срабатывании шанса враг дезориентирован — на
# WEAPON_STUN_TICKS ходов его точность падает: chance промаха = weapon_effect_dmg %.
WEAPON_STUN_TICKS = 2
WEAPON_EFFECT_LABELS = {
    "poison": "отравление",
    "bleed": "кровотечение",
    "frostbite": "обморожение",
    "stun": "оглушение",
}
WEAPON_EFFECT_EMOJI = {
    "poison": "☠️",
    "bleed": "🩸",
    "frostbite": "🧊",
    "stun": "💫",
}
WEAPON_EFFECT_ATTACK_LINE = {
    "poison": "Ты отравил врага — яд въедается в рану",
    "bleed": "Ты глубоко ранил врага — он истекает кровью",
    "frostbite": "Ты оковал врага холодом — мороз сковывает его тело",
    "stun": "Ты оглушил врага — его следующие удары неточны",
}

# Рыба подземного водохранилища (после победы над Крысиным капитаном): веса.
RESERVOIR_AP_COST = FISH_AP_COST
RESERVOIR_FISH_POOL = (
    ("Мерцающий сом", 62),
    ("Искрящийся угорь", 33),
    ("Светящаяся форель", 5),
)
RESERVOIR_EMOJI = {
    "Мерцающий сом": "🐟",
    "Искрящийся угорь": "🐠",
    "Светящаяся форель": "✨",
}
# Картинка водохранилища: assets/img/city/reservoir_{tod}.jpg (day/night/…).
RESERVOIR_PHOTO = "city/reservoir"


def _reservoir_photo() -> str:
    """Фон водохранилища; если картинки нет — падаем на озеро."""
    path = resolve_image(RESERVOIR_PHOTO)
    if not os.path.isfile(path):
        path = resolve_image("city/lake")
    return path


async def _pick_reservoir_fish() -> str:
    """Случайная рыба водохранилища по весам из БД (water_fish).

    Светятся день и ночь одинаково, поэтому берём day_weight.
    Откат на константу RESERVOIR_FISH_POOL, если таблица пуста.
    """
    pool_rows = await get_water_fish_pool("reservoir")
    pool = [(r['name'], r['day_weight']) for r in pool_rows if r['day_weight'] > 0]
    if not pool:
        pool = list(RESERVOIR_FISH_POOL)
    total = sum(w for _, w in pool)
    r = random.random() * total
    acc = 0
    for name, weight in pool:
        acc += weight
        if r < acc:
            return name
    return pool[-1][0]


async def dungeon_current_step(state: FSMContext) -> int:
    """Текущий шаг подземелья (для защиты от повторного нажатия старых кнопок)."""
    data = await state.get_data()
    return int(data.get('dungeon_step', 0) or 0)


async def dungeon_new_step(state: FSMContext) -> int:
    """Выдаёт следующий шаг и сохраняет его в FSM (новая кнопка перебивает старые)."""
    step = await dungeon_current_step(state) + 1
    await state.update_data(dungeon_step=step)
    return step


async def rooms_total_now(run) -> int:
    """Число обычных комнат до босса на текущем этаже забега."""
    rooms_map = await get_dungeon_rooms_map(run['dungeon_id'])
    if not rooms_map:
        return 10
    floor = run['floor']
    if 1 <= floor <= len(rooms_map):
        return rooms_map[floor - 1]
    return rooms_map[0]


def status_lines(data) -> list:
    """Строки активных статусов боя (яд, кровотечение, обморожение)."""
    lines = []
    if data.get('active_poison'):
        lines.append(f"☠️ Ты отравлен! Яд: −{data['active_poison']} HP каждый ход")
    if data.get('active_bleed'):
        ticks = int(data.get('bleed_ticks', 0) or 0)
        rem = f" (спадёт через {ticks} х.)" if ticks else " (спадёт скоро)"
        lines.append(f"🩸 Кровотечение: −{data['active_bleed']} HP каждый ход{rem}")
    if data.get('active_frostbite'):
        lines.append(f"🧊 Обморожение: лечение −50%. {FROSTBITE_CURE_HINT}")
    return lines


def dungeon_main_keyboard(step: int = 0):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏃 Продолжить путь", callback_data=f"dungeon:continue:{step}")],
        [InlineKeyboardButton(text="🚪 Выйти из подземелья", callback_data="dungeon:exit")],
    ])


def _slot_button_label(row):
    qty = int(row.get('quantity') or 0)
    suffix = f" x{qty}" if qty > 0 else ""
    if row['name'] == SMOKE_ITEM_NAME:
        return f"💨 Дымовая шашка{suffix}"
    if row['cure_poison']:
        return f"⚗️ Антидот{suffix}"
    if row.get('cure_frostbite'):
        return f"🧊 {row['name']}{suffix}"
    if row['heal'] > 0:
        return f"💊 {row['name']}{suffix}"
    return f"🧪 {row['name']}{suffix}"


def dungeon_combat_keyboard(enemy_id: int, slot_items: list = None, step: int = 0):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    buttons = [
        [InlineKeyboardButton(text="🗡️ Атаковать", callback_data=f"dungeon:attack:{enemy_id}:{step}")],
    ]
    for slot, row in (slot_items or []):
        buttons.append([InlineKeyboardButton(text=_slot_button_label(row), callback_data=f"dungeon:use_slot:{slot}:{step}")])
    buttons.append([InlineKeyboardButton(text="🏃 Попытаться убежать", callback_data=f"dungeon:escape:{enemy_id}:{step}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def dungeon_boss_keyboard(boss_id: int, slot_items: list = None, step: int = 0):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    buttons = [
        [InlineKeyboardButton(text="🗡️ Атаковать", callback_data=f"dungeon:attack:{boss_id}:{step}")],
    ]
    for slot, row in (slot_items or []):
        buttons.append([InlineKeyboardButton(text=_slot_button_label(row), callback_data=f"dungeon:use_slot:{slot}:{step}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def _combat_slot_items(user_id: int, is_boss: bool = False):
    """Слоты расходников для боевой клавиатуры.

    Дымовая шашка показывается только в бою с обычными врагами (не боссами):
    от боссов убежать нельзя, поэтому кнопка шашки там не нужна.
    """
    return await get_equipment_slot_items(user_id, include_smoke=not is_boss)


def post_captain_keyboard(step: int = 0):
    """Выбор после победы над Крысиным капитаном: водохранилище или дальше."""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎣 Порыбачить в водохранилище", callback_data=f"resv:enter:{step}")],
        [InlineKeyboardButton(text="⚔️ Продолжить вглубь (Этаж 2)", callback_data=f"resv:deeper:{step}")],
        [InlineKeyboardButton(text="🚪 Выйти из подземелья", callback_data="dungeon:exit")],
    ])


def reservoir_keyboard(step: int = 0):
    """Меню подземного водохранилища: рыбалка, наживка, снаряжение, дальше, выход."""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"🎣 Забросить удочку (−{RESERVOIR_AP_COST} ОД)", callback_data=f"resv:cast:{step}")],
        [InlineKeyboardButton(text="🪱 Наживка", callback_data=f"resv:bait:{step}")],
        [InlineKeyboardButton(text="🎒 Снаряжение", callback_data=f"resv:eq:{step}")],
        [InlineKeyboardButton(text="⚔️ Продолжить вглубь (Этаж 2)", callback_data=f"resv:deeper:{step}")],
        [InlineKeyboardButton(text="🚪 Выйти из подземелья", callback_data="dungeon:exit")],
    ])


def _reservoir_bait_markup(chosen: str, worms_qty: int, spider_qty: int, combined_qty: int = 0,
                           step: int = 0):
    """Выбор наживки для водохранилища (аналог озера, но в подземелье)."""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    def row(label: str, value: str):
        return label + (" ✓" if chosen == value else "")

    rows = []
    if worms_qty:
        rows.append([InlineKeyboardButton(
            text=row(f"🐛 {WORMS_NAME} x{worms_qty} (+{BAIT_BONUS[WORMS_NAME]}%)", "worms"),
            callback_data=f"resv:bait:set:{step}:worms")])
    if spider_qty:
        rows.append([InlineKeyboardButton(
            text=row(f"🕷 {SPIDER_LEG_NAME} x{spider_qty} (+{BAIT_BONUS[SPIDER_LEG_NAME]}%)", "spider"),
            callback_data=f"resv:bait:set:{step}:spider")])
    if combined_qty:
        rows.append([InlineKeyboardButton(
            text=row(f"🪤 {COMBINED_BAIT_NAME} x{combined_qty} (+{BAIT_BONUS[COMBINED_BAIT_NAME]}%)", "combined"),
            callback_data=f"resv:bait:set:{step}:combined")])
    rows.append([InlineKeyboardButton(
        text=row("🚫 Без наживки", "none"),
        callback_data=f"resv:bait:set:{step}:none")])
    rows.append([InlineKeyboardButton(text="🔙 В водохранилище", callback_data=f"resv:menu:{step}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _reservoir_result_markup(step: int = 0):
    """Кнопки после заброса в водохранилище."""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎣 Ещё раз", callback_data=f"resv:cast:{step}")],
        [InlineKeyboardButton(text="🪱 Наживка", callback_data=f"resv:bait:{step}")],
        [InlineKeyboardButton(text="⚔️ Продолжить вглубь (Этаж 2)", callback_data=f"resv:deeper:{step}")],
        [InlineKeyboardButton(text="🚪 Выйти из подземелья", callback_data="dungeon:exit")],
    ])


def dungeon_start_keyboard():
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏰 К списку контрактов", callback_data="contracts:list")],
        [InlineKeyboardButton(text="🏠 В меню города", callback_data="city:menu")],
    ])


def contract_missing_keyboard():
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏰 К списку контрактов", callback_data="contracts:list")],
        [InlineKeyboardButton(text="🏠 В меню города", callback_data="city:menu")],
    ])


async def show_contracts(msg, user_id: int, state: FSMContext | None = None):
    """«Доска контрактов» — список доступных подземелий (каждое = контракт).
    Используется из contracts:list и входа в локацию «Доска контрактов».
    msg — Message или CallbackQuery.message."""
    active = await get_active_run(user_id)

    if active:
        await resume_dungeon(msg, active, user_id, state)
        return

    dungeons = await get_all_dungeons(training=False)
    if not dungeons:
        await msg.answer("❌ Контрактов пока нет.")
        return

    contracts = await get_user_contract_count(user_id)

    text = (
        "📜 ДОСКА КОНТРАКТОВ ОТ ШТАБА ВС\n\n"
        "Штаб вывешивает контракты на зачистку подземелий. "
        "Выбери контракт, чтобы посмотреть условия.\n\n"
    )

    buttons = []
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    for i, d in enumerate(dungeons, 1):
        rooms = await get_dungeon_rooms_map(d['id'])
        floors_n = len(rooms) or int(d.get('floors_count') or 1)
        text += (
            f"{i}. ⚔️ {d['name']}\n"
            f"    Этажей: {floors_n}, комнат/этаж: {rooms[0] if rooms else d.get('rooms_per_floor') or '—'}\n"
        )
        buttons.append([InlineKeyboardButton(
            text=f"📜 {d['name']} — условия контракта",
            callback_data=f"contract:pick:{d['id']}"
        )])

    text += (
        f"\n🎫 Контрактов на зачистку: {contracts}\n"
        f"(покупаются в магазине, доступно Ветеранам).\n"
        f"Вход по контракту списывает его и 30 ⚡ ОД."
    )
    buttons.append([InlineKeyboardButton(text="🏠 В меню города", callback_data="city:menu")])

    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    photo = dungeon_entrance_photo(dungeons[0])
    if photo:
        try:
            await msg.answer_photo(photo=photo, caption=text, reply_markup=markup)
        except Exception:
            await msg.answer(text, reply_markup=markup)
    else:
        await msg.answer(text, reply_markup=markup)


@router.callback_query(F.data == "contracts:list")
async def contracts_list(callback: CallbackQuery, state: FSMContext):
    """«📜 Доска контрактов» — список доступных подземелий (каждое = контракт)."""
    await callback.answer()
    await show_contracts(callback.message, callback.from_user.id, state)


async def _contract_difficulty(dng) -> int:
    """Уровень сложности 1–5 по суммарным статам врагов данжа."""
    enemies = await get_dungeon_enemies(dng['id'])
    pool = sum((e['hp'] or 0) for e in enemies) + 10 * sum((e['attack'] or 0) for e in enemies)
    if pool < 300:
        return 1
    if pool < 600:
        return 2
    if pool < 1000:
        return 3
    if pool < 1600:
        return 4
    return 5


async def _contract_reward_nm(dng) -> int:
    """Суммарная награда (НМ) за зачистку: реварды всех врагов данжа."""
    enemies = await get_dungeon_enemies(dng['id'])
    return sum((e['reward_nm'] or 0) for e in enemies)


@router.callback_query(F.data.startswith("contract:pick:"))
async def contract_pick(callback: CallbackQuery, state: FSMContext):
    """Карточка выбранного контракта: условия, награда, стоимость входа."""
    await callback.answer()
    try:
        dungeon_id = int(callback.data.split(":", 2)[2])
    except (IndexError, ValueError):
        return
    dungeon = await get_dungeon(dungeon_id)
    if not dungeon:
        await callback.message.answer("❌ Контракт не найден.")
        return

    user_id = callback.from_user.id
    contracts = await get_user_contract_count(user_id)
    user = await get_user(user_id)

    rooms = await get_dungeon_rooms_map(dungeon_id)
    floors_n = len(rooms) or int(dungeon.get('floors_count') or 1)
    difficulty = await _contract_difficulty(dungeon)
    reward_nm = await _contract_reward_nm(dungeon)

    stars = "★" * difficulty + "☆" * (5 - difficulty)
    text = (
        f"📜 КОНТРАКТ ОТ ШТАБА ВС\n\n"
        f"⚔️ {dungeon['name']}\n"
        f"{dungeon['description'] or ''}\n\n"
        f"🏚 Этажей: {floors_n} (комнат/этаж: {rooms[0] if rooms else dungeon.get('rooms_per_floor') or '—'})\n"
        f"☠ Сложность: {stars}\n"
        f"💰 Награда за зачистку: до {reward_nm} НМ с врагов\n\n"
        f"🎫 Стоимость входа:\n"
        f"   • 1 «Контракт на зачистку» (у тебя: {contracts})\n"
        f"   • 30 ⚡ ОД (у тебя: {user['ap'] if user else 0})\n\n"
        f"Ресурсы списываются сразу при входе, даже если ты выйдешь из подземелья."
    )

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎫 Войти (1 контракт)", callback_data=f"contract:enter:{dungeon_id}")],
        [InlineKeyboardButton(text="↩️ К списку контрактов", callback_data="contracts:list")],
        [InlineKeyboardButton(text="🏠 В меню города", callback_data="city:menu")],
    ])
    photo = dungeon_entrance_photo(dungeon)
    if photo:
        try:
            await callback.message.answer_photo(photo=photo, caption=text, reply_markup=markup)
        except Exception:
            await callback.message.answer(text, reply_markup=markup)
    else:
        await callback.message.answer(text, reply_markup=markup)


@router.callback_query(F.data.regexp(r"^contract:enter:\d+$"))
async def contract_enter(callback: CallbackQuery, state: FSMContext):
    """Подтверждение входа по выбранному контракту."""
    await callback.answer()
    try:
        dungeon_id = int(callback.data.split(":", 2)[2])
    except (IndexError, ValueError):
        return
    dungeon = await get_dungeon(dungeon_id)
    if not dungeon:
        return

    user_id = callback.from_user.id
    contracts = await get_user_contract_count(user_id)
    if contracts <= 0:
        await callback.message.answer(
            "❌ У тебя нет «Контракта на зачистку».\n\n"
            "Купи его в магазине (Особое) — доступно Ветеранам. Контракт даёт право на один вход.",
            reply_markup=contract_missing_keyboard()
        )
        return

    user = await get_user(user_id)
    if user['ap'] < 30:
        await callback.message.answer(
            f"❌ Недостаточно очков действий для входа.\n"
            f"Нужно 30 AP за попытку, у тебя {user['ap']} AP.\n\n"
            f"⚡ Очки действий восстанавливаются раз в сутки.",
        )
        return

    await state.update_data(dungeon_id=dungeon['id'])
    await state.set_state(DungeonFSM.confirm_enter)
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    await callback.message.answer(
        f"⚠️ ПО КОНТРАКТУ «{dungeon['name']}» БУДУТ СПИСАНЫ:\n\n"
        f"🎫 1 «Контракт на зачистку» (у тебя: {contracts})\n"
        f"⚡ 30 очков действий (у тебя: {user['ap']})\n\n"
        f"Эти ресурсы потратятся сразу, даже если ты выйдешь из подземелья. Продолжить?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Да, войти", callback_data=f"contract:enter:confirm:{dungeon_id}")],
            [InlineKeyboardButton(text="↩️ Отмена", callback_data=f"contract:pick:{dungeon_id}")],
        ])
    )


@router.callback_query(F.data.startswith("contract:enter:confirm:"))
async def contract_enter_confirm(callback: CallbackQuery, state: FSMContext):
    """Списание контракта + ОД и вход в выбранное подземелье."""
    await callback.answer()
    try:
        dungeon_id = int(callback.data.split(":", 3)[3])
    except (IndexError, ValueError):
        return
    user_id = callback.from_user.id
    dungeon = await get_dungeon(dungeon_id)
    if not dungeon:
        await state.clear()
        return

    contracts = await get_user_contract_count(user_id)
    if contracts <= 0:
        await state.clear()
        await callback.message.answer(
            "❌ У тебя нет «Контракта на зачистку».",
            reply_markup=contract_missing_keyboard()
        )
        return

    user = await get_user(user_id)
    if user['ap'] < 30:
        await state.clear()
        await callback.message.answer(
            f"❌ Недостаточно очков действий. Нужно 30 AP, у тебя {user['ap']} AP."
        )
        return

    contract = await get_item_by_name("Контракт на зачистку")
    ok = await remove_inventory_item(user_id, contract['id'], 1)
    if not ok:
        await state.clear()
        await callback.message.answer("❌ Не удалось списать контракт.")
        return

    ok = await remove_ap(user_id, 30, reason="вход в подземелье")
    if not ok:
        await state.clear()
        await callback.message.answer("❌ Не удалось списать очки действий.")
        return

    await start_dungeon_run(user_id, dungeon['id'])
    run = await get_active_run(user_id)
    await state.update_data(dungeon_heal_uses=0, dungeon_smoke_uses=0)
    await log_activity(user_id, "dungeon_enter", f"Контракт «{dungeon['name']}»")

    rooms0 = await rooms_total_now(run)
    await callback.message.answer(
        f"🎫 Контракт использован! ⚡ −30 AP за вход\n"
        f"🏰 {dungeon['name']}\n"
        f"Этаж 1 | Комната 0/{rooms0}\n"
        f"❤️ {_hp_bar(run['hp'], run['hp_max'])}\n\n"
        f"Ты входишь в подземелье...",
    )
    await state.set_state(DungeonFSM.in_dungeon)
    await show_room(callback.message, run, user_id, state)


# Совместимость: старые кнопки «Подземелье» переадресуются на список контрактов.
@router.callback_query(F.data == "city:dungeon")
async def dungeon_entry_legacy(callback: CallbackQuery, state: FSMContext):
    await contracts_list(callback, state)


async def answer_enemy_photo(where, enemy, text, reply_markup=None):
    """Отправляет сообщение с фото врага; если файла нет — падает на текстовое."""
    image = enemy['image'] if 'image' in enemy.keys() and enemy['image'] else None
    if image:
        if os.path.isfile(image):
            return await where.answer_photo(photo=FSInputFile(image), caption=text, reply_markup=reply_markup)
        # Админ мог прислать фото ботом — сохраняем Telegram file_id.
        return await where.answer_photo(photo=image, caption=text, reply_markup=reply_markup)
    return await where.answer(text, reply_markup=reply_markup)


def dungeon_entrance_photo(dng):
    """Входная картинка подземелья по времени суток: file_id или None.

    Приоритет как у локаций: photo_{tod} → dawn → day → sunset → night.
    """
    keys = dng.keys()
    tod = time_of_day_key()
    for slot in (f"photo_{tod}", "photo_dawn", "photo_day", "photo_sunset", "photo_night"):
        if slot in keys and dng[slot]:
            return dng[slot]
    return None


async def count_potions(user_id: int) -> int:
    potions = await get_user_potions(user_id)
    return sum(p['quantity'] for p in potions)


async def roll_enemy_drops(run_id: int, enemy) -> list:
    """Бросает дропы врага, добавляет в инвентарь забега. Возвращает [(название, кол-во)]."""
    dropped = []
    drops = []
    if 'drops' in enemy.keys() and enemy['drops']:
        try:
            drops = json.loads(enemy['drops'])
        except (json.JSONDecodeError, TypeError):
            drops = []
    for d in drops:
        if random.random() < d.get('chance', 0):
            item = None
            if d.get('item_id'):
                item = await get_item(int(d['item_id']))
            if not item:
                item = await get_item_by_name(d.get('item', '') or '')
            if item:
                qty = max(1, int(d.get('qty', 1)))
                await add_run_item(run_id, item['id'], qty)
                dropped.append((item['name'], qty))
    return dropped


async def post_captain_menu(where, run, state: FSMContext):
    """Экран после победы над Крысиным капитаном: водохранилище или этаж 2."""
    loot_nm = run['loot_nm'] or 0
    text = (
        "🏆 КРЫСИНЫЙ КАПИТАН ПОВЕРЖЁН!\n"
        "💀 «Генерал» в кастрюлевом шлеме с жалким писком отползает в темноту, "
        "и на этаже становится тихо.\n\n"
        "Впереди развилка:\n"
        "🎣 Боковое ответвление ведёт к подземному водохранилищу — там слышен плеск "
        "невидимой рыбы. Говорят, в тёмной воде водится рыба, которой больше нигде нет.\n"
        "⚔️ Вниз уходит ход в сердце подвала, где ждёт сам Король крыс.\n"
    )
    if loot_nm > 0:
        text += f"\n💰 В лут с 1-го этажа накоплено: {loot_nm} НМ (заберёшь при выходе)."
    text += "\n\nМожно порыбачить, а потом продолжить путь на 2-й этаж."
    step = await dungeon_new_step(state)
    await state.set_state(DungeonFSM.in_dungeon)
    await where.answer(text, reply_markup=post_captain_keyboard(step))


async def _resv_answer(where, text, markup=None, photo=None, photo_id=None):
    """Отправка/редактирование в водохранилище: фото (файл или file_id), иначе текст."""
    if photo or photo_id:
        media = photo_id or FSInputFile(photo)
        if getattr(where, 'photo', None):
            try:
                await where.edit_caption(caption=text, reply_markup=markup)
                return
            except Exception:
                pass
        try:
            await where.delete()
        except Exception:
            pass
        # Из text-сообщения в фото: обычный edit невозможен — отправляем новое.
        try:
            await where.answer_photo(photo=media, caption=text, reply_markup=markup)
        except Exception:
            await where.edit_text(text, reply_markup=markup)
        return
    await edit_or_replace(where, text, markup)


async def show_reservoir(where, user_id: int, state: FSMContext):
    """Меню подземного водохранилища (рыбалка как на озере: наживка, удочка, улов)."""
    run = await get_active_run(user_id)
    step = await dungeon_new_step(state)
    text = (
        "🌊 ПОДЗЕМНОЕ ВОДОХРАНИЛИЩЕ\n\n"
        "Тёмная вода мерцает холодным светом. Тишина такая, что слышно собственные шаги. "
        "Иногда по воде пробегает рябь — там кто-то есть, и рыба тут непугливая.\n\n"
        "🐟 В глубине водится редкий улов, которого больше нигде не найти. "
        "Что именно попадётся на крючок — заранее не скажешь.\n"
    )
    user = await get_user(user_id) or {}
    chosen = (user.get('fishing_bait') or "").strip()
    rod = await _rod_for(user_id)
    if rod:
        rank = rod['rarity'] or 1
        bait_label = await _bait_label(user_id, chosen)
        bait_name, _ = await _resolve_bait(user_id, chosen)
        chance = _catch_chance(rod, bait_name, (await get_award_bonus(user_id))['fishing'])
        text += (
            f"\n🎣 Удочка: {rod['name']} (ранг {rank}, +{rank * ROD_BONUS_PER_RANK}%)\n"
            f"🪱 Наживка: {bait_label}\n"
        )
        if bait_name:
            text += f"⚡ Шанс улова: {chance}%\n"
        else:
            text += (f"⚡ Без наживки рыба НЕ клюёт: со дна только мусор "
                     f"{await junk_hint('reservoir')}.\n")
    else:
        text += "\n🎣 Удочка: нет — купи «Удочка из орешника» (магазин → Рыбалка)\n"

    ap = user.get('ap', 0) or 0
    ap_max = user.get('ap_max', ap) or ap
    text += f"\n⚡ ОД: {ap}/{ap_max}"
    if ap < RESERVOIR_AP_COST:
        text += f" — не хватит на заброс ({RESERVOIR_AP_COST} ОД)"

    caught = await get_fish_catches(user_id)
    names = {r['name'] for r in await get_water_fish_pool("reservoir")}
    if not names:
        names = {f[0] for f in RESERVOIR_FISH_POOL}
    resv_caught = [c for c in caught if c['name'] in names]
    if resv_caught:
        counts = {}
        for c in resv_caught:
            counts[c['name']] = counts.get(c['name'], 0) + 1
        text += "\n\n🎒 Поймано тут (Улов):\n" + "\n".join(f"• {n} x{k}" for n, k in counts.items())

    text += "\n\nЗдесь можно спокойно поменять слоты расходников — боя в этом зале нет."

    photo = _reservoir_photo()
    if photo and not os.path.isfile(photo):
        photo = None
    await _resv_answer(where, text, reservoir_keyboard(step), photo=photo)


async def resume_dungeon(where, run, user_id: int, state: FSMContext):
    """Возврат в активный забег: водохранилище, пост-капитанский выбор или комната."""
    if await state.get_state() == DungeonFSM.in_reservoir.state:
        await show_reservoir(where, user_id, state)
        return
    data = await state.get_data()
    if run['floor'] == 1 and run['room_number'] >= await rooms_total_now(run) \
            and data.get('captain_defeated'):
        await post_captain_menu(where, run, state)
        return
    await show_room(where, run, user_id, state)


@router.callback_query(F.data.startswith("dungeon:continue:"))
async def dungeon_continue(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    user_id = callback.from_user.id
    run = await get_active_run(user_id)
    if not run:
        await callback.message.answer("❌ Активное подземелье не найдено.")
        await state.clear()
        return

    parts = callback.data.split(":")
    if len(parts) < 3 or int(parts[2]) != await dungeon_current_step(state):
        await _log_stale(callback, "данж: устаревшая кнопка продолжения")
        await callback.message.answer("⚠️ Это устаревшая кнопка. Открой подземелье заново и продолжай с последнего сообщения.")
        return

    if user_id in FISHING_CASTING:
        await callback.answer("⏳ Сначала дождись улова из водохранилища!", show_alert=True)
        return

    if await state.get_state() == DungeonFSM.in_reservoir.state:
        await show_reservoir(callback.message, user_id, state)
        return

    data = await state.get_data()
    rooms_total = await rooms_total_now(run)
    if run['room_number'] >= rooms_total:
        if run['floor'] == 1 and data.get('captain_defeated'):
            await post_captain_menu(callback.message, run, state)
        else:
            await show_boss(callback.message, run, user_id, state)
        return

    await advance_room(run['id'])
    run = await get_active_run(user_id)
    await show_room(callback.message, run, user_id, state)


async def show_room(message, run, user_id, state: FSMContext):
    dungeon = await get_dungeon(run['dungeon_id'])
    room_type = room_type_roll()
    hp_text = _hp_bar(run['hp'], run['hp_max'])
    slot_items = await _combat_slot_items(user_id)
    sdata = await state.get_data()
    poison = sdata.get('active_poison')
    heal_uses = int(sdata.get('dungeon_heal_uses', 0) or 0)
    step = await dungeon_new_step(state)
    rooms_total = await rooms_total_now(run)

    heal_line = ""
    if heal_uses >= DUNGEON_HEAL_SOFT_LIMIT:
        mult = heal_limit_mult(heal_uses)
        heal_line = f"💊 Лекарства: {heal_uses} применений (×{mult:.0%})\n"

    room_header = f"Этаж {run['floor']} | Комната {run['room_number']}/{rooms_total}"
    status_text = status_lines(sdata)
    status_text.append(heal_line.strip())
    status_block = "\n".join(s for s in status_text if s)
    if status_block:
        status_block += "\n"

    if room_type == "enemy":
        enemies = await get_floor_enemies(run['dungeon_id'], run['floor'])
        non_boss = [e for e in enemies if not e['is_boss']]
        enemy = random.choice(non_boss) if non_boss else random.choice(enemies)

        await state.update_data(current_enemy_id=enemy['id'], current_enemy_hp=enemy['hp'],
                                enemy_effect=None, enemy_effect_dmg=0, enemy_effect_ticks=0)

        text = (
            f"🏰 {dungeon['name']}\n"
            f"{room_header}\n"
            f"❤️ {hp_text}\n"
            f"{status_block}"
            f"⚠️ Ты входишь в комнату и видишь врага!\n"
            f"👾 {enemy['name']} (HP: {enemy['hp']}, АТК: {enemy['attack']}, УКЛ: {enemy['dodge'] if 'dodge' in enemy.keys() else 0}%)\n\n"
            f"{enemy['description'] if 'description' in enemy.keys() and enemy['description'] else ''}\n"
            f"Что делаешь?"
        )
        await answer_enemy_photo(message, enemy, text, reply_markup=dungeon_combat_keyboard(enemy['id'], slot_items, step))

    elif room_type == "resource":
        nm = resource_amount(run['floor'])
        await add_run_nordmarks(run['id'], nm)

        text = (
            f"🏰 {dungeon['name']}\n"
            f"{room_header}\n"
            f"❤️ {hp_text}\n"
            f"{status_block}"
            f"📦 Ты нашёл хранилище с припасами!\n"
            f"+{nm} Нордмарок (заберёшь при выходе)\n\n"
            f"Нажми «Продолжить путь» чтобы идти дальше."
        )
        await message.answer(text, reply_markup=dungeon_main_keyboard(step))

    else:
        text = (
            f"🏰 {dungeon['name']}\n"
            f"{room_header}\n"
            f"❤️ {hp_text}\n"
            f"{status_block}"
            f"🪨 Комната пуста. Здесь ничего нет.\n\n"
            f"Нажми «Продолжить путь» чтобы идти дальше."
        )
        await message.answer(text, reply_markup=dungeon_main_keyboard(step))


async def _enemy_defeated(callback, state, bot, run, enemy, player_hp):
    """Победа над врагом (обычный или босс): награды, лут, переходы.

    Используется и при убийстве ударом, и когда враг пал от эффекта оружия
    (тики DoT в начале хода игрока). Вызывается с гарантией, что HP врага == 0.
    """
    user_id = callback.from_user.id
    if enemy['is_boss']:
        reward = enemy['reward_nm'] or 0
        if reward > 0:
            await add_run_nordmarks(run['id'], reward)

        if run['floor'] == 1:
            # Промежуточный босс «Крысиный капитан»: награда копится в луте,
            # после победы — выбор: водохранилище или этаж 2.
            await state.update_data(captain_defeated=1)
            await log_activity(user_id, "dungeon_boss",
                               f"Победил промежуточного босса «{enemy['name']}» на 1 этаже")
            run = await get_active_run(user_id)
            await post_captain_menu(callback.message, run, state)
        else:
            # Финальный босс «Король крыс» (этаж 2): полная зачистка.
            run = await get_active_run(user_id)
            loot_nm = run['loot_nm'] or 0
            if loot_nm > 0:
                await add_nordmarks(user_id, loot_nm, "dungeon_win", "Вынесено из подземелья")

            transferred = await transfer_run_items_to_inventory(user_id, run['id'])

            text = (
                f"🏆 БОСС ПОБЕЖДЁН!\n"
                f"💀 {enemy['name']} повержен!\n\n"
                f"🎉 Поздравляем! Ты прошёл подземелье до конца!\n\n"
                f"📦 Ты выносишь из подземелья:\n"
            )
            if loot_nm > 0:
                text += f"💰 {loot_nm} Нордмарок\n"
            for name, qty in transferred:
                text += f"🎁 {name} x{qty}\n"
            if loot_nm <= 0 and not transferred:
                text += "… пусто."

            await end_run(run['id'], 0)
            await state.clear()
            await log_activity(user_id, "dungeon_win",
                               f"Прошёл «{enemy['name']}»/подземелье на {run['floor']} этаже")
            await answer_enemy_photo(callback.message, enemy, text, reply_markup=dungeon_start_keyboard())
            pilot = await get_user(user_id)
            await notify(bot, f"🏆 Пилот {await player_display(pilot)} прошёл подземелье и победил босса «{enemy['name']}»!", user_id)
    else:
        hp_text = _hp_bar(player_hp, run['hp_max'])
        text = (
            f"🏆 {enemy['name']} повержен!\n"
        )

        dropped = await roll_enemy_drops(run['id'], enemy)
        if dropped:
            text += "\n🎁 Лут:\n" + "\n".join(f"• {name} x{qty}" for name, qty in dropped) + "\n\n"
        else:
            text += "\n"

        text += f"❤️ {hp_text}\n"
        text += f"Нажми «Продолжить путь» чтобы идти дальше."
        next_step = await dungeon_new_step(state)
        await answer_enemy_photo(callback.message, enemy, text, reply_markup=dungeon_main_keyboard(next_step))


@router.callback_query(F.data.startswith("dungeon:attack:"))
async def dungeon_attack(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    user_id = callback.from_user.id
    run = await get_active_run(user_id)
    if not run:
        await callback.message.answer("❌ Подземелье не найдено.")
        await state.clear()
        return

    parts = callback.data.split(":")
    if len(parts) < 4:
        return
    enemy_id = int(parts[2])
    encoded_step = int(parts[3])

    data = await state.get_data()
    if encoded_step != await dungeon_current_step(state):
        await _log_stale(callback, "данж: устаревшая кнопка атаки")
        await callback.message.answer("⚠️ Это устаревшая кнопка. Используй кнопки из последнего сообщения боя.")
        return
    current_enemy_id = data.get('current_enemy_id')
    if current_enemy_id is not None and current_enemy_id != enemy_id:
        await callback.message.answer("⚠️ Этого врага уже нет в текущей комнате.")
        return

    conn = await get_db()
    cursor = await conn.execute("SELECT * FROM dungeon_enemies WHERE id = ?", (enemy_id,))
    enemy = await cursor.fetchone()
    if not enemy:
        return

    current_enemy_hp = data.get('current_enemy_hp', enemy['hp'])
    poison = data.get('active_poison')
    player_hp = run['hp']

    # ── Тики статусов в начале хода игрока (яд, кровотечение, обморожение) ──
    async def dot_death(line):
        nm_penalty = max(5, enemy['reward_nm'] * 2)
        await remove_nordmarks(user_id, nm_penalty, "dungeon_death", "Штраф за смерть в подземелье")
        text = f"{line}\n💀 Ты погиб! −{nm_penalty} Нордмарок штраф.\nСобранный лут потерян."
        await end_run(run['id'], 0)
        await state.clear()
        await answer_enemy_photo(callback.message, enemy, text, reply_markup=dungeon_start_keyboard())

    # Яд (не спадает сам, снимается антидотом).
    if poison:
        player_hp = max(0, player_hp - poison)
        await update_run_hp(run['id'], player_hp)
        if player_hp <= 0:
            await dot_death(f"☠️ Яд погубил тебя (−{poison} HP)")
            return

    # Кровотечение (спадает через BLEED_TICKS_MAX ходов).
    bleed = data.get('active_bleed')
    if bleed:
        player_hp = max(0, player_hp - bleed)
        await update_run_hp(run['id'], player_hp)
        if player_hp <= 0:
            await dot_death(f"🩸 Ты истёк кровью (−{bleed} HP)")
            return
        bticks = int(data.get('bleed_ticks', 0) or 0) - 1
        if bticks <= 0:
            await state.update_data(active_bleed=None, bleed_ticks=0)
        else:
            await state.update_data(bleed_ticks=bticks)

    # Обморожение спадает само через FROSTBITE_TURNS ходов игрока.
    if data.get('active_frostbite'):
        fticks = int(data.get('frostbite_ticks', 0) or 0) - 1
        if fticks <= 0:
            await state.update_data(active_frostbite=None, frostbite_ticks=0)
        else:
            await state.update_data(frostbite_ticks=fticks)

    # ── Тики эффекта оружия игрока на враге (в начале хода игрока) ──
    if data.get('enemy_effect'):
        edmg = int(data.get('enemy_effect_dmg', 0) or 0)
        eticks = int(data.get('enemy_effect_ticks', 0) or 0)
        if edmg > 0:
            current_enemy_hp = max(0, current_enemy_hp - edmg)
        remained = eticks - 1
        if remained <= 0:
            await state.update_data(enemy_effect=None, enemy_effect_dmg=0, enemy_effect_ticks=0)
        else:
            await state.update_data(enemy_effect_ticks=remained)
        await state.update_data(current_enemy_hp=current_enemy_hp)
        if current_enemy_hp <= 0:
            label = WEAPON_EFFECT_LABELS.get(data['enemy_effect'], data['enemy_effect'])
            await callback.message.answer(
                f"💀 {enemy['name']} пал от {label} твоего оружия (−{edmg} HP)!"
            )
            await _enemy_defeated(callback, state, bot, run, enemy, player_hp)
            return

    weapon_damage = await get_player_weapon_damage(user_id)
    damage_to_enemy = calculate_attack(0, weapon_damage)
    from utils.states import get_state_info, combat_multipliers
    state_info = await get_state_info(user_id)
    mult = combat_multipliers(state_info['names'])
    am = mult.get('attack_mult', 1.0)
    award_bonus = await get_award_bonus(user_id)
    am *= 1.0 + award_bonus['attack'] / 100.0
    damage_to_enemy = max(1, int(damage_to_enemy * am))

    # Уклонение врага: может полностью избежать удара
    enemy_dodge = enemy['dodge'] if 'dodge' in enemy.keys() else 0
    enemy_dodged = roll_dodge(enemy_dodge)
    if enemy_dodged:
        damage_to_enemy = 0

    current_enemy_hp = max(0, current_enemy_hp - damage_to_enemy)
    await state.update_data(current_enemy_hp=current_enemy_hp)

    enemy_eff_just = False
    if current_enemy_hp <= 0:
        await _enemy_defeated(callback, state, bot, run, enemy, player_hp)
        return

    from utils.combat import get_enemy_bar
    enemy_bar = get_enemy_bar(current_enemy_hp, enemy['hp'])
    if enemy_dodged:
        attack_line = f"💨 {enemy['name']} уклонился от удара! (−0 HP врагу)\n"
    else:
        attack_line = f"−{damage_to_enemy} HP врагу\n"
    text = (
        f"🗡️ Ты атакуешь {enemy['name']}!\n"
        f"{attack_line}"
        f"{enemy_bar}\n\n"
    )

    # Особый эффект оружия: при попадании есть шанс наложить DoT/оглушение на врага.
    weapon = await get_equipped_weapon(user_id)
    weff = weapon.get('weapon_effect') if weapon else None
    if weff and not enemy_dodged:
        wch = int(weapon.get('weapon_effect_chance') or 0)
        wdmg = int(weapon.get('weapon_effect_dmg') or 0)
        if wch and wdmg and random.randint(1, 100) <= wch:
            if weff == 'stun':
                await state.update_data(enemy_stun_ticks=WEAPON_STUN_TICKS,
                                        enemy_stun_penalty=wdmg)
                text += (f"\n{WEAPON_EFFECT_EMOJI[weff]} {WEAPON_EFFECT_ATTACK_LINE[weff]}! "
                         f"Шанс {enemy['name']} промахнуться: +{wdmg}% "
                         f"({WEAPON_STUN_TICKS} хода).")
                enemy_eff_just = True
            else:
                await state.update_data(enemy_effect=weff, enemy_effect_dmg=wdmg,
                                        enemy_effect_ticks=WEAPON_DOT_TICKS)
                text += (f"\n{WEAPON_EFFECT_EMOJI[weff]} {WEAPON_EFFECT_ATTACK_LINE[weff]}! "
                         f"{WEAPON_EFFECT_LABELS[weff]}: −{wdmg} HP врагу каждый ход "
                         f"({WEAPON_DOT_TICKS} хода).")
                enemy_eff_just = True

    # Уклонение пилота: шанс избежать контратаки (база + нашивка, × состояния)
    player_dodge = await get_player_dodge(user_id, mult.get('dodge_mult', 1.0))
    player_dodged = roll_dodge(player_dodge)
    # Оглушение: враг дезориентирован, его точность падает (штраф к попаданию).
    stun_data = await state.get_data()
    enemy_stun_ticks = int(stun_data.get('enemy_stun_ticks', 0) or 0)
    enemy_stun_penalty = int(stun_data.get('enemy_stun_penalty', 0) or 0)
    stunned_miss = (not player_dodged and enemy_stun_ticks > 0
                    and enemy_stun_penalty > 0 and roll_dodge(enemy_stun_penalty))
    enemy_dmg = calculate_enemy_damage(enemy['attack'])
    armor = await get_player_armor_with_bonus(user_id)
    blocked_line = ""
    if stunned_miss:
        reduced = 0
        stun_line = (f"💫 {enemy['name']} оглушён и промахивается! (−0 HP)")
    elif player_dodged:
        reduced = 0
        dodge_line = f"💨 Ты уклонился от атаки {enemy['name']}! (−0 HP)"
    else:
        reduced = max(1, enemy_dmg - armor)
        if armor > 0 and reduced < enemy_dmg:
            blocked_line = f"\n🛡️ Броня поглотила {enemy_dmg - reduced} урона!"
        dodge_line = ""
    player_hp = max(0, player_hp - reduced)
    await update_run_hp(run['id'], player_hp)

    # Оглушение длится WEAPON_STUN_TICKS ходов — снимаем тик после атаки врага.
    if enemy_stun_ticks > 0:
        enemy_stun_ticks -= 1
        if enemy_stun_ticks <= 0:
            await state.update_data(enemy_stun_ticks=0, enemy_stun_penalty=0)
        else:
            await state.update_data(enemy_stun_ticks=enemy_stun_ticks)

    if stunned_miss:
        text += stun_line
    elif player_dodged:
        text += dodge_line
    else:
        from utils.combat import get_enemy_attack_text
        text += get_enemy_attack_text(enemy['name'], reduced, player_hp) + blocked_line

    # Навесить яд/кровотечение/обморожение при укусе врага (только если враг попал)
    poison_just_applied = False
    bleed_just_applied = False
    frost_just_applied = False
    if not player_dodged:
        pc = enemy['poison_chance'] if 'poison_chance' in enemy.keys() else 0
        if pc and enemy['poison_dmg'] and random.randint(1, 100) <= pc:
            await state.update_data(active_poison=enemy['poison_dmg'])
            text += f"\n☠️ {enemy['name']} отравил тебя! Яд: −{enemy['poison_dmg']} HP каждый ход."
            poison_just_applied = True
        bc = enemy['bleed_chance'] if 'bleed_chance' in enemy.keys() else 0
        bd = enemy['bleed_dmg'] if 'bleed_dmg' in enemy.keys() else 0
        if bc and bd and random.randint(1, 100) <= bc:
            await state.update_data(active_bleed=bd, bleed_ticks=BLEED_TICKS_MAX)
            text += (f"\n🩸 {enemy['name']} ранил тебя! Кровотечение: −{bd} HP каждый ход "
                     f"(спадёт через {BLEED_TICKS_MAX} ходов).")
            bleed_just_applied = True
        fc = enemy['frostbite_chance'] if 'frostbite_chance' in enemy.keys() else 0
        if fc and random.randint(1, 100) <= fc:
            await state.update_data(active_frostbite=1, frostbite_ticks=FROSTBITE_TURNS)
            text += (f"\n🧊 {enemy['name']} окутал тебя морозом! Обморожение: лечение −50%. "
                     f"{FROSTBITE_CURE_HINT} Или пройдёт само через {FROSTBITE_TURNS} хода.")
            frost_just_applied = True

    # Показывать текущие статусы, пока игрок их не снял
    data_after = await state.get_data()
    active_poison = data_after.get('active_poison')
    if active_poison and not poison_just_applied:
        text += f"\n☠️ Ты отравлен! Яд: −{active_poison} HP каждый ход."
    if data_after.get('active_bleed') and not bleed_just_applied:
        fticks = int(data_after.get('bleed_ticks', 0) or 0)
        rem = f" (спадёт через {fticks} х.)" if fticks else " (спадёт скоро)"
        text += f"\n🩸 Кровотечение: −{data_after['active_bleed']} HP каждый ход{rem}."
    if data_after.get('active_frostbite') and not frost_just_applied:
        text += f"\n🧊 Обморожение: лечение −50%. {FROSTBITE_CURE_HINT}"
    # Текущий эффект оружия на враге (пока сам не спал).
    if data_after.get('enemy_effect') and not enemy_eff_just:
        eeff = data_after['enemy_effect']
        edmg = int(data_after.get('enemy_effect_dmg', 0) or 0)
        eticks = int(data_after.get('enemy_effect_ticks', 0) or 0)
        rem = f" (осталось {eticks} х.)" if eticks else ""
        text += (f"\n{WEAPON_EFFECT_EMOJI[eeff]} Враг под "
                 f"{WEAPON_EFFECT_LABELS.get(eeff, eeff)}: −{edmg} HP каждый ход{rem}.")
    # Оглушение врага (отдельно: это не DoT, а штраф к точности).
    if data_after.get('enemy_stun_ticks') and not enemy_eff_just:
        stun_ticks_left = int(data_after.get('enemy_stun_ticks', 0) or 0)
        stun_pen = int(data_after.get('enemy_stun_penalty', 0) or 0)
        text += (f"\n💫 Враг оглушён: его точность −{stun_pen}% "
                 f"(осталось {stun_ticks_left} х.).")

    if player_hp <= 0:
        nm_penalty = max(5, enemy['reward_nm'] * 2)
        await remove_nordmarks(user_id, nm_penalty, "dungeon_death", "Штраф за смерть в подземелье")
        text += f"\n\n💀 Ты погиб! −{nm_penalty} Нордмарок штраф.\nСобранный лут потерян."
        await end_run(run['id'], 0)
        await state.clear()
        await log_activity(user_id, "dungeon_death", f"Погиб в подземелье от «{enemy['name']}»")
        await answer_enemy_photo(callback.message, enemy, text, reply_markup=dungeon_start_keyboard())
    else:
        slot_items = await _combat_slot_items(user_id, is_boss=bool(enemy['is_boss']))
        next_step = await dungeon_new_step(state)
        if enemy['is_boss']:
            await answer_enemy_photo(callback.message, enemy, text, reply_markup=dungeon_boss_keyboard(enemy['id'], slot_items, next_step))
        else:
            await answer_enemy_photo(callback.message, enemy, text, reply_markup=dungeon_combat_keyboard(enemy['id'], slot_items, next_step))


async def battle_state_block_message(user_id: int):
    """Сообщение, если состояния игрока запрещают расходники в бою.

    Возвращает текст блокировки («несварение»/«очень пьян») или None — всё
    в порядке. В бою применение предметов из слотов (антидот, зелья, напитки,
    дымовые шашки) подчиняется тем же правилам, что и вне боя.
    """
    from utils.states import get_state_info, consumables_blocked
    info = await get_state_info(user_id)
    blocked = consumables_blocked(info.get('names') or [])
    if not blocked:
        return None
    if "очень пьян" in blocked:
        return ("🥴 Ты слишком пьян, чтобы что-то применять. "
                "Зелья и расходники станут доступны, когда «очень пьян» пройдёт (6 часов).")
    return ("🤢 Несварение: пищеварение на паузе. "
            "Расходники нельзя применять ещё сутки.")


@router.callback_query(F.data.startswith("dungeon:use_slot:"))
async def dungeon_use_slot(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    user_id = callback.from_user.id
    parts = callback.data.split(":")
    if len(parts) < 4:
        return
    slot = parts[2]
    encoded_step = int(parts[3])

    data = await state.get_data()
    if encoded_step != await dungeon_current_step(state):
        await _log_stale(callback, "данж: устаревшая кнопка слота")
        await callback.message.answer("⚠️ Это устаревшая кнопка. Используй кнопки из последнего сообщения боя.")
        return

    run = await get_active_run(user_id)
    if not run:
        await callback.message.answer("❌ Подземелье не найдено.")
        await state.clear()
        return

    item = None
    for s, row in await get_equipment_slot_items(user_id, include_smoke=True):
        if s == slot:
            item = row
            break
    if not item:
        await callback.message.answer("❌ Этот слот пуст.")
        return

    # Состояния «несварение»/«очень пьян» блокируют расходники (еда/питьё) и в бою,
    # но дымовая шашка — тактический предмет, а не еда/питьё: её состояния не блокируют.
    if item['name'] == SMOKE_ITEM_NAME:
        blk = None
    else:
        blk = await battle_state_block_message(user_id)
    if blk:
        await callback.message.answer(blk)
        return

    smoke_uses = int(data.get('dungeon_smoke_uses', 0) or 0)

    # Враг текущей комнаты (нужен для шашки и финальной перерисовки).
    enemy_id = data.get('current_enemy_id')
    enemy_row = None
    if enemy_id is not None:
        conn = await get_db()
        cursor = await conn.execute("SELECT * FROM dungeon_enemies WHERE id = ?", (enemy_id,))
        enemy_row = await cursor.fetchone()
    is_boss = bool(enemy_row and enemy_row['is_boss'])

    # Дымовая шашка: применение = попытка побега с 95% шансом (расходует предмет).
    if item['name'] == SMOKE_ITEM_NAME:
        if slot != 'smoke':
            await callback.message.answer(
                "❌ Дымовая шашка применяется только из своего слота «Дымовая шашка» "
                "(Инвентарь → Снаряжение).")
            return
        if not enemy_row:
            await callback.message.answer("❌ Врага не найдено.")
            return
        if is_boss:
            await callback.message.answer("⚠️ От босса не убежать! Дымовая шашка не поможет.")
            return
        if smoke_uses >= DUNGEON_SMOKE_MAX:
            await callback.message.answer(
                f"❌ За один забег в подземелье можно применить не больше {DUNGEON_SMOKE_MAX} дымовых шашек."
            )
            return
        ok = await remove_inventory_item(user_id, item['id'], 1)
        if not ok:
            await callback.message.answer("❌ Не удалось списать шашку.")
            return
        await log_activity(user_id, "item_use", "В бою: дымовая шашка (попытка побега)")
        inv_after_sm = await get_inventory_item(user_id, item['id'])
        if not inv_after_sm or (inv_after_sm['quantity'] or 0) <= 0:
            await clear_equipment_slot(user_id, slot)
        await state.update_data(dungeon_smoke_uses=smoke_uses + 1)
        await _do_dungeon_escape(callback.message, state, user_id, run, enemy_row, smoke_used=True)
        return

    if item['cure_poison'] and not data.get('active_poison'):
        await callback.message.answer("Ты не отравлен, антидот бесполезен.")
        return

    from utils.helpers import row_get
    is_drink = bool(row_get(item, 'drink_effect'))
    if item['heal'] > 0 and run['hp'] >= run['hp_max'] and not is_drink:
        await callback.message.answer(
            f"❤️ HP уже полное ({run['hp']}/{run['hp_max']}), зелье не нужно.\n"
            f"Примени его в бою, когда потеряешь HP."
        )
        return

    ok = await remove_inventory_item(user_id, item['id'], 1)
    if not ok:
        await callback.message.answer("❌ Не удалось списать предмет.")
        return

    # Предмет кончился — очищаем слот, чтобы он не остался «призрачным»
    inv_after = await get_inventory_item(user_id, item['id'])
    if not inv_after or (inv_after['quantity'] or 0) <= 0:
        await clear_equipment_slot(user_id, slot)

    slot_items = await _combat_slot_items(user_id, is_boss=is_boss)
    await log_activity(user_id, "item_use", f"В бою: «{item['name']}»")

    if item['cure_poison']:
        await state.update_data(active_poison=None)
        text = (
            f"⚗️ {item['name']} применён: отравление снято!\n"
            f"Продолжай бой:"
        )

    # Напиток: (+10 HP отдельным путём, +effect на состояние).
    elif is_drink:
        from database.db import consume_drink
        _ok, _msg = await consume_drink(user_id, item['id'])
        hp_note = ""
        frost_note = ""
        # Напитки с cure_frostbite (Огненная вода, Горячий ягодный морс) снимают обморожение.
        if item.get('cure_frostbite') and data.get('active_frostbite'):
            await state.update_data(active_frostbite=None, frostbite_ticks=0)
            frost_note = "\n🧊 Обморожение снято!"
        if item['heal'] > 0:
            heal_uses = int(data.get('dungeon_heal_uses', 0) or 0) + 1
            await state.update_data(dungeon_heal_uses=heal_uses)
            mult = heal_limit_mult(heal_uses)
            frozen = bool(data.get('active_frostbite'))
            if frozen:
                mult *= FROSTBITE_HEAL_MULT
            heal = max(1, round(item['heal'] * mult))
            new_hp = min(run['hp_max'], run['hp'] + heal)
            await update_run_hp(run['id'], new_hp)
            hp_note = f"\n❤️ {_hp_bar(new_hp, run['hp_max'])}"
            if mult < 1.0:
                hp_note += f" (эффективность ×{mult:.0%}: {heal} HP вместо {item['heal']})"
            if frozen:
                hp_note += "\n🧊 Обморожение снизило лечение."
        text = _msg + frost_note + hp_note + heal_limit_note(int(data.get('dungeon_heal_uses', 0) or 0)) + "\n\nПродолжай бой:"

    # Зелья лечения / яблоко / испорченная рыба.
    elif item['heal'] > 0:
        heal_uses = int(data.get('dungeon_heal_uses', 0) or 0) + 1
        await state.update_data(dungeon_heal_uses=heal_uses)
        mult = heal_limit_mult(heal_uses)
        frozen = bool(data.get('active_frostbite'))
        if frozen:
            mult *= FROSTBITE_HEAL_MULT
        heal = max(1, round(item['heal'] * mult))
        new_hp = min(run['hp_max'], run['hp'] + heal)
        await update_run_hp(run['id'], new_hp)
        eff = ""
        if mult < 1.0:
            eff = f" (эффективность ×{mult:.0%}: {heal} HP вместо {item['heal']})"
        if frozen:
            eff += "\n🧊 Обморожение снизило лечение."
        text = (
            f"💊 {item['name']} применено: +{heal} HP{eff}!\n"
            f"❤️ {_hp_bar(new_hp, run['hp_max'])}\n"
            f"{heal_limit_note(heal_uses)}"
            f"\n\nПродолжай бой:"
        )

        # Яблоко: иногда из него выпадает семечко (10%)
        if item['name'] == "Яблоко" and random.random() < 0.1:
            seed = await get_item_by_name("Яблочное семечко")
            if seed:
                await add_inventory_item(user_id, seed['id'], 1)
                text += "\n\n🌱 Из яблока выпало семечко!"
        # Испорченная рыба: несварение на сутки
        if item['name'].startswith("Испорченный"):
            from utils.states import apply_state_to
            await apply_state_to(user_id, "несварение", caused_by=user_id,
                                 reason="съедена испорченная рыба")
            text += ("\n\n🤢 Ты съел испорченную рыбу — наступило несварение на сутки. "
                     "Нельзя применять расходники.")
    else:
        await add_inventory_item(user_id, item['id'], 1)
        await callback.message.answer("❌ Этот предмет нельзя использовать в бою.")
        return

    next_step = await dungeon_new_step(state)
    if is_boss:
        await callback.message.answer(text, reply_markup=dungeon_boss_keyboard(enemy_id, slot_items, next_step))
    else:
        await callback.message.answer(text, reply_markup=dungeon_combat_keyboard(enemy_id, slot_items, next_step))


async def _do_dungeon_escape(where, state, user_id: int, run, enemy,
                             smoke_used: bool = False):
    """Попытка побега из боя с обычным врагом.

    smoke_used=True — побег через дымовую шашку (предмет уже списан):
    шанс DUNGEON_SMOKE_ESCAPE% против пониженного без шашки.
    В состоянии «очень пьян» шанс побега сильно снижен (× DUNGEON_ESCAPE_DRUNK_MULT),
    даже при применении дымовой шашки.
    """
    from config import DUNGEON_ESCAPE_DRUNK_MULT
    from utils.states import get_state_info
    info = await get_state_info(user_id)
    drunk_escape = "очень пьян" in info['names']
    percent_mult = DUNGEON_ESCAPE_DRUNK_MULT if drunk_escape else 1.0

    hp_percent = run['hp'] / run['hp_max'] if run['hp_max'] > 0 else 1.0
    escaped = escape_chance(hp_percent, smoke_used=smoke_used, percent_mult=percent_mult)

    if escaped:
        next_step = await dungeon_new_step(state)
        if smoke_used:
            text = (
                f"💨 Ты взрываешь дымовую шашку — едкий дым застилает комнату!\n"
                f"🏃 Пока враг мечется в пелене дыма, ты успешно убежал от {enemy['name']}!\n"
                f"Нажми «Продолжить путь» чтобы идти дальше."
            )
        else:
            text = (
                f"🏃 Ты успешно убежал от {enemy['name']}!\n"
                f"Нажми «Продолжить путь» чтобы идти дальше."
            )
        if drunk_escape:
            text = f"🥴 Ты едва держишься на ногах, но удача не покинула тебя!\n\n" + text
        await where.answer(text, reply_markup=dungeon_main_keyboard(next_step))
        return

    penalty = calculate_escape_damage()
    player_hp = max(0, run['hp'] - penalty)
    await update_run_hp(run['id'], player_hp)

    text = (
        f"❌ Не удалось убежать!\n"
        f"−{penalty} HP (штрафной удар)\n"
        f"❤️ {_hp_bar(player_hp, run['hp_max'])}\n\n"
        f"Ты продолжаешь бой с {enemy['name']}."
    )
    if smoke_used:
        text += "\n💨 Дымовая шашка потрачена впустую."
    if drunk_escape:
        text = "🥴 Шатаясь, ты совсем теряешь координацию!\n\n" + text

    if player_hp <= 0:
        nm_penalty = max(5, enemy['reward_nm'] * 2)
        await remove_nordmarks(user_id, nm_penalty, "dungeon_death", "Штраф за смерть в подземелье")
        text += f"\n\n💀 Ты погиб! −{nm_penalty} Нордмарок штраф.\nСобранный лут потерян."
        await end_run(run['id'], 0)
        await state.clear()
        await log_activity(user_id, "dungeon_death", "Погиб при попытке побега в подземелье")
        await answer_enemy_photo(where, enemy, text, reply_markup=dungeon_start_keyboard())
    else:
        slot_items = await _combat_slot_items(user_id)
        next_step = await dungeon_new_step(state)
        await answer_enemy_photo(where, enemy, text,
                                 reply_markup=dungeon_combat_keyboard(enemy['id'], slot_items, next_step))


@router.callback_query(F.data.startswith("dungeon:escape:"))
async def dungeon_escape(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    user_id = callback.from_user.id
    run = await get_active_run(user_id)
    if not run:
        await state.clear()
        return

    parts = callback.data.split(":")
    if len(parts) < 4:
        return
    enemy_id = int(parts[2])
    encoded_step = int(parts[3])

    data = await state.get_data()
    if encoded_step != await dungeon_current_step(state):
        await _log_stale(callback, "данж: устаревшая кнопка побега")
        await callback.message.answer("⚠️ Это устаревшая кнопка. Используй кнопки из последнего сообщения боя.")
        return
    current_enemy_id = data.get('current_enemy_id')
    if current_enemy_id is not None and current_enemy_id != enemy_id:
        await callback.message.answer("⚠️ Этого врага уже нет в текущей комнате.")
        return

    conn = await get_db()
    cursor = await conn.execute("SELECT * FROM dungeon_enemies WHERE id = ?", (enemy_id,))
    enemy = await cursor.fetchone()
    if not enemy:
        return

    if enemy['is_boss']:
        slot_items = await _combat_slot_items(user_id, is_boss=True)
        next_step = await dungeon_new_step(state)
        await callback.message.answer(
            "⚠️ От босса не убежать! Бой продолжается.",
            reply_markup=dungeon_boss_keyboard(enemy['id'], slot_items, next_step)
        )
        return

    await _do_dungeon_escape(callback.message, state, user_id, run, enemy)


async def show_boss(message, run, user_id, state: FSMContext):
    enemies = await get_floor_enemies(run['dungeon_id'], run['floor'])
    boss_list = [e for e in enemies if e['is_boss']]
    if not boss_list:
        await message.answer("❌ Босс не найден.")
        return

    boss = boss_list[0]
    hp_text = _hp_bar(run['hp'], run['hp_max'])
    slot_items = await _combat_slot_items(user_id, is_boss=True)
    sdata = await state.get_data()
    step = await dungeon_new_step(state)

    await state.update_data(current_enemy_id=boss['id'], current_enemy_hp=boss['hp'],
                                enemy_effect=None, enemy_effect_dmg=0, enemy_effect_ticks=0)

    boss_status = status_lines(sdata)
    boss_heal_uses = int(sdata.get('dungeon_heal_uses', 0) or 0)
    if boss_heal_uses >= DUNGEON_HEAL_SOFT_LIMIT:
        bmult = heal_limit_mult(boss_heal_uses)
        boss_status.append(f"💊 Лекарства: {boss_heal_uses} применений (×{bmult:.0%})")
    status_block = "\n".join(boss_status)
    if status_block:
        status_block += "\n"
    bdesc = boss['description'] if 'description' in boss.keys() and boss['description'] else ""
    boss_name = "КОМНАТА БОССА" if run['floor'] == 2 else "ПРОМЕЖУТОЧНЫЙ БОСС"
    text = (
        f"💀 {boss_name}\n"
        f"Этаж {run['floor']} | БОСС\n"
        f"❤️ {hp_text}\n"
        f"{status_block}"
        f"💀 {boss['name']} (HP: {boss['hp']}, АТК: {boss['attack']}, УКЛ: {boss['dodge'] if 'dodge' in boss.keys() else 0}%)\n\n"
        f"{bdesc}\n\n"
        f"⚠️ Это решающий бой! Убежать нельзя!"
    )
    await answer_enemy_photo(message, boss, text, reply_markup=dungeon_boss_keyboard(boss['id'], slot_items, step))
    await state.set_state(DungeonFSM.in_boss)


@router.callback_query(F.data.regexp(r"^resv:enter:\d+$"))
async def resv_enter(callback: CallbackQuery, state: FSMContext):
    """Вход в подземное водохранилище (доступно после победы над капитаном)."""
    await callback.answer()
    user_id = callback.from_user.id
    parts = callback.data.split(":")
    if parts[2] != str(await dungeon_current_step(state)):
        await _log_stale(callback, "данж: устаревшая кнопка водохранилища")
        await callback.message.answer("⚠️ Это устаревшая кнопка.")
        return
    run = await get_active_run(user_id)
    if not run:
        await callback.message.answer("❌ Активное подземелье не найдено.")
        await state.clear()
        return
    data = await state.get_data()
    if not (run['floor'] == 1 and data.get('captain_defeated')):
        await callback.message.answer("⚠️ Водохранилище доступно только после победы над Крысиным капитаном.")
        return
    await state.set_state(DungeonFSM.in_reservoir)
    await log_activity(user_id, "dungeon_reservoir", "Зашёл в подземное водохранилище")
    await show_reservoir(callback.message, user_id, state)


@router.callback_query(F.data.regexp(r"^resv:menu:\d+$"))
async def resv_menu(callback: CallbackQuery, state: FSMContext):
    """Назад в меню водохранилища."""
    await callback.answer()
    user_id = callback.from_user.id
    parts = callback.data.split(":")
    if parts[2] != str(await dungeon_current_step(state)):
        await _log_stale(callback, "данж: устаревшая кнопка водохранилища")
        await callback.message.answer("⚠️ Это устаревшая кнопка.")
        return
    await state.set_state(DungeonFSM.in_reservoir)
    await show_reservoir(callback.message, user_id, state)


@router.callback_query(F.data.regexp(r"^resv:bait:\d+$"))
async def resv_bait_menu(callback: CallbackQuery, state: FSMContext):
    """Выбор наживки в подземном водохранилище."""
    await callback.answer()
    user_id = callback.from_user.id
    parts = callback.data.split(":")
    if parts[2] != str(await dungeon_current_step(state)):
        await _log_stale(callback, "данж: устаревшая кнопка водохранилища")
        await callback.message.answer("⚠️ Это устаревшая кнопка.")
        return
    if await state.get_state() != DungeonFSM.in_reservoir.state:
        await callback.message.answer("❌ Ты больше не в водохранилище.")
        return

    user = await get_user(user_id) or {}
    chosen = (user.get('fishing_bait') or "").strip()

    worms = await get_item_by_name(WORMS_NAME)
    spider = await get_item_by_name(SPIDER_LEG_NAME)
    combined = await get_item_by_name(COMBINED_BAIT_NAME)
    worms_qty = 0
    if worms:
        w_inv = await get_inventory_item(user_id, worms['id'])
        worms_qty = w_inv['quantity'] if w_inv else 0
    spider_inv = await get_inventory_item(user_id, spider['id']) if spider else None
    spider_qty = spider_inv['quantity'] if spider_inv else 0
    combined_inv = await get_inventory_item(user_id, combined['id']) if combined else None
    combined_qty = combined_inv['quantity'] if combined_inv else 0

    selected = {
        "worms": WORMS_NAME,
        "spider": SPIDER_LEG_NAME,
        "combined": COMBINED_BAIT_NAME,
        "none": "Без наживки",
        "": "Авто (что есть)",
    }.get(chosen, "")
    text = (
        "🪱 НАЖИВКА (ВОДОХРАНИЛИЩЕ)\n\n"
        f"Сейчас: {selected or chosen}\n"
        "Наживка расходуется при каждом забросе.\n"
        "«Авто»: сначала черви, затем лапка, затем комбинированная.\n\n"
        f"⚠️ Без наживки рыба не клюёт: со дна только мусор "
        f"{await junk_hint('reservoir')}."
    )
    await edit_or_replace(callback.message, text, _reservoir_bait_markup(
        chosen, worms_qty, spider_qty, combined_qty, step=int(parts[2])))


@router.callback_query(F.data.regexp(r"^resv:bait:set:\d+:[a-z]+$"))
async def resv_bait_set(callback: CallbackQuery, state: FSMContext):
    """Применить выбранную наживку в водохранилище."""
    await callback.answer()
    user_id = callback.from_user.id
    parts = callback.data.split(":")
    step, value = parts[3], parts[4]
    if step != str(await dungeon_current_step(state)):
        await _log_stale(callback, "данж: устаревшая кнопка водохранилища")
        await callback.message.answer("⚠️ Это устаревшая кнопка.")
        return
    if await state.get_state() != DungeonFSM.in_reservoir.state:
        await callback.message.answer("❌ Ты больше не в водохранилище.")
        return
    await update_user(user_id, fishing_bait=value)
    await state.set_state(DungeonFSM.in_reservoir)
    await show_reservoir(callback.message, user_id, state)


@router.callback_query(F.data.regexp(r"^resv:cast:\d+$"))
async def resv_cast(callback: CallbackQuery, state: FSMContext):
    """Заброс удочки в подземном водохранилище (механика как на озере: наживка, шанс, улов)."""
    await callback.answer()
    user_id = callback.from_user.id
    parts = callback.data.split(":")
    if parts[2] != str(await dungeon_current_step(state)):
        await _log_stale(callback, "данж: устаревшая кнопка водохранилища")
        await callback.message.answer("⚠️ Это устаревшая кнопка.")
        return
    if await state.get_state() != DungeonFSM.in_reservoir.state:
        await callback.message.answer("❌ Ты больше не в водохранилище.")
        return
    if user_id in FISHING_CASTING:
        await callback.answer("🎣 Ты уже ждёшь улов — дождись результата!", show_alert=True)
        return
    # Лок ставим сразу, до первого await: иначе двойной тап проходит
    # проверку дважды и игрок забрасывает удочку многократно подряд.
    FISHING_CASTING.add(user_id)
    try:
        run = await get_active_run(user_id)
        if not run:
            await callback.message.answer("❌ Подземелье не найдено.")
            await state.clear()
            return

        user = await get_user(user_id)
        if not user:
            return

        rod = await _rod_for(user_id)
        if not rod:
            await callback.message.answer(
                "❌ У тебя нет удочки. Купи «Удочка из орешника» в магазине (категория «Рыбалка»)."
            )
            return

        if user['ap'] < RESERVOIR_AP_COST:
            await callback.message.answer(
                f"❌ Не хватает ОД: нужно {RESERVOIR_AP_COST}, у тебя {user['ap']}.\n"
                f"⚡ ОД восстанавливаются раз в сутки."
            )
            return
        ok = await remove_ap(user_id, RESERVOIR_AP_COST, reason="рыбалка в водохранилище")
        if not ok:
            await callback.message.answer("❌ Не удалось списать ОД.")
            return

        chosen = (user.get('fishing_bait') or "").strip()
        bait_name, bait_id = await _resolve_bait(user_id, chosen)
        if bait_id is not None:
            await remove_inventory_item(user_id, bait_id, 1)

        # Перебиваем старую кнопку заброса (защита от двойного списания ОД).
        await dungeon_new_step(state)

        # Пока идёт ожидание улова — держим лок: выйти, продолжить путь и
        # повторный заброс блокируются (middleware FishingActiveLock + гарды ниже).
        bait_part = f" с наживкой «{bait_name}»" if bait_name else " без наживки"
        try:
            await callback.message.edit_text(
                f"🎣 Ты забрасываешь удочку{bait_part} в тёмную воду подземного водохранилища...\n"
                "Поплавок замер неподвижно. Ждёшь..."
            )
        except Exception:
            await callback.message.answer("🎣 Забрасываешь удочку...")

        await asyncio.sleep(random.uniform(4, 7))

        # Забег мог завершиться (рестарт/форс-выход), пока мы ждали —
        # результат не отдаём и улов не пишем.
        run = await get_active_run(user_id)
        if not run or await state.get_state() != DungeonFSM.in_reservoir.state:
            try:
                await edit_or_replace(callback.message, "🌊 Вода в водохранилище снова гладкая…", None)
            except Exception:
                pass
            return

        fresh = await get_user(user_id) or {}
        _ap = fresh.get('ap', 0) or 0
        _ap_max = fresh.get('ap_max', _ap) or _ap
        ap_line = f"⚡ ОД: {_ap}/{_ap_max}"
        if _ap < RESERVOIR_AP_COST:
            ap_line += f" — на следующий заброс не хватит ({RESERVOIR_AP_COST} ОД)"
        else:
            ap_line += f" — можно забрасывать"
        bait = await _bait_line(user_id, chosen)
        ap_block = f"\n\n{ap_line}\n{bait}"

        next_step = await dungeon_new_step(state)

        if bait_name:
            chance = _catch_chance(rod, bait_name, (await get_award_bonus(callback.from_user.id))['fishing'])
            caught = random.random() * 100 < chance
            if caught:
                fish_name = await _pick_reservoir_fish()
                item = await get_item_by_name(fish_name)
                if not item:
                    result = "❌ Ошибка: рыба не определена."
                else:
                    weight_idx = _roll_fish_weight()
                    tier = fish_weight_tier(weight_idx)
                    sell = fish_sell_price(item['sell_price'], weight_idx)
                    kind = await get_water_fish_kind("reservoir", fish_name)
                    await add_fish_catch(user_id, item['id'], weight_idx, kind=kind)
                    await log_activity(user_id, "dungeon_reservoir_fish",
                                       f"Поймал «{fish_name}» ({tier['label']}) в водохранилище")
                    if fish_name == "Светящаяся форель":
                        name_line = "\n✨ СВЕТЯЩАЯСЯ ФОРЕЛЬ! Секретный улов, о котором шепчутся в Нордхайме!"
                    elif fish_name == "Искрящийся угорь":
                        name_line = "\n🐡 Искрящийся угорь! Редкий улов."
                    else:
                        name_line = "\n🐟 Мерцающий сом. Обычный, но вкусный."
                    result = (
                        f"🎣 ПОКЛЁВКА!\n"
                        f"{RESERVOIR_EMOJI.get(fish_name, '🐟')} Ты поймал: «{fish_name}» — "
                        f"{tier['label'].lower()}!\n"
                        f"{name_line}\n\n"
                        f"🎒 Улов записан в «Улов» (Рыба). Раз в 4 дня сырая рыба портится.\n"
                        f"Вес влияет на цену: продажа за {sell} {plural_nordmark(sell)}."
                    ) + ap_block
                    wf_photo = await get_water_fish_photo_by_name("reservoir", fish_name)
                    local_photo = item_local_photo(fish_name) if not wf_photo else None
                    await _resv_answer(callback.message, result, _reservoir_result_markup(next_step),
                                       photo=local_photo, photo_id=wf_photo)
                    return
            else:
                result = (
                    "🎣 РЫБАЛКА\n\n"
                    "Поплавок дёрнулся, ты подсекаешь... и вдруг пусто.\n"
                    "Сорвалось. Но рыба никуда не денется — пробуй ещё!"
                )
        else:
            # Без наживки рыба не клюёт — из глубины достаётся только мусор.
            junk_name = await _pick_junk("reservoir")
            if junk_name:
                junk_item = await get_item_by_name(junk_name)
                if junk_item:
                    await add_fish_catch(user_id, junk_item['id'], 1, kind="resource")
                    await log_activity(user_id, "dungeon_reservoir_fish", f"Выловил «{junk_name}»")
                    sell_line = ""
                    if junk_item['sell_price'] > 0:
                        sell_line = (
                            f"\nПродать можно за {junk_item['sell_price']} "
                            f"{plural_nordmark(junk_item['sell_price'])}."
                        )
                    result = (
                        f"🎣 РЫБАЛКА\n\n"
                        f"Поплавок дёрнулся, ты подсекаешь...\n"
                        f"Из тёмной воды появляется: «{junk_name}»!\n\n"
                        f"🎒 Улов записан в «Улов».{sell_line}"
                    ) + ap_block
                    jphoto = await junk_photo("reservoir", junk_name)
                    if jphoto:
                        await _resv_answer(callback.message, result, _reservoir_result_markup(next_step),
                                           photo_id=jphoto)
                        return
                    local_photo = item_local_photo(junk_name)
                    if local_photo:
                        await _resv_answer(callback.message, result, _reservoir_result_markup(next_step),
                                           photo=local_photo)
                    else:
                        await edit_or_replace(callback.message, result, _reservoir_result_markup(next_step))
                    return
                else:
                    result = "🎣 Рыбалка\n\n👢 Что-то выловил, но предмет потерялся. Сообщи хранителю."
            else:
                result = (
                    "🎣 РЫБАЛКА\n\n"
                    "Поплавок даже не дрогнул. Без наживки рыба не клюёт — "
                    "с дна достаётся только мусор. Попробуй с наживкой!"
                )
        result += ap_block
        await edit_or_replace(callback.message, result, _reservoir_result_markup(next_step))
    finally:
        FISHING_CASTING.discard(user_id)


@router.callback_query(F.data.regexp(r"^resv:deeper:\d+$"))
async def resv_deeper(callback: CallbackQuery, state: FSMContext):
    """Спуск на 2-й этаж (из выбора после капитана или из водохранилища)."""
    await callback.answer()
    user_id = callback.from_user.id
    parts = callback.data.split(":")
    if parts[2] != str(await dungeon_current_step(state)):
        await _log_stale(callback, "данж: устаревшая кнопка водохранилища")
        await callback.message.answer("⚠️ Это устаревшая кнопка.")
        return
    if user_id in FISHING_CASTING:
        await callback.answer("⏳ Сначала дождись улова из водохранилища!", show_alert=True)
        return
    run = await get_active_run(user_id)
    if not run:
        await callback.message.answer("❌ Подземелье не найдено.")
        await state.clear()
        return
    if run['floor'] >= 2:
        await callback.message.answer("⚠️ Ты уже на самом нижнем этаже.")
        return
    await advance_floor(run['id'], 2)
    await state.update_data(captain_defeated=None)
    await state.set_state(DungeonFSM.in_dungeon)
    run = await get_active_run(user_id)
    await log_activity(user_id, "dungeon_floor", "Спустился на 2-й этаж (лог Короля крыс)")
    await callback.message.answer(
        "⬇️ Ты спускаешься по скрипучей лестнице во мрак. Здесь пахнет сыростью, "
        "плесенью и старой королевской гордостью.\n"
        "🏰 ЭТАЖ 2 | ЛОГОВО КОРОЛЯ КРЫС"
    )
    await show_room(callback.message, run, user_id, state)


@router.callback_query(F.data.regexp(r"^resv:eq:\d+$"))
async def resv_eq(callback: CallbackQuery, state: FSMContext):
    """Смена слотов расходников в водохранилище."""
    await callback.answer()
    user_id = callback.from_user.id
    parts = callback.data.split(":")
    if parts[2] != str(await dungeon_current_step(state)):
        await _log_stale(callback, "данж: устаревшая кнопка водохранилища")
        await callback.message.answer("⚠️ Это устаревшая кнопка.")
        return
    if await state.get_state() != DungeonFSM.in_reservoir.state:
        await callback.message.answer("❌ Ты больше не в водохранилище.")
        return
    await _resv_eq_view(callback.message, user_id, state)


async def _resv_eq_view(where, user_id: int, state: FSMContext):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    eq = await get_equipment(user_id)
    step = await dungeon_new_step(state)
    lines = [
        "🎒 СНАРЯЖЕНИЕ (водохранилище)",
        "",
        "Здесь нет врагов — можно спокойно сменить расходники в активных слотах.",
        "",
    ]
    for slot in ('potion1', 'potion2'):
        item_id = eq.get(slot)
        it = await get_item(item_id) if item_id else None
        lines.append(f"⚗️ {EQUIPMENT_SLOT_LABELS[slot]}: {it['name'] if it else '—'}")
    rows = [
        [InlineKeyboardButton(text="🔄 Слот 1", callback_data=f"resv:eqslot:potion1:{step}")],
        [InlineKeyboardButton(text="🔄 Слот 2", callback_data=f"resv:eqslot:potion2:{step}")],
        [InlineKeyboardButton(text="🔙 К водохранилищу", callback_data=f"resv:menu:{step}")],
    ]
    await edit_or_replace(where, "\n".join(lines), InlineKeyboardMarkup(inline_keyboard=rows))


@router.callback_query(F.data.regexp(r"^resv:eqslot:[a-z0-9_]+:\d+$"))
async def resv_eqslot(callback: CallbackQuery, state: FSMContext):
    """Выбор расходника для слота."""
    await callback.answer()
    user_id = callback.from_user.id
    parts = callback.data.split(":")
    slot = parts[2]
    if parts[3] != str(await dungeon_current_step(state)):
        await _log_stale(callback, "данж: устаревшая кнопка водохранилища")
        await callback.message.answer("⚠️ Это устаревшая кнопка.")
        return
    if await state.get_state() != DungeonFSM.in_reservoir.state:
        await callback.message.answer("❌ Ты больше не в водохранилище.")
        return

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    eq = await get_equipment(user_id)
    equipped_id = eq.get(slot)
    items = await get_inventory(user_id)
    candidates = [it for it in items if item_fits_slot(it, slot)]
    step = await dungeon_new_step(state)

    text = f"🎒 СНАРЯЖЕНИЕ → {EQUIPMENT_SLOT_LABELS[slot]}\n\n"
    if equipped_id:
        it = await get_item(equipped_id)
        text += f"Поставлено: {it['name'] if it else equipped_id}\n"
    else:
        text += "Слот пуст.\n"
    if candidates:
        text += "\nПодходит из инвентаря:"
    else:
        text += "\nВ инвентаре нет подходящих расходников."

    rows = []
    if equipped_id:
        rows.append([InlineKeyboardButton(text="✖️ Снять из слота",
                                          callback_data=f"resv:eqclear:{slot}:{step}")])
    for it in candidates:
        marker = "✅ " if it['id'] == equipped_id else ""
        rows.append([InlineKeyboardButton(
            text=f"{marker}{it['name']} x{it['quantity']}",
            callback_data=f"resv:eqset:{slot}:{it['id']}:{step}")])
    rows.append([InlineKeyboardButton(text="🔙 К снаряжению", callback_data=f"resv:eq:{step}")])
    await edit_or_replace(callback.message, text, InlineKeyboardMarkup(inline_keyboard=rows))


@router.callback_query(F.data.regexp(r"^resv:eqset:[a-z0-9_]+:\d+:\d+$"))
async def resv_eqset(callback: CallbackQuery, state: FSMContext):
    """Установка предмета в слот расходников."""
    await callback.answer()
    user_id = callback.from_user.id
    parts = callback.data.split(":")
    slot, item_id = parts[2], int(parts[3])
    if parts[4] != str(await dungeon_current_step(state)):
        await _log_stale(callback, "данж: устаревшая кнопка водохранилища")
        await callback.message.answer("⚠️ Это устаревшая кнопка.")
        return
    if await state.get_state() != DungeonFSM.in_reservoir.state:
        await callback.message.answer("❌ Ты больше не в водохранилище.")
        return
    item = await get_item(item_id)
    if not item:
        await callback.message.answer("❌ Предмет не найден.")
        return
    await set_equipment_slot(user_id, slot, item_id)
    await callback.message.answer(f"⚗️ {item['name']} поставлен в активный слот.\n"
                                  f"Используется в бою подземелья кнопкой слота.")
    await _resv_eq_view(callback.message, user_id, state)


@router.callback_query(F.data.regexp(r"^resv:eqclear:[a-z0-9_]+:\d+$"))
async def resv_eqclear(callback: CallbackQuery, state: FSMContext):
    """Снятие предмета из слота расходников."""
    await callback.answer()
    user_id = callback.from_user.id
    parts = callback.data.split(":")
    slot = parts[2]
    if parts[3] != str(await dungeon_current_step(state)):
        await _log_stale(callback, "данж: устаревшая кнопка водохранилища")
        await callback.message.answer("⚠️ Это устаревшая кнопка.")
        return
    if await state.get_state() != DungeonFSM.in_reservoir.state:
        await callback.message.answer("❌ Ты больше не в водохранилище.")
        return
    eq = await get_equipment(user_id)
    item_id = eq.get(slot)
    if item_id:
        await clear_equipment_slot(user_id, slot)
        it = await get_item(item_id)
        await callback.message.answer(f"✖️ {it['name'] if it else 'Предмет'} снят из активного слота.")
    await _resv_eq_view(callback.message, user_id, state)


@router.callback_query(F.data == "dungeon:exit")
async def dungeon_exit(callback: CallbackQuery, state: FSMContext):
    """Запрос подтверждения выхода из подземелья (против случайного клика)."""
    await callback.answer()
    user_id = callback.from_user.id

    # Во время боя с боссом покинуть подземелье нельзя.
    if await state.get_state() == DungeonFSM.in_boss.state:
        await callback.message.answer(
            "⚠️ Идёт бой с боссом! Убежать нельзя — это решающий бой.\n"
            "Продолжай бой кнопками последнего сообщения."
        )
        return

    # Пока идёт рыбалка — сначала дождись улова.
    if user_id in FISHING_CASTING:
        await callback.answer("⏳ Сначала дождись улова из водохранилища!", show_alert=True)
        return

    run = await get_active_run(user_id)
    if not run:
        await callback.message.answer("❌ Подземелье не найдено.")
        await state.clear()
        return

    loot_nm = run['loot_nm'] or 0
    run_items = await get_run_items(run['id'])

    parts = []
    if loot_nm > 0:
        parts.append(f"💰 {loot_nm} Нордмарок")
    parts.extend(f"🎁 {n} x{q}" for n, q in run_items)
    loot_text = "\n".join(parts) if parts else "Ничего."

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    await callback.message.answer(
        f"🚪 ПОКИНУТЬ ПОДЗЕМЕЛЬЕ?\n\n"
        f"Ты уверен, что хочешь покинуть подземелье?\n\n"
        f"📦 Ты выносишь:\n{loot_text}\n\n"
        f"Вернуться в забег с этого момента будет нельзя.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Да, выйти", callback_data="dungeon:exit:confirm")],
            [InlineKeyboardButton(text="↩️ Нет, остаться", callback_data="dungeon:exit:cancel")],
        ])
    )


@router.callback_query(F.data == "dungeon:exit:confirm")
async def dungeon_exit_confirm(callback: CallbackQuery, state: FSMContext):
    """Фактический выход: перенос лута, начисление НМ, завершение забега."""
    await callback.answer()
    user_id = callback.from_user.id
    run = await get_active_run(user_id)
    if not run:
        await callback.message.answer("❌ Подземелье не найдено.")
        await state.clear()
        return

    loot_nm = run['loot_nm'] or 0
    items = await transfer_run_items_to_inventory(user_id, run['id'])
    if loot_nm > 0:
        await add_nordmarks(user_id, loot_nm, "dungeon_exit", "Вынесено из подземелья")
    await end_run(run['id'], 0)
    await log_activity(user_id, "dungeon_exit", "Покинул подземелье (досрочный выход)")

    parts = []
    if loot_nm > 0:
        parts.append(f"💰 {loot_nm} Нордмарок")
    parts.extend(f"🎁 {n} x{q}" for n, q in items)

    if parts:
        text = "📦 Ты выносишь из подземелья:\n" + "\n".join(parts) + "\n\nТы покидаешь подземелье."
    else:
        text = "Ты покидаешь подземелье ни с чем."

    await callback.message.answer(text + "\n\nВойти снова?", reply_markup=dungeon_start_keyboard())
    await state.clear()


@router.callback_query(F.data == "dungeon:exit:cancel")
async def dungeon_exit_cancel(callback: CallbackQuery, state: FSMContext):
    """Отмена выхода — возврат к текущему экрану подземелья."""
    await callback.answer("Продолжаем подземелье!", show_alert=False)
    user_id = callback.from_user.id
    run = await get_active_run(user_id)
    if not run:
        await callback.message.answer("❌ Подземелье не найдено.")
        await state.clear()
        return
    await resume_dungeon(callback.message, run, user_id, state)
