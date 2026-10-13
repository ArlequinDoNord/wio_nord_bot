# Карта меню и навигации

> Навигационная карта бота: reply-меню, команды, inline-панели и неймспейсы
> `callback_data`. Клавиатуры собираются в `keyboards/keyboards.py`; хендлеры —
> в `bot/handlers/`. Полный реестр колбэков — в [FSM_STATES.md](FSM_STATES.md).

## Reply-клавиатура главного меню

Собирается в `keyboards.main_menu_keyboard(is_admin, is_pilot)` и
`keyboards.main_menu_kb(user_id)` (пересчитывает флаги каждый раз — важно, иначе
у админа пропадает кнопка «👑 Админ-панель» после навигации).

| Кнопка | Обработчик | Примечание |
|---|---|---|
| `Профиль` | `profile.py:233` | |
| `Инвентарь` | `inventory.py:553` | |
| `Магазин` | `shop.py` | |
| `Город` | `start.py:119` | открывает Аркхольм |
| `📰 Новости Нордхайма` | `news.py` | |
| `🧱 Стена изречений` | `wall.py` | |
| `📝 Сдать отчёт` | `reports.py` | только пилот (не турист) |
| `👑 Админ-панель` | `admin.py` | только админ |

Множество текстов, считающихся главным меню, — `utils/helpers.MAIN_MENU_TEXTS`
(используется в `MainMenuFSMReset` и FSM-хендлерах как `~F.text.func(is_main_menu_text)`).

> Ранее `MAIN_MENU_TEXTS` содержал рудимент `"Банк"` (кнопки «Банк» в reply-меню
> нет — банк доступен через «Город»). Убран в v0.23.9.

## Команды

Регистрируются в `main.py:515` (`set_my_commands`).

| Команда | Хендлер |
|---|---|
| `/start` | `start.py` (вход, тизер версии) |
| `/profile` | `profile.py:228` |
| `/shop` | `shop.py:192` |
| `/help` | `start.py:85` |
| `/changelog` | `changelog.py:20` |
| `/chatinfo` | `admin.py:2799` (админ) |

## Inline-меню по разделам

| Раздел | Клавиатура | Неймспейс |
|---|---|---|
| Главное (админ) | `admin_panel_keyboard` → `admin:menu` | `admin:*` |
| Профиль | `profile_keyboard` | `profile:*` |
| Магазин | `shop_keyboard`, `shop_catalog_keyboard`, `item_card_keyboard` | `shop:*`, `shopcat:*`, `buy_nord:*` |
| Банк | `bank_keyboard` | `bank:*` |
| Инвентарь | `inventory_keyboard` | `inv:*`, `trade:*` |
| Город | `city_keyboard` | `city:*`, `location:*` |
| Стена изречений | `wall_keyboard` | `wall:*` |
| Подземелье | `dungeon_keyboard` | `dungeon:*` |
| Производство | `production_keyboard` | `prod:*` |
| Отчёты | `report_keyboard` | `report:*` |
| Дуэль | `interaction_keyboard` | `duel:*`, `interact:*` |
| Жильё | `housing.py` | `housing:*` |
| Авиакрылья | `admin:wing` / `hq.py` | `wing:*`, `hq:*` |
| Реклама рецептов | `admin_recipes.py` | `recadm:*` |
| Опросы | `polls.py` / `poll_archive.py` | `poll:*` |
| Общие | `back_to_main`, `cancel_keyboard`, `confirm_keyboard` | `back:main`, `cancel`, `noop`, `confirm:*` |

Клавиатуры зданий: эмодзи задаётся `keyboards.LOCATION_BUTTON_EMOJI`
(`hq` → 🎖️, `contracts` → 📜, `duel_house` → 🥊, остальные → 📍).

## Админ-панель (`admin_panel_keyboard(permissions)`)

Кнопка видна только при наличии соответствующего права:

| Кнопка | Право | Колбэк |
|---|---|---|
| 🛒 Управление магазином | `can_manage_shop` | `admin:shop` |
| 📜 Менеджер рецептов | `can_manage_shop` | `recadm:menu` |
| 💰 Финансы | финансы/балансы/валюта | `admin:finance` |
| 📋 Отчёты | `can_view_reports`/`can_approve_reports` | `admin:reports` |
| 📊 Статистика регионов | то же | `admin:region_stats` |
| 👑 Управление ролями | `can_manage_admins`/`can_assign_mvd_helper` | `admin:roles` |
| 🎖️ Статусы | `can_manage_statuses`/`can_grant_statuses`/`can_grant_citizen_status` | `admin:statuses` |
| ⭐ Повышение в звании | `can_grant_troops` | `admin:ranks` |
| 🎭 Состояния | `can_manage_states` | `admin:states` |
| 🏅 Награды | `can_manage_awards`/`can_grant_awards` | `admin:awards` |
| 📍 Локации | `can_manage_locations` | `admin:locations` |
| 🏰 Подземелья | `can_manage_locations` | `admin:dungeons` |
| 🐟 Рыбалка | `can_manage_locations` | `admin:fishing` |
| 🍄 Грибы леса | `can_manage_locations` | `admin:forest` |
| ⚔️ Враги | `can_manage_locations` | `admin:enemies` |
| 🧾 Логи действий | `can_view_logs` | `admin:logs` |
| 📒 Лог игрока | `can_view_logs` | `admin:player_log` |
| 📊 Активность игроков | `can_view_logs` | `act:all` |
| 📈 Популярность локаций | `can_view_logs` | `locstat:7` |
| 🗑 Удалить фото пилота | `can_manage_users` | `admin:del_photo` |
| 📡 Установить позывной | `can_manage_users` | `admin:callsign` |
| 🪽 Авиакрылья | `can_manage_wing` | `admin:wing` |
| 📦 Хранилище | `can_manage_storage` | `admin:storage` |
| 🔙 В меню | — | `back:main` |

## Порядок регистрации роутеров (`main.py:523`)

Первый совпавший хендлер выигрывает, поэтому порядок критичен:
`start → changelog → profile → bank → admin → admin_recipes → shop → inventory →
reports → dungeon → pilots → polls → poll_archive → representative → library →
locations → park → fishing → forest → housing → news → kvp → wall → hq → clans →
nii → tourist_booklet → duel`.

Подробнее о хендлерах и неймспейсах — [HANDLERS.md](HANDLERS.md).
