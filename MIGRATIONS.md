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
| `awards` | `achievement_key` | `TEXT DEFAULT NULL` | :1339 |
| `awards` | `achievement_level` | `INTEGER DEFAULT 0` | :1340 |
| `awards` | `bonus_attack` | `INTEGER DEFAULT 0` | :1318 |
| `awards` | `bonus_crit` | `INTEGER DEFAULT 0` | :1325 |
| `awards` | `bonus_defense` | `INTEGER DEFAULT 0` | :1319 |
| `awards` | `bonus_dodge` | `INTEGER DEFAULT 0` | :1320 |
| `awards` | `bonus_fishing` | `INTEGER DEFAULT 0` | :1321 |
| `awards` | `bonus_hp` | `INTEGER DEFAULT 0` | :1322 |
| `awards` | `bonus_json` | `TEXT DEFAULT '{}'` | :1341 |
| `awards` | `bonus_report_tax` | `INTEGER DEFAULT 0` | :1329 |
| `awards` | `bonus_shop_discount` | `INTEGER DEFAULT 0` | :1328 |
| `awards` | `image` | `TEXT` | :1317 |
| `awards` | `monthly_nm` | `INTEGER DEFAULT 0` | :1333 |
| `awards` | `reward_nm` | `INTEGER DEFAULT 0` | :1332 |
| `buildings` | `required_status` | `TEXT` | :1083 |
| `clan_buildings` | `building_photo_file_id` | `TEXT` | :1657 |
| `clan_members` | `role` | `TEXT NOT NULL DEFAULT 'member'` | :1085 |
| `dungeon_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1253 |
| `dungeon_enemies` | `admin_tuned` | `INTEGER DEFAULT 0` | :1289 |
| `dungeon_enemies` | `armor` | `INTEGER DEFAULT 0` | :1249 |
| `dungeon_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1513 |
| `dungeon_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1514 |
| `dungeon_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1251 |
| `dungeon_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1252 |
| `dungeon_enemies` | `damage_max` | `INTEGER DEFAULT 0` | :1248 |
| `dungeon_enemies` | `damage_min` | `INTEGER DEFAULT 0` | :1247 |
| `dungeon_enemies` | `description` | `TEXT` | :1245 |
| `dungeon_enemies` | `dodge` | `INTEGER DEFAULT 0` | :1246 |
| `dungeon_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1250 |
| `dungeon_enemies` | `drops` | `TEXT DEFAULT '[]'` | :1241 |
| `dungeon_enemies` | `frostbite_chance` | `INTEGER DEFAULT 0` | :1515 |
| `dungeon_enemies` | `image` | `TEXT` | :1242 |
| `dungeon_enemies` | `poison_chance` | `INTEGER DEFAULT 0` | :1243 |
| `dungeon_enemies` | `poison_dmg` | `INTEGER DEFAULT 0` | :1244 |
| `dungeons` | `is_training` | `INTEGER DEFAULT 0` | :1504 |
| `dungeons` | `photo_dawn` | `TEXT` | :1302 |
| `dungeons` | `photo_day` | `TEXT` | :1303 |
| `dungeons` | `photo_night` | `TEXT` | :1305 |
| `dungeons` | `photo_rope` | `TEXT` | :1308 |
| `dungeons` | `photo_sunset` | `TEXT` | :1304 |
| `dungeons` | `photo_water` | `TEXT` | :1307 |
| `dungeons` | `rooms_map` | `TEXT` | :1520 |
| `fish_catches` | `expires_at` | `TIMESTAMP` | :1378 |
| `fish_catches` | `kind` | `TEXT DEFAULT 'fish'` | :1526 |
| `fishing_enemies` | `armor` | `INTEGER DEFAULT 0` | :1264 |
| `fishing_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1262 |
| `fishing_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1263 |
| `forest_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1258 |
| `forest_enemies` | `armor` | `INTEGER DEFAULT 0` | :1254 |
| `forest_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1260 |
| `forest_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1261 |
| `forest_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1256 |
| `forest_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1257 |
| `forest_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1255 |
| `forest_mushrooms` | `zone` | `TEXT DEFAULT 'clearing'` | :1423 |
| `housing_slots` | `embedded` | `INTEGER DEFAULT 0` | :1454 |
| `inventory` | `expires_at` | `TIMESTAMP` | :1373 |
| `inventory` | `plant_data` | `TEXT` | :1375 |
| `items` | `armor` | `INTEGER DEFAULT 0` | :1115 |
| `items` | `crit_chance` | `INTEGER DEFAULT 0` | :1118 |
| `items` | `crit_mult` | `REAL DEFAULT 0` | :1119 |
| `items` | `cure_frostbite` | `INTEGER DEFAULT 0` | :1517 |
| `items` | `cure_poison` | `INTEGER DEFAULT 0` | :1290 |
| `items` | `damage` | `INTEGER DEFAULT 0` | :1239 |
| `items` | `drink_effect` | `TEXT DEFAULT NULL` | :1361 |
| `items` | `equip_slot` | `TEXT` | :1121 |
| `items` | `heal` | `INTEGER DEFAULT 0` | :1240 |
| `items` | `housing_slots` | `INTEGER` | :1609 |
| `items` | `housing_type` | `TEXT` | :1608 |
| `items` | `loot_only` | `INTEGER DEFAULT 0` | :1614 |
| `items` | `market_ok` | `INTEGER DEFAULT 0` | :1523 |
| `items` | `plant_name` | `TEXT` | :1533 |
| `items` | `regen` | `INTEGER DEFAULT 0` | :1300 |
| `items` | `required_status` | `TEXT` | :1082 |
| `items` | `weapon_effect` | `TEXT` | :1544 |
| `items` | `weapon_effect_chance` | `INTEGER DEFAULT 0` | :1545 |
| `items` | `weapon_effect_dmg` | `INTEGER DEFAULT 0` | :1546 |
| `locations` | `clearing_photo` | `TEXT DEFAULT NULL` | :1409 |
| `locations` | `glade_photo` | `TEXT DEFAULT NULL` | :1408 |
| `locations` | `logging_photo` | `TEXT DEFAULT NULL` | :1418 |
| `locations` | `mine_level_photo` | `TEXT DEFAULT NULL` | :1412 |
| `locations` | `photo_dawn` | `TEXT` | :1292 |
| `locations` | `photo_day` | `TEXT` | :1293 |
| `locations` | `photo_night` | `TEXT` | :1295 |
| `locations` | `photo_sunset` | `TEXT` | :1294 |
| `locations` | `preview_photo` | `TEXT` | :1291 |
| `locations` | `season_photos` | `TEXT DEFAULT NULL` | :1405 |
| `locations` | `storage_photo` | `TEXT DEFAULT NULL` | :1414 |
| `locations` | `visits` | `INTEGER DEFAULT 0` | :1297 |
| `logging_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1279 |
| `logging_enemies` | `armor` | `INTEGER DEFAULT 0` | :1275 |
| `logging_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1277 |
| `logging_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1278 |
| `logging_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1276 |
| `market_fish` | `base_price` | `INTEGER DEFAULT 0` | :1507 |
| `mine_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1270 |
| `mine_enemies` | `armor` | `INTEGER DEFAULT 0` | :1266 |
| `mine_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1271 |
| `mine_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1272 |
| `mine_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1268 |
| `mine_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1269 |
| `mine_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1267 |
| `nii_reports` | `photo2_file_id` | `TEXT DEFAULT NULL` | :1343 |
| `player_dungeon_run` | `loot_nm` | `INTEGER DEFAULT 0` | :1226 |
| `player_dungeon_run` | `started_at` | `TIMESTAMP DEFAULT CURRENT_TIMESTAMP` | :1227 |
| `player_housing` | `expansions_installed` | `INTEGER DEFAULT 0` | :1456 |
| `player_housing` | `housing_label` | `TEXT` | :1610 |
| `player_housing` | `housing_slots` | `INTEGER` | :1611 |
| `player_housing` | `tax_last_check` | `TEXT DEFAULT NULL` | :1508 |
| `player_housing` | `tax_unpaid_months` | `INTEGER DEFAULT 0` | :1509 |
| `polls` | `archived_day` | `TEXT DEFAULT ''` | :1472 |
| `polls` | `closed_at` | `TIMESTAMP` | :1371 |
| `polls` | `closed_by` | `INTEGER` | :1370 |
| `polls` | `closes_at` | `TIMESTAMP` | :1461 |
| `polls` | `is_archived` | `INTEGER DEFAULT 0` | :1471 |
| `reports` | `credited_troops` | `INTEGER` | :1126 |
| `reports` | `paid` | `INTEGER DEFAULT 0` | :1133 |
| `reports` | `total_troops` | `INTEGER DEFAULT 0` | :1124 |
| `statuses` | `sort_order` | `INTEGER DEFAULT 0` | :1084 |
| `users` | `about` | `TEXT DEFAULT ''` | :1109 |
| `users` | `alcohol_strong_used_day` | `TEXT DEFAULT NULL` | :1365 |
| `users` | `alcohol_strong_used_today` | `INTEGER DEFAULT 0` | :1364 |
| `users` | `alcohol_weak_used_day` | `TEXT DEFAULT NULL` | :1363 |
| `users` | `alcohol_weak_used_today` | `INTEGER DEFAULT 0` | :1362 |
| `users` | `ap_recovery_day` | `TEXT DEFAULT NULL` | :1357 |
| `users` | `ap_restored_day` | `TEXT DEFAULT NULL` | :1230 |
| `users` | `ap_restored_today` | `INTEGER DEFAULT 0` | :1231 |
| `users` | `beer_used_day` | `TEXT DEFAULT NULL` | :1360 |
| `users` | `beer_used_today` | `INTEGER DEFAULT 0` | :1359 |
| `users` | `callsign` | `TEXT` | :1315 |
| `users` | `callsign_free_used` | `INTEGER DEFAULT 0` | :1506 |
| `users` | `duel_losses` | `INTEGER DEFAULT 0` | :1235 |
| `users` | `duel_rating` | `INTEGER DEFAULT 0` | :1233 |
| `users` | `duel_wins` | `INTEGER DEFAULT 0` | :1234 |
| `users` | `equipment` | `TEXT DEFAULT '{}'` | :1110 |
| `users` | `fish_sold_day` | `TEXT DEFAULT NULL` | :1386 |
| `users` | `fish_sold_today` | `INTEGER DEFAULT 0` | :1387 |
| `users` | `fishing_bait` | `TEXT DEFAULT ''` | :1313 |
| `users` | `forest_attempts_since_boar` | `INTEGER DEFAULT 0` | :1389 |
| `users` | `forest_attempts_since_wolf` | `INTEGER DEFAULT 0` | :1391 |
| `users` | `forest_sold_day` | `TEXT DEFAULT NULL` | :1401 |
| `users` | `forest_sold_today` | `INTEGER DEFAULT 0` | :1402 |
| `users` | `fountain_used_day` | `TEXT DEFAULT NULL` | :1380 |
| `users` | `fountain_used_today` | `INTEGER DEFAULT 0` | :1381 |
| `users` | `last_active` | `REAL DEFAULT 0` | :1238 |
| `users` | `last_salary_date` | `TIMESTAMP` | :1113 |
| `users` | `legioner` | `INTEGER DEFAULT 0` | :1551 |
| `users` | `logging_attempts_since_owl` | `INTEGER DEFAULT 0` | :1398 |
| `users` | `logging_attempts_since_snake` | `INTEGER DEFAULT 0` | :1397 |
| `users` | `market_license_expires` | `TEXT DEFAULT NULL` | :1505 |
| `users` | `mine_attempts_since_bat` | `INTEGER DEFAULT 0` | :1394 |
| `users` | `notify_enabled` | `INTEGER DEFAULT 1` | :1107 |
| `users` | `profile_public` | `INTEGER DEFAULT 1` | :1108 |
| `users` | `promoted_rank` | `TEXT` | :1087 |
| `users` | `salary` | `INTEGER DEFAULT 0` | :1111 |
| `users` | `salary_debt` | `INTEGER DEFAULT 0` | :1114 |
| `users` | `salary_period_days` | `INTEGER DEFAULT 7` | :1112 |
| `users` | `seaweed_used_day` | `TEXT DEFAULT NULL` | :1354 |
| `users` | `seaweed_used_today` | `INTEGER DEFAULT 0` | :1353 |
| `users` | `shower_used_day` | `TEXT DEFAULT NULL` | :1383 |
| `users` | `shower_used_today` | `INTEGER DEFAULT 0` | :1384 |
| `users` | `special_blocked_until` | `TEXT DEFAULT NULL` | :1368 |
| `users` | `special_fails_today` | `INTEGER DEFAULT 0` | :1367 |
| `users` | `wing` | `TEXT` | :1548 |
| `users` | `xp_balance` | `INTEGER DEFAULT 0` | :1091 |
| `water_fish` | `excluded` | `INTEGER DEFAULT 0` | :1311 |
| `water_fish` | `kind` | `TEXT DEFAULT 'fish'` | :1527 |
| `water_fish` | `super_rare` | `INTEGER DEFAULT 0` | :1530 |
| `wings` | `abbr` | `TEXT DEFAULT ''` | :1347 |
| `wings` | `callsign` | `TEXT DEFAULT ''` | :1349 |
| `wings` | `emoji` | `TEXT DEFAULT ''` | :1350 |
| `wings` | `name` | `TEXT DEFAULT ''` | :1348 |
| `wings` | `num` | `TEXT DEFAULT ''` | :1346 |
| `wings` | `sort_order` | `INTEGER DEFAULT 0` | :1351 |

## 2. Идемпотентные засевы и миграции данных

| Функция | Вызывается из main.py | Назначение (первая строка docstring) | db.py |
|---|---|---|---|
| `backfill_rank_statuses` | — | Разово выдать статусы по текущим званиям всех пилотов (войска и админ-звания). | :5827 |
| `ensure_achievements` | ✅ | Идемпотентно засевает награды-уровни достижений и синхронизирует их. | :12406 |
| `ensure_base_status` | — | Базовый статус «Турист» для каждого нового игрока. | :6064 |
| `ensure_base_statuses` | — | Создаёт базовые статусы иерархии, если их нет. | :6019 |
| `ensure_clan_building` | — | — | :14191 |
| `ensure_duel_items` | ✅ | Товары Дома Дуэлей: дуэльные перчатки (отдельный слот) и клубная карта. | :10093 |
| `ensure_dungeon_enemy_drops` | ✅ | Синхронизирует врагов существующего данжа с DEFAULT_DUNGEON (дропы, HP, награды, | :11912 |
| `ensure_dungeon_reservoir_items` | ✅ | Идемпотентно добавляет предметы водохранилища подземелья (v0.12.0). | :11816 |
| `ensure_dungeon_shop_items` | ✅ | Идемпотентно добавляет предметы данжа (зелье в магазин, трофеи) — для существующих БД. | :11431 |
| `ensure_fishing_enemies` | ✅ | Идемпотентно засевает врагов рыбалки (мутировавший моллюск) из MOLLUSK_SEED. | :9131 |
| `ensure_forest_enemies` | ✅ | Идемпотентно засевает врагов леса (кабан и Белый Волк Севера). | :9106 |
| `ensure_forest_items` | ✅ | Идемпотентно создаёт предметы леса (грибы, добыча кабана, жареные блюда, яд). | :8452 |
| `ensure_forest_mushrooms` | ✅ | Идемпотентно засевает пул грибов леса из FOREST_DEFAULTS. | :8624 |
| `ensure_forest_zones` | ✅ | Разовый перенос старого пула леса в зону поляны и засев пула опушки. | :8867 |
| `ensure_kvp_award` | ✅ | — | :10352 |
| `ensure_kvp_items` | ✅ | Обеспечивает эксклюзивный предмет К.В.П. — «Сержантскую трость». | :10066 |
| `ensure_kvp_user` | — | Гарантирует наличие строки прогресса К.В.П. для игрока. | :10539 |
| `ensure_life_items` | ✅ | Идемпотентно добавляет предметы жилья, мебели, семян, ресурсов и продовольствия. | :11637 |
| `ensure_logging_enemies` | ✅ | Идемпотентно засевает врагов Лесозаготовки (Змея и Неясыть). | :8613 |
| `ensure_logging_items` | ✅ | Идемпотентно создаёт предметы Лесозаготовки (топор, бревна, дропы). | :8570 |
| `ensure_market_license_item` | ✅ | Идемпотентно добавляет «Торговую лицензию» в магазин. | :9615 |
| `ensure_mine_enemies` | ✅ | Идемпотентно засевает врагов копи (Летучая мышь) из MINE_BAT_SEED. | :8561 |
| `ensure_mine_items` | ✅ | Идемпотентно создаёт предметы Железной копи (кирка, руда, самоцветы). | :8530 |
| `ensure_mollusk_items` | ✅ | Идемпотентно создаёт предметы моллюска (из его добычи и готового блюда). | :9137 |
| `ensure_player_housing` | — | Возвращает жильё игрока, создавая муниципальную квартиру для пилота при первом обращении. | :12043 |
| `ensure_rank_statuses_for_troops` | — | Выдать статус по текущему званию игрока (по войскам или админ-назначению). | :5815 |
| `ensure_recipe_shop_item` | — | Синхронизирует товар-рецепт «Рецепт: <name>» с рецептом (менеджер). | :12819 |
| `ensure_recipe_shop_items` | ✅ | Создаёт в магазине предметы-рецепты категории 'recipes'. | :13881 |
| `ensure_recipes` | ✅ | Идемпотентно засевает рецепты и синхронизирует уже существующие. | :12669 |
| `ensure_tourist_booklet` | ✅ | Создаёт предмет «Буклет туриста» и награду «Опытный турист», если их нет. | :10388 |
| `ensure_user_recipes_backfill` | ✅ | Разово открывает все рецепты существующим игрокам. | :14027 |
| `ensure_water_fish` | ✅ | Идемпотентно засевает water_fish из дефолтов. Правившие админом строки | :8043 |
| `migrate_legacy_junk` | ✅ | Переносит старые копии мусора (сапог, водоросли) из инвентаря в улов. | :7889 |
| `seed_default_items` | ✅ | Заполняет магазин базовым набором товаров, если он пуст и не было своих товаров. | :9789 |
| `seed_dungeon` | ✅ | — | :9944 |
| `seed_kvp` | ✅ | Создаёт тренировочный данж К.В.П. с врагами (Ефрейтор, Старший сержант), если его нет. | :10015 |
| `seed_locations` | — | Засеивает базовые локации города (Ратуша, Библиотека) как пример управляемого доступа. | :1738 |

## 3. Отдельные скрипты миграций

- `migrate_113.py` — Проверка миграций 0.19.0 на чистой БД: колонки polls, таблица rep_speeches.
- `migrate_113_old.py` — Миграция 0.19.0 поверх БД со старой схемой polls (без closes_at/is_archived).

