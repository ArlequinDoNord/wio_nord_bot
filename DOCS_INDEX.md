# Индекс документации N.O.R.D.

> Единая точка входа. Когда не знаешь с чего начать — смотри сюда.
> Документы ниже созданы для ускорения работы. К ним лучше обращаться, чем держать всё в голове/grep'ать вслепую.

## 1) Карта проекта (быстрый ориентир)
| Док | Для чего | Когда читать |
|---|---|---|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Структура проекта, точки входа, связки `main.py`↔`bot/`↔`database/`, middlewares, запуск. | Перед первым знакомством с модулем/перед крупной правкой. |
| [HANDLERS.md](HANDLERS.md) | Все роутеры и хендлеры (`bot/handlers/*.py`), связи с `main.py`, фильтры `F.data`. **Генерируется** `tools/export_handlers.py`. | «Где править X?» — первое, что стоит глянуть. |
| [FSM_STATES.md](FSM_STATES.md) | Все `StatesGroup`/стейты, кто сетит/обрабатывает, привязка к `callback_data`. **Генерируется** `tools/export_states.py`. | Перед правками состояний, диалогов, многошаговых форм. |
| [MENU_MAP.md](MENU_MAP.md) | Карта кнопок/меню, навигация по городу/разделам. | Быстро сориентироваться в UX-навигации. |
| [GLOSSARY.md](GLOSSARY.md) | Единые термины проекта. | Когда сомневаешься в названии сущности/кнопки. |

## 2) БД, миграции, данные
| Док | Для чего | Когда читать |
|---|---|---|
| [db_schema.md](db_schema.md) | Читаемая схема БД. | Перед правками БД/запросов, быстрее чем `PRAGMA table_info`. |
| [MIGRATIONS.md](MIGRATIONS.md) | Подход миграций: `_ensure_column`, `ensure_*`, `seed_*`, `init_db()`. **Генерируется** `tools/export_migrations.py`. | Перед добавлением колонок/новых таблиц/миграционных правок. |
| [DATABASE.md](DATABASE.md) | Доп. заметки по работе с БД (если есть). | При нетривиальных правках/поиске связей. |

## 3) Тесты и качество
| Док | Для чего | Когда читать |
|---|---|---|
| [SMOKE_INDEX.md](SMOKE_INDEX.md) | Индекс всех `smoke_NNN.py`, что за что отвечает. **Генерируется** `tools/export_smokes.py`. | Перед правкой фичи — найти релевантный смоук. Перед релизом — понять покрытие. |
| [tools/run_smokes.py](tools/run_smokes.py) | Раннер смоуков (отчёт, таймауты/HANG, прогон всего пула). | Всегда перед релизом: `python tools/run_smokes.py` (с `PYTHONIOENCODING=utf-8`). |
| [tools/docs_check_sync.py](tools/docs_check_sync.py) | **Автопроверка**: напомнит если `FSM_STATES.md`/`MIGRATIONS.md`/`SMOKE_INDEX.md`/`HANDLERS.md` устарели. | Перед коммитом/перед релизом — быстрая страховка. |

## 4) Деплой, сервер, процессы
| Док | Для чего | Когда читать |
|---|---|---|
| [AGENTS.md](AGENTS.md) | **Главные правила** для работы в репозитории: ремоуты, правила релиза, кодировки, смоуки, вопрос про спойлер/интригу. Краткий чек-листовый формат. | **Начинать здесь**. Обязателен к прочтению перед любыми изменениями. |
| [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md) | Пошаговый чек-лист релиза (commit → tag на HEAD → push server/origin → проверка). | **Перед каждым деплоем**. Снижает риск косяков. |
| [SERVER_MAINTENANCE.md](SERVER_MAINTENANCE.md) | Детали прод-сервера: docker, post-receive хук, бэкапы БД, место на диске, rootless/docker, обслуживание. | При вопросах про деплой/сервер, восстановление БД, чистку. |
| [CHANGELOG.md](CHANGELOG.md) | История релизов. | Для понимания что менялось в прошлых версиях. |

## 5) Конфиг, баланс, контент
| Док | Для чего | Когда читать |
|---|---|---|
| [CONFIG_REFERENCE.md](CONFIG_REFERENCE.md) | Справочник по `config.py`. | При правках констант/настроек. |
| [BALANCE.md](BALANCE.md), [BALANCE_AUDIT.md](BALANCE_AUDIT.md), [BALANCE_ANALYSIS.md](BALANCE_ANALYSIS.md) | Балансные заметки/аудит. | При экономических/балансных правках. |
| [BATTLE_TEXTS.md](BATTLE_TEXTS.md) | Каталог боевых текстов. **Обновлять при правках боевых хендлеров.** | При правках `forest/dungeon/kvp/mine/logging_site/utils/combat.py`. |
| [CLAN_HALL.md](CLAN_HALL.md) | Спека «Клан-холл»: типы зданий, склад, расширения, права, схема БД, фазы. | Перед любой работой по клановому зданию. |

## Правило «перед правкой»
- **Хендлер/навигация** → [HANDLERS.md](HANDLERS.md) + [MENU_MAP.md](MENU_MAP.md)
- **Состояния/диалоги** → [FSM_STATES.md](FSM_STATES.md)
- **БД/миграции** → [db_schema.md](db_schema.md) + [MIGRATIONS.md](MIGRATIONS.md)
- **Новая фича/регресс** → поиск по [SMOKE_INDEX.md](SMOKE_INDEX.md), запустить релевантный смоук
- **Релиз** → [AGENTS.md](AGENTS.md) → [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md) → [SERVER_MAINTENANCE.md](SERVER_MAINTENANCE.md)

## Автогенерация
Если меняли `bot/handlers/`, `utils/states.py`, `main.py`, `database/db.py`, `config.py`, `smoke_*.py` — достаточно одной команды:

```powershell
.\.venv\Scripts\python.exe tools\docs_check_sync.py --fix
```

Либо точечно по скриптам:

```powershell
.\.venv\Scripts\python.exe tools\export_handlers.py
.\.venv\Scripts\python.exe tools\export_states.py
.\.venv\Scripts\python.exe tools\export_migrations.py
.\.venv\Scripts\python.exe tools\export_smokes.py
.\.venv\Scripts\python.exe tools\export_config.py
```
