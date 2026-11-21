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
| `awards` | `achievement_key` | `TEXT DEFAULT NULL` | :1442 |
| `awards` | `achievement_level` | `INTEGER DEFAULT 0` | :1443 |
| `awards` | `bonus_attack` | `INTEGER DEFAULT 0` | :1421 |
| `awards` | `bonus_crit` | `INTEGER DEFAULT 0` | :1428 |
| `awards` | `bonus_defense` | `INTEGER DEFAULT 0` | :1422 |
| `awards` | `bonus_dodge` | `INTEGER DEFAULT 0` | :1423 |
| `awards` | `bonus_fishing` | `INTEGER DEFAULT 0` | :1424 |
| `awards` | `bonus_hp` | `INTEGER DEFAULT 0` | :1425 |
| `awards` | `bonus_json` | `TEXT DEFAULT '{}'` | :1444 |
| `awards` | `bonus_report_tax` | `INTEGER DEFAULT 0` | :1432 |
| `awards` | `bonus_shop_discount` | `INTEGER DEFAULT 0` | :1431 |
| `awards` | `image` | `TEXT` | :1420 |
| `awards` | `monthly_nm` | `INTEGER DEFAULT 0` | :1436 |
| `awards` | `reward_nm` | `INTEGER DEFAULT 0` | :1435 |
| `buildings` | `required_status` | `TEXT` | :1163 |
| `clan_buildings` | `building_photo_file_id` | `TEXT` | :1839 |
| `clan_members` | `role` | `TEXT NOT NULL DEFAULT 'member'` | :1165 |
| `clans` | `tree_amber_at` | `TEXT DEFAULT NULL` | :1491 |
| `dungeon_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1342 |
| `dungeon_enemies` | `admin_tuned` | `INTEGER DEFAULT 0` | :1380 |
| `dungeon_enemies` | `armor` | `INTEGER DEFAULT 0` | :1338 |
| `dungeon_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1623 |
| `dungeon_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1624 |
| `dungeon_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1340 |
| `dungeon_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1341 |
| `dungeon_enemies` | `damage_max` | `INTEGER DEFAULT 0` | :1337 |
| `dungeon_enemies` | `damage_min` | `INTEGER DEFAULT 0` | :1336 |
| `dungeon_enemies` | `description` | `TEXT` | :1334 |
| `dungeon_enemies` | `dodge` | `INTEGER DEFAULT 0` | :1335 |
| `dungeon_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1339 |
| `dungeon_enemies` | `drops` | `TEXT DEFAULT '[]'` | :1330 |
| `dungeon_enemies` | `effect_resist` | `TEXT DEFAULT NULL` | :1377 |
| `dungeon_enemies` | `frostbite_chance` | `INTEGER DEFAULT 0` | :1625 |
| `dungeon_enemies` | `image` | `TEXT` | :1331 |
| `dungeon_enemies` | `poison_chance` | `INTEGER DEFAULT 0` | :1332 |
| `dungeon_enemies` | `poison_dmg` | `INTEGER DEFAULT 0` | :1333 |
| `dungeons` | `is_training` | `INTEGER DEFAULT 0` | :1613 |
| `dungeons` | `photo_dawn` | `TEXT` | :1393 |
| `dungeons` | `photo_day` | `TEXT` | :1394 |
| `dungeons` | `photo_night` | `TEXT` | :1396 |
| `dungeons` | `photo_rope` | `TEXT` | :1399 |
| `dungeons` | `photo_sunset` | `TEXT` | :1395 |
| `dungeons` | `photo_water` | `TEXT` | :1398 |
| `dungeons` | `rooms_map` | `TEXT` | :1630 |
| `fire_lab_sessions` | `boss_encounters` | `INTEGER DEFAULT 0` | :1846 |
| `fire_lab_sessions` | `effects_json` | `TEXT DEFAULT NULL` | :1845 |
| `fire_lab_sessions` | `enemy_json` | `TEXT DEFAULT NULL` | :1844 |
| `fire_lab_sessions` | `fish_used` | `INTEGER DEFAULT 0` | :1847 |
| `fire_lab_sessions` | `last_active_at` | `TIMESTAMP` | :1853 |
| `fire_lab_sessions` | `tree_open` | `INTEGER DEFAULT 0` | :1851 |
| `fire_lab_sessions` | `well_open` | `INTEGER DEFAULT 0` | :1849 |
| `firelab_enemies` | `armor` | `INTEGER DEFAULT 0` | :1843 |
| `firelab_enemies` | `on_hit_effects` | `TEXT DEFAULT NULL` | :1842 |
| `fish_catches` | `expires_at` | `TIMESTAMP` | :1481 |
| `fish_catches` | `kind` | `TEXT DEFAULT 'fish'` | :1636 |
| `fishing_enemies` | `armor` | `INTEGER DEFAULT 0` | :1353 |
| `fishing_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1351 |
| `fishing_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1352 |
| `forest_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1347 |
| `forest_enemies` | `armor` | `INTEGER DEFAULT 0` | :1343 |
| `forest_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1349 |
| `forest_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1350 |
| `forest_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1345 |
| `forest_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1346 |
| `forest_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1344 |
| `forest_mushrooms` | `zone` | `TEXT DEFAULT 'clearing'` | :1533 |
| `housing_slots` | `embedded` | `INTEGER DEFAULT 0` | :1564 |
| `inventory` | `expires_at` | `TIMESTAMP` | :1476 |
| `inventory` | `plant_data` | `TEXT` | :1478 |
| `inventory` | `shop_qty` | `INTEGER DEFAULT 0` | :1672 |
| `items` | `armor` | `INTEGER DEFAULT 0` | :1196 |
| `items` | `crit_chance` | `INTEGER DEFAULT 0` | :1199 |
| `items` | `crit_mult` | `REAL DEFAULT 0` | :1200 |
| `items` | `cure_frostbite` | `INTEGER DEFAULT 0` | :1627 |
| `items` | `cure_poison` | `INTEGER DEFAULT 0` | :1381 |
| `items` | `damage` | `INTEGER DEFAULT 0` | :1328 |
| `items` | `dodge_bonus` | `INTEGER DEFAULT 0` | :1660 |
| `items` | `dodge_buff_pct` | `INTEGER DEFAULT 0` | :1664 |
| `items` | `drink_effect` | `TEXT DEFAULT NULL` | :1464 |
| `items` | `equip_slot` | `TEXT` | :1202 |
| `items` | `heal` | `INTEGER DEFAULT 0` | :1329 |
| `items` | `heal_bonus_pct` | `INTEGER DEFAULT 0` | :1659 |
| `items` | `housing_slots` | `INTEGER` | :1791 |
| `items` | `housing_type` | `TEXT` | :1790 |
| `items` | `loot_only` | `INTEGER DEFAULT 0` | :1796 |
| `items` | `market_ok` | `INTEGER DEFAULT 0` | :1633 |
| `items` | `plant_name` | `TEXT` | :1643 |
| `items` | `regen` | `INTEGER DEFAULT 0` | :1391 |
| `items` | `regen_turns` | `INTEGER DEFAULT 0` | :1663 |
| `items` | `required_status` | `TEXT` | :1162 |
| `items` | `restock_enabled` | `INTEGER DEFAULT 0` | :1667 |
| `items` | `restock_target` | `INTEGER DEFAULT 0` | :1668 |
| `items` | `shop_limit` | `INTEGER DEFAULT 0` | :1671 |
| `items` | `weapon_effect` | `TEXT` | :1654 |
| `items` | `weapon_effect_chance` | `INTEGER DEFAULT 0` | :1655 |
| `items` | `weapon_effect_dmg` | `INTEGER DEFAULT 0` | :1656 |
| `locations` | `clearing_photo` | `TEXT DEFAULT NULL` | :1519 |
| `locations` | `fire_photo` | `TEXT DEFAULT NULL` | :1517 |
| `locations` | `glade_photo` | `TEXT DEFAULT NULL` | :1518 |
| `locations` | `logging_photo` | `TEXT DEFAULT NULL` | :1528 |
| `locations` | `mine_level_photo` | `TEXT DEFAULT NULL` | :1522 |
| `locations` | `photo_dawn` | `TEXT` | :1383 |
| `locations` | `photo_day` | `TEXT` | :1384 |
| `locations` | `photo_night` | `TEXT` | :1386 |
| `locations` | `photo_sunset` | `TEXT` | :1385 |
| `locations` | `preview_photo` | `TEXT` | :1382 |
| `locations` | `season_photos` | `TEXT DEFAULT NULL` | :1514 |
| `locations` | `storage_photo` | `TEXT DEFAULT NULL` | :1524 |
| `locations` | `visits` | `INTEGER DEFAULT 0` | :1388 |
| `logging_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1368 |
| `logging_enemies` | `armor` | `INTEGER DEFAULT 0` | :1364 |
| `logging_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1366 |
| `logging_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1367 |
| `logging_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1365 |
| `market_fish` | `base_price` | `INTEGER DEFAULT 0` | :1616 |
| `market_items` | `qty` | `INTEGER DEFAULT 1` | :1619 |
| `mine_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1359 |
| `mine_enemies` | `armor` | `INTEGER DEFAULT 0` | :1355 |
| `mine_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1360 |
| `mine_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1361 |
| `mine_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1357 |
| `mine_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1358 |
| `mine_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1356 |
| `nii_reports` | `photo2_file_id` | `TEXT DEFAULT NULL` | :1446 |
| `player_dungeon_run` | `loot_nm` | `INTEGER DEFAULT 0` | :1315 |
| `player_dungeon_run` | `started_at` | `TIMESTAMP DEFAULT CURRENT_TIMESTAMP` | :1316 |
| `player_housing` | `expansions_installed` | `INTEGER DEFAULT 0` | :1566 |
| `player_housing` | `housing_label` | `TEXT` | :1792 |
| `player_housing` | `housing_slots` | `INTEGER` | :1793 |
| `player_housing` | `tax_last_check` | `TEXT DEFAULT NULL` | :1617 |
| `player_housing` | `tax_unpaid_months` | `INTEGER DEFAULT 0` | :1618 |
| `polls` | `archived_day` | `TEXT DEFAULT ''` | :1582 |
| `polls` | `closed_at` | `TIMESTAMP` | :1474 |
| `polls` | `closed_by` | `INTEGER` | :1473 |
| `polls` | `closes_at` | `TIMESTAMP` | :1571 |
| `polls` | `is_archived` | `INTEGER DEFAULT 0` | :1581 |
| `reports` | `credited_troops` | `INTEGER` | :1207 |
| `reports` | `paid` | `INTEGER DEFAULT 0` | :1214 |
| `reports` | `reject_reason` | `TEXT` | :1220 |
| `reports` | `reviewed_at` | `TEXT` | :1224 |
| `reports` | `reviewed_by_name` | `TEXT` | :1221 |
| `reports` | `total_troops` | `INTEGER DEFAULT 0` | :1205 |
| `statuses` | `sort_order` | `INTEGER DEFAULT 0` | :1164 |
| `users` | `about` | `TEXT DEFAULT ''` | :1190 |
| `users` | `alcohol_strong_used_day` | `TEXT DEFAULT NULL` | :1468 |
| `users` | `alcohol_strong_used_today` | `INTEGER DEFAULT 0` | :1467 |
| `users` | `alcohol_weak_used_day` | `TEXT DEFAULT NULL` | :1466 |
| `users` | `alcohol_weak_used_today` | `INTEGER DEFAULT 0` | :1465 |
| `users` | `ap_recovery_day` | `TEXT DEFAULT NULL` | :1460 |
| `users` | `ap_restored_day` | `TEXT DEFAULT NULL` | :1319 |
| `users` | `ap_restored_today` | `INTEGER DEFAULT 0` | :1320 |
| `users` | `beer_used_day` | `TEXT DEFAULT NULL` | :1463 |
| `users` | `beer_used_today` | `INTEGER DEFAULT 0` | :1462 |
| `users` | `callsign` | `TEXT` | :1406 |
| `users` | `callsign_free_used` | `INTEGER DEFAULT 0` | :1615 |
| `users` | `dodge_buff_pct` | `INTEGER DEFAULT 0` | :1687 |
| `users` | `dodge_buff_until` | `TEXT DEFAULT NULL` | :1686 |
| `users` | `duel_losses` | `INTEGER DEFAULT 0` | :1324 |
| `users` | `duel_rating` | `INTEGER DEFAULT 0` | :1322 |
| `users` | `duel_wins` | `INTEGER DEFAULT 0` | :1323 |
| `users` | `equipment` | `TEXT DEFAULT '{}'` | :1191 |
| `users` | `fish_sold_day` | `TEXT DEFAULT NULL` | :1495 |
| `users` | `fish_sold_today` | `INTEGER DEFAULT 0` | :1496 |
| `users` | `fishing_bait` | `TEXT DEFAULT ''` | :1404 |
| `users` | `forest_attempts_since_boar` | `INTEGER DEFAULT 0` | :1498 |
| `users` | `forest_attempts_since_wolf` | `INTEGER DEFAULT 0` | :1500 |
| `users` | `forest_sold_day` | `TEXT DEFAULT NULL` | :1510 |
| `users` | `forest_sold_today` | `INTEGER DEFAULT 0` | :1511 |
| `users` | `fountain_used_day` | `TEXT DEFAULT NULL` | :1483 |
| `users` | `fountain_used_today` | `INTEGER DEFAULT 0` | :1484 |
| `users` | `lang` | `TEXT DEFAULT 'ru'` | :1168 |
| `users` | `lantern_amber_at` | `TEXT DEFAULT NULL` | :1489 |
| `users` | `lantern_medit_day` | `TEXT DEFAULT NULL` | :1488 |
| `users` | `last_active` | `REAL DEFAULT 0` | :1327 |
| `users` | `last_salary_date` | `TIMESTAMP` | :1194 |
| `users` | `legioner` | `INTEGER DEFAULT 0` | :1733 |
| `users` | `logging_attempts_since_owl` | `INTEGER DEFAULT 0` | :1507 |
| `users` | `logging_attempts_since_snake` | `INTEGER DEFAULT 0` | :1506 |
| `users` | `market_license_expires` | `TEXT DEFAULT NULL` | :1614 |
| `users` | `mine_attempts_since_bat` | `INTEGER DEFAULT 0` | :1503 |
| `users` | `notify_enabled` | `INTEGER DEFAULT 1` | :1188 |
| `users` | `profile_public` | `INTEGER DEFAULT 1` | :1189 |
| `users` | `promoted_rank` | `TEXT` | :1167 |
| `users` | `salary` | `INTEGER DEFAULT 0` | :1192 |
| `users` | `salary_debt` | `INTEGER DEFAULT 0` | :1195 |
| `users` | `salary_period_days` | `INTEGER DEFAULT 7` | :1193 |
| `users` | `seaweed_used_day` | `TEXT DEFAULT NULL` | :1457 |
| `users` | `seaweed_used_today` | `INTEGER DEFAULT 0` | :1456 |
| `users` | `shower_used_day` | `TEXT DEFAULT NULL` | :1486 |
| `users` | `shower_used_today` | `INTEGER DEFAULT 0` | :1493 |
| `users` | `special_blocked_until` | `TEXT DEFAULT NULL` | :1471 |
| `users` | `special_fails_today` | `INTEGER DEFAULT 0` | :1470 |
| `users` | `wing` | `TEXT` | :1730 |
| `users` | `xp_balance` | `INTEGER DEFAULT 0` | :1172 |
| `water_fish` | `excluded` | `INTEGER DEFAULT 0` | :1402 |
| `water_fish` | `kind` | `TEXT DEFAULT 'fish'` | :1637 |
| `water_fish` | `super_rare` | `INTEGER DEFAULT 0` | :1640 |
| `wings` | `abbr` | `TEXT DEFAULT ''` | :1450 |
| `wings` | `callsign` | `TEXT DEFAULT ''` | :1452 |
| `wings` | `emoji` | `TEXT DEFAULT ''` | :1453 |
| `wings` | `name` | `TEXT DEFAULT ''` | :1451 |
| `wings` | `num` | `TEXT DEFAULT ''` | :1449 |
| `wings` | `sort_order` | `INTEGER DEFAULT 0` | :1454 |

## 2. Идемпотентные засевы и миграции данных

| Функция | Вызывается из main.py | Назначение (первая строка docstring) | db.py |
|---|---|---|---|
| `backfill_rank_statuses` | — | Разово выдать статусы по текущим званиям всех пилотов (войска и админ-звания). | :6704 |
| `ensure_achievements` | ✅ | Идемпотентно засевает награды-уровни достижений и синхронизирует их. | :14589 |
| `ensure_base_status` | — | Базовый статус «Турист» для каждого нового игрока. | :7087 |
| `ensure_base_statuses` | — | Создаёт базовые статусы иерархии, если их нет. | :7042 |
| `ensure_berry_candy_recipe` | — | Рецепт «Леденец из ягод»: черника + малина + сахар. Создаётся скрытым: | :10648 |
| `ensure_clan_building` | — | — | :16698 |
| `ensure_clan_cape_item` | — | Клановая накидка: экипировка слота «Клановая накидка». Продаётся в клановой | :10630 |
| `ensure_duel_items` | ✅ | Товары Дома Дуэлей: дуэльные перчатки (отдельный слот) и клубная карта. | :12132 |
| `ensure_dungeon_enemy_drops` | ✅ | Синхронизирует врагов существующего данжа с DEFAULT_DUNGEON (дропы, HP, награды, | :14039 |
| `ensure_dungeon_reservoir_items` | ✅ | Идемпотентно добавляет предметы водохранилища подземелья (v0.12.0). | :13962 |
| `ensure_dungeon_shop_items` | ✅ | Идемпотентно добавляет предметы данжа (зелье в магазин, трофеи) — для существующих БД. | :13570 |
| `ensure_fire_mushroom_pool` | — | Огненный гриб — на прогалину с весом 15; по 1 снимаем с пяти самых редких грибов. Один раз. | :10506 |
| `ensure_fire_tree_items` | — | Предметы пожертвования и талисмана: скрыты, без цены продажи, не на рынке. | :10439 |
| `ensure_firelab_enemies` | ✅ | Идемпотентно засевает врагов Огненного Лабиринта (4 обычных + босс). | :10753 |
| `ensure_firelab_items` | ✅ | Идемпотентно создаёт предметы Фазы 3 «Дней Пламенного Круговорота». | :10801 |
| `ensure_fishing_enemies` | ✅ | Идемпотентно засевает врагов рыбалки (мутировавший моллюск) из MOLLUSK_SEED. | :11075 |
| `ensure_forest_berry_items` | — | Ягоды (горсть) и шкура медведя: предметы-ресурсы вне магазина. Идемпотентно. | :10610 |
| `ensure_forest_berry_pool` | — | Таблица ягод поиска по зонам (как у грибов): шансы правит админ. Засев — один раз. | :10477 |
| `ensure_forest_enemies` | ✅ | Идемпотентно засевает врагов леса (кабан и Белый Волк Севера). | :10721 |
| `ensure_forest_items` | ✅ | Идемпотентно создаёт предметы леса (грибы, добыча кабана, жареные блюда, яд). | :9667 |
| `ensure_forest_mushrooms` | ✅ | Идемпотентно засевает пул грибов леса из FOREST_DEFAULTS. | :9839 |
| `ensure_forest_zones` | ✅ | Разовый перенос старого пула леса в зону поляны и засев пула опушки. | :10082 |
| `ensure_item_rarity_unified` | ✅ | Идемпотентно применяет единую градацию редкости (v0.43.10). | :2148 |
| `ensure_kvp_award` | ✅ | — | :12391 |
| `ensure_kvp_items` | ✅ | Обеспечивает эксклюзивный предмет К.В.П. — «Сержантскую трость». | :12105 |
| `ensure_kvp_user` | — | Гарантирует наличие строки прогресса К.В.П. для игрока. | :12578 |
| `ensure_life_items` | ✅ | Идемпотентно добавляет предметы жилья, мебели, семян, ресурсов и продовольствия. | :13786 |
| `ensure_logging_enemies` | ✅ | Идемпотентно засевает врагов Лесозаготовки (Змея и Неясыть). | :9828 |
| `ensure_logging_items` | ✅ | Идемпотентно создаёт предметы Лесозаготовки (топор, бревна, дропы). | :9785 |
| `ensure_market_license_item` | ✅ | Идемпотентно добавляет «Торговую лицензию» в магазин. | :11655 |
| `ensure_mine_enemies` | ✅ | Идемпотентно засевает врагов копи (Летучая мышь) из MINE_BAT_SEED. | :9776 |
| `ensure_mine_items` | ✅ | Идемпотентно создаёт предметы Железной копи (кирка, руда, самоцветы). | :9745 |
| `ensure_mollusk_items` | ✅ | Идемпотентно создаёт предметы моллюска (из его добычи и готового блюда). | :11081 |
| `ensure_player_housing` | — | Возвращает жильё игрока, создавая муниципальную квартиру для пилота при первом обращении. | :14184 |
| `ensure_rank_statuses_for_troops` | — | Выдать статус по текущему званию игрока (по войскам или админ-назначению). | :6692 |
| `ensure_recipe_shop_item` | — | Синхронизирует товар-рецепт «Рецепт: <name>» с рецептом (менеджер). | :15024 |
| `ensure_recipe_shop_items` | ✅ | Создаёт в магазине предметы-рецепты категории 'recipes'. | :16374 |
| `ensure_recipes` | ✅ | Идемпотентно засевает рецепты и синхронизирует уже существующие. | :14874 |
| `ensure_tourist_booklet` | ✅ | Создаёт предмет «Буклет туриста» и награду «Опытный турист», если их нет. | :12427 |
| `ensure_user_recipes_backfill` | ✅ | Разово открывает все рецепты существующим игрокам. | :16524 |
| `ensure_water_fish` | ✅ | Идемпотентно засевает water_fish из дефолтов. Правившие админом строки | :9177 |
| `migrate_legacy_junk` | ✅ | Переносит старые копии мусора (сапог, водоросли) из инвентаря в улов. | :9019 |
| `seed_default_items` | ✅ | Заполняет магазин базовым набором товаров, если он пуст и не было своих товаров. | :11828 |
| `seed_dungeon` | ✅ | — | :11983 |
| `seed_kvp` | ✅ | Создаёт тренировочный данж К.В.П. с врагами (Ефрейтор, Старший сержант), если его нет. | :12054 |
| `seed_locations` | — | Засеивает базовые локации города (Ратуша, Библиотека) как пример управляемого доступа. | :1943 |

## 3. Отдельные скрипты миграций

- `migrate_113.py` — Проверка миграций 0.19.0 на чистой БД: колонки polls, таблица rep_speeches.
- `migrate_113_old.py` — Миграция 0.19.0 поверх БД со старой схемой polls (без closes_at/is_archived).

