# SMOKE 123: легионер — флаг users.legioner, кеп доступа «не выше Ветерана»
# и запрет голосования (решение владельца 2026-10-03, вариант А выдачи).
#
# Ключевая идея, которую тут и проверяем: кеп держится НЕ на sort_order статуса,
# а на отдельном флаге. Иначе он ломался бы сам собой по мере роста звания
# (MAX(sort_order) у легионера-Аса дал бы 9 и все доступы раскрылись бы).
#
# ⚠️ DATABASE_PATH выставляется ДО импорта config/database — config.py читает
# путь к базе в момент импорта. Иначе тест пишет в настоящую локальную базу
# (так случилось с первой версией smoke_122).
import asyncio
import os
import sys
import tempfile

WORK = tempfile.mkdtemp(prefix="sm123_")
DB = os.path.join(WORK, "t.db")
os.environ["DATABASE_PATH"] = DB
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

PASSED = 0
FAILED = []


def check(name, cond, extra=""):
    global PASSED
    if cond:
        PASSED += 1
        print(f"  ok   {name}")
    else:
        FAILED.append(name)
        print(f"  FAIL {name} {extra}")


async def main():
    import database.db as D
    from config import LEGIONER_ACCESS_CAP_ORDER

    await D.init_db()

    print("1. Схема и статус")
    cur = await (await D.get_db()).execute("PRAGMA table_info(users)")
    cols = {r['name'] for r in await cur.fetchall()}
    check("users.legioner есть", 'legioner' in cols)
    check("значение по умолчанию 0 (не легионер)", not await D.is_legioner(777001))
    st = await D.get_status_by_tag("legioner")
    check("статус «Легионер» создан", st is not None)
    check("в названии есть эмодзи", st and "Легионер" in st['name'],
          st['name'] if st else "")
    check("sort_order = как у Ветерана (5)", st and st['sort_order'] == 5,
          st['sort_order'] if st else "")
    check("кеп в конфиге совпадает с иерархией (5)",
          LEGIONER_ACCESS_CAP_ORDER == 5)

    # Пилот: Ас (9) — самый высокий обычный статус. Именно он проверяет кеп:
    # без флага у него открыто всё, с флагом — не выше Ветерана.
    ace = await D.get_status_by_tag("ace")
    vet = await D.get_status_by_tag("veteran")
    recruit = await D.get_status_by_tag("recruit")
    conn = await D.get_db()
    # Настоящий Ас. Два момента, из-за которых это не «просто много войск»:
    #  * get_effective_rank() намеренно ограничивает АВТО-ранг Veteran'ом
    #    (AUTO_RANK_NAMES), выше — только назначение админом;
    #  * порог Аса — 15000 войск (8500 это лишь Мастер-пилот).
    # Иначе «легионер-Ас» был бы на деле Ветераном и проверка «кеп не режет
    # бой» сравнивала бы пилота с самим собой.
    from config import RANK_STATUS_TAGS
    ace_rank = next(n for n, t in RANK_STATUS_TAGS.items() if t == "ace")
    for uid in (777001, 777002):
        await conn.execute(
            "INSERT OR IGNORE INTO users (user_id, troops, username) VALUES (?, 20000, ?)",
            (uid, f"leg{uid}"))
        await conn.execute(
            "UPDATE users SET troops = 20000, promoted_rank = ? WHERE user_id = ?",
            (ace_rank, uid))
    await conn.commit()
    for s in (recruit, vet, ace, st):
        await D.grant_status(777001, s['id'])   # Ас + легионер
        await D.grant_status(777002, s['id'])   # Ас без флага
    await conn.commit()
    check("ставлю флаг легионера", await D.set_legioner(777001, True))

    print("\n2. Кеп: флаг решает, а не sort_order")
    check("без флага Ас открывает свой статус", await D.user_has_status_tag(777002, "ace"))
    check("без флага Ас не хватает до keeper (100)",
          not await D.user_has_status_tag(777002, "keeper"))
    check("флажок стоит только у 777001", await D.is_legioner(777001))
    check("второй пилот — не легионер", not await D.is_legioner(777002))
    check("легионер-Ас НЕ получает ace-доступы",
          not await D.user_has_status_tag(777001, "ace"))
    check("легионер-Ас сохраняет veteran-доступы",
          await D.user_has_status_tag(777001, "veteran"))
    check("легионер-Ас сохраняет recruit-доступы",
          await D.user_has_status_tag(777001, "recruit"))
    check("легионер-Ас не получает keeper (100)",
          not await D.user_has_status_tag(777001, "keeper"))
    check("без флага Ас по-прежнему не keeper",
          not await D.user_has_status_tag(777002, "keeper"))
    check("effective_access_top легионера = 5",
          await D.effective_access_top(777001) == 5)
    check("effective_access_top обычного Аса = 9",
          await D.effective_access_top(777002) == 9)

    print("\n3. Витрина магазина — кеп до расчёта «+1 ступень»")
    # Кеп обязан ставиться ДО шага «видно свой статус и одну ступень выше».
    # Если бы кепили после, легионер увидел бы вещи уровня Мастер-пилота.
    top_leg = await D.user_status_visibility_top(777001)
    top_ace = await D.user_status_visibility_top(777002)
    # Ас (9) — высшая ступень карьеры, поэтому «одна ступень выше» для него —
    # это Хранитель (100), и обычный Ас видит всю витрину целиком. Это поведение
    # существовало до легионера и тут только фиксируется как контрольная точка.
    check("витрина обычного Аса = 100 (следующая ступень — Хранитель)",
          top_ace == 100, f"получено {top_ace}")
    check("витрина легионера как у Ветерана (6 = master_pilot)",
          top_leg == 6, f"получено {top_leg}")
    check("кеп сузил витрину", top_leg < top_ace)

    # Реальный фильтр витрины, а не только хелпер.
    from bot.handlers.shop import visible_items
    items = [
        {"name": "штука для рекрута", "category": "gear", "required_status": "recruit"},
        {"name": "штука для ветерана", "category": "gear", "required_status": "veteran"},
        {"name": "штука для мастера", "category": "gear", "required_status": "master_pilot"},
        {"name": "штука для аса", "category": "gear", "required_status": "ace"},
        {"name": "сувенир", "category": "souvenirs", "required_status": None},
    ]
    leg_names = [i['name'] for i in await visible_items(777001, items)]
    ace_names = [i['name'] for i in await visible_items(777002, items)]
    check("легионер НЕ видит вещи для Аса", "штука для аса" not in leg_names, leg_names)
    check("легионер видит вещи до Мастера включительно",
          "штука для мастера" in leg_names, leg_names)
    check("легионер видит сувениры", "сувенир" in leg_names, leg_names)
    check("обычный Ас видит и вещи для аса",
          "штука для аса" in ace_names, ace_names)

    print("\n4. Гейт покупки (отдельный от витрины!)")
    # Покупка идёт мимо витрины, через user_has_status_tag напрямую.
    check("легионер не купит вещь для Аса (гейт покупки)",
          not await D.user_has_status_tag(777001, "ace"))
    check("легионер купит вещь для Ветерана",
          await D.user_has_status_tag(777001, "veteran"))

    print("\n5. Кеп НЕ трогает карьеру, бой и крит")
    # «Не выше Ветерана» — про вещи и доступы, а не про звание и урон.
    from database.db import get_pilot_base_damage, get_pilot_crit_chance
    dmg_leg = await get_pilot_base_damage(777001)
    dmg_ace = await get_pilot_base_damage(777002)
    check("урон у легионера-Аса не срезан кепом", dmg_leg == dmg_ace,
          f"{dmg_leg} vs {dmg_ace}")
    check("это действительно урон Аса (4, 8)", tuple(dmg_leg) == (4, 8), dmg_leg)
    check("крит у легионера-Аса не срезан",
          await get_pilot_crit_chance(777001) == await get_pilot_crit_chance(777002))
    check("крит = 7.5 (шкала Аса)", await get_pilot_crit_chance(777001) == 7.5,
          await get_pilot_crit_chance(777001))
    check("легионер — не турист", not await D.user_is_tourist(777001))

    print("\n6. Голосование")
    from bot.handlers.polls import _require_pilot

    class FakeAnswer:
        def __init__(self):
            self.texts = []

        async def answer(self, text, show_alert=False):
            self.texts.append(text)

    class FakeMsg:
        async def answer(self, *a, **k):
            pass

    class FakeCB:
        def __init__(self, uid):
            self.from_user = type("U", (), {"id": uid})()
            self.message = FakeMsg()
            self._ans = FakeAnswer()

        async def answer(self, text, show_alert=False):
            self._ans.texts.append(text)

    cb_leg = FakeCB(777001)
    check("легионер НЕ проходит гейт голосования",
          not await _require_pilot(cb_leg))
    check("и получает внятный отказ",
          any("Легионер" in t for t in cb_leg._ans.texts), cb_leg._ans.texts)
    cb_ace = FakeCB(777002)
    check("обычный Ас голосует как раньше", await _require_pilot(cb_ace))

    print("\n7. Строка статуса доступна для выбора в профиле")
    have = await D.get_user_statuses(777001)
    check("«🦅 Легионер» есть в списке статусов игрока",
          any(s['access_tag'] == 'legioner' for s in have),
          [s['name'] for s in have])
    check("его можно выбрать отображаемым (is_selected)",
          await D.set_selected_status(
              777001, next(s['id'] for s in have if s['access_tag'] == 'legioner')))
    sel = await D.get_selected_status(777001)
    check("выбран именно Легионер", sel and sel['access_tag'] == 'legioner',
          sel['name'] if sel else None)

    print("\n8. Снятие флага (вариант А: кнопка ставит и снимает разом)")
    check("снятие флага работает", await D.set_legioner(777001, False))
    check("флаг снят", not await D.is_legioner(777001))
    check("после снятия кеп пропал — Ас снова открывает ace-доступы",
          await D.user_has_status_tag(777001, "ace"))
    _vt = await D.user_status_visibility_top(777001)
    check("витрина расширилась обратно (100)", _vt == 100, _vt)

    print("\n9. Смена звания не ломает кеп")
    # Ключевая причина, почему кеп на флаге, а не на sort_order: если бы он был
    # на статусе, рост звания до Ветерана поднимал бы доступы сам собой.
    await D.set_legioner(777001, True)
    await conn.execute(
        "UPDATE user_statuses SET is_selected = 0 WHERE user_id = 777001")
    await conn.commit()
    check("после смены выбора кеп держится",
          not await D.user_has_status_tag(777001, "ace"))
    check("и веща для Ветерана по-прежнему доступна",
          await D.user_has_status_tag(777001, "veteran"))

    print("\n10. Пилот без флага не затронут")
    check("777002 по-прежнему Ас со всеми доступами",
          await D.user_has_status_tag(777002, "ace"))
    check("и кеп не применяется к туристу",
          not await D.user_has_status_tag(999999, "recruit"))

    print("\n11. Легионер НЕ выдаётся общим списком (иначе строка без флага)")
    # Кнопка «➕ 🦅 Легионер» в общем списке выдала бы только строку статуса,
    # без users.legioner — получился бы легионер без кепа и без запрета голосовать.
    from bot.handlers.admin import _status_grant_markup
    from database.db import get_all_statuses
    _lg = next((s for s in await get_all_statuses()
                if s['access_tag'] == 'legioner'), None)
    check("статус Легионер существует", _lg is not None)
    if _lg:
        _rows = _status_grant_markup([_lg], [], legioner=True)
        _cbs = [b.callback_data for row in _rows.inline_keyboard for b in row]
        check(f"в общем списке нет кнопки выдачи Легионера (кнопки: {_cbs})",
              f"st_pick:{_lg['id']}" not in _cbs)
        check("зато есть отдельная кнопка st:legioner", "st:legioner" in _cbs)
        _rows2 = _status_grant_markup([_lg], [], legioner=False)
        _cbs2 = [b.callback_data for row in _rows2.inline_keyboard for b in row]
        check("кнопка снятия — тоже st:legioner", _cbs2.count("st:legioner") == 1)

    await D.close_db()


asyncio.run(main())
total = len(FAILED)
print(f"\n=== SMOKE 123: {PASSED} passed, {total} failed ===")
for f in FAILED:
    print(f"  FAILED: {f}")
sys.exit(1 if FAILED else 0)