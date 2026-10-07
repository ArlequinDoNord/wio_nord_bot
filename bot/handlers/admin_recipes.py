"""
Менеджер рецептов крафта (v0.22.13): создание, правка и удаление рецептов.

Рецепты живут в таблице recipes наравне с сидированными (RECIPES_DEF), но
ensure_recipes() их не перезатирает — она работает только по RECIPES_DEF
(по имени+расширению+уровню), поэтому менеджерные строки не трогаются.

Возможности:
- создание: название, картинка результата, ингредиенты (циклом «название:кол-во»),
  результат — существующий предмет ИЛИ новый (мини-визард характеристик и фото),
  расширение/уровень, ОД, время крафта, редкость, кол-во результата, цена
  товара-рецепта «Рецепт: <название>» в лавке (0 — не продавать);
- правка: все поля карточки по одному + быстрые кнопки расширения/редкости,
  показать/скрыть, перевыбор результата и переписывание ингредиентов;
- удаление: скрытие рецепта и его товара (строки не трогаем — на id ссылаются
  выученные user_recipes).

Вход — из админ-панели (кнопка «📜 Менеджер рецептов», can_manage_shop).
Всё пространство callbacks живёт под префиксом recadm: — оно не пересекается
с админкой (admin.py) и снимает риск перехвата в smoke_127.
"""

import json
import re

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.db import (
    get_item_by_name, get_recipe, list_recipes_for_admin,
    upsert_recipe, ensure_recipe_shop_item, delete_recipe,
    find_recipe, set_recipe_visible, add_item,
)
from utils.permissions import has_permission, log_action
from utils.helpers import edit_message_safe
from keyboards.keyboards import cancel_keyboard
from config import RARITY_LEVELS, RARITY_EMOJI, ITEM_CATEGORIES

router = Router()

RECIPES_PER_PAGE = 8

EXPANSION_LABELS = {
    "kitchen": "🍳 Кухня",
    "workbench": "🔧 Верстак",
}

RESULT_CATEGORIES = {
    "consumable": "🍗 Расходники",
    "equipment": "🧥 Одежда",
    "weapon": "⚔️ Оружие",
    "special": "📦 Особое",
}

RARITY_MAX = 5


class RecipeManager(StatesGroup):
    # создание (и переиспользование для правки структурных полей)
    ing = State()           # ингредиенты: «название:кол-во», кнопка «готово»
    res_mode = State()      # результат: существующий / новый
    res_pick = State()      # ввод имени существующего результата
    # мини-визард нового предмета-результата
    n_name = State()
    n_desc = State()
    n_cat = State()
    n_heal = State()
    n_regen = State()
    n_ap = State()
    n_armor = State()
    n_dmg = State()
    n_drink = State()
    n_price = State()
    n_rarity = State()
    n_photo = State()
    # параметры рецепта
    c_exp = State()
    c_lvl = State()
    c_ap = State()
    c_time = State()
    c_rarity = State()
    c_qty = State()
    c_shop = State()
    c_confirm = State()
    # правка скалярных полей
    e_value = State()


# ---------- helpers ----------

async def _ok(callback: CallbackQuery) -> bool:
    """Проверка прав менеджера (can_manage_shop) + ответ на нажатие."""
    if not await has_permission(callback.from_user.id, "can_manage_shop"):
        await callback.answer("❌ Нет прав (can_manage_shop).", show_alert=True)
        return False
    await callback.answer()
    return True


def _new_draft() -> dict:
    return {
        "ctx": "create",
        "rid": None,
        "name": "",
        "description": "",
        "ingredients": [],
        "result_mode": "existing",
        "result_item_name": None,
        "newitem": None,
        "exp": None,
        "lvl": 1,
        "ap": 0,
        "time": 30,
        "rarity": 1,
        "qty": 1,
        "shop": 0,
    }


def _parse_ingredient(text: str):
    """«Название:3» или «Название 3» -> (name, qty); None если не распарсилось."""
    text = text.strip()
    if not text:
        return None
    m = re.match(r"^(.+?)\s*[:]\s*(\d+)$", text) or re.match(r"^(.+?)\s+(\d+)$", text)
    if not m:
        return None
    name = m.group(1).strip()
    qty = int(m.group(2))
    if not name or qty <= 0:
        return None
    return name, qty


def _ingredients_str(recipe) -> str:
    try:
        lst = json.loads(recipe.get("ingredients") or "[]")
    except (TypeError, ValueError):
        lst = []
    return ", ".join(f"{n} × {q}" for n, q in lst)


def _rarity_buttons(prefix: str, extra: str = "") -> list:
    rows = []
    row = []
    for r in range(1, RARITY_MAX + 1):
        row.append(InlineKeyboardButton(
            text=f"{RARITY_EMOJI[r]} {RARITY_LEVELS[r]}",
            callback_data=f"recadm:{prefix}:{r}{extra}"))
    return [row]


async def _show_recipe_card(msg, rid: int, state: FSMContext = None):
    """Карточка рецепта с кнопками правки (правка + показать/скрыть + удаление)."""
    recipe = await get_recipe(rid)
    if not recipe:
        await msg.answer("❌ Рецепт не найден. Он удалён?")
        return
    exp = EXPANSION_LABELS.get(recipe['required_expansion'] or '', recipe['required_expansion'] or '?')
    status = "✅ доступен" if recipe['is_available'] else "⛔ скрыт"
    result = recipe['result_item_name'] or "—"
    text = (
        f"📜 Рецепт #{recipe['id']} — {recipe['name']}\n\n"
        f"📍 {exp} · уровень {recipe['required_level']}\n"
        f"{'✅ ' if recipe['is_available'] else '⛔ '}Статус: {status}\n"
        f"🔁 {_ingredients_str(recipe) or '—'}\n"
        f"📦 Результат: {result} × {recipe['result_quantity']}\n"
        f"⚡ {recipe['ap_cost']} ОД · ⏱ {recipe['production_time']} сек\n"
        f"💎 {RARITY_EMOJI.get(recipe['rarity'], '?')} {RARITY_LEVELS.get(recipe['rarity'], recipe['rarity'])}\n"
    )
    if recipe.get('description'):
        text += f"\n📝 {recipe['description']}"
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Название", callback_data=f"recadm:ef:name:{rid}")],
        [InlineKeyboardButton(text="📝 Описание", callback_data=f"recadm:ef:desc:{rid}")],
        [InlineKeyboardButton(text="🧪 Ингредиенты", callback_data=f"recadm:ei:{rid}")],
        [InlineKeyboardButton(text="📦 Результат", callback_data=f"recadm:er:{rid}")],
        [InlineKeyboardButton(text="⚡ ОД", callback_data=f"recadm:ef:ap:{rid}"),
         InlineKeyboardButton(text="⏱ Время", callback_data=f"recadm:ef:time:{rid}")],
        [InlineKeyboardButton(text="🏠 Расширение", callback_data=f"recadm:es:{rid}"),
         InlineKeyboardButton(text="🔓 Уровень", callback_data=f"recadm:ef:lvl:{rid}")],
        [InlineKeyboardButton(text="💎 Редкость", callback_data=f"recadm:eq:{rid}"),
         InlineKeyboardButton(text="🔢 Кол-во", callback_data=f"recadm:ef:qty:{rid}")],
        [InlineKeyboardButton(text="🏷 Цена «Рецепт: X»", callback_data=f"recadm:ef:shop:{rid}")],
        [InlineKeyboardButton(text="👁 Скрыть" if recipe['is_available'] else "👁 Показать",
                              callback_data=f"recadm:et:{rid}"),
         InlineKeyboardButton(text="🗑 Удалить", callback_data=f"recadm:ed:{rid}")],
        [InlineKeyboardButton(text="🔙 К списку", callback_data="recadm:list")],
    ])
    if state is not None:
        await state.clear()
    await edit_message_safe(msg, text, markup)


async def _show_list(callback: CallbackQuery, page: int):
    recipes = await list_recipes_for_admin()
    total = len(recipes)
    pages = max(1, (total + RECIPES_PER_PAGE - 1) // RECIPES_PER_PAGE)
    page = max(0, min(page, pages - 1))
    rows = []
    for r in recipes[page * RECIPES_PER_PAGE: page * RECIPES_PER_PAGE + RECIPES_PER_PAGE]:
        exp = EXPANSION_LABELS.get(r['required_expansion'] or '', '?')
        mark = "⛔ " if not r['is_available'] else ""
        label = f"{mark}{r['name']} · {exp} {r['required_level']}"
        rows.append([InlineKeyboardButton(text=label, callback_data=f"recadm:open:{r['id']}")])
    nav = [InlineKeyboardButton(text="⬅️", callback_data=f"recadm:page:{page - 1}")]
    nav.append(InlineKeyboardButton(text=f"{page + 1}/{pages}", callback_data="recadm:noop"))
    nav.append(InlineKeyboardButton(text="➡️", callback_data=f"recadm:page:{page + 1}"))
    rows.append(nav)
    rows.append([
        InlineKeyboardButton(text="➕ Создать рецепт", callback_data="recadm:create"),
        InlineKeyboardButton(text="🔙 В менеджер", callback_data="recadm:menu"),
    ])
    text = f"📜 Рецепты крафта — всего {total}:\n\n"
    text += f"Страница {page + 1} из {pages}. ⛔ — скрытые."
    await edit_message_safe(callback.message, text,
                            InlineKeyboardMarkup(inline_keyboard=rows))


async def _resolve_result(state: FSMContext, callback: CallbackQuery):
    """Результат выбран (существующий предмет). Зависит от контекста: создание
    идёт дальше по визарду, правка — сразу сохраняет результат в карточке."""
    d = (await state.get_data()).get("d", {})
    if d.get("ctx") == "edit":
        rid = d["rid"]
        recipe = dict(await get_recipe(rid))
        if not recipe:
            await callback.message.answer("❌ Рецепт не найден.")
            await state.clear()
            return
        recipe["result_item_name"] = d["result_item_name"]
        await upsert_recipe(
            recipe["name"], recipe["description"], recipe["result_item_name"],
            recipe["result_quantity"], recipe["required_expansion"],
            recipe["required_level"], json.loads(recipe["ingredients"]),
            recipe["ap_cost"], recipe["production_time"], recipe["rarity"],
            recipe_id=rid)
        await state.clear()
        await _show_recipe_card(callback.message, rid)
    else:
        await state.set_state(RecipeManager.c_exp)
        await callback.message.answer(
            "🏠 На каком расширении крафтится?",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=v, callback_data=f"recadm:exp:{k}")]
                for k, v in EXPANSION_LABELS.items()
            ] + [[InlineKeyboardButton(text="❌ Отмена", callback_data="recadm:cancel")]])
        )


async def _newitem_done(message, state: FSMContext, photo: str = None):
    """Мини-визард нового предмета-результата завершён."""
    d = (await state.get_data()).get("d", {})
    ni = d.get("newitem") or {}
    ni["photo"] = photo
    d["newitem"] = ni
    d["result_mode"] = "new"
    d["result_item_name"] = ni["name"]
    await state.update_data(d=d)
    if d.get("ctx") == "edit":
        rid = d["rid"]
        recipe = dict(await get_recipe(rid))
        if not recipe:
            await message.answer("❌ Рецепт не найден.")
            await state.clear()
            return
        await add_item(
            ni["name"], ni.get("desc") or "", ni.get("price") or 0,
            (ni.get("price") or 0) // 2, ni.get("rarity", 1), ni["cat"], -1,
            message.from_user.id, photo, ap_cost=ni.get("ap") or 0,
            heal=ni.get("heal") or 0, regen=ni.get("regen") or 0,
            armor=ni.get("armor") or 0, damage=ni.get("dmg") or 0,
            drink_effect=ni.get("drink") or None)
        recipe["result_item_name"] = ni["name"]
        await upsert_recipe(
            recipe["name"], recipe["description"], recipe["result_item_name"],
            recipe["result_quantity"], recipe["required_expansion"],
            recipe["required_level"], json.loads(recipe["ingredients"]),
            recipe["ap_cost"], recipe["production_time"], recipe["rarity"],
            recipe_id=rid)
        await state.clear()
        await message.answer(f"✅ Предмет «{ni['name']}» создан и привязан к рецепту.")
        await _show_recipe_card(callback_message(message), rid)
        return
    await state.set_state(RecipeManager.c_exp)
    await message.answer(
        "🏠 На каком расширении крафтится?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=v, callback_data=f"recadm:exp:{k}")]
            for k, v in EXPANSION_LABELS.items()
        ] + [[InlineKeyboardButton(text="❌ Отмена", callback_data="recadm:cancel")]])
    )


def callback_message(msg):
    """Подойдёт для .answer: Message и CallbackQuery.message имеют .answer() у
    Message. В edit-ветке нового результата у нас обычное Message или CallbackQuery."""
    return msg


def _int(text, lo=None, hi=None):
    try:
        v = int(text.strip().replace(" ", ""))
    except (TypeError, ValueError):
        return None
    if lo is not None and v < lo:
        return None
    if hi is not None and v > hi:
        return None
    return v


# ---------- вход и список ----------

@router.callback_query(F.data == "recadm:noop")
async def recadm_noop(callback: CallbackQuery):
    await callback.answer()


@router.callback_query(F.data == "recadm:menu")
async def recadm_menu(callback: CallbackQuery, state: FSMContext):
    if not await _ok(callback):
        return
    await state.clear()
    text = (
        "📜 МЕНЕДЖЕР РЕЦЕПТОВ\n\n"
        "Рецепты крафта (кухня/верстак) — здесь можно добавить, поправить и "
        "удалить рецепт. Удаление скрывает рецепт и его товар из лавки."
    )
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📜 Список рецептов", callback_data="recadm:list")],
        [InlineKeyboardButton(text="➕ Создать рецепт", callback_data="recadm:create")],
        [InlineKeyboardButton(text="🔙 В админ-панель", callback_data="admin:menu")],
    ])
    await edit_message_safe(callback.message, text, markup)


@router.callback_query(F.data == "recadm:list")
async def recadm_list(callback: CallbackQuery, state: FSMContext):
    if not await _ok(callback):
        return
    await state.clear()
    await _show_list(callback, 0)


@router.callback_query(F.data.startswith("recadm:page:"))
async def recadm_page(callback: CallbackQuery, state: FSMContext):
    if not await _ok(callback):
        return
    try:
        page = int(callback.data.split(":")[-1])
    except ValueError:
        page = 0
    await _show_list(callback, page)


@router.callback_query(F.data.startswith("recadm:open:"))
async def recadm_open(callback: CallbackQuery, state: FSMContext):
    if not await _ok(callback):
        return
    try:
        rid = int(callback.data.split(":")[-1])
    except ValueError:
        return
    await _show_recipe_card(callback.message, rid, state)


@router.callback_query(F.data == "recadm:create")
async def recadm_create(callback: CallbackQuery, state: FSMContext):
    if not await _ok(callback):
        return
    await state.set_state(RecipeManager.ing)
    await state.update_data(d=_new_draft())
    await callback.message.answer(
        "🧪 Новый рецепт. Вводи ингредиенты по одному: <b>Название:количество</b>\n"
        "Например: <code>Сиг:1</code> или <code>Соль 1</code>.\n"
        "Когда список готов — нажми «✅ Готово».",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Готово", callback_data="recadm:ing_done")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="recadm:cancel")],
        ]),
    )


# ---------- создание: ингредиенты ----------

@router.message(RecipeManager.ing)
async def recadm_ing_add(message: Message, state: FSMContext):
    parsed = _parse_ingredient(message.text or "")
    if not parsed:
        await message.answer(
            "❌ Не понял. Формат: <code>Название:3</code> или <code>Название 3</code>.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ Готово", callback_data="recadm:ing_done")],
            ]),
        )
        return
    name, qty = parsed
    data = await state.get_data()
    d = data.get("d", _new_draft())
    ing = [list(x) for x in d["ingredients"]]
    merged = False
    for i in ing:
        if i[0] == name:
            i[1] += qty
            merged = True
            break
    if not merged:
        ing.append([name, qty])
    d["ingredients"] = ing
    await state.update_data(d=d)
    listed = ", ".join(str(x[0]) + "×" + str(x[1]) for x in ing)
    await message.answer(
        f"✅ {name} × {qty} {'обновлён' if merged else 'добавлен'}.\n"
        f"Список: {listed}\n"
        "Введи следующий или нажми «✅ Готово».",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Готово", callback_data="recadm:ing_done")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="recadm:cancel")],
        ]),
    )


@router.callback_query(F.data == "recadm:ing_done")
async def recadm_ing_done(callback: CallbackQuery, state: FSMContext):
    if not await _ok(callback):
        return
    d = (await state.get_data()).get("d", _new_draft())
    if not d["ingredients"]:
        await callback.message.answer("❌ Добавь хотя бы один ингредиент.")
        return
    if d.get("ctx") == "edit":
        rid = d["rid"]
        recipe = dict(await get_recipe(rid))
        recipe["ingredients"] = json.dumps(d["ingredients"], ensure_ascii=False)
        await upsert_recipe(
            recipe["name"], recipe["description"], recipe["result_item_name"],
            recipe["result_quantity"], recipe["required_expansion"],
            recipe["required_level"], json.loads(recipe["ingredients"]),
            recipe["ap_cost"], recipe["production_time"], recipe["rarity"],
            recipe_id=rid)
        await state.clear()
        await _show_recipe_card(callback.message, rid)
        return
    await state.set_state(RecipeManager.res_mode)
    await callback.message.answer(
        "📦 Результат крафта — что получаем?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🎯 Взять существующий предмет",
                                  callback_data="recadm:res_existing")],
            [InlineKeyboardButton(text="➕ Создать новый предмет",
                                  callback_data="recadm:res_new")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="recadm:cancel")],
        ]),
    )


@router.callback_query(F.data == "recadm:res_existing")
async def recadm_res_existing(callback: CallbackQuery, state: FSMContext):
    if not await _ok(callback):
        return
    await state.set_state(RecipeManager.res_pick)
    await callback.message.answer(
        "🎯 Введи ТОЧНОЕ название предмета-результата из каталога.\n"
        "Например: <code>Рыбный пирог</code>",
        reply_markup=cancel_keyboard(),
    )


@router.message(RecipeManager.res_pick)
async def recadm_res_pick(message: Message, state: FSMContext):
    d = (await state.get_data()).get("d", _new_draft())
    name = (message.text or "").strip()
    if not name:
        await message.answer("❌ Пустое название.")
        return
    item = await get_item_by_name(name)
    if not item:
        await message.answer(
            f"❌ Предмет «{name}» не найден в каталоге.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="➕ Создать новый предмет",
                                      callback_data="recadm:res_new")],
                [InlineKeyboardButton(text="↩ Попробовать ещё раз",
                                      callback_data="recadm:res_existing")],
            ]),
        )
        return
    d["result_item_name"] = name
    d["result_mode"] = "existing"
    await state.update_data(d=d)
    await _resolve_result(state, _Msg(message))


class _Msg:
    """Обёртка Message под API callback (message.answer)."""
    def __init__(self, message):
        self.message = message


# ---------- создание: новый предмет-результат ----------

@router.callback_query(F.data == "recadm:res_new")
async def recadm_res_new(callback: CallbackQuery, state: FSMContext):
    if not await _ok(callback):
        return
    await state.set_state(RecipeManager.n_name)
    await callback.message.answer(
        "➕ Новый предмет. Шаг 1/12 — НАЗВАНИЕ предмета-результата:",
        reply_markup=cancel_keyboard(),
    )


@router.message(RecipeManager.n_name)
async def recadm_n_name(message: Message, state: FSMContext):
    name = (message.text or "").strip()
    if not name:
        await message.answer("❌ Пустое название.")
        return
    if await get_item_by_name(name):
        await message.answer(
            f"❌ Предмет «{name}» уже существует. Выбери его как существующий "
            "результат в меню результата.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🎯 Взять существующий",
                                      callback_data="recadm:res_existing")],
            ]),
        )
        return
    d = (await state.get_data()).get("d", _new_draft())
    ni = d.get("newitem") or {}
    ni["name"] = name
    d["newitem"] = ni
    await state.update_data(d=d)
    await state.set_state(RecipeManager.n_desc)
    await message.answer("➋ ОПИСАНИЕ предмета (или «-» если нет):",
                         reply_markup=cancel_keyboard())


@router.message(RecipeManager.n_desc)
async def recadm_n_desc(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    d = (await state.get_data()).get("d", _new_draft())
    ni = d.get("newitem") or {}
    ni["desc"] = None if text == "-" else text
    d["newitem"] = ni
    await state.update_data(d=d)
    await state.set_state(RecipeManager.n_cat)
    await message.answer(
        "➌ КАТЕГОРИЯ предмета:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=v, callback_data=f"recadm:cat:{k}")]
            for k, v in RESULT_CATEGORIES.items()
        ] + [[InlineKeyboardButton(text="❌ Отмена", callback_data="recadm:cancel")]]),
    )


@router.callback_query(F.data.startswith("recadm:cat:"))
async def recadm_n_cat(callback: CallbackQuery, state: FSMContext):
    if not await _ok(callback):
        return
    cat = callback.data.split(":")[-1]
    if cat not in RESULT_CATEGORIES:
        return
    d = (await state.get_data()).get("d", _new_draft())
    ni = d.get("newitem") or {}
    ni["cat"] = cat
    d["newitem"] = ni
    await state.update_data(d=d)
    await state.set_state(RecipeManager.n_heal)
    await callback.message.answer(
        "➍ HP предмета (лечение в бою подземелья; число, 0 если нет):",
        reply_markup=cancel_keyboard(),
    )


@router.message(RecipeManager.n_heal)
async def recadm_n_heal(message: Message, state: FSMContext):
    v = _int(message.text)
    if v is None:
        await message.answer("❌ Введи целое число (0 — если нет healing).")
        return
    d = (await state.get_data()).get("d", _new_draft())
    ni = d.get("newitem") or {}
    ni["heal"] = v
    d["newitem"] = ni
    await state.update_data(d=d)
    await state.set_state(RecipeManager.n_regen)
    await message.answer(
        "➎ РЕГЕНЕРАЦИЯ — % от лечения, тиками 3 хода (как у рыбного пирога; "
        "0 если нет):",
        reply_markup=cancel_keyboard(),
    )


@router.message(RecipeManager.n_regen)
async def recadm_n_regen(message: Message, state: FSMContext):
    v = _int(message.text, lo=0)
    if v is None:
        await message.answer("❌ Введи целое число от 0.")
        return
    d = (await state.get_data()).get("d", _new_draft())
    ni = d.get("newitem") or {}
    ni["regen"] = v
    d["newitem"] = ni
    await state.update_data(d=d)
    await state.set_state(RecipeManager.n_ap)
    await message.answer(
        "➏ ЭФФЕКТ ОД (восстанавливает ОД при использовании; 0 если нет):",
        reply_markup=cancel_keyboard(),
    )


@router.message(RecipeManager.n_ap)
async def recadm_n_ap(message: Message, state: FSMContext):
    v = _int(message.text, lo=0)
    if v is None:
        await message.answer("❌ Введи целое число от 0.")
        return
    d = (await state.get_data()).get("d", _new_draft())
    ni = d.get("newitem") or {}
    ni["ap"] = v
    d["newitem"] = ni
    await state.update_data(d=d)
    await state.set_state(RecipeManager.n_armor)
    await message.answer("➐ БРОНЯ (для одежды; 0 если нет):", reply_markup=cancel_keyboard())


@router.message(RecipeManager.n_armor)
async def recadm_n_armor(message: Message, state: FSMContext):
    v = _int(message.text, lo=0)
    if v is None:
        await message.answer("❌ Введи целое число от 0.")
        return
    d = (await state.get_data()).get("d", _new_draft())
    ni = d.get("newitem") or {}
    ni["armor"] = v
    d["newitem"] = ni
    await state.update_data(d=d)
    await state.set_state(RecipeManager.n_dmg)
    await message.answer("➑ УРОН (для оружия; 0 если нет):", reply_markup=cancel_keyboard())


@router.message(RecipeManager.n_dmg)
async def recadm_n_dmg(message: Message, state: FSMContext):
    v = _int(message.text, lo=0)
    if v is None:
        await message.answer("❌ Введи целое число от 0.")
        return
    d = (await state.get_data()).get("d", _new_draft())
    ni = d.get("newitem") or {}
    ni["dmg"] = v
    d["newitem"] = ni
    await state.update_data(d=d)
    await state.set_state(RecipeManager.n_drink)
    await message.answer(
        "➒ ЭФФЕКТ НАПИТКА (текст, напр. «+50 ОД» при употреблении; «-» если не напиток):",
        reply_markup=cancel_keyboard(),
    )


@router.message(RecipeManager.n_drink)
async def recadm_n_drink(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    d = (await state.get_data()).get("d", _new_draft())
    ni = d.get("newitem") or {}
    ni["drink"] = None if text == "-" else text
    d["newitem"] = ni
    await state.update_data(d=d)
    await state.set_state(RecipeManager.n_price)
    await message.answer(
        "➓ ЦЕНА в Нордмарках (для «Продать товару»; 0 — не продаётся):",
        reply_markup=cancel_keyboard(),
    )


@router.message(RecipeManager.n_price)
async def recadm_n_price(message: Message, state: FSMContext):
    v = _int(message.text, lo=0)
    if v is None:
        await message.answer("❌ Введи целое число от 0.")
        return
    d = (await state.get_data()).get("d", _new_draft())
    ni = d.get("newitem") or {}
    ni["price"] = v
    d["newitem"] = ni
    await state.update_data(d=d)
    await state.set_state(RecipeManager.n_rarity)
    await message.answer(
        "💎 Редкость нового предмета:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=_rarity_buttons("newrar")
                                          + [[InlineKeyboardButton(text="❌ Отмена",
                                                                   callback_data="recadm:cancel")]]),
    )


@router.callback_query(F.data.startswith("recadm:newrar:"))
async def recadm_n_rarity(callback: CallbackQuery, state: FSMContext):
    if not await _ok(callback):
        return
    v = callback.data.split(":")[-1]
    if not v.isdigit():
        return
    d = (await state.get_data()).get("d", _new_draft())
    ni = d.get("newitem") or {}
    ni["rarity"] = int(v)
    d["newitem"] = ni
    await state.update_data(d=d)
    await state.set_state(RecipeManager.n_photo)
    await callback.message.answer(
        "🖼 Фото предмета (пришли картинку) или «🚫 Без фото»:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🚫 Без фото", callback_data="recadm:no_photo")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="recadm:cancel")],
        ]),
    )


@router.message(RecipeManager.n_photo, F.photo)
async def recadm_n_photo(message: Message, state: FSMContext):
    photo = (message.photo or [None])[-1]
    await _newitem_done(message, state, photo.file_id if photo else None)


@router.callback_query(F.data == "recadm:no_photo")
async def recadm_no_photo(callback: CallbackQuery, state: FSMContext):
    if not await _ok(callback):
        return
    await _newitem_done(callback.message, state, None)


# ---------- создание: параметры рецепта ----------

@router.callback_query(F.data.startswith("recadm:exp:"))
async def recadm_exp(callback: CallbackQuery, state: FSMContext):
    if not await _ok(callback):
        return
    value = callback.data.split(":")[-1]
    if value not in EXPANSION_LABELS:
        return
    d = (await state.get_data()).get("d", _new_draft())
    d["exp"] = value
    await state.update_data(d=d)
    await state.set_state(RecipeManager.c_lvl)
    await callback.message.answer(
        "🔓 Уровень расширения (нужен рецепту для крафта):",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text=f"Ур. {n}", callback_data=f"recadm:lvl:{n}")
                              for n in range(1, 6)]]
            + [[InlineKeyboardButton(text="❌ Отмена", callback_data="recadm:cancel")]]),
    )


@router.callback_query(F.data.startswith("recadm:lvl:"))
async def recadm_lvl(callback: CallbackQuery, state: FSMContext):
    if not await _ok(callback):
        return
    n = callback.data.split(":")[-1]
    if not n.isdigit() or not (1 <= int(n) <= 5):
        return
    d = (await state.get_data()).get("d", _new_draft())
    d["lvl"] = int(n)
    await state.update_data(d=d)
    await state.set_state(RecipeManager.c_ap)
    await callback.message.answer("⚡ ОД на один крафт (число):", reply_markup=cancel_keyboard())


@router.message(RecipeManager.c_ap)
async def recadm_c_ap(message: Message, state: FSMContext):
    v = _int(message.text, lo=0)
    if v is None:
        await message.answer("❌ Введи целое число от 0.")
        return
    d = (await state.get_data()).get("d", _new_draft())
    d["ap"] = v
    await state.update_data(d=d)
    await state.set_state(RecipeManager.c_time)
    await message.answer("⏱ Время крафта в СЕКУНДАХ (число):", reply_markup=cancel_keyboard())


@router.message(RecipeManager.c_time)
async def recadm_c_time(message: Message, state: FSMContext):
    v = _int(message.text, lo=1)
    if v is None:
        await message.answer("❌ Введи целое число >= 1.")
        return
    d = (await state.get_data()).get("d", _new_draft())
    d["time"] = v
    await state.update_data(d=d)
    await state.set_state(RecipeManager.c_rarity)
    await message.answer(
        "💎 Редкость РЕЦЕПТА:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=_rarity_buttons("rar")
                                          + [[InlineKeyboardButton(text="❌ Отмена",
                                                                   callback_data="recadm:cancel")]]),
    )


@router.callback_query(F.data.startswith("recadm:rar:"))
async def recadm_rar(callback: CallbackQuery, state: FSMContext):
    if not await _ok(callback):
        return
    n = callback.data.split(":")[-1]
    if not n.isdigit():
        return
    d = (await state.get_data()).get("d", _new_draft())
    d["rarity"] = int(n)
    await state.update_data(d=d)
    await state.set_state(RecipeManager.c_qty)
    await callback.message.answer(
        "🔢 Сколько предметов-результатов за один крафт (число):",
        reply_markup=cancel_keyboard(),
    )


@router.message(RecipeManager.c_qty)
async def recadm_c_qty(message: Message, state: FSMContext):
    v = _int(message.text, lo=1)
    if v is None:
        await message.answer("❌ Введи целое число >= 1.")
        return
    d = (await state.get_data()).get("d", _new_draft())
    d["qty"] = v
    await state.update_data(d=d)
    await state.set_state(RecipeManager.c_shop)
    await message.answer(
        "🏷 Цена товара-рецепта «Рецепт: <название>» в лавке НМ\n"
        "(0 — не продавать, рецепт доступен только через прокачку/лут):",
        reply_markup=cancel_keyboard(),
    )


@router.message(RecipeManager.c_shop)
async def recadm_c_shop(message: Message, state: FSMContext):
    v = _int(message.text, lo=0)
    if v is None:
        await message.answer("❌ Введи целое число от 0.")
        return
    d = (await state.get_data()).get("d", _new_draft())
    d["shop"] = v
    await state.update_data(d=d)
    await state.set_state(RecipeManager.c_confirm)
    exp = EXPANSION_LABELS.get(d["exp"], d["exp"])
    ing = ", ".join(f"{x[0]} × {x[1]}" for x in d["ingredients"])
    result = d["result_item_name"] or "—"
    shop_label = "не продаётся" if not d["shop"] else str(d["shop"]) + " НМ"
    text = (
        f"📜 Предпросмотр:\n\n"
        f"🏷 Название: {d['name'] or '—'}\n"
        f"🏠 Расширение: {exp} · уровень {d['lvl']}\n"
        f"🧪 Ингредиенты: {ing}\n"
        f"📦 Результат: {result} × {d['qty']}\n"
        f"⚡ {d['ap']} ОД · ⏱ {d['time']} сек\n"
        f"💎 {RARITY_EMOJI.get(d['rarity'], '?')} {RARITY_LEVELS.get(d['rarity'], '?')}\n"
        f"🏷 Товар-рецепт в лавке: {shop_label}"
    )
    await message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Сохранить", callback_data="recadm:save")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="recadm:cancel")],
    ]))


@router.callback_query(F.data == "recadm:save")
async def recadm_save(callback: CallbackQuery, state: FSMContext):
    if not await _ok(callback):
        return
    uid = callback.from_user.id
    d = (await state.get_data()).get("d", {})
    if not d.get("name") or not d.get("exp"):
        await callback.message.answer("❌ Данные рецепта неполные.")
        return
    dup = await find_recipe(d["name"], d["exp"], d["lvl"])
    if dup:
        await callback.message.answer(
            f"❌ Рецепт «{d['name']}» ({EXPANSION_LABELS.get(d['exp'], d['exp'])} {d['lvl']}) "
            f"уже есть — id {dup['id']}. Рецепты с одинаковым названием, "
            "расширением и уровнем не дублируются.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🗂 Открыть существующий",
                                      callback_data=f"recadm:open:{dup['id']}")],
            ]),
        )
        return
    if d.get("result_mode") == "new" and d.get("newitem"):
        ni = d["newitem"]
        await add_item(
            ni["name"], ni.get("desc") or "", ni.get("price") or 0,
            (ni.get("price") or 0) // 2, ni.get("rarity", 1), ni["cat"], -1,
            uid, ni.get("photo"), ap_cost=ni.get("ap") or 0,
            heal=ni.get("heal") or 0, regen=ni.get("regen") or 0,
            armor=ni.get("armor") or 0, damage=ni.get("dmg") or 0,
            drink_effect=ni.get("drink") or None)
        d["result_item_name"] = ni["name"]
    rid = await upsert_recipe(
        d["name"], d.get("description") or "", d["result_item_name"],
        d["qty"], d["exp"], d["lvl"], d["ingredients"], d["ap"], d["time"],
        d["rarity"])
    if d["shop"] > 0:
        recipe = await get_recipe(rid)
        await ensure_recipe_shop_item(recipe, price=d["shop"])
    await log_action(uid, "recipe_add", rid,
                     f"name={d['name']} exp={d['exp']} lvl={d['lvl']}")
    await state.clear()
    await callback.message.answer(
        f"✅ Рецепт «{d['name']}» сохранён (id {rid}).",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🗂 Открыть карточку",
                                  callback_data=f"recadm:open:{rid}")],
            [InlineKeyboardButton(text="📜 К списку", callback_data="recadm:list")],
        ]),
    )


# ---------- отмена мастеров ----------

@router.callback_query(F.data == "recadm:cancel")
async def recadm_cancel(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    text = "Действие отменено."
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📜 Менеджер рецептов", callback_data="recadm:menu")],
    ])
    await callback.message.answer(text, reply_markup=markup)


# ---------- правка полей ----------

@router.callback_query(F.data.startswith("recadm:ef:"))
async def recadm_ef(callback: CallbackQuery, state: FSMContext):
    if not await _ok(callback):
        return
    parts = callback.data.split(":")
    if len(parts) != 4:
        return
    field, rid_s = parts[2], parts[3]
    if not rid_s.isdigit():
        return
    rid = int(rid_s)
    prompts = {
        "name": "✏️ Новое НАЗВАНИЕ рецепта:",
        "desc": "📝 Новое ОПИСАНИЕ (или «-» чтобы очистить):",
        "ap": "⚡ Новые ОД на крафт (число):",
        "time": "⏱ Новое время крафта в СЕКУНДАХ (число):",
        "lvl": "🔓 Новый уровень расширения (1-5):",
        "qty": "🔢 Новое кол-во результата за крафт (число):",
        "shop": "🏷 Новая цена «Рецепт: X» в лавке, НМ (0 — не продавать):",
    }
    prompt = prompts.get(field)
    if not prompt:
        return
    await state.set_state(RecipeManager.e_value)
    await state.update_data(d={"rid": rid, "field": field})
    await callback.message.answer(prompt, reply_markup=cancel_keyboard())


@router.message(RecipeManager.e_value)
async def recadm_e_value(message: Message, state: FSMContext):
    d = (await state.get_data()).get("d", {})
    rid = d.get("rid")
    field = d.get("field")
    if not rid or not field:
        await state.clear()
        return
    recipe = dict(await get_recipe(rid))
    if not recipe:
        await message.answer("❌ Рецепт не найден.")
        await state.clear()
        return
    value = (message.text or "").strip()
    if field == "name":
        if not value:
            await message.answer("❌ Название не может быть пустым.")
            return
        dup = await find_recipe(value, recipe["required_expansion"], recipe["required_level"])
        if dup and dup["id"] != rid:
            await message.answer(
                f"❌ Рецепт «{value}» с таким расширением/уровнем уже есть (id {dup['id']}).",
            )
            return
        recipe["name"] = value
    elif field == "desc":
        recipe["description"] = None if value == "-" else value
    elif field == "ap":
        v = _int(value, lo=0)
        if v is None:
            await message.answer("❌ Введи целое число от 0.")
            return
        recipe["ap_cost"] = v
    elif field == "time":
        v = _int(value, lo=1)
        if v is None:
            await message.answer("❌ Введи целое число >= 1.")
            return
        recipe["production_time"] = v
    elif field == "lvl":
        v = _int(value, lo=1, hi=5)
        if v is None:
            await message.answer("❌ Уровень от 1 до 5.")
            return
        dup = await find_recipe(recipe["name"], recipe["required_expansion"], v)
        if dup and dup["id"] != rid:
            await message.answer(
                f"❌ Рецепт «{recipe['name']}» с уровнем {v} уже есть (id {dup['id']}).",
            )
            return
        recipe["required_level"] = v
    elif field == "qty":
        v = _int(value, lo=1)
        if v is None:
            await message.answer("❌ Введи целое число >= 1.")
            return
        recipe["result_quantity"] = v
    elif field == "shop":
        v = _int(value, lo=0)
        if v is None:
            await message.answer("❌ Введи целое число от 0.")
            return
    else:
        await state.clear()
        return

    old_name = (await get_recipe(rid))["name"]
    await upsert_recipe(
        recipe["name"], recipe["description"], recipe["result_item_name"],
        recipe["result_quantity"], recipe["required_expansion"],
        recipe["required_level"], json.loads(recipe["ingredients"]),
        recipe["ap_cost"], recipe["production_time"], recipe["rarity"], recipe_id=rid)
    if field == "name" and old_name != recipe["name"]:
        from database.db import get_db
        conn = await get_db()
        await conn.execute(
            "UPDATE items SET is_available = 0 WHERE name = ? AND category = 'recipes'",
            (f"Рецепт: {old_name}",))
        await conn.commit()
    if field == "shop":
        if value and int(value) > 0:
            await ensure_recipe_shop_item(recipe, price=int(value))
        else:
            from database.db import get_db
            conn = await get_db()
            await conn.execute(
                "UPDATE items SET is_available = 0 WHERE name = ? AND category = 'recipes'",
                (f"Рецепт: {recipe['name']}",))
            await conn.commit()
    await log_action(message.from_user.id, "recipe_edit", rid, f"field={field}")
    await state.clear()
    await _show_recipe_card(message, rid)


@router.callback_query(F.data.startswith("recadm:es:"))
async def recadm_es(callback: CallbackQuery, state: FSMContext):
    if not await _ok(callback):
        return
    rid_s = callback.data.split(":")[-1]
    if not rid_s.isdigit():
        return
    await callback.message.answer(
        "🏠 Новое расширение:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=v, callback_data=f"recadm:exv:{k}:{rid_s}")]
            for k, v in EXPANSION_LABELS.items()
        ] + [[InlineKeyboardButton(text="❌ Отмена", callback_data="recadm:cancel")]]),
    )


@router.callback_query(F.data.startswith("recadm:exv:"))
async def recadm_exv(callback: CallbackQuery, state: FSMContext):
    if not await _ok(callback):
        return
    parts = callback.data.split(":")
    if len(parts) != 4:
        return
    exp, rid_s = parts[2], parts[3]
    if exp not in EXPANSION_LABELS or not rid_s.isdigit():
        return
    rid = int(rid_s)
    recipe = dict(await get_recipe(rid))
    if not recipe:
        await callback.message.answer("❌ Рецепт не найден.")
        return
    dup = await find_recipe(recipe["name"], exp, recipe["required_level"])
    if dup and dup["id"] != rid:
        await callback.message.answer(
            f"❌ Рецепт «{recipe['name']}» на этом расширении/уровне уже есть (id {dup['id']}).",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🗂 Открыть", callback_data=f"recadm:open:{dup['id']}")],
            ]),
        )
        return
    recipe["required_expansion"] = exp
    await upsert_recipe(
        recipe["name"], recipe["description"], recipe["result_item_name"],
        recipe["result_quantity"], recipe["required_expansion"],
        recipe["required_level"], json.loads(recipe["ingredients"]),
        recipe["ap_cost"], recipe["production_time"], recipe["rarity"], recipe_id=rid)
    await state.clear()
    await _show_recipe_card(callback.message, rid)


@router.callback_query(F.data.startswith("recadm:eq:"))
async def recadm_eq(callback: CallbackQuery, state: FSMContext):
    if not await _ok(callback):
        return
    rid_s = callback.data.split(":")[-1]
    if not rid_s.isdigit():
        return
    await callback.message.answer(
        "💎 Новая редкость рецепта:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=_rarity_buttons("rxv", f":{rid_s}")
                                          + [[InlineKeyboardButton(text="❌ Отмена",
                                                                   callback_data="recadm:cancel")]]),
    )


@router.callback_query(F.data.startswith("recadm:rxv:"))
async def recadm_rxv(callback: CallbackQuery, state: FSMContext):
    if not await _ok(callback):
        return
    parts = callback.data.split(":")
    if len(parts) != 4:
        return
    n, rid_s = parts[2], parts[3]
    if not n.isdigit() or not rid_s.isdigit():
        return
    rid = int(rid_s)
    recipe = dict(await get_recipe(rid))
    if not recipe:
        await callback.message.answer("❌ Рецепт не найден.")
        return
    recipe["rarity"] = int(n)
    await upsert_recipe(
        recipe["name"], recipe["description"], recipe["result_item_name"],
        recipe["result_quantity"], recipe["required_expansion"],
        recipe["required_level"], json.loads(recipe["ingredients"]),
        recipe["ap_cost"], recipe["production_time"], recipe["rarity"], recipe_id=rid)
    await state.clear()
    await _show_recipe_card(callback.message, rid)


# ---------- правка: структура ----------

@router.callback_query(F.data.startswith("recadm:ei:"))
async def recadm_ei(callback: CallbackQuery, state: FSMContext):
    if not await _ok(callback):
        return
    rid_s = callback.data.split(":")[-1]
    if not rid_s.isdigit():
        return
    recipe = await get_recipe(int(rid_s))
    if not recipe:
        await callback.message.answer("❌ Рецепт не найден.")
        return
    d = _new_draft()
    d["ctx"] = "edit"
    d["rid"] = int(rid_s)
    try:
        d["ingredients"] = json.loads(recipe["ingredients"] or "[]")
    except (TypeError, ValueError):
        d["ingredients"] = []
    await state.set_state(RecipeManager.ing)
    await state.update_data(d=d)
    cur = ", ".join(f"{x[0]}×{x[1]}" for x in d["ingredients"]) or "—"
    await callback.message.answer(
        f"🧪 Текущие ингредиенты: {cur}\n\n"
        "Вводи новый список по одному <b>Название:количество</b>. "
        "Когда готово — «✅ Готово».",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Готово", callback_data="recadm:ing_done")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="recadm:cancel")],
        ]),
    )


@router.callback_query(F.data.startswith("recadm:er:"))
async def recadm_er(callback: CallbackQuery, state: FSMContext):
    if not await _ok(callback):
        return
    rid_s = callback.data.split(":")[-1]
    if not rid_s.isdigit():
        return
    recipe = await get_recipe(int(rid_s))
    if not recipe:
        await callback.message.answer("❌ Рецепт не найден.")
        return
    d = _new_draft()
    d["ctx"] = "edit"
    d["rid"] = int(rid_s)
    d["result_item_name"] = recipe["result_item_name"]
    await state.set_state(RecipeManager.res_mode)
    await state.update_data(d=d)
    await callback.message.answer(
        "📦 Новый результат крафта:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🎯 Взять существующий",
                                  callback_data="recadm:res_existing")],
            [InlineKeyboardButton(text="➕ Создать новый",
                                  callback_data="recadm:res_new")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="recadm:cancel")],
        ]),
    )


@router.callback_query(F.data.startswith("recadm:et:"))
async def recadm_et(callback: CallbackQuery, state: FSMContext):
    if not await _ok(callback):
        return
    rid_s = callback.data.split(":")[-1]
    if not rid_s.isdigit():
        return
    rid = int(rid_s)
    recipe = await get_recipe(rid)
    if not recipe:
        await callback.message.answer("❌ Рецепт не найден.")
        return
    await set_recipe_visible(rid, not recipe["is_available"])
    await log_action(callback.from_user.id, "recipe_toggle", rid,
                     f"visible={not recipe['is_available']}")
    await state.clear()
    await _show_recipe_card(callback.message, rid)


@router.callback_query(F.data.startswith("recadm:ed:"))
async def recadm_ed(callback: CallbackQuery, state: FSMContext):
    if not await _ok(callback):
        return
    rid_s = callback.data.split(":")[-1]
    if not rid_s.isdigit():
        return
    rid = int(rid_s)
    recipe = await get_recipe(rid)
    if not recipe:
        await callback.message.answer("❌ Рецепт не найден.")
        return
    await callback.message.answer(
        f"🗑 Удалить рецепт «{recipe['name']}»?\n\n"
        "⚠️ Рецепт и его товар «Рецепт: …» будут скрыты. Пилоты, уже выучившие "
        "рецепт, потеряют доступ к крафту.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Да, удалить", callback_data=f"recadm:ed_yes:{rid}")],
            [InlineKeyboardButton(text="❌ Нет", callback_data="recadm:noop")],
        ]),
    )


@router.callback_query(F.data.startswith("recadm:ed_yes:"))
async def recadm_ed_yes(callback: CallbackQuery, state: FSMContext):
    if not await _ok(callback):
        return
    rid_s = callback.data.split(":")[-1]
    if not rid_s.isdigit():
        return
    rid = int(rid_s)
    recipe = await get_recipe(rid)
    if recipe and delete_recipe(rid):
        await log_action(callback.from_user.id, "recipe_delete", rid,
                         f"name={recipe['name']}")
    await state.clear()
    await callback.message.answer(
        f"🗑 Рецепт «{recipe['name'] if recipe else '?'}» скрыт.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📜 К списку", callback_data="recadm:list")],
        ]),
    )