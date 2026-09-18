"""Инвентарь: просмотр, использование расходников, продажа и передача предметов."""

import time

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.db import (
    get_inventory, get_item, process_item_use, remove_inventory_item,
    add_nordmarks, get_user, get_inventory_item, get_inventory_expiry, get_all_users,
    add_inventory_item, update_item, get_db,
    get_equipment, set_equipment_slot, clear_equipment_slot, log_activity,
    get_fish_catches, take_fish_catch, sell_one_fish_catch, get_active_run,
    process_food_expiry, add_fish_offer, RAW_FISH_SHELF_SEC,
    get_market_slots_info,
    item_fits_slot, ARMOR_SLOTS, EQUIPMENT_SLOT_LABELS, EQUIPMENT_LOCKED_SLOTS,
)
from utils.helpers import (
    rarity_emoji, rarity_label, plural_nordmark, is_main_menu_text,
    item_local_photo, fish_weight_tier, fish_sell_price, edit_or_replace,
    row_get,
)
from keyboards.keyboards import cancel_keyboard, main_menu_kb

router = Router()


class TransferItem(StatesGroup):
    target = State()
    amount = State()
    message = State()


async def find_user(text: str):
    text = text.strip().lstrip("@")
    if text.isdigit():
        return await get_user(int(text))
    users = await get_all_users()
    for u in users:
        if u['username'] and u['username'].lower() == text.lower():
            return u
    return None


def _fish_groups(catches):
    """Уловы рыбы, сгруппированные по (предмет, вес) с подсчётом."""
    from collections import OrderedDict
    groups = OrderedDict()
    for c in catches:
        key = (c['item_id'], c['weight'])
        if key not in groups:
            groups[key] = {"count": 0, "name": c['name'], "rarity": c['rarity']}
        groups[key]["count"] += 1
    return groups


# Порядок категорий в подменю инвентаря (как каталог магазина)
INV_CATEGORIES = [
    "weapon", "equipment", "consumable", "resource", "seeds",
    "fishing", "housing", "furniture", "special", "souvenirs",
    "library_card", "building",
]
FISH_ALL_KEY = "__fish__"

# Расходники, которые нельзя «употребить» из меню предмета (ингредиенты).
NOT_EDIBLE_ITEMS = {"Соль"}


def inv_categories_markup(items, catches):
    """Подменю категорий: сколько предметов в каждой + улов."""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    from utils.helpers import category_label
    counts = {}
    for it in items:
        counts[it['category']] = counts.get(it['category'], 0) + (it['quantity'] or 1)
    fish_total = sum(g["count"] for g in _fish_groups(catches or []).values())
    if fish_total > 0:
        counts[FISH_ALL_KEY] = fish_total

    rows = []
    rows.append([InlineKeyboardButton(text="🛡️ Снаряжение", callback_data="inventory:eq")])
    for cat in INV_CATEGORIES:
        if cat not in counts or counts[cat] <= 0:
            continue
        label = category_label(cat)
        emoji = {"weapon": "⚔️", "equipment": "👕", "consumable": "🧪",
                 "resource": "⛏️", "seeds": "🌱", "fishing": "🎣",
                 "housing": "🏠", "furniture": "🪑", "special": "💎",
                 "souvenirs": "🏺", "library_card": "📚", "building": "🏗️"}.get(cat, "📦")
        rows.append([InlineKeyboardButton(
            text=f"{emoji} {label} — {counts[cat]}",
            callback_data=f"inventory:cat:{cat}")])
    if FISH_ALL_KEY in counts:
        rows.append([InlineKeyboardButton(
            text=f"🐟 Улов — {counts[FISH_ALL_KEY]}",
            callback_data=f"inventory:cat:{FISH_ALL_KEY}")])
    rows.append([InlineKeyboardButton(text="🔙 В меню", callback_data="back:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def inv_list_markup(items, catches=None, back_cb: str = "back:main", back_label: str = "🔙 В меню"):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    buttons = []
    for it in items:
        emoji = rarity_emoji(it['rarity'])
        buttons.append([InlineKeyboardButton(
            text=f"{emoji} {it['name']} x{it['quantity']}",
            callback_data=f"invitem:{it['id']}"
        )])
    for key, g in _fish_groups(catches or []).items():
        item_id, weight = key
        tier = fish_weight_tier(weight)
        emoji = rarity_emoji(g['rarity'])
        buttons.append([InlineKeyboardButton(
            text=f"{emoji} {g['name']} — {tier['label']} x{g['count']}",
            callback_data=f"fishcatch:{item_id}:{weight}"
        )])
    buttons.append([InlineKeyboardButton(text=back_label, callback_data=back_cb)])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def inv_item_markup(item_id: int, category: str, can_use: bool = False, is_equipped: bool = False,
                    equip_slot: str = None, potion_slots: list = None, sellable: bool = True,
                    qty: int = 1, occupied: dict = None):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    buttons = []
    if can_use:
        buttons.append([InlineKeyboardButton(text="✅ Использовать", callback_data=f"inv_use:{item_id}")])
    if category == 'consumable' and potion_slots is not None:
        occupied = occupied or {}
        slot_row = []
        if 1 in potion_slots:
            slot_row.append(InlineKeyboardButton(text="⚗️ Слот 1 ✓", callback_data=f"inv_unslot:potion1"))
        else:
            occ = occupied.get('potion1')
            label = f"⚗️ В слот 1 (замен. «{occ}»)" if occ else "⚗️ В слот 1"
            slot_row.append(InlineKeyboardButton(text=label, callback_data=f"inv_slot:{item_id}:1"))
        if 2 in potion_slots:
            slot_row.append(InlineKeyboardButton(text="⚗️ Слот 2 ✓", callback_data=f"inv_unslot:potion2"))
        else:
            occ = occupied.get('potion2')
            label = f"⚗️ В слот 2 (замен. «{occ}»)" if occ else "⚗️ В слот 2"
            slot_row.append(InlineKeyboardButton(text=label, callback_data=f"inv_slot:{item_id}:2"))
        buttons.append(slot_row)
    if equip_slot:
        if is_equipped:
            buttons.append([InlineKeyboardButton(text="✖️ Снять с себя", callback_data=f"inv_unequip:{item_id}")])
        else:
            buttons.append([InlineKeyboardButton(text="⚔️ Экипировать", callback_data=f"inv_equip:{item_id}")])
    if sellable:
        if qty > 1:
            buttons.append([
                InlineKeyboardButton(text="💵 Продать 1", callback_data=f"inv_sell:{item_id}"),
                InlineKeyboardButton(text=f"💵 Продать всё ({qty})", callback_data=f"inv_sellall:{item_id}"),
            ])
        else:
            buttons.append([InlineKeyboardButton(text="💵 Продать", callback_data=f"inv_sell:{item_id}")])
    buttons.append([InlineKeyboardButton(text="📤 Передать", callback_data=f"inv_transfer:{item_id}")])
    buttons.append([InlineKeyboardButton(text="🔙 В категорию", callback_data=f"inventory:cat:{category}")])
    buttons.append([InlineKeyboardButton(text="🔙 К списку категорий", callback_data="inventory:list")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ── Снаряжение: вкладка со слотами и списком подходящего из инвентаря ──

_ARMOR_SLOT_EMOJI = {"head": "🪖", "body": "🦺", "hands": "🧤", "legs": "🥾"}


def _slot_emoji(slot: str) -> str:
    if slot == 'weapon':
        return '⚔️'
    if slot in _ARMOR_SLOT_EMOJI:
        return _ARMOR_SLOT_EMOJI[slot]
    return '⚗️'


def _slot_extra(item, slot: str) -> str:
    if slot == 'weapon' and item['damage']:
        return f" ({item['damage']} ур.)"
    if slot in ARMOR_SLOTS and item['armor']:
        return f" ({item['armor']} защ.)"
    return ""


async def _equipment_view(user_id: int):
    """Текст и клавиатура вкладки «Снаряжение»."""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    eq = await get_equipment(user_id)
    equipped = {}
    for slot, item_id in eq.items():
        if slot not in EQUIPMENT_SLOT_LABELS:
            continue
        it = await get_item(item_id)
        if it:
            equipped[slot] = it

    def slot_line(slot):
        it = equipped.get(slot)
        emoji = _slot_emoji(slot)
        label = EQUIPMENT_SLOT_LABELS[slot]
        if not it:
            return f"{emoji} {label}: —"
        return f"{emoji} {label}: {it['name']}{_slot_extra(it, slot)}"

    def slot_button(slot):
        it = equipped.get(slot)
        emoji = _slot_emoji(slot)
        label = EQUIPMENT_SLOT_LABELS[slot]
        if not it:
            return f"{emoji} {label}: —"
        return f"{emoji} {label}: {it['name']}{_slot_extra(it, slot)}"

    lines = ["🛡️ СНАРЯЖЕНИЕ", "", "Нажми на слот — покажу подходящее из инвентаря."]
    lines += ["", "▫️ ⚔️ ОРУЖИЕ"]
    lines.append("• " + slot_line('weapon'))
    if 'weapon_aux' in EQUIPMENT_LOCKED_SLOTS:
        lines.append("• 🔒 Вспомогательное: заблокировано")
    lines += ["", "▫️ 🛡️ ЗАЩИТА"]
    for s in ARMOR_SLOTS:
        lines.append("• " + slot_line(s))
    lines += ["", "▫️ 🧪 РАСХОДНИКИ"]
    for s in ('potion1', 'potion2'):
        lines.append("• " + slot_line(s))
    if 'potion3' in EQUIPMENT_LOCKED_SLOTS:
        lines.append("• 🔒 Слот 3: заблокирован")

    rows = []
    rows.append([InlineKeyboardButton(text=slot_button('weapon'),
                                      callback_data=f"eqslot:weapon")])
    rows.append([InlineKeyboardButton(text="🔒 Вспомогательное оружие — заблокировано",
                                      callback_data="eqlock:weapon_aux")])
    for s in ARMOR_SLOTS:
        rows.append([InlineKeyboardButton(text=slot_button(s),
                                          callback_data=f"eqslot:{s}")])
    for s in ('potion1', 'potion2'):
        rows.append([InlineKeyboardButton(text=slot_button(s),
                                          callback_data=f"eqslot:{s}")])
    rows.append([InlineKeyboardButton(text="🔒 Слот 3 — заблокирован",
                                      callback_data="eqlock:potion3")])
    rows.append([InlineKeyboardButton(text="🔙 К категориям", callback_data="inventory:list")])
    return "\n".join(lines), InlineKeyboardMarkup(inline_keyboard=rows)


async def _render_equipment(message, user_id: int):
    text, markup = await _equipment_view(user_id)
    await edit_or_replace(message, text, markup)


async def _render_equip_slot(message, user_id: int, slot: str):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    label = EQUIPMENT_SLOT_LABELS.get(slot, slot)
    eq = await get_equipment(user_id)
    equipped_id = eq.get(slot)
    equipped = await get_item(equipped_id) if equipped_id else None
    items = await get_inventory(user_id)
    candidates = [it for it in items if item_fits_slot(it, slot)]

    text = f"🛡️ СНАРЯЖЕНИЕ → {label}"
    text += f" {_slot_emoji(slot)}\n\n"
    if equipped:
        text += (f"Надето: {equipped['name']}{_slot_extra(equipped, slot)}\n")
    else:
        text += "Слот пуст.\n"
    if candidates:
        text += "\nПодходит из инвентаря:"
    else:
        text += "\nВ инвентаре нет подходящих предметов."

    rows = []
    if equipped:
        rows.append([InlineKeyboardButton(text="✖️ Снять с себя",
                                          callback_data=f"equnequip:{slot}")])
    for it in candidates:
        marker = "✅ " if it['id'] == equipped_id else ""
        rows.append([InlineKeyboardButton(
            text=f"{marker}{it['name']} x{it['quantity']}",
            callback_data=f"eqequip:{slot}:{it['id']}")])
    rows.append([InlineKeyboardButton(text="🔙 К снаряжению",
                                      callback_data="inventory:eq")])
    await edit_or_replace(message, text, InlineKeyboardMarkup(inline_keyboard=rows))


@router.callback_query(F.data == "inventory:eq")
async def inventory_eq_cb(callback: CallbackQuery):
    await callback.answer()
    await _render_equipment(callback.message, callback.from_user.id)


@router.callback_query(F.data.regexp(r"^eqlock:[a-z0-9_]+$"))
async def equip_slot_locked_cb(callback: CallbackQuery):
    await callback.answer("Слот заблокирован — откроется позже.", show_alert=True)


@router.callback_query(F.data.regexp(r"^eqslot:[a-z0-9_]+$"))
async def equip_slot_cb(callback: CallbackQuery):
    await callback.answer()
    slot = callback.data.split(":", 1)[1]
    await _render_equip_slot(callback.message, callback.from_user.id, slot)


@router.callback_query(F.data.regexp(r"^eqequip:[a-z0-9_]+:\d+$"))
async def equip_from_slot_cb(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    if await get_active_run(user_id):
        await callback.message.answer("⏳ Идёт забег в подземелье: менять снаряжение в бою нельзя.")
        return
    _, slot, item_id_s = callback.data.split(":")
    item_id = int(item_id_s)
    item = await get_item(item_id)
    inv = await get_inventory_item(user_id, item_id)
    if not item or not inv or inv['quantity'] < 1:
        await callback.message.answer("❌ У тебя нет этого предмета.")
        return
    if not item_fits_slot(item, slot):
        await callback.message.answer("❌ Этот предмет не подходит в этот слот.")
        return
    eq = await get_equipment(user_id)
    replaced = eq.get(slot)
    await set_equipment_slot(user_id, slot, item_id)
    note = ""
    if replaced and replaced != item_id:
        old = await get_item(replaced)
        note = f" (было заменено: «{old['name'] if old else replaced}»)"
    await log_activity(user_id, "equip",
                       f"Надел «{item['name']}» в слот «{EQUIPMENT_SLOT_LABELS[slot]}»")
    await callback.message.answer(
        f"✅ Надето: {item['name']} — {EQUIPMENT_SLOT_LABELS[slot]}.{note}"
    )
    await _render_equip_slot(callback.message, user_id, slot)


@router.callback_query(F.data.regexp(r"^equnequip:[a-z0-9_]+$"))
async def unequip_slot_cb(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    if await get_active_run(user_id):
        await callback.message.answer("⏳ Идёт забег в подземелье: менять снаряжение в бою нельзя.")
        return
    slot = callback.data.split(":", 1)[1]
    eq = await get_equipment(user_id)
    item_id = eq.get(slot)
    if not item_id:
        await callback.message.answer("Этот слот пуст.")
        return
    item = await get_item(item_id)
    await clear_equipment_slot(user_id, slot)
    await log_activity(user_id, "unequip",
                       f"Снял «{item['name'] if item else item_id}» со слота «{EQUIPMENT_SLOT_LABELS.get(slot, slot)}»")
    await callback.message.answer(f"✖️ Снято: {item['name'] if item else 'предмет'}")
    await _render_equip_slot(callback.message, user_id, slot)


@router.message(F.text == "Инвентарь")
async def inventory_menu(message: Message):
    spoiled = await process_food_expiry(message.from_user.id)
    items = await get_inventory(message.from_user.id)
    catches = await get_fish_catches(message.from_user.id)
    if not items and not catches:
        await message.answer("Твой инвентарь пуст.")
        return
    header = "🎒 ИНВЕНТАРЬ\n\nВыбери категорию:"
    if spoiled:
        header = f"🥀 Часть провизии испортилась: {spoiled} шт. обращено.\n\n" + header
    run = await get_active_run(message.from_user.id)
    if run:
        header = ("🎒 ИНВЕНТАРЬ\n"
                  "⏳ Идёт забег в подземелье: вернуться в бой можно "
                  "старыми кнопками «Атаковать/Продолжить» в чате.\n\n"
                  "Выбери категорию:")
    await message.answer(header, reply_markup=inv_categories_markup(items, catches))


@router.callback_query(F.data == "inventory:list")
async def inventory_list_cb(callback: CallbackQuery):
    await callback.answer()
    spoiled = await process_food_expiry(callback.from_user.id)
    items = await get_inventory(callback.from_user.id)
    catches = await get_fish_catches(callback.from_user.id)
    if not items and not catches:
        await edit_or_replace(callback.message, "Твой инвентарь пуст.", None)
        return
    header = "🎒 ИНВЕНТАРЬ\n\nВыбери категорию:"
    if spoiled:
        header = f"🥀 Часть провизии испортилась: {spoiled} шт. обращено.\n\n" + header
    await edit_or_replace(
        callback.message,
        header,
        inv_categories_markup(items, catches)
    )


@router.callback_query(F.data.regexp(r"^inventory:cat:[^:]+$"))
async def inventory_cat_cb(callback: CallbackQuery):
    await callback.answer()
    cat = callback.data.split(":", 2)[2]
    user_id = callback.from_user.id
    items = await get_inventory(user_id)
    catches = await get_fish_catches(user_id)
    if cat != FISH_ALL_KEY:
        items = [i for i in items if i['category'] == cat]
        catches = []
    else:
        items = []
    if not items and not catches:
        await edit_or_replace(callback.message, "В этой категории нет предметов.", None)
        return
    header = "🎒 ИНВЕНТАРЬ"
    if cat == FISH_ALL_KEY:
        header += "\nУлов:"
    else:
        from utils.helpers import category_label
        header += f"\n{category_label(cat)}:"
    await edit_or_replace(callback.message, header,
                          inv_list_markup(items, catches,
                                          back_cb="inventory:list",
                                          back_label="🔙 К категориям"))


async def _render_item_card(message, user_id: int, item_id: int, note: str = ""):
    """Перерисовывает карточку предмета в указанном сообщении (edit или replace).

    note — строка об операции (например, чек продажи), показывается сверху карточки.
    """
    item = await get_item(item_id)
    inv = await get_inventory_item(user_id, item_id)
    if not item or not inv:
        await edit_or_replace(message, "Предмет не найден.", None)
        return

    eq = await get_equipment(user_id)
    in_run = bool(await get_active_run(user_id))

    text = (
        f"{rarity_emoji(item['rarity'])} {item['name']} {rarity_emoji(item['rarity'])}\n"
        f"Редкость: {rarity_label(item['rarity'])}\n"
        f"В наличии: {inv['quantity']} шт.\n\n"
    )
    dots = []
    if item['category'] == 'weapon':
        dots.append(f"⚔️ Урон: {item['damage']}")
    if item['category'] == 'equipment' and item['armor']:
        dots.append(f"🛡️ Защита: {item['armor']}")
    if item['heal']:
        dots.append(f"💚 Лечение: {item['heal']}")
    if dots:
        text += " • ".join(dots) + "\n\n"
    if item['heal']:
        text += "💊 Применяется в бою подземелья: поставь в слот 1/2 (кнопки ниже) и жми в бою.\n\n"
    if item['description']:
        text += f"📝 {item['description']}\n\n"

    # Срок годности (жареная рыба)
    exp = await get_inventory_expiry(user_id, item_id)
    if exp:
        try:
            remaining = float(exp) - time.time()
            if remaining > 0:
                text += f"⏳ Срок годности: ~{remaining/86400:.1f} сут\n"
            else:
                text += "🥀 Провизия испортилась…\n"
        except (TypeError, ValueError):
            pass

    text += f"💵 Продажа: {item['sell_price']} {plural_nordmark(item['sell_price'])}"

    # Определяем слот снаряжения и статус экипировки
    equip_slot = None
    if item['category'] == 'weapon':
        equip_slot = 'weapon'
    elif item['category'] == 'equipment' and item['armor']:
        equip_slot = item['equip_slot'] if ('equip_slot' in item.keys() and item['equip_slot']) else 'body'
    is_equipped = eq.get(equip_slot) == item_id if equip_slot else False
    if is_equipped:
        text += f"\n\n🔹 Экипировано: {_slot_emoji(equip_slot)} {EQUIPMENT_SLOT_LABELS.get(equip_slot, equip_slot)}"

    # Активные слоты зелий (potion1/potion2) — в каких стоит этот предмет
    potion_slots = [n for n, slot in ((1, 'potion1'), (2, 'potion2')) if eq.get(slot) == item_id]
    if potion_slots:
        text += f"\n\n⚗️ В активном слоте: {', '.join(str(n) for n in potion_slots)}"

    # Сколько экземпляров занято активными слотами — их продать нельзя, пока не снято
    used_slots = [s for s in EQUIPMENT_SLOT_LABELS if eq.get(s) == item_id]
    inventory_qty = inv['quantity'] or 0
    sellable_qty = max(0, inventory_qty - len(used_slots)) if used_slots else inventory_qty
    if used_slots:
        if sellable_qty > 0:
            text += (f"\n\n⚠️ {len(used_slots)} шт. занято слотами — "
                     f"продать можно не больше {sellable_qty} шт.")
        else:
            text += f"\n\n⚠️ Все {inventory_qty} шт. занято слотами — сними, чтобы продать."

    if note:
        text = f"{note}\n\n{text}"

    # Кто сейчас занимает слоты (для честной замены — без сюрпризов)
    occupied = {}
    if item['category'] == 'consumable':
        for n, slot in ((1, 'potion1'), (2, 'potion2')):
            occ_id = eq.get(slot)
            if occ_id and occ_id != item_id:
                occ_item = await get_item(occ_id)
                occupied[slot] = occ_item['name'] if occ_item else f"#{occ_id}"

    can_use = (
        item['category'] == "consumable"
        and item['name'] not in NOT_EDIBLE_ITEMS
        and (not (item['heal'] or 0) or bool(row_get(item, 'drink_effect')))
    )
    if in_run:
        can_use = False
        equip_slot = None
        potion_slots = []
        occupied = {}
    markup = inv_item_markup(item_id, item['category'], can_use=can_use,
                             is_equipped=is_equipped, equip_slot=equip_slot,
                             potion_slots=potion_slots,
                             sellable=(item['sell_price'] or 0) > 0 and sellable_qty > 0,
                             qty=sellable_qty,
                             occupied=occupied)

    photo_id = item['photo_file_id'] if 'photo_file_id' in item.keys() else None
    local_photo = None if photo_id else item_local_photo(item['name'])
    if photo_id or local_photo:
        media = photo_id or FSInputFile(local_photo)
        from aiogram.types import InputMediaPhoto
        try:
            if message.photo:
                await message.edit_media(
                    media=InputMediaPhoto(media=media, caption=text),
                    reply_markup=markup
                )
            else:
                await message.delete()
                await message.answer_photo(photo=media, caption=text, reply_markup=markup)
        except Exception:
            await message.answer_photo(photo=media, caption=text, reply_markup=markup)
    else:
        await message.edit_text(text, reply_markup=markup)


@router.callback_query(F.data.startswith("invitem:"))
async def inv_item_view(callback: CallbackQuery):
    await callback.answer()
    item_id = int(callback.data.split(":")[1])
    await _render_item_card(callback.message, callback.from_user.id, item_id)


@router.callback_query(F.data.startswith("inv_equip:"))
async def inv_equip(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    run = await get_active_run(user_id)
    if run:
        await callback.message.answer("⏳ Идёт забег в подземелье: менять оружие и броню в бою нельзя.")
        return
    item_id = int(callback.data.split(":")[1])
    item = await get_item(item_id)
    inv = await get_inventory_item(user_id, item_id)
    if not item or not inv or inv['quantity'] < 1:
        await callback.message.answer("❌ У тебя нет этого предмета.")
        return

    if item['category'] == 'weapon':
        slot = 'weapon'
    elif item['category'] == 'equipment' and item['armor']:
        slot = item['equip_slot'] if ('equip_slot' in item.keys() and item['equip_slot']) else 'body'
    else:
        await callback.message.answer("❌ Этот предмет нельзя экипировать.")
        return

    await set_equipment_slot(user_id, slot, item_id)
    await callback.message.answer(
        f"✅ Экипировано: {item['name']} — {EQUIPMENT_SLOT_LABELS.get(slot, slot)}"
    )
    await _render_item_card(callback.message, user_id, item_id)


@router.callback_query(F.data.startswith("inv_unequip:"))
async def inv_unequip(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    run = await get_active_run(user_id)
    if run:
        await callback.message.answer("⏳ Идёт забег в подземелье: менять оружие и броню в бою нельзя.")
        return
    item_id = int(callback.data.split(":")[1])
    item = await get_item(item_id)
    if not item:
        return

    eq = await get_equipment(user_id)
    slot = next((s for s in ("weapon", "head", "body", "hands", "legs",
                             "potion1", "potion2") if eq.get(s) == item_id), None)
    if not slot:
        await callback.message.answer("❌ Этот предмет сейчас не надет.")
        return
    await clear_equipment_slot(user_id, slot)
    await callback.message.answer(f"✖️ Снято: {item['name']}")
    await _render_item_card(callback.message, user_id, item_id)


@router.callback_query(F.data.startswith("inv_slot:"))
async def inv_potion_slot(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    run = await get_active_run(user_id)
    if run:
        await callback.message.answer("⏳ Идёт забег в подземелье: менять активные слоты нельзя. "
                                      "Заготовь слоты до входа или в новом забеге.")
        return
    _, item_id_s, slot_n = callback.data.split(":")
    item_id = int(item_id_s)
    item = await get_item(item_id)
    inv = await get_inventory_item(user_id, item_id)
    if not item or not inv or inv['quantity'] < 1:
        await callback.message.answer("❌ У тебя нет этого предмета.")
        return
    if item['category'] != 'consumable':
        await callback.message.answer("❌ В активный слот можно ставить только расходники (зелья/антидот).")
        return

    slot = f"potion{slot_n}"
    eq = await get_equipment(user_id)
    replaced = eq.get(slot)
    await set_equipment_slot(user_id, slot, item_id)
    note = ""
    if replaced and replaced != item_id:
        old = await get_item(replaced)
        note = f" (было заменено: «{old['name'] if old else replaced}»)"
    await callback.message.answer(
        f"⚗️ {item['name']} поставлен в активный слот {slot_n}.{note}\n"
        f"Используется в бою подземелья кнопкой слота."
    )
    await _render_item_card(callback.message, user_id, item_id)


@router.callback_query(F.data.startswith("inv_unslot:"))
async def inv_potion_unslot(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    run = await get_active_run(user_id)
    if run:
        await callback.message.answer("⏳ Идёт забег в подземелье: менять активные слоты нельзя. "
                                      "Заготовь слоты до входа или в новом забеге.")
        return
    slot = callback.data.split(":", 1)[1]
    eq = await get_equipment(user_id)
    item_id = eq.get(slot)
    if not item_id:
        await callback.message.answer("Этот слот пуст.")
        return
    item = await get_item(item_id)
    await clear_equipment_slot(user_id, slot)
    name = item['name'] if item else "Предмет"
    await callback.message.answer(f"✖️ {name} снят из активного слота.")
    await _render_item_card(callback.message, user_id, item_id)


@router.callback_query(F.data.startswith("inv_use:"))
async def inv_use(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    run = await get_active_run(user_id)
    if run:
        await callback.message.answer("⏳ Идёт забег в подземелье: использовать расходники из инвентаря нельзя. "
                                      "Зелья — только через активные слоты в бою, водоросли/энергетики — после забега.")
        return
    item_id = int(callback.data.split(":")[1])
    ok, msg = await process_item_use(callback.from_user.id, item_id)
    if ok:
        item = await get_item(item_id)
        await log_activity(callback.from_user.id, "item_use",
                           f"Использовал «{item['name']}»" if item else f"item #{item_id}")
    await callback.message.answer(("✅ " if ok else "❌ ") + msg)


@router.callback_query(F.data.startswith("inv_sell:"))
async def inv_sell(callback: CallbackQuery):
    item_id = int(callback.data.split(":")[1])
    inv = await get_inventory_item(callback.from_user.id, item_id)
    if inv and inv['quantity'] > 1:
        await _sell_confirm(callback, item_id, 1)
    else:
        await _sell_item(callback, item_id, 1)


@router.callback_query(F.data.startswith("inv_sellall:"))
async def inv_sellall(callback: CallbackQuery):
    item_id = int(callback.data.split(":")[1])
    inv = await get_inventory_item(callback.from_user.id, item_id)
    if not inv:
        await callback.answer("❌ Такого предмета нет в инвентаре.", show_alert=True)
        return
    await _sell_confirm(callback, item_id, inv['quantity'])


async def _sell_confirm(callback: CallbackQuery, item_id: int, qty: int):
    """Подтверждение продажи: сколько и за сколько, перед списанием."""
    user_id = callback.from_user.id
    item = await get_item(item_id)
    inv = await get_inventory_item(user_id, item_id)
    if not item or not inv or inv['quantity'] < qty:
        await callback.answer(f"❌ У тебя меньше {qty} шт. этого предмета.", show_alert=True)
        return

    # Занятые слотом экземпляры продать нельзя (иначе останется «призрачный слот»);
    # продаются только лишние, сверх надетых/занятых.
    eq = await get_equipment(user_id)
    used_slots = [s for s in EQUIPMENT_SLOT_LABELS if eq.get(s) == item_id]
    if used_slots:
        max_sellable = max(0, inv['quantity'] - len(used_slots))
        if qty > max_sellable:
            used = [EQUIPMENT_SLOT_LABELS[s].lower() for s in used_slots]
            extra = "" if max_sellable > 0 else " Сначала сними его."
            await callback.answer(
                f"❌ «{item['name']}» сейчас используется ({', '.join(used)}). "
                f"Можно продать не больше {max_sellable} шт.{extra}", show_alert=True
            )
            return

    total = item['sell_price'] * qty
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Да, продать", callback_data=f"inv_sell_ok:{item_id}:{qty}")],
        [InlineKeyboardButton(text="↩️ Нет, отмена", callback_data=f"invitem:{item_id}")],
    ])
    await callback.answer()
    await edit_or_replace(
        callback.message,
        f"💵 Продать «{item['name']}» x{qty} за {total} {plural_nordmark(total)}?\n\n"
        f"Предмет будет списан сразу.",
        markup
    )


@router.callback_query(F.data.startswith("inv_sell_ok:"))
async def inv_sell_ok(callback: CallbackQuery):
    await callback.answer()
    _, item_s, qty_s = callback.data.split(":")
    await _sell_item(callback, int(item_s), int(qty_s))


async def _sell_item(callback: CallbackQuery, item_id: int, qty: int):
    user_id = callback.from_user.id
    item = await get_item(item_id)
    inv = await get_inventory_item(user_id, item_id)
    if not item or not inv or inv['quantity'] < qty:
        await callback.answer(f"❌ У тебя меньше {qty} шт. этого предмета.", show_alert=True)
        return

    # Занятые слотом экземпляры продать нельзя (иначе останется «призрачный слот»:
    # урон/защита берутся напрямую из items по id в equipment, без проверки инвентаря).
    eq = await get_equipment(user_id)
    used_slots = [s for s in EQUIPMENT_SLOT_LABELS if eq.get(s) == item_id]
    if used_slots:
        max_sellable = max(0, inv['quantity'] - len(used_slots))
        if qty > max_sellable:
            used = [EQUIPMENT_SLOT_LABELS[s].lower() for s in used_slots]
            extra = "" if max_sellable > 0 else " Сначала сними его."
            await callback.answer(
                f"❌ «{item['name']}» сейчас используется ({', '.join(used)}). "
                f"Можно продать не больше {max_sellable} шт.{extra}", show_alert=True
            )
            return

    await callback.answer()
    await remove_inventory_item(user_id, item_id, qty)
    total = item['sell_price'] * qty
    await add_nordmarks(user_id, total, "shop_sale", f"Продажа: {item['name']} x{qty}")
    await log_activity(user_id, "shop_sale", f"Продал «{item['name']}» x{qty} за {total} НМ")

    # Маркетплейс: товар с ограниченным остатком (не -1 «безлимит») после продажи игроком
    # возвращается в магазин — сколько продали, столько и появилось к покупке.
    if item['stock'] != -1:
        await update_item(item_id, is_available=1)
        db = await get_db()
        await db.execute("UPDATE items SET stock = stock + ? WHERE id = ?", (qty, item_id))
        await db.commit()

    # Чек операции + возврат к карточке предмета с обновлённым количеством,
    # чтобы можно было сразу продать ещё, не заходя в инвентарь заново.
    receipt = f"💵 Ты продал {item['name']} x{qty} за {total} {plural_nordmark(total)}!"
    after = await get_inventory_item(user_id, item_id)
    if after and after['quantity'] > 0:
        await _render_item_card(callback.message, user_id, item_id, note=receipt)
    else:
        await edit_or_replace(callback.message, receipt)


@router.callback_query(F.data.startswith("fishcatch:"))
async def fish_catch_view(callback: CallbackQuery):
    await callback.answer()
    _, item_id_s, weight_s = callback.data.split(":")
    await _show_fish_catch(callback.message, callback.from_user.id,
                           int(item_id_s), int(weight_s))


async def _show_fish_catch(message, user_id: int, item_id: int, weight: int):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    item = await get_item(item_id)
    if not item:
        await edit_or_replace(message, "Рыба не найдена.", None)
        return
    catches = await get_fish_catches(user_id)
    count = sum(1 for c in catches if c['item_id'] == item_id and c['weight'] == weight)
    if count < 1:
        await edit_or_replace(message, "Такой рыбы у тебя больше нет.", None)
        return

    tier = fish_weight_tier(weight)
    sell = fish_sell_price(item['sell_price'], weight)
    sell_text = f"{sell} {plural_nordmark(sell)}"

    remaining = 0
    for c in catches:
        if c['item_id'] == item_id and c['weight'] == weight:
            remaining = c.get('remaining_sec', 0)
            break
    if remaining > 0:
        d, rem = divmod(remaining, 86400)
        h, m = rem // 3600, (rem % 3600) // 60
        if d > 0:
            fresh_line = f"⏳ Свежесть: {d} дн {h} ч"
        else:
            fresh_line = f"⏳ Свежесть: {h} ч {m} мин"
    else:
        fresh_line = "⏳ Свежий улов"

    text = (
        f"{rarity_emoji(item['rarity'])} {item['name']} {rarity_emoji(item['rarity'])}\n"
        f"Редкость: {rarity_label(item['rarity'])}\n\n"
        f"⚖️ Вес: {tier['label']}\n"
        f"В наличии: {count} шт.\n"
        f"{fresh_line}\n\n"
        f"{item['description']}\n\n"
        f"💰 Цена (с учётом веса): {sell_text}"
    )
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏪 На рынок",
                              callback_data=f"fishmarket:{item_id}:{weight}")],
        [InlineKeyboardButton(text=f"💵 Скупщику сразу (за {sell_text})",
                              callback_data=f"fishsell:{item_id}:{weight}")],
        [InlineKeyboardButton(text="🔙 В категорию", callback_data=f"inventory:cat:{FISH_ALL_KEY}")],
        [InlineKeyboardButton(text="🔙 К списку категорий", callback_data="inventory:list")],
    ])

    photo_id = item['photo_file_id'] if 'photo_file_id' in item.keys() else None
    local_photo = None if photo_id else item_local_photo(item['name'])
    if photo_id or local_photo:
        media = photo_id or FSInputFile(local_photo)
        from aiogram.types import InputMediaPhoto
        try:
            if message.photo:
                await message.edit_media(media=InputMediaPhoto(media=media, caption=text),
                                         reply_markup=markup)
            else:
                await message.delete()
                await message.answer_photo(photo=media, caption=text, reply_markup=markup)
        except Exception:
            await message.answer_photo(photo=media, caption=text, reply_markup=markup)
    else:
        await message.edit_text(text, reply_markup=markup)


@router.callback_query(F.data.startswith("fishmarket:"))
async def fish_market_set_price(callback: CallbackQuery):
    """Экран выбора цены ±30% от рыночной для вылова на рынок."""
    await callback.answer()
    user_id = callback.from_user.id
    _, item_id_s, weight_s = callback.data.split(":")
    item_id, weight = int(item_id_s), int(weight_s)
    item = await get_item(item_id)
    if not item:
        return

    catches = await get_fish_catches(user_id)
    catch = next((c for c in catches if c['item_id'] == item_id and c['weight'] == weight), None)
    if not catch:
        await callback.message.answer("❌ Свежего улова уже нет.")
        await _show_fish_catch(callback.message, user_id, item_id, weight)
        return

    base = fish_sell_price(item['sell_price'], weight)
    await _show_price_screen(callback, item, weight, base, base)


def _price_keyboard(item_id: int, weight: int, current: int, base: int):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    min_p = max(1, int(base * 0.7))
    max_p = int(base * 1.3)
    current = max(min_p, min(max_p, current))

    adj_row = []
    p10d = max(min_p, current - max(1, current // 10))
    p1d = max(min_p, current - 1)
    p1i = min(max_p, current + 1)
    p10i = min(max_p, current + max(1, current // 10))
    if p10d < current:
        adj_row.append(InlineKeyboardButton(text="−10", callback_data=f"fishprice:{item_id}:{weight}:{p10d}"))
    if p1d < current and p1d != p10d:
        adj_row.append(InlineKeyboardButton(text="−1", callback_data=f"fishprice:{item_id}:{weight}:{p1d}"))
    if p1i > current:
        adj_row.append(InlineKeyboardButton(text="+1", callback_data=f"fishprice:{item_id}:{weight}:{p1i}"))
    if p10i > current and p10i != p1i:
        adj_row.append(InlineKeyboardButton(text="+10", callback_data=f"fishprice:{item_id}:{weight}:{p10i}"))

    rows = []
    if adj_row:
        rows.append(adj_row)
    rows.append([InlineKeyboardButton(
        text=f"✅ Выставить за {current} НМ",
        callback_data=f"fishgo:{item_id}:{weight}:{current}")])
    rows.append([InlineKeyboardButton(text="🔙 Назад", callback_data=f"fishcatch:{item_id}:{weight}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def _show_price_screen(callback, item, weight, current, base):
    tier = fish_weight_tier(weight)
    min_p = max(1, int(base * 0.7))
    max_p = int(base * 1.3)
    current = max(min_p, min(max_p, current))
    text = (
        f"🏪 ВЫСТАВЛЕНИЕ НА РЫНОК\n\n"
        f"{rarity_emoji(item['rarity'])} {item['name']} {rarity_emoji(item['rarity'])}\n"
        f"⚖️ Вес: {tier['label']}\n\n"
        f"📊 Рыночная цена: {base} НМ\n"
        f"💲 Цена продажи: {current} НМ\n"
        f"📐 Диапазон: {min_p} – {max_p} НМ\n\n"
        f"Выбери цену кнопками или подтверди."
    )
    if current <= min_p:
        text += "\n\n⚠️ Достигнут нижний предел (−30% от рыночной). Ниже выставить нельзя."
    elif current >= max_p:
        text += "\n\n⚠️ Достигнут верхний предел (+30% от рыночной). Выше выставить нельзя."
    kb = _price_keyboard(item['id'], weight, current, base)
    try:
        await callback.message.edit_text(text, reply_markup=kb)
    except Exception:
        await callback.message.answer(text, reply_markup=kb)


@router.callback_query(F.data.startswith("fishprice:"))
async def fish_price_adjust(callback: CallbackQuery):
    await callback.answer()
    _, item_id_s, weight_s, price_s = callback.data.split(":")
    item_id, weight, price = int(item_id_s), int(weight_s), int(price_s)
    user_id = callback.from_user.id
    item = await get_item(item_id)
    if not item:
        return
    catches = await get_fish_catches(user_id)
    catch = next((c for c in catches if c['item_id'] == item_id and c['weight'] == weight), None)
    if not catch:
        await callback.answer("❌ Свежего улова уже нет.", show_alert=True)
        return
    base = fish_sell_price(item['sell_price'], weight)
    await _show_price_screen(callback, item, weight, price, base)


@router.callback_query(F.data.startswith("fishgo:"))
async def fish_market_confirm(callback: CallbackQuery):
    """Подтверждение выкладки на рынок с проверкой слотов."""
    await callback.answer()
    _, item_id_s, weight_s, price_s = callback.data.split(":")
    item_id, weight, price = int(item_id_s), int(weight_s), int(price_s)
    user_id = callback.from_user.id
    item = await get_item(item_id)
    if not item:
        return

    base = fish_sell_price(item['sell_price'], weight)
    min_p = max(1, int(base * 0.7))
    max_p = int(base * 1.3)
    price = max(min_p, min(max_p, price))

    slots = await get_market_slots_info(user_id)
    if slots['active_count'] >= slots['total_slots']:
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        await callback.message.answer(
            f"❌ Нет свободных слотов!\n"
            f"У тебя {slots['active_count']}/{slots['total_slots']} активных объявлений.\n\n"
            f"💡 Купи «Торговую лицензию» в Магазине → «Торговые лицензии» — +2 слота на 30 дней.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🛒 Магазин → Лицензии", callback_data="shopcat:license")],
                [InlineKeyboardButton(text="🔙 Назад", callback_data=f"fishcatch:{item_id}:{weight}")],
            ])
        )
        return

    c = await take_fish_catch(user_id, item_id, weight)
    if not c:
        await callback.message.answer("❌ Свежего улова уже нет.")
        await _show_fish_catch(callback.message, user_id, item_id, weight)
        return

    now = int(time.time())
    exp = c.get('expires_at')
    try:
        expi = int(float(exp)) if exp else None
    except (TypeError, ValueError):
        expi = None
    remaining = max(1, (expi or (now + RAW_FISH_SHELF_SEC)) - now)

    await add_fish_offer(user_id, item_id, weight, price, remaining, base_price=base)
    await log_activity(user_id, "shop_sale",
                       f"Выставил «{item['name']}» на рынок за {price} НМ (база {base})")
    await callback.message.answer(
        f"🏪 «{item['name']}» выставлен на продажу за "
        f"{price} {plural_nordmark(price)}!\n\n"
        f"📊 Рыночная цена: {base} НМ | Твоя: {price} НМ\n"
        f"💰 Нордмарки придут после покупки (за вычетом налога).\n"
        f"⏳ Срок годности заморожен."
    )
    await _show_fish_catch(callback.message, user_id, item_id, weight)


@router.callback_query(F.data.startswith("fishsell:"))
async def fish_sell(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    _, item_id_s, weight_s = callback.data.split(":")
    item_id, weight = int(item_id_s), int(weight_s)
    item = await get_item(item_id)
    if not item:
        return
    ok = await sell_one_fish_catch(user_id, item_id, weight)
    if not ok:
        await callback.message.answer("❌ Такого улова уже нет.")
        return
    sell = fish_sell_price(item['sell_price'], weight)
    await add_nordmarks(user_id, sell, "shop_sale", f"Продажа: {item['name']}")
    await log_activity(user_id, "shop_sale", f"Продал «{item['name']}» за {sell} НМ")
    await callback.message.answer(
        f"💵 Ты продал {item['name']} за {sell} {plural_nordmark(sell)}!"
    )
    # Обновляем карточку (или показываем, что рыбы не осталось)
    await _show_fish_catch(callback.message, user_id, item_id, weight)


@router.callback_query(F.data.startswith("inv_transfer:"))
async def inv_transfer_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    user_id = callback.from_user.id
    item_id = int(callback.data.split(":")[1])
    item = await get_item(item_id)
    inv = await get_inventory_item(user_id, item_id)
    if not item or not inv or inv['quantity'] < 1:
        await callback.message.answer("❌ У тебя нет этого предмета.")
        return

    eq = await get_equipment(user_id)
    if item_id in eq.values():
        used = [EQUIPMENT_SLOT_LABELS[s].lower() for s in EQUIPMENT_SLOT_LABELS if eq.get(s) == item_id]
        await callback.message.answer(
            f"❌ «{item['name']}» сейчас используется ({', '.join(used)}). "
            f"Сначала сними его."
        )
        return

    await state.update_data(item_id=item_id, item_name=item['name'])
    await state.set_state(TransferItem.target)
    await callback.message.answer(
        f"📤 Передача «{item['name']}» (у тебя: {inv['quantity']} шт.)\n\n"
        f"Введи @username или ID игрока, которому передать:",
        reply_markup=None
    )


@router.message(TransferItem.target, ~F.text.func(is_main_menu_text))
async def inv_transfer_target(message: Message, state: FSMContext):
    target = await find_user(message.text)
    if not target:
        await message.answer("❌ Игрок не найден. Попробуй @username или ID (или /cancel):")
        return
    await state.update_data(target_id=target['user_id'])
    data = await state.get_data()
    await state.set_state(TransferItem.amount)
    await message.answer(
        f"📤 Передача — получатель @{target['username'] or target['user_id']}\n"
        f"Введи количество (или «-» = 1):"
    )


@router.message(TransferItem.amount, ~F.text.func(is_main_menu_text))
async def inv_transfer_amount(message: Message, state: FSMContext):
    text = message.text.strip()
    if text == "-":
        amount = 1
    else:
        try:
            amount = int(text)
        except ValueError:
            await message.answer("❌ Введи целое число или «-».")
            return
    if amount < 1:
        await message.answer("❌ Количество должно быть не меньше 1.")
        return

    data = await state.get_data()
    from_user = message.from_user.id
    item_id = data['item_id']
    inv = await get_inventory_item(from_user, item_id)
    if not inv or inv['quantity'] < amount:
        await message.answer(f"❌ У тебя нет столько. В наличии: {inv['quantity'] if inv else 0} шт.")
        return

    eq = await get_equipment(from_user)
    if item_id in eq.values():
        await message.answer(
            f"❌ «{data['item_name']}» сейчас экипирован или в активном слоте. "
            f"Передать его можно только снятыми из слота."
        )
        return

    target_id = data['target_id']
    await state.update_data(target_id=target_id, amount=amount)
    await state.set_state(TransferItem.message)
    await message.answer(
        "📨 Сообщение получателю (до 40 символов).\n"
        "Отправь «Пропустить», чтобы передать без сообщения:",
        reply_markup=cancel_keyboard()
    )


@router.message(TransferItem.message, ~F.text.func(is_main_menu_text))
async def inv_transfer_message(message: Message, state: FSMContext):
    text = message.text.strip()
    if text in ("Отмена", "Пропустить", "Без сообщения", "-"):
        text = ""
    elif len(text) > 40:
        await message.answer("❌ Сообщение длиннее 40 символов. Сократи и пришли ещё раз:")
        return

    data = await state.get_data()
    from_user = message.from_user.id
    item_id = data['item_id']
    amount = data['amount']
    target_id = data['target_id']
    inv = await get_inventory_item(from_user, item_id)
    if not inv or inv['quantity'] < amount:
        await message.answer(f"❌ У тебя нет столько. В наличии: {inv['quantity'] if inv else 0} шт.")
        await state.clear()
        return

    ok = await remove_inventory_item(from_user, item_id, amount)
    if not ok:
        await message.answer("❌ Не удалось списать предмет.")
        await state.clear()
        return
    await add_inventory_item(target_id, item_id, amount)

    target_user = await get_user(target_id)
    target_name = f"@{target_user['username']}" if target_user and target_user['username'] else f"#{target_id}"
    await state.clear()

    sender_label = message.from_user.first_name or f"#{from_user}"
    if message.from_user.username:
        sender_label += f" (@{message.from_user.username})"

    # Оповещение получателю
    note = (
        f"📦 Тебе передали: {amount} шт. «{data['item_name']}»\n"
        f"От: {sender_label}"
    )
    if text:
        note += f"\n📨 Сообщение: «{text}»"
    try:
        await message.bot.send_message(target_id, note)
    except Exception:
        pass

    reply = (
        f"✅ Ты передал {amount} шт. «{data['item_name']}» игроку {target_name}!"
    )
    if text:
        reply += f"\n📨 Сообщение: «{text}»"
    await message.answer(reply, reply_markup=await main_menu_kb(message.from_user.id))