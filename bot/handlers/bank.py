from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.db import get_user, transfer_nordmarks, get_transactions_history, get_all_users, transfer_to_treasury, get_treasury_balance, log_activity
from keyboards.keyboards import bank_keyboard, cancel_keyboard, main_menu_keyboard
from utils.helpers import format_amount, plural_nordmark, is_main_menu_text

router = Router()


class BankStates(StatesGroup):
    waiting_recipient = State()
    waiting_amount = State()
    waiting_message = State()
    waiting_treasury_amount = State()


def tx_type_label(tx_type: str) -> str:
    labels = {
        "transfer": "💸 Перевод",
        "report": "📊 Отчёт",
        "shop_purchase": "🛒 Покупка",
        "shop_sale": "💵 Продажа",
        "salary": "💰 Зарплата",
        "bonus": "🎁 Бонус",
        "fine": "⚠️ Штраф",
        "building_purchase": "🏠 Здание",
        "admin": "⚙️ Админ",
        "trade": "🤝 Обмен",
        "treasury": "🏛️ Казна",
    }
    return labels.get(tx_type, tx_type)


@router.message(F.text == "Банк")
async def show_bank(message: Message):
    user = await get_user(message.from_user.id)
    if not user:
        await message.answer("Сначала нажми /start")
        return

    await message.answer(
        f"🏦 НОРДБАНК\n\n"
        f"💰 Баланс: {user['nordmarks']} {plural_nordmark(user['nordmarks'])}\n"
        f"⚡ Очки действия: {user['ap']}/{user['ap_max']}\n\n"
        f"────────────────────\n"
        f"Доступные операции:",
        reply_markup=bank_keyboard()
    )


@router.callback_query(F.data == "bank:balance")
async def bank_balance(callback: CallbackQuery):
    await callback.answer()
    user = await get_user(callback.from_user.id)
    if not user:
        return
    await callback.message.answer(
        f"💰 Твой баланс:\n"
        f"Нордмарки: {user['nordmarks']}\n"
        f"Очки действия: {user['ap']}/{user['ap_max']}"
    )


@router.callback_query(F.data == "bank:transfer")
async def bank_transfer(callback: CallbackQuery):
    await callback.answer()
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    rows = [[InlineKeyboardButton(text="✍️ Ввести username вручную", callback_data="bank:transfer_manual")]]
    me = callback.from_user.id
    shown = 0
    for u in await get_all_users():
        if u['user_id'] == me:
            continue
        label = u['first_name'] or u['username'] or str(u['user_id'])
        if u['username']:
            label += f" (@{u['username']})"
        rows.append([InlineKeyboardButton(text=label, callback_data=f"bank:pickrecipient:{u['user_id']}")])
        shown += 1
        if shown >= 50:
            break
    rows.append([InlineKeyboardButton(text="🔙 В банк", callback_data="bank:menu")])
    await callback.message.answer(
        "💸 Кому перевести? Выбери пилота из списка или введи username вручную:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows)
    )


@router.callback_query(F.data == "bank:transfer_manual")
async def bank_transfer_manual(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(BankStates.waiting_recipient)
    await callback.message.answer(
        "💸 Введи username игрока (без @, например: Ivanov):",
        reply_markup=cancel_keyboard()
    )


async def set_recipient(message, state, target):
    if target['user_id'] == message.from_user.id:
        await message.answer("❌ Нельзя перевести самому себе")
        return
    await state.update_data(recipient_id=target['user_id'], recipient_name=target['first_name'])
    await state.set_state(BankStates.waiting_amount)
    await message.answer(
        f"Получатель: {target['first_name']} (@{target['username']})\n"
        f"Введи сумму в Нордмарках:",
        reply_markup=cancel_keyboard()
    )


@router.callback_query(F.data.startswith("bank:pickrecipient:"))
async def bank_pick_recipient(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    user_id = int(callback.data.split(":")[2])
    if user_id == callback.from_user.id:
        await callback.message.answer("❌ Нельзя перевести самому себе")
        return
    target = await get_user(user_id)
    if not target:
        await callback.message.answer("❌ Пользователь не найден.")
        return
    await set_recipient(callback.message, state, target)


@router.callback_query(F.data == "bank:menu")
async def bank_menu_cb(callback: CallbackQuery):
    await callback.answer()
    user = await get_user(callback.from_user.id)
    if not user:
        await callback.message.answer("Сначала нажми /start")
        return
    await callback.message.answer(
        f"🏦 НОРДБАНК\n\n"
        f"💰 Баланс: {user['nordmarks']} {plural_nordmark(user['nordmarks'])}\n"
        f"⚡ Очки действия: {user['ap']}/{user['ap_max']}\n\n"
        f"────────────────────\n"
        f"Доступные операции:",
        reply_markup=bank_keyboard()
    )


@router.callback_query(F.data == "bank:treasury")
async def bank_treasury(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    balance = await get_treasury_balance()
    await state.set_state(BankStates.waiting_treasury_amount)
    await callback.message.answer(
        f"🏛️ КАЗНА НОРДХАЙМА\n\n"
        f"Текущий баланс: {balance} {plural_nordmark(balance)}\n\n"
        f"Пожертвовать в казну? Введи сумму:",
        reply_markup=cancel_keyboard()
    )


@router.message(BankStates.waiting_treasury_amount, ~F.text.func(is_main_menu_text))
async def process_treasury_amount(message: Message, state: FSMContext):
    text = message.text.strip()
    if text == "Отмена":
        await state.clear()
        await message.answer("Операция отменена", reply_markup=main_menu_keyboard())
        return

    try:
        amount = int(text)
    except ValueError:
        await message.answer("❌ Введи число (целое количество Нордмарок):")
        return

    if amount <= 0:
        await message.answer("❌ Сумма должна быть больше нуля")
        return

    sender = await get_user(message.from_user.id)
    if sender['nordmarks'] < amount:
        await message.answer(f"❌ Недостаточно средств. Баланс: {sender['nordmarks']} НМ")
        return

    await transfer_to_treasury(
        message.from_user.id,
        amount,
        f"Пожертвование от {message.from_user.first_name}"
    )
    await log_activity(message.from_user.id, "treasury_donate", f"{amount} НМ в казну")
    new_balance = await get_treasury_balance()
    await state.clear()
    await message.answer(
        f"✅ Пожертвование принято!\n"
        f"Сумма: {amount} НМ\n"
        f"Баланс казны: {new_balance} НМ",
        reply_markup=main_menu_keyboard()
    )


@router.message(BankStates.waiting_recipient, ~F.text.func(is_main_menu_text))
async def process_recipient(message: Message, state: FSMContext):
    username = message.text.strip()
    if not username or username == "Отмена":
        await state.clear()
        await message.answer("Операция отменена", reply_markup=main_menu_keyboard())
        return

    users = await get_all_users()
    target = None
    for u in users:
        if u['username'] and u['username'].lower() == username.lower():
            target = u
            break

    if not target:
        await message.answer("❌ Пользователь не найден. Попробуй ещё раз:")
        return

    await set_recipient(message, state, target)


@router.message(BankStates.waiting_amount, ~F.text.func(is_main_menu_text))
async def process_amount(message: Message, state: FSMContext):
    text = message.text.strip()
    if text == "Отмена":
        await state.clear()
        await message.answer("Операция отменена", reply_markup=main_menu_keyboard())
        return

    try:
        amount = int(text)
    except ValueError:
        await message.answer("❌ Введи число (целое количество Нордмарок):")
        return

    if amount <= 0:
        await message.answer("❌ Сумма должна быть больше нуля")
        return

    data = await state.get_data()
    sender = await get_user(message.from_user.id)
    if sender['nordmarks'] < amount:
        await message.answer(f"❌ Недостаточно средств. Баланс: {sender['nordmarks']} НМ")
        return

    await state.update_data(amount=amount)
    await state.set_state(BankStates.waiting_message)
    await message.answer(
        "📨 Сообщение получателю (до 40 символов).\n"
        "Отправь «Пропустить», чтобы перевести без сообщения:",
        reply_markup=cancel_keyboard()
    )


@router.message(BankStates.waiting_message, ~F.text.func(is_main_menu_text))
async def process_message(message: Message, state: FSMContext):
    text = message.text.strip()
    if text in ("Отмена", "Пропустить", "Без сообщения", "-"):
        text = ""
    elif len(text) > 40:
        await message.answer("❌ Сообщение длиннее 40 символов. Сократи и пришли ещё раз:")
        return

    data = await state.get_data()
    recipient_id = data['recipient_id']
    recipient_name = data.get('recipient_name', recipient_id)
    amount = data['amount']
    sender = await get_user(message.from_user.id)

    if not sender or sender['nordmarks'] < amount:
        await state.clear()
        await message.answer(
            f"❌ Недостаточно средств. Баланс: {sender['nordmarks'] if sender else 0} НМ",
            reply_markup=main_menu_keyboard()
        )
        return

    sender_label = sender['first_name'] or f"#{message.from_user.id}"
    if sender.get('username'):
        sender_label += f" (@{sender['username']})"
    description = f"Перевод от {sender_label}"
    if text:
        description += f": {text}"

    await transfer_nordmarks(
        message.from_user.id,
        recipient_id,
        amount,
        description
    )
    await log_activity(message.from_user.id, "bank_transfer_out",
                       f"{amount} НМ -> @{data.get('recipient_name', recipient_id)}")
    await log_activity(recipient_id, "bank_transfer_in",
                       f"+{amount} НМ от @{message.from_user.username or message.from_user.id}")

    # Оповещение получателю
    note = f"💸 Тебе перевели {amount} {plural_nordmark(amount)}!\nОт: {sender_label}"
    if text:
        note += f"\n📨 Сообщение: «{text}»"
    try:
        await message.bot.send_message(recipient_id, note)
    except Exception:
        pass

    await state.clear()
    reply = (
        f"✅ Перевод выполнен!\n"
        f"Сумма: {amount} НМ\n"
        f"Получатель: {recipient_name}"
    )
    if text:
        reply += f"\n📨 Сообщение: «{text}»"
    await message.answer(reply, reply_markup=main_menu_keyboard())


@router.callback_query(F.data == "bank:history")
async def bank_history(callback: CallbackQuery):
    await callback.answer()
    txns = await get_transactions_history(callback.from_user.id)

    if not txns:
        await callback.message.answer("Пока нет транзакций.")
        return

    text = "📜 История транзакций:\n\n"
    for t in txns[:10]:
        me = callback.from_user.id
        incoming = t['to_user'] == me and t['from_user'] != me
        sign = "+" if incoming else "-"

        # «Покупка» — только когда покупаешь товары/вещи; всё остальное движение
        # средств подписывается как «Списание» или «Зачисление».
        if t['tx_type'] == "shop_purchase":
            label = "🛒 Покупка"
        elif t['tx_type'] == "shop_sale":
            label = "💵 Продажа товара"
        elif incoming:
            label = "📥 Зачисление средств"
        else:
            label = "📤 Списание средств"

        date_str = t['created_at'][:16] if t['created_at'] else ""
        text += f"{date_str} {label}: {sign}{abs(t['amount'])} НМ\n"
        if t['description']:
            text += f"  {t['description']}\n"

    await callback.message.answer(text)
