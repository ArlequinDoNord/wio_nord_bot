# -*- coding: utf-8 -*-
"""Smoke 234 — общий счётчик руды первого уровня и открытие второго уровня.

- стартовое значение берётся из журнала (железная + пламенная руда, киркой);
- второй уровень открывается ровно при достижении порога и только один раз;
- объявление уходит в общий чат.

Прогон: .\\.venv\\Scripts\\python.exe smoke_234.py
"""
import asyncio
import os
import sys

_TEST_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_test_smoke234.db")
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
    from config import MINE_LEVEL2_ORE_TARGET, MINE_ORE_NAME, FIRE_ORE_NAME
    from database.db import init_db, close_db, log_activity, set_news_chat, add_user
    from utils import mine_progress as M

    await init_db()
    try:
        await add_user(801, "p801", "P801", "")
        await add_user(802, "p802", "P802", "")
        print("\n1. Стартовое значение из журнала")
        await log_activity(801, "mine", f"Добыл «{MINE_ORE_NAME}»")
        await log_activity(801, "mine", f"Добыл «{MINE_ORE_NAME}»")
        await log_activity(802, "mine", f"Добыл «{FIRE_ORE_NAME}»")
        await log_activity(802, "mine", "Добыча руды: удар киркой (12 ОД)")
        check("журнал даёт 2 руды: пламенная не считается, удары тоже",
              await M.get_ore_total() == 2)
        check("второй уровень ещё закрыт", not await M.is_level2_open())

        print("\n2. Открытие ровно на пороге")
        need = MINE_LEVEL2_ORE_TARGET - 2
        opened_before = await M.add_ore(need - 1)
        check("до порога не открывается", not opened_before and not await M.is_level2_open())
        opened_now = await M.add_ore(1)
        check("на пороге открывается", opened_now is True)
        check("флаг открытия стоит", await M.is_level2_open())

        print("\n3. Однократность")
        check("после открытия повторно не открывается", await M.add_ore(5) is False)

        print("\n4. Объявление в общий чат")
        await set_news_chat(-100777, None)
        bot = FakeBot()
        await M.announce_level2(bot)
        check("в чат ушло объявление", any(c == -100777 and str(MINE_LEVEL2_ORE_TARGET) in t
                                          for c, t in bot.sent))
    finally:
        await close_db()


if __name__ == "__main__":
    asyncio.run(run())
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
