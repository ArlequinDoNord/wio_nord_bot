"""Магазин: каталог по категориям, покупка за Нордмарки и AP."""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.db import (
    get_available_items, get_item, add_inventory_item,
    get_user, remove_nordmarks, add_nordmarks, get_db, user_has_status_tag, get_status_by_tag,
    activate_library_card, get_library_cards,
    add_treasury, get_sale_tax_percent, log_activity, update_item,
    get_player_housing, get_housing_slots, set_housing_slot, set_player_housing,
    get_item_by_name, HOUSING_TYPES, HOUSING_ORDER,
    get_special_dept_code, get_special_fails, register_special_fail,
    is_special_blocked, special_dept_block_left_minutes, clear_special_blocked,
)
from keyboards.keyboards import (
    shop_catalog_keyboard, item_card_keyboard, cancel_keyboard, main_menu_keyboard,
)
from bot.handlers.housing import (
    FURNITURE_BY_ITEM, FURNITURE_BY_EXPANSION, HOUSING_ITEM_BY_NAME, housing_menu,
)
from utils.helpers import rarity_emoji, rarity_label, plural_nordmark, item_local_photo, edit_or_replace
from config import ITEM_CATEGORIES, SPECIAL_DEPT_ATTEMPTS_LIMIT

router = Router()

CATEGORIES = [
    "weapon", "consumable", "equipment", "building", "resource",
    "special", "special_dept", "souvenirs", "library_card", "fishing",
    "housing", "furniture", "seeds",
]
PER_PAGE = 6


class SpecialDeptBuy(StatesGroup):
    """Ввод кода доступа к спец-отделу при покупке товара."""
    code = State()


def _allow_multi_buy(item) -> bool:
    """Покупать пачками (>1 шт.) можно только расходники и наживку.

    Жильё, мебель, удочки, билеты и прочее — только по одной штуке.
    """
    item = dict(item)
    if item.get("category") == "consumable":
        return True
    if item.get("category") == "fishing":
        text = f"{item['name']} {item.get('description') or ''}".lower()
        return "наживка" in text
    return False


async def furniture_block_reason(user_id: int, item) -> str:
    """Причина, почему расширение нельзя купить (некуда ставить), иначе пустая строка."""
    item = dict(item)
    if item.get("category") != "furniture":
        return ""
    h = await get_player_housing(user_id)
    info = HOUSING_TYPES[h["housing_type"]]
    # Студию нельзя расширять/улучшать по описанию: у неё только встроенная кухня
    if h["housing_type"] == "studio":
        return "студию нельзя расширять: у неё только встроенная кухня и нет слотов для мебели"
    slots = await get_housing_slots(user_id)
    free = info["slots"] - sum(1 for s in slots.values() if s.get("expansion_type"))
    if free > 0:
        return ""
    # Кухня более высокого уровня заменяет уже установленную кухню (не встроенную)
    mapping = FURNITURE_BY_ITEM.get(item["name"])
    if mapping:
        et, lvl = mapping
        if et == "kitchen":
            for s in slots.values():
                if (not s.get("embedded") and s.get("expansion_type") == "kitchen"
                        and s.get("expansion_level", 1) < lvl):
                    return ""
    return f"некуда установить: в твоём жилье «{info['name']}» нет свободных слотов"


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

    if item['category'] == "special_dept":
        has_code = bool(await get_special_dept_code())
        body += (
            "\n🔐 Товар из Спец-отдела: покупка возможна только по коду доступа."
            if has_code else "\n🔒 Спец-отдел сейчас закрыт."
        )

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

    # Мебель (расширения жилья): предупреждение, если устанавливать некуда
    block_reason = await furniture_block_reason(callback.from_user.id, item)
    if block_reason:
        body += f"\n⚠️ {block_reason}"

    # Нехватка Нордмарок: показываем сразу в карточке, а не только при покупке
    user = await get_user(callback.from_user.id)
    balance = user['nordmarks'] if user else 0
    if item['price'] > 0 and not cannot_buy and balance < item['price']:
        body += (
            f"\n⚠️ Не хватает {item['price'] - balance} "
            f"{plural_nordmark(item['price'] - balance)} "
            f"(нужно {item['price']}, у тебя {balance})"
        )

    # Для безлимитных расходников и наживки — кнопка «Купить 5 шт»
    if (item['stock'] == -1 and not cannot_buy and item['price'] > 0
            and _allow_multi_buy(item)):
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
async def buy_nord(callback: CallbackQuery, state: FSMContext):
    item_id = int(callback.data.split(":")[1])
    item = await get_item(item_id)
    if item and item['category'] == "special_dept":
        await _start_special_dept_buy(callback, state, item_id, 1)
        return
    await _buy_item(callback, item_id, 1)


@router.callback_query(F.data.startswith("buy5_nord:"))
async def buy5_nord(callback: CallbackQuery, state: FSMContext):
    item_id = int(callback.data.split(":")[1])
    item = await get_item(item_id)
    if not item:
        await callback.answer("❌ Товар не найден.", show_alert=True)
        return
    if item['category'] == "special_dept":
        await _start_special_dept_buy(callback, state, item_id, 5)
        return
    if _allow_multi_buy(item):
        await _buy_item(callback, item_id, 5)
    else:
        await callback.answer("❌ Этот товар продаётся только по одной штуке.", show_alert=True)


async def _start_special_dept_buy(callback: CallbackQuery, state: FSMContext, item_id: int, qty: int):
    """Начать покупку из спец-отдела: запрашиваем код доступа."""
    uid = callback.from_user.id

    code = await get_special_dept_code()
    if not code:
        await callback.answer("🔐 Спец-отдел сейчас закрыт.", show_alert=True)
        return

    if await is_special_blocked(uid):
        minutes = await special_dept_block_left_minutes(uid)
        await callback.answer(
            f"⛔ Ты ввёл код спец-отдела неверно 3 раза. "
            f"Покупки заблокированы ещё на {minutes} мин.",
            show_alert=True)
        return

    await state.set_state(SpecialDeptBuy.code)
    await state.update_data(special_item_id=item_id, special_qty=qty)
    await callback.message.answer(
        "🔐 СПЕЦ-ОТДЕЛ\n\n"
        "Эта секция магазина доступна по коду доступа.\n"
        f"Осталось попыток: {SPECIAL_DEPT_ATTEMPTS_LIMIT}.\n\n"
        "Введи код:",
        reply_markup=cancel_keyboard()
    )


@router.message(SpecialDeptBuy.code)
async def special_dept_enter_code(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    uid = message.from_user.id

    if text in ("Отмена", "-", "Пропустить"):
        await state.clear()
        await message.answer("Отменено.", reply_markup=main_menu_keyboard())
        return

    data = await state.get_data()
    item_id = data.get('special_item_id')
    qty = data.get('special_qty') or 1

    code = await get_special_dept_code()
    if not code:
        await state.clear()
        await message.answer("🔐 Спец-отдел сейчас закрыт.", reply_markup=main_menu_keyboard())
        return

    if await is_special_blocked(uid):
        minutes = await special_dept_block_left_minutes(uid)
        await state.clear()
        await message.answer(
            f"⛔ Ты ввёл код спец-отдела неверно 3 раза. "
            f"Покупки заблокированы ещё на {minutes} мин.",
            reply_markup=main_menu_keyboard())
        return

    if text == code:
        await clear_special_blocked(uid)
        await state.clear()
        await _buy_item(_MsgSender(message), item_id, qty, special_verified=True)
        return

    banned = await register_special_fail(uid)
    if banned:
        await state.clear()
        await message.answer(
            "⛔ Неверный код! Ты ввёл его неверно 3 раза — "
            f"покупки в спец-отделе заблокированы на 24 часа.",
            reply_markup=main_menu_keyboard())
        return

    fails = await get_special_fails(uid)
    left = max(0, SPECIAL_DEPT_ATTEMPTS_LIMIT - fails)
    await message.answer(
        f"❌ Неверный код. Осталось попыток: {left}.\n"
        "Введи код ещё раз:",
        reply_markup=cancel_keyboard()
    )


class _MsgSender:
    """Обёртка Message как CallbackQuery для повторного использования _buy_item."""

    def __init__(self, message: Message):
        self.message = message
        self.from_user = message.from_user

    async def answer(self, text: str = "", show_alert: bool = False):
        if text:
            await self.message.answer(text)


async def _buy_item(callback: CallbackQuery, item_id: int, qty: int, special_verified: bool = False):
    user_id = callback.from_user.id
    item = await get_item(item_id)

    if not item or not item['is_available']:
        await callback.answer("❌ Товар недоступен.", show_alert=True)
        return

    if not await user_has_status_tag(user_id, item['required_status']):
        await callback.answer("❌ Тебе нужен статус, чтобы купить этот товар.", show_alert=True)
        return

    # Спец-отдел: без подтверждённого кода покупка не проходит (кроме попытки из FSM)
    if not special_verified and item['category'] == "special_dept":
        await callback.answer("🔐 Покупка в спец-отделе только по коду доступа.", show_alert=True)
        return

    if item['stock'] == 0:
        await callback.answer("❌ Товар распродан.", show_alert=True)
        return

    if item['stock'] != -1 and item['stock'] < qty:
        await callback.answer(f"❌ В магазине осталось меньше {qty} шт.", show_alert=True)
        return

    # Расширения жилья нельзя купить, если их некуда ставить
    block_reason = await furniture_block_reason(user_id, item)
    if block_reason:
        await callback.answer(f"❌ {block_reason}", show_alert=True)
        return

    user = await get_user(user_id)
    total = item['price'] * qty
    if user['nordmarks'] < total:
        await callback.answer(
            f"❌ Недостаточно. Нужно {total} {plural_nordmark(total)}", show_alert=True
        )
        return

    # Жильё покупается как ПЕРЕЕЗД: показываем подтверждение вместо покупки
    if item['category'] == 'housing':
        await callback.answer()
        await _housing_purchase_confirm(callback, item)
        return

    await callback.answer()

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


# ───────── жильё: покупка = переезд с подтверждением ─────────

async def _housing_purchase_confirm(callback: CallbackQuery, item):
    """Экран подтверждения: покупка жилья сразу переселяет и заменяет текущее."""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    item = dict(item)
    h = await get_player_housing(callback.from_user.id)
    current_name = HOUSING_TYPES[h['housing_type']]['name'] if h else '—'
    text = (
        f"{rarity_emoji(item['rarity'])} {item['name']}\n\n"
        f"⚠️ Это жильё покупается сразу как ПЕРЕЕЗД:\n"
        f"• Текущее жильё «{current_name}» будет заменено.\n"
        f"• Вся установленная мебель вернётся в инвентарь.\n"
        f"• Стоимость: {item['price']} {plural_nordmark(item['price'])}\n\n"
        f"Подтверждаешь переезд?"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Да, переезжаем", callback_data=f"buy_housing:{item['id']}")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data=f"buy_housing_cancel:{item['id']}")],
    ])
    await callback.message.answer(text, reply_markup=kb)


@router.callback_query(F.data.startswith("buy_housing_cancel:"))
async def buy_housing_cancel(callback: CallbackQuery):
    await callback.answer()
    try:
        await callback.message.delete()
    except Exception:
        pass


@router.callback_query(F.data.startswith("buy_housing:"))
async def buy_housing_confirm(callback: CallbackQuery):
    await callback.answer()
    uid = callback.from_user.id
    item_id = int(callback.data.split(":")[1])
    item = await get_item(item_id)
    if not item or item['category'] != 'housing':
        return

    if not await user_has_status_tag(uid, item['required_status']):
        await callback.answer("❌ Тебе нужен статус, чтобы купить этот товар.", show_alert=True)
        return
    if item['stock'] == 0 or (item['stock'] != -1 and item['stock'] < 1):
        await callback.answer("❌ Товар распродан.", show_alert=True)
        return

    h = await get_player_housing(uid)
    current_idx = HOUSING_ORDER.index(h['housing_type']) if h and h['housing_type'] in HOUSING_ORDER else -1
    target = HOUSING_ITEM_BY_NAME.get(item['name'])
    if not target:
        return
    if HOUSING_ORDER.index(target) <= current_idx:
        await callback.answer("❌ У тебя уже есть такое жильё или лучше.", show_alert=True)
        return

    user = await get_user(uid)
    total = item['price']
    if user['nordmarks'] < total:
        await callback.answer(
            f"❌ Недостаточно. Нужно {total} {plural_nordmark(total)}", show_alert=True
        )
        return

    # Списываем деньги
    await remove_nordmarks(uid, total, "shop_purchase", f"Покупка: {item['name']} (переезд)")
    await add_treasury(total, f"Продажа: {item['name']}")

    # Вся текущая мебель возвращается в инвентарь (кроме встроенной)
    slots = await get_housing_slots(uid)
    for i, s in slots.items():
        et, lvl = s.get("expansion_type"), s.get("expansion_level", 1)
        await set_housing_slot(uid, i, None)
        if s.get("embedded"):
            continue
        fname = FURNITURE_BY_EXPANSION.get((et, lvl))
        if fname:
            fi = await get_item_by_name(fname)
            if fi:
                await add_inventory_item(uid, fi["id"], 1)

    # Переезд
    await set_player_housing(uid, target)
    if target == "studio":
        await set_housing_slot(uid, 0, "kitchen", 1, embedded=True)

    # Остаток на складе
    if item['stock'] != -1:
        db = await get_db()
        await db.execute("UPDATE items SET stock = stock - 1 WHERE id = ?", (item_id,))
        await db.commit()
        refreshed = await get_item(item_id)
        if refreshed['stock'] <= 0:
            await update_item(item_id, is_available=0)

    await log_activity(uid, "housing_move", target)
    await log_activity(uid, "shop_purchase",
                       f"Купил «{item['name']}» за {total} НМ (переезд)")

    await callback.answer(
        f"🎉 Переезд в «{HOUSING_TYPES[target]['name']}» завершён!", show_alert=True
    )
    await housing_menu(callback)
