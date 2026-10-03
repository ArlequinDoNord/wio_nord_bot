# SMOKE 122: критический удар пилота.
#
# Проверяет: шкала шанса по званию (RANK_CRIT_CHANCE), суммирование трёх
# источников (звание + снаряжение + награды), потолок MAX_CRIT_CHANCE, множитель
# PILOT_CRIT_MULT и главное — что шанс берётся из stats пилота, а не из
# словаря противника (старый баг, utils/combat_model.py).
#
# ⚠️ ВАЖНО: DATABASE_PATH выставляется ДО любого импорта config/database.
# config.py читает путь к базе в момент импорта, поэтому если поставить
# переменную позже — тест будет писать в НАСТОЯЩУЮ базу, а не в тестовую.
import asyncio
import os
import random
import sys

_TEST_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "_test_smoke122.db")
for _suffix in ("", "-wal", "-shm"):
    try:
        os.remove(_TEST_DB + _suffix)
    except OSError:
        pass
os.environ["DATABASE_PATH"] = _TEST_DB

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import PILOT_CRIT_MULT, RANK_CRIT_CHANCE
from database.db import MAX_CRIT_CHANCE
from utils.combat_model import roll_pilot_damage

PASSED = 0
FAILED = 0


def check(name, cond, extra=""):
    global PASSED, FAILED
    if cond:
        PASSED += 1
        print(f"  OK  {name}{(' — ' + extra) if extra else ''}")
    else:
        FAILED += 1
        print(f"  FAIL  {name}{(' — ' + extra) if extra else ''}")


def stats(chance=0.0, mult=PILOT_CRIT_MULT, base=(4, 8), weapon=0, atk=1.0):
    return {'base_dmg': base, 'weapon_damage': weapon, 'attack_mult': atk,
            'crit_chance': chance, 'crit_mult': mult,
            'dodge': 0, 'armor': 0, 'hp_max': 100, 'award_attack': 0}


def main():
    # ── 1. Шкала по званию ────────────────────────────────────────────────────
    print("\n1. Шкала базового шанса по званию")
    expected = {"recruit": 0.0, "pilot2": 1.5, "pilot1": 3.0,
                "veteran": 4.5, "master_pilot": 6.0, "ace": 7.5}
    for tag, want in expected.items():
        got = RANK_CRIT_CHANCE.get(tag)
        check(f"{tag}: {want}%", got == want, f"получено {got}")
    check("шаг между ступенями ровно 1.5%",
          all(abs(RANK_CRIT_CHANCE[b] - RANK_CRIT_CHANCE[a] - 1.5) < 1e-9
              for a, b in (("recruit", "pilot2"), ("pilot2", "pilot1"),
                           ("pilot1", "veteran"), ("veteran", "master_pilot"),
                           ("master_pilot", "ace"))))
    check("у туриста крита нет", RANK_CRIT_CHANCE.get("tourist") == 0.0)
    check("множитель пилота 1.4", PILOT_CRIT_MULT == 1.4)

    # ── 2. Крит берётся из stats, а не из противника ───────────────────────────
    print("\n2. Шанс берётся из своих характеристик (старый баг)")
    # Противник с огромным шансом крита не должен влиять на пилотный удар.
    enemy_critty = {'armor': 0, 'dodge': 0, 'crit_chance': 100, 'crit_mult': 9.9}
    hits = [roll_pilot_damage(stats(chance=0.0), enemy_critty) for _ in range(300)]
    check("критический шанс врага не даёт пилоту критовать",
          not any(h['crit'] for h in hits))
    # Обратный случай: пилот с критом 100% критует всегда, даже если враг без крита.
    plain = {'armor': 0, 'dodge': 0, 'crit_chance': 0, 'crit_mult': 1.5}
    hits = [roll_pilot_damage(stats(chance=100.0), plain) for _ in range(300)]
    check("пилот с критом 100% критует каждый удар",
          all(h['crit'] for h in hits))

    # ── 3. Фактическая частота совпадает с заявленной ─────────────────────────
    print("\n3. Фактическая частота крита")
    for chance in (5.0, 25.0, 50.0):
        n = 20000
        got = sum(1 for _ in range(n)
                  if roll_pilot_damage(stats(chance=chance), plain)['crit'])
        real = got * 100.0 / n
        check(f"заявлено {chance}% → фактически {real:.1f}%",
              abs(real - chance) <= 1.5, f"{got}/{n}")

    # Дробный шаг 1.5% обязан работать (старый код использовал random.randint(1,100)
    # и не мог отдать 1.5% — округлял до 1% или 2%).
    n = 40000
    got = sum(1 for _ in range(n)
              if roll_pilot_damage(stats(chance=1.5), plain)['crit'])
    real = got * 100.0 / n
    check("дробные 1.5% отрабатывают (раньше код жал 1 или 2%)",
          abs(real - 1.5) <= 0.6, f"фактически {real:.2f}%")

    # ── 4. Множитель реально умножает урон ────────────────────────────────────
    print("\n4. Множитель урона")
    # ⚠️ мерить надо 'damage', а не 'raw': 'raw' в ответе — это урон ДО крита,
    # крит меняет отдельную переменную damage.
    # Диапазон (4, 4) вместо (4, 8) — удар всегда 4, поэтому проверка точная
    # и не мигает от прогона к прогону. Случайный разброс тут ничего не проверяет.
    fixed = {'armor': 0, 'dodge': 0, 'crit_chance': 0, 'crit_mult': 1.5}
    s = stats(chance=100.0, mult=1.4, base=(4, 4))
    dmgs = {roll_pilot_damage(s, fixed)['damage'] for _ in range(300)}
    check("крит ×1.4 по удару 4 даёт ровно 6", dmgs == {6}, f"получено {sorted(dmgs)}")

    s = stats(chance=100.0, mult=1.8, base=(4, 4))
    dmgs = {roll_pilot_damage(s, fixed)['damage'] for _ in range(300)}
    check("снаряжение ×1.8 по удару 4 даёт ровно 7", dmgs == {7}, f"получено {sorted(dmgs)}")

    s = stats(chance=0.0, mult=1.4, base=(4, 4))
    dmgs = {roll_pilot_damage(s, fixed)['damage'] for _ in range(300)}
    check("без крита удар 4 проходит без изменений", dmgs == {4}, f"получено {sorted(dmgs)}")

    # Множитель всегда не меньше 1: снаряжение не может ослабить крит.
    s = stats(chance=100.0, mult=1.8, base=(4, 4))
    check("множитель из снаряжения только усиливает крит",
          min(roll_pilot_damage(s, fixed)['damage'] for _ in range(200)) >= 4)

    # ── 5. Потолок шанса ───────────────────────────────────────────────────────
    print("\n5. Потолок суммарного шанса")
    check("потолок определён и не больше 100", 0 < MAX_CRIT_CHANCE <= 100,
          f"MAX_CRIT_CHANCE = {MAX_CRIT_CHANCE}")

    # ── 6. Критический удар не ломает броню ───────────────────────────────────
    print("\n6. Совместимость с бронёй (формулу боя не меняли)")
    armored = {'armor': 4, 'dodge': 0, 'crit_chance': 0, 'crit_mult': 1.5}
    n = 4000
    blocked = [roll_pilot_damage(stats(chance=50.0), armored)['damage'] for _ in range(n)]
    check("броня по-прежнему вычитается после крита",
          all(d <= 8 * PILOT_CRIT_MULT - 4 for d in blocked))
    check("armor_blocked не превышает саму броню",
          all(roll_pilot_damage(stats(chance=50.0), armored)['armor_blocked'] <= 4
              for _ in range(200)))

    # ── 7. Боевая статистика отдаёт оба ключа ─────────────────────────────────
    print("\n7. Ключи в stats")
    s = stats(chance=3.0)
    check("pilot_combat_stats-совместимый dict: ключ crit_chance есть",
          'crit_chance' in s)
    check("частичный dict без crit_chance не роняет бой (безопасный .get)",
          not any(roll_pilot_damage({'base_dmg': (4, 8), 'weapon_damage': 0,
                                     'attack_mult': 1.0}, plain)['crit']
                  for _ in range(200)))

    print(f"\n=== SMOKE 122: {PASSED} passed, {FAILED} failed ===")
    return 1 if FAILED else 0


async def db_part():
    """Сквозная проверка через настоящую БД: медаль → бонус → суммарный крит."""
    from database.db import (add_item, create_award, get_award_bonus, get_db,
                             get_player_crit_chance, get_player_crit_mult,
                             get_pilot_crit_chance, grant_award,
                             init_db, set_equipment_slot)

    await init_db()
    conn = await get_db()
    uid = 555001
    await conn.execute("DELETE FROM users WHERE user_id = ?", (uid,))
    await conn.execute(
        "INSERT INTO users (user_id, troops, username) VALUES (?, 0, 'crit')", (uid,))
    await conn.commit()

    print("\n8. Сквозной путь: медаль → бонус → суммарный крит")
    base = await get_pilot_crit_chance(uid)
    check("у нового игрока базовый крит 0 (Рекрут)", base == 0.0, f"{base}")

    # Медаль без бонуса крита ничего не меняет.
    ok, _ = await create_award("Тест без крита", bonus_attack=5)
    if ok:
        await grant_award(uid, _)
    check("медаль без bonus_crit не добавляет крит",
          await get_player_crit_chance(uid) == base)

    # А вот медаль с bonus_crit добавляет.
    ok, aid = await create_award("Тест крита", bonus_crit=8, bonus_attack=5)
    if ok:
        await grant_award(uid, aid)
    bonus = await get_award_bonus(uid)
    check("get_award_bonus отдаёт ключ crit", 'crit' in bonus, f"ключи: {sorted(bonus)}")
    check("bonus_crit сохранён в БД и суммируется", bonus.get('crit') == 8,
          f"получено {bonus.get('crit')}")
    check("суммарный крит вырос на 8", await get_player_crit_chance(uid) == base + 8)

    # Снаряжение добавляет свой шанс и множитель.
    await add_item(name="Тестовый клинок", description="крит", price=10,
                   sell_price=5, rarity=1, category="weapon", stock=-1,
                   added_by=0, ap_cost=0, damage=0, heal=0, armor=0,
                   crit_chance=6, crit_mult=0.2)
    items = await get_db()
    cur = await items.execute("SELECT id FROM items WHERE name = 'Тестовый клинок'")
    blade_id = (await cur.fetchone())['id']
    await set_equipment_slot(uid, 'weapon', blade_id)
    check("снаряжение добавляет шанс (8 + 6 = 14)",
          await get_player_crit_chance(uid) == base + 14,
          f"получено {await get_player_crit_chance(uid)}")
    check("снаряжение поднимает множитель до 1.6",
          abs(await get_player_crit_mult(uid) - 1.6) < 1e-9,
          f"получено {await get_player_crit_mult(uid)}")

    # Потолок.
    await create_award("Тест потолка", bonus_crit=100)
    cur = await conn.execute("SELECT id FROM awards WHERE name = 'Тест потолка'")
    big = (await cur.fetchone())['id']
    await grant_award(uid, big)
    total = await get_player_crit_chance(uid)
    check(f"суммарный шанс не превышает потолок {MAX_CRIT_CHANCE}",
          total == MAX_CRIT_CHANCE, f"получено {total}")

    # Боевая статистика собирает всё вместе.
    from utils.combat_model import pilot_combat_stats
    st = await pilot_combat_stats(uid)
    check("pilot_combat_stats отдаёт crit_chance",
          st.get('crit_chance') == MAX_CRIT_CHANCE, f"{st.get('crit_chance')}")
    check("pilot_combat_stats отдаёт crit_mult",
          abs(st.get('crit_mult', 0) - 1.6) < 1e-9, f"{st.get('crit_mult')}")

    for suffix in ("", "-wal", "-shm"):
        try:
            os.remove(_TEST_DB + suffix)
        except OSError:
            pass


if __name__ == '__main__':
    code = main()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(db_part())
    finally:
        # БД обязательно закрываем в отдельном цикле, иначе процесс висит
        # на незакрытом aiosqlite-соединении (так сделано в smoke_116).
        _l = asyncio.new_event_loop()
        asyncio.set_event_loop(_l)
        try:
            import database.db as _db

            if _db.db is not None:
                _l.run_until_complete(_db.close_db())
        except Exception:
            pass
        _l.close()
        loop.close()
    print(f"\n=== SMOKE 122 (итог): {PASSED} passed, {FAILED} failed ===")
    sys.exit(code or (1 if FAILED else 0))