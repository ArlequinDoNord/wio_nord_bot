"""Smoke v0.15.14: новости (длинные фото-выпуски), снежинка спец отряда, долги казны.

Проверяет:
1. Новости: add_news/get_news с длинным текстом (2000+) и фото; текст хранится
   целиком; в news_view присутствует защита от «caption is too long» (long_text
   и лимит 3900 для текстовых выпусков).
2. Эмодзи спец отряда: WINGS/WINGS_SHORT ключа '4' содержат ❄️ (снежинку).
3. Казна: get_treasury_debts по пустой казне, после назначения зарплаты и
   накопления долга (add_salary_debt), прогноз на следующую выплату,
   clear_salary_debt обнуляет долг.

Запуск: .venv\\Scripts\\python.exe smoke_076.py
"""
import asyncio
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

_TEST_DB = os.path.join(os.path.dirname(__file__), "_test_smoke076.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB

sys.path.insert(0, os.path.dirname(__file__))


async def run():
    from database.db import (
        init_db, close_db, add_user, add_news, get_news,
        get_treasury_balance, get_treasury_debts,
        set_user_salary, add_salary_debt, clear_salary_debt, get_salaried_users,
        pay_salaries,
    )
    from utils.wings import wing_label, wing_display, WINGS_SHORT, WINGS

    await init_db()

    passed = 0
    failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
        else:
            failed += 1
            print(f"  FAIL: {name}")

    U1, U2 = 752001, 752002
    for uid, name in ((U1, "Т1-пилот"), (U2, "Т2-пилот")):
        await add_user(uid, f"u{uid}", name, "")

    # ── 1. Новости: длинные выпуски хранятся целиком ──
    long_body = "Сегодня в Нордхайме объявили о новых реформах. " * 60  # ~2450 символов
    nid = await add_news("Реформа казны", long_body, U1, "Т1-пилот",
                         photo_file_id="FOTO_LONG")
    n1 = await get_news(nid)
    check("add_news/get_news: длинный выпуск с фото", n1 is not None
          and n1['body'] == long_body and n1['photo_file_id'] == "FOTO_LONG")
    check("новость длиннее лимита caption (1024)",
          len(long_body) + 60 > 1024)

    nid2 = await add_news("Короткий выпуск", "Пара слов.", U2, "Т2-пилот", None)
    n2 = await get_news(nid2)
    check("add_news/get_news: короткий без фото", n2 is not None
          and n2['photo_file_id'] is None)

    import bot.handlers.news as news_mod
    src = open(news_mod.__file__, encoding="utf-8").read()
    check("news_view: защита от длинного caption (long_text)",
          "long_text" in src and "> 900" in src)
    check("news_view: текстовые выпуски > 3900 уходят отдельным сообщением",
          "> 3900" in src)
    check("news_write: лимит длины 3000",
          "3000 символов" in src)

    # ── 2. Снежинка спец отряда ──
    check("wing_label(4) = снежинка", wing_label("4") == "❄️ 4 СО «Буран» (спец отряд)")
    check("WINGS_SHORT[4] = снежинка", WINGS_SHORT["4"] == "❄️ 4 СО")
    check("в других крыльях метки целы",
          wing_label("1") == "🐺 1 АК «Небесные Волки»"
          and wing_label("2") == "🦉 2 АК «Полярные Совы»"
          and wing_label("3") == "🌑 3 АК «Тени Нордхама»"
          and set(WINGS.keys()) == {"1", "2", "3", "4"})
    check("wing_display(None)", wing_display(None) == "— не назначено")

    # ── 3. Казна и долги ──
    d0 = await get_treasury_debts()
    check("долгов нет в пустой казне",
          d0['total_debt'] == 0 and d0['salaried_count'] == 0
          and d0['shortfall'] == 0)

    await set_user_salary(U1, 200, 7)
    await set_user_salary(U2, 100, 7)
    sal = await get_salaried_users()
    check("зарплаты назначены (2 получателя)", len(sal) == 2)

    # не хватило на момент выплаты → долг в 50 НМ
    await add_salary_debt(U1, 50)
    d1 = await get_treasury_debts()
    check("накопленный долг виден", d1['total_debt'] == 50
          and len(d1['debtors']) == 1 and d1['debtors'][0]['user_id'] == U1)
    check("прогноз на выплату = ставки суммарно + долг",
          d1['salaried_count'] == 2 and d1['next_pay_need'] == 350)

    await clear_salary_debt(U1)
    d2 = await get_treasury_debts()
    check("clear_salary_debt обнулил долг", d2['total_debt'] == 0)

    # pay_salaries при пустой казне не падает и возвращает структуру
    res = await pay_salaries()
    check("pay_salaries: структура ответа", set(res.keys()) == {"paid", "debt", "reserves"})
    check("pay_salaries: казна не ушла в минус", (await get_treasury_balance()) >= 0)
    d3 = await get_treasury_debts()
    check("долг после выплаты корректен (нет отрицательных)",
          d3['total_debt'] >= 0)

    await close_db()
    print(f"\nSmoke 076: {passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    try:
        asyncio.run(run())
    except SystemExit:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        from database.db import close_db
        asyncio.run(close_db())
        print(f"SMOKE ERROR: {e!r}")
        sys.exit(1)