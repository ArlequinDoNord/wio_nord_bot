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
    # Боевые фразы эффектов оружия и статусов врага (подземелье). Правятся в TEXTS_EDIT.md.
    "battle.weapon.label.poison": {"ru": "отравление", "en": "poison"},
    "battle.weapon.label.bleed": {"ru": "кровотечение", "en": "bleeding"},
    "battle.weapon.label.frostbite": {"ru": "обморожение", "en": "frostbite"},
    "battle.weapon.label.stun": {"ru": "оглушение", "en": "stun"},
    "battle.weapon.label.burn": {"ru": "поджиг", "en": "burning"},
    "battle.weapon.attack.poison": {"ru": "Ты отравил врага — яд въедается в рану",
                                    "en": "You poisoned the enemy — the venom seeps into the wound"},
    "battle.weapon.attack.bleed": {"ru": "Ты глубоко ранил врага — он истекает кровью",
                                   "en": "You cut the enemy deep — it bleeds"},
    "battle.weapon.attack.frostbite": {"ru": "Ты оковал врага холодом — мороз сковывает его тело",
                                       "en": "You chilled the enemy — frost locks its body"},
    "battle.weapon.attack.stun": {"ru": "Ты оглушил врага — его следующие удары неточны",
                                  "en": "You stunned the enemy — its next blows go astray"},
    "battle.weapon.attack.burn": {"ru": "Ты поджёг врага — пламя лижет его броню",
                                  "en": "You set the enemy alight — flames lick its armor"},
    "battle.weapon.dot_applied": {
        "ru": "\n{emoji} {attack}! {label}: −{dmg} HP врагу каждый ход ({ticks} хода).",
        "en": "\n{emoji} {attack}! {label}: −{dmg} HP to the enemy each turn ({ticks} turns).",
    },
    "battle.weapon.dot_cancelled": {
        "ru": "\n{emoji} {attack}! Но {label} врага уже гасит этот эффект — оба снимаются.",
        "en": "\n{emoji} {attack}! But the enemy already has {label} — both cancel out.",
    },
    "battle.weapon.immune": {
        "ru": "\n🛡 {enemy} невосприимчив к «{label}» — эффект не сработал.",
        "en": "\n🛡 {enemy} is immune to «{label}» — the effect did nothing.",
    },
    "battle.enemy.stunned_miss": {
        "ru": "💫 {enemy} оглушён и промахивается! (−0 HP)",
        "en": "💫 {enemy} is stunned and misses! (−0 HP)",
    },
    "battle.player.dodged": {
        "ru": "💨 Ты уклонился от атаки {enemy}! (−0 HP)",
        "en": "💨 You dodged the attack of {enemy}! (−0 HP)",
    },
    "battle.armor_blocked": {
        "ru": "🛡️ Броня поглотила {amount} урона!",
        "en": "🛡️ Armor absorbed {amount} damage!",
    },
    "battle.crit": {"ru": "💥 crit!", "en": "💥 crit!"},
    "battle.crit_mark": {"ru": " 💥 crit!", "en": " 💥 crit!"},
    "battle.crit_short": {"ru": "💥 crit! ", "en": "💥 crit! "},
    # Лесозаготовка: вход и запреты (bot/handlers/logging_site.py).
    "logging.no_axe": {
        "ru": "❌ У тебя нет топора. Купи «Топор» в магазине (категория «Добыча ресурсов»).",
        "en": "❌ You have no axe. Buy one in the shop (Resource Mining category).",
    },
    "logging.no_ap": {
        "ru": "❌ Не хватает ОД: нужно {cost}, доступно меньше. Восстановление — в новые сутки.",
        "en": "❌ Not enough AP: you need {cost}. AP comes back with the new day.",
    },
    "logging.swing": {
        "ru": "🪓 Ты размахиваешься топором и рубишь дерево...\nРезультат через {delay} секунд. Не поранься — и не дремли: в подлеске что-то шевелится!",
        "en": "🪓 You swing the axe at the tree...\nResult in {delay} seconds. Don't cut yourself — and don't doze: something moves in the undergrowth!",
    },
    "logging.alert.busy": {
        "ru": "Ты уже замахнулся топором — дождись результата!",
        "en": "You're already swinging — wait for the result!",
    },
    "logging.res.slip": {
        "ru": "{head}\n\nТопор от усталости неудачно отскакивает от мощного ствола и отлетает пилоту в плечо.\n\nРесурса не получено, попытка потрачена.",
        "en": "{head}\n\nThe axe glances off the thick trunk out of fatigue and bounces back at your shoulder.\n\nNo resource gained, the attempt is spent.",
    },
    "logging.res.wood_sell": {
        "ru": "\nКазна выкупает бревна по {price} {money} за штуку.",
        "en": "\nThe treasury buys logs at {price} {money} each.",
    },
    "logging.res.wood": {
        "ru": "{head}\n\nТопор звонко вгрызается в древесину — с ровным треском падает свежесрубленное бревно!\n\n🎒 Добыча: «{name}» — в инвентарь.{sell_line}",
        "en": "{head}\n\nThe axe bites into the wood with a clean crack — a freshly felled log drops!\n\n🎒 Loot: «{name}» — added to your inventory.{sell_line}",
    },
    "logging.res.lost": {
        "ru": "{head}\n\n🌲 Срубил что-то, но предмет потерялся. Сообщи хранителю.",
        "en": "{head}\n\n🌲 You felled something, but the item got lost. Tell the keeper.",
    },
    "logging.res.firewood_loot": {
        "ru": "\n\n🎒 Добыча: «{name}» — в инвентарь.",
        "en": "\n\n🎒 Loot: «{name}» — added to your inventory.",
    },
    "logging.res.firewood": {
        "ru": "{head}\n\nУдар за ударом — стружка летит, но сук топор не берёт: сучковатое дерево уходит на дрова.\nПробуй ещё!",
        "en": "{head}\n\nStrike after strike — chips fly, but the knot won't give to the axe: the knotty tree goes to firewood.\nKeep trying!",
    },
    "logging.bat.owl_lost": {
        "ru": "Когти впиваются в плечо, крыло обрушивает темноту — сознание гаснет...\n\nОчнулся ты у сторожки, весь в ссадинах. Неясыть ушла в чащу (−{removed} ОД).",
        "en": "Claws dig into your shoulder, a wing drowns you in darkness — you black out...\n\nYou come to by the lodge, bruised all over. The owl flew off into the thicket (−{removed} AP).",
    },
    "logging.bat.snake_lost": {
        "ru": "Мир плывёт, зубы холодят кровь — сознание гаснет...\n\nОчнулся ты у сторожки, тяжело дыша. Змея уползла в подлесок (−{removed} ОД).",
        "en": "The world swims, fangs chill your blood — you black out...\n\nYou come to by the lodge, gasping. The snake slid off into the undergrowth (−{removed} AP).",
    },
    "logging.bat.flee.snake": {
        "ru": "🏃 Ты отступаешь к сторожке, отмахиваясь от врага.\n\nБой окончен — но рубка-то не закончена! Попробуй ещё раз!",
        "en": "🏃 You back off toward the lodge, swatting at the enemy.\n\nThe fight is over — but the chopping isn't! Try again!",
    },
    "logging.bat.flee.owl": {
        "ru": "🏃 Ты отступаешь к сторожке, не сводя глаз с тяжёлого силуэта над кронами.\n\nСова ушла — и хорошо. Рубка-то не закончена! Попробуй ещё раз!",
        "en": "🏃 You back off toward the lodge, eyes on the heavy shape above the treetops.\n\nThe owl is gone — good. The chopping isn't finished! Try again!",
    },
    "logging.alert.tourist": {"ru": "⛔ На лесозаготовку туристов не пускают.", "en": "⛔ Tourists aren't allowed at the logging camp."},
    "logging.alert.in_dungeon": {"ru": "⛔ Ты в подземелье — рубить деревья нельзя!", "en": "⛔ You're in a dungeon — no chopping!"},
    "logging.alert.no_start": {"ru": "Сначала нажми /start", "en": "Press /start first"},
    "logging.mill.empty": {
        "ru": "🪚 Переработка\n\nУ тебя нет брёвен — сначала наруби деревьев.",
        "en": "🪚 Log processing\n\nYou have no logs — chop some trees first.",
    },
    "logging.alert.plank_dungeon": {"ru": "⛔ Ты в подземелье — тут не до распила.", "en": "⛔ You're in a dungeon — no time for sawing."},
    "logging.alert.no_logs": {"ru": "❌ Нет брёвен для распила.", "en": "❌ No logs to saw."},
    "logging.alert.plank_money": {
        "ru": "❌ Не хватает денег: распил одного бревна стоит {fee} НМ, а у тебя {nm}.",
        "en": "❌ Not enough money: sawing one log costs {fee} NM, you have {nm}.",
    },
    "logging.alert.wood_short": {"ru": "❌ Брёвен уже не хватает.", "en": "❌ Not enough logs anymore."},
    "logging.alert.fire_dungeon": {"ru": "⛔ Ты в подземелье — тут не до дров.", "en": "⛔ You're in a dungeon — no time for firewood."},
    "logging.fire.no_axe": {
        "ru": "❌ Чтобы наколоть дров, нужен топор. Купи «Топор» в магазине (категория «Добыча ресурсов»).",
        "en": "❌ You need an axe to split firewood. Buy one in the shop (Resource Mining).",
    },
    "logging.alert.fire_no_logs": {"ru": "❌ Нет брёвен для рубки на дрова.", "en": "❌ No logs for firewood."},
    "logging.alert.fire_ap": {
        "ru": "❌ Не хватает ОД: на одно бревно нужно {cost} ОД, а у тебя {ap}.",
        "en": "❌ Not enough AP: one log needs {cost} AP, you have {ap}.",
    },
    "logging.alert.no_ap": {"ru": "❌ Не хватает ОД.", "en": "❌ Not enough AP."},
    "logging.btn.chop": {"ru": "🪓 Рубить дерево", "en": "🪓 Chop a tree"},
    "logging.btn.chop_again": {"ru": "🪓 Рубить ещё", "en": "🪓 Chop again"},
    "logging.btn.mill": {"ru": "🪚 Переработка брёвен", "en": "🪚 Log processing"},
    "logging.btn.back": {"ru": "🔙 На прогалину", "en": "🔙 Back to the clearing"},
    "logging.btn.back_plain": {"ru": "🔙 Назад", "en": "🔙 Back"},
    "logging.btn.plank_one": {"ru": "🪚 1 бревно ({cnt})", "en": "🪚 1 log ({cnt})"},
    "logging.btn.plank_all": {"ru": "🪚 Всё ({cnt})", "en": "🪚 All ({cnt})"},
    "logging.btn.fire_one": {"ru": "🪓 1 бревно ({cnt} дров)", "en": "🪓 1 log ({cnt} firewood)"},
    "logging.btn.fire_all": {"ru": "🪓 Всё ({cnt} дров)", "en": "🪓 All ({cnt} firewood)"},
    "logging.btn.hit": {"ru": "⚔️ Ударить", "en": "⚔️ Strike"},
    "logging.btn.flee": {"ru": "🏃 Сбежать", "en": "🏃 Run away"},
    # Лес: зоны, вход и переходы (bot/handlers/forest.py).
    "forest.deny.clearing": {
        "ru": "Дальше — только настоящим пилотам Нордхайма. Прогалина за опушкой раскинулась на десятки вёрст, а тропы между лесами незнакомые: чужой здесь легко заблудиться. Туристов сюда не пускают — и правильно.",
        "en": "Only real Nordheim pilots go further. The clearing beyond the glade stretches for dozens of versts, and the paths between the woods are unfamiliar: a stranger gets lost easily here. Tourists aren't let in — and rightly so.",
    },
    "forest.deny.default": {"ru": "Сюда туристов не пускают.", "en": "Tourists aren't allowed here."},
    "forest.dungeon_block": {
        "ru": "⛔ Ты сейчас проходишь подземелье — бродить по лесу нельзя.\nВыйди из подземелья, а потом иди на {where}.",
        "en": "⛔ You're in a dungeon right now — no wandering through the forest.\nLeave the dungeon, then head to the {where}.",
    },
    "forest.where.glade": {"ru": "опушку", "en": "glade"},
    "forest.where.clearing": {"ru": "прогалину", "en": "clearing"},
    "forest.zone.head": {"ru": "{prefix}{emoji} {title}\n\n{body}", "en": "{prefix}{emoji} {title}\n\n{body}"},
    "forest.zone.closed": {
        "ru": "Сейчас сюда не пускают — зона закрыта. Загляни позже.",
        "en": "Entry is closed right now. Come back later.",
    },
    "forest.tourist_safe": {
        "ru": "Зато на опушке грибы собирают и туристы — там безопасно.",
        "en": "But mushrooms are gathered on the glade, and tourists are welcome there — it's safe.",
    },
    "forest.ap_line": {"ru": "⚡ ОД: {ap}/{ap_max}", "en": "⚡ AP: {ap}/{ap_max}"},
    "forest.ap_short": {
        "ru": " — не хватит на поиск ({cost} ОД), придёт с новыми сутками",
        "en": " — not enough for a search ({cost} AP), it comes back with the new day",
    },
    "forest.zone.glade_desc": {
        "ru": "Тёмный еловый лес начинается прямо за городской окраиной. На опушке — только самое простое: обычные грибы у дороги и изредка бледная поганка. Здесь спокойно, сюда пускают и туристов.",
        "en": "The dark spruce forest begins right past the city edge. The glade has only the simplest finds: common mushrooms by the road and the occasional death cap. It's calm here, and tourists are welcome.",
    },
    "forest.zone.clearing_desc": {
        "ru": "За опушкой начинается настоящий лес. Прогалина тянется далеко, и растут здесь все грибы, какие только есть в Нордхайме — от опёнка до ежовика гребенчатого.",
        "en": "Past the glade the real forest begins. The clearing stretches far, and every mushroom Nordheim has grows here — from honey fungus to hericium.",
    },
    "forest.zone.beasts": {"ru": "Здесь водятся звери: {parts}.", "en": "Beasts live here: {parts}."},
    "forest.zone.boar_chance": {"ru": "шанс встречи {chance}%", "en": "encounter chance {chance}%"},
    "forest.zone.boar_every": {
        "ru": "не чаще одного раза на {every} попыток",
        "en": "at most once every {every} searches",
    },
    "forest.zone.screen": {
        "ru": "{desc}\n\n{ap_line}\n\nПоиск стоит {cost} ОД, результат через 5–10 секунд.\n\n🧺 Казна покупает грибы не больше {limit} НМ в сутки — остальное можно продать на рынке игроков.",
        "en": "{desc}\n\n{ap_line}\n\nA search costs {cost} AP, result in 5–10 seconds.\n\n🧺 The treasury buys mushrooms up to {limit} NM a day — the rest can be sold on the players' market.",
    },
    "forest.alert.closed": {"ru": "Сюда пока не пускают.", "en": "Entry is closed for now."},
    "forest.alert.tourist": {"ru": "🌲 Сюда туристов не пускают.", "en": "🌲 Tourists aren't allowed here."},
    "forest.btn.to_glade": {"ru": "{emoji} К опушке", "en": "{emoji} To the glade"},
    "forest.btn.to_glade_plain": {"ru": "К опушке", "en": "To the glade"},
    "forest.btn.deeper": {"ru": "Углубиться в лес", "en": "Go deeper"},
    "forest.btn.cast": {"ru": "{emoji} Искать грибы", "en": "{emoji} Search mushrooms"},
    "forest.btn.berry": {"ru": "🫐 Искать ягоды", "en": "🫐 Search berries"},
    "forest.btn.log": {"ru": "🪓 Лесозаготовка", "en": "🪓 Logging camp"},
    "forest.btn.city": {"ru": "🔙 В город", "en": "🔙 To the city"},
    "logging.bat.expired": {"ru": "⏳ Бой устарел.", "en": "⏳ The fight is out of date."},
    "logging.bat.miss.snake": {
        "ru": "Ты бьёшь — но змея уходит в сторону, словно сквозь тень.\n\n",
        "en": "You strike — but the snake slips aside like a shadow.\n\n",
    },
    "logging.bat.miss.owl": {
        "ru": "Ты бьёшь — но неясыть отклоняется в воздухе, хлопая крылом.\n\n",
        "en": "You strike — but the owl swerves in the air, beating its wing.\n\n",
    },
    "logging.bat.armor.snake": {
        "ru": "🛡️ {amount} урона поглотила чешуя. ",
        "en": "🛡️ {amount} damage absorbed by its scales. ",
    },
    "logging.bat.armor.owl": {
        "ru": "🛡️ {amount} урона поглотило оперение. ",
        "en": "🛡️ {amount} damage absorbed by its feathers. ",
    },
    "logging.bat.hit": {
        "ru": "Ты бьёшь наотмашь: −{dmg} HP по врагу! {extra}\n\n",
        "en": "You strike hard: −{dmg} HP to the enemy! {extra}\n\n",
    },
    "logging.bat.owl_title": {"ru": "{emoji} НЕЯСЫТЬ", "en": "{emoji} OWL"},
    "logging.bat.owl_fled": {
        "ru": "Раненая неясыть бросает бой: тяжёлый силуэт вздымается над кронами и растворяется в сумерках. Ты победил!\n\n",
        "en": "The wounded owl gives up the fight: its heavy shape rises above the treetops and dissolves into dusk. You won!\n\n",
    },
    "logging.bat.owl_loot": {
        "ru": "Из-под крыла, которым неясыть прикрывала гнездо, падает:\n{loot}\n\nПоложено в инвентарь.",
        "en": "From under the wing the owl used to shield its nest, falls:\n{loot}\n\nAdded to your inventory.",
    },
    "logging.bat.owl_loot_none": {
        "ru": "Сова улетела, не роняя ничего — на этот раз обошлось без трофеев.",
        "en": "The owl flew off, dropping nothing — no trophies this time.",
    },
    "logging.bat.snake_loot": {
        "ru": "Из-под поверженной змеи ты забираешь:\n{loot}\n\nПоложено в инвентарь.",
        "en": "From under the fallen snake you take:\n{loot}\n\nAdded to your inventory.",
    },
    "logging.bat.snake_loot_none": {
        "ru": "Змея повержена, но ничего ценного на этот раз не нашлось.",
        "en": "The snake is down, but there was nothing valuable this time.",
    },
    "logging.bat.snake_title": {"ru": "{emoji} БОЙ СО ЗМЕЁЙ", "en": "{emoji} SNAKE FIGHT"},
    "logging.bat.snake_down": {
        "ru": "Змея дёргается и замирает — подлесок снова затихает.\n\n",
        "en": "The snake jerks and goes still — the undergrowth falls quiet again.\n\n",
    },
    "logging.bat.dodged": {
        "ru": "💨 Ты уклоняешься от выпада! (−0 HP)\n\n",
        "en": "💨 You dodge the lunge! (−0 HP)\n\n",
    },
    "logging.bat.counter.snake": {
        "ru": "Змея бьёт: −{dmg} HP. {extra}\n\n",
        "en": "The snake strikes: −{dmg} HP. {extra}\n\n",
    },
    "logging.bat.counter.owl": {
        "ru": "Неясыть бьёт когтем: −{dmg} HP. {extra}\n\n",
        "en": "The owl rakes you with a claw: −{dmg} HP. {extra}\n\n",
    },
    "logging.bat.owl_appears": {
        "ru": "Из чащи вылетает тяжёлый силуэт — Неясыть! Совиный глаз прикован к тебе.\n\n",
        "en": "A heavy shape bursts out of the thicket — an Owl! Its eye is fixed on you.\n\n",
    },
    "logging.bat.owl_tail": {
        "ru": "Сову нельзя убить — она сама решит, когда отступить.",
        "en": "You can't kill the owl — it will decide for itself when to back off.",
    },
    "logging.bat.snake_appears": {
        "ru": "Из-под валуна с шипением выползает длинная тень — Лесная змея!\n\n",
        "en": "A long shadow hisses out from under a boulder — a Forest Snake!\n\n",
    },
    "logging.bat.snake_tail": {
        "ru": "Ударь змею — или уноси ноги.",
        "en": "Strike the snake — or run for it.",
    },
    "logging.bat.round_tail": {"ru": "Ход {round}. {tail}", "en": "Turn {round}. {tail}"},
    "battle.hp.enemy": {"ru": "Враг   HP", "en": "Enemy  HP"},
    "logging.firewood.result": {
        "ru": ("🪓 РУБКА ДРОВ\n\n"
               "Ты ставишь бревно на плаху и работаешь топором: щепки веером, "
               "из {n} {n_w} вышло {firewood} «{name}» — {pack_verb} у сторожки.\n\n"
               "⚡ Потрачено ОД: {spent}.\n"
               "🎒 Получено: «{name}» x{firewood}.\n"
               "📦 Осталось: {left} {left_w}.\n\n"
               "{ap_line}"),
        "en": ("🪓 FIREWOOD CHOPPING\n\n"
               "You set the log on the block and work the axe: chips fly everywhere — "
               "{n} log(s) gave {firewood} «{name}», stacked by the lodge.\n\n"
               "⚡ AP spent: {spent}.\n"
               "🎒 Received: «{name}» x{firewood}.\n"
               "📦 Left: {left} {left_w}.\n\n"
               "{ap_line}"),
    },
    "logging.plank.result": {
        "ru": ("🪚 РАСПИЛ БРЁВЕН\n\n"
               "Артельные пилы визжат, опилки летят в лицо: {n} {n_w} {verb} в {planks} {planks_w}.\n\n"
               "💰 Заплачено артели: {fee} НМ (ушло в казну).\n"
               "🎒 Получено: «{name}» x{planks}.\n"
               "📦 Осталось: {left} {left_w}."),
        "en": ("🪚 LOG SAWING\n\n"
               "The mill saws whine, sawdust flies in your face: {n} log(s) become {planks} plank(s).\n\n"
               "💰 Paid to the mill: {fee} (to the treasury).\n"
               "🎒 Received: «{name}» x{planks}.\n"
               "📦 Left: {left} {left_w}."),
    },
    "logging.mill.screen": {
        "ru": ("🪚 ПЕРЕРАБОТКА БРЁВЕН\n\n"
               "🎒 В инвентаре: {inv}\n"
               "💰 Кошелёк: {nm} {nm_word} НМ\n"
               "⚡ ОД: {ap}\n\n"
               "🪚 Распил на доски (артель)\n"
               "   1 бревно → {py} {py_w} «{pn}», плата {fee} НМ за бревно (в казну), топор не нужен.\n"
               "   Доступно: {pw} {pw_w} → {pl} {pl_w}.\n\n"
               "🪓 Рубка дров (самостоятельно)\n"
               "   1 бревно → {fy} {fy_w} «{fn}», тратит {fap} ОД за бревно, нужен топор.\n"
               "   Доступно: {fwq} {fwq_w} → {fw} {fw_w} дров."),
        "en": ("🪚 LOG PROCESSING\n\n"
               "🎒 In inventory: {inv}\n"
               "💰 Purse: {nm} {nm_word}\n"
               "⚡ AP: {ap}\n\n"
               "🪚 Sawing into planks (the mill)\n"
               "   1 log → {py} {py_w} «{pn}», fee {fee} per log (to the treasury), no axe needed.\n"
               "   Available: {pw} {pw_w} → {pl} {pl_w}.\n\n"
               "🪓 Chopping firewood (by hand)\n"
               "   1 log → {fy} {fy_w} «{fn}», costs {fap} AP per log, needs an axe.\n"
               "   Available: {fwq} {fwq_w} → {fw} {fw_w} of firewood."),
    },
    "logging.tourist": {
        "ru": "⛔ На лесозаготовку не пускают туристов — это работа настоящих пилотов.",
        "en": "⛔ Tourists aren't allowed at the logging camp — this is real pilots' work.",
    },
    "logging.in_dungeon": {
        "ru": "⛔ Ты сейчас проходишь подземелье — рубить деревья нельзя.\nВыйди из подземелья, а потом возвращайся.",
        "en": "⛔ You're in a dungeon right now — no chopping.\nLeave the dungeon and come back.",
    },
    "logging.hint.has_axe": {
        "ru": "🪓 Топор: {name} (ступень {rank}, шанс рубки {chance}%) — за работу!",
        "en": "🪓 Axe: {name} (tier {rank}, chop chance {chance}%) — get to work!",
    },
    "logging.hint.no_axe": {
        "ru": "🪓 Без топора сюда не пускают: купи «Топор» (магазин → Добыча ресурсов).",
        "en": "🪓 No axe, no entry: buy an axe (Shop → Resource Mining).",
    },
    "logging.mill_hint": {
        "ru": "\n\n🪚 В сарае {qty} — можно распилить их на доски в артели или наколоть дров.",
        "en": "\n\n🪚 {qty} in the shed — you can saw them into planks at the mill or split them for firewood.",
    },
    "logging.entrance": {
        "ru": ("🪓 ЛЕСОЗАГОТОВКА\n\n"
               "За дальнейшей опушкой, там, где тропа уходит в самый глухой подлесок, "
               "стоит сторожка лесорубов. Здесь пахнет свежими стружками и хвоей — "
               "и отсюда редко кто возвращается с пустыми руками. Или вообще не возвращается.\n\n"
               "{hint}\n\n"
               "Рубка дерева стоит {cost} ОД, результат через {lo}–{hi} секунд.{mill_hint}\n\n"
               "{ap_line}"),
        "en": ("🪓 LOGGING CAMP\n\n"
               "Past the last clearing, where the path disappears into the thickest undergrowth, "
               "stands the loggers' lodge. It smells of fresh shavings and pine — "
               "and few come back from here empty-handed. Or not at all.\n\n"
               "{hint}\n\n"
               "A tree chop costs {cost} AP, result in {lo}–{hi} seconds.{mill_hint}\n\n"
               "{ap_line}"),
    },
    # Железная копь: вход, запреты, подсказки (bot/handlers/mine.py).
    "mine.stale": {
        "ru": "⏳ Это окно копи устарело — открой её заново (Город → Железная копи).",
        "en": "⏳ This mine window is out of date — reopen it (City → Iron Mine).",
    },
    "mine.tourist": {
        "ru": "⛔ В копи не пускают туристов — вход только с «Пилота 1 класса».",
        "en": "⛔ Tourists aren't allowed in the mine — entry is for Pilots 1st class only.",
    },
    "mine.in_dungeon": {
        "ru": "⛔ Ты сейчас проходишь подземелье — в копи нельзя.\nВыйди из подземелья, а потом возвращайся.",
        "en": "⛔ You're in a dungeon right now — no mine.\nLeave the dungeon and come back.",
    },
    "mine.hint.has_pickaxe": {
        "ru": "⛏ У тебя есть кирка: {name} — спускайся и бей породу.",
        "en": "⛏ You have a pickaxe: {name} — go down and strike the rock.",
    },
    "mine.hint.no_pickaxe": {
        "ru": "⛏ Без кирки в штольню не сунешься: купи «Кирка» (магазин → Добыча ресурсов).",
        "en": "⛏ You can't go down without a pickaxe: buy one (Shop → Resource Mining).",
    },
    "mine.entrance": {
        "ru": ("⛏ ЖЕЛЕЗНАЯ КОПЬ\n\n"
               "Лампы у входа мерцают, из штольни тянет холодом и запахом руды. "
               "Ворота открыты — но где-то в глубине шелестит крыльями здешняя хозяйка.\n\n"
               "{hint}\n\n"
               "Спустись на первый уровень шахт или вернись в город."),
        "en": ("⛏ IRON MINE\n\n"
               "Lamps flicker at the entrance, cold and the smell of ore drift up from the "
               "shaft. The gate is open — but somewhere deep below, the mine's mistress rustles her wings.\n\n"
               "{hint}\n\n"
               "Go down to the first mine level or head back to town."),
    },
    "mine.ap_line": {"ru": "⚡ ОД: {ap}/{ap_max}", "en": "⚡ AP: {ap}/{ap_max}"},
    "mine.ap_short": {
        "ru": " — на следующий удар не хватит ({cost} ОД)",
        "en": " — not enough for the next strike ({cost} AP)",
    },
    "mine.ap_ok": {"ru": " — можно копать ещё", "en": " — you can keep digging"},
    "mine.level.pickaxe_has": {
        "ru": "⛏ Кирка: {name} (ступень {rank}, шанс добычи {chance}%)",
        "en": "⛏ Pickaxe: {name} (tier {rank}, mining chance {chance}%)",
    },
    "mine.level.pickaxe_none": {
        "ru": "⛏ Кирка: нет — купи «Кирка» (магазин → Добыча ресурсов)",
        "en": "⛏ Pickaxe: none — buy one (Shop → Resource Mining)",
    },
    "mine.level.dig_hint": {
        "ru": "Бей породу — авось блеснёт руда. А может, что и пострашнее.",
        "en": "Strike the rock — maybe ore will glint. Or something worse.",
    },
    "mine.level.no_pickaxe_hint": {
        "ru": "Без кирки в штольню не сунешься: сначала разживись киркой.",
        "en": "You can't go down without a pickaxe: get one first.",
    },
    "mine.level.screen": {
        "ru": ("⛏ УРОВЕНЬ 1 ШАХТ\n\n"
               "Крепь из подгнивших балок уходит вглубь, под ногами хрустит щебень, "
               "фонарь выхватывает жилы руды в тёмной породе.\n\n"
               "{pickaxe_line}\n{dig_line}\n\n"
               "Удар киркой стоит {cost} ОД, результат через {lo}–{hi} секунд.\n\n"
               "{ap_line}"),
        "en": ("⛏ MINE LEVEL 1\n\n"
               "Rotten beams run deep into the dark, gravel crunches underfoot, "
               "the lamp catches veins of ore in the black rock.\n\n"
               "{pickaxe_line}\n{dig_line}\n\n"
               "A pickaxe strike costs {cost} AP, result in {lo}–{hi} seconds.\n\n"
               "{ap_line}"),
    },
    "mine.deeper_stub": {
        "ru": "🪜 Спуск на второй уровень ещё не обустроен — работы идут.",
        "en": "🪜 The second level isn't ready yet — work is in progress.",
    },
    "mine.alert.tourist": {"ru": "⛔ В копи не пускают туристов.", "en": "⛔ Tourists aren't allowed in the mine."},
    "mine.alert.busy": {
        "ru": "Ты уже замахнулся киркой — дождись результата!",
        "en": "You're already swinging — wait for the result!",
    },
    "mine.alert.in_dungeon": {"ru": "⛔ Ты в подземелье — в копи нельзя!", "en": "⛔ You're in a dungeon — no mine!"},
    "mine.btn.level1": {"ru": "⛏ Уровень 1 шахт", "en": "⛏ Mine level 1"},
    "mine.btn.dig": {"ru": "⛏ Добыть руду", "en": "⛏ Mine ore"},
    "mine.btn.deeper": {"ru": "🪜 Спуститься глубже", "en": "🪜 Go deeper"},
    "mine.btn.exit": {"ru": "🚪 Выйти из шахты", "en": "🚪 Leave the mine"},
    "mine.btn.dig_again": {"ru": "⛏ Добыть ещё", "en": "⛏ Mine again"},
    "mine.btn.hit": {"ru": "⚔️ Ударить", "en": "⚔️ Strike"},
    "mine.btn.flee": {"ru": "🏃 Сбежать", "en": "🏃 Flee"},
    "mine.bat_appears": {
        "ru": "Из темноты штольни с писком выныривает крылатая тень — Летучая мышь!\n\n",
        "en": "A winged shadow darts out of the dark shaft with a squeak — a Cave Bat!\n\n",
    },
    "battle.hp.bat": {"ru": "Мышь   HP", "en": "Bat    HP"},
    "battle.hp.you": {"ru": "Ты     HP", "en": "You    HP"},
    "battle.round_note": {
        "ru": "Ход {round}. Бей — или уходи подобру-поздорову.",
        "en": "Turn {round}. Strike — or slip away while you can.",
    },
    "mine.bat_expired": {
        "ru": "⏳ Бой с мышью устарел.",
        "en": "⏳ The bat fight is out of date.",
    },
    "mine.flame_found": {
        "ru": "{head}\n\nВ породе блеснул жар — из камня выкололся тёплый кусок пламенной руды!\n\n🎒 Добыча: «{name}» — в инвентарь.",
        "en": "{head}\n\nHeat flashed in the rock — a warm chunk of flame ore broke free!\n\n🎒 Loot: «{name}» — added to your inventory.",
    },
    "mine.ore_found": {
        "ru": "{head}\n\nКирка звонко высекает искру — из породы выкалывается кусок руды!\n\n🎒 Добыча: «{name}» — в инвентарь.{sell_line}",
        "en": "{head}\n\nThe pick strikes a spark — a lump of ore breaks out of the rock!\n\n🎒 Loot: «{name}» — added to your inventory.{sell_line}",
    },
    "mine.item_lost": {
        "ru": "{head}\n\n🔨 Что-то добыл, но предмет потерялся. Сообщи хранителю.",
        "en": "{head}\n\n🔨 You dug something up, but the item got lost. Tell the keeper.",
    },
    "mine.empty": {
        "ru": "{head}\n\nУдар за ударом — только каменная крошка да серый блеск.\nПорода сегодня пуста. Пробуй ещё!",
        "en": "{head}\n\nStrike after strike — only grit and grey glints.\nThe rock is empty today. Keep trying!",
    },
    "mine.no_pickaxe": {
        "ru": "❌ У тебя нет кирки. Купи «Кирка» в магазине (категория «Добыча ресурсов»).",
        "en": "❌ You have no pickaxe. Buy one in the shop (Resource Mining category).",
    },
    "mine.no_ap": {
        "ru": "❌ Не хватает ОД: нужно {cost}, доступно меньше. Восстановление — в новые сутки.",
        "en": "❌ Not enough AP: you need {cost}. AP comes back with the new day.",
    },
    "mine.swing": {
        "ru": "⛏ Ты замахиваешься киркой и бьёшь по породе...\nРезультат через {delay} секунд. Не шуми — прислушивайся!",
        "en": "⛏ You swing your pickaxe at the rock...\nResult in {delay} seconds. Keep quiet — listen!",
    },
    # Бой с летучей мышью в копи (bot/handlers/mine.py).
    "battle.mine.bat.title": {"ru": "{emoji} БОЙ С МЫШЬЮ", "en": "{emoji} BATTLE WITH THE BAT"},
    "battle.mine.bat.miss": {
        "ru": "Ты бьёшь — но мышь уходит в сторону с писком.\n\n",
        "en": "You swing — but the bat darts aside with a squeak.\n\n",
    },
    "battle.mine.bat.hit": {
        "ru": "Ты бьёшь наотмашь: −{dmg} HP по мыши! {extra}\n\n",
        "en": "You strike hard: −{dmg} HP to the bat! {extra}\n\n",
    },
    "battle.mine.bat.armor": {
        "ru": "🛡️ {amount} урона поглотила шкура. ",
        "en": "🛡️ {amount} damage absorbed by its hide. ",
    },
    "battle.mine.bat.dodged": {
        "ru": "💨 Ты уклоняешься от когтей! (−0 HP)\n\n",
        "en": "💨 You dodge the claws! (−0 HP)\n\n",
    },
    "battle.mine.bat.counter": {
        "ru": "Мышь вцепляется и бьёт: −{dmg} HP. {extra}\n\n",
        "en": "The bat clings on and bites: −{dmg} HP. {extra}\n\n",
    },
    "battle.mine.bat.down": {
        "ru": "Мышь с писком падает на каменный пол — в штольне снова тихо.\n\n",
        "en": "The bat drops to the stone floor with a squeak — the mine goes quiet again.\n\n",
    },
    "battle.mine.bat.loot": {
        "ru": "Ты выхватил из-под писка мыши:\n{loot}\n\nПоложено в инвентарь.",
        "en": "You snatch from under the bat's squeaks:\n{loot}\n\nAdded to your inventory.",
    },
    "battle.mine.bat.loot_none": {
        "ru": "Мышь повержена, но ничего ценного в ней не нашлось.",
        "en": "The bat is down, but there was nothing valuable in it.",
    },
    "battle.mine.bat.defeat": {
        "ru": ("В глазах темнеет, писк крыльев всё дальше...\n\n"
               "Ты приходишь в себя на полу штольни. Мышь улетела — но добычу "
               "придётся начать заново (−{removed} ОД)."),
        "en": ("Darkness closes in, the squeaking wings fade away...\n\n"
               "You come to on the mine floor. The bat has flown off — you'll have to "
               "start the haul over (−{removed} AP)."),
    },
    "battle.mine.bat.flee": {
        "ru": ("🏃 Ты отступаешь к выходу из штольни, отмахиваясь от писка крыльев.\n\n"
               "Мышь не преследует — но и добычи не будет. Попробуй ещё раз!"),
        "en": ("🏃 You back out of the mine, swatting at the squeaking wings.\n\n"
               "The bat doesn't follow — but there'll be no haul. Try again!"),
    },
    "battle.armor_absorbed_short": {"ru": "🛡️ Броня поглотила {amount}. ",
                                    "en": "🛡️ Armor absorbed {amount}. "},
    "battle.enemy_dodged": {
        "ru": "💨 {enemy} уклонился от удара! (−0 HP врагу)\n",
        "en": "💨 {enemy} dodged the blow! (−0 HP to the enemy)\n",
    },
    "battle.on_hit.bleed": {
        "ru": "🩸 {enemy} ранил тебя! Кровотечение: −{dmg} HP каждый ход до конца боя.",
        "en": "🩸 {enemy} cut you! Bleeding: −{dmg} HP each turn until the battle ends.",
    },
    "battle.on_hit.poison": {
        "ru": "☠️ {enemy} отравил тебя! Яд: −{dmg} HP каждый ход до конца боя.",
        "en": "☠️ {enemy} poisoned you! Poison: −{dmg} HP each turn until the battle ends.",
    },
    "battle.on_hit.frostbite": {
        "ru": "💧 {enemy} окутал тебя морозом! Обморожение: лечение −50%, {rounds} ход(ов).",
        "en": "💧 {enemy} wrapped you in frost! Frostbite: healing −50%, {rounds} turn(s).",
    },
    "battle.on_hit.state": {
        "ru": "{emoji} {enemy} накладывает «{title}» ({rounds} ход(ов)): {hint}",
        "en": "{emoji} {enemy} applies «{title}» ({rounds} turn(s)): {hint}",
    },
    "battle.dot_tick.bleed": {"ru": "🩸 Кровотечение: −{dmg} HP.", "en": "🩸 Bleeding: −{dmg} HP."},
    "battle.dot_tick.poison": {"ru": "☠️ Яд: −{dmg} HP.", "en": "☠️ Poison: −{dmg} HP."},
    "battle.effect.expired": {
        "ru": "{emoji} {title} прошло.",
        "en": "{emoji} {title} is over.",
    },
    "battle.status.bleed": {"ru": "🩸 Кровотечение −{dmg} HP/ход", "en": "🩸 Bleeding −{dmg} HP/turn"},
    "battle.status.poison": {"ru": "☠️ Яд −{dmg} HP/ход", "en": "☠️ Poison −{dmg} HP/turn"},
    "battle.status.frostbite": {
        "ru": "💧 Обморожение (лечение −50%)",
        "en": "💧 Frostbite (healing −50%)",
    },
    "battle.status.state_rounds": {
        "ru": "{emoji} {title} ({rounds} х.)",
        "en": "{emoji} {title} ({rounds} t.)",
    },
    "battle.status.state": {"ru": "{emoji} {title}", "en": "{emoji} {title}"},
    "battle.consumables_blocked": {
        "ru": "{emoji} {title}: в бою сейчас нельзя применять расходники и зелья.",
        "en": "{emoji} {title}: consumables and potions can't be used in battle right now.",
    },
    "battle.lifesteal": {"ru": "🩸 Кровопийца: +{healed} HP", "en": "🩸 Lifesteal: +{healed} HP"},
    "battle.enemy_attack": {
        "ru": "⚔️ {enemy} атакует! −{dmg} HP\n❤️ Осталось: {hp}/100",
        "en": "⚔️ {enemy} attacks! −{dmg} HP\n❤️ Left: {hp}/100",
    },
    "battle.player_attack": {
        "ru": "🗡️ Ты наносишь удар! −{dmg} HP\n{bar}",
        "en": "🗡️ You strike! −{dmg} HP\n{bar}",
    },
    "battle.boss_attack": {
        "ru": "💀 {boss} обрушивает удар! −{dmg} HP\n❤️ Осталось: {hp}/100",
        "en": "💀 {boss} unleashes a blow! −{dmg} HP\n❤️ Left: {hp}/100",
    },
    # Состояния игрока (utils/states.py): название и подсказка, по имени состояния.
    "state.пьян.title": {"ru": "Пьян", "en": "Drunk"},
    "state.пьян.hint": {
        "ru": "Выпил лишнего. В Ратушу, Библиотеку и Лабиринт не пускают, в бою руки не слушаются.",
        "en": "You had too much to drink. Town Hall, Library and the Labyrinth won't let you in; in battle your hands won't listen.",
    },
    "state.очень пьян.title": {"ru": "Очень пьян", "en": "Very drunk"},
    "state.очень пьян.hint": {
        "ru": ("Ты едва держишься на ногах: атака и уклонение сильно снижены, "
               "зелья и расходники недоступны, вход во все здания закрыт. Пройдёт через 6 часов."),
        "en": ("You can barely stand: attack and dodge are badly reduced, potions and "
               "consumables are unavailable, all buildings are closed. Passes in 6 hours."),
    },
    "state.истощён.title": {"ru": "Истощён", "en": "Exhausted"},
    "state.истощён.hint": {
        "ru": ("Истощение от перегрузки ОД: лимит восстановления за сутки исчерпан. "
               "Восстановление 75 ОД/сутки, максимум 90 ОД."),
        "en": ("Exhaustion from AP overload: the daily restore limit is used up. "
               "Restores 75 AP per day, up to 90 AP."),
    },
    "state.несварение.title": {"ru": "Несварение", "en": "Indigestion"},
    "state.несварение.hint": {
        "ru": ("Слишком много водорослей! Нельзя применять расходники (в том числе для "
               "восстановления ОД). Пройдёт через сутки."),
        "en": ("Too much seaweed! Consumables can't be used (including AP restore). "
               "Passes in a day."),
    },
    "state.внимание севера.title": {"ru": "Внимание Севера", "en": "Northern Attention"},
    "state.внимание севера.hint": {
        "ru": ("Белый Волк Севера заметил тебя и отпустил. +5% к урону и уклонению на сутки. "
               "Пока действует — волк не придёт снова."),
        "en": ("The White Wolf of the North noticed you and let you go. +5% damage and dodge "
               "for a day. While it lasts, the wolf won't come again."),
    },
    "state.благословение севера.title": {"ru": "Благословение Севера", "en": "Northern Blessing"},
    "state.благословение севера.hint": {
        "ru": ("Боги Нордхайма отметили тебя за встречу с Белым Волком: +10% к атаке и уклонению, "
               "+5% к лечению, −3% к ценам в магазинах на сутки. Пока действует — волк не придёт снова."),
        "en": ("The gods of Nordheim marked you for meeting the White Wolf: +10% attack and dodge, "
               "+5% healing, −3% shop prices for a day. While it lasts, the wolf won't come again."),
    },
    "state.ослеплён.title": {"ru": "Ослеплён", "en": "Blinded"},
    "state.ослеплён.hint": {
        "ru": "Неясыть ослепила тебя: в темноте удары мимо цели, уклонение едва работает.",
        "en": "The owl blinded you: in the dark your blows miss, and dodging barely works.",
    },
    "state.оглушён.title": {"ru": "Оглушён", "en": "Stunned"},
    "state.оглушён.hint": {
        "ru": "Оглушение: точность, крит и уклонение снижены, расходники недоступны.",
        "en": "Stunned: accuracy, crit and dodge reduced, consumables unavailable.",
    },
    "battle.weapon.stun_applied": {
        "ru": "\n{emoji} {attack}! Шанс {enemy} промахнуться: +{dmg}% ({ticks} хода).",
        "en": "\n{emoji} {attack}! {enemy} now has a +{dmg}% chance to miss ({ticks} turns).",
    },
    "battle.enemy.dot_status": {
        "ru": "\n{emoji} Враг под {label}: −{dmg} HP каждый ход (осталось {ticks} х.).",
        "en": "\n{emoji} Enemy under {label}: −{dmg} HP each turn ({ticks} turns left).",
    },
    "battle.enemy.stun_status": {
        "ru": "\n💫 Враг оглушён: его точность −{penalty}% (осталось {ticks} х.).",
        "en": "\n💫 Enemy stunned: its accuracy −{penalty}% ({ticks} turns left).",
    },
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
    "shop.limit_reached": {
        "ru": "❌ Лимит на руках: у тебя уже {held} шт. купленных в магазине, максимум {limit}. Потрать хотя бы одну, чтобы докупить.",
        "en": "❌ Hand limit reached: you already hold {held} shop-bought, the maximum is {limit}. Use some to buy more.",
    },
    "shop_limit.btn": {"ru": "🛒 Лимит на руках на аккаунт", "en": "🛒 Hand limit per account"},
    "shop_limit.ask": {
        "ru": ("🛒 «{name}» — сколько штук можно держать на руках, купленных в магазине?\n"
               "Сейчас: {cur}. Введи число от 0 до 1000 (0 — без лимита)."),
        "en": ("🛒 «{name}» — how many shop-bought units can one account hold?\n"
               "Now: {cur}. Enter a number from 0 to 1000 (0 — no limit)."),
    },
    "shop_limit.bad": {
        "ru": "❌ Введи целое число от 0 до 1000.",
        "en": "❌ Enter a whole number from 0 to 1000.",
    },
    "shop_limit.saved": {
        "ru": "✅ «{name}»: лимит на руках {n} шт. (0 — без лимита).",
        "en": "✅ «{name}»: hand limit is {n} (0 — no limit).",
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
