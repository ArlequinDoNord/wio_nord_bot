from aiogram import Router, F
from aiogram import Bot
from aiogram.types import Message, CallbackQuery, ContentType
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import REPORT_MAX_TROOPS, REPORT_MAX_REGION, REPORT_DAILY_LIMIT
from database.db import add_report, approve_report, get_user, get_user_reports, report_tax_percent_for, get_report_auto_approve_troops, count_reports_today, log_activity, user_is_tourist, report_payout_context, report_prev_day_total, created_at_msk, report_day_value_of
from utils.helpers import is_main_menu_text
from utils.notify import notify_report_praise
from keyboards.keyboards import report_keyboard, cancel_keyboard

router = Router()


class ReportSubmit(StatesGroup):
    waiting_photo = State()
    waiting_daily_troops = State()
    waiting_total_troops = State()
    waiting_region = State()


@router.message(F.text == "📝 Сдать отчёт")
async def report_menu(message: Message):
    if await user_is_tourist(message.from_user.id):
        await message.answer(
            "❌ Сдавать отчёты могут рекруты и пилоты.\n"
            "Статус «Рекрут» выдают после проверки — напиши об этом администраторам."
        )
        return
    remaining = REPORT_DAILY_LIMIT - await count_reports_today(message.from_user.id)
    header = "📋 Меню отчётов"
    if remaining > 0:
        header += f"\nОсталось отчётов сегодня: {remaining}"
    else:
        header += "\n⚠️ Лимит отчётов на сегодня исчерпан (3 из 3)."
    await message.answer(
        header,
        reply_markup=report_keyboard()
    )


@router.callback_query(F.data == "report:submit")
async def report_submit_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    # Сдачу отчёта нельзя начинать, пока игрок внутри подземелья/КВП или идёт заброс.
    # Раньше report:submit молча перетирал состояние рыбалки: в подземном
    # водохранилище это означало потерю доступа к нему (восстановить можно только
    # «Продолжить путь», и тогда рыбалка в водохранилище уже недоступна), а во время
    # заброса (озеро/водохранилище, 4–7 секунд) — потерю улова при уже списанных ОД
    # и наживке: resv_cast/fish_cast выбрасывали результат (v0.22.7).
    from bot.handlers.fishing import FISHING_CASTING
    from bot.handlers.dungeon import DungeonFSM
    user_id = callback.from_user.id
    dungeon_states = {
        DungeonFSM.in_dungeon.state,
        DungeonFSM.in_combat.state,
        DungeonFSM.in_boss.state,
        DungeonFSM.in_reservoir.state,
    }
    if await state.get_state() in dungeon_states:
        await callback.message.answer(
            "🗺 Ты сейчас в подземелье — сначала выйди из него.\n"
            "Кнопка «Выход» есть в меню подземелья."
        )
        return
    if user_id in FISHING_CASTING:
        await callback.message.answer(
            "🎣 Дождись результата заброса — потом сдашь отчёт.\n"
            "Это займёт несколько секунд."
        )
        return
    if await user_is_tourist(user_id):
        await callback.message.answer(
            "❌ Сдавать отчёты могут рекруты и пилоты.\n"
            "Статус «Рекрут» выдают после проверки — напиши об этом администраторам."
        )
        await state.clear()
        return
    remaining = REPORT_DAILY_LIMIT - await count_reports_today(callback.from_user.id)
    if remaining <= 0:
        await callback.message.answer(
            "❌ Лимит отчётов на сегодня исчерпан (3 из 3).\n"
            "Новые отчёты станут доступны с наступлением новых суток."
        )
        await state.clear()
        return
    await state.set_state(ReportSubmit.waiting_photo)
    await callback.message.answer(
        "📸 Прикрепи скриншот боя.\n"
        f"Отправь фото одним сообщением.\n\nОсталось отчётов на сегодня: {remaining}",
        reply_markup=cancel_keyboard()
    )


@router.message(ReportSubmit.waiting_photo, F.photo)
async def report_receive_photo(message: Message, state: FSMContext):
    if message.media_group_id:
        await message.answer("❌ К отчёту прикрепляется только один файл. Отправь одно фото.")
        return
    photo = message.photo[-1]
    await state.update_data(screenshot_file_id=photo.file_id)
    await state.set_state(ReportSubmit.waiting_daily_troops)
    await message.answer(
        "✍️ Сколько войск ты заработал за СЕГОДНЯШНИЕ сутки?\n"
        "Только то, что набежало сегодня — НЕ всё накопленное за все дни.\n"
        f"(цифрами, до {REPORT_MAX_TROOPS:,})".replace(",", " ")
        + "\n\nℹ️ За сутки считается накопленное с 10:00 до 10:00. Если сдашь "
          "несколько отчётов, платят по ПОСЛЕДНЕМУ — отчёты не складываются. "
          "Поэтому сдавай отчёт по мере накопления, а не один раз в конце.",
        reply_markup=cancel_keyboard()
    )


@router.message(ReportSubmit.waiting_photo, ~F.text.func(is_main_menu_text))
async def report_photo_expected(message: Message):
    await message.answer("❌ Нужно отправить именно фото. Попробуй ещё раз.", reply_markup=cancel_keyboard())


@router.message(ReportSubmit.waiting_daily_troops, F.text.regexp(r"^\d{1,7}$"))
async def report_receive_daily_troops(message: Message, state: FSMContext):
    troops = int(message.text)
    if troops <= 0:
        await message.answer("❌ Число должно быть больше 0.")
        return
    if troops > REPORT_MAX_TROOPS:
        await message.answer(
            f"❌ Слишком большое число. Максимум для одного отчёта: {REPORT_MAX_TROOPS:,} войск."
            .replace(",", " ")
        )
        return
    await state.update_data(daily_troops=troops)
    await state.set_state(ReportSubmit.waiting_total_troops)
    prev_total = await report_prev_day_total(message.from_user.id)
    prev_note = (f"\n🗓 За прошлые сутки ты сдал: {prev_total}." if prev_total else "")
    await message.answer(
        f"🗺 Сколько у тебя сейчас войск на карте в регионе? (цифрами, до {REPORT_MAX_TROOPS:,})"
        .replace(",", " ")
        + prev_note + "\n\nЭто число нужно для статистики сил по регионам — на оплату "
                       "оно не влияет.",
        reply_markup=cancel_keyboard()
    )


@router.message(ReportSubmit.waiting_daily_troops, ~F.text.func(is_main_menu_text))
async def report_daily_troops_expected(message: Message):
    await message.answer("❌ Введи число цифрой. Например: 150", reply_markup=cancel_keyboard())


@router.message(ReportSubmit.waiting_total_troops, F.text.regexp(r"^\d{1,7}$"))
async def report_receive_total_troops(message: Message, state: FSMContext):
    total = int(message.text)
    if total > REPORT_MAX_TROOPS:
        await message.answer(
            f"❌ Слишком большое число. Максимум для одного отчёта: {REPORT_MAX_TROOPS:,} войск."
            .replace(",", " ")
        )
        return
    await state.update_data(total_troops=total)
    await state.set_state(ReportSubmit.waiting_region)

    remaining_after = REPORT_DAILY_LIMIT - (await count_reports_today(message.from_user.id) + 1)
    if remaining_after > 0:
        reminder = f"\n\n📊 Отчётов на сегодня останется после этого: {remaining_after}."
    else:
        reminder = "\n\n📊 Это последний отчёт за сегодня (лимит 3)."
    if total < (await state.get_data()).get("daily_troops", 0):
        reminder += (
            "\n\nℹ️ «Всего» меньше, чем «за сутки» — бывает при обороте региона. "
            "На оплату это не влияет: платят за «за сутки»."
        )
    from aiogram.types import FSInputFile
    map_photo = FSInputFile("assets/img/maps/map.jpg")
    await message.answer_photo(
        photo=map_photo,
        caption=f"🌍 Карта регионов. Введи номер региона от 0 (Столица) до {REPORT_MAX_REGION}:{reminder}",
        reply_markup=cancel_keyboard()
    )


@router.message(ReportSubmit.waiting_total_troops, ~F.text.func(is_main_menu_text))
async def report_total_troops_expected(message: Message):
    await message.answer("❌ Введи число цифрой. Например: 500", reply_markup=cancel_keyboard())


@router.message(ReportSubmit.waiting_region, F.text.regexp(r"^\d+$"))
async def report_receive_region(message: Message, state: FSMContext, bot: Bot):
    # Номер региона нормализуем и здесь, чтобы в подтверждении и в логе показать
    # ровно то, что лежит в базе (нормализация «в одном месте» — в add_report).
    region_code = str(int(message.text.strip()))

    region_int = int(region_code)
    if region_int > REPORT_MAX_REGION:
        await message.answer(
            f"❌ Регион {region_int} не существует. Введи номер от 0 (Столица) до {REPORT_MAX_REGION}:"
        )
        return

    reports_today = await count_reports_today(message.from_user.id)
    if reports_today >= REPORT_DAILY_LIMIT:
        await state.clear()
        await message.answer("❌ Лимит отчётов на сегодня исчерпан (3 из 3).")
        return

    data = await state.get_data()
    screenshot_file_id = data["screenshot_file_id"]
    daily_troops = data["daily_troops"]
    total_troops = data["total_troops"]

    report_id, credited = await add_report(
        message.from_user.id, screenshot_file_id,
        daily_troops, total_troops, region_code
    )
    await log_activity(message.from_user.id, "report_submit",
                       f"Сдал отчёт #{report_id}: {daily_troops} войск, регион {region_code or '—'}")

    ctx = await report_payout_context(message.from_user.id, daily_troops, total_troops,
                                      exclude_id=report_id)
    # Разбор оплаты: платим заявку «за сутки» (накопленное «всего» — только статистика).
    prev_note = (f"\n🗓 За прошлые сутки ты сдал: {ctx['prev_day_total']}"
                 if ctx['prev_day_total'] else "")
    payout_info = (
        f"⚔️ К оплате за текущие сутки: {credited} по заявке «за сутки»{prev_note}"
    )
    if ctx["assigned_today"] > 0:
        payout_info += (f"\n⚔️ Сумма заявок за сутки (справочно): {ctx['assigned_today']}"
                        f" — платится только твой последний отчёт, поэтому сдавай новый "
                        f"отчёт по мере накопления")
    if ctx.get("capped_by_limit"):
        payout_info += (f"\n🚦 Сработал суточный лимит: за сутки начисляется не больше "
                        f"{ctx['cap']} войск. Излишек в оплату не идёт.")

    remaining_after = REPORT_DAILY_LIMIT - (reports_today + 1)
    if remaining_after > 0:
        reminder = f"\n📊 Осталось отчётов на сегодня: {remaining_after}."
    else:
        reminder = "\n📊 Это последний отчёт за сегодня (лимит 3)."

    auto_approve_limit = await get_report_auto_approve_troops()
    # Автоодобрение — когда заявка в пороге.
    if daily_troops <= auto_approve_limit:
        actual = await approve_report(report_id, 0)
        if actual <= 0:
            await state.clear()
            await message.answer(
                f"✅ Отчёт #{report_id} принят.\n"
                f"К оплате 0: суточный лимит уже выбран, доплаты нет.{reminder}"
            )
            return
        tax_percent = await report_tax_percent_for(message.from_user.id)
        await state.clear()
        await message.answer(
            f"✅ Отчёт #{report_id} автоматически принят!\n"
            f"⚔️ К начислению: {actual} войск и столько же опыта (налог {tax_percent}% — "
            f"только с денег, в казну).\n"
            f"💰 Оплата по отчётам — в 10:00 МСК, в начале новых суток.{reminder}"
        )
        # Принятый отчёт — похвала в общий чат по накопленной сумме за сутки
        # (сама функция молчит ниже порога и не дублирует уже отправленный уровень).
        # Сутки берём те же, что и у отчёта: иначе автоодобрение хвалило бы по
        # «сегодняшним», а ручное — по суткам отчёта, и на границе 10:00 подписи
        # разъезжались бы.
        pilot_row = await get_user(message.from_user.id)
        await notify_report_praise(message.bot, pilot_row, message.from_user.id,
                                   day=ctx['cycle_day'])
    else:
        await state.clear()
        await message.answer(
            f"📤 Отчёт #{report_id} отправлен на проверку.\n\n"
            f"Войск за сутки (заявка): {daily_troops}\n"
            f"Всего войск (заявка): {total_troops}\n"
            f"{payout_info}\n"
            f"Регион: {region_code}\n\n"
            f"Оплачивается только фарм за текущие сутки (по суткам {ctx['day_label']}). "
            f"«Всего» и регион идут в статистику сил Нордхайма.\n"
            f"Ожидай решения администратора/МВД.{reminder}"
        )


@router.message(ReportSubmit.waiting_region, ~F.text.func(is_main_menu_text))
async def report_region_expected(message: Message):
    await message.answer("❌ Введи номер региона цифрой. Например: 0 (Столица)", reply_markup=cancel_keyboard())


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
        # Время сдачи — по МСК (created_at в базе UTC). Раньше тут печатался сырой
        # UTC-день, из-за чего отчёт, сданный в 08:00 МСК, показывался «вчера».
        when = created_at_msk(r["created_at"]) or r["created_at"][:16]
        # Сутки отчёта: у отчёта до 10:00 МСК календарная дата одна, а отчётные
        # сутки начинаются в 10:00 — поэтому день показываем отдельно.
        day = report_day_value_of(r["created_at"])
        day_hint = f" (сутки {day[5:]})" if day else ""
        lines.append(
            f"{emoji} #{r['id']} | {r['troops_reported']} войск | "
            f"{r['region'] or '—'} | {when}{day_hint}"
        )

    await callback.message.answer(
        "📋 Твои отчёты (время по МСК):\n\n" + "\n".join(lines)
    )
