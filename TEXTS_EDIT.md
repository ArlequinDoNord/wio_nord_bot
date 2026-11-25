# TEXTS_EDIT.md — правки текстов интерфейса N.O.R.D.

> Как править: в блоке ключа впишите текст после «✏️ НОВЫЙ RU» / «✏️ НОВЫЙ EN» в виде
> JSON-строки в обратных кавычках, например `"Привет\nМир"`. Пустое поле — без изменений.
> Потом: `python tools/apply_texts.py` (проверка и запись в `utils/texts_overrides.json`).
> «ТЕКУЩИЙ» — только для чтения: это значение после применения всех правок.
> Подстановки `{name}` менять нельзя — набор должен совпадать с текущим текстом.
> Сущности из БД (предметы, враги, локации) сюда не входят: они правятся в админ-боте.


### activity_xp.gain

- ТЕКУЩИЙ RU: `"✨ +{n} XP"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"✨ +{n} XP"`
- ✏️ НОВЫЙ EN:


### activity_xp.limit

- ТЕКУЩИЙ RU: `"⚠️ Лимит усвоения опыта достигнут."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⚠️ Experience intake limit reached."`
- ✏️ НОВЫЙ EN:


### admin.fine_ask_amount

- ТЕКУЩИЙ RU: `"Сумма штрафа в НМ (целое число больше нуля):"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Fine amount in NM (whole number greater than zero):"`
- ✏️ НОВЫЙ EN:


### admin.fine_ask_reason

- ТЕКУЩИЙ RU: `"Причина штрафа (текст, будет показан пилоту):"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Fine reason (text, shown to the pilot):"`
- ✏️ НОВЫЙ EN:


### admin.fine_ask_user

- ТЕКУЩИЙ RU: `"Укажи ID пилота (число):"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Enter the pilot's ID (number):"`
- ✏️ НОВЫЙ EN:


### admin.fine_bad_number

- ТЕКУЩИЙ RU: `"❌ Нужно целое число больше нуля. Попробуй ещё раз:"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ A whole number greater than zero is required. Try again:"`
- ✏️ НОВЫЙ EN:


### admin.fine_cancel_btn

- ТЕКУЩИЙ RU: `"🗑 Отменить #{id}"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🗑 Cancel #{id}"`
- ✏️ НОВЫЙ EN:


### admin.fine_cancel_done

- ТЕКУЩИЙ RU: `"✅ Штраф #{id} отменён."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"✅ Fine #{id} cancelled."`
- ✏️ НОВЫЙ EN:


### admin.fine_issued

- ТЕКУЩИЙ RU: `"✅ Штраф #{id} наложен на {name}: {amount} НМ.\nПричина: {reason}"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"✅ Fine #{id} issued to {name}: {amount} NM.\nReason: {reason}"`
- ✏️ НОВЫЙ EN:


### admin.fine_list

- ТЕКУЩИЙ RU: `"📋 Активные штрафы"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"📋 Active fines"`
- ✏️ НОВЫЙ EN:


### admin.fine_new

- ТЕКУЩИЙ RU: `"➕ Наложить штраф"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"➕ Issue fine"`
- ✏️ НОВЫЙ EN:


### admin.fine_no_user

- ТЕКУЩИЙ RU: `"❌ Пилот с таким ID не найден. Укажи другой ID:"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ No pilot with that ID. Enter another ID:"`
- ✏️ НОВЫЙ EN:


### admin.fine_none

- ТЕКУЩИЙ RU: `"Активных штрафов нет."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"There are no active fines."`
- ✏️ НОВЫЙ EN:


### admin.fine_not_super

- ТЕКУЩИЙ RU: `"⛔ Штрафы накладывает только супер-админ."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⛔ Only the super admin can issue fines."`
- ✏️ НОВЫЙ EN:


### admin.fine_pick_user

- ТЕКУЩИЙ RU: `"Выбери пилота из списка или введи ID:"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Pick a pilot from the list or enter their ID:"`
- ✏️ НОВЫЙ EN:


### admin.fines_btn

- ТЕКУЩИЙ RU: `"⚖️ Штрафы"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⚖️ Fines"`
- ✏️ НОВЫЙ EN:


### admin.fines_menu

- ТЕКУЩИЙ RU: `"⚖️ Штрафы пилотов. Выбери действие:"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⚖️ Pilot fines. Choose an action:"`
- ✏️ НОВЫЙ EN:


### admin.tax_min_error

- ТЕКУЩИЙ RU: `"❌ Ставка налога на отчёты не ниже {minimum}% (и не выше 100%). Введи другое значение:"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ The report tax can't go below {minimum}% (and not above 100%). Enter another value:"`
- ✏️ НОВЫЙ EN:


### bank.back

- ТЕКУЩИЙ RU: `"🔙 В банк"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🔙 Back to bank"`
- ✏️ НОВЫЙ EN:


### bank.back_to_city

- ТЕКУЩИЙ RU: `"🔙 В город"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🔙 Back to city"`
- ✏️ НОВЫЙ EN:


### bank.fines_btn

- ТЕКУЩИЙ RU: `"⚖️ Штрафы"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⚖️ Fines"`
- ✏️ НОВЫЙ EN:


### bank.history_btn

- ТЕКУЩИЙ RU: `"История транзакций"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Transaction history"`
- ✏️ НОВЫЙ EN:


### bank.history_title

- ТЕКУЩИЙ RU: `"📜 История транзакций (стр. {page}):\n\n"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"📜 Transaction history (p. {page}):\n\n"`
- ✏️ НОВЫЙ EN:


### bank.my_balance

- ТЕКУЩИЙ RU: `"Мой баланс"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"My balance"`
- ✏️ НОВЫЙ EN:


### bank.newer

- ТЕКУЩИЙ RU: `"⬅️ Новее"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⬅️ Newer"`
- ✏️ НОВЫЙ EN:


### bank.no_txns

- ТЕКУЩИЙ RU: `"Пока нет транзакций."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"No transactions yet."`
- ✏️ НОВЫЙ EN:


### bank.older

- ТЕКУЩИЙ RU: `"Старее ▶️"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Older ▶️"`
- ✏️ НОВЫЙ EN:


### bank.taxes_btn

- ТЕКУЩИЙ RU: `"📋 Налоги и ставки"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"📋 Taxes and rates"`
- ✏️ НОВЫЙ EN:


### bank.taxes_contract

- ТЕКУЩИЙ RU: `"📜 Налог с контракта на поставку: {pct}% (платит тот, кто размещает контракт)"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"📜 Supply contract tax: {pct}% (paid by whoever places the contract)"`
- ✏️ НОВЫЙ EN:


### bank.taxes_footer

- ТЕКУЩИЙ RU: `"Ставки меняет владелец. Изменения видны здесь сразу."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Rates are set by the owner. Changes show up here right away."`
- ✏️ НОВЫЙ EN:


### bank.taxes_housing_free

- ТЕКУЩИЙ RU: `"• {name}: без налога"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"• {name}: no tax"`
- ✏️ НОВЫЙ EN:


### bank.taxes_housing_line

- ТЕКУЩИЙ RU: `"• {name}: {rate} НМ"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"• {name}: {rate} NM"`
- ✏️ НОВЫЙ EN:


### bank.taxes_housing_title

- ТЕКУЩИЙ RU: `"🏠 Налог на жильё (НМ в месяц):"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🏠 Housing tax (NM per month):"`
- ✏️ НОВЫЙ EN:


### bank.taxes_report

- ТЕКУЩИЙ RU: `"📊 Налог с отчётов: {base}% (удерживается из каждой выплаты в казну)"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"📊 Report tax: {base}% (taken from each payout into the treasury)"`
- ✏️ НОВЫЙ EN:


### bank.taxes_report_personal

- ТЕКУЩИЙ RU: `"🎖 Твоя ставка с отчётов: {pct}% (снижена наградами, но не ниже {minimum}%)"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🎖 Your report tax: {pct}% (reduced by awards, but not below {minimum}%)"`
- ✏️ НОВЫЙ EN:


### bank.taxes_sale

- ТЕКУЩИЙ RU: `"🛒 Налог с продаж: {pct}% (удерживается из выручки продавца)"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🛒 Sales tax: {pct}% (taken from the seller's proceeds)"`
- ✏️ НОВЫЙ EN:


### bank.taxes_title

- ТЕКУЩИЙ RU: `"🧾 СТАВКИ НАЛОГОВ\n\nДействуют сейчас:"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🧾 TAX RATES\n\nCurrently in effect:"`
- ✏️ НОВЫЙ EN:


### bank.to_treasury

- ТЕКУЩИЙ RU: `"🏛️ В казну"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🏛️ To treasury"`
- ✏️ НОВЫЙ EN:


### bank.transfer_btn

- ТЕКУЩИЙ RU: `"Перевести"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Transfer"`
- ✏️ НОВЫЙ EN:


### battle.armor_absorbed_short

- ТЕКУЩИЙ RU: `"🛡️ Броня поглотила {amount}. "`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🛡️ Armor absorbed {amount}. "`
- ✏️ НОВЫЙ EN:


### battle.armor_blocked

- ТЕКУЩИЙ RU: `"🛡️ Броня поглотила {amount} урона!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🛡️ Armor absorbed {amount} damage!"`
- ✏️ НОВЫЙ EN:


### battle.boss_attack

- ТЕКУЩИЙ RU: `"💀 {boss} обрушивает удар! −{dmg} HP\n❤️ Осталось: {hp}/100"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"💀 {boss} unleashes a blow! −{dmg} HP\n❤️ Left: {hp}/100"`
- ✏️ НОВЫЙ EN:


### battle.consumables_blocked

- ТЕКУЩИЙ RU: `"{emoji} {title}: в бою сейчас нельзя применять расходники и зелья."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"{emoji} {title}: consumables and potions can't be used in battle right now."`
- ✏️ НОВЫЙ EN:


### battle.crit

- ТЕКУЩИЙ RU: `"💥 crit!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"💥 crit!"`
- ✏️ НОВЫЙ EN:


### battle.crit_mark

- ТЕКУЩИЙ RU: `" 💥 crit!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `" 💥 crit!"`
- ✏️ НОВЫЙ EN:


### battle.crit_short

- ТЕКУЩИЙ RU: `"💥 crit! "`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"💥 crit! "`
- ✏️ НОВЫЙ EN:


### battle.dot_tick.bleed

- ТЕКУЩИЙ RU: `"🩸 Кровотечение: −{dmg} HP."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🩸 Bleeding: −{dmg} HP."`
- ✏️ НОВЫЙ EN:


### battle.dot_tick.poison

- ТЕКУЩИЙ RU: `"☠️ Яд: −{dmg} HP."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"☠️ Poison: −{dmg} HP."`
- ✏️ НОВЫЙ EN:


### battle.effect.expired

- ТЕКУЩИЙ RU: `"{emoji} {title} прошло."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"{emoji} {title} is over."`
- ✏️ НОВЫЙ EN:


### battle.enemy.dot_status

- ТЕКУЩИЙ RU: `"\n{emoji} Враг под {label}: −{dmg} HP каждый ход (осталось {ticks} х.)."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"\n{emoji} Enemy under {label}: −{dmg} HP each turn ({ticks} turns left)."`
- ✏️ НОВЫЙ EN:


### battle.enemy.stun_status

- ТЕКУЩИЙ RU: `"\n💫 Враг оглушён: его точность −{penalty}% (осталось {ticks} х.)."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"\n💫 Enemy stunned: its accuracy −{penalty}% ({ticks} turns left)."`
- ✏️ НОВЫЙ EN:


### battle.enemy.stunned_miss

- ТЕКУЩИЙ RU: `"💫 {enemy} оглушён и промахивается! (−0 HP)"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"💫 {enemy} is stunned and misses! (−0 HP)"`
- ✏️ НОВЫЙ EN:


### battle.enemy_attack

- ТЕКУЩИЙ RU: `"⚔️ {enemy} атакует! −{dmg} HP\n❤️ Осталось: {hp}/100"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⚔️ {enemy} attacks! −{dmg} HP\n❤️ Left: {hp}/100"`
- ✏️ НОВЫЙ EN:


### battle.enemy_dodged

- ТЕКУЩИЙ RU: `"💨 {enemy} уклонился от удара! (−0 HP врагу)\n"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"💨 {enemy} dodged the blow! (−0 HP to the enemy)\n"`
- ✏️ НОВЫЙ EN:


### battle.hp.bat

- ТЕКУЩИЙ RU: `"Мышь   HP"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Bat    HP"`
- ✏️ НОВЫЙ EN:


### battle.hp.enemy

- ТЕКУЩИЙ RU: `"Враг   HP"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Enemy  HP"`
- ✏️ НОВЫЙ EN:


### battle.hp.you

- ТЕКУЩИЙ RU: `"Ты     HP"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"You    HP"`
- ✏️ НОВЫЙ EN:


### battle.lifesteal

- ТЕКУЩИЙ RU: `"🩸 Кровопийца: +{healed} HP"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🩸 Lifesteal: +{healed} HP"`
- ✏️ НОВЫЙ EN:


### battle.mine.bat.armor

- ТЕКУЩИЙ RU: `"🛡️ {amount} урона поглотила шкура. "`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🛡️ {amount} damage absorbed by its hide. "`
- ✏️ НОВЫЙ EN:


### battle.mine.bat.counter

- ТЕКУЩИЙ RU: `"Мышь вцепляется и бьёт: −{dmg} HP. {extra}\n\n"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"The bat clings on and bites: −{dmg} HP. {extra}\n\n"`
- ✏️ НОВЫЙ EN:


### battle.mine.bat.defeat

- ТЕКУЩИЙ RU: `"В глазах темнеет, писк крыльев всё дальше...\n\nТы приходишь в себя на полу штольни. Мышь улетела — но добычу придётся начать заново (−{removed} ОД)."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Darkness closes in, the squeaking wings fade away...\n\nYou come to on the mine floor. The bat has flown off — you'll have to start the haul over (−{removed} AP)."`
- ✏️ НОВЫЙ EN:


### battle.mine.bat.dodged

- ТЕКУЩИЙ RU: `"💨 Ты уклоняешься от когтей! (−0 HP)\n\n"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"💨 You dodge the claws! (−0 HP)\n\n"`
- ✏️ НОВЫЙ EN:


### battle.mine.bat.down

- ТЕКУЩИЙ RU: `"Мышь с писком падает на каменный пол — в штольне снова тихо.\n\n"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"The bat drops to the stone floor with a squeak — the mine goes quiet again.\n\n"`
- ✏️ НОВЫЙ EN:


### battle.mine.bat.flee

- ТЕКУЩИЙ RU: `"🏃 Ты отступаешь к выходу из штольни, отмахиваясь от писка крыльев.\n\nМышь не преследует — но и добычи не будет. Попробуй ещё раз!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🏃 You back out of the mine, swatting at the squeaking wings.\n\nThe bat doesn't follow — but there'll be no haul. Try again!"`
- ✏️ НОВЫЙ EN:


### battle.mine.bat.hit

- ТЕКУЩИЙ RU: `"Ты бьёшь наотмашь: −{dmg} HP по мыши! {extra}\n\n"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"You strike hard: −{dmg} HP to the bat! {extra}\n\n"`
- ✏️ НОВЫЙ EN:


### battle.mine.bat.loot

- ТЕКУЩИЙ RU: `"Ты выхватил из-под писка мыши:\n{loot}\n\nПоложено в инвентарь."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"You snatch from under the bat's squeaks:\n{loot}\n\nAdded to your inventory."`
- ✏️ НОВЫЙ EN:


### battle.mine.bat.loot_none

- ТЕКУЩИЙ RU: `"Мышь повержена, но ничего ценного в ней не нашлось."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"The bat is down, but there was nothing valuable in it."`
- ✏️ НОВЫЙ EN:


### battle.mine.bat.miss

- ТЕКУЩИЙ RU: `"Ты бьёшь — но мышь уходит в сторону с писком.\n\n"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"You swing — but the bat darts aside with a squeak.\n\n"`
- ✏️ НОВЫЙ EN:


### battle.mine.bat.title

- ТЕКУЩИЙ RU: `"{emoji} БОЙ С МЫШЬЮ"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"{emoji} BATTLE WITH THE BAT"`
- ✏️ НОВЫЙ EN:


### battle.on_hit.bleed

- ТЕКУЩИЙ RU: `"🩸 {enemy} ранил тебя! Кровотечение: −{dmg} HP каждый ход до конца боя."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🩸 {enemy} cut you! Bleeding: −{dmg} HP each turn until the battle ends."`
- ✏️ НОВЫЙ EN:


### battle.on_hit.frostbite

- ТЕКУЩИЙ RU: `"💧 {enemy} окутал тебя морозом! Обморожение: лечение −50%, {rounds} ход(ов)."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"💧 {enemy} wrapped you in frost! Frostbite: healing −50%, {rounds} turn(s)."`
- ✏️ НОВЫЙ EN:


### battle.on_hit.poison

- ТЕКУЩИЙ RU: `"☠️ {enemy} отравил тебя! Яд: −{dmg} HP каждый ход до конца боя."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"☠️ {enemy} poisoned you! Poison: −{dmg} HP each turn until the battle ends."`
- ✏️ НОВЫЙ EN:


### battle.on_hit.state

- ТЕКУЩИЙ RU: `"{emoji} {enemy} накладывает «{title}» ({rounds} ход(ов)): {hint}"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"{emoji} {enemy} applies «{title}» ({rounds} turn(s)): {hint}"`
- ✏️ НОВЫЙ EN:


### battle.player.dodged

- ТЕКУЩИЙ RU: `"💨 Ты уклонился от атаки {enemy}! (−0 HP)"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"💨 You dodged the attack of {enemy}! (−0 HP)"`
- ✏️ НОВЫЙ EN:


### battle.player_attack

- ТЕКУЩИЙ RU: `"🗡️ Ты наносишь удар! −{dmg} HP\n{bar}"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🗡️ You strike! −{dmg} HP\n{bar}"`
- ✏️ НОВЫЙ EN:


### battle.round_note

- ТЕКУЩИЙ RU: `"Ход {round}. Бей — или уходи подобру-поздорову."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Turn {round}. Strike — or slip away while you can."`
- ✏️ НОВЫЙ EN:


### battle.status.bleed

- ТЕКУЩИЙ RU: `"🩸 Кровотечение −{dmg} HP/ход"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🩸 Bleeding −{dmg} HP/turn"`
- ✏️ НОВЫЙ EN:


### battle.status.frostbite

- ТЕКУЩИЙ RU: `"💧 Обморожение (лечение −50%)"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"💧 Frostbite (healing −50%)"`
- ✏️ НОВЫЙ EN:


### battle.status.poison

- ТЕКУЩИЙ RU: `"☠️ Яд −{dmg} HP/ход"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"☠️ Poison −{dmg} HP/turn"`
- ✏️ НОВЫЙ EN:


### battle.status.state

- ТЕКУЩИЙ RU: `"{emoji} {title}"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"{emoji} {title}"`
- ✏️ НОВЫЙ EN:


### battle.status.state_rounds

- ТЕКУЩИЙ RU: `"{emoji} {title} ({rounds} х.)"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"{emoji} {title} ({rounds} t.)"`
- ✏️ НОВЫЙ EN:


### battle.weapon.attack.bleed

- ТЕКУЩИЙ RU: `"Ты глубоко ранил врага — он истекает кровью"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"You cut the enemy deep — it bleeds"`
- ✏️ НОВЫЙ EN:


### battle.weapon.attack.burn

- ТЕКУЩИЙ RU: `"Ты поджёг врага — пламя лижет его броню"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"You set the enemy alight — flames lick its armor"`
- ✏️ НОВЫЙ EN:


### battle.weapon.attack.frostbite

- ТЕКУЩИЙ RU: `"Ты оковал врага холодом — мороз сковывает его тело"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"You chilled the enemy — frost locks its body"`
- ✏️ НОВЫЙ EN:


### battle.weapon.attack.poison

- ТЕКУЩИЙ RU: `"Ты отравил врага — яд въедается в рану"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"You poisoned the enemy — the venom seeps into the wound"`
- ✏️ НОВЫЙ EN:


### battle.weapon.attack.stun

- ТЕКУЩИЙ RU: `"Ты оглушил врага — его следующие удары неточны"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"You stunned the enemy — its next blows go astray"`
- ✏️ НОВЫЙ EN:


### battle.weapon.dot_applied

- ТЕКУЩИЙ RU: `"\n{emoji} {attack}! {label}: −{dmg} HP врагу каждый ход ({ticks} хода)."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"\n{emoji} {attack}! {label}: −{dmg} HP to the enemy each turn ({ticks} turns)."`
- ✏️ НОВЫЙ EN:


### battle.weapon.dot_cancelled

- ТЕКУЩИЙ RU: `"\n{emoji} {attack}! Но {label} врага уже гасит этот эффект — оба снимаются."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"\n{emoji} {attack}! But the enemy already has {label} — both cancel out."`
- ✏️ НОВЫЙ EN:


### battle.weapon.immune

- ТЕКУЩИЙ RU: `"\n🛡 {enemy} невосприимчив к «{label}» — эффект не сработал."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"\n🛡 {enemy} is immune to «{label}» — the effect did nothing."`
- ✏️ НОВЫЙ EN:


### battle.weapon.label.bleed

- ТЕКУЩИЙ RU: `"кровотечение"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"bleeding"`
- ✏️ НОВЫЙ EN:


### battle.weapon.label.burn

- ТЕКУЩИЙ RU: `"поджиг"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"burning"`
- ✏️ НОВЫЙ EN:


### battle.weapon.label.frostbite

- ТЕКУЩИЙ RU: `"обморожение"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"frostbite"`
- ✏️ НОВЫЙ EN:


### battle.weapon.label.poison

- ТЕКУЩИЙ RU: `"отравление"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"poison"`
- ✏️ НОВЫЙ EN:


### battle.weapon.label.stun

- ТЕКУЩИЙ RU: `"оглушение"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"stun"`
- ✏️ НОВЫЙ EN:


### battle.weapon.stun_applied

- ТЕКУЩИЙ RU: `"\n{emoji} {attack}! Шанс {enemy} промахнуться: +{dmg}% ({ticks} хода)."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"\n{emoji} {attack}! {enemy} now has a +{dmg}% chance to miss ({ticks} turns)."`
- ✏️ НОВЫЙ EN:


### btn.admin

- ТЕКУЩИЙ RU: `"👑 Админ-панель"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"👑 Admin panel"`
- ✏️ НОВЫЙ EN:


### btn.city

- ТЕКУЩИЙ RU: `"Город"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"City"`
- ✏️ НОВЫЙ EN:


### btn.housing

- ТЕКУЩИЙ RU: `"🏠 Жильё"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🏠 Housing"`
- ✏️ НОВЫЙ EN:


### btn.inventory

- ТЕКУЩИЙ RU: `"Инвентарь"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Inventory"`
- ✏️ НОВЫЙ EN:


### btn.lang

- ТЕКУЩИЙ RU: `"🌐 English"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🌐 Русский"`
- ✏️ НОВЫЙ EN:


### btn.news

- ТЕКУЩИЙ RU: `"📰 Новости Нордхайма"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"📰 Nordheim news"`
- ✏️ НОВЫЙ EN:


### btn.profile

- ТЕКУЩИЙ RU: `"Профиль"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Profile"`
- ✏️ НОВЫЙ EN:


### btn.report

- ТЕКУЩИЙ RU: `"📝 Сдать отчёт"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"📝 Submit report"`
- ✏️ НОВЫЙ EN:


### btn.shop

- ТЕКУЩИЙ RU: `"Магазин"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Shop"`
- ✏️ НОВЫЙ EN:


### btn.wall

- ТЕКУЩИЙ RU: `"🧱 Стена изречений"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🧱 Wall of sayings"`
- ✏️ НОВЫЙ EN:


### cat.building

- ТЕКУЩИЙ RU: `"Недвижимость"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Real estate"`
- ✏️ НОВЫЙ EN:


### cat.consumable

- ТЕКУЩИЙ RU: `"Расходники"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Consumables"`
- ✏️ НОВЫЙ EN:


### cat.documents

- ТЕКУЩИЙ RU: `"Документы"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Documents"`
- ✏️ НОВЫЙ EN:


### cat.duel_card

- ТЕКУЩИЙ RU: `"🎫 Клубные карты"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🎫 Club cards"`
- ✏️ НОВЫЙ EN:


### cat.duel_gear

- ТЕКУЩИЙ RU: `"🥊 Дуэльное снаряжение"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🥊 Duel gear"`
- ✏️ НОВЫЙ EN:


### cat.equipment

- ТЕКУЩИЙ RU: `"Одежда"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Clothing"`
- ✏️ НОВЫЙ EN:


### cat.fishing

- ТЕКУЩИЙ RU: `"Рыбалка"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Fishing"`
- ✏️ НОВЫЙ EN:


### cat.furniture

- ТЕКУЩИЙ RU: `"Мебель и расширения"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Furniture & extensions"`
- ✏️ НОВЫЙ EN:


### cat.housing

- ТЕКУЩИЙ RU: `"Жильё"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Housing"`
- ✏️ НОВЫЙ EN:


### cat.library_card

- ТЕКУЩИЙ RU: `"Читательские билеты"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Library cards"`
- ✏️ НОВЫЙ EN:


### cat.license

- ТЕКУЩИЙ RU: `"Торговые лицензии"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Trade licenses"`
- ✏️ НОВЫЙ EN:


### cat.market

- ТЕКУЩИЙ RU: `"🎪 Рынок"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🎪 Market"`
- ✏️ НОВЫЙ EN:


### cat.mining

- ТЕКУЩИЙ RU: `"⛏ Добыча ресурсов"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⛏ Resource mining"`
- ✏️ НОВЫЙ EN:


### cat.recipes

- ТЕКУЩИЙ RU: `"📜 Рецепты"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"📜 Recipes"`
- ✏️ НОВЫЙ EN:


### cat.resource

- ТЕКУЩИЙ RU: `"Ресурсы"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Resources"`
- ✏️ НОВЫЙ EN:


### cat.seeds

- ТЕКУЩИЙ RU: `"Семена"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Seeds"`
- ✏️ НОВЫЙ EN:


### cat.souvenirs

- ТЕКУЩИЙ RU: `"Сувениры"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Souvenirs"`
- ✏️ НОВЫЙ EN:


### cat.special

- ТЕКУЩИЙ RU: `"Особое"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Special"`
- ✏️ НОВЫЙ EN:


### cat.special_dept

- ТЕКУЩИЙ RU: `"Спец-отдел"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Special Department"`
- ✏️ НОВЫЙ EN:


### cat.weapon

- ТЕКУЩИЙ RU: `"Оружие"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Weapons"`
- ✏️ НОВЫЙ EN:


### city.admin

- ТЕКУЩИЙ RU: `"🏢 Административный квартал"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🏢 Administrative quarter"`
- ✏️ НОВЫЙ EN:


### city.back

- ТЕКУЩИЙ RU: `"🔙 В город"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🔙 Back to city"`
- ✏️ НОВЫЙ EN:


### city.business

- ТЕКУЩИЙ RU: `"💼 Деловой квартал"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"💼 Business quarter"`
- ✏️ НОВЫЙ EN:


### city.caption

- ТЕКУЩИЙ RU: `"🏰 Город Аркхольм:"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🏰 City of Arkholm:"`
- ✏️ НОВЫЙ EN:


### city.countryside

- ТЕКУЩИЙ RU: `"🌲 Загородные территории"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🌲 Countryside"`
- ✏️ НОВЫЙ EN:


### city.speech_none

- ТЕКУЩИЙ RU: `"📢 Речь представителя: пока не произнесена."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"📢 Representative's speech: not given yet."`
- ✏️ НОВЫЙ EN:


### city.speech_title

- ТЕКУЩИЙ RU: `"📢 Речь представителя"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"📢 Representative's speech"`
- ✏️ НОВЫЙ EN:


### common.back

- ТЕКУЩИЙ RU: `"Назад"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Back"`
- ✏️ НОВЫЙ EN:


### duel.accept.ap_now

- ТЕКУЩИЙ RU: `"⛔ Дуэль не состоялась: у соперника не хватило ОД."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⛔ The duel didn't happen: your opponent is short on AP."`
- ✏️ НОВЫЙ EN:


### duel.accept.failed

- ТЕКУЩИЙ RU: `"Не удалось начать дуэль."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"The duel couldn't start."`
- ✏️ НОВЫЙ EN:


### duel.accept.need_ap

- ТЕКУЩИЙ RU: `"⛔ Для дуэли нужно {ap} ОД."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⛔ The duel needs {ap} AP."`
- ✏️ НОВЫЙ EN:


### duel.accept.need_card

- ТЕКУЩИЙ RU: `"Нужна клубная карта, чтобы принять вызов."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"You need a club card to accept the challenge."`
- ✏️ НОВЫЙ EN:


### duel.accept.nocard_now

- ТЕКУЩИЙ RU: `"У соперника больше нет клубной карты — вызов отменён."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Your opponent no longer has a club card — challenge cancelled."`
- ✏️ НОВЫЙ EN:


### duel.accept.push_ap

- ТЕКУЩИЙ RU: `"⛔ Дуэль не состоялась: не хватило ОД."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⛔ The duel didn't happen: not enough AP."`
- ✏️ НОВЫЙ EN:


### duel.accept.push_nocard

- ТЕКУЩИЙ RU: `"⛔ Дуэль не состоялась: у соперника нет клубной карты."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⛔ The duel didn't happen: your opponent has no club card."`
- ✏️ НОВЫЙ EN:


### duel.accept.stale

- ТЕКУЩИЙ RU: `"Этот вызов уже неактуален."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"This challenge is no longer valid."`
- ✏️ НОВЫЙ EN:


### duel.access_denied

- ТЕКУЩИЙ RU: `"⛔ Дом Дуэлей открыт с «Пилота 2 класса».\nПодрасти в звании — и добро пожаловать на арену."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⛔ The Duel House opens to Class 2 pilots.\nRank up — and you're welcome in the arena."`
- ✏️ НОВЫЙ EN:


### duel.btn.accept

- ТЕКУЩИЙ RU: `"✅ Принять"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"✅ Accept"`
- ✏️ НОВЫЙ EN:


### duel.btn.back

- ТЕКУЩИЙ RU: `"🔙 Назад"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🔙 Back"`
- ✏️ НОВЫЙ EN:


### duel.btn.back_house

- ТЕКУЩИЙ RU: `"🔙 В Дом Дуэлей"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🔙 To the Duel House"`
- ✏️ НОВЫЙ EN:


### duel.btn.back_house_alt

- ТЕКУЩИЙ RU: `"🔁 В Дом Дуэлей"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🔁 To the Duel House"`
- ✏️ НОВЫЙ EN:


### duel.btn.buy_card

- ТЕКУЩИЙ RU: `"🛒 Купить клубную карту ({price} НМ)"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🛒 Buy club card ({price} NM)"`
- ✏️ НОВЫЙ EN:


### duel.btn.cancel_invite

- ТЕКУЩИЙ RU: `"🚪 Отменить вызов"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🚪 Cancel challenge"`
- ✏️ НОВЫЙ EN:


### duel.btn.city

- ТЕКУЩИЙ RU: `"🔙 В город"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🔙 To the city"`
- ✏️ НОВЫЙ EN:


### duel.btn.decline

- ТЕКУЩИЙ RU: `"❌ Отклонить"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ Decline"`
- ✏️ НОВЫЙ EN:


### duel.btn.help

- ТЕКУЩИЙ RU: `"❓ Правила"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❓ Rules"`
- ✏️ НОВЫЙ EN:


### duel.btn.invite

- ТЕКУЩИЙ RU: `"🎯 Вызвать на дуэль"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🎯 Challenge to a duel"`
- ✏️ НОВЫЙ EN:


### duel.btn.leave

- ТЕКУЩИЙ RU: `"🚪 Покинуть дуэль"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🚪 Leave the duel"`
- ✏️ НОВЫЙ EN:


### duel.btn.top

- ТЕКУЩИЙ RU: `"🏆 Рейтинг арены"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🏆 Arena ranking"`
- ✏️ НОВЫЙ EN:


### duel.card.access

- ТЕКУЩИЙ RU: `"⛔ Клубная карта доступна с «Пилота 2 класса»."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⛔ The club card is available from Class 2 pilot."`
- ✏️ НОВЫЙ EN:


### duel.card.bought

- ТЕКУЩИЙ RU: `"Клубная карта куплена!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Club card bought!"`
- ✏️ НОВЫЙ EN:


### duel.card.has

- ТЕКУЩИЙ RU: `"У тебя уже есть клубная карта."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"You already have a club card."`
- ✏️ НОВЫЙ EN:


### duel.card.no

- ТЕКУЩИЙ RU: `"нет"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"no"`
- ✏️ НОВЫЙ EN:


### duel.card.no_money

- ТЕКУЩИЙ RU: `"Не хватает НМ (нужно {price})."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Not enough NM (need {price})."`
- ✏️ НОВЫЙ EN:


### duel.card.unavailable

- ТЕКУЩИЙ RU: `"❌ Товар временно недоступен."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ Item temporarily unavailable."`
- ✏️ НОВЫЙ EN:


### duel.card.yes

- ТЕКУЩИЙ RU: `"есть"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"yes"`
- ✏️ НОВЫЙ EN:


### duel.challenge.sent

- ТЕКУЩИЙ RU: `"⚔️ ВЫЗОВ БРОШЕН\n────────────────\nТы вызвал: {name}.\nНачало боя спишет {ap} ОД у обоих.\nЖдём ответа соперника…"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⚔️ CHALLENGE SENT\n────────────────\nYou challenged: {name}.\nStarting the bout costs {ap} AP from both.\nWaiting for an answer…"`
- ✏️ НОВЫЙ EN:


### duel.decline.done

- ТЕКУЩИЙ RU: `"Вызов отклонён."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Challenge declined."`
- ✏️ НОВЫЙ EN:


### duel.end.draw

- ТЕКУЩИЙ RU: `"🤝 Ничья."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🤝 Draw."`
- ✏️ НОВЫЙ EN:


### duel.end.draw_head

- ТЕКУЩИЙ RU: `"🤝 НИЧЬЯ"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🤝 DRAW"`
- ✏️ НОВЫЙ EN:


### duel.end.lost

- ТЕКУЩИЙ RU: `"💀 Ты проиграл."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"💀 You lost."`
- ✏️ НОВЫЙ EN:


### duel.end.no_change

- ТЕКУЩИЙ RU: `"Рейтинг не изменился."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Rating unchanged."`
- ✏️ НОВЫЙ EN:


### duel.end.win_head

- ТЕКУЩИЙ RU: `"🏆 ПОБЕДА"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🏆 VICTORY"`
- ✏️ НОВЫЙ EN:


### duel.end.winner

- ТЕКУЩИЙ RU: `"Победитель: {name}. +{win} / {loss} рейтинга."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Winner: {name}. +{win} / {loss} rating."`
- ✏️ НОВЫЙ EN:


### duel.end.won

- ТЕКУЩИЙ RU: `"🏆 Ты победил!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🏆 You won!"`
- ✏️ НОВЫЙ EN:


### duel.ended

- ТЕКУЩИЙ RU: `"Дуэль уже завершена."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"The duel is already over."`
- ✏️ НОВЫЙ EN:


### duel.gear.off

- ТЕКУЩИЙ RU: `"не надето"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"none equipped"`
- ✏️ НОВЫЙ EN:


### duel.gear.on

- ТЕКУЩИЙ RU: `"+{dmg} урона"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"+{dmg} damage"`
- ✏️ НОВЫЙ EN:


### duel.help

- ТЕКУЩИЙ RU: `"🥊 ДОМ ДУЭЛЕЙ — ПРАВИЛА\n────────────────\n• Каждый раунд оба тайно выбирают зону атаки и зону защиты (Голова / Тело / Руки / Ноги).\n• Если защита угадала зону атаки — удар гасится вдвое.\n• Раунд резолвится, когда выбор сделали оба.\n• Старт боя стоит {ap} ОД каждому.\n• Рейтинг: победа +{win}, поражение {loss}, ничья {draw}.\n• Покинул бой — {forfeit} и поражение, сопернику +{forfeit_win} и победа.\n• Дуэльные перчатки работают только на арене."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🥊 DUEL HOUSE — RULES\n────────────────\n• Each round both secretly pick an attack zone and a guard zone (Head / Body / Arms / Legs).\n• If your guard matches the enemy's attack zone, the hit is halved.\n• The round resolves once both have chosen.\n• A bout costs {ap} AP from each side.\n• Rating: win +{win}, loss {loss}, draw {draw}.\n• Leave the fight — {forfeit} and a loss; your opponent gets +{forfeit_win} and a win.\n• Duel gloves work only in the arena."`
- ✏️ НОВЫЙ EN:


### duel.invite.busy

- ТЕКУЩИЙ RU: `"У тебя или соперника уже идёт поединок."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"You or your opponent are already in a bout."`
- ✏️ НОВЫЙ EN:


### duel.invite.no_card

- ТЕКУЩИЙ RU: `"У соперника нет клубной карты."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Your opponent has no club card."`
- ✏️ НОВЫЙ EN:


### duel.invite.not_admitted

- ТЕКУЩИЙ RU: `"Этот пилот ещё не допущен к арене."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"This pilot isn't admitted to the arena yet."`
- ✏️ НОВЫЙ EN:


### duel.invite.not_found

- ТЕКУЩИЙ RU: `"Пилот не найден."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Pilot not found."`
- ✏️ НОВЫЙ EN:


### duel.invite.self

- ТЕКУЩИЙ RU: `"Нельзя вызвать себя."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"You can't challenge yourself."`
- ✏️ НОВЫЙ EN:


### duel.invite.sent

- ТЕКУЩИЙ RU: `"Вызов брошен!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Challenge sent!"`
- ✏️ НОВЫЙ EN:


### duel.invite.text

- ТЕКУЩИЙ RU: `"⚔️ ТЕБЯ ВЫЗВАЛИ НА ДУЭЛЬ\n────────────────\n{name} вызывает тебя на арену!\n\nСтарт боя спишет {ap} ОД у обоих. Решение за тобой."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⚔️ YOU'VE BEEN CHALLENGED\n────────────────\n{name} challenges you to the arena!\n\nStarting the bout costs {ap} AP from both. The choice is yours."`
- ✏️ НОВЫЙ EN:


### duel.left.opp

- ТЕКУЩИЙ RU: `"🏆 Соперник покинул дуэль — победа за тобой!\nРейтинг: +{rating}."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🏆 Your opponent left the duel — you win!\nRating: +{rating}."`
- ✏️ НОВЫЙ EN:


### duel.left.self

- ТЕКУЩИЙ RU: `"🚪 Ты покинул дуэль. Рейтинг: {rating}."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🚪 You left the duel. Rating: {rating}."`
- ✏️ НОВЫЙ EN:


### duel.list.head

- ТЕКУЩИЙ RU: `"🎯 Кого вызвать на дуэль?"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🎯 Who do you challenge?"`
- ✏️ НОВЫЙ EN:


### duel.list.none

- ТЕКУЩИЙ RU: `"— пока некого вызвать —"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"— no one to challenge yet —"`
- ✏️ НОВЫЙ EN:


### duel.menu

- ТЕКУЩИЙ RU: `"🥊 ДОМ ДУЭЛЕЙ\n────────────────\nАрена чести: поединки один на один «зона на зону».\n\n🏅 Рейтинг: {rating}\n🏆 Побед: {wins}   💀 Поражений: {losses}\n🎫 Клубная карта: {card}\n🥊 Дуэльное снаряжение: {gear}\n💰 Кошелёк: {nm} НМ\n⚔️ Старт дуэли: {ap} ОД с каждого участника"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🥊 DUEL HOUSE\n────────────────\nHonor arena: one-on-one bouts, «zone against zone».\n\n🏅 Rating: {rating}\n🏆 Wins: {wins}   💀 Losses: {losses}\n🎫 Club card: {card}\n🥊 Duel gear: {gear}\n💰 Purse: {nm} NM\n⚔️ Duel start: {ap} AP from each side"`
- ✏️ НОВЫЙ EN:


### duel.need_card

- ТЕКУЩИЙ RU: `"Нужна клубная карта."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"You need a club card."`
- ✏️ НОВЫЙ EN:


### duel.not_yours

- ТЕКУЩИЙ RU: `"Это не твоя дуэль."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"This isn't your duel."`
- ✏️ НОВЫЙ EN:


### duel.pick.def_head

- ТЕКУЩИЙ RU: `"🎯 Бьёшь в: {zone_emoji} {zone_label}.\nТеперь выбери, что защищаешь:"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🎯 Striking at: {zone_emoji} {zone_label}.\nNow pick what you guard:"`
- ✏️ НОВЫЙ EN:


### duel.push.cancelled

- ТЕКУЩИЙ RU: `"⚔️ Вызов отменён."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⚔️ Challenge cancelled."`
- ✏️ НОВЫЙ EN:


### duel.push.declined

- ТЕКУЩИЙ RU: `"❌ Соперник отклонил вызов."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ Your opponent declined the challenge."`
- ✏️ НОВЫЙ EN:


### duel.round.head

- ТЕКУЩИЙ RU: `"⚔️ ДОМ ДУЭЛЕЙ — РАУНД {turn}\n────────────────\n🎯 {me_name}  {my_bar} {my_hp}/{my_max}\n🥊 {op_name}  {op_bar} {op_hp}/{op_max}"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⚔️ DUEL HOUSE — ROUND {turn}\n────────────────\n🎯 {me_name}  {my_bar} {my_hp}/{my_max}\n🥊 {op_name}  {op_bar} {op_hp}/{op_max}"`
- ✏️ НОВЫЙ EN:


### duel.round.num

- ТЕКУЩИЙ RU: `"— Раунд {turn} —"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"— Round {turn} —"`
- ✏️ НОВЫЙ EN:


### duel.round.pick_atk

- ТЕКУЩИЙ RU: `"\n\nКуда бьёшь?"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"\n\nWhere do you strike?"`
- ✏️ НОВЫЙ EN:


### duel.round.picked

- ТЕКУЩИЙ RU: `"\n\n✅ Ты выбрал: {atk_emoji} {atk_label} (атака), {def_label} (защита).\nЖдём соперника…"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"\n\n✅ You picked: {atk_emoji} {atk_label} (attack), {def_label} (guard).\nWaiting for your opponent…"`
- ✏️ НОВЫЙ EN:


### duel.round.theirs

- ТЕКУЩИЙ RU: `"🛡 "`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🛡 "`
- ✏️ НОВЫЙ EN:


### duel.strike.crit

- ТЕКУЩИЙ RU: `"💥 КРИТ! "`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"💥 CRIT! "`
- ✏️ НОВЫЙ EN:


### duel.strike.dodged

- ТЕКУЩИЙ RU: `"🎯 Удар в {zone}: соперник уклонился"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🎯 Strike to {zone}: the opponent dodged"`
- ✏️ НОВЫЙ EN:


### duel.strike.guard

- ТЕКУЩИЙ RU: `" (парировано)"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `" (blocked)"`
- ✏️ НОВЫЙ EN:


### duel.strike.hit

- ТЕКУЩИЙ RU: `"🎯 Удар в {zone}: −{dmg} HP"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🎯 Strike to {zone}: −{dmg} HP"`
- ✏️ НОВЫЙ EN:


### duel.top.empty

- ТЕКУЩИЙ RU: `"Пока никто не сражался."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Nobody has fought yet."`
- ✏️ НОВЫЙ EN:


### duel.top.head

- ТЕКУЩИЙ RU: `"🏆 РЕЙТИНГ АРЕНЫ"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🏆 ARENA RANKING"`
- ✏️ НОВЫЙ EN:


### dungeon.alert.stale_fight

- ТЕКУЩИЙ RU: `"⚠️ Это устаревшая кнопка. Используй кнопки из последнего сообщения боя."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⚠️ This button is out of date. Use the buttons from the last fight message."`
- ✏️ НОВЫЙ EN:


### dungeon.alert.stale_reopen

- ТЕКУЩИЙ RU: `"⚠️ Это устаревшая кнопка. Открой подземелье заново и продолжай с последнего сообщения."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⚠️ This button is out of date. Reopen the dungeon and continue from the last message."`
- ✏️ НОВЫЙ EN:


### dungeon.antidote.useless

- ТЕКУЩИЙ RU: `"Ты не отравлен, антидот бесполезен."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"You're not poisoned — the antidote is useless."`
- ✏️ НОВЫЙ EN:


### dungeon.block.digest

- ТЕКУЩИЙ RU: `"🤢 Несварение: пищеварение на паузе. Расходники нельзя применять ещё сутки."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🤢 Indigestion: digestion is on pause. You can't use consumables for another day."`
- ✏️ НОВЫЙ EN:


### dungeon.block.drunk

- ТЕКУЩИЙ RU: `"🥴 Ты слишком пьян, чтобы что-то применять. Зелья и расходники станут доступны, когда «очень пьян» пройдёт (6 часов)."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🥴 You're too drunk to use anything. Potions and consumables become available once «very drunk» wears off (6 hours)."`
- ✏️ НОВЫЙ EN:


### dungeon.block.stunned

- ТЕКУЩИЙ RU: `"💫 Ты оглушён: тело не слушается. Расходники будут доступны, когда оглушение пройдёт."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"💫 You're stunned: your body won't obey. Consumables become available when it wears off."`
- ✏️ НОВЫЙ EN:


### dungeon.board.btn

- ТЕКУЩИЙ RU: `"📜 {name} — условия контракта"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"📜 {name} — contract terms"`
- ✏️ НОВЫЙ EN:


### dungeon.board.foot

- ТЕКУЩИЙ RU: `"\n🎫 Контрактов на зачистку: {contracts}\n(покупаются в магазине, доступно Ветеранам).\nВход по контракту списывает его и 30 ⚡ ОД."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"\n🎫 Clearance contracts: {contracts}\n(bought in the shop, available to Veterans).\nEntering on a contract uses one contract and 30 ⚡ AP."`
- ✏️ НОВЫЙ EN:


### dungeon.board.head

- ТЕКУЩИЙ RU: `"📜 ДОСКА КОНТРАКТОВ ОТ ШТАБА ВС\n\nШтаб вывешивает контракты на зачистку подземелий. Выбери контракт, чтобы посмотреть условия.\n\n"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"📜 CONTRACT BOARD FROM THE HQ\n\nHQ posts contracts to clear the dungeons. Pick a contract to see its terms.\n\n"`
- ✏️ НОВЫЙ EN:


### dungeon.board.item

- ТЕКУЩИЙ RU: `"{i}. ⚔️ {name}\n    Этажей: {floors}, комнат/этаж: {rooms}\n"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"{i}. ⚔️ {name}\n    Floors: {floors}, rooms/floor: {rooms}\n"`
- ✏️ НОВЫЙ EN:


### dungeon.boss.empty

- ТЕКУЩИЙ RU: `"… пусто."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"… nothing."`
- ✏️ НОВЫЙ EN:


### dungeon.boss.heal

- ТЕКУЩИЙ RU: `"💊 Лекарства: {uses} применений (×{mult})"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"💊 Medicine: {uses} uses (×{mult})"`
- ✏️ НОВЫЙ EN:


### dungeon.boss.no_escape

- ТЕКУЩИЙ RU: `"⚠️ От босса не убежать! Бой продолжается."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⚠️ You can't run from the boss! The fight goes on."`
- ✏️ НОВЫЙ EN:


### dungeon.boss.not_found

- ТЕКУЩИЙ RU: `"❌ Босс не найден."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ Boss not found."`
- ✏️ НОВЫЙ EN:


### dungeon.boss.screen

- ТЕКУЩИЙ RU: `"💀 {title}\nЭтаж {floor} | БОСС\n❤️ {hp}\n{status}💀 {boss} (HP: {bhp}, АТК: {atk}, УКЛ: {dodge}%)\n\n{desc}\n\n⚠️ Это решающий бой! Убежать нельзя!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"💀 {title}\nFloor {floor} | BOSS\n❤️ {hp}\n{status}💀 {boss} (HP: {bhp}, ATK: {atk}, DODGE: {dodge}%)\n\n{desc}\n\n⚠️ This is the decisive fight! You can't run!"`
- ✏️ НОВЫЙ EN:


### dungeon.boss.title_final

- ТЕКУЩИЙ RU: `"КОМНАТА БОССА"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"BOSS ROOM"`
- ✏️ НОВЫЙ EN:


### dungeon.boss.title_mid

- ТЕКУЩИЙ RU: `"ПРОМЕЖУТОЧНЫЙ БОСС"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"MIDBOSS"`
- ✏️ НОВЫЙ EN:


### dungeon.boss.won

- ТЕКУЩИЙ RU: `"🏆 БОСС ПОБЕЖДЁН!\n💀 {enemy} повержен!\n\n🎉 Поздравляем! Ты прошёл подземелье до конца!\n\n📦 Ты выносишь из подземелья:\n"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🏆 BOSS DEFEATED!\n💀 {enemy} is down!\n\n🎉 Congratulations! You cleared the dungeon to the end!\n\n📦 You take out of the dungeon:\n"`
- ✏️ НОВЫЙ EN:


### dungeon.btn.attack

- ТЕКУЩИЙ RU: `"🗡️ Атаковать"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🗡️ Attack"`
- ✏️ НОВЫЙ EN:


### dungeon.btn.back_list

- ТЕКУЩИЙ RU: `"↩️ К списку контрактов"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"↩️ To the contract list"`
- ✏️ НОВЫЙ EN:


### dungeon.btn.cancel

- ТЕКУЩИЙ RU: `"↩️ Отмена"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"↩️ Cancel"`
- ✏️ НОВЫЙ EN:


### dungeon.btn.city

- ТЕКУЩИЙ RU: `"🏠 В меню города"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🏠 To the city menu"`
- ✏️ НОВЫЙ EN:


### dungeon.btn.continue

- ТЕКУЩИЙ RU: `"🏃 Продолжить путь"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🏃 Keep going"`
- ✏️ НОВЫЙ EN:


### dungeon.btn.contracts

- ТЕКУЩИЙ RU: `"🏰 К списку контрактов"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🏰 To the contract list"`
- ✏️ НОВЫЙ EN:


### dungeon.btn.enter_contract

- ТЕКУЩИЙ RU: `"🎫 Войти (1 контракт)"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🎫 Enter (1 contract)"`
- ✏️ НОВЫЙ EN:


### dungeon.btn.escape

- ТЕКУЩИЙ RU: `"🏃 Попытаться убежать"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🏃 Try to escape"`
- ✏️ НОВЫЙ EN:


### dungeon.btn.yes_enter

- ТЕКУЩИЙ RU: `"✅ Да, войти"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"✅ Yes, enter"`
- ✏️ НОВЫЙ EN:


### dungeon.card.text

- ТЕКУЩИЙ RU: `"📜 КОНТРАКТ ОТ ШТАБА ВС\n\n⚔️ {name}\n{desc}\n\n🏚 Этажей: {floors} (комнат/этаж: {rooms})\n☠ Сложность: {stars}\n💰 Награда за зачистку: до {reward} НМ с врагов\n\n🎫 Стоимость входа:\n   • 1 «Контракт на зачистку» (у тебя: {contracts})\n   • 30 ⚡ ОД (у тебя: {ap})\n\nРесурсы списываются сразу при входе, даже если ты выйдешь из подземелья."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"📜 CONTRACT FROM THE HQ\n\n⚔️ {name}\n{desc}\n\n🏚 Floors: {floors} (rooms/floor: {rooms})\n☠ Difficulty: {stars}\n💰 Clearance reward: up to {reward} NM from enemies\n\n🎫 Entry cost:\n   • 1 «Clearance contract» (you have: {contracts})\n   • 30 ⚡ AP (you have: {ap})\n\nResources are spent at entry, even if you leave the dungeon."`
- ✏️ НОВЫЙ EN:


### dungeon.dot.killed

- ТЕКУЩИЙ RU: `"💀 {name} пал от {label} твоего оружия (−{dmg} HP)!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"💀 {name} fell to {label} from your weapon (−{dmg} HP)!"`
- ✏️ НОВЫЙ EN:


### dungeon.enemy.down

- ТЕКУЩИЙ RU: `"🏆 {name} повержен!\n"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🏆 {name} is down!\n"`
- ✏️ НОВЫЙ EN:


### dungeon.enter.confirm

- ТЕКУЩИЙ RU: `"⚠️ ПО КОНТРАКТУ «{name}» БУДУТ СПИСАНЫ:\n\n🎫 1 «Контракт на зачистку» (у тебя: {contracts})\n⚡ 30 очков действий (у тебя: {ap})\n\nЭти ресурсы потратятся сразу, даже если ты выйдешь из подземелья. Продолжить?"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⚠️ UNDER CONTRACT «{name}» THE FOLLOWING WILL BE SPENT:\n\n🎫 1 «Clearance contract» (you have: {contracts})\n⚡ 30 action points (you have: {ap})\n\nThese resources are spent right away, even if you leave the dungeon. Continue?"`
- ✏️ НОВЫЙ EN:


### dungeon.enter.done

- ТЕКУЩИЙ RU: `"🎫 Контракт использован! ⚡ −30 AP за вход\n🏰 {name}\nЭтаж 1 | Комната 0/{rooms}\n❤️ {bar}\n\nТы входишь в подземелье..."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🎫 Contract used! ⚡ −30 AP for entry\n🏰 {name}\nFloor 1 | Room 0/{rooms}\n❤️ {bar}\n\nYou enter the dungeon..."`
- ✏️ НОВЫЙ EN:


### dungeon.escape.drunk_fall

- ТЕКУЩИЙ RU: `"🥴 Шатаясь, ты совсем теряешь координацию!\n\n"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🥴 Staggering, you lose all coordination!\n\n"`
- ✏️ НОВЫЙ EN:


### dungeon.escape.drunk_luck

- ТЕКУЩИЙ RU: `"🥴 Ты едва держишься на ногах, но удача не покинула тебя!\n\n"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🥴 You barely stay on your feet, but luck hasn't left you!\n\n"`
- ✏️ НОВЫЙ EN:


### dungeon.escape.fail

- ТЕКУЩИЙ RU: `"❌ Не удалось убежать!\n−{penalty} HP (штрафной удар)\n❤️ {bar}\n\nТы продолжаешь бой с {enemy}."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ The escape failed!\n−{penalty} HP (penalty hit)\n❤️ {bar}\n\nYou keep fighting {enemy}."`
- ✏️ НОВЫЙ EN:


### dungeon.escape.run

- ТЕКУЩИЙ RU: `"🏃 Ты успешно убежал от {name}!\n"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🏃 You escaped {name}!\n"`
- ✏️ НОВЫЙ EN:


### dungeon.escape.smoke

- ТЕКУЩИЙ RU: `"💨 Ты взрываешь дымовую шашку — едкий дым застилает комнату!\n🏃 Пока враг мечется в пелене дыма, ты успешно убежал от {name}!\n"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"💨 You set off a smoke bomb — acrid smoke fills the room!\n🏃 While the enemy thrashes in the haze, you escape {name}!\n"`
- ✏️ НОВЫЙ EN:


### dungeon.escape.smoke_wasted

- ТЕКУЩИЙ RU: `"\n💨 Дымовая шашка потрачена впустую."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"\n💨 The smoke bomb was wasted."`
- ✏️ НОВЫЙ EN:


### dungeon.exit.again

- ТЕКУЩИЙ RU: `"{text}\n\nВойти снова?"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"{text}\n\nEnter again?"`
- ✏️ НОВЫЙ EN:


### dungeon.exit.boss

- ТЕКУЩИЙ RU: `"⚠️ Идёт бой с боссом! Убежать нельзя — это решающий бой.\nПродолжай бой кнопками последнего сообщения."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⚠️ The boss fight is on! You can't run — this is the decisive battle.\nKeep fighting with the buttons of the last message."`
- ✏️ НОВЫЙ EN:


### dungeon.exit.confirm

- ТЕКУЩИЙ RU: `"🚪 ПОКИНУТЬ ПОДЗЕМЕЛЬЕ?\n\nТы уверен, что хочешь покинуть подземелье?\n\n📦 Ты выносишь:\n{loot}\n\nВернуться в забег с этого момента будет нельзя."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🚪 LEAVE THE DUNGEON?\n\nAre you sure you want to leave the dungeon?\n\n📦 You take out:\n{loot}\n\nYou won't be able to return to this run from this point."`
- ✏️ НОВЫЙ EN:


### dungeon.exit.continue

- ТЕКУЩИЙ RU: `"Продолжаем подземелье!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Back to the dungeon!"`
- ✏️ НОВЫЙ EN:


### dungeon.exit.empty_leave

- ТЕКУЩИЙ RU: `"Ты покидаешь подземелье ни с чем."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"You leave the dungeon empty-handed."`
- ✏️ НОВЫЙ EN:


### dungeon.exit.leave

- ТЕКУЩИЙ RU: `"📦 Ты выносишь из подземелья:\n{loot}\n\nТы покидаешь подземелье."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"📦 You take out of the dungeon:\n{loot}\n\nYou leave the dungeon."`
- ✏️ НОВЫЙ EN:


### dungeon.exit.nm

- ТЕКУЩИЙ RU: `"💰 {nm} Нордмарок"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"💰 {nm} Nordmarks"`
- ✏️ НОВЫЙ EN:


### dungeon.exit.no

- ТЕКУЩИЙ RU: `"↩️ Нет, остаться"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"↩️ No, stay"`
- ✏️ НОВЫЙ EN:


### dungeon.exit.nothing

- ТЕКУЩИЙ RU: `"Ничего."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Nothing."`
- ✏️ НОВЫЙ EN:


### dungeon.exit.yes

- ТЕКУЩИЙ RU: `"✅ Да, выйти"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"✅ Yes, leave"`
- ✏️ НОВЫЙ EN:


### dungeon.fight.attack_head

- ТЕКУЩИЙ RU: `"{regen}🗡️ Ты атакуешь {enemy}!\n{attack}{bar}\n\n"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"{regen}🗡️ You attack {enemy}!\n{attack}{bar}\n\n"`
- ✏️ НОВЫЙ EN:


### dungeon.fight.death_line

- ТЕКУЩИЙ RU: `"💀 Ты погиб! −{nm} Нордмарок штраф.\nСобранный лут потерян."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"💀 You died! −{nm} Nordmarks penalty.\nThe loot you carried is lost."`
- ✏️ НОВЫЙ EN:


### dungeon.fight.enemy_armor

- ТЕКУЩИЙ RU: `"\n🛡️ Броня врага поглотила {n} урона!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"\n🛡️ The enemy's armor absorbed {n} damage!"`
- ✏️ НОВЫЙ EN:


### dungeon.fight.hit

- ТЕКУЩИЙ RU: `"−{dmg} HP врагу{crit}{armor}\n"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"−{dmg} HP to the enemy{crit}{armor}\n"`
- ✏️ НОВЫЙ EN:


### dungeon.fight.regen

- ТЕКУЩИЙ RU: `"♻ Регенерация: +{healed} HP.\n"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"♻ Regeneration: +{healed} HP.\n"`
- ✏️ НОВЫЙ EN:


### dungeon.fight.regen_active

- ТЕКУЩИЙ RU: `"\n♻ Регенерация активна: следующий тик +{tick} HP (осталось {left} х.)."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"\n♻ Regeneration active: next tick +{tick} HP ({left} turns left)."`
- ✏️ НОВЫЙ EN:


### dungeon.heal.hard

- ТЕКУЩИЙ RU: `"\n⚠️ Лекарства почти не действуют: эффективность −1/2 (применено: {uses})."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"\n⚠️ Medicine barely works: efficiency −1/2 (used: {uses})."`
- ✏️ НОВЫЙ EN:


### dungeon.heal.soft

- ТЕКУЩИЙ RU: `"\n⚠️ Лекарства действуют хуже: эффективность −1/3 (применено: {uses})."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"\n⚠️ Medicine works worse: efficiency −1/3 (used: {uses})."`
- ✏️ НОВЫЙ EN:


### dungeon.msg.ap_fail

- ТЕКУЩИЙ RU: `"❌ Не удалось списать очки действий."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ Couldn't spend action points."`
- ✏️ НОВЫЙ EN:


### dungeon.msg.ap_short

- ТЕКУЩИЙ RU: `"❌ Недостаточно очков действий. Нужно 30 AP, у тебя {ap} AP."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ Not enough action points. You need 30 AP, you have {ap} AP."`
- ✏️ НОВЫЙ EN:


### dungeon.msg.ap_short_enter

- ТЕКУЩИЙ RU: `"❌ Недостаточно очков действий для входа.\nНужно 30 AP за попытку, у тебя {ap} AP.\n\n⚡ Очки действий восстанавливаются раз в сутки."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ Not enough action points to enter.\nYou need 30 AP per attempt, you have {ap} AP.\n\n⚡ Action points come back once a day."`
- ✏️ НОВЫЙ EN:


### dungeon.msg.contract_fail

- ТЕКУЩИЙ RU: `"❌ Не удалось списать контракт."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ Couldn't spend the contract."`
- ✏️ НОВЫЙ EN:


### dungeon.msg.contract_missing

- ТЕКУЩИЙ RU: `"❌ Контракт не найден."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ Contract not found."`
- ✏️ НОВЫЙ EN:


### dungeon.msg.enemy_gone

- ТЕКУЩИЙ RU: `"⚠️ Этого врага уже нет в текущей комнате."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⚠️ That enemy is no longer in this room."`
- ✏️ НОВЫЙ EN:


### dungeon.msg.no_contract

- ТЕКУЩИЙ RU: `"❌ У тебя нет «Контракта на зачистку»."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ You have no «Clearance contract»."`
- ✏️ НОВЫЙ EN:


### dungeon.msg.no_contract_full

- ТЕКУЩИЙ RU: `"❌ У тебя нет «Контракта на зачистку».\n\nКупи его в магазине (Особое) — доступно Ветеранам. Контракт даёт право на один вход."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ You have no «Clearance contract».\n\nBuy one in the shop (Special) — available to Veterans. A contract allows one entry."`
- ✏️ НОВЫЙ EN:


### dungeon.msg.no_contracts

- ТЕКУЩИЙ RU: `"❌ Контрактов пока нет."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ No contracts yet."`
- ✏️ НОВЫЙ EN:


### dungeon.msg.no_enemy

- ТЕКУЩИЙ RU: `"❌ Врага не найдено."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ Enemy not found."`
- ✏️ НОВЫЙ EN:


### dungeon.msg.not_found

- ТЕКУЩИЙ RU: `"❌ Подземелье не найдено."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ Dungeon not found."`
- ✏️ НОВЫЙ EN:


### dungeon.msg.not_found_active

- ТЕКУЩИЙ RU: `"❌ Активное подземелье не найдено."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ No active dungeon found."`
- ✏️ НОВЫЙ EN:


### dungeon.notify.boss_won

- ТЕКУЩИЙ RU: `"🏆 {who} прошёл подземелье и победил босса «{boss}»!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🏆 {who} cleared the dungeon and defeated the boss «{boss}»!"`
- ✏️ НОВЫЙ EN:


### dungeon.resv.locked

- ТЕКУЩИЙ RU: `"⚠️ Водохранилище доступно только после победы над Крысиным капитаном."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⚠️ The reservoir opens only after defeating the Rat Captain."`
- ✏️ НОВЫЙ EN:


### dungeon.room.empty

- ТЕКУЩИЙ RU: `"🏰 {name}\n{header}\n❤️ {hp}\n{status}🪨 Комната пуста. Здесь ничего нет.\n\nНажми «Продолжить путь» чтобы идти дальше."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🏰 {name}\n{header}\n❤️ {hp}\n{status}🪨 The room is empty. There's nothing here.\n\nPress «Keep going» to move on."`
- ✏️ НОВЫЙ EN:


### dungeon.room.enemy

- ТЕКУЩИЙ RU: `"🏰 {name}\n{header}\n❤️ {hp}\n{status}⚠️ Ты входишь в комнату и видишь врага!\n👾 {enemy} (HP: {ehp}, АТК: {atk}, УКЛ: {dodge}%)\n\n{desc}\nЧто делаешь?"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🏰 {name}\n{header}\n❤️ {hp}\n{status}⚠️ You enter the room and see an enemy!\n👾 {enemy} (HP: {ehp}, ATK: {atk}, DODGE: {dodge}%)\n\n{desc}\nWhat do you do?"`
- ✏️ НОВЫЙ EN:


### dungeon.room.header

- ТЕКУЩИЙ RU: `"Этаж {floor} | Комната {room}/{total}"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Floor {floor} | Room {room}/{total}"`
- ✏️ НОВЫЙ EN:


### dungeon.room.heal

- ТЕКУЩИЙ RU: `"💊 Лекарства: {uses} применений (×{mult})\n"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"💊 Medicine: {uses} uses (×{mult})\n"`
- ✏️ НОВЫЙ EN:


### dungeon.room.loot_head

- ТЕКУЩИЙ RU: `"\n🎁 Лут:\n"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"\n🎁 Loot:\n"`
- ✏️ НОВЫЙ EN:


### dungeon.room.next_hint

- ТЕКУЩИЙ RU: `"Нажми «Продолжить путь» чтобы идти дальше."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Press «Keep going» to move on."`
- ✏️ НОВЫЙ EN:


### dungeon.room.resource

- ТЕКУЩИЙ RU: `"🏰 {name}\n{header}\n❤️ {hp}\n{status}📦 Ты нашёл хранилище с припасами!\n+{nm} Нордмарок (заберёшь при выходе)\n\nНажми «Продолжить путь» чтобы идти дальше."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🏰 {name}\n{header}\n❤️ {hp}\n{status}📦 You found a supply cache!\n+{nm} Nordmarks (you'll take them on the way out)\n\nPress «Keep going» to move on."`
- ✏️ НОВЫЙ EN:


### dungeon.slot.antidote

- ТЕКУЩИЙ RU: `"⚗️ Антидот{suffix}"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⚗️ Antidote{suffix}"`
- ✏️ НОВЫЙ EN:


### dungeon.slot.empty

- ТЕКУЩИЙ RU: `"❌ Этот слот пуст."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ This slot is empty."`
- ✏️ НОВЫЙ EN:


### dungeon.slot.frost

- ТЕКУЩИЙ RU: `"🧊 {name}{suffix}"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🧊 {name}{suffix}"`
- ✏️ НОВЫЙ EN:


### dungeon.slot.heal

- ТЕКУЩИЙ RU: `"💊 {name}{suffix}"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"💊 {name}{suffix}"`
- ✏️ НОВЫЙ EN:


### dungeon.slot.other

- ТЕКУЩИЙ RU: `"🧪 {name}{suffix}"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🧪 {name}{suffix}"`
- ✏️ НОВЫЙ EN:


### dungeon.slot.smoke

- ТЕКУЩИЙ RU: `"💨 Дымовая шашка{suffix}"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"💨 Smoke bomb{suffix}"`
- ✏️ НОВЫЙ EN:


### dungeon.smoke.boss

- ТЕКУЩИЙ RU: `"⚠️ От босса не убежать! Дымовая шашка не поможет."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⚠️ You can't run from a boss! A smoke bomb won't help."`
- ✏️ НОВЫЙ EN:


### dungeon.smoke.fail

- ТЕКУЩИЙ RU: `"❌ Не удалось списать шашку."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ Couldn't spend the smoke bomb."`
- ✏️ НОВЫЙ EN:


### dungeon.smoke.limit

- ТЕКУЩИЙ RU: `"❌ За один забег в подземелье можно применить не больше {n} дымовых шашек."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ You can use at most {n} smoke bombs per dungeon run."`
- ✏️ НОВЫЙ EN:


### dungeon.smoke.wrong_slot

- ТЕКУЩИЙ RU: `"❌ Дымовая шашка применяется только из своего слота «Дымовая шашка» (Инвентарь → Снаряжение)."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ A smoke bomb can only be used from its own «Smoke bomb» slot (Inventory → Gear)."`
- ✏️ НОВЫЙ EN:


### dungeon.use.antidote

- ТЕКУЩИЙ RU: `"⚗️ {name} применён: отравление снято!\nПродолжай бой:"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⚗️ {name} used: poison cured!\nKeep fighting:"`
- ✏️ НОВЫЙ EN:


### dungeon.use.bless_nl

- ТЕКУЩИЙ RU: `"\n🌟 Благословение Севера усилило лечение (+{pct}%)."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"\n🌟 Blessing of the North boosted the healing (+{pct}%)."`
- ✏️ НОВЫЙ EN:


### dungeon.use.bless_sp

- ТЕКУЩИЙ RU: `" 🌟 Благословение Севера усилило лечение (+{pct}%)."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `" 🌟 Blessing of the North boosted the healing (+{pct}%)."`
- ✏️ НОВЫЙ EN:


### dungeon.use.continue

- ТЕКУЩИЙ RU: `"\n\nПродолжай бой:"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"\n\nKeep fighting:"`
- ✏️ НОВЫЙ EN:


### dungeon.use.dodge

- ТЕКУЩИЙ RU: `"\n🪁 Уворот +{pct}% на сутки! (повторное применение баф не продлевает)"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"\n🪁 Dodge +{pct}% for a day! (using it again doesn't extend the buff)"`
- ✏️ НОВЫЙ EN:


### dungeon.use.dodge_active

- ТЕКУЩИЙ RU: `"\n🪁 Баф уворота +{pct}% уже активен — не продлевается."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"\n🪁 The +{pct}% dodge buff is already active — it doesn't extend."`
- ✏️ НОВЫЙ EN:


### dungeon.use.eff

- ТЕКУЩИЙ RU: `" (эффективность ×{mult}: {heal} HP вместо {base})"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `" (efficiency ×{mult}: {heal} HP instead of {base})"`
- ✏️ НОВЫЙ EN:


### dungeon.use.fail

- ТЕКУЩИЙ RU: `"❌ Не удалось списать предмет."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ Couldn't spend the item."`
- ✏️ НОВЫЙ EN:


### dungeon.use.frost_cured

- ТЕКУЩИЙ RU: `"\n🧊 Обморожение снято!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"\n🧊 Frostbite cured!"`
- ✏️ НОВЫЙ EN:


### dungeon.use.frost_weak

- ТЕКУЩИЙ RU: `"\n🧊 Обморожение снизило лечение."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"\n🧊 Frostbite reduced the healing."`
- ✏️ НОВЫЙ EN:


### dungeon.use.full_hp

- ТЕКУЩИЙ RU: `"❤️ HP уже полное ({hp}/{hp_max}), зелье не нужно.\nПримени его в бою, когда потеряешь HP."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❤️ HP is already full ({hp}/{hp_max}), no potion needed.\nUse it in a fight when you lose HP."`
- ✏️ НОВЫЙ EN:


### dungeon.use.healed

- ТЕКУЩИЙ RU: `"💊 {name} применено: +{heal} HP{eff}!\n❤️ {bar}{regen}\n{limit}\n\nПродолжай бой:"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"💊 {name} used: +{heal} HP{eff}!\n❤️ {bar}{regen}\n{limit}\n\nKeep fighting:"`
- ✏️ НОВЫЙ EN:


### dungeon.use.mastery_nl

- ТЕКУЩИЙ RU: `"\n✨ Мастерство усилило лечение (+{pct}%)."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"\n✨ Mastery boosted the healing (+{pct}%)."`
- ✏️ НОВЫЙ EN:


### dungeon.use.mastery_sp

- ТЕКУЩИЙ RU: `" ✨ Мастерство усилило лечение (+{pct}%)."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `" ✨ Mastery boosted the healing (+{pct}%)."`
- ✏️ НОВЫЙ EN:


### dungeon.use.not_in_fight

- ТЕКУЩИЙ RU: `"❌ Этот предмет нельзя использовать в бою."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ This item can't be used in a fight."`
- ✏️ НОВЫЙ EN:


### dungeon.use.regen

- ТЕКУЩИЙ RU: `"\n♻ Регенерация: следующие ходы +{ticks} HP (затухает)."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"\n♻ Regeneration: next turns +{ticks} HP (fading)."`
- ✏️ НОВЫЙ EN:


### dungeon.use.seed

- ТЕКУЩИЙ RU: `"\n\n🌱 Из яблока выпало семечко!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"\n\n🌱 A seed fell out of the apple!"`
- ✏️ НОВЫЙ EN:


### dungeon.use.spoiled

- ТЕКУЩИЙ RU: `"\n\n🤢 Ты съел испорченную рыбу — наступило несварение на сутки. Нельзя применять расходники."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"\n\n🤢 You ate spoiled fish — indigestion for a day. You can't use consumables."`
- ✏️ НОВЫЙ EN:


### fine.blocked

- ТЕКУЩИЙ RU: `"⚖️ У тебя есть неоплаченный штраф: покупки, переводы и передача предметов недоступны, пока он не закрыт. Оплатить можно в банке, раздел «Штрафы»."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⚖️ You have an unpaid fine: purchases, transfers and item handovers are unavailable until it is paid. Pay it at the bank, section «Fines»."`
- ✏️ НОВЫЙ EN:


### fine.cancelled

- ТЕКУЩИЙ RU: `"✅ Штраф #{id} отменён администратором."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"✅ Fine #{id} was cancelled by an administrator."`
- ✏️ НОВЫЙ EN:


### fine.charged

- ТЕКУЩИЙ RU: `"⚖️ По штрафу списано {taken} НМ (10% суммы).\nОсталось: {left} НМ.\nПричина: {reason}\nОплатить можно в банке, раздел «Штрафы»."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⚖️ {taken} NM was taken for your fine (10% of the amount).\nLeft: {left} NM.\nReason: {reason}\nYou can pay it at the bank, section «Fines»."`
- ✏️ НОВЫЙ EN:


### fine.closed

- ТЕКУЩИЙ RU: `"⚖️ Штраф закрыт.\nСписано за сутки: {taken} НМ.\nПричина: {reason}"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⚖️ Fine closed.\nTaken today: {taken} NM.\nReason: {reason}"`
- ✏️ НОВЫЙ EN:


### fine.issued

- ТЕКУЩИЙ RU: `"⚖️ Тебе наложен штраф: {amount} НМ.\nПричина: {reason}\nКаждые игровые сутки будет списываться 10% суммы, пока штраф не закрыт. Оплатить можно в банке, раздел «Штрафы»."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⚖️ A fine of {amount} NM was issued to you.\nReason: {reason}\n10% of the amount will be taken each game day until it is paid. You can pay it at the bank, section «Fines»."`
- ✏️ НОВЫЙ EN:


### fines.ask_amount

- ТЕКУЩИЙ RU: `"Сколько НМ внести по штрафу #{id}? Введи целое число:"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"How many NM to pay toward fine #{id}? Enter a whole number:"`
- ✏️ НОВЫЙ EN:


### fines.bad_amount

- ТЕКУЩИЙ RU: `"❌ Введи целое число больше нуля:"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ Enter a whole number greater than zero:"`
- ✏️ НОВЫЙ EN:


### fines.btn_pay_all

- ТЕКУЩИЙ RU: `"💰 Оплатить всё ({left} НМ)"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"💰 Pay all ({left} NM)"`
- ✏️ НОВЫЙ EN:


### fines.btn_pay_part

- ТЕКУЩИЙ RU: `"✏️ Оплатить часть"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"✏️ Pay part"`
- ✏️ НОВЫЙ EN:


### fines.line

- ТЕКУЩИЙ RU: `"#{id} · осталось {left} НМ из {total} НМ\nПричина: {reason}"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"#{id} · {left} NM left of {total} NM\nReason: {reason}"`
- ✏️ НОВЫЙ EN:


### fines.no_money

- ТЕКУЩИЙ RU: `"❌ Недостаточно НМ на счёте для этой суммы."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ Not enough NM in your account for this amount."`
- ✏️ НОВЫЙ EN:


### fines.none

- ТЕКУЩИЙ RU: `"✅ Неоплаченных штрафов нет."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"✅ You have no unpaid fines."`
- ✏️ НОВЫЙ EN:


### fines.not_found

- ТЕКУЩИЙ RU: `"❌ Штраф не найден или уже закрыт."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ Fine not found or already closed."`
- ✏️ НОВЫЙ EN:


### fines.nothing

- ТЕКУЩИЙ RU: `"❌ Нечего списывать."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ Nothing to pay."`
- ✏️ НОВЫЙ EN:


### fines.paid_full

- ТЕКУЩИЙ RU: `"✅ Штраф #{id} оплачен полностью: {taken} НМ."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"✅ Fine #{id} paid in full: {taken} NM."`
- ✏️ НОВЫЙ EN:


### fines.paid_part

- ТЕКУЩИЙ RU: `"✅ По штрафу #{id} внесено {taken} НМ."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"✅ {taken} NM paid toward fine #{id}."`
- ✏️ НОВЫЙ EN:


### fines.title

- ТЕКУЩИЙ RU: `"⚖️ Твои штрафы"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⚖️ Your fines"`
- ✏️ НОВЫЙ EN:


### fire.ach.fisher

- ТЕКУЩИЙ RU: `"\n\n🪣 <b>Мини-ачивка: «Рыбак древних»!</b> Все три праздничные рыбы — твои. Премия — доступна у наград, а в награду — рецепт «Предания предков»."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"\n\n🪣 <b>Mini achievement: «Angler of the Ancients»!</b> All three festival fish are yours. The bonus is available in rewards, and the prize is the «Ancestors' Lore» recipe."`
- ✏️ НОВЫЙ EN:


### fire.alert.casting

- ТЕКУЩИЙ RU: `"Ты уже закинул удочку — дождись результата!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"You've already cast — wait for the result!"`
- ✏️ НОВЫЙ EN:


### fire.alert.died

- ТЕКУЩИЙ RU: `"💀 Ты пал в Огненном Лабиринте!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"💀 You fell in the Fire Maze!"`
- ✏️ НОВЫЙ EN:


### fire.alert.drunk

- ТЕКУЩИЙ RU: `"🍺 В таком состоянии в Лабиринт не пускают. Загляни, когда пройдёт опьянение."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🍺 You're not let into the maze in this state. Come back once you've sobered up."`
- ✏️ НОВЫЙ EN:


### fire.alert.finished

- ТЕКУЩИЙ RU: `"🏁 Лабиринт пройден до конца!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🏁 Maze cleared!"`
- ✏️ НОВЫЙ EN:


### fire.alert.go_tourist

- ТЕКУЩИЙ RU: `"⛔ Вход только для граждан Нордхайма и легионеров."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⛔ Entry only for citizens of Nordheim and legionnaires."`
- ✏️ НОВЫЙ EN:


### fire.alert.inside

- ТЕКУЩИЙ RU: `"🔥 Ты уже внутри лабиринта."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🔥 You're already inside the maze."`
- ✏️ НОВЫЙ EN:


### fire.alert.left

- ТЕКУЩИЙ RU: `"🚪 Ты покинул лабиринт."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🚪 You left the maze."`
- ✏️ НОВЫЙ EN:


### fire.alert.limit

- ТЕКУЩИЙ RU: `"❌ Лимит заходов на сегодня исчерпан: {max} в сутки."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ Today's run limit is used up: {max} a day."`
- ✏️ НОВЫЙ EN:


### fire.alert.need_items

- ТЕКУЩИЙ RU: `"❌ Нужно {qty} × {name}."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ You need {qty} × {name}."`
- ✏️ НОВЫЙ EN:


### fire.alert.no_ap

- ТЕКУЩИЙ RU: `"❌ Не хватает ОД: нужно {cost}."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ Not enough AP: you need {cost}."`
- ✏️ НОВЫЙ EN:


### fire.alert.no_bait

- ТЕКУЩИЙ RU: `"❌ Нет такой наживки."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ No such bait."`
- ✏️ НОВЫЙ EN:


### fire.alert.no_battle

- ТЕКУЩИЙ RU: `"❌ Бой не найден — вернись на развилку."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ Fight not found — return to the fork."`
- ✏️ НОВЫЙ EN:


### fire.alert.no_exchange

- ТЕКУЩИЙ RU: `"❌ Нет такого обмена."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ No such exchange."`
- ✏️ НОВЫЙ EN:


### fire.alert.no_gift

- ТЕКУЩИЙ RU: `"❌ Нет такого дара."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ No such gift."`
- ✏️ НОВЫЙ EN:


### fire.alert.no_money

- ТЕКУЩИЙ RU: `"❌ Вход стоит {fee} НМ — не хватает."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ Entry costs {fee} NM — not enough."`
- ✏️ НОВЫЙ EN:


### fire.alert.no_path

- ТЕКУЩИЙ RU: `"❌ Нет такого пути."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ No such path."`
- ✏️ НОВЫЙ EN:


### fire.alert.no_rod

- ТЕКУЩИЙ RU: `"❌ Нужна удочка: «Удочка из орешника» из магазина (категория «Рыбалка»)."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ You need a rod: «Hazel rod» from the shop (Fishing category)."`
- ✏️ НОВЫЙ EN:


### fire.alert.none_left

- ТЕКУЩИЙ RU: `"❌ Зелий этого вида не осталось."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ No potions of this kind left."`
- ✏️ НОВЫЙ EN:


### fire.alert.not_heal

- ТЕКУЩИЙ RU: `"❌ Это не лечит."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ This doesn't heal."`
- ✏️ НОВЫЙ EN:


### fire.alert.not_taken

- ТЕКУЩИЙ RU: `"❌ Зелья не списалось."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ The potion wasn't used up."`
- ✏️ НОВЫЙ EN:


### fire.alert.not_well

- ТЕКУЩИЙ RU: `"🎣 Колодец остался позади — удочку можно забросить только в нём."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🎣 You've left the well behind — you can only cast a line from it."`
- ✏️ НОВЫЙ EN:


### fire.alert.paid

- ТЕКУЩИЙ RU: `"🔥 Вход оплачен!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🔥 Entry paid!"`
- ✏️ НОВЫЙ EN:


### fire.alert.remove_failed

- ТЕКУЩИЙ RU: `"❌ Не удалось списать предметы."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ Couldn't take the items."`
- ✏️ НОВЫЙ EN:


### fire.alert.shop_closed

- ТЕКУЩИЙ RU: `"🛍 Лавка ещё не открыта."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🛍 The shop isn't open yet."`
- ✏️ НОВЫЙ EN:


### fire.alert.shop_missing

- ТЕКУЩИЙ RU: `"⚠️ Товар лавки не заведён. Сообщи хранителю."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⚠️ The shop item isn't set up. Tell the keeper."`
- ✏️ НОВЫЙ EN:


### fire.alert.shop_pilots

- ТЕКУЩИЙ RU: `"⛔ Лавка — для пилотов."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⛔ The shop is for pilots."`
- ✏️ НОВЫЙ EN:


### fire.alert.slot_empty

- ТЕКУЩИЙ RU: `"❌ Слот пуст."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ The slot is empty."`
- ✏️ НОВЫЙ EN:


### fire.alert.souvenir_tourist

- ТЕКУЩИЙ RU: `"🔑 Сувенир — для гостей праздника."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🔑 The souvenir is for festival guests."`
- ✏️ НОВЫЙ EN:


### fire.alert.start

- ТЕКУЩИЙ RU: `"❌ Сначала /start."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ Press /start first."`
- ✏️ НОВЫЙ EN:


### fire.alert.stunned

- ТЕКУЩИЙ RU: `"💫 Ты оглушён: тело не слушается. Зелья будут доступны, когда оглушение пройдёт."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"💫 You're stunned: your body won't obey. Potions become available when it wears off."`
- ✏️ НОВЫЙ EN:


### fire.alert.tree_behind

- ТЕКУЩИЙ RU: `"🌳 Древо осталось позади — жертвовать можно только в его комнате."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🌳 The tree is behind you — you can only donate in its room."`
- ✏️ НОВЫЙ EN:


### fire.alert.tree_gone

- ТЕКУЩИЙ RU: `"🌳 Древо осталось позади."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🌳 The tree is behind you."`
- ✏️ НОВЫЙ EN:


### fire.alert.tries_out

- ТЕКУЩИЙ RU: `"🎣 Попытки этого визита исчерпаны — иди дальше."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🎣 This visit's tries are used up — move on."`
- ✏️ НОВЫЙ EN:


### fire.alert.won

- ТЕКУЩИЙ RU: `"💀 Враг повержен!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"💀 The enemy is down!"`
- ✏️ НОВЫЙ EN:


### fire.bait.auto

- ТЕКУЩИЙ RU: `"🔄 Авто (что есть)"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🔄 Auto (whatever you have)"`
- ✏️ НОВЫЙ EN:


### fire.bait.choose

- ТЕКУЩИЙ RU: `"🪱 Выбери наживку. Она списывается с каждым забросом.\nБез наживки рыба не клюёт, но со дна иногда поднимаются моток проволоки или пучок сена."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🪱 Pick your bait. It's used up with every cast.\nWithout bait the fish won't bite, but now and then something surfaces from the bottom: a coil of wire or a bundle of hay."`
- ✏️ НОВЫЙ EN:


### fire.bait.chosen

- ТЕКУЩИЙ RU: `"🪱 Наживка выбрана."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🪱 Bait chosen."`
- ✏️ НОВЫЙ EN:


### fire.bait.combined

- ТЕКУЩИЙ RU: `"🧪 Комбинированная наживка"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🧪 Combined bait"`
- ✏️ НОВЫЙ EN:


### fire.bait.none

- ТЕКУЩИЙ RU: `"🚫 Без наживки"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🚫 No bait"`
- ✏️ НОВЫЙ EN:


### fire.bait.spider

- ТЕКУЩИЙ RU: `"🕷 Лапка кристального паука"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🕷 Crystal spider leg"`
- ✏️ НОВЫЙ EN:


### fire.bait.with

- ТЕКУЩИЙ RU: `"с наживкой «{name}»"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"with bait «{name}»"`
- ✏️ НОВЫЙ EN:


### fire.bait.without

- ТЕКУЩИЙ RU: `"без наживки"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"without bait"`
- ✏️ НОВЫЙ EN:


### fire.bait.worms

- ТЕКУЩИЙ RU: `"🪱 Черви"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🪱 Worms"`
- ✏️ НОВЫЙ EN:


### fire.battle.armor

- ТЕКУЩИЙ RU: `" • 🛡 Броня: {armor}"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `" • 🛡 Armor: {armor}"`
- ✏️ НОВЫЙ EN:


### fire.battle.boss

- ТЕКУЩИЙ RU: `" 👑 БОСС"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `" 👑 BOSS"`
- ✏️ НОВЫЙ EN:


### fire.battle.text

- ТЕКУЩИЙ RU: `"⚔️ <b>Бой: {name}</b>{boss}\n💚 Враг: {hp}/{hp_max} HP{armor} • 💨 Укл: {dodge}%\n💙 Ты: {my_hp}/{my_max}\n✨ Твои эффекты:\n{fx}\n{log}"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⚔️ <b>Fight: {name}</b>{boss}\n💚 Enemy: {hp}/{hp_max} HP{armor} • 💨 Dodge: {dodge}%\n💙 You: {my_hp}/{my_max}\n✨ Your effects:\n{fx}\n{log}"`
- ✏️ НОВЫЙ EN:


### fire.bless.boost

- ТЕКУЩИЙ RU: `"🔥 Благословение усилило удар."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🔥 The blessing empowers your strike."`
- ✏️ НОВЫЙ EN:


### fire.bless.regen

- ТЕКУЩИЙ RU: `"🌿 Благословение: +{regen} HP"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🌿 Blessing: +{regen} HP"`
- ✏️ НОВЫЙ EN:


### fire.btn.back

- ТЕКУЩИЙ RU: `"🔙 Назад"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🔙 Back"`
- ✏️ НОВЫЙ EN:


### fire.btn.back_entry

- ТЕКУЩИЙ RU: `"🔙 Назад ко входу"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🔙 Back to entrance"`
- ✏️ НОВЫЙ EN:


### fire.btn.bait

- ТЕКУЩИЙ RU: `"🪱 Наживка: {label}"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🪱 Bait: {label}"`
- ✏️ НОВЫЙ EN:


### fire.btn.city

- ТЕКУЩИЙ RU: `"🏠 В город"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🏠 To the city"`
- ✏️ НОВЫЙ EN:


### fire.btn.donate

- ТЕКУЩИЙ RU: `"🎁 Пожертвовать Древу"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🎁 Donate to the tree"`
- ✏️ НОВЫЙ EN:


### fire.btn.enter

- ТЕКУЩИЙ RU: `"🔑 Войти — {fee} НМ"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🔑 Enter — {fee} NM"`
- ✏️ НОВЫЙ EN:


### fire.btn.fish

- ТЕКУЩИЙ RU: `"🎣 Ловить ({left})"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🎣 Fish ({left})"`
- ✏️ НОВЫЙ EN:


### fire.btn.give

- ТЕКУЩИЙ RU: `"🎁 Сдать «{name}»"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🎁 Give «{name}»"`
- ✏️ НОВЫЙ EN:


### fire.btn.leave

- ТЕКУЩИЙ RU: `"🚪 Покинуть лабиринт"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🚪 Leave the maze"`
- ✏️ НОВЫЙ EN:


### fire.btn.next

- ТЕКУЩИЙ RU: `"🚶 Идти дальше"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🚶 Move on"`
- ✏️ НОВЫЙ EN:


### fire.btn.no

- ТЕКУЩИЙ RU: `"❌ Нет"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ No"`
- ✏️ НОВЫЙ EN:


### fire.btn.potion

- ТЕКУЩИЙ RU: `"🧪 {name} (x{qty})"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🧪 {name} (x{qty})"`
- ✏️ НОВЫЙ EN:


### fire.btn.shop

- ТЕКУЩИЙ RU: `"🛍 Лавка Круговорота"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🛍 Cycle shop"`
- ✏️ НОВЫЙ EN:


### fire.btn.souvenir

- ТЕКУЩИЙ RU: `"🎁 Получить сувенир"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🎁 Get a souvenir"`
- ✏️ НОВЫЙ EN:


### fire.btn.strike

- ТЕКУЩИЙ RU: `"⚔️ Ударить"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⚔️ Strike"`
- ✏️ НОВЫЙ EN:


### fire.btn.well_back

- ТЕКУЩИЙ RU: `"🔙 Назад к колодцу"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🔙 Back to the well"`
- ✏️ НОВЫЙ EN:


### fire.btn.yes

- ТЕКУЩИЙ RU: `"✅ Да, применить"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"✅ Yes, use it"`
- ✏️ НОВЫЙ EN:


### fire.cast.text

- ТЕКУЩИЙ RU: `"🎣 Ты забросил удочку {bait}...\nРезультат через {delay} секунд. Наберись терпения!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🎣 You cast your line {bait}...\nResult in {delay} seconds. Be patient!"`
- ✏️ НОВЫЙ EN:


### fire.catch.hit

- ТЕКУЩИЙ RU: `"🎣 Поплавок подпрыгивает — <b>{fish}</b>!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🎣 The float bobs — <b>{fish}</b>!"`
- ✏️ НОВЫЙ EN:


### fire.catch.left

- ТЕКУЩИЙ RU: `"\nОсталось попыток: {left}."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"\nTries left: {left}."`
- ✏️ НОВЫЙ EN:


### fire.catch.lost

- ТЕКУЩИЙ RU: `"🐟 Что-то поймал, но предмет потерялся. Сообщи хранителю."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🐟 You caught something, but the item got lost. Tell the keeper."`
- ✏️ НОВЫЙ EN:


### fire.catch.miss

- ТЕКУЩИЙ RU: `"🎣 Поплавок дёрнулся, ты подсекаешь... и вдруг пусто. Сорвалось.\nОсталось попыток: {left}."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🎣 The float jerks, you set the hook... and nothing. It got away.\nTries left: {left}."`
- ✏️ НОВЫЙ EN:


### fire.catch.new

- ТЕКУЩИЙ RU: `" (новый вид!)"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `" (new species!)"`
- ✏️ НОВЫЙ EN:


### fire.closed.not_time

- ТЕКУЩИЙ RU: `"🕯 Не время для Круговорота: праздник ещё не начался или уже отгремел."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🕯 Not the time for the Cycle: the festival hasn't started yet or is already over."`
- ✏️ НОВЫЙ EN:


### fire.closed.soon

- ТЕКУЩИЙ RU: `"🔥 Дни Пламенного Круговорота ещё готовятся — скоро откроем."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🔥 The Flaming Cycle days are still being prepared — opening soon."`
- ✏️ НОВЫЙ EN:


### fire.died.text

- ТЕКУЩИЙ RU: `"💀 <b>Ты пал в Огненном Лабиринте.</b>\nПламя погасило твою искру — но Круговорот живуч, и попытка ценна. Заходы за сутки можно продолжать за НМ."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"💀 <b>You fell in the Fire Maze.</b>\nThe flame snuffed out your spark — but the Cycle endures, and the attempt was worth it. You can keep running the maze for NM today."`
- ✏️ НОВЫЙ EN:


### fire.donate.granted

- ТЕКУЩИЙ RU: `"✨ Древо откликнулось: ты получил талисман памяти!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"✨ The tree answered: you received a memory talisman!"`
- ✏️ НОВЫЙ EN:


### fire.donate.head

- ТЕКУЩИЙ RU: `"🌳 <b>Пожертвования Древу Огня</b>"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🌳 <b>Donations to the Tree of Fire</b>"`
- ✏️ НОВЫЙ EN:


### fire.donate.intro

- ТЕКУЩИЙ RU: `"Древо принимает дары один раз — за все три вида получишь талисман памяти."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"The tree accepts each gift once — bring all three kinds for a memory talisman."`
- ✏️ НОВЫЙ EN:


### fire.donate.talisman

- ТЕКУЩИЙ RU: `"\n✅ Талисман памяти получен. Больше пожертвовать нельзя."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"\n✅ Memory talisman received. No more donations possible."`
- ✏️ НОВЫЙ EN:


### fire.dot.bleed

- ТЕКУЩИЙ RU: `"🩸 Кровотечение"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🩸 Bleeding"`
- ✏️ НОВЫЙ EN:


### fire.dot.burn

- ТЕКУЩИЙ RU: `"🔥 Поджиг"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🔥 Burning"`
- ✏️ НОВЫЙ EN:


### fire.dot.frost

- ТЕКУЩИЙ RU: `"🧊 Обморожение"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🧊 Frostbite"`
- ✏️ НОВЫЙ EN:


### fire.dot.generic

- ТЕКУЩИЙ RU: `"DoT"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"DoT"`
- ✏️ НОВЫЙ EN:


### fire.dot.poison

- ТЕКУЩИЙ RU: `"☠️ Отравление"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"☠️ Poison"`
- ✏️ НОВЫЙ EN:


### fire.dot.tick

- ТЕКУЩИЙ RU: `"{name} добирает врага: −{dmg} HP ({hp}/{hp_max})"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"{name} hits the enemy: −{dmg} HP ({hp}/{hp_max})"`
- ✏️ НОВЫЙ EN:


### fire.enemy.down

- ТЕКУЩИЙ RU: `"💀 <b>{name} повержен!</b>{loot}\n\n"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"💀 <b>{name} is down!</b>{loot}\n\n"`
- ✏️ НОВЫЙ EN:


### fire.entry.head

- ТЕКУЩИЙ RU: `"🪔 <b>Дни Пламенного Круговорота</b>\n\nПеред тобой вход в Лабиринт из снопов сена — жаркое пламя, смех горожан и запах тыквы.\n\n"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🪔 <b>Days of the Flaming Cycle</b>\n\nIn front of you is the entrance to a maze of hay bales — hot flames, townsfolk laughing and the smell of pumpkin.\n\n"`
- ✏️ НОВЫЙ EN:


### fire.entry.info

- ТЕКУЩИЙ RU: `"🔑 Вход: <b>{fee} НМ</b>, до {max} заходов в сутки (сегодня: {used}/{max}).\nЛабиринт полон загадок."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🔑 Entry: <b>{fee} NM</b>, up to {max} runs a day (today: {used}/{max}).\nThe maze is full of riddles."`
- ✏️ НОВЫЙ EN:


### fire.entry.paid

- ТЕКУЩИЙ RU: `"🔥 <b>Дни Пламенного Круговорота</b>\nВход оплачен: −{fee} НМ в казну (заход {n}/{max} за сутки).\n\n"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🔥 <b>Days of the Flaming Cycle</b>\nEntry paid: −{fee} NM to the treasury (run {n}/{max} today).\n\n"`
- ✏️ НОВЫЙ EN:


### fire.entry.tourist

- ТЕКУЩИЙ RU: `"⛔ В лабиринт вход только для граждан Нордхайма и легионеров. Туристам — только поглядеть со стороны и получить сувенир."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⛔ The maze is open only to citizens of Nordheim and legionnaires. Tourists may only look on and take a souvenir."`
- ✏️ НОВЫЙ EN:


### fire.finish.text

- ТЕКУЩИЙ RU: `"🏁 <b>Ты прошёл все {rooms} комнат Огненного Лабиринта!</b>\nПламя памяти остаётся тёплым. Сессия завершена.\nСледующий заход — снова за плату (лимит суток тот же).{tier_note}"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🏁 <b>You cleared all {rooms} rooms of the Fire Maze!</b>\nThe flame of memory stays warm. Session over.\nThe next run costs a fee again (same daily limit).{tier_note}"`
- ✏️ НОВЫЙ EN:


### fire.fork.bless

- ТЕКУЩИЙ RU: `" • 🌳 Благословение активно"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `" • 🌳 Blessing active"`
- ✏️ НОВЫЙ EN:


### fire.fork.text

- ТЕКУЩИЙ RU: `"🪔 <b>Огненный Лабиринт</b>\nТы на развилке №{steps}. Стены полыхают тёплым светом, коридоры уходят вглубь.\n💙 {hp}/{hp_max}{bless}\n\nВыбери путь:"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🪔 <b>Fire Maze</b>\nYou're at fork #{steps}. The walls blaze with warm light, corridors lead deeper.\n💙 {hp}/{hp_max}{bless}\n\nChoose a path:"`
- ✏️ НОВЫЙ EN:


### fire.fx.blind

- ТЕКУЩИЙ RU: `"😵 Ослепление: {n}"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"😵 Blind: {n}"`
- ✏️ НОВЫЙ EN:


### fire.fx.burn

- ТЕКУЩИЙ RU: `"🔥 Поджиг: −{dmg} HP/ход, {rounds} х."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🔥 Burn: −{dmg} HP/turn, {rounds} turns"`
- ✏️ НОВЫЙ EN:


### fire.fx.burn_tick

- ТЕКУЩИЙ RU: `"🔥 Поджиг: −{dmg} HP ({rounds} х. осталось)"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🔥 Burn: −{dmg} HP ({rounds} turns left)"`
- ✏️ НОВЫЙ EN:


### fire.fx.none

- ТЕКУЩИЙ RU: `"   — нет"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"   — none"`
- ✏️ НОВЫЙ EN:


### fire.fx.regen

- ТЕКУЩИЙ RU: `"♻ Регенерация: +{ticks} HP (тики)"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"♻ Regeneration: +{ticks} HP (ticks)"`
- ✏️ НОВЫЙ EN:


### fire.fx.slow

- ТЕКУЩИЙ RU: `"🕸 Замедление: {n} х. (-укл, +укл Хуба)"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🕸 Slow: {n} turns (-dodge, +Hub dodge)"`
- ✏️ НОВЫЙ EN:


### fire.fx.stun

- ТЕКУЩИЙ RU: `"💫 Оглушение: {n}"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"💫 Stun: {n}"`
- ✏️ НОВЫЙ EN:


### fire.fx_end.apple

- ТЕКУЩИЙ RU: `"\n🍎 Спелое яблоко — ты оглушён!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"\n🍎 A ripe apple — you're stunned!"`
- ✏️ НОВЫЙ EN:


### fire.fx_end.boss

- ТЕКУЩИЙ RU: `"\n🔥 Мистер Тыква поджигает: −2 HP/ход на 3 хода!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"\n🔥 Mr. Pumpkin sets you alight: −2 HP/turn for 3 turns!"`
- ✏️ НОВЫЙ EN:


### fire.fx_end.crow

- ТЕКУЩИЙ RU: `"\n🐦 Ворон ослепил тебя!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"\n🐦 The crow blinded you!"`
- ✏️ НОВЫЙ EN:


### fire.fx_end.hub

- ТЕКУЩИЙ RU: `"\n🕸 Хуб опутывает паутиной: замедление (-укл, +укл Хуба)!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"\n🕸 The Hub wraps you in webs: slowed (-dodge, +Hub dodge)!"`
- ✏️ НОВЫЙ EN:


### fire.fx_end.scarecrow

- ТЕКУЩИЙ RU: `"\n🌾 Сено в лицо — ты ослеплён!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"\n🌾 Hay in your face — you're blinded!"`
- ✏️ НОВЫЙ EN:


### fire.hit.blind_miss

- ТЕКУЩИЙ RU: `"😵 Ослепление: удар ушёл в пустоту!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"😵 Blind: your strike hits thin air!"`
- ✏️ НОВЫЙ EN:


### fire.hit.crit

- ТЕКУЩИЙ RU: `"💥 Крит!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"💥 Crit!"`
- ✏️ НОВЫЙ EN:


### fire.hit.dealt

- ТЕКУЩИЙ RU: `"💥 Ты нанёс {eff} урона (враг {hp}/{hp_max})"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"💥 You dealt {eff} damage (enemy {hp}/{hp_max})"`
- ✏️ НОВЫЙ EN:


### fire.hit.enemy_armor

- ТЕКУЩИЙ RU: `"🛡 Броня врага поглотила удар!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🛡 The enemy's armor absorbed the strike!"`
- ✏️ НОВЫЙ EN:


### fire.hit.enemy_dodged

- ТЕКУЩИЙ RU: `"💨 Враг уклонился!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"💨 The enemy dodged!"`
- ✏️ НОВЫЙ EN:


### fire.hit.regen

- ТЕКУЩИЙ RU: `"♻ Регенерация: +{healed} HP"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"♻ Regeneration: +{healed} HP"`
- ✏️ НОВЫЙ EN:


### fire.hit.stun_skip

- ТЕКУЩИЙ RU: `"💫 Оглушение: ты пропускаешь ход!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"💫 Stunned: you skip your turn!"`
- ✏️ НОВЫЙ EN:


### fire.left.text

- ТЕКУЩИЙ RU: `"🚪 Ты покинул Огненный Лабиринт. Пламя остаётся тёплым.\nДо встречи в следующий заход!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🚪 You left the Fire Maze. The flame stays warm.\nSee you on the next run!"`
- ✏️ НОВЫЙ EN:


### fire.loot.head

- ТЕКУЩИЙ RU: `"\n\n🎉 <b>Добыча:</b>\n"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"\n\n🎉 <b>Loot:</b>\n"`
- ✏️ НОВЫЙ EN:


### fire.nobait.empty

- ТЕКУЩИЙ RU: `"🎣 Без наживки рыба не клюёт — со дна пусто.\nОсталось попыток: {left}."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🎣 Without bait the fish won't bite — nothing from the bottom.\nTries left: {left}."`
- ✏️ НОВЫЙ EN:


### fire.nobait.got

- ТЕКУЩИЙ RU: `"🪝 Без наживки рыба не клюёт, но со дна поднялось: <b>{name}</b>!\nОсталось попыток: {left}."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🪝 Without bait the fish won't bite, but something came up from the bottom: <b>{name}</b>!\nTries left: {left}."`
- ✏️ НОВЫЙ EN:


### fire.nobait.lost_item

- ТЕКУЩИЙ RU: `"🪝 Что-то зацепилось, но предмет не заведён. Сообщи хранителю."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🪝 Something snagged, but the item isn't set up. Tell the keeper."`
- ✏️ НОВЫЙ EN:


### fire.path.L

- ТЕКУЩИЙ RU: `"⬅️ Налево"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⬅️ Left"`
- ✏️ НОВЫЙ EN:


### fire.path.R

- ТЕКУЩИЙ RU: `"➡️ Направо"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"➡️ Right"`
- ✏️ НОВЫЙ EN:


### fire.path.S

- ТЕКУЩИЙ RU: `"⬆️ Прямо"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⬆️ Straight"`
- ✏️ НОВЫЙ EN:


### fire.path.go

- ТЕКУЩИЙ RU: `"🔀 {label}. Двигаемся дальше…"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🔀 {label}. Moving on…"`
- ✏️ НОВЫЙ EN:


### fire.potion.bonus

- ТЕКУЩИЙ RU: `" (+{pct}% от экипа и мастерства)"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `" (+{pct}% from gear and skill)"`
- ✏️ НОВЫЙ EN:


### fire.potion.cancelled

- ТЕКУЩИЙ RU: `"Отменено."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Cancelled."`
- ✏️ НОВЫЙ EN:


### fire.potion.confirm

- ТЕКУЩИЙ RU: `"🧪 HP уже полное ({hp}/{hp_max}). Точно применить «{name}»? Расходник будет потрачен."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🧪 HP is already full ({hp}/{hp_max}). Use «{name}» anyway? It will be used up."`
- ✏️ НОВЫЙ EN:


### fire.potion.dodge

- ТЕКУЩИЙ RU: `"\n🪁 Уворот +{pct}% на сутки!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"\n🪁 Dodge +{pct}% for a day!"`
- ✏️ НОВЫЙ EN:


### fire.potion.dodge_active

- ТЕКУЩИЙ RU: `"\n🪁 Баф уворота +{pct}% уже активен — не продлевается."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"\n🪁 The +{pct}% dodge buff is already active — it doesn't extend."`
- ✏️ НОВЫЙ EN:


### fire.potion.log

- ТЕКУЩИЙ RU: `"🧪 «{name}» (+{heal} HP)\n💙 Ты восстановил: ×{hp}/{hp_max}{bonus}"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🧪 «{name}» (+{heal} HP)\n💙 You restored: ×{hp}/{hp_max}{bonus}"`
- ✏️ НОВЫЙ EN:


### fire.potion.regen

- ТЕКУЩИЙ RU: `"\n♻ Регенерация: +{ticks} HP на {turns} ходов"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"\n♻ Regeneration: +{ticks} HP over {turns} turns"`
- ✏️ НОВЫЙ EN:


### fire.set.regen

- ТЕКУЩИЙ RU: `"🧥 Праздничный сет: +{regen} HP"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🧥 Festival set: +{regen} HP"`
- ✏️ НОВЫЙ EN:


### fire.shop.done

- ТЕКУЩИЙ RU: `"🛍 Обмен готов!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🛍 Exchange done!"`
- ✏️ НОВЫЙ EN:


### fire.shop.got

- ТЕКУЩИЙ RU: `"✅ Получено: {qty} × {name}."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"✅ Received: {qty} × {name}."`
- ✏️ НОВЫЙ EN:


### fire.shop.head

- ТЕКУЩИЙ RU: `"🛍 <b>Лавка Круговорота</b>"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🛍 <b>Cycle shop</b>"`
- ✏️ НОВЫЙ EN:


### fire.shop.intro

- ТЕКУЩИЙ RU: `"Праздничный сбор на сладости."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"A festival collection for sweets."`
- ✏️ НОВЫЙ EN:


### fire.shop.row

- ТЕКУЩИЙ RU: `"• {cost} → {qty} × {get} (у тебя: {have})"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"• {cost} → {qty} × {get} (you have: {have})"`
- ✏️ НОВЫЙ EN:


### fire.souvenir.ack_again

- ТЕКУЩИЙ RU: `"🪔 Праздник для гостей."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🪔 Festival for guests."`
- ✏️ НОВЫЙ EN:


### fire.souvenir.ack_fresh

- ТЕКУЩИЙ RU: `"🎁 Сувенир праздника!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🎁 Festival souvenir!"`
- ✏️ НОВЫЙ EN:


### fire.souvenir.again

- ТЕКУЩИЙ RU: `"\n\n🎁 Сувенир праздника ты уже получал — он у тебя (или был)."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"\n\n🎁 You've already received the festival souvenir."`
- ✏️ НОВЫЙ EN:


### fire.souvenir.fresh

- ТЕКУЩИЙ RU: `"\n\n🎁 <b>Сувенир праздника:</b> «Леденец языков пламени» — держи на память о Круговороте!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"\n\n🎁 <b>Festival souvenir:</b> «Flame-tongue lollipop» — keep it as a memento of the Cycle!"`
- ✏️ НОВЫЙ EN:


### fire.talisman.regen

- ТЕКУЩИЙ RU: `"🧿 Талисман памяти: +{treg} HP"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🧿 Memory talisman: +{treg} HP"`
- ✏️ НОВЫЙ EN:


### fire.tier.up

- ТЕКУЩИЙ RU: `"\n\n🔥 <b>Огненное эхо усилилось:</b> Тир {tier} — лабиринт стал сложнее, но награда стала вероятнее! (действует весь праздник)"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"\n\n🔥 <b>The fire echo grew stronger:</b> tier {tier} — the maze is harder, but rewards are more likely! (lasts the whole festival)"`
- ✏️ НОВЫЙ EN:


### fire.tree.body

- ТЕКУЩИЙ RU: `"Тёплый свет сквозь листву: Древо Огня вспыхивает янтарными жилами и кланяется тебе кроной. Долгое пламя из его коры встаёт тебе в плечи.\n\n🔥 Благословение Круговорота (до конца сессии):\n   • урон +{pct}%\n   • +{regen} HP после каждого твоего удара\n💙 Сейчас: {hp}/{hp_max} HP."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Warm light through the leaves: the Tree of Fire flares with amber veins and bows to you with its crown. A long flame from its bark settles on your shoulders.\n\n🔥 Blessing of the Cycle (until the end of the session):\n   • damage +{pct}%\n   • +{regen} HP after each of your strikes\n💙 Now: {hp}/{hp_max} HP."`
- ✏️ НОВЫЙ EN:


### fire.tree.title

- ТЕКУЩИЙ RU: `"🌳 ДРЕВО ОГНЯ"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🌳 TREE OF FIRE"`
- ✏️ НОВЫЙ EN:


### fire.turn.absorbed

- ТЕКУЩИЙ RU: `"⚔️ Враг бьёт на {enemy} — 🛡 броня поглотила удар полностью!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⚔️ The enemy strikes for {enemy} — 🛡 armor absorbed the whole blow!"`
- ✏️ НОВЫЙ EN:


### fire.turn.blocked

- ТЕКУЩИЙ RU: `"⚔️ Враг бьёт на {enemy} — 🛡 броня поглотила {blocked}, −{dmg} HP"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⚔️ The enemy strikes for {enemy} — 🛡 armor absorbed {blocked}, −{dmg} HP"`
- ✏️ НОВЫЙ EN:


### fire.turn.dodged

- ТЕКУЩИЙ RU: `"💨 Ты увернулся от удара врага!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"💨 You dodged the enemy's strike!"`
- ✏️ НОВЫЙ EN:


### fire.turn.hit

- ТЕКУЩИЙ RU: `"⚔️ Враг бьёт на {dmg} урона"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⚔️ The enemy strikes for {dmg} damage"`
- ✏️ НОВЫЙ EN:


### fire.turn.pierce

- ТЕКУЩИЙ RU: `"🗡 Враг пробивает броню! Удар на {dmg} урона"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🗡 The enemy pierces your armor! Strike for {dmg} damage"`
- ✏️ НОВЫЙ EN:


### fire.wdot.bleed

- ТЕКУЩИЙ RU: `"🩸 Кровотечение:"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🩸 Bleeding:"`
- ✏️ НОВЫЙ EN:


### fire.wdot.burn

- ТЕКУЩИЙ RU: `"🔥 Поджог:"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🔥 Burning:"`
- ✏️ НОВЫЙ EN:


### fire.wdot.frost

- ТЕКУЩИЙ RU: `"🧊 Обморожение:"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🧊 Frostbite:"`
- ✏️ НОВЫЙ EN:


### fire.wdot.line

- ТЕКУЩИЙ RU: `"{word} враг получит −{dmg} HP до удара (3 хода)"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"{word} the enemy takes −{dmg} HP before the strike (3 turns)"`
- ✏️ НОВЫЙ EN:


### fire.wdot.poison

- ТЕКУЩИЙ RU: `"☠️ Отравление:"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"☠️ Poison:"`
- ✏️ НОВЫЙ EN:


### fire.well.body

- ТЕКУЩИЙ RU: `"Звонкий всплеск из глубины: колодец Огненного Круговорота дышит паром, вода тёплая, как из ключа. Ты моешь руки, пьёшь — и тело наполняется силой: +{heal} HP и +{ap} ОД.\n\n💙 Сейчас: {hp}/{hp_max} HP.\n🎣 В тёмной воде ходят праздничные рыбы — можно закинуть удочку ({tries} попыток)."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"A ringing splash from the depths: the well of the Flaming Cycle breathes steam, its water warm as a spring. You wash your hands, drink — and your body fills with strength: +{heal} HP and +{ap} AP.\n\n💙 Now: {hp}/{hp_max} HP.\n🎣 Festival fish swim in the dark water — you can cast a line ({tries} tries)."`
- ✏️ НОВЫЙ EN:


### fire.well.status

- ТЕКУЩИЙ RU: `"💙 Сейчас: {hp}/{hp_max} HP.\n🎣 Попыток осталось: {left}."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"💙 Now: {hp}/{hp_max} HP.\n🎣 Tries left: {left}."`
- ✏️ НОВЫЙ EN:


### fire.well.title

- ТЕКУЩИЙ RU: `"🪣 КОЛОДЕЦ ОГНЕННОГО КРУГОВОРОТА"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🪣 WELL OF THE FLAMING CYCLE"`
- ✏️ НОВЫЙ EN:


### fire.well.visit

- ТЕКУЩИЙ RU: `" (визит {n}/{max})"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `" (visit {n}/{max})"`
- ✏️ НОВЫЙ EN:


### forest.alert.busy_any

- ТЕКУЩИЙ RU: `"Ты уже что-то ищешь — дождись результата!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"You're already searching — wait for the result!"`
- ✏️ НОВЫЙ EN:


### forest.alert.busy_mush

- ТЕКУЩИЙ RU: `"Ты уже ищешь грибы — дождись результата!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"You're already searching — wait for the result!"`
- ✏️ НОВЫЙ EN:


### forest.alert.closed

- ТЕКУЩИЙ RU: `"Сюда пока не пускают."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Entry is closed for now."`
- ✏️ НОВЫЙ EN:


### forest.alert.dungeon

- ТЕКУЩИЙ RU: `"⛔ Ты в подземелье — по лесу гулять нельзя!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⛔ You're in a dungeon — no wandering the forest!"`
- ✏️ НОВЫЙ EN:


### forest.alert.no_start

- ТЕКУЩИЙ RU: `"Сначала нажми /start"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Press /start first"`
- ✏️ НОВЫЙ EN:


### forest.alert.tourist

- ТЕКУЩИЙ RU: `"🌲 Сюда туристов не пускают."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🌲 Tourists aren't allowed here."`
- ✏️ НОВЫЙ EN:


### forest.ap_line

- ТЕКУЩИЙ RU: `"⚡ ОД: {ap}/{ap_max}"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⚡ AP: {ap}/{ap_max}"`
- ✏️ НОВЫЙ EN:


### forest.ap_next_ok

- ТЕКУЩИЙ RU: `" — можно искать ещё"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `" — you can search again"`
- ✏️ НОВЫЙ EN:


### forest.ap_next_short

- ТЕКУЩИЙ RU: `" — на следующий поиск не хватит ({cost} ОД)"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `" — not enough for the next search ({cost} AP)"`
- ✏️ НОВЫЙ EN:


### forest.ap_short

- ТЕКУЩИЙ RU: `" — не хватит на поиск ({cost} ОД), придёт с новыми сутками"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `" — not enough for a search ({cost} AP), it comes back with the new day"`
- ✏️ НОВЫЙ EN:


### forest.battle.after

- ТЕКУЩИЙ RU: `"Очнулся ты {where} весь в ссадинах — зверь ушёл в чащу. Победа досталась ему ценой твоих сил: −{removed} ОД."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"You come to {where}, bruised all over — the beast slipped back into the thicket. It won at the cost of your strength: −{removed} AP."`
- ✏️ НОВЫЙ EN:


### forest.battle.beast_hp

- ТЕКУЩИЙ RU: `"Зверь   HP"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Beast  HP"`
- ✏️ НОВЫЙ EN:


### forest.battle.bled

- ТЕКУЩИЙ RU: `"Ты истёк кровью и теряешь сознание.\n\nЗверь уходит, оставив тебя в чаще (−{removed} ОД)."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"You bleed out and pass out.\n\nThe beast leaves you in the thicket (−{removed} AP)."`
- ✏️ НОВЫЙ EN:


### forest.battle.faint

- ТЕКУЩИЙ RU: `"Ты теряешь сознание.\n\n"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"You pass out.\n\n"`
- ✏️ НОВЫЙ EN:


### forest.battle.fled

- ТЕКУЩИЙ RU: `"🏃 Ты вырвался из чащи — зверь остался позади.\n\n"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🏃 You break out of the thicket — the beast is left behind.\n\n"`
- ✏️ НОВЫЙ EN:


### forest.battle.intro

- ТЕКУЩИЙ RU: `"Кусты позади взрываются хрустом — на тебя несётся взбешённый зверь!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Bushes crack open behind you — a furious beast charges at you!"`
- ✏️ НОВЫЙ EN:


### forest.battle.lost

- ТЕКУЩИЙ RU: `"❌ Бой потерян.\n\n"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ The fight is lost.\n\n"`
- ✏️ НОВЫЙ EN:


### forest.battle.round

- ТЕКУЩИЙ RU: `"Ход {round}. Ударь зверя — или уноси ноги."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Turn {round}. Strike the beast — or run."`
- ✏️ НОВЫЙ EN:


### forest.battle.stale

- ТЕКУЩИЙ RU: `"⏳ Бой со зверем устарел.\n\n"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⏳ The beast fight is out of date.\n\n"`
- ✏️ НОВЫЙ EN:


### forest.battle.title

- ТЕКУЩИЙ RU: `"{emoji} БОЙ С ЗВЕРЕМ"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"{emoji} BEAST FIGHT"`
- ✏️ НОВЫЙ EN:


### forest.battle.won

- ТЕКУЩИЙ RU: `"Зверь споткнулся и рухнул — тишина снова принадлежит лесу.\n\n"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"The beast stumbles and drops — the silence belongs to the forest again.\n\n"`
- ✏️ НОВЫЙ EN:


### forest.battle.you_hp

- ТЕКУЩИЙ RU: `"Ты     HP"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"You    HP"`
- ✏️ НОВЫЙ EN:


### forest.berry.empty

- ТЕКУЩИЙ RU: `"{head}\n\nКусты пусты — ягод в этот раз не нашлось."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"{head}\n\nThe bushes are bare — no berries this time."`
- ✏️ НОВЫЙ EN:


### forest.berry.got

- ТЕКУЩИЙ RU: `"{head}\n\n🫐 Ты собрал: «{name}» — горсть положена в инвентарь."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"{head}\n\n🫐 You gathered: «{name}» — a handful is in your inventory."`
- ✏️ НОВЫЙ EN:


### forest.berry.lost

- ТЕКУЩИЙ RU: `"{head}\n\n🫐 Что-то нашёл, но предмет потерялся. Сообщи хранителю."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"{head}\n\n🫐 You found something, but the item got lost. Tell the keeper."`
- ✏️ НОВЫЙ EN:


### forest.berry.wait

- ТЕКУЩИЙ RU: `"{head}\n\n🫐 Ты пробираешься в кусты за ягодами...\nРезультат через {delay} секунд."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"{head}\n\n🫐 You push into the bushes for berries...\nResult in {delay} seconds."`
- ✏️ НОВЫЙ EN:


### forest.btn.again

- ТЕКУЩИЙ RU: `"{emoji} Поискать ещё"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"{emoji} Search again"`
- ✏️ НОВЫЙ EN:


### forest.btn.berry

- ТЕКУЩИЙ RU: `"🫐 Искать ягоды"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🫐 Search berries"`
- ✏️ НОВЫЙ EN:


### forest.btn.cast

- ТЕКУЩИЙ RU: `"{emoji} Искать грибы"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"{emoji} Search mushrooms"`
- ✏️ НОВЫЙ EN:


### forest.btn.city

- ТЕКУЩИЙ RU: `"🔙 В город"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🔙 To the city"`
- ✏️ НОВЫЙ EN:


### forest.btn.deeper

- ТЕКУЩИЙ RU: `"Углубиться в лес"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Go deeper"`
- ✏️ НОВЫЙ EN:


### forest.btn.flee

- ТЕКУЩИЙ RU: `"🏃 Сбежать"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🏃 Run away"`
- ✏️ НОВЫЙ EN:


### forest.btn.hit

- ТЕКУЩИЙ RU: `"⚔️ Ударить"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⚔️ Strike"`
- ✏️ НОВЫЙ EN:


### forest.btn.log

- ТЕКУЩИЙ RU: `"🪓 Лесозаготовка"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🪓 Logging camp"`
- ✏️ НОВЫЙ EN:


### forest.btn.to_glade

- ТЕКУЩИЙ RU: `"{emoji} К опушке"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"{emoji} To the glade"`
- ✏️ НОВЫЙ EN:


### forest.btn.to_glade_plain

- ТЕКУЩИЙ RU: `"К опушке"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"To the glade"`
- ✏️ НОВЫЙ EN:


### forest.cast.clearing

- ТЕКУЩИЙ RU: `"{emoji} Ты идёшь по тропе к поляне...\nРезультат через {delay} секунд. Не шуми — прислушивайся!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"{emoji} You follow the trail toward the clearing...\nResult in {delay} seconds. Keep quiet — listen!"`
- ✏️ НОВЫЙ EN:


### forest.cast.glade

- ТЕКУЩИЙ RU: `"{emoji} Ты оглядываешь опушку...\nРезультат через {delay} секунд. Здесь тихо."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"{emoji} You scan the glade...\nResult in {delay} seconds. It's quiet here."`
- ✏️ НОВЫЙ EN:


### forest.counter.armor

- ТЕКУЩИЙ RU: `"🛡️ Броня поглотила {amount}. "`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🛡️ Armor absorbed {amount}. "`
- ✏️ НОВЫЙ EN:


### forest.counter.dodged

- ТЕКУЩИЙ RU: `"💨 Ты уклонился от рывка зверя! (−0 HP)\n\n"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"💨 You dodge the beast's lunge! (−0 HP)\n\n"`
- ✏️ НОВЫЙ EN:


### forest.counter.hit

- ТЕКУЩИЙ RU: `"Зверь бьёт: −{dmg} HP. {extra}\n\n"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"The beast strikes: −{dmg} HP. {extra}\n\n"`
- ✏️ НОВЫЙ EN:


### forest.deny.clearing

- ТЕКУЩИЙ RU: `"Дальше — только настоящим пилотам Нордхайма. Прогалина за опушкой раскинулась на десятки вёрст, а тропы между лесами незнакомые: чужой здесь легко заблудиться. Туристов сюда не пускают — и правильно."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Only real Nordheim pilots go further. The clearing beyond the glade stretches for dozens of versts, and the paths between the woods are unfamiliar: a stranger gets lost easily here. Tourists aren't let in — and rightly so."`
- ✏️ НОВЫЙ EN:


### forest.deny.default

- ТЕКУЩИЙ RU: `"Сюда туристов не пускают."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Tourists aren't allowed here."`
- ✏️ НОВЫЙ EN:


### forest.dungeon_block

- ТЕКУЩИЙ RU: `"⛔ Ты сейчас проходишь подземелье — бродить по лесу нельзя.\nВыйди из подземелья, а потом иди на {where}."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⛔ You're in a dungeon right now — no wandering through the forest.\nLeave the dungeon, then head to the {where}."`
- ✏️ НОВЫЙ EN:


### forest.hit.armor

- ТЕКУЩИЙ RU: `"🛡️ Шкура зверя поглотила {amount}. "`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🛡️ The beast's hide absorbed {amount}. "`
- ✏️ НОВЫЙ EN:


### forest.hit.crit

- ТЕКУЩИЙ RU: `"💥 crit! "`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"💥 crit! "`
- ✏️ НОВЫЙ EN:


### forest.hit.dodged

- ТЕКУЩИЙ RU: `"Ты замахнулся — но зверь увернулся в последний миг.\n\n"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"You swing — but the beast dodges at the last moment.\n\n"`
- ✏️ НОВЫЙ EN:


### forest.hit.hit

- ТЕКУЩИЙ RU: `"Ты бьёшь наотмашь: −{dmg} HP по зверю! {extra}\n\n"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"You strike hard: −{dmg} HP to the beast! {extra}\n\n"`
- ✏️ НОВЫЙ EN:


### forest.loot.got

- ТЕКУЩИЙ RU: `"Из поверженного зверя ты добыл:\n{loot}\n\nПоложено в инвентарь."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"From the fallen beast you gained:\n{loot}\n\nAdded to your inventory."`
- ✏️ НОВЫЙ EN:


### forest.loot.lost

- ТЕКУЩИЙ RU: `"Зверь повержен, но добыча потерялась. Сообщи хранителю."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"The beast is down, but the loot got lost. Tell the keeper."`
- ✏️ НОВЫЙ EN:


### forest.loot.none

- ТЕКУЩИЙ RU: `"Зверь повержен, но ничего ценного на этот раз не нашлось."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"The beast is down, but there was nothing valuable this time."`
- ✏️ НОВЫЙ EN:


### forest.mush.empty

- ТЕКУЩИЙ RU: `"{head}\n\nТы обошёл несколько полян, заглянул под каждую ёлку — а грибов и нет. Бывает. Попробуй ещё раз!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"{head}\n\nYou crossed a few clearings and peeked under every spruce — no mushrooms at all. It happens. Try again!"`
- ✏️ НОВЫЙ EN:


### forest.mush.found

- ТЕКУЩИЙ RU: `"{head}\n\n{kind} Ты нашёл: «{name}»!\n\n🎒 Гриб положен в инвентарь.{heal_line}{sell_line}"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"{head}\n\n{kind} You found: «{name}»!\n\n🎒 The mushroom is in your inventory.{heal_line}{sell_line}"`
- ✏️ НОВЫЙ EN:


### forest.mush.heal

- ТЕКУЩИЙ RU: `" Сырым восстанавливает {heal} HP в бою."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `" Eaten raw, it restores {heal} HP in battle."`
- ✏️ НОВЫЙ EN:


### forest.mush.lost

- ТЕКУЩИЙ RU: `"{head}\n\n🍄 Что-то нашёл, но предмет потерялся. Сообщи хранителю."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"{head}\n\n🍄 You found something, but the item got lost. Tell the keeper."`
- ✏️ НОВЫЙ EN:


### forest.mush.sell

- ТЕКУЩИЙ RU: `"\nПродать можно за {price} {money}."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"\nCan be sold for {price} {money}."`
- ✏️ НОВЫЙ EN:


### forest.mush.toxic

- ТЕКУЩИЙ RU: `"☠ Ядовитый гриб!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"☠ Poisonous mushroom!"`
- ✏️ НОВЫЙ EN:


### forest.regen

- ТЕКУЩИЙ RU: `"♻ Регенерация: +{heal} HP.\n\n"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"♻ Regeneration: +{heal} HP.\n\n"`
- ✏️ НОВЫЙ EN:


### forest.tourist_safe

- ТЕКУЩИЙ RU: `"Зато на опушке грибы собирают и туристы — там безопасно."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"But mushrooms are gathered on the glade, and tourists are welcome there — it's safe."`
- ✏️ НОВЫЙ EN:


### forest.where.clearing

- ТЕКУЩИЙ RU: `"прогалину"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"clearing"`
- ✏️ НОВЫЙ EN:


### forest.where.glade

- ТЕКУЩИЙ RU: `"опушку"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"glade"`
- ✏️ НОВЫЙ EN:


### forest.where_loc.clearing

- ТЕКУЩИЙ RU: `"на прогалине"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"on the clearing"`
- ✏️ НОВЫЙ EN:


### forest.where_loc.glade

- ТЕКУЩИЙ RU: `"на опушке леса"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"at the forest glade"`
- ✏️ НОВЫЙ EN:


### forest.ww.bless_big

- ТЕКУЩИЙ RU: `"🌟 Волк не тронул тебя — он признал достойного. БЛАГОСЛОВЕНИЕ СЕВЕРА снизошло на тебя на сутки:\n• +10% к атаке\n• +10% к уклонению\n• +5% к эффективности лечения\n• −3% к ценам в магазинах"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🌟 The wolf didn't touch you — it deemed you worthy. The BLESSING OF THE NORTH falls on you for a day:\n• +10% attack\n• +10% dodge\n• +5% healing efficiency\n• −3% shop prices"`
- ✏️ НОВЫЙ EN:


### forest.ww.bless_small

- ТЕКУЩИЙ RU: `"❄️ Волк отпускает тебя, но ты чувствуешь на себе его взгляд. ВНИМАНИЕ СЕВЕРА с тобой на сутки:\n• +5% к урону\n• +5% к уклонению"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❄️ The wolf lets you go, but you feel its gaze on you. The WARNING OF THE NORTH stays with you for a day:\n• +5% damage\n• +5% dodge"`
- ✏️ НОВЫЙ EN:


### forest.ww.defeat

- ТЕКУЩИЙ RU: `"Снег взрывается белой тенью — ты не успеваешь даже замахнуться. Морозные клыки смыкаются, и сознание гаснет...\n\nОчнулся ты в сугробе. Волк сидит рядом и смотрит прямо в душу.\n\n"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Snow bursts into a white shadow — you don't even get to swing. Frozen fangs close in, and consciousness fades...\n\nYou come to in a snowdrift. The wolf sits nearby, staring straight into your soul.\n\n"`
- ✏️ НОВЫЙ EN:


### forest.ww.enrage

- ТЕКУЩИЙ RU: `"🐺 {name} припадает к земле — рана на боку затягивается, в глазах вспыхивает северное сияние. Зверь словно стал больше и страшнее!\n\n"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🐺 {name} crouches low — the wound on its flank knits shut, northern lights flare in its eyes. The beast seems bigger and more terrible!\n\n"`
- ✏️ НОВЫЙ EN:


### forest.ww.tail

- ТЕКУЩИЙ RU: `"−{removed} ОД."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"−{removed} AP."`
- ✏️ НОВЫЙ EN:


### forest.ww.title

- ТЕКУЩИЙ RU: `"{emoji} БЕЛЫЙ ВОЛК СЕВЕРА"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"{emoji} WHITE WOLF OF THE NORTH"`
- ✏️ НОВЫЙ EN:


### forest.zone.beasts

- ТЕКУЩИЙ RU: `"Здесь водятся звери: {parts}."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Beasts live here: {parts}."`
- ✏️ НОВЫЙ EN:


### forest.zone.boar_chance

- ТЕКУЩИЙ RU: `"шанс встречи {chance}%"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"encounter chance {chance}%"`
- ✏️ НОВЫЙ EN:


### forest.zone.boar_every

- ТЕКУЩИЙ RU: `"не чаще одного раза на {every} попыток"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"at most once every {every} searches"`
- ✏️ НОВЫЙ EN:


### forest.zone.clearing_desc

- ТЕКУЩИЙ RU: `"За опушкой начинается настоящий лес. Прогалина тянется далеко, и растут здесь все грибы, какие только есть в Нордхайме — от опёнка до ежовика гребенчатого."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Past the glade the real forest begins. The clearing stretches far, and every mushroom Nordheim has grows here — from honey fungus to hericium."`
- ✏️ НОВЫЙ EN:


### forest.zone.closed

- ТЕКУЩИЙ RU: `"Сейчас сюда не пускают — зона закрыта. Загляни позже."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Entry is closed right now. Come back later."`
- ✏️ НОВЫЙ EN:


### forest.zone.glade_desc

- ТЕКУЩИЙ RU: `"Тёмный еловый лес начинается прямо за городской окраиной. На опушке — только самое простое: обычные грибы у дороги и изредка бледная поганка. Здесь спокойно, сюда пускают и туристов."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"The dark spruce forest begins right past the city edge. The glade has only the simplest finds: common mushrooms by the road and the occasional death cap. It's calm here, and tourists are welcome."`
- ✏️ НОВЫЙ EN:


### forest.zone.head

- ТЕКУЩИЙ RU: `"{prefix}{emoji} {title}\n\n{body}"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"{prefix}{emoji} {title}\n\n{body}"`
- ✏️ НОВЫЙ EN:


### forest.zone.screen

- ТЕКУЩИЙ RU: `"{desc}\n\n{ap_line}\n\nПоиск стоит {cost} ОД, результат через 5–10 секунд.\n\n🧺 Казна покупает грибы не больше {limit} НМ в сутки — остальное можно продать на рынке игроков."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"{desc}\n\n{ap_line}\n\nA search costs {cost} AP, result in 5–10 seconds.\n\n🧺 The treasury buys mushrooms up to {limit} NM a day — the rest can be sold on the players' market."`
- ✏️ НОВЫЙ EN:


### hq.reserve_line

- ТЕКУЩИЙ RU: `"Резерв: {total}"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Reserve: {total}"`
- ✏️ НОВЫЙ EN:


### hq.reserve_stale_tail

- ТЕКУЩИЙ RU: `" ({icon} {n} — не заходили больше недели)"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `" ({icon} {n} — inactive for over a week)"`
- ✏️ НОВЫЙ EN:


### hq.stale_legend

- ТЕКУЩИЙ RU: `"{icon} — не заходил в бота больше недели"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"{icon} — has not opened the bot for over a week"`
- ✏️ НОВЫЙ EN:


### inv.catch

- ТЕКУЩИЙ RU: `"Улов"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Catch"`
- ✏️ НОВЫЙ EN:


### inv.gear

- ТЕКУЩИЙ RU: `"Снаряжение"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Gear"`
- ✏️ НОВЫЙ EN:


### kgb.archive_card

- ТЕКУЩИЙ RU: `"📘 {name}\n\nДействующий паспорт: № {series} {number}\nВыдан: {issue_date}\n"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"📘 {name}\n\nCurrent passport: No. {series} {number}\nIssued: {issue_date}\n"`
- ✏️ НОВЫЙ EN:


### kgb.archive_empty

- ТЕКУЩИЙ RU: `"Паспортов пока не выдано."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"No passports issued yet."`
- ✏️ НОВЫЙ EN:


### kgb.archive_history_head

- ТЕКУЩИЙ RU: `"\nПрежние паспорта:"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"\nPrevious passports:"`
- ✏️ НОВЫЙ EN:


### kgb.archive_history_line

- ТЕКУЩИЙ RU: `"• № {series} {number}, выдан {issue_date}, заменён {replaced_at}"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"• No. {series} {number}, issued {issue_date}, replaced {replaced_at}"`
- ✏️ НОВЫЙ EN:


### kgb.archive_no_history

- ТЕКУЩИЙ RU: `"\nПрежних паспортов не было."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"\nNo previous passports."`
- ✏️ НОВЫЙ EN:


### kgb.archive_title

- ТЕКУЩИЙ RU: `"📚 Архив паспортов. Выбери пилота:"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"📚 Passport archive. Pick a pilot:"`
- ✏️ НОВЫЙ EN:


### kgb.ask_birth

- ТЕКУЩИЙ RU: `"Дата рождения, ДД.ММ.ГГГГ:"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Date of birth, DD.MM.YYYY:"`
- ✏️ НОВЫЙ EN:


### kgb.ask_full_name

- ТЕКУЩИЙ RU: `"Имя пилота:"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Pilot's name:"`
- ✏️ НОВЫЙ EN:


### kgb.ask_issue

- ТЕКУЩИЙ RU: `"Дата выдачи, ДД.ММ.ГГГГ (или «сегодня»):"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Issue date, DD.MM.YYYY (or «today»):"`
- ✏️ НОВЫЙ EN:


### kgb.ask_marital

- ТЕКУЩИЙ RU: `"Семейное положение (например: холост, женат, в разводе):"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Marital status (e.g. single, married, divorced):"`
- ✏️ НОВЫЙ EN:


### kgb.ask_marks

- ТЕКУЩИЙ RU: `"Особые приметы (или «нет»):"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Distinguishing marks (or «none»):"`
- ✏️ НОВЫЙ EN:


### kgb.ask_number

- ТЕКУЩИЙ RU: `"Номер паспорта — 6 цифр:"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Passport number — 6 digits:"`
- ✏️ НОВЫЙ EN:


### kgb.ask_photo

- ТЕКУЩИЙ RU: `"📷 Пришли фото для паспорта. Или нажми «Без фото»."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"📷 Send a photo for the passport, or press «No photo»."`
- ✏️ НОВЫЙ EN:


### kgb.ask_position

- ТЕКУЩИЙ RU: `"Должность:"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Position:"`
- ✏️ НОВЫЙ EN:


### kgb.ask_rank

- ТЕКУЩИЙ RU: `"Звание:"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Rank:"`
- ✏️ НОВЫЙ EN:


### kgb.ask_series

- ТЕКУЩИЙ RU: `"Серия паспорта — 4 цифры:"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Passport series — 4 digits:"`
- ✏️ НОВЫЙ EN:


### kgb.ask_sex

- ТЕКУЩИЙ RU: `"Пол:"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Sex:"`
- ✏️ НОВЫЙ EN:


### kgb.back_docs

- ТЕКУЩИЙ RU: `"🔙 К документам"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🔙 To documents"`
- ✏️ НОВЫЙ EN:


### kgb.bad_date

- ТЕКУЩИЙ RU: `"❌ Дата в формате ДД.ММ.ГГГГ, например 05.03.1990. Попробуй ещё раз:"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ Use the DD.MM.YYYY format, e.g. 05.03.1990. Try again:"`
- ✏️ НОВЫЙ EN:


### kgb.bad_number

- ТЕКУЩИЙ RU: `"❌ Номер — ровно 6 цифр. Попробуй ещё раз:"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ Number must be exactly 6 digits. Try again:"`
- ✏️ НОВЫЙ EN:


### kgb.bad_series

- ТЕКУЩИЙ RU: `"❌ Серия — ровно 4 цифры. Попробуй ещё раз:"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ Series must be exactly 4 digits. Try again:"`
- ✏️ НОВЫЙ EN:


### kgb.bad_text

- ТЕКУЩИЙ RU: `"❌ Поле не может быть пустым и должно быть не длиннее 64 символов. Попробуй ещё раз:"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ The field can't be empty and must be at most 64 characters. Try again:"`
- ✏️ НОВЫЙ EN:


### kgb.btn_archive

- ТЕКУЩИЙ RU: `"📚 Архив паспортов"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"📚 Passport archive"`
- ✏️ НОВЫЙ EN:


### kgb.btn_back

- ТЕКУЩИЙ RU: `"🔙 В квартал"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🔙 To the quarter"`
- ✏️ НОВЫЙ EN:


### kgb.btn_cancel

- ТЕКУЩИЙ RU: `"❌ Отмена"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ Cancel"`
- ✏️ НОВЫЙ EN:


### kgb.btn_confirm

- ТЕКУЩИЙ RU: `"✅ Выдать паспорт"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"✅ Issue passport"`
- ✏️ НОВЫЙ EN:


### kgb.btn_issue

- ТЕКУЩИЙ RU: `"🛂 Выдать паспорт"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🛂 Issue passport"`
- ✏️ НОВЫЙ EN:


### kgb.btn_sex_f

- ТЕКУЩИЙ RU: `"Женский"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Female"`
- ✏️ НОВЫЙ EN:


### kgb.btn_sex_m

- ТЕКУЩИЙ RU: `"Мужской"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Male"`
- ✏️ НОВЫЙ EN:


### kgb.btn_skip_photo

- ТЕКУЩИЙ RU: `"⏭ Без фото"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⏭ No photo"`
- ✏️ НОВЫЙ EN:


### kgb.cancelled

- ТЕКУЩИЙ RU: `"Выдача паспорта отменена."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Passport issue cancelled."`
- ✏️ НОВЫЙ EN:


### kgb.card_title

- ТЕКУЩИЙ RU: `"🛂 ПАСПОРТ НОРДХАЙМА"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🛂 NORDHEIM PASSPORT"`
- ✏️ НОВЫЙ EN:


### kgb.exists_warn

- ТЕКУЩИЙ RU: `"⚠️ У пилота уже есть паспорт (№ {series} {number}). Новая выдача заменит его данные.\n\n"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⚠️ The pilot already has a passport (No. {series} {number}). A new issue replaces its data.\n\n"`
- ✏️ НОВЫЙ EN:


### kgb.f_birth

- ТЕКУЩИЙ RU: `"Дата рождения"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Date of birth"`
- ✏️ НОВЫЙ EN:


### kgb.f_issue

- ТЕКУЩИЙ RU: `"Дата выдачи"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Issue date"`
- ✏️ НОВЫЙ EN:


### kgb.f_marital

- ТЕКУЩИЙ RU: `"Семейное положение"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Marital status"`
- ✏️ НОВЫЙ EN:


### kgb.f_marks

- ТЕКУЩИЙ RU: `"Особые приметы"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Distinguishing marks"`
- ✏️ НОВЫЙ EN:


### kgb.f_name

- ТЕКУЩИЙ RU: `"Имя"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Name"`
- ✏️ НОВЫЙ EN:


### kgb.f_number

- ТЕКУЩИЙ RU: `"Номер"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Number"`
- ✏️ НОВЫЙ EN:


### kgb.f_position

- ТЕКУЩИЙ RU: `"Должность"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Position"`
- ✏️ НОВЫЙ EN:


### kgb.f_rank

- ТЕКУЩИЙ RU: `"Звание"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Rank"`
- ✏️ НОВЫЙ EN:


### kgb.f_series

- ТЕКУЩИЙ RU: `"Серия"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Series"`
- ✏️ НОВЫЙ EN:


### kgb.f_sex

- ТЕКУЩИЙ RU: `"Пол"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Sex"`
- ✏️ НОВЫЙ EN:


### kgb.has_passport_mark

- ТЕКУЩИЙ RU: `"✅ {series}"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"✅ {series}"`
- ✏️ НОВЫЙ EN:


### kgb.head_only

- ТЕКУЩИЙ RU: `"⛔ Паспорта выдаёт только глава КГБ."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⛔ Only the KGB head issues passports."`
- ✏️ НОВЫЙ EN:


### kgb.inv_hint

- ТЕКУЩИЙ RU: `"Документ нельзя продать или передать."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"This document can't be sold or transferred."`
- ✏️ НОВЫЙ EN:


### kgb.issued

- ТЕКУЩИЙ RU: `"✅ Паспорт выдан: {name}. Серия {series} № {number}."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"✅ Passport issued to {name}. Series {series} No. {number}."`
- ✏️ НОВЫЙ EN:


### kgb.issued_pilot

- ТЕКУЩИЙ RU: `"🛂 Тебе выдан паспорт Нордхайма. Он в инвентаре, в разделе «📄 Документы». Серия {series} № {number}."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🛂 You have been issued a Nordheim passport. It's in your inventory, under «📄 Documents». Series {series} No. {number}."`
- ✏️ НОВЫЙ EN:


### kgb.menu_title

- ТЕКУЩИЙ RU: `"🕵️ ЗДАНИЕ КГБ\n────────────────\nСлужба государственной безопасности Нордхайма. Здесь ведётся учёт личных дел пилотов и выдаются паспорта."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🕵️ KGB BUILDING\n────────────────\nThe State Security Service of Nordheim. Personnel files are kept here and passports are issued."`
- ✏️ НОВЫЙ EN:


### kgb.no_access

- ТЕКУЩИЙ RU: `"⛔ Вход в здание КГБ — только для сотрудников КГБ."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⛔ The KGB building is for KGB staff only."`
- ✏️ НОВЫЙ EN:


### kgb.no_passport

- ТЕКУЩИЙ RU: `"У тебя пока нет паспорта. Его выдаёт глава КГБ."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"You don't have a passport yet. The KGB head issues them."`
- ✏️ НОВЫЙ EN:


### kgb.number_taken

- ТЕКУЩИЙ RU: `"❌ Такая серия и номер уже у другого пилота. Введи номер заново:"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ This series and number already belong to another pilot. Enter the number again:"`
- ✏️ НОВЫЙ EN:


### kgb.photo_only

- ТЕКУЩИЙ RU: `"❌ Нужна картинка. Пришли фото или нажми «Без фото»."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ Send a picture, or press «No photo»."`
- ✏️ НОВЫЙ EN:


### kgb.pick_empty

- ТЕКУЩИЙ RU: `"Пилотов для выдачи нет."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"No pilots to issue to."`
- ✏️ НОВЫЙ EN:


### kgb.pick_title

- ТЕКУЩИЙ RU: `"🛂 Кому выдать паспорт? Выбери пилота:"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🛂 Who gets the passport? Pick a pilot:"`
- ✏️ НОВЫЙ EN:


### kgb.preview

- ТЕКУЩИЙ RU: `"Проверь данные паспорта:"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Check the passport details:"`
- ✏️ НОВЫЙ EN:


### kgb.sex_f

- ТЕКУЩИЙ RU: `"женский"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"female"`
- ✏️ НОВЫЙ EN:


### kgb.sex_m

- ТЕКУЩИЙ RU: `"мужской"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"male"`
- ✏️ НОВЫЙ EN:


### lang.switched_en

- ТЕКУЩИЙ RU: `"🌐 Язык: English"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🌐 Language: English"`
- ✏️ НОВЫЙ EN:


### lang.switched_ru

- ТЕКУЩИЙ RU: `"🌐 Язык: Русский"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🌐 Language: Русский"`
- ✏️ НОВЫЙ EN:


### loc.bank

- ТЕКУЩИЙ RU: `"Банк"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Bank"`
- ✏️ НОВЫЙ EN:


### loc.contracts

- ТЕКУЩИЙ RU: `"Доска контрактов"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Contract Board"`
- ✏️ НОВЫЙ EN:


### loc.duel_house

- ТЕКУЩИЙ RU: `"Дом Дуэлей"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Duel House"`
- ✏️ НОВЫЙ EN:


### loc.forest

- ТЕКУЩИЙ RU: `"Лес на окраине"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Outskirts Forest"`
- ✏️ НОВЫЙ EN:


### loc.gossmi

- ТЕКУЩИЙ RU: `"ГосСМИ"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"State Media"`
- ✏️ НОВЫЙ EN:


### loc.hq

- ТЕКУЩИЙ RU: `"Штаб ВВС"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Air Force HQ"`
- ✏️ НОВЫЙ EN:


### loc.kgb

- ТЕКУЩИЙ RU: `"Здание КГБ"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"KGB Building"`
- ✏️ НОВЫЙ EN:


### loc.kvp

- ТЕКУЩИЙ RU: `"Курс выживания"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Survival Course"`
- ✏️ НОВЫЙ EN:


### loc.library

- ТЕКУЩИЙ RU: `"Библиотека"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Library"`
- ✏️ НОВЫЙ EN:


### loc.mine

- ТЕКУЩИЙ RU: `"Железная копи"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Iron Mine"`
- ✏️ НОВЫЙ EN:


### loc.mvd

- ТЕКУЩИЙ RU: `"Здание МВД"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Interior Ministry"`
- ✏️ НОВЫЙ EN:


### loc.nii

- ТЕКУЩИЙ RU: `"НИИ Северной Кибернетики"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Northern Cybernetics Institute"`
- ✏️ НОВЫЙ EN:


### loc.park

- ТЕКУЩИЙ RU: `"Городской парк"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"City Park"`
- ✏️ НОВЫЙ EN:


### loc.storage

- ТЕКУЩИЙ RU: `"Городские склады"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"City Warehouses"`
- ✏️ НОВЫЙ EN:


### loc.townhall

- ТЕКУЩИЙ RU: `"Ратуша"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Town Hall"`
- ✏️ НОВЫЙ EN:


### logging.alert.busy

- ТЕКУЩИЙ RU: `"Ты уже замахнулся топором — дождись результата!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"You're already swinging — wait for the result!"`
- ✏️ НОВЫЙ EN:


### logging.alert.fire_ap

- ТЕКУЩИЙ RU: `"❌ Не хватает ОД: на одно бревно нужно {cost} ОД, а у тебя {ap}."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ Not enough AP: one log needs {cost} AP, you have {ap}."`
- ✏️ НОВЫЙ EN:


### logging.alert.fire_dungeon

- ТЕКУЩИЙ RU: `"⛔ Ты в подземелье — тут не до дров."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⛔ You're in a dungeon — no time for firewood."`
- ✏️ НОВЫЙ EN:


### logging.alert.fire_no_logs

- ТЕКУЩИЙ RU: `"❌ Нет брёвен для рубки на дрова."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ No logs for firewood."`
- ✏️ НОВЫЙ EN:


### logging.alert.in_dungeon

- ТЕКУЩИЙ RU: `"⛔ Ты в подземелье — рубить деревья нельзя!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⛔ You're in a dungeon — no chopping!"`
- ✏️ НОВЫЙ EN:


### logging.alert.no_ap

- ТЕКУЩИЙ RU: `"❌ Не хватает ОД."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ Not enough AP."`
- ✏️ НОВЫЙ EN:


### logging.alert.no_logs

- ТЕКУЩИЙ RU: `"❌ Нет брёвен для распила."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ No logs to saw."`
- ✏️ НОВЫЙ EN:


### logging.alert.no_start

- ТЕКУЩИЙ RU: `"Сначала нажми /start"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Press /start first"`
- ✏️ НОВЫЙ EN:


### logging.alert.plank_dungeon

- ТЕКУЩИЙ RU: `"⛔ Ты в подземелье — тут не до распила."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⛔ You're in a dungeon — no time for sawing."`
- ✏️ НОВЫЙ EN:


### logging.alert.plank_money

- ТЕКУЩИЙ RU: `"❌ Не хватает денег: распил одного бревна стоит {fee} НМ, а у тебя {nm}."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ Not enough money: sawing one log costs {fee} NM, you have {nm}."`
- ✏️ НОВЫЙ EN:


### logging.alert.tourist

- ТЕКУЩИЙ RU: `"⛔ На лесозаготовку туристов не пускают."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⛔ Tourists aren't allowed at the logging camp."`
- ✏️ НОВЫЙ EN:


### logging.alert.wood_short

- ТЕКУЩИЙ RU: `"❌ Брёвен уже не хватает."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ Not enough logs anymore."`
- ✏️ НОВЫЙ EN:


### logging.bat.armor.owl

- ТЕКУЩИЙ RU: `"🛡️ {amount} урона поглотило оперение. "`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🛡️ {amount} damage absorbed by its feathers. "`
- ✏️ НОВЫЙ EN:


### logging.bat.armor.snake

- ТЕКУЩИЙ RU: `"🛡️ {amount} урона поглотила чешуя. "`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🛡️ {amount} damage absorbed by its scales. "`
- ✏️ НОВЫЙ EN:


### logging.bat.counter.owl

- ТЕКУЩИЙ RU: `"Неясыть бьёт когтем: −{dmg} HP. {extra}\n\n"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"The owl rakes you with a claw: −{dmg} HP. {extra}\n\n"`
- ✏️ НОВЫЙ EN:


### logging.bat.counter.snake

- ТЕКУЩИЙ RU: `"Змея бьёт: −{dmg} HP. {extra}\n\n"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"The snake strikes: −{dmg} HP. {extra}\n\n"`
- ✏️ НОВЫЙ EN:


### logging.bat.dodged

- ТЕКУЩИЙ RU: `"💨 Ты уклоняешься от выпада! (−0 HP)\n\n"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"💨 You dodge the lunge! (−0 HP)\n\n"`
- ✏️ НОВЫЙ EN:


### logging.bat.expired

- ТЕКУЩИЙ RU: `"⏳ Бой устарел."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⏳ The fight is out of date."`
- ✏️ НОВЫЙ EN:


### logging.bat.flee.owl

- ТЕКУЩИЙ RU: `"🏃 Ты отступаешь к сторожке, не сводя глаз с тяжёлого силуэта над кронами.\n\nСова ушла — и хорошо. Рубка-то не закончена! Попробуй ещё раз!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🏃 You back off toward the lodge, eyes on the heavy shape above the treetops.\n\nThe owl is gone — good. The chopping isn't finished! Try again!"`
- ✏️ НОВЫЙ EN:


### logging.bat.flee.snake

- ТЕКУЩИЙ RU: `"🏃 Ты отступаешь к сторожке, отмахиваясь от врага.\n\nБой окончен — но рубка-то не закончена! Попробуй ещё раз!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🏃 You back off toward the lodge, swatting at the enemy.\n\nThe fight is over — but the chopping isn't! Try again!"`
- ✏️ НОВЫЙ EN:


### logging.bat.hit

- ТЕКУЩИЙ RU: `"Ты бьёшь наотмашь: −{dmg} HP по врагу! {extra}\n\n"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"You strike hard: −{dmg} HP to the enemy! {extra}\n\n"`
- ✏️ НОВЫЙ EN:


### logging.bat.miss.owl

- ТЕКУЩИЙ RU: `"Ты бьёшь — но неясыть отклоняется в воздухе, хлопая крылом.\n\n"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"You strike — but the owl swerves in the air, beating its wing.\n\n"`
- ✏️ НОВЫЙ EN:


### logging.bat.miss.snake

- ТЕКУЩИЙ RU: `"Ты бьёшь — но змея уходит в сторону, словно сквозь тень.\n\n"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"You strike — but the snake slips aside like a shadow.\n\n"`
- ✏️ НОВЫЙ EN:


### logging.bat.owl_appears

- ТЕКУЩИЙ RU: `"Из чащи вылетает тяжёлый силуэт — Неясыть! Совиный глаз прикован к тебе.\n\n"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"A heavy shape bursts out of the thicket — an Owl! Its eye is fixed on you.\n\n"`
- ✏️ НОВЫЙ EN:


### logging.bat.owl_fled

- ТЕКУЩИЙ RU: `"Раненая неясыть бросает бой: тяжёлый силуэт вздымается над кронами и растворяется в сумерках. Ты победил!\n\n"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"The wounded owl gives up the fight: its heavy shape rises above the treetops and dissolves into dusk. You won!\n\n"`
- ✏️ НОВЫЙ EN:


### logging.bat.owl_loot

- ТЕКУЩИЙ RU: `"Из-под крыла, которым неясыть прикрывала гнездо, падает:\n{loot}\n\nПоложено в инвентарь."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"From under the wing the owl used to shield its nest, falls:\n{loot}\n\nAdded to your inventory."`
- ✏️ НОВЫЙ EN:


### logging.bat.owl_loot_none

- ТЕКУЩИЙ RU: `"Сова улетела, не роняя ничего — на этот раз обошлось без трофеев."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"The owl flew off, dropping nothing — no trophies this time."`
- ✏️ НОВЫЙ EN:


### logging.bat.owl_lost

- ТЕКУЩИЙ RU: `"Когти впиваются в плечо, крыло обрушивает темноту — сознание гаснет...\n\nОчнулся ты у сторожки, весь в ссадинах. Неясыть ушла в чащу (−{removed} ОД)."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Claws dig into your shoulder, a wing drowns you in darkness — you black out...\n\nYou come to by the lodge, bruised all over. The owl flew off into the thicket (−{removed} AP)."`
- ✏️ НОВЫЙ EN:


### logging.bat.owl_tail

- ТЕКУЩИЙ RU: `"Сову нельзя убить — она сама решит, когда отступить."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"You can't kill the owl — it will decide for itself when to back off."`
- ✏️ НОВЫЙ EN:


### logging.bat.owl_title

- ТЕКУЩИЙ RU: `"{emoji} НЕЯСЫТЬ"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"{emoji} OWL"`
- ✏️ НОВЫЙ EN:


### logging.bat.round_tail

- ТЕКУЩИЙ RU: `"Ход {round}. {tail}"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Turn {round}. {tail}"`
- ✏️ НОВЫЙ EN:


### logging.bat.snake_appears

- ТЕКУЩИЙ RU: `"Из-под валуна с шипением выползает длинная тень — Лесная змея!\n\n"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"A long shadow hisses out from under a boulder — a Forest Snake!\n\n"`
- ✏️ НОВЫЙ EN:


### logging.bat.snake_down

- ТЕКУЩИЙ RU: `"Змея дёргается и замирает — подлесок снова затихает.\n\n"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"The snake jerks and goes still — the undergrowth falls quiet again.\n\n"`
- ✏️ НОВЫЙ EN:


### logging.bat.snake_loot

- ТЕКУЩИЙ RU: `"Из-под поверженной змеи ты забираешь:\n{loot}\n\nПоложено в инвентарь."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"From under the fallen snake you take:\n{loot}\n\nAdded to your inventory."`
- ✏️ НОВЫЙ EN:


### logging.bat.snake_loot_none

- ТЕКУЩИЙ RU: `"Змея повержена, но ничего ценного на этот раз не нашлось."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"The snake is down, but there was nothing valuable this time."`
- ✏️ НОВЫЙ EN:


### logging.bat.snake_lost

- ТЕКУЩИЙ RU: `"Мир плывёт, зубы холодят кровь — сознание гаснет...\n\nОчнулся ты у сторожки, тяжело дыша. Змея уползла в подлесок (−{removed} ОД)."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"The world swims, fangs chill your blood — you black out...\n\nYou come to by the lodge, gasping. The snake slid off into the undergrowth (−{removed} AP)."`
- ✏️ НОВЫЙ EN:


### logging.bat.snake_tail

- ТЕКУЩИЙ RU: `"Ударь змею — или уноси ноги."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Strike the snake — or run for it."`
- ✏️ НОВЫЙ EN:


### logging.bat.snake_title

- ТЕКУЩИЙ RU: `"{emoji} БОЙ СО ЗМЕЁЙ"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"{emoji} SNAKE FIGHT"`
- ✏️ НОВЫЙ EN:


### logging.btn.back

- ТЕКУЩИЙ RU: `"🔙 На прогалину"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🔙 Back to the clearing"`
- ✏️ НОВЫЙ EN:


### logging.btn.back_plain

- ТЕКУЩИЙ RU: `"🔙 Назад"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🔙 Back"`
- ✏️ НОВЫЙ EN:


### logging.btn.chop

- ТЕКУЩИЙ RU: `"🪓 Рубить дерево"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🪓 Chop a tree"`
- ✏️ НОВЫЙ EN:


### logging.btn.chop_again

- ТЕКУЩИЙ RU: `"🪓 Рубить ещё"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🪓 Chop again"`
- ✏️ НОВЫЙ EN:


### logging.btn.fire_all

- ТЕКУЩИЙ RU: `"🪓 Всё ({cnt} дров)"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🪓 All ({cnt} firewood)"`
- ✏️ НОВЫЙ EN:


### logging.btn.fire_one

- ТЕКУЩИЙ RU: `"🪓 1 бревно ({cnt} дров)"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🪓 1 log ({cnt} firewood)"`
- ✏️ НОВЫЙ EN:


### logging.btn.flee

- ТЕКУЩИЙ RU: `"🏃 Сбежать"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🏃 Run away"`
- ✏️ НОВЫЙ EN:


### logging.btn.hit

- ТЕКУЩИЙ RU: `"⚔️ Ударить"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⚔️ Strike"`
- ✏️ НОВЫЙ EN:


### logging.btn.mill

- ТЕКУЩИЙ RU: `"🪚 Переработка брёвен"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🪚 Log processing"`
- ✏️ НОВЫЙ EN:


### logging.btn.plank_all

- ТЕКУЩИЙ RU: `"🪚 Всё ({cnt})"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🪚 All ({cnt})"`
- ✏️ НОВЫЙ EN:


### logging.btn.plank_one

- ТЕКУЩИЙ RU: `"🪚 1 бревно ({cnt})"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🪚 1 log ({cnt})"`
- ✏️ НОВЫЙ EN:


### logging.entrance

- ТЕКУЩИЙ RU: `"🪓 ЛЕСОЗАГОТОВКА\n\nЗа дальнейшей опушкой, там, где тропа уходит в самый глухой подлесок, стоит сторожка лесорубов. Здесь пахнет свежими стружками и хвоей — и отсюда редко кто возвращается с пустыми руками. Или вообще не возвращается.\n\n{hint}\n\nРубка дерева стоит {cost} ОД, результат через {lo}–{hi} секунд.{mill_hint}\n\n{ap_line}"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🪓 LOGGING CAMP\n\nPast the last clearing, where the path disappears into the thickest undergrowth, stands the loggers' lodge. It smells of fresh shavings and pine — and few come back from here empty-handed. Or not at all.\n\n{hint}\n\nA tree chop costs {cost} AP, result in {lo}–{hi} seconds.{mill_hint}\n\n{ap_line}"`
- ✏️ НОВЫЙ EN:


### logging.fire.no_axe

- ТЕКУЩИЙ RU: `"❌ Чтобы наколоть дров, нужен топор. Купи «Топор» в магазине (категория «Добыча ресурсов»)."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ You need an axe to split firewood. Buy one in the shop (Resource Mining)."`
- ✏️ НОВЫЙ EN:


### logging.firewood.result

- ТЕКУЩИЙ RU: `"🪓 РУБКА ДРОВ\n\nТы ставишь бревно на плаху и работаешь топором: щепки веером, из {n} {n_w} вышло {firewood} «{name}» — {pack_verb} у сторожки.\n\n⚡ Потрачено ОД: {spent}.\n🎒 Получено: «{name}» x{firewood}.\n📦 Осталось: {left} {left_w}.\n\n{ap_line}"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🪓 FIREWOOD CHOPPING\n\nYou set the log on the block and work the axe: chips fly everywhere — {n} log(s) gave {firewood} «{name}», stacked by the lodge.\n\n⚡ AP spent: {spent}.\n🎒 Received: «{name}» x{firewood}.\n📦 Left: {left} {left_w}.\n\n{ap_line}"`
- ✏️ НОВЫЙ EN:


### logging.hint.has_axe

- ТЕКУЩИЙ RU: `"🪓 Топор: {name} (ступень {rank}, шанс рубки {chance}%) — за работу!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🪓 Axe: {name} (tier {rank}, chop chance {chance}%) — get to work!"`
- ✏️ НОВЫЙ EN:


### logging.hint.no_axe

- ТЕКУЩИЙ RU: `"🪓 Без топора сюда не пускают: купи «Топор» (магазин → Добыча ресурсов)."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🪓 No axe, no entry: buy an axe (Shop → Resource Mining)."`
- ✏️ НОВЫЙ EN:


### logging.in_dungeon

- ТЕКУЩИЙ RU: `"⛔ Ты сейчас проходишь подземелье — рубить деревья нельзя.\nВыйди из подземелья, а потом возвращайся."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⛔ You're in a dungeon right now — no chopping.\nLeave the dungeon and come back."`
- ✏️ НОВЫЙ EN:


### logging.mill.empty

- ТЕКУЩИЙ RU: `"🪚 Переработка\n\nУ тебя нет брёвен — сначала наруби деревьев."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🪚 Log processing\n\nYou have no logs — chop some trees first."`
- ✏️ НОВЫЙ EN:


### logging.mill.screen

- ТЕКУЩИЙ RU: `"🪚 ПЕРЕРАБОТКА БРЁВЕН\n\n🎒 В инвентаре: {inv}\n💰 Кошелёк: {nm} {nm_word} НМ\n⚡ ОД: {ap}\n\n🪚 Распил на доски (артель)\n   1 бревно → {py} {py_w} «{pn}», плата {fee} НМ за бревно (в казну), топор не нужен.\n   Доступно: {pw} {pw_w} → {pl} {pl_w}.\n\n🪓 Рубка дров (самостоятельно)\n   1 бревно → {fy} {fy_w} «{fn}», тратит {fap} ОД за бревно, нужен топор.\n   Доступно: {fwq} {fwq_w} → {fw} {fw_w} дров."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🪚 LOG PROCESSING\n\n🎒 In inventory: {inv}\n💰 Purse: {nm} {nm_word}\n⚡ AP: {ap}\n\n🪚 Sawing into planks (the mill)\n   1 log → {py} {py_w} «{pn}», fee {fee} per log (to the treasury), no axe needed.\n   Available: {pw} {pw_w} → {pl} {pl_w}.\n\n🪓 Chopping firewood (by hand)\n   1 log → {fy} {fy_w} «{fn}», costs {fap} AP per log, needs an axe.\n   Available: {fwq} {fwq_w} → {fw} {fw_w} of firewood."`
- ✏️ НОВЫЙ EN:


### logging.mill_hint

- ТЕКУЩИЙ RU: `"\n\n🪚 В сарае {qty} — можно распилить их на доски в артели или наколоть дров."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"\n\n🪚 {qty} in the shed — you can saw them into planks at the mill or split them for firewood."`
- ✏️ НОВЫЙ EN:


### logging.no_ap

- ТЕКУЩИЙ RU: `"❌ Не хватает ОД: нужно {cost}, доступно меньше. Восстановление — в новые сутки."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ Not enough AP: you need {cost}. AP comes back with the new day."`
- ✏️ НОВЫЙ EN:


### logging.no_axe

- ТЕКУЩИЙ RU: `"❌ У тебя нет топора. Купи «Топор» в магазине (категория «Добыча ресурсов»)."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ You have no axe. Buy one in the shop (Resource Mining category)."`
- ✏️ НОВЫЙ EN:


### logging.plank.result

- ТЕКУЩИЙ RU: `"🪚 РАСПИЛ БРЁВЕН\n\nАртельные пилы визжат, опилки летят в лицо: {n} {n_w} {verb} в {planks} {planks_w}.\n\n💰 Заплачено артели: {fee} НМ (ушло в казну).\n🎒 Получено: «{name}» x{planks}.\n📦 Осталось: {left} {left_w}."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🪚 LOG SAWING\n\nThe mill saws whine, sawdust flies in your face: {n} log(s) become {planks} plank(s).\n\n💰 Paid to the mill: {fee} (to the treasury).\n🎒 Received: «{name}» x{planks}.\n📦 Left: {left} {left_w}."`
- ✏️ НОВЫЙ EN:


### logging.res.firewood

- ТЕКУЩИЙ RU: `"{head}\n\nУдар за ударом — стружка летит, но сук топор не берёт: сучковатое дерево уходит на дрова.\nПробуй ещё!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"{head}\n\nStrike after strike — chips fly, but the knot won't give to the axe: the knotty tree goes to firewood.\nKeep trying!"`
- ✏️ НОВЫЙ EN:


### logging.res.firewood_loot

- ТЕКУЩИЙ RU: `"\n\n🎒 Добыча: «{name}» — в инвентарь."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"\n\n🎒 Loot: «{name}» — added to your inventory."`
- ✏️ НОВЫЙ EN:


### logging.res.lost

- ТЕКУЩИЙ RU: `"{head}\n\n🌲 Срубил что-то, но предмет потерялся. Сообщи хранителю."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"{head}\n\n🌲 You felled something, but the item got lost. Tell the keeper."`
- ✏️ НОВЫЙ EN:


### logging.res.slip

- ТЕКУЩИЙ RU: `"{head}\n\nТопор от усталости неудачно отскакивает от мощного ствола и отлетает пилоту в плечо.\n\nРесурса не получено, попытка потрачена."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"{head}\n\nThe axe glances off the thick trunk out of fatigue and bounces back at your shoulder.\n\nNo resource gained, the attempt is spent."`
- ✏️ НОВЫЙ EN:


### logging.res.wood

- ТЕКУЩИЙ RU: `"{head}\n\nТопор звонко вгрызается в древесину — с ровным треском падает свежесрубленное бревно!\n\n🎒 Добыча: «{name}» — в инвентарь.{sell_line}"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"{head}\n\nThe axe bites into the wood with a clean crack — a freshly felled log drops!\n\n🎒 Loot: «{name}» — added to your inventory.{sell_line}"`
- ✏️ НОВЫЙ EN:


### logging.res.wood_sell

- ТЕКУЩИЙ RU: `"\nКазна выкупает бревна по {price} {money} за штуку."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"\nThe treasury buys logs at {price} {money} each."`
- ✏️ НОВЫЙ EN:


### logging.swing

- ТЕКУЩИЙ RU: `"🪓 Ты размахиваешься топором и рубишь дерево...\nРезультат через {delay} секунд. Не поранься — и не дремли: в подлеске что-то шевелится!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🪓 You swing the axe at the tree...\nResult in {delay} seconds. Don't cut yourself — and don't doze: something moves in the undergrowth!"`
- ✏️ НОВЫЙ EN:


### logging.tourist

- ТЕКУЩИЙ RU: `"⛔ На лесозаготовку не пускают туристов — это работа настоящих пилотов."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⛔ Tourists aren't allowed at the logging camp — this is real pilots' work."`
- ✏️ НОВЫЙ EN:


### menu.choose

- ТЕКУЩИЙ RU: `"Выберите действие:"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Choose an action:"`
- ✏️ НОВЫЙ EN:


### mine.alert.busy

- ТЕКУЩИЙ RU: `"Ты уже замахнулся киркой — дождись результата!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"You're already swinging — wait for the result!"`
- ✏️ НОВЫЙ EN:


### mine.alert.in_dungeon

- ТЕКУЩИЙ RU: `"⛔ Ты в подземелье — в копи нельзя!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⛔ You're in a dungeon — no mine!"`
- ✏️ НОВЫЙ EN:


### mine.alert.tourist

- ТЕКУЩИЙ RU: `"⛔ В копи не пускают туристов."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⛔ Tourists aren't allowed in the mine."`
- ✏️ НОВЫЙ EN:


### mine.ap_line

- ТЕКУЩИЙ RU: `"⚡ ОД: {ap}/{ap_max}"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⚡ AP: {ap}/{ap_max}"`
- ✏️ НОВЫЙ EN:


### mine.ap_ok

- ТЕКУЩИЙ RU: `" — можно копать ещё"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `" — you can keep digging"`
- ✏️ НОВЫЙ EN:


### mine.ap_short

- ТЕКУЩИЙ RU: `" — на следующий удар не хватит ({cost} ОД)"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `" — not enough for the next strike ({cost} AP)"`
- ✏️ НОВЫЙ EN:


### mine.bat_appears

- ТЕКУЩИЙ RU: `"Из темноты штольни с писком выныривает крылатая тень — Летучая мышь!\n\n"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"A winged shadow darts out of the dark shaft with a squeak — a Cave Bat!\n\n"`
- ✏️ НОВЫЙ EN:


### mine.bat_expired

- ТЕКУЩИЙ RU: `"⏳ Бой с мышью устарел."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⏳ The bat fight is out of date."`
- ✏️ НОВЫЙ EN:


### mine.btn.deeper

- ТЕКУЩИЙ RU: `"🪜 Спуститься глубже"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🪜 Go deeper"`
- ✏️ НОВЫЙ EN:


### mine.btn.dig

- ТЕКУЩИЙ RU: `"⛏ Добыть руду"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⛏ Mine ore"`
- ✏️ НОВЫЙ EN:


### mine.btn.dig_again

- ТЕКУЩИЙ RU: `"⛏ Добыть ещё"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⛏ Mine again"`
- ✏️ НОВЫЙ EN:


### mine.btn.exit

- ТЕКУЩИЙ RU: `"🚪 Выйти из шахты"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🚪 Leave the mine"`
- ✏️ НОВЫЙ EN:


### mine.btn.flee

- ТЕКУЩИЙ RU: `"🏃 Сбежать"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🏃 Flee"`
- ✏️ НОВЫЙ EN:


### mine.btn.hit

- ТЕКУЩИЙ RU: `"⚔️ Ударить"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⚔️ Strike"`
- ✏️ НОВЫЙ EN:


### mine.btn.level1

- ТЕКУЩИЙ RU: `"⛏ Уровень 1 шахт"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⛏ Mine level 1"`
- ✏️ НОВЫЙ EN:


### mine.deeper_stub

- ТЕКУЩИЙ RU: `"🪜 Спуск на второй уровень ещё не обустроен — работы идут."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🪜 The second level isn't ready yet — work is in progress."`
- ✏️ НОВЫЙ EN:


### mine.empty

- ТЕКУЩИЙ RU: `"{head}\n\nУдар за ударом — только каменная крошка да серый блеск.\nПорода сегодня пуста. Пробуй ещё!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"{head}\n\nStrike after strike — only grit and grey glints.\nThe rock is empty today. Keep trying!"`
- ✏️ НОВЫЙ EN:


### mine.entrance

- ТЕКУЩИЙ RU: `"⛏ ЖЕЛЕЗНАЯ КОПЬ\n\nЛампы у входа мерцают, из штольни тянет холодом и запахом руды. Ворота открыты — но где-то в глубине шелестит крыльями здешняя хозяйка.\n\n{hint}\n\nСпустись на первый уровень шахт или вернись в город."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⛏ IRON MINE\n\nLamps flicker at the entrance, cold and the smell of ore drift up from the shaft. The gate is open — but somewhere deep below, the mine's mistress rustles her wings.\n\n{hint}\n\nGo down to the first mine level or head back to town."`
- ✏️ НОВЫЙ EN:


### mine.flame_found

- ТЕКУЩИЙ RU: `"{head}\n\nВ породе блеснул жар — из камня выкололся тёплый кусок пламенной руды!\n\n🎒 Добыча: «{name}» — в инвентарь."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"{head}\n\nHeat flashed in the rock — a warm chunk of flame ore broke free!\n\n🎒 Loot: «{name}» — added to your inventory."`
- ✏️ НОВЫЙ EN:


### mine.hint.has_pickaxe

- ТЕКУЩИЙ RU: `"⛏ У тебя есть кирка: {name} — спускайся и бей породу."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⛏ You have a pickaxe: {name} — go down and strike the rock."`
- ✏️ НОВЫЙ EN:


### mine.hint.no_pickaxe

- ТЕКУЩИЙ RU: `"⛏ Без кирки в штольню не сунешься: купи «Кирка» (магазин → Добыча ресурсов)."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⛏ You can't go down without a pickaxe: buy one (Shop → Resource Mining)."`
- ✏️ НОВЫЙ EN:


### mine.in_dungeon

- ТЕКУЩИЙ RU: `"⛔ Ты сейчас проходишь подземелье — в копи нельзя.\nВыйди из подземелья, а потом возвращайся."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⛔ You're in a dungeon right now — no mine.\nLeave the dungeon and come back."`
- ✏️ НОВЫЙ EN:


### mine.item_lost

- ТЕКУЩИЙ RU: `"{head}\n\n🔨 Что-то добыл, но предмет потерялся. Сообщи хранителю."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"{head}\n\n🔨 You dug something up, but the item got lost. Tell the keeper."`
- ✏️ НОВЫЙ EN:


### mine.l2.broadcast

- ТЕКУЩИЙ RU: `"📡 Приказ командира эскадрильи\n\nВыработка в шахтах достигла {target} единиц руды. Открыт второй уровень шахт!\nСпуск — в меню копи."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"📡 Squadron commander's order\n\nMine output has reached {target} ore units. The second mine level is open!\nDescend from the mine menu."`
- ✏️ НОВЫЙ EN:


### mine.l2.chat

- ТЕКУЩИЙ RU: `"⛏ В шахтах вскрыт второй уровень: выработка достигла {target} единиц руды."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⛏ The second mine level is open: output has reached {target} ore units."`
- ✏️ НОВЫЙ EN:


### mine.level.dig_hint

- ТЕКУЩИЙ RU: `"Бей породу — авось блеснёт руда. А может, что и пострашнее."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Strike the rock — maybe ore will glint. Or something worse."`
- ✏️ НОВЫЙ EN:


### mine.level.no_pickaxe_hint

- ТЕКУЩИЙ RU: `"Без кирки в штольню не сунешься: сначала разживись киркой."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"You can't go down without a pickaxe: get one first."`
- ✏️ НОВЫЙ EN:


### mine.level.pickaxe_has

- ТЕКУЩИЙ RU: `"⛏ Кирка: {name} (ступень {rank}, шанс добычи {chance}%)"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⛏ Pickaxe: {name} (tier {rank}, mining chance {chance}%)"`
- ✏️ НОВЫЙ EN:


### mine.level.pickaxe_none

- ТЕКУЩИЙ RU: `"⛏ Кирка: нет — купи «Кирка» (магазин → Добыча ресурсов)"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⛏ Pickaxe: none — buy one (Shop → Resource Mining)"`
- ✏️ НОВЫЙ EN:


### mine.level.screen

- ТЕКУЩИЙ RU: `"⛏ УРОВЕНЬ 1 ШАХТ\n\nКрепь из подгнивших балок уходит вглубь, под ногами хрустит щебень, фонарь выхватывает жилы руды в тёмной породе.\n\n{pickaxe_line}\n{dig_line}\n\nУдар киркой стоит {cost} ОД, результат через {lo}–{hi} секунд.\n\n{ap_line}"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⛏ MINE LEVEL 1\n\nRotten beams run deep into the dark, gravel crunches underfoot, the lamp catches veins of ore in the black rock.\n\n{pickaxe_line}\n{dig_line}\n\nA pickaxe strike costs {cost} AP, result in {lo}–{hi} seconds.\n\n{ap_line}"`
- ✏️ НОВЫЙ EN:


### mine.no_ap

- ТЕКУЩИЙ RU: `"❌ Не хватает ОД: нужно {cost}, доступно меньше. Восстановление — в новые сутки."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ Not enough AP: you need {cost}. AP comes back with the new day."`
- ✏️ НОВЫЙ EN:


### mine.no_pickaxe

- ТЕКУЩИЙ RU: `"❌ У тебя нет кирки. Купи «Кирка» в магазине (категория «Добыча ресурсов»)."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ You have no pickaxe. Buy one in the shop (Resource Mining category)."`
- ✏️ НОВЫЙ EN:


### mine.ore_found

- ТЕКУЩИЙ RU: `"{head}\n\nКирка звонко высекает искру — из породы выкалывается кусок руды!\n\n🎒 Добыча: «{name}» — в инвентарь.{sell_line}"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"{head}\n\nThe pick strikes a spark — a lump of ore breaks out of the rock!\n\n🎒 Loot: «{name}» — added to your inventory.{sell_line}"`
- ✏️ НОВЫЙ EN:


### mine.progress

- ТЕКУЩИЙ RU: `"⛏ Выработка шахт: {cur} / {target} ед. руды (второй уровень откроется при {target})"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⛏ Mine output: {cur} / {target} ore (the second level opens at {target})"`
- ✏️ НОВЫЙ EN:


### mine.stale

- ТЕКУЩИЙ RU: `"⏳ Это окно копи устарело — открой её заново (Город → Железная копи)."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⏳ This mine window is out of date — reopen it (City → Iron Mine)."`
- ✏️ НОВЫЙ EN:


### mine.swing

- ТЕКУЩИЙ RU: `"⛏ Ты замахиваешься киркой и бьёшь по породе...\nРезультат через {delay} секунд. Не шуми — прислушивайся!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⛏ You swing your pickaxe at the rock...\nResult in {delay} seconds. Keep quiet — listen!"`
- ✏️ НОВЫЙ EN:


### mine.tourist

- ТЕКУЩИЙ RU: `"⛔ В копи не пускают туристов — вход только с «Пилота 1 класса»."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⛔ Tourists aren't allowed in the mine — entry is for Pilots 1st class only."`
- ✏️ НОВЫЙ EN:


### mollusk.alert.not_here

- ТЕКУЩИЙ RU: `"❌ Ты больше не в водохранилище."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ You're no longer in the reservoir."`
- ✏️ НОВЫЙ EN:


### mollusk.alert.stale

- ТЕКУЩИЙ RU: `"⏳ Это окно устарело."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⏳ This window is out of date."`
- ✏️ НОВЫЙ EN:


### mollusk.btn.flee

- ТЕКУЩИЙ RU: `"🏃 Сбежать"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🏃 Run away"`
- ✏️ НОВЫЙ EN:


### mollusk.btn.hit

- ТЕКУЩИЙ RU: `"⚔️ Ударить"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⚔️ Strike"`
- ✏️ НОВЫЙ EN:


### mollusk.counter.armor

- ТЕКУЩИЙ RU: `"🛡️ Броня поглотила {amount}. "`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🛡️ Armor absorbed {amount}. "`
- ✏️ НОВЫЙ EN:


### mollusk.counter.dodged

- ТЕКУЩИЙ RU: `"💨 Ты уклонился от щупальца! (−0 HP)\n\n"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"💨 You dodge the tentacle! (−0 HP)\n\n"`
- ✏️ НОВЫЙ EN:


### mollusk.counter.hit

- ТЕКУЩИЙ RU: `"Молюск впивается щупальцем: −{dmg} HP. {extra}\n\n"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"The mollusk clamps on with a tentacle: −{dmg} HP. {extra}\n\n"`
- ✏️ НОВЫЙ EN:


### mollusk.default_name

- ТЕКУЩИЙ RU: `"Мутировавший моллюск"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Mutated mollusk"`
- ✏️ НОВЫЙ EN:


### mollusk.default_short

- ТЕКУЩИЙ RU: `"Моллюск"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Mollusk"`
- ✏️ НОВЫЙ EN:


### mollusk.defeat.counter

- ТЕКУЩИЙ RU: `"🦪 БОЙ С МОЛЮСКОМ\n\n{pre}{counter}Ты срываешься с крючка.\n\nПока ты выбирался из воды, снасть потерялась. Плата за бессмысленный риск: −{removed} ОД."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🦪 FIGHT WITH THE MOLLUSK\n\n{pre}{counter}You slip off the hook.\n\nWhile you climbed out of the water, the tackle was lost. The price of a pointless risk: −{removed} AP."`
- ✏️ НОВЫЙ EN:


### mollusk.defeat.dot

- ТЕКУЩИЙ RU: `"🦪 БОЙ С МОЛЮСКОМ\n\n{dot}Ты срываешься с крючка.\n\nПока ты выбирался из воды, снасть потерялась. Плата за бессмысленный риск: −{removed} ОД."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🦪 FIGHT WITH THE MOLLUSK\n\n{dot}You slip off the hook.\n\nWhile you climbed out of the water, the tackle was lost. The price of a pointless risk: −{removed} AP."`
- ✏️ НОВЫЙ EN:


### mollusk.fled

- ТЕКУЩИЙ RU: `"🎣 РЫБАЛКА\n\n🏃 Ты выдернул снасть и отчалил от раковины. Моллюск остался на дне — и немного обиделся."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🎣 FISHING\n\n🏃 You yanked the line and pulled away from the shell. The mollusk stayed on the bottom — and is a bit offended."`
- ✏️ НОВЫЙ EN:


### mollusk.hit.armor

- ТЕКУЩИЙ RU: `"🛡️ Панцирь поглотил {amount}. "`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🛡️ The shell absorbed {amount}. "`
- ✏️ НОВЫЙ EN:


### mollusk.hit.crit

- ТЕКУЩИЙ RU: `"💥 crit! "`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"💥 crit! "`
- ✏️ НОВЫЙ EN:


### mollusk.hit.hit

- ТЕКУЩИЙ RU: `"Ты сжимаешь раковину: −{dmg} HP по моллюску! {extra}\n\n"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"You squeeze the shell: −{dmg} HP to the mollusk! {extra}\n\n"`
- ✏️ НОВЫЙ EN:


### mollusk.hit.miss

- ТЕКУЩИЙ RU: `"Ты ударил по панцирю — раковина скользнула, моллюск ушёл в глубину.\n\n"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"You hit the shell — it slides off, and the mollusk sinks into the depths.\n\n"`
- ✏️ НОВЫЙ EN:


### mollusk.loot.empty

- ТЕКУЩИЙ RU: `"Добыча не досталась: моллюск оказался пустым."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"No loot: the mollusk turned out empty."`
- ✏️ НОВЫЙ EN:


### mollusk.loot.got

- ТЕКУЩИЙ RU: `"Из раковины ты вытащил:\n{items}\n\nВсё в инвентаре.{rare}"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"From the shell you pulled out:\n{items}\n\nAll in your inventory.{rare}"`
- ✏️ НОВЫЙ EN:


### mollusk.loot.lost

- ТЕКУЩИЙ RU: `"Добыча потерялась — предмет не найден. Сообщи хранителю."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"The loot got lost — item not found. Tell the keeper."`
- ✏️ НОВЫЙ EN:


### mollusk.loot.rare

- ТЕКУЩИЙ RU: `"\n\n✨ Редчайшая находка!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"\n\n✨ A rarest find!"`
- ✏️ НОВЫЙ EN:


### mollusk.loot.sell

- ТЕКУЩИЙ RU: `" — продать за {price} {money}"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `" — sells for {price} {money}"`
- ✏️ НОВЫЙ EN:


### mollusk.screen

- ТЕКУЩИЙ RU: `"{prefix}🦪 {name_up}\n\nВместо рыбы на крючке — раковина. Она вся в бугорках, панцирь хрустит от напряжения — и моллюск бросается на снасть!\n\n🦪 {name}  HP {ebar}\n🧑 Ты          HP {pbar}{effects}\n\nХод {round}. Ударь моллюска или сними снасть."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"{prefix}🦪 {name_up}\n\nInstead of a fish there's a shell on the hook. It's all bumps, its plates crack under strain — and the mollusk lunges at your line!\n\n🦪 {name}  HP {ebar}\n🧑 You         HP {pbar}{effects}\n\nTurn {round}. Strike the mollusk or cut the line."`
- ✏️ НОВЫЙ EN:


### mollusk.win

- ТЕКУЩИЙ RU: `"🦪 БОЙ С МОЛЮСКОМ\n\n{pre}Панцирь хрустнул и раскрылся — в тёмной воде осталось только сияние.\n\n{loot}"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🦪 FIGHT WITH THE MOLLUSK\n\n{pre}The shell cracks open — only a glow is left in the dark water.\n\n{loot}"`
- ✏️ НОВЫЙ EN:


### notify.award

- ТЕКУЩИЙ RU: `"🎖️ {who} награждён: {title}"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🎖️ {who} has been awarded: {title}"`
- ✏️ НОВЫЙ EN:


### notify.award.untitled

- ТЕКУЩИЙ RU: `"награда"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"award"`
- ✏️ НОВЫЙ EN:


### notify.praise.ace

- ТЕКУЩИЙ RU: `"🏆 {who} проявляет характер истинного Аса!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🏆 {who} shows the spirit of a true Ace!"`
- ✏️ НОВЫЙ EN:


### notify.praise.mastery

- ТЕКУЩИЙ RU: `"⚡ {who} показал высокое мастерство!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⚡ {who} showed high mastery!"`
- ✏️ НОВЫЙ EN:


### notify.rank

- ТЕКУЩИЙ RU: `"⭐ Пилот {who} получил звание «{rank}»!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⭐ Pilot {who} earned the rank «{rank}»!"`
- ✏️ НОВЫЙ EN:


### notify.speech.head

- ТЕКУЩИЙ RU: `"📢 РЕЧЬ ПРЕДСТАВИТЕЛЯ"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"📢 REPRESENTATIVE'S SPEECH"`
- ✏️ НОВЫЙ EN:


### notify.treasury.debtor

- ТЕКУЩИЙ RU: `"  • {name}: {amt} НМ"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"  • {name}: {amt} NM"`
- ✏️ НОВЫЙ EN:


### notify.treasury.head

- ТЕКУЩИЙ RU: `"⚠️ НЕХВАТКА КАЗНЫ НА ЗАРПЛАТЫ\nНе хватило суммарно: {total} НМ\nЗадолженность копится и будет выплачена, когда появятся средства.\n\nДолжники:"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⚠️ TREASURY SHORTFALL FOR SALARIES\nShort by a total of {total} NM\nThe debt accumulates and will be paid when funds appear.\n\nDebtors:"`
- ✏️ НОВЫЙ EN:


### notify.treasury.more

- ТЕКУЩИЙ RU: `"  … и ещё {n} пилотов"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"  … and {n} more pilots"`
- ✏️ НОВЫЙ EN:


### pers.clan.disbanded

- ТЕКУЩИЙ RU: `"🗑 {kind} «{name}» распущено — ты больше не глава."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🗑 The {kind} «{name}» has been disbanded — you're no longer its head."`
- ✏️ НОВЫЙ EN:


### pers.clan.leader_removed

- ТЕКУЩИЙ RU: `"👑 Ты больше не глава {kind} «{name}» — руководство передано другому пилоту."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"👑 You're no longer head of the {kind} «{name}» — leadership passed to another pilot."`
- ✏️ НОВЫЙ EN:


### pers.clan.leader_set

- ТЕКУЩИЙ RU: `"👑 Тебя назначили главой {kind} «{name}»."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"👑 You've been appointed head of the {kind} «{name}»."`
- ✏️ НОВЫЙ EN:


### pers.clan.leader_unset

- ТЕКУЩИЙ RU: `"👑 С тебя снята должность главы {kind} «{name}»."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"👑 You've been removed as head of the {kind} «{name}»."`
- ✏️ НОВЫЙ EN:


### pers.duty.add

- ТЕКУЩИЙ RU: `"🎖 Тебе присвоена должность: «{label}»."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🎖 You've been given the post: «{label}»."`
- ✏️ НОВЫЙ EN:


### pers.duty.remove

- ТЕКУЩИЙ RU: `"🎖 С тебя снята должность: «{label}»."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🎖 You've been removed from the post: «{label}»."`
- ✏️ НОВЫЙ EN:


### pers.legion.off

- ТЕКУЩИЙ RU: `"🦅 С тебя снят статус легионера."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🦅 Your legionnaire status has been removed."`
- ✏️ НОВЫЙ EN:


### pers.legion.on

- ТЕКУЩИЙ RU: `"🦅 Тебе присвоен статус легионера."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🦅 You've been granted legionnaire status."`
- ✏️ НОВЫЙ EN:


### pers.status.grant

- ТЕКУЩИЙ RU: `"🎖 Тебе присвоен статус «{name}»."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🎖 You've been granted the status «{name}»."`
- ✏️ НОВЫЙ EN:


### pers.wing.commander_removed

- ТЕКУЩИЙ RU: `"🎖 Ты больше не командир {wing} — назначен другой пилот."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🎖 You're no longer commander of {wing} — another pilot was appointed."`
- ✏️ НОВЫЙ EN:


### pers.wing.commander_set

- ТЕКУЩИЙ RU: `"🎖 Ты назначен командиром {wing}."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🎖 You've been appointed commander of {wing}."`
- ✏️ НОВЫЙ EN:


### pers.wing.commander_unset

- ТЕКУЩИЙ RU: `"🎖 С тебя снята должность командира {wing}."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🎖 You've been removed as commander of {wing}."`
- ✏️ НОВЫЙ EN:


### pers.wing.deputy_removed

- ТЕКУЩИЙ RU: `"🎖 Ты больше не заместитель командира {wing}."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🎖 You're no longer deputy commander of {wing}."`
- ✏️ НОВЫЙ EN:


### pers.wing.deputy_set

- ТЕКУЩИЙ RU: `"🎖 Ты назначен заместителем командира {wing}."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🎖 You've been appointed deputy commander of {wing}."`
- ✏️ НОВЫЙ EN:


### pers.wing.deputy_unset

- ТЕКУЩИЙ RU: `"🎖 С тебя снята должность заместителя командира {wing}."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🎖 You've been removed as deputy commander of {wing}."`
- ✏️ НОВЫЙ EN:


### profile.about

- ТЕКУЩИЙ RU: `"📖 О себе"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"📖 About me"`
- ✏️ НОВЫЙ EN:


### profile.achievements

- ТЕКУЩИЙ RU: `"🏅 Достижения"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🏅 Achievements"`
- ✏️ НОВЫЙ EN:


### profile.awards

- ТЕКУЩИЙ RU: `"🎖️ Награды"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🎖️ Awards"`
- ✏️ НОВЫЙ EN:


### profile.back

- ТЕКУЩИЙ RU: `"🏠 В профиль"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🏠 Back to profile"`
- ✏️ НОВЫЙ EN:


### profile.choose_status

- ТЕКУЩИЙ RU: `"Выбрать статус"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Choose status"`
- ✏️ НОВЫЙ EN:


### profile.passport

- ТЕКУЩИЙ RU: `"🛂 Паспорт: серия {series} № {number}"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🛂 Passport: series {series} No. {number}"`
- ✏️ НОВЫЙ EN:


### profile.passport_none

- ТЕКУЩИЙ RU: `"🛂 Паспорт: не выдан"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🛂 Passport: not issued"`
- ✏️ НОВЫЙ EN:


### profile.pilot_card

- ТЕКУЩИЙ RU: `"Карточка пилота"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Pilot card"`
- ✏️ НОВЫЙ EN:


### profile.recipes

- ТЕКУЩИЙ RU: `"📜 Выученные рецепты"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"📜 Learned recipes"`
- ✏️ НОВЫЙ EN:


### profile.set_photo

- ТЕКУЩИЙ RU: `"Изменить фото"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Change photo"`
- ✏️ НОВЫЙ EN:


### rarity.1

- ТЕКУЩИЙ RU: `"Обычный"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Common"`
- ✏️ НОВЫЙ EN:


### rarity.2

- ТЕКУЩИЙ RU: `"Качественный"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Quality"`
- ✏️ НОВЫЙ EN:


### rarity.3

- ТЕКУЩИЙ RU: `"Редкий"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Rare"`
- ✏️ НОВЫЙ EN:


### rarity.4

- ТЕКУЩИЙ RU: `"Шедевр"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Masterpiece"`
- ✏️ НОВЫЙ EN:


### rarity.5

- ТЕКУЩИЙ RU: `"Легендарный"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Legendary"`
- ✏️ НОВЫЙ EN:


### recipes.back

- ТЕКУЩИЙ RU: `"🔙 К рецептам"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🔙 Back to recipes"`
- ✏️ НОВЫЙ EN:


### recipes.card_ingredients

- ТЕКУЩИЙ RU: `"Ингредиенты:"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Ingredients:"`
- ✏️ НОВЫЙ EN:


### recipes.card_meta

- ТЕКУЩИЙ RU: `"ОД: {ap} · время: ~{time} сек · {station}, ур. {level}"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"AP: {ap} · time: ~{time} s · {station}, lvl {level}"`
- ✏️ НОВЫЙ EN:


### recipes.card_no_ingredients

- ТЕКУЩИЙ RU: `"Ингредиентов нет."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"No ingredients."`
- ✏️ НОВЫЙ EN:


### recipes.card_station_kitchen

- ТЕКУЩИЙ RU: `"кухня"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"kitchen"`
- ✏️ НОВЫЙ EN:


### recipes.card_station_other

- ТЕКУЩИЙ RU: `"прочее"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"other"`
- ✏️ НОВЫЙ EN:


### recipes.card_station_workbench

- ТЕКУЩИЙ RU: `"верстак"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"workbench"`
- ✏️ НОВЫЙ EN:


### recipes.empty

- ТЕКУЩИЙ RU: `"Пока ни один рецепт не выучен."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"No recipes learned yet."`
- ✏️ НОВЫЙ EN:


### recipes.group_kitchen

- ТЕКУЩИЙ RU: `"🍳 Кухня"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🍳 Kitchen"`
- ✏️ НОВЫЙ EN:


### recipes.group_other

- ТЕКУЩИЙ RU: `"📦 Прочее"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"📦 Other"`
- ✏️ НОВЫЙ EN:


### recipes.group_workbench

- ТЕКУЩИЙ RU: `"🔨 Верстак"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🔨 Workbench"`
- ✏️ НОВЫЙ EN:


### recipes.list_level

- ТЕКУЩИЙ RU: `"ур. {lvl}"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"lvl {lvl}"`
- ✏️ НОВЫЙ EN:


### recipes.not_found

- ТЕКУЩИЙ RU: `"❌ Рецепт не найден."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ Recipe not found."`
- ✏️ НОВЫЙ EN:


### recipes.title

- ТЕКУЩИЙ RU: `"📜 ВЫУЧЕННЫЕ РЕЦЕПТЫ ({n}):"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"📜 LEARNED RECIPES ({n}):"`
- ✏️ НОВЫЙ EN:


### report.btn_my

- ТЕКУЩИЙ RU: `"Мои отчёты"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"My reports"`
- ✏️ НОВЫЙ EN:


### report.btn_submit

- ТЕКУЩИЙ RU: `"Сдать отчёт"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Submit report"`
- ✏️ НОВЫЙ EN:


### report.card_reject_reason

- ТЕКУЩИЙ RU: `"📝 Причина отклонения: {reason}"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"📝 Rejection reason: {reason}"`
- ✏️ НОВЫЙ EN:


### report.card_reviewed_by

- ТЕКУЩИЙ RU: `"👮 Проверил: {name}"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"👮 Reviewed by: {name}"`
- ✏️ НОВЫЙ EN:


### report.daily_prompt

- ТЕКУЩИЙ RU: `"✍️ Сколько войск ты заработал за СЕГОДНЯШНИЕ сутки?\nТолько то, что набежало сегодня — НЕ всё накопленное за все дни.\n(цифрами, до {max})\n\nℹ️ За сутки считается накопленное с 10:00 до 10:00. Если сдашь несколько отчётов, платят по ПОСЛЕДНЕМУ — отчёты не складываются. Поэтому сдавай отчёт по мере накопления, а не один раз в конце."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"✍️ How many troops did you gain TODAY?\nOnly what accumulated today — NOT everything from all days.\n(in digits, up to {max})\n\nℹ️ A game day counts troops from 10:00 to 10:00. If you submit several reports, only the LAST one is paid — reports don't add up. So submit as you accumulate, not once at the end."`
- ✏️ НОВЫЙ EN:


### report.limit

- ТЕКУЩИЙ RU: `"⚠️ Лимит отчётов на сегодня исчерпан (3 из 3)."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⚠️ Daily report limit reached (3 of 3)."`
- ✏️ НОВЫЙ EN:


### report.menu_header

- ТЕКУЩИЙ RU: `"📋 Меню отчётов"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"📋 Report menu"`
- ✏️ НОВЫЙ EN:


### report.photo_prompt

- ТЕКУЩИЙ RU: `"📸 Прикрепи скриншот карты братства, где видно твой текущий регион с твоим общим кол-вом войск, твой ник и суточное накопление войск.\nОтправь фото одним сообщением.\n\nОсталось отчётов на сегодня: {remaining}"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"📸 Attach a screenshot of the brotherhood map showing your current region, your total troops, your nickname and your daily troop gain.\nSend the photo as one message.\n\nReports left today: {remaining}"`
- ✏️ НОВЫЙ EN:


### report.prev_day

- ТЕКУЩИЙ RU: `"🗓 За прошлые сутки ты сдал: {n}."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🗓 Last game day you submitted: {n}."`
- ✏️ НОВЫЙ EN:


### report.reject_ask

- ТЕКУЩИЙ RU: `"❌ ОТКЛОНЕНИЕ ОТЧЁТА #{id}\n\nНапиши причину отклонения: её увидит пилот в карточке отчёта и в личном сообщении. Причина обязательна.\nОтмена — вернуться к очереди."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ REJECTING REPORT #{id}\n\nWrite the reason for rejection: the pilot will see it in the report card and in a private message. The reason is required.\nCancel to go back to the queue."`
- ✏️ НОВЫЙ EN:


### report.reject_dm

- ТЕКУЩИЙ RU: `"❌ ТВОЙ ОТЧЁТ ОТКЛОНЁН\n\nОтчёт #{id} отклонён при проверке.\n📝 Причина: {reason}\n👮 Проверил: {name}\n\nЕсли считаешь отклонение ошибкой — напиши в МВД."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ YOUR REPORT WAS REJECTED\n\nReport #{id} was rejected during review.\n📝 Reason: {reason}\n👮 Reviewed by: {name}\n\nIf you think this was a mistake, contact the Interior Ministry."`
- ✏️ НОВЫЙ EN:


### report.reject_done

- ТЕКУЩИЙ RU: `"❌ Отчёт #{id} отклонён.\n📝 Причина: {reason}\n👮 Проверил: {name}"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ Report #{id} rejected.\n📝 Reason: {reason}\n👮 Reviewed by: {name}"`
- ✏️ НОВЫЙ EN:


### report.reject_reason_required

- ТЕКУЩИЙ RU: `"❌ Причину отклонения нельзя оставить пустой. Напиши её текстом:"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ The rejection reason cannot be empty. Write it as text:"`
- ✏️ НОВЫЙ EN:


### report.reject_reason_short

- ТЕКУЩИЙ RU: `"❌ Слишком коротко. Опиши причину хотя бы в {min} символов:"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ Too short. Describe the reason in at least {min} characters:"`
- ✏️ НОВЫЙ EN:


### report.rejected_back_btn

- ТЕКУЩИЙ RU: `"🔙 К отклонённым"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🔙 Back to rejected"`
- ✏️ НОВЫЙ EN:


### report.rejected_back_reports

- ТЕКУЩИЙ RU: `"🔙 К отчётам"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🔙 Back to reports"`
- ✏️ НОВЫЙ EN:


### report.rejected_delete_ask

- ТЕКУЩИЙ RU: `"🗑 УДАЛИТЬ ОТЧЁТ #{id}?\n\nЗапись исчезнет из БД: её не будет ни в списке отклонённых, ни в «Моих отчётах» пилота. Действие необратимо."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🗑 DELETE REPORT #{id}?\n\nThe record will be removed from the database: it disappears from the rejected list and from the pilot's «My reports». This cannot be undone."`
- ✏️ НОВЫЙ EN:


### report.rejected_delete_btn

- ТЕКУЩИЙ RU: `"🗑 Удалить из списка"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🗑 Remove from list"`
- ✏️ НОВЫЙ EN:


### report.rejected_delete_cancel

- ТЕКУЩИЙ RU: `"🔙 Отмена"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🔙 Cancel"`
- ✏️ НОВЫЙ EN:


### report.rejected_delete_done

- ТЕКУЩИЙ RU: `"🗑 Отчёт #{id} удалён из списка отклонённых."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🗑 Report #{id} removed from the rejected list."`
- ✏️ НОВЫЙ EN:


### report.rejected_delete_missing

- ТЕКУЩИЙ RU: `"❌ Отчёт #{id} не найден среди отклонённых (возможно, уже удалён)."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ Report #{id} is not among rejected ones (maybe already deleted)."`
- ✏️ НОВЫЙ EN:


### report.rejected_delete_super_only

- ТЕКУЩИЙ RU: `"❌ Удалять отклонённые отчёты может только супер-админ."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ Only a super admin can delete rejected reports."`
- ✏️ НОВЫЙ EN:


### report.rejected_delete_yes

- ТЕКУЩИЙ RU: `"✅ Да, удалить"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"✅ Yes, delete"`
- ✏️ НОВЫЙ EN:


### report.rejected_details

- ТЕКУЩИЙ RU: `"\n🗑 Отклонён: {when}"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"\n🗑 Rejected: {when}"`
- ✏️ НОВЫЙ EN:


### report.rejected_line

- ТЕКУЩИЙ RU: `"#{id} · {author} · {troops} ⚔️ · регион {region} · {when}\n   👮 {reviewer} · 📝 {reason}"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"#{id} · {author} · {troops} ⚔️ · region {region} · {when}\n   👮 {reviewer} · 📝 {reason}"`
- ✏️ НОВЫЙ EN:


### report.rejected_menu_btn

- ТЕКУЩИЙ RU: `"❌ Отклонённые отчёты · {n}"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ Rejected reports · {n}"`
- ✏️ НОВЫЙ EN:


### report.rejected_menu_line

- ТЕКУЩИЙ RU: `"• ❌ Отклонённые ({days} дн.): {n}"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"• ❌ Rejected (last {days} days): {n}"`
- ✏️ НОВЫЙ EN:


### report.rejected_none

- ТЕКУЩИЙ RU: `"\nЗа последние {days} дней отклонённых отчётов нет."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"\nNo rejected reports in the last {days} days."`
- ✏️ НОВЫЙ EN:


### report.rejected_page

- ТЕКУЩИЙ RU: `"Страница {page} из {total}"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Page {page} of {total}"`
- ✏️ НОВЫЙ EN:


### report.rejected_title

- ТЕКУЩИЙ RU: `"❌ ОТКЛОНЁННЫЕ ОТЧЁТЫ\n\nПоказаны только отчёты, отклонённые за последние {days} дней. Старые записи из списка уходят сами.\n"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ REJECTED REPORTS\n\nOnly reports rejected within the last {days} days are shown. Older entries leave the list automatically.\n"`
- ✏️ НОВЫЙ EN:


### report.rejected_view_btn

- ТЕКУЩИЙ RU: `"🔍 Отчёт #{id}"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🔍 Report #{id}"`
- ✏️ НОВЫЙ EN:


### report.remaining

- ТЕКУЩИЙ RU: `"Осталось отчётов сегодня: {n}"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Reports left today: {n}"`
- ✏️ НОВЫЙ EN:


### report.reviewer_system

- ТЕКУЩИЙ RU: `"автоматически (система)"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"automatically (system)"`
- ✏️ НОВЫЙ EN:


### report.reviewer_unknown

- ТЕКУЩИЙ RU: `"—"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"—"`
- ✏️ НОВЫЙ EN:


### report.start

- ТЕКУЩИЙ RU: `"📝 Сдать отчёт"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"📝 Submit report"`
- ✏️ НОВЫЙ EN:


### report.total_note

- ТЕКУЩИЙ RU: `"\n\nЭто число нужно для статистики сил по регионам — на оплату оно не влияет."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"\n\nThis number is for regional troop statistics — it does not affect payment."`
- ✏️ НОВЫЙ EN:


### report.total_prompt

- ТЕКУЩИЙ RU: `"🗺 Сколько у тебя сейчас войск на карте в регионе? (цифрами, до {max})"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🗺 How many troops do you have on the map in your region now? (in digits, up to {max})"`
- ✏️ НОВЫЙ EN:


### restock.ask_target

- ТЕКУЩИЙ RU: `"🔢 Сколько штук «{name}» выкладывать каждую неделю?\nВведи число от 1 до 100000. Включение выкладки включит и её."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🔢 How many «{name}» to restock every week?\nEnter a number from 1 to 100000. Setting it also turns restock on."`
- ✏️ НОВЫЙ EN:


### restock.back

- ТЕКУЩИЙ RU: `"🔙 К товару"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🔙 Back to item"`
- ✏️ НОВЫЙ EN:


### restock.bad_target

- ТЕКУЩИЙ RU: `"❌ Введи целое число от 1 до 100000."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ Enter a whole number from 1 to 100000."`
- ✏️ НОВЫЙ EN:


### restock.btn

- ТЕКУЩИЙ RU: `"🔁 Авто-выкладка раз в неделю"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🔁 Weekly auto-restock"`
- ✏️ НОВЫЙ EN:


### restock.saved

- ТЕКУЩИЙ RU: `"✅ «{name}»: авто-выкладка включена, до {n} шт. в неделю."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"✅ «{name}»: weekly auto-restock is on, up to {n} per week."`
- ✏️ НОВЫЙ EN:


### restock.screen

- ТЕКУЩИЙ RU: `"🔁 АВТО-ВЫКЛАДКА «{name}»\n\nРаз в неделю (первый суточный цикл недели, понедельник 10:00 МСК) остаток доводится до заданного числа. Если остаток выше — не трогаем. Безлимит не выкладываем.\n\nСейчас: {state}\nОстаток на складе: {stock}"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🔁 AUTO-RESTOCK «{name}»\n\nOnce a week (the first daily cycle of the week, Monday 10:00 MSK) the stock is topped up to the set number. If stock is already higher, nothing changes. Unlimited items are not restocked.\n\nNow: {state}\nStock on hand: {stock}"`
- ✏️ НОВЫЙ EN:


### restock.set_target

- ТЕКУЩИЙ RU: `"🔢 Сколько выкладывать"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🔢 Set weekly amount"`
- ✏️ НОВЫЙ EN:


### restock.state_off

- ТЕКУЩИЙ RU: `"выключена"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"off"`
- ✏️ НОВЫЙ EN:


### restock.state_on

- ТЕКУЩИЙ RU: `"включена, до {n} шт. в неделю"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"on, up to {n} per week"`
- ✏️ НОВЫЙ EN:


### restock.toggle_off

- ТЕКУЩИЙ RU: `"⏸ Выключить"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⏸ Turn off"`
- ✏️ НОВЫЙ EN:


### restock.toggle_on

- ТЕКУЩИЙ RU: `"✅ Включить"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"✅ Turn on"`
- ✏️ НОВЫЙ EN:


### restock.unlimited

- ТЕКУЩИЙ RU: `"ℹ️ Безлимитный или лут-товар — авто-выкладка не нужна."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"ℹ️ Unlimited or loot-only item — auto-restock is not needed."`
- ✏️ НОВЫЙ EN:


### resv.alert.busy

- ТЕКУЩИЙ RU: `"🎣 Ты уже ждёшь улов — дождись результата!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🎣 You're already waiting for a catch — wait for the result!"`
- ✏️ НОВЫЙ EN:


### resv.alert.pending

- ТЕКУЩИЙ RU: `"🎣 Результат ещё в пути — подожди пару секунд."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🎣 The result is still on its way — wait a couple of seconds."`
- ✏️ НОВЫЙ EN:


### resv.alert.stale_btn

- ТЕКУЩИЙ RU: `"⚠️ Это устаревшая кнопка."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⚠️ This button is out of date."`
- ✏️ НОВЫЙ EN:


### resv.alert.wait

- ТЕКУЩИЙ RU: `"⏳ Сначала дождись улова из водохранилища!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⏳ Wait for your catch from the reservoir first!"`
- ✏️ НОВЫЙ EN:


### resv.ap

- ТЕКУЩИЙ RU: `"\n⚡ ОД: {ap}/{ap_max}"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"\n⚡ AP: {ap}/{ap_max}"`
- ✏️ НОВЫЙ EN:


### resv.ap_next_ok

- ТЕКУЩИЙ RU: `" — можно забрасывать"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `" — you can cast again"`
- ✏️ НОВЫЙ EN:


### resv.ap_next_short

- ТЕКУЩИЙ RU: `" — на следующий заброс не хватит ({cost} ОД)"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `" — not enough for the next cast ({cost} AP)"`
- ✏️ НОВЫЙ EN:


### resv.ap_short

- ТЕКУЩИЙ RU: `" — не хватит на заброс ({cost} ОД)"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `" — not enough for a cast ({cost} AP)"`
- ✏️ НОВЫЙ EN:


### resv.bait.auto_plain

- ТЕКУЩИЙ RU: `"Авто (что есть)"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Auto (whatever you have)"`
- ✏️ НОВЫЙ EN:


### resv.bait.none

- ТЕКУЩИЙ RU: `"🚫 Без наживки"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🚫 No bait"`
- ✏️ НОВЫЙ EN:


### resv.bait.none_plain

- ТЕКУЩИЙ RU: `"Без наживки"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"No bait"`
- ✏️ НОВЫЙ EN:


### resv.bait.screen

- ТЕКУЩИЙ RU: `"🪱 НАЖИВКА (ВОДОХРАНИЛИЩЕ)\n\nСейчас: {selected}\nНаживка расходуется при каждом забросе.\n«Авто»: сначала черви, затем лапка, затем комбинированная.\n\n⚠️ Без наживки рыба не клюёт: со дна только мусор {junk}."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🪱 BAIT (RESERVOIR)\n\nNow: {selected}\nBait is used up with every cast.\n«Auto»: worms first, then spider leg, then combined bait.\n\n⚠️ Without bait the fish won't bite: the bottom only gives junk {junk}."`
- ✏️ НОВЫЙ EN:


### resv.bait.with

- ТЕКУЩИЙ RU: `" с наживкой «{name}»"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `" with bait «{name}»"`
- ✏️ НОВЫЙ EN:


### resv.bait.without

- ТЕКУЩИЙ RU: `" без наживки"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `" without bait"`
- ✏️ НОВЫЙ EN:


### resv.btn.again

- ТЕКУЩИЙ RU: `"🎣 Ещё раз"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🎣 Again"`
- ✏️ НОВЫЙ EN:


### resv.btn.back_resv

- ТЕКУЩИЙ RU: `"🔙 В водохранилище"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🔙 Back to the reservoir"`
- ✏️ НОВЫЙ EN:


### resv.btn.bait

- ТЕКУЩИЙ RU: `"🪱 Наживка"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🪱 Bait"`
- ✏️ НОВЫЙ EN:


### resv.btn.cast

- ТЕКУЩИЙ RU: `"🎣 Забросить удочку (−{ap} ОД)"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🎣 Cast the rod (−{ap} AP)"`
- ✏️ НОВЫЙ EN:


### resv.btn.deeper

- ТЕКУЩИЙ RU: `"⚔️ Продолжить вглубь (Этаж 2)"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⚔️ Go deeper (Floor 2)"`
- ✏️ НОВЫЙ EN:


### resv.btn.exit

- ТЕКУЩИЙ RU: `"🚪 Выйти из подземелья"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🚪 Leave the dungeon"`
- ✏️ НОВЫЙ EN:


### resv.btn.fish_here

- ТЕКУЩИЙ RU: `"🎣 Порыбачить в водохранилище"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🎣 Fish in the reservoir"`
- ✏️ НОВЫЙ EN:


### resv.btn.gear

- ТЕКУЩИЙ RU: `"🎒 Снаряжение"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🎒 Gear"`
- ✏️ НОВЫЙ EN:


### resv.btn.recover

- ТЕКУЩИЙ RU: `"🔄 Проверить крючок"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🔄 Check the hook"`
- ✏️ НОВЫЙ EN:


### resv.captain.loot

- ТЕКУЩИЙ RU: `"\n💰 В лут с 1-го этажа накоплено: {nm} НМ (заберёшь при выходе)."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"\n💰 Loot from floor 1 collected so far: {nm} NM (you'll take it on the way out)."`
- ✏️ НОВЫЙ EN:


### resv.captain.tail

- ТЕКУЩИЙ RU: `"\n\nМожно порыбачить, а потом продолжить путь на 2-й этаж."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"\n\nYou can fish first, then continue to floor 2."`
- ✏️ НОВЫЙ EN:


### resv.captain.text

- ТЕКУЩИЙ RU: `"🏆 КРЫСИНЫЙ КАПИТАН ПОВЕРЖЁН!\n💀 «Генерал» в кастрюлевом шлеме с жалким писком отползает в темноту, и на этаже становится тихо.\n\nВпереди развилка:\n🎣 Боковое ответвление ведёт к подземному водохранилищу — там слышен плеск невидимой рыбы. Говорят, в тёмной воде водится рыба, которой больше нигде нет.\n⚔️ Вниз уходит ход в сердце подвала, где ждёт сам Король крыс.\n"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🏆 THE RAT CAPTAIN IS DOWN!\n💀 The «General» in his pot helmet crawls into the dark with a pitiful squeal, and the floor goes quiet.\n\nAhead, a fork:\n🎣 A side branch leads to the underground reservoir — an unseen fish splashes there. They say the dark water holds a fish found nowhere else.\n⚔️ A passage leads down to the heart of the cellar, where the Rat King himself waits.\n"`
- ✏️ НОВЫЙ EN:


### resv.cast.lost

- ТЕКУЩИЙ RU: `"🌊 Вода в водохранилище снова гладкая…\n\nЗаброс прервался (подземелье закрылось или бот перезапускался). Вернись в водохранилище и попробуй снова."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🌊 The reservoir water is smooth again…\n\nThe cast was interrupted (the dungeon closed or the bot restarted). Return to the reservoir and try again."`
- ✏️ НОВЫЙ EN:


### resv.cast.wait

- ТЕКУЩИЙ RU: `"🎣 Ты забрасываешь удочку{bait} в тёмную воду подземного водохранилища...\nПоплавок замер неподвижно. Ждёшь..."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🎣 You cast your line{bait} into the dark water of the underground reservoir...\nThe float hangs still. You wait..."`
- ✏️ НОВЫЙ EN:


### resv.catch.catfish

- ТЕКУЩИЙ RU: `"\n🐟 Мерцающий сом. Обычный, но вкусный."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"\n🐟 A shimmering catfish. Common, but tasty."`
- ✏️ НОВЫЙ EN:


### resv.catch.eel

- ТЕКУЩИЙ RU: `"\n🐡 Искрящийся угорь! Редкий улов."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"\n🐡 A sparkling eel! A rare catch."`
- ✏️ НОВЫЙ EN:


### resv.catch.error

- ТЕКУЩИЙ RU: `"❌ Ошибка: рыба не определена."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ Error: fish not identified."`
- ✏️ НОВЫЙ EN:


### resv.catch.glow

- ТЕКУЩИЙ RU: `"\n✨ СВЕТЯЩАЯСЯ ФОРЕЛЬ! Секретный улов, о котором шепчутся в Нордхайме!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"\n✨ GLOWING TROUT! A secret catch the whispers in Nordheim talk about!"`
- ✏️ НОВЫЙ EN:


### resv.catch.head

- ТЕКУЩИЙ RU: `"\n\n🎒 Поймано тут (Улов):\n"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"\n\n🎒 Caught here (catch):\n"`
- ✏️ НОВЫЙ EN:


### resv.catch.hit

- ТЕКУЩИЙ RU: `"🎣 ПОКЛЁВКА!\n{emoji} Ты поймал: «{fish}» — {tier}!\n{name_line}\n\n🎒 Улов записан в «Улов» (Рыба). Раз в 4 дня сырая рыба портится.\nВес влияет на цену: продажа за {sell} {money}."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🎣 BITE!\n{emoji} You caught: «{fish}» — {tier}!\n{name_line}\n\n🎒 The catch is logged in «Catch» (Fish). Raw fish spoils every 4 days.\nWeight affects the price: sells for {sell} {money}."`
- ✏️ НОВЫЙ EN:


### resv.catch.miss

- ТЕКУЩИЙ RU: `"🎣 РЫБАЛКА\n\nПоплавок дёрнулся, ты подсекаешь... и вдруг пусто.\nСорвалось. Но рыба никуда не денется — пробуй ещё!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🎣 FISHING\n\nThe float jerks, you set the hook... and nothing.\nIt got away. But the fish aren't going anywhere — try again!"`
- ✏️ НОВЫЙ EN:


### resv.deeper.bottom

- ТЕКУЩИЙ RU: `"⚠️ Ты уже на самом нижнем этаже."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⚠️ You're already on the lowest floor."`
- ✏️ НОВЫЙ EN:


### resv.deeper.stairs

- ТЕКУЩИЙ RU: `"⬇️ Ты спускаешься по скрипучей лестнице во мрак. Здесь пахнет сыростью, плесенью и старой королевской гордостью.\n🏰 ЭТАЖ 2 | ЛОГОВО КОРОЛЯ КРЫС"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⬇️ You creep down a creaking staircase into the dark. It smells of damp, mould and old royal pride.\n🏰 FLOOR 2 | THE RAT KING'S LAIR"`
- ✏️ НОВЫЙ EN:


### resv.eq.back

- ТЕКУЩИЙ RU: `"🔙 К водохранилищу"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🔙 Back to the reservoir"`
- ✏️ НОВЫЙ EN:


### resv.eq.back_gear

- ТЕКУЩИЙ RU: `"🔙 К снаряжению"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🔙 Back to gear"`
- ✏️ НОВЫЙ EN:


### resv.eq.head

- ТЕКУЩИЙ RU: `"🎒 СНАРЯЖЕНИЕ (водохранилище)"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🎒 GEAR (reservoir)"`
- ✏️ НОВЫЙ EN:


### resv.eq.intro

- ТЕКУЩИЙ RU: `"Здесь нет врагов — можно спокойно сменить расходники в активных слотах."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"There are no enemies here — you can calmly swap consumables in your active slots."`
- ✏️ НОВЫЙ EN:


### resv.eq.slot1

- ТЕКУЩИЙ RU: `"🔄 Слот 1"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🔄 Slot 1"`
- ✏️ НОВЫЙ EN:


### resv.eq.slot2

- ТЕКУЩИЙ RU: `"🔄 Слот 2"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🔄 Slot 2"`
- ✏️ НОВЫЙ EN:


### resv.eqclear.done

- ТЕКУЩИЙ RU: `"✖️ {name} снят из активного слота."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"✖️ {name} removed from the active slot."`
- ✏️ НОВЫЙ EN:


### resv.eqclear.item

- ТЕКУЩИЙ RU: `"Предмет"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Item"`
- ✏️ НОВЫЙ EN:


### resv.eqset.done

- ТЕКУЩИЙ RU: `"⚗️ {name} поставлен в активный слот.\nИспользуется в бою подземелья кнопкой слота."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⚗️ {name} is in the active slot.\nUse it in dungeon fights with the slot button."`
- ✏️ НОВЫЙ EN:


### resv.eqset.no_item

- ТЕКУЩИЙ RU: `"❌ Предмет не найден."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ Item not found."`
- ✏️ НОВЫЙ EN:


### resv.eqslot.clear

- ТЕКУЩИЙ RU: `"✖️ Снять из слота"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"✖️ Remove from slot"`
- ✏️ НОВЫЙ EN:


### resv.eqslot.empty

- ТЕКУЩИЙ RU: `"Слот пуст.\n"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"The slot is empty.\n"`
- ✏️ НОВЫЙ EN:


### resv.eqslot.fits

- ТЕКУЩИЙ RU: `"\nПодходит из инвентаря:"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"\nFits from your inventory:"`
- ✏️ НОВЫЙ EN:


### resv.eqslot.head

- ТЕКУЩИЙ RU: `"🎒 СНАРЯЖЕНИЕ → {slot}\n\n"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🎒 GEAR → {slot}\n\n"`
- ✏️ НОВЫЙ EN:


### resv.eqslot.none

- ТЕКУЩИЙ RU: `"\nВ инвентаре нет подходящих расходников."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"\nNo suitable consumables in your inventory."`
- ✏️ НОВЫЙ EN:


### resv.eqslot.set

- ТЕКУЩИЙ RU: `"Поставлено: {name}\n"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Equipped: {name}\n"`
- ✏️ НОВЫЙ EN:


### resv.junk.hit

- ТЕКУЩИЙ RU: `"🎣 РЫБАЛКА\n\nПоплавок дёрнулся, ты подсекаешь...\nИз тёмной воды появляется: «{junk}»!\n\n🎒 Улов записан в «Улов».{sell_line}"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🎣 FISHING\n\nThe float jerks, you set the hook...\nFrom the dark water comes: «{junk}»!\n\n🎒 The catch is logged in «Catch».{sell_line}"`
- ✏️ НОВЫЙ EN:


### resv.junk.lost

- ТЕКУЩИЙ RU: `"🎣 Рыбалка\n\n👢 Что-то выловил, но предмет потерялся. Сообщи хранителю."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🎣 Fishing\n\n👢 You caught something, but the item got lost. Tell the keeper."`
- ✏️ НОВЫЙ EN:


### resv.junk.none

- ТЕКУЩИЙ RU: `"🎣 РЫБАЛКА\n\nПоплавок даже не дрогнул. Без наживки рыба не клюёт — с дна достаётся только мусор. Попробуй с наживкой!"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🎣 FISHING\n\nThe float doesn't even twitch. Without bait the fish don't bite — only junk comes off the bottom. Try with bait!"`
- ✏️ НОВЫЙ EN:


### resv.junk.sell

- ТЕКУЩИЙ RU: `"\nПродать можно за {price} {money}."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"\nCan be sold for {price} {money}."`
- ✏️ НОВЫЙ EN:


### resv.menu.chance

- ТЕКУЩИЙ RU: `"⚡ Шанс улова: {chance}%\n"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⚡ Catch chance: {chance}%\n"`
- ✏️ НОВЫЙ EN:


### resv.menu.intro

- ТЕКУЩИЙ RU: `"🌊 ПОДЗЕМНОЕ ВОДОХРАНИЛИЩЕ\n\nТёмная вода мерцает холодным светом. Тишина такая, что слышно собственные шаги. Иногда по воде пробегает рябь — там кто-то есть, и рыба тут непугливая.\n\n🐟 В глубине водится редкий улов, которого больше нигде не найти. Что именно попадётся на крючок — заранее не скажешь.\n"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🌊 UNDERGROUND RESERVOIR\n\nThe dark water glimmers with cold light. The silence is so deep you hear your own steps. Now and then a ripple runs across the water — something is there, and the fish here aren't shy.\n\n🐟 Rare catches live in the depths, found nowhere else. You can't tell in advance what will bite.\n"`
- ✏️ НОВЫЙ EN:


### resv.menu.no_rod

- ТЕКУЩИЙ RU: `"\n🎣 Удочка: нет — купи «Удочка из орешника» (магазин → Рыбалка)\n"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"\n🎣 Rod: none — buy a «Hazel rod» (Shop → Fishing)\n"`
- ✏️ НОВЫЙ EN:


### resv.menu.nobait

- ТЕКУЩИЙ RU: `"⚡ Без наживки рыба НЕ клюёт: со дна только мусор {junk}.\n"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⚡ Without bait the fish WON'T bite: the bottom only gives junk {junk}.\n"`
- ✏️ НОВЫЙ EN:


### resv.menu.rod

- ТЕКУЩИЙ RU: `"\n🎣 Удочка: {name} (ранг {rank}, +{bonus}%)\n🪱 Наживка: {bait}\n"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"\n🎣 Rod: {name} (tier {rank}, +{bonus}%)\n🪱 Bait: {bait}\n"`
- ✏️ НОВЫЙ EN:


### resv.menu.safe

- ТЕКУЩИЙ RU: `"\n\nЗдесь можно спокойно поменять слоты расходников — боя в этом зале нет."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"\n\nYou can safely swap your consumable slots here — there's no fight in this hall."`
- ✏️ НОВЫЙ EN:


### resv.msg.ap_fail

- ТЕКУЩИЙ RU: `"❌ Не удалось списать ОД."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ Couldn't spend AP."`
- ✏️ НОВЫЙ EN:


### resv.msg.no_ap

- ТЕКУЩИЙ RU: `"❌ Не хватает ОД: нужно {cost}, у тебя {ap}.\n⚡ ОД восстанавливаются раз в сутки."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ Not enough AP: you need {cost}, you have {ap}.\n⚡ AP comes back once a day."`
- ✏️ НОВЫЙ EN:


### resv.msg.no_rod

- ТЕКУЩИЙ RU: `"❌ У тебя нет удочки. Купи «Удочка из орешника» в магазине (категория «Рыбалка»)."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ You have no rod. Buy a «Hazel rod» in the shop (Fishing category)."`
- ✏️ НОВЫЙ EN:


### resv.msg.not_here

- ТЕКУЩИЙ RU: `"❌ Ты больше не в водохранилище."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ You're no longer in the reservoir."`
- ✏️ НОВЫЙ EN:


### resv.recover.gone

- ТЕКУЩИЙ RU: `"❌ Ты уже не в водохранилище.\nПродолжи путь кнопкой «🏃 Продолжить путь» в окне подземелья."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ You're no longer in the reservoir.\nContinue with the «🏃 Keep going» button in the dungeon window."`
- ✏️ НОВЫЙ EN:


### resv.recover.no_run

- ТЕКУЩИЙ RU: `"❌ Активное подземелье не найдено — забег закрыт.\nВернись к списку контрактов и начни новый."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ No active dungeon — the run is closed.\nReturn to the contract list and start a new one."`
- ✏️ НОВЫЙ EN:


### resv.seaweed.hit

- ТЕКУЩИЙ RU: `"🎣 РЫБАЛКА\n\nПоплавок дёрнулся, ты подсекаешь... и вдруг пусто.\nЗато на крючке что-то зацепилось: «Кусочек водорослей»!\n\n🎒 Улов записан в «Улов»."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🎣 FISHING\n\nThe float jerks, you set the hook... and nothing. But something snagged: «Piece of seaweed»!\n\n🎒 The catch is logged in «Catch»."`
- ✏️ НОВЫЙ EN:


### sell.cancel

- ТЕКУЩИЙ RU: `"↩️ Нет, отмена"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"↩️ No, cancel"`
- ✏️ НОВЫЙ EN:


### sell.rare_ask

- ТЕКУЩИЙ RU: `"⚠️ «{name}» — редкость: {rarity}.\nПродать {qty} шт.? Такой предмет потом не вернуть."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"⚠️ «{name}» — rarity: {rarity}.\nSell {qty} pcs.? You won't get such an item back."`
- ✏️ НОВЫЙ EN:


### sell.rare_final

- ТЕКУЩИЙ RU: `"✅ Да, точно продать"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"✅ Yes, sell for sure"`
- ✏️ НОВЫЙ EN:


### shop.catalog

- ТЕКУЩИЙ RU: `"Каталог"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Catalog"`
- ✏️ НОВЫЙ EN:


### shop.limit_reached

- ТЕКУЩИЙ RU: `"❌ Лимит на руках: у тебя уже {held} шт. купленных в магазине, максимум {limit}. Потрать хотя бы одну, чтобы докупить."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ Hand limit reached: you already hold {held} shop-bought, the maximum is {limit}. Use some to buy more."`
- ✏️ НОВЫЙ EN:


### shop.my_purchases

- ТЕКУЩИЙ RU: `"Мои покупки"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"My purchases"`
- ✏️ НОВЫЙ EN:


### shop.sell

- ТЕКУЩИЙ RU: `"Продать товар"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Sell an item"`
- ✏️ НОВЫЙ EN:


### shop_limit.ask

- ТЕКУЩИЙ RU: `"🛒 «{name}» — сколько штук можно держать на руках, купленных в магазине?\nСейчас: {cur}. Введи число от 0 до 1000 (0 — без лимита)."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🛒 «{name}» — how many shop-bought units can one account hold?\nNow: {cur}. Enter a number from 0 to 1000 (0 — no limit)."`
- ✏️ НОВЫЙ EN:


### shop_limit.bad

- ТЕКУЩИЙ RU: `"❌ Введи целое число от 0 до 1000."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"❌ Enter a whole number from 0 to 1000."`
- ✏️ НОВЫЙ EN:


### shop_limit.btn

- ТЕКУЩИЙ RU: `"🛒 Лимит на руках на аккаунт"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"🛒 Hand limit per account"`
- ✏️ НОВЫЙ EN:


### shop_limit.saved

- ТЕКУЩИЙ RU: `"✅ «{name}»: лимит на руках {n} шт. (0 — без лимита)."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"✅ «{name}»: hand limit is {n} (0 — no limit)."`
- ✏️ НОВЫЙ EN:


### state.благословение севера.hint

- ТЕКУЩИЙ RU: `"Боги Нордхайма отметили тебя за встречу с Белым Волком: +10% к атаке и уклонению, +5% к лечению, −3% к ценам в магазинах на сутки. Пока действует — волк не придёт снова."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"The gods of Nordheim marked you for meeting the White Wolf: +10% attack and dodge, +5% healing, −3% shop prices for a day. While it lasts, the wolf won't come again."`
- ✏️ НОВЫЙ EN:


### state.благословение севера.title

- ТЕКУЩИЙ RU: `"Благословение Севера"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Northern Blessing"`
- ✏️ НОВЫЙ EN:


### state.внимание севера.hint

- ТЕКУЩИЙ RU: `"Белый Волк Севера заметил тебя и отпустил. +5% к урону и уклонению на сутки. Пока действует — волк не придёт снова."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"The White Wolf of the North noticed you and let you go. +5% damage and dodge for a day. While it lasts, the wolf won't come again."`
- ✏️ НОВЫЙ EN:


### state.внимание севера.title

- ТЕКУЩИЙ RU: `"Внимание Севера"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Northern Attention"`
- ✏️ НОВЫЙ EN:


### state.истощён.hint

- ТЕКУЩИЙ RU: `"Истощение от перегрузки ОД: лимит восстановления за сутки исчерпан. Восстановление 75 ОД/сутки, максимум 90 ОД."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Exhaustion from AP overload: the daily restore limit is used up. Restores 75 AP per day, up to 90 AP."`
- ✏️ НОВЫЙ EN:


### state.истощён.title

- ТЕКУЩИЙ RU: `"Истощён"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Exhausted"`
- ✏️ НОВЫЙ EN:


### state.несварение.hint

- ТЕКУЩИЙ RU: `"Слишком много водорослей! Нельзя применять расходники (в том числе для восстановления ОД). Пройдёт через сутки."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Too much seaweed! Consumables can't be used (including AP restore). Passes in a day."`
- ✏️ НОВЫЙ EN:


### state.несварение.title

- ТЕКУЩИЙ RU: `"Несварение"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Indigestion"`
- ✏️ НОВЫЙ EN:


### state.оглушён.hint

- ТЕКУЩИЙ RU: `"Оглушение: точность, крит и уклонение снижены, расходники недоступны."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Stunned: accuracy, crit and dodge reduced, consumables unavailable."`
- ✏️ НОВЫЙ EN:


### state.оглушён.title

- ТЕКУЩИЙ RU: `"Оглушён"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Stunned"`
- ✏️ НОВЫЙ EN:


### state.ослеплён.hint

- ТЕКУЩИЙ RU: `"Неясыть ослепила тебя: в темноте удары мимо цели, уклонение едва работает."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"The owl blinded you: in the dark your blows miss, and dodging barely works."`
- ✏️ НОВЫЙ EN:


### state.ослеплён.title

- ТЕКУЩИЙ RU: `"Ослеплён"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Blinded"`
- ✏️ НОВЫЙ EN:


### state.очень пьян.hint

- ТЕКУЩИЙ RU: `"Ты едва держишься на ногах: атака и уклонение сильно снижены, зелья и расходники недоступны, вход во все здания закрыт. Пройдёт через 6 часов."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"You can barely stand: attack and dodge are badly reduced, potions and consumables are unavailable, all buildings are closed. Passes in 6 hours."`
- ✏️ НОВЫЙ EN:


### state.очень пьян.title

- ТЕКУЩИЙ RU: `"Очень пьян"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Very drunk"`
- ✏️ НОВЫЙ EN:


### state.пьян.hint

- ТЕКУЩИЙ RU: `"Выпил лишнего. В Ратушу, Библиотеку и Лабиринт не пускают, в бою руки не слушаются."`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"You had too much to drink. Town Hall, Library and the Labyrinth won't let you in; in battle your hands won't listen."`
- ✏️ НОВЫЙ EN:


### state.пьян.title

- ТЕКУЩИЙ RU: `"Пьян"`
- ✏️ НОВЫЙ RU:
- ТЕКУЩИЙ EN: `"Drunk"`
- ✏️ НОВЫЙ EN:
