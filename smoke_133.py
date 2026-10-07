"""Smoke v0.22.12: релизное оповещение в общий чат + команда /changelog.

Проверяем:
  • notify() теперь возвращает bool (успех отправки), а не None;
  • notify_release_update(): первый запуск (ключа нет) объявляет текущую
    версию; повторный старт с той же версией молчит; смена версии (деплой)
    шлёт оповещение заново;
  • ключ last_announced_version пишется ТОЛЬКО после успешной отправки:
    если чат не настроен или send_message упал — версия не запоминается
    (оповещение уйдёт при следующем старте после настройки);
  • текст оповещения короткий: версия, суть (VERSION_NOTES) и ссылка
    на /changelog;
  • /changelog отдаёт обе записи (текущий + предыдущий релиз);
  • main.py зовёт notify_release_update на старте, приветствие в /start
    осталось тизером (smoke_093 не нарушается).

Запуск: .venv\\Scripts\\python.exe smoke_133.py
"""
import asyncio
import os
import sys

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke133.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB

sys.path.insert(0, os.path.dirname(__file__))


class FakeBot:
    def __init__(self, fail=False):
        self.sent = []
        self.fail = fail

    async def send_message(self, chat_id, text, **kwargs):
        if self.fail:
            raise RuntimeError("нет прав в чате")
        self.sent.append((chat_id, text, kwargs))
        return None


class FakeMessage:
    def __init__(self):
        self.answers = []

    async def answer(self, text, **kwargs):
        self.answers.append(text)
        return None


async def run():
    from database.db import (init_db, close_db, get_db, set_news_chat,
                             get_news_chat, get_setting, set_setting)
    from utils.notify import (notify, notify_release_update, release_update_text,
                              RELEASE_ANNOUNCED_SETTING_KEY)
    from config import VERSION, VERSION_NOTES, PREV_VERSION, PREV_VERSION_NOTES

    await init_db()
    passed = 0
    failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
        else:
            failed += 1
            print(f"  FAIL: {name}")

    # ── 1. helpers settings ──
    check("get_setting: ключа нет → None", await get_setting("smoke133_missing") is None)
    await set_setting("smoke133_key", "abc")
    check("set/get roundtrip", await get_setting("smoke133_key") == "abc")
    await set_setting("smoke133_key", "def")
    check("set_setting — upsert", await get_setting("smoke133_key") == "def")

    # ── 2. notify() возвращает bool ──
    check("чат не настроен → notify False",
          await notify(FakeBot(), "привет") is False)
    await set_news_chat(-100999, 7)
    bot = FakeBot()
    check("чат настроен → notify True", await notify(bot, "привет") is True)
    check("ушло в тот чат и в тот топик",
          bot.sent[0][0] == -100999 and bot.sent[0][2].get("message_thread_id") == 7)
    check("упавшая отправка → notify False",
          await notify(FakeBot(fail=True), "привет") is False)

    # ── 3. текст оповещения короткий и со ссылкой ──
    txt = release_update_text(VERSION, VERSION_NOTES)
    check("в тексте есть версия", f"v{VERSION}" in txt)
    flat_notes = " ".join(VERSION_NOTES.split())
    check("в тексте есть суть релиза", flat_notes in txt)
    check("нет нерабочей команды-/ссылки /changelog", "/changelog" not in txt)
    check("подробности — обычной фразой «в боте»", "в боте" in txt)
    check("нет сырых переносов строк из заметок", "\n" not in flat_notes)
    check("оповещение не простыня (<= 700 символов)", len(txt) <= 700)

    # ── 4. первый запуск: ключа нет → объявляет сразу ──
    bot1 = FakeBot()
    ok1 = await notify_release_update(bot1)
    check("первый запуск: оповещение отправлено", ok1 is True and len(bot1.sent) == 1)
    check("версия запомнена", await get_setting(RELEASE_ANNOUNCED_SETTING_KEY) == VERSION)
    check("ушло в настроенный чат/топик",
          bot1.sent[0][0] == -100999 and bot1.sent[0][2].get("message_thread_id") == 7)

    # ── 5. обычный рестарт (та же версия) молчит ──
    bot2 = FakeBot()
    ok2 = await notify_release_update(bot2)
    check("тот же VERSION → без сообщения", ok2 is False and not bot2.sent)

    # ── 6. новый деплой (версия сменилась) → объявляет снова ──
    await set_setting(RELEASE_ANNOUNCED_SETTING_KEY, "0.0.1")
    bot3 = FakeBot()
    ok3 = await notify_release_update(bot3)
    check("смена версии → оповещение заново", ok3 is True and len(bot3.sent) == 1)
    check("ключ обновлён на новую версию",
          await get_setting(RELEASE_ANNOUNCED_SETTING_KEY) == VERSION)

    # ── 7. чат не настроен: не отправлено → ключ НЕ записан ──
    await set_news_chat(None)           # отключаем чат
    await set_setting(RELEASE_ANNOUNCED_SETTING_KEY, "0.0.1")
    bot4 = FakeBot()
    ok4 = await notify_release_update(bot4)
    check("без чата → не отправлено", ok4 is False and not bot4.sent)
    check("без чата ключ НЕ записан (будет повтор)",
          await get_setting(RELEASE_ANNOUNCED_SETTING_KEY) == "0.0.1")

    # ── 8. отправка падает (нет прав): тоже без записи ключа ──
    await set_news_chat(-100999, None)
    bot5 = FakeBot(fail=True)
    ok5 = await notify_release_update(bot5)
    check("упавшая отправка → False", ok5 is False)
    check("упавшая отправка → ключ не записан",
          await get_setting(RELEASE_ANNOUNCED_SETTING_KEY) == "0.0.1")
    # а после «починки прав» — уходит и записывается
    bot6 = FakeBot()
    ok6 = await notify_release_update(bot6)
    check("после починки прав оповещение уходит", ok6 is True and len(bot6.sent) == 1)
    check("и ключ наконец записан",
          await get_setting(RELEASE_ANNOUNCED_SETTING_KEY) == VERSION)

    # ── 9. /changelog: обе записи текущего конфига ──
    from bot.handlers.changelog import router as changelog_router, cmd_changelog
    msg = FakeMessage()
    await cmd_changelog(msg)
    out = msg.answers[0] if msg.answers else ""
    flat_cur = " ".join(VERSION_NOTES.split())
    flat_prev = " ".join(PREV_VERSION_NOTES.split())
    check("/changelog отвечает", bool(out))
    check("текущая сборка в ответе", f"v{VERSION}" in out and flat_cur in out)
    check("предыдущая сборка в ответе",
          f"v{PREV_VERSION}" in out and flat_prev in out)
    handlers = [m.callback for m in changelog_router.message.handlers]
    check("/changelog зарегистрирован в роутере", cmd_changelog in handlers)

    # ── 10. проводка в main.py и нетронутое приветствие ──
    root = os.path.dirname(__file__)
    main_src = open(os.path.join(root, "main.py"), encoding="utf-8").read()
    check("main зовёт notify_release_update на старте",
          main_src.count("notify_release_update(bot)") == 1)
    check("changelog_router подключён",
          "dp.include_router(changelog_router)" in main_src
          and "changelog_router" in main_src.split("for r in (")[1].split("):")[0])
    check("команда объявлена в меню бота",
          'BotCommand(command="changelog"' in main_src)
    start_src = open(os.path.join(root, "bot", "handlers", "start.py"), encoding="utf-8").read()
    check("приветствие осталось тизером (smoke_093 не нарушен)",
          start_src.count("_version_teaser(VERSION_NOTES)") == 1
          and "PREV_VERSION" not in start_src)

    await close_db()
    print(f"\nSmoke 133: {passed} passed, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    async def _main():
        try:
            return await run()
        finally:
            from database.db import close_db
            await close_db()

    sys.exit(asyncio.run(_main()))
