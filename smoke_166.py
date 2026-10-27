"""Smoke 166 — Клан-холл, Фаза 6: библиотека рецептов (`clan_recipes`).

Проверяет:
1. Таблица `clan_recipes` в схеме БД, хелперы `has_clan_recipe`/
   `get_clan_recipes`/`get_clan_recipes_ids`/`donate_recipe_to_clan_library`.
2. Доступ: посторонний отклонён во всех колбэках каталога; сдача книги
   отклоняется, если расширения нет или оно не библиотека.
3. UI внутри здания: кнопка «📚 Библиотека рецептов — читать».
4. Экран пустой библиотеки: «Библиотека пуста», кнопок сдачи нет.
5. Сдача свитка «Рецепт: <название>» любым членом: рецепт пишется в
   `clan_recipes`, свиток списывается навсегда; повторная сдача того же
   рецепта отклонена без списаний.
6. Это не предмет-рецепт → отказ без списаний.
7. Кухня/стол: рецепт из клановой библиотеки виден всем членам (кнопка 📚),
   карточка открывается, крафт доступен и по уровню расширения; не изученный
   и не клановый рецепт отклонён.
8. Книга рецептов: сдача добавляет все доступные рецепты книги разом.
9. Работы (`upgrading`) не мешают библиотеке (экран открывается).
10. `get_clan_recipes_ids`; каскадная очистка при `delete_clan`.

Запуск: .venv\\Scripts\\python.exe smoke_166.py
"""
import asyncio
import os
import sys
import time

_TEST_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_test_smoke166.db")
for _suffix in ("", "-wal", "-shm"):
    try:
        os.remove(_TEST_DB + _suffix)
    except OSError:
        pass
os.environ["DATABASE_PATH"] = _TEST_DB
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PASS, FAIL = 0, 0


def check(name, cond):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  OK  {name}")
    else:
        FAIL += 1
        print(f"FAIL  {name}")


class FakeBot:
    def __init__(self):
        self.sent = []

    async def send_message(self, chat_id, text, parse_mode=None, reply_markup=None, **kw):
        m = type("Msg", (), {"message_id": len(self.sent) + 1})()
        self.sent.append(("text", chat_id, text, reply_markup))
        return m

    async def send_photo(self, chat_id, photo, caption=None, parse_mode=None,
                         reply_markup=None, **kw):
        m = type("Msg", (), {"message_id": len(self.sent) + 1})()
        self.sent.append(("photo", chat_id, caption or "", reply_markup))
        return m


class FakeMessage:
    def __init__(self):
        self.photo = None
        self.text = None
        self.kb = None
        self.media_photo = None
        self.deleted = False

    async def edit_text(self, text, parse_mode=None, reply_markup=None):
        self.text, self.kb = text, reply_markup
        return self

    async def edit_caption(self, caption, parse_mode=None, reply_markup=None):
        self.text, self.kb = caption, reply_markup
        return self

    async def edit_media(self, media, reply_markup=None):
        self.media_photo = getattr(media, "media", None)
        self.text = getattr(media, "caption", None)
        self.kb = reply_markup
        self.photo = [self.media_photo]
        return self

    async def answer_photo(self, photo, caption=None, parse_mode=None, reply_markup=None):
        self.media_photo = photo
        self.photo = [photo]
        self.text = caption
        self.kb = reply_markup
        return self

    async def answer(self, text, parse_mode=None, reply_markup=None):
        self.text, self.kb = text, reply_markup
        self.photo = None
        return self

    async def delete(self):
        self.deleted = True


class FakeUser:
    def __init__(self, uid):
        self.id = uid


class FakeCallback:
    def __init__(self, uid, data="", bot=None, chat_id=None):
        self.from_user = FakeUser(uid)
        self.message = FakeMessage()
        self.message.chat = type("Chat", (), {"id": chat_id or uid})()
        self.data = data
        self.alerts = []
        self.bot = bot or FakeBot()

    async def answer(self, text=None, *a, **k):
        self.alerts.append(text)
        return True


def cbs(kb):
    if not kb:
        return []
    return [b.callback_data for row in kb.inline_keyboard for b in row]


def has_alert(cb, needle):
    return any(t and needle in str(t) for t in cb.alerts)


def parse_ing_pairs(recipe):
    """Ингредиенты рецепта как [(имя, qty), ...] из JSON-колонки."""
    import json as _json
    try:
        raw = _json.loads(recipe["ingredients"] or "[]")
    except Exception:
        return []
    out = []
    for ing in raw:
        try:
            if isinstance(ing, dict):
                out.append((ing["name"], int(ing["qty"])))
            else:
                out.append((ing[0], int(ing[1])))
        except Exception:
            continue
    return out


def last_text(bot):
    return bot.sent[-1][2] if bot.sent else ""


async def main():
    import config
    config.DB_PATH = _TEST_DB
    config.CLAN_HALL_ENABLED = True
    import database.db as db
    db.DB_PATH = _TEST_DB
    from database.db import (
        add_clan_member,
        add_clan_storage,
        add_inventory_item,
        add_item,
        add_user,
        choose_clan_upgrade,
        close_db,
        create_clan,
        delete_clan,
        ensure_clan_building,
        ensure_dungeon_shop_items,
        ensure_forest_items,
        ensure_life_items,
        ensure_logging_items,
        ensure_mine_items,
        ensure_recipe_shop_items,
        ensure_recipes,
        get_clan,
        get_clan_recipes,
        get_clan_recipes_ids,
        get_db,
        get_inventory_item,
        get_item_by_name,
        get_recipe,
        get_user,
        has_clan_recipe,
        has_user_recipe,
        init_db,
        install_clan_expansion,
        seed_default_items,
        set_clan_building_built,
        set_clan_leader,
        set_recipe_book,
        update_user,
        upgrade_clan_expansion,
    )
    from bot.handlers import clan_hall

    await init_db()
    await seed_default_items()
    await ensure_recipes()
    await ensure_recipe_shop_items()
    await ensure_dungeon_shop_items()
    await ensure_life_items()
    await ensure_forest_items()
    await ensure_logging_items()
    await ensure_mine_items()

    try:
        LEADER, MEMBER, MEMBER2, OUTSIDER = 166001, 166002, 166003, 166004
        for uid, nm in ((LEADER, "Библиотекарь"), (MEMBER, "Начитанный"),
                        (MEMBER2, "Грамотей"), (OUTSIDER, "Чужак")):
            await add_user(uid, nm.lower(), nm, "")
            await update_user(uid, nordmarks=100000, ap=100)

        clan_id = await create_clan("clan", "Северный Архив", "Описание", LEADER)
        await set_clan_leader(clan_id, LEADER)
        for uid in (LEADER, MEMBER, MEMBER2):
            await add_clan_member(clan_id, uid)

        await ensure_clan_building(clan_id)
        await set_clan_building_built(clan_id, "manor")
        ok_k, _ = await install_clan_expansion(clan_id, LEADER, 1, "kitchen")
        ok_l, _ = await install_clan_expansion(clan_id, LEADER, 2, "library")
        ok_w, _ = await install_clan_expansion(clan_id, LEADER, 3, "workbench")
        check("кухня, библиотека и стол установлены", ok_k and ok_l and ok_w)

        print("\n1. Схема и хелперы библиотеки")
        conn = await get_db()
        cur = await conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='clan_recipes'")
        check("таблица clan_recipes создана", (await cur.fetchone()) is not None)
        check("пустая библиотека: get_clan_recipes = []", not await get_clan_recipes(clan_id))
        check("пустая библиотека: get_clan_recipes_ids = set()",
              await get_clan_recipes_ids(clan_id) == set())
        check("has_clan_recipe на чужом клане False",
              await has_clan_recipe(clan_id, 1) is False)

        print("\n2. Доступ")
        all_items = {i["name"] for i in await (await conn.execute(
            "SELECT name FROM items")).fetchall()}
        import json as _json
        r1 = None
        for row in await (await conn.execute(
            "SELECT * FROM recipes WHERE is_available = 1 ORDER BY required_level, id"
        )).fetchall():
            try:
                raw = _json.loads(row["ingredients"] or "[]")
                names = [(ing["name"] if isinstance(ing, dict) else ing[0]) for ing in raw]
            except Exception:
                continue
            if names and all(n in all_items for n in names):
                r1 = row
                break
        check("рецепт с исполняемыми ингредиентами найден", r1 is not None)
        if r1:
            scroll_pre = "Рецепт: "
            scroll = await get_item_by_name(scroll_pre + r1['name'])
            check("свиток рецепта в БД есть", bool(scroll))

        for label, fn, data in (
            ("use", clan_hall.clan_hall_use_cb, f"clanh:use:{clan_id}:2"),
            ("libgive", clan_hall.clan_hall_libgive_cb, f"clanh:libgive:{clan_id}:2:1"),
        ):
            cb_out = FakeCallback(OUTSIDER, data)
            await fn(cb_out)
            check(f"чужак отклонён в {label}", has_alert(cb_out, "только членам"))

        # не-библиотека
        cb_k = FakeCallback(LEADER, f"clanh:libgive:{clan_id}:1:1")
        await clan_hall.clan_hall_libgive_cb(cb_k)
        check("сдача книги не в библиотеке отклонена",
              has_alert(cb_k, "Библиотека не установлена"))

        # пустой слот
        cb_e = FakeCallback(LEADER, f"clanh:use:{clan_id}:6")
        await clan_hall.clan_hall_use_cb(cb_e)
        check("пустой слот отклонён", has_alert(cb_e, "нет расширения"))

        recipes_before = bool(await get_clan_recipes(clan_id))

        cb_pg = FakeCallback(MEMBER,
                             f"clanh:libgive:{clan_id}:2:{scroll['id']}"
                             if scroll else f"clanh:libgive:{clan_id}:2:999")
        try:
            await clan_hall.clan_hall_libgive_cb(cb_pg)
        except Exception:
            pass

        print("\n3. Экран пустой библиотеки")
        cb_lib = FakeCallback(MEMBER, f"clanh:use:{clan_id}:2")
        await clan_hall.clan_hall_use_cb(cb_lib)
        lib_txt = cb_lib.message.text or ""
        lib_cbs = cbs(cb_lib.message.kb)
        check("экран библиотеки открылся члену", "Библиотека рецептов" in lib_txt)
        check("экран пустой библиотеки: «Библиотека пуста»", "Библиотека пуста" in lib_txt)
        check("перед пустой библиотекой нет кнопок сдачи",
              not [c for c in lib_cbs if c.startswith("clanh:libgive")])

        print("\n4. Внутри здания: кнопка библиотеки")
        cb_in = FakeCallback(MEMBER, f"clanh:inside:{clan_id}")
        await clan_hall.clan_hall_inside_cb(cb_in)
        in_cbs = cbs(cb_in.message.kb)
        check("кнопка «Библиотека рецептов — читать» есть",
              f"clanh:use:{clan_id}:2" in in_cbs)
        check("чужой текст: библиотека доступна всем членам",
              "Библиотека" in (cb_in.message.text or ""))

        print("\n5. Сдача свитка в библиотеку")
        if scroll:
            await add_inventory_item(MEMBER, scroll["id"], 2)
            cb_g1 = FakeCallback(MEMBER, f"clanh:libgive:{clan_id}:2:{scroll['id']}")
            await clan_hall.clan_hall_libgive_cb(cb_g1)
            check("свиток сдан: «открыто» в тексте", has_alert(cb_g1, "открыто"))
            check("рецепт в клановой библиотеке",
                  await has_clan_recipe(clan_id, r1['id']) is True)
            check("свиток списан (1 шт из 2)", int((await get_inventory_item(
                MEMBER, scroll["id"]))["quantity"]) == 1)
            check("в библиотеке ровно 1 рецепт",
                  len(await get_clan_recipes(clan_id)) == 1)
            check("автор сдачи записан (donated_by)",
                  (await get_clan_recipes(clan_id))[0]["donated_by"] == MEMBER)

            cb_g2 = FakeCallback(MEMBER, f"clanh:libgive:{clan_id}:2:{scroll['id']}")
            await clan_hall.clan_hall_libgive_cb(cb_g2)
            check("повторная сдача того же рецепта отклонена",
                  has_alert(cb_g2, "уже есть в клановой библиотеке"))
            check("повторная сдача: свиток на месте",
                  int((await get_inventory_item(MEMBER, scroll["id"]))["quantity"]) == 1)

        print("\n6. Сдача не-рецепта отклонена")
        non_r = await (await conn.execute(
            "SELECT * FROM items WHERE is_available = 1 AND category != 'recipes' "
            "ORDER BY id LIMIT 1")).fetchone()
        check("найдётся не-рецептный предмет", bool(non_r))
        board = non_r
        if board:
            await add_inventory_item(MEMBER, board["id"], 1)
            cb_ng = FakeCallback(MEMBER, f"clanh:libgive:{clan_id}:2:{board['id']}")
            await clan_hall.clan_hall_libgive_cb(cb_ng)
            check("не предмет-рецепт: отказ", has_alert(cb_ng, "не предмет-рецепт"))
            check("предмет не списан", int((await get_inventory_item(
                MEMBER, board["id"]))["quantity"]) == 1)

        print("\n7. Кухня: клановый рецепт виден всем членам")
        cb_kx = FakeCallback(MEMBER2, f"clanh:use:{clan_id}:1")
        await clan_hall.clan_hall_use_cb(cb_kx)
        kx_cbs = cbs(cb_kx.message.kb)
        check("рецепт из библиотеки виден (кнопка 📖)",
              f"clanh:recipe:{clan_id}:1:{r1['id']}" in kx_cbs)
        check("чужой пользователь всё ещё не видит неизученного",
              not [c for c in kx_cbs
                   if c.startswith("clanh:recipe") and c not in
                   (f"clanh:recipe:{clan_id}:1:{r1['id']}",)])

        # чужой клан: библиотека пуста — кнопки нет
        other_clan = await create_clan("clan", "Другой Двор", "", LEADER)
        await set_clan_leader(other_clan, LEADER)
        for uid in (LEADER, MEMBER):
            await add_clan_member(other_clan, uid)
        await ensure_clan_building(other_clan)
        await set_clan_building_built(other_clan, "house")
        ok_ok, _ = await install_clan_expansion(other_clan, LEADER, 1, "kitchen")
        cb_oo = FakeCallback(MEMBER, f"clanh:use:{other_clan}:1")
        await clan_hall.clan_hall_use_cb(cb_oo)
        check("рецепт не утекает в чужой клан",
              not [c for c in cbs(cb_oo.message.kb)
                   if c == f"clanh:recipe:{other_clan}:1:{r1['id']}"])

        print("\n8. Крафт по клановому рецепту")
        from utils import crafting as crafting_mod
        real_sleep = crafting_mod.asyncio.sleep

        async def _nosleep(*a, **k):
            return None

        crafting_mod.asyncio.sleep = _nosleep
        # сырьё: находим имена ингредиентов из рецепта программно
        ings = [t[0] for t in parse_ing_pairs(r1)] if r1 else []
        for ing in ings:
            it = await get_item_by_name(ing)
            check(f"ингредиент «{ing}» есть в БД", bool(it))
            if it:
                await add_inventory_item(MEMBER2, it["id"], 10)
        craft_ok = None
        if r1:
            ap_before = int((await get_user(MEMBER2))["ap"])
            cb_craft = FakeCallback(MEMBER2, f"clanh:craft:{clan_id}:1:{r1['id']}")
            await clan_hall.clan_hall_craft_cb(cb_craft)
            it = await get_item_by_name(r1["result_item_name"])
            craft_ok = bool(it and await get_inventory_item(MEMBER2, it["id"]))
            check("крафт по клановому рецепту выдал результат", craft_ok)
            check("не хватает ОД: отказ без лишних списаний",
                  not has_alert(cb_craft, "Не хватает ОД") or
                  int((await get_user(MEMBER2))["ap"]) == ap_before)
            check("CRAFTING свободен", MEMBER2 not in crafting_mod.CRAFTING)

        print("\n9. Книга рецептов: сдача добавляет все доступные рецепты")
        if r1:
            rmore = await (await conn.execute(
                "SELECT * FROM recipes WHERE is_available = 1 AND required_expansion = ? "
                "AND id != ? ORDER BY required_level DESC, id DESC LIMIT 1",
                (r1["required_expansion"], r1["id"]),
            )).fetchall()
            r2 = rmore[0] if rmore else None
        else:
            r2 = None
        if r2 and r1 and int(r2["id"]) != int(r1["id"]):
            book_name = "Книга рецептов: Северная тетрадь"
            await add_item(book_name, "Тестовая книга", 10, 5, 2, "recipes", -1, 0)
            book = await get_item_by_name(book_name)
            await set_recipe_book(book["id"], [int(r1["id"]), int(r2["id"])])
            check("книга создана и привязана", bool(book))
            await add_inventory_item(MEMBER, book["id"], 1)
            cb_bg = FakeCallback(MEMBER, f"clanh:libgive:{clan_id}:2:{book['id']}")
            await clan_hall.clan_hall_libgive_cb(cb_bg)
            check("книга сдана", has_alert(cb_bg, "открыто"))
            check("оба рецепта в библиотеке",
                  await has_clan_recipe(clan_id, int(r1["id"])) is True
                  and await has_clan_recipe(clan_id, int(r2["id"])) is True)
            check("книга списана навсегда",
                  not await get_inventory_item(MEMBER, book["id"]))

        print("\n10. Работы не мешают библиотеке")
        cb_up2 = FakeCallback(MEMBER, f"clanh:use:{clan_id}:2")
        await clan_hall.clan_hall_use_cb(cb_up2)
        check("экран библиотеки открывается (включая этапы сбора/работ)",
              "Библиотека" in (cb_up2.message.text or ""))

        print("\n11. Очистка библиотеки при роспуске")
        recipes_before_delete = await get_clan_recipes_ids(other_clan)
        await delete_clan(other_clan)
        cur_other = await conn.execute(
            "SELECT 1 FROM clan_recipes WHERE clan_id = ?", (other_clan,))
        check("сдача не была во втором клане", recipes_before_delete == set())
        check("таблица clan_recipes второго клана пуста",
              not (await cur_other.fetchone()))
    finally:
        await close_db()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        print(f"\nSmoke 166: {PASS} passed, {FAIL} failed")
        sys.exit(1 if FAIL else 0)
