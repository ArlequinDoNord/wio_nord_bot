# Архитектура N.O.R.D. 3.0

> Документ для быстрого входа в проект: как устроен код, откуда что
> вызывается и где искать нужное. Смежные доки: [HANDLERS.md](HANDLERS.md),
> [FSM_STATES.md](FSM_STATES.md), [MIGRATIONS.md](MIGRATIONS.md),
> [CONFIG_REFERENCE.md](CONFIG_REFERENCE.md), [db_schema.md](db_schema.md),
> [MENU_MAP.md](MENU_MAP.md).

## Обзор

Telegram-бот игрового сообщества (симулятор пилотов, мир «Нордхайм»).

| Слой | Технология |
|---|---|
| Язык | Python 3.12 |
| Фреймворк | aiogram 3.x |
| БД | SQLite через `aiosqlite` (файл `database/nordmark.db`) |
| Конфиг | `python-dotenv` (`.env`) |
| Хранение FSM | JSON-файл на диске (`bot/fsm_store.py`) |
| Запуск | Docker (`Dockerfile` + `docker-compose.yml`) |

Точка входа — `main.py`. Один процесс, long-polling (`dp.start_polling`).

## Структура проекта

```
main.py                 точка входа: инициализация, роутеры, middleware, планировщик
config.py               все константы и env (см. CONFIG_REFERENCE.md)
database/
    db.py               ВСЯ работа с БД (~12.6k строк): схема, миграции, засевы, CRUD
    nordmark.db         рабочая база (в контейнере — /app/data)
bot/
    fsm_store.py        JsonFileStorage — FSM-состояния переживают рестарт
    handlers/           по одному модулю на раздел (28 файлов, см. HANDLERS.md)
keyboards/
    keyboards.py        все клавиатуры: reply-меню, inline-панели, city, пагинация
utils/
    helpers.py          is_main_menu_text, formatters, resolve_image, edit_message_safe
    permissions.py      роли и права админов (is_admin и т.п.)
    states.py           игровые СОСТОЯНИЯ игрока (пьян, несварение) — НЕ FSM
    notify.py           уведомления (в т.ч. оповещение о релизе)
    chat_guard.py       ChatGuard middleware (фильтр чатов)
    combat.py           общая боевая логика
    combat_model.py     модель боя (урон/защита/уклонение)
    wings.py            авиакрылья
    formatters.py       форматирование карточек/сообщений
assets/                 изображения (сцены по времени суток, дропы)
tools/
    export_*.py         генераторы доков (states, handlers, smokes, config, migrations)
    run_smokes.py       прогон смоуков
smoke_NNN.py            автономные тесты (см. SMOKE_INDEX.md)
```

## Поток выполнения при старте (`main.py:main`)

1. `init_db()` — создаёт таблицы (`CREATE TABLE IF NOT EXISTS`) и прогоняет
   аддитивные миграции `_ensure_column` (см. [MIGRATIONS.md](MIGRATIONS.md)).
2. Засевы/идемпотентные миграции: `seed_default_items`, `seed_dungeon`,
   `ensure_dungeon_shop_items`, `ensure_life_items`, `ensure_recipes`,
   `ensure_water_fish`, `ensure_forest_*`, `seed_kvp`, `ensure_duel_items`,
   `ensure_achievements`, `ensure_tourist_booklet` и др.
3. `Bot(...)`; `Dispatcher(storage=JsonFileStorage(...))`.
4. Регистрируется глобальный `@dp.errors()` (логирует в `activity_log` + `bot.log`,
   пишет игроку «что-то пошло не так»).
5. `bot.set_my_commands` — `/start`, `/profile`, `/shop`, `/help`, `/changelog`.
6. `dp.include_router(...)` — порядок важен (первый совпавший хендлер выигрывает).
7. Навешиваются middleware на каждый роутер.
8. `notify_release_update` — разовое оповещение в общий чат при смене `VERSION`.
9. `asyncio.create_task(scheduled_jobs(bot))` + `dp.start_polling`.

## Слои и зависимости

```
handlers/  ->  utils/ (helpers, permissions, notify, states, combat)
           ->  database/db.py  (единственный слой доступа к SQLite)
keyboards/ <-  handlers (клавиатуры только собираются, логики нет)
config.py  <-  все слои (константы)
```

- **`database/db.py` — единая точка доступа к БД.** Хендлеры не пишут SQL
  напрямую; всё через функции `get_*`/`set_*`/`ensure_*`. `get_db()` ставит
  кастомный row-factory → строки это `dict` (`.get()` работает, но отсутствие
  колонки — `KeyError`). Для безопасного чтения есть `utils.helpers.row_get`.
- **`keyboards/keyboards.py`** содержит только фабрики клавиатур.
- **`utils/states.py`** — про игровые состояния (`users.state`), не про FSM
  aiogram. Не путать с [FSM_STATES.md](FSM_STATES.md).

## Middleware (`main.py`)

Навешиваются на `message` и `callback_query` каждого роутера в цикле
`main.py:552`.

| Middleware | Что делает |
|---|---|
| `ChatGuard` | фильтрует допустимые чаты |
| `FishingActiveLock` | пока идёт заброс рыбалки/поиск грибов/бой с моллюском — блокирует уход в другие меню, чтобы не сжечь окно |
| `MainMenuFSMReset` | нажатие reply-кнопки главного меню сбрасывает активное FSM (кроме активного забега в подземелье) |
| `ActivityTracker` | обновляет `users.last_active` не чаще раза в минуту (троттлинг in-memory) |

> ⚠️ `tourist_booklet_router` подключён (`main.py:549`), но **не входит** в
> кортеж роутеров middleware-цикла (`main.py:552`). Возможный недочёт — на нём
> не действуют ChatGuard/ActivityTracker.

## Планировщик `scheduled_jobs` (`main.py:219`)

Раз в сутки в **10:00 МСК** (`REPORT_DAY_START_HOUR/MINUTE`): восстановление AP,
налог на жильё (`run_housing_tax`), зарплаты (`pay_salaries`), 1-го числа —
ежемесячные наградные, 28-го — оклады за должности, выплаты по отчётам
(`payout_reports`), пересчёт статистики регионов, очистка логов, недельная
архивация стены, обслуживание опросов. Цикл сначала **ждёт** плановое время, а
не срабатывает сразу на старте (иначе время выплат плыло бы при каждом деплое).

## FSM

- Хранилище — `bot/fsm_store.py::JsonFileStorage`, файл `fsm_state.json` рядом
  с БД (`FSM_STORAGE_PATH`). Состояния незаконченных форм переживают рестарт.
- Все `StatesGroup` и их состояния с привязкой к хендлерам — в
  [FSM_STATES.md](FSM_STATES.md). Реестр `callback_data` — там же.

## Обработка ошибок

- Глобальный `@dp.errors()` (`main.py:477`): пишет `handle_error` в
  `activity_log` (можно найти по игроку), в `bot.log` с трейсбеком, и отправляет
  игроку понятный текст (кроме `TelegramBadRequest`).
- Смоук-тесты автономны (свой temp-DB), см. [SMOKE_INDEX.md](SMOKE_INDEX.md).

## Конфигурация и секреты

- Секреты (`BOT_TOKEN`, `ADMIN_IDS`, `DATABASE_PATH`, `NEWS_CHAT_ID`) — в `.env`
  (шаблон `.env.example`). В контейнере БД лежит в volume `/app/data`.
- `VERSION`/`PREV_VERSION`/`VERSION_NOTES` — правило релиза описано в
  [AGENTS.md](AGENTS.md): бампать версию при каждом деплое.

## Деплой (кратко)

`git push server main --tags` → bare-git хук пересобирает контейнер. Подробности —
[SERVER_MAINTENANCE.md](SERVER_MAINTENANCE.md), регламент — [AGENTS.md](AGENTS.md).
