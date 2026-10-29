# Справочник констант `config.py`

> **Сгенерировано** `tools/export_config.py`. Перегенерация:
> `.venv\Scripts\python.exe tools/export_config.py`.
>
> Все модульные константы `config.py`, сгруппированные по секциям
> (комментариям-разделителям `# ── … ──`). Длинные значения усечены `…`;
> точное значение — в `config.py` по строке из первой колонки.

Всего констант: **276**; разделов: **10**.

## Без раздела

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `VERSION` | `'0.41.0'` |  | :16 |
| `VERSION_NOTES` | `'Бюрократия Нордхайма обновилась: учёт и сроки стали строже.'` |  | :17 |
| `PREV_VERSION` | `'0.40.0'` |  | :19 |
| `PREV_VERSION_NOTES` | `'Коридоры упырей потемнели: в лабиринте объявились стражи.'` |  | :20 |
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
| `FIRELAB_HUB_DODGE` | `FIRELAB_GHOST_DODGE` |  | :60 |
| `FIRELAB_HUB_HP` | `FIRELAB_GHOST_HP` |  | :61 |
| `FIRELAB_HUB_DMG` | `FIRELAB_GHOST_DMG` |  | :62 |
| `FIRELAB_PUMPKIN_HP` | `60` |  | :63 |
| `FIRELAB_PUMPKIN_DMG` | `(4, 7)` |  | :64 |
| `FIRELAB_PUMPKIN_DODGE` | `5` |  | :65 |
| `FIRELAB_PUMPKIN_ARMOR` | `2` | броня босса | :66 |
| `FIRELAB_SCARECROW_SEED` | `{'key': 'scarecrow', 'spot': 'firelab', 'name': 'Пугало', 'hp': FIRELAB_SCARECROW_HP, 'dmg_min': FIRELAB_SCARECROW_DMG[0], 'dmg_max': FIRELAB_SCARECROW_DMG[1], 'dodge': FIRELAB_SCARECROW_DODGE, 'ar…` |  | :68 |
| `FIRELAB_APPLE_CHILD_SEED` | `{'key': 'apple_child', 'spot': 'firelab', 'name': 'Дитя Яблони', 'hp': FIRELAB_APPLE_CHILD_HP, 'dmg_min': FIRELAB_APPLE_CHILD_DMG[0], 'dmg_max': FIRELAB_APPLE_CHILD_DMG[1], 'dodge': FIRELAB_APPLE_C…` |  | :89 |
| `FIRELAB_CROW_SEED` | `{'key': 'crow', 'spot': 'firelab', 'name': 'Ворон', 'hp': FIRELAB_CROW_HP, 'dmg_min': FIRELAB_CROW_DMG[0], 'dmg_max': FIRELAB_CROW_DMG[1], 'dodge': FIRELAB_CROW_DODGE, 'loss_ap': 0, 'chance': 0, 'p…` |  | :109 |
| `FIRELAB_HUB_SEED` | `{'key': 'hub', 'spot': 'firelab', 'name': 'Хуб', 'hp': FIRELAB_HUB_HP, 'dmg_min': FIRELAB_HUB_DMG[0], 'dmg_max': FIRELAB_HUB_DMG[1], 'dodge': FIRELAB_HUB_DODGE, 'loss_ap': 0, 'chance': 0, 'pity_tar…` |  | :129 |
| `FIRELAB_PUMPKIN_SEED` | `{'key': 'pumpkin_boss', 'spot': 'firelab', 'name': 'Мощный Мистер Огненная Тыква', 'hp': FIRELAB_PUMPKIN_HP, 'dmg_min': FIRELAB_PUMPKIN_DMG[0], 'dmg_max': FIRELAB_PUMPKIN_DMG[1], 'dodge': FIRELAB_P…` |  | :150 |
| `FIRELAB_ENEMY_SEEDS` | `(FIRELAB_SCARECROW_SEED, FIRELAB_APPLE_CHILD_SEED, FIRELAB_CROW_SEED, FIRELAB_HUB_SEED, FIRELAB_PUMPKIN_SEED)` |  | :171 |
| `FIRE_EVENT_ENABLED` | `True` |  | :179 |
| `FIRE_EVENT_START` | `(2026, 10, 30, 0, 0)` | МСК, ночь на пятницу 30.10 | :180 |
| `FIRE_EVENT_DURATION_DAYS` | `5` | до ~00:00 МСК 4.11 | :181 |
| `FIRE_LAB_ENABLED` | `False` |  | :183 |
| `FIRE_EVENT_LAB_FEE` | `42` | вход в лабиринт, НМ | :184 |
| `FIRE_EVENT_MAX_ENTRIES_DAY` | `4` | максимум заходов за сутки | :185 |
| `FIRE_LAB_SESSION_TTL_SEC` | `3600` | неактивность: сессия закрывается автоматически (1 ч) | :186 |
| `FIRE_LAB_SCARECROW_BLIND_P` | `0.15` | Пугало: «сено в лицо» — ослепление | :191 |
| `FIRE_LAB_APPLE_STUN_P` | `0.1` | Дитя Яблони: «яблочко» — оглушение | :192 |
| `FIRE_LAB_CROW_BLIND_P` | `0.15` | Ворон: ослепление (как сова) | :193 |
| `FIRE_LAB_HUB_SLOW_P` | `0.25` |  | :194 |
| `FIRE_LAB_HUB_SLOW_ROUNDS` | `3` |  | :195 |
| `FIRE_LAB_HUB_PLAYER_DODGE_PENALTY` | `35` |  | :196 |
| `FIRE_LAB_HUB_ENEMY_DODGE_BONUS` | `10` |  | :197 |
| `FIRE_LAB_BOSS_BURN_P` | `0.25` | Босс «Мистер Тыква»: поджиг игрока | :198 |
| `FIRE_LAB_BOSS_BURN_DMG` | `2` | −HP/ход | :199 |
| `FIRE_LAB_BOSS_BURN_ROUNDS` | `3` |  | :200 |
| `FIRE_LAB_BOSS_MAX` | `2` | максимум встреч с боссом за заход | :201 |
| `FIRE_LAB_ROOMS_MAX` | `25` | после 25 комнат-развилок выход автоматом | :202 |
| `FIRE_LAB_TIER_MAX` | `5` | кап усилений | :205 |
| `FIRE_LAB_TIER_HP_STEP` | `2` | +HP всем врагам за тир (1–4) | :206 |
| `FIRE_LAB_TIER_HP_LAST` | `8` | 5-й тир: разово +8 (итого +16) | :207 |
| `FIRE_LAB_TIER_LOOT_STEP` | `0.02` | лут ×(1+2%) за тир (1–4) | :208 |
| `FIRE_LAB_TIER_LOOT_LAST` | `0.1` | 5-й тир: ×(1+10%) | :209 |
| `FIRE_LAB_P_WELL` | `0.07` | Колодец (перебивается паттерном ЛЛПП) | :212 |
| `FIRE_LAB_WELL_MAX` | `3` | максимум посещений за заход | :213 |
| `FIRE_LAB_P_TREE` | `0.09` | Древо Огня (перебивается ЛЛППНН) | :214 |
| `FIRE_LAB_TREE_MAX` | `1` | раз за заход | :215 |
| `FIRE_LAB_P_CHEST` | `0.1` | Сундук сокровищ | :216 |
| `FIRE_LAB_CHEST_MAX` | `2` | максимум за заход | :217 |
| `FIRE_TREE_DMG_BONUS_PCT` | `15` | +15% урона | :220 |
| `FIRE_TREE_REGEN_HP` | `1` | +1 HP после каждого удара игрока | :221 |
| `FIRE_LAB_PATTERN_WELL` | `('L', 'L', 'S', 'S')` | ЛЛПП → Колодец (до 3) | :225 |
| `FIRE_LAB_PATTERN_TREE` | `('L', 'L', 'S', 'S', 'R', 'R')` | ЛЛППНН → Древо Огня (1) | :226 |
| `CLAN_BUILDING_TYPES` | `{'house': {'name': 'Дом Клана', 'slots': 2, 'max_level': 2, 'days': 2, 'price_nm': 3000, 'required': {'Доска': 60, 'Бревна': 20, 'Железная руда': 15}}, 'manor': {'name': 'Клановое поместье', 'slots…` |  | :228 |
| `CLAN_BUILDING_NO_RESOURCES_MULT` | `2` |  | :243 |
| `CLAN_EXPANSION_TYPES` | `('kitchen', 'workbench', 'shower', 'garden', 'library', 'shop')` |  | :245 |
| `CLAN_EXPANSION_INFO` | `{'kitchen': {'name': 'Кухня', 'icon': '🍳', 'desc': 'Готовка по выученным рецептам; уровень задаёт доступные блюда.'}, 'workbench': {'name': 'Крафтовый стол', 'icon': '🛠', 'desc': 'Крафт снаряжения …` |  | :247 |
| `CLAN_EXPANSION_UPGRADE` | `{2: {'nm': 1500, 'required': {'Доска': 20, 'Железная руда': 10}}, 3: {'nm': 4000, 'required': {'Доска': 50, 'Железная руда': 30}}, 4: {'nm': 9000, 'required': {'Доска': 100, 'Железная руда': 60}}}` |  | :262 |
| `CLAN_SHOWER_AP_BY_LEVEL` | `{1: 25, 2: 50, 3: 75, 4: 100}` |  | :270 |
| `CLAN_SHOWER_SOBER_MINUTES` | `{1: 60, 2: 120, 3: 180, 4: 240}` |  | :271 |
| `CLAN_GARDEN_PLOTS` | `{1: 2, 2: 3, 3: 4, 4: 6}` |  | :273 |
| `CLAN_SHOP_DAILY_LIMIT` | `3` |  | :274 |
| `CLAN_SHOP_DISCOUNT` | `10` |  | :275 |
| `BOT_TOKEN` | `os.getenv('BOT_TOKEN')` |  | :277 |
| `ADMIN_IDS` | `[int(x) for x in os.getenv('ADMIN_IDS', '').split(',') if x.strip()]` |  | :278 |
| `_news_raw` | `os.getenv('NEWS_CHAT_ID', '').strip()` |  | :281 |
| `NEWS_CHAT_ID` | `int(_news_raw) if _news_raw.lstrip('-').isdigit() else None` |  | :282 |
| `DB_PATH` | `os.getenv('DATABASE_PATH', 'database/nordmark.db')` |  | :285 |
| `FSM_STORAGE_PATH` | `os.getenv('FSM_STORAGE_PATH', '').strip() or os.path.join(os.path.dirname(os.path.abspath(DB_PATH)), 'fsm')` |  | :294 |
| `REPORT_DAY_START_MINUTE` | `0` |  | :304 |
| `RANKS` | `[('Рекрут', 0), ('Рядовой', 100), ('Ефрейтор', 350), ('Капрал', 500), ('Сержант', 850), ('Старший Сержант', 1500), ('Лейтенант', 2500), ('Старший Лейтенант', 4040), ('Капитан', 6000), ('Майор', 850…` |  | :306 |
| `MAX_SELF_RANK_TROOPS` | `4040` |  | :327 |
| `AUTO_RANK_NAMES` | `('Рекрут', 'Рядовой', 'Ефрейтор', 'Капрал', 'Сержант', 'Старший Сержант', 'Лейтенант', 'Старший Лейтенант')` |  | :330 |
| `AWARD_MAX_SHOP_DISCOUNT` | `40` |  | :337 |
| `AWARD_MIN_REPORT_TAX` | `5` |  | :338 |
| `RANK_STATUS_TAGS` | `{'Ефрейтор': 'pilot2', 'Старший Сержант': 'pilot1', 'Старший Лейтенант': 'veteran', 'Майор': 'master_pilot', 'Полковник': 'ace'}` |  | :340 |
| `LEGIONER_ACCESS_CAP_ORDER` | `5` |  | :353 |
| `RANK_DAMAGE_TIERS` | `{'ace': (4, 8), 'master_pilot': (3, 5), 'veteran': (2, 4), 'pilot1': (1, 3), 'pilot2': (1, 2), 'recruit': (1, 1), 'tourist': (0, 1)}` |  | :359 |
| `RANK_CRIT_CHANCE` | `{'ace': 7.5, 'master_pilot': 6.0, 'veteran': 4.5, 'pilot1': 3.0, 'pilot2': 1.5, 'recruit': 0.0, 'tourist': 0.0}` |  | :377 |
| `PILOT_CRIT_MULT` | `1.4` |  | :391 |
| `PILOT_NO_WEAPON_DMG` | `(1, 1)` |  | :394 |
| `DUEL_ZONE_LABELS` | `{'head': 'Голова', 'body': 'Тело', 'hands': 'Руки', 'legs': 'Ноги'}` |  | :401 |
| `DUEL_ZONE_EMOJI` | `{'head': '🧠', 'body': '🫀', 'hands': '✊', 'legs': '🦵'}` |  | :407 |
| `DUEL_AP_COST` | `15` | списывается с обоих при старте боя | :413 |
| `DUEL_RATING_WIN` | `2` | рейтинг за победу | :414 |
| `DUEL_RATING_LOSS` | `-3` | рейтинг за поражение | :415 |
| `DUEL_RATING_DRAW` | `0` | рейтинг за ничью | :416 |
| `DUEL_RATING_FORFEIT` | `-1` | рейтинг тому, кто покинул бой («Покинуть дуэль») | :417 |
| `DUEL_RATING_FORFEIT_WIN` | `1` | рейтинг сопернику, если противник покинул бой (меньше чистой победы) | :418 |
| `DUEL_MIN_DAMAGE` | `1` | минимум урона за попавший (не уклонённый) удар | :419 |
| `DUEL_GUARD_REDUCTION` | `0.5` | доля урона, остающаяся при угаданной зоне защиты | :420 |
| `DUEL_HEAL_BETWEEN` | `0` | восстановление HP между раундами (пока нет) | :421 |
| `DUEL_CHALLENGE_TIMEOUT_SEC` | `120` | сколько живёт неотвеченный вызов | :422 |
| `DUEL_STALE_SEC` | `1800` | зависшая дуэль авто-завершается как void | :423 |
| `DUEL_GLOVES_NAME` | `'Дуэльные перчатки'` |  | :424 |
| `DUEL_GLOVES_DAMAGE` | `7` |  | :425 |
| `DUEL_GLOVES_PRICE` | `200` |  | :426 |
| `DUEL_GLOVES_SELL` | `100` |  | :427 |
| `DUEL_CLUB_CARD_NAME` | `'Клубная карта «Дом Дуэлей»'` |  | :428 |
| `DUEL_CLUB_CARD_PRICE` | `150` |  | :429 |
| `DUEL_CLUB_CARD_SELL` | `75` |  | :430 |
| `DUEL_CLUB_CARD_DAYS` | `30` |  | :431 |
| `DUEL_ACCESS_TAG` | `'pilot2'` |  | :434 |
| `RARITY_LEVELS` | `{1: 'Обычный', 2: 'Качественный', 3: 'Редкий', 4: 'Шедевр', 5: 'Легендарный'}` |  | :436 |
| `RARITY_EMOJI` | `{1: '⬜', 2: '🟩', 3: '🟦', 4: '🟪', 5: '🟧'}` |  | :444 |
| `ITEM_CATEGORIES` | `{'weapon': 'Оружие', 'consumable': 'Расходники', 'building': 'Недвижимость', 'housing': 'Жильё', 'furniture': 'Мебель и расширения', 'seeds': 'Семена', 'equipment': 'Одежда', 'resource': 'Ресурсы',…` |  | :452 |
| `MARKET_LICENSE_SLOTS` | `2` | доп. слоты при активной лицензии | :476 |
| `MARKET_LICENSE_DAYS` | `30` | срок действия лицензии (дней) | :477 |
| `MARKET_LICENSE_PRICE` | `500` | цена лицензии в НМ | :478 |
| `DUNGEON_HEAL_HARD_LIMIT` | `10` | после этого — ×1/2 | :495 |
| `DUNGEON_HEAL_SOFT_MULT` | `2 / 3` |  | :496 |
| `DUNGEON_HEAL_HARD_MULT` | `1 / 2` |  | :497 |
| `ESCAPE_HP_BONUS` | `20` |  | :512 |
| `DUNGEON_SMOKE_ESCAPE` | `95` |  | :513 |
| `DUNGEON_SMOKE_MAX` | `2` |  | :514 |
| `DUNGEON_ESCAPE_DRUNK_MULT` | `0.5` |  | :517 |
| `AP_MAX` | `150` |  | :519 |
| `AP_DAILY_RECOVERY` | `100` |  | :520 |
| `AP_BONUS_FROM_CONSUMABLE` | `50` |  | :521 |
| `AP_DAILY_RESTORE_LIMIT` | `150` |  | :526 |
| `AP_EXHAUSTED_MINUTES` | `2880` | 2 суток | :527 |
| `AP_EXHAUSTED_DAILY_RECOVERY` | `75` | суточное восстановление в «истощении» | :528 |
| `AP_EXHAUSTED_MAX_AP` | `90` | максимум ОД в «истощении» | :529 |
| `SEAWEED_DAILY_LIMIT` | `6` |  | :532 |
| `DIGESTIVE_UPSET_MINUTES` | `1440` | 24 часа | :533 |
| `ALCOHOL_WEAK_DRUNK_LIMIT` | `3` |  | :538 |
| `ALCOHOL_WEAK_VERY_DRUNK_LIMIT` | `6` |  | :539 |
| `ALCOHOL_STRONG_DRUNK_LIMIT` | `1` |  | :541 |
| `ALCOHOL_STRONG_VERY_DRUNK_LIMIT` | `2` |  | :542 |
| `DRUNK_MINUTES` | `60` |  | :543 |
| `VERY_DRUNK_MINUTES` | `360` | 6 часов | :544 |
| `DRINK_EFFECT_LABELS` | `{'alcohol_weak': '🍺 Слабоалкогольный: 3 шт/сутки — «пьян», 6 — «очень пьян»', 'alcohol_strong': '🥃 Крепкий алкоголь: 1 шт — «пьян», 2 — «очень пьян»', 'indigestion': '🤢 Вызывает «несварение» на сут…` |  | :547 |
| `SPECIAL_DEPT_CODE_MIN_LEN` | `4` |  | :558 |
| `SPECIAL_DEPT_CODE_MAX_LEN` | `8` |  | :559 |
| `SPECIAL_DEPT_ATTEMPTS_LIMIT` | `3` | ошибок кода подряд | :560 |
| `SPECIAL_DEPT_BLOCK_MINUTES` | `1440` | бан на 24 часа после 3 ошибок | :561 |
| `FISH_AP_COST` | `3` | стоимость одного заброса удочки | :564 |
| `RESERVOIR_AP_COST` | `5` |  | :569 |
| `FISH_WEIGHTS` | `[{'key': 'small', 'label': 'Мелкая', 'mult': 1.0, 'chance': 40}, {'key': 'medium', 'label': 'Средняя', 'mult': 1.15, 'chance': 40}, {'key': 'large', 'label': 'Большая', 'mult': 1.25, 'chance': 20}]` |  | :574 |
| `FISH_TREASURY_SALE_MULT` | `0.5` |  | :582 |
| `FISH_TREASURY_DAILY_LIMIT` | `300` |  | :587 |
| `FOREST_AP_COST` | `4` | запасной цена поиска, если у зоны нет ap_cost в БД | :590 |
| `FOREST_RESULT_DELAY` | `(5, 10)` | результат поиска через 5–10 секунд | :593 |
| `FOREST_SOLD_DAILY_LIMIT` | `250` |  | :598 |
| `FOREST_ALLOW_TOURISTS` | `False` |  | :603 |
| `FOREST_BOAR_PITY_TARGET` | `12` |  | :606 |
| `FOREST_BOAR_CHANCE` | `4.0` |  | :610 |
| `CALLSIGN_PRICE` | `500` |  | :612 |
| `PILOT_BASE_HP` | `100` |  | :614 |
| `FOREST_BOAR_HP` | `40` |  | :619 |
| `FOREST_BOAR_DMG` | `(4, 7)` |  | :620 |
| `FOREST_BOAR_DODGE` | `15` |  | :621 |
| `FOREST_BOAR_LOSS_AP` | `10` |  | :623 |
| `FOREST_BOAR_LOOT` | `[('Мясо кабана', 50), ('Шкура кабана', 20), ('Клык кабана', 10), ('', 20)]` |  | :625 |
| `FOREST_WHITE_WOLF_HP` | `120` |  | :637 |
| `FOREST_WHITE_WOLF_DMG` | `(7, 12)` |  | :638 |
| `FOREST_WHITE_WOLF_DODGE` | `20` |  | :639 |
| `FOREST_WHITE_WOLF_LOSS_AP` | `15` |  | :641 |
| `FOREST_WHITE_WOLF_CHANCE` | `2.0` |  | :642 |
| `FOREST_WHITE_WOLF_PITY_TARGET` | `36` |  | :645 |
| `FOREST_WHITE_WOLF_BLEED_CHANCE` | `30` |  | :647 |
| `FOREST_WHITE_WOLF_BLEED_DMG` | `3` |  | :648 |
| `FOREST_WHITE_WOLF_AUTOWIN_HP` | `20` |  | :650 |
| `FOREST_WHITE_WOLF_SMALL_BLESSING` | `'внимание севера'` |  | :652 |
| `FOREST_WHITE_WOLF_BIG_BLESSING` | `'благословение севера'` |  | :653 |
| `FOREST_BOAR_SEED` | `{'key': 'boar', 'spot': 'forest', 'name': 'Дикий кабан', 'hp': FOREST_BOAR_HP, 'dmg_min': FOREST_BOAR_DMG[0], 'dmg_max': FOREST_BOAR_DMG[1], 'dodge': FOREST_BOAR_DODGE, 'loss_ap': FOREST_BOAR_LOSS_…` |  | :660 |
| `FOREST_WHITE_WOLF_SEED` | `{'key': 'white_wolf', 'spot': 'forest', 'name': 'Белый Волк Севера', 'hp': FOREST_WHITE_WOLF_HP, 'dmg_min': FOREST_WHITE_WOLF_DMG[0], 'dmg_max': FOREST_WHITE_WOLF_DMG[1], 'dodge': FOREST_WHITE_WOLF…` |  | :685 |
| `MOLLUSK_SEED` | `{'key': 'mollusk', 'spot': 'reservoir', 'name': 'Мутировавший моллюск', 'hp': 24, 'dmg_min': 5, 'dmg_max': 9, 'dodge': 20, 'loss_ap': 12, 'chance': 4, 'pity_target': 0, 'reward_nm': 0, 'photo_key':…` |  | :713 |
| `MOLLUSK_ITEM_SEEDS` | `[('Мясо моллюска', 'Плотное мясо мутировавшего моллюска. В сыром виде есть нельзя — прожарь на кухне.', 120, 60, 3, 'resource', 0), ('Жемчужина', 'Редчайшая жемчужина из раковины мутировавшего молл…` |  | :736 |
| `MOLLUSK_ENEMY_DROPS` | `('Мясо моллюска', 'Жемчужина')` |  | :751 |
| `MINE_AP_COST` | `12` | стоимость одной попытки добычи | :760 |
| `MINE_BASE_CHANCE` | `30` | базовый шанс успеха без бонуса кирки | :761 |
| `MINE_PICKAXE_BONUS_PER_RANK` | `15` | надбавка к шансу за ступень кирки (ранг 1 → +15%) | :762 |
| `MINE_CHANCE_CAP` | `90` | потолок шанса успеха | :763 |
| `MINE_RESULT_DELAY` | `(7, 15)` | результат добычи через 7–15 секунд | :764 |
| `MINE_REQUIRED_STATUS` | `'pilot1'` | вход в копь — с «Пилота 1 класса» | :765 |
| `MINE_GEM_CAP` | `1` | из самоцветов за бой выпадает не больше одного | :766 |
| `MINE_PICKAXE_NAME` | `'Кирка'` |  | :767 |
| `MINE_ORE_NAME` | `'Железная руда'` |  | :768 |
| `MINE_BAT_KEY` | `'bat'` |  | :771 |
| `MINE_BAT_SPOT` | `'iron'` |  | :772 |
| `MINE_BAT_CHANCE` | `7.0` |  | :773 |
| `MINE_BAT_PITY_TARGET` | `12` |  | :774 |
| `MINE_BAT_SEED` | `{'key': MINE_BAT_KEY, 'spot': MINE_BAT_SPOT, 'name': 'Летучая мышь', 'hp': 22, 'dmg_min': 3, 'dmg_max': 7, 'dodge': 35, 'loss_ap': 15, 'chance': MINE_BAT_CHANCE, 'pity_target': MINE_BAT_PITY_TARGET…` |  | :779 |
| `MINE_ITEM_SEEDS` | `[(MINE_PICKAXE_NAME, 'Простая кирка шахтёра: без неё в штольню не сунешься, а с ней порода поддаётся легче. Повышает шанс успешной добычи руды.', 300, 150, 1, 'mining', 0), (MINE_ORE_NAME, 'Кусок ж…` |  | :805 |
| `MINE_SHOP_ITEMS` | `(MINE_PICKAXE_NAME,)` |  | :826 |
| `MINE_ENEMY_DROPS` | `('Изумруд', 'Рубин', 'Сапфир')` |  | :829 |
| `ON_HIT_EFFECTS` | `{'bleed': {'emoji': '🩸', 'title': 'Кровотечение', 'until_battle_end': True, 'params': (('chance', 'Шанс наложить, %', 'percent'), ('dmg', 'Урон, HP за ход', 'int')), 'hint': 'Раны сочатся кровью ка…` |  | :838 |
| `ON_HIT_KIND_ORDER` | `('bleed', 'poison', 'frostbite', 'state', 'lifesteal')` |  | :892 |
| `ON_HIT_STATE_ROUNDS` | `{'оглушён': 3, 'ослеплён': 4}` |  | :894 |
| `CLAN_ROLES` | `{'leader': '👑 Глава клана', 'seneschal': '🛡 Сенешаль клана', 'banner': '🚩 Знаменосец клана', 'elder': '⭐ Старшина', 'member': '▪️ Член клана'}` |  | :900 |
| `CLAN_ROLE_ORDER` | `('leader', 'seneschal', 'banner', 'elder', 'member')` |  | :907 |
| `LOGGING_AP_COST` | `12` | стоимость одной попытки рубки | :913 |
| `LOGGING_BASE_CHANCE` | `35` | базовый шанс успеха без бонуса топора | :914 |
| `LOGGING_AXE_BONUS_PER_RANK` | `15` | надбавка к шансу за ступень топора | :915 |
| `LOGGING_CHANCE_CAP` | `90` | потолок шанса успеха | :916 |
| `LOGGING_AXE_SLIP_CHANCE` | `2.5` | шанс, что топор отскочит пилоту в плечо, % | :917 |
| `LOGGING_RESULT_DELAY` | `(7, 15)` | результат рубки через 7–15 секунд | :918 |
| `LOGGING_AXE_NAME` | `'Топор'` |  | :919 |
| `LOGGING_WOOD_NAME` | `'Бревна'` |  | :920 |
| `LOGGING_PLANK_NAME` | `'Доска'` |  | :926 |
| `LOGGING_FIREWOOD_NAME` | `'Пак дров'` |  | :927 |
| `LOGGING_PLANK_YIELD` | `3` | досок из одного бревна | :928 |
| `LOGGING_PLANK_FEE` | `15` | НМ за распил одного бревна (в казну) | :929 |
| `LOGGING_FIREWOOD_YIELD` | `3` | паков дров из одного бревна | :930 |
| `LOGGING_FIREWOOD_AP_COST` | `4` | ОД за рубку дров из одного бревна | :931 |
| `LOGGING_SNAKE_KEY` | `'snake'` |  | :935 |
| `LOGGING_OWL_KEY` | `'owl'` |  | :936 |
| `LOGGING_SPOT` | `'logging'` |  | :937 |
| `LOGGING_SNAKE_CHANCE` | `8.0` |  | :938 |
| `LOGGING_SNAKE_PITY_TARGET` | `10` |  | :939 |
| `LOGGING_OWL_CHANCE` | `3.0` |  | :940 |
| `LOGGING_OWL_PITY_TARGET` | `24` |  | :941 |
| `LOGGING_SNAKE_POISON_CHANCE` | `30` |  | :943 |
| `LOGGING_SNAKE_POISON_DMG` | `2` |  | :944 |
| `LOGGING_OWL_FLEE_HP` | `20` |  | :948 |
| `LOGGING_OWL_BLIND_CHANCE` | `30` |  | :949 |
| `LOGGING_OWL_BLIND_ROUNDS` | `4` |  | :950 |
| `LOGGING_SNAKE_SEED` | `{'key': LOGGING_SNAKE_KEY, 'spot': LOGGING_SPOT, 'name': 'Лесная змея', 'hp': 30, 'dmg_min': 4, 'dmg_max': 8, 'dodge': 25, 'loss_ap': 10, 'chance': LOGGING_SNAKE_CHANCE, 'pity_target': LOGGING_SNAK…` |  | :954 |
| `LOGGING_OWL_SEED` | `{'key': LOGGING_OWL_KEY, 'spot': LOGGING_SPOT, 'name': 'Неясыть', 'hp': 90, 'dmg_min': 7, 'dmg_max': 12, 'dodge': 30, 'loss_ap': 15, 'chance': LOGGING_OWL_CHANCE, 'pity_target': LOGGING_OWL_PITY_TA…` |  | :984 |
| `LOGGING_ITEM_SEEDS` | `[(LOGGING_AXE_NAME, 'Крепкий лесорубский топор: без него к срубам не подпустят. Повышает шанс успешной рубки деревьев.', 300, 150, 1, 'mining', 0), (LOGGING_WOOD_NAME, 'Свежие срубленные брёвна из …` |  | :1016 |
| `LOGGING_SHOP_ITEMS` | `(LOGGING_AXE_NAME,)` |  | :1050 |
| `LOGGING_ENEMY_DROPS` | `('Змеиная кожа', 'Змеиный яд', 'Совиное перо')` |  | :1053 |
| `LOGGING_MARKET_RESOURCES` | `(LOGGING_PLANK_NAME, LOGGING_FIREWOOD_NAME)` |  | :1056 |
| `REPORT_DAILY_LIMIT` | `3` |  | :1058 |
| `REPORT_AUTO_APPROVE_TROOPS` | `100` |  | :1059 |
| `NEWS_PUBLISH_BONUS` | `10` |  | :1063 |
| `NEWS_PUBLISH_CAP` | `28` |  | :1064 |
| `ROLE_SALARY_PAY_DAY` | `28` |  | :1067 |
| `REPORT_DAILY_PAY_CAP` | `4000` |  | :1072 |
| `REPORT_MAX_TROOPS` | `1000000` |  | :1073 |
| `REPORT_MAX_REGION` | `38` | 0 = Столица, 1..38 регионы | :1074 |
| `WALL_TEXT_MAX_LEN` | `40` | лимит символов на одно изречение | :1077 |
| `WALL_FREE_PER_DAY` | `2` | бесплатных сообщений в сутки | :1078 |
| `WALL_PAID_STEPS` | `[(3, 30), (3, 90), (3, 200)]` | далее платные ступени: (кол-во, цена НМ) | :1079 |
| `WALL_REVIEW_TOTAL` | `11` | максимум сообщений в сутки (2 + 3+3+3) | :1084 |
| `WALL_PAGE_SIZE` | `5` | постов на страницу стены | :1085 |
| `WALL_ARCHIVE_PAGE_SIZE` | `8` | записей архива стены на страницу списка | :1086 |
| `REPORT_ARCHIVE_PAGE` | `8` | отчётов на страницу архива МВД и в «Моих отчётах» | :1089 |
| `POLL_MAX_DAYS` | `10` | максимум дней, сколько живёт опрос. Не закрыл | :1092 |
| `POLL_VISIBLE` | `4` | сколько новейших опросов висит в меню голосования. | :1095 |
| `POLL_ARCHIVE_DAYS_PER_PAGE` | `5` | дней (дат) архива опросов на страницу списка | :1098 |
| `POLL_ARCHIVE_PER_DAY` | `6` | опросов под одним заголовком-днём | :1099 |
| `REP_SPEECH_MAX_LEN` | `100` | лимит символов одного обращения | :1102 |
| `REP_SPEECH_PER_DAY` | `2` | обращений в сутки от представителя | :1103 |
| `AUTO_PROMOTE_MAX_TROOPS` | `4040` |  | :1108 |

## Буклет туриста

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `TOURIST_BOOKLET_NAME` | `'Буклет туриста'` |  | :23 |

## Суточный цикл Нордхайма

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `REPORT_DAY_START_HOUR` | `10` |  | :303 |

## Дом Дуэлей (PvP-арена)

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `DUEL_ZONES` | `('head', 'body', 'hands', 'legs')` |  | :400 |

## Рынок: слоты продажи

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `MARKET_BASE_SLOTS` | `1` | слоты без лицензии | :475 |

## Налог на недвижимость (НМ/мес)

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `HOUSING_TAX` | `{'municipal': 0, 'studio': 20, 'apartment': 35, 'improved': 60, 'mansion': 100}` |  | :481 |

## Банк: лимит счёта туриста (НМ)

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `TOURIST_BALANCE_LIMIT` | `200` |  | :491 |

## Данж: лимит хила (количество применений за забег)

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `DUNGEON_HEAL_SOFT_LIMIT` | `6` | после этого — ×2/3 | :494 |

## Сброс протухших забегов подземелья

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `DUNGEON_RUN_STALE_SEC` | `3600` |  | :503 |

## Данж: побег и дымовая шашка

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `ESCAPE_BASE_CHANCE` | `25` |  | :511 |

