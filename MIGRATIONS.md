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
| `awards` | `achievement_key` | `TEXT DEFAULT NULL` | :1481 |
| `awards` | `achievement_level` | `INTEGER DEFAULT 0` | :1482 |
| `awards` | `bonus_attack` | `INTEGER DEFAULT 0` | :1460 |
| `awards` | `bonus_crit` | `INTEGER DEFAULT 0` | :1467 |
| `awards` | `bonus_defense` | `INTEGER DEFAULT 0` | :1461 |
| `awards` | `bonus_dodge` | `INTEGER DEFAULT 0` | :1462 |
| `awards` | `bonus_fishing` | `INTEGER DEFAULT 0` | :1463 |
| `awards` | `bonus_hp` | `INTEGER DEFAULT 0` | :1464 |
| `awards` | `bonus_json` | `TEXT DEFAULT '{}'` | :1483 |
| `awards` | `bonus_report_tax` | `INTEGER DEFAULT 0` | :1471 |
| `awards` | `bonus_shop_discount` | `INTEGER DEFAULT 0` | :1470 |
| `awards` | `image` | `TEXT` | :1459 |
| `awards` | `monthly_nm` | `INTEGER DEFAULT 0` | :1475 |
| `awards` | `reward_nm` | `INTEGER DEFAULT 0` | :1474 |
| `buildings` | `required_status` | `TEXT` | :1202 |
| `clan_buildings` | `building_photo_file_id` | `TEXT` | :1882 |
| `clan_members` | `role` | `TEXT NOT NULL DEFAULT 'member'` | :1204 |
| `clans` | `tree_amber_at` | `TEXT DEFAULT NULL` | :1530 |
| `dungeon_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1381 |
| `dungeon_enemies` | `admin_tuned` | `INTEGER DEFAULT 0` | :1419 |
| `dungeon_enemies` | `armor` | `INTEGER DEFAULT 0` | :1377 |
| `dungeon_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1662 |
| `dungeon_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1663 |
| `dungeon_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1379 |
| `dungeon_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1380 |
| `dungeon_enemies` | `damage_max` | `INTEGER DEFAULT 0` | :1376 |
| `dungeon_enemies` | `damage_min` | `INTEGER DEFAULT 0` | :1375 |
| `dungeon_enemies` | `description` | `TEXT` | :1373 |
| `dungeon_enemies` | `dodge` | `INTEGER DEFAULT 0` | :1374 |
| `dungeon_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1378 |
| `dungeon_enemies` | `drops` | `TEXT DEFAULT '[]'` | :1369 |
| `dungeon_enemies` | `effect_resist` | `TEXT DEFAULT NULL` | :1416 |
| `dungeon_enemies` | `frostbite_chance` | `INTEGER DEFAULT 0` | :1664 |
| `dungeon_enemies` | `image` | `TEXT` | :1370 |
| `dungeon_enemies` | `poison_chance` | `INTEGER DEFAULT 0` | :1371 |
| `dungeon_enemies` | `poison_dmg` | `INTEGER DEFAULT 0` | :1372 |
| `dungeons` | `is_training` | `INTEGER DEFAULT 0` | :1652 |
| `dungeons` | `photo_dawn` | `TEXT` | :1432 |
| `dungeons` | `photo_day` | `TEXT` | :1433 |
| `dungeons` | `photo_night` | `TEXT` | :1435 |
| `dungeons` | `photo_rope` | `TEXT` | :1438 |
| `dungeons` | `photo_sunset` | `TEXT` | :1434 |
| `dungeons` | `photo_water` | `TEXT` | :1437 |
| `dungeons` | `rooms_map` | `TEXT` | :1669 |
| `fire_lab_sessions` | `boss_encounters` | `INTEGER DEFAULT 0` | :1889 |
| `fire_lab_sessions` | `effects_json` | `TEXT DEFAULT NULL` | :1888 |
| `fire_lab_sessions` | `enemy_json` | `TEXT DEFAULT NULL` | :1887 |
| `fire_lab_sessions` | `fish_used` | `INTEGER DEFAULT 0` | :1890 |
| `fire_lab_sessions` | `last_active_at` | `TIMESTAMP` | :1896 |
| `fire_lab_sessions` | `tree_open` | `INTEGER DEFAULT 0` | :1894 |
| `fire_lab_sessions` | `well_open` | `INTEGER DEFAULT 0` | :1892 |
| `firelab_enemies` | `armor` | `INTEGER DEFAULT 0` | :1886 |
| `firelab_enemies` | `on_hit_effects` | `TEXT DEFAULT NULL` | :1885 |
| `fish_catches` | `expires_at` | `TIMESTAMP` | :1520 |
| `fish_catches` | `kind` | `TEXT DEFAULT 'fish'` | :1675 |
| `fishing_enemies` | `armor` | `INTEGER DEFAULT 0` | :1392 |
| `fishing_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1390 |
| `fishing_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1391 |
| `forest_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1386 |
| `forest_enemies` | `armor` | `INTEGER DEFAULT 0` | :1382 |
| `forest_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1388 |
| `forest_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1389 |
| `forest_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1384 |
| `forest_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1385 |
| `forest_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1383 |
| `forest_mushrooms` | `zone` | `TEXT DEFAULT 'clearing'` | :1572 |
| `housing_slots` | `embedded` | `INTEGER DEFAULT 0` | :1603 |
| `inventory` | `expires_at` | `TIMESTAMP` | :1515 |
| `inventory` | `plant_data` | `TEXT` | :1517 |
| `inventory` | `shop_qty` | `INTEGER DEFAULT 0` | :1711 |
| `items` | `armor` | `INTEGER DEFAULT 0` | :1235 |
| `items` | `crit_chance` | `INTEGER DEFAULT 0` | :1238 |
| `items` | `crit_mult` | `REAL DEFAULT 0` | :1239 |
| `items` | `cure_frostbite` | `INTEGER DEFAULT 0` | :1666 |
| `items` | `cure_poison` | `INTEGER DEFAULT 0` | :1420 |
| `items` | `damage` | `INTEGER DEFAULT 0` | :1367 |
| `items` | `dodge_bonus` | `INTEGER DEFAULT 0` | :1699 |
| `items` | `dodge_buff_pct` | `INTEGER DEFAULT 0` | :1703 |
| `items` | `drink_effect` | `TEXT DEFAULT NULL` | :1503 |
| `items` | `equip_slot` | `TEXT` | :1241 |
| `items` | `heal` | `INTEGER DEFAULT 0` | :1368 |
| `items` | `heal_bonus_pct` | `INTEGER DEFAULT 0` | :1698 |
| `items` | `housing_slots` | `INTEGER` | :1830 |
| `items` | `housing_type` | `TEXT` | :1829 |
| `items` | `loot_only` | `INTEGER DEFAULT 0` | :1835 |
| `items` | `market_ok` | `INTEGER DEFAULT 0` | :1672 |
| `items` | `plant_name` | `TEXT` | :1682 |
| `items` | `regen` | `INTEGER DEFAULT 0` | :1430 |
| `items` | `regen_turns` | `INTEGER DEFAULT 0` | :1702 |
| `items` | `required_status` | `TEXT` | :1201 |
| `items` | `restock_enabled` | `INTEGER DEFAULT 0` | :1706 |
| `items` | `restock_target` | `INTEGER DEFAULT 0` | :1707 |
| `items` | `shop_limit` | `INTEGER DEFAULT 0` | :1710 |
| `items` | `weapon_effect` | `TEXT` | :1693 |
| `items` | `weapon_effect_chance` | `INTEGER DEFAULT 0` | :1694 |
| `items` | `weapon_effect_dmg` | `INTEGER DEFAULT 0` | :1695 |
| `locations` | `clearing_photo` | `TEXT DEFAULT NULL` | :1558 |
| `locations` | `fire_photo` | `TEXT DEFAULT NULL` | :1556 |
| `locations` | `glade_photo` | `TEXT DEFAULT NULL` | :1557 |
| `locations` | `logging_photo` | `TEXT DEFAULT NULL` | :1567 |
| `locations` | `mine_level_photo` | `TEXT DEFAULT NULL` | :1561 |
| `locations` | `photo_dawn` | `TEXT` | :1422 |
| `locations` | `photo_day` | `TEXT` | :1423 |
| `locations` | `photo_night` | `TEXT` | :1425 |
| `locations` | `photo_sunset` | `TEXT` | :1424 |
| `locations` | `preview_photo` | `TEXT` | :1421 |
| `locations` | `season_photos` | `TEXT DEFAULT NULL` | :1553 |
| `locations` | `storage_photo` | `TEXT DEFAULT NULL` | :1563 |
| `locations` | `visits` | `INTEGER DEFAULT 0` | :1427 |
| `logging_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1407 |
| `logging_enemies` | `armor` | `INTEGER DEFAULT 0` | :1403 |
| `logging_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1405 |
| `logging_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1406 |
| `logging_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1404 |
| `market_fish` | `base_price` | `INTEGER DEFAULT 0` | :1655 |
| `market_items` | `qty` | `INTEGER DEFAULT 1` | :1658 |
| `mine_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1398 |
| `mine_enemies` | `armor` | `INTEGER DEFAULT 0` | :1394 |
| `mine_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1399 |
| `mine_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1400 |
| `mine_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1396 |
| `mine_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1397 |
| `mine_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1395 |
| `nii_reports` | `photo2_file_id` | `TEXT DEFAULT NULL` | :1485 |
| `player_dungeon_run` | `loot_nm` | `INTEGER DEFAULT 0` | :1354 |
| `player_dungeon_run` | `started_at` | `TIMESTAMP DEFAULT CURRENT_TIMESTAMP` | :1355 |
| `player_housing` | `expansions_installed` | `INTEGER DEFAULT 0` | :1605 |
| `player_housing` | `housing_label` | `TEXT` | :1831 |
| `player_housing` | `housing_slots` | `INTEGER` | :1832 |
| `player_housing` | `tax_last_check` | `TEXT DEFAULT NULL` | :1656 |
| `player_housing` | `tax_unpaid_months` | `INTEGER DEFAULT 0` | :1657 |
| `polls` | `archived_day` | `TEXT DEFAULT ''` | :1621 |
| `polls` | `closed_at` | `TIMESTAMP` | :1513 |
| `polls` | `closed_by` | `INTEGER` | :1512 |
| `polls` | `closes_at` | `TIMESTAMP` | :1610 |
| `polls` | `is_archived` | `INTEGER DEFAULT 0` | :1620 |
| `reports` | `credited_troops` | `INTEGER` | :1246 |
| `reports` | `paid` | `INTEGER DEFAULT 0` | :1253 |
| `reports` | `reject_reason` | `TEXT` | :1259 |
| `reports` | `reviewed_at` | `TEXT` | :1263 |
| `reports` | `reviewed_by_name` | `TEXT` | :1260 |
| `reports` | `total_troops` | `INTEGER DEFAULT 0` | :1244 |
| `statuses` | `sort_order` | `INTEGER DEFAULT 0` | :1203 |
| `users` | `about` | `TEXT DEFAULT ''` | :1229 |
| `users` | `alcohol_strong_used_day` | `TEXT DEFAULT NULL` | :1507 |
| `users` | `alcohol_strong_used_today` | `INTEGER DEFAULT 0` | :1506 |
| `users` | `alcohol_weak_used_day` | `TEXT DEFAULT NULL` | :1505 |
| `users` | `alcohol_weak_used_today` | `INTEGER DEFAULT 0` | :1504 |
| `users` | `ap_recovery_day` | `TEXT DEFAULT NULL` | :1499 |
| `users` | `ap_restored_day` | `TEXT DEFAULT NULL` | :1358 |
| `users` | `ap_restored_today` | `INTEGER DEFAULT 0` | :1359 |
| `users` | `beer_used_day` | `TEXT DEFAULT NULL` | :1502 |
| `users` | `beer_used_today` | `INTEGER DEFAULT 0` | :1501 |
| `users` | `callsign` | `TEXT` | :1445 |
| `users` | `callsign_free_used` | `INTEGER DEFAULT 0` | :1654 |
| `users` | `dodge_buff_pct` | `INTEGER DEFAULT 0` | :1726 |
| `users` | `dodge_buff_until` | `TEXT DEFAULT NULL` | :1725 |
| `users` | `duel_losses` | `INTEGER DEFAULT 0` | :1363 |
| `users` | `duel_rating` | `INTEGER DEFAULT 0` | :1361 |
| `users` | `duel_wins` | `INTEGER DEFAULT 0` | :1362 |
| `users` | `equipment` | `TEXT DEFAULT '{}'` | :1230 |
| `users` | `fish_sold_day` | `TEXT DEFAULT NULL` | :1534 |
| `users` | `fish_sold_today` | `INTEGER DEFAULT 0` | :1535 |
| `users` | `fishing_bait` | `TEXT DEFAULT ''` | :1443 |
| `users` | `forest_attempts_since_boar` | `INTEGER DEFAULT 0` | :1537 |
| `users` | `forest_attempts_since_wolf` | `INTEGER DEFAULT 0` | :1539 |
| `users` | `forest_sold_day` | `TEXT DEFAULT NULL` | :1549 |
| `users` | `forest_sold_today` | `INTEGER DEFAULT 0` | :1550 |
| `users` | `fountain_used_day` | `TEXT DEFAULT NULL` | :1522 |
| `users` | `fountain_used_today` | `INTEGER DEFAULT 0` | :1523 |
| `users` | `lang` | `TEXT DEFAULT 'ru'` | :1207 |
| `users` | `lantern_amber_at` | `TEXT DEFAULT NULL` | :1528 |
| `users` | `lantern_medit_day` | `TEXT DEFAULT NULL` | :1527 |
| `users` | `last_active` | `REAL DEFAULT 0` | :1366 |
| `users` | `last_salary_date` | `TIMESTAMP` | :1233 |
| `users` | `legioner` | `INTEGER DEFAULT 0` | :1772 |
| `users` | `logging_attempts_since_owl` | `INTEGER DEFAULT 0` | :1546 |
| `users` | `logging_attempts_since_snake` | `INTEGER DEFAULT 0` | :1545 |
| `users` | `market_license_expires` | `TEXT DEFAULT NULL` | :1653 |
| `users` | `mine_attempts_since_bat` | `INTEGER DEFAULT 0` | :1542 |
| `users` | `notify_enabled` | `INTEGER DEFAULT 1` | :1227 |
| `users` | `profile_public` | `INTEGER DEFAULT 1` | :1228 |
| `users` | `promoted_rank` | `TEXT` | :1206 |
| `users` | `salary` | `INTEGER DEFAULT 0` | :1231 |
| `users` | `salary_debt` | `INTEGER DEFAULT 0` | :1234 |
| `users` | `salary_period_days` | `INTEGER DEFAULT 7` | :1232 |
| `users` | `seaweed_used_day` | `TEXT DEFAULT NULL` | :1496 |
| `users` | `seaweed_used_today` | `INTEGER DEFAULT 0` | :1495 |
| `users` | `shower_used_day` | `TEXT DEFAULT NULL` | :1525 |
| `users` | `shower_used_today` | `INTEGER DEFAULT 0` | :1532 |
| `users` | `special_blocked_until` | `TEXT DEFAULT NULL` | :1510 |
| `users` | `special_fails_today` | `INTEGER DEFAULT 0` | :1509 |
| `users` | `wing` | `TEXT` | :1769 |
| `users` | `xp_balance` | `INTEGER DEFAULT 0` | :1211 |
| `water_fish` | `excluded` | `INTEGER DEFAULT 0` | :1441 |
| `water_fish` | `kind` | `TEXT DEFAULT 'fish'` | :1676 |
| `water_fish` | `super_rare` | `INTEGER DEFAULT 0` | :1679 |
| `wings` | `abbr` | `TEXT DEFAULT ''` | :1489 |
| `wings` | `callsign` | `TEXT DEFAULT ''` | :1491 |
| `wings` | `emoji` | `TEXT DEFAULT ''` | :1492 |
| `wings` | `name` | `TEXT DEFAULT ''` | :1490 |
| `wings` | `num` | `TEXT DEFAULT ''` | :1488 |
| `wings` | `sort_order` | `INTEGER DEFAULT 0` | :1493 |

## 2. Идемпотентные засевы и миграции данных

| Функция | Вызывается из main.py | Назначение (первая строка docstring) | db.py |
|---|---|---|---|
| `backfill_rank_statuses` | — | Разово выдать статусы по текущим званиям всех пилотов (войска и админ-звания). | :6880 |
| `ensure_achievements` | ✅ | Идемпотентно засевает награды-уровни достижений и синхронизирует их. | :14882 |
| `ensure_base_status` | — | Базовый статус «Турист» для каждого нового игрока. | :7263 |
| `ensure_base_statuses` | — | Создаёт базовые статусы иерархии, если их нет. | :7218 |
| `ensure_berry_candy_recipe` | — | Рецепт «Леденец из ягод»: черника + малина + сахар. Создаётся скрытым: | :10849 |
| `ensure_clan_building` | — | — | :16995 |
| `ensure_clan_cape_item` | — | Клановая накидка: экипировка слота «Клановая накидка». Продаётся в клановой | :10831 |
| `ensure_duel_items` | ✅ | Товары Дома Дуэлей: дуэльные перчатки (отдельный слот) и клубная карта. | :12333 |
| `ensure_dungeon_enemy_drops` | ✅ | Синхронизирует врагов существующего данжа с DEFAULT_DUNGEON (дропы, HP, награды, | :14332 |
| `ensure_dungeon_reservoir_items` | ✅ | Идемпотентно добавляет предметы водохранилища подземелья (v0.12.0). | :14255 |
| `ensure_dungeon_shop_items` | ✅ | Идемпотентно добавляет предметы данжа (зелье в магазин, трофеи) — для существующих БД. | :13863 |
| `ensure_fire_mushroom_pool` | — | Огненный гриб — на прогалину с весом 15; по 1 снимаем с пяти самых редких грибов. Один раз. | :10707 |
| `ensure_fire_tree_items` | — | Предметы пожертвования и талисмана: скрыты, без цены продажи, не на рынке. | :10640 |
| `ensure_firelab_enemies` | ✅ | Идемпотентно засевает врагов Огненного Лабиринта (4 обычных + босс). | :10954 |
| `ensure_firelab_items` | ✅ | Идемпотентно создаёт предметы Фазы 3 «Дней Пламенного Круговорота». | :11002 |
| `ensure_fishing_enemies` | ✅ | Идемпотентно засевает врагов рыбалки (мутировавший моллюск) из MOLLUSK_SEED. | :11276 |
| `ensure_forest_berry_items` | — | Ягоды (горсть) и шкура медведя: предметы-ресурсы вне магазина. Идемпотентно. | :10811 |
| `ensure_forest_berry_pool` | — | Таблица ягод поиска по зонам (как у грибов): шансы правит админ. Засев — один раз. | :10678 |
| `ensure_forest_enemies` | ✅ | Идемпотентно засевает врагов леса (кабан и Белый Волк Севера). | :10922 |
| `ensure_forest_items` | ✅ | Идемпотентно создаёт предметы леса (грибы, добыча кабана, жареные блюда, яд). | :9868 |
| `ensure_forest_mushrooms` | ✅ | Идемпотентно засевает пул грибов леса из FOREST_DEFAULTS. | :10040 |
| `ensure_forest_zones` | ✅ | Разовый перенос старого пула леса в зону поляны и засев пула опушки. | :10283 |
| `ensure_item_rarity_unified` | ✅ | Идемпотентно применяет единую градацию редкости (v0.43.10). | :2253 |
| `ensure_kvp_award` | ✅ | — | :12592 |
| `ensure_kvp_items` | ✅ | Обеспечивает эксклюзивный предмет К.В.П. — «Сержантскую трость». | :12306 |
| `ensure_kvp_user` | — | Гарантирует наличие строки прогресса К.В.П. для игрока. | :12871 |
| `ensure_life_items` | ✅ | Идемпотентно добавляет предметы жилья, мебели, семян, ресурсов и продовольствия. | :14079 |
| `ensure_logging_enemies` | ✅ | Идемпотентно засевает врагов Лесозаготовки (Змея и Неясыть). | :10029 |
| `ensure_logging_items` | ✅ | Идемпотентно создаёт предметы Лесозаготовки (топор, бревна, дропы). | :9986 |
| `ensure_market_license_item` | ✅ | Идемпотентно добавляет «Торговую лицензию» в магазин. | :11856 |
| `ensure_mine_enemies` | ✅ | Идемпотентно засевает врагов копи (Летучая мышь) из MINE_BAT_SEED. | :9977 |
| `ensure_mine_items` | ✅ | Идемпотентно создаёт предметы Железной копи (кирка, руда, самоцветы). | :9946 |
| `ensure_mollusk_items` | ✅ | Идемпотентно создаёт предметы моллюска (из его добычи и готового блюда). | :11282 |
| `ensure_passport_item` | ✅ | Создаёт предмет «Паспорт Нордхайма» (категория «Документы»), если его нет. | :12665 |
| `ensure_player_housing` | — | Возвращает жильё игрока, создавая муниципальную квартиру для пилота при первом обращении. | :14477 |
| `ensure_rank_statuses_for_troops` | — | Выдать статус по текущему званию игрока (по войскам или админ-назначению). | :6868 |
| `ensure_recipe_shop_item` | — | Синхронизирует товар-рецепт «Рецепт: <name>» с рецептом (менеджер). | :15317 |
| `ensure_recipe_shop_items` | ✅ | Создаёт в магазине предметы-рецепты категории 'recipes'. | :16671 |
| `ensure_recipes` | ✅ | Идемпотентно засевает рецепты и синхронизирует уже существующие. | :15167 |
| `ensure_tourist_booklet` | ✅ | Создаёт предмет «Буклет туриста» и награду «Опытный турист», если их нет. | :12628 |
| `ensure_user_recipes_backfill` | ✅ | Разово открывает все рецепты существующим игрокам. | :16821 |
| `ensure_water_fish` | ✅ | Идемпотентно засевает water_fish из дефолтов. Правившие админом строки | :9378 |
| `migrate_legacy_junk` | ✅ | Переносит старые копии мусора (сапог, водоросли) из инвентаря в улов. | :9220 |
| `seed_default_items` | ✅ | Заполняет магазин базовым набором товаров, если он пуст и не было своих товаров. | :12029 |
| `seed_dungeon` | ✅ | — | :12184 |
| `seed_kvp` | ✅ | Создаёт тренировочный данж К.В.П. с врагами (Ефрейтор, Старший сержант), если его нет. | :12255 |
| `seed_locations` | — | Засеивает базовые локации города (Ратуша, Библиотека) как пример управляемого доступа. | :2045 |

## 3. Отдельные скрипты миграций

- `migrate_113.py` — Проверка миграций 0.19.0 на чистой БД: колонки polls, таблица rep_speeches.
- `migrate_113_old.py` — Миграция 0.19.0 поверх БД со старой схемой polls (без closes_at/is_archived).

