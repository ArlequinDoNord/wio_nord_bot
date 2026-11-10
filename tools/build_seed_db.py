# -*- coding: utf-8 -*-
"""Собирает временную БД из сидов кода — для TEXTS_CATALOG.md до деплоя.

Зачем: каталог генерируется из БД, но новинки (враги, предметы, рецепты,
награды) появляются в коде раньше, чем на проде. Этот скрипт поднимает БД
из `init_db()` + `ensure_*/seed_*` (та же последовательность, что в `main.py`),
чтобы каталог увидел новые сущности ещё на этапе проработки.

Запуск (обычно вызывается из tools/export_texts.py --from-seeds):
    .venv\\Scripts\\python.exe tools/build_seed_db.py ВРЕМЕННАЯ_БД [--base ПРОД_БД]

--base: сначала копируется прод-снимок, затем сверху прогоняются сиды —
получается «прод + новинки кода».

ВНИМАНИЕ: env DATABASE_PATH выставляется до импорта config/database.db.
"""
from __future__ import annotations

import argparse
import asyncio
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


async def _seed_all() -> None:
    from database import db as D

    await D.init_db()
    await D.seed_default_items()
    await D.seed_dungeon()
    await D.ensure_dungeon_shop_items()
    await D.ensure_dungeon_enemy_drops()
    await D.ensure_life_items()
    await D.ensure_dungeon_reservoir_items()
    await D.ensure_recipes()
    await D.ensure_recipe_shop_items()
    await D.ensure_water_fish()
    await D.ensure_forest_items()
    await D.ensure_forest_mushrooms()
    await D.ensure_forest_zones()
    await D.ensure_forest_enemies()
    await D.ensure_mollusk_items()
    await D.ensure_fishing_enemies()
    await D.ensure_mine_items()
    await D.ensure_mine_enemies()
    await D.ensure_logging_items()
    await D.ensure_logging_enemies()
    await D.ensure_firelab_items()
    await D.ensure_firelab_enemies()
    await D.ensure_market_license_item()
    await D.seed_kvp()
    await D.ensure_kvp_items()
    await D.ensure_kvp_award()
    await D.ensure_duel_items()
    await D.ensure_achievements()
    await D.ensure_tourist_booklet()
    await D.repair_mojibake_entities()
    await D.ensure_item_rarity_unified()
    await D.close_db()


def main() -> int:
    parser = argparse.ArgumentParser(description="Сборка временной БД из сидов кода.")
    parser.add_argument("path", help="куда записать временную БД")
    parser.add_argument("--base", help="прод-снимок, поверх которого накатываются сиды")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    path = os.path.abspath(args.path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    for suffix in ("", "-wal", "-shm"):
        if os.path.exists(path + suffix):
            os.remove(path + suffix)
    if args.base:
        base = os.path.abspath(args.base)
        if not os.path.exists(base):
            sys.exit(f"Нет файла БД для --base: {base}")
        shutil.copy2(base, path)
        for suffix in ("-wal", "-shm"):
            if os.path.exists(base + suffix):
                shutil.copy2(base + suffix, path + suffix)

    os.environ["DATABASE_PATH"] = path
    if ROOT not in sys.path:
        sys.path.insert(0, ROOT)

    asyncio.run(_seed_all())
    if not args.quiet:
        print(f"seed db: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
