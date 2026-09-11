"""Магазин: каталог по категориям, покупка за Нордмарки и AP."""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from database.db import (
    get_available_items, get_item, add_inventory_item,
    get_user, remove_nordmarks, add_nordmarks, get_db, user_has_status_tag, get_status_by_tag,
    activate_library_card, get_library_cards,
    add_treasury, get_sale_tax_percent, log_activity, update_item,
)
from keyboards.keyboards import (
    shop_catalog_keyboard, item_card_keyboard,
)
from utils.helpers import rarity_emoji, rarity_label, plural_nordmark, item_local_photo, edit_or_replace
from config import ITEM_CATEGORIES

router = Router()

CATEGORIES = [
    "weapon", "consumable", "equipment", "building", "resource",
    "special", "souvenirs", "library_card", "fishing",
    "housing", "furniture", "seeds",
]
PER_PAGE = 6


async def is_pilot(user_id: int) -> bool:
    """Гражданин ли (пилот и выше). Туристам доступен только раздел сувениров."""
    return await user_has_status_tag(user_id, "pilot")


async def visible_items(user_id: int, items) -> list:
    """Отфильтровать товары: скрыть те, что требуют статус, которого нет у игрока.

    Туристы (без статуса «Пилот») видят только сувениры.
    """
    pilot = await is_pilot(user_id)
    result = []
    for it in items:
        if it['category'] == "souvenirs":
            result.append(it)
            continue
        if not pilot:
            continue
        req = it['required_status']
        if req and not await user_has_status_tag(user_id, req):
            continue
        result.append(it)
    return result


async def status_req_label(tag: str) -> str:
    if not tag:
        return ""
    s = await get_status_by_tag(tag)
    return s['name'] if s else tag


@router.message(Command("shop"))
async def shop_cmd(message: Message):
    await shop_menu(message)


@router.message(F.text == "Магазин")
async def shop_menu(message: Message):
    user = await get_user(message.from_user.id)
    if not user:
        await message.answer("Сначала нажми /start")
        return

    items = await visible_items(message.from_user.id, await get_available_items())
    counts = {c: 0 for c in CATEGORIES}
    for it in items:
        if it['category'] in counts:
            counts[it['category']] += 1
    counts = {k: v for k, v in counts.items() if v > 0}

    if not counts:
        await message.answer("🛒 Магазин временно пуст.")
        return

    await message.answer(
        f"🛒 МАГАЗИН\n\n"
        f"💰 Баланс: {user['nordmarks']} {plural_nordmark(user['nordmarks'])}\n"
        f"⚡ AP: {user['ap']}/{user['ap_max']}\n\n"
        f"Выбери категорию:",
        reply_markup=shop_catalog_keyboard(counts)
    )


@router.callback_query(F.data == "shop:catalog")
async def shop_catalog(callback: CallbackQuery):
    await callback.answer()
    items = await visible_items(callback.from_user.id, await get_available_items())
    counts = {c: 0 for c in CATEGORIES}
    for it in items:
        if it['category'] in counts:
            counts[it['category']] += 1
    counts = {k: v for k, v in counts.items() if v > 0}
    await edit_or_replace(
        callback.message,
        "🛒 Каталог — выбери категорию:",
        shop_catalog_keyboard(counts)
    )


@router.callback_query(F.data.regexp(r"^shopcat:[^:]+$"))
async def shop_category(callback: CallbackQuery):
    await callback.answer()
    category = callback.data.split(":")[1]
    items = await visible_items(callback.from_user.id, await get_available_items(category=category))
    if not items:
        await callback.message.edit_text(
            "В этой категории пока нет доступных товаров.", reply_markup=None)
        return
    await show_items_page(callback, category, items, 0)


def items_page_markup(items, category, page: int):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    total = len(items)
    pages = max(1, (total + PER_PAGE - 1) // PER_PAGE)
    page = max(0, min(page, pages - 1))
    start = page * PER_PAGE
    chunk = items[start:start + PER_PAGE]

    buttons = []
    for it in chunk:
        emoji = rarity_emoji(it['rarity'])
        stats = ""
        if it['damage'] > 0:
            stats += f" ⚔️{it['damage']}"
        if it['armor'] > 0:
            stats += f" 🛡{it['armor']}"
        buttons.append([InlineKeyboardButton(
            text=f"{emoji} {it['name']}{stats} — {it['price']} НМ",
            callback_data=f"shopitem:{it['id']}"
        )])

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="◀️", callback_data=f"shopcat:{category}:{page-1}"))
    nav.append(InlineKeyboardButton(text=f"{page+1}/{pages}", callback_data="noop"))
    if page < pages - 1:
        nav.append(InlineKeyboardButton(text="▶️", callback_data=f"shopcat:{category}:{page+1}"))
    if nav:
        buttons.append(nav)

    buttons.append([InlineKeyboardButton(text="🔙 В каталог", callback_data="shop:catalog")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def show_items_page(callback: CallbackQuery, category: str, items, page: int):
    await callback.message.edit_text(
        f"🛒 {ITEM_CATEGORIES.get(category, category)}:",
        reply_markup=items_page_markup(items, category, page)
    )


@router.callback_query(F.data.regexp(r"^shopcat:[^:]+:\d+$"))
async def shop_category_page(callback: CallbackQuery):
    await callback.answer()
    category, page = callback.data.split(":")[1], int(callback.data.split(":")[2])
    items = await visible_items(callback.from_user.id, await get_available_items(category=category))
    await show_items_page(callback, category, items, page)


@router.callback_query(F.data.startswith("shopitem:"))
async def shop_item_view(callback: CallbackQuery):
    await callback.answer()
    item_id = int(callback.data.split(":")[1])
    item = await get_item(item_id)
    if not item:
        await edit_or_replace(callback.message, "Товар не найден.", None)
        return

    header = (
        f"{rarity_emoji(item['rarity'])} {item['name']} {rarity_emoji(item['rarity'])}\n"
        f"Редкость: {rarity_label(item['rarity'])}\n"
        f"Категория: {ITEM_CATEGORIES.get(item['category'], item['category'])}"
    )
    if item['damage'] > 0:
        header += f"\n⚔️ Урон: {item['damage']}"
    if item['armor'] > 0:
        header += f"\n🛡 Броня: {item['armor']}"
    header += "\n\n"
    body = ""
    if item['description']:
        body += f"📝 {item['description']}\n\n"
    body += f"💰 Цена: {item['price']} {plural_nordmark(item['price'])}"
    stock_text = "безлимит" if item['stock'] == -1 else item['stock']
    body += f"\n📦 Остаток: {stock_text}"

    req = await status_req_label(item['required_status'])
    if req:
        body += f"\n🔒 Требуется статус: {req}"

    producer = item['produced_by'] if 'produced_by' in item.keys() else None
    if producer:
        sale_tax = await get_sale_tax_percent()
        seller = await get_user(producer)
        seller_name = f"@{seller['username']}" if seller and seller['username'] else f"#{producer}"
        body += (
            f"\n👨‍🏭 Продавец: {seller_name}\n"
            f"📊 Налог с продажи: {sale_tax}% (выручка продавцу за вычетом налога)"
        )

    has_access = await user_has_status_tag(callback.from_user.id, item['required_status'])
    cannot_buy = (item['stock'] == 0) or not has_access
    markup = item_card_keyboard(item['id'], item['price'], can_buy_nord=not cannot_buy)

    # Для безлимитных товаров (fishing/consumable) — кнопка «Купить 5 шт»
    if item['stock'] == -1 and not cannot_buy and item['price'] > 0:
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        rows = list(markup.inline_keyboard)
        buy5_price = item['price'] * 5
        rows.insert(-1, [InlineKeyboardButton(
            text=f"💰 Купить 5 за {buy5_price}",
            callback_data=f"buy5_nord:{item['id']}"
        )])
        markup = InlineKeyboardMarkup(inline_keyboard=rows)

    text = header + body
    photo_id = item['photo_file_id'] if 'photo_file_id' in item.keys() else None
    local_photo = None if photo_id else item_local_photo(item['name'])
    if photo_id or local_photo:
        from aiogram.types import InputMediaPhoto, FSInputFile
        media = photo_id or FSInputFile(local_photo)
        try:
            if callback.message.photo:
                await callback.message.edit_media(
                    media=InputMediaPhoto(media=media, caption=text),
                    reply_markup=markup
                )
            else:
                await callback.message.delete()
                await callback.message.answer_photo(photo=media, caption=text, reply_markup=markup)
        except Exception:
            await callback.message.answer_photo(photo=media, caption=text, reply_markup=markup)
    else:
        await callback.message.edit_text(text, reply_markup=markup)


@router.callback_query(F.data.startswith("buy_nord:"))
async def buy_nord(callback: CallbackQuery):
    await callback.answer()
    item_id = int(callback.data.split(":")[1])
    await _buy_item(callback, item_id, 1)


@router.callback_query(F.data.startswith("buy5_nord:"))
async def buy5_nord(callback: CallbackQuery):
    await callback.answer()
    item_id = int(callback.data.split(":")[1])
    await _buy_item(callback, item_id, 5)


async def _buy_item(callback: CallbackQuery, item_id: int, qty: int):
    user_id = callback.from_user.id
    item = await get_item(item_id)

    if not item or not item['is_available']:
        await callback.answer("❌ Товар недоступен.", show_alert=True)
        return

    if not await user_has_status_tag(user_id, item['required_status']):
        await callback.answer("❌ Тебе нужен статус, чтобы купить этот товар.", show_alert=True)
        return

    if item['stock'] == 0:
        await callback.answer("❌ Товар распродан.", show_alert=True)
        return

    if item['stock'] != -1 and item['stock'] < qty:
        await callback.answer(f"❌ В магазине осталось меньше {qty} шт.", show_alert=True)
        return

    user = await get_user(user_id)
    total = item['price'] * qty
    if user['nordmarks'] < total:
        await callback.answer(
            f"❌ Недостаточно. Нужно {total} {plural_nordmark(total)}", show_alert=True
        )
        return

    await remove_nordmarks(user_id, total, "shop_purchase", f"Покупка: {item['name']} x{qty}")
    await add_inventory_item(user_id, item_id, qty)

    if item['stock'] != -1:
        db = await get_db()
        await db.execute("UPDATE items SET stock = stock - ? WHERE id = ?", (qty, item_id))
        await db.commit()
        refreshed = await get_item(item_id)
        if refreshed['stock'] <= 0:
            await update_item(item_id, is_available=0)

    await log_activity(user_id, "shop_purchase", f"Купил «{item['name']}» x{qty} за {total} НМ")
    await add_treasury(total, f"Продажа: {item['name']} x{qty}")

    producer = item['produced_by'] if 'produced_by' in item.keys() else None
    if producer:
        sale_tax = await get_sale_tax_percent()
        tax_amount = int(total * sale_tax / 100)
        seller_pay = total - tax_amount
        await add_nordmarks(
            producer, seller_pay, "shop_payout",
            f"Продажа товара: {item['name']} x{qty} ({sale_tax}% налог)"
        )

    if item['category'] == "library_card" and qty == 1:
        card_type = "silver" if "Серебряный" in item['name'] else "basic"
        await activate_library_card(user_id, card_type)
        await callback.message.answer(
            f"✅ Читательский билет активирован на 30 дней!\n"
            f"📚 Заходи в Библиотеку через Город."
        )
    else:
        await callback.message.answer(
            f"✅ Куплено: {item['name']} x{qty} за {total} {plural_nordmark(total)}!"
        )


async def decrement_stock(item_id: int):
    item = await get_item(item_id)
    if item and item['stock'] != -1 and item['stock'] > 0:
        db = await get_db()
        await db.execute("UPDATE items SET stock = stock - 1 WHERE id = ?", (item_id,))
        await db.commit()
