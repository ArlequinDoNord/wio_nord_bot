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
import random

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

# Ключи врагов Огненного Лабиринта (firelab_enemies).
FIRELAB_ENEMY_KEYS = ("scarecrow", "apple_child", "crow", "hub")
FIRELAB_BOSS_KEY = "pumpkin_boss"

# Ключи эффектов на игрока (хранятся в effects_json сессии).
FX_BLIND = "blind"        # ослепление: часть ударов промахивается
FX_STUN = "stun"          # оглушение: игрок пропускает ход
FX_SLOW = "slow"          # замедление: сильно снижает уклон игрока, чуть +уклон врага
FX_BURN = "burn"          # поджиг: −N HP/ход


# ==================== ВСТРЕЧИ И БРОСКИ РАЗВИЛКИ (Фаза 2/3) ====================

async def _roll_room(user_id: int, session, path: str, history: list) -> str:
    """Бросок комнаты после выбора пути. Возвращает название комнаты:
    'tree'/'well'/'chest'/'boss'/'enemy'/'empty'."""
    tree_visits = int(session['tree_visits'] or 0)
    well_visits = int(session['well_visits'] or 0)
    chest_visits = int(session['chest_visits'] or 0)
    boss_encounters = int(session['boss_encounters'] or 0)
    steps = int(session['steps'] or 0)

    tree_max = int(getattr(config, "FIRE_LAB_TREE_MAX", 1) or 1)
    well_max = int(getattr(config, "FIRE_LAB_WELL_MAX", 3) or 3)
    chest_max = int(getattr(config, "FIRE_LAB_CHEST_MAX", 2) or 2)
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
    if chest_visits < chest_max and random.random() < float(getattr(config, "FIRE_LAB_P_CHEST", 0.10)):
        return "chest"

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
    """Словарь врага со сдвигом по Тиру Огненного эха (HP +bonus)."""
    return {
        'key': e['key'], 'name': e['name'],
        'hp': int(e['hp']) + db.firelab_tier_enemy_bonus(tier),
        'hp_max': int(e['hp']) + db.firelab_tier_enemy_bonus(tier),
        'armor': int(e.get('armor') or 0),
        'dodge': float(e.get('dodge') or 0),
        'dmg_min': int(e.get('dmg_min') or 0),
        'dmg_max': int(e.get('dmg_max') or 0),
        'is_boss': e['key'] == FIRELAB_BOSS_KEY,
    }


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
    room = await _roll_room(cb.from_user.id, updated, path, history)
    # счётчики посещенийς особых комнат проводятся при их отрисовке (Ф3).
    if room == "empty":
        await cb.message.answer(_fork_text(updated),
                                reply_markup=_fork_kb(session_id),
                                parse_mode="HTML")
        return
    if room in ("enemy", "boss"):
        await _start_battle(cb, updated, session_id, room, tier=await db.get_fire_lab_tier(cb.from_user.id))
        return
    # особые комнаты: Фаза 3 (Колодец/Древо/Сундук) — сейчас заглушка
    await cb.message.answer(
        f"✨ Здесь откроется особая комната (Фаза 3): {room}.\n"
        f"Комнаты Колодца, Древа Огня и Сундука откроются на следующей фазе — "
        f"пока возвращаемся на развилку.",
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
            await cb.message.answer(_fork_text(session), reply_markup=_fork_kb(session_id),
                                    parse_mode="HTML")
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


def _battle_kb(session_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚔️ Ударить",
                              callback_data=f"fireevent:attack:{session_id}")],
        [InlineKeyboardButton(text="🚪 Покинуть лабиринт",
                              callback_data=f"fireevent:leave:{session_id}")],
    ])


async def _paint_battle(cb, session, enemy, log: str = ""):
    try:
        await cb.message.edit_text(
            _battle_text(session, enemy, json.loads(session['effects_json'] or '{}'), log),
            reply_markup=_battle_kb(int(session['id'])),
            parse_mode="HTML")
    except Exception:
        await cb.message.answer(
            _battle_text(session, enemy, json.loads(session['effects_json'] or '{}'), log),
            reply_markup=_battle_kb(int(session['id'])),
            parse_mode="HTML")


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
    eff = max(0, int(dmg) - int(enemy.get('armor') or 0))
    if eff <= 0:
        log_lines.append("🛡 Броня врага поглотила удар!")
        return await _after_player_tick(cb, session, session_id, enemy, effects,
                                        "\n".join(log_lines))
    enemy['hp'] = max(0, int(enemy['hp']) - eff)
    log_lines.append(f"💥 Ты нанёс {eff} урона (враг {enemy['hp']}/{enemy['hp_max']})")
    # реген благословения
    if int(session.get('blessing') or 0):
        regen = int(getattr(config, "FIRE_TREE_REGEN_HP", 1) or 0)
        session['hp'] = min(int(session['hp_max']), int(session['hp']) + regen)
        log_lines.append(f"🌿 Благословение: +{regen} HP")
    await _after_player_tick(cb, session, session_id, enemy, effects,
                             "\n".join(log_lines))


async def _after_player_tick(cb, session, session_id: int, enemy, effects, player_log: str):
    """Запись после удара игрока + ход врага + проверка исходов."""
    conn = await db.get_db()
    # победа над врагом
    if int(enemy['hp']) <= 0:
        await conn.execute("UPDATE fire_lab_sessions SET enemy_json = NULL, "
                           "effects_json = '{}' WHERE id = ?", (session_id,))
        if enemy.get('is_boss'):
            await conn.execute(
                "UPDATE fire_lab_sessions SET boss_defeated = boss_defeated + 1 "
                "WHERE id = ?", (session_id,))
        await conn.commit()
        updated = await db.get_active_fire_lab_session(cb.from_user.id)
        # TODO(Ф3/Ф5): лут врага (drops × Тир) — опишет владелец
        await cb.answer("💀 Враг повержен!", show_alert=True)
        text = f"💀 <b>{_esc(enemy['name'])} повержен!</b>\n\n" + _fork_text(updated)
        try:
            await cb.message.edit_text(text, reply_markup=_fork_kb(session_id),
                                       parse_mode="HTML")
        except Exception:
            await cb.message.answer(text, reply_markup=_fork_kb(session_id),
                                    parse_mode="HTML")
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
        enemy_dmg = random.randint(int(enemy.get('dmg_min') or 0), int(enemy.get('dmg_max') or 0))
        armor_player = 0
        try:
            armor_player = int((st or {}).get('armor') or 0)
        except Exception:
            armor_player = 0
        blocked = min(enemy_dmg, armor_player)
        eff = max(0, enemy_dmg - armor_player)
        hp_now = max(0, hp_now - eff)
        if blocked > 0:
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
    try:
        await cb.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except Exception:
        await cb.message.answer(text, reply_markup=kb, parse_mode="HTML")
