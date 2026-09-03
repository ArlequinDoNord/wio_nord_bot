from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import REPORT_AUTO_APPROVE_TROOPS, get_rank, get_effective_rank
from database.db import add_report, approve_report, get_user_reports, get_user
from keyboards.keyboards import report_keyboard, main_menu_keyboard
from utils.permissions import is_admin

router = Router()


class ReportSubmit(StatesGroup):
    waiting_photo = State()
    waiting_troops = State()


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
    await state.set_state(ReportSubmit.waiting_troops)
    await message.answer(
        "✍️ Введи количество войск, заработанных в бою (цифрами)."
    )


@router.message(ReportSubmit.waiting_photo)
async def report_photo_expected(message: Message):
    await message.answer("❌ Нужно отправить именно фото. Попробуй ещё раз.")


@router.message(ReportSubmit.waiting_troops, F.text.regexp(r"^\d+$"))
async def report_receive_troops(message: Message, state: FSMContext):
    troops = int(message.text)
    if troops <= 0:
        await message.answer("❌ Число должно быть больше 0.")
        return

    data = await state.get_data()
    screenshot_file_id = data["screenshot_file_id"]

    report_id = await add_report(message.from_user.id, screenshot_file_id, troops)

    if troops <= REPORT_AUTO_APPROVE_TROOPS:
        await approve_report(report_id, 0, troops)
        user = await get_user(message.from_user.id)
        rank = get_effective_rank(user["troops"], user.get("promoted_rank"))
        await state.clear()
        await message.answer(
            f"✅ Отчёт #{report_id} автоматически принят!\n"
            f"Начислено: {troops} войск, {troops} нордмарок.\n"
            f"Текущее звание: {rank} ({user['troops']} войск)"
        )
    else:
        await state.clear()
        await message.answer(
            f"📤 Отчёт #{report_id} отправлен на проверку.\n"
            f"Заявлено войск: {troops}\n"
            f"Ожидай решения администратора/МВД."
        )


@router.message(ReportSubmit.waiting_troops)
async def report_troops_expected(message: Message):
    await message.answer("❌ Введи число цифрой. Например: 150")


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
            f"{r['created_at'][:10]}"
        )

    await callback.message.answer(
        "📋 Твои отчёты:\n\n" + "\n".join(lines)
    )
