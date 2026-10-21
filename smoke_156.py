"""Smoke v0.37.0/v0.38.0: «Лесозаготовка» — рубка деревьев, змея/неясыть, ослепление.

Проверяет:
1. Сид предметов: «Топор» (магазин, mining), «Бревна» (казна, не маркет),
   дропы змеи/неясыти (loot_only, не маркет).
2. Константы лесозаготовки и чистая логика: logging_wood_chance, owl_after_hit.
3. Сид врагов в logging_enemies (змея: яд 30%/2 в on_hit_effects, неясыть:
   flee 20, ослепление 30% через on_hit) и дропы (кожа 50%, яд 10%, перо 35%).
4. Счётчики гарантии (snake/owl) и колонки users.
5. Состояние «ослеплён» в STATE_CONF (урон ×0.7, уклонение ×0.5, 30 минут
   для ручной выдачи; в бою — на ходы боя, v0.38.0).
6. Кнопка «🪓 Лесозаготовка» на Лесной поляне (и отсутствие на опушке).
7. Вход: туриста не пускают; пилоту без топора — подсказка; с топором — окно.
8. Бой: змея убиваема + яд (on_hit store, v0.38.0); неясыть отлетает при
   HP ≤ 20 (победа, лут), ослепление накладывается на ходы боя;
   поражение от змеи −10 ОД.
9. Ратуша: в подписи есть «Пилот 2 класса».
10. Картинка Лесозаготовки: колонка/слот в картинках леса, сохранение и
    очистка через админ-обработчик, фон окна берёт свою картинку (photo_id)
    иначе — локальный файл.
11. Переработка брёвен (v0.38.2): предметы «Доска» и «Пак дров» (resource,
    market_ok=1), чистая логика max_planks/max_firewood, окно переработки,
    распил брёвен за НМ в казну (топор не нужен), рубка дров за ОД
    (топор обязателен), проверки нехватки денег и ОД.

Запуск: .venv\\Scripts\\python.exe smoke_156.py
"""
import asyncio
import os
import sys
from types import SimpleNamespace

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke156.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB

sys.path.insert(0, os.path.dirname(__file__))


class FakeSender:
    def __init__(self):
        self.sent = []
        self.edited = []

    async def send_message(self, chat_id, text, reply_markup=None, **kw):
        m = SimpleNamespace(message_id=len(self.sent) + 1)
        self.sent.append(("text", chat_id, text, reply_markup))
        return m

    async def send_photo(self, chat_id, photo, caption=None, reply_markup=None, **kw):
        m = SimpleNamespace(message_id=len(self.sent) + 1)
        self.sent.append(("photo", chat_id, caption or "", reply_markup))
        return m

    async def edit_message_text(self, chat_id, message_id, text=None, reply_markup=None, **kw):
        self.edited.append(("text", text, reply_markup))
        return SimpleNamespace(message_id=message_id)

    async def edit_message_media(self, chat_id, message_id, media=None, reply_markup=None, **kw):
        self.edited.append(("media", getattr(media, "caption", ""), reply_markup))
        return SimpleNamespace(message_id=message_id)

    async def edit_message_reply_markup(self, *a, **kw):
        return None

    async def delete_message(self, *a, **kw):
        return None


class FakeMessage:
    def __init__(self, user_id, bot=None):
        self.from_user = SimpleNamespace(id=user_id)
        self.chat = SimpleNamespace(id=user_id)
        self.message_id = 1
        self.bot = bot or FakeSender()
        self.sent = []

    async def answer(self, *a, **kw):
        self.sent.append(("answer", a, kw))

    async def __getattr__(self, name):
        async def _noop(*a, **kw):
            return None
        return _noop


class FakeCallback:
    def __init__(self, user_id, data="", message=None, bot=None):
        self.from_user = SimpleNamespace(id=user_id)
        self.bot = bot or FakeSender()
        self.message = message or FakeMessage(user_id, self.bot)
        self.data = data
        self.alerts = []

    async def answer(self, text=None, *a, **kw):
        self.alerts.append(text)


def markup_callbacks(markup):
    if not markup:
        return set()
    out = set()
    for row in getattr(markup, "inline_keyboard", []):
        for btn in row:
            out.add(btn.callback_data)
    return out


def last_send(bot):
    # Правка (edit) всегда новее отправки: окно рисуется один раз, дальше редактируется.
    if bot.edited:
        _, text, markup = bot.edited[-1]
        return text or "", markup
    if bot.sent:
        _, _chat, text, markup = bot.sent[-1]
        return text or "", markup
    return "", None


async def run():
    from config import (
        LOGGING_AP_COST, LOGGING_BASE_CHANCE, LOGGING_AXE_BONUS_PER_RANK,
        LOGGING_CHANCE_CAP, LOGGING_RESULT_DELAY, LOGGING_AXE_NAME,
        LOGGING_WOOD_NAME, LOGGING_SNAKE_KEY, LOGGING_OWL_KEY, LOGGING_SPOT,
        LOGGING_SNAKE_CHANCE, LOGGING_SNAKE_PITY_TARGET,
        LOGGING_OWL_CHANCE, LOGGING_OWL_PITY_TARGET,
        LOGGING_SNAKE_POISON_CHANCE, LOGGING_SNAKE_POISON_DMG,
        LOGGING_OWL_FLEE_HP, LOGGING_OWL_BLIND_CHANCE,
        LOGGING_ENEMY_DROPS, LOGGING_SHOP_ITEMS,
        LOGGING_PLANK_NAME, LOGGING_FIREWOOD_NAME, LOGGING_PLANK_YIELD,
        LOGGING_PLANK_FEE, LOGGING_FIREWOOD_YIELD, LOGGING_FIREWOOD_AP_COST,
        LOGGING_MARKET_RESOURCES,
    )
    from database.db import (
        init_db, close_db, seed_default_items, ensure_base_statuses,
        ensure_logging_items, ensure_logging_enemies,
        add_user, update_user, get_item_by_name, add_inventory_item, get_inventory,
        get_source_enemy_by_key, get_source_enemy_drops, get_source_enemies,
        enemy_encounter_hit, get_user,
        get_logging_snake_attempts, set_logging_snake_attempts, reset_logging_snake_counter,
        get_logging_owl_attempts, set_logging_owl_attempts, reset_logging_owl_counter,
        get_status_by_tag, grant_status,
        get_location_by_key, location_logging_photo, update_location_logging_photo,
        get_treasury_balance,
    )
    from utils.states import STATE_CONF
    from bot.handlers import logging_site as ls
    from bot.handlers import forest as fs
    import utils.combat_model as cm
    from contextlib import contextmanager

    @contextmanager
    def fixed_combat(pilot_damage=5, enemy_damage=1):
        """Детерминированный бой: без промахов, критов и уклонений."""
        saved_p, saved_e = cm.roll_pilot_damage, cm.roll_enemy_damage
        cm.roll_pilot_damage = lambda stats, enemy, *a, **k: {
            "damage": pilot_damage, "dodged": False, "armor_blocked": 0, "crit": False}
        cm.roll_enemy_damage = lambda stats, enemy, *a, **k: {
            "damage": enemy_damage, "dodged": False, "armor_blocked": 0, "crit": False}
        try:
            yield
        finally:
            cm.roll_pilot_damage, cm.roll_enemy_damage = saved_p, saved_e

    await init_db()
    await seed_default_items()
    await ensure_logging_items()
    await ensure_logging_enemies()
    from database.db import ensure_forest_zones
    await ensure_forest_zones()

    passed = 0
    failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
        else:
            failed += 1
            print(f"  FAIL: {name}")

    # ── 1. Предметы ──
    axe = await get_item_by_name(LOGGING_AXE_NAME)
    wood = await get_item_by_name(LOGGING_WOOD_NAME)
    plank = await get_item_by_name(LOGGING_PLANK_NAME)
    firewood = await get_item_by_name(LOGGING_FIREWOOD_NAME)
    skin = await get_item_by_name("Змеиная кожа")
    venom = await get_item_by_name("Змеиный яд")
    feather = await get_item_by_name("Совиное перо")
    check("предмет «Топор» есть", axe is not None)
    check("предмет «Бревна» есть", wood is not None)
    check("предмет «Доска» есть (v0.38.2)", plank is not None)
    check("предмет «Пак дров» есть (v0.38.2)", firewood is not None)
    check("Доска — категория resource", plank and plank["category"] == "resource")
    check("Пак дров — категория resource", firewood and firewood["category"] == "resource")
    check("Доска: sell 17 / price 34",
          plank and plank["sell_price"] == 17 and plank["price"] == 34)
    check("Пак дров: sell 10 / price 20",
          firewood and firewood["sell_price"] == 10 and firewood["price"] == 20)
    check("Доска market_ok=1", plank and plank["market_ok"] == 1)
    check("Пак дров market_ok=1", firewood and firewood["market_ok"] == 1)
    check("Доска не в магазине", plank and plank["is_available"] == 0)
    check("Пак дров не в магазине", firewood and firewood["is_available"] == 0)
    check("Доска не loot_only", plank and not plank["loot_only"])
    check("Пак дров не loot_only", firewood and not firewood["loot_only"])
    check("Доска/Пак дров в LOGGING_MARKET_RESOURCES",
          LOGGING_PLANK_NAME in LOGGING_MARKET_RESOURCES
          and LOGGING_FIREWOOD_NAME in LOGGING_MARKET_RESOURCES)
    check("дропы есть (кожа/яд/перо)", all((skin, venom, feather)))
    check("Топор — категория mining", axe and axe["category"] == "mining")
    check("Топор в магазине (is_available=1)", axe and axe["is_available"] == 1)
    check("Топор не loot_only", axe and not axe["loot_only"])
    check("Топор в LOGGING_SHOP_ITEMS", LOGGING_AXE_NAME in LOGGING_SHOP_ITEMS)
    check("Бревна — не в магазине", wood and wood["is_available"] == 0)
    check("Бревна market_ok=0", wood and wood["market_ok"] == 0)
    check("Бревна sell_price>0", wood and wood["sell_price"] > 0)
    check("дропы loot_only=1",
          all(d and d["loot_only"] == 1 for d in (skin, venom, feather)))
    check("дропы market_ok=0",
          all(d and d["market_ok"] == 0 for d in (skin, venom, feather)))
    check("все дропы в LOGGING_ENEMY_DROPS",
          all(n in LOGGING_ENEMY_DROPS for n in ("Змеиная кожа", "Змеиный яд", "Совиное перо")))

    # ── 2. Константы и чистая логика ──
    check("LOGGING_AP_COST = 12", LOGGING_AP_COST == 12)
    check("база шанса = 35", LOGGING_BASE_CHANCE == 35)
    check("надбавка топора = 15/ступень", LOGGING_AXE_BONUS_PER_RANK == 15)
    check("кап шанса = 90", LOGGING_CHANCE_CAP == 90)
    check("LOGGING_RESULT_DELAY = (7,15)", tuple(LOGGING_RESULT_DELAY) == (7, 15))
    check("шанс рубки ступень 1 = 50", ls.logging_wood_chance(1) == 50)
    check("шанс рубки ступень 2 = 65", ls.logging_wood_chance(2) == 65)
    check("шанс рубки ступень 5 = кап 90", ls.logging_wood_chance(5) == LOGGING_CHANCE_CAP)
    check("шанс рубки не ниже 0", ls.logging_wood_chance(0, logging_bonus=-999) == 0)
    hp, fled = ls.owl_after_hit(30, 10, LOGGING_OWL_FLEE_HP)
    check("неясыть: 30−10=20 ≤ 20 → отлетела", hp == 20 and fled is True)
    hp, fled = ls.owl_after_hit(50, 10, LOGGING_OWL_FLEE_HP)
    check("неясыть: 50−10=40 > 20 → держится", hp == 40 and fled is False)
    hp, fled = ls.owl_after_hit(20, 0, LOGGING_OWL_FLEE_HP)
    check("неясыть: без урона и HP=20 → отлетела", hp == 20 and fled is True)

    # ── 2b. Константы и логика переработки (v0.38.2) ──
    check("LOGGING_PLANK_YIELD = 3", LOGGING_PLANK_YIELD == 3)
    check("LOGGING_PLANK_FEE = 15", LOGGING_PLANK_FEE == 15)
    check("LOGGING_FIREWOOD_YIELD = 3", LOGGING_FIREWOOD_YIELD == 3)
    check("LOGGING_FIREWOOD_AP_COST = 4", LOGGING_FIREWOOD_AP_COST == 4)
    check("max_planks: 3 бревна, 100 НМ (fr. 6) → 9 досок",
          ls.max_planks(3, 100, 15, 3) == 9)
    check("max_planks: деньги режут (3 бревна, 30 НМ) → 6 досок",
          ls.max_planks(3, 30, 15, 3) == 6)
    check("max_planks: брёвна режут (10 бревён, 1000 НМ) → 30 досок",
          ls.max_planks(10, 1000, 15, 3) == 30)
    check("max_planks: ровно 15 НМ → 3 доски", ls.max_planks(5, 15, 15, 3) == 3)
    check("max_planks: нет денег → 0", ls.max_planks(5, 14, 15, 3) == 0)
    check("max_firewood: 3 бревна, 100 ОД (fr. 4) → 9 паков",
          ls.max_firewood(3, 100, 4, 3) == 9)
    check("max_firewood: ОД режут (3 бревна, 9 ОД) → 6 паков",
          ls.max_firewood(3, 9, 4, 3) == 6)
    check("max_firewood: брёвна режут (10 бревён, 100 ОД) → 30 паков",
          ls.max_firewood(10, 100, 4, 3) == 30)
    check("max_firewood: нет ОД → 0", ls.max_firewood(5, 3, 4, 3) == 0)

    # ── 3. Pity-бросок встречи ──
    # Счётчик = число пропущенных попыток: гарантия срабатывает на N-й попытке
    # при значении N−1 (та же семантика, что у кабана и мыши).
    check("встреча гарантирована на 10-й (sn)", enemy_encounter_hit(8.0, 99.0, 9, 10) is True)
    check("на 9-й ещё нет (sn)", enemy_encounter_hit(8.0, 99.0, 8, 10) is False)
    check("гарантия неясыти на 24-й", enemy_encounter_hit(3.0, 99.0, 23, 24) is True)
    check("низкий бросок → встреча", enemy_encounter_hit(3.0, 1.0, 0, 24) is True)

    # ── 4. Враги и дропы ──
    snake = await get_source_enemy_by_key("logging", LOGGING_SNAKE_KEY, spot=LOGGING_SPOT)
    owl = await get_source_enemy_by_key("logging", LOGGING_OWL_KEY, spot=LOGGING_SPOT)
    check("змея посеяна в logging_enemies", snake is not None)
    check("неясыть посеяна в logging_enemies", owl is not None)
    check("змея: шанс 8, pity 10",
          snake and abs(snake["chance"] - LOGGING_SNAKE_CHANCE) < 1e-9
          and snake["pity_target"] == LOGGING_SNAKE_PITY_TARGET)
    # v0.38.0: яд змеи — в on_hit_effects (JSON), legacy bleed_* убраны из сида.
    import json as _json
    snake_oh = _json.loads(snake['on_hit_effects'] or '[]') if snake else []
    check("змея: яд 30% на 2 HP (on_hit_effects)",
          any(e.get('kind') == 'poison' and int(e.get('chance') or 0) == 30
              and int(e.get('dmg') or 0) == 2 for e in snake_oh))
    check("змея: loss_ap 10", snake and snake["loss_ap"] == 10)
    check("неясыть: шанс 3, pity 24",
          owl and abs(owl["chance"] - LOGGING_OWL_CHANCE) < 1e-9
          and owl["pity_target"] == LOGGING_OWL_PITY_TARGET)
    check("неясыть: loss_ap 15", owl and owl["loss_ap"] == 15)
    snake_drops = await get_source_enemy_drops("logging", snake["id"]) if snake else []
    owl_drops = await get_source_enemy_drops("logging", owl["id"]) if owl else []
    check("у змеи 2 дропа", len(snake_drops) == 2)
    check("дропы змеи: кожа 50%, яд 10%",
          len(snake_drops) == 2
          and any(abs(d["chance"] - 0.50) < 1e-9 for d in snake_drops)
          and any(abs(d["chance"] - 0.10) < 1e-9 for d in snake_drops))
    check("у неясыти 1 дроп (перо 35%)",
          len(owl_drops) == 1 and abs(owl_drops[0]["chance"] - 0.35) < 1e-9)
    all_log = await get_source_enemies("logging")
    check("в logging_enemies ровно 2 врага", len(all_log) == 2)

    # Идемпотентность сидов: повторный вызов не добавляет дублей.
    await ensure_logging_items()
    await ensure_logging_enemies()
    check("сиды идемпотентны (врагов всё ещё 2)", len(await get_source_enemies("logging")) == 2)

    # ── 5. Счётчики гарантии и колонки ──
    uid = 561001
    await add_user(uid, "logger1", "Лесоруб1", "")
    check("счётчик змеи по умолчанию 0", await get_logging_snake_attempts(uid) == 0)
    await set_logging_snake_attempts(uid, 7)
    check("счётчик змеи ставится", await get_logging_snake_attempts(uid) == 7)
    await reset_logging_snake_counter(uid)
    check("счётчик змеи сбрасывается", await get_logging_snake_attempts(uid) == 0)
    check("счётчик неясыти по умолчанию 0", await get_logging_owl_attempts(uid) == 0)
    await set_logging_owl_attempts(uid, 15)
    check("счётчик неясыти ставится", await get_logging_owl_attempts(uid) == 15)
    await reset_logging_owl_counter(uid)
    check("счётчик неясыти сбрасывается", await get_logging_owl_attempts(uid) == 0)

    # ── 6. Состояние «ослеплён» ──
    conf = STATE_CONF.get("ослеплён")
    check("«ослеплён» есть в STATE_CONF", conf is not None)
    check("ослепление: урон ×0.7", conf and abs(conf["attack_mult"] - 0.7) < 1e-9)
    check("ослепление: уклонение ×0.5", conf and abs(conf["dodge_mult"] - 0.5) < 1e-9)
    check("ослепление: 30 минут", conf and conf["default_minutes"] == 30)

    # ── 7. Кнопка на Лесной поляне ──
    kb_clear = await fs._area_markup("tok1", "clearing")
    check("кнопка лесозаготовки на поляне", "logsite:enter" in markup_callbacks(kb_clear))
    kb_glade = await fs._area_markup("tok1", "glade")
    check("на опушке кнопки нет", "logsite:enter" not in markup_callbacks(kb_glade))
    check("результирующая клавиша поляны ведёт на лесозаготовку",
          "logsite:enter" in markup_callbacks(fs._simple_markup("tok1", "clearing")))
    check("на опушке «ещё» без лесозаготовки",
          "logsite:enter" not in markup_callbacks(fs._simple_markup("tok1", "glade")))

    # ── 8. Админ-заголовки ──
    from bot.handlers.admin import ENEMY_SRC_LOGGING, ENEMY_SOURCE_TITLES, _enemy_loc_title
    check("ENEMY_SRC_LOGGING = logging", ENEMY_SRC_LOGGING == "logging")
    check("заголовок источника есть", "Лесозаготовка" in ENEMY_SOURCE_TITLES[ENEMY_SRC_LOGGING])
    check("_enemy_loc_title(logging)", "Лесозаготовка" in _enemy_loc_title("logging", "logging"))

    # ── 8b. Картинка Лесозаготовки (слот в картинках леса) ──
    import bot.handlers.admin as admin_mod
    loc_forest = await get_location_by_key("forest")
    check("локация «Лес» есть", loc_forest is not None)
    check("колонка locations.logging_photo есть",
          loc_forest is not None and "logging_photo" in loc_forest.keys())
    await update_location_logging_photo(loc_forest["id"], "LOG_FID")
    loc_ref = await get_location_by_key("forest")
    check("сеттер сохранил картинку", location_logging_photo(loc_ref) == "LOG_FID")
    check("logging_site видит свою картинку", await ls._logging_photo_id() == "LOG_FID")

    picked = {}

    async def _pick_answer(text=None, reply_markup=None, **kw):
        picked["text"] = text
        picked["markup"] = reply_markup

    await admin_mod._loc_photos_pick_send(
        SimpleNamespace(answer=_pick_answer), loc_forest["id"])
    check("пикер картинок леса: кнопка «Лесозаготовка»",
          "loc:logging_set" in markup_callbacks(picked.get("markup")))
    check("пикер: статус слота в тексте", "Лесозаготовка" in (picked.get("text") or ""))

    class _State:
        def __init__(self, data):
            self._d = dict(data)

        async def get_data(self):
            return dict(self._d)

        async def clear(self):
            self._d = {}

    class _PhotoMsg:
        def __init__(self, uid, photo_id=None, text=None):
            self.from_user = SimpleNamespace(id=uid)
            self.photo = [SimpleNamespace(file_id=photo_id)] if photo_id else None
            self.text = text
            self.answers = []

        async def answer(self, *a, **kw):
            self.answers.append(a)

    await admin_mod.loc_step_photo(
        _PhotoMsg(uid, photo_id="LOG_PHOTO_FID"),
        _State({"target_id": loc_forest["id"], "photo_kind": "logging"}))
    loc_ref = await get_location_by_key("forest")
    check("админ-сохранение картинки (loc_step_photo)",
          location_logging_photo(loc_ref) == "LOG_PHOTO_FID")

    captured = {}
    orig_paint = ls._paint

    async def _fake_paint(callback, *, text=None, media_path=None,
                          photo_id=None, kb=None):
        captured.update(photo_id=photo_id, media_path=media_path)

    ls._paint = _fake_paint
    try:
        await ls._logging_paint(SimpleNamespace(), text="T")
        check("фон окна: своя картинка → photo_id",
              captured.get("photo_id") == "LOG_PHOTO_FID" and not captured.get("media_path"))
    finally:
        ls._paint = orig_paint

    await admin_mod.loc_step_photo(
        _PhotoMsg(uid, text="-"),
        _State({"target_id": loc_forest["id"], "photo_kind": "logging"}))
    loc_ref = await get_location_by_key("forest")
    check("очистка «-» вернула локальный фон",
          location_logging_photo(loc_ref) is None)
    check("после очистки logging_site без photo_id",
          await ls._logging_photo_id() is None)

    # ── 9. Вход: турист заблокирован ──
    await ensure_base_statuses()
    tourist = await get_status_by_tag("tourist")
    uid_t = 561000
    await add_user(uid_t, "tourist1", "Турист1", "")
    if tourist:
        await grant_status(uid_t, tourist["id"])
    bot_t = FakeSender()
    cb_t = FakeCallback(uid_t, data="logsite:enter", bot=bot_t)
    await ls.logging_menu_cb(cb_t)
    txt_t, _ = last_send(bot_t)
    tour_msg = ((cb_t.message.sent[-1][1][0] if cb_t.message.sent else "") or "") + txt_t
    check("туриста не пускают", "турист" in tour_msg.lower())

    # ── 10. Вход: пилот без топора ──
    await update_user(uid, ap=100)
    bot_n = FakeSender()
    cb_n = FakeCallback(uid, data="logsite:enter", bot=bot_n)
    await ls.logging_menu_cb(cb_n)
    txt_n, kb_n = last_send(bot_n)
    check("без топора: подсказка купить", "без топора" in txt_n.lower())
    token = ls.LOGGING_TOKEN.get(uid, "")
    check("без топора: токен выдан", bool(token))
    check("без топора: кнопка рубки есть", f"logsite:chop:{token}" in markup_callbacks(kb_n))

    # ── 11. Вход: пилот с топором ──
    await add_inventory_item(uid, axe["id"], 1)
    bot_a = FakeSender()
    cb_a = FakeCallback(uid, data="logsite:enter", bot=bot_a)
    await ls.logging_menu_cb(cb_a)
    txt_a, kb_a = last_send(bot_a)
    token = ls.LOGGING_TOKEN.get(uid, "")
    check("с топором: строка топора", "Топор" in txt_a)
    check("с топором: шанс рубки 50%", "50%" in txt_a)
    check("с топором: кнопка в лес", "logsite:back" in markup_callbacks(kb_a))

    # ── 12. Рубка без топора (прямой вызов) — нет, топор уже есть; рубка с топором ──
    uid2 = 561002
    await add_user(uid2, "logger2", "Лесоруб2", "")
    await update_user(uid2, ap=60)
    await add_inventory_item(uid2, axe["id"], 1)
    tok2 = ls._new_token()
    ls.LOGGING_TOKEN[uid2] = tok2
    ls.LOGGING_RESULT_DELAY_SAVED = ls.LOGGING_RESULT_DELAY
    ls.LOGGING_RESULT_DELAY = (0, 0)  # без задержки в тесте
    # Форсим находку бревна: без врагов и удачный бросок.
    saved_snake, saved_owl = ls._snake, ls._owl
    async def _no_snake():
        return None
    async def _no_owl():
        return None
    ls._snake, ls._owl = _no_snake, _no_owl
    saved_random = ls.random.random
    ls.random.random = lambda: 0.0  # 0.0 < шанса 50% → успех
    try:
        bot_c = FakeSender()
        cb_c = FakeCallback(uid2, data=f"logsite:chop:{tok2}", bot=bot_c)
        await ls.logging_chop(cb_c)
    finally:
        ls.random.random = saved_random
        ls._snake, ls._owl = saved_snake, saved_owl
        ls.LOGGING_RESULT_DELAY = ls.LOGGING_RESULT_DELAY_SAVED
    txt_c, kb_c = last_send(bot_c)
    check("рубка списала ОД", (await get_user(uid2))["ap"] == 60 - LOGGING_AP_COST)
    inv2 = await get_inventory(uid2)
    check("бревно в инвентаре",
          wood and any(i["id"] == wood["id"] for i in inv2))
    check("текст с бревном", "Бревна" in txt_c or "бревно" in txt_c.lower())
    check("кнопка «рубить ещё»", f"logsite:chop:{tok2}" in markup_callbacks(kb_c))
    check("кастинг снят", uid2 not in ls.LOGGING_CASTING)

    # ── 13. Бой со змеёй: победа + лут, яд не висит ──
    uid3 = 561003
    await add_user(uid3, "logger3", "Лесоруб3", "")
    await update_user(uid3, ap=50)
    tok3 = ls._new_token()
    ls.LOGGING_TOKEN[uid3] = tok3
    ls.LOGGING_BATTLE[uid3] = {
        "token": tok3, "kind": "snake",
        "player_hp": 400, "player_hp_max": 400,
        "enemy_hp": 1, "enemy_hp_max": 30, "enemy_name": "Лесная змея", "emoji": "🐍",
        "dodge": 0.0, "armor": 0, "dmg_min": 1, "dmg_max": 1, "loss_ap": 10,
        "poison_chance": 0, "poison_dmg": 0, "active_poison": 0, "poison_ticks": 0,
        "enemy": snake, "round": 1,
    }
    skin_before = 0
    it_skin = await get_item_by_name("Змеиная кожа")
    if it_skin:
        skin_before = next((i["quantity"] for i in await get_inventory(uid3)
                            if i["id"] == it_skin["id"]), 0)
    ls.roll_enemy_drops = lambda d: [{"item_id": it_skin["id"], "qty": 1, "chance": 0.5}] if it_skin else []
    cb_s = FakeCallback(uid3, data=f"logsite:battle:hit:{tok3}", bot=FakeSender())
    with fixed_combat(pilot_damage=5, enemy_damage=1):
        for _ in range(50):
            if uid3 not in ls.LOGGING_BATTLE:
                break
            await ls.logging_battle_hit(cb_s)
    check("змея: бой завершён", uid3 not in ls.LOGGING_BATTLE)
    inv3 = await get_inventory(uid3)
    skin_after = next((i["quantity"] for i in inv3 if i["id"] == it_skin["id"]), 0) if it_skin else 0
    check("змея: кожа в инвентаре (+1)", skin_after == skin_before + 1)

    # ── 14. Бой со змеёй: яд накладывается ответным ударом ──
    uid4 = 561004
    await add_user(uid4, "logger4", "Лесоруб4", "")
    await update_user(uid4, ap=50)
    tok4 = ls._new_token()
    ls.LOGGING_TOKEN[uid4] = tok4
    ls.LOGGING_BATTLE[uid4] = {
        "token": tok4, "kind": "snake",
        "player_hp": 400, "player_hp_max": 400,
        "enemy_hp": 999999, "enemy_hp_max": 999999, "enemy_name": "Лесная змея", "emoji": "🐍",
        "dodge": 0.0, "armor": 0, "dmg_min": 1, "dmg_max": 1, "loss_ap": 10,
        # v0.38.0: яд врага — через on_hit_effects, не legacy-ключи.
        "on_hit_effects": [{"kind": "poison", "chance": 100, "dmg": 2}],
        "enemy": snake, "round": 1,
    }
    cb_p = FakeCallback(uid4, data=f"logsite:battle:hit:{tok4}", bot=FakeSender())
    with fixed_combat(pilot_damage=5, enemy_damage=1):
        await ls.logging_battle_hit(cb_p)
    b4 = ls.LOGGING_BATTLE.get(uid4) or {}
    check("змея: яд наложен (on_hit poison)",
          (b4.get("on_hit") or {}).get("poison", {}).get("dmg") == 2)
    ls.LOGGING_BATTLE.pop(uid4, None)

    # ── 15. Бой с неясытью: отлёт при HP ≤ 20 → победа, бой завершён ──
    uid5 = 561005
    await add_user(uid5, "logger5", "Лесоруб5", "")
    await update_user(uid5, ap=50)
    tok5 = ls._new_token()
    ls.LOGGING_TOKEN[uid5] = tok5
    feather_item = await get_item_by_name("Совиное перо")
    ls.LOGGING_BATTLE[uid5] = {
        "token": tok5, "kind": "owl",
        "player_hp": 400, "player_hp_max": 400,
        "enemy_hp": LOGGING_OWL_FLEE_HP + 1, "enemy_hp_max": 90,
        "enemy_name": "Неясыть", "emoji": "🦉",
        "dodge": 0.0, "armor": 0, "dmg_min": 1, "dmg_max": 1, "loss_ap": 15,
        "poison_chance": 0, "poison_dmg": 0, "active_poison": 0, "poison_ticks": 0,
        "enemy": owl, "round": 1,
    }
    ls.roll_enemy_drops = lambda d: [{"item_id": feather_item["id"], "qty": 1, "chance": 0.35}] if feather_item else []
    cb_o = FakeCallback(uid5, data=f"logsite:battle:hit:{tok5}", bot=FakeSender())
    with fixed_combat(pilot_damage=10, enemy_damage=1):
        for _ in range(20):
            if uid5 not in ls.LOGGING_BATTLE:
                break
            await ls.logging_battle_hit(cb_o)
    check("неясыть: отлетела, бой завершён", uid5 not in ls.LOGGING_BATTLE)
    inv5 = await get_inventory(uid5)
    check("неясыть: перо в инвентаре",
          feather_item and any(i["id"] == feather_item["id"] for i in inv5))

    # ── 16. Неясыть: ослепление накладывается при попадании ──
    uid6 = 561006
    await add_user(uid6, "logger6", "Лесоруб6", "")
    await update_user(uid6, ap=50)
    tok6 = ls._new_token()
    ls.LOGGING_TOKEN[uid6] = tok6
    ls.LOGGING_BATTLE[uid6] = {
        "token": tok6, "kind": "owl",
        "player_hp": 400, "player_hp_max": 400,
        "enemy_hp": 90, "enemy_hp_max": 90, "enemy_name": "Неясыть", "emoji": "🦉",
        "dodge": 0.0, "armor": 0, "dmg_min": 0, "dmg_max": 0, "loss_ap": 15,
        # v0.38.0: ослепление — эффект on_hit врага (бой store), не users.state.
        "on_hit_effects": [{"kind": "state", "key": "ослеплён",
                            "chance": 100, "rounds": 4}],
        "enemy": owl, "round": 1,
    }
    saved_ri = ls.random.randint
    ls.random.randint = lambda a, b: 1  # детерминированный бросок прока
    cb_bl = FakeCallback(uid6, data=f"logsite:battle:hit:{tok6}", bot=FakeSender())
    try:
        with fixed_combat(pilot_damage=5, enemy_damage=1):
            await ls.logging_battle_hit(cb_bl)
    finally:
        ls.random.randint = saved_ri
    b6 = ls.LOGGING_BATTLE.get(uid6) or {}
    check("неясыть: «ослеплён» наложен (on_hit store)",
          (b6.get("on_hit") or {}).get("ослеплён", {}).get("rounds_left") is not None)
    ls.LOGGING_BATTLE.pop(uid6, None)

    # ── 17. Поражение от змеи: −10 ОД ──
    uid7 = 561007
    await add_user(uid7, "logger7", "Лесоруб7", "")
    await update_user(uid7, ap=50)
    tok7 = ls._new_token()
    ls.LOGGING_TOKEN[uid7] = tok7
    ls.LOGGING_BATTLE[uid7] = {
        "token": tok7, "kind": "snake",
        "player_hp": 1, "player_hp_max": 100,
        "enemy_hp": 999999, "enemy_hp_max": 999999, "enemy_name": "Лесная змея", "emoji": "🐍",
        "dodge": 0.0, "armor": 0, "dmg_min": 999, "dmg_max": 999, "loss_ap": 10,
        "poison_chance": 0, "poison_dmg": 0, "active_poison": 0, "poison_ticks": 0,
        "enemy": snake, "round": 1,
    }
    cb_lose = FakeCallback(uid7, data=f"logsite:battle:hit:{tok7}", bot=FakeSender())
    with fixed_combat(pilot_damage=5, enemy_damage=999):
        for _ in range(50):
            if uid7 not in ls.LOGGING_BATTLE:
                break
            await ls.logging_battle_hit(cb_lose)
    check("поражение: бой завершён", uid7 not in ls.LOGGING_BATTLE)
    check("поражение: −10 ОД", (await get_user(uid7))["ap"] == 40)

    # ── 18b. Переработка брёвен: распил на доски (v0.38.2) ──
    uid_m = 561010
    await add_user(uid_m, "miller", "Мельник", "")
    await update_user(uid_m, ap=60, nordmarks=100)
    await add_inventory_item(uid_m, wood["id"], 4)
    tok_m = ls._new_token()
    ls.LOGGING_TOKEN[uid_m] = tok_m
    treasury_before = await get_treasury_balance()

    # Окно переработки
    bot_m = FakeSender()
    cb_m = FakeCallback(uid_m, data=f"logsite:mill:{tok_m}", bot=bot_m)
    await ls.logging_mill(cb_m)
    txt_m, kb_m = last_send(bot_m)
    check("переработка: окно показывает брёвна", "4" in txt_m)
    check("переработка: кнопка распила на доски",
          f"logsite:plank:all:{tok_m}" in markup_callbacks(kb_m))
    check("переработка: кнопка дров",
          f"logsite:fire:all:{tok_m}" in markup_callbacks(kb_m))

    # Распил: 4 бревна × 15 = 60 НМ → 12 досок
    bot_p = FakeSender()
    cb_p = FakeCallback(uid_m, data=f"logsite:plank:all:{tok_m}", bot=bot_p)
    await ls.logging_plank(cb_p)
    txt_p, kb_p = last_send(bot_p)
    inv_m = await get_inventory(uid_m)
    planks_m = next((i["quantity"] for i in inv_m if i["id"] == plank["id"]), 0)
    wood_m = next((i["quantity"] for i in inv_m if i["id"] == wood["id"]), 0)
    check("распил: 12 досок в инвентаре", planks_m == 12)
    check("распил: брёвна ушли (0 осталось)", wood_m == 0)
    check("распил: деньги ушли (100−60=40)",
          (await get_user(uid_m))["nordmarks"] == 40)
    check("распил: казна пополнилась на 60",
          await get_treasury_balance() == treasury_before + 60)
    check("распил: текст про доски", "Доска" in txt_p or "доск" in txt_p.lower())
    check("распил: кнопки переработки пропали (нет брёвен)",
          f"logsite:mill:{tok_m}" not in markup_callbacks(kb_p))

    # Распил без денег: 2 бревна, 10 НМ → 0 досок
    uid_m2 = 561011
    await add_user(uid_m2, "miller2", "Мельник2", "")
    await update_user(uid_m2, ap=60, nordmarks=10)
    await add_inventory_item(uid_m2, wood["id"], 2)
    tok_m2 = ls._new_token()
    ls.LOGGING_TOKEN[uid_m2] = tok_m2
    bot_p2 = FakeSender()
    cb_p2 = FakeCallback(uid_m2, data=f"logsite:plank:all:{tok_m2}", bot=bot_p2)
    await ls.logging_plank(cb_p2)
    check("распил без денег: отказ с подсказкой",
          any("Не хватает денег" in (a or "") for a in cb_p2.alerts))
    inv_m2 = await get_inventory(uid_m2)
    wood_m2 = next((i["quantity"] for i in inv_m2 if i["id"] == wood["id"]), 0)
    check("распил без денег: брёвна целы", wood_m2 == 2)
    check("распил без денег: доски не появились",
          next((i["quantity"] for i in inv_m2 if i["id"] == plank["id"]), 0) == 0)

    # ── 18c. Переработка брёвен: рубка дров за ОД (v0.38.2) ──
    uid_f = 561012
    await add_user(uid_f, "fireman", "Дровосек", "")
    await update_user(uid_f, ap=20)
    await add_inventory_item(uid_f, wood["id"], 3)
    await add_inventory_item(uid_f, axe["id"], 1)  # топор нужен
    tok_f = ls._new_token()
    ls.LOGGING_TOKEN[uid_f] = tok_f
    bot_f = FakeSender()
    cb_f = FakeCallback(uid_f, data=f"logsite:fire:all:{tok_f}", bot=bot_f)
    await ls.logging_firewood(cb_f)
    txt_f, kb_f = last_send(bot_f)
    inv_f = await get_inventory(uid_f)
    fw_f = next((i["quantity"] for i in inv_f if i["id"] == firewood["id"]), 0)
    wood_f = next((i["quantity"] for i in inv_f if i["id"] == wood["id"]), 0)
    check("дрова: 9 паков получено", fw_f == 9)
    check("дрова: брёвна ушли (0)", wood_f == 0)
    check("дрова: ОД −12 (20−12=8)", (await get_user(uid_f))["ap"] == 8)
    check("дрова: текст про дрова", "дров" in txt_f.lower())

    # Дрова без топора: отказано
    uid_f2 = 561013
    await add_user(uid_f2, "fireman2", "Дровосек2", "")
    await update_user(uid_f2, ap=20)
    await add_inventory_item(uid_f2, wood["id"], 2)
    tok_f2 = ls._new_token()
    ls.LOGGING_TOKEN[uid_f2] = tok_f2
    bot_f2 = FakeSender()
    cb_f2 = FakeCallback(uid_f2, data=f"logsite:fire:all:{tok_f2}", bot=bot_f2)
    await ls.logging_firewood(cb_f2)
    txt_f2, _ = last_send(bot_f2)
    check("дрова без топора: подсказка", "топор" in txt_f2.lower())
    inv_f2 = await get_inventory(uid_f2)
    check("дрова без топора: брёвна целы",
          next((i["quantity"] for i in inv_f2 if i["id"] == wood["id"]), 0) == 2)

    # Дрова без ОД: отказано
    uid_f3 = 561014
    await add_user(uid_f3, "fireman3", "Дровосек3", "")
    await update_user(uid_f3, ap=3)
    await add_inventory_item(uid_f3, wood["id"], 2)
    await add_inventory_item(uid_f3, axe["id"], 1)
    tok_f3 = ls._new_token()
    ls.LOGGING_TOKEN[uid_f3] = tok_f3
    bot_f3 = FakeSender()
    cb_f3 = FakeCallback(uid_f3, data=f"logsite:fire:all:{tok_f3}", bot=bot_f3)
    await ls.logging_firewood(cb_f3)
    check("дрова без ОД: отказ с подсказкой",
          any("Не хватает ОД" in (a or "") for a in cb_f3.alerts))

    # Окно переработки без брёвен: нет кнопок распила/дров
    uid_m3 = 561015
    await add_user(uid_m3, "miller3", "Мельник3", "")
    await update_user(uid_m3, ap=60)
    tok_m3 = ls._new_token()
    ls.LOGGING_TOKEN[uid_m3] = tok_m3
    bot_m3 = FakeSender()
    cb_m3 = FakeCallback(uid_m3, data=f"logsite:mill:{tok_m3}", bot=bot_m3)
    await ls.logging_mill(cb_m3)
    txt_m3, kb_m3 = last_send(bot_m3)
    check("переработка без брёвен: нет кнопок",
          f"logsite:plank:all:{tok_m3}" not in markup_callbacks(kb_m3)
          and f"logsite:fire:all:{tok_m3}" not in markup_callbacks(kb_m3))
    check("переработка без брёвен: подсказка",
          "нет брёвен" in txt_m3.lower() or "сначала наруби" in txt_m3.lower())

    # ── 18. deactivate сбрасывает окно ──
    ls.LOGGING_TOKEN[uid] = "abc"
    ls.LOGGING_MSG[uid] = (1, 1)
    ls.LOGGING_CASTING.add(uid)
    ls.LOGGING_BATTLE[uid] = {"token": "abc"}
    await ls.deactivate_logging_site(uid)
    check("deactivate: токен снят", uid not in ls.LOGGING_TOKEN)
    check("deactivate: сообщение снято", uid not in ls.LOGGING_MSG)
    check("deactivate: кастинг снят", uid not in ls.LOGGING_CASTING)
    check("deactivate: бой снят", uid not in ls.LOGGING_BATTLE)

    # ── 19. Ратуша: строка про «Пилота 2 класса» ──
    from bot.handlers import pilots as pl

    class HallMessage(FakeMessage):
        def __init__(self, user_id):
            super().__init__(user_id)
            self.texts = []

        async def edit_text(self, text=None, reply_markup=None, **kw):
            self.texts.append(text)
            return None

        async def edit_media(self, media=None, reply_markup=None, **kw):
            self.texts.append(getattr(media, "caption", ""))
            return None

        async def answer_photo(self, photo=None, caption=None, reply_markup=None, **kw):
            self.texts.append(caption)
            m = SimpleNamespace(message_id=1)
            self.sent.append(("photo", 0, caption or "", reply_markup))
            return m

    saved_resolve = pl.resolve_image
    pl.resolve_image = lambda key: os.path.join(os.path.dirname(__file__), "_no_such.jpg")
    hall_msg = HallMessage(uid)
    cb_hall = FakeCallback(uid, data="city:pilots", message=hall_msg, bot=FakeSender())
    try:
        await pl._show_hall(cb_hall)
    finally:
        pl.resolve_image = saved_resolve
    hall_text = " ".join(t or "" for t in hall_msg.texts)
    if not hall_text:
        hall_text, _ = last_send(cb_hall.bot)
    check("Ратуша: «Пилот 2 класса» в подписи",
          "Пилот 2 класса" in hall_text)

    await close_db()
    print(f"\nSmoke 156: {passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    try:
        asyncio.run(run())
    except SystemExit:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        from database.db import close_db
        asyncio.run(close_db())
        print(f"SMOKE ERROR: {e!r}")
        sys.exit(1)
