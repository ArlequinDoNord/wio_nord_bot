"""Smoke v0.18.1: отметка туристов 🎫 в меню выдачи/снятия статусов.

Гражданство = старший статус не ниже «Рекрута» (sort_order >= 1). Проверяем
всю границу: Турист отсекается, игрок вообще без статусов отсекается, Рекрут и
выше проходят, Хранитель (100) — тоже (он обычный пилот с повышенными правами,
а не служебное исключение). Плюс что метка НЕ протекает в посторонние
админские списки, где вызывается тот же самый сборщик клавиатуры.
"""
import asyncio
import os
import shutil
import sys
import tempfile

WORK = tempfile.mkdtemp(prefix="sm095_")
os.environ["DATABASE_PATH"] = os.path.join(WORK, "t.db")

from database import db as D
from bot.handlers.admin import pilot_picker_markup, _send_status_picker

FAILED = []


def check(name, cond):
    print(("  ok   " if cond else "  FAIL ") + name)
    if not cond:
        FAILED.append(name)


def labels(markup):
    return [b.text for row in markup.inline_keyboard for b in row]


class FakeChat:
    def __init__(self):
        self.text = None

    async def answer(self, text, **kw):
        self.text = text


async def sid(tag):
    conn = await D.get_db()
    row = await (await conn.execute(
        "SELECT id FROM statuses WHERE access_tag = ?", (tag,))).fetchone()
    return row["id"]


async def mkuser(uid, username, first):
    await D.add_user(uid, username, first, "")


async def main():
    await D.init_db()
    await D.ensure_base_statuses()

    # Турист — базовый статус из ensure_base_status
    await mkuser(1001, "tour1", "Турист Гость")
    await D.ensure_base_status(1001)

    # Гражданин: Рекрут
    await mkuser(1002, "cit1", "Гражданин Петр")
    await D.grant_status(1002, await sid("recruit"), 0)

    # Гражданин выше: Ветеран (остаётся и базовый Турист — старший побеждает)
    await mkuser(1003, "vet1", "Ветеран Вася")
    await D.ensure_base_status(1003)
    await D.grant_status(1003, await sid("recruit"), 0)
    await D.grant_status(1003, await sid("veteran"), 0)

    # Хранитель: обычный пилот с повышенными правами — гражданин
    await mkuser(1004, "keep1", "Хранитель Хоз")
    await D.grant_status(1004, await sid("keeper"), 0)

    # Вообще без статусов — тоже без гражданства
    await mkuser(1005, "nost1", "Без Статусов")

    citizens = await D.citizen_user_ids()
    check("турист — не гражданин", 1001 not in citizens)
    check("рекрут — гражданин", 1002 in citizens)
    check("ветеран — гражданин", 1003 in citizens)
    check("хранитель — гражданин (100, не режем)", 1004 in citizens)
    check("без статусов — не гражданин", 1005 not in citizens)

    texts = labels(await pilot_picker_markup("status_pick", mark_tourists=True))
    check("турист помечен 🎫", any("Турист Гость" in t and "🎫" in t for t in texts))
    check("без статусов помечен 🎫", any("Без Статусов" in t and "🎫" in t for t in texts))
    check("рекрут без метки", any("Гражданин Петр" in t and "🎫" not in t for t in texts))
    check("ветеран без метки", any("Ветеран Вася" in t and "🎫" not in t for t in texts))
    check("хранитель без метки", any("Хранитель Хоз" in t and "🎫" not in t for t in texts))
    check("метка в конце имени", any(t.strip().endswith("🎫") for t in texts))
    check("служебные кнопки на месте",
          any("Ввести вручную" in t for t in texts) and any("Отмена" in t for t in texts))

    for step in ("delphoto", "treasury_target", "wing", "state_target", "salary_set"):
        t2 = labels(await pilot_picker_markup(step))
        check(f"в «{step}» меток нет (обратная совместимость)", "🎫" not in "\n".join(t2))

    chat = FakeChat()
    await _send_status_picker(chat, await D.get_user(1001))
    check("экран туриста предупреждает", "🎫 Турист" in chat.text)
    check("на экране туриста нет **жирного** (нет parse_mode)", "**" not in chat.text)
    check("на экране туриста нет обещания про штаб", "Штаб" not in chat.text)

    chat2 = FakeChat()
    await _send_status_picker(chat2, await D.get_user(1002))
    check("экран гражданина без метки туриста", "🎫 Турист" not in chat2.text)
    check("экран гражданина показывает статус", "Рекрут" in chat2.text)

    await D.close_db()
    shutil.rmtree(WORK, ignore_errors=True)
    total = len(FAILED)
    print("\nSmoke 095: " + ("all passed" if not total else f"{total} failed"))
    sys.exit(1 if FAILED else 0)


asyncio.run(main())
