"""Инвентарь: просмотр, использование расходников, продажа и передача предметов."""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.db import (
    get_inventory, get_item, process_item_use, remove_inventory_item,
    add_nordmarks, get_user, get_inventory_item, get_all_users,
    add_inventory_item, update_item, get_db,
    get_equipment, set_equipment_slot, clear_equipment_slot, log_activity,
)
from utils.helpers import rarity_emoji, rarity_label, plural_nordmark, is_main_menu_text

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


def inv_list_markup(items):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    buttons = []
    for it in items:
        emoji = rarity_emoji(it['rarity'])
        buttons.append([InlineKeyboardButton(
            text=f"{emoji} {it['name']} x{it['quantity']}",
            callback_data=f"invitem:{it['id']}"
        )])
    buttons.append([InlineKeyboardButton(text="🔙 В меню", callback_data="back:main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def inv_item_markup(item_id: int, category: str, can_use: bool = False, is_equipped: bool = False,
                    equip_slot: str = None, potion_slots: list = None):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    buttons = []
    if can_use:
        buttons.append([InlineKeyboardButton(text="✅ Использовать", callback_data=f"inv_use:{item_id}")])
    if category == 'consumable' and potion_slots is not None:
        slot_row = []
        if 1 in potion_slots:
            slot_row.append(InlineKeyboardButton(text="⚗️ Слот 1 ✓", callback_data=f"inv_unslot:potion1"))
        else:
            slot_row.append(InlineKeyboardButton(text="⚗️ В слот 1", callback_data=f"inv_slot:{item_id}:1"))
        if 2 in potion_slots:
            slot_row.append(InlineKeyboardButton(text="⚗️ Слот 2 ✓", callback_data=f"inv_unslot:potion2"))
        else:
            slot_row.append(InlineKeyboardButton(text="⚗️ В слот 2", callback_data=f"inv_slot:{item_id}:2"))
        buttons.append(slot_row)
    if equip_slot:
        if is_equipped:
            buttons.append([InlineKeyboardButton(text="✖️ Снять с себя", callback_data=f"inv_unequip:{item_id}")])
        else:
            buttons.append([InlineKeyboardButton(text="⚔️ Экипировать", callback_data=f"inv_equip:{item_id}")])
    buttons.append([InlineKeyboardButton(text="💵 Продать", callback_data=f"inv_sell:{item_id}")])
    buttons.append([InlineKeyboardButton(text="📤 Передать", callback_data=f"inv_transfer:{item_id}")])
    buttons.append([InlineKeyboardButton(text="🔙 В инвентарь", callback_data="inventory:list")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.message(F.text == "Инвентарь")
async def inventory_menu(message: Message):
    items = await get_inventory(message.from_user.id)
    if not items:
        await message.answer("Твой инвентарь пуст.")
        return
    await message.answer(
        "🎒 ИНВЕНТАРЬ\n\nВыбери предмет:",
        reply_markup=inv_list_markup(items)
    )


@router.callback_query(F.data == "inventory:list")
async def inventory_list_cb(callback: CallbackQuery):
    await callback.answer()
    items = await get_inventory(callback.from_user.id)
    if not items:
        await callback.message.edit_text("Твой инвентарь пуст.", reply_markup=None)
        return
    await callback.message.edit_text("🎒 ИНВЕНТАРЬ\n\nВыбери предмет:",
                                     reply_markup=inv_list_markup(items))


@router.callback_query(F.data.startswith("invitem:"))
async def inv_item_view(callback: CallbackQuery):
    await callback.answer()
    item_id = int(callback.data.split(":")[1])
    item = await get_item(item_id)
    inv = await get_inventory_item(callback.from_user.id, item_id)
    if not item or not inv:
        await callback.message.edit_text("Предмет не найден.", reply_markup=None)
        return

    eq = await get_equipment(callback.from_user.id)

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

    can_use = item['category'] == "consumable" and not (item['heal'] or 0)
    markup = inv_item_markup(item_id, item['category'], can_use=can_use,
                             is_equipped=is_equipped, equip_slot=equip_slot,
                             potion_slots=potion_slots)

    photo_id = item['photo_file_id'] if 'photo_file_id' in item.keys() else None
    if photo_id:
        from aiogram.types import InputMediaPhoto
        try:
            if callback.message.photo:
                await callback.message.edit_media(
                    media=InputMediaPhoto(media=photo_id, caption=text),
                    reply_markup=markup
                )
            else:
                await callback.message.delete()
                await callback.message.answer_photo(photo=photo_id, caption=text, reply_markup=markup)
        except Exception:
            await callback.message.answer_photo(photo=photo_id, caption=text, reply_markup=markup)
    else:
        await callback.message.edit_text(text, reply_markup=markup)


@router.callback_query(F.data.startswith("inv_equip:"))
async def inv_equip(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
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
    await set_equipment_slot(user_id, slot, item_id)
    await callback.message.answer(f"⚗️ {item['name']} поставлен в активный слот {slot_n}.")


@router.callback_query(F.data.startswith("inv_unslot:"))
async def inv_potion_unslot(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
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


@router.callback_query(F.data.startswith("inv_use:"))
async def inv_use(callback: CallbackQuery):
    await callback.answer()
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
    user_id = callback.from_user.id
    item_id = int(callback.data.split(":")[1])
    item = await get_item(item_id)
    inv = await get_inventory_item(user_id, item_id)
    if not item or not inv or inv['quantity'] < 1:
        await callback.message.answer("❌ У тебя нет этого предмета.")
        return

    await remove_inventory_item(user_id, item_id, 1)
    await add_nordmarks(user_id, item['sell_price'], "shop_sale", f"Продажа: {item['name']}")
    await log_activity(user_id, "shop_sale", f"Продал «{item['name']}» за {item['sell_price']} НМ")

    # Маркетплейс: товар с ограниченным остатком (не -1 «безлимит») после продажи игроком
    # возвращается в магазин — сколько продали, столько и появилось к покупке.
    if item['stock'] != -1:
        await update_item(item_id, is_available=1)
        db = await get_db()
        await db.execute("UPDATE items SET stock = stock + 1 WHERE id = ?", (item_id,))
        await db.commit()

    await callback.message.answer(
        f"💵 Ты продал {item['name']} за {item['sell_price']} {plural_nordmark(item['sell_price'])}!"
    )


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