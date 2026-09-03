import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from config import BOT_TOKEN
from database.db import init_db, close_db, daily_ap_recovery
from bot.handlers.start import router as start_router
from bot.handlers.profile import router as profile_router
from bot.handlers.bank import router as bank_router

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
    logger.info("Запуск бота Нордмарк")
    logger.info("=" * 50)

    await init_db()
    logger.info("База данных инициализирована")

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(start_router)
    dp.include_router(profile_router)
    dp.include_router(bank_router)

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
