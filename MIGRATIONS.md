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
| `awards` | `achievement_key` | `TEXT DEFAULT NULL` | :1306 |
| `awards` | `achievement_level` | `INTEGER DEFAULT 0` | :1307 |
| `awards` | `bonus_attack` | `INTEGER DEFAULT 0` | :1285 |
| `awards` | `bonus_crit` | `INTEGER DEFAULT 0` | :1292 |
| `awards` | `bonus_defense` | `INTEGER DEFAULT 0` | :1286 |
| `awards` | `bonus_dodge` | `INTEGER DEFAULT 0` | :1287 |
| `awards` | `bonus_fishing` | `INTEGER DEFAULT 0` | :1288 |
| `awards` | `bonus_hp` | `INTEGER DEFAULT 0` | :1289 |
| `awards` | `bonus_json` | `TEXT DEFAULT '{}'` | :1308 |
| `awards` | `bonus_report_tax` | `INTEGER DEFAULT 0` | :1296 |
| `awards` | `bonus_shop_discount` | `INTEGER DEFAULT 0` | :1295 |
| `awards` | `image` | `TEXT` | :1284 |
| `awards` | `monthly_nm` | `INTEGER DEFAULT 0` | :1300 |
| `awards` | `reward_nm` | `INTEGER DEFAULT 0` | :1299 |
| `buildings` | `required_status` | `TEXT` | :1052 |
| `clan_buildings` | `building_photo_file_id` | `TEXT` | :1624 |
| `dungeon_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1220 |
| `dungeon_enemies` | `admin_tuned` | `INTEGER DEFAULT 0` | :1256 |
| `dungeon_enemies` | `armor` | `INTEGER DEFAULT 0` | :1216 |
| `dungeon_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1480 |
| `dungeon_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1481 |
| `dungeon_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1218 |
| `dungeon_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1219 |
| `dungeon_enemies` | `damage_max` | `INTEGER DEFAULT 0` | :1215 |
| `dungeon_enemies` | `damage_min` | `INTEGER DEFAULT 0` | :1214 |
| `dungeon_enemies` | `description` | `TEXT` | :1212 |
| `dungeon_enemies` | `dodge` | `INTEGER DEFAULT 0` | :1213 |
| `dungeon_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1217 |
| `dungeon_enemies` | `drops` | `TEXT DEFAULT '[]'` | :1208 |
| `dungeon_enemies` | `frostbite_chance` | `INTEGER DEFAULT 0` | :1482 |
| `dungeon_enemies` | `image` | `TEXT` | :1209 |
| `dungeon_enemies` | `poison_chance` | `INTEGER DEFAULT 0` | :1210 |
| `dungeon_enemies` | `poison_dmg` | `INTEGER DEFAULT 0` | :1211 |
| `dungeons` | `is_training` | `INTEGER DEFAULT 0` | :1471 |
| `dungeons` | `photo_dawn` | `TEXT` | :1269 |
| `dungeons` | `photo_day` | `TEXT` | :1270 |
| `dungeons` | `photo_night` | `TEXT` | :1272 |
| `dungeons` | `photo_rope` | `TEXT` | :1275 |
| `dungeons` | `photo_sunset` | `TEXT` | :1271 |
| `dungeons` | `photo_water` | `TEXT` | :1274 |
| `dungeons` | `rooms_map` | `TEXT` | :1487 |
| `fish_catches` | `expires_at` | `TIMESTAMP` | :1345 |
| `fish_catches` | `kind` | `TEXT DEFAULT 'fish'` | :1493 |
| `fishing_enemies` | `armor` | `INTEGER DEFAULT 0` | :1231 |
| `fishing_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1229 |
| `fishing_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1230 |
| `forest_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1225 |
| `forest_enemies` | `armor` | `INTEGER DEFAULT 0` | :1221 |
| `forest_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1227 |
| `forest_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1228 |
| `forest_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1223 |
| `forest_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1224 |
| `forest_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1222 |
| `forest_mushrooms` | `zone` | `TEXT DEFAULT 'clearing'` | :1390 |
| `housing_slots` | `embedded` | `INTEGER DEFAULT 0` | :1421 |
| `inventory` | `expires_at` | `TIMESTAMP` | :1340 |
| `inventory` | `plant_data` | `TEXT` | :1342 |
| `items` | `armor` | `INTEGER DEFAULT 0` | :1082 |
| `items` | `crit_chance` | `INTEGER DEFAULT 0` | :1085 |
| `items` | `crit_mult` | `REAL DEFAULT 0` | :1086 |
| `items` | `cure_frostbite` | `INTEGER DEFAULT 0` | :1484 |
| `items` | `cure_poison` | `INTEGER DEFAULT 0` | :1257 |
| `items` | `damage` | `INTEGER DEFAULT 0` | :1206 |
| `items` | `drink_effect` | `TEXT DEFAULT NULL` | :1328 |
| `items` | `equip_slot` | `TEXT` | :1088 |
| `items` | `heal` | `INTEGER DEFAULT 0` | :1207 |
| `items` | `housing_slots` | `INTEGER` | :1576 |
| `items` | `housing_type` | `TEXT` | :1575 |
| `items` | `loot_only` | `INTEGER DEFAULT 0` | :1581 |
| `items` | `market_ok` | `INTEGER DEFAULT 0` | :1490 |
| `items` | `plant_name` | `TEXT` | :1500 |
| `items` | `regen` | `INTEGER DEFAULT 0` | :1267 |
| `items` | `required_status` | `TEXT` | :1051 |
| `items` | `weapon_effect` | `TEXT` | :1511 |
| `items` | `weapon_effect_chance` | `INTEGER DEFAULT 0` | :1512 |
| `items` | `weapon_effect_dmg` | `INTEGER DEFAULT 0` | :1513 |
| `locations` | `clearing_photo` | `TEXT DEFAULT NULL` | :1376 |
| `locations` | `glade_photo` | `TEXT DEFAULT NULL` | :1375 |
| `locations` | `logging_photo` | `TEXT DEFAULT NULL` | :1385 |
| `locations` | `mine_level_photo` | `TEXT DEFAULT NULL` | :1379 |
| `locations` | `photo_dawn` | `TEXT` | :1259 |
| `locations` | `photo_day` | `TEXT` | :1260 |
| `locations` | `photo_night` | `TEXT` | :1262 |
| `locations` | `photo_sunset` | `TEXT` | :1261 |
| `locations` | `preview_photo` | `TEXT` | :1258 |
| `locations` | `season_photos` | `TEXT DEFAULT NULL` | :1372 |
| `locations` | `storage_photo` | `TEXT DEFAULT NULL` | :1381 |
| `locations` | `visits` | `INTEGER DEFAULT 0` | :1264 |
| `logging_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1246 |
| `logging_enemies` | `armor` | `INTEGER DEFAULT 0` | :1242 |
| `logging_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1244 |
| `logging_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1245 |
| `logging_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1243 |
| `market_fish` | `base_price` | `INTEGER DEFAULT 0` | :1474 |
| `mine_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1237 |
| `mine_enemies` | `armor` | `INTEGER DEFAULT 0` | :1233 |
| `mine_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1238 |
| `mine_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1239 |
| `mine_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1235 |
| `mine_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1236 |
| `mine_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1234 |
| `nii_reports` | `photo2_file_id` | `TEXT DEFAULT NULL` | :1310 |
| `player_dungeon_run` | `loot_nm` | `INTEGER DEFAULT 0` | :1193 |
| `player_dungeon_run` | `started_at` | `TIMESTAMP DEFAULT CURRENT_TIMESTAMP` | :1194 |
| `player_housing` | `expansions_installed` | `INTEGER DEFAULT 0` | :1423 |
| `player_housing` | `housing_label` | `TEXT` | :1577 |
| `player_housing` | `housing_slots` | `INTEGER` | :1578 |
| `player_housing` | `tax_last_check` | `TEXT DEFAULT NULL` | :1475 |
| `player_housing` | `tax_unpaid_months` | `INTEGER DEFAULT 0` | :1476 |
| `polls` | `archived_day` | `TEXT DEFAULT ''` | :1439 |
| `polls` | `closed_at` | `TIMESTAMP` | :1338 |
| `polls` | `closed_by` | `INTEGER` | :1337 |
| `polls` | `closes_at` | `TIMESTAMP` | :1428 |
| `polls` | `is_archived` | `INTEGER DEFAULT 0` | :1438 |
| `reports` | `credited_troops` | `INTEGER` | :1093 |
| `reports` | `paid` | `INTEGER DEFAULT 0` | :1100 |
| `reports` | `total_troops` | `INTEGER DEFAULT 0` | :1091 |
| `statuses` | `sort_order` | `INTEGER DEFAULT 0` | :1053 |
| `users` | `about` | `TEXT DEFAULT ''` | :1076 |
| `users` | `alcohol_strong_used_day` | `TEXT DEFAULT NULL` | :1332 |
| `users` | `alcohol_strong_used_today` | `INTEGER DEFAULT 0` | :1331 |
| `users` | `alcohol_weak_used_day` | `TEXT DEFAULT NULL` | :1330 |
| `users` | `alcohol_weak_used_today` | `INTEGER DEFAULT 0` | :1329 |
| `users` | `ap_recovery_day` | `TEXT DEFAULT NULL` | :1324 |
| `users` | `ap_restored_day` | `TEXT DEFAULT NULL` | :1197 |
| `users` | `ap_restored_today` | `INTEGER DEFAULT 0` | :1198 |
| `users` | `beer_used_day` | `TEXT DEFAULT NULL` | :1327 |
| `users` | `beer_used_today` | `INTEGER DEFAULT 0` | :1326 |
| `users` | `callsign` | `TEXT` | :1282 |
| `users` | `callsign_free_used` | `INTEGER DEFAULT 0` | :1473 |
| `users` | `duel_losses` | `INTEGER DEFAULT 0` | :1202 |
| `users` | `duel_rating` | `INTEGER DEFAULT 0` | :1200 |
| `users` | `duel_wins` | `INTEGER DEFAULT 0` | :1201 |
| `users` | `equipment` | `TEXT DEFAULT '{}'` | :1077 |
| `users` | `fish_sold_day` | `TEXT DEFAULT NULL` | :1353 |
| `users` | `fish_sold_today` | `INTEGER DEFAULT 0` | :1354 |
| `users` | `fishing_bait` | `TEXT DEFAULT ''` | :1280 |
| `users` | `forest_attempts_since_boar` | `INTEGER DEFAULT 0` | :1356 |
| `users` | `forest_attempts_since_wolf` | `INTEGER DEFAULT 0` | :1358 |
| `users` | `forest_sold_day` | `TEXT DEFAULT NULL` | :1368 |
| `users` | `forest_sold_today` | `INTEGER DEFAULT 0` | :1369 |
| `users` | `fountain_used_day` | `TEXT DEFAULT NULL` | :1347 |
| `users` | `fountain_used_today` | `INTEGER DEFAULT 0` | :1348 |
| `users` | `last_active` | `REAL DEFAULT 0` | :1205 |
| `users` | `last_salary_date` | `TIMESTAMP` | :1080 |
| `users` | `legioner` | `INTEGER DEFAULT 0` | :1518 |
| `users` | `logging_attempts_since_owl` | `INTEGER DEFAULT 0` | :1365 |
| `users` | `logging_attempts_since_snake` | `INTEGER DEFAULT 0` | :1364 |
| `users` | `market_license_expires` | `TEXT DEFAULT NULL` | :1472 |
| `users` | `mine_attempts_since_bat` | `INTEGER DEFAULT 0` | :1361 |
| `users` | `notify_enabled` | `INTEGER DEFAULT 1` | :1074 |
| `users` | `profile_public` | `INTEGER DEFAULT 1` | :1075 |
| `users` | `promoted_rank` | `TEXT` | :1054 |
| `users` | `salary` | `INTEGER DEFAULT 0` | :1078 |
| `users` | `salary_debt` | `INTEGER DEFAULT 0` | :1081 |
| `users` | `salary_period_days` | `INTEGER DEFAULT 7` | :1079 |
| `users` | `seaweed_used_day` | `TEXT DEFAULT NULL` | :1321 |
| `users` | `seaweed_used_today` | `INTEGER DEFAULT 0` | :1320 |
| `users` | `shower_used_day` | `TEXT DEFAULT NULL` | :1350 |
| `users` | `shower_used_today` | `INTEGER DEFAULT 0` | :1351 |
| `users` | `special_blocked_until` | `TEXT DEFAULT NULL` | :1335 |
| `users` | `special_fails_today` | `INTEGER DEFAULT 0` | :1334 |
| `users` | `wing` | `TEXT` | :1515 |
| `users` | `xp_balance` | `INTEGER DEFAULT 0` | :1058 |
| `water_fish` | `excluded` | `INTEGER DEFAULT 0` | :1278 |
| `water_fish` | `kind` | `TEXT DEFAULT 'fish'` | :1494 |
| `water_fish` | `super_rare` | `INTEGER DEFAULT 0` | :1497 |
| `wings` | `abbr` | `TEXT DEFAULT ''` | :1314 |
| `wings` | `callsign` | `TEXT DEFAULT ''` | :1316 |
| `wings` | `emoji` | `TEXT DEFAULT ''` | :1317 |
| `wings` | `name` | `TEXT DEFAULT ''` | :1315 |
| `wings` | `num` | `TEXT DEFAULT ''` | :1313 |
| `wings` | `sort_order` | `INTEGER DEFAULT 0` | :1318 |

## 2. Идемпотентные засевы и миграции данных

| Функция | Вызывается из main.py | Назначение (первая строка docstring) | db.py |
|---|---|---|---|
| `backfill_rank_statuses` | — | Разово выдать статусы по текущим званиям всех пилотов (войска и админ-звания). | :5783 |
| `ensure_achievements` | ✅ | Идемпотентно засевает награды-уровни достижений и синхронизирует их. | :12326 |
| `ensure_base_status` | — | Базовый статус «Турист» для каждого нового игрока. | :6020 |
| `ensure_base_statuses` | — | Создаёт базовые статусы иерархии, если их нет. | :5975 |
| `ensure_clan_building` | — | — | :14023 |
| `ensure_duel_items` | ✅ | Товары Дома Дуэлей: дуэльные перчатки (отдельный слот) и клубная карта. | :10032 |
| `ensure_dungeon_enemy_drops` | ✅ | Синхронизирует врагов существующего данжа с DEFAULT_DUNGEON (дропы, HP, награды, | :11851 |
| `ensure_dungeon_reservoir_items` | ✅ | Идемпотентно добавляет предметы водохранилища подземелья (v0.12.0). | :11755 |
| `ensure_dungeon_shop_items` | ✅ | Идемпотентно добавляет предметы данжа (зелье в магазин, трофеи) — для существующих БД. | :11370 |
| `ensure_fishing_enemies` | ✅ | Идемпотентно засевает врагов рыбалки (мутировавший моллюск) из MOLLUSK_SEED. | :9070 |
| `ensure_forest_enemies` | ✅ | Идемпотентно засевает врагов леса (кабан и Белый Волк Севера). | :9045 |
| `ensure_forest_items` | ✅ | Идемпотентно создаёт предметы леса (грибы, добыча кабана, жареные блюда, яд). | :8399 |
| `ensure_forest_mushrooms` | ✅ | Идемпотентно засевает пул грибов леса из FOREST_DEFAULTS. | :8563 |
| `ensure_forest_zones` | ✅ | Разовый перенос старого пула леса в зону поляны и засев пула опушки. | :8806 |
| `ensure_kvp_award` | ✅ | — | :10291 |
| `ensure_kvp_items` | ✅ | Обеспечивает эксклюзивный предмет К.В.П. — «Сержантскую трость». | :10005 |
| `ensure_kvp_user` | — | Гарантирует наличие строки прогресса К.В.П. для игрока. | :10478 |
| `ensure_life_items` | ✅ | Идемпотентно добавляет предметы жилья, мебели, семян, ресурсов и продовольствия. | :11576 |
| `ensure_logging_enemies` | ✅ | Идемпотентно засевает врагов Лесозаготовки (Змея и Неясыть). | :8552 |
| `ensure_logging_items` | ✅ | Идемпотентно создаёт предметы Лесозаготовки (топор, бревна, дропы). | :8509 |
| `ensure_market_license_item` | ✅ | Идемпотентно добавляет «Торговую лицензию» в магазин. | :9554 |
| `ensure_mine_enemies` | ✅ | Идемпотентно засевает врагов копи (Летучая мышь) из MINE_BAT_SEED. | :8500 |
| `ensure_mine_items` | ✅ | Идемпотентно создаёт предметы Железной копи (кирка, руда, самоцветы). | :8469 |
| `ensure_mollusk_items` | ✅ | Идемпотентно создаёт предметы моллюска (из его добычи и готового блюда). | :9076 |
| `ensure_player_housing` | — | Возвращает жильё игрока, создавая муниципальную квартиру для пилота при первом обращении. | :11982 |
| `ensure_rank_statuses_for_troops` | — | Выдать статус по текущему званию игрока (по войскам или админ-назначению). | :5771 |
| `ensure_recipe_shop_item` | — | Синхронизирует товар-рецепт «Рецепт: <name>» с рецептом (менеджер). | :12739 |
| `ensure_recipe_shop_items` | ✅ | Создаёт в магазине предметы-рецепты категории 'recipes'. | :13794 |
| `ensure_recipes` | ✅ | Идемпотентно засевает рецепты и синхронизирует уже существующие. | :12589 |
| `ensure_tourist_booklet` | ✅ | Создаёт предмет «Буклет туриста» и награду «Опытный турист», если их нет. | :10327 |
| `ensure_user_recipes_backfill` | ✅ | Разово открывает все рецепты существующим игрокам. | :13940 |
| `ensure_water_fish` | ✅ | Идемпотентно засевает water_fish из дефолтов. Правившие админом строки | :7999 |
| `migrate_legacy_junk` | ✅ | Переносит старые копии мусора (сапог, водоросли) из инвентаря в улов. | :7845 |
| `seed_default_items` | ✅ | Заполняет магазин базовым набором товаров, если он пуст и не было своих товаров. | :9728 |
| `seed_dungeon` | ✅ | — | :9883 |
| `seed_kvp` | ✅ | Создаёт тренировочный данж К.В.П. с врагами (Ефрейтор, Старший сержант), если его нет. | :9954 |
| `seed_locations` | — | Засеивает базовые локации города (Ратуша, Библиотека) как пример управляемого доступа. | :1705 |

## 3. Отдельные скрипты миграций

- `migrate_113.py` — Проверка миграций 0.19.0 на чистой БД: колонки polls, таблица rep_speeches.
- `migrate_113_old.py` — Миграция 0.19.0 поверх БД со старой схемой polls (без closes_at/is_archived).

