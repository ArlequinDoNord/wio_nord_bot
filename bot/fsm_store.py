"""Персистентное хранилище состояний FSM (v0.22.7).

Зачем оно нужно
---------------
По умолчанию aiogram кладёт состояния в память (``MemoryStorage``). Любой рестарт
бота — деплой, падение, перезапуск контейнера — обнулял их. Формы бота живут
ИМЕННО на состоянии: сдача отчёта (скриншот → суточная сумма → всего → регион),
передача предмета, ввод позывного, забег в подземелье. Поэтому игрок, который
на середине формы пережил рестарт, дальше не получал вообще ничего: состояние
исчезло, его сообщения не попадали ни в один хендлер формы, и бот выглядел
«зависшим». Такой отказ трудно отличить от настоящего зависания, и пилот
04.10 как раз жаловался на молчание — причина его случая не была доказана
(логи того дня не сохранились), но класс отказов этим хранилищем закрыт.

Почему свой класс, а не библиотечный
-----------------------------------
В aiogram 3.31 готовых хранилищ три: ``memory``, ``redis``, ``mongo``. Redis и
Mongo требуют отдельного сервера, а ботаняется одним контейнером. Файлового
хранилища в aiogram больше нет, поэтому здесь оно реализовано само — это ровно
четыре метода ``BaseStorage`` плюс ``close``.

Где лежат данные
----------------
Один JSON-файл на каталог (по умолчанию рядом с БД: в контейнере ``/app/data/fsm``,
это docker volume, который переживает пересоздание контейнера). Запись атомарная
через временный файл + ``os.replace``, поэтому оборванный деплой не оставляет
повреждённый JSON: при ошибке чтения состояние просто считается пустым.

Один экземпляр на файл
----------------------
Чтения кэшируются в памяти, а каждая запись перечитывает файл, поэтому два
экземпляра на одном файле не могут стереть записи друг друга. Но чтения у
второго экземпляра будут видеть устаревший кэш, поэтому экземпляр должен быть
один — его и создаёт ``Dispatcher`` в ``main.py``.

Почему JSON, а не pickle
------------------------
Данные FSM в этом боте — строки, числа и ``None``. JSON безопаснее и читаем
глазами. Значения неизвестных типов не роняют запись, а сохраняются через
``default=str`` с предупреждением в лог: лучше потерять одно поле, чем уронить
состояние целиком и снова получить «молчащий» бот.
"""
import asyncio
import json
import logging
import os
import time
from collections.abc import Mapping
from typing import Any

from aiogram.exceptions import DataNotDictLikeError
from aiogram.fsm.state import State
from aiogram.fsm.storage.base import BaseStorage, StateType, StorageKey

logger = logging.getLogger(__name__)

# Записи старше этого срока выбрасываются при старте: незакрытая форма не должна
# жить вечно. 14 суток заведомо больше любой формы (сдача отчёта, забег, ввод текста).
STALE_AFTER_SECONDS = 14 * 24 * 3600
# Защита от разрастания файла, если prune по времени не успел.
MAX_RECORDS = 5000


def _key_id(key: StorageKey) -> str:
    """Ключ хранилища -> стабильный id записи: 'bot_id:chat_id:user_id'.

    Именно атрибуты, а НЕ итерация по ключу: в aiogram 3 ``StorageKey`` — это
    frozen dataclass, а не кортеж-NamedTuple, поэтому ``":".join(str(p) for p in
    key)`` падает с ``TypeError: 'StorageKey' object is not iterable`` на каждом
    обращении к состоянию. ``thread_id`` и ``business_connection_id`` в id не
    входят — состояние пилота одно и то же в личке и в теме, как и у MemoryStorage.
    """
    return f"{key.bot_id}:{key.chat_id}:{key.user_id}"


class JsonFileStorage(BaseStorage):
    """FSM-хранилище в одном JSON-файле: состояния переживают рестарт бота."""

    def __init__(self, path: str) -> None:
        self._path = path
        self._lock = asyncio.Lock()
        self._cache: dict[str, dict[str, Any]] | None = None
        self._dirty = False

    # ── ввод-вывод ──────────────────────────────────────────────────────────
    def _read_sync(self) -> dict[str, dict[str, Any]]:
        if not os.path.isfile(self._path):
            return {}
        try:
            with open(self._path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            return data if isinstance(data, dict) else {}
        except (json.JSONDecodeError, OSError) as e:
            # Битый файл не должен ронять бота: состояние считаем пустым.
            logger.warning("FSM-хранилище %s не прочитано (%s), начинаем с чистого", self._path, e)
            return {}

    def _write_sync(self, data: dict[str, dict[str, Any]]) -> None:
        os.makedirs(os.path.dirname(self._path) or ".", exist_ok=True)
        tmp = f"{self._path}.tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, default=str)
        os.replace(tmp, self._path)

    async def _load(self) -> dict[str, dict[str, Any]]:
        """Кэш в памяти + одноразовая запись, чтобы не писать файл на каждое чтение."""
        if self._cache is None:
            self._cache = await asyncio.to_thread(self._read_sync)
            self._dirty = False
            await asyncio.to_thread(self._prune_sync, self._cache)
            self._dirty = True
        return self._cache

    def _prune_sync(self, data: dict[str, dict[str, Any]]) -> None:
        now = time.time()
        stale = [k for k, v in data.items() if now - float(v.get("_ts") or 0) > STALE_AFTER_SECONDS]
        for k in stale:
            data.pop(k, None)
        if len(data) > MAX_RECORDS:
            # Сначала самые старые записи.
            for k in sorted(data, key=lambda x: float(data[x].get("_ts") or 0))[
                :len(data) - MAX_RECORDS
            ]:
                data.pop(k, None)
        if stale:
            logger.info("FSM: вычищено устаревших записей — %d", len(stale))

    async def _apply(self, key: StorageKey, **changes: Any) -> None:
        """Изменить запись и записать файл.

        Файл перечитывается на КАЖДОЙ записи, а не берётся из кэша: иначе два
        экземпляра хранилища на одном файле затирали бы друг друга (кэш первого
        не знает о правке второго, и следующая запись первого затирала её целиком).
        В боте экземпляр один и чтения идут чаще записей, так что лишний
        read+write на шаг формы ничем не мешает.
        """
        async with self._lock:
            data = await asyncio.to_thread(self._read_sync)
            await asyncio.to_thread(self._prune_sync, data)
            rec = data.setdefault(_key_id(key), {"state": None, "data": {}})
            rec.update(changes)
            rec["_ts"] = time.time()
            await asyncio.to_thread(self._write_sync, data)
            self._cache = data
            self._dirty = False

    # ── BaseStorage ─────────────────────────────────────────────────────────
    async def close(self) -> None:
        """Нечего закрывать: каждая запись уходит в файл сразу, буфера нет."""
        return None

    async def set_state(self, key: StorageKey, state: StateType = None) -> None:
        value = state.state if isinstance(state, State) else state
        await self._apply(key, state=value)

    async def get_state(self, key: StorageKey) -> str | None:
        data = await self._load()
        rec = data.get(_key_id(key))
        return rec.get("state") if rec else None

    async def set_data(self, key: StorageKey, data: Mapping[str, Any]) -> None:
        if not isinstance(data, dict):
            msg = f"Data must be a dict or dict-like object, got {type(data).__name__}"
            raise DataNotDictLikeError(msg)
        try:
            json.dumps(dict(data))
        except (TypeError, ValueError):
            logger.warning("FSM: нестандартные значения в данных %s — сохраняю через str()", key)
        await self._apply(key, data=dict(data))

    async def get_data(self, key: StorageKey) -> dict[str, Any]:
        data = await self._load()
        rec = data.get(_key_id(key))
        return dict(rec.get("data") or {}) if rec else {}
