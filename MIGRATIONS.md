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

Всего вызовов: **172**; таблиц: **24**.

| Таблица | Колонка | Тип / значение по умолчанию | db.py |
|---|---|---|---|
| `awards` | `achievement_key` | `TEXT DEFAULT NULL` | :1208 |
| `awards` | `achievement_level` | `INTEGER DEFAULT 0` | :1209 |
| `awards` | `bonus_attack` | `INTEGER DEFAULT 0` | :1187 |
| `awards` | `bonus_crit` | `INTEGER DEFAULT 0` | :1194 |
| `awards` | `bonus_defense` | `INTEGER DEFAULT 0` | :1188 |
| `awards` | `bonus_dodge` | `INTEGER DEFAULT 0` | :1189 |
| `awards` | `bonus_fishing` | `INTEGER DEFAULT 0` | :1190 |
| `awards` | `bonus_hp` | `INTEGER DEFAULT 0` | :1191 |
| `awards` | `bonus_json` | `TEXT DEFAULT '{}'` | :1210 |
| `awards` | `bonus_report_tax` | `INTEGER DEFAULT 0` | :1198 |
| `awards` | `bonus_shop_discount` | `INTEGER DEFAULT 0` | :1197 |
| `awards` | `image` | `TEXT` | :1186 |
| `awards` | `monthly_nm` | `INTEGER DEFAULT 0` | :1202 |
| `awards` | `reward_nm` | `INTEGER DEFAULT 0` | :1201 |
| `buildings` | `required_status` | `TEXT` | :954 |
| `dungeon_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1122 |
| `dungeon_enemies` | `admin_tuned` | `INTEGER DEFAULT 0` | :1158 |
| `dungeon_enemies` | `armor` | `INTEGER DEFAULT 0` | :1118 |
| `dungeon_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1382 |
| `dungeon_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1383 |
| `dungeon_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1120 |
| `dungeon_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1121 |
| `dungeon_enemies` | `damage_max` | `INTEGER DEFAULT 0` | :1117 |
| `dungeon_enemies` | `damage_min` | `INTEGER DEFAULT 0` | :1116 |
| `dungeon_enemies` | `description` | `TEXT` | :1114 |
| `dungeon_enemies` | `dodge` | `INTEGER DEFAULT 0` | :1115 |
| `dungeon_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1119 |
| `dungeon_enemies` | `drops` | `TEXT DEFAULT '[]'` | :1110 |
| `dungeon_enemies` | `frostbite_chance` | `INTEGER DEFAULT 0` | :1384 |
| `dungeon_enemies` | `image` | `TEXT` | :1111 |
| `dungeon_enemies` | `poison_chance` | `INTEGER DEFAULT 0` | :1112 |
| `dungeon_enemies` | `poison_dmg` | `INTEGER DEFAULT 0` | :1113 |
| `dungeons` | `is_training` | `INTEGER DEFAULT 0` | :1373 |
| `dungeons` | `photo_dawn` | `TEXT` | :1171 |
| `dungeons` | `photo_day` | `TEXT` | :1172 |
| `dungeons` | `photo_night` | `TEXT` | :1174 |
| `dungeons` | `photo_rope` | `TEXT` | :1177 |
| `dungeons` | `photo_sunset` | `TEXT` | :1173 |
| `dungeons` | `photo_water` | `TEXT` | :1176 |
| `dungeons` | `rooms_map` | `TEXT` | :1389 |
| `fish_catches` | `expires_at` | `TIMESTAMP` | :1247 |
| `fish_catches` | `kind` | `TEXT DEFAULT 'fish'` | :1395 |
| `fishing_enemies` | `armor` | `INTEGER DEFAULT 0` | :1133 |
| `fishing_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1131 |
| `fishing_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1132 |
| `forest_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1127 |
| `forest_enemies` | `armor` | `INTEGER DEFAULT 0` | :1123 |
| `forest_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1129 |
| `forest_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1130 |
| `forest_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1125 |
| `forest_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1126 |
| `forest_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1124 |
| `forest_mushrooms` | `zone` | `TEXT DEFAULT 'clearing'` | :1292 |
| `housing_slots` | `embedded` | `INTEGER DEFAULT 0` | :1323 |
| `inventory` | `expires_at` | `TIMESTAMP` | :1242 |
| `inventory` | `plant_data` | `TEXT` | :1244 |
| `items` | `armor` | `INTEGER DEFAULT 0` | :984 |
| `items` | `crit_chance` | `INTEGER DEFAULT 0` | :987 |
| `items` | `crit_mult` | `REAL DEFAULT 0` | :988 |
| `items` | `cure_frostbite` | `INTEGER DEFAULT 0` | :1386 |
| `items` | `cure_poison` | `INTEGER DEFAULT 0` | :1159 |
| `items` | `damage` | `INTEGER DEFAULT 0` | :1108 |
| `items` | `drink_effect` | `TEXT DEFAULT NULL` | :1230 |
| `items` | `equip_slot` | `TEXT` | :990 |
| `items` | `heal` | `INTEGER DEFAULT 0` | :1109 |
| `items` | `housing_slots` | `INTEGER` | :1478 |
| `items` | `housing_type` | `TEXT` | :1477 |
| `items` | `loot_only` | `INTEGER DEFAULT 0` | :1483 |
| `items` | `market_ok` | `INTEGER DEFAULT 0` | :1392 |
| `items` | `plant_name` | `TEXT` | :1402 |
| `items` | `regen` | `INTEGER DEFAULT 0` | :1169 |
| `items` | `required_status` | `TEXT` | :953 |
| `items` | `weapon_effect` | `TEXT` | :1413 |
| `items` | `weapon_effect_chance` | `INTEGER DEFAULT 0` | :1414 |
| `items` | `weapon_effect_dmg` | `INTEGER DEFAULT 0` | :1415 |
| `locations` | `clearing_photo` | `TEXT DEFAULT NULL` | :1278 |
| `locations` | `glade_photo` | `TEXT DEFAULT NULL` | :1277 |
| `locations` | `logging_photo` | `TEXT DEFAULT NULL` | :1287 |
| `locations` | `mine_level_photo` | `TEXT DEFAULT NULL` | :1281 |
| `locations` | `photo_dawn` | `TEXT` | :1161 |
| `locations` | `photo_day` | `TEXT` | :1162 |
| `locations` | `photo_night` | `TEXT` | :1164 |
| `locations` | `photo_sunset` | `TEXT` | :1163 |
| `locations` | `preview_photo` | `TEXT` | :1160 |
| `locations` | `season_photos` | `TEXT DEFAULT NULL` | :1274 |
| `locations` | `storage_photo` | `TEXT DEFAULT NULL` | :1283 |
| `locations` | `visits` | `INTEGER DEFAULT 0` | :1166 |
| `logging_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1148 |
| `logging_enemies` | `armor` | `INTEGER DEFAULT 0` | :1144 |
| `logging_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1146 |
| `logging_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1147 |
| `logging_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1145 |
| `market_fish` | `base_price` | `INTEGER DEFAULT 0` | :1376 |
| `mine_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1139 |
| `mine_enemies` | `armor` | `INTEGER DEFAULT 0` | :1135 |
| `mine_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1140 |
| `mine_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1141 |
| `mine_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1137 |
| `mine_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1138 |
| `mine_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1136 |
| `nii_reports` | `photo2_file_id` | `TEXT DEFAULT NULL` | :1212 |
| `player_dungeon_run` | `loot_nm` | `INTEGER DEFAULT 0` | :1095 |
| `player_dungeon_run` | `started_at` | `TIMESTAMP DEFAULT CURRENT_TIMESTAMP` | :1096 |
| `player_housing` | `expansions_installed` | `INTEGER DEFAULT 0` | :1325 |
| `player_housing` | `housing_label` | `TEXT` | :1479 |
| `player_housing` | `housing_slots` | `INTEGER` | :1480 |
| `player_housing` | `tax_last_check` | `TEXT DEFAULT NULL` | :1377 |
| `player_housing` | `tax_unpaid_months` | `INTEGER DEFAULT 0` | :1378 |
| `polls` | `archived_day` | `TEXT DEFAULT ''` | :1341 |
| `polls` | `closed_at` | `TIMESTAMP` | :1240 |
| `polls` | `closed_by` | `INTEGER` | :1239 |
| `polls` | `closes_at` | `TIMESTAMP` | :1330 |
| `polls` | `is_archived` | `INTEGER DEFAULT 0` | :1340 |
| `reports` | `credited_troops` | `INTEGER` | :995 |
| `reports` | `paid` | `INTEGER DEFAULT 0` | :1002 |
| `reports` | `total_troops` | `INTEGER DEFAULT 0` | :993 |
| `statuses` | `sort_order` | `INTEGER DEFAULT 0` | :955 |
| `users` | `about` | `TEXT DEFAULT ''` | :978 |
| `users` | `alcohol_strong_used_day` | `TEXT DEFAULT NULL` | :1234 |
| `users` | `alcohol_strong_used_today` | `INTEGER DEFAULT 0` | :1233 |
| `users` | `alcohol_weak_used_day` | `TEXT DEFAULT NULL` | :1232 |
| `users` | `alcohol_weak_used_today` | `INTEGER DEFAULT 0` | :1231 |
| `users` | `ap_recovery_day` | `TEXT DEFAULT NULL` | :1226 |
| `users` | `ap_restored_day` | `TEXT DEFAULT NULL` | :1099 |
| `users` | `ap_restored_today` | `INTEGER DEFAULT 0` | :1100 |
| `users` | `beer_used_day` | `TEXT DEFAULT NULL` | :1229 |
| `users` | `beer_used_today` | `INTEGER DEFAULT 0` | :1228 |
| `users` | `callsign` | `TEXT` | :1184 |
| `users` | `callsign_free_used` | `INTEGER DEFAULT 0` | :1375 |
| `users` | `duel_losses` | `INTEGER DEFAULT 0` | :1104 |
| `users` | `duel_rating` | `INTEGER DEFAULT 0` | :1102 |
| `users` | `duel_wins` | `INTEGER DEFAULT 0` | :1103 |
| `users` | `equipment` | `TEXT DEFAULT '{}'` | :979 |
| `users` | `fish_sold_day` | `TEXT DEFAULT NULL` | :1255 |
| `users` | `fish_sold_today` | `INTEGER DEFAULT 0` | :1256 |
| `users` | `fishing_bait` | `TEXT DEFAULT ''` | :1182 |
| `users` | `forest_attempts_since_boar` | `INTEGER DEFAULT 0` | :1258 |
| `users` | `forest_attempts_since_wolf` | `INTEGER DEFAULT 0` | :1260 |
| `users` | `forest_sold_day` | `TEXT DEFAULT NULL` | :1270 |
| `users` | `forest_sold_today` | `INTEGER DEFAULT 0` | :1271 |
| `users` | `fountain_used_day` | `TEXT DEFAULT NULL` | :1249 |
| `users` | `fountain_used_today` | `INTEGER DEFAULT 0` | :1250 |
| `users` | `last_active` | `REAL DEFAULT 0` | :1107 |
| `users` | `last_salary_date` | `TIMESTAMP` | :982 |
| `users` | `legioner` | `INTEGER DEFAULT 0` | :1420 |
| `users` | `logging_attempts_since_owl` | `INTEGER DEFAULT 0` | :1267 |
| `users` | `logging_attempts_since_snake` | `INTEGER DEFAULT 0` | :1266 |
| `users` | `market_license_expires` | `TEXT DEFAULT NULL` | :1374 |
| `users` | `mine_attempts_since_bat` | `INTEGER DEFAULT 0` | :1263 |
| `users` | `notify_enabled` | `INTEGER DEFAULT 1` | :976 |
| `users` | `profile_public` | `INTEGER DEFAULT 1` | :977 |
| `users` | `promoted_rank` | `TEXT` | :956 |
| `users` | `salary` | `INTEGER DEFAULT 0` | :980 |
| `users` | `salary_debt` | `INTEGER DEFAULT 0` | :983 |
| `users` | `salary_period_days` | `INTEGER DEFAULT 7` | :981 |
| `users` | `seaweed_used_day` | `TEXT DEFAULT NULL` | :1223 |
| `users` | `seaweed_used_today` | `INTEGER DEFAULT 0` | :1222 |
| `users` | `shower_used_day` | `TEXT DEFAULT NULL` | :1252 |
| `users` | `shower_used_today` | `INTEGER DEFAULT 0` | :1253 |
| `users` | `special_blocked_until` | `TEXT DEFAULT NULL` | :1237 |
| `users` | `special_fails_today` | `INTEGER DEFAULT 0` | :1236 |
| `users` | `wing` | `TEXT` | :1417 |
| `users` | `xp_balance` | `INTEGER DEFAULT 0` | :960 |
| `water_fish` | `excluded` | `INTEGER DEFAULT 0` | :1180 |
| `water_fish` | `kind` | `TEXT DEFAULT 'fish'` | :1396 |
| `water_fish` | `super_rare` | `INTEGER DEFAULT 0` | :1399 |
| `wings` | `abbr` | `TEXT DEFAULT ''` | :1216 |
| `wings` | `callsign` | `TEXT DEFAULT ''` | :1218 |
| `wings` | `emoji` | `TEXT DEFAULT ''` | :1219 |
| `wings` | `name` | `TEXT DEFAULT ''` | :1217 |
| `wings` | `num` | `TEXT DEFAULT ''` | :1215 |
| `wings` | `sort_order` | `INTEGER DEFAULT 0` | :1220 |

## 2. Идемпотентные засевы и миграции данных

| Функция | Вызывается из main.py | Назначение (первая строка docstring) | db.py |
|---|---|---|---|
| `backfill_rank_statuses` | — | Разово выдать статусы по текущим званиям всех пилотов (войска и админ-звания). | :5650 |
| `ensure_achievements` | ✅ | Идемпотентно засевает награды-уровни достижений и синхронизирует их. | :12172 |
| `ensure_base_status` | — | Базовый статус «Турист» для каждого нового игрока. | :5887 |
| `ensure_base_statuses` | — | Создаёт базовые статусы иерархии, если их нет. | :5842 |
| `ensure_duel_items` | ✅ | Товары Дома Дуэлей: дуэльные перчатки (отдельный слот) и клубная карта. | :9888 |
| `ensure_dungeon_enemy_drops` | ✅ | Синхронизирует врагов существующего данжа с DEFAULT_DUNGEON (дропы, HP, награды, | :11707 |
| `ensure_dungeon_reservoir_items` | ✅ | Идемпотентно добавляет предметы водохранилища подземелья (v0.12.0). | :11611 |
| `ensure_dungeon_shop_items` | ✅ | Идемпотентно добавляет предметы данжа (зелье в магазин, трофеи) — для существующих БД. | :11226 |
| `ensure_fishing_enemies` | ✅ | Идемпотентно засевает врагов рыбалки (мутировавший моллюск) из MOLLUSK_SEED. | :8926 |
| `ensure_forest_enemies` | ✅ | Идемпотентно засевает врагов леса (кабан и Белый Волк Севера). | :8901 |
| `ensure_forest_items` | ✅ | Идемпотентно создаёт предметы леса (грибы, добыча кабана, жареные блюда, яд). | :8266 |
| `ensure_forest_mushrooms` | ✅ | Идемпотентно засевает пул грибов леса из FOREST_DEFAULTS. | :8419 |
| `ensure_forest_zones` | ✅ | Разовый перенос старого пула леса в зону поляны и засев пула опушки. | :8662 |
| `ensure_kvp_award` | ✅ | — | :10147 |
| `ensure_kvp_items` | ✅ | Обеспечивает эксклюзивный предмет К.В.П. — «Сержантскую трость». | :9861 |
| `ensure_kvp_user` | — | Гарантирует наличие строки прогресса К.В.П. для игрока. | :10334 |
| `ensure_life_items` | ✅ | Идемпотентно добавляет предметы жилья, мебели, семян, ресурсов и продовольствия. | :11432 |
| `ensure_logging_enemies` | ✅ | Идемпотентно засевает врагов Лесозаготовки (Змея и Неясыть). | :8408 |
| `ensure_logging_items` | ✅ | Идемпотентно создаёт предметы Лесозаготовки (топор, бревна, дропы). | :8376 |
| `ensure_market_license_item` | ✅ | Идемпотентно добавляет «Торговую лицензию» в магазин. | :9410 |
| `ensure_mine_enemies` | ✅ | Идемпотентно засевает врагов копи (Летучая мышь) из MINE_BAT_SEED. | :8367 |
| `ensure_mine_items` | ✅ | Идемпотентно создаёт предметы Железной копи (кирка, руда, самоцветы). | :8336 |
| `ensure_mollusk_items` | ✅ | Идемпотентно создаёт предметы моллюска (из его добычи и готового блюда). | :8932 |
| `ensure_player_housing` | — | Возвращает жильё игрока, создавая муниципальную квартиру для пилота при первом обращении. | :11828 |
| `ensure_rank_statuses_for_troops` | — | Выдать статус по текущему званию игрока (по войскам или админ-назначению). | :5638 |
| `ensure_recipe_shop_item` | — | Синхронизирует товар-рецепт «Рецепт: <name>» с рецептом (менеджер). | :12585 |
| `ensure_recipe_shop_items` | ✅ | Создаёт в магазине предметы-рецепты категории 'recipes'. | :13357 |
| `ensure_recipes` | ✅ | Идемпотентно засевает рецепты и синхронизирует уже существующие. | :12435 |
| `ensure_tourist_booklet` | ✅ | Создаёт предмет «Буклет туриста» и награду «Опытный турист», если их нет. | :10183 |
| `ensure_user_recipes_backfill` | ✅ | Разово открывает все рецепты существующим игрокам. | :13468 |
| `ensure_water_fish` | ✅ | Идемпотентно засевает water_fish из дефолтов. Правившие админом строки | :7866 |
| `migrate_legacy_junk` | ✅ | Переносит старые копии мусора (сапог, водоросли) из инвентаря в улов. | :7712 |
| `seed_default_items` | ✅ | Заполняет магазин базовым набором товаров, если он пуст и не было своих товаров. | :9584 |
| `seed_dungeon` | ✅ | — | :9739 |
| `seed_kvp` | ✅ | Создаёт тренировочный данж К.В.П. с врагами (Ефрейтор, Старший сержант), если его нет. | :9810 |
| `seed_locations` | — | Засеивает базовые локации города (Ратуша, Библиотека) как пример управляемого доступа. | :1572 |

## 3. Отдельные скрипты миграций

- `migrate_113.py` — Проверка миграций 0.19.0 на чистой БД: колонки polls, таблица rep_speeches.
- `migrate_113_old.py` — Миграция 0.19.0 поверх БД со старой схемой polls (без closes_at/is_archived).

