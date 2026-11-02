# -*- coding: utf-8 -*-
"""Админ-редактор ягод леса по зонам (как грибы): шанс, добавить, убрать, создать.

Шансы — в %. Остаток до 100% — «пусто». Медведь (ref=bear) — это встреча, а не предмет.
"""

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton

import database.db as db
from keyboards.keyboards import cancel_keyboard
from utils.permissions import has_permission

router = Router()

AREA_TITLE = {"glade": "🌿 Опушка", "clearing": "🌲 Прогалина"}


class BerryAdmin(StatesGroup):
    chance = State()
    c_name = State()
    c_sell = State()
    c_chance = State()


async def _allowed(cb) -> bool:
    return await has_permission(cb.from_user.id, "can_manage_locations")


async def _zone_card(callback: CallbackQuery, area: str, prefix: str = ""):
    pool = await db.get_berry_pool(area)
    total = sum(r["chance"] for r in pool)
    lines = [f"{prefix}🫐 Ягоды зоны: {AREA_TITLE.get(area, area)}\n",
             "Шанс — в %, остаток до 100% — пусто.\n"]
    rows = []
    for r in pool:
        lines.append(f"• {r['name']} — {r['chance']}%")
        rows.append([InlineKeyboardButton(text=f"{r['name']} — {r['chance']}%",
                                          callback_data=f"berry:row:{area}:{r['ref']}")])
    if not pool:
        lines.append("Ягод в зоне пока нет.")
    lines.append(f"\nВсего: {total}% (пусто: {max(0, 100 - total)}%)")
    if total > 100:
        lines.append("⚠️ Сумма больше 100% — последние по списку не выпадут.")
    rows.append([InlineKeyboardButton(text="➕ Добавить из списка", callback_data=f"berry:add:{area}")])
    rows.append([InlineKeyboardButton(text="✨ Создать ягоду", callback_data=f"berry:new:{area}")])
    rows.append([InlineKeyboardButton(text="🔙 К зоне леса", callback_data=f"forest:zone:{area}")])
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    await callback.message.edit_text("\n".join(lines), reply_markup=markup)


@router.callback_query(F.data.regexp(r"^berry:zone:(glade|clearing)$"))
async def berry_zone(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await _allowed(callback):
        return
    await state.clear()
    await _zone_card(callback, callback.data.split(":")[2])


@router.callback_query(F.data.regexp(r"^berry:row:(glade|clearing):.+$"))
async def berry_row(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await _allowed(callback):
        return
    _, _, area, ref = callback.data.split(":", 3)
    row = next((r for r in await db.get_berry_pool(area) if r["ref"] == ref), None)
    if not row:
        await callback.message.answer("❌ Ягода не найдена в зоне.")
        return
    rows = [
        [InlineKeyboardButton(text="🎲 Шанс", callback_data=f"berry:chance:{area}:{ref}")],
        [InlineKeyboardButton(text="🗑 Убрать из зоны", callback_data=f"berry:del:{area}:{ref}")],
        [InlineKeyboardButton(text="🔙 К ягодам зоны", callback_data=f"berry:zone:{area}")],
    ]
    await callback.message.edit_text(
        f"🫐 {row['name']} — {AREA_TITLE.get(area, area)}\nШанс: {row['chance']}%",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))


@router.callback_query(F.data.regexp(r"^berry:chance:(glade|clearing):.+$"))
async def berry_chance(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await _allowed(callback):
        return
    _, _, area, ref = callback.data.split(":", 3)
    await state.set_state(BerryAdmin.chance)
    await state.update_data(area=area, ref=ref)
    await callback.message.answer("🎲 Введи шанс в % (целое число 0–100):",
                                  reply_markup=cancel_keyboard())


@router.message(BerryAdmin.chance)
async def berry_chance_msg(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    if not text.isdigit() or int(text) > 100:
        await message.answer("❌ Введи целое число от 0 до 100.", reply_markup=cancel_keyboard())
        return
    data = await state.get_data()
    await state.clear()
    await db.set_berry_chance(data["area"], data["ref"], int(text))
    await message.answer(f"✅ Шанс сохранён: {text}%.")


@router.callback_query(F.data.regexp(r"^berry:del:(glade|clearing):.+$"))
async def berry_del(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await _allowed(callback):
        return
    _, _, area, ref = callback.data.split(":", 3)
    await db.remove_berry_from_zone(area, ref)
    await _zone_card(callback, area, prefix="🗑 Убрано из зоны.\n\n")


@router.callback_query(F.data.regexp(r"^berry:add:(glade|clearing)$"))
async def berry_add(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await _allowed(callback):
        return
    area = callback.data.split(":")[2]
    cands = await db.get_berry_candidates(area)
    rows = [[InlineKeyboardButton(text=f"{c['name']} (продажа {c['sell_price']} НМ)",
                                  callback_data=f"berry:pick:{area}:{c['id']}")]
            for c in cands[:30]]
    lines = [f"➕ Ягода в зону: {AREA_TITLE.get(area, area)}\n"]
    if not cands:
        lines.append("Подходящих ресурсов нет. Создай новую ягоду.")
    rows.append([InlineKeyboardButton(text="🔙 К ягодам зоны", callback_data=f"berry:zone:{area}")])
    await callback.message.edit_text("\n".join(lines),
                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))


@router.callback_query(F.data.regexp(r"^berry:pick:(glade|clearing):\d+$"))
async def berry_pick(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await _allowed(callback):
        return
    _, _, area, item_id = callback.data.split(":")
    item = await db.get_item(int(item_id))
    if not item:
        await callback.message.answer("❌ Предмет не найден.")
        return
    await db.add_berry_to_zone(area, int(item_id), 5)
    await _zone_card(callback, area, prefix=f"✅ «{item['name']}» добавлена (5%, поменяй при нужде).\n\n")


@router.callback_query(F.data.regexp(r"^berry:new:(glade|clearing)$"))
async def berry_new(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await _allowed(callback):
        return
    area = callback.data.split(":")[2]
    await state.clear()
    await state.update_data(area=area)
    await state.set_state(BerryAdmin.c_name)
    await callback.message.answer("✨ Новая ягода.\nШаг 1/3 — название (например «Горсть брусники»):",
                                  reply_markup=cancel_keyboard())


@router.message(BerryAdmin.c_name)
async def berry_new_name(message: Message, state: FSMContext):
    name = (message.text or "").strip()
    if not name or len(name) > 60:
        await message.answer("❌ Название — от 1 до 60 символов.", reply_markup=cancel_keyboard())
        return
    await state.update_data(c_name=name)
    await state.set_state(BerryAdmin.c_sell)
    await message.answer("Шаг 2/3 — цена продажи скупщику, Нордмарок (целое число ≥ 0):",
                         reply_markup=cancel_keyboard())


@router.message(BerryAdmin.c_sell)
async def berry_new_sell(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    if not text.isdigit():
        await message.answer("❌ Введи целое число ≥ 0.", reply_markup=cancel_keyboard())
        return
    await state.update_data(c_sell=int(text))
    await state.set_state(BerryAdmin.c_chance)
    await message.answer("Шаг 3/3 — шанс в % (целое число 0–100):", reply_markup=cancel_keyboard())


@router.message(BerryAdmin.c_chance)
async def berry_new_chance(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    if not text.isdigit() or int(text) > 100:
        await message.answer("❌ Введи целое число от 0 до 100.", reply_markup=cancel_keyboard())
        return
    data = await state.get_data()
    await state.clear()
    fid = await db.create_berry_item(data["area"], data["c_name"], data["c_sell"], int(text),
                                     added_by=message.from_user.id)
    if not fid:
        await message.answer("⚠️ Предмет с таким названием уже есть.")
        return
    await message.answer(f"✅ Ягода «{data['c_name']}» создана и добавлена в зону.")
