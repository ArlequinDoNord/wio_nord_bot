"""Smoke 143 — Белый Волк Севера: состояния-благословения и бой.

Проверяет:
    1. Состояния-благословения в STATE_CONF: «внимание севера» (+5% урон/уклон.)
       и «благословение севера» (+10% атака/уклон., +5% лечение, −3% магазин).
       BLESSING_STATES / is_blessed / combat_multipliers / state_heal_pct /
       state_shop_discount.
    2. Применение через БД: apply_state_to → get_heal_bonus_pct=5,
       get_shop_discount_pct=3; скидка видна в shop_price_for (−3% на 100 НМ).
    3. Гейт встречи: под благословением _roll_extra_beast волка НЕ бросает;
       после снятия — бросает снова.
    4. Волка нельзя убить: white_wolf_after_hit не опускает HP ниже 1 и
       выставляет авто-победу при остатке <= AUTOWIN.
    5. Бой (big): _white_wolf_defeat выдаёт «благословение севера», списывает
       15 ОД и завершает бой. Бой (small) — «внимание севера».
    6. forest_battle_hit: удар по волку с низким HP ярится → авто-победа (big),
       добычи нет, только благословение.

Запуск: .venv\\Scripts\\python.exe smoke_143.py
"""
import asyncio
import os
import sys

_TEST_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_test_smoke143.db")
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


class CB:
    def __init__(self, data="x", user_id=1):
        self.data = data
        self.from_user = type("U", (), {})()
        self.from_user.id = user_id
        self.message = type("M", (), {})()
        self.message.message_id = 1

    async def answer(self, text=None, show_alert=False, reply_markup=None):
        return None


async def main():
    import config
    config.DB_PATH = _TEST_DB
    import database.db as db
    db.DB_PATH = _TEST_DB

    from database.db import (
        init_db, close_db, add_user, get_user, shop_price_for,
        ensure_forest_enemies,
    )
    from utils.states import (
        STATE_CONF, BLESSING_STATES, is_blessed, combat_multipliers,
        state_heal_pct, state_shop_discount, apply_state_to, clear_state_of,
        get_heal_bonus_pct, get_shop_discount_pct, get_state_info,
    )
    import bot.handlers.forest as forest
    from bot.handlers.forest import white_wolf_after_hit

    await init_db()
    await ensure_forest_enemies()

    print("\n1. Состояния-благословения")
    check("STATE_CONF: «внимание севера»", "внимание севера" in STATE_CONF)
    check("STATE_CONF: «благословение севера»", "благословение севера" in STATE_CONF)
    small = STATE_CONF["внимание севера"]
    big = STATE_CONF["благословение севера"]
    check("малое: +5% урон", abs(small["attack_mult"] - 1.05) < 1e-9)
    check("малое: +5% уклонение", abs(small["dodge_mult"] - 1.05) < 1e-9)
    check("малое: без лечения/магазина",
          "heal_pct" not in small and "shop_discount" not in small)
    check("большое: +10% атака", abs(big["attack_mult"] - 1.10) < 1e-9)
    check("большое: +10% уклонение", abs(big["dodge_mult"] - 1.10) < 1e-9)
    check("большое: +5% лечение", int(big["heal_pct"]) == 5)
    check("большое: −3% магазин", int(big["shop_discount"]) == 3)
    check("большое: сутки (1440 мин)", int(big["default_minutes"]) == 1440)
    check("BLESSING_STATES = оба ключа",
          set(BLESSING_STATES) == {"внимание севера", "благословение севера"})
    check("is_blessed: большое → True", is_blessed(["благословение севера"]))
    check("is_blessed: малое → True", is_blessed(["внимание севера"]))
    check("is_blessed: пьян → False", not is_blessed(["пьян"]))
    mult = combat_multipliers(["благословение севера"])
    check("combat_multipliers: атака ×1.10",
          abs(mult.get("attack_mult", 1) - 1.10) < 1e-9)
    check("combat_multipliers: уклонение ×1.10",
          abs(mult.get("dodge_mult", 1) - 1.10) < 1e-9)
    check("state_heal_pct(большое) = 5", state_heal_pct(["благословение севера"]) == 5)
    check("state_shop_discount(большое) = 3",
          state_shop_discount(["благословение севера"]) == 3)

    print("\n2. Применение через БД и скидка")
    await add_user(143001, "blessed", "B", "T")
    await add_user(143002, "plain", "P", "T")
    await apply_state_to(143001, "благословение севера", caused_by=143001)
    info = await get_state_info(143001)
    check("состояние активно", "благословение севера" in info["names"])
    check("get_heal_bonus_pct = 5", await get_heal_bonus_pct(143001) == 5)
    check("get_shop_discount_pct = 3", await get_shop_discount_pct(143001) == 3)
    check("shop_price_for: 100 НМ → 97 (благословение)",
          await shop_price_for(143001, 100) == 97)
    check("shop_price_for: без благословения 100 → 100",
          await shop_price_for(143002, 100) == 100)

    print("\n3. Гейт встречи под благословением")
    from unittest.mock import patch
    with patch("random.random", lambda: 0.0):
        blessed_beast = await forest._roll_extra_beast(143001)
    check("под благословением волк не встречается", blessed_beast is None)
    await clear_state_of(143001)
    with patch("random.random", lambda: 0.0):
        plain_beast = await forest._roll_extra_beast(143001)
    check("без благословения волк встречается",
          plain_beast and plain_beast.get("key") == "white_wolf")

    print("\n4. Волка нельзя убить (чистая функция)")
    check("HP 120 − 5 → 115, без авто-победы",
          white_wolf_after_hit(120, 5, 20) == (115, False))
    check("HP 25 − 50 (смертельный) → 1, авто-победа",
          white_wolf_after_hit(25, 50, 20) == (1, True))
    check("HP 21 − 1 → 20, авто-победа", white_wolf_after_hit(21, 1, 20) == (20, True))
    check("HP 22 − 1 → 21, без авто-победы", white_wolf_after_hit(22, 1, 20) == (21, False))
    check("HP 15 − 0 → 15, авто-победа", white_wolf_after_hit(15, 0, 20) == (15, True))

    captured = {}

    async def fake_glade_paint(callback, *, text, kb=None, area="glade"):
        captured["text"] = text

    forest._glade_paint = fake_glade_paint

    async def _set_ap(uid, value):
        conn = await db.get_db()
        await conn.execute("UPDATE users SET ap = ? WHERE user_id = ?", (value, uid))
        await conn.commit()

    print("\n5. Поражение от волка выдаёт благословение")
    await add_user(143003, "wolfed", "W", "T")
    await _set_ap(143003, 50)
    forest.FOREST_BATTLE[143003] = {
        "area": "clearing", "loss_ap": 15, "emoji": "🐺",
        "boar_name": "Белый Волк Севера",
    }
    forest.FOREST_TOKEN[143003] = "555555"
    # Большое благословение (ярость).
    await forest._white_wolf_defeat(
        CB("forest:battle:hit:555555", 143003), 143003,
        forest.FOREST_BATTLE[143003], big=True, prefix="")
    user = await get_user(143003)
    check("big: AP списано 15 (50 → 35)", int(user["ap"]) == 35)
    check("big: волк-благословение наложено",
          "благословение севера" in (await get_state_info(143003))["names"])
    check("big: бой завершён", 143003 not in forest.FOREST_BATTLE)
    check("big: текст про БЛАГОСЛОВЕНИЕ",
          "БЛАГОСЛОВЕНИЕ" in (captured.get("text") or ""))
    check("big: текст про −15 ОД", "15" in (captured.get("text") or ""))

    await add_user(143004, "wok", "W", "T")
    await _set_ap(143004, 50)
    forest.FOREST_BATTLE[143004] = {
        "area": "clearing", "loss_ap": 15, "emoji": "🐺",
        "boar_name": "Белый Волк Севера",
    }
    forest.FOREST_TOKEN[143004] = "666666"
    await forest._white_wolf_defeat(
        CB("forest:battle:hit:666666", 143004), 143004,
        forest.FOREST_BATTLE[143004], big=False, prefix="")
    check("small: AP списано 15 (50 → 35)", int((await get_user(143004))["ap"]) == 35)
    check("small: наложено «внимание севера»",
          "внимание севера" in (await get_state_info(143004))["names"])
    check("small: текст про ВНИМАНИЕ",
          "ВНИМАНИЕ" in (captured.get("text") or ""))

    print("\n6. forest_battle_hit: удар по волку с низким HP → ярость (big)")
    await add_user(143005, "wsh", "W", "T")
    await _set_ap(143005, 50)
    forest.FOREST_TOKEN[143005] = "777777"
    forest.FOREST_BATTLE[143005] = {
        "token": "777777", "area": "clearing",
        "player_hp": 100, "player_hp_max": 100,
        "boar_hp": 15, "boar_hp_max": 120,
        "boar_name": "Белый Волк Севера",
        "beast_key": "white_wolf", "is_white_wolf": True,
        "emoji": "🐺", "dodge": 0, "armor": 0,
        "crit_chance": 0, "crit_mult": 1.5,
        "dmg_min": 7, "dmg_max": 12, "loss_ap": 15,
        "bleed_chance": 0, "bleed_dmg": 0,
        "active_bleed": 0, "bleed_ticks": 0, "boar": {}, "round": 1,
    }
    await forest.forest_battle_hit(CB("forest:battle:hit:777777", 143005))
    check("hit: бой завершён (волк не убит, а ярится)",
          143005 not in forest.FOREST_BATTLE)
    check("hit: выдано большое благословение",
          "благословение севера" in (await get_state_info(143005))["names"])
    check("hit: добычи нет — упомянуто благословение, не лут",
          "БЛАГОСЛОВЕНИЕ" in (captured.get("text") or "")
          and "инвентарь" not in (captured.get("text") or ""))
    check("hit: AP списано 15 (50 → 35)", int((await get_user(143005))["ap"]) == 35)

    await close_db()
    print(f"\nSmoke 143: {PASS} passed, {FAIL} failed")
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
