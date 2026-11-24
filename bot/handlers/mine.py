"""Железная копи: ресурсная локация (v0.31.0).

Пилот входит в копь (локация city «Железная копи», вход с «Пилота 1 класса»)
и бьёт породу («⛏ Добыть руду»): 15 ОД за попытку, результат через 7–15 секунд.
Без кирки копать нельзя. Шанс находки — база 30% плюс надбавка за ступень кирки
(базовая кирка ранг 1 → +15%, итого 45%), не выше MINE_CHANCE_CAP.

Врагов в копи пока один — Летучая мышь. Как в сборе грибов, её встреча
бросается ПЕРЕД находкой руды и заменяет её (мышь прерывает добычу): свой шанс
(MINE_BAT_CHANCE) плюс гарантия не реже, чем раз в MINE_BAT_PITY_TARGET попыток.
Победа над мышью — редкий самоцвет (не больше одного за бой), поражение —
−MINE_BAT_SEED['loss_ap'] ОД, после чего можно вернуться к добыче.
"""

import asyncio
import os
import random

from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database.db import (
    get_user, remove_ap, get_active_run, add_inventory_item,
    get_item, get_item_by_name, get_inventory_item,
    get_source_enemy_by_key, get_source_enemy_drops, roll_enemy_drops,
    enemy_encounter_hit,
    get_mine_bat_attempts, set_mine_bat_attempts, reset_mine_bat_counter,
    remove_ap_or_floor, user_is_tourist, log_activity,
    get_location_by_key, location_photo_for_tod, location_mine_level_photo,
    bump_achievement, get_achievement_bonus,
)
from utils.helpers import (
    resolve_image_seasonal, season_key, time_of_day_key, plural_nordmark,
)
from utils import onhit
from config import (
    MINE_AP_COST, MINE_BASE_CHANCE, MINE_PICKAXE_BONUS_PER_RANK, MINE_CHANCE_CAP,
    MINE_RESULT_DELAY, MINE_PICKAXE_NAME, MINE_ORE_NAME, MINE_GEM_CAP,
    MINE_BAT_KEY, MINE_BAT_SPOT, MINE_BAT_SEED,
)

router = Router()

MINE_HOME_PHOTO = "city/mine"
MINE_LEVEL_PHOTO = "city/mine_level"
MINE_BAT_EMOJI = "🦇"

# Пользователи, чья добыча ещё не завершена (защита от повторного клика).
MINE_CASTING = set()

# Отслеживаемое сообщение окна копи: user_id -> (chat_id, message_id).
MINE_MSG: dict = {}

# Токен текущего окна копи: уход в другое меню инвалидирует старые кнопки.
MINE_TOKEN: dict = {}

# Активные бои с Летучей мышью: user_id -> {token, player_hp, bat_hp, round, ...}.
MINE_BATTLE: dict = {}


def _new_token() -> str:
    return str(random.randint(100000, 999999))


async def deactivate_mine(user_id: int):
    """Инвалидация окна копи при уходе в другое меню (магазин, город и т.п.)."""
    MINE_TOKEN.pop(user_id, None)
    MINE_MSG.pop(user_id, None)
    MINE_CASTING.discard(user_id)
    MINE_BATTLE.pop(user_id, None)
    onhit.unregister(user_id)


def _callback_token(data: str) -> str:
    """Токен окна копи из callback_data (последний числовой сегмент)."""
    for part in reversed(data.split(":")[1:]):
        if part.isdigit():
            return part
    return ""


async def _mine_ok(callback) -> bool:
    """Step-guard: callback должен приходить из текущего окна копи."""
    token = _callback_token(callback.data)
    if MINE_TOKEN.get(callback.from_user.id) != token:
        try:
            await log_activity(callback.from_user.id, "stale_button", "копи: устаревшее окно")
        except Exception:
            pass
        from utils.localization import t as _tmine
        await callback.answer(_tmine("mine.stale"), show_alert=True)
        return False
    return True


def _mine_path() -> str:
    """Картинка копи: сезонный локальный файл с фолбэками."""
    path = resolve_image_seasonal(MINE_HOME_PHOTO)
    if not os.path.isfile(path):
        path = resolve_image_seasonal("city/forest")
    if not os.path.isfile(path):
        path = resolve_image_seasonal("city/park")
    return path


async def _mine_media() -> tuple:
    """Картинка входа в копь: (photo_id, media_path).

    Берём фото локации из админ-редактора (season_photos → photo_<tod>), а без
    него — локальный сезонный файл. Как у опушки леса: картинка задаётся админом.
    """
    loc = await get_location_by_key("mine")
    if loc:
        photo_id = location_photo_for_tod(loc, season_key(), time_of_day_key())
        if photo_id:
            return photo_id, None
    return None, _mine_path()


def _level_path() -> str:
    """Картинка 1-го уровня шахт: сезонный локальный файл с фолбэком на вход."""
    path = resolve_image_seasonal(MINE_LEVEL_PHOTO)
    if not os.path.isfile(path):
        path = _mine_path()
    return path


async def _level_media() -> tuple:
    """Картинка 1-го уровня шахт: (photo_id, media_path).

    Своя картинка из админ-редактора локации (как опушка у леса), иначе —
    локальный сезонный файл city/mine_level_<сезон>.jpg, иначе картинка входа.
    """
    loc = await get_location_by_key("mine")
    if loc:
        photo_id = location_mine_level_photo(loc)
        if photo_id:
            return photo_id, None
    return None, _level_path()


async def _paint(callback, *, text: str = None, media_path: str = None, photo_id: str = None, kb=None):
    """Единая отрисовка окна копи в одном сообщении на игрока."""
    bot = callback.message.bot
    chat_id = callback.message.chat.id
    user_id = callback.from_user.id
    entry = MINE_MSG.get(user_id)
    target_id = entry[1] if entry and entry[0] == chat_id else None

    if target_id is not None:
        try:
            if media_path or photo_id:
                from aiogram.types import InputMediaPhoto
                await bot.edit_message_media(
                    chat_id, target_id,
                    media=InputMediaPhoto(media=photo_id or FSInputFile(media_path), caption=text),
                    reply_markup=kb,
                )
            else:
                await bot.edit_message_text(chat_id, target_id, text=text, reply_markup=kb)
            return
        except Exception:
            pass

    if target_id is not None and target_id != callback.message.message_id:
        try:
            await bot.delete_message(chat_id, target_id)
        except Exception:
            pass
    if media_path or photo_id:
        sent = await bot.send_photo(chat_id, photo_id or FSInputFile(media_path), caption=text, reply_markup=kb)
    else:
        sent = await bot.send_message(chat_id, text, reply_markup=kb)
    MINE_MSG[user_id] = (chat_id, sent.message_id)


async def _mine_paint(callback, *, text: str, kb=None):
    """Отрисовка окна копи на фоне её картинки."""
    photo_id, media_path = await _mine_media()
    await _paint(callback, text=text, photo_id=photo_id, media_path=media_path, kb=kb)


async def _level_paint(callback, *, text: str, kb=None):
    """Отрисовка окна 1-го уровня шахт (место добычи руды)."""
    photo_id, media_path = await _level_media()
    await _paint(callback, text=text, photo_id=photo_id, media_path=media_path, kb=kb)


async def _enemy_paint(callback, *, text: str, kb=None, image=None):
    """Отрисовка боя на фото врага; без него — на картинке уровня.

    image — file_id (фото, загруженное ботом) или локальный путь к файлу.
    """
    if image:
        if os.path.isfile(image):
            await _paint(callback, text=text, media_path=image, kb=kb)
        else:
            await _paint(callback, text=text, photo_id=image, kb=kb)
        return
    await _level_paint(callback, text=text, kb=kb)


# ───────── чистые функции (тестируются в smoke) ─────────

async def _mine_card(user_id: int, chance: int) -> str:
    """Исход обычной попытки копи из персонального мешка (руда или пусто)."""
    from config import GATHER_BAG_SIZE
    from database.db import draw_gather_card
    return await draw_gather_card(user_id, "mine",
                                  {"ore": chance, "none": GATHER_BAG_SIZE - chance})


def mine_ore_chance(pickaxe_rank: int, mining_bonus: int = 0) -> int:
    """Шанс успешной добычи руды, % : база + надбавка кирки + бонус наград.

    pickaxe_rank — ступень кирки (ранг = редкость предмета); линейно повышает
    шанс на MINE_PICKAXE_BONUS_PER_RANK за ступень. Итог не выше MINE_CHANCE_CAP.
    """
    rank = max(1, int(pickaxe_rank or 1))
    chance = MINE_BASE_CHANCE + MINE_PICKAXE_BONUS_PER_RANK * rank + int(mining_bonus or 0)
    return min(MINE_CHANCE_CAP, max(0, chance))


def cap_gem_drops(picked: list, cap: int = MINE_GEM_CAP) -> list:
    """Ограничивает число выпавших самоцветов кэпом (по умолчанию один за бой).

    Дропы врага бросаются независимо, поэтому могут сработать несколько сразу.
    Если выпало больше cap — оставляем случайные cap.
    """
    picked = list(picked or [])
    if cap <= 0:
        return []
    if len(picked) <= cap:
        return picked
    return random.sample(picked, cap)


async def _pickaxe_for(user_id: int):
    """Кирка игрока (предмет + наличие в инвентаре) или None."""
    item = await get_item_by_name(MINE_PICKAXE_NAME)
    if not item:
        return None
    inv = await get_inventory_item(user_id, item['id'])
    if not inv or inv['quantity'] < 1:
        return None
    return item


async def _bat():
    """Строка врага Летучей мыши из БД (или None)."""
    return await get_source_enemy_by_key("mine", MINE_BAT_KEY, spot=MINE_BAT_SPOT)


def _bat_fallback() -> dict:
    """Параметры мыши из конфига — если строки в БД ещё нет (до сида)."""
    return dict(MINE_BAT_SEED)


def _bat_emoji(enemy: dict | None) -> str:
    return MINE_BAT_EMOJI


def _hp_bar(hp: int, hp_max: int) -> str:
    hp = max(0, int(hp))
    hp_max = max(1, int(hp_max))
    filled = round(10 * hp / hp_max)
    return "█" * filled + "░" * (10 - filled)


def _enter_markup(token: str):
    """Меню входа в копь: спуск на 1-й уровень и выход в город."""
    from utils.localization import t as _tb
    rows = [
        [InlineKeyboardButton(text=_tb("mine.btn.level1"), callback_data=f"mine:level:{token}")],
        [InlineKeyboardButton(text=_tb("city.back"), callback_data="city:menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _level_markup(token: str):
    """Меню 1-го уровня шахт: добыча, спуск глубже, выход из шахты."""
    from utils.localization import t as _tb
    rows = [
        [InlineKeyboardButton(text=_tb("mine.btn.dig"), callback_data=f"mine:dig:{token}")],
        [InlineKeyboardButton(text=_tb("mine.btn.deeper"), callback_data=f"mine:deeper:{token}")],
        [InlineKeyboardButton(text=_tb("mine.btn.exit"), callback_data=f"mine:menu:{token}")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _result_markup(token: str):
    from utils.localization import t as _tb
    rows = [
        [InlineKeyboardButton(text=_tb("mine.btn.dig_again"), callback_data=f"mine:dig:{token}")],
        [InlineKeyboardButton(text=_tb("mine.btn.exit"), callback_data=f"mine:menu:{token}")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _battle_markup(token: str):
    from utils.localization import t as _tb
    rows = [
        [InlineKeyboardButton(text=_tb("mine.btn.hit"), callback_data=f"mine:battle:hit:{token}")],
        [InlineKeyboardButton(text=_tb("mine.btn.flee"), callback_data=f"mine:battle:flee:{token}")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def _ap_line(user_id: int) -> str:
    """Строка остатка ОД для окна копи (аналог ОД в лесу)."""
    fresh = await get_user(user_id) or {}
    ap = fresh.get('ap', 0) or 0
    ap_max = fresh.get('ap_max', ap) or ap
    from utils.localization import t as _tp
    line = _tp("mine.ap_line", ap=ap, ap_max=ap_max)
    from database.db import gather_ap_cost
    ap_cost = await gather_ap_cost(user_id, "mining", MINE_AP_COST)
    if ap < ap_cost:
        line += _tp("mine.ap_short", cost=ap_cost)
    else:
        line += _tp("mine.ap_ok")
    return line


async def mine_menu_cb(callback: CallbackQuery):
    """Вход в Железную копи (location:enter:mine)."""
    await callback.answer()

    from utils.localization import t as _tmine
    if await user_is_tourist(callback.from_user.id):
        await callback.message.answer(_tmine("mine.tourist"))
        return

    if await get_active_run(callback.from_user.id):
        await callback.message.answer(_tmine("mine.in_dungeon"))
        return

    token = _new_token()
    MINE_TOKEN[callback.from_user.id] = token

    pickaxe = await _pickaxe_for(callback.from_user.id)
    if pickaxe:
        hint = _tmine("mine.hint.has_pickaxe", name=pickaxe['name'])
    else:
        hint = _tmine("mine.hint.no_pickaxe")

    caption = _tmine("mine.entrance", hint=hint)
    await _mine_paint(callback, text=caption, kb=_enter_markup(token))


@router.callback_query(F.data.regexp(r"^mine:menu:\d+$"))
async def mine_menu_again(callback: CallbackQuery):
    if not await _mine_ok(callback):
        return
    await mine_menu_cb(callback)


@router.callback_query(F.data.regexp(r"^mine:level:\d+$"))
async def mine_level_cb(callback: CallbackQuery):
    """1-й уровень шахт: место добычи руды (своя картинка, кнопки добычи/спуска)."""
    if not await _mine_ok(callback):
        return
    await callback.answer()
    user_id = callback.from_user.id

    from utils.localization import t as _tl1
    pickaxe = await _pickaxe_for(user_id)
    if pickaxe:
        rank = pickaxe['rarity'] or 1
        mining_bonus = await get_achievement_bonus(user_id, "mining", "mining_pct")
        chance = mine_ore_chance(rank, mining_bonus=mining_bonus)
        pickaxe_line = _tl1("mine.level.pickaxe_has", name=pickaxe['name'], rank=rank, chance=chance)
        dig_line = _tl1("mine.level.dig_hint")
    else:
        pickaxe_line = _tl1("mine.level.pickaxe_none")
        dig_line = _tl1("mine.level.no_pickaxe_hint")

    from database.db import gather_ap_cost
    ap_cost = await gather_ap_cost(user_id, "mining", MINE_AP_COST)
    caption = _tl1("mine.level.screen", pickaxe_line=pickaxe_line, dig_line=dig_line,
                   cost=ap_cost, lo=MINE_RESULT_DELAY[0], hi=MINE_RESULT_DELAY[1],
                   ap_line=await _ap_line(user_id))
    from utils.mine_progress import get_ore_total
    from config import MINE_LEVEL2_ORE_TARGET
    caption += "\n\n" + _tl1("mine.progress", cur=await get_ore_total(), target=MINE_LEVEL2_ORE_TARGET)
    await _level_paint(callback, text=caption,
                       kb=_level_markup(MINE_TOKEN.get(user_id, "")))


@router.callback_query(F.data.regexp(r"^mine:deeper:\d+$"))
async def mine_deeper(callback: CallbackQuery):
    """Спуск на 2-й уровень шахт — пока не обустроен (заглушка)."""
    if not await _mine_ok(callback):
        return
    from utils.localization import t as _tdeep
    await callback.answer(_tdeep("mine.deeper_stub"), show_alert=True)


@router.callback_query(F.data.regexp(r"^mine:dig:\d+$"))
async def mine_dig(callback: CallbackQuery):
    if not await _mine_ok(callback):
        return
    user_id = callback.from_user.id

    if await user_is_tourist(user_id):
        from utils.localization import t as _ta
        await callback.answer(_ta("mine.alert.tourist"), show_alert=True)
        return
    if user_id in MINE_CASTING:
        from utils.localization import t as _ta
        await callback.answer(_ta("mine.alert.busy"), show_alert=True)
        return

    # Лок ставим сразу, до первого await: иначе двойной тап проходит дважды.
    MINE_CASTING.add(user_id)
    try:
        if await get_active_run(user_id):
            from utils.localization import t as _ta
            await callback.answer(_ta("mine.alert.in_dungeon"), show_alert=True)
            return

        user = await get_user(user_id)
        if not user:
            await callback.answer("Сначала нажми /start", show_alert=True)
            return

        from utils.localization import t as _tmine
        pickaxe = await _pickaxe_for(user_id)
        if not pickaxe:
            await _level_paint(
                callback,
                text=_tmine("mine.no_pickaxe"),
                kb=_level_markup(MINE_TOKEN.get(user_id, "")),
            )
            return

        from database.db import gather_ap_cost
        ap_cost = await gather_ap_cost(user_id, "mining", MINE_AP_COST)
        if not await remove_ap(user_id, ap_cost, reason="добыча руды"):
            await _level_paint(
                callback,
                text=_tmine("mine.no_ap", cost=ap_cost),
                kb=_level_markup(MINE_TOKEN.get(user_id, "")),
            )
            return

        delay = random.randint(*MINE_RESULT_DELAY)
        await _level_paint(
            callback,
            text=_tmine("mine.swing", delay=delay),
            kb=None,
        )
        await log_activity(user_id, "mine", f"Добыча руды: удар киркой ({ap_cost} ОД)")
        await asyncio.sleep(delay)

        # ── встреча с Летучей мышью: бросок ПЕРЕД находкой (как грибы/рыбалка) ──
        bat = await _bat()
        encountered = False
        attempts = 0
        if bat and bat.get('enabled', 1):
            attempts = await get_mine_bat_attempts(user_id)
            chance = float(bat.get('chance') or 0)
            pity = int(bat.get('pity_target') or 0)
            if enemy_encounter_hit(chance, random.random() * 100, attempts, pity):
                encountered = True

        if encountered:
            await reset_mine_bat_counter(user_id)
            await _start_battle(callback, user_id, bat)
            return

        # Мышь не встретилась — счётчик гарантии растёт (если враг включён).
        if bat and bat.get('enabled', 1):
            await set_mine_bat_attempts(user_id, attempts + 1)

        # ── находка руды ──
        rank = pickaxe['rarity'] or 1
        mining_bonus = await get_achievement_bonus(user_id, "mining", "mining_pct")
        chance = mine_ore_chance(rank, mining_bonus=mining_bonus)
        head = "⛏ ЖЕЛЕЗНАЯ КОПЬ"
        ap_block = f"\n\n{await _ap_line(user_id)}"
        result_kb = _result_markup(MINE_TOKEN.get(user_id, ""))
        from config import FIRE_ORE_NAME, FIRE_ORE_CHANCE
        from database.db import tree_collect_allowed, tree_record_collect
        flame = None
        if (await tree_collect_allowed(user_id, FIRE_ORE_NAME)
                and random.random() * 100 < FIRE_ORE_CHANCE):
            flame = await get_item_by_name(FIRE_ORE_NAME)
        from utils.localization import t as _tmd
        from config import ACTIVITY_XP_MINE_ORE, ACTIVITY_XP_MINE_ORE_SENIOR
        from utils.activity_xp import activity_xp_line
        if flame:
            await add_inventory_item(user_id, flame['id'], 1)
            await tree_record_collect(user_id, FIRE_ORE_NAME)
            await log_activity(user_id, "mine", f"Добыл «{flame['name']}»")
            xp = await activity_xp_line(user_id, ACTIVITY_XP_MINE_ORE, senior_amount=ACTIVITY_XP_MINE_ORE_SENIOR)
            text = _tmd("mine.flame_found", head=head, name=flame['name']) + ap_block + xp
        elif await _mine_card(user_id, chance) == "ore":
            ore = await get_item_by_name(MINE_ORE_NAME)
            if ore:
                await add_inventory_item(user_id, ore['id'], 1)
                await bump_achievement(user_id, "mining", 1)
                await log_activity(user_id, "mine", f"Добыл «{ore['name']}»")
                from utils.mine_progress import add_ore, start_announce
                if await add_ore(1):
                    start_announce(callback.bot)
                sell_line = ""
                if ore['sell_price'] > 0:
                    sell_line = (f"\nКазна выкупает руду по {ore['sell_price']} "
                                 f"{plural_nordmark(ore['sell_price'])} за кусок.")
                xp = await activity_xp_line(user_id, ACTIVITY_XP_MINE_ORE, senior_amount=ACTIVITY_XP_MINE_ORE_SENIOR)
                text = _tmd("mine.ore_found", head=head, name=ore['name'],
                            sell_line=sell_line) + ap_block + xp
            else:
                text = _tmd("mine.item_lost", head=head) + ap_block
        else:
            text = _tmd("mine.empty", head=head) + ap_block
        await _level_paint(callback, text=text, kb=result_kb)
    finally:
        MINE_CASTING.discard(user_id)


async def _start_battle(callback: CallbackQuery, user_id: int, bat: dict):
    """Начало мини-боя с Летучей мышью."""
    from utils.combat_model import pilot_combat_stats
    bat = bat or _bat_fallback()
    stats = await pilot_combat_stats(user_id)
    player_hp = stats['hp_max']
    token = MINE_TOKEN.get(user_id, "")
    bat_hp = int(bat.get('hp') or MINE_BAT_SEED['hp'])
    MINE_BATTLE[user_id] = {
        "token": token,
        "player_hp": player_hp,
        "player_hp_max": player_hp,
        "bat_hp": bat_hp,
        "bat_hp_max": bat_hp,
        "bat_name": bat.get('name') or "Летучая мышь",
        "emoji": _bat_emoji(bat),
        "dodge": float(bat.get('dodge') or 0),
        "armor": int(bat.get('armor') or 0),
        "dmg_min": int(bat.get('dmg_min') or MINE_BAT_SEED['dmg_min']),
        "dmg_max": int(bat.get('dmg_max') or MINE_BAT_SEED['dmg_max']),
        "loss_ap": int(bat.get('loss_ap') or MINE_BAT_SEED['loss_ap']),
        "on_hit_effects": onhit.parse_on_hit_effects(bat.get('on_hit_effects')),
        "bat": bat,
        "round": 1,
    }
    onhit.register(user_id, MINE_BATTLE[user_id])
    await _show_battle(callback)


async def _show_battle(callback: CallbackQuery, prefix: str = ""):
    battle = MINE_BATTLE.get(callback.from_user.id)
    if not battle:
        await mine_menu_cb(callback)
        return
    player_hp = battle['player_hp']
    bat_hp = battle['bat_hp']
    bat_hp_max = battle.get('bat_hp_max') or battle['bat_hp']
    bat_name = battle.get('bat_name') or "Летучая мышь"
    emoji = battle.get('emoji') or MINE_BAT_EMOJI
    effects_line = onhit.active_line(battle)
    effects_line = f"\n{effects_line}" if effects_line else ""
    from utils.localization import t as _ts
    text = (
        f"{prefix}{emoji} {bat_name.upper()}\n\n"
        + _ts("mine.bat_appears")
        + f"{emoji} {_ts('battle.hp.bat')} {_hp_bar(bat_hp, bat_hp_max)} {max(0, bat_hp)}/{bat_hp_max}\n"
        + f"🧑 {_ts('battle.hp.you')} {_hp_bar(player_hp, battle['player_hp_max'])} "
        + f"{max(0, player_hp)}/{battle['player_hp_max']}{effects_line}\n\n"
        + _ts("battle.round_note", round=battle['round'])
    )
    await _enemy_paint(callback, text=text, kb=_battle_markup(battle['token']),
                       image=(battle.get('bat') or {}).get('image'))


async def _battle_loot(user_id: int, battle: dict) -> list:
    """Лут за победу над мышью: самоцветы с кэпом MINE_GEM_CAP."""
    drops = await get_source_enemy_drops("mine", (battle.get('bat') or {}).get('id'))
    if not drops:
        return []
    picked = roll_enemy_drops(drops)
    return cap_gem_drops(picked, MINE_GEM_CAP)


@router.callback_query(F.data.regexp(r"^mine:battle:hit:\d+$"))
async def mine_battle_hit(callback: CallbackQuery):
    if not await _mine_ok(callback):
        return
    user_id = callback.from_user.id
    battle = MINE_BATTLE.get(user_id)
    if not battle:
        from utils.localization import t as _tx
        await _level_paint(
            callback,
            text=_tx("mine.bat_expired"),
            kb=_level_markup(MINE_TOKEN.get(user_id, "")),
        )
        return
    await callback.answer()
    emoji = battle.get('emoji') or MINE_BAT_EMOJI
    bat_img = (battle.get('bat') or {}).get('image')

    # DoT (яд/кровотечение, единая система v0.38.0): тикает в начале хода игрока.
    dot_dmg, dot_lines = onhit.tick_dots(battle)
    dot_note = "".join(f"{line}\n\n" for line in dot_lines)
    if dot_dmg:
        battle['player_hp'] = max(0, battle['player_hp'] - dot_dmg)
        if battle['player_hp'] <= 0:
            MINE_BATTLE.pop(user_id, None)
            onhit.unregister(user_id)
            removed = await remove_ap_or_floor(user_id, int(battle.get('loss_ap') or MINE_BAT_SEED['loss_ap']))
            await log_activity(user_id, "mine", f"Проиграл Летучей мыши (−{removed} ОД)")
            from utils.localization import t as _td
            text = (
                _td("battle.mine.bat.title", emoji=emoji) + "\n\n"
                + f"{dot_note}"
                + _td("battle.mine.bat.defeat", removed=removed)
            )
            await _enemy_paint(callback, text=text,
                               kb=_result_markup(MINE_TOKEN.get(user_id, "")),
                               image=bat_img)
            return

    # Твой удар: свой урон/крит, мышь может увернуться, броня поглощает часть.
    from utils.combat_model import pilot_combat_stats, roll_pilot_damage, roll_enemy_damage
    stats = await pilot_combat_stats(user_id, onhit.battle_state_keys(battle))
    res = roll_pilot_damage(stats, {
        'dodge': battle.get('dodge') or 0,
        'armor': battle.get('armor') or 0,
    })
    player_hit = res['damage']
    battle['bat_hp'] -= player_hit
    from utils.localization import t as _tm
    if res['dodged']:
        hit_line = _tm("battle.mine.bat.miss")
    else:
        extra = ""
        if res['armor_blocked']:
            extra += _tm("battle.mine.bat.armor", amount=res['armor_blocked'])
        if res['crit']:
            extra += _tm("battle.crit_short")
        hit_line = _tm("battle.mine.bat.hit", dmg=player_hit, extra=extra)

    if battle['bat_hp'] <= 0:
        MINE_BATTLE.pop(user_id, None)
        onhit.unregister(user_id)
        await bump_achievement(user_id, "monsters", 1)
        await log_activity(user_id, "mine", "Победил Летучую мышь в копи")
        loot = await _battle_loot(user_id, battle)
        got = []
        for entry in loot:
            item = await get_item(int(entry.get('item_id'))) if entry.get('item_id') else None
            if not item:
                continue
            await add_inventory_item(user_id, item['id'], int(entry.get('qty') or 1))
            await log_activity(user_id, "mine", f"Добыча: {item['name']}")
            got.append(item['name'])
        if got:
            loot_list = "\n".join(f"• «{name}»" for name in got)
            result_line = _tm("battle.mine.bat.loot", loot=loot_list)
        else:
            result_line = _tm("battle.mine.bat.loot_none")
        from utils.activity_xp import beast_xp_line
        xp = await beast_xp_line(user_id, "bat")
        text = (
            _tm("battle.mine.bat.title", emoji=emoji) + "\n\n"
            f"{dot_note}{hit_line}"
            + _tm("battle.mine.bat.down")
            + f"{result_line}" + xp
        )
        await _enemy_paint(callback, text=text,
                           kb=_result_markup(MINE_TOKEN.get(user_id, "")),
                           image=bat_img)
        return

    # Ответный удар мыши.
    eres = roll_enemy_damage(stats, {
        'dmg_min': battle.get('dmg_min') or MINE_BAT_SEED['dmg_min'],
        'dmg_max': battle.get('dmg_max') or MINE_BAT_SEED['dmg_max'],
        'on_hit_effects': battle.get('on_hit_effects') or [],
    })
    bat_hit = eres['damage']
    if eres['dodged']:
        counter_line = _tm("battle.mine.bat.dodged")
        bat_hit = 0
    else:
        extra = ""
        if eres['armor_blocked']:
            extra += _tm("battle.armor_absorbed_short", amount=eres['armor_blocked'])
        if eres['crit']:
            extra += _tm("battle.crit_short")
        counter_line = _tm("battle.mine.bat.counter", dmg=bat_hit, extra=extra)
    battle['player_hp'] -= bat_hit
    lifesteal_line = ""
    if not eres['dodged'] and bat_hit > 0 and battle.get('bat_hp', 0) > 0:
        ls_eff = onhit.roll_lifesteal(battle.get('on_hit_effects') or [])
        if ls_eff:
            new_bhp, healed, ls_txt = onhit.apply_lifesteal_to_attacker(
                battle.get('bat_hp', 0),
                battle.get('bat_hp_max') or battle.get('bat_hp') or 1,
                bat_hit,
                ls_eff,
            )
            if healed > 0:
                battle['bat_hp'] = new_bhp
                lifesteal_line = f"{ls_txt}\n\n"
    if battle['player_hp'] <= 0:
        MINE_BATTLE.pop(user_id, None)
        onhit.unregister(user_id)
        removed = await remove_ap_or_floor(user_id, int(battle.get('loss_ap') or MINE_BAT_SEED['loss_ap']))
        await log_activity(user_id, "mine", f"Проиграл Летучей мыши (−{removed} ОД)")
        text = (
            _tm("battle.mine.bat.title", emoji=emoji) + "\n\n"
            f"{dot_note}{hit_line}{counter_line}"
            + _tm("battle.mine.bat.defeat", removed=removed)
        )
        await _enemy_paint(callback, text=text,
                           kb=_result_markup(MINE_TOKEN.get(user_id, "")),
                           image=bat_img)
        return

    # Эффекты при ударе (v0.38.0): единая система — on_hit_effects мыши.
    proc_line = ""
    if not eres['dodged']:
        procs = onhit.roll_procs(battle.get('on_hit_effects') or [])
        if procs:
            proc_lines = onhit.apply_procs(user_id, battle, procs,
                                           enemy_name=battle.get('bat_name') or "Мышь")
            proc_line = "".join(f"{line}\n\n" for line in proc_lines)

    # Спад срочных эффектов (оглушение/ослепление и т.д.) в конце хода.
    round_note = "".join(f"{line}\n\n" for line in onhit.end_round(battle))

    battle['round'] += 1
    await _show_battle(callback, prefix=f"{dot_note}{hit_line}{counter_line}{lifesteal_line}{proc_line}{round_note}")


@router.callback_query(F.data.regexp(r"^mine:battle:flee:\d+$"))
async def mine_battle_flee(callback: CallbackQuery):
    if not await _mine_ok(callback):
        return
    user_id = callback.from_user.id
    battle = MINE_BATTLE.pop(user_id, None)
    onhit.unregister(user_id)
    await callback.answer()
    if battle:
        await log_activity(user_id, "mine", "Сбежал из боя с Летучей мышью")
    from utils.localization import t as _tf
    await _level_paint(
        callback,
        text=_tf("battle.mine.bat.flee"),
        kb=_result_markup(MINE_TOKEN.get(user_id, "")),
    )
