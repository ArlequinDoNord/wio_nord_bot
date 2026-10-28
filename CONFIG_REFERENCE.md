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
| `VERSION` | `'0.39.5'` |  | :16 |
| `VERSION_NOTES` | `'История кошелька теперь помнит всё: листается страницами.'` |  | :17 |
| `PREV_VERSION` | `'0.39.4'` |  | :19 |
| `PREV_VERSION_NOTES` | `'Касса неслучайно заметила: чей-то оклад дошёл наконец до адресата.'` |  | :20 |
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
| `CLAN_SHOWER_AP_BY_LEVEL` | `{1: 25, 2: 50, 3: 75, 4: 100}` |  | :90 |
| `CLAN_SHOWER_SOBER_MINUTES` | `{1: 60, 2: 120, 3: 180, 4: 240}` |  | :91 |
| `CLAN_GARDEN_PLOTS` | `{1: 2, 2: 3, 3: 4, 4: 6}` |  | :93 |
| `CLAN_SHOP_DAILY_LIMIT` | `3` |  | :94 |
| `CLAN_SHOP_DISCOUNT` | `10` |  | :95 |
| `BOT_TOKEN` | `os.getenv('BOT_TOKEN')` |  | :97 |
| `ADMIN_IDS` | `[int(x) for x in os.getenv('ADMIN_IDS', '').split(',') if x.strip()]` |  | :98 |
| `_news_raw` | `os.getenv('NEWS_CHAT_ID', '').strip()` |  | :101 |
| `NEWS_CHAT_ID` | `int(_news_raw) if _news_raw.lstrip('-').isdigit() else None` |  | :102 |
| `DB_PATH` | `os.getenv('DATABASE_PATH', 'database/nordmark.db')` |  | :105 |
| `FSM_STORAGE_PATH` | `os.getenv('FSM_STORAGE_PATH', '').strip() or os.path.join(os.path.dirname(os.path.abspath(DB_PATH)), 'fsm')` |  | :114 |
| `REPORT_DAY_START_MINUTE` | `0` |  | :124 |
| `RANKS` | `[('Рекрут', 0), ('Рядовой', 100), ('Ефрейтор', 350), ('Капрал', 500), ('Сержант', 850), ('Старший Сержант', 1500), ('Лейтенант', 2500), ('Старший Лейтенант', 4040), ('Капитан', 6000), ('Майор', 850…` |  | :126 |
| `MAX_SELF_RANK_TROOPS` | `4040` |  | :147 |
| `AUTO_RANK_NAMES` | `('Рекрут', 'Рядовой', 'Ефрейтор', 'Капрал', 'Сержант', 'Старший Сержант', 'Лейтенант', 'Старший Лейтенант')` |  | :150 |
| `AWARD_MAX_SHOP_DISCOUNT` | `40` |  | :157 |
| `AWARD_MIN_REPORT_TAX` | `5` |  | :158 |
| `RANK_STATUS_TAGS` | `{'Ефрейтор': 'pilot2', 'Старший Сержант': 'pilot1', 'Старший Лейтенант': 'veteran', 'Майор': 'master_pilot', 'Полковник': 'ace'}` |  | :160 |
| `LEGIONER_ACCESS_CAP_ORDER` | `5` |  | :173 |
| `RANK_DAMAGE_TIERS` | `{'ace': (4, 8), 'master_pilot': (3, 5), 'veteran': (2, 4), 'pilot1': (1, 3), 'pilot2': (1, 2), 'recruit': (1, 1), 'tourist': (0, 1)}` |  | :179 |
| `RANK_CRIT_CHANCE` | `{'ace': 7.5, 'master_pilot': 6.0, 'veteran': 4.5, 'pilot1': 3.0, 'pilot2': 1.5, 'recruit': 0.0, 'tourist': 0.0}` |  | :197 |
| `PILOT_CRIT_MULT` | `1.4` |  | :211 |
| `PILOT_NO_WEAPON_DMG` | `(1, 1)` |  | :214 |
| `DUEL_ZONE_LABELS` | `{'head': 'Голова', 'body': 'Тело', 'hands': 'Руки', 'legs': 'Ноги'}` |  | :221 |
| `DUEL_ZONE_EMOJI` | `{'head': '🧠', 'body': '🫀', 'hands': '✊', 'legs': '🦵'}` |  | :227 |
| `DUEL_AP_COST` | `15` | списывается с обоих при старте боя | :233 |
| `DUEL_RATING_WIN` | `2` | рейтинг за победу | :234 |
| `DUEL_RATING_LOSS` | `-3` | рейтинг за поражение | :235 |
| `DUEL_RATING_DRAW` | `0` | рейтинг за ничью | :236 |
| `DUEL_RATING_FORFEIT` | `-1` | рейтинг тому, кто покинул бой («Покинуть дуэль») | :237 |
| `DUEL_RATING_FORFEIT_WIN` | `1` | рейтинг сопернику, если противник покинул бой (меньше чистой победы) | :238 |
| `DUEL_MIN_DAMAGE` | `1` | минимум урона за попавший (не уклонённый) удар | :239 |
| `DUEL_GUARD_REDUCTION` | `0.5` | доля урона, остающаяся при угаданной зоне защиты | :240 |
| `DUEL_HEAL_BETWEEN` | `0` | восстановление HP между раундами (пока нет) | :241 |
| `DUEL_CHALLENGE_TIMEOUT_SEC` | `120` | сколько живёт неотвеченный вызов | :242 |
| `DUEL_STALE_SEC` | `1800` | зависшая дуэль авто-завершается как void | :243 |
| `DUEL_GLOVES_NAME` | `'Дуэльные перчатки'` |  | :244 |
| `DUEL_GLOVES_DAMAGE` | `7` |  | :245 |
| `DUEL_GLOVES_PRICE` | `200` |  | :246 |
| `DUEL_GLOVES_SELL` | `100` |  | :247 |
| `DUEL_CLUB_CARD_NAME` | `'Клубная карта «Дом Дуэлей»'` |  | :248 |
| `DUEL_CLUB_CARD_PRICE` | `150` |  | :249 |
| `DUEL_CLUB_CARD_SELL` | `75` |  | :250 |
| `DUEL_CLUB_CARD_DAYS` | `30` |  | :251 |
| `DUEL_ACCESS_TAG` | `'pilot2'` |  | :254 |
| `RARITY_LEVELS` | `{1: 'Обычный', 2: 'Качественный', 3: 'Редкий', 4: 'Шедевр', 5: 'Легендарный'}` |  | :256 |
| `RARITY_EMOJI` | `{1: '⬜', 2: '🟩', 3: '🟦', 4: '🟪', 5: '🟧'}` |  | :264 |
| `ITEM_CATEGORIES` | `{'weapon': 'Оружие', 'consumable': 'Расходники', 'building': 'Недвижимость', 'housing': 'Жильё', 'furniture': 'Мебель и расширения', 'seeds': 'Семена', 'equipment': 'Одежда', 'resource': 'Ресурсы',…` |  | :272 |
| `MARKET_LICENSE_SLOTS` | `2` | доп. слоты при активной лицензии | :296 |
| `MARKET_LICENSE_DAYS` | `30` | срок действия лицензии (дней) | :297 |
| `MARKET_LICENSE_PRICE` | `500` | цена лицензии в НМ | :298 |
| `DUNGEON_HEAL_HARD_LIMIT` | `10` | после этого — ×1/2 | :315 |
| `DUNGEON_HEAL_SOFT_MULT` | `2 / 3` |  | :316 |
| `DUNGEON_HEAL_HARD_MULT` | `1 / 2` |  | :317 |
| `ESCAPE_HP_BONUS` | `20` |  | :332 |
| `DUNGEON_SMOKE_ESCAPE` | `95` |  | :333 |
| `DUNGEON_SMOKE_MAX` | `2` |  | :334 |
| `DUNGEON_ESCAPE_DRUNK_MULT` | `0.5` |  | :337 |
| `AP_MAX` | `150` |  | :339 |
| `AP_DAILY_RECOVERY` | `100` |  | :340 |
| `AP_BONUS_FROM_CONSUMABLE` | `50` |  | :341 |
| `AP_DAILY_RESTORE_LIMIT` | `150` |  | :346 |
| `AP_EXHAUSTED_MINUTES` | `2880` | 2 суток | :347 |
| `AP_EXHAUSTED_DAILY_RECOVERY` | `75` | суточное восстановление в «истощении» | :348 |
| `AP_EXHAUSTED_MAX_AP` | `90` | максимум ОД в «истощении» | :349 |
| `SEAWEED_DAILY_LIMIT` | `6` |  | :352 |
| `DIGESTIVE_UPSET_MINUTES` | `1440` | 24 часа | :353 |
| `ALCOHOL_WEAK_DRUNK_LIMIT` | `3` |  | :358 |
| `ALCOHOL_WEAK_VERY_DRUNK_LIMIT` | `6` |  | :359 |
| `ALCOHOL_STRONG_DRUNK_LIMIT` | `1` |  | :361 |
| `ALCOHOL_STRONG_VERY_DRUNK_LIMIT` | `2` |  | :362 |
| `DRUNK_MINUTES` | `60` |  | :363 |
| `VERY_DRUNK_MINUTES` | `360` | 6 часов | :364 |
| `DRINK_EFFECT_LABELS` | `{'alcohol_weak': '🍺 Слабоалкогольный: 3 шт/сутки — «пьян», 6 — «очень пьян»', 'alcohol_strong': '🥃 Крепкий алкоголь: 1 шт — «пьян», 2 — «очень пьян»', 'indigestion': '🤢 Вызывает «несварение» на сут…` |  | :367 |
| `SPECIAL_DEPT_CODE_MIN_LEN` | `4` |  | :378 |
| `SPECIAL_DEPT_CODE_MAX_LEN` | `8` |  | :379 |
| `SPECIAL_DEPT_ATTEMPTS_LIMIT` | `3` | ошибок кода подряд | :380 |
| `SPECIAL_DEPT_BLOCK_MINUTES` | `1440` | бан на 24 часа после 3 ошибок | :381 |
| `FISH_AP_COST` | `3` | стоимость одного заброса удочки | :384 |
| `RESERVOIR_AP_COST` | `5` |  | :389 |
| `FISH_WEIGHTS` | `[{'key': 'small', 'label': 'Мелкая', 'mult': 1.0, 'chance': 40}, {'key': 'medium', 'label': 'Средняя', 'mult': 1.15, 'chance': 40}, {'key': 'large', 'label': 'Большая', 'mult': 1.25, 'chance': 20}]` |  | :394 |
| `FISH_TREASURY_SALE_MULT` | `0.5` |  | :402 |
| `FISH_TREASURY_DAILY_LIMIT` | `300` |  | :407 |
| `FOREST_AP_COST` | `4` | запасной цена поиска, если у зоны нет ap_cost в БД | :410 |
| `FOREST_RESULT_DELAY` | `(5, 10)` | результат поиска через 5–10 секунд | :413 |
| `FOREST_SOLD_DAILY_LIMIT` | `250` |  | :418 |
| `FOREST_ALLOW_TOURISTS` | `False` |  | :423 |
| `FOREST_BOAR_PITY_TARGET` | `12` |  | :426 |
| `FOREST_BOAR_CHANCE` | `4.0` |  | :430 |
| `CALLSIGN_PRICE` | `500` |  | :432 |
| `PILOT_BASE_HP` | `100` |  | :434 |
| `FOREST_BOAR_HP` | `40` |  | :439 |
| `FOREST_BOAR_DMG` | `(4, 7)` |  | :440 |
| `FOREST_BOAR_DODGE` | `15` |  | :441 |
| `FOREST_BOAR_LOSS_AP` | `10` |  | :443 |
| `FOREST_BOAR_LOOT` | `[('Мясо кабана', 50), ('Шкура кабана', 20), ('Клык кабана', 10), ('', 20)]` |  | :445 |
| `FOREST_WHITE_WOLF_HP` | `120` |  | :457 |
| `FOREST_WHITE_WOLF_DMG` | `(7, 12)` |  | :458 |
| `FOREST_WHITE_WOLF_DODGE` | `20` |  | :459 |
| `FOREST_WHITE_WOLF_LOSS_AP` | `15` |  | :461 |
| `FOREST_WHITE_WOLF_CHANCE` | `2.0` |  | :462 |
| `FOREST_WHITE_WOLF_PITY_TARGET` | `36` |  | :465 |
| `FOREST_WHITE_WOLF_BLEED_CHANCE` | `30` |  | :467 |
| `FOREST_WHITE_WOLF_BLEED_DMG` | `3` |  | :468 |
| `FOREST_WHITE_WOLF_AUTOWIN_HP` | `20` |  | :470 |
| `FOREST_WHITE_WOLF_SMALL_BLESSING` | `'внимание севера'` |  | :472 |
| `FOREST_WHITE_WOLF_BIG_BLESSING` | `'благословение севера'` |  | :473 |
| `FOREST_BOAR_SEED` | `{'key': 'boar', 'spot': 'forest', 'name': 'Дикий кабан', 'hp': FOREST_BOAR_HP, 'dmg_min': FOREST_BOAR_DMG[0], 'dmg_max': FOREST_BOAR_DMG[1], 'dodge': FOREST_BOAR_DODGE, 'loss_ap': FOREST_BOAR_LOSS_…` |  | :480 |
| `FOREST_WHITE_WOLF_SEED` | `{'key': 'white_wolf', 'spot': 'forest', 'name': 'Белый Волк Севера', 'hp': FOREST_WHITE_WOLF_HP, 'dmg_min': FOREST_WHITE_WOLF_DMG[0], 'dmg_max': FOREST_WHITE_WOLF_DMG[1], 'dodge': FOREST_WHITE_WOLF…` |  | :505 |
| `MOLLUSK_SEED` | `{'key': 'mollusk', 'spot': 'reservoir', 'name': 'Мутировавший моллюск', 'hp': 24, 'dmg_min': 5, 'dmg_max': 9, 'dodge': 20, 'loss_ap': 12, 'chance': 4, 'pity_target': 0, 'reward_nm': 0, 'photo_key':…` |  | :533 |
| `MOLLUSK_ITEM_SEEDS` | `[('Мясо моллюска', 'Плотное мясо мутировавшего моллюска. В сыром виде есть нельзя — прожарь на кухне.', 120, 60, 3, 'resource', 0), ('Жемчужина', 'Редчайшая жемчужина из раковины мутировавшего молл…` |  | :556 |
| `MOLLUSK_ENEMY_DROPS` | `('Мясо моллюска', 'Жемчужина')` |  | :571 |
| `MINE_AP_COST` | `12` | стоимость одной попытки добычи | :580 |
| `MINE_BASE_CHANCE` | `30` | базовый шанс успеха без бонуса кирки | :581 |
| `MINE_PICKAXE_BONUS_PER_RANK` | `15` | надбавка к шансу за ступень кирки (ранг 1 → +15%) | :582 |
| `MINE_CHANCE_CAP` | `90` | потолок шанса успеха | :583 |
| `MINE_RESULT_DELAY` | `(7, 15)` | результат добычи через 7–15 секунд | :584 |
| `MINE_REQUIRED_STATUS` | `'pilot1'` | вход в копь — с «Пилота 1 класса» | :585 |
| `MINE_GEM_CAP` | `1` | из самоцветов за бой выпадает не больше одного | :586 |
| `MINE_PICKAXE_NAME` | `'Кирка'` |  | :587 |
| `MINE_ORE_NAME` | `'Железная руда'` |  | :588 |
| `MINE_BAT_KEY` | `'bat'` |  | :591 |
| `MINE_BAT_SPOT` | `'iron'` |  | :592 |
| `MINE_BAT_CHANCE` | `7.0` |  | :593 |
| `MINE_BAT_PITY_TARGET` | `12` |  | :594 |
| `MINE_BAT_SEED` | `{'key': MINE_BAT_KEY, 'spot': MINE_BAT_SPOT, 'name': 'Летучая мышь', 'hp': 22, 'dmg_min': 3, 'dmg_max': 7, 'dodge': 35, 'loss_ap': 15, 'chance': MINE_BAT_CHANCE, 'pity_target': MINE_BAT_PITY_TARGET…` |  | :599 |
| `MINE_ITEM_SEEDS` | `[(MINE_PICKAXE_NAME, 'Простая кирка шахтёра: без неё в штольню не сунешься, а с ней порода поддаётся легче. Повышает шанс успешной добычи руды.', 300, 150, 1, 'mining', 0), (MINE_ORE_NAME, 'Кусок ж…` |  | :625 |
| `MINE_SHOP_ITEMS` | `(MINE_PICKAXE_NAME,)` |  | :646 |
| `MINE_ENEMY_DROPS` | `('Изумруд', 'Рубин', 'Сапфир')` |  | :649 |
| `ON_HIT_EFFECTS` | `{'bleed': {'emoji': '🩸', 'title': 'Кровотечение', 'until_battle_end': True, 'params': (('chance', 'Шанс наложить, %', 'percent'), ('dmg', 'Урон, HP за ход', 'int')), 'hint': 'Раны сочатся кровью ка…` |  | :658 |
| `ON_HIT_KIND_ORDER` | `('bleed', 'poison', 'frostbite', 'state', 'lifesteal')` |  | :712 |
| `ON_HIT_STATE_ROUNDS` | `{'оглушён': 3, 'ослеплён': 4}` |  | :714 |
| `CLAN_ROLES` | `{'leader': '👑 Глава клана', 'seneschal': '🛡 Сенешаль клана', 'banner': '🚩 Знаменосец клана', 'elder': '⭐ Старшина', 'member': '▪️ Член клана'}` |  | :720 |
| `CLAN_ROLE_ORDER` | `('leader', 'seneschal', 'banner', 'elder', 'member')` |  | :727 |
| `LOGGING_AP_COST` | `12` | стоимость одной попытки рубки | :733 |
| `LOGGING_BASE_CHANCE` | `35` | базовый шанс успеха без бонуса топора | :734 |
| `LOGGING_AXE_BONUS_PER_RANK` | `15` | надбавка к шансу за ступень топора | :735 |
| `LOGGING_CHANCE_CAP` | `90` | потолок шанса успеха | :736 |
| `LOGGING_AXE_SLIP_CHANCE` | `2.5` | шанс, что топор отскочит пилоту в плечо, % | :737 |
| `LOGGING_RESULT_DELAY` | `(7, 15)` | результат рубки через 7–15 секунд | :738 |
| `LOGGING_AXE_NAME` | `'Топор'` |  | :739 |
| `LOGGING_WOOD_NAME` | `'Бревна'` |  | :740 |
| `LOGGING_PLANK_NAME` | `'Доска'` |  | :746 |
| `LOGGING_FIREWOOD_NAME` | `'Пак дров'` |  | :747 |
| `LOGGING_PLANK_YIELD` | `3` | досок из одного бревна | :748 |
| `LOGGING_PLANK_FEE` | `15` | НМ за распил одного бревна (в казну) | :749 |
| `LOGGING_FIREWOOD_YIELD` | `3` | паков дров из одного бревна | :750 |
| `LOGGING_FIREWOOD_AP_COST` | `4` | ОД за рубку дров из одного бревна | :751 |
| `LOGGING_SNAKE_KEY` | `'snake'` |  | :755 |
| `LOGGING_OWL_KEY` | `'owl'` |  | :756 |
| `LOGGING_SPOT` | `'logging'` |  | :757 |
| `LOGGING_SNAKE_CHANCE` | `8.0` |  | :758 |
| `LOGGING_SNAKE_PITY_TARGET` | `10` |  | :759 |
| `LOGGING_OWL_CHANCE` | `3.0` |  | :760 |
| `LOGGING_OWL_PITY_TARGET` | `24` |  | :761 |
| `LOGGING_SNAKE_POISON_CHANCE` | `30` |  | :763 |
| `LOGGING_SNAKE_POISON_DMG` | `2` |  | :764 |
| `LOGGING_OWL_FLEE_HP` | `20` |  | :768 |
| `LOGGING_OWL_BLIND_CHANCE` | `30` |  | :769 |
| `LOGGING_OWL_BLIND_ROUNDS` | `4` |  | :770 |
| `LOGGING_SNAKE_SEED` | `{'key': LOGGING_SNAKE_KEY, 'spot': LOGGING_SPOT, 'name': 'Лесная змея', 'hp': 30, 'dmg_min': 4, 'dmg_max': 8, 'dodge': 25, 'loss_ap': 10, 'chance': LOGGING_SNAKE_CHANCE, 'pity_target': LOGGING_SNAK…` |  | :774 |
| `LOGGING_OWL_SEED` | `{'key': LOGGING_OWL_KEY, 'spot': LOGGING_SPOT, 'name': 'Неясыть', 'hp': 90, 'dmg_min': 7, 'dmg_max': 12, 'dodge': 30, 'loss_ap': 15, 'chance': LOGGING_OWL_CHANCE, 'pity_target': LOGGING_OWL_PITY_TA…` |  | :804 |
| `LOGGING_ITEM_SEEDS` | `[(LOGGING_AXE_NAME, 'Крепкий лесорубский топор: без него к срубам не подпустят. Повышает шанс успешной рубки деревьев.', 300, 150, 1, 'mining', 0), (LOGGING_WOOD_NAME, 'Свежие срубленные брёвна из …` |  | :836 |
| `LOGGING_SHOP_ITEMS` | `(LOGGING_AXE_NAME,)` |  | :870 |
| `LOGGING_ENEMY_DROPS` | `('Змеиная кожа', 'Змеиный яд', 'Совиное перо')` |  | :873 |
| `LOGGING_MARKET_RESOURCES` | `(LOGGING_PLANK_NAME, LOGGING_FIREWOOD_NAME)` |  | :876 |
| `REPORT_DAILY_LIMIT` | `3` |  | :878 |
| `REPORT_AUTO_APPROVE_TROOPS` | `100` |  | :879 |
| `NEWS_PUBLISH_BONUS` | `10` |  | :883 |
| `NEWS_PUBLISH_CAP` | `28` |  | :884 |
| `ROLE_SALARY_PAY_DAY` | `28` |  | :887 |
| `REPORT_DAILY_PAY_CAP` | `4000` |  | :892 |
| `REPORT_MAX_TROOPS` | `1000000` |  | :893 |
| `REPORT_MAX_REGION` | `38` | 0 = Столица, 1..38 регионы | :894 |
| `WALL_TEXT_MAX_LEN` | `40` | лимит символов на одно изречение | :897 |
| `WALL_FREE_PER_DAY` | `2` | бесплатных сообщений в сутки | :898 |
| `WALL_PAID_STEPS` | `[(3, 30), (3, 90), (3, 200)]` | далее платные ступени: (кол-во, цена НМ) | :899 |
| `WALL_REVIEW_TOTAL` | `11` | максимум сообщений в сутки (2 + 3+3+3) | :904 |
| `WALL_PAGE_SIZE` | `5` | постов на страницу стены | :905 |
| `WALL_ARCHIVE_PAGE_SIZE` | `8` | записей архива стены на страницу списка | :906 |
| `REPORT_ARCHIVE_PAGE` | `8` | отчётов на страницу архива МВД и в «Моих отчётах» | :909 |
| `POLL_MAX_DAYS` | `10` | максимум дней, сколько живёт опрос. Не закрыл | :912 |
| `POLL_VISIBLE` | `4` | сколько новейших опросов висит в меню голосования. | :915 |
| `POLL_ARCHIVE_DAYS_PER_PAGE` | `5` | дней (дат) архива опросов на страницу списка | :918 |
| `POLL_ARCHIVE_PER_DAY` | `6` | опросов под одним заголовком-днём | :919 |
| `REP_SPEECH_MAX_LEN` | `100` | лимит символов одного обращения | :922 |
| `REP_SPEECH_PER_DAY` | `2` | обращений в сутки от представителя | :923 |
| `AUTO_PROMOTE_MAX_TROOPS` | `4040` |  | :928 |

## Буклет туриста

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `TOURIST_BOOKLET_NAME` | `'Буклет туриста'` |  | :23 |

## Суточный цикл Нордхайма

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `REPORT_DAY_START_HOUR` | `10` |  | :123 |

## Дом Дуэлей (PvP-арена)

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `DUEL_ZONES` | `('head', 'body', 'hands', 'legs')` |  | :220 |

## Рынок: слоты продажи

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `MARKET_BASE_SLOTS` | `1` | слоты без лицензии | :295 |

## Налог на недвижимость (НМ/мес)

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `HOUSING_TAX` | `{'municipal': 0, 'studio': 20, 'apartment': 35, 'improved': 60, 'mansion': 100}` |  | :301 |

## Банк: лимит счёта туриста (НМ)

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `TOURIST_BALANCE_LIMIT` | `200` |  | :311 |

## Данж: лимит хила (количество применений за забег)

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `DUNGEON_HEAL_SOFT_LIMIT` | `6` | после этого — ×2/3 | :314 |

## Сброс протухших забегов подземелья

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `DUNGEON_RUN_STALE_SEC` | `3600` |  | :323 |

## Данж: побег и дымовая шашка

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `ESCAPE_BASE_CHANCE` | `25` |  | :331 |

