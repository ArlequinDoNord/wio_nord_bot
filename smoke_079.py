"""Smoke v0.15.18: жильё с параметрами в товаре + эффект оружия «stun».

Проверяет:
1. Миграция создаёт items.housing_type / items.housing_slots и
   player_housing.housing_label / player_housing.housing_slots.
2. add_item поддерживает housing_type/housing_slots; get_item их возвращает.
3. set_player_housing с label и произвольным числом слотов; фолбэк на дефолт типа.
4. Эффект оружия 'stun' добавлен в словари боя (dungeon) и админки.
5. Простое приведение боевого штрафа: при применении stun в бой
   weapon_effect_dmg > 0 даёт шанс промаха врага (roll_dodge(penalty)).

Запуск: .venv\\Scripts\\python.exe smoke_079.py
"""
import asyncio
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke079.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB
os.environ["ADMIN_IDS"] = "400001"

sys.path.insert(0, os.path.dirname(__file__))

CHECK = []


def check(name, cond):
    CHECK.append((name, bool(cond)))


async def main():
    import builtins
    from database import db as D
    def step(s):
        print(f"[step] {s}", flush=True)

    step("init_db")
    await D.init_db()
    step("init_db done")
    conn = await D.get_db()
    step("conn got")

    # 1. Миграции создали колонки.
    cols_items = {r['name'] for r in (await (await conn.execute("PRAGMA table_info(items)")).fetchall())}
    cols_house = {r['name'] for r in (await (await conn.execute("PRAGMA table_info(player_housing)")).fetchall())}
    check("mi.items.housing_type", "housing_type" in cols_items)
    check("mi.items.housing_slots", "housing_slots" in cols_items)
    check("mi.player.housing_label", "housing_label" in cols_house)
    check("mi.player.housing_slots", "housing_slots" in cols_house)

    # 2. add_item с параметрами жилья.
    uid = 700001
    await D.add_user(uid, "testpilot", "Test", "Pilot")
    item_id = await D.add_item(
        name="Особняк «Янтарный» №1", description="Индивидуальный дом.",
        price=8000, sell_price=4000, rarity=5, category="housing", stock=1,
        added_by=400001, housing_type="mansion", housing_slots=8,
    )
    item = await D.get_item(item_id)
    check("item.housing_type", item.get("housing_type") == "mansion")
    check("item.housing_slots", item.get("housing_slots") == 8)

    # 3. set_player_housing с label/slots и фолбэк слотов по типу.
    await D.set_player_housing(uid, "mansion", housing_label="Особняк «Янтарный» №1",
                               housing_slots=8)
    h = await D.get_player_housing(uid)
    check("house.label", h.get("housing_label") == "Особняк «Янтарный» №1")
    check("house.slots", h.get("housing_slots") == 8)
    eff = h.get("housing_slots") or D.HOUSING_TYPES[h["housing_type"]]["slots"]
    check("house.eff_slots", eff == 8)

    # Фолбэк без явного числа слотов — дефолт типа.
    await D.set_player_housing(uid, "studio")
    h2 = await D.get_player_housing(uid)
    eff2 = h2.get("housing_slots") or D.HOUSING_TYPES[h2["housing_type"]]["slots"]
    check("house.fallback_studio_slots", eff2 == 1)

    # 4. stun в боевых словарях.
    step("import dungeon/admin")
    import bot.handlers.dungeon as dung
    import bot.handlers.admin as adm
    step("imports done")
    check("stun.label", "stun" in dung.WEAPON_EFFECT_LABELS)
    check("stun.emoji", "stun" in dung.WEAPON_EFFECT_EMOJI)
    check("stun.admin_label", "stun" in adm.WEAPON_EFFECT_LABELS)

    # 5. roll_dodge работает как штраф точности (шанс промаха = penalty%).
    step("rolling")
    from utils.combat import roll_dodge
    hits = sum(1 for _ in range(1000) if roll_dodge(50))
    check("stun.roll50_approx", 400 <= hits <= 600)
    misses0 = sum(1 for _ in range(500) if roll_dodge(0))
    check("stun.roll0_zero", misses0 == 0)

    # 6. Обновление полей через update_item (редактор).
    step("editor")
    await D.update_item(item_id, rarity=4)
    check("edit.rarity", (await D.get_item(item_id))["rarity"] == 4)
    await D.update_item(item_id, housing_slots=None)
    check("edit.housing_slots_none", (await D.get_item(item_id)).get("housing_slots") is None)
    step("done")

    await D.close_db()

    for name, ok in CHECK:
        print(f"{'OK' if ok else 'FAIL'}  {name}")
    failed = sum(1 for _, ok in CHECK if not ok)
    print(f"Smoke 079: {len(CHECK) - failed} passed, {failed} failed")
    sys.exit(1 if failed else 0)


asyncio.run(main())