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
| `awards` | `achievement_key` | `TEXT DEFAULT NULL` | :1260 |
| `awards` | `achievement_level` | `INTEGER DEFAULT 0` | :1261 |
| `awards` | `bonus_attack` | `INTEGER DEFAULT 0` | :1239 |
| `awards` | `bonus_crit` | `INTEGER DEFAULT 0` | :1246 |
| `awards` | `bonus_defense` | `INTEGER DEFAULT 0` | :1240 |
| `awards` | `bonus_dodge` | `INTEGER DEFAULT 0` | :1241 |
| `awards` | `bonus_fishing` | `INTEGER DEFAULT 0` | :1242 |
| `awards` | `bonus_hp` | `INTEGER DEFAULT 0` | :1243 |
| `awards` | `bonus_json` | `TEXT DEFAULT '{}'` | :1262 |
| `awards` | `bonus_report_tax` | `INTEGER DEFAULT 0` | :1250 |
| `awards` | `bonus_shop_discount` | `INTEGER DEFAULT 0` | :1249 |
| `awards` | `image` | `TEXT` | :1238 |
| `awards` | `monthly_nm` | `INTEGER DEFAULT 0` | :1254 |
| `awards` | `reward_nm` | `INTEGER DEFAULT 0` | :1253 |
| `buildings` | `required_status` | `TEXT` | :1006 |
| `dungeon_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1174 |
| `dungeon_enemies` | `admin_tuned` | `INTEGER DEFAULT 0` | :1210 |
| `dungeon_enemies` | `armor` | `INTEGER DEFAULT 0` | :1170 |
| `dungeon_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1434 |
| `dungeon_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1435 |
| `dungeon_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1172 |
| `dungeon_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1173 |
| `dungeon_enemies` | `damage_max` | `INTEGER DEFAULT 0` | :1169 |
| `dungeon_enemies` | `damage_min` | `INTEGER DEFAULT 0` | :1168 |
| `dungeon_enemies` | `description` | `TEXT` | :1166 |
| `dungeon_enemies` | `dodge` | `INTEGER DEFAULT 0` | :1167 |
| `dungeon_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1171 |
| `dungeon_enemies` | `drops` | `TEXT DEFAULT '[]'` | :1162 |
| `dungeon_enemies` | `frostbite_chance` | `INTEGER DEFAULT 0` | :1436 |
| `dungeon_enemies` | `image` | `TEXT` | :1163 |
| `dungeon_enemies` | `poison_chance` | `INTEGER DEFAULT 0` | :1164 |
| `dungeon_enemies` | `poison_dmg` | `INTEGER DEFAULT 0` | :1165 |
| `dungeons` | `is_training` | `INTEGER DEFAULT 0` | :1425 |
| `dungeons` | `photo_dawn` | `TEXT` | :1223 |
| `dungeons` | `photo_day` | `TEXT` | :1224 |
| `dungeons` | `photo_night` | `TEXT` | :1226 |
| `dungeons` | `photo_rope` | `TEXT` | :1229 |
| `dungeons` | `photo_sunset` | `TEXT` | :1225 |
| `dungeons` | `photo_water` | `TEXT` | :1228 |
| `dungeons` | `rooms_map` | `TEXT` | :1441 |
| `fish_catches` | `expires_at` | `TIMESTAMP` | :1299 |
| `fish_catches` | `kind` | `TEXT DEFAULT 'fish'` | :1447 |
| `fishing_enemies` | `armor` | `INTEGER DEFAULT 0` | :1185 |
| `fishing_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1183 |
| `fishing_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1184 |
| `forest_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1179 |
| `forest_enemies` | `armor` | `INTEGER DEFAULT 0` | :1175 |
| `forest_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1181 |
| `forest_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1182 |
| `forest_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1177 |
| `forest_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1178 |
| `forest_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1176 |
| `forest_mushrooms` | `zone` | `TEXT DEFAULT 'clearing'` | :1344 |
| `housing_slots` | `embedded` | `INTEGER DEFAULT 0` | :1375 |
| `inventory` | `expires_at` | `TIMESTAMP` | :1294 |
| `inventory` | `plant_data` | `TEXT` | :1296 |
| `items` | `armor` | `INTEGER DEFAULT 0` | :1036 |
| `items` | `crit_chance` | `INTEGER DEFAULT 0` | :1039 |
| `items` | `crit_mult` | `REAL DEFAULT 0` | :1040 |
| `items` | `cure_frostbite` | `INTEGER DEFAULT 0` | :1438 |
| `items` | `cure_poison` | `INTEGER DEFAULT 0` | :1211 |
| `items` | `damage` | `INTEGER DEFAULT 0` | :1160 |
| `items` | `drink_effect` | `TEXT DEFAULT NULL` | :1282 |
| `items` | `equip_slot` | `TEXT` | :1042 |
| `items` | `heal` | `INTEGER DEFAULT 0` | :1161 |
| `items` | `housing_slots` | `INTEGER` | :1530 |
| `items` | `housing_type` | `TEXT` | :1529 |
| `items` | `loot_only` | `INTEGER DEFAULT 0` | :1535 |
| `items` | `market_ok` | `INTEGER DEFAULT 0` | :1444 |
| `items` | `plant_name` | `TEXT` | :1454 |
| `items` | `regen` | `INTEGER DEFAULT 0` | :1221 |
| `items` | `required_status` | `TEXT` | :1005 |
| `items` | `weapon_effect` | `TEXT` | :1465 |
| `items` | `weapon_effect_chance` | `INTEGER DEFAULT 0` | :1466 |
| `items` | `weapon_effect_dmg` | `INTEGER DEFAULT 0` | :1467 |
| `locations` | `clearing_photo` | `TEXT DEFAULT NULL` | :1330 |
| `locations` | `glade_photo` | `TEXT DEFAULT NULL` | :1329 |
| `locations` | `logging_photo` | `TEXT DEFAULT NULL` | :1339 |
| `locations` | `mine_level_photo` | `TEXT DEFAULT NULL` | :1333 |
| `locations` | `photo_dawn` | `TEXT` | :1213 |
| `locations` | `photo_day` | `TEXT` | :1214 |
| `locations` | `photo_night` | `TEXT` | :1216 |
| `locations` | `photo_sunset` | `TEXT` | :1215 |
| `locations` | `preview_photo` | `TEXT` | :1212 |
| `locations` | `season_photos` | `TEXT DEFAULT NULL` | :1326 |
| `locations` | `storage_photo` | `TEXT DEFAULT NULL` | :1335 |
| `locations` | `visits` | `INTEGER DEFAULT 0` | :1218 |
| `logging_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1200 |
| `logging_enemies` | `armor` | `INTEGER DEFAULT 0` | :1196 |
| `logging_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1198 |
| `logging_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1199 |
| `logging_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1197 |
| `market_fish` | `base_price` | `INTEGER DEFAULT 0` | :1428 |
| `mine_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1191 |
| `mine_enemies` | `armor` | `INTEGER DEFAULT 0` | :1187 |
| `mine_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1192 |
| `mine_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1193 |
| `mine_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1189 |
| `mine_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1190 |
| `mine_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1188 |
| `nii_reports` | `photo2_file_id` | `TEXT DEFAULT NULL` | :1264 |
| `player_dungeon_run` | `loot_nm` | `INTEGER DEFAULT 0` | :1147 |
| `player_dungeon_run` | `started_at` | `TIMESTAMP DEFAULT CURRENT_TIMESTAMP` | :1148 |
| `player_housing` | `expansions_installed` | `INTEGER DEFAULT 0` | :1377 |
| `player_housing` | `housing_label` | `TEXT` | :1531 |
| `player_housing` | `housing_slots` | `INTEGER` | :1532 |
| `player_housing` | `tax_last_check` | `TEXT DEFAULT NULL` | :1429 |
| `player_housing` | `tax_unpaid_months` | `INTEGER DEFAULT 0` | :1430 |
| `polls` | `archived_day` | `TEXT DEFAULT ''` | :1393 |
| `polls` | `closed_at` | `TIMESTAMP` | :1292 |
| `polls` | `closed_by` | `INTEGER` | :1291 |
| `polls` | `closes_at` | `TIMESTAMP` | :1382 |
| `polls` | `is_archived` | `INTEGER DEFAULT 0` | :1392 |
| `reports` | `credited_troops` | `INTEGER` | :1047 |
| `reports` | `paid` | `INTEGER DEFAULT 0` | :1054 |
| `reports` | `total_troops` | `INTEGER DEFAULT 0` | :1045 |
| `statuses` | `sort_order` | `INTEGER DEFAULT 0` | :1007 |
| `users` | `about` | `TEXT DEFAULT ''` | :1030 |
| `users` | `alcohol_strong_used_day` | `TEXT DEFAULT NULL` | :1286 |
| `users` | `alcohol_strong_used_today` | `INTEGER DEFAULT 0` | :1285 |
| `users` | `alcohol_weak_used_day` | `TEXT DEFAULT NULL` | :1284 |
| `users` | `alcohol_weak_used_today` | `INTEGER DEFAULT 0` | :1283 |
| `users` | `ap_recovery_day` | `TEXT DEFAULT NULL` | :1278 |
| `users` | `ap_restored_day` | `TEXT DEFAULT NULL` | :1151 |
| `users` | `ap_restored_today` | `INTEGER DEFAULT 0` | :1152 |
| `users` | `beer_used_day` | `TEXT DEFAULT NULL` | :1281 |
| `users` | `beer_used_today` | `INTEGER DEFAULT 0` | :1280 |
| `users` | `callsign` | `TEXT` | :1236 |
| `users` | `callsign_free_used` | `INTEGER DEFAULT 0` | :1427 |
| `users` | `duel_losses` | `INTEGER DEFAULT 0` | :1156 |
| `users` | `duel_rating` | `INTEGER DEFAULT 0` | :1154 |
| `users` | `duel_wins` | `INTEGER DEFAULT 0` | :1155 |
| `users` | `equipment` | `TEXT DEFAULT '{}'` | :1031 |
| `users` | `fish_sold_day` | `TEXT DEFAULT NULL` | :1307 |
| `users` | `fish_sold_today` | `INTEGER DEFAULT 0` | :1308 |
| `users` | `fishing_bait` | `TEXT DEFAULT ''` | :1234 |
| `users` | `forest_attempts_since_boar` | `INTEGER DEFAULT 0` | :1310 |
| `users` | `forest_attempts_since_wolf` | `INTEGER DEFAULT 0` | :1312 |
| `users` | `forest_sold_day` | `TEXT DEFAULT NULL` | :1322 |
| `users` | `forest_sold_today` | `INTEGER DEFAULT 0` | :1323 |
| `users` | `fountain_used_day` | `TEXT DEFAULT NULL` | :1301 |
| `users` | `fountain_used_today` | `INTEGER DEFAULT 0` | :1302 |
| `users` | `last_active` | `REAL DEFAULT 0` | :1159 |
| `users` | `last_salary_date` | `TIMESTAMP` | :1034 |
| `users` | `legioner` | `INTEGER DEFAULT 0` | :1472 |
| `users` | `logging_attempts_since_owl` | `INTEGER DEFAULT 0` | :1319 |
| `users` | `logging_attempts_since_snake` | `INTEGER DEFAULT 0` | :1318 |
| `users` | `market_license_expires` | `TEXT DEFAULT NULL` | :1426 |
| `users` | `mine_attempts_since_bat` | `INTEGER DEFAULT 0` | :1315 |
| `users` | `notify_enabled` | `INTEGER DEFAULT 1` | :1028 |
| `users` | `profile_public` | `INTEGER DEFAULT 1` | :1029 |
| `users` | `promoted_rank` | `TEXT` | :1008 |
| `users` | `salary` | `INTEGER DEFAULT 0` | :1032 |
| `users` | `salary_debt` | `INTEGER DEFAULT 0` | :1035 |
| `users` | `salary_period_days` | `INTEGER DEFAULT 7` | :1033 |
| `users` | `seaweed_used_day` | `TEXT DEFAULT NULL` | :1275 |
| `users` | `seaweed_used_today` | `INTEGER DEFAULT 0` | :1274 |
| `users` | `shower_used_day` | `TEXT DEFAULT NULL` | :1304 |
| `users` | `shower_used_today` | `INTEGER DEFAULT 0` | :1305 |
| `users` | `special_blocked_until` | `TEXT DEFAULT NULL` | :1289 |
| `users` | `special_fails_today` | `INTEGER DEFAULT 0` | :1288 |
| `users` | `wing` | `TEXT` | :1469 |
| `users` | `xp_balance` | `INTEGER DEFAULT 0` | :1012 |
| `water_fish` | `excluded` | `INTEGER DEFAULT 0` | :1232 |
| `water_fish` | `kind` | `TEXT DEFAULT 'fish'` | :1448 |
| `water_fish` | `super_rare` | `INTEGER DEFAULT 0` | :1451 |
| `wings` | `abbr` | `TEXT DEFAULT ''` | :1268 |
| `wings` | `callsign` | `TEXT DEFAULT ''` | :1270 |
| `wings` | `emoji` | `TEXT DEFAULT ''` | :1271 |
| `wings` | `name` | `TEXT DEFAULT ''` | :1269 |
| `wings` | `num` | `TEXT DEFAULT ''` | :1267 |
| `wings` | `sort_order` | `INTEGER DEFAULT 0` | :1272 |

## 2. Идемпотентные засевы и миграции данных

| Функция | Вызывается из main.py | Назначение (первая строка docstring) | db.py |
|---|---|---|---|
| `backfill_rank_statuses` | — | Разово выдать статусы по текущим званиям всех пилотов (войска и админ-звания). | :5734 |
| `ensure_achievements` | ✅ | Идемпотентно засевает награды-уровни достижений и синхронизирует их. | :12267 |
| `ensure_base_status` | — | Базовый статус «Турист» для каждого нового игрока. | :5971 |
| `ensure_base_statuses` | — | Создаёт базовые статусы иерархии, если их нет. | :5926 |
| `ensure_duel_items` | ✅ | Товары Дома Дуэлей: дуэльные перчатки (отдельный слот) и клубная карта. | :9983 |
| `ensure_dungeon_enemy_drops` | ✅ | Синхронизирует врагов существующего данжа с DEFAULT_DUNGEON (дропы, HP, награды, | :11802 |
| `ensure_dungeon_reservoir_items` | ✅ | Идемпотентно добавляет предметы водохранилища подземелья (v0.12.0). | :11706 |
| `ensure_dungeon_shop_items` | ✅ | Идемпотентно добавляет предметы данжа (зелье в магазин, трофеи) — для существующих БД. | :11321 |
| `ensure_fishing_enemies` | ✅ | Идемпотентно засевает врагов рыбалки (мутировавший моллюск) из MOLLUSK_SEED. | :9021 |
| `ensure_forest_enemies` | ✅ | Идемпотентно засевает врагов леса (кабан и Белый Волк Севера). | :8996 |
| `ensure_forest_items` | ✅ | Идемпотентно создаёт предметы леса (грибы, добыча кабана, жареные блюда, яд). | :8350 |
| `ensure_forest_mushrooms` | ✅ | Идемпотентно засевает пул грибов леса из FOREST_DEFAULTS. | :8514 |
| `ensure_forest_zones` | ✅ | Разовый перенос старого пула леса в зону поляны и засев пула опушки. | :8757 |
| `ensure_kvp_award` | ✅ | — | :10242 |
| `ensure_kvp_items` | ✅ | Обеспечивает эксклюзивный предмет К.В.П. — «Сержантскую трость». | :9956 |
| `ensure_kvp_user` | — | Гарантирует наличие строки прогресса К.В.П. для игрока. | :10429 |
| `ensure_life_items` | ✅ | Идемпотентно добавляет предметы жилья, мебели, семян, ресурсов и продовольствия. | :11527 |
| `ensure_logging_enemies` | ✅ | Идемпотентно засевает врагов Лесозаготовки (Змея и Неясыть). | :8503 |
| `ensure_logging_items` | ✅ | Идемпотентно создаёт предметы Лесозаготовки (топор, бревна, дропы). | :8460 |
| `ensure_market_license_item` | ✅ | Идемпотентно добавляет «Торговую лицензию» в магазин. | :9505 |
| `ensure_mine_enemies` | ✅ | Идемпотентно засевает врагов копи (Летучая мышь) из MINE_BAT_SEED. | :8451 |
| `ensure_mine_items` | ✅ | Идемпотентно создаёт предметы Железной копи (кирка, руда, самоцветы). | :8420 |
| `ensure_mollusk_items` | ✅ | Идемпотентно создаёт предметы моллюска (из его добычи и готового блюда). | :9027 |
| `ensure_player_housing` | — | Возвращает жильё игрока, создавая муниципальную квартиру для пилота при первом обращении. | :11923 |
| `ensure_rank_statuses_for_troops` | — | Выдать статус по текущему званию игрока (по войскам или админ-назначению). | :5722 |
| `ensure_recipe_shop_item` | — | Синхронизирует товар-рецепт «Рецепт: <name>» с рецептом (менеджер). | :12680 |
| `ensure_recipe_shop_items` | ✅ | Создаёт в магазине предметы-рецепты категории 'recipes'. | :13552 |
| `ensure_recipes` | ✅ | Идемпотентно засевает рецепты и синхронизирует уже существующие. | :12530 |
| `ensure_tourist_booklet` | ✅ | Создаёт предмет «Буклет туриста» и награду «Опытный турист», если их нет. | :10278 |
| `ensure_user_recipes_backfill` | ✅ | Разово открывает все рецепты существующим игрокам. | :13663 |
| `ensure_water_fish` | ✅ | Идемпотентно засевает water_fish из дефолтов. Правившие админом строки | :7950 |
| `migrate_legacy_junk` | ✅ | Переносит старые копии мусора (сапог, водоросли) из инвентаря в улов. | :7796 |
| `seed_default_items` | ✅ | Заполняет магазин базовым набором товаров, если он пуст и не было своих товаров. | :9679 |
| `seed_dungeon` | ✅ | — | :9834 |
| `seed_kvp` | ✅ | Создаёт тренировочный данж К.В.П. с врагами (Ефрейтор, Старший сержант), если его нет. | :9905 |
| `seed_locations` | — | Засеивает базовые локации города (Ратуша, Библиотека) как пример управляемого доступа. | :1656 |

## 3. Отдельные скрипты миграций

- `migrate_113.py` — Проверка миграций 0.19.0 на чистой БД: колонки polls, таблица rep_speeches.
- `migrate_113_old.py` — Миграция 0.19.0 поверх БД со старой схемой polls (без closes_at/is_archived).

