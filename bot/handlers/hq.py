"""
Штаб ВВС: командование рассылает приказы авиакрыльям.

Вход — по праву can_send_orders (главнокомандование) или can_wing_commands
(командир авиакрыла). Кнопка «Штаб ВВС» появляется в городе у носителей этих
прав. Приказы от командира подписываются «ПРИКАЗ КОМАНДИРА <крыло>», от
командования — «ПРИКАЗ ШТАБА ВВС».
"""

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.db import (
    get_wing_members, get_all_users, get_user, set_wing,
    get_wing_commander, get_wing_commanders, get_wing_commander_by_user,
    set_wing_commander, add_user_role, remove_user_role,
)
from utils.permissions import has_permission, log_action
from utils.wings import WINGS, WINGS_SHORT, wing_display
from utils.notify import player_display
from keyboards.keyboards import cancel_keyboard

router = Router()


class HqOrder(StatesGroup):
    """Ожидание текста приказа. target в payload: 'all' или ключ крыла."""
    target = State()


def hq_menu_markup(roster_ok: bool = False, can_order: bool = True,
                   commander_ok: bool = False):
    rows = []
    if can_order:
        rows.append([InlineKeyboardButton(text="📢 Отправить приказ", callback_data="hq:send")])
    if commander_ok:
        rows.append([InlineKeyboardButton(text="📢 Приказ своему крылу", callback_data="hq:wingcmd_send")])
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
    can_order = await has_permission(callback.from_user.id, "can_send_orders")
    has_wing = await get_wing_commander_by_user(callback.from_user.id)
    can_cmd = bool(has_wing) and await has_permission(callback.from_user.id, "can_wing_commands")
    if not (can_order or can_cmd):
        await callback.message.answer("❌ Нет доступа к штабу ВВС.")
        return
    roster_ok = await has_permission(callback.from_user.id, "can_manage_wing")
    await callback.message.answer(
        "🎖️ ШТАБ ВВС\n\n"
        "Командный центр военно-воздушных сил Нордхайма.\n"
        "Здесь отдаются приказы авиакрыльям и комплектуется состав.",
        reply_markup=hq_menu_markup(roster_ok=roster_ok, can_order=can_order,
                                    commander_ok=can_cmd)
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
    can_send = await has_permission(message.from_user.id, "can_send_orders")
    can_cmd = await has_permission(message.from_user.id, "can_wing_commands")
    if not (can_send or can_cmd):
        await message.answer("❌ Нет доступа к штабу ВВС.")
        await state.clear()
        return
    data = await state.get_data()
    target = data.get('hq_target')
    text = message.text.strip()
    if not text:
        await message.answer("❌ Приказ не может быть пустым. Введи текст:")
        return

    commander_wing = await get_wing_commander_by_user(message.from_user.id)
    if commander_wing and not can_send:
        target = commander_wing
    if (commander_wing and target != "all" and commander_wing == target and can_cmd):
        header = f"🪖 ПРИКАЗ КОМАНДИРА {WINGS[target]}"
        signature = f"\n📝 — Командир {WINGS[target]}"
    else:
        header = "🎖️ ПРИКАЗ ШТАБА ВВС"
        signature = "\n📝 — Главнокомандующий ВВС"
    body = f"{header}\n\n{text}{signature}"

    members = await get_wing_members(None if target == "all" else target)
    sent = 0
    for uid in members:
        try:
            await message.bot.send_message(uid, body)
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
    commanders = await get_wing_commanders()
    lines = ["🪽 СОСТАВ ВВС\n"]
    for key, label in WINGS.items():
        lines.append(f"{label}: {grouped.get(key, 0)}")
    lines.append(f"Без крыла: {grouped.get('', 0)}")
    lines.append(f"\nВсего пилотов: {len(users)}\n")
    lines.append("🛡 Командиры крыльев:")
    for key, label in WINGS.items():
        uid = commanders.get(key)
        if uid:
            u = await get_user(uid)
            name = await player_display(u) if u else f"#{uid}"
        else:
            name = "— не назначен"
        lines.append(f"{WINGS_SHORT[key]}: {name}")
    await callback.message.answer(
        "\n".join(lines),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Выбрать пилота", callback_data="hq:roster:0")],
            [InlineKeyboardButton(text="🛡 Командиры крыльев", callback_data="hq:wingcmd")],
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
    await _pilot_picker(
        callback, page,
        page_base="hq:roster:", assign_prefix="hq:pilot", back="hq:wing",
        caption="🪽 Выбери пилота",
    )


async def _pilot_picker(callback: CallbackQuery, page: int, page_base: str,
                        assign_prefix: str, back: str, caption: str):
    """Пагинированный список пилотов для выбора (Состав ВВС / назначение командира)."""
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
            callback_data=f"{assign_prefix}:{u['user_id']}",
        )])
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="⬅️", callback_data=f"{page_base}{page - 1}"))
    nav.append(InlineKeyboardButton(text=f"{page + 1}/{pages}", callback_data="hq:noop"))
    if page < pages - 1:
        nav.append(InlineKeyboardButton(text="➡️", callback_data=f"{page_base}{page + 1}"))
    if nav:
        rows.append(nav)
    rows.append([InlineKeyboardButton(text="🔙 Назад", callback_data=back)])
    await callback.message.answer(
        f"{caption} ({total} всего):",
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


# ----- Командиры крыльев -----


@router.callback_query(F.data == "hq:wingcmd")
async def hq_wingcmd_cb(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_wing"):
        await callback.message.answer("❌ Нет доступа к составу ВВС.")
        return
    commanders = await get_wing_commanders()
    lines = ["🛡 КОМАНДИРЫ КРЫЛЬЕВ\n"]
    rows = []
    for key in WINGS:
        uid = commanders.get(key)
        if uid:
            u = await get_user(uid)
            name = await player_display(u) if u else f"#{uid}"
        else:
            name = "— не назначен"
        lines.append(f"{WINGS_SHORT[key]}: {name}")
        rows.append([InlineKeyboardButton(
            text=f"👨‍✈️ {WINGS_SHORT[key]} — назначить", callback_data=f"hq:wingcmd:pick:{key}:0"
        ),
            InlineKeyboardButton(
            text="➖ Снять", callback_data=f"hq:wingcmd:unset:{key}"
        )])
    rows.append([InlineKeyboardButton(text="🔙 В состав ВВС", callback_data="hq:wing")])
    await callback.message.answer(
        "\n".join(lines),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows)
    )


@router.callback_query(F.data.startswith("hq:wingcmd:pick:"))
async def hq_wingcmd_pick(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_wing"):
        await callback.message.answer("❌ Нет доступа к составу ВВС.")
        return
    parts = callback.data.split(":")
    wing = parts[3] if len(parts) >= 4 else ""
    if wing not in WINGS:
        return
    try:
        page = int(parts[4]) if len(parts) >= 5 else 0
    except ValueError:
        page = 0
    await _pilot_picker(
        callback, page,
        page_base=f"hq:wingcmd:pick:{wing}:",
        assign_prefix=f"hq:wingcmd:assign:{wing}",
        back="hq:wingcmd",
        caption=f"👨‍✈️ Командир для {WINGS_SHORT[wing]}",
    )


@router.callback_query(F.data.startswith("hq:wingcmd:assign:"))
async def hq_wingcmd_assign(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_wing"):
        await callback.message.answer("❌ Нет доступа к составу ВВС.")
        return
    parts = callback.data.split(":")
    if len(parts) < 5:
        return
    wing, uid_s = parts[3], parts[4]
    if wing not in WINGS:
        return
    try:
        uid = int(uid_s)
    except ValueError:
        return
    u = await get_user(uid)
    if not u:
        await callback.message.answer("❌ Пилот не найден.")
        return
    old_uid = await get_wing_commander(wing)
    await set_wing_commander(wing, uid)
    await add_user_role(uid, 'wing_commander', granted_by=callback.from_user.id)
    await set_wing(uid, wing)
    await log_action(callback.from_user.id, 'hq_set_wing_commander',
                     details=f"wing={wing}, commander={uid}")
    if old_uid and old_uid != uid:
        if not await get_wing_commander_by_user(old_uid):
            await remove_user_role(old_uid, 'wing_commander')
    await callback.message.answer(
        f"✅ Командир {WINGS_SHORT[wing]}: {await player_display(u)}"
    )


@router.callback_query(F.data.startswith("hq:wingcmd:unset:"))
async def hq_wingcmd_unset(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_wing"):
        await callback.message.answer("❌ Нет доступа к составу ВВС.")
        return
    parts = callback.data.split(":")
    wing = parts[3] if len(parts) >= 4 else ""
    if wing not in WINGS:
        return
    old_uid = await get_wing_commander(wing)
    if not old_uid:
        await callback.message.answer("ℹ️ У этого крыла уже нет командира.")
        return
    await set_wing_commander(wing)
    await log_action(callback.from_user.id, 'hq_unset_wing_commander',
                     details=f"wing={wing}, commander={old_uid}")
    if not await get_wing_commander_by_user(old_uid):
        await remove_user_role(old_uid, 'wing_commander')
    await callback.message.answer(f"✅ Командир снят с {WINGS_SHORT[wing]}.")


@router.callback_query(F.data == "hq:wingcmd_send")
async def hq_wingcmd_send_cb(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_wing_commands"):
        await callback.message.answer("❌ Нет доступа к штабу ВВС.")
        return
    wing = await get_wing_commander_by_user(callback.from_user.id)
    if not wing:
        await callback.message.answer("❌ Твоё крыло не назначено. Обратись в штаб.")
        return
    await state.update_data(hq_target=wing)
    await state.set_state(HqOrder.target)
    await callback.message.answer(
        f"📢 Приказ для крыла: {WINGS[wing]}\n\nВведи текст приказа:",
        reply_markup=cancel_keyboard()
    )