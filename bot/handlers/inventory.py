"""Инвентарь: просмотр, использование расходников и продажа предметов."""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from database.db import (
    get_inventory, get_item, process_item_use, remove_inventory_item,
    add_nordmarks, get_user, get_inventory_item,
)
from utils.helpers import rarity_emoji, rarity_label, plural_nordmark

router = Router()


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


def inv_item_markup(item_id: int, category: str):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    buttons = []
    if category == "consumable":
        buttons.append([InlineKeyboardButton(text="✅ Использовать", callback_data=f"inv_use:{item_id}")])
    buttons.append([InlineKeyboardButton(text="💵 Продать", callback_data=f"inv_sell:{item_id}")])
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

    text = (
        f"{rarity_emoji(item['rarity'])} {item['name']} {rarity_emoji(item['rarity'])}\n"
        f"Редкость: {rarity_label(item['rarity'])}\n"
        f"В наличии: {inv['quantity']} шт.\n\n"
    )
    if item['description']:
        text += f"📝 {item['description']}\n\n"
    text += f"💵 Продажа: {item['sell_price']} {plural_nordmark(item['sell_price'])}"

    await callback.message.edit_text(text, reply_markup=inv_item_markup(item_id, item['category']))


@router.callback_query(F.data.startswith("inv_use:"))
async def inv_use(callback: CallbackQuery):
    await callback.answer()
    item_id = int(callback.data.split(":")[1])
    ok, msg = await process_item_use(callback.from_user.id, item_id)
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
    await callback.message.answer(
        f"💵 Ты продал {item['name']} за {item['sell_price']} {plural_nordmark(item['sell_price'])}!"
    )
