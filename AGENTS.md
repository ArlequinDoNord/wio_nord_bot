# AGENTS.md

Проект: игровой Telegram-бот (aiogram 3, aiosqlite). Python: `.venv\Scripts\python.exe`.
Smoke-тесты: `tools/run_smokes.py` — прогон всех `smoke_NNN.py` одной командой
(27 шт., каждый автономен и специализирован под свою версию/фичу).

## Деплой
- py_compile + smoke → бамп `VERSION`/`VERSION_NOTES` в `config.py`, `CHANGELOG.md` → commit → tag `vX.Y.Z` → `git push origin main --tags` (github ArlequinDoNord/wio_nord_bot) → `git push server main:master --tags` (server `arlequin@89.19.210.194:/opt/arlequin.git`, хук сам пересобирает контейнер).
- Прод-БД: `wio_nord_bot-wio_nord_bot-1`:/app/data/nordmark.db (sqlite3 в контейнере нет — использовать `docker exec -i ... python -`).

## Пользователи
- Simargl1 — владелец/супер-админ (Telegram ID 561309060). Подтверждает деплой.
- 207599548 Platual, 1218849548 victoriya1228 и др. — обычные игроки/тестировщики.