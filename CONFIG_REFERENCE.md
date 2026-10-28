# Справочник констант `config.py`

> **Сгенерировано** `tools/export_config.py`. Перегенерация:
> `.venv\Scripts\python.exe tools/export_config.py`.
>
> Все модульные константы `config.py`, сгруппированные по секциям
> (комментариям-разделителям `# ── … ──`). Длинные значения усечены `…`;
> точное значение — в `config.py` по строке из первой колонки.

Всего констант: **243**; разделов: **10**.

## Без раздела

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `VERSION` | `'0.39.10'` |  | :16 |
| `VERSION_NOTES` | `'Подготовка к празднику продолжается: мелочи отточены.'` |  | :17 |
| `PREV_VERSION` | `'0.39.9'` |  | :19 |
| `PREV_VERSION_NOTES` | `'В городе затеплились огонёк — идёт подготовка к празднику.'` |  | :20 |
| `TOURIST_BOOKLET_DESCRIPTION` | `'Печатная карта Нордхайма для гостей города. Просматривай превью городских локаций — и отмечай их в буклете. Собери все 9 и получи награду от командования.'` |  | :24 |
| `TOURIST_BOOKLET_PRICE` | `1` |  | :27 |
| `TOURIST_BOOKLET_SELL_PRICE` | `0` | буклет не продаётся (иначе чек-лист теряется) | :28 |
| `TOURIST_BOOKLET_AWARD` | `'Опытный турист'` |  | :29 |
| `TOURIST_BOOKLET_AWARD_EMOJI` | `'🧭'` |  | :30 |
| `TOURIST_BOOKLET_AWARD_DESCRIPTION` | `'Посетил все городские локации Нордхайма по «Буклету туриста». Знак почётного гостя города.'` |  | :31 |
| `TOURIST_BOOKLET_REWARD_NM` | `20` |  | :33 |
| `TOURIST_BOOKLET_REWARD_TX` | `'booklet'` |  | :34 |
| `TOURIST_BOOKLET_LOCATIONS` | `('townhall', 'library', 'park', 'gossmi', 'bank', 'kvp', 'hq', 'contracts', 'nii')` |  | :37 |
| `CLAN_HALL_ENABLED` | `True` |  | :44 |
| `FIRE_EVENT_ENABLED` | `True` |  | :50 |
| `FIRE_EVENT_START` | `(2026, 10, 30, 0, 0)` | МСК, ночь на пятницу 30.10 | :51 |
| `FIRE_EVENT_DURATION_DAYS` | `5` | до ~00:00 МСК 4.11 | :52 |
| `FIRE_LAB_ENABLED` | `False` |  | :54 |
| `FIRE_EVENT_LAB_FEE` | `42` | вход в лабиринт, НМ | :55 |
| `FIRE_EVENT_MAX_ENTRIES_DAY` | `4` | максимум заходов за сутки | :56 |
| `FIRE_LAB_SESSION_TTL_SEC` | `3600` | неактивность: сессия закрывается автоматически (1 ч) | :57 |
| `FIRE_LAB_SCARECROW_BLIND_P` | `0.15` | Пугало: «сено в лицо» — ослепление | :62 |
| `FIRE_LAB_APPLE_STUN_P` | `0.1` | Дитя Яблони: «яблочко» — оглушение | :63 |
| `FIRE_LAB_CROW_BLIND_P` | `0.15` | Ворон: ослепление (как сова) | :64 |
| `FIRE_LAB_GHOST_FROST_P` | `0.2` | Призрак: обморожение на 3 хода | :65 |
| `FIRE_LAB_GHOST_FROST_ROUNDS` | `3` |  | :66 |
| `FIRE_LAB_BOSS_BURN_P` | `0.25` | Босс «Мистер Тыква»: поджиг игрока | :67 |
| `FIRE_LAB_BOSS_BURN_DMG` | `2` | −HP/ход | :68 |
| `FIRE_LAB_BOSS_BURN_ROUNDS` | `3` |  | :69 |
| `FIRE_LAB_BOSS_MAX` | `2` | максимум встреч с боссом за заход | :70 |
| `FIRE_LAB_ROOMS_MAX` | `25` | после 25 комнат-развилок выход автоматом | :71 |
| `FIRE_LAB_P_WELL` | `0.07` | Колодец (перебивается паттерном ЛЛПП) | :74 |
| `FIRE_LAB_WELL_MAX` | `3` | максимум посещений за заход | :75 |
| `FIRE_LAB_P_TREE` | `0.09` | Древо Огня (перебивается ЛЛППНН) | :76 |
| `FIRE_LAB_TREE_MAX` | `1` | раз за заход | :77 |
| `FIRE_LAB_P_CHEST` | `0.1` | Сундук сокровищ | :78 |
| `FIRE_LAB_CHEST_MAX` | `2` | максимум за заход | :79 |
| `FIRE_TREE_DMG_BONUS_PCT` | `15` | +15% урона | :82 |
| `FIRE_TREE_REGEN_HP` | `1` | +1 HP после каждого удара игрока | :83 |
| `FIRE_LAB_PATTERN_WELL` | `('L', 'L', 'S', 'S')` | ЛЛПП → Колодец (до 3) | :87 |
| `FIRE_LAB_PATTERN_TREE` | `('L', 'L', 'S', 'S', 'R', 'R')` | ЛЛППНН → Древо Огня (1) | :88 |
| `CLAN_BUILDING_TYPES` | `{'house': {'name': 'Дом Клана', 'slots': 2, 'max_level': 2, 'days': 2, 'price_nm': 3000, 'required': {'Доска': 60, 'Бревна': 20, 'Железная руда': 15}}, 'manor': {'name': 'Клановое поместье', 'slots…` |  | :90 |
| `CLAN_BUILDING_NO_RESOURCES_MULT` | `2` |  | :105 |
| `CLAN_EXPANSION_TYPES` | `('kitchen', 'workbench', 'shower', 'garden', 'library', 'shop')` |  | :107 |
| `CLAN_EXPANSION_INFO` | `{'kitchen': {'name': 'Кухня', 'icon': '🍳', 'desc': 'Готовка по выученным рецептам; уровень задаёт доступные блюда.'}, 'workbench': {'name': 'Крафтовый стол', 'icon': '🛠', 'desc': 'Крафт снаряжения …` |  | :109 |
| `CLAN_EXPANSION_UPGRADE` | `{2: {'nm': 1500, 'required': {'Доска': 20, 'Железная руда': 10}}, 3: {'nm': 4000, 'required': {'Доска': 50, 'Железная руда': 30}}, 4: {'nm': 9000, 'required': {'Доска': 100, 'Железная руда': 60}}}` |  | :124 |
| `CLAN_SHOWER_AP_BY_LEVEL` | `{1: 25, 2: 50, 3: 75, 4: 100}` |  | :132 |
| `CLAN_SHOWER_SOBER_MINUTES` | `{1: 60, 2: 120, 3: 180, 4: 240}` |  | :133 |
| `CLAN_GARDEN_PLOTS` | `{1: 2, 2: 3, 3: 4, 4: 6}` |  | :135 |
| `CLAN_SHOP_DAILY_LIMIT` | `3` |  | :136 |
| `CLAN_SHOP_DISCOUNT` | `10` |  | :137 |
| `BOT_TOKEN` | `os.getenv('BOT_TOKEN')` |  | :139 |
| `ADMIN_IDS` | `[int(x) for x in os.getenv('ADMIN_IDS', '').split(',') if x.strip()]` |  | :140 |
| `_news_raw` | `os.getenv('NEWS_CHAT_ID', '').strip()` |  | :143 |
| `NEWS_CHAT_ID` | `int(_news_raw) if _news_raw.lstrip('-').isdigit() else None` |  | :144 |
| `DB_PATH` | `os.getenv('DATABASE_PATH', 'database/nordmark.db')` |  | :147 |
| `FSM_STORAGE_PATH` | `os.getenv('FSM_STORAGE_PATH', '').strip() or os.path.join(os.path.dirname(os.path.abspath(DB_PATH)), 'fsm')` |  | :156 |
| `REPORT_DAY_START_MINUTE` | `0` |  | :166 |
| `RANKS` | `[('Рекрут', 0), ('Рядовой', 100), ('Ефрейтор', 350), ('Капрал', 500), ('Сержант', 850), ('Старший Сержант', 1500), ('Лейтенант', 2500), ('Старший Лейтенант', 4040), ('Капитан', 6000), ('Майор', 850…` |  | :168 |
| `MAX_SELF_RANK_TROOPS` | `4040` |  | :189 |
| `AUTO_RANK_NAMES` | `('Рекрут', 'Рядовой', 'Ефрейтор', 'Капрал', 'Сержант', 'Старший Сержант', 'Лейтенант', 'Старший Лейтенант')` |  | :192 |
| `AWARD_MAX_SHOP_DISCOUNT` | `40` |  | :199 |
| `AWARD_MIN_REPORT_TAX` | `5` |  | :200 |
| `RANK_STATUS_TAGS` | `{'Ефрейтор': 'pilot2', 'Старший Сержант': 'pilot1', 'Старший Лейтенант': 'veteran', 'Майор': 'master_pilot', 'Полковник': 'ace'}` |  | :202 |
| `LEGIONER_ACCESS_CAP_ORDER` | `5` |  | :215 |
| `RANK_DAMAGE_TIERS` | `{'ace': (4, 8), 'master_pilot': (3, 5), 'veteran': (2, 4), 'pilot1': (1, 3), 'pilot2': (1, 2), 'recruit': (1, 1), 'tourist': (0, 1)}` |  | :221 |
| `RANK_CRIT_CHANCE` | `{'ace': 7.5, 'master_pilot': 6.0, 'veteran': 4.5, 'pilot1': 3.0, 'pilot2': 1.5, 'recruit': 0.0, 'tourist': 0.0}` |  | :239 |
| `PILOT_CRIT_MULT` | `1.4` |  | :253 |
| `PILOT_NO_WEAPON_DMG` | `(1, 1)` |  | :256 |
| `DUEL_ZONE_LABELS` | `{'head': 'Голова', 'body': 'Тело', 'hands': 'Руки', 'legs': 'Ноги'}` |  | :263 |
| `DUEL_ZONE_EMOJI` | `{'head': '🧠', 'body': '🫀', 'hands': '✊', 'legs': '🦵'}` |  | :269 |
| `DUEL_AP_COST` | `15` | списывается с обоих при старте боя | :275 |
| `DUEL_RATING_WIN` | `2` | рейтинг за победу | :276 |
| `DUEL_RATING_LOSS` | `-3` | рейтинг за поражение | :277 |
| `DUEL_RATING_DRAW` | `0` | рейтинг за ничью | :278 |
| `DUEL_RATING_FORFEIT` | `-1` | рейтинг тому, кто покинул бой («Покинуть дуэль») | :279 |
| `DUEL_RATING_FORFEIT_WIN` | `1` | рейтинг сопернику, если противник покинул бой (меньше чистой победы) | :280 |
| `DUEL_MIN_DAMAGE` | `1` | минимум урона за попавший (не уклонённый) удар | :281 |
| `DUEL_GUARD_REDUCTION` | `0.5` | доля урона, остающаяся при угаданной зоне защиты | :282 |
| `DUEL_HEAL_BETWEEN` | `0` | восстановление HP между раундами (пока нет) | :283 |
| `DUEL_CHALLENGE_TIMEOUT_SEC` | `120` | сколько живёт неотвеченный вызов | :284 |
| `DUEL_STALE_SEC` | `1800` | зависшая дуэль авто-завершается как void | :285 |
| `DUEL_GLOVES_NAME` | `'Дуэльные перчатки'` |  | :286 |
| `DUEL_GLOVES_DAMAGE` | `7` |  | :287 |
| `DUEL_GLOVES_PRICE` | `200` |  | :288 |
| `DUEL_GLOVES_SELL` | `100` |  | :289 |
| `DUEL_CLUB_CARD_NAME` | `'Клубная карта «Дом Дуэлей»'` |  | :290 |
| `DUEL_CLUB_CARD_PRICE` | `150` |  | :291 |
| `DUEL_CLUB_CARD_SELL` | `75` |  | :292 |
| `DUEL_CLUB_CARD_DAYS` | `30` |  | :293 |
| `DUEL_ACCESS_TAG` | `'pilot2'` |  | :296 |
| `RARITY_LEVELS` | `{1: 'Обычный', 2: 'Качественный', 3: 'Редкий', 4: 'Шедевр', 5: 'Легендарный'}` |  | :298 |
| `RARITY_EMOJI` | `{1: '⬜', 2: '🟩', 3: '🟦', 4: '🟪', 5: '🟧'}` |  | :306 |
| `ITEM_CATEGORIES` | `{'weapon': 'Оружие', 'consumable': 'Расходники', 'building': 'Недвижимость', 'housing': 'Жильё', 'furniture': 'Мебель и расширения', 'seeds': 'Семена', 'equipment': 'Одежда', 'resource': 'Ресурсы',…` |  | :314 |
| `MARKET_LICENSE_SLOTS` | `2` | доп. слоты при активной лицензии | :338 |
| `MARKET_LICENSE_DAYS` | `30` | срок действия лицензии (дней) | :339 |
| `MARKET_LICENSE_PRICE` | `500` | цена лицензии в НМ | :340 |
| `DUNGEON_HEAL_HARD_LIMIT` | `10` | после этого — ×1/2 | :357 |
| `DUNGEON_HEAL_SOFT_MULT` | `2 / 3` |  | :358 |
| `DUNGEON_HEAL_HARD_MULT` | `1 / 2` |  | :359 |
| `ESCAPE_HP_BONUS` | `20` |  | :374 |
| `DUNGEON_SMOKE_ESCAPE` | `95` |  | :375 |
| `DUNGEON_SMOKE_MAX` | `2` |  | :376 |
| `DUNGEON_ESCAPE_DRUNK_MULT` | `0.5` |  | :379 |
| `AP_MAX` | `150` |  | :381 |
| `AP_DAILY_RECOVERY` | `100` |  | :382 |
| `AP_BONUS_FROM_CONSUMABLE` | `50` |  | :383 |
| `AP_DAILY_RESTORE_LIMIT` | `150` |  | :388 |
| `AP_EXHAUSTED_MINUTES` | `2880` | 2 суток | :389 |
| `AP_EXHAUSTED_DAILY_RECOVERY` | `75` | суточное восстановление в «истощении» | :390 |
| `AP_EXHAUSTED_MAX_AP` | `90` | максимум ОД в «истощении» | :391 |
| `SEAWEED_DAILY_LIMIT` | `6` |  | :394 |
| `DIGESTIVE_UPSET_MINUTES` | `1440` | 24 часа | :395 |
| `ALCOHOL_WEAK_DRUNK_LIMIT` | `3` |  | :400 |
| `ALCOHOL_WEAK_VERY_DRUNK_LIMIT` | `6` |  | :401 |
| `ALCOHOL_STRONG_DRUNK_LIMIT` | `1` |  | :403 |
| `ALCOHOL_STRONG_VERY_DRUNK_LIMIT` | `2` |  | :404 |
| `DRUNK_MINUTES` | `60` |  | :405 |
| `VERY_DRUNK_MINUTES` | `360` | 6 часов | :406 |
| `DRINK_EFFECT_LABELS` | `{'alcohol_weak': '🍺 Слабоалкогольный: 3 шт/сутки — «пьян», 6 — «очень пьян»', 'alcohol_strong': '🥃 Крепкий алкоголь: 1 шт — «пьян», 2 — «очень пьян»', 'indigestion': '🤢 Вызывает «несварение» на сут…` |  | :409 |
| `SPECIAL_DEPT_CODE_MIN_LEN` | `4` |  | :420 |
| `SPECIAL_DEPT_CODE_MAX_LEN` | `8` |  | :421 |
| `SPECIAL_DEPT_ATTEMPTS_LIMIT` | `3` | ошибок кода подряд | :422 |
| `SPECIAL_DEPT_BLOCK_MINUTES` | `1440` | бан на 24 часа после 3 ошибок | :423 |
| `FISH_AP_COST` | `3` | стоимость одного заброса удочки | :426 |
| `RESERVOIR_AP_COST` | `5` |  | :431 |
| `FISH_WEIGHTS` | `[{'key': 'small', 'label': 'Мелкая', 'mult': 1.0, 'chance': 40}, {'key': 'medium', 'label': 'Средняя', 'mult': 1.15, 'chance': 40}, {'key': 'large', 'label': 'Большая', 'mult': 1.25, 'chance': 20}]` |  | :436 |
| `FISH_TREASURY_SALE_MULT` | `0.5` |  | :444 |
| `FISH_TREASURY_DAILY_LIMIT` | `300` |  | :449 |
| `FOREST_AP_COST` | `4` | запасной цена поиска, если у зоны нет ap_cost в БД | :452 |
| `FOREST_RESULT_DELAY` | `(5, 10)` | результат поиска через 5–10 секунд | :455 |
| `FOREST_SOLD_DAILY_LIMIT` | `250` |  | :460 |
| `FOREST_ALLOW_TOURISTS` | `False` |  | :465 |
| `FOREST_BOAR_PITY_TARGET` | `12` |  | :468 |
| `FOREST_BOAR_CHANCE` | `4.0` |  | :472 |
| `CALLSIGN_PRICE` | `500` |  | :474 |
| `PILOT_BASE_HP` | `100` |  | :476 |
| `FOREST_BOAR_HP` | `40` |  | :481 |
| `FOREST_BOAR_DMG` | `(4, 7)` |  | :482 |
| `FOREST_BOAR_DODGE` | `15` |  | :483 |
| `FOREST_BOAR_LOSS_AP` | `10` |  | :485 |
| `FOREST_BOAR_LOOT` | `[('Мясо кабана', 50), ('Шкура кабана', 20), ('Клык кабана', 10), ('', 20)]` |  | :487 |
| `FOREST_WHITE_WOLF_HP` | `120` |  | :499 |
| `FOREST_WHITE_WOLF_DMG` | `(7, 12)` |  | :500 |
| `FOREST_WHITE_WOLF_DODGE` | `20` |  | :501 |
| `FOREST_WHITE_WOLF_LOSS_AP` | `15` |  | :503 |
| `FOREST_WHITE_WOLF_CHANCE` | `2.0` |  | :504 |
| `FOREST_WHITE_WOLF_PITY_TARGET` | `36` |  | :507 |
| `FOREST_WHITE_WOLF_BLEED_CHANCE` | `30` |  | :509 |
| `FOREST_WHITE_WOLF_BLEED_DMG` | `3` |  | :510 |
| `FOREST_WHITE_WOLF_AUTOWIN_HP` | `20` |  | :512 |
| `FOREST_WHITE_WOLF_SMALL_BLESSING` | `'внимание севера'` |  | :514 |
| `FOREST_WHITE_WOLF_BIG_BLESSING` | `'благословение севера'` |  | :515 |
| `FOREST_BOAR_SEED` | `{'key': 'boar', 'spot': 'forest', 'name': 'Дикий кабан', 'hp': FOREST_BOAR_HP, 'dmg_min': FOREST_BOAR_DMG[0], 'dmg_max': FOREST_BOAR_DMG[1], 'dodge': FOREST_BOAR_DODGE, 'loss_ap': FOREST_BOAR_LOSS_…` |  | :522 |
| `FOREST_WHITE_WOLF_SEED` | `{'key': 'white_wolf', 'spot': 'forest', 'name': 'Белый Волк Севера', 'hp': FOREST_WHITE_WOLF_HP, 'dmg_min': FOREST_WHITE_WOLF_DMG[0], 'dmg_max': FOREST_WHITE_WOLF_DMG[1], 'dodge': FOREST_WHITE_WOLF…` |  | :547 |
| `MOLLUSK_SEED` | `{'key': 'mollusk', 'spot': 'reservoir', 'name': 'Мутировавший моллюск', 'hp': 24, 'dmg_min': 5, 'dmg_max': 9, 'dodge': 20, 'loss_ap': 12, 'chance': 4, 'pity_target': 0, 'reward_nm': 0, 'photo_key':…` |  | :575 |
| `MOLLUSK_ITEM_SEEDS` | `[('Мясо моллюска', 'Плотное мясо мутировавшего моллюска. В сыром виде есть нельзя — прожарь на кухне.', 120, 60, 3, 'resource', 0), ('Жемчужина', 'Редчайшая жемчужина из раковины мутировавшего молл…` |  | :598 |
| `MOLLUSK_ENEMY_DROPS` | `('Мясо моллюска', 'Жемчужина')` |  | :613 |
| `MINE_AP_COST` | `12` | стоимость одной попытки добычи | :622 |
| `MINE_BASE_CHANCE` | `30` | базовый шанс успеха без бонуса кирки | :623 |
| `MINE_PICKAXE_BONUS_PER_RANK` | `15` | надбавка к шансу за ступень кирки (ранг 1 → +15%) | :624 |
| `MINE_CHANCE_CAP` | `90` | потолок шанса успеха | :625 |
| `MINE_RESULT_DELAY` | `(7, 15)` | результат добычи через 7–15 секунд | :626 |
| `MINE_REQUIRED_STATUS` | `'pilot1'` | вход в копь — с «Пилота 1 класса» | :627 |
| `MINE_GEM_CAP` | `1` | из самоцветов за бой выпадает не больше одного | :628 |
| `MINE_PICKAXE_NAME` | `'Кирка'` |  | :629 |
| `MINE_ORE_NAME` | `'Железная руда'` |  | :630 |
| `MINE_BAT_KEY` | `'bat'` |  | :633 |
| `MINE_BAT_SPOT` | `'iron'` |  | :634 |
| `MINE_BAT_CHANCE` | `7.0` |  | :635 |
| `MINE_BAT_PITY_TARGET` | `12` |  | :636 |
| `MINE_BAT_SEED` | `{'key': MINE_BAT_KEY, 'spot': MINE_BAT_SPOT, 'name': 'Летучая мышь', 'hp': 22, 'dmg_min': 3, 'dmg_max': 7, 'dodge': 35, 'loss_ap': 15, 'chance': MINE_BAT_CHANCE, 'pity_target': MINE_BAT_PITY_TARGET…` |  | :641 |
| `MINE_ITEM_SEEDS` | `[(MINE_PICKAXE_NAME, 'Простая кирка шахтёра: без неё в штольню не сунешься, а с ней порода поддаётся легче. Повышает шанс успешной добычи руды.', 300, 150, 1, 'mining', 0), (MINE_ORE_NAME, 'Кусок ж…` |  | :667 |
| `MINE_SHOP_ITEMS` | `(MINE_PICKAXE_NAME,)` |  | :688 |
| `MINE_ENEMY_DROPS` | `('Изумруд', 'Рубин', 'Сапфир')` |  | :691 |
| `ON_HIT_EFFECTS` | `{'bleed': {'emoji': '🩸', 'title': 'Кровотечение', 'until_battle_end': True, 'params': (('chance', 'Шанс наложить, %', 'percent'), ('dmg', 'Урон, HP за ход', 'int')), 'hint': 'Раны сочатся кровью ка…` |  | :700 |
| `ON_HIT_KIND_ORDER` | `('bleed', 'poison', 'frostbite', 'state', 'lifesteal')` |  | :754 |
| `ON_HIT_STATE_ROUNDS` | `{'оглушён': 3, 'ослеплён': 4}` |  | :756 |
| `CLAN_ROLES` | `{'leader': '👑 Глава клана', 'seneschal': '🛡 Сенешаль клана', 'banner': '🚩 Знаменосец клана', 'elder': '⭐ Старшина', 'member': '▪️ Член клана'}` |  | :762 |
| `CLAN_ROLE_ORDER` | `('leader', 'seneschal', 'banner', 'elder', 'member')` |  | :769 |
| `LOGGING_AP_COST` | `12` | стоимость одной попытки рубки | :775 |
| `LOGGING_BASE_CHANCE` | `35` | базовый шанс успеха без бонуса топора | :776 |
| `LOGGING_AXE_BONUS_PER_RANK` | `15` | надбавка к шансу за ступень топора | :777 |
| `LOGGING_CHANCE_CAP` | `90` | потолок шанса успеха | :778 |
| `LOGGING_AXE_SLIP_CHANCE` | `2.5` | шанс, что топор отскочит пилоту в плечо, % | :779 |
| `LOGGING_RESULT_DELAY` | `(7, 15)` | результат рубки через 7–15 секунд | :780 |
| `LOGGING_AXE_NAME` | `'Топор'` |  | :781 |
| `LOGGING_WOOD_NAME` | `'Бревна'` |  | :782 |
| `LOGGING_PLANK_NAME` | `'Доска'` |  | :788 |
| `LOGGING_FIREWOOD_NAME` | `'Пак дров'` |  | :789 |
| `LOGGING_PLANK_YIELD` | `3` | досок из одного бревна | :790 |
| `LOGGING_PLANK_FEE` | `15` | НМ за распил одного бревна (в казну) | :791 |
| `LOGGING_FIREWOOD_YIELD` | `3` | паков дров из одного бревна | :792 |
| `LOGGING_FIREWOOD_AP_COST` | `4` | ОД за рубку дров из одного бревна | :793 |
| `LOGGING_SNAKE_KEY` | `'snake'` |  | :797 |
| `LOGGING_OWL_KEY` | `'owl'` |  | :798 |
| `LOGGING_SPOT` | `'logging'` |  | :799 |
| `LOGGING_SNAKE_CHANCE` | `8.0` |  | :800 |
| `LOGGING_SNAKE_PITY_TARGET` | `10` |  | :801 |
| `LOGGING_OWL_CHANCE` | `3.0` |  | :802 |
| `LOGGING_OWL_PITY_TARGET` | `24` |  | :803 |
| `LOGGING_SNAKE_POISON_CHANCE` | `30` |  | :805 |
| `LOGGING_SNAKE_POISON_DMG` | `2` |  | :806 |
| `LOGGING_OWL_FLEE_HP` | `20` |  | :810 |
| `LOGGING_OWL_BLIND_CHANCE` | `30` |  | :811 |
| `LOGGING_OWL_BLIND_ROUNDS` | `4` |  | :812 |
| `LOGGING_SNAKE_SEED` | `{'key': LOGGING_SNAKE_KEY, 'spot': LOGGING_SPOT, 'name': 'Лесная змея', 'hp': 30, 'dmg_min': 4, 'dmg_max': 8, 'dodge': 25, 'loss_ap': 10, 'chance': LOGGING_SNAKE_CHANCE, 'pity_target': LOGGING_SNAK…` |  | :816 |
| `LOGGING_OWL_SEED` | `{'key': LOGGING_OWL_KEY, 'spot': LOGGING_SPOT, 'name': 'Неясыть', 'hp': 90, 'dmg_min': 7, 'dmg_max': 12, 'dodge': 30, 'loss_ap': 15, 'chance': LOGGING_OWL_CHANCE, 'pity_target': LOGGING_OWL_PITY_TA…` |  | :846 |
| `LOGGING_ITEM_SEEDS` | `[(LOGGING_AXE_NAME, 'Крепкий лесорубский топор: без него к срубам не подпустят. Повышает шанс успешной рубки деревьев.', 300, 150, 1, 'mining', 0), (LOGGING_WOOD_NAME, 'Свежие срубленные брёвна из …` |  | :878 |
| `LOGGING_SHOP_ITEMS` | `(LOGGING_AXE_NAME,)` |  | :912 |
| `LOGGING_ENEMY_DROPS` | `('Змеиная кожа', 'Змеиный яд', 'Совиное перо')` |  | :915 |
| `LOGGING_MARKET_RESOURCES` | `(LOGGING_PLANK_NAME, LOGGING_FIREWOOD_NAME)` |  | :918 |
| `REPORT_DAILY_LIMIT` | `3` |  | :920 |
| `REPORT_AUTO_APPROVE_TROOPS` | `100` |  | :921 |
| `NEWS_PUBLISH_BONUS` | `10` |  | :925 |
| `NEWS_PUBLISH_CAP` | `28` |  | :926 |
| `ROLE_SALARY_PAY_DAY` | `28` |  | :929 |
| `REPORT_DAILY_PAY_CAP` | `4000` |  | :934 |
| `REPORT_MAX_TROOPS` | `1000000` |  | :935 |
| `REPORT_MAX_REGION` | `38` | 0 = Столица, 1..38 регионы | :936 |
| `WALL_TEXT_MAX_LEN` | `40` | лимит символов на одно изречение | :939 |
| `WALL_FREE_PER_DAY` | `2` | бесплатных сообщений в сутки | :940 |
| `WALL_PAID_STEPS` | `[(3, 30), (3, 90), (3, 200)]` | далее платные ступени: (кол-во, цена НМ) | :941 |
| `WALL_REVIEW_TOTAL` | `11` | максимум сообщений в сутки (2 + 3+3+3) | :946 |
| `WALL_PAGE_SIZE` | `5` | постов на страницу стены | :947 |
| `WALL_ARCHIVE_PAGE_SIZE` | `8` | записей архива стены на страницу списка | :948 |
| `REPORT_ARCHIVE_PAGE` | `8` | отчётов на страницу архива МВД и в «Моих отчётах» | :951 |
| `POLL_MAX_DAYS` | `10` | максимум дней, сколько живёт опрос. Не закрыл | :954 |
| `POLL_VISIBLE` | `4` | сколько новейших опросов висит в меню голосования. | :957 |
| `POLL_ARCHIVE_DAYS_PER_PAGE` | `5` | дней (дат) архива опросов на страницу списка | :960 |
| `POLL_ARCHIVE_PER_DAY` | `6` | опросов под одним заголовком-днём | :961 |
| `REP_SPEECH_MAX_LEN` | `100` | лимит символов одного обращения | :964 |
| `REP_SPEECH_PER_DAY` | `2` | обращений в сутки от представителя | :965 |
| `AUTO_PROMOTE_MAX_TROOPS` | `4040` |  | :970 |

## Буклет туриста

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `TOURIST_BOOKLET_NAME` | `'Буклет туриста'` |  | :23 |

## Суточный цикл Нордхайма

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `REPORT_DAY_START_HOUR` | `10` |  | :165 |

## Дом Дуэлей (PvP-арена)

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `DUEL_ZONES` | `('head', 'body', 'hands', 'legs')` |  | :262 |

## Рынок: слоты продажи

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `MARKET_BASE_SLOTS` | `1` | слоты без лицензии | :337 |

## Налог на недвижимость (НМ/мес)

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `HOUSING_TAX` | `{'municipal': 0, 'studio': 20, 'apartment': 35, 'improved': 60, 'mansion': 100}` |  | :343 |

## Банк: лимит счёта туриста (НМ)

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `TOURIST_BALANCE_LIMIT` | `200` |  | :353 |

## Данж: лимит хила (количество применений за забег)

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `DUNGEON_HEAL_SOFT_LIMIT` | `6` | после этого — ×2/3 | :356 |

## Сброс протухших забегов подземелья

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `DUNGEON_RUN_STALE_SEC` | `3600` |  | :365 |

## Данж: побег и дымовая шашка

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `ESCAPE_BASE_CHANCE` | `25` |  | :373 |

