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
| `awards` | `achievement_key` | `TEXT DEFAULT NULL` | :1471 |
| `awards` | `achievement_level` | `INTEGER DEFAULT 0` | :1472 |
| `awards` | `bonus_attack` | `INTEGER DEFAULT 0` | :1450 |
| `awards` | `bonus_crit` | `INTEGER DEFAULT 0` | :1457 |
| `awards` | `bonus_defense` | `INTEGER DEFAULT 0` | :1451 |
| `awards` | `bonus_dodge` | `INTEGER DEFAULT 0` | :1452 |
| `awards` | `bonus_fishing` | `INTEGER DEFAULT 0` | :1453 |
| `awards` | `bonus_hp` | `INTEGER DEFAULT 0` | :1454 |
| `awards` | `bonus_json` | `TEXT DEFAULT '{}'` | :1473 |
| `awards` | `bonus_report_tax` | `INTEGER DEFAULT 0` | :1461 |
| `awards` | `bonus_shop_discount` | `INTEGER DEFAULT 0` | :1460 |
| `awards` | `image` | `TEXT` | :1449 |
| `awards` | `monthly_nm` | `INTEGER DEFAULT 0` | :1465 |
| `awards` | `reward_nm` | `INTEGER DEFAULT 0` | :1464 |
| `buildings` | `required_status` | `TEXT` | :1192 |
| `clan_buildings` | `building_photo_file_id` | `TEXT` | :1869 |
| `clan_members` | `role` | `TEXT NOT NULL DEFAULT 'member'` | :1194 |
| `clans` | `tree_amber_at` | `TEXT DEFAULT NULL` | :1520 |
| `dungeon_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1371 |
| `dungeon_enemies` | `admin_tuned` | `INTEGER DEFAULT 0` | :1409 |
| `dungeon_enemies` | `armor` | `INTEGER DEFAULT 0` | :1367 |
| `dungeon_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1652 |
| `dungeon_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1653 |
| `dungeon_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1369 |
| `dungeon_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1370 |
| `dungeon_enemies` | `damage_max` | `INTEGER DEFAULT 0` | :1366 |
| `dungeon_enemies` | `damage_min` | `INTEGER DEFAULT 0` | :1365 |
| `dungeon_enemies` | `description` | `TEXT` | :1363 |
| `dungeon_enemies` | `dodge` | `INTEGER DEFAULT 0` | :1364 |
| `dungeon_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1368 |
| `dungeon_enemies` | `drops` | `TEXT DEFAULT '[]'` | :1359 |
| `dungeon_enemies` | `effect_resist` | `TEXT DEFAULT NULL` | :1406 |
| `dungeon_enemies` | `frostbite_chance` | `INTEGER DEFAULT 0` | :1654 |
| `dungeon_enemies` | `image` | `TEXT` | :1360 |
| `dungeon_enemies` | `poison_chance` | `INTEGER DEFAULT 0` | :1361 |
| `dungeon_enemies` | `poison_dmg` | `INTEGER DEFAULT 0` | :1362 |
| `dungeons` | `is_training` | `INTEGER DEFAULT 0` | :1642 |
| `dungeons` | `photo_dawn` | `TEXT` | :1422 |
| `dungeons` | `photo_day` | `TEXT` | :1423 |
| `dungeons` | `photo_night` | `TEXT` | :1425 |
| `dungeons` | `photo_rope` | `TEXT` | :1428 |
| `dungeons` | `photo_sunset` | `TEXT` | :1424 |
| `dungeons` | `photo_water` | `TEXT` | :1427 |
| `dungeons` | `rooms_map` | `TEXT` | :1659 |
| `fire_lab_sessions` | `boss_encounters` | `INTEGER DEFAULT 0` | :1876 |
| `fire_lab_sessions` | `effects_json` | `TEXT DEFAULT NULL` | :1875 |
| `fire_lab_sessions` | `enemy_json` | `TEXT DEFAULT NULL` | :1874 |
| `fire_lab_sessions` | `fish_used` | `INTEGER DEFAULT 0` | :1877 |
| `fire_lab_sessions` | `last_active_at` | `TIMESTAMP` | :1883 |
| `fire_lab_sessions` | `tree_open` | `INTEGER DEFAULT 0` | :1881 |
| `fire_lab_sessions` | `well_open` | `INTEGER DEFAULT 0` | :1879 |
| `firelab_enemies` | `armor` | `INTEGER DEFAULT 0` | :1873 |
| `firelab_enemies` | `on_hit_effects` | `TEXT DEFAULT NULL` | :1872 |
| `fish_catches` | `expires_at` | `TIMESTAMP` | :1510 |
| `fish_catches` | `kind` | `TEXT DEFAULT 'fish'` | :1665 |
| `fishing_enemies` | `armor` | `INTEGER DEFAULT 0` | :1382 |
| `fishing_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1380 |
| `fishing_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1381 |
| `forest_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1376 |
| `forest_enemies` | `armor` | `INTEGER DEFAULT 0` | :1372 |
| `forest_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1378 |
| `forest_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1379 |
| `forest_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1374 |
| `forest_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1375 |
| `forest_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1373 |
| `forest_mushrooms` | `zone` | `TEXT DEFAULT 'clearing'` | :1562 |
| `housing_slots` | `embedded` | `INTEGER DEFAULT 0` | :1593 |
| `inventory` | `expires_at` | `TIMESTAMP` | :1505 |
| `inventory` | `plant_data` | `TEXT` | :1507 |
| `inventory` | `shop_qty` | `INTEGER DEFAULT 0` | :1701 |
| `items` | `armor` | `INTEGER DEFAULT 0` | :1225 |
| `items` | `crit_chance` | `INTEGER DEFAULT 0` | :1228 |
| `items` | `crit_mult` | `REAL DEFAULT 0` | :1229 |
| `items` | `cure_frostbite` | `INTEGER DEFAULT 0` | :1656 |
| `items` | `cure_poison` | `INTEGER DEFAULT 0` | :1410 |
| `items` | `damage` | `INTEGER DEFAULT 0` | :1357 |
| `items` | `dodge_bonus` | `INTEGER DEFAULT 0` | :1689 |
| `items` | `dodge_buff_pct` | `INTEGER DEFAULT 0` | :1693 |
| `items` | `drink_effect` | `TEXT DEFAULT NULL` | :1493 |
| `items` | `equip_slot` | `TEXT` | :1231 |
| `items` | `heal` | `INTEGER DEFAULT 0` | :1358 |
| `items` | `heal_bonus_pct` | `INTEGER DEFAULT 0` | :1688 |
| `items` | `housing_slots` | `INTEGER` | :1820 |
| `items` | `housing_type` | `TEXT` | :1819 |
| `items` | `loot_only` | `INTEGER DEFAULT 0` | :1825 |
| `items` | `market_ok` | `INTEGER DEFAULT 0` | :1662 |
| `items` | `plant_name` | `TEXT` | :1672 |
| `items` | `regen` | `INTEGER DEFAULT 0` | :1420 |
| `items` | `regen_turns` | `INTEGER DEFAULT 0` | :1692 |
| `items` | `required_status` | `TEXT` | :1191 |
| `items` | `restock_enabled` | `INTEGER DEFAULT 0` | :1696 |
| `items` | `restock_target` | `INTEGER DEFAULT 0` | :1697 |
| `items` | `shop_limit` | `INTEGER DEFAULT 0` | :1700 |
| `items` | `weapon_effect` | `TEXT` | :1683 |
| `items` | `weapon_effect_chance` | `INTEGER DEFAULT 0` | :1684 |
| `items` | `weapon_effect_dmg` | `INTEGER DEFAULT 0` | :1685 |
| `locations` | `clearing_photo` | `TEXT DEFAULT NULL` | :1548 |
| `locations` | `fire_photo` | `TEXT DEFAULT NULL` | :1546 |
| `locations` | `glade_photo` | `TEXT DEFAULT NULL` | :1547 |
| `locations` | `logging_photo` | `TEXT DEFAULT NULL` | :1557 |
| `locations` | `mine_level_photo` | `TEXT DEFAULT NULL` | :1551 |
| `locations` | `photo_dawn` | `TEXT` | :1412 |
| `locations` | `photo_day` | `TEXT` | :1413 |
| `locations` | `photo_night` | `TEXT` | :1415 |
| `locations` | `photo_sunset` | `TEXT` | :1414 |
| `locations` | `preview_photo` | `TEXT` | :1411 |
| `locations` | `season_photos` | `TEXT DEFAULT NULL` | :1543 |
| `locations` | `storage_photo` | `TEXT DEFAULT NULL` | :1553 |
| `locations` | `visits` | `INTEGER DEFAULT 0` | :1417 |
| `logging_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1397 |
| `logging_enemies` | `armor` | `INTEGER DEFAULT 0` | :1393 |
| `logging_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1395 |
| `logging_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1396 |
| `logging_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1394 |
| `market_fish` | `base_price` | `INTEGER DEFAULT 0` | :1645 |
| `market_items` | `qty` | `INTEGER DEFAULT 1` | :1648 |
| `mine_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1388 |
| `mine_enemies` | `armor` | `INTEGER DEFAULT 0` | :1384 |
| `mine_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1389 |
| `mine_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1390 |
| `mine_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1386 |
| `mine_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1387 |
| `mine_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1385 |
| `nii_reports` | `photo2_file_id` | `TEXT DEFAULT NULL` | :1475 |
| `player_dungeon_run` | `loot_nm` | `INTEGER DEFAULT 0` | :1344 |
| `player_dungeon_run` | `started_at` | `TIMESTAMP DEFAULT CURRENT_TIMESTAMP` | :1345 |
| `player_housing` | `expansions_installed` | `INTEGER DEFAULT 0` | :1595 |
| `player_housing` | `housing_label` | `TEXT` | :1821 |
| `player_housing` | `housing_slots` | `INTEGER` | :1822 |
| `player_housing` | `tax_last_check` | `TEXT DEFAULT NULL` | :1646 |
| `player_housing` | `tax_unpaid_months` | `INTEGER DEFAULT 0` | :1647 |
| `polls` | `archived_day` | `TEXT DEFAULT ''` | :1611 |
| `polls` | `closed_at` | `TIMESTAMP` | :1503 |
| `polls` | `closed_by` | `INTEGER` | :1502 |
| `polls` | `closes_at` | `TIMESTAMP` | :1600 |
| `polls` | `is_archived` | `INTEGER DEFAULT 0` | :1610 |
| `reports` | `credited_troops` | `INTEGER` | :1236 |
| `reports` | `paid` | `INTEGER DEFAULT 0` | :1243 |
| `reports` | `reject_reason` | `TEXT` | :1249 |
| `reports` | `reviewed_at` | `TEXT` | :1253 |
| `reports` | `reviewed_by_name` | `TEXT` | :1250 |
| `reports` | `total_troops` | `INTEGER DEFAULT 0` | :1234 |
| `statuses` | `sort_order` | `INTEGER DEFAULT 0` | :1193 |
| `users` | `about` | `TEXT DEFAULT ''` | :1219 |
| `users` | `alcohol_strong_used_day` | `TEXT DEFAULT NULL` | :1497 |
| `users` | `alcohol_strong_used_today` | `INTEGER DEFAULT 0` | :1496 |
| `users` | `alcohol_weak_used_day` | `TEXT DEFAULT NULL` | :1495 |
| `users` | `alcohol_weak_used_today` | `INTEGER DEFAULT 0` | :1494 |
| `users` | `ap_recovery_day` | `TEXT DEFAULT NULL` | :1489 |
| `users` | `ap_restored_day` | `TEXT DEFAULT NULL` | :1348 |
| `users` | `ap_restored_today` | `INTEGER DEFAULT 0` | :1349 |
| `users` | `beer_used_day` | `TEXT DEFAULT NULL` | :1492 |
| `users` | `beer_used_today` | `INTEGER DEFAULT 0` | :1491 |
| `users` | `callsign` | `TEXT` | :1435 |
| `users` | `callsign_free_used` | `INTEGER DEFAULT 0` | :1644 |
| `users` | `dodge_buff_pct` | `INTEGER DEFAULT 0` | :1716 |
| `users` | `dodge_buff_until` | `TEXT DEFAULT NULL` | :1715 |
| `users` | `duel_losses` | `INTEGER DEFAULT 0` | :1353 |
| `users` | `duel_rating` | `INTEGER DEFAULT 0` | :1351 |
| `users` | `duel_wins` | `INTEGER DEFAULT 0` | :1352 |
| `users` | `equipment` | `TEXT DEFAULT '{}'` | :1220 |
| `users` | `fish_sold_day` | `TEXT DEFAULT NULL` | :1524 |
| `users` | `fish_sold_today` | `INTEGER DEFAULT 0` | :1525 |
| `users` | `fishing_bait` | `TEXT DEFAULT ''` | :1433 |
| `users` | `forest_attempts_since_boar` | `INTEGER DEFAULT 0` | :1527 |
| `users` | `forest_attempts_since_wolf` | `INTEGER DEFAULT 0` | :1529 |
| `users` | `forest_sold_day` | `TEXT DEFAULT NULL` | :1539 |
| `users` | `forest_sold_today` | `INTEGER DEFAULT 0` | :1540 |
| `users` | `fountain_used_day` | `TEXT DEFAULT NULL` | :1512 |
| `users` | `fountain_used_today` | `INTEGER DEFAULT 0` | :1513 |
| `users` | `lang` | `TEXT DEFAULT 'ru'` | :1197 |
| `users` | `lantern_amber_at` | `TEXT DEFAULT NULL` | :1518 |
| `users` | `lantern_medit_day` | `TEXT DEFAULT NULL` | :1517 |
| `users` | `last_active` | `REAL DEFAULT 0` | :1356 |
| `users` | `last_salary_date` | `TIMESTAMP` | :1223 |
| `users` | `legioner` | `INTEGER DEFAULT 0` | :1762 |
| `users` | `logging_attempts_since_owl` | `INTEGER DEFAULT 0` | :1536 |
| `users` | `logging_attempts_since_snake` | `INTEGER DEFAULT 0` | :1535 |
| `users` | `market_license_expires` | `TEXT DEFAULT NULL` | :1643 |
| `users` | `mine_attempts_since_bat` | `INTEGER DEFAULT 0` | :1532 |
| `users` | `notify_enabled` | `INTEGER DEFAULT 1` | :1217 |
| `users` | `profile_public` | `INTEGER DEFAULT 1` | :1218 |
| `users` | `promoted_rank` | `TEXT` | :1196 |
| `users` | `salary` | `INTEGER DEFAULT 0` | :1221 |
| `users` | `salary_debt` | `INTEGER DEFAULT 0` | :1224 |
| `users` | `salary_period_days` | `INTEGER DEFAULT 7` | :1222 |
| `users` | `seaweed_used_day` | `TEXT DEFAULT NULL` | :1486 |
| `users` | `seaweed_used_today` | `INTEGER DEFAULT 0` | :1485 |
| `users` | `shower_used_day` | `TEXT DEFAULT NULL` | :1515 |
| `users` | `shower_used_today` | `INTEGER DEFAULT 0` | :1522 |
| `users` | `special_blocked_until` | `TEXT DEFAULT NULL` | :1500 |
| `users` | `special_fails_today` | `INTEGER DEFAULT 0` | :1499 |
| `users` | `wing` | `TEXT` | :1759 |
| `users` | `xp_balance` | `INTEGER DEFAULT 0` | :1201 |
| `water_fish` | `excluded` | `INTEGER DEFAULT 0` | :1431 |
| `water_fish` | `kind` | `TEXT DEFAULT 'fish'` | :1666 |
| `water_fish` | `super_rare` | `INTEGER DEFAULT 0` | :1669 |
| `wings` | `abbr` | `TEXT DEFAULT ''` | :1479 |
| `wings` | `callsign` | `TEXT DEFAULT ''` | :1481 |
| `wings` | `emoji` | `TEXT DEFAULT ''` | :1482 |
| `wings` | `name` | `TEXT DEFAULT ''` | :1480 |
| `wings` | `num` | `TEXT DEFAULT ''` | :1478 |
| `wings` | `sort_order` | `INTEGER DEFAULT 0` | :1483 |

## 2. Идемпотентные засевы и миграции данных

| Функция | Вызывается из main.py | Назначение (первая строка docstring) | db.py |
|---|---|---|---|
| `backfill_rank_statuses` | — | Разово выдать статусы по текущим званиям всех пилотов (войска и админ-звания). | :6823 |
| `ensure_achievements` | ✅ | Идемпотентно засевает награды-уровни достижений и синхронизирует их. | :14770 |
| `ensure_base_status` | — | Базовый статус «Турист» для каждого нового игрока. | :7206 |
| `ensure_base_statuses` | — | Создаёт базовые статусы иерархии, если их нет. | :7161 |
| `ensure_berry_candy_recipe` | — | Рецепт «Леденец из ягод»: черника + малина + сахар. Создаётся скрытым: | :10774 |
| `ensure_clan_building` | — | — | :16879 |
| `ensure_clan_cape_item` | — | Клановая накидка: экипировка слота «Клановая накидка». Продаётся в клановой | :10756 |
| `ensure_duel_items` | ✅ | Товары Дома Дуэлей: дуэльные перчатки (отдельный слот) и клубная карта. | :12258 |
| `ensure_dungeon_enemy_drops` | ✅ | Синхронизирует врагов существующего данжа с DEFAULT_DUNGEON (дропы, HP, награды, | :14220 |
| `ensure_dungeon_reservoir_items` | ✅ | Идемпотентно добавляет предметы водохранилища подземелья (v0.12.0). | :14143 |
| `ensure_dungeon_shop_items` | ✅ | Идемпотентно добавляет предметы данжа (зелье в магазин, трофеи) — для существующих БД. | :13751 |
| `ensure_fire_mushroom_pool` | — | Огненный гриб — на прогалину с весом 15; по 1 снимаем с пяти самых редких грибов. Один раз. | :10632 |
| `ensure_fire_tree_items` | — | Предметы пожертвования и талисмана: скрыты, без цены продажи, не на рынке. | :10565 |
| `ensure_firelab_enemies` | ✅ | Идемпотентно засевает врагов Огненного Лабиринта (4 обычных + босс). | :10879 |
| `ensure_firelab_items` | ✅ | Идемпотентно создаёт предметы Фазы 3 «Дней Пламенного Круговорота». | :10927 |
| `ensure_fishing_enemies` | ✅ | Идемпотентно засевает врагов рыбалки (мутировавший моллюск) из MOLLUSK_SEED. | :11201 |
| `ensure_forest_berry_items` | — | Ягоды (горсть) и шкура медведя: предметы-ресурсы вне магазина. Идемпотентно. | :10736 |
| `ensure_forest_berry_pool` | — | Таблица ягод поиска по зонам (как у грибов): шансы правит админ. Засев — один раз. | :10603 |
| `ensure_forest_enemies` | ✅ | Идемпотентно засевает врагов леса (кабан и Белый Волк Севера). | :10847 |
| `ensure_forest_items` | ✅ | Идемпотентно создаёт предметы леса (грибы, добыча кабана, жареные блюда, яд). | :9793 |
| `ensure_forest_mushrooms` | ✅ | Идемпотентно засевает пул грибов леса из FOREST_DEFAULTS. | :9965 |
| `ensure_forest_zones` | ✅ | Разовый перенос старого пула леса в зону поляны и засев пула опушки. | :10208 |
| `ensure_item_rarity_unified` | ✅ | Идемпотентно применяет единую градацию редкости (v0.43.10). | :2202 |
| `ensure_kvp_award` | ✅ | — | :12517 |
| `ensure_kvp_items` | ✅ | Обеспечивает эксклюзивный предмет К.В.П. — «Сержантскую трость». | :12231 |
| `ensure_kvp_user` | — | Гарантирует наличие строки прогресса К.В.П. для игрока. | :12759 |
| `ensure_life_items` | ✅ | Идемпотентно добавляет предметы жилья, мебели, семян, ресурсов и продовольствия. | :13967 |
| `ensure_logging_enemies` | ✅ | Идемпотентно засевает врагов Лесозаготовки (Змея и Неясыть). | :9954 |
| `ensure_logging_items` | ✅ | Идемпотентно создаёт предметы Лесозаготовки (топор, бревна, дропы). | :9911 |
| `ensure_market_license_item` | ✅ | Идемпотентно добавляет «Торговую лицензию» в магазин. | :11781 |
| `ensure_mine_enemies` | ✅ | Идемпотентно засевает врагов копи (Летучая мышь) из MINE_BAT_SEED. | :9902 |
| `ensure_mine_items` | ✅ | Идемпотентно создаёт предметы Железной копи (кирка, руда, самоцветы). | :9871 |
| `ensure_mollusk_items` | ✅ | Идемпотентно создаёт предметы моллюска (из его добычи и готового блюда). | :11207 |
| `ensure_passport_item` | ✅ | Создаёт предмет «Паспорт Нордхайма» (категория «Документы»), если его нет. | :12590 |
| `ensure_player_housing` | — | Возвращает жильё игрока, создавая муниципальную квартиру для пилота при первом обращении. | :14365 |
| `ensure_rank_statuses_for_troops` | — | Выдать статус по текущему званию игрока (по войскам или админ-назначению). | :6811 |
| `ensure_recipe_shop_item` | — | Синхронизирует товар-рецепт «Рецепт: <name>» с рецептом (менеджер). | :15205 |
| `ensure_recipe_shop_items` | ✅ | Создаёт в магазине предметы-рецепты категории 'recipes'. | :16555 |
| `ensure_recipes` | ✅ | Идемпотентно засевает рецепты и синхронизирует уже существующие. | :15055 |
| `ensure_tourist_booklet` | ✅ | Создаёт предмет «Буклет туриста» и награду «Опытный турист», если их нет. | :12553 |
| `ensure_user_recipes_backfill` | ✅ | Разово открывает все рецепты существующим игрокам. | :16705 |
| `ensure_water_fish` | ✅ | Идемпотентно засевает water_fish из дефолтов. Правившие админом строки | :9303 |
| `migrate_legacy_junk` | ✅ | Переносит старые копии мусора (сапог, водоросли) из инвентаря в улов. | :9145 |
| `seed_default_items` | ✅ | Заполняет магазин базовым набором товаров, если он пуст и не было своих товаров. | :11954 |
| `seed_dungeon` | ✅ | — | :12109 |
| `seed_kvp` | ✅ | Создаёт тренировочный данж К.В.П. с врагами (Ефрейтор, Старший сержант), если его нет. | :12180 |
| `seed_locations` | — | Засеивает базовые локации города (Ратуша, Библиотека) как пример управляемого доступа. | :1994 |

## 3. Отдельные скрипты миграций

- `migrate_113.py` — Проверка миграций 0.19.0 на чистой БД: колонки polls, таблица rep_speeches.
- `migrate_113_old.py` — Миграция 0.19.0 поверх БД со старой схемой polls (без closes_at/is_archived).

