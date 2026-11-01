# Справочник констант `config.py`

> **Сгенерировано** `tools/export_config.py`. Перегенерация:
> `.venv\Scripts\python.exe tools/export_config.py`.
>
> Все модульные константы `config.py`, сгруппированные по секциям
> (комментариям-разделителям `# ── … ──`). Длинные значения усечены `…`;
> точное значение — в `config.py` по строке из первой колонки.

Всего констант: **339**; разделов: **11**.

## Без раздела

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `VERSION` | `'0.41.18'` |  | :16 |
| `VERSION_NOTES` | `'Праздничные хлопоты: вход в Лабиринт идёт в казну, КВП теперь 5 попыток.'` |  | :17 |
| `PREV_VERSION` | `'0.41.17'` |  | :19 |
| `PREV_VERSION_NOTES` | `'Праздничные хлопоты: подготовка праздничной лавки.'` |  | :20 |
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
| `FIRE_LAB_PIE_NAME` | `'Кусочек тыквенного пирога'` |  | :70 |
| `FIRE_LAB_CANDY_NAME` | `'Леденец языков пламени'` |  | :71 |
| `FIRE_LAB_HAY_NAME` | `'Пучок сена'` |  | :72 |
| `FIRE_LAB_BRANCH_NAME` | `'Ветка дерева'` |  | :73 |
| `FIRE_LAB_RECIPE_NAME` | `'Рецепт: Тыквенный пирог'` |  | :74 |
| `FIRE_PUMPKIN_SEED_NAME` | `'Семечко тыквы'` | посадка в кадку / клан. сад | :75 |
| `FIRE_CROW_FEATHER_NAME` | `'Перо ворона'` | ресурс (дроп стража? — Ф5) | :76 |
| `FIRE_WIRE_NAME` | `'Моток железной проволоки'` | ингредиент трости | :77 |
| `FIRE_EGGS_NAME` | `'Яйца'` | ингредиент пирога (x2) | :78 |
| `FIRE_CROWN_NAME` | `'Огненный венец'` | голова: броня 2, лечение +25% | :79 |
| `FIRE_CLOAK_NAME` | `'Плащ Памяти'` | тело: броня 2, уклон +5% | :80 |
| `FIRE_GLOVES_NAME` | `'Перчатки стража посевов'` | руки: броня 2, уклон +3% | :81 |
| `FIRE_KEYS_NAME` | `'Вилы'` | оружие: +2 к удару, кровотечение | :82 |
| `FIRE_FLAME_DEVICE_NAME` | `'Ручное пламенеющее устройство'` | ингредиент трости | :83 |
| `FIRELAB_SCARECROW_SEED` | `{'key': 'scarecrow', 'spot': 'firelab', 'name': 'Пугало', 'hp': FIRELAB_SCARECROW_HP, 'dmg_min': FIRELAB_SCARECROW_DMG[0], 'dmg_max': FIRELAB_SCARECROW_DMG[1], 'dodge': FIRELAB_SCARECROW_DODGE, 'ar…` |  | :85 |
| `FIRELAB_APPLE_CHILD_SEED` | `{'key': 'apple_child', 'spot': 'firelab', 'name': 'Дитя Яблони', 'hp': FIRELAB_APPLE_CHILD_HP, 'dmg_min': FIRELAB_APPLE_CHILD_DMG[0], 'dmg_max': FIRELAB_APPLE_CHILD_DMG[1], 'dodge': FIRELAB_APPLE_C…` |  | :112 |
| `FIRELAB_CROW_SEED` | `{'key': 'crow', 'spot': 'firelab', 'name': 'Ворон', 'hp': FIRELAB_CROW_HP, 'dmg_min': FIRELAB_CROW_DMG[0], 'dmg_max': FIRELAB_CROW_DMG[1], 'dodge': FIRELAB_CROW_DODGE, 'loss_ap': 0, 'chance': 0, 'p…` |  | :139 |
| `FIRELAB_HUB_SEED` | `{'key': 'hub', 'spot': 'firelab', 'name': 'Хуб', 'hp': FIRELAB_HUB_HP, 'dmg_min': FIRELAB_HUB_DMG[0], 'dmg_max': FIRELAB_HUB_DMG[1], 'dodge': FIRELAB_HUB_DODGE, 'loss_ap': 0, 'chance': 0, 'pity_tar…` |  | :164 |
| `FIRELAB_PUMPKIN_SEED` | `{'key': 'pumpkin_boss', 'spot': 'firelab', 'name': 'Мощный Мистер Огненная Тыква', 'hp': FIRELAB_PUMPKIN_HP, 'dmg_min': FIRELAB_PUMPKIN_DMG[0], 'dmg_max': FIRELAB_PUMPKIN_DMG[1], 'dodge': FIRELAB_P…` |  | :191 |
| `FIRELAB_ENEMY_SEEDS` | `(FIRELAB_SCARECROW_SEED, FIRELAB_APPLE_CHILD_SEED, FIRELAB_CROW_SEED, FIRELAB_HUB_SEED, FIRELAB_PUMPKIN_SEED)` |  | :221 |
| `FIRE_EVENT_ENABLED` | `True` |  | :229 |
| `FIRE_EVENT_START` | `(2026, 10, 30, 0, 0)` | МСК, ночь на пятницу 30.10 | :230 |
| `FIRE_EVENT_DURATION_DAYS` | `5` | до ~00:00 МСК 4.11 | :231 |
| `FIRE_LAB_ENABLED` | `True` |  | :233 |
| `FIRE_EVENT_LAB_FEE` | `32` | вход в лабиринт, НМ | :234 |
| `FIRE_EVENT_MAX_ENTRIES_DAY` | `4` | максимум заходов за сутки | :235 |
| `FIRE_LAB_SESSION_TTL_SEC` | `3600` | неактивность: сессия закрывается автоматически (1 ч) | :236 |
| `FIRE_LAB_FORK_KEY` | `'city/fire_maze'` | развилка (вход/смерть/уход/финиш) | :239 |
| `FIRE_LAB_WELL_KEY` | `'city/fire_well'` | Колодец | :240 |
| `FIRE_LAB_TREE_KEY` | `'city/fire_tree'` | Древо Огня | :241 |
| `FIRE_LAB_SCARECROW_BLIND_P` | `0.15` | Пугало: «сено в лицо» — ослепление | :246 |
| `FIRE_LAB_APPLE_STUN_P` | `0.1` | Дитя Яблони: «яблочко» — оглушение | :247 |
| `FIRE_LAB_CROW_BLIND_P` | `0.15` | Ворон: ослепление (как сова) | :248 |
| `FIRE_LAB_HUB_SLOW_P` | `0.25` |  | :249 |
| `FIRE_LAB_HUB_SLOW_ROUNDS` | `3` |  | :250 |
| `FIRE_LAB_HUB_PLAYER_DODGE_PENALTY` | `35` |  | :251 |
| `FIRE_LAB_HUB_ENEMY_DODGE_BONUS` | `10` |  | :252 |
| `FIRE_LAB_BOSS_BURN_P` | `0.25` | Босс «Мистер Тыква»: поджиг игрока | :253 |
| `FIRE_LAB_BOSS_BURN_DMG` | `2` | −HP/ход | :254 |
| `FIRE_LAB_BOSS_BURN_ROUNDS` | `3` |  | :255 |
| `FIRE_LAB_BOSS_MAX` | `2` | максимум встреч с боссом за заход | :256 |
| `FIRE_LAB_ROOMS_MAX` | `25` | после 25 комнат-развилок выход автоматом | :257 |
| `FIRE_LAB_TIER_MAX` | `10` | кап усилений | :260 |
| `FIRE_LAB_TIER_HP_STEP` | `2` | +HP всем врагам за тир (1–4) | :261 |
| `FIRE_LAB_TIER_HP_LAST` | `8` | 5-й тир: разово +8 (итого +16) | :262 |
| `FIRE_LAB_TIER_HP_STEP_MID` | `4` | +HP всем врагам за тир (6–9) | :263 |
| `FIRE_LAB_TIER_HP_10` | `16` | 10-й тир: разово +16 | :264 |
| `FIRE_LAB_TIER_LOOT_STEP` | `0.02` | лут ×(1+2%) за тир (1–4, 6–9) | :265 |
| `FIRE_LAB_TIER_LOOT_LAST` | `0.1` | 5-й и 10-й тиры: ×(1+10%) | :266 |
| `FIRE_LAB_P_WELL` | `0.07` | Колодец (перебивается паттерном ЛЛПП) | :269 |
| `FIRE_LAB_WELL_MAX` | `3` | максимум посещений за заход | :270 |
| `FIRE_LAB_P_TREE` | `0.09` | Древо Огня (перебивается ЛЛППНН) | :271 |
| `FIRE_LAB_TREE_MAX` | `1` | раз за заход | :272 |
| `FIRE_TREE_DMG_BONUS_PCT` | `15` | +15% урона | :276 |
| `FIRE_TREE_REGEN_HP` | `1` | +1 HP после каждого удара игрока | :277 |
| `FIRE_LAB_PATTERN_WELL` | `('L', 'L', 'S', 'S')` | ЛЛПП → Колодец (до 3) | :281 |
| `FIRE_LAB_PATTERN_TREE` | `('L', 'L', 'S', 'S', 'R', 'R')` | ЛЛППНН → Древо Огня (1) | :282 |
| `FIRE_LAB_WELL_FISH_TRIES` | `6` | попыток рыбалки за один визит в Колодец | :285 |
| `FIRE_LAB_WELL_HEAL` | `50` | колодец: фиксированное лечение за визит, HP | :286 |
| `FIRE_LAB_WELL_AP` | `10` | колодец: восстановление ОД за визит (не выше максимума) | :287 |
| `FIRE_SET_REGEN_HP` | `1` | сет праздничной одежды+оружия: регенерация за ход в Лабиринте | :288 |
| `FIRE_EXCHANGE_ENABLED` | `False` |  | :291 |
| `FIRE_EXCHANGE_OFFERS` | `((FIRE_LAB_HAY_NAME, 3, FIRE_LAB_CANDY_NAME, 1), (FIRE_LAB_BRANCH_NAME, 3, FIRE_LAB_PIE_NAME, 1))` |  | :292 |
| `FIRE_LAB_FISH_DELAY` | `(7, 15)` | колодец: поклёвка через N секунд (как на озере) | :297 |
| `FIRE_LAB_NOBAIT_FIND_P` | `0.12` | колодец без наживки: шанс поднять что-то со дна (%/100) | :298 |
| `FIRE_LAB_NOBAIT_FIND` | `((FIRE_WIRE_NAME, 35), (FIRE_LAB_HAY_NAME, 65))` | что поднимается без наживки (вес) | :299 |
| `FIRE_LAB_FISH_OSETR_NAME` | `'Спектральная Латимерия'` | рыба 1 (rarity 2) | :304 |
| `FIRE_LAB_FISH_SOUL_NAME` | `'Скелетная Арована'` | рыба 2 (rarity 3) | :305 |
| `FIRE_LAB_FISH_CARP_NAME` | `'Пылающая Душа'` | рыба 3 (rarity 4, редкая) | :306 |
| `FIRE_LAB_FISH_TABLE` | `((FIRE_LAB_FISH_OSETR_NAME, 60), (FIRE_LAB_FISH_SOUL_NAME, 25), (FIRE_LAB_FISH_CARP_NAME, 15))` | взвешенный выбор улова | :307 |
| `FIRE_FISHER_ACH_KEY` | `'fire_fisher'` |  | :313 |
| `FIRE_FISHER_THRESHOLD` | `3` |  | :314 |
| `FIRE_FISHER_REWARD_NM` | `150` |  | :315 |
| `FIRE_LAB_PIE_HEAL` | `15` |  | :317 |
| `FIRE_LAB_CANDY_HEAL` | `12` |  | :318 |
| `FIRE_PUMPKIN_NAME` | `'Тыква'` | плод; ингредиент пирога | :322 |
| `FIRE_SUGAR_NAME` | `'Сахар'` | ингредиент пирога | :323 |
| `FIRE_KEYS_DMG` | `2` |  | :324 |
| `FIRE_KEYS_BLEED_P` | `10` |  | :325 |
| `FIRE_KEYS_BLEED_DMG` | `2` |  | :326 |
| `FIRE_CROWN_HEAL_BONUS_PCT` | `25` |  | :327 |
| `FIRE_CLOAK_DODGE` | `5` |  | :328 |
| `FIRE_GLOVES_DODGE` | `3` |  | :329 |
| `FIRE_CANE_NAME` | `'Обжигающая трость'` | оружие: удар 3, поджог 20% | :330 |
| `FIRE_CANE_DMG` | `3` |  | :331 |
| `FIRE_CANE_BURN_P` | `20` |  | :332 |
| `FIRE_CANE_BURN_DMG` | `2` |  | :333 |
| `FIRE_CANE_BURN_ROUNDS` | `3` |  | :334 |
| `FIRE_LANTERN_NAME` | `'Лампа Круговорота'` | награда за «Чтящего Предков» (Ф4б) | :335 |
| `FIRE_AMBER_NAME` | `'Пламя Памяти'` | янтарь из Лампы (Ф4б), продам 100 НМ | :336 |
| `FIRE_LANTERN_MEDIT_AP` | `20` | 🪔 медитация раз в сутки | :337 |
| `FIRE_LANTERN_AMBER_DAYS` | `7` | янтарь раз в N суток | :338 |
| `FIRE_PREDKI_NAME` | `'Предания предков'` |  | :341 |
| `FIRE_PREDKI_HEAL` | `60` | +60 HP в бою | :342 |
| `FIRE_PREDKI_REGEN` | `50` | регенерация: 50% от лечения | :343 |
| `FIRE_PREDKI_REGEN_TURNS` | `4` | разлитая на 4 хода (нестандарт!) | :344 |
| `FIRE_PREDKI_DODGE_PCT` | `5` | суточный баф: уворот +5% | :345 |
| `FIRE_PREDKI_DODGE_HOURS` | `24` | длительность бафа (не продлевается) | :346 |
| `CLAN_BUILDING_TYPES` | `{'house': {'name': 'Дом Клана', 'slots': 2, 'max_level': 2, 'days': 2, 'price_nm': 3000, 'required': {'Доска': 60, 'Бревна': 20, 'Железная руда': 15}}, 'manor': {'name': 'Клановое поместье', 'slots…` |  | :348 |
| `CLAN_BUILDING_NO_RESOURCES_MULT` | `2` |  | :363 |
| `CLAN_EXPANSION_TYPES` | `('kitchen', 'workbench', 'shower', 'garden', 'library', 'shop', 'tree')` |  | :365 |
| `CLAN_EXPANSION_INFO` | `{'kitchen': {'name': 'Кухня', 'icon': '🍳', 'desc': 'Готовка по выученным рецептам; уровень задаёт доступные блюда.'}, 'workbench': {'name': 'Крафтовый стол', 'icon': '🛠', 'desc': 'Крафт снаряжения …` |  | :367 |
| `FIRE_TREE_CLAN_MEDIT_AP` | `20` | 🧘 медитация у Древа (в доп. к домашней) | :389 |
| `FIRE_TREE_CLAN_ESSENCE_NAME` | `'Эссенция Памяти'` |  | :390 |
| `FIRE_TREE_CLAN_ESSENCE_DAYS` | `30` | раз в 30 дней (от установки/сбора) | :391 |
| `FIRE_TREE_CLAN_ESSENCE_SELL` | `500` | продажа кристалла на скупке | :392 |
| `CLAN_EXPANSION_UPGRADE` | `{2: {'nm': 1500, 'required': {'Доска': 20, 'Железная руда': 10}}, 3: {'nm': 4000, 'required': {'Доска': 50, 'Железная руда': 30}}, 4: {'nm': 9000, 'required': {'Доска': 100, 'Железная руда': 60}}}` |  | :394 |
| `CLAN_SHOWER_AP_BY_LEVEL` | `{1: 25, 2: 50, 3: 75, 4: 100}` |  | :402 |
| `CLAN_SHOWER_SOBER_MINUTES` | `{1: 60, 2: 120, 3: 180, 4: 240}` |  | :403 |
| `CLAN_GARDEN_PLOTS` | `{1: 2, 2: 3, 3: 4, 4: 6}` |  | :405 |
| `CLAN_SHOP_DAILY_LIMIT` | `3` |  | :406 |
| `CLAN_SHOP_DISCOUNT` | `10` |  | :407 |
| `BOT_TOKEN` | `os.getenv('BOT_TOKEN')` |  | :409 |
| `ADMIN_IDS` | `[int(x) for x in os.getenv('ADMIN_IDS', '').split(',') if x.strip()]` |  | :410 |
| `_news_raw` | `os.getenv('NEWS_CHAT_ID', '').strip()` |  | :413 |
| `NEWS_CHAT_ID` | `int(_news_raw) if _news_raw.lstrip('-').isdigit() else None` |  | :414 |
| `DB_PATH` | `os.getenv('DATABASE_PATH', 'database/nordmark.db')` |  | :417 |
| `FSM_STORAGE_PATH` | `os.getenv('FSM_STORAGE_PATH', '').strip() or os.path.join(os.path.dirname(os.path.abspath(DB_PATH)), 'fsm')` |  | :426 |
| `REPORT_DAY_START_MINUTE` | `0` |  | :436 |
| `RANKS` | `[('Рекрут', 0), ('Рядовой', 100), ('Ефрейтор', 350), ('Капрал', 500), ('Сержант', 850), ('Старший Сержант', 1500), ('Лейтенант', 2500), ('Старший Лейтенант', 4040), ('Капитан', 6000), ('Майор', 850…` |  | :438 |
| `MAX_SELF_RANK_TROOPS` | `4040` |  | :459 |
| `AUTO_RANK_NAMES` | `('Рекрут', 'Рядовой', 'Ефрейтор', 'Капрал', 'Сержант', 'Старший Сержант', 'Лейтенант', 'Старший Лейтенант')` |  | :462 |
| `AWARD_MAX_SHOP_DISCOUNT` | `40` |  | :469 |
| `AWARD_MIN_REPORT_TAX` | `5` |  | :470 |
| `RANK_STATUS_TAGS` | `{'Ефрейтор': 'pilot2', 'Старший Сержант': 'pilot1', 'Старший Лейтенант': 'veteran', 'Майор': 'master_pilot', 'Полковник': 'ace'}` |  | :472 |
| `LEGIONER_ACCESS_CAP_ORDER` | `5` |  | :485 |
| `RANK_DAMAGE_TIERS` | `{'ace': (4, 8), 'master_pilot': (3, 5), 'veteran': (2, 4), 'pilot1': (1, 3), 'pilot2': (1, 2), 'recruit': (1, 1), 'tourist': (0, 1)}` |  | :491 |
| `RANK_CRIT_CHANCE` | `{'ace': 7.5, 'master_pilot': 6.0, 'veteran': 4.5, 'pilot1': 3.0, 'pilot2': 1.5, 'recruit': 0.0, 'tourist': 0.0}` |  | :509 |
| `PILOT_CRIT_MULT` | `1.4` |  | :523 |
| `PILOT_NO_WEAPON_DMG` | `(1, 1)` |  | :526 |
| `DUEL_ZONE_LABELS` | `{'head': 'Голова', 'body': 'Тело', 'hands': 'Руки', 'legs': 'Ноги'}` |  | :533 |
| `DUEL_ZONE_EMOJI` | `{'head': '🧠', 'body': '🫀', 'hands': '✊', 'legs': '🦵'}` |  | :539 |
| `DUEL_AP_COST` | `15` | списывается с обоих при старте боя | :545 |
| `DUEL_RATING_WIN` | `2` | рейтинг за победу | :546 |
| `DUEL_RATING_LOSS` | `-3` | рейтинг за поражение | :547 |
| `DUEL_RATING_DRAW` | `0` | рейтинг за ничью | :548 |
| `DUEL_RATING_FORFEIT` | `-1` | рейтинг тому, кто покинул бой («Покинуть дуэль») | :549 |
| `DUEL_RATING_FORFEIT_WIN` | `1` | рейтинг сопернику, если противник покинул бой (меньше чистой победы) | :550 |
| `DUEL_MIN_DAMAGE` | `1` | минимум урона за попавший (не уклонённый) удар | :551 |
| `DUEL_GUARD_REDUCTION` | `0.5` | доля урона, остающаяся при угаданной зоне защиты | :552 |
| `DUEL_HEAL_BETWEEN` | `0` | восстановление HP между раундами (пока нет) | :553 |
| `DUEL_CHALLENGE_TIMEOUT_SEC` | `120` | сколько живёт неотвеченный вызов | :554 |
| `DUEL_STALE_SEC` | `1800` | зависшая дуэль авто-завершается как void | :555 |
| `DUEL_GLOVES_NAME` | `'Дуэльные перчатки'` |  | :556 |
| `DUEL_GLOVES_DAMAGE` | `7` |  | :557 |
| `DUEL_GLOVES_PRICE` | `200` |  | :558 |
| `DUEL_GLOVES_SELL` | `100` |  | :559 |
| `DUEL_CLUB_CARD_NAME` | `'Клубная карта «Дом Дуэлей»'` |  | :560 |
| `DUEL_CLUB_CARD_PRICE` | `150` |  | :561 |
| `DUEL_CLUB_CARD_SELL` | `75` |  | :562 |
| `DUEL_CLUB_CARD_DAYS` | `30` |  | :563 |
| `DUEL_ACCESS_TAG` | `'pilot2'` |  | :566 |
| `RARITY_LEVELS` | `{1: 'Обычный', 2: 'Качественный', 3: 'Редкий', 4: 'Шедевр', 5: 'Легендарный'}` |  | :568 |
| `RARITY_EMOJI` | `{1: '⬜', 2: '🟩', 3: '🟦', 4: '🟪', 5: '🟧'}` |  | :576 |
| `ITEM_CATEGORIES` | `{'weapon': 'Оружие', 'consumable': 'Расходники', 'building': 'Недвижимость', 'housing': 'Жильё', 'furniture': 'Мебель и расширения', 'seeds': 'Семена', 'equipment': 'Одежда', 'resource': 'Ресурсы',…` |  | :584 |
| `MARKET_LICENSE_SLOTS` | `2` | доп. слоты при активной лицензии | :608 |
| `MARKET_LICENSE_DAYS` | `30` | срок действия лицензии (дней) | :609 |
| `MARKET_LICENSE_PRICE` | `500` | цена лицензии в НМ | :610 |
| `DUNGEON_HEAL_HARD_LIMIT` | `10` | после этого — ×1/2 | :627 |
| `DUNGEON_HEAL_SOFT_MULT` | `2 / 3` |  | :628 |
| `DUNGEON_HEAL_HARD_MULT` | `1 / 2` |  | :629 |
| `ESCAPE_HP_BONUS` | `20` |  | :644 |
| `DUNGEON_SMOKE_ESCAPE` | `95` |  | :645 |
| `DUNGEON_SMOKE_MAX` | `2` |  | :646 |
| `DUNGEON_ESCAPE_DRUNK_MULT` | `0.5` |  | :649 |
| `AP_MAX` | `150` |  | :651 |
| `AP_DAILY_RECOVERY` | `100` |  | :652 |
| `AP_BONUS_FROM_CONSUMABLE` | `50` |  | :653 |
| `AP_DAILY_RESTORE_LIMIT` | `150` |  | :658 |
| `AP_EXHAUSTED_MINUTES` | `2880` | 2 суток | :659 |
| `AP_EXHAUSTED_DAILY_RECOVERY` | `75` | суточное восстановление в «истощении» | :660 |
| `AP_EXHAUSTED_MAX_AP` | `90` | максимум ОД в «истощении» | :661 |
| `SEAWEED_DAILY_LIMIT` | `6` |  | :664 |
| `DIGESTIVE_UPSET_MINUTES` | `1440` | 24 часа | :665 |
| `ALCOHOL_WEAK_DRUNK_LIMIT` | `3` |  | :670 |
| `ALCOHOL_WEAK_VERY_DRUNK_LIMIT` | `6` |  | :671 |
| `ALCOHOL_STRONG_DRUNK_LIMIT` | `1` |  | :673 |
| `ALCOHOL_STRONG_VERY_DRUNK_LIMIT` | `2` |  | :674 |
| `DRUNK_MINUTES` | `60` |  | :675 |
| `VERY_DRUNK_MINUTES` | `360` | 6 часов | :676 |
| `DRINK_EFFECT_LABELS` | `{'alcohol_weak': '🍺 Слабоалкогольный: 3 шт/сутки — «пьян», 6 — «очень пьян»', 'alcohol_strong': '🥃 Крепкий алкоголь: 1 шт — «пьян», 2 — «очень пьян»', 'indigestion': '🤢 Вызывает «несварение» на сут…` |  | :679 |
| `SPECIAL_DEPT_CODE_MIN_LEN` | `4` |  | :690 |
| `SPECIAL_DEPT_CODE_MAX_LEN` | `8` |  | :691 |
| `SPECIAL_DEPT_ATTEMPTS_LIMIT` | `3` | ошибок кода подряд | :692 |
| `SPECIAL_DEPT_BLOCK_MINUTES` | `1440` | бан на 24 часа после 3 ошибок | :693 |
| `FISH_AP_COST` | `3` | стоимость одного заброса удочки | :696 |
| `RESERVOIR_AP_COST` | `5` |  | :701 |
| `FISH_WEIGHTS` | `[{'key': 'small', 'label': 'Мелкая', 'mult': 1.0, 'chance': 40}, {'key': 'medium', 'label': 'Средняя', 'mult': 1.15, 'chance': 40}, {'key': 'large', 'label': 'Большая', 'mult': 1.25, 'chance': 20}]` |  | :706 |
| `FISH_TREASURY_SALE_MULT` | `0.5` |  | :714 |
| `FISH_TREASURY_DAILY_LIMIT` | `300` |  | :719 |
| `FOREST_AP_COST` | `4` | запасной цена поиска, если у зоны нет ap_cost в БД | :722 |
| `FOREST_RESULT_DELAY` | `(5, 10)` | результат поиска через 5–10 секунд | :725 |
| `FOREST_SOLD_DAILY_LIMIT` | `250` |  | :730 |
| `FOREST_ALLOW_TOURISTS` | `False` |  | :735 |
| `FOREST_BOAR_PITY_TARGET` | `12` |  | :738 |
| `FOREST_BOAR_CHANCE` | `4.0` |  | :742 |
| `CALLSIGN_PRICE` | `500` |  | :744 |
| `PILOT_BASE_HP` | `100` |  | :746 |
| `FOREST_BOAR_HP` | `40` |  | :751 |
| `FOREST_BOAR_DMG` | `(4, 7)` |  | :752 |
| `FOREST_BOAR_DODGE` | `15` |  | :753 |
| `FOREST_BOAR_LOSS_AP` | `10` |  | :755 |
| `FOREST_BOAR_LOOT` | `[('Мясо кабана', 50), ('Шкура кабана', 20), ('Клык кабана', 10), ('', 20)]` |  | :757 |
| `FOREST_WHITE_WOLF_HP` | `120` |  | :769 |
| `FOREST_WHITE_WOLF_DMG` | `(7, 12)` |  | :770 |
| `FOREST_WHITE_WOLF_DODGE` | `20` |  | :771 |
| `FOREST_WHITE_WOLF_LOSS_AP` | `15` |  | :773 |
| `FOREST_WHITE_WOLF_CHANCE` | `2.0` |  | :774 |
| `FOREST_WHITE_WOLF_PITY_TARGET` | `36` |  | :777 |
| `FOREST_WHITE_WOLF_BLEED_CHANCE` | `30` |  | :779 |
| `FOREST_WHITE_WOLF_BLEED_DMG` | `3` |  | :780 |
| `FOREST_WHITE_WOLF_AUTOWIN_HP` | `20` |  | :782 |
| `FOREST_WHITE_WOLF_SMALL_BLESSING` | `'внимание севера'` |  | :784 |
| `FOREST_WHITE_WOLF_BIG_BLESSING` | `'благословение севера'` |  | :785 |
| `FOREST_BOAR_SEED` | `{'key': 'boar', 'spot': 'forest', 'name': 'Дикий кабан', 'hp': FOREST_BOAR_HP, 'dmg_min': FOREST_BOAR_DMG[0], 'dmg_max': FOREST_BOAR_DMG[1], 'dodge': FOREST_BOAR_DODGE, 'loss_ap': FOREST_BOAR_LOSS_…` |  | :792 |
| `FOREST_WHITE_WOLF_SEED` | `{'key': 'white_wolf', 'spot': 'forest', 'name': 'Белый Волк Севера', 'hp': FOREST_WHITE_WOLF_HP, 'dmg_min': FOREST_WHITE_WOLF_DMG[0], 'dmg_max': FOREST_WHITE_WOLF_DMG[1], 'dodge': FOREST_WHITE_WOLF…` |  | :817 |
| `MOLLUSK_SEED` | `{'key': 'mollusk', 'spot': 'reservoir', 'name': 'Мутировавший моллюск', 'hp': 24, 'dmg_min': 5, 'dmg_max': 9, 'dodge': 20, 'loss_ap': 12, 'chance': 4, 'pity_target': 0, 'reward_nm': 0, 'photo_key':…` |  | :845 |
| `MOLLUSK_ITEM_SEEDS` | `[('Мясо моллюска', 'Плотное мясо мутировавшего моллюска. В сыром виде есть нельзя — прожарь на кухне.', 120, 60, 3, 'resource', 0), ('Жемчужина', 'Редчайшая жемчужина из раковины мутировавшего молл…` |  | :868 |
| `MOLLUSK_ENEMY_DROPS` | `('Мясо моллюска', 'Жемчужина')` |  | :883 |
| `MINE_AP_COST` | `12` | стоимость одной попытки добычи | :892 |
| `MINE_BASE_CHANCE` | `30` | базовый шанс успеха без бонуса кирки | :893 |
| `MINE_PICKAXE_BONUS_PER_RANK` | `15` | надбавка к шансу за ступень кирки (ранг 1 → +15%) | :894 |
| `MINE_CHANCE_CAP` | `90` | потолок шанса успеха | :895 |
| `MINE_RESULT_DELAY` | `(7, 15)` | результат добычи через 7–15 секунд | :896 |
| `MINE_REQUIRED_STATUS` | `'pilot1'` | вход в копь — с «Пилота 1 класса» | :897 |
| `MINE_GEM_CAP` | `1` | из самоцветов за бой выпадает не больше одного | :898 |
| `MINE_PICKAXE_NAME` | `'Кирка'` |  | :899 |
| `MINE_ORE_NAME` | `'Железная руда'` |  | :900 |
| `MINE_BAT_KEY` | `'bat'` |  | :903 |
| `MINE_BAT_SPOT` | `'iron'` |  | :904 |
| `MINE_BAT_CHANCE` | `7.0` |  | :905 |
| `MINE_BAT_PITY_TARGET` | `12` |  | :906 |
| `MINE_BAT_SEED` | `{'key': MINE_BAT_KEY, 'spot': MINE_BAT_SPOT, 'name': 'Летучая мышь', 'hp': 22, 'dmg_min': 3, 'dmg_max': 7, 'dodge': 35, 'loss_ap': 15, 'chance': MINE_BAT_CHANCE, 'pity_target': MINE_BAT_PITY_TARGET…` |  | :911 |
| `MINE_ITEM_SEEDS` | `[(MINE_PICKAXE_NAME, 'Простая кирка шахтёра: без неё в штольню не сунешься, а с ней порода поддаётся легче. Повышает шанс успешной добычи руды.', 300, 150, 1, 'mining', 0), (MINE_ORE_NAME, 'Кусок ж…` |  | :937 |
| `MINE_SHOP_ITEMS` | `(MINE_PICKAXE_NAME,)` |  | :958 |
| `MINE_ENEMY_DROPS` | `('Изумруд', 'Рубин', 'Сапфир')` |  | :961 |
| `ON_HIT_EFFECTS` | `{'bleed': {'emoji': '🩸', 'title': 'Кровотечение', 'until_battle_end': True, 'params': (('chance', 'Шанс наложить, %', 'percent'), ('dmg', 'Урон, HP за ход', 'int')), 'hint': 'Раны сочатся кровью ка…` |  | :970 |
| `ON_HIT_KIND_ORDER` | `('bleed', 'poison', 'frostbite', 'state', 'lifesteal', 'armor_pierce')` |  | :1034 |
| `ON_HIT_STATE_ROUNDS` | `{'оглушён': 3, 'ослеплён': 4}` |  | :1036 |
| `CLAN_ROLES` | `{'leader': '👑 Глава клана', 'seneschal': '🛡 Сенешаль клана', 'banner': '🚩 Знаменосец клана', 'elder': '⭐ Старшина', 'member': '▪️ Член клана'}` |  | :1042 |
| `CLAN_ROLE_ORDER` | `('leader', 'seneschal', 'banner', 'elder', 'member')` |  | :1049 |
| `LOGGING_AP_COST` | `12` | стоимость одной попытки рубки | :1055 |
| `LOGGING_BASE_CHANCE` | `35` | базовый шанс успеха без бонуса топора | :1056 |
| `LOGGING_AXE_BONUS_PER_RANK` | `15` | надбавка к шансу за ступень топора | :1057 |
| `LOGGING_CHANCE_CAP` | `90` | потолок шанса успеха | :1058 |
| `LOGGING_AXE_SLIP_CHANCE` | `2.5` | шанс, что топор отскочит пилоту в плечо, % | :1059 |
| `LOGGING_RESULT_DELAY` | `(7, 15)` | результат рубки через 7–15 секунд | :1060 |
| `LOGGING_AXE_NAME` | `'Топор'` |  | :1061 |
| `LOGGING_WOOD_NAME` | `'Бревна'` |  | :1062 |
| `LOGGING_PLANK_NAME` | `'Доска'` |  | :1068 |
| `LOGGING_FIREWOOD_NAME` | `'Пак дров'` |  | :1069 |
| `LOGGING_PLANK_YIELD` | `3` | досок из одного бревна | :1070 |
| `LOGGING_PLANK_FEE` | `15` | НМ за распил одного бревна (в казну) | :1071 |
| `LOGGING_FIREWOOD_YIELD` | `3` | паков дров из одного бревна | :1072 |
| `LOGGING_FIREWOOD_AP_COST` | `4` | ОД за рубку дров из одного бревна | :1073 |
| `LOGGING_SNAKE_KEY` | `'snake'` |  | :1077 |
| `LOGGING_OWL_KEY` | `'owl'` |  | :1078 |
| `LOGGING_SPOT` | `'logging'` |  | :1079 |
| `LOGGING_SNAKE_CHANCE` | `8.0` |  | :1080 |
| `LOGGING_SNAKE_PITY_TARGET` | `10` |  | :1081 |
| `LOGGING_OWL_CHANCE` | `3.0` |  | :1082 |
| `LOGGING_OWL_PITY_TARGET` | `24` |  | :1083 |
| `LOGGING_SNAKE_POISON_CHANCE` | `30` |  | :1085 |
| `LOGGING_SNAKE_POISON_DMG` | `2` |  | :1086 |
| `LOGGING_OWL_FLEE_HP` | `20` |  | :1090 |
| `LOGGING_OWL_BLIND_CHANCE` | `30` |  | :1091 |
| `LOGGING_OWL_BLIND_ROUNDS` | `4` |  | :1092 |
| `LOGGING_SNAKE_SEED` | `{'key': LOGGING_SNAKE_KEY, 'spot': LOGGING_SPOT, 'name': 'Лесная змея', 'hp': 30, 'dmg_min': 4, 'dmg_max': 8, 'dodge': 25, 'loss_ap': 10, 'chance': LOGGING_SNAKE_CHANCE, 'pity_target': LOGGING_SNAK…` |  | :1096 |
| `LOGGING_OWL_SEED` | `{'key': LOGGING_OWL_KEY, 'spot': LOGGING_SPOT, 'name': 'Неясыть', 'hp': 90, 'dmg_min': 7, 'dmg_max': 12, 'dodge': 30, 'loss_ap': 15, 'chance': LOGGING_OWL_CHANCE, 'pity_target': LOGGING_OWL_PITY_TA…` |  | :1126 |
| `LOGGING_ITEM_SEEDS` | `[(LOGGING_AXE_NAME, 'Крепкий лесорубский топор: без него к срубам не подпустят. Повышает шанс успешной рубки деревьев.', 300, 150, 1, 'mining', 0), (LOGGING_WOOD_NAME, 'Свежие срубленные брёвна из …` |  | :1158 |
| `LOGGING_SHOP_ITEMS` | `(LOGGING_AXE_NAME,)` |  | :1192 |
| `LOGGING_ENEMY_DROPS` | `('Змеиная кожа', 'Змеиный яд', 'Совиное перо')` |  | :1195 |
| `LOGGING_MARKET_RESOURCES` | `(LOGGING_PLANK_NAME, LOGGING_FIREWOOD_NAME)` |  | :1198 |
| `REPORT_DAILY_LIMIT` | `3` |  | :1200 |
| `REPORT_AUTO_APPROVE_TROOPS` | `100` |  | :1201 |
| `NEWS_PUBLISH_BONUS` | `10` |  | :1205 |
| `NEWS_PUBLISH_CAP` | `28` |  | :1206 |
| `ROLE_SALARY_PAY_DAY` | `28` |  | :1209 |
| `REPORT_DAILY_PAY_CAP` | `4000` |  | :1214 |
| `REPORT_MAX_TROOPS` | `1000000` |  | :1215 |
| `REPORT_MAX_REGION` | `38` | 0 = Столица, 1..38 регионы | :1216 |
| `WALL_TEXT_MAX_LEN` | `40` | лимит символов на одно изречение | :1219 |
| `WALL_FREE_PER_DAY` | `2` | бесплатных сообщений в сутки | :1220 |
| `WALL_PAID_STEPS` | `[(3, 30), (3, 90), (3, 200)]` | далее платные ступени: (кол-во, цена НМ) | :1221 |
| `WALL_REVIEW_TOTAL` | `11` | максимум сообщений в сутки (2 + 3+3+3) | :1226 |
| `WALL_PAGE_SIZE` | `5` | постов на страницу стены | :1227 |
| `WALL_ARCHIVE_PAGE_SIZE` | `8` | записей архива стены на страницу списка | :1228 |
| `REPORT_ARCHIVE_PAGE` | `8` | отчётов на страницу архива МВД и в «Моих отчётах» | :1231 |
| `POLL_MAX_DAYS` | `10` | максимум дней, сколько живёт опрос. Не закрыл | :1234 |
| `POLL_VISIBLE` | `4` | сколько новейших опросов висит в меню голосования. | :1237 |
| `POLL_ARCHIVE_DAYS_PER_PAGE` | `5` | дней (дат) архива опросов на страницу списка | :1240 |
| `POLL_ARCHIVE_PER_DAY` | `6` | опросов под одним заголовком-днём | :1241 |
| `REP_SPEECH_MAX_LEN` | `100` | лимит символов одного обращения | :1244 |
| `REP_SPEECH_PER_DAY` | `2` | обращений в сутки от представителя | :1245 |
| `AUTO_PROMOTE_MAX_TROOPS` | `4040` |  | :1250 |

## Буклет туриста

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `TOURIST_BOOKLET_NAME` | `'Буклет туриста'` |  | :23 |

## Древо Пламенного Круговорота (клановое расширение 'tree')

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `FIRE_TREE_CLAN_REQ_LAMPS` | `7` | сколько чланов с Лампой нужно для установки | :388 |

## Суточный цикл Нордхайма

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `REPORT_DAY_START_HOUR` | `10` |  | :435 |

## Дом Дуэлей (PvP-арена)

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `DUEL_ZONES` | `('head', 'body', 'hands', 'legs')` |  | :532 |

## Рынок: слоты продажи

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `MARKET_BASE_SLOTS` | `1` | слоты без лицензии | :607 |

## Налог на недвижимость (НМ/мес)

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `HOUSING_TAX` | `{'municipal': 0, 'studio': 20, 'apartment': 35, 'improved': 60, 'mansion': 100}` |  | :613 |

## Банк: лимит счёта туриста (НМ)

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `TOURIST_BALANCE_LIMIT` | `200` |  | :623 |

## Данж: лимит хила (количество применений за забег)

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `DUNGEON_HEAL_SOFT_LIMIT` | `6` | после этого — ×2/3 | :626 |

## Сброс протухших забегов подземелья

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `DUNGEON_RUN_STALE_SEC` | `3600` |  | :635 |

## Данж: побег и дымовая шашка

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `ESCAPE_BASE_CHANCE` | `25` |  | :643 |

