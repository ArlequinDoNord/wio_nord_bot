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

Всего вызовов: **203**; таблиц: **30**.

| Таблица | Колонка | Тип / значение по умолчанию | db.py |
|---|---|---|---|
| `awards` | `achievement_key` | `TEXT DEFAULT NULL` | :1444 |
| `awards` | `achievement_level` | `INTEGER DEFAULT 0` | :1445 |
| `awards` | `bonus_attack` | `INTEGER DEFAULT 0` | :1423 |
| `awards` | `bonus_crit` | `INTEGER DEFAULT 0` | :1430 |
| `awards` | `bonus_defense` | `INTEGER DEFAULT 0` | :1424 |
| `awards` | `bonus_dodge` | `INTEGER DEFAULT 0` | :1425 |
| `awards` | `bonus_fishing` | `INTEGER DEFAULT 0` | :1426 |
| `awards` | `bonus_hp` | `INTEGER DEFAULT 0` | :1427 |
| `awards` | `bonus_json` | `TEXT DEFAULT '{}'` | :1446 |
| `awards` | `bonus_report_tax` | `INTEGER DEFAULT 0` | :1434 |
| `awards` | `bonus_shop_discount` | `INTEGER DEFAULT 0` | :1433 |
| `awards` | `image` | `TEXT` | :1422 |
| `awards` | `monthly_nm` | `INTEGER DEFAULT 0` | :1438 |
| `awards` | `reward_nm` | `INTEGER DEFAULT 0` | :1437 |
| `buildings` | `required_status` | `TEXT` | :1165 |
| `clan_buildings` | `building_photo_file_id` | `TEXT` | :1841 |
| `clan_members` | `role` | `TEXT NOT NULL DEFAULT 'member'` | :1167 |
| `clans` | `tree_amber_at` | `TEXT DEFAULT NULL` | :1493 |
| `dungeon_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1344 |
| `dungeon_enemies` | `admin_tuned` | `INTEGER DEFAULT 0` | :1382 |
| `dungeon_enemies` | `armor` | `INTEGER DEFAULT 0` | :1340 |
| `dungeon_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1625 |
| `dungeon_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1626 |
| `dungeon_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1342 |
| `dungeon_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1343 |
| `dungeon_enemies` | `damage_max` | `INTEGER DEFAULT 0` | :1339 |
| `dungeon_enemies` | `damage_min` | `INTEGER DEFAULT 0` | :1338 |
| `dungeon_enemies` | `description` | `TEXT` | :1336 |
| `dungeon_enemies` | `dodge` | `INTEGER DEFAULT 0` | :1337 |
| `dungeon_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1341 |
| `dungeon_enemies` | `drops` | `TEXT DEFAULT '[]'` | :1332 |
| `dungeon_enemies` | `effect_resist` | `TEXT DEFAULT NULL` | :1379 |
| `dungeon_enemies` | `frostbite_chance` | `INTEGER DEFAULT 0` | :1627 |
| `dungeon_enemies` | `image` | `TEXT` | :1333 |
| `dungeon_enemies` | `poison_chance` | `INTEGER DEFAULT 0` | :1334 |
| `dungeon_enemies` | `poison_dmg` | `INTEGER DEFAULT 0` | :1335 |
| `dungeons` | `is_training` | `INTEGER DEFAULT 0` | :1615 |
| `dungeons` | `photo_dawn` | `TEXT` | :1395 |
| `dungeons` | `photo_day` | `TEXT` | :1396 |
| `dungeons` | `photo_night` | `TEXT` | :1398 |
| `dungeons` | `photo_rope` | `TEXT` | :1401 |
| `dungeons` | `photo_sunset` | `TEXT` | :1397 |
| `dungeons` | `photo_water` | `TEXT` | :1400 |
| `dungeons` | `rooms_map` | `TEXT` | :1632 |
| `fire_lab_sessions` | `boss_encounters` | `INTEGER DEFAULT 0` | :1848 |
| `fire_lab_sessions` | `effects_json` | `TEXT DEFAULT NULL` | :1847 |
| `fire_lab_sessions` | `enemy_json` | `TEXT DEFAULT NULL` | :1846 |
| `fire_lab_sessions` | `fish_used` | `INTEGER DEFAULT 0` | :1849 |
| `fire_lab_sessions` | `last_active_at` | `TIMESTAMP` | :1855 |
| `fire_lab_sessions` | `tree_open` | `INTEGER DEFAULT 0` | :1853 |
| `fire_lab_sessions` | `well_open` | `INTEGER DEFAULT 0` | :1851 |
| `firelab_enemies` | `armor` | `INTEGER DEFAULT 0` | :1845 |
| `firelab_enemies` | `on_hit_effects` | `TEXT DEFAULT NULL` | :1844 |
| `fish_catches` | `expires_at` | `TIMESTAMP` | :1483 |
| `fish_catches` | `kind` | `TEXT DEFAULT 'fish'` | :1638 |
| `fishing_enemies` | `armor` | `INTEGER DEFAULT 0` | :1355 |
| `fishing_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1353 |
| `fishing_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1354 |
| `forest_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1349 |
| `forest_enemies` | `armor` | `INTEGER DEFAULT 0` | :1345 |
| `forest_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1351 |
| `forest_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1352 |
| `forest_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1347 |
| `forest_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1348 |
| `forest_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1346 |
| `forest_mushrooms` | `zone` | `TEXT DEFAULT 'clearing'` | :1535 |
| `housing_slots` | `embedded` | `INTEGER DEFAULT 0` | :1566 |
| `inventory` | `expires_at` | `TIMESTAMP` | :1478 |
| `inventory` | `plant_data` | `TEXT` | :1480 |
| `inventory` | `shop_qty` | `INTEGER DEFAULT 0` | :1674 |
| `items` | `armor` | `INTEGER DEFAULT 0` | :1198 |
| `items` | `crit_chance` | `INTEGER DEFAULT 0` | :1201 |
| `items` | `crit_mult` | `REAL DEFAULT 0` | :1202 |
| `items` | `cure_frostbite` | `INTEGER DEFAULT 0` | :1629 |
| `items` | `cure_poison` | `INTEGER DEFAULT 0` | :1383 |
| `items` | `damage` | `INTEGER DEFAULT 0` | :1330 |
| `items` | `dodge_bonus` | `INTEGER DEFAULT 0` | :1662 |
| `items` | `dodge_buff_pct` | `INTEGER DEFAULT 0` | :1666 |
| `items` | `drink_effect` | `TEXT DEFAULT NULL` | :1466 |
| `items` | `equip_slot` | `TEXT` | :1204 |
| `items` | `heal` | `INTEGER DEFAULT 0` | :1331 |
| `items` | `heal_bonus_pct` | `INTEGER DEFAULT 0` | :1661 |
| `items` | `housing_slots` | `INTEGER` | :1793 |
| `items` | `housing_type` | `TEXT` | :1792 |
| `items` | `loot_only` | `INTEGER DEFAULT 0` | :1798 |
| `items` | `market_ok` | `INTEGER DEFAULT 0` | :1635 |
| `items` | `plant_name` | `TEXT` | :1645 |
| `items` | `regen` | `INTEGER DEFAULT 0` | :1393 |
| `items` | `regen_turns` | `INTEGER DEFAULT 0` | :1665 |
| `items` | `required_status` | `TEXT` | :1164 |
| `items` | `restock_enabled` | `INTEGER DEFAULT 0` | :1669 |
| `items` | `restock_target` | `INTEGER DEFAULT 0` | :1670 |
| `items` | `shop_limit` | `INTEGER DEFAULT 0` | :1673 |
| `items` | `weapon_effect` | `TEXT` | :1656 |
| `items` | `weapon_effect_chance` | `INTEGER DEFAULT 0` | :1657 |
| `items` | `weapon_effect_dmg` | `INTEGER DEFAULT 0` | :1658 |
| `locations` | `clearing_photo` | `TEXT DEFAULT NULL` | :1521 |
| `locations` | `fire_photo` | `TEXT DEFAULT NULL` | :1519 |
| `locations` | `glade_photo` | `TEXT DEFAULT NULL` | :1520 |
| `locations` | `logging_photo` | `TEXT DEFAULT NULL` | :1530 |
| `locations` | `mine_level_photo` | `TEXT DEFAULT NULL` | :1524 |
| `locations` | `photo_dawn` | `TEXT` | :1385 |
| `locations` | `photo_day` | `TEXT` | :1386 |
| `locations` | `photo_night` | `TEXT` | :1388 |
| `locations` | `photo_sunset` | `TEXT` | :1387 |
| `locations` | `preview_photo` | `TEXT` | :1384 |
| `locations` | `season_photos` | `TEXT DEFAULT NULL` | :1516 |
| `locations` | `storage_photo` | `TEXT DEFAULT NULL` | :1526 |
| `locations` | `visits` | `INTEGER DEFAULT 0` | :1390 |
| `logging_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1370 |
| `logging_enemies` | `armor` | `INTEGER DEFAULT 0` | :1366 |
| `logging_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1368 |
| `logging_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1369 |
| `logging_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1367 |
| `market_fish` | `base_price` | `INTEGER DEFAULT 0` | :1618 |
| `market_items` | `qty` | `INTEGER DEFAULT 1` | :1621 |
| `mine_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1361 |
| `mine_enemies` | `armor` | `INTEGER DEFAULT 0` | :1357 |
| `mine_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1362 |
| `mine_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1363 |
| `mine_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1359 |
| `mine_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1360 |
| `mine_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1358 |
| `nii_reports` | `photo2_file_id` | `TEXT DEFAULT NULL` | :1448 |
| `player_dungeon_run` | `loot_nm` | `INTEGER DEFAULT 0` | :1317 |
| `player_dungeon_run` | `started_at` | `TIMESTAMP DEFAULT CURRENT_TIMESTAMP` | :1318 |
| `player_housing` | `expansions_installed` | `INTEGER DEFAULT 0` | :1568 |
| `player_housing` | `housing_label` | `TEXT` | :1794 |
| `player_housing` | `housing_slots` | `INTEGER` | :1795 |
| `player_housing` | `tax_last_check` | `TEXT DEFAULT NULL` | :1619 |
| `player_housing` | `tax_unpaid_months` | `INTEGER DEFAULT 0` | :1620 |
| `polls` | `archived_day` | `TEXT DEFAULT ''` | :1584 |
| `polls` | `closed_at` | `TIMESTAMP` | :1476 |
| `polls` | `closed_by` | `INTEGER` | :1475 |
| `polls` | `closes_at` | `TIMESTAMP` | :1573 |
| `polls` | `is_archived` | `INTEGER DEFAULT 0` | :1583 |
| `reports` | `credited_troops` | `INTEGER` | :1209 |
| `reports` | `paid` | `INTEGER DEFAULT 0` | :1216 |
| `reports` | `reject_reason` | `TEXT` | :1222 |
| `reports` | `reviewed_at` | `TEXT` | :1226 |
| `reports` | `reviewed_by_name` | `TEXT` | :1223 |
| `reports` | `total_troops` | `INTEGER DEFAULT 0` | :1207 |
| `statuses` | `sort_order` | `INTEGER DEFAULT 0` | :1166 |
| `users` | `about` | `TEXT DEFAULT ''` | :1192 |
| `users` | `alcohol_strong_used_day` | `TEXT DEFAULT NULL` | :1470 |
| `users` | `alcohol_strong_used_today` | `INTEGER DEFAULT 0` | :1469 |
| `users` | `alcohol_weak_used_day` | `TEXT DEFAULT NULL` | :1468 |
| `users` | `alcohol_weak_used_today` | `INTEGER DEFAULT 0` | :1467 |
| `users` | `ap_recovery_day` | `TEXT DEFAULT NULL` | :1462 |
| `users` | `ap_restored_day` | `TEXT DEFAULT NULL` | :1321 |
| `users` | `ap_restored_today` | `INTEGER DEFAULT 0` | :1322 |
| `users` | `beer_used_day` | `TEXT DEFAULT NULL` | :1465 |
| `users` | `beer_used_today` | `INTEGER DEFAULT 0` | :1464 |
| `users` | `callsign` | `TEXT` | :1408 |
| `users` | `callsign_free_used` | `INTEGER DEFAULT 0` | :1617 |
| `users` | `dodge_buff_pct` | `INTEGER DEFAULT 0` | :1689 |
| `users` | `dodge_buff_until` | `TEXT DEFAULT NULL` | :1688 |
| `users` | `duel_losses` | `INTEGER DEFAULT 0` | :1326 |
| `users` | `duel_rating` | `INTEGER DEFAULT 0` | :1324 |
| `users` | `duel_wins` | `INTEGER DEFAULT 0` | :1325 |
| `users` | `equipment` | `TEXT DEFAULT '{}'` | :1193 |
| `users` | `fish_sold_day` | `TEXT DEFAULT NULL` | :1497 |
| `users` | `fish_sold_today` | `INTEGER DEFAULT 0` | :1498 |
| `users` | `fishing_bait` | `TEXT DEFAULT ''` | :1406 |
| `users` | `forest_attempts_since_boar` | `INTEGER DEFAULT 0` | :1500 |
| `users` | `forest_attempts_since_wolf` | `INTEGER DEFAULT 0` | :1502 |
| `users` | `forest_sold_day` | `TEXT DEFAULT NULL` | :1512 |
| `users` | `forest_sold_today` | `INTEGER DEFAULT 0` | :1513 |
| `users` | `fountain_used_day` | `TEXT DEFAULT NULL` | :1485 |
| `users` | `fountain_used_today` | `INTEGER DEFAULT 0` | :1486 |
| `users` | `lang` | `TEXT DEFAULT 'ru'` | :1170 |
| `users` | `lantern_amber_at` | `TEXT DEFAULT NULL` | :1491 |
| `users` | `lantern_medit_day` | `TEXT DEFAULT NULL` | :1490 |
| `users` | `last_active` | `REAL DEFAULT 0` | :1329 |
| `users` | `last_salary_date` | `TIMESTAMP` | :1196 |
| `users` | `legioner` | `INTEGER DEFAULT 0` | :1735 |
| `users` | `logging_attempts_since_owl` | `INTEGER DEFAULT 0` | :1509 |
| `users` | `logging_attempts_since_snake` | `INTEGER DEFAULT 0` | :1508 |
| `users` | `market_license_expires` | `TEXT DEFAULT NULL` | :1616 |
| `users` | `mine_attempts_since_bat` | `INTEGER DEFAULT 0` | :1505 |
| `users` | `notify_enabled` | `INTEGER DEFAULT 1` | :1190 |
| `users` | `profile_public` | `INTEGER DEFAULT 1` | :1191 |
| `users` | `promoted_rank` | `TEXT` | :1169 |
| `users` | `salary` | `INTEGER DEFAULT 0` | :1194 |
| `users` | `salary_debt` | `INTEGER DEFAULT 0` | :1197 |
| `users` | `salary_period_days` | `INTEGER DEFAULT 7` | :1195 |
| `users` | `seaweed_used_day` | `TEXT DEFAULT NULL` | :1459 |
| `users` | `seaweed_used_today` | `INTEGER DEFAULT 0` | :1458 |
| `users` | `shower_used_day` | `TEXT DEFAULT NULL` | :1488 |
| `users` | `shower_used_today` | `INTEGER DEFAULT 0` | :1495 |
| `users` | `special_blocked_until` | `TEXT DEFAULT NULL` | :1473 |
| `users` | `special_fails_today` | `INTEGER DEFAULT 0` | :1472 |
| `users` | `wing` | `TEXT` | :1732 |
| `users` | `xp_balance` | `INTEGER DEFAULT 0` | :1174 |
| `water_fish` | `excluded` | `INTEGER DEFAULT 0` | :1404 |
| `water_fish` | `kind` | `TEXT DEFAULT 'fish'` | :1639 |
| `water_fish` | `super_rare` | `INTEGER DEFAULT 0` | :1642 |
| `wings` | `abbr` | `TEXT DEFAULT ''` | :1452 |
| `wings` | `callsign` | `TEXT DEFAULT ''` | :1454 |
| `wings` | `emoji` | `TEXT DEFAULT ''` | :1455 |
| `wings` | `name` | `TEXT DEFAULT ''` | :1453 |
| `wings` | `num` | `TEXT DEFAULT ''` | :1451 |
| `wings` | `sort_order` | `INTEGER DEFAULT 0` | :1456 |

## 2. Идемпотентные засевы и миграции данных

| Функция | Вызывается из main.py | Назначение (первая строка docstring) | db.py |
|---|---|---|---|
| `backfill_rank_statuses` | — | Разово выдать статусы по текущим званиям всех пилотов (войска и админ-звания). | :6708 |
| `ensure_achievements` | ✅ | Идемпотентно засевает награды-уровни достижений и синхронизирует их. | :14593 |
| `ensure_base_status` | — | Базовый статус «Турист» для каждого нового игрока. | :7091 |
| `ensure_base_statuses` | — | Создаёт базовые статусы иерархии, если их нет. | :7046 |
| `ensure_berry_candy_recipe` | — | Рецепт «Леденец из ягод»: черника + малина + сахар. Создаётся скрытым: | :10652 |
| `ensure_clan_building` | — | — | :16702 |
| `ensure_clan_cape_item` | — | Клановая накидка: экипировка слота «Клановая накидка». Продаётся в клановой | :10634 |
| `ensure_duel_items` | ✅ | Товары Дома Дуэлей: дуэльные перчатки (отдельный слот) и клубная карта. | :12136 |
| `ensure_dungeon_enemy_drops` | ✅ | Синхронизирует врагов существующего данжа с DEFAULT_DUNGEON (дропы, HP, награды, | :14043 |
| `ensure_dungeon_reservoir_items` | ✅ | Идемпотентно добавляет предметы водохранилища подземелья (v0.12.0). | :13966 |
| `ensure_dungeon_shop_items` | ✅ | Идемпотентно добавляет предметы данжа (зелье в магазин, трофеи) — для существующих БД. | :13574 |
| `ensure_fire_mushroom_pool` | — | Огненный гриб — на прогалину с весом 15; по 1 снимаем с пяти самых редких грибов. Один раз. | :10510 |
| `ensure_fire_tree_items` | — | Предметы пожертвования и талисмана: скрыты, без цены продажи, не на рынке. | :10443 |
| `ensure_firelab_enemies` | ✅ | Идемпотентно засевает врагов Огненного Лабиринта (4 обычных + босс). | :10757 |
| `ensure_firelab_items` | ✅ | Идемпотентно создаёт предметы Фазы 3 «Дней Пламенного Круговорота». | :10805 |
| `ensure_fishing_enemies` | ✅ | Идемпотентно засевает врагов рыбалки (мутировавший моллюск) из MOLLUSK_SEED. | :11079 |
| `ensure_forest_berry_items` | — | Ягоды (горсть) и шкура медведя: предметы-ресурсы вне магазина. Идемпотентно. | :10614 |
| `ensure_forest_berry_pool` | — | Таблица ягод поиска по зонам (как у грибов): шансы правит админ. Засев — один раз. | :10481 |
| `ensure_forest_enemies` | ✅ | Идемпотентно засевает врагов леса (кабан и Белый Волк Севера). | :10725 |
| `ensure_forest_items` | ✅ | Идемпотентно создаёт предметы леса (грибы, добыча кабана, жареные блюда, яд). | :9671 |
| `ensure_forest_mushrooms` | ✅ | Идемпотентно засевает пул грибов леса из FOREST_DEFAULTS. | :9843 |
| `ensure_forest_zones` | ✅ | Разовый перенос старого пула леса в зону поляны и засев пула опушки. | :10086 |
| `ensure_item_rarity_unified` | ✅ | Идемпотентно применяет единую градацию редкости (v0.43.10). | :2150 |
| `ensure_kvp_award` | ✅ | — | :12395 |
| `ensure_kvp_items` | ✅ | Обеспечивает эксклюзивный предмет К.В.П. — «Сержантскую трость». | :12109 |
| `ensure_kvp_user` | — | Гарантирует наличие строки прогресса К.В.П. для игрока. | :12582 |
| `ensure_life_items` | ✅ | Идемпотентно добавляет предметы жилья, мебели, семян, ресурсов и продовольствия. | :13790 |
| `ensure_logging_enemies` | ✅ | Идемпотентно засевает врагов Лесозаготовки (Змея и Неясыть). | :9832 |
| `ensure_logging_items` | ✅ | Идемпотентно создаёт предметы Лесозаготовки (топор, бревна, дропы). | :9789 |
| `ensure_market_license_item` | ✅ | Идемпотентно добавляет «Торговую лицензию» в магазин. | :11659 |
| `ensure_mine_enemies` | ✅ | Идемпотентно засевает врагов копи (Летучая мышь) из MINE_BAT_SEED. | :9780 |
| `ensure_mine_items` | ✅ | Идемпотентно создаёт предметы Железной копи (кирка, руда, самоцветы). | :9749 |
| `ensure_mollusk_items` | ✅ | Идемпотентно создаёт предметы моллюска (из его добычи и готового блюда). | :11085 |
| `ensure_player_housing` | — | Возвращает жильё игрока, создавая муниципальную квартиру для пилота при первом обращении. | :14188 |
| `ensure_rank_statuses_for_troops` | — | Выдать статус по текущему званию игрока (по войскам или админ-назначению). | :6696 |
| `ensure_recipe_shop_item` | — | Синхронизирует товар-рецепт «Рецепт: <name>» с рецептом (менеджер). | :15028 |
| `ensure_recipe_shop_items` | ✅ | Создаёт в магазине предметы-рецепты категории 'recipes'. | :16378 |
| `ensure_recipes` | ✅ | Идемпотентно засевает рецепты и синхронизирует уже существующие. | :14878 |
| `ensure_tourist_booklet` | ✅ | Создаёт предмет «Буклет туриста» и награду «Опытный турист», если их нет. | :12431 |
| `ensure_user_recipes_backfill` | ✅ | Разово открывает все рецепты существующим игрокам. | :16528 |
| `ensure_water_fish` | ✅ | Идемпотентно засевает water_fish из дефолтов. Правившие админом строки | :9181 |
| `migrate_legacy_junk` | ✅ | Переносит старые копии мусора (сапог, водоросли) из инвентаря в улов. | :9023 |
| `seed_default_items` | ✅ | Заполняет магазин базовым набором товаров, если он пуст и не было своих товаров. | :11832 |
| `seed_dungeon` | ✅ | — | :11987 |
| `seed_kvp` | ✅ | Создаёт тренировочный данж К.В.П. с врагами (Ефрейтор, Старший сержант), если его нет. | :12058 |
| `seed_locations` | — | Засеивает базовые локации города (Ратуша, Библиотека) как пример управляемого доступа. | :1945 |

## 3. Отдельные скрипты миграций

- `migrate_113.py` — Проверка миграций 0.19.0 на чистой БД: колонки polls, таблица rep_speeches.
- `migrate_113_old.py` — Миграция 0.19.0 поверх БД со старой схемой polls (без closes_at/is_archived).

