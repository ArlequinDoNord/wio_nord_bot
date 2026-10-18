# Карта FSM-состояний и callback-неймспейсов N.O.R.D.

> **Сгенерировано** `tools/export_states.py`. Не редактировать вручную —
> правь код и перегенерируй: `.venv\Scripts\python.exe tools/export_states.py`.
>
> Назначение: единый обзор всех `StatesGroup`, где они ставятся и где ловятся,
> а также реестр `callback_data` — чтобы не допускать конфликтов меню/хендлеров.

Всего классов состояний: **48**; полей-состояний: **209**; уникальных `callback_data`: **250**.

## 1. Классы состояний по модулям

### `AdminAddItem` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `name` | `bot/handlers/admin.py:1202` `shop_admin_add`<br>`bot/handlers/admin.py:5891` `enemy_drop_new_item` | `bot/handlers/admin.py:1210` `add_item_name` |
| `desc` | `bot/handlers/admin.py:1212` `add_item_name` | `bot/handlers/admin.py:1218` `add_item_desc` |
| `price` | `bot/handlers/admin.py:1221` `add_item_desc` | `bot/handlers/admin.py:1227` `add_item_price` |
| `sell_price` | `bot/handlers/admin.py:1237` `add_item_price` | `bot/handlers/admin.py:1243` `add_item_sell_price` |
| `rarity` | `bot/handlers/admin.py:1255` `add_item_sell_price` | — |
| `category` | `bot/handlers/admin.py:1264` `add_item_rarity` | — |
| `drink` | `bot/handlers/admin.py:1287` `add_item_category` | — |
| `plant_name` | `bot/handlers/admin.py:1276` `add_item_category` | `bot/handlers/admin.py:1312` `add_item_plant_name` |
| `stock` | `bot/handlers/admin.py:1296` `add_item_category`<br>`bot/handlers/admin.py:1306` `add_item_drink_choice`<br>`bot/handlers/admin.py:1315` `add_item_plant_name` | `bot/handlers/admin.py:1321` `add_item_stock` |
| `stats` | `bot/handlers/admin.py:1335` `add_item_stock`<br>`bot/handlers/admin.py:1340` `add_item_stock` | `bot/handlers/admin.py:1348` `add_item_stats`<br>`bot/handlers/admin.py:1388` `add_item_stats_bad` |
| `equip_slot` | `bot/handlers/admin.py:1365` `add_item_stats` | — |
| `weapon_effect` | `bot/handlers/admin.py:1353` `add_item_stats` | — |
| `weapon_effect_chance` | `bot/handlers/admin.py:1401` `add_item_weapon_effect_cb` | `bot/handlers/admin.py:1410` `add_item_weapon_effect_chance` |
| `weapon_effect_dmg` | `bot/handlers/admin.py:1422` `add_item_weapon_effect_chance` | `bot/handlers/admin.py:1434` `add_item_weapon_effect_dmg` |
| `producer` | `bot/handlers/admin.py:1449` `_go_add_item_producer` | — |
| `producer_user` | `bot/handlers/admin.py:1464` `add_item_producer` | `bot/handlers/admin.py:1476` `add_item_producer_user` |
| `market` | `bot/handlers/admin.py:1487` `_go_add_item_market` | — |
| `loot` | `bot/handlers/admin.py:1509` `_go_add_item_loot` | — |
| `status` | `bot/handlers/admin.py:1537` `_go_add_item_status` | — |
| `photo` | `bot/handlers/admin.py:1556` `add_item_status_cb` | `bot/handlers/admin.py:1564` `add_item_photo` |

### `AdminSaleTax` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `percent` | `bot/handlers/admin.py:2446` `admin_saletax_view` | `bot/handlers/admin.py:2460` `admin_saletax_set` |

### `AdminSpecialCode` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `code` | `bot/handlers/admin.py:2488` `admin_special_code_view` | `bot/handlers/admin.py:2503` `admin_special_code_set` |

### `AdminEditItem` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `item_id` | — | — |
| `field` | `bot/handlers/admin.py:1792` `edit_item_pick` | — |
| `value` | `bot/handlers/admin.py:2096` `edit_item_field` | `bot/handlers/admin.py:2107` `edit_item_value` |
| `photo` | `bot/handlers/admin.py:1881` `edit_item_field_photo` | `bot/handlers/admin.py:1931` `edit_item_photo` |

### `AdminFinance` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | `bot/handlers/admin.py:2526` `finance_manual`<br>`bot/handlers/admin.py:2543` `finance_pick` | `bot/handlers/admin.py:2604` `finance_target` |
| `currency` | — | — |
| `amount` | `bot/handlers/admin.py:448` `pickuser_cb`<br>`bot/handlers/admin.py:2573` `finance_pick_user`<br>`bot/handlers/admin.py:2611` `finance_target` | `bot/handlers/admin.py:2619` `finance_amount` |

### `AdminTreasury` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `amount` | `bot/handlers/admin.py:2353` `treasury_give` | `bot/handlers/admin.py:2363` `treasury_amount` |
| `target` | `bot/handlers/admin.py:2379` `treasury_amount` | `bot/handlers/admin.py:2385` `treasury_target_manual` |

### `AdminStorageRestock` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `amount` | `bot/handlers/admin.py:1064` `storage_restock` | `bot/handlers/admin.py:1078` `storage_restock_amount` |

### `AdminStorageDelete` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `confirm` | `bot/handlers/admin.py:1136` `storage_purge` | `bot/handlers/admin.py:1150` `storage_purge_confirm` |

### `AdminTax` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `percent` | `bot/handlers/admin.py:2409` `admin_tax_view` | `bot/handlers/admin.py:2421` `admin_tax_set` |

### `AdminReportAutoApprove` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `value` | `bot/handlers/admin.py:4161` `report_auto_approve_edit_cb` | `bot/handlers/admin.py:4174` `report_auto_approve_edit_value` |

### `AdminReportPayCap` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `value` | `bot/handlers/admin.py:4200` `report_pay_cap_edit_cb` | `bot/handlers/admin.py:4215` `report_pay_cap_edit_value` |

### `AdminReportFix` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `daily` | `bot/handlers/admin.py:4401` `report_fix_start` | `bot/handlers/admin.py:4414` `report_fix_daily` |
| `total` | `bot/handlers/admin.py:4428` `report_fix_daily` | `bot/handlers/admin.py:4442` `report_fix_total` |

### `AdminRoles` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | `bot/handlers/admin.py:2692` `admin_roles` | `bot/handlers/admin.py:2701` `roles_target` |
| `action` | `bot/handlers/admin.py:451` `pickuser_cb`<br>`bot/handlers/admin.py:2707` `roles_target` | — |
| `role` | `bot/handlers/admin.py:2725` `roles_action` | — |

### `AdminStatuses` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `name` | `bot/handlers/admin.py:2976` `status_create_start` | `bot/handlers/admin.py:2984` `status_create_name` |
| `tag` | `bot/handlers/admin.py:2986` `status_create_name` | `bot/handlers/admin.py:2995` `status_create_tag` |
| `level` | `bot/handlers/admin.py:3002` `status_create_tag` | `bot/handlers/admin.py:3012` `status_create_level` |
| `desc` | `bot/handlers/admin.py:3023` `status_create_level` | `bot/handlers/admin.py:3028` `status_create_desc` |
| `target` | `bot/handlers/admin.py:3249` `status_grant_target`<br>`bot/handlers/admin.py:3318` `status_revoke_target` | `bot/handlers/admin.py:3259` `status_grant_target_msg` |
| `grant_action` | — | — |
| `status_pick` | `bot/handlers/admin.py:466` `pickuser_cb`<br>`bot/handlers/admin.py:475` `pickuser_cb`<br>`bot/handlers/admin.py:3270` `status_grant_target_msg`<br>`bot/handlers/admin.py:3395` `status_grant_more` | — |
| `item_pick` | — | — |
| `item_status` | — | — |

### `AdminAwards` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `name` | `bot/handlers/admin.py:3484` `award_create_start` | `bot/handlers/admin.py:3541` `award_create_name` |
| `desc` | `bot/handlers/admin.py:3547` `award_create_name` | `bot/handlers/admin.py:3555` `award_create_desc` |
| `emoji` | `bot/handlers/admin.py:3558` `award_create_desc` | `bot/handlers/admin.py:3566` `award_create_emoji` |
| `bonus` | `bot/handlers/admin.py:3532` `_award_ask_bonus` | `bot/handlers/admin.py:3574` `award_create_bonus` |
| `preview` | `bot/handlers/admin.py:3520` `_award_ask_bonus` | — |
| `target` | `bot/handlers/admin.py:3960` `award_grant_target` | `bot/handlers/admin.py:3966` `award_grant_target_msg` |
| `award_pick` | `bot/handlers/admin.py:4041` `award_revoke_pick_user` | — |
| `comment` | `bot/handlers/admin.py:3984` `award_grant_pick` | `bot/handlers/admin.py:4001` `award_grant_comment` |
| `edit_value` | `bot/handlers/admin.py:3840` `award_edit_field_pick` | `bot/handlers/admin.py:3864` `award_edit_value` |

### `AdminFishing` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `water` | — | — |
| `wf_id` | — | — |
| `value` | `bot/handlers/admin.py:6452` `admin_fishing_junk_field_pick`<br>`bot/handlers/admin.py:6866` `admin_fishing_field_pick` | `bot/handlers/admin.py:6893` `admin_fishing_value` |
| `c_name` | `bot/handlers/admin.py:6703` `admin_fishing_new` | `bot/handlers/admin.py:6712` `admin_fishing_new_name` |
| `c_desc` | `bot/handlers/admin.py:6722` `admin_fishing_new_name` | `bot/handlers/admin.py:6728` `admin_fishing_new_desc` |
| `c_sell_price` | `bot/handlers/admin.py:6731` `admin_fishing_new_desc` | `bot/handlers/admin.py:6737` `admin_fishing_new_sell_price` |
| `c_day_weight` | `bot/handlers/admin.py:6745` `admin_fishing_new_sell_price` | `bot/handlers/admin.py:6753` `admin_fishing_new_day_weight` |
| `c_night_weight` | `bot/handlers/admin.py:6761` `admin_fishing_new_day_weight` | `bot/handlers/admin.py:6769` `admin_fishing_new_night_weight` |
| `c_photo` | `bot/handlers/admin.py:6801` `admin_fishing_new_super` | `bot/handlers/admin.py:6809` `admin_fishing_new_photo` |
| `c_super_rare` | `bot/handlers/admin.py:6777` `admin_fishing_new_night_weight` | — |

### `AdminForest` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `f_id` | — | — |
| `field` | — | — |
| `value` | `bot/handlers/admin.py:7448` `admin_forest_field_pick` | `bot/handlers/admin.py:7474` `admin_forest_value` |
| `c_name` | `bot/handlers/admin.py:7530` `admin_forest_new` | `bot/handlers/admin.py:7539` `admin_forest_new_name` |
| `c_desc` | `bot/handlers/admin.py:7549` `admin_forest_new_name` | `bot/handlers/admin.py:7555` `admin_forest_new_desc` |
| `c_sell_price` | `bot/handlers/admin.py:7558` `admin_forest_new_desc` | `bot/handlers/admin.py:7564` `admin_forest_new_sell_price` |
| `c_chance` | `bot/handlers/admin.py:7571` `admin_forest_new_sell_price` | `bot/handlers/admin.py:7580` `admin_forest_new_chance` |
| `c_kind` | `bot/handlers/admin.py:7588` `admin_forest_new_chance` | — |
| `c_photo` | `bot/handlers/admin.py:7611` `admin_forest_new_kind` | `bot/handlers/admin.py:7619` `admin_forest_new_photo` |
| `zone_value` | `bot/handlers/admin.py:7128` `admin_forest_zone_chance`<br>`bot/handlers/admin.py:7203` `admin_forest_zone_set_pick`<br>`bot/handlers/admin.py:7216` `admin_forest_limit_set` | `bot/handlers/admin.py:7223` `admin_forest_zone_value` |

### `AdminEnemy` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `field` | `bot/handlers/admin.py:8893` `admin_enemies_field_pick` | `bot/handlers/admin.py:8899` `admin_enemies_field_value` |
| `photo` | `bot/handlers/admin.py:8950` `admin_enemies_photo_pick` | `bot/handlers/admin.py:8956` `admin_enemies_photo_value` |
| `drop_chance` | `bot/handlers/admin.py:9110` `admin_enemies_drop_edit_chance`<br>`bot/handlers/admin.py:9184` `admin_enemies_drop_add_pick` | `bot/handlers/admin.py:9190` `admin_enemies_drop_chance_value` |
| `drop_qty` | `bot/handlers/admin.py:9123` `admin_enemies_drop_edit_qty`<br>`bot/handlers/admin.py:9211` `admin_enemies_drop_chance_value` | `bot/handlers/admin.py:9217` `admin_enemies_drop_qty_value` |
| `c_name` | `bot/handlers/admin.py:9256` `admin_enemies_new` | `bot/handlers/admin.py:9261` `admin_enemies_new_name` |
| `c_hp` | `bot/handlers/admin.py:9267` `admin_enemies_new_name` | `bot/handlers/admin.py:9272` `admin_enemies_new_hp` |
| `c_dmg` | `bot/handlers/admin.py:9278` `admin_enemies_new_hp` | `bot/handlers/admin.py:9283` `admin_enemies_new_dmg` |
| `c_dodge` | `bot/handlers/admin.py:9296` `admin_enemies_new_dmg` | `bot/handlers/admin.py:9301` `admin_enemies_new_dodge` |
| `c_chance` | `bot/handlers/admin.py:9307` `admin_enemies_new_dodge` | `bot/handlers/admin.py:9313` `admin_enemies_new_chance` |
| `c_loss_ap` | `bot/handlers/admin.py:9319` `admin_enemies_new_chance` | `bot/handlers/admin.py:9325` `admin_enemies_new_done` |

### `AdminCallsign` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | `bot/handlers/admin.py:749` `admin_callsign_start` | `bot/handlers/admin.py:770` `admin_callsign_target_msg` |
| `value` | `bot/handlers/admin.py:533` `pickuser_cb`<br>`bot/handlers/admin.py:780` `admin_callsign_target_msg` | `bot/handlers/admin.py:791` `admin_callsign_value_msg` |

### `AdminWing` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | `bot/handlers/admin.py:762` `admin_wing_start` | — |
| `value` | `bot/handlers/admin.py:544` `pickuser_cb` | — |

### `AdminStates` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | `bot/handlers/admin.py:4937` `admin_states_menu` | `bot/handlers/admin.py:4946` `admin_states_target_text` |
| `action` | `bot/handlers/admin.py:505` `pickuser_cb`<br>`bot/handlers/admin.py:4952` `admin_states_target_text` | — |
| `state_key` | `bot/handlers/admin.py:4978` `admin_states_op` | — |
| `minutes` | `bot/handlers/admin.py:5003` `admin_states_key` | `bot/handlers/admin.py:5012` `admin_states_minutes`<br>`bot/handlers/admin.py:5033` `admin_states_minutes_bad` |

### `AdminPlayerLog` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | `bot/handlers/admin.py:735` `admin_player_log_start` | `bot/handlers/admin.py:605` `admin_player_log_manual_msg` |

### `AdminSalary` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | — | — |
| `amount` | `bot/handlers/admin.py:518` `pickuser_cb` | `bot/handlers/admin.py:5114` `admin_salary_amount` |
| `period` | `bot/handlers/admin.py:5142` `admin_salary_amount` | `bot/handlers/admin.py:5154` `admin_salary_period_cb`<br>`bot/handlers/admin.py:5173` `admin_salary_period_text` |

### `AdminLocation` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `action` | — | — |
| `target_id` | — | — |
| `key` | `bot/handlers/admin.py:7674` `loc_create` | `bot/handlers/admin.py:7938` `loc_step_key` |
| `name` | `bot/handlers/admin.py:7944` `loc_step_key` | `bot/handlers/admin.py:7949` `loc_step_name` |
| `set_name` | `bot/handlers/admin.py:7965` `loc_set_name` | `bot/handlers/admin.py:7976` `loc_step_set_name` |
| `description` | `bot/handlers/admin.py:7951` `loc_step_name`<br>`bot/handlers/admin.py:7990` `loc_step_set_name`<br>`bot/handlers/admin.py:8004` `loc_set_desc` | `bot/handlers/admin.py:8206` `loc_step_desc` |
| `mode` | `bot/handlers/admin.py:7770` `loc_set_mode`<br>`bot/handlers/admin.py:8217` `loc_step_desc` | `bot/handlers/admin.py:7783` `loc_mode_chosen` |
| `req_status` | `bot/handlers/admin.py:7796` `loc_mode_chosen`<br>`bot/handlers/admin.py:7805` `loc_mode_chosen`<br>`bot/handlers/admin.py:7814` `loc_set_status` | `bot/handlers/admin.py:7819` `loc_req_status_chosen` |
| `blocking` | `bot/handlers/admin.py:7802` `loc_mode_chosen`<br>`bot/handlers/admin.py:7833` `loc_req_status_chosen`<br>`bot/handlers/admin.py:7849` `loc_set_blocking` | `bot/handlers/admin.py:7854` `loc_blocking_chosen` |
| `preview` | `bot/handlers/admin.py:8243` `loc_glade_set`<br>`bot/handlers/admin.py:8293` `loc_clearing_set`<br>`bot/handlers/admin.py:8344` `loc_mine_set`<br>`bot/handlers/admin.py:8395` `loc_storage_set`<br>`bot/handlers/admin.py:8444` `loc_photo_set`<br>`bot/handlers/admin.py:8482` `loc_season_photo_set` | `bot/handlers/admin.py:8524` `loc_step_photo` |

### `AdminDungeon` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target_id` | — | — |
| `photo_tod` | `bot/handlers/admin.py:5323` `dungeon_photo_set` | `bot/handlers/admin.py:5359` `dungeon_step_photo` |
| `enemy_id` | — | — |
| `enemy_field` | — | — |
| `enemy_value` | `bot/handlers/admin.py:5600` `dungeon_enemy_field_pick` | `bot/handlers/admin.py:5626` `dungeon_enemy_value` |
| `drop_chance` | `bot/handlers/admin.py:1608` `add_item_photo`<br>`bot/handlers/admin.py:5868` `enemy_drop_pick_item`<br>`bot/handlers/admin.py:5951` `enemy_drop_set_chance` | `bot/handlers/admin.py:6273` `enemy_drop_chance_value` |
| `drop_qty` | `bot/handlers/admin.py:5974` `enemy_drop_set_qty`<br>`bot/handlers/admin.py:6282` `enemy_drop_chance_value` | `bot/handlers/admin.py:6288` `enemy_drop_qty_value` |
| `drop_item_photo` | `bot/handlers/admin.py:6019` `enemy_drop_item_photo` | `bot/handlers/admin.py:6028` `enemy_drop_item_photo_value` |
| `drop_item_desc` | `bot/handlers/admin.py:6073` `enemy_drop_item_desc` | `bot/handlers/admin.py:6082` `enemy_drop_item_desc_value` |
| `drop_item_field` | — | — |
| `drop_item_value` | `bot/handlers/admin.py:6171` `enemy_drop_item_stat_pick` | `bot/handlers/admin.py:6182` `enemy_drop_item_stat_value` |
| `pending_enemy_id` | — | — |

### `RecipeManager` — `bot/handlers/admin_recipes.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `ing` | `bot/handlers/admin_recipes.py:374` `recadm_create`<br>`bot/handlers/admin_recipes.py:1163` `recadm_ei` | `bot/handlers/admin_recipes.py:390` `recadm_ing_add` |
| `res_mode` | `bot/handlers/admin_recipes.py:447` `recadm_ing_done`<br>`bot/handlers/admin_recipes.py:1192` `recadm_er` | — |
| `res_pick` | `bot/handlers/admin_recipes.py:464` `recadm_res_existing` | `bot/handlers/admin_recipes.py:473` `recadm_res_pick` |
| `n_name` | `bot/handlers/admin_recipes.py:509` `recadm_res_new` | `bot/handlers/admin_recipes.py:517` `recadm_n_name` |
| `n_desc` | `bot/handlers/admin_recipes.py:537` `recadm_n_name` | `bot/handlers/admin_recipes.py:543` `recadm_n_desc` |
| `n_cat` | `bot/handlers/admin_recipes.py:550` `recadm_n_desc` | — |
| `n_heal` | `bot/handlers/admin_recipes.py:572` `recadm_n_cat` | `bot/handlers/admin_recipes.py:580` `recadm_n_heal` |
| `n_regen` | `bot/handlers/admin_recipes.py:590` `recadm_n_heal` | `bot/handlers/admin_recipes.py:599` `recadm_n_regen` |
| `n_ap` | `bot/handlers/admin_recipes.py:609` `recadm_n_regen` | `bot/handlers/admin_recipes.py:617` `recadm_n_ap` |
| `n_armor` | `bot/handlers/admin_recipes.py:627` `recadm_n_ap` | `bot/handlers/admin_recipes.py:632` `recadm_n_armor` |
| `n_dmg` | `bot/handlers/admin_recipes.py:642` `recadm_n_armor` | `bot/handlers/admin_recipes.py:647` `recadm_n_dmg` |
| `n_drink` | `bot/handlers/admin_recipes.py:657` `recadm_n_dmg` | `bot/handlers/admin_recipes.py:665` `recadm_n_drink` |
| `n_price` | `bot/handlers/admin_recipes.py:672` `recadm_n_drink` | `bot/handlers/admin_recipes.py:680` `recadm_n_price` |
| `n_rarity` | `bot/handlers/admin_recipes.py:690` `recadm_n_price` | — |
| `n_photo` | `bot/handlers/admin_recipes.py:711` `recadm_n_rarity` | `bot/handlers/admin_recipes.py:722` `recadm_n_photo` |
| `c_exp` | `bot/handlers/admin_recipes.py:243` `_resolve_result`<br>`bot/handlers/admin_recipes.py:287` `_newitem_done` | — |
| `c_lvl` | `bot/handlers/admin_recipes.py:746` `recadm_exp` | — |
| `c_ap` | `bot/handlers/admin_recipes.py:766` `recadm_lvl` | `bot/handlers/admin_recipes.py:771` `recadm_c_ap` |
| `c_time` | `bot/handlers/admin_recipes.py:779` `recadm_c_ap` | `bot/handlers/admin_recipes.py:784` `recadm_c_time` |
| `c_rarity` | `bot/handlers/admin_recipes.py:792` `recadm_c_time` | — |
| `c_qty` | `bot/handlers/admin_recipes.py:811` `recadm_rar` | `bot/handlers/admin_recipes.py:819` `recadm_c_qty` |
| `c_shop` | `bot/handlers/admin_recipes.py:827` `recadm_c_qty` | `bot/handlers/admin_recipes.py:836` `recadm_c_shop` |
| `c_confirm` | `bot/handlers/admin_recipes.py:844` `recadm_c_shop` | — |
| `e_value` | `bot/handlers/admin_recipes.py:954` `recadm_ef` | `bot/handlers/admin_recipes.py:960` `recadm_e_value` |

### `BankStates` — `bot/handlers/bank.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `waiting_recipient` | `bot/handlers/bank.py:150` `bank_transfer_manual` | `bot/handlers/bank.py:257` `process_recipient` |
| `waiting_amount` | `bot/handlers/bank.py:162` `set_recipient` | `bot/handlers/bank.py:279` `process_amount` |
| `waiting_message` | `bot/handlers/bank.py:322` `process_amount` | `bot/handlers/bank.py:331` `process_message` |
| `waiting_treasury_amount` | `bot/handlers/bank.py:208` `bank_treasury` | `bot/handlers/bank.py:218` `process_treasury_amount` |

### `ClansCreate` — `bot/handlers/clans.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `kind` | — | — |
| `wait_name` | `bot/handlers/clans.py:563` `clan_create_start` | `bot/handlers/clans.py:571` `clan_create_name` |
| `wait_desc` | `bot/handlers/clans.py:578` `clan_create_name` | `bot/handlers/clans.py:586` `clan_create_desc` |
| `wait_photo` | `bot/handlers/clans.py:596` `clan_create_desc` | `bot/handlers/clans.py:640` `clan_create_photo`<br>`bot/handlers/clans.py:647` `clan_create_photo_hint` |

### `ClansEdit` — `bot/handlers/clans.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `field` | — | — |
| `wait_value` | `bot/handlers/clans.py:705` `clan_edit_field_cb` | `bot/handlers/clans.py:711` `clan_edit_finish_photo`<br>`bot/handlers/clans.py:725` `clan_edit_finish_text` |

### `ClansMessage` — `bot/handlers/clans.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `wait_text` | `bot/handlers/clans.py:762` `clan_msg_start` | `bot/handlers/clans.py:770` `clan_msg_send` |

### `DungeonFSM` — `bot/handlers/dungeon.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `in_dungeon` | `bot/handlers/dungeon.py:883` `contract_enter_confirm`<br>`bot/handlers/dungeon.py:962` `post_captain_menu`<br>`bot/handlers/dungeon.py:2288` `resv_deeper` | — |
| `in_combat` | — | — |
| `in_boss` | `bot/handlers/dungeon.py:1972` `show_boss` | — |
| `confirm_enter` | `bot/handlers/dungeon.py:812` `contract_enter` | — |
| `in_reservoir` | `bot/handlers/dungeon.py:1994` `resv_enter`<br>`bot/handlers/dungeon.py:2009` `resv_menu`<br>`bot/handlers/dungeon.py:2076` `resv_bait_set` | — |

### `HqOrder` — `bot/handlers/hq.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | `bot/handlers/hq.py:175` `hq_order_start`<br>`bot/handlers/hq.py:713` `hq_wingcmd_send_cb` | `bot/handlers/hq.py:184` `hq_order_text` |

### `HqWingCreate` — `bot/handlers/hq.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `num` | `bot/handlers/hq.py:1066` `hq_wing_add_start` | `bot/handlers/hq.py:1075` `hq_wing_add_num` |
| `abbr` | `bot/handlers/hq.py:1084` `hq_wing_add_num` | `bot/handlers/hq.py:1094` `hq_wing_add_abbr` |
| `name` | `bot/handlers/hq.py:1103` `hq_wing_add_abbr` | `bot/handlers/hq.py:1111` `hq_wing_add_name` |
| `callsign` | `bot/handlers/hq.py:1120` `hq_wing_add_name` | `bot/handlers/hq.py:1128` `hq_wing_add_callsign` |
| `emoji` | `bot/handlers/hq.py:1136` `hq_wing_add_callsign` | `bot/handlers/hq.py:1144` `hq_wing_add_emoji` |

### `HqWingEdit` — `bot/handlers/hq.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `field` | — | — |
| `value` | `bot/handlers/hq.py:1190` `hq_wing_edit_cb` | `bot/handlers/hq.py:1200` `hq_wing_edit_value` |

### `TransferItem` — `bot/handlers/inventory.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | `bot/handlers/inventory.py:1649` `inv_transfer_start` | `bot/handlers/inventory.py:1658` `inv_transfer_target` |
| `amount` | `bot/handlers/inventory.py:1665` `inv_transfer_target` | `bot/handlers/inventory.py:1673` `inv_transfer_amount` |
| `message` | `bot/handlers/inventory.py:1705` `inv_transfer_amount` | `bot/handlers/inventory.py:1714` `inv_transfer_message` |

### `KvpFSM` — `bot/handlers/kvp.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `in_course` | `bot/handlers/kvp.py:277` `kvp_start`<br>`bot/handlers/kvp.py:301` `kvp_resume` | — |

### `AdminAddBook` — `bot/handlers/library.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `section` | `bot/handlers/library.py:293` `book_add_section` | — |
| `title` | `bot/handlers/library.py:302` `book_section` | `bot/handlers/library.py:307` `book_title` |
| `author` | `bot/handlers/library.py:309` `book_title` | `bot/handlers/library.py:314` `book_author` |
| `description` | `bot/handlers/library.py:317` `book_author` | `bot/handlers/library.py:322` `book_description` |
| `cover` | `bot/handlers/library.py:324` `book_description` | `bot/handlers/library.py:333` `book_cover` |
| `content` | `bot/handlers/library.py:343` `book_cover` | `bot/handlers/library.py:351` `book_content` |

### `NewsWrite` — `bot/handlers/news.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `title` | `bot/handlers/news.py:295` `news_write_start` | `bot/handlers/news.py:306` `news_write_title` |
| `body` | `bot/handlers/news.py:316` `news_write_title` | `bot/handlers/news.py:326` `news_write_body` |
| `photo` | `bot/handlers/news.py:339` `news_write_body` | `bot/handlers/news.py:357` `news_write_photo` |

### `NewsEdit` — `bot/handlers/news.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | — | — |
| `field` | `bot/handlers/news.py:412` `news_edit_start` | `bot/handlers/news.py:424` `news_edit_title` |
| `value` | `bot/handlers/news.py:442` `news_edit_title` | `bot/handlers/news.py:452` `news_edit_body` |

### `NiiWrite` — `bot/handlers/nii.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `text` | `bot/handlers/nii.py:89` `nii_write_start` | `bot/handlers/nii.py:103` `nii_write_text` |
| `photo` | `bot/handlers/nii.py:119` `nii_write_text` | `bot/handlers/nii.py:137` `nii_write_photo` |

### `AdminStatue` — `bot/handlers/park.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `name` | `bot/handlers/park.py:294` `statue_add_start` | `bot/handlers/park.py:299` `statue_name` |
| `description` | `bot/handlers/park.py:301` `statue_name` | `bot/handlers/park.py:306` `statue_description` |
| `image_dawn` | `bot/handlers/park.py:340` `statue_img_day` | `bot/handlers/park.py:345` `statue_img_dawn` |
| `image_day` | `bot/handlers/park.py:308` `statue_description` | `bot/handlers/park.py:337` `statue_img_day` |
| `image_sunset` | `bot/handlers/park.py:348` `statue_img_dawn` | `bot/handlers/park.py:353` `statue_img_sunset` |
| `image_night` | `bot/handlers/park.py:356` `statue_img_sunset` | `bot/handlers/park.py:361` `statue_img_night` |

### `AdminStatueEdit` — `bot/handlers/park.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `field` | `bot/handlers/park.py:488` `statue_admin_edit_start`<br>`bot/handlers/park.py:553` `statue_admin_edit_value` | — |
| `value` | `bot/handlers/park.py:499` `statue_admin_edit_field` | `bot/handlers/park.py:528` `statue_admin_edit_value` |

### `PollCreate` — `bot/handlers/polls.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `question` | `bot/handlers/polls.py:235` `vote_create` | `bot/handlers/polls.py:247` `poll_question_handler` |
| `options` | `bot/handlers/polls.py:249` `poll_question_handler` | `bot/handlers/polls.py:256` `poll_options_handler` |

### `ProfileStates` — `bot/handlers/profile.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `waiting_photo` | `bot/handlers/profile.py:249` `set_photo` | `bot/handlers/profile.py:257` `process_photo` |
| `waiting_about` | `bot/handlers/profile.py:270` `edit_about` | `bot/handlers/profile.py:278` `process_about` |
| `waiting_callsign` | `bot/handlers/profile.py:601` `profile_callsign`<br>`bot/handlers/profile.py:612` `profile_callsign`<br>`bot/handlers/profile.py:710` `profile_callsign_buy` | `bot/handlers/profile.py:649` `profile_callsign_input` |

### `ReportSubmit` — `bot/handlers/reports.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `waiting_photo` | `bot/handlers/reports.py:102` `report_submit_start` | `bot/handlers/reports.py:111` `report_receive_photo`<br>`bot/handlers/reports.py:130` `report_photo_expected` |
| `waiting_daily_troops` | `bot/handlers/reports.py:117` `report_receive_photo` | `bot/handlers/reports.py:135` `report_receive_daily_troops`<br>`bot/handlers/reports.py:160` `report_daily_troops_expected` |
| `waiting_total_troops` | `bot/handlers/reports.py:147` `report_receive_daily_troops` | `bot/handlers/reports.py:165` `report_receive_total_troops`<br>`bot/handlers/reports.py:196` `report_total_troops_expected` |
| `waiting_region` | `bot/handlers/reports.py:174` `report_receive_total_troops` | `bot/handlers/reports.py:201` `report_receive_region`<br>`bot/handlers/reports.py:295` `report_region_expected` |

### `RepSpeech` — `bot/handlers/representative.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `waiting_text` | `bot/handlers/representative.py:101` `rep_speech_write`<br>`bot/handlers/representative.py:128` `rep_speech_delete` | `bot/handlers/representative.py:176` `rep_speech_text` |

### `SpecialDeptBuy` — `bot/handlers/shop.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `code` | `bot/handlers/shop.py:520` `_start_special_dept_buy` | `bot/handlers/shop.py:532` `special_dept_enter_code` |

### `WallWrite` — `bot/handlers/wall.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `waiting_text` | `bot/handlers/wall.py:179` `wall_write_start` | `bot/handlers/wall.py:187` `wall_write_text` |

## 2. Реестр callback_data по неймспейсам

Все ключи, встречающиеся в фабриках кнопок (`callback_data=`), сгруппированы
по неймспейсу (текст до первого `:`). Это «занятые» префиксы: новый ключ
с таким же префиксом должен учитывать уже существующие фильтры (раздел 3).

| Неймспейс | Ключей | callback_data |
|---|---:|---|
| `addreq:` | 1 | `addreq:none` |
| `admin:` | 19 | `admin:awards`, `admin:dungeons`, `admin:enemies`, `admin:finance`, `admin:fishing`, `admin:forest`, `admin:locations`, `admin:menu`, `admin:ranks`, `admin:reports`, `admin:reports_done`, `admin:reports_pending`, `admin:salaries`, `admin:saletax`, `admin:shop`, `admin:statuses`, `admin:storage`, `admin:tax`, `admin:treasury` |
| `aw:` | 7 | `aw:ach`, `aw:create`, `aw:delete`, `aw:edit`, `aw:grant`, `aw:list`, `aw:revoke` |
| `aw_comment:` | 1 | `aw_comment:skip` |
| `aw_confirm:` | 1 | `aw_confirm` |
| `aw_kind:` | 2 | `aw_kind:ach`, `aw_kind:reg` |
| `back:` | 2 | `back:main`, `back:to_main` |
| `bank:` | 2 | `bank:menu`, `bank:transfer_manual` |
| `booklet:` | 1 | `booklet:claim` |
| `cancel:` | 1 | `cancel` |
| `city:` | 5 | `city:clans`, `city:menu`, `city:pilots`, `city:pilots:list`, `city:vote` |
| `clans:` | 4 | `clans:create_skip`, `clans:list:clan`, `clans:list:party`, `clans:noop` |
| `contracts:` | 1 | `contracts:list` |
| `duel:` | 5 | `duel:card:buy`, `duel:help`, `duel:list`, `duel:menu`, `duel:top` |
| `dungeon:` | 6 | `dungeon:enemies`, `dungeon:exit`, `dungeon:exit:cancel`, `dungeon:exit:confirm`, `dungeon:photos`, `dungeon:photos:clear` |
| `enemy_field:` | 9 | `enemy_field:armor`, `enemy_field:attack`, `enemy_field:description`, `enemy_field:dodge`, `enemy_field:hp`, `enemy_field:image`, `enemy_field:poison_chance`, `enemy_field:poison_dmg`, `enemy_field:reward_nm` |
| `eqlock:` | 2 | `eqlock:potion3`, `eqlock:weapon_aux` |
| `eqpart:` | 4 | `eqpart:body`, `eqpart:hands`, `eqpart:head`, `eqpart:legs` |
| `eqslot:` | 2 | `eqslot:duel`, `eqslot:smoke` |
| `field:` | 24 | `field:ap_cost`, `field:armor`, `field:category`, `field:damage`, `field:description`, `field:drink`, `field:heal`, `field:housing_slots`, `field:housing_type`, `field:is_available`, `field:loot_only`, `field:market_ok`, `field:name`, `field:photo`, `field:plant_name`, `field:price`, `field:rarity`, `field:regen`, `field:required_status`, `field:sell_price`, `field:stock`, `field:weapon_effect`, `field:weapon_effect_chance`, `field:weapon_effect_dmg` |
| `field_req:` | 1 | `field_req:none` |
| `fin:` | 3 | `fin:manual`, `fin:nord:add`, `fin:nord:sub` |
| `fishing:` | 4 | `fishing:new_super:0`, `fishing:new_super:1`, `fishing:water:lake`, `fishing:water:reservoir` |
| `fishing_field:` | 4 | `fishing_field:day_weight`, `fishing_field:night_weight`, `fishing_field:photo`, `fishing_field:sell_price` |
| `forest:` | 4 | `forest:new`, `forest:new_kind:edible`, `forest:new_kind:toxic`, `forest:zset:sold_daily_limit` |
| `forest_field:` | 3 | `forest_field:chance`, `forest_field:photo`, `forest_field:sell_price` |
| `hq:` | 19 | `hq:farms`, `hq:menu`, `hq:noop`, `hq:order:all`, `hq:region_stats`, `hq:region_stats_refresh`, `hq:roster:0`, `hq:send`, `hq:wing`, `hq:wingadd`, `hq:wingcmd`, `hq:wingcmd_send`, `hq:wingdrop:0`, `hq:wingedit:callsign`, `hq:wingedit:emoji`, `hq:wingedit:name`, `hq:wingfarm:0`, `hq:wings`, `hq:wingtake:0` |
| `inventory:` | 2 | `inventory:eq`, `inventory:list` |
| `kvp:` | 3 | `kvp:exit`, `kvp:resume`, `kvp:start` |
| `lib:` | 2 | `lib:menu`, `lib:no_access` |
| `libadmin:` | 3 | `libadmin:add`, `libadmin:list`, `libadmin:menu` |
| `loc:` | 20 | `loc:blocking:done`, `loc:blocking:none`, `loc:building_pick`, `loc:clearing_set`, `loc:create`, `loc:edit_pick`, `loc:glade_set`, `loc:mine_set`, `loc:mode:all`, `loc:mode:exact`, `loc:mode:min`, `loc:photos`, `loc:photos:clear`, `loc:photos:clear_seasons`, `loc:set_blocking`, `loc:set_desc`, `loc:set_mode`, `loc:set_name`, `loc:set_status`, `loc:storage_set` |
| `lootonly:` | 2 | `lootonly:no`, `lootonly:yes` |
| `marketok:` | 2 | `marketok:no`, `marketok:yes` |
| `mvd:` | 2 | `mvd:archive:0`, `mvd:menu` |
| `news:` | 5 | `news:archive`, `news:no_photo`, `news:off`, `news:tab`, `news:write` |
| `nii:` | 5 | `nii:all`, `nii:menu_back`, `nii:mine`, `nii:no_photo`, `nii:write` |
| `noop:` | 1 | `noop` |
| `park:` | 9 | `park:admin`, `park:admin:add`, `park:admin:editlist`, `park:admin:list`, `park:fountain`, `park:fountain:drink`, `park:lake`, `park:menu`, `park:statues` |
| `pollarch:` | 1 | `pollarch:list` |
| `prod:` | 2 | `prod:player`, `prod:state` |
| `prof:` | 1 | `prof:back` |
| `profile:` | 5 | `profile`, `profile:awards`, `profile:callsign_buy`, `profile:callsign_cancel`, `profile:open` |
| `recadm:` | 10 | `recadm:cancel`, `recadm:create`, `recadm:ing_done`, `recadm:list`, `recadm:menu`, `recadm:no_photo`, `recadm:noop`, `recadm:res_existing`, `recadm:res_new`, `recadm:save` |
| `rep:` | 5 | `rep:auto_approve_edit`, `rep:pay_cap_edit`, `rep:speech`, `rep:speech:delete`, `rep:speech:write` |
| `report:` | 1 | `report:menu` |
| `rolop:` | 2 | `rolop:add`, `rolop:remove` |
| `salary:` | 2 | `salary:choose`, `salary:pay` |
| `salary_period:` | 2 | `salary_period:30`, `salary_period:7` |
| `shop:` | 1 | `shop:catalog` |
| `shop_admin:` | 2 | `shop_admin:add`, `shop_admin:edit` |
| `shopcat:` | 2 | `shopcat:license`, `shopcat:market` |
| `st:` | 7 | `st:create`, `st:delete`, `st:grant`, `st:legioner`, `st:list`, `st:more`, `st:revoke` |
| `st_op:` | 2 | `st_op:clear`, `st_op:set` |
| `storage:` | 4 | `storage:cats`, `storage:create`, `storage:menu`, `storage:noop` |
| `treasury:` | 3 | `treasury:debts`, `treasury:give`, `treasury:stats` |
| `vote:` | 2 | `vote:close_cancel`, `vote:create` |
| `wall:` | 2 | `wall:archive`, `wall:write` |
| `wing_set:` | 1 | `wing_set:none` |

## 3. Фильтры хендлеров `F.data`

### Точное совпадение (`F.data == "..."`)

- `admin:awards`: `bot/handlers/admin.py:3401`
- `admin:callsign`: `bot/handlers/admin.py:743`
- `admin:del_photo`: `bot/handlers/admin.py:717`
- `admin:dungeons`: `bot/handlers/admin.py:5221`
- `admin:enemies`: `bot/handlers/admin.py:8700`
- `admin:finance`: `bot/handlers/admin.py:2175`
- `admin:fishing`: `bot/handlers/admin.py:6476`
- `admin:forest`: `bot/handlers/admin.py:7038`
- `admin:locations`: `bot/handlers/admin.py:5197`
- `admin:logs`: `bot/handlers/admin.py:4733`
- `admin:menu`: `bot/handlers/admin.py:707`
- `admin:player_log`: `bot/handlers/admin.py:729`
- `admin:ranks`: `bot/handlers/admin.py:4623`
- `admin:reports`: `bot/handlers/admin.py:4058`
- `admin:reports_done`: `bot/handlers/admin.py:4110`
- `admin:reports_pending`: `bot/handlers/admin.py:4067`
- `admin:roles`: `bot/handlers/admin.py:2682`
- `admin:salaries`: `bot/handlers/admin.py:5037`
- `admin:saletax`: `bot/handlers/admin.py:2439`
- `admin:shop`: `bot/handlers/admin.py:858`
- `admin:states`: `bot/handlers/admin.py:4931`
- `admin:statuses`: `bot/handlers/admin.py:2916`
- `admin:storage`: `bot/handlers/admin.py:932`
- `admin:tax`: `bot/handlers/admin.py:2402`
- `admin:treasury`: `bot/handlers/admin.py:2215`
- `admin:wing`: `bot/handlers/admin.py:756`
- `aw:ach`: `bot/handlers/admin.py:3459`
- `aw:create`: `bot/handlers/admin.py:3477`
- `aw:delete`: `bot/handlers/admin.py:3618`
- `aw:edit`: `bot/handlers/admin.py:3799`
- `aw:grant`: `bot/handlers/admin.py:3957`
- `aw:list`: `bot/handlers/admin.py:3438`
- `aw:revoke`: `bot/handlers/admin.py:4038`
- `aw_comment:skip`: `bot/handlers/admin.py:3995`
- `aw_confirm`: `bot/handlers/admin.py:3594`
- `back:main`: `bot/handlers/admin.py:4906`
- `bank:balance`: `bot/handlers/bank.py:72`
- `bank:history`: `bot/handlers/bank.py:403`
- `bank:menu`: `bot/handlers/bank.py:191`
- `bank:transfer`: `bot/handlers/bank.py:131`
- `bank:transfer_manual`: `bot/handlers/bank.py:147`
- `bank:treasury`: `bot/handlers/bank.py:204`
- `booklet:claim`: `bot/handlers/tourist_booklet.py:71`
- `booklet:menu`: `bot/handlers/tourist_booklet.py:65`
- `cancel`: `bot/handlers/admin.py:4914`
- `city:clans`: `bot/handlers/clans.py:88`
- `city:dungeon`: `bot/handlers/dungeon.py:888`
- `city:library`: `bot/handlers/library.py:82`
- `city:menu`: `bot/handlers/start.py:158`
- `city:pilots`: `bot/handlers/pilots.py:100`
- `city:pilots:list`: `bot/handlers/pilots.py:127`
- `city:quarter`: `bot/handlers/locations.py:223`
- `city:vote`: `bot/handlers/polls.py:70`
- `clans:create_skip`: `bot/handlers/clans.py:651`
- `clans:noop`: `bot/handlers/clans.py:436`
- `contracts:list`: `bot/handlers/dungeon.py:700`
- `del_item:back`: `bot/handlers/admin.py:1684`
- `duel:card:buy`: `bot/handlers/duel.py:246`
- `duel:help`: `bot/handlers/duel.py:224`
- `duel:list`: `bot/handlers/duel.py:272`
- `duel:menu`: `bot/handlers/duel.py:218`
- `duel:top`: `bot/handlers/duel.py:292`
- `dungeon:enemies`: `bot/handlers/admin.py:5542`
- `dungeon:exit`: `bot/handlers/dungeon.py:2430`
- `dungeon:exit:cancel`: `bot/handlers/dungeon.py:2509`
- `dungeon:exit:confirm`: `bot/handlers/dungeon.py:2477`
- `dungeon:photos`: `bot/handlers/admin.py:5304`
- `dungeon:photos:clear`: `bot/handlers/admin.py:5348`
- `enemy:fi`: `bot/handlers/admin.py:8738`
- `field:drink`: `bot/handlers/admin.py:1955`
- `field:loot_only`: `bot/handlers/admin.py:2019`
- `field:market_ok`: `bot/handlers/admin.py:1999`
- `field:photo`: `bot/handlers/admin.py:1876`
- `field:weapon_effect`: `bot/handlers/admin.py:1896`
- `fin:manual`: `bot/handlers/admin.py:2523`
- `forest:addlist`: `bot/handlers/admin.py:7369`
- `forest:new`: `bot/handlers/admin.py:7522`
- `forest:zset:sold_daily_limit`: `bot/handlers/admin.py:7208`
- `housing:menu`: `bot/handlers/housing.py:182`
- `housing:noop`: `bot/handlers/housing.py:714`
- `housing:pay_debt`: `bot/handlers/housing.py:272`
- `housing:pay_tax`: `bot/handlers/housing.py:263`
- `hq:farms`: `bot/handlers/hq.py:464`
- `hq:menu`: `bot/handlers/hq.py:148`
- `hq:noop`: `bot/handlers/hq.py:556`
- `hq:region_stats`: `bot/handlers/hq.py:503`
- `hq:region_stats_refresh`: `bot/handlers/hq.py:512`
- `hq:send`: `bot/handlers/hq.py:155`
- `hq:wing`: `bot/handlers/hq.py:235`
- `hq:wingadd`: `bot/handlers/hq.py:1060`
- `hq:wingcmd`: `bot/handlers/hq.py:564`
- `hq:wingcmd_send`: `bot/handlers/hq.py:702`
- `hq:wings`: `bot/handlers/hq.py:1030`
- `inventory:eq`: `bot/handlers/inventory.py:482`
- `inventory:list`: `bot/handlers/inventory.py:573`
- `kvp:exit`: `bot/handlers/kvp.py:718`
- `kvp:resume`: `bot/handlers/kvp.py:288`
- `kvp:start`: `bot/handlers/kvp.py:248`
- `lib:menu`: `bot/handlers/library.py:141`
- `lib:no_access`: `bot/handlers/library.py:136`
- `libadmin:add`: `bot/handlers/library.py:288`
- `libadmin:list`: `bot/handlers/library.py:384`
- `libadmin:menu`: `bot/handlers/library.py:271`
- `loc:building_pick`: `bot/handlers/admin.py:7700`
- `loc:clearing_clear`: `bot/handlers/admin.py:8317`
- `loc:clearing_set`: `bot/handlers/admin.py:8280`
- `loc:create`: `bot/handlers/admin.py:7668`
- `loc:edit_pick`: `bot/handlers/admin.py:7684`
- `loc:glade_clear`: `bot/handlers/admin.py:8267`
- `loc:glade_set`: `bot/handlers/admin.py:8229`
- `loc:mine_clear`: `bot/handlers/admin.py:8368`
- `loc:mine_set`: `bot/handlers/admin.py:8330`
- `loc:photos`: `bot/handlers/admin.py:8155`
- `loc:photos:clear`: `bot/handlers/admin.py:8510`
- `loc:photos:clear_seasons`: `bot/handlers/admin.py:8178`
- `loc:set_blocking`: `bot/handlers/admin.py:7837`
- `loc:set_desc`: `bot/handlers/admin.py:7994`
- `loc:set_mode`: `bot/handlers/admin.py:7766`
- `loc:set_name`: `bot/handlers/admin.py:7955`
- `loc:set_status`: `bot/handlers/admin.py:7809`
- `loc:storage_clear`: `bot/handlers/admin.py:8419`
- `loc:storage_set`: `bot/handlers/admin.py:8381`
- `mvd:menu`: `bot/handlers/mvd.py:29`
- `news:archive`: `bot/handlers/news.py:132`
- `news:no_photo`: `bot/handlers/news.py:350`
- `news:tab`: `bot/handlers/news.py:259`
- `news:write`: `bot/handlers/news.py:279`
- `nii:all`: `bot/handlers/nii.py:253`
- `nii:menu_back`: `bot/handlers/nii.py:247`
- `nii:mine`: `bot/handlers/nii.py:228`
- `nii:no_photo`: `bot/handlers/nii.py:130`
- `nii:write`: `bot/handlers/nii.py:77`
- `noop`: `bot/handlers/admin.py:4901`
- `park:admin`: `bot/handlers/park.py:274`
- `park:admin:add`: `bot/handlers/park.py:289`
- `park:admin:editlist`: `bot/handlers/park.py:459`
- `park:admin:list`: `bot/handlers/park.py:376`
- `park:fountain`: `bot/handlers/park.py:136`
- `park:fountain:drink`: `bot/handlers/park.py:161`
- `park:lake`: `bot/handlers/park.py:107`
- `park:menu`: `bot/handlers/park.py:101`
- `park:statues`: `bot/handlers/park.py:242`
- `pollarch:list`: `bot/handlers/poll_archive.py:125`
- `prof:back`: `bot/handlers/profile.py:336`
- `profile`: `bot/handlers/profile.py:238`
- `profile:achievements`: `bot/handlers/profile.py:490`
- `profile:awards`: `bot/handlers/profile.py:460`
- `profile:callsign`: `bot/handlers/profile.py:587`
- `profile:callsign_buy`: `bot/handlers/profile.py:693`
- `profile:callsign_cancel`: `bot/handlers/profile.py:641`
- `profile:choose_status`: `bot/handlers/profile.py:296`
- `profile:edit_about`: `bot/handlers/profile.py:267`
- `profile:notify_toggle`: `bot/handlers/profile.py:343`
- `profile:open`: `bot/handlers/profile.py:580`
- `profile:pilot_card`: `bot/handlers/profile.py:383`
- `profile:public_toggle`: `bot/handlers/profile.py:363`
- `profile:set_photo`: `bot/handlers/profile.py:246`
- `recadm:cancel`: `bot/handlers/admin_recipes.py:918`
- `recadm:create`: `bot/handlers/admin_recipes.py:370`
- `recadm:ing_done`: `bot/handlers/admin_recipes.py:426`
- `recadm:list`: `bot/handlers/admin_recipes.py:340`
- `recadm:menu`: `bot/handlers/admin_recipes.py:322`
- `recadm:no_photo`: `bot/handlers/admin_recipes.py:727`
- `recadm:noop`: `bot/handlers/admin_recipes.py:317`
- `recadm:res_existing`: `bot/handlers/admin_recipes.py:460`
- `recadm:res_new`: `bot/handlers/admin_recipes.py:505`
- `recadm:save`: `bot/handlers/admin_recipes.py:865`
- `rep:auto_approve_edit`: `bot/handlers/admin.py:4154`
- `rep:next`: `bot/handlers/admin.py:4596`
- `rep:pay_cap_edit`: `bot/handlers/admin.py:4193`
- `rep:speech`: `bot/handlers/representative.py:77`
- `rep:speech:delete`: `bot/handlers/representative.py:109`
- `rep:speech:write`: `bot/handlers/representative.py:89`
- `report:menu`: `bot/handlers/reports.py:47`
- `report:my_reports`: `bot/handlers/reports.py:394`
- `report:submit`: `bot/handlers/reports.py:57`
- `salary:choose`: `bot/handlers/admin.py:5076`
- `salary:pay`: `bot/handlers/admin.py:5088`
- `shop:catalog`: `bot/handlers/shop.py:228`
- `shop_admin:add`: `bot/handlers/admin.py:1195`
- `shop_admin:delete`: `bot/handlers/admin.py:1655`
- `shop_admin:edit`: `bot/handlers/admin.py:1778`
- `shop_admin:special_code`: `bot/handlers/admin.py:2480`
- `shop_del:cats`: `bot/handlers/admin.py:1772`
- `shop_edit:cats`: `bot/handlers/admin.py:1757`
- `st:create`: `bot/handlers/admin.py:2970`
- `st:delete`: `bot/handlers/admin.py:3043`
- `st:grant`: `bot/handlers/admin.py:3243`
- `st:legioner`: `bot/handlers/admin.py:3188`
- `st:list`: `bot/handlers/admin.py:2953`
- `st:more`: `bot/handlers/admin.py:3382`
- `st:revoke`: `bot/handlers/admin.py:3309`
- `storage:cats`: `bot/handlers/admin.py:951`
- `storage:create`: `bot/handlers/admin.py:1196`
- `storage:menu`: `bot/handlers/storage.py:89`
- `storage:noop`: `bot/handlers/admin.py:946`
- `treasury:debts`: `bot/handlers/admin.py:2248`
- `treasury:give`: `bot/handlers/admin.py:2347`
- `treasury:stats`: `bot/handlers/admin.py:2295`
- `vote:close_cancel`: `bot/handlers/polls.py:332`
- `vote:create`: `bot/handlers/polls.py:224`
- `wall:archive`: `bot/handlers/wall.py:315`
- `wall:view`: `bot/handlers/wall.py:149`
- `wall:write`: `bot/handlers/wall.py:170`

### По префиксу (`F.data.startswith("...")`)

- `\d+$`: `bot/handlers/admin.py:1347`; `bot/handlers/admin.py:5011`; `bot/handlers/admin.py:7222`; `bot/handlers/reports.py:200`
- `\d{1,7}$`: `bot/handlers/reports.py:134`; `bot/handlers/reports.py:164`
- `act:`: `bot/handlers/admin.py:4808`
- `addreq:`: `bot/handlers/admin.py:1546`
- `aw_del:`: `bot/handlers/admin.py:3639`
- `aw_edit:`: `bot/handlers/admin.py:3819`
- `aw_ei:`: `bot/handlers/admin.py:3830`
- `aw_kind:`: `bot/handlers/admin.py:3928`
- `aw_pick:`: `bot/handlers/admin.py:3979`
- `awr_grant:`: `bot/handlers/admin.py:4046`
- `bait:set:`: `bot/handlers/fishing.py:176`
- `bank:pickrecipient:`: `bot/handlers/bank.py:177`
- `bank:transfer:list:`: `bot/handlers/bank.py:137`
- `buy5_nord:`: `bot/handlers/shop.py:487`
- `buy_housing:`: `bot/handlers/shop.py:1001`
- `buy_housing_cancel:`: `bot/handlers/shop.py:992`
- `buy_nord:`: `bot/handlers/shop.py:477`
- `cat:`: `bot/handlers/admin.py:1268`
- `city/`: `bot/handlers/locations.py:85`
- `city:pilots:list:`: `bot/handlers/pilots.py:133`
- `clans:add:`: `bot/handlers/clans.py:441`
- `clans:addset:`: `bot/handlers/clans.py:458`
- `clans:cancel:`: `bot/handlers/clans.py:257`
- `clans:create:`: `bot/handlers/clans.py:553`
- `clans:del:`: `bot/handlers/clans.py:799`
- `clans:delyes:`: `bot/handlers/clans.py:816`
- `clans:edit:`: `bot/handlers/clans.py:666`
- `clans:editf:`: `bot/handlers/clans.py:684`
- `clans:join:`: `bot/handlers/clans.py:220`
- `clans:kick:`: `bot/handlers/clans.py:391`
- `clans:leader:`: `bot/handlers/clans.py:482`
- `clans:leaderset:`: `bot/handlers/clans.py:499`
- `clans:leaderunset:`: `bot/handlers/clans.py:529`
- `clans:leave:`: `bot/handlers/clans.py:267`
- `clans:list:`: `bot/handlers/clans.py:128`
- `clans:manage:`: `bot/handlers/clans.py:335`
- `clans:msg:`: `bot/handlers/clans.py:754`
- `clans:reqno:`: `bot/handlers/clans.py:318`
- `clans:reqok:`: `bot/handlers/clans.py:294`
- `clans:view:`: `bot/handlers/clans.py:165`
- `confirm_del_photo:`: `bot/handlers/admin.py:837`
- `contract:enter:\d+$`: `bot/handlers/dungeon.py:780`
- `contract:enter:confirm:`: `bot/handlers/dungeon.py:826`
- `contract:pick:`: `bot/handlers/dungeon.py:728`
- `del_item:`: `bot/handlers/admin.py:1669`
- `drinksel:`: `bot/handlers/admin.py:1301`
- `duel:accept:`: `bot/handlers/duel.py:399`
- `duel:atk:`: `bot/handlers/duel.py:529`
- `duel:cancel:`: `bot/handlers/duel.py:373`
- `duel:decline:`: `bot/handlers/duel.py:385`
- `duel:def:`: `bot/handlers/duel.py:545`
- `duel:invite:`: `bot/handlers/duel.py:310`
- `duel:leave:`: `bot/handlers/duel.py:448`
- `dungeon:attack:`: `bot/handlers/dungeon.py:1277`
- `dungeon:continue:`: `bot/handlers/dungeon.py:1078`
- `dungeon:edit:`: `bot/handlers/admin.py:5241`
- `dungeon:enemy:`: `bot/handlers/admin.py:5574`
- `dungeon:escape:`: `bot/handlers/dungeon.py:1893`
- `dungeon:photo_set:`: `bot/handlers/admin.py:5313`
- `dungeon:use_slot:`: `bot/handlers/dungeon.py:1594`
- `eddrop:`: `bot/handlers/admin.py:5899`
- `eddrop_del:`: `bot/handlers/admin.py:5985`
- `eddrop_desc:`: `bot/handlers/admin.py:6057`
- `eddrop_photo:`: `bot/handlers/admin.py:6003`
- `eddrop_set_ch:`: `bot/handlers/admin.py:5940`
- `eddrop_set_q:`: `bot/handlers/admin.py:5963`
- `eddrop_stat:`: `bot/handlers/admin.py:6152`
- `eddrop_stats:`: `bot/handlers/admin.py:6113`
- `eddrop_weff:`: `bot/handlers/admin.py:6215`
- `eddrop_weff_set:`: `bot/handlers/admin.py:6237`
- `edit_item:`: `bot/handlers/admin.py:1787`
- `editem_add:`: `bot/handlers/admin.py:5851`
- `editem_new:`: `bot/handlers/admin.py:5876`
- `editem_pick:`: `bot/handlers/admin.py:5806`
- `editset:drink:`: `bot/handlers/admin.py:1978`
- `editset:weff:`: `bot/handlers/admin.py:1912`
- `enemy:card:`: `bot/handlers/admin.py:8872`
- `enemy:dcard:`: `bot/handlers/admin.py:8800`
- `enemy:del:`: `bot/handlers/admin.py:8998`
- `enemy:dn:\d+$`: `bot/handlers/admin.py:8710`
- `enemy:dropadd:`: `bot/handlers/admin.py:9175`
- `enemy:dropch:`: `bot/handlers/admin.py:9102`
- `enemy:dropdel:`: `bot/handlers/admin.py:9128`
- `enemy:dropedit:`: `bot/handlers/admin.py:9064`
- `enemy:dropitem:`: `bot/handlers/admin.py:9140`
- `enemy:dropq:`: `bot/handlers/admin.py:9115`
- `enemy:drops:`: `bot/handlers/admin.py:9054`
- `enemy:fld:`: `bot/handlers/admin.py:8882`
- `enemy:list:[a-z]+:[\w-]+$`: `bot/handlers/admin.py:8758`
- `enemy:new:`: `bot/handlers/admin.py:9249`
- `enemy:photo:`: `bot/handlers/admin.py:8942`
- `enemy:tog:`: `bot/handlers/admin.py:8979`
- `enemy_drops:`: `bot/handlers/admin.py:5793`
- `enemy_field:`: `bot/handlers/admin.py:5587`
- `eqequip:[a-z0-9_]+:\d+$`: `bot/handlers/inventory.py:500`
- `eqlock:[a-z0-9_]+$`: `bot/handlers/inventory.py:488`
- `eqpart:`: `bot/handlers/admin.py:1379`
- `eqslot:[a-z0-9_]+$`: `bot/handlers/inventory.py:493`
- `equnequip:[a-z0-9_]+$`: `bot/handlers/inventory.py:532`
- `field:`: `bot/handlers/admin.py:2083`
- `field:required_status`: `bot/handlers/admin.py:1826`
- `field_req:`: `bot/handlers/admin.py:1859`
- `fin:`: `bot/handlers/admin.py:2533`
- `finuser:`: `bot/handlers/admin.py:2563`
- `fish:bait:\d+$`: `bot/handlers/fishing.py:478`
- `fish:bait:set:\d+:[a-z]+$`: `bot/handlers/fishing.py:520`
- `fish:cast:\d+$`: `bot/handlers/fishing.py:530`
- `fish:lake:\d+$`: `bot/handlers/fishing.py:471`
- `fishbuy:`: `bot/handlers/shop.py:790`
- `fishcatch:`: `bot/handlers/inventory.py:1280`
- `fishgo:`: `bot/handlers/inventory.py:1531`
- `fishing:addfish:`: `bot/handlers/admin.py:6643`
- `fishing:addlist:`: `bot/handlers/admin.py:6613`
- `fishing:del:`: `bot/handlers/admin.py:6666`
- `fishing:fish:`: `bot/handlers/admin.py:6533`
- `fishing:junk:`: `bot/handlers/admin.py:6389`
- `fishing:kind:`: `bot/handlers/admin.py:6547`
- `fishing:market:`: `bot/handlers/admin.py:6569`
- `fishing:new:`: `bot/handlers/admin.py:6691`
- `fishing:new_super:`: `bot/handlers/admin.py:6794`
- `fishing:super:`: `bot/handlers/admin.py:6591`
- `fishing:water:`: `bot/handlers/admin.py:6495`
- `fishing_field:`: `bot/handlers/admin.py:6853`
- `fishing_j:`: `bot/handlers/admin.py:6439`
- `fishmarket:`: `bot/handlers/inventory.py:1433`
- `fishoffer:`: `bot/handlers/shop.py:726`
- `fishprice:`: `bot/handlers/inventory.py:1513`
- `fishsell:`: `bot/handlers/inventory.py:1589`
- `fishuse:`: `bot/handlers/inventory.py:1288`
- `forest:add:`: `bot/handlers/admin.py:7394`
- `forest:area:\d+:(glade|clearing)$`: `bot/handlers/forest.py:427`
- `forest:battle:flee:\d+$`: `bot/handlers/forest.py:1052`
- `forest:battle:hit:\d+$`: `bot/handlers/forest.py:854`
- `forest:card:`: `bot/handlers/admin.py:7308`
- `forest:cast:\d+(?::(glade|clearing))?$`: `bot/handlers/forest.py:490`
- `forest:del:`: `bot/handlers/admin.py:7413`
- `forest:kind:`: `bot/handlers/admin.py:7322`
- `forest:market:`: `bot/handlers/admin.py:7347`
- `forest:new_kind:`: `bot/handlers/admin.py:7602`
- `forest:zadd:(glade|clearing):\d+$`: `bot/handlers/admin.py:7174`
- `forest:zaddlist:(glade|clearing)$`: `bot/handlers/admin.py:7147`
- `forest:zchance:(glade|clearing):\d+$`: `bot/handlers/admin.py:7120`
- `forest:zdel:(glade|clearing):\d+$`: `bot/handlers/admin.py:7135`
- `forest:zone:(glade|clearing)$`: `bot/handlers/admin.py:7048`
- `forest:zset:(glade|clearing):(\w+)$`: `bot/handlers/admin.py:7186`
- `forest_field:`: `bot/handlers/admin.py:7434`
- `housing:craft:`: `bot/handlers/housing.py:560`
- `housing:harvest:`: `bot/handlers/housing.py:983`
- `housing:install:`: `bot/handlers/housing.py:721`
- `housing:install_item:`: `bot/handlers/housing.py:759`
- `housing:kitchen:`: `bot/handlers/housing.py:338`
- `housing:move:`: `bot/handlers/housing.py:1004`
- `housing:plant:`: `bot/handlers/housing.py:962`
- `housing:recipe:`: `bot/handlers/housing.py:515`
- `housing:room:`: `bot/handlers/housing.py:283`
- `housing:shower:`: `bot/handlers/housing.py:428`
- `housing:uninstall:`: `bot/handlers/housing.py:862`
- `housing:uninstall_confirm:`: `bot/handlers/housing.py:928`
- `hq:farms:`: `bot/handlers/hq.py:480`
- `hq:order:`: `bot/handlers/hq.py:167`
- `hq:pilot:`: `bot/handlers/hq.py:337`
- `hq:roster:`: `bot/handlers/hq.py:283`
- `hq:wing:set:`: `bot/handlers/hq.py:364`
- `hq:wingcmd:assign:`: `bot/handlers/hq.py:628`
- `hq:wingcmd:pick:`: `bot/handlers/hq.py:605`
- `hq:wingcmd:unset:`: `bot/handlers/hq.py:673`
- `hq:wingdel:`: `bot/handlers/hq.py:1226`
- `hq:wingdep:`: `bot/handlers/hq.py:905`
- `hq:wingdrop:`: `bot/handlers/hq.py:822`
- `hq:wingedit:`: `bot/handlers/hq.py:1162`
- `hq:wingfarm:`: `bot/handlers/hq.py:444`
- `hq:wingtake:`: `bot/handlers/hq.py:748`
- `http`: `bot/handlers/library.py:360`
- `inv_equip:`: `bot/handlers/inventory.py:786`
- `inv_sell:`: `bot/handlers/inventory.py:921`
- `inv_sell_keep1:`: `bot/handlers/inventory.py:941`
- `inv_sell_ok:`: `bot/handlers/inventory.py:1016`
- `inv_sellall:`: `bot/handlers/inventory.py:931`
- `inv_sellmore:`: `bot/handlers/inventory.py:1126`
- `inv_slot:`: `bot/handlers/inventory.py:840`
- `inv_transfer:`: `bot/handlers/inventory.py:1621`
- `inv_unequip:`: `bot/handlers/inventory.py:816`
- `inv_unslot:`: `bot/handlers/inventory.py:875`
- `inv_use:`: `bot/handlers/inventory.py:897`
- `inventory:cat:[^:]+$`: `bot/handlers/inventory.py:592`
- `invitem:`: `bot/handlers/inventory.py:779`
- `itembuy:`: `bot/handlers/shop.py:905`
- `itemgo:`: `bot/handlers/inventory.py:1224`
- `itemmarket:`: `bot/handlers/inventory.py:1134`
- `itemoffer:`: `bot/handlers/shop.py:845`
- `itemprice:`: `bot/handlers/inventory.py:1213`
- `kvp:attack:`: `bot/handlers/kvp.py:514`
- `kvp:attempt:`: `bot/handlers/kvp.py:440`
- `kvp:continue:`: `bot/handlers/kvp.py:410`
- `libadmin_del:`: `bot/handlers/library.py:409`
- `libadmin_sec:`: `bot/handlers/library.py:297`
- `libbook:`: `bot/handlers/library.py:204`
- `libdl:`: `bot/handlers/library.py:249`
- `libsec:[a-z]+$`: `bot/handlers/library.py:178`
- `loc:blocking:`: `bot/handlers/admin.py:7853`
- `loc:building:`: `bot/handlers/admin.py:7742`
- `loc:edit:`: `bot/handlers/admin.py:7716`
- `loc:mode:`: `bot/handlers/admin.py:7782`
- `loc:photo_set:`: `bot/handlers/admin.py:8432`
- `loc:req_status:`: `bot/handlers/admin.py:7818`
- `loc:season:(winter|spring|summer|autumn)$`: `bot/handlers/admin.py:8165`
- `loc:season_clear:(winter|spring|summer|autumn)$`: `bot/handlers/admin.py:8191`
- `loc:season_photo_set:(winter|spring|summer|autumn):(dawn|day|sunset|night)$`: `bot/handlers/admin.py:8469`
- `location:enter:`: `bot/handlers/locations.py:105`
- `location:preview:`: `bot/handlers/locations.py:38`
- `locstat:`: `bot/handlers/admin.py:4867`
- `lootonly:`: `bot/handlers/admin.py:1521`
- `marketok:`: `bot/handlers/admin.py:1499`
- `mine:battle:flee:\d+$`: `bot/handlers/mine.py:664`
- `mine:battle:hit:\d+$`: `bot/handlers/mine.py:564`
- `mine:deeper:\d+$`: `bot/handlers/mine.py:387`
- `mine:dig:\d+$`: `bot/handlers/mine.py:398`
- `mine:level:\d+$`: `bot/handlers/mine.py:355`
- `mine:menu:\d+$`: `bot/handlers/mine.py:348`
- `mollusk:flee:\d+$`: `bot/handlers/dungeon.py:459`
- `mollusk:hit:\d+$`: `bot/handlers/dungeon.py:365`
- `mvd:arch:`: `bot/handlers/mvd.py:95`
- `mvd:archive:`: `bot/handlers/mvd.py:45`
- `news:(?:off|(?:dis)?allow:-?\d+|chat:-?\d+:-?\d+|topic:-?\d+:-?\d+)$`: `bot/handlers/admin.py:2855`
- `news:arch:\d+$`: `bot/handlers/news.py:179`
- `news:del:`: `bot/handlers/news.py:473`
- `news:delconf:`: `bot/handlers/news.py:495`
- `news:edit:`: `bot/handlers/news.py:400`
- `news:view:`: `bot/handlers/news.py:196`
- `nii:set:`: `bot/handlers/nii.py:319`
- `nii:view:`: `bot/handlers/nii.py:284`
- `page`: `bot/handlers/admin.py:404`
- `park:admin:del:`: `bot/handlers/park.py:390`
- `park:admin:delyes:`: `bot/handlers/park.py:408`
- `park:admin:edit:`: `bot/handlers/park.py:474`
- `park:adminedit:f:`: `bot/handlers/park.py:492`
- `park:statue:`: `bot/handlers/park.py:257`
- `pickuser:`: `bot/handlers/admin.py:395`
- `pollarch:day:\d{4}-\d{2}-\d{2}(?::\d+)?$`: `bot/handlers/poll_archive.py:176`
- `pollarch:days:\d+$`: `bot/handlers/poll_archive.py:154`
- `prod:`: `bot/handlers/admin.py:1459`
- `prof_sel_status:`: `bot/handlers/profile.py:321`
- `profile:award:`: `bot/handlers/profile.py:541`
- `rank_pick:`: `bot/handlers/admin.py:4700`
- `rank_promote:`: `bot/handlers/admin.py:4659`
- `rar:`: `bot/handlers/admin.py:1259`
- `rathaus:`: `bot/handlers/pilots.py:172`
- `rathaus_prof:`: `bot/handlers/pilots.py:212`
- `recadm:cat:`: `bot/handlers/admin_recipes.py:560`
- `recadm:ed:`: `bot/handlers/admin_recipes.py:1225`
- `recadm:ed_yes:`: `bot/handlers/admin_recipes.py:1248`
- `recadm:ef:`: `bot/handlers/admin_recipes.py:931`
- `recadm:ei:`: `bot/handlers/admin_recipes.py:1145`
- `recadm:eq:`: `bot/handlers/admin_recipes.py:1103`
- `recadm:er:`: `bot/handlers/admin_recipes.py:1177`
- `recadm:es:`: `bot/handlers/admin_recipes.py:1053`
- `recadm:et:`: `bot/handlers/admin_recipes.py:1206`
- `recadm:exp:`: `bot/handlers/admin_recipes.py:736`
- `recadm:exv:`: `bot/handlers/admin_recipes.py:1069`
- `recadm:lvl:`: `bot/handlers/admin_recipes.py:756`
- `recadm:newrar:`: `bot/handlers/admin_recipes.py:699`
- `recadm:open:`: `bot/handlers/admin_recipes.py:359`
- `recadm:page:`: `bot/handlers/admin_recipes.py:348`
- `recadm:rar:`: `bot/handlers/admin_recipes.py:801`
- `recadm:rxv:`: `bot/handlers/admin_recipes.py:1118`
- `rep:nav:`: `bot/handlers/admin.py:4585`
- `rep_fix:`: `bot/handlers/admin.py:4384`
- `rep_no:`: `bot/handlers/admin.py:4570`
- `rep_ok:`: `bot/handlers/admin.py:4501`
- `report:my:`: `bot/handlers/reports.py:389`
- `report:view:`: `bot/handlers/reports.py:401`
- `resv:bait:\d+$`: `bot/handlers/dungeon.py:2013`
- `resv:bait:set:\d+:[a-z]+$`: `bot/handlers/dungeon.py:2061`
- `resv:cast:\d+$`: `bot/handlers/dungeon.py:2080`
- `resv:deeper:\d+$`: `bot/handlers/dungeon.py:2265`
- `resv:enter:\d+$`: `bot/handlers/dungeon.py:1975`
- `resv:eq:\d+$`: `bot/handlers/dungeon.py:2299`
- `resv:eqclear:[a-z0-9_]+:\d+$`: `bot/handlers/dungeon.py:2407`
- `resv:eqset:[a-z0-9_]+:\d+:\d+$`: `bot/handlers/dungeon.py:2383`
- `resv:eqslot:[a-z0-9_]+:\d+$`: `bot/handlers/dungeon.py:2337`
- `resv:menu:\d+$`: `bot/handlers/dungeon.py:1999`
- `role:`: `bot/handlers/admin.py:2768`
- `rolop:`: `bot/handlers/admin.py:2719`
- `salary_period:`: `bot/handlers/admin.py:5153`
- `shop_del:cat:`: `bot/handlers/admin.py:1763`
- `shop_edit:cat:`: `bot/handlers/admin.py:1748`
- `shopcat:[^:]+$`: `bot/handlers/shop.py:248`
- `shopcat:[^:]+:\d+$`: `bot/handlers/shop.py:332`
- `shopitem:`: `bot/handlers/shop.py:343`
- `st_del:`: `bot/handlers/admin.py:3062`
- `st_key:`: `bot/handlers/admin.py:4996`
- `st_op:`: `bot/handlers/admin.py:4966`
- `st_pick:`: `bot/handlers/admin.py:3344`
- `st_rev:`: `bot/handlers/admin.py:3274`
- `storage:cat:`: `bot/handlers/admin.py:964`
- `storage:item:`: `bot/handlers/admin.py:995`
- `storage:page:`: `bot/handlers/admin.py:981`
- `storage:purge:`: `bot/handlers/admin.py:1121`
- `storage:restock:`: `bot/handlers/admin.py:1053`
- `toggle:`: `bot/handlers/admin.py:7858`
- `vote:cast:`: `bot/handlers/polls.py:163`
- `vote:close:`: `bot/handlers/polls.py:287`
- `vote:close_confirm:`: `bot/handlers/polls.py:310`
- `vote:results:`: `bot/handlers/polls.py:185`
- `vote:show:`: `bot/handlers/polls.py:109`
- `wall:archpage:\d+$`: `bot/handlers/wall.py:338`
- `wall:archread:\d+(?::\d+)?$`: `bot/handlers/wall.py:357`
- `wall:delete:\d+$`: `bot/handlers/wall.py:224`
- `wall:page:\d+$`: `bot/handlers/wall.py:156`
- `weff:`: `bot/handlers/admin.py:1392`
- `wing_set:`: `bot/handlers/admin.py:812`
- `Испорченный`: `bot/handlers/dungeon.py:1808`
- `⛔`: `bot/handlers/wall.py:176`

## 4. ⚠️ Возможные конфликты

- Дублей точных `F.data ==` фильтров не найдено.

**Префиксный фильтр перекрывает точный ключ** (проверь порядок регистрации):

- `startswith("field:")` ⇄ `== "field:weapon_effect"`
- `startswith("field:")` ⇄ `== "field:photo"`
- `startswith("field:")` ⇄ `== "field:drink"`
- `startswith("field:")` ⇄ `== "field:market_ok"`
- `startswith("field:")` ⇄ `== "field:loot_only"`
- `startswith("fin:")` ⇄ `== "fin:manual"`

