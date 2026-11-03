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

Всего вызовов: **194**; таблиц: **29**.

| Таблица | Колонка | Тип / значение по умолчанию | db.py |
|---|---|---|---|
| `awards` | `achievement_key` | `TEXT DEFAULT NULL` | :1402 |
| `awards` | `achievement_level` | `INTEGER DEFAULT 0` | :1403 |
| `awards` | `bonus_attack` | `INTEGER DEFAULT 0` | :1381 |
| `awards` | `bonus_crit` | `INTEGER DEFAULT 0` | :1388 |
| `awards` | `bonus_defense` | `INTEGER DEFAULT 0` | :1382 |
| `awards` | `bonus_dodge` | `INTEGER DEFAULT 0` | :1383 |
| `awards` | `bonus_fishing` | `INTEGER DEFAULT 0` | :1384 |
| `awards` | `bonus_hp` | `INTEGER DEFAULT 0` | :1385 |
| `awards` | `bonus_json` | `TEXT DEFAULT '{}'` | :1404 |
| `awards` | `bonus_report_tax` | `INTEGER DEFAULT 0` | :1392 |
| `awards` | `bonus_shop_discount` | `INTEGER DEFAULT 0` | :1391 |
| `awards` | `image` | `TEXT` | :1380 |
| `awards` | `monthly_nm` | `INTEGER DEFAULT 0` | :1396 |
| `awards` | `reward_nm` | `INTEGER DEFAULT 0` | :1395 |
| `buildings` | `required_status` | `TEXT` | :1145 |
| `clan_buildings` | `building_photo_file_id` | `TEXT` | :1778 |
| `clan_members` | `role` | `TEXT NOT NULL DEFAULT 'member'` | :1147 |
| `clans` | `tree_amber_at` | `TEXT DEFAULT NULL` | :1451 |
| `dungeon_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1316 |
| `dungeon_enemies` | `admin_tuned` | `INTEGER DEFAULT 0` | :1352 |
| `dungeon_enemies` | `armor` | `INTEGER DEFAULT 0` | :1312 |
| `dungeon_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1583 |
| `dungeon_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1584 |
| `dungeon_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1314 |
| `dungeon_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1315 |
| `dungeon_enemies` | `damage_max` | `INTEGER DEFAULT 0` | :1311 |
| `dungeon_enemies` | `damage_min` | `INTEGER DEFAULT 0` | :1310 |
| `dungeon_enemies` | `description` | `TEXT` | :1308 |
| `dungeon_enemies` | `dodge` | `INTEGER DEFAULT 0` | :1309 |
| `dungeon_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1313 |
| `dungeon_enemies` | `drops` | `TEXT DEFAULT '[]'` | :1304 |
| `dungeon_enemies` | `frostbite_chance` | `INTEGER DEFAULT 0` | :1585 |
| `dungeon_enemies` | `image` | `TEXT` | :1305 |
| `dungeon_enemies` | `poison_chance` | `INTEGER DEFAULT 0` | :1306 |
| `dungeon_enemies` | `poison_dmg` | `INTEGER DEFAULT 0` | :1307 |
| `dungeons` | `is_training` | `INTEGER DEFAULT 0` | :1574 |
| `dungeons` | `photo_dawn` | `TEXT` | :1365 |
| `dungeons` | `photo_day` | `TEXT` | :1366 |
| `dungeons` | `photo_night` | `TEXT` | :1368 |
| `dungeons` | `photo_rope` | `TEXT` | :1371 |
| `dungeons` | `photo_sunset` | `TEXT` | :1367 |
| `dungeons` | `photo_water` | `TEXT` | :1370 |
| `dungeons` | `rooms_map` | `TEXT` | :1590 |
| `fire_lab_sessions` | `boss_encounters` | `INTEGER DEFAULT 0` | :1783 |
| `fire_lab_sessions` | `effects_json` | `TEXT DEFAULT NULL` | :1782 |
| `fire_lab_sessions` | `enemy_json` | `TEXT DEFAULT NULL` | :1781 |
| `fire_lab_sessions` | `fish_used` | `INTEGER DEFAULT 0` | :1784 |
| `fire_lab_sessions` | `last_active_at` | `TIMESTAMP` | :1790 |
| `fire_lab_sessions` | `tree_open` | `INTEGER DEFAULT 0` | :1788 |
| `fire_lab_sessions` | `well_open` | `INTEGER DEFAULT 0` | :1786 |
| `firelab_enemies` | `armor` | `INTEGER DEFAULT 0` | :1780 |
| `firelab_enemies` | `on_hit_effects` | `TEXT DEFAULT NULL` | :1779 |
| `fish_catches` | `expires_at` | `TIMESTAMP` | :1441 |
| `fish_catches` | `kind` | `TEXT DEFAULT 'fish'` | :1596 |
| `fishing_enemies` | `armor` | `INTEGER DEFAULT 0` | :1327 |
| `fishing_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1325 |
| `fishing_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1326 |
| `forest_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1321 |
| `forest_enemies` | `armor` | `INTEGER DEFAULT 0` | :1317 |
| `forest_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1323 |
| `forest_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1324 |
| `forest_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1319 |
| `forest_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1320 |
| `forest_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1318 |
| `forest_mushrooms` | `zone` | `TEXT DEFAULT 'clearing'` | :1493 |
| `housing_slots` | `embedded` | `INTEGER DEFAULT 0` | :1524 |
| `inventory` | `expires_at` | `TIMESTAMP` | :1436 |
| `inventory` | `plant_data` | `TEXT` | :1438 |
| `items` | `armor` | `INTEGER DEFAULT 0` | :1178 |
| `items` | `crit_chance` | `INTEGER DEFAULT 0` | :1181 |
| `items` | `crit_mult` | `REAL DEFAULT 0` | :1182 |
| `items` | `cure_frostbite` | `INTEGER DEFAULT 0` | :1587 |
| `items` | `cure_poison` | `INTEGER DEFAULT 0` | :1353 |
| `items` | `damage` | `INTEGER DEFAULT 0` | :1302 |
| `items` | `dodge_bonus` | `INTEGER DEFAULT 0` | :1620 |
| `items` | `dodge_buff_pct` | `INTEGER DEFAULT 0` | :1624 |
| `items` | `drink_effect` | `TEXT DEFAULT NULL` | :1424 |
| `items` | `equip_slot` | `TEXT` | :1184 |
| `items` | `heal` | `INTEGER DEFAULT 0` | :1303 |
| `items` | `heal_bonus_pct` | `INTEGER DEFAULT 0` | :1619 |
| `items` | `housing_slots` | `INTEGER` | :1730 |
| `items` | `housing_type` | `TEXT` | :1729 |
| `items` | `loot_only` | `INTEGER DEFAULT 0` | :1735 |
| `items` | `market_ok` | `INTEGER DEFAULT 0` | :1593 |
| `items` | `plant_name` | `TEXT` | :1603 |
| `items` | `regen` | `INTEGER DEFAULT 0` | :1363 |
| `items` | `regen_turns` | `INTEGER DEFAULT 0` | :1623 |
| `items` | `required_status` | `TEXT` | :1144 |
| `items` | `weapon_effect` | `TEXT` | :1614 |
| `items` | `weapon_effect_chance` | `INTEGER DEFAULT 0` | :1615 |
| `items` | `weapon_effect_dmg` | `INTEGER DEFAULT 0` | :1616 |
| `locations` | `clearing_photo` | `TEXT DEFAULT NULL` | :1479 |
| `locations` | `fire_photo` | `TEXT DEFAULT NULL` | :1477 |
| `locations` | `glade_photo` | `TEXT DEFAULT NULL` | :1478 |
| `locations` | `logging_photo` | `TEXT DEFAULT NULL` | :1488 |
| `locations` | `mine_level_photo` | `TEXT DEFAULT NULL` | :1482 |
| `locations` | `photo_dawn` | `TEXT` | :1355 |
| `locations` | `photo_day` | `TEXT` | :1356 |
| `locations` | `photo_night` | `TEXT` | :1358 |
| `locations` | `photo_sunset` | `TEXT` | :1357 |
| `locations` | `preview_photo` | `TEXT` | :1354 |
| `locations` | `season_photos` | `TEXT DEFAULT NULL` | :1474 |
| `locations` | `storage_photo` | `TEXT DEFAULT NULL` | :1484 |
| `locations` | `visits` | `INTEGER DEFAULT 0` | :1360 |
| `logging_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1342 |
| `logging_enemies` | `armor` | `INTEGER DEFAULT 0` | :1338 |
| `logging_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1340 |
| `logging_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1341 |
| `logging_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1339 |
| `market_fish` | `base_price` | `INTEGER DEFAULT 0` | :1577 |
| `mine_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1333 |
| `mine_enemies` | `armor` | `INTEGER DEFAULT 0` | :1329 |
| `mine_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1334 |
| `mine_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1335 |
| `mine_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1331 |
| `mine_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1332 |
| `mine_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1330 |
| `nii_reports` | `photo2_file_id` | `TEXT DEFAULT NULL` | :1406 |
| `player_dungeon_run` | `loot_nm` | `INTEGER DEFAULT 0` | :1289 |
| `player_dungeon_run` | `started_at` | `TIMESTAMP DEFAULT CURRENT_TIMESTAMP` | :1290 |
| `player_housing` | `expansions_installed` | `INTEGER DEFAULT 0` | :1526 |
| `player_housing` | `housing_label` | `TEXT` | :1731 |
| `player_housing` | `housing_slots` | `INTEGER` | :1732 |
| `player_housing` | `tax_last_check` | `TEXT DEFAULT NULL` | :1578 |
| `player_housing` | `tax_unpaid_months` | `INTEGER DEFAULT 0` | :1579 |
| `polls` | `archived_day` | `TEXT DEFAULT ''` | :1542 |
| `polls` | `closed_at` | `TIMESTAMP` | :1434 |
| `polls` | `closed_by` | `INTEGER` | :1433 |
| `polls` | `closes_at` | `TIMESTAMP` | :1531 |
| `polls` | `is_archived` | `INTEGER DEFAULT 0` | :1541 |
| `reports` | `credited_troops` | `INTEGER` | :1189 |
| `reports` | `paid` | `INTEGER DEFAULT 0` | :1196 |
| `reports` | `total_troops` | `INTEGER DEFAULT 0` | :1187 |
| `statuses` | `sort_order` | `INTEGER DEFAULT 0` | :1146 |
| `users` | `about` | `TEXT DEFAULT ''` | :1172 |
| `users` | `alcohol_strong_used_day` | `TEXT DEFAULT NULL` | :1428 |
| `users` | `alcohol_strong_used_today` | `INTEGER DEFAULT 0` | :1427 |
| `users` | `alcohol_weak_used_day` | `TEXT DEFAULT NULL` | :1426 |
| `users` | `alcohol_weak_used_today` | `INTEGER DEFAULT 0` | :1425 |
| `users` | `ap_recovery_day` | `TEXT DEFAULT NULL` | :1420 |
| `users` | `ap_restored_day` | `TEXT DEFAULT NULL` | :1293 |
| `users` | `ap_restored_today` | `INTEGER DEFAULT 0` | :1294 |
| `users` | `beer_used_day` | `TEXT DEFAULT NULL` | :1423 |
| `users` | `beer_used_today` | `INTEGER DEFAULT 0` | :1422 |
| `users` | `callsign` | `TEXT` | :1378 |
| `users` | `callsign_free_used` | `INTEGER DEFAULT 0` | :1576 |
| `users` | `dodge_buff_pct` | `INTEGER DEFAULT 0` | :1626 |
| `users` | `dodge_buff_until` | `TEXT DEFAULT NULL` | :1625 |
| `users` | `duel_losses` | `INTEGER DEFAULT 0` | :1298 |
| `users` | `duel_rating` | `INTEGER DEFAULT 0` | :1296 |
| `users` | `duel_wins` | `INTEGER DEFAULT 0` | :1297 |
| `users` | `equipment` | `TEXT DEFAULT '{}'` | :1173 |
| `users` | `fish_sold_day` | `TEXT DEFAULT NULL` | :1455 |
| `users` | `fish_sold_today` | `INTEGER DEFAULT 0` | :1456 |
| `users` | `fishing_bait` | `TEXT DEFAULT ''` | :1376 |
| `users` | `forest_attempts_since_boar` | `INTEGER DEFAULT 0` | :1458 |
| `users` | `forest_attempts_since_wolf` | `INTEGER DEFAULT 0` | :1460 |
| `users` | `forest_sold_day` | `TEXT DEFAULT NULL` | :1470 |
| `users` | `forest_sold_today` | `INTEGER DEFAULT 0` | :1471 |
| `users` | `fountain_used_day` | `TEXT DEFAULT NULL` | :1443 |
| `users` | `fountain_used_today` | `INTEGER DEFAULT 0` | :1444 |
| `users` | `lang` | `TEXT DEFAULT 'ru'` | :1150 |
| `users` | `lantern_amber_at` | `TEXT DEFAULT NULL` | :1449 |
| `users` | `lantern_medit_day` | `TEXT DEFAULT NULL` | :1448 |
| `users` | `last_active` | `REAL DEFAULT 0` | :1301 |
| `users` | `last_salary_date` | `TIMESTAMP` | :1176 |
| `users` | `legioner` | `INTEGER DEFAULT 0` | :1672 |
| `users` | `logging_attempts_since_owl` | `INTEGER DEFAULT 0` | :1467 |
| `users` | `logging_attempts_since_snake` | `INTEGER DEFAULT 0` | :1466 |
| `users` | `market_license_expires` | `TEXT DEFAULT NULL` | :1575 |
| `users` | `mine_attempts_since_bat` | `INTEGER DEFAULT 0` | :1463 |
| `users` | `notify_enabled` | `INTEGER DEFAULT 1` | :1170 |
| `users` | `profile_public` | `INTEGER DEFAULT 1` | :1171 |
| `users` | `promoted_rank` | `TEXT` | :1149 |
| `users` | `salary` | `INTEGER DEFAULT 0` | :1174 |
| `users` | `salary_debt` | `INTEGER DEFAULT 0` | :1177 |
| `users` | `salary_period_days` | `INTEGER DEFAULT 7` | :1175 |
| `users` | `seaweed_used_day` | `TEXT DEFAULT NULL` | :1417 |
| `users` | `seaweed_used_today` | `INTEGER DEFAULT 0` | :1416 |
| `users` | `shower_used_day` | `TEXT DEFAULT NULL` | :1446 |
| `users` | `shower_used_today` | `INTEGER DEFAULT 0` | :1453 |
| `users` | `special_blocked_until` | `TEXT DEFAULT NULL` | :1431 |
| `users` | `special_fails_today` | `INTEGER DEFAULT 0` | :1430 |
| `users` | `wing` | `TEXT` | :1669 |
| `users` | `xp_balance` | `INTEGER DEFAULT 0` | :1154 |
| `water_fish` | `excluded` | `INTEGER DEFAULT 0` | :1374 |
| `water_fish` | `kind` | `TEXT DEFAULT 'fish'` | :1597 |
| `water_fish` | `super_rare` | `INTEGER DEFAULT 0` | :1600 |
| `wings` | `abbr` | `TEXT DEFAULT ''` | :1410 |
| `wings` | `callsign` | `TEXT DEFAULT ''` | :1412 |
| `wings` | `emoji` | `TEXT DEFAULT ''` | :1413 |
| `wings` | `name` | `TEXT DEFAULT ''` | :1411 |
| `wings` | `num` | `TEXT DEFAULT ''` | :1409 |
| `wings` | `sort_order` | `INTEGER DEFAULT 0` | :1414 |

## 2. Идемпотентные засевы и миграции данных

| Функция | Вызывается из main.py | Назначение (первая строка docstring) | db.py |
|---|---|---|---|
| `backfill_rank_statuses` | — | Разово выдать статусы по текущим званиям всех пилотов (войска и админ-звания). | :6383 |
| `ensure_achievements` | ✅ | Идемпотентно засевает награды-уровни достижений и синхронизирует их. | :14149 |
| `ensure_base_status` | — | Базовый статус «Турист» для каждого нового игрока. | :6766 |
| `ensure_base_statuses` | — | Создаёт базовые статусы иерархии, если их нет. | :6721 |
| `ensure_berry_candy_recipe` | — | Рецепт «Леденец из ягод»: черника + малина + сахар. Создаётся скрытым: | :10235 |
| `ensure_clan_building` | — | — | :16248 |
| `ensure_clan_cape_item` | — | Клановая накидка: экипировка слота «Клановая накидка». Продаётся в клановой | :10217 |
| `ensure_duel_items` | ✅ | Товары Дома Дуэлей: дуэльные перчатки (отдельный слот) и клубная карта. | :11703 |
| `ensure_dungeon_enemy_drops` | ✅ | Синхронизирует врагов существующего данжа с DEFAULT_DUNGEON (дропы, HP, награды, | :13610 |
| `ensure_dungeon_reservoir_items` | ✅ | Идемпотентно добавляет предметы водохранилища подземелья (v0.12.0). | :13533 |
| `ensure_dungeon_shop_items` | ✅ | Идемпотентно добавляет предметы данжа (зелье в магазин, трофеи) — для существующих БД. | :13141 |
| `ensure_fire_mushroom_pool` | — | Огненный гриб — на прогалину с весом 15; по 1 снимаем с пяти самых редких грибов. Один раз. | :10095 |
| `ensure_fire_tree_items` | — | Предметы пожертвования и талисмана: скрыты, без цены продажи, не на рынке. | :10028 |
| `ensure_firelab_enemies` | ✅ | Идемпотентно засевает врагов Огненного Лабиринта (4 обычных + босс). | :10340 |
| `ensure_firelab_items` | ✅ | Идемпотентно создаёт предметы Фазы 3 «Дней Пламенного Круговорота». | :10388 |
| `ensure_fishing_enemies` | ✅ | Идемпотентно засевает врагов рыбалки (мутировавший моллюск) из MOLLUSK_SEED. | :10662 |
| `ensure_forest_berry_items` | — | Ягоды (горсть) и шкура медведя: предметы-ресурсы вне магазина. Идемпотентно. | :10199 |
| `ensure_forest_berry_pool` | — | Таблица ягод поиска по зонам (как у грибов): шансы правит админ. Засев — один раз. | :10066 |
| `ensure_forest_enemies` | ✅ | Идемпотентно засевает врагов леса (кабан и Белый Волк Севера). | :10308 |
| `ensure_forest_items` | ✅ | Идемпотентно создаёт предметы леса (грибы, добыча кабана, жареные блюда, яд). | :9260 |
| `ensure_forest_mushrooms` | ✅ | Идемпотентно засевает пул грибов леса из FOREST_DEFAULTS. | :9432 |
| `ensure_forest_zones` | ✅ | Разовый перенос старого пула леса в зону поляны и засев пула опушки. | :9675 |
| `ensure_kvp_award` | ✅ | — | :11962 |
| `ensure_kvp_items` | ✅ | Обеспечивает эксклюзивный предмет К.В.П. — «Сержантскую трость». | :11676 |
| `ensure_kvp_user` | — | Гарантирует наличие строки прогресса К.В.П. для игрока. | :12149 |
| `ensure_life_items` | ✅ | Идемпотентно добавляет предметы жилья, мебели, семян, ресурсов и продовольствия. | :13357 |
| `ensure_logging_enemies` | ✅ | Идемпотентно засевает врагов Лесозаготовки (Змея и Неясыть). | :9421 |
| `ensure_logging_items` | ✅ | Идемпотентно создаёт предметы Лесозаготовки (топор, бревна, дропы). | :9378 |
| `ensure_market_license_item` | ✅ | Идемпотентно добавляет «Торговую лицензию» в магазин. | :11225 |
| `ensure_mine_enemies` | ✅ | Идемпотентно засевает врагов копи (Летучая мышь) из MINE_BAT_SEED. | :9369 |
| `ensure_mine_items` | ✅ | Идемпотентно создаёт предметы Железной копи (кирка, руда, самоцветы). | :9338 |
| `ensure_mollusk_items` | ✅ | Идемпотентно создаёт предметы моллюска (из его добычи и готового блюда). | :10668 |
| `ensure_player_housing` | — | Возвращает жильё игрока, создавая муниципальную квартиру для пилота при первом обращении. | :13746 |
| `ensure_rank_statuses_for_troops` | — | Выдать статус по текущему званию игрока (по войскам или админ-назначению). | :6371 |
| `ensure_recipe_shop_item` | — | Синхронизирует товар-рецепт «Рецепт: <name>» с рецептом (менеджер). | :14574 |
| `ensure_recipe_shop_items` | ✅ | Создаёт в магазине предметы-рецепты категории 'recipes'. | :15924 |
| `ensure_recipes` | ✅ | Идемпотентно засевает рецепты и синхронизирует уже существующие. | :14424 |
| `ensure_tourist_booklet` | ✅ | Создаёт предмет «Буклет туриста» и награду «Опытный турист», если их нет. | :11998 |
| `ensure_user_recipes_backfill` | ✅ | Разово открывает все рецепты существующим игрокам. | :16074 |
| `ensure_water_fish` | ✅ | Идемпотентно засевает water_fish из дефолтов. Правившие админом строки | :8760 |
| `migrate_legacy_junk` | ✅ | Переносит старые копии мусора (сапог, водоросли) из инвентаря в улов. | :8605 |
| `seed_default_items` | ✅ | Заполняет магазин базовым набором товаров, если он пуст и не было своих товаров. | :11399 |
| `seed_dungeon` | ✅ | — | :11554 |
| `seed_kvp` | ✅ | Создаёт тренировочный данж К.В.П. с врагами (Ефрейтор, Старший сержант), если его нет. | :11625 |
| `seed_locations` | — | Засеивает базовые локации города (Ратуша, Библиотека) как пример управляемого доступа. | :1880 |

## 3. Отдельные скрипты миграций

- `migrate_113.py` — Проверка миграций 0.19.0 на чистой БД: колонки polls, таблица rep_speeches.
- `migrate_113_old.py` — Миграция 0.19.0 поверх БД со старой схемой polls (без closes_at/is_archived).

