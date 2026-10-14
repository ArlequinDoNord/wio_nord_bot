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

Всего вызовов: **151**; таблиц: **21**.

| Таблица | Колонка | Тип / значение по умолчанию | db.py |
|---|---|---|---|
| `awards` | `achievement_key` | `TEXT DEFAULT NULL` | :1123 |
| `awards` | `achievement_level` | `INTEGER DEFAULT 0` | :1124 |
| `awards` | `bonus_attack` | `INTEGER DEFAULT 0` | :1102 |
| `awards` | `bonus_crit` | `INTEGER DEFAULT 0` | :1109 |
| `awards` | `bonus_defense` | `INTEGER DEFAULT 0` | :1103 |
| `awards` | `bonus_dodge` | `INTEGER DEFAULT 0` | :1104 |
| `awards` | `bonus_fishing` | `INTEGER DEFAULT 0` | :1105 |
| `awards` | `bonus_hp` | `INTEGER DEFAULT 0` | :1106 |
| `awards` | `bonus_json` | `TEXT DEFAULT '{}'` | :1125 |
| `awards` | `bonus_report_tax` | `INTEGER DEFAULT 0` | :1113 |
| `awards` | `bonus_shop_discount` | `INTEGER DEFAULT 0` | :1112 |
| `awards` | `image` | `TEXT` | :1101 |
| `awards` | `monthly_nm` | `INTEGER DEFAULT 0` | :1117 |
| `awards` | `reward_nm` | `INTEGER DEFAULT 0` | :1116 |
| `buildings` | `required_status` | `TEXT` | :891 |
| `dungeon_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1059 |
| `dungeon_enemies` | `admin_tuned` | `INTEGER DEFAULT 0` | :1073 |
| `dungeon_enemies` | `armor` | `INTEGER DEFAULT 0` | :1055 |
| `dungeon_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1276 |
| `dungeon_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1277 |
| `dungeon_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1057 |
| `dungeon_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1058 |
| `dungeon_enemies` | `damage_max` | `INTEGER DEFAULT 0` | :1054 |
| `dungeon_enemies` | `damage_min` | `INTEGER DEFAULT 0` | :1053 |
| `dungeon_enemies` | `description` | `TEXT` | :1051 |
| `dungeon_enemies` | `dodge` | `INTEGER DEFAULT 0` | :1052 |
| `dungeon_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1056 |
| `dungeon_enemies` | `drops` | `TEXT DEFAULT '[]'` | :1047 |
| `dungeon_enemies` | `frostbite_chance` | `INTEGER DEFAULT 0` | :1278 |
| `dungeon_enemies` | `image` | `TEXT` | :1048 |
| `dungeon_enemies` | `poison_chance` | `INTEGER DEFAULT 0` | :1049 |
| `dungeon_enemies` | `poison_dmg` | `INTEGER DEFAULT 0` | :1050 |
| `dungeons` | `is_training` | `INTEGER DEFAULT 0` | :1267 |
| `dungeons` | `photo_dawn` | `TEXT` | :1086 |
| `dungeons` | `photo_day` | `TEXT` | :1087 |
| `dungeons` | `photo_night` | `TEXT` | :1089 |
| `dungeons` | `photo_rope` | `TEXT` | :1092 |
| `dungeons` | `photo_sunset` | `TEXT` | :1088 |
| `dungeons` | `photo_water` | `TEXT` | :1091 |
| `dungeons` | `rooms_map` | `TEXT` | :1283 |
| `fish_catches` | `expires_at` | `TIMESTAMP` | :1160 |
| `fish_catches` | `kind` | `TEXT DEFAULT 'fish'` | :1289 |
| `fishing_enemies` | `armor` | `INTEGER DEFAULT 0` | :1070 |
| `fishing_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1068 |
| `fishing_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1069 |
| `forest_enemies` | `abilities` | `TEXT DEFAULT '[]'` | :1064 |
| `forest_enemies` | `armor` | `INTEGER DEFAULT 0` | :1060 |
| `forest_enemies` | `bleed_chance` | `INTEGER DEFAULT 0` | :1066 |
| `forest_enemies` | `bleed_dmg` | `INTEGER DEFAULT 0` | :1067 |
| `forest_enemies` | `crit_chance` | `INTEGER DEFAULT 0` | :1062 |
| `forest_enemies` | `crit_mult` | `REAL DEFAULT 1.5` | :1063 |
| `forest_enemies` | `dodge_chance` | `INTEGER DEFAULT 0` | :1061 |
| `forest_mushrooms` | `zone` | `TEXT DEFAULT 'clearing'` | :1186 |
| `housing_slots` | `embedded` | `INTEGER DEFAULT 0` | :1217 |
| `inventory` | `expires_at` | `TIMESTAMP` | :1155 |
| `inventory` | `plant_data` | `TEXT` | :1157 |
| `items` | `armor` | `INTEGER DEFAULT 0` | :921 |
| `items` | `crit_chance` | `INTEGER DEFAULT 0` | :924 |
| `items` | `crit_mult` | `REAL DEFAULT 0` | :925 |
| `items` | `cure_frostbite` | `INTEGER DEFAULT 0` | :1280 |
| `items` | `cure_poison` | `INTEGER DEFAULT 0` | :1074 |
| `items` | `damage` | `INTEGER DEFAULT 0` | :1045 |
| `items` | `drink_effect` | `TEXT DEFAULT NULL` | :1143 |
| `items` | `equip_slot` | `TEXT` | :927 |
| `items` | `heal` | `INTEGER DEFAULT 0` | :1046 |
| `items` | `housing_slots` | `INTEGER` | :1372 |
| `items` | `housing_type` | `TEXT` | :1371 |
| `items` | `loot_only` | `INTEGER DEFAULT 0` | :1377 |
| `items` | `market_ok` | `INTEGER DEFAULT 0` | :1286 |
| `items` | `plant_name` | `TEXT` | :1296 |
| `items` | `regen` | `INTEGER DEFAULT 0` | :1084 |
| `items` | `required_status` | `TEXT` | :890 |
| `items` | `weapon_effect` | `TEXT` | :1307 |
| `items` | `weapon_effect_chance` | `INTEGER DEFAULT 0` | :1308 |
| `items` | `weapon_effect_dmg` | `INTEGER DEFAULT 0` | :1309 |
| `locations` | `clearing_photo` | `TEXT DEFAULT NULL` | :1181 |
| `locations` | `glade_photo` | `TEXT DEFAULT NULL` | :1180 |
| `locations` | `photo_dawn` | `TEXT` | :1076 |
| `locations` | `photo_day` | `TEXT` | :1077 |
| `locations` | `photo_night` | `TEXT` | :1079 |
| `locations` | `photo_sunset` | `TEXT` | :1078 |
| `locations` | `preview_photo` | `TEXT` | :1075 |
| `locations` | `season_photos` | `TEXT DEFAULT NULL` | :1177 |
| `locations` | `visits` | `INTEGER DEFAULT 0` | :1081 |
| `market_fish` | `base_price` | `INTEGER DEFAULT 0` | :1270 |
| `player_dungeon_run` | `loot_nm` | `INTEGER DEFAULT 0` | :1032 |
| `player_dungeon_run` | `started_at` | `TIMESTAMP DEFAULT CURRENT_TIMESTAMP` | :1033 |
| `player_housing` | `expansions_installed` | `INTEGER DEFAULT 0` | :1219 |
| `player_housing` | `housing_label` | `TEXT` | :1373 |
| `player_housing` | `housing_slots` | `INTEGER` | :1374 |
| `player_housing` | `tax_last_check` | `TEXT DEFAULT NULL` | :1271 |
| `player_housing` | `tax_unpaid_months` | `INTEGER DEFAULT 0` | :1272 |
| `polls` | `archived_day` | `TEXT DEFAULT ''` | :1235 |
| `polls` | `closed_at` | `TIMESTAMP` | :1153 |
| `polls` | `closed_by` | `INTEGER` | :1152 |
| `polls` | `closes_at` | `TIMESTAMP` | :1224 |
| `polls` | `is_archived` | `INTEGER DEFAULT 0` | :1234 |
| `reports` | `credited_troops` | `INTEGER` | :932 |
| `reports` | `paid` | `INTEGER DEFAULT 0` | :939 |
| `reports` | `total_troops` | `INTEGER DEFAULT 0` | :930 |
| `statuses` | `sort_order` | `INTEGER DEFAULT 0` | :892 |
| `users` | `about` | `TEXT DEFAULT ''` | :915 |
| `users` | `alcohol_strong_used_day` | `TEXT DEFAULT NULL` | :1147 |
| `users` | `alcohol_strong_used_today` | `INTEGER DEFAULT 0` | :1146 |
| `users` | `alcohol_weak_used_day` | `TEXT DEFAULT NULL` | :1145 |
| `users` | `alcohol_weak_used_today` | `INTEGER DEFAULT 0` | :1144 |
| `users` | `ap_recovery_day` | `TEXT DEFAULT NULL` | :1139 |
| `users` | `ap_restored_day` | `TEXT DEFAULT NULL` | :1036 |
| `users` | `ap_restored_today` | `INTEGER DEFAULT 0` | :1037 |
| `users` | `beer_used_day` | `TEXT DEFAULT NULL` | :1142 |
| `users` | `beer_used_today` | `INTEGER DEFAULT 0` | :1141 |
| `users` | `callsign` | `TEXT` | :1099 |
| `users` | `callsign_free_used` | `INTEGER DEFAULT 0` | :1269 |
| `users` | `duel_losses` | `INTEGER DEFAULT 0` | :1041 |
| `users` | `duel_rating` | `INTEGER DEFAULT 0` | :1039 |
| `users` | `duel_wins` | `INTEGER DEFAULT 0` | :1040 |
| `users` | `equipment` | `TEXT DEFAULT '{}'` | :916 |
| `users` | `fish_sold_day` | `TEXT DEFAULT NULL` | :1165 |
| `users` | `fish_sold_today` | `INTEGER DEFAULT 0` | :1166 |
| `users` | `fishing_bait` | `TEXT DEFAULT ''` | :1097 |
| `users` | `forest_attempts_since_boar` | `INTEGER DEFAULT 0` | :1168 |
| `users` | `forest_attempts_since_wolf` | `INTEGER DEFAULT 0` | :1170 |
| `users` | `forest_sold_day` | `TEXT DEFAULT NULL` | :1173 |
| `users` | `forest_sold_today` | `INTEGER DEFAULT 0` | :1174 |
| `users` | `fountain_used_day` | `TEXT DEFAULT NULL` | :1162 |
| `users` | `fountain_used_today` | `INTEGER DEFAULT 0` | :1163 |
| `users` | `last_active` | `REAL DEFAULT 0` | :1044 |
| `users` | `last_salary_date` | `TIMESTAMP` | :919 |
| `users` | `legioner` | `INTEGER DEFAULT 0` | :1314 |
| `users` | `market_license_expires` | `TEXT DEFAULT NULL` | :1268 |
| `users` | `notify_enabled` | `INTEGER DEFAULT 1` | :913 |
| `users` | `profile_public` | `INTEGER DEFAULT 1` | :914 |
| `users` | `promoted_rank` | `TEXT` | :893 |
| `users` | `salary` | `INTEGER DEFAULT 0` | :917 |
| `users` | `salary_debt` | `INTEGER DEFAULT 0` | :920 |
| `users` | `salary_period_days` | `INTEGER DEFAULT 7` | :918 |
| `users` | `seaweed_used_day` | `TEXT DEFAULT NULL` | :1136 |
| `users` | `seaweed_used_today` | `INTEGER DEFAULT 0` | :1135 |
| `users` | `special_blocked_until` | `TEXT DEFAULT NULL` | :1150 |
| `users` | `special_fails_today` | `INTEGER DEFAULT 0` | :1149 |
| `users` | `wing` | `TEXT` | :1311 |
| `users` | `xp_balance` | `INTEGER DEFAULT 0` | :897 |
| `water_fish` | `excluded` | `INTEGER DEFAULT 0` | :1095 |
| `water_fish` | `kind` | `TEXT DEFAULT 'fish'` | :1290 |
| `water_fish` | `super_rare` | `INTEGER DEFAULT 0` | :1293 |
| `wings` | `abbr` | `TEXT DEFAULT ''` | :1129 |
| `wings` | `callsign` | `TEXT DEFAULT ''` | :1131 |
| `wings` | `emoji` | `TEXT DEFAULT ''` | :1132 |
| `wings` | `name` | `TEXT DEFAULT ''` | :1130 |
| `wings` | `num` | `TEXT DEFAULT ''` | :1128 |
| `wings` | `sort_order` | `INTEGER DEFAULT 0` | :1133 |

## 2. Идемпотентные засевы и миграции данных

| Функция | Вызывается из main.py | Назначение (первая строка docstring) | db.py |
|---|---|---|---|
| `backfill_rank_statuses` | — | Разово выдать статусы по текущим званиям всех пилотов (войска и админ-звания). | :5390 |
| `ensure_achievements` | ✅ | Идемпотентно засевает награды-уровни достижений и синхронизирует их. | :11355 |
| `ensure_base_status` | — | Базовый статус «Турист» для каждого нового игрока. | :5627 |
| `ensure_base_statuses` | — | Создаёт базовые статусы иерархии, если их нет. | :5582 |
| `ensure_duel_items` | ✅ | Товары Дома Дуэлей: дуэльные перчатки (отдельный слот) и клубная карта. | :9247 |
| `ensure_dungeon_enemy_drops` | ✅ | Синхронизирует врагов существующего данжа с DEFAULT_DUNGEON (дропы, HP, награды, | :10892 |
| `ensure_dungeon_reservoir_items` | ✅ | Идемпотентно добавляет предметы водохранилища подземелья (v0.12.0). | :10796 |
| `ensure_dungeon_shop_items` | ✅ | Идемпотентно добавляет предметы данжа (зелье в магазин, трофеи) — для существующих БД. | :10415 |
| `ensure_fishing_enemies` | ✅ | Идемпотентно засевает врагов рыбалки (мутировавший моллюск) из MOLLUSK_SEED. | :8441 |
| `ensure_forest_enemies` | ✅ | Идемпотентно засевает врагов леса (кабан и Белый Волк Севера). | :8416 |
| `ensure_forest_items` | ✅ | Идемпотентно создаёт предметы леса (грибы, добыча кабана, жареные блюда, яд). | :7866 |
| `ensure_forest_mushrooms` | ✅ | Идемпотентно засевает пул грибов леса из FOREST_DEFAULTS. | :7936 |
| `ensure_forest_zones` | ✅ | Разовый перенос старого пула леса в зону поляны и засев пула опушки. | :8179 |
| `ensure_kvp_award` | ✅ | — | :9336 |
| `ensure_kvp_items` | ✅ | Обеспечивает эксклюзивный предмет К.В.П. — «Сержантскую трость». | :9220 |
| `ensure_kvp_user` | — | Гарантирует наличие строки прогресса К.В.П. для игрока. | :9523 |
| `ensure_life_items` | ✅ | Идемпотентно добавляет предметы жилья, мебели, семян, ресурсов и продовольствия. | :10621 |
| `ensure_market_license_item` | ✅ | Идемпотентно добавляет «Торговую лицензию» в магазин. | :8803 |
| `ensure_mollusk_items` | ✅ | Идемпотентно создаёт предметы моллюска (из его добычи и готового блюда). | :8447 |
| `ensure_player_housing` | — | Возвращает жильё игрока, создавая муниципальную квартиру для пилота при первом обращении. | :11011 |
| `ensure_rank_statuses_for_troops` | — | Выдать статус по текущему званию игрока (по войскам или админ-назначению). | :5378 |
| `ensure_recipe_shop_item` | — | Синхронизирует товар-рецепт «Рецепт: <name>» с рецептом (менеджер). | :11768 |
| `ensure_recipe_shop_items` | ✅ | Создаёт в магазине предметы-рецепты категории 'recipes'. | :12523 |
| `ensure_recipes` | ✅ | Идемпотентно засевает рецепты и синхронизирует уже существующие. | :11618 |
| `ensure_tourist_booklet` | ✅ | Создаёт предмет «Буклет туриста» и награду «Опытный турист», если их нет. | :9372 |
| `ensure_user_recipes_backfill` | ✅ | Разово открывает все рецепты существующим игрокам. | :12634 |
| `ensure_water_fish` | ✅ | Идемпотентно засевает water_fish из дефолтов. Правившие админом строки | :7466 |
| `migrate_legacy_junk` | ✅ | Переносит старые копии мусора (сапог, водоросли) из инвентаря в улов. | :7312 |
| `seed_default_items` | ✅ | Заполняет магазин базовым набором товаров, если он пуст и не было своих товаров. | :8977 |
| `seed_dungeon` | ✅ | — | :9101 |
| `seed_kvp` | ✅ | Создаёт тренировочный данж К.В.П. с врагами (Ефрейтор, Старший сержант), если его нет. | :9170 |
| `seed_locations` | — | Засеивает базовые локации города (Ратуша, Библиотека) как пример управляемого доступа. | :1396 |

## 3. Отдельные скрипты миграций

- `migrate_113.py` — Проверка миграций 0.19.0 на чистой БД: колонки polls, таблица rep_speeches.
- `migrate_113_old.py` — Миграция 0.19.0 поверх БД со старой схемой polls (без closes_at/is_archived).

