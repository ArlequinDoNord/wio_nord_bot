"""Рыбалка на Озере в парке.

Механика: игрок закидывает удочку (за 3 ОД), наживка списывается сразу,
результат приходит через 7–15 секунд. Шанс улова зависит от удочки (ранг =
редкость предмета) и наживки. В пуле озера: Сиг (часто), Муксун (редкий),
Чир (очень редкий); ночью (19:10–08:00 МСК) дополнительно — Налим.
"""

import asyncio
import os
import random

from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database.db import (
    get_item_by_name, get_inventory_item, remove_inventory_item,
    add_fish_catch, add_inventory_item, get_user, update_user,
    remove_ap, log_activity,
)
from utils.helpers import resolve_image, time_of_day_key, plural_nordmark, item_local_photo, fish_weight_tier, fish_sell_price
from config import FISH_AP_COST, FISH_WEIGHTS

router = Router()

ROD_NAME = "Удочка из орешника"
WORMS_NAME = "Черви"
SPIDER_LEG_NAME = "Лапка кристального паука"
SEAWEED_NAME = "Кусочек водорослей"
BOOT_NAME = "Старый сапог"
LAKE_PHOTO = "city/lake"

# Пользователи, чей заброс ещё не завершён (защита от повторного клика)
FISHING_CASTING = set()

# Шанс улова: 50% база + ранг удочки*10 + бонус наживки, максимум 90%
FISHING_BASE_CHANCE = 50
BAIT_BONUS = {WORMS_NAME: 15, SPIDER_LEG_NAME: 25}
ROD_BONUS_PER_RANK = 10
CHANCE_CAP = 90

FISH_EMOJI = {
    "Сиг": "🐟",
    "Муксун": "🐟",
    "Чир": "🌟",
    "Налим": "🐠",
}

# (название рыбы, вес в случайном пуле)
FISH_POOL_DAY = [("Сиг", 65), ("Муксун", 25), ("Чир", 10)]
FISH_POOL_NIGHT = [("Сиг", 63), ("Муксун", 23), ("Чир", 9), ("Налим", 5)]

# Без наживки рыба не клюёт: с дна достаются только мусорные находки.
JUNK_SEAWEED_CHANCE = 15   # кусочек водорослей (крафт энергетиков)
JUNK_BOOT_CHANCE = 2       # старый сапог (продажа за 15 НМ)


def _pick_junk():
    """Случайная находка со дна без наживки: None — ничего."""
    r = random.random() * 100
    if r < JUNK_BOOT_CHANCE:
        return BOOT_NAME
    if r < JUNK_BOOT_CHANCE + JUNK_SEAWEED_CHANCE:
        return SEAWEED_NAME
    return None


def _lake_path() -> str:
    path = resolve_image(LAKE_PHOTO)
    if not os.path.isfile(path):
        path = resolve_image("city/park")
    return path


# Отслеживаемое сообщение окна рыбалки: user_id -> (chat_id, message_id).
# Все отрисовки переиспользуют одно сообщение, чтобы не копились старые
# кнопки «Забросить/Ещё раз», которые можно спамить.
FISH_MSG: dict = {}


async def _paint(callback, *, text: str = None, media_path: str = None, kb=None):
    """Единая отрисовка окна рыбалки в одном сообщении на игрока.

    media_path — локальный файл фото (озеро/рыба); иначе обычный текст.
    Если сообщение не удаётся отредактировать (другой тип медиа / удалено),
    создаём новое и запоминаем его, старое — удаляем.
    """
    bot = callback.message.bot
    chat_id = callback.message.chat.id
    user_id = callback.from_user.id
    entry = FISH_MSG.get(user_id)
    target_id = entry[1] if entry and entry[0] == chat_id else None

    if target_id is not None:
        try:
            if media_path:
                from aiogram.types import InputMediaPhoto
                await bot.edit_message_media(
                    chat_id, target_id,
                    media=InputMediaPhoto(media=FSInputFile(media_path), caption=text),
                    reply_markup=kb,
                )
            else:
                await bot.edit_message_text(chat_id, target_id, text=text, reply_markup=kb)
            return
        except Exception:
            pass

    # Не получилось отредактировать: убираем старую версию и шлём новую.
    if target_id is not None and target_id != callback.message.message_id:
        try:
            await bot.delete_message(chat_id, target_id)
        except Exception:
            pass
    if media_path:
        sent = await bot.send_photo(chat_id, FSInputFile(media_path), caption=text, reply_markup=kb)
    else:
        sent = await bot.send_message(chat_id, text, reply_markup=kb)
    FISH_MSG[user_id] = (chat_id, sent.message_id)


async def _rod_for(user_id: int):
    """Удочка игрока (предмет + наличие в инвентаре) или None."""
    item = await get_item_by_name(ROD_NAME)
    if not item:
        return None
    inv = await get_inventory_item(user_id, item['id'])
    if not inv or inv['quantity'] < 1:
        return None
    return item


async def _resolve_bait(user_id: int, chosen: str):
    """Подбирает наживку для заброса.

    chosen: '' — авто (сначала черви, затем лапка), 'worms'/'spider' —
    конкретная, 'none' — без наживки осознанно.
    Возвращает (имя_наживки_или_None, item_id_наживки_или_None).
    """
    if chosen == "none":
        return None, None
    candidates = []
    if chosen:
        candidates.append(chosen)
    candidates += [n for n in (WORMS_NAME, SPIDER_LEG_NAME) if n not in candidates]
    for name in candidates:
        item = await get_item_by_name(name)
        if not item:
            continue
        inv = await get_inventory_item(user_id, item['id'])
        if inv and inv['quantity'] > 0:
            return name, item['id']
    return None, None


def _catch_chance(rod, bait_name: str) -> int:
    """Шанс улова в процентах при данной удочке и наживке."""
    if not rod:
        return 0
    rank = rod['rarity'] or 1
    bonus = ROD_BONUS_PER_RANK * rank
    bait = BAIT_BONUS.get(bait_name, 0)
    return min(CHANCE_CAP, FISHING_BASE_CHANCE + bonus + bait)


def _pick_fish() -> str:
    """Случайная рыба по весам; ночью в пуле дополнительно Налим."""
    pool = FISH_POOL_NIGHT if time_of_day_key() == "night" else FISH_POOL_DAY
    total = sum(w for _, w in pool)
    r = random.random() * total
    acc = 0
    for name, weight in pool:
        acc += weight
        if r < acc:
            return name
    return pool[-1][0]


def _roll_fish_weight() -> int:
    """Случайный вес улова (индекс в FISH_WEIGHTS: 1=мелкая..3=большая)."""
    total = sum(t['chance'] for t in FISH_WEIGHTS)
    r = random.random() * total
    acc = 0
    for idx, tier in enumerate(FISH_WEIGHTS, 1):
        acc += tier['chance']
        if r < acc:
            return idx
    return len(FISH_WEIGHTS)


async def _bait_label(user_id: int, chosen: str):
    """Текстовая строка наживки для меню озера."""
    if chosen == "none":
        return "🚫 Без наживки"
    name, item_id = await _resolve_bait(user_id, chosen)
    if not name:
        return "🚫 Наживки нет"
    inv = await get_inventory_item(user_id, item_id)
    qty = inv['quantity'] if inv else 0
    return f"{name} x{qty} (+{BAIT_BONUS[name]}%)"


def _lake_markup():
    rows = [
        [InlineKeyboardButton(text="🎣 Забросить удочку", callback_data="fish:cast")],
        [InlineKeyboardButton(text="🪱 Наживка", callback_data="fish:bait")],
        [InlineKeyboardButton(text="🔙 В парк", callback_data="park:menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _result_markup():
    rows = [
        [InlineKeyboardButton(text="🎣 Ещё раз", callback_data="fish:cast")],
        [InlineKeyboardButton(text="🔙 В парк", callback_data="park:menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _bait_markup(user_id: int, chosen: str, worms_qty: int, spider_qty: int):
    def row(label: str, value: str):
        marked = " ✓" if chosen == value else ""
        return label + marked
    rows = [
        [InlineKeyboardButton(
            row(f"🐛 {WORMS_NAME} x{worms_qty} (+{BAIT_BONUS[WORMS_NAME]}%)", "worms"),
            callback_data="fish:bait:set:worms")],
        [InlineKeyboardButton(
            row(f"🕷 {SPIDER_LEG_NAME} x{spider_qty} (+{BAIT_BONUS[SPIDER_LEG_NAME]}%)", "spider"),
            callback_data="fish:bait:set:spider")],
        [InlineKeyboardButton(
            row("🚫 Без наживки", "none"),
            callback_data="fish:bait:set:none")],
        [InlineKeyboardButton(text="🔙 К озеру", callback_data="fish:lake")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def fishing_lake_menu(callback: CallbackQuery):
    """Меню озера с рыбалкой (вход из парка: park:lake)."""
    await callback.answer()
    user = await get_user(callback.from_user.id)
    user = user or {}
    chosen = (user.get('fishing_bait') or "").strip()

    rod = await _rod_for(callback.from_user.id)
    if rod:
        rank = rod['rarity'] or 1
        bait_label = await _bait_label(callback.from_user.id, chosen)
        bait_name, _ = await _resolve_bait(callback.from_user.id, chosen)
        chance = _catch_chance(rod, bait_name)
        rod_line = f"🎣 Удочка: {rod['name']} (ранг {rank}, +{rank * ROD_BONUS_PER_RANK}%)"
        bait_line = f"🪱 Наживка: {bait_label}"
        chance_line = f"⚡ Шанс улова: {chance}%"
        if not bait_name:
            chance_line = (
                f"⚡ Без наживки рыба НЕ клюёт.\n"
                f"Со дна можно выловить только мусор: водоросли {JUNK_SEAWEED_CHANCE}%, "
                f"старый сапог {JUNK_BOOT_CHANCE}%."
            )
    else:
        rod_line = "🎣 Удочка: нет — купи «Удочка из орешника» (магазин → Рыбалка)"
        bait_line = "🪱 Наживка: нужна удочка"
        chance_line = ""

    ap = user.get('ap', 0) or 0
    ap_max = user.get('ap_max', ap) or ap
    ap_line = f"⚡ ОД: {ap}/{ap_max}"
    if ap < FISH_AP_COST:
        ap_line += f" — не хватит на заброс ({FISH_AP_COST} ОД), придёт с новыми сутками"

    caption = (
        "🌊 ОЗЕРО В ПАРКЕ\n\n"
        "Зеркальная гладь среди деревьев. Тут водятся рыбы: "
        "чаще всего Сиг, встречаются Муксун и редкий Чир, а ночами — Налим.\n\n"
        f"{rod_line}\n"
        f"{bait_line}\n"
        f"{chance_line}\n\n"
        f"{ap_line}\n\n"
        f"Заброс стоит {FISH_AP_COST} ОД, результат через 7–15 секунд."
    )
    await _paint(callback, text=caption, media_path=_lake_path(), kb=_lake_markup())


@router.callback_query(F.data == "fish:lake")
async def fish_lake_cb(callback: CallbackQuery):
    await fishing_lake_menu(callback)


@router.callback_query(F.data == "fish:bait")
async def fish_bait_menu(callback: CallbackQuery):
    await callback.answer()
    user = await get_user(callback.from_user.id)
    user = user or {}
    chosen = (user.get('fishing_bait') or "").strip()

    worms = await get_item_by_name(WORMS_NAME)
    spider = await get_item_by_name(SPIDER_LEG_NAME)
    worms_qty = 0
    if worms:
        w_inv = await get_inventory_item(callback.from_user.id, worms['id'])
        worms_qty = w_inv['quantity'] if w_inv else 0
    spider_inv = await get_inventory_item(callback.from_user.id, spider['id']) if spider else None
    spider_qty = spider_inv['quantity'] if spider else 0

    selected = {
        "worms": WORMS_NAME,
        "spider": SPIDER_LEG_NAME,
        "none": "Без наживки",
        "": "Авто (что есть)",
    }.get(chosen, "")
    text = (
        "🪱 НАЖИВКА\n\n"
        f"Сейчас: {selected or chosen}\n"
        "Наживка расходуется при каждом забросе.\n"
        "«Авто»: сначала черви, при их отсутствии — лапка.\n\n"
        f"⚠️ Без наживки рыба не клюёт: со дна только мусор "
        f"(водоросли {JUNK_SEAWEED_CHANCE}%, сапог {JUNK_BOOT_CHANCE}%)."
    )
    await _paint(callback, text=text, kb=_bait_markup(callback.from_user.id, chosen, worms_qty, spider_qty))


@router.callback_query(F.data.startswith("fish:bait:set:"))
async def fish_bait_choose(callback: CallbackQuery):
    await callback.answer()
    value = callback.data.split(":", 3)[3]
    await update_user(callback.from_user.id, fishing_bait=value)
    await fishing_lake_menu(callback)


@router.callback_query(F.data == "fish:cast")
async def fish_cast(callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id in FISHING_CASTING:
        await callback.answer("Ты уже закинул удочку — дождись результата!", show_alert=True)
        return

    user = await get_user(user_id)
    if not user:
        await callback.answer("Сначала нажми /start", show_alert=True)
        return

    rod = await _rod_for(user_id)
    if not rod:
        await _paint(
            callback,
            text="❌ У тебя нет удочки. Купи «Удочка из орешника» в магазине (категория «Рыбалка»).",
            kb=_lake_markup(),
        )
        return

    if not await remove_ap(user_id, FISH_AP_COST):
        await _paint(
            callback,
            text=f"❌ Не хватает ОД: нужно {FISH_AP_COST}, доступно меньше. Восстановление — в новые сутки.",
            kb=_lake_markup(),
        )
        return

    chosen = (user.get('fishing_bait') or "").strip()
    bait_name, bait_id = await _resolve_bait(user_id, chosen)
    if bait_id is not None:
        await remove_inventory_item(user_id, bait_id, 1)

    FISHING_CASTING.add(user_id)
    try:
        delay = random.randint(7, 15)
        bait_part = f" с наживкой «{bait_name}»" if bait_name else " без наживки"
        chance = _catch_chance(rod, bait_name)
        # Заброс всегда показываем на картинке озера (базовый ракурс),
        # чтобы результат заметно менял картинку.
        cast_text = (
            f"🎣 Ты забросил удочку{bait_part}...\n"
            f"Результат через {delay} секунд. Наберись терпения!"
        )
        await _paint(callback, text=cast_text, media_path=_lake_path(), kb=None)
        await log_activity(user_id, "fishing",
                           f"Заброс: наживка={'—' if not bait_name else bait_name}, шанс {chance}%")
        await asyncio.sleep(delay)

        # Счётичик ОД после поклёвки (перед решением «Ещё раз»)
        fresh = await get_user(user_id) or {}
        _ap = fresh.get('ap', 0) or 0
        _ap_max = fresh.get('ap_max', _ap) or _ap
        ap_line = f"⚡ ОД: {_ap}/{_ap_max}"
        if _ap < FISH_AP_COST:
            ap_line += f" — на следующий заброс не хватит ({FISH_AP_COST} ОД)"
        else:
            ap_line += f" — можно забрасывать"
        ap_block = f"\n\n{ap_line}"

        if bait_name:
            # С наживкой — рыбалка как раньше.
            caught = random.random() * 100 < chance
            if caught:
                fish_name = _pick_fish()
                fish_item = await get_item_by_name(fish_name)
                if fish_item:
                    weight_idx = _roll_fish_weight()
                    tier = fish_weight_tier(weight_idx)
                    sell = fish_sell_price(fish_item['sell_price'], weight_idx)
                    await add_fish_catch(user_id, fish_item['id'], weight_idx)
                    await log_activity(user_id, "fishing", f"Поймал «{fish_name}» ({tier['label']})")
                    text = (
                        f"{FISH_EMOJI.get(fish_name, '🐟')} РЫБАЛКА\n\n"
                        f"Поплавок дёрнулся — поклёвка!\n"
                        f"Ты поймал: «{fish_name}» — {tier['label'].lower()}!\n\n"
                        f"🎒 Улов отправлен в инвентарь.\n"
                        f"Вес влияет на цену: продажа за {sell} {plural_nordmark(sell)}."
                    )
                    local_photo = item_local_photo(fish_name)
                    if local_photo:
                        await _paint(callback, text=text + ap_block, media_path=local_photo, kb=_result_markup())
                        return
                else:
                    text = "🎣 Рыбалка\n\n🐟 Что-то поймал, но предмет потерялся. Сообщи хранителю."
            else:
                text = (
                    "🎣 РЫБАЛКА\n\n"
                    "Поплавок дёрнулся, ты подсекаешь... и вдруг пусто.\n"
                    "Сорвалось. Но рыба никуда не денется — пробуй ещё!"
                )
        else:
            # Без наживки рыба не клюёт — из дна достаётся только мусор.
            junk_name = _pick_junk()
            if junk_name:
                junk_item = await get_item_by_name(junk_name)
                if junk_item:
                    await add_inventory_item(user_id, junk_item['id'], 1)
                    await log_activity(user_id, "fishing", f"Выловил «{junk_name}»")
                    sell_line = ""
                    if junk_item['sell_price'] > 0:
                        sell_line = (
                            f"\nПродать можно за {junk_item['sell_price']} "
                            f"{plural_nordmark(junk_item['sell_price'])}."
                        )
                    text = (
                        f"🎣 РЫБАЛКА\n\n"
                        f"Поплавок дёрнулся, ты подсекаешь...\n"
                        f"Из воды появляется: «{junk_name}»!\n\n"
                        f"🎒 Предмет отправлен в инвентарь.{sell_line}"
                    )
                else:
                    text = "🎣 Рыбалка\n\n🐟 Что-то выловил, но предмет потерялся. Сообщи хранителю."
            else:
                text = (
                    "🎣 РЫБАЛКА\n\n"
                    "Поплавок даже не дрогнул. Без наживки рыба не клюёт — "
                    "с дна достаётся только мусор. Попробуй с наживкой!"
                )
        # Счётчик ОД перед следующим забросом
        text += ap_block
        await _paint(callback, text=text, kb=_result_markup())
    finally:
        FISHING_CASTING.discard(user_id)