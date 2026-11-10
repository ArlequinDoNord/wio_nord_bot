# -*- coding: utf-8 -*-
"""Smoke 218 — раздел «Награды» в профиле: две вкладки.

1. В меню профиля одна кнопка «Награды», отдельной «Достижения» нет.
2. Вкладка «Достижения» (первая): ачивки с прогрессом, без медалей.
3. Вкладка «Награды» (вторая): медали, нашивки и значки — ВУСП и «Опытный турист».
4. Значки НЕ попадают на вкладку достижений, ачивки — НЕ попадают на вкладку наград.
5. Вкладки переключаются, активная отмечена «•», есть «В профиль».
6. Старая кнопка «Достижения» (profile:achievements) открывает вкладку достижений.
7. Английский интерфейс: вкладки переведены.
"""
import asyncio
import sys

from tests_support import Checker, use_test_db

_TEST_DB = use_test_db(__file__, "smoke218")

UID = 218001


class FakeMsg:
    def __init__(self):
        self.sent = []

    async def answer(self, text=None, reply_markup=None, **kw):
        self.sent.append((text, reply_markup))
        return True


class FakeCB:
    def __init__(self, uid, data=""):
        self.from_user = type("U", (), {"id": uid})()
        self.data = data
        self.message = FakeMsg()

    async def answer(self, *a, **kw):
        return True


async def main():
    check = Checker()

    from database.db import (
        init_db, close_db, add_user, ensure_achievements, bump_achievement,
        ensure_kvp_award, ensure_tourist_booklet, grant_award, get_db,
    )
    from config import TOURIST_BOOKLET_AWARD
    from bot.handlers import profile as pf
    from keyboards.keyboards import profile_keyboard
    from utils.i18n import _current

    await init_db()
    await ensure_achievements()
    await ensure_kvp_award()
    await ensure_tourist_booklet()
    await add_user(UID, 'aw', 'Награды', "")

    def cbs(kb):
        return [b.callback_data for row in kb.inline_keyboard for b in row]

    def texts(kb):
        return [b.text for row in kb.inline_keyboard for b in row]

    print("\n1. Кнопки профиля")
    pkb = profile_keyboard()
    pcbs = [b.callback_data for row in pkb.inline_keyboard for b in row]
    check("кнопка «Награды» есть", "profile:awards" in pcbs)
    check("отдельной «Достижения» нет", "profile:achievements" not in pcbs)

    print("\n2. Вкладка «Достижения» без ачивок")
    text0, kb0 = await pf.build_awards_tab(UID, "ach")
    check("пусто: «Нет полученных достижений»", "Нет полученных достижений" in text0)
    check("вкладки: достижения и награды", "profile:awards:ach" in cbs(kb0)
          and "profile:awards:awd" in cbs(kb0))
    check("активна вкладка «Достижения»", any(t.startswith("• ") and "Достижения" in t
                                              for t in texts(kb0)))
    check("есть «В профиль»", "profile:open" in cbs(kb0))

    print("\n3. Награды: медали и значки")
    conn = await get_db()
    cur = await conn.execute("SELECT id FROM awards WHERE name = ?", ("Значок В.У.С.П.",))
    row = await cur.fetchone()
    check("значок ВУСП заведён", row is not None)
    await grant_award(UID, row["id"])
    cur = await conn.execute("SELECT id FROM awards WHERE name = ?", (TOURIST_BOOKLET_AWARD,))
    row2 = await cur.fetchone()
    check("значок «Опытный турист» заведён", row2 is not None)
    await grant_award(UID, row2["id"])

    text_awd, kb_awd = await pf.build_awards_tab(UID, "awd")
    check("на вкладке наград есть ВУСП", "Значок В.У.С.П." in text_awd)
    check("на вкладке наград есть «Опытный турист»", TOURIST_BOOKLET_AWARD in text_awd)
    check("награда открывается карточкой (profile:award:<id>)",
          any(c and c.startswith("profile:award:") for c in cbs(kb_awd)))
    check("активна вкладка «Награды»", any(t.startswith("• ") and "Награды" in t
                                           for t in texts(kb_awd)))

    print("\n4. Разделение: значки не в достижениях, ачивки не в наградах")
    await bump_achievement(UID, "berries", 10)
    text_ach, _ = await pf.build_awards_tab(UID, "ach")
    check("достижения показаны", "🏅 ДОСТИЖЕНИЯ" in text_ach)
    check("значка ВУСП нет в достижениях", "Значок В.У.С.П." not in text_ach)
    check("значка туриста нет в достижениях", TOURIST_BOOKLET_AWARD not in text_ach)
    text_awd2, _ = await pf.build_awards_tab(UID, "awd")
    conn2 = await get_db()
    cur2 = await conn2.execute(
        "SELECT COUNT(*) AS c FROM user_awards ua JOIN awards a ON a.id = ua.award_id "
        "WHERE ua.user_id = ? AND a.achievement_key = 'berries'", (UID,))
    check("уровень ачивки реально выдан (как награда)", (await cur2.fetchone())["c"] >= 1)
    check("награда за уровень ачивки не попала в награды", "Уже не цветочки" not in text_awd2)
    check("награда за уровень ачивки видна в достижениях",
          "Собиратель ягод" in text_ach or "Уже не цветочки" in text_ach)
    check("в достижениях есть название и описание открытого уровня",
          "«Уже не цветочки»" in text_ach and "Уровень 1." in text_ach)
    check("на вкладке наград нет заголовка достижений", "🏅 ДОСТИЖЕНИЯ" not in text_awd2)

    print("\n5. Переключение вкладок")
    cb = FakeCB(UID, "profile:awards:awd")
    await pf.profile_awards_tab(cb)
    check("переключение открывает награды", cb.message.sent and "ТВОИ НАГРАДЫ" in cb.message.sent[0][0])
    cb2 = FakeCB(UID, "profile:awards:ach")
    await pf.profile_awards_tab(cb2)
    check("переключение открывает достижения",
          cb2.message.sent and "ДОСТИЖЕНИЯ" in cb2.message.sent[0][0])

    print("\n6. Старая кнопка «Достижения»")
    cb3 = FakeCB(UID, "profile:achievements")
    await pf.profile_achievements(cb3)
    check("старая кнопка открывает достижения",
          cb3.message.sent and "ДОСТИЖЕНИЯ" in cb3.message.sent[0][0])
    cb4 = FakeCB(UID, "profile:awards")
    await pf.profile_awards(cb4)
    check("«Награды» открывает вкладку достижений первой",
          cb4.message.sent and "ДОСТИЖЕНИЯ" in cb4.message.sent[0][0])

    print("\n7. Английский интерфейс")
    token = _current.set("en")
    try:
        _text_en, kb_en = await pf.build_awards_tab(UID, "ach")
        labels = texts(kb_en)
        check("en: вкладка «Achievements»", any("Achievements" in x for x in labels))
        check("en: вкладка «Awards»", any("Awards" in x for x in labels))
        check("en: «Back to profile»", any("Back to profile" in x for x in labels))
    finally:
        _current.reset(token)

    failed = check.summary()
    await close_db()
    return failed


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
