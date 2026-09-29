"""Smoke v0.18.12: сквозная выдача награды и дропа за прохождение К.В.П.

Имитируем последовательность kvp_win (bot/handlers/kvp.py) против временной БД:
  1. сед КВП: трость в каталоге, награда «Значок В.У.С.П.» с бонусами 2/3;
  2. 1-е прохождение → награда в user_awards, трость в инвентаре, прогресс 1/4,
     badge_awarded=1, stick_dropped=1;
  3. награда видна в «Наградах» (get_user_awards) со всеми полями карточки,
     а _award_perks рендерит её бонусы (+2% атака, +3% уклонение);
  4. 2-е прохождение → награда НЕ дублируется (защита от повтора).

Запуск: .venv\\Scripts\\python.exe smoke_105.py
"""
import asyncio
import os
import shutil
import sys
import tempfile

WORK = tempfile.mkdtemp(prefix="sm105_")
os.environ["DATABASE_PATH"] = os.path.join(WORK, "t.db")
sys.path.insert(0, os.path.dirname(__file__))

from database import db as D

CARD_FIELDS = ('grant_id', 'comment', 'granted_at', 'award_id', 'name',
               'description', 'emoji', 'image',
               'bonus_attack', 'bonus_defense', 'bonus_dodge', 'bonus_fishing',
               'bonus_hp', 'bonus_shop_discount', 'bonus_report_tax')


def check(name, cond):
    print(("  ok   " if cond else "  FAIL ") + name)
    if not cond:
        FAILED.append(name)


FAILED = []


async def main():
    await D.init_db()
    await D.seed_kvp()
    await D.ensure_kvp_items()
    await D.ensure_kvp_award()

    uid = 777
    await D.add_user(uid, "pilot", "Пилот", "Нордхайма")

    cane = await D.get_item_by_name(D.KVP_CANE_NAME)
    check("трость в каталоге", cane is not None)
    if cane:
        check("трость: урон 3 + stun + loot_only",
              (cane["damage"] or 0) == 3 and (cane["weapon_effect"] or "") == "stun"
              and bool(cane["loot_only"]))

    # --- «kvp_win»: 1-е прохождение ---
    progress = await D.get_kvp_progress(uid)
    granted = False
    if not progress["badge_awarded"]:
        cur = await D.get_db()
        row = await (await cur.execute(
            "SELECT id FROM awards WHERE name = ?", (D.KVP_BADGE_NAME,))).fetchone()
        if row:
            granted, _ = await D.grant_award(uid, row["id"],
                                             comment="Пройден К.В.П. впервые")
    if granted:
        await D.mark_kvp_badge(uid)
    if cane and not progress["stick_dropped"]:
        await D.add_inventory_item(uid, cane["id"], 1)
        await D.mark_kvp_stick(uid)
    await D.increment_kvp_completions(uid)

    progress = await D.get_kvp_progress(uid)
    check("прогресс 1/4, badge и stick", progress["completions"] == 1
          and progress["badge_awarded"] == 1 and progress["stick_dropped"] == 1)

    # --- награда в «Наградах» (get_user_awards + карточка профиля) ---
    awards = await D.get_user_awards(uid)
    badge = next((a for a in awards if a["name"] == D.KVP_BADGE_NAME), None)
    check("значок в списке наград", badge is not None)
    if badge:
        missing = [f for f in CARD_FIELDS if f not in badge.keys()]
        check("все поля карточки на месте (включая image)", not missing)
        check("бонусы 2/3 в карточке",
              badge["bonus_attack"] == 2 and badge["bonus_dodge"] == 3)
        check("комментарий «впервые»", badge["comment"] == "Пройден К.В.П. впервые")

        from bot.handlers.profile import _award_perks
        perks = _award_perks(badge)
        check("бонусы рендерятся в карточке",
              "⚔️ +2% атака" in perks and "💨 +3% уклонение" in perks)

    # --- трость в инвентаре ---
    if cane:
        inv = await D.get_inventory_item(uid, cane["id"])
        check("трость в инвентаре, 1 шт", bool(inv and inv["quantity"] == 1))

    # --- 2-е прохождение: защита от дубля награды ---
    before = len(await D.get_user_awards(uid))
    progress = await D.get_kvp_progress(uid)
    granted2 = False
    if not progress["badge_awarded"]:
        cur = await D.get_db()
        row = await (await cur.execute(
            "SELECT id FROM awards WHERE name = ?", (D.KVP_BADGE_NAME,))).fetchone()
        if row:
            granted2, _ = await D.grant_award(uid, row["id"],
                                              comment="Пройден К.В.П. впервые")
    if granted2:
        await D.mark_kvp_badge(uid)
    await D.increment_kvp_completions(uid)
    after = len(await D.get_user_awards(uid))
    check("2-е прохождение не дублирует награду",
          granted2 is False and after == before)

    await D.close_db()
    shutil.rmtree(WORK, ignore_errors=True)
    total = len(FAILED)
    print("\nSmoke 105: " + ("all passed" if not total else f"{total} failed"))
    sys.exit(1 if FAILED else 0)


asyncio.run(main())