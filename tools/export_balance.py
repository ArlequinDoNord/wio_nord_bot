"""Экспорт баланса N.O.R.D. в Markdown.

Читает актуальные значения из БД (товары, враги, статусы, награды, рыба,
рецепты) + константы из config. Запуск:
    python tools/export_balance.py [path_to_nordmark.db]
По умолчанию БД — database/nordmark.db (или DATABASE_PATH).
Вывод — Markdown в stdout (сохраняйте в BALANCE.md).
"""
import os
import sqlite3
import sys
from datetime import datetime

from fractions import Fraction

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config

DB = sys.argv[1] if len(sys.argv) > 1 else os.getenv(
    "DATABASE_PATH", os.path.join(os.path.dirname(config.__file__), "database", "nordmark.db"))
if not os.path.isabs(DB):
    DB = os.path.join(os.path.dirname(__file__), DB)

_L = []


def emit(*lines):
    for ln in lines:
        _L.append(str(ln))


def money(n):
    return f"{int(n or 0):,}".replace(",", " ")


def esc(x):
    return str(x).replace("|", "\\|") if x is not None else "—"


def rarity_of(r):
    return config.RARITY_LEVELS.get(r, f"уровень {r}")


def md_table(headers, rows):
    emit("| " + " | ".join(headers) + " |")
    emit("|" + "|".join(["---"] * len(headers)) + "|")
    for r in rows:
        emit("| " + " | ".join(esc(c) for c in r) + " |")


def drops_str(drops_json):
    if not drops_json:
        return "—"
    try:
        import json
        drops = json.loads(drops_json)
    except Exception:
        return esc(drops_json)
    parts = []
    for d in drops:
        chance = (d.get('chance') or 0) * 100
        qty = d.get('qty') or 1
        parts.append(f"{d.get('item')} ({chance:.0f}%, x{qty})")
    return "<br>".join(parts) if parts else "—"


def main():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    emit(f"# Баланс N.O.R.D. 3.0 — v{config.VERSION}")
    emit("")
    emit(f"*Сгенерировано: {datetime.now().strftime('%Y-%m-%d %H:%M')} "
         f"· источник: {os.path.basename(DB)} (актуальные значения на сервере)*")
    emit("")
    emit("> Файл для анализа и правки цифр баланса. Значения из таблиц БД — "
         "текущие игровые (в т.ч. правки через админку); константы — из `config.py`.")

    # ── 1. Налоги и экономика ──
    emit("## 1. Экономика и налоги")
    emit("")
    settings = {r['key']: r['value'] for r in conn.execute("SELECT key, value FROM settings")}
    tr = conn.execute("SELECT balance FROM treasury WHERE id = 1").fetchone()
    emit(f"- **Казна (treasury)**: {money(tr['balance'] if tr else 0)} НМ")
    emit(f"- **Налог с отчёта** (`settings.report_tax_percent`): "
         f"{settings.get('report_tax_percent', '15')}% — с доначисления войск по отчёту в казну")
    emit(f"- **Налог с продажи** (`settings.sale_tax_percent`): "
         f"{settings.get('sale_tax_percent', '15')}% — комиссия рынка/витрины при продаже")
    emit("")
    emit("**Налог на жильё (НМ/мес, `HOUSING_TAX`):**")
    md_table(["Жильё", "Налог, НМ/мес"],
             [(k, money(v)) for k, v in config.HOUSING_TAX.items()])
    emit("")
    emit("**Финансовые лимиты:**")
    emit(f"- Банк: туристу счёт не больше **{money(config.TOURIST_BALANCE_LIMIT)} НМ** (`TOURIST_BALANCE_LIMIT`)")
    emit(f"- Рынок: слотов {config.MARKET_BASE_SLOTS} + {config.MARKET_LICENSE_SLOTS} по лицензии; "
         f"лицензия {money(config.MARKET_LICENSE_PRICE)} НМ на {config.MARKET_LICENSE_DAYS} дн.")
    emit(f"- Стена изречений: {config.WALL_FREE_PER_DAY} бесплатных/сутки, далее ступени — ")
    emit("  " + "; ".join(f"{q} шт × {p} НМ" for q, p in config.WALL_PAID_STEPS)
         + f", лимит в сутки {config.WALL_REVIEW_TOTAL} (текст ≤ {config.WALL_TEXT_MAX_LEN} симв.)")

    # ── 2. Звания ──
    emit("")
    emit("## 2. Звания (войсковые, `RANKS`)")
    emit("")
    md_table(["Звание", "Порог войск"],
             [(r, money(t)) for r, t in config.RANKS])
    emit(f"\n- До звания **«Лейтенант»** ({config.MAX_SELF_RANK_TROOPS} войск) пилот набирает войска "
         f"через отчёты; свыше — только выдача админом/МВД (`MAX_SELF_RANK_TROOPS`).")

    # ── 3. Отчёты и ОД ──
    emit("")
    emit("## 3. Отчёты и ОД (действия)")
    emit("")
    emit(f"- Отчёты: до **{config.REPORT_DAILY_LIMIT}/сутки**; автосогласование до "
         f"**{config.REPORT_AUTO_APPROVE_TROOPS}** войск в день; максимум в одном отчёте "
         f"**{config.REPORT_MAX_TROOPS:,}**; регионов **{config.REPORT_MAX_REGION}** (0 — Столица).")
    emit(f"- ОД (AP): максимум **{config.AP_MAX}**, суточное восстановление **{config.AP_DAILY_RECOVERY}**; "
         f"от расходника — **{config.AP_BONUS_FROM_CONSUMABLE}** (доп. лимит восстановления "
         f"{config.AP_DAILY_RESTORE_LIMIT}/сутки, далее «истощён» на {config.AP_EXHAUSTED_MINUTES // 60} ч — "
         f"восстановление {config.AP_EXHAUSTED_DAILY_RECOVERY}/сутки, максимум {config.AP_EXHAUSTED_MAX_AP}).")
    emit(f"- Данж: лимит лечения {config.DUNGEON_HEAL_SOFT_LIMIT} → x{Fraction(config.DUNGEON_HEAL_SOFT_MULT).limit_denominator(8)}, "
         f"{config.DUNGEON_HEAL_HARD_LIMIT} → x{Fraction(config.DUNGEON_HEAL_HARD_MULT).limit_denominator(8)}; побег (без шашки) "
         f"{config.ESCAPE_BASE_CHANCE}%+{config.ESCAPE_HP_BONUS}%·(1−HP), дымовая шашка "
         f"{config.DUNGEON_SMOKE_ESCAPE}% (макс {config.DUNGEON_SMOKE_MAX} шт), в «очень пьян» x"
         f"{config.DUNGEON_ESCAPE_DRUNK_MULT}.")
    C = config
    emit(f"- К.В.П.: прохождение препятствия {C.KVP_OD_COST if hasattr(C, 'KVP_OD_COST') else '5'} ОД; "
         f"прохождений максимум {C.KVP_MAX_COMPLETIONS if hasattr(C, 'KVP_MAX_COMPLETIONS') else '4'}; "
         f"награда — значок «В.У.С.П.».")
    emit(f"- Рыбалка: **{config.FISH_AP_COST} ОД** за заброс; вес улова и множитель цены: ")
    emit("  " + "; ".join(f"{w['label']} ×{w['mult']} ({w['chance']}%)" for w in config.FISH_WEIGHTS))
    emit(f"- Алкоголь: лёгкий — {config.ALCOHOL_WEAK_DRUNK_LIMIT}-й/сутки «пьян», "
         f"{config.ALCOHOL_WEAK_VERY_DRUNK_LIMIT}-й «очень пьян»; крепкий — "
         f"{config.ALCOHOL_STRONG_DRUNK_LIMIT}-й/сутки «пьян», {config.ALCOHOL_STRONG_VERY_DRUNK_LIMIT}-й «очень пьян»; "
         f"«пьян» {config.DRUNK_MINUTES} мин, «очень пьян» {config.VERY_DRUNK_MINUTES} мин.")
    emit(f"- Водоросли (еда из ламинарии): лимит {config.SEAWEED_DAILY_LIMIT}/сутки, далее «несварение» "
         f"{config.DIGESTIVE_UPSET_MINUTES // 60} ч.")

    # ── 4. Статусы ──
    emit("")
    emit("## 4. Статусы игроков")
    emit("")
    st_rows = conn.execute("SELECT name, access_tag, description FROM statuses ORDER BY sort_order, id").fetchall()
    if st_rows:
        md_table(["Статус (access_tag)", "Описание"],
                 [(f"{r['name']} (`{r['access_tag']}`)", r['description'] or "") for r in st_rows])
    else:
        emit("Нет статусов.")

    # ── 5. Награды ──
    emit("")
    emit("## 5. Награды и их бонусы")
    emit("")
    aw_rows = conn.execute(
        "SELECT name, emoji, bonus_attack, bonus_defense, bonus_dodge, bonus_fishing, bonus_hp, description "
        "FROM awards ORDER BY id").fetchall()
    if aw_rows:
        md_table(["Награда", "АТК", "Защита", "Уклонение", "Рыбалка", "HP", "Описание"],
                 [(f"{r['emoji'] or ''} {r['name']}", r['bonus_attack'], r['bonus_defense'],
                   r['bonus_dodge'], r['bonus_fishing'], r['bonus_hp'], r['description'] or "")
                  for r in aw_rows])
    else:
        emit("Наград нет.")

    # ── 6. Магазин (товары) ──
    emit("")
    emit("## 6. Магазин — товары (из `items`)")
    emit("")
    it = conn.execute(
        "SELECT name, price, sell_price, rarity, category, stock, ap_cost, heal, armor, damage, "
        "required_status, cure_poison, cure_frostbite, drink_effect, equip_slot, "
        "weapon_effect, weapon_effect_chance, weapon_effect_dmg, plant_name, produced_by, description "
        "FROM items WHERE is_available != 0 "
        "ORDER BY CASE category WHEN 'weapon' THEN 1 WHEN 'consumable' THEN 2 WHEN 'housing' THEN 3 "
        "  WHEN 'furniture' THEN 4 WHEN 'equipment' THEN 5 WHEN 'seeds' THEN 6 WHEN 'resource' THEN 7 "
        "  WHEN 'fishing' THEN 8 WHEN 'special' THEN 9 WHEN 'special_dept' THEN 10 WHEN 'souvenirs' THEN 11 "
        "  WHEN 'library_card' THEN 12 WHEN 'license' THEN 13 WHEN 'recipes' THEN 14 ELSE 99 END, price, id").fetchall()
    for cat in ("weapon", "consumable", "housing", "furniture", "equipment", "seeds",
                "resource", "fishing", "special", "special_dept", "souvenirs",
                "library_card", "license", "recipes"):
        rows = [r for r in it if r['category'] == cat]
        if not rows:
            continue
        emit(f"### 6.{list(config.ITEM_CATEGORIES).index(cat) + 1}. {config.ITEM_CATEGORIES.get(cat, cat)} "
             f"({len(rows)})")
        emit("")
        table = []
        for r in rows:
            extra = []
            if r['damage']:
                extra.append(f"⚔️{r['damage']}")
            if r['heal']:
                extra.append(f"❤️{r['heal']}")
            if r['armor']:
                extra.append(f"🛡{r['armor']}")
            if r['ap_cost']:
                extra.append(f"AP{r['ap_cost']}")
            if r['equip_slot']:
                extra.append(f"слот:{r['equip_slot']}")
            if r['required_status']:
                extra.append(f"треб.:{r['required_status']}")
            if r['cure_poison']:
                extra.append("леч.яд")
            if r['cure_frostbite']:
                extra.append("леч.мороз")
            if r['drink_effect'] and r['drink_effect'] != 'none':
                extra.append(config.DRINK_EFFECT_LABELS.get(r['drink_effect'], r['drink_effect']))
            if r['weapon_effect']:
                extra.append(f"эффект:{r['weapon_effect']} ({r['weapon_effect_chance'] or 0}%, "
                             f"{r['weapon_effect_dmg'] or 0} урона)")
            if r['plant_name']:
                extra.append(f"растение:{r['plant_name']}")
            if r['produced_by']:
                extra.append(f"рецепт:{r['produced_by']}")
            table.append([
                r['name'],
                money(r['price']),
                money(r['sell_price']),
                rarity_of(r['rarity']),
                "∞" if r['stock'] is None or r['stock'] < 0 else str(r['stock']),
                "<br>".join(extra) if extra else "—",
            ])
        md_table(["Товар", "Цена, НМ", "Продажа, НМ", "Редкость", "Запас", "Статы и эффекты"], table)
        emit("")

    # ── 7. Подземелья и враги ──
    emit("## 7. Подземелья и враги")
    emit("")
    dungeons = conn.execute(
        "SELECT id, name, description, floors_count, rooms_per_floor, is_training, rooms_map "
        "FROM dungeons ORDER BY id").fetchall()
    for d in dungeons:
        label = " (тренировочный)" if d['is_training'] else ""
        emit(f"### 7.{d['id']}. {d['name']}{label}")
        emit("")
        emit(f"*Этажи: {d['floors_count']} · комнат на этаж: {d['rooms_per_floor']}*")
        floors = conn.execute(
            "SELECT floor, name, hp, attack, dodge, poison_chance, poison_dmg, bleed_chance, bleed_dmg, "
            "frostbite_chance, reward_nm, is_boss, drops "
            "FROM dungeon_enemies WHERE dungeon_id = ? ORDER BY floor, is_boss, id",
            (d['id'],)).fetchall()
        rows = []
        for e in floors:
            statuses = []
            if e['poison_chance']:
                statuses.append(f"яд {e['poison_chance']}%/{e['poison_dmg']}")
            if e['bleed_chance']:
                statuses.append(f"кровот {e['bleed_chance']}%/{e['bleed_dmg']}")
            if e['frostbite_chance']:
                statuses.append(f"мороз {e['frostbite_chance']}%")
            rows.append([
                f"{e['floor']} эт.",
                (("👑 " if e['is_boss'] else "") + e['name']),
                e['hp'], e['attack'], e['dodge'],
                "<br>".join(statuses) if statuses else "—",
                money(e['reward_nm']),
                drops_str(e['drops']),
            ])
        md_table(["Этаж", "Враг", "HP", "АТК", "Укл", "Статусы", "Награда НМ", "Дропы"], rows)
        emit("")

    # ── 8. Рыбалка ──
    emit("## 8. Рыбалка (водоёмы)")
    emit("")
    fishes = conn.execute(
        "SELECT wf.water, wf.day_weight, wf.night_weight, wf.excluded, wf.kind, "
        "it.name, it.price, it.sell_price "
        "FROM water_fish wf LEFT JOIN items it ON wf.item_id = it.id "
        "ORDER BY wf.water, it.name").fetchall()
    if fishes:
        emit("Строка «вес днём/ночью» — множитель базы цены рыбы в интерфейсе улова; "
             "цифры в таблице — базовая цена/выкуп.")
        md_table(["Водоём", "Рыба", "Вес дн/ноч", "Цена, НМ", "Выкуп, НМ", "Тип"],
                 [(wf['water'], wf['name'] or '?', f"{wf['day_weight']}/{wf['night_weight']}",
                   money(wf['price']), money(wf['sell_price']), wf['kind'] or "")
                  for wf in fishes])
    junk = conn.execute("SELECT water, name, chance FROM water_junk ORDER BY water, id").fetchall()
    if junk:
        md_table(["Водоём", "Мусор/находка", "Шанс, %"],
                 [(j['water'], j['name'],
                   f"{j['chance'] * 100:.0f}" if (j['chance'] or 0) <= 1 else f"{j['chance']:.0f}")
                  for j in junk])

    EXPANSION_LABELS = {"kitchen": "Кухня", "workbench": "Верстак",
                        "plant_pot": "Кадка для растений"}

    # ── 9. Крафт (рецепты) ──
    emit("")
    emit("## 9. Крафт — рецепты (`recipes`)")
    emit("")
    recs = conn.execute(
        "SELECT name, result_item_name, result_quantity, ingredients, ap_cost, production_time, "
        "required_expansion, required_level, rarity, description "
        "FROM recipes ORDER BY required_level, id").fetchall()
    if recs:
        md_table(["Рецепт", "Результат", "Ингредиенты (название × кол-во)", "AP", "Время", "Треб.",
                  "Редкость"],
                 [(r['name'],
                   f"{r['result_item_name']} ×{r['result_quantity'] or 1}",
                   (r['ingredients'] or '') if isinstance(r['ingredients'], str) else str(r['ingredients']),
                   r['ap_cost'], r['production_time'], 
                   ", ".join(x for x in [r['required_expansion'] or '',
                                         (f"уровень {r['required_level']}" if r['required_level'] else '')] if x) or "—",
                   rarity_of(r['rarity']))
                  for r in recs])
    else:
        emit("Рецептов нет.")

    # ── 10. Парк и библиотека ──
    emit("")
    emit("## 10. Парк (статуи) и Библиотека")
    emit("")
    st = conn.execute("SELECT name, description FROM park_statues ORDER BY sort_order, id").fetchall()
    if st:
        md_table(["Статуя", "Описание"], [(s['name'], s['description'] or "") for s in st])
    cards = conn.execute("SELECT DISTINCT card_type FROM library_cards").fetchall()
    if cards:
        emit("\nТипы читательских билетов (в прокате): " + ", ".join(c['card_type'] for c in cards))
    books_n = conn.execute("SELECT COUNT(*) FROM library_books").fetchone()[0]
    emit(f"\nКниг в библиотеке: {books_n}.")

    # ── 11. Жильё и слоты ──
    emit("")
    emit("## 11. Жильё и домашние слоты")
    emit("")
    slots = conn.execute("SELECT DISTINCT expansion_type FROM housing_slots").fetchall()
    if slots:
        emit("Расширения жилья: " + ", ".join(
            EXPANSION_LABELS.get(s['expansion_type'], s['expansion_type']) for s in slots))
    others = [r for r in it if r['category'] in ("housing", "furniture")]
    if others:
        emit("\nТовары жилья и расширений включены в раздел 6 (Магазин).")

    # ── 12. Локации ──
    emit("")
    emit("## 12. Локации города")
    emit("")
    locs = conn.execute("SELECT name, access_mode, required_status, blocking_states FROM locations "
                        "ORDER BY sort_order, id").fetchall()
    md_table(["Локация", "Режим доступа", "Треб. статус", "Блокируют состояния"],
             [(l['name'], l['access_mode'], l['required_status'] or "—", l['blocking_states'] or "—")
              for l in locs])

    emit("")
    emit("---")
    emit("*Файл генерируется `tools/export_balance.py`; после правки цифр в коде/админке можно "
         "перегенерировать.*")

    print("\n".join(_L))


if __name__ == "__main__":
    main()