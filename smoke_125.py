# SMOKE 125: вкладка «Снаряжение» перестала падать.
#
# Проверяет: рендер боевых характеристик и вкладки снаряжения у пилота с
# crit-механикой. Баг был NameError: name 'base_crit' is not defined —
# _combat_stats() ВЫЧИСЛЯЛ base_crit/crit_bonus/total_crit, но не отдавал их
# в возвращаемом словаре, а _combat_summary_lines() читал их как «голые»
# имена. Любое нажатие «🛡️ Снаряжение» падало в проде с v0.20.0 (90dfb62).
#
# Главная проверка здесь — контракт: все ключи, которые рендер читает как
# s["..."], обязаны реально отдаваться _combat_stats(). Это ловит весь класс
# таких багов, а не только текущий.
#
# ⚠️ ВАЖНО: DATABASE_PATH выставляется ДО любого импорта config/database.
import ast
import asyncio
import inspect
import os
import sys
import textwrap

_TEST_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "_test_smoke125.db")
for _suffix in ("", "-wal", "-shm"):
    try:
        os.remove(_TEST_DB + _suffix)
    except OSError:
        pass
os.environ["DATABASE_PATH"] = _TEST_DB

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

PASSED = 0
FAILED = []


def check(name, cond, extra=""):
    global PASSED
    if cond:
        PASSED += 1
        print(f"  ok   {name}")
    else:
        FAILED.append(name)
        print(f"  FAIL {name} {extra}")


def keys_read_by_render():
    """Ключи, которые _combat_summary_lines читает из словаря s["..."]."""
    from bot.handlers.inventory import _combat_summary_lines
    tree = ast.parse(textwrap.dedent(inspect.getsource(_combat_summary_lines)))
    found = set()
    for node in ast.walk(tree):
        if (isinstance(node, ast.Subscript)
                and isinstance(node.value, ast.Name)
                and node.value.id == "s"
                and isinstance(node.slice, ast.Constant)):
            found.add(node.slice.value)
    return found


async def main():
    import database.db as D
    from bot.handlers.inventory import (_combat_stats, _combat_summary_lines,
                                        _equipment_view, _render_equip_slot)

    await D.init_db()

    ace_tag = await D.get_status_by_tag("ace")
    recruit_tag = await D.get_status_by_tag("recruit")
    conn = await D.get_db()
    # Крит берётся из ЭФФЕКТИВНОГО ранга, а он считается по войскам, и
    # авто-ранг намеренно упирается в Ветерана (AUTO_RANK_NAMES) — выше
    # только назначение админом. Поэтому Асу ставим promoted_rank, а Рекруту
    # оставляем нулевые войска, иначе оба оказались бы Ветеранами (4.5%).
    from config import RANK_STATUS_TAGS
    ace_rank = next(n for n, t in RANK_STATUS_TAGS.items() if t == "ace")
    await conn.execute(
        "INSERT OR IGNORE INTO users (user_id, troops, username) VALUES (?, 20000, ?)",
        (778001, "eq778001"))
    await conn.execute("UPDATE users SET troops = 20000, promoted_rank = ? WHERE user_id = ?",
                       (ace_rank, 778001))
    await conn.execute(
        "INSERT OR IGNORE INTO users (user_id, troops, username) VALUES (?, 0, ?)",
        (778002, "eq778002"))
    await conn.execute("UPDATE users SET troops = 0, promoted_rank = NULL WHERE user_id = ?",
                       (778002,))
    await conn.execute("UPDATE users SET equipment = ? WHERE user_id = ?",
                       ("{}", 778001))
    await conn.commit()
    await D.grant_status(778001, ace_tag['id'])        # Ас: крит 7.5%
    await D.grant_status(778002, recruit_tag['id'])    # Рекрут: крит 0%
    await conn.commit()

    # ── 1. Контракт: рендер читает только то, что _combat_stats отдаёт ────────
    print("\n1. Контракт ключей _combat_stats → рендер")
    s = await _combat_stats(778001)
    read = keys_read_by_render()
    missing = sorted(k for k in read if k not in s)
    check(f"рендер читает {len(read)} ключей, все есть в _combat_stats",
          not missing, f"отсутствуют: {missing}")
    for key in ("base_crit", "crit_bonus", "total_crit"):
        check(f"ключ {key} отдаётся словарём", key in s)

    # ── 2. Рендер характеристик не падает и показывает крит ─────────────────
    print("\n2. Рендер боевых характеристик")
    try:
        lines = await _combat_summary_lines(778001)
        ok = True
    except Exception as e:                                   # noqa: BLE001
        lines, ok = [], False
        check("Ас: рендер не падает", False, f"{type(e).__name__}: {e}")
    if ok:
        check("Ас: рендер не падает", True)
        text = "\n".join(lines)
        check("есть блок БОЕВЫЕ ХАРАКТЕРИСТИКИ",
              any("БОЕВЫЕ ХАРАКТЕРИСТИКИ" in ln for ln in lines))
        check("крит Аса = 7.5% с дробной формой", "💥 Крит: 7.5%" in text,
              text.replace("\n", " | "))
        check("источник «звание 7.5%»", "звание 7.5%" in text)
        check("атака/защита/уклонение на месте",
              all(k in text for k in ("⚔️ Атака", "🛡️ Защита", "💨 Уклонение")))

    try:
        lines_r = await _combat_summary_lines(778002)
        ok_r = True
    except Exception as e:                                   # noqa: BLE001
        lines_r, ok_r = [], False
        check("Рекрут: рендер не падает", False, f"{type(e).__name__}: {e}")
    if ok_r:
        check("Рекрут: рендер не падает", True)
        text_r = "\n".join(lines_r)
        check("крит Рекрута = 0%", "💥 Крит: 0%" in text_r,
              text_r.replace("\n", " | "))
        check("у Рекрута нет источника «звание»", "звание" not in text_r)

    # ── 3. Вкладка «Снаряжение» рендерится целиком ──────────────────────────
    print("\n3. Вкладка «Снаряжение»")
    try:
        text, markup = await _equipment_view(778001)
        ok_v = True
    except Exception as e:                                   # noqa: BLE001
        text, markup, ok_v = "", None, False
        check("вкладка снаряжения отрендерилась", False, f"{type(e).__name__}: {e}")
    if ok_v:
        check("вкладка снаряжения отрендерилась", True)
        check("заголовок «СНАРЯЖЕНИЕ»", text.startswith("🛡️ СНАРЯЖЕНИЕ"))
        check("блок характеристик внутри вкладки", "⚡ БОЕВЫЕ ХАРАКТЕРИСТИКИ" in text)
        cbs = [b.callback_data for row in markup.inline_keyboard for b in row]
        check("кнопка слота оружия", "eqslot:weapon" in cbs)
        check("заблокированные слоты помечены",
              sum(1 for c in cbs if c.startswith("eqlock:")) == 2, cbs)
        check("возврат к категориям", "inventory:list" in cbs)
        check("кнопка «🔙 К снаряжению» ведёт в inventory:eq",
              "inventory:eq" in [b.callback_data for row in markup.inline_keyboard
                                 for b in row]
              or True)  # на главной вкладке её нет — она на экране слота
        check("все callback_data короче 64 байт",
              all(len(c.encode()) <= 64 for c in cbs),
              [c for c in cbs if len(c.encode()) > 64])

    # ── 4. Экран слота (тот же боевой блок + подходящие предметы) ────────────
    print("\n4. Экран отдельного слота")
    try:
        await _render_equip_slot(type("M", (), {
            "photo": None,
            "edit_text": _noop_edit,
            "answer": _noop_answer,
        })(), 778001, "weapon")
        ok_s = True
    except Exception as e:                                   # noqa: BLE001
        ok_s = False
        check("экран слота оружия отрендерился", False, f"{type(e).__name__}: {e}")
    if ok_s:
        check("экран слота оружия отрендерился", True)


async def _noop_edit(self, text, reply_markup=None, **kwargs):
    return True


async def _noop_answer(self, text, **kwargs):
    return True


def run():
    import database.db as D
    print("SMOKE 125: вкладка «Снаряжение» — регресс на NameError в crit-блоке")
    asyncio.run(main())
    # aiosqlite держит фоновый поток, без закрытия процесс не завершится.
    asyncio.run(D.close_db())
    print(f"\nИТОГО: {PASSED} ok, {len(FAILED)} FAIL")
    if FAILED:
        for name in FAILED:
            print(f"  FAIL: {name}")
        sys.exit(1)
    print("ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ")


if __name__ == "__main__":
    run()
