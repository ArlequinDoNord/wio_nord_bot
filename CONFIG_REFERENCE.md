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
| `VERSION` | `'0.38.9'` |  | :16 |
| `VERSION_NOTES` | `'В клан-холле появились слоты расширений: установка бесплатна, улучшение — за нордмарки и ресурсы.'` |  | :17 |
| `PREV_VERSION` | `'0.38.8'` |  | :20 |
| `PREV_VERSION_NOTES` | `'В штабе стали понятнее объяснять, что ждут от бумаг…'` |  | :21 |
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
| `CLAN_BUILDING_TYPES` | `{'house': {'name': 'Дом Клана', 'slots': 2, 'max_level': 2, 'days': 2, 'price_nm': 3000, 'required': {'Доска': 60, 'Бревна': 20, 'Железная руда': 15}}, 'manor': {'name': 'Клановое поместье', 'slots…` |  | :49 |
| `CLAN_BUILDING_NO_RESOURCES_MULT` | `2` |  | :64 |
| `CLAN_EXPANSION_TYPES` | `('kitchen', 'workbench', 'shower', 'garden', 'library', 'shop')` |  | :66 |
| `CLAN_EXPANSION_INFO` | `{'kitchen': {'name': 'Кухня', 'icon': '🍳', 'desc': 'Готовка по выученным рецептам; уровень задаёт доступные блюда.'}, 'workbench': {'name': 'Крафтовый стол', 'icon': '🛠', 'desc': 'Крафт снаряжения …` |  | :68 |
| `CLAN_EXPANSION_UPGRADE` | `{2: {'nm': 1500, 'required': {'Доска': 20, 'Железная руда': 10}}, 3: {'nm': 4000, 'required': {'Доска': 50, 'Железная руда': 30}}, 4: {'nm': 9000, 'required': {'Доска': 100, 'Железная руда': 60}}}` |  | :83 |
| `CLAN_GARDEN_PLOTS` | `{1: 2, 2: 3, 3: 4, 4: 6}` |  | :89 |
| `CLAN_SHOP_DAILY_LIMIT` | `3` |  | :90 |
| `CLAN_SHOP_DISCOUNT` | `10` |  | :91 |
| `BOT_TOKEN` | `os.getenv('BOT_TOKEN')` |  | :93 |
| `ADMIN_IDS` | `[int(x) for x in os.getenv('ADMIN_IDS', '').split(',') if x.strip()]` |  | :94 |
| `_news_raw` | `os.getenv('NEWS_CHAT_ID', '').strip()` |  | :97 |
| `NEWS_CHAT_ID` | `int(_news_raw) if _news_raw.lstrip('-').isdigit() else None` |  | :98 |
| `DB_PATH` | `os.getenv('DATABASE_PATH', 'database/nordmark.db')` |  | :101 |
| `FSM_STORAGE_PATH` | `os.getenv('FSM_STORAGE_PATH', '').strip() or os.path.join(os.path.dirname(os.path.abspath(DB_PATH)), 'fsm')` |  | :110 |
| `REPORT_DAY_START_MINUTE` | `0` |  | :120 |
| `RANKS` | `[('Рекрут', 0), ('Рядовой', 100), ('Ефрейтор', 350), ('Капрал', 500), ('Сержант', 850), ('Старший Сержант', 1500), ('Лейтенант', 2500), ('Старший Лейтенант', 4040), ('Капитан', 6000), ('Майор', 850…` |  | :122 |
| `MAX_SELF_RANK_TROOPS` | `4040` |  | :143 |
| `AUTO_RANK_NAMES` | `('Рекрут', 'Рядовой', 'Ефрейтор', 'Капрал', 'Сержант', 'Старший Сержант', 'Лейтенант', 'Старший Лейтенант')` |  | :146 |
| `AWARD_MAX_SHOP_DISCOUNT` | `40` |  | :153 |
| `AWARD_MIN_REPORT_TAX` | `5` |  | :154 |
| `RANK_STATUS_TAGS` | `{'Ефрейтор': 'pilot2', 'Старший Сержант': 'pilot1', 'Старший Лейтенант': 'veteran', 'Майор': 'master_pilot', 'Полковник': 'ace'}` |  | :156 |
| `LEGIONER_ACCESS_CAP_ORDER` | `5` |  | :169 |
| `RANK_DAMAGE_TIERS` | `{'ace': (4, 8), 'master_pilot': (3, 5), 'veteran': (2, 4), 'pilot1': (1, 3), 'pilot2': (1, 2), 'recruit': (1, 1), 'tourist': (0, 1)}` |  | :175 |
| `RANK_CRIT_CHANCE` | `{'ace': 7.5, 'master_pilot': 6.0, 'veteran': 4.5, 'pilot1': 3.0, 'pilot2': 1.5, 'recruit': 0.0, 'tourist': 0.0}` |  | :193 |
| `PILOT_CRIT_MULT` | `1.4` |  | :207 |
| `PILOT_NO_WEAPON_DMG` | `(1, 1)` |  | :210 |
| `DUEL_ZONE_LABELS` | `{'head': 'Голова', 'body': 'Тело', 'hands': 'Руки', 'legs': 'Ноги'}` |  | :217 |
| `DUEL_ZONE_EMOJI` | `{'head': '🧠', 'body': '🫀', 'hands': '✊', 'legs': '🦵'}` |  | :223 |
| `DUEL_AP_COST` | `15` | списывается с обоих при старте боя | :229 |
| `DUEL_RATING_WIN` | `2` | рейтинг за победу | :230 |
| `DUEL_RATING_LOSS` | `-3` | рейтинг за поражение | :231 |
| `DUEL_RATING_DRAW` | `0` | рейтинг за ничью | :232 |
| `DUEL_RATING_FORFEIT` | `-1` | рейтинг тому, кто покинул бой («Покинуть дуэль») | :233 |
| `DUEL_RATING_FORFEIT_WIN` | `1` | рейтинг сопернику, если противник покинул бой (меньше чистой победы) | :234 |
| `DUEL_MIN_DAMAGE` | `1` | минимум урона за попавший (не уклонённый) удар | :235 |
| `DUEL_GUARD_REDUCTION` | `0.5` | доля урона, остающаяся при угаданной зоне защиты | :236 |
| `DUEL_HEAL_BETWEEN` | `0` | восстановление HP между раундами (пока нет) | :237 |
| `DUEL_CHALLENGE_TIMEOUT_SEC` | `120` | сколько живёт неотвеченный вызов | :238 |
| `DUEL_STALE_SEC` | `1800` | зависшая дуэль авто-завершается как void | :239 |
| `DUEL_GLOVES_NAME` | `'Дуэльные перчатки'` |  | :240 |
| `DUEL_GLOVES_DAMAGE` | `7` |  | :241 |
| `DUEL_GLOVES_PRICE` | `200` |  | :242 |
| `DUEL_GLOVES_SELL` | `100` |  | :243 |
| `DUEL_CLUB_CARD_NAME` | `'Клубная карта «Дом Дуэлей»'` |  | :244 |
| `DUEL_CLUB_CARD_PRICE` | `150` |  | :245 |
| `DUEL_CLUB_CARD_SELL` | `75` |  | :246 |
| `DUEL_CLUB_CARD_DAYS` | `30` |  | :247 |
| `DUEL_ACCESS_TAG` | `'pilot2'` |  | :250 |
| `RARITY_LEVELS` | `{1: 'Обычный', 2: 'Качественный', 3: 'Редкий', 4: 'Шедевр', 5: 'Легендарный'}` |  | :252 |
| `RARITY_EMOJI` | `{1: '⬜', 2: '🟩', 3: '🟦', 4: '🟪', 5: '🟧'}` |  | :260 |
| `ITEM_CATEGORIES` | `{'weapon': 'Оружие', 'consumable': 'Расходники', 'building': 'Недвижимость', 'housing': 'Жильё', 'furniture': 'Мебель и расширения', 'seeds': 'Семена', 'equipment': 'Одежда', 'resource': 'Ресурсы',…` |  | :268 |
| `MARKET_LICENSE_SLOTS` | `2` | доп. слоты при активной лицензии | :292 |
| `MARKET_LICENSE_DAYS` | `30` | срок действия лицензии (дней) | :293 |
| `MARKET_LICENSE_PRICE` | `500` | цена лицензии в НМ | :294 |
| `DUNGEON_HEAL_HARD_LIMIT` | `10` | после этого — ×1/2 | :311 |
| `DUNGEON_HEAL_SOFT_MULT` | `2 / 3` |  | :312 |
| `DUNGEON_HEAL_HARD_MULT` | `1 / 2` |  | :313 |
| `ESCAPE_HP_BONUS` | `20` |  | :328 |
| `DUNGEON_SMOKE_ESCAPE` | `95` |  | :329 |
| `DUNGEON_SMOKE_MAX` | `2` |  | :330 |
| `DUNGEON_ESCAPE_DRUNK_MULT` | `0.5` |  | :333 |
| `AP_MAX` | `150` |  | :335 |
| `AP_DAILY_RECOVERY` | `100` |  | :336 |
| `AP_BONUS_FROM_CONSUMABLE` | `50` |  | :337 |
| `AP_DAILY_RESTORE_LIMIT` | `150` |  | :342 |
| `AP_EXHAUSTED_MINUTES` | `2880` | 2 суток | :343 |
| `AP_EXHAUSTED_DAILY_RECOVERY` | `75` | суточное восстановление в «истощении» | :344 |
| `AP_EXHAUSTED_MAX_AP` | `90` | максимум ОД в «истощении» | :345 |
| `SEAWEED_DAILY_LIMIT` | `6` |  | :348 |
| `DIGESTIVE_UPSET_MINUTES` | `1440` | 24 часа | :349 |
| `ALCOHOL_WEAK_DRUNK_LIMIT` | `3` |  | :354 |
| `ALCOHOL_WEAK_VERY_DRUNK_LIMIT` | `6` |  | :355 |
| `ALCOHOL_STRONG_DRUNK_LIMIT` | `1` |  | :357 |
| `ALCOHOL_STRONG_VERY_DRUNK_LIMIT` | `2` |  | :358 |
| `DRUNK_MINUTES` | `60` |  | :359 |
| `VERY_DRUNK_MINUTES` | `360` | 6 часов | :360 |
| `DRINK_EFFECT_LABELS` | `{'alcohol_weak': '🍺 Слабоалкогольный: 3 шт/сутки — «пьян», 6 — «очень пьян»', 'alcohol_strong': '🥃 Крепкий алкоголь: 1 шт — «пьян», 2 — «очень пьян»', 'indigestion': '🤢 Вызывает «несварение» на сут…` |  | :363 |
| `SPECIAL_DEPT_CODE_MIN_LEN` | `4` |  | :374 |
| `SPECIAL_DEPT_CODE_MAX_LEN` | `8` |  | :375 |
| `SPECIAL_DEPT_ATTEMPTS_LIMIT` | `3` | ошибок кода подряд | :376 |
| `SPECIAL_DEPT_BLOCK_MINUTES` | `1440` | бан на 24 часа после 3 ошибок | :377 |
| `FISH_AP_COST` | `3` | стоимость одного заброса удочки | :380 |
| `RESERVOIR_AP_COST` | `5` |  | :385 |
| `FISH_WEIGHTS` | `[{'key': 'small', 'label': 'Мелкая', 'mult': 1.0, 'chance': 40}, {'key': 'medium', 'label': 'Средняя', 'mult': 1.15, 'chance': 40}, {'key': 'large', 'label': 'Большая', 'mult': 1.25, 'chance': 20}]` |  | :390 |
| `FISH_TREASURY_SALE_MULT` | `0.5` |  | :398 |
| `FISH_TREASURY_DAILY_LIMIT` | `300` |  | :403 |
| `FOREST_AP_COST` | `4` | запасной цена поиска, если у зоны нет ap_cost в БД | :406 |
| `FOREST_RESULT_DELAY` | `(5, 10)` | результат поиска через 5–10 секунд | :409 |
| `FOREST_SOLD_DAILY_LIMIT` | `250` |  | :414 |
| `FOREST_ALLOW_TOURISTS` | `False` |  | :419 |
| `FOREST_BOAR_PITY_TARGET` | `12` |  | :422 |
| `FOREST_BOAR_CHANCE` | `4.0` |  | :426 |
| `CALLSIGN_PRICE` | `500` |  | :428 |
| `PILOT_BASE_HP` | `100` |  | :430 |
| `FOREST_BOAR_HP` | `40` |  | :435 |
| `FOREST_BOAR_DMG` | `(4, 7)` |  | :436 |
| `FOREST_BOAR_DODGE` | `15` |  | :437 |
| `FOREST_BOAR_LOSS_AP` | `10` |  | :439 |
| `FOREST_BOAR_LOOT` | `[('Мясо кабана', 50), ('Шкура кабана', 20), ('Клык кабана', 10), ('', 20)]` |  | :441 |
| `FOREST_WHITE_WOLF_HP` | `120` |  | :453 |
| `FOREST_WHITE_WOLF_DMG` | `(7, 12)` |  | :454 |
| `FOREST_WHITE_WOLF_DODGE` | `20` |  | :455 |
| `FOREST_WHITE_WOLF_LOSS_AP` | `15` |  | :457 |
| `FOREST_WHITE_WOLF_CHANCE` | `2.0` |  | :458 |
| `FOREST_WHITE_WOLF_PITY_TARGET` | `36` |  | :461 |
| `FOREST_WHITE_WOLF_BLEED_CHANCE` | `30` |  | :463 |
| `FOREST_WHITE_WOLF_BLEED_DMG` | `3` |  | :464 |
| `FOREST_WHITE_WOLF_AUTOWIN_HP` | `20` |  | :466 |
| `FOREST_WHITE_WOLF_SMALL_BLESSING` | `'внимание севера'` |  | :468 |
| `FOREST_WHITE_WOLF_BIG_BLESSING` | `'благословение севера'` |  | :469 |
| `FOREST_BOAR_SEED` | `{'key': 'boar', 'spot': 'forest', 'name': 'Дикий кабан', 'hp': FOREST_BOAR_HP, 'dmg_min': FOREST_BOAR_DMG[0], 'dmg_max': FOREST_BOAR_DMG[1], 'dodge': FOREST_BOAR_DODGE, 'loss_ap': FOREST_BOAR_LOSS_…` |  | :476 |
| `FOREST_WHITE_WOLF_SEED` | `{'key': 'white_wolf', 'spot': 'forest', 'name': 'Белый Волк Севера', 'hp': FOREST_WHITE_WOLF_HP, 'dmg_min': FOREST_WHITE_WOLF_DMG[0], 'dmg_max': FOREST_WHITE_WOLF_DMG[1], 'dodge': FOREST_WHITE_WOLF…` |  | :501 |
| `MOLLUSK_SEED` | `{'key': 'mollusk', 'spot': 'reservoir', 'name': 'Мутировавший моллюск', 'hp': 24, 'dmg_min': 5, 'dmg_max': 9, 'dodge': 20, 'loss_ap': 12, 'chance': 4, 'pity_target': 0, 'reward_nm': 0, 'photo_key':…` |  | :529 |
| `MOLLUSK_ITEM_SEEDS` | `[('Мясо моллюска', 'Плотное мясо мутировавшего моллюска. В сыром виде есть нельзя — прожарь на кухне.', 120, 60, 3, 'resource', 0), ('Жемчужина', 'Редчайшая жемчужина из раковины мутировавшего молл…` |  | :552 |
| `MOLLUSK_ENEMY_DROPS` | `('Мясо моллюска', 'Жемчужина')` |  | :567 |
| `MINE_AP_COST` | `12` | стоимость одной попытки добычи | :576 |
| `MINE_BASE_CHANCE` | `30` | базовый шанс успеха без бонуса кирки | :577 |
| `MINE_PICKAXE_BONUS_PER_RANK` | `15` | надбавка к шансу за ступень кирки (ранг 1 → +15%) | :578 |
| `MINE_CHANCE_CAP` | `90` | потолок шанса успеха | :579 |
| `MINE_RESULT_DELAY` | `(7, 15)` | результат добычи через 7–15 секунд | :580 |
| `MINE_REQUIRED_STATUS` | `'pilot1'` | вход в копь — с «Пилота 1 класса» | :581 |
| `MINE_GEM_CAP` | `1` | из самоцветов за бой выпадает не больше одного | :582 |
| `MINE_PICKAXE_NAME` | `'Кирка'` |  | :583 |
| `MINE_ORE_NAME` | `'Железная руда'` |  | :584 |
| `MINE_BAT_KEY` | `'bat'` |  | :587 |
| `MINE_BAT_SPOT` | `'iron'` |  | :588 |
| `MINE_BAT_CHANCE` | `7.0` |  | :589 |
| `MINE_BAT_PITY_TARGET` | `12` |  | :590 |
| `MINE_BAT_SEED` | `{'key': MINE_BAT_KEY, 'spot': MINE_BAT_SPOT, 'name': 'Летучая мышь', 'hp': 22, 'dmg_min': 3, 'dmg_max': 7, 'dodge': 35, 'loss_ap': 15, 'chance': MINE_BAT_CHANCE, 'pity_target': MINE_BAT_PITY_TARGET…` |  | :595 |
| `MINE_ITEM_SEEDS` | `[(MINE_PICKAXE_NAME, 'Простая кирка шахтёра: без неё в штольню не сунешься, а с ней порода поддаётся легче. Повышает шанс успешной добычи руды.', 300, 150, 1, 'mining', 0), (MINE_ORE_NAME, 'Кусок ж…` |  | :621 |
| `MINE_SHOP_ITEMS` | `(MINE_PICKAXE_NAME,)` |  | :642 |
| `MINE_ENEMY_DROPS` | `('Изумруд', 'Рубин', 'Сапфир')` |  | :645 |
| `ON_HIT_EFFECTS` | `{'bleed': {'emoji': '🩸', 'title': 'Кровотечение', 'until_battle_end': True, 'params': (('chance', 'Шанс наложить, %', 'percent'), ('dmg', 'Урон, HP за ход', 'int')), 'hint': 'Раны сочатся кровью ка…` |  | :654 |
| `ON_HIT_KIND_ORDER` | `('bleed', 'poison', 'frostbite', 'state')` |  | :698 |
| `ON_HIT_STATE_ROUNDS` | `{'оглушён': 3, 'ослеплён': 4}` |  | :700 |
| `LOGGING_AP_COST` | `12` | стоимость одной попытки рубки | :706 |
| `LOGGING_BASE_CHANCE` | `35` | базовый шанс успеха без бонуса топора | :707 |
| `LOGGING_AXE_BONUS_PER_RANK` | `15` | надбавка к шансу за ступень топора | :708 |
| `LOGGING_CHANCE_CAP` | `90` | потолок шанса успеха | :709 |
| `LOGGING_AXE_SLIP_CHANCE` | `2.5` | шанс, что топор отскочит пилоту в плечо, % | :710 |
| `LOGGING_RESULT_DELAY` | `(7, 15)` | результат рубки через 7–15 секунд | :711 |
| `LOGGING_AXE_NAME` | `'Топор'` |  | :712 |
| `LOGGING_WOOD_NAME` | `'Бревна'` |  | :713 |
| `LOGGING_PLANK_NAME` | `'Доска'` |  | :719 |
| `LOGGING_FIREWOOD_NAME` | `'Пак дров'` |  | :720 |
| `LOGGING_PLANK_YIELD` | `3` | досок из одного бревна | :721 |
| `LOGGING_PLANK_FEE` | `15` | НМ за распил одного бревна (в казну) | :722 |
| `LOGGING_FIREWOOD_YIELD` | `3` | паков дров из одного бревна | :723 |
| `LOGGING_FIREWOOD_AP_COST` | `4` | ОД за рубку дров из одного бревна | :724 |
| `LOGGING_SNAKE_KEY` | `'snake'` |  | :728 |
| `LOGGING_OWL_KEY` | `'owl'` |  | :729 |
| `LOGGING_SPOT` | `'logging'` |  | :730 |
| `LOGGING_SNAKE_CHANCE` | `8.0` |  | :731 |
| `LOGGING_SNAKE_PITY_TARGET` | `10` |  | :732 |
| `LOGGING_OWL_CHANCE` | `3.0` |  | :733 |
| `LOGGING_OWL_PITY_TARGET` | `24` |  | :734 |
| `LOGGING_SNAKE_POISON_CHANCE` | `30` |  | :736 |
| `LOGGING_SNAKE_POISON_DMG` | `2` |  | :737 |
| `LOGGING_OWL_FLEE_HP` | `20` |  | :741 |
| `LOGGING_OWL_BLIND_CHANCE` | `30` |  | :742 |
| `LOGGING_OWL_BLIND_ROUNDS` | `4` |  | :743 |
| `LOGGING_SNAKE_SEED` | `{'key': LOGGING_SNAKE_KEY, 'spot': LOGGING_SPOT, 'name': 'Лесная змея', 'hp': 30, 'dmg_min': 4, 'dmg_max': 8, 'dodge': 25, 'loss_ap': 10, 'chance': LOGGING_SNAKE_CHANCE, 'pity_target': LOGGING_SNAK…` |  | :747 |
| `LOGGING_OWL_SEED` | `{'key': LOGGING_OWL_KEY, 'spot': LOGGING_SPOT, 'name': 'Неясыть', 'hp': 90, 'dmg_min': 7, 'dmg_max': 12, 'dodge': 30, 'loss_ap': 15, 'chance': LOGGING_OWL_CHANCE, 'pity_target': LOGGING_OWL_PITY_TA…` |  | :777 |
| `LOGGING_ITEM_SEEDS` | `[(LOGGING_AXE_NAME, 'Крепкий лесорубский топор: без него к срубам не подпустят. Повышает шанс успешной рубки деревьев.', 300, 150, 1, 'mining', 0), (LOGGING_WOOD_NAME, 'Свежие срубленные брёвна из …` |  | :809 |
| `LOGGING_SHOP_ITEMS` | `(LOGGING_AXE_NAME,)` |  | :843 |
| `LOGGING_ENEMY_DROPS` | `('Змеиная кожа', 'Змеиный яд', 'Совиное перо')` |  | :846 |
| `LOGGING_MARKET_RESOURCES` | `(LOGGING_PLANK_NAME, LOGGING_FIREWOOD_NAME)` |  | :849 |
| `REPORT_DAILY_LIMIT` | `3` |  | :851 |
| `REPORT_AUTO_APPROVE_TROOPS` | `100` |  | :852 |
| `NEWS_PUBLISH_BONUS` | `10` |  | :856 |
| `NEWS_PUBLISH_CAP` | `28` |  | :857 |
| `ROLE_SALARY_PAY_DAY` | `28` |  | :860 |
| `REPORT_DAILY_PAY_CAP` | `4000` |  | :865 |
| `REPORT_MAX_TROOPS` | `1000000` |  | :866 |
| `REPORT_MAX_REGION` | `38` | 0 = Столица, 1..38 регионы | :867 |
| `WALL_TEXT_MAX_LEN` | `40` | лимит символов на одно изречение | :870 |
| `WALL_FREE_PER_DAY` | `2` | бесплатных сообщений в сутки | :871 |
| `WALL_PAID_STEPS` | `[(3, 30), (3, 90), (3, 200)]` | далее платные ступени: (кол-во, цена НМ) | :872 |
| `WALL_REVIEW_TOTAL` | `11` | максимум сообщений в сутки (2 + 3+3+3) | :877 |
| `WALL_PAGE_SIZE` | `5` | постов на страницу стены | :878 |
| `WALL_ARCHIVE_PAGE_SIZE` | `8` | записей архива стены на страницу списка | :879 |
| `REPORT_ARCHIVE_PAGE` | `8` | отчётов на страницу архива МВД и в «Моих отчётах» | :882 |
| `POLL_MAX_DAYS` | `10` | максимум дней, сколько живёт опрос. Не закрыл | :885 |
| `POLL_VISIBLE` | `4` | сколько новейших опросов висит в меню голосования. | :888 |
| `POLL_ARCHIVE_DAYS_PER_PAGE` | `5` | дней (дат) архива опросов на страницу списка | :891 |
| `POLL_ARCHIVE_PER_DAY` | `6` | опросов под одним заголовком-днём | :892 |
| `REP_SPEECH_MAX_LEN` | `100` | лимит символов одного обращения | :895 |
| `REP_SPEECH_PER_DAY` | `2` | обращений в сутки от представителя | :896 |
| `AUTO_PROMOTE_MAX_TROOPS` | `4040` |  | :901 |

## Буклет туриста

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `TOURIST_BOOKLET_NAME` | `'Буклет туриста'` |  | :24 |

## Суточный цикл Нордхайма

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `REPORT_DAY_START_HOUR` | `10` |  | :119 |

## Дом Дуэлей (PvP-арена)

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `DUEL_ZONES` | `('head', 'body', 'hands', 'legs')` |  | :216 |

## Рынок: слоты продажи

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `MARKET_BASE_SLOTS` | `1` | слоты без лицензии | :291 |

## Налог на недвижимость (НМ/мес)

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `HOUSING_TAX` | `{'municipal': 0, 'studio': 20, 'apartment': 35, 'improved': 60, 'mansion': 100}` |  | :297 |

## Банк: лимит счёта туриста (НМ)

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `TOURIST_BALANCE_LIMIT` | `200` |  | :307 |

## Данж: лимит хила (количество применений за забег)

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `DUNGEON_HEAL_SOFT_LIMIT` | `6` | после этого — ×2/3 | :310 |

## Сброс протухших забегов подземелья

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `DUNGEON_RUN_STALE_SEC` | `3600` |  | :319 |

## Данж: побег и дымовая шашка

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `ESCAPE_BASE_CHANCE` | `25` |  | :327 |

