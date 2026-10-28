# Справочник констант `config.py`

> **Сгенерировано** `tools/export_config.py`. Перегенерация:
> `.venv\Scripts\python.exe tools/export_config.py`.
>
> Все модульные константы `config.py`, сгруппированные по секциям
> (комментариям-разделителям `# ── … ──`). Длинные значения усечены `…`;
> точное значение — в `config.py` по строке из первой колонки.

Всего констант: **216**; разделов: **10**.

## Без раздела

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `VERSION` | `'0.39.8'` |  | :16 |
| `VERSION_NOTES` | `'🏰 Клановое поместье открывает двери! Здание, склад, кухня, сад, библиотека, лавка и иерархия — всё внутри.'` |  | :17 |
| `PREV_VERSION` | `'0.39.7'` |  | :20 |
| `PREV_VERSION_NOTES` | `'Художнику выдали кисти: картинки клан-холла — из админ-панели.'` |  | :21 |
| `TOURIST_BOOKLET_DESCRIPTION` | `'Печатная карта Нордхайма для гостей города. Просматривай превью городских локаций — и отмечай их в буклете. Собери все 9 и получи награду от командования.'` |  | :25 |
| `TOURIST_BOOKLET_PRICE` | `1` |  | :28 |
| `TOURIST_BOOKLET_SELL_PRICE` | `0` | буклет не продаётся (иначе чек-лист теряется) | :29 |
| `TOURIST_BOOKLET_AWARD` | `'Опытный турист'` |  | :30 |
| `TOURIST_BOOKLET_AWARD_EMOJI` | `'🧭'` |  | :31 |
| `TOURIST_BOOKLET_AWARD_DESCRIPTION` | `'Посетил все городские локации Нордхайма по «Буклету туриста». Знак почётного гостя города.'` |  | :32 |
| `TOURIST_BOOKLET_REWARD_NM` | `20` |  | :34 |
| `TOURIST_BOOKLET_REWARD_TX` | `'booklet'` |  | :35 |
| `TOURIST_BOOKLET_LOCATIONS` | `('townhall', 'library', 'park', 'gossmi', 'bank', 'kvp', 'hq', 'contracts', 'nii')` |  | :38 |
| `CLAN_HALL_ENABLED` | `True` |  | :45 |
| `CLAN_BUILDING_TYPES` | `{'house': {'name': 'Дом Клана', 'slots': 2, 'max_level': 2, 'days': 2, 'price_nm': 3000, 'required': {'Доска': 60, 'Бревна': 20, 'Железная руда': 15}}, 'manor': {'name': 'Клановое поместье', 'slots…` |  | :47 |
| `CLAN_BUILDING_NO_RESOURCES_MULT` | `2` |  | :62 |
| `CLAN_EXPANSION_TYPES` | `('kitchen', 'workbench', 'shower', 'garden', 'library', 'shop')` |  | :64 |
| `CLAN_EXPANSION_INFO` | `{'kitchen': {'name': 'Кухня', 'icon': '🍳', 'desc': 'Готовка по выученным рецептам; уровень задаёт доступные блюда.'}, 'workbench': {'name': 'Крафтовый стол', 'icon': '🛠', 'desc': 'Крафт снаряжения …` |  | :66 |
| `CLAN_EXPANSION_UPGRADE` | `{2: {'nm': 1500, 'required': {'Доска': 20, 'Железная руда': 10}}, 3: {'nm': 4000, 'required': {'Доска': 50, 'Железная руда': 30}}, 4: {'nm': 9000, 'required': {'Доска': 100, 'Железная руда': 60}}}` |  | :81 |
| `CLAN_SHOWER_AP_BY_LEVEL` | `{1: 25, 2: 50, 3: 75, 4: 100}` |  | :89 |
| `CLAN_SHOWER_SOBER_MINUTES` | `{1: 60, 2: 120, 3: 180, 4: 240}` |  | :90 |
| `CLAN_GARDEN_PLOTS` | `{1: 2, 2: 3, 3: 4, 4: 6}` |  | :92 |
| `CLAN_SHOP_DAILY_LIMIT` | `3` |  | :93 |
| `CLAN_SHOP_DISCOUNT` | `10` |  | :94 |
| `BOT_TOKEN` | `os.getenv('BOT_TOKEN')` |  | :96 |
| `ADMIN_IDS` | `[int(x) for x in os.getenv('ADMIN_IDS', '').split(',') if x.strip()]` |  | :97 |
| `_news_raw` | `os.getenv('NEWS_CHAT_ID', '').strip()` |  | :100 |
| `NEWS_CHAT_ID` | `int(_news_raw) if _news_raw.lstrip('-').isdigit() else None` |  | :101 |
| `DB_PATH` | `os.getenv('DATABASE_PATH', 'database/nordmark.db')` |  | :104 |
| `FSM_STORAGE_PATH` | `os.getenv('FSM_STORAGE_PATH', '').strip() or os.path.join(os.path.dirname(os.path.abspath(DB_PATH)), 'fsm')` |  | :113 |
| `REPORT_DAY_START_MINUTE` | `0` |  | :123 |
| `RANKS` | `[('Рекрут', 0), ('Рядовой', 100), ('Ефрейтор', 350), ('Капрал', 500), ('Сержант', 850), ('Старший Сержант', 1500), ('Лейтенант', 2500), ('Старший Лейтенант', 4040), ('Капитан', 6000), ('Майор', 850…` |  | :125 |
| `MAX_SELF_RANK_TROOPS` | `4040` |  | :146 |
| `AUTO_RANK_NAMES` | `('Рекрут', 'Рядовой', 'Ефрейтор', 'Капрал', 'Сержант', 'Старший Сержант', 'Лейтенант', 'Старший Лейтенант')` |  | :149 |
| `AWARD_MAX_SHOP_DISCOUNT` | `40` |  | :156 |
| `AWARD_MIN_REPORT_TAX` | `5` |  | :157 |
| `RANK_STATUS_TAGS` | `{'Ефрейтор': 'pilot2', 'Старший Сержант': 'pilot1', 'Старший Лейтенант': 'veteran', 'Майор': 'master_pilot', 'Полковник': 'ace'}` |  | :159 |
| `LEGIONER_ACCESS_CAP_ORDER` | `5` |  | :172 |
| `RANK_DAMAGE_TIERS` | `{'ace': (4, 8), 'master_pilot': (3, 5), 'veteran': (2, 4), 'pilot1': (1, 3), 'pilot2': (1, 2), 'recruit': (1, 1), 'tourist': (0, 1)}` |  | :178 |
| `RANK_CRIT_CHANCE` | `{'ace': 7.5, 'master_pilot': 6.0, 'veteran': 4.5, 'pilot1': 3.0, 'pilot2': 1.5, 'recruit': 0.0, 'tourist': 0.0}` |  | :196 |
| `PILOT_CRIT_MULT` | `1.4` |  | :210 |
| `PILOT_NO_WEAPON_DMG` | `(1, 1)` |  | :213 |
| `DUEL_ZONE_LABELS` | `{'head': 'Голова', 'body': 'Тело', 'hands': 'Руки', 'legs': 'Ноги'}` |  | :220 |
| `DUEL_ZONE_EMOJI` | `{'head': '🧠', 'body': '🫀', 'hands': '✊', 'legs': '🦵'}` |  | :226 |
| `DUEL_AP_COST` | `15` | списывается с обоих при старте боя | :232 |
| `DUEL_RATING_WIN` | `2` | рейтинг за победу | :233 |
| `DUEL_RATING_LOSS` | `-3` | рейтинг за поражение | :234 |
| `DUEL_RATING_DRAW` | `0` | рейтинг за ничью | :235 |
| `DUEL_RATING_FORFEIT` | `-1` | рейтинг тому, кто покинул бой («Покинуть дуэль») | :236 |
| `DUEL_RATING_FORFEIT_WIN` | `1` | рейтинг сопернику, если противник покинул бой (меньше чистой победы) | :237 |
| `DUEL_MIN_DAMAGE` | `1` | минимум урона за попавший (не уклонённый) удар | :238 |
| `DUEL_GUARD_REDUCTION` | `0.5` | доля урона, остающаяся при угаданной зоне защиты | :239 |
| `DUEL_HEAL_BETWEEN` | `0` | восстановление HP между раундами (пока нет) | :240 |
| `DUEL_CHALLENGE_TIMEOUT_SEC` | `120` | сколько живёт неотвеченный вызов | :241 |
| `DUEL_STALE_SEC` | `1800` | зависшая дуэль авто-завершается как void | :242 |
| `DUEL_GLOVES_NAME` | `'Дуэльные перчатки'` |  | :243 |
| `DUEL_GLOVES_DAMAGE` | `7` |  | :244 |
| `DUEL_GLOVES_PRICE` | `200` |  | :245 |
| `DUEL_GLOVES_SELL` | `100` |  | :246 |
| `DUEL_CLUB_CARD_NAME` | `'Клубная карта «Дом Дуэлей»'` |  | :247 |
| `DUEL_CLUB_CARD_PRICE` | `150` |  | :248 |
| `DUEL_CLUB_CARD_SELL` | `75` |  | :249 |
| `DUEL_CLUB_CARD_DAYS` | `30` |  | :250 |
| `DUEL_ACCESS_TAG` | `'pilot2'` |  | :253 |
| `RARITY_LEVELS` | `{1: 'Обычный', 2: 'Качественный', 3: 'Редкий', 4: 'Шедевр', 5: 'Легендарный'}` |  | :255 |
| `RARITY_EMOJI` | `{1: '⬜', 2: '🟩', 3: '🟦', 4: '🟪', 5: '🟧'}` |  | :263 |
| `ITEM_CATEGORIES` | `{'weapon': 'Оружие', 'consumable': 'Расходники', 'building': 'Недвижимость', 'housing': 'Жильё', 'furniture': 'Мебель и расширения', 'seeds': 'Семена', 'equipment': 'Одежда', 'resource': 'Ресурсы',…` |  | :271 |
| `MARKET_LICENSE_SLOTS` | `2` | доп. слоты при активной лицензии | :295 |
| `MARKET_LICENSE_DAYS` | `30` | срок действия лицензии (дней) | :296 |
| `MARKET_LICENSE_PRICE` | `500` | цена лицензии в НМ | :297 |
| `DUNGEON_HEAL_HARD_LIMIT` | `10` | после этого — ×1/2 | :314 |
| `DUNGEON_HEAL_SOFT_MULT` | `2 / 3` |  | :315 |
| `DUNGEON_HEAL_HARD_MULT` | `1 / 2` |  | :316 |
| `ESCAPE_HP_BONUS` | `20` |  | :331 |
| `DUNGEON_SMOKE_ESCAPE` | `95` |  | :332 |
| `DUNGEON_SMOKE_MAX` | `2` |  | :333 |
| `DUNGEON_ESCAPE_DRUNK_MULT` | `0.5` |  | :336 |
| `AP_MAX` | `150` |  | :338 |
| `AP_DAILY_RECOVERY` | `100` |  | :339 |
| `AP_BONUS_FROM_CONSUMABLE` | `50` |  | :340 |
| `AP_DAILY_RESTORE_LIMIT` | `150` |  | :345 |
| `AP_EXHAUSTED_MINUTES` | `2880` | 2 суток | :346 |
| `AP_EXHAUSTED_DAILY_RECOVERY` | `75` | суточное восстановление в «истощении» | :347 |
| `AP_EXHAUSTED_MAX_AP` | `90` | максимум ОД в «истощении» | :348 |
| `SEAWEED_DAILY_LIMIT` | `6` |  | :351 |
| `DIGESTIVE_UPSET_MINUTES` | `1440` | 24 часа | :352 |
| `ALCOHOL_WEAK_DRUNK_LIMIT` | `3` |  | :357 |
| `ALCOHOL_WEAK_VERY_DRUNK_LIMIT` | `6` |  | :358 |
| `ALCOHOL_STRONG_DRUNK_LIMIT` | `1` |  | :360 |
| `ALCOHOL_STRONG_VERY_DRUNK_LIMIT` | `2` |  | :361 |
| `DRUNK_MINUTES` | `60` |  | :362 |
| `VERY_DRUNK_MINUTES` | `360` | 6 часов | :363 |
| `DRINK_EFFECT_LABELS` | `{'alcohol_weak': '🍺 Слабоалкогольный: 3 шт/сутки — «пьян», 6 — «очень пьян»', 'alcohol_strong': '🥃 Крепкий алкоголь: 1 шт — «пьян», 2 — «очень пьян»', 'indigestion': '🤢 Вызывает «несварение» на сут…` |  | :366 |
| `SPECIAL_DEPT_CODE_MIN_LEN` | `4` |  | :377 |
| `SPECIAL_DEPT_CODE_MAX_LEN` | `8` |  | :378 |
| `SPECIAL_DEPT_ATTEMPTS_LIMIT` | `3` | ошибок кода подряд | :379 |
| `SPECIAL_DEPT_BLOCK_MINUTES` | `1440` | бан на 24 часа после 3 ошибок | :380 |
| `FISH_AP_COST` | `3` | стоимость одного заброса удочки | :383 |
| `RESERVOIR_AP_COST` | `5` |  | :388 |
| `FISH_WEIGHTS` | `[{'key': 'small', 'label': 'Мелкая', 'mult': 1.0, 'chance': 40}, {'key': 'medium', 'label': 'Средняя', 'mult': 1.15, 'chance': 40}, {'key': 'large', 'label': 'Большая', 'mult': 1.25, 'chance': 20}]` |  | :393 |
| `FISH_TREASURY_SALE_MULT` | `0.5` |  | :401 |
| `FISH_TREASURY_DAILY_LIMIT` | `300` |  | :406 |
| `FOREST_AP_COST` | `4` | запасной цена поиска, если у зоны нет ap_cost в БД | :409 |
| `FOREST_RESULT_DELAY` | `(5, 10)` | результат поиска через 5–10 секунд | :412 |
| `FOREST_SOLD_DAILY_LIMIT` | `250` |  | :417 |
| `FOREST_ALLOW_TOURISTS` | `False` |  | :422 |
| `FOREST_BOAR_PITY_TARGET` | `12` |  | :425 |
| `FOREST_BOAR_CHANCE` | `4.0` |  | :429 |
| `CALLSIGN_PRICE` | `500` |  | :431 |
| `PILOT_BASE_HP` | `100` |  | :433 |
| `FOREST_BOAR_HP` | `40` |  | :438 |
| `FOREST_BOAR_DMG` | `(4, 7)` |  | :439 |
| `FOREST_BOAR_DODGE` | `15` |  | :440 |
| `FOREST_BOAR_LOSS_AP` | `10` |  | :442 |
| `FOREST_BOAR_LOOT` | `[('Мясо кабана', 50), ('Шкура кабана', 20), ('Клык кабана', 10), ('', 20)]` |  | :444 |
| `FOREST_WHITE_WOLF_HP` | `120` |  | :456 |
| `FOREST_WHITE_WOLF_DMG` | `(7, 12)` |  | :457 |
| `FOREST_WHITE_WOLF_DODGE` | `20` |  | :458 |
| `FOREST_WHITE_WOLF_LOSS_AP` | `15` |  | :460 |
| `FOREST_WHITE_WOLF_CHANCE` | `2.0` |  | :461 |
| `FOREST_WHITE_WOLF_PITY_TARGET` | `36` |  | :464 |
| `FOREST_WHITE_WOLF_BLEED_CHANCE` | `30` |  | :466 |
| `FOREST_WHITE_WOLF_BLEED_DMG` | `3` |  | :467 |
| `FOREST_WHITE_WOLF_AUTOWIN_HP` | `20` |  | :469 |
| `FOREST_WHITE_WOLF_SMALL_BLESSING` | `'внимание севера'` |  | :471 |
| `FOREST_WHITE_WOLF_BIG_BLESSING` | `'благословение севера'` |  | :472 |
| `FOREST_BOAR_SEED` | `{'key': 'boar', 'spot': 'forest', 'name': 'Дикий кабан', 'hp': FOREST_BOAR_HP, 'dmg_min': FOREST_BOAR_DMG[0], 'dmg_max': FOREST_BOAR_DMG[1], 'dodge': FOREST_BOAR_DODGE, 'loss_ap': FOREST_BOAR_LOSS_…` |  | :479 |
| `FOREST_WHITE_WOLF_SEED` | `{'key': 'white_wolf', 'spot': 'forest', 'name': 'Белый Волк Севера', 'hp': FOREST_WHITE_WOLF_HP, 'dmg_min': FOREST_WHITE_WOLF_DMG[0], 'dmg_max': FOREST_WHITE_WOLF_DMG[1], 'dodge': FOREST_WHITE_WOLF…` |  | :504 |
| `MOLLUSK_SEED` | `{'key': 'mollusk', 'spot': 'reservoir', 'name': 'Мутировавший моллюск', 'hp': 24, 'dmg_min': 5, 'dmg_max': 9, 'dodge': 20, 'loss_ap': 12, 'chance': 4, 'pity_target': 0, 'reward_nm': 0, 'photo_key':…` |  | :532 |
| `MOLLUSK_ITEM_SEEDS` | `[('Мясо моллюска', 'Плотное мясо мутировавшего моллюска. В сыром виде есть нельзя — прожарь на кухне.', 120, 60, 3, 'resource', 0), ('Жемчужина', 'Редчайшая жемчужина из раковины мутировавшего молл…` |  | :555 |
| `MOLLUSK_ENEMY_DROPS` | `('Мясо моллюска', 'Жемчужина')` |  | :570 |
| `MINE_AP_COST` | `12` | стоимость одной попытки добычи | :579 |
| `MINE_BASE_CHANCE` | `30` | базовый шанс успеха без бонуса кирки | :580 |
| `MINE_PICKAXE_BONUS_PER_RANK` | `15` | надбавка к шансу за ступень кирки (ранг 1 → +15%) | :581 |
| `MINE_CHANCE_CAP` | `90` | потолок шанса успеха | :582 |
| `MINE_RESULT_DELAY` | `(7, 15)` | результат добычи через 7–15 секунд | :583 |
| `MINE_REQUIRED_STATUS` | `'pilot1'` | вход в копь — с «Пилота 1 класса» | :584 |
| `MINE_GEM_CAP` | `1` | из самоцветов за бой выпадает не больше одного | :585 |
| `MINE_PICKAXE_NAME` | `'Кирка'` |  | :586 |
| `MINE_ORE_NAME` | `'Железная руда'` |  | :587 |
| `MINE_BAT_KEY` | `'bat'` |  | :590 |
| `MINE_BAT_SPOT` | `'iron'` |  | :591 |
| `MINE_BAT_CHANCE` | `7.0` |  | :592 |
| `MINE_BAT_PITY_TARGET` | `12` |  | :593 |
| `MINE_BAT_SEED` | `{'key': MINE_BAT_KEY, 'spot': MINE_BAT_SPOT, 'name': 'Летучая мышь', 'hp': 22, 'dmg_min': 3, 'dmg_max': 7, 'dodge': 35, 'loss_ap': 15, 'chance': MINE_BAT_CHANCE, 'pity_target': MINE_BAT_PITY_TARGET…` |  | :598 |
| `MINE_ITEM_SEEDS` | `[(MINE_PICKAXE_NAME, 'Простая кирка шахтёра: без неё в штольню не сунешься, а с ней порода поддаётся легче. Повышает шанс успешной добычи руды.', 300, 150, 1, 'mining', 0), (MINE_ORE_NAME, 'Кусок ж…` |  | :624 |
| `MINE_SHOP_ITEMS` | `(MINE_PICKAXE_NAME,)` |  | :645 |
| `MINE_ENEMY_DROPS` | `('Изумруд', 'Рубин', 'Сапфир')` |  | :648 |
| `ON_HIT_EFFECTS` | `{'bleed': {'emoji': '🩸', 'title': 'Кровотечение', 'until_battle_end': True, 'params': (('chance', 'Шанс наложить, %', 'percent'), ('dmg', 'Урон, HP за ход', 'int')), 'hint': 'Раны сочатся кровью ка…` |  | :657 |
| `ON_HIT_KIND_ORDER` | `('bleed', 'poison', 'frostbite', 'state', 'lifesteal')` |  | :711 |
| `ON_HIT_STATE_ROUNDS` | `{'оглушён': 3, 'ослеплён': 4}` |  | :713 |
| `CLAN_ROLES` | `{'leader': '👑 Глава клана', 'seneschal': '🛡 Сенешаль клана', 'banner': '🚩 Знаменосец клана', 'elder': '⭐ Старшина', 'member': '▪️ Член клана'}` |  | :719 |
| `CLAN_ROLE_ORDER` | `('leader', 'seneschal', 'banner', 'elder', 'member')` |  | :726 |
| `LOGGING_AP_COST` | `12` | стоимость одной попытки рубки | :732 |
| `LOGGING_BASE_CHANCE` | `35` | базовый шанс успеха без бонуса топора | :733 |
| `LOGGING_AXE_BONUS_PER_RANK` | `15` | надбавка к шансу за ступень топора | :734 |
| `LOGGING_CHANCE_CAP` | `90` | потолок шанса успеха | :735 |
| `LOGGING_AXE_SLIP_CHANCE` | `2.5` | шанс, что топор отскочит пилоту в плечо, % | :736 |
| `LOGGING_RESULT_DELAY` | `(7, 15)` | результат рубки через 7–15 секунд | :737 |
| `LOGGING_AXE_NAME` | `'Топор'` |  | :738 |
| `LOGGING_WOOD_NAME` | `'Бревна'` |  | :739 |
| `LOGGING_PLANK_NAME` | `'Доска'` |  | :745 |
| `LOGGING_FIREWOOD_NAME` | `'Пак дров'` |  | :746 |
| `LOGGING_PLANK_YIELD` | `3` | досок из одного бревна | :747 |
| `LOGGING_PLANK_FEE` | `15` | НМ за распил одного бревна (в казну) | :748 |
| `LOGGING_FIREWOOD_YIELD` | `3` | паков дров из одного бревна | :749 |
| `LOGGING_FIREWOOD_AP_COST` | `4` | ОД за рубку дров из одного бревна | :750 |
| `LOGGING_SNAKE_KEY` | `'snake'` |  | :754 |
| `LOGGING_OWL_KEY` | `'owl'` |  | :755 |
| `LOGGING_SPOT` | `'logging'` |  | :756 |
| `LOGGING_SNAKE_CHANCE` | `8.0` |  | :757 |
| `LOGGING_SNAKE_PITY_TARGET` | `10` |  | :758 |
| `LOGGING_OWL_CHANCE` | `3.0` |  | :759 |
| `LOGGING_OWL_PITY_TARGET` | `24` |  | :760 |
| `LOGGING_SNAKE_POISON_CHANCE` | `30` |  | :762 |
| `LOGGING_SNAKE_POISON_DMG` | `2` |  | :763 |
| `LOGGING_OWL_FLEE_HP` | `20` |  | :767 |
| `LOGGING_OWL_BLIND_CHANCE` | `30` |  | :768 |
| `LOGGING_OWL_BLIND_ROUNDS` | `4` |  | :769 |
| `LOGGING_SNAKE_SEED` | `{'key': LOGGING_SNAKE_KEY, 'spot': LOGGING_SPOT, 'name': 'Лесная змея', 'hp': 30, 'dmg_min': 4, 'dmg_max': 8, 'dodge': 25, 'loss_ap': 10, 'chance': LOGGING_SNAKE_CHANCE, 'pity_target': LOGGING_SNAK…` |  | :773 |
| `LOGGING_OWL_SEED` | `{'key': LOGGING_OWL_KEY, 'spot': LOGGING_SPOT, 'name': 'Неясыть', 'hp': 90, 'dmg_min': 7, 'dmg_max': 12, 'dodge': 30, 'loss_ap': 15, 'chance': LOGGING_OWL_CHANCE, 'pity_target': LOGGING_OWL_PITY_TA…` |  | :803 |
| `LOGGING_ITEM_SEEDS` | `[(LOGGING_AXE_NAME, 'Крепкий лесорубский топор: без него к срубам не подпустят. Повышает шанс успешной рубки деревьев.', 300, 150, 1, 'mining', 0), (LOGGING_WOOD_NAME, 'Свежие срубленные брёвна из …` |  | :835 |
| `LOGGING_SHOP_ITEMS` | `(LOGGING_AXE_NAME,)` |  | :869 |
| `LOGGING_ENEMY_DROPS` | `('Змеиная кожа', 'Змеиный яд', 'Совиное перо')` |  | :872 |
| `LOGGING_MARKET_RESOURCES` | `(LOGGING_PLANK_NAME, LOGGING_FIREWOOD_NAME)` |  | :875 |
| `REPORT_DAILY_LIMIT` | `3` |  | :877 |
| `REPORT_AUTO_APPROVE_TROOPS` | `100` |  | :878 |
| `NEWS_PUBLISH_BONUS` | `10` |  | :882 |
| `NEWS_PUBLISH_CAP` | `28` |  | :883 |
| `ROLE_SALARY_PAY_DAY` | `28` |  | :886 |
| `REPORT_DAILY_PAY_CAP` | `4000` |  | :891 |
| `REPORT_MAX_TROOPS` | `1000000` |  | :892 |
| `REPORT_MAX_REGION` | `38` | 0 = Столица, 1..38 регионы | :893 |
| `WALL_TEXT_MAX_LEN` | `40` | лимит символов на одно изречение | :896 |
| `WALL_FREE_PER_DAY` | `2` | бесплатных сообщений в сутки | :897 |
| `WALL_PAID_STEPS` | `[(3, 30), (3, 90), (3, 200)]` | далее платные ступени: (кол-во, цена НМ) | :898 |
| `WALL_REVIEW_TOTAL` | `11` | максимум сообщений в сутки (2 + 3+3+3) | :903 |
| `WALL_PAGE_SIZE` | `5` | постов на страницу стены | :904 |
| `WALL_ARCHIVE_PAGE_SIZE` | `8` | записей архива стены на страницу списка | :905 |
| `REPORT_ARCHIVE_PAGE` | `8` | отчётов на страницу архива МВД и в «Моих отчётах» | :908 |
| `POLL_MAX_DAYS` | `10` | максимум дней, сколько живёт опрос. Не закрыл | :911 |
| `POLL_VISIBLE` | `4` | сколько новейших опросов висит в меню голосования. | :914 |
| `POLL_ARCHIVE_DAYS_PER_PAGE` | `5` | дней (дат) архива опросов на страницу списка | :917 |
| `POLL_ARCHIVE_PER_DAY` | `6` | опросов под одним заголовком-днём | :918 |
| `REP_SPEECH_MAX_LEN` | `100` | лимит символов одного обращения | :921 |
| `REP_SPEECH_PER_DAY` | `2` | обращений в сутки от представителя | :922 |
| `AUTO_PROMOTE_MAX_TROOPS` | `4040` |  | :927 |

## Буклет туриста

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `TOURIST_BOOKLET_NAME` | `'Буклет туриста'` |  | :24 |

## Суточный цикл Нордхайма

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `REPORT_DAY_START_HOUR` | `10` |  | :122 |

## Дом Дуэлей (PvP-арена)

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `DUEL_ZONES` | `('head', 'body', 'hands', 'legs')` |  | :219 |

## Рынок: слоты продажи

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `MARKET_BASE_SLOTS` | `1` | слоты без лицензии | :294 |

## Налог на недвижимость (НМ/мес)

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `HOUSING_TAX` | `{'municipal': 0, 'studio': 20, 'apartment': 35, 'improved': 60, 'mansion': 100}` |  | :300 |

## Банк: лимит счёта туриста (НМ)

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `TOURIST_BALANCE_LIMIT` | `200` |  | :310 |

## Данж: лимит хила (количество применений за забег)

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `DUNGEON_HEAL_SOFT_LIMIT` | `6` | после этого — ×2/3 | :313 |

## Сброс протухших забегов подземелья

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `DUNGEON_RUN_STALE_SEC` | `3600` |  | :322 |

## Данж: побег и дымовая шашка

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `ESCAPE_BASE_CHANCE` | `25` |  | :330 |

