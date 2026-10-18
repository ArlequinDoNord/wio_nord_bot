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
| `awards` | `achievement_key` | `TEXT DEFAULT NULL` | :1167 |
| `awards` | `achievement_level` | `INTEGER DEFAULT 0` | :1168 |
| `awards` | `bonus_attack` | `INTEGER DEFAULT 0` | :1146 |
| `awards` | `bonus_crit` | `INTEGER DEFAULT 0` | :1153 |
| `awards` | `bonus_defense` | `INTEGER DEFAULT 0` | :1147 |
| `awards` | `bonus_dodge` | `INTEGER DEFAULT 0` | :1148 |
| `awards` | `bonus_fishing` | `INTEGER DEFAULT 0` | :1149 |
| `awards` | `bonus_hp` | `INTEGER DEFAULT 0` | :1150 |
| `awards` | `bonus_json` | `TEXT DEFAULT '{}'` | :1169 |
| `awards` | `bonus_report_tax` | `INTEGER DEFAULT 0` | :1157 |
| `awards` | `bonus_shop_discount` | `INTEGER DEFAULT 0` | :1156 |
| `awards` | `image` | `TEXT` | :1145 |
| `awards` | `monthly_nm` | `INTEGER DEFAULT 0` | :1161 |
| `awards` | `reward_nm` | `INTEGER DEFAULT 0` | :1160 |
| `buildings` | `required_status` | `TEXT` | :927 |
| `dungeon_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1095 |
| `dungeon_enemies` | `admin_tuned` | `INTEGER DEFAULT 0` | :1117 |
| `dungeon_enemies` | `armor` | `INTEGER DEFAULT 0` | :1091 |
| `dungeon_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1333 |
| `dungeon_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1334 |
| `dungeon_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1093 |
| `dungeon_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1094 |
| `dungeon_enemies` | `damage_max` | `INTEGER DEFAULT 0` | :1090 |
| `dungeon_enemies` | `damage_min` | `INTEGER DEFAULT 0` | :1089 |
| `dungeon_enemies` | `description` | `TEXT` | :1087 |
| `dungeon_enemies` | `dodge` | `INTEGER DEFAULT 0` | :1088 |
| `dungeon_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1092 |
| `dungeon_enemies` | `drops` | `TEXT DEFAULT '[]'` | :1083 |
| `dungeon_enemies` | `frostbite_chance` | `INTEGER DEFAULT 0` | :1335 |
| `dungeon_enemies` | `image` | `TEXT` | :1084 |
| `dungeon_enemies` | `poison_chance` | `INTEGER DEFAULT 0` | :1085 |
| `dungeon_enemies` | `poison_dmg` | `INTEGER DEFAULT 0` | :1086 |
| `dungeons` | `is_training` | `INTEGER DEFAULT 0` | :1324 |
| `dungeons` | `photo_dawn` | `TEXT` | :1130 |
| `dungeons` | `photo_day` | `TEXT` | :1131 |
| `dungeons` | `photo_night` | `TEXT` | :1133 |
| `dungeons` | `photo_rope` | `TEXT` | :1136 |
| `dungeons` | `photo_sunset` | `TEXT` | :1132 |
| `dungeons` | `photo_water` | `TEXT` | :1135 |
| `dungeons` | `rooms_map` | `TEXT` | :1340 |
| `fish_catches` | `expires_at` | `TIMESTAMP` | :1206 |
| `fish_catches` | `kind` | `TEXT DEFAULT 'fish'` | :1346 |
| `fishing_enemies` | `armor` | `INTEGER DEFAULT 0` | :1106 |
| `fishing_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1104 |
| `fishing_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1105 |
| `forest_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1100 |
| `forest_enemies` | `armor` | `INTEGER DEFAULT 0` | :1096 |
| `forest_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1102 |
| `forest_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1103 |
| `forest_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1098 |
| `forest_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1099 |
| `forest_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1097 |
| `forest_mushrooms` | `zone` | `TEXT DEFAULT 'clearing'` | :1243 |
| `housing_slots` | `embedded` | `INTEGER DEFAULT 0` | :1274 |
| `inventory` | `expires_at` | `TIMESTAMP` | :1201 |
| `inventory` | `plant_data` | `TEXT` | :1203 |
| `items` | `armor` | `INTEGER DEFAULT 0` | :957 |
| `items` | `crit_chance` | `INTEGER DEFAULT 0` | :960 |
| `items` | `crit_mult` | `REAL DEFAULT 0` | :961 |
| `items` | `cure_frostbite` | `INTEGER DEFAULT 0` | :1337 |
| `items` | `cure_poison` | `INTEGER DEFAULT 0` | :1118 |
| `items` | `damage` | `INTEGER DEFAULT 0` | :1081 |
| `items` | `drink_effect` | `TEXT DEFAULT NULL` | :1189 |
| `items` | `equip_slot` | `TEXT` | :963 |
| `items` | `heal` | `INTEGER DEFAULT 0` | :1082 |
| `items` | `housing_slots` | `INTEGER` | :1429 |
| `items` | `housing_type` | `TEXT` | :1428 |
| `items` | `loot_only` | `INTEGER DEFAULT 0` | :1434 |
| `items` | `market_ok` | `INTEGER DEFAULT 0` | :1343 |
| `items` | `plant_name` | `TEXT` | :1353 |
| `items` | `regen` | `INTEGER DEFAULT 0` | :1128 |
| `items` | `required_status` | `TEXT` | :926 |
| `items` | `weapon_effect` | `TEXT` | :1364 |
| `items` | `weapon_effect_chance` | `INTEGER DEFAULT 0` | :1365 |
| `items` | `weapon_effect_dmg` | `INTEGER DEFAULT 0` | :1366 |
| `locations` | `clearing_photo` | `TEXT DEFAULT NULL` | :1233 |
| `locations` | `glade_photo` | `TEXT DEFAULT NULL` | :1232 |
| `locations` | `mine_level_photo` | `TEXT DEFAULT NULL` | :1236 |
| `locations` | `photo_dawn` | `TEXT` | :1120 |
| `locations` | `photo_day` | `TEXT` | :1121 |
| `locations` | `photo_night` | `TEXT` | :1123 |
| `locations` | `photo_sunset` | `TEXT` | :1122 |
| `locations` | `preview_photo` | `TEXT` | :1119 |
| `locations` | `season_photos` | `TEXT DEFAULT NULL` | :1229 |
| `locations` | `storage_photo` | `TEXT DEFAULT NULL` | :1238 |
| `locations` | `visits` | `INTEGER DEFAULT 0` | :1125 |
| `market_fish` | `base_price` | `INTEGER DEFAULT 0` | :1327 |
| `mine_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1112 |
| `mine_enemies` | `armor` | `INTEGER DEFAULT 0` | :1108 |
| `mine_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1113 |
| `mine_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1114 |
| `mine_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1110 |
| `mine_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1111 |
| `mine_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1109 |
| `nii_reports` | `photo2_file_id` | `TEXT DEFAULT NULL` | :1171 |
| `player_dungeon_run` | `loot_nm` | `INTEGER DEFAULT 0` | :1068 |
| `player_dungeon_run` | `started_at` | `TIMESTAMP DEFAULT CURRENT_TIMESTAMP` | :1069 |
| `player_housing` | `expansions_installed` | `INTEGER DEFAULT 0` | :1276 |
| `player_housing` | `housing_label` | `TEXT` | :1430 |
| `player_housing` | `housing_slots` | `INTEGER` | :1431 |
| `player_housing` | `tax_last_check` | `TEXT DEFAULT NULL` | :1328 |
| `player_housing` | `tax_unpaid_months` | `INTEGER DEFAULT 0` | :1329 |
| `polls` | `archived_day` | `TEXT DEFAULT ''` | :1292 |
| `polls` | `closed_at` | `TIMESTAMP` | :1199 |
| `polls` | `closed_by` | `INTEGER` | :1198 |
| `polls` | `closes_at` | `TIMESTAMP` | :1281 |
| `polls` | `is_archived` | `INTEGER DEFAULT 0` | :1291 |
| `reports` | `credited_troops` | `INTEGER` | :968 |
| `reports` | `paid` | `INTEGER DEFAULT 0` | :975 |
| `reports` | `total_troops` | `INTEGER DEFAULT 0` | :966 |
| `statuses` | `sort_order` | `INTEGER DEFAULT 0` | :928 |
| `users` | `about` | `TEXT DEFAULT ''` | :951 |
| `users` | `alcohol_strong_used_day` | `TEXT DEFAULT NULL` | :1193 |
| `users` | `alcohol_strong_used_today` | `INTEGER DEFAULT 0` | :1192 |
| `users` | `alcohol_weak_used_day` | `TEXT DEFAULT NULL` | :1191 |
| `users` | `alcohol_weak_used_today` | `INTEGER DEFAULT 0` | :1190 |
| `users` | `ap_recovery_day` | `TEXT DEFAULT NULL` | :1185 |
| `users` | `ap_restored_day` | `TEXT DEFAULT NULL` | :1072 |
| `users` | `ap_restored_today` | `INTEGER DEFAULT 0` | :1073 |
| `users` | `beer_used_day` | `TEXT DEFAULT NULL` | :1188 |
| `users` | `beer_used_today` | `INTEGER DEFAULT 0` | :1187 |
| `users` | `callsign` | `TEXT` | :1143 |
| `users` | `callsign_free_used` | `INTEGER DEFAULT 0` | :1326 |
| `users` | `duel_losses` | `INTEGER DEFAULT 0` | :1077 |
| `users` | `duel_rating` | `INTEGER DEFAULT 0` | :1075 |
| `users` | `duel_wins` | `INTEGER DEFAULT 0` | :1076 |
| `users` | `equipment` | `TEXT DEFAULT '{}'` | :952 |
| `users` | `fish_sold_day` | `TEXT DEFAULT NULL` | :1214 |
| `users` | `fish_sold_today` | `INTEGER DEFAULT 0` | :1215 |
| `users` | `fishing_bait` | `TEXT DEFAULT ''` | :1141 |
| `users` | `forest_attempts_since_boar` | `INTEGER DEFAULT 0` | :1217 |
| `users` | `forest_attempts_since_wolf` | `INTEGER DEFAULT 0` | :1219 |
| `users` | `forest_sold_day` | `TEXT DEFAULT NULL` | :1225 |
| `users` | `forest_sold_today` | `INTEGER DEFAULT 0` | :1226 |
| `users` | `fountain_used_day` | `TEXT DEFAULT NULL` | :1208 |
| `users` | `fountain_used_today` | `INTEGER DEFAULT 0` | :1209 |
| `users` | `last_active` | `REAL DEFAULT 0` | :1080 |
| `users` | `last_salary_date` | `TIMESTAMP` | :955 |
| `users` | `legioner` | `INTEGER DEFAULT 0` | :1371 |
| `users` | `market_license_expires` | `TEXT DEFAULT NULL` | :1325 |
| `users` | `mine_attempts_since_bat` | `INTEGER DEFAULT 0` | :1222 |
| `users` | `notify_enabled` | `INTEGER DEFAULT 1` | :949 |
| `users` | `profile_public` | `INTEGER DEFAULT 1` | :950 |
| `users` | `promoted_rank` | `TEXT` | :929 |
| `users` | `salary` | `INTEGER DEFAULT 0` | :953 |
| `users` | `salary_debt` | `INTEGER DEFAULT 0` | :956 |
| `users` | `salary_period_days` | `INTEGER DEFAULT 7` | :954 |
| `users` | `seaweed_used_day` | `TEXT DEFAULT NULL` | :1182 |
| `users` | `seaweed_used_today` | `INTEGER DEFAULT 0` | :1181 |
| `users` | `shower_used_day` | `TEXT DEFAULT NULL` | :1211 |
| `users` | `shower_used_today` | `INTEGER DEFAULT 0` | :1212 |
| `users` | `special_blocked_until` | `TEXT DEFAULT NULL` | :1196 |
| `users` | `special_fails_today` | `INTEGER DEFAULT 0` | :1195 |
| `users` | `wing` | `TEXT` | :1368 |
| `users` | `xp_balance` | `INTEGER DEFAULT 0` | :933 |
| `water_fish` | `excluded` | `INTEGER DEFAULT 0` | :1139 |
| `water_fish` | `kind` | `TEXT DEFAULT 'fish'` | :1347 |
| `water_fish` | `super_rare` | `INTEGER DEFAULT 0` | :1350 |
| `wings` | `abbr` | `TEXT DEFAULT ''` | :1175 |
| `wings` | `callsign` | `TEXT DEFAULT ''` | :1177 |
| `wings` | `emoji` | `TEXT DEFAULT ''` | :1178 |
| `wings` | `name` | `TEXT DEFAULT ''` | :1176 |
| `wings` | `num` | `TEXT DEFAULT ''` | :1174 |
| `wings` | `sort_order` | `INTEGER DEFAULT 0` | :1179 |

## 2. Идемпотентные засевы и миграции данных

| Функция | Вызывается из main.py | Назначение (первая строка docstring) | db.py |
|---|---|---|---|
| `backfill_rank_statuses` | — | Разово выдать статусы по текущим званиям всех пилотов (войска и админ-звания). | :5524 |
| `ensure_achievements` | ✅ | Идемпотентно засевает награды-уровни достижений и синхронизирует их. | :11832 |
| `ensure_base_status` | — | Базовый статус «Турист» для каждого нового игрока. | :5761 |
| `ensure_base_statuses` | — | Создаёт базовые статусы иерархии, если их нет. | :5716 |
| `ensure_duel_items` | ✅ | Товары Дома Дуэлей: дуэльные перчатки (отдельный слот) и клубная карта. | :9550 |
| `ensure_dungeon_enemy_drops` | ✅ | Синхронизирует врагов существующего данжа с DEFAULT_DUNGEON (дропы, HP, награды, | :11369 |
| `ensure_dungeon_reservoir_items` | ✅ | Идемпотентно добавляет предметы водохранилища подземелья (v0.12.0). | :11273 |
| `ensure_dungeon_shop_items` | ✅ | Идемпотентно добавляет предметы данжа (зелье в магазин, трофеи) — для существующих БД. | :10888 |
| `ensure_fishing_enemies` | ✅ | Идемпотентно засевает врагов рыбалки (мутировавший моллюск) из MOLLUSK_SEED. | :8719 |
| `ensure_forest_enemies` | ✅ | Идемпотентно засевает врагов леса (кабан и Белый Волк Севера). | :8694 |
| `ensure_forest_items` | ✅ | Идемпотентно создаёт предметы леса (грибы, добыча кабана, жареные блюда, яд). | :8103 |
| `ensure_forest_mushrooms` | ✅ | Идемпотентно засевает пул грибов леса из FOREST_DEFAULTS. | :8213 |
| `ensure_forest_zones` | ✅ | Разовый перенос старого пула леса в зону поляны и засев пула опушки. | :8456 |
| `ensure_kvp_award` | ✅ | — | :9809 |
| `ensure_kvp_items` | ✅ | Обеспечивает эксклюзивный предмет К.В.П. — «Сержантскую трость». | :9523 |
| `ensure_kvp_user` | — | Гарантирует наличие строки прогресса К.В.П. для игрока. | :9996 |
| `ensure_life_items` | ✅ | Идемпотентно добавляет предметы жилья, мебели, семян, ресурсов и продовольствия. | :11094 |
| `ensure_market_license_item` | ✅ | Идемпотентно добавляет «Торговую лицензию» в магазин. | :9106 |
| `ensure_mine_enemies` | ✅ | Идемпотентно засевает врагов копи (Летучая мышь) из MINE_BAT_SEED. | :8204 |
| `ensure_mine_items` | ✅ | Идемпотентно создаёт предметы Железной копи (кирка, руда, самоцветы). | :8173 |
| `ensure_mollusk_items` | ✅ | Идемпотентно создаёт предметы моллюска (из его добычи и готового блюда). | :8725 |
| `ensure_player_housing` | — | Возвращает жильё игрока, создавая муниципальную квартиру для пилота при первом обращении. | :11488 |
| `ensure_rank_statuses_for_troops` | — | Выдать статус по текущему званию игрока (по войскам или админ-назначению). | :5512 |
| `ensure_recipe_shop_item` | — | Синхронизирует товар-рецепт «Рецепт: <name>» с рецептом (менеджер). | :12245 |
| `ensure_recipe_shop_items` | ✅ | Создаёт в магазине предметы-рецепты категории 'recipes'. | :13017 |
| `ensure_recipes` | ✅ | Идемпотентно засевает рецепты и синхронизирует уже существующие. | :12095 |
| `ensure_tourist_booklet` | ✅ | Создаёт предмет «Буклет туриста» и награду «Опытный турист», если их нет. | :9845 |
| `ensure_user_recipes_backfill` | ✅ | Разово открывает все рецепты существующим игрокам. | :13128 |
| `ensure_water_fish` | ✅ | Идемпотентно засевает water_fish из дефолтов. Правившие админом строки | :7703 |
| `migrate_legacy_junk` | ✅ | Переносит старые копии мусора (сапог, водоросли) из инвентаря в улов. | :7549 |
| `seed_default_items` | ✅ | Заполняет магазин базовым набором товаров, если он пуст и не было своих товаров. | :9280 |
| `seed_dungeon` | ✅ | — | :9404 |
| `seed_kvp` | ✅ | Создаёт тренировочный данж К.В.П. с врагами (Ефрейтор, Старший сержант), если его нет. | :9473 |
| `seed_locations` | — | Засеивает базовые локации города (Ратуша, Библиотека) как пример управляемого доступа. | :1453 |

## 3. Отдельные скрипты миграций

- `migrate_113.py` — Проверка миграций 0.19.0 на чистой БД: колонки polls, таблица rep_speeches.
- `migrate_113_old.py` — Миграция 0.19.0 поверх БД со старой схемой polls (без closes_at/is_archived).

