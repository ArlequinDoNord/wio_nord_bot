"""Общий счётчик руды первого уровня шахт и открытие второго уровня.

Считается руда, добытая киркой (железная и пламенная), у всех пилотов вместе.
Стартовое значение берётся из журнала действий (уже добытое до введения счётчика),
дальше растёт при каждой находке. Когда счётчик достигает MINE_LEVEL2_ORE_TARGET,
второй уровень открывается один раз: в общий чат и личным сообщением каждому пилоту.
"""

import asyncio

from config import FIRE_ORE_NAME, MINE_LEVEL2_ORE_TARGET
from database.db import citizen_user_ids, get_db, get_setting, log_activity, set_setting
from utils.localization import t
from utils.notify import notify, notify_user_t

TOTAL_KEY = "mine_ore_total"
OPENED_KEY = "mine_level2_opened_at"


async def _count_from_log() -> int:
    """Вся руда, добытая киркой, кроме праздничной (пламенной и будущей новогодней)."""
    conn = await get_db()
    cur = await conn.execute(
        "SELECT COUNT(*) AS n FROM activity_log WHERE action = 'mine' AND details LIKE ? AND details <> ?",
        ("Добыл «%»", f"Добыл «{FIRE_ORE_NAME}»"),
    )
    row = await cur.fetchone()
    return int(row["n"] or 0)


async def get_ore_total() -> int:
    stored = await get_setting(TOTAL_KEY)
    if stored is None:
        total = await _count_from_log()
        await set_setting(TOTAL_KEY, str(total))
        return total
    return int(stored)


async def is_level2_open() -> bool:
    return bool(await get_setting(OPENED_KEY))


async def add_ore(count: int = 1) -> bool:
    """Засчитать руду. True — именно этим вызовом второй уровень открылся."""
    total = await get_ore_total() + count
    await set_setting(TOTAL_KEY, str(total))
    if total < MINE_LEVEL2_ORE_TARGET or await is_level2_open():
        return False
    await set_setting(OPENED_KEY, str(total))
    return True


async def announce_level2(bot) -> None:
    """Оповещение об открытии: общий чат и личка каждому пилоту (на его языке)."""
    await notify(bot, t("mine.l2.chat", target=MINE_LEVEL2_ORE_TARGET))
    for uid in await citizen_user_ids():
        try:
            await notify_user_t(bot, uid, "mine.l2.broadcast", target=MINE_LEVEL2_ORE_TARGET)
        except Exception as e:
            await log_activity(None, "mine_l2_notify_failed", f"uid={uid}: {e}")


def start_announce(bot) -> None:
    """Запуск рассылки в фоне, чтобы хендлер шахты не ждал сотни отправок."""
    asyncio.create_task(announce_level2(bot))
