# История миграций базы данных

> **Сгенерировано** `tools/export_migrations.py`. Перегенерация:
> `.venv\Scripts\python.exe tools/export_migrations.py`.
>
> Схема эволюционирует **аддитивно**: новые колонки добавляются в `init_db()`
> через `_ensure_column(...)` (проверяет `PRAGMA table_info` и делает
> `ALTER TABLE ADD COLUMN`, если колонки нет). Повторный запуск безопасен.
> Засевы данных (`ensure_*`/`seed_*`) идемпотентны и вызываются из `main.py`
> при каждом старте.

## 1. Колоночные миграции `_ensure_column`

Всего вызовов: **203**; таблиц: **30**.

| Таблица | Колонка | Тип / значение по умолчанию | db.py |
|---|---|---|---|
| `awards` | `achievement_key` | `TEXT DEFAULT NULL` | :1462 |
| `awards` | `achievement_level` | `INTEGER DEFAULT 0` | :1463 |
| `awards` | `bonus_attack` | `INTEGER DEFAULT 0` | :1441 |
| `awards` | `bonus_crit` | `INTEGER DEFAULT 0` | :1448 |
| `awards` | `bonus_defense` | `INTEGER DEFAULT 0` | :1442 |
| `awards` | `bonus_dodge` | `INTEGER DEFAULT 0` | :1443 |
| `awards` | `bonus_fishing` | `INTEGER DEFAULT 0` | :1444 |
| `awards` | `bonus_hp` | `INTEGER DEFAULT 0` | :1445 |
| `awards` | `bonus_json` | `TEXT DEFAULT '{}'` | :1464 |
| `awards` | `bonus_report_tax` | `INTEGER DEFAULT 0` | :1452 |
| `awards` | `bonus_shop_discount` | `INTEGER DEFAULT 0` | :1451 |
| `awards` | `image` | `TEXT` | :1440 |
| `awards` | `monthly_nm` | `INTEGER DEFAULT 0` | :1456 |
| `awards` | `reward_nm` | `INTEGER DEFAULT 0` | :1455 |
| `buildings` | `required_status` | `TEXT` | :1183 |
| `clan_buildings` | `building_photo_file_id` | `TEXT` | :1859 |
| `clan_members` | `role` | `TEXT NOT NULL DEFAULT 'member'` | :1185 |
| `clans` | `tree_amber_at` | `TEXT DEFAULT NULL` | :1511 |
| `dungeon_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1362 |
| `dungeon_enemies` | `admin_tuned` | `INTEGER DEFAULT 0` | :1400 |
| `dungeon_enemies` | `armor` | `INTEGER DEFAULT 0` | :1358 |
| `dungeon_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1643 |
| `dungeon_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1644 |
| `dungeon_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1360 |
| `dungeon_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1361 |
| `dungeon_enemies` | `damage_max` | `INTEGER DEFAULT 0` | :1357 |
| `dungeon_enemies` | `damage_min` | `INTEGER DEFAULT 0` | :1356 |
| `dungeon_enemies` | `description` | `TEXT` | :1354 |
| `dungeon_enemies` | `dodge` | `INTEGER DEFAULT 0` | :1355 |
| `dungeon_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1359 |
| `dungeon_enemies` | `drops` | `TEXT DEFAULT '[]'` | :1350 |
| `dungeon_enemies` | `effect_resist` | `TEXT DEFAULT NULL` | :1397 |
| `dungeon_enemies` | `frostbite_chance` | `INTEGER DEFAULT 0` | :1645 |
| `dungeon_enemies` | `image` | `TEXT` | :1351 |
| `dungeon_enemies` | `poison_chance` | `INTEGER DEFAULT 0` | :1352 |
| `dungeon_enemies` | `poison_dmg` | `INTEGER DEFAULT 0` | :1353 |
| `dungeons` | `is_training` | `INTEGER DEFAULT 0` | :1633 |
| `dungeons` | `photo_dawn` | `TEXT` | :1413 |
| `dungeons` | `photo_day` | `TEXT` | :1414 |
| `dungeons` | `photo_night` | `TEXT` | :1416 |
| `dungeons` | `photo_rope` | `TEXT` | :1419 |
| `dungeons` | `photo_sunset` | `TEXT` | :1415 |
| `dungeons` | `photo_water` | `TEXT` | :1418 |
| `dungeons` | `rooms_map` | `TEXT` | :1650 |
| `fire_lab_sessions` | `boss_encounters` | `INTEGER DEFAULT 0` | :1866 |
| `fire_lab_sessions` | `effects_json` | `TEXT DEFAULT NULL` | :1865 |
| `fire_lab_sessions` | `enemy_json` | `TEXT DEFAULT NULL` | :1864 |
| `fire_lab_sessions` | `fish_used` | `INTEGER DEFAULT 0` | :1867 |
| `fire_lab_sessions` | `last_active_at` | `TIMESTAMP` | :1873 |
| `fire_lab_sessions` | `tree_open` | `INTEGER DEFAULT 0` | :1871 |
| `fire_lab_sessions` | `well_open` | `INTEGER DEFAULT 0` | :1869 |
| `firelab_enemies` | `armor` | `INTEGER DEFAULT 0` | :1863 |
| `firelab_enemies` | `on_hit_effects` | `TEXT DEFAULT NULL` | :1862 |
| `fish_catches` | `expires_at` | `TIMESTAMP` | :1501 |
| `fish_catches` | `kind` | `TEXT DEFAULT 'fish'` | :1656 |
| `fishing_enemies` | `armor` | `INTEGER DEFAULT 0` | :1373 |
| `fishing_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1371 |
| `fishing_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1372 |
| `forest_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1367 |
| `forest_enemies` | `armor` | `INTEGER DEFAULT 0` | :1363 |
| `forest_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1369 |
| `forest_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1370 |
| `forest_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1365 |
| `forest_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1366 |
| `forest_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1364 |
| `forest_mushrooms` | `zone` | `TEXT DEFAULT 'clearing'` | :1553 |
| `housing_slots` | `embedded` | `INTEGER DEFAULT 0` | :1584 |
| `inventory` | `expires_at` | `TIMESTAMP` | :1496 |
| `inventory` | `plant_data` | `TEXT` | :1498 |
| `inventory` | `shop_qty` | `INTEGER DEFAULT 0` | :1692 |
| `items` | `armor` | `INTEGER DEFAULT 0` | :1216 |
| `items` | `crit_chance` | `INTEGER DEFAULT 0` | :1219 |
| `items` | `crit_mult` | `REAL DEFAULT 0` | :1220 |
| `items` | `cure_frostbite` | `INTEGER DEFAULT 0` | :1647 |
| `items` | `cure_poison` | `INTEGER DEFAULT 0` | :1401 |
| `items` | `damage` | `INTEGER DEFAULT 0` | :1348 |
| `items` | `dodge_bonus` | `INTEGER DEFAULT 0` | :1680 |
| `items` | `dodge_buff_pct` | `INTEGER DEFAULT 0` | :1684 |
| `items` | `drink_effect` | `TEXT DEFAULT NULL` | :1484 |
| `items` | `equip_slot` | `TEXT` | :1222 |
| `items` | `heal` | `INTEGER DEFAULT 0` | :1349 |
| `items` | `heal_bonus_pct` | `INTEGER DEFAULT 0` | :1679 |
| `items` | `housing_slots` | `INTEGER` | :1811 |
| `items` | `housing_type` | `TEXT` | :1810 |
| `items` | `loot_only` | `INTEGER DEFAULT 0` | :1816 |
| `items` | `market_ok` | `INTEGER DEFAULT 0` | :1653 |
| `items` | `plant_name` | `TEXT` | :1663 |
| `items` | `regen` | `INTEGER DEFAULT 0` | :1411 |
| `items` | `regen_turns` | `INTEGER DEFAULT 0` | :1683 |
| `items` | `required_status` | `TEXT` | :1182 |
| `items` | `restock_enabled` | `INTEGER DEFAULT 0` | :1687 |
| `items` | `restock_target` | `INTEGER DEFAULT 0` | :1688 |
| `items` | `shop_limit` | `INTEGER DEFAULT 0` | :1691 |
| `items` | `weapon_effect` | `TEXT` | :1674 |
| `items` | `weapon_effect_chance` | `INTEGER DEFAULT 0` | :1675 |
| `items` | `weapon_effect_dmg` | `INTEGER DEFAULT 0` | :1676 |
| `locations` | `clearing_photo` | `TEXT DEFAULT NULL` | :1539 |
| `locations` | `fire_photo` | `TEXT DEFAULT NULL` | :1537 |
| `locations` | `glade_photo` | `TEXT DEFAULT NULL` | :1538 |
| `locations` | `logging_photo` | `TEXT DEFAULT NULL` | :1548 |
| `locations` | `mine_level_photo` | `TEXT DEFAULT NULL` | :1542 |
| `locations` | `photo_dawn` | `TEXT` | :1403 |
| `locations` | `photo_day` | `TEXT` | :1404 |
| `locations` | `photo_night` | `TEXT` | :1406 |
| `locations` | `photo_sunset` | `TEXT` | :1405 |
| `locations` | `preview_photo` | `TEXT` | :1402 |
| `locations` | `season_photos` | `TEXT DEFAULT NULL` | :1534 |
| `locations` | `storage_photo` | `TEXT DEFAULT NULL` | :1544 |
| `locations` | `visits` | `INTEGER DEFAULT 0` | :1408 |
| `logging_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1388 |
| `logging_enemies` | `armor` | `INTEGER DEFAULT 0` | :1384 |
| `logging_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1386 |
| `logging_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1387 |
| `logging_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1385 |
| `market_fish` | `base_price` | `INTEGER DEFAULT 0` | :1636 |
| `market_items` | `qty` | `INTEGER DEFAULT 1` | :1639 |
| `mine_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1379 |
| `mine_enemies` | `armor` | `INTEGER DEFAULT 0` | :1375 |
| `mine_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1380 |
| `mine_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1381 |
| `mine_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1377 |
| `mine_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1378 |
| `mine_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1376 |
| `nii_reports` | `photo2_file_id` | `TEXT DEFAULT NULL` | :1466 |
| `player_dungeon_run` | `loot_nm` | `INTEGER DEFAULT 0` | :1335 |
| `player_dungeon_run` | `started_at` | `TIMESTAMP DEFAULT CURRENT_TIMESTAMP` | :1336 |
| `player_housing` | `expansions_installed` | `INTEGER DEFAULT 0` | :1586 |
| `player_housing` | `housing_label` | `TEXT` | :1812 |
| `player_housing` | `housing_slots` | `INTEGER` | :1813 |
| `player_housing` | `tax_last_check` | `TEXT DEFAULT NULL` | :1637 |
| `player_housing` | `tax_unpaid_months` | `INTEGER DEFAULT 0` | :1638 |
| `polls` | `archived_day` | `TEXT DEFAULT ''` | :1602 |
| `polls` | `closed_at` | `TIMESTAMP` | :1494 |
| `polls` | `closed_by` | `INTEGER` | :1493 |
| `polls` | `closes_at` | `TIMESTAMP` | :1591 |
| `polls` | `is_archived` | `INTEGER DEFAULT 0` | :1601 |
| `reports` | `credited_troops` | `INTEGER` | :1227 |
| `reports` | `paid` | `INTEGER DEFAULT 0` | :1234 |
| `reports` | `reject_reason` | `TEXT` | :1240 |
| `reports` | `reviewed_at` | `TEXT` | :1244 |
| `reports` | `reviewed_by_name` | `TEXT` | :1241 |
| `reports` | `total_troops` | `INTEGER DEFAULT 0` | :1225 |
| `statuses` | `sort_order` | `INTEGER DEFAULT 0` | :1184 |
| `users` | `about` | `TEXT DEFAULT ''` | :1210 |
| `users` | `alcohol_strong_used_day` | `TEXT DEFAULT NULL` | :1488 |
| `users` | `alcohol_strong_used_today` | `INTEGER DEFAULT 0` | :1487 |
| `users` | `alcohol_weak_used_day` | `TEXT DEFAULT NULL` | :1486 |
| `users` | `alcohol_weak_used_today` | `INTEGER DEFAULT 0` | :1485 |
| `users` | `ap_recovery_day` | `TEXT DEFAULT NULL` | :1480 |
| `users` | `ap_restored_day` | `TEXT DEFAULT NULL` | :1339 |
| `users` | `ap_restored_today` | `INTEGER DEFAULT 0` | :1340 |
| `users` | `beer_used_day` | `TEXT DEFAULT NULL` | :1483 |
| `users` | `beer_used_today` | `INTEGER DEFAULT 0` | :1482 |
| `users` | `callsign` | `TEXT` | :1426 |
| `users` | `callsign_free_used` | `INTEGER DEFAULT 0` | :1635 |
| `users` | `dodge_buff_pct` | `INTEGER DEFAULT 0` | :1707 |
| `users` | `dodge_buff_until` | `TEXT DEFAULT NULL` | :1706 |
| `users` | `duel_losses` | `INTEGER DEFAULT 0` | :1344 |
| `users` | `duel_rating` | `INTEGER DEFAULT 0` | :1342 |
| `users` | `duel_wins` | `INTEGER DEFAULT 0` | :1343 |
| `users` | `equipment` | `TEXT DEFAULT '{}'` | :1211 |
| `users` | `fish_sold_day` | `TEXT DEFAULT NULL` | :1515 |
| `users` | `fish_sold_today` | `INTEGER DEFAULT 0` | :1516 |
| `users` | `fishing_bait` | `TEXT DEFAULT ''` | :1424 |
| `users` | `forest_attempts_since_boar` | `INTEGER DEFAULT 0` | :1518 |
| `users` | `forest_attempts_since_wolf` | `INTEGER DEFAULT 0` | :1520 |
| `users` | `forest_sold_day` | `TEXT DEFAULT NULL` | :1530 |
| `users` | `forest_sold_today` | `INTEGER DEFAULT 0` | :1531 |
| `users` | `fountain_used_day` | `TEXT DEFAULT NULL` | :1503 |
| `users` | `fountain_used_today` | `INTEGER DEFAULT 0` | :1504 |
| `users` | `lang` | `TEXT DEFAULT 'ru'` | :1188 |
| `users` | `lantern_amber_at` | `TEXT DEFAULT NULL` | :1509 |
| `users` | `lantern_medit_day` | `TEXT DEFAULT NULL` | :1508 |
| `users` | `last_active` | `REAL DEFAULT 0` | :1347 |
| `users` | `last_salary_date` | `TIMESTAMP` | :1214 |
| `users` | `legioner` | `INTEGER DEFAULT 0` | :1753 |
| `users` | `logging_attempts_since_owl` | `INTEGER DEFAULT 0` | :1527 |
| `users` | `logging_attempts_since_snake` | `INTEGER DEFAULT 0` | :1526 |
| `users` | `market_license_expires` | `TEXT DEFAULT NULL` | :1634 |
| `users` | `mine_attempts_since_bat` | `INTEGER DEFAULT 0` | :1523 |
| `users` | `notify_enabled` | `INTEGER DEFAULT 1` | :1208 |
| `users` | `profile_public` | `INTEGER DEFAULT 1` | :1209 |
| `users` | `promoted_rank` | `TEXT` | :1187 |
| `users` | `salary` | `INTEGER DEFAULT 0` | :1212 |
| `users` | `salary_debt` | `INTEGER DEFAULT 0` | :1215 |
| `users` | `salary_period_days` | `INTEGER DEFAULT 7` | :1213 |
| `users` | `seaweed_used_day` | `TEXT DEFAULT NULL` | :1477 |
| `users` | `seaweed_used_today` | `INTEGER DEFAULT 0` | :1476 |
| `users` | `shower_used_day` | `TEXT DEFAULT NULL` | :1506 |
| `users` | `shower_used_today` | `INTEGER DEFAULT 0` | :1513 |
| `users` | `special_blocked_until` | `TEXT DEFAULT NULL` | :1491 |
| `users` | `special_fails_today` | `INTEGER DEFAULT 0` | :1490 |
| `users` | `wing` | `TEXT` | :1750 |
| `users` | `xp_balance` | `INTEGER DEFAULT 0` | :1192 |
| `water_fish` | `excluded` | `INTEGER DEFAULT 0` | :1422 |
| `water_fish` | `kind` | `TEXT DEFAULT 'fish'` | :1657 |
| `water_fish` | `super_rare` | `INTEGER DEFAULT 0` | :1660 |
| `wings` | `abbr` | `TEXT DEFAULT ''` | :1470 |
| `wings` | `callsign` | `TEXT DEFAULT ''` | :1472 |
| `wings` | `emoji` | `TEXT DEFAULT ''` | :1473 |
| `wings` | `name` | `TEXT DEFAULT ''` | :1471 |
| `wings` | `num` | `TEXT DEFAULT ''` | :1469 |
| `wings` | `sort_order` | `INTEGER DEFAULT 0` | :1474 |

## 2. Идемпотентные засевы и миграции данных

| Функция | Вызывается из main.py | Назначение (первая строка docstring) | db.py |
|---|---|---|---|
| `backfill_rank_statuses` | — | Разово выдать статусы по текущим званиям всех пилотов (войска и админ-звания). | :6729 |
| `ensure_achievements` | ✅ | Идемпотентно засевает награды-уровни достижений и синхронизирует их. | :14669 |
| `ensure_base_status` | — | Базовый статус «Турист» для каждого нового игрока. | :7112 |
| `ensure_base_statuses` | — | Создаёт базовые статусы иерархии, если их нет. | :7067 |
| `ensure_berry_candy_recipe` | — | Рецепт «Леденец из ягод»: черника + малина + сахар. Создаётся скрытым: | :10673 |
| `ensure_clan_building` | — | — | :16778 |
| `ensure_clan_cape_item` | — | Клановая накидка: экипировка слота «Клановая накидка». Продаётся в клановой | :10655 |
| `ensure_duel_items` | ✅ | Товары Дома Дуэлей: дуэльные перчатки (отдельный слот) и клубная карта. | :12157 |
| `ensure_dungeon_enemy_drops` | ✅ | Синхронизирует врагов существующего данжа с DEFAULT_DUNGEON (дропы, HP, награды, | :14119 |
| `ensure_dungeon_reservoir_items` | ✅ | Идемпотентно добавляет предметы водохранилища подземелья (v0.12.0). | :14042 |
| `ensure_dungeon_shop_items` | ✅ | Идемпотентно добавляет предметы данжа (зелье в магазин, трофеи) — для существующих БД. | :13650 |
| `ensure_fire_mushroom_pool` | — | Огненный гриб — на прогалину с весом 15; по 1 снимаем с пяти самых редких грибов. Один раз. | :10531 |
| `ensure_fire_tree_items` | — | Предметы пожертвования и талисмана: скрыты, без цены продажи, не на рынке. | :10464 |
| `ensure_firelab_enemies` | ✅ | Идемпотентно засевает врагов Огненного Лабиринта (4 обычных + босс). | :10778 |
| `ensure_firelab_items` | ✅ | Идемпотентно создаёт предметы Фазы 3 «Дней Пламенного Круговорота». | :10826 |
| `ensure_fishing_enemies` | ✅ | Идемпотентно засевает врагов рыбалки (мутировавший моллюск) из MOLLUSK_SEED. | :11100 |
| `ensure_forest_berry_items` | — | Ягоды (горсть) и шкура медведя: предметы-ресурсы вне магазина. Идемпотентно. | :10635 |
| `ensure_forest_berry_pool` | — | Таблица ягод поиска по зонам (как у грибов): шансы правит админ. Засев — один раз. | :10502 |
| `ensure_forest_enemies` | ✅ | Идемпотентно засевает врагов леса (кабан и Белый Волк Севера). | :10746 |
| `ensure_forest_items` | ✅ | Идемпотентно создаёт предметы леса (грибы, добыча кабана, жареные блюда, яд). | :9692 |
| `ensure_forest_mushrooms` | ✅ | Идемпотентно засевает пул грибов леса из FOREST_DEFAULTS. | :9864 |
| `ensure_forest_zones` | ✅ | Разовый перенос старого пула леса в зону поляны и засев пула опушки. | :10107 |
| `ensure_item_rarity_unified` | ✅ | Идемпотентно применяет единую градацию редкости (v0.43.10). | :2171 |
| `ensure_kvp_award` | ✅ | — | :12416 |
| `ensure_kvp_items` | ✅ | Обеспечивает эксклюзивный предмет К.В.П. — «Сержантскую трость». | :12130 |
| `ensure_kvp_user` | — | Гарантирует наличие строки прогресса К.В.П. для игрока. | :12658 |
| `ensure_life_items` | ✅ | Идемпотентно добавляет предметы жилья, мебели, семян, ресурсов и продовольствия. | :13866 |
| `ensure_logging_enemies` | ✅ | Идемпотентно засевает врагов Лесозаготовки (Змея и Неясыть). | :9853 |
| `ensure_logging_items` | ✅ | Идемпотентно создаёт предметы Лесозаготовки (топор, бревна, дропы). | :9810 |
| `ensure_market_license_item` | ✅ | Идемпотентно добавляет «Торговую лицензию» в магазин. | :11680 |
| `ensure_mine_enemies` | ✅ | Идемпотентно засевает врагов копи (Летучая мышь) из MINE_BAT_SEED. | :9801 |
| `ensure_mine_items` | ✅ | Идемпотентно создаёт предметы Железной копи (кирка, руда, самоцветы). | :9770 |
| `ensure_mollusk_items` | ✅ | Идемпотентно создаёт предметы моллюска (из его добычи и готового блюда). | :11106 |
| `ensure_passport_item` | ✅ | Создаёт предмет «Паспорт Нордхайма» (категория «Документы»), если его нет. | :12489 |
| `ensure_player_housing` | — | Возвращает жильё игрока, создавая муниципальную квартиру для пилота при первом обращении. | :14264 |
| `ensure_rank_statuses_for_troops` | — | Выдать статус по текущему званию игрока (по войскам или админ-назначению). | :6717 |
| `ensure_recipe_shop_item` | — | Синхронизирует товар-рецепт «Рецепт: <name>» с рецептом (менеджер). | :15104 |
| `ensure_recipe_shop_items` | ✅ | Создаёт в магазине предметы-рецепты категории 'recipes'. | :16454 |
| `ensure_recipes` | ✅ | Идемпотентно засевает рецепты и синхронизирует уже существующие. | :14954 |
| `ensure_tourist_booklet` | ✅ | Создаёт предмет «Буклет туриста» и награду «Опытный турист», если их нет. | :12452 |
| `ensure_user_recipes_backfill` | ✅ | Разово открывает все рецепты существующим игрокам. | :16604 |
| `ensure_water_fish` | ✅ | Идемпотентно засевает water_fish из дефолтов. Правившие админом строки | :9202 |
| `migrate_legacy_junk` | ✅ | Переносит старые копии мусора (сапог, водоросли) из инвентаря в улов. | :9044 |
| `seed_default_items` | ✅ | Заполняет магазин базовым набором товаров, если он пуст и не было своих товаров. | :11853 |
| `seed_dungeon` | ✅ | — | :12008 |
| `seed_kvp` | ✅ | Создаёт тренировочный данж К.В.П. с врагами (Ефрейтор, Старший сержант), если его нет. | :12079 |
| `seed_locations` | — | Засеивает базовые локации города (Ратуша, Библиотека) как пример управляемого доступа. | :1963 |

## 3. Отдельные скрипты миграций

- `migrate_113.py` — Проверка миграций 0.19.0 на чистой БД: колонки polls, таблица rep_speeches.
- `migrate_113_old.py` — Миграция 0.19.0 поверх БД со старой схемой polls (без closes_at/is_archived).

