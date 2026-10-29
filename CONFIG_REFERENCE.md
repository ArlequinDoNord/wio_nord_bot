# Справочник констант `config.py`

> **Сгенерировано** `tools/export_config.py`. Перегенерация:
> `.venv\Scripts\python.exe tools/export_config.py`.
>
> Все модульные константы `config.py`, сгруппированные по секциям
> (комментариям-разделителям `# ── … ──`). Длинные значения усечены `…`;
> точное значение — в `config.py` по строке из первой колонки.

Всего констант: **271**; разделов: **10**.

## Без раздела

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `VERSION` | `'0.39.11'` |  | :16 |
| `VERSION_NOTES` | `'Подготовка к празднику: правила стали чуть строже и честнее.'` |  | :17 |
| `PREV_VERSION` | `'0.39.10'` |  | :19 |
| `PREV_VERSION_NOTES` | `'Подготовка к празднику продолжается: мелочи отточены.'` |  | :20 |
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
| `FIRELAB_SCARECROW_HP` | `25` |  | :47 |
| `FIRELAB_SCARECROW_DMG` | `(3, 5)` |  | :48 |
| `FIRELAB_SCARECROW_DODGE` | `10` |  | :49 |
| `FIRELAB_SCARECROW_ARMOR` | `1` | броня Пугала (стены соломы) | :50 |
| `FIRELAB_APPLE_CHILD_HP` | `27` |  | :51 |
| `FIRELAB_APPLE_CHILD_DMG` | `(2, 4)` |  | :52 |
| `FIRELAB_APPLE_CHILD_DODGE` | `9` |  | :53 |
| `FIRELAB_CROW_HP` | `16` |  | :54 |
| `FIRELAB_CROW_DMG` | `(2, 4)` |  | :55 |
| `FIRELAB_CROW_DODGE` | `20` |  | :56 |
| `FIRELAB_GHOST_HP` | `24` |  | :57 |
| `FIRELAB_GHOST_DMG` | `(2, 4)` |  | :58 |
| `FIRELAB_GHOST_DODGE` | `15` |  | :59 |
| `FIRELAB_PUMPKIN_HP` | `60` |  | :60 |
| `FIRELAB_PUMPKIN_DMG` | `(4, 7)` |  | :61 |
| `FIRELAB_PUMPKIN_DODGE` | `5` |  | :62 |
| `FIRELAB_PUMPKIN_ARMOR` | `2` | броня босса | :63 |
| `FIRELAB_SCARECROW_SEED` | `{'key': 'scarecrow', 'spot': 'firelab', 'name': 'Пугало', 'hp': FIRELAB_SCARECROW_HP, 'dmg_min': FIRELAB_SCARECROW_DMG[0], 'dmg_max': FIRELAB_SCARECROW_DMG[1], 'dodge': FIRELAB_SCARECROW_DODGE, 'ar…` |  | :65 |
| `FIRELAB_APPLE_CHILD_SEED` | `{'key': 'apple_child', 'spot': 'firelab', 'name': 'Дитя Яблони', 'hp': FIRELAB_APPLE_CHILD_HP, 'dmg_min': FIRELAB_APPLE_CHILD_DMG[0], 'dmg_max': FIRELAB_APPLE_CHILD_DMG[1], 'dodge': FIRELAB_APPLE_C…` |  | :86 |
| `FIRELAB_CROW_SEED` | `{'key': 'crow', 'spot': 'firelab', 'name': 'Ворон', 'hp': FIRELAB_CROW_HP, 'dmg_min': FIRELAB_CROW_DMG[0], 'dmg_max': FIRELAB_CROW_DMG[1], 'dodge': FIRELAB_CROW_DODGE, 'loss_ap': 0, 'chance': 0, 'p…` |  | :106 |
| `FIRELAB_GHOST_SEED` | `{'key': 'ghost', 'spot': 'firelab', 'name': 'Призрак', 'hp': FIRELAB_GHOST_HP, 'dmg_min': FIRELAB_GHOST_DMG[0], 'dmg_max': FIRELAB_GHOST_DMG[1], 'dodge': FIRELAB_GHOST_DODGE, 'loss_ap': 0, 'chance'…` |  | :126 |
| `FIRELAB_PUMPKIN_SEED` | `{'key': 'pumpkin_boss', 'spot': 'firelab', 'name': 'Мощный Мистер Огненная Тыква', 'hp': FIRELAB_PUMPKIN_HP, 'dmg_min': FIRELAB_PUMPKIN_DMG[0], 'dmg_max': FIRELAB_PUMPKIN_DMG[1], 'dodge': FIRELAB_P…` |  | :146 |
| `FIRELAB_ENEMY_SEEDS` | `(FIRELAB_SCARECROW_SEED, FIRELAB_APPLE_CHILD_SEED, FIRELAB_CROW_SEED, FIRELAB_GHOST_SEED, FIRELAB_PUMPKIN_SEED)` |  | :167 |
| `FIRE_EVENT_ENABLED` | `True` |  | :175 |
| `FIRE_EVENT_START` | `(2026, 10, 30, 0, 0)` | МСК, ночь на пятницу 30.10 | :176 |
| `FIRE_EVENT_DURATION_DAYS` | `5` | до ~00:00 МСК 4.11 | :177 |
| `FIRE_LAB_ENABLED` | `False` |  | :179 |
| `FIRE_EVENT_LAB_FEE` | `42` | вход в лабиринт, НМ | :180 |
| `FIRE_EVENT_MAX_ENTRIES_DAY` | `4` | максимум заходов за сутки | :181 |
| `FIRE_LAB_SESSION_TTL_SEC` | `3600` | неактивность: сессия закрывается автоматически (1 ч) | :182 |
| `FIRE_LAB_SCARECROW_BLIND_P` | `0.15` | Пугало: «сено в лицо» — ослепление | :187 |
| `FIRE_LAB_APPLE_STUN_P` | `0.1` | Дитя Яблони: «яблочко» — оглушение | :188 |
| `FIRE_LAB_CROW_BLIND_P` | `0.15` | Ворон: ослепление (как сова) | :189 |
| `FIRE_LAB_GHOST_FROST_P` | `0.2` | Призрак: обморожение на 3 хода | :190 |
| `FIRE_LAB_GHOST_FROST_ROUNDS` | `3` |  | :191 |
| `FIRE_LAB_BOSS_BURN_P` | `0.25` | Босс «Мистер Тыква»: поджиг игрока | :192 |
| `FIRE_LAB_BOSS_BURN_DMG` | `2` | −HP/ход | :193 |
| `FIRE_LAB_BOSS_BURN_ROUNDS` | `3` |  | :194 |
| `FIRE_LAB_BOSS_MAX` | `2` | максимум встреч с боссом за заход | :195 |
| `FIRE_LAB_ROOMS_MAX` | `25` | после 25 комнат-развилок выход автоматом | :196 |
| `FIRE_LAB_TIER_MAX` | `5` | кап усилений | :199 |
| `FIRE_LAB_TIER_HP_STEP` | `2` | +HP всем врагам за тир (1–4) | :200 |
| `FIRE_LAB_TIER_HP_LAST` | `8` | 5-й тир: разово +8 (итого +16) | :201 |
| `FIRE_LAB_TIER_LOOT_STEP` | `0.02` | лут ×(1+2%) за тир (1–4) | :202 |
| `FIRE_LAB_TIER_LOOT_LAST` | `0.1` | 5-й тир: ×(1+10%) | :203 |
| `FIRE_LAB_P_WELL` | `0.07` | Колодец (перебивается паттерном ЛЛПП) | :206 |
| `FIRE_LAB_WELL_MAX` | `3` | максимум посещений за заход | :207 |
| `FIRE_LAB_P_TREE` | `0.09` | Древо Огня (перебивается ЛЛППНН) | :208 |
| `FIRE_LAB_TREE_MAX` | `1` | раз за заход | :209 |
| `FIRE_LAB_P_CHEST` | `0.1` | Сундук сокровищ | :210 |
| `FIRE_LAB_CHEST_MAX` | `2` | максимум за заход | :211 |
| `FIRE_TREE_DMG_BONUS_PCT` | `15` | +15% урона | :214 |
| `FIRE_TREE_REGEN_HP` | `1` | +1 HP после каждого удара игрока | :215 |
| `FIRE_LAB_PATTERN_WELL` | `('L', 'L', 'S', 'S')` | ЛЛПП → Колодец (до 3) | :219 |
| `FIRE_LAB_PATTERN_TREE` | `('L', 'L', 'S', 'S', 'R', 'R')` | ЛЛППНН → Древо Огня (1) | :220 |
| `CLAN_BUILDING_TYPES` | `{'house': {'name': 'Дом Клана', 'slots': 2, 'max_level': 2, 'days': 2, 'price_nm': 3000, 'required': {'Доска': 60, 'Бревна': 20, 'Железная руда': 15}}, 'manor': {'name': 'Клановое поместье', 'slots…` |  | :222 |
| `CLAN_BUILDING_NO_RESOURCES_MULT` | `2` |  | :237 |
| `CLAN_EXPANSION_TYPES` | `('kitchen', 'workbench', 'shower', 'garden', 'library', 'shop')` |  | :239 |
| `CLAN_EXPANSION_INFO` | `{'kitchen': {'name': 'Кухня', 'icon': '🍳', 'desc': 'Готовка по выученным рецептам; уровень задаёт доступные блюда.'}, 'workbench': {'name': 'Крафтовый стол', 'icon': '🛠', 'desc': 'Крафт снаряжения …` |  | :241 |
| `CLAN_EXPANSION_UPGRADE` | `{2: {'nm': 1500, 'required': {'Доска': 20, 'Железная руда': 10}}, 3: {'nm': 4000, 'required': {'Доска': 50, 'Железная руда': 30}}, 4: {'nm': 9000, 'required': {'Доска': 100, 'Железная руда': 60}}}` |  | :256 |
| `CLAN_SHOWER_AP_BY_LEVEL` | `{1: 25, 2: 50, 3: 75, 4: 100}` |  | :264 |
| `CLAN_SHOWER_SOBER_MINUTES` | `{1: 60, 2: 120, 3: 180, 4: 240}` |  | :265 |
| `CLAN_GARDEN_PLOTS` | `{1: 2, 2: 3, 3: 4, 4: 6}` |  | :267 |
| `CLAN_SHOP_DAILY_LIMIT` | `3` |  | :268 |
| `CLAN_SHOP_DISCOUNT` | `10` |  | :269 |
| `BOT_TOKEN` | `os.getenv('BOT_TOKEN')` |  | :271 |
| `ADMIN_IDS` | `[int(x) for x in os.getenv('ADMIN_IDS', '').split(',') if x.strip()]` |  | :272 |
| `_news_raw` | `os.getenv('NEWS_CHAT_ID', '').strip()` |  | :275 |
| `NEWS_CHAT_ID` | `int(_news_raw) if _news_raw.lstrip('-').isdigit() else None` |  | :276 |
| `DB_PATH` | `os.getenv('DATABASE_PATH', 'database/nordmark.db')` |  | :279 |
| `FSM_STORAGE_PATH` | `os.getenv('FSM_STORAGE_PATH', '').strip() or os.path.join(os.path.dirname(os.path.abspath(DB_PATH)), 'fsm')` |  | :288 |
| `REPORT_DAY_START_MINUTE` | `0` |  | :298 |
| `RANKS` | `[('Рекрут', 0), ('Рядовой', 100), ('Ефрейтор', 350), ('Капрал', 500), ('Сержант', 850), ('Старший Сержант', 1500), ('Лейтенант', 2500), ('Старший Лейтенант', 4040), ('Капитан', 6000), ('Майор', 850…` |  | :300 |
| `MAX_SELF_RANK_TROOPS` | `4040` |  | :321 |
| `AUTO_RANK_NAMES` | `('Рекрут', 'Рядовой', 'Ефрейтор', 'Капрал', 'Сержант', 'Старший Сержант', 'Лейтенант', 'Старший Лейтенант')` |  | :324 |
| `AWARD_MAX_SHOP_DISCOUNT` | `40` |  | :331 |
| `AWARD_MIN_REPORT_TAX` | `5` |  | :332 |
| `RANK_STATUS_TAGS` | `{'Ефрейтор': 'pilot2', 'Старший Сержант': 'pilot1', 'Старший Лейтенант': 'veteran', 'Майор': 'master_pilot', 'Полковник': 'ace'}` |  | :334 |
| `LEGIONER_ACCESS_CAP_ORDER` | `5` |  | :347 |
| `RANK_DAMAGE_TIERS` | `{'ace': (4, 8), 'master_pilot': (3, 5), 'veteran': (2, 4), 'pilot1': (1, 3), 'pilot2': (1, 2), 'recruit': (1, 1), 'tourist': (0, 1)}` |  | :353 |
| `RANK_CRIT_CHANCE` | `{'ace': 7.5, 'master_pilot': 6.0, 'veteran': 4.5, 'pilot1': 3.0, 'pilot2': 1.5, 'recruit': 0.0, 'tourist': 0.0}` |  | :371 |
| `PILOT_CRIT_MULT` | `1.4` |  | :385 |
| `PILOT_NO_WEAPON_DMG` | `(1, 1)` |  | :388 |
| `DUEL_ZONE_LABELS` | `{'head': 'Голова', 'body': 'Тело', 'hands': 'Руки', 'legs': 'Ноги'}` |  | :395 |
| `DUEL_ZONE_EMOJI` | `{'head': '🧠', 'body': '🫀', 'hands': '✊', 'legs': '🦵'}` |  | :401 |
| `DUEL_AP_COST` | `15` | списывается с обоих при старте боя | :407 |
| `DUEL_RATING_WIN` | `2` | рейтинг за победу | :408 |
| `DUEL_RATING_LOSS` | `-3` | рейтинг за поражение | :409 |
| `DUEL_RATING_DRAW` | `0` | рейтинг за ничью | :410 |
| `DUEL_RATING_FORFEIT` | `-1` | рейтинг тому, кто покинул бой («Покинуть дуэль») | :411 |
| `DUEL_RATING_FORFEIT_WIN` | `1` | рейтинг сопернику, если противник покинул бой (меньше чистой победы) | :412 |
| `DUEL_MIN_DAMAGE` | `1` | минимум урона за попавший (не уклонённый) удар | :413 |
| `DUEL_GUARD_REDUCTION` | `0.5` | доля урона, остающаяся при угаданной зоне защиты | :414 |
| `DUEL_HEAL_BETWEEN` | `0` | восстановление HP между раундами (пока нет) | :415 |
| `DUEL_CHALLENGE_TIMEOUT_SEC` | `120` | сколько живёт неотвеченный вызов | :416 |
| `DUEL_STALE_SEC` | `1800` | зависшая дуэль авто-завершается как void | :417 |
| `DUEL_GLOVES_NAME` | `'Дуэльные перчатки'` |  | :418 |
| `DUEL_GLOVES_DAMAGE` | `7` |  | :419 |
| `DUEL_GLOVES_PRICE` | `200` |  | :420 |
| `DUEL_GLOVES_SELL` | `100` |  | :421 |
| `DUEL_CLUB_CARD_NAME` | `'Клубная карта «Дом Дуэлей»'` |  | :422 |
| `DUEL_CLUB_CARD_PRICE` | `150` |  | :423 |
| `DUEL_CLUB_CARD_SELL` | `75` |  | :424 |
| `DUEL_CLUB_CARD_DAYS` | `30` |  | :425 |
| `DUEL_ACCESS_TAG` | `'pilot2'` |  | :428 |
| `RARITY_LEVELS` | `{1: 'Обычный', 2: 'Качественный', 3: 'Редкий', 4: 'Шедевр', 5: 'Легендарный'}` |  | :430 |
| `RARITY_EMOJI` | `{1: '⬜', 2: '🟩', 3: '🟦', 4: '🟪', 5: '🟧'}` |  | :438 |
| `ITEM_CATEGORIES` | `{'weapon': 'Оружие', 'consumable': 'Расходники', 'building': 'Недвижимость', 'housing': 'Жильё', 'furniture': 'Мебель и расширения', 'seeds': 'Семена', 'equipment': 'Одежда', 'resource': 'Ресурсы',…` |  | :446 |
| `MARKET_LICENSE_SLOTS` | `2` | доп. слоты при активной лицензии | :470 |
| `MARKET_LICENSE_DAYS` | `30` | срок действия лицензии (дней) | :471 |
| `MARKET_LICENSE_PRICE` | `500` | цена лицензии в НМ | :472 |
| `DUNGEON_HEAL_HARD_LIMIT` | `10` | после этого — ×1/2 | :489 |
| `DUNGEON_HEAL_SOFT_MULT` | `2 / 3` |  | :490 |
| `DUNGEON_HEAL_HARD_MULT` | `1 / 2` |  | :491 |
| `ESCAPE_HP_BONUS` | `20` |  | :506 |
| `DUNGEON_SMOKE_ESCAPE` | `95` |  | :507 |
| `DUNGEON_SMOKE_MAX` | `2` |  | :508 |
| `DUNGEON_ESCAPE_DRUNK_MULT` | `0.5` |  | :511 |
| `AP_MAX` | `150` |  | :513 |
| `AP_DAILY_RECOVERY` | `100` |  | :514 |
| `AP_BONUS_FROM_CONSUMABLE` | `50` |  | :515 |
| `AP_DAILY_RESTORE_LIMIT` | `150` |  | :520 |
| `AP_EXHAUSTED_MINUTES` | `2880` | 2 суток | :521 |
| `AP_EXHAUSTED_DAILY_RECOVERY` | `75` | суточное восстановление в «истощении» | :522 |
| `AP_EXHAUSTED_MAX_AP` | `90` | максимум ОД в «истощении» | :523 |
| `SEAWEED_DAILY_LIMIT` | `6` |  | :526 |
| `DIGESTIVE_UPSET_MINUTES` | `1440` | 24 часа | :527 |
| `ALCOHOL_WEAK_DRUNK_LIMIT` | `3` |  | :532 |
| `ALCOHOL_WEAK_VERY_DRUNK_LIMIT` | `6` |  | :533 |
| `ALCOHOL_STRONG_DRUNK_LIMIT` | `1` |  | :535 |
| `ALCOHOL_STRONG_VERY_DRUNK_LIMIT` | `2` |  | :536 |
| `DRUNK_MINUTES` | `60` |  | :537 |
| `VERY_DRUNK_MINUTES` | `360` | 6 часов | :538 |
| `DRINK_EFFECT_LABELS` | `{'alcohol_weak': '🍺 Слабоалкогольный: 3 шт/сутки — «пьян», 6 — «очень пьян»', 'alcohol_strong': '🥃 Крепкий алкоголь: 1 шт — «пьян», 2 — «очень пьян»', 'indigestion': '🤢 Вызывает «несварение» на сут…` |  | :541 |
| `SPECIAL_DEPT_CODE_MIN_LEN` | `4` |  | :552 |
| `SPECIAL_DEPT_CODE_MAX_LEN` | `8` |  | :553 |
| `SPECIAL_DEPT_ATTEMPTS_LIMIT` | `3` | ошибок кода подряд | :554 |
| `SPECIAL_DEPT_BLOCK_MINUTES` | `1440` | бан на 24 часа после 3 ошибок | :555 |
| `FISH_AP_COST` | `3` | стоимость одного заброса удочки | :558 |
| `RESERVOIR_AP_COST` | `5` |  | :563 |
| `FISH_WEIGHTS` | `[{'key': 'small', 'label': 'Мелкая', 'mult': 1.0, 'chance': 40}, {'key': 'medium', 'label': 'Средняя', 'mult': 1.15, 'chance': 40}, {'key': 'large', 'label': 'Большая', 'mult': 1.25, 'chance': 20}]` |  | :568 |
| `FISH_TREASURY_SALE_MULT` | `0.5` |  | :576 |
| `FISH_TREASURY_DAILY_LIMIT` | `300` |  | :581 |
| `FOREST_AP_COST` | `4` | запасной цена поиска, если у зоны нет ap_cost в БД | :584 |
| `FOREST_RESULT_DELAY` | `(5, 10)` | результат поиска через 5–10 секунд | :587 |
| `FOREST_SOLD_DAILY_LIMIT` | `250` |  | :592 |
| `FOREST_ALLOW_TOURISTS` | `False` |  | :597 |
| `FOREST_BOAR_PITY_TARGET` | `12` |  | :600 |
| `FOREST_BOAR_CHANCE` | `4.0` |  | :604 |
| `CALLSIGN_PRICE` | `500` |  | :606 |
| `PILOT_BASE_HP` | `100` |  | :608 |
| `FOREST_BOAR_HP` | `40` |  | :613 |
| `FOREST_BOAR_DMG` | `(4, 7)` |  | :614 |
| `FOREST_BOAR_DODGE` | `15` |  | :615 |
| `FOREST_BOAR_LOSS_AP` | `10` |  | :617 |
| `FOREST_BOAR_LOOT` | `[('Мясо кабана', 50), ('Шкура кабана', 20), ('Клык кабана', 10), ('', 20)]` |  | :619 |
| `FOREST_WHITE_WOLF_HP` | `120` |  | :631 |
| `FOREST_WHITE_WOLF_DMG` | `(7, 12)` |  | :632 |
| `FOREST_WHITE_WOLF_DODGE` | `20` |  | :633 |
| `FOREST_WHITE_WOLF_LOSS_AP` | `15` |  | :635 |
| `FOREST_WHITE_WOLF_CHANCE` | `2.0` |  | :636 |
| `FOREST_WHITE_WOLF_PITY_TARGET` | `36` |  | :639 |
| `FOREST_WHITE_WOLF_BLEED_CHANCE` | `30` |  | :641 |
| `FOREST_WHITE_WOLF_BLEED_DMG` | `3` |  | :642 |
| `FOREST_WHITE_WOLF_AUTOWIN_HP` | `20` |  | :644 |
| `FOREST_WHITE_WOLF_SMALL_BLESSING` | `'внимание севера'` |  | :646 |
| `FOREST_WHITE_WOLF_BIG_BLESSING` | `'благословение севера'` |  | :647 |
| `FOREST_BOAR_SEED` | `{'key': 'boar', 'spot': 'forest', 'name': 'Дикий кабан', 'hp': FOREST_BOAR_HP, 'dmg_min': FOREST_BOAR_DMG[0], 'dmg_max': FOREST_BOAR_DMG[1], 'dodge': FOREST_BOAR_DODGE, 'loss_ap': FOREST_BOAR_LOSS_…` |  | :654 |
| `FOREST_WHITE_WOLF_SEED` | `{'key': 'white_wolf', 'spot': 'forest', 'name': 'Белый Волк Севера', 'hp': FOREST_WHITE_WOLF_HP, 'dmg_min': FOREST_WHITE_WOLF_DMG[0], 'dmg_max': FOREST_WHITE_WOLF_DMG[1], 'dodge': FOREST_WHITE_WOLF…` |  | :679 |
| `MOLLUSK_SEED` | `{'key': 'mollusk', 'spot': 'reservoir', 'name': 'Мутировавший моллюск', 'hp': 24, 'dmg_min': 5, 'dmg_max': 9, 'dodge': 20, 'loss_ap': 12, 'chance': 4, 'pity_target': 0, 'reward_nm': 0, 'photo_key':…` |  | :707 |
| `MOLLUSK_ITEM_SEEDS` | `[('Мясо моллюска', 'Плотное мясо мутировавшего моллюска. В сыром виде есть нельзя — прожарь на кухне.', 120, 60, 3, 'resource', 0), ('Жемчужина', 'Редчайшая жемчужина из раковины мутировавшего молл…` |  | :730 |
| `MOLLUSK_ENEMY_DROPS` | `('Мясо моллюска', 'Жемчужина')` |  | :745 |
| `MINE_AP_COST` | `12` | стоимость одной попытки добычи | :754 |
| `MINE_BASE_CHANCE` | `30` | базовый шанс успеха без бонуса кирки | :755 |
| `MINE_PICKAXE_BONUS_PER_RANK` | `15` | надбавка к шансу за ступень кирки (ранг 1 → +15%) | :756 |
| `MINE_CHANCE_CAP` | `90` | потолок шанса успеха | :757 |
| `MINE_RESULT_DELAY` | `(7, 15)` | результат добычи через 7–15 секунд | :758 |
| `MINE_REQUIRED_STATUS` | `'pilot1'` | вход в копь — с «Пилота 1 класса» | :759 |
| `MINE_GEM_CAP` | `1` | из самоцветов за бой выпадает не больше одного | :760 |
| `MINE_PICKAXE_NAME` | `'Кирка'` |  | :761 |
| `MINE_ORE_NAME` | `'Железная руда'` |  | :762 |
| `MINE_BAT_KEY` | `'bat'` |  | :765 |
| `MINE_BAT_SPOT` | `'iron'` |  | :766 |
| `MINE_BAT_CHANCE` | `7.0` |  | :767 |
| `MINE_BAT_PITY_TARGET` | `12` |  | :768 |
| `MINE_BAT_SEED` | `{'key': MINE_BAT_KEY, 'spot': MINE_BAT_SPOT, 'name': 'Летучая мышь', 'hp': 22, 'dmg_min': 3, 'dmg_max': 7, 'dodge': 35, 'loss_ap': 15, 'chance': MINE_BAT_CHANCE, 'pity_target': MINE_BAT_PITY_TARGET…` |  | :773 |
| `MINE_ITEM_SEEDS` | `[(MINE_PICKAXE_NAME, 'Простая кирка шахтёра: без неё в штольню не сунешься, а с ней порода поддаётся легче. Повышает шанс успешной добычи руды.', 300, 150, 1, 'mining', 0), (MINE_ORE_NAME, 'Кусок ж…` |  | :799 |
| `MINE_SHOP_ITEMS` | `(MINE_PICKAXE_NAME,)` |  | :820 |
| `MINE_ENEMY_DROPS` | `('Изумруд', 'Рубин', 'Сапфир')` |  | :823 |
| `ON_HIT_EFFECTS` | `{'bleed': {'emoji': '🩸', 'title': 'Кровотечение', 'until_battle_end': True, 'params': (('chance', 'Шанс наложить, %', 'percent'), ('dmg', 'Урон, HP за ход', 'int')), 'hint': 'Раны сочатся кровью ка…` |  | :832 |
| `ON_HIT_KIND_ORDER` | `('bleed', 'poison', 'frostbite', 'state', 'lifesteal')` |  | :886 |
| `ON_HIT_STATE_ROUNDS` | `{'оглушён': 3, 'ослеплён': 4}` |  | :888 |
| `CLAN_ROLES` | `{'leader': '👑 Глава клана', 'seneschal': '🛡 Сенешаль клана', 'banner': '🚩 Знаменосец клана', 'elder': '⭐ Старшина', 'member': '▪️ Член клана'}` |  | :894 |
| `CLAN_ROLE_ORDER` | `('leader', 'seneschal', 'banner', 'elder', 'member')` |  | :901 |
| `LOGGING_AP_COST` | `12` | стоимость одной попытки рубки | :907 |
| `LOGGING_BASE_CHANCE` | `35` | базовый шанс успеха без бонуса топора | :908 |
| `LOGGING_AXE_BONUS_PER_RANK` | `15` | надбавка к шансу за ступень топора | :909 |
| `LOGGING_CHANCE_CAP` | `90` | потолок шанса успеха | :910 |
| `LOGGING_AXE_SLIP_CHANCE` | `2.5` | шанс, что топор отскочит пилоту в плечо, % | :911 |
| `LOGGING_RESULT_DELAY` | `(7, 15)` | результат рубки через 7–15 секунд | :912 |
| `LOGGING_AXE_NAME` | `'Топор'` |  | :913 |
| `LOGGING_WOOD_NAME` | `'Бревна'` |  | :914 |
| `LOGGING_PLANK_NAME` | `'Доска'` |  | :920 |
| `LOGGING_FIREWOOD_NAME` | `'Пак дров'` |  | :921 |
| `LOGGING_PLANK_YIELD` | `3` | досок из одного бревна | :922 |
| `LOGGING_PLANK_FEE` | `15` | НМ за распил одного бревна (в казну) | :923 |
| `LOGGING_FIREWOOD_YIELD` | `3` | паков дров из одного бревна | :924 |
| `LOGGING_FIREWOOD_AP_COST` | `4` | ОД за рубку дров из одного бревна | :925 |
| `LOGGING_SNAKE_KEY` | `'snake'` |  | :929 |
| `LOGGING_OWL_KEY` | `'owl'` |  | :930 |
| `LOGGING_SPOT` | `'logging'` |  | :931 |
| `LOGGING_SNAKE_CHANCE` | `8.0` |  | :932 |
| `LOGGING_SNAKE_PITY_TARGET` | `10` |  | :933 |
| `LOGGING_OWL_CHANCE` | `3.0` |  | :934 |
| `LOGGING_OWL_PITY_TARGET` | `24` |  | :935 |
| `LOGGING_SNAKE_POISON_CHANCE` | `30` |  | :937 |
| `LOGGING_SNAKE_POISON_DMG` | `2` |  | :938 |
| `LOGGING_OWL_FLEE_HP` | `20` |  | :942 |
| `LOGGING_OWL_BLIND_CHANCE` | `30` |  | :943 |
| `LOGGING_OWL_BLIND_ROUNDS` | `4` |  | :944 |
| `LOGGING_SNAKE_SEED` | `{'key': LOGGING_SNAKE_KEY, 'spot': LOGGING_SPOT, 'name': 'Лесная змея', 'hp': 30, 'dmg_min': 4, 'dmg_max': 8, 'dodge': 25, 'loss_ap': 10, 'chance': LOGGING_SNAKE_CHANCE, 'pity_target': LOGGING_SNAK…` |  | :948 |
| `LOGGING_OWL_SEED` | `{'key': LOGGING_OWL_KEY, 'spot': LOGGING_SPOT, 'name': 'Неясыть', 'hp': 90, 'dmg_min': 7, 'dmg_max': 12, 'dodge': 30, 'loss_ap': 15, 'chance': LOGGING_OWL_CHANCE, 'pity_target': LOGGING_OWL_PITY_TA…` |  | :978 |
| `LOGGING_ITEM_SEEDS` | `[(LOGGING_AXE_NAME, 'Крепкий лесорубский топор: без него к срубам не подпустят. Повышает шанс успешной рубки деревьев.', 300, 150, 1, 'mining', 0), (LOGGING_WOOD_NAME, 'Свежие срубленные брёвна из …` |  | :1010 |
| `LOGGING_SHOP_ITEMS` | `(LOGGING_AXE_NAME,)` |  | :1044 |
| `LOGGING_ENEMY_DROPS` | `('Змеиная кожа', 'Змеиный яд', 'Совиное перо')` |  | :1047 |
| `LOGGING_MARKET_RESOURCES` | `(LOGGING_PLANK_NAME, LOGGING_FIREWOOD_NAME)` |  | :1050 |
| `REPORT_DAILY_LIMIT` | `3` |  | :1052 |
| `REPORT_AUTO_APPROVE_TROOPS` | `100` |  | :1053 |
| `NEWS_PUBLISH_BONUS` | `10` |  | :1057 |
| `NEWS_PUBLISH_CAP` | `28` |  | :1058 |
| `ROLE_SALARY_PAY_DAY` | `28` |  | :1061 |
| `REPORT_DAILY_PAY_CAP` | `4000` |  | :1066 |
| `REPORT_MAX_TROOPS` | `1000000` |  | :1067 |
| `REPORT_MAX_REGION` | `38` | 0 = Столица, 1..38 регионы | :1068 |
| `WALL_TEXT_MAX_LEN` | `40` | лимит символов на одно изречение | :1071 |
| `WALL_FREE_PER_DAY` | `2` | бесплатных сообщений в сутки | :1072 |
| `WALL_PAID_STEPS` | `[(3, 30), (3, 90), (3, 200)]` | далее платные ступени: (кол-во, цена НМ) | :1073 |
| `WALL_REVIEW_TOTAL` | `11` | максимум сообщений в сутки (2 + 3+3+3) | :1078 |
| `WALL_PAGE_SIZE` | `5` | постов на страницу стены | :1079 |
| `WALL_ARCHIVE_PAGE_SIZE` | `8` | записей архива стены на страницу списка | :1080 |
| `REPORT_ARCHIVE_PAGE` | `8` | отчётов на страницу архива МВД и в «Моих отчётах» | :1083 |
| `POLL_MAX_DAYS` | `10` | максимум дней, сколько живёт опрос. Не закрыл | :1086 |
| `POLL_VISIBLE` | `4` | сколько новейших опросов висит в меню голосования. | :1089 |
| `POLL_ARCHIVE_DAYS_PER_PAGE` | `5` | дней (дат) архива опросов на страницу списка | :1092 |
| `POLL_ARCHIVE_PER_DAY` | `6` | опросов под одним заголовком-днём | :1093 |
| `REP_SPEECH_MAX_LEN` | `100` | лимит символов одного обращения | :1096 |
| `REP_SPEECH_PER_DAY` | `2` | обращений в сутки от представителя | :1097 |
| `AUTO_PROMOTE_MAX_TROOPS` | `4040` |  | :1102 |

## Буклет туриста

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `TOURIST_BOOKLET_NAME` | `'Буклет туриста'` |  | :23 |

## Суточный цикл Нордхайма

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `REPORT_DAY_START_HOUR` | `10` |  | :297 |

## Дом Дуэлей (PvP-арена)

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `DUEL_ZONES` | `('head', 'body', 'hands', 'legs')` |  | :394 |

## Рынок: слоты продажи

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `MARKET_BASE_SLOTS` | `1` | слоты без лицензии | :469 |

## Налог на недвижимость (НМ/мес)

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `HOUSING_TAX` | `{'municipal': 0, 'studio': 20, 'apartment': 35, 'improved': 60, 'mansion': 100}` |  | :475 |

## Банк: лимит счёта туриста (НМ)

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `TOURIST_BALANCE_LIMIT` | `200` |  | :485 |

## Данж: лимит хила (количество применений за забег)

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `DUNGEON_HEAL_SOFT_LIMIT` | `6` | после этого — ×2/3 | :488 |

## Сброс протухших забегов подземелья

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `DUNGEON_RUN_STALE_SEC` | `3600` |  | :497 |

## Данж: побег и дымовая шашка

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `ESCAPE_BASE_CHANCE` | `25` |  | :505 |

