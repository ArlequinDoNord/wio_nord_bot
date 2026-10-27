"""Общее ядро крафта: проверки, списание/возврат и выдача результата.

Используется и жильём (`bot/handlers/housing.py`), и клан-холлом
(`bot/handlers/clan_hall.py`). Крафт всегда личный: ОД и ингредиенты
списываются у пилота, результат получает он же. Расширение (кухня или
крафтовый стол) лишь даёт доступ и задаёт максимальный уровень рецепта.

`CRAFTING` — общий на процесс per-user лок: не даёт запустить два крафта
одновременно ни в жилье, ни в клан-холле.
"""

import asyncio
import json
import os
import random
import time

from aiogram.types import FSInputFile, InlineKeyboardButton, InlineKeyboardMarkup

from database.db import (
    FOREST_RAW_MUSHROOMS,
    add_ap,
    add_inventory_item,
    bump_achievement,
    can_use_shower,
    consume_ingredient,
    get_achievement_bonus,
    get_db,
    get_ingredient_map,
    get_inventory,
    get_item_by_name,
    get_recipe,
    get_user,
    has_user_recipe,
    log_activity,
    mark_shower_used,
    remove_ap,
    remove_inventory_item,
)
from utils.states import DRUNK_STATES, reduce_state_minutes


class CraftError(Exception):
    """Отказ крафта: текст сообщения уже готов для показа игроку."""


# Готовая еда протухает через 6 дней: жареные блюда и выпечка (рыбный пирог).
FRIED_PREFIX = "Жареный "
FRIED_PREFIXES = ("Жареный ", "Жареная ", "Жареное ", "Жареные ")
FOOD_EXPIRY_SEC = 6 * 86400
FOOD_EXPIRY_PREFIXES = FRIED_PREFIXES + ("Рыбный ", "Жареный гриб", "Жареные грибы")

# Защита от двойного крафта (общая для жилья и клан-холла).
CRAFTING: set = set()


def parse_ingredients(recipe) -> list[tuple[str, int]]:
    """Ингредиенты рецепта как список пар (имя, количество).

    В БД они хранятся парами, но менеджер рецептов умеет писать словари —
    поддерживаем оба формата.
    """
    try:
        raw = json.loads(recipe["ingredients"] or "[]")
    except Exception:
        return []
    result = []
    for ing in raw:
        try:
            if isinstance(ing, dict):
                result.append((ing["name"], int(ing["qty"])))
            else:
                result.append((ing[0], int(ing[1])))
        except (KeyError, IndexError, TypeError, ValueError):
            continue
    return result


async def recipe_ap_cost(user_id: int, recipe) -> int:
    """Стоимость рецепта в ОД с учётом скидки за ачивку «Крафт»."""
    bonus = await get_achievement_bonus(user_id, "craft", "craft_ap_pct")
    return max(1, round(int(recipe["ap_cost"] or 0) * (100 - bonus) / 100))


async def refund_ingredients(user_id: int, consumed) -> None:
    """Возвращает в инвентарь уже списанное сырьё (откат неудачного крафта)."""
    for name, qty in consumed or ():
        item = await get_item_by_name(name)
        if item:
            await add_inventory_item(user_id, item["id"], qty)


async def begin_craft(user_id: int, recipe_id: int, expansion_type: str | None,
                      expansion_level: int) -> dict:
    """Проверяет рецепт и списывает ингредиенты/ОД.

    Уровень расширения проверяется здесь же, поэтому устаревшая кнопка не
    скрафтит рецепт выше уровня. При любой ошибке списанное возвращается, а
    `CRAFTING` освобождается. При успехе лок держится до `finish_craft` /
    `cancel_craft` / `end_craft`.
    """
    if user_id in CRAFTING:
        raise CraftError("⏳ Уже готовишься!")
    CRAFTING.add(user_id)
    consumed: list[tuple[str, int]] = []
    try:
        recipe = await get_recipe(recipe_id)
        if not recipe:
            raise CraftError("❌ Рецепт не найден.")
        if not await has_user_recipe(user_id, recipe_id):
            raise CraftError("❌ Ты ещё не изучил этот рецепт.")
        if not expansion_type or recipe["required_expansion"] != expansion_type:
            raise CraftError("❌ Это расширение не подходит для рецепта.")
        if int(expansion_level or 1) < int(recipe["required_level"] or 1):
            raise CraftError("❌ Рецепт выше уровня расширения.")

        ingredients = parse_ingredients(recipe)
        inv_map = await get_ingredient_map(user_id)
        for name, qty in ingredients:
            if inv_map.get(name, 0) < qty:
                raise CraftError(f"❌ Нет «{name}»!")

        ap_cost = await recipe_ap_cost(user_id, recipe)
        user = await get_user(user_id)
        if not user or int(user.get("ap") or 0) < ap_cost:
            raise CraftError("❌ Не хватает ОД!")

        for name, qty in ingredients:
            if not await consume_ingredient(user_id, name, qty):
                await refund_ingredients(user_id, consumed)
                raise CraftError(f"❌ Не удалось списать «{name}»!")
            consumed.append((name, qty))

        if not await remove_ap(user_id, ap_cost, reason="крафт"):
            await refund_ingredients(user_id, consumed)
            raise CraftError("❌ Не хватает ОД!")

        return {
            "recipe": recipe,
            "recipe_id": int(recipe_id),
            "ap_cost": ap_cost,
            "ingredients": ingredients,
            "consumed": consumed,
        }
    except Exception:
        CRAFTING.discard(user_id)
        raise


async def animate_craft(bot, chat_id: int, recipe, photo=None,
                        noop_data: str = "crafting:noop") -> None:
    """Показывает сообщение о приготовлении и выдерживает production_time."""
    wait = max(0, int(recipe["production_time"] or 0))
    text = f"🏭 Готовлю «{recipe['name']}»…\n\n⏳ ·"
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="⏳ Приготовление…", callback_data=noop_data)]])
    if photo:
        media = FSInputFile(photo) if os.path.isfile(str(photo)) else photo
        await bot.send_photo(chat_id, media, caption=text, reply_markup=kb)
    else:
        await bot.send_message(chat_id, text, reply_markup=kb)

    for _ in range(3):
        await asyncio.sleep(wait / 3)
    await asyncio.sleep(wait % 3)


async def can_craft_again(user_id: int, ctx: dict) -> bool:
    """Хватает ли ещё сырья и ОД на повторный крафт того же рецепта."""
    inv_map = await get_ingredient_map(user_id)
    for name, qty in ctx.get("ingredients") or ():
        if inv_map.get(name, 0) < qty:
            return False
    user = await get_user(user_id)
    return bool(user and int(user.get("ap") or 0) >= int(ctx.get("ap_cost") or 0))


async def finish_craft(user_id: int, ctx: dict) -> dict:
    """Выдаёт результат, начисляет ачивку и отпускает лок.

    Возвращает данные для экрана результата. Если предмет результата пропал
    из БД — сырьё возвращается, лок освобождается, бросается `CraftError`.
    """
    recipe = ctx["recipe"]
    result_name = recipe["result_item_name"]
    result_qty = int(recipe["result_quantity"] or 1)
    try:
        item = await get_item_by_name(result_name)
        if not item:
            raise CraftError(f"❌ Предмет «{result_name}» не найден.")

        expires_at = None
        if result_name.startswith(FOOD_EXPIRY_PREFIXES):
            expires_at = str(int(time.time()) + FOOD_EXPIRY_SEC)

        await add_inventory_item(user_id, item["id"], result_qty, expires_at=expires_at)

        if recipe["required_expansion"] == "kitchen":
            await bump_achievement(user_id, "cooking", result_qty)
        else:
            await bump_achievement(user_id, "craft", result_qty)

        return {
            "item_id": item["id"],
            "name": result_name,
            "qty": result_qty,
            "expires_at": expires_at,
            "can_repeat": await can_craft_again(user_id, ctx),
        }
    except Exception:
        await refund_ingredients(user_id, ctx.get("consumed"))
        CRAFTING.discard(user_id)
        raise
    finally:
        CRAFTING.discard(user_id)


async def cancel_craft(user_id: int, ctx: dict | None = None) -> None:
    """Откат незавершённого крафта: вернуть сырьё и освободить лок."""
    if ctx:
        await refund_ingredients(user_id, ctx.get("consumed"))
    CRAFTING.discard(user_id)


def end_craft(user_id: int) -> None:
    """Гарантированно освободить лок (вызывается в finally)."""
    CRAFTING.discard(user_id)


async def use_shower(user_id: int, level: int, *, ap_by_level: dict,
                     sober_by_level: dict, reason: str = "душевая") -> dict | None:
    """Раз в игровые сутки: +ОД и отрезвление.

    Возвращает данные для сообщения или None, если сегодня уже мылись.
    Кулдаун общий для жилья и клан-холла (`can_use_shower`).
    """
    if not await can_use_shower(user_id):
        return None
    ap_gain = int(ap_by_level.get(level) or ap_by_level.get(1) or 0)
    sober = int(sober_by_level.get(level) or sober_by_level.get(1) or 0)

    if ap_gain:
        await add_ap(user_id, ap_gain, reason=reason)
    await mark_shower_used(user_id)
    changes = await reduce_state_minutes(
        user_id, DRUNK_STATES, sober, reason=f"{reason}: протрезвел")

    note = f"+{ap_gain} ОД"
    if changes:
        note += f", опьянение −{sober} мин."
    await log_activity(user_id, "shower", note)

    return {"ap_gain": ap_gain, "sober": sober, "changes": changes}


# ── Переработка сырых грибов в порошок и эссенцию (на кухне, без рецепта) ──────

MUSHROOM_HEAL_POWDER_NAME = "Грибной целебный порошок"
MUSHROOM_ESSENCE_NAME = "Грибная эссенция"
MUSHROOM_POISON_POWDER_NAME = "Ядовитый грибной порошок"
MUSHROOM_PROCESS_AP_COST = 1

MUSHROOM_POWDER_SPECS = {
    "Опёнок": {
        "powder": MUSHROOM_HEAL_POWDER_NAME,
        "min": 1, "max": 2, "essence_chance": 0, "kind": "edible",
    },
    "Подберёзовик": {
        "powder": MUSHROOM_HEAL_POWDER_NAME,
        "min": 1, "max": 2, "essence_chance": 0, "kind": "edible",
    },
    "Лисичка": {
        "powder": MUSHROOM_HEAL_POWDER_NAME,
        "min": 2, "max": 3, "essence_chance": 0, "kind": "edible",
    },
    "Белый гриб": {
        "powder": MUSHROOM_HEAL_POWDER_NAME,
        "min": 2, "max": 3, "essence_chance": 0, "kind": "edible",
    },
    "Гиропор": {
        "powder": MUSHROOM_HEAL_POWDER_NAME,
        "min": 3, "max": 4, "essence_chance": 8, "kind": "edible",
    },
    "Ежовик гребенчатый": {
        "powder": MUSHROOM_HEAL_POWDER_NAME,
        "min": 4, "max": 5, "essence_chance": 17, "kind": "edible",
    },
    "Мухомор": {
        "powder": MUSHROOM_POISON_POWDER_NAME,
        "min": 1, "max": 2, "essence_chance": 0, "kind": "toxic",
    },
    "Бледная поганка": {
        "powder": MUSHROOM_POISON_POWDER_NAME,
        "min": 2, "max": 3, "essence_chance": 0, "kind": "toxic",
    },
}


def mushroom_powder_spec(name: str, rarity: int = 1, kind: str = "edible") -> dict:
    """Параметры переработки сырого гриба (с фолбэком для грибов из пула админа)."""
    if name in MUSHROOM_POWDER_SPECS:
        return dict(MUSHROOM_POWDER_SPECS[name])
    r = max(1, int(rarity or 1))
    if kind == "toxic":
        min_q, max_q = (1, 2) if r <= 1 else (2, 3)
        return {
            "powder": MUSHROOM_POISON_POWDER_NAME,
            "min": min_q, "max": max_q, "essence_chance": 0, "kind": "toxic",
        }
    if r <= 1:
        min_q, max_q, ess = 1, 2, 0
    elif r == 2:
        min_q, max_q, ess = 2, 3, 0
    elif r == 3:
        min_q, max_q, ess = 3, 4, 8
    else:
        min_q, max_q, ess = 4, 5, 17
    return {
        "powder": MUSHROOM_HEAL_POWDER_NAME,
        "min": min_q, "max": max_q, "essence_chance": ess, "kind": "edible",
    }


async def get_user_raw_mushrooms(user_id: int) -> list[dict]:
    """Сырые грибы в инвентаре пилота (для переработки на кухне без рецепта)."""
    conn = await get_db()
    fm_rows = await (await conn.execute(
        "SELECT item_id, kind FROM forest_mushrooms WHERE excluded = 0"
    )).fetchall()
    pool_kinds = {int(r["item_id"]): (r["kind"] or "edible") for r in fm_rows}

    inv = [dict(i) for i in await get_inventory(user_id)]
    by_item: dict[int, dict] = {}
    for row in inv:
        qty = int(row.get("quantity") or 0)
        if qty <= 0:
            continue
        item_id = int(row.get("item_id") or row["id"])
        name = row.get("name") or ""
        if name.startswith(FRIED_PREFIXES):
            continue
        if name in FOREST_RAW_MUSHROOMS:
            kind = FOREST_RAW_MUSHROOMS[name][4]
        elif item_id in pool_kinds:
            kind = pool_kinds[item_id]
        else:
            continue
        rarity = int(row.get("rarity") or 1)
        if item_id in by_item:
            by_item[item_id]["quantity"] += qty
        else:
            by_item[item_id] = {
                "item_id": item_id,
                "name": name,
                "quantity": qty,
                "rarity": rarity,
                "kind": kind,
                "spec": mushroom_powder_spec(name, rarity=rarity, kind=kind),
            }

    order_names = list(FOREST_RAW_MUSHROOMS.keys())

    def _sort_key(d: dict):
        n = d["name"]
        return (0, order_names.index(n)) if n in order_names else (1, d["item_id"])

    return sorted(by_item.values(), key=_sort_key)


async def process_mushrooms(user_id: int, item_id: int, mode: str = "1",
                            rng=None) -> dict:
    """Перерабатывает 1 или все сырые грибы выбранного вида в порошок (+эссенцию).

    Стоит `MUSHROOM_PROCESS_AP_COST` (1 ОД) за каждый гриб. При `mode == 'all'`
    проверяет достаточность ОД на все грибы этого вида в инвентаре.
    """
    if user_id in CRAFTING:
        raise CraftError("⏳ Уже готовишься!")
    rng = rng or random
    mushrooms = await get_user_raw_mushrooms(user_id)
    target = next((m for m in mushrooms if int(m["item_id"]) == int(item_id)), None)
    if not target or int(target["quantity"]) <= 0:
        raise CraftError("❌ У тебя нет таких грибов.")

    have_qty = int(target["quantity"])
    if mode == "1":
        count = 1
    elif mode == "all":
        count = have_qty
    else:
        try:
            count = max(1, int(mode))
        except (TypeError, ValueError):
            count = 1
    if count > have_qty:
        raise CraftError("❌ Недостаточно грибов в инвентаре.")

    ap_cost = count * MUSHROOM_PROCESS_AP_COST
    user = await get_user(user_id)
    have_ap = int((user or {}).get("ap") or 0)
    if have_ap < ap_cost:
        raise CraftError(
            f"❌ Не хватает ОД: нужно {ap_cost} ОД "
            f"(по {MUSHROOM_PROCESS_AP_COST} ОД за гриб), а у тебя {have_ap} ОД."
        )

    spec = target["spec"]
    powder_item = await get_item_by_name(spec["powder"])
    if not powder_item:
        raise CraftError(f"❌ Предмет «{spec['powder']}» не найден.")
    essence_item = None
    if int(spec.get("essence_chance") or 0) > 0:
        essence_item = await get_item_by_name(MUSHROOM_ESSENCE_NAME)

    if not await remove_inventory_item(user_id, int(item_id), count):
        raise CraftError("❌ Не удалось списать грибы.")
    if not await remove_ap(
        user_id, ap_cost, reason=f"переработка грибов ({target['name']} x{count})"
    ):
        await add_inventory_item(user_id, int(item_id), count)
        raise CraftError("❌ Не хватает ОД!")

    powder_qty = sum(rng.randint(int(spec["min"]), int(spec["max"])) for _ in range(count))
    ess_chance = float(spec.get("essence_chance") or 0)
    essence_qty = 0
    if ess_chance > 0 and essence_item:
        essence_qty = sum(1 for _ in range(count) if rng.random() * 100 < ess_chance)

    await add_inventory_item(user_id, int(powder_item["id"]), powder_qty)
    if essence_qty > 0 and essence_item:
        await add_inventory_item(user_id, int(essence_item["id"]), essence_qty)

    ess_note = f" + «{MUSHROOM_ESSENCE_NAME}» x{essence_qty}" if essence_qty > 0 else ""
    await log_activity(
        user_id,
        "crafting",
        f"Переработал «{target['name']}» x{count} (−{ap_cost} ОД) → "
        f"«{spec['powder']}» x{powder_qty}{ess_note}",
    )
    return {
        "mushroom_id": int(item_id),
        "mushroom_name": target["name"],
        "processed_count": count,
        "ap_spent": ap_cost,
        "powder_name": spec["powder"],
        "powder_qty": powder_qty,
        "essence_name": MUSHROOM_ESSENCE_NAME if essence_qty > 0 else None,
        "essence_qty": essence_qty,
        "kind": spec["kind"],
    }

