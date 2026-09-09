import os
import random
import json
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from database.db import (
    get_all_dungeons, get_dungeon, get_floor_enemies, start_dungeon_run,
    get_active_run, update_run_hp, advance_room, end_run, add_run_item,
    get_run_items, clear_run_items, get_user, add_nordmarks, remove_nordmarks, remove_ap, get_db,
    get_player_weapon_damage, get_user_potions, get_item_by_name, remove_inventory_item,
    get_user_contract_count, get_player_armor, add_inventory_item,
    transfer_run_items_to_inventory, get_equipment_slot_items, log_activity,
)
from utils.combat import (
    calculate_attack, calculate_enemy_damage,
    escape_chance, calculate_escape_damage, room_type_roll, resource_amount,
    _hp_bar,
)
from utils.notify import notify, player_display


class DungeonFSM(StatesGroup):
    in_dungeon = State()
    in_combat = State()
    in_boss = State()
    confirm_enter = State()


router = Router()


async def dungeon_current_step(state: FSMContext) -> int:
    """Текущий шаг подземелья (для защиты от повторного нажатия старых кнопок)."""
    data = await state.get_data()
    return int(data.get('dungeon_step', 0) or 0)


async def dungeon_new_step(state: FSMContext) -> int:
    """Выдаёт следующий шаг и сохраняет его в FSM (новая кнопка перебивает старые)."""
    step = await dungeon_current_step(state) + 1
    await state.update_data(dungeon_step=step)
    return step


def dungeon_main_keyboard(step: int = 0):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏃 Продолжить путь", callback_data=f"dungeon:continue:{step}")],
        [InlineKeyboardButton(text="🚪 Выйти из подземелья", callback_data="dungeon:exit")],
    ])


def _slot_button_label(row):
    if row['cure_poison']:
        return "⚗️ Антидот"
    if row['heal'] > 0:
        return f"💊 {row['name']}"
    return f"🧪 {row['name']}"


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


def dungeon_start_keyboard():
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎫 Войти (1 контракт)", callback_data="dungeon:enter")],
        [InlineKeyboardButton(text="🏠 В меню города", callback_data="city:menu")],
    ])


def contract_missing_keyboard():
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏰 К списку подземелий", callback_data="city:dungeon")],
        [InlineKeyboardButton(text="🏠 В меню города", callback_data="city:menu")],
    ])


async def answer_enemy_photo(where, enemy, text, reply_markup=None):
    """Отправляет сообщение с фото врага; если файла нет — падает на текстовое."""
    image = enemy['image'] if 'image' in enemy.keys() and enemy['image'] else None
    if image and os.path.isfile(image):
        return await where.answer_photo(photo=FSInputFile(image), caption=text, reply_markup=reply_markup)
    return await where.answer(text, reply_markup=reply_markup)


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
            item = await get_item_by_name(d.get('item', ''))
            if item:
                qty = max(1, int(d.get('qty', 1)))
                await add_run_item(run_id, item['id'], qty)
                dropped.append((item['name'], qty))
    return dropped


@router.callback_query(F.data == "city:dungeon")
async def dungeon_entry(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    user_id = callback.from_user.id
    active = await get_active_run(user_id)

    if active:
        await show_room(callback.message, active, user_id, state)
        return

    dungeons = await get_all_dungeons()
    if not dungeons:
        await callback.message.answer("❌ Подземелий пока нет.")
        return

    text = "🏰 ПОДЗЕМЕЛЬЯ\n\n"
    for d in dungeons:
        text += f"⚔️ {d['name']}\n{d['description']}\nЭтажей: {d['floors_count']}\n\n"

    contracts = await get_user_contract_count(user_id)
    text += f"🎫 Контрактов на зачистку: {contracts}\n(покупаются в магазине, доступно Ветеранам)"

    await callback.message.answer(text, reply_markup=dungeon_start_keyboard())


@router.callback_query(F.data == "dungeon:enter")
async def dungeon_enter(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    user_id = callback.from_user.id
    dungeons = await get_all_dungeons()
    if not dungeons:
        return

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

    dungeon = dungeons[0]
    await state.update_data(dungeon_id=dungeon['id'])
    await state.set_state(DungeonFSM.confirm_enter)
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    await callback.message.answer(
        f"⚠️ ЗА ПОПЫТКУ ВХОДА БУДУТ СПИСАНЫ:\n\n"
        f"🎫 1 «Контракт на зачистку» (у тебя: {contracts})\n"
        f"⚡ 30 очков действий (у тебя: {user['ap']})\n\n"
        f"Эти ресурсы потратятся сразу, даже если ты выйдешь из подземелья. Продолжить?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Да, войти", callback_data="dungeon:enter:confirm")],
            [InlineKeyboardButton(text="↩️ Отмена", callback_data="city:dungeon")],
        ])
    )


@router.callback_query(F.data == "dungeon:enter:confirm")
async def dungeon_enter_confirm(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    user_id = callback.from_user.id
    data = await state.get_data()
    dungeon_id = data.get('dungeon_id')
    dungeon = await get_dungeon(dungeon_id) if dungeon_id else None
    if not dungeon:
        dungeon = (await get_all_dungeons() or [None])[0]
        if not dungeon:
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

    ok = await remove_ap(user_id, 30)
    if not ok:
        await state.clear()
        await callback.message.answer("❌ Не удалось списать очки действий.")
        return

    await start_dungeon_run(user_id, dungeon['id'])
    run = await get_active_run(user_id)
    await log_activity(user_id, "dungeon_enter", f"Вошел в «{dungeon['name']}»")

    await callback.message.answer(
        f"🎫 Контракт использован! ⚡ −30 AP за вход\n"
        f"🏰 {dungeon['name']}\n"
        f"Этаж 1 | Комната 0/10\n"
        f"❤️ {_hp_bar(run['hp'], run['hp_max'])}\n\n"
        f"Ты входишь в подземелье...",
    )
    await state.set_state(DungeonFSM.in_dungeon)
    await show_room(callback.message, run, user_id, state)


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
        await callback.message.answer("⚠️ Это устаревшая кнопка. Открой подземелье заново и продолжай с последнего сообщения.")
        return

    if run['room_number'] >= 10:
        await show_boss(callback.message, run, user_id, state)
        return

    await advance_room(run['id'])
    run = await get_active_run(user_id)
    await show_room(callback.message, run, user_id, state)


async def show_room(message, run, user_id, state: FSMContext):
    dungeon = await get_dungeon(run['dungeon_id'])
    room_type = room_type_roll()
    hp_text = _hp_bar(run['hp'], run['hp_max'])
    slot_items = await get_equipment_slot_items(user_id)
    poison = (await state.get_data()).get('active_poison')
    step = await dungeon_new_step(state)

    if room_type == "enemy":
        enemies = await get_floor_enemies(run['dungeon_id'], run['floor'])
        non_boss = [e for e in enemies if not e['is_boss']]
        enemy = random.choice(non_boss) if non_boss else random.choice(enemies)

        await state.update_data(current_enemy_id=enemy['id'], current_enemy_hp=enemy['hp'])

        poison_line = f"☠️ Ты отравлен! Яд: −{poison} HP каждый ход\n" if poison else ""
        text = (
            f"🏰 {dungeon['name']}\n"
            f"Этаж {run['floor']} | Комната {run['room_number']}/10\n"
            f"❤️ {hp_text}\n"
            f"{poison_line}\n"
            f"⚠️ Ты входишь в комнату и видишь врага!\n"
            f"👾 {enemy['name']} (HP: {enemy['hp']}, АТК: {enemy['attack']})\n\n"
            f"Что делаешь?"
        )
        await answer_enemy_photo(message, enemy, text, reply_markup=dungeon_combat_keyboard(enemy['id'], slot_items, step))

    elif room_type == "resource":
        nm = resource_amount(run['floor'])
        await add_nordmarks(user_id, nm, "dungeon_loot", "Найдено в подземелье")

        text = (
            f"🏰 {dungeon['name']}\n"
            f"Этаж {run['floor']} | Комната {run['room_number']}/10\n"
            f"❤️ {hp_text}\n\n"
            f"📦 Ты нашёл хранилище с припасами!\n"
            f"+{nm} Нордмарок\n\n"
            f"Нажми «Продолжить путь» чтобы идти дальше."
        )
        await message.answer(text, reply_markup=dungeon_main_keyboard(step))

    else:
        text = (
            f"🏰 {dungeon['name']}\n"
            f"Этаж {run['floor']} | Комната {run['room_number']}/10\n"
            f"❤️ {hp_text}\n\n"
            f"🪨 Комната пуста. Здесь ничего нет.\n\n"
            f"Нажми «Продолжить путь» чтобы идти дальше."
        )
        await message.answer(text, reply_markup=dungeon_main_keyboard(step))


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

    # Тик яда в начале хода игрока
    if poison:
        player_hp = max(0, player_hp - poison)
        await update_run_hp(run['id'], player_hp)
        if player_hp <= 0:
            nm_penalty = max(5, enemy['reward_nm'] * 2)
            await remove_nordmarks(user_id, nm_penalty, "dungeon_death", "Штраф за смерть в подземелье")
            text = (
                f"☠️ Яд погубил тебя (−{poison} HP)\n"
                f"💀 Ты погиб! −{nm_penalty} Нордмарок штраф.\nСобранный лут потерян."
            )
            await end_run(run['id'], 0)
            await state.clear()
            await answer_enemy_photo(callback.message, enemy, text, reply_markup=dungeon_start_keyboard())
            return

    weapon_damage = await get_player_weapon_damage(user_id)
    damage_to_enemy = calculate_attack(0, weapon_damage)
    from utils.states import get_state_info, combat_multipliers
    state_info = await get_state_info(user_id)
    mult = combat_multipliers(state_info['name'])
    am = mult.get('attack_mult', 1.0)
    damage_to_enemy = max(1, int(damage_to_enemy * am))
    current_enemy_hp = max(0, current_enemy_hp - damage_to_enemy)
    await state.update_data(current_enemy_hp=current_enemy_hp)

    if current_enemy_hp <= 0:
        if enemy['is_boss']:
            await add_nordmarks(user_id, enemy['reward_nm'], "dungeon_kill", f"Убил босса {enemy['name']}")
            text = (
                f"🏆 БОСС ПОБЕЖДЁН!\n"
                f"💀 {enemy['name']} повержен!\n"
                f"+{enemy['reward_nm']} Нордмарок"
            )

            boss_dropped = await roll_enemy_drops(run['id'], enemy)
            if boss_dropped:
                text += "\n\n🎁 Лут:\n" + "\n".join(f"• {name} x{qty}" for name, qty in boss_dropped)

            text += "\n\n🎉 Поздравляем! Ты прошёл подземелье!"

            transferred = await transfer_run_items_to_inventory(user_id, run['id'])
            if transferred:
                items_text = "\n".join([f"• {n} x{q}" for n, q in transferred])
                text += f"\n\n📦 Найденные предметы отправлены в инвентарь:\n{items_text}"

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
        return

    from utils.combat import get_enemy_bar
    enemy_bar = get_enemy_bar(current_enemy_hp, enemy['hp'])
    text = (
        f"🗡️ Ты атакуешь {enemy['name']}!\n"
        f"−{damage_to_enemy} HP врагу\n"
        f"{enemy_bar}\n\n"
    )

    enemy_dmg = calculate_enemy_damage(enemy['attack'])
    armor = await get_player_armor(user_id)
    reduced = max(1, enemy_dmg - armor)
    blocked_line = f"\n🛡️ Броня поглотила {enemy_dmg - reduced} урона!" if armor > 0 and reduced < enemy_dmg else ""
    player_hp = max(0, player_hp - reduced)
    await update_run_hp(run['id'], player_hp)

    from utils.combat import get_enemy_attack_text
    text += get_enemy_attack_text(enemy['name'], reduced, player_hp) + blocked_line

    # Навесить яд при укусе врага
    pc = enemy['poison_chance'] if 'poison_chance' in enemy.keys() else 0
    poison_just_applied = False
    if pc and enemy['poison_dmg'] and random.randint(1, 100) <= pc:
        await state.update_data(active_poison=enemy['poison_dmg'])
        text += f"\n☠️ {enemy['name']} отравил тебя! Яд: −{enemy['poison_dmg']} HP каждый ход."
        poison_just_applied = True

    # Показывать текущий статус отравления, пока игрок не снял его антидотом
    data_after = await state.get_data()
    active_poison = data_after.get('active_poison')
    if active_poison and not poison_just_applied:
        text += f"\n☠️ Ты отравлен! Яд: −{active_poison} HP каждый ход."

    if player_hp <= 0:
        nm_penalty = max(5, enemy['reward_nm'] * 2)
        await remove_nordmarks(user_id, nm_penalty, "dungeon_death", "Штраф за смерть в подземелье")
        text += f"\n\n💀 Ты погиб! −{nm_penalty} Нордмарок штраф.\nСобранный лут потерян."
        await end_run(run['id'], 0)
        await state.clear()
        await log_activity(user_id, "dungeon_death", f"Погиб в подземелье от «{enemy['name']}»")
        await answer_enemy_photo(callback.message, enemy, text, reply_markup=dungeon_start_keyboard())
    else:
        slot_items = await get_equipment_slot_items(user_id)
        next_step = await dungeon_new_step(state)
        await answer_enemy_photo(callback.message, enemy, text, reply_markup=dungeon_combat_keyboard(enemy['id'], slot_items, next_step))


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
        await callback.message.answer("⚠️ Это устаревшая кнопка. Используй кнопки из последнего сообщения боя.")
        return

    run = await get_active_run(user_id)
    if not run:
        await callback.message.answer("❌ Подземелье не найдено.")
        await state.clear()
        return

    item = None
    for s, row in await get_equipment_slot_items(user_id):
        if s == slot:
            item = row
            break
    if not item:
        await callback.message.answer("❌ Этот слот пуст.")
        return

    if item['cure_poison'] and not data.get('active_poison'):
        await callback.message.answer("Ты не отравлен, антидот бесполезен.")
        return

    if item['heal'] > 0 and run['hp'] >= run['hp_max']:
        await callback.message.answer("❤️ HP уже полное, зелье не нужно.")
        return

    ok = await remove_inventory_item(user_id, item['id'], 1)
    if not ok:
        await callback.message.answer("❌ Не удалось списать предмет.")
        return

    enemy_id = data.get('current_enemy_id')
    is_boss = False
    if enemy_id is not None:
        conn = await get_db()
        cursor = await conn.execute("SELECT is_boss FROM dungeon_enemies WHERE id = ?", (enemy_id,))
        erow = await cursor.fetchone()
        is_boss = bool(erow and erow['is_boss'])

    slot_items = await get_equipment_slot_items(user_id)

    if item['cure_poison']:
        await state.update_data(active_poison=None)
        text = (
            f"⚗️ {item['name']} применён: отравление снято!\n"
            f"Продолжай бой:"
        )
    elif item['heal'] > 0:
        new_hp = min(run['hp_max'], run['hp'] + item['heal'])
        await update_run_hp(run['id'], new_hp)
        text = (
            f"💊 {item['name']} применено: +{item['heal']} HP!\n"
            f"❤️ {_hp_bar(new_hp, run['hp_max'])}\n\n"
            f"Продолжай бой:"
        )
    else:
        await add_inventory_item(user_id, item['id'], 1)
        await callback.message.answer("❌ Этот предмет нельзя использовать в бою.")
        return

    next_step = await dungeon_new_step(state)
    if is_boss:
        await callback.message.answer(text, reply_markup=dungeon_boss_keyboard(enemy_id, slot_items, next_step))
    else:
        await callback.message.answer(text, reply_markup=dungeon_combat_keyboard(enemy_id, slot_items, next_step))


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

    hp_percent = run['hp'] / run['hp_max'] if run['hp_max'] > 0 else 1.0

    if escape_chance(hp_percent):
        next_step = await dungeon_new_step(state)
        text = (
            f"🏃 Ты успешно убежал от {enemy['name']}!\n"
            f"Нажми «Продолжить путь» чтобы идти дальше."
        )
        await callback.message.answer(text, reply_markup=dungeon_main_keyboard(next_step))
    else:
        penalty = calculate_escape_damage()
        player_hp = max(0, run['hp'] - penalty)
        await update_run_hp(run['id'], player_hp)

        text = (
            f"❌ Не удалось убежать!\n"
            f"−{penalty} HP (штрафной удар)\n"
            f"❤️ {_hp_bar(player_hp, run['hp_max'])}\n\n"
            f"Ты продолжаешь бой с {enemy['name']}."
        )

        if player_hp <= 0:
            nm_penalty = max(5, enemy['reward_nm'] * 2)
            await remove_nordmarks(user_id, nm_penalty, "dungeon_death", "Штраф за смерть в подземелье")
            text += f"\n\n💀 Ты погиб! −{nm_penalty} Нордмарок штраф.\nСобранный лут потерян."
            await end_run(run['id'], 0)
            await state.clear()
            await log_activity(user_id, "dungeon_death", f"Погиб от босса в подземелье")
            await answer_enemy_photo(callback.message, enemy, text, reply_markup=dungeon_start_keyboard())
        else:
            slot_items = await get_equipment_slot_items(user_id)
            next_step = await dungeon_new_step(state)
            await answer_enemy_photo(callback.message, enemy, text, reply_markup=dungeon_combat_keyboard(enemy['id'], slot_items, next_step))


async def show_boss(message, run, user_id, state: FSMContext):
    enemies = await get_floor_enemies(run['dungeon_id'], run['floor'])
    boss_list = [e for e in enemies if e['is_boss']]
    if not boss_list:
        await message.answer("❌ Босс не найден.")
        return

    boss = boss_list[0]
    hp_text = _hp_bar(run['hp'], run['hp_max'])
    slot_items = await get_equipment_slot_items(user_id)
    poison = (await state.get_data()).get('active_poison')
    step = await dungeon_new_step(state)

    await state.update_data(current_enemy_id=boss['id'], current_enemy_hp=boss['hp'])

    poison_line = f"☠️ Ты отравлен! Яд: −{poison} HP каждый ход\n" if poison else ""
    text = (
        f"💀 КОМНАТА БОССА\n"
        f"Этаж {run['floor']} | БОСС\n"
        f"❤️ {hp_text}\n"
        f"{poison_line}\n"
        f"💀 {boss['name']} (HP: {boss['hp']}, АТК: {boss['attack']})\n\n"
        f"⚠️ Это решающий бой! Убежать нельзя!"
    )
    await answer_enemy_photo(message, boss, text, reply_markup=dungeon_boss_keyboard(boss['id'], slot_items, step))
    await state.set_state(DungeonFSM.in_boss)


@router.callback_query(F.data == "dungeon:exit")
async def dungeon_exit(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    user_id = callback.from_user.id
    run = await get_active_run(user_id)
    if run:
        items = await transfer_run_items_to_inventory(user_id, run['id'])
        await end_run(run['id'], 0)
        await log_activity(user_id, "dungeon_exit", "Покинул подземелье (досрочный выход)")

        if items:
            text = "📦 Ты забрал с собой и получил в инвентарь:\n"
            for n, q in items:
                text += f"• {n} x{q}\n"
            text += "\nТы покидаешь подземелье."
        else:
            text = "Ты покидаешь подземелье ни с чем."

        await callback.message.answer(text + "\n\nВойти снова?", reply_markup=dungeon_start_keyboard())
    else:
        await callback.message.answer("Ты покидаешь подземелье.", reply_markup=dungeon_start_keyboard())
    await state.clear()
