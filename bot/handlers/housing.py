"""Жильё пилота: комнаты-расширения (кухня/верстак/кадка/душевая), крафт и растение."""

import json
import os
import time

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton

from database.db import (
    get_user, get_player_housing, set_player_housing, get_housing_slots, set_housing_slot,
    ensure_player_housing, HOUSING_TYPES, HOUSING_ORDER, PLANT_STAGES, FRUIT_EVERY_DAYS,
    PLANT_NAMES,
    get_recipe, get_ingredient_map,
    get_learned_recipes, has_user_recipe,
    plant_seed, plant_stage_info, harvest_plant,
    get_inventory, get_item, get_item_by_name,
    remove_inventory_item, add_inventory_item,
    get_inventory_item, get_inventory_plant_data, set_inventory_plant_data,
    user_has_status_tag, log_activity, log_location_visit,
    remove_nordmarks,
    can_use_shower,
    get_housing_expansions_installed, increment_housing_expansions,
    get_housing_tax_rate, pay_housing_tax, is_housing_tax_paid, pay_housing_debt,
    use_lantern_meditation, has_lantern_installed, can_meditate_lantern,
    set_lantern_amber_next, get_lantern_amber_at, grant_lantern_amber_if_due,
)
from utils.crafting import (
    CRAFTING, FOOD_EXPIRY_PREFIXES, FOOD_EXPIRY_SEC, FRIED_PREFIX, FRIED_PREFIXES,
    MUSHROOM_ESSENCE_NAME, MUSHROOM_HEAL_POWDER_NAME, MUSHROOM_POISON_POWDER_NAME,
    MUSHROOM_POWDER_SPECS, MUSHROOM_PROCESS_AP_COST,
    CraftError, animate_craft, begin_craft, cancel_craft, end_craft, finish_craft,
    get_user_raw_mushrooms, mushroom_powder_spec, process_mushrooms, use_shower,
)
from utils.helpers import resolve_image, rarity_emoji, rarity_label, edit_or_replace

router = Router()

# ───────── константы ─────────

FURNITURE_BY_EXPANSION = {
    ("kitchen", 1): "Кухня 1 уровня",
    ("kitchen", 2): "Кухня 2 уровня",
    ("kitchen", 3): "Кухня 3 уровня",
    ("workbench", 1): "Верстак",
    ("plant_pot", 1): "Кадка для растений",
    ("shower", 1): "Душевая",
    ("shower", 2): "Ванная с душем",
    ("lantern", 1): "Лампа Круговорота",
}
FURNITURE_BY_ITEM = {v: k for k, v in FURNITURE_BY_EXPANSION.items()}

EXPANSION_LABELS = {
    "kitchen": "🍳 Кухня",
    "workbench": "🔧 Верстак",
    "plant_pot": "🌱 Кадка для растений",
    "shower": "🚿 Душевая",
    "lantern": "🪔 Лампа Круговорота",
}

# Душевая: раз в игровые сутки восстанавливает ОД. Душевая (ур. 1) — +25,
# ванна с душем (ур. 2) — +50. Лимит общий: одна комната, одно применение в сутки.
SHOWER_AP_BY_LEVEL = {1: 25, 2: 50}

# Помывка сбивает опьянение: душевая (ур. 1) — на 60 мин, ванная с душем
# (ур. 2) — на 180 мин. Сокращает «пьян» и «очень пьян» (utils/states.py).
SHOWER_SOBER_MINUTES = {1: 60, 2: 180}

# Встроенная кухня студии (идёт вместе с жильём, не снимается и не возвращается).
STUDIO_KITCHEN_NAME = "Маленький духовой шкаф, совмещённый с плиткой"

HOUSING_PHOTOS = {
    "municipal": "housing/kubrick",
    "studio": "housing/studio",
    "apartment": "housing/apartment",
    "improved": "housing/improved",
    "mansion": "housing/mansion",
}

# Предметы жилья из магазина → тип жилья (для переезда).
HOUSING_ITEM_BY_NAME = {
    "Студия": "studio",
    "Квартира": "apartment",
    "Улучшенное жильё": "improved",
    "Особняк": "mansion",
}

# Картинки стадий растений: seed_name → {1..4: путь}. Файлы в assets/img/housing.
# Под стадией 0 («Семя») показывается общая «стоковая» кадка — EMPTY_KADKA_PHOTO
# (фото кадки без растения, подпись стадии идёт в тексте описания).
# Стадии 1..4 — индивидуальные картинки под каждый вид семечек.
# Новое семечко из админ-мастера без своих файлов просто получит фолбэк
# на фото комнаты (см. _room_plant).
EMPTY_KADKA_PHOTO = "assets/img/housing/kadka.jpg"
PLANT_PHOTOS: dict[str, dict[int, str]] = {
    "Яблочное семечко": {
        # 0: общая кадка (EMPTY_KADKA_PHOTO) — отдельный файл не нужен
        1: "assets/img/housing/plant_apple_1.jpg",  # Росток
        2: "assets/img/housing/plant_apple_2.jpg",  # Саженец
        3: "assets/img/housing/plant_apple_3.jpg",  # Цветущее
        4: "assets/img/housing/plant_apple_4.jpg",  # Плодоносящее
    },
}

# Сроки годности и префиксы еды живут в общем ядре крафта (utils/crafting.py),
# сюда импортированы для обратной совместимости (smoke_126 и другие импорты).
# Защита от двойного крафта — тоже общая: CRAFTING из utils/crafting.py.

# Перепланировка: первая установка расширения в дом бесплатна, далее платно.
# Цена зависит от уровня жилья: Квартира (2 слота) — 300 НМ, далее +300 за уровень.
def replanning_cost(housing_type: str) -> int:
    try:
        idx = HOUSING_ORDER.index(housing_type)
    except ValueError:
        return 0
    return max(0, (idx - 1)) * 300

# Отрисованное сообщение жилья: user_id → (chat_id, message_id)
_HMSG: dict = {}


# ───────── вспомогательные ─────────

def _housing_photo(htype: str):
    key = HOUSING_PHOTOS.get(htype)
    if not key:
        return None
    path = resolve_image(key)
    return path if os.path.isfile(path) else None


def _plant_stage_photo(data: dict, ht: str, stage: int):
    """Картинка кадки/растения по стадии: «Семя» — общая стоковая кадка,
    стадии 1..4 — индивидуальные файлы (если загружены), иначе — фото комнаты."""
    if stage == 0:
        return EMPTY_KADKA_PHOTO if os.path.isfile(EMPTY_KADKA_PHOTO) else _housing_photo(ht)
    seed_name = data.get("seed")
    seed_photos = PLANT_PHOTOS.get(seed_name) or {} if seed_name else {}
    p = seed_photos.get(stage)
    return p if p and os.path.isfile(p) else _housing_photo(ht)


def _slot_icon(et):
    return {"kitchen": "🍳", "workbench": "🔧", "plant_pot": "🌱",
            "shower": "🚿", "lantern": "🪔"}.get(et, "📦")


def _slot_name(slot):
    et = slot.get("expansion_type", "")
    lvl = slot.get("expansion_level", 1)
    if slot.get("embedded"):
        return STUDIO_KITCHEN_NAME
    if et == "kitchen":
        return f"Кухня {lvl} ур."
    if et == "workbench":
        return "Верстак"
    if et == "plant_pot":
        return "Кадка для растений"
    if et == "shower":
        return "Ванная с душем" if lvl >= 2 else "Душевая"
    if et == "lantern":
        return "Лампа Круговорота"
    return "Пустой слот"


async def _paint(cb: CallbackQuery, text: str, photo=None, markup=None):
    """Отрисовка в одно сообщение (как в fishing)."""
    uid = cb.from_user.id
    chat_id = cb.message.chat.id
    tracked = _HMSG.get(uid)
    # Убираем inline-кнопки у старого сообщения
    if tracked:
        try:
            await cb.bot.edit_message_reply_markup(
                chat_id=tracked[0], message_id=tracked[1], reply_markup=None)
        except Exception:
            pass
    # Отправляем новое
    if photo and os.path.isfile(photo):
        msg = await cb.bot.send_photo(chat_id, FSInputFile(photo),
                                      caption=text, reply_markup=markup)
    else:
        msg = await cb.bot.send_message(chat_id, text, reply_markup=markup)
    _HMSG[uid] = (chat_id, msg.message_id)


def _inv_row(btn_text, cb_data):
    return InlineKeyboardButton(text=btn_text, callback_data=cb_data)


# ───────── главный экран ─────────

async def _housing_screen(uid: int):
    """Собирает главный экран жилья: (текст, фото, клавиатура).

    Вынесено из housing_menu, чтобы экран рисовался и из callback-кнопки,
    и из reply-кнопки «🏠 Жильё» главного меню.
    """
    h = await get_player_housing(uid)
    ht = h["housing_type"]
    info = HOUSING_TYPES[ht]
    label = h.get("housing_label") or info['name']
    eff_slots = h.get("housing_slots") or info["slots"]
    slots = await get_housing_slots(uid)

    lines = [f"🏠 *{label}*"]
    if info.get("desc"):
        lines.append(info["desc"])
    lines.append(f"Комнат-слотов: {len(slots)}/{eff_slots}\n")
    rows = []
    for i in range(eff_slots):
        s = slots.get(i)
        if s and s.get("expansion_type"):
            label = f"{_slot_icon(s['expansion_type'])} {_slot_name(s)}  ·  слот {i+1}"
        else:
            label = f"⬜ Пусто  ·  слот {i+1}"
        rows.append([_inv_row(label, f"housing:room:{i}")])

    # Кнопка «Перееезд» — если в инвентаре есть жильё более высокого типа
    inv = await get_inventory(uid)
    free = eff_slots - sum(1 for s in slots.values() if s.get("expansion_type"))
    if free == 0 and any(i["category"] == "furniture" for i in inv):
        lines.append("⚠️ В инвентаре есть мебель, но все слоты заняты.")
    cur_idx = HOUSING_ORDER.index(ht)
    for item in inv:
        if item["category"] != "housing":
            continue
        target = item.get("housing_type") or HOUSING_ITEM_BY_NAME.get(item["name"])
        if target and target in HOUSING_ORDER and HOUSING_ORDER.index(target) > cur_idx:
            rows.append([_inv_row(
                f"🏠 Переехать в «{item['name']}»",
                f"housing:move:{item['id']}")])

    rows.append([_inv_row("🔙 В город", "city:menu")])

    # Налог на недвижимость
    tax_rate = await get_housing_tax_rate(ht)
    if tax_rate > 0:
        tax_paid = await is_housing_tax_paid(uid)
        unpaid = h.get('tax_unpaid_months') or 0
        tax_line = f"\n🏛 Налог на жильё: {tax_rate} НМ/мес («за отопление и ремонт»)"
        if tax_paid:
            tax_line += " — ✅ оплачен за этот месяц"
        else:
            tax_line += " — ⚠️ за этот месяц ещё не оплачен"
        lines.append(tax_line)
        if unpaid > 0:
            debt = unpaid * tax_rate
            lines.append(
                f"🚨 Задолженность: {unpaid} {_month_word(unpaid)} ({debt} НМ). "
                f"При 3 мес. неуплаты жильё будет изъято."
            )
            rows.insert(-1, [_inv_row(f"💳 Оплатить долг ({debt} НМ)", "housing:pay_debt")])
        elif not tax_paid:
            rows.insert(-1, [_inv_row(f"💳 Оплатить налог ({tax_rate} НМ)", "housing:pay_tax")])

    return "\n".join(lines), _housing_photo(ht), InlineKeyboardMarkup(inline_keyboard=rows)


async def _open_housing_screen(uid: int, chat_id: int, bot):
    """Отрисовка экрана жилья новым сообщением (трекинг старого — как в _paint)."""
    text, photo, kb = await _housing_screen(uid)
    tracked = _HMSG.get(uid)
    if tracked:
        try:
            await bot.edit_message_reply_markup(
                chat_id=tracked[0], message_id=tracked[1], reply_markup=None)
        except Exception:
            pass
    if photo and os.path.isfile(photo):
        msg = await bot.send_photo(chat_id, FSInputFile(photo),
                                   caption=text, reply_markup=kb)
    else:
        msg = await bot.send_message(chat_id, text, reply_markup=kb)
    _HMSG[uid] = (chat_id, msg.message_id)


async def _housing_access_denied(uid: int) -> str:
    if not await user_has_status_tag(uid, "recruit"):
        return "❌ Жильё доступно только рекрутам и пилотам."
    return None


@router.callback_query(F.data == "housing:menu")
async def housing_menu(cb: CallbackQuery):
    await cb.answer()
    uid = cb.from_user.id
    denied = await _housing_access_denied(uid)
    if denied:
        await cb.answer(denied, show_alert=True)
        return
    await log_location_visit(uid, "housing")
    text, photo, kb = await _housing_screen(uid)
    await _paint(cb, text, photo, kb)


@router.message(F.text == "🏠 Жильё")
async def housing_menu_reply(message: Message):
    """Открытие жилья из reply-кнопки главного меню."""
    uid = message.from_user.id
    denied = await _housing_access_denied(uid)
    if denied:
        await message.answer(denied)
        return
    await log_location_visit(uid, "housing")
    await _open_housing_screen(uid, message.chat.id, message.bot)


def _month_word(n: int) -> str:
    if 11 <= n % 100 <= 14:
        return "месяцев"
    d = n % 10
    if d == 1:
        return "месяц"
    if 2 <= d <= 4:
        return "месяца"
    return "месяцев"


@router.callback_query(F.data == "housing:pay_tax")
async def housing_pay_tax(cb: CallbackQuery):
    await cb.answer()
    uid = cb.from_user.id
    ok, msg = await pay_housing_tax(uid)
    await cb.message.answer(msg)
    await housing_menu(cb)


@router.callback_query(F.data == "housing:pay_debt")
async def housing_pay_debt(cb: CallbackQuery):
    await cb.answer()
    uid = cb.from_user.id
    ok, msg = await pay_housing_debt(uid)
    await cb.message.answer(msg)
    await housing_menu(cb)


# ───────── комната ─────────

@router.callback_query(F.data.startswith("housing:room:"))
async def housing_room(cb: CallbackQuery):
    await cb.answer()
    uid = cb.from_user.id
    idx = int(cb.data.split(":")[2])
    h = await get_player_housing(uid)
    ht = h["housing_type"]
    info = HOUSING_TYPES[ht]
    eff_slots = h.get("housing_slots") or info["slots"]
    if idx >= eff_slots:
        return
    slots = await get_housing_slots(uid)
    slot = slots.get(idx)

    # Пустой слот
    if not slot or not slot.get("expansion_type"):
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [_inv_row("➕ Установить расширение", f"housing:install:{idx}")],
            [_inv_row("🔙 К жилью", "housing:menu")],
        ])
        await _paint(cb, f"⬜ *Слот {idx+1} пуст*\nУстанови мебель из инвентаря.", _housing_photo(ht), kb)
        return

    et = slot["expansion_type"]
    lvl = slot.get("expansion_level", 1)

    if et == "kitchen":
        await _room_kitchen(cb, uid, idx, slot, ht, lvl)
    elif et == "workbench":
        await _room_workbench(cb, uid, idx, slot, ht, lvl)
    elif et == "plant_pot":
        await _room_plant(cb, uid, idx, slot, ht)
    elif et == "shower":
        await _room_shower(cb, uid, idx, slot, ht, lvl)
    elif et == "lantern":
        await _room_lantern(cb, uid, idx, slot, ht)
    else:
        kb = InlineKeyboardMarkup(inline_keyboard=[[_inv_row("🔙 К жилью", "housing:menu")]])
        await _paint(cb, "Неизвестное расширение.", _housing_photo(ht), kb)


async def _room_kitchen(cb, uid, idx, slot, ht, lvl):
    title = _slot_name(slot)
    lines = [f"🍳 *{title}* (слот {idx+1})\n"]
    if slot.get("embedded"):
        lines.append("⚙️ Встроено в жильё — убрать нельзя.\n")
    lines.append("Выбери действие:")
    rows = [
        [_inv_row("🍳 Готовить", f"housing:kitchen:{idx}")],
        [_inv_row("🍄 Переработка грибов", f"housing:mushrooms:{idx}")],
    ]
    if not slot.get("embedded"):
        rows.append([_inv_row("🛠️ Убрать из слота", f"housing:uninstall:{idx}")])
    rows.append([_inv_row("🔙 К жилью", "housing:menu")])
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    await _paint(cb, "\n".join(lines), _housing_photo(ht), kb)


@router.callback_query(F.data.startswith("housing:kitchen:"))
async def housing_kitchen_recipes(cb: CallbackQuery):
    await cb.answer()
    uid = cb.from_user.id
    idx = int(cb.data.split(":")[2])
    slots = await get_housing_slots(uid)
    slot = slots.get(idx)
    if not slot or slot.get("expansion_type") != "kitchen":
        return
    lvl = slot.get("expansion_level", 1)
    ht = (await get_player_housing(uid))["housing_type"]
    await _kitchen_recipes(cb, uid, idx, slot, ht, lvl)


async def _kitchen_recipes(cb, uid, idx, slot, ht, lvl):
    learned = await get_learned_recipes(uid, "kitchen")
    available = [r for r in learned if (r["required_level"] or 1) <= lvl]
    locked = [r for r in learned if (r["required_level"] or 1) > lvl]
    title = _slot_name(slot)
    lines = [f"🍳 *{title}* (слот {idx+1})\n"]
    if not learned:
        lines.append("Нет выученных рецептов.\nКупи «📜 Рецепты» в Магазине 🏪.")
    else:
        if available:
            lines.append("Доступные рецепты:")
            for r in available:
                lines.append(f"  • {r['name']}")
        else:
            lines.append("Рецептов для этого уровня кухни нет.")
        if locked:
            lines.append("")
            lines.append(f"🔒 Выучено, но нужна кухня выше (твоя — {lvl} ур.):")
            for r in locked:
                lines.append(f"  • {r['name']} — кухня {r['required_level']} ур.")

    rows = []
    for r in available:
        rows.append([_inv_row(f"📋 {r['name']}", f"housing:recipe:{idx}:{r['id']}")])
    rows.append([_inv_row("🍄 Переработка грибов", f"housing:mushrooms:{idx}")])
    rows.append([_inv_row("🔙 К кухне", f"housing:room:{idx}")])
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    await _paint(cb, "\n".join(lines), _housing_photo(ht), kb)


async def _kitchen_mushrooms(cb, uid, idx, slot, ht, lvl, notice: str = ""):
    title = _slot_name(slot)
    user = await get_user(uid) or {}
    ap = int(user.get("ap") or 0)
    ap_max = int(user.get("ap_max") or ap)
    mushrooms = await get_user_raw_mushrooms(uid)

    lines = [f"🍄 *Переработка грибов* — {title} (слот {idx+1})\n"]
    if notice:
        lines.append(notice)
        lines.append("")
    lines.append(
        f"Рецепт не нужен. Стоимость: *{MUSHROOM_PROCESS_AP_COST} ОД* за 1 гриб.\n"
        f"• Съедобные → «{MUSHROOM_HEAL_POWDER_NAME}» "
        f"(из Гиропора и Ежовика редко выпадает «{MUSHROOM_ESSENCE_NAME}»).\n"
        f"• Ядовитые → «{MUSHROOM_POISON_POWDER_NAME}».\n"
        f"⚡ Твои ОД: *{ap}/{ap_max}*\n"
    )
    rows = []
    if not mushrooms:
        lines.append("У тебя нет сырых грибов для переработки.")
    else:
        lines.append("Твои сырые грибы:")
        for m in mushrooms:
            spec = m["spec"]
            ess = f", эссенция {spec['essence_chance']}%" if spec.get("essence_chance") else ""
            icon = "☠" if m["kind"] == "toxic" else "🍄"
            qty = int(m["quantity"])
            lines.append(
                f"  • {icon} {m['name']} ×{qty} → "
                f"{spec['min']}–{spec['max']} порошка{ess}"
            )
            iid = int(m["item_id"])
            btn_one = InlineKeyboardButton(
                text=f"{icon} {m['name']}: 1 шт. ({MUSHROOM_PROCESS_AP_COST} ОД)",
                callback_data=f"housing:mushproc:{idx}:{iid}:1",
            )
            if qty > 1:
                all_ap = qty * MUSHROOM_PROCESS_AP_COST
                btn_all = InlineKeyboardButton(
                    text=f"Все ×{qty} ({all_ap} ОД)",
                    callback_data=f"housing:mushproc:{idx}:{iid}:all",
                )
                rows.append([btn_one, btn_all])
            else:
                rows.append([btn_one])

    rows.append([_inv_row("🔙 К кухне", f"housing:room:{idx}")])
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    await _paint(cb, "\n".join(lines), _housing_photo(ht), kb)


@router.callback_query(F.data.startswith("housing:mushrooms:"))
async def housing_kitchen_mushrooms(cb: CallbackQuery):
    await cb.answer()
    uid = cb.from_user.id
    idx = int(cb.data.split(":")[2])
    slots = await get_housing_slots(uid)
    slot = slots.get(idx)
    if not slot or slot.get("expansion_type") != "kitchen":
        return
    lvl = slot.get("expansion_level", 1)
    ht = (await get_player_housing(uid))["housing_type"]
    await _kitchen_mushrooms(cb, uid, idx, slot, ht, lvl)


@router.callback_query(F.data.startswith("housing:mushproc:"))
async def housing_kitchen_mushproc(cb: CallbackQuery):
    uid = cb.from_user.id
    parts = cb.data.split(":")
    idx = int(parts[2])
    item_id = int(parts[3])
    mode = parts[4] if len(parts) > 4 else "1"
    slots = await get_housing_slots(uid)
    slot = slots.get(idx)
    if not slot or slot.get("expansion_type") != "kitchen":
        await cb.answer("❌ Здесь нет кухни.", show_alert=True)
        return
    try:
        out = await process_mushrooms(uid, item_id, mode=mode)
    except CraftError as e:
        await cb.answer(str(e), show_alert=True)
        return

    ess_line = (
        f"\n✨ Редкая удача! «{out['essence_name']}» ×{out['essence_qty']}"
        if out.get("essence_qty")
        else ""
    )
    notice = (
        f"✅ Переработано: «{out['mushroom_name']}» ×{out['processed_count']} "
        f"(−{out['ap_spent']} ОД)\n"
        f"🎒 Получено: «{out['powder_name']}» ×{out['powder_qty']}{ess_line}"
    )
    await cb.answer("✅ Грибы переработаны!")
    lvl = slot.get("expansion_level", 1)
    ht = (await get_player_housing(uid))["housing_type"]
    await _kitchen_mushrooms(cb, uid, idx, slot, ht, lvl, notice=notice)


async def _room_workbench(cb, uid, idx, slot, ht, lvl):
    learned = await get_learned_recipes(uid, "workbench")
    available = [r for r in learned if (r["required_level"] or 1) <= lvl]
    locked = [r for r in learned if (r["required_level"] or 1) > lvl]
    lines = [f"🔧 *Верстак* (слот {idx+1})\n"]
    if not learned:
        lines.append("Нет выученных рецептов.\nКупи «📜 Рецепты» в Магазине 🏪.")
    else:
        if available:
            lines.append("Доступные рецепты:")
            for r in available:
                lines.append(f"  • {r['name']}")
        else:
            lines.append("Рецептов для этого уровня верстака нет.")
        if locked:
            lines.append("")
            lines.append(f"🔒 Выучено, но нужен верстак выше (твой — {lvl} ур.):")
            for r in locked:
                lines.append(f"  • {r['name']} — верстак {r['required_level']} ур.")

    rows = []
    for r in available:
        rows.append([_inv_row(f"📋 {r['name']}", f"housing:recipe:{idx}:{r['id']}")])
    rows.append([_inv_row("🛠️ Убрать из слота", f"housing:uninstall:{idx}")])
    rows.append([_inv_row("🔙 К жилью", "housing:menu")])
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    await _paint(cb, "\n".join(lines), _housing_photo(ht), kb)


async def _room_shower(cb, uid, idx, slot, ht, lvl):
    title = _slot_name(slot)
    ap_gain = SHOWER_AP_BY_LEVEL.get(lvl, 25)
    sober = SHOWER_SOBER_MINUTES.get(lvl, 60)
    can = await can_use_shower(uid)
    lines = [f"🚿 *{title}* (слот {idx+1})\n"]
    if can:
        lines.append(f"Раз в сутки можно освежиться: +{ap_gain} ОД и −{sober} мин "
                     f"к состояниям «пьян» и «очень пьян».")
    else:
        lines.append("✅ Сегодня ты уже мылся — приходи завтра.")
    rows = []
    if can:
        rows.append([_inv_row(f"🚿 Принять душ (+{ap_gain} ОД)", f"housing:shower:{idx}")])
    rows.append([_inv_row("🛠️ Убрать из слота", f"housing:uninstall:{idx}")])
    rows.append([_inv_row("🔙 К жилью", "housing:menu")])
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    await _paint(cb, "\n".join(lines), _housing_photo(ht), kb)


@router.callback_query(F.data.startswith("housing:shower:"))
async def housing_shower(cb: CallbackQuery):
    await cb.answer()
    uid = cb.from_user.id
    idx = int(cb.data.split(":")[2])
    slots = await get_housing_slots(uid)
    slot = slots.get(idx)
    if not slot or slot.get("expansion_type") != "shower":
        await cb.answer("❌ Здесь нет душевой.", show_alert=True)
        return
    if not await can_use_shower(uid):
        await cb.answer("🚿 Сегодня ты уже мылся — приходи завтра.", show_alert=True)
        return
    lvl = slot.get("expansion_level", 1)
    outcome = await use_shower(
        uid, lvl, ap_by_level=SHOWER_AP_BY_LEVEL,
        sober_by_level=SHOWER_SOBER_MINUTES, reason="душевая")
    if not outcome:
        await cb.answer("🚿 Сегодня ты уже мылся — приходи завтра.", show_alert=True)
        return
    ap_gain = outcome["ap_gain"]
    sober = outcome["sober"]
    changes = outcome["changes"]
    alert = f"🚿 Освежился: +{ap_gain} ОД!"
    if changes:
        titles = ", ".join(f"«{c['title']}»" for c in changes)
        alert += f"\n🍺 {titles}: −{sober} мин."
        if all(c["removed"] for c in changes):
            alert += "\n✅ Ты совсем трезв."
    await cb.answer(alert, show_alert=True)
    ht = (await get_player_housing(uid))["housing_type"]
    await _room_shower(cb, uid, idx, slot, ht, lvl)


# ───────── Лампа Круговорота (Ф4б) ─────────

async def _room_lantern(cb, uid, idx, slot, ht):
    """Генератор (не привязан к празднику): медитация +ОД раз в сутки,
    Пламя Памяти раз в 5 суток."""
    import config as _cfg
    from datetime import datetime
    from utils.helpers import MOSCOW_TZ
    # пришло время янтаря? — начисляем сразу при открытии комнаты
    await grant_lantern_amber_if_due(uid)
    medit_ap = int(_cfg.FIRE_LANTERN_MEDIT_AP)
    can_medit = await can_meditate_lantern(uid)
    amber_days = int(_cfg.FIRE_LANTERN_AMBER_DAYS)
    lines = [f"🪔 *Лампа Круговорота* (слот {idx + 1})\n"]
    lines.append("Тёплый огонёк из Огненного Круговорота: помнит предков и "
                 "делится силой с пилотом, который её почтит.")
    if can_medit:
        lines.append(f"\n🧘 Раз в сутки: медитация у Лампы — +{medit_ap} ОД.")
    else:
        lines.append("\n🧘 Ты уже медитировал сегодня — приходи завтра.")
    ts = await get_lantern_amber_at(uid)
    if ts:
        nxt = datetime.fromtimestamp(ts, MOSCOW_TZ)
        left = nxt - datetime.now(MOSCOW_TZ)
        if left.total_seconds() > 0:
            days_left = int(left.total_seconds() // 86400) + 1
            lines.append(f"\n🪵 Пламя Памяти: следующий кусок янтаря — через "
                         f"~{days_left} сут. ({nxt.strftime('%d.%m %H:%M')}), "
                         f"каждые {amber_days} суток.")
        else:
            lines.append("\n🪵 Пламя Памяти готово и отправлено в инвентарь!")
    rows = []
    if can_medit:
        rows.append([_inv_row(f"🧘 Медитировать (+{medit_ap} ОД)",
                              f"housing:lantern_medit:{idx}")])
    rows.append([_inv_row("🛠️ Убрать из слота", f"housing:uninstall:{idx}")])
    rows.append([_inv_row("🔙 К жилью", "housing:menu")])
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    await _paint(cb, "\n".join(lines), _housing_photo(ht), kb)


@router.callback_query(F.data.startswith("housing:lantern_medit:"))
async def housing_lantern_medit(cb: CallbackQuery):
    await cb.answer()
    uid = cb.from_user.id
    idx = int(cb.data.split(":")[2])
    slots = await get_housing_slots(uid)
    slot = slots.get(idx)
    if not slot or slot.get("expansion_type") != "lantern":
        await cb.answer("❌ Здесь нет Лампы.", show_alert=True)
        return
    gained = await use_lantern_meditation(uid)
    if not gained:
        await cb.answer("🧘 Ты уже медитировал сегодня — приходи завтра.",
                        show_alert=True)
        return
    await cb.answer(f"🪔 Медитация: +{gained} ОД!", show_alert=True)
    ht = (await get_player_housing(uid))["housing_type"]
    await _room_lantern(cb, uid, idx, slot, ht)


async def _room_plant(cb, uid, idx, slot, ht):
    data = {}
    try:
        data = json.loads(slot.get("plant_data") or "{}")
    except Exception:
        pass

    seed_name = data.get("seed")
    plant_name = data.get("plant_name") or (PLANT_NAMES.get(seed_name, seed_name) if seed_name else seed_name)
    if not seed_name:
        # Пустая кадка — список семян в инвентаре
        inv = await get_inventory(uid)
        seeds = [i for i in inv if i["category"] == "seeds"]
        lines = ["🌱 *Кадка пуста*\nВыбери семечко для посадки:"]
        rows = []
        for s in seeds:
            rows.append([_inv_row(
                f"🌱 {s['name']} ({s['quantity']} шт.)",
                f"housing:plant:{idx}:{s['id']}")])
        if not seeds:
            lines.append("\nСемян в инвентаре нет.")
        rows.append([_inv_row("🛠️ Убрать кадку", f"housing:uninstall:{idx}")])
        rows.append([_inv_row("🔙 К жилью", "housing:menu")])
        kb = InlineKeyboardMarkup(inline_keyboard=rows)
        photo = EMPTY_KADKA_PHOTO if os.path.isfile(EMPTY_KADKA_PHOTO) else _housing_photo(ht)
        await _paint(cb, "\n".join(lines), photo, kb)
        return

    now = time.time()
    info = plant_stage_info(data, now)
    stage = info["stage"]
    stage_name = PLANT_STAGES[stage][0]
    fruits = info["fruits"]
    next_in = info["next_in"]

    lines = [f"🌱 *Растение: {plant_name}*\nСтадия: {stage_name}"]
    if stage < 4 and next_in > 0:
        lines.append(f"До следующей стадии: {next_in/86400:.1f} сут.")
    elif fruits > 0:
        lines.append(f"🍎 Плодов на дереве: {fruits}/5")
    elif fruits == 0:
        lines.append(f"До плодов: {next_in/86400:.1f} сут.")

    rows = []
    if fruits > 0:
        if fruits == 1:
            label = "🍎 Собрать плод"
        elif 2 <= fruits <= 4:
            label = f"🍎 Собрать {fruits} плода"
        else:
            label = f"🍎 Собрать {fruits} плодов"
        rows.append([_inv_row(label, f"housing:harvest:{idx}")])
    rows.append([_inv_row("🛠️ Убрать кадку", f"housing:uninstall:{idx}")])
    rows.append([_inv_row("🔙 К жилью", "housing:menu")])
    kb = InlineKeyboardMarkup(inline_keyboard=rows)

    # Картинка стадии растения: «Семя» — общая стоковая кадка, дальше —
    # индивидуальная под вид семечка (если её файл загружен), иначе — фото комнаты.
    plant_photo = _plant_stage_photo(data, ht, stage)
    await _paint(cb, "\n".join(lines), plant_photo, kb)


# ───────── карточка рецепта ─────────

@router.callback_query(F.data.startswith("housing:recipe:"))
async def housing_recipe(cb: CallbackQuery):
    await cb.answer()
    uid = cb.from_user.id
    _, _, idx_s, rid_s = cb.data.split(":")
    idx, rid = int(idx_s), int(rid_s)

    r = await get_recipe(rid)
    if not r:
        await cb.answer("❌ Рецепт не найден.", show_alert=True)
        return
    if not await has_user_recipe(uid, rid):
        await cb.answer("❌ Ты ещё не изучил этот рецепт.", show_alert=True)
        return
    ingredients = json.loads(r["ingredients"] or "[]")

    inv_map = await get_ingredient_map(uid)
    lines = [f"📋 *{r['name']}*\n{r['description']}\n", "Ингредиенты:"]
    can_craft = True
    for ing_name, qty in ingredients:
        have = inv_map.get(ing_name, 0)
        ok = have >= qty
        mark = "✅" if ok else "❌"
        lines.append(f"  {mark} {ing_name}: {have}/{qty}")
        if not ok:
            can_craft = False

    lines.append(f"\nОД: {r['ap_cost']} | Время: ~{r['production_time']} сек")

    rows = []
    if can_craft:
        rows.append([_inv_row(
            f"🏭 Готовить  ({r['production_time']} сек)",
            f"housing:craft:{idx}:{rid}")])
    else:
        lines.append("\n⚠️ Нет ингредиентов!")
    rows.append([_inv_row("🔙 Назад", f"housing:room:{idx}")])
    kb = InlineKeyboardMarkup(inline_keyboard=rows)

    h = await get_player_housing(uid)
    await _paint(cb, "\n".join(lines), _housing_photo(h["housing_type"]), kb)


# ───────── крафт ─────────

@router.callback_query(F.data.startswith("housing:craft:"))
async def housing_craft(cb: CallbackQuery):
    uid = cb.from_user.id
    _, _, idx_s, rid_s = cb.data.split(":")
    idx, rid = int(idx_s), int(rid_s)

    slots = await get_housing_slots(uid)
    slot = slots.get(idx) or {}
    try:
        ctx = await begin_craft(uid, rid, slot.get("expansion_type"),
                                int(slot.get("expansion_level") or 1))
    except CraftError as e:
        await cb.answer(str(e), show_alert=True)
        return

    r = ctx["recipe"]
    ap_cost = ctx["ap_cost"]
    try:
        await cb.answer("🏭 Начал готовить!")
        h = await get_player_housing(uid)
        await animate_craft(cb.bot, cb.message.chat.id, r,
                            photo=_housing_photo(h["housing_type"]),
                            noop_data="housing:noop")
        try:
            outcome = await finish_craft(uid, ctx)
        except CraftError as e:
            await cb.bot.send_message(cb.message.chat.id, str(e))
            return
        # Результат уже выдан — при сбое отправки сообщения сырьё не возвращаем.
        ctx["consumed"] = []

        lines = [f"✅ *{outcome['name']}* готово!",
                 f"Количество: ×{outcome['qty']}"]
        if outcome["expires_at"]:
            lines.append("⏳ Срок годности: 6 дней")
        lines.append("\nДобавлено в инвентарь.")

        if outcome["can_repeat"]:
            inv_map2 = await get_ingredient_map(uid)
            lines.append("\n🔄 *Можно приготовить ещё:*")
            for ing_name, qty in ctx["ingredients"]:
                have = inv_map2.get(ing_name, 0)
                lines.append(f"• {ing_name}: {have}/{qty}")

        rows = []
        if outcome["can_repeat"]:
            rows.append([_inv_row(f"🔄 Жарить ещё ({ap_cost} ОД)",
                                  f"housing:craft:{idx}:{rid}")])
        rows.append([_inv_row("📋 К рецептам", f"housing:room:{idx}")])
        rows.append([_inv_row("🏠 К жилью", "housing:menu")])
        kb = InlineKeyboardMarkup(inline_keyboard=rows)
        await cb.bot.send_message(cb.message.chat.id, "\n".join(lines), reply_markup=kb)
    except Exception:
        await cancel_craft(uid, ctx)
        raise
    finally:
        end_craft(uid)


@router.callback_query(F.data == "housing:noop")
async def noop_handler(cb: CallbackQuery):
    await cb.answer("⏳ Приготовление…")


# ───────── установка расширения ─────────

@router.callback_query(F.data.startswith("housing:install:"))
async def housing_install(cb: CallbackQuery):
    uid = cb.from_user.id
    idx = int(cb.data.split(":")[2])

    h = await get_player_housing(uid)
    ht = h["housing_type"]
    info = HOUSING_TYPES[ht]
    if idx >= info["slots"]:
        return

    slots = await get_housing_slots(uid)
    if slots.get(idx, {}).get("expansion_type"):
        await cb.answer("❌ Слот уже занят.", show_alert=True)
        return

    installed = await get_housing_expansions_installed(uid)
    cost = replanning_cost(ht) if installed > 0 else 0

    inv = await get_inventory(uid)
    furniture = [i for i in inv if i["category"] == "furniture"]
    lines = ["➕ *Установить расширение*\nВыбери мебель из инвентаря:"]
    if cost:
        lines.append(f"\n⚠️ Перепланировка (не первая установка): {cost} НМ")
    else:
        lines.append("\n🆓 Первая установка в этом жильё — бесплатно.")
    rows = []
    for item in furniture:
        rows.append([_inv_row(
            f"{item['name']} ({item['quantity']} шт.)",
            f"housing:install_item:{idx}:{item['id']}")])
    if not furniture:
        lines.append("\nМебели нет.")
    rows.append([_inv_row("🔙 Назад", f"housing:room:{idx}")])
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    await _paint(cb, "\n".join(lines), _housing_photo(ht), kb)


@router.callback_query(F.data.startswith("housing:install_item:"))
async def housing_install_item(cb: CallbackQuery):
    uid = cb.from_user.id
    _, _, idx_s, iid_s = cb.data.split(":")
    idx, item_id = int(idx_s), int(iid_s)

    item = await get_item(item_id)
    if not item or item["category"] != "furniture":
        await cb.answer("❌ Это не мебель.", show_alert=True)
        return

    mapping = FURNITURE_BY_ITEM.get(item["name"])
    if not mapping:
        await cb.answer("❌ Нельзя установить.", show_alert=True)
        return
    et, lvl = mapping

    h = await get_player_housing(uid)
    ht = h["housing_type"]
    info = HOUSING_TYPES[ht]
    max_slots = info["slots"]
    slots = await get_housing_slots(uid)

    # Плата за перепланировку: первая установка расширения в это жильё — бесплатно,
    # каждая последующая — платно (цена зависит от уровня жилья).
    installed = await get_housing_expansions_installed(uid)
    cost = replanning_cost(ht) if installed > 0 else 0
    if cost:
        user = await get_user(uid)
        if not user or user['nordmarks'] < cost:
            await cb.answer(f"❌ Перепланировка стоит {cost} НМ. Не хватает средств!",
                            show_alert=True)
            return

    # Кухня/душевая: замена старой версии на более высокий уровень (возврат в
    # инвентарь). Встроенную кухню студии не трогаем.
    if et in ("kitchen", "shower"):
        for i, s in sorted(slots.items()):
            if (not s.get("embedded")
                    and s.get("expansion_type") == et
                    and s.get("expansion_level", 1) < lvl):
                old_name = FURNITURE_BY_EXPANSION.get((et, s["expansion_level"]))
                if cost:
                    await remove_nordmarks(uid, cost, "replanning", f"Перепланировка жилья ({ht})")
                await set_housing_slot(uid, i, et, lvl)
                await remove_inventory_item(uid, item_id, 1)
                if old_name:
                    old_item = await get_item_by_name(old_name)
                    if old_item:
                        await add_inventory_item(uid, old_item["id"], 1)
                await increment_housing_expansions(uid)
                await cb.answer(f"✅ {item['name']} установлена (заменила «{old_name}»).",
                                show_alert=True)
                await housing_menu(cb)
                return

    # Проверка дубликата
    if any(s.get("expansion_type") == et for s in slots.values()):
        await cb.answer("❌ Такое расширение уже установлено.", show_alert=True)
        return

    # Ищем пустой слот
    empty = None
    for i in range(max_slots):
        if i not in slots:
            empty = i
            break
    if empty is None:
        await cb.answer("❌ Нет свободных слотов.", show_alert=True)
        return

    if cost:
        await remove_nordmarks(uid, cost, "replanning", f"Перепланировка жилья ({ht})")

    # Кадка с растением: восстанавливаем plant_data из инвентария (заморозка снимается)
    restored_pd = None
    if et == "plant_pot":
        stored_pd = await get_inventory_plant_data(uid, item_id)
        if stored_pd and stored_pd.get("seed"):
            stowed_at = float(stored_pd.pop("stowed_at", 0) or 0)
            if stowed_at > 0:
                shift = time.time() - stowed_at
                if stored_pd.get("stage_started_at"):
                    stored_pd["stage_started_at"] = float(stored_pd["stage_started_at"]) + shift
                if stored_pd.get("last_harvest_at"):
                    stored_pd["last_harvest_at"] = float(stored_pd["last_harvest_at"]) + shift
            restored_pd = stored_pd
        await set_inventory_plant_data(uid, item_id, None)

    await set_housing_slot(uid, empty, et, lvl, restored_pd)
    await remove_inventory_item(uid, item_id, 1)
    await increment_housing_expansions(uid)
    if et == "lantern":
        # Ф4б: таймер Пламени Памяти запускается с установки (или продолжается).
        if await get_lantern_amber_at(uid) is None:
            await set_lantern_amber_next(uid)
    if restored_pd and restored_pd.get("seed"):
        rp_name = restored_pd.get("plant_name") or PLANT_NAMES.get(restored_pd["seed"], restored_pd["seed"])
        await cb.answer(f"✅ «{item['name']}» установлена — растение «{rp_name}» восстановлено!",
                        show_alert=True)
    else:
        await cb.answer(f"✅ «{item['name']}» установлено в слот {empty+1}.", show_alert=True)
    await housing_menu(cb)


# ───────── снятие расширения ─────────

@router.callback_query(F.data.startswith("housing:uninstall:"))
async def housing_uninstall(cb: CallbackQuery):
    await cb.answer()
    uid = cb.from_user.id
    idx = int(cb.data.split(":")[2])

    slots = await get_housing_slots(uid)
    slot = slots.get(idx)
    if not slot or not slot.get("expansion_type"):
        await cb.answer("❌ Слот уже пуст.", show_alert=True)
        return
    if slot.get("embedded"):
        await cb.answer("⚙️ Это встроено в жильё — убрать нельзя.", show_alert=True)
        return

    et = slot["expansion_type"]
    ht = (await get_player_housing(uid))["housing_type"]
    installed = await get_housing_expansions_installed(uid)
    cost = replanning_cost(ht) if installed > 0 else 0
    if cost:
        cost_line = (f"\n💸 Повторная установка расширения будет платной "
                     f"(перепланировка: {cost} НМ).")
    else:
        cost_line = "\n💸 Первая установка в это жильё снова будет бесплатной."

    # Кадка с растением: отдельное предупреждение — растение удалится безвозвратно.
    if et == "plant_pot":
        try:
            data = json.loads(slot.get("plant_data") or "{}")
        except Exception:
            data = {}
        if data.get("seed"):
            info = plant_stage_info(data, time.time())
            stage_name = PLANT_STAGES[info["stage"]][0]
            plant_name = data.get("plant_name") or PLANT_NAMES.get(data["seed"], data["seed"])
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [_inv_row("✅ Убрать, растение удалить", f"housing:uninstall_confirm:{idx}")],
                [_inv_row("❌ Оставить", f"housing:room:{idx}")],
            ])
            await _paint(
                cb,
                f"🌱 *Убрать кадку с растением?*\n\n"
                f"Растение «{plant_name}» (стадия: {stage_name}) будет удалено "
                f"безвозвратно — семечко и прогресс не вернутся.\n"
                f"Кадка снова станет обычной пустой.{cost_line}",
                _plant_stage_photo(data, ht, info["stage"]),
                kb
            )
            return

    # Любое другое расширение: подтверждение перед снятием, чтобы случайное
    # нажатие не снимало мебель и не тянуло за собой платную перепланировку.
    title = _slot_name(slot)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [_inv_row("✅ Убрать из слота", f"housing:uninstall_confirm:{idx}")],
        [_inv_row("❌ Оставить", f"housing:room:{idx}")],
    ])
    await _paint(
        cb,
        f"🛠️ *Убрать «{title}» из слота {idx+1}?*\n\n"
        f"Расширение вернётся в инвентарь.{cost_line}",
        _housing_photo(ht),
        kb
    )


@router.callback_query(F.data.startswith("housing:uninstall_confirm:"))
async def housing_uninstall_confirm(cb: CallbackQuery):
    await cb.answer()
    uid = cb.from_user.id
    idx = int(cb.data.split(":")[2])

    slots = await get_housing_slots(uid)
    slot = slots.get(idx)
    if not slot or not slot.get("expansion_type"):
        await cb.answer("❌ Слот уже пуст.", show_alert=True)
        return
    if slot.get("embedded"):
        await cb.answer("⚙️ Это встроено в жильё — убрать нельзя.", show_alert=True)
        return

    et = slot["expansion_type"]
    lvl = slot.get("expansion_level", 1)
    fname = FURNITURE_BY_EXPANSION.get((et, lvl))
    await set_housing_slot(uid, idx, None)
    if fname:
        fi = await get_item_by_name(fname)
        if fi:
            await add_inventory_item(uid, fi["id"], 1)

    if et == "plant_pot":
        await cb.answer("✅ Кадка возвращена в инвентарь, растение удалено.",
                        show_alert=True)
    else:
        await cb.answer(f"✅ «{fname}» возвращено в инвентарь.", show_alert=True)
    await housing_menu(cb)


# ───────── посадка семечка ─────────

@router.callback_query(F.data.startswith("housing:plant:"))
async def housing_plant_seed(cb: CallbackQuery):
    await cb.answer()
    uid = cb.from_user.id
    _, _, idx_s, seed_s = cb.data.split(":")
    idx, seed_id = int(idx_s), int(seed_s)

    ok, msg = await plant_seed(uid, idx, seed_id)
    if ok:
        await cb.answer(f"✅ {msg} посажено!", show_alert=True)
    else:
        await cb.answer(f"❌ {msg}", show_alert=True)
    h = await get_player_housing(uid)
    slots = await get_housing_slots(uid)
    slot = slots.get(idx)
    if slot:
        await _room_plant(cb, uid, idx, slot, h["housing_type"])


# ───────── сбор плодов ─────────

@router.callback_query(F.data.startswith("housing:harvest:"))
async def housing_harvest(cb: CallbackQuery):
    await cb.answer()
    uid = cb.from_user.id
    idx = int(cb.data.split(":")[2])

    ok, result = await harvest_plant(uid, idx)
    if ok:
        apple, qty = result
        await cb.answer(f"🍎 Собрано: {apple['name']} ×{qty}!", show_alert=True)
    else:
        await cb.answer(f"❌ {result}", show_alert=True)
    h = await get_player_housing(uid)
    slots = await get_housing_slots(uid)
    slot = slots.get(idx)
    if slot:
        await _room_plant(cb, uid, idx, slot, h["housing_type"])


# ───────── переезд ─────────

@router.callback_query(F.data.startswith("housing:move:"))
async def housing_move(cb: CallbackQuery):
    await cb.answer()
    uid = cb.from_user.id
    item_id = int(cb.data.split(":")[2])

    item = await get_item(item_id)
    if not item or item["category"] != "housing":
        return

    target = item.get("housing_type") or HOUSING_ITEM_BY_NAME.get(item["name"])
    if not target or target not in HOUSING_ORDER:
        return

    h = await get_player_housing(uid)
    current_idx = HOUSING_ORDER.index(h["housing_type"])
    target_idx = HOUSING_ORDER.index(target)
    if target_idx <= current_idx:
        await cb.answer("❌ Нельзя переехать в жильё того же типа или ниже.", show_alert=True)
        return

    # Все текущие расширения возвращаются в инвентарь (кроме встроенных)
    slots = await get_housing_slots(uid)
    plant_saved = False
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
                # Кадка с растением: сохраняем plant_data в инвентарь (прогресс замораживается)
                if et == "plant_pot":
                    try:
                        pdata = json.loads(s.get("plant_data") or "{}")
                    except Exception:
                        pdata = {}
                    if pdata.get("seed"):
                        pdata["stowed_at"] = time.time()
                        await set_inventory_plant_data(uid, fi["id"], pdata)
                        plant_saved = True

    await remove_inventory_item(uid, item_id, 1)
    await set_player_housing(uid, target, housing_label=item["name"],
                             housing_slots=item.get("housing_slots"))

    # Студия поставляется с встроенной кухней (социальная программа «Забота Нордхайма»)
    if target == "studio":
        await set_housing_slot(uid, 0, "kitchen", 1, embedded=True)

    await log_activity(uid, "housing_move", target)

    new_name = HOUSING_TYPES[target]["name"]
    plant_note = "\n\n🌱 Кадка с растением сохранена в инвентаре — прогресс заморожен." if plant_saved else ""
    await cb.answer(f"🎉 Переезд в «{new_name}» завершён!{plant_note}", show_alert=True)
    await housing_menu(cb)
