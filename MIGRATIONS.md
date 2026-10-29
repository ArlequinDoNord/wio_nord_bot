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

Всего вызовов: **179**; таблиц: **28**.

| Таблица | Колонка | Тип / значение по умолчанию | db.py |
|---|---|---|---|
| `awards` | `achievement_key` | `TEXT DEFAULT NULL` | :1400 |
| `awards` | `achievement_level` | `INTEGER DEFAULT 0` | :1401 |
| `awards` | `bonus_attack` | `INTEGER DEFAULT 0` | :1379 |
| `awards` | `bonus_crit` | `INTEGER DEFAULT 0` | :1386 |
| `awards` | `bonus_defense` | `INTEGER DEFAULT 0` | :1380 |
| `awards` | `bonus_dodge` | `INTEGER DEFAULT 0` | :1381 |
| `awards` | `bonus_fishing` | `INTEGER DEFAULT 0` | :1382 |
| `awards` | `bonus_hp` | `INTEGER DEFAULT 0` | :1383 |
| `awards` | `bonus_json` | `TEXT DEFAULT '{}'` | :1402 |
| `awards` | `bonus_report_tax` | `INTEGER DEFAULT 0` | :1390 |
| `awards` | `bonus_shop_discount` | `INTEGER DEFAULT 0` | :1389 |
| `awards` | `image` | `TEXT` | :1378 |
| `awards` | `monthly_nm` | `INTEGER DEFAULT 0` | :1394 |
| `awards` | `reward_nm` | `INTEGER DEFAULT 0` | :1393 |
| `buildings` | `required_status` | `TEXT` | :1144 |
| `clan_buildings` | `building_photo_file_id` | `TEXT` | :1718 |
| `clan_members` | `role` | `TEXT NOT NULL DEFAULT 'member'` | :1146 |
| `dungeon_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1314 |
| `dungeon_enemies` | `admin_tuned` | `INTEGER DEFAULT 0` | :1350 |
| `dungeon_enemies` | `armor` | `INTEGER DEFAULT 0` | :1310 |
| `dungeon_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1574 |
| `dungeon_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1575 |
| `dungeon_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1312 |
| `dungeon_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1313 |
| `dungeon_enemies` | `damage_max` | `INTEGER DEFAULT 0` | :1309 |
| `dungeon_enemies` | `damage_min` | `INTEGER DEFAULT 0` | :1308 |
| `dungeon_enemies` | `description` | `TEXT` | :1306 |
| `dungeon_enemies` | `dodge` | `INTEGER DEFAULT 0` | :1307 |
| `dungeon_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1311 |
| `dungeon_enemies` | `drops` | `TEXT DEFAULT '[]'` | :1302 |
| `dungeon_enemies` | `frostbite_chance` | `INTEGER DEFAULT 0` | :1576 |
| `dungeon_enemies` | `image` | `TEXT` | :1303 |
| `dungeon_enemies` | `poison_chance` | `INTEGER DEFAULT 0` | :1304 |
| `dungeon_enemies` | `poison_dmg` | `INTEGER DEFAULT 0` | :1305 |
| `dungeons` | `is_training` | `INTEGER DEFAULT 0` | :1565 |
| `dungeons` | `photo_dawn` | `TEXT` | :1363 |
| `dungeons` | `photo_day` | `TEXT` | :1364 |
| `dungeons` | `photo_night` | `TEXT` | :1366 |
| `dungeons` | `photo_rope` | `TEXT` | :1369 |
| `dungeons` | `photo_sunset` | `TEXT` | :1365 |
| `dungeons` | `photo_water` | `TEXT` | :1368 |
| `dungeons` | `rooms_map` | `TEXT` | :1581 |
| `fire_lab_sessions` | `boss_encounters` | `INTEGER DEFAULT 0` | :1723 |
| `fire_lab_sessions` | `effects_json` | `TEXT DEFAULT NULL` | :1722 |
| `fire_lab_sessions` | `enemy_json` | `TEXT DEFAULT NULL` | :1721 |
| `firelab_enemies` | `armor` | `INTEGER DEFAULT 0` | :1720 |
| `firelab_enemies` | `on_hit_effects` | `TEXT DEFAULT NULL` | :1719 |
| `fish_catches` | `expires_at` | `TIMESTAMP` | :1439 |
| `fish_catches` | `kind` | `TEXT DEFAULT 'fish'` | :1587 |
| `fishing_enemies` | `armor` | `INTEGER DEFAULT 0` | :1325 |
| `fishing_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1323 |
| `fishing_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1324 |
| `forest_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1319 |
| `forest_enemies` | `armor` | `INTEGER DEFAULT 0` | :1315 |
| `forest_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1321 |
| `forest_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1322 |
| `forest_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1317 |
| `forest_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1318 |
| `forest_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1316 |
| `forest_mushrooms` | `zone` | `TEXT DEFAULT 'clearing'` | :1484 |
| `housing_slots` | `embedded` | `INTEGER DEFAULT 0` | :1515 |
| `inventory` | `expires_at` | `TIMESTAMP` | :1434 |
| `inventory` | `plant_data` | `TEXT` | :1436 |
| `items` | `armor` | `INTEGER DEFAULT 0` | :1176 |
| `items` | `crit_chance` | `INTEGER DEFAULT 0` | :1179 |
| `items` | `crit_mult` | `REAL DEFAULT 0` | :1180 |
| `items` | `cure_frostbite` | `INTEGER DEFAULT 0` | :1578 |
| `items` | `cure_poison` | `INTEGER DEFAULT 0` | :1351 |
| `items` | `damage` | `INTEGER DEFAULT 0` | :1300 |
| `items` | `drink_effect` | `TEXT DEFAULT NULL` | :1422 |
| `items` | `equip_slot` | `TEXT` | :1182 |
| `items` | `heal` | `INTEGER DEFAULT 0` | :1301 |
| `items` | `housing_slots` | `INTEGER` | :1670 |
| `items` | `housing_type` | `TEXT` | :1669 |
| `items` | `loot_only` | `INTEGER DEFAULT 0` | :1675 |
| `items` | `market_ok` | `INTEGER DEFAULT 0` | :1584 |
| `items` | `plant_name` | `TEXT` | :1594 |
| `items` | `regen` | `INTEGER DEFAULT 0` | :1361 |
| `items` | `required_status` | `TEXT` | :1143 |
| `items` | `weapon_effect` | `TEXT` | :1605 |
| `items` | `weapon_effect_chance` | `INTEGER DEFAULT 0` | :1606 |
| `items` | `weapon_effect_dmg` | `INTEGER DEFAULT 0` | :1607 |
| `locations` | `clearing_photo` | `TEXT DEFAULT NULL` | :1470 |
| `locations` | `glade_photo` | `TEXT DEFAULT NULL` | :1469 |
| `locations` | `logging_photo` | `TEXT DEFAULT NULL` | :1479 |
| `locations` | `mine_level_photo` | `TEXT DEFAULT NULL` | :1473 |
| `locations` | `photo_dawn` | `TEXT` | :1353 |
| `locations` | `photo_day` | `TEXT` | :1354 |
| `locations` | `photo_night` | `TEXT` | :1356 |
| `locations` | `photo_sunset` | `TEXT` | :1355 |
| `locations` | `preview_photo` | `TEXT` | :1352 |
| `locations` | `season_photos` | `TEXT DEFAULT NULL` | :1466 |
| `locations` | `storage_photo` | `TEXT DEFAULT NULL` | :1475 |
| `locations` | `visits` | `INTEGER DEFAULT 0` | :1358 |
| `logging_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1340 |
| `logging_enemies` | `armor` | `INTEGER DEFAULT 0` | :1336 |
| `logging_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1338 |
| `logging_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1339 |
| `logging_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1337 |
| `market_fish` | `base_price` | `INTEGER DEFAULT 0` | :1568 |
| `mine_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1331 |
| `mine_enemies` | `armor` | `INTEGER DEFAULT 0` | :1327 |
| `mine_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1332 |
| `mine_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1333 |
| `mine_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1329 |
| `mine_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1330 |
| `mine_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1328 |
| `nii_reports` | `photo2_file_id` | `TEXT DEFAULT NULL` | :1404 |
| `player_dungeon_run` | `loot_nm` | `INTEGER DEFAULT 0` | :1287 |
| `player_dungeon_run` | `started_at` | `TIMESTAMP DEFAULT CURRENT_TIMESTAMP` | :1288 |
| `player_housing` | `expansions_installed` | `INTEGER DEFAULT 0` | :1517 |
| `player_housing` | `housing_label` | `TEXT` | :1671 |
| `player_housing` | `housing_slots` | `INTEGER` | :1672 |
| `player_housing` | `tax_last_check` | `TEXT DEFAULT NULL` | :1569 |
| `player_housing` | `tax_unpaid_months` | `INTEGER DEFAULT 0` | :1570 |
| `polls` | `archived_day` | `TEXT DEFAULT ''` | :1533 |
| `polls` | `closed_at` | `TIMESTAMP` | :1432 |
| `polls` | `closed_by` | `INTEGER` | :1431 |
| `polls` | `closes_at` | `TIMESTAMP` | :1522 |
| `polls` | `is_archived` | `INTEGER DEFAULT 0` | :1532 |
| `reports` | `credited_troops` | `INTEGER` | :1187 |
| `reports` | `paid` | `INTEGER DEFAULT 0` | :1194 |
| `reports` | `total_troops` | `INTEGER DEFAULT 0` | :1185 |
| `statuses` | `sort_order` | `INTEGER DEFAULT 0` | :1145 |
| `users` | `about` | `TEXT DEFAULT ''` | :1170 |
| `users` | `alcohol_strong_used_day` | `TEXT DEFAULT NULL` | :1426 |
| `users` | `alcohol_strong_used_today` | `INTEGER DEFAULT 0` | :1425 |
| `users` | `alcohol_weak_used_day` | `TEXT DEFAULT NULL` | :1424 |
| `users` | `alcohol_weak_used_today` | `INTEGER DEFAULT 0` | :1423 |
| `users` | `ap_recovery_day` | `TEXT DEFAULT NULL` | :1418 |
| `users` | `ap_restored_day` | `TEXT DEFAULT NULL` | :1291 |
| `users` | `ap_restored_today` | `INTEGER DEFAULT 0` | :1292 |
| `users` | `beer_used_day` | `TEXT DEFAULT NULL` | :1421 |
| `users` | `beer_used_today` | `INTEGER DEFAULT 0` | :1420 |
| `users` | `callsign` | `TEXT` | :1376 |
| `users` | `callsign_free_used` | `INTEGER DEFAULT 0` | :1567 |
| `users` | `duel_losses` | `INTEGER DEFAULT 0` | :1296 |
| `users` | `duel_rating` | `INTEGER DEFAULT 0` | :1294 |
| `users` | `duel_wins` | `INTEGER DEFAULT 0` | :1295 |
| `users` | `equipment` | `TEXT DEFAULT '{}'` | :1171 |
| `users` | `fish_sold_day` | `TEXT DEFAULT NULL` | :1447 |
| `users` | `fish_sold_today` | `INTEGER DEFAULT 0` | :1448 |
| `users` | `fishing_bait` | `TEXT DEFAULT ''` | :1374 |
| `users` | `forest_attempts_since_boar` | `INTEGER DEFAULT 0` | :1450 |
| `users` | `forest_attempts_since_wolf` | `INTEGER DEFAULT 0` | :1452 |
| `users` | `forest_sold_day` | `TEXT DEFAULT NULL` | :1462 |
| `users` | `forest_sold_today` | `INTEGER DEFAULT 0` | :1463 |
| `users` | `fountain_used_day` | `TEXT DEFAULT NULL` | :1441 |
| `users` | `fountain_used_today` | `INTEGER DEFAULT 0` | :1442 |
| `users` | `last_active` | `REAL DEFAULT 0` | :1299 |
| `users` | `last_salary_date` | `TIMESTAMP` | :1174 |
| `users` | `legioner` | `INTEGER DEFAULT 0` | :1612 |
| `users` | `logging_attempts_since_owl` | `INTEGER DEFAULT 0` | :1459 |
| `users` | `logging_attempts_since_snake` | `INTEGER DEFAULT 0` | :1458 |
| `users` | `market_license_expires` | `TEXT DEFAULT NULL` | :1566 |
| `users` | `mine_attempts_since_bat` | `INTEGER DEFAULT 0` | :1455 |
| `users` | `notify_enabled` | `INTEGER DEFAULT 1` | :1168 |
| `users` | `profile_public` | `INTEGER DEFAULT 1` | :1169 |
| `users` | `promoted_rank` | `TEXT` | :1148 |
| `users` | `salary` | `INTEGER DEFAULT 0` | :1172 |
| `users` | `salary_debt` | `INTEGER DEFAULT 0` | :1175 |
| `users` | `salary_period_days` | `INTEGER DEFAULT 7` | :1173 |
| `users` | `seaweed_used_day` | `TEXT DEFAULT NULL` | :1415 |
| `users` | `seaweed_used_today` | `INTEGER DEFAULT 0` | :1414 |
| `users` | `shower_used_day` | `TEXT DEFAULT NULL` | :1444 |
| `users` | `shower_used_today` | `INTEGER DEFAULT 0` | :1445 |
| `users` | `special_blocked_until` | `TEXT DEFAULT NULL` | :1429 |
| `users` | `special_fails_today` | `INTEGER DEFAULT 0` | :1428 |
| `users` | `wing` | `TEXT` | :1609 |
| `users` | `xp_balance` | `INTEGER DEFAULT 0` | :1152 |
| `water_fish` | `excluded` | `INTEGER DEFAULT 0` | :1372 |
| `water_fish` | `kind` | `TEXT DEFAULT 'fish'` | :1588 |
| `water_fish` | `super_rare` | `INTEGER DEFAULT 0` | :1591 |
| `wings` | `abbr` | `TEXT DEFAULT ''` | :1408 |
| `wings` | `callsign` | `TEXT DEFAULT ''` | :1410 |
| `wings` | `emoji` | `TEXT DEFAULT ''` | :1411 |
| `wings` | `name` | `TEXT DEFAULT ''` | :1409 |
| `wings` | `num` | `TEXT DEFAULT ''` | :1407 |
| `wings` | `sort_order` | `INTEGER DEFAULT 0` | :1412 |

## 2. Идемпотентные засевы и миграции данных

| Функция | Вызывается из main.py | Назначение (первая строка docstring) | db.py |
|---|---|---|---|
| `backfill_rank_statuses` | — | Разово выдать статусы по текущим званиям всех пилотов (войска и админ-звания). | :6076 |
| `ensure_achievements` | ✅ | Идемпотентно засевает награды-уровни достижений и синхронизирует их. | :12684 |
| `ensure_base_status` | — | Базовый статус «Турист» для каждого нового игрока. | :6322 |
| `ensure_base_statuses` | — | Создаёт базовые статусы иерархии, если их нет. | :6277 |
| `ensure_clan_building` | — | — | :14479 |
| `ensure_duel_items` | ✅ | Товары Дома Дуэлей: дуэльные перчатки (отдельный слот) и клубная карта. | :10371 |
| `ensure_dungeon_enemy_drops` | ✅ | Синхронизирует врагов существующего данжа с DEFAULT_DUNGEON (дропы, HP, награды, | :12190 |
| `ensure_dungeon_reservoir_items` | ✅ | Идемпотентно добавляет предметы водохранилища подземелья (v0.12.0). | :12094 |
| `ensure_dungeon_shop_items` | ✅ | Идемпотентно добавляет предметы данжа (зелье в магазин, трофеи) — для существующих БД. | :11709 |
| `ensure_firelab_enemies` | — | Идемпотентно засевает врагов Огненного Лабиринта (4 обычных + босс). | :9390 |
| `ensure_fishing_enemies` | ✅ | Идемпотентно засевает врагов рыбалки (мутировавший моллюск) из MOLLUSK_SEED. | :9409 |
| `ensure_forest_enemies` | ✅ | Идемпотентно засевает врагов леса (кабан и Белый Волк Севера). | :9365 |
| `ensure_forest_items` | ✅ | Идемпотентно создаёт предметы леса (грибы, добыча кабана, жареные блюда, яд). | :8710 |
| `ensure_forest_mushrooms` | ✅ | Идемпотентно засевает пул грибов леса из FOREST_DEFAULTS. | :8882 |
| `ensure_forest_zones` | ✅ | Разовый перенос старого пула леса в зону поляны и засев пула опушки. | :9125 |
| `ensure_kvp_award` | ✅ | — | :10630 |
| `ensure_kvp_items` | ✅ | Обеспечивает эксклюзивный предмет К.В.П. — «Сержантскую трость». | :10344 |
| `ensure_kvp_user` | — | Гарантирует наличие строки прогресса К.В.П. для игрока. | :10817 |
| `ensure_life_items` | ✅ | Идемпотентно добавляет предметы жилья, мебели, семян, ресурсов и продовольствия. | :11915 |
| `ensure_logging_enemies` | ✅ | Идемпотентно засевает врагов Лесозаготовки (Змея и Неясыть). | :8871 |
| `ensure_logging_items` | ✅ | Идемпотентно создаёт предметы Лесозаготовки (топор, бревна, дропы). | :8828 |
| `ensure_market_license_item` | ✅ | Идемпотентно добавляет «Торговую лицензию» в магазин. | :9893 |
| `ensure_mine_enemies` | ✅ | Идемпотентно засевает врагов копи (Летучая мышь) из MINE_BAT_SEED. | :8819 |
| `ensure_mine_items` | ✅ | Идемпотентно создаёт предметы Железной копи (кирка, руда, самоцветы). | :8788 |
| `ensure_mollusk_items` | ✅ | Идемпотентно создаёт предметы моллюска (из его добычи и готового блюда). | :9415 |
| `ensure_player_housing` | — | Возвращает жильё игрока, создавая муниципальную квартиру для пилота при первом обращении. | :12321 |
| `ensure_rank_statuses_for_troops` | — | Выдать статус по текущему званию игрока (по войскам или админ-назначению). | :6064 |
| `ensure_recipe_shop_item` | — | Синхронизирует товар-рецепт «Рецепт: <name>» с рецептом (менеджер). | :13097 |
| `ensure_recipe_shop_items` | ✅ | Создаёт в магазине предметы-рецепты категории 'recipes'. | :14159 |
| `ensure_recipes` | ✅ | Идемпотентно засевает рецепты и синхронизирует уже существующие. | :12947 |
| `ensure_tourist_booklet` | ✅ | Создаёт предмет «Буклет туриста» и награду «Опытный турист», если их нет. | :10666 |
| `ensure_user_recipes_backfill` | ✅ | Разово открывает все рецепты существующим игрокам. | :14305 |
| `ensure_water_fish` | ✅ | Идемпотентно засевает water_fish из дефолтов. Правившие админом строки | :8301 |
| `migrate_legacy_junk` | ✅ | Переносит старые копии мусора (сапог, водоросли) из инвентаря в улов. | :8147 |
| `seed_default_items` | ✅ | Заполняет магазин базовым набором товаров, если он пуст и не было своих товаров. | :10067 |
| `seed_dungeon` | ✅ | — | :10222 |
| `seed_kvp` | ✅ | Создаёт тренировочный данж К.В.П. с врагами (Ефрейтор, Старший сержант), если его нет. | :10293 |
| `seed_locations` | — | Засеивает базовые локации города (Ратуша, Библиотека) как пример управляемого доступа. | :1804 |

## 3. Отдельные скрипты миграций

- `migrate_113.py` — Проверка миграций 0.19.0 на чистой БД: колонки polls, таблица rep_speeches.
- `migrate_113_old.py` — Миграция 0.19.0 поверх БД со старой схемой polls (без closes_at/is_archived).

