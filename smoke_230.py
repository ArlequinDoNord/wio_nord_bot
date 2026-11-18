# -*- coding: utf-8 -*-
"""Smoke 230 — иммунитеты и сопротивления врагов к эффектам (шаг 2).

Правила (решения владельца 2026-11-18):
- иммунитет: вид эффекта на этого врага не накладывается совсем;
- сопротивление: шанс наложения вида умножается на долю (0.5 = вдвое реже);
- редактор: переключение без защиты → иммунитет → ×0.5 → без защиты.

Прогон: .\\.venv\\Scripts\\python.exe smoke_230.py
"""
import asyncio
import os
import sys
from types import SimpleNamespace

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke230.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB

sys.path.insert(0, os.path.dirname(__file__))


class FakeMessage:
    def __init__(self):
        self.sent = []
        self.photo = None
        self.text = ""

    async def answer(self, *a, **kw):
        self.sent.append(("answer", a, kw))

    async def edit_text(self, *a, **kw):
        self.sent.append(("edit_text", a, kw))

    async def answer_photo(self, *a, **kw):
        self.sent.append(("answer_photo", a, kw))

    async def __getattr__(self, name):
        async def _noop(*a, **kw):
            return None
        return _noop


class FakeCallback:
    def __init__(self, user_id, data="", message=None):
        self.from_user = SimpleNamespace(id=user_id, username="u", full_name="u")
        self.message = message or FakeMessage()
        self.data = data

    async def answer(self, text=None, *a, **kw):
        return True


class FakeState:
    def __init__(self, data=None):
        self._data = dict(data or {})

    async def get_data(self):
        return dict(self._data)

    async def update_data(self, **kw):
        self._data.update(kw)

    async def clear(self):
        self._data.clear()


def all_text(msg):
    out = []
    for kind, a, kw in msg.sent:
        if a:
            out.append(str(a[0]))
        if kw.get("caption"):
            out.append(str(kw["caption"]))
    return " | ".join(out)


async def run():
    from database.db import (
        init_db, close_db, seed_default_items, seed_dungeon, ensure_dungeon_shop_items,
        add_user, add_item, get_db, get_equipped_weapon, add_inventory_item,
        set_equipment_slot, update_item, get_all_dungeons, get_dungeon_enemies,
        start_dungeon_run, get_active_run, end_run, get_enemy_effect_resist,
        set_enemy_effect_resist,
    )
    from bot.handlers import dungeon as DH
    from bot.handlers import admin as adm
    from utils import effects as E

    await init_db()
    await seed_default_items()
    await seed_dungeon()
    await ensure_dungeon_shop_items()

    uid = 999230
    ADMIN = 999231
    await add_user(uid, "res230", "Тест", "")
    await add_user(ADMIN, "admin230", "Админ", "")
    conn = await get_db()
    await conn.execute("INSERT INTO user_roles (telegram_id, role) VALUES (?, 'super_admin')", (ADMIN,))
    await conn.commit()

    passed = failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
            print(f"  OK  {name}")
        else:
            failed += 1
            print(f"  FAIL: {name}")

    print("\n1. Разбор и правила в модуле")
    check("пустые данные = без защиты", E.parse_resist(None) == {"immune": [], "resist": {}})
    check("битый JSON не ломает", E.parse_resist("{не json") == {"immune": [], "resist": {}})
    r = E.parse_resist({"immune": ["poison", "нет-такого"], "resist": {"stun": 0.5, "bleed": 9}})
    check("неизвестные виды отброшены", r["immune"] == ["poison"])
    check("доля ограничена 0..1", r["resist"] == {"stun": 0.5, "bleed": 1.0})
    check("иммунитет работает", E.is_immune(r, "poison") and not E.is_immune(r, "bleed"))
    check("шанс ×0.5: 40 → 20", E.effective_chance(40, r, "stun") == 20)
    check("без сопротивления шанс прежний", E.effective_chance(40, r, "bleed") == 40)

    print("\n2. Хранение в БД")
    dng = (await get_all_dungeons(training=False))[0]
    enemies = await get_dungeon_enemies(dng['id'])
    foe = [e for e in enemies if not e['is_boss']][0]
    await set_enemy_effect_resist(foe['id'], {"immune": ["poison"], "resist": {"stun": 0.5}})
    got = await get_enemy_effect_resist(foe['id'])
    check("записано и прочитано", got == {"immune": ["poison"], "resist": {"stun": 0.5}})

    print("\n3. Бой: иммунный к яду враг не получает яд от оружия")
    weapon_id = await add_item(
        name="Клинок яда 230", description="", price=50, sell_price=25, rarity=1,
        category="weapon", stock=-1, added_by=1, damage=6,
        weapon_effect="poison", weapon_effect_chance=100, weapon_effect_dmg=10)
    await add_inventory_item(uid, weapon_id, 1)
    await set_equipment_slot(uid, 'weapon', weapon_id)
    check("оружие экипировано", (await get_equipped_weapon(uid))["weapon_effect"] == "poison")
    await conn.execute("UPDATE dungeon_enemies SET dodge = 0, hp = 500 WHERE id = ?", (foe['id'],))
    await conn.commit()
    await start_dungeon_run(uid, dng['id'])
    st = FakeState({"current_enemy_id": foe['id'], "current_enemy_hp": 500, "dungeon_step": 1})
    msg = FakeMessage()
    cb = FakeCallback(uid, data=f"dungeon:attack:{foe['id']}:1", message=msg)
    await DH.dungeon_attack(cb, st, bot=None)
    check("яд не наложен на иммунного врага",
          "poison" not in (st._data.get("enemy_dots") or {}))
    check("в бою есть сообщение об иммунитете",
          "невосприимчив" in all_text(msg))
    await end_run((await get_active_run(uid))['id'], 0)

    print("\n4. Редактор: переключение без защиты → иммунитет → ×0.5 → без защиты")
    await set_enemy_effect_resist(foe['id'], {"immune": [], "resist": {}})
    admin_cb = lambda idx: FakeCallback(ADMIN, data=f"enemy:res:tog:{foe['id']}:{idx}")
    await adm.enemy_resist_toggle(admin_cb(1), FakeState())  # 1 = кровотечение
    r1 = await get_enemy_effect_resist(foe['id'])
    check("шаг 1: иммунитет к кровотечению", r1["immune"] == ["bleed"])
    await adm.enemy_resist_toggle(admin_cb(1), FakeState())
    r2 = await get_enemy_effect_resist(foe['id'])
    check("шаг 2: сопротивление ×0.5", r2["immune"] == [] and r2["resist"] == {"bleed": 0.5})
    await adm.enemy_resist_toggle(admin_cb(1), FakeState())
    r3 = await get_enemy_effect_resist(foe['id'])
    check("шаг 3: защиты нет", r3 == {"immune": [], "resist": {}})

    print("\n5. Экран иммунитетов открывается и показывает виды")
    m = FakeMessage()
    await adm.enemy_resist_screen(FakeCallback(ADMIN, data=f"enemy:res:{foe['id']}", message=m), FakeState())
    check("экран показан", "ИММУНИТЕТЫ" in all_text(m))

    await close_db()
    print(f"\nИТОГО: {passed} passed, {failed} failed")
    return failed


if __name__ == "__main__":
    sys.exit(1 if asyncio.run(run()) else 0)
