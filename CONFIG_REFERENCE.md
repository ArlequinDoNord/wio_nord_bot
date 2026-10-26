# Справочник констант `config.py`

> **Сгенерировано** `tools/export_config.py`. Перегенерация:
> `.venv\Scripts\python.exe tools/export_config.py`.
>
> Все модульные константы `config.py`, сгруппированные по секциям
> (комментариям-разделителям `# ── … ──`). Длинные значения усечены `…`;
> точное значение — в `config.py` по строке из первой колонки.

Всего констант: **212**; разделов: **10**.

## Без раздела

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `VERSION` | `'0.38.8'` |  | :16 |
| `VERSION_NOTES` | `'В штабе стали понятнее объяснять, что ждут от бумаг…'` |  | :17 |
| `PREV_VERSION` | `'0.38.7'` |  | :19 |
| `PREV_VERSION_NOTES` | `'В клановых угодьях снова шум и суета…'` |  | :20 |
| `TOURIST_BOOKLET_DESCRIPTION` | `'Печатная карта Нордхайма для гостей города. Просматривай превью городских локаций — и отмечай их в буклете. Собери все 9 и получи награду от командования.'` |  | :24 |
| `TOURIST_BOOKLET_PRICE` | `1` |  | :27 |
| `TOURIST_BOOKLET_SELL_PRICE` | `0` | буклет не продаётся (иначе чек-лист теряется) | :28 |
| `TOURIST_BOOKLET_AWARD` | `'Опытный турист'` |  | :29 |
| `TOURIST_BOOKLET_AWARD_EMOJI` | `'🧭'` |  | :30 |
| `TOURIST_BOOKLET_AWARD_DESCRIPTION` | `'Посетил все городские локации Нордхайма по «Буклету туриста». Знак почётного гостя города.'` |  | :31 |
| `TOURIST_BOOKLET_REWARD_NM` | `20` |  | :33 |
| `TOURIST_BOOKLET_REWARD_TX` | `'booklet'` |  | :34 |
| `TOURIST_BOOKLET_LOCATIONS` | `('townhall', 'library', 'park', 'gossmi', 'bank', 'kvp', 'hq', 'contracts', 'nii')` |  | :37 |
| `CLAN_HALL_ENABLED` | `False` |  | :46 |
| `CLAN_BUILDING_TYPES` | `{'house': {'name': 'Дом Клана', 'slots': 2, 'max_level': 2, 'days': 2, 'price_nm': 3000, 'required': {'Доска': 60, 'Бревна': 20, 'Железная руда': 15}}, 'manor': {'name': 'Клановое поместье', 'slots…` |  | :48 |
| `CLAN_BUILDING_NO_RESOURCES_MULT` | `2` |  | :63 |
| `CLAN_EXPANSION_TYPES` | `('kitchen', 'workbench', 'shower', 'garden', 'library', 'shop')` |  | :65 |
| `CLAN_EXPANSION_INFO` | `{'kitchen': {'name': 'Кухня', 'icon': '🍳', 'desc': 'Готовка по выученным рецептам; уровень задаёт доступные блюда.'}, 'workbench': {'name': 'Крафтовый стол', 'icon': '🛠', 'desc': 'Крафт снаряжения …` |  | :67 |
| `CLAN_EXPANSION_UPGRADE` | `{2: {'nm': 1500, 'required': {'Доска': 20, 'Железная руда': 10}}, 3: {'nm': 4000, 'required': {'Доска': 50, 'Железная руда': 30}}, 4: {'nm': 9000, 'required': {'Доска': 100, 'Железная руда': 60}}}` |  | :82 |
| `CLAN_GARDEN_PLOTS` | `{1: 2, 2: 3, 3: 4, 4: 6}` |  | :88 |
| `CLAN_SHOP_DAILY_LIMIT` | `3` |  | :89 |
| `CLAN_SHOP_DISCOUNT` | `10` |  | :90 |
| `BOT_TOKEN` | `os.getenv('BOT_TOKEN')` |  | :92 |
| `ADMIN_IDS` | `[int(x) for x in os.getenv('ADMIN_IDS', '').split(',') if x.strip()]` |  | :93 |
| `_news_raw` | `os.getenv('NEWS_CHAT_ID', '').strip()` |  | :96 |
| `NEWS_CHAT_ID` | `int(_news_raw) if _news_raw.lstrip('-').isdigit() else None` |  | :97 |
| `DB_PATH` | `os.getenv('DATABASE_PATH', 'database/nordmark.db')` |  | :100 |
| `FSM_STORAGE_PATH` | `os.getenv('FSM_STORAGE_PATH', '').strip() or os.path.join(os.path.dirname(os.path.abspath(DB_PATH)), 'fsm')` |  | :109 |
| `REPORT_DAY_START_MINUTE` | `0` |  | :119 |
| `RANKS` | `[('Рекрут', 0), ('Рядовой', 100), ('Ефрейтор', 350), ('Капрал', 500), ('Сержант', 850), ('Старший Сержант', 1500), ('Лейтенант', 2500), ('Старший Лейтенант', 4040), ('Капитан', 6000), ('Майор', 850…` |  | :121 |
| `MAX_SELF_RANK_TROOPS` | `4040` |  | :142 |
| `AUTO_RANK_NAMES` | `('Рекрут', 'Рядовой', 'Ефрейтор', 'Капрал', 'Сержант', 'Старший Сержант', 'Лейтенант', 'Старший Лейтенант')` |  | :145 |
| `AWARD_MAX_SHOP_DISCOUNT` | `40` |  | :152 |
| `AWARD_MIN_REPORT_TAX` | `5` |  | :153 |
| `RANK_STATUS_TAGS` | `{'Ефрейтор': 'pilot2', 'Старший Сержант': 'pilot1', 'Старший Лейтенант': 'veteran', 'Майор': 'master_pilot', 'Полковник': 'ace'}` |  | :155 |
| `LEGIONER_ACCESS_CAP_ORDER` | `5` |  | :168 |
| `RANK_DAMAGE_TIERS` | `{'ace': (4, 8), 'master_pilot': (3, 5), 'veteran': (2, 4), 'pilot1': (1, 3), 'pilot2': (1, 2), 'recruit': (1, 1), 'tourist': (0, 1)}` |  | :174 |
| `RANK_CRIT_CHANCE` | `{'ace': 7.5, 'master_pilot': 6.0, 'veteran': 4.5, 'pilot1': 3.0, 'pilot2': 1.5, 'recruit': 0.0, 'tourist': 0.0}` |  | :192 |
| `PILOT_CRIT_MULT` | `1.4` |  | :206 |
| `PILOT_NO_WEAPON_DMG` | `(1, 1)` |  | :209 |
| `DUEL_ZONE_LABELS` | `{'head': 'Голова', 'body': 'Тело', 'hands': 'Руки', 'legs': 'Ноги'}` |  | :216 |
| `DUEL_ZONE_EMOJI` | `{'head': '🧠', 'body': '🫀', 'hands': '✊', 'legs': '🦵'}` |  | :222 |
| `DUEL_AP_COST` | `15` | списывается с обоих при старте боя | :228 |
| `DUEL_RATING_WIN` | `2` | рейтинг за победу | :229 |
| `DUEL_RATING_LOSS` | `-3` | рейтинг за поражение | :230 |
| `DUEL_RATING_DRAW` | `0` | рейтинг за ничью | :231 |
| `DUEL_RATING_FORFEIT` | `-1` | рейтинг тому, кто покинул бой («Покинуть дуэль») | :232 |
| `DUEL_RATING_FORFEIT_WIN` | `1` | рейтинг сопернику, если противник покинул бой (меньше чистой победы) | :233 |
| `DUEL_MIN_DAMAGE` | `1` | минимум урона за попавший (не уклонённый) удар | :234 |
| `DUEL_GUARD_REDUCTION` | `0.5` | доля урона, остающаяся при угаданной зоне защиты | :235 |
| `DUEL_HEAL_BETWEEN` | `0` | восстановление HP между раундами (пока нет) | :236 |
| `DUEL_CHALLENGE_TIMEOUT_SEC` | `120` | сколько живёт неотвеченный вызов | :237 |
| `DUEL_STALE_SEC` | `1800` | зависшая дуэль авто-завершается как void | :238 |
| `DUEL_GLOVES_NAME` | `'Дуэльные перчатки'` |  | :239 |
| `DUEL_GLOVES_DAMAGE` | `7` |  | :240 |
| `DUEL_GLOVES_PRICE` | `200` |  | :241 |
| `DUEL_GLOVES_SELL` | `100` |  | :242 |
| `DUEL_CLUB_CARD_NAME` | `'Клубная карта «Дом Дуэлей»'` |  | :243 |
| `DUEL_CLUB_CARD_PRICE` | `150` |  | :244 |
| `DUEL_CLUB_CARD_SELL` | `75` |  | :245 |
| `DUEL_CLUB_CARD_DAYS` | `30` |  | :246 |
| `DUEL_ACCESS_TAG` | `'pilot2'` |  | :249 |
| `RARITY_LEVELS` | `{1: 'Обычный', 2: 'Качественный', 3: 'Редкий', 4: 'Шедевр', 5: 'Легендарный'}` |  | :251 |
| `RARITY_EMOJI` | `{1: '⬜', 2: '🟩', 3: '🟦', 4: '🟪', 5: '🟧'}` |  | :259 |
| `ITEM_CATEGORIES` | `{'weapon': 'Оружие', 'consumable': 'Расходники', 'building': 'Недвижимость', 'housing': 'Жильё', 'furniture': 'Мебель и расширения', 'seeds': 'Семена', 'equipment': 'Одежда', 'resource': 'Ресурсы',…` |  | :267 |
| `MARKET_LICENSE_SLOTS` | `2` | доп. слоты при активной лицензии | :291 |
| `MARKET_LICENSE_DAYS` | `30` | срок действия лицензии (дней) | :292 |
| `MARKET_LICENSE_PRICE` | `500` | цена лицензии в НМ | :293 |
| `DUNGEON_HEAL_HARD_LIMIT` | `10` | после этого — ×1/2 | :310 |
| `DUNGEON_HEAL_SOFT_MULT` | `2 / 3` |  | :311 |
| `DUNGEON_HEAL_HARD_MULT` | `1 / 2` |  | :312 |
| `ESCAPE_HP_BONUS` | `20` |  | :327 |
| `DUNGEON_SMOKE_ESCAPE` | `95` |  | :328 |
| `DUNGEON_SMOKE_MAX` | `2` |  | :329 |
| `DUNGEON_ESCAPE_DRUNK_MULT` | `0.5` |  | :332 |
| `AP_MAX` | `150` |  | :334 |
| `AP_DAILY_RECOVERY` | `100` |  | :335 |
| `AP_BONUS_FROM_CONSUMABLE` | `50` |  | :336 |
| `AP_DAILY_RESTORE_LIMIT` | `150` |  | :341 |
| `AP_EXHAUSTED_MINUTES` | `2880` | 2 суток | :342 |
| `AP_EXHAUSTED_DAILY_RECOVERY` | `75` | суточное восстановление в «истощении» | :343 |
| `AP_EXHAUSTED_MAX_AP` | `90` | максимум ОД в «истощении» | :344 |
| `SEAWEED_DAILY_LIMIT` | `6` |  | :347 |
| `DIGESTIVE_UPSET_MINUTES` | `1440` | 24 часа | :348 |
| `ALCOHOL_WEAK_DRUNK_LIMIT` | `3` |  | :353 |
| `ALCOHOL_WEAK_VERY_DRUNK_LIMIT` | `6` |  | :354 |
| `ALCOHOL_STRONG_DRUNK_LIMIT` | `1` |  | :356 |
| `ALCOHOL_STRONG_VERY_DRUNK_LIMIT` | `2` |  | :357 |
| `DRUNK_MINUTES` | `60` |  | :358 |
| `VERY_DRUNK_MINUTES` | `360` | 6 часов | :359 |
| `DRINK_EFFECT_LABELS` | `{'alcohol_weak': '🍺 Слабоалкогольный: 3 шт/сутки — «пьян», 6 — «очень пьян»', 'alcohol_strong': '🥃 Крепкий алкоголь: 1 шт — «пьян», 2 — «очень пьян»', 'indigestion': '🤢 Вызывает «несварение» на сут…` |  | :362 |
| `SPECIAL_DEPT_CODE_MIN_LEN` | `4` |  | :373 |
| `SPECIAL_DEPT_CODE_MAX_LEN` | `8` |  | :374 |
| `SPECIAL_DEPT_ATTEMPTS_LIMIT` | `3` | ошибок кода подряд | :375 |
| `SPECIAL_DEPT_BLOCK_MINUTES` | `1440` | бан на 24 часа после 3 ошибок | :376 |
| `FISH_AP_COST` | `3` | стоимость одного заброса удочки | :379 |
| `RESERVOIR_AP_COST` | `5` |  | :384 |
| `FISH_WEIGHTS` | `[{'key': 'small', 'label': 'Мелкая', 'mult': 1.0, 'chance': 40}, {'key': 'medium', 'label': 'Средняя', 'mult': 1.15, 'chance': 40}, {'key': 'large', 'label': 'Большая', 'mult': 1.25, 'chance': 20}]` |  | :389 |
| `FISH_TREASURY_SALE_MULT` | `0.5` |  | :397 |
| `FISH_TREASURY_DAILY_LIMIT` | `300` |  | :402 |
| `FOREST_AP_COST` | `4` | запасной цена поиска, если у зоны нет ap_cost в БД | :405 |
| `FOREST_RESULT_DELAY` | `(5, 10)` | результат поиска через 5–10 секунд | :408 |
| `FOREST_SOLD_DAILY_LIMIT` | `250` |  | :413 |
| `FOREST_ALLOW_TOURISTS` | `False` |  | :418 |
| `FOREST_BOAR_PITY_TARGET` | `12` |  | :421 |
| `FOREST_BOAR_CHANCE` | `4.0` |  | :425 |
| `CALLSIGN_PRICE` | `500` |  | :427 |
| `PILOT_BASE_HP` | `100` |  | :429 |
| `FOREST_BOAR_HP` | `40` |  | :434 |
| `FOREST_BOAR_DMG` | `(4, 7)` |  | :435 |
| `FOREST_BOAR_DODGE` | `15` |  | :436 |
| `FOREST_BOAR_LOSS_AP` | `10` |  | :438 |
| `FOREST_BOAR_LOOT` | `[('Мясо кабана', 50), ('Шкура кабана', 20), ('Клык кабана', 10), ('', 20)]` |  | :440 |
| `FOREST_WHITE_WOLF_HP` | `120` |  | :452 |
| `FOREST_WHITE_WOLF_DMG` | `(7, 12)` |  | :453 |
| `FOREST_WHITE_WOLF_DODGE` | `20` |  | :454 |
| `FOREST_WHITE_WOLF_LOSS_AP` | `15` |  | :456 |
| `FOREST_WHITE_WOLF_CHANCE` | `2.0` |  | :457 |
| `FOREST_WHITE_WOLF_PITY_TARGET` | `36` |  | :460 |
| `FOREST_WHITE_WOLF_BLEED_CHANCE` | `30` |  | :462 |
| `FOREST_WHITE_WOLF_BLEED_DMG` | `3` |  | :463 |
| `FOREST_WHITE_WOLF_AUTOWIN_HP` | `20` |  | :465 |
| `FOREST_WHITE_WOLF_SMALL_BLESSING` | `'внимание севера'` |  | :467 |
| `FOREST_WHITE_WOLF_BIG_BLESSING` | `'благословение севера'` |  | :468 |
| `FOREST_BOAR_SEED` | `{'key': 'boar', 'spot': 'forest', 'name': 'Дикий кабан', 'hp': FOREST_BOAR_HP, 'dmg_min': FOREST_BOAR_DMG[0], 'dmg_max': FOREST_BOAR_DMG[1], 'dodge': FOREST_BOAR_DODGE, 'loss_ap': FOREST_BOAR_LOSS_…` |  | :475 |
| `FOREST_WHITE_WOLF_SEED` | `{'key': 'white_wolf', 'spot': 'forest', 'name': 'Белый Волк Севера', 'hp': FOREST_WHITE_WOLF_HP, 'dmg_min': FOREST_WHITE_WOLF_DMG[0], 'dmg_max': FOREST_WHITE_WOLF_DMG[1], 'dodge': FOREST_WHITE_WOLF…` |  | :500 |
| `MOLLUSK_SEED` | `{'key': 'mollusk', 'spot': 'reservoir', 'name': 'Мутировавший моллюск', 'hp': 24, 'dmg_min': 5, 'dmg_max': 9, 'dodge': 20, 'loss_ap': 12, 'chance': 4, 'pity_target': 0, 'reward_nm': 0, 'photo_key':…` |  | :528 |
| `MOLLUSK_ITEM_SEEDS` | `[('Мясо моллюска', 'Плотное мясо мутировавшего моллюска. В сыром виде есть нельзя — прожарь на кухне.', 120, 60, 3, 'resource', 0), ('Жемчужина', 'Редчайшая жемчужина из раковины мутировавшего молл…` |  | :551 |
| `MOLLUSK_ENEMY_DROPS` | `('Мясо моллюска', 'Жемчужина')` |  | :566 |
| `MINE_AP_COST` | `12` | стоимость одной попытки добычи | :575 |
| `MINE_BASE_CHANCE` | `30` | базовый шанс успеха без бонуса кирки | :576 |
| `MINE_PICKAXE_BONUS_PER_RANK` | `15` | надбавка к шансу за ступень кирки (ранг 1 → +15%) | :577 |
| `MINE_CHANCE_CAP` | `90` | потолок шанса успеха | :578 |
| `MINE_RESULT_DELAY` | `(7, 15)` | результат добычи через 7–15 секунд | :579 |
| `MINE_REQUIRED_STATUS` | `'pilot1'` | вход в копь — с «Пилота 1 класса» | :580 |
| `MINE_GEM_CAP` | `1` | из самоцветов за бой выпадает не больше одного | :581 |
| `MINE_PICKAXE_NAME` | `'Кирка'` |  | :582 |
| `MINE_ORE_NAME` | `'Железная руда'` |  | :583 |
| `MINE_BAT_KEY` | `'bat'` |  | :586 |
| `MINE_BAT_SPOT` | `'iron'` |  | :587 |
| `MINE_BAT_CHANCE` | `7.0` |  | :588 |
| `MINE_BAT_PITY_TARGET` | `12` |  | :589 |
| `MINE_BAT_SEED` | `{'key': MINE_BAT_KEY, 'spot': MINE_BAT_SPOT, 'name': 'Летучая мышь', 'hp': 22, 'dmg_min': 3, 'dmg_max': 7, 'dodge': 35, 'loss_ap': 15, 'chance': MINE_BAT_CHANCE, 'pity_target': MINE_BAT_PITY_TARGET…` |  | :594 |
| `MINE_ITEM_SEEDS` | `[(MINE_PICKAXE_NAME, 'Простая кирка шахтёра: без неё в штольню не сунешься, а с ней порода поддаётся легче. Повышает шанс успешной добычи руды.', 300, 150, 1, 'mining', 0), (MINE_ORE_NAME, 'Кусок ж…` |  | :620 |
| `MINE_SHOP_ITEMS` | `(MINE_PICKAXE_NAME,)` |  | :641 |
| `MINE_ENEMY_DROPS` | `('Изумруд', 'Рубин', 'Сапфир')` |  | :644 |
| `ON_HIT_EFFECTS` | `{'bleed': {'emoji': '🩸', 'title': 'Кровотечение', 'until_battle_end': True, 'params': (('chance', 'Шанс наложить, %', 'percent'), ('dmg', 'Урон, HP за ход', 'int')), 'hint': 'Раны сочатся кровью ка…` |  | :653 |
| `ON_HIT_KIND_ORDER` | `('bleed', 'poison', 'frostbite', 'state')` |  | :697 |
| `ON_HIT_STATE_ROUNDS` | `{'оглушён': 3, 'ослеплён': 4}` |  | :699 |
| `LOGGING_AP_COST` | `12` | стоимость одной попытки рубки | :705 |
| `LOGGING_BASE_CHANCE` | `35` | базовый шанс успеха без бонуса топора | :706 |
| `LOGGING_AXE_BONUS_PER_RANK` | `15` | надбавка к шансу за ступень топора | :707 |
| `LOGGING_CHANCE_CAP` | `90` | потолок шанса успеха | :708 |
| `LOGGING_AXE_SLIP_CHANCE` | `2.5` | шанс, что топор отскочит пилоту в плечо, % | :709 |
| `LOGGING_RESULT_DELAY` | `(7, 15)` | результат рубки через 7–15 секунд | :710 |
| `LOGGING_AXE_NAME` | `'Топор'` |  | :711 |
| `LOGGING_WOOD_NAME` | `'Бревна'` |  | :712 |
| `LOGGING_PLANK_NAME` | `'Доска'` |  | :718 |
| `LOGGING_FIREWOOD_NAME` | `'Пак дров'` |  | :719 |
| `LOGGING_PLANK_YIELD` | `3` | досок из одного бревна | :720 |
| `LOGGING_PLANK_FEE` | `15` | НМ за распил одного бревна (в казну) | :721 |
| `LOGGING_FIREWOOD_YIELD` | `3` | паков дров из одного бревна | :722 |
| `LOGGING_FIREWOOD_AP_COST` | `4` | ОД за рубку дров из одного бревна | :723 |
| `LOGGING_SNAKE_KEY` | `'snake'` |  | :727 |
| `LOGGING_OWL_KEY` | `'owl'` |  | :728 |
| `LOGGING_SPOT` | `'logging'` |  | :729 |
| `LOGGING_SNAKE_CHANCE` | `8.0` |  | :730 |
| `LOGGING_SNAKE_PITY_TARGET` | `10` |  | :731 |
| `LOGGING_OWL_CHANCE` | `3.0` |  | :732 |
| `LOGGING_OWL_PITY_TARGET` | `24` |  | :733 |
| `LOGGING_SNAKE_POISON_CHANCE` | `30` |  | :735 |
| `LOGGING_SNAKE_POISON_DMG` | `2` |  | :736 |
| `LOGGING_OWL_FLEE_HP` | `20` |  | :740 |
| `LOGGING_OWL_BLIND_CHANCE` | `30` |  | :741 |
| `LOGGING_OWL_BLIND_ROUNDS` | `4` |  | :742 |
| `LOGGING_SNAKE_SEED` | `{'key': LOGGING_SNAKE_KEY, 'spot': LOGGING_SPOT, 'name': 'Лесная змея', 'hp': 30, 'dmg_min': 4, 'dmg_max': 8, 'dodge': 25, 'loss_ap': 10, 'chance': LOGGING_SNAKE_CHANCE, 'pity_target': LOGGING_SNAK…` |  | :746 |
| `LOGGING_OWL_SEED` | `{'key': LOGGING_OWL_KEY, 'spot': LOGGING_SPOT, 'name': 'Неясыть', 'hp': 90, 'dmg_min': 7, 'dmg_max': 12, 'dodge': 30, 'loss_ap': 15, 'chance': LOGGING_OWL_CHANCE, 'pity_target': LOGGING_OWL_PITY_TA…` |  | :776 |
| `LOGGING_ITEM_SEEDS` | `[(LOGGING_AXE_NAME, 'Крепкий лесорубский топор: без него к срубам не подпустят. Повышает шанс успешной рубки деревьев.', 300, 150, 1, 'mining', 0), (LOGGING_WOOD_NAME, 'Свежие срубленные брёвна из …` |  | :808 |
| `LOGGING_SHOP_ITEMS` | `(LOGGING_AXE_NAME,)` |  | :842 |
| `LOGGING_ENEMY_DROPS` | `('Змеиная кожа', 'Змеиный яд', 'Совиное перо')` |  | :845 |
| `LOGGING_MARKET_RESOURCES` | `(LOGGING_PLANK_NAME, LOGGING_FIREWOOD_NAME)` |  | :848 |
| `REPORT_DAILY_LIMIT` | `3` |  | :850 |
| `REPORT_AUTO_APPROVE_TROOPS` | `100` |  | :851 |
| `NEWS_PUBLISH_BONUS` | `10` |  | :855 |
| `NEWS_PUBLISH_CAP` | `28` |  | :856 |
| `ROLE_SALARY_PAY_DAY` | `28` |  | :859 |
| `REPORT_DAILY_PAY_CAP` | `4000` |  | :864 |
| `REPORT_MAX_TROOPS` | `1000000` |  | :865 |
| `REPORT_MAX_REGION` | `38` | 0 = Столица, 1..38 регионы | :866 |
| `WALL_TEXT_MAX_LEN` | `40` | лимит символов на одно изречение | :869 |
| `WALL_FREE_PER_DAY` | `2` | бесплатных сообщений в сутки | :870 |
| `WALL_PAID_STEPS` | `[(3, 30), (3, 90), (3, 200)]` | далее платные ступени: (кол-во, цена НМ) | :871 |
| `WALL_REVIEW_TOTAL` | `11` | максимум сообщений в сутки (2 + 3+3+3) | :876 |
| `WALL_PAGE_SIZE` | `5` | постов на страницу стены | :877 |
| `WALL_ARCHIVE_PAGE_SIZE` | `8` | записей архива стены на страницу списка | :878 |
| `REPORT_ARCHIVE_PAGE` | `8` | отчётов на страницу архива МВД и в «Моих отчётах» | :881 |
| `POLL_MAX_DAYS` | `10` | максимум дней, сколько живёт опрос. Не закрыл | :884 |
| `POLL_VISIBLE` | `4` | сколько новейших опросов висит в меню голосования. | :887 |
| `POLL_ARCHIVE_DAYS_PER_PAGE` | `5` | дней (дат) архива опросов на страницу списка | :890 |
| `POLL_ARCHIVE_PER_DAY` | `6` | опросов под одним заголовком-днём | :891 |
| `REP_SPEECH_MAX_LEN` | `100` | лимит символов одного обращения | :894 |
| `REP_SPEECH_PER_DAY` | `2` | обращений в сутки от представителя | :895 |
| `AUTO_PROMOTE_MAX_TROOPS` | `4040` |  | :900 |

## Буклет туриста

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `TOURIST_BOOKLET_NAME` | `'Буклет туриста'` |  | :23 |

## Суточный цикл Нордхайма

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `REPORT_DAY_START_HOUR` | `10` |  | :118 |

## Дом Дуэлей (PvP-арена)

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `DUEL_ZONES` | `('head', 'body', 'hands', 'legs')` |  | :215 |

## Рынок: слоты продажи

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `MARKET_BASE_SLOTS` | `1` | слоты без лицензии | :290 |

## Налог на недвижимость (НМ/мес)

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `HOUSING_TAX` | `{'municipal': 0, 'studio': 20, 'apartment': 35, 'improved': 60, 'mansion': 100}` |  | :296 |

## Банк: лимит счёта туриста (НМ)

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `TOURIST_BALANCE_LIMIT` | `200` |  | :306 |

## Данж: лимит хила (количество применений за забег)

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `DUNGEON_HEAL_SOFT_LIMIT` | `6` | после этого — ×2/3 | :309 |

## Сброс протухших забегов подземелья

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `DUNGEON_RUN_STALE_SEC` | `3600` |  | :318 |

## Данж: побег и дымовая шашка

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `ESCAPE_BASE_CHANCE` | `25` |  | :326 |

