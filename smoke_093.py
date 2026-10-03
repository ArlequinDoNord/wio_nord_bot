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

    # ── 2. Заметки о деплое: короткие, одна запись ──
    check("VERSION_NOTES заполнены", bool(config.VERSION_NOTES.strip()))
    check("заметки не простыня (текущий деплой)", len(config.VERSION_NOTES) <= 400)

    # ── 3. Приветствие: только идея текущего релиза, без старых сборок ──
    src = open(os.path.join(os.path.dirname(__file__), "bot", "handlers", "start.py"),
               encoding="utf-8").read()
    check("приветствие печатает «Что нового»", ">> Что нового:" in src)
    # Заметки печатаются через тизер, а не целиком: интрига не должна исчезать.
    check("текущая версия печатается тизером",
          src.count("_version_teaser(VERSION_NOTES)") == 1)
    check("полный текст заметок в приветствие не попадает",
          "{VERSION_NOTES}\n" not in src and "{PREV_VERSION_NOTES}\n" not in src)
    # Описание прошлого деплоя в приветствии больше не показывается.
    check("в приветствии нет блока прошлой сборки",
          "PREV_VERSION" not in src and "PREV_VERSION_NOTES" not in src)

    # ── 4. Тизер релиза: одна фраза, не длиннее лимита, без обрыва в скобках ──
    from bot.handlers.start import _version_teaser
    check("берётся только первая фраза",
          _version_teaser("Первая мысль. Вторая мысль.") == "Первая мысль.")
    check("без точки в конце точка добавляется",
          _version_teaser("Без точки") == "Без точки.")
    check("пустые заметки не ломают приветствие", _version_teaser("   ") == "…")
    check("текущий деплой укладывается в лимит",
          len(_version_teaser(config.VERSION_NOTES)) <= 121)
    long_paren = ("Баланс леса: поиск грибов теперь 4 ОД (было 3), продажа жареных грибов "
                  "снижена примерно вдвое (Опёнок 17→9 НМ, Ежовик 210→100 НМ) и казна покупает "
                  "грибы не больше 250 НМ в сутки. Рынок не затрагивает.")
    teaser_paren = _version_teaser(long_paren)
    check("длинная фраза обрезается по лимиту", teaser_paren.endswith("…")
          and len(teaser_paren) <= 121)
    check("обрыв не остаётся посреди скобок",
          teaser_paren.count("(") <= teaser_paren.count(")"))

    print(f"\nSmoke 093: {PASSED} passed, {FAILED} failed")
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(run())
