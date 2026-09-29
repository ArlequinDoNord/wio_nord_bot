"""Smoke v0.16.1: время суточного цикла 10:00 МСК и приветствие (2 деплоя).

Проверяем, что выплаты по отчётам идут в 10:00 МСК (ночной/утренний фарм попадает
в прошлые сутки вместе с игровым сбросом очков),
и что приветствие показывает ровно два блока: текущий деплой и один предыдущий —
никакой простыни из трёх-четырёх сборок.

Запуск: .venv\\Scripts\\python.exe smoke_093.py
"""
import os
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(__file__))

PASSED = 0
FAILED = 0


def check(name, cond):
    global PASSED, FAILED
    if cond:
        PASSED += 1
    else:
        FAILED += 1
        print(f"  FAIL: {name}")


def run():
    import config
    from main import PAYOUT_HOUR_MSK, PAYOUT_MINUTE_MSK, MSK, _seconds_until_payout

    # ── 1. Время цикла: 10:00 МСК ──
    check("цикл назначен на 10:00 МСК",
          (PAYOUT_HOUR_MSK, PAYOUT_MINUTE_MSK) == (10, 0))

    now = datetime.now(MSK)
    target = now.replace(hour=10, minute=0, second=10, microsecond=0)
    if target <= now:
        target += timedelta(days=1)
    check("до 10:00 МСК считается верно",
          abs(_seconds_until_payout() - (target - now).total_seconds()) < 2)
    check("ожидание в пределах суток", 0 < _seconds_until_payout() <= 24 * 3600)
    check("следующий запуск не в прошлом",
          datetime.fromtimestamp(datetime.now().timestamp() + _seconds_until_payout(), MSK).hour == 10)

    # ── 2. Заметки о деплоях: ровно две, короткие ──
    check("VERSION_NOTES заполнены", bool(config.VERSION_NOTES.strip()))
    check("PREV_VERSION_NOTES заполнены", bool(config.PREV_VERSION_NOTES.strip()))
    check("предыдущая версия указана", bool(str(config.PREV_VERSION).strip()))
    v_now = tuple(int(x) for x in str(config.VERSION).split("."))
    v_prev = tuple(int(x) for x in str(config.PREV_VERSION).split("."))
    check("текущая версия не старше предыдущей", v_now >= v_prev, )
    check("заметки не простыня (текущий деплой)", len(config.VERSION_NOTES) <= 400)
    check("заметки не простыня (предыдущий деплой)", len(config.PREV_VERSION_NOTES) <= 400)

    # ── 3. Приветствие: два блока, а не четыре ──
    src = open(os.path.join(os.path.dirname(__file__), "bot", "handlers", "start.py"),
               encoding="utf-8").read()
    check("приветствие печатает «Что нового»", ">> Что нового:" in src)
    check("приветствие печатает предыдущую сборку", "PREV_VERSION_NOTES}" in src)
    check("VERSION_NOTES печатается один раз", src.count("{VERSION_NOTES}") == 1)
    check("PREV_VERSION_NOTES печатается один раз", src.count("{PREV_VERSION_NOTES}") == 1)
    # В приветствии нет места под третью-четвёртую сборку.
    check("нет третьего блока деплоя",
          "PREV2_" not in src and "PREV_PREV" not in src)

    print(f"\nSmoke 093: {PASSED} passed, {FAILED} failed")
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(run())
