"""Smoke v0.18.2: экономические бонусы наград (медалей).

- Скидка в магазине: действует на цену товара; потолок AWARD_MAX_SHOP_DISCOUNT (40%)
  применяется в shop_price_for(). Суммарный бонус в get_award_bonus() хранит сырую сумму.
- Снижение налога с отчёта: в п.п. от общей ставки, пол AWARD_MIN_REPORT_TAX (5%).
- create_award()/update_award() принимают новые поля.
- Мелочь не становится бесплатной (минимум 1 НМ).
"""
import asyncio
import os
import shutil
import sys
import tempfile

WORK = tempfile.mkdtemp(prefix="sm096_")
os.environ["DATABASE_PATH"] = os.path.join(WORK, "t.db")

from database import db as D
from config import AWARD_MAX_SHOP_DISCOUNT, AWARD_MIN_REPORT_TAX

FAILED = []


def check(name, cond, extra=""):
    print(("  ok   " if cond else "  FAIL ") + name + (f"  [{extra}]" if extra else ""))
    if not cond:
        FAILED.append(name)


async def main():
    await D.init_db()
    conn = await D.get_db()

    cols = [r["name"] for r in await (await conn.execute(
        "PRAGMA table_info(awards)")).fetchall()]
    check("в схеме есть bonus_shop_discount", "bonus_shop_discount" in cols)
    check("в схеме есть bonus_report_tax", "bonus_report_tax" in cols)

    for uid, name in ((2001, "Скидка"), (2002, "Перекос"),
                      (2003, "Налог"), (2004, "НалогПол"), (2999, "Обычный")):
        await conn.execute("INSERT INTO users (user_id, username) VALUES (?, ?)", (uid, name))
    await conn.commit()

    base_tax = await D.get_report_tax_percent()

    ok, aid_d = await D.create_award("Скидочная", "х", "💰", 1, bonus_shop_discount=15)
    ok2, aid_big = await D.create_award("Гигаскидка", "х", "💎", 1, bonus_shop_discount=100)
    ok3, aid_t = await D.create_award("Налоговая", "х", "🧾", 1, bonus_report_tax=3)
    ok4, aid_combo = await D.create_award("Супер", "х", "🏅", 1,
                                          bonus_attack=5, bonus_defense=4, bonus_hp=10)
    check("создание с бонусами", ok and ok2 and ok3 and ok4)

    check("без медалей цена та же", await D.shop_price_for(2999, 100) == 100)
    check("без медалей налог базовый", await D.report_tax_percent_for(2999) == base_tax)

    # --- 2001: одна медаль со скидкой 15% ---
    await D.grant_award(2001, aid_d, 0)
    check("скидка 15% → 85", await D.shop_price_for(2001, 100) == 85,
          str(await D.shop_price_for(2001, 100)))
    check("налоги не затронуты", await D.report_tax_percent_for(2001) == base_tax)

    # --- 2002: сумма скидок 100+100+100=300 → потолок применяется на покупке ---
    await D.grant_award(2002, aid_big, 0)
    await D.grant_award(2002, aid_big, 0)
    await D.grant_award(2002, aid_big, 0)
    b = await D.get_award_bonus(2002)
    capped = 100 * (100 - AWARD_MAX_SHOP_DISCOUNT) // 100
    check("сырая сумма бонуса 300", b["shop_discount"] == 300, str(b["shop_discount"]))
    check(f"потолок на покупке {AWARD_MAX_SHOP_DISCOUNT}% → {capped}",
          await D.shop_price_for(2002, 100) == capped, str(await D.shop_price_for(2002, 100)))
    check("мелочь не бесплатна", await D.shop_price_for(2002, 1) >= 1)

    # --- 2003: одна налоговая медаль −3 п.п. ---
    await D.grant_award(2003, aid_t, 0)
    check("налог 15−3=12", await D.report_tax_percent_for(2003) == base_tax - 3,
          str(await D.report_tax_percent_for(2003)))
    check("скидки нет", await D.shop_price_for(2003, 100) == 100)

    # --- 2004: налоговая ×4 → −12 → пол 5% ---
    await D.grant_award(2004, aid_t, 0)
    await D.grant_award(2004, aid_t, 0)
    await D.grant_award(2004, aid_t, 0)
    await D.grant_award(2004, aid_t, 0)
    check("пол налога 5%", await D.report_tax_percent_for(2004) == AWARD_MIN_REPORT_TAX,
          str(await D.report_tax_percent_for(2004)))

    # --- боевые бонусы по-прежнему суммируются ---
    await D.grant_award(2999, aid_combo, 0)
    bb = await D.get_award_bonus(2999)
    check("атака 5/защита 4/hp 10", bb["attack"] == 5 and bb["defense"] == 4 and bb["hp"] == 10,
          str(bb))

    # --- update_award с новыми полями ---
    await D.grant_award(2001, aid_t, 0)
    await D.update_award(aid_t, bonus_report_tax=10, bonus_shop_discount=7)
    bu = await D.get_award_bonus(2001)
    check("update: налог −10, скидка 15+7",
          bu["report_tax"] == 10 and bu["shop_discount"] == 22, str(bu))
    check("налог 15−10=5 (пол)", await D.report_tax_percent_for(2001) == 5,
          str(await D.report_tax_percent_for(2001)))

    # --- высокая ставка — снижение всё ещё п.п. ---
    await D.set_report_tax_percent(30)
    # у 2003 уже две медали aid_t по −3 → сумма −6
    await D.grant_award(2003, aid_t, 0)
    await D.update_award(aid_t, bonus_report_tax=3)
    check("при ставке 30% − (−3×2) → 24", await D.report_tax_percent_for(2003) == 24,
          str(await D.report_tax_percent_for(2003)))

    await D.close_db()
    shutil.rmtree(WORK, ignore_errors=True)
    total = len(FAILED)
    print("\nSmoke 096: " + ("all passed" if not total else f"{total} failed"))
    sys.exit(1 if FAILED else 0)


asyncio.run(main())