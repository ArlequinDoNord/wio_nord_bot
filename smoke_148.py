"""Smoke v0.31.0: «Железная копи» — ресурсная локация и бой с Летучей мышью.

Проверяет:
1. Сид предметов: «Кирка» (магазин, mining), «Железная руда» (казна, не маркет),
   самоцветы (лут, loot_only).
2. Константы копи и чистая логика: mine_ore_chance, cap_gem_drops, pity.
3. Сид врага в mine_enemies (мышь: chance/pity/loss_ap/enabled) и 3 дропа по 1%.
4. Сид локации «mine» (access_mode=min, required_status=pilot1) и дефолтные карты.
5. Вход: туриста не пускают; пилота с киркой пускают, окно предлагает копать.
6. Бой: победа → самоцветы с кэпом 1; поражение → −15 ОД, бой не зависает.

Запуск: .venv\\Scripts\\python.exe smoke_148.py
"""
import asyncio
import os
import sys
from types import SimpleNamespace

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke148.db")
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
    if bot.sent:
        _, _chat, text, markup = bot.sent[-1]
        return text or "", markup
    if bot.edited:
        _, text, markup = bot.edited[-1]
        return text or "", markup
    return "", None


async def run():
    from config import (
        MINE_AP_COST, MINE_BASE_CHANCE, MINE_PICKAXE_BONUS_PER_RANK, MINE_CHANCE_CAP,
        MINE_RESULT_DELAY, MINE_GEM_CAP, MINE_BAT_KEY, MINE_BAT_SPOT,
        MINE_BAT_CHANCE, MINE_BAT_PITY_TARGET, MINE_PICKAXE_NAME, MINE_ORE_NAME,
        ITEM_CATEGORIES,
    )
    from database.db import (
        init_db, close_db, seed_default_items, ensure_base_statuses,
        ensure_mine_items, ensure_mine_enemies,
        add_user, update_user, get_item_by_name, add_inventory_item, get_inventory,
        get_source_enemy_by_key, get_source_enemy_drops, enemy_encounter_hit,
        get_all_locations, get_status_by_tag, grant_status, get_inventory_item,
    )
    from bot.handlers import mine as mm

    await init_db()
    await seed_default_items()
    await ensure_mine_items()
    await ensure_mine_enemies()

    passed = 0
    failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
        else:
            failed += 1
            print(f"  FAIL: {name}")

    async def gem_total(uid):
        inv = await get_inventory(uid)
        total = 0
        for g in ("Изумруд", "Рубин", "Сапфир"):
            it = await get_item_by_name(g)
            if it:
                total += next((i["quantity"] for i in inv if i["id"] == it["id"]), 0)
        return total

    # ── 1. Предметы ──
    pick = await get_item_by_name(MINE_PICKAXE_NAME)
    ore = await get_item_by_name(MINE_ORE_NAME)
    gems = [await get_item_by_name(g) for g in ("Изумруд", "Рубин", "Сапфир")]
    check("предмет «Кирка» есть", pick is not None)
    check("предмет «Железная руда» есть", ore is not None)
    check("все самоцветы есть", all(gems))
    check("Кирка — категория mining", pick and pick["category"] == "mining")
    check("Кирка в магазине (is_available=1)", pick and pick["is_available"] == 1)
    check("Кирка обычная (не loot_only)", pick and not pick["loot_only"])
    check("Руда — не в магазине", ore and ore["is_available"] == 0)
    check("Руда market_ok=0 (только казна)", ore and ore["market_ok"] == 0)
    check("Руда sell_price>0", ore and ore["sell_price"] > 0)
    check("Самоцветы loot_only=1", all(g and g["loot_only"] == 1 for g in gems))
    check("Самоцветы market_ok=0", all(g and g["market_ok"] == 0 for g in gems))
    check("категория mining в ITEM_CATEGORIES", "mining" in ITEM_CATEGORIES)

    # ── 2. Константы и чистая логика ──
    check("MINE_AP_COST = 12", MINE_AP_COST == 12)
    check("база шанса = 30", MINE_BASE_CHANCE == 30)
    check("надбавка кирки = 15/ступень", MINE_PICKAXE_BONUS_PER_RANK == 15)
    check("кап шанса = 90", MINE_CHANCE_CAP == 90)
    check("MINE_RESULT_DELAY = (7,15)", tuple(MINE_RESULT_DELAY) == (7, 15))
    check("MINE_GEM_CAP = 1", MINE_GEM_CAP == 1)
    check("MINE_BAT_KEY/SPOT", MINE_BAT_KEY == "bat" and MINE_BAT_SPOT == "iron")
    check("шанс руды ступень 1 = 45", mm.mine_ore_chance(1) == 45)
    check("шанс руды ступень 5 = кап 90", mm.mine_ore_chance(5) == MINE_CHANCE_CAP)
    check("шанс руды не ниже 0", mm.mine_ore_chance(0, mining_bonus=-999) == 0)
    three = [{"item_id": 1}, {"item_id": 2}, {"item_id": 3}]
    check("кэп гемов оставляет 1", len(mm.cap_gem_drops(three)) == 1)
    check("кэп гемов 2 из 3", len(mm.cap_gem_drops(three, cap=2)) == 2)
    check("кэп гемов cap<=0 → пусто", mm.cap_gem_drops(three, cap=0) == [])

    # ── 3. Pity-бросок встречи ──
    check("встреча гарантирована на 12-й", enemy_encounter_hit(7.0, 99.0, 11, 12) is True)
    check("на 11-й ещё нет", enemy_encounter_hit(7.0, 99.0, 10, 12) is False)
    check("низкий бросок → встреча", enemy_encounter_hit(7.0, 3.0, 0, 12) is True)
    check("высокий бросок без pity → нет", enemy_encounter_hit(7.0, 90.0, 0, 12) is False)

    # ── 4. Враг и дропы ──
    bat = await get_source_enemy_by_key("mine", MINE_BAT_KEY, spot=MINE_BAT_SPOT)
    check("мышь посеяна в mine_enemies", bat is not None)
    drops = await get_source_enemy_drops("mine", bat["id"]) if bat else []
    check("у мыши 3 дропа", len(drops) == 3)
    check("дропы — самоцветы по 1%",
          len(drops) == 3 and all(abs(d["chance"] - 0.01) < 1e-9 for d in drops))

    # ── 5. Локация и дефолтные карты ──
    locs = await get_all_locations()
    mine_loc = next((l for l in locs if l["key"] == "mine"), None)
    check("локация mine посеяна", mine_loc is not None)
    check("mine access_mode=min", mine_loc and mine_loc["access_mode"] == "min")
    check("mine required_status=pilot1", mine_loc and mine_loc["required_status"] == "pilot1")
    from bot.handlers.locations import LOCATION_ACCESS_LINES
    from keyboards.keyboards import LOCATION_BUTTON_EMOJI
    from bot.handlers.inventory import INV_CATEGORIES
    from bot.handlers.shop import CATEGORIES
    check("LOCATION_ACCESS_LINES[mine]", "mine" in LOCATION_ACCESS_LINES)
    check("LOCATION_BUTTON_EMOJI[mine]", LOCATION_BUTTON_EMOJI.get("mine"))
    check("INV_CATEGORIES[mining]", "mining" in INV_CATEGORIES)
    check("shop CATEGORIES[mining]", "mining" in CATEGORIES)

    # ── 5b. Картинка 1-го уровня шахт (отдельная от входа) ──
    from database.db import (
        get_location, update_location_mine_level_photo, location_mine_level_photo,
    )
    check("колонка locations.mine_level_photo есть",
          mine_loc is not None and "mine_level_photo" in mine_loc.keys())
    check("уровень 1 без своей картинки → None",
          location_mine_level_photo(mine_loc) is None)
    await update_location_mine_level_photo(mine_loc["id"], "LEVEL_FID")
    fresh = await get_location(mine_loc["id"])
    check("уровень 1: своя картинка сохранена",
          location_mine_level_photo(fresh) == "LEVEL_FID")
    pid_l, path_l = await mm._level_media()
    check("уровень 1: берётся file_id (media_path=None)", pid_l == "LEVEL_FID" and path_l is None)
    await update_location_mine_level_photo(mine_loc["id"], None)
    pid_l, path_l = await mm._level_media()
    check("уровень 1: откат на локальный файл",
          pid_l is None and path_l == mm._level_path())

    if not pick or not ore or not all(gems):
        await close_db()
        print(f"\nSmoke 148: {passed} passed, {failed} failed")
        sys.exit(1)

    # ── 6. Вход: турист заблокирован ──
    await ensure_base_statuses()
    tourist = await get_status_by_tag("tourist")
    uid_t = 481000
    await add_user(uid_t, "tourist1", "Турист1", "")
    if tourist:
        await grant_status(uid_t, tourist["id"])
    bot_t = FakeSender()
    cb_t = FakeCallback(uid_t, data="location:enter:mine", bot=bot_t)
    await mm.mine_menu_cb(cb_t)
    txt_t, _ = last_send(bot_t)
    check("туриста в копь не пускают",
          "турист" in ((cb_t.message.sent[-1][1][0] if cb_t.message.sent else "") or "").lower()
          or "турист" in txt_t.lower())

    # ── 7. Вход: пилот с киркой ──
    uid = 481001
    await add_user(uid, "miner", "Шахтёр", "")
    await update_user(uid, ap=100)
    await add_inventory_item(uid, pick["id"], 1)
    bot_m = FakeSender()
    cb_m = FakeCallback(uid, data="location:enter:mine", bot=bot_m)
    await mm.mine_menu_cb(cb_m)
    txt_m, kb_m = last_send(bot_m)
    token = mm.MINE_TOKEN.get(uid, "")
    check("вход в копь: токен выдан", bool(token))
    check("вход в копь: кнопка 1-го уровня", f"mine:level:{token}" in markup_callbacks(kb_m))
    check("вход в копь: кнопка в город", "city:menu" in markup_callbacks(kb_m))

    # ── 7b. 1-й уровень шахт: свои кнопки (добыча / спуск / выход) ──
    bot_l = FakeSender()
    cb_l = FakeCallback(uid, data=f"mine:level:{token}", bot=bot_l)
    await mm.mine_level_cb(cb_l)
    txt_l, kb_l = last_send(bot_l)
    cbs_l = markup_callbacks(kb_l)
    check("уровень 1: строка кирки", "Кирка" in txt_l)
    check("уровень 1: кнопка добычи", f"mine:dig:{token}" in cbs_l)
    check("уровень 1: кнопка спуска глубже", f"mine:deeper:{token}" in cbs_l)
    check("уровень 1: кнопка выйти из шахты", f"mine:menu:{token}" in cbs_l)

    # ── 7c. Спуск глубже — заблокирован (заглушка) ──
    cb_d = FakeCallback(uid, data=f"mine:deeper:{token}", bot=FakeSender())
    await mm.mine_deeper(cb_d)
    check("спуск глубже: предупреждение",
          any("не обустроен" in (a or "") for a in cb_d.alerts))

    # ── 8. Бой: победа → кэп самоцветов ──
    all_drops = [{"item_id": g["id"], "qty": 1, "chance": 0.01} for g in gems]
    mm.roll_enemy_drops = lambda d: list(all_drops)  # форсим «выпали все три»
    mm.MINE_BATTLE[uid] = {
        "token": token, "player_hp": 500, "player_hp_max": 500,
        "bat_hp": 1, "bat_hp_max": 1, "bat_name": "Летучая мышь", "emoji": "🦇",
        "dodge": 0.0, "armor": 0, "dmg_min": 1, "dmg_max": 2, "loss_ap": 15,
        "bat": bat, "round": 1,
    }
    cb_hit = FakeCallback(uid, data=f"mine:battle:hit:{token}", bot=FakeSender())
    for _ in range(50):
        if uid not in mm.MINE_BATTLE:
            break
        await mm.mine_battle_hit(cb_hit)
    check("победа: бой завершён", uid not in mm.MINE_BATTLE)
    check("победа: ровно 1 самоцвет (кэп)", await gem_total(uid) == 1)

    # ── 9. Бой: поражение → −15 ОД ──
    uid2 = 481002
    await add_user(uid2, "miner2", "Шахтёр2", "")
    await update_user(uid2, ap=50)
    token2 = mm._new_token()
    mm.MINE_TOKEN[uid2] = token2
    mm.MINE_BATTLE[uid2] = {
        "token": token2, "player_hp": 1, "player_hp_max": 100,
        "bat_hp": 999999, "bat_hp_max": 999999, "bat_name": "Летучая мышь", "emoji": "🦇",
        "dodge": 0.0, "armor": 0, "dmg_min": 999, "dmg_max": 999, "loss_ap": 15,
        "bat": bat, "round": 1,
    }
    cb_lose = FakeCallback(uid2, data=f"mine:battle:hit:{token2}", bot=FakeSender())
    for _ in range(50):
        if uid2 not in mm.MINE_BATTLE:
            break
        await mm.mine_battle_hit(cb_lose)
    from database.db import (
        get_user, ACHIEVEMENTS_DEF, ensure_achievements,
        get_achievement_progress, get_achievement_bonus, bump_achievement,
    )
    check("поражение: бой завершён", uid2 not in mm.MINE_BATTLE)
    check("поражение: −15 ОД", (await get_user(uid2))["ap"] == 35)

    # ── 10. Достижение «⛏️ Шахты» (mining) и «👹 Монстры» в копи ──
    await ensure_achievements()
    m_spec = ACHIEVEMENTS_DEF.get("mining")
    check("ACHIEVEMENTS_DEF[mining] есть", bool(m_spec))
    m_thresholds = [(lvl["threshold"], lvl["name"], lvl["bonus"].get("mining_pct"))
                    for lvl in m_spec["levels"]]
    check(
        "mining: пороги 10/50/150/400 и названия Осколок/Старатель/Армадило/Глашатай Скади (+2/+4/+7/+10%)",
        m_thresholds == [
            (10, "Осколок", 2),
            (50, "Старатель", 4),
            (150, "Армадило", 7),
            (400, "Глашатай Скади", 10),
        ],
    )
    _, mon_prog = await get_achievement_progress(uid, "monsters")
    check("победа над Летучей мышью двигает monsters", mon_prog >= 1)

    # Добыча руды (mine_dig) без мыши и с 100% броском двигает mining
    saved_delay = mm.MINE_RESULT_DELAY
    saved_bat = mm._bat
    saved_rand = mm.random.random
    mm.MINE_RESULT_DELAY = (0, 0)
    async def _no_bat():
        return None
    mm._bat = _no_bat
    mm.random.random = lambda: 0.0
    try:
        cb_dig = FakeCallback(uid, data=f"mine:dig:{token}", bot=FakeSender())
        await mm.mine_dig(cb_dig)
    finally:
        mm.MINE_RESULT_DELAY = saved_delay
        mm._bat = saved_bat
        mm.random.random = saved_rand

    _, mine_prog = await get_achievement_progress(uid, "mining")
    check("добыча руды двигает прогресс mining", mine_prog >= 1)
    await bump_achievement(uid, "mining", max(0, 10 - mine_prog))
    m_lvl, m_prog2 = await get_achievement_progress(uid, "mining")
    check("mining: на 10 руды открыт 1 ур. («Осколок»)",
          m_lvl == 1 and m_prog2 >= 10)
    check("mining: бонус 1 ур. = +2%",
          await get_achievement_bonus(uid, "mining", "mining_pct") == 2)

    await close_db()
    print(f"\nSmoke 148: {passed} passed, {failed} failed")
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
