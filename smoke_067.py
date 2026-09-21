"""Smoke v0.14.3: особые эффекты оружия (DoT на врага в подземелье).

Проверяет:
1. Колонки items.weapon_effect / weapon_effect_chance / weapon_effect_dmg созданы.
2. add_item создаёт оружие с эффектом (poison, шанс 100, урон 10).
3. get_equipped_weapon возвращает оружие вместе с эффектом;
   get_player_weapon_damage возвращает урон.
4. Бой: удар с шансом 100% накладывает эффект на врага — в FSM появляются
   enemy_effect / enemy_effect_dmg / enemy_effect_ticks (3 хода), в тексте
   атаки появляется строка про отравление.
5. Тики: в начале следующего хода враг теряет урон эффекта, тики уменьшаются.
6. Враг, добитый эффектом, «пал» из-за него — выводится кнопка «Продолжить путь».
7. Админ-панель: словари WEAPON_EFFECT_LABELS (dungeon и admin), кнопка
   weapon_effect_choice_markup, DROP_ITEM_STAT_LABELS содержат новые поля.

Запуск: .venv\\Scripts\\python.exe smoke_067.py
"""
import asyncio
import os
import sys
from types import SimpleNamespace

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke067.db")
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

    async def edit_caption(self, *a, **kw):
        self.sent.append(("edit_caption", a, kw))

    async def delete(self, *a, **kw):
        self.sent.append(("delete", a, kw))

    async def answer_photo(self, *a, **kw):
        self.sent.append(("answer_photo", a, kw))

    async def __getattr__(self, name):
        async def _noop(*a, **kw):
            return None
        return _noop


class FakeCallback:
    def __init__(self, user_id, data="", message=None):
        self.from_user = SimpleNamespace(id=user_id)
        self.message = message or FakeMessage()
        self.data = data
        self.alerts = []

    async def answer(self, text=None, *a, **kw):
        self.alerts.append(text)


class FakeState:
    def __init__(self, state=None, data=None):
        self._state = state
        self._data = dict(data or {})
        self.cleared = False

    async def get_state(self):
        return self._state

    async def set_state(self, s):
        self._state = s

    async def get_data(self):
        return dict(self._data)

    async def update_data(self, **kw):
        self._data.update(kw)

    async def clear(self):
        self._data.clear()
        self._state = None
        self.cleared = True


def sent_text(msg):
    for kind, a, kw in msg.sent:
        if kind == "answer" and a:
            return a[0]
        if kind == "answer_photo" and kw.get('caption'):
            return kw.get('caption')
        if kind == "edit_text" and a:
            return a[0]
    return ""


def last_sent_text(msg):
    text = ""
    for kind, a, kw in msg.sent:
        if kind == "answer" and a:
            text = a[0]
        if kind == "answer_photo" and kw.get('caption'):
            text = kw.get('caption')
    return text


def markup_callbacks(markup):
    if not markup:
        return []
    return [b.callback_data for row in markup.inline_keyboard for b in row]


async def run():
    from database.db import (
        init_db, close_db, seed_default_items, seed_dungeon,
        ensure_dungeon_shop_items,
        add_user, add_item, get_item, get_db, get_equipped_weapon,
        get_player_weapon_damage, add_inventory_item, set_equipment_slot,
        update_item,
        get_all_dungeons, get_dungeon_enemies,
        start_dungeon_run, get_active_run, end_run,
    )
    from bot.handlers import dungeon as DH

    await init_db()
    await seed_default_items()
    await seed_dungeon()
    await ensure_dungeon_shop_items()

    uid = 999872
    await add_user(uid, "wpoison", "Тест", "")

    passed = 0
    failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
        else:
            failed += 1
            print(f"  FAIL: {name}")

    # ── 1. Колонки items ──
    conn = await get_db()
    cur = await conn.execute("PRAGMA table_info(items)")
    cols = [r['name'] for r in await cur.fetchall()]
    check("колонки weapon_effect* созданы",
          all(c in cols for c in ("weapon_effect", "weapon_effect_chance", "weapon_effect_dmg")))

    # ── 2. add_item с эффектом оружия ──
    weapon_id = await add_item(
        name="Клинок отрав", description="", price=50, sell_price=25,
        rarity=1, category="weapon", stock=-1, added_by=1,
        damage=6, weapon_effect="poison", weapon_effect_chance=100,
        weapon_effect_dmg=10,
    )
    weapon = await get_item(weapon_id)
    check("add_item сохранил эффект оружия",
          weapon is not None
          and weapon['category'] == 'weapon'
          and weapon['weapon_effect'] == 'poison'
          and weapon['weapon_effect_chance'] == 100
          and weapon['weapon_effect_dmg'] == 10)

    # ── 3. get_equipped_weapon ──
    await add_inventory_item(uid, weapon_id, 1)
    await set_equipment_slot(uid, 'weapon', weapon_id)
    eq_weapon = await get_equipped_weapon(uid)
    check("get_equipped_weapon возвращает оружие с эффектом",
          eq_weapon is not None
          and eq_weapon['weapon_effect'] == 'poison'
          and eq_weapon['weapon_effect_dmg'] == 10)
    check("get_player_weapon_damage = 6",
          await get_player_weapon_damage(uid) == 6)

    # ── Враг: убрать уклонение и поднять HP, чтобы бой был детерминированным ──
    dng = (await get_all_dungeons(training=False))[0]
    enemies = await get_dungeon_enemies(dng['id'])
    foes = [e for e in enemies if not e['is_boss']]
    check("есть обычные враги", bool(foes))
    foe = foes[0]
    await conn.execute("UPDATE dungeon_enemies SET dodge = 0, hp = 500 WHERE id = ?", (foe['id'],))
    await conn.commit()

    # ── 4. Проклятие эффекта при ударе ──
    await start_dungeon_run(uid, dng['id'])
    st = FakeState(data={
        "current_enemy_id": foe['id'],
        "current_enemy_hp": 500,
        "dungeon_step": 1,
    })
    cb = FakeCallback(uid, data=f"dungeon:attack:{foe['id']}:1", message=FakeMessage())
    await DH.dungeon_attack(cb, st, bot=None)
    check("при попадании эффект наложен на врага",
          st._data.get('enemy_effect') == 'poison'
          and st._data.get('enemy_effect_dmg') == 10
          and st._data.get('enemy_effect_ticks') == 3)
    text1 = last_sent_text(cb.message)
    check("в тексте боя есть строка про отравление врага",
          "отравил" in text1 and "HP врагу каждый ход" in text1)
    hp_after_hit = st._data.get('current_enemy_hp')
    check("удар прошёл (HP врага уменьшился)", 0 < hp_after_hit < 500)

    # ── 5. Тик эффекта в начале следующего хода (без повторного прока) ──
    await update_item(weapon_id, weapon_effect_chance=0)
    cb2 = FakeCallback(uid, data=f"dungeon:attack:{foe['id']}:2", message=FakeMessage())
    await DH.dungeon_attack(cb2, st, bot=None)
    check("тик эффекта в начале хода: HP врага уменьшился более чем на 10",
          st._data.get('current_enemy_hp') < hp_after_hit - 10)
    check("тики эффекта уменьшены (3 -> 2)",
          st._data.get('enemy_effect_ticks') == 2)

    # ── 6. Враг, добитый эффектом ──
    # У оружия: урон 0 (удар не убьёт), шанс 100 (прокае первый ход), эффект 10.
    await update_item(weapon_id, damage=0, weapon_effect_chance=100, weapon_effect_dmg=10)
    await end_run((await get_active_run(uid))['id'], 0)
    await conn.execute("UPDATE dungeon_enemies SET dodge = 0, hp = 8 WHERE id = ?", (foe['id'],))
    await conn.commit()
    await start_dungeon_run(uid, dng['id'])
    st3 = FakeState(data={
        "current_enemy_id": foe['id'],
        "current_enemy_hp": 8,
        "dungeon_step": 1,
    })
    cb3 = FakeCallback(uid, data=f"dungeon:attack:{foe['id']}:1", message=FakeMessage())
    await DH.dungeon_attack(cb3, st3, bot=None)
    check("первый удар: враг выжил и отравлен",
          st3._data.get('current_enemy_hp') > 0
          and st3._data.get('enemy_effect') == 'poison')

    cb4 = FakeCallback(uid, data=f"dungeon:attack:{foe['id']}:2", message=FakeMessage())
    await DH.dungeon_attack(cb4, st4 := st3, bot=None)
    check("второй ход: тик яда добил врага",
          st4._data.get('current_enemy_hp') == 0)
    text4 = last_sent_text(cb4.message)
    check("в тексте победы видно, что враг пал от эффекта",
          "пал от отравления" in text4 or "повержен" in text4)
    win_markup = None
    for kind, a, kw in cb4.message.sent:
        if kw.get('reply_markup'):
            win_markup = kw['reply_markup']
    check("после падения врага от эффекта предлагается продолжить путь",
          any(x.startswith("dungeon:continue")
              for x in markup_callbacks(win_markup)))

    # ── 7. Админ-панель: новые поля эффектов ──
    from bot.handlers.admin import (
        WEAPON_EFFECT_LABELS as ADMIN_WEF,
        weapon_effect_choice_markup,
        DROP_ITEM_STAT_LABELS,
    )
    check("словари эффектов идентичны (admin vs dungeon)",
          set(ADMIN_WEF.keys()) == set(DH.WEAPON_EFFECT_LABELS.keys()))
    check("список эффектов admin: poison/bleed/frostbite",
          "poison" in ADMIN_WEF and "bleed" in ADMIN_WEF and "frostbite" in ADMIN_WEF)
    weff_markup = weapon_effect_choice_markup()
    weff_cbs = markup_callbacks(weff_markup)
    check("кнопка «Без эффекта» есть в меню",
          "weff:none" in weff_cbs)
    check("в характеристиках дропа есть шанс и урон эффекта",
          "weapon_effect_chance" in DROP_ITEM_STAT_LABELS
          and "weapon_effect_dmg" in DROP_ITEM_STAT_LABELS)

    await close_db()
    print(f"\nSmoke 067: {passed} passed, {failed} failed")
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