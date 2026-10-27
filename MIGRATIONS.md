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

Всего вызовов: **173**; таблиц: **25**.

| Таблица | Колонка | Тип / значение по умолчанию | db.py |
|---|---|---|---|
| `awards` | `achievement_key` | `TEXT DEFAULT NULL` | :1336 |
| `awards` | `achievement_level` | `INTEGER DEFAULT 0` | :1337 |
| `awards` | `bonus_attack` | `INTEGER DEFAULT 0` | :1315 |
| `awards` | `bonus_crit` | `INTEGER DEFAULT 0` | :1322 |
| `awards` | `bonus_defense` | `INTEGER DEFAULT 0` | :1316 |
| `awards` | `bonus_dodge` | `INTEGER DEFAULT 0` | :1317 |
| `awards` | `bonus_fishing` | `INTEGER DEFAULT 0` | :1318 |
| `awards` | `bonus_hp` | `INTEGER DEFAULT 0` | :1319 |
| `awards` | `bonus_json` | `TEXT DEFAULT '{}'` | :1338 |
| `awards` | `bonus_report_tax` | `INTEGER DEFAULT 0` | :1326 |
| `awards` | `bonus_shop_discount` | `INTEGER DEFAULT 0` | :1325 |
| `awards` | `image` | `TEXT` | :1314 |
| `awards` | `monthly_nm` | `INTEGER DEFAULT 0` | :1330 |
| `awards` | `reward_nm` | `INTEGER DEFAULT 0` | :1329 |
| `buildings` | `required_status` | `TEXT` | :1082 |
| `clan_buildings` | `building_photo_file_id` | `TEXT` | :1654 |
| `dungeon_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1250 |
| `dungeon_enemies` | `admin_tuned` | `INTEGER DEFAULT 0` | :1286 |
| `dungeon_enemies` | `armor` | `INTEGER DEFAULT 0` | :1246 |
| `dungeon_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1510 |
| `dungeon_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1511 |
| `dungeon_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1248 |
| `dungeon_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1249 |
| `dungeon_enemies` | `damage_max` | `INTEGER DEFAULT 0` | :1245 |
| `dungeon_enemies` | `damage_min` | `INTEGER DEFAULT 0` | :1244 |
| `dungeon_enemies` | `description` | `TEXT` | :1242 |
| `dungeon_enemies` | `dodge` | `INTEGER DEFAULT 0` | :1243 |
| `dungeon_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1247 |
| `dungeon_enemies` | `drops` | `TEXT DEFAULT '[]'` | :1238 |
| `dungeon_enemies` | `frostbite_chance` | `INTEGER DEFAULT 0` | :1512 |
| `dungeon_enemies` | `image` | `TEXT` | :1239 |
| `dungeon_enemies` | `poison_chance` | `INTEGER DEFAULT 0` | :1240 |
| `dungeon_enemies` | `poison_dmg` | `INTEGER DEFAULT 0` | :1241 |
| `dungeons` | `is_training` | `INTEGER DEFAULT 0` | :1501 |
| `dungeons` | `photo_dawn` | `TEXT` | :1299 |
| `dungeons` | `photo_day` | `TEXT` | :1300 |
| `dungeons` | `photo_night` | `TEXT` | :1302 |
| `dungeons` | `photo_rope` | `TEXT` | :1305 |
| `dungeons` | `photo_sunset` | `TEXT` | :1301 |
| `dungeons` | `photo_water` | `TEXT` | :1304 |
| `dungeons` | `rooms_map` | `TEXT` | :1517 |
| `fish_catches` | `expires_at` | `TIMESTAMP` | :1375 |
| `fish_catches` | `kind` | `TEXT DEFAULT 'fish'` | :1523 |
| `fishing_enemies` | `armor` | `INTEGER DEFAULT 0` | :1261 |
| `fishing_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1259 |
| `fishing_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1260 |
| `forest_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1255 |
| `forest_enemies` | `armor` | `INTEGER DEFAULT 0` | :1251 |
| `forest_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1257 |
| `forest_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1258 |
| `forest_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1253 |
| `forest_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1254 |
| `forest_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1252 |
| `forest_mushrooms` | `zone` | `TEXT DEFAULT 'clearing'` | :1420 |
| `housing_slots` | `embedded` | `INTEGER DEFAULT 0` | :1451 |
| `inventory` | `expires_at` | `TIMESTAMP` | :1370 |
| `inventory` | `plant_data` | `TEXT` | :1372 |
| `items` | `armor` | `INTEGER DEFAULT 0` | :1112 |
| `items` | `crit_chance` | `INTEGER DEFAULT 0` | :1115 |
| `items` | `crit_mult` | `REAL DEFAULT 0` | :1116 |
| `items` | `cure_frostbite` | `INTEGER DEFAULT 0` | :1514 |
| `items` | `cure_poison` | `INTEGER DEFAULT 0` | :1287 |
| `items` | `damage` | `INTEGER DEFAULT 0` | :1236 |
| `items` | `drink_effect` | `TEXT DEFAULT NULL` | :1358 |
| `items` | `equip_slot` | `TEXT` | :1118 |
| `items` | `heal` | `INTEGER DEFAULT 0` | :1237 |
| `items` | `housing_slots` | `INTEGER` | :1606 |
| `items` | `housing_type` | `TEXT` | :1605 |
| `items` | `loot_only` | `INTEGER DEFAULT 0` | :1611 |
| `items` | `market_ok` | `INTEGER DEFAULT 0` | :1520 |
| `items` | `plant_name` | `TEXT` | :1530 |
| `items` | `regen` | `INTEGER DEFAULT 0` | :1297 |
| `items` | `required_status` | `TEXT` | :1081 |
| `items` | `weapon_effect` | `TEXT` | :1541 |
| `items` | `weapon_effect_chance` | `INTEGER DEFAULT 0` | :1542 |
| `items` | `weapon_effect_dmg` | `INTEGER DEFAULT 0` | :1543 |
| `locations` | `clearing_photo` | `TEXT DEFAULT NULL` | :1406 |
| `locations` | `glade_photo` | `TEXT DEFAULT NULL` | :1405 |
| `locations` | `logging_photo` | `TEXT DEFAULT NULL` | :1415 |
| `locations` | `mine_level_photo` | `TEXT DEFAULT NULL` | :1409 |
| `locations` | `photo_dawn` | `TEXT` | :1289 |
| `locations` | `photo_day` | `TEXT` | :1290 |
| `locations` | `photo_night` | `TEXT` | :1292 |
| `locations` | `photo_sunset` | `TEXT` | :1291 |
| `locations` | `preview_photo` | `TEXT` | :1288 |
| `locations` | `season_photos` | `TEXT DEFAULT NULL` | :1402 |
| `locations` | `storage_photo` | `TEXT DEFAULT NULL` | :1411 |
| `locations` | `visits` | `INTEGER DEFAULT 0` | :1294 |
| `logging_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1276 |
| `logging_enemies` | `armor` | `INTEGER DEFAULT 0` | :1272 |
| `logging_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1274 |
| `logging_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1275 |
| `logging_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1273 |
| `market_fish` | `base_price` | `INTEGER DEFAULT 0` | :1504 |
| `mine_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1267 |
| `mine_enemies` | `armor` | `INTEGER DEFAULT 0` | :1263 |
| `mine_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1268 |
| `mine_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1269 |
| `mine_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1265 |
| `mine_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1266 |
| `mine_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1264 |
| `nii_reports` | `photo2_file_id` | `TEXT DEFAULT NULL` | :1340 |
| `player_dungeon_run` | `loot_nm` | `INTEGER DEFAULT 0` | :1223 |
| `player_dungeon_run` | `started_at` | `TIMESTAMP DEFAULT CURRENT_TIMESTAMP` | :1224 |
| `player_housing` | `expansions_installed` | `INTEGER DEFAULT 0` | :1453 |
| `player_housing` | `housing_label` | `TEXT` | :1607 |
| `player_housing` | `housing_slots` | `INTEGER` | :1608 |
| `player_housing` | `tax_last_check` | `TEXT DEFAULT NULL` | :1505 |
| `player_housing` | `tax_unpaid_months` | `INTEGER DEFAULT 0` | :1506 |
| `polls` | `archived_day` | `TEXT DEFAULT ''` | :1469 |
| `polls` | `closed_at` | `TIMESTAMP` | :1368 |
| `polls` | `closed_by` | `INTEGER` | :1367 |
| `polls` | `closes_at` | `TIMESTAMP` | :1458 |
| `polls` | `is_archived` | `INTEGER DEFAULT 0` | :1468 |
| `reports` | `credited_troops` | `INTEGER` | :1123 |
| `reports` | `paid` | `INTEGER DEFAULT 0` | :1130 |
| `reports` | `total_troops` | `INTEGER DEFAULT 0` | :1121 |
| `statuses` | `sort_order` | `INTEGER DEFAULT 0` | :1083 |
| `users` | `about` | `TEXT DEFAULT ''` | :1106 |
| `users` | `alcohol_strong_used_day` | `TEXT DEFAULT NULL` | :1362 |
| `users` | `alcohol_strong_used_today` | `INTEGER DEFAULT 0` | :1361 |
| `users` | `alcohol_weak_used_day` | `TEXT DEFAULT NULL` | :1360 |
| `users` | `alcohol_weak_used_today` | `INTEGER DEFAULT 0` | :1359 |
| `users` | `ap_recovery_day` | `TEXT DEFAULT NULL` | :1354 |
| `users` | `ap_restored_day` | `TEXT DEFAULT NULL` | :1227 |
| `users` | `ap_restored_today` | `INTEGER DEFAULT 0` | :1228 |
| `users` | `beer_used_day` | `TEXT DEFAULT NULL` | :1357 |
| `users` | `beer_used_today` | `INTEGER DEFAULT 0` | :1356 |
| `users` | `callsign` | `TEXT` | :1312 |
| `users` | `callsign_free_used` | `INTEGER DEFAULT 0` | :1503 |
| `users` | `duel_losses` | `INTEGER DEFAULT 0` | :1232 |
| `users` | `duel_rating` | `INTEGER DEFAULT 0` | :1230 |
| `users` | `duel_wins` | `INTEGER DEFAULT 0` | :1231 |
| `users` | `equipment` | `TEXT DEFAULT '{}'` | :1107 |
| `users` | `fish_sold_day` | `TEXT DEFAULT NULL` | :1383 |
| `users` | `fish_sold_today` | `INTEGER DEFAULT 0` | :1384 |
| `users` | `fishing_bait` | `TEXT DEFAULT ''` | :1310 |
| `users` | `forest_attempts_since_boar` | `INTEGER DEFAULT 0` | :1386 |
| `users` | `forest_attempts_since_wolf` | `INTEGER DEFAULT 0` | :1388 |
| `users` | `forest_sold_day` | `TEXT DEFAULT NULL` | :1398 |
| `users` | `forest_sold_today` | `INTEGER DEFAULT 0` | :1399 |
| `users` | `fountain_used_day` | `TEXT DEFAULT NULL` | :1377 |
| `users` | `fountain_used_today` | `INTEGER DEFAULT 0` | :1378 |
| `users` | `last_active` | `REAL DEFAULT 0` | :1235 |
| `users` | `last_salary_date` | `TIMESTAMP` | :1110 |
| `users` | `legioner` | `INTEGER DEFAULT 0` | :1548 |
| `users` | `logging_attempts_since_owl` | `INTEGER DEFAULT 0` | :1395 |
| `users` | `logging_attempts_since_snake` | `INTEGER DEFAULT 0` | :1394 |
| `users` | `market_license_expires` | `TEXT DEFAULT NULL` | :1502 |
| `users` | `mine_attempts_since_bat` | `INTEGER DEFAULT 0` | :1391 |
| `users` | `notify_enabled` | `INTEGER DEFAULT 1` | :1104 |
| `users` | `profile_public` | `INTEGER DEFAULT 1` | :1105 |
| `users` | `promoted_rank` | `TEXT` | :1084 |
| `users` | `salary` | `INTEGER DEFAULT 0` | :1108 |
| `users` | `salary_debt` | `INTEGER DEFAULT 0` | :1111 |
| `users` | `salary_period_days` | `INTEGER DEFAULT 7` | :1109 |
| `users` | `seaweed_used_day` | `TEXT DEFAULT NULL` | :1351 |
| `users` | `seaweed_used_today` | `INTEGER DEFAULT 0` | :1350 |
| `users` | `shower_used_day` | `TEXT DEFAULT NULL` | :1380 |
| `users` | `shower_used_today` | `INTEGER DEFAULT 0` | :1381 |
| `users` | `special_blocked_until` | `TEXT DEFAULT NULL` | :1365 |
| `users` | `special_fails_today` | `INTEGER DEFAULT 0` | :1364 |
| `users` | `wing` | `TEXT` | :1545 |
| `users` | `xp_balance` | `INTEGER DEFAULT 0` | :1088 |
| `water_fish` | `excluded` | `INTEGER DEFAULT 0` | :1308 |
| `water_fish` | `kind` | `TEXT DEFAULT 'fish'` | :1524 |
| `water_fish` | `super_rare` | `INTEGER DEFAULT 0` | :1527 |
| `wings` | `abbr` | `TEXT DEFAULT ''` | :1344 |
| `wings` | `callsign` | `TEXT DEFAULT ''` | :1346 |
| `wings` | `emoji` | `TEXT DEFAULT ''` | :1347 |
| `wings` | `name` | `TEXT DEFAULT ''` | :1345 |
| `wings` | `num` | `TEXT DEFAULT ''` | :1343 |
| `wings` | `sort_order` | `INTEGER DEFAULT 0` | :1348 |

## 2. Идемпотентные засевы и миграции данных

| Функция | Вызывается из main.py | Назначение (первая строка docstring) | db.py |
|---|---|---|---|
| `backfill_rank_statuses` | — | Разово выдать статусы по текущим званиям всех пилотов (войска и админ-звания). | :5813 |
| `ensure_achievements` | ✅ | Идемпотентно засевает награды-уровни достижений и синхронизирует их. | :12392 |
| `ensure_base_status` | — | Базовый статус «Турист» для каждого нового игрока. | :6050 |
| `ensure_base_statuses` | — | Создаёт базовые статусы иерархии, если их нет. | :6005 |
| `ensure_clan_building` | — | — | :14092 |
| `ensure_duel_items` | ✅ | Товары Дома Дуэлей: дуэльные перчатки (отдельный слот) и клубная карта. | :10079 |
| `ensure_dungeon_enemy_drops` | ✅ | Синхронизирует врагов существующего данжа с DEFAULT_DUNGEON (дропы, HP, награды, | :11898 |
| `ensure_dungeon_reservoir_items` | ✅ | Идемпотентно добавляет предметы водохранилища подземелья (v0.12.0). | :11802 |
| `ensure_dungeon_shop_items` | ✅ | Идемпотентно добавляет предметы данжа (зелье в магазин, трофеи) — для существующих БД. | :11417 |
| `ensure_fishing_enemies` | ✅ | Идемпотентно засевает врагов рыбалки (мутировавший моллюск) из MOLLUSK_SEED. | :9117 |
| `ensure_forest_enemies` | ✅ | Идемпотентно засевает врагов леса (кабан и Белый Волк Севера). | :9092 |
| `ensure_forest_items` | ✅ | Идемпотентно создаёт предметы леса (грибы, добыча кабана, жареные блюда, яд). | :8438 |
| `ensure_forest_mushrooms` | ✅ | Идемпотентно засевает пул грибов леса из FOREST_DEFAULTS. | :8610 |
| `ensure_forest_zones` | ✅ | Разовый перенос старого пула леса в зону поляны и засев пула опушки. | :8853 |
| `ensure_kvp_award` | ✅ | — | :10338 |
| `ensure_kvp_items` | ✅ | Обеспечивает эксклюзивный предмет К.В.П. — «Сержантскую трость». | :10052 |
| `ensure_kvp_user` | — | Гарантирует наличие строки прогресса К.В.П. для игрока. | :10525 |
| `ensure_life_items` | ✅ | Идемпотентно добавляет предметы жилья, мебели, семян, ресурсов и продовольствия. | :11623 |
| `ensure_logging_enemies` | ✅ | Идемпотентно засевает врагов Лесозаготовки (Змея и Неясыть). | :8599 |
| `ensure_logging_items` | ✅ | Идемпотентно создаёт предметы Лесозаготовки (топор, бревна, дропы). | :8556 |
| `ensure_market_license_item` | ✅ | Идемпотентно добавляет «Торговую лицензию» в магазин. | :9601 |
| `ensure_mine_enemies` | ✅ | Идемпотентно засевает врагов копи (Летучая мышь) из MINE_BAT_SEED. | :8547 |
| `ensure_mine_items` | ✅ | Идемпотентно создаёт предметы Железной копи (кирка, руда, самоцветы). | :8516 |
| `ensure_mollusk_items` | ✅ | Идемпотентно создаёт предметы моллюска (из его добычи и готового блюда). | :9123 |
| `ensure_player_housing` | — | Возвращает жильё игрока, создавая муниципальную квартиру для пилота при первом обращении. | :12029 |
| `ensure_rank_statuses_for_troops` | — | Выдать статус по текущему званию игрока (по войскам или админ-назначению). | :5801 |
| `ensure_recipe_shop_item` | — | Синхронизирует товар-рецепт «Рецепт: <name>» с рецептом (менеджер). | :12805 |
| `ensure_recipe_shop_items` | ✅ | Создаёт в магазине предметы-рецепты категории 'recipes'. | :13863 |
| `ensure_recipes` | ✅ | Идемпотентно засевает рецепты и синхронизирует уже существующие. | :12655 |
| `ensure_tourist_booklet` | ✅ | Создаёт предмет «Буклет туриста» и награду «Опытный турист», если их нет. | :10374 |
| `ensure_user_recipes_backfill` | ✅ | Разово открывает все рецепты существующим игрокам. | :14009 |
| `ensure_water_fish` | ✅ | Идемпотентно засевает water_fish из дефолтов. Правившие админом строки | :8029 |
| `migrate_legacy_junk` | ✅ | Переносит старые копии мусора (сапог, водоросли) из инвентаря в улов. | :7875 |
| `seed_default_items` | ✅ | Заполняет магазин базовым набором товаров, если он пуст и не было своих товаров. | :9775 |
| `seed_dungeon` | ✅ | — | :9930 |
| `seed_kvp` | ✅ | Создаёт тренировочный данж К.В.П. с врагами (Ефрейтор, Старший сержант), если его нет. | :10001 |
| `seed_locations` | — | Засеивает базовые локации города (Ратуша, Библиотека) как пример управляемого доступа. | :1735 |

## 3. Отдельные скрипты миграций

- `migrate_113.py` — Проверка миграций 0.19.0 на чистой БД: колонки polls, таблица rep_speeches.
- `migrate_113_old.py` — Миграция 0.19.0 поверх БД со старой схемой polls (без closes_at/is_archived).

