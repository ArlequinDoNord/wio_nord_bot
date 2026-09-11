"""Жильё пилота: комнаты-расширения (кухня/верстак/кадка), крафт и растение."""

import asyncio
import json
import os
import time

from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton

from database.db import (
    get_user, get_player_housing, set_player_housing, get_housing_slots, set_housing_slot,
    ensure_player_housing, HOUSING_TYPES, HOUSING_ORDER, PLANT_STAGES, FRUIT_EVERY_DAYS,
    get_recipes, get_recipe, get_ingredient_map, consume_ingredient,
    plant_seed, plant_stage_info, harvest_plant,
    get_inventory, get_item, get_item_by_name,
    remove_inventory_item, add_inventory_item, remove_ap, add_ap,
    get_inventory_item, user_has_status_tag, log_activity,
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
}
FURNITURE_BY_ITEM = {v: k for k, v in FURNITURE_BY_EXPANSION.items()}

EXPANSION_LABELS = {
    "kitchen": "🍳 Кухня",
    "workbench": "🔧 Верстак",
    "plant_pot": "🌱 Кадка для растений",
}

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

FRIED_PREFIX = "Жареный "
FOOD_EXPIRY_SEC = 4 * 86400          # 96 часов

# Защита от двойного крафта
CRAFTING: set = set()

# Отрисованное сообщение жилья: user_id → (chat_id, message_id)
_HMSG: dict = {}


# ───────── вспомогательные ─────────

def _housing_photo(htype: str):
    key = HOUSING_PHOTOS.get(htype)
    if not key:
        return None
    path = resolve_image(key)
    return path if os.path.isfile(path) else None


def _slot_icon(et):
    return {"kitchen": "🍳", "workbench": "🔧", "plant_pot": "🌱"}.get(et, "📦")


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

@router.callback_query(F.data == "housing:menu")
async def housing_menu(cb: CallbackQuery):
    await cb.answer()
    uid = cb.from_user.id
    if not await user_has_status_tag(uid, "recruit"):
        await cb.answer("❌ Жильё доступно только рекрутам и пилотам.", show_alert=True)
        return
    h = await get_player_housing(uid)
    ht = h["housing_type"]
    info = HOUSING_TYPES[ht]
    slots = await get_housing_slots(uid)

    lines = [f"🏠 *{info['name']}*"]
    if info.get("desc"):
        lines.append(info["desc"])
    lines.append(f"Комнат-слотов: {len(slots)}/{info['slots']}\n")
    rows = []
    for i in range(info["slots"]):
        s = slots.get(i)
        if s and s.get("expansion_type"):
            label = f"{_slot_icon(s['expansion_type'])} {_slot_name(s)}  ·  слот {i+1}"
        else:
            label = f"⬜ Пусто  ·  слот {i+1}"
        rows.append([_inv_row(label, f"housing:room:{i}")])

    # Кнопка «Перееезд» — если в инвентаре есть жильё более высокого типа
    inv = await get_inventory(uid)
    free = info["slots"] - sum(1 for s in slots.values() if s.get("expansion_type"))
    if free == 0 and any(i["category"] == "furniture" for i in inv):
        lines.append("⚠️ В инвентаре есть мебель, но все слоты заняты.")
    cur_idx = HOUSING_ORDER.index(ht)
    for item in inv:
        if item["category"] != "housing":
            continue
        target = HOUSING_ITEM_BY_NAME.get(item["name"])
        if target and HOUSING_ORDER.index(target) > cur_idx:
            rows.append([_inv_row(
                f"🏠 Переехать в «{item['name']}»",
                f"housing:move:{item['id']}")])

    rows.append([_inv_row("🔙 В город", "city:menu")])
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    await _paint(cb, "\n".join(lines), _housing_photo(ht), kb)


# ───────── комната ─────────

@router.callback_query(F.data.startswith("housing:room:"))
async def housing_room(cb: CallbackQuery):
    await cb.answer()
    uid = cb.from_user.id
    idx = int(cb.data.split(":")[2])
    h = await get_player_housing(uid)
    ht = h["housing_type"]
    info = HOUSING_TYPES[ht]
    if idx >= info["slots"]:
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
    else:
        kb = InlineKeyboardMarkup(inline_keyboard=[[_inv_row("🔙 К жилью", "housing:menu")]])
        await _paint(cb, "Неизвестное расширение.", _housing_photo(ht), kb)


async def _room_kitchen(cb, uid, idx, slot, ht, lvl):
    recipes = await get_recipes("kitchen", lvl)
    title = _slot_name(slot)
    lines = [f"🍳 *{title}* (слот {idx+1})\n"]
    if not recipes:
        lines.append("Нет доступных рецептов.")
    else:
        lines.append("Доступные рецепты:")
        for r in recipes:
            lines.append(f"  • {r['name']}")

    rows = []
    for r in recipes:
        rows.append([_inv_row(f"📋 {r['name']}", f"housing:recipe:{idx}:{r['id']}")])
    if slot.get("embedded"):
        lines.append("\n⚙️ Встроено в жильё — убрать нельзя.")
    else:
        rows.append([_inv_row("🔪 Убрать из слота", f"housing:uninstall:{idx}")])
    rows.append([_inv_row("🔙 К жилью", "housing:menu")])
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    await _paint(cb, "\n".join(lines), _housing_photo(ht), kb)


async def _room_workbench(cb, uid, idx, slot, ht, lvl):
    recipes = await get_recipes("workbench", lvl)
    lines = [f"🔧 *Верстак* (слот {idx+1})\n"]
    if not recipes:
        lines.append("Нет доступных рецептов.")
    else:
        lines.append("Доступные рецепты:")
        for r in recipes:
            lines.append(f"  • {r['name']}")

    rows = []
    for r in recipes:
        rows.append([_inv_row(f"📋 {r['name']}", f"housing:recipe:{idx}:{r['id']}")])
    rows.append([_inv_row("🔪 Убрать из слота", f"housing:uninstall:{idx}")])
    rows.append([_inv_row("🔙 К жилью", "housing:menu")])
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    await _paint(cb, "\n".join(lines), _housing_photo(ht), kb)


async def _room_plant(cb, uid, idx, slot, ht):
    data = {}
    try:
        data = json.loads(slot.get("plant_data") or "{}")
    except Exception:
        pass

    seed_name = data.get("seed")
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
        rows.append([_inv_row("🔪 Убрать кадку", f"housing:uninstall:{idx}")])
        rows.append([_inv_row("🔙 К жилью", "housing:menu")])
        kb = InlineKeyboardMarkup(inline_keyboard=rows)
        await _paint(cb, "\n".join(lines), _housing_photo(ht), kb)
        return

    now = time.time()
    info = plant_stage_info(data, now)
    stage = info["stage"]
    stage_name = PLANT_STAGES[stage][0]
    fruits = info["fruits"]
    next_in = info["next_in"]

    lines = [f"🌱 *Растение: {seed_name}*\nСтадия: {stage_name}"]
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
    rows.append([_inv_row("🔪 Убрать кадку", f"housing:uninstall:{idx}")])
    rows.append([_inv_row("🔙 К жилью", "housing:menu")])
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    await _paint(cb, "\n".join(lines), _housing_photo(ht), kb)


# ───────── карточка рецепта ─────────

@router.callback_query(F.data.startswith("housing:recipe:"))
async def housing_recipe(cb: CallbackQuery):
    await cb.answer()
    uid = cb.from_user.id
    _, _, idx_s, rid_s = cb.data.split(":")
    idx, rid = int(idx_s), int(rid_s)

    r = await get_recipe(rid)
    if not r:
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
    await cb.answer()
    uid = cb.from_user.id
    if uid in CRAFTING:
        await cb.answer("⏳ Уже готовишься!", show_alert=True)
        return

    _, _, idx_s, rid_s = cb.data.split(":")
    idx, rid = int(idx_s), int(rid_s)
    r = await get_recipe(rid)
    if not r:
        return

    # Проверяем слот и тип расширения
    slots = await get_housing_slots(uid)
    slot = slots.get(idx)
    if not slot or slot.get("expansion_type") != r["required_expansion"]:
        await cb.answer("❌ Это расширение не подходит для рецепта.", show_alert=True)
        return

    ingredients = json.loads(r["ingredients"] or "[]")
    inv_map = await get_ingredient_map(uid)
    for ing_name, qty in ingredients:
        if inv_map.get(ing_name, 0) < qty:
            await cb.answer(f"❌ Нет «{ing_name}»!", show_alert=True)
            return

    # Снимаем ОД и ингредиенты
    if not await remove_ap(uid, r["ap_cost"]):
        await cb.answer("❌ Не хватает ОД!", show_alert=True)
        return

    for ing_name, qty in ingredients:
        if not await consume_ingredient(uid, ing_name, qty):
            await cb.answer(f"❌ Не удалось списать «{ing_name}»!", show_alert=True)
            return

    CRAFTING.add(uid)
    try:
        wait = r["production_time"]
        h = await get_player_housing(uid)
        photo = _housing_photo(h["housing_type"])

        # Показать прогресс
        progress_lines = [
            f"🏭 *Готовлю «{r['name']}»…*\n",
            "⏳ ·",
        ]
        kb_wait = InlineKeyboardMarkup(inline_keyboard=[
            [_inv_row("⏳ Приготовление…", "housing:noop")]])
        if photo and os.path.isfile(photo):
            await cb.bot.send_photo(cb.message.chat.id, FSInputFile(photo),
                                    caption="\n".join(progress_lines),
                                    reply_markup=kb_wait)
        else:
            await cb.bot.send_message(cb.message.chat.id,
                                      "\n".join(progress_lines),
                                      reply_markup=kb_wait)

        # Анимация шагами
        dots = ["⏳ ·", "⏳ ··", "⏳ ···"]
        for d in dots:
            await asyncio.sleep(wait / 3)

        await asyncio.sleep(wait % 3)

        result_name = r["result_item_name"]
        result_qty = r["result_quantity"]
        result_item = await get_item_by_name(result_name)
        if not result_item:
            await cb.bot.send_message(cb.message.chat.id, f"❌ Предмет «{result_name}» не найден.")
            return

        # Жареная рыба — срок годности 96 часов
        expires_at = None
        if result_name.startswith(FRIED_PREFIX):
            expires_at = str(int(time.time()) + FOOD_EXPIRY_SEC)

        await add_inventory_item(uid, result_item["id"], result_qty, expires_at=expires_at)

        lines = [f"✅ *{result_name}* готово!",
                 f"Количество: ×{result_qty}"]
        if expires_at:
            lines.append("⏳ Срок годности: 96 часов")
        lines.append("\nДобавлено в инвентарь.")

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [_inv_row("🏠 К жилью", "housing:menu")]])
        await cb.bot.send_message(cb.message.chat.id, "\n".join(lines), reply_markup=kb)

    finally:
        CRAFTING.discard(uid)


@router.callback_query(F.data == "housing:noop")
async def noop_handler(cb: CallbackQuery):
    await cb.answer("⏳ Приготовление…")


# ───────── установка расширения ─────────

@router.callback_query(F.data.startswith("housing:install:"))
async def housing_install(cb: CallbackQuery):
    await cb.answer()
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

    inv = await get_inventory(uid)
    furniture = [i for i in inv if i["category"] == "furniture"]
    lines = ["➕ *Установить расширение*\nВыбери мебель из инвентаря:"]
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
    await cb.answer()
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

    # Кухня: замена старой (возврат в инвентарь). Встроенную кухню студии не трогаем.
    if et == "kitchen":
        for i, s in sorted(slots.items()):
            if (not s.get("embedded")
                    and s.get("expansion_type") == "kitchen"
                    and s.get("expansion_level", 1) < lvl):
                old_name = FURNITURE_BY_EXPANSION.get(("kitchen", s["expansion_level"]))
                await set_housing_slot(uid, i, et, lvl)
                await remove_inventory_item(uid, item_id, 1)
                if old_name:
                    old_item = await get_item_by_name(old_name)
                    if old_item:
                        await add_inventory_item(uid, old_item["id"], 1)
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

    await set_housing_slot(uid, empty, et, lvl)
    await remove_inventory_item(uid, item_id, 1)
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
    lvl = slot.get("expansion_level", 1)
    fname = FURNITURE_BY_EXPANSION.get((et, lvl))
    await set_housing_slot(uid, idx, None)
    if fname:
        fi = await get_item_by_name(fname)
        if fi:
            await add_inventory_item(uid, fi["id"], 1)

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

    target = HOUSING_ITEM_BY_NAME.get(item["name"])
    if not target:
        return

    h = await get_player_housing(uid)
    current_idx = HOUSING_ORDER.index(h["housing_type"])
    target_idx = HOUSING_ORDER.index(target)
    if target_idx <= current_idx:
        await cb.answer("❌ Нельзя переехать в жильё того же типа или ниже.", show_alert=True)
        return

    # Все текущие расширения возвращаются в инвентарь (кроме встроенных)
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

    await remove_inventory_item(uid, item_id, 1)
    await set_player_housing(uid, target)

    # Студия поставляется с встроенной кухней (социальная программа «Забота Нордхайма»)
    if target == "studio":
        await set_housing_slot(uid, 0, "kitchen", 1, embedded=True)

    await log_activity(uid, "housing_move", target)

    new_name = HOUSING_TYPES[target]["name"]
    await cb.answer(f"🎉 Переезд в «{new_name}» завершён!", show_alert=True)
    await housing_menu(cb)
