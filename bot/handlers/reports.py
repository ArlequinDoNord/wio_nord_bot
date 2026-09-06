from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import REPORT_AUTO_APPROVE_TROOPS, get_effective_rank
from database.db import add_report, approve_report, get_user_reports, get_user, get_report_tax_percent
from keyboards.keyboards import report_keyboard

router = Router()


class ReportSubmit(StatesGroup):
    waiting_photo = State()
    waiting_daily_troops = State()
    waiting_total_troops = State()
    waiting_region = State()


@router.message(F.text == "📝 Сдать отчёт")
async def report_menu(message: Message):
    await message.answer(
        "📋 Меню отчётов",
        reply_markup=report_keyboard()
    )


@router.callback_query(F.data == "report:submit")
async def report_submit_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(ReportSubmit.waiting_photo)
    await callback.message.answer(
        "📸 Прикрепи скриншот боя.\n"
        "Отправь фото одним сообщением."
    )


@router.message(ReportSubmit.waiting_photo, F.photo)
async def report_receive_photo(message: Message, state: FSMContext):
    photo = message.photo[-1]
    await state.update_data(screenshot_file_id=photo.file_id)
    await state.set_state(ReportSubmit.waiting_daily_troops)
    await message.answer(
        "✍️ Сколько войск ты заработал за сутки? (цифрами)"
    )


@router.message(ReportSubmit.waiting_photo)
async def report_photo_expected(message: Message):
    await message.answer("❌ Нужно отправить именно фото. Попробуй ещё раз.")


@router.message(ReportSubmit.waiting_daily_troops, F.text.regexp(r"^\d+$"))
async def report_receive_daily_troops(message: Message, state: FSMContext):
    troops = int(message.text)
    if troops <= 0:
        await message.answer("❌ Число должно быть больше 0.")
        return
    await state.update_data(daily_troops=troops)
    await state.set_state(ReportSubmit.waiting_total_troops)
    await message.answer(
        "📊 Сколько у тебя всего войск на данный момент? (цифрами)"
    )


@router.message(ReportSubmit.waiting_daily_troops)
async def report_daily_troops_expected(message: Message):
    await message.answer("❌ Введи число цифрой. Например: 150")


@router.message(ReportSubmit.waiting_total_troops, F.text.regexp(r"^\d+$"))
async def report_receive_total_troops(message: Message, state: FSMContext):
    total = int(message.text)
    if total < 0:
        await message.answer("❌ Число не может быть отрицательным.")
        return
    await state.update_data(total_troops=total)
    await state.set_state(ReportSubmit.waiting_region)
    from aiogram.types import FSInputFile
    map_photo = FSInputFile("assets/img/maps/map.jpg")
    await message.answer_photo(
        photo=map_photo,
        caption="🌍 Карта регионов. Введи номер региона (0 = Столица):"
    )


@router.message(ReportSubmit.waiting_total_troops)
async def report_total_troops_expected(message: Message):
    await message.answer("❌ Введи число цифрой. Например: 500")


@router.message(ReportSubmit.waiting_region, F.text.regexp(r"^\d+$"))
async def report_receive_region(message: Message, state: FSMContext):
    region_code = message.text.strip()

    data = await state.get_data()
    screenshot_file_id = data["screenshot_file_id"]
    daily_troops = data["daily_troops"]
    total_troops = data["total_troops"]

    report_id = await add_report(
        message.from_user.id, screenshot_file_id,
        daily_troops, total_troops, region_code
    )

    if daily_troops <= REPORT_AUTO_APPROVE_TROOPS:
        await approve_report(report_id, 0, daily_troops)
        user = await get_user(message.from_user.id)
        rank = get_effective_rank(user["troops"], user["promoted_rank"] if "promoted_rank" in user.keys() else None)
        tax_percent = await get_report_tax_percent()
        tax = int(daily_troops * tax_percent / 100)
        nordmarks_earned = daily_troops - tax
        tax_line = f"\nналог в казну: {tax_percent}% (−{tax} НМ)" if tax > 0 else ""
        await state.clear()
        await message.answer(
            f"✅ Отчёт #{report_id} автоматически принят!\n"
            f"Начислено: {daily_troops} войск, {nordmarks_earned} нордмарок{tax_line}.\n"
            f"Текущее звание: {rank} ({user['troops']} войск)"
        )
    else:
        await state.clear()
        await message.answer(
            f"📤 Отчёт #{report_id} отправлен на проверку.\n"
            f"Войск за сутки: {daily_troops}\n"
            f"Всего войск: {total_troops}\n"
            f"Регион: {region_code}\n"
            f"Ожидай решения администратора/МВД."
        )


@router.message(ReportSubmit.waiting_region)
async def report_region_expected(message: Message):
    await message.answer("❌ Введи номер региона цифрой. Например: 0 (Столица)")


@router.callback_query(F.data == "report:my_reports")
async def report_my_reports(callback: CallbackQuery):
    await callback.answer()
    reports = await get_user_reports(callback.from_user.id)
    if not reports:
        await callback.message.answer("📋 У тебя пока нет отчётов.")
        return

    status_emoji = {"pending": "⏳", "approved": "✅", "rejected": "❌"}
    lines = []
    for r in reports[:10]:
        emoji = status_emoji.get(r["status"], "❓")
        lines.append(
            f"{emoji} #{r['id']} | {r['troops_reported']} войск | "
            f"{r['region'] or '—'} | {r['created_at'][:10]}"
        )

    await callback.message.answer(
        "📋 Твои отчёты:\n\n" + "\n".join(lines)
    )
