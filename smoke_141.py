"""Smoke v0.25.0: эмблема клана/партии при создании + личные уведомления.

Фича 1: в поток создания клана/партии добавлен шаг эмблемы. Раньше картинку
можно было задать только ПОСЛЕ создания (в меню «Редактировать»), из-за чего при
создании объединение всегда получалось без эмблемы. Теперь после описания бот
просит фото (необязательно) с кнопкой «⏭ Пропустить»; объединение создаётся на
последнем шаге (`_create_clan_finish`), поэтому «Отмена» на любом шаге не
оставляет пустой записи.

Фича 2: адресные (личные) уведомления о назначениях — новый `notify_user()`.
Раньше о назначении главы/должности/статуса/командира игрок никак не узнавал
(в чат уходят только общие публикации). `notify_user` шлёт в личку и НЕ зависит
от флага `notify_enabled` (это событие про самого игрока, а не публикация).

Проверяет:
1. `notify_user` реально шлёт в личку и возвращает True.
2. Нет цели (None/0) — молчит, не шлёт.
3. Ошибка отправки (бот заблокирован) — False, исключение не протекает.
4. `notify_user` не зовёт `notifications_enabled` (не зависит от флага).
5. Состояние `ClansCreate.wait_photo` объявлено.
6. В clans.py есть `_create_clan_finish`, обработчики фото/подсказки, skip-кнопка,
   сброс состояния на входе в список.
7. Точечные `notify_user` вызовы в clans.py / admin.py / hq.py + импорты.

Запуск: .venv\\Scripts\\python.exe smoke_141.py
"""
import asyncio
import os
import re
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(__file__))

_ROOT = os.path.dirname(os.path.abspath(__file__))


class FakeBot:
    """Минимальный бот: пишет отправленные сообщения (или падает)."""

    def __init__(self, fail=False):
        self.sent = []
        self.fail = fail

    async def send_message(self, chat_id, text, **kwargs):
        if self.fail:
            raise RuntimeError("bot was blocked by the user")
        self.sent.append((chat_id, text))
        return True


def _read(rel):
    return open(os.path.join(_ROOT, rel), encoding="utf-8").read()


def _body(src, name):
    """Тело функции/класса по имени (от объявления до следующего def/класса)."""
    m = re.search(rf"(?:async def|def|class) {re.escape(name)}\b.*?(?=\n(?:async def|def|class|@router) )",
                  src, re.DOTALL)
    return m.group(0) if m else ""


def run():
    passed = 0
    failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
            print(f"  ok   {name}")
        else:
            failed += 1
            print(f"  FAIL {name}")

    from utils.notify import notify_user

    # ── 1-3. Функциональная проверка notify_user ──
    loop = asyncio.new_event_loop()
    try:
        bot = FakeBot()
        ok = loop.run_until_complete(notify_user(bot, 111, "привет"))
        check("notify_user шлёт в личку и возвращает True",
              ok is True and bot.sent == [(111, "привет")])

        bot0 = FakeBot()
        check("notify_user(None) молчит", loop.run_until_complete(notify_user(bot0, None, "x")) is False)
        check("notify_user(0) молчит", loop.run_until_complete(notify_user(bot0, 0, "x")) is False)
        check("notify_user без цели ничего не отправил", bot0.sent == [])

        botfail = FakeBot(fail=True)
        check("ошибка отправки гасится, возврат False",
              loop.run_until_complete(notify_user(botfail, 222, "x")) is False)
    finally:
        loop.close()

    # ── 4. notify_user не зависит от notify_enabled ──
    notify_src = _read("utils/notify.py")
    check("notify_user определён", "async def notify_user" in notify_src)
    nu_body = _body(notify_src, "notify_user")
    check("notify_user не проверяет notifications_enabled",
          "notifications_enabled" not in nu_body)

    # ── 5-6. Поток создания с эмблемой ──
    clans = _read(os.path.join("bot", "handlers", "clans.py"))
    check("объявлено состояние ClansCreate.wait_photo", "wait_photo = State()" in clans)
    check("есть завершение создания _create_clan_finish", "async def _create_clan_finish" in clans)
    check("обработчик фото на шаге эмблемы (F.photo)", re.search(
        r"@router\.message\(ClansCreate\.wait_photo, F\.photo\)", clans) is not None)
    check("подсказка, если прислали не фото", "clan_create_photo_hint" in clans)
    check("кнопка «Пропустить» (clans:create_skip)", 'callback_data="clans:create_skip"' in clans)
    check("обработчик clans:create_skip", 'F.data == "clans:create_skip"' in clans)
    check("объединение создаётся только в _create_clan_finish",
          clans.count("await create_clan(") == 1 and "await create_clan(" in _body(clans, "_create_clan_finish"))
    check("фото сохраняется через update_clan(photo_file_id=...)",
          "update_clan(clan_id, photo_file_id=photo_file_id)" in clans)
    check("вход в список кланов сбрасывает FSM (state.clear)",
          "await state.clear()" in _body(clans, "clans_list_cb"))
    check("карточка объединения показывает фото",
          "photo=clan.get('photo_file_id')" in clans)

    # ── 7. Точечные уведомления и импорты ──
    def uses_notify_user(src, needle):
        return needle in src

    for mod, label in (("bot/handlers/clans.py", "кланы"),
                       ("bot/handlers/admin.py", "админка"),
                       ("bot/handlers/hq.py", "штаб")):
        src = _read(os.path.join(*mod.split("/")))
        check(f"{label}: notify_user импортирован", "notify_user" in src.split("router = ")[0])
        check(f"{label}: notify_user вызывается", "await notify_user(" in src)

    check("уведомление о назначении главы",
          'f"👑 Тебя назначили главой' in clans)
    check("уведомление о снятии главы", "👑 С тебя снята должность главы" in clans)
    check("уведомление о роспуске объединения", "распущено" in clans)

    admin = _read(os.path.join("bot", "handlers", "admin.py"))
    check("уведомление о должности (add/remove role)",
          "Тебе присвоена должность" in admin and "С тебя снята должность" in admin)
    check("уведомление о выдаче статуса", "Тебе присвоен статус" in admin)
    check("уведомление о легионере", "присвоен статус легионера" in admin)

    hq = _read(os.path.join("bot", "handlers", "hq.py"))
    check("уведомление командиру крыла", "Ты назначен командиром" in hq)
    check("уведомление заместителю крыла", "Ты назначен заместителем командира" in hq)

    print(f"\n{passed} passed, {failed} failed")
    return failed


if __name__ == "__main__":
    sys.exit(1 if run() else 0)
