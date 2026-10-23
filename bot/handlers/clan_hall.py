"""Клан-холл: клановый склад (пожертвования ресурсов).

Первый блок большой фичи «Клан-холл» (см. CLAN_HALL.md): общий склад клана,
куда любой член может безвозвратно передать ресурсы из личного инвентаря.
Строительство здания и расширения подключаются следующими фазами.
"""

import html

from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from database.db import (
    get_clan, is_clan_member, get_clan_storage, get_clan_storage_qty,
    get_inventory, get_inventory_item, get_item, donate_to_clan_storage,
    get_clan_contributions,
)

router = Router()

STORAGE_PAGE = 12


def _esc(text) -> str:
    return html.escape(str(text or ""))


def build_clan_storage_text(clan, rows) -> str:
    lines = [f"📦 <b>Клановый склад</b> — «{_esc(clan['name'])}»", ""]
    if not rows:
        lines.append("Склад пуст. Внеси ресурсы первым!")
    else:
        total = 0
        for r in rows:
            total += r['qty']
            lines.append(f"• {_esc(r['name'])} — <b>{r['qty']}</b>")
        lines.append(f"\nВсего единиц: <b>{total}</b>")
    lines.append("\nВклад невозвратен: ресурсы идут на нужды клана.")
    return "\n".join(lines)


def build_donate_text(clan, items) -> str:
    lines = [
        f"➕ <b>Внести ресурсы</b> — «{_esc(clan['name'])}»",
        "",
        "Выбери ресурс из инвентаря. Вклад невозвратен.",
    ]
    if not items:
        lines.append("\nУ тебя нет ресурсов для вклада.")
    return "\n".join(lines)


def build_donate_item_text(item, have: int, stored: int) -> str:
    return (
        f"📦 <b>{_esc(item['name'])}</b>\n\n"
        f"У тебя: <b>{have}</b>\n"
        f"На складе клана: <b>{stored}</b>\n\n"
        "Сколько внести? Вклад невозвратен."
    )


def build_contrib_text(clan, rows) -> str:
    lines = [f"🧾 <b>Вклады</b> — «{_esc(clan['name'])}»", ""]
    if not rows:
        lines.append("Пока никто ничего не вносил.")
    else:
        for r in rows:
            who = _esc(r['user_name'] or f"#{r['user_id']}")
            item = _esc(r['item_name'] or f"#{r['item_id']}")
            day = str(r['created_at'] or "")[:10]
            lines.append(f"• {who}: {item} × {r['qty']}  <i>{day}</i>")
    return "\n".join(lines)


async def _paint(cb: CallbackQuery, text: str, kb: InlineKeyboardMarkup):
    """Рисует экран: на фото-сообщении отправляет новое и убирает старое."""
    msg = cb.message
    try:
        if getattr(msg, "photo", None):
            new = await msg.answer(text, reply_markup=kb, parse_mode="HTML")
            try:
                await msg.delete()
            except Exception:
                pass
            return new
        return await msg.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except Exception:
        return await msg.answer(text, reply_markup=kb, parse_mode="HTML")


async def _member_clan(cb: CallbackQuery, clan_id: int):
    """Клан, если отправитель — его член. Иначе alert и None."""
    clan = await get_clan(clan_id)
    if not clan or clan['kind'] != 'clan':
        await cb.answer("❌ Клан не найден.", show_alert=True)
        return None
    if not await is_clan_member(clan_id, cb.from_user.id):
        await cb.answer("❌ Склад доступен только членам клана.", show_alert=True)
        return None
    return clan


@router.callback_query(F.data.startswith("clanh:storage:"))
async def clan_storage_cb(cb: CallbackQuery):
    await cb.answer()
    clan_id = int(cb.data.split(":")[2])
    clan = await _member_clan(cb, clan_id)
    if not clan:
        return
    rows = await get_clan_storage(clan_id)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Внести ресурсы",
                              callback_data=f"clanh:donate:{clan_id}")],
        [InlineKeyboardButton(text="🧾 Вклады",
                              callback_data=f"clanh:log:{clan_id}")],
        [InlineKeyboardButton(text="🔙 К клану",
                              callback_data=f"clans:view:{clan_id}")],
    ])
    await _paint(cb, build_clan_storage_text(clan, rows), kb)


@router.callback_query(F.data.startswith("clanh:donate:"))
async def clan_donate_cb(cb: CallbackQuery):
    await cb.answer()
    clan_id = int(cb.data.split(":")[2])
    clan = await _member_clan(cb, clan_id)
    if not clan:
        return
    inv = await get_inventory(cb.from_user.id)
    items = [i for i in inv if i['category'] == 'resource' and (i['quantity'] or 0) > 0]
    rows = []
    for it in items[:STORAGE_PAGE]:
        rows.append([InlineKeyboardButton(
            text=f"{it['name']} · {it['quantity']} шт.",
            callback_data=f"clanh:item:{clan_id}:{it['id']}")])
    if len(items) > STORAGE_PAGE:
        rows.append([InlineKeyboardButton(
            text=f"… и ещё {len(items) - STORAGE_PAGE}",
            callback_data="clanh:noop")])
    rows.append([InlineKeyboardButton(text="🔙 К складу",
                                      callback_data=f"clanh:storage:{clan_id}")])
    await _paint(cb, build_donate_text(clan, items),
                 InlineKeyboardMarkup(inline_keyboard=rows))


@router.callback_query(F.data.startswith("clanh:item:"))
async def clan_donate_item_cb(cb: CallbackQuery):
    await cb.answer()
    _, _, clan_id_s, item_id_s = cb.data.split(":")
    clan_id, item_id = int(clan_id_s), int(item_id_s)
    clan = await _member_clan(cb, clan_id)
    if not clan:
        return
    item = await get_item(item_id)
    if not item or item['category'] != 'resource':
        await cb.answer("❌ Это не ресурс.", show_alert=True)
        return
    inv = await get_inventory_item(cb.from_user.id, item_id)
    have = inv['quantity'] if inv else 0
    stored = await get_clan_storage_qty(clan_id, item_id)
    rows = []
    if have > 0:
        btns = [InlineKeyboardButton(text="+1",
                                     callback_data=f"clanh:give:{clan_id}:{item_id}:1")]
        if have >= 10:
            btns.append(InlineKeyboardButton(
                text="+10", callback_data=f"clanh:give:{clan_id}:{item_id}:10"))
        btns.append(InlineKeyboardButton(
            text=f"Всё ({have})", callback_data=f"clanh:give:{clan_id}:{item_id}:all"))
        rows.append(btns)
    rows.append([InlineKeyboardButton(text="🔙 К выбору ресурса",
                                      callback_data=f"clanh:donate:{clan_id}")])
    await _paint(cb, build_donate_item_text(item, have, stored),
                 InlineKeyboardMarkup(inline_keyboard=rows))


@router.callback_query(F.data.startswith("clanh:give:"))
async def clan_donate_give_cb(cb: CallbackQuery):
    _, _, clan_id_s, item_id_s, amount = cb.data.split(":")
    clan_id, item_id = int(clan_id_s), int(item_id_s)
    clan = await _member_clan(cb, clan_id)
    if not clan:
        return
    item = await get_item(item_id)
    if not item or item['category'] != 'resource':
        await cb.answer("❌ Это не ресурс.", show_alert=True)
        return
    inv = await get_inventory_item(cb.from_user.id, item_id)
    have = inv['quantity'] if inv else 0
    qty = have if amount == 'all' else int(amount)
    if qty <= 0 or qty > have:
        await cb.answer("❌ Недостаточно ресурсов.", show_alert=True)
        return
    if not await donate_to_clan_storage(clan_id, cb.from_user.id, item_id, qty):
        await cb.answer("❌ Не удалось внести ресурс.", show_alert=True)
        return
    await cb.answer(f"✅ Внесено: {item['name']} × {qty}", show_alert=True)

    inv = await get_inventory_item(cb.from_user.id, item_id)
    have = inv['quantity'] if inv else 0
    stored = await get_clan_storage_qty(clan_id, item_id)
    if have <= 0:
        inv_all = await get_inventory(cb.from_user.id)
        items = [i for i in inv_all
                 if i['category'] == 'resource' and (i['quantity'] or 0) > 0]
        rows = []
        for it in items[:STORAGE_PAGE]:
            rows.append([InlineKeyboardButton(
                text=f"{it['name']} · {it['quantity']} шт.",
                callback_data=f"clanh:item:{clan_id}:{it['id']}")])
        rows.append([InlineKeyboardButton(text="🔙 К складу",
                                          callback_data=f"clanh:storage:{clan_id}")])
        await _paint(cb, build_donate_text(clan, items),
                     InlineKeyboardMarkup(inline_keyboard=rows))
        return

    rows = [[
        InlineKeyboardButton(text="+1",
                             callback_data=f"clanh:give:{clan_id}:{item_id}:1"),
    ]]
    btns = rows[0]
    if have >= 10:
        btns.append(InlineKeyboardButton(
            text="+10", callback_data=f"clanh:give:{clan_id}:{item_id}:10"))
    btns.append(InlineKeyboardButton(
        text=f"Всё ({have})", callback_data=f"clanh:give:{clan_id}:{item_id}:all"))
    rows.append([InlineKeyboardButton(text="🔙 К выбору ресурса",
                                      callback_data=f"clanh:donate:{clan_id}")])
    await _paint(cb, build_donate_item_text(item, have, stored),
                 InlineKeyboardMarkup(inline_keyboard=rows))


@router.callback_query(F.data.startswith("clanh:log:"))
async def clan_contrib_cb(cb: CallbackQuery):
    await cb.answer()
    clan_id = int(cb.data.split(":")[2])
    clan = await _member_clan(cb, clan_id)
    if not clan:
        return
    rows = await get_clan_contributions(clan_id, limit=20)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 К складу",
                              callback_data=f"clanh:storage:{clan_id}")],
    ])
    await _paint(cb, build_contrib_text(clan, rows), kb)


@router.callback_query(F.data == "clanh:noop")
async def clan_hall_noop(cb: CallbackQuery):
    await cb.answer()
