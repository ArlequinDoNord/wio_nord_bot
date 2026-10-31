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

Всего вызовов: **191**; таблиц: **29**.

| Таблица | Колонка | Тип / значение по умолчанию | db.py |
|---|---|---|---|
| `awards` | `achievement_key` | `TEXT DEFAULT NULL` | :1401 |
| `awards` | `achievement_level` | `INTEGER DEFAULT 0` | :1402 |
| `awards` | `bonus_attack` | `INTEGER DEFAULT 0` | :1380 |
| `awards` | `bonus_crit` | `INTEGER DEFAULT 0` | :1387 |
| `awards` | `bonus_defense` | `INTEGER DEFAULT 0` | :1381 |
| `awards` | `bonus_dodge` | `INTEGER DEFAULT 0` | :1382 |
| `awards` | `bonus_fishing` | `INTEGER DEFAULT 0` | :1383 |
| `awards` | `bonus_hp` | `INTEGER DEFAULT 0` | :1384 |
| `awards` | `bonus_json` | `TEXT DEFAULT '{}'` | :1403 |
| `awards` | `bonus_report_tax` | `INTEGER DEFAULT 0` | :1391 |
| `awards` | `bonus_shop_discount` | `INTEGER DEFAULT 0` | :1390 |
| `awards` | `image` | `TEXT` | :1379 |
| `awards` | `monthly_nm` | `INTEGER DEFAULT 0` | :1395 |
| `awards` | `reward_nm` | `INTEGER DEFAULT 0` | :1394 |
| `buildings` | `required_status` | `TEXT` | :1145 |
| `clan_buildings` | `building_photo_file_id` | `TEXT` | :1777 |
| `clan_members` | `role` | `TEXT NOT NULL DEFAULT 'member'` | :1147 |
| `clans` | `tree_amber_at` | `TEXT DEFAULT NULL` | :1450 |
| `dungeon_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1315 |
| `dungeon_enemies` | `admin_tuned` | `INTEGER DEFAULT 0` | :1351 |
| `dungeon_enemies` | `armor` | `INTEGER DEFAULT 0` | :1311 |
| `dungeon_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1582 |
| `dungeon_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1583 |
| `dungeon_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1313 |
| `dungeon_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1314 |
| `dungeon_enemies` | `damage_max` | `INTEGER DEFAULT 0` | :1310 |
| `dungeon_enemies` | `damage_min` | `INTEGER DEFAULT 0` | :1309 |
| `dungeon_enemies` | `description` | `TEXT` | :1307 |
| `dungeon_enemies` | `dodge` | `INTEGER DEFAULT 0` | :1308 |
| `dungeon_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1312 |
| `dungeon_enemies` | `drops` | `TEXT DEFAULT '[]'` | :1303 |
| `dungeon_enemies` | `frostbite_chance` | `INTEGER DEFAULT 0` | :1584 |
| `dungeon_enemies` | `image` | `TEXT` | :1304 |
| `dungeon_enemies` | `poison_chance` | `INTEGER DEFAULT 0` | :1305 |
| `dungeon_enemies` | `poison_dmg` | `INTEGER DEFAULT 0` | :1306 |
| `dungeons` | `is_training` | `INTEGER DEFAULT 0` | :1573 |
| `dungeons` | `photo_dawn` | `TEXT` | :1364 |
| `dungeons` | `photo_day` | `TEXT` | :1365 |
| `dungeons` | `photo_night` | `TEXT` | :1367 |
| `dungeons` | `photo_rope` | `TEXT` | :1370 |
| `dungeons` | `photo_sunset` | `TEXT` | :1366 |
| `dungeons` | `photo_water` | `TEXT` | :1369 |
| `dungeons` | `rooms_map` | `TEXT` | :1589 |
| `fire_lab_sessions` | `boss_encounters` | `INTEGER DEFAULT 0` | :1782 |
| `fire_lab_sessions` | `effects_json` | `TEXT DEFAULT NULL` | :1781 |
| `fire_lab_sessions` | `enemy_json` | `TEXT DEFAULT NULL` | :1780 |
| `fire_lab_sessions` | `fish_used` | `INTEGER DEFAULT 0` | :1783 |
| `fire_lab_sessions` | `last_active_at` | `TIMESTAMP` | :1785 |
| `firelab_enemies` | `armor` | `INTEGER DEFAULT 0` | :1779 |
| `firelab_enemies` | `on_hit_effects` | `TEXT DEFAULT NULL` | :1778 |
| `fish_catches` | `expires_at` | `TIMESTAMP` | :1440 |
| `fish_catches` | `kind` | `TEXT DEFAULT 'fish'` | :1595 |
| `fishing_enemies` | `armor` | `INTEGER DEFAULT 0` | :1326 |
| `fishing_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1324 |
| `fishing_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1325 |
| `forest_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1320 |
| `forest_enemies` | `armor` | `INTEGER DEFAULT 0` | :1316 |
| `forest_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1322 |
| `forest_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1323 |
| `forest_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1318 |
| `forest_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1319 |
| `forest_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1317 |
| `forest_mushrooms` | `zone` | `TEXT DEFAULT 'clearing'` | :1492 |
| `housing_slots` | `embedded` | `INTEGER DEFAULT 0` | :1523 |
| `inventory` | `expires_at` | `TIMESTAMP` | :1435 |
| `inventory` | `plant_data` | `TEXT` | :1437 |
| `items` | `armor` | `INTEGER DEFAULT 0` | :1177 |
| `items` | `crit_chance` | `INTEGER DEFAULT 0` | :1180 |
| `items` | `crit_mult` | `REAL DEFAULT 0` | :1181 |
| `items` | `cure_frostbite` | `INTEGER DEFAULT 0` | :1586 |
| `items` | `cure_poison` | `INTEGER DEFAULT 0` | :1352 |
| `items` | `damage` | `INTEGER DEFAULT 0` | :1301 |
| `items` | `dodge_bonus` | `INTEGER DEFAULT 0` | :1619 |
| `items` | `dodge_buff_pct` | `INTEGER DEFAULT 0` | :1623 |
| `items` | `drink_effect` | `TEXT DEFAULT NULL` | :1423 |
| `items` | `equip_slot` | `TEXT` | :1183 |
| `items` | `heal` | `INTEGER DEFAULT 0` | :1302 |
| `items` | `heal_bonus_pct` | `INTEGER DEFAULT 0` | :1618 |
| `items` | `housing_slots` | `INTEGER` | :1729 |
| `items` | `housing_type` | `TEXT` | :1728 |
| `items` | `loot_only` | `INTEGER DEFAULT 0` | :1734 |
| `items` | `market_ok` | `INTEGER DEFAULT 0` | :1592 |
| `items` | `plant_name` | `TEXT` | :1602 |
| `items` | `regen` | `INTEGER DEFAULT 0` | :1362 |
| `items` | `regen_turns` | `INTEGER DEFAULT 0` | :1622 |
| `items` | `required_status` | `TEXT` | :1144 |
| `items` | `weapon_effect` | `TEXT` | :1613 |
| `items` | `weapon_effect_chance` | `INTEGER DEFAULT 0` | :1614 |
| `items` | `weapon_effect_dmg` | `INTEGER DEFAULT 0` | :1615 |
| `locations` | `clearing_photo` | `TEXT DEFAULT NULL` | :1478 |
| `locations` | `fire_photo` | `TEXT DEFAULT NULL` | :1476 |
| `locations` | `glade_photo` | `TEXT DEFAULT NULL` | :1477 |
| `locations` | `logging_photo` | `TEXT DEFAULT NULL` | :1487 |
| `locations` | `mine_level_photo` | `TEXT DEFAULT NULL` | :1481 |
| `locations` | `photo_dawn` | `TEXT` | :1354 |
| `locations` | `photo_day` | `TEXT` | :1355 |
| `locations` | `photo_night` | `TEXT` | :1357 |
| `locations` | `photo_sunset` | `TEXT` | :1356 |
| `locations` | `preview_photo` | `TEXT` | :1353 |
| `locations` | `season_photos` | `TEXT DEFAULT NULL` | :1473 |
| `locations` | `storage_photo` | `TEXT DEFAULT NULL` | :1483 |
| `locations` | `visits` | `INTEGER DEFAULT 0` | :1359 |
| `logging_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1341 |
| `logging_enemies` | `armor` | `INTEGER DEFAULT 0` | :1337 |
| `logging_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1339 |
| `logging_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1340 |
| `logging_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1338 |
| `market_fish` | `base_price` | `INTEGER DEFAULT 0` | :1576 |
| `mine_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1332 |
| `mine_enemies` | `armor` | `INTEGER DEFAULT 0` | :1328 |
| `mine_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1333 |
| `mine_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1334 |
| `mine_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1330 |
| `mine_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1331 |
| `mine_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1329 |
| `nii_reports` | `photo2_file_id` | `TEXT DEFAULT NULL` | :1405 |
| `player_dungeon_run` | `loot_nm` | `INTEGER DEFAULT 0` | :1288 |
| `player_dungeon_run` | `started_at` | `TIMESTAMP DEFAULT CURRENT_TIMESTAMP` | :1289 |
| `player_housing` | `expansions_installed` | `INTEGER DEFAULT 0` | :1525 |
| `player_housing` | `housing_label` | `TEXT` | :1730 |
| `player_housing` | `housing_slots` | `INTEGER` | :1731 |
| `player_housing` | `tax_last_check` | `TEXT DEFAULT NULL` | :1577 |
| `player_housing` | `tax_unpaid_months` | `INTEGER DEFAULT 0` | :1578 |
| `polls` | `archived_day` | `TEXT DEFAULT ''` | :1541 |
| `polls` | `closed_at` | `TIMESTAMP` | :1433 |
| `polls` | `closed_by` | `INTEGER` | :1432 |
| `polls` | `closes_at` | `TIMESTAMP` | :1530 |
| `polls` | `is_archived` | `INTEGER DEFAULT 0` | :1540 |
| `reports` | `credited_troops` | `INTEGER` | :1188 |
| `reports` | `paid` | `INTEGER DEFAULT 0` | :1195 |
| `reports` | `total_troops` | `INTEGER DEFAULT 0` | :1186 |
| `statuses` | `sort_order` | `INTEGER DEFAULT 0` | :1146 |
| `users` | `about` | `TEXT DEFAULT ''` | :1171 |
| `users` | `alcohol_strong_used_day` | `TEXT DEFAULT NULL` | :1427 |
| `users` | `alcohol_strong_used_today` | `INTEGER DEFAULT 0` | :1426 |
| `users` | `alcohol_weak_used_day` | `TEXT DEFAULT NULL` | :1425 |
| `users` | `alcohol_weak_used_today` | `INTEGER DEFAULT 0` | :1424 |
| `users` | `ap_recovery_day` | `TEXT DEFAULT NULL` | :1419 |
| `users` | `ap_restored_day` | `TEXT DEFAULT NULL` | :1292 |
| `users` | `ap_restored_today` | `INTEGER DEFAULT 0` | :1293 |
| `users` | `beer_used_day` | `TEXT DEFAULT NULL` | :1422 |
| `users` | `beer_used_today` | `INTEGER DEFAULT 0` | :1421 |
| `users` | `callsign` | `TEXT` | :1377 |
| `users` | `callsign_free_used` | `INTEGER DEFAULT 0` | :1575 |
| `users` | `dodge_buff_pct` | `INTEGER DEFAULT 0` | :1625 |
| `users` | `dodge_buff_until` | `TEXT DEFAULT NULL` | :1624 |
| `users` | `duel_losses` | `INTEGER DEFAULT 0` | :1297 |
| `users` | `duel_rating` | `INTEGER DEFAULT 0` | :1295 |
| `users` | `duel_wins` | `INTEGER DEFAULT 0` | :1296 |
| `users` | `equipment` | `TEXT DEFAULT '{}'` | :1172 |
| `users` | `fish_sold_day` | `TEXT DEFAULT NULL` | :1454 |
| `users` | `fish_sold_today` | `INTEGER DEFAULT 0` | :1455 |
| `users` | `fishing_bait` | `TEXT DEFAULT ''` | :1375 |
| `users` | `forest_attempts_since_boar` | `INTEGER DEFAULT 0` | :1457 |
| `users` | `forest_attempts_since_wolf` | `INTEGER DEFAULT 0` | :1459 |
| `users` | `forest_sold_day` | `TEXT DEFAULT NULL` | :1469 |
| `users` | `forest_sold_today` | `INTEGER DEFAULT 0` | :1470 |
| `users` | `fountain_used_day` | `TEXT DEFAULT NULL` | :1442 |
| `users` | `fountain_used_today` | `INTEGER DEFAULT 0` | :1443 |
| `users` | `lantern_amber_at` | `TEXT DEFAULT NULL` | :1448 |
| `users` | `lantern_medit_day` | `TEXT DEFAULT NULL` | :1447 |
| `users` | `last_active` | `REAL DEFAULT 0` | :1300 |
| `users` | `last_salary_date` | `TIMESTAMP` | :1175 |
| `users` | `legioner` | `INTEGER DEFAULT 0` | :1671 |
| `users` | `logging_attempts_since_owl` | `INTEGER DEFAULT 0` | :1466 |
| `users` | `logging_attempts_since_snake` | `INTEGER DEFAULT 0` | :1465 |
| `users` | `market_license_expires` | `TEXT DEFAULT NULL` | :1574 |
| `users` | `mine_attempts_since_bat` | `INTEGER DEFAULT 0` | :1462 |
| `users` | `notify_enabled` | `INTEGER DEFAULT 1` | :1169 |
| `users` | `profile_public` | `INTEGER DEFAULT 1` | :1170 |
| `users` | `promoted_rank` | `TEXT` | :1149 |
| `users` | `salary` | `INTEGER DEFAULT 0` | :1173 |
| `users` | `salary_debt` | `INTEGER DEFAULT 0` | :1176 |
| `users` | `salary_period_days` | `INTEGER DEFAULT 7` | :1174 |
| `users` | `seaweed_used_day` | `TEXT DEFAULT NULL` | :1416 |
| `users` | `seaweed_used_today` | `INTEGER DEFAULT 0` | :1415 |
| `users` | `shower_used_day` | `TEXT DEFAULT NULL` | :1445 |
| `users` | `shower_used_today` | `INTEGER DEFAULT 0` | :1452 |
| `users` | `special_blocked_until` | `TEXT DEFAULT NULL` | :1430 |
| `users` | `special_fails_today` | `INTEGER DEFAULT 0` | :1429 |
| `users` | `wing` | `TEXT` | :1668 |
| `users` | `xp_balance` | `INTEGER DEFAULT 0` | :1153 |
| `water_fish` | `excluded` | `INTEGER DEFAULT 0` | :1373 |
| `water_fish` | `kind` | `TEXT DEFAULT 'fish'` | :1596 |
| `water_fish` | `super_rare` | `INTEGER DEFAULT 0` | :1599 |
| `wings` | `abbr` | `TEXT DEFAULT ''` | :1409 |
| `wings` | `callsign` | `TEXT DEFAULT ''` | :1411 |
| `wings` | `emoji` | `TEXT DEFAULT ''` | :1412 |
| `wings` | `name` | `TEXT DEFAULT ''` | :1410 |
| `wings` | `num` | `TEXT DEFAULT ''` | :1408 |
| `wings` | `sort_order` | `INTEGER DEFAULT 0` | :1413 |

## 2. Идемпотентные засевы и миграции данных

| Функция | Вызывается из main.py | Назначение (первая строка docstring) | db.py |
|---|---|---|---|
| `backfill_rank_statuses` | — | Разово выдать статусы по текущим званиям всех пилотов (войска и админ-звания). | :6311 |
| `ensure_achievements` | ✅ | Идемпотентно засевает награды-уровни достижений и синхронизирует их. | :13347 |
| `ensure_base_status` | — | Базовый статус «Турист» для каждого нового игрока. | :6557 |
| `ensure_base_statuses` | — | Создаёт базовые статусы иерархии, если их нет. | :6512 |
| `ensure_clan_building` | — | — | :15442 |
| `ensure_duel_items` | ✅ | Товары Дома Дуэлей: дуэльные перчатки (отдельный слот) и клубная карта. | :10919 |
| `ensure_dungeon_enemy_drops` | ✅ | Синхронизирует врагов существующего данжа с DEFAULT_DUNGEON (дропы, HP, награды, | :12829 |
| `ensure_dungeon_reservoir_items` | ✅ | Идемпотентно добавляет предметы водохранилища подземелья (v0.12.0). | :12733 |
| `ensure_dungeon_shop_items` | ✅ | Идемпотентно добавляет предметы данжа (зелье в магазин, трофеи) — для существующих БД. | :12348 |
| `ensure_firelab_enemies` | ✅ | Идемпотентно засевает врагов Огненного Лабиринта (4 обычных + босс). | :9640 |
| `ensure_firelab_items` | ✅ | Идемпотентно создаёт предметы Фазы 3 «Дней Пламенного Круговорота». | :9688 |
| `ensure_fishing_enemies` | ✅ | Идемпотентно засевает врагов рыбалки (мутировавший моллюск) из MOLLUSK_SEED. | :9957 |
| `ensure_forest_enemies` | ✅ | Идемпотентно засевает врагов леса (кабан и Белый Волк Севера). | :9615 |
| `ensure_forest_items` | ✅ | Идемпотентно создаёт предметы леса (грибы, добыча кабана, жареные блюда, яд). | :8960 |
| `ensure_forest_mushrooms` | ✅ | Идемпотентно засевает пул грибов леса из FOREST_DEFAULTS. | :9132 |
| `ensure_forest_zones` | ✅ | Разовый перенос старого пула леса в зону поляны и засев пула опушки. | :9375 |
| `ensure_kvp_award` | ✅ | — | :11178 |
| `ensure_kvp_items` | ✅ | Обеспечивает эксклюзивный предмет К.В.П. — «Сержантскую трость». | :10892 |
| `ensure_kvp_user` | — | Гарантирует наличие строки прогресса К.В.П. для игрока. | :11365 |
| `ensure_life_items` | ✅ | Идемпотентно добавляет предметы жилья, мебели, семян, ресурсов и продовольствия. | :12554 |
| `ensure_logging_enemies` | ✅ | Идемпотентно засевает врагов Лесозаготовки (Змея и Неясыть). | :9121 |
| `ensure_logging_items` | ✅ | Идемпотентно создаёт предметы Лесозаготовки (топор, бревна, дропы). | :9078 |
| `ensure_market_license_item` | ✅ | Идемпотентно добавляет «Торговую лицензию» в магазин. | :10441 |
| `ensure_mine_enemies` | ✅ | Идемпотентно засевает врагов копи (Летучая мышь) из MINE_BAT_SEED. | :9069 |
| `ensure_mine_items` | ✅ | Идемпотентно создаёт предметы Железной копи (кирка, руда, самоцветы). | :9038 |
| `ensure_mollusk_items` | ✅ | Идемпотентно создаёт предметы моллюска (из его добычи и готового блюда). | :9963 |
| `ensure_player_housing` | — | Возвращает жильё игрока, создавая муниципальную квартиру для пилота при первом обращении. | :12965 |
| `ensure_rank_statuses_for_troops` | — | Выдать статус по текущему званию игрока (по войскам или админ-назначению). | :6299 |
| `ensure_recipe_shop_item` | — | Синхронизирует товар-рецепт «Рецепт: <name>» с рецептом (менеджер). | :13772 |
| `ensure_recipe_shop_items` | ✅ | Создаёт в магазине предметы-рецепты категории 'recipes'. | :15116 |
| `ensure_recipes` | ✅ | Идемпотентно засевает рецепты и синхронизирует уже существующие. | :13622 |
| `ensure_tourist_booklet` | ✅ | Создаёт предмет «Буклет туриста» и награду «Опытный турист», если их нет. | :11214 |
| `ensure_user_recipes_backfill` | ✅ | Разово открывает все рецепты существующим игрокам. | :15268 |
| `ensure_water_fish` | ✅ | Идемпотентно засевает water_fish из дефолтов. Правившие админом строки | :8551 |
| `migrate_legacy_junk` | ✅ | Переносит старые копии мусора (сапог, водоросли) из инвентаря в улов. | :8396 |
| `seed_default_items` | ✅ | Заполняет магазин базовым набором товаров, если он пуст и не было своих товаров. | :10615 |
| `seed_dungeon` | ✅ | — | :10770 |
| `seed_kvp` | ✅ | Создаёт тренировочный данж К.В.П. с врагами (Ефрейтор, Старший сержант), если его нет. | :10841 |
| `seed_locations` | — | Засеивает базовые локации города (Ратуша, Библиотека) как пример управляемого доступа. | :1875 |

## 3. Отдельные скрипты миграций

- `migrate_113.py` — Проверка миграций 0.19.0 на чистой БД: колонки polls, таблица rep_speeches.
- `migrate_113_old.py` — Миграция 0.19.0 поверх БД со старой схемой polls (без closes_at/is_archived).

