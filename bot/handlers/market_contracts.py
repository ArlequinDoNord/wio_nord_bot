"""Меню контрактов на поставку (рынок → «📜 Контракты на поставку»).

Логика и правила — в utils/market_contracts.py. Здесь только экраны и ввод.
"""

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from database.db import get_db, get_item, get_user, user_is_tourist
from utils import market_contracts as MC
from utils.helpers import plural_nordmark

router = Router()


class ContractNew(StatesGroup):
    qty = State()
    price = State()
    confirm = State()


async def _market_items():
    conn = await get_db()
    cur = await conn.execute(
        "SELECT id, name, sell_price FROM items WHERE market_ok = 1 ORDER BY name LIMIT 12")
    return await cur.fetchall()


def _money(n: int) -> str:
    return f"{n} {plural_nordmark(n)}"


async def _screen(callback_or_msg, text: str, kb: InlineKeyboardMarkup):
    msg = callback_or_msg.message if isinstance(callback_or_msg, CallbackQuery) else callback_or_msg
    try:
        await msg.edit_text(text, reply_markup=kb)
    except Exception:
        await msg.answer(text, reply_markup=kb)


@router.callback_query(F.data == "mkt:contracts")
async def contracts_menu(callback: CallbackQuery):
    await callback.answer()
    uid = callback.from_user.id
    if await user_is_tourist(uid):
        await callback.message.answer("⛔ Контракты доступны только гражданам.")
        return
    rows = await MC.list_open(uid)
    lines = ["📜 КОНТРАКТЫ НА ПОСТАВКУ", "",
             "Заказчик ставит товар и цену за шт., поставщик закрывает контракт целиком.",
             f"Минимум {MC.MIN_QTY} шт., максимум {await MC.max_qty_for(uid)} шт. Налог заказчика {MC.TAX_PERCENT}%.", ""]
    buttons = []
    for r in rows[:20]:
        buttons.append([InlineKeyboardButton(
            text=f"📦 {r['item_name']} ×{r['qty']} — {r['unit_price']} НМ/шт",
            callback_data=f"mkt:view:{r['id']}")])
    if not rows:
        lines.append("Открытых контрактов пока нет.")
    buttons.append([InlineKeyboardButton(text="➕ Выставить контракт", callback_data="mkt:new")])
    buttons.append([InlineKeyboardButton(text="📋 Мои контракты", callback_data="mkt:mine")])
    buttons.append([InlineKeyboardButton(text="🔙 Рынок", callback_data="shopcat:market")])
    await _screen(callback, "\n".join(lines), InlineKeyboardMarkup(inline_keyboard=buttons))


@router.callback_query(F.data == "mkt:mine")
async def contracts_mine(callback: CallbackQuery):
    await callback.answer()
    uid = callback.from_user.id
    conn = await get_db()
    cur = await conn.execute(
        "SELECT mc.*, i.name AS item_name FROM market_contracts mc JOIN items i ON i.id = mc.item_id "
        "WHERE mc.buyer_id = ? ORDER BY mc.id DESC LIMIT 20", (uid,))
    rows = await cur.fetchall()
    status = {"open": "открыт", "closed": "закрыт", "cancelled": "отменён", "expired": "истёк"}
    lines = ["📋 МОИ КОНТРАКТЫ", ""]
    buttons = []
    for r in rows:
        lines.append(f"#{r['id']} {r['item_name']} ×{r['qty']} — {status.get(r['status'], r['status'])}")
        buttons.append([InlineKeyboardButton(text=f"#{r['id']} {r['item_name']} ×{r['qty']}",
                                             callback_data=f"mkt:view:{r['id']}")])
    if not rows:
        lines.append("У тебя пока нет контрактов.")
    buttons.append([InlineKeyboardButton(text="🔙 Контракты", callback_data="mkt:contracts")])
    await _screen(callback, "\n".join(lines), InlineKeyboardMarkup(inline_keyboard=buttons))


@router.callback_query(F.data.regexp(r"^mkt:view:\d+$"))
async def contract_view(callback: CallbackQuery):
    await callback.answer()
    uid = callback.from_user.id
    cid = int(callback.data.split(":")[2])
    conn = await get_db()
    cur = await conn.execute(
        "SELECT mc.*, i.name AS item_name FROM market_contracts mc JOIN items i ON i.id = mc.item_id "
        "WHERE mc.id = ?", (cid,))
    c = await cur.fetchone()
    if not c:
        await callback.message.answer("❌ Контракт не найден.")
        return
    status = {"open": "открыт", "closed": "закрыт", "cancelled": "отменён", "expired": "истёк"}
    text = (
        f"📜 Контракт #{c['id']}\n\n"
        f"📦 {c['item_name']} ×{c['qty']}\n"
        f"💰 {c['unit_price']} НМ за шт. · сумма {_money(c['total'])}\n"
        f"📌 Статус: {status.get(c['status'], c['status'])}\n"
    )
    buttons = []
    if c["status"] == "open":
        if c["buyer_id"] == uid:
            buttons.append([InlineKeyboardButton(text="✖️ Отменить контракт",
                                                 callback_data=f"mkt:cancel:{cid}")])
        else:
            buttons.append([InlineKeyboardButton(text="✅ Закрыть: поставить товар",
                                                 callback_data=f"mkt:close:{cid}")])
    buttons.append([InlineKeyboardButton(text="🔙 Контракты", callback_data="mkt:contracts")])
    await _screen(callback, text, InlineKeyboardMarkup(inline_keyboard=buttons))


@router.callback_query(F.data.regexp(r"^mkt:close:\d+$"))
async def contract_close(callback: CallbackQuery):
    uid = callback.from_user.id
    cid = int(callback.data.split(":")[2])
    ok, msg = await MC.close_contract(uid, cid)
    await callback.answer(msg if ok else "", show_alert=not ok)
    if not ok:
        await callback.message.answer(f"❌ {msg}")
    await contracts_menu(callback)


@router.callback_query(F.data.regexp(r"^mkt:cancel:\d+$"))
async def contract_cancel(callback: CallbackQuery):
    uid = callback.from_user.id
    cid = int(callback.data.split(":")[2])
    ok, res = await MC.cancel_contract(uid, cid)
    if ok:
        await callback.answer("Контракт отменён.")
        await callback.message.answer(f"✖️ Контракт #{cid} отменён. Возврат: {_money(res)}.")
    else:
        await callback.answer(res, show_alert=True)
    await contracts_menu(callback)


# ───────── Выставление ─────────

@router.callback_query(F.data == "mkt:new")
async def contract_new(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    uid = callback.from_user.id
    if await user_is_tourist(uid):
        await callback.message.answer("⛔ Контракты доступны только гражданам.")
        return
    await state.clear()
    items = await _market_items()
    if not items:
        await callback.message.answer("В каталоге пока нет товаров для контрактов.")
        return
    buttons = [[InlineKeyboardButton(text=f"📦 {it['name']} (казна {it['sell_price']} НМ)",
                                     callback_data=f"mkt:pick:{it['id']}")] for it in items]
    buttons.append([InlineKeyboardButton(text="🔙 Контракты", callback_data="mkt:contracts")])
    await _screen(callback, "➕ Выставить контракт\n\nВыбери товар:",
                  InlineKeyboardMarkup(inline_keyboard=buttons))


@router.callback_query(F.data.regexp(r"^mkt:pick:\d+$"))
async def contract_pick(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    item_id = int(callback.data.split(":")[2])
    item = await get_item(item_id)
    if not item:
        await callback.message.answer("❌ Товар не найден.")
        return
    await state.update_data(item_id=item_id)
    await state.set_state(ContractNew.qty)
    limit = await MC.max_qty_for(callback.from_user.id)
    await callback.message.answer(
        f"📦 {item['name']}\n\nВведи количество от {MC.MIN_QTY} до {limit} шт. (сейчас лимит {limit}).")


@router.message(ContractNew.qty, F.text.regexp(r"^\d{1,4}$"))
async def contract_qty(message: Message, state: FSMContext):
    qty = int(message.text)
    limit = await MC.max_qty_for(message.from_user.id)
    if qty < MC.MIN_QTY or qty > limit:
        await message.answer(f"❌ Введи число от {MC.MIN_QTY} до {limit}.")
        return
    data = await state.get_data()
    item = await get_item(data["item_id"])
    q = MC.quote(item["sell_price"], qty, item["sell_price"])
    await state.update_data(qty=qty)
    await state.set_state(ContractNew.price)
    await message.answer(
        f"Минимум по казне: {q['min_unit']} НМ за шт. → сумма {_money(q['min_total'])}, "
        f"с налогом {MC.TAX_PERCENT}% заказчику {_money(q['min_pay'])}.\n\n"
        f"Введи свою цену за шт. (не ниже {q['min_unit']}).")


@router.message(ContractNew.price, F.text.regexp(r"^\d{1,7}$"))
async def contract_price(message: Message, state: FSMContext):
    data = await state.get_data()
    item = await get_item(data["item_id"])
    price = int(message.text)
    if price < int(item["sell_price"] or 0):
        await message.answer(f"❌ Цена не ниже казённой: {item['sell_price']} НМ за шт.")
        return
    q = MC.quote(item["sell_price"], data["qty"], price)
    await state.update_data(price=price)
    await state.set_state(ContractNew.confirm)
    buttons = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Выставить", callback_data="mkt:confirm")],
        [InlineKeyboardButton(text="✖️ Отмена", callback_data="mkt:contracts")],
    ])
    await message.answer(
        f"📜 Подтверждение\n\n📦 {item['name']} ×{data['qty']}\n"
        f"💰 {price} НМ за шт. · сумма исполнителю {_money(q['total'])}\n"
        f"🧾 Налог {MC.TAX_PERCENT}%: {_money(q['tax'])}\n"
        f"👉 Ты заплатишь сейчас: {_money(q['pay'])} (уходит в эскроу и казну)",
        reply_markup=buttons)


@router.callback_query(F.data == "mkt:confirm", ContractNew.confirm)
async def contract_confirm(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    ok, res = await MC.create_contract(callback.from_user.id, data["item_id"], data["qty"], data["price"])
    await state.clear()
    if ok:
        await callback.answer("Контракт выставлен!")
        await callback.message.answer(f"✅ Контракт #{res} выставлен. Срок — {MC.DURATION_DAYS} дней.")
    else:
        await callback.answer(res, show_alert=True)
    await contracts_menu(callback)
