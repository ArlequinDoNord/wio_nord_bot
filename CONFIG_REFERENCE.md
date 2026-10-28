# Справочник констант `config.py`

> **Сгенерировано** `tools/export_config.py`. Перегенерация:
> `.venv\Scripts\python.exe tools/export_config.py`.
>
> Все модульные константы `config.py`, сгруппированные по секциям
> (комментариям-разделителям `# ── … ──`). Длинные значения усечены `…`;
> точное значение — в `config.py` по строке из первой колонки.

Всего констант: **222**; разделов: **10**.

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
| `FIRE_EVENT_ENABLED` | `True` |  | :51 |
| `FIRE_EVENT_START` | `(2026, 10, 30, 0, 0)` | МСК, ночь на пятницу 30.10 | :52 |
| `FIRE_EVENT_DURATION_DAYS` | `5` | до ~00:00 МСК 4.11 | :53 |
| `FIRE_LAB_ENABLED` | `False` |  | :55 |
| `FIRE_EVENT_LAB_FEE` | `42` | вход в лабиринт, НМ | :56 |
| `FIRE_EVENT_MAX_ENTRIES_DAY` | `4` | максимум заходов за сутки | :57 |
| `CLAN_BUILDING_TYPES` | `{'house': {'name': 'Дом Клана', 'slots': 2, 'max_level': 2, 'days': 2, 'price_nm': 3000, 'required': {'Доска': 60, 'Бревна': 20, 'Железная руда': 15}}, 'manor': {'name': 'Клановое поместье', 'slots…` |  | :59 |
| `CLAN_BUILDING_NO_RESOURCES_MULT` | `2` |  | :74 |
| `CLAN_EXPANSION_TYPES` | `('kitchen', 'workbench', 'shower', 'garden', 'library', 'shop')` |  | :76 |
| `CLAN_EXPANSION_INFO` | `{'kitchen': {'name': 'Кухня', 'icon': '🍳', 'desc': 'Готовка по выученным рецептам; уровень задаёт доступные блюда.'}, 'workbench': {'name': 'Крафтовый стол', 'icon': '🛠', 'desc': 'Крафт снаряжения …` |  | :78 |
| `CLAN_EXPANSION_UPGRADE` | `{2: {'nm': 1500, 'required': {'Доска': 20, 'Железная руда': 10}}, 3: {'nm': 4000, 'required': {'Доска': 50, 'Железная руда': 30}}, 4: {'nm': 9000, 'required': {'Доска': 100, 'Железная руда': 60}}}` |  | :93 |
| `CLAN_SHOWER_AP_BY_LEVEL` | `{1: 25, 2: 50, 3: 75, 4: 100}` |  | :101 |
| `CLAN_SHOWER_SOBER_MINUTES` | `{1: 60, 2: 120, 3: 180, 4: 240}` |  | :102 |
| `CLAN_GARDEN_PLOTS` | `{1: 2, 2: 3, 3: 4, 4: 6}` |  | :104 |
| `CLAN_SHOP_DAILY_LIMIT` | `3` |  | :105 |
| `CLAN_SHOP_DISCOUNT` | `10` |  | :106 |
| `BOT_TOKEN` | `os.getenv('BOT_TOKEN')` |  | :108 |
| `ADMIN_IDS` | `[int(x) for x in os.getenv('ADMIN_IDS', '').split(',') if x.strip()]` |  | :109 |
| `_news_raw` | `os.getenv('NEWS_CHAT_ID', '').strip()` |  | :112 |
| `NEWS_CHAT_ID` | `int(_news_raw) if _news_raw.lstrip('-').isdigit() else None` |  | :113 |
| `DB_PATH` | `os.getenv('DATABASE_PATH', 'database/nordmark.db')` |  | :116 |
| `FSM_STORAGE_PATH` | `os.getenv('FSM_STORAGE_PATH', '').strip() or os.path.join(os.path.dirname(os.path.abspath(DB_PATH)), 'fsm')` |  | :125 |
| `REPORT_DAY_START_MINUTE` | `0` |  | :135 |
| `RANKS` | `[('Рекрут', 0), ('Рядовой', 100), ('Ефрейтор', 350), ('Капрал', 500), ('Сержант', 850), ('Старший Сержант', 1500), ('Лейтенант', 2500), ('Старший Лейтенант', 4040), ('Капитан', 6000), ('Майор', 850…` |  | :137 |
| `MAX_SELF_RANK_TROOPS` | `4040` |  | :158 |
| `AUTO_RANK_NAMES` | `('Рекрут', 'Рядовой', 'Ефрейтор', 'Капрал', 'Сержант', 'Старший Сержант', 'Лейтенант', 'Старший Лейтенант')` |  | :161 |
| `AWARD_MAX_SHOP_DISCOUNT` | `40` |  | :168 |
| `AWARD_MIN_REPORT_TAX` | `5` |  | :169 |
| `RANK_STATUS_TAGS` | `{'Ефрейтор': 'pilot2', 'Старший Сержант': 'pilot1', 'Старший Лейтенант': 'veteran', 'Майор': 'master_pilot', 'Полковник': 'ace'}` |  | :171 |
| `LEGIONER_ACCESS_CAP_ORDER` | `5` |  | :184 |
| `RANK_DAMAGE_TIERS` | `{'ace': (4, 8), 'master_pilot': (3, 5), 'veteran': (2, 4), 'pilot1': (1, 3), 'pilot2': (1, 2), 'recruit': (1, 1), 'tourist': (0, 1)}` |  | :190 |
| `RANK_CRIT_CHANCE` | `{'ace': 7.5, 'master_pilot': 6.0, 'veteran': 4.5, 'pilot1': 3.0, 'pilot2': 1.5, 'recruit': 0.0, 'tourist': 0.0}` |  | :208 |
| `PILOT_CRIT_MULT` | `1.4` |  | :222 |
| `PILOT_NO_WEAPON_DMG` | `(1, 1)` |  | :225 |
| `DUEL_ZONE_LABELS` | `{'head': 'Голова', 'body': 'Тело', 'hands': 'Руки', 'legs': 'Ноги'}` |  | :232 |
| `DUEL_ZONE_EMOJI` | `{'head': '🧠', 'body': '🫀', 'hands': '✊', 'legs': '🦵'}` |  | :238 |
| `DUEL_AP_COST` | `15` | списывается с обоих при старте боя | :244 |
| `DUEL_RATING_WIN` | `2` | рейтинг за победу | :245 |
| `DUEL_RATING_LOSS` | `-3` | рейтинг за поражение | :246 |
| `DUEL_RATING_DRAW` | `0` | рейтинг за ничью | :247 |
| `DUEL_RATING_FORFEIT` | `-1` | рейтинг тому, кто покинул бой («Покинуть дуэль») | :248 |
| `DUEL_RATING_FORFEIT_WIN` | `1` | рейтинг сопернику, если противник покинул бой (меньше чистой победы) | :249 |
| `DUEL_MIN_DAMAGE` | `1` | минимум урона за попавший (не уклонённый) удар | :250 |
| `DUEL_GUARD_REDUCTION` | `0.5` | доля урона, остающаяся при угаданной зоне защиты | :251 |
| `DUEL_HEAL_BETWEEN` | `0` | восстановление HP между раундами (пока нет) | :252 |
| `DUEL_CHALLENGE_TIMEOUT_SEC` | `120` | сколько живёт неотвеченный вызов | :253 |
| `DUEL_STALE_SEC` | `1800` | зависшая дуэль авто-завершается как void | :254 |
| `DUEL_GLOVES_NAME` | `'Дуэльные перчатки'` |  | :255 |
| `DUEL_GLOVES_DAMAGE` | `7` |  | :256 |
| `DUEL_GLOVES_PRICE` | `200` |  | :257 |
| `DUEL_GLOVES_SELL` | `100` |  | :258 |
| `DUEL_CLUB_CARD_NAME` | `'Клубная карта «Дом Дуэлей»'` |  | :259 |
| `DUEL_CLUB_CARD_PRICE` | `150` |  | :260 |
| `DUEL_CLUB_CARD_SELL` | `75` |  | :261 |
| `DUEL_CLUB_CARD_DAYS` | `30` |  | :262 |
| `DUEL_ACCESS_TAG` | `'pilot2'` |  | :265 |
| `RARITY_LEVELS` | `{1: 'Обычный', 2: 'Качественный', 3: 'Редкий', 4: 'Шедевр', 5: 'Легендарный'}` |  | :267 |
| `RARITY_EMOJI` | `{1: '⬜', 2: '🟩', 3: '🟦', 4: '🟪', 5: '🟧'}` |  | :275 |
| `ITEM_CATEGORIES` | `{'weapon': 'Оружие', 'consumable': 'Расходники', 'building': 'Недвижимость', 'housing': 'Жильё', 'furniture': 'Мебель и расширения', 'seeds': 'Семена', 'equipment': 'Одежда', 'resource': 'Ресурсы',…` |  | :283 |
| `MARKET_LICENSE_SLOTS` | `2` | доп. слоты при активной лицензии | :307 |
| `MARKET_LICENSE_DAYS` | `30` | срок действия лицензии (дней) | :308 |
| `MARKET_LICENSE_PRICE` | `500` | цена лицензии в НМ | :309 |
| `DUNGEON_HEAL_HARD_LIMIT` | `10` | после этого — ×1/2 | :326 |
| `DUNGEON_HEAL_SOFT_MULT` | `2 / 3` |  | :327 |
| `DUNGEON_HEAL_HARD_MULT` | `1 / 2` |  | :328 |
| `ESCAPE_HP_BONUS` | `20` |  | :343 |
| `DUNGEON_SMOKE_ESCAPE` | `95` |  | :344 |
| `DUNGEON_SMOKE_MAX` | `2` |  | :345 |
| `DUNGEON_ESCAPE_DRUNK_MULT` | `0.5` |  | :348 |
| `AP_MAX` | `150` |  | :350 |
| `AP_DAILY_RECOVERY` | `100` |  | :351 |
| `AP_BONUS_FROM_CONSUMABLE` | `50` |  | :352 |
| `AP_DAILY_RESTORE_LIMIT` | `150` |  | :357 |
| `AP_EXHAUSTED_MINUTES` | `2880` | 2 суток | :358 |
| `AP_EXHAUSTED_DAILY_RECOVERY` | `75` | суточное восстановление в «истощении» | :359 |
| `AP_EXHAUSTED_MAX_AP` | `90` | максимум ОД в «истощении» | :360 |
| `SEAWEED_DAILY_LIMIT` | `6` |  | :363 |
| `DIGESTIVE_UPSET_MINUTES` | `1440` | 24 часа | :364 |
| `ALCOHOL_WEAK_DRUNK_LIMIT` | `3` |  | :369 |
| `ALCOHOL_WEAK_VERY_DRUNK_LIMIT` | `6` |  | :370 |
| `ALCOHOL_STRONG_DRUNK_LIMIT` | `1` |  | :372 |
| `ALCOHOL_STRONG_VERY_DRUNK_LIMIT` | `2` |  | :373 |
| `DRUNK_MINUTES` | `60` |  | :374 |
| `VERY_DRUNK_MINUTES` | `360` | 6 часов | :375 |
| `DRINK_EFFECT_LABELS` | `{'alcohol_weak': '🍺 Слабоалкогольный: 3 шт/сутки — «пьян», 6 — «очень пьян»', 'alcohol_strong': '🥃 Крепкий алкоголь: 1 шт — «пьян», 2 — «очень пьян»', 'indigestion': '🤢 Вызывает «несварение» на сут…` |  | :378 |
| `SPECIAL_DEPT_CODE_MIN_LEN` | `4` |  | :389 |
| `SPECIAL_DEPT_CODE_MAX_LEN` | `8` |  | :390 |
| `SPECIAL_DEPT_ATTEMPTS_LIMIT` | `3` | ошибок кода подряд | :391 |
| `SPECIAL_DEPT_BLOCK_MINUTES` | `1440` | бан на 24 часа после 3 ошибок | :392 |
| `FISH_AP_COST` | `3` | стоимость одного заброса удочки | :395 |
| `RESERVOIR_AP_COST` | `5` |  | :400 |
| `FISH_WEIGHTS` | `[{'key': 'small', 'label': 'Мелкая', 'mult': 1.0, 'chance': 40}, {'key': 'medium', 'label': 'Средняя', 'mult': 1.15, 'chance': 40}, {'key': 'large', 'label': 'Большая', 'mult': 1.25, 'chance': 20}]` |  | :405 |
| `FISH_TREASURY_SALE_MULT` | `0.5` |  | :413 |
| `FISH_TREASURY_DAILY_LIMIT` | `300` |  | :418 |
| `FOREST_AP_COST` | `4` | запасной цена поиска, если у зоны нет ap_cost в БД | :421 |
| `FOREST_RESULT_DELAY` | `(5, 10)` | результат поиска через 5–10 секунд | :424 |
| `FOREST_SOLD_DAILY_LIMIT` | `250` |  | :429 |
| `FOREST_ALLOW_TOURISTS` | `False` |  | :434 |
| `FOREST_BOAR_PITY_TARGET` | `12` |  | :437 |
| `FOREST_BOAR_CHANCE` | `4.0` |  | :441 |
| `CALLSIGN_PRICE` | `500` |  | :443 |
| `PILOT_BASE_HP` | `100` |  | :445 |
| `FOREST_BOAR_HP` | `40` |  | :450 |
| `FOREST_BOAR_DMG` | `(4, 7)` |  | :451 |
| `FOREST_BOAR_DODGE` | `15` |  | :452 |
| `FOREST_BOAR_LOSS_AP` | `10` |  | :454 |
| `FOREST_BOAR_LOOT` | `[('Мясо кабана', 50), ('Шкура кабана', 20), ('Клык кабана', 10), ('', 20)]` |  | :456 |
| `FOREST_WHITE_WOLF_HP` | `120` |  | :468 |
| `FOREST_WHITE_WOLF_DMG` | `(7, 12)` |  | :469 |
| `FOREST_WHITE_WOLF_DODGE` | `20` |  | :470 |
| `FOREST_WHITE_WOLF_LOSS_AP` | `15` |  | :472 |
| `FOREST_WHITE_WOLF_CHANCE` | `2.0` |  | :473 |
| `FOREST_WHITE_WOLF_PITY_TARGET` | `36` |  | :476 |
| `FOREST_WHITE_WOLF_BLEED_CHANCE` | `30` |  | :478 |
| `FOREST_WHITE_WOLF_BLEED_DMG` | `3` |  | :479 |
| `FOREST_WHITE_WOLF_AUTOWIN_HP` | `20` |  | :481 |
| `FOREST_WHITE_WOLF_SMALL_BLESSING` | `'внимание севера'` |  | :483 |
| `FOREST_WHITE_WOLF_BIG_BLESSING` | `'благословение севера'` |  | :484 |
| `FOREST_BOAR_SEED` | `{'key': 'boar', 'spot': 'forest', 'name': 'Дикий кабан', 'hp': FOREST_BOAR_HP, 'dmg_min': FOREST_BOAR_DMG[0], 'dmg_max': FOREST_BOAR_DMG[1], 'dodge': FOREST_BOAR_DODGE, 'loss_ap': FOREST_BOAR_LOSS_…` |  | :491 |
| `FOREST_WHITE_WOLF_SEED` | `{'key': 'white_wolf', 'spot': 'forest', 'name': 'Белый Волк Севера', 'hp': FOREST_WHITE_WOLF_HP, 'dmg_min': FOREST_WHITE_WOLF_DMG[0], 'dmg_max': FOREST_WHITE_WOLF_DMG[1], 'dodge': FOREST_WHITE_WOLF…` |  | :516 |
| `MOLLUSK_SEED` | `{'key': 'mollusk', 'spot': 'reservoir', 'name': 'Мутировавший моллюск', 'hp': 24, 'dmg_min': 5, 'dmg_max': 9, 'dodge': 20, 'loss_ap': 12, 'chance': 4, 'pity_target': 0, 'reward_nm': 0, 'photo_key':…` |  | :544 |
| `MOLLUSK_ITEM_SEEDS` | `[('Мясо моллюска', 'Плотное мясо мутировавшего моллюска. В сыром виде есть нельзя — прожарь на кухне.', 120, 60, 3, 'resource', 0), ('Жемчужина', 'Редчайшая жемчужина из раковины мутировавшего молл…` |  | :567 |
| `MOLLUSK_ENEMY_DROPS` | `('Мясо моллюска', 'Жемчужина')` |  | :582 |
| `MINE_AP_COST` | `12` | стоимость одной попытки добычи | :591 |
| `MINE_BASE_CHANCE` | `30` | базовый шанс успеха без бонуса кирки | :592 |
| `MINE_PICKAXE_BONUS_PER_RANK` | `15` | надбавка к шансу за ступень кирки (ранг 1 → +15%) | :593 |
| `MINE_CHANCE_CAP` | `90` | потолок шанса успеха | :594 |
| `MINE_RESULT_DELAY` | `(7, 15)` | результат добычи через 7–15 секунд | :595 |
| `MINE_REQUIRED_STATUS` | `'pilot1'` | вход в копь — с «Пилота 1 класса» | :596 |
| `MINE_GEM_CAP` | `1` | из самоцветов за бой выпадает не больше одного | :597 |
| `MINE_PICKAXE_NAME` | `'Кирка'` |  | :598 |
| `MINE_ORE_NAME` | `'Железная руда'` |  | :599 |
| `MINE_BAT_KEY` | `'bat'` |  | :602 |
| `MINE_BAT_SPOT` | `'iron'` |  | :603 |
| `MINE_BAT_CHANCE` | `7.0` |  | :604 |
| `MINE_BAT_PITY_TARGET` | `12` |  | :605 |
| `MINE_BAT_SEED` | `{'key': MINE_BAT_KEY, 'spot': MINE_BAT_SPOT, 'name': 'Летучая мышь', 'hp': 22, 'dmg_min': 3, 'dmg_max': 7, 'dodge': 35, 'loss_ap': 15, 'chance': MINE_BAT_CHANCE, 'pity_target': MINE_BAT_PITY_TARGET…` |  | :610 |
| `MINE_ITEM_SEEDS` | `[(MINE_PICKAXE_NAME, 'Простая кирка шахтёра: без неё в штольню не сунешься, а с ней порода поддаётся легче. Повышает шанс успешной добычи руды.', 300, 150, 1, 'mining', 0), (MINE_ORE_NAME, 'Кусок ж…` |  | :636 |
| `MINE_SHOP_ITEMS` | `(MINE_PICKAXE_NAME,)` |  | :657 |
| `MINE_ENEMY_DROPS` | `('Изумруд', 'Рубин', 'Сапфир')` |  | :660 |
| `ON_HIT_EFFECTS` | `{'bleed': {'emoji': '🩸', 'title': 'Кровотечение', 'until_battle_end': True, 'params': (('chance', 'Шанс наложить, %', 'percent'), ('dmg', 'Урон, HP за ход', 'int')), 'hint': 'Раны сочатся кровью ка…` |  | :669 |
| `ON_HIT_KIND_ORDER` | `('bleed', 'poison', 'frostbite', 'state', 'lifesteal')` |  | :723 |
| `ON_HIT_STATE_ROUNDS` | `{'оглушён': 3, 'ослеплён': 4}` |  | :725 |
| `CLAN_ROLES` | `{'leader': '👑 Глава клана', 'seneschal': '🛡 Сенешаль клана', 'banner': '🚩 Знаменосец клана', 'elder': '⭐ Старшина', 'member': '▪️ Член клана'}` |  | :731 |
| `CLAN_ROLE_ORDER` | `('leader', 'seneschal', 'banner', 'elder', 'member')` |  | :738 |
| `LOGGING_AP_COST` | `12` | стоимость одной попытки рубки | :744 |
| `LOGGING_BASE_CHANCE` | `35` | базовый шанс успеха без бонуса топора | :745 |
| `LOGGING_AXE_BONUS_PER_RANK` | `15` | надбавка к шансу за ступень топора | :746 |
| `LOGGING_CHANCE_CAP` | `90` | потолок шанса успеха | :747 |
| `LOGGING_AXE_SLIP_CHANCE` | `2.5` | шанс, что топор отскочит пилоту в плечо, % | :748 |
| `LOGGING_RESULT_DELAY` | `(7, 15)` | результат рубки через 7–15 секунд | :749 |
| `LOGGING_AXE_NAME` | `'Топор'` |  | :750 |
| `LOGGING_WOOD_NAME` | `'Бревна'` |  | :751 |
| `LOGGING_PLANK_NAME` | `'Доска'` |  | :757 |
| `LOGGING_FIREWOOD_NAME` | `'Пак дров'` |  | :758 |
| `LOGGING_PLANK_YIELD` | `3` | досок из одного бревна | :759 |
| `LOGGING_PLANK_FEE` | `15` | НМ за распил одного бревна (в казну) | :760 |
| `LOGGING_FIREWOOD_YIELD` | `3` | паков дров из одного бревна | :761 |
| `LOGGING_FIREWOOD_AP_COST` | `4` | ОД за рубку дров из одного бревна | :762 |
| `LOGGING_SNAKE_KEY` | `'snake'` |  | :766 |
| `LOGGING_OWL_KEY` | `'owl'` |  | :767 |
| `LOGGING_SPOT` | `'logging'` |  | :768 |
| `LOGGING_SNAKE_CHANCE` | `8.0` |  | :769 |
| `LOGGING_SNAKE_PITY_TARGET` | `10` |  | :770 |
| `LOGGING_OWL_CHANCE` | `3.0` |  | :771 |
| `LOGGING_OWL_PITY_TARGET` | `24` |  | :772 |
| `LOGGING_SNAKE_POISON_CHANCE` | `30` |  | :774 |
| `LOGGING_SNAKE_POISON_DMG` | `2` |  | :775 |
| `LOGGING_OWL_FLEE_HP` | `20` |  | :779 |
| `LOGGING_OWL_BLIND_CHANCE` | `30` |  | :780 |
| `LOGGING_OWL_BLIND_ROUNDS` | `4` |  | :781 |
| `LOGGING_SNAKE_SEED` | `{'key': LOGGING_SNAKE_KEY, 'spot': LOGGING_SPOT, 'name': 'Лесная змея', 'hp': 30, 'dmg_min': 4, 'dmg_max': 8, 'dodge': 25, 'loss_ap': 10, 'chance': LOGGING_SNAKE_CHANCE, 'pity_target': LOGGING_SNAK…` |  | :785 |
| `LOGGING_OWL_SEED` | `{'key': LOGGING_OWL_KEY, 'spot': LOGGING_SPOT, 'name': 'Неясыть', 'hp': 90, 'dmg_min': 7, 'dmg_max': 12, 'dodge': 30, 'loss_ap': 15, 'chance': LOGGING_OWL_CHANCE, 'pity_target': LOGGING_OWL_PITY_TA…` |  | :815 |
| `LOGGING_ITEM_SEEDS` | `[(LOGGING_AXE_NAME, 'Крепкий лесорубский топор: без него к срубам не подпустят. Повышает шанс успешной рубки деревьев.', 300, 150, 1, 'mining', 0), (LOGGING_WOOD_NAME, 'Свежие срубленные брёвна из …` |  | :847 |
| `LOGGING_SHOP_ITEMS` | `(LOGGING_AXE_NAME,)` |  | :881 |
| `LOGGING_ENEMY_DROPS` | `('Змеиная кожа', 'Змеиный яд', 'Совиное перо')` |  | :884 |
| `LOGGING_MARKET_RESOURCES` | `(LOGGING_PLANK_NAME, LOGGING_FIREWOOD_NAME)` |  | :887 |
| `REPORT_DAILY_LIMIT` | `3` |  | :889 |
| `REPORT_AUTO_APPROVE_TROOPS` | `100` |  | :890 |
| `NEWS_PUBLISH_BONUS` | `10` |  | :894 |
| `NEWS_PUBLISH_CAP` | `28` |  | :895 |
| `ROLE_SALARY_PAY_DAY` | `28` |  | :898 |
| `REPORT_DAILY_PAY_CAP` | `4000` |  | :903 |
| `REPORT_MAX_TROOPS` | `1000000` |  | :904 |
| `REPORT_MAX_REGION` | `38` | 0 = Столица, 1..38 регионы | :905 |
| `WALL_TEXT_MAX_LEN` | `40` | лимит символов на одно изречение | :908 |
| `WALL_FREE_PER_DAY` | `2` | бесплатных сообщений в сутки | :909 |
| `WALL_PAID_STEPS` | `[(3, 30), (3, 90), (3, 200)]` | далее платные ступени: (кол-во, цена НМ) | :910 |
| `WALL_REVIEW_TOTAL` | `11` | максимум сообщений в сутки (2 + 3+3+3) | :915 |
| `WALL_PAGE_SIZE` | `5` | постов на страницу стены | :916 |
| `WALL_ARCHIVE_PAGE_SIZE` | `8` | записей архива стены на страницу списка | :917 |
| `REPORT_ARCHIVE_PAGE` | `8` | отчётов на страницу архива МВД и в «Моих отчётах» | :920 |
| `POLL_MAX_DAYS` | `10` | максимум дней, сколько живёт опрос. Не закрыл | :923 |
| `POLL_VISIBLE` | `4` | сколько новейших опросов висит в меню голосования. | :926 |
| `POLL_ARCHIVE_DAYS_PER_PAGE` | `5` | дней (дат) архива опросов на страницу списка | :929 |
| `POLL_ARCHIVE_PER_DAY` | `6` | опросов под одним заголовком-днём | :930 |
| `REP_SPEECH_MAX_LEN` | `100` | лимит символов одного обращения | :933 |
| `REP_SPEECH_PER_DAY` | `2` | обращений в сутки от представителя | :934 |
| `AUTO_PROMOTE_MAX_TROOPS` | `4040` |  | :939 |

## Буклет туриста

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `TOURIST_BOOKLET_NAME` | `'Буклет туриста'` |  | :24 |

## Суточный цикл Нордхайма

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `REPORT_DAY_START_HOUR` | `10` |  | :134 |

## Дом Дуэлей (PvP-арена)

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `DUEL_ZONES` | `('head', 'body', 'hands', 'legs')` |  | :231 |

## Рынок: слоты продажи

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `MARKET_BASE_SLOTS` | `1` | слоты без лицензии | :306 |

## Налог на недвижимость (НМ/мес)

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `HOUSING_TAX` | `{'municipal': 0, 'studio': 20, 'apartment': 35, 'improved': 60, 'mansion': 100}` |  | :312 |

## Банк: лимит счёта туриста (НМ)

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `TOURIST_BALANCE_LIMIT` | `200` |  | :322 |

## Данж: лимит хила (количество применений за забег)

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `DUNGEON_HEAL_SOFT_LIMIT` | `6` | после этого — ×2/3 | :325 |

## Сброс протухших забегов подземелья

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `DUNGEON_RUN_STALE_SEC` | `3600` |  | :334 |

## Данж: побег и дымовая шашка

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `ESCAPE_BASE_CHANCE` | `25` |  | :342 |

