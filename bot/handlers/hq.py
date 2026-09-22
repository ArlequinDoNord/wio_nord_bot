"""
Штаб ВВС: командование рассылает приказы авиакрыльям.

Вход — по праву can_send_orders (см. utils/permissions.py). Кнопка «Штаб ВВС»
появляется в городе только у тех, у кого это право есть.
"""

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.db import get_wing_members, get_all_users, get_user, set_wing
from utils.permissions import has_permission, log_action
from utils.wings import WINGS, wing_display
from utils.notify import player_display
from keyboards.keyboards import cancel_keyboard

router = Router()


class HqOrder(StatesGroup):
    """Ожидание текста приказа. target в payload: 'all' или ключ крыла."""
    target = State()


def hq_menu_markup(roster_ok: bool = False):
    rows = [[InlineKeyboardButton(text="📢 Отправить приказ", callback_data="hq:send")]]
    if roster_ok:
        rows.append([InlineKeyboardButton(text="🪽 Состав ВВС", callback_data="hq:wing")])
    rows.append([InlineKeyboardButton(text="🏠 В меню города", callback_data="city:menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


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
    roster_ok = await has_permission(callback.from_user.id, "can_manage_wing")
    await callback.message.answer(
        "🎖️ ШТАБ ВВС\n\n"
        "Командный центр военно-воздушных сил Нордхайма.\n"
        "Здесь отдаются приказы авиакрыльям и комплектуется состав.",
        reply_markup=hq_menu_markup(roster_ok)
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


# ----- Состав ВВС -----

ROSTER_PAGE_SIZE = 12


@router.callback_query(F.data == "hq:wing")
async def hq_wing_cb(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_wing"):
        await callback.message.answer("❌ Нет доступа к составу ВВС.")
        return
    users = await get_all_users()
    grouped = {"1": 0, "2": 0, "3": 0, "": 0}
    for u in users:
        wing = u['wing'] if 'wing' in u.keys() and u['wing'] else ""
        grouped[wing] = grouped.get(wing, 0) + 1
    lines = ["🪽 СОСТАВ ВВС\n"]
    for key, label in WINGS.items():
        lines.append(f"{label}: {grouped.get(key, 0)}")
    lines.append(f"Без крыла: {grouped.get('', 0)}")
    lines.append(f"\nВсего пилотов: {len(users)}")
    await callback.message.answer(
        "\n".join(lines),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Выбрать пилота", callback_data="hq:roster:0")],
            [InlineKeyboardButton(text="🔙 Назад в штаб", callback_data="hq:menu")],
        ])
    )


@router.callback_query(F.data.startswith("hq:roster:"))
async def hq_roster_pick(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_wing"):
        await callback.message.answer("❌ Нет доступа к составу ВВС.")
        return
    try:
        page = int(callback.data.split(":", 2)[2])
    except (ValueError, IndexError):
        page = 0
    users = sorted(await get_all_users(), key=lambda u: u['user_id'])
    total = len(users)
    pages = max(1, (total + ROSTER_PAGE_SIZE - 1) // ROSTER_PAGE_SIZE)
    page = max(0, min(page, pages - 1))
    chunk = users[page * ROSTER_PAGE_SIZE:(page + 1) * ROSTER_PAGE_SIZE]
    rows = []
    for u in chunk:
        wing = u['wing'] if 'wing' in u.keys() and u['wing'] else None
        rows.append([InlineKeyboardButton(
            text=f"{await player_display(u)} — {wing_display(wing)}",
            callback_data=f"hq:pilot:{u['user_id']}",
        )])
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="⬅️", callback_data=f"hq:roster:{page - 1}"))
    nav.append(InlineKeyboardButton(text=f"{page + 1}/{pages}", callback_data="hq:noop"))
    if page < pages - 1:
        nav.append(InlineKeyboardButton(text="➡️", callback_data=f"hq:roster:{page + 1}"))
    if nav:
        rows.append(nav)
    rows.append([InlineKeyboardButton(text="🔙 В состав ВВС", callback_data="hq:wing")])
    await callback.message.answer(
        f"🪽 Выбери пилота ({total} всего):",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows)
    )


@router.callback_query(F.data.startswith("hq:pilot:"))
async def hq_pilot_cb(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_wing"):
        await callback.message.answer("❌ Нет доступа к составу ВВС.")
        return
    try:
        uid = int(callback.data.split(":", 2)[2])
    except (ValueError, IndexError):
        return
    u = await get_user(uid)
    if not u:
        await callback.message.answer("❌ Пилот не найден.")
        return
    rows = []
    for key, label in WINGS.items():
        rows.append([InlineKeyboardButton(text=label, callback_data=f"hq:wing:set:{uid}:{key}")])
    rows.append([InlineKeyboardButton(text="➖ Снять крыло", callback_data=f"hq:wing:set:{uid}:none")])
    rows.append([InlineKeyboardButton(text="🔙 К списку", callback_data="hq:roster:0")])
    current_wing = u['wing'] if 'wing' in u.keys() else None
    await callback.message.answer(
        f"🪽 Авиакрыло для {await player_display(u)}\n\n"
        f"Текущее: {wing_display(current_wing)}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows)
    )


@router.callback_query(F.data.startswith("hq:wing:set:"))
async def hq_wingset(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_wing"):
        await callback.message.answer("❌ Нет доступа к составу ВВС.")
        return
    parts = callback.data.split(":")
    if len(parts) < 5:
        return
    wing = parts[4]
    try:
        uid = int(parts[3])
    except ValueError:
        return
    wing = None if wing == "none" else wing
    if wing is not None and wing not in WINGS:
        return
    await set_wing(uid, wing)
    await log_action(callback.from_user.id, 'hq_set_wing', details=f"pilot={uid}, wing={wing}")
    u = await get_user(uid)
    await callback.message.answer(
        f"✅ Крыло пилота {await player_display(u)}: {wing_display(wing)}"
    )


@router.callback_query(F.data == "hq:noop")
async def hq_noop_cb(callback: CallbackQuery):
    await callback.answer()