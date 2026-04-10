"""
Утилиты для форматирования текста в боте
"""


def create_progress_bar(percent, length=10):
    """
    Создать визуальный прогресс-бар

    Args:
        percent: Процент заполнения (0-100)
        length: Длина полоски в символах

    Returns:
        str: Прогресс-бар вида '██████░░░░'
    """
    # Ограничиваем процент от 0 до 100
    percent = max(0, min(100, percent))

    # Рассчитываем количество заполненных символов
    filled = int(percent / 100 * length)
    empty = length - filled

    # Создаем полоску
    return '█' * filled + '░' * empty


def format_number(number):
    """
    Форматировать число с разделителями

    Args:
        number: Число для форматирования

    Returns:
        str: Отформатированное число (например: 1 234 567)
    """
    if number is None:
        return "0"

    # Форматируем с пробелами как разделителями тысяч
    return f"{number:,}".replace(',', ' ')


def get_rank_emoji(rank):
    """
    Получить эмодзи для ранга

    Args:
        rank: Название ранга

    Returns:
        str: Эмодзи соответствующее рангу
    """
    rank_emojis = {
        'Рядовой': '🔰',
        'Капрал': '⭐',
        'Сержант': '⭐⭐',
        'Лейтенант': '⭐⭐⭐',
        'Капитан': '📯',
        'Майор': '🎖️',
        'Подполковник': '🎖️🎖️',
        'Полковник': '🎖️🎖️🎖️',
        'Генерал-майор': '🏅',
        'Генерал-лейтенант': '🏅🏅',
        'Генерал': '🏅🏅🏅'
    }
    return rank_emojis.get(rank, '👤')


def format_time(seconds):
    """
    Форматировать время в секундах в читаемый вид

    Args:
        seconds: Количество секунд

    Returns:
        str: Отформатированное время (например: "1 час 30 минут")
    """
    if seconds < 60:
        return f"{seconds} сек"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} мин"
    elif seconds < 86400:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        if minutes > 0:
            return f"{hours} ч {minutes} мин"
        return f"{hours} ч"
    else:
        days = seconds // 86400
        return f"{days} дн"


def truncate_text(text, max_length=50):
    """
    Обрезать текст до определенной длины и добавить многоточие

    Args:
        text: Исходный текст
        max_length: Максимальная длина

    Returns:
        str: Обрезанный текст
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."