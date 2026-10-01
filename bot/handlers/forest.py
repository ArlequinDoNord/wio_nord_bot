"""Лес на окраине: опушка и лесная поляна, сбор грибов и кабан.

Механика: пилот входит в лес (локация city «Лес на окраине») и попадает на ОПУШКУ.
Дальше есть две зоны (v0.18.18), у каждой свой пул грибов и свои настройки:

  🌿 Опушка (glade) — «первый уровень». Только четыре первых простых гриба и
     Бледная поганка, кабана нет, поиск 4 ОД. Туристов сюда пускаем.
  🌲 Лесная поляна (clearing) — «второй уровень», доступна кнопкой с опушки.
     Весь пул грибов, кабан и поиск 5 ОД. Туристам закрыта:
     «не местные — легко заблудиться».

Поиск стоит ap_cost ОД зоны (правится админом), результат через 5–10 секунд,
находка — 90%, остальное делят грибы по весам зоны. В зоне с кабаном не чаще
одного раза на boar_every попыток случается мини-бой: за победу — добыча,
за поражение — −loss_ap ОД. Продажа грибов казне ограничена суточным лимитом
выкупа (forest_settings 'sold_daily_limit', счётчик сбрасывается по суткам МСК).
"""

import asyncio
import os
import random

from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database.db import (
    get_user, remove_ap, get_active_run, add_inventory_item,
    get_award_bonus, get_item, get_item_by_name,
    get_forest_mushroom_pool, get_forest_zone, get_forest_zones, FOREST_AREAS,
    get_forest_setting,
    get_forest_boar_attempts, set_forest_boar_attempts, reset_forest_boar_counter,
    remove_ap_or_floor, user_is_tourist, log_activity,
    get_source_enemy_by_key, get_source_enemy_drops, roll_enemy_drops,
    enemy_encounter_hit,
    get_location_by_key, location_glade_photo, location_photo_for_tod,
)
from utils.helpers import (
    resolve_image, resolve_image_seasonal, season_key, time_of_day_key,
    plural_nordmark, item_local_photo,
)
from config import (
    FOREST_AP_COST, FOREST_RESULT_DELAY, FOREST_ALLOW_TOURISTS, FOREST_SOLD_DAILY_LIMIT,
    FOREST_BOAR_PITY_TARGET, FOREST_BOAR_HP, FOREST_BOAR_DMG,
    FOREST_BOAR_DODGE, FOREST_BOAR_LOSS_AP, FOREST_BOAR_LOOT,
)

router = Router()

# Зона по умолчанию при входе в лес.
FOREST_HOME_AREA = "glade"

# Эмблемы зон для текстов и кнопок.
FOREST_AREA_EMOJI = {"glade": "🌿", "clearing": "🌲"}
FOREST_AREA_NAME = {"glade": "ОПУШКА ЛЕСА", "clearing": "ЛЕСНАЯ ПОЛЯНА"}

# Почему туристам закрыта поляна: не местные, легко заблудиться.
AREA_DENY_TEXT = {
    "clearing": (
        "Дальше — только настоящим пилотам Нордхайма. Поляна за опушкой "
        "раскинулась на десятки вёрст, а тропы между лесами незнакомые: "
        "чужой здесь легко заблудиться. Туристов сюда не пускают — и правильно."
    ),
}

# Доля «ничего не нашёл» на 1 попытку. Остальное (100 − эта доля) делят грибы
# по шансам пула: сейчас находка — 90% (решение владельца 2026-09-30).
FOREST_EMPTY_CHANCE = 10

# Пользователи, чей поиск ещё не завершён (защита от повторного клика).
FOREST_CASTING = set()

# Отслеживаемое сообщение окна леса: user_id -> (chat_id, message_id).
FOREST_MSG: dict = {}

# Токен текущего окна леса: уход в другое меню инвалидирует старые кнопки.
FOREST_TOKEN: dict = {}

# Активные бои с кабаном: user_id -> {token, player_hp, boar_hp, round}.
FOREST_BATTLE: dict = {}


def _new_token() -> str:
    return str(random.randint(100000, 999999))


async def deactivate_forest(user_id: int):
    """Инвалидация окна леса при уходе в другое меню (магазин, город и т.п.)."""
    FOREST_TOKEN.pop(user_id, None)
    FOREST_MSG.pop(user_id, None)
    FOREST_CASTING.discard(user_id)
    FOREST_BATTLE.pop(user_id, None)


def _callback_token(data: str) -> str:
    """Токен окна леса из callback_data.

    Форматы: forest:area:TOKEN:ЗОНА, forest:cast:TOKEN[:ЗОНА],
    forest:battle:hit:TOKEN, forest:battle:flee:TOKEN.

    Раньше токен брали как последний сегмент — это работало только для
    forest:cast:TOKEN. После разделения леса на зоны (v0.18.18) у «поиска»
    и «перехода» появился хвост с названием зоны, токен перестал быть
    последним, и step-guard рубил живые кнопки («окно устарело»).
    Берём последний сегмент из цифр: команды и зоны — словами.
    """
    for part in reversed(data.split(":")[1:]):
        if part.isdigit():
            return part
    return ""


async def _forest_ok(callback) -> bool:
    """Step-guard: callback должен приходить из текущего окна леса."""
    token = _callback_token(callback.data)
    if FOREST_TOKEN.get(callback.from_user.id) != token:
        try:
            await log_activity(callback.from_user.id, "stale_button", "лес: устаревшее окно")
        except Exception:
            pass
        await callback.answer(
            "⏳ Это окно леса устарело — открой опушку заново (Город → Лес на окраине).",
            show_alert=True,
        )
        return False
    return True


def _glade_path() -> str:
    """Опушка, где собирают грибы. Сезонная картинка (зимой — зимняя)."""
    path = resolve_image_seasonal("city/forest_glade")
    if not os.path.isfile(path):
        path = resolve_image_seasonal("city/forest")
    if not os.path.isfile(path):
        path = resolve_image("city/park")
    return path


def _clearing_path() -> str:
    """Лесная поляна: сезонная картинка входа в лес (зимой — зимняя)."""
    path = resolve_image_seasonal("city/forest")
    if not os.path.isfile(path):
        path = resolve_image_seasonal("city/forest_glade")
    if not os.path.isfile(path):
        path = resolve_image("city/park")
    return path


async def _glade_media() -> tuple:
    """Картинка опушки: (photo_id, media_path).

    Опушка — самостоятельная картинка, задаётся админом отдельной кнопкой
    «🌲 Опушка» в редакторе локации (locations.glade_photo). Фото входа в лес
    сюда намеренно НЕ подставляется: это разные места. Если своей картинки нет —
    локальный сезонный файл assets/img/city/forest_glade_<сезон>_<время>.jpg.
    """
    loc = await get_location_by_key("forest")
    photo_id = location_glade_photo(loc)
    if photo_id:
        return photo_id, None
    return None, _glade_path()


async def _clearing_media() -> tuple:
    """Картинка лесной поляны: (photo_id, media_path).

    Здесь наоборот — берётся фото входа в лес из сезонного редактора локации
    (season_photos → photo_<tod>), а без него локальный сезонный файл.
    """
    loc = await get_location_by_key("forest")
    if loc:
        photo_id = location_photo_for_tod(loc, season_key(), time_of_day_key())
        if photo_id:
            return photo_id, None
    return None, _clearing_path()


async def _area_media(area: str) -> tuple:
    """Картинка зоны леса: опушка — своя, поляна — фото входа в лес."""
    if area == "clearing":
        return await _clearing_media()
    return await _glade_media()


async def _glade_paint(callback, *, text: str, kb=None, area: str = "glade"):
    """Отрисовка окна леса на фоне картинки зоны (фото из админки или локальный файл)."""
    photo_id, media_path = await _area_media(area)
    await _paint(callback, text=text, photo_id=photo_id, media_path=media_path, kb=kb)


async def _boar_paint(callback, *, text: str, kb=None):
    """Отрисовка окна схватки: фото врага из БД, иначе сезонная картинка зверя."""
    battle = FOREST_BATTLE.get(callback.from_user.id) or {}
    boar = battle.get('boar') or {}
    if boar.get('image'):
        await _paint(callback, text=text, photo_id=boar['image'], kb=kb)
        return
    path = resolve_image_seasonal(boar.get('photo_key') or "city/forest_boar")
    if not os.path.isfile(path):
        path = _glade_path()
    await _paint(callback, text=text, media_path=path, kb=kb)


async def _paint(callback, *, text: str = None, media_path: str = None, photo_id: str = None, kb=None):
    """Единая отрисовка окна леса в одном сообщении на игрока."""
    bot = callback.message.bot
    chat_id = callback.message.chat.id
    user_id = callback.from_user.id
    entry = FOREST_MSG.get(user_id)
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
    FOREST_MSG[user_id] = (chat_id, sent.message_id)


# ───────── чистые функции (тестируются в smoke) ─────────

def forest_boar_hit(counter_before: int, roll_1toN: int) -> bool:
    """Встреча ли это с кабаном.

    counter_before — число спокойных попыток подряд с последней встречи;
    roll_1toN — бросок 1..N. Встреча, если подряд было N-1 спокойных попыток
    (гарантия на N-й) либо бросок выпал 1 (шанс 1/N).
    """
    if counter_before >= FOREST_BOAR_PITY_TARGET - 1:
        return True
    return roll_1toN == 1


def roll_boar_loot(r: float) -> str:
    """Добыча за победу над кабаном по броску r в [0, 100) (пустая строка — ничего)."""
    acc = 0
    for name, chance in FOREST_BOAR_LOOT:
        acc += chance
        if r < acc:
            return name
    return ""


def pick_forest_mushroom(pool_rows, r: float):
    """Гриб по броску r в [0, 100): FOREST_EMPTY_CHANCE % — пусто, остальное —
    шансы пула. Возвращает строку пула или None.

    Шансы пула — это ВЕСА, а не готовые проценты: они нормируются на свою сумму.
    Поэтому «находка» всегда ровно 100 − FOREST_EMPTY_CHANCE (сейчас 90%), а правка
    веса в админке не обрезает хвост пула и не ломает итог. До нормировки сумма
    весов жёстко складывалась с «пусто» в 100, и грибы из конца списка переставали
    выпадать, если админ завышал веса.
    """
    if r < FOREST_EMPTY_CHANCE:
        return None
    total = sum(int(row['chance'] or 0) for row in pool_rows)
    if total <= 0:
        return None
    acc = float(FOREST_EMPTY_CHANCE)
    for row in pool_rows:
        acc += int(row['chance'] or 0) * (100.0 - FOREST_EMPTY_CHANCE) / total
        if r < acc:
            return row
    return None


# ───────── зоны леса: опушка и лесная поляна ─────────

async def forest_menu_cb(callback: CallbackQuery):
    """Вход из города в лес (location:enter:forest) — открываем опушку."""
    await callback.answer()

    if await get_active_run(callback.from_user.id):
        await callback.message.answer(
            "⛔ Ты сейчас проходишь подземелье — бродить по лесу нельзя.\n"
            "Выйди из подземелья, а потом иди на опушку."
        )
        return

    token = _new_token()
    FOREST_TOKEN[callback.from_user.id] = token
    await _show_area(callback, FOREST_HOME_AREA)


async def _area_allowed(area: str, user_id: int) -> bool:
    """Может ли игрок зайти в зону (открыта ли она и допущены ли туристы)."""
    zone = await get_forest_zone(area)
    if not zone.get("enabled"):
        return False
    if await user_is_tourist(user_id):
        return bool(zone.get("allow_tourists"))
    return True


async def _show_area(callback: CallbackQuery, area: str, prefix: str = ""):
    """Экран зоны леса: описание, цена поиска, кнопки перехода и поиска."""
    if area not in FOREST_AREAS:
        area = FOREST_HOME_AREA
    token = FOREST_TOKEN.get(callback.from_user.id, "")
    zone = await get_forest_zone(area)
    emoji = FOREST_AREA_EMOJI[area]
    title = (zone.get("title") or FOREST_AREA_NAME[area]).upper()
    ap_cost = int(zone.get("ap_cost") or FOREST_AP_COST)

    # Зона выключена админом.
    if not zone.get("enabled"):
        text = (
            f"{prefix}{emoji} {title}\n\n"
            "Сейчас сюда не пускают — зона закрыта. Загляни позже."
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🌿 К опушке", callback_data=f"forest:area:{token}:glade")],
            [InlineKeyboardButton(text="🔙 В город", callback_data="city:menu")],
        ])
        await _glade_paint(callback, text=text, kb=kb, area=area)
        return

    # Турист в зоне без туристов.
    if await user_is_tourist(callback.from_user.id) and not zone.get("allow_tourists"):
        text = (
            f"{prefix}{emoji} {title}\n\n"
            f"{AREA_DENY_TEXT.get(area, 'Сюда туристов не пускают.')}\n\n"
            "Зато на опушке грибы собирают и туристы — там безопасно."
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🌿 К опушке", callback_data=f"forest:area:{token}:glade")],
            [InlineKeyboardButton(text="🔙 В город", callback_data="city:menu")],
        ])
        await _glade_paint(callback, text=text, kb=kb, area=area)
        return

    user = await get_user(callback.from_user.id) or {}
    ap = user.get('ap', 0) or 0
    ap_max = user.get('ap_max', ap) or ap
    ap_line = f"⚡ ОД: {ap}/{ap_max}"
    if ap < ap_cost:
        ap_line += f" — не хватит на поиск ({ap_cost} ОД), придёт с новыми сутками"

    limit = await _treasury_limit()
    if area == "glade":
        desc = (
            "Тёмный еловый лес начинается прямо за городской окраиной. На "
            "опушке — только самое простое: обычные грибы у дороги и изредка "
            "бледная поганка. Здесь спокойно, сюда пускают и туристов."
        )
    else:
        boar_line = ""
        if zone.get("boar_enabled"):
            boar = await _boar()
            every = int(zone.get("boar_every") or 0) or int((boar or {}).get("pity_target") or 0)
            chance = int(zone.get("boar_chance") or 0) or float((boar or {}).get("chance") or 0)
            parts = []
            if chance:
                parts.append(f"шанс встречи {chance:g}%")
            if every:
                parts.append(f"не чаще одного раза на {every} попыток")
            if parts:
                boar_line = "Здесь водятся звери: " + ", ".join(parts) + "."
        desc = (
            "За опушкой начинается настоящий лес. Поляна тянется далеко, и "
            "растут здесь все грибы, какие только есть в Нордхайме — от "
            "опёнка до ежовика гребенчатого." + (f"\n\n{boar_line}" if boar_line else "")
        )

    text = (
        f"{prefix}{emoji} {title}\n\n{desc}\n\n"
        f"{ap_line}\n\n"
        f"Поиск стоит {ap_cost} ОД, результат через 5–10 секунд.\n\n"
        f"🧺 Казна покупает грибы не больше {limit} НМ в сутки — "
        "остальное можно продать на рынке игроков."
    )
    await _glade_paint(callback, text=text, kb=await _area_markup(token, area), area=area)


async def _treasury_limit() -> int:
    """Суточный лимит выкупа грибов казной (из настроек леса)."""
    stored = await get_forest_setting("sold_daily_limit", FOREST_SOLD_DAILY_LIMIT)
    try:
        return max(0, int(stored))
    except (TypeError, ValueError):
        return FOREST_SOLD_DAILY_LIMIT


@router.callback_query(F.data.regexp(r"^forest:area:\d+:(glade|clearing)$"))
async def forest_area_switch(callback: CallbackQuery):
    """Переход между зонами леса: опушка ⇄ лесная поляна."""
    await callback.answer()
    if not await _forest_ok(callback):
        return
    area = callback.data.split(":")[3]
    if not await _area_allowed(area, callback.from_user.id):
        zone = await get_forest_zone(area)
        if not zone.get("enabled"):
            await callback.answer("Сюда пока не пускают.", show_alert=True)
        else:
            await callback.answer("🌲 Сюда туристов не пускают.", show_alert=True)
        return
    await _show_area(callback, area)


async def _area_markup(token: str, area: str):
    """Кнопки зоны: поиск грибов, переход в другую зону, город."""
    rows = [[InlineKeyboardButton(
        text=f"{FOREST_AREA_EMOJI[area]} Искать грибы",
        callback_data=f"forest:cast:{token}:{area}")]]
    other = "clearing" if area == "glade" else "glade"
    if await _zone_open(other):
        rows.append([InlineKeyboardButton(
            text=(f"{FOREST_AREA_EMOJI[other]} "
                  + ("Углубиться в лес" if other == "clearing" else "К опушке")),
            callback_data=f"forest:area:{token}:{other}")])
    rows.append([InlineKeyboardButton(text="🔙 В город", callback_data="city:menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def _zone_open(area: str) -> bool:
    """Открыта ли зона (и пускает ли туристов, если смотрим для туриста)."""
    zone = await get_forest_zone(area)
    return bool(zone.get("enabled"))


async def _show_glade(callback: CallbackQuery, prefix: str = ""):
    """Совместимость со старыми вызовами: показывает опушку."""
    await _show_area(callback, FOREST_HOME_AREA, prefix)


def _glade_markup(token: str, area: str = "glade"):
    """Кнопки зоны (совместимый вызов без зоны = опушка)."""
    return _simple_markup(token, area)


async def _result_markup(token: str, area: str = "glade"):
    """Кнопки после находки: искать ещё в этой же зоне или уйти."""
    return _simple_markup(token, area)


def _simple_markup(token: str, area: str = "glade"):
    emoji = FOREST_AREA_EMOJI.get(area, "🌲")
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{emoji} Поискать ещё", callback_data=f"forest:cast:{token}:{area}")],
        [InlineKeyboardButton(text="🔙 В город", callback_data="city:menu")],
    ])


# ───────── поиск грибов ─────────

@router.callback_query(F.data.regexp(r"^forest:cast:\d+(?::(glade|clearing))?$"))
async def forest_cast(callback: CallbackQuery):
    if not await _forest_ok(callback):
        return
    user_id = callback.from_user.id
    parts = callback.data.split(":")
    area = parts[3] if len(parts) > 3 and parts[3] in FOREST_AREAS else FOREST_HOME_AREA

    # Туристам опушка открыта (если разрешена админом), поляна — никогда.
    if not await _area_allowed(area, user_id):
        zone = await get_forest_zone(area)
        if not zone.get("enabled"):
            await callback.answer("Сюда пока не пускают.", show_alert=True)
        else:
            await callback.answer("🌲 Сюда туристов не пускают.", show_alert=True)
        await _show_area(callback, area)
        return

    if user_id in FOREST_CASTING:
        await callback.answer("Ты уже ищешь грибы — дождись результата!", show_alert=True)
        return

    FOREST_CASTING.add(user_id)
    try:
        if await get_active_run(user_id):
            await callback.answer("⛔ Ты в подземелье — по лесу гулять нельзя!", show_alert=True)
            return

        user = await get_user(user_id)
        if not user:
            await callback.answer("Сначала нажми /start", show_alert=True)
            return

        zone = await get_forest_zone(area)
        ap_cost = int(zone.get("ap_cost") or FOREST_AP_COST)
        area_emoji = FOREST_AREA_EMOJI[area]
        area_name = (zone.get("title") or FOREST_AREA_NAME[area]).lower()

        if not await remove_ap(user_id, ap_cost, reason=f"поиск грибов ({area_name})"):
            await _show_area(callback, area)
            return

        delay = random.randint(*FOREST_RESULT_DELAY)
        cast_text = (
            f"{area_emoji} Ты {'оглядываешь опушку' if area == 'glade' else 'идёшь по тропе к поляне'}...\n"
            f"Результат через {delay} секунд. {'Здесь тихо.' if area == 'glade' else 'Не шуми — прислушивайся!'}"
        )
        await _glade_paint(callback, text=cast_text, kb=None, area=area)
        await log_activity(user_id, "forest", f"Поиск грибов: {area_name} ({ap_cost} ОД)")
        await asyncio.sleep(delay)

        # ── встреча с кабаном: только в зонах, где он включён (v0.18.18) ──
        boar = None
        if zone.get("boar_enabled"):
            boar = await _boar()
        counter_before = await get_forest_boar_attempts(user_id)
        encounter = False
        if boar:
            # Шанс и гарантия: настройки зоны перекрывают карточку врага, если заданы.
            chance = float(zone.get("boar_chance") or 0) or float(boar.get('chance') or 0)
            pity = int(zone.get("boar_every") or 0) or int(boar.get('pity_target') or 0)
            encounter = enemy_encounter_hit(
                chance, random.random() * 100, counter_before, pity)
        if encounter:
            await reset_forest_boar_counter(user_id)
            bonus = (await get_award_bonus(user_id)) or {}
            player_hp = 100 + int(bonus.get('hp') or 0)
            token = FOREST_TOKEN.get(user_id, "")
            FOREST_BATTLE[user_id] = {
                "token": token,
                "area": area,
                "player_hp": player_hp,
                "player_hp_max": player_hp,
                "boar_hp": int(boar.get('hp') or FOREST_BOAR_HP),
                "boar_hp_max": int(boar.get('hp') or FOREST_BOAR_HP),
                "boar_name": boar.get('name') or "Дикий кабан",
                "dodge": float(boar.get('dodge') or 0),
                "dmg_min": int(boar.get('dmg_min') or FOREST_BOAR_DMG[0]),
                "dmg_max": int(boar.get('dmg_max') or FOREST_BOAR_DMG[1]),
                "player_dmg_min": int(boar.get('player_dmg_min') or 9),
                "player_dmg_max": int(boar.get('player_dmg_max') or 15),
                "loss_ap": int(boar.get('loss_ap') or FOREST_BOAR_LOSS_AP),
                "boar": boar,
                "round": 1,
            }
            await _show_battle(callback)
            return

        # Счётчик кабана растёт только там, где кабан есть.
        if zone.get("boar_enabled"):
            await set_forest_boar_attempts(user_id, counter_before + 1)

        # ── выбор гриба из пула ЗОНЫ ──
        pool = await get_forest_mushroom_pool(area)
        row = pick_forest_mushroom(pool, random.random() * 100)
        fresh = await get_user(user_id) or {}
        _ap = fresh.get('ap', 0) or 0
        _ap_max = fresh.get('ap_max', _ap) or _ap
        ap_line = f"⚡ ОД: {_ap}/{_ap_max}"
        if _ap < ap_cost:
            ap_line += f" — на следующий поиск не хватит ({ap_cost} ОД)"
        else:
            ap_line += f" — можно искать ещё"
        ap_block = f"\n\n{ap_line}"
        head = f"{area_emoji} {FOREST_AREA_NAME[area]}"
        result_kb = await _result_markup(FOREST_TOKEN.get(user_id, ""), area)

        if row is None:
            text = (
                f"{head}\n\n"
                "Ты обошёл несколько полян, заглянул под каждую ёлку — "
                "а грибов и нет. Бывает. Попробуй ещё раз!"
            ) + ap_block
            await _glade_paint(callback, text=text, kb=result_kb, area=area)
            return

        item = await get_item(row['item_id'])
        if not item:
            text = (f"{head}\n\n🍄 Что-то нашёл, но предмет потерялся. Сообщи хранителю.") + ap_block
            await _glade_paint(callback, text=text, kb=result_kb, area=area)
            return

        await add_inventory_item(user_id, item['id'], 1)
        await log_activity(user_id, "forest", f"Нашёл «{item['name']}» ({area_name})")
        kind_label = "☠ Ядовитый гриб!" if (row.get('kind') or 'edible') == "toxic" else "🍄"
        sell_line = ""
        if item['sell_price'] > 0:
            sell_line = (
                f"\nПродать можно за {item['sell_price']} "
                f"{plural_nordmark(item['sell_price'])}."
            )
        heal_line = ""
        if item['heal'] and item['heal'] > 0:
            heal_line = f" Сырым восстанавливает {item['heal']} HP в бою."
        text = (
            f"{head}\n\n"
            f"{kind_label} Ты нашёл: «{item['name']}»!\n\n"
            f"🎒 Гриб положен в инвентарь.{heal_line}{sell_line}"
        ) + ap_block
        if row.get('photo_file_id'):
            await _paint(callback, text=text, photo_id=row['photo_file_id'], kb=result_kb)
            return
        local_photo = item_local_photo(item['name'])
        if local_photo:
            await _paint(callback, text=text, media_path=local_photo, kb=result_kb)
            return
        await _glade_paint(callback, text=text, kb=result_kb, area=area)
    finally:
        FOREST_CASTING.discard(user_id)


# ───────── бой с кабаном ─────────

def _hp_bar(hp: int, hp_max: int) -> str:
    hp = max(0, int(hp))
    hp_max = max(1, int(hp_max))
    filled = round(10 * hp / hp_max)
    return "█" * filled + "░" * (10 - filled)


def _boar_fallback() -> dict:
    """Параметры кабана из конфига — если строки в БД ещё нет (или враг выключен).

    Нужно, чтобы лес работал и до сида forest_enemies, и если админ выключил
    кабана (enabled=0) — тогда встреча просто не случается."""
    return {
        "id": 0,
        "name": "Дикий кабан",
        "hp": FOREST_BOAR_HP,
        "dmg_min": FOREST_BOAR_DMG[0],
        "dmg_max": FOREST_BOAR_DMG[1],
        "dodge": FOREST_BOAR_DODGE,
        "player_dmg_min": 9,
        "player_dmg_max": 15,
        "loss_ap": FOREST_BOAR_LOSS_AP,
        "chance": round(100 / FOREST_BOAR_PITY_TARGET, 2),
        "pity_target": FOREST_BOAR_PITY_TARGET,
        "photo_key": "city/forest_boar",
        "enabled": 1,
    }


async def _boar() -> dict | None:
    """Кабан из БД (админ может править HP/урон/шанс/дропы) или None, если выключен."""
    row = await get_source_enemy_by_key("forest", "boar")
    if not row:
        return _boar_fallback()
    if not row.get('enabled'):
        return None
    return dict(row)


async def _roll_boar_loot_items(boar: dict) -> list:
    """Добыча из кабана: список названий предметов (может быть пустым).

    Каждый дроп бросается независимо, поэтому шкура и клык достижимы,
    а не «затеняются» мясом. Нет дропов в БД — запасной вариант из конфига.
    """
    if boar.get('id'):
        drops = await get_source_enemy_drops("forest", boar['id'])
        if drops:
            names = []
            for d in roll_enemy_drops(drops):
                item = await get_item(d.get('item_id'))
                if item:
                    names.append(item['name'])
            return names
    name = roll_boar_loot(random.random() * 100)
    return [name] if name else []


def _battle_markup(token: str):
    rows = [
        [InlineKeyboardButton(text="⚔️ Ударить", callback_data=f"forest:battle:hit:{token}")],
        [InlineKeyboardButton(text="🏃 Сбежать", callback_data=f"forest:battle:flee:{token}")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def _show_battle(callback: CallbackQuery, prefix: str = ""):
    battle = FOREST_BATTLE.get(callback.from_user.id)
    if not battle:
        await _show_area(callback, FOREST_HOME_AREA, prefix="❌ Бой потерян.\n\n")
        return
    player_hp = battle['player_hp']
    boar_hp = battle['boar_hp']
    boar_hp_max = battle.get('boar_hp_max') or battle['boar_hp']
    boar_name = battle.get('boar_name') or "Дикий кабан"
    text = (
        f"{prefix}🐗 {boar_name.upper()}\n\n"
        f"Кусты позади взрываются хрустом — на тебя несётся взбешённый зверь!\n\n"
        f"🐗 Зверь   HP {_hp_bar(boar_hp, boar_hp_max)} {max(0, boar_hp)}/{boar_hp_max}\n"
        f"🧑 Ты     HP {_hp_bar(player_hp, battle['player_hp_max'])} "
        f"{max(0, player_hp)}/{battle['player_hp_max']}\n\n"
        f"Ход {battle['round']}. Ударь зверя — или уноси ноги."
    )
    await _boar_paint(callback, text=text,
                 kb=_battle_markup(battle['token']))


@router.callback_query(F.data.regexp(r"^forest:battle:hit:\d+$"))
async def forest_battle_hit(callback: CallbackQuery):
    if not await _forest_ok(callback):
        return
    user_id = callback.from_user.id
    battle = FOREST_BATTLE.get(user_id)
    if not battle:
        await _show_area(callback, FOREST_HOME_AREA, prefix="⏳ Бой с кабаном устарел.\n\n")
        return
    await callback.answer()

    # Твой удар: зверь может уклониться (шанс уклонения — из БД).
    if random.random() * 100 < float(battle.get('dodge') or 0):
        player_hit = 0
        hit_line = "Ты замахнулся — но зверь увернулся в последний миг.\n\n"
    else:
        player_hit = random.randint(int(battle.get('player_dmg_min') or 9),
                                    int(battle.get('player_dmg_max') or 15))
        battle['boar_hp'] -= player_hit
        hit_line = f"Ты бьёшь наотмашь: −{player_hit} HP по зверю!\n\n"

    if battle['boar_hp'] <= 0:
        battle_area = battle.get('area') or FOREST_HOME_AREA
        FOREST_BATTLE.pop(user_id, None)
        await log_activity(user_id, "forest", "Победил зверя в лесу")
        loot_names = await _roll_boar_loot_items(battle.get('boar') or {})
        got = []
        for loot in loot_names:
            loot_item = await get_item_by_name(loot)
            if not loot_item:
                continue
            await add_inventory_item(user_id, loot_item['id'], 1)
            await log_activity(user_id, "forest", f"Добыча: {loot}")
            got.append(loot)
        if got:
            loot_list = "\n".join(f"• «{name}»" for name in got)
            head = "Из поверженного зверя ты добыл:" if len(got) > 1 \
                else "Из поверженного зверя ты добыл:"
            result_line = f"{head}\n{loot_list}\n\nПоложено в инвентарь."
        elif loot_names:
            result_line = "Зверь повержен, но добыча потерялась. Сообщи хранителю."
        else:
            result_line = "Зверь повержен, но ничего ценного на этот раз не нашлось."
        text = (
            "🐗 БОЙ С ЗВЕРЕМ\n\n"
            f"{hit_line}"
            "Зверь споткнулся и рухнул — тишина снова принадлежит лесу.\n\n"
            f"{result_line}"
        )
        await _boar_paint(callback, text=text,
                     kb=await _result_markup(FOREST_TOKEN.get(user_id, ""), battle_area))
        return

    # Ответный удар зверя.
    boar_hit = random.randint(int(battle.get('dmg_min') or FOREST_BOAR_DMG[0]),
                              int(battle.get('dmg_max') or FOREST_BOAR_DMG[1]))
    battle['player_hp'] -= boar_hit
    if battle['player_hp'] <= 0:
        battle_area = battle.get('area') or FOREST_HOME_AREA
        FOREST_BATTLE.pop(user_id, None)
        removed = await remove_ap_or_floor(user_id, int(battle.get('loss_ap') or FOREST_BOAR_LOSS_AP))
        await log_activity(user_id, "forest", f"Проиграл зверю в лесу (−{removed} ОД)")
        text = (
            "🐗 БОЙ С ЗВЕРЕМ\n\n"
            f"{hit_line}"
            f"Зверь бьёт: −{boar_hit} HP... ты теряешь сознание.\n\n"
            f"Очнулся ты на {FOREST_AREA_NAME[battle_area].lower()} весь в ссадинах — "
            f"зверь ушёл в чащу. Победа досталась ему ценой твоих сил: −{removed} ОД."
        )
        await _boar_paint(callback, text=text,
                     kb=await _result_markup(FOREST_TOKEN.get(user_id, ""), battle_area))
        return

    battle['round'] += 1
    await _show_battle(
        callback,
        prefix=f"{hit_line}"
    )


@router.callback_query(F.data.regexp(r"^forest:battle:flee:\d+$"))
async def forest_battle_flee(callback: CallbackQuery):
    if not await _forest_ok(callback):
        return
    user_id = callback.from_user.id
    stale = FOREST_BATTLE.pop(user_id, None)
    if not stale:
        await _show_area(callback, FOREST_HOME_AREA, prefix="⏳ Бой с кабаном устарел.\n\n")
        return
    flee_area = stale.get('area') or FOREST_HOME_AREA
    await callback.answer()
    await log_activity(user_id, "forest", "Сбежал от кабана")
    await _show_area(
        callback, flee_area,
        prefix=f"🏃 Ты вырвался из чащи — кабан остался позади.\n\n")