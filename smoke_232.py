# -*- coding: utf-8 -*-
"""Smoke 232 — оповещения на языке получателя/пилота.

- оповещение в общий чат о прохождении подземелья: язык пилота, который прошёл;
- награда и похвала в общий чат: язык пилота;
- личное сообщение (должность): язык получателя;
- у пилота ru — русский текст (без изменений), у en — английский.

Прогон: .\\.venv\\Scripts\\python.exe smoke_232.py
"""
import asyncio
import os
import sys

_TEST_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_test_smoke232.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

passed = failed = 0


def check(name, cond):
    global passed, failed
    if cond:
        passed += 1
        print(f"  OK  {name}")
    else:
        failed += 1
        print(f"  FAIL: {name}")


class FakeBot:
    def __init__(self):
        self.sent = []

    async def send_message(self, chat_id, text, **kwargs):
        self.sent.append((chat_id, text))
        return None


async def run():
    from database.db import init_db, close_db, add_user, set_user_lang, set_news_chat
    from utils import notify as N
    from utils.notify import notify_t, notify_user_t, notify_award, praise_text_for

    await init_db()
    try:
        await add_user(501, "ru_pilot", "Иван", "")
        await add_user(502, "en_pilot", "John", "")
        await set_user_lang(502, "en")
        await set_news_chat(-100555, None)

        print("\n1. Общий чат: язык пилота, который прошёл подземелье")
        bot = FakeBot()
        await notify_t(bot, 502, "dungeon.notify.boss_won", who="John", boss="Rat King")
        await notify_t(bot, 501, "dungeon.notify.boss_won", who="Иван", boss="Крысиный король")
        check("en-пилот: сообщение на английском",
              "cleared the dungeon" in bot.sent[0][1] and "Rat King" in bot.sent[0][1])
        check("ru-пилот: сообщение на русском",
              "прошёл подземелье" in bot.sent[1][1] and "Крысиный король" in bot.sent[1][1])
        check("оба ушли в общий чат", all(c == -100555 for c, _ in bot.sent))

        print("\n2. Награда и похвала: язык пилота")
        bot = FakeBot()
        await notify_award(bot, {"username": "john", "first_name": "John", "user_id": 502},
                           "Medal", 502)
        check("награда en: «has been awarded»", "has been awarded" in bot.sent[0][1])
        check("похвала en (ace)", "true Ace" in (await praise_text_for(502, "John", 2)))
        check("похвала ru (mastery)", "высокое мастерство" in (await praise_text_for(501, "Иван", 1)))
        check("ниже порога — без текста", await praise_text_for(502, "John", 0) is None)

        print("\n3. Личное сообщение: язык получателя")
        bot = FakeBot()
        await notify_user_t(bot, 502, "pers.duty.add", label="Captain")
        await notify_user_t(bot, 501, "pers.duty.add", label="Капитан")
        check("личное en: в личку английский",
              bot.sent[0][0] == 502 and "given the post" in bot.sent[0][1])
        check("личное ru: в личку русский",
              bot.sent[1][0] == 501 and "Тебе присвоена должность" in bot.sent[1][1])
    finally:
        await close_db()


if __name__ == "__main__":
    asyncio.run(run())
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
