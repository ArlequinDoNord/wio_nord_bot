import os
import random
import json
import time
import asyncio
from utils.localization import t as _LT
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile, InputMediaPhoto
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
    log_location_visit,
    get_source_enemies, get_source_enemy_drops,
    roll_enemy_drops as roll_enemy_drops_db,
    enemy_encounter_hit, remove_ap_or_floor,
    bump_achievement, get_achievement_bonus,
)
from utils.combat import (
    calculate_attack, calculate_enemy_damage, roll_dodge,
    escape_chance, calculate_escape_damage, room_type_roll, resource_amount,
    _hp_bar,
)
from utils.helpers import (
    time_of_day_key, resolve_image,
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
from utils import onhit
from utils import effects
from config import (
    DUNGEON_HEAL_SOFT_LIMIT, DUNGEON_HEAL_HARD_LIMIT,
    DUNGEON_HEAL_SOFT_MULT, DUNGEON_HEAL_HARD_MULT,
    DUNGEON_SMOKE_MAX,
    FISH_AP_COST,
)
from config import RESERVOIR_AP_COST as RESERVOIR_AP_COST_CFG, FISH_BAIT_MISS_SEAWEED_CHANCE


# Достижения: ачивка «Эликсиры» считает применения зелий лечения (настоек),
# «Готовка» — бонус к лечению приготовленными блюдами (жареные блюда, пирог).
# Префиксы блюд продублированы из housing.FOOD_EXPIRY_PREFIXES (чтобы не тянуть
# целый модуль жилья в данж).
FOOD_DISH_PREFIXES = ("Жареный ", "Жареная ", "Жареное ", "Жареные ", "Рыбный ")
ELIXIR_ITEM_NAMES = ("Малая настойка здоровья", "Улучшенная настойка здоровья")


def heal_limit_mult(uses: int) -> float:
    """Множитель эффективности лечения: после 6-7 применений — -1/3, после 10 — -1/2."""
    if uses >= DUNGEON_HEAL_HARD_LIMIT:
        return DUNGEON_HEAL_HARD_MULT
    if uses >= DUNGEON_HEAL_SOFT_LIMIT:
        return DUNGEON_HEAL_SOFT_MULT
    return 1.0


def heal_limit_note(uses: int) -> str:
    if uses >= DUNGEON_HEAL_HARD_LIMIT:
        return _LT("dungeon.heal.hard", uses=uses)
    if uses >= DUNGEON_HEAL_SOFT_LIMIT:
        return _LT("dungeon.heal.soft", uses=uses)
    return ""


# Регенерация расходников (v0.15.23): items.regen — % от эффективного лечения
# (с учётом лимита применений и обморожения), разливается по REGEN_TURNS ходам
# игрока линейно затухая к нулю: первый тик самый большой, последний — маленький.
REGEN_TURNS = 3
REGEN_PCT_MAX = 100


def regen_amounts(heal: int, pct: int, turns: int = REGEN_TURNS) -> list:
    """Тики регенерации: всего round(heal * pct%) HP разлито по `turns` ходам.

    Линейное затухание: тики k*turns, k*(turns−1), …, k*1 (сумма = total).
    Например heal=40, pct=40, turns=3 → [8, 5, 3].
    Возвращает [] если ничего не разлито.
    """
    if heal <= 0 or pct <= 0 or turns <= 0:
        return []
    total = round(heal * min(pct, REGEN_PCT_MAX) / 100.0)
    if total <= 0:
        return []
    k = 2.0 * total / (turns * (turns + 1))
    return [round(k * (turns - i)) for i in range(turns)]


async def clear_dungeon_regen(state: FSMContext):
    """Сброс очереди регенерации по окончании боя (v0.22.13).

    Тики «тикают» только по ходам игрока в бою, но очередь жила в FSM-стейте
    забега и переносилась между боями. По решению владельца бой закончился —
    регенерация сгорает: недопитые тики в следующий бой НЕ переходят
    (иначе между боями пирог работал бы «накоплением»).
    """
    await state.update_data(regen_amounts=None)


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
WEAPON_EFFECT_EMOJI = {
    "poison": "☠️",
    "bleed": "🩸",
    "frostbite": "🧊",
    "stun": "💫",
    "burn": "🔥",
}


def _weapon_label(kind: str) -> str:
    """Название эффекта оружия/статуса для текста боя (из utils/localization)."""
    from utils.localization import t
    return t(f"battle.weapon.label.{kind}")


def _weapon_attack(kind: str) -> str:
    """Строка атаки с эффектом (из utils/localization)."""
    from utils.localization import t
    return t(f"battle.weapon.attack.{kind}")

# Рыба подземного водохранилища (после победы над Крысиным капитаном): веса.
# Стоимость заброса — RESERVOIR_AP_COST из config (5 ОД, дороже озера).
RESERVOIR_AP_COST = RESERVOIR_AP_COST_CFG
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

    Подземное водохранилище: рыба светится день и ночь одинаково, поэтому
    берём day_weight (night_weight для этого водоёма не используется).
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


# ───────── Мутировавший моллюск: редкий боевой улов водохранилища ─────────
# Враг живёт в fishing_enemies (spot='reservoir') и настраивается в админке
# «⚔️ Враги»: HP, урон, уклонение, шанс встречи, дропы, фото, описание.
# Бой — кнопками, как с кабаном в лесу, и не трогает HP забега: за поражение
# снимаются ОД (loss_ap), за победу дроп идёт сразу в инвентарь.
# Пока бой идёт, игрок заперт в водохранилище (гард в FishingActiveLock).
MOLLUSK_BATTLE: dict = {}

# Бой не может длиться вечно: если боец куда-то пропал (забег закончился, рестарт),
# запись стареет и снимается, чтобы не заблокировать игрока навсегда.
MOLLUSK_BATTLE_TTL = 900


def deactivate_mollusk(user_id: int):
    """Сброс боя с моллюском (уход в другое меню)."""
    MOLLUSK_BATTLE.pop(user_id, None)
    onhit.unregister(user_id)


def purge_mollusk_battle(now: float | None = None):
    """Убирает бои старше MOLLUSK_BATTLE_TTL секунд."""
    now = now if now is not None else time.time()
    for uid in [u for u, b in MOLLUSK_BATTLE.items()
                if now - float(b.get('started_at') or 0) > MOLLUSK_BATTLE_TTL]:
        MOLLUSK_BATTLE.pop(uid, None)
        onhit.unregister(uid)


def _mollusk_markup(token: str):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=_LT("mollusk.btn.hit"), callback_data=f"mollusk:hit:{token}")],
        [InlineKeyboardButton(text=_LT("mollusk.btn.flee"), callback_data=f"mollusk:flee:{token}")],
    ])


async def _mollusk_roll() -> dict | None:
    """Ролл встречи с моллюском: враг из БД или None (шанс не выпал)."""
    enemies = await get_source_enemies("fishing", spot="reservoir", enabled_only=True)
    roll = random.random() * 100
    for enemy in enemies:
        if enemy_encounter_hit(float(enemy.get('chance') or 0), roll,
                               0, int(enemy.get('pity_target') or 0)):
            return dict(enemy)
    return None


async def _mollusk_media(enemy: dict) -> tuple:
    """(photo_id, media_path): фото врага из БД, иначе локальный файл, иначе фон."""
    if enemy.get('image'):
        return enemy['image'], None
    path = resolve_image(enemy.get('photo_key') or "city/mollusk")
    if os.path.isfile(path):
        return None, path
    return None, _reservoir_photo()


async def _show_mollusk_battle(callback, prefix: str = ""):
    """Экран боя с моллюском (по данным MOLLUSK_BATTLE)."""
    battle = MOLLUSK_BATTLE.get(callback.from_user.id)
    if not battle:
        return
    enemy = battle['enemy']
    name = enemy.get('name') or _LT("mollusk.default_name")
    effects_line = onhit.active_line(battle)
    effects_line = f"\n🧑 {effects_line}" if effects_line else ""
    hp_max = battle['enemy_hp_max']
    text = _LT(
        "mollusk.screen", prefix=prefix, name_up=name.upper(), name=name,
        ebar=_hp_bar(battle['enemy_hp'], hp_max),
        pbar=_hp_bar(battle['player_hp'], battle['player_hp_max']),
        effects=effects_line, round=battle['round'])
    photo_id, photo = await _mollusk_media(enemy)
    await _resv_answer(callback.from_user.id, callback.message, text, _mollusk_markup(battle['token']),
                       photo=photo, photo_id=photo_id)


async def _mollusk_start(callback, state: FSMContext, user_id: int, extra: str = "") -> bool:
    """Пытается начать бой с моллюском после заброса. True — бой начался."""
    if MOLLUSK_BATTLE.get(user_id):
        return False
    enemy = await _mollusk_roll()
    if not enemy:
        return False
    from utils.combat_model import pilot_combat_stats
    player_hp = (await pilot_combat_stats(user_id))['hp_max']
    enemy_hp = max(1, int(enemy.get('hp') or 20))
    MOLLUSK_BATTLE[user_id] = {
        "token": str(random.randint(100000, 999999)),
        "started_at": time.time(),
        "enemy": enemy,
        "enemy_hp": enemy_hp,
        "enemy_hp_max": enemy_hp,
        "player_hp": player_hp,
        "player_hp_max": player_hp,
        "on_hit_effects": onhit.parse_on_hit_effects(enemy.get('on_hit_effects')),
        "round": 1,
    }
    onhit.register(user_id, MOLLUSK_BATTLE[user_id])
    await log_activity(user_id, "dungeon_reservoir", f"Встреча: {enemy.get('name')}")
    await _show_mollusk_battle(callback, prefix=extra)
    return True


async def _mollusk_loot(user_id: int, enemy: dict) -> str:
    """Дроп за победу (по дропам врага из БД) — текстом для экрана результата."""
    drops = await get_source_enemy_drops("fishing", enemy.get('id'))
    picked = roll_enemy_drops_db(drops)
    if not picked:
        return _LT("mollusk.loot.empty")
    got = []
    rare = False
    for p in picked:
        item = await get_item(p.get('item_id'))
        if not item:
            continue
        qty = max(1, int(p.get('qty') or 1))
        await add_inventory_item(user_id, item['id'], qty)
        await log_activity(user_id, "dungeon_reservoir", f"Добыча: {item['name']}")
        line = f"• «{item['name']}» ×{qty}"
        if item['sell_price'] > 0:
            line += _LT("mollusk.loot.sell", price=item['sell_price'],
                        money=plural_nordmark(item['sell_price']))
        if int(item.get('rarity') or 1) >= 5:
            rare = True
        got.append(line)
    if not got:
        return _LT("mollusk.loot.lost")
    rare_line = _LT("mollusk.loot.rare") if rare else ""
    return _LT("mollusk.loot.got", items="\n".join(got), rare=rare_line)


async def _reservoir_answer_result(callback, text, markup, enemy: dict | None = None):
    """Ответ с картинкой врага, если она есть, иначе — фон водохранилища."""
    user_id = callback.from_user.id
    if enemy and enemy.get('image'):
        await _resv_answer(user_id, callback.message, text, markup, photo_id=enemy['image'])
        return
    if enemy:
        path = resolve_image(enemy.get('photo_key') or "city/mollusk")
        if os.path.isfile(path):
            await _resv_answer(user_id, callback.message, text, markup, photo=path)
            return
    await _resv_answer(user_id, callback.message, text, markup, photo=_reservoir_photo())


@router.callback_query(F.data.regexp(r"^mollusk:hit:\d+$"))
async def mollusk_hit(callback: CallbackQuery, state: FSMContext):
    """Удар по моллюску."""
    user_id = callback.from_user.id
    battle = MOLLUSK_BATTLE.get(user_id)
    if not battle or battle['token'] != callback.data.split(":")[-1]:
        await callback.answer(_LT("mollusk.alert.stale"), show_alert=True)
        return
    if await state.get_state() != DungeonFSM.in_reservoir.state:
        MOLLUSK_BATTLE.pop(user_id, None)
        onhit.unregister(user_id)
        await callback.answer(_LT("mollusk.alert.not_here"), show_alert=True)
        return
    await callback.answer()

    enemy = battle['enemy']
    # DoT (яд/кровотечение, единая система v0.38.0): тикает в начале хода.
    dot_dmg, dot_lines = onhit.tick_dots(battle)
    dot_note = "".join(f"{line}\n\n" for line in dot_lines)
    if dot_dmg:
        battle['player_hp'] = max(0, battle['player_hp'] - dot_dmg)
        if battle['player_hp'] <= 0:
            MOLLUSK_BATTLE.pop(user_id, None)
            onhit.unregister(user_id)
            loss_ap = int(enemy.get('loss_ap') or 12)
            removed = await remove_ap_or_floor(user_id, loss_ap)
            await log_activity(user_id, "dungeon_reservoir", f"Проиграл моллюску (−{removed} ОД)")
            text = _LT("mollusk.defeat.dot", dot=dot_note, removed=removed)
            step = await dungeon_new_step(state)
            await _reservoir_answer_result(callback, text, _reservoir_result_markup(step))
            return

    # Ачивка «Эликсиры» lvl4: пассивная регенерация в начале хода игрока.
    ach_regen = await get_achievement_bonus(user_id, "elixir", "regen_hp")
    regen_note = ""
    if ach_regen > 0 and battle['player_hp'] < battle['player_hp_max']:
        heal = min(battle['player_hp_max'] - battle['player_hp'], ach_regen)
        if heal > 0:
            battle['player_hp'] += heal
            regen_note = _LT("dungeon.fight.regen", healed=heal) + "\n"

    # Твой удар: считается от ТВОЕГО оружия, наград и состояний.
    from utils.combat_model import pilot_combat_stats, roll_pilot_damage
    stats = await pilot_combat_stats(user_id, onhit.battle_state_keys(battle))
    res = roll_pilot_damage(stats, enemy)
    player_hit = res['damage']
    # Достижение «Монстры»: урон в водохранилище тоже считается подземельем.
    dungeon_dmg_pct = await get_achievement_bonus(user_id, "monsters", "dmg_dungeon")
    if dungeon_dmg_pct and player_hit > 0:
        player_hit = max(1, round(player_hit * (100 + dungeon_dmg_pct) / 100))
    battle['enemy_hp'] -= player_hit
    if res['dodged']:
        hit_line = _LT("mollusk.hit.miss")
    else:
        extra = ""
        if res['armor_blocked']:
            extra += _LT("mollusk.hit.armor", amount=res['armor_blocked'])
        if res['crit']:
            extra += _LT("mollusk.hit.crit")
        hit_line = _LT("mollusk.hit.hit", dmg=player_hit, extra=extra)

    if battle['enemy_hp'] <= 0:
        MOLLUSK_BATTLE.pop(user_id, None)
        onhit.unregister(user_id)
        name = enemy.get('name') or _LT("mollusk.default_name")
        loot_line = await _mollusk_loot(user_id, enemy)
        await log_activity(user_id, "dungeon_reservoir", f"Победил: {name}")
        await bump_achievement(user_id, "monsters", 1)
        text = _LT("mollusk.win", pre=dot_note + regen_note + hit_line, loot=loot_line)
        await clear_dungeon_regen(state)
        step = await dungeon_new_step(state)
        await _reservoir_answer_result(callback, text, _reservoir_result_markup(step), enemy)
        return

    from utils.combat_model import roll_enemy_damage
    eres = roll_enemy_damage(stats, enemy)
    dmg = eres['damage']
    battle['player_hp'] -= dmg
    if eres['dodged']:
        counter_line = _LT("mollusk.counter.dodged")
    else:
        extra = ""
        if eres['armor_blocked']:
            extra += _LT("mollusk.counter.armor", amount=eres['armor_blocked'])
        if eres['crit']:
            extra += _LT("mollusk.hit.crit")
        counter_line = _LT("mollusk.counter.hit", dmg=dmg, extra=extra)
    if battle['player_hp'] <= 0:
        MOLLUSK_BATTLE.pop(user_id, None)
        onhit.unregister(user_id)
        loss_ap = int(enemy.get('loss_ap') or 12)
        removed = await remove_ap_or_floor(user_id, loss_ap)
        await log_activity(user_id, "dungeon_reservoir", f"Проиграл моллюску (−{removed} ОД)")
        text = _LT("mollusk.defeat.counter", pre=dot_note + regen_note + hit_line,
                   counter=counter_line, removed=removed)
        step = await dungeon_new_step(state)
        await _reservoir_answer_result(callback, text, _reservoir_result_markup(step))
        return

    # Эффекты при ударе (v0.38.0): единая система — on_hit_effects врага.
    proc_line = ""
    if not eres['dodged']:
        procs = onhit.roll_procs(battle.get('on_hit_effects') or [])
        if procs:
            proc_lines = onhit.apply_procs(user_id, battle, procs,
                                           enemy_name=enemy.get('name') or _LT("mollusk.default_short"))
            proc_line = "".join(f"{line}\n\n" for line in proc_lines)

    # Спад срочных эффектов (оглушение/ослепление и т.д.) в конце хода.
    round_note = "".join(f"{line}\n\n" for line in onhit.end_round(battle))

    battle['round'] += 1
    await _show_mollusk_battle(
        callback, prefix=f"{dot_note}{regen_note}{hit_line}{counter_line}{proc_line}{round_note}")


@router.callback_query(F.data.regexp(r"^mollusk:flee:\d+$"))
async def mollusk_flee(callback: CallbackQuery, state: FSMContext):
    """Сбежать от моллюска (без штрафа, как с кабаном в лесу)."""
    user_id = callback.from_user.id
    battle = MOLLUSK_BATTLE.get(user_id)
    if not battle or battle['token'] != callback.data.split(":")[-1]:
        await callback.answer(_LT("mollusk.alert.stale"), show_alert=True)
        return
    MOLLUSK_BATTLE.pop(user_id, None)
    onhit.unregister(user_id)
    await callback.answer()
    await log_activity(user_id, "dungeon_reservoir", "Сбежал от моллюска")
    step = await dungeon_new_step(state)
    await _reservoir_answer_result(
        callback,
        _LT("mollusk.fled"),
        _reservoir_result_markup(step))


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
    """Строки активных статусов боя (яд/кровотечение/обморожение/состояния)."""
    line = onhit.active_line(data)
    return [line] if line else []


def dungeon_main_keyboard(step: int = 0):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=_LT("dungeon.btn.continue"), callback_data=f"dungeon:continue:{step}")],
        [InlineKeyboardButton(text=_LT("resv.btn.exit"), callback_data="dungeon:exit")],
    ])


def _slot_button_label(row):
    qty = int(row.get('quantity') or 0)
    suffix = f" x{qty}" if qty > 0 else ""
    if row['name'] == SMOKE_ITEM_NAME:
        return _LT("dungeon.slot.smoke", suffix=suffix)
    if row['cure_poison']:
        return _LT("dungeon.slot.antidote", suffix=suffix)
    if row.get('cure_frostbite'):
        return _LT("dungeon.slot.frost", name=row['name'], suffix=suffix)
    if row['heal'] > 0:
        return _LT("dungeon.slot.heal", name=row['name'], suffix=suffix)
    return _LT("dungeon.slot.other", name=row['name'], suffix=suffix)


def dungeon_combat_keyboard(enemy_id: int, slot_items: list = None, step: int = 0):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    buttons = [
        [InlineKeyboardButton(text=_LT("dungeon.btn.attack"), callback_data=f"dungeon:attack:{enemy_id}:{step}")],
    ]
    for slot, row in (slot_items or []):
        buttons.append([InlineKeyboardButton(text=_slot_button_label(row), callback_data=f"dungeon:use_slot:{slot}:{step}")])
    buttons.append([InlineKeyboardButton(text=_LT("dungeon.btn.escape"), callback_data=f"dungeon:escape:{enemy_id}:{step}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def dungeon_boss_keyboard(boss_id: int, slot_items: list = None, step: int = 0):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    buttons = [
        [InlineKeyboardButton(text=_LT("dungeon.btn.attack"), callback_data=f"dungeon:attack:{boss_id}:{step}")],
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
        [InlineKeyboardButton(text=_LT("resv.btn.fish_here"), callback_data=f"resv:enter:{step}")],
        [InlineKeyboardButton(text=_LT("resv.btn.deeper"), callback_data=f"resv:deeper:{step}")],
        [InlineKeyboardButton(text=_LT("resv.btn.exit"), callback_data="dungeon:exit")],
    ])


def reservoir_keyboard(step: int = 0):
    """Меню подземного водохранилища: рыбалка, наживка, снаряжение, дальше, выход."""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=_LT("resv.btn.cast", ap=RESERVOIR_AP_COST), callback_data=f"resv:cast:{step}")],
        [InlineKeyboardButton(text=_LT("resv.btn.bait"), callback_data=f"resv:bait:{step}")],
        [InlineKeyboardButton(text=_LT("resv.btn.gear"), callback_data=f"resv:eq:{step}")],
        [InlineKeyboardButton(text=_LT("resv.btn.deeper"), callback_data=f"resv:deeper:{step}")],
        [InlineKeyboardButton(text=_LT("resv.btn.exit"), callback_data="dungeon:exit")],
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
        text=row(_LT("resv.bait.none"), "none"),
        callback_data=f"resv:bait:set:{step}:none")])
    rows.append([InlineKeyboardButton(text=_LT("resv.btn.back_resv"), callback_data=f"resv:menu:{step}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _reservoir_result_markup(step: int = 0):
    """Кнопки после заброса в водохранилище."""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=_LT("resv.btn.again"), callback_data=f"resv:cast:{step}")],
        [InlineKeyboardButton(text=_LT("resv.btn.bait"), callback_data=f"resv:bait:{step}")],
        [InlineKeyboardButton(text=_LT("resv.btn.deeper"), callback_data=f"resv:deeper:{step}")],
        [InlineKeyboardButton(text=_LT("resv.btn.exit"), callback_data="dungeon:exit")],
    ])


def _reservoir_wait_markup():
    """Кнопка на экране ожидания улова в водохранилище.

    Окно «Поплавок замер неподвижно. Ждёшь...» раньше шло без клавиатуры: если
    результат не приходил (процесс перезапустился — деплой, OOM-kill), в чате
    оставалось сообщение без кнопок, и пилот «зависал» в водохранилище.
    """
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=_LT("resv.btn.recover"), callback_data="resv:recover")],
    ])


def dungeon_start_keyboard():
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=_LT("dungeon.btn.contracts"), callback_data="contracts:list")],
        [InlineKeyboardButton(text=_LT("dungeon.btn.city"), callback_data="city:menu")],
    ])


def contract_missing_keyboard():
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=_LT("dungeon.btn.contracts"), callback_data="contracts:list")],
        [InlineKeyboardButton(text=_LT("dungeon.btn.city"), callback_data="city:menu")],
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
        await msg.answer(_LT("dungeon.msg.no_contracts"))
        return

    contracts = await get_user_contract_count(user_id)

    text = _LT("dungeon.board.head")

    buttons = []
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    for i, d in enumerate(dungeons, 1):
        rooms = await get_dungeon_rooms_map(d['id'])
        floors_n = len(rooms) or int(d.get('floors_count') or 1)
        text += _LT("dungeon.board.item", i=i, name=d['name'], floors=floors_n,
                    rooms=rooms[0] if rooms else d.get('rooms_per_floor') or '—')
        buttons.append([InlineKeyboardButton(
            text=_LT("dungeon.board.btn", name=d['name']),
            callback_data=f"contract:pick:{d['id']}"
        )])

    text += _LT("dungeon.board.foot", contracts=contracts)
    buttons.append([InlineKeyboardButton(text=_LT("dungeon.btn.city"), callback_data="city:menu")])

    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    photo = None
    # Приоритет: локальная картинка доски контрактов → фото входа данжа.
    board = resolve_image("city/contracts_board")
    if os.path.isfile(board):
        photo = FSInputFile(board)
    if not photo:
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
        await callback.message.answer(_LT("dungeon.msg.contract_missing"))
        return

    user_id = callback.from_user.id
    contracts = await get_user_contract_count(user_id)
    user = await get_user(user_id)

    rooms = await get_dungeon_rooms_map(dungeon_id)
    floors_n = len(rooms) or int(dungeon.get('floors_count') or 1)
    difficulty = await _contract_difficulty(dungeon)
    reward_nm = await _contract_reward_nm(dungeon)

    stars = "★" * difficulty + "☆" * (5 - difficulty)
    text = _LT(
        "dungeon.card.text", name=dungeon['name'], desc=dungeon['description'] or '',
        floors=floors_n, rooms=rooms[0] if rooms else dungeon.get('rooms_per_floor') or '—',
        stars=stars, reward=reward_nm, contracts=contracts, ap=user['ap'] if user else 0)

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=_LT("dungeon.btn.enter_contract"), callback_data=f"contract:enter:{dungeon_id}")],
        [InlineKeyboardButton(text=_LT("dungeon.btn.back_list"), callback_data="contracts:list")],
        [InlineKeyboardButton(text=_LT("dungeon.btn.city"), callback_data="city:menu")],
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
            _LT("dungeon.msg.no_contract_full"),
            reply_markup=contract_missing_keyboard()
        )
        return

    user = await get_user(user_id)
    if user['ap'] < 30:
        await callback.message.answer(
            _LT("dungeon.msg.ap_short_enter", ap=user['ap']),
        )
        return

    await state.update_data(dungeon_id=dungeon['id'])
    await state.set_state(DungeonFSM.confirm_enter)
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    await callback.message.answer(
        _LT("dungeon.enter.confirm", name=dungeon['name'], contracts=contracts, ap=user['ap']),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=_LT("dungeon.btn.yes_enter"), callback_data=f"contract:enter:confirm:{dungeon_id}")],
            [InlineKeyboardButton(text=_LT("dungeon.btn.cancel"), callback_data=f"contract:pick:{dungeon_id}")],
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
            _LT("dungeon.msg.no_contract"),
            reply_markup=contract_missing_keyboard()
        )
        return

    user = await get_user(user_id)
    if user['ap'] < 30:
        await state.clear()
        await callback.message.answer(
            _LT("dungeon.msg.ap_short", ap=user['ap'])
        )
        return

    contract = await get_item_by_name("Контракт на зачистку")
    ok = await remove_inventory_item(user_id, contract['id'], 1)
    if not ok:
        await state.clear()
        await callback.message.answer(_LT("dungeon.msg.contract_fail"))
        return

    ok = await remove_ap(user_id, 30, reason="вход в подземелье")
    if not ok:
        await state.clear()
        await callback.message.answer(_LT("dungeon.msg.ap_fail"))
        return

    await start_dungeon_run(user_id, dungeon['id'])
    run = await get_active_run(user_id)
    await state.update_data(dungeon_heal_uses=0, dungeon_smoke_uses=0)
    await log_activity(user_id, "dungeon_enter", f"Контракт «{dungeon['name']}»")

    rooms0 = await rooms_total_now(run)
    await callback.message.answer(
        _LT("dungeon.enter.done", name=dungeon['name'], rooms=rooms0,
            bar=_hp_bar(run['hp'], run['hp_max'])),
    )
    await state.set_state(DungeonFSM.in_dungeon)
    await show_room(callback.message, run, user_id, state)


# Совместимость: старые кнопки «Подземелье» переадресуются на список контрактов.
@router.callback_query(F.data == "city:dungeon")
async def dungeon_entry_legacy(callback: CallbackQuery, state: FSMContext):
    await log_location_visit(callback.from_user.id, "contracts")
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
    text = _LT("resv.captain.text")
    if loot_nm > 0:
        text += _LT("resv.captain.loot", nm=loot_nm)
    text += _LT("resv.captain.tail")
    step = await dungeon_new_step(state)
    await state.set_state(DungeonFSM.in_dungeon)
    await where.answer(text, reply_markup=post_captain_keyboard(step))


def _message_photo_id(where):
    """file_id последнего фото сообщения (или None)."""
    photos = getattr(where, 'photo', None)
    return photos[-1].file_id if photos else None


# ───────── Окно водохранилища: одно сообщение на игрока ─────────
# Как у озера (fishing.FISH_MSG): все экраны — меню, заброс, результат, бой с
# моллюском — рисуются в одном и том же сообщении. Без трекера надпись
# «Ты забрасываешь удочку… Ждёшь…» уходила отдельным сообщением (edit_text по
# фото-окну падал) и её никто не удалял — чат забивался мусором.
# Значение: user_id -> (chat_id, message_id, media_key); media_key —
# "fid:<file_id>" для фото, "path:<путь>" для локального файла, None для текста.
RESV_MSG: dict = {}


async def close_reservoir_window(user_id: int, bot: Bot):
    """Убирает окно водохранилища из чата (спуск на этаж 2 / выход из подземелья)."""
    entry = RESV_MSG.pop(user_id, None)
    if not entry:
        return
    try:
        await bot.delete_message(entry[0], entry[1])
    except Exception:
        pass


async def _resv_paint(user_id: int, where, text, markup=None, photo=None, photo_id=None):
    """Единая отрисовка окна водохранилища в одном сообщении на игрока.

    photo_id — Telegram file_id (фото врага/рыбы из редактора), photo — путь к
    локальному файлу (фон водохранилища). Если тип сообщения меняется
    (фото <-> текст) или редактирование не прошло — старое окно удаляется,
    чтобы в чате не копились осиротевшие сообщения.
    """
    bot = where.bot
    chat_id = where.chat.id

    entry = RESV_MSG.get(user_id)
    if entry and entry[0] == chat_id:
        mid, cur_key = entry[1], entry[2]
    else:
        mid = where.message_id
        fid = _message_photo_id(where)
        cur_key = f"fid:{fid}" if fid else None

    want_key = f"fid:{photo_id}" if photo_id else (f"path:{photo}" if photo else None)

    # Фото -> фото, та же картинка: правим только подпись.
    if want_key is not None and want_key == cur_key:
        try:
            await bot.edit_message_caption(chat_id, mid, caption=text, reply_markup=markup)
            RESV_MSG[user_id] = (chat_id, mid, cur_key)
            return
        except Exception:
            pass
    # Фото -> фото, другая картинка: подмена медиа (тип сообщения не меняется).
    if want_key is not None and cur_key is not None:
        try:
            await bot.edit_message_media(
                chat_id, mid,
                media=InputMediaPhoto(media=photo_id or FSInputFile(photo), caption=text),
                reply_markup=markup)
            RESV_MSG[user_id] = (chat_id, mid, want_key)
            return
        except Exception:
            pass
    # Текст -> текст.
    if want_key is None and cur_key is None:
        try:
            await bot.edit_message_text(chat_id, mid, text=text, reply_markup=markup)
            RESV_MSG[user_id] = (chat_id, mid, None)
            return
        except Exception:
            pass

    # Смена типа сообщения (фото <-> текст) или неудачный edit: убираем старое
    # окно (в т.ч. сообщение с нажатой кнопкой) и шлём новое.
    for old in {mid, getattr(where, 'message_id', None)}:
        if old:
            try:
                await bot.delete_message(chat_id, old)
            except Exception:
                pass
    if photo_id:
        sent = await bot.send_photo(chat_id, photo_id, caption=text, reply_markup=markup)
    elif photo:
        sent = await bot.send_photo(chat_id, FSInputFile(photo), caption=text, reply_markup=markup)
    else:
        sent = await bot.send_message(chat_id, text, reply_markup=markup)
    RESV_MSG[user_id] = (chat_id, sent.message_id, want_key)


async def _resv_answer(user_id: int, where, text, markup=None, photo=None, photo_id=None):
    """Отрисовка экрана водохранилища в едином окне (см. _resv_paint)."""
    await _resv_paint(user_id, where, text, markup, photo, photo_id)


async def show_reservoir(where, user_id: int, state: FSMContext):
    """Меню подземного водохранилища (рыбалка как на озере: наживка, удочка, улов)."""
    run = await get_active_run(user_id)
    step = await dungeon_new_step(state)
    text = _LT("resv.menu.intro")
    user = await get_user(user_id) or {}
    chosen = (user.get('fishing_bait') or "").strip()
    rod = await _rod_for(user_id)
    if rod:
        rank = rod['rarity'] or 1
        bait_label = await _bait_label(user_id, chosen)
        bait_name, _ = await _resolve_bait(user_id, chosen)
        chance = _catch_chance(rod, bait_name, (await get_award_bonus(user_id))['fishing'])
        text += _LT("resv.menu.rod", name=rod['name'], rank=rank,
                    bonus=rank * ROD_BONUS_PER_RANK, bait=bait_label)
        if bait_name:
            text += _LT("resv.menu.chance", chance=chance)
        else:
            text += _LT("resv.menu.nobait", junk=await junk_hint('reservoir'))
    else:
        text += _LT("resv.menu.no_rod")

    ap = user.get('ap', 0) or 0
    ap_max = user.get('ap_max', ap) or ap
    text += _LT("resv.ap", ap=ap, ap_max=ap_max)
    if ap < RESERVOIR_AP_COST:
        text += _LT("resv.ap_short", cost=RESERVOIR_AP_COST)

    caught = await get_fish_catches(user_id)
    names = {r['name'] for r in await get_water_fish_pool("reservoir")}
    if not names:
        names = {f[0] for f in RESERVOIR_FISH_POOL}
    resv_caught = [c for c in caught if c['name'] in names]
    if resv_caught:
        counts = {}
        for c in resv_caught:
            counts[c['name']] = counts.get(c['name'], 0) + 1
        text += _LT("resv.catch.head") + "\n".join(f"• {n} x{k}" for n, k in counts.items())

    text += _LT("resv.menu.safe")

    photo = _reservoir_photo()
    if photo and not os.path.isfile(photo):
        photo = None
    await _resv_answer(user_id, where, text, reservoir_keyboard(step), photo=photo)


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
        await callback.message.answer(_LT("dungeon.msg.not_found_active"))
        await state.clear()
        return

    parts = callback.data.split(":")
    if len(parts) < 3 or int(parts[2]) != await dungeon_current_step(state):
        await _log_stale(callback, "данж: устаревшая кнопка продолжения")
        await callback.message.answer(_LT("dungeon.alert.stale_reopen"))
        return

    if user_id in FISHING_CASTING:
        await callback.answer(_LT("resv.alert.wait"), show_alert=True)
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
    hp_text = _hp_bar(run['hp'], run['hp_max'])
    slot_items = await _combat_slot_items(user_id)
    sdata = await state.get_data()
    # Комната «проживается» один раз: перерисовка (возврат в забег, отмена
    # выхода, повторный вход) не должна перебрасывать тип комнаты и повторно
    # начислять НМ. Иначе игрок фармит ресурс через выход/отмену выхода.
    if sdata.get('dungeon_room_rolled') == run['room_number']:
        room_type = sdata.get('dungeon_room_type')
        rolled = False
    else:
        room_type = room_type_roll()
        rolled = True
        await state.update_data(dungeon_room_rolled=run['room_number'],
                                dungeon_room_type=room_type)
    heal_uses = int(sdata.get('dungeon_heal_uses', 0) or 0)
    step = await dungeon_new_step(state)
    rooms_total = await rooms_total_now(run)

    heal_line = ""
    if heal_uses >= DUNGEON_HEAL_SOFT_LIMIT:
        mult = heal_limit_mult(heal_uses)
        heal_line = _LT("dungeon.room.heal", uses=heal_uses, mult=f"{mult:.0%}")

    room_header = _LT("dungeon.room.header", floor=run['floor'], room=run['room_number'], total=rooms_total)
    status_text = status_lines(sdata)
    status_text.append(heal_line.strip())
    status_block = "\n".join(s for s in status_text if s)
    if status_block:
        status_block += "\n"

    if room_type == "enemy":
        enemies = await get_floor_enemies(run['dungeon_id'], run['floor'])
        non_boss = [e for e in enemies if not e['is_boss']]
        if rolled:
            enemy = random.choice(non_boss) if non_boss else random.choice(enemies)
            await state.update_data(current_enemy_id=enemy['id'], current_enemy_hp=enemy['hp'],
                                    enemy_dots={})
        else:
            prev_id = sdata.get('current_enemy_id')
            enemy = next((e for e in enemies if e['id'] == prev_id), None)
            if enemy is None:
                enemy = random.choice(non_boss) if non_boss else random.choice(enemies)

        text = _LT(
            "dungeon.room.enemy", name=dungeon['name'], header=room_header, hp=hp_text,
            status=status_block, enemy=enemy['name'], ehp=enemy['hp'], atk=enemy['attack'],
            dodge=enemy['dodge'] if 'dodge' in enemy.keys() else 0,
            desc=enemy['description'] if 'description' in enemy.keys() and enemy['description'] else '')
        await answer_enemy_photo(message, enemy, text, reply_markup=dungeon_combat_keyboard(enemy['id'], slot_items, step))

    elif room_type == "resource":
        if rolled:
            nm = resource_amount(run['floor'])
            await add_run_nordmarks(run['id'], nm)
        else:
            nm = sdata.get('dungeon_room_nm', resource_amount(run['floor']))
        await state.update_data(dungeon_room_nm=nm)

        text = _LT("dungeon.room.resource", name=dungeon['name'], header=room_header, hp=hp_text,
                   status=status_block, nm=nm)
        await message.answer(text, reply_markup=dungeon_main_keyboard(step))

    else:
        text = _LT("dungeon.room.empty", name=dungeon['name'], header=room_header, hp=hp_text,
                   status=status_block)
        await message.answer(text, reply_markup=dungeon_main_keyboard(step))


async def _enemy_defeated(callback, state, bot, run, enemy, player_hp):
    """Победа над врагом (обычный или босс): награды, лут, переходы.

    Используется и при убийстве ударом, и когда враг пал от эффекта оружия
    (тики DoT в начале хода игрока). Вызывается с гарантией, что HP врага == 0.
    """
    user_id = callback.from_user.id
    # Достижения: каждое поверженное чудовище данжа (обычный, капитан или босс).
    await bump_achievement(user_id, "monsters", 1)
    if enemy['is_boss']:
        reward = enemy['reward_nm'] or 0
        if reward > 0:
            await add_run_nordmarks(run['id'], reward)

        if run['floor'] == 1:
            # Промежуточный босс «Крысиный капитан»: награда копится в луте,
            # после победы — выбор: водохранилище или этаж 2.
            await state.update_data(captain_defeated=1)
            await clear_dungeon_regen(state)
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

            text = _LT("dungeon.boss.won", enemy=enemy['name'])
            if loot_nm > 0:
                text += _LT("dungeon.exit.nm", nm=loot_nm) + "\n"
            for name, qty in transferred:
                text += f"🎁 {name} x{qty}\n"
            if loot_nm <= 0 and not transferred:
                text += _LT("dungeon.boss.empty")

            await end_run(run['id'], 0)
            await state.clear()
            onhit.unregister(user_id)
            await log_activity(user_id, "dungeon_win",
                               f"Прошёл «{enemy['name']}»/подземелье на {run['floor']} этаже")
            await bump_achievement(user_id, "raider", 1)
            await answer_enemy_photo(callback.message, enemy, text, reply_markup=dungeon_start_keyboard())
            pilot = await get_user(user_id)
            await notify(bot, f"🏆 {await player_display(pilot)} прошёл подземелье и победил босса «{enemy['name']}»!", user_id)
    else:
        hp_text = _hp_bar(player_hp, run['hp_max'])
        text = _LT("dungeon.enemy.down", name=enemy['name'])

        dropped = await roll_enemy_drops(run['id'], enemy)
        if dropped:
            text += _LT("dungeon.room.loot_head") + "\n".join(f"• {name} x{qty}" for name, qty in dropped) + "\n\n"
        else:
            text += "\n"

        text += f"❤️ {hp_text}\n"
        text += _LT("dungeon.room.next_hint")
        await clear_dungeon_regen(state)
        next_step = await dungeon_new_step(state)
        await answer_enemy_photo(callback.message, enemy, text, reply_markup=dungeon_main_keyboard(next_step))


@router.callback_query(F.data.startswith("dungeon:attack:"))
async def dungeon_attack(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    user_id = callback.from_user.id
    run = await get_active_run(user_id)
    if not run:
        await callback.message.answer(_LT("dungeon.msg.not_found"))
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
        await callback.message.answer(_LT("dungeon.alert.stale_fight"))
        return
    current_enemy_id = data.get('current_enemy_id')
    if current_enemy_id is not None and current_enemy_id != enemy_id:
        await callback.message.answer(_LT("dungeon.msg.enemy_gone"))
        return

    conn = await get_db()
    cursor = await conn.execute("SELECT * FROM dungeon_enemies WHERE id = ?", (enemy_id,))
    enemy = await cursor.fetchone()
    if not enemy:
        return

    current_enemy_hp = data.get('current_enemy_hp', enemy['hp'])
    player_hp = run['hp']

    # ── Тик регенерации (расходник) в начале хода игрока: первый тик самый большой ──
    regen_healed = 0
    regen_queue = data.get('regen_amounts')
    if regen_queue:
        heal_hp = min(run['hp_max'] - player_hp, regen_queue[0])
        if heal_hp > 0:
            player_hp += heal_hp
            regen_healed = heal_hp
        await update_run_hp(run['id'], player_hp)
        if len(regen_queue) > 1:
            await state.update_data(regen_amounts=list(regen_queue)[1:])
        else:
            await state.update_data(regen_amounts=None)

    # ── Пассивная регенерация от ачивки «Эликсиры» (lvl4, regen_hp): +N HP/ход ──
    ach_regen = await get_achievement_bonus(user_id, "elixir", "regen_hp")
    if ach_regen > 0 and player_hp < run['hp_max']:
        heal_hp = min(run['hp_max'] - player_hp, ach_regen)
        if heal_hp > 0:
            player_hp += heal_hp
            regen_healed += heal_hp
            await update_run_hp(run['id'], player_hp)

    # ── Тики статусов в начале хода игрока (яд, кровотечение, обморожение) ──
    async def dot_death(line):
        nm_penalty = max(5, enemy['reward_nm'] * 2)
        await remove_nordmarks(user_id, nm_penalty, "dungeon_death", "Штраф за смерть в подземелье")
        text = f"{line}\n" + _LT("dungeon.fight.death_line", nm=nm_penalty)
        await end_run(run['id'], 0)
        await state.clear()
        await answer_enemy_photo(callback.message, enemy, text, reply_markup=dungeon_start_keyboard())

    # DoT (яд/кровотечение, единая система v0.38.0): тики в начале хода игрока.
    # Резист от ачивки «Антидоты» снижает урон яда (считаем на всю сумму DoT,
    # если яд наложен — legacy-поведение poison_res_pct).
    onhit.register(user_id, data)
    dot_dmg, dot_lines = onhit.tick_dots(data)
    if dot_dmg:
        if onhit.has_dot(data, 'poison'):
            res_pct = await get_achievement_bonus(user_id, "antidote", "poison_res_pct")
            if res_pct:
                poison_raw = int((onhit.get_store(data).get('poison') or {}).get('dmg') or 0)
                if poison_raw:
                    poison_cut = max(1, round(poison_raw * (100 - res_pct) / 100))
                    dot_dmg = dot_dmg - poison_raw + poison_cut
        player_hp = max(0, player_hp - dot_dmg)
        await update_run_hp(run['id'], player_hp)
        if player_hp <= 0:
            await dot_death("\n".join(dot_lines) + f"\n(−{dot_dmg} HP за ход)")
            return

    # Обморожение/оглушение и прочие срочные эффекты спадают в конце хода —
    # см. end_round ниже (здесь ничего не декрементируем).

    # ── Тики эффекта оружия игрока на враге (в начале хода игрока) ──
    enemy_dots = dict(data.get('enemy_dots') or {})
    if enemy_dots:
        edmg, eparts = effects.tick_dots(enemy_dots)
        if edmg > 0:
            current_enemy_hp = max(0, current_enemy_hp - edmg)
        await state.update_data(enemy_dots=enemy_dots, current_enemy_hp=current_enemy_hp)
        if current_enemy_hp <= 0:
            label = " и ".join(_weapon_label(k) for k, _ in eparts)
            await callback.message.answer(
                _LT("dungeon.dot.killed", name=enemy['name'], label=label, dmg=edmg)
            )
            await _enemy_defeated(callback, state, bot, run, enemy, player_hp)
            return

    # Урон игрока: своё оружие + награды + состояния, броня врага поглощает часть.
    from utils.combat_model import pilot_combat_stats, roll_pilot_damage
    stats = await pilot_combat_stats(user_id, onhit.battle_state_keys(data))
    enemy_row = enemy if isinstance(enemy, dict) else dict(enemy)
    if not enemy_row.get('dodge') and enemy_row.get('dodge_chance'):
        enemy_row['dodge'] = enemy_row['dodge_chance']
    res = roll_pilot_damage(stats, enemy_row)
    damage_to_enemy = res['damage']
    # Достижения «Монстры» и «Глубины»: урон в подземельях прибавляется процентом.
    dungeon_dmg_pct = (await get_achievement_bonus(user_id, "monsters", "dmg_dungeon")
                       + await get_achievement_bonus(user_id, "raider", "dmg_dungeon"))
    if dungeon_dmg_pct and damage_to_enemy > 0:
        damage_to_enemy = max(1, round(damage_to_enemy * (100 + dungeon_dmg_pct) / 100))
    enemy_dodged = res['dodged']
    enemy_armor_line = (_LT("dungeon.fight.enemy_armor", n=res['armor_blocked'])
                        if res['armor_blocked'] else "")

    current_enemy_hp = max(0, current_enemy_hp - damage_to_enemy)
    await state.update_data(current_enemy_hp=current_enemy_hp)

    enemy_eff_just = False
    if current_enemy_hp <= 0:
        await _enemy_defeated(callback, state, bot, run, enemy, player_hp)
        return

    from utils.combat import get_enemy_bar
    enemy_bar = get_enemy_bar(current_enemy_hp, enemy['hp'])
    from utils.localization import t as _tt
    if enemy_dodged:
        attack_line = _tt("battle.enemy_dodged", enemy=enemy['name'])
    else:
        crit_mark = _tt("battle.crit_mark") if res['crit'] else ""
        attack_line = _LT("dungeon.fight.hit", dmg=damage_to_enemy, crit=crit_mark, armor=enemy_armor_line)
    regen_line = _LT("dungeon.fight.regen", healed=regen_healed) if regen_healed else ""
    text = _LT("dungeon.fight.attack_head", regen=regen_line, enemy=enemy['name'],
               attack=attack_line, bar=enemy_bar)

    # Особый эффект оружия: при попадании есть шанс наложить DoT/оглушение на врага.
    weapon = await get_equipped_weapon(user_id)
    weff = weapon.get('weapon_effect') if weapon else None
    if weff and not enemy_dodged:
        wch = int(weapon.get('weapon_effect_chance') or 0)
        wdmg = int(weapon.get('weapon_effect_dmg') or 0)
        from database.db import get_enemy_effect_resist
        resist = await get_enemy_effect_resist(enemy['id'])
        if effects.is_immune(resist, weff):
            if wch and wdmg and random.randint(1, 100) <= wch:
                from utils.localization import t
                text += t("battle.weapon.immune", enemy=enemy['name'], label=_weapon_label(weff))
            wch = 0
        else:
            wch = effects.effective_chance(wch, resist, weff)
        if wch and wdmg and random.randint(1, 100) <= wch:
            if weff == 'stun':
                await state.update_data(enemy_stun_ticks=WEAPON_STUN_TICKS,
                                        enemy_stun_penalty=wdmg)
                from utils.localization import t
                text += t("battle.weapon.stun_applied", emoji=WEAPON_EFFECT_EMOJI[weff],
                          attack=_weapon_attack(weff), enemy=enemy['name'], dmg=wdmg,
                          ticks=WEAPON_STUN_TICKS)
                enemy_eff_just = True
            else:
                enemy_dots = dict(data.get('enemy_dots') or {})
                res = effects.apply_dot(enemy_dots, weff, wdmg, WEAPON_DOT_TICKS)
                await state.update_data(enemy_dots=enemy_dots)
                from utils.localization import t
                if res["applied"]:
                    text += t("battle.weapon.dot_applied", emoji=WEAPON_EFFECT_EMOJI[weff],
                              attack=_weapon_attack(weff), label=_weapon_label(weff),
                              dmg=wdmg, ticks=WEAPON_DOT_TICKS)
                else:
                    text += t("battle.weapon.dot_cancelled", emoji=WEAPON_EFFECT_EMOJI[weff],
                              attack=_weapon_attack(weff), label=_weapon_label(res['cancelled']))
                enemy_eff_just = True

    # Уклонение пилота: шанс избежать контратаки (база + нашивка, × состояния)
    player_dodge = stats['dodge']
    player_dodged = roll_dodge(player_dodge)
    # Оглушение: враг дезориентирован, его точность падает (штраф к попаданию).
    stun_data = await state.get_data()
    enemy_stun_ticks = int(stun_data.get('enemy_stun_ticks', 0) or 0)
    enemy_stun_penalty = int(stun_data.get('enemy_stun_penalty', 0) or 0)
    stunned_miss = (not player_dodged and enemy_stun_ticks > 0
                    and enemy_stun_penalty > 0 and roll_dodge(enemy_stun_penalty))
    from utils.combat_model import roll_enemy_damage
    eres = roll_enemy_damage(stats, enemy_row)
    blocked_line = ""
    from utils.localization import t as _tr
    if stunned_miss:
        reduced = 0
        stun_line = _tr("battle.enemy.stunned_miss", enemy=enemy['name'])
    elif eres['dodged']:
        reduced = 0
        stun_line = ""
        dodge_line = _tr("battle.player.dodged", enemy=enemy['name'])
    else:
        reduced = eres['damage']
        if eres['armor_blocked']:
            blocked_line = "\n" + _tr("battle.armor_blocked", amount=eres['armor_blocked'])
        if eres['crit']:
            blocked_line += " " + _tr("battle.crit")
        stun_line = ""
        dodge_line = ""
    player_hp = max(0, player_hp - reduced)
    await update_run_hp(run['id'], player_hp)
    lifesteal_line = ""
    if reduced > 0 and current_enemy_hp > 0:
        ls_eff = onhit.roll_lifesteal(
            onhit.parse_on_hit_effects(enemy_row.get('on_hit_effects')))
        if ls_eff:
            new_ehp, healed, ls_txt = onhit.apply_lifesteal_to_attacker(
                current_enemy_hp,
                enemy['hp'],
                reduced,
                ls_eff,
            )
            if healed > 0:
                current_enemy_hp = new_ehp
                await state.update_data(current_enemy_hp=current_enemy_hp)
                lifesteal_line = f"\n{ls_txt}"

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
    text += lifesteal_line

    # Наложение эффектов при ударе врага (v0.38.0): единая система —
    # on_hit_effects строки врага (яд/кровотечение/оглушение и всё, что
    # админ добавит). Наложение только если враг попал.
    proc_text = ""
    if not player_dodged:
        procs = onhit.roll_procs(
            onhit.parse_on_hit_effects(enemy_row.get('on_hit_effects')))
        if procs:
            proc_lines = onhit.apply_procs(user_id, data, procs,
                                           enemy_name=enemy['name'])
            proc_text = "".join(f"\n{line}" for line in proc_lines)
            await state.update_data(on_hit=data.get('on_hit'))

    # Спад срочных эффектов (оглушение/ослепление и т.д.) в конце хода.
    round_note = "".join(f"\n{line}" for line in onhit.end_round(data))
    await state.update_data(on_hit=data.get('on_hit'))

    # Показывать текущие статусы, пока игрок их не снял
    data_after = await state.get_data()
    status_text = ""
    cur_status = onhit.active_line(data_after)
    if cur_status:
        status_text = f"\n{cur_status}"
    if data_after.get('regen_amounts'):
        rq = list(data_after['regen_amounts'])
        status_text += _LT("dungeon.fight.regen_active", tick=rq[0], left=len(rq))
    text += proc_text + round_note + status_text
    # Текущий эффект оружия на враге (пока сам не спал).
    from utils.localization import t as _t
    enemy_dots_after = data_after.get('enemy_dots') or {}
    if enemy_dots_after and not enemy_eff_just:
        for kind, entry in enemy_dots_after.items():
            text += _t("battle.enemy.dot_status", emoji=WEAPON_EFFECT_EMOJI.get(kind, '•'),
                       label=_weapon_label(kind), dmg=entry['dmg'], ticks=entry['ticks'])
    # Оглушение врага (отдельно: это не DoT, а штраф к точности).
    if data_after.get('enemy_stun_ticks') and not enemy_eff_just:
        stun_ticks_left = int(data_after.get('enemy_stun_ticks', 0) or 0)
        stun_pen = int(data_after.get('enemy_stun_penalty', 0) or 0)
        text += _t("battle.enemy.stun_status", penalty=stun_pen, ticks=stun_ticks_left)

    if player_hp <= 0:
        nm_penalty = max(5, enemy['reward_nm'] * 2)
        await remove_nordmarks(user_id, nm_penalty, "dungeon_death", "Штраф за смерть в подземелье")
        text += "\n\n" + _LT("dungeon.fight.death_line", nm=nm_penalty)
        await end_run(run['id'], 0)
        await state.clear()
        onhit.unregister(user_id)
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

    Возвращает текст блокировки («несварение»/«очень пьян»/«оглушён») или None
    — всё в порядке. В бою применение предметов из слотов (антидот, зелья,
    напитки, дымовые шашки) подчиняется тем же правилам, что и вне боя;
    оглушение врагом (v0.38.0) тоже блокирует расходники на время действия.
    """
    from utils.states import get_state_info, consumables_blocked
    if onhit.consumables_blocked_by_battle(user_id):
        return _LT("dungeon.block.stunned")
    info = await get_state_info(user_id)
    blocked = consumables_blocked(info.get('names') or [])
    if not blocked:
        return None
    if "очень пьян" in blocked:
        return _LT("dungeon.block.drunk")
    return _LT("dungeon.block.digest")


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
        await callback.message.answer(_LT("dungeon.alert.stale_fight"))
        return

    run = await get_active_run(user_id)
    if not run:
        await callback.message.answer(_LT("dungeon.msg.not_found"))
        await state.clear()
        return

    item = None
    for s, row in await get_equipment_slot_items(user_id, include_smoke=True):
        if s == slot:
            item = row
            break
    if not item:
        await callback.message.answer(_LT("dungeon.slot.empty"))
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
                _LT("dungeon.smoke.wrong_slot"))
            return
        if not enemy_row:
            await callback.message.answer(_LT("dungeon.msg.no_enemy"))
            return
        if is_boss:
            await callback.message.answer(_LT("dungeon.smoke.boss"))
            return
        if smoke_uses >= DUNGEON_SMOKE_MAX:
            await callback.message.answer(_LT("dungeon.smoke.limit", n=DUNGEON_SMOKE_MAX))
            return
        ok = await remove_inventory_item(user_id, item['id'], 1)
        if not ok:
            await callback.message.answer(_LT("dungeon.smoke.fail"))
            return
        await log_activity(user_id, "item_use", "В бою: дымовая шашка (попытка побега)")
        inv_after_sm = await get_inventory_item(user_id, item['id'])
        if not inv_after_sm or (inv_after_sm['quantity'] or 0) <= 0:
            await clear_equipment_slot(user_id, slot)
        await state.update_data(dungeon_smoke_uses=smoke_uses + 1)
        await _do_dungeon_escape(callback.message, state, user_id, run, enemy_row, smoke_used=True)
        return

    if item['cure_poison'] and not onhit.has_dot(data, 'poison'):
        await callback.message.answer(_LT("dungeon.antidote.useless"))
        return

    from utils.helpers import row_get
    is_drink = bool(row_get(item, 'drink_effect'))
    if item['heal'] > 0 and run['hp'] >= run['hp_max'] and not is_drink:
        await callback.message.answer(
            _LT("dungeon.use.full_hp", hp=run['hp'], hp_max=run['hp_max'])
        )
        return

    ok = await remove_inventory_item(user_id, item['id'], 1)
    if not ok:
        await callback.message.answer(_LT("dungeon.use.fail"))
        return

    # Предмет кончился — очищаем слот, чтобы он не остался «призрачным»
    inv_after = await get_inventory_item(user_id, item['id'])
    if not inv_after or (inv_after['quantity'] or 0) <= 0:
        await clear_equipment_slot(user_id, slot)

    slot_items = await _combat_slot_items(user_id, is_boss=is_boss)
    await log_activity(user_id, "item_use", f"В бою: «{item['name']}»")

    if item['cure_poison']:
        _oh = dict(data.get('on_hit') or {})
        _oh.pop('poison', None)
        await state.update_data(on_hit=_oh)
        await bump_achievement(user_id, "antidote", 1)
        text = _LT("dungeon.use.antidote", name=item['name'])

    # Напиток: (+10 HP отдельным путём, +effect на состояние).
    elif is_drink:
        from database.db import consume_drink
        _ok, _msg = await consume_drink(user_id, item['id'])
        hp_note = ""
        frost_note = ""
        regen_note = ""
        # Напитки с cure_frostbite (Огненная вода, Горячий ягодный морс) снимают обморожение.
        if item.get('cure_frostbite') and onhit.frostbite_active(data):
            _oh = dict(data.get('on_hit') or {})
            _oh.pop('frostbite', None)
            await state.update_data(on_hit=_oh)
            frost_note = _LT("dungeon.use.frost_cured")
        if item['heal'] > 0:
            heal_uses = int(data.get('dungeon_heal_uses', 0) or 0) + 1
            await state.update_data(dungeon_heal_uses=heal_uses)
            mult = heal_limit_mult(heal_uses)
            frozen = onhit.frostbite_active(data)
            if frozen:
                mult *= FROSTBITE_HEAL_MULT
            # Достижения: блюда усиливают «Готовка», зелья — «Эликсиры».
            ach_heal_pct = 0
            if item['name'].startswith(FOOD_DISH_PREFIXES):
                ach_heal_pct += await get_achievement_bonus(user_id, "cooking", "heal_pct")
            if item['name'] in ELIXIR_ITEM_NAMES:
                ach_heal_pct += await get_achievement_bonus(user_id, "elixir", "heal_pct")
                await bump_achievement(user_id, "elixir", 1)
            from utils.states import get_heal_bonus_pct
            state_heal_pct = await get_heal_bonus_pct(user_id)
            heal = max(1, round(item['heal'] * mult * (100 + ach_heal_pct + state_heal_pct) / 100))
            new_hp = min(run['hp_max'], run['hp'] + heal)
            await update_run_hp(run['id'], new_hp)
            hp_note = f"\n❤️ {_hp_bar(new_hp, run['hp_max'])}"
            if mult < 1.0:
                hp_note += _LT("dungeon.use.eff", mult=f"{mult:.0%}", heal=heal, base=item['heal'])
            if frozen:
                hp_note += _LT("dungeon.use.frost_weak")
            if ach_heal_pct > 0:
                hp_note += _LT("dungeon.use.mastery_nl", pct=ach_heal_pct)
            if state_heal_pct > 0:
                hp_note += _LT("dungeon.use.bless_nl", pct=state_heal_pct)
            rpct = int(row_get(item, 'regen') or 0)
            if rpct > 0:
                rturns = int(row_get(item, 'regen_turns') or 0) or REGEN_TURNS
                amounts = regen_amounts(heal, rpct, turns=rturns)
                await state.update_data(regen_amounts=amounts)
                regen_note = _LT("dungeon.use.regen", ticks="/".join(map(str, amounts)))
        text = _msg + frost_note + hp_note + regen_note + heal_limit_note(int(data.get('dungeon_heal_uses', 0) or 0)) + _LT("dungeon.use.continue")

    # Зелья лечения / яблоко / испорченная рыба.
    elif item['heal'] > 0:
        heal_uses = int(data.get('dungeon_heal_uses', 0) or 0) + 1
        await state.update_data(dungeon_heal_uses=heal_uses)
        mult = heal_limit_mult(heal_uses)
        frozen = onhit.frostbite_active(data)
        if frozen:
            mult *= FROSTBITE_HEAL_MULT
        # Достижения: блюда усиливают «Готовка», зелья — «Эликсиры».
        ach_heal_pct = 0
        if item['name'].startswith(FOOD_DISH_PREFIXES):
            ach_heal_pct += await get_achievement_bonus(user_id, "cooking", "heal_pct")
        if item['name'] in ELIXIR_ITEM_NAMES:
            ach_heal_pct += await get_achievement_bonus(user_id, "elixir", "heal_pct")
            await bump_achievement(user_id, "elixir", 1)
        from utils.states import get_heal_bonus_pct
        state_heal_pct = await get_heal_bonus_pct(user_id)
        heal = max(1, round(item['heal'] * mult * (100 + ach_heal_pct + state_heal_pct) / 100))
        new_hp = min(run['hp_max'], run['hp'] + heal)
        await update_run_hp(run['id'], new_hp)
        eff = ""
        if mult < 1.0:
            eff = _LT("dungeon.use.eff", mult=f"{mult:.0%}", heal=heal, base=item['heal'])
        if frozen:
            eff += _LT("dungeon.use.frost_weak")
        if ach_heal_pct > 0:
            eff += _LT("dungeon.use.mastery_sp", pct=ach_heal_pct)
        if state_heal_pct > 0:
            eff += _LT("dungeon.use.bless_sp", pct=state_heal_pct)
        regen_note = ""
        rpct = int(row_get(item, 'regen') or 0)
        if rpct > 0:
            rturns = int(row_get(item, 'regen_turns') or 0) or REGEN_TURNS
            amounts = regen_amounts(heal, rpct, turns=rturns)
            await state.update_data(regen_amounts=amounts)
            regen_note = _LT("dungeon.use.regen", ticks="/".join(map(str, amounts)))
        text = _LT("dungeon.use.healed", name=item['name'], heal=heal, eff=eff,
                   bar=_hp_bar(new_hp, run['hp_max']), regen=regen_note,
                   limit=heal_limit_note(heal_uses))

        # Яблоко: иногда из него выпадает семечко (10%)
        if item['name'] == "Яблоко" and random.random() < 0.1:
            seed = await get_item_by_name("Яблочное семечко")
            if seed:
                await add_inventory_item(user_id, seed['id'], 1)
                text += _LT("dungeon.use.seed")
        # Испорченная рыба: несварение на сутки
        if item['name'].startswith("Испорченн"):
            from utils.states import apply_state_to
            await apply_state_to(user_id, "несварение", caused_by=user_id,
                                 reason="съедена испорченная рыба")
            text += _LT("dungeon.use.spoiled")

        # Суточный баф уворота (items.dodge_buff_pct, v0.41.4 «Предания предков»):
        # активируется первым применением, повторное в течение суток НЕ продлевает.
        dbuff = int(row_get(item, 'dodge_buff_pct') or 0)
        if dbuff > 0:
            from database.db import activate_dodge_buff, dodge_buff_active
            if await activate_dodge_buff(user_id, dbuff):
                text += _LT("dungeon.use.dodge", pct=dbuff)
            elif await dodge_buff_active(user_id):
                text += _LT("dungeon.use.dodge_active", pct=dbuff)
    else:
        await add_inventory_item(user_id, item['id'], 1)
        await callback.message.answer(_LT("dungeon.use.not_in_fight"))
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
        await clear_dungeon_regen(state)
        next_step = await dungeon_new_step(state)
        if smoke_used:
            text = _LT("dungeon.escape.smoke", name=enemy['name']) + _LT("dungeon.room.next_hint")
        else:
            text = _LT("dungeon.escape.run", name=enemy['name']) + _LT("dungeon.room.next_hint")
        if drunk_escape:
            text = _LT("dungeon.escape.drunk_luck") + text
        await where.answer(text, reply_markup=dungeon_main_keyboard(next_step))
        return

    penalty = calculate_escape_damage()
    player_hp = max(0, run['hp'] - penalty)
    await update_run_hp(run['id'], player_hp)

    text = _LT("dungeon.escape.fail", penalty=penalty, bar=_hp_bar(player_hp, run['hp_max']),
               enemy=enemy['name'])
    if smoke_used:
        text += _LT("dungeon.escape.smoke_wasted")
    if drunk_escape:
        text = _LT("dungeon.escape.drunk_fall") + text

    if player_hp <= 0:
        nm_penalty = max(5, enemy['reward_nm'] * 2)
        await remove_nordmarks(user_id, nm_penalty, "dungeon_death", "Штраф за смерть в подземелье")
        text += "\n\n" + _LT("dungeon.fight.death_line", nm=nm_penalty)
        await end_run(run['id'], 0)
        await state.clear()
        onhit.unregister(user_id)
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
        await callback.message.answer(_LT("dungeon.alert.stale_fight"))
        return
    current_enemy_id = data.get('current_enemy_id')
    if current_enemy_id is not None and current_enemy_id != enemy_id:
        await callback.message.answer(_LT("dungeon.msg.enemy_gone"))
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
            _LT("dungeon.boss.no_escape"),
            reply_markup=dungeon_boss_keyboard(enemy['id'], slot_items, next_step)
        )
        return

    await _do_dungeon_escape(callback.message, state, user_id, run, enemy)


async def show_boss(message, run, user_id, state: FSMContext):
    enemies = await get_floor_enemies(run['dungeon_id'], run['floor'])
    boss_list = [e for e in enemies if e['is_boss']]
    if not boss_list:
        await message.answer(_LT("dungeon.boss.not_found"))
        return

    boss = boss_list[0]
    hp_text = _hp_bar(run['hp'], run['hp_max'])
    slot_items = await _combat_slot_items(user_id, is_boss=True)
    sdata = await state.get_data()
    step = await dungeon_new_step(state)

    await state.update_data(current_enemy_id=boss['id'], current_enemy_hp=boss['hp'],
                            enemy_dots={})

    boss_status = status_lines(sdata)
    boss_heal_uses = int(sdata.get('dungeon_heal_uses', 0) or 0)
    if boss_heal_uses >= DUNGEON_HEAL_SOFT_LIMIT:
        bmult = heal_limit_mult(boss_heal_uses)
        boss_status.append(_LT("dungeon.boss.heal", uses=boss_heal_uses, mult=f"{bmult:.0%}"))
    status_block = "\n".join(boss_status)
    if status_block:
        status_block += "\n"
    bdesc = boss['description'] if 'description' in boss.keys() and boss['description'] else ""
    boss_name = _LT("dungeon.boss.title_final") if run['floor'] == 2 else _LT("dungeon.boss.title_mid")
    text = _LT(
        "dungeon.boss.screen", title=boss_name, floor=run['floor'], hp=hp_text,
        status=status_block, boss=boss['name'], bhp=boss['hp'], atk=boss['attack'],
        dodge=boss['dodge'] if 'dodge' in boss.keys() else 0, desc=bdesc)
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
        await callback.message.answer(_LT("resv.alert.stale_btn"))
        return
    run = await get_active_run(user_id)
    if not run:
        await callback.message.answer(_LT("dungeon.msg.not_found_active"))
        await state.clear()
        return
    data = await state.get_data()
    if not (run['floor'] == 1 and data.get('captain_defeated')):
        await callback.message.answer(_LT("dungeon.resv.locked"))
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
        await callback.message.answer(_LT("resv.alert.stale_btn"))
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
        await callback.message.answer(_LT("resv.alert.stale_btn"))
        return
    if await state.get_state() != DungeonFSM.in_reservoir.state:
        await callback.message.answer(_LT("resv.msg.not_here"))
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
        "none": _LT("resv.bait.none_plain"),
        "": _LT("resv.bait.auto_plain"),
    }.get(chosen, "")
    text = _LT("resv.bait.screen", selected=selected or chosen, junk=await junk_hint('reservoir'))
    await _resv_answer(user_id, callback.message, text, _reservoir_bait_markup(
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
        await callback.message.answer(_LT("resv.alert.stale_btn"))
        return
    if await state.get_state() != DungeonFSM.in_reservoir.state:
        await callback.message.answer(_LT("resv.msg.not_here"))
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
        await callback.message.answer(_LT("resv.alert.stale_btn"))
        return
    if await state.get_state() != DungeonFSM.in_reservoir.state:
        await callback.message.answer(_LT("resv.msg.not_here"))
        return
    if user_id in FISHING_CASTING:
        await callback.answer(_LT("resv.alert.busy"), show_alert=True)
        return
    # Лок ставим сразу, до первого await: иначе двойной тап проходит
    # проверку дважды и игрок забрасывает удочку многократно подряд.
    FISHING_CASTING.add(user_id)
    try:
        run = await get_active_run(user_id)
        if not run:
            await callback.message.answer(_LT("dungeon.msg.not_found"))
            await state.clear()
            return

        user = await get_user(user_id)
        if not user:
            return

        rod = await _rod_for(user_id)
        if not rod:
            await callback.message.answer(_LT("resv.msg.no_rod"))
            return

        if user['ap'] < RESERVOIR_AP_COST:
            await callback.message.answer(
                _LT("resv.msg.no_ap", cost=RESERVOIR_AP_COST, ap=user['ap'])
            )
            return
        ok = await remove_ap(user_id, RESERVOIR_AP_COST, reason="рыбалка в водохранилище")
        if not ok:
            await callback.message.answer(_LT("resv.msg.ap_fail"))
            return

        chosen = (user.get('fishing_bait') or "").strip()
        bait_name, bait_id = await _resolve_bait(user_id, chosen)
        if bait_id is not None:
            await remove_inventory_item(user_id, bait_id, 1)

        # Перебиваем старую кнопку заброса (защита от двойного списания ОД).
        await dungeon_new_step(state)

        # Пока идёт ожидание улова — держим лок: выйти, продолжить путь и
        # повторный заброс блокируются (middleware FishingActiveLock + гарды ниже).
        bait_part = _LT("resv.bait.with", name=bait_name) if bait_name else _LT("resv.bait.without")
        cast_photo = _reservoir_photo()
        if cast_photo and not os.path.isfile(cast_photo):
            cast_photo = None
        await _resv_answer(
            user_id, callback.message,
            _LT("resv.cast.wait", bait=bait_part),
            _reservoir_wait_markup(),
            photo=cast_photo)

        await asyncio.sleep(random.uniform(4, 7))

        # Забег мог завершиться (рестарт/форс-выход), пока мы ждали —
        # результат не отдаём и улов не пишем.
        run = await get_active_run(user_id)
        if not run or await state.get_state() != DungeonFSM.in_reservoir.state:
            # Причину фиксируем в activity_log: раньше эта ветка молчала, и
            # «зависшее» окно заброса нельзя было разобрать по логам.
            try:
                await log_activity(
                    user_id, "resv_cast_lost",
                    "Заброс в водохранилище без результата: "
                    f"забег={'нет' if not run else 'есть'}, "
                    f"состояние={await state.get_state()}")
            except Exception:
                pass
            try:
                await _resv_answer(user_id, callback.message,
                                   _LT("resv.cast.lost"),
                                   _reservoir_wait_markup())
            except Exception:
                pass
            return

        fresh = await get_user(user_id) or {}
        _ap = fresh.get('ap', 0) or 0
        _ap_max = fresh.get('ap_max', _ap) or _ap
        ap_line = _LT("forest.ap_line", ap=_ap, ap_max=_ap_max)
        if _ap < RESERVOIR_AP_COST:
            ap_line += _LT("resv.ap_next_short", cost=RESERVOIR_AP_COST)
        else:
            ap_line += _LT("resv.ap_next_ok")
        bait = await _bait_line(user_id, chosen)
        ap_block = f"\n\n{ap_line}\n{bait}"

        next_step = await dungeon_new_step(state)

        # ── редкий боевой улов: вместо рыбы — мутировавший моллюск ──
        if await _mollusk_start(callback, state, user_id):
            return

        if bait_name:
            chance = _catch_chance(rod, bait_name, (await get_award_bonus(callback.from_user.id))['fishing'])
            caught = random.random() * 100 < chance
            if caught:
                fish_name = await _pick_reservoir_fish()
                item = await get_item_by_name(fish_name)
                if not item:
                    result = _LT("resv.catch.error")
                else:
                    weight_idx = _roll_fish_weight()
                    tier = fish_weight_tier(weight_idx)
                    sell = fish_sell_price(item['sell_price'], weight_idx)
                    kind = await get_water_fish_kind("reservoir", fish_name)
                    await add_fish_catch(user_id, item['id'], weight_idx, kind=kind)
                    await log_activity(user_id, "dungeon_reservoir_fish",
                                       f"Поймал «{fish_name}» ({tier['label']}) в водохранилище")
                    if kind == "fish":
                        await bump_achievement(user_id, "fishing", 1)
                    if fish_name == "Светящаяся форель":
                        name_line = _LT("resv.catch.glow")
                    elif fish_name == "Искрящийся угорь":
                        name_line = _LT("resv.catch.eel")
                    else:
                        name_line = _LT("resv.catch.catfish")
                    result = _LT(
                        "resv.catch.hit", emoji=RESERVOIR_EMOJI.get(fish_name, '🐟'), fish=fish_name,
                        tier=tier['label'].lower(), name_line=name_line, sell=sell,
                        money=plural_nordmark(sell)) + ap_block
                    wf_photo = await get_water_fish_photo_by_name("reservoir", fish_name)
                    local_photo = item_local_photo(fish_name) if not wf_photo else None
                    await _resv_answer(user_id, callback.message, result, _reservoir_result_markup(next_step),
                                       photo=local_photo or (None if wf_photo else _reservoir_photo()),
                                       photo_id=wf_photo)
                    return
            else:
                # Промах с наживкой: шанс вытащить водоросли (как на озере).
                if random.random() * 100 < FISH_BAIT_MISS_SEAWEED_CHANCE:
                    sea = await get_item_by_name("Кусочек водорослей")
                    if sea:
                        kind = await get_water_fish_kind("reservoir", "Кусочек водорослей")
                        await add_fish_catch(user_id, sea['id'], 1, kind=kind or "resource")
                        await log_activity(user_id, "dungeon_reservoir_fish",
                                           "Промах с наживкой, выловил «Кусочек водорослей»")
                        result = _LT("resv.seaweed.hit") + ap_block
                        jphoto = await junk_photo("reservoir", "Кусочек водорослей")
                        if jphoto:
                            await _resv_answer(user_id, callback.message, result,
                                               _reservoir_result_markup(next_step),
                                               photo_id=jphoto)
                            return
                        local_photo = item_local_photo("Кусочек водорослей")
                        if local_photo:
                            await _resv_answer(user_id, callback.message, result,
                                               _reservoir_result_markup(next_step),
                                               photo=local_photo)
                            return
                        await _resv_answer(user_id, callback.message, result,
                                           _reservoir_result_markup(next_step),
                                           photo=_reservoir_photo())
                        return
                result = _LT("resv.catch.miss")
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
                        sell_line = _LT("resv.junk.sell", price=junk_item['sell_price'],
                                        money=plural_nordmark(junk_item['sell_price']))
                    result = _LT("resv.junk.hit", junk=junk_name, sell_line=sell_line) + ap_block
                    jphoto = await junk_photo("reservoir", junk_name)
                    if jphoto:
                        await _resv_answer(user_id, callback.message, result, _reservoir_result_markup(next_step),
                                           photo_id=jphoto)
                        return
                    local_photo = item_local_photo(junk_name)
                    if local_photo:
                        await _resv_answer(user_id, callback.message, result, _reservoir_result_markup(next_step),
                                           photo=local_photo)
                    else:
                        await _resv_answer(user_id, callback.message, result,
                                           _reservoir_result_markup(next_step),
                                           photo=_reservoir_photo())
                    return
                else:
                    result = _LT("resv.junk.lost")
            else:
                result = _LT("resv.junk.none")
        result += ap_block
        await _resv_answer(user_id, callback.message, result,
                           _reservoir_result_markup(next_step),
                           photo=_reservoir_photo())
    finally:
        FISHING_CASTING.discard(user_id)


@router.callback_query(F.data == "resv:recover")
async def resv_recover(callback: CallbackQuery, state: FSMContext):
    """Восстановление окна водохранилища, если результат заброса потерялся.

    Единственная кнопка на экране «Ждёшь...»: перерисовывает меню водохранилища
    заново. ОД и наживку не тратит. Нужна после рестарта процесса (деплой,
    OOM-kill), когда ждать уже нечего, а окно осталось без кнопок.
    """
    user_id = callback.from_user.id
    if user_id in FISHING_CASTING:
        await callback.answer(_LT("resv.alert.pending"),
                              show_alert=True)
        return
    await callback.answer()
    run = await get_active_run(user_id)
    if not run:
        await state.clear()
        await callback.message.answer(
            _LT("resv.recover.no_run")
        )
        return
    if await state.get_state() == DungeonFSM.in_reservoir.state:
        await show_reservoir(callback.message, user_id, state)
        return
    await callback.message.answer(
        _LT("resv.recover.gone")
    )


@router.callback_query(F.data.regexp(r"^resv:deeper:\d+$"))
async def resv_deeper(callback: CallbackQuery, state: FSMContext):
    """Спуск на 2-й этаж (из выбора после капитана или из водохранилища)."""
    await callback.answer()
    user_id = callback.from_user.id
    parts = callback.data.split(":")
    if parts[2] != str(await dungeon_current_step(state)):
        await _log_stale(callback, "данж: устаревшая кнопка водохранилища")
        await callback.message.answer(_LT("resv.alert.stale_btn"))
        return
    if user_id in FISHING_CASTING:
        await callback.answer(_LT("resv.alert.wait"), show_alert=True)
        return
    run = await get_active_run(user_id)
    if not run:
        await callback.message.answer(_LT("dungeon.msg.not_found"))
        await state.clear()
        return
    if run['floor'] >= 2:
        await callback.message.answer(_LT("resv.deeper.bottom"))
        return
    await advance_floor(run['id'], 2)
    await state.update_data(captain_defeated=None)
    await state.set_state(DungeonFSM.in_dungeon)
    run = await get_active_run(user_id)
    await log_activity(user_id, "dungeon_floor", "Спустился на 2-й этаж (лог Короля крыс)")
    await close_reservoir_window(user_id, callback.bot)
    await callback.message.answer(
        _LT("resv.deeper.stairs"),
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
        await callback.message.answer(_LT("resv.alert.stale_btn"))
        return
    if await state.get_state() != DungeonFSM.in_reservoir.state:
        await callback.message.answer(_LT("resv.msg.not_here"))
        return
    await _resv_eq_view(callback.message, user_id, state)


async def _resv_eq_view(where, user_id: int, state: FSMContext):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    eq = await get_equipment(user_id)
    step = await dungeon_new_step(state)
    lines = [_LT("resv.eq.head"), "", _LT("resv.eq.intro"), ""]
    for slot in ('potion1', 'potion2'):
        item_id = eq.get(slot)
        it = await get_item(item_id) if item_id else None
        lines.append(f"⚗️ {EQUIPMENT_SLOT_LABELS[slot]}: {it['name'] if it else '—'}")
    rows = [
        [InlineKeyboardButton(text=_LT("resv.eq.slot1"), callback_data=f"resv:eqslot:potion1:{step}")],
        [InlineKeyboardButton(text=_LT("resv.eq.slot2"), callback_data=f"resv:eqslot:potion2:{step}")],
        [InlineKeyboardButton(text=_LT("resv.eq.back"), callback_data=f"resv:menu:{step}")],
    ]
    await _resv_answer(user_id, where, "\n".join(lines), InlineKeyboardMarkup(inline_keyboard=rows))


@router.callback_query(F.data.regexp(r"^resv:eqslot:[a-z0-9_]+:\d+$"))
async def resv_eqslot(callback: CallbackQuery, state: FSMContext):
    """Выбор расходника для слота."""
    await callback.answer()
    user_id = callback.from_user.id
    parts = callback.data.split(":")
    slot = parts[2]
    if parts[3] != str(await dungeon_current_step(state)):
        await _log_stale(callback, "данж: устаревшая кнопка водохранилища")
        await callback.message.answer(_LT("resv.alert.stale_btn"))
        return
    if await state.get_state() != DungeonFSM.in_reservoir.state:
        await callback.message.answer(_LT("resv.msg.not_here"))
        return

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    eq = await get_equipment(user_id)
    equipped_id = eq.get(slot)
    items = await get_inventory(user_id)
    candidates = [it for it in items if item_fits_slot(it, slot)]
    step = await dungeon_new_step(state)

    text = _LT("resv.eqslot.head", slot=EQUIPMENT_SLOT_LABELS[slot])
    if equipped_id:
        it = await get_item(equipped_id)
        text += _LT("resv.eqslot.set", name=it['name'] if it else equipped_id)
    else:
        text += _LT("resv.eqslot.empty")
    if candidates:
        text += _LT("resv.eqslot.fits")
    else:
        text += _LT("resv.eqslot.none")

    rows = []
    if equipped_id:
        rows.append([InlineKeyboardButton(text=_LT("resv.eqslot.clear"),
                                          callback_data=f"resv:eqclear:{slot}:{step}")])
    for it in candidates:
        marker = "✅ " if it['id'] == equipped_id else ""
        rows.append([InlineKeyboardButton(
            text=f"{marker}{it['name']} x{it['quantity']}",
            callback_data=f"resv:eqset:{slot}:{it['id']}:{step}")])
    rows.append([InlineKeyboardButton(text=_LT("resv.eq.back_gear"), callback_data=f"resv:eq:{step}")])
    await _resv_answer(user_id, callback.message, text, InlineKeyboardMarkup(inline_keyboard=rows))


@router.callback_query(F.data.regexp(r"^resv:eqset:[a-z0-9_]+:\d+:\d+$"))
async def resv_eqset(callback: CallbackQuery, state: FSMContext):
    """Установка предмета в слот расходников."""
    await callback.answer()
    user_id = callback.from_user.id
    parts = callback.data.split(":")
    slot, item_id = parts[2], int(parts[3])
    if parts[4] != str(await dungeon_current_step(state)):
        await _log_stale(callback, "данж: устаревшая кнопка водохранилища")
        await callback.message.answer(_LT("resv.alert.stale_btn"))
        return
    if await state.get_state() != DungeonFSM.in_reservoir.state:
        await callback.message.answer(_LT("resv.msg.not_here"))
        return
    item = await get_item(item_id)
    if not item:
        await callback.message.answer(_LT("resv.eqset.no_item"))
        return
    await set_equipment_slot(user_id, slot, item_id)
    await callback.message.answer(_LT("resv.eqset.done", name=item['name']))
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
        await callback.message.answer(_LT("resv.alert.stale_btn"))
        return
    if await state.get_state() != DungeonFSM.in_reservoir.state:
        await callback.message.answer(_LT("resv.msg.not_here"))
        return
    eq = await get_equipment(user_id)
    item_id = eq.get(slot)
    if item_id:
        await clear_equipment_slot(user_id, slot)
        it = await get_item(item_id)
        await callback.message.answer(_LT("resv.eqclear.done", name=it['name'] if it else _LT("resv.eqclear.item")))
    await _resv_eq_view(callback.message, user_id, state)


@router.callback_query(F.data == "dungeon:exit")
async def dungeon_exit(callback: CallbackQuery, state: FSMContext):
    """Запрос подтверждения выхода из подземелья (против случайного клика)."""
    await callback.answer()
    user_id = callback.from_user.id

    # Во время боя с боссом покинуть подземелье нельзя.
    if await state.get_state() == DungeonFSM.in_boss.state:
        await callback.message.answer(
            _LT("dungeon.exit.boss"),
        )
        return

    # Пока идёт рыбалка — сначала дождись улова.
    if user_id in FISHING_CASTING:
        await callback.answer(_LT("resv.alert.wait"), show_alert=True)
        return

    run = await get_active_run(user_id)
    if not run:
        await callback.message.answer(_LT("dungeon.msg.not_found"))
        await state.clear()
        return

    loot_nm = run['loot_nm'] or 0
    run_items = await get_run_items(run['id'])

    parts = []
    if loot_nm > 0:
        parts.append(_LT("dungeon.exit.nm", nm=loot_nm))
    parts.extend(f"🎁 {n} x{q}" for n, q in run_items)
    loot_text = "\n".join(parts) if parts else _LT("dungeon.exit.nothing")

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    await callback.message.answer(
        _LT("dungeon.exit.confirm", loot=loot_text),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=_LT("dungeon.exit.yes"), callback_data="dungeon:exit:confirm")],
            [InlineKeyboardButton(text=_LT("dungeon.exit.no"), callback_data="dungeon:exit:cancel")],
        ])
    )


@router.callback_query(F.data == "dungeon:exit:confirm")
async def dungeon_exit_confirm(callback: CallbackQuery, state: FSMContext):
    """Фактический выход: перенос лута, начисление НМ, завершение забега."""
    await callback.answer()
    user_id = callback.from_user.id
    run = await get_active_run(user_id)
    if not run:
        await callback.message.answer(_LT("dungeon.msg.not_found"))
        await state.clear()
        return

    loot_nm = run['loot_nm'] or 0
    items = await transfer_run_items_to_inventory(user_id, run['id'])
    if loot_nm > 0:
        await add_nordmarks(user_id, loot_nm, "dungeon_exit", "Вынесено из подземелья")
    await end_run(run['id'], 0)
    onhit.unregister(user_id)
    await log_activity(user_id, "dungeon_exit", "Покинул подземелье (досрочный выход)")

    parts = []
    if loot_nm > 0:
        parts.append(_LT("dungeon.exit.nm", nm=loot_nm))
    parts.extend(f"🎁 {n} x{q}" for n, q in items)

    if parts:
        text = _LT("dungeon.exit.leave", loot="\n".join(parts))
    else:
        text = _LT("dungeon.exit.empty_leave")

    await close_reservoir_window(user_id, callback.bot)
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.message.answer(_LT("dungeon.exit.again", text=text), reply_markup=dungeon_start_keyboard())
    await state.clear()


@router.callback_query(F.data == "dungeon:exit:cancel")
async def dungeon_exit_cancel(callback: CallbackQuery, state: FSMContext):
    """Отмена выхода — возврат к текущему экрану подземелья."""
    await callback.answer(_LT("dungeon.exit.continue"), show_alert=False)
    user_id = callback.from_user.id
    run = await get_active_run(user_id)
    if not run:
        await callback.message.answer(_LT("dungeon.msg.not_found"))
        await state.clear()
        return
    # Промежуточный запрос на выход больше не нужен — убираем его, чтобы
    # рядом с окном водохранилища не оставалось второго сообщения с кнопками.
    try:
        await callback.message.delete()
    except Exception:
        pass
    await resume_dungeon(callback.message, run, user_id, state)
