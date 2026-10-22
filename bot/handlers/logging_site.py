"""Лесозаготовка: ресурсная локация в лесу (v0.37.0).

Пилот входит кнопкой «🪓 Лесозаготовка» с Лесной поляны (лес → опушка → поляна)
и рубит деревья («🪓 Рубить дерево»): 15 ОД за попытку, результат через 7–15
секунд. Без топора рубить нельзя. Шанс успеха — база 35% плюс надбавка за
ступень топора (базовый топор ранг 1 → +15%, итого 50%), не выше
LOGGING_CHANCE_CAP.

Врагов двое, как в лесу с двумя зверями: встреча бросается ПЕРЕД находкой
бревен и заменяет её. Сначала — Лесная змея (обычный враг: убиваема, может
отравить ядом), потом — Неясыть (реже и сильнее): убить её нельзя — при HP
не выше LOGGING_OWL_FLEE_HP она отлетает (победа = редкое Совиное перо), а
ударом может наложить «ослепление» (v0.38.0 — эффекты при ударе из
on_hit_effects врага, считаются в ходах боя). Поражение — минус loss_ap ОД.
"""

import asyncio
import os
import random

from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database.db import (
    get_user, remove_ap, get_active_run, add_inventory_item,
    get_item, get_item_by_name, get_inventory_item, remove_inventory_item,
    transfer_to_treasury,
    get_source_enemy_by_key, get_source_enemy_drops, roll_enemy_drops,
    enemy_encounter_hit,
    get_logging_snake_attempts, set_logging_snake_attempts, reset_logging_snake_counter,
    get_logging_owl_attempts, set_logging_owl_attempts, reset_logging_owl_counter,
    remove_ap_or_floor, user_is_tourist, log_activity,
    get_location_by_key, location_logging_photo,
)
from utils.helpers import (
    resolve_image_seasonal, resolve_image, item_local_photo,
    season_key, time_of_day_key, plural_nordmark,
)
from utils import onhit
from config import (
    LOGGING_AP_COST, LOGGING_BASE_CHANCE, LOGGING_AXE_BONUS_PER_RANK,
    LOGGING_CHANCE_CAP, LOGGING_RESULT_DELAY, LOGGING_AXE_NAME, LOGGING_WOOD_NAME,
    LOGGING_SNAKE_KEY, LOGGING_OWL_KEY, LOGGING_SPOT, LOGGING_SNAKE_SEED,
    LOGGING_OWL_SEED, LOGGING_OWL_FLEE_HP,
    LOGGING_PLANK_NAME, LOGGING_FIREWOOD_NAME, LOGGING_PLANK_YIELD,
    LOGGING_PLANK_FEE, LOGGING_FIREWOOD_YIELD, LOGGING_FIREWOOD_AP_COST,
    LOGGING_AXE_SLIP_CHANCE,
)

router = Router()

LOGGING_HOME_PHOTO = "city/logging"
SNAKE_EMOJI = "🐍"
OWL_EMOJI = "🦉"

# Пользователи, чья рубка ещё не завершена (защита от повторного клика).
LOGGING_CASTING = set()

# Отслеживаемое сообщение окна Лесозаготовки: user_id -> (chat_id, message_id).
LOGGING_MSG: dict = {}

# Токен текущего окна: уход в другое меню инвалидирует старые кнопки.
LOGGING_TOKEN: dict = {}

# Активные бои: user_id -> {token, player_hp, enemy_hp, round, kind, ...}.
LOGGING_BATTLE: dict = {}


def _new_token() -> str:
    return str(random.randint(100000, 999999))


async def deactivate_logging_site(user_id: int):
    """Инвалидация окна Лесозаготовки при уходе в другое меню."""
    LOGGING_TOKEN.pop(user_id, None)
    LOGGING_MSG.pop(user_id, None)
    LOGGING_CASTING.discard(user_id)
    LOGGING_BATTLE.pop(user_id, None)
    onhit.unregister(user_id)


def _callback_token(data: str) -> str:
    """Токен окна из callback_data (последний числовой сегмент)."""
    for part in reversed(data.split(":")[1:]):
        if part.isdigit():
            return part
    return ""


async def _logging_ok(callback) -> bool:
    """Step-guard: callback должен приходить из текущего окна Лесозаготовки."""
    token = _callback_token(callback.data)
    if LOGGING_TOKEN.get(callback.from_user.id) != token:
        try:
            await log_activity(callback.from_user.id, "stale_button",
                               "лесозаготовка: устаревшее окно")
        except Exception:
            pass
        await callback.answer(
            "⏳ Это окно устарело — открой Лесозаготовку заново "
            "(Лес → Поляна → 🪓 Лесозаготовка).",
            show_alert=True,
        )
        return False
    return True


def _logging_path() -> str:
    """Картинка Лесозаготовки: сезонный локальный файл с фолбэками на лес/парк."""
    path = resolve_image_seasonal(LOGGING_HOME_PHOTO)
    if not os.path.isfile(path):
        path = resolve_image_seasonal("city/forest")
    if not os.path.isfile(path):
        path = resolve_image_seasonal("city/park")
    return path


async def _logging_photo_id():
    """Своя картинка Лесозаготовки из админ-редактора (слот в картинках леса)."""
    try:
        loc = await get_location_by_key("forest")
        return location_logging_photo(loc)
    except Exception:
        return None


async def _paint(callback, *, text: str = None, media_path: str = None,
                 photo_id: str = None, kb=None):
    """Единая отрисовка окна в одном сообщении на игрока (как в копи)."""
    bot = callback.message.bot
    chat_id = callback.message.chat.id
    user_id = callback.from_user.id
    entry = LOGGING_MSG.get(user_id)
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
        sent = await bot.send_photo(chat_id, photo_id or FSInputFile(media_path),
                                    caption=text, reply_markup=kb)
    else:
        sent = await bot.send_message(chat_id, text, reply_markup=kb)
    LOGGING_MSG[user_id] = (chat_id, sent.message_id)


async def _logging_paint(callback, *, text: str, kb=None,
                         photo_id=None, media_path=None):
    """Отрисовка окна: своя картинка из админ-редактора, иначе локальный фон.

    photo_id/media_path — явный override (фото врага или находки); если заданы,
    используются вместо фона локации.
    """
    if photo_id or media_path:
        await _paint(callback, text=text, photo_id=photo_id,
                     media_path=media_path, kb=kb)
        return
    loc_photo = await _logging_photo_id()
    if loc_photo:
        await _paint(callback, text=text, photo_id=loc_photo, kb=kb)
    else:
        await _paint(callback, text=text, media_path=_logging_path(), kb=kb)


async def _enemy_paint(callback, battle: dict, *, text: str, kb=None):
    """Отрисовка боя: фото врага из БД (image), иначе локальный ключ, иначе фон."""
    enemy = battle.get('enemy') or {}
    image = enemy.get('image')
    if image:
        await _logging_paint(callback, text=text, kb=kb, photo_id=image)
        return
    path = resolve_image(enemy.get('photo_key') or "")
    if path and os.path.isfile(path):
        await _logging_paint(callback, text=text, kb=kb, media_path=path)
        return
    await _logging_paint(callback, text=text, kb=kb)


async def _item_paint(callback, item, *, text: str, kb=None):
    """Отрисовка находки: фото предмета (items.photo_file_id), иначе локальный файл."""
    if item:
        photo_id = item.get('photo_file_id') if item.keys() is not None and 'photo_file_id' in item.keys() else None
        if photo_id:
            await _logging_paint(callback, text=text, kb=kb, photo_id=photo_id)
            return
        local_photo = item_local_photo(item.get('name') or "")
        if local_photo:
            await _logging_paint(callback, text=text, kb=kb, media_path=local_photo)
            return
    await _logging_paint(callback, text=text, kb=kb)


# ───────── чистые функции (тестируются в smoke) ─────────

def logging_wood_chance(axe_rank: int, logging_bonus: int = 0) -> int:
    """Шанс успешной рубки дерева, % : база + надбавка топора + бонус наград.

    axe_rank — ступень топора (ранг = редкость предмета); линейно повышает
    шанс на LOGGING_AXE_BONUS_PER_RANK за ступень. Итог не выше LOGGING_CHANCE_CAP.
    """
    rank = max(1, int(axe_rank or 1))
    chance = LOGGING_BASE_CHANCE + LOGGING_AXE_BONUS_PER_RANK * rank + int(logging_bonus or 0)
    return min(LOGGING_CHANCE_CAP, max(0, chance))


def owl_after_hit(hp: int, damage: int, flee_hp: int) -> tuple:
    """HP Неясыти после удара пилота и флаг «отлетела».

    Неясыть нельзя убить: при HP <= flee_hp она бросает бой и улетает
    (второй элемент кортежа True — это победа пилота).
    """
    hp = int(hp) - max(0, int(damage))
    return hp, hp <= int(flee_hp)


async def _axe_for(user_id: int):
    """Топор игрока (предмет + наличие в инвентаре) или None."""
    item = await get_item_by_name(LOGGING_AXE_NAME)
    if not item:
        return None
    inv = await get_inventory_item(user_id, item['id'])
    if not inv or inv['quantity'] < 1:
        return None
    return item


async def _wood_count(user_id: int) -> int:
    """Сколько брёвен (LOGGING_WOOD_NAME) у игрока в инвентаре."""
    item = await get_item_by_name(LOGGING_WOOD_NAME)
    if not item:
        return 0
    inv = await get_inventory_item(user_id, item['id'])
    return int(inv['quantity']) if inv else 0


async def _snake():
    """Строка Лесной змеи из БД (или None)."""
    return await get_source_enemy_by_key("logging", LOGGING_SNAKE_KEY, spot=LOGGING_SPOT)


async def _owl():
    """Строка Неясыти из БД (или None)."""
    return await get_source_enemy_by_key("logging", LOGGING_OWL_KEY, spot=LOGGING_SPOT)


def _snake_fallback() -> dict:
    """Параметры змеи из конфига — если строки в БД ещё нет (до сида)."""
    return dict(LOGGING_SNAKE_SEED)


def _owl_fallback() -> dict:
    """Параметры неясыти из конфига — если строки в БД ещё нет (до сида)."""
    return dict(LOGGING_OWL_SEED)


def _enemy_emoji(kind: str) -> str:
    return OWL_EMOJI if kind == "owl" else SNAKE_EMOJI


def _hp_bar(hp: int, hp_max: int) -> str:
    hp = max(0, int(hp))
    hp_max = max(1, int(hp_max))
    filled = round(10 * hp / hp_max)
    return "█" * filled + "░" * (10 - filled)


def _enter_markup(token: str):
    """Меню входа: рубка деревьев и возврат в лес."""
    rows = [
        [InlineKeyboardButton(text="🪓 Рубить дерево", callback_data=f"logsite:chop:{token}")],
        [InlineKeyboardButton(text="🔙 К лесу", callback_data="logsite:back")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _result_markup(token: str, has_wood: bool = False):
    rows = [
        [InlineKeyboardButton(text="🪓 Рубить ещё", callback_data=f"logsite:chop:{token}")],
    ]
    if has_wood:
        rows.append([InlineKeyboardButton(text="🪚 Переработка брёвен",
                                          callback_data=f"logsite:mill:{token}")])
    rows.append([InlineKeyboardButton(text="🔙 К лесу", callback_data="logsite:back")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _enter_markup_extra(token: str, has_wood: bool):
    """Меню входа: рубка деревьев, переработка (если есть брёвна) и возврат."""
    rows = [
        [InlineKeyboardButton(text="🪓 Рубить дерево", callback_data=f"logsite:chop:{token}")],
    ]
    if has_wood:
        rows.append([InlineKeyboardButton(text="🪚 Переработка брёвен",
                                          callback_data=f"logsite:mill:{token}")])
    rows.append([InlineKeyboardButton(text="🔙 К лесу", callback_data="logsite:back")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def max_planks(wood_qty: int, nordmarks: int, fee: int, yield_per: int) -> int:
    """Сколько досок выйдет при распиле wood_qty брёвен с учетом денег.

    Ограничено наличием брёвен и кошельком: каждое бревно стоит fee НМ.
    Возвращает количество досок (yield_per за каждое оплаченное бревно).
    """
    wood_qty = max(0, int(wood_qty or 0))
    nordmarks = max(0, int(nordmarks or 0))
    fee = max(1, int(fee or 1))
    yield_per = max(1, int(yield_per or 1))
    affordable = nordmarks // fee
    return min(wood_qty, affordable) * yield_per


def max_firewood(wood_qty: int, ap: int, ap_cost: int, yield_per: int) -> int:
    """Сколько паков дров выйдет при рубке wood_qty брёвен с учетом ОД."""
    wood_qty = max(0, int(wood_qty or 0))
    ap = max(0, int(ap or 0))
    ap_cost = max(1, int(ap_cost or 1))
    yield_per = max(1, int(yield_per or 1))
    affordable = ap // ap_cost
    return min(wood_qty, affordable) * yield_per


def _mill_markup(token: str, planks: int, firewood: int, planks_one: int,
                 firewood_one: int):
    """Окно переработки: распил на доски и рубка дров, по 1 или всё доступное."""
    rows = []
    if planks > 0:
        row = []
        if planks_one > 0:
            row.append(InlineKeyboardButton(
                text=f"🪚 1 бревно ({planks_one} дос.)",
                callback_data=f"logsite:plank:1:{token}"))
        row.append(InlineKeyboardButton(
            text=f"🪚 Всё ({planks} досок)",
            callback_data=f"logsite:plank:all:{token}"))
        rows.append(row)
    if firewood > 0:
        row = []
        if firewood_one > 0:
            row.append(InlineKeyboardButton(
                text=f"🪓 1 бревно ({firewood_one} пак.)",
                callback_data=f"logsite:fire:1:{token}"))
        row.append(InlineKeyboardButton(
            text=f"🪓 Всё ({firewood} паков)",
            callback_data=f"logsite:fire:all:{token}"))
        rows.append(row)
    rows.append([InlineKeyboardButton(text="🔙 Назад",
                                      callback_data=f"logsite:menu:{token}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)



def _battle_markup(token: str):
    rows = [
        [InlineKeyboardButton(text="⚔️ Ударить", callback_data=f"logsite:battle:hit:{token}")],
        [InlineKeyboardButton(text="🏃 Сбежать", callback_data=f"logsite:battle:flee:{token}")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def _ap_line(user_id: int) -> str:
    """Строка остатка ОД для окна Лесозаготовки."""
    fresh = await get_user(user_id) or {}
    ap = fresh.get('ap', 0) or 0
    ap_max = fresh.get('ap_max', ap) or ap
    line = f"⚡ ОД: {ap}/{ap_max}"
    if ap < LOGGING_AP_COST:
        line += f" — на следующий удар топора не хватит ({LOGGING_AP_COST} ОД)"
    else:
        line += " — можно рубить ещё"
    return line


@router.callback_query(F.data == "logsite:enter")
async def logging_menu_cb(callback: CallbackQuery):
    """Вход в Лесозаготовку (кнопка с Лесной поляны)."""
    await callback.answer()

    if await user_is_tourist(callback.from_user.id):
        await callback.message.answer(
            "⛔ На лесозаготовку не пускают туристов — это работа настоящих пилотов."
        )
        return

    if await get_active_run(callback.from_user.id):
        await callback.message.answer(
            "⛔ Ты сейчас проходишь подземелье — рубить деревья нельзя.\n"
            "Выйди из подземелья, а потом возвращайся."
        )
        return

    token = _new_token()
    LOGGING_TOKEN[callback.from_user.id] = token

    axe = await _axe_for(callback.from_user.id)
    if axe:
        rank = axe['rarity'] or 1
        chance = logging_wood_chance(rank)
        hint = (f"🪓 Топор: {axe['name']} (ступень {rank}, шанс рубки {chance}%) — "
                "за работу!")
    else:
        hint = ("🪓 Без топора сюда не пускают: купи «Топор» "
                "(магазин → Добыча ресурсов).")

    wood_qty = await _wood_count(callback.from_user.id)
    mill_hint = ""
    if wood_qty > 0:
        mill_hint = (f"\n\n🪚 В сарае {wood_qty} брёвен — их можно распилить "
                     "на доски в артели или наколоть дров.")

    caption = (
        "🪓 ЛЕСОЗАГОТОВКА\n\n"
        "За дальнейшей опушкой, там, где тропа уходит в самый глухой подлесок, "
        "стоит сторожка лесорубов. Здесь пахнет свежими стружками и хвоей — "
        "и отсюда редко кто возвращается с пустыми руками. Или вообще "
        "не возвращается.\n\n"
        f"{hint}\n\n"
        f"Рубка дерева стоит {LOGGING_AP_COST} ОД, результат через "
        f"{LOGGING_RESULT_DELAY[0]}–{LOGGING_RESULT_DELAY[1]} секунд."
        f"{mill_hint}\n\n"
        f"{await _ap_line(callback.from_user.id)}"
    )
    await _logging_paint(callback, text=caption,
                         kb=_enter_markup_extra(token, wood_qty > 0))


@router.callback_query(F.data.regexp(r"^logsite:menu:\d+$"))
async def logging_menu_again(callback: CallbackQuery):
    if not await _logging_ok(callback):
        return
    await logging_menu_cb(callback)


@router.callback_query(F.data == "logsite:back")
async def logging_back(callback: CallbackQuery):
    """Возврат из Лесозаготовки в лес (открываем опушку)."""
    from bot.handlers.forest import forest_menu_cb
    await deactivate_logging_site(callback.from_user.id)
    await forest_menu_cb(callback)


@router.callback_query(F.data.regexp(r"^logsite:chop:\d+$"))
async def logging_chop(callback: CallbackQuery):
    if not await _logging_ok(callback):
        return
    user_id = callback.from_user.id

    if await user_is_tourist(user_id):
        await callback.answer("⛔ На лесозаготовку туристов не пускают.", show_alert=True)
        return
    if user_id in LOGGING_CASTING:
        await callback.answer("Ты уже замахнулся топором — дождись результата!",
                              show_alert=True)
        return

    # Лок ставим сразу, до первого await: иначе двойной тап проходит дважды.
    LOGGING_CASTING.add(user_id)
    try:
        if await get_active_run(user_id):
            await callback.answer("⛔ Ты в подземелье — рубить деревья нельзя!",
                                  show_alert=True)
            return

        user = await get_user(user_id)
        if not user:
            await callback.answer("Сначала нажми /start", show_alert=True)
            return

        axe = await _axe_for(user_id)
        if not axe:
            await _logging_paint(
                callback,
                text="❌ У тебя нет топора. Купи «Топор» в магазине "
                     "(категория «Добыча ресурсов»).",
                kb=_enter_markup(LOGGING_TOKEN.get(user_id, "")),
            )
            return

        if not await remove_ap(user_id, LOGGING_AP_COST, reason="рубка деревьев"):
            await _logging_paint(
                callback,
                text=f"❌ Не хватает ОД: нужно {LOGGING_AP_COST}, доступно меньше. "
                     "Восстановление — в новые сутки.",
                kb=_enter_markup(LOGGING_TOKEN.get(user_id, "")),
            )
            return

        delay = random.randint(*LOGGING_RESULT_DELAY)
        await _logging_paint(
            callback,
            text=(f"🪓 Ты размахиваешься топором и рубишь дерево...\n"
                  f"Результат через {delay} секунд. Не поранься — и не дремли: "
                  "в подлеске что-то шевелится!"),
            kb=None,
        )
        await log_activity(user_id, "logging", f"Рубка деревьев ({LOGGING_AP_COST} ОД)")
        await asyncio.sleep(delay)

        # ── встреча со Змеёй: бросок ПЕРЕД находкой бревен ──
        snake = await _snake()
        if snake and snake.get('enabled', 1):
            attempts = await get_logging_snake_attempts(user_id)
            chance = float(snake.get('chance') or 0)
            pity = int(snake.get('pity_target') or 0)
            if enemy_encounter_hit(chance, random.random() * 100, attempts, pity):
                await reset_logging_snake_counter(user_id)
                await _start_battle(callback, user_id, snake, "snake")
                return
            await set_logging_snake_attempts(user_id, attempts + 1)

        # ── встреча с Неясытью: реже, но опаснее ──
        owl = await _owl()
        if owl and owl.get('enabled', 1):
            attempts = await get_logging_owl_attempts(user_id)
            chance = float(owl.get('chance') or 0)
            pity = int(owl.get('pity_target') or 0)
            if enemy_encounter_hit(chance, random.random() * 100, attempts, pity):
                await reset_logging_owl_counter(user_id)
                await _start_battle(callback, user_id, owl, "owl")
                return
            await set_logging_owl_attempts(user_id, attempts + 1)

        # Малый шанс: топор отскакивает и бьёт пилота в плечо
        rank = axe['rarity'] or 1
        chance = logging_wood_chance(rank)
        head = "🪓 ЛЕСОЗАГОТОВКА"
        ap_block = f"\n\n{await _ap_line(user_id)}"
        # Малый шанс: топор от усталости/невнимательности отскакивает от
        # мощного ствола и бьёт пилота в плечо. Ресурса нет, попытка (ОД) уже
        # потрачена — вторая неудача того же вида, что и «сучковатое дерево».
        if random.random() * 100 < LOGGING_AXE_SLIP_CHANCE:
            text = (
                f"{head}\n\n"
                "Топор от усталости неудачно отскакивает от мощного ствола "
                "и отлетает пилоту в плечо.\n\n"
                "Ресурса не получено, попытка потрачена."
            ) + ap_block
            left_wood = await _wood_count(user_id)
            result_kb = _result_markup(LOGGING_TOKEN.get(user_id, ""), left_wood > 0)
            await _logging_paint(callback, text=text, kb=result_kb)
            return

        # ── находка бревен ──
        found_wood = False
        item_meta = None
        if random.random() * 100 < chance:
            wood = await get_item_by_name(LOGGING_WOOD_NAME)
            if wood:
                await add_inventory_item(user_id, wood['id'], 1)
                await log_activity(user_id, "logging", f"Срубил «{wood['name']}»")
                found_wood = True
                item_meta = wood
                sell_line = ""
                if wood['sell_price'] > 0:
                    sell_line = (f"\nКазна выкупает бревна по {wood['sell_price']} "
                                 f"{plural_nordmark(wood['sell_price'])} за штуку.")
                text = (
                    f"{head}\n\n"
                    "Топор звонко вгрызается в древесину — с ровным треском "
                    "падает свежесрубленное бревно!\n\n"
                    f"🎒 Добыча: «{wood['name']}» — в инвентарь.{sell_line}"
                ) + ap_block
            else:
                text = (f"{head}\n\n🌲 Срубил что-то, но предмет потерялся. "
                        "Сообщи хранителю.") + ap_block
        else:
            firewood = await get_item_by_name(LOGGING_FIREWOOD_NAME)
            loot_line = ""
            if firewood:
                await add_inventory_item(user_id, firewood['id'], 1)
                await log_activity(user_id, "logging", f"Срубил «{firewood['name']}» (суковатое дерево)")
                item_meta = firewood
                loot_line = f"\n\n🎒 Добыча: «{firewood['name']}» — в инвентарь."
            text = (
                f"{head}\n\n"
                "Удар за ударом — стружка летит, но сук топор не берёт: сучковатое "
                "дерево уходит на дрова.\n"
                "Пробуй ещё!"
            ) + loot_line + ap_block
        left_wood = await _wood_count(user_id)
        result_kb = _result_markup(LOGGING_TOKEN.get(user_id, ""), left_wood > 0)
        await _item_paint(callback, item_meta, text=text, kb=result_kb)
    finally:
        LOGGING_CASTING.discard(user_id)


@router.callback_query(F.data.regexp(r"^logsite:mill:\d+$"))
async def logging_mill(callback: CallbackQuery):
    """Окно переработки брёвен: распил на доски и рубка дров."""
    if not await _logging_ok(callback):
        return
    user_id = callback.from_user.id
    await callback.answer()
    token = LOGGING_TOKEN.get(user_id, "")

    wood_qty = await _wood_count(user_id)
    if wood_qty <= 0:
        await _logging_paint(
            callback,
            text="🪚 Переработка\n\nУ тебя нет брёвен — сначала наруби деревьев.",
            kb=_enter_markup_extra(token, False),
        )
        return

    user = await get_user(user_id) or {}
    nordmarks = int(user.get('nordmarks', 0) or 0)
    ap = int(user.get('ap', 0) or 0)

    planks = max_planks(wood_qty, nordmarks, LOGGING_PLANK_FEE, LOGGING_PLANK_YIELD)
    firewood = max_firewood(wood_qty, ap, LOGGING_FIREWOOD_AP_COST,
                            LOGGING_FIREWOOD_YIELD)
    planks_one = max_planks(1, nordmarks, LOGGING_PLANK_FEE, LOGGING_PLANK_YIELD)
    firewood_one = max_firewood(1, ap, LOGGING_FIREWOOD_AP_COST,
                                LOGGING_FIREWOOD_YIELD)
    paid_wood = min(wood_qty, nordmarks // max(1, LOGGING_PLANK_FEE))
    fw_wood = min(wood_qty, ap // max(1, LOGGING_FIREWOOD_AP_COST))

    lines = [f"🪚 ПЕРЕРАБОТКА БРЁВЕН", ""]
    lines.append(f"🎒 Брёвен в инвентаре: {wood_qty} шт.")
    lines.append(f"💰 Кошелёк: {nordmarks} {plural_nordmark(nordmarks)} НМ")
    lines.append(f"⚡ ОД: {ap}")
    lines.append("")
    lines.append(
        f"🪚 Распил на доски (артель)\n"
        f"   1 бревно → {LOGGING_PLANK_YIELD} «{LOGGING_PLANK_NAME}», "
        f"плата {LOGGING_PLANK_FEE} НМ за бревно (в казну), топор не нужен.\n"
        f"   Доступно: {paid_wood} бревён → {planks} досок."
    )
    lines.append("")
    lines.append(
        f"🪓 Рубка дров (самостоятельно)\n"
        f"   1 бревно → {LOGGING_FIREWOOD_YIELD} «{LOGGING_FIREWOOD_NAME}», "
        f"тратит {LOGGING_FIREWOOD_AP_COST} ОД за бревно, нужен топор.\n"
        f"   Доступно: {fw_wood} бревён → {firewood} паков дров."
    )
    await _logging_paint(callback, text="\n".join(lines),
                         kb=_mill_markup(token, planks, firewood,
                                         planks_one, firewood_one))


@router.callback_query(F.data.regexp(r"^logsite:plank:(1|all):\d+$"))
async def logging_plank(callback: CallbackQuery):
    """Распил брёвен на доски (1 или всё доступное): плата в казну, топор не нужен."""
    if not await _logging_ok(callback):
        return
    user_id = callback.from_user.id
    token = LOGGING_TOKEN.get(user_id, "")
    mode = callback.data.split(":")[2]

    if await get_active_run(user_id):
        await callback.answer("⛔ Ты в подземелье — тут не до распила.", show_alert=True)
        return

    wood_item = await get_item_by_name(LOGGING_WOOD_NAME)
    plank_item = await get_item_by_name(LOGGING_PLANK_NAME)
    wood_qty = await _wood_count(user_id)
    if not wood_item or not plank_item or wood_qty <= 0:
        await callback.answer("❌ Нет брёвен для распила.", show_alert=True)
        await logging_mill(callback)
        return

    user = await get_user(user_id) or {}
    nordmarks = int(user.get('nordmarks', 0) or 0)
    afford = nordmarks // max(1, LOGGING_PLANK_FEE)
    want = 1 if mode == "1" else wood_qty
    n = min(wood_qty, afford, want)
    if n <= 0:
        await callback.answer(
            f"❌ Не хватает денег: распил одного бревна стоит "
            f"{LOGGING_PLANK_FEE} НМ, а у тебя {nordmarks}.",
            show_alert=True)
        return

    total_fee = n * LOGGING_PLANK_FEE
    planks = n * LOGGING_PLANK_YIELD
    if not await remove_inventory_item(user_id, wood_item['id'], n):
        await callback.answer("❌ Брёвен уже не хватает.", show_alert=True)
        return
    await transfer_to_treasury(user_id, total_fee, "Распил брёвен на доски")
    await add_inventory_item(user_id, plank_item['id'], planks)
    await log_activity(user_id, "logging",
                       f"Распилил {n} брёвен → {planks} «{plank_item['name']}» "
                       f"(−{total_fee} НМ в казну)")
    await callback.answer()

    left_wood = await _wood_count(user_id)
    text = (
        "🪚 РАСПИЛ БРЁВЕН\n\n"
        f"Артельные пилы визжат, опилки летят в лицо: {n} брёвен "
        f"превращаются в {planks} {plural_nordmark(planks)} "
        f"«{plank_item['name']}».\n\n"
        f"💰 Заплачено артели: {total_fee} НМ (ушло в казну).\n"
        f"🎒 Получено: «{plank_item['name']}» x{planks}.\n"
        f"📦 Брёвен осталось: {left_wood} шт."
    )
    await _item_paint(callback, plank_item, text=text,
                      kb=_enter_markup_extra(token, left_wood > 0))


@router.callback_query(F.data.regexp(r"^logsite:fire:(1|all):\d+$"))
async def logging_firewood(callback: CallbackQuery):
    """Рубка дров из брёвен (1 или всё доступное): тратит ОД, требует топор."""
    if not await _logging_ok(callback):
        return
    user_id = callback.from_user.id
    token = LOGGING_TOKEN.get(user_id, "")
    mode = callback.data.split(":")[2]
    await callback.answer()

    if await get_active_run(user_id):
        await callback.answer("⛔ Ты в подземелье — тут не до дров.", show_alert=True)
        return

    if not await _axe_for(user_id):
        await _logging_paint(
            callback,
            text="❌ Чтобы наколоть дров, нужен топор. Купи «Топор» в магазине "
                 "(категория «Добыча ресурсов»).",
            kb=_enter_markup_extra(token, True),
        )
        return

    wood_item = await get_item_by_name(LOGGING_WOOD_NAME)
    fw_item = await get_item_by_name(LOGGING_FIREWOOD_NAME)
    wood_qty = await _wood_count(user_id)
    if not wood_item or not fw_item or wood_qty <= 0:
        await callback.answer("❌ Нет брёвен для рубки на дрова.", show_alert=True)
        await logging_mill(callback)
        return

    user = await get_user(user_id) or {}
    ap = int(user.get('ap', 0) or 0)
    afford = ap // max(1, LOGGING_FIREWOOD_AP_COST)
    want = 1 if mode == "1" else wood_qty
    n = min(wood_qty, afford, want)
    if n <= 0:
        await callback.answer(
            f"❌ Не хватает ОД: на одно бревно нужно "
            f"{LOGGING_FIREWOOD_AP_COST} ОД, а у тебя {ap}.",
            show_alert=True)
        return

    if not await remove_ap(user_id, n * LOGGING_FIREWOOD_AP_COST,
                           reason="рубка дров"):
        await callback.answer("❌ Не хватает ОД.", show_alert=True)
        return
    if not await remove_inventory_item(user_id, wood_item['id'], n):
        await callback.answer("❌ Брёвен уже не хватает.", show_alert=True)
        return
    firewood = n * LOGGING_FIREWOOD_YIELD
    await add_inventory_item(user_id, fw_item['id'], firewood)
    await log_activity(user_id, "logging",
                       f"Нарубил дров: {n} брёвен → {firewood} «{fw_item['name']}» "
                       f"(−{n * LOGGING_FIREWOOD_AP_COST} ОД)")

    left_wood = await _wood_count(user_id)
    text = (
        "🪓 РУБКА ДРОВ\n\n"
        f"Ты ставишь бревно на плаху и работаешь топором: щепки веером, "
        f"{firewood} {plural_nordmark(firewood)} "
        f"«{fw_item['name']}» сложены у сторожки.\n\n"
        f"⚡ Потрачено ОД: {n * LOGGING_FIREWOOD_AP_COST}.\n"
        f"🎒 Получено: «{fw_item['name']}» x{firewood}.\n"
        f"📦 Брёвен осталось: {left_wood} шт.\n\n"
        f"{await _ap_line(user_id)}"
    )
    await _item_paint(callback, fw_item, text=text,
                      kb=_enter_markup_extra(token, left_wood > 0))


async def _start_battle(callback: CallbackQuery, user_id: int, enemy: dict, kind: str):
    """Начало мини-боя со Змеёй или Неясытью."""
    from utils.combat_model import pilot_combat_stats
    if not enemy:
        enemy = _owl_fallback() if kind == "owl" else _snake_fallback()
    stats = await pilot_combat_stats(user_id)
    player_hp = stats['hp_max']
    token = LOGGING_TOKEN.get(user_id, "")
    enemy_hp = int(enemy.get('hp') or (LOGGING_OWL_SEED if kind == "owl" else LOGGING_SNAKE_SEED)['hp'])
    LOGGING_BATTLE[user_id] = {
        "token": token,
        "kind": kind,
        "player_hp": player_hp,
        "player_hp_max": player_hp,
        "enemy_hp": enemy_hp,
        "enemy_hp_max": enemy_hp,
        "enemy_name": enemy.get('name') or ("Неясыть" if kind == "owl" else "Лесная змея"),
        "emoji": _enemy_emoji(kind),
        "dodge": float(enemy.get('dodge') or 0),
        "armor": int(enemy.get('armor') or 0),
        "dmg_min": int(enemy.get('dmg_min') or (LOGGING_OWL_SEED if kind == "owl" else LOGGING_SNAKE_SEED)['dmg_min']),
        "dmg_max": int(enemy.get('dmg_max') or (LOGGING_OWL_SEED if kind == "owl" else LOGGING_SNAKE_SEED)['dmg_max']),
        "loss_ap": int(enemy.get('loss_ap') or (LOGGING_OWL_SEED if kind == "owl" else LOGGING_SNAKE_SEED)['loss_ap']),
        # v0.38.0: эффекты при ударе (яд змеи, ослепление неясыти) — единая
        # система: JSON со строки врага, активные пишутся в on_hit.
        "on_hit_effects": onhit.parse_on_hit_effects(enemy.get('on_hit_effects')),
        "enemy": enemy,
        "round": 1,
    }
    onhit.register(user_id, LOGGING_BATTLE[user_id])
    await _show_battle(callback)


async def _show_battle(callback: CallbackQuery, prefix: str = ""):
    battle = LOGGING_BATTLE.get(callback.from_user.id)
    if not battle:
        await logging_menu_cb(callback)
        return
    player_hp = battle['player_hp']
    enemy_hp = battle['enemy_hp']
    enemy_hp_max = battle.get('enemy_hp_max') or battle['enemy_hp']
    enemy_name = battle.get('enemy_name') or "Враг"
    emoji = battle.get('emoji') or SNAKE_EMOJI
    effects_line = onhit.active_line(battle)
    effects_line = f"\n{effects_line}" if effects_line else ""
    if battle.get('kind') == "owl":
        flavor = ("Из чащи вылетает тяжёлый силуэт — Неясыть! Совиный глаз "
                  "прикован к тебе.\n\n")
        tail = "Сову нельзя убить — она сама решит, когда отступить."
    else:
        flavor = ("Из-под валуна с шипением выползает длинная тень — Лесная "
                  "змея!\n\n")
        tail = "Ударь змею — или уноси ноги."
    text = (
        f"{prefix}{emoji} {enemy_name.upper()}\n\n"
        f"{flavor}"
        f"{emoji} Враг   HP {_hp_bar(enemy_hp, enemy_hp_max)} {max(0, enemy_hp)}/{enemy_hp_max}\n"
        f"🧑 Ты     HP {_hp_bar(player_hp, battle['player_hp_max'])} "
        f"{max(0, player_hp)}/{battle['player_hp_max']}{effects_line}\n\n"
        f"Ход {battle['round']}. {tail}"
    )
    await _enemy_paint(callback, battle, text=text,
                       kb=_battle_markup(battle['token']))


async def _battle_loot(user_id: int, battle: dict) -> list:
    """Лут за победу: дропы врага из БД (для змеи — с кэпом один предмет)."""
    drops = await get_source_enemy_drops("logging", (battle.get('enemy') or {}).get('id'))
    if not drops:
        return []
    picked = roll_enemy_drops(drops)
    # Кэп один предмет за бой (как за самоцветами мыши): яд/перо/кожа редкие,
    # множить их случайными проходами не нужно.
    return picked[:1]


@router.callback_query(F.data.regexp(r"^logsite:battle:hit:\d+$"))
async def logging_battle_hit(callback: CallbackQuery):
    if not await _logging_ok(callback):
        return
    user_id = callback.from_user.id
    battle = LOGGING_BATTLE.get(user_id)
    if not battle:
        await _logging_paint(
            callback,
            text="⏳ Бой устарел.",
            kb=_enter_markup(LOGGING_TOKEN.get(user_id, "")),
        )
        return
    await callback.answer()
    emoji = battle.get('emoji') or SNAKE_EMOJI
    kind = battle.get('kind') or "snake"

    # DoT (яд/кровотечение): тикает в начале хода игрока (наложен змеёй
    # на прошлом ходу; живёт до конца боя).
    dot_dmg, dot_lines = onhit.tick_dots(battle)
    dot_note = "".join(f"{line}\n\n" for line in dot_lines)
    if dot_dmg:
        battle['player_hp'] = max(0, battle['player_hp'] - dot_dmg)
        if battle['player_hp'] <= 0:
            await _battle_defeat(callback, user_id, battle, prefix=dot_note)
            return

    # Твой удар: свой урон/крит, враг может увернуться, броня поглощает часть.
    from utils.combat_model import pilot_combat_stats, roll_pilot_damage, roll_enemy_damage
    stats = await pilot_combat_stats(user_id, onhit.battle_state_keys(battle))
    res = roll_pilot_damage(stats, {
        'dodge': battle.get('dodge') or 0,
        'armor': battle.get('armor') or 0,
    })
    player_hit = res['damage']
    prev_hp = battle['enemy_hp']
    enemy_fled = False
    if kind == "owl":
        # Неясыть нельзя убить: при низком HP отлетает — это победа.
        battle['enemy_hp'], enemy_fled = owl_after_hit(
            prev_hp, player_hit, LOGGING_OWL_FLEE_HP)
    else:
        battle['enemy_hp'] = prev_hp - player_hit
    if res['dodged']:
        hit_line = "Ты бьёшь — но змея уходит в сторону, словно сквозь тень.\n\n" \
            if kind == "snake" else \
            "Ты бьёшь — но неясыть отклоняется в воздухе, хлопая крылом.\n\n"
    else:
        extra = ""
        if res['armor_blocked']:
            extra += f"🛡️ {res['armor_blocked']} урона поглотила чешуя. " if kind == "snake" \
                else f"🛡️ {res['armor_blocked']} урона поглотило оперение. "
        if res['crit']:
            extra += "💥 crit! "
        hit_line = f"Ты бьёшь наотмашь: −{player_hit} HP по врагу! {extra}\n\n"

    # ── Неясыть отлетает (победа) ──
    if kind == "owl" and enemy_fled:
        LOGGING_BATTLE.pop(user_id, None)
        onhit.unregister(user_id)
        await log_activity(user_id, "logging", "Неясыть отлетела (победа над неясытью)")
        loot = await _battle_loot(user_id, battle)
        got = []
        for entry in loot:
            item = await get_item(int(entry.get('item_id'))) if entry.get('item_id') else None
            if not item:
                continue
            await add_inventory_item(user_id, item['id'], int(entry.get('qty') or 1))
            await log_activity(user_id, "logging", f"Добыча: {item['name']}")
            got.append(item['name'])
        if got:
            loot_list = "\n".join(f"• «{name}»" for name in got)
            result_line = (f"Из-под крыла, которым неясыть прикрывала гнездо, "
                           f"падает:\n{loot_list}\n\nПоложено в инвентарь.")
        else:
            result_line = ("Сова улетела, не роняя ничего — на этот раз обошлось "
                           "без трофеев.")
        text = (
            f"{emoji} НЕЯСЫТЬ\n\n"
            f"{dot_note}{hit_line}"
            "Раненая неясыть бросает бой: тяжёлый силуэт вздымается над кронами "
            "и растворяется в сумерках. Ты победил!\n\n"
            f"{result_line}"
        )
        await _logging_paint(callback, text=text,
                             kb=_result_markup(LOGGING_TOKEN.get(user_id, "")))
        return

    # ── Змея повержена (обычный враг, убиваема) ──
    if kind == "snake" and battle['enemy_hp'] <= 0:
        LOGGING_BATTLE.pop(user_id, None)
        onhit.unregister(user_id)
        await log_activity(user_id, "logging", "Победил Лесную змею")
        loot = await _battle_loot(user_id, battle)
        got = []
        for entry in loot:
            item = await get_item(int(entry.get('item_id'))) if entry.get('item_id') else None
            if not item:
                continue
            await add_inventory_item(user_id, item['id'], int(entry.get('qty') or 1))
            await log_activity(user_id, "logging", f"Добыча: {item['name']}")
            got.append(item['name'])
        if got:
            loot_list = "\n".join(f"• «{name}»" for name in got)
            result_line = f"Из-под поверженной змеи ты забираешь:\n{loot_list}\n\nПоложено в инвентарь."
        else:
            result_line = "Змея повержена, но ничего ценного на этот раз не нашлось."
        text = (
            f"{emoji} БОЙ СО ЗМЕЁЙ\n\n"
            f"{dot_note}{hit_line}"
            "Змея дёргается и замирает — подлесок снова затихает.\n\n"
            f"{result_line}"
        )
        await _logging_paint(callback, text=text,
                             kb=_result_markup(LOGGING_TOKEN.get(user_id, "")))
        return

    # Ответный удар врага.
    eres = roll_enemy_damage(stats, {
        'dmg_min': battle.get('dmg_min') or LOGGING_SNAKE_SEED['dmg_min'],
        'dmg_max': battle.get('dmg_max') or LOGGING_SNAKE_SEED['dmg_max'],
    })
    enemy_hit = eres['damage']
    if eres['dodged']:
        counter_line = "💨 Ты уклоняешься от выпада! (−0 HP)\n\n"
    else:
        extra = ""
        if eres['armor_blocked']:
            extra += f"🛡️ Броня поглотила {eres['armor_blocked']}. "
        if eres['crit']:
            extra += "💥 crit! "
        counter_line = (f"Змея бьёт: −{enemy_hit} HP. {extra}\n\n" if kind == "snake"
                        else f"Неясыть бьёт когтем: −{enemy_hit} HP. {extra}\n\n")
    battle['player_hp'] -= enemy_hit
    if battle['player_hp'] <= 0:
        await _battle_defeat(callback, user_id, battle,
                             prefix=f"{dot_note}{hit_line}{counter_line}")
        return

    # Наложение эффектов ответным ударом (только если попал): единая система
    # эффектов при ударе (v0.38.0) — яд змеи, ослепление неясыти и всё, что
    # админ добавит в on_hit_effects врага.
    proc_line = ""
    if not eres['dodged']:
        procs = onhit.roll_procs(battle.get('on_hit_effects') or [])
        if procs:
            proc_lines = onhit.apply_procs(user_id, battle, procs,
                                           enemy_name=battle.get('enemy_name') or "Враг")
            proc_line = "".join(f"{line}\n\n" for line in proc_lines)

    # Спад срочных эффектов (оглушение/ослепление и т.д.) в конце хода.
    round_note = "".join(f"{line}\n\n" for line in onhit.end_round(battle))

    battle['round'] += 1
    await _show_battle(callback, prefix=f"{dot_note}{hit_line}{counter_line}{proc_line}{round_note}")


async def _battle_defeat(callback: CallbackQuery, user_id: int, battle: dict,
                         prefix: str = ""):
    """Поражение в бою: пилот теряет ОД и приходит в себя у сторожки."""
    kind = battle.get('kind') or "snake"
    emoji = battle.get('emoji') or SNAKE_EMOJI
    LOGGING_BATTLE.pop(user_id, None)
    onhit.unregister(user_id)
    removed = await remove_ap_or_floor(user_id, int(battle.get('loss_ap')
                                                     or LOGGING_SNAKE_SEED['loss_ap']))
    if kind == "owl":
        await log_activity(user_id, "logging", f"Проиграл Неясыти (−{removed} ОД)")
        text = (
            f"{emoji} НЕЯСЫТЬ\n\n"
            f"{prefix}"
            "Когти впиваются в плечо, крыло обрушивает темноту — сознание "
            "гаснет...\n\n"
            f"Очнулся ты у сторожки, весь в ссадинах. Неясыть ушла в чащу "
            f"(−{removed} ОД)."
        )
    else:
        await log_activity(user_id, "logging", f"Проиграл Лесной змее (−{removed} ОД)")
        text = (
            f"{emoji} БОЙ СО ЗМЕЁЙ\n\n"
            f"{prefix}"
            "Мир плывёт, зубы холодят кровь — сознание гаснет...\n\n"
            f"Очнулся ты у сторожки, тяжело дыша. Змея уползла в подлесок "
            f"(−{removed} ОД)."
        )
    await _logging_paint(callback, text=text,
                         kb=_result_markup(LOGGING_TOKEN.get(user_id, "")))


@router.callback_query(F.data.regexp(r"^logsite:battle:flee:\d+$"))
async def logging_battle_flee(callback: CallbackQuery):
    if not await _logging_ok(callback):
        return
    user_id = callback.from_user.id
    battle = LOGGING_BATTLE.pop(user_id, None)
    onhit.unregister(user_id)
    await callback.answer()
    kind = (battle or {}).get('kind') or "snake"
    if battle:
        await log_activity(user_id, "logging", "Сбежал из боя на лесозаготовке")
    await _logging_paint(
        callback,
        text=("🏃 Ты отступаешь к сторожке, отмахиваясь от врага.\n\n"
              "Бой окончен — но рубка-то не закончена! Попробуй ещё раз!")
        if kind == "snake" else
        ("🏃 Ты отступаешь к сторожке, не сводя глаз с тяжёлого силуэта над "
         "кронами.\n\n"
         "Сова ушла — и хорошо. Рубка-то не закончена! Попробуй ещё раз!"),
        kb=_result_markup(LOGGING_TOKEN.get(user_id, "")),
    )
