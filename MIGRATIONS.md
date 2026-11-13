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

Всего вызовов: **201**; таблиц: **29**.

| Таблица | Колонка | Тип / значение по умолчанию | db.py |
|---|---|---|---|
| `awards` | `achievement_key` | `TEXT DEFAULT NULL` | :1422 |
| `awards` | `achievement_level` | `INTEGER DEFAULT 0` | :1423 |
| `awards` | `bonus_attack` | `INTEGER DEFAULT 0` | :1401 |
| `awards` | `bonus_crit` | `INTEGER DEFAULT 0` | :1408 |
| `awards` | `bonus_defense` | `INTEGER DEFAULT 0` | :1402 |
| `awards` | `bonus_dodge` | `INTEGER DEFAULT 0` | :1403 |
| `awards` | `bonus_fishing` | `INTEGER DEFAULT 0` | :1404 |
| `awards` | `bonus_hp` | `INTEGER DEFAULT 0` | :1405 |
| `awards` | `bonus_json` | `TEXT DEFAULT '{}'` | :1424 |
| `awards` | `bonus_report_tax` | `INTEGER DEFAULT 0` | :1412 |
| `awards` | `bonus_shop_discount` | `INTEGER DEFAULT 0` | :1411 |
| `awards` | `image` | `TEXT` | :1400 |
| `awards` | `monthly_nm` | `INTEGER DEFAULT 0` | :1416 |
| `awards` | `reward_nm` | `INTEGER DEFAULT 0` | :1415 |
| `buildings` | `required_status` | `TEXT` | :1145 |
| `clan_buildings` | `building_photo_file_id` | `TEXT` | :1812 |
| `clan_members` | `role` | `TEXT NOT NULL DEFAULT 'member'` | :1147 |
| `clans` | `tree_amber_at` | `TEXT DEFAULT NULL` | :1471 |
| `dungeon_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1324 |
| `dungeon_enemies` | `admin_tuned` | `INTEGER DEFAULT 0` | :1360 |
| `dungeon_enemies` | `armor` | `INTEGER DEFAULT 0` | :1320 |
| `dungeon_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1602 |
| `dungeon_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1603 |
| `dungeon_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1322 |
| `dungeon_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1323 |
| `dungeon_enemies` | `damage_max` | `INTEGER DEFAULT 0` | :1319 |
| `dungeon_enemies` | `damage_min` | `INTEGER DEFAULT 0` | :1318 |
| `dungeon_enemies` | `description` | `TEXT` | :1316 |
| `dungeon_enemies` | `dodge` | `INTEGER DEFAULT 0` | :1317 |
| `dungeon_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1321 |
| `dungeon_enemies` | `drops` | `TEXT DEFAULT '[]'` | :1312 |
| `dungeon_enemies` | `frostbite_chance` | `INTEGER DEFAULT 0` | :1604 |
| `dungeon_enemies` | `image` | `TEXT` | :1313 |
| `dungeon_enemies` | `poison_chance` | `INTEGER DEFAULT 0` | :1314 |
| `dungeon_enemies` | `poison_dmg` | `INTEGER DEFAULT 0` | :1315 |
| `dungeons` | `is_training` | `INTEGER DEFAULT 0` | :1593 |
| `dungeons` | `photo_dawn` | `TEXT` | :1373 |
| `dungeons` | `photo_day` | `TEXT` | :1374 |
| `dungeons` | `photo_night` | `TEXT` | :1376 |
| `dungeons` | `photo_rope` | `TEXT` | :1379 |
| `dungeons` | `photo_sunset` | `TEXT` | :1375 |
| `dungeons` | `photo_water` | `TEXT` | :1378 |
| `dungeons` | `rooms_map` | `TEXT` | :1609 |
| `fire_lab_sessions` | `boss_encounters` | `INTEGER DEFAULT 0` | :1819 |
| `fire_lab_sessions` | `effects_json` | `TEXT DEFAULT NULL` | :1818 |
| `fire_lab_sessions` | `enemy_json` | `TEXT DEFAULT NULL` | :1817 |
| `fire_lab_sessions` | `fish_used` | `INTEGER DEFAULT 0` | :1820 |
| `fire_lab_sessions` | `last_active_at` | `TIMESTAMP` | :1826 |
| `fire_lab_sessions` | `tree_open` | `INTEGER DEFAULT 0` | :1824 |
| `fire_lab_sessions` | `well_open` | `INTEGER DEFAULT 0` | :1822 |
| `firelab_enemies` | `armor` | `INTEGER DEFAULT 0` | :1816 |
| `firelab_enemies` | `on_hit_effects` | `TEXT DEFAULT NULL` | :1815 |
| `fish_catches` | `expires_at` | `TIMESTAMP` | :1461 |
| `fish_catches` | `kind` | `TEXT DEFAULT 'fish'` | :1615 |
| `fishing_enemies` | `armor` | `INTEGER DEFAULT 0` | :1335 |
| `fishing_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1333 |
| `fishing_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1334 |
| `forest_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1329 |
| `forest_enemies` | `armor` | `INTEGER DEFAULT 0` | :1325 |
| `forest_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1331 |
| `forest_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1332 |
| `forest_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1327 |
| `forest_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1328 |
| `forest_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1326 |
| `forest_mushrooms` | `zone` | `TEXT DEFAULT 'clearing'` | :1513 |
| `housing_slots` | `embedded` | `INTEGER DEFAULT 0` | :1544 |
| `inventory` | `expires_at` | `TIMESTAMP` | :1456 |
| `inventory` | `plant_data` | `TEXT` | :1458 |
| `inventory` | `shop_qty` | `INTEGER DEFAULT 0` | :1651 |
| `items` | `armor` | `INTEGER DEFAULT 0` | :1178 |
| `items` | `crit_chance` | `INTEGER DEFAULT 0` | :1181 |
| `items` | `crit_mult` | `REAL DEFAULT 0` | :1182 |
| `items` | `cure_frostbite` | `INTEGER DEFAULT 0` | :1606 |
| `items` | `cure_poison` | `INTEGER DEFAULT 0` | :1361 |
| `items` | `damage` | `INTEGER DEFAULT 0` | :1310 |
| `items` | `dodge_bonus` | `INTEGER DEFAULT 0` | :1639 |
| `items` | `dodge_buff_pct` | `INTEGER DEFAULT 0` | :1643 |
| `items` | `drink_effect` | `TEXT DEFAULT NULL` | :1444 |
| `items` | `equip_slot` | `TEXT` | :1184 |
| `items` | `heal` | `INTEGER DEFAULT 0` | :1311 |
| `items` | `heal_bonus_pct` | `INTEGER DEFAULT 0` | :1638 |
| `items` | `housing_slots` | `INTEGER` | :1764 |
| `items` | `housing_type` | `TEXT` | :1763 |
| `items` | `loot_only` | `INTEGER DEFAULT 0` | :1769 |
| `items` | `market_ok` | `INTEGER DEFAULT 0` | :1612 |
| `items` | `plant_name` | `TEXT` | :1622 |
| `items` | `regen` | `INTEGER DEFAULT 0` | :1371 |
| `items` | `regen_turns` | `INTEGER DEFAULT 0` | :1642 |
| `items` | `required_status` | `TEXT` | :1144 |
| `items` | `restock_enabled` | `INTEGER DEFAULT 0` | :1646 |
| `items` | `restock_target` | `INTEGER DEFAULT 0` | :1647 |
| `items` | `shop_limit` | `INTEGER DEFAULT 0` | :1650 |
| `items` | `weapon_effect` | `TEXT` | :1633 |
| `items` | `weapon_effect_chance` | `INTEGER DEFAULT 0` | :1634 |
| `items` | `weapon_effect_dmg` | `INTEGER DEFAULT 0` | :1635 |
| `locations` | `clearing_photo` | `TEXT DEFAULT NULL` | :1499 |
| `locations` | `fire_photo` | `TEXT DEFAULT NULL` | :1497 |
| `locations` | `glade_photo` | `TEXT DEFAULT NULL` | :1498 |
| `locations` | `logging_photo` | `TEXT DEFAULT NULL` | :1508 |
| `locations` | `mine_level_photo` | `TEXT DEFAULT NULL` | :1502 |
| `locations` | `photo_dawn` | `TEXT` | :1363 |
| `locations` | `photo_day` | `TEXT` | :1364 |
| `locations` | `photo_night` | `TEXT` | :1366 |
| `locations` | `photo_sunset` | `TEXT` | :1365 |
| `locations` | `preview_photo` | `TEXT` | :1362 |
| `locations` | `season_photos` | `TEXT DEFAULT NULL` | :1494 |
| `locations` | `storage_photo` | `TEXT DEFAULT NULL` | :1504 |
| `locations` | `visits` | `INTEGER DEFAULT 0` | :1368 |
| `logging_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1350 |
| `logging_enemies` | `armor` | `INTEGER DEFAULT 0` | :1346 |
| `logging_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1348 |
| `logging_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1349 |
| `logging_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1347 |
| `market_fish` | `base_price` | `INTEGER DEFAULT 0` | :1596 |
| `mine_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1341 |
| `mine_enemies` | `armor` | `INTEGER DEFAULT 0` | :1337 |
| `mine_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1342 |
| `mine_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1343 |
| `mine_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1339 |
| `mine_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1340 |
| `mine_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1338 |
| `nii_reports` | `photo2_file_id` | `TEXT DEFAULT NULL` | :1426 |
| `player_dungeon_run` | `loot_nm` | `INTEGER DEFAULT 0` | :1297 |
| `player_dungeon_run` | `started_at` | `TIMESTAMP DEFAULT CURRENT_TIMESTAMP` | :1298 |
| `player_housing` | `expansions_installed` | `INTEGER DEFAULT 0` | :1546 |
| `player_housing` | `housing_label` | `TEXT` | :1765 |
| `player_housing` | `housing_slots` | `INTEGER` | :1766 |
| `player_housing` | `tax_last_check` | `TEXT DEFAULT NULL` | :1597 |
| `player_housing` | `tax_unpaid_months` | `INTEGER DEFAULT 0` | :1598 |
| `polls` | `archived_day` | `TEXT DEFAULT ''` | :1562 |
| `polls` | `closed_at` | `TIMESTAMP` | :1454 |
| `polls` | `closed_by` | `INTEGER` | :1453 |
| `polls` | `closes_at` | `TIMESTAMP` | :1551 |
| `polls` | `is_archived` | `INTEGER DEFAULT 0` | :1561 |
| `reports` | `credited_troops` | `INTEGER` | :1189 |
| `reports` | `paid` | `INTEGER DEFAULT 0` | :1196 |
| `reports` | `reject_reason` | `TEXT` | :1202 |
| `reports` | `reviewed_at` | `TEXT` | :1206 |
| `reports` | `reviewed_by_name` | `TEXT` | :1203 |
| `reports` | `total_troops` | `INTEGER DEFAULT 0` | :1187 |
| `statuses` | `sort_order` | `INTEGER DEFAULT 0` | :1146 |
| `users` | `about` | `TEXT DEFAULT ''` | :1172 |
| `users` | `alcohol_strong_used_day` | `TEXT DEFAULT NULL` | :1448 |
| `users` | `alcohol_strong_used_today` | `INTEGER DEFAULT 0` | :1447 |
| `users` | `alcohol_weak_used_day` | `TEXT DEFAULT NULL` | :1446 |
| `users` | `alcohol_weak_used_today` | `INTEGER DEFAULT 0` | :1445 |
| `users` | `ap_recovery_day` | `TEXT DEFAULT NULL` | :1440 |
| `users` | `ap_restored_day` | `TEXT DEFAULT NULL` | :1301 |
| `users` | `ap_restored_today` | `INTEGER DEFAULT 0` | :1302 |
| `users` | `beer_used_day` | `TEXT DEFAULT NULL` | :1443 |
| `users` | `beer_used_today` | `INTEGER DEFAULT 0` | :1442 |
| `users` | `callsign` | `TEXT` | :1386 |
| `users` | `callsign_free_used` | `INTEGER DEFAULT 0` | :1595 |
| `users` | `dodge_buff_pct` | `INTEGER DEFAULT 0` | :1660 |
| `users` | `dodge_buff_until` | `TEXT DEFAULT NULL` | :1659 |
| `users` | `duel_losses` | `INTEGER DEFAULT 0` | :1306 |
| `users` | `duel_rating` | `INTEGER DEFAULT 0` | :1304 |
| `users` | `duel_wins` | `INTEGER DEFAULT 0` | :1305 |
| `users` | `equipment` | `TEXT DEFAULT '{}'` | :1173 |
| `users` | `fish_sold_day` | `TEXT DEFAULT NULL` | :1475 |
| `users` | `fish_sold_today` | `INTEGER DEFAULT 0` | :1476 |
| `users` | `fishing_bait` | `TEXT DEFAULT ''` | :1384 |
| `users` | `forest_attempts_since_boar` | `INTEGER DEFAULT 0` | :1478 |
| `users` | `forest_attempts_since_wolf` | `INTEGER DEFAULT 0` | :1480 |
| `users` | `forest_sold_day` | `TEXT DEFAULT NULL` | :1490 |
| `users` | `forest_sold_today` | `INTEGER DEFAULT 0` | :1491 |
| `users` | `fountain_used_day` | `TEXT DEFAULT NULL` | :1463 |
| `users` | `fountain_used_today` | `INTEGER DEFAULT 0` | :1464 |
| `users` | `lang` | `TEXT DEFAULT 'ru'` | :1150 |
| `users` | `lantern_amber_at` | `TEXT DEFAULT NULL` | :1469 |
| `users` | `lantern_medit_day` | `TEXT DEFAULT NULL` | :1468 |
| `users` | `last_active` | `REAL DEFAULT 0` | :1309 |
| `users` | `last_salary_date` | `TIMESTAMP` | :1176 |
| `users` | `legioner` | `INTEGER DEFAULT 0` | :1706 |
| `users` | `logging_attempts_since_owl` | `INTEGER DEFAULT 0` | :1487 |
| `users` | `logging_attempts_since_snake` | `INTEGER DEFAULT 0` | :1486 |
| `users` | `market_license_expires` | `TEXT DEFAULT NULL` | :1594 |
| `users` | `mine_attempts_since_bat` | `INTEGER DEFAULT 0` | :1483 |
| `users` | `notify_enabled` | `INTEGER DEFAULT 1` | :1170 |
| `users` | `profile_public` | `INTEGER DEFAULT 1` | :1171 |
| `users` | `promoted_rank` | `TEXT` | :1149 |
| `users` | `salary` | `INTEGER DEFAULT 0` | :1174 |
| `users` | `salary_debt` | `INTEGER DEFAULT 0` | :1177 |
| `users` | `salary_period_days` | `INTEGER DEFAULT 7` | :1175 |
| `users` | `seaweed_used_day` | `TEXT DEFAULT NULL` | :1437 |
| `users` | `seaweed_used_today` | `INTEGER DEFAULT 0` | :1436 |
| `users` | `shower_used_day` | `TEXT DEFAULT NULL` | :1466 |
| `users` | `shower_used_today` | `INTEGER DEFAULT 0` | :1473 |
| `users` | `special_blocked_until` | `TEXT DEFAULT NULL` | :1451 |
| `users` | `special_fails_today` | `INTEGER DEFAULT 0` | :1450 |
| `users` | `wing` | `TEXT` | :1703 |
| `users` | `xp_balance` | `INTEGER DEFAULT 0` | :1154 |
| `water_fish` | `excluded` | `INTEGER DEFAULT 0` | :1382 |
| `water_fish` | `kind` | `TEXT DEFAULT 'fish'` | :1616 |
| `water_fish` | `super_rare` | `INTEGER DEFAULT 0` | :1619 |
| `wings` | `abbr` | `TEXT DEFAULT ''` | :1430 |
| `wings` | `callsign` | `TEXT DEFAULT ''` | :1432 |
| `wings` | `emoji` | `TEXT DEFAULT ''` | :1433 |
| `wings` | `name` | `TEXT DEFAULT ''` | :1431 |
| `wings` | `num` | `TEXT DEFAULT ''` | :1429 |
| `wings` | `sort_order` | `INTEGER DEFAULT 0` | :1434 |

## 2. Идемпотентные засевы и миграции данных

| Функция | Вызывается из main.py | Назначение (первая строка docstring) | db.py |
|---|---|---|---|
| `backfill_rank_statuses` | — | Разово выдать статусы по текущим званиям всех пилотов (войска и админ-звания). | :6648 |
| `ensure_achievements` | ✅ | Идемпотентно засевает награды-уровни достижений и синхронизирует их. | :14484 |
| `ensure_base_status` | — | Базовый статус «Турист» для каждого нового игрока. | :7031 |
| `ensure_base_statuses` | — | Создаёт базовые статусы иерархии, если их нет. | :6986 |
| `ensure_berry_candy_recipe` | — | Рецепт «Леденец из ягод»: черника + малина + сахар. Создаётся скрытым: | :10562 |
| `ensure_clan_building` | — | — | :16583 |
| `ensure_clan_cape_item` | — | Клановая накидка: экипировка слота «Клановая накидка». Продаётся в клановой | :10544 |
| `ensure_duel_items` | ✅ | Товары Дома Дуэлей: дуэльные перчатки (отдельный слот) и клубная карта. | :12029 |
| `ensure_dungeon_enemy_drops` | ✅ | Синхронизирует врагов существующего данжа с DEFAULT_DUNGEON (дропы, HP, награды, | :13936 |
| `ensure_dungeon_reservoir_items` | ✅ | Идемпотентно добавляет предметы водохранилища подземелья (v0.12.0). | :13859 |
| `ensure_dungeon_shop_items` | ✅ | Идемпотентно добавляет предметы данжа (зелье в магазин, трофеи) — для существующих БД. | :13467 |
| `ensure_fire_mushroom_pool` | — | Огненный гриб — на прогалину с весом 15; по 1 снимаем с пяти самых редких грибов. Один раз. | :10420 |
| `ensure_fire_tree_items` | — | Предметы пожертвования и талисмана: скрыты, без цены продажи, не на рынке. | :10353 |
| `ensure_firelab_enemies` | ✅ | Идемпотентно засевает врагов Огненного Лабиринта (4 обычных + босс). | :10667 |
| `ensure_firelab_items` | ✅ | Идемпотентно создаёт предметы Фазы 3 «Дней Пламенного Круговорота». | :10715 |
| `ensure_fishing_enemies` | ✅ | Идемпотентно засевает врагов рыбалки (мутировавший моллюск) из MOLLUSK_SEED. | :10989 |
| `ensure_forest_berry_items` | — | Ягоды (горсть) и шкура медведя: предметы-ресурсы вне магазина. Идемпотентно. | :10524 |
| `ensure_forest_berry_pool` | — | Таблица ягод поиска по зонам (как у грибов): шансы правит админ. Засев — один раз. | :10391 |
| `ensure_forest_enemies` | ✅ | Идемпотентно засевает врагов леса (кабан и Белый Волк Севера). | :10635 |
| `ensure_forest_items` | ✅ | Идемпотентно создаёт предметы леса (грибы, добыча кабана, жареные блюда, яд). | :9581 |
| `ensure_forest_mushrooms` | ✅ | Идемпотентно засевает пул грибов леса из FOREST_DEFAULTS. | :9753 |
| `ensure_forest_zones` | ✅ | Разовый перенос старого пула леса в зону поляны и засев пула опушки. | :9996 |
| `ensure_item_rarity_unified` | ✅ | Идемпотентно применяет единую градацию редкости (v0.43.10). | :2121 |
| `ensure_kvp_award` | ✅ | — | :12288 |
| `ensure_kvp_items` | ✅ | Обеспечивает эксклюзивный предмет К.В.П. — «Сержантскую трость». | :12002 |
| `ensure_kvp_user` | — | Гарантирует наличие строки прогресса К.В.П. для игрока. | :12475 |
| `ensure_life_items` | ✅ | Идемпотентно добавляет предметы жилья, мебели, семян, ресурсов и продовольствия. | :13683 |
| `ensure_logging_enemies` | ✅ | Идемпотентно засевает врагов Лесозаготовки (Змея и Неясыть). | :9742 |
| `ensure_logging_items` | ✅ | Идемпотентно создаёт предметы Лесозаготовки (топор, бревна, дропы). | :9699 |
| `ensure_market_license_item` | ✅ | Идемпотентно добавляет «Торговую лицензию» в магазин. | :11552 |
| `ensure_mine_enemies` | ✅ | Идемпотентно засевает врагов копи (Летучая мышь) из MINE_BAT_SEED. | :9690 |
| `ensure_mine_items` | ✅ | Идемпотентно создаёт предметы Железной копи (кирка, руда, самоцветы). | :9659 |
| `ensure_mollusk_items` | ✅ | Идемпотентно создаёт предметы моллюска (из его добычи и готового блюда). | :10995 |
| `ensure_player_housing` | — | Возвращает жильё игрока, создавая муниципальную квартиру для пилота при первом обращении. | :14081 |
| `ensure_rank_statuses_for_troops` | — | Выдать статус по текущему званию игрока (по войскам или админ-назначению). | :6636 |
| `ensure_recipe_shop_item` | — | Синхронизирует товар-рецепт «Рецепт: <name>» с рецептом (менеджер). | :14909 |
| `ensure_recipe_shop_items` | ✅ | Создаёт в магазине предметы-рецепты категории 'recipes'. | :16259 |
| `ensure_recipes` | ✅ | Идемпотентно засевает рецепты и синхронизирует уже существующие. | :14759 |
| `ensure_tourist_booklet` | ✅ | Создаёт предмет «Буклет туриста» и награду «Опытный турист», если их нет. | :12324 |
| `ensure_user_recipes_backfill` | ✅ | Разово открывает все рецепты существующим игрокам. | :16409 |
| `ensure_water_fish` | ✅ | Идемпотентно засевает water_fish из дефолтов. Правившие админом строки | :9091 |
| `migrate_legacy_junk` | ✅ | Переносит старые копии мусора (сапог, водоросли) из инвентаря в улов. | :8936 |
| `seed_default_items` | ✅ | Заполняет магазин базовым набором товаров, если он пуст и не было своих товаров. | :11725 |
| `seed_dungeon` | ✅ | — | :11880 |
| `seed_kvp` | ✅ | Создаёт тренировочный данж К.В.П. с врагами (Ефрейтор, Старший сержант), если его нет. | :11951 |
| `seed_locations` | — | Засеивает базовые локации города (Ратуша, Библиотека) как пример управляемого доступа. | :1916 |

## 3. Отдельные скрипты миграций

- `migrate_113.py` — Проверка миграций 0.19.0 на чистой БД: колонки polls, таблица rep_speeches.
- `migrate_113_old.py` — Миграция 0.19.0 поверх БД со старой схемой polls (без closes_at/is_archived).

