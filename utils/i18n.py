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
    "profile.recipes": {"ru": "📜 Выученные рецепты", "en": "📜 Learned recipes"},
    "profile.pilot_card": {"ru": "Карточка пилота", "en": "Pilot card"},
    # выученные рецепты (профиль)
    "recipes.title": {"ru": "📜 ВЫУЧЕННЫЕ РЕЦЕПТЫ ({n}):", "en": "📜 LEARNED RECIPES ({n}):"},
    "recipes.empty": {"ru": "Пока ни один рецепт не выучен.",
                      "en": "No recipes learned yet."},
    "recipes.group_kitchen": {"ru": "🍳 Кухня", "en": "🍳 Kitchen"},
    "recipes.group_workbench": {"ru": "🔨 Верстак", "en": "🔨 Workbench"},
    "recipes.group_other": {"ru": "📦 Прочее", "en": "📦 Other"},
    "recipes.card_ingredients": {"ru": "Ингредиенты:", "en": "Ingredients:"},
    "recipes.card_no_ingredients": {"ru": "Ингредиентов нет.", "en": "No ingredients."},
    "recipes.card_meta": {"ru": "ОД: {ap} · время: ~{time} сек · {station}, ур. {level}",
                          "en": "AP: {ap} · time: ~{time} s · {station}, lvl {level}"},
    "recipes.card_station_kitchen": {"ru": "кухня", "en": "kitchen"},
    "recipes.card_station_workbench": {"ru": "верстак", "en": "workbench"},
    "recipes.card_station_other": {"ru": "прочее", "en": "other"},
    "recipes.back": {"ru": "🔙 К рецептам", "en": "🔙 Back to recipes"},
    "recipes.list_level": {"ru": "ур. {lvl}", "en": "lvl {lvl}"},
    "profile.back": {"ru": "🏠 В профиль", "en": "🏠 Back to profile"},
    "recipes.not_found": {"ru": "❌ Рецепт не найден.", "en": "❌ Recipe not found."},
    # редкость предметов
    "rarity.1": {"ru": "Обычный", "en": "Common"},
    "rarity.2": {"ru": "Качественный", "en": "Quality"},
    "rarity.3": {"ru": "Редкий", "en": "Rare"},
    "rarity.4": {"ru": "Шедевр", "en": "Masterpiece"},
    "rarity.5": {"ru": "Легендарный", "en": "Legendary"},
    # подтверждение продажи редких предметов
    "sell.rare_ask": {
        "ru": ("⚠️ «{name}» — редкость: {rarity}.\n"
               "Продать {qty} шт.? Такой предмет потом не вернуть."),
        "en": ("⚠️ «{name}» — rarity: {rarity}.\n"
               "Sell {qty} pcs.? You won't get such an item back."),
    },
    "sell.rare_final": {"ru": "✅ Да, точно продать", "en": "✅ Yes, sell for sure"},
    "sell.cancel": {"ru": "↩️ Нет, отмена", "en": "↩️ No, cancel"},
    # банк
    "bank.my_balance": {"ru": "Мой баланс", "en": "My balance"},
    "bank.transfer_btn": {"ru": "Перевести", "en": "Transfer"},
    "bank.to_treasury": {"ru": "🏛️ В казну", "en": "🏛️ To treasury"},
    "bank.history_btn": {"ru": "История транзакций", "en": "Transaction history"},
    "bank.fines_btn": {"ru": "⚖️ Штрафы", "en": "⚖️ Fines"},
    "bank.back": {"ru": "🔙 В банк", "en": "🔙 Back to bank"},
    "bank.back_to_city": {"ru": "🔙 В город", "en": "🔙 Back to city"},
    "bank.no_txns": {"ru": "Пока нет транзакций.", "en": "No transactions yet."},
    "bank.history_title": {"ru": "📜 История транзакций (стр. {page}):\n\n",
                           "en": "📜 Transaction history (p. {page}):\n\n"},
    "bank.newer": {"ru": "⬅️ Новее", "en": "⬅️ Newer"},
    "bank.older": {"ru": "Старее ▶️", "en": "Older ▶️"},
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
    # Проверка отчётов МВД: причина отклонения обязательна, в карточке — имя
    # проверяющего в боте (позывной/@username), а не Telegram ID.
    "report.reject_ask": {
        "ru": ("❌ ОТКЛОНЕНИЕ ОТЧЁТА #{id}\n\n"
               "Напиши причину отклонения: её увидит пилот в карточке отчёта и в "
               "личном сообщении. Причина обязательна.\n"
               "Отмена — вернуться к очереди."),
        "en": ("❌ REJECTING REPORT #{id}\n\n"
               "Write the reason for rejection: the pilot will see it in the report "
               "card and in a private message. The reason is required.\n"
               "Cancel to go back to the queue."),
    },
    "report.reject_reason_short": {
        "ru": "❌ Слишком коротко. Опиши причину хотя бы в {min} символов:",
        "en": "❌ Too short. Describe the reason in at least {min} characters:",
    },
    "report.reject_done": {
        "ru": "❌ Отчёт #{id} отклонён.\n📝 Причина: {reason}\n👮 Проверил: {name}",
        "en": "❌ Report #{id} rejected.\n📝 Reason: {reason}\n👮 Reviewed by: {name}",
    },
    "report.reject_dm": {
        "ru": ("❌ ТВОЙ ОТЧЁТ ОТКЛОНЁН\n\n"
               "Отчёт #{id} отклонён при проверке.\n"
               "📝 Причина: {reason}\n"
               "👮 Проверил: {name}\n\n"
               "Если считаешь отклонение ошибкой — напиши в МВД."),
        "en": ("❌ YOUR REPORT WAS REJECTED\n\n"
               "Report #{id} was rejected during review.\n"
               "📝 Reason: {reason}\n"
               "👮 Reviewed by: {name}\n\n"
               "If you think this was a mistake, contact the Interior Ministry."),
    },
    "report.card_reviewed_by": {"ru": "👮 Проверил: {name}", "en": "👮 Reviewed by: {name}"},
    "report.card_reject_reason": {"ru": "📝 Причина отклонения: {reason}",
                                  "en": "📝 Rejection reason: {reason}"},
    "report.reviewer_system": {"ru": "автоматически (система)", "en": "automatically (system)"},
    "report.reviewer_unknown": {"ru": "—", "en": "—"},
    "report.reject_reason_required": {
        "ru": "❌ Причину отклонения нельзя оставить пустой. Напиши её текстом:",
        "en": "❌ The rejection reason cannot be empty. Write it as text:",
    },
    # Вкладка админки «Отклонённые отчёты»: только свежие (неделя), с именем
    # проверяющего и причиной; супер-админ может убрать запись из списка.
    "report.rejected_menu_line": {
        "ru": "• ❌ Отклонённые ({days} дн.): {n}",
        "en": "• ❌ Rejected (last {days} days): {n}",
    },
    "report.rejected_menu_btn": {
        "ru": "❌ Отклонённые отчёты · {n}",
        "en": "❌ Rejected reports · {n}",
    },
    "report.rejected_title": {
        "ru": "❌ ОТКЛОНЁННЫЕ ОТЧЁТЫ\n\nПоказаны только отчёты, отклонённые за последние "
              "{days} дней. Старые записи из списка уходят сами.\n",
        "en": "❌ REJECTED REPORTS\n\nOnly reports rejected within the last {days} days "
              "are shown. Older entries leave the list automatically.\n",
    },
    "report.rejected_none": {
        "ru": "\nЗа последние {days} дней отклонённых отчётов нет.",
        "en": "\nNo rejected reports in the last {days} days.",
    },
    "report.rejected_line": {
        "ru": "#{id} · {author} · {troops} ⚔️ · регион {region} · {when}\n"
              "   👮 {reviewer} · 📝 {reason}",
        "en": "#{id} · {author} · {troops} ⚔️ · region {region} · {when}\n"
              "   👮 {reviewer} · 📝 {reason}",
    },
    "report.rejected_page": {"ru": "Страница {page} из {total}", "en": "Page {page} of {total}"},
    "report.rejected_view_btn": {"ru": "🔍 Отчёт #{id}", "en": "🔍 Report #{id}"},
    "report.rejected_back_btn": {"ru": "🔙 К отклонённым", "en": "🔙 Back to rejected"},
    "report.rejected_back_reports": {"ru": "🔙 К отчётам", "en": "🔙 Back to reports"},
    # Авто-выкладка товара «как госпоставка» (карточка в Хранилище, раз в неделю).
    "restock.btn": {"ru": "🔁 Авто-выкладка раз в неделю", "en": "🔁 Weekly auto-restock"},
    "restock.screen": {
        "ru": ("🔁 АВТО-ВЫКЛАДКА «{name}»\n\n"
               "Раз в неделю (первый суточный цикл недели, понедельник 10:00 МСК) "
               "остаток доводится до заданного числа. Если остаток выше — не трогаем. "
               "Безлимит не выкладываем.\n\n"
               "Сейчас: {state}\nОстаток на складе: {stock}"),
        "en": ("🔁 AUTO-RESTOCK «{name}»\n\n"
               "Once a week (the first daily cycle of the week, Monday 10:00 MSK) "
               "the stock is topped up to the set number. If stock is already higher, "
               "nothing changes. Unlimited items are not restocked.\n\n"
               "Now: {state}\nStock on hand: {stock}"),
    },
    "restock.state_on": {"ru": "включена, до {n} шт. в неделю", "en": "on, up to {n} per week"},
    "restock.state_off": {"ru": "выключена", "en": "off"},
    "restock.toggle_on": {"ru": "✅ Включить", "en": "✅ Turn on"},
    "restock.toggle_off": {"ru": "⏸ Выключить", "en": "⏸ Turn off"},
    "restock.set_target": {"ru": "🔢 Сколько выкладывать", "en": "🔢 Set weekly amount"},
    "restock.back": {"ru": "🔙 К товару", "en": "🔙 Back to item"},
    "restock.ask_target": {
        "ru": ("🔢 Сколько штук «{name}» выкладывать каждую неделю?\n"
               "Введи число от 1 до 100000. Включение выкладки включит и её."),
        "en": ("🔢 How many «{name}» to restock every week?\n"
               "Enter a number from 1 to 100000. Setting it also turns restock on."),
    },
    "restock.bad_target": {
        "ru": "❌ Введи целое число от 1 до 100000.",
        "en": "❌ Enter a whole number from 1 to 100000.",
    },
    "restock.saved": {
        "ru": "✅ «{name}»: авто-выкладка включена, до {n} шт. в неделю.",
        "en": "✅ «{name}»: weekly auto-restock is on, up to {n} per week.",
    },
    "restock.unlimited": {
        "ru": "ℹ️ Безлимитный или лут-товар — авто-выкладка не нужна.",
        "en": "ℹ️ Unlimited or loot-only item — auto-restock is not needed.",
    },
    "report.rejected_details": {
        "ru": "\n🗑 Отклонён: {when}",
        "en": "\n🗑 Rejected: {when}",
    },
    "report.rejected_delete_btn": {"ru": "🗑 Удалить из списка", "en": "🗑 Remove from list"},
    "report.rejected_delete_ask": {
        "ru": ("🗑 УДАЛИТЬ ОТЧЁТ #{id}?\n\n"
               "Запись исчезнет из БД: её не будет ни в списке отклонённых, ни в "
               "«Моих отчётах» пилота. Действие необратимо."),
        "en": ("🗑 DELETE REPORT #{id}?\n\n"
               "The record will be removed from the database: it disappears from the "
               "rejected list and from the pilot's «My reports». This cannot be undone."),
    },
    "report.rejected_delete_yes": {"ru": "✅ Да, удалить", "en": "✅ Yes, delete"},
    "report.rejected_delete_cancel": {"ru": "🔙 Отмена", "en": "🔙 Cancel"},
    "report.rejected_delete_done": {
        "ru": "🗑 Отчёт #{id} удалён из списка отклонённых.",
        "en": "🗑 Report #{id} removed from the rejected list.",
    },
    "report.rejected_delete_missing": {
        "ru": "❌ Отчёт #{id} не найден среди отклонённых (возможно, уже удалён).",
        "en": "❌ Report #{id} is not among rejected ones (maybe already deleted).",
    },
    "report.rejected_delete_super_only": {
        "ru": "❌ Удалять отклонённые отчёты может только супер-админ.",
        "en": "❌ Only a super admin can delete rejected reports.",
    },
    # Локации города: ru — название, как оно показано в боте (из БД для кнопки
    # «Курс выживания», из кода для подменю); en — перевод.
    "loc.townhall": {"ru": "Ратуша", "en": "Town Hall"},
    "loc.library": {"ru": "Библиотека", "en": "Library"},
    "loc.park": {"ru": "Городской парк", "en": "City Park"},
    "loc.gossmi": {"ru": "ГосСМИ", "en": "State Media"},
    "loc.bank": {"ru": "Банк", "en": "Bank"},
    "loc.kvp": {"ru": "Курс выживания", "en": "Survival Course"},
    "loc.hq": {"ru": "Штаб ВВС", "en": "Air Force HQ"},
    "loc.contracts": {"ru": "Доска контрактов", "en": "Contract Board"},
    "loc.nii": {"ru": "НИИ Северной Кибернетики", "en": "Northern Cybernetics Institute"},
    "loc.forest": {"ru": "Лес на окраине", "en": "Outskirts Forest"},
    "loc.duel_house": {"ru": "Дом Дуэлей", "en": "Duel House"},
    "loc.mine": {"ru": "Железная копи", "en": "Iron Mine"},
    "loc.storage": {"ru": "Городские склады", "en": "City Warehouses"},
    "loc.mvd": {"ru": "Здание МВД", "en": "Interior Ministry"},
    # Категории предметов (магазин и инвентарь): ru — как в config.ITEM_CATEGORIES.
    "cat.weapon": {"ru": "Оружие", "en": "Weapons"},
    "cat.consumable": {"ru": "Расходники", "en": "Consumables"},
    "cat.building": {"ru": "Недвижимость", "en": "Real estate"},
    "cat.housing": {"ru": "Жильё", "en": "Housing"},
    "cat.furniture": {"ru": "Мебель и расширения", "en": "Furniture & extensions"},
    "cat.seeds": {"ru": "Семена", "en": "Seeds"},
    "cat.equipment": {"ru": "Одежда", "en": "Clothing"},
    "cat.resource": {"ru": "Ресурсы", "en": "Resources"},
    "cat.special": {"ru": "Особое", "en": "Special"},
    "cat.special_dept": {"ru": "Спец-отдел", "en": "Special Department"},
    "cat.souvenirs": {"ru": "Сувениры", "en": "Souvenirs"},
    "cat.library_card": {"ru": "Читательские билеты", "en": "Library cards"},
    "cat.fishing": {"ru": "Рыбалка", "en": "Fishing"},
    "cat.mining": {"ru": "⛏ Добыча ресурсов", "en": "⛏ Resource mining"},
    "cat.license": {"ru": "Торговые лицензии", "en": "Trade licenses"},
    "cat.recipes": {"ru": "📜 Рецепты", "en": "📜 Recipes"},
    "cat.market": {"ru": "🎪 Рынок", "en": "🎪 Market"},
    "cat.duel_gear": {"ru": "🥊 Дуэльное снаряжение", "en": "🥊 Duel gear"},
    "cat.duel_card": {"ru": "🎫 Клубные карты", "en": "🎫 Club cards"},
    # Разделы магазина и инвентаря.
    "shop.catalog": {"ru": "Каталог", "en": "Catalog"},
    "shop.my_purchases": {"ru": "Мои покупки", "en": "My purchases"},
    "shop.sell": {"ru": "Продать товар", "en": "Sell an item"},
    "inv.gear": {"ru": "Снаряжение", "en": "Gear"},
    "inv.catch": {"ru": "Улов", "en": "Catch"},
}


def place_name(key: str, ru_name: str) -> str:
    """Название локации/квартала для кнопки.

    В русском — ru_name как есть (он может прийти из БД и правиться админом);
    в английском — перевод из STRINGS['loc.<key>'], если он есть.
    """
    if _current.get() == "en":
        entry = STRINGS.get(f"loc.{key}")
        if entry:
            return entry["en"]
    return ru_name


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


# Надписи названий мест, категорий и разделов — не reply-кнопки, в фильтр меню не входят
# (иначе «Банк» или «Каталог» в FSM-формах перехватывались бы как нажатие кнопки меню).
_NOT_MENU_PREFIXES = ("loc.", "cat.", "shop.", "inv.")


def all_button_labels() -> set:
    """Все надписи всех кнопок: их не должны перехватывать FSM-формы как ввод."""
    out = set()
    for key in STRINGS:
        if key.startswith(_NOT_MENU_PREFIXES):
            continue
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
