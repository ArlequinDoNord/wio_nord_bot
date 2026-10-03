# SMOKE 121: позывной — бесплатная первая установка, платная смена, админка
#
# Регресс: кнопка позывного не нажималась (в profile.py не было импорта
# InlineKeyboardMarkup/InlineKeyboardButton), а хендлер использовал
# ProfileStates.waiting_callsign.set() без инъекции state. Плюс callback_data
# "profile" (кнопка «Отмена») вообще не имел обработчика.
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import CALLSIGN_PRICE

PASSED = 0
FAILED = 0


def check(name, cond, extra=""):
    global PASSED, FAILED
    if cond:
        PASSED += 1
        print(f"  OK  {name}{(' — ' + extra) if extra else ''}")
    else:
        FAILED += 1
        print(f"  FAIL  {name}{(' — ' + extra) if extra else ''}")


def src_of(rel):
    return open(os.path.join(os.path.dirname(__file__), rel), encoding="utf-8").read()


def main():
    prof = src_of("bot/handlers/profile.py")
    kbd = src_of("keyboards/keyboards.py")
    adm = src_of("bot/handlers/admin.py")

    # ── 1. Кнопка позывного вернулась в профиль ──
    check("кнопка позывного не закомментирована",
          "callsign_text" in kbd and 'callback_data="profile:callsign"' in kbd)
    check("кнопка не помечена как временно убранная",
          "временно убран" not in kbd and "Позывной: временно" not in kbd)
    check("текст кнопки зависит от наличия позывного",
          "Сменить позывной" in kbd and "Установить позывной" in kbd)

    # ── 2. Импорт aiogram-типов на уровне модуля (причина прошлой поломки) ──
    head = prof.split("router = Router()")[0]
    check("InlineKeyboardMarkup импортирован в profile.py",
          "InlineKeyboardMarkup" in head)
    check("InlineKeyboardButton импортирован в profile.py",
          "InlineKeyboardButton" in head)

    # ── 3. Состояние выставляется через инъекцию state, а не глобально ──
    check("profile_callsign принимает state: FSMContext",
          "async def profile_callsign(callback: CallbackQuery, state: FSMContext)" in prof)
    check("нет вызова State.set() без инъекции",
          "ProfileStates.waiting_callsign.set()" not in prof)
    check("используется state.set_state(ProfileStates.waiting_callsign)",
          prof.count("await state.set_state(ProfileStates.waiting_callsign)") >= 2)

    # ── 4. Кнопка «Отмена» (callback_data="profile") обрабатывается ──
    check("есть хендлер на profile", 'F.data == "profile"' in prof)
    check("хендлер сбрасывает состояние", "profile_back" in prof)
    check("хендлер возвращает в профиль",
          "render_profile(callback.message, callback.from_user.id)" in prof)

    # ── 5. Платная смена требует состояния ввода ──
    check("оплата выставляет waiting_callsign",
          "await state.set_state(ProfileStates.waiting_callsign)" in prof)
    check("после оплаты позывной сбрасывается для замены",
          "await set_callsign(user_id, None)" in prof)
    check("цена берётся из конфига", "CALLSIGN_PRICE" in prof)

    # ── 6. Правила бесплатной установки ──
    check("бесплатная установка только при callsign_free_used = 0",
          "if not has_callsign and not free_used:" in prof)
    check("бесплатная установка помечается использованной",
          "await set_callsign_free_used(user_id, 1)" in prof)
    check("суперадмин меняет бесплатно", "if super_admin:" in prof)
    check("ввод без оплаты отклоняется для не-суперадмина",
          "Бесплатная установка уже использована" in prof)

    # ── 7. Валидация ввода ──
    check("проверка длины до 32", "len(callsign) > 32" in prof)
    check("проверка минимума 2 символа", "len(callsign) < 2" in prof)

    # ── 8. Цена = 500 ──
    check("CALLSIGN_PRICE = 500", CALLSIGN_PRICE == 500)
    check("цена не захардкожена в profile.py", "price = 500" not in prof)

    # ── 9. Админ может ставить/менять позывной любому ──
    check("кнопка админки есть", 'callback_data="admin:callsign"' in kbd)
    check("админ выбирает пилота", 'pilot_picker_markup("callsign")' in adm)
    check("админское состояние ввода", "AdminCallsign.value" in adm)
    check("админ может убрать позывной", 'text in ("", "-")' in adm)
    check("админское действие логируется", "'set_callsign'" in adm)

    # ── 10. Позывной виден в карточке пилота ──
    check("позывной в карточке", "Позывной:" in prof)

    # ── 11. pyflakes: нет undefined name в изменённых файлах ──
    import subprocess
    for rel in ("bot/handlers/profile.py", "bot/handlers/admin.py",
                "database/db.py", "config.py"):
        r = subprocess.run([sys.executable, "-m", "pyflakes", rel],
                           capture_output=True, text=True,
                           cwd=os.path.dirname(os.path.abspath(__file__)))
        bad = [ln for ln in r.stdout.splitlines() if "undefined name" in ln]
        check(f"{rel}: нет undefined name", not bad)

    # ── 12. Кабану поднято HP до 40 ──
    from config import FOREST_BOAR_HP
    check("FOREST_BOAR_HP = 40", FOREST_BOAR_HP == 40)
    dbsrc = src_of("database/db.py")
    check("миграция поднимает HP кабана", "FOREST_BOAR_HP, FOREST_BOAR_HP" in dbsrc)
    check("миграция уважает admin_tuned", "admin_tuned = 0" in dbsrc)

    print(f"\n=== SMOKE 121: {PASSED} passed, {FAILED} failed ===")
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())