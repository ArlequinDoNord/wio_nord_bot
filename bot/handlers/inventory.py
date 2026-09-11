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
    get_fish_catches, sell_one_fish_catch, get_active_run, process_food_expiry,
)
from utils.helpers import (
    rarity_emoji, rarity_label, plural_nordmark, is_main_menu_text,
    item_local_photo, fish_weight_tier, fish_sell_price, edit_or_replace,
)

router = Router()


class TransferItem(StatesGroup):
    target = State()
    amount = State()


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
    for cat in INV_CATEGORIES:
        if cat not in counts or counts[cat] <= 0:
            continue
        label = category_label(cat)
        emoji = {"weapon": "⚔️", "equipment": "🛡️", "consumable": "🧪",
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
                    sell5: bool = False, occupied: dict = None):
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
        buttons.append([InlineKeyboardButton(text="💵 Продать", callback_data=f"inv_sell:{item_id}")])
        if sell5:
            buttons.append([InlineKeyboardButton(text="💵 Продать 5 шт", callback_data=f"inv_sell5:{item_id}")])
    buttons.append([InlineKeyboardButton(text="📤 Передать", callback_data=f"inv_transfer:{item_id}")])
    buttons.append([InlineKeyboardButton(text="🔙 К категориям", callback_data="inventory:list")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


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


async def _render_item_card(message, user_id: int, item_id: int):
    """Перерисовывает карточку предмета в указанном сообщении (edit или replace)."""
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
        equip_slot = 'armor'
    is_equipped = eq.get(equip_slot) == item_id if equip_slot else False
    if is_equipped:
        text += f"\n\n🔹 Экипировано: {'⚔️' if equip_slot == 'weapon' else '🛡️'}"

    # Активные слоты зелий (potion1/potion2) — в каких стоит этот предмет
    potion_slots = [n for n, slot in ((1, 'potion1'), (2, 'potion2')) if eq.get(slot) == item_id]
    if potion_slots:
        text += f"\n\n⚗️ В активном слоте: {', '.join(str(n) for n in potion_slots)}"

    # Кто сейчас занимает слоты (для честной замены — без сюрпризов)
    occupied = {}
    if item['category'] == 'consumable':
        for n, slot in ((1, 'potion1'), (2, 'potion2')):
            occ_id = eq.get(slot)
            if occ_id and occ_id != item_id:
                occ_item = await get_item(occ_id)
                occupied[slot] = occ_item['name'] if occ_item else f"#{occ_id}"

    can_use = item['category'] == "consumable" and not (item['heal'] or 0)
    if in_run:
        can_use = False
        equip_slot = None
        potion_slots = []
        occupied = {}
    markup = inv_item_markup(item_id, item['category'], can_use=can_use,
                             is_equipped=is_equipped, equip_slot=equip_slot,
                             potion_slots=potion_slots,
                             sellable=(item['sell_price'] or 0) > 0,
                             sell5=(inv['quantity'] or 0) >= 5,
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
        slot = 'armor'
    else:
        await callback.message.answer("❌ Этот предмет нельзя экипировать.")
        return

    await set_equipment_slot(user_id, slot, item_id)
    await callback.message.answer(
        f"✅ Экипировано: {item['name']}"
    )


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

    if item['category'] == 'weapon':
        slot = 'weapon'
    else:
        slot = 'armor'
    await clear_equipment_slot(user_id, slot)
    await callback.message.answer(f"✖️ Снято: {item['name']}")


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
    await callback.answer()
    item_id = int(callback.data.split(":")[1])
    await _sell_item(callback, item_id, 1)


@router.callback_query(F.data.startswith("inv_sell5:"))
async def inv_sell5(callback: CallbackQuery):
    await callback.answer()
    item_id = int(callback.data.split(":")[1])
    await _sell_item(callback, item_id, 5)


async def _sell_item(callback: CallbackQuery, item_id: int, qty: int):
    user_id = callback.from_user.id
    item = await get_item(item_id)
    inv = await get_inventory_item(user_id, item_id)
    if not item or not inv or inv['quantity'] < qty:
        await callback.answer(f"❌ У тебя меньше {qty} шт. этого предмета.", show_alert=True)
        return

    # Нельзя продать предмет, стоящий в любом активном слоте (иначе останется «призрачный слот»:
    # урон/защита берутся напрямую из items по id в equipment, без проверки инвентаря).
    eq = await get_equipment(user_id)
    if item_id in eq.values():
        slot_names = {
            'potion1': 'активный слот 1',
            'potion2': 'активный слот 2',
            'weapon': 'оружие',
            'armor': 'броня',
        }
        used = [slot_names[s] for s in ('potion1', 'potion2', 'weapon', 'armor') if eq.get(s) == item_id]
        await callback.message.answer(
            f"❌ «{item['name']}» сейчас используется ({', '.join(used)}). "
            f"Сначала сними его."
        )
        return

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

    await callback.message.answer(
        f"💵 Ты продал {item['name']} x{qty} за {total} {plural_nordmark(total)}!"
    )


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
    text = (
        f"{rarity_emoji(item['rarity'])} {item['name']} {rarity_emoji(item['rarity'])}\n"
        f"Редкость: {rarity_label(item['rarity'])}\n\n"
        f"⚖️ Вес: {tier['label']}\n"
        f"В наличии: {count} шт.\n\n"
        f"{item['description']}\n\n"
        f"💵 Цена продажи (с учётом веса): {sell_text}"
    )
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"💵 Продать одну (за {sell_text})",
                              callback_data=f"fishsell:{item_id}:{weight}")],
        [InlineKeyboardButton(text="🔙 К категориям", callback_data="inventory:list")],
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
        slot_names = {
            'potion1': 'активный слот 1',
            'potion2': 'активный слот 2',
            'weapon': 'оружие',
            'armor': 'броня',
        }
        used = [slot_names[s] for s in ('potion1', 'potion2', 'weapon', 'armor') if eq.get(s) == item_id]
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
    ok = await remove_inventory_item(from_user, item_id, amount)
    if not ok:
        await message.answer("❌ Не удалось списать предмет.")
        await state.clear()
        return
    await add_inventory_item(target_id, item_id, amount)

    target_user = await get_user(target_id)
    target_name = f"@{target_user['username']}" if target_user and target_user['username'] else f"#{target_id}"
    await state.clear()
    await message.answer(
        f"✅ Ты передал {amount} шт. «{data['item_name']}» игроку {target_name}!"
    )