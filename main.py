import asyncio
import logging
import os
import sys
from datetime import datetime, timedelta, timezone

from aiogram import Bot, Dispatcher, BaseMiddleware
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import BotCommand, Message, CallbackQuery
from dotenv import load_dotenv

from config import (BOT_TOKEN,
                    FSM_STORAGE_PATH,
                    REPORT_DAY_START_HOUR as PAYOUT_HOUR_MSK,
                    REPORT_DAY_START_MINUTE as PAYOUT_MINUTE_MSK)
from database.db import (
    init_db, close_db, daily_ap_recovery, seed_default_items, seed_dungeon,
    ensure_dungeon_shop_items, ensure_dungeon_enemy_drops, ensure_life_items, ensure_recipes,
    ensure_dungeon_reservoir_items, ensure_market_license_item, pay_salaries, payout_reports,
    pay_award_monthly,
    run_housing_tax, seed_kvp, ensure_kvp_items, ensure_kvp_award,
    ensure_tourist_booklet,
    ensure_water_fish, migrate_legacy_junk,
    ensure_forest_items, ensure_forest_mushrooms, ensure_forest_zones,
    ensure_forest_enemies, ensure_fishing_enemies, ensure_mollusk_items,
    ensure_recipe_shop_items, ensure_user_recipes_backfill,
    log_activity, prune_activity_log, prune_location_visits, recompute_region_stats,
    maybe_archive_wall_weekly, maintain_polls,
)
from utils.notify import notify_treasury_shortage
from utils.chat_guard import ChatGuard
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
from bot.handlers.poll_archive import router as poll_archive_router
from bot.handlers.representative import router as representative_router
from bot.handlers.library import router as library_router
from bot.handlers.locations import router as locations_router
from bot.handlers.park import router as park_router
from bot.handlers.fishing import router as fishing_router
from bot.handlers.forest import router as forest_router
from bot.handlers.housing import router as housing_router
from bot.handlers.news import router as news_router
from bot.handlers.kvp import router as kvp_router
from bot.handlers.wall import router as wall_router
from bot.handlers.hq import router as hq_router
from bot.handlers.clans import router as clans_router
from bot.handlers.nii import router as nii_router
from bot.handlers.tourist_booklet import router as tourist_booklet_router
from bot.handlers.changelog import router as changelog_router

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
            from bot.handlers.forest import deactivate_forest
            if is_main_menu_text(event.text) or event.text.startswith("/"):
                try:
                    await deactivate_fishing(event.from_user.id)
                    await deactivate_forest(event.from_user.id)
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

    Аналогично для леса: пока идёт поиск грибов (ложится результат через
    5–10 секунд), другие меню блокируются.
    """

    async def __call__(self, handler, event, data):
        from bot.handlers.fishing import FISHING_CASTING
        from bot.handlers.forest import FOREST_CASTING
        from bot.handlers.dungeon import MOLLUSK_BATTLE, purge_mollusk_battle

        purge_mollusk_battle()
        uid = getattr(event, "from_user", None)
        uid = uid.id if uid else None
        if uid and uid in MOLLUSK_BATTLE:
            # Идёт бой с моллюском в водохранилище: доступны только его кнопки.
            tip = "🦪 Ты в бою с моллюском — ударь или сбеги!"
            if isinstance(event, CallbackQuery):
                if (event.data or "").startswith("mollusk:"):
                    return await handler(event, data)
                await event.answer(tip, show_alert=True)
                return
            if isinstance(event, Message):
                if (event.text and (is_main_menu_text(event.text) or event.text.startswith("/"))) \
                        or not event.text:
                    try:
                        await event.answer(tip)
                    except Exception:
                        pass
                    return
            return await handler(event, data)
        if uid and (uid in FISHING_CASTING or uid in FOREST_CASTING):
            own_prefix = "fish:" if uid in FISHING_CASTING else "forest:"
            tip = ("🎣 Ты ещё ждёшь улов — дождись результата, а потом продолжим!"
                   if uid in FISHING_CASTING else
                   "🌲 Ты ещё ищешь грибы — дождись результата, а потом продолжим!")
            if isinstance(event, CallbackQuery):
                cb_data = event.data or ""
                if cb_data.startswith(own_prefix):
                    return await handler(event, data)
                await event.answer(tip, show_alert=True)
                return
            if isinstance(event, Message):
                if (event.text and (is_main_menu_text(event.text) or event.text.startswith("/"))) \
                        or not event.text:
                    try:
                        await event.answer(tip)
                    except Exception:
                        pass
                    return
        return await handler(event, data)


# Выплаты по отчётам, налоги, зарплаты и восстановление AP идут в одном суточном цикле.
# Время фиксировано по МСК: каждый день в 10:00 (PAYOUT_* импортированы из config —
# тот же час задаёт начало суток для отчётов, см. _report_day в database/db.py).
# Раньше цикл был «раз в 24 часа от старта процесса», поэтому время выплат плыло при
# каждом перезапуске (деплой). 10:00, а не 05:05: совпадает со сбросом суточных
# очков в игре, и ночной/утренний фарм попадает в те же сутки, что и в игре.
MSK = timezone(timedelta(hours=3))


def _seconds_until_payout() -> float:
    """Сколько секунд до ближайшего суточного цикла (10:00 МСК)."""
    local = datetime.now(MSK)
    target = local.replace(hour=PAYOUT_HOUR_MSK, minute=PAYOUT_MINUTE_MSK,
                           second=10, microsecond=0)
    if target <= local:
        target += timedelta(days=1)
    return (target - local).total_seconds()


async def scheduled_jobs(bot: Bot):
    while True:
        wait = _seconds_until_payout()
        logger.info(
            f"Суточный цикл: выплаты в {PAYOUT_HOUR_MSK:02d}:{PAYOUT_MINUTE_MSK:02d} МСК, "
            f"следующий запуск через {wait / 3600:.1f} ч"
        )
        # Сначала ЖДЁМ плановое время: цикл не должен срабатывать в момент рестарта
        # бота/деплоя, иначе выплаты и налоги происходят посреди дня. Раньше тело
        # выполнялось сразу при старте, и после деплоя вечером начисления шли
        # «в 22:00» вместо 10:00 — время плыло при каждом перезапуске.
        if wait > 0:
            await asyncio.sleep(wait)
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
            # v0.18.13: ежемесячные наградные (например, оклад ветерана) — 1-го числа,
            # деньги всегда из казны. Нехватка казны уходит в зарплатный долг.
            if datetime.now(MSK).day == 1:
                monthly = await pay_award_monthly()
                if monthly['paid'] or monthly['debt']:
                    logger.info(
                        f"Ежемесячные наградные: выплачено {len(monthly['paid'])}, "
                        f"в долг {len(monthly['debt'])}"
                    )
        except Exception as e:
            logger.error(f"Ошибка ежемесячных наградных: {e}", exc_info=True)
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
                            f"✨ Опыт (накопительный): +{p['xp']} "
                            f"(всего {p['xp_balance']}, без налога)\n"
                            f"💰 Нордмарки: +{p['nordmarks']} (налог {p['tax']} НМ в казну)\n"
                            f"──────────────\n"
                            f"Итого у тебя: {p['total_troops']} войск, {p['total_nordmarks']} нордмарок"
                        )
                    except Exception:
                        pass
                logger.info(f"Оплата отчётов: выплачено игрокам {len(payouts)}")
        except Exception as e:
            logger.error(f"Ошибка выплаты по отчётам: {e}", exc_info=True)
        # Статистика регионов = сумма показаний пилотов из их последних одобренных
        # отчётов, поэтому пересчитывается после выплаты: к этому моменту одобрены все
        # вчерашние сдачи. Раньше считалась только по кнопке админа и на проде
        # показывала устаревшие значения.
        try:
            regions = await recompute_region_stats()
            logger.info(f"Статистика регионов пересчитана: регионов {regions}")
        except Exception as e:
            logger.error(f"Ошибка пересчёта статистики регионов: {e}", exc_info=True)
        try:
            pruned = await prune_activity_log(days=30)
            if pruned:
                logger.info(f"Очистка activity_log: удалено записей {pruned}")
        except Exception as e:
            logger.error(f"Ошибка очистки activity_log: {e}", exc_info=True)
        try:
            pruned = await prune_location_visits(days=90)
            if pruned:
                logger.info(f"Очистка location_visits: удалено записей {pruned}")
        except Exception as e:
            logger.error(f"Ошибка очистки location_visits: {e}", exc_info=True)
        # Стена изречений: раз в неделю (пн) архивируем накопившееся, если его
        # больше одной страницы; иначе стена копится дальше, и архив покроет
        # несколько недель одним периодом.
        try:
            wall_res = await maybe_archive_wall_weekly()
            if wall_res:
                if wall_res.get('archived'):
                    logger.info(
                        f"Стена изречений: архивация #{wall_res['archive_id']} "
                        f"({wall_res['count']} изречений), стена очищена"
                    )
                else:
                    logger.info(
                        f"Стена изречений: архивация не нужна, "
                        f"{wall_res['count']} изречений (не больше страницы)"
                    )
        except Exception as e:
            logger.error(f"Ошибка недельной архивации стены: {e}", exc_info=True)
        # Опросы Ратуши: истёкшие (10 суток) закрываются, лишние уходят в архив
        # библиотеки. В меню голосования остаётся POLL_VISIBLE новейших. То же
        # выполняется лениво при открытии меню голосования — суточный проход
        # нужен, чтобы счётчик и архив были в порядке, даже если в меню не заходят.
        try:
            poll_res = await maintain_polls()
            if poll_res['closed'] or poll_res['archived']:
                logger.info(
                    f"Опросы: закрыто по сроку {poll_res['closed']}, "
                    f"в архив ушло {poll_res['archived']}"
                )
        except Exception as e:
            logger.error(f"Ошибка обслуживания опросов: {e}", exc_info=True)


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

    forest_items_seeded = await ensure_forest_items()
    if forest_items_seeded:
        logger.info("Предметы леса (грибы, кабан, жареные блюда, яд) добавлены")

    forest_seeded = await ensure_forest_mushrooms()
    if forest_seeded:
        logger.info("Пул грибов леса (forest_mushrooms) приведён к дефолтам")

    # v0.18.18: лес разделён на опушку и лесную поляну — перенос старого пула
    # в поляну и засев пула опушки (4 простых гриба + Бледная поганка).
    await ensure_forest_zones()
    logger.info("Зоны леса: опушка и лесная поляна настроены")

    # Враги леса и рыбалки (единый админ-редактор «⚔️ Враги»).
    forest_enemy_seeded = await ensure_forest_enemies()
    if forest_enemy_seeded:
        logger.info("Враг леса (кабан) добавлен в forest_enemies")

    mollusk_items_seeded = await ensure_mollusk_items()
    if mollusk_items_seeded:
        logger.info("Предметы моллюска (мясо, жемчужина, жареное мясо) добавлены")

    fishing_enemy_seeded = await ensure_fishing_enemies()
    if fishing_enemy_seeded:
        logger.info("Враг рыбалки (мутировавший моллюск) добавлен в fishing_enemies")

    license_seeded = await ensure_market_license_item()
    if license_seeded:
        logger.info("Торговая лицензия добавлена в магазин")

    junk_moved = await migrate_legacy_junk()
    if junk_moved:
        logger.info("Легаси-мусор (сапог, водоросли) перенесён из инвентаря в «Улов»")

    await seed_kvp()
    logger.info("К.В.П. (Курс выживания) создан или проверен")

    await ensure_kvp_items()
    logger.info("Предметы К.В.П. (Сержантская трость) проверены")

    await ensure_kvp_award()
    logger.info("Награда К.В.П. («Значок В.У.С.П.») проверена")

    await ensure_tourist_booklet()
    logger.info("Буклет туриста (предмет и награда) проверены")

    bot = Bot(token=BOT_TOKEN)
    # FSM — на диске, рядом с БД (/app/data в контейнере, docker volume): состояния
    # незаконченных форм переживают рестарт и деплой. На MemoryStorage любой рестарт
    # обнулял их, и пилот на середине формы получал молчание (v0.22.7).
    from bot.fsm_store import JsonFileStorage
    os.makedirs(FSM_STORAGE_PATH, exist_ok=True)
    dp = Dispatcher(storage=JsonFileStorage(os.path.join(FSM_STORAGE_PATH, "fsm_state.json")))
    logger.info(f"FSM-хранилище: {FSM_STORAGE_PATH}")

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
        # Раньше обработчик писал ошибку только в логи, и игрок после неудачного
        # действия не получал ровно ничего — выглядело как «бот завис». Теперь
        # сообщаем, что произошло, и что можно просто повторить действие (v0.22.7).
        try:
            ev = event.update.event if event.update else None
            if uid and ev is not None and not isinstance(ex, TelegramBadRequest):
                await ev.answer(
                    "⚠️ Что-то пошло не так — действие не выполнено.\n"
                    "Попробуй ещё раз. Если не помогло, напиши в техподдержку."
                )
        except Exception:
            pass
        return True

    logger.info("Глобальный обработчик ошибок зарегистрирован")

    await bot.set_my_commands([
        BotCommand(command="start", description="Вход в систему"),
        BotCommand(command="profile", description="Мой профиль"),
        BotCommand(command="shop", description="Магазин товаров"),
        BotCommand(command="help", description="Справочник"),
        BotCommand(command="changelog", description="Что нового в боте"),
    ])

    dp.include_router(start_router)
    dp.include_router(changelog_router)
    dp.include_router(profile_router)
    dp.include_router(bank_router)
    dp.include_router(admin_router)
    dp.include_router(shop_router)
    dp.include_router(inventory_router)
    dp.include_router(reports_router)
    dp.include_router(dungeon_router)
    dp.include_router(pilots_router)
    dp.include_router(polls_router)
    dp.include_router(poll_archive_router)
    dp.include_router(representative_router)
    dp.include_router(library_router)
    dp.include_router(locations_router)
    dp.include_router(park_router)
    dp.include_router(fishing_router)
    dp.include_router(forest_router)
    dp.include_router(housing_router)
    dp.include_router(news_router)
    dp.include_router(kvp_router)
    dp.include_router(wall_router)
    dp.include_router(hq_router)
    dp.include_router(clans_router)
    dp.include_router(nii_router)
    dp.include_router(tourist_booklet_router)

    for r in (start_router, changelog_router, profile_router, bank_router, admin_router, shop_router,
              inventory_router, reports_router, dungeon_router, pilots_router,
              polls_router, poll_archive_router, representative_router, library_router,
              locations_router, park_router,
              fishing_router, forest_router, housing_router, news_router, kvp_router,
              wall_router, hq_router, clans_router, nii_router):
        r.message.middleware(ChatGuard())
        r.message.middleware(FishingActiveLock())
        r.message.middleware(MainMenuFSMReset())
        r.callback_query.middleware(ChatGuard())
        r.callback_query.middleware(FishingActiveLock())

    logger.info("Хендлеры зарегистрированы")

    # Оповещение в общий чат о новой версии — один раз на релиз (v0.22.12):
    # срабатывает только при смене config.VERSION, обычный рестарт молчит.
    # Ошибка/отсутствие чата не мешает запуску — при неудаче попробуем в
    # следующий старт (ключ версии пишется только после успешной отправки).
    try:
        from utils.notify import notify_release_update
        if await notify_release_update(bot):
            logger.info("Оповещение о новой версии отправлено в общий чат")
    except Exception as e:
        logger.warning(f"Оповещение о новой версии не отправлено: {e}")

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
