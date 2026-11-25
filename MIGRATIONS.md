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
| `awards` | `achievement_key` | `TEXT DEFAULT NULL` | :1489 |
| `awards` | `achievement_level` | `INTEGER DEFAULT 0` | :1490 |
| `awards` | `bonus_attack` | `INTEGER DEFAULT 0` | :1468 |
| `awards` | `bonus_crit` | `INTEGER DEFAULT 0` | :1475 |
| `awards` | `bonus_defense` | `INTEGER DEFAULT 0` | :1469 |
| `awards` | `bonus_dodge` | `INTEGER DEFAULT 0` | :1470 |
| `awards` | `bonus_fishing` | `INTEGER DEFAULT 0` | :1471 |
| `awards` | `bonus_hp` | `INTEGER DEFAULT 0` | :1472 |
| `awards` | `bonus_json` | `TEXT DEFAULT '{}'` | :1491 |
| `awards` | `bonus_report_tax` | `INTEGER DEFAULT 0` | :1479 |
| `awards` | `bonus_shop_discount` | `INTEGER DEFAULT 0` | :1478 |
| `awards` | `image` | `TEXT` | :1467 |
| `awards` | `monthly_nm` | `INTEGER DEFAULT 0` | :1483 |
| `awards` | `reward_nm` | `INTEGER DEFAULT 0` | :1482 |
| `buildings` | `required_status` | `TEXT` | :1210 |
| `clan_buildings` | `building_photo_file_id` | `TEXT` | :1891 |
| `clan_members` | `role` | `TEXT NOT NULL DEFAULT 'member'` | :1212 |
| `clans` | `tree_amber_at` | `TEXT DEFAULT NULL` | :1538 |
| `dungeon_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1389 |
| `dungeon_enemies` | `admin_tuned` | `INTEGER DEFAULT 0` | :1427 |
| `dungeon_enemies` | `armor` | `INTEGER DEFAULT 0` | :1385 |
| `dungeon_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1670 |
| `dungeon_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1671 |
| `dungeon_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1387 |
| `dungeon_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1388 |
| `dungeon_enemies` | `damage_max` | `INTEGER DEFAULT 0` | :1384 |
| `dungeon_enemies` | `damage_min` | `INTEGER DEFAULT 0` | :1383 |
| `dungeon_enemies` | `description` | `TEXT` | :1381 |
| `dungeon_enemies` | `dodge` | `INTEGER DEFAULT 0` | :1382 |
| `dungeon_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1386 |
| `dungeon_enemies` | `drops` | `TEXT DEFAULT '[]'` | :1377 |
| `dungeon_enemies` | `effect_resist` | `TEXT DEFAULT NULL` | :1424 |
| `dungeon_enemies` | `frostbite_chance` | `INTEGER DEFAULT 0` | :1672 |
| `dungeon_enemies` | `image` | `TEXT` | :1378 |
| `dungeon_enemies` | `poison_chance` | `INTEGER DEFAULT 0` | :1379 |
| `dungeon_enemies` | `poison_dmg` | `INTEGER DEFAULT 0` | :1380 |
| `dungeons` | `is_training` | `INTEGER DEFAULT 0` | :1660 |
| `dungeons` | `photo_dawn` | `TEXT` | :1440 |
| `dungeons` | `photo_day` | `TEXT` | :1441 |
| `dungeons` | `photo_night` | `TEXT` | :1443 |
| `dungeons` | `photo_rope` | `TEXT` | :1446 |
| `dungeons` | `photo_sunset` | `TEXT` | :1442 |
| `dungeons` | `photo_water` | `TEXT` | :1445 |
| `dungeons` | `rooms_map` | `TEXT` | :1677 |
| `fire_lab_sessions` | `boss_encounters` | `INTEGER DEFAULT 0` | :1898 |
| `fire_lab_sessions` | `effects_json` | `TEXT DEFAULT NULL` | :1897 |
| `fire_lab_sessions` | `enemy_json` | `TEXT DEFAULT NULL` | :1896 |
| `fire_lab_sessions` | `fish_used` | `INTEGER DEFAULT 0` | :1899 |
| `fire_lab_sessions` | `last_active_at` | `TIMESTAMP` | :1905 |
| `fire_lab_sessions` | `tree_open` | `INTEGER DEFAULT 0` | :1903 |
| `fire_lab_sessions` | `well_open` | `INTEGER DEFAULT 0` | :1901 |
| `firelab_enemies` | `armor` | `INTEGER DEFAULT 0` | :1895 |
| `firelab_enemies` | `on_hit_effects` | `TEXT DEFAULT NULL` | :1894 |
| `fish_catches` | `expires_at` | `TIMESTAMP` | :1528 |
| `fish_catches` | `kind` | `TEXT DEFAULT 'fish'` | :1683 |
| `fishing_enemies` | `armor` | `INTEGER DEFAULT 0` | :1400 |
| `fishing_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1398 |
| `fishing_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1399 |
| `forest_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1394 |
| `forest_enemies` | `armor` | `INTEGER DEFAULT 0` | :1390 |
| `forest_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1396 |
| `forest_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1397 |
| `forest_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1392 |
| `forest_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1393 |
| `forest_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1391 |
| `forest_mushrooms` | `zone` | `TEXT DEFAULT 'clearing'` | :1580 |
| `housing_slots` | `embedded` | `INTEGER DEFAULT 0` | :1611 |
| `inventory` | `expires_at` | `TIMESTAMP` | :1523 |
| `inventory` | `plant_data` | `TEXT` | :1525 |
| `inventory` | `shop_qty` | `INTEGER DEFAULT 0` | :1719 |
| `items` | `armor` | `INTEGER DEFAULT 0` | :1243 |
| `items` | `crit_chance` | `INTEGER DEFAULT 0` | :1246 |
| `items` | `crit_mult` | `REAL DEFAULT 0` | :1247 |
| `items` | `cure_frostbite` | `INTEGER DEFAULT 0` | :1674 |
| `items` | `cure_poison` | `INTEGER DEFAULT 0` | :1428 |
| `items` | `damage` | `INTEGER DEFAULT 0` | :1375 |
| `items` | `dodge_bonus` | `INTEGER DEFAULT 0` | :1707 |
| `items` | `dodge_buff_pct` | `INTEGER DEFAULT 0` | :1711 |
| `items` | `drink_effect` | `TEXT DEFAULT NULL` | :1511 |
| `items` | `equip_slot` | `TEXT` | :1249 |
| `items` | `heal` | `INTEGER DEFAULT 0` | :1376 |
| `items` | `heal_bonus_pct` | `INTEGER DEFAULT 0` | :1706 |
| `items` | `housing_slots` | `INTEGER` | :1838 |
| `items` | `housing_type` | `TEXT` | :1837 |
| `items` | `loot_only` | `INTEGER DEFAULT 0` | :1843 |
| `items` | `market_ok` | `INTEGER DEFAULT 0` | :1680 |
| `items` | `plant_name` | `TEXT` | :1690 |
| `items` | `regen` | `INTEGER DEFAULT 0` | :1438 |
| `items` | `regen_turns` | `INTEGER DEFAULT 0` | :1710 |
| `items` | `required_status` | `TEXT` | :1209 |
| `items` | `restock_enabled` | `INTEGER DEFAULT 0` | :1714 |
| `items` | `restock_target` | `INTEGER DEFAULT 0` | :1715 |
| `items` | `shop_limit` | `INTEGER DEFAULT 0` | :1718 |
| `items` | `weapon_effect` | `TEXT` | :1701 |
| `items` | `weapon_effect_chance` | `INTEGER DEFAULT 0` | :1702 |
| `items` | `weapon_effect_dmg` | `INTEGER DEFAULT 0` | :1703 |
| `locations` | `clearing_photo` | `TEXT DEFAULT NULL` | :1566 |
| `locations` | `fire_photo` | `TEXT DEFAULT NULL` | :1564 |
| `locations` | `glade_photo` | `TEXT DEFAULT NULL` | :1565 |
| `locations` | `logging_photo` | `TEXT DEFAULT NULL` | :1575 |
| `locations` | `mine_level_photo` | `TEXT DEFAULT NULL` | :1569 |
| `locations` | `photo_dawn` | `TEXT` | :1430 |
| `locations` | `photo_day` | `TEXT` | :1431 |
| `locations` | `photo_night` | `TEXT` | :1433 |
| `locations` | `photo_sunset` | `TEXT` | :1432 |
| `locations` | `preview_photo` | `TEXT` | :1429 |
| `locations` | `season_photos` | `TEXT DEFAULT NULL` | :1561 |
| `locations` | `storage_photo` | `TEXT DEFAULT NULL` | :1571 |
| `locations` | `visits` | `INTEGER DEFAULT 0` | :1435 |
| `logging_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1415 |
| `logging_enemies` | `armor` | `INTEGER DEFAULT 0` | :1411 |
| `logging_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1413 |
| `logging_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1414 |
| `logging_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1412 |
| `market_fish` | `base_price` | `INTEGER DEFAULT 0` | :1663 |
| `market_items` | `qty` | `INTEGER DEFAULT 1` | :1666 |
| `mine_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1406 |
| `mine_enemies` | `armor` | `INTEGER DEFAULT 0` | :1402 |
| `mine_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1407 |
| `mine_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1408 |
| `mine_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1404 |
| `mine_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1405 |
| `mine_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1403 |
| `nii_reports` | `photo2_file_id` | `TEXT DEFAULT NULL` | :1493 |
| `player_dungeon_run` | `loot_nm` | `INTEGER DEFAULT 0` | :1362 |
| `player_dungeon_run` | `started_at` | `TIMESTAMP DEFAULT CURRENT_TIMESTAMP` | :1363 |
| `player_housing` | `expansions_installed` | `INTEGER DEFAULT 0` | :1613 |
| `player_housing` | `housing_label` | `TEXT` | :1839 |
| `player_housing` | `housing_slots` | `INTEGER` | :1840 |
| `player_housing` | `tax_last_check` | `TEXT DEFAULT NULL` | :1664 |
| `player_housing` | `tax_unpaid_months` | `INTEGER DEFAULT 0` | :1665 |
| `polls` | `archived_day` | `TEXT DEFAULT ''` | :1629 |
| `polls` | `closed_at` | `TIMESTAMP` | :1521 |
| `polls` | `closed_by` | `INTEGER` | :1520 |
| `polls` | `closes_at` | `TIMESTAMP` | :1618 |
| `polls` | `is_archived` | `INTEGER DEFAULT 0` | :1628 |
| `reports` | `credited_troops` | `INTEGER` | :1254 |
| `reports` | `paid` | `INTEGER DEFAULT 0` | :1261 |
| `reports` | `reject_reason` | `TEXT` | :1267 |
| `reports` | `reviewed_at` | `TEXT` | :1271 |
| `reports` | `reviewed_by_name` | `TEXT` | :1268 |
| `reports` | `total_troops` | `INTEGER DEFAULT 0` | :1252 |
| `statuses` | `sort_order` | `INTEGER DEFAULT 0` | :1211 |
| `users` | `about` | `TEXT DEFAULT ''` | :1237 |
| `users` | `alcohol_strong_used_day` | `TEXT DEFAULT NULL` | :1515 |
| `users` | `alcohol_strong_used_today` | `INTEGER DEFAULT 0` | :1514 |
| `users` | `alcohol_weak_used_day` | `TEXT DEFAULT NULL` | :1513 |
| `users` | `alcohol_weak_used_today` | `INTEGER DEFAULT 0` | :1512 |
| `users` | `ap_recovery_day` | `TEXT DEFAULT NULL` | :1507 |
| `users` | `ap_restored_day` | `TEXT DEFAULT NULL` | :1366 |
| `users` | `ap_restored_today` | `INTEGER DEFAULT 0` | :1367 |
| `users` | `beer_used_day` | `TEXT DEFAULT NULL` | :1510 |
| `users` | `beer_used_today` | `INTEGER DEFAULT 0` | :1509 |
| `users` | `callsign` | `TEXT` | :1453 |
| `users` | `callsign_free_used` | `INTEGER DEFAULT 0` | :1662 |
| `users` | `dodge_buff_pct` | `INTEGER DEFAULT 0` | :1734 |
| `users` | `dodge_buff_until` | `TEXT DEFAULT NULL` | :1733 |
| `users` | `duel_losses` | `INTEGER DEFAULT 0` | :1371 |
| `users` | `duel_rating` | `INTEGER DEFAULT 0` | :1369 |
| `users` | `duel_wins` | `INTEGER DEFAULT 0` | :1370 |
| `users` | `equipment` | `TEXT DEFAULT '{}'` | :1238 |
| `users` | `fish_sold_day` | `TEXT DEFAULT NULL` | :1542 |
| `users` | `fish_sold_today` | `INTEGER DEFAULT 0` | :1543 |
| `users` | `fishing_bait` | `TEXT DEFAULT ''` | :1451 |
| `users` | `forest_attempts_since_boar` | `INTEGER DEFAULT 0` | :1545 |
| `users` | `forest_attempts_since_wolf` | `INTEGER DEFAULT 0` | :1547 |
| `users` | `forest_sold_day` | `TEXT DEFAULT NULL` | :1557 |
| `users` | `forest_sold_today` | `INTEGER DEFAULT 0` | :1558 |
| `users` | `fountain_used_day` | `TEXT DEFAULT NULL` | :1530 |
| `users` | `fountain_used_today` | `INTEGER DEFAULT 0` | :1531 |
| `users` | `lang` | `TEXT DEFAULT 'ru'` | :1215 |
| `users` | `lantern_amber_at` | `TEXT DEFAULT NULL` | :1536 |
| `users` | `lantern_medit_day` | `TEXT DEFAULT NULL` | :1535 |
| `users` | `last_active` | `REAL DEFAULT 0` | :1374 |
| `users` | `last_salary_date` | `TIMESTAMP` | :1241 |
| `users` | `legioner` | `INTEGER DEFAULT 0` | :1780 |
| `users` | `logging_attempts_since_owl` | `INTEGER DEFAULT 0` | :1554 |
| `users` | `logging_attempts_since_snake` | `INTEGER DEFAULT 0` | :1553 |
| `users` | `market_license_expires` | `TEXT DEFAULT NULL` | :1661 |
| `users` | `mine_attempts_since_bat` | `INTEGER DEFAULT 0` | :1550 |
| `users` | `notify_enabled` | `INTEGER DEFAULT 1` | :1235 |
| `users` | `profile_public` | `INTEGER DEFAULT 1` | :1236 |
| `users` | `promoted_rank` | `TEXT` | :1214 |
| `users` | `salary` | `INTEGER DEFAULT 0` | :1239 |
| `users` | `salary_debt` | `INTEGER DEFAULT 0` | :1242 |
| `users` | `salary_period_days` | `INTEGER DEFAULT 7` | :1240 |
| `users` | `seaweed_used_day` | `TEXT DEFAULT NULL` | :1504 |
| `users` | `seaweed_used_today` | `INTEGER DEFAULT 0` | :1503 |
| `users` | `shower_used_day` | `TEXT DEFAULT NULL` | :1533 |
| `users` | `shower_used_today` | `INTEGER DEFAULT 0` | :1540 |
| `users` | `special_blocked_until` | `TEXT DEFAULT NULL` | :1518 |
| `users` | `special_fails_today` | `INTEGER DEFAULT 0` | :1517 |
| `users` | `wing` | `TEXT` | :1777 |
| `users` | `xp_balance` | `INTEGER DEFAULT 0` | :1219 |
| `water_fish` | `excluded` | `INTEGER DEFAULT 0` | :1449 |
| `water_fish` | `kind` | `TEXT DEFAULT 'fish'` | :1684 |
| `water_fish` | `super_rare` | `INTEGER DEFAULT 0` | :1687 |
| `wings` | `abbr` | `TEXT DEFAULT ''` | :1497 |
| `wings` | `callsign` | `TEXT DEFAULT ''` | :1499 |
| `wings` | `emoji` | `TEXT DEFAULT ''` | :1500 |
| `wings` | `name` | `TEXT DEFAULT ''` | :1498 |
| `wings` | `num` | `TEXT DEFAULT ''` | :1496 |
| `wings` | `sort_order` | `INTEGER DEFAULT 0` | :1501 |

## 2. Идемпотентные засевы и миграции данных

| Функция | Вызывается из main.py | Назначение (первая строка docstring) | db.py |
|---|---|---|---|
| `backfill_rank_statuses` | — | Разово выдать статусы по текущим званиям всех пилотов (войска и админ-звания). | :6916 |
| `ensure_achievements` | ✅ | Идемпотентно засевает награды-уровни достижений и синхронизирует их. | :14937 |
| `ensure_base_status` | — | Базовый статус «Турист» для каждого нового игрока. | :7299 |
| `ensure_base_statuses` | — | Создаёт базовые статусы иерархии, если их нет. | :7254 |
| `ensure_berry_candy_recipe` | — | Рецепт «Леденец из ягод»: черника + малина + сахар. Создаётся скрытым: | :10905 |
| `ensure_clan_building` | — | — | :17050 |
| `ensure_clan_cape_item` | — | Клановая накидка: экипировка слота «Клановая накидка». Продаётся в клановой | :10887 |
| `ensure_duel_items` | ✅ | Товары Дома Дуэлей: дуэльные перчатки (отдельный слот) и клубная карта. | :12389 |
| `ensure_dungeon_enemy_drops` | ✅ | Синхронизирует врагов существующего данжа с DEFAULT_DUNGEON (дропы, HP, награды, | :14388 |
| `ensure_dungeon_reservoir_items` | ✅ | Идемпотентно добавляет предметы водохранилища подземелья (v0.12.0). | :14311 |
| `ensure_dungeon_shop_items` | ✅ | Идемпотентно добавляет предметы данжа (зелье в магазин, трофеи) — для существующих БД. | :13919 |
| `ensure_fire_mushroom_pool` | — | Огненный гриб — на прогалину с весом 15; по 1 снимаем с пяти самых редких грибов. Один раз. | :10763 |
| `ensure_fire_tree_items` | — | Предметы пожертвования и талисмана: скрыты, без цены продажи, не на рынке. | :10696 |
| `ensure_firelab_enemies` | ✅ | Идемпотентно засевает врагов Огненного Лабиринта (4 обычных + босс). | :11010 |
| `ensure_firelab_items` | ✅ | Идемпотентно создаёт предметы Фазы 3 «Дней Пламенного Круговорота». | :11058 |
| `ensure_fishing_enemies` | ✅ | Идемпотентно засевает врагов рыбалки (мутировавший моллюск) из MOLLUSK_SEED. | :11332 |
| `ensure_forest_berry_items` | — | Ягоды (горсть) и шкура медведя: предметы-ресурсы вне магазина. Идемпотентно. | :10867 |
| `ensure_forest_berry_pool` | — | Таблица ягод поиска по зонам (как у грибов): шансы правит админ. Засев — один раз. | :10734 |
| `ensure_forest_enemies` | ✅ | Идемпотентно засевает врагов леса (кабан и Белый Волк Севера). | :10978 |
| `ensure_forest_items` | ✅ | Идемпотентно создаёт предметы леса (грибы, добыча кабана, жареные блюда, яд). | :9923 |
| `ensure_forest_mushrooms` | ✅ | Идемпотентно засевает пул грибов леса из FOREST_DEFAULTS. | :10096 |
| `ensure_forest_zones` | ✅ | Разовый перенос старого пула леса в зону поляны и засев пула опушки. | :10339 |
| `ensure_item_rarity_unified` | ✅ | Идемпотентно применяет единую градацию редкости (v0.43.10). | :2289 |
| `ensure_kvp_award` | ✅ | — | :12648 |
| `ensure_kvp_items` | ✅ | Обеспечивает эксклюзивный предмет К.В.П. — «Сержантскую трость». | :12362 |
| `ensure_kvp_user` | — | Гарантирует наличие строки прогресса К.В.П. для игрока. | :12927 |
| `ensure_life_items` | ✅ | Идемпотентно добавляет предметы жилья, мебели, семян, ресурсов и продовольствия. | :14135 |
| `ensure_logging_enemies` | ✅ | Идемпотентно засевает врагов Лесозаготовки (Змея и Неясыть). | :10085 |
| `ensure_logging_items` | ✅ | Идемпотентно создаёт предметы Лесозаготовки (топор, бревна, дропы). | :10042 |
| `ensure_market_license_item` | ✅ | Идемпотентно добавляет «Торговую лицензию» в магазин. | :11912 |
| `ensure_mine_enemies` | ✅ | Идемпотентно засевает врагов копи (Летучая мышь) из MINE_BAT_SEED. | :10033 |
| `ensure_mine_items` | ✅ | Идемпотентно создаёт предметы Железной копи (кирка, руда, самоцветы). | :10001 |
| `ensure_mollusk_items` | ✅ | Идемпотентно создаёт предметы моллюска (из его добычи и готового блюда). | :11338 |
| `ensure_passport_item` | ✅ | Создаёт предмет «Паспорт Нордхайма» (категория «Документы»), если его нет. | :12721 |
| `ensure_player_housing` | — | Возвращает жильё игрока, создавая муниципальную квартиру для пилота при первом обращении. | :14533 |
| `ensure_rank_statuses_for_troops` | — | Выдать статус по текущему званию игрока (по войскам или админ-назначению). | :6904 |
| `ensure_recipe_shop_item` | — | Синхронизирует товар-рецепт «Рецепт: <name>» с рецептом (менеджер). | :15372 |
| `ensure_recipe_shop_items` | ✅ | Создаёт в магазине предметы-рецепты категории 'recipes'. | :16726 |
| `ensure_recipes` | ✅ | Идемпотентно засевает рецепты и синхронизирует уже существующие. | :15222 |
| `ensure_tourist_booklet` | ✅ | Создаёт предмет «Буклет туриста» и награду «Опытный турист», если их нет. | :12684 |
| `ensure_user_recipes_backfill` | ✅ | Разово открывает все рецепты существующим игрокам. | :16876 |
| `ensure_water_fish` | ✅ | Идемпотентно засевает water_fish из дефолтов. Правившие админом строки | :9433 |
| `migrate_legacy_junk` | ✅ | Переносит старые копии мусора (сапог, водоросли) из инвентаря в улов. | :9275 |
| `seed_default_items` | ✅ | Заполняет магазин базовым набором товаров, если он пуст и не было своих товаров. | :12085 |
| `seed_dungeon` | ✅ | — | :12240 |
| `seed_kvp` | ✅ | Создаёт тренировочный данж К.В.П. с врагами (Ефрейтор, Старший сержант), если его нет. | :12311 |
| `seed_locations` | — | Засеивает базовые локации города (Ратуша, Библиотека) как пример управляемого доступа. | :2081 |

## 3. Отдельные скрипты миграций

- `migrate_113.py` — Проверка миграций 0.19.0 на чистой БД: колонки polls, таблица rep_speeches.
- `migrate_113_old.py` — Миграция 0.19.0 поверх БД со старой схемой polls (без closes_at/is_archived).

