import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import BotCommand, Message, CallbackQuery
from dotenv import load_dotenv

from config import BOT_TOKEN
from database.db import (
    init_db, close_db, daily_ap_recovery, seed_default_items, seed_dungeon,
    ensure_dungeon_shop_items, ensure_dungeon_enemy_drops, ensure_life_items, ensure_recipes,
    ensure_dungeon_reservoir_items, ensure_market_license_item, pay_salaries, payout_reports,
    run_housing_tax, seed_kvp, ensure_kvp_items, ensure_kvp_award,
    ensure_water_fish, migrate_legacy_junk,
    ensure_recipe_shop_items, ensure_user_recipes_backfill,
    log_activity, prune_activity_log,
)
from utils.notify import notify_treasury_shortage
from utils.helpers import is_main_menu_text
from bot.handlers.start import router as start_router
from bot.handlers.profile import router as profile_router
from bot.handlers.bank import router as bank_router
from bot.handlers.admin import router as admin_router
from bot.handlers.shop import router as shop_router
from bot.handlers.inventory import router as inventory_router
from bot.handlers.reports import router as reports_router
from bot.handlers.dungeon import router as dungeon_router
from bot.handlers.pilots import router as pilots_router
from bot.handlers.polls import router as polls_router
from bot.handlers.library import router as library_router
from bot.handlers.locations import router as locations_router
from bot.handlers.park import router as park_router
from bot.handlers.fishing import router as fishing_router
from bot.handlers.housing import router as housing_router
from bot.handlers.news import router as news_router
from bot.handlers.kvp import router as kvp_router
from bot.handlers.wall import router as wall_router
from bot.handlers.hq import router as hq_router
from bot.handlers.clans import router as clans_router
from bot.handlers.nii import router as nii_router

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


class MainMenuFSMReset(BaseMiddleware):
    """Если приходит нажатие reply-кнопки главного меню, сбрасывает активное
    FSM-состояние. Иначе FSM-хендлеры (админ-панель, передача и т.д.) перехватывают
    «Магазин»/«Инвентарь»/«Сдать отчёт» как ввод числа и отвечают мусором.

    Исключение — активный забег в подземелье: там состояние хранит бой
    (шаг кнопок, HP врага, яд). Его сбрасывать нельзя, иначе игрок, открывший
    «Инвентарь»/«Магазин» посреди забега, не сможет продолжить бой старыми
    кнопками и «застрянет» (жетон сгорел, кнопки мертвы).
    """

    DUNGEON_STATE_KEYS = ('dungeon_step', 'current_enemy_id', 'current_enemy_hp', 'dungeon_id')

    async def __call__(self, handler, event, data):
        if isinstance(event, Message) and event.text:
            from bot.handlers.fishing import deactivate_fishing
            if is_main_menu_text(event.text) or event.text.startswith("/"):
                try:
                    await deactivate_fishing(event.from_user.id)
                except Exception:
                    pass
            if is_main_menu_text(event.text):
                state: FSMContext | None = data.get('state')
                if state is not None:
                    try:
                        active = await state.get_data()
                        if not any(k in active for k in self.DUNGEON_STATE_KEYS):
                            await state.clear()
                    except Exception:
                        pass
        return await handler(event, data)


class FishingActiveLock(BaseMiddleware):
    """Пока идёт активная фаза рыбалки (заброс → результат), игрок не может
    уходить в другие меню: callback-кнопки других разделов и reply-клавиатура
    отсекаются с подсказкой.

    Иначе уход в другое меню приводит к инвалидации окна рыбалки (токен
    сгорает), и кнопка «Ещё раз» после результата перестаёт работать.
    """

    async def __call__(self, handler, event, data):
        from bot.handlers.fishing import FISHING_CASTING

        uid = getattr(event, "from_user", None)
        uid = uid.id if uid else None
        if uid and uid in FISHING_CASTING:
            # Свои рыболовные кнопки пропускаем, остальное — блокируем.
            if isinstance(event, CallbackQuery):
                cb_data = event.data or ""
                if cb_data.startswith("fish:"):
                    return await handler(event, data)
                await event.answer(
                    "🎣 Ты ещё ждёшь улов — дождись результата, а потом продолжим!",
                    show_alert=True,
                )
                return
            if isinstance(event, Message):
                if (event.text and (is_main_menu_text(event.text) or event.text.startswith("/"))) \
                        or not event.text:
                    try:
                        await event.answer("🎣 Ты ещё ждёшь улов — дождись результата!")
                    except Exception:
                        pass
                    return
        return await handler(event, data)


async def scheduled_jobs(bot: Bot):
    while True:
        try:
            await daily_ap_recovery()
            logger.info("Суточное восстановление AP выполнено")
        except Exception as e:
            logger.error(f"Ошибка восстановления AP: {e}", exc_info=True)
        try:
            forfeited = await run_housing_tax()
            if forfeited:
                for uid in forfeited:
                    try:
                        await bot.send_message(
                            uid,
                            "🏠 ВНИМАНИЕ! Жильё изъято!\n\n"
                            "Твоё жильё было изъято за неуплату налогов (3 месяца просрочки).\n"
                            "Ты возвращаешься в муниципальный кубрик.\n"
                            "Вся установленная мебель вернулась в инвентарь."
                        )
                    except Exception:
                        pass
                logger.info(f"Изъято жильё у {len(forfeited)} игроков за неуплату налога")
        except Exception as e:
            logger.error(f"Ошибка начисления налога на жильё: {e}", exc_info=True)
        try:
            res = await pay_salaries()
            if res['paid'] or res['debt']:
                logger.info(
                    f"Зарплаты: выплачено {len(res['paid'])}, долг {len(res['debt'])} "
                    f"на {res['reserves']}"
                )
            if res['debt']:
                await notify_treasury_shortage(
                    bot, res['reserves'],
                    [(uid, amt) for uid, amt in res['debt']]
                )
        except Exception as e:
            logger.error(f"Ошибка выплаты зарплат: {e}", exc_info=True)
        try:
            payouts = await payout_reports()
            if payouts:
                for p in payouts:
                    try:
                        await bot.send_message(
                            p['user_id'],
                            "💰 ОПЛАТА ЗА ОТЧЁТЫ\n\n"
                            f"Одобрено отчётов: {p['count']}\n"
                            f"⚔️ Войска: +{p['troops']}\n"
                            f"💰 Нордмарки: +{p['nordmarks']} (налог {p['tax']} НМ в казну)\n"
                            f"──────────────\n"
                            f"Итого у тебя: {p['total_troops']} войск, {p['total_nordmarks']} нордмарок"
                        )
                    except Exception:
                        pass
                logger.info(f"Оплата отчётов: выплачено игрокам {len(payouts)}")
        except Exception as e:
            logger.error(f"Ошибка выплаты по отчётам: {e}", exc_info=True)
        try:
            pruned = await prune_activity_log(days=30)
            if pruned:
                logger.info(f"Очистка activity_log: удалено записей {pruned}")
        except Exception as e:
            logger.error(f"Ошибка очистки activity_log: {e}", exc_info=True)
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

    life_seeded = await ensure_life_items()
    if life_seeded:
        logger.info("Предметы жилья, мебели, еды и семян добавлены")

    reservoir_seeded = await ensure_dungeon_reservoir_items()
    if reservoir_seeded:
        logger.info("Рыба водохранилища и напитки-лечение обморожения добавлены")

    recipes_seeded = await ensure_recipes()
    if recipes_seeded:
        logger.info("Рецепты кухни и верстака добавлены")

    recipe_shop_seeded = await ensure_recipe_shop_items()
    if recipe_shop_seeded:
        logger.info("Рецепты добавлены в магазин (категория «Рецепты»)")
    if await ensure_user_recipes_backfill():
        logger.info("Существующим игрокам открыты все рецепты (бэкфилл)")

    wf_seeded = await ensure_water_fish()
    if wf_seeded:
        logger.info("Пулы рыбалки по водоёмам (water_fish) приведены к дефолтам")

    license_seeded = await ensure_market_license_item()
    if license_seeded:
        logger.info("Торговая лицензия добавлена в магазин")

    junk_moved = await migrate_legacy_junk()
    if junk_moved:
        logger.info("Легаси-мусор (сапог, водоросли) перенесён из инвентаря в «Улов»")

    await seed_kvp()
    logger.info("К.В.П. (Курс выживания) создан или проверен")

    await ensure_kvp_items()
    logger.info("Предметы К.В.П. (Офицерский стек) проверены")

    await ensure_kvp_award()
    logger.info("Награда К.В.П. («Значок В.У.С.П.») проверена")

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    @dp.errors()
    async def global_error_handler(event):
        """Глобальный перехват исключений хендлеров: пишем в activity_log (для
        поиска проблем по имени/тегу игрока) и в bot.log."""
        ex = event.exception
        uid = None
        try:
            ev = event.update.event if event.update else None
            src = getattr(ev, "from_user", None)
            uid = getattr(src, "id", None)
        except Exception:
            pass
        try:
            if uid:
                err_desc = f"{type(ex).__name__}: {str(ex)[:400]}"
                await log_activity(uid, "handle_error", err_desc)
        except Exception:
            pass
        logger.error(
            f"Ошибка хендлера (user {uid}): {type(ex).__name__}: {ex}",
            exc_info=(type(ex), ex, ex.__traceback__),
        )
        return True

    logger.info("Глобальный обработчик ошибок зарегистрирован")

    await bot.set_my_commands([
        BotCommand(command="start", description="Вход в систему"),
        BotCommand(command="profile", description="Мой профиль"),
        BotCommand(command="shop", description="Магазин товаров"),
        BotCommand(command="help", description="Справочник"),
    ])

    dp.include_router(start_router)
    dp.include_router(profile_router)
    dp.include_router(bank_router)
    dp.include_router(admin_router)
    dp.include_router(shop_router)
    dp.include_router(inventory_router)
    dp.include_router(reports_router)
    dp.include_router(dungeon_router)
    dp.include_router(pilots_router)
    dp.include_router(polls_router)
    dp.include_router(library_router)
    dp.include_router(locations_router)
    dp.include_router(park_router)
    dp.include_router(fishing_router)
    dp.include_router(housing_router)
    dp.include_router(news_router)
    dp.include_router(kvp_router)
    dp.include_router(wall_router)
    dp.include_router(hq_router)
    dp.include_router(clans_router)
    dp.include_router(nii_router)

    for r in (start_router, profile_router, bank_router, admin_router, shop_router,
              inventory_router, reports_router, dungeon_router, pilots_router,
              polls_router, library_router, locations_router, park_router,
              fishing_router, housing_router, news_router, kvp_router,
              wall_router, hq_router, clans_router, nii_router):
        r.message.middleware(FishingActiveLock())
        r.message.middleware(MainMenuFSMReset())
        r.callback_query.middleware(FishingActiveLock())

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
