# -*- coding: utf-8 -*-
"""Smoke 198 — после картинки предмета в «Хранилище» есть кнопки возврата:
к товарам его категории, к самому товару, к списку категорий."""
import os
import sys

os.environ["DATABASE_PATH"] = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "_test_smoke198.db")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    from bot.handlers.admin import _after_photo_markup
    from config import ITEM_CATEGORIES
    kb = _after_photo_markup(42, "consumable")
    cbs = [b.callback_data for row in kb.inline_keyboard for b in row]
    labels = [b.text for row in kb.inline_keyboard for b in row]
    checks = [
        ("кнопка к товарам категории", "storage:cat:consumable:page:0" in cbs),
        ("кнопка к самому товару", "storage:item:42" in cbs),
        ("кнопка к категориям", "storage:cats" in cbs),
        ("подпись содержит название категории",
         any(t == f"📦 К товарам: {ITEM_CATEGORIES['consumable']}" for t in labels)),
    ]
    failed = 0
    for name, ok in checks:
        print(("  OK  " if ok else "  FAIL ") + name)
        failed += 0 if ok else 1
    print(f"ИТОГО: {len(checks) - failed} passed, {failed} failed")
    return failed


if __name__ == "__main__":
    sys.exit(main())
