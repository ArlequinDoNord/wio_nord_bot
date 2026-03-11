"""
Модуль для создания inline-клавиатур
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_item_keyboard(item_id: int, price_nord: int, price_ap: int):
    """Клавиатура для предмета в магазине"""
    keyboard = [
        [
            InlineKeyboardButton(
                f"💵 Купить за {price_nord} ✈️",
                callback_data=f"buy_nord_{item_id}"
            )
        ]
    ]

    # Если есть цена в AP, добавляем вторую кнопку
    if price_ap > 0:
        keyboard[0].append(
            InlineKeyboardButton(
                f"⚡️ Купить за {price_ap} AP",
                callback_data=f"buy_ap_{item_id}"
            )
        )

    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back_to_shop")])

    return InlineKeyboardMarkup(keyboard)


def get_back_keyboard(back_to: str):
    """Простая клавиатура с кнопкой назад"""
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data=back_to)]]
    return InlineKeyboardMarkup(keyboard)