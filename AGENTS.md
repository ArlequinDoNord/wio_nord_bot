# AGENTS.md

Проект: игровой Telegram-бот (aiogram 3, aiosqlite). Python: `.venv\Scripts\python.exe`.
Smoke-тесты: `tools/run_smokes.py` — прогон всех `smoke_NNN.py` одной командой
(55 шт., каждый автономен и специализирован под свою версию/фичу).

## Ремоуты (обязательно прочитать перед деплоем)
В рабочем клоне исключительно прод и зеркало, GitHub-ремоут по SSH НЕ работает:
- `origin` = `server` = прод `arlequin@89.19.210.194:/opt/arlequin.git` (bare-репо на сервере, post-receive-хук слушает только `refs/heads/main` и сам пересобирает контейнер).
- `github` = зеркало https://github.com/ArlequinDoNord/wio_nord_bot.git (HTTPS).

⚠️ SSH-пуш на GitHub бесполезен: в этой сети исходящий SSH к `github.com:22` и
`ssh.github.com:443` зависает после обмена ключами. GitHub пушим ТОЛЬКО по HTTPS —
авторизация через Windows Credential Manager (учётка `git:https://github.com`
уже сохранена, работает без интерактива). SSH-ключ нужен только для прода.

## Деплой
- py_compile + smoke → бамп `VERSION`/`VERSION_NOTES`/`PREV_VERSION`/`PREV_VERSION_NOTES` в `config.py`, `CHANGELOG.md` → commit → tag `vX.Y.Z` → два пуша:
  1. `git push origin main --tags` — деплой на прод (хук пересобирает контейнер; при первом контакте хоста нужен `GIT_SSH_COMMAND="ssh -o StrictHostKeyChecking=accept-new -i \"$env:USERPROFILE\.ssh\id_ed25519\""`);
  2. `git push github main --tags` — синхронизация GitHub-зеркала (HTTPS, без ключа; НЕ забывать — зеркало стояло на месте ещё c v0.18.8 именно из-за пропуска этого шага). Недостающие старые теги (`v0.18.9` и т.д.) пуш снимет сам.
- После деплоя проверить прод: VERSION в контейнере (`docker exec -i wio_nord_bot-wio_nord_bot-1 python -u -` → `import config`) и `git ls-remote https://github.com/ArlequinDoNord/wio_nord_bot.git refs/heads/main refs/tags/vX.Y.Z` для зеркала.
- Прод-БД: `wio_nord_bot-wio_nord_bot-1`:/app/data/nordmark.db (sqlite3 в контейнере нет — использовать `docker exec -i ... python -`).

## Пользователи
- Simargl1 — владелец/супер-админ (Telegram ID 561309060). Подтверждает деплой.
- 207599548 Platual, 1218849548 victoriya1228 и др. — обычные игроки/тестировщики.