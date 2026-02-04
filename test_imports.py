try:
    import telegram
    import dotenv
    import aiosqlite
    from PIL import Image
    print("Все Библиотеки успешно импортируются!")
    print(f"python-telegram-bot: {telegram.__version__}")
except ImportError as e:
    print(f"Ошибка импорта: {e}")