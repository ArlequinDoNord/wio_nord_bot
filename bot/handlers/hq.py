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
    get_wing_deputy, get_wing_deputies, get_wing_deputy_by_user, set_wing_deputy,
    get_wing_staff_wing, get_wing_staff_role, count_unassigned_pilots,
    get_unassigned_pilots, get_wing_member_rows, count_wing_members,
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
                   commander_ok: bool = False, wing_manage_ok: bool = False,
                   wing: str = None):
    rows = []
    if can_order:
        rows.append([InlineKeyboardButton(text="📢 Отправить приказ", callback_data="hq:send")])
    if commander_ok:
        rows.append([InlineKeyboardButton(text="📢 Приказ своему крылу", callback_data="hq:wingcmd_send")])
    if wing_manage_ok and wing:
        rows.append([
            InlineKeyboardButton(text="➕ Взять пилота", callback_data="hq:wingtake:0"),
            InlineKeyboardButton(text="➖ Убрать из крыла", callback_data="hq:wingdrop:0"),
        ])
        rows.append([InlineKeyboardButton(text="🛡 Заместитель",
                                          callback_data=f"hq:wingdep:{wing}")])
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


async def hq_menu_show(msg, user_id: int):
    """Показать меню штаба (используется из hq:menu и входа в локацию «Штаб ВВС»).
    msg — Message или CallbackQuery.message."""
    can_order = await has_permission(user_id, "can_send_orders")
    has_wing = await get_wing_staff_wing(user_id)
    can_cmd = bool(has_wing) and await has_permission(user_id, "can_wing_commands")
    if not (can_order or can_cmd):
        await msg.answer("❌ Нет доступа к штабу ВВС.")
        return False
    roster_ok = await has_permission(user_id, "can_manage_wing")
    # Составом своего крыла управляет только командир; штаб работает через «Состав ВВС».
    commander_wing = await get_wing_commander_by_user(user_id)
    wing_manage_ok = commander_wing is not None
    await msg.answer(
        "🎖️ ШТАБ ВВС\n\n"
        "Командный центр военно-воздушных сил Нордхайма.\n"
        "Здесь отдаются приказы авиакрыльям и комплектуется состав.",
        reply_markup=hq_menu_markup(roster_ok=roster_ok, can_order=can_order,
                                    commander_ok=can_cmd, wing_manage_ok=wing_manage_ok,
                                    wing=commander_wing)
    )
    return True


@router.callback_query(F.data == "hq:menu")
async def hq_menu_cb(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await hq_menu_show(callback.message, callback.from_user.id)


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

    staff_wing = await get_wing_staff_wing(message.from_user.id)
    if staff_wing and not can_send:
        target = staff_wing
    if (staff_wing and target != "all" and staff_wing == target and can_cmd):
        role = await get_wing_staff_role(message.from_user.id)
        if role == 'deputy':
            header = f"🪖 ПРИКАЗ ЗАМЕСТИТЕЛЯ КОМАНДИРА {WINGS[target]}"
            signature = f"\n📝 — Заместитель командира {WINGS_SHORT[target]}"
        else:
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
    deputies = await get_wing_deputies()
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
    lines.append("\n🎖️ Заместители:")
    for key, label in WINGS.items():
        uid = deputies.get(key)
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
                        assign_prefix: str, back: str, caption: str,
                        users: list = None):
    """Пагинированный список пилотов для выбора (Состав ВВС / назначение командира).

    users=None — все пилоты; иначе готовый список строк (например, только свободные
    или только пилоты своего крыла).
    """
    if users is None:
        users = await get_all_users()
    users = sorted(users, key=lambda u: u['user_id'])
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
    deputies = await get_wing_deputies()
    lines = ["🛡 КОМАНДИРЫ И ЗАМЕСТИТЕЛИ КРЫЛЬЕВ\n"]
    rows = []
    for key in WINGS:
        uid = commanders.get(key)
        if uid:
            u = await get_user(uid)
            name = await player_display(u) if u else f"#{uid}"
        else:
            name = "— не назначен"
        lines.append(f"{WINGS_SHORT[key]}: {name}")
        dep_uid = deputies.get(key)
        if dep_uid:
            du = await get_user(dep_uid)
            dep_name = await player_display(du) if du else f"#{dep_uid}"
        else:
            dep_name = "— не назначен"
        lines.append(f"   заместитель: {dep_name}")
        rows.append([InlineKeyboardButton(
            text=f"👨‍✈️ {WINGS_SHORT[key]} — командир", callback_data=f"hq:wingcmd:pick:{key}:0"
        ),
            InlineKeyboardButton(
            text="➖ Снять", callback_data=f"hq:wingcmd:unset:{key}"
        )])
        rows.append([InlineKeyboardButton(
            text=f"🎖️ {WINGS_SHORT[key]} — заместитель", callback_data=f"hq:wingdep:{key}"
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
    old_dep = await get_wing_deputy(wing)
    await set_wing_commander(wing, uid)
    await add_user_role(uid, 'wing_commander', granted_by=callback.from_user.id)
    await set_wing(uid, wing)
    # Назначенный командиром бывший заместитель теряет пост (и роль, если других нет).
    if old_dep == uid:
        await set_wing_deputy(wing)
        if not await get_wing_staff_wing(uid):
            await remove_user_role(uid, 'wing_deputy')
    await log_action(callback.from_user.id, 'hq_set_wing_commander',
                     details=f"wing={wing}, commander={uid}")
    if old_uid and old_uid != uid:
        if not await get_wing_staff_wing(old_uid):
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
    # Командир остаётся в крылу и может быть назначен заместителем.
    if not await get_wing_staff_wing(old_uid):
        await remove_user_role(old_uid, 'wing_commander')
    await callback.message.answer(
        f"✅ Командир снят с {WINGS_SHORT[wing]}."
        + ("" if await get_wing_deputy(wing) == old_uid
           else f" {await player_display(await get_user(old_uid))} остаётся в составе крыла.")
    )


@router.callback_query(F.data == "hq:wingcmd_send")
async def hq_wingcmd_send_cb(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_wing_commands"):
        await callback.message.answer("❌ Нет доступа к штабу ВВС.")
        return
    wing = await get_wing_staff_wing(callback.from_user.id)
    if not wing:
        await callback.message.answer("❌ Твоё крыло не назначено. Обратись в штаб.")
        return
    await state.update_data(hq_target=wing)
    await state.set_state(HqOrder.target)
    await callback.message.answer(
        f"📢 Приказ для крыла: {WINGS[wing]}\n\nВведи текст приказа:",
        reply_markup=cancel_keyboard()
    )
# ----- Состав своего крыла: командир берёт и убирает пилотов -----
# Командир управляет ТОЛЬКО своим крылом и ТОЛЬКО пилотами, ещё нигде не зачисленными:
# перебрасывать чужих пилотов между крыльями может штаб (can_manage_wing).
#
# Формат callback_data (однозначный, без пересечений префиксов):
#   hq:wingtake:{page}            — список свободных пилотов
#   hq:wingtake:do:{wing}:{uid}   — взять пилота в крыло
#   hq:wingdrop:{page}            — список пилотов своего крыла
#   hq:wingdrop:do:{wing}:{uid}   — убрать пилота из крыла
#   hq:wingdep:{wing}             — экран заместителя
#   hq:wingdep:{wing}:list:{page} — выбор заместителя из состава
#   hq:wingdep:{wing}:set:{uid}   — назначить заместителем
#   hq:wingdep:{wing}:unset       — снять заместителя


async def _commander_wing(user_id: int):
    """Крыло, которым пользователь командует как командир (или None)."""
    return await get_wing_commander_by_user(user_id)


def _is_free_pilot(user) -> bool:
    """Пилот ещё не зачислен ни в одно крыло."""
    wing = user['wing'] if 'wing' in user.keys() and user['wing'] else ""
    return wing in ("", "none", None)


def _hq_back_rows(*buttons):
    return InlineKeyboardMarkup(inline_keyboard=list(buttons))


@router.callback_query(F.data.startswith("hq:wingtake:"))
async def hq_wing_take_cb(callback: CallbackQuery):
    """Взять свободного пилота в своё крыло (или показать список таких)."""
    await callback.answer()
    wing = await _commander_wing(callback.from_user.id)
    if not wing:
        await callback.message.answer("❌ Ты не командир авиакрыла.")
        return
    parts = callback.data.split(":")

    if parts[2] == "do":
        if len(parts) < 5 or parts[3] != wing:
            return
        try:
            uid = int(parts[4])
        except ValueError:
            return
        u = await get_user(uid)
        if not u:
            await callback.message.answer("❌ Пилот не найден.")
            return
        # Повторная проверка: пока пилот свободен, он в списке остаётся.
        if not _is_free_pilot(u):
            await callback.message.answer(
                f"⚠️ {await player_display(u)} уже в {wing_display(u['wing'])} — "
                f"командир берёт только свободных пилотов. Переводы — через штаб."
            )
            return
        await set_wing(uid, wing)
        await log_action(callback.from_user.id, 'hq_wing_take_pilot',
                         details=f"pilot={uid}, wing={wing}")
        await callback.message.answer(
            f"✅ {await player_display(u)} принят в {WINGS[wing]}.\n"
            f"Теперь он получает приказы твоего крыла.",
            reply_markup=_hq_back_rows(
                [InlineKeyboardButton(text="➕ Взять ещё", callback_data="hq:wingtake:0")],
                [InlineKeyboardButton(text="🔙 В штаб", callback_data="hq:menu")],
            )
        )
        return

    try:
        page = int(parts[2])
    except ValueError:
        page = 0
    free = await get_unassigned_pilots()
    if not free:
        await callback.message.answer(
            f"✅ Свободных пилотов нет — все уже в крыльях.\n"
            f"Состав {WINGS_SHORT[wing]}: {await count_wing_members(wing)}",
            reply_markup=_hq_back_rows(
                [InlineKeyboardButton(text="➖ Убрать из крыла", callback_data="hq:wingdrop:0")],
                [InlineKeyboardButton(text="🔙 В штаб", callback_data="hq:menu")],
            )
        )
        return
    await _pilot_picker(
        callback, page,
        page_base="hq:wingtake:",
        assign_prefix=f"hq:wingtake:do:{wing}",
        back="hq:menu",
        caption=f"➕ Кого взять в {WINGS[wing]}?",
        users=free,
    )


@router.callback_query(F.data.startswith("hq:wingdrop:"))
async def hq_wing_drop_cb(callback: CallbackQuery):
    """Убрать пилота из своего крыла (или показать состав своего крыла)."""
    await callback.answer()
    wing = await _commander_wing(callback.from_user.id)
    if not wing:
        await callback.message.answer("❌ Ты не командир авиакрыла.")
        return
    parts = callback.data.split(":")

    if parts[2] == "do":
        if len(parts) < 5 or parts[3] != wing:
            return
        try:
            uid = int(parts[4])
        except ValueError:
            return
        u = await get_user(uid)
        if not u:
            await callback.message.answer("❌ Пилот не найден.")
            return
        if not _is_free_pilot(u) and u['wing'] != wing:
            await callback.message.answer(
                f"⚠️ {await player_display(u)} состоит в {wing_display(u['wing'])} — "
                f"чужое крыло трогать нельзя."
            )
            return
        # Командира и заместителя не выбрасывают из их же крыла: сначала снять с поста.
        post = ""
        if await get_wing_commander(wing) == uid:
            post = " Он командир этого крыла — сначала смени командира в штабе."
        elif await get_wing_deputy(wing) == uid:
            post = " Он заместитель — сначала сними его с поста."
        if post:
            await callback.message.answer(f"⚠️ {await player_display(u)}: убрать нельзя.{post}")
            return
        await set_wing(uid, None)
        await log_action(callback.from_user.id, 'hq_wing_drop_pilot',
                         details=f"pilot={uid}, wing={wing}")
        await callback.message.answer(
            f"✅ {await player_display(u)} убран из {WINGS[wing]}. Пилот снова свободен.",
            reply_markup=_hq_back_rows(
                [InlineKeyboardButton(text="➕ Взять пилота", callback_data="hq:wingtake:0")],
                [InlineKeyboardButton(text="🔙 В штаб", callback_data="hq:menu")],
            )
        )
        return

    try:
        page = int(parts[2])
    except ValueError:
        page = 0
    members = await get_wing_member_rows(wing)
    if not members:
        await callback.message.answer(
            f"В {WINGS[wing]} пока нет пилотов. Возьми кого-нибудь командой ниже.",
            reply_markup=_hq_back_rows(
                [InlineKeyboardButton(text="➕ Взять пилота", callback_data="hq:wingtake:0")],
                [InlineKeyboardButton(text="🔙 В штаб", callback_data="hq:menu")],
            )
        )
        return
    await _pilot_picker(
        callback, page,
        page_base="hq:wingdrop:",
        assign_prefix=f"hq:wingdrop:do:{wing}",
        back="hq:menu",
        caption=f"➖ Кого убрать из {WINGS[wing]}?",
        users=members,
    )


# ----- Заместитель командира -----
# Назначает и снимает заместителя командир этого крыла или штаб.
# Заместитель умеет отдавать приказы своему крылу, но составом не управляет.


async def _may_manage_deputy(user_id: int, wing: str) -> bool:
    if await has_permission(user_id, "can_manage_wing"):
        return True
    return await get_wing_commander_by_user(user_id) == wing


@router.callback_query(F.data.startswith("hq:wingdep:"))
async def hq_wing_deputy_cb(callback: CallbackQuery):
    """Экран заместителя: назначить, снять, показать текущего."""
    await callback.answer()
    parts = callback.data.split(":")
    wing = parts[2] if len(parts) >= 3 else ""
    if wing not in WINGS:
        return
    if not await _may_manage_deputy(callback.from_user.id, wing):
        await callback.message.answer("❌ Заместителя назначает только командир крыла.")
        return

    dep_uid = await get_wing_deputy(wing)
    dep_name = "— не назначен"
    if dep_uid:
        u = await get_user(dep_uid)
        dep_name = await player_display(u) if u else f"#{dep_uid}"

    rows = []
    if parts[3:] and parts[3] == "list":
        try:
            page = int(parts[4])
        except (ValueError, IndexError):
            page = 0
        members = await get_wing_member_rows(wing)
        if not members:
            await callback.message.answer(
                f"В {WINGS[wing]} нет пилотов — заместителем быть некому."
            )
            return
        await _pilot_picker(
            callback, page,
            page_base=f"hq:wingdep:{wing}:list:",
            assign_prefix=f"hq:wingdep:{wing}:set",
            back=f"hq:wingdep:{wing}",
            caption=f"🎖️ Заместитель из состава {WINGS_SHORT[wing]}",
            users=members,
        )
        return

    if parts[3:] and parts[3] == "set":
        try:
            uid = int(parts[4])
        except (ValueError, IndexError):
            return
        u = await get_user(uid)
        if not u:
            await callback.message.answer("❌ Пилот не найден.")
            return
        if not _is_free_pilot(u) and u['wing'] != wing:
            await callback.message.answer(
                f"⚠️ {await player_display(u)} состоит в {wing_display(u['wing'])} — "
                f"заместителем может быть только пилот этого крыла."
            )
            return
        if dep_uid == uid:
            await callback.message.answer(f"ℹ️ {await player_display(u)} уже заместитель.")
            return
        if await get_wing_commander(wing) == uid:
            await callback.message.answer(
                "⚠️ Командир и так отдаёт приказы — заместителем назначают другого пилота."
            )
            return
        await set_wing(uid, wing)
        await set_wing_deputy(wing, uid)
        await add_user_role(uid, 'wing_deputy', granted_by=callback.from_user.id)
        await log_action(callback.from_user.id, 'hq_set_wing_deputy',
                         details=f"wing={wing}, deputy={uid}")
        if dep_uid and not await get_wing_staff_wing(dep_uid):
            await remove_user_role(dep_uid, 'wing_deputy')
        await callback.message.answer(
            f"✅ Заместитель {WINGS_SHORT[wing]}: {await player_display(u)}\n"
            f"Теперь он отдаёт приказы своему крылу.",
            reply_markup=_hq_back_rows(
                [InlineKeyboardButton(text="🔙 В штаб", callback_data="hq:menu")],
            )
        )
        return

    if parts[3:] and parts[3] == "unset":
        if not dep_uid:
            await callback.message.answer("ℹ️ У этого крыла уже нет заместителя.")
            return
        await set_wing_deputy(wing)
        await log_action(callback.from_user.id, 'hq_unset_wing_deputy',
                         details=f"wing={wing}, deputy={dep_uid}")
        if not await get_wing_staff_wing(dep_uid):
            await remove_user_role(dep_uid, 'wing_deputy')
        await callback.message.answer(f"✅ Заместитель {WINGS_SHORT[wing]} снят: {dep_name}.")
        return

    rows = [[InlineKeyboardButton(text="🎖️ Назначить заместителя",
                                  callback_data=f"hq:wingdep:{wing}:list:0")]]
    if dep_uid:
        rows.append([InlineKeyboardButton(text="➖ Снять заместителя",
                                          callback_data=f"hq:wingdep:{wing}:unset")])
    rows.append([InlineKeyboardButton(text="🔙 В штаб", callback_data="hq:menu")])
    await callback.message.answer(
        f"🎖️ ЗАМЕСТИТЕЛЬ: {WINGS[wing]}\n\n"
        f"Заместитель: {dep_name}\n"
        f"Пилотов в крыле: {await count_wing_members(wing)}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows)
    )
