"""Лес на окраине: сбор грибов и кабан.

Механика: пилот входит в лес (локация city «Лес на окраине»), на опушке
выбирает «🌲 Искать грибы» (3 ОД). Результат приходит через 5–10 секунд.
Из пула грибов (forest_mushrooms, шансы правит админ в редакторе грибов)
выпадает один из 8 грибов или ничего. Не чаще одного раза на 12 попыток
встречается кабан — интерактивный мини-бой с кнопками; за победу — добыча
(мясо/шкура/клык), за проигрыш — −10 ОД (до нуля).

Туристы пока не собирают грибы (FOREST_ALLOW_TOURISTS = False): они гуляют
по опушке и ждут, когда лес откроют и для них.
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
    get_forest_mushroom_pool,
    get_forest_boar_attempts, set_forest_boar_attempts, reset_forest_boar_counter,
    remove_ap_or_floor, user_is_tourist, log_activity,
    get_source_enemy_by_key, get_source_enemy_drops, roll_enemy_drops,
    enemy_encounter_hit,
)
from utils.helpers import (
    resolve_image, resolve_image_seasonal,
    plural_nordmark, item_local_photo,
)
from config import (
    FOREST_AP_COST, FOREST_RESULT_DELAY, FOREST_ALLOW_TOURISTS,
    FOREST_BOAR_PITY_TARGET, FOREST_BOAR_HP, FOREST_BOAR_DMG,
    FOREST_BOAR_DODGE, FOREST_BOAR_LOSS_AP, FOREST_BOAR_LOOT,
)

router = Router()

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


async def _forest_ok(callback) -> bool:
    """Step-guard: callback должен приходить из текущего окна леса."""
    rest = callback.data[len("forest:"):]
    # cast:TOKEN | battle:hit:TOKEN | battle:flee:TOKEN
    token = rest.split(":")[-1]
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


async def _glade_media() -> tuple:
    """Картинка опушки: (photo_id, media_path).

    Опушка намеренно НЕ берёт фото локации «Лес на окраине»: то фото —
    это вход в лес, и по требованию игрока опушка должна быть отдельной
    картинкой. Здесь всегда локальный сезонный файл
    assets/img/city/forest_glade_<сезон>_<время>.jpg → forest_glade_<сезон>
    → forest_glade_<время> → forest_glade_day → forest (запасной вариант).
    """
    return None, _glade_path()


async def _glade_paint(callback, *, text: str, kb=None):
    """Отрисовка окна леса на фоне опушки (фото из админки или локальный файл)."""
    photo_id, media_path = await _glade_media()
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


# ───────── опушка ─────────

async def forest_menu_cb(callback: CallbackQuery):
    """Опушка леса (вход из города: location:enter:forest)."""
    await callback.answer()

    if await get_active_run(callback.from_user.id):
        await callback.message.answer(
            "⛔ Ты сейчас проходишь подземелье — бродить по лесу нельзя.\n"
            "Выйди из подземелья, а потом иди на опушку."
        )
        return

    token = _new_token()
    FOREST_TOKEN[callback.from_user.id] = token

    tourist = await user_is_tourist(callback.from_user.id)
    if tourist and not FOREST_ALLOW_TOURISTS:
        text = (
            "🌲 ОПУШКА ЛЕСА\n\n"
            "Сосны шумят высоко над головой, пахнет хвоей и сырой землёй. "
            "Под ногами — упругий ковёр мха.\n\n"
            "Ты пока только турист: собирать грибы отважные пилоты Нордхайма "
            "доверяют лишь себе. Но опушка ждёт и тебя — как только лес откроют "
            "для всех, ты сможешь отправиться за грибами."
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 В город", callback_data="city:menu")],
        ])
        await _glade_paint(callback, text=text, kb=kb)
        return

    await _show_glade(callback)


async def _show_glade(callback: CallbackQuery, prefix: str = ""):
    token = FOREST_TOKEN.get(callback.from_user.id, "")
    user = await get_user(callback.from_user.id)
    user = user or {}
    ap = user.get('ap', 0) or 0
    ap_max = user.get('ap_max', ap) or ap
    ap_line = f"⚡ ОД: {ap}/{ap_max}"
    if ap < FOREST_AP_COST:
        ap_line += f" — не хватит на поиск ({FOREST_AP_COST} ОД), придёт с новыми сутками"

    text = (
        f"{prefix}🌲 ОПУШКА ЛЕСА\n\n"
        "Тёмный еловый лес начинается прямо за городской окраиной. Здесь "
        "прячутся и грибы, и кое-что посмелее: говорят, по опушкам бродит "
        "злобный кабан.\n\n"
        f"{ap_line}\n\n"
        f"Поиск стоит {FOREST_AP_COST} ОД, результат через 5–10 секунд.\n"
        "Не чаще одного раза на 12 попыток тебя ждёт встреча со зверем. "
        "За победу — добыча, за поражение — потеря 10 ОД."
    )
    await _glade_paint(callback, text=text, kb=_glade_markup(token))


def _glade_markup(token: str):
    rows = [
        [InlineKeyboardButton(text="🌲 Искать грибы", callback_data=f"forest:cast:{token}")],
        [InlineKeyboardButton(text="🔙 В город", callback_data="city:menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _result_markup(token: str):
    rows = [
        [InlineKeyboardButton(text="🌲 Поискать ещё", callback_data=f"forest:cast:{token}")],
        [InlineKeyboardButton(text="🔙 В город", callback_data="city:menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ───────── поиск грибов ─────────

@router.callback_query(F.data.regexp(r"^forest:cast:\d+$"))
async def forest_cast(callback: CallbackQuery):
    if not await _forest_ok(callback):
        return
    user_id = callback.from_user.id
    if await user_is_tourist(user_id):
        await callback.answer("🌲 Пока только пилоты собирают грибы.", show_alert=True)
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

        if not await remove_ap(user_id, FOREST_AP_COST, reason="поиск грибов"):
            await _show_glade(callback)
            return

        delay = random.randint(*FOREST_RESULT_DELAY)
        cast_text = (
            f"🌲 Ты углубился в лес по еле заметной тропе...\n"
            f"Результат через {delay} секунд. Не шуми — прислушивайся!"
        )
        await _glade_paint(callback, text=cast_text, kb=None)
        await log_activity(user_id, "forest", f"Поиск грибов ({FOREST_AP_COST} ОД)")
        await asyncio.sleep(delay)

        # ── встреча с кабаном (шанс и гарантия — из БД) ──
        boar = await _boar()
        counter_before = await get_forest_boar_attempts(user_id)
        encounter = False
        if boar:
            encounter = enemy_encounter_hit(
                float(boar.get('chance') or 0), random.random() * 100,
                counter_before, int(boar.get('pity_target') or 0))
        if encounter:
            await reset_forest_boar_counter(user_id)
            bonus = (await get_award_bonus(user_id)) or {}
            player_hp = 100 + int(bonus.get('hp') or 0)
            token = FOREST_TOKEN.get(user_id, "")
            FOREST_BATTLE[user_id] = {
                "token": token,
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

        await set_forest_boar_attempts(user_id, counter_before + 1)

        # ── выбор гриба из пула ──
        pool = await get_forest_mushroom_pool()
        row = pick_forest_mushroom(pool, random.random() * 100)
        fresh = await get_user(user_id) or {}
        _ap = fresh.get('ap', 0) or 0
        _ap_max = fresh.get('ap_max', _ap) or _ap
        ap_line = f"⚡ ОД: {_ap}/{_ap_max}"
        if _ap < FOREST_AP_COST:
            ap_line += f" — на следующий поиск не хватит ({FOREST_AP_COST} ОД)"
        else:
            ap_line += f" — можно искать ещё"
        ap_block = f"\n\n{ap_line}"

        if row is None:
            text = (
                "🌲 ЛЕС\n\n"
                "Ты обошёл несколько полян, заглянул под каждую ёлку — "
                "а грибов и нет. Бывает. Попробуй ещё раз!"
            ) + ap_block
            await _glade_paint(callback, text=text,
                         kb=_result_markup(FOREST_TOKEN.get(user_id, "")))
            return

        item = await get_item(row['item_id'])
        if not item:
            text = ("🌲 ЛЕС\n\n🍄 Что-то нашёл, но предмет потерялся. Сообщи хранителю.") + ap_block
            await _glade_paint(callback, text=text,
                         kb=_result_markup(FOREST_TOKEN.get(user_id, "")))
            return

        await add_inventory_item(user_id, item['id'], 1)
        await log_activity(user_id, "forest", f"Нашёл «{item['name']}»")
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
            f"🌲 ЛЕС\n\n"
            f"{kind_label} Ты нашёл: «{item['name']}»!\n\n"
            f"🎒 Гриб положен в инвентарь.{heal_line}{sell_line}"
        ) + ap_block
        if row.get('photo_file_id'):
            await _paint(callback, text=text, photo_id=row['photo_file_id'],
                         kb=_result_markup(FOREST_TOKEN.get(user_id, "")))
            return
        local_photo = item_local_photo(item['name'])
        if local_photo:
            await _paint(callback, text=text, media_path=local_photo,
                         kb=_result_markup(FOREST_TOKEN.get(user_id, "")))
            return
        await _glade_paint(callback, text=text,
                     kb=_result_markup(FOREST_TOKEN.get(user_id, "")))
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
        await _show_glade(callback, prefix="❌ Бой потерян.\n\n")
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
        await _show_glade(callback, prefix="⏳ Бой с кабаном устарел.\n\n")
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
                     kb=_result_markup(FOREST_TOKEN.get(user_id, "")))
        return

    # Ответный удар зверя.
    boar_hit = random.randint(int(battle.get('dmg_min') or FOREST_BOAR_DMG[0]),
                              int(battle.get('dmg_max') or FOREST_BOAR_DMG[1]))
    battle['player_hp'] -= boar_hit
    if battle['player_hp'] <= 0:
        FOREST_BATTLE.pop(user_id, None)
        removed = await remove_ap_or_floor(user_id, int(battle.get('loss_ap') or FOREST_BOAR_LOSS_AP))
        await log_activity(user_id, "forest", f"Проиграл зверю в лесу (−{removed} ОД)")
        text = (
            "🐗 БОЙ С ЗВЕРЕМ\n\n"
            f"{hit_line}"
            f"Зверь бьёт: −{boar_hit} HP... ты теряешь сознание.\n\n"
            "Очнулся ты на опушке весь в ссадинах — зверь ушёл в чащу. "
            f"Победа досталась ему ценой твоих сил: −{removed} ОД."
        )
        await _boar_paint(callback, text=text,
                     kb=_result_markup(FOREST_TOKEN.get(user_id, "")))
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
    if not FOREST_BATTLE.pop(user_id, None):
        await _show_glade(callback, prefix="⏳ Бой с кабаном устарел.\n\n")
        return
    await callback.answer()
    await log_activity(user_id, "forest", "Сбежал от кабана")
    await _show_glade(callback, prefix="🏃 Ты вырвался из чащи — кабан остался позади.\n\n")