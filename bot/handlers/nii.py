"""НИИ Северной Кибернетики и кремниевых систем — здание обратной связи.

Любой пилот может оставить жалобу или запрос (до 2 в сутки, до 2000 символов,
одна картинка). О новом обращении оповещаются Хранители и супер-админы;
они же могут прочитать все обращения в здании и закрыть их.
"""

from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from database.db import (
    get_user, count_nii_reports_today, add_nii_report, get_nii_report,
    get_my_nii_reports, get_all_nii_reports, set_nii_report_status,
    nii_notify_ids, user_has_status_tag, log_activity,
    NII_DAILY_LIMIT,
)
from utils.helpers import edit_or_replace, is_main_menu_text
from utils.permissions import is_admin
from utils.notify import player_display

router = Router()

NII_TEXT_MAX_LEN = 2000


class NiiWrite(StatesGroup):
    text = State()
    photo = State()


def _nii_main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✍️ Оставить жалобу / запрос", callback_data="nii:write")],
        [InlineKeyboardButton(text="📜 Мои обращения", callback_data="nii:mine")],
        [InlineKeyboardButton(text="🏠 В меню города", callback_data="city:menu")],
    ])


def _nii_admin_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✍️ Оставить жалобу / запрос", callback_data="nii:write")],
        [InlineKeyboardButton(text="📜 Мои обращения", callback_data="nii:mine")],
        [InlineKeyboardButton(text="📥 Все обращения", callback_data="nii:all")],
        [InlineKeyboardButton(text="🏠 В меню города", callback_data="city:menu")],
    ])


async def nii_menu(callback: CallbackQuery):
    """Вход в здание НИИ."""
    await callback.answer()
    user_id = callback.from_user.id
    used = await count_nii_reports_today(user_id)
    left = max(0, NII_DAILY_LIMIT - used)
    text = (
        "🔬 НИИ Северной Кибернетики и кремниевых систем\n"
        "────────────────────────\n"
        "Институт кремниевых систем и кибернетики Нордхайма.\n"
        "Здесь принимают жалобы и запросы на доработку бота.\n\n"
        f"📮 Сегодня можно отправить ещё: {left} из {NII_DAILY_LIMIT}.\n"
        "Обращение видно Хранителям: они прочтут, разберутся и, "
        "если нужно, ответят в чате."
    )
    kb = _nii_admin_keyboard() if await _nii_can_view_all(user_id) else _nii_main_keyboard()
    await edit_or_replace(callback.message, text, kb)


async def _nii_can_view_all(user_id: int) -> bool:
    """Доступ к списку всех обращений: Хранитель или любой админ."""
    if await is_admin(user_id):
        return True
    return await user_has_status_tag(user_id, "keeper")


@router.callback_query(F.data == "nii:write")
async def nii_write_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    user_id = callback.from_user.id
    used = await count_nii_reports_today(user_id)
    left = NII_DAILY_LIMIT - used
    if left <= 0:
        await callback.message.answer(
            f"🚫 Суточный лимит обращений исчерпан ({NII_DAILY_LIMIT} в сутки). "
            f"Новое можно отправить завтра."
        )
        return
    await state.set_state(NiiWrite.text)
    await callback.message.answer(
        "📮 НОВОЕ ОБРАЩЕНИЕ\n\n"
        f"Опиши проблему или запрос (до {NII_TEXT_MAX_LEN} символов).\n"
        f"Осталось сегодня: {left} из {NII_DAILY_LIMIT}.\n\n"
        "Напиши текст — или /cancel для отмены:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]
        ])
    )


@router.message(NiiWrite.text, F.text, ~F.text.func(is_main_menu_text))
async def nii_write_text(message: Message, state: FSMContext):
    text = message.text.strip()
    if text.lower() == "/cancel":
        await state.clear()
        await message.answer("Обращение отменено.")
        return
    if not text:
        await message.answer("❌ Текст не может быть пустым. Напиши его:")
        return
    if len(text) > NII_TEXT_MAX_LEN:
        await message.answer(
            f"❌ Обращение не может быть длиннее {NII_TEXT_MAX_LEN} символов. "
            f"Сократи:"
        )
        return
    await state.update_data(text=text)
    await state.set_state(NiiWrite.photo)
    await message.answer(
        "🖼 Можешь прикрепить одну картинку к обращению.\n"
        "Отправь фото или нажми «Без фото»:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Без фото", callback_data="nii:no_photo")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")],
        ])
    )


@router.callback_query(F.data == "nii:no_photo")
async def nii_photo_skip(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    await _nii_finish(callback.message, state, bot, photo_file_id=None)


@router.message(NiiWrite.photo)
async def nii_write_photo(message: Message, state: FSMContext, bot: Bot):
    if message.text and message.text.strip().lower() == "/cancel":
        await state.clear()
        await message.answer("Обращение отменено.")
        return
    if message.text and message.text.strip() in ("-", "Пропустить"):
        await _nii_finish(message, state, bot, photo_file_id=None)
        return
    if not message.photo:
        await message.answer("❌ Отправь фото, «-», «Пропустить» или кнопку «Без фото»:")
        return
    await _nii_finish(message, state, bot, photo_file_id=message.photo[-1].file_id)


async def _nii_finish(message, state: FSMContext, bot: Bot, photo_file_id):
    user_id = message.from_user.id
    data = await state.get_data()
    text = data.get('text')

    # Повторная проверка лимита (на случай долгого ввода).
    used = await count_nii_reports_today(user_id)
    left = NII_DAILY_LIMIT - used
    if left <= 0:
        await state.clear()
        await message.answer(
            f"🚫 Суточный лимит обращений исчерпан ({NII_DAILY_LIMIT} в сутки). "
            f"Новое — завтра."
        )
        return

    report_id = await add_nii_report(user_id, text, photo_file_id)
    await log_activity(user_id, "nii_report",
                       f"Обращение #{report_id} ({len(text)} симв.)")
    await state.clear()

    author = await get_user(user_id)
    notif = (
        f"🔔 Обращение №{report_id} в НИИ\n"
        f"От: {await player_display(author)}\n"
        "Подробности — в здании «НИИ»."
    )
    target_ids = await nii_notify_ids()
    for tg_id in target_ids:
        try:
            await bot.send_message(tg_id, notif)
        except Exception:
            pass

    await message.answer(
        f"✅ Обращение №{report_id} принято и передано Хранителям.\n"
        f"Осталось сегодня: {left - 1} из {NII_DAILY_LIMIT}."
    )


async def _fmt_report(r, with_text: bool = True) -> str:
    author = await get_user(r['user_id'])
    name = await player_display(author)
    status = {"open": "🟡 открыто", "done": "🟢 решено", "closed": "🔵 закрыто"}.get(
        r['status'], r['status'])
    lines = [
        f"#{r['id']} • {r['created_at']}",
        f"👤 {name} • {status}",
    ]
    if with_text:
        lines.append(f"📝 {r['text']}")
    return "\n".join(lines)


@router.callback_query(F.data == "nii:mine")
async def nii_my_reports(callback: CallbackQuery):
    await callback.answer()
    reports = await get_my_nii_reports(callback.from_user.id)
    if not reports:
        await edit_or_replace(callback.message,
                              "У тебя пока нет обращений.",
                              _nii_main_keyboard())
        return
    parts = ["📜 ТВОИ ОБРАЩЕНИЯ\n"]
    for r in reports[:5]:
        parts.append(await _fmt_report(r))
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 В НИИ", callback_data="nii:menu_back")],
        [InlineKeyboardButton(text="🏠 В меню города", callback_data="city:menu")],
    ])
    await edit_or_replace(callback.message, "\n\n".join(parts), kb)


@router.callback_query(F.data == "nii:menu_back")
async def nii_menu_back(callback: CallbackQuery):
    await callback.answer()
    await nii_menu(callback)


@router.callback_query(F.data == "nii:all")
async def nii_all_reports(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    if not await _nii_can_view_all(user_id):
        await callback.message.answer("⛔ Список всех обращений открыт только Хранителям.")
        return
    reports = await get_all_nii_reports()
    if not reports:
        await edit_or_replace(callback.message, "Обращений пока нет.",
                              _nii_admin_keyboard())
        return
    # Список: id + автор + статус + фрагмент текста.
    parts = ["📥 ВСЕ ОБРАЩЕНИЯ\n----------------"]
    shown = []
    for r in reports[:20]:
        author = await get_user(r['user_id'])
        nm = await player_display(author)
        status = {"open": "🟡", "done": "🟢", "closed": "🔵"}.get(r['status'], "⚪")
        frag = r['text'][:40] + ("…" if len(r['text']) > 40 else "")
        shown.append([InlineKeyboardButton(
            text=f"{status} #{r['id']} • {nm}: {frag}",
            callback_data=f"nii:view:{r['id']}")])
    kb = InlineKeyboardMarkup(inline_keyboard=[
        *shown,
        [InlineKeyboardButton(text="🔙 В НИИ", callback_data="nii:menu_back")],
        [InlineKeyboardButton(text="🏠 В меню города", callback_data="city:menu")],
    ])
    await edit_or_replace(callback.message, "\n".join(parts), kb)


@router.callback_query(F.data.startswith("nii:view:"))
async def nii_view_report(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    if not await _nii_can_view_all(user_id):
        await callback.message.answer("⛔ Доступ только Хранителям.")
        return
    report_id = int(callback.data.split(":")[2])
    r = await get_nii_report(report_id)
    if not r:
        await callback.message.answer("❌ Обращение не найдено.")
        return
    text = await _fmt_report(r, with_text=True)
    status_btns = [
        InlineKeyboardButton(
            text="🟢 Решено",
            callback_data=f"nii:set:{report_id}:done"),
        InlineKeyboardButton(
            text="🔵 Закрыть",
            callback_data=f"nii:set:{report_id}:closed"),
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=[
        status_btns,
        [InlineKeyboardButton(text="🔙 Ко всем", callback_data="nii:all")],
        [InlineKeyboardButton(text="🏠 В меню города", callback_data="city:menu")],
    ])
    if r['photo_file_id']:
        try:
            await callback.message.answer_photo(r['photo_file_id'], caption=text,
                                                reply_markup=kb)
            return
        except Exception:
            pass
    await callback.message.answer(text, reply_markup=kb)


@router.callback_query(F.data.startswith("nii:set:"))
async def nii_set_status(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    if not await _nii_can_view_all(user_id):
        await callback.message.answer("⛔ Доступ только Хранителям.")
        return
    _, _, report_id_s, status = callback.data.split(":")
    report_id = int(report_id_s)
    ok = await set_nii_report_status(report_id, status)
    await callback.message.answer(
        ("✅ " if ok else "❌ ") + f"Обращение #{report_id} отмечено: "
        + {"done": "решено", "closed": "закрыто"}.get(status, status)
    )