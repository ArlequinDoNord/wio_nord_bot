# Схема базы данных WIO Nord Bot

> Сгенерировано из `database/db.py`: SQL из `init_db()` (CREATE TABLE / CREATE INDEX) исполнен в sqlite, плюс колонки, добавляемые через `_ensure_column`.

Всего таблиц: **73**.

- **Миграции** — колонки, которых нет в исходном `CREATE TABLE`, но которые добавляются в существующие БД через `_ensure_column`.
- **UNIQUE** у индекса помечает уникальный индекс.

## `users`

| Колонка |
|---|
| `user_id INTEGER PRIMARY KEY` |
| `username TEXT` |
| `first_name TEXT` |
| `last_name TEXT` |
| `photo_file_id TEXT` |
| `troops INTEGER DEFAULT 0` |
| `nordmarks INTEGER DEFAULT 10` |
| `ap INTEGER DEFAULT 100` |
| `ap_max INTEGER DEFAULT 150` |
| `state TEXT DEFAULT 'нормально'` |
| `state_effects TEXT DEFAULT '{}'` |
| `promoted_rank TEXT` |
| `status_text TEXT DEFAULT 'Боевой пилот'` |
| `about TEXT DEFAULT ''` |
| `notify_enabled INTEGER DEFAULT 1` |
| `profile_public INTEGER DEFAULT 1` |
| `equipment TEXT DEFAULT '{}'` |
| `salary INTEGER DEFAULT 0` |
| `salary_period_days INTEGER DEFAULT 7` |
| `last_salary_date TIMESTAMP` |
| `salary_debt INTEGER DEFAULT 0` |
| `created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP` |

**Добавлено миграциями (`_ensure_column`):**

| Колонка | Тип |
|---|---|
| `xp_balance` | `INTEGER DEFAULT 0` |
| `ap_restored_day` | `TEXT DEFAULT NULL` |
| `ap_restored_today` | `INTEGER DEFAULT 0` |
| `duel_rating` | `INTEGER DEFAULT 0` |
| `duel_wins` | `INTEGER DEFAULT 0` |
| `duel_losses` | `INTEGER DEFAULT 0` |
| `last_active` | `REAL DEFAULT 0` |
| `fishing_bait` | `TEXT DEFAULT ''` |
| `callsign` | `TEXT` |
| `seaweed_used_today` | `INTEGER DEFAULT 0` |
| `seaweed_used_day` | `TEXT DEFAULT NULL` |
| `ap_recovery_day` | `TEXT DEFAULT NULL` |
| `beer_used_today` | `INTEGER DEFAULT 0` |
| `beer_used_day` | `TEXT DEFAULT NULL` |
| `alcohol_weak_used_today` | `INTEGER DEFAULT 0` |
| `alcohol_weak_used_day` | `TEXT DEFAULT NULL` |
| `alcohol_strong_used_today` | `INTEGER DEFAULT 0` |
| `alcohol_strong_used_day` | `TEXT DEFAULT NULL` |
| `special_fails_today` | `INTEGER DEFAULT 0` |
| `special_blocked_until` | `TEXT DEFAULT NULL` |
| `fountain_used_day` | `TEXT DEFAULT NULL` |
| `fountain_used_today` | `INTEGER DEFAULT 0` |
| `shower_used_day` | `TEXT DEFAULT NULL` |
| `shower_used_today` | `INTEGER DEFAULT 0` |
| `fish_sold_day` | `TEXT DEFAULT NULL` |
| `fish_sold_today` | `INTEGER DEFAULT 0` |
| `forest_attempts_since_boar` | `INTEGER DEFAULT 0` |
| `forest_attempts_since_wolf` | `INTEGER DEFAULT 0` |
| `mine_attempts_since_bat` | `INTEGER DEFAULT 0` |
| `logging_attempts_since_snake` | `INTEGER DEFAULT 0` |
| `logging_attempts_since_owl` | `INTEGER DEFAULT 0` |
| `forest_sold_day` | `TEXT DEFAULT NULL` |
| `forest_sold_today` | `INTEGER DEFAULT 0` |
| `market_license_expires` | `TEXT DEFAULT NULL` |
| `callsign_free_used` | `INTEGER DEFAULT 0` |
| `wing` | `TEXT` |
| `legioner` | `INTEGER DEFAULT 0` |

## `items`

| Колонка |
|---|
| `id INTEGER PRIMARY KEY` |
| `name TEXT NOT NULL` |
| `description TEXT` |
| `photo_file_id TEXT` |
| `price INTEGER NOT NULL` |
| `sell_price INTEGER NOT NULL` |
| `rarity INTEGER DEFAULT 1` |
| `category TEXT DEFAULT 'special'` |
| `is_available INTEGER DEFAULT 1` |
| `stock INTEGER DEFAULT -1` |
| `added_by INTEGER` |
| `produced_by INTEGER` |
| `production_time_hours INTEGER DEFAULT 0` |
| `ap_cost INTEGER DEFAULT 0` |
| `heal INTEGER DEFAULT 0` |
| `armor INTEGER DEFAULT 0` |
| `drink_effect TEXT DEFAULT NULL` |
| `created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP` |

**Добавлено миграциями (`_ensure_column`):**

| Колонка | Тип |
|---|---|
| `required_status` | `TEXT` |
| `crit_chance` | `INTEGER DEFAULT 0` |
| `crit_mult` | `REAL DEFAULT 0` |
| `equip_slot` | `TEXT` |
| `damage` | `INTEGER DEFAULT 0` |
| `cure_poison` | `INTEGER DEFAULT 0` |
| `regen` | `INTEGER DEFAULT 0` |
| `cure_frostbite` | `INTEGER DEFAULT 0` |
| `market_ok` | `INTEGER DEFAULT 0` |
| `plant_name` | `TEXT` |
| `weapon_effect` | `TEXT` |
| `weapon_effect_chance` | `INTEGER DEFAULT 0` |
| `weapon_effect_dmg` | `INTEGER DEFAULT 0` |
| `housing_type` | `TEXT` |
| `housing_slots` | `INTEGER` |
| `loot_only` | `INTEGER DEFAULT 0` |

## `inventory`

| Колонка |
|---|
| `id INTEGER PRIMARY KEY` |
| `user_id INTEGER NOT NULL` |
| `item_id INTEGER NOT NULL` |
| `quantity INTEGER DEFAULT 1` |

**Добавлено миграциями (`_ensure_column`):**

| Колонка | Тип |
|---|---|
| `expires_at` | `TIMESTAMP` |
| `plant_data` | `TEXT` |

## `transactions`

| Колонка |
|---|
| `id INTEGER PRIMARY KEY` |
| `from_user INTEGER` |
| `to_user INTEGER` |
| `amount INTEGER NOT NULL` |
| `tx_type TEXT NOT NULL` |
| `description TEXT` |
| `created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP` |

## `trades`

| Колонка |
|---|
| `id INTEGER PRIMARY KEY` |
| `from_user INTEGER NOT NULL` |
| `to_user INTEGER NOT NULL` |
| `from_item_id INTEGER` |
| `from_item_qty INTEGER DEFAULT 0` |
| `from_nordmarks INTEGER DEFAULT 0` |
| `to_item_id INTEGER` |
| `to_item_qty INTEGER DEFAULT 0` |
| `to_nordmarks INTEGER DEFAULT 0` |
| `status TEXT DEFAULT 'pending'` |
| `created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP` |

## `polls`

| Колонка |
|---|
| `id INTEGER PRIMARY KEY` |
| `admin_id INTEGER NOT NULL` |
| `question TEXT NOT NULL` |
| `options TEXT NOT NULL` |
| `is_active INTEGER DEFAULT 1` |
| `created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP` |

**Добавлено миграциями (`_ensure_column`):**

| Колонка | Тип |
|---|---|
| `closed_by` | `INTEGER` |
| `closed_at` | `TIMESTAMP` |
| `closes_at` | `TIMESTAMP` |
| `is_archived` | `INTEGER DEFAULT 0` |
| `archived_day` | `TEXT DEFAULT ''` |

## `poll_votes`

| Колонка |
|---|
| `id INTEGER PRIMARY KEY` |
| `poll_id INTEGER NOT NULL` |
| `user_id INTEGER NOT NULL` |
| `option_index INTEGER NOT NULL` |
| `created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP` |

## `news_releases`

| Колонка |
|---|
| `id INTEGER PRIMARY KEY` |
| `title TEXT NOT NULL` |
| `body TEXT DEFAULT ''` |
| `photo_file_id TEXT` |
| `author_id INTEGER NOT NULL` |
| `author_name TEXT DEFAULT ''` |
| `created_at TEXT NOT NULL DEFAULT ''` |
| `edited INTEGER DEFAULT 0` |

## `daily_limits`

| Колонка |
|---|
| `admin_id INTEGER NOT NULL` |
| `date TEXT NOT NULL` |
| `spent INTEGER DEFAULT 0` |

**Составной PRIMARY KEY:** (admin_id, date)

## `treasury`

| Колонка |
|---|
| `id INTEGER PRIMARY KEY` |
| `balance INTEGER DEFAULT 0` |

## `award_monthly_paid`

| Колонка |
|---|
| `user_id INTEGER NOT NULL` |
| `award_id INTEGER NOT NULL` |
| `month TEXT NOT NULL` |
| `paid_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP` |

**Составной PRIMARY KEY:** (user_id, award_id, month)

## `role_salaries`

| Колонка |
|---|
| `role TEXT PRIMARY KEY` |
| `amount INTEGER NOT NULL DEFAULT 0` |

## `role_salary_paid`

| Колонка |
|---|
| `user_id INTEGER NOT NULL` |
| `month TEXT NOT NULL` |
| `amount INTEGER DEFAULT 0` |
| `paid_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP` |

**Составной PRIMARY KEY:** (user_id, month)

## `role_dismissal_paid`

| Колонка |
|---|
| `user_id INTEGER NOT NULL` |
| `role TEXT NOT NULL` |
| `month TEXT NOT NULL` |
| `amount INTEGER DEFAULT 0` |
| `paid_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP` |

**Составной PRIMARY KEY:** (user_id, role, month)

## `news_pub_paid`

| Колонка |
|---|
| `user_id INTEGER NOT NULL` |
| `month TEXT NOT NULL` |
| `count INTEGER DEFAULT 0` |

**Составной PRIMARY KEY:** (user_id, month)

## `settings`

| Колонка |
|---|
| `key TEXT PRIMARY KEY` |
| `value TEXT NOT NULL DEFAULT ''` |

## `library_cards`

| Колонка |
|---|
| `user_id INTEGER NOT NULL` |
| `card_type TEXT NOT NULL` |
| `expires_at TEXT NOT NULL` |

**Составной PRIMARY KEY:** (user_id, card_type)

## `library_books`

| Колонка |
|---|
| `id INTEGER PRIMARY KEY` |
| `section TEXT NOT NULL` |
| `title TEXT NOT NULL` |
| `author TEXT DEFAULT ''` |
| `description TEXT DEFAULT ''` |
| `cover_file_id TEXT` |
| `file_id TEXT` |
| `file_type TEXT` |
| `url TEXT` |
| `added_by INTEGER` |
| `created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP` |

## `interactions`

| Колонка |
|---|
| `id INTEGER PRIMARY KEY` |
| `from_user INTEGER NOT NULL` |
| `to_user INTEGER NOT NULL` |
| `interaction_type TEXT NOT NULL` |
| `state_change TEXT` |
| `created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP` |

## `duel_runs`

| Колонка |
|---|
| `id INTEGER PRIMARY KEY` |
| `challenger_id INTEGER NOT NULL` |
| `opponent_id INTEGER NOT NULL` |
| `status TEXT NOT NULL DEFAULT 'invited'` |
| `challenger_hp INTEGER NOT NULL DEFAULT 0` |
| `opponent_hp INTEGER NOT NULL DEFAULT 0` |
| `challenger_hp_max INTEGER NOT NULL DEFAULT 0` |
| `opponent_hp_max INTEGER NOT NULL DEFAULT 0` |
| `turn INTEGER NOT NULL DEFAULT 1` |
| `challenger_atk TEXT` |
| `challenger_def TEXT` |
| `opponent_atk TEXT` |
| `opponent_def TEXT` |
| `winner_id INTEGER` |
| `rating_delta INTEGER DEFAULT 0` |
| `created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP` |
| `updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP` |

**Индексы:**

- `idx_duel_runs_challenger` по (challenger_id, status)
- `idx_duel_runs_opponent` по (opponent_id, status)

## `buildings`

| Колонка |
|---|
| `id INTEGER PRIMARY KEY` |
| `name TEXT NOT NULL` |
| `description TEXT` |
| `photo_file_id TEXT` |
| `price INTEGER NOT NULL` |
| `category TEXT DEFAULT 'production'` |
| `production_type TEXT` |
| `production_item_id INTEGER` |
| `production_time_hours INTEGER DEFAULT 24` |
| `requires_resources INTEGER DEFAULT 0` |
| `created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP` |

**Добавлено миграциями (`_ensure_column`):**

| Колонка | Тип |
|---|---|
| `required_status` | `TEXT` |

## `user_buildings`

| Колонка |
|---|
| `id INTEGER PRIMARY KEY` |
| `user_id INTEGER NOT NULL` |
| `building_id INTEGER NOT NULL` |
| `level INTEGER DEFAULT 1` |
| `purchased_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP` |

## `production_queue`

| Колонка |
|---|
| `id INTEGER PRIMARY KEY` |
| `user_id INTEGER NOT NULL` |
| `building_id INTEGER NOT NULL` |
| `recipe_item_id INTEGER NOT NULL` |
| `ap_cost INTEGER NOT NULL` |
| `resources_used TEXT DEFAULT '{}'` |
| `started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP` |
| `completes_at TIMESTAMP NOT NULL` |
| `status TEXT DEFAULT 'active'` |

## `dungeon_progress`

| Колонка |
|---|
| `id INTEGER PRIMARY KEY` |
| `user_id INTEGER NOT NULL` |
| `floor INTEGER DEFAULT 1` |
| `enemies_defeated INTEGER DEFAULT 0` |
| `items_found TEXT DEFAULT '[]'` |

## `dungeon_rewards`

| Колонка |
|---|
| `id INTEGER PRIMARY KEY` |
| `user_id INTEGER NOT NULL` |
| `item_id INTEGER NOT NULL` |
| `floor INTEGER NOT NULL` |
| `created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP` |

## `dungeons`

| Колонка |
|---|
| `id INTEGER PRIMARY KEY` |
| `name TEXT NOT NULL` |
| `description TEXT` |
| `floors_count INTEGER DEFAULT 1` |
| `rooms_per_floor INTEGER DEFAULT 10` |
| `is_active INTEGER DEFAULT 1` |
| `photo_dawn TEXT` |
| `photo_day TEXT` |
| `photo_sunset TEXT` |
| `photo_night TEXT` |

**Добавлено миграциями (`_ensure_column`):**

| Колонка | Тип |
|---|---|
| `photo_water` | `TEXT` |
| `photo_rope` | `TEXT` |
| `is_training` | `INTEGER DEFAULT 0` |
| `rooms_map` | `TEXT` |

## `dungeon_enemies`

| Колонка |
|---|
| `id INTEGER PRIMARY KEY` |
| `dungeon_id INTEGER NOT NULL` |
| `floor INTEGER NOT NULL` |
| `name TEXT NOT NULL` |
| `hp INTEGER NOT NULL` |
| `attack INTEGER NOT NULL` |
| `reward_nm INTEGER DEFAULT 5` |
| `is_boss INTEGER DEFAULT 0` |
| `drops TEXT DEFAULT '[]'` |
| `dodge INTEGER DEFAULT 0` |

**Добавлено миграциями (`_ensure_column`):**

| Колонка | Тип |
|---|---|
| `image` | `TEXT` |
| `poison_chance` | `INTEGER DEFAULT 0` |
| `poison_dmg` | `INTEGER DEFAULT 0` |
| `description` | `TEXT` |
| `damage_min` | `INTEGER DEFAULT 0` |
| `damage_max` | `INTEGER DEFAULT 0` |
| `armor` | `INTEGER DEFAULT 0` |
| `dodge_chance` | `INTEGER DEFAULT 0` |
| `crit_chance` | `INTEGER DEFAULT 0` |
| `crit_mult` | `REAL DEFAULT 1.5` |
| `abilities` | `TEXT DEFAULT '[]'` |
| `admin_tuned` | `INTEGER DEFAULT 0` |
| `bleed_chance` | `INTEGER DEFAULT 0` |
| `bleed_dmg` | `INTEGER DEFAULT 0` |
| `frostbite_chance` | `INTEGER DEFAULT 0` |
| `on_hit_effects` | `TEXT DEFAULT NULL` (v0.38.0, JSON-массив эффектов при ударе) |

## `dungeon_items`

| Колонка |
|---|
| `id INTEGER PRIMARY KEY` |
| `dungeon_id INTEGER NOT NULL` |
| `floor INTEGER NOT NULL` |
| `item_id INTEGER NOT NULL` |
| `drop_chance REAL DEFAULT 0.1` |

## `player_dungeon_run`

| Колонка |
|---|
| `id INTEGER PRIMARY KEY` |
| `user_id INTEGER NOT NULL` |
| `dungeon_id INTEGER NOT NULL` |
| `floor INTEGER DEFAULT 1` |
| `room_number INTEGER DEFAULT 0` |
| `hp INTEGER DEFAULT 100` |
| `hp_max INTEGER DEFAULT 100` |
| `is_active INTEGER DEFAULT 1` |
| `started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP` |

**Добавлено миграциями (`_ensure_column`):**

| Колонка | Тип |
|---|---|
| `loot_nm` | `INTEGER DEFAULT 0` |

## `player_dungeon_inventory`

| Колонка |
|---|
| `id INTEGER PRIMARY KEY` |
| `run_id INTEGER NOT NULL` |
| `item_id INTEGER NOT NULL` |
| `quantity INTEGER DEFAULT 1` |

## `player_kvp`

| Колонка |
|---|
| `user_id INTEGER PRIMARY KEY` |
| `completions INTEGER DEFAULT 0` |
| `badge_awarded INTEGER DEFAULT 0` |
| `stick_dropped INTEGER DEFAULT 0` |

## `reports`

| Колонка |
|---|
| `id INTEGER PRIMARY KEY` |
| `user_id INTEGER NOT NULL` |
| `screenshot_file_id TEXT` |
| `troops_reported INTEGER NOT NULL` |
| `region TEXT` |
| `status TEXT DEFAULT 'pending'` |
| `reviewed_by INTEGER` |
| `created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP` |

**Добавлено миграциями (`_ensure_column`):**

| Колонка | Тип |
|---|---|
| `total_troops` | `INTEGER DEFAULT 0` |
| `credited_troops` | `INTEGER` |
| `paid` | `INTEGER DEFAULT 0` |

**Индексы:**

- `idx_reports_created` по (created_at)

## `resource_sources`

| Колонка |
|---|
| `id INTEGER PRIMARY KEY` |
| `user_id INTEGER NOT NULL` |
| `item_id INTEGER NOT NULL` |
| `building_id INTEGER` |
| `interval_days INTEGER DEFAULT 3` |
| `last_harvest TIMESTAMP` |

## `region_stats`

| Колонка |
|---|
| `region TEXT PRIMARY KEY` |
| `troops_total INTEGER DEFAULT 0` |
| `pilots_count INTEGER DEFAULT 0` |
| `computed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP` |

## `state_log`

| Колонка |
|---|
| `id INTEGER PRIMARY KEY` |
| `user_id INTEGER NOT NULL` |
| `old_state TEXT` |
| `new_state TEXT` |
| `reason TEXT` |
| `caused_by INTEGER` |
| `created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP` |

## `user_roles`

| Колонка |
|---|
| `id INTEGER PRIMARY KEY` |
| `telegram_id INTEGER NOT NULL` |
| `role TEXT NOT NULL` |
| `granted_by INTEGER` |
| `created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP` |

## `wing_commanders`

| Колонка |
|---|
| `wing TEXT PRIMARY KEY` |
| `user_id INTEGER NOT NULL` |
| `created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP` |

## `wing_deputies`

| Колонка |
|---|
| `wing TEXT PRIMARY KEY` |
| `user_id INTEGER NOT NULL` |
| `created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP` |

## `wings`

| Колонка |
|---|
| `key TEXT PRIMARY KEY` |
| `num TEXT NOT NULL DEFAULT ''` |
| `abbr TEXT NOT NULL DEFAULT ''` |
| `name TEXT NOT NULL DEFAULT ''` |
| `callsign TEXT NOT NULL DEFAULT ''` |
| `emoji TEXT NOT NULL DEFAULT ''` |
| `sort_order INTEGER DEFAULT 0` |

Сид (в коде): `1`–`4` (крылья/спецотряд) + `reserve` («🪖 Резерв», sort_order 99) —
пилоты без формирования (`users.wing` NULL → `reserve`, миграция `mig_reserve_wing`).

## `admin_logs`

| Колонка |
|---|
| `id INTEGER PRIMARY KEY` |
| `admin_id INTEGER NOT NULL` |
| `action TEXT NOT NULL` |
| `target_id INTEGER` |
| `details TEXT` |
| `created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP` |

## `report_notify_tiers`

| Колонка |
|---|
| `user_id INTEGER NOT NULL` |
| `day TEXT NOT NULL` |
| `tier INTEGER NOT NULL DEFAULT 0` |
| `updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP` |

**Составной PRIMARY KEY:** (user_id, day)

## `activity_log`

| Колонка |
|---|
| `id INTEGER PRIMARY KEY` |
| `user_id INTEGER NOT NULL` |
| `action TEXT NOT NULL` |
| `details TEXT` |
| `created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP` |

**Индексы:**

- `idx_activity_user` по (user_id, id)

## `ap_log`

| Колонка |
|---|
| `id INTEGER PRIMARY KEY` |
| `user_id INTEGER NOT NULL` |
| `delta INTEGER NOT NULL` |
| `ap_before INTEGER NOT NULL` |
| `ap_after INTEGER NOT NULL` |
| `reason TEXT` |
| `created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP` |

**Индексы:**

- `idx_ap_user` по (user_id, id)

## `location_visits`

| Колонка |
|---|
| `id INTEGER PRIMARY KEY` |
| `user_id INTEGER NOT NULL` |
| `location_key TEXT NOT NULL` |
| `created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP` |

**Индексы:**

- `idx_locvis_user` по (user_id, id)
- `idx_locvis_loc` по (location_key, created_at)

## `booklet_visits`

| Колонка |
|---|
| `user_id INTEGER NOT NULL` |
| `location_key TEXT NOT NULL` |
| `visited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP` |

**Составной PRIMARY KEY:** (user_id, location_key)

## `booklet_claims`

| Колонка |
|---|
| `user_id INTEGER PRIMARY KEY` |
| `claimed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP` |

## `nii_reports`

| Колонка |
|---|
| `id INTEGER PRIMARY KEY` |
| `user_id INTEGER NOT NULL` |
| `text TEXT NOT NULL` |
| `photo_file_id TEXT` |
| `status TEXT DEFAULT 'open'` |
| `created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP` |

**Индексы:**

- `idx_nii_user` по (user_id, id)
- `idx_nii_created` по (created_at)

## `locations`

| Колонка |
|---|
| `id INTEGER PRIMARY KEY` |
| `key TEXT NOT NULL` |
| `name TEXT NOT NULL` |
| `description TEXT` |
| `access_mode TEXT NOT NULL DEFAULT 'all'` |
| `required_status TEXT` |
| `blocking_states TEXT DEFAULT '[]'` |
| `preview_photo TEXT` |
| `photo_dawn TEXT` |
| `photo_day TEXT` |
| `photo_sunset TEXT` |
| `photo_night TEXT` |
| `sort_order INTEGER DEFAULT 0` |
| `created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP` |

**Добавлено миграциями (`_ensure_column`):**

| Колонка | Тип |
|---|---|
| `visits` | `INTEGER DEFAULT 0` |
| `season_photos` | `TEXT DEFAULT NULL` |
| `glade_photo` | `TEXT DEFAULT NULL` |
| `clearing_photo` | `TEXT DEFAULT NULL` |
| `mine_level_photo` | `TEXT DEFAULT NULL` |
| `storage_photo` | `TEXT DEFAULT NULL` |
| `logging_photo` | `TEXT DEFAULT NULL` |

## `park_statues`

| Колонка |
|---|
| `id INTEGER PRIMARY KEY` |
| `name TEXT NOT NULL` |
| `description TEXT` |
| `image_dawn TEXT` |
| `image_day TEXT` |
| `image_sunset TEXT` |
| `image_night TEXT` |
| `created_by INTEGER` |
| `sort_order INTEGER DEFAULT 0` |
| `created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP` |

## `fish_catches`

| Колонка |
|---|
| `id INTEGER PRIMARY KEY` |
| `user_id INTEGER NOT NULL` |
| `item_id INTEGER NOT NULL` |
| `weight INTEGER NOT NULL DEFAULT 1` |
| `created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP` |
| `sold_at TIMESTAMP` |

**Добавлено миграциями (`_ensure_column`):**

| Колонка | Тип |
|---|---|
| `expires_at` | `TIMESTAMP` |
| `kind` | `TEXT DEFAULT 'fish'` |

**Индексы:**

- `idx_fish_catches_user` по (user_id, sold_at)

## `market_fish`

| Колонка |
|---|
| `id INTEGER PRIMARY KEY` |
| `seller_id INTEGER NOT NULL` |
| `item_id INTEGER NOT NULL` |
| `weight INTEGER NOT NULL DEFAULT 1` |
| `price INTEGER NOT NULL` |
| `remaining_sec INTEGER NOT NULL` |
| `created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP` |

**Добавлено миграциями (`_ensure_column`):**

| Колонка | Тип |
|---|---|
| `base_price` | `INTEGER DEFAULT 0` |

**Индексы:**

- `idx_market_fish` по (created_at)

## `market_items`

| Колонка |
|---|
| `id INTEGER PRIMARY KEY` |
| `seller_id INTEGER NOT NULL` |
| `item_id INTEGER NOT NULL` |
| `price INTEGER NOT NULL` |
| `created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP` |

**Индексы:**

- `idx_market_items` по (created_at)

## `statuses`

| Колонка |
|---|
| `id INTEGER PRIMARY KEY` |
| `name TEXT NOT NULL` |
| `access_tag TEXT` |
| `description TEXT` |
| `sort_order INTEGER DEFAULT 0` |
| `created_by INTEGER` |
| `created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP` |

## `user_statuses`

| Колонка |
|---|
| `id INTEGER PRIMARY KEY` |
| `user_id INTEGER NOT NULL` |
| `status_id INTEGER NOT NULL` |
| `granted_by INTEGER` |
| `is_selected INTEGER DEFAULT 0` |
| `created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP` |

## `awards`

| Колонка |
|---|
| `id INTEGER PRIMARY KEY` |
| `name TEXT NOT NULL` |
| `description TEXT` |
| `emoji TEXT DEFAULT '🏅'` |
| `created_by INTEGER` |
| `created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP` |

**Добавлено миграциями (`_ensure_column`):**

| Колонка | Тип |
|---|---|
| `image` | `TEXT` |
| `bonus_attack` | `INTEGER DEFAULT 0` |
| `bonus_defense` | `INTEGER DEFAULT 0` |
| `bonus_dodge` | `INTEGER DEFAULT 0` |
| `bonus_fishing` | `INTEGER DEFAULT 0` |
| `bonus_hp` | `INTEGER DEFAULT 0` |
| `bonus_crit` | `INTEGER DEFAULT 0` |
| `bonus_shop_discount` | `INTEGER DEFAULT 0` |
| `bonus_report_tax` | `INTEGER DEFAULT 0` |
| `reward_nm` | `INTEGER DEFAULT 0` |
| `monthly_nm` | `INTEGER DEFAULT 0` |
| `achievement_key` | `TEXT DEFAULT NULL` |
| `achievement_level` | `INTEGER DEFAULT 0` |
| `bonus_json` | `TEXT DEFAULT '{}'` |

## `user_awards`

| Колонка |
|---|
| `id INTEGER PRIMARY KEY` |
| `user_id INTEGER NOT NULL` |
| `award_id INTEGER NOT NULL` |
| `granted_by INTEGER` |
| `comment TEXT` |
| `created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP` |

## `user_achievements`

| Колонка |
|---|
| `user_id INTEGER NOT NULL` |
| `akey TEXT NOT NULL` |
| `level INTEGER NOT NULL DEFAULT 0` |
| `progress INTEGER NOT NULL DEFAULT 0` |
| `updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP` |

**Составной PRIMARY KEY:** (user_id, akey)

## `city_storage`

| Колонка |
|---|
| `item_id INTEGER PRIMARY KEY` |
| `qty INTEGER NOT NULL DEFAULT 0` |
| `updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP` |

**FOREIGN KEY:** item_id → items(id)

## `player_housing`

| Колонка |
|---|
| `user_id INTEGER PRIMARY KEY` |
| `housing_type TEXT DEFAULT 'municipal'` |
| `purchased_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP` |

**Добавлено миграциями (`_ensure_column`):**

| Колонка | Тип |
|---|---|
| `expansions_installed` | `INTEGER DEFAULT 0` |
| `tax_last_check` | `TEXT DEFAULT NULL` |
| `tax_unpaid_months` | `INTEGER DEFAULT 0` |
| `housing_label` | `TEXT` |
| `housing_slots` | `INTEGER` |

## `housing_slots`

| Колонка |
|---|
| `id INTEGER PRIMARY KEY` |
| `user_id INTEGER NOT NULL` |
| `slot_index INTEGER NOT NULL` |
| `expansion_type TEXT` |
| `expansion_level INTEGER DEFAULT 1` |
| `plant_data TEXT DEFAULT '{}'` |

**Добавлено миграциями (`_ensure_column`):**

| Колонка | Тип |
|---|---|
| `embedded` | `INTEGER DEFAULT 0` |

## `recipes`

| Колонка |
|---|
| `id INTEGER PRIMARY KEY` |
| `name TEXT NOT NULL` |
| `description TEXT` |
| `result_item_name TEXT NOT NULL` |
| `result_quantity INTEGER DEFAULT 1` |
| `required_expansion TEXT` |
| `required_level INTEGER DEFAULT 1` |
| `ingredients TEXT NOT NULL DEFAULT '[]'` |
| `ap_cost INTEGER DEFAULT 0` |
| `production_time INTEGER DEFAULT 30` |
| `rarity INTEGER DEFAULT 1` |
| `is_available INTEGER DEFAULT 1` |
| `created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP` |

## `water_fish`

| Колонка |
|---|
| `id INTEGER PRIMARY KEY` |
| `water TEXT NOT NULL` |
| `item_id INTEGER NOT NULL` |
| `day_weight INTEGER DEFAULT 0` |
| `night_weight INTEGER DEFAULT 0` |
| `photo_file_id TEXT` |
| `admin_tuned INTEGER DEFAULT 0` |
| `super_rare INTEGER DEFAULT 0` |

**Добавлено миграциями (`_ensure_column`):**

| Колонка | Тип |
|---|---|
| `excluded` | `INTEGER DEFAULT 0` |
| `kind` | `TEXT DEFAULT 'fish'` |

## `water_junk`

| Колонка |
|---|
| `id INTEGER PRIMARY KEY` |
| `water TEXT NOT NULL` |
| `name TEXT NOT NULL` |
| `chance INTEGER DEFAULT 15` |
| `photo_file_id TEXT` |
| `admin_tuned INTEGER DEFAULT 0` |

## `forest_mushrooms`

| Колонка |
|---|
| `id INTEGER PRIMARY KEY` |
| `item_id INTEGER NOT NULL` |
| `chance INTEGER DEFAULT 10` |
| `kind TEXT DEFAULT 'edible'` |
| `photo_file_id TEXT` |
| `admin_tuned INTEGER DEFAULT 0` |
| `excluded INTEGER DEFAULT 0` |
| `zone TEXT DEFAULT 'clearing'` |

## `forest_enemies`

| Колонка |
|---|
| `id INTEGER PRIMARY KEY` |
| `key TEXT` |
| `spot TEXT DEFAULT 'forest'` |
| `name TEXT NOT NULL` |
| `hp INTEGER DEFAULT 30` |
| `dmg_min INTEGER DEFAULT 5` |
| `dmg_max INTEGER DEFAULT 9` |
| `dodge INTEGER DEFAULT 0` |
| `loss_ap INTEGER DEFAULT 0` |
| `bleed_chance INTEGER DEFAULT 0` |
| `bleed_dmg INTEGER DEFAULT 0` |
| `chance REAL DEFAULT 0` |
| `pity_target INTEGER DEFAULT 0` |
| `reward_nm INTEGER DEFAULT 0` |
| `drops TEXT DEFAULT '[]'` |
| `description TEXT` |
| `image TEXT` |
| `photo_key TEXT` |
| `enabled INTEGER DEFAULT 1` |
| `admin_tuned INTEGER DEFAULT 0` |

**Добавлено миграциями (`_ensure_column`):**

| Колонка | Тип |
|---|---|
| `armor` | `INTEGER DEFAULT 0` |
| `dodge_chance` | `INTEGER DEFAULT 0` |
| `crit_chance` | `INTEGER DEFAULT 0` |
| `crit_mult` | `REAL DEFAULT 1.5` |
| `abilities` | `TEXT DEFAULT '[]'` |
| `on_hit_effects` | `TEXT DEFAULT NULL` (v0.38.0, JSON-массив эффектов при ударе) |

## `fishing_enemies`

| Колонка |
|---|
| `id INTEGER PRIMARY KEY` |
| `key TEXT` |
| `spot TEXT DEFAULT 'reservoir'` |
| `name TEXT NOT NULL` |
| `hp INTEGER DEFAULT 30` |
| `dmg_min INTEGER DEFAULT 5` |
| `dmg_max INTEGER DEFAULT 9` |
| `dodge INTEGER DEFAULT 0` |
| `loss_ap INTEGER DEFAULT 0` |
| `bleed_chance INTEGER DEFAULT 0` |
| `bleed_dmg INTEGER DEFAULT 0` |
| `chance REAL DEFAULT 0` |
| `pity_target INTEGER DEFAULT 0` |
| `reward_nm INTEGER DEFAULT 0` |
| `drops TEXT DEFAULT '[]'` |
| `description TEXT` |
| `image TEXT` |
| `photo_key TEXT` |
| `enabled INTEGER DEFAULT 1` |
| `admin_tuned INTEGER DEFAULT 0` |

**Добавлено миграциями (`_ensure_column`):**

| Колонка | Тип |
|---|---|
| `on_hit_effects` | `TEXT DEFAULT NULL` (v0.38.0, JSON-массив эффектов при ударе) |

## `mine_enemies`

| Колонка |
|---|
| `id INTEGER PRIMARY KEY` |
| `key TEXT` |
| `spot TEXT DEFAULT 'iron'` |
| `name TEXT NOT NULL` |
| `hp INTEGER DEFAULT 30` |
| `dmg_min INTEGER DEFAULT 5` |
| `dmg_max INTEGER DEFAULT 9` |
| `dodge INTEGER DEFAULT 0` |
| `loss_ap INTEGER DEFAULT 0` |
| `bleed_chance INTEGER DEFAULT 0` |
| `bleed_dmg INTEGER DEFAULT 0` |
| `chance REAL DEFAULT 0` |
| `pity_target INTEGER DEFAULT 0` |
| `reward_nm INTEGER DEFAULT 0` |
| `drops TEXT DEFAULT '[]'` |
| `description TEXT` |
| `image TEXT` |
| `photo_key TEXT` |
| `enabled INTEGER DEFAULT 1` |
| `admin_tuned INTEGER DEFAULT 0` |

**Добавлено миграциями (`_ensure_column`):**

| Колонка | Тип |
|---|---|
| `armor` | `INTEGER DEFAULT 0` |
| `dodge_chance` | `INTEGER DEFAULT 0` |
| `crit_chance` | `INTEGER DEFAULT 0` |
| `crit_mult` | `REAL DEFAULT 1.5` |
| `abilities` | `TEXT DEFAULT '[]'` |
| `on_hit_effects` | `TEXT DEFAULT NULL` (v0.38.0, JSON-массив эффектов при ударе) |

## `logging_enemies`

Враги Лесозаготовки (v0.37.0): Лесная змея (`snake`) и Неясыть (`owl`).
Набор колонок повторяет `mine_enemies`; миграции добавляют те же колонки,
что и у копи (`armor`, `dodge_chance`, `crit_chance`, `crit_mult`, `abilities`).
v0.38.0: колонка `on_hit_effects` (у `snake` — яд, у `owl` — «ослеплён»).

| Колонка |
|---|
| `id INTEGER PRIMARY KEY` |
| `key TEXT` |
| `spot TEXT DEFAULT 'logging'` |
| `name TEXT NOT NULL` |
| `hp INTEGER DEFAULT 30` |
| `dmg_min INTEGER DEFAULT 5` |
| `dmg_max INTEGER DEFAULT 9` |
| `dodge INTEGER DEFAULT 0` |
| `loss_ap INTEGER DEFAULT 0` |
| `bleed_chance INTEGER DEFAULT 0` |
| `bleed_dmg INTEGER DEFAULT 0` |
| `chance REAL DEFAULT 0` |
| `pity_target INTEGER DEFAULT 0` |
| `reward_nm INTEGER DEFAULT 0` |
| `drops TEXT DEFAULT '[]'` |
| `description TEXT` |
| `image TEXT` |
| `photo_key TEXT` |
| `enabled INTEGER DEFAULT 1` |
| `admin_tuned INTEGER DEFAULT 0` |

## `wall_posts`

| Колонка |
|---|
| `id INTEGER PRIMARY KEY` |
| `user_id INTEGER NOT NULL` |
| `text TEXT NOT NULL` |
| `created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP` |
| `created_day TEXT NOT NULL DEFAULT ''` |
| `tier INTEGER DEFAULT 0` |
| `cost INTEGER DEFAULT 0` |

## `wall_archives`

| Колонка |
|---|
| `id INTEGER PRIMARY KEY` |
| `title TEXT NOT NULL` |
| `period_start TEXT NOT NULL DEFAULT ''` |
| `period_end TEXT NOT NULL DEFAULT ''` |
| `post_count INTEGER DEFAULT 0` |
| `archived_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP` |

## `wall_archive_posts`

| Колонка |
|---|
| `id INTEGER PRIMARY KEY` |
| `archive_id INTEGER NOT NULL` |
| `post_id INTEGER NOT NULL` |
| `user_id INTEGER NOT NULL` |
| `text TEXT NOT NULL` |
| `created_at TEXT NOT NULL DEFAULT ''` |
| `created_day TEXT NOT NULL DEFAULT ''` |
| `cost INTEGER DEFAULT 0` |
| `tier INTEGER DEFAULT 0` |

## `clans`

| Колонка |
|---|
| `id INTEGER PRIMARY KEY` |
| `kind TEXT NOT NULL DEFAULT 'clan'` |
| `name TEXT NOT NULL` |
| `description TEXT DEFAULT ''` |
| `photo_file_id TEXT` |
| `leader_id INTEGER` |
| `created_by INTEGER` |
| `created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP` |

## `clan_members`

| Колонка |
|---|
| `clan_id INTEGER NOT NULL` |
| `user_id INTEGER NOT NULL` |
| `joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP` |

**Составной PRIMARY KEY:** (clan_id, user_id)

## `clan_requests`

| Колонка |
|---|
| `clan_id INTEGER NOT NULL` |
| `user_id INTEGER NOT NULL` |
| `created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP` |

**Составной PRIMARY KEY:** (clan_id, user_id)

## `clan_storage`

| Колонка |
|---|
| `clan_id INTEGER NOT NULL` |
| `item_id INTEGER NOT NULL` |
| `qty INTEGER NOT NULL DEFAULT 0` |
| `updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP` |

**Составной PRIMARY KEY:** (clan_id, item_id)

**Индексы:**

- `idx_clan_storage_clan` по (clan_id)

## `clan_build_contrib`

| Колонка |
|---|
| `id INTEGER PRIMARY KEY AUTOINCREMENT` |
| `clan_id INTEGER NOT NULL` |
| `user_id INTEGER NOT NULL` |
| `item_id INTEGER NOT NULL` |
| `qty INTEGER NOT NULL` |
| `created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP` |

**Индексы:**

- `idx_clan_contrib_clan` по (clan_id)

## `clan_buildings`

| Колонка |
|---|
| `clan_id INTEGER PRIMARY KEY` |
| `building_type TEXT` |
| `target_type TEXT` |
| `status TEXT NOT NULL DEFAULT 'choosing'` |
| `required_json TEXT` |
| `price_nm INTEGER DEFAULT 0` |
| `chosen_at TIMESTAMP` |
| `started_at TIMESTAMP` |
| `completes_at TIMESTAMP` |
| `updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP` |
| `building_photo_file_id TEXT` |

## `user_recipes`

| Колонка |
|---|
| `user_id INTEGER NOT NULL` |
| `recipe_id INTEGER NOT NULL` |
| `learned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP` |

**Составной PRIMARY KEY:** (user_id, recipe_id)
