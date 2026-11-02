# -*- coding: utf-8 -*-
"""Общие помощники для smoke-тестов: счётчик проверок и фейковые aiogram-объекты.

Файл не начинается с smoke_ — раннер tools/run_smokes.py его не запускает как тест.
"""
import os
import sys


class Checker:
    """check(name, cond) печатает OK/FAIL и считает итог; summary() печатает ИТОГО."""

    def __init__(self):
        self.passed = 0
        self.failed = 0

    def __call__(self, name, cond):
        if cond:
            self.passed += 1
            print(f"  OK  {name}")
        else:
            self.failed += 1
            print(f"  FAIL {name}")

    def summary(self):
        print(f"\nИТОГО: {self.passed} passed, {self.failed} failed")
        return self.failed


def use_test_db(smoke_file, name):
    """Своя временная база на смоук: DATABASE_PATH до импорта database.db."""
    base = os.path.dirname(os.path.abspath(smoke_file))
    path = os.path.join(base, f"_test_{name}.db")
    os.environ["DATABASE_PATH"] = path
    if base not in sys.path:
        sys.path.insert(0, base)
    if os.path.exists(path):
        os.remove(path)
    return path


class FakeBot:
    last_text = None
    last_kb = None

    async def send_message(self, chat_id, text, **kw):
        FakeBot.last_text = text
        FakeBot.last_kb = kw.get("reply_markup")
        return type("M", (), {"message_id": 43,
                              "chat": type("C", (), {"id": chat_id})()})()

    async def send_photo(self, *a, **kw):
        FakeBot.last_text = kw.get("caption") or (a[1] if len(a) > 1 else "")
        FakeBot.last_kb = kw.get("reply_markup")
        return type("M", (), {"message_id": 44,
                              "chat": type("C", (), {"id": (a[0] or 0)})()})()

    async def delete_message(self, *a, **kw):
        return True

    async def edit_message_reply_markup(self, **kw):
        return True


class FakeMsg:
    def __init__(self, chat_id=0, message_id=42):
        self.text = None
        self.kb = None
        self.photo = None
        self.chat = type("C", (), {"id": chat_id})()
        self.message_id = message_id
        self.bot = FakeBot()

    async def edit_text(self, t=None, reply_markup=None, **kw):
        self.text = t
        self.kb = reply_markup
        return True

    async def answer(self, *a, **kw):
        if a and isinstance(a[0], str):
            self.text = a[0]
        if kw.get("reply_markup"):
            self.kb = kw["reply_markup"]
        return True


class FakeCB:
    def __init__(self, uid, data, chat_id=None):
        self.from_user = type("U", (), {"id": uid})()
        self.data = data
        self.message = FakeMsg(uid if chat_id is None else chat_id)
        self.bot = FakeBot()

    async def answer(self, *a, **kw):
        return True
