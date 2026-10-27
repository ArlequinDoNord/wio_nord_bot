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
| `awards` | `achievement_key` | `TEXT DEFAULT NULL` | :1316 |
| `awards` | `achievement_level` | `INTEGER DEFAULT 0` | :1317 |
| `awards` | `bonus_attack` | `INTEGER DEFAULT 0` | :1295 |
| `awards` | `bonus_crit` | `INTEGER DEFAULT 0` | :1302 |
| `awards` | `bonus_defense` | `INTEGER DEFAULT 0` | :1296 |
| `awards` | `bonus_dodge` | `INTEGER DEFAULT 0` | :1297 |
| `awards` | `bonus_fishing` | `INTEGER DEFAULT 0` | :1298 |
| `awards` | `bonus_hp` | `INTEGER DEFAULT 0` | :1299 |
| `awards` | `bonus_json` | `TEXT DEFAULT '{}'` | :1318 |
| `awards` | `bonus_report_tax` | `INTEGER DEFAULT 0` | :1306 |
| `awards` | `bonus_shop_discount` | `INTEGER DEFAULT 0` | :1305 |
| `awards` | `image` | `TEXT` | :1294 |
| `awards` | `monthly_nm` | `INTEGER DEFAULT 0` | :1310 |
| `awards` | `reward_nm` | `INTEGER DEFAULT 0` | :1309 |
| `buildings` | `required_status` | `TEXT` | :1062 |
| `clan_buildings` | `building_photo_file_id` | `TEXT` | :1634 |
| `dungeon_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1230 |
| `dungeon_enemies` | `admin_tuned` | `INTEGER DEFAULT 0` | :1266 |
| `dungeon_enemies` | `armor` | `INTEGER DEFAULT 0` | :1226 |
| `dungeon_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1490 |
| `dungeon_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1491 |
| `dungeon_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1228 |
| `dungeon_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1229 |
| `dungeon_enemies` | `damage_max` | `INTEGER DEFAULT 0` | :1225 |
| `dungeon_enemies` | `damage_min` | `INTEGER DEFAULT 0` | :1224 |
| `dungeon_enemies` | `description` | `TEXT` | :1222 |
| `dungeon_enemies` | `dodge` | `INTEGER DEFAULT 0` | :1223 |
| `dungeon_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1227 |
| `dungeon_enemies` | `drops` | `TEXT DEFAULT '[]'` | :1218 |
| `dungeon_enemies` | `frostbite_chance` | `INTEGER DEFAULT 0` | :1492 |
| `dungeon_enemies` | `image` | `TEXT` | :1219 |
| `dungeon_enemies` | `poison_chance` | `INTEGER DEFAULT 0` | :1220 |
| `dungeon_enemies` | `poison_dmg` | `INTEGER DEFAULT 0` | :1221 |
| `dungeons` | `is_training` | `INTEGER DEFAULT 0` | :1481 |
| `dungeons` | `photo_dawn` | `TEXT` | :1279 |
| `dungeons` | `photo_day` | `TEXT` | :1280 |
| `dungeons` | `photo_night` | `TEXT` | :1282 |
| `dungeons` | `photo_rope` | `TEXT` | :1285 |
| `dungeons` | `photo_sunset` | `TEXT` | :1281 |
| `dungeons` | `photo_water` | `TEXT` | :1284 |
| `dungeons` | `rooms_map` | `TEXT` | :1497 |
| `fish_catches` | `expires_at` | `TIMESTAMP` | :1355 |
| `fish_catches` | `kind` | `TEXT DEFAULT 'fish'` | :1503 |
| `fishing_enemies` | `armor` | `INTEGER DEFAULT 0` | :1241 |
| `fishing_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1239 |
| `fishing_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1240 |
| `forest_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1235 |
| `forest_enemies` | `armor` | `INTEGER DEFAULT 0` | :1231 |
| `forest_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1237 |
| `forest_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1238 |
| `forest_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1233 |
| `forest_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1234 |
| `forest_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1232 |
| `forest_mushrooms` | `zone` | `TEXT DEFAULT 'clearing'` | :1400 |
| `housing_slots` | `embedded` | `INTEGER DEFAULT 0` | :1431 |
| `inventory` | `expires_at` | `TIMESTAMP` | :1350 |
| `inventory` | `plant_data` | `TEXT` | :1352 |
| `items` | `armor` | `INTEGER DEFAULT 0` | :1092 |
| `items` | `crit_chance` | `INTEGER DEFAULT 0` | :1095 |
| `items` | `crit_mult` | `REAL DEFAULT 0` | :1096 |
| `items` | `cure_frostbite` | `INTEGER DEFAULT 0` | :1494 |
| `items` | `cure_poison` | `INTEGER DEFAULT 0` | :1267 |
| `items` | `damage` | `INTEGER DEFAULT 0` | :1216 |
| `items` | `drink_effect` | `TEXT DEFAULT NULL` | :1338 |
| `items` | `equip_slot` | `TEXT` | :1098 |
| `items` | `heal` | `INTEGER DEFAULT 0` | :1217 |
| `items` | `housing_slots` | `INTEGER` | :1586 |
| `items` | `housing_type` | `TEXT` | :1585 |
| `items` | `loot_only` | `INTEGER DEFAULT 0` | :1591 |
| `items` | `market_ok` | `INTEGER DEFAULT 0` | :1500 |
| `items` | `plant_name` | `TEXT` | :1510 |
| `items` | `regen` | `INTEGER DEFAULT 0` | :1277 |
| `items` | `required_status` | `TEXT` | :1061 |
| `items` | `weapon_effect` | `TEXT` | :1521 |
| `items` | `weapon_effect_chance` | `INTEGER DEFAULT 0` | :1522 |
| `items` | `weapon_effect_dmg` | `INTEGER DEFAULT 0` | :1523 |
| `locations` | `clearing_photo` | `TEXT DEFAULT NULL` | :1386 |
| `locations` | `glade_photo` | `TEXT DEFAULT NULL` | :1385 |
| `locations` | `logging_photo` | `TEXT DEFAULT NULL` | :1395 |
| `locations` | `mine_level_photo` | `TEXT DEFAULT NULL` | :1389 |
| `locations` | `photo_dawn` | `TEXT` | :1269 |
| `locations` | `photo_day` | `TEXT` | :1270 |
| `locations` | `photo_night` | `TEXT` | :1272 |
| `locations` | `photo_sunset` | `TEXT` | :1271 |
| `locations` | `preview_photo` | `TEXT` | :1268 |
| `locations` | `season_photos` | `TEXT DEFAULT NULL` | :1382 |
| `locations` | `storage_photo` | `TEXT DEFAULT NULL` | :1391 |
| `locations` | `visits` | `INTEGER DEFAULT 0` | :1274 |
| `logging_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1256 |
| `logging_enemies` | `armor` | `INTEGER DEFAULT 0` | :1252 |
| `logging_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1254 |
| `logging_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1255 |
| `logging_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1253 |
| `market_fish` | `base_price` | `INTEGER DEFAULT 0` | :1484 |
| `mine_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1247 |
| `mine_enemies` | `armor` | `INTEGER DEFAULT 0` | :1243 |
| `mine_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1248 |
| `mine_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1249 |
| `mine_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1245 |
| `mine_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1246 |
| `mine_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1244 |
| `nii_reports` | `photo2_file_id` | `TEXT DEFAULT NULL` | :1320 |
| `player_dungeon_run` | `loot_nm` | `INTEGER DEFAULT 0` | :1203 |
| `player_dungeon_run` | `started_at` | `TIMESTAMP DEFAULT CURRENT_TIMESTAMP` | :1204 |
| `player_housing` | `expansions_installed` | `INTEGER DEFAULT 0` | :1433 |
| `player_housing` | `housing_label` | `TEXT` | :1587 |
| `player_housing` | `housing_slots` | `INTEGER` | :1588 |
| `player_housing` | `tax_last_check` | `TEXT DEFAULT NULL` | :1485 |
| `player_housing` | `tax_unpaid_months` | `INTEGER DEFAULT 0` | :1486 |
| `polls` | `archived_day` | `TEXT DEFAULT ''` | :1449 |
| `polls` | `closed_at` | `TIMESTAMP` | :1348 |
| `polls` | `closed_by` | `INTEGER` | :1347 |
| `polls` | `closes_at` | `TIMESTAMP` | :1438 |
| `polls` | `is_archived` | `INTEGER DEFAULT 0` | :1448 |
| `reports` | `credited_troops` | `INTEGER` | :1103 |
| `reports` | `paid` | `INTEGER DEFAULT 0` | :1110 |
| `reports` | `total_troops` | `INTEGER DEFAULT 0` | :1101 |
| `statuses` | `sort_order` | `INTEGER DEFAULT 0` | :1063 |
| `users` | `about` | `TEXT DEFAULT ''` | :1086 |
| `users` | `alcohol_strong_used_day` | `TEXT DEFAULT NULL` | :1342 |
| `users` | `alcohol_strong_used_today` | `INTEGER DEFAULT 0` | :1341 |
| `users` | `alcohol_weak_used_day` | `TEXT DEFAULT NULL` | :1340 |
| `users` | `alcohol_weak_used_today` | `INTEGER DEFAULT 0` | :1339 |
| `users` | `ap_recovery_day` | `TEXT DEFAULT NULL` | :1334 |
| `users` | `ap_restored_day` | `TEXT DEFAULT NULL` | :1207 |
| `users` | `ap_restored_today` | `INTEGER DEFAULT 0` | :1208 |
| `users` | `beer_used_day` | `TEXT DEFAULT NULL` | :1337 |
| `users` | `beer_used_today` | `INTEGER DEFAULT 0` | :1336 |
| `users` | `callsign` | `TEXT` | :1292 |
| `users` | `callsign_free_used` | `INTEGER DEFAULT 0` | :1483 |
| `users` | `duel_losses` | `INTEGER DEFAULT 0` | :1212 |
| `users` | `duel_rating` | `INTEGER DEFAULT 0` | :1210 |
| `users` | `duel_wins` | `INTEGER DEFAULT 0` | :1211 |
| `users` | `equipment` | `TEXT DEFAULT '{}'` | :1087 |
| `users` | `fish_sold_day` | `TEXT DEFAULT NULL` | :1363 |
| `users` | `fish_sold_today` | `INTEGER DEFAULT 0` | :1364 |
| `users` | `fishing_bait` | `TEXT DEFAULT ''` | :1290 |
| `users` | `forest_attempts_since_boar` | `INTEGER DEFAULT 0` | :1366 |
| `users` | `forest_attempts_since_wolf` | `INTEGER DEFAULT 0` | :1368 |
| `users` | `forest_sold_day` | `TEXT DEFAULT NULL` | :1378 |
| `users` | `forest_sold_today` | `INTEGER DEFAULT 0` | :1379 |
| `users` | `fountain_used_day` | `TEXT DEFAULT NULL` | :1357 |
| `users` | `fountain_used_today` | `INTEGER DEFAULT 0` | :1358 |
| `users` | `last_active` | `REAL DEFAULT 0` | :1215 |
| `users` | `last_salary_date` | `TIMESTAMP` | :1090 |
| `users` | `legioner` | `INTEGER DEFAULT 0` | :1528 |
| `users` | `logging_attempts_since_owl` | `INTEGER DEFAULT 0` | :1375 |
| `users` | `logging_attempts_since_snake` | `INTEGER DEFAULT 0` | :1374 |
| `users` | `market_license_expires` | `TEXT DEFAULT NULL` | :1482 |
| `users` | `mine_attempts_since_bat` | `INTEGER DEFAULT 0` | :1371 |
| `users` | `notify_enabled` | `INTEGER DEFAULT 1` | :1084 |
| `users` | `profile_public` | `INTEGER DEFAULT 1` | :1085 |
| `users` | `promoted_rank` | `TEXT` | :1064 |
| `users` | `salary` | `INTEGER DEFAULT 0` | :1088 |
| `users` | `salary_debt` | `INTEGER DEFAULT 0` | :1091 |
| `users` | `salary_period_days` | `INTEGER DEFAULT 7` | :1089 |
| `users` | `seaweed_used_day` | `TEXT DEFAULT NULL` | :1331 |
| `users` | `seaweed_used_today` | `INTEGER DEFAULT 0` | :1330 |
| `users` | `shower_used_day` | `TEXT DEFAULT NULL` | :1360 |
| `users` | `shower_used_today` | `INTEGER DEFAULT 0` | :1361 |
| `users` | `special_blocked_until` | `TEXT DEFAULT NULL` | :1345 |
| `users` | `special_fails_today` | `INTEGER DEFAULT 0` | :1344 |
| `users` | `wing` | `TEXT` | :1525 |
| `users` | `xp_balance` | `INTEGER DEFAULT 0` | :1068 |
| `water_fish` | `excluded` | `INTEGER DEFAULT 0` | :1288 |
| `water_fish` | `kind` | `TEXT DEFAULT 'fish'` | :1504 |
| `water_fish` | `super_rare` | `INTEGER DEFAULT 0` | :1507 |
| `wings` | `abbr` | `TEXT DEFAULT ''` | :1324 |
| `wings` | `callsign` | `TEXT DEFAULT ''` | :1326 |
| `wings` | `emoji` | `TEXT DEFAULT ''` | :1327 |
| `wings` | `name` | `TEXT DEFAULT ''` | :1325 |
| `wings` | `num` | `TEXT DEFAULT ''` | :1323 |
| `wings` | `sort_order` | `INTEGER DEFAULT 0` | :1328 |

## 2. Идемпотентные засевы и миграции данных

| Функция | Вызывается из main.py | Назначение (первая строка docstring) | db.py |
|---|---|---|---|
| `backfill_rank_statuses` | — | Разово выдать статусы по текущим званиям всех пилотов (войска и админ-звания). | :5793 |
| `ensure_achievements` | ✅ | Идемпотентно засевает награды-уровни достижений и синхронизирует их. | :12372 |
| `ensure_base_status` | — | Базовый статус «Турист» для каждого нового игрока. | :6030 |
| `ensure_base_statuses` | — | Создаёт базовые статусы иерархии, если их нет. | :5985 |
| `ensure_clan_building` | — | — | :14070 |
| `ensure_duel_items` | ✅ | Товары Дома Дуэлей: дуэльные перчатки (отдельный слот) и клубная карта. | :10059 |
| `ensure_dungeon_enemy_drops` | ✅ | Синхронизирует врагов существующего данжа с DEFAULT_DUNGEON (дропы, HP, награды, | :11878 |
| `ensure_dungeon_reservoir_items` | ✅ | Идемпотентно добавляет предметы водохранилища подземелья (v0.12.0). | :11782 |
| `ensure_dungeon_shop_items` | ✅ | Идемпотентно добавляет предметы данжа (зелье в магазин, трофеи) — для существующих БД. | :11397 |
| `ensure_fishing_enemies` | ✅ | Идемпотентно засевает врагов рыбалки (мутировавший моллюск) из MOLLUSK_SEED. | :9097 |
| `ensure_forest_enemies` | ✅ | Идемпотентно засевает врагов леса (кабан и Белый Волк Севера). | :9072 |
| `ensure_forest_items` | ✅ | Идемпотентно создаёт предметы леса (грибы, добыча кабана, жареные блюда, яд). | :8418 |
| `ensure_forest_mushrooms` | ✅ | Идемпотентно засевает пул грибов леса из FOREST_DEFAULTS. | :8590 |
| `ensure_forest_zones` | ✅ | Разовый перенос старого пула леса в зону поляны и засев пула опушки. | :8833 |
| `ensure_kvp_award` | ✅ | — | :10318 |
| `ensure_kvp_items` | ✅ | Обеспечивает эксклюзивный предмет К.В.П. — «Сержантскую трость». | :10032 |
| `ensure_kvp_user` | — | Гарантирует наличие строки прогресса К.В.П. для игрока. | :10505 |
| `ensure_life_items` | ✅ | Идемпотентно добавляет предметы жилья, мебели, семян, ресурсов и продовольствия. | :11603 |
| `ensure_logging_enemies` | ✅ | Идемпотентно засевает врагов Лесозаготовки (Змея и Неясыть). | :8579 |
| `ensure_logging_items` | ✅ | Идемпотентно создаёт предметы Лесозаготовки (топор, бревна, дропы). | :8536 |
| `ensure_market_license_item` | ✅ | Идемпотентно добавляет «Торговую лицензию» в магазин. | :9581 |
| `ensure_mine_enemies` | ✅ | Идемпотентно засевает врагов копи (Летучая мышь) из MINE_BAT_SEED. | :8527 |
| `ensure_mine_items` | ✅ | Идемпотентно создаёт предметы Железной копи (кирка, руда, самоцветы). | :8496 |
| `ensure_mollusk_items` | ✅ | Идемпотентно создаёт предметы моллюска (из его добычи и готового блюда). | :9103 |
| `ensure_player_housing` | — | Возвращает жильё игрока, создавая муниципальную квартиру для пилота при первом обращении. | :12009 |
| `ensure_rank_statuses_for_troops` | — | Выдать статус по текущему званию игрока (по войскам или админ-назначению). | :5781 |
| `ensure_recipe_shop_item` | — | Синхронизирует товар-рецепт «Рецепт: <name>» с рецептом (менеджер). | :12785 |
| `ensure_recipe_shop_items` | ✅ | Создаёт в магазине предметы-рецепты категории 'recipes'. | :13841 |
| `ensure_recipes` | ✅ | Идемпотентно засевает рецепты и синхронизирует уже существующие. | :12635 |
| `ensure_tourist_booklet` | ✅ | Создаёт предмет «Буклет туриста» и награду «Опытный турист», если их нет. | :10354 |
| `ensure_user_recipes_backfill` | ✅ | Разово открывает все рецепты существующим игрокам. | :13987 |
| `ensure_water_fish` | ✅ | Идемпотентно засевает water_fish из дефолтов. Правившие админом строки | :8009 |
| `migrate_legacy_junk` | ✅ | Переносит старые копии мусора (сапог, водоросли) из инвентаря в улов. | :7855 |
| `seed_default_items` | ✅ | Заполняет магазин базовым набором товаров, если он пуст и не было своих товаров. | :9755 |
| `seed_dungeon` | ✅ | — | :9910 |
| `seed_kvp` | ✅ | Создаёт тренировочный данж К.В.П. с врагами (Ефрейтор, Старший сержант), если его нет. | :9981 |
| `seed_locations` | — | Засеивает базовые локации города (Ратуша, Библиотека) как пример управляемого доступа. | :1715 |

## 3. Отдельные скрипты миграций

- `migrate_113.py` — Проверка миграций 0.19.0 на чистой БД: колонки polls, таблица rep_speeches.
- `migrate_113_old.py` — Миграция 0.19.0 поверх БД со старой схемой polls (без closes_at/is_archived).

