"""Админ-менеджер клановых лавок (Фаза 7).

Вход — из админ-панели (кнопка «🏪 Клановые лавки», право can_manage_clans).

Что умеет:
- выбрать клан → экран лавки: активные и скрытые позиции витрины;
- добавить товар: имя/ID предмета → цена НМ → остаток (-1 = ∞) → сохранить
  (`upsert_clan_shop_item`); так добавляется и «клановая накидка» —
  личный предмет каждого клана;
- карточка товара: правка цены/остатка, скрыть/показать, удалить;
- все правки мгновенны, витрина читается колбэками лавки на лету
  (инвалидов нет — покупается только активная позиция с остатком).

Суточный лимит покупок на пилота: `config.CLAN_SHOP_DAILY_LIMIT`
(0 = лимит отключён).
"""

import html

import config

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from database.db import (
    delete_clan_shop_item,
    get_clan,
    get_clans,
    get_clan_shop_bought_today,
    get_clan_shop_item,
    get_clan_shop_items,
    get_item,
    get_item_by_name,
    set_clan_shop_active,
    upsert_clan_shop_item,
)
from utils.permissions import has_permission

router = Router()

PAGE = 10


def _esc(text) -> str:
    return html.escape(str(text or ""))


class ClanShopAdmin(StatesGroup):
    wait_item = State()
    wait_price = State()
    wait_stock = State()
    edit_price = State()
    edit_stock = State()


async def _require(cb_or_msg) -> bool:
    uid = getattr(cb_or_msg, "from_user", None)
    uid = uid.id if uid else cb_or_msg.from_user.id
    return await has_permission(uid, "can_manage_clans")


async def _shop_screen(cb: CallbackQuery, clan):
    """Экран лавки выбранного клана: активные + скрытые позиции."""
    clan_id = int(clan["id"])
    rows_active = await get_clan_shop_items(clan_id, active_only=True)
    rows_hidden = await get_clan_shop_items(clan_id, active_only=False)
    rows_hidden = [r for r in rows_hidden if not r.get("is_active")]
    limit = int(getattr(config, "CLAN_SHOP_DAILY_LIMIT", 3) or 0)
    lines = [
        f"🏪 <b>Клановая лавка</b> — «{_esc(clan['name'])}»",
        f"Позиций в витрине: <b>{len(rows_active)}</b>"
        + (f" • скрыто: {len(rows_hidden)}" if rows_hidden else ""),
        f"Суточный лимит покупок: <b>{limit if limit > 0 else 'выкл (0)'}</b>",
        "",
    ]
    if not rows_active and not rows_hidden:
        lines.append("Витрина пуста. Добавь первый товар (или накидку клана).")
    if rows_active:
        lines.append("Активные:")
        for r in rows_active:
            stock = r.get("stock")
            stock_txt = "∞" if stock is None or int(stock) < 0 else str(int(stock))
            lines.append(f"  • {_esc(r['name'])} — 💰 {int(r['price'])} НМ, ост. {stock_txt}")
    if rows_hidden:
        lines.append("")
        lines.append("Скрытые:")
        for r in rows_hidden:
            lines.append(f"  • {_esc(r['name'])} (скрыт)")
    kb = []
    kb.append([InlineKeyboardButton(text="➕ Добавить товар",
                                    callback_data=f"clanshopadm:add:{clan_id}")])
    kb.append([InlineKeyboardButton(text="🔄 Обновить",
                                    callback_data=f"clanshopadm:clan:{clan_id}")])
    kb.append([InlineKeyboardButton(text="🔙 В админ-панель",
                                    callback_data="admin:menu")])
    await cb.message.edit_text("\n".join(lines),
                               parse_mode="HTML",
                               reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))


@router.callback_query(F.data == "clanshopadm:menu")
async def clanshopadm_menu_cb(cb: CallbackQuery):
    if not await _require(cb):
        await cb.answer("❌ Недостаточно прав.", show_alert=True)
        return
    await cb.answer()
    clans = [c for c in await get_clans("clan")]
    lines = [f"🏪 <b>Клановые лавки</b> — кланов: {len(clans)}", ""]
    kb = []
    for c in clans:
        kb.append([InlineKeyboardButton(
            text=f"🏪 {c['name']}",
            callback_data=f"clanshopadm:clan:{c['id']}")])
    kb.append([InlineKeyboardButton(text="🔙 В админ-панель", callback_data="admin:menu")])
    await cb.message.edit_text("\n".join(lines), parse_mode="HTML",
                               reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))


@router.callback_query(F.data.startswith("clanshopadm:clan:"))
async def clanshopadm_clan_cb(cb: CallbackQuery):
    if not await _require(cb):
        await cb.answer("❌ Недостаточно прав.", show_alert=True)
        return
    clan = await get_clan(int(cb.data.split(":")[2]))
    if not clan:
        await cb.answer("❌ Клан не найден.", show_alert=True)
        return
    await cb.answer()
    await _shop_screen(cb, clan)


@router.callback_query(F.data.startswith("clanshopadm:add:"))
async def clanshopadm_add_cb(cb: CallbackQuery, state: FSMContext):
    if not await _require(cb):
        await cb.answer("❌ Недостаточно прав.", show_alert=True)
        return
    clan_id = int(cb.data.split(":")[2])
    await cb.answer()
    await state.update_data(cs_clan_id=clan_id)
    await state.set_state(ClanShopAdmin.wait_item)
    await cb.message.edit_text(
        "➕ <b>Добавить товар в клановую лавку</b>\n\n"
        "Пришли название предмета (точное) или его числовой ID.\n"
        "Отмена: <i>отмена</i>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="🔙 Отмена",
                                 callback_data=f"clanshopadm:clan:{clan_id}"),
        ]]))


@router.message(ClanShopAdmin.wait_item, F.text)
async def clanshopadm_item_msg(message: Message, state: FSMContext):
    if not await has_permission(message.from_user.id, "can_manage_clans"):
        await state.clear()
        return
    text = (message.text or "").strip()
    if text.lower() in ("отмена", "cancel"):
        await state.clear()
        await message.answer("❌ Отменено.")
        return
    item = None
    if text.isdigit():
        item = await get_item(int(text))
    if not item:
        item = await get_item_by_name(text)
    data = await state.get_data()
    clan_id = int(data.get("cs_clan_id") or 0)
    clan = await get_clan(clan_id)
    if not item:
        await message.answer(
            f"❌ Предмет «{_esc(text)}» не найден (точное имя или ID). Попробуй ещё раз:")
        return
    await state.update_data(cs_item_id=int(item["id"]))
    await state.set_state(ClanShopAdmin.wait_price)
    await message.answer(
        f"🏪 <b>{_esc(item['name'])}</b>\n\n"
        f"Цена для членов клана, НМ (целое ≥ 1):",
        parse_mode="HTML")


@router.message(ClanShopAdmin.wait_price, F.text)
async def clanshopadm_price_msg(message: Message, state: FSMContext):
    if not await has_permission(message.from_user.id, "can_manage_clans"):
        await state.clear()
        return
    text = (message.text or "").strip()
    if not text.isdigit() or int(text) < 1:
        await message.answer("❌ Нужно целое число ≥ 1. Ещё раз:")
        return
    await state.update_data(cs_price=int(text))
    await state.set_state(ClanShopAdmin.wait_stock)
    await message.answer(
        f"💰 Цена: {int(text)} НМ.\n\n"
        "Остаток: целое число или −1 (∞):")


@router.message(ClanShopAdmin.wait_stock, F.text)
async def clanshopadm_stock_msg(message: Message, state: FSMContext):
    if not await has_permission(message.from_user.id, "can_manage_clans"):
        await state.clear()
        return
    text = (message.text or "").strip()
    if not text.lstrip("-").isdigit():
        await message.answer("❌ Нужно целое число или −1 (∞). Ещё раз:")
        return
    stock = int(text)
    if stock == 0:
        await message.answer("❌ Остаток 0 недопустим — 0 означало бы «распродано». "
                             "Возьми 1 или −1 (∞).")
        return
    data = await state.get_data()
    clan_id = int(data.get("cs_clan_id") or 0)
    item_id = int(data.get("cs_item_id") or 0)
    price = int(data.get("cs_price") or 1)
    item = await get_item(item_id)
    clan = await get_clan(clan_id)
    await upsert_clan_shop_item(clan_id, item_id, price, stock, is_active=True)
    await state.clear()
    who = await clan.get("name") if clan else f"#{clan_id}"
    await message.answer(
        f"✅ Добавлено в лавку «{_esc(who)}»: {_esc(item['name'] if item else item_id)} — "
        f"💰 {price} НМ, остаток {'∞' if stock < 0 else stock}.")
    if clan:
        await clanshopadm_clan_msg_refresh(message, clan)


async def clanshopadm_clan_msg_refresh(message: Message, clan):
    """Перерисовка экрана лавки как сообщение (после ввода значений FSM)."""
    clan_id = int(clan["id"])
    rows_active = await get_clan_shop_items(clan_id, active_only=True)
    rows_hidden = [r for r in await get_clan_shop_items(
        clan_id, active_only=False) if not r.get("is_active")]
    lines = [f"🏪 <b>Клановая лавка</b> — «{_esc(clan['name'])}»", ""]
    if not rows_active and not rows_hidden:
        lines.append("Витрина пуста.")
    if rows_active:
        lines.append("Активные:")
        for r in rows_active:
            stock = r.get("stock")
            stock_txt = "∞" if stock is None or int(stock) < 0 else str(int(stock))
            lines.append(f"  • {_esc(r['name'])} — 💰 {int(r['price'])} НМ, ост. {stock_txt}")
    if rows_hidden:
        lines.append("")
        lines.append("Скрытые:")
        for r in rows_hidden:
            lines.append(f"  • {_esc(r['name'])} (скрыт)")
    kb = [[InlineKeyboardButton(text="➕ Добавить товар",
                                callback_data=f"clanshopadm:add:{clan_id}")],
          [InlineKeyboardButton(text="🔙 В админ-панель", callback_data="admin:menu")]]
    await message.answer("\n".join(lines), parse_mode="HTML",
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))


@router.callback_query(F.data.startswith("clanshopadm:it:"))
async def clanshopadm_item_card_cb(cb: CallbackQuery, state: FSMContext):
    if not await _require(cb):
        await cb.answer("❌ Недостаточно прав.", show_alert=True)
        return
    parts = cb.data.split(":")
    clan_id = int(parts[2])
    item_id = int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else 0
    clan = await get_clan(clan_id)
    item = await get_clan_shop_item(clan_id, item_id)
    if not clan or not item:
        await cb.answer("❌ Позиция не найдена.", show_alert=True)
        return
    await cb.answer()
    stock = item.get("stock")
    stock_txt = "∞" if stock is None or int(stock) < 0 else str(int(stock))
    status_txt = "активен" if item.get("is_active") else "скрыт"
    rows = [
        [InlineKeyboardButton(text="💰 Цена", callback_data=f"clanshopadm:ep:{clan_id}:{item_id}"),
         InlineKeyboardButton(text="📦 Остаток", callback_data=f"clanshopadm:es:{clan_id}:{item_id}")],
    ]
    if item.get("is_active"):
        rows.append([InlineKeyboardButton(text="🙈 Скрыть",
                                          callback_data=f"clanshopadm:hide:{clan_id}:{item_id}")])
    else:
        rows.append([InlineKeyboardButton(text="👁 Показать",
                                          callback_data=f"clanshopadm:show:{clan_id}:{item_id}")])
    rows.append([InlineKeyboardButton(text="🗑 Удалить",
                                      callback_data=f"clanshopadm:del:{clan_id}:{item_id}")])
    rows.append([InlineKeyboardButton(text="🔙 В лавку", callback_data=f"clanshopadm:clan:{clan_id}")])
    text = (f"🛒 <b>{_esc(item['name'])}</b> — «{_esc(clan['name'])}»\n"
            f"💰 Цена: {int(item['price'])} НМ • 📦 Остаток: {stock_txt} • {status_txt}\n\n"
            f"{_esc(item['description'] or '')}")
    try:
        await cb.message.edit_text(text, parse_mode="HTML",
                                   reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))
    except Exception:
        await cb.message.answer(text, parse_mode="HTML",
                                reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))


@router.callback_query(F.data.startswith("clanshopadm:ep:"))
async def clanshopadm_edit_price_cb(cb: CallbackQuery, state: FSMContext):
    if not await _require(cb):
        await cb.answer("❌ Недостаточно прав.", show_alert=True)
        return
    parts = cb.data.split(":")
    clan_id, item_id = int(parts[2]), int(parts[3])
    await cb.answer()
    await state.update_data(cs_clan_id=clan_id, cs_item_id=item_id)
    await state.set_state(ClanShopAdmin.edit_price)
    await cb.message.answer("💰 Новая цена (целое ≥ 1). Отмена: <i>отмена</i>",
                            parse_mode="HTML")


@router.message(ClanShopAdmin.edit_price, F.text)
async def clanshopadm_edit_price_msg(message: Message, state: FSMContext):
    if not await has_permission(message.from_user.id, "can_manage_clans"):
        await state.clear()
        return
    text = (message.text or "").strip()
    if not text.isdigit() or int(text) < 1:
        await message.answer("❌ Нужно целое число ≥ 1. Ещё раз:")
        return
    data = await state.get_data()
    clan_id = int(data.get("cs_clan_id") or 0)
    item_id = int(data.get("cs_item_id") or 0)
    item = await get_clan_shop_item(clan_id, item_id)
    stock = int(item["stock"]) if item and item.get("stock") is not None else -1
    await upsert_clan_shop_item(clan_id, item_id, int(text), stock,
                                bool(item and item.get("is_active")))
    await state.clear()
    await message.answer(f"✅ Цена обновлена: {int(text)} НМ.")


@router.callback_query(F.data.startswith("clanshopadm:es:"))
async def clanshopadm_edit_stock_cb(cb: CallbackQuery, state: FSMContext):
    if not await _require(cb):
        await cb.answer("❌ Недостаточно прав.", show_alert=True)
        return
    parts = cb.data.split(":")
    clan_id, item_id = int(parts[2]), int(parts[3])
    await cb.answer()
    await state.update_data(cs_clan_id=clan_id, cs_item_id=item_id)
    await state.set_state(ClanShopAdmin.edit_stock)
    await cb.message.answer("📦 Новый остаток (целое ≥ 1 или −1 = ∞). Отмена: <i>отмена</i>",
                            parse_mode="HTML")


@router.message(ClanShopAdmin.edit_stock, F.text)
async def clanshopadm_edit_stock_msg(message: Message, state: FSMContext):
    if not await has_permission(message.from_user.id, "can_manage_clans"):
        await state.clear()
        return
    text = (message.text or "").strip()
    if not text.lstrip("-").isdigit():
        await message.answer("❌ Нужно целое число или −1 (∞). Ещё раз:")
        return
    stock = int(text)
    if stock == 0:
        await message.answer("❌ 0 недопустим — возьми 1 или −1 (∞).")
        return
    data = await state.get_data()
    clan_id = int(data.get("cs_clan_id") or 0)
    item_id = int(data.get("cs_item_id") or 0)
    item = await get_clan_shop_item(clan_id, item_id)
    await upsert_clan_shop_item(clan_id, item_id, int(item["price"]), stock,
                                bool(item and item.get("is_active")))
    await state.clear()
    await message.answer(f"✅ Остаток обновлён: {'∞' if stock < 0 else stock}.")


@router.callback_query(F.data.startswith("clanshopadm:hide:"))
async def clanshopadm_hide_cb(cb: CallbackQuery):
    if not await _require(cb):
        await cb.answer("❌ Недостаточно прав.", show_alert=True)
        return
    parts = cb.data.split(":")
    clan_id, item_id = int(parts[2]), int(parts[3])
    await set_clan_shop_active(clan_id, item_id, False)
    await cb.answer("🙈 Товар скрыт.", show_alert=True)
    clan = await get_clan(clan_id)
    if clan:
        await _shop_screen(cb, clan)


@router.callback_query(F.data.startswith("clanshopadm:show:"))
async def clanshopadm_show_cb(cb: CallbackQuery):
    if not await _require(cb):
        await cb.answer("❌ Недостаточно прав.", show_alert=True)
        return
    parts = cb.data.split(":")
    clan_id, item_id = int(parts[2]), int(parts[3])
    await set_clan_shop_active(clan_id, item_id, True)
    await cb.answer("👁 Товар в витрине.", show_alert=True)
    clan = await get_clan(clan_id)
    if clan:
        await _shop_screen(cb, clan)


@router.callback_query(F.data.startswith("clanshopadm:del:"))
async def clanshopadm_del_cb(cb: CallbackQuery):
    if not await _require(cb):
        await cb.answer("❌ Недостаточно прав.", show_alert=True)
        return
    parts = cb.data.split(":")
    clan_id, item_id = int(parts[2]), int(parts[3])
    await delete_clan_shop_item(clan_id, item_id)
    await cb.answer("🗑 Позиция удалена.", show_alert=True)
    clan = await get_clan(clan_id)
    if clan:
        await _shop_screen(cb, clan)
    else:
        await cb.message.answer("\n🏪 Выбери лавку:", reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(
                text="🔙 В админ-панель", callback_data="admin:menu")]]))
