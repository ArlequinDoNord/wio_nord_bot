"""Паспорт Нордхайма: проверки ввода главы КГБ и текст карточки.

Логика выдачи и хранения — в database/db.py (issue_passport, get_passport).
Здесь только то, что нужно и менеджеру, и профилю/инвентарю.
"""
import re
from datetime import datetime, timedelta, timezone

from utils.localization import t

MAX_TEXT_LEN = 64
DATE_FORMAT = "%d.%m.%Y"
SEX_VALUES = ("m", "f")


def validate_series(raw: str):
    value = (raw or "").strip()
    if re.fullmatch(r"\d{4}", value):
        return value, None
    return None, "kgb.bad_series"


def validate_number(raw: str):
    value = (raw or "").strip()
    if re.fullmatch(r"\d{6}", value):
        return value, None
    return None, "kgb.bad_number"


def validate_text(raw: str):
    value = (raw or "").strip()
    if not value or len(value) > MAX_TEXT_LEN:
        return None, "kgb.bad_text"
    return value, None


def validate_marks(raw: str):
    value = (raw or "").strip()
    if not value:
        return None, "kgb.bad_text"
    if len(value) > 200:
        return None, "kgb.bad_text"
    return value, None


def parse_date(raw: str, now: datetime = None):
    """Дата в формате ДД.ММ.ГГГГ; «сегодня» — текущая дата по Москве.

    Возвращает (строка ДД.ММ.ГГГГ, None) или (None, ключ ошибки).
    """
    value = (raw or "").strip().lower()
    if value in ("сегодня", "today"):
        moscow = (now or datetime.now(timezone.utc)) + timedelta(hours=3)
        return moscow.strftime(DATE_FORMAT), None
    if not re.fullmatch(r"\d{2}\.\d{2}\.\d{4}", value):
        return None, "kgb.bad_date"
    try:
        parsed = datetime.strptime(value, DATE_FORMAT)
    except ValueError:
        return None, "kgb.bad_date"
    if parsed.year < 1900:
        return None, "kgb.bad_date"
    return parsed.strftime(DATE_FORMAT), None


def sex_label(sex: str) -> str:
    return t("kgb.sex_m") if sex == "m" else t("kgb.sex_f")


def format_passport(p) -> str:
    """Текст карточки паспорта. p — строка из passports (или dict с теми же полями)."""
    keys = p.keys() if hasattr(p, "keys") else ()

    def field(name):
        return (p[name] if name in keys else "") or "—"

    lines = [
        t("kgb.card_title"),
        "────────────────",
        f"{t('kgb.f_series')}: {field('series')}",
        f"{t('kgb.f_number')}: {field('number')}",
        f"{t('kgb.f_name')}: {field('full_name')}",
        f"{t('kgb.f_position')}: {field('position')}",
        f"{t('kgb.f_rank')}: {field('rank')}",
        f"{t('kgb.f_sex')}: {sex_label(field('sex')) if field('sex') != '—' else '—'}",
        f"{t('kgb.f_marital')}: {field('marital_status')}",
        f"{t('kgb.f_birth')}: {field('birth_date')}",
        f"{t('kgb.f_issue')}: {field('issue_date')}",
        f"{t('kgb.f_marks')}: {field('distinguishing_marks')}",
    ]
    return "\n".join(lines)
