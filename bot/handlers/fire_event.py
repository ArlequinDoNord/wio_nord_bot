"""Дни Пламенного Круговорота — праздничное событие (ТЗ — FIRE_EVENT.md).

Фаза 1 (каркас): городская кнопка «🪔 Дни Пламенного Кругворота», вход в
Огненный Лабиринт (42 НМ, до 4 заходов/сутки), сессии в `fire_lab_sessions`,
комната-развилка с тремя путями (запись шагов, скрытые паттерны появятся на
Фазе 3). Пока FIRE_LAB_ENABLED = False — все `fireevent:`-колбэки отвечают
заглушкой, кнопка города скрыта (аналог гварда клан-холла).

Остальные фазы: враги и босс (Ф2), Колодец/Древо Огня/Сундук + скрытая
геометрия (Ф3), предметы/рецепты/Лампа/достижение (Ф4), дроп и финал (Ф5).
"""

import html
import json

import config

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

import database.db as db
from database.db import (
    fire_event_active,
    get_fire_lab_entries_today,
    inc_fire_lab_entries,
    create_fire_lab_session,
    get_active_fire_lab_session,
    end_fire_lab_session,
    touch_fire_lab_session,
)
from keyboards.keyboards import main_menu_kb

router = Router()

# Пока лабиринт закрыт (FIRE_LAB_ENABLED=False), все fireevent:-хендлеры
# отвечают заглушкой (аналог гварда клан-холла).
FIRE_EVENT_CLOSED_TEXT = "🔥 Дни Пламенного Круговорота ещё готовятся — скоро откроем!"

# Пути развилки: L = налево, S = прямо, R = направо.
PATH_LABELS = {"L": "⬅️ Налево", "S": "⬆️ Прямо", "R": "➡️ Направо"}


def _esc(text) -> str:
    return html.escape(str(text or ""))


def fire_event_closed_text() -> str:
    """Текст события: закрыто флагом vs не время (вне окна дат)."""
    if not getattr(config, "FIRE_EVENT_ENABLED", False):
        return "🔥 Дни Пламенного Круговорота ещё готовятся — скоро откроем."
    return "🕯 Не время для Круговорота: праздник ещё не начался или уже отгремел."


async def fire_event_guard(handler, event, data):
    """Middleware-гвард: не пускает `fireevent:`-хендлеры при закрытом событии."""
    if db.fire_event_visible():
        return await handler(event, data)
    try:
        if isinstance(event, CallbackQuery):
            await event.answer(fire_event_closed_text(), show_alert=True)
        else:
            await event.answer(fire_event_closed_text())
    except Exception:
        pass
    return None


router.callback_query.middleware(fire_event_guard)
router.message.middleware(fire_event_guard)


def _fork_text(session) -> str:
    """Текст комнаты-развилки (шаги считаются по session.steps + 1)."""
    depth = int(session['steps'] or 0)
    head = (
        "🪔 <b>Огненный Лабиринт</b>\n"
        f"Ты на развилке №{depth + 1}. Стены полыхают тёплым светом, "
        f"коридоры уходят вглубь.\n"
        f"💙 {session['hp']}/{session['hp_max']}"
        + (" • 🌳 Благословение активно" if session['blessing'] else "")
        + "\n\nВыбери путь:"
    )
    return head


def _fork_kb(session_id: int) -> InlineKeyboardMarkup:
    rows = []
    for pth, label in PATH_LABELS.items():
        rows.append([InlineKeyboardButton(
            text=label, callback_data=f"fireevent:step:{session_id}:{pth}")])
    rows.append([InlineKeyboardButton(
        text="🚪 Покинуть лабиринт", callback_data=f"fireevent:leave:{session_id}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


@router.callback_query(F.data.startswith("fireevent:step:"))
async def fire_event_step_cb(cb: CallbackQuery):
    """Выбор пути: запись шага + броски комнаты (Фаза 2/3 добавит встречи)."""
    parts = cb.data.split(":")
    session_id, path = int(parts[2]), parts[3]
    if path not in PATH_LABELS:
        await cb.answer("❌ Нет такого пути.", show_alert=True)
        return
    session = await _session_of(cb.from_user.id, session_id)
    if not session:
        return
    history = json.loads(session['path_history'] or '[]')
    history.append(path)
    conn = await db.get_db()
    await conn.execute(
        "UPDATE fire_lab_sessions SET steps = steps + 1, path_history = ?, "
        "last_active_at = datetime('now') WHERE id = ?",
        (json.dumps(history, ensure_ascii=False), session_id))
    await conn.commit()
    updated = await _session_of(cb.from_user.id, session_id)
    if not updated:
        return
    # Выход автоматом после FIRE_LAB_ROOMS_MAX комнат (25): сессия пройдена.
    rooms_limit = int(getattr(config, "FIRE_LAB_ROOMS_MAX", 25) or 25)
    if rooms_limit > 0 and int(updated['steps']) >= rooms_limit:
        await end_fire_lab_session(session_id, 'finished')
        await cb.answer("🏁 Лабиринт пройден до конца!", show_alert=True)
        try:
            await cb.message.edit_text(
                f"🏁 <b>Ты прошёл все {rooms_limit} комнат Огненного Лабиринта!</b>\n"
                f"Пламя памяти остаётся тёплым. Сессия завершена.\n"
                f"Хочешь дальше — оплати новый заход.",
                reply_markup=await main_menu_kb(cb.from_user.id),
                parse_mode="HTML")
        except Exception:
            await cb.message.answer(
                f"🏁 <b>Ты прошёл все {rooms_limit} комнат Огненного Лабиринта!</b>\n"
                f"Пламя памяти остаётся тёплым. Сессия завершена.\n"
                f"Хочешь дальше — оплати новый заход.",
                reply_markup=await main_menu_kb(cb.from_user.id),
                parse_mode="HTML")
        return
    await cb.answer(f"🔀 {PATH_LABELS[path]}. Двигаемся дальше…")
    # Фаза 2/3: здесь будут броски встреч (враги/Колодец/Древо/Сундук/босс).
    # Пока — следующая развилка (пустая) с учётом паттерна геометрии.
    await cb.message.answer(_fork_text(updated),
                            reply_markup=_fork_kb(session_id),
                            parse_mode="HTML")


@router.callback_query(F.data.startswith("fireevent:leave:"))
async def fire_event_leave_cb(cb: CallbackQuery):
    parts = cb.data.split(":")
    session_id = int(parts[2]) if len(parts) > 2 else 0
    session = await _session_of(cb.from_user.id, session_id)
    if not session:
        return
    await end_fire_lab_session(session_id, 'left')
    await cb.answer("🚪 Ты покинул лабиринт.", show_alert=True)
    try:
        await cb.message.edit_text("🚪 Ты покинул Огненный Лабиринт. Пламя остаётся тёплым.\n"
                                   "До встречи в следующий заход!",
                                   reply_markup=await main_menu_kb(cb.from_user.id),
                                   parse_mode="HTML")
    except Exception:
        await cb.message.answer(
            "🚪 Ты покинул Огненный Лабиринт.\nДо встречи в следующий заход!",
            reply_markup=await main_menu_kb(cb.from_user.id),
            parse_mode="HTML")


async def _session_of(user_id: int, session_id: int):
    """Сессия, принадлежащая именно этому игроку (защита от чужих id)."""
    s = await get_active_fire_lab_session(user_id)
    if not s or int(s['id']) != int(session_id):
        return None
    return s


@router.callback_query(F.data == "fireevent:enter")
async def fire_event_enter_cb(cb: CallbackQuery, state: FSMContext):
    """Вход в лабиринт: окно уже проверено гвардом — платный вход."""
    from database.db import get_user
    user = await get_user(cb.from_user.id)
    if not user:
        await cb.answer("❌ Сначала /start.", show_alert=True)
        return
    fee = int(getattr(config, "FIRE_EVENT_LAB_FEE", 42) or 0)
    if int(user['nordmarks'] or 0) < fee:
        await cb.answer(f"❌ Вход стоит {fee} НМ — не хватает.", show_alert=True)
        return
    already = await get_active_fire_lab_session(cb.from_user.id)
    if already:
        # незакрытая сессия — просто вернёмся в неё, повторно не платим
        await cb.answer("🔥 Ты уже внутри лабиринта.")
        await cb.message.answer(_fork_text(already),
                                reply_markup=_fork_kb(already['id']),
                                parse_mode="HTML")
        return
    day = db.today_report_day()
    max_entries = int(getattr(config, "FIRE_EVENT_MAX_ENTRIES_DAY", 4) or 0)
    used = await get_fire_lab_entries_today(cb.from_user.id, day)
    if max_entries > 0 and used >= max_entries:
        await cb.answer(f"❌ Лимит заходов на сегодня исчерпан: {max_entries} в сутки.",
                        show_alert=True)
        return
    from database.db import remove_nordmarks
    hp = 0
    try:
        from utils.combat_model import pilot_combat_stats
        stats = await pilot_combat_stats(cb.from_user.id)
        hp = int(stats.get('hp_max') or 0) if stats else 0
    except Exception:
        hp = 0
    if hp <= 0:
        hp = 10  # подстраховка
    await remove_nordmarks(cb.from_user.id, fee, "firelab_entry",
                           f"Вход в Огненный Лабиринт (заход {used + 1}/{max_entries})")
    n = await inc_fire_lab_entries(cb.from_user.id, day)
    session_id = await create_fire_lab_session(cb.from_user.id, hp)
    updated = await get_active_fire_lab_session(cb.from_user.id)
    await cb.answer("🔥 Вход оплачен!")
    await cb.message.answer(
        f"🔥 <b>Дни Пламенного Круговорота</b>\n"
        f"Вход оплачен: −{fee} НМ (заход {n}/{max_entries} за сутки).\n\n"
        + _fork_text(updated),
        reply_markup=_fork_kb(session_id),
        parse_mode="HTML")
