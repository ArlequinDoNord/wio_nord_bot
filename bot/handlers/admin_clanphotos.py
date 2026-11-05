"""Админ-менеджер картинок клан-холла (Фаза 8).

Вход — из админ-панели (кнопка «🖼 Картинки клан-холла», право can_manage_clans).

Что умеет:
- 🧩 картинки расширений: глобальные (на все кланы) фото для каждого из 6 типов
  (кухня, крафтовый стол, душевые, сад, библиотека, лавка) — settings
  `clanh_exp_photo_<type>`;
- 🏢 картинки зданий по кланам: индивидуальное фото «какое будет после
  постройки» (clan_buildings.building_photo_file_id) — можно ставить и пока
  здание ещё строится/собирается, показано будет после built;
- 🚧 заглушка стройки: общая картинка, показываемая во время стройки/апгрейда
  (settings `clan_construction_photo`).

Загрузка: отправляешь фото в состояние; «-» — убрать картинку. Не игроки не
видят: только can_manage_clans, и клан-холл остаётся закрытым флагом.
"""

import html

import config

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from database.db import (
    clan_expansion_icon,
    clan_expansion_name,
    get_all_clan_buildings,
    get_clan,
    get_clan_building,
    get_clan_construction_photo,
    get_clan_expansion_photo,
    set_clan_building_photo,
    set_clan_construction_photo,
    set_clan_expansion_photo,
    update_clan_building_photos,
)
from utils.permissions import has_permission
from keyboards.keyboards import cancel_keyboard

router = Router()

PER_PAGE = 8


def _esc(text) -> str:
    return html.escape(str(text or ""))


class ClanPhotosAdmin(StatesGroup):
    wait_exp_photo = State()
    wait_building_photo = State()
    wait_construction_photo = State()


async def _require(cb_or_msg) -> bool:
    uid = getattr(cb_or_msg, "from_user", None)
    uid = uid.id if uid else cb_or_msg.from_user.id
    return await has_permission(uid, "can_manage_clans")


def _mark(ok: bool) -> str:
    return "✅" if ok else "▫️"


async def _menu_screen(source) -> None:
    """Главный экран менеджера картинок; source — CallbackQuery или Message."""
    expansion_types = tuple(getattr(config, "CLAN_EXPANSION_TYPES", ()))
    construction = await get_clan_construction_photo()
    lines = ["🖼 <b>Картинки клан-холла</b>", ""]
    rows = []

    n = 0
    for et in expansion_types:
        has = bool(await get_clan_expansion_photo(et))
        n += int(has)
        lines.append(f"{_mark(has)} {clan_expansion_icon(et)} {clan_expansion_name(et)}")
        rows.append([InlineKeyboardButton(
            text=f"{_mark(has)} {clan_expansion_icon(et)} {clan_expansion_name(et)}",
            callback_data=f"clanhph:exp:{et}")])
    lines.append("")
    lines.append(f"🚧 Заглушка стройки: {_mark(bool(construction))}")
    rows.append([InlineKeyboardButton(
        text=f"{_mark(bool(construction))} 🚧 Заглушка стройки",
        callback_data="clanhph:construction")])
    lines.append("")
    lines.append("🏢 Отдельные картинки зданий кланов — по кланам:")
    rows.append([InlineKeyboardButton(
        text="🏢 Картинки зданий кланов",
        callback_data="clanhph:buildings")])
    rows.append([InlineKeyboardButton(text="🔙 В админ-панель", callback_data="admin:menu")])
    text = _esc("\n".join(lines))
    if hasattr(source, "message") and getattr(source, "message", None) is not None:
        try:
            await source.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows),
                                           parse_mode="HTML")
            return
        except Exception:
            pass
    if hasattr(source, "message"):
        await source.message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows),
                                    parse_mode="HTML")
    else:
        await source.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows),
                            parse_mode="HTML")


@router.callback_query(F.data == "clanhph:menu")
async def clanph_menu_cb(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    if not await _require(cb):
        return
    await state.clear()
    await _menu_screen(cb)


@router.callback_query(F.data.startswith("clanhph:exp:"))
async def clanph_exp_cb(cb: CallbackQuery, state: FSMContext):
    """Запрос фото расширения (глобально на тип)."""
    await cb.answer()
    if not await _require(cb):
        return
    et = cb.data.split(":")[2]
    if et not in getattr(config, "CLAN_EXPANSION_TYPES", ()):
        await cb.message.answer("❌ Неизвестное расширение.")
        return
    await state.update_data(clanhph_exp=et)
    await state.set_state(ClanPhotosAdmin.wait_exp_photo)
    cur = await get_clan_expansion_photo(et)
    await cb.message.answer(
        f"🖼 Картинка «{clan_expansion_name(et)}»"
        f"{clan_expansion_icon(et)}\n"
        f"Сейчас: {'есть' if cur else 'нет'}.\n\n"
        f"Отправь фото — оно станет картинкой этого расширения во всех кланах.\n"
        f"«-» — убрать картинку.",
        reply_markup=cancel_keyboard())


@router.message(ClanPhotosAdmin.wait_exp_photo)
async def clanph_exp_photo_save(message: Message, state: FSMContext):
    if not await _require(message):
        await state.clear()
        return
    data = await state.get_data()
    et = data.get("clanhph_exp")
    if not et:
        await state.clear()
        await message.answer("❌ Расширение не распознано. Начни заново: админ-панель → Картинки клан-холла.")
        return
    if message.photo:
        await set_clan_expansion_photo(et, message.photo[-1].file_id)
        await state.clear()
        await message.answer(
            f"✅ Картинка «{clan_expansion_name(et)}» сохранена (глобально).")
        return
    text_in = (message.text or "").strip()
    if text_in == "-":
        await set_clan_expansion_photo(et, None)
        await state.clear()
        await message.answer(f"✅ Картинка «{clan_expansion_name(et)}» удалена.")
        return
    await state.clear()
    await message.answer("❌ Нужно фото (или «-» чтобы убрать). Открой заново: админ → Картинки клан-холла.")


@router.callback_query(F.data == "clanhph:construction")
async def clanph_construction_cb(cb: CallbackQuery, state: FSMContext):
    """Запрос общей картинки-заглушки стройки."""
    await cb.answer()
    if not await _require(cb):
        return
    await state.set_state(ClanPhotosAdmin.wait_construction_photo)
    cur = await get_clan_construction_photo()
    await cb.message.answer(
        "🚧 Общая картинка-заглушка стройки кланового здания\n"
        f"Сейчас: {'есть' if cur else 'нет'}.\n\n"
        "Отправь фото — оно будет видно во время стройки/апгрейда у всех кланов.\n"
        "«-» — убрать.",
        reply_markup=cancel_keyboard())


@router.message(ClanPhotosAdmin.wait_construction_photo)
async def clanph_construction_photo_save(message: Message, state: FSMContext):
    if not await _require(message):
        await state.clear()
        return
    if message.photo:
        await set_clan_construction_photo(message.photo[-1].file_id)
        await state.clear()
        await message.answer("✅ Заглушка стройки сохранена (глобально).")
        return
    text_in = (message.text or "").strip()
    if text_in == "-":
        await set_clan_construction_photo(None)
        await state.clear()
        await message.answer("✅ Заглушка стройки удалена.")
        return
    await state.clear()
    await message.answer("❌ Нужно фото (или «-» чтобы убрать). Открой заново: админ → Картинки клан-холла.")


BUILDING_TOD_KEYS = ("dawn", "day", "sunset", "night")
BUILDING_TOD_LABELS = {
    "dawn": "🌅 Рассвет", "day": "☀️ День", "sunset": "🌇 Закат", "night": "🌙 Ночь",
}


def _building_photo_count(b) -> int:
    n = 0
    for k in BUILDING_TOD_KEYS:
        val = b.get(f"photo_{k}") if hasattr(b, "get") else (b[f"photo_{k}"] if f"photo_{k}" in b.keys() else None)
        if (val or "").strip():
            n += 1
    if not n and (b.get("building_photo_file_id") or "").strip():
        n = 1  # legacy
    return n


@router.callback_query(F.data.startswith("clanhph:buildings"))
async def clanph_buildings_cb(cb: CallbackQuery, state: FSMContext):
    """Выбор клана для индивидуальных картинок здания (4 времени суток)."""
    await cb.answer()
    if not await _require(cb):
        return
    buildings = await get_all_clan_buildings()
    lines = ["🏢 <b>Картинки зданий кланов</b>", ""]
    rows = []
    if not buildings:
        lines.append("Зданий пока нет: ни один клан не выбрал проект.")
    for b in buildings[:30]:
        status = b["status"]
        marks = {
            "built": "✅ построено",
            "building": "🏗 стройка",
            "upgrading": "⬆️ апгрейд",
            "funding": "💰 сбор",
            "choosing": "⚙️ выбор проекта",
        }.get(status, status)
        cnt = _building_photo_count(b)
        title = b.get("clan_name") or f"#{b['clan_id']}"
        lines.append(f"{_mark(cnt > 0)} «{_esc(title)}» — {marks} ({cnt}/4)")
        rows.append([InlineKeyboardButton(
            text=f"{_mark(cnt > 0)} {title} ({cnt}/4)",
            callback_data=f"clanhph:bclan:{b['clan_id']}")])
    lines.append("\nВыбери клан и загрузи 4 картинки (рассвет, день, закат, ночь).")
    rows.append([InlineKeyboardButton(text="🖼 Назад", callback_data="clanhph:menu")])
    text = "\n".join(lines)
    if hasattr(cb, "message") and getattr(cb, "message", None) is not None:
        try:
            await cb.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows),
                                       parse_mode="HTML")
            return
        except Exception:
            pass
    await cb.message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows),
                            parse_mode="HTML")


async def _render_building_slots(cb: CallbackQuery, clan_id: int) -> None:
    clan = await get_clan(clan_id)
    if not clan:
        await cb.message.answer("❌ Клан не найден.")
        return
    b = await get_clan_building(clan_id)
    lines = [
        f"🏢 <b>Картинки здания</b> — «{_esc(clan['name'])}»",
        "",
        "Загрузи картинку для каждого времени суток (видно после постройки).",
        "",
    ]
    rows = []
    for tod in BUILDING_TOD_KEYS:
        val = None
        if b:
            val = b.get(f"photo_{tod}") if hasattr(b, "get") else (b[f"photo_{tod}"] if f"photo_{tod}" in b.keys() else None)
        has = bool((val or "").strip())
        lines.append(f"{_mark(has)} {BUILDING_TOD_LABELS[tod]}")
        rows.append([InlineKeyboardButton(
            text=f"{_mark(has)} {BUILDING_TOD_LABELS[tod]}",
            callback_data=f"clanhph:bset:{clan_id}:{tod}")])
        if has:
            rows.append([InlineKeyboardButton(
                text=f"🗑 Убрать «{BUILDING_TOD_LABELS[tod]}»",
                callback_data=f"clanhph:bclr:{clan_id}:{tod}")])
    rows.append([InlineKeyboardButton(text="🔙 К списку кланов", callback_data="clanhph:buildings")])
    text = "\n".join(lines)
    try:
        await cb.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows),
                                   parse_mode="HTML")
    except Exception:
        await cb.message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows),
                                parse_mode="HTML")


@router.callback_query(F.data.startswith("clanhph:bclan:"))
async def clanph_bclan_cb(cb: CallbackQuery, state: FSMContext):
    """Экран 4 слотов картинок здания клана."""
    await cb.answer()
    if not await _require(cb):
        return
    await state.clear()
    clan_id = int(cb.data.split(":")[2])
    await _render_building_slots(cb, clan_id)


@router.callback_query(F.data.startswith("clanhph:bclr:"))
async def clanph_bclr_cb(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    if not await _require(cb):
        return
    _, _, clan_id_s, tod = cb.data.split(":")
    if tod not in BUILDING_TOD_KEYS:
        return
    await update_clan_building_photos(int(clan_id_s), {tod: None})
    await cb.answer("🗑 Убрано.", show_alert=False)
    await _render_building_slots(cb, int(clan_id_s))


@router.callback_query(F.data.startswith("clanhph:bset:"))
async def clanph_bset_cb(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    if not await _require(cb):
        return
    _, _, clan_id_s, tod = cb.data.split(":")
    if tod not in BUILDING_TOD_KEYS:
        return
    clan_id = int(clan_id_s)
    clan = await get_clan(clan_id)
    if not clan:
        await cb.message.answer("❌ Клан не найден.")
        return
    await state.update_data(clanhph_clan_id=clan_id, clanhph_btod=tod)
    await state.set_state(ClanPhotosAdmin.wait_building_photo)
    await cb.message.answer(
        f"🏢 Картинка здания «{_esc(clan['name'])}» — {BUILDING_TOD_LABELS[tod]}\n\n"
        f"Отправь фото (или «-» чтобы убрать этот слот).",
        reply_markup=cancel_keyboard())


@router.message(ClanPhotosAdmin.wait_building_photo)
async def clanph_building_photo_save(message: Message, state: FSMContext):
    if not await _require(message):
        await state.clear()
        return
    data = await state.get_data()
    clan_id = data.get("clanhph_clan_id")
    tod = data.get("clanhph_btod")
    if not clan_id:
        await state.clear()
        await message.answer("❌ Клан не распознан. Открой заново: админ → Картинки клан-холла → Картинки зданий.")
        return
    if not tod or tod not in BUILDING_TOD_KEYS:
        # legacy path fallback
        tod = "day"
    if message.photo:
        await update_clan_building_photos(int(clan_id), {tod: message.photo[-1].file_id})
        await state.clear()
        await message.answer(f"✅ Картинка ({BUILDING_TOD_LABELS[tod]}) сохранена.")
        return
    text_in = (message.text or "").strip()
    if text_in == "-":
        await update_clan_building_photos(int(clan_id), {tod: None})
        await state.clear()
        await message.answer(f"✅ Картинка ({BUILDING_TOD_LABELS[tod]}) удалена.")
        return
    await state.clear()
    await message.answer("❌ Нужно фото (или «-» чтобы убрать). Открой заново: админ → Картинки клан-холла.")
