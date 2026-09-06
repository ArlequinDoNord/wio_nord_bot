from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.db import get_user, transfer_nordmarks, get_transactions_history, get_all_users, transfer_to_treasury, get_treasury_balance
from keyboards.keyboards import bank_keyboard, cancel_keyboard, main_menu_keyboard
from utils.helpers import format_amount, plural_nordmark

router = Router()


class BankStates(StatesGroup):
    waiting_recipient = State()
    waiting_amount = State()
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
async def bank_transfer(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(BankStates.waiting_recipient)
    await callback.message.answer(
        "💸 Кому перевести? Введи username игрока (без @, например: Ivanov):\n\n"
        "Или нажми Отмена:",
        reply_markup=cancel_keyboard()
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


@router.message(BankStates.waiting_treasury_amount)
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
    new_balance = await get_treasury_balance()
    await state.clear()
    await message.answer(
        f"✅ Пожертвование принято!\n"
        f"Сумма: {amount} НМ\n"
        f"Баланс казны: {new_balance} НМ",
        reply_markup=main_menu_keyboard()
    )


@router.message(BankStates.waiting_recipient)
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


@router.message(BankStates.waiting_amount)
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

    await transfer_nordmarks(
        message.from_user.id,
        data['recipient_id'],
        amount,
        f"Перевод от {message.from_user.first_name}"
    )
    await state.clear()
    await message.answer(
        f"✅ Перевод выполнен!\n"
        f"Сумма: {amount} НМ\n"
        f"Получатель: {data['recipient_name']}",
        reply_markup=main_menu_keyboard()
    )


@router.callback_query(F.data == "bank:history")
async def bank_history(callback: CallbackQuery):
    await callback.answer()
    txns = await get_transactions_history(callback.from_user.id)

    if not txns:
        await callback.message.answer("Пока нет транзакций.")
        return

    text = "📜 История транзакций:\n\n"
    for t in txns[:10]:
        sign = "+" if (t['to_user'] == callback.from_user.id and t['amount'] > 0) else ""
        if t['to_user'] == callback.from_user.id and t['tx_type'] in ("transfer", "report", "salary", "bonus", "shop_sale", "treasury"):
            sign = "+"
        elif t['from_user'] == callback.from_user.id:
            sign = "-"

        date_str = t['created_at'][:16] if t['created_at'] else ""
        text += f"{date_str} {tx_type_label(t['tx_type'])}: {sign}{abs(t['amount'])} НМ\n"
        if t['description']:
            text += f"  {t['description']}\n"

    await callback.message.answer(text)
