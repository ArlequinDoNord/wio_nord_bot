"""Дом Дуэлей — PvP-арена «зона на зону».

Поединок двух пилотов: каждый раунд оба тайно выбирают зону атаки и зону
защиты (Голова / Тело / Руки / Ноги). Раунд резолвится, когда выбор сделали
оба; если защита угадала зону атаки, удар гасится (DUEL_GUARD_REDUCTION).
Дуэль идёт до истощения HP одного из участников; ничья — если оба упали в
одном раунде. За победу +2 рейтинга, за поражение −3, за ничью 0.

Доступ — с пилота первого класса (location:enter:duel_house). Для дуэлей нужна
клубная карта; дуэльные перчатки (отдельный слот снаряжения) дают урон на арене
и в других боях не работают. 15 ОД списываются с обоих при старте боя.
"""

import asyncio

from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from config import (
    DUEL_ZONES, DUEL_ZONE_LABELS, DUEL_ZONE_EMOJI, DUEL_AP_COST,
    DUEL_RATING_WIN, DUEL_RATING_LOSS, DUEL_RATING_DRAW, DUEL_GUARD_REDUCTION,
    DUEL_CLUB_CARD_NAME, DUEL_CLUB_CARD_PRICE, DUEL_ACCESS_TAG,
)
from database.db import (
    get_user, get_item_by_name, add_inventory_item, remove_nordmarks,
    has_duel_club_card, get_user_duel_stats, get_active_duel, get_duel,
    create_duel_challenge, accept_duel, decline_duel, set_duel_zone,
    duel_round_ready, apply_duel_round, finish_duel, apply_duel_result,
    get_duel_opponents, get_duel_rating_top, get_player_duel_gear_damage,
    remove_ap, user_has_status_tag, bump_achievement,
)
from utils.combat_model import pilot_combat_stats, roll_pilot_damage

router = Router()

# Одно сообщение арены на игрока: {user_id: (chat_id, message_id)}.
DUEL_MSG: dict = {}
# Незавершённый выбор атаки (между двумя тапами): {user_id: zone}.
DUEL_PICK: dict = {}
# Сериализация резолва раундов (два callback могут прийти одновременно).
_RESOLVE_LOCK = asyncio.Lock()


# ───────── вспомогательные ─────────

def _grid_kb(callback_prefix: str) -> InlineKeyboardMarkup:
    """Клавиатура выбора зоны 2×2 (компактно)."""
    rows, pair = [], []
    for z in DUEL_ZONES:
        pair.append(InlineKeyboardButton(
            text=f"{DUEL_ZONE_EMOJI[z]} {DUEL_ZONE_LABELS[z]}",
            callback_data=f"{callback_prefix}:{z}"))
        if len(pair) == 2:
            rows.append(pair)
            pair = []
    if pair:
        rows.append(pair)
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def _has_access(user_id: int) -> bool:
    return await user_has_status_tag(user_id, DUEL_ACCESS_TAG)


def _other(duel, uid):
    return duel['opponent_id'] if uid == duel['challenger_id'] else duel['challenger_id']


def _side(duel, uid):
    if uid == duel['challenger_id']:
        return 'challenger'
    if uid == duel['opponent_id']:
        return 'opponent'
    return None


def _hp_bar(cur: int, mx: int, width: int = 12) -> str:
    mx = max(1, mx)
    cur = max(0, min(cur, mx))
    filled = int(round(width * cur / mx))
    return "█" * filled + "░" * (width - filled)


def _pilot_name(user) -> str:
    from bot.handlers.profile import _pilot_name as pn
    return pn(user)


async def _show(callback: CallbackQuery, text: str, kb=None):
    """Отрисовка экрана действующего игрока (редактируем его же сообщение)."""
    uid = callback.from_user.id
    try:
        await callback.message.edit_text(text, reply_markup=kb)
        DUEL_MSG[uid] = (callback.message.chat.id, callback.message.message_id)
    except Exception:
        sent = await callback.message.answer(text, reply_markup=kb)
        DUEL_MSG[uid] = (sent.chat.id, sent.message_id)


async def _push(callback: CallbackQuery, uid: int, text: str, kb=None):
    """Отрисовка экрана другого игрока (редактируем его сообщение, иначе шлём новое)."""
    bot = callback.message.bot
    entry = DUEL_MSG.get(uid)
    if entry:
        try:
            await bot.edit_message_text(entry[0], entry[1], text=text, reply_markup=kb)
            return
        except Exception:
            pass
    try:
        sent = await bot.send_message(uid, text, reply_markup=kb)
        DUEL_MSG[uid] = (sent.chat.id, sent.message_id)
    except Exception:
        pass


async def _ack(callback: CallbackQuery, *a, **kw):
    """Безопасный ответ на callback: повторный answer() Telegram отклоняет,
    а хендлеры арены иногда уточняют его алертом — глотаем ошибку."""
    try:
        await getattr(callback, "answer")(*a, **kw)
    except Exception:
        pass


# ───────── доступ и меню арены ─────────

async def duel_house_menu(callback: CallbackQuery):
    """Вход из города (location:enter:duel_house)."""
    await _ack(callback)
    uid = callback.from_user.id
    if not await _has_access(uid):
        await callback.message.answer(
            "⛔ Дом Дуэлей открыт с «Пилота 1 класса».\n"
            "Подрасти в звании — и добро пожаловать на арену.")
        return
    cur = await get_active_duel(uid)
    if cur:
        if cur['status'] == 'active':
            text, kb = await _battle_view(cur, uid)
            await _show(callback, text, kb)
        else:
            await _render_invite(callback, cur, acting_uid=uid)
        return
    await _render_menu(callback)


async def _render_menu(callback: CallbackQuery):
    uid = callback.from_user.id
    stats = await get_user_duel_stats(uid)
    user = await get_user(uid)
    nm = user['nordmarks'] if user else 0
    has_card = await has_duel_club_card(uid)
    gear = await get_player_duel_gear_damage(uid)

    text = (
        "🥊 ДОМ ДУЭЛЕЙ\n"
        "────────────────\n"
        "Арена чести: поединки один на один «зона на зону».\n\n"
        f"🏅 Рейтинг: {stats['rating']}\n"
        f"🏆 Побед: {stats['wins']}   💀 Поражений: {stats['losses']}\n"
        f"🎫 Клубная карта: {'есть' if has_card else 'нет'}\n"
        f"🥊 Дуэльное снаряжение: {f'+{gear} урона' if gear else 'не надето'}\n"
        f"💰 Кошелёк: {nm} НМ"
    )
    rows = []
    if has_card:
        rows.append([InlineKeyboardButton(text="🎯 Вызвать на дуэль",
                                          callback_data="duel:list")])
    else:
        rows.append([InlineKeyboardButton(
            text=f"🛒 Купить клубную карту ({DUEL_CLUB_CARD_PRICE} НМ)",
            callback_data="duel:card:buy")])
    rows.append([InlineKeyboardButton(text="🏆 Рейтинг арены", callback_data="duel:top"),
                 InlineKeyboardButton(text="❓ Правила", callback_data="duel:help")])
    rows.append([InlineKeyboardButton(text="🔙 В город", callback_data="city:menu")])
    await _show(callback, text, InlineKeyboardMarkup(inline_keyboard=rows))


@router.callback_query(F.data == "duel:menu")
async def duel_menu_cb(callback: CallbackQuery):
    await _ack(callback)
    await _render_menu(callback)


@router.callback_query(F.data == "duel:help")
async def duel_help(callback: CallbackQuery):
    await _ack(callback)
    text = (
        "🥊 ДОМ ДУЭЛЕЙ — ПРАВИЛА\n"
        "────────────────\n"
        "• Каждый раунд оба тайно выбирают зону атаки и зону защиты "
        "(Голова / Тело / Руки / Ноги).\n"
        "• Если защита угадала зону атаки — удар гасится вдвое.\n"
        "• Раунд резолвится, когда выбор сделали оба.\n"
        f"• Старт боя стоит {DUEL_AP_COST} ОД каждому.\n"
        f"• Рейтинг: победа +{DUEL_RATING_WIN}, поражение {DUEL_RATING_LOSS}, "
        f"ничья {DUEL_RATING_DRAW}.\n"
        "• Дуэльные перчатки работают только на арене."
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="duel:menu")]])
    await callback.message.answer(text, reply_markup=kb)


@router.callback_query(F.data == "duel:card:buy")
async def duel_buy_card(callback: CallbackQuery):
    uid = callback.from_user.id
    if not await _has_access(uid):
        await _ack(callback)
        await callback.message.answer("⛔ Клубная карта доступна с «Пилота 1 класса».")
        return
    if await has_duel_club_card(uid):
        await _ack(callback, "У тебя уже есть клубная карта.", show_alert=True)
        return
    item = await get_item_by_name(DUEL_CLUB_CARD_NAME)
    if not item:
        await _ack(callback)
        await callback.message.answer("❌ Товар временно недоступен.")
        return
    user = await get_user(uid)
    price = item['price'] or DUEL_CLUB_CARD_PRICE
    if (user['nordmarks'] or 0) < price:
        await _ack(callback, f"Не хватает НМ (нужно {price}).", show_alert=True)
        return
    await remove_nordmarks(uid, price, "duel_card", "Клубная карта «Дом Дуэлей»")
    await add_inventory_item(uid, item['id'], 1)
    await _ack(callback, "Клубная карта куплена!", show_alert=True)
    await _render_menu(callback)


@router.callback_query(F.data == "duel:list")
async def duel_list(callback: CallbackQuery):
    uid = callback.from_user.id
    if not await has_duel_club_card(uid):
        await _ack(callback, "Нужна клубная карта.", show_alert=True)
        return
    await _ack(callback)
    opponents = await get_duel_opponents(uid)
    rows = [[InlineKeyboardButton(
        text=f"{_pilot_name(o)} · 🏅{o['duel_rating'] or 0}",
        callback_data=f"duel:invite:{o['user_id']}")] for o in opponents]
    if not rows:
        rows.append([InlineKeyboardButton(text="— пока некого вызвать —",
                                          callback_data="noop")])
    rows.append([InlineKeyboardButton(text="🔙 Назад", callback_data="duel:menu")])
    await callback.message.answer(
        "🎯 Кого вызвать на дуэль?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))


@router.callback_query(F.data == "duel:top")
async def duel_top(callback: CallbackQuery):
    await _ack(callback)
    top = await get_duel_rating_top(10)
    lines = ["🏆 РЕЙТИНГ АРЕНЫ", "────────────────"]
    if not top:
        lines.append("Пока никто не сражался.")
    for i, r in enumerate(top, 1):
        u = await get_user(r['user_id'])
        lines.append(f"{i}. {_pilot_name(u)} — {r['duel_rating']} "
                     f"({r['duel_wins']}−{r['duel_losses']})")
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="duel:menu")]])
    await callback.message.answer("\n".join(lines), reply_markup=kb)


# ───────── вызов и старт боя ─────────

@router.callback_query(F.data.startswith("duel:invite:"))
async def duel_invite(callback: CallbackQuery):
    uid = callback.from_user.id
    opp_id = int(callback.data.split(":")[2])
    if opp_id == uid:
        await _ack(callback, "Нельзя вызвать себя.", show_alert=True)
        return
    if not await has_duel_club_card(uid):
        await _ack(callback, "Нужна клубная карта.", show_alert=True)
        return
    if not await _has_access(opp_id):
        await _ack(callback, "Этот пилот ещё не допущен к арене.", show_alert=True)
        return
    opponent = await get_user(opp_id)
    if not opponent:
        await _ack(callback, "Пилот не найден.", show_alert=True)
        return
    if not await has_duel_club_card(opp_id):
        await _ack(callback, "У соперника нет клубной карты.", show_alert=True)
        return

    duel_id = await create_duel_challenge(uid, opp_id)
    if duel_id is None:
        await _ack(callback, "У тебя или соперника уже идёт поединок.",
                              show_alert=True)
        return

    duel = await get_duel(duel_id)
    challenger = await get_user(uid)
    await _push(callback, opp_id, _invite_text(duel, challenger), _invite_kb(duel))
    await _ack(callback, "Вызов брошен!")
    await _render_invite(callback, duel, acting_uid=uid)


def _invite_text(duel, challenger) -> str:
    return (f"⚔️ ТЕБЯ ВЫЗВАЛИ НА ДУЭЛЬ\n────────────────\n"
            f"{_pilot_name(challenger)} вызывает тебя на арену!\n\nРешение за тобой.")


def _invite_kb(duel) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Принять", callback_data=f"duel:accept:{duel['id']}"),
        InlineKeyboardButton(text="❌ Отклонить", callback_data=f"duel:decline:{duel['id']}"),
    ]])


async def _render_invite(callback: CallbackQuery, duel, acting_uid: int):
    if acting_uid == duel['challenger_id']:
        op = await get_user(duel['opponent_id'])
        text = (f"⚔️ ВЫЗОВ БРОШЕН\n────────────────\n"
                f"Ты вызвал: {_pilot_name(op)}.\nЖдём ответа соперника…")
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🚪 Отменить вызов",
                                  callback_data=f"duel:cancel:{duel['id']}")]])
        await _show(callback, text, kb)
    else:
        ch = await get_user(duel['challenger_id'])
        await _show(callback, _invite_text(duel, ch), _invite_kb(duel))


@router.callback_query(F.data.startswith("duel:cancel:"))
async def duel_cancel(callback: CallbackQuery):
    await _ack(callback)
    duel_id = int(callback.data.split(":")[2])
    duel = await get_duel(duel_id)
    uid = callback.from_user.id
    if duel and duel['status'] == 'invited' and uid == duel['challenger_id']:
        await decline_duel(duel_id)
        await _push(callback, duel['opponent_id'], "⚔️ Вызов отменён.", None)
    await _render_menu(callback)


@router.callback_query(F.data.startswith("duel:decline:"))
async def duel_decline(callback: CallbackQuery):
    await _ack(callback)
    duel_id = int(callback.data.split(":")[2])
    duel = await get_duel(duel_id)
    uid = callback.from_user.id
    if duel and duel['status'] == 'invited' and uid == duel['opponent_id']:
        await decline_duel(duel_id)
        await _push(callback, duel['challenger_id'], "❌ Соперник отклонил вызов.", None)
    await _show(callback, "Вызов отклонён.",
                InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 В Дом Дуэлей", callback_data="duel:menu")]]))


@router.callback_query(F.data.startswith("duel:accept:"))
async def duel_accept(callback: CallbackQuery):
    await _ack(callback)
    duel_id = int(callback.data.split(":")[2])
    uid = callback.from_user.id
    duel = await get_duel(duel_id)
    if not duel or duel['status'] != 'invited' or uid != duel['opponent_id']:
        await _show(callback, "Этот вызов уже неактуален.",
                    InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="🔙 В Дом Дуэлей",
                                              callback_data="duel:menu")]]))
        return
    if not await has_duel_club_card(uid):
        await _show(callback, "Нужна клубная карта, чтобы принять вызов.")
        return
    if not await has_duel_club_card(duel['challenger_id']):
        await decline_duel(duel_id)
        await _push(callback, duel['challenger_id'],
                    "⛔ Дуэль не состоялась: у соперника нет клубной карты.", None)
        await _show(callback, "У соперника больше нет клубной карты — вызов отменён.")
        return

    ch = await get_user(duel['challenger_id'])
    op = await get_user(uid)
    if (ch['ap'] or 0) < DUEL_AP_COST:
        await decline_duel(duel_id)
        await _push(callback, duel['challenger_id'],
                    "⛔ Дуэль не состоялась: не хватило ОД.", None)
        await _show(callback, "⛔ Дуэль не состоялась: у соперника не хватило ОД.")
        return
    if (op['ap'] or 0) < DUEL_AP_COST:
        await _show(callback, f"⛔ Для дуэли нужно {DUEL_AP_COST} ОД.")
        return

    ch_max = (await _duel_stats(duel['challenger_id']))['hp_max']
    op_max = (await _duel_stats(uid))['hp_max']
    await remove_ap(duel['challenger_id'], DUEL_AP_COST, "Дуэль на арене")
    await remove_ap(uid, DUEL_AP_COST, "Дуэль на арене")

    if not await accept_duel(duel_id, uid, ch_max, ch_max, op_max, op_max):
        await _show(callback, "Не удалось начать дуэль.")
        return

    duel = await get_duel(duel_id)
    text, kb = await _battle_view(duel, uid)
    await _show(callback, text, kb)
    await _push_battle(callback, duel, duel['challenger_id'])


# ───────── бой ─────────

async def _duel_stats(user_id: int) -> dict:
    """Боевые характеристики для арены: базовый урон по званию + дуэльное
    снаряжение (обычное оружие на арене не участвует)."""
    stats = await pilot_combat_stats(user_id)
    stats['weapon_damage'] = await get_player_duel_gear_damage(user_id)
    return stats


async def _battle_view(duel, uid, note: str = None):
    """Текст и клавиатура боя для конкретного игрока."""
    side = _side(duel, uid)
    if side is None:
        return "Это не твоя дуэль.", None
    opp_side = 'opponent' if side == 'challenger' else 'challenger'
    me = await get_user(uid)
    opp = await get_user(_other(duel, uid))
    my_hp, my_max = duel[f'{side}_hp'], duel[f'{side}_hp_max']
    op_hp, op_max = duel[f'{opp_side}_hp'], duel[f'{opp_side}_hp_max']

    text = (
        f"⚔️ ДОМ ДУЭЛЕЙ — РАУНД {duel['turn']}\n"
        "────────────────\n"
        f"🎯 {_pilot_name(me)}  {_hp_bar(my_hp, my_max)} {my_hp}/{my_max}\n"
        f"🥊 {_pilot_name(opp)}  {_hp_bar(op_hp, op_max)} {op_hp}/{op_max}"
    )
    if note:
        text += f"\n\n{note}"
    if duel[f'{side}_atk']:
        atk = duel[f'{side}_atk']
        default = duel[f'{side}_def']
        text += (f"\n\n✅ Ты выбрал: {DUEL_ZONE_EMOJI[atk]} {DUEL_ZONE_LABELS[atk]} "
                 f"(атака), {DUEL_ZONE_LABELS[default]} (защита).\nЖдём соперника…")
        return text, None
    text += "\n\nКуда бьёшь?"
    return text, _grid_kb(f"duel:atk:{duel['id']}")


async def _push_battle(callback: CallbackQuery, duel, target_uid: int, note: str = None):
    text, kb = await _battle_view(duel, target_uid, note=note)
    await _push(callback, target_uid, text, kb)


@router.callback_query(F.data.startswith("duel:atk:"))
async def duel_choose_atk(callback: CallbackQuery):
    await _ack(callback)
    _, _, duel_id, zone = callback.data.split(":")
    uid = callback.from_user.id
    duel = await get_duel(int(duel_id))
    if not duel or duel['status'] != 'active':
        await _show(callback, "Дуэль уже завершена.")
        return
    DUEL_PICK[uid] = zone
    text = (f"🎯 Бьёшь в: {DUEL_ZONE_EMOJI[zone]} {DUEL_ZONE_LABELS[zone]}.\n"
            f"Теперь выбери, что защищаешь:")
    await _show(callback, text, _grid_kb(f"duel:def:{duel_id}:{zone}"))


@router.callback_query(F.data.startswith("duel:def:"))
async def duel_choose_def(callback: CallbackQuery):
    await _ack(callback)
    _, _, duel_id, atk, zone = callback.data.split(":")
    uid = callback.from_user.id
    duel = await get_duel(int(duel_id))
    if not duel or duel['status'] != 'active' or uid not in (
            duel['challenger_id'], duel['opponent_id']):
        await _show(callback, "Дуэль уже завершена.")
        return
    DUEL_PICK.pop(uid, None)
    await set_duel_zone(int(duel_id), uid, atk, zone)

    row = await get_duel(int(duel_id))
    if not duel_round_ready(row):
        text, kb = await _battle_view(row, uid)
        await _show(callback, text, kb)
        await _push_battle(callback, row, _other(row, uid),
                           note="🔔 Соперник сделал свой выбор.")
        return

    async with _RESOLVE_LOCK:
        row = await get_duel(int(duel_id))
        if row['status'] != 'active':
            return
        if not duel_round_ready(row):
            text, kb = await _battle_view(row, uid)
            await _show(callback, text, kb)
            return
        await _resolve_round(callback, row)


async def _resolve_round(callback: CallbackQuery, duel):
    ch_stats = await _duel_stats(duel['challenger_id'])
    op_stats = await _duel_stats(duel['opponent_id'])
    ch_target = {'armor': ch_stats['armor'], 'dodge': ch_stats['dodge']}
    op_target = {'armor': op_stats['armor'], 'dodge': op_stats['dodge']}

    strike_ch = roll_pilot_damage(ch_stats, op_target)   # удар challenger
    strike_ch['guarded'] = duel['challenger_atk'] == duel['opponent_def']
    if strike_ch['guarded']:
        strike_ch['damage'] = int(round(strike_ch['damage'] * DUEL_GUARD_REDUCTION))
    strike_op = roll_pilot_damage(op_stats, ch_target)   # удар opponent
    strike_op['guarded'] = duel['opponent_atk'] == duel['challenger_def']
    if strike_op['guarded']:
        strike_op['damage'] = int(round(strike_op['damage'] * DUEL_GUARD_REDUCTION))

    op_hp = max(0, duel['opponent_hp'] - strike_ch['damage'])
    ch_hp = max(0, duel['challenger_hp'] - strike_op['damage'])

    if ch_hp <= 0 or op_hp <= 0:
        await _finish_battle(callback, duel, ch_hp, op_hp)
        return

    turn = duel['turn'] + 1
    await apply_duel_round(duel['id'], ch_hp, op_hp, turn)
    row = await get_duel(duel['id'])
    text_ch, kb_ch = await _battle_view(
        row, duel['challenger_id'], note=_round_log(duel, strike_ch, strike_op, True))
    text_op, kb_op = await _battle_view(
        row, duel['opponent_id'], note=_round_log(duel, strike_ch, strike_op, False))
    await _push(callback, duel['challenger_id'], text_ch, kb_ch)
    await _push(callback, duel['opponent_id'], text_op, kb_op)


def _strike_log(strike, zone_label) -> str:
    if strike.get('dodged'):
        return f"🎯 Удар в {zone_label}: соперник уклонился"
    line = f"🎯 Удар в {zone_label}: −{strike['damage']} HP"
    if strike.get('guarded'):
        line += " (парировано)"
    if strike.get('crit'):
        line = "💥 КРИТ! " + line
    return line


def _round_log(duel, strike_ch, strike_op, as_challenger: bool) -> str:
    if as_challenger:
        mine, theirs = strike_ch, strike_op
        my_zone = DUEL_ZONE_LABELS[duel['challenger_atk']]
        their_zone = DUEL_ZONE_LABELS[duel['opponent_atk']]
    else:
        mine, theirs = strike_op, strike_ch
        my_zone = DUEL_ZONE_LABELS[duel['opponent_atk']]
        their_zone = DUEL_ZONE_LABELS[duel['challenger_atk']]
    return (f"— Раунд {duel['turn']} —\n"
            + _strike_log(mine, my_zone) + "\n"
            + "🛡 " + _strike_log(theirs, their_zone))


async def _finish_battle(callback: CallbackQuery, duel, ch_hp: int, op_hp: int):
    if ch_hp <= 0 and op_hp <= 0:
        winner, result_ch, result_op, delta_ch, delta_op = (
            None, 'draw', 'draw', DUEL_RATING_DRAW, DUEL_RATING_DRAW)
    elif op_hp <= 0:
        winner, result_ch, result_op, delta_ch, delta_op = (
            duel['challenger_id'], 'win', 'loss', DUEL_RATING_WIN, DUEL_RATING_LOSS)
    else:
        winner, result_ch, result_op, delta_ch, delta_op = (
            duel['opponent_id'], 'loss', 'win', DUEL_RATING_LOSS, DUEL_RATING_WIN)

    await finish_duel(duel['id'], winner, DUEL_RATING_WIN if winner else 0)
    await apply_duel_result(duel['challenger_id'], delta_ch, result_ch)
    await apply_duel_result(duel['opponent_id'], delta_op, result_op)
    if winner:
        try:
            await bump_achievement(winner, 'duels')
        except Exception:
            pass

    ch = await get_user(duel['challenger_id'])
    op = await get_user(duel['opponent_id'])
    if winner is None:
        header = "🤝 НИЧЬЯ"
        note = "Рейтинг не изменился."
    else:
        wname = _pilot_name(ch if winner == duel['challenger_id'] else op)
        header = "🏆 ПОБЕДА"
        note = f"Победитель: {wname}. +{DUEL_RATING_WIN} / {DUEL_RATING_LOSS} рейтинга."

    def verdict(uid):
        if winner is None:
            return "🤝 Ничья."
        return "🏆 Ты победил!" if winner == uid else "💀 Ты проиграл."

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔁 В Дом Дуэлей", callback_data="duel:menu")]])
    await _push(callback, duel['challenger_id'],
                f"{header}\n────────────────\n{verdict(duel['challenger_id'])}\n{note}", kb)
    await _push(callback, duel['opponent_id'],
                f"{header}\n────────────────\n{verdict(duel['opponent_id'])}\n{note}", kb)
    DUEL_PICK.pop(duel['challenger_id'], None)
    DUEL_PICK.pop(duel['opponent_id'], None)
