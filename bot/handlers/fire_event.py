"""Дни Пламенного Круговорота — праздничное событие (ТЗ — FIRE_EVENT.md).

Фаза 1 (каркас): городская кнопка «🪔 Дни Пламенного Кругворота», вход в
Огненный Лабиринт (32 НМ, до 4 заходов/сутки), сессии в `fire_lab_sessions`,
комната-развилка с тремя путями (запись шагов, скрытые паттерны появятся на
Фазе 3). Пока FIRE_LAB_ENABLED = False — все `fireevent:`-колбэки отвечают
заглушкой, кнопка города скрыта (аналог гварда клан-холла).

Остальные фазы: враги и босс (Ф2), Колодец/Древо Огня/Сундук + скрытая
геометрия (Ф3), предметы/рецепты/Лампа/достижение (Ф4), дроп и финал (Ф5).
"""

import asyncio
import html
import json
import os
import random

import config

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.types import FSInputFile

import database.db as db
from database.db import (
    fire_event_active,
    get_fire_lab_entries_today,
    inc_fire_lab_entries,
    create_fire_lab_session,
    get_active_fire_lab_session,
    end_fire_lab_session,
    touch_fire_lab_session,
    get_fire_photo,
)
from utils.helpers import plural_nordmark, resolve_image_seasonal, resolve_image
from keyboards.keyboards import main_menu_kb

router = Router()

# ───────── Единая отрисовка Лабиринта (одно сообщение на игрока, как в лесу) ─────────
# Храним последнее сообщение лабиринта: user → (chat_id, message_id)
FIRELAB_MSG: dict[int, tuple[int, int]] = {}


async def _fire_paint(cb: CallbackQuery, *, text: str = None,
                      kb: InlineKeyboardMarkup = None,
                      media_path: str = None,
                      photo_id: str = None) -> None:
    """Рисование/замена окна Лабиринта: фото локации/врага внутри сообщения.

    media_path — путь в assets/img (resolve_image), photo_id — file_id из
    админ-редактора врага (перебивает файл). Одно сообщение на игрока (edit).
    """
    bot = cb.message.bot
    chat_id = cb.message.chat.id
    uid = cb.from_user.id
    entry = FIRELAB_MSG.get(uid)
    target_id = entry[1] if entry and entry[0] == chat_id else None

    sent = None
    if photo_id:
        try:
            sent = await bot.send_photo(
                chat_id, photo_id,
                caption=text, reply_markup=kb, parse_mode="HTML")
        except Exception:
            sent = None
    elif media_path and os.path.isfile(media_path):
        try:
            sent = await bot.send_photo(
                chat_id, FSInputFile(media_path),
                caption=text, reply_markup=kb, parse_mode="HTML")
        except Exception:
            sent = None

    if sent is not None:
        FIRELAB_MSG[uid] = (chat_id, sent.message_id)
        return
    # медиа нет или потерялась — рисуем текст в самом старом сообщении
    if target_id is not None:
        try:
            await bot.delete_message(chat_id, target_id)
        except Exception:
            pass
        FIRELAB_MSG.pop(uid, None)
        try:
            sent = await bot.send_message(chat_id, text, reply_markup=kb,
                                          parse_mode="HTML")
            if sent:
                FIRELAB_MSG[uid] = (chat_id, sent.message_id)
            return
        except Exception:
            pass
    await cb.message.answer(text, reply_markup=kb, parse_mode="HTML")

# Пока лабиринт закрыт (FIRE_LAB_ENABLED=False), все fireevent:-хендлеры
# отвечают заглушкой (аналог гварда клан-холла).
FIRE_EVENT_CLOSED_TEXT = "🔥 Дни Пламенного Круговорота ещё готовятся — скоро откроем!"

# Пути развилки: L = налево, S = прямо, R = направо.
PATH_LABELS = {"L": "⬅️ Налево", "S": "⬆️ Прямо", "R": "➡️ Направо"}

# Ключи врагов Огненного Лабиринта (firelab_enemies).
FIRELAB_ENEMY_KEYS = ("scarecrow", "apple_child", "crow", "hub")
FIRELAB_BOSS_KEY = "pumpkin_boss"

# Ключи эффектов на игрока (хранятся в effects_json сессии).
FX_BLIND = "blind"        # ослепление: часть ударов промахивается
FX_STUN = "stun"          # оглушение: игрок пропускает ход
FX_SLOW = "slow"          # замедление: сильно снижает уклон игрока, чуть +уклон врага
FX_BURN = "burn"          # поджиг: −N HP/ход
FX_REGEN = "regen"        # регенерация от расходника: очередь тиков [+a1, +a2, +a3]


# ==================== ВСТРЕЧИ И БРОСКИ РАЗВИЛКИ (Фаза 2/3) ====================

async def _roll_room(user_id: int, session, path: str, history: list) -> str:
    """Бросок комнаты после выбора пути. Возвращает название комнаты:
    'tree'/'well'/'boss'/'enemy'/'empty' (Сундук убран из праздника)."""
    tree_visits = int(session['tree_visits'] or 0)
    well_visits = int(session['well_visits'] or 0)
    boss_encounters = int(session['boss_encounters'] or 0)
    steps = int(session['steps'] or 0)

    tree_max = int(getattr(config, "FIRE_LAB_TREE_MAX", 1) or 1)
    well_max = int(getattr(config, "FIRE_LAB_WELL_MAX", 3) or 3)
    boss_max = int(getattr(config, "FIRE_LAB_BOSS_MAX", 2) or 2)

    tree_pattern = tuple(getattr(config, "FIRE_LAB_PATTERN_TREE", ("L", "L", "S", "S", "R", "R")))
    well_pattern = tuple(getattr(config, "FIRE_LAB_PATTERN_WELL", ("L", "L", "S", "S")))

    # 0) скрытые паттерны (перебивают шансы; окно последних шагов ВКЛЮЧАЕТ
    #    только что выбранный путь)
    def _window_matches(pattern):
        if len(history) < len(pattern):
            return False
        return tuple(history[-len(pattern):]) == pattern

    if tree_visits < tree_max and _window_matches(tree_pattern):
        return "tree"
    if well_visits < well_max and _window_matches(well_pattern):
        return "well"

    # 1) случайные особые комнаты
    if tree_visits < tree_max and random.random() < float(getattr(config, "FIRE_LAB_P_TREE", 0.09)):
        return "tree"
    if well_visits < well_max and random.random() < float(getattr(config, "FIRE_LAB_P_WELL", 0.07)):
        return "well"

    # 2) босс: после 13 комнат, шанс 50%, максимум встреч
    boss_after = int(getattr(config, "FIRE_LAB_BOSS_AFTER_ROOMS", 13) or 13)
    if steps >= boss_after and boss_encounters < boss_max \
            and random.random() < float(getattr(config, "FIRE_LAB_BOSS_P", 0.50)):
        return "boss"

    # 3) обычный враг 50% (4 вида поровну)
    if random.random() < float(getattr(config, "FIRE_LAB_ENEMY_P", 0.50)):
        return "enemy"

    # 4) пустая развилка
    return "empty"


# ============================== БОЕВОЙ ЦИКЛ ==============================

async def _get_forelab_enemy(kind: str = None):
    """Враг firelab_enemies по ключу (или None)."""
    conn = await db.get_db()
    if kind:
        cur = await conn.execute(
            "SELECT * FROM firelab_enemies WHERE key = ?", (kind,))
        return await cur.fetchone()
    return None


def _tier_enemy(e, tier: int):
    """Словарь врага со сдвигом по Тиру Огненного эха (HP +bonus) и дропами.

    Дроп-карточки читаются из строки firelab_enemies (drops_json), шанс каждой
    умножается на tier-множитель и капсится на 1: min(1, base × (1+bonus)).
    """
    loot_mult = db.firelab_tier_loot_mult(tier)
    drops = []
    try:
        raw = e.get('drops') if hasattr(e, 'get') else None
        if isinstance(raw, str):
            raw = json.loads(raw or '[]')
        if not isinstance(raw, (list, tuple)):
            raw = []
    except (TypeError, ValueError):
        raw = []
    for d in raw:
        try:
            base = float(d['chance'] or 0) * loot_mult
            drops.append({"item_id": int(d['item_id']), "qty": int(d.get('qty') or 1),
                          "chance": min(1.0, base), "base": base})
        except (KeyError, TypeError, ValueError):
            continue
    return {
        'key': e['key'], 'name': e['name'],
        'hp': int(e['hp']) + db.firelab_tier_enemy_bonus(tier),
        'hp_max': int(e['hp']) + db.firelab_tier_enemy_bonus(tier),
        'armor': int(e.get('armor') or 0),
        'dodge': float(e.get('dodge') or 0),
        'dmg_min': int(e.get('dmg_min') or 0),
        'dmg_max': int(e.get('dmg_max') or 0),
        'is_boss': e['key'] == FIRELAB_BOSS_KEY,
        'drops': drops,
        'on_hit_effects': e.get('on_hit_effects'),
        # картинки: file_id из админ-редактора перебивает локальные файлы
        'image': e.get('image'),
        'photo_key': e.get('photo_key') or f"city/fire_{(e.get('key') or '')}",
    }


def _roll_enemy_loot(enemy: dict) -> list[tuple[str, int, float]]:
    """Броски по дроп-карточкам врага: [(имя, qty, шанс_броска)] по факту выпадения."""
    loot = []
    for d in enemy.get('drops') or []:
        if random.random() < float(d['chance']):
            loot.append(d)
    return loot


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


async def _paint_fork(cb, session, session_id: int, prefix: str = ""):
    """Развилка: единое сообщение с картинкой лабиринта (prefix — текст перед ней)."""
    await _fire_paint(cb, text=(prefix or "") + _fork_text(session),
                      kb=_fork_kb(session_id), **(await _room_kw("fork")))


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
        old_tier = await db.get_fire_lab_tier(cb.from_user.id)
        await end_fire_lab_session(session_id, 'finished')
        new_tier = await db.inc_fire_lab_tier(cb.from_user.id)
        tier_note = ""
        if new_tier > old_tier:
            tier_note = (f"\n\n🔥 <b>Огненное эхо усилилось:</b> Тир {new_tier} — "
                         "лабиринт стал сложнее, но награда стала вероятнее! "
                         "(действует весь праздник)")
        finish_text = (
            f"🏁 <b>Ты прошёл все {rooms_limit} комнат Огненного Лабиринта!</b>\n"
            f"Пламя памяти остаётся тёплым. Сессия завершена.\n"
            f"Следующий заход — снова за плату (лимит суток тот же)."
            f"{tier_note}"
        )
        await cb.answer("🏁 Лабиринт пройден до конца!", show_alert=True)
        await _fire_paint(
            cb, text=finish_text,
            kb=await main_menu_kb(cb.from_user.id), **(await _room_kw("fork")))
        return
    await cb.answer(f"🔀 {PATH_LABELS[path]}. Двигаемся дальше…")
    room = await _roll_room(cb.from_user.id, updated, path, history)
    if room == "empty":
        await _paint_fork(cb, updated, session_id)
        return
    if room in ("enemy", "boss"):
        await _start_battle(cb, updated, session_id, room,
                            tier=await db.get_fire_lab_tier(cb.from_user.id))
        return
    if room == "well":
        await _enter_well(cb, updated, session_id)
        return
    if room == "tree":
        await _enter_tree(cb, updated, session_id)
        return


def _room_chrome(title: str, body: str, extra_row=None,
                 hint: str = "") -> str:
    """Каркасс текста особой комнаты: заголовок, тело, хвост с подсказкой."""
    return (f"{title}\n\n{body}\n{hint}".rstrip() + "\n")


def _cont_kb(session_id: int, back: str = None) -> InlineKeyboardMarkup:
    """Единая кнопка «идти дальше» для особых комнат."""
    rows = []
    if back:
        rows.append(back)
    rows.append([InlineKeyboardButton(
        text="🚶 Идти дальше", callback_data=f"fireevent:cont:{session_id}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


@router.callback_query(F.data.startswith("fireevent:cont:"))
async def fire_event_cont_cb(cb: CallbackQuery):
    """Уйти из особой комнаты обратно на развилку."""
    session_id = int(cb.data.split(":")[2])
    session = await _session_of(cb.from_user.id, session_id)
    if not session:
        return
    await cb.answer()
    await _paint_fork(cb, session, session_id)


# ------------------------------ КОЛОДЕЦ ------------------------------

async def _enter_well(cb, session, session_id: int):
    """Колодец: фиксированное лечение (FIRE_LAB_WELL_HEAL) + праздничная рыбалка."""
    heal = int(getattr(config, "FIRE_LAB_WELL_HEAL", 50) or 50)
    ap_gain = int(getattr(config, "FIRE_LAB_WELL_AP", 10) or 0)
    conn = await db.get_db()
    await conn.execute(
        "UPDATE fire_lab_sessions SET hp = MIN(hp_max, hp + ?) WHERE id = ?",
        (heal, session_id))
    await conn.commit()
    if ap_gain > 0:
        await db.add_ap(cb.from_user.id, ap_gain, reason="Колодец Круговорота")
    visits = await db.bump_fire_lab_room_visit(session_id, "well")
    session = await db.get_active_fire_lab_session(cb.from_user.id)
    tries_left = int(getattr(config, "FIRE_LAB_WELL_FISH_TRIES", 6) or 6)
    body = (
        "Звонкий всплеск из глубины: колодец Огненного Круговорота дышит "
        "паром, вода тёплая, как из ключа. Ты моешь руки, пьёшь — и тело "
        f"наполняется силой: +{heal} HP и +{ap_gain} ОД.\n\n"
        f"💙 Сейчас: {int(session['hp'])}/{int(session['hp_max'])} HP.\n"
        f"🎣 В тёмной воде ходят праздничные рыбы — можно закинуть удочку "
        f"({tries_left} попыток)."
    )
    text = _room_chrome("🪣 КОЛОДЕЦ ОГНЕННОГО КРУГОВОРОТА" +
                        (f" (визит {visits}/"
                         f"{int(getattr(config, 'FIRE_LAB_WELL_MAX', 3) or 3)})"
                         if visits else ""), body)
    kb = await _well_kb(cb.from_user.id, session_id, tries_left)
    await _fire_paint(cb, text=text, kb=kb, **(await _room_kw('well')))


async def _room_kw(room_key: str) -> dict:
    """Картинка комнаты праздника для _fire_paint: file_id из админ-менеджера
    («Картинки Круговорота»), иначе локальный файл assets/img, иначе без фото."""
    photo_id = await get_fire_photo(room_key)
    if photo_id:
        return {"photo_id": photo_id}
    base = {
        "fork": getattr(config, "FIRE_LAB_FORK_KEY", "city/fire_maze"),
        "entry": getattr(config, "FIRE_LAB_FORK_KEY", "city/fire_maze"),
        "well": getattr(config, "FIRE_LAB_WELL_KEY", "city/fire_well"),
        "tree": getattr(config, "FIRE_LAB_TREE_KEY", "city/fire_tree"),
    }.get(room_key)
    return {"media_path": resolve_image(base) if base else None}


BAIT_CHOICES = (
    ("worms", "🪱 Черви"),
    ("spider", "🕷 Лапка кристального паука"),
    ("combined", "🧪 Комбинированная наживка"),
    ("auto", "🔄 Авто (что есть)"),
    ("none", "🚫 Без наживки"),
)


async def _well_kb(uid: int, session_id: int, left: int) -> InlineKeyboardMarkup:
    """Кнопки колодца: забросить, выбрать наживку, идти дальше."""
    from bot.handlers import fishing as fs
    user = await db.get_user(uid) or {}
    label = await fs._bait_label(uid, (user.get('fishing_bait') or "").strip())
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"🎣 Ловить ({left})",
                              callback_data=f"fireevent:fishing:{session_id}")],
        [InlineKeyboardButton(text=f"🪱 Наживка: {label}",
                              callback_data=f"fireevent:bait:{session_id}")],
        [InlineKeyboardButton(text="🚶 Идти дальше",
                              callback_data=f"fireevent:cont:{session_id}")],
    ])


async def _paint_well_menu(cb, session_id: int, uid: int, session) -> None:
    """Экран колодца без нового лечения (после выбора наживки)."""
    cap = int(getattr(config, "FIRE_LAB_WELL_FISH_TRIES", 6) or 6)
    left = max(0, cap - int(session['fish_used'] or 0))
    text = _room_chrome(
        "🪣 КОЛОДЕЦ ОГНЕННОГО КРУГОВОРОТА",
        f"💙 Сейчас: {int(session['hp'])}/{int(session['hp_max'])} HP.\n"
        f"🎣 Попыток осталось: {left}.")
    await _fire_paint(cb, text=text, kb=await _well_kb(uid, session_id, left),
                      **(await _room_kw('well')))


@router.callback_query(F.data.startswith("fireevent:bait:"))
async def fire_event_bait_cb(cb: CallbackQuery):
    """Выбор наживки прямо в колодце (та же настройка, что в меню озера)."""
    session_id = int(cb.data.split(":")[2])
    session = await _session_of(cb.from_user.id, session_id)
    if not session:
        return
    await cb.answer()
    rows = [[InlineKeyboardButton(text=title,
                                  callback_data=f"fireevent:baitset:{session_id}:{code}")]
            for code, title in BAIT_CHOICES]
    rows.append([InlineKeyboardButton(text="🔙 Назад к колодцу",
                                      callback_data=f"fireevent:wellback:{session_id}")])
    await _fire_paint(
        cb,
        text=_room_chrome("🪣 КОЛОДЕЦ ОГНЕННОГО КРУГОВОРОТА",
                          "🪱 Выбери наживку. Она списывается с каждым забросом.\n"
                          "Без наживки рыба не клюёт, но со дна иногда поднимаются "
                          "моток проволоки или пучок сена."),
        kb=InlineKeyboardMarkup(inline_keyboard=rows), **(await _room_kw('well')))


@router.callback_query(F.data.startswith("fireevent:baitset:"))
async def fire_event_baitset_cb(cb: CallbackQuery):
    parts = cb.data.split(":")
    session_id = int(parts[2])
    code = parts[3]
    session = await _session_of(cb.from_user.id, session_id)
    if not session:
        return
    allowed = {code_ for code_, _ in BAIT_CHOICES}
    if code not in allowed:
        await cb.answer("❌ Нет такой наживки.", show_alert=True)
        return
    value = "" if code == "auto" else code
    await db.update_user(cb.from_user.id, fishing_bait=value)
    await cb.answer("🪱 Наживка выбрана.")
    await _paint_well_menu(cb, session_id, cb.from_user.id, session)


@router.callback_query(F.data.startswith("fireevent:wellback:"))
async def fire_event_wellback_cb(cb: CallbackQuery):
    session_id = int(cb.data.split(":")[2])
    session = await _session_of(cb.from_user.id, session_id)
    if not session:
        return
    await cb.answer()
    await _paint_well_menu(cb, session_id, cb.from_user.id, session)


async def _nobait_result(uid: int, left_now: int):
    """Без наживки рыба не клюёт; редко со дна поднимается проволока или сено."""
    title = "🪣 КОЛОДЕЦ ОГНЕННОГО КРУГОВОРОТА"
    if random.random() >= float(getattr(config, "FIRE_LAB_NOBAIT_FIND_P", 0.12) or 0):
        return _room_chrome(title, "🎣 Без наживки рыба не клюёт — со дна пусто.\n"
                                   f"Осталось попыток: {left_now}."), None
    table = tuple(getattr(config, "FIRE_LAB_NOBAIT_FIND", ()))
    if not table:
        return _room_chrome(title, "🎣 Без наживки рыба не клюёт — со дна пусто.\n"
                                   f"Осталось попыток: {left_now}."), None
    name = random.choices([n for n, _ in table], weights=[w for _, w in table], k=1)[0]
    item = await db.get_item_by_name(name)
    if not item:
        return _room_chrome(title, "🪝 Что-то зацепилось, но предмет не заведён. "
                                   "Сообщи хранителю."), None
    await db.add_inventory_item(uid, item['id'], 1)
    await db.log_activity(uid, "firelab", f"Колодец без наживки: поднял «{name}»")
    text = _room_chrome(
        title,
        f"🪝 Без наживки рыба не клюёт, но со дна поднялось: <b>{_esc(name)}</b>!\n"
        f"Осталось попыток: {left_now}.")
    return text, await _fish_kw(name)


async def _fish_kw(fish_name: str) -> dict | None:
    """Картинка пойманной рыбы: фото из редактора рыбалки (колодец), иначе локальный файл."""
    from utils.helpers import item_local_photo
    pid = await db.get_water_fish_photo_by_name("fire_well", fish_name)
    if pid:
        return {"photo_id": pid}
    path = item_local_photo(fish_name)
    if path:
        return {"media_path": path}
    return None


@router.callback_query(F.data.startswith("fireevent:fishing:"))
async def fire_event_fishing_cb(cb: CallbackQuery):
    """Праздничная рыбалка в Колодце — как на озере: удочка, наживка, ОД и ожидание поклёвки."""
    from bot.handlers import fishing as fs
    uid = cb.from_user.id
    session_id = int(cb.data.split(":")[2])
    session = await _session_of(uid, session_id)
    if not session:
        return
    cap = int(getattr(config, "FIRE_LAB_WELL_FISH_TRIES", 6) or 6)
    if cap - int(session['fish_used'] or 0) <= 0:
        await cb.answer("🎣 Попытки этого визита исчерпаны — иди дальше.", show_alert=True)
        return
    if uid in fs.FISHING_CASTING:
        await cb.answer("Ты уже закинул удочку — дождись результата!", show_alert=True)
        return
    rod = await fs._rod_for(uid)
    if not rod:
        await cb.answer("❌ Нужна удочка: «Удочка из орешника» из магазина (категория «Рыбалка»).",
                        show_alert=True)
        return
    user = await db.get_user(uid)
    chosen = (user.get('fishing_bait') or "").strip()
    bait_name, bait_id = await fs._resolve_bait(uid, chosen)
    ap_cost = int(getattr(config, "FISH_AP_COST", 3) or 3)
    if not await db.remove_ap(uid, ap_cost, reason="заброс удочки (Колодец)"):
        await cb.answer(f"❌ Не хватает ОД: нужно {ap_cost}.", show_alert=True)
        return

    fs.FISHING_CASTING.add(uid)
    try:
        fs._mark_fishing_active(uid)
        if bait_id is not None:
            await db.remove_inventory_item(uid, bait_id, 1)
        used = await db.inc_fire_lab_fish_used(session_id)
        left_now = cap - int(used)
        delay = random.randint(*getattr(config, "FIRE_LAB_FISH_DELAY", (7, 15)))
        chance = (fs._catch_chance(rod, bait_name, (await db.get_award_bonus(uid))['fishing'])
                  if bait_name else 0)
        bait_desc = f"с наживкой «{bait_name}»" if bait_name else "без наживки"
        await db.log_activity(uid, "firelab",
                              f"Колодец: заброс {bait_desc}, шанс {chance}%")
        cast_text = _room_chrome(
            "🪣 КОЛОДЕЦ ОГНЕННОГО КРУГОВОРОТА",
            f"🎣 Ты забросил удочку {_esc(bait_desc)}...\n"
            f"Результат через {delay} секунд. Наберись терпения!")
        await _fire_paint(cb, text=cast_text, kb=None, **(await _room_kw('well')))
        await cb.answer()
        await asyncio.sleep(delay)

        fish_kw = None
        if not bait_name:
            text, fish_kw = await _nobait_result(uid, left_now)
        elif random.random() * 100 >= chance:
            text = _room_chrome(
                "🪣 КОЛОДЕЦ ОГНЕННОГО КРУГОВОРОТА",
                "🎣 Поплавок дёрнулся, ты подсекаешь... и вдруг пусто. Сорвалось.\n"
                f"Осталось попыток: {left_now}.")
        else:
            pool = await db.get_water_fish_pool("fire_well")
            if pool:
                names = [r['name'] for r in pool]
                weights = [max(1, int(r['day_weight'] or 0) + int(r['night_weight'] or 0))
                           for r in pool]
                fish_name = random.choices(names, weights=weights, k=1)[0]
            else:
                table = ((getattr(config, "FIRE_LAB_FISH_OSETR_NAME",
                                  "Спектральная Латимерия"), 60),
                         (getattr(config, "FIRE_LAB_FISH_SOUL_NAME",
                                  "Скелетная Арована"), 25),
                         (getattr(config, "FIRE_LAB_FISH_CARP_NAME",
                                  "Пылающая Душа"), 15))
                weights = [w for _, w in table]
                fish_name = random.choices([n for n, _ in table], weights=weights, k=1)[0]
            conn = await db.get_db()
            cur = await conn.execute("SELECT id FROM items WHERE name = ?", (fish_name,))
            row = await cur.fetchone()
            if not row:
                text = _room_chrome("🪣 КОЛОДЕЦ ОГНЕННОГО КРУГОВОРОТА",
                                    "🐟 Что-то поймал, но предмет потерялся. Сообщи хранителю.")
            else:
                item_id = int(row['id'])
                await db.add_inventory_item(uid, item_id, 1)
                fresh = await db.mark_fire_fish_caught(uid, item_id)
                kinds = await db.count_fire_fish_kinds(uid)
                await db.log_activity(uid, "firelab",
                                      f"Праздничная рыбалка: поймал «{fish_name}»")
                line = f"🎣 Поплавок подпрыгивает — <b>{_esc(fish_name)}</b>!"
                if fresh:
                    line += " (новый вид!)"
                line += f"\nОсталось попыток: {left_now}."
                ach_note = ""
                if kinds >= int(getattr(config, "FIRE_FISHER_THRESHOLD", 3) or 3):
                    lvl, _n, _ = await db.set_achievement_progress(
                        uid, getattr(config, "FIRE_FISHER_ACH_KEY", "fire_fisher"), kinds)
                    if lvl:
                        ach_note = ("\n\n🪣 <b>Мини-ачивка: «Рыбак древних»!</b> "
                                    "Все три праздничные рыбы — твои. Премия — доступна у наград, "
                                    "а в награду — рецепт «Предания предков».")
                text = _room_chrome("🪣 КОЛОДЕЦ ОГНЕННОГО КРУГОВОРОТА", line + ach_note)
                fish_kw = await _fish_kw(fish_name)
        fish_kb = await _well_kb(uid, session_id, left_now)
        await _fire_paint(cb, text=text, kb=fish_kb, **(fish_kw or await _room_kw('well')))
    finally:
        fs.FISHING_CASTING.discard(uid)


# ------------------------------ ДРЕВО ОГНЯ ------------------------------

async def _enter_tree(cb, session, session_id: int):
    """Древо Огня: благословение (+15% урона, +1 HP после удара) до конца сессии."""
    visits = await db.bump_fire_lab_room_visit(session_id, "tree")
    if not int(session['blessing'] or 0):
        await db.set_fire_lab_blessing(session_id)
        session = await db.get_active_fire_lab_session(cb.from_user.id)
    pct = int(getattr(config, "FIRE_TREE_DMG_BONUS_PCT", 15) or 15)
    regen = int(getattr(config, "FIRE_TREE_REGEN_HP", 1) or 1)
    body = (
        "Тёплый свет сквозь листву: Древо Огня вспыхивает янтарными жилами и "
        "кланяется тебе кроной. Долгое пламя из его коры встаёт тебе в плечи.\n\n"
        f"🔥 Благословение Круговорота (до конца сессии):\n"
        f"   • урон +{pct}%\n"
        f"   • +{regen} HP после каждого твоего удара\n"
        f"💙 Сейчас: {int(session['hp'])}/{int(session['hp_max'])} HP."
    )
    text = _room_chrome("🌳 ДРЕВО ОГНЯ", body)
    await _fire_paint(cb, text=text, kb=_cont_kb(session_id), **(await _room_kw('tree')))


# ------------------------------ СУНДУК (убран из праздника) ------------------------------


@router.callback_query(F.data.startswith("fireevent:leave:"))
async def fire_event_leave_cb(cb: CallbackQuery):
    parts = cb.data.split(":")
    session_id = int(parts[2]) if len(parts) > 2 else 0
    session = await _session_of(cb.from_user.id, session_id)
    if not session:
        return
    await end_fire_lab_session(session_id, 'left')
    await cb.answer("🚪 Ты покинул лабиринт.", show_alert=True)
    await _fire_paint(
        cb, text=("🚪 Ты покинул Огненный Лабиринт. Пламя остаётся тёплым.\n"
                  "До встречи в следующий заход!"),
        kb=await main_menu_kb(cb.from_user.id), **(await _room_kw("fork")))


async def _session_of(user_id: int, session_id: int):
    """Сессия, принадлежащая именно этому игроку (защита от чужих id)."""
    s = await get_active_fire_lab_session(user_id)
    if not s or int(s['id']) != int(session_id):
        return None
    return s


def _entry_text(fee: int, used: int, max_entries: int, tourist: bool) -> str:
    head = ("🪔 <b>Дни Пламенного Круговорота</b>\n\n"
            "Перед тобой вход в Лабиринт из снопов сена — жаркое пламя, "
            "смех горожан и запах тыквы.\n\n")
    if tourist:
        return head + ("⛔ В лабиринт вход только для граждан Нордхайма и легионеров. "
                       "Туристам — только поглядеть со стороны и получить сувенир.")
    return head + (f"🔑 Вход: <b>{fee} НМ</b>, до {max_entries} заходов в сутки "
                   f"(сегодня: {used}/{max_entries}).\n"
                   f"Лабиринт полон загадок.")


@router.callback_query(F.data == "fireevent:enter")
async def fire_event_enter_cb(cb: CallbackQuery, state: FSMContext):
    """Экран входа в Лабиринт: картинка входа, цена и кнопки (вход — отдельным шагом)."""
    from database.db import get_user, user_is_tourist
    user = await get_user(cb.from_user.id)
    if not user:
        await cb.answer("❌ Сначала /start.", show_alert=True)
        return
    fee = int(getattr(config, "FIRE_EVENT_LAB_FEE", 32) or 0)
    max_entries = int(getattr(config, "FIRE_EVENT_MAX_ENTRIES_DAY", 4) or 0)
    if await user_is_tourist(cb.from_user.id):
        text = _entry_text(fee, 0, max_entries, tourist=True)
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🎁 Получить сувенир",
                                  callback_data="fireevent:souvenir")],
            [InlineKeyboardButton(text="🏠 В город", callback_data="city:menu")],
        ])
    else:
        used = await get_fire_lab_entries_today(cb.from_user.id, db.today_report_day())
        text = _entry_text(fee, used, max_entries, tourist=False)
        rows = [[InlineKeyboardButton(text=f"🔑 Войти — {fee} НМ",
                                      callback_data="fireevent:go")]]
        if getattr(config, "FIRE_EXCHANGE_ENABLED", False):
            rows.append([InlineKeyboardButton(text="🛍 Лавка Круговорота",
                                              callback_data="fireevent:shop")])
        rows.append([InlineKeyboardButton(text="🏠 В город", callback_data="city:menu")])
        kb = InlineKeyboardMarkup(inline_keyboard=rows)
    await cb.answer()
    await _fire_paint(cb, text=text, kb=kb, **(await _room_kw("entry")))


@router.callback_query(F.data == "fireevent:souvenir")
async def fire_event_souvenir_cb(cb: CallbackQuery):
    """Туристу — разовый сувенир (леденец) прямо на экране входа."""
    from database.db import user_is_tourist, grant_fire_souvenir, get_item_by_name, add_inventory_item
    if not await user_is_tourist(cb.from_user.id):
        await cb.answer("🔑 Сувенир — для гостей праздника.", show_alert=True)
        return
    candy = await get_item_by_name(
        getattr(config, "FIRE_LAB_CANDY_NAME", "Леденец языков пламени"))
    fresh = False
    if candy:
        fresh = await grant_fire_souvenir(cb.from_user.id)
        if fresh:
            await add_inventory_item(cb.from_user.id, candy['id'], 1)
            await db.log_activity(cb.from_user.id, "firelab",
                                  "Сувенир праздника: леденец (туристу, бесплатно)")
    fee = int(getattr(config, "FIRE_EVENT_LAB_FEE", 32) or 0)
    max_entries = int(getattr(config, "FIRE_EVENT_MAX_ENTRIES_DAY", 4) or 0)
    sweet = ("\n\n🎁 <b>Сувенир праздника:</b> «Леденец языков пламени» — "
             "держи на память о Круговороте!" if fresh else
             "\n\n🎁 Сувенир праздника ты уже получал — он у тебя (или был).")
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 В город", callback_data="city:menu")],
    ])
    await cb.answer("🎁 Сувенир праздника!" if fresh else "🪔 Праздник для гостей.")
    await _fire_paint(cb, text=_entry_text(fee, 0, max_entries, tourist=True) + sweet,
                      kb=kb, **(await _room_kw("entry")))


async def _item_qty(uid: int, name: str) -> int:
    item = await db.get_item_by_name(name)
    if not item:
        return 0
    inv = await db.get_inventory_item(uid, item['id'])
    return int(inv['quantity'] or 0) if inv else 0


async def _exchange_screen(cb, uid: int, note: str = "") -> None:
    rows = []
    lines = ["🛍 <b>Лавка Круговорота</b>", "Праздничный сбор на сладости.", ""]
    for idx, (give, give_qty, get, get_qty) in enumerate(config.FIRE_EXCHANGE_OFFERS):
        have = await _item_qty(uid, give)
        lines.append(f"• {give_qty} × {_esc(give)} → {get_qty} × {_esc(get)} (у тебя: {have})")
        rows.append([InlineKeyboardButton(
            text=f"{give_qty} {give} → {get_qty} {get}",
            callback_data=f"fireevent:xchg:{idx}")])
    rows.append([InlineKeyboardButton(text="🔙 Назад ко входу", callback_data="fireevent:enter")])
    if note:
        lines += ["", note]
    # картинка лавки из менеджера «Картинки Круговорота»; нет — картинка входа
    kw = await _room_kw('shop')
    if not kw.get('photo_id') and not kw.get('media_path'):
        kw = await _room_kw('entry')
    await _fire_paint(cb, text="\n".join(lines), kb=InlineKeyboardMarkup(inline_keyboard=rows),
                      **kw)


@router.callback_query(F.data == "fireevent:shop")
async def fire_event_shop_cb(cb: CallbackQuery):
    if not getattr(config, "FIRE_EXCHANGE_ENABLED", False):
        await cb.answer("🛍 Лавка ещё не открыта.", show_alert=True)
        return
    if await db.user_is_tourist(cb.from_user.id):
        await cb.answer("⛔ Лавка — для пилотов.", show_alert=True)
        return
    await cb.answer()
    await _exchange_screen(cb, cb.from_user.id)


@router.callback_query(F.data.startswith("fireevent:xchg:"))
async def fire_event_xchg_cb(cb: CallbackQuery):
    if not getattr(config, "FIRE_EXCHANGE_ENABLED", False):
        await cb.answer("🛍 Лавка ещё не открыта.", show_alert=True)
        return
    if await db.user_is_tourist(cb.from_user.id):
        await cb.answer("⛔ Лавка — для пилотов.", show_alert=True)
        return
    uid = cb.from_user.id
    try:
        idx = int(cb.data.split(":")[2])
        give, give_qty, get, get_qty = config.FIRE_EXCHANGE_OFFERS[idx]
    except (ValueError, IndexError):
        await cb.answer("❌ Нет такого обмена.", show_alert=True)
        return
    give_item = await db.get_item_by_name(give)
    get_item = await db.get_item_by_name(get)
    if not give_item or not get_item:
        await cb.answer("⚠️ Товар лавки не заведён. Сообщи хранителю.", show_alert=True)
        return
    if await _item_qty(uid, give) < give_qty:
        await cb.answer(f"❌ Нужно {give_qty} × {give}.", show_alert=True)
        return
    if not await db.remove_inventory_item(uid, give_item['id'], give_qty):
        await cb.answer("❌ Не удалось списать предметы.", show_alert=True)
        return
    await db.add_inventory_item(uid, get_item['id'], get_qty)
    await db.log_activity(uid, "firelab", f"Лавка: {give_qty} × {give} → {get_qty} × {get}")
    await cb.answer("🛍 Обмен готов!")
    await _exchange_screen(cb, uid, note=f"✅ Получено: {get_qty} × {_esc(get)}.")


@router.callback_query(F.data == "fireevent:go")
async def fire_event_go_cb(cb: CallbackQuery, state: FSMContext):
    """Вход пилота: проверки, оплата и первая развилка."""
    from database.db import get_user, user_is_tourist
    user = await get_user(cb.from_user.id)
    if not user:
        await cb.answer("❌ Сначала /start.", show_alert=True)
        return
    if await user_is_tourist(cb.from_user.id):
        await cb.answer("⛔ Вход только для граждан Нордхайма и легионеров.", show_alert=True)
        return

    from utils.states import is_place_blocked
    if await is_place_blocked(cb.from_user.id, "firelab"):
        await cb.answer("🍺 В таком состоянии в Лабиринт не пускают. "
                        "Загляни, когда пройдёт опьянение.", show_alert=True)
        return

    fee = int(getattr(config, "FIRE_EVENT_LAB_FEE", 32) or 0)
    if int(user['nordmarks'] or 0) < fee:
        await cb.answer(f"❌ Вход стоит {fee} НМ — не хватает.", show_alert=True)
        return
    already = await get_active_fire_lab_session(cb.from_user.id)
    if already:
        # незакрытая сессия — просто вернёмся в неё, повторно не платим
        await cb.answer("🔥 Ты уже внутри лабиринта.")
        await _paint_fork(cb, already, already['id'])
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
    text = (f"🔥 <b>Дни Пламенного Круговорота</b>\n"
            f"Вход оплачен: −{fee} НМ (заход {n}/{max_entries} за сутки).\n\n"
            + _fork_text(updated))
    await _fire_paint(cb, text=text, kb=_fork_kb(session_id), **(await _room_kw("fork")))


# ============================== БОЕВОЙ ЦИКЛ (Фаза 2) ==============================

async def _start_battle(cb, session, session_id: int, room: str, tier: int):
    """Начало боя: выбор врага, запись в сессию, отрисовка боевого экрана."""
    conn = await db.get_db()
    enemy = None
    if room == "boss":
        cur = await conn.execute("SELECT * FROM firelab_enemies WHERE key = ?", (FIRELAB_BOSS_KEY,))
        enemy = await cur.fetchone()
        if enemy:
            await conn.execute(
                "UPDATE fire_lab_sessions SET boss_encounters = boss_encounters + 1 "
                "WHERE id = ?", (session_id,))
            await conn.commit()
    if not enemy:
        obstacles = []
        for key in FIRELAB_ENEMY_KEYS:
            cur = await conn.execute("SELECT * FROM firelab_enemies WHERE key = ?", (key,))
            e = await cur.fetchone()
            if e:
                obstacles.append(e)
        if not obstacles:
            await _paint_fork(cb, session, session_id)
            return
        enemy = random.choice(obstacles)
    eng = _tier_enemy(enemy, tier)
    await _save_enemy(session_id, eng)
    await _paint_battle(cb, session, eng)


async def _save_enemy(session_id: int, eng: dict) -> None:
    conn = await db.get_db()
    await conn.execute(
        "UPDATE fire_lab_sessions SET enemy_json = ?, effects_json = ? WHERE id = ?",
        (json.dumps(eng, ensure_ascii=False), json.dumps({}, ensure_ascii=False), session_id))
    await conn.commit()


async def _save_sessions_effects(session_id: int, effects: dict) -> None:
    conn = await db.get_db()
    await conn.execute(
        "UPDATE fire_lab_sessions SET effects_json = ? WHERE id = ?",
        (json.dumps(effects, ensure_ascii=False), session_id))
    await conn.commit()


async def _get_enemy_state(session_id: int):
    """(enemy dict, effects dict) из сессии, если бой идёт."""
    conn = await db.get_db()
    cur = await conn.execute(
        "SELECT enemy_json, effects_json FROM fire_lab_sessions WHERE id = ?", (session_id,))
    row = await cur.fetchone()
    if not row or not row['enemy_json']:
        return None, {}
    try:
        enemy = json.loads(row['enemy_json'])
        effects = json.loads(row['effects_json'] or '{}')
    except Exception:
        return None, {}
    return enemy, effects


def _battle_text(session, enemy, effects: dict, log: str = "") -> str:
    fx = []
    if effects.get(FX_BLIND):
        fx.append(f"😵 Ослепление: {effects[FX_BLIND]}")
    if effects.get(FX_STUN):
        fx.append(f"💫 Оглушение: {effects[FX_STUN]}")
    if effects.get(FX_SLOW):
        fx.append(f"🕸 Замедление: {effects[FX_SLOW]} х. (-укл, +укл Хуба)")
    if effects.get(FX_BURN):
        burn = effects[FX_BURN]
        fx.append(f"🔥 Поджиг: −{burn.get('dmg')} HP/ход, {burn.get('rounds')} х.")
    if effects.get(FX_REGEN):
        rq = effects[FX_REGEN]
        fx.append(f"♻ Регенерация: +{'/'.join(str(t) for t in rq)} HP (тики)")
    fx_line = "\n".join("   • " + x for x in fx) or "   — нет"
    return (
        f"⚔️ <b>Бой: {_esc(enemy['name'])}</b>"
        + (" 👑 БОСС" if enemy.get('is_boss') else "") + "\n"
        f"💚 Враг: {enemy['hp']}/{enemy['hp_max']} HP"
        + (f" • 🛡 Броня: {enemy['armor']}" if int(enemy.get('armor') or 0) else "")
        + f" • 💨 Укл: {int(enemy.get('dodge') or 0)}%\n"
        f"💙 Ты: {int(session['hp'])}/{int(session['hp_max'])}\n"
        f"✨ Твои эффекты:\n{fx_line}\n"
        + (f"\n{log}\n" if log else "")
    )


async def _potions_labels(user_id: int) -> list:
    """Лечащие расходники из слотов potion1/potion2: [(slot, name, qty)]."""
    labels = []
    eq = await db.get_equipment(user_id)
    for slot in ("potion1", "potion2"):
        item_id = eq.get(slot)
        if not item_id:
            continue
        it = await db.get_item(item_id)
        if not it or int(it['heal'] or 0) <= 0:
            continue
        inv = await db.get_inventory_item(user_id, item_id)
        qty = int(inv['quantity'] or 0) if inv else 0
        if qty <= 0:
            continue
        labels.append((slot, it['name'], qty))
    return labels


async def _battle_kb(user_id: int, session_id: int) -> InlineKeyboardMarkup:
    """Кнопки боя: удар + зелья из слотов (если есть) + выход."""
    rows = [[InlineKeyboardButton(text="⚔️ Ударить",
                                  callback_data=f"fireevent:attack:{session_id}")]]
    for i in range(0, len(labels := await _potions_labels(user_id)), 2):
        rows.append([InlineKeyboardButton(
            text=f"🧪 {nm} (x{qty})",
            callback_data=f"fireevent:potion:{session_id}:{slot}")
            for slot, nm, qty in labels[i:i + 2]])
    rows.append([InlineKeyboardButton(text="🚪 Покинуть лабиринт",
                                      callback_data=f"fireevent:leave:{session_id}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def _paint_battle(cb, session, enemy, log: str = ""):
    kb = await _battle_kb(cb.from_user.id, int(session['id']))
    media = resolve_image_seasonal(enemy.get('photo_key')
                                   or "city/fire_scarecrow")
    await _fire_paint(
        cb, text=_battle_text(session, enemy,
                              json.loads(session['effects_json'] or '{}'), log),
        kb=kb,
        photo_id=enemy.get('image'),
        media_path=None if enemy.get('image') else media)


@router.callback_query(F.data.startswith("fireevent:attack:"))
async def fire_event_attack_cb(cb: CallbackQuery):
    parts = cb.data.split(":")
    session_id = int(parts[2])
    session = await _session_of(cb.from_user.id, session_id)
    if not session:
        return
    enemy, effects = await _get_enemy_state(session_id)
    if not enemy:
        await cb.answer("❌ Бой не найден — вернись на развилку.", show_alert=True)
        return
    log_lines = []
    # тик регенерации от расходников (FX_REGEN — очередь затухающих тиков)
    regen_q = effects.get(FX_REGEN)
    if regen_q:
        tick = int(regen_q[0] or 0)
        if tick > 0:
            healed = min(tick, int(session['hp_max']) - int(session['hp']))
            if healed > 0:
                session['hp'] = int(session['hp']) + healed
                log_lines.append(f"♻ Регенерация: +{healed} HP")
        effects[FX_REGEN] = regen_q[1:]
        if not effects[FX_REGEN]:
            effects.pop(FX_REGEN, None)
    # оглушение: пропуск хода
    if int(effects.get(FX_STUN) or 0) > 0:
        effects[FX_STUN] = int(effects.get(FX_STUN)) - 1
        if effects.get(FX_STUN, 0) <= 0:
            effects.pop(FX_STUN, None)
        log_lines.append("💫 Оглушение: ты пропускаешь ход!")
        session['hp'] = int(session['hp'])
        return await _after_player_tick(cb, session, session_id, enemy, effects,
                                        "\n".join(log_lines))
    # ослепление: 50% промах; тик уменьшается всегда
    if int(effects.get(FX_BLIND) or 0) > 0:
        effects[FX_BLIND] = int(effects.get(FX_BLIND)) - 1
        if effects.get(FX_BLIND, 0) <= 0:
            effects.pop(FX_BLIND, None)
        if random.random() < 0.5:
            log_lines.append("😵 Ослепление: удар ушёл в пустоту!")
            return await _after_player_tick(cb, session, session_id, enemy, effects,
                                            "\n".join(log_lines))
    # уклонение врага
    if random.random() * 100 < float(enemy.get('dodge') or 0):
        log_lines.append("💨 Враг уклонился!")
        return await _after_player_tick(cb, session, session_id, enemy, effects,
                                        "\n".join(log_lines))

    # урон игрока: base + weapon, в диапазоне lo..hi
    from utils.combat_model import pilot_combat_stats
    st = await pilot_combat_stats(cb.from_user.id)
    # тик вражеского DoT (кровотечение/поджиг от нашего оружия) — до удара
    dot = enemy.get('dot')
    if dot and int(dot.get('rounds') or 0) > 0 and int(enemy.get('hp') or 0) > 0:
        dmg_dot = int(dot.get('dmg') or 0)
        if dmg_dot > 0:
            enemy['hp'] = max(0, int(enemy['hp']) - dmg_dot)
            dot['rounds'] = int(dot.get('rounds') or 1) - 1
            if dot['rounds'] <= 0:
                enemy.pop('dot', None)
            eff_names = {"bleed": "🩸 Кровотечение", "burn": "🔥 Поджиг",
                         "poison": "☠️ Отравление", "frostbite": "🧊 Обморожение"}
            log_lines.append(
                f"{eff_names.get(dot.get('kind'), 'DoT')} добирает врага: "
                f"−{dmg_dot} HP ({enemy['hp']}/{enemy['hp_max']})")
    lo, hi = st.get('base_dmg') or (0, 0)
    w = st.get('weapon_damage') or 0
    if isinstance(w, tuple):
        w_lo, w_hi = w
    else:
        w_lo = w_hi = int(w or 0)
    dmg = random.randint(int(lo) + w_lo, max(int(lo) + w_lo, int(hi) + w_hi))
    # крит
    if float(st.get('crit_chance') or 0) > 0 and random.random() * 100 < float(st['crit_chance']):
        dmg = int(dmg * float(st.get('crit_mult') or 1.4))
        log_lines.append("💥 Крит!")
    # благословение: +Х% урона
    if int(session.get('blessing') or 0):
        pct = float(getattr(config, "FIRE_TREE_DMG_BONUS_PCT", 15) or 0)
        dmg = int(dmg * (1 + pct / 100.0))
        log_lines.append("🔥 Благословение усилило удар.")
    # реген благословения — на каждом ударе игрока, в том числе если броня поглотила урон
    if int(session.get('blessing') or 0):
        regen = int(getattr(config, "FIRE_TREE_REGEN_HP", 1) or 0)
        session['hp'] = min(int(session['hp_max']), int(session['hp']) + regen)
        log_lines.append(f"🌿 Благословение: +{regen} HP")
    # праздничный сет (3 одежды + оружие): постоянная регенерация за ход
    fire_set = await db.get_fire_set_status(cb.from_user.id)
    if fire_set['regen'] and int(session['hp']) < int(session['hp_max']):
        session['hp'] = min(int(session['hp_max']), int(session['hp']) + fire_set['regen'])
        log_lines.append(f"🧥 Праздничный сет: +{fire_set['regen']} HP")
    eff = max(0, int(dmg) - int(enemy.get('armor') or 0))
    if eff <= 0:
        log_lines.append("🛡 Броня врага поглотила удар!")
        return await _after_player_tick(cb, session, session_id, enemy, effects,
                                        "\n".join(log_lines))
    enemy['hp'] = max(0, int(enemy['hp']) - eff)
    log_lines.append(f"💥 Ты нанёс {eff} урона (враг {enemy['hp']}/{enemy['hp_max']})")
    # оружие: шанс DoT на врага (кровотечение Вил, поджиг Тродce), если враг жив
    if int(enemy['hp']) > 0:
        wep = await db.get_equipped_weapon(cb.from_user.id)
        weff = (wep.get('weapon_effect') or "").strip() if wep else ""
        wch = int((wep or {}).get('weapon_effect_chance') or 0)
        wdmg = int((wep or {}).get('weapon_effect_dmg') or 0)
        if weff in ("bleed", "burn", "poison", "frostbite") and wch and wdmg \
                and random.randint(1, 100) <= wch:
            enemy['dot'] = {"kind": weff, "dmg": wdmg, "rounds": 3}
            fx_word = {"bleed": "🩸 Кровотечение:", "burn": "🔥 Поджог:",
                       "poison": "☠️ Отравление:", "frostbite": "🧊 Обморожение:"}[weff]
            log_lines.append(
                f"{fx_word} враг получит −{wdmg} HP до удара (3 хода)")
    await _after_player_tick(cb, session, session_id, enemy, effects,
                             "\n".join(log_lines))


@router.callback_query(F.data.startswith("fireevent:potion:"))
async def fire_event_potion_cb(cb: CallbackQuery, confirmed: bool = False):
    """Зелье в бою Лабиринта (слоты potion1/potion2, как в городе)."""
    parts = cb.data.split(":")
    session_id = int(parts[2])
    slot = parts[3]
    session = await _session_of(cb.from_user.id, session_id)
    if not session:
        return
    from bot.handlers.dungeon import battle_state_block_message
    blk = await battle_state_block_message(cb.from_user.id)
    if not blk:
        _enemy_now, fx_now = await _get_enemy_state(session_id)
        if int(fx_now.get(FX_STUN) or 0) > 0:
            blk = "💫 Ты оглушён: тело не слушается. Зелья будут доступны, когда оглушение пройдёт."
    if blk:
        await cb.answer(blk, show_alert=True)
        return
    eq = await db.get_equipment(cb.from_user.id)
    item_id = eq.get(slot)
    if not item_id:
        await cb.answer("❌ Слот пуст.", show_alert=True)
        return
    it = await db.get_item(item_id)
    if not it or int(it['heal'] or 0) <= 0:
        await cb.answer("❌ Это не лечит.", show_alert=True)
        return
    inv = await db.get_inventory_item(cb.from_user.id, item_id)
    if not inv or int(inv['quantity'] or 0) <= 0:
        await cb.answer("❌ Зелий этого вида не осталось.", show_alert=True)
        return
    if not confirmed and int(session['hp']) >= int(session['hp_max']):
        await cb.answer()
        await cb.message.answer(
            f"🧪 HP уже полное ({int(session['hp'])}/{int(session['hp_max'])}). "
            f"Точно применить «{_esc(it['name'])}»? Расходник будет потрачен.",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ Да, применить",
                                      callback_data=f"fireevent:potionok:{session_id}:{slot}"),
                 InlineKeyboardButton(text="❌ Нет",
                                      callback_data="fireevent:potioncancel")],
            ]))
        return
    if not await db.remove_inventory_item(cb.from_user.id, item_id, 1):
        await cb.answer("❌ Зелья не списалось.", show_alert=True)
        return
    heal_base = int(it['heal'] or 0)
    pct = await db.get_player_heal_bonus_pct(cb.from_user.id)
    pct += await db.get_achievement_bonus(cb.from_user.id, "cooking", "heal_pct")
    pct += await db.get_achievement_bonus(cb.from_user.id, "elixir", "heal_pct")
    heal = max(1, round(heal_base * (100 + pct) / 100))
    new_hp = min(int(session['hp_max']), int(session['hp']) + heal)
    conn = await db.get_db()
    await conn.execute(
        "UPDATE fire_lab_sessions SET hp = ?, last_active_at = datetime('now') "
        "WHERE id = ?", (new_hp, session_id))
    await conn.commit()
    await db.log_activity(cb.from_user.id, "firelab",
                          f"Зелье в бою: «{it['name']}» (+{heal} HP)")
    bonus_note = f" (+{pct}% от экипа и мастерства)" if pct else ""
    session = await db.get_active_fire_lab_session(cb.from_user.id)
    enemy, effects = await _get_enemy_state(session_id)
    if not enemy:
        await cb.answer()
        return
    # затухающая регенерация (items.regen): тики на N следующих ходов игрока
    regen_note = ""
    rpct = int(it['regen'] or 0) if 'regen' in it.keys() else 0
    if rpct > 0 and int(session['hp']) < int(session['hp_max']):
        rturns = int(it['regen_turns'] or 0) if 'regen_turns' in it.keys() else 0
        from bot.handlers.dungeon import regen_amounts, REGEN_TURNS
        ticks = regen_amounts(heal, rpct, turns=(rturns or REGEN_TURNS))
        if ticks:
            effects[FX_REGEN] = ticks
            regen_note = (f"\n♻ Регенерация: +{'/'.join(str(t) for t in ticks)} "
                          f"HP на {len(ticks)} ходов")
    # суточный баф уворота (items.dodge_buff_pct): первый раз активирует,
    # повторное применение в течение суток НЕ продлевает
    dbuff = int(it['dodge_buff_pct'] or 0) if 'dodge_buff_pct' in it.keys() else 0
    dbuff_note = ""
    if dbuff > 0:
        if await db.activate_dodge_buff(cb.from_user.id, dbuff):
            dbuff_note = f"\n🪁 Уворот +{dbuff}% на сутки!"
        elif await db.dodge_buff_active(cb.from_user.id):
            dbuff_note = f"\n🪁 Баф уворота +{dbuff}% уже активен — не продлевается."
    # зелье — это действие: враг отвечает (обычный ход)
    log = (f"🧪 «{_esc(it['name'])}» (+{heal} HP)\n"
           f"💙 Ты восстановил: ×{new_hp}/{int(session['hp_max'])}{bonus_note}"
           + regen_note + dbuff_note)
    await _after_player_tick(cb, session, session_id, enemy, effects, log)


@router.callback_query(F.data.startswith("fireevent:potionok:"))
async def fire_event_potion_ok_cb(cb: CallbackQuery):
    """Подтверждённое зелье при полном HP (кнопка «Да, применить»)."""
    await fire_event_potion_cb(cb, confirmed=True)


@router.callback_query(F.data == "fireevent:potioncancel")
async def fire_event_potion_cancel_cb(cb: CallbackQuery):
    await cb.answer("Отменено.")
    try:
        await cb.message.delete()
    except Exception:
        pass


async def _after_player_tick(cb, session, session_id: int, enemy, effects, player_log: str):
    """Запись после удара игрока + ход врага + проверка исходов."""
    conn = await db.get_db()
    # победа над врагом
    if int(enemy['hp']) <= 0:
        await conn.execute("UPDATE fire_lab_sessions SET hp = ?, enemy_json = NULL, "
                           "effects_json = '{}' WHERE id = ?",
                           (int(session['hp']), session_id))
        if enemy.get('is_boss'):
            await conn.execute(
                "UPDATE fire_lab_sessions SET boss_defeated = boss_defeated + 1 "
                "WHERE id = ?", (session_id,))
        await conn.commit()
        updated = await db.get_active_fire_lab_session(cb.from_user.id)
        # Фаза 5: лут врага (drops × Тир «Огненного эха»)
        loot_notes = []
        for d in _roll_enemy_loot(enemy):
            try:
                await db.add_inventory_item(cb.from_user.id, int(d['item_id']),
                                            int(d.get('qty') or 1))
                it = await db.get_item(int(d['item_id']))
                it_name = it['name'] if it else f"#{d['item_id']}"
                loot_notes.append(f"🎁 «{it_name}» ×{int(d.get('qty') or 1)}")
            except Exception:
                pass
        if loot_notes:
            await db.log_activity(cb.from_user.id, "firelab",
                                  f"Лут с {enemy['name']}: "
                                  + "; ".join(loot_notes))
        loot_text = ("\n\n🎉 <b>Добыча:</b>\n" + "\n".join(loot_notes)
                     if loot_notes else "")
        await cb.answer("💀 Враг повержен!", show_alert=True)
        text = (f"💀 <b>{_esc(enemy['name'])} повержен!</b>{loot_text}\n\n")
        await _paint_fork(cb, updated, session_id, prefix=text)
        return
    # фиксация врага и эффектов
    await conn.execute("UPDATE fire_lab_sessions SET enemy_json = ? WHERE id = ?",
                       (json.dumps(enemy, ensure_ascii=False), session_id))
    await _save_sessions_effects(session_id, effects)
    await conn.commit()
    session = await db.get_active_fire_lab_session(cb.from_user.id)

    # --- ход врага ---
    hp_now = int(session['hp'])
    log_lines = []
    burn = effects.get(FX_BURN)
    if burn:
        dmg_burn = int(burn.get('dmg') or 2)
        hp_now = max(0, hp_now - dmg_burn)
        log_lines.append(f"🔥 Поджиг: −{dmg_burn} HP ({burn.get('rounds')} х. осталось)")
        burn['rounds'] = int(burn.get('rounds') or 0) - 1
        if burn['rounds'] <= 0:
            effects.pop(FX_BURN, None)
    # удар врага (с учётом замедления Хуба)
    dodge_player = 0.0
    st = None
    try:
        from utils.combat_model import pilot_combat_stats
        st = await pilot_combat_stats(cb.from_user.id)
        dodge_player = float(st.get('dodge') or 0)
    except Exception:
        dodge_player = 0.0
    if int(effects.get(FX_SLOW) or 0) > 0:
        dodge_player = max(0.0, dodge_player - float(getattr(config, "FIRE_LAB_HUB_PLAYER_DODGE_PENALTY", 35) or 0))
    # тикаем замедление у игрока (отнимаем в конце хода, после удара врага)
    if random.random() * 100 < dodge_player:
        log_lines.append("💨 Ты увернулся от удара врага!")
    else:
        from utils.combat_model import armor_hit, _enemy_pierce_roll
        enemy_dmg = random.randint(int(enemy.get('dmg_min') or 0), int(enemy.get('dmg_max') or 0))
        armor_player = 0
        try:
            armor_player = int((st or {}).get('armor') or 0)
        except Exception:
            armor_player = 0
        hit = armor_hit(enemy_dmg, armor_player, _enemy_pierce_roll(enemy), minimum=0)
        eff = hit['damage']
        blocked = hit['armor_blocked']
        hp_now = max(0, hp_now - eff)
        if hit['pierced']:
            log_lines.append(f"🗡 Враг пробивает броню! Удар на {eff} урона")
        elif blocked > 0:
            log_lines.append(f"⚔️ Враг бьёт на {enemy_dmg} — 🛡 броня поглотила {blocked}, −{eff} HP")
        else:
            log_lines.append(f"⚔️ Враг бьёт на {eff} урона")
        if eff <= 0:
            log_lines[-1] = f"⚔️ Враг бьёт на {enemy_dmg} — 🛡 броня поглотила удар полностью!"
    # фирменные эффекты врага (только если игрок жив)
    fx_end = ""
    if hp_now > 0 and log_lines and "Ты увернулся" not in log_lines[-1]:
        key = enemy.get('key')
        if key == "scarecrow" and random.random() < float(getattr(config, "FIRE_LAB_SCARECROW_BLIND_P", 0.15)):
            effects[FX_BLIND] = effects.get(FX_BLIND, 0) + 1
            fx_end = "\n🌾 Сено в лицо — ты ослеплён!"
        if key == "crow" and random.random() < float(getattr(config, "FIRE_LAB_CROW_BLIND_P", 0.15)):
            effects[FX_BLIND] = effects.get(FX_BLIND, 0) + 1
            fx_end = "\n🐦 Ворон ослепил тебя!"
        if key == "apple_child" and random.random() < float(getattr(config, "FIRE_LAB_APPLE_STUN_P", 0.10)):
            effects[FX_STUN] = effects.get(FX_STUN, 0) + 1
            fx_end = "\n🍎 Спелое яблоко — ты оглушён!"
        if key == "hub" and random.random() < float(getattr(config, "FIRE_LAB_HUB_SLOW_P", 0.25)):
            effects[FX_SLOW] = int(getattr(config, "FIRE_LAB_HUB_SLOW_ROUNDS", 3) or 3)
            # Хуб чуть добавляет уклонение сам
            try:
                enemy['dodge'] = float(enemy.get('dodge') or 0) + float(getattr(config, "FIRE_LAB_HUB_ENEMY_DODGE_BONUS", 10) or 0)
            except Exception:
                pass
            fx_end = "\n🕸 Хуб опутывает паутиной: замедление (-укл, +укл Хуба)!"
        if key == FIRELAB_BOSS_KEY and hp_now > 0 and random.random() < float(
                getattr(config, "FIRE_LAB_BOSS_BURN_P", 0.25)):
            effects[FX_BURN] = {'dmg': int(getattr(config, "FIRE_LAB_BOSS_BURN_DMG", 2) or 2),
                                'rounds': int(getattr(config, "FIRE_LAB_BOSS_BURN_ROUNDS", 3) or 3)}
            fx_end = "\n🔥 Мистер Тыква поджигает: −2 HP/ход на 3 хода!"
    # тик замедления
    if int(effects.get(FX_SLOW) or 0) > 0:
        effects[FX_SLOW] = int(effects[FX_SLOW]) - 1
        if effects.get(FX_SLOW, 0) <= 0:
            effects.pop(FX_SLOW, None)
    if hp_now <= 0:
        await conn.execute("UPDATE fire_lab_sessions SET hp = 0 WHERE id = ?", (session_id,))
        await _save_sessions_effects(session_id, effects)
        await conn.commit()
        return await _player_death(cb, session_id)
    await conn.execute(
        "UPDATE fire_lab_sessions SET hp = ?, enemy_json = ?, effects_json = ? WHERE id = ?",
        (hp_now, json.dumps(enemy, ensure_ascii=False),
         json.dumps(effects, ensure_ascii=False), session_id))
    await conn.commit()
    session = await db.get_active_fire_lab_session(cb.from_user.id)
    await _paint_battle(cb, session, enemy, log=player_log + "\n" + "\n".join(log_lines) + fx_end)


async def _player_death(cb, session_id: int):
    await db.end_fire_lab_session(session_id, 'dead')
    await cb.answer("💀 Ты пал в Огненном Лабиринте!", show_alert=True)
    text = ("💀 <b>Ты пал в Огненном Лабиринте.</b>\n"
            "Пламя погасило твою искру — но Круговорот живуч, и попытка "
            "ценна. Заходы за сутки можно продолжать за НМ.")
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 В город", callback_data="city:menu")],
    ])
    await _fire_paint(cb, text=text, kb=kb,
                      media_path=resolve_image(
                          getattr(config, "FIRE_LAB_FORK_KEY", "city/fire_maze")))
