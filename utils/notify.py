"""Оповещения об игровых событиях в общую группу (NEWS_CHAT_ID).

Каждого игрока можно исключить из оповещений (флаг notify_enabled),
переключаемый в профиле — доступно со статуса «Ветеран» и выше.

Все тексты оповещений в общий чат намеренно обходятся БЕЗ точных цифр отчётов:
в группе видно только похвалу за мастерство, имена и названия наград.
"""

from aiogram import Bot

from database.db import get_db, get_user, get_news_chat
from config import ADMIN_IDS

# Пороги для похвалы за суточный отчёт (строго больше):
#   > MASTERY — «высокое мастерство», > ACE — «истинный Ас», иначе молчим.
NOTIFY_REPORT_MASTERY_TROOPS = 150
NOTIFY_REPORT_ACE_TROOPS = 300


async def player_display(user) -> str:
    """Имя или позывной пилота для красивой подписи."""
    if user is None:
        return "пилот"
    keys = user.keys() if hasattr(user, 'keys') else []
    try:
        username = user['username'] if 'username' in keys else None
    except (KeyError, IndexError):
        username = None
    if username:
        return f"@{username}"
    try:
        name = (user['first_name'] if 'first_name' in keys else '') or ''
    except (KeyError, IndexError):
        name = ''
    name = name.strip()
    if name:
        return name
    try:
        uid = user['user_id'] if 'user_id' in keys else None
    except (KeyError, IndexError):
        uid = None
    return f"#{uid}" if uid is not None else "пилот"


async def player_callsign_display(user) -> str:
    """Имя пилота для похвалы за рекордные отчёты: позывной, иначе @username.

    В общий чат при записи рекорда выводится игровой позывной (callsign), а не
    тег телеграма, если пилот его установил; иначе — @username, затем реальное имя.
    """
    if user is None:
        return "пилот"
    keys = user.keys() if hasattr(user, 'keys') else []
    try:
        callsign = user['callsign'] if 'callsign' in keys else None
    except (KeyError, IndexError):
        callsign = None
    if callsign and str(callsign).strip():
        return str(callsign).strip()
    return await player_display(user)


async def notifications_enabled(user_id: int) -> bool:
    user = await get_user(user_id)
    if not user:
        return True
    return bool(user['notify_enabled'] if 'notify_enabled' in user.keys() else 1)


async def notify(bot: Bot, text: str, user_id: int = None) -> bool:
    """Отправить игровое оповещение в общую группу (или в её топик).

    Куда именно — настройка «news_chat_id» + «news_topic_id» (см. get_news_chat):
    для супергруппы с форумом бот пишет в конкретный топик, иначе — в общий чат.

    Если пользователь отключил оповещения о себе — сообщение не отправляется.
    Ошибка отправки пишется в журнал (handle_error), а не проглатывается молча:
    иначе «нет оповещений» и «бот не имеет прав в чате» выглядят одинаково.

    Возвращает True только при реально отправленном сообщении — вызывающий по
    этому признаку решает, запоминать ли состояние (см. notify_release_update).
    """
    chat_id, topic_id = await get_news_chat()
    if not chat_id:
        return False
    if user_id is not None and not await notifications_enabled(user_id):
        return False
    try:
        await bot.send_message(chat_id, text, message_thread_id=topic_id)
        return True
    except Exception as e:
        from database.db import log_activity
        await log_activity(None, 'notify_failed', f"chat={chat_id} topic={topic_id}: {e}")
        return False


# Ключ settings с последней версией, объявленной в общем чате (см. notify_release_update).
RELEASE_ANNOUNCED_SETTING_KEY = "last_announced_version"


def release_update_text(version: str, notes: str) -> str:
    """Короткое релизное оповещение для общего чата: версия, суть, где подробности.

    Без команды-/ссылки `/changelog`: в общем чате Telegram она нерабочая и
    выглядит как сломанная кнопка — подробности смотрят прямо в боте.
    """
    flat = " ".join(str(notes or "").split())
    return (
        f"🔄 Н.О.Р.Д. обновлён — v{version}\n"
        f"📝 {flat}\n"
        f"📄 Подробности смотри в боте."
    )


async def notify_release_update(bot: Bot) -> bool:
    """Сообщить в общий чат о новой версии бота — один раз на релиз.

    Сравнивает config.VERSION с последней объявленной версией в settings
    (ключ last_announced_version). Обычный рестарт/пересборка с той же версией
    молчит; смена версии (деплой) — шлёт короткое описание (VERSION_NOTES).

    Ключ записывается ТОЛЬКО после успешной отправки: если чат не настроен или
    бот без прав, оповещение уйдёт при следующем старте после настройки.
    Первый запуск (ключа ещё нет) объявляет текущую версию — фичу видно сразу.
    """
    from config import VERSION, VERSION_NOTES
    from database.db import get_setting, set_setting

    last = await get_setting(RELEASE_ANNOUNCED_SETTING_KEY)
    if last == VERSION:
        return False
    if not await notify(bot, release_update_text(VERSION, VERSION_NOTES)):
        return False
    await set_setting(RELEASE_ANNOUNCED_SETTING_KEY, VERSION)
    return True


PRIZE_TIER_NONE = 0
PRIZE_TIER_MASTERY = 1
PRIZE_TIER_ACE = 2


def praise_tier_for(day_total: int) -> int:
    """Уровень похвалы по накопленной сумме за сутки.

    Считается от суммы всех принятых отчётов за МСК-сутки, поэтому несколько
    отчётов складываются: 160 → «мастерство», а +200 сверху (350 за сутки) →
    «истинный Ас».
    """
    try:
        day_total = int(day_total)
    except (TypeError, ValueError):
        return PRIZE_TIER_NONE
    if day_total > NOTIFY_REPORT_ACE_TROOPS:
        return PRIZE_TIER_ACE
    if day_total > NOTIFY_REPORT_MASTERY_TROOPS:
        return PRIZE_TIER_MASTERY
    return PRIZE_TIER_NONE


def report_praise_text(display: str, amount: int):
    """Похвала за суточный отчёт. Без цифр — только ободряющая фраза.

    Ниже порогов возвращается None: обычные отчёты в общий чат не попадают.
    """
    return praise_tier_text(display, praise_tier_for(amount))


def praise_tier_text(display: str, tier: int):
    """Текст похвалы для заданного уровня (None — уровня нет)."""
    if tier >= PRIZE_TIER_ACE:
        return f"🏆 {display} проявляет характер истинного Аса!"
    if tier >= PRIZE_TIER_MASTERY:
        return f"⚡ {display} показал высокое мастерство!"
    return None


async def notify_report_praise(bot: Bot, pilot, user_id: int = None, day_total: int = None,
                               day: str = None):
    """Похвала за суточный отчёт по накопленной сумме за отчётные сутки.

    Уровень считается по сумме всех принятых отчётов за сутки, а не по одному
    отчёту. За сутки один уровень отправляется только один раз: переход на
    следующий (накопил свыше 300 за день) приходит повторным оповещением, отчёт
    ниже порога молчит.

    day — отчётные сутки 'YYYY-MM-DD' САМОГО одобряемого отчёта. Когда отчёт
    сдан вчера (после 10:00), а одобряется сегодня, без этого дня «сегодняшняя»
    сумма была бы пустой и похвала терялась бы.

    day_total — переопределение суммы за сутки (для тестов).
    """
    from database.db import report_day_credited_total, get_report_notify_tier, bump_report_notify_tier

    uid = user_id if user_id is not None else getattr(pilot, "id", None)
    if uid is None:
        return False
    if day_total is None:
        day_total = await report_day_credited_total(uid, day=day)
    tier = praise_tier_for(day_total)
    if tier == PRIZE_TIER_NONE:
        return False
    if tier <= await get_report_notify_tier(uid, day=day):
        return False
    text = praise_tier_text(await player_callsign_display(pilot), tier)
    if not text:
        return False
    await notify(bot, text, uid)
    await bump_report_notify_tier(uid, tier, day=day)
    return True


async def notify_award(bot: Bot, pilot, award_title: str, user_id: int = None):
    """Оповещение о выдаче любой награды: «@pilot награждён: Название»."""
    title = (award_title or "").strip() or "награда"
    await notify(bot, f"🎖️ {await player_display(pilot)} награждён: {title}", user_id)


async def treasury_staff_ids() -> list:
    """Telegram-id суперадминов и минфина (для уведомлений о казне)."""
    ids = set(ADMIN_IDS)
    db = await get_db()
    cursor = await db.execute(
        "SELECT DISTINCT telegram_id FROM user_roles WHERE role = 'finance_admin'"
    )
    for row in await cursor.fetchall():
        ids.add(row['telegram_id'])
    return list(ids)


async def notify_treasury_shortage(bot: Bot, total_shortage: int, details: list):
    """Сообщить суперадмину и минфину о нехватке казны на зарплаты.

    details — список кортежей (user_id, amount_owed) тех, кому не хватило.
    """
    if total_shortage <= 0 or not details:
        return
    lines = [
        f"⚠️ НЕХВАТКА КАЗНЫ НА ЗАРПЛАТЫ\n"
        f"Не хватило суммарно: {total_shortage} НМ\n"
        f"Задолженность копится и будет выплачена, когда появятся средства.\n"
        f"\nДолжники:"
    ]
    for uid, amt in details[:15]:
        u = await get_user(uid)
        name = await player_display(u)
        lines.append(f"  • {name}: {amt} НМ")
    if len(details) > 15:
        lines.append(f"  … и ещё {len(details) - 15} пилотов")
    text = "\n".join(lines)
    for tg_id in await treasury_staff_ids():
        try:
            await bot.send_message(tg_id, text)
        except Exception:
            pass