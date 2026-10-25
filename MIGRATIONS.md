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
| `awards` | `achievement_key` | `TEXT DEFAULT NULL` | :1282 |
| `awards` | `achievement_level` | `INTEGER DEFAULT 0` | :1283 |
| `awards` | `bonus_attack` | `INTEGER DEFAULT 0` | :1261 |
| `awards` | `bonus_crit` | `INTEGER DEFAULT 0` | :1268 |
| `awards` | `bonus_defense` | `INTEGER DEFAULT 0` | :1262 |
| `awards` | `bonus_dodge` | `INTEGER DEFAULT 0` | :1263 |
| `awards` | `bonus_fishing` | `INTEGER DEFAULT 0` | :1264 |
| `awards` | `bonus_hp` | `INTEGER DEFAULT 0` | :1265 |
| `awards` | `bonus_json` | `TEXT DEFAULT '{}'` | :1284 |
| `awards` | `bonus_report_tax` | `INTEGER DEFAULT 0` | :1272 |
| `awards` | `bonus_shop_discount` | `INTEGER DEFAULT 0` | :1271 |
| `awards` | `image` | `TEXT` | :1260 |
| `awards` | `monthly_nm` | `INTEGER DEFAULT 0` | :1276 |
| `awards` | `reward_nm` | `INTEGER DEFAULT 0` | :1275 |
| `buildings` | `required_status` | `TEXT` | :1028 |
| `clan_buildings` | `building_photo_file_id` | `TEXT` | :1600 |
| `dungeon_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1196 |
| `dungeon_enemies` | `admin_tuned` | `INTEGER DEFAULT 0` | :1232 |
| `dungeon_enemies` | `armor` | `INTEGER DEFAULT 0` | :1192 |
| `dungeon_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1456 |
| `dungeon_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1457 |
| `dungeon_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1194 |
| `dungeon_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1195 |
| `dungeon_enemies` | `damage_max` | `INTEGER DEFAULT 0` | :1191 |
| `dungeon_enemies` | `damage_min` | `INTEGER DEFAULT 0` | :1190 |
| `dungeon_enemies` | `description` | `TEXT` | :1188 |
| `dungeon_enemies` | `dodge` | `INTEGER DEFAULT 0` | :1189 |
| `dungeon_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1193 |
| `dungeon_enemies` | `drops` | `TEXT DEFAULT '[]'` | :1184 |
| `dungeon_enemies` | `frostbite_chance` | `INTEGER DEFAULT 0` | :1458 |
| `dungeon_enemies` | `image` | `TEXT` | :1185 |
| `dungeon_enemies` | `poison_chance` | `INTEGER DEFAULT 0` | :1186 |
| `dungeon_enemies` | `poison_dmg` | `INTEGER DEFAULT 0` | :1187 |
| `dungeons` | `is_training` | `INTEGER DEFAULT 0` | :1447 |
| `dungeons` | `photo_dawn` | `TEXT` | :1245 |
| `dungeons` | `photo_day` | `TEXT` | :1246 |
| `dungeons` | `photo_night` | `TEXT` | :1248 |
| `dungeons` | `photo_rope` | `TEXT` | :1251 |
| `dungeons` | `photo_sunset` | `TEXT` | :1247 |
| `dungeons` | `photo_water` | `TEXT` | :1250 |
| `dungeons` | `rooms_map` | `TEXT` | :1463 |
| `fish_catches` | `expires_at` | `TIMESTAMP` | :1321 |
| `fish_catches` | `kind` | `TEXT DEFAULT 'fish'` | :1469 |
| `fishing_enemies` | `armor` | `INTEGER DEFAULT 0` | :1207 |
| `fishing_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1205 |
| `fishing_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1206 |
| `forest_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1201 |
| `forest_enemies` | `armor` | `INTEGER DEFAULT 0` | :1197 |
| `forest_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1203 |
| `forest_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1204 |
| `forest_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1199 |
| `forest_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1200 |
| `forest_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1198 |
| `forest_mushrooms` | `zone` | `TEXT DEFAULT 'clearing'` | :1366 |
| `housing_slots` | `embedded` | `INTEGER DEFAULT 0` | :1397 |
| `inventory` | `expires_at` | `TIMESTAMP` | :1316 |
| `inventory` | `plant_data` | `TEXT` | :1318 |
| `items` | `armor` | `INTEGER DEFAULT 0` | :1058 |
| `items` | `crit_chance` | `INTEGER DEFAULT 0` | :1061 |
| `items` | `crit_mult` | `REAL DEFAULT 0` | :1062 |
| `items` | `cure_frostbite` | `INTEGER DEFAULT 0` | :1460 |
| `items` | `cure_poison` | `INTEGER DEFAULT 0` | :1233 |
| `items` | `damage` | `INTEGER DEFAULT 0` | :1182 |
| `items` | `drink_effect` | `TEXT DEFAULT NULL` | :1304 |
| `items` | `equip_slot` | `TEXT` | :1064 |
| `items` | `heal` | `INTEGER DEFAULT 0` | :1183 |
| `items` | `housing_slots` | `INTEGER` | :1552 |
| `items` | `housing_type` | `TEXT` | :1551 |
| `items` | `loot_only` | `INTEGER DEFAULT 0` | :1557 |
| `items` | `market_ok` | `INTEGER DEFAULT 0` | :1466 |
| `items` | `plant_name` | `TEXT` | :1476 |
| `items` | `regen` | `INTEGER DEFAULT 0` | :1243 |
| `items` | `required_status` | `TEXT` | :1027 |
| `items` | `weapon_effect` | `TEXT` | :1487 |
| `items` | `weapon_effect_chance` | `INTEGER DEFAULT 0` | :1488 |
| `items` | `weapon_effect_dmg` | `INTEGER DEFAULT 0` | :1489 |
| `locations` | `clearing_photo` | `TEXT DEFAULT NULL` | :1352 |
| `locations` | `glade_photo` | `TEXT DEFAULT NULL` | :1351 |
| `locations` | `logging_photo` | `TEXT DEFAULT NULL` | :1361 |
| `locations` | `mine_level_photo` | `TEXT DEFAULT NULL` | :1355 |
| `locations` | `photo_dawn` | `TEXT` | :1235 |
| `locations` | `photo_day` | `TEXT` | :1236 |
| `locations` | `photo_night` | `TEXT` | :1238 |
| `locations` | `photo_sunset` | `TEXT` | :1237 |
| `locations` | `preview_photo` | `TEXT` | :1234 |
| `locations` | `season_photos` | `TEXT DEFAULT NULL` | :1348 |
| `locations` | `storage_photo` | `TEXT DEFAULT NULL` | :1357 |
| `locations` | `visits` | `INTEGER DEFAULT 0` | :1240 |
| `logging_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1222 |
| `logging_enemies` | `armor` | `INTEGER DEFAULT 0` | :1218 |
| `logging_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1220 |
| `logging_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1221 |
| `logging_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1219 |
| `market_fish` | `base_price` | `INTEGER DEFAULT 0` | :1450 |
| `mine_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1213 |
| `mine_enemies` | `armor` | `INTEGER DEFAULT 0` | :1209 |
| `mine_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1214 |
| `mine_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1215 |
| `mine_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1211 |
| `mine_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1212 |
| `mine_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1210 |
| `nii_reports` | `photo2_file_id` | `TEXT DEFAULT NULL` | :1286 |
| `player_dungeon_run` | `loot_nm` | `INTEGER DEFAULT 0` | :1169 |
| `player_dungeon_run` | `started_at` | `TIMESTAMP DEFAULT CURRENT_TIMESTAMP` | :1170 |
| `player_housing` | `expansions_installed` | `INTEGER DEFAULT 0` | :1399 |
| `player_housing` | `housing_label` | `TEXT` | :1553 |
| `player_housing` | `housing_slots` | `INTEGER` | :1554 |
| `player_housing` | `tax_last_check` | `TEXT DEFAULT NULL` | :1451 |
| `player_housing` | `tax_unpaid_months` | `INTEGER DEFAULT 0` | :1452 |
| `polls` | `archived_day` | `TEXT DEFAULT ''` | :1415 |
| `polls` | `closed_at` | `TIMESTAMP` | :1314 |
| `polls` | `closed_by` | `INTEGER` | :1313 |
| `polls` | `closes_at` | `TIMESTAMP` | :1404 |
| `polls` | `is_archived` | `INTEGER DEFAULT 0` | :1414 |
| `reports` | `credited_troops` | `INTEGER` | :1069 |
| `reports` | `paid` | `INTEGER DEFAULT 0` | :1076 |
| `reports` | `total_troops` | `INTEGER DEFAULT 0` | :1067 |
| `statuses` | `sort_order` | `INTEGER DEFAULT 0` | :1029 |
| `users` | `about` | `TEXT DEFAULT ''` | :1052 |
| `users` | `alcohol_strong_used_day` | `TEXT DEFAULT NULL` | :1308 |
| `users` | `alcohol_strong_used_today` | `INTEGER DEFAULT 0` | :1307 |
| `users` | `alcohol_weak_used_day` | `TEXT DEFAULT NULL` | :1306 |
| `users` | `alcohol_weak_used_today` | `INTEGER DEFAULT 0` | :1305 |
| `users` | `ap_recovery_day` | `TEXT DEFAULT NULL` | :1300 |
| `users` | `ap_restored_day` | `TEXT DEFAULT NULL` | :1173 |
| `users` | `ap_restored_today` | `INTEGER DEFAULT 0` | :1174 |
| `users` | `beer_used_day` | `TEXT DEFAULT NULL` | :1303 |
| `users` | `beer_used_today` | `INTEGER DEFAULT 0` | :1302 |
| `users` | `callsign` | `TEXT` | :1258 |
| `users` | `callsign_free_used` | `INTEGER DEFAULT 0` | :1449 |
| `users` | `duel_losses` | `INTEGER DEFAULT 0` | :1178 |
| `users` | `duel_rating` | `INTEGER DEFAULT 0` | :1176 |
| `users` | `duel_wins` | `INTEGER DEFAULT 0` | :1177 |
| `users` | `equipment` | `TEXT DEFAULT '{}'` | :1053 |
| `users` | `fish_sold_day` | `TEXT DEFAULT NULL` | :1329 |
| `users` | `fish_sold_today` | `INTEGER DEFAULT 0` | :1330 |
| `users` | `fishing_bait` | `TEXT DEFAULT ''` | :1256 |
| `users` | `forest_attempts_since_boar` | `INTEGER DEFAULT 0` | :1332 |
| `users` | `forest_attempts_since_wolf` | `INTEGER DEFAULT 0` | :1334 |
| `users` | `forest_sold_day` | `TEXT DEFAULT NULL` | :1344 |
| `users` | `forest_sold_today` | `INTEGER DEFAULT 0` | :1345 |
| `users` | `fountain_used_day` | `TEXT DEFAULT NULL` | :1323 |
| `users` | `fountain_used_today` | `INTEGER DEFAULT 0` | :1324 |
| `users` | `last_active` | `REAL DEFAULT 0` | :1181 |
| `users` | `last_salary_date` | `TIMESTAMP` | :1056 |
| `users` | `legioner` | `INTEGER DEFAULT 0` | :1494 |
| `users` | `logging_attempts_since_owl` | `INTEGER DEFAULT 0` | :1341 |
| `users` | `logging_attempts_since_snake` | `INTEGER DEFAULT 0` | :1340 |
| `users` | `market_license_expires` | `TEXT DEFAULT NULL` | :1448 |
| `users` | `mine_attempts_since_bat` | `INTEGER DEFAULT 0` | :1337 |
| `users` | `notify_enabled` | `INTEGER DEFAULT 1` | :1050 |
| `users` | `profile_public` | `INTEGER DEFAULT 1` | :1051 |
| `users` | `promoted_rank` | `TEXT` | :1030 |
| `users` | `salary` | `INTEGER DEFAULT 0` | :1054 |
| `users` | `salary_debt` | `INTEGER DEFAULT 0` | :1057 |
| `users` | `salary_period_days` | `INTEGER DEFAULT 7` | :1055 |
| `users` | `seaweed_used_day` | `TEXT DEFAULT NULL` | :1297 |
| `users` | `seaweed_used_today` | `INTEGER DEFAULT 0` | :1296 |
| `users` | `shower_used_day` | `TEXT DEFAULT NULL` | :1326 |
| `users` | `shower_used_today` | `INTEGER DEFAULT 0` | :1327 |
| `users` | `special_blocked_until` | `TEXT DEFAULT NULL` | :1311 |
| `users` | `special_fails_today` | `INTEGER DEFAULT 0` | :1310 |
| `users` | `wing` | `TEXT` | :1491 |
| `users` | `xp_balance` | `INTEGER DEFAULT 0` | :1034 |
| `water_fish` | `excluded` | `INTEGER DEFAULT 0` | :1254 |
| `water_fish` | `kind` | `TEXT DEFAULT 'fish'` | :1470 |
| `water_fish` | `super_rare` | `INTEGER DEFAULT 0` | :1473 |
| `wings` | `abbr` | `TEXT DEFAULT ''` | :1290 |
| `wings` | `callsign` | `TEXT DEFAULT ''` | :1292 |
| `wings` | `emoji` | `TEXT DEFAULT ''` | :1293 |
| `wings` | `name` | `TEXT DEFAULT ''` | :1291 |
| `wings` | `num` | `TEXT DEFAULT ''` | :1289 |
| `wings` | `sort_order` | `INTEGER DEFAULT 0` | :1294 |

## 2. Идемпотентные засевы и миграции данных

| Функция | Вызывается из main.py | Назначение (первая строка docstring) | db.py |
|---|---|---|---|
| `backfill_rank_statuses` | — | Разово выдать статусы по текущим званиям всех пилотов (войска и админ-звания). | :5759 |
| `ensure_achievements` | ✅ | Идемпотентно засевает награды-уровни достижений и синхронизирует их. | :12292 |
| `ensure_base_status` | — | Базовый статус «Турист» для каждого нового игрока. | :5996 |
| `ensure_base_statuses` | — | Создаёт базовые статусы иерархии, если их нет. | :5951 |
| `ensure_clan_building` | — | — | :13874 |
| `ensure_duel_items` | ✅ | Товары Дома Дуэлей: дуэльные перчатки (отдельный слот) и клубная карта. | :10008 |
| `ensure_dungeon_enemy_drops` | ✅ | Синхронизирует врагов существующего данжа с DEFAULT_DUNGEON (дропы, HP, награды, | :11827 |
| `ensure_dungeon_reservoir_items` | ✅ | Идемпотентно добавляет предметы водохранилища подземелья (v0.12.0). | :11731 |
| `ensure_dungeon_shop_items` | ✅ | Идемпотентно добавляет предметы данжа (зелье в магазин, трофеи) — для существующих БД. | :11346 |
| `ensure_fishing_enemies` | ✅ | Идемпотентно засевает врагов рыбалки (мутировавший моллюск) из MOLLUSK_SEED. | :9046 |
| `ensure_forest_enemies` | ✅ | Идемпотентно засевает врагов леса (кабан и Белый Волк Севера). | :9021 |
| `ensure_forest_items` | ✅ | Идемпотентно создаёт предметы леса (грибы, добыча кабана, жареные блюда, яд). | :8375 |
| `ensure_forest_mushrooms` | ✅ | Идемпотентно засевает пул грибов леса из FOREST_DEFAULTS. | :8539 |
| `ensure_forest_zones` | ✅ | Разовый перенос старого пула леса в зону поляны и засев пула опушки. | :8782 |
| `ensure_kvp_award` | ✅ | — | :10267 |
| `ensure_kvp_items` | ✅ | Обеспечивает эксклюзивный предмет К.В.П. — «Сержантскую трость». | :9981 |
| `ensure_kvp_user` | — | Гарантирует наличие строки прогресса К.В.П. для игрока. | :10454 |
| `ensure_life_items` | ✅ | Идемпотентно добавляет предметы жилья, мебели, семян, ресурсов и продовольствия. | :11552 |
| `ensure_logging_enemies` | ✅ | Идемпотентно засевает врагов Лесозаготовки (Змея и Неясыть). | :8528 |
| `ensure_logging_items` | ✅ | Идемпотентно создаёт предметы Лесозаготовки (топор, бревна, дропы). | :8485 |
| `ensure_market_license_item` | ✅ | Идемпотентно добавляет «Торговую лицензию» в магазин. | :9530 |
| `ensure_mine_enemies` | ✅ | Идемпотентно засевает врагов копи (Летучая мышь) из MINE_BAT_SEED. | :8476 |
| `ensure_mine_items` | ✅ | Идемпотентно создаёт предметы Железной копи (кирка, руда, самоцветы). | :8445 |
| `ensure_mollusk_items` | ✅ | Идемпотентно создаёт предметы моллюска (из его добычи и готового блюда). | :9052 |
| `ensure_player_housing` | — | Возвращает жильё игрока, создавая муниципальную квартиру для пилота при первом обращении. | :11948 |
| `ensure_rank_statuses_for_troops` | — | Выдать статус по текущему званию игрока (по войскам или админ-назначению). | :5747 |
| `ensure_recipe_shop_item` | — | Синхронизирует товар-рецепт «Рецепт: <name>» с рецептом (менеджер). | :12705 |
| `ensure_recipe_shop_items` | ✅ | Создаёт в магазине предметы-рецепты категории 'recipes'. | :13645 |
| `ensure_recipes` | ✅ | Идемпотентно засевает рецепты и синхронизирует уже существующие. | :12555 |
| `ensure_tourist_booklet` | ✅ | Создаёт предмет «Буклет туриста» и награду «Опытный турист», если их нет. | :10303 |
| `ensure_user_recipes_backfill` | ✅ | Разово открывает все рецепты существующим игрокам. | :13791 |
| `ensure_water_fish` | ✅ | Идемпотентно засевает water_fish из дефолтов. Правившие админом строки | :7975 |
| `migrate_legacy_junk` | ✅ | Переносит старые копии мусора (сапог, водоросли) из инвентаря в улов. | :7821 |
| `seed_default_items` | ✅ | Заполняет магазин базовым набором товаров, если он пуст и не было своих товаров. | :9704 |
| `seed_dungeon` | ✅ | — | :9859 |
| `seed_kvp` | ✅ | Создаёт тренировочный данж К.В.П. с врагами (Ефрейтор, Старший сержант), если его нет. | :9930 |
| `seed_locations` | — | Засеивает базовые локации города (Ратуша, Библиотека) как пример управляемого доступа. | :1681 |

## 3. Отдельные скрипты миграций

- `migrate_113.py` — Проверка миграций 0.19.0 на чистой БД: колонки polls, таблица rep_speeches.
- `migrate_113_old.py` — Миграция 0.19.0 поверх БД со старой схемой polls (без closes_at/is_archived).

