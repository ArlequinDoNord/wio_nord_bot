"""Smoke v0.23.0: Дом Дуэлей (PvP).

Проверяет:
1. Товары арены: «Дуэльные перчатки» (duel_gear, слот duel, урон 7,
   статус pilot1) и «Клубная карта» (duel_card); идемпотентность сидинга.
2. item_fits_slot: перчатки — только слот «duel», обычное оружие туда не встаёт.
3. get_player_duel_gear_damage: 0 без снаряжения, 7 с перчатками в слоте duel.
4. has_duel_club_card: False → True после покупки карты в инвентарь.
5. Жизненный цикл дуэли: вызов → занятость (второй вызов None) → принятие →
   выбор зон → резолв раунда → завершение → рейтинг/счётчики → дуэль неактивна.
6. Доступ по статусу: pilot1 открывает арену, без статуса — нет.
7. Локация «duel_house» создана; чистая функция _hp_bar.

Запуск: .venv\\Scripts\\python.exe smoke_137.py
"""
import asyncio
import os
import sys

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke137.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB
sys.path.insert(0, os.path.dirname(__file__))

PASS = 0
FAIL = 0


def check(name, cond):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  [OK] {name}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name}")


async def run():
    from database.db import (
        init_db, close_db, add_user, get_user,
        get_item_by_name, add_inventory_item, set_equipment_slot, get_equipment,
        item_fits_slot, get_player_duel_gear_damage, has_duel_club_card,
        get_user_duel_stats, get_active_duel, get_duel, create_duel_challenge,
        accept_duel, set_duel_zone, duel_round_ready, apply_duel_round,
        finish_duel, apply_duel_result, get_duel_opponents, get_duel_rating_top,
        get_status_by_tag, grant_status, user_has_status_tag, get_location_by_key,
    )
    from config import (
        DUEL_GLOVES_NAME, DUEL_CLUB_CARD_NAME, DUEL_ZONES, DUEL_ACCESS_TAG,
    )

    await init_db()

    print("\n1. Товары арены")
    from database.db import ensure_duel_items
    await ensure_duel_items()
    gloves = await get_item_by_name(DUEL_GLOVES_NAME)
    card = await get_item_by_name(DUEL_CLUB_CARD_NAME)
    check("перчатки созданы", gloves is not None)
    check("перчатки: категория duel_gear", gloves and gloves['category'] == 'duel_gear')
    check("перчатки: слот duel", gloves and gloves['equip_slot'] == 'duel')
    check("перчатки: урон 7", gloves and gloves['damage'] == 7)
    check("перчатки: статус pilot1", gloves and gloves['required_status'] == 'pilot1')
    check("карта создана (duel_card)", card is not None and card['category'] == 'duel_card')
    await ensure_duel_items()
    g2 = await get_item_by_name(DUEL_GLOVES_NAME)
    check("сидинг идемпотентен (перчатки)", g2['id'] == gloves['id'])

    print("\n2. item_fits_slot")
    check("перчатки встают в слот duel", item_fits_slot(gloves, 'duel'))
    check("перчатки НЕ встают в weapon", not item_fits_slot(gloves, 'weapon'))
    check("оружие НЕ встаёт в duel",
          not item_fits_slot({'category': 'weapon'}, 'duel'))

    print("\n3. Дуэльное снаряжение")
    await add_user(101, "alpha", "Альфа", "")
    await add_user(102, "beta", "Бета", "")
    check("без снаряжения урон 0", await get_player_duel_gear_damage(101) == 0)
    await add_inventory_item(101, gloves['id'], 1)
    await set_equipment_slot(101, 'duel', gloves['id'])
    check("с перчатками урон 7", await get_player_duel_gear_damage(101) == 7)

    print("\n4. Клубная карта")
    check("карты нет", not await has_duel_club_card(101))
    await add_inventory_item(101, card['id'], 1)
    check("карта есть", await has_duel_club_card(101))
    check("у второго карты нет", not await has_duel_club_card(102))

    print("\n5. Жизненный цикл дуэли")
    duel_id = await create_duel_challenge(101, 102)
    check("вызов создан", duel_id is not None)
    cur = await get_active_duel(101)
    check("активная дуэль видна", cur is not None and cur['status'] == 'invited')
    check("повторный вызов отклонён", await create_duel_challenge(101, 102) is None)
    check("сам с собой нельзя", await create_duel_challenge(101, 101) is None)

    check("принятие вызова", await accept_duel(duel_id, 102, 100, 100, 100, 100))
    row = await get_duel(duel_id)
    check("статус active", row['status'] == 'active')
    check("HP выставлены", row['challenger_hp'] == 100 and row['opponent_hp'] == 100)

    check("зона записана", await set_duel_zone(duel_id, 101, 'head', 'body'))
    check("раунд не готов после одного", not duel_round_ready(await get_duel(duel_id)))
    await set_duel_zone(duel_id, 102, 'legs', 'head')
    check("раунд готов после двух", duel_round_ready(await get_duel(duel_id)))

    await apply_duel_round(duel_id, 80, 70, 2)
    row = await get_duel(duel_id)
    check("HP обновлены", row['challenger_hp'] == 80 and row['opponent_hp'] == 70)
    check("зоны очищены", not row['challenger_atk'] and not row['opponent_def'])
    check("ход 2", row['turn'] == 2)

    await finish_duel(duel_id, 101, 2)
    await apply_duel_result(101, 2, 'win')
    await apply_duel_result(102, -3, 'loss')
    s1 = await get_user_duel_stats(101)
    s2 = await get_user_duel_stats(102)
    check("победитель: рейтинг +2, win", s1['rating'] == 2 and s1['wins'] == 1)
    check("проигравший: рейтинг -3, loss", s2['rating'] == -3 and s2['losses'] == 1)
    check("дуэль завершена", await get_active_duel(101) is None)

    print("\n4b. Рейтинг/пилоты")
    top = await get_duel_rating_top(10)
    check("в рейтинге есть победитель", any(r['user_id'] == 101 for r in top))

    print("\n6. Доступ по статусу")
    check("без статуса арена закрыта", not await user_has_status_tag(102, DUEL_ACCESS_TAG))
    st = await get_status_by_tag(DUEL_ACCESS_TAG)
    await grant_status(101, st['id'])
    check("с pilot1 арена открыта", await user_has_status_tag(101, DUEL_ACCESS_TAG))
    opponents = await get_duel_opponents(999)
    check("пилот со статусом в списке соперников",
          any(o['user_id'] == 101 for o in opponents))

    print("\n7. Локация и чистые функции")
    loc = await get_location_by_key('duel_house')
    check("локация duel_house создана", loc is not None)
    check("локация: доступ с pilot1",
          loc and loc['access_mode'] == 'min' and loc['required_status'] == 'pilot1')
    from bot.handlers.duel import _hp_bar
    check("4 зоны", len(DUEL_ZONES) == 4)
    check("_hp_bar полный", _hp_bar(100, 100).count('█') == 12)
    check("_hp_bar пустой", _hp_bar(0, 100).count('░') == 12)

    await close_db()


if __name__ == "__main__":
    asyncio.run(run())
    print(f"\nИТОГ: {PASS} ok / {FAIL} fail")
    sys.exit(1 if FAIL else 0)
