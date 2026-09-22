"""Курс Выживания для Пилотов (К.В.П.) — тренировочный данж.

8 комнат: комнаты 0-6 — случайные (Ефрейтор / Водное препятствие / Верёвка),
комната 7 — Инструктор «Старший сержант». Вход бесплатный, препятствия стоят 5 ОД.
Лимит — 4 прохождения на пилота. Первое прохождение даёт награду
«Значок В.У.С.П.» (+2% урона в подземельях и в К.В.П. и +3% уклонения, постоянно).
"""

import os
import random

from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from database.db import (
    get_db, get_dungeon, get_kvp_dungeon, start_dungeon_run, get_active_run,
    advance_room, end_run, update_run_hp, add_run_nordmarks, add_nordmarks,
    transfer_run_items_to_inventory, get_user, remove_ap, get_player_weapon_damage,
    get_player_armor, get_player_dodge, get_award_bonus, get_player_armor_with_bonus,
    get_item_by_name, add_inventory_item, get_kvp_progress,
    increment_kvp_completions, mark_kvp_badge, mark_kvp_stick, grant_award,
    log_activity, KVP_BADGE_NAME, KVP_MAX_COMPLETIONS,
)
from utils.combat import (
    calculate_attack, calculate_enemy_damage, roll_dodge, _hp_bar,
    get_enemy_bar, get_enemy_attack_text,
)
from utils.states import get_state_info, combat_multipliers
from utils.notify import notify, player_display
from bot.handlers.dungeon import (
    dungeon_current_step, dungeon_new_step, dungeon_entrance_photo, answer_enemy_photo,
)

router = Router()

# ----- Константы курса -----
ROOM_TOTAL = 8              # всего комнат
BOSS_ROOM_INDEX = 7         # последняя комната — босс
ROOM_EFREITOR = "efreitor"
ROOM_WATER = "water"
ROOM_ROPE = "rope"
ROOM_BOSS = "boss"
ROOM_TYPES_POOL = [ROOM_EFREITOR, ROOM_WATER, ROOM_ROPE]
# Веса для random.choices: Ефрейтор встречается заметно чаще препятствий.
ROOM_TYPES_WEIGHTS = [0.5, 0.25, 0.25]

OD_ATTEMPT_COST = 5         # стоимость попытки преодоления препятствия
WATER_FAIL_CHANCE = 0.10    # вероятность срыва на водном препятствии
ROPE_FAIL_CHANCE = 0.20     # вероятность срыва на верёвке
NM_CHANCE = 0.30            # шанс дропа 2 НМ с врага
STICK_CHANCE = 0.15         # шанс дропа «Офицерского стека» с босса (один раз)

EFREITOR_NAME = "Ефрейтор"
BOSS_NAME = "Старший сержант"
STICK_NAME = "Офицерский стек"

# Допуск по снаряжению: на курс не пускают с овергиром (иначе врагов выносят за секунды).
WPN_MAX_DAMAGE = 1          # максимальный урон оружия для входа
ARMOR_MAX = 2               # максимальная защита брони для входа


class KvpFSM(StatesGroup):
    in_course = State()


# ----- Клавиатуры -----

def kvp_menu_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎯 Начать курс", callback_data="kvp:start")],
        [InlineKeyboardButton(text="🏠 В меню города", callback_data="city:menu")],
    ])


def kvp_resume_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="▶️ Продолжить забег", callback_data="kvp:resume")],
        [InlineKeyboardButton(text="🚪 Выйти из курса", callback_data="kvp:exit")],
        [InlineKeyboardButton(text="🏠 В меню города", callback_data="city:menu")],
    ])


def kvp_continue_keyboard(step: int = 0):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏃 Продолжить путь", callback_data=f"kvp:continue:{step}")],
        [InlineKeyboardButton(text="🚪 Выйти из курса", callback_data="kvp:exit")],
    ])


def kvp_combat_keyboard(enemy_id: int, step: int = 0):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🗡️ Атаковать", callback_data=f"kvp:attack:{enemy_id}:{step}")],
    ])


def kvp_obstacle_keyboard(room_type: str, step: int = 0):
    if room_type == ROOM_WATER:
        label = "🌊 Перейти вброд (−5 ОД)"
    else:
        label = "🪢 Перейти по верёвке (−5 ОД)"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=label, callback_data=f"kvp:attempt:{room_type}:{step}")],
        [InlineKeyboardButton(text="🚪 Выйти из курса", callback_data="kvp:exit")],
    ])


# ----- Служебные -----

async def is_kvp_run(run) -> bool:
    """Активный забег принадлежит тренировочному данжу К.В.П.?"""
    if not run:
        return False
    dng = await get_dungeon(run['dungeon_id'])
    return bool(dng and dng['is_training'])


async def course_gear_block(user_id: int):
    """Текст отказа, если снаряжение превышает допуск курса, иначе None."""
    wpn = await get_player_weapon_damage(user_id)
    armor = await get_player_armor(user_id)
    issues = []
    if wpn > WPN_MAX_DAMAGE:
        issues.append(f"• оружие: урон {wpn} (макс. {WPN_MAX_DAMAGE})")
    if armor > ARMOR_MAX:
        issues.append(f"• броня: защита {armor} (макс. {ARMOR_MAX})")
    if not issues:
        return None
    return (
        "🎖️ На курс не пускают с тяжёлым снаряжением — это испытание для лёгкого снаряжения.\n"
        f"Допуск: оружие с уроном до {WPN_MAX_DAMAGE}, броня с защитой до {ARMOR_MAX}.\n"
        "Сними лишнее и попробуй снова:\n" + "\n".join(issues)
    )


async def get_course_enemy(name: str = EFREITOR_NAME, boss: bool = False):
    dng = await get_kvp_dungeon()
    if not dng:
        return None
    conn = await get_db()
    q = "SELECT * FROM dungeon_enemies WHERE dungeon_id = ? AND is_boss = ? AND name = ? LIMIT 1"
    cursor = await conn.execute(q, (dng['id'], int(boss), name))
    return await cursor.fetchone()


async def answer_course_photo(where, text, reply_markup=None):
    """Отправляет сообщение курса с входной картинкой данжа К.В.П. (photo_*).

    Админ задаёт картинки через менеджер подземелий; они же показываются
    на меню входа и внутри курса. Без картинки — обычный текст.
    """
    photo = await kvp_dungeon_photo()
    if photo:
        try:
            if os.path.isfile(photo):
                return await where.answer_photo(photo=FSInputFile(photo), caption=text,
                                                reply_markup=reply_markup)
            return await where.answer_photo(photo=photo, caption=text,
                                            reply_markup=reply_markup)
        except Exception:
            pass
    return await where.answer(text, reply_markup=reply_markup)


async def answer_enemy_or_course_photo(where, enemy, text, reply_markup=None):
    """Фото врага курса; без картинки врага — входная картинка курса, затем текст."""
    image = enemy['image'] if 'image' in enemy.keys() and enemy['image'] else None
    if image:
        return await answer_enemy_photo(where, enemy, text, reply_markup=reply_markup)
    return await answer_course_photo(where, text, reply_markup=reply_markup)


async def kvp_dungeon_photo():
    """Входная картинка данжа К.В.П. (file_id или локальный путь) или None."""
    dng = await get_kvp_dungeon()
    return dungeon_entrance_photo(dng) if dng else None


async def kvp_badge_award_id():
    conn = await get_db()
    cursor = await conn.execute("SELECT id FROM awards WHERE name = ?", (KVP_BADGE_NAME,))
    row = await cursor.fetchone()
    return row['id'] if row else None


def _course_header(run, title: str) -> str:
    room = run['room_number']
    if room >= BOSS_ROOM_INDEX:
        room_line = "КОМНАТА БОССА"
    else:
        room_line = f"Комната {room + 1}/{ROOM_TOTAL}"
    return (
        f"🎖️ КУРС ВЫЖИВАНИЯ ДЛЯ ПИЛОТОВ\n"
        f"{room_line}\n"
        f"❤️ {_hp_bar(run['hp'], run['hp_max'])}\n"
    )


# ----- Меню курса -----

async def kvp_menu_cb(callback: CallbackQuery):
    """Вход в локацию «Курс выживания»: описание, правила, прогресс."""
    await callback.answer()
    user_id = callback.from_user.id
    progress = await get_kvp_progress(user_id)
    dng = await get_kvp_dungeon()

    active = await get_active_run(user_id)
    in_run = await is_kvp_run(active)

    text = (
        f"🎖️ КУРС ВЫЖИВАНИЯ ДЛЯ ПИЛОТОВ (К.В.П.)\n"
        f"────────────────────────────\n"
        f"{dng['description'] if dng else 'Набор испытаний для пилотов ВВС Нордхайма.'}\n\n"
        f"⚙️ Правила:\n"
        f"• {ROOM_TOTAL} комнат: случайные препятствия и Инструктор.\n"
        f"• Допуск: оружие — урон до {WPN_MAX_DAMAGE}, броня — защита до {ARMOR_MAX}.\n"
        f"• Лимит прохождений: {progress['completions']}/{KVP_MAX_COMPLETIONS}.\n\n"
        f"📊 Прогресс курса: {progress['completions']}/{KVP_MAX_COMPLETIONS}"
    )

    if in_run:
        markup = kvp_resume_keyboard()
    elif progress['completions'] >= KVP_MAX_COMPLETIONS:
        await answer_course_photo(
            callback.message,
            text + "\n\n✅ Ты уже полностью прошёл курс. Возвращайся к своим прямым обязанностям.",
            reply_markup=None
        )
        return
    else:
        markup = kvp_menu_keyboard()

    await answer_course_photo(callback.message, text, markup)


@router.callback_query(F.data == "kvp:start")
async def kvp_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    user_id = callback.from_user.id
    progress = await get_kvp_progress(user_id)
    if progress['completions'] >= KVP_MAX_COMPLETIONS:
        await callback.message.answer(
            f"✅ Лимит курса исчерпан ({KVP_MAX_COMPLETIONS}/{KVP_MAX_COMPLETIONS})."
        )
        return

    dng = await get_kvp_dungeon()
    if not dng:
        await callback.message.answer("❌ Курс сейчас недоступен.")
        return

    block = await course_gear_block(user_id)
    if block:
        await callback.message.answer(block, reply_markup=kvp_menu_keyboard())
        return

    await start_dungeon_run(user_id, dng['id'])
    run = await get_active_run(user_id)
    await state.set_state(KvpFSM.in_course)
    await state.update_data(dungeon_id=dng['id'], kvp_room_type=None, kvp_in_boss=0)
    await log_activity(user_id, "kvp_start", f"Начал «{dng['name']}»")

    await callback.message.answer(
        f"🎖️ Ты входишь на полигон «Курс Выживания».\n\n"
        f"Впереди {ROOM_TOTAL} комнат. Босс — «{BOSS_NAME}». Удачи, пилот!"
    )
    await show_kvp_room(callback.message, run, user_id, state)


@router.callback_query(F.data == "kvp:resume")
async def kvp_resume(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    user_id = callback.from_user.id
    run = await get_active_run(user_id)
    if not run or not await is_kvp_run(run):
        await callback.message.answer("❌ Активного забега нет. Начни курс заново.",
                                      reply_markup=kvp_menu_keyboard())
        return
    block = await course_gear_block(user_id)
    if block:
        await callback.message.answer(block, reply_markup=kvp_menu_keyboard())
        return
    await state.set_state(KvpFSM.in_course)
    await show_kvp_room(callback.message, run, user_id, state)


# ----- Отрисовка комнаты -----

async def show_kvp_room(message, run, user_id, state: FSMContext):
    data = await state.get_data()
    room_type = data.get('kvp_room_type')

    # Босс — всегда последняя комната.
    if run['room_number'] >= BOSS_ROOM_INDEX:
        await show_boss_room(message, run, user_id, state, data.get('current_enemy_hp'))
        return

    if room_type not in ROOM_TYPES_POOL:
        room_type = random.choices(ROOM_TYPES_POOL, weights=ROOM_TYPES_WEIGHTS, k=1)[0]
        await state.update_data(kvp_room_type=room_type, kvp_in_boss=0)

    if room_type == ROOM_EFREITOR:
        await show_enemy_room(message, run, user_id, state)
    else:
        await show_obstacle_room(message, run, user_id, state, room_type)


async def show_enemy_room(message, run, user_id, state: FSMContext):
    enemy = await get_course_enemy(EFREITOR_NAME)
    if not enemy:
        await message.answer("❌ Ефрейтор не найден на курсе.")
        return
    data = await state.get_data()
    current_hp = data.get('current_enemy_hp')
    if current_hp is None:
        current_hp = enemy['hp']
    step = await dungeon_new_step(state)
    await state.update_data(current_enemy_id=enemy['id'], current_enemy_hp=current_hp,
                            kvp_room_type=ROOM_EFREITOR)
    text = (
        f"{_course_header(run, 'БОЙ')}\n"
        f"⚠️ Комната с Ефрейтором. Он смотрит угрюмо и без оружия — "
        f"проверка на умение убеждать.\n"
        f"👾 {enemy['name']} (HP: {enemy['hp']}, АТК: {enemy['attack']}, УКЛ: {enemy['dodge'] if 'dodge' in enemy.keys() else 0}%)\n\n"
        f"Что делаешь?"
    )
    await answer_enemy_or_course_photo(message, enemy, text,
                                    reply_markup=kvp_combat_keyboard(enemy['id'], step))


async def show_obstacle_room(message, run, user_id, state: FSMContext, room_type: str):
    if room_type == ROOM_WATER:
        icon, title, fail = "🌊", "Водное препятствие", WATER_FAIL_CHANCE
        desc = "Мутный брод. Если сорвёшься — вернёшься на этот же берег."
    else:
        icon, title, fail = "🪢", "Верёвочная переправа", ROPE_FAIL_CHANCE
        desc = "Туго натянутая верёвка над провалом. Одна ошибка — и ты снова здесь."
    step = await dungeon_new_step(state)
    text = (
        f"{_course_header(run, title)}\n"
        f"{icon} {title}!\n{desc}\n\n"
        f"Цена попытки: {OD_ATTEMPT_COST} ОД. Шанс срыва: {int(fail*100)}%.\n"
        f"При срыве попытаешься ещё раз (снова за ОД)."
    )
    await answer_obstacle_photo(message, room_type, text,
                                reply_markup=kvp_obstacle_keyboard(room_type, step))


async def answer_obstacle_photo(where, room_type: str, text, reply_markup=None):
    """Картинка комнаты-препятствия (photo_water/photo_rope); без неё — вход курса."""
    dng = await get_kvp_dungeon()
    photo = None
    if dng:
        photo = dng[f"photo_{room_type}"] if f"photo_{room_type}" in dng.keys() else None
    if photo:
        try:
            if os.path.isfile(photo):
                return await where.answer_photo(photo=FSInputFile(photo), caption=text,
                                                reply_markup=reply_markup)
            return await where.answer_photo(photo=photo, caption=text, reply_markup=reply_markup)
        except Exception:
            pass
    return await answer_course_photo(where, text, reply_markup=reply_markup)


async def show_boss_room(message, run, user_id, state: FSMContext, current_hp=None):
    boss = await get_course_enemy(BOSS_NAME, boss=True)
    if not boss:
        await message.answer("❌ Старший сержант не найден на курсе.")
        return
    data = await state.get_data()
    hp = current_hp
    if hp is None:
        hp = data.get('current_enemy_hp')
    if hp is None:
        hp = boss['hp']
    step = await dungeon_new_step(state)
    await state.update_data(current_enemy_id=boss['id'], current_enemy_hp=hp,
                            kvp_room_type=ROOM_BOSS, kvp_in_boss=1)
    text = (
        f"🎖️ {_course_header(run, 'БОСС')}\n"
        f"💀 КОМНАТА БОССА! В центре — «{boss['name']}» с «Офицерским стеком».\n"
        f"👾 {boss['name']} (HP: {boss['hp']}, АТК: {boss['attack']}, УКЛ: {boss['dodge'] if 'dodge' in boss.keys() else 0}%)\n\n"
        f"⚠️ Убежать с полигона нельзя — сдай экзамен!"
    )
    await answer_enemy_or_course_photo(message, boss, text,
                                    reply_markup=kvp_combat_keyboard(boss['id'], step))


# ----- Продолжить путь -----

@router.callback_query(F.data.startswith("kvp:continue:"))
async def kvp_continue(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    user_id = callback.from_user.id
    run = await get_active_run(user_id)
    if not run or not await is_kvp_run(run):
        await callback.message.answer("❌ Активный забег не найден.")
        await state.clear()
        return

    parts = callback.data.split(":")
    if len(parts) < 3 or int(parts[2]) != await dungeon_current_step(state):
        try:
            await log_activity(user_id, "stale_button", "КВП: устаревшая кнопка продолжения")
        except Exception:
            pass
        await callback.message.answer(
            "⚠️ Это устаревшая кнопка. Открой курс заново и продолжай с последнего сообщения."
        )
        return

    await advance_room(run['id'])
    run = await get_active_run(user_id)
    await state.update_data(kvp_room_type=None, kvp_in_boss=0,
                            current_enemy_id=None, current_enemy_hp=None)
    await show_kvp_room(callback.message, run, user_id, state)


# ----- Препятствие (вода / верёвка) -----

@router.callback_query(F.data.startswith("kvp:attempt:"))
async def kvp_attempt(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    user_id = callback.from_user.id
    run = await get_active_run(user_id)
    if not run or not await is_kvp_run(run):
        await callback.message.answer("❌ Активный забег не найден.")
        await state.clear()
        return

    parts = callback.data.split(":")
    if len(parts) < 3:
        await callback.message.answer("⚠️ Некорректная кнопка. Открой курс заново.")
        return
    room_type = parts[2]
    encoded_step = int(parts[3]) if len(parts) > 3 else 0

    if encoded_step != await dungeon_current_step(state):
        try:
            await log_activity(user_id, "stale_button", "КВП: устаревшая кнопка препятствия")
        except Exception:
            pass
        await callback.message.answer(
            "⚠️ Это устаревшая кнопка. Открой курс заново и продолжай с последнего сообщения."
        )
        return
    data = await state.get_data()
    if data.get('kvp_room_type') != room_type:
        await callback.message.answer("⚠️ Это препятствие уже позади.")
        return

    user = await get_user(user_id)
    if (user['ap'] or 0) < OD_ATTEMPT_COST:
        await callback.message.answer(
            f"⚡ Недостаточно очков действий: нужно {OD_ATTEMPT_COST} ОД, у тебя {user['ap']} ОД.\n"
            f"Очки восстанавливаются раз в сутки."
        )
        return

    ok = await remove_ap(user_id, OD_ATTEMPT_COST)
    if not ok:
        await callback.message.answer("❌ Не удалось списать очки действий.")
        return

    fail_chance = WATER_FAIL_CHANCE if room_type == ROOM_WATER else ROPE_FAIL_CHANCE
    icon = "🌊" if room_type == ROOM_WATER else "🪢"
    title = "водное препятствие" if room_type == ROOM_WATER else "верёвочную переправу"

    if random.random() < fail_chance:
        text = (
            f"{icon} Попытка преодолеть {title} сорвалась!\n"
            f"⚡ −{OD_ATTEMPT_COST} ОД\n\n"
            f"Ты вернулся на исходную позицию. Попробуй ещё раз."
        )
        await callback.message.answer(text)
        new_step = await dungeon_new_step(state)
        await callback.message.answer(
            f"{icon} {title.capitalize()}: новая попытка\n"
            f"Цена: {OD_ATTEMPT_COST} ОД. Шанс срыва: {int(fail_chance*100)}%.",
            reply_markup=kvp_obstacle_keyboard(room_type, new_step)
        )
        return

    text = (
        f"{icon} Ты успешно преодолел {title}!\n"
        f"⚡ −{OD_ATTEMPT_COST} ОД\n\n"
        f"Идти дальше?"
    )
    new_step = await dungeon_new_step(state)
    await callback.message.answer(text, reply_markup=kvp_continue_keyboard(new_step))


# ----- Бой -----

@router.callback_query(F.data.startswith("kvp:attack:"))
async def kvp_attack(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    user_id = callback.from_user.id
    run = await get_active_run(user_id)
    if not run or not await is_kvp_run(run):
        await callback.message.answer("❌ Активный забег не найден.")
        await state.clear()
        return

    block = await course_gear_block(user_id)
    if block:
        await callback.message.answer(block)
        return

    parts = callback.data.split(":")
    if len(parts) < 4:
        await callback.message.answer("⚠️ Некорректная кнопка. Открой курс заново.")
        return
    enemy_id = int(parts[2])
    encoded_step = int(parts[3])
    if encoded_step != await dungeon_current_step(state):
        try:
            await log_activity(user_id, "stale_button", "КВП: устаревшая кнопка боя")
        except Exception:
            pass
        await callback.message.answer(
            "⚠️ Это устаревшая кнопка. Используй кнопки из последнего сообщения боя."
        )
        return
    data = await state.get_data()
    cur_id = data.get('current_enemy_id')
    if cur_id is not None and cur_id != enemy_id:
        await callback.message.answer("⚠️ Этого врага уже нет в текущей комнате.")
        return

    conn = await get_db()
    cursor = await conn.execute("SELECT * FROM dungeon_enemies WHERE id = ?", (enemy_id,))
    enemy = await cursor.fetchone()
    if not enemy:
        await callback.message.answer("⚠️ Враг не найден. Открой курс заново.")
        return

    current_enemy_hp = data.get('current_enemy_hp')
    if current_enemy_hp is None:
        current_enemy_hp = enemy['hp']
    player_hp = run['hp']

    # Урон игрока
    weapon_damage = await get_player_weapon_damage(user_id)
    damage_to_enemy = calculate_attack(0, weapon_damage)
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

    # Враг повержен
    if current_enemy_hp <= 0:
        if enemy['is_boss']:
            await kvp_win(callback, run, user_id, state, bot, enemy)
            return

        text = f"🏆 Враг повержен!\n−{damage_to_enemy} HP, {enemy['name']} упал."
        if random.random() < NM_CHANCE:
            await add_run_nordmarks(run['id'], 2)
            text += "\n💰 +2 Нордмарки (заберёшь при выходе)"
        text += f"\n\n❤️ {_hp_bar(player_hp, run['hp_max'])}\nНажми «Продолжить путь»."
        new_step = await dungeon_new_step(state)
        await answer_course_photo(callback.message, text,
                                  reply_markup=kvp_continue_keyboard(new_step))
        return

    # Враг контратакует (с шансом пилот уклоняется)
    player_dodge = await get_player_dodge(user_id, mult.get('dodge_mult', 1.0))
    player_dodged = roll_dodge(player_dodge)
    enemy_dmg = calculate_enemy_damage(enemy['attack'])
    armor = await get_player_armor_with_bonus(user_id)
    blocked_line = ""
    if player_dodged:
        reduced = 0
        dodge_line = f"💨 Ты уклонился от атаки {enemy['name']}! (−0 HP)"
    else:
        reduced = max(1, enemy_dmg - armor)
        if armor > 0 and reduced < enemy_dmg:
            blocked_line = f"\n🛡️ Броня поглотила {enemy_dmg - reduced} урона!"
        dodge_line = ""
    player_hp = max(0, player_hp - reduced)
    await update_run_hp(run['id'], player_hp)

    if enemy_dodged:
        attack_line = f"💨 {enemy['name']} уклонился от удара! (−0 HP врагу)\n"
    else:
        attack_line = f"−{damage_to_enemy} HP врагу\n"
    enemy_bar = get_enemy_bar(current_enemy_hp, enemy['hp'])
    text = (
        f"🗡️ Ты атакуешь {enemy['name']}!\n"
        f"{attack_line}"
        f"{enemy_bar}\n\n"
    )
    if player_dodged:
        text += dodge_line
    else:
        text += get_enemy_attack_text(enemy['name'], reduced, player_hp) + blocked_line

    if player_hp <= 0:
        await end_run(run['id'], 0)
        await state.clear()
        await log_activity(user_id, "kvp_death", f"Погиб на курсе от «{enemy['name']}»")
        text += (
            f"\n\n💀 Ты погиб на полигоне. Курс — непройден, лут потерян.\n"
            f"Попробуешь ещё раз?"
        )
        await answer_course_photo(callback.message, text, reply_markup=kvp_menu_keyboard())
        return

    new_step = await dungeon_new_step(state)
    await answer_course_photo(callback.message, text,
                              reply_markup=kvp_combat_keyboard(enemy['id'], new_step))


async def kvp_win(callback: CallbackQuery, run, user_id, state: FSMContext, bot: Bot, boss):
    """Победа над Старшим сержантом: дроп, значок, завершение курса."""
    await callback.answer()

    # Нордмарки курса (лут копится в забеге)
    if random.random() < NM_CHANCE:
        await add_run_nordmarks(run['id'], 2)

    run = await get_active_run(user_id)
    loot_nm = run['loot_nm'] or 0
    transferred = await transfer_run_items_to_inventory(user_id, run['id'])
    if loot_nm > 0:
        await add_nordmarks(user_id, loot_nm, "kvp_win", "Вынесено с курса")

    # Дроп «Офицерского стека» — только один раз за пилота
    stick_line = ""
    progress = await get_kvp_progress(user_id)
    if not progress['stick_dropped'] and random.random() < STICK_CHANCE:
        stick = await get_item_by_name(STICK_NAME)
        if stick:
            await add_inventory_item(user_id, stick['id'], 1)
            await mark_kvp_stick(user_id)
            stick_line = f"\n💼 Дроп: «{STICK_NAME}» (оружие, урон 2)!"

    # Зачёт прохождения
    await increment_kvp_completions(user_id)
    progress = await get_kvp_progress(user_id)

    # Значок — при первом прохождении
    badge_line = ""
    if not progress['badge_awarded']:
        award_id = await kvp_badge_award_id()
        if award_id:
            granted, _ = await grant_award(user_id, award_id,
                                           comment="Пройден К.В.П. впервые")
            if granted:
                await mark_kvp_badge(user_id)
                badge_line = (
                    f"\n🎖️ Получена награда «{KVP_BADGE_NAME}»!\n"
                    f"Постоянный бонус: +2% урона и +3% уклонения в подземельях."
                )

    await end_run(run['id'], 0)
    await state.clear()
    await log_activity(user_id, "kvp_win", "Прошёл Курс Выживания для Пилотов")

    text = (
        f"🎖️ БОСС ПОБЕЖДЁН!\n"
        f"💀 «{BOSS_NAME}» сложил стек. Курс пройден!\n\n"
    )
    if loot_nm > 0:
        text += f"💰 Вынесено: {loot_nm} Нордмарок\n"
    for name, qty in transferred:
        text += f"🎁 {name} x{qty}\n"
    if stick_line:
        text += stick_line + "\n"
    if badge_line:
        text += badge_line + "\n"
    text += f"\n📊 Прогресс курса: {progress['completions']}/{KVP_MAX_COMPLETIONS}"

    await answer_course_photo(callback.message, text, reply_markup=kvp_menu_keyboard())

    pilot = await get_user(user_id)
    await notify(bot,
                 f"🎖️ Пилот {await player_display(pilot)} прошёл Курс Выживания и "
                 f"получил «{KVP_BADGE_NAME}»!",
                 user_id)


# ----- Выход -----

@router.callback_query(F.data == "kvp:exit")
async def kvp_exit(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    user_id = callback.from_user.id
    data = await state.get_data()
    if data.get('kvp_in_boss'):
        await callback.message.answer(
            "⚠️ Идёт бой с боссом! Убежать с полигона нельзя — это экзамен."
        )
        return

    run = await get_active_run(user_id)
    if run and await is_kvp_run(run):
        loot_nm = run['loot_nm'] or 0
        items = await transfer_run_items_to_inventory(user_id, run['id'])
        if loot_nm > 0:
            await add_nordmarks(user_id, loot_nm, "kvp_exit", "Вынесено с курса")
        await end_run(run['id'], 0)
        await log_activity(user_id, "kvp_exit", "Покинул К.В.П. досрочно")

        parts = []
        if loot_nm > 0:
            parts.append(f"💰 {loot_nm} Нордмарок")
        parts.extend(f"🎁 {n} x{q}" for n, q in items)

        if parts:
            text = "📦 Ты выносишь с курса:\n" + "\n".join(parts) + "\n\nТы покидаешь полигон."
        else:
            text = "Ты покидаешь полигон ни с чем."
    else:
        text = "Ты покидаешь курс."
    await state.clear()
    await callback.message.answer(text, reply_markup=kvp_menu_keyboard())