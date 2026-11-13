# -*- coding: utf-8 -*-
"""Smoke 222 — проверка отчётов: причина отклонения и имя проверяющего.

Правила владельца (v0.43.17):
1. Отклонить отчёт без причины нельзя — бот спрашивает причину отдельным шагом.
2. Причина сохраняется в БД и видна пилоту: в карточке отчёта и в личном
   сообщении сразу после отклонения.
3. В отчёте пишется, КТО принял/отклонил — имя в боте (позывной/@username),
   а не Telegram ID. Для автоодобрения — «автоматически (система)».

Прогон: .\\.venv\\Scripts\\python.exe smoke_222.py
"""
import asyncio
import os
import sys
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke222.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB

sys.path.insert(0, os.path.dirname(__file__))


class FakeMessage:
    def __init__(self, text="", user_id=1):
        self.text = text
        self.photo = None
        self.from_user = SimpleNamespace(id=user_id, username=f"u{user_id}",
                                         full_name=f"User {user_id}")
        self.chat = SimpleNamespace(id=user_id)
        self.sent = []

    async def answer(self, *a, **kw):
        self.sent.append((a, kw))

    async def answer_photo(self, *a, **kw):
        self.sent.append((a, kw))

    async def edit_text(self, *a, **kw):
        self.sent.append((a, kw))


class FakeCallback:
    def __init__(self, user_id, data=""):
        self.from_user = SimpleNamespace(id=user_id, username=f"u{user_id}",
                                         full_name=f"User {user_id}")
        self.message = FakeMessage(user_id=user_id)
        self.data = data
        self.answers = []

    async def answer(self, *a, **kw):
        self.answers.append((a, kw))
        return True


class FakeBot:
    def __init__(self):
        self.messages = []

    async def send_message(self, chat_id, text, **kw):
        self.messages.append((chat_id, text))


class FakeState:
    def __init__(self):
        self._state = None
        self._data = {}

    async def get_state(self):
        return self._state

    async def set_state(self, s):
        self._state = s

    async def get_data(self):
        return dict(self._data)

    async def update_data(self, **kw):
        self._data.update({k: v for k, v in kw.items() if v is not None})

    async def clear(self):
        self._data.clear()
        self._state = None


def _texts(msg):
    return " ".join(str(a[0]) for a in msg.sent if a)


def _all_texts(msg):
    """Текст сообщений включая подписи к фото (caption)."""
    return _texts(msg) + " " + " ".join(str(kw.get("caption", "")) for _a, kw in msg.sent)


def _kb_texts(msg):
    """Тексты кнопок из всех отправленных сообщений."""
    out = []
    for _a, kw in msg.sent:
        markup = kw.get("reply_markup")
        if markup:
            for row in markup.inline_keyboard:
                out.extend(b.text for b in row)
    return " | ".join(out)


async def run():
    from database.db import (init_db, close_db, add_user, add_report, approve_report,
                             reject_report, get_user_reports, get_report_with_user,
                             get_rejected_reports_fresh, count_rejected_reports_fresh,
                             delete_rejected_report, get_db, set_callsign)
    from bot.handlers import admin as adm
    from bot.handlers.reports import report_card_text
    from utils import i18n

    await init_db()
    passed = failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
            print(f"  OK  {name}")
        else:
            failed += 1
            print(f"  FAIL: {name}")

    ADMIN = 9992221
    PILOT = 9992222
    PILOT2 = 9992223

    await add_user(ADMIN, "inspector", "Инспектор", "МВД")
    await set_callsign(ADMIN, "Инспектор")
    await add_user(PILOT, "pilot222", "Пилот", "Тестов")
    await add_user(PILOT2, "pilot223", "Второй", "Тестов")
    conn = await get_db()
    await conn.execute("INSERT INTO user_roles (telegram_id, role) VALUES (?, 'moderator')",
                       (ADMIN,))
    await conn.commit()

    print("\n1. Миграция: новые колонки отчёта")
    cols = [r["name"] for r in await (await conn.execute(
        "PRAGMA table_info(reports)")).fetchall()]
    check("есть reject_reason", "reject_reason" in cols)
    check("есть reviewed_by_name", "reviewed_by_name" in cols)
    check("есть reviewed_at", "reviewed_at" in cols)

    print("\n2. Отклонение без причины невозможно")
    rid, _ = await add_report(PILOT, "file", 500, 900, "0")
    st = FakeState()
    cb = FakeCallback(ADMIN, f"rep_no:{rid}")
    await adm.report_reject(cb, st)
    check("состояние «ждём причину»", st._state == adm.AdminReportReject.reason.state)
    check("просит причину", "ОТКЛОНЕНИЕ ОТЧЁТА" in _texts(cb.message))
    check("отчёт ещё не отклонён",
          (await get_report_with_user(rid))["status"] == "pending")

    msg = FakeMessage(text="   ", user_id=ADMIN)
    await adm.report_reject_reason(msg, st, FakeBot())
    check("пустая причина не принимается", "нельзя оставить пустой" in _texts(msg))
    check("состояние сохранено (можно повторить)",
          st._state == adm.AdminReportReject.reason.state)

    msg = FakeMessage(text="Профиль", user_id=ADMIN)
    await adm.report_reject_reason(msg, st, FakeBot())
    check("кнопка меню не стала причиной", "нельзя оставить пустой" in _texts(msg))

    msg = FakeMessage(text="ок", user_id=ADMIN)
    await adm.report_reject_reason(msg, st, FakeBot())
    check("слишком короткая причина отклонена", "Слишком коротко" in _texts(msg))
    check("отчёт всё ещё на проверке",
          (await get_report_with_user(rid))["status"] == "pending")

    print("\n3. Отклонение с причиной: причина в БД и у пилота")
    bot = FakeBot()
    msg = FakeMessage(text="Скриншот нечитаемый, цифры не разобрать", user_id=ADMIN)
    await adm.report_reject_reason(msg, st, bot)
    row = await get_report_with_user(rid)
    check("статус rejected", row["status"] == "rejected")
    check("причина сохранена", row["reject_reason"] == "Скриншот нечитаемый, цифры не разобрать")
    check("сохранён ID проверяющего", row["reviewed_by"] == ADMIN)
    check("сохранено имя проверяющего", row["reviewed_by_name"] == "Инспектор")
    check("состояние сброшено", st._state is None)
    check("подтверждение админу с именем",
          "Проверил: Инспектор" in _texts(msg) and "Причина: Скриншот" in _texts(msg))
    check("пилоту ушло личное сообщение", any(m[0] == PILOT for m in bot.messages))
    dm = next((m[1] for m in bot.messages if m[0] == PILOT), "")
    check("в личке есть причина", "Скриншот нечитаемый" in dm)
    check("в личке имя проверяющего", "Инспектор" in dm)
    check("в личке нет Telegram ID", str(ADMIN) not in dm)

    print("\n4. Карточка отчёта: имя проверяющего вместо ID")
    r = await get_report_with_user(rid)
    texts = [report_card_text(r),
             report_card_text(next(x for x in await get_user_reports(PILOT)
                                   if x["id"] == rid), include_author=False)]
    check("везде имя проверяющего",
          all("Проверил: Инспектор" in x for x in texts))
    check("нигде нет ID", all(str(ADMIN) not in x for x in texts))
    check("причина отклонения в карточке",
          all("Причина отклонения: Скриншот нечитаемый" in x for x in texts))

    print("\n5. Английский интерфейс")
    token = i18n._current.set("en")
    try:
        en_card = report_card_text(r)
        check("EN: Reviewed by", "Reviewed by: Инспектор" in en_card)
        check("EN: Rejection reason", "Rejection reason:" in en_card)
    finally:
        i18n._current.reset(token)

    print("\n6. Принятый отчёт: имя проверяющего тоже пишется")
    rid2, _ = await add_report(PILOT2, "file", 400, 400, "0")
    await approve_report(rid2, ADMIN)
    r2 = await get_report_with_user(rid2)
    check("статус approved", r2["status"] == "approved")
    check("имя проверяющего записано", r2["reviewed_by_name"] == "Инспектор")
    check("карточка показывает имя", "Проверил: Инспектор" in report_card_text(r2))

    print("\n7. Автоодобрение: без ID в карточке")
    rid3, _ = await add_report(PILOT2, "file", 50, 50, "0")
    await approve_report(rid3, 0)
    r3 = await get_report_with_user(rid3)
    check("reviewed_by = 0", r3["reviewed_by"] == 0)
    check("имени нет (система)", not r3["reviewed_by_name"])
    check("карточка: «автоматически»",
          "автоматически (система)" in report_card_text(r3))

    print("\n8. reject_report напрямую тоже сохраняет причину и имя")
    rid4, _ = await add_report(PILOT, "file", 700, 700, "0")
    await reject_report(rid4, ADMIN, reason="Дубликат отчёта")
    r4 = await get_report_with_user(rid4)
    check("причина сохранена", r4["reject_reason"] == "Дубликат отчёта")
    check("имя подставлено автоматически", r4["reviewed_by_name"] == "Инспектор")

    print("\n9. Вкладка «Отклонённые»: только свежие (неделя)")
    fresh = await get_rejected_reports_fresh()
    check("свежий отклонённый в списке", any(x["id"] == rid for x in fresh))
    check("счётчик свежих совпадает с длиной списка",
          await count_rejected_reports_fresh() == len(fresh))
    rid_old, _ = await add_report(PILOT, "file", 100, 100, "0")
    await reject_report(rid_old, ADMIN, reason="Старый отчёт")
    old_stamp = (datetime.now(timezone.utc) - timedelta(days=30)).strftime(
        "%Y-%m-%d %H:%M:%S")
    await conn.execute("UPDATE reports SET reviewed_at = ?, created_at = ? WHERE id = ?",
                       (old_stamp, old_stamp, rid_old))
    await conn.commit()
    fresh2 = await get_rejected_reports_fresh()
    check("старый (30 дней) не попадает в список",
          all(x["id"] != rid_old for x in fresh2))
    check("свежий остался в списке", any(x["id"] == rid for x in fresh2))

    print("\n10. Экран списка: что за отчёт, кто и за что отклонил")
    msg = FakeMessage(user_id=ADMIN)
    await adm.show_rejected_reports(msg, 0)
    list_text = _texts(msg)
    check("заголовок вкладки", "ОТКЛОНЁННЫЕ ОТЧЁТЫ" in list_text)
    check("в списке причина", "Скриншот нечитаемый" in list_text)
    check("в списке имя проверяющего", "Инспектор" in list_text)
    check("в списке нет Telegram ID", str(ADMIN) not in list_text)
    check("есть кнопка просмотра отчёта", "Отчёт #" in _kb_texts(msg))

    print("\n11. Карточка отклонённого отчёта")
    cb = FakeCallback(ADMIN, f"rep_rej_view:{rid}:0")
    await adm.rejected_report_view(cb)
    card_text = _all_texts(cb.message)
    check("карточка: статус rejected", "rejected" in card_text)
    check("карточка: причина", "Скриншот нечитаемый" in card_text)
    check("карточка: имя проверяющего", "Проверил: Инспектор" in card_text)
    check("карточка: время решения", "Отклонён:" in card_text)
    check("модератор не видит кнопку удаления",
          "Удалить" not in _kb_texts(cb.message))
    check("скриншот уходит фото-карточкой",
          any("photo" in kw for _a, kw in cb.message.sent))

    print("\n12. Удаление: только супер-админ")
    cb = FakeCallback(ADMIN, f"rep_rej_del:{rid}:0")
    await adm.rejected_report_delete_ask(cb)
    check("модератору удалять нельзя", "только супер-админ" in _texts(cb.message))
    check("отчёт не удалён", (await get_report_with_user(rid)) is not None)
    await conn.execute("INSERT INTO user_roles (telegram_id, role) VALUES (?, 'super_admin')",
                       (ADMIN,))
    await conn.commit()
    cb = FakeCallback(ADMIN, f"rep_rej_del:{rid}:0")
    await adm.rejected_report_delete_ask(cb)
    check("супер-админу предложено подтверждение",
          "УДАЛИТЬ ОТЧЁТ" in _texts(cb.message))
    check("есть кнопка подтверждения", "Да, удалить" in _kb_texts(cb.message))

    print("\n13. Удаление из списка отклонённых")
    check("принятый отчёт не удаляется", await delete_rejected_report(rid2) is False)
    check("принятый отчёт на месте", (await get_report_with_user(rid2)) is not None)
    cb = FakeCallback(ADMIN, f"rep_rej_del_ok:{rid}")
    await adm.rejected_report_delete(cb)
    check("отчёт удалён из БД", (await get_report_with_user(rid)) is None)
    check("подтверждение удаления", "удалён" in _texts(cb.message))
    check("в списке отклонённых его больше нет",
          all(x["id"] != rid for x in await get_rejected_reports_fresh()))
    check("свежий сосед (rid4) не тронут",
          any(x["id"] == rid4 for x in await get_rejected_reports_fresh()))

    print("\n14. Английский интерфейс вкладки")
    token = i18n._current.set("en")
    try:
        msg = FakeMessage(user_id=ADMIN)
        await adm.show_rejected_reports(msg, 0)
        check("EN: заголовок", "REJECTED REPORTS" in _texts(msg))
        check("EN: кнопка «Back to reports»", "Back to reports" in _kb_texts(msg))
    finally:
        i18n._current.reset(token)

    await close_db()
    print(f"\nИТОГО: {passed} passed, {failed} failed")
    return failed


if __name__ == "__main__":
    sys.exit(1 if asyncio.run(run()) else 0)
