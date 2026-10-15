"""Smoke 146 — раздел «Партии и кланы»: свёрнутый список по категориям.

Раньше на экране раздела висел плоский список всех объединений — кнопка на каждый
клан/партию (плюс создание и выход). С ростом числа объединений раздел становился
громоздким. Теперь верхний экран — только две кнопки-категории («Список партий»,
«Список кланов»), а сам список открывается по своей кнопке.

Проверяет:
1. Сводный экран: текстом — счётчики партий и кланов, кнопками — ровно
   «Список партий» (clans:list:party), «Список кланов» (clans:list:clan), «В Ратушу»
   (city:pilots); НИ ОДНОЙ кнопки-объединения (clans:view:) на нём нет.
2. Категорийный экран партий: перечислены партии, есть кнопки `clans:view:`, у
   админа — «Создать партию», возврат `city:clans`.
3. Категорийный экран кланов: аналогично, «Создать клан».
4. Роутинг `clans:list:<kind>` открывает нужную категорию.
5. Без прав `can_manage_clans` кнопки создания нет.
6. Пустая категория — «пока пусто», кнопка категории всё равно доступна сверху.

Запуск: .venv\\Scripts\\python.exe smoke_146.py
"""
import asyncio
import os
import sys

_TEST_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_test_smoke146.db")
for _suffix in ("", "-wal", "-shm"):
    try:
        os.remove(_TEST_DB + _suffix)
    except OSError:
        pass
os.environ["DATABASE_PATH"] = _TEST_DB
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

PASS, FAIL = 0, 0


def check(name, cond):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  OK  {name}")
    else:
        FAIL += 1
        print(f"FAIL  {name}")


class FakeMessage:
    def __init__(self):
        self.photo = None
        self.text = None
        self.kb = None

    async def edit_text(self, text, parse_mode=None, reply_markup=None):
        self.text, self.kb = text, reply_markup

    async def edit_caption(self, caption, parse_mode=None, reply_markup=None):
        self.text, self.kb = caption, reply_markup


class FakeUser:
    def __init__(self, uid):
        self.id = uid


class FakeCallback:
    def __init__(self, uid, data=""):
        self.from_user = FakeUser(uid)
        self.message = FakeMessage()
        self.data = data

    async def answer(self, *a, **k):
        return True


def cbs(kb):
    return [b.callback_data for row in kb.inline_keyboard for b in row]


def texts(kb):
    return [b.text for row in kb.inline_keyboard for b in row]


async def main():
    import config
    config.DB_PATH = _TEST_DB
    import database.db as db
    db.DB_PATH = _TEST_DB
    from database.db import init_db, close_db, add_user, create_clan
    from bot.handlers import clans

    await init_db()
    ADMIN = 146000
    await add_user(ADMIN, "adm", "Админ", "")

    await create_clan("clan", "Северный Легион", "", ADMIN)
    await create_clan("party", "Партия Исследователей", "", ADMIN)
    await create_clan("party", "Союз Рыбаков", "", ADMIN)

    orig_perm = clans.has_permission

    async def _perm(uid, code, *a, **k):
        return code == "can_manage_clans"

    clans.has_permission = _perm

    try:
        print("\n1. Сводный экран: только две категории")
        cb = FakeCallback(ADMIN)
        await clans._show_clans_list(cb)
        txt = cb.message.text
        c = cbs(cb.message.kb)
        t = texts(cb.message.kb)
        check("текст: счётчик партий", "Партий: 2" in txt)
        check("текст: счётчик кланов", "Кланов: 1" in txt)
        check("есть кнопка «Список партий»", "clans:list:party" in c)
        check("есть кнопка «Список кланов»", "clans:list:clan" in c)
        check("есть возврат в Ратушу", "city:pilots" in c)
        check("на сводном экране НЕТ кнопок-объединений",
              not any(x.startswith("clans:view:") for x in c))
        check("сводный экран — ровно 3 кнопки", len(c) == 3)
        check("кнопка партий показывает счётчик", any("Список партий (2)" in x for x in t))

        print("\n2. Категория «партии»: список и создание")
        cb = FakeCallback(ADMIN, "clans:list:party")
        await clans.clans_list_kind_cb(cb)
        c = cbs(cb.message.kb)
        check("роутинг clans:list:party открыл партии",
              "ПАРТИИ" in cb.message.text or "Партии" in cb.message.text)
        check("партии перечислены (2 кнопки clans:view:)",
              sum(1 for x in c if x.startswith("clans:view:")) == 2)
        check("есть «Создать партию»", "clans:create:party" in c)
        check("создание клана тут не предлагается", "clans:create:clan" not in c)
        check("возврат к партиям и кланам", "city:clans" in c)

        print("\n3. Категория «кланы»: список и создание")
        cb = FakeCallback(ADMIN, "clans:list:clan")
        await clans.clans_list_kind_cb(cb)
        c = cbs(cb.message.kb)
        check("роутинг clans:list:clan открыл кланы", "КЛАНЫ" in cb.message.text)
        check("клан перечислен (1 кнопка clans:view:)",
              sum(1 for x in c if x.startswith("clans:view:")) == 1)
        check("есть «Создать клан»", "clans:create:clan" in c)
        check("создание партии тут не предлагается", "clans:create:party" not in c)

        print("\n4. Без прав создания кнопки нет")
        async def _perm_no(uid, code, *a, **k):
            return False
        clans.has_permission = _perm_no
        cb = FakeCallback(ADMIN, "clans:list:clan")
        await clans.clans_list_kind_cb(cb)
        c = cbs(cb.message.kb)
        check("нет кнопки создания без прав",
              "clans:create:clan" not in c and "clans:create:party" not in c)
        check("список всё равно показан",
              sum(1 for x in c if x.startswith("clans:view:")) == 1)

        print("\n5. Пустая категория")
        # Отдельная временная проверка: удаляем все партии.
        from database.db import get_clans, delete_clan
        for p in await get_clans("party"):
            await delete_clan(p["id"])
        clans.has_permission = _perm
        cb = FakeCallback(ADMIN, "clans:list:party")
        await clans.clans_list_kind_cb(cb)
        check("пустая партия: «пока пусто»", "пока пусто" in cb.message.text)
        check("пустая партия: нет кнопок-объединений",
              not any(x.startswith("clans:view:") for x in cbs(cb.message.kb)))
        # Сводный экран всё равно предлагает обе категории.
        cb = FakeCallback(ADMIN)
        await clans._show_clans_list(cb)
        check("сводный экран с пустыми партиями показывает 0",
              "Партий: 0" in cb.message.text)
    finally:
        clans.has_permission = orig_perm
        await close_db()

    print(f"\nSmoke 146: {PASS} passed, {FAIL} failed")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except SystemExit:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"SMOKE ERROR: {e}")
        sys.exit(2)
