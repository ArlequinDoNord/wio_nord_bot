"""Smoke v0.22.7: регрессии по жалобам пилотов от 04–05.10.2026.

Каждый пункт — реальная поломка, из-за которой пилот упирался в «молчащий бот»:

  1. Трость КВП отдавалась другому игроку (рынок закрыт, а передача — нет).
  2. Перевод денег: список получателей обрывался на первых 50 игроках, поэтому
     новички (и игроки без позывного) были недоступны для перевода.
  3. Водохранилище стоило 3 ОД — столько же, как озеро, при улове в разы дороже.
  4. КВП: UnboundLocalError по crit_mark, когда враг уклонялся. Пилот нажимал
     «Атаковать» и не получал НИЧЕГО — экран боя не доходил.
  5. profile.py звал state.finish(), которого нет в aiogram 3: AttributeError.
  6. Сдача отчёта перетирала состояние подземелья/заброса (Виктория).
  7. FSM жила в памяти: рестарт обнулял незаконченные формы (отчёт Никиты).
  8. Глобальный обработчик ошибок не сообщал игроку ничего.

Запуск: .venv\\Scripts\\python.exe smoke_128.py
"""
import asyncio
import inspect
import json
import os
import shutil
import sys
import tempfile
import types

WORK = tempfile.mkdtemp(prefix="sm128_")
os.environ["DATABASE_PATH"] = os.path.join(WORK, "t.db")
os.environ["FSM_STORAGE_PATH"] = os.path.join(WORK, "fsm")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

from database import db as D
from database.db import KVP_CANE_NAME, UNTRANSFERABLE_ITEMS
from bot.handlers import inventory as INV
from bot.handlers import bank as BANK
from bot.handlers import dungeon as DUN
from bot.handlers import kvp as KVP
from bot.handlers import reports as REP
from bot.handlers import profile as PROF
from bot.fsm_store import JsonFileStorage

FAILED = []


def check(name, cond, extra=""):
    print(("  ok   " if cond else "  FAIL ") + name + (f"   [{extra}]" if extra else ""))
    if not cond:
        FAILED.append(name)


def buttons_text(markup):
    return [b.text for row in markup.inline_keyboard for b in row]


def callbacks(markup):
    return [b.callback_data or "" for row in markup.inline_keyboard for b in row]


class FakeMsg:
    """Минимальный Message: хендлерам нужны text, photo и answer()."""

    def __init__(self, uid, text=None, photo=None):
        self.text = text
        self.photo = photo
        self.media_group_id = None
        self.from_user = types.SimpleNamespace(id=uid, first_name="Тест", username="tester")
        self.answers = []
        self.last_markup = None

    async def answer(self, text, reply_markup=None, **kw):
        self.answers.append(text)
        self.last_markup = reply_markup

    async def answer_photo(self, *a, **kw):
        self.answers.append("[photo]")

    @property
    def last(self):
        return self.answers[-1] if self.answers else ""


class FakeCallback:
    def __init__(self, uid, data):
        self.data = data
        self.from_user = types.SimpleNamespace(id=uid, first_name="Тест", username="tester")
        self.message = FakeMsg(uid)

    async def answer(self, text=None, show_alert=False, **kw):
        pass


async def main():
    await D.init_db()
    await D.seed_kvp()
    await D.ensure_kvp_items()

    cane = await D.get_item_by_name(KVP_CANE_NAME)
    cane_id = cane["id"]

    # ── 1. Трость КВП не передаётся ──────────────────────────────────────────
    print("\n1. Трость КВП не передаётся игроку")
    check("трость в UNTRANSFERABLE_ITEMS", KVP_CANE_NAME in UNTRANSFERABLE_ITEMS)
    check("обычный лут передаётся как раньше",
          not ({"Клык дикого кабана", "Жемчужина"} & UNTRANSFERABLE_ITEMS))

    # Разметку собираем так же, как в проде: флаг считается по названию предмета.
    m_cane = INV.inv_item_markup(cane_id, "weapon", sellable=True, qty=1, market_ok=False,
                                 transferable=KVP_CANE_NAME not in UNTRANSFERABLE_ITEMS)
    check("кнопки «Передать» нет", "📤 Передать" not in buttons_text(m_cane))
    check("продажа скупщику осталась", "💵 Продать" in buttons_text(m_cane))
    check("рынок закрыт", "🏪 На рынок" not in buttons_text(m_cane))
    check("в callback_data нет inv_transfer",
          not any("inv_transfer" in c for c in callbacks(m_cane)))

    # Продовая точка вызова обязана сама передавать флаг — иначе кнопка вернётся.
    inv_src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "bot", "handlers", "inventory.py"), encoding="utf-8").read()
    check("продовая точка вызова передаёт transferable",
          "transferable=item['name'] not in UNTRANSFERABLE_ITEMS" in inv_src)

    m_norm = INV.inv_item_markup(999, "weapon", sellable=True, qty=1, market_ok=False)
    check("у обычного предмета «Передать» осталась", "📤 Передать" in buttons_text(m_norm))

    await D.add_user(1, "caneuser", "Владелец", "")
    await D.add_inventory_item(1, cane_id, 1)
    st = FSMContext(MemoryStorage(), key=("t", 1))
    cb = FakeCallback(1, f"inv_transfer:{cane_id}")
    await INV.inv_transfer_start(cb, st)
    check("inv_transfer_start отказывает", "нельзя передать" in cb.message.last)
    check("состояние передачи не выставлено", await st.get_state() is None)

    # Устаревшее состояние FSM (кнопка нажата до деплоя) — тоже отказ, вещь не списана.
    from bot.handlers.inventory import TransferItem
    st2 = FSMContext(MemoryStorage(), key=("t", 1))
    await st2.set_state(TransferItem.message)
    await st2.update_data(item_id=cane_id, item_name=KVP_CANE_NAME, amount=1, target_id=2)
    m2 = FakeMsg(1, text="ок")
    await INV.inv_transfer_message(m2, st2)
    check("inv_transfer_message отказывает", "нельзя передать" in m2.last)
    left = await D.get_inventory_item(1, cane_id)
    check("трость у игрока осталась", bool(left) and left["quantity"] == 1)

    # ── 2. Перевод денег: список больше не обрезан на 50 ─────────────────────
    print("\n2. Перевод денег: доступны все получатели")
    check("задана пагинация получателей", BANK.RECIPIENTS_PER_PAGE > 0)
    await D.add_user(100, "payer", "Плательщик", "")
    for i in range(2, 72):
        await D.add_user(i, f"user{i}", f"Пилот{i:02d}", "")

    seen = set()
    pages = 0
    page = 0
    while pages < 30:
        cb = FakeCallback(100, f"bank:transfer:list:{page}")
        await BANK._recipient_page(cb, page)
        mk = cb.message.last_markup
        if mk is None:
            check("разметка списка получена", False)
            break
        seen.update(c for c in callbacks(mk) if c.startswith("bank:pickrecipient:"))
        pages += 1
        if f"bank:transfer:list:{page + 1}" not in callbacks(mk):
            break
        page += 1

    check("список разбит на страницы", pages > 1)
    check("доступно больше 50 получателей", len(seen) >= 69)
    check("доступен игрок за 50-м местом (id=68)", "bank:pickrecipient:68" in seen)
    check("доступен игрок без позывного", "bank:pickrecipient:68" in seen)
    check("себя в списке нет", "bank:pickrecipient:100" not in seen)
    check("есть ручной ввод username", "bank:transfer_manual" in callbacks(mk))

    # ── 3. Водохранилище дороже озера ───────────────────────────────────────
    print("\n3. Стоимость заброса в водохранилище")
    from config import FISH_AP_COST, RESERVOIR_AP_COST
    check("в config задана стоимость", RESERVOIR_AP_COST in (4, 5))
    check("водохранилище дороже озера", RESERVOIR_AP_COST > FISH_AP_COST)
    check("dungeon берёт цену из config", DUN.RESERVOIR_AP_COST == RESERVOIR_AP_COST)
    check("кнопка показывает новую цену",
          f"(−{RESERVOIR_AP_COST} ОД)" in buttons_text(DUN.reservoir_keyboard())[0])

    # ── 4. КВП: crit_mark определён всегда ──────────────────────────────────
    print("\n4. КВП: уклонение врага больше не роняет бой")
    src = inspect.getsource(KVP.kvp_attack)
    check("crit_mark присваивается и в ветке уклонения", 'crit_mark = ""' in src)
    check("значение crit_mark используется после присваивания",
          src.index("crit_mark = \"\"") < src.index("{crit_mark}"))

    # ── 5. profile.py больше не зовёт state.finish() ────────────────────────
    print("\n5. profile.py: state.finish()")
    # Ищем именно вызов в AST: в комментариях это слово тоже встречается.
    import ast
    prof_tree = ast.parse(inspect.getsource(PROF))
    calls_finish = [n.attr for n in ast.walk(prof_tree)
                    if isinstance(n, ast.Attribute) and n.attr == "finish"]
    check("вызова .finish() нет", not calls_finish)
    prof_src = inspect.getsource(PROF)
    check("состояние снимается через clear()", ".clear()" in prof_src)

    # ── 6. Сдача отчёта не ломает подземелье и заброс ───────────────────────
    print("\n6. Сдача отчёта во время подземелья/заброса")
    from bot.handlers.dungeon import DungeonFSM
    from bot.handlers.fishing import FISHING_CASTING
    await D.add_user(2, "victoria", "Виктория", "")
    for s in (DungeonFSM.in_dungeon, DungeonFSM.in_combat,
              DungeonFSM.in_boss, DungeonFSM.in_reservoir):
        name = s.state.split(":")[-1]
        stv = FSMContext(MemoryStorage(), key=("t", 2))
        await stv.set_state(s)
        cb = FakeCallback(2, "report:submit")
        await REP.report_submit_start(cb, stv)
        check(f"отчёт не начинается в состоянии {name}",
              "подземель" in cb.message.last.lower())
        check(f"состояние {name} не перетёрто", await stv.get_state() == s.state)

    FISHING_CASTING.add(2)
    stf = FSMContext(MemoryStorage(), key=("t", 2))
    cbf = FakeCallback(2, "report:submit")
    await REP.report_submit_start(cbf, stf)
    check("отчёт не начинается во время заброса", "заброс" in cbf.message.last.lower())
    check("состояние не выставлено во время заброса", await stf.get_state() is None)
    FISHING_CASTING.discard(2)

    # ── 7. FSM переживает рестарт ───────────────────────────────────────────
    print("\n7. Персистентность FSM")
    path = os.path.join(WORK, "fsm2", "fsm_state.json")
    # Именно настоящий StorageKey, а не плейсхолдер-кортеж: StorageKey в aiogram 3
    # это frozen dataclass, и итерация по нему падает. Настоящий ключ ловит это.
    from aiogram.fsm.storage.base import StorageKey
    key = StorageKey(bot_id=42, chat_id=42, user_id=555)
    check("StorageKey — dataclass, не кортеж", not isinstance(key, tuple),
          f"{type(key).__name__}")
    from bot.handlers.reports import ReportSubmit
    st_a = FSMContext(JsonFileStorage(path), key=key)
    await st_a.set_state(ReportSubmit.waiting_total_troops)
    await st_a.update_data(daily_troops=111)
    st_b = FSMContext(JsonFileStorage(path), key=key)  # «новый процесс»
    check("состояние пережило рестарт",
          (await st_b.get_state()) == ReportSubmit.waiting_total_troops.state)
    check("данные формы пережили рестарт",
          (await st_b.get_data()).get("daily_troops") == 111)

    # Один экземпляр на файл — как в проде (его создаёт Dispatcher): состояния
    # разных пилотов не сливаются, clear() не задевает соседей.
    shared = JsonFileStorage(path)
    k1 = StorageKey(bot_id=1, chat_id=1, user_id=2)
    k2 = StorageKey(bot_id=1, chat_id=1, user_id=3)
    k3 = StorageKey(bot_id=1, chat_id=1, user_id=4)
    st_1 = FSMContext(shared, key=k1)
    st_2 = FSMContext(shared, key=k2)
    await st_1.set_state("S:one")
    await st_1.update_data(v="один")
    await st_2.set_state("S:two")
    await st_2.update_data(v="два")
    check("состояние пилота 1 не затирается пилотом 2",
          (await st_1.get_state()) == "S:one" and (await st_1.get_data())["v"] == "один",
          f"{(await st_1.get_state())} {(await st_1.get_data())}")
    check("состояние пилота 2 отдельно",
          (await st_2.get_state()) == "S:two" and (await st_2.get_data())["v"] == "два")
    await st_1.clear()
    check("clear() убирает состояние и данные",
          (await st_1.get_state()) is None and (await st_1.get_data()) == {},
          f"{(await st_1.get_state())} {(await st_1.get_data())}")
    check("соседний пилот не пострадал от clear()",
          (await st_2.get_state()) == "S:two", f"={(await st_2.get_state())}")

    # Второй экземпляр на том же файле не должен УДАЛЯТЬ чужие записи при записи.
    other = JsonFileStorage(path)
    st_3 = FSMContext(other, key=k3)
    await st_3.set_state("S:three")
    raw = json.load(open(path, encoding="utf-8"))
    check("запись второго экземпляра не стирает записи первого",
          "1:1:2" in raw and "1:1:3" in raw and "42:42:555" in raw, f"{sorted(raw.keys())}")
    check("в файле ключ записан как bot:chat:user", "1:1:4" in raw, f"{sorted(raw.keys())}")

    import config
    check("FSM_STORAGE_PATH берётся из окружения",
          config.FSM_STORAGE_PATH == os.path.join(WORK, "fsm"))

    # ── 8. Ошибку видно и игрок ─────────────────────────────────────────────
    print("\n8. Ошибки больше не молчат")
    root = os.path.dirname(os.path.abspath(__file__))
    main_src = open(os.path.join(root, "main.py"), encoding="utf-8").read()
    check("обработчик ошибок отвечает игроку", "Что-то пошло не так" in main_src)
    check("Dispatcher получает файловое хранилище", "JsonFileStorage" in main_src)

    conn = await D.get_db()
    await conn.close()
    shutil.rmtree(WORK, ignore_errors=True)
    print("\n" + ("ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ" if not FAILED else f"ПРОВАЛЕНО ({len(FAILED)}): {FAILED}"))
    sys.exit(1 if FAILED else 0)


asyncio.run(main())
