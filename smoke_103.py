"""Smoke v0.18.11: создание рыбы прямо в водоёме (админ-редактор рыбалки).

Новая функция database/db.create_water_fish заводит предмет (категория fishing)
и запись пула water_fish одним махом — как «Создать рыбу» в админке. Проверяем:
  • предмет создан: категория fishing, продажа = заданная, вне магазина, рынок вкл;
  • запись водоёма создана с весами дня/ночи и фото;
  • рыба видна в списке и в пулах (веса > 0);
  • ensure_water_fish не перезаписывает созданное (admin_tuned);
  • предмет доступен как кандидат для ДРУГОГО водоёма (is_available=0);
  • нулевой вес дня — рыба не ловится днём (только ночь).

Запуск: .venv\\Scripts\\python.exe smoke_103.py
"""
import asyncio
import os
import shutil
import sys
import tempfile

WORK = tempfile.mkdtemp(prefix="sm103_")
os.environ["DATABASE_PATH"] = os.path.join(WORK, "t.db")
sys.path.insert(0, os.path.dirname(__file__))

from database import db as D


def check(name, cond):
    print(("  ok   " if cond else "  FAIL ") + name)
    if not cond:
        FAILED.append(name)


FAILED = []


async def main():
    await D.init_db()
    await D.ensure_water_fish()

    ok, res = await D.create_water_fish(
        water="lake", name="Карась", sell_price=6,
        day_weight=50, night_weight=30,
        description="Мелкая и частная.", photo_file_id="photo_mock_1",
        added_by=777,
    )
    check("рыба создана", ok is True)
    if not ok:
        await D.close_db()
        print("\nSmoke 103: FAILED")
        sys.exit(1)
    item_id, wf_id = res['item_id'], res['wf_id']

    item = await D.get_item(item_id)
    check("предмет существует", item is not None)
    if item:
        check("категория fishing", item['category'] == 'fishing')
        check("цена продажи 6 НМ", item['sell_price'] == 6)
        check("не в магазине (is_available=0)", item['is_available'] == 0)
        check("на рынок можно (market_ok=1)", item['market_ok'] == 1)

    rows = await D.get_water_fish_rows("lake")
    k = [r for r in rows if r['name'] == "Карась"]
    check("рыба видна в списке водоёма", len(k) == 1)
    if k:
        check("вес дня 50 / ночи 30", k[0]['day_weight'] == 50 and k[0]['night_weight'] == 30)
        check("фото в водоёме", k[0]['photo_file_id'] == "photo_mock_1")

    pool = await D.get_water_fish_pool("lake")
    check("в дневном/ночном пуле есть карась",
          any(r['name'] == "Карась" for r in pool))

    # Повторный ensure_water_fish не должен ничего перезаписать.
    await D.ensure_water_fish()
    row = await D.get_water_fish_row(wf_id)
    check("ensure_water_fish не трогает созданное",
          row and row['day_weight'] == 50 and row['night_weight'] == 30)

    # Ночью только (вес дня 0) — рыба не в дневном пуле, но в ночном.
    ok2, res2 = await D.create_water_fish(
        water="lake", name="Ночник", sell_price=3, day_weight=0, night_weight=10)
    check("вторая рыба создана", ok2 is True)
    if ok2:
        pool2 = await D.get_water_fish_pool("lake")
        check("вес дня 0 → в пуле НЕ ловится днём",
              not any(r['name'] == "Ночник" and r['day_weight'] > 0 for r in pool2))

    # Карась — кандидат для другого водоёма (но не для озера).
    cand_reservoir = await D.get_water_fish_candidates("reservoir")
    cand_lake = await D.get_water_fish_candidates("lake")
    check("карась доступен как кандидат в водохранилище",
          any(c['name'] == "Карась" for c in cand_reservoir))
    check("карась не предлагается дважды в озеро",
          not any(c['name'] == "Карась" for c in cand_lake))

    await D.close_db()
    shutil.rmtree(WORK, ignore_errors=True)
    total = len(FAILED)
    print("\nSmoke 103: " + ("all passed" if not total else f"{total} failed"))
    sys.exit(1 if FAILED else 0)


asyncio.run(main())