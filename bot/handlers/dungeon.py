import random
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from database.db import (
    get_all_dungeons, get_dungeon, get_floor_enemies, start_dungeon_run,
    get_active_run, update_run_hp, advance_room, end_run, add_run_item,
    get_run_items, clear_run_items, get_user, add_nordmarks, remove_nordmarks, get_db,
    get_player_weapon_damage,
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


def dungeon_combat_keyboard(enemy_id: int):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🗡️ Атаковать", callback_data=f"dungeon:attack:{enemy_id}")],
        [InlineKeyboardButton(text="🏃 Попытаться убежать", callback_data=f"dungeon:escape:{enemy_id}")],
    ])


def dungeon_boss_keyboard(boss_id: int):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🗡️ Атаковать", callback_data=f"dungeon:attack:{boss_id}")],
    ])


def dungeon_start_keyboard():
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚔️ Войти в подземелье", callback_data="dungeon:enter")],
        [InlineKeyboardButton(text="🏠 Назад", callback_data="back:main")],
    ])


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

    await callback.message.answer(text, reply_markup=dungeon_start_keyboard())


@router.callback_query(F.data == "dungeon:enter")
async def dungeon_enter(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    user_id = callback.from_user.id
    dungeons = await get_all_dungeons()
    if not dungeons:
        return

    dungeon = dungeons[0]
    await start_dungeon_run(user_id, dungeon['id'])
    run = await get_active_run(user_id)

    await callback.message.answer(
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
        await message.answer(text, reply_markup=dungeon_combat_keyboard(enemy['id']))

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
        await add_nordmarks(user_id, enemy['reward_nm'], "dungeon_kill", f"Убил {enemy['name']}")

        if enemy['is_boss']:
            text = (
                f"🏆 БОСС ПОБЕЖДЁН!\n"
                f"💀 {enemy['name']} повержен!\n"
                f"+{enemy['reward_nm']} Нордмарок\n\n"
                f"🎉 Поздравляем! Ты прошёл подземелье!"
            )

            conn2 = await get_db()
            cursor2 = await conn2.execute(
                "SELECT * FROM dungeon_items WHERE dungeon_id = ? AND floor = ?",
                (run['dungeon_id'], run['floor'])
            )
            floor_items = await cursor2.fetchall()
            for fi in floor_items:
                if random.random() < fi['drop_chance']:
                    await add_run_item(run['id'], fi['item_id'])

            run_items = await get_run_items(run['id'])
            if run_items:
                items_text = "\n".join([f"• {i['name']} x{i['quantity']}" for i in run_items])
                text += f"\n\n📦 Найденные предметы:\n{items_text}"

            await end_run(run['id'], 0)
            await state.clear()
            await callback.message.answer(text, reply_markup=dungeon_start_keyboard())
        else:
            hp_text = _hp_bar(run['hp'], run['hp_max'])
            text = (
                f"🏆 {enemy['name']} повержен!\n"
                f"+{enemy['reward_nm']} Нордмарок\n\n"
                f"❤️ {hp_text}\n"
                f"Нажми «Продолжить путь» чтобы идти дальше."
            )
            await callback.message.answer(text, reply_markup=dungeon_main_keyboard())
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
        await callback.message.answer(text, reply_markup=dungeon_start_keyboard())
    else:
        await callback.message.answer(text, reply_markup=dungeon_combat_keyboard(enemy['id']))


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
            await callback.message.answer(text, reply_markup=dungeon_start_keyboard())
        else:
            await callback.message.answer(text, reply_markup=dungeon_combat_keyboard(enemy['id']))


async def show_boss(message, run, user_id, state: FSMContext):
    enemies = await get_floor_enemies(run['dungeon_id'], run['floor'])
    boss_list = [e for e in enemies if e['is_boss']]
    if not boss_list:
        await message.answer("❌ Босс не найден.")
        return

    boss = boss_list[0]
    hp_text = _hp_bar(run['hp'], run['hp_max'])

    await state.update_data(current_enemy_id=boss['id'], current_enemy_hp=boss['hp'])

    text = (
        f"💀 КОМНАТА БОССА\n"
        f"Этаж {run['floor']} | БОСС\n"
        f"❤️ {hp_text}\n\n"
        f"💀 {boss['name']} (HP: {boss['hp']}, АТК: {boss['attack']})\n\n"
        f"⚠️ Это решающий бой! Убежать нельзя!"
    )
    await message.answer(text, reply_markup=dungeon_boss_keyboard(boss['id']))
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

        await callback.message.answer(text)
    else:
        await callback.message.answer("Ты покидаешь подземелье.")
    await state.clear()
