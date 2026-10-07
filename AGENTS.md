# AGENTS.md

Проект: игровой Telegram-бот (aiogram 3, aiosqlite). Python: `.venv\Scripts\python.exe`.
Smoke-тесты: `tools/run_smokes.py` — прогон всех `smoke_NNN.py` одной командой
(82 шт., каждый автономен и специализирован под свою версию/фичу; известные
долги: `smoke_055`/`085`/`088` падают, `smoke_095` после исключения зависает —
раннер на нём падает по таймауту, хвост 096–134 гонять отдельно).

## Ремоуты (обязательно прочитать перед деплоем)
В рабочем клоне два репозитория (сверять с `git remote -v`):
- `server` = прод `arlequin@89.19.210.194:/opt/arlequin.git` (bare-репо на сервере, post-receive-хук слушает только `refs/heads/main` и сам пересобирает контейнер).
- `origin` = GitHub-зеркало https://github.com/ArlequinDoNord/wio_nord_bot.git (HTTPS).

⚠️ Названия обманчивы: **пуш в `origin` ничего не деплоит** — это только зеркало
GitHub. Деплой на прод — всегда `git push server main --tags`.

⚠️ SSH-пуш на GitHub бесполезен: в этой сети исходящий SSH к `github.com:22` и
`ssh.github.com:443` зависает после обмена ключами. GitHub лежит на `origin` по
HTTPS — авторизация через Windows Credential Manager (учётка `git:https://github.com`
уже сохранена, работает без интерактива). SSH-ключ нужен только для `server`.

## Деплой
- py_compile + smoke → бамп `VERSION`/`VERSION_NOTES`/`PREV_VERSION`/`PREV_VERSION_NOTES` в `config.py`, `CHANGELOG.md` → commit → tag `vX.Y.Z` → два пуша:
  1. `git push server main --tags` — деплой на прод (хук пересобирает контейнер; git-клиент не проходит проверку host key — перед пушем `$env:GIT_SSH_COMMAND = "C:/Windows/System32/OpenSSH/ssh.exe"`);
  2. `git push origin main --tags` — синхронизация GitHub-зеркала (HTTPS, без ключа; НЕ забывать — зеркало стояло на месте ещё c v0.18.8 именно из-за пропуска этого шага). Недостающие старые теги (`v0.18.9` и т.д.) пуш снимет сам.
- После деплоя проверить прод: VERSION в контейнере (`docker exec -i wio_nord_bot-wio_nord_bot-1 python -u -` → `import config`) и `git ls-remote https://github.com/ArlequinDoNord/wio_nord_bot.git refs/heads/main refs/tags/vX.Y.Z` для зеркала.
- Прод-БД: `wio_nord_bot-wio_nord_bot-1`:/app/data/nordmark.db (sqlite3 в контейнере нет — использовать `docker exec -i ... python -`).

## Пользователи
- Simargl1 — владелец/супер-админ (Telegram ID 561309060). Подтверждает деплой.
- 207599548 Platual, 1218849548 victoriya1228 и др. — обычные игроки/тестировщики.