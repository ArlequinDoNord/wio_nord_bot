# Справочник констант `config.py`

> **Сгенерировано** `tools/export_config.py`. Перегенерация:
> `.venv\Scripts\python.exe tools/export_config.py`.
>
> Все модульные константы `config.py`, сгруппированные по секциям
> (комментариям-разделителям `# ── … ──`). Длинные значения усечены `…`;
> точное значение — в `config.py` по строке из первой колонки.

Всего констант: **344**; разделов: **11**.

## Без раздела

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `VERSION` | `'0.41.5'` |  | :16 |
| `VERSION_NOTES` | `'Праздничные хлопоты: в артели пишут новые рецепты для праздничного стола.'` |  | :17 |
| `PREV_VERSION` | `'0.41.4'` |  | :19 |
| `PREV_VERSION_NOTES` | `'Праздничные хлопоты: на артели появились новые заказы.'` |  | :20 |
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
| `FIRE_PUMPKIN_SEED_NAME` | `'Семечко тыквы'` |  | :75 |
| `FIRE_CROW_FEATHER_NAME` | `'Перо ворона'` |  | :76 |
| `FIRE_WIRE_NAME` | `'Моток железной проволоки'` |  | :77 |
| `FIRE_EGGS_NAME` | `'Яйца'` |  | :78 |
| `FIRE_CROWN_NAME` | `'Огненный венец'` |  | :79 |
| `FIRE_CLOAK_NAME` | `'Плащ Памяти'` |  | :80 |
| `FIRE_GLOVES_NAME` | `'Перчатки стража посевов'` |  | :81 |
| `FIRE_KEYS_NAME` | `'Вилы'` |  | :82 |
| `FIRE_FLAME_DEVICE_NAME` | `'Ручное пламенеющее устройство'` |  | :83 |
| `FIRELAB_SCARECROW_SEED` | `{'key': 'scarecrow', 'spot': 'firelab', 'name': 'Пугало', 'hp': FIRELAB_SCARECROW_HP, 'dmg_min': FIRELAB_SCARECROW_DMG[0], 'dmg_max': FIRELAB_SCARECROW_DMG[1], 'dodge': FIRELAB_SCARECROW_DODGE, 'ar…` |  | :85 |
| `FIRELAB_APPLE_CHILD_SEED` | `{'key': 'apple_child', 'spot': 'firelab', 'name': 'Дитя Яблони', 'hp': FIRELAB_APPLE_CHILD_HP, 'dmg_min': FIRELAB_APPLE_CHILD_DMG[0], 'dmg_max': FIRELAB_APPLE_CHILD_DMG[1], 'dodge': FIRELAB_APPLE_C…` |  | :112 |
| `FIRELAB_CROW_SEED` | `{'key': 'crow', 'spot': 'firelab', 'name': 'Ворон', 'hp': FIRELAB_CROW_HP, 'dmg_min': FIRELAB_CROW_DMG[0], 'dmg_max': FIRELAB_CROW_DMG[1], 'dodge': FIRELAB_CROW_DODGE, 'loss_ap': 0, 'chance': 0, 'p…` |  | :139 |
| `FIRELAB_HUB_SEED` | `{'key': 'hub', 'spot': 'firelab', 'name': 'Хуб', 'hp': FIRELAB_HUB_HP, 'dmg_min': FIRELAB_HUB_DMG[0], 'dmg_max': FIRELAB_HUB_DMG[1], 'dodge': FIRELAB_HUB_DODGE, 'loss_ap': 0, 'chance': 0, 'pity_tar…` |  | :164 |
| `FIRELAB_PUMPKIN_SEED` | `{'key': 'pumpkin_boss', 'spot': 'firelab', 'name': 'Мощный Мистер Огненная Тыква', 'hp': FIRELAB_PUMPKIN_HP, 'dmg_min': FIRELAB_PUMPKIN_DMG[0], 'dmg_max': FIRELAB_PUMPKIN_DMG[1], 'dodge': FIRELAB_P…` |  | :191 |
| `FIRELAB_ENEMY_SEEDS` | `(FIRELAB_SCARECROW_SEED, FIRELAB_APPLE_CHILD_SEED, FIRELAB_CROW_SEED, FIRELAB_HUB_SEED, FIRELAB_PUMPKIN_SEED)` |  | :221 |
| `FIRE_EVENT_ENABLED` | `True` |  | :229 |
| `FIRE_EVENT_START` | `(2026, 10, 30, 0, 0)` | МСК, ночь на пятницу 30.10 | :230 |
| `FIRE_EVENT_DURATION_DAYS` | `5` | до ~00:00 МСК 4.11 | :231 |
| `FIRE_LAB_ENABLED` | `False` |  | :233 |
| `FIRE_EVENT_LAB_FEE` | `42` | вход в лабиринт, НМ | :234 |
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
| `FIRE_LAB_TIER_MAX` | `5` | кап усилений | :260 |
| `FIRE_LAB_TIER_HP_STEP` | `2` | +HP всем врагам за тир (1–4) | :261 |
| `FIRE_LAB_TIER_HP_LAST` | `8` | 5-й тир: разово +8 (итого +16) | :262 |
| `FIRE_LAB_TIER_LOOT_STEP` | `0.02` | лут ×(1+2%) за тир (1–4) | :263 |
| `FIRE_LAB_TIER_LOOT_LAST` | `0.1` | 5-й тир: ×(1+10%) | :264 |
| `FIRE_LAB_P_WELL` | `0.07` | Колодец (перебивается паттерном ЛЛПП) | :267 |
| `FIRE_LAB_WELL_MAX` | `3` | максимум посещений за заход | :268 |
| `FIRE_LAB_P_TREE` | `0.09` | Древо Огня (перебивается ЛЛППНН) | :269 |
| `FIRE_LAB_TREE_MAX` | `1` | раз за заход | :270 |
| `FIRE_TREE_DMG_BONUS_PCT` | `15` | +15% урона | :274 |
| `FIRE_TREE_REGEN_HP` | `1` | +1 HP после каждого удара игрока | :275 |
| `FIRE_LAB_PATTERN_WELL` | `('L', 'L', 'S', 'S')` | ЛЛПП → Колодец (до 3) | :279 |
| `FIRE_LAB_PATTERN_TREE` | `('L', 'L', 'S', 'S', 'R', 'R')` | ЛЛППНН → Древо Огня (1) | :280 |
| `FIRE_LAB_WELL_FISH_TRIES` | `6` | попыток рыбалки за один визит в Колодец | :283 |
| `FIRE_LAB_FISH_BITE_P` | `0.75` | шанс поклёвки за попытку | :284 |
| `FIRE_LAB_FISH_OSETR_NAME` | `'Спектральная Латимерия'` | рыба 1 (rarity 2) | :286 |
| `FIRE_LAB_FISH_SOUL_NAME` | `'Скелетная Арована'` | рыба 2 (rarity 3) | :287 |
| `FIRE_LAB_FISH_CARP_NAME` | `'Пылающая Душа'` | рыба 3 (rarity 4, редкая) | :288 |
| `FIRE_LAB_FISH_TABLE` | `((FIRE_LAB_FISH_OSETR_NAME, 60), (FIRE_LAB_FISH_SOUL_NAME, 25), (FIRE_LAB_FISH_CARP_NAME, 15))` | взвешенный выбор улова | :289 |
| `FIRE_FISHER_ACH_KEY` | `'fire_fisher'` |  | :295 |
| `FIRE_FISHER_THRESHOLD` | `3` |  | :296 |
| `FIRE_FISHER_REWARD_NM` | `150` |  | :297 |
| `FIRE_LAB_PIE_NAME` | `'Кусочек тыквенного пирога'` |  | :299 |
| `FIRE_LAB_PIE_HEAL` | `15` |  | :300 |
| `FIRE_LAB_RECIPE_NAME` | `'Рецепт: Тыквенный пирог'` |  | :301 |
| `FIRE_LAB_CANDY_NAME` | `'Леденец языков пламени'` |  | :302 |
| `FIRE_LAB_CANDY_HEAL` | `12` |  | :303 |
| `FIRE_LAB_HAY_NAME` | `'Пучок сена'` |  | :304 |
| `FIRE_LAB_BRANCH_NAME` | `'Ветка дерева'` |  | :305 |
| `FIRE_PUMPKIN_SEED_NAME` | `'Семечко тыквы'` | посадка в кадку / клан. сад | :309 |
| `FIRE_PUMPKIN_NAME` | `'Тыква'` | плод; ингредиент пирога | :310 |
| `FIRE_CROW_FEATHER_NAME` | `'Перо ворона'` | ресурс (дроп стража? — Ф5) | :311 |
| `FIRE_WIRE_NAME` | `'Моток железной проволоки'` | ингредиент трости | :312 |
| `FIRE_SUGAR_NAME` | `'Сахар'` | ингредиент пирога | :313 |
| `FIRE_EGGS_NAME` | `'Яйца'` | ингредиент пирога (x2) | :314 |
| `FIRE_KEYS_NAME` | `'Вилы'` | оружие: +2 к удару, кровотечение | :315 |
| `FIRE_KEYS_DMG` | `2` |  | :316 |
| `FIRE_KEYS_BLEED_P` | `10` |  | :317 |
| `FIRE_KEYS_BLEED_DMG` | `2` |  | :318 |
| `FIRE_CROWN_NAME` | `'Огненный венец'` | голова: броня 2, лечение +25% | :319 |
| `FIRE_CROWN_HEAL_BONUS_PCT` | `25` |  | :320 |
| `FIRE_CLOAK_NAME` | `'Плащ Памяти'` | тело: броня 2, уклон +5% | :321 |
| `FIRE_CLOAK_DODGE` | `5` |  | :322 |
| `FIRE_GLOVES_NAME` | `'Перчатки стража посевов'` | руки: броня 2, уклон +3% | :323 |
| `FIRE_GLOVES_DODGE` | `3` |  | :324 |
| `FIRE_CANE_NAME` | `'Обжигающая трость'` | оружие: удар 3, поджог 20% | :325 |
| `FIRE_CANE_DMG` | `3` |  | :326 |
| `FIRE_FLAME_DEVICE_NAME` | `'Ручное пламенеющее устройство'` | ингредиент трости | :327 |
| `FIRE_CANE_BURN_P` | `20` |  | :328 |
| `FIRE_CANE_BURN_DMG` | `2` |  | :329 |
| `FIRE_CANE_BURN_ROUNDS` | `3` |  | :330 |
| `FIRE_LANTERN_NAME` | `'Лампа Круговорота'` | награда за «Чтящего Предков» (Ф4б) | :331 |
| `FIRE_AMBER_NAME` | `'Пламя Памяти'` | янтарь из Лампы (Ф4б), продам 100 НМ | :332 |
| `FIRE_LANTERN_MEDIT_AP` | `20` | 🪔 медитация раз в сутки | :333 |
| `FIRE_LANTERN_AMBER_DAYS` | `7` | янтарь раз в N суток | :334 |
| `FIRE_PREDKI_NAME` | `'Предания предков'` |  | :337 |
| `FIRE_PREDKI_HEAL` | `60` | +60 HP в бою | :338 |
| `FIRE_PREDKI_REGEN` | `50` | регенерация: 50% от лечения | :339 |
| `FIRE_PREDKI_REGEN_TURNS` | `4` | разлитая на 4 хода (нестандарт!) | :340 |
| `FIRE_PREDKI_DODGE_PCT` | `5` | суточный баф: уворот +5% | :341 |
| `FIRE_PREDKI_DODGE_HOURS` | `24` | длительность бафа (не продлевается) | :342 |
| `CLAN_BUILDING_TYPES` | `{'house': {'name': 'Дом Клана', 'slots': 2, 'max_level': 2, 'days': 2, 'price_nm': 3000, 'required': {'Доска': 60, 'Бревна': 20, 'Железная руда': 15}}, 'manor': {'name': 'Клановое поместье', 'slots…` |  | :344 |
| `CLAN_BUILDING_NO_RESOURCES_MULT` | `2` |  | :359 |
| `CLAN_EXPANSION_TYPES` | `('kitchen', 'workbench', 'shower', 'garden', 'library', 'shop', 'tree')` |  | :361 |
| `CLAN_EXPANSION_INFO` | `{'kitchen': {'name': 'Кухня', 'icon': '🍳', 'desc': 'Готовка по выученным рецептам; уровень задаёт доступные блюда.'}, 'workbench': {'name': 'Крафтовый стол', 'icon': '🛠', 'desc': 'Крафт снаряжения …` |  | :363 |
| `FIRE_TREE_CLAN_MEDIT_AP` | `20` | 🧘 медитация у Древа (в доп. к домашней) | :385 |
| `FIRE_TREE_CLAN_ESSENCE_NAME` | `'Эссенция Памяти'` |  | :386 |
| `FIRE_TREE_CLAN_ESSENCE_DAYS` | `30` | раз в 30 дней (от установки/сбора) | :387 |
| `FIRE_TREE_CLAN_ESSENCE_SELL` | `500` | продажа кристалла на скупке | :388 |
| `CLAN_EXPANSION_UPGRADE` | `{2: {'nm': 1500, 'required': {'Доска': 20, 'Железная руда': 10}}, 3: {'nm': 4000, 'required': {'Доска': 50, 'Железная руда': 30}}, 4: {'nm': 9000, 'required': {'Доска': 100, 'Железная руда': 60}}}` |  | :390 |
| `CLAN_SHOWER_AP_BY_LEVEL` | `{1: 25, 2: 50, 3: 75, 4: 100}` |  | :398 |
| `CLAN_SHOWER_SOBER_MINUTES` | `{1: 60, 2: 120, 3: 180, 4: 240}` |  | :399 |
| `CLAN_GARDEN_PLOTS` | `{1: 2, 2: 3, 3: 4, 4: 6}` |  | :401 |
| `CLAN_SHOP_DAILY_LIMIT` | `3` |  | :402 |
| `CLAN_SHOP_DISCOUNT` | `10` |  | :403 |
| `BOT_TOKEN` | `os.getenv('BOT_TOKEN')` |  | :405 |
| `ADMIN_IDS` | `[int(x) for x in os.getenv('ADMIN_IDS', '').split(',') if x.strip()]` |  | :406 |
| `_news_raw` | `os.getenv('NEWS_CHAT_ID', '').strip()` |  | :409 |
| `NEWS_CHAT_ID` | `int(_news_raw) if _news_raw.lstrip('-').isdigit() else None` |  | :410 |
| `DB_PATH` | `os.getenv('DATABASE_PATH', 'database/nordmark.db')` |  | :413 |
| `FSM_STORAGE_PATH` | `os.getenv('FSM_STORAGE_PATH', '').strip() or os.path.join(os.path.dirname(os.path.abspath(DB_PATH)), 'fsm')` |  | :422 |
| `REPORT_DAY_START_MINUTE` | `0` |  | :432 |
| `RANKS` | `[('Рекрут', 0), ('Рядовой', 100), ('Ефрейтор', 350), ('Капрал', 500), ('Сержант', 850), ('Старший Сержант', 1500), ('Лейтенант', 2500), ('Старший Лейтенант', 4040), ('Капитан', 6000), ('Майор', 850…` |  | :434 |
| `MAX_SELF_RANK_TROOPS` | `4040` |  | :455 |
| `AUTO_RANK_NAMES` | `('Рекрут', 'Рядовой', 'Ефрейтор', 'Капрал', 'Сержант', 'Старший Сержант', 'Лейтенант', 'Старший Лейтенант')` |  | :458 |
| `AWARD_MAX_SHOP_DISCOUNT` | `40` |  | :465 |
| `AWARD_MIN_REPORT_TAX` | `5` |  | :466 |
| `RANK_STATUS_TAGS` | `{'Ефрейтор': 'pilot2', 'Старший Сержант': 'pilot1', 'Старший Лейтенант': 'veteran', 'Майор': 'master_pilot', 'Полковник': 'ace'}` |  | :468 |
| `LEGIONER_ACCESS_CAP_ORDER` | `5` |  | :481 |
| `RANK_DAMAGE_TIERS` | `{'ace': (4, 8), 'master_pilot': (3, 5), 'veteran': (2, 4), 'pilot1': (1, 3), 'pilot2': (1, 2), 'recruit': (1, 1), 'tourist': (0, 1)}` |  | :487 |
| `RANK_CRIT_CHANCE` | `{'ace': 7.5, 'master_pilot': 6.0, 'veteran': 4.5, 'pilot1': 3.0, 'pilot2': 1.5, 'recruit': 0.0, 'tourist': 0.0}` |  | :505 |
| `PILOT_CRIT_MULT` | `1.4` |  | :519 |
| `PILOT_NO_WEAPON_DMG` | `(1, 1)` |  | :522 |
| `DUEL_ZONE_LABELS` | `{'head': 'Голова', 'body': 'Тело', 'hands': 'Руки', 'legs': 'Ноги'}` |  | :529 |
| `DUEL_ZONE_EMOJI` | `{'head': '🧠', 'body': '🫀', 'hands': '✊', 'legs': '🦵'}` |  | :535 |
| `DUEL_AP_COST` | `15` | списывается с обоих при старте боя | :541 |
| `DUEL_RATING_WIN` | `2` | рейтинг за победу | :542 |
| `DUEL_RATING_LOSS` | `-3` | рейтинг за поражение | :543 |
| `DUEL_RATING_DRAW` | `0` | рейтинг за ничью | :544 |
| `DUEL_RATING_FORFEIT` | `-1` | рейтинг тому, кто покинул бой («Покинуть дуэль») | :545 |
| `DUEL_RATING_FORFEIT_WIN` | `1` | рейтинг сопернику, если противник покинул бой (меньше чистой победы) | :546 |
| `DUEL_MIN_DAMAGE` | `1` | минимум урона за попавший (не уклонённый) удар | :547 |
| `DUEL_GUARD_REDUCTION` | `0.5` | доля урона, остающаяся при угаданной зоне защиты | :548 |
| `DUEL_HEAL_BETWEEN` | `0` | восстановление HP между раундами (пока нет) | :549 |
| `DUEL_CHALLENGE_TIMEOUT_SEC` | `120` | сколько живёт неотвеченный вызов | :550 |
| `DUEL_STALE_SEC` | `1800` | зависшая дуэль авто-завершается как void | :551 |
| `DUEL_GLOVES_NAME` | `'Дуэльные перчатки'` |  | :552 |
| `DUEL_GLOVES_DAMAGE` | `7` |  | :553 |
| `DUEL_GLOVES_PRICE` | `200` |  | :554 |
| `DUEL_GLOVES_SELL` | `100` |  | :555 |
| `DUEL_CLUB_CARD_NAME` | `'Клубная карта «Дом Дуэлей»'` |  | :556 |
| `DUEL_CLUB_CARD_PRICE` | `150` |  | :557 |
| `DUEL_CLUB_CARD_SELL` | `75` |  | :558 |
| `DUEL_CLUB_CARD_DAYS` | `30` |  | :559 |
| `DUEL_ACCESS_TAG` | `'pilot2'` |  | :562 |
| `RARITY_LEVELS` | `{1: 'Обычный', 2: 'Качественный', 3: 'Редкий', 4: 'Шедевр', 5: 'Легендарный'}` |  | :564 |
| `RARITY_EMOJI` | `{1: '⬜', 2: '🟩', 3: '🟦', 4: '🟪', 5: '🟧'}` |  | :572 |
| `ITEM_CATEGORIES` | `{'weapon': 'Оружие', 'consumable': 'Расходники', 'building': 'Недвижимость', 'housing': 'Жильё', 'furniture': 'Мебель и расширения', 'seeds': 'Семена', 'equipment': 'Одежда', 'resource': 'Ресурсы',…` |  | :580 |
| `MARKET_LICENSE_SLOTS` | `2` | доп. слоты при активной лицензии | :604 |
| `MARKET_LICENSE_DAYS` | `30` | срок действия лицензии (дней) | :605 |
| `MARKET_LICENSE_PRICE` | `500` | цена лицензии в НМ | :606 |
| `DUNGEON_HEAL_HARD_LIMIT` | `10` | после этого — ×1/2 | :623 |
| `DUNGEON_HEAL_SOFT_MULT` | `2 / 3` |  | :624 |
| `DUNGEON_HEAL_HARD_MULT` | `1 / 2` |  | :625 |
| `ESCAPE_HP_BONUS` | `20` |  | :640 |
| `DUNGEON_SMOKE_ESCAPE` | `95` |  | :641 |
| `DUNGEON_SMOKE_MAX` | `2` |  | :642 |
| `DUNGEON_ESCAPE_DRUNK_MULT` | `0.5` |  | :645 |
| `AP_MAX` | `150` |  | :647 |
| `AP_DAILY_RECOVERY` | `100` |  | :648 |
| `AP_BONUS_FROM_CONSUMABLE` | `50` |  | :649 |
| `AP_DAILY_RESTORE_LIMIT` | `150` |  | :654 |
| `AP_EXHAUSTED_MINUTES` | `2880` | 2 суток | :655 |
| `AP_EXHAUSTED_DAILY_RECOVERY` | `75` | суточное восстановление в «истощении» | :656 |
| `AP_EXHAUSTED_MAX_AP` | `90` | максимум ОД в «истощении» | :657 |
| `SEAWEED_DAILY_LIMIT` | `6` |  | :660 |
| `DIGESTIVE_UPSET_MINUTES` | `1440` | 24 часа | :661 |
| `ALCOHOL_WEAK_DRUNK_LIMIT` | `3` |  | :666 |
| `ALCOHOL_WEAK_VERY_DRUNK_LIMIT` | `6` |  | :667 |
| `ALCOHOL_STRONG_DRUNK_LIMIT` | `1` |  | :669 |
| `ALCOHOL_STRONG_VERY_DRUNK_LIMIT` | `2` |  | :670 |
| `DRUNK_MINUTES` | `60` |  | :671 |
| `VERY_DRUNK_MINUTES` | `360` | 6 часов | :672 |
| `DRINK_EFFECT_LABELS` | `{'alcohol_weak': '🍺 Слабоалкогольный: 3 шт/сутки — «пьян», 6 — «очень пьян»', 'alcohol_strong': '🥃 Крепкий алкоголь: 1 шт — «пьян», 2 — «очень пьян»', 'indigestion': '🤢 Вызывает «несварение» на сут…` |  | :675 |
| `SPECIAL_DEPT_CODE_MIN_LEN` | `4` |  | :686 |
| `SPECIAL_DEPT_CODE_MAX_LEN` | `8` |  | :687 |
| `SPECIAL_DEPT_ATTEMPTS_LIMIT` | `3` | ошибок кода подряд | :688 |
| `SPECIAL_DEPT_BLOCK_MINUTES` | `1440` | бан на 24 часа после 3 ошибок | :689 |
| `FISH_AP_COST` | `3` | стоимость одного заброса удочки | :692 |
| `RESERVOIR_AP_COST` | `5` |  | :697 |
| `FISH_WEIGHTS` | `[{'key': 'small', 'label': 'Мелкая', 'mult': 1.0, 'chance': 40}, {'key': 'medium', 'label': 'Средняя', 'mult': 1.15, 'chance': 40}, {'key': 'large', 'label': 'Большая', 'mult': 1.25, 'chance': 20}]` |  | :702 |
| `FISH_TREASURY_SALE_MULT` | `0.5` |  | :710 |
| `FISH_TREASURY_DAILY_LIMIT` | `300` |  | :715 |
| `FOREST_AP_COST` | `4` | запасной цена поиска, если у зоны нет ap_cost в БД | :718 |
| `FOREST_RESULT_DELAY` | `(5, 10)` | результат поиска через 5–10 секунд | :721 |
| `FOREST_SOLD_DAILY_LIMIT` | `250` |  | :726 |
| `FOREST_ALLOW_TOURISTS` | `False` |  | :731 |
| `FOREST_BOAR_PITY_TARGET` | `12` |  | :734 |
| `FOREST_BOAR_CHANCE` | `4.0` |  | :738 |
| `CALLSIGN_PRICE` | `500` |  | :740 |
| `PILOT_BASE_HP` | `100` |  | :742 |
| `FOREST_BOAR_HP` | `40` |  | :747 |
| `FOREST_BOAR_DMG` | `(4, 7)` |  | :748 |
| `FOREST_BOAR_DODGE` | `15` |  | :749 |
| `FOREST_BOAR_LOSS_AP` | `10` |  | :751 |
| `FOREST_BOAR_LOOT` | `[('Мясо кабана', 50), ('Шкура кабана', 20), ('Клык кабана', 10), ('', 20)]` |  | :753 |
| `FOREST_WHITE_WOLF_HP` | `120` |  | :765 |
| `FOREST_WHITE_WOLF_DMG` | `(7, 12)` |  | :766 |
| `FOREST_WHITE_WOLF_DODGE` | `20` |  | :767 |
| `FOREST_WHITE_WOLF_LOSS_AP` | `15` |  | :769 |
| `FOREST_WHITE_WOLF_CHANCE` | `2.0` |  | :770 |
| `FOREST_WHITE_WOLF_PITY_TARGET` | `36` |  | :773 |
| `FOREST_WHITE_WOLF_BLEED_CHANCE` | `30` |  | :775 |
| `FOREST_WHITE_WOLF_BLEED_DMG` | `3` |  | :776 |
| `FOREST_WHITE_WOLF_AUTOWIN_HP` | `20` |  | :778 |
| `FOREST_WHITE_WOLF_SMALL_BLESSING` | `'внимание севера'` |  | :780 |
| `FOREST_WHITE_WOLF_BIG_BLESSING` | `'благословение севера'` |  | :781 |
| `FOREST_BOAR_SEED` | `{'key': 'boar', 'spot': 'forest', 'name': 'Дикий кабан', 'hp': FOREST_BOAR_HP, 'dmg_min': FOREST_BOAR_DMG[0], 'dmg_max': FOREST_BOAR_DMG[1], 'dodge': FOREST_BOAR_DODGE, 'loss_ap': FOREST_BOAR_LOSS_…` |  | :788 |
| `FOREST_WHITE_WOLF_SEED` | `{'key': 'white_wolf', 'spot': 'forest', 'name': 'Белый Волк Севера', 'hp': FOREST_WHITE_WOLF_HP, 'dmg_min': FOREST_WHITE_WOLF_DMG[0], 'dmg_max': FOREST_WHITE_WOLF_DMG[1], 'dodge': FOREST_WHITE_WOLF…` |  | :813 |
| `MOLLUSK_SEED` | `{'key': 'mollusk', 'spot': 'reservoir', 'name': 'Мутировавший моллюск', 'hp': 24, 'dmg_min': 5, 'dmg_max': 9, 'dodge': 20, 'loss_ap': 12, 'chance': 4, 'pity_target': 0, 'reward_nm': 0, 'photo_key':…` |  | :841 |
| `MOLLUSK_ITEM_SEEDS` | `[('Мясо моллюска', 'Плотное мясо мутировавшего моллюска. В сыром виде есть нельзя — прожарь на кухне.', 120, 60, 3, 'resource', 0), ('Жемчужина', 'Редчайшая жемчужина из раковины мутировавшего молл…` |  | :864 |
| `MOLLUSK_ENEMY_DROPS` | `('Мясо моллюска', 'Жемчужина')` |  | :879 |
| `MINE_AP_COST` | `12` | стоимость одной попытки добычи | :888 |
| `MINE_BASE_CHANCE` | `30` | базовый шанс успеха без бонуса кирки | :889 |
| `MINE_PICKAXE_BONUS_PER_RANK` | `15` | надбавка к шансу за ступень кирки (ранг 1 → +15%) | :890 |
| `MINE_CHANCE_CAP` | `90` | потолок шанса успеха | :891 |
| `MINE_RESULT_DELAY` | `(7, 15)` | результат добычи через 7–15 секунд | :892 |
| `MINE_REQUIRED_STATUS` | `'pilot1'` | вход в копь — с «Пилота 1 класса» | :893 |
| `MINE_GEM_CAP` | `1` | из самоцветов за бой выпадает не больше одного | :894 |
| `MINE_PICKAXE_NAME` | `'Кирка'` |  | :895 |
| `MINE_ORE_NAME` | `'Железная руда'` |  | :896 |
| `MINE_BAT_KEY` | `'bat'` |  | :899 |
| `MINE_BAT_SPOT` | `'iron'` |  | :900 |
| `MINE_BAT_CHANCE` | `7.0` |  | :901 |
| `MINE_BAT_PITY_TARGET` | `12` |  | :902 |
| `MINE_BAT_SEED` | `{'key': MINE_BAT_KEY, 'spot': MINE_BAT_SPOT, 'name': 'Летучая мышь', 'hp': 22, 'dmg_min': 3, 'dmg_max': 7, 'dodge': 35, 'loss_ap': 15, 'chance': MINE_BAT_CHANCE, 'pity_target': MINE_BAT_PITY_TARGET…` |  | :907 |
| `MINE_ITEM_SEEDS` | `[(MINE_PICKAXE_NAME, 'Простая кирка шахтёра: без неё в штольню не сунешься, а с ней порода поддаётся легче. Повышает шанс успешной добычи руды.', 300, 150, 1, 'mining', 0), (MINE_ORE_NAME, 'Кусок ж…` |  | :933 |
| `MINE_SHOP_ITEMS` | `(MINE_PICKAXE_NAME,)` |  | :954 |
| `MINE_ENEMY_DROPS` | `('Изумруд', 'Рубин', 'Сапфир')` |  | :957 |
| `ON_HIT_EFFECTS` | `{'bleed': {'emoji': '🩸', 'title': 'Кровотечение', 'until_battle_end': True, 'params': (('chance', 'Шанс наложить, %', 'percent'), ('dmg', 'Урон, HP за ход', 'int')), 'hint': 'Раны сочатся кровью ка…` |  | :966 |
| `ON_HIT_KIND_ORDER` | `('bleed', 'poison', 'frostbite', 'state', 'lifesteal')` |  | :1020 |
| `ON_HIT_STATE_ROUNDS` | `{'оглушён': 3, 'ослеплён': 4}` |  | :1022 |
| `CLAN_ROLES` | `{'leader': '👑 Глава клана', 'seneschal': '🛡 Сенешаль клана', 'banner': '🚩 Знаменосец клана', 'elder': '⭐ Старшина', 'member': '▪️ Член клана'}` |  | :1028 |
| `CLAN_ROLE_ORDER` | `('leader', 'seneschal', 'banner', 'elder', 'member')` |  | :1035 |
| `LOGGING_AP_COST` | `12` | стоимость одной попытки рубки | :1041 |
| `LOGGING_BASE_CHANCE` | `35` | базовый шанс успеха без бонуса топора | :1042 |
| `LOGGING_AXE_BONUS_PER_RANK` | `15` | надбавка к шансу за ступень топора | :1043 |
| `LOGGING_CHANCE_CAP` | `90` | потолок шанса успеха | :1044 |
| `LOGGING_AXE_SLIP_CHANCE` | `2.5` | шанс, что топор отскочит пилоту в плечо, % | :1045 |
| `LOGGING_RESULT_DELAY` | `(7, 15)` | результат рубки через 7–15 секунд | :1046 |
| `LOGGING_AXE_NAME` | `'Топор'` |  | :1047 |
| `LOGGING_WOOD_NAME` | `'Бревна'` |  | :1048 |
| `LOGGING_PLANK_NAME` | `'Доска'` |  | :1054 |
| `LOGGING_FIREWOOD_NAME` | `'Пак дров'` |  | :1055 |
| `LOGGING_PLANK_YIELD` | `3` | досок из одного бревна | :1056 |
| `LOGGING_PLANK_FEE` | `15` | НМ за распил одного бревна (в казну) | :1057 |
| `LOGGING_FIREWOOD_YIELD` | `3` | паков дров из одного бревна | :1058 |
| `LOGGING_FIREWOOD_AP_COST` | `4` | ОД за рубку дров из одного бревна | :1059 |
| `LOGGING_SNAKE_KEY` | `'snake'` |  | :1063 |
| `LOGGING_OWL_KEY` | `'owl'` |  | :1064 |
| `LOGGING_SPOT` | `'logging'` |  | :1065 |
| `LOGGING_SNAKE_CHANCE` | `8.0` |  | :1066 |
| `LOGGING_SNAKE_PITY_TARGET` | `10` |  | :1067 |
| `LOGGING_OWL_CHANCE` | `3.0` |  | :1068 |
| `LOGGING_OWL_PITY_TARGET` | `24` |  | :1069 |
| `LOGGING_SNAKE_POISON_CHANCE` | `30` |  | :1071 |
| `LOGGING_SNAKE_POISON_DMG` | `2` |  | :1072 |
| `LOGGING_OWL_FLEE_HP` | `20` |  | :1076 |
| `LOGGING_OWL_BLIND_CHANCE` | `30` |  | :1077 |
| `LOGGING_OWL_BLIND_ROUNDS` | `4` |  | :1078 |
| `LOGGING_SNAKE_SEED` | `{'key': LOGGING_SNAKE_KEY, 'spot': LOGGING_SPOT, 'name': 'Лесная змея', 'hp': 30, 'dmg_min': 4, 'dmg_max': 8, 'dodge': 25, 'loss_ap': 10, 'chance': LOGGING_SNAKE_CHANCE, 'pity_target': LOGGING_SNAK…` |  | :1082 |
| `LOGGING_OWL_SEED` | `{'key': LOGGING_OWL_KEY, 'spot': LOGGING_SPOT, 'name': 'Неясыть', 'hp': 90, 'dmg_min': 7, 'dmg_max': 12, 'dodge': 30, 'loss_ap': 15, 'chance': LOGGING_OWL_CHANCE, 'pity_target': LOGGING_OWL_PITY_TA…` |  | :1112 |
| `LOGGING_ITEM_SEEDS` | `[(LOGGING_AXE_NAME, 'Крепкий лесорубский топор: без него к срубам не подпустят. Повышает шанс успешной рубки деревьев.', 300, 150, 1, 'mining', 0), (LOGGING_WOOD_NAME, 'Свежие срубленные брёвна из …` |  | :1144 |
| `LOGGING_SHOP_ITEMS` | `(LOGGING_AXE_NAME,)` |  | :1178 |
| `LOGGING_ENEMY_DROPS` | `('Змеиная кожа', 'Змеиный яд', 'Совиное перо')` |  | :1181 |
| `LOGGING_MARKET_RESOURCES` | `(LOGGING_PLANK_NAME, LOGGING_FIREWOOD_NAME)` |  | :1184 |
| `REPORT_DAILY_LIMIT` | `3` |  | :1186 |
| `REPORT_AUTO_APPROVE_TROOPS` | `100` |  | :1187 |
| `NEWS_PUBLISH_BONUS` | `10` |  | :1191 |
| `NEWS_PUBLISH_CAP` | `28` |  | :1192 |
| `ROLE_SALARY_PAY_DAY` | `28` |  | :1195 |
| `REPORT_DAILY_PAY_CAP` | `4000` |  | :1200 |
| `REPORT_MAX_TROOPS` | `1000000` |  | :1201 |
| `REPORT_MAX_REGION` | `38` | 0 = Столица, 1..38 регионы | :1202 |
| `WALL_TEXT_MAX_LEN` | `40` | лимит символов на одно изречение | :1205 |
| `WALL_FREE_PER_DAY` | `2` | бесплатных сообщений в сутки | :1206 |
| `WALL_PAID_STEPS` | `[(3, 30), (3, 90), (3, 200)]` | далее платные ступени: (кол-во, цена НМ) | :1207 |
| `WALL_REVIEW_TOTAL` | `11` | максимум сообщений в сутки (2 + 3+3+3) | :1212 |
| `WALL_PAGE_SIZE` | `5` | постов на страницу стены | :1213 |
| `WALL_ARCHIVE_PAGE_SIZE` | `8` | записей архива стены на страницу списка | :1214 |
| `REPORT_ARCHIVE_PAGE` | `8` | отчётов на страницу архива МВД и в «Моих отчётах» | :1217 |
| `POLL_MAX_DAYS` | `10` | максимум дней, сколько живёт опрос. Не закрыл | :1220 |
| `POLL_VISIBLE` | `4` | сколько новейших опросов висит в меню голосования. | :1223 |
| `POLL_ARCHIVE_DAYS_PER_PAGE` | `5` | дней (дат) архива опросов на страницу списка | :1226 |
| `POLL_ARCHIVE_PER_DAY` | `6` | опросов под одним заголовком-днём | :1227 |
| `REP_SPEECH_MAX_LEN` | `100` | лимит символов одного обращения | :1230 |
| `REP_SPEECH_PER_DAY` | `2` | обращений в сутки от представителя | :1231 |
| `AUTO_PROMOTE_MAX_TROOPS` | `4040` |  | :1236 |

## Буклет туриста

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `TOURIST_BOOKLET_NAME` | `'Буклет туриста'` |  | :23 |

## Древо Пламенного Круговорота (клановое расширение 'tree')

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `FIRE_TREE_CLAN_REQ_LAMPS` | `7` | сколько чланов с Лампой нужно для установки | :384 |

## Суточный цикл Нордхайма

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `REPORT_DAY_START_HOUR` | `10` |  | :431 |

## Дом Дуэлей (PvP-арена)

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `DUEL_ZONES` | `('head', 'body', 'hands', 'legs')` |  | :528 |

## Рынок: слоты продажи

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `MARKET_BASE_SLOTS` | `1` | слоты без лицензии | :603 |

## Налог на недвижимость (НМ/мес)

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `HOUSING_TAX` | `{'municipal': 0, 'studio': 20, 'apartment': 35, 'improved': 60, 'mansion': 100}` |  | :609 |

## Банк: лимит счёта туриста (НМ)

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `TOURIST_BALANCE_LIMIT` | `200` |  | :619 |

## Данж: лимит хила (количество применений за забег)

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `DUNGEON_HEAL_SOFT_LIMIT` | `6` | после этого — ×2/3 | :622 |

## Сброс протухших забегов подземелья

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `DUNGEON_RUN_STALE_SEC` | `3600` |  | :631 |

## Данж: побег и дымовая шашка

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `ESCAPE_BASE_CHANCE` | `25` |  | :639 |

