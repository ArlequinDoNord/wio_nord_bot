"""
Менеджер рецептов крафта (v0.22.13): создание, правка и удаление рецептов.

Рецепты живут в таблице recipes наравне с сидированными (RECIPES_DEF), но
ensure_recipes() их не перезатирает — она работает только по RECIPES_DEF
(по имени+расширению+уровню), поэтому менеджерные строки не трогаются.

Возможности:
- создание свитка (одного рецепта): тип → название → описание → состав
  (ингредиенты выбираются из каталога предметов по категориям, затем
  спрашивается количество) → результат → расширение/уровень → ОД → время →
  редкость → кол-во → цена товара-рецепта «Рецепт: <название>» в лавке;
- создание книги рецептов: тип → название → описание → выбор готовых рецептов
  (минимум один) → цена; книга — предмет категории `recipes`, при использовании
  открывает все свои рецепты (`recipe_book_items`, `learn_recipe_from_item`);
- правка рецепта: все поля карточки по одному + быстрые кнопки расширения/редкости,
  показать/скрыть, перевыбор результата и состава;
- книги: список, карточка, показать/скрыть, мягкое удаление;
- удаление рецепта: скрытие рецепта и его товара (строки не трогаем — на id
  ссылаются выученные user_recipes).

Вход — из админ-панели (кнопка «📜 Менеджер рецептов», can_manage_shop).
Всё пространство callbacks живёт под префиксом recadm: — оно не пересекается
с админкой (admin.py) и снимает риск перехвата в smoke_127.
"""

import json

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.db import (
    get_item, get_item_by_name, get_items_by_category, count_items_by_category,
    get_recipe, list_recipes_for_admin,
    upsert_recipe, ensure_recipe_shop_item, delete_recipe,
    find_recipe, set_recipe_visible, add_item,
    set_recipe_book, get_recipe_book_recipes, list_recipe_books,
    set_recipe_book_visible, delete_recipe_book,
    BOOK_ITEM_PREFIX,
)
from utils.permissions import has_permission, log_action
from utils.helpers import edit_message_safe
from keyboards.keyboards import cancel_keyboard
from config import RARITY_LEVELS, RARITY_EMOJI, ITEM_CATEGORIES

router = Router()

RECIPES_PER_PAGE = 8
PICK_PER_PAGE = 8

# Служебные категории не предлагаем в пикере состава/результата: рецепты,
# рыночные лоты, дуэльные карты и лицензии в крафт не кладут.
PICK_EXCLUDE_CATEGORIES = {"recipes", "market", "duel_card", "license"}

KIND_LABELS = {
    "scroll": "📜 Свиток",
    "book": "📖 Книга рецептов",
}

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
    # создание: тип -> название -> описание -> состав / выбор рецептов книги
    c_kind = State()        # свиток или книга рецептов
    c_name = State()        # название рецепта/книги
    c_desc = State()        # описание
    c_ing_cat = State()     # состав: выбор категории и предметов
    c_ing_qty = State()     # состав: количество выбранного ингредиента
    c_book = State()        # книга: выбор готовых рецептов
    c_book_price = State()  # книга: цена в лавке
    res_mode = State()      # результат: существующий / новый
    c_res_cat = State()     # результат: выбор предмета из каталога
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
        "kind": "scroll",
        "rid": None,
        "name": "",
        "description": "",
        "ingredients": [],
        "pending_ing": None,
        "book_recipes": [],
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


def _composition_str(d: dict) -> str:
    ings = d.get("ingredients") or []
    if not ings:
        return "пока пусто"
    return ", ".join(f"{x[0]} × {x[1]}" for x in ings)


def _pick_category_rows(prefix: str, counts: dict) -> list:
    """Кнопки категорий каталога (без служебных) для пикера предметов."""
    rows = []
    for key, label in sorted(ITEM_CATEGORIES.items(), key=lambda x: x[1]):
        if key in PICK_EXCLUDE_CATEGORIES:
            continue
        c = counts.get(key, 0)
        if not c:
            continue
        rows.append([InlineKeyboardButton(
            text=f"{label} ({c})", callback_data=f"recadm:{prefix}:{key}:0")])
    rows.append([InlineKeyboardButton(
        text="📦 Все предметы", callback_data=f"recadm:{prefix}:all:0")])
    return rows


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


async def _show_composition(target, state: FSMContext, edit: bool = True):
    """Экран состава: категории каталога + текущий список ингредиентов."""
    d = (await state.get_data()).get("d", _new_draft())
    counts = await count_items_by_category()
    rows = _pick_category_rows("ingcat", counts)
    if d.get("ingredients"):
        rows.append([InlineKeyboardButton(text="✅ Состав готов",
                                          callback_data="recadm:ing_done")])
    rows.append([InlineKeyboardButton(text="❌ Отмена", callback_data="recadm:cancel")])
    text = (
        "🧪 СОСТАВ РЕЦЕПТА\n\n"
        f"Сейчас: {_composition_str(d)}\n\n"
        "Выбери категорию — покажу предметы игры. После выбора спрошу количество."
    )
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    if edit:
        await edit_message_safe(target, text, kb)
    else:
        await target.answer(text, reply_markup=kb)


async def _show_pick_items(target, state: FSMContext, kind: str, cat: str,
                           page: int, edit: bool = True):
    """Список предметов каталога с пагинацией.

    kind='ing' — выбор ингредиента, kind='res' — выбор результата крафта.
    """
    d = (await state.get_data()).get("d", _new_draft())
    items = await get_items_by_category(cat)
    # «Все предметы» и любой прямой callback не должны тянуть служебные
    # категории (рецепты, рынок, дуэльные карты, лицензии) в состав/результат.
    items = [it for it in items if it.get("category") not in PICK_EXCLUDE_CATEGORIES]
    pages = max(1, (len(items) + PICK_PER_PAGE - 1) // PICK_PER_PAGE)
    page = max(0, min(page, pages - 1))
    chunk = items[page * PICK_PER_PAGE: page * PICK_PER_PAGE + PICK_PER_PAGE]

    selected = {x[0] for x in (d.get("ingredients") or [])} if kind == "ing" else set()
    rows = []
    for it in chunk:
        mark = "✅ " if it["name"] in selected else ""
        rows.append([InlineKeyboardButton(
            text=f"{mark}{it['name']}",
            callback_data=f"recadm:{kind}pick:{it['id']}")])
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(
            text="⬅️", callback_data=f"recadm:{kind}cat:{cat}:{page - 1}"))
    nav.append(InlineKeyboardButton(text=f"{page + 1}/{pages}",
                                    callback_data="recadm:noop"))
    if page < pages - 1:
        nav.append(InlineKeyboardButton(
            text="➡️", callback_data=f"recadm:{kind}cat:{cat}:{page + 1}"))
    if nav:
        rows.append(nav)
    rows.append([InlineKeyboardButton(
        text="🔙 Категории", callback_data=f"recadm:{kind}cats")])
    if kind == "ing" and d.get("ingredients"):
        rows.append([InlineKeyboardButton(text="✅ Состав готов",
                                          callback_data="recadm:ing_done")])
    rows.append([InlineKeyboardButton(text="❌ Отмена", callback_data="recadm:cancel")])

    cat_name = ITEM_CATEGORIES.get(cat, cat) if cat != "all" else "Все предметы"
    if kind == "ing":
        text = (f"🧪 {cat_name} — страница {page + 1}/{pages}\n\n"
                f"Сейчас: {_composition_str(d)}")
    else:
        text = f"📦 {cat_name} — страница {page + 1}/{pages}\n\nВыбери предмет-результат."
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    if edit:
        await edit_message_safe(target, text, kb)
    else:
        await target.answer(text, reply_markup=kb)


async def _show_result_categories(target, edit: bool = True):
    counts = await count_items_by_category()
    rows = _pick_category_rows("rescat", counts)
    rows.append([InlineKeyboardButton(text="❌ Отмена", callback_data="recadm:cancel")])
    text = ("📦 РЕЗУЛЬТАТ КРАФТА\n\n"
            "Выбери категорию — покажу предметы. Результатом может быть любой предмет игры.")
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    if edit:
        await edit_message_safe(target, text, kb)
    else:
        await target.answer(text, reply_markup=kb)


async def _show_book_picker(target, state: FSMContext, page: int = 0, edit: bool = True):
    """Выбор готовых рецептов для книги (отметить/снять, пагинация)."""
    d = (await state.get_data()).get("d", _new_draft())
    recipes = [r for r in await list_recipes_for_admin() if r["is_available"]]
    pages = max(1, (len(recipes) + RECIPES_PER_PAGE - 1) // RECIPES_PER_PAGE)
    page = max(0, min(page, pages - 1))
    chunk = recipes[page * RECIPES_PER_PAGE: page * RECIPES_PER_PAGE + RECIPES_PER_PAGE]
    selected = list(d.get("book_recipes") or [])
    rows = []
    for r in chunk:
        mark = "✅" if r["id"] in selected else "▫️"
        exp = EXPANSION_LABELS.get(r["required_expansion"] or '', r["required_expansion"] or '?')
        rows.append([InlineKeyboardButton(
            text=f"{mark} {r['name']} · {exp} {r['required_level']}",
            callback_data=f"recadm:bookpick:{page}:{r['id']}")])
    nav = [InlineKeyboardButton(text="⬅️", callback_data=f"recadm:bookpage:{page - 1}"),
           InlineKeyboardButton(text=f"{page + 1}/{pages}", callback_data="recadm:noop"),
           InlineKeyboardButton(text="➡️", callback_data=f"recadm:bookpage:{page + 1}")]
    rows.append(nav)
    rows.append([InlineKeyboardButton(
        text=f"✅ Готово (выбрано {len(selected)})", callback_data="recadm:book_done")])
    rows.append([InlineKeyboardButton(text="❌ Отмена", callback_data="recadm:cancel")])
    text = (
        f"📖 КНИГА «{d.get('name') or '—'}»\n\n"
        f"Отмечено рецептов: {len(selected)}.\n"
        "Нажми на рецепт, чтобы отметить или снять. Нужен минимум один."
    )
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    if edit:
        await edit_message_safe(target, text, kb)
    else:
        await target.answer(text, reply_markup=kb)


def _book_description(raw: str, recipes) -> str:
    lines = ["📖 Книга рецептов."]
    if raw:
        lines.append(raw)
    lines.append("")
    lines.append("Открывает рецепты:")
    for r in recipes:
        lines.append(f"• {r['name']}")
    lines.append("")
    lines.append("Используй из инвентаря, чтобы выучить все рецепты сразу.")
    return "\n".join(lines)


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
        InlineKeyboardButton(text="➕ Создать", callback_data="recadm:create"),
        InlineKeyboardButton(text="📖 Книги", callback_data="recadm:books"),
        InlineKeyboardButton(text="🔙 В менеджер", callback_data="recadm:menu"),
    ])
    text = f"📜 Рецепты крафта — всего {total}:\n\n"
    text += f"Страница {page + 1} из {pages}. ⛔ — скрытые."
    await edit_message_safe(callback.message, text,
                            InlineKeyboardMarkup(inline_keyboard=rows))


async def _show_books(callback: CallbackQuery, page: int):
    """Список книг рецептов (предметы с привязкой к рецептам)."""
    books = await list_recipe_books()
    total = len(books)
    pages = max(1, (total + RECIPES_PER_PAGE - 1) // RECIPES_PER_PAGE)
    page = max(0, min(page, pages - 1))
    rows = []
    for b in books[page * RECIPES_PER_PAGE: page * RECIPES_PER_PAGE + RECIPES_PER_PAGE]:
        short = b["name"]
        if short.startswith(BOOK_ITEM_PREFIX):
            short = short[len(BOOK_ITEM_PREFIX):]
        mark = "⛔ " if not b["is_available"] else "📖 "
        rows.append([InlineKeyboardButton(
            text=f"{mark}{short} · рецептов: {b['recipes_count']}",
            callback_data=f"recadm:bookopen:{b['id']}")])
    nav = [InlineKeyboardButton(text="⬅️", callback_data=f"recadm:bookspage:{page - 1}"),
           InlineKeyboardButton(text=f"{page + 1}/{pages}", callback_data="recadm:noop"),
           InlineKeyboardButton(text="➡️", callback_data=f"recadm:bookspage:{page + 1}")]
    rows.append(nav)
    rows.append([InlineKeyboardButton(text="📜 Рецепты", callback_data="recadm:list"),
                 InlineKeyboardButton(text="🔙 В менеджер", callback_data="recadm:menu")])
    text = (f"📖 КНИГИ РЕЦЕПТОВ — всего {total}:\n\n"
            "Нажми на книгу, чтобы открыть карточку. ⛔ — скрытые.")
    await edit_message_safe(callback.message, text,
                            InlineKeyboardMarkup(inline_keyboard=rows))


async def _show_book_card(msg, item_id: int):
    item = await get_item(item_id)
    recipes = await get_recipe_book_recipes(item_id)
    if not item or not recipes:
        await msg.answer("❌ Книга не найдена.")
        return
    status = "✅ в продаже" if item["is_available"] else "⛔ скрыта"
    listing = "\n".join(
        f"• {r['name']} — "
        f"{EXPANSION_LABELS.get(r['required_expansion'] or '', r['required_expansion'] or '?')}"
        f" {r['required_level']}"
        for r in recipes)
    text = (
        f"📖 Книга #{item['id']} — {item['name']}\n\n"
        f"{status} · 🏷 {item['price']} НМ\n"
        f"Открывает рецептов: {len(recipes)}\n{listing}"
    )
    if item.get("description"):
        text += f"\n\n📝 {item['description']}"
    await edit_message_safe(msg, text, InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="👁 Скрыть" if item["is_available"] else "👁 Показать",
            callback_data=f"recadm:booktoggle:{item_id}"),
         InlineKeyboardButton(text="🗑 Удалить",
                              callback_data=f"recadm:bookdel:{item_id}")],
        [InlineKeyboardButton(text="🔙 К книгам", callback_data="recadm:books")],
    ]))


async def _resolve_result(state: FSMContext, message):
    """Результат выбран (существующий предмет). Зависит от контекста: создание
    идёт дальше по визарду, правка — сразу сохраняет результат в карточке."""
    d = (await state.get_data()).get("d", {})
    if d.get("ctx") == "edit":
        rid = d["rid"]
        recipe = dict(await get_recipe(rid))
        if not recipe:
            await message.answer("❌ Рецепт не найден.")
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
        await _show_recipe_card(message, rid)
    else:
        await state.set_state(RecipeManager.c_exp)
        await message.answer(
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
        await _show_recipe_card(message, rid)
        return
    await state.set_state(RecipeManager.c_exp)
    await message.answer(
        "🏠 На каком расширении крафтится?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=v, callback_data=f"recadm:exp:{k}")]
            for k, v in EXPANSION_LABELS.items()
        ] + [[InlineKeyboardButton(text="❌ Отмена", callback_data="recadm:cancel")]])
    )


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
        "удалить рецепт. Удаление скрывает рецепт и его товар из лавки.\n\n"
        "📖 Книги рецептов — предметы, которые открывают набор готовых рецептов."
    )
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📜 Список рецептов", callback_data="recadm:list")],
        [InlineKeyboardButton(text="📖 Книги рецептов", callback_data="recadm:books")],
        [InlineKeyboardButton(text="➕ Создать", callback_data="recadm:create")],
        [InlineKeyboardButton(text="🔙 В админ-панель", callback_data="admin:menu")],
    ])
    await edit_message_safe(callback.message, text, markup)


@router.callback_query(F.data == "recadm:list")
async def recadm_list(callback: CallbackQuery, state: FSMContext):
    if not await _ok(callback):
        return
    await state.clear()
    await _show_list(callback, 0)


@router.callback_query(F.data == "recadm:books")
async def recadm_books(callback: CallbackQuery, state: FSMContext):
    if not await _ok(callback):
        return
    await state.clear()
    await _show_books(callback, 0)


@router.callback_query(F.data.startswith("recadm:bookspage:"))
async def recadm_books_page(callback: CallbackQuery, state: FSMContext):
    if not await _ok(callback):
        return
    try:
        page = int(callback.data.split(":")[-1])
    except ValueError:
        page = 0
    await _show_books(callback, page)


@router.callback_query(F.data.startswith("recadm:bookopen:"))
async def recadm_book_open(callback: CallbackQuery, state: FSMContext):
    if not await _ok(callback):
        return
    item_id_s = callback.data.split(":")[-1]
    if not item_id_s.isdigit():
        return
    await state.clear()
    await _show_book_card(callback.message, int(item_id_s))


@router.callback_query(F.data.startswith("recadm:booktoggle:"))
async def recadm_book_toggle(callback: CallbackQuery, state: FSMContext):
    if not await _ok(callback):
        return
    item_id_s = callback.data.split(":")[-1]
    if not item_id_s.isdigit():
        return
    item_id = int(item_id_s)
    item = await get_item(item_id)
    if not item:
        await callback.message.answer("❌ Книга не найдена.")
        return
    await set_recipe_book_visible(item_id, not item["is_available"])
    await log_action(callback.from_user.id, "recipe_book_toggle", item_id,
                     f"visible={not item['is_available']}")
    await _show_book_card(callback.message, item_id)


@router.callback_query(F.data.startswith("recadm:bookdel:"))
async def recadm_book_del(callback: CallbackQuery, state: FSMContext):
    if not await _ok(callback):
        return
    item_id_s = callback.data.split(":")[-1]
    if not item_id_s.isdigit():
        return
    item_id = int(item_id_s)
    item = await get_item(item_id)
    if not item:
        await callback.message.answer("❌ Книга не найдена.")
        return
    await callback.message.answer(
        f"🗑 Скрыть книгу «{item['name']}» из лавки?\n\n"
        "⚠️ Книги в инвентарях игроков продолжат работать, связка с рецептами "
        "сохранится — книгу можно вернуть кнопкой «Показать».",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Да, скрыть",
                                  callback_data=f"recadm:bookdel_yes:{item_id}")],
            [InlineKeyboardButton(text="❌ Нет", callback_data="recadm:noop")],
        ]),
    )


@router.callback_query(F.data.startswith("recadm:bookdel_yes:"))
async def recadm_book_del_yes(callback: CallbackQuery, state: FSMContext):
    if not await _ok(callback):
        return
    item_id_s = callback.data.split(":")[-1]
    if not item_id_s.isdigit():
        return
    item_id = int(item_id_s)
    if await delete_recipe_book(item_id):
        await log_action(callback.from_user.id, "recipe_book_delete", item_id)
    await state.clear()
    await callback.message.answer(
        "🗑 Книга скрыта.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📖 К книгам", callback_data="recadm:books")],
        ]),
    )


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
    await state.set_state(RecipeManager.c_kind)
    await state.update_data(d=_new_draft())
    await callback.message.answer(
        "➕ Что создаём?\n\n"
        "📜 <b>Свиток</b> — один рецепт: название, описание, состав, результат.\n"
        "📖 <b>Книга рецептов</b> — предмет, открывающий набор уже готовых рецептов.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📜 Свиток — один рецепт",
                                  callback_data="recadm:kind:scroll")],
            [InlineKeyboardButton(text="📖 Книга рецептов — набор рецептов",
                                  callback_data="recadm:kind:book")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="recadm:cancel")],
        ]),
    )


# ---------- создание: тип -> название -> описание ----------

@router.callback_query(F.data.startswith("recadm:kind:"))
async def recadm_kind(callback: CallbackQuery, state: FSMContext):
    if not await _ok(callback):
        return
    kind = callback.data.split(":")[-1]
    if kind not in KIND_LABELS:
        return
    d = (await state.get_data()).get("d", _new_draft())
    d["kind"] = kind
    d["ingredients"] = []
    d["book_recipes"] = []
    await state.update_data(d=d)
    await state.set_state(RecipeManager.c_name)
    what = "рецепта" if kind == "scroll" else "книги"
    await callback.message.answer(
        f"{KIND_LABELS[kind]}. Шаг 1/3 — НАЗВАНИЕ {what}:",
        reply_markup=cancel_keyboard(),
    )


@router.message(RecipeManager.c_name)
async def recadm_c_name(message: Message, state: FSMContext):
    name = (message.text or "").strip()
    if not name:
        await message.answer("❌ Название не может быть пустым.")
        return
    if len(name) > 60:
        await message.answer("❌ Слишком длинное название (максимум 60 символов).")
        return
    d = (await state.get_data()).get("d", _new_draft())
    if d.get("kind") == "book":
        item_name = BOOK_ITEM_PREFIX + name
        if await get_item_by_name(item_name):
            await message.answer(
                f"❌ Книга «{item_name}» уже существует. Выбери другое название.")
            return
    d["name"] = name
    await state.update_data(d=d)
    await state.set_state(RecipeManager.c_desc)
    await message.answer(
        "📝 Описание (как увидит игрок; «-», если не нужно):",
        reply_markup=cancel_keyboard(),
    )


@router.message(RecipeManager.c_desc)
async def recadm_c_desc(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    d = (await state.get_data()).get("d", _new_draft())
    d["description"] = "" if text == "-" else text
    await state.update_data(d=d)
    if d.get("kind") == "book":
        await state.set_state(RecipeManager.c_book)
        await _show_book_picker(message, state, 0, edit=False)
        return
    await state.set_state(RecipeManager.c_ing_cat)
    await _show_composition(message, state, edit=False)


# ---------- создание: состав (каталог предметов) ----------

@router.callback_query(F.data.startswith("recadm:ingcat:"))
async def recadm_ing_cat(callback: CallbackQuery, state: FSMContext):
    if not await _ok(callback):
        return
    parts = callback.data.split(":")
    cat = parts[2] if len(parts) > 2 else "all"
    try:
        page = int(parts[3]) if len(parts) > 3 else 0
    except ValueError:
        page = 0
    await state.set_state(RecipeManager.c_ing_cat)
    await _show_pick_items(callback.message, state, "ing", cat, page)


@router.callback_query(F.data == "recadm:ingcats")
async def recadm_ing_cats(callback: CallbackQuery, state: FSMContext):
    if not await _ok(callback):
        return
    await state.set_state(RecipeManager.c_ing_cat)
    await _show_composition(callback.message, state)


@router.callback_query(F.data == "recadm:ing_more")
async def recadm_ing_more(callback: CallbackQuery, state: FSMContext):
    if not await _ok(callback):
        return
    await state.set_state(RecipeManager.c_ing_cat)
    await _show_composition(callback.message, state)


@router.callback_query(F.data.startswith("recadm:ingpick:"))
async def recadm_ing_pick(callback: CallbackQuery, state: FSMContext):
    if not await _ok(callback):
        return
    item_id_s = callback.data.split(":")[-1]
    if not item_id_s.isdigit():
        return
    item = await get_item(int(item_id_s))
    if not item:
        await callback.message.answer("❌ Предмет не найден.")
        return
    d = (await state.get_data()).get("d", _new_draft())
    d["pending_ing"] = {"id": item["id"], "name": item["name"]}
    await state.update_data(d=d)
    await state.set_state(RecipeManager.c_ing_qty)
    cur = next((x[1] for x in (d.get("ingredients") or []) if x[0] == item["name"]), 0)
    await callback.message.answer(
        f"🔢 Сколько «{item['name']}» нужно в рецепте?\n"
        f"Сейчас в составе: {cur}. Введи целое число (0 — убрать из состава).",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 К составу", callback_data="recadm:ingcats")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="recadm:cancel")],
        ]),
    )


@router.message(RecipeManager.c_ing_qty)
async def recadm_c_ing_qty(message: Message, state: FSMContext):
    v = _int(message.text, lo=0, hi=9999)
    if v is None:
        await message.answer("❌ Введи целое число от 0 до 9999.")
        return
    d = (await state.get_data()).get("d", _new_draft())
    pending = d.get("pending_ing") or {}
    name = pending.get("name")
    if not name:
        await message.answer("❌ Предмет не выбран. Вернись к составу.",
                             reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                 [InlineKeyboardButton(text="🧪 К составу",
                                                       callback_data="recadm:ingcats")],
                             ]))
        return
    ings = [list(x) for x in (d.get("ingredients") or [])]
    found = None
    for row in ings:
        if row[0] == name:
            found = row
            break
    if v == 0:
        if found:
            ings.remove(found)
        text = f"🗑 «{name}» убран из состава."
    elif found:
        found[1] = v
        text = f"✅ «{name}» × {v} — обновлён в составе."
    else:
        ings.append([name, v])
        text = f"✅ «{name}» × {v} — добавлен в состав."
    d["ingredients"] = ings
    d["pending_ing"] = None
    await state.update_data(d=d)
    await state.set_state(RecipeManager.c_ing_cat)
    await message.answer(
        f"{text}\nСейчас: {_composition_str(d)}\n\n"
        "Добавить ещё ингредиент или закончить состав?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ Добавить ещё ингредиент",
                                  callback_data="recadm:ing_more")],
            [InlineKeyboardButton(text="✅ Состав готов", callback_data="recadm:ing_done")],
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


# ---------- создание: результат из каталога ----------

@router.callback_query(F.data == "recadm:res_existing")
async def recadm_res_existing(callback: CallbackQuery, state: FSMContext):
    if not await _ok(callback):
        return
    await state.set_state(RecipeManager.c_res_cat)
    await _show_result_categories(callback.message)


@router.callback_query(F.data.startswith("recadm:rescat:"))
async def recadm_res_cat(callback: CallbackQuery, state: FSMContext):
    if not await _ok(callback):
        return
    parts = callback.data.split(":")
    cat = parts[2] if len(parts) > 2 else "all"
    try:
        page = int(parts[3]) if len(parts) > 3 else 0
    except ValueError:
        page = 0
    await state.set_state(RecipeManager.c_res_cat)
    await _show_pick_items(callback.message, state, "res", cat, page)


@router.callback_query(F.data == "recadm:rescats")
async def recadm_res_cats(callback: CallbackQuery, state: FSMContext):
    if not await _ok(callback):
        return
    await state.set_state(RecipeManager.c_res_cat)
    await _show_result_categories(callback.message)


@router.callback_query(F.data.startswith("recadm:respick:"))
async def recadm_res_pick(callback: CallbackQuery, state: FSMContext):
    if not await _ok(callback):
        return
    item_id_s = callback.data.split(":")[-1]
    if not item_id_s.isdigit():
        return
    item = await get_item(int(item_id_s))
    if not item:
        await callback.message.answer("❌ Предмет не найден.")
        return
    d = (await state.get_data()).get("d", _new_draft())
    d["result_item_name"] = item["name"]
    d["result_mode"] = "existing"
    await state.update_data(d=d)
    await _resolve_result(state, callback.message)


# ---------- создание: книга рецептов ----------

@router.callback_query(F.data.startswith("recadm:bookpage:"))
async def recadm_book_page(callback: CallbackQuery, state: FSMContext):
    if not await _ok(callback):
        return
    try:
        page = int(callback.data.split(":")[-1])
    except ValueError:
        page = 0
    await state.set_state(RecipeManager.c_book)
    await _show_book_picker(callback.message, state, page)


@router.callback_query(F.data.startswith("recadm:bookpick:"))
async def recadm_book_pick(callback: CallbackQuery, state: FSMContext):
    if not await _ok(callback):
        return
    parts = callback.data.split(":")
    if len(parts) != 4:
        return
    page = int(parts[2]) if parts[2].isdigit() else 0
    if not parts[3].isdigit():
        return
    rid = int(parts[3])
    d = (await state.get_data()).get("d", _new_draft())
    selected = list(d.get("book_recipes") or [])
    if rid in selected:
        selected.remove(rid)
    else:
        selected.append(rid)
    d["book_recipes"] = selected
    await state.update_data(d=d)
    await state.set_state(RecipeManager.c_book)
    await _show_book_picker(callback.message, state, page)


@router.callback_query(F.data == "recadm:book_done")
async def recadm_book_done(callback: CallbackQuery, state: FSMContext):
    if not await _ok(callback):
        return
    d = (await state.get_data()).get("d", _new_draft())
    if not d.get("book_recipes"):
        await callback.message.answer(
            "❌ Отметь хотя бы один рецепт для книги.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 К выбору рецептов",
                                      callback_data="recadm:bookpage:0")],
            ]),
        )
        return
    await state.set_state(RecipeManager.c_book_price)
    await callback.message.answer(
        f"🏷 Цена книги «{d.get('name') or '—'}» в лавке, НМ\n"
        "(0 — не продавать, книга будет только лут/выдача):",
        reply_markup=cancel_keyboard(),
    )


@router.message(RecipeManager.c_book_price)
async def recadm_c_book_price(message: Message, state: FSMContext):
    v = _int(message.text, lo=0, hi=1000000)
    if v is None:
        await message.answer("❌ Введи целое число от 0.")
        return
    d = (await state.get_data()).get("d", _new_draft())
    name = (d.get("name") or "").strip()
    if not name:
        await message.answer("❌ Название книги потеряно. Начни создание заново.")
        await state.clear()
        return
    item_name = BOOK_ITEM_PREFIX + name
    if await get_item_by_name(item_name):
        await message.answer(f"❌ Предмет «{item_name}» уже существует.")
        return
    recipes = []
    for rid in d.get("book_recipes") or []:
        recipe = await get_recipe(rid)
        if recipe and recipe["is_available"]:
            recipes.append(dict(recipe))
    if not recipes:
        await message.answer("❌ Ни один из выбранных рецептов больше не доступен.")
        return
    desc = _book_description(d.get("description") or "", recipes)
    rarity = max((r.get("rarity") or 1) for r in recipes)
    item_id = await add_item(
        item_name, desc, v, v // 2, rarity, "recipes", -1, message.from_user.id)
    await set_recipe_book(item_id, [r["id"] for r in recipes])
    if v <= 0:
        await set_recipe_book_visible(item_id, False)
    await log_action(message.from_user.id, "recipe_book_add", item_id,
                     f"name={name} recipes={len(recipes)}")
    await state.clear()
    listing = "\n".join(f"• {r['name']}" for r in recipes)
    await message.answer(
        f"✅ Книга «{name}» создана (id {item_id}).\n\n"
        f"📖 Открывает рецептов: {len(recipes)}\n{listing}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🗂 Открыть карточку",
                                  callback_data=f"recadm:bookopen:{item_id}")],
            [InlineKeyboardButton(text="📜 В менеджер", callback_data="recadm:menu")],
        ]),
    )


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
    d["kind"] = "scroll"
    d["rid"] = int(rid_s)
    d["name"] = recipe["name"]
    try:
        d["ingredients"] = [list(x) for x in json.loads(recipe["ingredients"] or "[]")]
    except (TypeError, ValueError):
        d["ingredients"] = []
    await state.set_state(RecipeManager.c_ing_cat)
    await state.update_data(d=d)
    await callback.message.answer(
        f"🧪 Состав рецепта «{recipe['name']}»\n\n"
        f"Сейчас: {_composition_str(d)}\n\n"
        "Выбери категорию и предмет — спрошу количество (0 — убрать). "
        "Когда состав готов — «✅ Состав готов».",
    )
    await _show_composition(callback.message, state, edit=False)


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