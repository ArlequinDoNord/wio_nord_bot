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

Всего вызовов: **161**; таблиц: **22**.

| Таблица | Колонка | Тип / значение по умолчанию | db.py |
|---|---|---|---|
| `awards` | `achievement_key` | `TEXT DEFAULT NULL` | :1158 |
| `awards` | `achievement_level` | `INTEGER DEFAULT 0` | :1159 |
| `awards` | `bonus_attack` | `INTEGER DEFAULT 0` | :1137 |
| `awards` | `bonus_crit` | `INTEGER DEFAULT 0` | :1144 |
| `awards` | `bonus_defense` | `INTEGER DEFAULT 0` | :1138 |
| `awards` | `bonus_dodge` | `INTEGER DEFAULT 0` | :1139 |
| `awards` | `bonus_fishing` | `INTEGER DEFAULT 0` | :1140 |
| `awards` | `bonus_hp` | `INTEGER DEFAULT 0` | :1141 |
| `awards` | `bonus_json` | `TEXT DEFAULT '{}'` | :1160 |
| `awards` | `bonus_report_tax` | `INTEGER DEFAULT 0` | :1148 |
| `awards` | `bonus_shop_discount` | `INTEGER DEFAULT 0` | :1147 |
| `awards` | `image` | `TEXT` | :1136 |
| `awards` | `monthly_nm` | `INTEGER DEFAULT 0` | :1152 |
| `awards` | `reward_nm` | `INTEGER DEFAULT 0` | :1151 |
| `buildings` | `required_status` | `TEXT` | :918 |
| `dungeon_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1086 |
| `dungeon_enemies` | `admin_tuned` | `INTEGER DEFAULT 0` | :1108 |
| `dungeon_enemies` | `armor` | `INTEGER DEFAULT 0` | :1082 |
| `dungeon_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1317 |
| `dungeon_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1318 |
| `dungeon_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1084 |
| `dungeon_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1085 |
| `dungeon_enemies` | `damage_max` | `INTEGER DEFAULT 0` | :1081 |
| `dungeon_enemies` | `damage_min` | `INTEGER DEFAULT 0` | :1080 |
| `dungeon_enemies` | `description` | `TEXT` | :1078 |
| `dungeon_enemies` | `dodge` | `INTEGER DEFAULT 0` | :1079 |
| `dungeon_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1083 |
| `dungeon_enemies` | `drops` | `TEXT DEFAULT '[]'` | :1074 |
| `dungeon_enemies` | `frostbite_chance` | `INTEGER DEFAULT 0` | :1319 |
| `dungeon_enemies` | `image` | `TEXT` | :1075 |
| `dungeon_enemies` | `poison_chance` | `INTEGER DEFAULT 0` | :1076 |
| `dungeon_enemies` | `poison_dmg` | `INTEGER DEFAULT 0` | :1077 |
| `dungeons` | `is_training` | `INTEGER DEFAULT 0` | :1308 |
| `dungeons` | `photo_dawn` | `TEXT` | :1121 |
| `dungeons` | `photo_day` | `TEXT` | :1122 |
| `dungeons` | `photo_night` | `TEXT` | :1124 |
| `dungeons` | `photo_rope` | `TEXT` | :1127 |
| `dungeons` | `photo_sunset` | `TEXT` | :1123 |
| `dungeons` | `photo_water` | `TEXT` | :1126 |
| `dungeons` | `rooms_map` | `TEXT` | :1324 |
| `fish_catches` | `expires_at` | `TIMESTAMP` | :1195 |
| `fish_catches` | `kind` | `TEXT DEFAULT 'fish'` | :1330 |
| `fishing_enemies` | `armor` | `INTEGER DEFAULT 0` | :1097 |
| `fishing_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1095 |
| `fishing_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1096 |
| `forest_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1091 |
| `forest_enemies` | `armor` | `INTEGER DEFAULT 0` | :1087 |
| `forest_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1093 |
| `forest_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1094 |
| `forest_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1089 |
| `forest_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1090 |
| `forest_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1088 |
| `forest_mushrooms` | `zone` | `TEXT DEFAULT 'clearing'` | :1227 |
| `housing_slots` | `embedded` | `INTEGER DEFAULT 0` | :1258 |
| `inventory` | `expires_at` | `TIMESTAMP` | :1190 |
| `inventory` | `plant_data` | `TEXT` | :1192 |
| `items` | `armor` | `INTEGER DEFAULT 0` | :948 |
| `items` | `crit_chance` | `INTEGER DEFAULT 0` | :951 |
| `items` | `crit_mult` | `REAL DEFAULT 0` | :952 |
| `items` | `cure_frostbite` | `INTEGER DEFAULT 0` | :1321 |
| `items` | `cure_poison` | `INTEGER DEFAULT 0` | :1109 |
| `items` | `damage` | `INTEGER DEFAULT 0` | :1072 |
| `items` | `drink_effect` | `TEXT DEFAULT NULL` | :1178 |
| `items` | `equip_slot` | `TEXT` | :954 |
| `items` | `heal` | `INTEGER DEFAULT 0` | :1073 |
| `items` | `housing_slots` | `INTEGER` | :1413 |
| `items` | `housing_type` | `TEXT` | :1412 |
| `items` | `loot_only` | `INTEGER DEFAULT 0` | :1418 |
| `items` | `market_ok` | `INTEGER DEFAULT 0` | :1327 |
| `items` | `plant_name` | `TEXT` | :1337 |
| `items` | `regen` | `INTEGER DEFAULT 0` | :1119 |
| `items` | `required_status` | `TEXT` | :917 |
| `items` | `weapon_effect` | `TEXT` | :1348 |
| `items` | `weapon_effect_chance` | `INTEGER DEFAULT 0` | :1349 |
| `items` | `weapon_effect_dmg` | `INTEGER DEFAULT 0` | :1350 |
| `locations` | `clearing_photo` | `TEXT DEFAULT NULL` | :1222 |
| `locations` | `glade_photo` | `TEXT DEFAULT NULL` | :1221 |
| `locations` | `photo_dawn` | `TEXT` | :1111 |
| `locations` | `photo_day` | `TEXT` | :1112 |
| `locations` | `photo_night` | `TEXT` | :1114 |
| `locations` | `photo_sunset` | `TEXT` | :1113 |
| `locations` | `preview_photo` | `TEXT` | :1110 |
| `locations` | `season_photos` | `TEXT DEFAULT NULL` | :1218 |
| `locations` | `visits` | `INTEGER DEFAULT 0` | :1116 |
| `market_fish` | `base_price` | `INTEGER DEFAULT 0` | :1311 |
| `mine_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1103 |
| `mine_enemies` | `armor` | `INTEGER DEFAULT 0` | :1099 |
| `mine_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1104 |
| `mine_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1105 |
| `mine_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1101 |
| `mine_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1102 |
| `mine_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1100 |
| `player_dungeon_run` | `loot_nm` | `INTEGER DEFAULT 0` | :1059 |
| `player_dungeon_run` | `started_at` | `TIMESTAMP DEFAULT CURRENT_TIMESTAMP` | :1060 |
| `player_housing` | `expansions_installed` | `INTEGER DEFAULT 0` | :1260 |
| `player_housing` | `housing_label` | `TEXT` | :1414 |
| `player_housing` | `housing_slots` | `INTEGER` | :1415 |
| `player_housing` | `tax_last_check` | `TEXT DEFAULT NULL` | :1312 |
| `player_housing` | `tax_unpaid_months` | `INTEGER DEFAULT 0` | :1313 |
| `polls` | `archived_day` | `TEXT DEFAULT ''` | :1276 |
| `polls` | `closed_at` | `TIMESTAMP` | :1188 |
| `polls` | `closed_by` | `INTEGER` | :1187 |
| `polls` | `closes_at` | `TIMESTAMP` | :1265 |
| `polls` | `is_archived` | `INTEGER DEFAULT 0` | :1275 |
| `reports` | `credited_troops` | `INTEGER` | :959 |
| `reports` | `paid` | `INTEGER DEFAULT 0` | :966 |
| `reports` | `total_troops` | `INTEGER DEFAULT 0` | :957 |
| `statuses` | `sort_order` | `INTEGER DEFAULT 0` | :919 |
| `users` | `about` | `TEXT DEFAULT ''` | :942 |
| `users` | `alcohol_strong_used_day` | `TEXT DEFAULT NULL` | :1182 |
| `users` | `alcohol_strong_used_today` | `INTEGER DEFAULT 0` | :1181 |
| `users` | `alcohol_weak_used_day` | `TEXT DEFAULT NULL` | :1180 |
| `users` | `alcohol_weak_used_today` | `INTEGER DEFAULT 0` | :1179 |
| `users` | `ap_recovery_day` | `TEXT DEFAULT NULL` | :1174 |
| `users` | `ap_restored_day` | `TEXT DEFAULT NULL` | :1063 |
| `users` | `ap_restored_today` | `INTEGER DEFAULT 0` | :1064 |
| `users` | `beer_used_day` | `TEXT DEFAULT NULL` | :1177 |
| `users` | `beer_used_today` | `INTEGER DEFAULT 0` | :1176 |
| `users` | `callsign` | `TEXT` | :1134 |
| `users` | `callsign_free_used` | `INTEGER DEFAULT 0` | :1310 |
| `users` | `duel_losses` | `INTEGER DEFAULT 0` | :1068 |
| `users` | `duel_rating` | `INTEGER DEFAULT 0` | :1066 |
| `users` | `duel_wins` | `INTEGER DEFAULT 0` | :1067 |
| `users` | `equipment` | `TEXT DEFAULT '{}'` | :943 |
| `users` | `fish_sold_day` | `TEXT DEFAULT NULL` | :1203 |
| `users` | `fish_sold_today` | `INTEGER DEFAULT 0` | :1204 |
| `users` | `fishing_bait` | `TEXT DEFAULT ''` | :1132 |
| `users` | `forest_attempts_since_boar` | `INTEGER DEFAULT 0` | :1206 |
| `users` | `forest_attempts_since_wolf` | `INTEGER DEFAULT 0` | :1208 |
| `users` | `forest_sold_day` | `TEXT DEFAULT NULL` | :1214 |
| `users` | `forest_sold_today` | `INTEGER DEFAULT 0` | :1215 |
| `users` | `fountain_used_day` | `TEXT DEFAULT NULL` | :1197 |
| `users` | `fountain_used_today` | `INTEGER DEFAULT 0` | :1198 |
| `users` | `last_active` | `REAL DEFAULT 0` | :1071 |
| `users` | `last_salary_date` | `TIMESTAMP` | :946 |
| `users` | `legioner` | `INTEGER DEFAULT 0` | :1355 |
| `users` | `market_license_expires` | `TEXT DEFAULT NULL` | :1309 |
| `users` | `mine_attempts_since_bat` | `INTEGER DEFAULT 0` | :1211 |
| `users` | `notify_enabled` | `INTEGER DEFAULT 1` | :940 |
| `users` | `profile_public` | `INTEGER DEFAULT 1` | :941 |
| `users` | `promoted_rank` | `TEXT` | :920 |
| `users` | `salary` | `INTEGER DEFAULT 0` | :944 |
| `users` | `salary_debt` | `INTEGER DEFAULT 0` | :947 |
| `users` | `salary_period_days` | `INTEGER DEFAULT 7` | :945 |
| `users` | `seaweed_used_day` | `TEXT DEFAULT NULL` | :1171 |
| `users` | `seaweed_used_today` | `INTEGER DEFAULT 0` | :1170 |
| `users` | `shower_used_day` | `TEXT DEFAULT NULL` | :1200 |
| `users` | `shower_used_today` | `INTEGER DEFAULT 0` | :1201 |
| `users` | `special_blocked_until` | `TEXT DEFAULT NULL` | :1185 |
| `users` | `special_fails_today` | `INTEGER DEFAULT 0` | :1184 |
| `users` | `wing` | `TEXT` | :1352 |
| `users` | `xp_balance` | `INTEGER DEFAULT 0` | :924 |
| `water_fish` | `excluded` | `INTEGER DEFAULT 0` | :1130 |
| `water_fish` | `kind` | `TEXT DEFAULT 'fish'` | :1331 |
| `water_fish` | `super_rare` | `INTEGER DEFAULT 0` | :1334 |
| `wings` | `abbr` | `TEXT DEFAULT ''` | :1164 |
| `wings` | `callsign` | `TEXT DEFAULT ''` | :1166 |
| `wings` | `emoji` | `TEXT DEFAULT ''` | :1167 |
| `wings` | `name` | `TEXT DEFAULT ''` | :1165 |
| `wings` | `num` | `TEXT DEFAULT ''` | :1163 |
| `wings` | `sort_order` | `INTEGER DEFAULT 0` | :1168 |

## 2. Идемпотентные засевы и миграции данных

| Функция | Вызывается из main.py | Назначение (первая строка docstring) | db.py |
|---|---|---|---|
| `backfill_rank_statuses` | — | Разово выдать статусы по текущим званиям всех пилотов (войска и админ-звания). | :5436 |
| `ensure_achievements` | ✅ | Идемпотентно засевает награды-уровни достижений и синхронизирует их. | :11641 |
| `ensure_base_status` | — | Базовый статус «Турист» для каждого нового игрока. | :5673 |
| `ensure_base_statuses` | — | Создаёт базовые статусы иерархии, если их нет. | :5628 |
| `ensure_duel_items` | ✅ | Товары Дома Дуэлей: дуэльные перчатки (отдельный слот) и клубная карта. | :9359 |
| `ensure_dungeon_enemy_drops` | ✅ | Синхронизирует врагов существующего данжа с DEFAULT_DUNGEON (дропы, HP, награды, | :11178 |
| `ensure_dungeon_reservoir_items` | ✅ | Идемпотентно добавляет предметы водохранилища подземелья (v0.12.0). | :11082 |
| `ensure_dungeon_shop_items` | ✅ | Идемпотентно добавляет предметы данжа (зелье в магазин, трофеи) — для существующих БД. | :10697 |
| `ensure_fishing_enemies` | ✅ | Идемпотентно засевает врагов рыбалки (мутировавший моллюск) из MOLLUSK_SEED. | :8528 |
| `ensure_forest_enemies` | ✅ | Идемпотентно засевает врагов леса (кабан и Белый Волк Севера). | :8503 |
| `ensure_forest_items` | ✅ | Идемпотентно создаёт предметы леса (грибы, добыча кабана, жареные блюда, яд). | :7912 |
| `ensure_forest_mushrooms` | ✅ | Идемпотентно засевает пул грибов леса из FOREST_DEFAULTS. | :8022 |
| `ensure_forest_zones` | ✅ | Разовый перенос старого пула леса в зону поляны и засев пула опушки. | :8265 |
| `ensure_kvp_award` | ✅ | — | :9618 |
| `ensure_kvp_items` | ✅ | Обеспечивает эксклюзивный предмет К.В.П. — «Сержантскую трость». | :9332 |
| `ensure_kvp_user` | — | Гарантирует наличие строки прогресса К.В.П. для игрока. | :9805 |
| `ensure_life_items` | ✅ | Идемпотентно добавляет предметы жилья, мебели, семян, ресурсов и продовольствия. | :10903 |
| `ensure_market_license_item` | ✅ | Идемпотентно добавляет «Торговую лицензию» в магазин. | :8915 |
| `ensure_mine_enemies` | ✅ | Идемпотентно засевает врагов копи (Летучая мышь) из MINE_BAT_SEED. | :8013 |
| `ensure_mine_items` | ✅ | Идемпотентно создаёт предметы Железной копи (кирка, руда, самоцветы). | :7982 |
| `ensure_mollusk_items` | ✅ | Идемпотентно создаёт предметы моллюска (из его добычи и готового блюда). | :8534 |
| `ensure_player_housing` | — | Возвращает жильё игрока, создавая муниципальную квартиру для пилота при первом обращении. | :11297 |
| `ensure_rank_statuses_for_troops` | — | Выдать статус по текущему званию игрока (по войскам или админ-назначению). | :5424 |
| `ensure_recipe_shop_item` | — | Синхронизирует товар-рецепт «Рецепт: <name>» с рецептом (менеджер). | :12054 |
| `ensure_recipe_shop_items` | ✅ | Создаёт в магазине предметы-рецепты категории 'recipes'. | :12826 |
| `ensure_recipes` | ✅ | Идемпотентно засевает рецепты и синхронизирует уже существующие. | :11904 |
| `ensure_tourist_booklet` | ✅ | Создаёт предмет «Буклет туриста» и награду «Опытный турист», если их нет. | :9654 |
| `ensure_user_recipes_backfill` | ✅ | Разово открывает все рецепты существующим игрокам. | :12937 |
| `ensure_water_fish` | ✅ | Идемпотентно засевает water_fish из дефолтов. Правившие админом строки | :7512 |
| `migrate_legacy_junk` | ✅ | Переносит старые копии мусора (сапог, водоросли) из инвентаря в улов. | :7358 |
| `seed_default_items` | ✅ | Заполняет магазин базовым набором товаров, если он пуст и не было своих товаров. | :9089 |
| `seed_dungeon` | ✅ | — | :9213 |
| `seed_kvp` | ✅ | Создаёт тренировочный данж К.В.П. с врагами (Ефрейтор, Старший сержант), если его нет. | :9282 |
| `seed_locations` | — | Засеивает базовые локации города (Ратуша, Библиотека) как пример управляемого доступа. | :1437 |

## 3. Отдельные скрипты миграций

- `migrate_113.py` — Проверка миграций 0.19.0 на чистой БД: колонки polls, таблица rep_speeches.
- `migrate_113_old.py` — Миграция 0.19.0 поверх БД со старой схемой polls (без closes_at/is_archived).

