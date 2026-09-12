"""Новости ГосСМИ: лента, публикация, управление выпусками, архив.

Публиковать могут «Журналист ГосСМИ» (до 2 выпусков/сутки) и «Редактор
ГосСМИ» / суперадмин (до 4). Редактор и суперадмин могут редактировать и
удалять выпуски. Лента показывает последние 10 выпусков; полный архив —
в Библиотеке.
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.db import (
    add_news, get_news, get_latest_news, get_all_news, update_news,
    delete_news, get_news_count_today, get_user,
)
from utils.permissions import has_permission
from utils.helpers import edit_or_replace, edit_message_safe
from config import ADMIN_IDS

router = Router()

FEED_LIMIT = 10
NEWS_PER_PAGE = 8

# Дневные лимиты публикаций по ролям
JOURNALIST_LIMIT = 2
EDITOR_LIMIT = 4


class NewsWrite(StatesGroup):
    title = State()
    body = State()
    photo = State()


class NewsEdit(StatesGroup):
    target = State()
    field = State()
    value = State()


async def daily_limit_for(user_id: int) -> tuple:
    """(лимит, неограничен): журналист 2/сутки, редактор 4/сутки, суперадмин — без лимита."""
    if await has_permission(user_id, "can_post_news") is False:
        return 0, False
    if await has_permission(user_id, "can_manage_news"):
        if user_id in ADMIN_IDS:
            return 0, True
        return EDITOR_LIMIT, False
    return JOURNALIST_LIMIT, False


async def news_menu_kb(has_manage: bool = False):
    rows = []
    if has_manage:
        rows.append([InlineKeyboardButton(text="✍️ Опубликовать", callback_data="news:write")])
    rows.append([InlineKeyboardButton(text="📚 Архив в Библиотеке", callback_data="news:archive")])
    rows.append([InlineKeyboardButton(text="🔙 Назад", callback_data="city:menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def feed_markup(news_list, has_manage: bool = False):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    rows = []
    for n in news_list:
        rows.append([InlineKeyboardButton(
            text=f"📰 {n['title']}",
            callback_data=f"news:view:{n['id']}"
        )])
    if has_manage:
        rows.append([InlineKeyboardButton(text="✍️ Опубликовать", callback_data="news:write")])
    rows.append([InlineKeyboardButton(text="📚 Архив новостей", callback_data="news:archive")])
    rows.append([InlineKeyboardButton(text="🔙 В город", callback_data="city:menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def fmt_release(n) -> str:
    author = n['author_name'] or f"#{n['author_id']}"
    when = (n['created_at'] or '')[:16].replace("T", " ")
    edited = " ✏️" if n['edited'] else ""
    return (f"📰 {n['title']}{edited}\n"
            f"✍️ {author} · {when}\n"
            f"{n['body'] or ''}")


@router.message(F.text == "📰 Новости Нордхайма")
async def news_tab(message: Message, user_id: int | None = None):
    """Вкладка «Новости Нордхайма» в главном меню и вход в здание «ГосСМИ».

    user_id нужен, когда вызываем напрямую из callback на ботовском сообщении
    (вход в здание): там message.from_user — это бот, а не игрок.
    """
    actor = user_id if user_id is not None else message.from_user.id if message.from_user else 0
    feed = await get_latest_news(FEED_LIMIT)
    if not feed:
        await message.answer(
            "📰 НОВОСТИ НОРДХАЙМА\n\n"
            "Новостей пока нет. Корреспонденты ГосСМИ ещё не выходили в эфир.",
            reply_markup=await news_menu_kb(await has_permission(actor, "can_post_news"))
        )
        return

    lines = [f"📰 НОВОСТИ НОРДХАЙМА\n\nПоследние {len(feed)} выпусков:"]
    for i, n in enumerate(feed, 1):
        lines.append(
            f"{i}. {n['title']} — {n['body'][:60] + ('…' if len(n['body']) > 60 else '')}"
        )
    await message.answer(
        "\n".join(lines),
        reply_markup=feed_markup(feed, await has_permission(actor, "can_post_news"))
    )


@router.callback_query(F.data == "news:archive")
async def news_archive(callback: CallbackQuery):
    await callback.answer()
    all_news = await get_all_news()
    if not all_news:
        await edit_or_replace(callback.message, "Архив новостей пуст.", None)
        return
    await _archive_page(callback, all_news, 0)


def archive_page_markup(all_news, page: int):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    total = len(all_news)
    pages = max(1, (total + NEWS_PER_PAGE - 1) // NEWS_PER_PAGE)
    page = max(0, min(page, pages - 1))
    start = page * NEWS_PER_PAGE
    chunk = all_news[start:start + NEWS_PER_PAGE]
    rows = []
    for n in chunk:
        rows.append([InlineKeyboardButton(text=f"📰 {n['title']}", callback_data=f"news:view:{n['id']}")])
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="◀️", callback_data=f"news:arch:{page-1}"))
    nav.append(InlineKeyboardButton(text=f"{page+1}/{pages}", callback_data="noop"))
    if page < pages - 1:
        nav.append(InlineKeyboardButton(text="▶️", callback_data=f"news:arch:{page+1}"))
    if nav:
        rows.append(nav)
    rows.append([InlineKeyboardButton(text="🔙 Назад", callback_data="city:menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def _archive_page(callback: CallbackQuery, all_news, page: int):
    await edit_or_replace(
        callback.message,
        f"📚 АРХИВ НОВОСТЕЙ\nВсего выпусков: {len(all_news)}",
        archive_page_markup(all_news, page)
    )


@router.callback_query(F.data.regexp(r"^news:arch:\d+$"))
async def news_archive_page(callback: CallbackQuery):
    await callback.answer()
    page = int(callback.data.split(":")[2])
    all_news = await get_all_news()
    if not all_news:
        await edit_or_replace(callback.message, "Архив новостей пуст.", None)
        return
    await _archive_page(callback, all_news, page)


@router.callback_query(F.data.startswith("news:view:"))
async def news_view(callback: CallbackQuery):
    await callback.answer()
    news_id = int(callback.data.split(":")[2])
    n = await get_news(news_id)
    if not n:
        await callback.message.answer("❌ Выпуск не найден.")
        return

    text = fmt_release(n)
    user_id = callback.from_user.id
    can_manage = await has_permission(user_id, "can_manage_news")

    rows = []
    if can_manage:
        rows.append([
            InlineKeyboardButton(text="✏️ Изменить", callback_data=f"news:edit:{news_id}"),
            InlineKeyboardButton(text="🗑 Удалить", callback_data=f"news:del:{news_id}"),
        ])
    rows.append([InlineKeyboardButton(text="🔙 Назад", callback_data="news:tab")])
    kb = InlineKeyboardMarkup(inline_keyboard=rows)

    if n['photo_file_id']:
        from aiogram.types import InputMediaPhoto
        try:
            if callback.message.photo:
                await callback.message.edit_media(
                    media=InputMediaPhoto(media=n['photo_file_id'], caption=text),
                    reply_markup=kb
                )
            else:
                await callback.message.delete()
                await callback.message.answer_photo(photo=n['photo_file_id'], caption=text, reply_markup=kb)
        except Exception:
            await callback.message.answer_photo(photo=n['photo_file_id'], caption=text, reply_markup=kb)
    else:
        await edit_or_replace(callback.message, text, kb)


@router.callback_query(F.data == "news:tab")
async def news_tab_back(callback: CallbackQuery):
    await callback.answer()
    feed = await get_latest_news(FEED_LIMIT)
    can = await has_permission(callback.from_user.id, "can_post_news")
    if not feed:
        await edit_or_replace(
            callback.message,
            "📰 НОВОСТИ НОРДХАЙМА\n\nНовостей пока нет.",
            await news_menu_kb(can)
        )
        return
    lines = [f"📰 НОВОСТИ НОРДХАЙМА\n\nПоследние {len(feed)} выпусков:"]
    for i, n in enumerate(feed, 1):
        lines.append(f"{i}. {n['title']} — {n['body'][:60] + ('…' if len(n['body']) > 60 else '')}")
    await edit_or_replace(callback.message, "\n".join(lines), feed_markup(feed, can))


# ───────── публикация ─────────

@router.callback_query(F.data == "news:write")
async def news_write_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    user_id = callback.from_user.id
    if not await has_permission(user_id, "can_post_news"):
        await callback.message.answer("❌ Публиковать новости может только корреспондент ГосСМИ.")
        return

    limit, unlimited = await daily_limit_for(user_id)
    used = await get_news_count_today(user_id)
    if not unlimited and used >= limit:
        await callback.message.answer(
            f"⛔ Твой дневной лимит публикаций исчерпан ({limit} в сутки). Попробуй завтра."
        )
        return

    await state.set_state(NewsWrite.title)
    await callback.message.answer(
        "📰 НОВЫЙ ВЫПУСК\n\n"
        "Напиши заголовок новости:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]
        ])
    )


@router.message(NewsWrite.title, F.text)
async def news_write_title(message: Message, state: FSMContext):
    title = message.text.strip()
    if title.lower() == "/cancel":
        await state.clear()
        await message.answer("Публикация отменена.")
        return
    if not title or len(title) > 80:
        await message.answer("❌ Заголовок не может быть пустым и длиннее 80 символов. Повтори:")
        return
    await state.update_data(title=title)
    await state.set_state(NewsWrite.body)
    await message.answer(
        "📝 Теперь напиши текст новости:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]
        ])
    )


@router.message(NewsWrite.body, F.text)
async def news_write_body(message: Message, state: FSMContext):
    body = message.text.strip()
    if body.lower() == "/cancel":
        await state.clear()
        await message.answer("Публикация отменена.")
        return
    if not body:
        await message.answer("❌ Текст не может быть пустым. Напиши его:")
        return
    await state.update_data(body=body)
    await state.set_state(NewsWrite.photo)
    await message.answer(
        "🖼 Можешь прикрепить фото к выпуску. Отправь фото "
        "(или «-» / «Пропустить», чтобы без картинки):",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Без фото", callback_data="news:no_photo")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")],
        ])
    )


@router.callback_query(F.data == "news:no_photo")
async def news_photo_skip(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await _finish_news(callback.message, state, photo_file_id=None)


@router.message(NewsWrite.photo)
async def news_write_photo(message: Message, state: FSMContext):
    if message.text and message.text.strip().lower() == "/cancel":
        await state.clear()
        await message.answer("Публикация отменена.")
        return
    if message.text and message.text.strip() in ("-", "Пропустить"):
        await _finish_news(message, state, photo_file_id=None)
        return
    if not message.photo:
        await message.answer("❌ Отправь фото, «-», «Пропустить» или кнопку «Без фото»:")
        return
    await _finish_news(message, state, photo_file_id=message.photo[-1].file_id)


async def _finish_news(message, state: FSMContext, photo_file_id):
    user_id = message.from_user.id
    data = await state.get_data()
    title, body = data.get('title'), data.get('body')

    # повторная проверка лимита на случай долгого ввода
    limit, unlimited = await daily_limit_for(user_id)
    used = await get_news_count_today(user_id)
    if not unlimited and used >= limit:
        await state.clear()
        await message.answer(
            f"⛔ Дневной лимит публикаций исчерпан ({limit} в сутки). Попробуй завтра."
        )
        return

    author = await get_user(user_id)
    author_name = f"@{author['username']}" if author and author['username'] else ""
    news_id = await add_news(title, body, user_id, author_name, photo_file_id)

    await state.clear()
    await message.answer(f"✅ Выпуск опубликован!\n\n{fmt_release(await get_news(news_id))}")


# ───────── редактирование и удаление (редактор / суперадмин) ─────────

@router.callback_query(F.data.startswith("news:edit:"))
async def news_edit_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_news"):
        await callback.message.answer("❌ Изменять новости может только редактор ГосСМИ.")
        return
    news_id = int(callback.data.split(":")[2])
    n = await get_news(news_id)
    if not n:
        await callback.message.answer("❌ Выпуск не найден.")
        return
    await state.update_data(target=news_id)
    await state.set_state(NewsEdit.field)
    await callback.message.answer(
        "✏️ ЧТО ИЗМЕНИТЬ?\n\n"
        f"Текущий заголовок: {n['title']}\n\n"
        "Пришли новый заголовок (или «-», чтобы оставить):",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]
        ])
    )


@router.message(NewsEdit.field, F.text)
async def news_edit_title(message: Message, state: FSMContext):
    data = await state.get_data()
    news_id = data['target']
    n = await get_news(news_id)
    if not n:
        await state.clear()
        await message.answer("❌ Выпуск не найден.")
        return
    new_title = message.text.strip()
    if new_title.lower() == "/cancel":
        await state.clear()
        await message.answer("Редактирование отменено.")
        return
    if new_title and new_title != "-" and len(new_title) > 80:
        await message.answer("❌ Заголовок не может быть длиннее 80 символов. Повтори:")
        return
    await update_news(news_id, title=(new_title if new_title and new_title != "-" else None))
    await state.update_data(title=(new_title if new_title and new_title != "-" else None))
    await state.set_state(NewsEdit.value)
    await message.answer(
        f"Текущий текст: {n['body']}\n\nПришли новый текст (или «-», чтобы оставить):",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]
        ])
    )


@router.message(NewsEdit.value, F.text)
async def news_edit_body(message: Message, state: FSMContext):
    data = await state.get_data()
    news_id = data['target']
    new_body = message.text.strip()
    if new_body.lower() == "/cancel":
        await state.clear()
        await message.answer("Редактирование отменено.")
        return
    if new_body and new_body != "-":
        await update_news(news_id, body=new_body)
    await state.clear()
    n = await get_news(news_id)
    if not n:
        await message.answer("❌ Выпуск не найден.")
        return
    await message.answer(f"✅ Выпуск обновлён.\n\n{fmt_release(n)}")


@router.callback_query(F.data.startswith("news:del:"))
async def news_delete(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_news"):
        await callback.message.answer("❌ Удалять новости может только редактор ГосСМИ.")
        return
    news_id = int(callback.data.split(":")[2])
    n = await get_news(news_id)
    if not n:
        await callback.message.answer("❌ Выпуск не найден.")
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Да, удалить", callback_data=f"news:delconf:{news_id}")],
        [InlineKeyboardButton(text="❌ Нет", callback_data=f"news:view:{news_id}")],
    ])
    await edit_or_replace(
        callback.message,
        f"🗑 УДАЛИТЬ ВЫПУСК?\n\n{fmt_release(n)}",
        kb
    )


@router.callback_query(F.data.startswith("news:delconf:"))
async def news_delete_confirm(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_news"):
        await callback.message.answer("❌ Удалять новости может только редактор ГосСМИ.")
        return
    news_id = int(callback.data.split(":")[2])
    deleted = await delete_news(news_id)
    await edit_or_replace(
        callback.message,
        "🗑 Выпуск удалён." if deleted else "❌ Выпуск не найден.",
        None
    )