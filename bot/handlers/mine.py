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
        await callback.answer(
            "⏳ Это окно копи устарело — открой её заново (Город → Железная копи).",
            show_alert=True,
        )
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
    rows = [
        [InlineKeyboardButton(text="⛏ Уровень 1 шахт", callback_data=f"mine:level:{token}")],
        [InlineKeyboardButton(text="🔙 В город", callback_data="city:menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _level_markup(token: str):
    """Меню 1-го уровня шахт: добыча, спуск глубже, выход из шахты."""
    rows = [
        [InlineKeyboardButton(text="⛏ Добыть руду", callback_data=f"mine:dig:{token}")],
        [InlineKeyboardButton(text="🪜 Спуститься глубже", callback_data=f"mine:deeper:{token}")],
        [InlineKeyboardButton(text="🚪 Выйти из шахты", callback_data=f"mine:menu:{token}")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _result_markup(token: str):
    rows = [
        [InlineKeyboardButton(text="⛏ Добыть ещё", callback_data=f"mine:dig:{token}")],
        [InlineKeyboardButton(text="🚪 Выйти из шахты", callback_data=f"mine:menu:{token}")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _battle_markup(token: str):
    rows = [
        [InlineKeyboardButton(text="⚔️ Ударить", callback_data=f"mine:battle:hit:{token}")],
        [InlineKeyboardButton(text="🏃 Сбежать", callback_data=f"mine:battle:flee:{token}")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def _ap_line(user_id: int) -> str:
    """Строка остатка ОД для окна копи (аналог ОД в лесу)."""
    fresh = await get_user(user_id) or {}
    ap = fresh.get('ap', 0) or 0
    ap_max = fresh.get('ap_max', ap) or ap
    line = f"⚡ ОД: {ap}/{ap_max}"
    if ap < MINE_AP_COST:
        line += f" — на следующий удар не хватит ({MINE_AP_COST} ОД)"
    else:
        line += " — можно копать ещё"
    return line


async def mine_menu_cb(callback: CallbackQuery):
    """Вход в Железную копи (location:enter:mine)."""
    await callback.answer()

    if await user_is_tourist(callback.from_user.id):
        await callback.message.answer(
            "⛔ В копи не пускают туристов — вход только с «Пилота 1 класса»."
        )
        return

    if await get_active_run(callback.from_user.id):
        await callback.message.answer(
            "⛔ Ты сейчас проходишь подземелье — в копи нельзя.\n"
            "Выйди из подземелья, а потом возвращайся."
        )
        return

    token = _new_token()
    MINE_TOKEN[callback.from_user.id] = token

    pickaxe = await _pickaxe_for(callback.from_user.id)
    if pickaxe:
        hint = f"⛏ У тебя есть кирка: {pickaxe['name']} — спускайся и бей породу."
    else:
        hint = ("⛏ Без кирки в штольню не сунешься: купи «Кирка» "
                "(магазин → Добыча ресурсов).")

    caption = (
        "⛏ ЖЕЛЕЗНАЯ КОПЬ\n\n"
        "Лампы у входа мерцают, из штольни тянет холодом и запахом руды. "
        "Ворота открыты — но где-то в глубине шелестит крыльями здешняя "
        "хозяйка.\n\n"
        f"{hint}\n\n"
        "Спустись на первый уровень шахт или вернись в город."
    )
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

    pickaxe = await _pickaxe_for(user_id)
    if pickaxe:
        rank = pickaxe['rarity'] or 1
        chance = mine_ore_chance(rank)
        pickaxe_line = f"⛏ Кирка: {pickaxe['name']} (ступень {rank}, шанс добычи {chance}%)"
        dig_line = "Бей породу — авось блеснёт руда. А может, что и пострашнее."
    else:
        pickaxe_line = "⛏ Кирка: нет — купи «Кирка» (магазин → Добыча ресурсов)"
        dig_line = "Без кирки в штольню не сунешься: сначала разживись киркой."

    caption = (
        "⛏ УРОВЕНЬ 1 ШАХТ\n\n"
        "Крепь из подгнивших балок уходит вглубь, под ногами хрустит щебень, "
        "фонарь выхватывает жилы руды в тёмной породе.\n\n"
        f"{pickaxe_line}\n"
        f"{dig_line}\n\n"
        f"Удар киркой стоит {MINE_AP_COST} ОД, результат через "
        f"{MINE_RESULT_DELAY[0]}–{MINE_RESULT_DELAY[1]} секунд.\n\n"
        f"{await _ap_line(user_id)}"
    )
    await _level_paint(callback, text=caption,
                       kb=_level_markup(MINE_TOKEN.get(user_id, "")))


@router.callback_query(F.data.regexp(r"^mine:deeper:\d+$"))
async def mine_deeper(callback: CallbackQuery):
    """Спуск на 2-й уровень шахт — пока не обустроен (заглушка)."""
    if not await _mine_ok(callback):
        return
    await callback.answer(
        "🪜 Спуск на второй уровень ещё не обустроен — работы идут.",
        show_alert=True,
    )


@router.callback_query(F.data.regexp(r"^mine:dig:\d+$"))
async def mine_dig(callback: CallbackQuery):
    if not await _mine_ok(callback):
        return
    user_id = callback.from_user.id

    if await user_is_tourist(user_id):
        await callback.answer("⛔ В копи не пускают туристов.", show_alert=True)
        return
    if user_id in MINE_CASTING:
        await callback.answer("Ты уже замахнулся киркой — дождись результата!", show_alert=True)
        return

    # Лок ставим сразу, до первого await: иначе двойной тап проходит дважды.
    MINE_CASTING.add(user_id)
    try:
        if await get_active_run(user_id):
            await callback.answer("⛔ Ты в подземелье — в копи нельзя!", show_alert=True)
            return

        user = await get_user(user_id)
        if not user:
            await callback.answer("Сначала нажми /start", show_alert=True)
            return

        pickaxe = await _pickaxe_for(user_id)
        if not pickaxe:
            await _level_paint(
                callback,
                text="❌ У тебя нет кирки. Купи «Кирка» в магазине (категория «Добыча ресурсов»).",
                kb=_level_markup(MINE_TOKEN.get(user_id, "")),
            )
            return

        if not await remove_ap(user_id, MINE_AP_COST, reason="добыча руды"):
            await _level_paint(
                callback,
                text=f"❌ Не хватает ОД: нужно {MINE_AP_COST}, доступно меньше. "
                     "Восстановление — в новые сутки.",
                kb=_level_markup(MINE_TOKEN.get(user_id, "")),
            )
            return

        delay = random.randint(*MINE_RESULT_DELAY)
        await _level_paint(
            callback,
            text=(f"⛏ Ты замахиваешься киркой и бьёшь по породе...\n"
                  f"Результат через {delay} секунд. Не шуми — прислушивайся!"),
            kb=None,
        )
        await log_activity(user_id, "mine", f"Добыча руды: удар киркой ({MINE_AP_COST} ОД)")
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
        chance = mine_ore_chance(rank)
        head = "⛏ ЖЕЛЕЗНАЯ КОПЬ"
        ap_block = f"\n\n{await _ap_line(user_id)}"
        result_kb = _result_markup(MINE_TOKEN.get(user_id, ""))
        if random.random() * 100 < chance:
            ore = await get_item_by_name(MINE_ORE_NAME)
            if ore:
                await add_inventory_item(user_id, ore['id'], 1)
                await log_activity(user_id, "mine", f"Добыл «{ore['name']}»")
                sell_line = ""
                if ore['sell_price'] > 0:
                    sell_line = (f"\nКазна выкупает руду по {ore['sell_price']} "
                                 f"{plural_nordmark(ore['sell_price'])} за кусок.")
                text = (
                    f"{head}\n\n"
                    "Кирка звонко высекает искру — из породы выкалывается кусок "
                    "руды!\n\n"
                    f"🎒 Добыча: «{ore['name']}» — в инвентарь.{sell_line}"
                ) + ap_block
            else:
                text = (f"{head}\n\n🔨 Что-то добыл, но предмет потерялся. "
                        "Сообщи хранителю.") + ap_block
        else:
            text = (
                f"{head}\n\n"
                "Удар за ударом — только каменная крошка да серый блеск.\n"
                "Порода сегодня пуста. Пробуй ещё!"
            ) + ap_block
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
    text = (
        f"{prefix}{emoji} {bat_name.upper()}\n\n"
        "Из темноты штольни с писком выныривает крылатая тень — Летучая мышь!\n\n"
        f"{emoji} Мышь   HP {_hp_bar(bat_hp, bat_hp_max)} {max(0, bat_hp)}/{bat_hp_max}\n"
        f"🧑 Ты     HP {_hp_bar(player_hp, battle['player_hp_max'])} "
        f"{max(0, player_hp)}/{battle['player_hp_max']}{effects_line}\n\n"
        f"Ход {battle['round']}. Бей — или уходи подобру-поздорову."
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
        await _level_paint(
            callback,
            text="⏳ Бой с мышью устарел.",
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
            text = (
                f"{emoji} БОЙ С МЫШЬЮ\n\n"
                f"{dot_note}"
                "В глазах темнеет, писк крыльев всё дальше...\n\n"
                f"Ты приходишь в себя на полу штольни. Мышь улетела — но добычу "
                f"придётся начать заново (−{removed} ОД)."
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
    if res['dodged']:
        hit_line = "Ты бьёшь — но мышь уходит в сторону с писком.\n\n"
    else:
        extra = ""
        if res['armor_blocked']:
            extra += f"🛡️ {res['armor_blocked']} урона поглотила шкура. "
        if res['crit']:
            extra += "💥 crit! "
        hit_line = f"Ты бьёшь наотмашь: −{player_hit} HP по мыши! {extra}\n\n"

    if battle['bat_hp'] <= 0:
        MINE_BATTLE.pop(user_id, None)
        onhit.unregister(user_id)
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
            result_line = f"Ты выхватил из-под писка мыши:\n{loot_list}\n\nПоложено в инвентарь."
        else:
            result_line = "Мышь повержена, но ничего ценного в ней не нашлось."
        text = (
            f"{emoji} БОЙ С МЫШЬЮ\n\n"
            f"{dot_note}{hit_line}"
            "Мышь с писком падает на каменный пол — в штольне снова тихо.\n\n"
            f"{result_line}"
        )
        await _enemy_paint(callback, text=text,
                           kb=_result_markup(MINE_TOKEN.get(user_id, "")),
                           image=bat_img)
        return

    # Ответный удар мыши.
    eres = roll_enemy_damage(stats, {
        'dmg_min': battle.get('dmg_min') or MINE_BAT_SEED['dmg_min'],
        'dmg_max': battle.get('dmg_max') or MINE_BAT_SEED['dmg_max'],
    })
    bat_hit = eres['damage']
    if eres['dodged']:
        counter_line = "💨 Ты уклоняешься от когтей! (−0 HP)\n\n"
    else:
        extra = ""
        if eres['armor_blocked']:
            extra += f"🛡️ Броня поглотила {eres['armor_blocked']}. "
        if eres['crit']:
            extra += "💥 crit! "
        counter_line = f"Мышь вцепляется и бьёт: −{bat_hit} HP. {extra}\n\n"
    battle['player_hp'] -= bat_hit
    if battle['player_hp'] <= 0:
        MINE_BATTLE.pop(user_id, None)
        onhit.unregister(user_id)
        removed = await remove_ap_or_floor(user_id, int(battle.get('loss_ap') or MINE_BAT_SEED['loss_ap']))
        await log_activity(user_id, "mine", f"Проиграл Летучей мыши (−{removed} ОД)")
        text = (
            f"{emoji} БОЙ С МЫШЬЮ\n\n"
            f"{dot_note}{hit_line}{counter_line}"
            "В глазах темнеет, писк крыльев всё дальше...\n\n"
            f"Ты приходишь в себя на полу штольни. Мышь улетела — но добычу "
            f"придётся начать заново (−{removed} ОД)."
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
    await _show_battle(callback, prefix=f"{dot_note}{hit_line}{counter_line}{proc_line}{round_note}")


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
    await _level_paint(
        callback,
        text=("🏃 Ты отступаешь к выходу из штольни, отмахиваясь от писка крыльев.\n\n"
              "Мышь не преследует — но и добычи не будет. Попробуй ещё раз!"),
        kb=_result_markup(MINE_TOKEN.get(user_id, "")),
    )
