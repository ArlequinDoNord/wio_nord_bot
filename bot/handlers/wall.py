"""Стена изречений — доска объявлений города.

Лимит 40 символов; 4 изречения в сутки бесплатно, далее платные ступени
(3×30 → 3×90 → 3×200 НМ), после 13-го — жёсткий стоп. Сутки считаются по МСК.
Сообщения видны всем игрокам; админ (can_manage_users) может удалить любое;
при удалении платного изречения автору возвращается ⅓ цены.
"""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import (
    WALL_TEXT_MAX_LEN, WALL_FREE_PER_DAY, WALL_PAID_STEPS, WALL_REVIEW_TOTAL,
    WALL_PAGE_SIZE,
)
from database.db import (
    get_user, count_wall_posts_today, wall_post_tier, add_wall_post,
    get_wall_posts, get_wall_post, count_wall_posts, delete_wall_post,
    log_activity,
)
from utils.helpers import plural_nordmark, is_main_menu_text
from utils.permissions import has_permission, log_action
from keyboards.keyboards import wall_keyboard, cancel_keyboard

router = Router()


class WallWrite(StatesGroup):
    waiting_text = State()


def _wall_footer(user_id: int, count_today: int, user: dict) -> str:
    """Строка лимитов на сегодня: сколько осталось и по какой цене."""
    if count_today >= WALL_REVIEW_TOTAL:
        return f"⛔ Сегодня стена заполнена: лимит {WALL_REVIEW_TOTAL} изречений исчерпан. Новые — с завтра."
    free_left = max(0, WALL_FREE_PER_DAY - count_today)
    if free_left > 0:
        return f"🆓 Бесплатных сегодня осталось: {free_left}"
    paid_made = count_today - WALL_FREE_PER_DAY
    next_price = 0
    remaining = paid_made
    for quota, price in WALL_PAID_STEPS:
        if remaining < quota:
            next_price = price
            break
        remaining -= quota
    if next_price:
        balance = user['nordmarks'] if user else 0
        return f"💰 Следующее изречение: {next_price} НМ. Баланс: {plural_nordmark(balance)}"
    return f"⛔ Сегодня стена заполнена: лимит {WALL_REVIEW_TOTAL} изречений исчерпан. Новые — с завтра."


async def _show_wall(sender, state: FSMContext, page: int = 0):
    """Показать страницу стены (текст + клавиатура).

    sender: Message или CallbackQuery (у обоих есть .from_user.id;
    текст шлём через .message.answer, а у Message — .answer).
    """
    try:
        await state.clear()
    except Exception:
        pass
    user_id = sender.from_user.id
    total = await count_wall_posts()
    rows = await get_wall_posts(page, WALL_PAGE_SIZE)
    manage = await has_permission(user_id, "can_manage_users")
    ids = [r['id'] for r in rows]

    if not total:
        text = "🧱 СТЕНА ИЗРЕЧЕНИЙ\n\nПока пусто — будь первым, кто оставит своё изречение!"
    else:
        lines = ["🧱 СТЕНА ИЗРЕЧЕНИЙ"]
        for r in rows:
            author = _author_label(r)
            price_tag = ""
            if r['cost'] > 0:
                price_tag = f" · {r['cost']} НМ"
            lines.append(
                f"\n💬 {r['text']} "
                f"\n   — {author}{price_tag} · №{r['id']} · {_post_date_short(r['created_at'])}"
            )
        # показать лимиты автора запроса
        user = await get_user(user_id)
        cnt = await count_wall_posts_today(user_id)
        lines.append(f"\n{_wall_footer(user_id, cnt, user)}")
        text = "\n".join(lines)

    if not hasattr(sender, "message"):  # Message (у Callback есть .message)
        sent = await sender.answer(text, reply_markup=wall_keyboard(
            page=page, total_posts=total, post_ids=ids,
            is_admin=manage, can_manage=manage,
        ))
    else:  # CallbackQuery
        sent = await sender.message.answer(text, reply_markup=wall_keyboard(
            page=page, total_posts=total, post_ids=ids,
            is_admin=manage, can_manage=manage,
        ))
    try:
        await state.update_data(wall_active_msg=getattr(sent, "message_id", None))
    except Exception:
        pass


def _author_label(r: dict) -> str:
    callsign = (r.get('callsign') or '').strip()
    username = (r.get('username') or '').strip()
    if callsign:
        return callsign
    if username:
        return f"@{username}"
    first = (r.get('first_name') or '').strip()
    last = (r.get('last_name') or '').strip()
    return (f"{first} {last}").strip() or "Неизвестный"


def _post_date_short(created_at) -> str:
    """'2026-09-22 07:36:12' → '22.09 07:36' (UTC) — короткая подпись изречения."""
    if not created_at:
        return "—"
    try:
        dt = str(created_at).replace("T", " ").replace("Z", "").strip()
        date_part, _, time_part = dt.partition(" ")
        d = date_part.split("-")
        if len(d) >= 3:
            dd = d[2]
            mm = d[1]
        else:
            return str(created_at)
        if time_part:
            hhmm = ":".join(time_part.split(":")[:2])
            return f"{dd}.{mm} {hhmm}"
        return f"{dd}.{mm}"
    except Exception:
        return str(created_at)


@router.message(F.text == "🧱 Стена изречений")
async def wall_open_text(message: Message, state: FSMContext):
    await state.clear()
    await _show_wall(message, state, page=0)


@router.callback_query(F.data == "wall:view")
async def wall_view(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await _show_wall(callback, state, page=0)


@router.callback_query(F.data.regexp(r"^wall:page:\d+$"))
async def wall_page(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    active = data.get('wall_active_msg')
    if active is None or getattr(callback.message, "message_id", None) != active:
        await callback.message.answer(
            "⚠️ Это устаревшее сообщение стены. Открой стену заново, чтобы продолжить листать."
        )
        return
    page = int(callback.data.split(":")[2])
    await _show_wall(callback, state, page=page)


@router.callback_query(F.data == "wall:write")
async def wall_write_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    user = await get_user(callback.from_user.id)
    cnt = await count_wall_posts_today(callback.from_user.id)
    footer = _wall_footer(callback.from_user.id, cnt, user)
    if footer.startswith("⛔"):
        await callback.message.answer(f"❌ {footer}")
        return
    await state.set_state(WallWrite.waiting_text)
    await callback.message.answer(
        f"✍️ Оставь своё изречение (до {WALL_TEXT_MAX_LEN} символов):\n\n{footer}",
        reply_markup=cancel_keyboard()
    )


@router.message(WallWrite.waiting_text, F.text, ~F.text.func(is_main_menu_text))
async def wall_write_text(message: Message, state: FSMContext):
    text = message.text.strip()
    if len(text) > WALL_TEXT_MAX_LEN:
        cnt = await count_wall_posts_today(message.from_user.id)
        user = await get_user(message.from_user.id)
        await message.answer(
            f"❌ Слишком длинно: {len(text)} символов, лимит {WALL_TEXT_MAX_LEN}.\n"
            f"\n{_wall_footer(message.from_user.id, cnt, user)}"
        )
        return
    result = await add_wall_post(message.from_user.id, text)
    await state.clear()
    if result is None or result.get('post_id') is None:
        if result and result.get('need_nm'):
            await message.answer(
                "❌ Не хватает Нордмарок для платного изречения "
                f"(нужно {result.get('cost')} НМ)."
            )
        else:
            await message.answer("❌ Лимит изречений на сегодня исчерпан. Попробуй завтра.")
        return
    cost = result.get('cost', 0)
    parts = ["✅ Изречение отправлено на стену!"]
    if cost > 0:
        parts.append(f"Списано {cost} {plural_nordmark(cost)}.")
    parts.append("Свежие записи — в городе: «🧱 Стена изречений».")
    await message.answer("\n".join(parts))
    await log_activity(message.from_user.id, "wall_post", text[:60])


@router.callback_query(F.data.regexp(r"^wall:delete:\d+$"))
async def wall_delete(callback: CallbackQuery, state: FSMContext):
    """Админ-удаление: can_manage_users. Платное изречение возвращает ⅓ автору."""
    await callback.answer()
    actor = callback.from_user.id
    can_manage = await has_permission(actor, "can_manage_users")
    if not can_manage:
        await callback.message.answer("❌ Удалять изречения могут только админы (can_manage_users).")
        return
    post_id = int(callback.data.split(":")[2])
    res = await delete_wall_post(post_id)
    if not res:
        await callback.message.answer("❌ Изречение уже удалено.")
        return
    parts = [f"🗑 Изречение #{post_id} удалено."]
    if res['refund'] > 0:
        parts.append(f"Автору возвращено {res['refund']} НМ (⅓ от {res['cost']}).")
    await callback.message.answer("\n".join(parts))
    await log_action(actor, "wall_delete", res['author_id'], f"post #{post_id}, refund {res['refund']}")


__all__ = ["router"]