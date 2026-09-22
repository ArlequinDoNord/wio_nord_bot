"""
Штаб ВВС: командование рассылает приказы авиакрыльям.

Вход — по праву can_send_orders (см. utils/permissions.py). Кнопка «Штаб ВВС»
появляется в городе только у тех, у кого это право есть.
"""

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.db import get_wing_members
from utils.permissions import has_permission, log_action
from utils.wings import WINGS
from keyboards.keyboards import cancel_keyboard

router = Router()


class HqOrder(StatesGroup):
    """Ожидание текста приказа. target в payload: 'all' или ключ крыла."""
    target = State()


def hq_menu_markup():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Отправить приказ", callback_data="hq:send")],
        [InlineKeyboardButton(text="🏠 В меню города", callback_data="city:menu")],
    ])


def hq_target_markup():
    rows = [[InlineKeyboardButton(text="🌍 Всем авиакрыльям", callback_data="hq:order:all")]]
    for key, label in WINGS.items():
        rows.append([InlineKeyboardButton(text=label, callback_data=f"hq:order:{key}")])
    rows.append([InlineKeyboardButton(text="🔙 Назад в штаб", callback_data="hq:menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


@router.callback_query(F.data == "hq:menu")
async def hq_menu_cb(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    if not await has_permission(callback.from_user.id, "can_send_orders"):
        await callback.message.answer("❌ Нет доступа к штабу ВВС.")
        return
    await callback.message.answer(
        "🎖️ ШТАБ ВВС\n\n"
        "Командный центр военно-воздушных сил Нордхайма.\n"
        "Здесь отдаются приказы авиакрыльям.",
        reply_markup=hq_menu_markup()
    )


@router.callback_query(F.data == "hq:send")
async def hq_send_cb(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_send_orders"):
        await callback.message.answer("❌ Нет доступа к штабу ВВС.")
        return
    await callback.message.answer(
        "📢 Кому направить приказ?",
        reply_markup=hq_target_markup()
    )


@router.callback_query(F.data.startswith("hq:order:"))
async def hq_order_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_send_orders"):
        await callback.message.answer("❌ Нет доступа к штабу ВВС.")
        return
    _, _, target = callback.data.split(":", 2)
    await state.update_data(hq_target=target)
    await state.set_state(HqOrder.target)
    scope = "все авиакрылья" if target == "all" else WINGS.get(target, "крыло")
    await callback.message.answer(
        f"📢 Приказ для: {scope}\n\nВведи текст приказа:",
        reply_markup=cancel_keyboard()
    )


@router.message(HqOrder.target)
async def hq_order_text(message: Message, state: FSMContext):
    if not await has_permission(message.from_user.id, "can_send_orders"):
        await message.answer("❌ Нет доступа к штабу ВВС.")
        await state.clear()
        return
    data = await state.get_data()
    target = data.get('hq_target')
    text = message.text.strip()
    if not text:
        await message.answer("❌ Приказ не может быть пустым. Введи текст:")
        return

    members = await get_wing_members(None if target == "all" else target)
    sent = 0
    for uid in members:
        try:
            await message.bot.send_message(
                uid,
                f"🎖️ ПРИКАЗ ШТАБА ВВС\n\n{text}"
            )
            sent += 1
        except Exception:
            pass

    scope = "все авиакрылья" if target == "all" else WINGS.get(target, "крыло")
    await log_action(message.from_user.id, 'hq_order', details=f"target={target}, sent={sent}")
    await state.clear()
    noun = "пилот" if sent == 1 else ("пилота" if 2 <= sent <= 4 else "пилотов")
    await message.answer(f"✅ Приказ отправлен {sent} {noun} ({scope}).")