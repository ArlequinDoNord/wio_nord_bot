import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from config import BOT_TOKEN
from database.db import init_db, close_db, daily_ap_recovery, seed_default_items, seed_dungeon, ensure_dungeon_shop_items, ensure_dungeon_enemy_drops
from bot.handlers.start import router as start_router
from bot.handlers.profile import router as profile_router
from bot.handlers.bank import router as bank_router
from bot.handlers.admin import router as admin_router
from bot.handlers.shop import router as shop_router
from bot.handlers.inventory import router as inventory_router
from bot.handlers.reports import router as reports_router
from bot.handlers.dungeon import router as dungeon_router

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("bot.log", encoding="utf-8")
    ]
)
logger = logging.getLogger(__name__)


async def scheduled_jobs(bot: Bot):
    while True:
        try:
            await daily_ap_recovery()
            logger.info("Суточное восстановление AP выполнено")
        except Exception as e:
            logger.error(f"Ошибка восстановления AP: {e}", exc_info=True)
        await asyncio.sleep(24 * 60 * 60)


async def main():
    logger.info("=" * 50)
    logger.info("Запуск бота N.O.R.D. 3.0")
    logger.info("=" * 50)

    await init_db()
    logger.info("База данных инициализирована")

    seeded = await seed_default_items()
    if seeded:
        logger.info("Магазин наполнен базовым набором товаров (тестовые заглушки)")

    dungeon_seeded = await seed_dungeon()
    if dungeon_seeded:
        logger.info("Тестовый данж «Крысиный Подвал» создан")

    await ensure_dungeon_shop_items()
    logger.info("Предметы данжа (зелье, трофеи) проверены")

    await ensure_dungeon_enemy_drops()
    logger.info("Дропы врагов обновлены")

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(start_router)
    dp.include_router(profile_router)
    dp.include_router(bank_router)
    dp.include_router(admin_router)
    dp.include_router(shop_router)
    dp.include_router(inventory_router)
    dp.include_router(reports_router)
    dp.include_router(dungeon_router)

    logger.info("Хендлеры зарегистрированы")

    job_task = asyncio.create_task(scheduled_jobs(bot))

    try:
        await dp.start_polling(bot, skip_updates=True)
    except Exception as e:
        logger.error(f"Ошибка в главном цикле: {e}", exc_info=True)
    finally:
        job_task.cancel()
        await close_db()
        logger.info("Бот остановлен")


if __name__ == "__main__":
    asyncio.run(main())
