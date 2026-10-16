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
| `awards` | `achievement_key` | `TEXT DEFAULT NULL` | :1166 |
| `awards` | `achievement_level` | `INTEGER DEFAULT 0` | :1167 |
| `awards` | `bonus_attack` | `INTEGER DEFAULT 0` | :1145 |
| `awards` | `bonus_crit` | `INTEGER DEFAULT 0` | :1152 |
| `awards` | `bonus_defense` | `INTEGER DEFAULT 0` | :1146 |
| `awards` | `bonus_dodge` | `INTEGER DEFAULT 0` | :1147 |
| `awards` | `bonus_fishing` | `INTEGER DEFAULT 0` | :1148 |
| `awards` | `bonus_hp` | `INTEGER DEFAULT 0` | :1149 |
| `awards` | `bonus_json` | `TEXT DEFAULT '{}'` | :1168 |
| `awards` | `bonus_report_tax` | `INTEGER DEFAULT 0` | :1156 |
| `awards` | `bonus_shop_discount` | `INTEGER DEFAULT 0` | :1155 |
| `awards` | `image` | `TEXT` | :1144 |
| `awards` | `monthly_nm` | `INTEGER DEFAULT 0` | :1160 |
| `awards` | `reward_nm` | `INTEGER DEFAULT 0` | :1159 |
| `buildings` | `required_status` | `TEXT` | :926 |
| `dungeon_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1094 |
| `dungeon_enemies` | `admin_tuned` | `INTEGER DEFAULT 0` | :1116 |
| `dungeon_enemies` | `armor` | `INTEGER DEFAULT 0` | :1090 |
| `dungeon_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1332 |
| `dungeon_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1333 |
| `dungeon_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1092 |
| `dungeon_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1093 |
| `dungeon_enemies` | `damage_max` | `INTEGER DEFAULT 0` | :1089 |
| `dungeon_enemies` | `damage_min` | `INTEGER DEFAULT 0` | :1088 |
| `dungeon_enemies` | `description` | `TEXT` | :1086 |
| `dungeon_enemies` | `dodge` | `INTEGER DEFAULT 0` | :1087 |
| `dungeon_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1091 |
| `dungeon_enemies` | `drops` | `TEXT DEFAULT '[]'` | :1082 |
| `dungeon_enemies` | `frostbite_chance` | `INTEGER DEFAULT 0` | :1334 |
| `dungeon_enemies` | `image` | `TEXT` | :1083 |
| `dungeon_enemies` | `poison_chance` | `INTEGER DEFAULT 0` | :1084 |
| `dungeon_enemies` | `poison_dmg` | `INTEGER DEFAULT 0` | :1085 |
| `dungeons` | `is_training` | `INTEGER DEFAULT 0` | :1323 |
| `dungeons` | `photo_dawn` | `TEXT` | :1129 |
| `dungeons` | `photo_day` | `TEXT` | :1130 |
| `dungeons` | `photo_night` | `TEXT` | :1132 |
| `dungeons` | `photo_rope` | `TEXT` | :1135 |
| `dungeons` | `photo_sunset` | `TEXT` | :1131 |
| `dungeons` | `photo_water` | `TEXT` | :1134 |
| `dungeons` | `rooms_map` | `TEXT` | :1339 |
| `fish_catches` | `expires_at` | `TIMESTAMP` | :1205 |
| `fish_catches` | `kind` | `TEXT DEFAULT 'fish'` | :1345 |
| `fishing_enemies` | `armor` | `INTEGER DEFAULT 0` | :1105 |
| `fishing_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1103 |
| `fishing_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1104 |
| `forest_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1099 |
| `forest_enemies` | `armor` | `INTEGER DEFAULT 0` | :1095 |
| `forest_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1101 |
| `forest_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1102 |
| `forest_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1097 |
| `forest_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1098 |
| `forest_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1096 |
| `forest_mushrooms` | `zone` | `TEXT DEFAULT 'clearing'` | :1242 |
| `housing_slots` | `embedded` | `INTEGER DEFAULT 0` | :1273 |
| `inventory` | `expires_at` | `TIMESTAMP` | :1200 |
| `inventory` | `plant_data` | `TEXT` | :1202 |
| `items` | `armor` | `INTEGER DEFAULT 0` | :956 |
| `items` | `crit_chance` | `INTEGER DEFAULT 0` | :959 |
| `items` | `crit_mult` | `REAL DEFAULT 0` | :960 |
| `items` | `cure_frostbite` | `INTEGER DEFAULT 0` | :1336 |
| `items` | `cure_poison` | `INTEGER DEFAULT 0` | :1117 |
| `items` | `damage` | `INTEGER DEFAULT 0` | :1080 |
| `items` | `drink_effect` | `TEXT DEFAULT NULL` | :1188 |
| `items` | `equip_slot` | `TEXT` | :962 |
| `items` | `heal` | `INTEGER DEFAULT 0` | :1081 |
| `items` | `housing_slots` | `INTEGER` | :1428 |
| `items` | `housing_type` | `TEXT` | :1427 |
| `items` | `loot_only` | `INTEGER DEFAULT 0` | :1433 |
| `items` | `market_ok` | `INTEGER DEFAULT 0` | :1342 |
| `items` | `plant_name` | `TEXT` | :1352 |
| `items` | `regen` | `INTEGER DEFAULT 0` | :1127 |
| `items` | `required_status` | `TEXT` | :925 |
| `items` | `weapon_effect` | `TEXT` | :1363 |
| `items` | `weapon_effect_chance` | `INTEGER DEFAULT 0` | :1364 |
| `items` | `weapon_effect_dmg` | `INTEGER DEFAULT 0` | :1365 |
| `locations` | `clearing_photo` | `TEXT DEFAULT NULL` | :1232 |
| `locations` | `glade_photo` | `TEXT DEFAULT NULL` | :1231 |
| `locations` | `mine_level_photo` | `TEXT DEFAULT NULL` | :1235 |
| `locations` | `photo_dawn` | `TEXT` | :1119 |
| `locations` | `photo_day` | `TEXT` | :1120 |
| `locations` | `photo_night` | `TEXT` | :1122 |
| `locations` | `photo_sunset` | `TEXT` | :1121 |
| `locations` | `preview_photo` | `TEXT` | :1118 |
| `locations` | `season_photos` | `TEXT DEFAULT NULL` | :1228 |
| `locations` | `storage_photo` | `TEXT DEFAULT NULL` | :1237 |
| `locations` | `visits` | `INTEGER DEFAULT 0` | :1124 |
| `market_fish` | `base_price` | `INTEGER DEFAULT 0` | :1326 |
| `mine_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1111 |
| `mine_enemies` | `armor` | `INTEGER DEFAULT 0` | :1107 |
| `mine_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1112 |
| `mine_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1113 |
| `mine_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1109 |
| `mine_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1110 |
| `mine_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1108 |
| `nii_reports` | `photo2_file_id` | `TEXT DEFAULT NULL` | :1170 |
| `player_dungeon_run` | `loot_nm` | `INTEGER DEFAULT 0` | :1067 |
| `player_dungeon_run` | `started_at` | `TIMESTAMP DEFAULT CURRENT_TIMESTAMP` | :1068 |
| `player_housing` | `expansions_installed` | `INTEGER DEFAULT 0` | :1275 |
| `player_housing` | `housing_label` | `TEXT` | :1429 |
| `player_housing` | `housing_slots` | `INTEGER` | :1430 |
| `player_housing` | `tax_last_check` | `TEXT DEFAULT NULL` | :1327 |
| `player_housing` | `tax_unpaid_months` | `INTEGER DEFAULT 0` | :1328 |
| `polls` | `archived_day` | `TEXT DEFAULT ''` | :1291 |
| `polls` | `closed_at` | `TIMESTAMP` | :1198 |
| `polls` | `closed_by` | `INTEGER` | :1197 |
| `polls` | `closes_at` | `TIMESTAMP` | :1280 |
| `polls` | `is_archived` | `INTEGER DEFAULT 0` | :1290 |
| `reports` | `credited_troops` | `INTEGER` | :967 |
| `reports` | `paid` | `INTEGER DEFAULT 0` | :974 |
| `reports` | `total_troops` | `INTEGER DEFAULT 0` | :965 |
| `statuses` | `sort_order` | `INTEGER DEFAULT 0` | :927 |
| `users` | `about` | `TEXT DEFAULT ''` | :950 |
| `users` | `alcohol_strong_used_day` | `TEXT DEFAULT NULL` | :1192 |
| `users` | `alcohol_strong_used_today` | `INTEGER DEFAULT 0` | :1191 |
| `users` | `alcohol_weak_used_day` | `TEXT DEFAULT NULL` | :1190 |
| `users` | `alcohol_weak_used_today` | `INTEGER DEFAULT 0` | :1189 |
| `users` | `ap_recovery_day` | `TEXT DEFAULT NULL` | :1184 |
| `users` | `ap_restored_day` | `TEXT DEFAULT NULL` | :1071 |
| `users` | `ap_restored_today` | `INTEGER DEFAULT 0` | :1072 |
| `users` | `beer_used_day` | `TEXT DEFAULT NULL` | :1187 |
| `users` | `beer_used_today` | `INTEGER DEFAULT 0` | :1186 |
| `users` | `callsign` | `TEXT` | :1142 |
| `users` | `callsign_free_used` | `INTEGER DEFAULT 0` | :1325 |
| `users` | `duel_losses` | `INTEGER DEFAULT 0` | :1076 |
| `users` | `duel_rating` | `INTEGER DEFAULT 0` | :1074 |
| `users` | `duel_wins` | `INTEGER DEFAULT 0` | :1075 |
| `users` | `equipment` | `TEXT DEFAULT '{}'` | :951 |
| `users` | `fish_sold_day` | `TEXT DEFAULT NULL` | :1213 |
| `users` | `fish_sold_today` | `INTEGER DEFAULT 0` | :1214 |
| `users` | `fishing_bait` | `TEXT DEFAULT ''` | :1140 |
| `users` | `forest_attempts_since_boar` | `INTEGER DEFAULT 0` | :1216 |
| `users` | `forest_attempts_since_wolf` | `INTEGER DEFAULT 0` | :1218 |
| `users` | `forest_sold_day` | `TEXT DEFAULT NULL` | :1224 |
| `users` | `forest_sold_today` | `INTEGER DEFAULT 0` | :1225 |
| `users` | `fountain_used_day` | `TEXT DEFAULT NULL` | :1207 |
| `users` | `fountain_used_today` | `INTEGER DEFAULT 0` | :1208 |
| `users` | `last_active` | `REAL DEFAULT 0` | :1079 |
| `users` | `last_salary_date` | `TIMESTAMP` | :954 |
| `users` | `legioner` | `INTEGER DEFAULT 0` | :1370 |
| `users` | `market_license_expires` | `TEXT DEFAULT NULL` | :1324 |
| `users` | `mine_attempts_since_bat` | `INTEGER DEFAULT 0` | :1221 |
| `users` | `notify_enabled` | `INTEGER DEFAULT 1` | :948 |
| `users` | `profile_public` | `INTEGER DEFAULT 1` | :949 |
| `users` | `promoted_rank` | `TEXT` | :928 |
| `users` | `salary` | `INTEGER DEFAULT 0` | :952 |
| `users` | `salary_debt` | `INTEGER DEFAULT 0` | :955 |
| `users` | `salary_period_days` | `INTEGER DEFAULT 7` | :953 |
| `users` | `seaweed_used_day` | `TEXT DEFAULT NULL` | :1181 |
| `users` | `seaweed_used_today` | `INTEGER DEFAULT 0` | :1180 |
| `users` | `shower_used_day` | `TEXT DEFAULT NULL` | :1210 |
| `users` | `shower_used_today` | `INTEGER DEFAULT 0` | :1211 |
| `users` | `special_blocked_until` | `TEXT DEFAULT NULL` | :1195 |
| `users` | `special_fails_today` | `INTEGER DEFAULT 0` | :1194 |
| `users` | `wing` | `TEXT` | :1367 |
| `users` | `xp_balance` | `INTEGER DEFAULT 0` | :932 |
| `water_fish` | `excluded` | `INTEGER DEFAULT 0` | :1138 |
| `water_fish` | `kind` | `TEXT DEFAULT 'fish'` | :1346 |
| `water_fish` | `super_rare` | `INTEGER DEFAULT 0` | :1349 |
| `wings` | `abbr` | `TEXT DEFAULT ''` | :1174 |
| `wings` | `callsign` | `TEXT DEFAULT ''` | :1176 |
| `wings` | `emoji` | `TEXT DEFAULT ''` | :1177 |
| `wings` | `name` | `TEXT DEFAULT ''` | :1175 |
| `wings` | `num` | `TEXT DEFAULT ''` | :1173 |
| `wings` | `sort_order` | `INTEGER DEFAULT 0` | :1178 |

## 2. Идемпотентные засевы и миграции данных

| Функция | Вызывается из main.py | Назначение (первая строка docstring) | db.py |
|---|---|---|---|
| `backfill_rank_statuses` | — | Разово выдать статусы по текущим званиям всех пилотов (войска и админ-звания). | :5456 |
| `ensure_achievements` | ✅ | Идемпотентно засевает награды-уровни достижений и синхронизирует их. | :11764 |
| `ensure_base_status` | — | Базовый статус «Турист» для каждого нового игрока. | :5693 |
| `ensure_base_statuses` | — | Создаёт базовые статусы иерархии, если их нет. | :5648 |
| `ensure_duel_items` | ✅ | Товары Дома Дуэлей: дуэльные перчатки (отдельный слот) и клубная карта. | :9482 |
| `ensure_dungeon_enemy_drops` | ✅ | Синхронизирует врагов существующего данжа с DEFAULT_DUNGEON (дропы, HP, награды, | :11301 |
| `ensure_dungeon_reservoir_items` | ✅ | Идемпотентно добавляет предметы водохранилища подземелья (v0.12.0). | :11205 |
| `ensure_dungeon_shop_items` | ✅ | Идемпотентно добавляет предметы данжа (зелье в магазин, трофеи) — для существующих БД. | :10820 |
| `ensure_fishing_enemies` | ✅ | Идемпотентно засевает врагов рыбалки (мутировавший моллюск) из MOLLUSK_SEED. | :8651 |
| `ensure_forest_enemies` | ✅ | Идемпотентно засевает врагов леса (кабан и Белый Волк Севера). | :8626 |
| `ensure_forest_items` | ✅ | Идемпотентно создаёт предметы леса (грибы, добыча кабана, жареные блюда, яд). | :8035 |
| `ensure_forest_mushrooms` | ✅ | Идемпотентно засевает пул грибов леса из FOREST_DEFAULTS. | :8145 |
| `ensure_forest_zones` | ✅ | Разовый перенос старого пула леса в зону поляны и засев пула опушки. | :8388 |
| `ensure_kvp_award` | ✅ | — | :9741 |
| `ensure_kvp_items` | ✅ | Обеспечивает эксклюзивный предмет К.В.П. — «Сержантскую трость». | :9455 |
| `ensure_kvp_user` | — | Гарантирует наличие строки прогресса К.В.П. для игрока. | :9928 |
| `ensure_life_items` | ✅ | Идемпотентно добавляет предметы жилья, мебели, семян, ресурсов и продовольствия. | :11026 |
| `ensure_market_license_item` | ✅ | Идемпотентно добавляет «Торговую лицензию» в магазин. | :9038 |
| `ensure_mine_enemies` | ✅ | Идемпотентно засевает врагов копи (Летучая мышь) из MINE_BAT_SEED. | :8136 |
| `ensure_mine_items` | ✅ | Идемпотентно создаёт предметы Железной копи (кирка, руда, самоцветы). | :8105 |
| `ensure_mollusk_items` | ✅ | Идемпотентно создаёт предметы моллюска (из его добычи и готового блюда). | :8657 |
| `ensure_player_housing` | — | Возвращает жильё игрока, создавая муниципальную квартиру для пилота при первом обращении. | :11420 |
| `ensure_rank_statuses_for_troops` | — | Выдать статус по текущему званию игрока (по войскам или админ-назначению). | :5444 |
| `ensure_recipe_shop_item` | — | Синхронизирует товар-рецепт «Рецепт: <name>» с рецептом (менеджер). | :12177 |
| `ensure_recipe_shop_items` | ✅ | Создаёт в магазине предметы-рецепты категории 'recipes'. | :12949 |
| `ensure_recipes` | ✅ | Идемпотентно засевает рецепты и синхронизирует уже существующие. | :12027 |
| `ensure_tourist_booklet` | ✅ | Создаёт предмет «Буклет туриста» и награду «Опытный турист», если их нет. | :9777 |
| `ensure_user_recipes_backfill` | ✅ | Разово открывает все рецепты существующим игрокам. | :13060 |
| `ensure_water_fish` | ✅ | Идемпотентно засевает water_fish из дефолтов. Правившие админом строки | :7635 |
| `migrate_legacy_junk` | ✅ | Переносит старые копии мусора (сапог, водоросли) из инвентаря в улов. | :7481 |
| `seed_default_items` | ✅ | Заполняет магазин базовым набором товаров, если он пуст и не было своих товаров. | :9212 |
| `seed_dungeon` | ✅ | — | :9336 |
| `seed_kvp` | ✅ | Создаёт тренировочный данж К.В.П. с врагами (Ефрейтор, Старший сержант), если его нет. | :9405 |
| `seed_locations` | — | Засеивает базовые локации города (Ратуша, Библиотека) как пример управляемого доступа. | :1452 |

## 3. Отдельные скрипты миграций

- `migrate_113.py` — Проверка миграций 0.19.0 на чистой БД: колонки polls, таблица rep_speeches.
- `migrate_113_old.py` — Миграция 0.19.0 поверх БД со старой схемой polls (без closes_at/is_archived).

