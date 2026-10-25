"""Smoke 160 — менеджер рецептов: визард свитка/книги, пикер каталога, книги рецептов.

Проверяет:
1. Таблицу `recipe_book_items` и префикс предмета-книги `BOOK_ITEM_PREFIX`.
2. Полный визард свитка: тип → название → описание → состав из каталога
   (ингредиент + количество, добавление/обновление/удаление, «добавить ещё»)
   → результат из каталога → расширение/уровень/ОД/время/редкость/кол-во/цена → сохранение.
3. Пикер состава и результата: категории берутся из каталога, служебные
   (`recipes`, `market`, `duel_card`, `license`) не показываются, в том числе
   в «Все предметы».
4. Дубликат рецепта (имя + расширение + уровень) не создаётся.
5. Хелперы книг: `set_recipe_book` (дедупликация), `get_recipe_book_recipes`,
   `list_recipe_books`, `set_recipe_book_visible`, `delete_recipe_book`.
6. Обучение по предметам: свиток учит один рецепт и списывается; повторное
   использование уже выученного свитка не списывает предмет; книга учит все
   свои рецепты, пропускает уже выученные, не списывается, если учить нечего.
7. Визард книги: выбор готовых рецептов (минимум один), цена, создание предмета,
   список/карточка/показ-скрытие/мягкое удаление, цена 0 → книга скрыта.
8. Правка состава рецепта (`recadm:ei:`) через тот же пикер каталога.
9. Отказ в доступе без прав `can_manage_shop`.

Запуск: .venv\\Scripts\\python.exe smoke_160.py
"""
import asyncio
import json
import os
import sys
from types import SimpleNamespace

_TEST_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_test_smoke160.db")
for _suffix in ("", "-wal", "-shm"):
    try:
        os.remove(_TEST_DB + _suffix)
    except OSError:
        pass
os.environ["DATABASE_PATH"] = _TEST_DB
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ADMIN_UID = 560160
LEARNER = 560161
LEARNER2 = 560162
LEARNER3 = 560163
OUTSIDER = 560164

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

    async def send_message(self, chat_id, text, parse_mode=None, reply_markup=None):
        self.sent.append((chat_id, text))
        return True


class FakeMessage:
    def __init__(self, text=None, uid=ADMIN_UID):
        self.photo = None
        self.text = text
        self.kb = None
        self.from_user = SimpleNamespace(id=uid)

    async def answer(self, text, parse_mode=None, reply_markup=None):
        self.text, self.kb = text, reply_markup
        self.photo = None
        return self

    async def edit_text(self, text, parse_mode=None, reply_markup=None):
        self.text, self.kb = text, reply_markup
        return self

    async def edit_caption(self, caption, parse_mode=None, reply_markup=None):
        self.text, self.kb = caption, reply_markup
        return self

    async def delete(self):
        return True


class Callback:
    def __init__(self, uid, data="", message=None):
        self.from_user = SimpleNamespace(id=uid)
        self.message = message or FakeMessage(uid=uid)
        self.data = data
        self.alerts = []
        self.bot = FakeBot()

    async def answer(self, text=None, *a, **k):
        self.alerts.append(text)
        return True


class FakeState:
    def __init__(self):
        self.data = {}
        self.state = None

    async def get_data(self):
        return dict(self.data)

    async def update_data(self, **kw):
        self.data.update(kw)

    async def set_state(self, s):
        self.state = s

    async def clear(self):
        self.data = {}
        self.state = None


def cbs(kb):
    if not kb:
        return []
    return [b.callback_data for row in kb.inline_keyboard for b in row]


async def main():
    import config
    # until utils.permissions imports ADMIN_IDS; мутируем список до импорта handlers.
    config.ADMIN_IDS = [ADMIN_UID]
    config.DB_PATH = _TEST_DB
    import database.db as db
    db.DB_PATH = _TEST_DB
    from database.db import (
        init_db, close_db, get_db, add_user, add_item, get_item, get_item_by_name,
        add_inventory_item, get_inventory_item, get_items_by_category,
        upsert_recipe, get_recipe, find_recipe,
        BOOK_ITEM_PREFIX, RECIPE_ITEM_PREFIX,
        set_recipe_book, get_recipe_book_recipes, list_recipe_books,
        set_recipe_book_visible, delete_recipe_book,
        learn_recipe_from_item, learn_recipe, has_user_recipe,
        ensure_recipe_shop_items,
    )
    from bot.handlers import admin_recipes as ar

    await init_db()

    for uid, nm in ((ADMIN_UID, "admin"), (LEARNER, "learner"),
                    (LEARNER2, "learner2"), (LEARNER3, "learner3"),
                    (OUTSIDER, "outsider")):
        await add_user(uid, nm, nm.title(), "")

    try:
        print("\n1. Схема и константы книг")
        conn = await get_db()
        cur = await conn.execute("PRAGMA table_info(recipe_book_items)")
        cols = {r["name"] for r in await cur.fetchall()}
        check("таблица recipe_book_items создана",
              cols == {"book_item_id", "recipe_id"})
        check("префикс книги рецептов", BOOK_ITEM_PREFIX == "Книга рецептов: ")

        print("\n2. Визард свитка: тип → название → описание → состав")
        ing1 = await add_item("AAA-Ингредиент", "тест", 0, 0, 1, "resource",
                              100, ADMIN_UID)
        ing2 = await add_item("AAB-Ингредиент2", "тест", 0, 0, 1, "resource",
                              100, ADMIN_UID)
        result_item = await add_item("AAA-Результат", "тест", 10, 5, 2,
                                     "consumable", 100, ADMIN_UID)
        # Служебные категории: не должны попадать в пикер состава/результата.
        svc_recipe = await add_item("AAA-Служебный рецепт", "тест", 0, 0, 1,
                                    "recipes", -1, ADMIN_UID)
        svc_license = await add_item("AAA-Лицензия", "тест", 0, 0, 1,
                                     "license", 1, ADMIN_UID)
        svc_market = await add_item("AAA-Рыночный лот", "тест", 0, 0, 1,
                                    "market", 1, ADMIN_UID)
        svc_duel = await add_item("AAA-Дуэльная карта", "тест", 0, 0, 1,
                                  "duel_card", 1, ADMIN_UID)
        service_ids = {svc_recipe, svc_license, svc_market, svc_duel}

        st = FakeState()
        cb = Callback(ADMIN_UID, "recadm:create")
        await ar.recadm_create(cb, st)
        check("создание начинается с выбора типа",
              "recadm:kind:scroll" in cbs(cb.message.kb)
              and "recadm:kind:book" in cbs(cb.message.kb))

        cb = Callback(ADMIN_UID, "recadm:kind:scroll")
        await ar.recadm_kind(cb, st)
        check("после выбора свитка спрашивается название",
              st.state == ar.RecipeManager.c_name and "НАЗВАНИЕ" in cb.message.text)

        m = FakeMessage("AAA-Блюдо")
        await ar.recadm_c_name(m, st)
        check("после названия спрашивается описание",
              st.state == ar.RecipeManager.c_desc and "Описание" in m.text)

        m = FakeMessage("Тестовое описание")
        await ar.recadm_c_desc(m, st)
        cat_cbs = cbs(m.kb)
        check("после описания открывается состав по категориям",
              st.state == ar.RecipeManager.c_ing_cat
              and "recadm:ingcat:resource:0" in cat_cbs
              and "recadm:ingcat:all:0" in cat_cbs)
        check("в категориях состава нет служебных",
              not any(x in cat_cbs for x in (
                  "recadm:ingcat:recipes:0", "recadm:ingcat:market:0",
                  "recadm:ingcat:license:0", "recadm:ingcat:duel_card:0")))

        cb = Callback(ADMIN_UID, "recadm:ingcat:resource:0")
        await ar.recadm_ing_cat(cb, st)
        check("категория ресурсов показывает предметы каталога",
              f"recadm:ingpick:{ing1}" in cbs(cb.message.kb)
              and f"recadm:ingpick:{ing2}" in cbs(cb.message.kb))

        cb = Callback(ADMIN_UID, "recadm:ingcat:all:0")
        await ar.recadm_ing_cat(cb, st)
        all_pick = cbs(cb.message.kb)
        check("«Все предметы» не содержит служебных предметов",
              not any(f"recadm:ingpick:{i}" in all_pick for i in service_ids))

        cb = Callback(ADMIN_UID, f"recadm:ingpick:{ing1}")
        await ar.recadm_ing_pick(cb, st)
        check("после выбора ингредиента спрашивается количество",
              st.state == ar.RecipeManager.c_ing_qty
              and "Сколько" in cb.message.text)

        m = FakeMessage("2")
        await ar.recadm_c_ing_qty(m, st)
        d = (await st.get_data())["d"]
        check("ингредиент добавлен с количеством",
              d["ingredients"] == [["AAA-Ингредиент", 2]])
        check("после количества предлагается добавить ещё или закончить",
              "recadm:ing_more" in cbs(m.kb) and "recadm:ing_done" in cbs(m.kb))

        await ar.recadm_ing_more(Callback(ADMIN_UID, "recadm:ing_more"), st)
        await ar.recadm_ing_pick(
            Callback(ADMIN_UID, f"recadm:ingpick:{ing2}"), st)
        m2 = FakeMessage("2")
        await ar.recadm_c_ing_qty(m2, st)
        d = (await st.get_data())["d"]
        check("второй ингредиент добавлен",
              ["AAB-Ингредиент2", 2] in d["ingredients"])

        # Повторный выбор того же предмета: 0 — убрать, затем 3 — обновить.
        await ar.recadm_ing_pick(
            Callback(ADMIN_UID, f"recadm:ingpick:{ing2}"), st)
        m3 = FakeMessage("0")
        await ar.recadm_c_ing_qty(m3, st)
        d = (await st.get_data())["d"]
        check("количество 0 убирает ингредиент",
              ["AAB-Ингредиент2", 2] not in d["ingredients"]
              and "убран" in m3.text)

        await ar.recadm_ing_pick(
            Callback(ADMIN_UID, f"recadm:ingpick:{ing2}"), st)
        m4 = FakeMessage("3")
        await ar.recadm_c_ing_qty(m4, st)
        d = (await st.get_data())["d"]
        check("повторный выбор обновляет количество",
              d["ingredients"] == [["AAA-Ингредиент", 2],
                                   ["AAB-Ингредиент2", 3]])

        cb = Callback(ADMIN_UID, "recadm:ing_done")
        await ar.recadm_ing_done(cb, st)
        check("состав готов → выбор результата",
              st.state == ar.RecipeManager.res_mode
              and "recadm:res_existing" in cbs(cb.message.kb))

        print("\n3. Результат из каталога и параметры рецепта")
        cb = Callback(ADMIN_UID, "recadm:res_existing")
        await ar.recadm_res_existing(cb, st)
        res_cbs = cbs(cb.message.kb)
        check("категории результата без служебных",
              "recadm:rescat:consumable:0" in res_cbs
              and not any(x in res_cbs for x in (
                  "recadm:rescat:recipes:0", "recadm:rescat:market:0",
                  "recadm:rescat:license:0", "recadm:rescat:duel_card:0")))

        cb = Callback(ADMIN_UID, "recadm:rescat:consumable:0")
        await ar.recadm_res_cat(cb, st)
        check("предмет-результат выбирается из каталога",
              f"recadm:respick:{result_item}" in cbs(cb.message.kb))

        cb = Callback(ADMIN_UID, f"recadm:respick:{result_item}")
        await ar.recadm_res_pick(cb, st)
        check("после результата спрашивается расширение",
              st.state == ar.RecipeManager.c_exp
              and "recadm:exp:kitchen" in cbs(cb.message.kb))

        cb = Callback(ADMIN_UID, "recadm:exp:kitchen")
        await ar.recadm_exp(cb, st)
        check("после расширения спрашивается уровень",
              st.state == ar.RecipeManager.c_lvl
              and "recadm:lvl:2" in cbs(cb.message.kb))

        await ar.recadm_lvl(Callback(ADMIN_UID, "recadm:lvl:2"), st)
        check("после уровня спрашиваются ОД", st.state == ar.RecipeManager.c_ap)
        m = FakeMessage("7")
        await ar.recadm_c_ap(m, st)
        check("после ОД спрашивается время", st.state == ar.RecipeManager.c_time)
        m = FakeMessage("45")
        await ar.recadm_c_time(m, st)
        check("после времени спрашивается редкость",
              st.state == ar.RecipeManager.c_rarity)

        await ar.recadm_rar(Callback(ADMIN_UID, "recadm:rar:3"), st)
        check("после редкости спрашивается количество",
              st.state == ar.RecipeManager.c_qty)
        m = FakeMessage("2")
        await ar.recadm_c_qty(m, st)
        check("после количества спрашивается цена товара-рецепта",
              st.state == ar.RecipeManager.c_shop)

        m = FakeMessage("120")
        await ar.recadm_c_shop(m, st)
        check("предпросмотр содержит все параметры",
              st.state == ar.RecipeManager.c_confirm
              and "AAA-Блюдо" in m.text and "AAA-Результат" in m.text
              and "120 НМ" in m.text and "recadm:save" in cbs(m.kb))

        cb = Callback(ADMIN_UID, "recadm:save")
        await ar.recadm_save(cb, st)
        check("рецепт сохранён", "сохранён" in cb.message.text)
        rid1 = (await find_recipe("AAA-Блюдо", "kitchen", 2))["id"]
        recipe = await get_recipe(rid1)
        ings = json.loads(recipe["ingredients"])
        check("поля рецепта сохранены верно",
              recipe["description"] == "Тестовое описание"
              and recipe["result_item_name"] == "AAA-Результат"
              and recipe["result_quantity"] == 2
              and recipe["ap_cost"] == 7
              and recipe["production_time"] == 45
              and recipe["rarity"] == 3
              and ings == [["AAA-Ингредиент", 2], ["AAB-Ингредиент2", 3]])

        shop_item = await get_item_by_name(RECIPE_ITEM_PREFIX + "AAA-Блюдо")
        check("товар-рецепт создан в лавке",
              shop_item is not None and shop_item["price"] == 120
              and shop_item["category"] == "recipes"
              and shop_item["is_available"] == 1)

        st_dup = FakeState()
        await st_dup.update_data(d={
            "ctx": "create", "name": "AAA-Блюдо", "exp": "kitchen", "lvl": 2,
            "ingredients": [["AAA-Ингредиент", 1]], "result_item_name":
            "AAA-Результат", "qty": 1, "ap": 0, "time": 30, "rarity": 1,
            "shop": 0,
        })
        cb = Callback(ADMIN_UID, "recadm:save")
        await ar.recadm_save(cb, st_dup)
        check("дубликат рецепта не создаётся",
              "уже есть" in cb.message.text)

        print("\n4. Хелперы книг")
        rid2 = await upsert_recipe(
            "AAA-Второй рецепт", "второй", "AAA-Результат", 1, "kitchen", 1,
            [["AAA-Ингредиент", 1]], 0, 30, 1)
        book_item = await add_item(
            BOOK_ITEM_PREFIX + "Тестовая книга", "книга", 300, 150, 2,
            "recipes", -1, ADMIN_UID)
        linked = await set_recipe_book(book_item, [rid1, rid2, rid2])
        check("set_recipe_book дедуплицирует рецепты", linked == 2)
        book_recipes = await get_recipe_book_recipes(book_item)
        check("get_recipe_book_recipes возвращает оба рецепта",
              {r["id"] for r in book_recipes} == {rid1, rid2})

        books = await list_recipe_books()
        mine = next((b for b in books if b["id"] == book_item), None)
        check("list_recipe_books считает рецепты книги",
              mine is not None and mine["recipes_count"] == 2)

        check("скрытие книги работает",
              await set_recipe_book_visible(book_item, False) is True
              and (await get_item(book_item))["is_available"] == 0)
        check("показ книги работает",
              await set_recipe_book_visible(book_item, True) is True
              and (await get_item(book_item))["is_available"] == 1)
        check("не-книга не управляется как книга",
              await set_recipe_book_visible(ing1, True) is False
              and await delete_recipe_book(ing1) is False)

        print("\n5. Обучение по свитку и книге")
        # Свиток первого рецепта (товар уже создан при сохранении).
        await add_inventory_item(LEARNER, shop_item["id"], 1)
        ok1, msg1 = await learn_recipe_from_item(LEARNER, shop_item["id"])
        check("свиток учит рецепт и списывается",
              ok1 is True and "AAA-Блюдо" in msg1
              and await get_inventory_item(LEARNER, shop_item["id"]) is None
              and await has_user_recipe(LEARNER, rid1) is True)

        await add_inventory_item(LEARNER, shop_item["id"], 1)
        ok2, msg2 = await learn_recipe_from_item(LEARNER, shop_item["id"])
        check("уже выученный свиток не списывается",
              ok2 is False and "уже выучен" in msg2
              and (await get_inventory_item(LEARNER, shop_item["id"]))["quantity"] == 1)

        scroll2 = await add_item(
            RECIPE_ITEM_PREFIX + "AAA-Второй рецепт", "свиток", 100, 50, 1,
            "recipes", -1, ADMIN_UID)
        await add_inventory_item(LEARNER, scroll2, 1)
        ok3, _ = await learn_recipe_from_item(LEARNER, scroll2)
        check("свиток второго рецепта выучен",
              ok3 is True and await has_user_recipe(LEARNER, rid2) is True)

        # Книга с двумя рецептами, оба уже выучены — не списывается.
        await add_inventory_item(LEARNER, book_item, 1)
        ok4, msg4 = await learn_recipe_from_item(LEARNER, book_item)
        check("книга не списывается, если учить нечего",
              ok4 is False and "уже выучены" in msg4
              and (await get_inventory_item(LEARNER, book_item))["quantity"] == 1)

        # Новый игрок: книга открывает оба рецепта и списывается.
        await add_inventory_item(LEARNER2, book_item, 1)
        ok5, msg5 = await learn_recipe_from_item(LEARNER2, book_item)
        check("книга учит все рецепты и списывается",
              ok5 is True and "AAA-Блюдо" in msg5
              and "AAA-Второй рецепт" in msg5
              and await get_inventory_item(LEARNER2, book_item) is None
              and await has_user_recipe(LEARNER2, rid1) is True
              and await has_user_recipe(LEARNER2, rid2) is True)

        # Книга только с уже выученным рецептом — не списывается.
        book3 = await add_item(BOOK_ITEM_PREFIX + "Только первый", "книга",
                               50, 25, 1, "recipes", -1, ADMIN_UID)
        await set_recipe_book(book3, [rid1])
        await add_inventory_item(LEARNER3, book3, 1)
        await learn_recipe(LEARNER3, rid1)
        ok6, msg6 = await learn_recipe_from_item(LEARNER3, book3)
        check("книга с одним выученным рецептом остаётся у игрока",
              ok6 is False and "уже выучены" in msg6
              and (await get_inventory_item(LEARNER3, book3))["quantity"] == 1)

        print("\n6. Визард книги рецептов")
        st = FakeState()
        await ar.recadm_create(Callback(ADMIN_UID, "recadm:create"), st)
        await ar.recadm_kind(Callback(ADMIN_UID, "recadm:kind:book"), st)
        m = FakeMessage("Книга Визарда")
        await ar.recadm_c_name(m, st)
        check("для книги тоже спрашивается название",
              st.state == ar.RecipeManager.c_desc)
        m = FakeMessage("-")
        await ar.recadm_c_desc(m, st)
        check("после описания открывается выбор готовых рецептов",
              st.state == ar.RecipeManager.c_book
              and f"recadm:bookpick:0:{rid1}" in cbs(m.kb)
              and f"recadm:bookpick:0:{rid2}" in cbs(m.kb))

        cb = Callback(ADMIN_UID, "recadm:book_done")
        await ar.recadm_book_done(cb, st)
        check("книга без рецептов не создаётся",
              "хотя бы один" in cb.message.text)

        await ar.recadm_book_pick(
            Callback(ADMIN_UID, f"recadm:bookpick:0:{rid1}"), st)
        await ar.recadm_book_pick(
            Callback(ADMIN_UID, f"recadm:bookpick:0:{rid2}"), st)
        d = (await st.get_data())["d"]
        check("выбор рецептов для книги работает",
              set(d["book_recipes"]) == {rid1, rid2})

        cb = Callback(ADMIN_UID, "recadm:book_done")
        await ar.recadm_book_done(cb, st)
        check("после выбора рецептов спрашивается цена книги",
              st.state == ar.RecipeManager.c_book_price
              and "Цена книги" in cb.message.text)

        m = FakeMessage("700")
        await ar.recadm_c_book_price(m, st)
        check("книга создана", "создана" in m.text)
        wizard_book = await get_item_by_name(BOOK_ITEM_PREFIX + "Книга Визарда")
        check("предмет-книга создан с ценой и связкой",
              wizard_book is not None and wizard_book["price"] == 700
              and wizard_book["category"] == "recipes"
              and wizard_book["is_available"] == 1
              and {r["id"] for r in await get_recipe_book_recipes(
                  wizard_book["id"])} == {rid1, rid2})

        # Стартовая ensure_recipe_shop_items() не должна гасить книги: она ищет
        # рецепт по имени товара и без пропуска скрыла бы все книги.
        stale_scroll = await add_item(
            RECIPE_ITEM_PREFIX + "AAA-Удалённый рецепт", "свиток", 10, 5, 1,
            "recipes", -1, ADMIN_UID)
        await ensure_recipe_shop_items()
        check("старт не гасит книги, но скрывает мёртвые свитки",
              (await get_item(wizard_book["id"]))["is_available"] == 1
              and (await get_item(stale_scroll))["is_available"] == 0)

        cb = Callback(ADMIN_UID, f"recadm:bookopen:{wizard_book['id']}")
        await ar.recadm_book_open(cb, st)
        check("карточка книги показывает рецепты и цену",
              "AAA-Блюдо" in cb.message.text
              and "AAA-Второй рецепт" in cb.message.text
              and "700" in cb.message.text)

        cb = Callback(ADMIN_UID, f"recadm:booktoggle:{wizard_book['id']}")
        await ar.recadm_book_toggle(cb, st)
        check("кнопка «Скрыть» прячет книгу",
              (await get_item(wizard_book["id"]))["is_available"] == 0)
        cb = Callback(ADMIN_UID, f"recadm:booktoggle:{wizard_book['id']}")
        await ar.recadm_book_toggle(cb, st)
        check("кнопка «Показать» возвращает книгу",
              (await get_item(wizard_book["id"]))["is_available"] == 1)

        cb = Callback(ADMIN_UID, "recadm:books")
        await ar.recadm_books(cb, st)
        check("список книг показывает созданную книгу",
              "КНИГИ РЕЦЕПТОВ" in cb.message.text
              and f"recadm:bookopen:{wizard_book['id']}" in cbs(cb.message.kb))

        cb = Callback(ADMIN_UID, f"recadm:bookdel:{wizard_book['id']}")
        await ar.recadm_book_del(cb, st)
        check("удаление книги просит подтверждение",
              f"recadm:bookdel_yes:{wizard_book['id']}" in cbs(cb.message.kb))
        cb = Callback(ADMIN_UID, f"recadm:bookdel_yes:{wizard_book['id']}")
        await ar.recadm_book_del_yes(cb, st)
        check("мягкое удаление скрывает книгу, связка остаётся",
              (await get_item(wizard_book["id"]))["is_available"] == 0
              and len(await get_recipe_book_recipes(wizard_book["id"])) == 2)

        # Книга с ценой 0 создаётся, но скрыта.
        st = FakeState()
        await ar.recadm_create(Callback(ADMIN_UID, "recadm:create"), st)
        await ar.recadm_kind(Callback(ADMIN_UID, "recadm:kind:book"), st)
        await ar.recadm_c_name(FakeMessage("Нулевая книга"), st)
        await ar.recadm_c_desc(FakeMessage("-"), st)
        await ar.recadm_book_pick(
            Callback(ADMIN_UID, f"recadm:bookpick:0:{rid1}"), st)
        await ar.recadm_book_done(Callback(ADMIN_UID, "recadm:book_done"), st)
        m = FakeMessage("0")
        await ar.recadm_c_book_price(m, st)
        zero_book = await get_item_by_name(BOOK_ITEM_PREFIX + "Нулевая книга")
        check("книга с ценой 0 создаётся скрытой",
              zero_book is not None and zero_book["is_available"] == 0)

        print("\n7. Правка состава через пикер каталога")
        st = FakeState()
        cb = Callback(ADMIN_UID, f"recadm:ei:{rid1}")
        await ar.recadm_ei(cb, st)
        d = (await st.get_data())["d"]
        check("правка состава стартует с текущими ингредиентами",
              d.get("ctx") == "edit" and d.get("rid") == rid1
              and st.state == ar.RecipeManager.c_ing_cat
              and "СОСТАВ РЕЦЕПТА" in cb.message.text
              and "AAA-Ингредиент" in cb.message.text)

        await ar.recadm_ing_pick(
            Callback(ADMIN_UID, f"recadm:ingpick:{ing1}"), st)
        await ar.recadm_c_ing_qty(FakeMessage("5"), st)
        await ar.recadm_ing_pick(
            Callback(ADMIN_UID, f"recadm:ingpick:{ing2}"), st)
        await ar.recadm_c_ing_qty(FakeMessage("0"), st)
        await ar.recadm_ing_done(Callback(ADMIN_UID, "recadm:ing_done"), st)
        edited = await get_recipe(rid1)
        check("состав рецепта обновлён через пикер",
              json.loads(edited["ingredients"]) == [["AAA-Ингредиент", 5]])

        print("\n8. Доступ без прав")
        st = FakeState()
        cb = Callback(OUTSIDER, "recadm:create")
        await ar.recadm_create(cb, st)
        check("без can_manage_shop визард не открывается",
              cb.alerts and "Нет прав" in (cb.alerts[0] or "")
              and st.state is None)

    finally:
        await close_db()
        for _suffix in ("", "-wal", "-shm"):
            try:
                os.remove(_TEST_DB + _suffix)
            except OSError:
                pass

    print(f"\nИТОГО: {PASS} passed, {FAIL} failed")
    if FAIL:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
