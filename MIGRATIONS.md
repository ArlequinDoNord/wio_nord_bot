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

Всего вызовов: **174**; таблиц: **26**.

| Таблица | Колонка | Тип / значение по умолчанию | db.py |
|---|---|---|---|
| `awards` | `achievement_key` | `TEXT DEFAULT NULL` | :1367 |
| `awards` | `achievement_level` | `INTEGER DEFAULT 0` | :1368 |
| `awards` | `bonus_attack` | `INTEGER DEFAULT 0` | :1346 |
| `awards` | `bonus_crit` | `INTEGER DEFAULT 0` | :1353 |
| `awards` | `bonus_defense` | `INTEGER DEFAULT 0` | :1347 |
| `awards` | `bonus_dodge` | `INTEGER DEFAULT 0` | :1348 |
| `awards` | `bonus_fishing` | `INTEGER DEFAULT 0` | :1349 |
| `awards` | `bonus_hp` | `INTEGER DEFAULT 0` | :1350 |
| `awards` | `bonus_json` | `TEXT DEFAULT '{}'` | :1369 |
| `awards` | `bonus_report_tax` | `INTEGER DEFAULT 0` | :1357 |
| `awards` | `bonus_shop_discount` | `INTEGER DEFAULT 0` | :1356 |
| `awards` | `image` | `TEXT` | :1345 |
| `awards` | `monthly_nm` | `INTEGER DEFAULT 0` | :1361 |
| `awards` | `reward_nm` | `INTEGER DEFAULT 0` | :1360 |
| `buildings` | `required_status` | `TEXT` | :1111 |
| `clan_buildings` | `building_photo_file_id` | `TEXT` | :1685 |
| `clan_members` | `role` | `TEXT NOT NULL DEFAULT 'member'` | :1113 |
| `dungeon_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1281 |
| `dungeon_enemies` | `admin_tuned` | `INTEGER DEFAULT 0` | :1317 |
| `dungeon_enemies` | `armor` | `INTEGER DEFAULT 0` | :1277 |
| `dungeon_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1541 |
| `dungeon_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1542 |
| `dungeon_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1279 |
| `dungeon_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1280 |
| `dungeon_enemies` | `damage_max` | `INTEGER DEFAULT 0` | :1276 |
| `dungeon_enemies` | `damage_min` | `INTEGER DEFAULT 0` | :1275 |
| `dungeon_enemies` | `description` | `TEXT` | :1273 |
| `dungeon_enemies` | `dodge` | `INTEGER DEFAULT 0` | :1274 |
| `dungeon_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1278 |
| `dungeon_enemies` | `drops` | `TEXT DEFAULT '[]'` | :1269 |
| `dungeon_enemies` | `frostbite_chance` | `INTEGER DEFAULT 0` | :1543 |
| `dungeon_enemies` | `image` | `TEXT` | :1270 |
| `dungeon_enemies` | `poison_chance` | `INTEGER DEFAULT 0` | :1271 |
| `dungeon_enemies` | `poison_dmg` | `INTEGER DEFAULT 0` | :1272 |
| `dungeons` | `is_training` | `INTEGER DEFAULT 0` | :1532 |
| `dungeons` | `photo_dawn` | `TEXT` | :1330 |
| `dungeons` | `photo_day` | `TEXT` | :1331 |
| `dungeons` | `photo_night` | `TEXT` | :1333 |
| `dungeons` | `photo_rope` | `TEXT` | :1336 |
| `dungeons` | `photo_sunset` | `TEXT` | :1332 |
| `dungeons` | `photo_water` | `TEXT` | :1335 |
| `dungeons` | `rooms_map` | `TEXT` | :1548 |
| `fish_catches` | `expires_at` | `TIMESTAMP` | :1406 |
| `fish_catches` | `kind` | `TEXT DEFAULT 'fish'` | :1554 |
| `fishing_enemies` | `armor` | `INTEGER DEFAULT 0` | :1292 |
| `fishing_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1290 |
| `fishing_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1291 |
| `forest_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1286 |
| `forest_enemies` | `armor` | `INTEGER DEFAULT 0` | :1282 |
| `forest_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1288 |
| `forest_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1289 |
| `forest_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1284 |
| `forest_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1285 |
| `forest_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1283 |
| `forest_mushrooms` | `zone` | `TEXT DEFAULT 'clearing'` | :1451 |
| `housing_slots` | `embedded` | `INTEGER DEFAULT 0` | :1482 |
| `inventory` | `expires_at` | `TIMESTAMP` | :1401 |
| `inventory` | `plant_data` | `TEXT` | :1403 |
| `items` | `armor` | `INTEGER DEFAULT 0` | :1143 |
| `items` | `crit_chance` | `INTEGER DEFAULT 0` | :1146 |
| `items` | `crit_mult` | `REAL DEFAULT 0` | :1147 |
| `items` | `cure_frostbite` | `INTEGER DEFAULT 0` | :1545 |
| `items` | `cure_poison` | `INTEGER DEFAULT 0` | :1318 |
| `items` | `damage` | `INTEGER DEFAULT 0` | :1267 |
| `items` | `drink_effect` | `TEXT DEFAULT NULL` | :1389 |
| `items` | `equip_slot` | `TEXT` | :1149 |
| `items` | `heal` | `INTEGER DEFAULT 0` | :1268 |
| `items` | `housing_slots` | `INTEGER` | :1637 |
| `items` | `housing_type` | `TEXT` | :1636 |
| `items` | `loot_only` | `INTEGER DEFAULT 0` | :1642 |
| `items` | `market_ok` | `INTEGER DEFAULT 0` | :1551 |
| `items` | `plant_name` | `TEXT` | :1561 |
| `items` | `regen` | `INTEGER DEFAULT 0` | :1328 |
| `items` | `required_status` | `TEXT` | :1110 |
| `items` | `weapon_effect` | `TEXT` | :1572 |
| `items` | `weapon_effect_chance` | `INTEGER DEFAULT 0` | :1573 |
| `items` | `weapon_effect_dmg` | `INTEGER DEFAULT 0` | :1574 |
| `locations` | `clearing_photo` | `TEXT DEFAULT NULL` | :1437 |
| `locations` | `glade_photo` | `TEXT DEFAULT NULL` | :1436 |
| `locations` | `logging_photo` | `TEXT DEFAULT NULL` | :1446 |
| `locations` | `mine_level_photo` | `TEXT DEFAULT NULL` | :1440 |
| `locations` | `photo_dawn` | `TEXT` | :1320 |
| `locations` | `photo_day` | `TEXT` | :1321 |
| `locations` | `photo_night` | `TEXT` | :1323 |
| `locations` | `photo_sunset` | `TEXT` | :1322 |
| `locations` | `preview_photo` | `TEXT` | :1319 |
| `locations` | `season_photos` | `TEXT DEFAULT NULL` | :1433 |
| `locations` | `storage_photo` | `TEXT DEFAULT NULL` | :1442 |
| `locations` | `visits` | `INTEGER DEFAULT 0` | :1325 |
| `logging_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1307 |
| `logging_enemies` | `armor` | `INTEGER DEFAULT 0` | :1303 |
| `logging_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1305 |
| `logging_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1306 |
| `logging_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1304 |
| `market_fish` | `base_price` | `INTEGER DEFAULT 0` | :1535 |
| `mine_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1298 |
| `mine_enemies` | `armor` | `INTEGER DEFAULT 0` | :1294 |
| `mine_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1299 |
| `mine_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1300 |
| `mine_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1296 |
| `mine_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1297 |
| `mine_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1295 |
| `nii_reports` | `photo2_file_id` | `TEXT DEFAULT NULL` | :1371 |
| `player_dungeon_run` | `loot_nm` | `INTEGER DEFAULT 0` | :1254 |
| `player_dungeon_run` | `started_at` | `TIMESTAMP DEFAULT CURRENT_TIMESTAMP` | :1255 |
| `player_housing` | `expansions_installed` | `INTEGER DEFAULT 0` | :1484 |
| `player_housing` | `housing_label` | `TEXT` | :1638 |
| `player_housing` | `housing_slots` | `INTEGER` | :1639 |
| `player_housing` | `tax_last_check` | `TEXT DEFAULT NULL` | :1536 |
| `player_housing` | `tax_unpaid_months` | `INTEGER DEFAULT 0` | :1537 |
| `polls` | `archived_day` | `TEXT DEFAULT ''` | :1500 |
| `polls` | `closed_at` | `TIMESTAMP` | :1399 |
| `polls` | `closed_by` | `INTEGER` | :1398 |
| `polls` | `closes_at` | `TIMESTAMP` | :1489 |
| `polls` | `is_archived` | `INTEGER DEFAULT 0` | :1499 |
| `reports` | `credited_troops` | `INTEGER` | :1154 |
| `reports` | `paid` | `INTEGER DEFAULT 0` | :1161 |
| `reports` | `total_troops` | `INTEGER DEFAULT 0` | :1152 |
| `statuses` | `sort_order` | `INTEGER DEFAULT 0` | :1112 |
| `users` | `about` | `TEXT DEFAULT ''` | :1137 |
| `users` | `alcohol_strong_used_day` | `TEXT DEFAULT NULL` | :1393 |
| `users` | `alcohol_strong_used_today` | `INTEGER DEFAULT 0` | :1392 |
| `users` | `alcohol_weak_used_day` | `TEXT DEFAULT NULL` | :1391 |
| `users` | `alcohol_weak_used_today` | `INTEGER DEFAULT 0` | :1390 |
| `users` | `ap_recovery_day` | `TEXT DEFAULT NULL` | :1385 |
| `users` | `ap_restored_day` | `TEXT DEFAULT NULL` | :1258 |
| `users` | `ap_restored_today` | `INTEGER DEFAULT 0` | :1259 |
| `users` | `beer_used_day` | `TEXT DEFAULT NULL` | :1388 |
| `users` | `beer_used_today` | `INTEGER DEFAULT 0` | :1387 |
| `users` | `callsign` | `TEXT` | :1343 |
| `users` | `callsign_free_used` | `INTEGER DEFAULT 0` | :1534 |
| `users` | `duel_losses` | `INTEGER DEFAULT 0` | :1263 |
| `users` | `duel_rating` | `INTEGER DEFAULT 0` | :1261 |
| `users` | `duel_wins` | `INTEGER DEFAULT 0` | :1262 |
| `users` | `equipment` | `TEXT DEFAULT '{}'` | :1138 |
| `users` | `fish_sold_day` | `TEXT DEFAULT NULL` | :1414 |
| `users` | `fish_sold_today` | `INTEGER DEFAULT 0` | :1415 |
| `users` | `fishing_bait` | `TEXT DEFAULT ''` | :1341 |
| `users` | `forest_attempts_since_boar` | `INTEGER DEFAULT 0` | :1417 |
| `users` | `forest_attempts_since_wolf` | `INTEGER DEFAULT 0` | :1419 |
| `users` | `forest_sold_day` | `TEXT DEFAULT NULL` | :1429 |
| `users` | `forest_sold_today` | `INTEGER DEFAULT 0` | :1430 |
| `users` | `fountain_used_day` | `TEXT DEFAULT NULL` | :1408 |
| `users` | `fountain_used_today` | `INTEGER DEFAULT 0` | :1409 |
| `users` | `last_active` | `REAL DEFAULT 0` | :1266 |
| `users` | `last_salary_date` | `TIMESTAMP` | :1141 |
| `users` | `legioner` | `INTEGER DEFAULT 0` | :1579 |
| `users` | `logging_attempts_since_owl` | `INTEGER DEFAULT 0` | :1426 |
| `users` | `logging_attempts_since_snake` | `INTEGER DEFAULT 0` | :1425 |
| `users` | `market_license_expires` | `TEXT DEFAULT NULL` | :1533 |
| `users` | `mine_attempts_since_bat` | `INTEGER DEFAULT 0` | :1422 |
| `users` | `notify_enabled` | `INTEGER DEFAULT 1` | :1135 |
| `users` | `profile_public` | `INTEGER DEFAULT 1` | :1136 |
| `users` | `promoted_rank` | `TEXT` | :1115 |
| `users` | `salary` | `INTEGER DEFAULT 0` | :1139 |
| `users` | `salary_debt` | `INTEGER DEFAULT 0` | :1142 |
| `users` | `salary_period_days` | `INTEGER DEFAULT 7` | :1140 |
| `users` | `seaweed_used_day` | `TEXT DEFAULT NULL` | :1382 |
| `users` | `seaweed_used_today` | `INTEGER DEFAULT 0` | :1381 |
| `users` | `shower_used_day` | `TEXT DEFAULT NULL` | :1411 |
| `users` | `shower_used_today` | `INTEGER DEFAULT 0` | :1412 |
| `users` | `special_blocked_until` | `TEXT DEFAULT NULL` | :1396 |
| `users` | `special_fails_today` | `INTEGER DEFAULT 0` | :1395 |
| `users` | `wing` | `TEXT` | :1576 |
| `users` | `xp_balance` | `INTEGER DEFAULT 0` | :1119 |
| `water_fish` | `excluded` | `INTEGER DEFAULT 0` | :1339 |
| `water_fish` | `kind` | `TEXT DEFAULT 'fish'` | :1555 |
| `water_fish` | `super_rare` | `INTEGER DEFAULT 0` | :1558 |
| `wings` | `abbr` | `TEXT DEFAULT ''` | :1375 |
| `wings` | `callsign` | `TEXT DEFAULT ''` | :1377 |
| `wings` | `emoji` | `TEXT DEFAULT ''` | :1378 |
| `wings` | `name` | `TEXT DEFAULT ''` | :1376 |
| `wings` | `num` | `TEXT DEFAULT ''` | :1374 |
| `wings` | `sort_order` | `INTEGER DEFAULT 0` | :1379 |

## 2. Идемпотентные засевы и миграции данных

| Функция | Вызывается из main.py | Назначение (первая строка docstring) | db.py |
|---|---|---|---|
| `backfill_rank_statuses` | — | Разово выдать статусы по текущим званиям всех пилотов (войска и админ-звания). | :5957 |
| `ensure_achievements` | ✅ | Идемпотентно засевает награды-уровни достижений и синхронизирует их. | :12545 |
| `ensure_base_status` | — | Базовый статус «Турист» для каждого нового игрока. | :6203 |
| `ensure_base_statuses` | — | Создаёт базовые статусы иерархии, если их нет. | :6158 |
| `ensure_clan_building` | — | — | :14340 |
| `ensure_duel_items` | ✅ | Товары Дома Дуэлей: дуэльные перчатки (отдельный слот) и клубная карта. | :10232 |
| `ensure_dungeon_enemy_drops` | ✅ | Синхронизирует врагов существующего данжа с DEFAULT_DUNGEON (дропы, HP, награды, | :12051 |
| `ensure_dungeon_reservoir_items` | ✅ | Идемпотентно добавляет предметы водохранилища подземелья (v0.12.0). | :11955 |
| `ensure_dungeon_shop_items` | ✅ | Идемпотентно добавляет предметы данжа (зелье в магазин, трофеи) — для существующих БД. | :11570 |
| `ensure_fishing_enemies` | ✅ | Идемпотентно засевает врагов рыбалки (мутировавший моллюск) из MOLLUSK_SEED. | :9270 |
| `ensure_forest_enemies` | ✅ | Идемпотентно засевает врагов леса (кабан и Белый Волк Севера). | :9245 |
| `ensure_forest_items` | ✅ | Идемпотентно создаёт предметы леса (грибы, добыча кабана, жареные блюда, яд). | :8591 |
| `ensure_forest_mushrooms` | ✅ | Идемпотентно засевает пул грибов леса из FOREST_DEFAULTS. | :8763 |
| `ensure_forest_zones` | ✅ | Разовый перенос старого пула леса в зону поляны и засев пула опушки. | :9006 |
| `ensure_kvp_award` | ✅ | — | :10491 |
| `ensure_kvp_items` | ✅ | Обеспечивает эксклюзивный предмет К.В.П. — «Сержантскую трость». | :10205 |
| `ensure_kvp_user` | — | Гарантирует наличие строки прогресса К.В.П. для игрока. | :10678 |
| `ensure_life_items` | ✅ | Идемпотентно добавляет предметы жилья, мебели, семян, ресурсов и продовольствия. | :11776 |
| `ensure_logging_enemies` | ✅ | Идемпотентно засевает врагов Лесозаготовки (Змея и Неясыть). | :8752 |
| `ensure_logging_items` | ✅ | Идемпотентно создаёт предметы Лесозаготовки (топор, бревна, дропы). | :8709 |
| `ensure_market_license_item` | ✅ | Идемпотентно добавляет «Торговую лицензию» в магазин. | :9754 |
| `ensure_mine_enemies` | ✅ | Идемпотентно засевает врагов копи (Летучая мышь) из MINE_BAT_SEED. | :8700 |
| `ensure_mine_items` | ✅ | Идемпотентно создаёт предметы Железной копи (кирка, руда, самоцветы). | :8669 |
| `ensure_mollusk_items` | ✅ | Идемпотентно создаёт предметы моллюска (из его добычи и готового блюда). | :9276 |
| `ensure_player_housing` | — | Возвращает жильё игрока, создавая муниципальную квартиру для пилота при первом обращении. | :12182 |
| `ensure_rank_statuses_for_troops` | — | Выдать статус по текущему званию игрока (по войскам или админ-назначению). | :5945 |
| `ensure_recipe_shop_item` | — | Синхронизирует товар-рецепт «Рецепт: <name>» с рецептом (менеджер). | :12958 |
| `ensure_recipe_shop_items` | ✅ | Создаёт в магазине предметы-рецепты категории 'recipes'. | :14020 |
| `ensure_recipes` | ✅ | Идемпотентно засевает рецепты и синхронизирует уже существующие. | :12808 |
| `ensure_tourist_booklet` | ✅ | Создаёт предмет «Буклет туриста» и награду «Опытный турист», если их нет. | :10527 |
| `ensure_user_recipes_backfill` | ✅ | Разово открывает все рецепты существующим игрокам. | :14166 |
| `ensure_water_fish` | ✅ | Идемпотентно засевает water_fish из дефолтов. Правившие админом строки | :8182 |
| `migrate_legacy_junk` | ✅ | Переносит старые копии мусора (сапог, водоросли) из инвентаря в улов. | :8028 |
| `seed_default_items` | ✅ | Заполняет магазин базовым набором товаров, если он пуст и не было своих товаров. | :9928 |
| `seed_dungeon` | ✅ | — | :10083 |
| `seed_kvp` | ✅ | Создаёт тренировочный данж К.В.П. с врагами (Ефрейтор, Старший сержант), если его нет. | :10154 |
| `seed_locations` | — | Засеивает базовые локации города (Ратуша, Библиотека) как пример управляемого доступа. | :1766 |

## 3. Отдельные скрипты миграций

- `migrate_113.py` — Проверка миграций 0.19.0 на чистой БД: колонки polls, таблица rep_speeches.
- `migrate_113_old.py` — Миграция 0.19.0 поверх БД со старой схемой polls (без closes_at/is_archived).

