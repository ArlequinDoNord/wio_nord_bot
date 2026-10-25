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
    can_manage_clan_hall,
    cancel_clan_building,
    choose_clan_building,
    donate_to_clan_storage,
    ensure_clan_building,
    get_clan,
    get_clan_building,
    get_clan_construction_photo,
    get_clan_contributions,
    get_clan_members,
    get_clan_project_progress,
    get_clan_storage,
    get_clan_storage_qty,
    get_inventory,
    get_inventory_item,
    get_item,
    get_user,
    is_clan_member,
    resolve_clan_building_with_event,
    set_clan_building_photo,
    set_clan_construction_photo,
    start_clan_building_project,
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
    btype = building_row["building_type"]
    cfg = _building_cfg(btype)
    bname = cfg.get("name") or btype or "Здание клана"
    slots = cfg.get("slots", 0)
    max_lvl = cfg.get("max_level", 1)
    days = cfg.get("days", 2)
    price_nm = int(building_row["price_nm"] or cfg.get("price_nm") or 0)
    mult = int(getattr(config, "CLAN_BUILDING_NO_RESOURCES_MULT", 2) or 2)
    nores_price = price_nm * mult

    lines = [
        f"🏗 <b>Проект: {_esc(bname)}</b> — «{_esc(clan['name'])}»",
        f"Этап: <b>Сбор ресурсов</b> (срок постройки: {days} дн., слотов: {slots}, макс. ур.: {max_lvl})",
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
        lines.append("\n✅ Все ресурсы собраны! Глава клана может запустить стройку.")
    else:
        lines.append(
            "\nВносите ресурсы на склад клана — или глава может оплатить "
            f"двойную цену ({nores_price} НМ) и начать стройку сразу без ресурсов."
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


def build_hall_inside_text(clan, building_row) -> str:
    btype = building_row["building_type"]
    cfg = _building_cfg(btype)
    bname = cfg.get("name") or btype or "Здание клана"
    slots = int(cfg.get("slots") or 0)
    max_lvl = int(cfg.get("max_level") or 1)
    lines = [
        f"🚪 <b>Внутри: {_esc(bname)}</b> — «{_esc(clan['name'])}»",
        f"Слоты расширений ({slots} шт., макс. ур. {max_lvl}):",
        "",
    ]
    for idx in range(1, slots + 1):
        if btype == "castle" and idx == 7:
            lines.append(f"  {idx}. 🔒 <i>Резервный слот</i>")
        else:
            lines.append(f"  {idx}. ▫️ <i>Пустой слот</i>")
    lines.append("\n📦 Клановый склад и взносы доступны всем членам клана.")
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

    if status == "funding":
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
            if all_ok:
                rows.append([InlineKeyboardButton(
                    text=f"🚀 Начать строительство ({price_nm} НМ)",
                    callback_data=f"clanh:start:{clan_id}",
                )])
            rows.append([InlineKeyboardButton(
                text=f"💰 Начать без ресурсов ({price_nm * mult} НМ)",
                callback_data=f"clanh:startfull:{clan_id}",
            )])
            rows.append([InlineKeyboardButton(
                text="↩️ Сменить / отменить проект",
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
    rows = [
        [InlineKeyboardButton(text="🚪 Войти в здание",
                              callback_data=f"clanh:inside:{clan_id}")],
        [InlineKeyboardButton(text="📦 Склад клана",
                              callback_data=f"clanh:storage:{clan_id}")],
    ]
    if is_admin:
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
    bname = _building_cfg(building["building_type"]).get("name") or building["building_type"]
    completes = str(building["completes_at"] or "")[:10]
    await notify_clan_members(
        getattr(cb, "bot", None),
        clan_id,
        f"🏗 <b>Стройка начата!</b>\n"
        f"Клан «{_esc(clan['name'])}» начал возведение здания «<b>{_esc(bname)}</b>».\n"
        f"Завершение: <b>{completes}</b>.",
    )
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
    bname = _building_cfg(building["building_type"]).get("name") or building["building_type"]
    completes = str(building["completes_at"] or "")[:10]
    await notify_clan_members(
        getattr(cb, "bot", None),
        clan_id,
        f"🏗 <b>Стройка начата без сбора ресурсов!</b>\n"
        f"Клан «{_esc(clan['name'])}» начал возведение здания «<b>{_esc(bname)}</b>».\n"
        f"Глава оплатил двойную цену, склад клана не тронут.\n"
        f"Завершение: <b>{completes}</b>.",
    )
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
        await notify_clan_members(
            getattr(cb, "bot", None),
            clan_id,
            f"🎉 <b>Строительство завершено!</b>\n"
            f"Здание клана «{_esc(clan['name'])}» — <b>{_esc(bname)}</b> — открыто!",
        )
    if not building or building["status"] not in ("built", "upgrading"):
        await cb.answer("❌ Здание клана ещё не построено.", show_alert=True)
        return
    await cb.answer()
    photo = await resolve_clan_hall_photo(building)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📦 Склад клана",
                              callback_data=f"clanh:storage:{clan_id}")],
        [InlineKeyboardButton(text="➕ Внести ресурсы",
                              callback_data=f"clanh:donate:{clan_id}")],
        [InlineKeyboardButton(text="🔙 К фасаду здания",
                              callback_data=f"clanh:hall:{clan_id}")],
        [InlineKeyboardButton(text="🔙 К клану",
                              callback_data=f"clans:view:{clan_id}")],
    ])
    await _paint(cb, build_hall_inside_text(clan, building), kb, photo=photo)


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
