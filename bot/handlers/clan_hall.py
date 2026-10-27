"""Клан-холл: клановый склад и строительство кланового здания (Фаза 1).

См. CLAN_HALL.md:
- общий склад клана (пожертвования ресурсов +1/+10/всё, журнал вкладов);
- выбор типа здания главой клана (Дом Клана / Клановое поместье /
  Индивидуальный проект резиденции клана);
- сбор ресурсов на складе + оплата НМ лидером -> старт строительства
  (либо двойная оплата НМ без сбора ресурсов);
- во время стройки/апгрейда отображается общая картинка-заглушка стройки,
  а после постройки — индивидуальная картинка здания клана (устанавливается админом);
- ленивое завершение стройки по таймеру + вход внутрь здания.
"""

import html
import json

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    Message,
)

import config
from database.db import (
    PLANT_NAMES,
    PLANT_STAGES,
    can_harvest_clan_garden,
    can_manage_clan_hall,
    can_use_shower,
    buy_clan_shop_item,
    cancel_clan_building,
    choose_clan_building,
    choose_clan_upgrade,
    clan_expansion_icon,
    clan_expansion_max_level,
    clan_expansion_name,
    clan_expansion_slots,
    clan_garden_plots,
    clan_plot_info,
    donate_to_clan_storage,
    donate_recipe_to_clan_library,
    ensure_clan_building,
    get_clan,
    get_clan_building,
    get_clan_construction_photo,
    get_clan_contributions,
    get_clan_expansion,
    get_clan_expansions,
    get_clan_garden,
    get_clan_members,
    get_clan_project_progress,
    get_clan_recipes,
    get_clan_recipes_ids,
    get_clan_shop_items,
    get_clan_shop_item,
    get_clan_storage,
    get_clan_storage_qty,
    get_ingredient_map,
    get_inventory,
    get_inventory_item,
    get_item,
    get_learned_recipes,
    get_recipe,
    get_user,
    harvest_clan_plot,
    has_clan_recipe,
    get_clan_shop_bought_today,
    has_user_recipe,
    install_clan_expansion,
    is_clan_member,
    next_clan_building_type,
    get_clan_shop_item,
    plant_clan_seed,
    resolve_clan_building_with_event,
    set_clan_building_photo,
    set_clan_construction_photo,
    start_clan_building_project,
    upgrade_clan_expansion,
)
from utils.crafting import (
    MUSHROOM_ESSENCE_NAME,
    MUSHROOM_HEAL_POWDER_NAME,
    MUSHROOM_POISON_POWDER_NAME,
    MUSHROOM_PROCESS_AP_COST,
    CraftError,
    animate_craft,
    begin_craft,
    cancel_craft,
    end_craft,
    finish_craft,
    get_user_raw_mushrooms,
    parse_ingredients,
    process_mushrooms,
    recipe_ap_cost,
    use_shower,
)
from utils.permissions import has_permission

router = Router()

# Пока CLAN_HALL_ENABLED=False (Фаза 2 не доделана), весь клан-холл закрыт:
# роутерные middleware не пускают ни один `clanh:`-колбэк и ни один шаг FSM,
# даже если у кого-то осталась старая кнопка в переписке.
CLAN_HALL_CLOSED_TEXT = "🏗 Клановое здание ещё дорабатывается — скоро откроем."


async def clan_hall_guard(handler, event, data):
    if getattr(config, "CLAN_HALL_ENABLED", False):
        return await handler(event, data)
    try:
        if isinstance(event, CallbackQuery):
            await event.answer(CLAN_HALL_CLOSED_TEXT, show_alert=True)
        else:
            await event.answer(CLAN_HALL_CLOSED_TEXT)
    except Exception:
        pass
    return None


router.callback_query.middleware(clan_hall_guard)
router.message.middleware(clan_hall_guard)
router.edited_message.middleware(clan_hall_guard)

STORAGE_PAGE = 12


class ClanHallAdminPhoto(StatesGroup):
    wait_building_photo = State()
    wait_construction_photo = State()


def _esc(text) -> str:
    return html.escape(str(text or ""))


def _building_cfg(btype: str | None) -> dict:
    btypes = getattr(config, "CLAN_BUILDING_TYPES", {})
    return btypes.get(btype or "", {})


async def resolve_clan_hall_photo(building_row) -> str | None:
    """Подбирает фото для экрана клан-холла по статусу здания.

    - building / upgrading -> общая картинка-заглушка стройки (settings.clan_construction_photo);
    - built -> индивидуальная картинка здания клана (clan_buildings.building_photo_file_id);
    - choosing / funding -> None.
    """
    if not building_row:
        return None
    status = building_row["status"]
    if status in ("building", "upgrading"):
        return await get_clan_construction_photo()
    if status == "built":
        photo = building_row["building_photo_file_id"] if "building_photo_file_id" in building_row.keys() else None
        return (photo or "").strip() or None
    return None


async def notify_clan_members(bot, clan_id: int, text: str) -> int:
    """Рассылка уведомления всем членам клана (старт/завершение стройки или апгрейда)."""
    if not bot:
        return 0
    members = await get_clan_members(clan_id)
    sent = 0
    for m in members:
        try:
            await bot.send_message(m["user_id"], text, parse_mode="HTML")
            sent += 1
        except Exception:
            pass
    return sent


# ── Текстовые билдеры ──────────────────────────────────────────────────────────

def build_clan_storage_text(clan, rows) -> str:
    lines = [f"📦 <b>Клановый склад</b> — «{_esc(clan['name'])}»", ""]
    if not rows:
        lines.append("Склад пуст. Внеси ресурсы первым!")
    else:
        total = 0
        for r in rows:
            total += r["qty"]
            lines.append(f"• {_esc(r['name'])} — <b>{r['qty']}</b>")
        lines.append(f"\nВсего единиц: <b>{total}</b>")
    lines.append("\nВклад невозвратен: ресурсы идут на нужды клана.")
    return "\n".join(lines)


def build_donate_text(clan, items) -> str:
    lines = [
        f"➕ <b>Внести ресурсы</b> — «{_esc(clan['name'])}»",
        "",
        "Выбери ресурс из инвентаря. Вклад невозвратен.",
    ]
    if not items:
        lines.append("\nУ тебя нет ресурсов для вклада.")
    return "\n".join(lines)


def build_donate_item_text(item, have: int, stored: int) -> str:
    return (
        f"📦 <b>{_esc(item['name'])}</b>\n\n"
        f"У тебя: <b>{have}</b>\n"
        f"На складе клана: <b>{stored}</b>\n\n"
        "Сколько внести? Вклад невозвратен."
    )


def build_contrib_text(clan, rows) -> str:
    lines = [f"🧾 <b>Вклады</b> — «{_esc(clan['name'])}»", ""]
    if not rows:
        lines.append("Пока никто ничего не вносил.")
    else:
        for r in rows:
            who = _esc(r["user_name"] or f"#{r['user_id']}")
            item = _esc(r["item_name"] or f"#{r['item_id']}")
            day = str(r["created_at"] or "")[:10]
            lines.append(f"• {who}: {item} × {r['qty']}  <i>{day}</i>")
    return "\n".join(lines)


def build_hall_choosing_text(clan, is_leader: bool) -> str:
    lines = [
        f"🏰 <b>Здание клана</b> — «{_esc(clan['name'])}»",
        "",
        "У клана пока нет собственного здания. Доступные проекты:",
        "",
    ]
    btypes = getattr(config, "CLAN_BUILDING_TYPES", {})
    mult = int(getattr(config, "CLAN_BUILDING_NO_RESOURCES_MULT", 2) or 2)
    for key, cfg in btypes.items():
        req_parts = [f"{_esc(k)} × {v}" for k, v in (cfg.get("required") or {}).items()]
        req_str = ", ".join(req_parts) if req_parts else "нет"
        price = int(cfg.get("price_nm") or 0)
        lines.append(
            f"• <b>{_esc(cfg['name'])}</b> — слотов: <b>{cfg['slots']}</b> "
            f"(макс. ур. {cfg['max_level']}), срок: <b>{cfg['days']} дн.</b>\n"
            f"  💰 {price} НМ + 📦 {req_str}\n"
            f"  💰 {price * mult} НМ без ресурсов (двойная цена)"
        )
    lines.append("")
    if is_leader:
        lines.append("👑 Выбери проект здания, чтобы начать сбор ресурсов на складе клана.")
    else:
        lines.append("⏳ Ожидаем, пока глава клана выберет проект здания.")
    return "\n".join(lines)


def build_hall_funding_text(clan, building_row, progress: list[dict],
                            leader_nm: int = 0, is_leader: bool = False) -> str:
    status = building_row["status"] if "status" in building_row.keys() else None
    is_upgrade = status == "upgrade_funding"
    if is_upgrade:
        cur_cfg = _building_cfg(building_row["building_type"])
        cur_name = cur_cfg.get("name") or building_row["building_type"] or "Здание клана"
        btype = building_row["target_type"]
    else:
        cur_name = ""
        btype = building_row["building_type"]
    cfg = _building_cfg(btype)
    bname = cfg.get("name") or btype or "Здание клана"
    slots = cfg.get("slots", 0)
    max_lvl = cfg.get("max_level", 1)
    days = cfg.get("days", 2)
    price_nm = int(building_row["price_nm"] or cfg.get("price_nm") or 0)
    mult = int(getattr(config, "CLAN_BUILDING_NO_RESOURCES_MULT", 2) or 2)
    nores_price = price_nm * mult

    if is_upgrade:
        lines = [
            f"⬆️ <b>Улучшение: {_esc(cur_name)} → {_esc(bname)}</b> — «{_esc(clan['name'])}»",
            f"Этап: <b>Сбор ресурсов на улучшение</b> "
            f"(работы: {days} дн., слотов станет: {slots}, макс. ур.: {max_lvl})",
            "",
            "<b>Ресурсы на клановом складе:</b>",
        ]
    else:
        lines = [
            f"🏗 <b>Проект: {_esc(bname)}</b> — «{_esc(clan['name'])}»",
            f"Этап: <b>Сбор ресурсов</b> (срок постройки: {days} дн., "
            f"слотов: {slots}, макс. ур.: {max_lvl})",
            "",
            "<b>Ресурсы на клановом складе:</b>",
        ]
    all_ok = bool(progress)
    for r in progress:
        mark = "✅" if r["ok"] else "⏳"
        if not r["ok"]:
            all_ok = False
        lines.append(f"{mark} {_esc(r['name'])}: <b>{r['have']}/{r['need']}</b>")
    lines.append("")
    if is_leader:
        nm_ok = leader_nm >= price_nm
        nm_mark = "✅" if nm_ok else "⏳"
        lines.append(f"{nm_mark} Оплата работ главой: <b>{price_nm} НМ</b> (у тебя: {leader_nm} НМ)")
        nores_mark = "✅" if leader_nm >= nores_price else "⏳"
        lines.append(
            f"{nores_mark} Без сбора ресурсов: <b>{nores_price} НМ</b> "
            f"(двойная цена, склад не тратится)"
        )
    else:
        lines.append(f"💰 Оплата работ главой: <b>{price_nm} НМ</b> + ресурсы")
        lines.append(f"💰 Либо без ресурсов: <b>{nores_price} НМ</b> (двойная цена)")

    if all_ok:
        action = "улучшение" if is_upgrade else "стройку"
        lines.append(f"\n✅ Все ресурсы собраны! Глава клана может запустить {action}.")
    else:
        action = "улучшения" if is_upgrade else "стройки"
        lines.append(
            "\nВносите ресурсы на склад клана — или глава может оплатить "
            f"двойную цену ({nores_price} НМ) и начать {action} сразу без ресурсов."
        )
    return "\n".join(lines)


def build_hall_building_text(clan, building_row) -> str:
    btype = building_row["building_type"]
    cfg = _building_cfg(btype)
    bname = cfg.get("name") or btype or "Здание клана"
    started = str(building_row["started_at"] or "")[:16].replace("T", " ")
    completes = str(building_row["completes_at"] or "")[:16].replace("T", " ")
    lines = [
        f"🚧 <b>Строительство: {_esc(bname)}</b> — «{_esc(clan['name'])}»",
        "",
        "На стройплощадке кипит работа.",
        f"📅 Начато: <b>{started or '—'} UTC</b>",
        f"🏁 Завершение: <b>{completes or '—'} UTC</b>",
        "",
        "Пока идёт строительство, склад клана остаётся открытым для взносов.",
    ]
    return "\n".join(lines)


def build_hall_built_text(clan, building_row) -> str:
    btype = building_row["building_type"]
    cfg = _building_cfg(btype)
    bname = cfg.get("name") or btype or "Здание клана"
    slots = cfg.get("slots", 0)
    max_lvl = cfg.get("max_level", 1)
    lines = [
        f"🏰 <b>{_esc(bname)}</b> — «{_esc(clan['name'])}»",
        "",
        f"• Тип здания: <b>{_esc(bname)}</b>",
        f"• Слотов расширений: <b>{slots}</b> (макс. уровень: <b>{max_lvl}</b>)",
    ]
    if building_row["status"] == "upgrading":
        tcfg = _building_cfg(building_row["target_type"])
        tname = tcfg.get("name") or building_row["target_type"] or "новый уровень"
        completes = str(building_row["completes_at"] or "")[:16].replace("T", " ")
        lines.append(f"• 🚧 Идёт улучшение до «<b>{_esc(tname)}</b>» (до {completes} UTC)")
    has_photo = bool(
        "building_photo_file_id" in building_row.keys()
        and (building_row["building_photo_file_id"] or "").strip()
    )
    if not has_photo and building_row["status"] == "built":
        lines.append("\n<i>🖼 Индивидуальная картинка здания ещё не загружена.</i>")
    lines.append("\nДобро пожаловать в клан-холл!")
    return "\n".join(lines)


def build_hall_inside_text(clan, building_row, expansions=None) -> str:
    btype = building_row["building_type"]
    cfg = _building_cfg(btype)
    bname = cfg.get("name") or btype or "Здание клана"
    slots = int(cfg.get("slots") or 0)
    max_lvl = int(cfg.get("max_level") or 1)
    by_slot = {}
    for exp in (expansions or []):
        try:
            by_slot[int(exp["slot_index"])] = exp
        except Exception:
            continue
    lines = [
        f"🚪 <b>Внутри: {_esc(bname)}</b> — «{_esc(clan['name'])}»",
        f"Слоты расширений ({slots} шт., макс. ур. {max_lvl}):",
        "",
    ]
    for idx in range(1, slots + 1):
        exp = by_slot.get(idx)
        if btype == "castle" and idx == 7:
            lines.append(f"  {idx}. 🔒 <i>Резервный слот</i>")
        elif exp:
            et = exp["expansion_type"]
            lvl = int(exp["expansion_level"] or 1)
            lines.append(
                f"  {idx}. {clan_expansion_icon(et)} <b>{_esc(clan_expansion_name(et))}</b>"
                f" — ур. {lvl}")
        else:
            lines.append(f"  {idx}. ▫️ <i>Пустой слот</i>")
    status = building_row["status"] if "status" in building_row.keys() else None
    usable = [e for e in (expansions or [])
              if e["expansion_type"] in ("kitchen", "workbench", "shower",
                                         "garden", "library", "shop")]
    if usable:
        lines.append("\n🛠 Кухня, стол, душевые, сад, библиотека и лавка доступны всем — "
                     "крафт личный, урожай сада и книги идут на нужды клана.")
    if status == "upgrading":
        tcfg = _building_cfg(building_row["target_type"])
        tname = tcfg.get("name") or building_row["target_type"] or "новый уровень"
        completes = str(building_row["completes_at"] or "")[:16].replace("T", " ")
        lines.append(
            f"\n🚧 Идёт улучшение до «<b>{_esc(tname)}</b>»"
            + (f" (до {completes} UTC)" if completes else "")
        )
        lines.append(
            "Пока идут работы, доступны слоты и лимиты текущего уровня; "
            "ставить и улучшать расширения нельзя, а пользоваться уже "
            "установленными — можно."
        )
    lines.append("\n📦 Клановый склад и взносы доступны всем членам клана.")
    return "\n".join(lines)


def build_expansions_manage_text(clan, building_row, expansions) -> str:
    btype = building_row["building_type"]
    cfg = _building_cfg(btype)
    bname = cfg.get("name") or btype or "Здание клана"
    slots = clan_expansion_slots(btype)
    max_lvl = clan_expansion_max_level(btype)
    by_slot = {}
    for exp in (expansions or []):
        try:
            by_slot[int(exp["slot_index"])] = exp
        except Exception:
            continue
    lines = [
        f"⚙️ <b>Расширения</b> — «{_esc(clan['name'])}»",
        f"Здание: <b>{_esc(bname)}</b>",
        f"Доступно слотов: <b>{slots}</b> • макс. уровень: <b>{max_lvl}</b>",
        "",
    ]
    for idx in range(1, slots + 1):
        exp = by_slot.get(idx)
        if exp:
            et = exp["expansion_type"]
            lvl = int(exp["expansion_level"] or 1)
            lines.append(
                f"  {idx}. {clan_expansion_icon(et)} <b>{_esc(clan_expansion_name(et))}</b>"
                f" — ур. {lvl}")
        else:
            lines.append(f"  {idx}. ▫️ <i>Пустой слот</i>")
    if btype == "castle":
        lines.append(f"  {clan_expansion_slots(btype) + 1}. 🔒 <i>Резервный слот</i>")
    lines.append("")
    lines.append("• Установка — бесплатная, тип выбирает глава клана.")
    lines.append("• Улучшение — мгновенное: НМ главы + ресурсы с кланового склада.")
    upgrades = getattr(config, "CLAN_EXPANSION_UPGRADE", {})
    if upgrades:
        lines.append("")
        lines.append("<b>Стоимость улучшений:</b>")
        for lvl in sorted(upgrades):
            u = upgrades[lvl] or {}
            req = ", ".join(f"{n} {q}" for n, q in (u.get("required") or {}).items())
            parts = [f"{int(u.get('nm') or 0)} НМ"]
            if req:
                parts.append(req)
            lines.append(f"• до ур. {lvl}: {' • '.join(parts)}")
    return "\n".join(lines)


def build_expansion_choose_text(clan, building_row, slot_index, available) -> str:
    cfg = _building_cfg(building_row["building_type"])
    bname = cfg.get("name") or building_row["building_type"] or "Здание клана"
    lines = [
        f"🧩 <b>Выбор расширения — слот {slot_index}</b>",
        f"Клан «{_esc(clan['name'])}», здание: <b>{_esc(bname)}</b>",
        "",
        "Доступные типы (каждый — только один раз на клан):",
    ]
    for et in available:
        lines.append(f"• {clan_expansion_icon(et)} <b>{_esc(clan_expansion_name(et))}</b> — "
                     f"{_esc(getattr(config, 'CLAN_EXPANSION_INFO', {}).get(et, {}).get('desc') or '')}")
    lines.append("")
    lines.append("Установка бесплатна.")
    return "\n".join(lines)


def build_clan_room_text(clan, building_row, expansion, learned, level: int,
                         clan_only=()) -> str:
    """Экран кухни/крафтового стола внутри клан-холла (личные + клановые рецепты)."""
    et = expansion["expansion_type"]
    icon = clan_expansion_icon(et)
    name = clan_expansion_name(et)
    cfg = _building_cfg(building_row["building_type"])
    bname = cfg.get("name") or building_row["building_type"] or "Здание клана"

    available = [r for r in learned if int(r["required_level"] or 1) <= level]
    locked = [r for r in learned if int(r["required_level"] or 1) > level]
    clan_avail = [r for r in clan_only if int(r["required_level"] or 1) <= level]
    clan_locked = [r for r in clan_only if int(r["required_level"] or 1) > level]
    lines = [
        f"{icon} <b>{_esc(name)}</b> (ур. {level}) — «{_esc(clan['name'])}»",
        f"Здание: <b>{_esc(bname)}</b>",
        "",
        "Крафт личный: ингредиенты и ОД списываются у тебя, результат — в твой инвентарь.",
        "Уровень кланового расширения задаёт, какие рецепты доступны.",
        "",
    ]
    if not learned and not clan_only:
        lines.append("Нет выученных рецептов.")
        lines.append("Купи «📜 Рецепты» в Магазине 🏪 или сдай книгу в клановую библиотеку.")
    else:
        if available:
            lines.append("Доступные рецепты:")
            for r in available:
                lines.append(f"  • {_esc(r['name'])}")
        elif not clan_avail:
            lines.append("Рецептов для этого уровня нет.")
        if clan_avail:
            lines.append("Из клановой библиотеки:")
            for r in clan_avail:
                lines.append(f"  • 📚 {_esc(r['name'])}")
        if locked:
            lines.append("")
            lines.append(f"🔒 Выучено, но нужно расширение выше (твоё — {level} ур.):")
            for r in locked:
                lines.append(f"  • {_esc(r['name'])} — нужен ур. {int(r['required_level'] or 1)}")
        if clan_locked:
            lines.append("")
            lines.append(f"🔒 В клановой библиотеке, но нужен уровень выше (твой — {level} ур.):")
            for r in clan_locked:
                lines.append(f"  • {_esc(r['name'])} — нужен ур. {int(r['required_level'] or 1)}")
    return "\n".join(lines)


def build_clan_shower_text(clan, expansion, level: int, can_use: bool) -> str:
    """Экран клановых душевых: +ОД и отрезвление по уровню."""
    ap_gain = int(getattr(config, "CLAN_SHOWER_AP_BY_LEVEL", {}).get(level, 25))
    sober = int(getattr(config, "CLAN_SHOWER_SOBER_MINUTES", {}).get(level, 60))
    lines = [
        f"🚿 <b>Душевые</b> (ур. {level}) — «{_esc(clan['name'])}»",
        "",
    ]
    if can_use:
        lines.append(f"Раз в игровые сутки можно освежиться: <b>+{ap_gain} ОД</b> "
                     f"и −{sober} мин к состояниям «пьян» и «очень пьян».")
        lines.append("Кулдаун личный и общий с душевой в жилье.")
    else:
        lines.append("✅ Сегодня ты уже мылся — приходи после сброса суток.")
    return "\n".join(lines)


def build_clan_garden_text(clan, building_row, expansion, garden_map: dict,
                           planters: dict, is_leader: bool) -> str:
    """Экран кланового сада: уровень, число грядок, состояние каждой грядки."""
    level = int(expansion["expansion_level"] or 1)
    max_plots = clan_garden_plots(level)
    cfg = _building_cfg(building_row["building_type"])
    bname = cfg.get("name") or building_row["building_type"] or "Здание клана"
    lines = [
        f"🌱 <b>Сад</b> (ур. {level}) — «{_esc(clan['name'])}»",
        f"Здание: <b>{_esc(bname)}</b> • Грядок: <b>{max_plots}</b>",
        "",
        "Сажать может любой член клана (семя списывается из твоего инвентаря).",
        "Собирает урожай только глава клана — плоды идут в клановый склад.",
        "",
    ]
    any_ripe = False
    for plot_idx in range(1, max_plots + 1):
        plot = (garden_map or {}).get(plot_idx)
        if not plot:
            lines.append(f"  {plot_idx}. ▫️ <i>Пустая грядка</i>")
            continue
        info = clan_plot_info(plot)
        stage = int(info["stage"] or 0)
        stage_name = PLANT_STAGES[stage][0]
        fruits = int(info["fruits"] or 0)
        next_in = float(info["next_in"] or 0)
        seed_name = plot.get("seed_name") or ""
        plant_name = plot.get("plant_name") or PLANT_NAMES.get(seed_name, seed_name)
        planter_id = plot.get("planted_by")
        planter_name = (planters or {}).get(int(planter_id)) if planter_id else None
        who = f" (посадил: {_esc(planter_name)})" if planter_name else ""
        if stage < 4 and next_in > 0:
            tail = f"{stage_name}, до след. стадии {next_in / 86400:.1f} сут."
        elif fruits > 0:
            any_ripe = True
            tail = f"{stage_name}, 🍎 плодов: {fruits}/5"
        else:
            tail = f"{stage_name}, до плодов {next_in / 86400:.1f} сут."
        lines.append(f"  {plot_idx}. 🌿 <b>{_esc(plant_name)}</b> — {tail}{who}")
    if any_ripe and not is_leader:
        lines.append("\n<i>Собрать спелые плоды на клановый склад может глава клана.</i>")
    return "\n".join(lines)


def build_clan_library_text(clan, building_row, expansion, clan_recipe_rows) -> str:
    """Экран клановой библиотеки рецептов (Фаза 6)."""
    level = int(expansion["expansion_level"] or 1)
    cfg = _building_cfg(building_row["building_type"])
    bname = cfg.get("name") or building_row["building_type"] or "Здание клана"
    lines = [
        f"📚 <b>Библиотека рецептов</b> (ур. {level}) — «{_esc(clan['name'])}»",
        f"Здание: <b>{_esc(bname)}</b>",
        "",
        "Рецепты из библиотеки доступны ВСЕМ членам клана в кухне и крафтовом столе",
        "(гейт по уровню кухни/стола — как обычно). Книга сдаётся навсегда.",
        "",
    ]
    if not clan_recipe_rows:
        lines.append("Библиотека пуста. Сдай первую книгу рецептов из инвентаря!")
    else:
        lines.append("Рецепты клана:")
        for r in clan_recipe_rows:
            lines.append(f"  📖 {_esc(r['recipe_name'] or ('#' + str(r['recipe_id'])))}")
        lines.append(f"\nВсего рецептов: <b>{len(clan_recipe_rows)}</b>")
    return "\n".join(lines)


def build_clan_shop_text(clan, building_row, expansion, shop_rows,
                         bought: int) -> str:
    """Экран клановой лавки (Фаза 7)."""
    level = int(expansion["expansion_level"] or 1)
    cfg = _building_cfg(building_row["building_type"])
    bname = cfg.get("name") or building_row["building_type"] or "Здание клана"
    limit = int(getattr(config, "CLAN_SHOP_DAILY_LIMIT", 3) or 0)
    lines = [
        f"🏪 <b>Клановая лавка</b> (ур. {level}) — «{_esc(clan['name'])}»",
        f"Здание: <b>{_esc(bname)}</b>",
        "",
    ]
    if limit > 0:
        lines.append(f"Покупок на тебя сегодня: <b>{bought}</b> из {limit}, "
                     "лимит общий на всю лавку. Сутки — игровое время города.")
    lines.append("")
    if not shop_rows:
        lines.append("Лавка пока пуста — админ добавит товары накидкой и дисплеем.")
    else:
        lines.append("Товары:")
        for r in shop_rows:
            stock = r.get("stock")
            stock_txt = "∞" if stock is None or int(stock) < 0 else f"ост. {int(stock)}"
            lines.append(f"  • {_esc(r['name'])} — 💰 {int(r['price'])} НМ "
                         f"({stock_txt})")
    return "\n".join(lines)


# ── Отрисовка и проверки доступа ──────────────────────────────────────────────

async def _paint(cb: CallbackQuery, text: str, kb: InlineKeyboardMarkup,
                 photo: str | None = None):
    """Рисует экран с учётом фото (заглушка стройки / индивидуальное фото здания)."""
    msg = cb.message
    if photo:
        try:
            if getattr(msg, "photo", None):
                return await msg.edit_media(
                    media=InputMediaPhoto(media=photo, caption=text, parse_mode="HTML"),
                    reply_markup=kb,
                )
            new = await msg.answer_photo(
                photo=photo, caption=text, parse_mode="HTML", reply_markup=kb
            )
            try:
                await msg.delete()
            except Exception:
                pass
            return new
        except Exception:
            pass
    try:
        if getattr(msg, "photo", None):
            new = await msg.answer(text, reply_markup=kb, parse_mode="HTML")
            try:
                await msg.delete()
            except Exception:
                pass
            return new
        return await msg.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except Exception:
        return await msg.answer(text, reply_markup=kb, parse_mode="HTML")


async def _member_clan(cb: CallbackQuery, clan_id: int):
    """Клан, если отправитель — его член. Иначе alert и None."""
    clan = await get_clan(clan_id)
    if not clan or clan["kind"] != "clan":
        await cb.answer("❌ Клан не найден.", show_alert=True)
        return None
    if not await is_clan_member(clan_id, cb.from_user.id):
        await cb.answer("❌ Доступно только членам клана.", show_alert=True)
        return None
    return clan


# ── Экраны здания клана (Фаза 1) ──────────────────────────────────────────────

async def _render_hall(cb: CallbackQuery, clan, building_row):
    clan_id = int(clan["id"])
    uid = cb.from_user.id
    is_leader = await can_manage_clan_hall(clan_id, uid)
    is_admin = await has_permission(uid, "can_manage_clans")
    status = building_row["status"]
    photo = await resolve_clan_hall_photo(building_row)

    if status == "choosing":
        text = build_hall_choosing_text(clan, is_leader)
        rows = []
        if is_leader:
            btypes = getattr(config, "CLAN_BUILDING_TYPES", {})
            for key, cfg in btypes.items():
                rows.append([InlineKeyboardButton(
                    text=f"🏗 Выбрать: {cfg['name']} ({cfg['price_nm']} НМ)",
                    callback_data=f"clanh:choose:{clan_id}:{key}",
                )])
        rows.append([InlineKeyboardButton(text="📦 Склад клана",
                                          callback_data=f"clanh:storage:{clan_id}")])
        rows.append([InlineKeyboardButton(text="🔙 К клану",
                                          callback_data=f"clans:view:{clan_id}")])
        return await _paint(cb, text, InlineKeyboardMarkup(inline_keyboard=rows), photo=None)

    if status in ("funding", "upgrade_funding"):
        is_upgrade = status == "upgrade_funding"
        try:
            req = json.loads(building_row["required_json"] or "{}")
        except Exception:
            req = {}
        progress, all_ok = await get_clan_project_progress(clan_id, req)
        leader_user = await get_user(uid) if is_leader else None
        leader_nm = int((leader_user["nordmarks"] if leader_user else 0) or 0)
        text = build_hall_funding_text(clan, building_row, progress,
                                       leader_nm=leader_nm, is_leader=is_leader)
        rows = [
            [InlineKeyboardButton(text="➕ Внести ресурсы",
                                  callback_data=f"clanh:donate:{clan_id}")],
            [InlineKeyboardButton(text="📦 Склад клана",
                                  callback_data=f"clanh:storage:{clan_id}")],
        ]
        if is_leader:
            price_nm = int(building_row["price_nm"] or 0)
            mult = int(getattr(config, "CLAN_BUILDING_NO_RESOURCES_MULT", 2) or 2)
            start_label = ("🚀 Начать улучшение" if is_upgrade
                           else "🚀 Начать строительство")
            if all_ok:
                rows.append([InlineKeyboardButton(
                    text=f"{start_label} ({price_nm} НМ)",
                    callback_data=f"clanh:start:{clan_id}",
                )])
            nores_label = ("💰 Начать улучшение без ресурсов" if is_upgrade
                           else "💰 Начать без ресурсов")
            rows.append([InlineKeyboardButton(
                text=f"{nores_label} ({price_nm * mult} НМ)",
                callback_data=f"clanh:startfull:{clan_id}",
            )])
            cancel_label = ("↩️ Отменить улучшение" if is_upgrade
                            else "↩️ Сменить / отменить проект")
            rows.append([InlineKeyboardButton(
                text=cancel_label,
                callback_data=f"clanh:cancel:{clan_id}",
            )])
        rows.append([InlineKeyboardButton(text="🔙 К клану",
                                          callback_data=f"clans:view:{clan_id}")])
        return await _paint(cb, text, InlineKeyboardMarkup(inline_keyboard=rows), photo=None)

    if status == "building":
        text = build_hall_building_text(clan, building_row)
        rows = [
            [InlineKeyboardButton(text="🔄 Обновить",
                                  callback_data=f"clanh:hall:{clan_id}")],
            [InlineKeyboardButton(text="📦 Склад клана",
                                  callback_data=f"clanh:storage:{clan_id}")],
        ]
        if is_admin:
            rows.append([InlineKeyboardButton(
                text="🏗 Фото-заглушка стройки (админ)",
                callback_data=f"clanh:admconstphoto:{clan_id}",
            )])
        rows.append([InlineKeyboardButton(text="🔙 К клану",
                                          callback_data=f"clans:view:{clan_id}")])
        return await _paint(cb, text, InlineKeyboardMarkup(inline_keyboard=rows), photo=photo)

    # built / upgrading
    text = build_hall_built_text(clan, building_row)
    rows = []
    if status == "built" and is_leader:
        nxt = next_clan_building_type(building_row["building_type"])
        if nxt:
            ncfg = _building_cfg(nxt)
            nname = ncfg.get("name") or nxt
            rows.append([InlineKeyboardButton(
                text=f"⬆️ Улучшить до «{nname}»",
                callback_data=f"clanh:upgrade:{clan_id}",
            )])
    rows.append([InlineKeyboardButton(text="🚪 Войти в здание",
                                      callback_data=f"clanh:inside:{clan_id}")])
    rows.append([InlineKeyboardButton(text="📦 Склад клана",
                                      callback_data=f"clanh:storage:{clan_id}")])
    if is_admin and status == "upgrading":
        rows.append([InlineKeyboardButton(
            text="🏗 Фото-заглушка стройки (админ)",
            callback_data=f"clanh:admconstphoto:{clan_id}",
        )])
    if is_admin and status == "built":
        rows.append([InlineKeyboardButton(
            text="🖼 Установить фото здания (админ)",
            callback_data=f"clanh:admphoto:{clan_id}",
        )])
        has_bphoto = bool(
            "building_photo_file_id" in building_row.keys()
            and (building_row["building_photo_file_id"] or "").strip()
        )
        if has_bphoto:
            rows.append([InlineKeyboardButton(
                text="❌ Убрать фото здания (админ)",
                callback_data=f"clanh:admnophoto:{clan_id}",
            )])
    rows.append([InlineKeyboardButton(text="🔙 К клану",
                                      callback_data=f"clans:view:{clan_id}")])
    return await _paint(cb, text, InlineKeyboardMarkup(inline_keyboard=rows), photo=photo)


# ── Расширения (Фаза 3): управление и выбор типа ──────────────────────────────

async def _render_expansions(cb: CallbackQuery, clan, building_row):
    """Экран управления расширениями (только глава и только готовое здание)."""
    clan_id = int(clan["id"])
    if not await can_manage_clan_hall(clan_id, cb.from_user.id):
        await cb.answer("❌ Управлять расширениями может только глава клана.",
                        show_alert=True)
        return
    if building_row["status"] != "built" or not building_row["building_type"]:
        await cb.answer("❌ Управление расширениями доступно только в готовом здании.",
                        show_alert=True)
        return
    btype = building_row["building_type"]
    slots = clan_expansion_slots(btype)
    max_lvl = clan_expansion_max_level(btype)
    expansions = await get_clan_expansions(clan_id)
    by_slot = {}
    for exp in expansions:
        try:
            by_slot[int(exp["slot_index"])] = exp
        except Exception:
            continue
    text = build_expansions_manage_text(clan, building_row, expansions)
    upgrades = getattr(config, "CLAN_EXPANSION_UPGRADE", {})
    rows = []
    for idx in range(1, slots + 1):
        exp = by_slot.get(idx)
        if not exp:
            rows.append([InlineKeyboardButton(
                text=f"➕ Слот {idx}: выбрать расширение",
                callback_data=f"clanh:expchoose:{clan_id}:{idx}",
            )])
            continue
        lvl = int(exp["expansion_level"] or 1)
        if lvl < max_lvl and (lvl + 1) in upgrades:
            et = exp["expansion_type"]
            rows.append([InlineKeyboardButton(
                text=f"⬆️ {clan_expansion_name(et)}: ур. {lvl}→{lvl + 1}",
                callback_data=f"clanh:expup:{clan_id}:{idx}",
            )])
    rows.append([InlineKeyboardButton(text="🚪 Внутрь здания",
                                      callback_data=f"clanh:inside:{clan_id}")])
    rows.append([InlineKeyboardButton(text="📦 Склад клана",
                                      callback_data=f"clanh:storage:{clan_id}")])
    rows.append([InlineKeyboardButton(text="🔙 К клану",
                                      callback_data=f"clans:view:{clan_id}")])
    return await _paint(cb, text, InlineKeyboardMarkup(inline_keyboard=rows), photo=None)


async def _render_expansion_choose(cb: CallbackQuery, clan, building_row, slot_index: int):
    """Экран выбора типа расширения для конкретного пустого слота."""
    clan_id = int(clan["id"])
    if not await can_manage_clan_hall(clan_id, cb.from_user.id):
        await cb.answer("❌ Устанавливать расширения может только глава клана.",
                        show_alert=True)
        return
    if building_row["status"] != "built" or not building_row["building_type"]:
        await cb.answer("❌ Установка расширений доступна только в готовом здании.",
                        show_alert=True)
        return
    btype = building_row["building_type"]
    max_slot = clan_expansion_slots(btype)
    if slot_index < 1 or slot_index > max_slot:
        await cb.answer(f"❌ В этом здании доступно слотов: {max_slot}.", show_alert=True)
        return await _render_expansions(cb, clan, building_row)
    expansions = await get_clan_expansions(clan_id)
    if any(int(exp["slot_index"]) == slot_index for exp in expansions):
        await cb.answer("❌ Этот слот уже занят расширением.", show_alert=True)
        return await _render_expansions(cb, clan, building_row)
    installed = {exp["expansion_type"] for exp in expansions}
    all_types = getattr(config, "CLAN_EXPANSION_TYPES", ())
    available = [t for t in all_types if t not in installed]
    if not available:
        await cb.answer("❌ Все типы расширений уже установлены.", show_alert=True)
        return await _render_expansions(cb, clan, building_row)
    text = build_expansion_choose_text(clan, building_row, slot_index, available)
    rows = [[InlineKeyboardButton(
        text=f"{clan_expansion_icon(et)} {clan_expansion_name(et)}",
        callback_data=f"clanh:expinstall:{clan_id}:{slot_index}:{et}",
    )] for et in available]
    rows.append([InlineKeyboardButton(
        text="🔙 К управлению расширениями",
        callback_data=f"clanh:expmanage:{clan_id}",
    )])
    return await _paint(cb, text, InlineKeyboardMarkup(inline_keyboard=rows), photo=None)


async def _resolve_hall_for_expansions(cb: CallbackQuery, clan_id: int, clan):
    """Лениво завершает стройку/апгрейд и возвращает строку здания."""
    building, event = await resolve_clan_building_with_event(clan_id)
    if event in ("built", "upgraded"):
        bname = _building_cfg(building["building_type"]).get("name") or building["building_type"]
        if event == "built":
            note = (f"🎉 <b>Строительство завершено!</b>\n"
                    f"Здание клана «{_esc(clan['name'])}» — <b>{_esc(bname)}</b> — открыто!")
        else:
            note = (f"🎉 <b>Улучшение завершено!</b>\n"
                    f"Здание клана «{_esc(clan['name'])}» улучшено до «<b>{_esc(bname)}</b>»!")
        await notify_clan_members(getattr(cb, "bot", None), clan_id, note)
    return building


async def _load_usable(cb: CallbackQuery, clan_id: int, slot_index: int):
    """Членство + готовое/улучшающееся здание + расширение в слоте.

    Возвращает (clan, building, expansion) или (None, None, None) с alert.
    Использовать расширения можно и во время `upgrading` — работы блокируют
    только установку/улучшение, но не саму механику.
    """
    clan = await _member_clan(cb, clan_id)
    if not clan:
        return None, None, None
    building = await _resolve_hall_for_expansions(cb, clan_id, clan)
    if not building or building["status"] not in ("built", "upgrading"):
        await cb.answer("❌ Здание клана ещё не построено.", show_alert=True)
        return None, None, None
    exp = await get_clan_expansion(clan_id, slot_index)
    if not exp:
        await cb.answer("❌ В этом слоте нет расширения.", show_alert=True)
        return None, None, None
    return clan, building, exp


async def _render_clan_use(cb: CallbackQuery, clan, building, exp):
    """Экран использования расширения: рецепты кухни/стола или душевые."""
    clan_id = int(clan["id"])
    slot_index = int(exp["slot_index"])
    level = int(exp["expansion_level"] or 1)
    et = exp["expansion_type"]
    photo = await resolve_clan_hall_photo(building)

    if et in ("kitchen", "workbench"):
        learned = await get_learned_recipes(cb.from_user.id, et)
        # Рецепты из клановой библиотеки (Фаза 6): видны всем членам клана.
        clan_only = [r for r in await get_clan_recipes_for_roster(clan_id, et)
                     if not await has_user_recipe(cb.from_user.id, int(r["id"]))]
        text = build_clan_room_text(clan, building, exp, learned, level, clan_only=clan_only)
        rows = []
        for r in learned:
            if int(r["required_level"] or 1) <= level:
                rows.append([InlineKeyboardButton(
                    text=f"📋 {r['name']}",
                    callback_data=f"clanh:recipe:{clan_id}:{slot_index}:{r['id']}")])
        for r in clan_only:
            if int(r["required_level"] or 1) <= level:
                rows.append([InlineKeyboardButton(
                    text=f"📚 {r['name']}",
                    callback_data=f"clanh:recipe:{clan_id}:{slot_index}:{r['id']}")])
        if et == "kitchen":
            rows.append([InlineKeyboardButton(
                text="🍄 Переработка грибов",
                callback_data=f"clanh:mushrooms:{clan_id}:{slot_index}")])
        rows.append([InlineKeyboardButton(
            text="🔙 Внутрь здания", callback_data=f"clanh:inside:{clan_id}")])
        return await _paint(cb, text, InlineKeyboardMarkup(inline_keyboard=rows), photo=photo)

    if et == "shower":
        return await _render_clan_shower(cb, clan, building, exp)

    if et == "garden":
        return await _render_clan_garden(cb, clan, building, exp)

    if et == "library":
        return await _render_clan_library(cb, clan, building, exp)

    if et == "shop":
        return await _render_clan_shop(cb, clan, building, exp)

    await cb.answer(f"❌ {clan_expansion_name(et)} пока не работает.", show_alert=True)


async def _render_clan_shop(cb: CallbackQuery, clan, building, exp):
    """Экран клановой лавки: витрина + покупка (Фаза 7)."""
    clan_id = int(clan["id"])
    slot_index = int(exp["slot_index"])
    shop_rows = await get_clan_shop_items(clan_id, active_only=True)
    bought = await get_clan_shop_bought_today(clan_id, cb.from_user.id)
    text = build_clan_shop_text(clan, building, exp, shop_rows, bought)
    rows = []
    for r in shop_rows:
        stock = int(r.get("stock") if r.get("stock") is not None else -1)
        if stock == 0:
            continue  # распродано — кнопки нет
        rows.append([InlineKeyboardButton(
            text=f"🛒 {r['name']} — 💰 {int(r['price'])} НМ",
            callback_data=f"clanh:bitem:{clan_id}:{slot_index}:{r['item_id']}")])
    rows.append([InlineKeyboardButton(
        text="🔙 Внутрь здания", callback_data=f"clanh:inside:{clan_id}")])
    photo = await resolve_clan_hall_photo(building)
    await _paint(cb, text, InlineKeyboardMarkup(inline_keyboard=rows), photo=photo)


@router.callback_query(F.data.startswith("clanh:bitem:"))
async def clan_hall_bitem_cb(cb: CallbackQuery):
    """Карточка товара клановой лавки (подтверждение покупки)."""
    parts = cb.data.split(":")
    clan_id = int(parts[2])
    slot_index = int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else 0
    item_id = int(parts[4]) if len(parts) > 4 and parts[4].isdigit() else 0
    clan, building, exp = await _load_usable(cb, clan_id, slot_index)
    if not clan:
        return
    if exp["expansion_type"] != "shop":
        await cb.answer("❌ Лавка не установлена.", show_alert=True)
        return
    item = await get_clan_shop_item(clan_id, item_id)
    if not item or not item.get('is_active'):
        await cb.answer("❌ Товар скрыт или распродан.", show_alert=True)
        return
    limit = int(getattr(config, "CLAN_SHOP_DAILY_LIMIT", 3) or 0)
    bought = await get_clan_shop_bought_today(clan_id, cb.from_user.id)
    stock = item.get("stock")
    stock = int(stock) if stock is not None else -1
    avail_text = "∞" if stock < 0 else f"{stock} шт.\n"
    limit_text = f"Лимит: {limit}/день.\n" if limit > 0 else \
        "Без лимита на день."
    text = (
        f"🛒 {_esc(item['name'])} — 💰 {int(item['price'])} НМ\n"
        f"Оплата НМ со склада клана: {avail_text.strip() or '∞'}\n"
        f"{limit_text}"
        f"Осталось за сутки: {(limit - bought) if limit > 0 else 'без лимита'}\n\n"
        f"{_esc(item['description'] or '')}"
    )
    rows = [[InlineKeyboardButton(
        text="✅ Купить",
        callback_data=f"clanh:buy:{clan_id}:{slot_index}:{item_id}")],
        [InlineKeyboardButton(text="🏪 В лавку",
                              callback_data=f"clanh:use:{clan_id}:{slot_index}")],
        [InlineKeyboardButton(text="🚪 Внутрь здания",
                              callback_data=f"clanh:inside:{clan_id}")]]
    await cb.answer()
    photo = await resolve_clan_hall_photo(building)
    await _paint(cb, text, InlineKeyboardMarkup(inline_keyboard=rows), photo=photo)


@router.callback_query(F.data.startswith("clanh:buy:"))
async def clan_hall_buy_cb(cb: CallbackQuery):
    """Покупка в клановой лавке: лимиты и остатки считает buy_clan_shop_item в db."""
    parts = cb.data.split(":")
    clan_id = int(parts[2])
    slot_index = int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else 0
    item_id = int(parts[4]) if len(parts) > 4 and parts[4].isdigit() else 0
    clan, building, exp = await _load_usable(cb, clan_id, slot_index)
    if not clan:
        return
    if exp["expansion_type"] != "shop":
        await cb.answer("❌ Лавка не установлена.", show_alert=True)
        return
    ok, msg, left = await buy_clan_shop_item(clan_id, cb.from_user.id, item_id)
    if not ok:
        await cb.answer(msg, show_alert=True)
        return
    extra = f" Осталось покупок сегодня: {left}." if left is not None else ""
    await cb.answer(f"✅ {msg}{extra}", show_alert=True)
    await _render_clan_shop(cb, clan, building, exp)


async def get_clan_recipes_for_roster(clan_id: int, expansion_type: str) -> list:
    """Рецепты клановой библиотеки, пригодные для расширения этого типа."""
    rows = []
    for r in await get_clan_recipes(clan_id):
        full = await get_recipe(int(r["recipe_id"]))
        if full and full.get("is_available") and full.get("required_expansion") == expansion_type:
            rows.append(full)
    return rows


async def get_donatable_recipe_items(user_id: int) -> list:
    """Предметы-книги рецептов из инвентаря пользователя."""
    items = await get_inventory(user_id)
    donatable = []
    for i in items:
        if i.get("category") == "recipes" and i.get("is_available"):
            donatable.append(i)
    return donatable


async def _render_clan_library(cb: CallbackQuery, clan, building, exp):
    """Экран клановой библиотеки: список рецептов + сдача книги."""
    clan_id = int(clan["id"])
    slot_index = int(exp["slot_index"])
    clan_rows = await get_clan_recipes(clan_id)
    text = build_clan_library_text(clan, building, exp, clan_rows)
    rows = []
    for r in await get_donatable_recipe_items(cb.from_user.id):
        rows.append([InlineKeyboardButton(
            text=f"📄 Сдать: {r['name']}",
            callback_data=f"clanh:libgive:{clan_id}:{slot_index}:{r['id']}")])
    rows.append([InlineKeyboardButton(
        text="🔙 Внутрь здания", callback_data=f"clanh:inside:{clan_id}")])
    photo = await resolve_clan_hall_photo(building)
    await _paint(cb, text, InlineKeyboardMarkup(inline_keyboard=rows), photo=photo)


@router.callback_query(F.data.startswith("clanh:libgive:"))
async def clan_hall_libgive_cb(cb: CallbackQuery):
    """Сдача предмета-книги рецептов в клановую библиотеку (Фаза 6)."""
    parts = cb.data.split(":")
    clan_id = int(parts[2])
    slot_index = int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else 0
    item_id = int(parts[4]) if len(parts) > 4 and parts[4].isdigit() else 0
    clan = await _member_clan(cb, clan_id)
    if not clan:
        return
    exp = await get_clan_expansion(clan_id, slot_index)
    if not exp or exp["expansion_type"] != "library":
        await cb.answer("❌ Библиотека не установлена.", show_alert=True)
        return
    building = await get_clan_building(clan_id)
    if not building or building["status"] not in ("built", "upgrading"):
        await cb.answer("❌ Здание клана недоступно.", show_alert=True)
        return
    ok, msg, _ = await donate_recipe_to_clan_library(clan_id, cb.from_user.id, item_id)
    await cb.answer(msg, show_alert=True)
    if not ok:
        return
    await _render_clan_library(cb, clan, building, exp)


async def _render_clan_shower(cb: CallbackQuery, clan, building, exp):
    clan_id = int(clan["id"])
    slot_index = int(exp["slot_index"])
    level = int(exp["expansion_level"] or 1)
    can_use = await can_use_shower(cb.from_user.id)
    text = build_clan_shower_text(clan, exp, level, can_use)
    rows = []
    if can_use:
        ap_gain = int(getattr(config, "CLAN_SHOWER_AP_BY_LEVEL", {}).get(level, 25))
        rows.append([InlineKeyboardButton(
            text=f"🚿 Принять душ (+{ap_gain} ОД)",
            callback_data=f"clanh:shower:{clan_id}:{slot_index}")])
    rows.append([InlineKeyboardButton(
        text="🔙 Внутрь здания", callback_data=f"clanh:inside:{clan_id}")])
    photo = await resolve_clan_hall_photo(building)
    await _paint(cb, text, InlineKeyboardMarkup(inline_keyboard=rows), photo=photo)


async def _load_planter_names(garden_map: dict) -> dict:
    """Словарь user_id -> отображаемое имя для авторов посадки в саду."""
    planters = {}
    for plot in (garden_map or {}).values():
        uid = plot.get("planted_by")
        if not uid:
            continue
        uid = int(uid)
        if uid in planters:
            continue
        u = await get_user(uid)
        if u:
            planters[uid] = u["first_name"] or u["username"] or f"ID {uid}"
        else:
            planters[uid] = f"ID {uid}"
    return planters


async def _render_clan_garden(cb: CallbackQuery, clan, building, exp):
    """Экран кланового сада: грядки, посадка любым членом, сбор главой."""
    clan_id = int(clan["id"])
    slot_index = int(exp["slot_index"])
    level = int(exp["expansion_level"] or 1)
    max_plots = clan_garden_plots(level)
    garden = await get_clan_garden(clan_id)
    planters = await _load_planter_names(garden)
    is_leader = await can_harvest_clan_garden(clan_id, cb.from_user.id)
    text = build_clan_garden_text(clan, building, exp, garden, planters, is_leader)

    rows = []
    total_fruits = 0
    for plot_idx in range(1, max_plots + 1):
        plot = garden.get(plot_idx)
        if not plot:
            rows.append([InlineKeyboardButton(
                text=f"🌱 Грядка {plot_idx}: посадить семечко",
                callback_data=f"clanh:plantlist:{clan_id}:{slot_index}:{plot_idx}",
            )])
            continue
        info = clan_plot_info(plot)
        fruits = int(info["fruits"] or 0)
        if fruits > 0:
            total_fruits += fruits
            if is_leader:
                seed_name = plot.get("seed_name") or ""
                plant_name = plot.get("plant_name") or PLANT_NAMES.get(seed_name, seed_name)
                rows.append([InlineKeyboardButton(
                    text=f"🍎 Грядка {plot_idx} ({plant_name}): собрать ×{fruits}",
                    callback_data=f"clanh:harvest:{clan_id}:{slot_index}:{plot_idx}",
                )])

    if is_leader and total_fruits > 0:
        rows.append([InlineKeyboardButton(
            text=f"🧺 Собрать весь урожай ({total_fruits} шт.)",
            callback_data=f"clanh:harvestall:{clan_id}:{slot_index}",
        )])

    rows.append([InlineKeyboardButton(
        text="📦 Склад клана", callback_data=f"clanh:storage:{clan_id}")])
    rows.append([InlineKeyboardButton(
        text="🔙 Внутрь здания", callback_data=f"clanh:inside:{clan_id}")])
    photo = await resolve_clan_hall_photo(building)
    await _paint(cb, text, InlineKeyboardMarkup(inline_keyboard=rows), photo=photo)


@router.callback_query(F.data.startswith("clanh:expmanage:"))
async def clan_hall_expmanage_cb(cb: CallbackQuery):
    clan_id = int(cb.data.split(":")[2])
    clan = await _member_clan(cb, clan_id)
    if not clan:
        return
    building = await _resolve_hall_for_expansions(cb, clan_id, clan)
    await cb.answer()
    await _render_expansions(cb, clan, building)


@router.callback_query(F.data.startswith("clanh:expchoose:"))
async def clan_hall_expchoose_cb(cb: CallbackQuery):
    parts = cb.data.split(":")
    clan_id = int(parts[2])
    slot_index = int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else 0
    clan = await _member_clan(cb, clan_id)
    if not clan:
        return
    building = await _resolve_hall_for_expansions(cb, clan_id, clan)
    await cb.answer()
    await _render_expansion_choose(cb, clan, building, slot_index)


@router.callback_query(F.data.startswith("clanh:expinstall:"))
async def clan_hall_expinstall_cb(cb: CallbackQuery):
    parts = cb.data.split(":")
    clan_id = int(parts[2])
    slot_index = int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else 0
    expansion_type = parts[4] if len(parts) > 4 else ""
    clan = await _member_clan(cb, clan_id)
    if not clan:
        return
    ok, msg = await install_clan_expansion(clan_id, cb.from_user.id,
                                           slot_index, expansion_type)
    await cb.answer(msg, show_alert=True)
    building = await get_clan_building(clan_id)
    if not building:
        return
    await _render_expansions(cb, clan, building)


@router.callback_query(F.data.startswith("clanh:expup:"))
async def clan_hall_expup_cb(cb: CallbackQuery):
    parts = cb.data.split(":")
    clan_id = int(parts[2])
    slot_index = int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else 0
    clan = await _member_clan(cb, clan_id)
    if not clan:
        return
    ok, msg = await upgrade_clan_expansion(clan_id, cb.from_user.id, slot_index)
    await cb.answer(msg, show_alert=True)
    building = await get_clan_building(clan_id)
    if not building:
        return
    await _render_expansions(cb, clan, building)


@router.callback_query(F.data.startswith("clanh:use:"))
async def clan_hall_use_cb(cb: CallbackQuery):
    """Использование установленного расширения (кухня/стол/душевые/сад)."""
    parts = cb.data.split(":")
    clan_id = int(parts[2])
    slot_index = int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else 0
    clan, building, exp = await _load_usable(cb, clan_id, slot_index)
    if not clan:
        return
    if exp["expansion_type"] not in ("kitchen", "workbench", "shower", "garden",
                                     "library", "shop"):
        await cb.answer("❌ Это расширение пока не работает.", show_alert=True)
        return
    await cb.answer()
    await _render_clan_use(cb, clan, building, exp)


@router.callback_query(F.data.startswith("clanh:recipe:"))
async def clan_hall_recipe_cb(cb: CallbackQuery):
    """Карточка личного рецепта в клановой кухне/крафтовом столе."""
    parts = cb.data.split(":")
    clan_id = int(parts[2])
    slot_index = int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else 0
    recipe_id = int(parts[4]) if len(parts) > 4 and parts[4].isdigit() else 0
    clan, building, exp = await _load_usable(cb, clan_id, slot_index)
    if not clan:
        return
    et = exp["expansion_type"]
    level = int(exp["expansion_level"] or 1)
    if et not in ("kitchen", "workbench"):
        await cb.answer("❌ Здесь нельзя готовить.", show_alert=True)
        return
    recipe = await get_recipe(recipe_id)
    if not recipe:
        await cb.answer("❌ Рецепт не найден.", show_alert=True)
        return
    if not (await has_user_recipe(cb.from_user.id, recipe_id)
            or await has_clan_recipe(clan_id, recipe_id)):
        await cb.answer("❌ Ты ещё не изучил этот рецепт.", show_alert=True)
        return
    if recipe["required_expansion"] != et:
        await cb.answer("❌ Это расширение не подходит для рецепта.", show_alert=True)
        return
    if int(recipe["required_level"] or 1) > level:
        await cb.answer("❌ Рецепт выше уровня расширения.", show_alert=True)
        return

    ingredients = parse_ingredients(recipe)
    inv_map = await get_ingredient_map(cb.from_user.id)
    ap_cost = await recipe_ap_cost(cb.from_user.id, recipe)
    time_sec = int(recipe["production_time"] or 0)
    lines = [
        f"📋 <b>{_esc(recipe['name'])}</b>",
        f"Клан «{_esc(clan['name'])}» • {clan_expansion_name(et)} ур. {level}",
        f"{_esc(recipe['description'] or '')}",
        "",
        "Ингредиенты:",
    ]
    can_craft = True
    for ing_name, qty in ingredients:
        have = inv_map.get(ing_name, 0)
        if have < qty:
            can_craft = False
        mark = "✅" if have >= qty else "❌"
        lines.append(f"  {mark} {_esc(ing_name)}: {have}/{qty}")
    lines.append("")
    lines.append(f"ОД: <b>{ap_cost}</b> • Время: ~{time_sec} сек")
    lines.append("Крафт личный: ингредиенты и ОД — твои, результат — тебе.")

    rows = []
    if can_craft:
        rows.append([InlineKeyboardButton(
            text=f"🏭 Готовить ({time_sec} сек)",
            callback_data=f"clanh:craft:{clan_id}:{slot_index}:{recipe_id}")])
    else:
        lines.append("\n⚠️ Не хватает ингредиентов!")
    rows.append([InlineKeyboardButton(
        text="🔙 К рецептам", callback_data=f"clanh:use:{clan_id}:{slot_index}")])
    rows.append([InlineKeyboardButton(
        text="🚪 Внутрь здания", callback_data=f"clanh:inside:{clan_id}")])

    await cb.answer()
    photo = await resolve_clan_hall_photo(building)
    await _paint(cb, "\n".join(lines), InlineKeyboardMarkup(inline_keyboard=rows), photo=photo)


@router.callback_query(F.data.startswith("clanh:craft:"))
async def clan_hall_craft_cb(cb: CallbackQuery):
    """Личный крафт в клан-холле: общий лок CRAFTING, личные ОД/сырьё/результат."""
    parts = cb.data.split(":")
    clan_id = int(parts[2])
    slot_index = int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else 0
    recipe_id = int(parts[4]) if len(parts) > 4 and parts[4].isdigit() else 0
    clan, building, exp = await _load_usable(cb, clan_id, slot_index)
    if not clan:
        return
    et = exp["expansion_type"]
    if et not in ("kitchen", "workbench"):
        await cb.answer("❌ Здесь нельзя готовить.", show_alert=True)
        return

    uid = cb.from_user.id
    try:
        ctx = await begin_craft(uid, recipe_id, et, int(exp["expansion_level"] or 1),
                                clan_id=clan_id)
    except CraftError as e:
        await cb.answer(str(e), show_alert=True)
        return

    recipe = ctx["recipe"]
    ap_cost = ctx["ap_cost"]
    try:
        await cb.answer("🏭 Начал готовить!")
        photo = await resolve_clan_hall_photo(building)
        await animate_craft(cb.bot, cb.message.chat.id, recipe,
                            photo=photo, noop_data="clanh:noop")
        try:
            outcome = await finish_craft(uid, ctx)
        except CraftError as e:
            await cb.bot.send_message(cb.message.chat.id, str(e))
            return
        # Результат уже выдан — при сбое отправки сообщения сырьё не возвращаем.
        ctx["consumed"] = []

        lines = [f"✅ <b>{_esc(outcome['name'])}</b> готово!",
                 f"Количество: ×{outcome['qty']}"]
        if outcome["expires_at"]:
            lines.append("⏳ Срок годности: 6 дней")
        lines.append("\nДобавлено в твой инвентарь.")

        if outcome["can_repeat"]:
            inv_map = await get_ingredient_map(uid)
            lines.append("\n🔄 <b>Можно приготовить ещё:</b>")
            for ing_name, qty in ctx["ingredients"]:
                have = inv_map.get(ing_name, 0)
                lines.append(f"• {_esc(ing_name)}: {have}/{qty}")

        rows = []
        if outcome["can_repeat"]:
            rows.append([InlineKeyboardButton(
                text=f"🔄 Готовить ещё ({ap_cost} ОД)",
                callback_data=f"clanh:craft:{clan_id}:{slot_index}:{recipe_id}")])
        rows.append([InlineKeyboardButton(
            text="📋 К рецептам", callback_data=f"clanh:use:{clan_id}:{slot_index}")])
        rows.append([InlineKeyboardButton(
            text="🚪 Внутрь здания", callback_data=f"clanh:inside:{clan_id}")])
        await cb.bot.send_message(cb.message.chat.id, "\n".join(lines),
                                  parse_mode="HTML",
                                  reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))
    except Exception:
        await cancel_craft(uid, ctx)
        raise
    finally:
        end_craft(uid)


async def _render_clan_mushrooms(cb: CallbackQuery, clan, building, exp,
                                 notice: str = ""):
    """Экран переработки сырых грибов в клановой кухне (без рецепта)."""
    clan_id = int(clan["id"])
    slot_index = int(exp["slot_index"])
    level = int(exp["expansion_level"] or 1)
    uid = cb.from_user.id
    user = await get_user(uid) or {}
    ap = int(user.get("ap") or 0)
    ap_max = int(user.get("ap_max") or ap)
    mushrooms = await get_user_raw_mushrooms(uid)

    lines = [
        f"🍄 <b>Переработка грибов</b> — Кухня (ур. {level}) — «{_esc(clan['name'])}»",
        "",
    ]
    if notice:
        lines.append(notice)
        lines.append("")
    lines.append(
        f"Рецепт не нужен. Стоимость: <b>{MUSHROOM_PROCESS_AP_COST} ОД</b> за 1 гриб.\n"
        f"• Съедобные → «{_esc(MUSHROOM_HEAL_POWDER_NAME)}» "
        f"(из Гиропора и Ежовика редко выпадает «{_esc(MUSHROOM_ESSENCE_NAME)}»).\n"
        f"• Ядовитые → «{_esc(MUSHROOM_POISON_POWDER_NAME)}».\n"
        f"⚡ Твои ОД: <b>{ap}/{ap_max}</b>"
    )
    rows = []
    if not mushrooms:
        lines.append("\nУ тебя нет сырых грибов для переработки.")
    else:
        lines.append("\nТвои сырые грибы:")
        for m in mushrooms:
            spec = m["spec"]
            ess = f", эссенция {spec['essence_chance']}%" if spec.get("essence_chance") else ""
            icon = "☠" if m["kind"] == "toxic" else "🍄"
            qty = int(m["quantity"])
            lines.append(
                f"  • {icon} {_esc(m['name'])} ×{qty} → "
                f"{spec['min']}–{spec['max']} порошка{ess}"
            )
            iid = int(m["item_id"])
            btn_one = InlineKeyboardButton(
                text=f"{icon} {m['name']}: 1 шт. ({MUSHROOM_PROCESS_AP_COST} ОД)",
                callback_data=f"clanh:mushproc:{clan_id}:{slot_index}:{iid}:1",
            )
            if qty > 1:
                all_ap = qty * MUSHROOM_PROCESS_AP_COST
                btn_all = InlineKeyboardButton(
                    text=f"Все ×{qty} ({all_ap} ОД)",
                    callback_data=f"clanh:mushproc:{clan_id}:{slot_index}:{iid}:all",
                )
                rows.append([btn_one, btn_all])
            else:
                rows.append([btn_one])

    rows.append([InlineKeyboardButton(
        text="🔙 К кухне", callback_data=f"clanh:use:{clan_id}:{slot_index}")])
    photo = await resolve_clan_hall_photo(building)
    await _paint(cb, "\n".join(lines), InlineKeyboardMarkup(inline_keyboard=rows), photo=photo)


@router.callback_query(F.data.startswith("clanh:mushrooms:"))
async def clan_hall_mushrooms_cb(cb: CallbackQuery):
    """Открыть переработку грибов на клановой кухне."""
    parts = cb.data.split(":")
    clan_id = int(parts[2])
    slot_index = int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else 0
    clan, building, exp = await _load_usable(cb, clan_id, slot_index)
    if not clan:
        return
    if exp["expansion_type"] != "kitchen":
        await cb.answer("❌ Переработка грибов доступна только на кухне.",
                        show_alert=True)
        return
    await cb.answer()
    await _render_clan_mushrooms(cb, clan, building, exp)


@router.callback_query(F.data.startswith("clanh:mushproc:"))
async def clan_hall_mushproc_cb(cb: CallbackQuery):
    """Переработать 1 или все сырые грибы выбранного вида на клановой кухне."""
    parts = cb.data.split(":")
    clan_id = int(parts[2])
    slot_index = int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else 0
    item_id = int(parts[4]) if len(parts) > 4 and parts[4].isdigit() else 0
    mode = parts[5] if len(parts) > 5 else "1"
    clan, building, exp = await _load_usable(cb, clan_id, slot_index)
    if not clan:
        return
    if exp["expansion_type"] != "kitchen":
        await cb.answer("❌ Переработка грибов доступна только на кухне.",
                        show_alert=True)
        return
    try:
        out = await process_mushrooms(cb.from_user.id, item_id, mode=mode)
    except CraftError as e:
        await cb.answer(str(e), show_alert=True)
        return

    ess_line = (
        f"\n✨ Редкая удача! «{_esc(out['essence_name'])}» ×{out['essence_qty']}"
        if out.get("essence_qty")
        else ""
    )
    notice = (
        f"✅ Переработано: <b>{_esc(out['mushroom_name'])}</b> ×{out['processed_count']} "
        f"(−{out['ap_spent']} ОД)\n"
        f"🎒 Получено: <b>{_esc(out['powder_name'])}</b> ×{out['powder_qty']}{ess_line}"
    )
    await cb.answer("✅ Грибы переработаны!")
    await _render_clan_mushrooms(cb, clan, building, exp, notice=notice)


@router.callback_query(F.data.startswith("clanh:shower:"))
async def clan_hall_shower_cb(cb: CallbackQuery):
    """Клановые душевые: +ОД раз в сутки, кулдаун общий с жильём."""
    parts = cb.data.split(":")
    clan_id = int(parts[2])
    slot_index = int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else 0
    clan, building, exp = await _load_usable(cb, clan_id, slot_index)
    if not clan:
        return
    if exp["expansion_type"] != "shower":
        await cb.answer("❌ В этом слоте нет душевых.", show_alert=True)
        return

    level = int(exp["expansion_level"] or 1)
    outcome = await use_shower(
        cb.from_user.id, level,
        ap_by_level=getattr(config, "CLAN_SHOWER_AP_BY_LEVEL", {1: 25}),
        sober_by_level=getattr(config, "CLAN_SHOWER_SOBER_MINUTES", {1: 60}),
        reason="клановая душевая")
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
    await _render_clan_shower(cb, clan, building, exp)


@router.callback_query(F.data.startswith("clanh:plantlist:"))
async def clan_hall_plantlist_cb(cb: CallbackQuery):
    """Выбор семечка из личного инвентаря для посадки на общую грядку клана."""
    parts = cb.data.split(":")
    clan_id = int(parts[2])
    slot_index = int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else 0
    plot_index = int(parts[4]) if len(parts) > 4 and parts[4].isdigit() else 0
    clan, building, exp = await _load_usable(cb, clan_id, slot_index)
    if not clan:
        return
    if exp["expansion_type"] != "garden":
        await cb.answer("❌ В этом слоте нет сада.", show_alert=True)
        return
    level = int(exp["expansion_level"] or 1)
    max_plots = clan_garden_plots(level)
    if plot_index < 1 or plot_index > max_plots:
        await cb.answer("❌ Такой грядки в саду нет.", show_alert=True)
        return
    garden = await get_clan_garden(clan_id)
    if plot_index in garden:
        await cb.answer("❌ Грядка уже занята.", show_alert=True)
        await _render_clan_garden(cb, clan, building, exp)
        return

    inv = await get_inventory(cb.from_user.id)
    seeds = [i for i in inv if i["category"] == "seeds" and int(i["quantity"] or 0) > 0]
    lines = [
        f"🌱 <b>Посадка на грядку {plot_index}</b> — «{_esc(clan['name'])}»",
        "",
    ]
    rows = []
    if seeds:
        lines.append("Выбери семечко из личного инвентаря:")
        for s in seeds:
            rows.append([InlineKeyboardButton(
                text=f"🌱 {s['name']} ({s['quantity']} шт.)",
                callback_data=f"clanh:plant:{clan_id}:{slot_index}:{plot_index}:{s['id']}",
            )])
    else:
        lines.append("В твоём инвентаре нет семян.")
    rows.append([InlineKeyboardButton(
        text="🔙 К саду", callback_data=f"clanh:use:{clan_id}:{slot_index}")])

    await cb.answer()
    photo = await resolve_clan_hall_photo(building)
    await _paint(cb, "\n".join(lines), InlineKeyboardMarkup(inline_keyboard=rows), photo=photo)


@router.callback_query(F.data.startswith("clanh:plant:"))
async def clan_hall_plant_cb(cb: CallbackQuery):
    """Посадка семечка на грядку кланового сада (доступна любому члену клана)."""
    parts = cb.data.split(":")
    clan_id = int(parts[2])
    slot_index = int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else 0
    plot_index = int(parts[4]) if len(parts) > 4 and parts[4].isdigit() else 0
    seed_id = int(parts[5]) if len(parts) > 5 and parts[5].isdigit() else 0
    clan, building, exp = await _load_usable(cb, clan_id, slot_index)
    if not clan:
        return
    if exp["expansion_type"] != "garden":
        await cb.answer("❌ В этом слоте нет сада.", show_alert=True)
        return
    max_plots = clan_garden_plots(int(exp["expansion_level"] or 1))
    ok, msg = await plant_clan_seed(
        clan_id, cb.from_user.id, plot_index, seed_id, max_plots)
    if not ok:
        await cb.answer(f"❌ {msg}", show_alert=True)
        return
    await cb.answer(f"🌱 На грядку {plot_index} посажено: {msg}!", show_alert=True)
    await _render_clan_garden(cb, clan, building, exp)


@router.callback_query(F.data.startswith("clanh:harvest:"))
async def clan_hall_harvest_cb(cb: CallbackQuery):
    """Сбор урожая с одной грядки на склад клана (только глава клана)."""
    parts = cb.data.split(":")
    clan_id = int(parts[2])
    slot_index = int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else 0
    plot_index = int(parts[4]) if len(parts) > 4 and parts[4].isdigit() else 0
    clan, building, exp = await _load_usable(cb, clan_id, slot_index)
    if not clan:
        return
    if exp["expansion_type"] != "garden":
        await cb.answer("❌ В этом слоте нет сада.", show_alert=True)
        return
    if not await can_harvest_clan_garden(clan_id, cb.from_user.id):
        await cb.answer(
            "❌ Собирать урожай кланового сада может только глава клана.",
            show_alert=True)
        return
    max_plots = clan_garden_plots(int(exp["expansion_level"] or 1))
    if plot_index < 1 or plot_index > max_plots:
        await cb.answer("❌ Такой грядки в саду нет.", show_alert=True)
        return
    ok, res = await harvest_clan_plot(clan_id, plot_index)
    if not ok:
        await cb.answer(f"❌ {res}", show_alert=True)
        return
    await cb.answer(
        f"🍎 Собрано на склад клана: {res['name']} ×{res['qty']}!",
        show_alert=True)
    await _render_clan_garden(cb, clan, building, exp)


@router.callback_query(F.data.startswith("clanh:harvestall:"))
async def clan_hall_harvestall_cb(cb: CallbackQuery):
    """Сбор всего созревшего урожая в клановый склад (только глава клана)."""
    parts = cb.data.split(":")
    clan_id = int(parts[2])
    slot_index = int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else 0
    clan, building, exp = await _load_usable(cb, clan_id, slot_index)
    if not clan:
        return
    if exp["expansion_type"] != "garden":
        await cb.answer("❌ В этом слоте нет сада.", show_alert=True)
        return
    if not await can_harvest_clan_garden(clan_id, cb.from_user.id):
        await cb.answer(
            "❌ Собирать урожай кланового сада может только глава клана.",
            show_alert=True)
        return
    max_plots = clan_garden_plots(int(exp["expansion_level"] or 1))
    totals = {}
    for plot_idx in range(1, max_plots + 1):
        ok, res = await harvest_clan_plot(clan_id, plot_idx)
        if ok:
            totals[res["name"]] = totals.get(res["name"], 0) + int(res["qty"])
    if not totals:
        await cb.answer("❌ Спелых плодов для сбора пока нет.", show_alert=True)
        return
    summary = ", ".join(f"{name} ×{qty}" for name, qty in totals.items())
    await cb.answer(f"🧺 Собрано на склад клана: {summary}!", show_alert=True)
    await _render_clan_garden(cb, clan, building, exp)


@router.callback_query(F.data.startswith("clanh:hall:"))
async def clan_hall_cb(cb: CallbackQuery):
    await cb.answer()
    clan_id = int(cb.data.split(":")[2])
    clan = await _member_clan(cb, clan_id)
    if not clan:
        return
    building, event = await resolve_clan_building_with_event(clan_id)
    if event in ("built", "upgraded"):
        bname = _building_cfg(building["building_type"]).get("name") or building["building_type"]
        if event == "built":
            msg = (f"🎉 <b>Строительство завершено!</b>\n"
                   f"Здание клана «{_esc(clan['name'])}» — <b>{_esc(bname)}</b> — построено и открыто!")
        else:
            msg = (f"🎉 <b>Улучшение завершено!</b>\n"
                   f"Здание клана «{_esc(clan['name'])}» улучшено до «<b>{_esc(bname)}</b>»!")
        await notify_clan_members(getattr(cb, "bot", None), clan_id, msg)
    await _render_hall(cb, clan, building)


@router.callback_query(F.data.startswith("clanh:choose:"))
async def clan_hall_choose_cb(cb: CallbackQuery):
    parts = cb.data.split(":")
    clan_id = int(parts[2])
    btype = parts[3] if len(parts) > 3 else ""
    clan = await _member_clan(cb, clan_id)
    if not clan:
        return
    ok, msg = await choose_clan_building(clan_id, cb.from_user.id, btype)
    await cb.answer(msg, show_alert=True)
    if not ok:
        return
    building = await ensure_clan_building(clan_id)
    await _render_hall(cb, clan, building)


@router.callback_query(F.data.startswith("clanh:upgrade:"))
async def clan_hall_upgrade_cb(cb: CallbackQuery):
    """Выбор улучшения построенного здания до следующего уровня."""
    clan_id = int(cb.data.split(":")[2])
    clan = await _member_clan(cb, clan_id)
    if not clan:
        return
    ok, msg = await choose_clan_upgrade(clan_id, cb.from_user.id)
    await cb.answer(msg, show_alert=True)
    if not ok:
        return
    building = await ensure_clan_building(clan_id)
    await _render_hall(cb, clan, building)


@router.callback_query(F.data.startswith("clanh:cancel:"))
async def clan_hall_cancel_cb(cb: CallbackQuery):
    clan_id = int(cb.data.split(":")[2])
    clan = await _member_clan(cb, clan_id)
    if not clan:
        return
    ok, msg = await cancel_clan_building(clan_id, cb.from_user.id)
    await cb.answer(msg, show_alert=True)
    if not ok:
        return
    building = await ensure_clan_building(clan_id)
    await _render_hall(cb, clan, building)


@router.callback_query(F.data.startswith("clanh:start:"))
async def clan_hall_start_cb(cb: CallbackQuery):
    clan_id = int(cb.data.split(":")[2])
    clan = await _member_clan(cb, clan_id)
    if not clan:
        return
    ok, msg, building = await start_clan_building_project(clan_id, cb.from_user.id)
    await cb.answer(msg, show_alert=True)
    if not ok or not building:
        return
    completes = str(building["completes_at"] or "")[:10]
    if building["status"] == "upgrading":
        cur_name = (_building_cfg(building["building_type"]).get("name")
                    or building["building_type"])
        tgt_name = (_building_cfg(building["target_type"]).get("name")
                    or building["target_type"])
        note = (f"⬆️ <b>Улучшение начато!</b>\n"
                f"Клан «{_esc(clan['name'])}» улучшает «<b>{_esc(cur_name)}</b>» "
                f"до «<b>{_esc(tgt_name)}</b>».\n"
                f"Завершение: <b>{completes}</b>.")
    else:
        bname = _building_cfg(building["building_type"]).get("name") or building["building_type"]
        note = (f"🏗 <b>Стройка начата!</b>\n"
                f"Клан «{_esc(clan['name'])}» начал возведение здания «<b>{_esc(bname)}</b>».\n"
                f"Завершение: <b>{completes}</b>.")
    await notify_clan_members(getattr(cb, "bot", None), clan_id, note)
    await _render_hall(cb, clan, building)


@router.callback_query(F.data.startswith("clanh:startfull:"))
async def clan_hall_startfull_cb(cb: CallbackQuery):
    """Старт стройки без сбора ресурсов: глава платит двойную цену."""
    clan_id = int(cb.data.split(":")[2])
    clan = await _member_clan(cb, clan_id)
    if not clan:
        return
    ok, msg, building = await start_clan_building_project(
        clan_id, cb.from_user.id, skip_resources=True)
    await cb.answer(msg, show_alert=True)
    if not ok or not building:
        return
    completes = str(building["completes_at"] or "")[:10]
    if building["status"] == "upgrading":
        cur_name = (_building_cfg(building["building_type"]).get("name")
                    or building["building_type"])
        tgt_name = (_building_cfg(building["target_type"]).get("name")
                    or building["target_type"])
        note = (f"⬆️ <b>Улучшение начато без сбора ресурсов!</b>\n"
                f"Клан «{_esc(clan['name'])}» улучшает «<b>{_esc(cur_name)}</b>» "
                f"до «<b>{_esc(tgt_name)}</b>».\n"
                f"Глава оплатил двойную цену, склад клана не тронут.\n"
                f"Завершение: <b>{completes}</b>.")
    else:
        bname = _building_cfg(building["building_type"]).get("name") or building["building_type"]
        note = (f"🏗 <b>Стройка начата без сбора ресурсов!</b>\n"
                f"Клан «{_esc(clan['name'])}» начал возведение здания «<b>{_esc(bname)}</b>».\n"
                f"Глава оплатил двойную цену, склад клана не тронут.\n"
                f"Завершение: <b>{completes}</b>.")
    await notify_clan_members(getattr(cb, "bot", None), clan_id, note)
    await _render_hall(cb, clan, building)


@router.callback_query(F.data.startswith("clanh:inside:"))
async def clan_hall_inside_cb(cb: CallbackQuery):
    clan_id = int(cb.data.split(":")[2])
    clan = await _member_clan(cb, clan_id)
    if not clan:
        return
    building, event = await resolve_clan_building_with_event(clan_id)
    if event in ("built", "upgraded"):
        bname = _building_cfg(building["building_type"]).get("name") or building["building_type"]
        if event == "upgraded":
            note = (f"🎉 <b>Улучшение завершено!</b>\n"
                    f"Здание клана «{_esc(clan['name'])}» улучшено до "
                    f"«<b>{_esc(bname)}</b>» и открыто!")
        else:
            note = (f"🎉 <b>Строительство завершено!</b>\n"
                    f"Здание клана «{_esc(clan['name'])}» — <b>{_esc(bname)}</b> — открыто!")
        await notify_clan_members(getattr(cb, "bot", None), clan_id, note)
    if not building or building["status"] not in ("built", "upgrading"):
        await cb.answer("❌ Здание клана ещё не построено.", show_alert=True)
        return
    await cb.answer()
    photo = await resolve_clan_hall_photo(building)
    expansions = await get_clan_expansions(clan_id)
    rows = []
    for exp in expansions:
        et = exp["expansion_type"]
        if et not in ("kitchen", "workbench", "shower", "garden", "library", "shop"):
            continue
        slot_index = int(exp["slot_index"])
        level = int(exp["expansion_level"] or 1)
        action = {"kitchen": "готовить", "workbench": "крафтить",
                  "shower": "помыться", "garden": "грядки",
                  "library": "читать", "shop": "покупать"}.get(et, "открыть")
        rows.append([InlineKeyboardButton(
            text=f"{clan_expansion_icon(et)} {clan_expansion_name(et)} "
                 f"(ур. {level}) — {action}",
            callback_data=f"clanh:use:{clan_id}:{slot_index}",
        )])
    if (building["status"] == "built"
            and await can_manage_clan_hall(clan_id, cb.from_user.id)):
        rows.append([InlineKeyboardButton(
            text="⚙️ Управление расширениями",
            callback_data=f"clanh:expmanage:{clan_id}",
        )])
    rows.append([InlineKeyboardButton(text="📦 Склад клана",
                                      callback_data=f"clanh:storage:{clan_id}")])
    rows.append([InlineKeyboardButton(text="➕ Внести ресурсы",
                                      callback_data=f"clanh:donate:{clan_id}")])
    rows.append([InlineKeyboardButton(text="🔙 К фасаду здания",
                                      callback_data=f"clanh:hall:{clan_id}")])
    rows.append([InlineKeyboardButton(text="🔙 К клану",
                                      callback_data=f"clans:view:{clan_id}")])
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    await _paint(cb, build_hall_inside_text(clan, building, expansions), kb, photo=photo)


# ── Админская установка индивидуальной картинки здания и заглушки стройки ─────

@router.callback_query(F.data.startswith("clanh:admphoto:"))
async def clan_hall_admphoto_cb(cb: CallbackQuery, state: FSMContext):
    if not await has_permission(cb.from_user.id, "can_manage_clans"):
        await cb.answer("❌ Недостаточно прав.", show_alert=True)
        return
    await cb.answer()
    clan_id = int(cb.data.split(":")[2])
    clan = await get_clan(clan_id)
    if not clan:
        return
    await state.update_data(clanh_photo_clan_id=clan_id)
    await state.set_state(ClanHallAdminPhoto.wait_building_photo)
    await cb.message.answer(
        f"🖼 Пришли фото готового здания для клана «{_esc(clan['name'])}»:",
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("clanh:admnophoto:"))
async def clan_hall_admnophoto_cb(cb: CallbackQuery):
    if not await has_permission(cb.from_user.id, "can_manage_clans"):
        await cb.answer("❌ Недостаточно прав.", show_alert=True)
        return
    clan_id = int(cb.data.split(":")[2])
    await set_clan_building_photo(clan_id, None)
    await cb.answer("✅ Индивидуальное фото здания убрано.", show_alert=True)
    clan = await get_clan(clan_id)
    if clan and await is_clan_member(clan_id, cb.from_user.id):
        building = await ensure_clan_building(clan_id)
        await _render_hall(cb, clan, building)


@router.callback_query(F.data.startswith("clanh:admconstphoto:"))
async def clan_hall_admconstphoto_cb(cb: CallbackQuery, state: FSMContext):
    if not await has_permission(cb.from_user.id, "can_manage_clans"):
        await cb.answer("❌ Недостаточно прав.", show_alert=True)
        return
    await cb.answer()
    clan_id = int(cb.data.split(":")[2])
    await state.update_data(clanh_photo_clan_id=clan_id)
    await state.set_state(ClanHallAdminPhoto.wait_construction_photo)
    await cb.message.answer(
        "🏗 Пришли общую картинку-заглушку с видом на стройку (для всех строящихся зданий кланов):"
    )


@router.message(ClanHallAdminPhoto.wait_building_photo, F.photo)
async def clan_hall_admphoto_save(message: Message, state: FSMContext):
    if not await has_permission(message.from_user.id, "can_manage_clans"):
        await state.clear()
        return
    data = await state.get_data()
    clan_id = int(data.get("clanh_photo_clan_id") or 0)
    clan = await get_clan(clan_id)
    if not clan:
        await state.clear()
        await message.answer("❌ Клан не найден.")
        return
    file_id = message.photo[-1].file_id
    await set_clan_building_photo(clan_id, file_id)
    await state.clear()
    await message.answer(f"✅ Индивидуальное фото здания клана «{clan['name']}» сохранено.")


@router.message(ClanHallAdminPhoto.wait_construction_photo, F.photo)
async def clan_hall_admconstphoto_save(message: Message, state: FSMContext):
    if not await has_permission(message.from_user.id, "can_manage_clans"):
        await state.clear()
        return
    file_id = message.photo[-1].file_id
    await set_clan_construction_photo(file_id)
    await state.clear()
    await message.answer("✅ Общая картинка-заглушка стройки кланового здания сохранена.")


# ── Экраны кланового склада ───────────────────────────────────────────────────

@router.callback_query(F.data.startswith("clanh:storage:"))
async def clan_storage_cb(cb: CallbackQuery):
    await cb.answer()
    clan_id = int(cb.data.split(":")[2])
    clan = await _member_clan(cb, clan_id)
    if not clan:
        return
    rows = await get_clan_storage(clan_id)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Внести ресурсы",
                              callback_data=f"clanh:donate:{clan_id}")],
        [InlineKeyboardButton(text="🧾 Вклады",
                              callback_data=f"clanh:log:{clan_id}")],
        [InlineKeyboardButton(text="🏰 Здание клана",
                              callback_data=f"clanh:hall:{clan_id}")],
        [InlineKeyboardButton(text="🔙 К клану",
                              callback_data=f"clans:view:{clan_id}")],
    ])
    await _paint(cb, build_clan_storage_text(clan, rows), kb)


@router.callback_query(F.data.startswith("clanh:donate:"))
async def clan_donate_cb(cb: CallbackQuery):
    await cb.answer()
    clan_id = int(cb.data.split(":")[2])
    clan = await _member_clan(cb, clan_id)
    if not clan:
        return
    inv = await get_inventory(cb.from_user.id)
    items = [i for i in inv if i["category"] == "resource" and (i["quantity"] or 0) > 0]
    rows = []
    for it in items[:STORAGE_PAGE]:
        rows.append([InlineKeyboardButton(
            text=f"{it['name']} · {it['quantity']} шт.",
            callback_data=f"clanh:item:{clan_id}:{it['id']}")])
    if len(items) > STORAGE_PAGE:
        rows.append([InlineKeyboardButton(
            text=f"… и ещё {len(items) - STORAGE_PAGE}",
            callback_data="clanh:noop")])
    rows.append([InlineKeyboardButton(text="🏰 К зданию клана",
                                      callback_data=f"clanh:hall:{clan_id}")])
    rows.append([InlineKeyboardButton(text="🔙 К складу",
                                      callback_data=f"clanh:storage:{clan_id}")])
    await _paint(cb, build_donate_text(clan, items),
                 InlineKeyboardMarkup(inline_keyboard=rows))


@router.callback_query(F.data.startswith("clanh:item:"))
async def clan_donate_item_cb(cb: CallbackQuery):
    await cb.answer()
    _, _, clan_id_s, item_id_s = cb.data.split(":")
    clan_id, item_id = int(clan_id_s), int(item_id_s)
    clan = await _member_clan(cb, clan_id)
    if not clan:
        return
    item = await get_item(item_id)
    if not item or item["category"] != "resource":
        await cb.answer("❌ Это не ресурс.", show_alert=True)
        return
    inv = await get_inventory_item(cb.from_user.id, item_id)
    have = inv["quantity"] if inv else 0
    stored = await get_clan_storage_qty(clan_id, item_id)
    rows = []
    if have > 0:
        btns = [InlineKeyboardButton(text="+1",
                                     callback_data=f"clanh:give:{clan_id}:{item_id}:1")]
        if have >= 10:
            btns.append(InlineKeyboardButton(
                text="+10", callback_data=f"clanh:give:{clan_id}:{item_id}:10"))
        btns.append(InlineKeyboardButton(
            text=f"Всё ({have})", callback_data=f"clanh:give:{clan_id}:{item_id}:all"))
        rows.append(btns)
    rows.append([InlineKeyboardButton(text="🔙 К выбору ресурса",
                                      callback_data=f"clanh:donate:{clan_id}")])
    await _paint(cb, build_donate_item_text(item, have, stored),
                 InlineKeyboardMarkup(inline_keyboard=rows))


@router.callback_query(F.data.startswith("clanh:give:"))
async def clan_donate_give_cb(cb: CallbackQuery):
    _, _, clan_id_s, item_id_s, amount = cb.data.split(":")
    clan_id, item_id = int(clan_id_s), int(item_id_s)
    clan = await _member_clan(cb, clan_id)
    if not clan:
        return
    item = await get_item(item_id)
    if not item or item["category"] != "resource":
        await cb.answer("❌ Это не ресурс.", show_alert=True)
        return
    inv = await get_inventory_item(cb.from_user.id, item_id)
    have = inv["quantity"] if inv else 0
    qty = have if amount == "all" else int(amount)
    if qty <= 0 or qty > have:
        await cb.answer("❌ Недостаточно ресурсов.", show_alert=True)
        return
    if not await donate_to_clan_storage(clan_id, cb.from_user.id, item_id, qty):
        await cb.answer("❌ Не удалось внести ресурс.", show_alert=True)
        return
    await cb.answer(f"✅ Внесено: {item['name']} × {qty}", show_alert=True)

    inv = await get_inventory_item(cb.from_user.id, item_id)
    have = inv["quantity"] if inv else 0
    stored = await get_clan_storage_qty(clan_id, item_id)
    if have <= 0:
        inv_all = await get_inventory(cb.from_user.id)
        items = [i for i in inv_all
                 if i["category"] == "resource" and (i["quantity"] or 0) > 0]
        rows = []
        for it in items[:STORAGE_PAGE]:
            rows.append([InlineKeyboardButton(
                text=f"{it['name']} · {it['quantity']} шт.",
                callback_data=f"clanh:item:{clan_id}:{it['id']}")])
        rows.append([InlineKeyboardButton(text="🏰 К зданию клана",
                                          callback_data=f"clanh:hall:{clan_id}")])
        rows.append([InlineKeyboardButton(text="🔙 К складу",
                                          callback_data=f"clanh:storage:{clan_id}")])
        await _paint(cb, build_donate_text(clan, items),
                     InlineKeyboardMarkup(inline_keyboard=rows))
        return

    rows = [[
        InlineKeyboardButton(text="+1",
                             callback_data=f"clanh:give:{clan_id}:{item_id}:1"),
    ]]
    btns = rows[0]
    if have >= 10:
        btns.append(InlineKeyboardButton(
            text="+10", callback_data=f"clanh:give:{clan_id}:{item_id}:10"))
    btns.append(InlineKeyboardButton(
        text=f"Всё ({have})", callback_data=f"clanh:give:{clan_id}:{item_id}:all"))
    rows.append([InlineKeyboardButton(text="🔙 К выбору ресурса",
                                      callback_data=f"clanh:donate:{clan_id}")])
    await _paint(cb, build_donate_item_text(item, have, stored),
                 InlineKeyboardMarkup(inline_keyboard=rows))


@router.callback_query(F.data.startswith("clanh:log:"))
async def clan_contrib_cb(cb: CallbackQuery):
    await cb.answer()
    clan_id = int(cb.data.split(":")[2])
    clan = await _member_clan(cb, clan_id)
    if not clan:
        return
    rows = await get_clan_contributions(clan_id, limit=20)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 К складу",
                              callback_data=f"clanh:storage:{clan_id}")],
    ])
    await _paint(cb, build_contrib_text(clan, rows), kb)


@router.callback_query(F.data == "clanh:noop")
async def clan_hall_noop(cb: CallbackQuery):
    await cb.answer()
