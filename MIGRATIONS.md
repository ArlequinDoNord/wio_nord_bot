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
| `awards` | `achievement_key` | `TEXT DEFAULT NULL` | :1274 |
| `awards` | `achievement_level` | `INTEGER DEFAULT 0` | :1275 |
| `awards` | `bonus_attack` | `INTEGER DEFAULT 0` | :1253 |
| `awards` | `bonus_crit` | `INTEGER DEFAULT 0` | :1260 |
| `awards` | `bonus_defense` | `INTEGER DEFAULT 0` | :1254 |
| `awards` | `bonus_dodge` | `INTEGER DEFAULT 0` | :1255 |
| `awards` | `bonus_fishing` | `INTEGER DEFAULT 0` | :1256 |
| `awards` | `bonus_hp` | `INTEGER DEFAULT 0` | :1257 |
| `awards` | `bonus_json` | `TEXT DEFAULT '{}'` | :1276 |
| `awards` | `bonus_report_tax` | `INTEGER DEFAULT 0` | :1264 |
| `awards` | `bonus_shop_discount` | `INTEGER DEFAULT 0` | :1263 |
| `awards` | `image` | `TEXT` | :1252 |
| `awards` | `monthly_nm` | `INTEGER DEFAULT 0` | :1268 |
| `awards` | `reward_nm` | `INTEGER DEFAULT 0` | :1267 |
| `buildings` | `required_status` | `TEXT` | :1020 |
| `clan_buildings` | `building_photo_file_id` | `TEXT` | :1592 |
| `dungeon_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1188 |
| `dungeon_enemies` | `admin_tuned` | `INTEGER DEFAULT 0` | :1224 |
| `dungeon_enemies` | `armor` | `INTEGER DEFAULT 0` | :1184 |
| `dungeon_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1448 |
| `dungeon_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1449 |
| `dungeon_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1186 |
| `dungeon_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1187 |
| `dungeon_enemies` | `damage_max` | `INTEGER DEFAULT 0` | :1183 |
| `dungeon_enemies` | `damage_min` | `INTEGER DEFAULT 0` | :1182 |
| `dungeon_enemies` | `description` | `TEXT` | :1180 |
| `dungeon_enemies` | `dodge` | `INTEGER DEFAULT 0` | :1181 |
| `dungeon_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1185 |
| `dungeon_enemies` | `drops` | `TEXT DEFAULT '[]'` | :1176 |
| `dungeon_enemies` | `frostbite_chance` | `INTEGER DEFAULT 0` | :1450 |
| `dungeon_enemies` | `image` | `TEXT` | :1177 |
| `dungeon_enemies` | `poison_chance` | `INTEGER DEFAULT 0` | :1178 |
| `dungeon_enemies` | `poison_dmg` | `INTEGER DEFAULT 0` | :1179 |
| `dungeons` | `is_training` | `INTEGER DEFAULT 0` | :1439 |
| `dungeons` | `photo_dawn` | `TEXT` | :1237 |
| `dungeons` | `photo_day` | `TEXT` | :1238 |
| `dungeons` | `photo_night` | `TEXT` | :1240 |
| `dungeons` | `photo_rope` | `TEXT` | :1243 |
| `dungeons` | `photo_sunset` | `TEXT` | :1239 |
| `dungeons` | `photo_water` | `TEXT` | :1242 |
| `dungeons` | `rooms_map` | `TEXT` | :1455 |
| `fish_catches` | `expires_at` | `TIMESTAMP` | :1313 |
| `fish_catches` | `kind` | `TEXT DEFAULT 'fish'` | :1461 |
| `fishing_enemies` | `armor` | `INTEGER DEFAULT 0` | :1199 |
| `fishing_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1197 |
| `fishing_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1198 |
| `forest_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1193 |
| `forest_enemies` | `armor` | `INTEGER DEFAULT 0` | :1189 |
| `forest_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1195 |
| `forest_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1196 |
| `forest_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1191 |
| `forest_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1192 |
| `forest_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1190 |
| `forest_mushrooms` | `zone` | `TEXT DEFAULT 'clearing'` | :1358 |
| `housing_slots` | `embedded` | `INTEGER DEFAULT 0` | :1389 |
| `inventory` | `expires_at` | `TIMESTAMP` | :1308 |
| `inventory` | `plant_data` | `TEXT` | :1310 |
| `items` | `armor` | `INTEGER DEFAULT 0` | :1050 |
| `items` | `crit_chance` | `INTEGER DEFAULT 0` | :1053 |
| `items` | `crit_mult` | `REAL DEFAULT 0` | :1054 |
| `items` | `cure_frostbite` | `INTEGER DEFAULT 0` | :1452 |
| `items` | `cure_poison` | `INTEGER DEFAULT 0` | :1225 |
| `items` | `damage` | `INTEGER DEFAULT 0` | :1174 |
| `items` | `drink_effect` | `TEXT DEFAULT NULL` | :1296 |
| `items` | `equip_slot` | `TEXT` | :1056 |
| `items` | `heal` | `INTEGER DEFAULT 0` | :1175 |
| `items` | `housing_slots` | `INTEGER` | :1544 |
| `items` | `housing_type` | `TEXT` | :1543 |
| `items` | `loot_only` | `INTEGER DEFAULT 0` | :1549 |
| `items` | `market_ok` | `INTEGER DEFAULT 0` | :1458 |
| `items` | `plant_name` | `TEXT` | :1468 |
| `items` | `regen` | `INTEGER DEFAULT 0` | :1235 |
| `items` | `required_status` | `TEXT` | :1019 |
| `items` | `weapon_effect` | `TEXT` | :1479 |
| `items` | `weapon_effect_chance` | `INTEGER DEFAULT 0` | :1480 |
| `items` | `weapon_effect_dmg` | `INTEGER DEFAULT 0` | :1481 |
| `locations` | `clearing_photo` | `TEXT DEFAULT NULL` | :1344 |
| `locations` | `glade_photo` | `TEXT DEFAULT NULL` | :1343 |
| `locations` | `logging_photo` | `TEXT DEFAULT NULL` | :1353 |
| `locations` | `mine_level_photo` | `TEXT DEFAULT NULL` | :1347 |
| `locations` | `photo_dawn` | `TEXT` | :1227 |
| `locations` | `photo_day` | `TEXT` | :1228 |
| `locations` | `photo_night` | `TEXT` | :1230 |
| `locations` | `photo_sunset` | `TEXT` | :1229 |
| `locations` | `preview_photo` | `TEXT` | :1226 |
| `locations` | `season_photos` | `TEXT DEFAULT NULL` | :1340 |
| `locations` | `storage_photo` | `TEXT DEFAULT NULL` | :1349 |
| `locations` | `visits` | `INTEGER DEFAULT 0` | :1232 |
| `logging_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1214 |
| `logging_enemies` | `armor` | `INTEGER DEFAULT 0` | :1210 |
| `logging_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1212 |
| `logging_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1213 |
| `logging_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1211 |
| `market_fish` | `base_price` | `INTEGER DEFAULT 0` | :1442 |
| `mine_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1205 |
| `mine_enemies` | `armor` | `INTEGER DEFAULT 0` | :1201 |
| `mine_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1206 |
| `mine_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1207 |
| `mine_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1203 |
| `mine_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1204 |
| `mine_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1202 |
| `nii_reports` | `photo2_file_id` | `TEXT DEFAULT NULL` | :1278 |
| `player_dungeon_run` | `loot_nm` | `INTEGER DEFAULT 0` | :1161 |
| `player_dungeon_run` | `started_at` | `TIMESTAMP DEFAULT CURRENT_TIMESTAMP` | :1162 |
| `player_housing` | `expansions_installed` | `INTEGER DEFAULT 0` | :1391 |
| `player_housing` | `housing_label` | `TEXT` | :1545 |
| `player_housing` | `housing_slots` | `INTEGER` | :1546 |
| `player_housing` | `tax_last_check` | `TEXT DEFAULT NULL` | :1443 |
| `player_housing` | `tax_unpaid_months` | `INTEGER DEFAULT 0` | :1444 |
| `polls` | `archived_day` | `TEXT DEFAULT ''` | :1407 |
| `polls` | `closed_at` | `TIMESTAMP` | :1306 |
| `polls` | `closed_by` | `INTEGER` | :1305 |
| `polls` | `closes_at` | `TIMESTAMP` | :1396 |
| `polls` | `is_archived` | `INTEGER DEFAULT 0` | :1406 |
| `reports` | `credited_troops` | `INTEGER` | :1061 |
| `reports` | `paid` | `INTEGER DEFAULT 0` | :1068 |
| `reports` | `total_troops` | `INTEGER DEFAULT 0` | :1059 |
| `statuses` | `sort_order` | `INTEGER DEFAULT 0` | :1021 |
| `users` | `about` | `TEXT DEFAULT ''` | :1044 |
| `users` | `alcohol_strong_used_day` | `TEXT DEFAULT NULL` | :1300 |
| `users` | `alcohol_strong_used_today` | `INTEGER DEFAULT 0` | :1299 |
| `users` | `alcohol_weak_used_day` | `TEXT DEFAULT NULL` | :1298 |
| `users` | `alcohol_weak_used_today` | `INTEGER DEFAULT 0` | :1297 |
| `users` | `ap_recovery_day` | `TEXT DEFAULT NULL` | :1292 |
| `users` | `ap_restored_day` | `TEXT DEFAULT NULL` | :1165 |
| `users` | `ap_restored_today` | `INTEGER DEFAULT 0` | :1166 |
| `users` | `beer_used_day` | `TEXT DEFAULT NULL` | :1295 |
| `users` | `beer_used_today` | `INTEGER DEFAULT 0` | :1294 |
| `users` | `callsign` | `TEXT` | :1250 |
| `users` | `callsign_free_used` | `INTEGER DEFAULT 0` | :1441 |
| `users` | `duel_losses` | `INTEGER DEFAULT 0` | :1170 |
| `users` | `duel_rating` | `INTEGER DEFAULT 0` | :1168 |
| `users` | `duel_wins` | `INTEGER DEFAULT 0` | :1169 |
| `users` | `equipment` | `TEXT DEFAULT '{}'` | :1045 |
| `users` | `fish_sold_day` | `TEXT DEFAULT NULL` | :1321 |
| `users` | `fish_sold_today` | `INTEGER DEFAULT 0` | :1322 |
| `users` | `fishing_bait` | `TEXT DEFAULT ''` | :1248 |
| `users` | `forest_attempts_since_boar` | `INTEGER DEFAULT 0` | :1324 |
| `users` | `forest_attempts_since_wolf` | `INTEGER DEFAULT 0` | :1326 |
| `users` | `forest_sold_day` | `TEXT DEFAULT NULL` | :1336 |
| `users` | `forest_sold_today` | `INTEGER DEFAULT 0` | :1337 |
| `users` | `fountain_used_day` | `TEXT DEFAULT NULL` | :1315 |
| `users` | `fountain_used_today` | `INTEGER DEFAULT 0` | :1316 |
| `users` | `last_active` | `REAL DEFAULT 0` | :1173 |
| `users` | `last_salary_date` | `TIMESTAMP` | :1048 |
| `users` | `legioner` | `INTEGER DEFAULT 0` | :1486 |
| `users` | `logging_attempts_since_owl` | `INTEGER DEFAULT 0` | :1333 |
| `users` | `logging_attempts_since_snake` | `INTEGER DEFAULT 0` | :1332 |
| `users` | `market_license_expires` | `TEXT DEFAULT NULL` | :1440 |
| `users` | `mine_attempts_since_bat` | `INTEGER DEFAULT 0` | :1329 |
| `users` | `notify_enabled` | `INTEGER DEFAULT 1` | :1042 |
| `users` | `profile_public` | `INTEGER DEFAULT 1` | :1043 |
| `users` | `promoted_rank` | `TEXT` | :1022 |
| `users` | `salary` | `INTEGER DEFAULT 0` | :1046 |
| `users` | `salary_debt` | `INTEGER DEFAULT 0` | :1049 |
| `users` | `salary_period_days` | `INTEGER DEFAULT 7` | :1047 |
| `users` | `seaweed_used_day` | `TEXT DEFAULT NULL` | :1289 |
| `users` | `seaweed_used_today` | `INTEGER DEFAULT 0` | :1288 |
| `users` | `shower_used_day` | `TEXT DEFAULT NULL` | :1318 |
| `users` | `shower_used_today` | `INTEGER DEFAULT 0` | :1319 |
| `users` | `special_blocked_until` | `TEXT DEFAULT NULL` | :1303 |
| `users` | `special_fails_today` | `INTEGER DEFAULT 0` | :1302 |
| `users` | `wing` | `TEXT` | :1483 |
| `users` | `xp_balance` | `INTEGER DEFAULT 0` | :1026 |
| `water_fish` | `excluded` | `INTEGER DEFAULT 0` | :1246 |
| `water_fish` | `kind` | `TEXT DEFAULT 'fish'` | :1462 |
| `water_fish` | `super_rare` | `INTEGER DEFAULT 0` | :1465 |
| `wings` | `abbr` | `TEXT DEFAULT ''` | :1282 |
| `wings` | `callsign` | `TEXT DEFAULT ''` | :1284 |
| `wings` | `emoji` | `TEXT DEFAULT ''` | :1285 |
| `wings` | `name` | `TEXT DEFAULT ''` | :1283 |
| `wings` | `num` | `TEXT DEFAULT ''` | :1281 |
| `wings` | `sort_order` | `INTEGER DEFAULT 0` | :1286 |

## 2. Идемпотентные засевы и миграции данных

| Функция | Вызывается из main.py | Назначение (первая строка docstring) | db.py |
|---|---|---|---|
| `backfill_rank_statuses` | — | Разово выдать статусы по текущим званиям всех пилотов (войска и админ-звания). | :5751 |
| `ensure_achievements` | ✅ | Идемпотентно засевает награды-уровни достижений и синхронизирует их. | :12284 |
| `ensure_base_status` | — | Базовый статус «Турист» для каждого нового игрока. | :5988 |
| `ensure_base_statuses` | — | Создаёт базовые статусы иерархии, если их нет. | :5943 |
| `ensure_clan_building` | — | — | :13764 |
| `ensure_duel_items` | ✅ | Товары Дома Дуэлей: дуэльные перчатки (отдельный слот) и клубная карта. | :10000 |
| `ensure_dungeon_enemy_drops` | ✅ | Синхронизирует врагов существующего данжа с DEFAULT_DUNGEON (дропы, HP, награды, | :11819 |
| `ensure_dungeon_reservoir_items` | ✅ | Идемпотентно добавляет предметы водохранилища подземелья (v0.12.0). | :11723 |
| `ensure_dungeon_shop_items` | ✅ | Идемпотентно добавляет предметы данжа (зелье в магазин, трофеи) — для существующих БД. | :11338 |
| `ensure_fishing_enemies` | ✅ | Идемпотентно засевает врагов рыбалки (мутировавший моллюск) из MOLLUSK_SEED. | :9038 |
| `ensure_forest_enemies` | ✅ | Идемпотентно засевает врагов леса (кабан и Белый Волк Севера). | :9013 |
| `ensure_forest_items` | ✅ | Идемпотентно создаёт предметы леса (грибы, добыча кабана, жареные блюда, яд). | :8367 |
| `ensure_forest_mushrooms` | ✅ | Идемпотентно засевает пул грибов леса из FOREST_DEFAULTS. | :8531 |
| `ensure_forest_zones` | ✅ | Разовый перенос старого пула леса в зону поляны и засев пула опушки. | :8774 |
| `ensure_kvp_award` | ✅ | — | :10259 |
| `ensure_kvp_items` | ✅ | Обеспечивает эксклюзивный предмет К.В.П. — «Сержантскую трость». | :9973 |
| `ensure_kvp_user` | — | Гарантирует наличие строки прогресса К.В.П. для игрока. | :10446 |
| `ensure_life_items` | ✅ | Идемпотентно добавляет предметы жилья, мебели, семян, ресурсов и продовольствия. | :11544 |
| `ensure_logging_enemies` | ✅ | Идемпотентно засевает врагов Лесозаготовки (Змея и Неясыть). | :8520 |
| `ensure_logging_items` | ✅ | Идемпотентно создаёт предметы Лесозаготовки (топор, бревна, дропы). | :8477 |
| `ensure_market_license_item` | ✅ | Идемпотентно добавляет «Торговую лицензию» в магазин. | :9522 |
| `ensure_mine_enemies` | ✅ | Идемпотентно засевает врагов копи (Летучая мышь) из MINE_BAT_SEED. | :8468 |
| `ensure_mine_items` | ✅ | Идемпотентно создаёт предметы Железной копи (кирка, руда, самоцветы). | :8437 |
| `ensure_mollusk_items` | ✅ | Идемпотентно создаёт предметы моллюска (из его добычи и готового блюда). | :9044 |
| `ensure_player_housing` | — | Возвращает жильё игрока, создавая муниципальную квартиру для пилота при первом обращении. | :11940 |
| `ensure_rank_statuses_for_troops` | — | Выдать статус по текущему званию игрока (по войскам или админ-назначению). | :5739 |
| `ensure_recipe_shop_item` | — | Синхронизирует товар-рецепт «Рецепт: <name>» с рецептом (менеджер). | :12697 |
| `ensure_recipe_shop_items` | ✅ | Создаёт в магазине предметы-рецепты категории 'recipes'. | :13570 |
| `ensure_recipes` | ✅ | Идемпотентно засевает рецепты и синхронизирует уже существующие. | :12547 |
| `ensure_tourist_booklet` | ✅ | Создаёт предмет «Буклет туриста» и награду «Опытный турист», если их нет. | :10295 |
| `ensure_user_recipes_backfill` | ✅ | Разово открывает все рецепты существующим игрокам. | :13681 |
| `ensure_water_fish` | ✅ | Идемпотентно засевает water_fish из дефолтов. Правившие админом строки | :7967 |
| `migrate_legacy_junk` | ✅ | Переносит старые копии мусора (сапог, водоросли) из инвентаря в улов. | :7813 |
| `seed_default_items` | ✅ | Заполняет магазин базовым набором товаров, если он пуст и не было своих товаров. | :9696 |
| `seed_dungeon` | ✅ | — | :9851 |
| `seed_kvp` | ✅ | Создаёт тренировочный данж К.В.П. с врагами (Ефрейтор, Старший сержант), если его нет. | :9922 |
| `seed_locations` | — | Засеивает базовые локации города (Ратуша, Библиотека) как пример управляемого доступа. | :1673 |

## 3. Отдельные скрипты миграций

- `migrate_113.py` — Проверка миграций 0.19.0 на чистой БД: колонки polls, таблица rep_speeches.
- `migrate_113_old.py` — Миграция 0.19.0 поверх БД со старой схемой polls (без closes_at/is_archived).

