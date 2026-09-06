"""Библиотека Нордхайма: разделы, чтение книг, управление книгами."""

import os

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.db import (
    get_library_cards, can_access_sections, has_library_access,
    get_library_books, get_library_book, add_library_book, delete_library_book,
)
from keyboards.keyboards import cancel_keyboard
from utils.permissions import has_permission, log_action
from utils.helpers import resolve_image

router = Router()

SECTION_LABELS = {
    "history": "🏛️ Исторический",
    "laws": "⚖️ Законы",
    "religion": "🕯️ Религия",
    "fiction": "📖 Художественная литература",
    "encyclopedias": "📚 Энциклопедии",
}

LIBRARY_PHOTO = "city/library"


class AdminAddBook(StatesGroup):
    section = State()
    title = State()
    author = State()
    description = State()
    cover = State()
    content = State()  # либо файл, либо ссылка


def library_photo() -> FSInputFile:
    path = resolve_image(LIBRARY_PHOTO)
    if not os.path.isfile(path):
        path = resolve_image("city/arkholm")
    return FSInputFile(path)


def sections_markup(open_sections: list, is_manager: bool = False):
    rows = []
    for key, label in SECTION_LABELS.items():
        if key in open_sections:
            rows.append([InlineKeyboardButton(text=label, callback_data=f"libsec:{key}")])
        else:
            rows.append([InlineKeyboardButton(
                text=f"🔒 {label}", callback_data="lib:no_access"
            )])
    if is_manager:
        rows.append([InlineKeyboardButton(text="🛠 Управление книгами", callback_data="libadmin:menu")])
    rows.append([InlineKeyboardButton(text="🔙 В город", callback_data="city:menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def books_markup(books, section: str):
    rows = []
    for b in books:
        label = b['title']
        if b['author']:
            label += f" — {b['author']}"
        rows.append([InlineKeyboardButton(text=label, callback_data=f"libbook:{b['id']}")])
    rows.append([InlineKeyboardButton(text="🔙 В библиотеку", callback_data="lib:menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def manager_markup(user_id: int):
    return await has_permission(user_id, "can_manage_library")


@router.callback_query(F.data == "city:library")
async def library_enter(callback: CallbackQuery):
    await callback.answer()
    photo = FSInputFile(resolve_image(LIBRARY_PHOTO))
    is_manager = await manager_markup(callback.from_user.id)
    if not await has_library_access(callback.from_user.id):
        if is_manager:
            caption = (
                "📚 БИБЛИОТЕКА НОРДХАЙМА\n\n"
                "У тебя есть права управления книгами.\n"
                "Разделы доступны читателям с билетом."
            )
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🛠 Управление книгами", callback_data="libadmin:menu")],
                [InlineKeyboardButton(text="🔙 В город", callback_data="city:menu")],
            ])
        else:
            caption = (
                "📚 БИБЛИОТЕКА НОРДХАЙМА\n\n"
                "Доступ только по читательскому билету.\n"
                "Билеты продаются в Магазине → «Читательские билеты»."
            )
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 В город", callback_data="city:menu")]
            ])
    else:
        cards = await get_library_cards(callback.from_user.id)
        lines = []
        for c in cards:
            kind = "Серебряный" if c['card_type'] == "silver" else "Обычный"
            expires = c['expires_at'][:10] if c['expires_at'] else "?"
            lines.append(f"• {kind} — действует до {expires}")
        open_list = await can_access_sections(callback.from_user.id)
        caption = (
            "📚 БИБЛИОТЕКА НОРДХАЙМА\n\n"
            "Твои билеты:\n" + "\n".join(lines) + "\n\n"
            "Выбери раздел:"
        )
        kb = sections_markup(open_list, is_manager)

    if callback.message.photo:
        from aiogram.types import InputMediaPhoto
        await callback.message.edit_media(
            media=InputMediaPhoto(media=photo, caption=caption),
            reply_markup=kb
        )
    else:
        await callback.message.answer_photo(photo=photo, caption=caption, reply_markup=kb)


@router.callback_query(F.data == "lib:no_access")
async def lib_no_access(callback: CallbackQuery):
    await callback.answer("🔒 Нужна карта получше. Серебряный билет открывает все разделы.", show_alert=False)


@router.callback_query(F.data == "lib:menu")
async def library_menu(callback: CallbackQuery):
    """Возврат в меню разделов изнутри библиотеки."""
    await callback.answer()
    photo = FSInputFile(resolve_image(LIBRARY_PHOTO))
    is_manager = await manager_markup(callback.from_user.id)
    cards = await get_library_cards(callback.from_user.id)
    if not cards:
        if is_manager:
            await callback.message.answer(
                "📚 У тебя нет активного билета.\n"
                "Но ты можешь управлять книгами.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🛠 Управление книгами", callback_data="libadmin:menu")],
                    [InlineKeyboardButton(text="🔙 В город", callback_data="city:menu")],
                ])
            )
        else:
            await callback.message.answer(
                "📚 У тебя нет активного билета. Купи его в Магазине.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 В город", callback_data="city:menu")]
                ])
            )
        return
    open_list = await can_access_sections(callback.from_user.id)
    caption = "📚 БИБЛИОТЕКА НОРДХАЙМА\n\nВыбери раздел:"
    if callback.message.photo:
        from aiogram.types import InputMediaPhoto
        await callback.message.edit_media(
            media=InputMediaPhoto(media=photo, caption=caption),
            reply_markup=sections_markup(open_list, is_manager)
        )
    else:
        await callback.message.answer_photo(photo=photo, caption=caption, reply_markup=sections_markup(open_list, is_manager))


@router.callback_query(F.data.regexp(r"^libsec:[a-z]+$"))
async def library_section(callback: CallbackQuery):
    await callback.answer()
    section = callback.data.split(":")[1]
    open_list = await can_access_sections(callback.from_user.id)
    if section not in open_list:
        await callback.message.answer("🔒 У этого раздела нет доступа с твоим билетом.")
        return

    books = await get_library_books(section)
    if not books:
        await callback.message.edit_text(
            f"{SECTION_LABELS.get(section, section)}\n\nПока нет книг в этом разделе.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 В библиотеку", callback_data="lib:menu")]
            ])
        )
        return
    await callback.message.edit_text(
        f"{SECTION_LABELS.get(section, section)}:",
        reply_markup=books_markup(books, section)
    )


@router.callback_query(F.data.startswith("libbook:"))
async def library_book(callback: CallbackQuery):
    await callback.answer()
    book_id = int(callback.data.split(":")[1])
    book = await get_library_book(book_id)
    if not book:
        await callback.message.edit_text("Книга не найдена.", reply_markup=None)
        return

    open_list = await can_access_sections(callback.from_user.id)
    if book['section'] not in open_list:
        await callback.message.answer("🔒 Нет доступа к этой книге с твоим билетом.")
        return

    text = f"📖 {book['title']}\n"
    if book['author']:
        text += f"✍️ {book['author']}\n"
    text += f"\n{SECTION_LABELS.get(book['section'], book['section'])}\n"
    if book['description']:
        text += f"\n{book['description']}\n"

    buttons = []
    if book['url']:
        buttons.append([InlineKeyboardButton(text="🔗 Открыть", url=book['url'])])
    if book['file_id']:
        buttons.append([InlineKeyboardButton(text="📥 Скачать", callback_data=f"libdl:{book['id']}")])
    buttons.append([InlineKeyboardButton(text="🔙 В библиотеку", callback_data="lib:menu")])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    cover = book['cover_file_id']
    if cover:
        if callback.message.photo:
            from aiogram.types import InputMediaPhoto
            await callback.message.edit_media(
                media=InputMediaPhoto(media=cover, caption=text),
                reply_markup=kb
            )
        else:
            await callback.message.answer_photo(photo=cover, caption=text, reply_markup=kb)
    else:
        await callback.message.edit_text(text, reply_markup=kb)


@router.callback_query(F.data.startswith("libdl:"))
async def library_download(callback: CallbackQuery):
    await callback.answer()
    book_id = int(callback.data.split(":")[1])
    book = await get_library_book(book_id)
    if not book or not book['file_id']:
        await callback.message.answer("Файл недоступен.")
        return
    await callback.message.answer_document(document=book['file_id'], caption=book['title'])


# ============ УПРАВЛЕНИЕ КНИГАМИ (внутри библиотеки) ============

def library_section_picker_markup():
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    rows = []
    for key, label in SECTION_LABELS.items():
        rows.append([InlineKeyboardButton(text=label, callback_data=f"libadmin_sec:{key}")])
    rows.append([InlineKeyboardButton(text="🔙 В библиотеку", callback_data="lib:menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


@router.callback_query(F.data == "libadmin:menu")
async def library_admin_menu(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_library"):
        await callback.message.answer("❌ Нет прав для управления книгами.")
        return
    await callback.message.edit_text(
        "🛠 УПРАВЛЕНИЕ БИБЛИОТЕКОЙ\n\nВыбери действие:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ Добавить книгу", callback_data="libadmin:add")],
            [InlineKeyboardButton(text="🗑️ Удалить книгу", callback_data="libadmin:list")],
            [InlineKeyboardButton(text="🔙 В библиотеку", callback_data="lib:menu")],
        ])
    )


@router.callback_query(F.data == "libadmin:add")
async def book_add_section(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_library"):
        return
    await state.set_state(AdminAddBook.section)
    await callback.message.answer("Выбери раздел книги:", reply_markup=library_section_picker_markup())


@router.callback_query(F.data.startswith("libadmin_sec:"))
async def book_section(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    section = callback.data.split(":")[1]
    await state.update_data(section=section)
    await state.set_state(AdminAddBook.title)
    await callback.message.answer("📖 Введи название книги:", reply_markup=cancel_keyboard())


@router.message(AdminAddBook.title)
async def book_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text.strip())
    await state.set_state(AdminAddBook.author)
    await message.answer("✍️ Введи автора (или «—»):", reply_markup=cancel_keyboard())


@router.message(AdminAddBook.author)
async def book_author(message: Message, state: FSMContext):
    author = message.text.strip()
    await state.update_data(author="" if author == "—" else author)
    await state.set_state(AdminAddBook.description)
    await message.answer("📝 Введи описание книги:", reply_markup=cancel_keyboard())


@router.message(AdminAddBook.description)
async def book_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text.strip())
    await state.set_state(AdminAddBook.cover)
    await message.answer(
        "🖼️ Пришли обложку книги (картинка).\n"
        "Или напиши «—», если обложки нет:",
        reply_markup=cancel_keyboard()
    )


@router.message(AdminAddBook.cover)
async def book_cover(message: Message, state: FSMContext):
    cover_file_id = None
    if message.photo:
        cover_file_id = message.photo[-1].file_id
    elif message.text and message.text.strip() == "—":
        cover_file_id = None
    else:
        await message.answer("❌ Пришли картинку (фото) или «—» для пропуска:", reply_markup=cancel_keyboard())
        return
    await state.update_data(cover_file_id=cover_file_id)
    await state.set_state(AdminAddBook.content)
    await message.answer(
        "📎 Пришли файл книги (pdf/epub/txt) ИЛИ просто ссылку на скачивание:",
        reply_markup=cancel_keyboard()
    )


@router.message(AdminAddBook.content)
async def book_content(message: Message, state: FSMContext):
    data = await state.get_data()
    file_id = None
    file_type = None
    url = None

    if message.document:
        file_id = message.document.file_id
        file_type = message.document.mime_type or "document"
    elif message.text and message.text.startswith("http"):
        url = message.text.strip()
    else:
        await message.answer("❌ Пришли файл документом или ссылку (начинается с http).", reply_markup=cancel_keyboard())
        return

    await add_library_book(
        section=data['section'],
        title=data['title'],
        author=data['author'],
        description=data['description'],
        cover_file_id=data.get('cover_file_id'),
        file_id=file_id,
        file_type=file_type,
        url=url,
        added_by=message.from_user.id,
    )
    await log_action(message.from_user.id, 'add_book', None, data['title'])
    await state.clear()
    await message.answer(
        f"✅ Книга «{data['title']}» добавлена в раздел «{SECTION_LABELS.get(data['section'], data['section'])}»."
    )


@router.callback_query(F.data == "libadmin:list")
async def book_list(callback: CallbackQuery):
    await callback.answer()
    if not await has_permission(callback.from_user.id, "can_manage_library"):
        return
    all_books = []
    for section in SECTION_LABELS:
        all_books.extend(await get_library_books(section))
    if not all_books:
        await callback.message.answer("📚 В библиотеке пока нет книг.")
        return
    rows = []
    for b in all_books:
        rows.append([InlineKeyboardButton(
            text=f"🗑 {b['title']}",
            callback_data=f"libadmin_del:{b['id']}"
        )])
    rows.append([InlineKeyboardButton(text="🔙 В библиотеку", callback_data="libadmin:menu")])
    await callback.message.edit_text(
        "📚 Книги в библиотеке (выбери для удаления):",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows)
    )


@router.callback_query(F.data.startswith("libadmin_del:"))
async def book_delete(callback: CallbackQuery):
    await callback.answer()
    book_id = int(callback.data.split(":")[1])
    book = await get_library_book(book_id)
    if not book:
        await callback.message.answer("❌ Книга не найдена.")
        return
    await delete_library_book(book_id)
    await log_action(callback.from_user.id, 'delete_book', None, book['title'])
    await callback.message.answer(f"🗑️ Книга «{book['title']}» удалена из библиотеки.")