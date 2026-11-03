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
    # банк: раздел «Штрафы»
    "bank.fines_btn": {"ru": "⚖️ Штрафы", "en": "⚖️ Fines"},
    "fines.title": {"ru": "⚖️ Твои штрафы", "en": "⚖️ Your fines"},
    "fines.none": {"ru": "✅ Неоплаченных штрафов нет.", "en": "✅ You have no unpaid fines."},
    "fines.line": {"ru": "#{id} · осталось {left} НМ из {total} НМ\nПричина: {reason}",
                   "en": "#{id} · {left} NM left of {total} NM\nReason: {reason}"},
    "fines.btn_pay_all": {"ru": "💰 Оплатить всё ({left} НМ)", "en": "💰 Pay all ({left} NM)"},
    "fines.btn_pay_part": {"ru": "✏️ Оплатить часть", "en": "✏️ Pay part"},
    "fines.ask_amount": {"ru": "Сколько НМ внести по штрафу #{id}? Введи целое число:",
                         "en": "How many NM to pay toward fine #{id}? Enter a whole number:"},
    "fines.paid_full": {"ru": "✅ Штраф #{id} оплачен полностью: {taken} НМ.",
                        "en": "✅ Fine #{id} paid in full: {taken} NM."},
    "fines.paid_part": {"ru": "✅ По штрафу #{id} внесено {taken} НМ.",
                        "en": "✅ {taken} NM paid toward fine #{id}."},
    "fines.not_found": {"ru": "❌ Штраф не найден или уже закрыт.",
                        "en": "❌ Fine not found or already closed."},
    "fines.nothing": {"ru": "❌ Нечего списывать.", "en": "❌ Nothing to pay."},
    "fines.no_money": {"ru": "❌ Недостаточно НМ на счёте для этой суммы.",
                       "en": "❌ Not enough NM in your account for this amount."},
    "fines.bad_amount": {"ru": "❌ Введи целое число больше нуля:",
                         "en": "❌ Enter a whole number greater than zero:"},
    # админ: штрафы (только супер-админ)
    "admin.fines_btn": {"ru": "⚖️ Штрафы", "en": "⚖️ Fines"},
    "admin.fines_menu": {"ru": "⚖️ Штрафы пилотов. Выбери действие:",
                         "en": "⚖️ Pilot fines. Choose an action:"},
    "admin.fine_new": {"ru": "➕ Наложить штраф", "en": "➕ Issue fine"},
    "admin.fine_list": {"ru": "📋 Активные штрафы", "en": "📋 Active fines"},
    "admin.fine_cancel_btn": {"ru": "🗑 Отменить #{id}", "en": "🗑 Cancel #{id}"},
    "admin.fine_pick_user": {"ru": "Выбери пилота из списка или введи ID:",
                             "en": "Pick a pilot from the list or enter their ID:"},
    "admin.fine_ask_user": {"ru": "Укажи ID пилота (число):", "en": "Enter the pilot's ID (number):"},
    "admin.fine_ask_amount": {"ru": "Сумма штрафа в НМ (целое число больше нуля):",
                              "en": "Fine amount in NM (whole number greater than zero):"},
    "admin.fine_ask_reason": {"ru": "Причина штрафа (текст, будет показан пилоту):",
                              "en": "Fine reason (text, shown to the pilot):"},
    "admin.fine_bad_number": {"ru": "❌ Нужно целое число больше нуля. Попробуй ещё раз:",
                              "en": "❌ A whole number greater than zero is required. Try again:"},
    "admin.fine_no_user": {"ru": "❌ Пилот с таким ID не найден. Укажи другой ID:",
                           "en": "❌ No pilot with that ID. Enter another ID:"},
    "admin.fine_issued": {"ru": "✅ Штраф #{id} наложен на {name}: {amount} НМ.\nПричина: {reason}",
                          "en": "✅ Fine #{id} issued to {name}: {amount} NM.\nReason: {reason}"},
    "admin.fine_cancel_done": {"ru": "✅ Штраф #{id} отменён.", "en": "✅ Fine #{id} cancelled."},
    "admin.fine_none": {"ru": "Активных штрафов нет.", "en": "There are no active fines."},
    "admin.fine_not_super": {"ru": "⛔ Штрафы накладывает только супер-админ.",
                             "en": "⛔ Only the super admin can issue fines."},
    "fine.issued": {"ru": "⚖️ Тебе наложен штраф: {amount} НМ.\nПричина: {reason}\n"
                         "Каждые игровые сутки будет списываться 10% суммы, пока штраф не закрыт. "
                         "Оплатить можно в банке, раздел «Штрафы».",
                    "en": "⚖️ A fine of {amount} NM was issued to you.\nReason: {reason}\n"
                          "10% of the amount will be taken each game day until it is paid. "
                          "You can pay it at the bank, section «Fines»."},
    "fine.cancelled": {"ru": "✅ Штраф #{id} отменён администратором.",
                       "en": "✅ Fine #{id} was cancelled by an administrator."},
    # штрафы
    "fine.blocked": {
        "ru": ("⚖️ У тебя есть неоплаченный штраф: покупки, переводы и передача предметов "
               "недоступны, пока он не закрыт. Оплатить можно в банке, раздел «Штрафы»."),
        "en": ("⚖️ You have an unpaid fine: purchases, transfers and item handovers are "
               "unavailable until it is paid. Pay it at the bank, section «Fines»."),
    },
    "fine.charged": {
        "ru": ("⚖️ По штрафу списано {taken} НМ (10% суммы).\nОсталось: {left} НМ.\n"
               "Причина: {reason}\nОплатить можно в банке, раздел «Штрафы»."),
        "en": ("⚖️ {taken} NM was taken for your fine (10% of the amount).\nLeft: {left} NM.\n"
               "Reason: {reason}\nYou can pay it at the bank, section «Fines»."),
    },
    "fine.closed": {
        "ru": "⚖️ Штраф закрыт.\nСписано за сутки: {taken} НМ.\nПричина: {reason}",
        "en": "⚖️ Fine closed.\nTaken today: {taken} NM.\nReason: {reason}",
    },
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


async def t_user(user_id: int, key: str, **fmt) -> str:
    """Текст на языке конкретного пилота — для фоновых задач и рассылок (вне обработчика)."""
    from database.db import get_user_lang
    try:
        lang = await get_user_lang(user_id)
    except Exception:
        lang = "ru"
    entry = STRINGS.get(key)
    if entry is None:
        return key
    text = entry.get(lang) or entry["ru"]
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
