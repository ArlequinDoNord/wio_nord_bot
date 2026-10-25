# RELEASE_CHECKLIST.md

Короткий чек-лист для деплоя. Ключевое правило: **тег вешаем ТОЛЬКО на коммит с релизными правками**.

## 1) Предрелиз
- [ ] **Синхронизация доков**: `.\.venv\Scripts\python.exe tools\docs_check_sync.py --fix` — все `UP TO DATE`
- [ ] **Смоуки**: `.\.venv\Scripts\python.exe tools\run_smokes.py` (по умолчанию в 4 потока, либо точечно `tools\run_smokes.py --last 10` / `146 158-159`) → **0 failed**
- [ ] **Код компилируется** (быстрая проверка): `.\.venv\Scripts\python.exe -m py_compile config.py main.py database/db.py` (либо по затронутым модулям)
- [ ] **Уточнить у владельца**: явный спойлер в анонсе или неявный намёк (см. [AGENTS.md](AGENTS.md) «Предрелизный вопрос»)

## 2) Бамп версии
- [ ] **Обновить `config.py`**: `VERSION`, `VERSION_NOTES` (с учётом выбора), сдвинуть старый `VERSION_NOTES` в `PREV_VERSION`/`PREV_VERSION_NOTES`. Держим только **текущий + предыдущий**.
- [ ] **Обновить `CHANGELOG.md`**: добавить секцию `[X.Y.Z] - YYYY-MM-DD` с полным описанием изменений.
- [ ] **Сверить HEAD**: `git log -1 --oneline` — понять на каком коммите сейчас.

## 3) Коммит и тег (ОБЯЗАТЕЛЬНО в таком порядке)
- [ ] **Стейджим всё релизное**: `git add -A` (убедиться что нет лишних temp-файлов)
- [ ] **Коммитим**: `git commit -m "release: vX.Y.Z — короткое описание"`
- [ ] **Проверяем HEAD**: `git log -1 --oneline` — в нём должны быть `config.py`, `CHANGELOG.md` и релизные правки
- [ ] **Вешаем тег ТОЛЬКО на HEAD**: `git tag vX.Y.Z $(git rev-parse HEAD)` (или просто `git tag vX.Y.Z`)
- [ ] **Финальная сверка**: `git rev-parse vX.Y.Z` == `git rev-parse HEAD`

## 4) Деплой
- [ ] **Настроить SSH для server** (WSL/PowerShell): `$env:GIT_SSH_COMMAND = "C:/Windows/System32/OpenSSH/ssh.exe"`
- [ ] **Пуш в прод**: `git push server main --tags`  
  *(хук на сервере пересоберёт и перезапустит контейнер)*
- [ ] **Пуш в зеркало GitHub**: `git push origin main --tags`  
  *(только зеркало, не деплоит. SSH на GitHub может зависать — в нашей сети HTTPS)*
- [ ] **Если тег уже был повешен не на HEAD**: **только в крайнем случае** `git push server refs/tags/vX.Y.Z --force` и `git push origin refs/tags/vX.Y.Z --force`. Предпочтительнее **исправить через новый коммит + новый тег**.

## 5) Верификация
- [ ] **Проверить версию в контейнере**:  
  `ssh arlequin@89.19.210.194 "docker exec -i wio_nord_bot-wio_nord_bot-1 python -u -c \"import config; print(config.VERSION)\""`
- [ ] **Проверить зеркало**:  
  `git ls-remote https://github.com/ArlequinDoNord/wio_nord_bot.git refs/heads/main refs/tags/vX.Y.Z`
- [ ] **Проверить в боте**: зайти в `/start` — должен появиться тизер `>> Что нового:` с `VERSION_NOTES`. Если выбран явный анонс — должен прийти в общий чат.
- [ ] **Смоуки на всякий случай** (опц.): `.\.venv\Scripts\python.exe tools/run_smokes.py` локально — ок.

## Важные напоминания
- **Commit before tag.** Никогда не тегай до коммита.
- **origin != деплой.** Деплоит только `server`.
- **Держим PREV_VERSION** только на 1 предыдущий релиз.
- **UTF-8 без BOM.** Не править `.py/.md` через PowerShell `Out-File/>`.
- **Детали по серверу** — см. [SERVER_MAINTENANCE.md](SERVER_MAINTENANCE.md)
- **Общие правила** — см. [AGENTS.md](AGENTS.md)
