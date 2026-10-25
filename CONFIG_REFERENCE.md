# Справочник констант `config.py`

> **Сгенерировано** `tools/export_config.py`. Перегенерация:
> `.venv\Scripts\python.exe tools/export_config.py`.
>
> Все модульные константы `config.py`, сгруппированные по секциям
> (комментариям-разделителям `# ── … ──`). Длинные значения усечены `…`;
> точное значение — в `config.py` по строке из первой колонки.

Всего констант: **210**; разделов: **10**.

## Без раздела

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `VERSION` | `'0.38.6'` |  | :16 |
| `VERSION_NOTES` | `'В кланах закладывают первые фундаменты…'` |  | :17 |
| `PREV_VERSION` | `'0.38.5'` |  | :19 |
| `PREV_VERSION_NOTES` | `'Кланы открыли общий склад: ресурсы — в общий котёл, вклады — в журнал.'` |  | :20 |
| `TOURIST_BOOKLET_DESCRIPTION` | `'Печатная карта Нордхайма для гостей города. Просматривай превью городских локаций — и отмечай их в буклете. Собери все 9 и получи награду от командования.'` |  | :25 |
| `TOURIST_BOOKLET_PRICE` | `1` |  | :28 |
| `TOURIST_BOOKLET_SELL_PRICE` | `0` | буклет не продаётся (иначе чек-лист теряется) | :29 |
| `TOURIST_BOOKLET_AWARD` | `'Опытный турист'` |  | :30 |
| `TOURIST_BOOKLET_AWARD_EMOJI` | `'🧭'` |  | :31 |
| `TOURIST_BOOKLET_AWARD_DESCRIPTION` | `'Посетил все городские локации Нордхайма по «Буклету туриста». Знак почётного гостя города.'` |  | :32 |
| `TOURIST_BOOKLET_REWARD_NM` | `20` |  | :34 |
| `TOURIST_BOOKLET_REWARD_TX` | `'booklet'` |  | :35 |
| `TOURIST_BOOKLET_LOCATIONS` | `('townhall', 'library', 'park', 'gossmi', 'bank', 'kvp', 'hq', 'contracts', 'nii')` |  | :38 |
| `CLAN_HALL_ENABLED` | `False` |  | :47 |
| `CLAN_BUILDING_TYPES` | `{'house': {'name': 'Дом Клана', 'slots': 2, 'max_level': 2, 'days': 5, 'price_nm': 3000, 'required': {'Доска': 60, 'Бревна': 20, 'Железная руда': 15}}, 'manor': {'name': 'Клановое поместье', 'slots…` |  | :49 |
| `CLAN_EXPANSION_TYPES` | `('kitchen', 'workbench', 'shower', 'garden', 'library', 'shop')` |  | :61 |
| `CLAN_EXPANSION_UPGRADE` | `{2: {'nm': 1500, 'required': {'Доска': 20, 'Железная руда': 10}}, 3: {'nm': 4000, 'required': {'Доска': 50, 'Железная руда': 30}}, 4: {'nm': 9000, 'required': {'Доска': 100, 'Железная руда': 60}}}` |  | :63 |
| `CLAN_GARDEN_PLOTS` | `{1: 2, 2: 3, 3: 4, 4: 6}` |  | :69 |
| `CLAN_SHOP_DAILY_LIMIT` | `3` |  | :70 |
| `CLAN_SHOP_DISCOUNT` | `10` |  | :71 |
| `BOT_TOKEN` | `os.getenv('BOT_TOKEN')` |  | :73 |
| `ADMIN_IDS` | `[int(x) for x in os.getenv('ADMIN_IDS', '').split(',') if x.strip()]` |  | :74 |
| `_news_raw` | `os.getenv('NEWS_CHAT_ID', '').strip()` |  | :77 |
| `NEWS_CHAT_ID` | `int(_news_raw) if _news_raw.lstrip('-').isdigit() else None` |  | :78 |
| `DB_PATH` | `os.getenv('DATABASE_PATH', 'database/nordmark.db')` |  | :81 |
| `FSM_STORAGE_PATH` | `os.getenv('FSM_STORAGE_PATH', '').strip() or os.path.join(os.path.dirname(os.path.abspath(DB_PATH)), 'fsm')` |  | :90 |
| `REPORT_DAY_START_MINUTE` | `0` |  | :100 |
| `RANKS` | `[('Рекрут', 0), ('Рядовой', 100), ('Ефрейтор', 350), ('Капрал', 500), ('Сержант', 850), ('Старший Сержант', 1500), ('Лейтенант', 2500), ('Старший Лейтенант', 4040), ('Капитан', 6000), ('Майор', 850…` |  | :102 |
| `MAX_SELF_RANK_TROOPS` | `4040` |  | :123 |
| `AUTO_RANK_NAMES` | `('Рекрут', 'Рядовой', 'Ефрейтор', 'Капрал', 'Сержант', 'Старший Сержант', 'Лейтенант', 'Старший Лейтенант')` |  | :126 |
| `AWARD_MAX_SHOP_DISCOUNT` | `40` |  | :133 |
| `AWARD_MIN_REPORT_TAX` | `5` |  | :134 |
| `RANK_STATUS_TAGS` | `{'Ефрейтор': 'pilot2', 'Старший Сержант': 'pilot1', 'Старший Лейтенант': 'veteran', 'Майор': 'master_pilot', 'Полковник': 'ace'}` |  | :136 |
| `LEGIONER_ACCESS_CAP_ORDER` | `5` |  | :149 |
| `RANK_DAMAGE_TIERS` | `{'ace': (4, 8), 'master_pilot': (3, 5), 'veteran': (2, 4), 'pilot1': (1, 3), 'pilot2': (1, 2), 'recruit': (1, 1), 'tourist': (0, 1)}` |  | :155 |
| `RANK_CRIT_CHANCE` | `{'ace': 7.5, 'master_pilot': 6.0, 'veteran': 4.5, 'pilot1': 3.0, 'pilot2': 1.5, 'recruit': 0.0, 'tourist': 0.0}` |  | :173 |
| `PILOT_CRIT_MULT` | `1.4` |  | :187 |
| `PILOT_NO_WEAPON_DMG` | `(1, 1)` |  | :190 |
| `DUEL_ZONE_LABELS` | `{'head': 'Голова', 'body': 'Тело', 'hands': 'Руки', 'legs': 'Ноги'}` |  | :197 |
| `DUEL_ZONE_EMOJI` | `{'head': '🧠', 'body': '🫀', 'hands': '✊', 'legs': '🦵'}` |  | :203 |
| `DUEL_AP_COST` | `15` | списывается с обоих при старте боя | :209 |
| `DUEL_RATING_WIN` | `2` | рейтинг за победу | :210 |
| `DUEL_RATING_LOSS` | `-3` | рейтинг за поражение | :211 |
| `DUEL_RATING_DRAW` | `0` | рейтинг за ничью | :212 |
| `DUEL_RATING_FORFEIT` | `-1` | рейтинг тому, кто покинул бой («Покинуть дуэль») | :213 |
| `DUEL_RATING_FORFEIT_WIN` | `1` | рейтинг сопернику, если противник покинул бой (меньше чистой победы) | :214 |
| `DUEL_MIN_DAMAGE` | `1` | минимум урона за попавший (не уклонённый) удар | :215 |
| `DUEL_GUARD_REDUCTION` | `0.5` | доля урона, остающаяся при угаданной зоне защиты | :216 |
| `DUEL_HEAL_BETWEEN` | `0` | восстановление HP между раундами (пока нет) | :217 |
| `DUEL_CHALLENGE_TIMEOUT_SEC` | `120` | сколько живёт неотвеченный вызов | :218 |
| `DUEL_STALE_SEC` | `1800` | зависшая дуэль авто-завершается как void | :219 |
| `DUEL_GLOVES_NAME` | `'Дуэльные перчатки'` |  | :220 |
| `DUEL_GLOVES_DAMAGE` | `7` |  | :221 |
| `DUEL_GLOVES_PRICE` | `200` |  | :222 |
| `DUEL_GLOVES_SELL` | `100` |  | :223 |
| `DUEL_CLUB_CARD_NAME` | `'Клубная карта «Дом Дуэлей»'` |  | :224 |
| `DUEL_CLUB_CARD_PRICE` | `150` |  | :225 |
| `DUEL_CLUB_CARD_SELL` | `75` |  | :226 |
| `DUEL_CLUB_CARD_DAYS` | `30` |  | :227 |
| `DUEL_ACCESS_TAG` | `'pilot2'` |  | :230 |
| `RARITY_LEVELS` | `{1: 'Обычный', 2: 'Качественный', 3: 'Редкий', 4: 'Шедевр', 5: 'Легендарный'}` |  | :232 |
| `RARITY_EMOJI` | `{1: '⬜', 2: '🟩', 3: '🟦', 4: '🟪', 5: '🟧'}` |  | :240 |
| `ITEM_CATEGORIES` | `{'weapon': 'Оружие', 'consumable': 'Расходники', 'building': 'Недвижимость', 'housing': 'Жильё', 'furniture': 'Мебель и расширения', 'seeds': 'Семена', 'equipment': 'Одежда', 'resource': 'Ресурсы',…` |  | :248 |
| `MARKET_LICENSE_SLOTS` | `2` | доп. слоты при активной лицензии | :272 |
| `MARKET_LICENSE_DAYS` | `30` | срок действия лицензии (дней) | :273 |
| `MARKET_LICENSE_PRICE` | `500` | цена лицензии в НМ | :274 |
| `DUNGEON_HEAL_HARD_LIMIT` | `10` | после этого — ×1/2 | :291 |
| `DUNGEON_HEAL_SOFT_MULT` | `2 / 3` |  | :292 |
| `DUNGEON_HEAL_HARD_MULT` | `1 / 2` |  | :293 |
| `ESCAPE_HP_BONUS` | `20` |  | :308 |
| `DUNGEON_SMOKE_ESCAPE` | `95` |  | :309 |
| `DUNGEON_SMOKE_MAX` | `2` |  | :310 |
| `DUNGEON_ESCAPE_DRUNK_MULT` | `0.5` |  | :313 |
| `AP_MAX` | `150` |  | :315 |
| `AP_DAILY_RECOVERY` | `100` |  | :316 |
| `AP_BONUS_FROM_CONSUMABLE` | `50` |  | :317 |
| `AP_DAILY_RESTORE_LIMIT` | `150` |  | :322 |
| `AP_EXHAUSTED_MINUTES` | `2880` | 2 суток | :323 |
| `AP_EXHAUSTED_DAILY_RECOVERY` | `75` | суточное восстановление в «истощении» | :324 |
| `AP_EXHAUSTED_MAX_AP` | `90` | максимум ОД в «истощении» | :325 |
| `SEAWEED_DAILY_LIMIT` | `6` |  | :328 |
| `DIGESTIVE_UPSET_MINUTES` | `1440` | 24 часа | :329 |
| `ALCOHOL_WEAK_DRUNK_LIMIT` | `3` |  | :334 |
| `ALCOHOL_WEAK_VERY_DRUNK_LIMIT` | `6` |  | :335 |
| `ALCOHOL_STRONG_DRUNK_LIMIT` | `1` |  | :337 |
| `ALCOHOL_STRONG_VERY_DRUNK_LIMIT` | `2` |  | :338 |
| `DRUNK_MINUTES` | `60` |  | :339 |
| `VERY_DRUNK_MINUTES` | `360` | 6 часов | :340 |
| `DRINK_EFFECT_LABELS` | `{'alcohol_weak': '🍺 Слабоалкогольный: 3 шт/сутки — «пьян», 6 — «очень пьян»', 'alcohol_strong': '🥃 Крепкий алкоголь: 1 шт — «пьян», 2 — «очень пьян»', 'indigestion': '🤢 Вызывает «несварение» на сут…` |  | :343 |
| `SPECIAL_DEPT_CODE_MIN_LEN` | `4` |  | :354 |
| `SPECIAL_DEPT_CODE_MAX_LEN` | `8` |  | :355 |
| `SPECIAL_DEPT_ATTEMPTS_LIMIT` | `3` | ошибок кода подряд | :356 |
| `SPECIAL_DEPT_BLOCK_MINUTES` | `1440` | бан на 24 часа после 3 ошибок | :357 |
| `FISH_AP_COST` | `3` | стоимость одного заброса удочки | :360 |
| `RESERVOIR_AP_COST` | `5` |  | :365 |
| `FISH_WEIGHTS` | `[{'key': 'small', 'label': 'Мелкая', 'mult': 1.0, 'chance': 40}, {'key': 'medium', 'label': 'Средняя', 'mult': 1.15, 'chance': 40}, {'key': 'large', 'label': 'Большая', 'mult': 1.25, 'chance': 20}]` |  | :370 |
| `FISH_TREASURY_SALE_MULT` | `0.5` |  | :378 |
| `FISH_TREASURY_DAILY_LIMIT` | `300` |  | :383 |
| `FOREST_AP_COST` | `4` | запасной цена поиска, если у зоны нет ap_cost в БД | :386 |
| `FOREST_RESULT_DELAY` | `(5, 10)` | результат поиска через 5–10 секунд | :389 |
| `FOREST_SOLD_DAILY_LIMIT` | `250` |  | :394 |
| `FOREST_ALLOW_TOURISTS` | `False` |  | :399 |
| `FOREST_BOAR_PITY_TARGET` | `12` |  | :402 |
| `FOREST_BOAR_CHANCE` | `4.0` |  | :406 |
| `CALLSIGN_PRICE` | `500` |  | :408 |
| `PILOT_BASE_HP` | `100` |  | :410 |
| `FOREST_BOAR_HP` | `40` |  | :415 |
| `FOREST_BOAR_DMG` | `(4, 7)` |  | :416 |
| `FOREST_BOAR_DODGE` | `15` |  | :417 |
| `FOREST_BOAR_LOSS_AP` | `10` |  | :419 |
| `FOREST_BOAR_LOOT` | `[('Мясо кабана', 50), ('Шкура кабана', 20), ('Клык кабана', 10), ('', 20)]` |  | :421 |
| `FOREST_WHITE_WOLF_HP` | `120` |  | :433 |
| `FOREST_WHITE_WOLF_DMG` | `(7, 12)` |  | :434 |
| `FOREST_WHITE_WOLF_DODGE` | `20` |  | :435 |
| `FOREST_WHITE_WOLF_LOSS_AP` | `15` |  | :437 |
| `FOREST_WHITE_WOLF_CHANCE` | `2.0` |  | :438 |
| `FOREST_WHITE_WOLF_PITY_TARGET` | `36` |  | :441 |
| `FOREST_WHITE_WOLF_BLEED_CHANCE` | `30` |  | :443 |
| `FOREST_WHITE_WOLF_BLEED_DMG` | `3` |  | :444 |
| `FOREST_WHITE_WOLF_AUTOWIN_HP` | `20` |  | :446 |
| `FOREST_WHITE_WOLF_SMALL_BLESSING` | `'внимание севера'` |  | :448 |
| `FOREST_WHITE_WOLF_BIG_BLESSING` | `'благословение севера'` |  | :449 |
| `FOREST_BOAR_SEED` | `{'key': 'boar', 'spot': 'forest', 'name': 'Дикий кабан', 'hp': FOREST_BOAR_HP, 'dmg_min': FOREST_BOAR_DMG[0], 'dmg_max': FOREST_BOAR_DMG[1], 'dodge': FOREST_BOAR_DODGE, 'loss_ap': FOREST_BOAR_LOSS_…` |  | :456 |
| `FOREST_WHITE_WOLF_SEED` | `{'key': 'white_wolf', 'spot': 'forest', 'name': 'Белый Волк Севера', 'hp': FOREST_WHITE_WOLF_HP, 'dmg_min': FOREST_WHITE_WOLF_DMG[0], 'dmg_max': FOREST_WHITE_WOLF_DMG[1], 'dodge': FOREST_WHITE_WOLF…` |  | :481 |
| `MOLLUSK_SEED` | `{'key': 'mollusk', 'spot': 'reservoir', 'name': 'Мутировавший моллюск', 'hp': 24, 'dmg_min': 5, 'dmg_max': 9, 'dodge': 20, 'loss_ap': 12, 'chance': 4, 'pity_target': 0, 'reward_nm': 0, 'photo_key':…` |  | :509 |
| `MOLLUSK_ITEM_SEEDS` | `[('Мясо моллюска', 'Плотное мясо мутировавшего моллюска. В сыром виде есть нельзя — прожарь на кухне.', 120, 60, 3, 'resource', 0), ('Жемчужина', 'Редчайшая жемчужина из раковины мутировавшего молл…` |  | :532 |
| `MOLLUSK_ENEMY_DROPS` | `('Мясо моллюска', 'Жемчужина')` |  | :547 |
| `MINE_AP_COST` | `12` | стоимость одной попытки добычи | :556 |
| `MINE_BASE_CHANCE` | `30` | базовый шанс успеха без бонуса кирки | :557 |
| `MINE_PICKAXE_BONUS_PER_RANK` | `15` | надбавка к шансу за ступень кирки (ранг 1 → +15%) | :558 |
| `MINE_CHANCE_CAP` | `90` | потолок шанса успеха | :559 |
| `MINE_RESULT_DELAY` | `(7, 15)` | результат добычи через 7–15 секунд | :560 |
| `MINE_REQUIRED_STATUS` | `'pilot1'` | вход в копь — с «Пилота 1 класса» | :561 |
| `MINE_GEM_CAP` | `1` | из самоцветов за бой выпадает не больше одного | :562 |
| `MINE_PICKAXE_NAME` | `'Кирка'` |  | :563 |
| `MINE_ORE_NAME` | `'Железная руда'` |  | :564 |
| `MINE_BAT_KEY` | `'bat'` |  | :567 |
| `MINE_BAT_SPOT` | `'iron'` |  | :568 |
| `MINE_BAT_CHANCE` | `7.0` |  | :569 |
| `MINE_BAT_PITY_TARGET` | `12` |  | :570 |
| `MINE_BAT_SEED` | `{'key': MINE_BAT_KEY, 'spot': MINE_BAT_SPOT, 'name': 'Летучая мышь', 'hp': 22, 'dmg_min': 3, 'dmg_max': 7, 'dodge': 35, 'loss_ap': 15, 'chance': MINE_BAT_CHANCE, 'pity_target': MINE_BAT_PITY_TARGET…` |  | :575 |
| `MINE_ITEM_SEEDS` | `[(MINE_PICKAXE_NAME, 'Простая кирка шахтёра: без неё в штольню не сунешься, а с ней порода поддаётся легче. Повышает шанс успешной добычи руды.', 300, 150, 1, 'mining', 0), (MINE_ORE_NAME, 'Кусок ж…` |  | :601 |
| `MINE_SHOP_ITEMS` | `(MINE_PICKAXE_NAME,)` |  | :622 |
| `MINE_ENEMY_DROPS` | `('Изумруд', 'Рубин', 'Сапфир')` |  | :625 |
| `ON_HIT_EFFECTS` | `{'bleed': {'emoji': '🩸', 'title': 'Кровотечение', 'until_battle_end': True, 'params': (('chance', 'Шанс наложить, %', 'percent'), ('dmg', 'Урон, HP за ход', 'int')), 'hint': 'Раны сочатся кровью ка…` |  | :634 |
| `ON_HIT_KIND_ORDER` | `('bleed', 'poison', 'frostbite', 'state')` |  | :678 |
| `ON_HIT_STATE_ROUNDS` | `{'оглушён': 3, 'ослеплён': 4}` |  | :680 |
| `LOGGING_AP_COST` | `12` | стоимость одной попытки рубки | :686 |
| `LOGGING_BASE_CHANCE` | `35` | базовый шанс успеха без бонуса топора | :687 |
| `LOGGING_AXE_BONUS_PER_RANK` | `15` | надбавка к шансу за ступень топора | :688 |
| `LOGGING_CHANCE_CAP` | `90` | потолок шанса успеха | :689 |
| `LOGGING_AXE_SLIP_CHANCE` | `2.5` | шанс, что топор отскочит пилоту в плечо, % | :690 |
| `LOGGING_RESULT_DELAY` | `(7, 15)` | результат рубки через 7–15 секунд | :691 |
| `LOGGING_AXE_NAME` | `'Топор'` |  | :692 |
| `LOGGING_WOOD_NAME` | `'Бревна'` |  | :693 |
| `LOGGING_PLANK_NAME` | `'Доска'` |  | :699 |
| `LOGGING_FIREWOOD_NAME` | `'Пак дров'` |  | :700 |
| `LOGGING_PLANK_YIELD` | `3` | досок из одного бревна | :701 |
| `LOGGING_PLANK_FEE` | `15` | НМ за распил одного бревна (в казну) | :702 |
| `LOGGING_FIREWOOD_YIELD` | `3` | паков дров из одного бревна | :703 |
| `LOGGING_FIREWOOD_AP_COST` | `4` | ОД за рубку дров из одного бревна | :704 |
| `LOGGING_SNAKE_KEY` | `'snake'` |  | :708 |
| `LOGGING_OWL_KEY` | `'owl'` |  | :709 |
| `LOGGING_SPOT` | `'logging'` |  | :710 |
| `LOGGING_SNAKE_CHANCE` | `8.0` |  | :711 |
| `LOGGING_SNAKE_PITY_TARGET` | `10` |  | :712 |
| `LOGGING_OWL_CHANCE` | `3.0` |  | :713 |
| `LOGGING_OWL_PITY_TARGET` | `24` |  | :714 |
| `LOGGING_SNAKE_POISON_CHANCE` | `30` |  | :716 |
| `LOGGING_SNAKE_POISON_DMG` | `2` |  | :717 |
| `LOGGING_OWL_FLEE_HP` | `20` |  | :721 |
| `LOGGING_OWL_BLIND_CHANCE` | `30` |  | :722 |
| `LOGGING_OWL_BLIND_ROUNDS` | `4` |  | :723 |
| `LOGGING_SNAKE_SEED` | `{'key': LOGGING_SNAKE_KEY, 'spot': LOGGING_SPOT, 'name': 'Лесная змея', 'hp': 30, 'dmg_min': 4, 'dmg_max': 8, 'dodge': 25, 'loss_ap': 10, 'chance': LOGGING_SNAKE_CHANCE, 'pity_target': LOGGING_SNAK…` |  | :727 |
| `LOGGING_OWL_SEED` | `{'key': LOGGING_OWL_KEY, 'spot': LOGGING_SPOT, 'name': 'Неясыть', 'hp': 90, 'dmg_min': 7, 'dmg_max': 12, 'dodge': 30, 'loss_ap': 15, 'chance': LOGGING_OWL_CHANCE, 'pity_target': LOGGING_OWL_PITY_TA…` |  | :757 |
| `LOGGING_ITEM_SEEDS` | `[(LOGGING_AXE_NAME, 'Крепкий лесорубский топор: без него к срубам не подпустят. Повышает шанс успешной рубки деревьев.', 300, 150, 1, 'mining', 0), (LOGGING_WOOD_NAME, 'Свежие срубленные брёвна из …` |  | :789 |
| `LOGGING_SHOP_ITEMS` | `(LOGGING_AXE_NAME,)` |  | :823 |
| `LOGGING_ENEMY_DROPS` | `('Змеиная кожа', 'Змеиный яд', 'Совиное перо')` |  | :826 |
| `LOGGING_MARKET_RESOURCES` | `(LOGGING_PLANK_NAME, LOGGING_FIREWOOD_NAME)` |  | :829 |
| `REPORT_DAILY_LIMIT` | `3` |  | :831 |
| `REPORT_AUTO_APPROVE_TROOPS` | `100` |  | :832 |
| `NEWS_PUBLISH_BONUS` | `10` |  | :836 |
| `NEWS_PUBLISH_CAP` | `28` |  | :837 |
| `ROLE_SALARY_PAY_DAY` | `28` |  | :840 |
| `REPORT_DAILY_PAY_CAP` | `4000` |  | :845 |
| `REPORT_MAX_TROOPS` | `1000000` |  | :846 |
| `REPORT_MAX_REGION` | `38` | 0 = Столица, 1..38 регионы | :847 |
| `WALL_TEXT_MAX_LEN` | `40` | лимит символов на одно изречение | :850 |
| `WALL_FREE_PER_DAY` | `2` | бесплатных сообщений в сутки | :851 |
| `WALL_PAID_STEPS` | `[(3, 30), (3, 90), (3, 200)]` | далее платные ступени: (кол-во, цена НМ) | :852 |
| `WALL_REVIEW_TOTAL` | `11` | максимум сообщений в сутки (2 + 3+3+3) | :857 |
| `WALL_PAGE_SIZE` | `5` | постов на страницу стены | :858 |
| `WALL_ARCHIVE_PAGE_SIZE` | `8` | записей архива стены на страницу списка | :859 |
| `REPORT_ARCHIVE_PAGE` | `8` | отчётов на страницу архива МВД и в «Моих отчётах» | :862 |
| `POLL_MAX_DAYS` | `10` | максимум дней, сколько живёт опрос. Не закрыл | :865 |
| `POLL_VISIBLE` | `4` | сколько новейших опросов висит в меню голосования. | :868 |
| `POLL_ARCHIVE_DAYS_PER_PAGE` | `5` | дней (дат) архива опросов на страницу списка | :871 |
| `POLL_ARCHIVE_PER_DAY` | `6` | опросов под одним заголовком-днём | :872 |
| `REP_SPEECH_MAX_LEN` | `100` | лимит символов одного обращения | :875 |
| `REP_SPEECH_PER_DAY` | `2` | обращений в сутки от представителя | :876 |
| `AUTO_PROMOTE_MAX_TROOPS` | `4040` |  | :881 |

## Буклет туриста

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `TOURIST_BOOKLET_NAME` | `'Буклет туриста'` |  | :24 |

## Суточный цикл Нордхайма

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `REPORT_DAY_START_HOUR` | `10` |  | :99 |

## Дом Дуэлей (PvP-арена)

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `DUEL_ZONES` | `('head', 'body', 'hands', 'legs')` |  | :196 |

## Рынок: слоты продажи

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `MARKET_BASE_SLOTS` | `1` | слоты без лицензии | :271 |

## Налог на недвижимость (НМ/мес)

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `HOUSING_TAX` | `{'municipal': 0, 'studio': 20, 'apartment': 35, 'improved': 60, 'mansion': 100}` |  | :277 |

## Банк: лимит счёта туриста (НМ)

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `TOURIST_BALANCE_LIMIT` | `200` |  | :287 |

## Данж: лимит хила (количество применений за забег)

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `DUNGEON_HEAL_SOFT_LIMIT` | `6` | после этого — ×2/3 | :290 |

## Сброс протухших забегов подземелья

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `DUNGEON_RUN_STALE_SEC` | `3600` |  | :299 |

## Данж: побег и дымовая шашка

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `ESCAPE_BASE_CHANCE` | `25` |  | :307 |

