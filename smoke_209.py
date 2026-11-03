# -*- coding: utf-8 -*-
"""Smoke 209 — тыква в кадке: свой интервал плодов и свои картинки стадий.

1. Яблоня даёт плод каждые 2 суток, тыква — каждые 3 (по семечку).
2. Созревание тыквы по времени прежнее: 30 суток до стадии «Плодоносящее».
3. На стадиях 1–4 у тыквы есть файлы картинок, они лежат на диске.
4. Описание семечка тыквы не обещает 2 суток до первого плода.
"""
import os
import sys
import time

from tests_support import Checker

import config


def main():
    check = Checker()
    import database.db as db
    from bot.handlers import housing as hh

    print("\n1. Интервал плодов по семечку")
    check("яблоня: раз в 2 суток", db.fruit_every_days(db.APPLE_SEED_NAME) == 2)
    check("тыква: раз в 3 суток", db.fruit_every_days(config.FIRE_PUMPKIN_SEED_NAME) == 3)

    print("\n2. Созревание тыквы по времени прежнее")
    now = time.time()
    t4 = now - 2.5 * 86400
    started = t4 - 30 * 86400
    base = {"seed": config.FIRE_PUMPKIN_SEED_NAME, "stage_started_at": started, "last_harvest_at": None}
    info = db.plant_stage_info(base, now)
    check("через 30 суток и 2.5 суток — стадия 4", info["stage"] == 4)
    check("тыква: через 2.5 суток после созревания плодов ещё нет", info["fruits"] == 0)
    apple = dict(base, seed=db.APPLE_SEED_NAME)
    check("яблоня за те же 2.5 суток уже дала плод", db.plant_stage_info(apple, now)["fruits"] == 1)
    later = dict(base, stage_started_at=now - 30 * 86400 - 3.5 * 86400)
    check("тыква через 3.5 суток после созревания даёт 1 плод",
          db.plant_stage_info(later, now)["fruits"] == 1)

    print("\n3. Картинки стадий тыквы")
    photos = hh.PLANT_PHOTOS.get(config.FIRE_PUMPKIN_SEED_NAME, {})
    check("все четыре стадии прописаны", sorted(photos) == [1, 2, 3, 4])
    check("файлы картинок на диске", all(os.path.isfile(p) for p in photos.values()))

    print("\n4. Описание семечка")
    src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "database", "db.py"),
               encoding="utf-8").read()
    check("в описании нет «2 суток до первого плода»", "2 суток до первого плода" not in src)
    check("в описании есть «плоды раз в 3 дня»", "плоды раз в 3 дня" in src)

    failed = check.summary()
    return failed


if __name__ == "__main__":
    sys.exit(main())
