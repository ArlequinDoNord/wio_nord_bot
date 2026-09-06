import os
import random
import json
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from database.db import (
    get_all_dungeons, get_dungeon, get_floor_enemies, start_dungeon_run,
    get_active_run, update_run_hp, advance_room, end_run, add_run_item,
    get_run_items, clear_run_items, get_user, add_nordmarks, remove_nordmarks, remove_ap, get_db,
    get_player_weapon_damage, get_user_potions, get_item_by_name, remove_inventory_item,
    get_user_contract_count,
)
from utils.combat import (
    calculate_attack, calculate_enemy_damage,
    escape_chance, calculate_escape_damage, room_type_roll, resource_amount,
    _hp_bar,
)


class DungeonFSM(StatesGroup):
    in_dungeon = State()
    in_combat = State()
    in_boss = State()


router = Router()


def dungeon_main_keyboard():
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏃 Продолжить путь", callback_data="dungeon:continue")],
        [InlineKeyboardButton(text="🚪 Выйти из подземелья", callback_data="dungeon:exit")],
    ])


def dungeon_combat_keyboard(enemy_id: int, potions: int = 0):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    buttons = [
        [InlineKeyboardButton(text="🗡️ Атаковать", callback_data=f"dungeon:attack:{enemy_id}")],
    ]
    if potions > 0:
        buttons.append([InlineKeyboardButton(text=f"💊 Зелье здоровья x{potions}", callback_data="dungeon:potion")])
    buttons.append([InlineKeyboardButton(text="🏃 Попытаться убежать", callback_data=f"dungeon:escape:{enemy_id}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def dungeon_boss_keyboard(boss_id: int, potions: int = 0):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    buttons = [
        [InlineKeyboardButton(text="🗡️ Атаковать", callback_data=f"dungeon:attack:{boss_id}")],
    ]
    if potions > 0:
        buttons.append([InlineKeyboardButton(text=f"💊 Зелье здоровья x{potions}", callback_data="dungeon:potion")])
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

    contract = await get_item_by_name("Контракт на зачистку")
    ok = await remove_inventory_item(user_id, contract['id'], 1)
    if not ok:
        await callback.message.answer("❌ Не удалось списать контракт.")
        return

    ok = await remove_ap(user_id, 30)
    if not ok:
        await callback.message.answer("❌ Не удалось списать очки действий.")
        return

    dungeon = dungeons[0]
    await start_dungeon_run(user_id, dungeon['id'])
    run = await get_active_run(user_id)

    await callback.message.answer(
        f"🎫 Контракт использован! ⚡ −30 AP за вход\n"
        f"🏰 {dungeon['name']}\n"
        f"Этаж 1 | Комната 0/10\n"
        f"❤️ {_hp_bar(run['hp'], run['hp_max'])}\n\n"
        f"Ты входишь в подземелье...",
    )
    await state.set_state(DungeonFSM.in_dungeon)
    await show_room(callback.message, run, user_id, state)


@router.callback_query(F.data == "dungeon:continue")
async def dungeon_continue(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    user_id = callback.from_user.id
    run = await get_active_run(user_id)
    if not run:
        await callback.message.answer("❌ Активное подземелье не найдено.")
        await state.clear()
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
    potions = await count_potions(user_id)

    if room_type == "enemy":
        enemies = await get_floor_enemies(run['dungeon_id'], run['floor'])
        non_boss = [e for e in enemies if not e['is_boss']]
        enemy = random.choice(non_boss) if non_boss else random.choice(enemies)

        await state.update_data(current_enemy_id=enemy['id'], current_enemy_hp=enemy['hp'])

        text = (
            f"🏰 {dungeon['name']}\n"
            f"Этаж {run['floor']} | Комната {run['room_number']}/10\n"
            f"❤️ {hp_text}\n\n"
            f"⚠️ Ты входишь в комнату и видишь врага!\n"
            f"👾 {enemy['name']} (HP: {enemy['hp']}, АТК: {enemy['attack']})\n\n"
            f"Что делаешь?"
        )
        await answer_enemy_photo(message, enemy, text, reply_markup=dungeon_combat_keyboard(enemy['id'], potions))

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
        await message.answer(text, reply_markup=dungeon_main_keyboard())

    else:
        text = (
            f"🏰 {dungeon['name']}\n"
            f"Этаж {run['floor']} | Комната {run['room_number']}/10\n"
            f"❤️ {hp_text}\n\n"
            f"🪨 Комната пуста. Здесь ничего нет.\n\n"
            f"Нажми «Продолжить путь» чтобы идти дальше."
        )
        await message.answer(text, reply_markup=dungeon_main_keyboard())


@router.callback_query(F.data.startswith("dungeon:attack:"))
async def dungeon_attack(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    user_id = callback.from_user.id
    run = await get_active_run(user_id)
    if not run:
        await callback.message.answer("❌ Подземелье не найдено.")
        await state.clear()
        return

    enemy_id = int(callback.data.split(":")[2])
    conn = await get_db()
    cursor = await conn.execute("SELECT * FROM dungeon_enemies WHERE id = ?", (enemy_id,))
    enemy = await cursor.fetchone()
    if not enemy:
        return

    data = await state.get_data()
    current_enemy_hp = data.get('current_enemy_hp', enemy['hp'])

    weapon_damage = await get_player_weapon_damage(user_id)
    damage_to_enemy = calculate_attack(0, weapon_damage)
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

            run_items = await get_run_items(run['id'])
            if run_items:
                items_text = "\n".join([f"• {i['name']} x{i['quantity']}" for i in run_items])
                text += f"\n\n📦 Найденные предметы:\n{items_text}"

            await end_run(run['id'], 0)
            await state.clear()
            await answer_enemy_photo(callback.message, enemy, text, reply_markup=dungeon_start_keyboard())
        else:
            hp_text = _hp_bar(run['hp'], run['hp_max'])
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
            await answer_enemy_photo(callback.message, enemy, text, reply_markup=dungeon_main_keyboard())
        return

    from utils.combat import get_enemy_bar
    enemy_bar = get_enemy_bar(current_enemy_hp, enemy['hp'])
    text = (
        f"🗡️ Ты атакуешь {enemy['name']}!\n"
        f"−{damage_to_enemy} HP врагу\n"
        f"{enemy_bar}\n\n"
    )

    enemy_dmg = calculate_enemy_damage(enemy['attack'])
    player_hp = max(0, run['hp'] - enemy_dmg)
    await update_run_hp(run['id'], player_hp)

    from utils.combat import get_enemy_attack_text
    text += get_enemy_attack_text(enemy['name'], enemy_dmg, player_hp)

    if player_hp <= 0:
        nm_penalty = max(5, enemy['reward_nm'] * 2)
        await remove_nordmarks(user_id, nm_penalty, "dungeon_death", "Штраф за смерть в подземелье")
        text += f"\n\n💀 Ты погиб! −{nm_penalty} Нордмарок штраф.\nПредметы сохранены."
        await end_run(run['id'], 0)
        await state.clear()
        await answer_enemy_photo(callback.message, enemy, text, reply_markup=dungeon_start_keyboard())
    else:
        potions = await count_potions(user_id)
        await answer_enemy_photo(callback.message, enemy, text, reply_markup=dungeon_combat_keyboard(enemy['id'], potions))


@router.callback_query(F.data == "dungeon:potion")
async def dungeon_use_potion(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    user_id = callback.from_user.id
    run = await get_active_run(user_id)
    if not run:
        await callback.message.answer("❌ Подземелье не найдено.")
        await state.clear()
        return

    potions = await get_user_potions(user_id)
    if not potions:
        await callback.message.answer("💊 Зелий здоровья нет в инвентаре.")
        return

    if run['hp'] >= run['hp_max']:
        await callback.message.answer("❤️ HP уже полное, зелье не нужно.")
        return

    potion = potions[0]
    new_hp = min(run['hp_max'], run['hp'] + potion['heal'])
    await update_run_hp(run['id'], new_hp)

    ok = await remove_inventory_item(user_id, potion['id'], 1)
    if not ok:
        return

    data = await state.get_data()
    enemy_id = data.get('current_enemy_id')
    remaining = await count_potions(user_id)

    text = (
        f"💊 {potion['name']} применено: +{potion['heal']} HP!\n"
        f"❤️ {_hp_bar(new_hp, run['hp_max'])}\n\n"
        f"Продолжай бой:"
    )

    if enemy_id is not None:
        conn = await get_db()
        cursor = await conn.execute("SELECT is_boss FROM dungeon_enemies WHERE id = ?", (enemy_id,))
        enemy_row = await cursor.fetchone()
        if enemy_row and enemy_row['is_boss']:
            await callback.message.answer(text, reply_markup=dungeon_boss_keyboard(enemy_id, remaining))
            return

    await callback.message.answer(text, reply_markup=dungeon_combat_keyboard(enemy_id, remaining))


@router.callback_query(F.data.startswith("dungeon:escape:"))
async def dungeon_escape(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    user_id = callback.from_user.id
    run = await get_active_run(user_id)
    if not run:
        await state.clear()
        return

    enemy_id = int(callback.data.split(":")[2])
    conn = await get_db()
    cursor = await conn.execute("SELECT * FROM dungeon_enemies WHERE id = ?", (enemy_id,))
    enemy = await cursor.fetchone()
    if not enemy:
        return

    hp_percent = run['hp'] / run['hp_max'] if run['hp_max'] > 0 else 1.0

    if escape_chance(hp_percent):
        text = (
            f"🏃 Ты успешно убежал от {enemy['name']}!\n"
            f"Нажми «Продолжить путь» чтобы идти дальше."
        )
        await callback.message.answer(text, reply_markup=dungeon_main_keyboard())
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
            text += f"\n\n💀 Ты погиб! −{nm_penalty} Нордмарок штраф.\nПредметы сохранены."
            await end_run(run['id'], 0)
            await state.clear()
            await answer_enemy_photo(callback.message, enemy, text, reply_markup=dungeon_start_keyboard())
        else:
            potions = await count_potions(user_id)
            await answer_enemy_photo(callback.message, enemy, text, reply_markup=dungeon_combat_keyboard(enemy['id'], potions))


async def show_boss(message, run, user_id, state: FSMContext):
    enemies = await get_floor_enemies(run['dungeon_id'], run['floor'])
    boss_list = [e for e in enemies if e['is_boss']]
    if not boss_list:
        await message.answer("❌ Босс не найден.")
        return

    boss = boss_list[0]
    hp_text = _hp_bar(run['hp'], run['hp_max'])
    potions = await count_potions(user_id)

    await state.update_data(current_enemy_id=boss['id'], current_enemy_hp=boss['hp'])

    text = (
        f"💀 КОМНАТА БОССА\n"
        f"Этаж {run['floor']} | БОСС\n"
        f"❤️ {hp_text}\n\n"
        f"💀 {boss['name']} (HP: {boss['hp']}, АТК: {boss['attack']})\n\n"
        f"⚠️ Это решающий бой! Убежать нельзя!"
    )
    await answer_enemy_photo(message, boss, text, reply_markup=dungeon_boss_keyboard(boss['id'], potions))
    await state.set_state(DungeonFSM.in_boss)


@router.callback_query(F.data == "dungeon:exit")
async def dungeon_exit(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    user_id = callback.from_user.id
    run = await get_active_run(user_id)
    if run:
        items = await get_run_items(run['id'])
        await end_run(run['id'], 0)
        await clear_run_items(run['id'])

        if items:
            text = "📦 Ты забрал с собой:\n"
            for i in items:
                text += f"• {i['name']} x{i['quantity']}\n"
            text += "\nТы покидаешь подземелье."
        else:
            text = "Ты покидаешь подземелье ни с чем."

        await callback.message.answer(text + "\n\nВойти снова?", reply_markup=dungeon_start_keyboard())
    else:
        await callback.message.answer("Ты покидаешь подземелье.", reply_markup=dungeon_start_keyboard())
    await state.clear()
