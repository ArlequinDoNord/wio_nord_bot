"""Здание КГБ: вход (глава КГБ и Хранитель) и выдача паспортов Нордхайма.

Выдавать паспорта может только глава КГБ (роль kgb_head). Пошаговый ввод данных —
FSM KgbPassport. Готовый паспорт попадает в инвентарь пилота (категория «Документы»)
и показывается в профиле (серия и номер).
"""

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message

from database.db import (
    get_all_users, get_user, get_passport, passport_number_taken, issue_passport,
    get_passport_map, get_passport_archive, get_passport_history,
)
from utils.localization import t
from utils.notify import notify_user_t
from utils.passports import (
    validate_series, validate_number, validate_text, validate_marks, parse_date,
    format_passport,
)
from utils.permissions import can_enter_kgb, is_kgb_head, log_action
from config import ADMIN_IDS

router = Router()

PICK_PAGE_SIZE = 10


async def can_see_passport_archive(user_id: int) -> bool:
    """Архив паспортов: глава КГБ и владелец (ADMIN_IDS). Роль «Хранитель» сюда не входит."""
    return user_id in ADMIN_IDS or await is_kgb_head(user_id)


class KgbPassport(StatesGroup):
    photo = State()
    series = State()
    number = State()
    full_name = State()
    position = State()
    rank = State()
    sex = State()
    marital = State()
    birth = State()
    issue = State()
    marks = State()
    confirm = State()


# Порядок вопросов после фото; sex — кнопками, остальные — текстом.
ORDER = [
    KgbPassport.series, KgbPassport.number, KgbPassport.full_name, KgbPassport.position,
    KgbPassport.rank, KgbPassport.sex, KgbPassport.marital, KgbPassport.birth,
    KgbPassport.issue, KgbPassport.marks,
]

# Вопрос для каждого шага.
PROMPTS = {
    KgbPassport.series.state: "kgb.ask_series",
    KgbPassport.number.state: "kgb.ask_number",
    KgbPassport.full_name.state: "kgb.ask_full_name",
    KgbPassport.position.state: "kgb.ask_position",
    KgbPassport.rank.state: "kgb.ask_rank",
    KgbPassport.sex.state: "kgb.ask_sex",
    KgbPassport.marital.state: "kgb.ask_marital",
    KgbPassport.birth.state: "kgb.ask_birth",
    KgbPassport.issue.state: "kgb.ask_issue",
    KgbPassport.marks.state: "kgb.ask_marks",
}

# Текстовые шаги: состояние → (поле в passports, валидатор). Валидатор возвращает
# (значение, ключ ошибки); parse_date и validate_* имеют одну сигнатуру.
TEXT_STEPS = {
    KgbPassport.series.state: ("series", validate_series),
    KgbPassport.number.state: ("number", validate_number),
    KgbPassport.full_name.state: ("full_name", validate_text),
    KgbPassport.position.state: ("position", validate_text),
    KgbPassport.rank.state: ("rank", validate_text),
    KgbPassport.marital.state: ("marital_status", validate_text),
    KgbPassport.birth.state: ("birth_date", parse_date),
    KgbPassport.issue.state: ("issue_date", parse_date),
    KgbPassport.marks.state: ("distinguishing_marks", validate_marks),
}

STATE_BY_NAME = {s.state: s for s in ORDER + [KgbPassport.photo, KgbPassport.confirm]}


def _cancel_row():
    return [InlineKeyboardButton(text=t("kgb.btn_cancel"), callback_data="kgb:cancel")]


def _cancel_kb():
    return InlineKeyboardMarkup(inline_keyboard=[_cancel_row()])


def _sex_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("kgb.btn_sex_m"), callback_data="kgb:sex:m"),
         InlineKeyboardButton(text=t("kgb.btn_sex_f"), callback_data="kgb:sex:f")],
        _cancel_row(),
    ])


def _photo_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("kgb.btn_skip_photo"), callback_data="kgb:nophoto")],
        _cancel_row(),
    ])


def _confirm_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("kgb.btn_confirm"), callback_data="kgb:confirm")],
        _cancel_row(),
    ])


async def _ask(message: Message, state_obj: State):
    if state_obj == KgbPassport.sex:
        await message.answer(t(PROMPTS[state_obj.state]), reply_markup=_sex_kb())
    else:
        await message.answer(t(PROMPTS[state_obj.state]), reply_markup=_cancel_kb())


async def _advance(message: Message, state: FSMContext, current: State):
    idx = ORDER.index(current)
    if idx + 1 < len(ORDER):
        nxt = ORDER[idx + 1]
        await state.set_state(nxt)
        await _ask(message, nxt)
        return
    await _preview(message, state)


async def _preview(message: Message, state: FSMContext):
    await state.set_state(KgbPassport.confirm)
    data = await state.get_data()
    text = t("kgb.preview") + "\n\n" + format_passport(data)
    photo = data.get('photo_file_id')
    if photo:
        await message.answer_photo(photo=photo, caption=text, reply_markup=_confirm_kb())
    else:
        await message.answer(text, reply_markup=_confirm_kb())


def _people_markup(page: int, users: list, item_cb: str, page_cb: str, back_cb: str,
                   passports: dict = None) -> InlineKeyboardMarkup:
    """Список пилотов по страницам. passports: {user_id: ...} — у кого уже есть паспорт.

    В подписи таких пилотов стоит серия паспорта, чтобы не выдать второй по ошибке.
    """
    pages = max(1, (len(users) + PICK_PAGE_SIZE - 1) // PICK_PAGE_SIZE)
    page = max(0, min(page, pages - 1))
    passports = passports or {}
    rows = []
    for u in users[page * PICK_PAGE_SIZE:(page + 1) * PICK_PAGE_SIZE]:
        uid = int(u['user_id'])
        label = u['first_name'] or u['username'] or str(uid)
        if u['username']:
            label += f" (@{u['username']})"
        if uid in passports:
            label = t("kgb.has_passport_mark", series=passports[uid]['series']) + " " + label
        rows.append([InlineKeyboardButton(text=label, callback_data=f"{item_cb}{uid}")])
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="◀️", callback_data=f"{page_cb}{page - 1}"))
    nav.append(InlineKeyboardButton(text=f"{page + 1}/{pages}", callback_data="noop"))
    if page < pages - 1:
        nav.append(InlineKeyboardButton(text="▶️", callback_data=f"{page_cb}{page + 1}"))
    rows.append(nav)
    rows.append([InlineKeyboardButton(text=t("kgb.btn_back"), callback_data=back_cb)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _pick_markup(page: int, users: list, passports: dict = None) -> InlineKeyboardMarkup:
    return _people_markup(page, users, "kgb:user:", "kgb:pick:", "kgb:menu", passports)


async def kgb_menu(callback: CallbackQuery):
    """Экран здания КГБ. Вызывается из location_enter после проверки входа."""
    rows = []
    if await is_kgb_head(callback.from_user.id):
        rows.append([InlineKeyboardButton(text=t("kgb.btn_issue"), callback_data="kgb:issue")])
    if await can_see_passport_archive(callback.from_user.id):
        rows.append([InlineKeyboardButton(text=t("kgb.btn_archive"), callback_data="kgb:archive")])
    rows.append([InlineKeyboardButton(text=t("kgb.btn_back"), callback_data="city:quarter")])
    await callback.message.answer(t("kgb.menu_title"), reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))


@router.callback_query(F.data == "kgb:menu")
async def kgb_menu_cb(callback: CallbackQuery):
    await callback.answer()
    if not await can_enter_kgb(callback.from_user.id):
        await callback.message.answer(t("kgb.no_access"))
        return
    await kgb_menu(callback)


@router.callback_query(F.data == "kgb:issue")
async def kgb_issue_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await is_kgb_head(callback.from_user.id):
        await callback.message.answer(t("kgb.head_only"))
        return
    await state.clear()
    users = sorted(await get_all_users(citizens_only=True),
                   key=lambda u: (u['first_name'] or u['username'] or '').lower())
    if not users:
        await callback.message.answer(t("kgb.pick_empty"))
        return
    passports = await get_passport_map()
    await callback.message.answer(t("kgb.pick_title"), reply_markup=_pick_markup(0, users, passports))


@router.callback_query(F.data.startswith("kgb:pick:"))
async def kgb_issue_page(callback: CallbackQuery):
    await callback.answer()
    if not await is_kgb_head(callback.from_user.id):
        await callback.message.answer(t("kgb.head_only"))
        return
    try:
        page = int(callback.data.split(":")[2])
    except (ValueError, IndexError):
        page = 0
    users = sorted(await get_all_users(citizens_only=True),
                   key=lambda u: (u['first_name'] or u['username'] or '').lower())
    passports = await get_passport_map()
    await callback.message.answer(t("kgb.pick_title"), reply_markup=_pick_markup(page, users, passports))


@router.callback_query(F.data == "kgb:archive")
async def kgb_archive_start(callback: CallbackQuery):
    await callback.answer()
    if not await can_see_passport_archive(callback.from_user.id):
        await callback.message.answer(t("kgb.head_only"))
        return
    await _send_archive(callback.message, 0)


@router.callback_query(F.data.startswith("kgb:arch:"))
async def kgb_archive_page(callback: CallbackQuery):
    await callback.answer()
    if not await can_see_passport_archive(callback.from_user.id):
        await callback.message.answer(t("kgb.head_only"))
        return
    try:
        page = int(callback.data.split(":")[2])
    except (ValueError, IndexError):
        page = 0
    await _send_archive(callback.message, page)


async def _send_archive(message, page: int):
    rows = await get_passport_archive()
    if not rows:
        await message.answer(t("kgb.archive_empty"), reply_markup=_archive_back_kb())
        return
    users = [{'user_id': r['user_id'], 'first_name': r['name'], 'username': None} for r in rows]
    series_map = {r['user_id']: r for r in rows}
    markup = _people_markup(page, users, "kgb:archcard:", "kgb:arch:", "kgb:menu", series_map)
    await message.answer(t("kgb.archive_title"), reply_markup=markup)


def _archive_back_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("kgb.btn_back"), callback_data="kgb:menu")]])


@router.callback_query(F.data.startswith("kgb:archcard:"))
async def kgb_archive_card(callback: CallbackQuery):
    await callback.answer()
    if not await can_see_passport_archive(callback.from_user.id):
        await callback.message.answer(t("kgb.head_only"))
        return
    try:
        uid = int(callback.data.split(":")[2])
    except (ValueError, IndexError):
        return
    current = await get_passport(uid)
    if not current:
        await callback.message.answer(t("kgb.archive_empty"), reply_markup=_archive_back_kb())
        return
    user = await get_user(uid)
    name = (user['first_name'] or user['username'] or str(uid)) if user else str(uid)
    text = t("kgb.archive_card", name=name, series=current['series'], number=current['number'],
             issue_date=current['issue_date'])
    history = await get_passport_history(uid)
    if history:
        text += t("kgb.archive_history_head") + "\n"
        for h in history:
            text += t("kgb.archive_history_line", series=h['series'], number=h['number'],
                      issue_date=h['issue_date'], replaced_at=str(h['replaced_at'])[:10]) + "\n"
    else:
        text += t("kgb.archive_no_history")
    await callback.message.answer(text, reply_markup=_archive_back_kb())


@router.callback_query(F.data.startswith("kgb:user:"))
async def kgb_issue_target(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await is_kgb_head(callback.from_user.id):
        await callback.message.answer(t("kgb.head_only"))
        return
    try:
        target_id = int(callback.data.split(":")[2])
    except (ValueError, IndexError):
        return
    if not await get_user(target_id):
        return
    await state.clear()
    await state.update_data(target_id=target_id)
    warn = ""
    old = await get_passport(target_id)
    if old:
        warn = t("kgb.exists_warn", series=old['series'], number=old['number'])
    await state.set_state(KgbPassport.photo)
    await callback.message.answer(warn + t("kgb.ask_photo"), reply_markup=_photo_kb())


@router.message(KgbPassport.photo, F.photo)
async def kgb_photo_step(message: Message, state: FSMContext):
    if not await is_kgb_head(message.from_user.id):
        await state.clear()
        return
    await state.update_data(photo_file_id=message.photo[-1].file_id)
    await state.set_state(ORDER[0])
    await _ask(message, ORDER[0])


@router.message(KgbPassport.photo)
async def kgb_photo_wrong(message: Message):
    await message.answer(t("kgb.photo_only"), reply_markup=_photo_kb())


@router.callback_query(KgbPassport.photo, F.data == "kgb:nophoto")
async def kgb_photo_skip(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await is_kgb_head(callback.from_user.id):
        await state.clear()
        return
    await state.update_data(photo_file_id=None)
    await state.set_state(ORDER[0])
    await _ask(callback.message, ORDER[0])


@router.message(KgbPassport.sex)
async def kgb_sex_wrong(message: Message):
    await message.answer(t("kgb.ask_sex"), reply_markup=_sex_kb())


@router.message(KgbPassport.series)
@router.message(KgbPassport.number)
@router.message(KgbPassport.full_name)
@router.message(KgbPassport.position)
@router.message(KgbPassport.rank)
@router.message(KgbPassport.marital)
@router.message(KgbPassport.birth)
@router.message(KgbPassport.issue)
@router.message(KgbPassport.marks)
async def kgb_text_step(message: Message, state: FSMContext):
    if not await is_kgb_head(message.from_user.id):
        await state.clear()
        return
    current_name = await state.get_state()
    if current_name not in TEXT_STEPS:
        return
    field, validator = TEXT_STEPS[current_name]
    value, err = validator(message.text or "")
    if err:
        await message.answer(t(err), reply_markup=_cancel_kb())
        return
    data = await state.get_data()
    if field == "number" and await passport_number_taken(
            data.get('series'), value, exclude_user=data.get('target_id')):
        await message.answer(t("kgb.number_taken"), reply_markup=_cancel_kb())
        return
    await state.update_data({field: value})
    await _advance(message, state, STATE_BY_NAME[current_name])


@router.callback_query(KgbPassport.sex, F.data.startswith("kgb:sex:"))
async def kgb_sex_step(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await is_kgb_head(callback.from_user.id):
        await state.clear()
        return
    sex = callback.data.split(":")[2]
    if sex not in ("m", "f"):
        return
    await state.update_data(sex=sex)
    await _advance(callback.message, state, KgbPassport.sex)


@router.callback_query(KgbPassport.confirm, F.data == "kgb:confirm")
async def kgb_confirm(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await is_kgb_head(callback.from_user.id):
        await state.clear()
        return
    data = await state.get_data()
    target = data.get('target_id')
    if not target:
        await state.clear()
        return
    if await passport_number_taken(data['series'], data['number'], exclude_user=target):
        await callback.message.answer(t("kgb.number_taken"), reply_markup=_cancel_kb())
        await state.set_state(KgbPassport.number)
        return
    await issue_passport(target, data, issued_by=callback.from_user.id)
    await log_action(callback.from_user.id, 'kgb_issue_passport', target,
                     f"{data['series']} {data['number']}")
    await notify_user_t(callback.bot, target, "kgb.issued_pilot",
                        series=data['series'], number=data['number'])
    await state.clear()
    await callback.message.answer(t("kgb.issued", name=data['full_name'],
                                    series=data['series'], number=data['number']))


@router.callback_query(F.data == "kgb:cancel")
async def kgb_cancel(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await callback.message.answer(t("kgb.cancelled"))


async def render_passport_card(message, user_id: int):
    """Карточка паспорта в инвентаре («📄 Документы»). Вызывается из inventory."""
    back = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=t("kgb.back_docs"), callback_data="inventory:cat:documents")]])
    passport = await get_passport(user_id)
    if not passport:
        await message.answer(t("kgb.no_passport"), reply_markup=back)
        return
    text = format_passport(passport) + "\n\n" + t("kgb.inv_hint")
    try:
        await message.delete()
    except Exception:
        pass
    if passport['photo_file_id']:
        await message.answer_photo(photo=passport['photo_file_id'], caption=text, reply_markup=back)
    else:
        await message.answer(text, reply_markup=back)
