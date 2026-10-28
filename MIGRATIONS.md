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
| `awards` | `achievement_key` | `TEXT DEFAULT NULL` | :1366 |
| `awards` | `achievement_level` | `INTEGER DEFAULT 0` | :1367 |
| `awards` | `bonus_attack` | `INTEGER DEFAULT 0` | :1345 |
| `awards` | `bonus_crit` | `INTEGER DEFAULT 0` | :1352 |
| `awards` | `bonus_defense` | `INTEGER DEFAULT 0` | :1346 |
| `awards` | `bonus_dodge` | `INTEGER DEFAULT 0` | :1347 |
| `awards` | `bonus_fishing` | `INTEGER DEFAULT 0` | :1348 |
| `awards` | `bonus_hp` | `INTEGER DEFAULT 0` | :1349 |
| `awards` | `bonus_json` | `TEXT DEFAULT '{}'` | :1368 |
| `awards` | `bonus_report_tax` | `INTEGER DEFAULT 0` | :1356 |
| `awards` | `bonus_shop_discount` | `INTEGER DEFAULT 0` | :1355 |
| `awards` | `image` | `TEXT` | :1344 |
| `awards` | `monthly_nm` | `INTEGER DEFAULT 0` | :1360 |
| `awards` | `reward_nm` | `INTEGER DEFAULT 0` | :1359 |
| `buildings` | `required_status` | `TEXT` | :1110 |
| `clan_buildings` | `building_photo_file_id` | `TEXT` | :1684 |
| `clan_members` | `role` | `TEXT NOT NULL DEFAULT 'member'` | :1112 |
| `dungeon_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1280 |
| `dungeon_enemies` | `admin_tuned` | `INTEGER DEFAULT 0` | :1316 |
| `dungeon_enemies` | `armor` | `INTEGER DEFAULT 0` | :1276 |
| `dungeon_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1540 |
| `dungeon_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1541 |
| `dungeon_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1278 |
| `dungeon_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1279 |
| `dungeon_enemies` | `damage_max` | `INTEGER DEFAULT 0` | :1275 |
| `dungeon_enemies` | `damage_min` | `INTEGER DEFAULT 0` | :1274 |
| `dungeon_enemies` | `description` | `TEXT` | :1272 |
| `dungeon_enemies` | `dodge` | `INTEGER DEFAULT 0` | :1273 |
| `dungeon_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1277 |
| `dungeon_enemies` | `drops` | `TEXT DEFAULT '[]'` | :1268 |
| `dungeon_enemies` | `frostbite_chance` | `INTEGER DEFAULT 0` | :1542 |
| `dungeon_enemies` | `image` | `TEXT` | :1269 |
| `dungeon_enemies` | `poison_chance` | `INTEGER DEFAULT 0` | :1270 |
| `dungeon_enemies` | `poison_dmg` | `INTEGER DEFAULT 0` | :1271 |
| `dungeons` | `is_training` | `INTEGER DEFAULT 0` | :1531 |
| `dungeons` | `photo_dawn` | `TEXT` | :1329 |
| `dungeons` | `photo_day` | `TEXT` | :1330 |
| `dungeons` | `photo_night` | `TEXT` | :1332 |
| `dungeons` | `photo_rope` | `TEXT` | :1335 |
| `dungeons` | `photo_sunset` | `TEXT` | :1331 |
| `dungeons` | `photo_water` | `TEXT` | :1334 |
| `dungeons` | `rooms_map` | `TEXT` | :1547 |
| `fish_catches` | `expires_at` | `TIMESTAMP` | :1405 |
| `fish_catches` | `kind` | `TEXT DEFAULT 'fish'` | :1553 |
| `fishing_enemies` | `armor` | `INTEGER DEFAULT 0` | :1291 |
| `fishing_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1289 |
| `fishing_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1290 |
| `forest_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1285 |
| `forest_enemies` | `armor` | `INTEGER DEFAULT 0` | :1281 |
| `forest_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1287 |
| `forest_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1288 |
| `forest_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1283 |
| `forest_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1284 |
| `forest_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1282 |
| `forest_mushrooms` | `zone` | `TEXT DEFAULT 'clearing'` | :1450 |
| `housing_slots` | `embedded` | `INTEGER DEFAULT 0` | :1481 |
| `inventory` | `expires_at` | `TIMESTAMP` | :1400 |
| `inventory` | `plant_data` | `TEXT` | :1402 |
| `items` | `armor` | `INTEGER DEFAULT 0` | :1142 |
| `items` | `crit_chance` | `INTEGER DEFAULT 0` | :1145 |
| `items` | `crit_mult` | `REAL DEFAULT 0` | :1146 |
| `items` | `cure_frostbite` | `INTEGER DEFAULT 0` | :1544 |
| `items` | `cure_poison` | `INTEGER DEFAULT 0` | :1317 |
| `items` | `damage` | `INTEGER DEFAULT 0` | :1266 |
| `items` | `drink_effect` | `TEXT DEFAULT NULL` | :1388 |
| `items` | `equip_slot` | `TEXT` | :1148 |
| `items` | `heal` | `INTEGER DEFAULT 0` | :1267 |
| `items` | `housing_slots` | `INTEGER` | :1636 |
| `items` | `housing_type` | `TEXT` | :1635 |
| `items` | `loot_only` | `INTEGER DEFAULT 0` | :1641 |
| `items` | `market_ok` | `INTEGER DEFAULT 0` | :1550 |
| `items` | `plant_name` | `TEXT` | :1560 |
| `items` | `regen` | `INTEGER DEFAULT 0` | :1327 |
| `items` | `required_status` | `TEXT` | :1109 |
| `items` | `weapon_effect` | `TEXT` | :1571 |
| `items` | `weapon_effect_chance` | `INTEGER DEFAULT 0` | :1572 |
| `items` | `weapon_effect_dmg` | `INTEGER DEFAULT 0` | :1573 |
| `locations` | `clearing_photo` | `TEXT DEFAULT NULL` | :1436 |
| `locations` | `glade_photo` | `TEXT DEFAULT NULL` | :1435 |
| `locations` | `logging_photo` | `TEXT DEFAULT NULL` | :1445 |
| `locations` | `mine_level_photo` | `TEXT DEFAULT NULL` | :1439 |
| `locations` | `photo_dawn` | `TEXT` | :1319 |
| `locations` | `photo_day` | `TEXT` | :1320 |
| `locations` | `photo_night` | `TEXT` | :1322 |
| `locations` | `photo_sunset` | `TEXT` | :1321 |
| `locations` | `preview_photo` | `TEXT` | :1318 |
| `locations` | `season_photos` | `TEXT DEFAULT NULL` | :1432 |
| `locations` | `storage_photo` | `TEXT DEFAULT NULL` | :1441 |
| `locations` | `visits` | `INTEGER DEFAULT 0` | :1324 |
| `logging_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1306 |
| `logging_enemies` | `armor` | `INTEGER DEFAULT 0` | :1302 |
| `logging_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1304 |
| `logging_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1305 |
| `logging_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1303 |
| `market_fish` | `base_price` | `INTEGER DEFAULT 0` | :1534 |
| `mine_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1297 |
| `mine_enemies` | `armor` | `INTEGER DEFAULT 0` | :1293 |
| `mine_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1298 |
| `mine_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1299 |
| `mine_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1295 |
| `mine_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1296 |
| `mine_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1294 |
| `nii_reports` | `photo2_file_id` | `TEXT DEFAULT NULL` | :1370 |
| `player_dungeon_run` | `loot_nm` | `INTEGER DEFAULT 0` | :1253 |
| `player_dungeon_run` | `started_at` | `TIMESTAMP DEFAULT CURRENT_TIMESTAMP` | :1254 |
| `player_housing` | `expansions_installed` | `INTEGER DEFAULT 0` | :1483 |
| `player_housing` | `housing_label` | `TEXT` | :1637 |
| `player_housing` | `housing_slots` | `INTEGER` | :1638 |
| `player_housing` | `tax_last_check` | `TEXT DEFAULT NULL` | :1535 |
| `player_housing` | `tax_unpaid_months` | `INTEGER DEFAULT 0` | :1536 |
| `polls` | `archived_day` | `TEXT DEFAULT ''` | :1499 |
| `polls` | `closed_at` | `TIMESTAMP` | :1398 |
| `polls` | `closed_by` | `INTEGER` | :1397 |
| `polls` | `closes_at` | `TIMESTAMP` | :1488 |
| `polls` | `is_archived` | `INTEGER DEFAULT 0` | :1498 |
| `reports` | `credited_troops` | `INTEGER` | :1153 |
| `reports` | `paid` | `INTEGER DEFAULT 0` | :1160 |
| `reports` | `total_troops` | `INTEGER DEFAULT 0` | :1151 |
| `statuses` | `sort_order` | `INTEGER DEFAULT 0` | :1111 |
| `users` | `about` | `TEXT DEFAULT ''` | :1136 |
| `users` | `alcohol_strong_used_day` | `TEXT DEFAULT NULL` | :1392 |
| `users` | `alcohol_strong_used_today` | `INTEGER DEFAULT 0` | :1391 |
| `users` | `alcohol_weak_used_day` | `TEXT DEFAULT NULL` | :1390 |
| `users` | `alcohol_weak_used_today` | `INTEGER DEFAULT 0` | :1389 |
| `users` | `ap_recovery_day` | `TEXT DEFAULT NULL` | :1384 |
| `users` | `ap_restored_day` | `TEXT DEFAULT NULL` | :1257 |
| `users` | `ap_restored_today` | `INTEGER DEFAULT 0` | :1258 |
| `users` | `beer_used_day` | `TEXT DEFAULT NULL` | :1387 |
| `users` | `beer_used_today` | `INTEGER DEFAULT 0` | :1386 |
| `users` | `callsign` | `TEXT` | :1342 |
| `users` | `callsign_free_used` | `INTEGER DEFAULT 0` | :1533 |
| `users` | `duel_losses` | `INTEGER DEFAULT 0` | :1262 |
| `users` | `duel_rating` | `INTEGER DEFAULT 0` | :1260 |
| `users` | `duel_wins` | `INTEGER DEFAULT 0` | :1261 |
| `users` | `equipment` | `TEXT DEFAULT '{}'` | :1137 |
| `users` | `fish_sold_day` | `TEXT DEFAULT NULL` | :1413 |
| `users` | `fish_sold_today` | `INTEGER DEFAULT 0` | :1414 |
| `users` | `fishing_bait` | `TEXT DEFAULT ''` | :1340 |
| `users` | `forest_attempts_since_boar` | `INTEGER DEFAULT 0` | :1416 |
| `users` | `forest_attempts_since_wolf` | `INTEGER DEFAULT 0` | :1418 |
| `users` | `forest_sold_day` | `TEXT DEFAULT NULL` | :1428 |
| `users` | `forest_sold_today` | `INTEGER DEFAULT 0` | :1429 |
| `users` | `fountain_used_day` | `TEXT DEFAULT NULL` | :1407 |
| `users` | `fountain_used_today` | `INTEGER DEFAULT 0` | :1408 |
| `users` | `last_active` | `REAL DEFAULT 0` | :1265 |
| `users` | `last_salary_date` | `TIMESTAMP` | :1140 |
| `users` | `legioner` | `INTEGER DEFAULT 0` | :1578 |
| `users` | `logging_attempts_since_owl` | `INTEGER DEFAULT 0` | :1425 |
| `users` | `logging_attempts_since_snake` | `INTEGER DEFAULT 0` | :1424 |
| `users` | `market_license_expires` | `TEXT DEFAULT NULL` | :1532 |
| `users` | `mine_attempts_since_bat` | `INTEGER DEFAULT 0` | :1421 |
| `users` | `notify_enabled` | `INTEGER DEFAULT 1` | :1134 |
| `users` | `profile_public` | `INTEGER DEFAULT 1` | :1135 |
| `users` | `promoted_rank` | `TEXT` | :1114 |
| `users` | `salary` | `INTEGER DEFAULT 0` | :1138 |
| `users` | `salary_debt` | `INTEGER DEFAULT 0` | :1141 |
| `users` | `salary_period_days` | `INTEGER DEFAULT 7` | :1139 |
| `users` | `seaweed_used_day` | `TEXT DEFAULT NULL` | :1381 |
| `users` | `seaweed_used_today` | `INTEGER DEFAULT 0` | :1380 |
| `users` | `shower_used_day` | `TEXT DEFAULT NULL` | :1410 |
| `users` | `shower_used_today` | `INTEGER DEFAULT 0` | :1411 |
| `users` | `special_blocked_until` | `TEXT DEFAULT NULL` | :1395 |
| `users` | `special_fails_today` | `INTEGER DEFAULT 0` | :1394 |
| `users` | `wing` | `TEXT` | :1575 |
| `users` | `xp_balance` | `INTEGER DEFAULT 0` | :1118 |
| `water_fish` | `excluded` | `INTEGER DEFAULT 0` | :1338 |
| `water_fish` | `kind` | `TEXT DEFAULT 'fish'` | :1554 |
| `water_fish` | `super_rare` | `INTEGER DEFAULT 0` | :1557 |
| `wings` | `abbr` | `TEXT DEFAULT ''` | :1374 |
| `wings` | `callsign` | `TEXT DEFAULT ''` | :1376 |
| `wings` | `emoji` | `TEXT DEFAULT ''` | :1377 |
| `wings` | `name` | `TEXT DEFAULT ''` | :1375 |
| `wings` | `num` | `TEXT DEFAULT ''` | :1373 |
| `wings` | `sort_order` | `INTEGER DEFAULT 0` | :1378 |

## 2. Идемпотентные засевы и миграции данных

| Функция | Вызывается из main.py | Назначение (первая строка docstring) | db.py |
|---|---|---|---|
| `backfill_rank_statuses` | — | Разово выдать статусы по текущим званиям всех пилотов (войска и админ-звания). | :5923 |
| `ensure_achievements` | ✅ | Идемпотентно засевает награды-уровни достижений и синхронизирует их. | :12511 |
| `ensure_base_status` | — | Базовый статус «Турист» для каждого нового игрока. | :6169 |
| `ensure_base_statuses` | — | Создаёт базовые статусы иерархии, если их нет. | :6124 |
| `ensure_clan_building` | — | — | :14306 |
| `ensure_duel_items` | ✅ | Товары Дома Дуэлей: дуэльные перчатки (отдельный слот) и клубная карта. | :10198 |
| `ensure_dungeon_enemy_drops` | ✅ | Синхронизирует врагов существующего данжа с DEFAULT_DUNGEON (дропы, HP, награды, | :12017 |
| `ensure_dungeon_reservoir_items` | ✅ | Идемпотентно добавляет предметы водохранилища подземелья (v0.12.0). | :11921 |
| `ensure_dungeon_shop_items` | ✅ | Идемпотентно добавляет предметы данжа (зелье в магазин, трофеи) — для существующих БД. | :11536 |
| `ensure_fishing_enemies` | ✅ | Идемпотентно засевает врагов рыбалки (мутировавший моллюск) из MOLLUSK_SEED. | :9236 |
| `ensure_forest_enemies` | ✅ | Идемпотентно засевает врагов леса (кабан и Белый Волк Севера). | :9211 |
| `ensure_forest_items` | ✅ | Идемпотентно создаёт предметы леса (грибы, добыча кабана, жареные блюда, яд). | :8557 |
| `ensure_forest_mushrooms` | ✅ | Идемпотентно засевает пул грибов леса из FOREST_DEFAULTS. | :8729 |
| `ensure_forest_zones` | ✅ | Разовый перенос старого пула леса в зону поляны и засев пула опушки. | :8972 |
| `ensure_kvp_award` | ✅ | — | :10457 |
| `ensure_kvp_items` | ✅ | Обеспечивает эксклюзивный предмет К.В.П. — «Сержантскую трость». | :10171 |
| `ensure_kvp_user` | — | Гарантирует наличие строки прогресса К.В.П. для игрока. | :10644 |
| `ensure_life_items` | ✅ | Идемпотентно добавляет предметы жилья, мебели, семян, ресурсов и продовольствия. | :11742 |
| `ensure_logging_enemies` | ✅ | Идемпотентно засевает врагов Лесозаготовки (Змея и Неясыть). | :8718 |
| `ensure_logging_items` | ✅ | Идемпотентно создаёт предметы Лесозаготовки (топор, бревна, дропы). | :8675 |
| `ensure_market_license_item` | ✅ | Идемпотентно добавляет «Торговую лицензию» в магазин. | :9720 |
| `ensure_mine_enemies` | ✅ | Идемпотентно засевает врагов копи (Летучая мышь) из MINE_BAT_SEED. | :8666 |
| `ensure_mine_items` | ✅ | Идемпотентно создаёт предметы Железной копи (кирка, руда, самоцветы). | :8635 |
| `ensure_mollusk_items` | ✅ | Идемпотентно создаёт предметы моллюска (из его добычи и готового блюда). | :9242 |
| `ensure_player_housing` | — | Возвращает жильё игрока, создавая муниципальную квартиру для пилота при первом обращении. | :12148 |
| `ensure_rank_statuses_for_troops` | — | Выдать статус по текущему званию игрока (по войскам или админ-назначению). | :5911 |
| `ensure_recipe_shop_item` | — | Синхронизирует товар-рецепт «Рецепт: <name>» с рецептом (менеджер). | :12924 |
| `ensure_recipe_shop_items` | ✅ | Создаёт в магазине предметы-рецепты категории 'recipes'. | :13986 |
| `ensure_recipes` | ✅ | Идемпотентно засевает рецепты и синхронизирует уже существующие. | :12774 |
| `ensure_tourist_booklet` | ✅ | Создаёт предмет «Буклет туриста» и награду «Опытный турист», если их нет. | :10493 |
| `ensure_user_recipes_backfill` | ✅ | Разово открывает все рецепты существующим игрокам. | :14132 |
| `ensure_water_fish` | ✅ | Идемпотентно засевает water_fish из дефолтов. Правившие админом строки | :8148 |
| `migrate_legacy_junk` | ✅ | Переносит старые копии мусора (сапог, водоросли) из инвентаря в улов. | :7994 |
| `seed_default_items` | ✅ | Заполняет магазин базовым набором товаров, если он пуст и не было своих товаров. | :9894 |
| `seed_dungeon` | ✅ | — | :10049 |
| `seed_kvp` | ✅ | Создаёт тренировочный данж К.В.П. с врагами (Ефрейтор, Старший сержант), если его нет. | :10120 |
| `seed_locations` | — | Засеивает базовые локации города (Ратуша, Библиотека) как пример управляемого доступа. | :1765 |

## 3. Отдельные скрипты миграций

- `migrate_113.py` — Проверка миграций 0.19.0 на чистой БД: колонки polls, таблица rep_speeches.
- `migrate_113_old.py` — Миграция 0.19.0 поверх БД со старой схемой polls (без closes_at/is_archived).

