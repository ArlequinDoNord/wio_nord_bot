"""Smoke 138 — Белый Волк Севера в лесу и редактор дропов у врагов.

Проверяет:
    1. Сид волка: ключ 'white_wolf', spot forest, шанс 2%, своя гарантия (36),
       HP 120 / урон 7–12 / уклонение 20 / кровотечение 30%×3, без дропов
       (волк оставляет только суточные благословения).
    2. Спавн: _roll_extra_beast бросает зверей кроме кабана (Белый Волк может
       выпасть, кабан сюда не попадает), эмодзи зверя по ключу.
    3. Админ-редактор дропов источника: экран дропов открывается, кнопка дропа
       ведёт в редактор (шанс/кол-во/удаление), правка сохраняется, а удаление
       больше НЕ падает (регресс старого бага с кнопкой-именем лута).
    4. Рудимент player_dmg_min/max убран: нет в полях/сидах, колонки БД
       вычищаются (в т.ч. миграцией legacy-БД).

Запуск: .venv\\Scripts\\python.exe smoke_138.py
"""
import asyncio
import os
import sys

_TEST_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_test_smoke138.db")
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


def _callbacks(markup):
    try:
        return [b.callback_data for row in markup.inline_keyboard for b in row]
    except Exception:
        return []


class CBMsg:
    def __init__(self):
        self.text = None
        self.markup = None

    async def edit_text(self, text, reply_markup=None):
        self.text = text
        self.markup = reply_markup
        return None

    async def answer(self, text=None, reply_markup=None):
        self.text = text
        self.markup = reply_markup
        return None


class CB:
    def __init__(self, data="x"):
        self.data = data
        self.from_user = type("U", (), {})()
        self.from_user.id = 1
        self.message = CBMsg()

    async def answer(self, text=None, show_alert=False, reply_markup=None):
        return None


class Msg:
    def __init__(self, text=None):
        self.text = text
        self.from_user = type("U", (), {})()
        self.from_user.id = 1
        self.sent = []

    async def answer(self, text=None, reply_markup=None):
        self.sent.append(text)
        return None


class State:
    def __init__(self, **kw):
        self.d = dict(kw)
        self._state = None

    async def get_data(self):
        return self.d

    async def update_data(self, **kw):
        self.d.update(kw)

    async def set_state(self, s):
        self._state = s

    async def clear(self):
        self.d = {}
        self._state = None


async def main():
    from config import (
        FOREST_WHITE_WOLF_CHANCE, FOREST_WHITE_WOLF_PITY_TARGET,
        FOREST_WHITE_WOLF_BLEED_CHANCE, FOREST_WHITE_WOLF_BLEED_DMG,
    )
    from database.db import (
        init_db, close_db, ensure_forest_enemies, get_source_enemy_by_key,
        get_source_enemy_drops, get_item, get_item_by_name,
        get_forest_wolf_attempts, set_forest_wolf_attempts, add_user,
    )
    from bot.handlers.forest import _roll_extra_beast, _beast_emoji
    from unittest.mock import patch
    import bot.handlers.admin as admin

    await init_db()

    print("\n1. Сид волка")
    await ensure_forest_enemies()
    wolf = await get_source_enemy_by_key("forest", "white_wolf")
    check("волк в БД по ключу 'white_wolf'", bool(wolf))
    check("волк: spot = forest", wolf and wolf['spot'] == "forest")
    check("волк: шанс из БД = конфиг (2%)",
          wolf and abs(float(wolf['chance']) - FOREST_WHITE_WOLF_CHANCE) < 0.01)
    check("волк: своя гарантия = конфиг (36)",
          wolf and int(wolf['pity_target']) == FOREST_WHITE_WOLF_PITY_TARGET)
    check("волк: HP = 120", wolf and int(wolf['hp']) == 120)
    check("волк: урон 7–12", wolf and int(wolf['dmg_min']) == 7 and int(wolf['dmg_max']) == 12)
    check("волк: уклонение 20%", wolf and int(wolf['dodge']) == 20)
    check("волк: потеря ОД = 15", wolf and int(wolf['loss_ap']) == 15)
    check("волк: шанс кровотечения = конфиг",
          wolf and int(wolf['bleed_chance']) == FOREST_WHITE_WOLF_BLEED_CHANCE)
    check("волк: урон кровотечения = конфиг",
          wolf and int(wolf['bleed_dmg']) == FOREST_WHITE_WOLF_BLEED_DMG)
    check("волк: включён", wolf and wolf['enabled'] == 1)
    check("волк: без дропов (только благословения)",
          len(await get_source_enemy_drops("forest", wolf['id'])) == 0)
    check("legacy-волк 'wolf' вычищен",
          (await get_source_enemy_by_key("forest", "wolf")) is None)

    print("\n2. Сид идемпотентен")
    check("повторный сид — без дублей", await ensure_forest_enemies() is False)
    boar = await get_source_enemy_by_key("forest", "boar")
    check("кабан на месте вместе с волком", bool(boar))

    print("\n3. Предметы волка — только лут")
    for name in ("Мясо волка", "Шкура волка", "Клык волка"):
        full = await get_item((await get_item_by_name(name))['id'])
        check(f"«{name}» loot-only (market_ok=0, loot_only=1, is_available=0)",
              full['market_ok'] == 0 and (full['loot_only'] or 0) == 1
              and (full['is_available'] or 0) == 0)

    print("\n4. Спавн и эмодзи")
    check("эмодзи кабана", _beast_emoji({"key": "boar"}) == "🐗")
    check("эмодзи волка", _beast_emoji({"key": "white_wolf"}) == "🐺")
    check("эмодзи по умолчанию", _beast_emoji(None) == "🐗")
    with patch("random.random", lambda: 0.0):
        beast = await _roll_extra_beast()
    check("_roll_extra_beast ловит Белого Волка", beast and beast.get('key') == 'white_wolf')
    check("_roll_extra_beast НЕ возвращает кабана",
          beast is not None and beast.get('key') != 'boar')
    with patch("random.random", lambda: 0.99):
        beast_miss = await _roll_extra_beast()
    check("_roll_extra_beast: высокий бросок — пусто", beast_miss is None)
    await add_user(999001, "wolf_test", "Wolf", "Test")
    check("счётчик волка стартует с нуля", await get_forest_wolf_attempts(999001) == 0)
    await set_forest_wolf_attempts(999001, FOREST_WHITE_WOLF_PITY_TARGET - 1)
    check("счётчик волка сохраняется",
          await get_forest_wolf_attempts(999001) == FOREST_WHITE_WOLF_PITY_TARGET - 1)
    with patch("random.random", lambda: 0.99):
        beast_pity = await _roll_extra_beast(999001)
    check("гарантия волка: на 36-й поиск ловит даже при высоком броске",
          beast_pity and beast_pity.get('key') == 'white_wolf')
    with patch("random.random", lambda: 0.99):
        beast_fresh = await _roll_extra_beast(999002)
    check("гарантия волка не срабатывает раньше срока", beast_fresh is None)

    print("\n5. Админ-редактор дропов")

    async def fake_perm(uid, perm):
        return True

    admin.has_permission = fake_perm
    state = State()
    bid = boar['id']

    cb = CB(f"enemy:drops:forest:forest:{bid}")
    await admin.admin_enemies_drops(cb, state)
    check("экран дропов открылся", bool(cb.message.text) and "ДРОПЫ" in cb.message.text)
    cbs = _callbacks(cb.message.markup)
    check("кнопка дропа ведёт в редактор (не в удаление)",
          any(c.startswith("enemy:dropedit:") for c in cbs)
          and not any(c.startswith("enemy:dropdel:") for c in cbs))

    print("\n6. Экран дропа и правка шанса")
    cbe = CB(f"enemy:dropedit:forest:forest:{bid}:0")
    await admin.admin_enemies_drop_edit(cbe, state)
    check("экран дропа показывает шанс", "Шанс: 50%" in (cbe.message.text or ""))
    await admin.admin_enemies_drop_edit_chance(
        CB(f"enemy:dropch:forest:forest:{bid}:0"), state)
    check("состояние: правка дропа #0", state.d.get('drop_index') == 0)
    await admin.admin_enemies_drop_chance_value(Msg("30"), state)
    drops = await get_source_enemy_drops("forest", bid)
    check("шанс дропа сохранён (30%)", abs(float(drops[0]['chance']) - 0.30) < 1e-9)

    print("\n7. Правка количества")
    await admin.admin_enemies_drop_edit_qty(
        CB(f"enemy:dropq:forest:forest:{bid}:0"), state)
    await admin.admin_enemies_drop_qty_value(Msg("3"), state)
    drops = await get_source_enemy_drops("forest", bid)
    check("кол-во дропа сохранено (3)", int(drops[0]['qty']) == 3)

    print("\n8. Удаление дропа не падает (регресс)")
    before = len(await get_source_enemy_drops("forest", bid))
    await admin.admin_enemies_drop_del(
        CB(f"enemy:dropdel:forest:forest:{bid}:0"), state)
    after = len(await get_source_enemy_drops("forest", bid))
    check("дроп удалён", after == before - 1)

    print("\n9. Рудимент player_dmg_min/max убран (v0.23.3)")
    from database.db import (
        SOURCE_ENEMY_FIELDS, ENEMY_SEED_FIELDS,
        get_source_enemy, ensure_fishing_enemies,
    )
    from config import FOREST_BOAR_SEED, FOREST_WHITE_WOLF_SEED, MOLLUSK_SEED
    check("SOURCE_ENEMY_FIELDS без player_dmg_*",
          "player_dmg_min" not in SOURCE_ENEMY_FIELDS
          and "player_dmg_max" not in SOURCE_ENEMY_FIELDS)
    check("ENEMY_SEED_FIELDS без player_dmg_*",
          "player_dmg_min" not in ENEMY_SEED_FIELDS
          and "player_dmg_max" not in ENEMY_SEED_FIELDS)
    check("сиды леса/рыбалки без player_dmg_*",
          all("player_dmg_min" not in s and "player_dmg_max" not in s
              for s in (FOREST_BOAR_SEED, FOREST_WHITE_WOLF_SEED, MOLLUSK_SEED)))
    forest_keys = set((await get_source_enemy("forest", bid)).keys())
    check("колонки forest_enemies убраны",
          "player_dmg_min" not in forest_keys and "player_dmg_max" not in forest_keys)
    await ensure_fishing_enemies()
    mollusk = await get_source_enemy_by_key("fishing", "mollusk", "reservoir")
    fish_keys = set(mollusk.keys())
    check("колонки fishing_enemies убраны",
          "player_dmg_min" not in fish_keys and "player_dmg_max" not in fish_keys)

    print("\n9b. Кровотечение и броня (поля/колонки/админка)")
    check("SOURCE_ENEMY_FIELDS содержит bleed_*",
          "bleed_chance" in SOURCE_ENEMY_FIELDS and "bleed_dmg" in SOURCE_ENEMY_FIELDS)
    check("ENEMY_SEED_FIELDS содержит bleed_*",
          "bleed_chance" in ENEMY_SEED_FIELDS and "bleed_dmg" in ENEMY_SEED_FIELDS)
    wolf_keys = set((await get_source_enemy_by_key("forest", "white_wolf")).keys())
    check("колонки bleed_* есть у white_wolf",
          "bleed_chance" in wolf_keys and "bleed_dmg" in wolf_keys)
    check("ENEMY_FIELDS: есть правка шанса кровотечения",
          "bleed_chance" in admin.ENEMY_FIELDS)
    check("ENEMY_FIELDS: есть правка урона кровотечения",
          "bleed_dmg" in admin.ENEMY_FIELDS)

    print("\n9c. Броня у врагов (поля/колонки/админка)")
    check("SOURCE_ENEMY_FIELDS содержит armor", "armor" in SOURCE_ENEMY_FIELDS)
    check("ENEMY_FIELDS: есть правка брони", "armor" in admin.ENEMY_FIELDS)
    check("ENEMY_FIELD_LABELS: есть броня", "armor" in admin.ENEMY_FIELD_LABELS)
    check("ENEMY_INPUT_PROMPTS: есть броня", "armor" in admin.ENEMY_INPUT_PROMPTS)
    from database.db import ENEMY_EDITABLE_FIELDS
    check("ENEMY_EDITABLE_FIELDS (данжи) содержит armor", "armor" in ENEMY_EDITABLE_FIELDS)
    check("колонка armor есть у white_wolf", "armor" in wolf_keys)
    await ensure_fishing_enemies()
    mollusk2 = await get_source_enemy_by_key("fishing", "mollusk", "reservoir")
    check("колонка armor есть у моллюска (fishing)",
          "armor" in set(mollusk2.keys()))

    # Миграция legacy-БД: колонки были — init_db их вычищает.
    from database.db import get_db, init_db as _init_db
    conn = await get_db()
    await conn.execute("ALTER TABLE forest_enemies ADD COLUMN player_dmg_min INTEGER DEFAULT 5")
    await conn.execute("ALTER TABLE forest_enemies ADD COLUMN player_dmg_max INTEGER DEFAULT 9")
    await conn.commit()
    await _init_db()
    legacy_keys = set((await get_source_enemy("forest", bid)).keys())
    check("миграция вычищает legacy-колонки player_dmg_*",
          "player_dmg_min" not in legacy_keys and "player_dmg_max" not in legacy_keys)

    await close_db()
    print(f"\nSmoke 138: {PASS} passed, {FAIL} failed")
    sys.exit(1 if FAIL else 0)


def item_ok(item):
    return bool(item)


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
