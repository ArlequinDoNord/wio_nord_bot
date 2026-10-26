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
| `awards` | `achievement_key` | `TEXT DEFAULT NULL` | :1294 |
| `awards` | `achievement_level` | `INTEGER DEFAULT 0` | :1295 |
| `awards` | `bonus_attack` | `INTEGER DEFAULT 0` | :1273 |
| `awards` | `bonus_crit` | `INTEGER DEFAULT 0` | :1280 |
| `awards` | `bonus_defense` | `INTEGER DEFAULT 0` | :1274 |
| `awards` | `bonus_dodge` | `INTEGER DEFAULT 0` | :1275 |
| `awards` | `bonus_fishing` | `INTEGER DEFAULT 0` | :1276 |
| `awards` | `bonus_hp` | `INTEGER DEFAULT 0` | :1277 |
| `awards` | `bonus_json` | `TEXT DEFAULT '{}'` | :1296 |
| `awards` | `bonus_report_tax` | `INTEGER DEFAULT 0` | :1284 |
| `awards` | `bonus_shop_discount` | `INTEGER DEFAULT 0` | :1283 |
| `awards` | `image` | `TEXT` | :1272 |
| `awards` | `monthly_nm` | `INTEGER DEFAULT 0` | :1288 |
| `awards` | `reward_nm` | `INTEGER DEFAULT 0` | :1287 |
| `buildings` | `required_status` | `TEXT` | :1040 |
| `clan_buildings` | `building_photo_file_id` | `TEXT` | :1612 |
| `dungeon_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1208 |
| `dungeon_enemies` | `admin_tuned` | `INTEGER DEFAULT 0` | :1244 |
| `dungeon_enemies` | `armor` | `INTEGER DEFAULT 0` | :1204 |
| `dungeon_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1468 |
| `dungeon_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1469 |
| `dungeon_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1206 |
| `dungeon_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1207 |
| `dungeon_enemies` | `damage_max` | `INTEGER DEFAULT 0` | :1203 |
| `dungeon_enemies` | `damage_min` | `INTEGER DEFAULT 0` | :1202 |
| `dungeon_enemies` | `description` | `TEXT` | :1200 |
| `dungeon_enemies` | `dodge` | `INTEGER DEFAULT 0` | :1201 |
| `dungeon_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1205 |
| `dungeon_enemies` | `drops` | `TEXT DEFAULT '[]'` | :1196 |
| `dungeon_enemies` | `frostbite_chance` | `INTEGER DEFAULT 0` | :1470 |
| `dungeon_enemies` | `image` | `TEXT` | :1197 |
| `dungeon_enemies` | `poison_chance` | `INTEGER DEFAULT 0` | :1198 |
| `dungeon_enemies` | `poison_dmg` | `INTEGER DEFAULT 0` | :1199 |
| `dungeons` | `is_training` | `INTEGER DEFAULT 0` | :1459 |
| `dungeons` | `photo_dawn` | `TEXT` | :1257 |
| `dungeons` | `photo_day` | `TEXT` | :1258 |
| `dungeons` | `photo_night` | `TEXT` | :1260 |
| `dungeons` | `photo_rope` | `TEXT` | :1263 |
| `dungeons` | `photo_sunset` | `TEXT` | :1259 |
| `dungeons` | `photo_water` | `TEXT` | :1262 |
| `dungeons` | `rooms_map` | `TEXT` | :1475 |
| `fish_catches` | `expires_at` | `TIMESTAMP` | :1333 |
| `fish_catches` | `kind` | `TEXT DEFAULT 'fish'` | :1481 |
| `fishing_enemies` | `armor` | `INTEGER DEFAULT 0` | :1219 |
| `fishing_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1217 |
| `fishing_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1218 |
| `forest_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1213 |
| `forest_enemies` | `armor` | `INTEGER DEFAULT 0` | :1209 |
| `forest_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1215 |
| `forest_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1216 |
| `forest_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1211 |
| `forest_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1212 |
| `forest_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1210 |
| `forest_mushrooms` | `zone` | `TEXT DEFAULT 'clearing'` | :1378 |
| `housing_slots` | `embedded` | `INTEGER DEFAULT 0` | :1409 |
| `inventory` | `expires_at` | `TIMESTAMP` | :1328 |
| `inventory` | `plant_data` | `TEXT` | :1330 |
| `items` | `armor` | `INTEGER DEFAULT 0` | :1070 |
| `items` | `crit_chance` | `INTEGER DEFAULT 0` | :1073 |
| `items` | `crit_mult` | `REAL DEFAULT 0` | :1074 |
| `items` | `cure_frostbite` | `INTEGER DEFAULT 0` | :1472 |
| `items` | `cure_poison` | `INTEGER DEFAULT 0` | :1245 |
| `items` | `damage` | `INTEGER DEFAULT 0` | :1194 |
| `items` | `drink_effect` | `TEXT DEFAULT NULL` | :1316 |
| `items` | `equip_slot` | `TEXT` | :1076 |
| `items` | `heal` | `INTEGER DEFAULT 0` | :1195 |
| `items` | `housing_slots` | `INTEGER` | :1564 |
| `items` | `housing_type` | `TEXT` | :1563 |
| `items` | `loot_only` | `INTEGER DEFAULT 0` | :1569 |
| `items` | `market_ok` | `INTEGER DEFAULT 0` | :1478 |
| `items` | `plant_name` | `TEXT` | :1488 |
| `items` | `regen` | `INTEGER DEFAULT 0` | :1255 |
| `items` | `required_status` | `TEXT` | :1039 |
| `items` | `weapon_effect` | `TEXT` | :1499 |
| `items` | `weapon_effect_chance` | `INTEGER DEFAULT 0` | :1500 |
| `items` | `weapon_effect_dmg` | `INTEGER DEFAULT 0` | :1501 |
| `locations` | `clearing_photo` | `TEXT DEFAULT NULL` | :1364 |
| `locations` | `glade_photo` | `TEXT DEFAULT NULL` | :1363 |
| `locations` | `logging_photo` | `TEXT DEFAULT NULL` | :1373 |
| `locations` | `mine_level_photo` | `TEXT DEFAULT NULL` | :1367 |
| `locations` | `photo_dawn` | `TEXT` | :1247 |
| `locations` | `photo_day` | `TEXT` | :1248 |
| `locations` | `photo_night` | `TEXT` | :1250 |
| `locations` | `photo_sunset` | `TEXT` | :1249 |
| `locations` | `preview_photo` | `TEXT` | :1246 |
| `locations` | `season_photos` | `TEXT DEFAULT NULL` | :1360 |
| `locations` | `storage_photo` | `TEXT DEFAULT NULL` | :1369 |
| `locations` | `visits` | `INTEGER DEFAULT 0` | :1252 |
| `logging_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1234 |
| `logging_enemies` | `armor` | `INTEGER DEFAULT 0` | :1230 |
| `logging_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1232 |
| `logging_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1233 |
| `logging_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1231 |
| `market_fish` | `base_price` | `INTEGER DEFAULT 0` | :1462 |
| `mine_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1225 |
| `mine_enemies` | `armor` | `INTEGER DEFAULT 0` | :1221 |
| `mine_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1226 |
| `mine_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1227 |
| `mine_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1223 |
| `mine_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1224 |
| `mine_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1222 |
| `nii_reports` | `photo2_file_id` | `TEXT DEFAULT NULL` | :1298 |
| `player_dungeon_run` | `loot_nm` | `INTEGER DEFAULT 0` | :1181 |
| `player_dungeon_run` | `started_at` | `TIMESTAMP DEFAULT CURRENT_TIMESTAMP` | :1182 |
| `player_housing` | `expansions_installed` | `INTEGER DEFAULT 0` | :1411 |
| `player_housing` | `housing_label` | `TEXT` | :1565 |
| `player_housing` | `housing_slots` | `INTEGER` | :1566 |
| `player_housing` | `tax_last_check` | `TEXT DEFAULT NULL` | :1463 |
| `player_housing` | `tax_unpaid_months` | `INTEGER DEFAULT 0` | :1464 |
| `polls` | `archived_day` | `TEXT DEFAULT ''` | :1427 |
| `polls` | `closed_at` | `TIMESTAMP` | :1326 |
| `polls` | `closed_by` | `INTEGER` | :1325 |
| `polls` | `closes_at` | `TIMESTAMP` | :1416 |
| `polls` | `is_archived` | `INTEGER DEFAULT 0` | :1426 |
| `reports` | `credited_troops` | `INTEGER` | :1081 |
| `reports` | `paid` | `INTEGER DEFAULT 0` | :1088 |
| `reports` | `total_troops` | `INTEGER DEFAULT 0` | :1079 |
| `statuses` | `sort_order` | `INTEGER DEFAULT 0` | :1041 |
| `users` | `about` | `TEXT DEFAULT ''` | :1064 |
| `users` | `alcohol_strong_used_day` | `TEXT DEFAULT NULL` | :1320 |
| `users` | `alcohol_strong_used_today` | `INTEGER DEFAULT 0` | :1319 |
| `users` | `alcohol_weak_used_day` | `TEXT DEFAULT NULL` | :1318 |
| `users` | `alcohol_weak_used_today` | `INTEGER DEFAULT 0` | :1317 |
| `users` | `ap_recovery_day` | `TEXT DEFAULT NULL` | :1312 |
| `users` | `ap_restored_day` | `TEXT DEFAULT NULL` | :1185 |
| `users` | `ap_restored_today` | `INTEGER DEFAULT 0` | :1186 |
| `users` | `beer_used_day` | `TEXT DEFAULT NULL` | :1315 |
| `users` | `beer_used_today` | `INTEGER DEFAULT 0` | :1314 |
| `users` | `callsign` | `TEXT` | :1270 |
| `users` | `callsign_free_used` | `INTEGER DEFAULT 0` | :1461 |
| `users` | `duel_losses` | `INTEGER DEFAULT 0` | :1190 |
| `users` | `duel_rating` | `INTEGER DEFAULT 0` | :1188 |
| `users` | `duel_wins` | `INTEGER DEFAULT 0` | :1189 |
| `users` | `equipment` | `TEXT DEFAULT '{}'` | :1065 |
| `users` | `fish_sold_day` | `TEXT DEFAULT NULL` | :1341 |
| `users` | `fish_sold_today` | `INTEGER DEFAULT 0` | :1342 |
| `users` | `fishing_bait` | `TEXT DEFAULT ''` | :1268 |
| `users` | `forest_attempts_since_boar` | `INTEGER DEFAULT 0` | :1344 |
| `users` | `forest_attempts_since_wolf` | `INTEGER DEFAULT 0` | :1346 |
| `users` | `forest_sold_day` | `TEXT DEFAULT NULL` | :1356 |
| `users` | `forest_sold_today` | `INTEGER DEFAULT 0` | :1357 |
| `users` | `fountain_used_day` | `TEXT DEFAULT NULL` | :1335 |
| `users` | `fountain_used_today` | `INTEGER DEFAULT 0` | :1336 |
| `users` | `last_active` | `REAL DEFAULT 0` | :1193 |
| `users` | `last_salary_date` | `TIMESTAMP` | :1068 |
| `users` | `legioner` | `INTEGER DEFAULT 0` | :1506 |
| `users` | `logging_attempts_since_owl` | `INTEGER DEFAULT 0` | :1353 |
| `users` | `logging_attempts_since_snake` | `INTEGER DEFAULT 0` | :1352 |
| `users` | `market_license_expires` | `TEXT DEFAULT NULL` | :1460 |
| `users` | `mine_attempts_since_bat` | `INTEGER DEFAULT 0` | :1349 |
| `users` | `notify_enabled` | `INTEGER DEFAULT 1` | :1062 |
| `users` | `profile_public` | `INTEGER DEFAULT 1` | :1063 |
| `users` | `promoted_rank` | `TEXT` | :1042 |
| `users` | `salary` | `INTEGER DEFAULT 0` | :1066 |
| `users` | `salary_debt` | `INTEGER DEFAULT 0` | :1069 |
| `users` | `salary_period_days` | `INTEGER DEFAULT 7` | :1067 |
| `users` | `seaweed_used_day` | `TEXT DEFAULT NULL` | :1309 |
| `users` | `seaweed_used_today` | `INTEGER DEFAULT 0` | :1308 |
| `users` | `shower_used_day` | `TEXT DEFAULT NULL` | :1338 |
| `users` | `shower_used_today` | `INTEGER DEFAULT 0` | :1339 |
| `users` | `special_blocked_until` | `TEXT DEFAULT NULL` | :1323 |
| `users` | `special_fails_today` | `INTEGER DEFAULT 0` | :1322 |
| `users` | `wing` | `TEXT` | :1503 |
| `users` | `xp_balance` | `INTEGER DEFAULT 0` | :1046 |
| `water_fish` | `excluded` | `INTEGER DEFAULT 0` | :1266 |
| `water_fish` | `kind` | `TEXT DEFAULT 'fish'` | :1482 |
| `water_fish` | `super_rare` | `INTEGER DEFAULT 0` | :1485 |
| `wings` | `abbr` | `TEXT DEFAULT ''` | :1302 |
| `wings` | `callsign` | `TEXT DEFAULT ''` | :1304 |
| `wings` | `emoji` | `TEXT DEFAULT ''` | :1305 |
| `wings` | `name` | `TEXT DEFAULT ''` | :1303 |
| `wings` | `num` | `TEXT DEFAULT ''` | :1301 |
| `wings` | `sort_order` | `INTEGER DEFAULT 0` | :1306 |

## 2. Идемпотентные засевы и миграции данных

| Функция | Вызывается из main.py | Назначение (первая строка docstring) | db.py |
|---|---|---|---|
| `backfill_rank_statuses` | — | Разово выдать статусы по текущим званиям всех пилотов (войска и админ-звания). | :5771 |
| `ensure_achievements` | ✅ | Идемпотентно засевает награды-уровни достижений и синхронизирует их. | :12304 |
| `ensure_base_status` | — | Базовый статус «Турист» для каждого нового игрока. | :6008 |
| `ensure_base_statuses` | — | Создаёт базовые статусы иерархии, если их нет. | :5963 |
| `ensure_clan_building` | — | — | :13887 |
| `ensure_duel_items` | ✅ | Товары Дома Дуэлей: дуэльные перчатки (отдельный слот) и клубная карта. | :10020 |
| `ensure_dungeon_enemy_drops` | ✅ | Синхронизирует врагов существующего данжа с DEFAULT_DUNGEON (дропы, HP, награды, | :11839 |
| `ensure_dungeon_reservoir_items` | ✅ | Идемпотентно добавляет предметы водохранилища подземелья (v0.12.0). | :11743 |
| `ensure_dungeon_shop_items` | ✅ | Идемпотентно добавляет предметы данжа (зелье в магазин, трофеи) — для существующих БД. | :11358 |
| `ensure_fishing_enemies` | ✅ | Идемпотентно засевает врагов рыбалки (мутировавший моллюск) из MOLLUSK_SEED. | :9058 |
| `ensure_forest_enemies` | ✅ | Идемпотентно засевает врагов леса (кабан и Белый Волк Севера). | :9033 |
| `ensure_forest_items` | ✅ | Идемпотентно создаёт предметы леса (грибы, добыча кабана, жареные блюда, яд). | :8387 |
| `ensure_forest_mushrooms` | ✅ | Идемпотентно засевает пул грибов леса из FOREST_DEFAULTS. | :8551 |
| `ensure_forest_zones` | ✅ | Разовый перенос старого пула леса в зону поляны и засев пула опушки. | :8794 |
| `ensure_kvp_award` | ✅ | — | :10279 |
| `ensure_kvp_items` | ✅ | Обеспечивает эксклюзивный предмет К.В.П. — «Сержантскую трость». | :9993 |
| `ensure_kvp_user` | — | Гарантирует наличие строки прогресса К.В.П. для игрока. | :10466 |
| `ensure_life_items` | ✅ | Идемпотентно добавляет предметы жилья, мебели, семян, ресурсов и продовольствия. | :11564 |
| `ensure_logging_enemies` | ✅ | Идемпотентно засевает врагов Лесозаготовки (Змея и Неясыть). | :8540 |
| `ensure_logging_items` | ✅ | Идемпотентно создаёт предметы Лесозаготовки (топор, бревна, дропы). | :8497 |
| `ensure_market_license_item` | ✅ | Идемпотентно добавляет «Торговую лицензию» в магазин. | :9542 |
| `ensure_mine_enemies` | ✅ | Идемпотентно засевает врагов копи (Летучая мышь) из MINE_BAT_SEED. | :8488 |
| `ensure_mine_items` | ✅ | Идемпотентно создаёт предметы Железной копи (кирка, руда, самоцветы). | :8457 |
| `ensure_mollusk_items` | ✅ | Идемпотентно создаёт предметы моллюска (из его добычи и готового блюда). | :9064 |
| `ensure_player_housing` | — | Возвращает жильё игрока, создавая муниципальную квартиру для пилота при первом обращении. | :11960 |
| `ensure_rank_statuses_for_troops` | — | Выдать статус по текущему званию игрока (по войскам или админ-назначению). | :5759 |
| `ensure_recipe_shop_item` | — | Синхронизирует товар-рецепт «Рецепт: <name>» с рецептом (менеджер). | :12717 |
| `ensure_recipe_shop_items` | ✅ | Создаёт в магазине предметы-рецепты категории 'recipes'. | :13658 |
| `ensure_recipes` | ✅ | Идемпотентно засевает рецепты и синхронизирует уже существующие. | :12567 |
| `ensure_tourist_booklet` | ✅ | Создаёт предмет «Буклет туриста» и награду «Опытный турист», если их нет. | :10315 |
| `ensure_user_recipes_backfill` | ✅ | Разово открывает все рецепты существующим игрокам. | :13804 |
| `ensure_water_fish` | ✅ | Идемпотентно засевает water_fish из дефолтов. Правившие админом строки | :7987 |
| `migrate_legacy_junk` | ✅ | Переносит старые копии мусора (сапог, водоросли) из инвентаря в улов. | :7833 |
| `seed_default_items` | ✅ | Заполняет магазин базовым набором товаров, если он пуст и не было своих товаров. | :9716 |
| `seed_dungeon` | ✅ | — | :9871 |
| `seed_kvp` | ✅ | Создаёт тренировочный данж К.В.П. с врагами (Ефрейтор, Старший сержант), если его нет. | :9942 |
| `seed_locations` | — | Засеивает базовые локации города (Ратуша, Библиотека) как пример управляемого доступа. | :1693 |

## 3. Отдельные скрипты миграций

- `migrate_113.py` — Проверка миграций 0.19.0 на чистой БД: колонки polls, таблица rep_speeches.
- `migrate_113_old.py` — Миграция 0.19.0 поверх БД со старой схемой polls (без closes_at/is_archived).

