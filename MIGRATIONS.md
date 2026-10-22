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
| `awards` | `achievement_key` | `TEXT DEFAULT NULL` | :1240 |
| `awards` | `achievement_level` | `INTEGER DEFAULT 0` | :1241 |
| `awards` | `bonus_attack` | `INTEGER DEFAULT 0` | :1219 |
| `awards` | `bonus_crit` | `INTEGER DEFAULT 0` | :1226 |
| `awards` | `bonus_defense` | `INTEGER DEFAULT 0` | :1220 |
| `awards` | `bonus_dodge` | `INTEGER DEFAULT 0` | :1221 |
| `awards` | `bonus_fishing` | `INTEGER DEFAULT 0` | :1222 |
| `awards` | `bonus_hp` | `INTEGER DEFAULT 0` | :1223 |
| `awards` | `bonus_json` | `TEXT DEFAULT '{}'` | :1242 |
| `awards` | `bonus_report_tax` | `INTEGER DEFAULT 0` | :1230 |
| `awards` | `bonus_shop_discount` | `INTEGER DEFAULT 0` | :1229 |
| `awards` | `image` | `TEXT` | :1218 |
| `awards` | `monthly_nm` | `INTEGER DEFAULT 0` | :1234 |
| `awards` | `reward_nm` | `INTEGER DEFAULT 0` | :1233 |
| `buildings` | `required_status` | `TEXT` | :986 |
| `dungeon_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1154 |
| `dungeon_enemies` | `admin_tuned` | `INTEGER DEFAULT 0` | :1190 |
| `dungeon_enemies` | `armor` | `INTEGER DEFAULT 0` | :1150 |
| `dungeon_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1414 |
| `dungeon_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1415 |
| `dungeon_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1152 |
| `dungeon_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1153 |
| `dungeon_enemies` | `damage_max` | `INTEGER DEFAULT 0` | :1149 |
| `dungeon_enemies` | `damage_min` | `INTEGER DEFAULT 0` | :1148 |
| `dungeon_enemies` | `description` | `TEXT` | :1146 |
| `dungeon_enemies` | `dodge` | `INTEGER DEFAULT 0` | :1147 |
| `dungeon_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1151 |
| `dungeon_enemies` | `drops` | `TEXT DEFAULT '[]'` | :1142 |
| `dungeon_enemies` | `frostbite_chance` | `INTEGER DEFAULT 0` | :1416 |
| `dungeon_enemies` | `image` | `TEXT` | :1143 |
| `dungeon_enemies` | `poison_chance` | `INTEGER DEFAULT 0` | :1144 |
| `dungeon_enemies` | `poison_dmg` | `INTEGER DEFAULT 0` | :1145 |
| `dungeons` | `is_training` | `INTEGER DEFAULT 0` | :1405 |
| `dungeons` | `photo_dawn` | `TEXT` | :1203 |
| `dungeons` | `photo_day` | `TEXT` | :1204 |
| `dungeons` | `photo_night` | `TEXT` | :1206 |
| `dungeons` | `photo_rope` | `TEXT` | :1209 |
| `dungeons` | `photo_sunset` | `TEXT` | :1205 |
| `dungeons` | `photo_water` | `TEXT` | :1208 |
| `dungeons` | `rooms_map` | `TEXT` | :1421 |
| `fish_catches` | `expires_at` | `TIMESTAMP` | :1279 |
| `fish_catches` | `kind` | `TEXT DEFAULT 'fish'` | :1427 |
| `fishing_enemies` | `armor` | `INTEGER DEFAULT 0` | :1165 |
| `fishing_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1163 |
| `fishing_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1164 |
| `forest_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1159 |
| `forest_enemies` | `armor` | `INTEGER DEFAULT 0` | :1155 |
| `forest_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1161 |
| `forest_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1162 |
| `forest_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1157 |
| `forest_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1158 |
| `forest_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1156 |
| `forest_mushrooms` | `zone` | `TEXT DEFAULT 'clearing'` | :1324 |
| `housing_slots` | `embedded` | `INTEGER DEFAULT 0` | :1355 |
| `inventory` | `expires_at` | `TIMESTAMP` | :1274 |
| `inventory` | `plant_data` | `TEXT` | :1276 |
| `items` | `armor` | `INTEGER DEFAULT 0` | :1016 |
| `items` | `crit_chance` | `INTEGER DEFAULT 0` | :1019 |
| `items` | `crit_mult` | `REAL DEFAULT 0` | :1020 |
| `items` | `cure_frostbite` | `INTEGER DEFAULT 0` | :1418 |
| `items` | `cure_poison` | `INTEGER DEFAULT 0` | :1191 |
| `items` | `damage` | `INTEGER DEFAULT 0` | :1140 |
| `items` | `drink_effect` | `TEXT DEFAULT NULL` | :1262 |
| `items` | `equip_slot` | `TEXT` | :1022 |
| `items` | `heal` | `INTEGER DEFAULT 0` | :1141 |
| `items` | `housing_slots` | `INTEGER` | :1510 |
| `items` | `housing_type` | `TEXT` | :1509 |
| `items` | `loot_only` | `INTEGER DEFAULT 0` | :1515 |
| `items` | `market_ok` | `INTEGER DEFAULT 0` | :1424 |
| `items` | `plant_name` | `TEXT` | :1434 |
| `items` | `regen` | `INTEGER DEFAULT 0` | :1201 |
| `items` | `required_status` | `TEXT` | :985 |
| `items` | `weapon_effect` | `TEXT` | :1445 |
| `items` | `weapon_effect_chance` | `INTEGER DEFAULT 0` | :1446 |
| `items` | `weapon_effect_dmg` | `INTEGER DEFAULT 0` | :1447 |
| `locations` | `clearing_photo` | `TEXT DEFAULT NULL` | :1310 |
| `locations` | `glade_photo` | `TEXT DEFAULT NULL` | :1309 |
| `locations` | `logging_photo` | `TEXT DEFAULT NULL` | :1319 |
| `locations` | `mine_level_photo` | `TEXT DEFAULT NULL` | :1313 |
| `locations` | `photo_dawn` | `TEXT` | :1193 |
| `locations` | `photo_day` | `TEXT` | :1194 |
| `locations` | `photo_night` | `TEXT` | :1196 |
| `locations` | `photo_sunset` | `TEXT` | :1195 |
| `locations` | `preview_photo` | `TEXT` | :1192 |
| `locations` | `season_photos` | `TEXT DEFAULT NULL` | :1306 |
| `locations` | `storage_photo` | `TEXT DEFAULT NULL` | :1315 |
| `locations` | `visits` | `INTEGER DEFAULT 0` | :1198 |
| `logging_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1180 |
| `logging_enemies` | `armor` | `INTEGER DEFAULT 0` | :1176 |
| `logging_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1178 |
| `logging_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1179 |
| `logging_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1177 |
| `market_fish` | `base_price` | `INTEGER DEFAULT 0` | :1408 |
| `mine_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1171 |
| `mine_enemies` | `armor` | `INTEGER DEFAULT 0` | :1167 |
| `mine_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1172 |
| `mine_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1173 |
| `mine_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1169 |
| `mine_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1170 |
| `mine_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1168 |
| `nii_reports` | `photo2_file_id` | `TEXT DEFAULT NULL` | :1244 |
| `player_dungeon_run` | `loot_nm` | `INTEGER DEFAULT 0` | :1127 |
| `player_dungeon_run` | `started_at` | `TIMESTAMP DEFAULT CURRENT_TIMESTAMP` | :1128 |
| `player_housing` | `expansions_installed` | `INTEGER DEFAULT 0` | :1357 |
| `player_housing` | `housing_label` | `TEXT` | :1511 |
| `player_housing` | `housing_slots` | `INTEGER` | :1512 |
| `player_housing` | `tax_last_check` | `TEXT DEFAULT NULL` | :1409 |
| `player_housing` | `tax_unpaid_months` | `INTEGER DEFAULT 0` | :1410 |
| `polls` | `archived_day` | `TEXT DEFAULT ''` | :1373 |
| `polls` | `closed_at` | `TIMESTAMP` | :1272 |
| `polls` | `closed_by` | `INTEGER` | :1271 |
| `polls` | `closes_at` | `TIMESTAMP` | :1362 |
| `polls` | `is_archived` | `INTEGER DEFAULT 0` | :1372 |
| `reports` | `credited_troops` | `INTEGER` | :1027 |
| `reports` | `paid` | `INTEGER DEFAULT 0` | :1034 |
| `reports` | `total_troops` | `INTEGER DEFAULT 0` | :1025 |
| `statuses` | `sort_order` | `INTEGER DEFAULT 0` | :987 |
| `users` | `about` | `TEXT DEFAULT ''` | :1010 |
| `users` | `alcohol_strong_used_day` | `TEXT DEFAULT NULL` | :1266 |
| `users` | `alcohol_strong_used_today` | `INTEGER DEFAULT 0` | :1265 |
| `users` | `alcohol_weak_used_day` | `TEXT DEFAULT NULL` | :1264 |
| `users` | `alcohol_weak_used_today` | `INTEGER DEFAULT 0` | :1263 |
| `users` | `ap_recovery_day` | `TEXT DEFAULT NULL` | :1258 |
| `users` | `ap_restored_day` | `TEXT DEFAULT NULL` | :1131 |
| `users` | `ap_restored_today` | `INTEGER DEFAULT 0` | :1132 |
| `users` | `beer_used_day` | `TEXT DEFAULT NULL` | :1261 |
| `users` | `beer_used_today` | `INTEGER DEFAULT 0` | :1260 |
| `users` | `callsign` | `TEXT` | :1216 |
| `users` | `callsign_free_used` | `INTEGER DEFAULT 0` | :1407 |
| `users` | `duel_losses` | `INTEGER DEFAULT 0` | :1136 |
| `users` | `duel_rating` | `INTEGER DEFAULT 0` | :1134 |
| `users` | `duel_wins` | `INTEGER DEFAULT 0` | :1135 |
| `users` | `equipment` | `TEXT DEFAULT '{}'` | :1011 |
| `users` | `fish_sold_day` | `TEXT DEFAULT NULL` | :1287 |
| `users` | `fish_sold_today` | `INTEGER DEFAULT 0` | :1288 |
| `users` | `fishing_bait` | `TEXT DEFAULT ''` | :1214 |
| `users` | `forest_attempts_since_boar` | `INTEGER DEFAULT 0` | :1290 |
| `users` | `forest_attempts_since_wolf` | `INTEGER DEFAULT 0` | :1292 |
| `users` | `forest_sold_day` | `TEXT DEFAULT NULL` | :1302 |
| `users` | `forest_sold_today` | `INTEGER DEFAULT 0` | :1303 |
| `users` | `fountain_used_day` | `TEXT DEFAULT NULL` | :1281 |
| `users` | `fountain_used_today` | `INTEGER DEFAULT 0` | :1282 |
| `users` | `last_active` | `REAL DEFAULT 0` | :1139 |
| `users` | `last_salary_date` | `TIMESTAMP` | :1014 |
| `users` | `legioner` | `INTEGER DEFAULT 0` | :1452 |
| `users` | `logging_attempts_since_owl` | `INTEGER DEFAULT 0` | :1299 |
| `users` | `logging_attempts_since_snake` | `INTEGER DEFAULT 0` | :1298 |
| `users` | `market_license_expires` | `TEXT DEFAULT NULL` | :1406 |
| `users` | `mine_attempts_since_bat` | `INTEGER DEFAULT 0` | :1295 |
| `users` | `notify_enabled` | `INTEGER DEFAULT 1` | :1008 |
| `users` | `profile_public` | `INTEGER DEFAULT 1` | :1009 |
| `users` | `promoted_rank` | `TEXT` | :988 |
| `users` | `salary` | `INTEGER DEFAULT 0` | :1012 |
| `users` | `salary_debt` | `INTEGER DEFAULT 0` | :1015 |
| `users` | `salary_period_days` | `INTEGER DEFAULT 7` | :1013 |
| `users` | `seaweed_used_day` | `TEXT DEFAULT NULL` | :1255 |
| `users` | `seaweed_used_today` | `INTEGER DEFAULT 0` | :1254 |
| `users` | `shower_used_day` | `TEXT DEFAULT NULL` | :1284 |
| `users` | `shower_used_today` | `INTEGER DEFAULT 0` | :1285 |
| `users` | `special_blocked_until` | `TEXT DEFAULT NULL` | :1269 |
| `users` | `special_fails_today` | `INTEGER DEFAULT 0` | :1268 |
| `users` | `wing` | `TEXT` | :1449 |
| `users` | `xp_balance` | `INTEGER DEFAULT 0` | :992 |
| `water_fish` | `excluded` | `INTEGER DEFAULT 0` | :1212 |
| `water_fish` | `kind` | `TEXT DEFAULT 'fish'` | :1428 |
| `water_fish` | `super_rare` | `INTEGER DEFAULT 0` | :1431 |
| `wings` | `abbr` | `TEXT DEFAULT ''` | :1248 |
| `wings` | `callsign` | `TEXT DEFAULT ''` | :1250 |
| `wings` | `emoji` | `TEXT DEFAULT ''` | :1251 |
| `wings` | `name` | `TEXT DEFAULT ''` | :1249 |
| `wings` | `num` | `TEXT DEFAULT ''` | :1247 |
| `wings` | `sort_order` | `INTEGER DEFAULT 0` | :1252 |

## 2. Идемпотентные засевы и миграции данных

| Функция | Вызывается из main.py | Назначение (первая строка docstring) | db.py |
|---|---|---|---|
| `backfill_rank_statuses` | — | Разово выдать статусы по текущим званиям всех пилотов (войска и админ-звания). | :5714 |
| `ensure_achievements` | ✅ | Идемпотентно засевает награды-уровни достижений и синхронизирует их. | :12247 |
| `ensure_base_status` | — | Базовый статус «Турист» для каждого нового игрока. | :5951 |
| `ensure_base_statuses` | — | Создаёт базовые статусы иерархии, если их нет. | :5906 |
| `ensure_duel_items` | ✅ | Товары Дома Дуэлей: дуэльные перчатки (отдельный слот) и клубная карта. | :9963 |
| `ensure_dungeon_enemy_drops` | ✅ | Синхронизирует врагов существующего данжа с DEFAULT_DUNGEON (дропы, HP, награды, | :11782 |
| `ensure_dungeon_reservoir_items` | ✅ | Идемпотентно добавляет предметы водохранилища подземелья (v0.12.0). | :11686 |
| `ensure_dungeon_shop_items` | ✅ | Идемпотентно добавляет предметы данжа (зелье в магазин, трофеи) — для существующих БД. | :11301 |
| `ensure_fishing_enemies` | ✅ | Идемпотентно засевает врагов рыбалки (мутировавший моллюск) из MOLLUSK_SEED. | :9001 |
| `ensure_forest_enemies` | ✅ | Идемпотентно засевает врагов леса (кабан и Белый Волк Севера). | :8976 |
| `ensure_forest_items` | ✅ | Идемпотентно создаёт предметы леса (грибы, добыча кабана, жареные блюда, яд). | :8330 |
| `ensure_forest_mushrooms` | ✅ | Идемпотентно засевает пул грибов леса из FOREST_DEFAULTS. | :8494 |
| `ensure_forest_zones` | ✅ | Разовый перенос старого пула леса в зону поляны и засев пула опушки. | :8737 |
| `ensure_kvp_award` | ✅ | — | :10222 |
| `ensure_kvp_items` | ✅ | Обеспечивает эксклюзивный предмет К.В.П. — «Сержантскую трость». | :9936 |
| `ensure_kvp_user` | — | Гарантирует наличие строки прогресса К.В.П. для игрока. | :10409 |
| `ensure_life_items` | ✅ | Идемпотентно добавляет предметы жилья, мебели, семян, ресурсов и продовольствия. | :11507 |
| `ensure_logging_enemies` | ✅ | Идемпотентно засевает врагов Лесозаготовки (Змея и Неясыть). | :8483 |
| `ensure_logging_items` | ✅ | Идемпотентно создаёт предметы Лесозаготовки (топор, бревна, дропы). | :8440 |
| `ensure_market_license_item` | ✅ | Идемпотентно добавляет «Торговую лицензию» в магазин. | :9485 |
| `ensure_mine_enemies` | ✅ | Идемпотентно засевает врагов копи (Летучая мышь) из MINE_BAT_SEED. | :8431 |
| `ensure_mine_items` | ✅ | Идемпотентно создаёт предметы Железной копи (кирка, руда, самоцветы). | :8400 |
| `ensure_mollusk_items` | ✅ | Идемпотентно создаёт предметы моллюска (из его добычи и готового блюда). | :9007 |
| `ensure_player_housing` | — | Возвращает жильё игрока, создавая муниципальную квартиру для пилота при первом обращении. | :11903 |
| `ensure_rank_statuses_for_troops` | — | Выдать статус по текущему званию игрока (по войскам или админ-назначению). | :5702 |
| `ensure_recipe_shop_item` | — | Синхронизирует товар-рецепт «Рецепт: <name>» с рецептом (менеджер). | :12660 |
| `ensure_recipe_shop_items` | ✅ | Создаёт в магазине предметы-рецепты категории 'recipes'. | :13432 |
| `ensure_recipes` | ✅ | Идемпотентно засевает рецепты и синхронизирует уже существующие. | :12510 |
| `ensure_tourist_booklet` | ✅ | Создаёт предмет «Буклет туриста» и награду «Опытный турист», если их нет. | :10258 |
| `ensure_user_recipes_backfill` | ✅ | Разово открывает все рецепты существующим игрокам. | :13543 |
| `ensure_water_fish` | ✅ | Идемпотентно засевает water_fish из дефолтов. Правившие админом строки | :7930 |
| `migrate_legacy_junk` | ✅ | Переносит старые копии мусора (сапог, водоросли) из инвентаря в улов. | :7776 |
| `seed_default_items` | ✅ | Заполняет магазин базовым набором товаров, если он пуст и не было своих товаров. | :9659 |
| `seed_dungeon` | ✅ | — | :9814 |
| `seed_kvp` | ✅ | Создаёт тренировочный данж К.В.П. с врагами (Ефрейтор, Старший сержант), если его нет. | :9885 |
| `seed_locations` | — | Засеивает базовые локации города (Ратуша, Библиотека) как пример управляемого доступа. | :1636 |

## 3. Отдельные скрипты миграций

- `migrate_113.py` — Проверка миграций 0.19.0 на чистой БД: колонки polls, таблица rep_speeches.
- `migrate_113_old.py` — Миграция 0.19.0 поверх БД со старой схемой polls (без closes_at/is_archived).

