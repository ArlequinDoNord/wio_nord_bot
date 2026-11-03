# -*- coding: utf-8 -*-
"""Язык интерфейса: русский (по умолчанию) и английский.

Язык пилота хранится в users.lang. LangMiddleware на каждом обновлении кладёт
язык пользователя в ContextVar — поэтому t() и клавиатуры работают без передачи
языка через все функции. Строки, которых нет в словаре, остаются русскими.
"""
import contextvars

from aiogram import BaseMiddleware

SUPPORTED = ("ru", "en")
_current = contextvars.ContextVar("interface_lang", default="ru")

STRINGS = {
    # главное меню (reply-кнопки)
    "btn.profile": {"ru": "Профиль", "en": "Profile"},
    "btn.report": {"ru": "📝 Сдать отчёт", "en": "📝 Submit report"},
    "btn.inventory": {"ru": "Инвентарь", "en": "Inventory"},
    "btn.shop": {"ru": "Магазин", "en": "Shop"},
    "btn.housing": {"ru": "🏠 Жильё", "en": "🏠 Housing"},
    "btn.city": {"ru": "Город", "en": "City"},
    "btn.news": {"ru": "📰 Новости Нордхайма", "en": "📰 Nordheim news"},
    "btn.wall": {"ru": "🧱 Стена изречений", "en": "🧱 Wall of sayings"},
    "btn.admin": {"ru": "👑 Админ-панель", "en": "👑 Admin panel"},
    "btn.lang": {"ru": "🌐 English", "en": "🌐 Русский"},
    "menu.choose": {"ru": "Выберите действие:", "en": "Choose an action:"},
    "lang.switched_en": {"ru": "🌐 Язык: English", "en": "🌐 Language: English"},
    "lang.switched_ru": {"ru": "🌐 Язык: Русский", "en": "🌐 Language: Русский"},
    # город
    "city.caption": {"ru": "🏰 Город Аркхольм:", "en": "🏰 City of Arkholm:"},
    "city.speech_none": {"ru": "📢 Речь представителя: пока не произнесена.",
                         "en": "📢 Representative's speech: not given yet."},
    "city.speech_title": {"ru": "📢 Речь представителя", "en": "📢 Representative's speech"},
    "city.back": {"ru": "🔙 В город", "en": "🔙 Back to city"},
    "city.business": {"ru": "💼 Деловой квартал", "en": "💼 Business quarter"},
    "city.admin": {"ru": "🏢 Административный квартал", "en": "🏢 Administrative quarter"},
    "city.countryside": {"ru": "🌲 Загородные территории", "en": "🌲 Countryside"},
    # профиль (кнопки)
    "profile.set_photo": {"ru": "Изменить фото", "en": "Change photo"},
    "profile.choose_status": {"ru": "Выбрать статус", "en": "Choose status"},
    "profile.about": {"ru": "📖 О себе", "en": "📖 About me"},
    "profile.awards": {"ru": "🎖️ Награды", "en": "🎖️ Awards"},
    "profile.achievements": {"ru": "🏅 Достижения", "en": "🏅 Achievements"},
    "profile.pilot_card": {"ru": "Карточка пилота", "en": "Pilot card"},
    # отчёт
    "report.start": {"ru": "📝 Сдать отчёт", "en": "📝 Submit report"},
    "report.menu_header": {"ru": "📋 Меню отчётов", "en": "📋 Report menu"},
    "report.remaining": {"ru": "Осталось отчётов сегодня: {n}", "en": "Reports left today: {n}"},
    "report.limit": {"ru": "⚠️ Лимит отчётов на сегодня исчерпан (3 из 3).",
                     "en": "⚠️ Daily report limit reached (3 of 3)."},
    "report.btn_submit": {"ru": "Сдать отчёт", "en": "Submit report"},
    "report.btn_my": {"ru": "Мои отчёты", "en": "My reports"},
    "common.back": {"ru": "Назад", "en": "Back"},
    "report.photo_prompt": {
        "ru": ("📸 Прикрепи скриншот карты братства, где видно твой текущий регион "
               "с твоим общим кол-вом войск, твой ник и суточное накопление войск.\n"
               "Отправь фото одним сообщением.\n\nОсталось отчётов на сегодня: {remaining}"),
        "en": ("📸 Attach a screenshot of the brotherhood map showing your current region, "
               "your total troops, your nickname and your daily troop gain.\n"
               "Send the photo as one message.\n\nReports left today: {remaining}"),
    },
    "report.daily_prompt": {
        "ru": ("✍️ Сколько войск ты заработал за СЕГОДНЯШНИЕ сутки?\n"
               "Только то, что набежало сегодня — НЕ всё накопленное за все дни.\n"
               "(цифрами, до {max})\n\nℹ️ За сутки считается накопленное с 10:00 до 10:00. "
               "Если сдашь несколько отчётов, платят по ПОСЛЕДНЕМУ — отчёты не складываются. "
               "Поэтому сдавай отчёт по мере накопления, а не один раз в конце."),
        "en": ("✍️ How many troops did you gain TODAY?\n"
               "Only what accumulated today — NOT everything from all days.\n"
               "(in digits, up to {max})\n\nℹ️ A game day counts troops from 10:00 to 10:00. "
               "If you submit several reports, only the LAST one is paid — reports don't add up. "
               "So submit as you accumulate, not once at the end."),
    },
    "report.total_prompt": {
        "ru": ("🗺 Сколько у тебя сейчас войск на карте в регионе? (цифрами, до {max})"),
        "en": ("🗺 How many troops do you have on the map in your region now? (in digits, up to {max})"),
    },
    "report.total_note": {
        "ru": ("\n\nЭто число нужно для статистики сил по регионам — на оплату оно не влияет."),
        "en": ("\n\nThis number is for regional troop statistics — it does not affect payment."),
    },
    "report.prev_day": {"ru": "🗓 За прошлые сутки ты сдал: {n}.", "en": "🗓 Last game day you submitted: {n}."},
}


def t(key: str, **fmt) -> str:
    """Текст по ключу на языке текущего запроса; нет перевода — русский."""
    entry = STRINGS.get(key)
    if entry is None:
        return key
    text = entry.get(_current.get()) or entry["ru"]
    return text.format(**fmt) if fmt else text


def btn_labels(key: str) -> tuple:
    """Все надписи кнопки на всех языках — для фильтров F.text.in_(...)."""
    entry = STRINGS.get(key, {})
    return tuple(dict.fromkeys(entry.values()))


def all_button_labels() -> set:
    """Все надписи всех кнопок: их не должны перехватывать FSM-формы как ввод."""
    out = set()
    for key in STRINGS:
        out.update(btn_labels(key))
    return out


def current_lang() -> str:
    return _current.get()


def use_lang(lang: str) -> None:
    """Сменить язык для остатка текущего обработчика (например, перерисовать меню)."""
    if lang in SUPPORTED:
        _current.set(lang)


class LangMiddleware(BaseMiddleware):
    """Выставляет язык пилота на время обработки обновления."""

    async def __call__(self, handler, event, data):
        from_user = data.get("event_from_user")
        lang = "ru"
        if from_user is not None:
            from database.db import get_user_lang
            try:
                lang = await get_user_lang(from_user.id)
            except Exception:
                lang = "ru"
        token = _current.set(lang)
        try:
            return await handler(event, data)
        finally:
            _current.reset(token)
