"""Магазин: каталог по категориям, покупка за Нордмарки и AP."""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from database.db import (
    get_available_items, get_item, add_inventory_item,
    get_user, remove_nordmarks, get_db, user_has_status_tag, get_status_by_tag,
)
from keyboards.keyboards import (
    shop_catalog_keyboard, item_card_keyboard,
)
from utils.helpers import rarity_emoji, rarity_label, plural_nordmark
from config import ITEM_CATEGORIES

router = Router()

CATEGORIES = ["weapon", "consumable", "equipment", "building", "resource", "special"]
PER_PAGE = 6


async def visible_items(user_id: int, items) -> list:
    """Отфильтровать товары: скрыть те, что требуют статус, которого нет у игрока."""
    result = []
    for it in items:
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
    await callback.message.edit_text(
        "🛒 Каталог — выбери категорию:",
        reply_markup=shop_catalog_keyboard(counts)
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
        buttons.append([InlineKeyboardButton(
            text=f"{emoji} {it['name']} — {it['price']} НМ",
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
        await callback.message.edit_text("Товар не найден.", reply_markup=None)
        return

    header = (
        f"{rarity_emoji(item['rarity'])} {item['name']} {rarity_emoji(item['rarity'])}\n"
        f"Редкость: {rarity_label(item['rarity'])}\n"
        f"Категория: {ITEM_CATEGORIES.get(item['category'], item['category'])}\n\n"
    )
    body = ""
    if item['description']:
        body += f"📝 {item['description']}\n\n"
    body += f"💰 Цена: {item['price']} {plural_nordmark(item['price'])}"
    stock_text = "безлимит" if item['stock'] == -1 else item['stock']
    body += f"\n📦 Остаток: {stock_text}"

    req = await status_req_label(item['required_status'])
    if req:
        body += f"\n🔒 Требуется статус: {req}"

    has_access = await user_has_status_tag(callback.from_user.id, item['required_status'])
    cannot_buy = (item['stock'] == 0) or not has_access
    markup = item_card_keyboard(item['id'], item['price'], can_buy_nord=not cannot_buy)

    await callback.message.edit_text(header + body, reply_markup=markup)


@router.callback_query(F.data.startswith("buy_nord:"))
async def buy_nord(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    item_id = int(callback.data.split(":")[1])
    item = await get_item(item_id)

    if not item or not item['is_available']:
        await callback.message.answer("❌ Товар недоступен.")
        return

    if not await user_has_status_tag(user_id, item['required_status']):
        await callback.message.answer("❌ Тебе нужен статус, чтобы купить этот товар.")
        return

    if item['stock'] == 0:
        await callback.message.answer("❌ Товар распродан.")
        return

    user = await get_user(user_id)
    if user['nordmarks'] < item['price']:
        await callback.message.answer(
            f"❌ Недостаточно средств. Нужно {item['price']} {plural_nordmark(item['price'])}."
        )
        return

    await remove_nordmarks(user_id, item['price'], "shop_purchase", f"Покупка: {item['name']}")
    await add_inventory_item(user_id, item_id, 1)
    await decrement_stock(item_id)
    await callback.message.answer(
        f"✅ Куплено: {item['name']} за {item['price']} {plural_nordmark(item['price'])}!"
    )


async def decrement_stock(item_id: int):
    item = await get_item(item_id)
    if item and item['stock'] != -1 and item['stock'] > 0:
        db = await get_db()
        await db.execute("UPDATE items SET stock = stock - 1 WHERE id = ?", (item_id,))
        await db.commit()
