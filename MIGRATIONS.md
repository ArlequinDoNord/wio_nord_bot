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

Всего вызовов: **164**; таблиц: **23**.

| Таблица | Колонка | Тип / значение по умолчанию | db.py |
|---|---|---|---|
| `awards` | `achievement_key` | `TEXT DEFAULT NULL` | :1168 |
| `awards` | `achievement_level` | `INTEGER DEFAULT 0` | :1169 |
| `awards` | `bonus_attack` | `INTEGER DEFAULT 0` | :1147 |
| `awards` | `bonus_crit` | `INTEGER DEFAULT 0` | :1154 |
| `awards` | `bonus_defense` | `INTEGER DEFAULT 0` | :1148 |
| `awards` | `bonus_dodge` | `INTEGER DEFAULT 0` | :1149 |
| `awards` | `bonus_fishing` | `INTEGER DEFAULT 0` | :1150 |
| `awards` | `bonus_hp` | `INTEGER DEFAULT 0` | :1151 |
| `awards` | `bonus_json` | `TEXT DEFAULT '{}'` | :1170 |
| `awards` | `bonus_report_tax` | `INTEGER DEFAULT 0` | :1158 |
| `awards` | `bonus_shop_discount` | `INTEGER DEFAULT 0` | :1157 |
| `awards` | `image` | `TEXT` | :1146 |
| `awards` | `monthly_nm` | `INTEGER DEFAULT 0` | :1162 |
| `awards` | `reward_nm` | `INTEGER DEFAULT 0` | :1161 |
| `buildings` | `required_status` | `TEXT` | :928 |
| `dungeon_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1096 |
| `dungeon_enemies` | `admin_tuned` | `INTEGER DEFAULT 0` | :1118 |
| `dungeon_enemies` | `armor` | `INTEGER DEFAULT 0` | :1092 |
| `dungeon_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1334 |
| `dungeon_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1335 |
| `dungeon_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1094 |
| `dungeon_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1095 |
| `dungeon_enemies` | `damage_max` | `INTEGER DEFAULT 0` | :1091 |
| `dungeon_enemies` | `damage_min` | `INTEGER DEFAULT 0` | :1090 |
| `dungeon_enemies` | `description` | `TEXT` | :1088 |
| `dungeon_enemies` | `dodge` | `INTEGER DEFAULT 0` | :1089 |
| `dungeon_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1093 |
| `dungeon_enemies` | `drops` | `TEXT DEFAULT '[]'` | :1084 |
| `dungeon_enemies` | `frostbite_chance` | `INTEGER DEFAULT 0` | :1336 |
| `dungeon_enemies` | `image` | `TEXT` | :1085 |
| `dungeon_enemies` | `poison_chance` | `INTEGER DEFAULT 0` | :1086 |
| `dungeon_enemies` | `poison_dmg` | `INTEGER DEFAULT 0` | :1087 |
| `dungeons` | `is_training` | `INTEGER DEFAULT 0` | :1325 |
| `dungeons` | `photo_dawn` | `TEXT` | :1131 |
| `dungeons` | `photo_day` | `TEXT` | :1132 |
| `dungeons` | `photo_night` | `TEXT` | :1134 |
| `dungeons` | `photo_rope` | `TEXT` | :1137 |
| `dungeons` | `photo_sunset` | `TEXT` | :1133 |
| `dungeons` | `photo_water` | `TEXT` | :1136 |
| `dungeons` | `rooms_map` | `TEXT` | :1341 |
| `fish_catches` | `expires_at` | `TIMESTAMP` | :1207 |
| `fish_catches` | `kind` | `TEXT DEFAULT 'fish'` | :1347 |
| `fishing_enemies` | `armor` | `INTEGER DEFAULT 0` | :1107 |
| `fishing_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1105 |
| `fishing_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1106 |
| `forest_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1101 |
| `forest_enemies` | `armor` | `INTEGER DEFAULT 0` | :1097 |
| `forest_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1103 |
| `forest_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1104 |
| `forest_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1099 |
| `forest_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1100 |
| `forest_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1098 |
| `forest_mushrooms` | `zone` | `TEXT DEFAULT 'clearing'` | :1244 |
| `housing_slots` | `embedded` | `INTEGER DEFAULT 0` | :1275 |
| `inventory` | `expires_at` | `TIMESTAMP` | :1202 |
| `inventory` | `plant_data` | `TEXT` | :1204 |
| `items` | `armor` | `INTEGER DEFAULT 0` | :958 |
| `items` | `crit_chance` | `INTEGER DEFAULT 0` | :961 |
| `items` | `crit_mult` | `REAL DEFAULT 0` | :962 |
| `items` | `cure_frostbite` | `INTEGER DEFAULT 0` | :1338 |
| `items` | `cure_poison` | `INTEGER DEFAULT 0` | :1119 |
| `items` | `damage` | `INTEGER DEFAULT 0` | :1082 |
| `items` | `drink_effect` | `TEXT DEFAULT NULL` | :1190 |
| `items` | `equip_slot` | `TEXT` | :964 |
| `items` | `heal` | `INTEGER DEFAULT 0` | :1083 |
| `items` | `housing_slots` | `INTEGER` | :1430 |
| `items` | `housing_type` | `TEXT` | :1429 |
| `items` | `loot_only` | `INTEGER DEFAULT 0` | :1435 |
| `items` | `market_ok` | `INTEGER DEFAULT 0` | :1344 |
| `items` | `plant_name` | `TEXT` | :1354 |
| `items` | `regen` | `INTEGER DEFAULT 0` | :1129 |
| `items` | `required_status` | `TEXT` | :927 |
| `items` | `weapon_effect` | `TEXT` | :1365 |
| `items` | `weapon_effect_chance` | `INTEGER DEFAULT 0` | :1366 |
| `items` | `weapon_effect_dmg` | `INTEGER DEFAULT 0` | :1367 |
| `locations` | `clearing_photo` | `TEXT DEFAULT NULL` | :1234 |
| `locations` | `glade_photo` | `TEXT DEFAULT NULL` | :1233 |
| `locations` | `mine_level_photo` | `TEXT DEFAULT NULL` | :1237 |
| `locations` | `photo_dawn` | `TEXT` | :1121 |
| `locations` | `photo_day` | `TEXT` | :1122 |
| `locations` | `photo_night` | `TEXT` | :1124 |
| `locations` | `photo_sunset` | `TEXT` | :1123 |
| `locations` | `preview_photo` | `TEXT` | :1120 |
| `locations` | `season_photos` | `TEXT DEFAULT NULL` | :1230 |
| `locations` | `storage_photo` | `TEXT DEFAULT NULL` | :1239 |
| `locations` | `visits` | `INTEGER DEFAULT 0` | :1126 |
| `market_fish` | `base_price` | `INTEGER DEFAULT 0` | :1328 |
| `mine_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1113 |
| `mine_enemies` | `armor` | `INTEGER DEFAULT 0` | :1109 |
| `mine_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1114 |
| `mine_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1115 |
| `mine_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1111 |
| `mine_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1112 |
| `mine_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1110 |
| `nii_reports` | `photo2_file_id` | `TEXT DEFAULT NULL` | :1172 |
| `player_dungeon_run` | `loot_nm` | `INTEGER DEFAULT 0` | :1069 |
| `player_dungeon_run` | `started_at` | `TIMESTAMP DEFAULT CURRENT_TIMESTAMP` | :1070 |
| `player_housing` | `expansions_installed` | `INTEGER DEFAULT 0` | :1277 |
| `player_housing` | `housing_label` | `TEXT` | :1431 |
| `player_housing` | `housing_slots` | `INTEGER` | :1432 |
| `player_housing` | `tax_last_check` | `TEXT DEFAULT NULL` | :1329 |
| `player_housing` | `tax_unpaid_months` | `INTEGER DEFAULT 0` | :1330 |
| `polls` | `archived_day` | `TEXT DEFAULT ''` | :1293 |
| `polls` | `closed_at` | `TIMESTAMP` | :1200 |
| `polls` | `closed_by` | `INTEGER` | :1199 |
| `polls` | `closes_at` | `TIMESTAMP` | :1282 |
| `polls` | `is_archived` | `INTEGER DEFAULT 0` | :1292 |
| `reports` | `credited_troops` | `INTEGER` | :969 |
| `reports` | `paid` | `INTEGER DEFAULT 0` | :976 |
| `reports` | `total_troops` | `INTEGER DEFAULT 0` | :967 |
| `statuses` | `sort_order` | `INTEGER DEFAULT 0` | :929 |
| `users` | `about` | `TEXT DEFAULT ''` | :952 |
| `users` | `alcohol_strong_used_day` | `TEXT DEFAULT NULL` | :1194 |
| `users` | `alcohol_strong_used_today` | `INTEGER DEFAULT 0` | :1193 |
| `users` | `alcohol_weak_used_day` | `TEXT DEFAULT NULL` | :1192 |
| `users` | `alcohol_weak_used_today` | `INTEGER DEFAULT 0` | :1191 |
| `users` | `ap_recovery_day` | `TEXT DEFAULT NULL` | :1186 |
| `users` | `ap_restored_day` | `TEXT DEFAULT NULL` | :1073 |
| `users` | `ap_restored_today` | `INTEGER DEFAULT 0` | :1074 |
| `users` | `beer_used_day` | `TEXT DEFAULT NULL` | :1189 |
| `users` | `beer_used_today` | `INTEGER DEFAULT 0` | :1188 |
| `users` | `callsign` | `TEXT` | :1144 |
| `users` | `callsign_free_used` | `INTEGER DEFAULT 0` | :1327 |
| `users` | `duel_losses` | `INTEGER DEFAULT 0` | :1078 |
| `users` | `duel_rating` | `INTEGER DEFAULT 0` | :1076 |
| `users` | `duel_wins` | `INTEGER DEFAULT 0` | :1077 |
| `users` | `equipment` | `TEXT DEFAULT '{}'` | :953 |
| `users` | `fish_sold_day` | `TEXT DEFAULT NULL` | :1215 |
| `users` | `fish_sold_today` | `INTEGER DEFAULT 0` | :1216 |
| `users` | `fishing_bait` | `TEXT DEFAULT ''` | :1142 |
| `users` | `forest_attempts_since_boar` | `INTEGER DEFAULT 0` | :1218 |
| `users` | `forest_attempts_since_wolf` | `INTEGER DEFAULT 0` | :1220 |
| `users` | `forest_sold_day` | `TEXT DEFAULT NULL` | :1226 |
| `users` | `forest_sold_today` | `INTEGER DEFAULT 0` | :1227 |
| `users` | `fountain_used_day` | `TEXT DEFAULT NULL` | :1209 |
| `users` | `fountain_used_today` | `INTEGER DEFAULT 0` | :1210 |
| `users` | `last_active` | `REAL DEFAULT 0` | :1081 |
| `users` | `last_salary_date` | `TIMESTAMP` | :956 |
| `users` | `legioner` | `INTEGER DEFAULT 0` | :1372 |
| `users` | `market_license_expires` | `TEXT DEFAULT NULL` | :1326 |
| `users` | `mine_attempts_since_bat` | `INTEGER DEFAULT 0` | :1223 |
| `users` | `notify_enabled` | `INTEGER DEFAULT 1` | :950 |
| `users` | `profile_public` | `INTEGER DEFAULT 1` | :951 |
| `users` | `promoted_rank` | `TEXT` | :930 |
| `users` | `salary` | `INTEGER DEFAULT 0` | :954 |
| `users` | `salary_debt` | `INTEGER DEFAULT 0` | :957 |
| `users` | `salary_period_days` | `INTEGER DEFAULT 7` | :955 |
| `users` | `seaweed_used_day` | `TEXT DEFAULT NULL` | :1183 |
| `users` | `seaweed_used_today` | `INTEGER DEFAULT 0` | :1182 |
| `users` | `shower_used_day` | `TEXT DEFAULT NULL` | :1212 |
| `users` | `shower_used_today` | `INTEGER DEFAULT 0` | :1213 |
| `users` | `special_blocked_until` | `TEXT DEFAULT NULL` | :1197 |
| `users` | `special_fails_today` | `INTEGER DEFAULT 0` | :1196 |
| `users` | `wing` | `TEXT` | :1369 |
| `users` | `xp_balance` | `INTEGER DEFAULT 0` | :934 |
| `water_fish` | `excluded` | `INTEGER DEFAULT 0` | :1140 |
| `water_fish` | `kind` | `TEXT DEFAULT 'fish'` | :1348 |
| `water_fish` | `super_rare` | `INTEGER DEFAULT 0` | :1351 |
| `wings` | `abbr` | `TEXT DEFAULT ''` | :1176 |
| `wings` | `callsign` | `TEXT DEFAULT ''` | :1178 |
| `wings` | `emoji` | `TEXT DEFAULT ''` | :1179 |
| `wings` | `name` | `TEXT DEFAULT ''` | :1177 |
| `wings` | `num` | `TEXT DEFAULT ''` | :1175 |
| `wings` | `sort_order` | `INTEGER DEFAULT 0` | :1180 |

## 2. Идемпотентные засевы и миграции данных

| Функция | Вызывается из main.py | Назначение (первая строка docstring) | db.py |
|---|---|---|---|
| `backfill_rank_statuses` | — | Разово выдать статусы по текущим званиям всех пилотов (войска и админ-звания). | :5545 |
| `ensure_achievements` | ✅ | Идемпотентно засевает награды-уровни достижений и синхронизирует их. | :11860 |
| `ensure_base_status` | — | Базовый статус «Турист» для каждого нового игрока. | :5782 |
| `ensure_base_statuses` | — | Создаёт базовые статусы иерархии, если их нет. | :5737 |
| `ensure_duel_items` | ✅ | Товары Дома Дуэлей: дуэльные перчатки (отдельный слот) и клубная карта. | :9578 |
| `ensure_dungeon_enemy_drops` | ✅ | Синхронизирует врагов существующего данжа с DEFAULT_DUNGEON (дропы, HP, награды, | :11397 |
| `ensure_dungeon_reservoir_items` | ✅ | Идемпотентно добавляет предметы водохранилища подземелья (v0.12.0). | :11301 |
| `ensure_dungeon_shop_items` | ✅ | Идемпотентно добавляет предметы данжа (зелье в магазин, трофеи) — для существующих БД. | :10916 |
| `ensure_fishing_enemies` | ✅ | Идемпотентно засевает врагов рыбалки (мутировавший моллюск) из MOLLUSK_SEED. | :8747 |
| `ensure_forest_enemies` | ✅ | Идемпотентно засевает врагов леса (кабан и Белый Волк Севера). | :8722 |
| `ensure_forest_items` | ✅ | Идемпотентно создаёт предметы леса (грибы, добыча кабана, жареные блюда, яд). | :8131 |
| `ensure_forest_mushrooms` | ✅ | Идемпотентно засевает пул грибов леса из FOREST_DEFAULTS. | :8241 |
| `ensure_forest_zones` | ✅ | Разовый перенос старого пула леса в зону поляны и засев пула опушки. | :8484 |
| `ensure_kvp_award` | ✅ | — | :9837 |
| `ensure_kvp_items` | ✅ | Обеспечивает эксклюзивный предмет К.В.П. — «Сержантскую трость». | :9551 |
| `ensure_kvp_user` | — | Гарантирует наличие строки прогресса К.В.П. для игрока. | :10024 |
| `ensure_life_items` | ✅ | Идемпотентно добавляет предметы жилья, мебели, семян, ресурсов и продовольствия. | :11122 |
| `ensure_market_license_item` | ✅ | Идемпотентно добавляет «Торговую лицензию» в магазин. | :9134 |
| `ensure_mine_enemies` | ✅ | Идемпотентно засевает врагов копи (Летучая мышь) из MINE_BAT_SEED. | :8232 |
| `ensure_mine_items` | ✅ | Идемпотентно создаёт предметы Железной копи (кирка, руда, самоцветы). | :8201 |
| `ensure_mollusk_items` | ✅ | Идемпотентно создаёт предметы моллюска (из его добычи и готового блюда). | :8753 |
| `ensure_player_housing` | — | Возвращает жильё игрока, создавая муниципальную квартиру для пилота при первом обращении. | :11516 |
| `ensure_rank_statuses_for_troops` | — | Выдать статус по текущему званию игрока (по войскам или админ-назначению). | :5533 |
| `ensure_recipe_shop_item` | — | Синхронизирует товар-рецепт «Рецепт: <name>» с рецептом (менеджер). | :12273 |
| `ensure_recipe_shop_items` | ✅ | Создаёт в магазине предметы-рецепты категории 'recipes'. | :13045 |
| `ensure_recipes` | ✅ | Идемпотентно засевает рецепты и синхронизирует уже существующие. | :12123 |
| `ensure_tourist_booklet` | ✅ | Создаёт предмет «Буклет туриста» и награду «Опытный турист», если их нет. | :9873 |
| `ensure_user_recipes_backfill` | ✅ | Разово открывает все рецепты существующим игрокам. | :13156 |
| `ensure_water_fish` | ✅ | Идемпотентно засевает water_fish из дефолтов. Правившие админом строки | :7731 |
| `migrate_legacy_junk` | ✅ | Переносит старые копии мусора (сапог, водоросли) из инвентаря в улов. | :7577 |
| `seed_default_items` | ✅ | Заполняет магазин базовым набором товаров, если он пуст и не было своих товаров. | :9308 |
| `seed_dungeon` | ✅ | — | :9432 |
| `seed_kvp` | ✅ | Создаёт тренировочный данж К.В.П. с врагами (Ефрейтор, Старший сержант), если его нет. | :9501 |
| `seed_locations` | — | Засеивает базовые локации города (Ратуша, Библиотека) как пример управляемого доступа. | :1474 |

## 3. Отдельные скрипты миграций

- `migrate_113.py` — Проверка миграций 0.19.0 на чистой БД: колонки polls, таблица rep_speeches.
- `migrate_113_old.py` — Миграция 0.19.0 поверх БД со старой схемой polls (без closes_at/is_archived).

