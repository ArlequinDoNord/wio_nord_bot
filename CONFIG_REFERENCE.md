# Справочник констант `config.py`

> **Сгенерировано** `tools/export_config.py`. Перегенерация:
> `.venv\Scripts\python.exe tools/export_config.py`.
>
> Все модульные константы `config.py`, сгруппированные по секциям
> (комментариям-разделителям `# ── … ──`). Длинные значения усечены `…`;
> точное значение — в `config.py` по строке из первой колонки.

Всего констант: **360**; разделов: **11**.

## Без раздела

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `VERSION` | `'0.43.15'` |  | :16 |
| `VERSION_NOTES` | `'В глубинах... что-то изменилось'` |  | :17 |
| `PREV_VERSION` | `'0.43.14'` |  | :18 |
| `PREV_VERSION_NOTES` | `'В глубинах... что-то изменилось'` |  | :19 |
| `TOURIST_BOOKLET_DESCRIPTION` | `'Печатная карта Нордхайма для гостей города. Просматривай превью городских локаций — и отмечай их в буклете. Собери все 9 и получи награду от командования.'` |  | :22 |
| `TOURIST_BOOKLET_PRICE` | `1` |  | :25 |
| `TOURIST_BOOKLET_SELL_PRICE` | `0` | буклет не продаётся (иначе чек-лист теряется) | :26 |
| `TOURIST_BOOKLET_AWARD` | `'Опытный турист'` |  | :27 |
| `TOURIST_BOOKLET_AWARD_EMOJI` | `'🧭'` |  | :28 |
| `TOURIST_BOOKLET_AWARD_DESCRIPTION` | `'Посетил все городские локации Нордхайма по «Буклету туриста». Знак почётного гостя города.'` |  | :29 |
| `TOURIST_BOOKLET_REWARD_NM` | `20` |  | :31 |
| `TOURIST_BOOKLET_REWARD_TX` | `'booklet'` |  | :32 |
| `TOURIST_BOOKLET_LOCATIONS` | `('townhall', 'library', 'park', 'gossmi', 'bank', 'kvp', 'hq', 'contracts', 'nii')` |  | :35 |
| `CLAN_HALL_ENABLED` | `True` |  | :42 |
| `FIRELAB_SCARECROW_HP` | `25` |  | :45 |
| `FIRELAB_SCARECROW_DMG` | `(3, 5)` |  | :46 |
| `FIRELAB_SCARECROW_DODGE` | `10` |  | :47 |
| `FIRELAB_SCARECROW_ARMOR` | `1` | броня Пугала (стены соломы) | :48 |
| `FIRELAB_APPLE_CHILD_HP` | `27` |  | :49 |
| `FIRELAB_APPLE_CHILD_DMG` | `(2, 4)` |  | :50 |
| `FIRELAB_APPLE_CHILD_DODGE` | `9` |  | :51 |
| `FIRELAB_CROW_HP` | `16` |  | :52 |
| `FIRELAB_CROW_DMG` | `(2, 4)` |  | :53 |
| `FIRELAB_CROW_DODGE` | `20` |  | :54 |
| `FIRELAB_GHOST_HP` | `24` |  | :55 |
| `FIRELAB_GHOST_DMG` | `(2, 4)` |  | :56 |
| `FIRELAB_GHOST_DODGE` | `15` |  | :57 |
| `FIRELAB_HUB_DODGE` | `FIRELAB_GHOST_DODGE` |  | :58 |
| `FIRELAB_HUB_HP` | `FIRELAB_GHOST_HP` |  | :59 |
| `FIRELAB_HUB_DMG` | `FIRELAB_GHOST_DMG` |  | :60 |
| `FIRELAB_PUMPKIN_HP` | `60` |  | :61 |
| `FIRELAB_PUMPKIN_DMG` | `(4, 7)` |  | :62 |
| `FIRELAB_PUMPKIN_DODGE` | `5` |  | :63 |
| `FIRELAB_PUMPKIN_ARMOR` | `2` | броня босса | :64 |
| `FIRE_LAB_PIE_NAME` | `'Кусочек тыквенного пирога'` |  | :68 |
| `FIRE_LAB_CANDY_NAME` | `'Леденец языков пламени'` |  | :69 |
| `FIRE_LAB_HAY_NAME` | `'Пучок сена'` |  | :70 |
| `FIRE_LAB_BRANCH_NAME` | `'Ветка дерева'` |  | :71 |
| `FIRE_LAB_RECIPE_NAME` | `'Рецепт: Тыквенный пирог'` |  | :72 |
| `FIRE_PUMPKIN_SEED_NAME` | `'Семечко тыквы'` | посадка в кадку / клан. сад | :73 |
| `FIRE_CROW_FEATHER_NAME` | `'Перо ворона'` | ресурс (дроп стража? — Ф5) | :74 |
| `FIRE_WIRE_NAME` | `'Моток железной проволоки'` | ингредиент трости | :75 |
| `FIRE_EGGS_NAME` | `'Яйца'` | ингредиент пирога (x2) | :76 |
| `FIRE_CROWN_NAME` | `'Огненный венец'` | голова: броня 2, лечение +25% | :77 |
| `FIRE_CLOAK_NAME` | `'Плащ Памяти'` | тело: броня 2, уклон +5% | :78 |
| `FIRE_GLOVES_NAME` | `'Перчатки стража посевов'` | руки: броня 2, уклон +3% | :79 |
| `FIRE_KEYS_NAME` | `'Вилы'` | оружие: +2 к удару, кровотечение | :80 |
| `FIRE_FLAME_DEVICE_NAME` | `'Ручное пламенеющее устройство'` | ингредиент трости | :81 |
| `FIRELAB_SCARECROW_SEED` | `{'key': 'scarecrow', 'spot': 'firelab', 'name': 'Пугало', 'hp': FIRELAB_SCARECROW_HP, 'dmg_min': FIRELAB_SCARECROW_DMG[0], 'dmg_max': FIRELAB_SCARECROW_DMG[1], 'dodge': FIRELAB_SCARECROW_DODGE, 'ar…` |  | :83 |
| `FIRELAB_APPLE_CHILD_SEED` | `{'key': 'apple_child', 'spot': 'firelab', 'name': 'Дитя Яблони', 'hp': FIRELAB_APPLE_CHILD_HP, 'dmg_min': FIRELAB_APPLE_CHILD_DMG[0], 'dmg_max': FIRELAB_APPLE_CHILD_DMG[1], 'dodge': FIRELAB_APPLE_C…` |  | :110 |
| `FIRELAB_CROW_SEED` | `{'key': 'crow', 'spot': 'firelab', 'name': 'Ворон', 'hp': FIRELAB_CROW_HP, 'dmg_min': FIRELAB_CROW_DMG[0], 'dmg_max': FIRELAB_CROW_DMG[1], 'dodge': FIRELAB_CROW_DODGE, 'loss_ap': 0, 'chance': 0, 'p…` |  | :137 |
| `FIRELAB_HUB_SEED` | `{'key': 'hub', 'spot': 'firelab', 'name': 'Хуб', 'hp': FIRELAB_HUB_HP, 'dmg_min': FIRELAB_HUB_DMG[0], 'dmg_max': FIRELAB_HUB_DMG[1], 'dodge': FIRELAB_HUB_DODGE, 'loss_ap': 0, 'chance': 0, 'pity_tar…` |  | :162 |
| `FIRELAB_PUMPKIN_SEED` | `{'key': 'pumpkin_boss', 'spot': 'firelab', 'name': 'Мощный Мистер Огненная Тыква', 'hp': FIRELAB_PUMPKIN_HP, 'dmg_min': FIRELAB_PUMPKIN_DMG[0], 'dmg_max': FIRELAB_PUMPKIN_DMG[1], 'dodge': FIRELAB_P…` |  | :189 |
| `FIRELAB_ENEMY_SEEDS` | `(FIRELAB_SCARECROW_SEED, FIRELAB_APPLE_CHILD_SEED, FIRELAB_CROW_SEED, FIRELAB_HUB_SEED, FIRELAB_PUMPKIN_SEED)` |  | :219 |
| `FIRE_EVENT_ENABLED` | `True` |  | :227 |
| `FIRE_EVENT_START` | `(2026, 10, 30, 0, 0)` | МСК, ночь на пятницу 30.10 | :228 |
| `FIRE_EVENT_DURATION_DAYS` | `7` | до ~00:00 МСК 6.11 (т.е. весь 5.11) | :229 |
| `FIRE_LAB_ENABLED` | `True` |  | :231 |
| `FIRE_EVENT_LAB_FEE` | `32` | вход в лабиринт, НМ | :232 |
| `FIRE_EVENT_MAX_ENTRIES_DAY` | `4` | максимум заходов за сутки | :233 |
| `FIRE_LAB_SESSION_TTL_SEC` | `3600` | неактивность: сессия закрывается автоматически (1 ч) | :234 |
| `FIRE_LAB_FORK_KEY` | `'city/fire_maze'` | развилка (вход/смерть/уход/финиш) | :237 |
| `FIRE_LAB_WELL_KEY` | `'city/fire_well'` | Колодец | :238 |
| `FIRE_LAB_TREE_KEY` | `'city/fire_tree'` | Древо Огня | :239 |
| `FIRE_LAB_SCARECROW_BLIND_P` | `0.15` | Пугало: «сено в лицо» — ослепление | :244 |
| `FIRE_LAB_APPLE_STUN_P` | `0.1` | Дитя Яблони: «яблочко» — оглушение | :245 |
| `FIRE_LAB_CROW_BLIND_P` | `0.15` | Ворон: ослепление (как сова) | :246 |
| `FIRE_LAB_HUB_SLOW_P` | `0.25` |  | :247 |
| `FIRE_LAB_HUB_SLOW_ROUNDS` | `3` |  | :248 |
| `FIRE_LAB_HUB_PLAYER_DODGE_PENALTY` | `35` |  | :249 |
| `FIRE_LAB_HUB_ENEMY_DODGE_BONUS` | `10` |  | :250 |
| `FIRE_LAB_BOSS_BURN_P` | `0.25` | Босс «Мистер Тыква»: поджиг игрока | :251 |
| `FIRE_LAB_BOSS_BURN_DMG` | `2` | −HP/ход | :252 |
| `FIRE_LAB_BOSS_BURN_ROUNDS` | `3` |  | :253 |
| `FIRE_LAB_BOSS_MAX` | `2` | максимум встреч с боссом за заход | :254 |
| `FIRE_LAB_ROOMS_MAX` | `25` | после 25 комнат-развилок выход автоматом | :255 |
| `FIRE_LAB_TIER_MAX` | `10` | кап усилений | :258 |
| `FIRE_LAB_TIER_HP_STEP` | `2` | +HP всем врагам за тир (1–4) | :259 |
| `FIRE_LAB_TIER_HP_LAST` | `8` | 5-й тир: разово +8 (итого +16) | :260 |
| `FIRE_LAB_TIER_HP_STEP_MID` | `4` | +HP всем врагам за тир (6–9) | :261 |
| `FIRE_LAB_TIER_HP_10` | `16` | 10-й тир: разово +16 | :262 |
| `FIRE_LAB_TIER_LOOT_STEP` | `0.02` | лут ×(1+2%) за тир (1–4, 6–9) | :263 |
| `FIRE_LAB_RARE_MIN_RARITY` | `3` | редкий лут = предмет с полем редкости >= 3 («Редкий» и выше) | :264 |
| `FIRE_LAB_RARE_TIER_BONUS` | `0.014` | редкий лут: +1.4 п.п. шанса за каждый тир (в долях) | :265 |
| `FIRE_LAB_TIER_LOOT_LAST` | `0.1` | 5-й и 10-й тиры: ×(1+10%) | :266 |
| `FIRE_LAB_WELL_MAX` | `3` | максимум посещений колодца за заход | :269 |
| `FIRE_LAB_TREE_MAX` | `1` | древо — раз за заход | :270 |
| `FIRE_LAB_ROOM_WEIGHTS` | `{(False, True): (('tree', 9), ('well', 6), ('enemy', 60)), (False, False): (('enemy', 65),), (True, True): (('tree', 9), ('well', 6), ('boss', 32), ('enemy', 41)), (True, False): (('boss', 32), ('e…` |  | :274 |
| `FIRE_TREE_DMG_BONUS_PCT` | `15` | +15% урона | :283 |
| `FIRE_TREE_REGEN_HP` | `1` | +1 HP после каждого удара игрока | :284 |
| `FIRE_LAB_PATTERN_WELL` | `('L', 'L', 'S', 'S')` | ЛЛПП → Колодец (до 3) | :288 |
| `FIRE_LAB_PATTERN_TREE` | `('L', 'L', 'S', 'S', 'R', 'R')` | ЛЛППНН → Древо Огня (1) | :289 |
| `FIRE_LAB_WELL_FISH_TRIES` | `6` | попыток рыбалки за один визит в Колодец | :292 |
| `FIRE_LAB_WELL_HEAL` | `50` | колодец: фиксированное лечение за визит, HP | :293 |
| `FIRE_LAB_WELL_AP` | `10` | колодец: восстановление ОД за визит (не выше максимума) | :294 |
| `FIRE_SET_REGEN_HP` | `1` | сет праздничной одежды+оружия: регенерация за ход в Лабиринте | :295 |
| `FIRE_EXCHANGE_ENABLED` | `True` |  | :298 |
| `FIRE_EXCHANGE_OFFERS` | `((FIRE_LAB_HAY_NAME, 3, FIRE_LAB_PIE_NAME, 1), (FIRE_LAB_BRANCH_NAME, 3, FIRE_LAB_CANDY_NAME, 1), (((FIRE_LAB_HAY_NAME, 15), (FIRE_LAB_BRANCH_NAME, 15)), 'Рецепт: Леденец из ягод', 1))` |  | :299 |
| `FIRE_LAB_FISH_DELAY` | `(7, 15)` | колодец: поклёвка через N секунд (как на озере) | :307 |
| `FIRE_LAB_NOBAIT_FIND_P` | `0.12` | колодец без наживки: шанс поднять что-то со дна (%/100) | :308 |
| `FIRE_LAB_NOBAIT_FIND` | `((FIRE_WIRE_NAME, 35), (FIRE_LAB_HAY_NAME, 65))` | что поднимается без наживки (вес) | :309 |
| `FIRE_LAB_FISH_OSETR_NAME` | `'Спектральная Латимерия'` | рыба 1 (rarity 2) | :314 |
| `FIRE_LAB_FISH_SOUL_NAME` | `'Скелетная Арована'` | рыба 2 (rarity 3) | :315 |
| `FIRE_LAB_FISH_CARP_NAME` | `'Пылающая Душа'` | рыба 3 (rarity 4, редкая) | :316 |
| `FIRE_LAB_FISH_TABLE` | `((FIRE_LAB_FISH_OSETR_NAME, 60), (FIRE_LAB_FISH_SOUL_NAME, 25), (FIRE_LAB_FISH_CARP_NAME, 15))` | взвешенный выбор улова | :317 |
| `FIRE_FISHER_ACH_KEY` | `'fire_fisher'` |  | :323 |
| `FIRE_FISHER_THRESHOLD` | `3` |  | :324 |
| `FIRE_FISHER_REWARD_NM` | `150` |  | :325 |
| `FIRE_LAB_PIE_HEAL` | `15` |  | :327 |
| `FIRE_LAB_CANDY_HEAL` | `12` |  | :328 |
| `FIRE_PUMPKIN_NAME` | `'Тыква'` | плод; ингредиент пирога | :332 |
| `FIRE_SUGAR_NAME` | `'Сахар'` | ингредиент пирога | :333 |
| `FIRE_KEYS_DMG` | `2` |  | :334 |
| `FIRE_KEYS_BLEED_P` | `10` |  | :335 |
| `FIRE_KEYS_BLEED_DMG` | `2` |  | :336 |
| `FIRE_CROWN_HEAL_BONUS_PCT` | `25` |  | :337 |
| `FIRE_CLOAK_DODGE` | `5` |  | :338 |
| `FIRE_GLOVES_DODGE` | `3` |  | :339 |
| `FIRE_CANE_NAME` | `'Обжигающая трость'` | оружие: удар 3, поджог 20% | :340 |
| `FIRE_CANE_DMG` | `3` |  | :341 |
| `FIRE_CANE_BURN_P` | `20` |  | :342 |
| `FIRE_CANE_BURN_DMG` | `2` |  | :343 |
| `FIRE_CANE_BURN_ROUNDS` | `3` |  | :344 |
| `FIRE_LANTERN_NAME` | `'Лампа Круговорота'` | награда за «Чтящего Предков» (Ф4б) | :345 |
| `FIRE_MUSHROOM_NAME` | `'Огненный гриб'` | гриб леса; только пожертвование | :348 |
| `FIRE_BERRY_NAME` | `'Горсть Пылающих ягод'` | ягода леса (прогалина); только пожертвование | :349 |
| `FIRE_ORE_NAME` | `'Пламенная руда'` | добыча шахты; только пожертвование | :350 |
| `FIRE_ORE_CHANCE` | `15` | % за один удар киркой | :351 |
| `FIRE_TALISMAN_NAME` | `'Талисман памяти'` | награда за полное пожертвование: +1 регенерация за ход | :352 |
| `FIRE_TALISMAN_REGEN` | `1` |  | :353 |
| `FIRE_SPOILED_FOOD_NAME` | `'Испорченная еда'` | один предмет для любой испорченной съедобной еды | :354 |
| `FIRE_TREE_DONATION` | `((FIRE_MUSHROOM_NAME, 2), (FIRE_BERRY_NAME, 2), (FIRE_ORE_NAME, 1))` |  | :356 |
| `FIRE_DONATION_ONLY` | `(FIRE_MUSHROOM_NAME, FIRE_BERRY_NAME, FIRE_ORE_NAME)` |  | :362 |
| `FIRE_AMBER_NAME` | `'Пламя Памяти'` | янтарь из Лампы (Ф4б), продам 100 НМ | :363 |
| `FIRE_LANTERN_MEDIT_AP` | `20` | 🪔 медитация раз в сутки | :364 |
| `FIRE_LANTERN_AMBER_DAYS` | `7` | янтарь раз в N суток | :365 |
| `FIRE_PREDKI_NAME` | `'Предания предков'` |  | :368 |
| `FIRE_PREDKI_HEAL` | `60` | +60 HP в бою | :369 |
| `FIRE_PREDKI_REGEN` | `50` | регенерация: 50% от лечения | :370 |
| `FIRE_PREDKI_REGEN_TURNS` | `4` | разлитая на 4 хода (нестандарт!) | :371 |
| `FIRE_PREDKI_DODGE_PCT` | `5` | суточный баф: уворот +5% | :372 |
| `FIRE_PREDKI_DODGE_HOURS` | `24` | длительность бафа (не продлевается) | :373 |
| `CLAN_BUILDING_TYPES` | `{'house': {'name': 'Дом Клана', 'slots': 2, 'max_level': 2, 'days': 2, 'price_nm': 3000, 'required': {'Доска': 60, 'Бревна': 20, 'Железная руда': 15}}, 'manor': {'name': 'Клановое поместье', 'slots…` |  | :375 |
| `CLAN_BUILDING_NO_RESOURCES_MULT` | `2` |  | :390 |
| `CLAN_EXPANSION_TYPES` | `('kitchen', 'workbench', 'shower', 'garden', 'library', 'shop', 'tree')` |  | :392 |
| `CLAN_EXPANSION_INFO` | `{'kitchen': {'name': 'Кухня', 'icon': '🍳', 'desc': 'Готовка по выученным рецептам; уровень задаёт доступные блюда.'}, 'workbench': {'name': 'Крафтовый стол', 'icon': '🛠', 'desc': 'Крафт снаряжения …` |  | :394 |
| `FIRE_TREE_CLAN_MEDIT_AP` | `20` | 🧘 медитация у Древа (в доп. к домашней) | :416 |
| `FIRE_TREE_CLAN_ESSENCE_NAME` | `'Эссенция Памяти'` |  | :417 |
| `FIRE_TREE_CLAN_ESSENCE_DAYS` | `30` | раз в 30 дней (от установки/сбора) | :418 |
| `FIRE_TREE_CLAN_ESSENCE_SELL` | `500` | продажа кристалла на скупке | :419 |
| `CLAN_EXPANSION_UPGRADE` | `{2: {'nm': 1500, 'required': {'Доска': 20, 'Железная руда': 10}}, 3: {'nm': 4000, 'required': {'Доска': 50, 'Железная руда': 30}}, 4: {'nm': 9000, 'required': {'Доска': 100, 'Железная руда': 60}}}` |  | :421 |
| `CLAN_SHOWER_AP_BY_LEVEL` | `{1: 25, 2: 50, 3: 75, 4: 100}` |  | :429 |
| `CLAN_SHOWER_SOBER_MINUTES` | `{1: 60, 2: 120, 3: 180, 4: 240}` |  | :430 |
| `CLAN_GARDEN_PLOTS` | `{1: 2, 2: 3, 3: 4, 4: 6}` |  | :432 |
| `CLAN_SHOP_DAILY_LIMIT` | `3` |  | :433 |
| `CLAN_SHOP_DISCOUNT` | `10` |  | :434 |
| `BOT_TOKEN` | `os.getenv('BOT_TOKEN')` |  | :436 |
| `ADMIN_IDS` | `[int(x) for x in os.getenv('ADMIN_IDS', '').split(',') if x.strip()]` |  | :437 |
| `_news_raw` | `os.getenv('NEWS_CHAT_ID', '').strip()` |  | :440 |
| `NEWS_CHAT_ID` | `int(_news_raw) if _news_raw.lstrip('-').isdigit() else None` |  | :441 |
| `DB_PATH` | `os.getenv('DATABASE_PATH', 'database/nordmark.db')` |  | :444 |
| `FSM_STORAGE_PATH` | `os.getenv('FSM_STORAGE_PATH', '').strip() or os.path.join(os.path.dirname(os.path.abspath(DB_PATH)), 'fsm')` |  | :453 |
| `REPORT_DAY_START_MINUTE` | `0` |  | :463 |
| `RANKS` | `[('Рекрут', 0), ('Рядовой', 100), ('Ефрейтор', 350), ('Капрал', 500), ('Сержант', 850), ('Старший Сержант', 1500), ('Лейтенант', 2500), ('Старший Лейтенант', 4040), ('Капитан', 6000), ('Майор', 850…` |  | :465 |
| `MAX_SELF_RANK_TROOPS` | `4040` |  | :486 |
| `AUTO_RANK_NAMES` | `('Рекрут', 'Рядовой', 'Ефрейтор', 'Капрал', 'Сержант', 'Старший Сержант', 'Лейтенант', 'Старший Лейтенант')` |  | :489 |
| `AWARD_MAX_SHOP_DISCOUNT` | `40` |  | :496 |
| `AWARD_MIN_REPORT_TAX` | `5` |  | :497 |
| `RANK_STATUS_TAGS` | `{'Ефрейтор': 'pilot2', 'Старший Сержант': 'pilot1', 'Старший Лейтенант': 'veteran', 'Майор': 'master_pilot', 'Полковник': 'ace'}` |  | :499 |
| `LEGIONER_ACCESS_CAP_ORDER` | `5` |  | :512 |
| `RANK_DAMAGE_TIERS` | `{'ace': (4, 8), 'master_pilot': (3, 5), 'veteran': (2, 4), 'pilot1': (1, 3), 'pilot2': (1, 2), 'recruit': (1, 1), 'tourist': (0, 1)}` |  | :518 |
| `RANK_CRIT_CHANCE` | `{'ace': 7.5, 'master_pilot': 6.0, 'veteran': 4.5, 'pilot1': 3.0, 'pilot2': 1.5, 'recruit': 0.0, 'tourist': 0.0}` |  | :536 |
| `PILOT_CRIT_MULT` | `1.4` |  | :550 |
| `PILOT_NO_WEAPON_DMG` | `(1, 1)` |  | :553 |
| `DUEL_ZONE_LABELS` | `{'head': 'Голова', 'body': 'Тело', 'hands': 'Руки', 'legs': 'Ноги'}` |  | :560 |
| `DUEL_ZONE_EMOJI` | `{'head': '🧠', 'body': '🫀', 'hands': '✊', 'legs': '🦵'}` |  | :566 |
| `DUEL_AP_COST` | `15` | списывается с обоих при старте боя | :572 |
| `DUEL_RATING_WIN` | `2` | рейтинг за победу | :573 |
| `DUEL_RATING_LOSS` | `-3` | рейтинг за поражение | :574 |
| `DUEL_RATING_DRAW` | `0` | рейтинг за ничью | :575 |
| `DUEL_RATING_FORFEIT` | `-1` | рейтинг тому, кто покинул бой («Покинуть дуэль») | :576 |
| `DUEL_RATING_FORFEIT_WIN` | `1` | рейтинг сопернику, если противник покинул бой (меньше чистой победы) | :577 |
| `DUEL_MIN_DAMAGE` | `1` | минимум урона за попавший (не уклонённый) удар | :578 |
| `DUEL_GUARD_REDUCTION` | `0.5` | доля урона, остающаяся при угаданной зоне защиты | :579 |
| `DUEL_HEAL_BETWEEN` | `0` | восстановление HP между раундами (пока нет) | :580 |
| `DUEL_CHALLENGE_TIMEOUT_SEC` | `120` | сколько живёт неотвеченный вызов | :581 |
| `DUEL_STALE_SEC` | `1800` | зависшая дуэль авто-завершается как void | :582 |
| `DUEL_GLOVES_NAME` | `'Дуэльные перчатки'` |  | :583 |
| `DUEL_GLOVES_DAMAGE` | `7` |  | :584 |
| `DUEL_GLOVES_PRICE` | `200` |  | :585 |
| `DUEL_GLOVES_SELL` | `100` |  | :586 |
| `DUEL_CLUB_CARD_NAME` | `'Клубная карта «Дом Дуэлей»'` |  | :587 |
| `DUEL_CLUB_CARD_PRICE` | `150` |  | :588 |
| `DUEL_CLUB_CARD_SELL` | `75` |  | :589 |
| `DUEL_CLUB_CARD_DAYS` | `30` |  | :590 |
| `DUEL_ACCESS_TAG` | `'pilot2'` |  | :593 |
| `RARITY_LEVELS` | `{1: 'Обычный', 2: 'Качественный', 3: 'Редкий', 4: 'Шедевр', 5: 'Легендарный'}` |  | :595 |
| `SALE_CONFIRM_MIN_RARITY` | `3` |  | :604 |
| `RARITY_EMOJI` | `{1: '⬜', 2: '🟩', 3: '🟦', 4: '🟪', 5: '🟧'}` |  | :606 |
| `ITEM_CATEGORIES` | `{'weapon': 'Оружие', 'consumable': 'Расходники', 'building': 'Недвижимость', 'housing': 'Жильё', 'furniture': 'Мебель и расширения', 'seeds': 'Семена', 'equipment': 'Одежда', 'resource': 'Ресурсы',…` |  | :614 |
| `MARKET_LICENSE_SLOTS` | `2` | доп. слоты при активной лицензии | :638 |
| `MARKET_LICENSE_DAYS` | `30` | срок действия лицензии (дней) | :639 |
| `MARKET_LICENSE_PRICE` | `500` | цена лицензии в НМ | :640 |
| `DUNGEON_HEAL_HARD_LIMIT` | `10` | после этого — ×1/2 | :657 |
| `DUNGEON_HEAL_SOFT_MULT` | `2 / 3` |  | :658 |
| `DUNGEON_HEAL_HARD_MULT` | `1 / 2` |  | :659 |
| `ESCAPE_HP_BONUS` | `20` |  | :674 |
| `DUNGEON_SMOKE_ESCAPE` | `95` |  | :675 |
| `DUNGEON_SMOKE_MAX` | `2` |  | :676 |
| `DUNGEON_ESCAPE_DRUNK_MULT` | `0.5` |  | :679 |
| `AP_MAX` | `150` |  | :681 |
| `AP_DAILY_RECOVERY` | `100` |  | :682 |
| `AP_BONUS_FROM_CONSUMABLE` | `50` |  | :683 |
| `AP_DAILY_RESTORE_LIMIT` | `150` |  | :688 |
| `AP_EXHAUSTED_MINUTES` | `2880` | 2 суток | :689 |
| `AP_EXHAUSTED_DAILY_RECOVERY` | `75` | суточное восстановление в «истощении» | :690 |
| `AP_EXHAUSTED_MAX_AP` | `90` | максимум ОД в «истощении» | :691 |
| `FIRE_LANTERN_EXHAUST_REDUCE_PCT` | `50` |  | :693 |
| `SEAWEED_DAILY_LIMIT` | `6` |  | :696 |
| `DIGESTIVE_UPSET_MINUTES` | `1440` | 24 часа | :697 |
| `ALCOHOL_WEAK_DRUNK_LIMIT` | `3` |  | :702 |
| `ALCOHOL_WEAK_VERY_DRUNK_LIMIT` | `6` |  | :703 |
| `ALCOHOL_STRONG_DRUNK_LIMIT` | `1` |  | :705 |
| `ALCOHOL_STRONG_VERY_DRUNK_LIMIT` | `2` |  | :706 |
| `DRUNK_MINUTES` | `60` |  | :707 |
| `VERY_DRUNK_MINUTES` | `360` | 6 часов | :708 |
| `DRINK_EFFECT_LABELS` | `{'alcohol_weak': '🍺 Слабоалкогольный: 3 шт/сутки — «пьян», 6 — «очень пьян»', 'alcohol_strong': '🥃 Крепкий алкоголь: 1 шт — «пьян», 2 — «очень пьян»', 'indigestion': '🤢 Вызывает «несварение» на сут…` |  | :711 |
| `SPECIAL_DEPT_CODE_MIN_LEN` | `4` |  | :722 |
| `SPECIAL_DEPT_CODE_MAX_LEN` | `8` |  | :723 |
| `SPECIAL_DEPT_ATTEMPTS_LIMIT` | `3` | ошибок кода подряд | :724 |
| `SPECIAL_DEPT_BLOCK_MINUTES` | `1440` | бан на 24 часа после 3 ошибок | :725 |
| `FISH_AP_COST` | `3` | стоимость одного заброса удочки | :728 |
| `FISH_BAIT_MISS_SEAWEED_CHANCE` | `8` | % шанс вытащить водоросли при промахе с наживкой | :729 |
| `RESERVOIR_AP_COST` | `5` |  | :734 |
| `FISH_WEIGHTS` | `[{'key': 'small', 'label': 'Мелкая', 'mult': 1.0, 'chance': 40}, {'key': 'medium', 'label': 'Средняя', 'mult': 1.15, 'chance': 40}, {'key': 'large', 'label': 'Большая', 'mult': 1.25, 'chance': 20}]` |  | :739 |
| `FISH_TREASURY_SALE_MULT` | `0.5` |  | :747 |
| `FISH_TREASURY_DAILY_LIMIT` | `300` |  | :752 |
| `FOREST_AP_COST` | `4` | запасной цена поиска, если у зоны нет ap_cost в БД | :755 |
| `FOREST_RESULT_DELAY` | `(5, 10)` | результат поиска через 5–10 секунд | :758 |
| `FOREST_SOLD_DAILY_LIMIT` | `250` |  | :763 |
| `FOREST_ALLOW_TOURISTS` | `False` |  | :768 |
| `FOREST_BOAR_PITY_TARGET` | `12` |  | :771 |
| `FOREST_BOAR_CHANCE` | `4.0` |  | :775 |
| `CALLSIGN_PRICE` | `500` |  | :777 |
| `PILOT_BASE_HP` | `100` |  | :779 |
| `FOREST_BOAR_HP` | `40` |  | :784 |
| `FOREST_BOAR_DMG` | `(4, 7)` |  | :785 |
| `FOREST_BOAR_DODGE` | `15` |  | :786 |
| `FOREST_BOAR_LOSS_AP` | `10` |  | :788 |
| `FOREST_BOAR_LOOT` | `[('Мясо кабана', 50), ('Шкура кабана', 20), ('Клык кабана', 10), ('', 20)]` |  | :790 |
| `FOREST_WHITE_WOLF_HP` | `120` |  | :802 |
| `FOREST_WHITE_WOLF_DMG` | `(7, 12)` |  | :803 |
| `FOREST_WHITE_WOLF_DODGE` | `20` |  | :804 |
| `FOREST_WHITE_WOLF_LOSS_AP` | `15` |  | :806 |
| `FOREST_WHITE_WOLF_CHANCE` | `2.0` |  | :807 |
| `FOREST_WHITE_WOLF_PITY_TARGET` | `36` |  | :810 |
| `FOREST_WHITE_WOLF_BLEED_CHANCE` | `30` |  | :812 |
| `FOREST_WHITE_WOLF_BLEED_DMG` | `3` |  | :813 |
| `FOREST_WHITE_WOLF_AUTOWIN_HP` | `20` |  | :815 |
| `FOREST_WHITE_WOLF_SMALL_BLESSING` | `'внимание севера'` |  | :817 |
| `FOREST_WHITE_WOLF_BIG_BLESSING` | `'благословение севера'` |  | :818 |
| `FOREST_BOAR_SEED` | `{'key': 'boar', 'spot': 'forest', 'name': 'Дикий кабан', 'hp': FOREST_BOAR_HP, 'dmg_min': FOREST_BOAR_DMG[0], 'dmg_max': FOREST_BOAR_DMG[1], 'dodge': FOREST_BOAR_DODGE, 'loss_ap': FOREST_BOAR_LOSS_…` |  | :825 |
| `FOREST_WHITE_WOLF_SEED` | `{'key': 'white_wolf', 'spot': 'forest', 'name': 'Белый Волк Севера', 'hp': FOREST_WHITE_WOLF_HP, 'dmg_min': FOREST_WHITE_WOLF_DMG[0], 'dmg_max': FOREST_WHITE_WOLF_DMG[1], 'dodge': FOREST_WHITE_WOLF…` |  | :850 |
| `FOREST_BERRY_BLUEBERRY` | `'Горсть черники'` |  | :878 |
| `FOREST_BERRY_RASPBERRY` | `'Горсть малины'` |  | :879 |
| `FOREST_BERRY_STRAWBERRY` | `'Горсть земляники'` |  | :880 |
| `FOREST_BEAR_SKIN_NAME` | `'Шкура медведя'` |  | :881 |
| `FOREST_BERRY_TABLE` | `{'glade': ((FOREST_BERRY_BLUEBERRY, 50),), 'clearing': ((FOREST_BERRY_BLUEBERRY, 40), (FOREST_BERRY_RASPBERRY, 25), (FOREST_BERRY_STRAWBERRY, 20), ('bear', 5), (FIRE_BERRY_NAME, 10))}` |  | :884 |
| `FOREST_BEAR_SEED` | `{'key': 'bear', 'spot': 'forest', 'name': 'Медведь', 'hp': round(FOREST_BOAR_HP * 1.5), 'dmg_min': round(FOREST_BOAR_DMG[0] * 1.5), 'dmg_max': round(FOREST_BOAR_DMG[1] * 1.5), 'dodge': FOREST_BOAR_…` |  | :891 |
| `CLAN_CAPE_NAME` | `'Клановая накидка'` |  | :913 |
| `CLAN_CAPE_DODGE` | `2` | +% уклонения, пока накидка надета | :914 |
| `MOLLUSK_SEED` | `{'key': 'mollusk', 'spot': 'reservoir', 'name': 'Мутировавший моллюск', 'hp': 24, 'dmg_min': 5, 'dmg_max': 9, 'dodge': 20, 'loss_ap': 12, 'chance': 4, 'pity_target': 0, 'reward_nm': 0, 'photo_key':…` |  | :917 |
| `MOLLUSK_ITEM_SEEDS` | `[('Мясо моллюска', 'Плотное мясо мутировавшего моллюска. В сыром виде есть нельзя — прожарь на кухне.', 120, 60, 2, 'resource', 0), ('Жемчужина', 'Редчайшая жемчужина из раковины мутировавшего молл…` |  | :940 |
| `MOLLUSK_ENEMY_DROPS` | `('Мясо моллюска', 'Жемчужина')` |  | :955 |
| `MINE_AP_COST` | `12` | стоимость одной попытки добычи | :964 |
| `MINE_BASE_CHANCE` | `30` | базовый шанс успеха без бонуса кирки | :965 |
| `MINE_PICKAXE_BONUS_PER_RANK` | `15` | надбавка к шансу за ступень кирки (ранг 1 → +15%) | :966 |
| `MINE_CHANCE_CAP` | `90` | потолок шанса успеха | :967 |
| `MINE_RESULT_DELAY` | `(7, 15)` | результат добычи через 7–15 секунд | :968 |
| `MINE_REQUIRED_STATUS` | `'pilot1'` | вход в копь — с «Пилота 1 класса» | :969 |
| `MINE_GEM_CAP` | `1` | из самоцветов за бой выпадает не больше одного | :970 |
| `MINE_PICKAXE_NAME` | `'Кирка'` |  | :971 |
| `MINE_ORE_NAME` | `'Железная руда'` |  | :972 |
| `MINE_BAT_KEY` | `'bat'` |  | :975 |
| `MINE_BAT_SPOT` | `'iron'` |  | :976 |
| `MINE_BAT_CHANCE` | `7.0` |  | :977 |
| `MINE_BAT_PITY_TARGET` | `12` |  | :978 |
| `MINE_BAT_SEED` | `{'key': MINE_BAT_KEY, 'spot': MINE_BAT_SPOT, 'name': 'Летучая мышь', 'hp': 22, 'dmg_min': 3, 'dmg_max': 7, 'dodge': 35, 'loss_ap': 15, 'chance': MINE_BAT_CHANCE, 'pity_target': MINE_BAT_PITY_TARGET…` |  | :983 |
| `MINE_ITEM_SEEDS` | `[(MINE_PICKAXE_NAME, 'Простая кирка шахтёра: без неё в штольню не сунешься, а с ней порода поддаётся легче. Повышает шанс успешной добычи руды.', 300, 150, 1, 'mining', 0), (MINE_ORE_NAME, 'Кусок ж…` |  | :1009 |
| `MINE_SHOP_ITEMS` | `(MINE_PICKAXE_NAME,)` |  | :1030 |
| `MINE_ENEMY_DROPS` | `('Изумруд', 'Рубин', 'Сапфир')` |  | :1033 |
| `ON_HIT_EFFECTS` | `{'bleed': {'emoji': '🩸', 'title': 'Кровотечение', 'until_battle_end': True, 'params': (('chance', 'Шанс наложить, %', 'percent'), ('dmg', 'Урон, HP за ход', 'int')), 'hint': 'Раны сочатся кровью ка…` |  | :1042 |
| `ON_HIT_KIND_ORDER` | `('bleed', 'poison', 'frostbite', 'state', 'lifesteal', 'armor_pierce')` |  | :1106 |
| `ON_HIT_STATE_ROUNDS` | `{'оглушён': 3, 'ослеплён': 4}` |  | :1108 |
| `CLAN_ROLES` | `{'leader': '👑 Глава клана', 'seneschal': '🛡 Сенешаль клана', 'banner': '🚩 Знаменосец клана', 'elder': '⭐ Старшина', 'member': '▪️ Пилот клана'}` |  | :1114 |
| `CLAN_ROLE_ORDER` | `('leader', 'seneschal', 'banner', 'elder', 'member')` |  | :1121 |
| `LOGGING_AP_COST` | `12` | стоимость одной попытки рубки | :1127 |
| `LOGGING_BASE_CHANCE` | `35` | базовый шанс успеха без бонуса топора | :1128 |
| `LOGGING_AXE_BONUS_PER_RANK` | `15` | надбавка к шансу за ступень топора | :1129 |
| `LOGGING_CHANCE_CAP` | `90` | потолок шанса успеха | :1130 |
| `LOGGING_AXE_SLIP_CHANCE` | `2.5` | шанс, что топор отскочит пилоту в плечо, % | :1131 |
| `LOGGING_RESULT_DELAY` | `(7, 15)` | результат рубки через 7–15 секунд | :1132 |
| `LOGGING_AXE_NAME` | `'Топор'` |  | :1133 |
| `LOGGING_WOOD_NAME` | `'Бревна'` |  | :1134 |
| `LOGGING_PLANK_NAME` | `'Доска'` |  | :1140 |
| `LOGGING_FIREWOOD_NAME` | `'Пак дров'` |  | :1141 |
| `LOGGING_PLANK_YIELD` | `3` | досок из одного бревна | :1142 |
| `LOGGING_PLANK_FEE` | `15` | НМ за распил одного бревна (в казну) | :1143 |
| `LOGGING_FIREWOOD_YIELD` | `3` | паков дров из одного бревна | :1144 |
| `LOGGING_FIREWOOD_AP_COST` | `4` | ОД за рубку дров из одного бревна | :1145 |
| `LOGGING_SNAKE_KEY` | `'snake'` |  | :1149 |
| `LOGGING_OWL_KEY` | `'owl'` |  | :1150 |
| `LOGGING_SPOT` | `'logging'` |  | :1151 |
| `LOGGING_SNAKE_CHANCE` | `8.0` |  | :1152 |
| `LOGGING_SNAKE_PITY_TARGET` | `10` |  | :1153 |
| `LOGGING_OWL_CHANCE` | `3.0` |  | :1154 |
| `LOGGING_OWL_PITY_TARGET` | `24` |  | :1155 |
| `LOGGING_SNAKE_POISON_CHANCE` | `30` |  | :1157 |
| `LOGGING_SNAKE_POISON_DMG` | `2` |  | :1158 |
| `LOGGING_OWL_FLEE_HP` | `20` |  | :1162 |
| `LOGGING_OWL_BLIND_CHANCE` | `30` |  | :1163 |
| `LOGGING_OWL_BLIND_ROUNDS` | `4` |  | :1164 |
| `LOGGING_SNAKE_SEED` | `{'key': LOGGING_SNAKE_KEY, 'spot': LOGGING_SPOT, 'name': 'Лесная змея', 'hp': 30, 'dmg_min': 4, 'dmg_max': 8, 'dodge': 25, 'loss_ap': 10, 'chance': LOGGING_SNAKE_CHANCE, 'pity_target': LOGGING_SNAK…` |  | :1168 |
| `LOGGING_OWL_SEED` | `{'key': LOGGING_OWL_KEY, 'spot': LOGGING_SPOT, 'name': 'Неясыть', 'hp': 90, 'dmg_min': 7, 'dmg_max': 12, 'dodge': 30, 'loss_ap': 15, 'chance': LOGGING_OWL_CHANCE, 'pity_target': LOGGING_OWL_PITY_TA…` |  | :1198 |
| `LOGGING_ITEM_SEEDS` | `[(LOGGING_AXE_NAME, 'Крепкий лесорубский топор: без него к срубам не подпустят. Повышает шанс успешной рубки деревьев.', 300, 150, 1, 'mining', 0), (LOGGING_WOOD_NAME, 'Свежие срубленные брёвна из …` |  | :1230 |
| `LOGGING_SHOP_ITEMS` | `(LOGGING_AXE_NAME,)` |  | :1264 |
| `LOGGING_ENEMY_DROPS` | `('Змеиная кожа', 'Змеиный яд', 'Совиное перо')` |  | :1267 |
| `LOGGING_MARKET_RESOURCES` | `(LOGGING_PLANK_NAME, LOGGING_FIREWOOD_NAME)` |  | :1270 |
| `REPORT_DAILY_LIMIT` | `3` |  | :1272 |
| `REPORT_AUTO_APPROVE_TROOPS` | `100` |  | :1273 |
| `NEWS_PUBLISH_BONUS` | `10` |  | :1277 |
| `NEWS_PUBLISH_CAP` | `28` |  | :1278 |
| `ROLE_SALARY_PAY_DAY` | `28` |  | :1281 |
| `REPORT_DAILY_PAY_CAP` | `4000` |  | :1286 |
| `REPORT_MAX_TROOPS` | `1000000` |  | :1287 |
| `REPORT_MAX_REGION` | `38` | 0 = Столица, 1..38 регионы | :1288 |
| `WALL_TEXT_MAX_LEN` | `40` | лимит символов на одно изречение | :1291 |
| `WALL_FREE_PER_DAY` | `2` | бесплатных сообщений в сутки | :1292 |
| `WALL_PAID_STEPS` | `[(3, 30), (3, 90), (3, 200)]` | далее платные ступени: (кол-во, цена НМ) | :1293 |
| `WALL_REVIEW_TOTAL` | `11` | максимум сообщений в сутки (2 + 3+3+3) | :1298 |
| `WALL_PAGE_SIZE` | `5` | постов на страницу стены | :1299 |
| `WALL_ARCHIVE_PAGE_SIZE` | `8` | записей архива стены на страницу списка | :1300 |
| `REPORT_ARCHIVE_PAGE` | `8` | отчётов на страницу архива МВД и в «Моих отчётах» | :1303 |
| `POLL_MAX_DAYS` | `10` | максимум дней, сколько живёт опрос. Не закрыл | :1306 |
| `POLL_VISIBLE` | `4` | сколько новейших опросов висит в меню голосования. | :1309 |
| `POLL_ARCHIVE_DAYS_PER_PAGE` | `5` | дней (дат) архива опросов на страницу списка | :1312 |
| `POLL_ARCHIVE_PER_DAY` | `6` | опросов под одним заголовком-днём | :1313 |
| `REP_SPEECH_MAX_LEN` | `100` | лимит символов одного обращения | :1316 |
| `REP_SPEECH_PER_DAY` | `2` | обращений в сутки от представителя | :1317 |
| `AUTO_PROMOTE_MAX_TROOPS` | `4040` |  | :1322 |

## Буклет туриста

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `TOURIST_BOOKLET_NAME` | `'Буклет туриста'` |  | :21 |

## Древо Пламенного Круговорота (клановое расширение 'tree')

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `FIRE_TREE_CLAN_REQ_LAMPS` | `5` | сколько чланов с Лампой нужно для получения Древа | :415 |

## Суточный цикл Нордхайма

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `REPORT_DAY_START_HOUR` | `10` |  | :462 |

## Дом Дуэлей (PvP-арена)

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `DUEL_ZONES` | `('head', 'body', 'hands', 'legs')` |  | :559 |

## Рынок: слоты продажи

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `MARKET_BASE_SLOTS` | `1` | слоты без лицензии | :637 |

## Налог на недвижимость (НМ/мес)

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `HOUSING_TAX` | `{'municipal': 0, 'studio': 20, 'apartment': 35, 'improved': 60, 'mansion': 100}` |  | :643 |

## Банк: лимит счёта туриста (НМ)

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `TOURIST_BALANCE_LIMIT` | `200` |  | :653 |

## Данж: лимит хила (количество применений за забег)

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `DUNGEON_HEAL_SOFT_LIMIT` | `6` | после этого — ×2/3 | :656 |

## Сброс протухших забегов подземелья

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `DUNGEON_RUN_STALE_SEC` | `3600` |  | :665 |

## Данж: побег и дымовая шашка

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `ESCAPE_BASE_CHANCE` | `25` |  | :673 |

