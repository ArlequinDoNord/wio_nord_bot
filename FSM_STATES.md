# Карта FSM-состояний и callback-неймспейсов N.O.R.D.

> **Сгенерировано** `tools/export_states.py`. Не редактировать вручную —
> правь код и перегенерируй: `.venv\Scripts\python.exe tools/export_states.py`.
>
> Назначение: единый обзор всех `StatesGroup`, где они ставятся и где ловятся,
> а также реестр `callback_data` — чтобы не допускать конфликтов меню/хендлеров.

Всего классов состояний: **51**; полей-состояний: **226**; уникальных `callback_data`: **264**.

## 1. Классы состояний по модулям

### `AdminAddItem` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `name` | `bot/handlers/admin.py:1211` `shop_admin_add`<br>`bot/handlers/admin.py:6322` `enemy_drop_new_item` | `bot/handlers/admin.py:1219` `add_item_name` |
| `desc` | `bot/handlers/admin.py:1221` `add_item_name` | `bot/handlers/admin.py:1227` `add_item_desc` |
| `price` | `bot/handlers/admin.py:1230` `add_item_desc` | `bot/handlers/admin.py:1236` `add_item_price` |
| `sell_price` | `bot/handlers/admin.py:1246` `add_item_price` | `bot/handlers/admin.py:1252` `add_item_sell_price` |
| `rarity` | `bot/handlers/admin.py:1264` `add_item_sell_price` | — |
| `category` | `bot/handlers/admin.py:1273` `add_item_rarity` | — |
| `drink` | `bot/handlers/admin.py:1296` `add_item_category` | — |
| `plant_name` | `bot/handlers/admin.py:1285` `add_item_category` | `bot/handlers/admin.py:1321` `add_item_plant_name` |
| `stock` | `bot/handlers/admin.py:1305` `add_item_category`<br>`bot/handlers/admin.py:1315` `add_item_drink_choice`<br>`bot/handlers/admin.py:1324` `add_item_plant_name` | `bot/handlers/admin.py:1330` `add_item_stock` |
| `stats` | `bot/handlers/admin.py:1344` `add_item_stock`<br>`bot/handlers/admin.py:1349` `add_item_stock` | `bot/handlers/admin.py:1357` `add_item_stats`<br>`bot/handlers/admin.py:1397` `add_item_stats_bad` |
| `equip_slot` | `bot/handlers/admin.py:1374` `add_item_stats` | — |
| `weapon_effect` | `bot/handlers/admin.py:1362` `add_item_stats` | — |
| `weapon_effect_chance` | `bot/handlers/admin.py:1410` `add_item_weapon_effect_cb` | `bot/handlers/admin.py:1419` `add_item_weapon_effect_chance` |
| `weapon_effect_dmg` | `bot/handlers/admin.py:1431` `add_item_weapon_effect_chance` | `bot/handlers/admin.py:1443` `add_item_weapon_effect_dmg` |
| `producer` | `bot/handlers/admin.py:1458` `_go_add_item_producer` | — |
| `producer_user` | `bot/handlers/admin.py:1473` `add_item_producer` | `bot/handlers/admin.py:1485` `add_item_producer_user` |
| `market` | `bot/handlers/admin.py:1496` `_go_add_item_market` | — |
| `loot` | `bot/handlers/admin.py:1518` `_go_add_item_loot` | — |
| `status` | `bot/handlers/admin.py:1546` `_go_add_item_status` | — |
| `photo` | `bot/handlers/admin.py:1565` `add_item_status_cb` | `bot/handlers/admin.py:1573` `add_item_photo` |

### `AdminSaleTax` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `percent` | `bot/handlers/admin.py:2458` `admin_saletax_view` | `bot/handlers/admin.py:2472` `admin_saletax_set` |

### `AdminSpecialCode` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `code` | `bot/handlers/admin.py:2500` `admin_special_code_view` | `bot/handlers/admin.py:2515` `admin_special_code_set` |

### `AdminEditItem` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `item_id` | — | — |
| `field` | `bot/handlers/admin.py:1801` `edit_item_pick` | — |
| `value` | `bot/handlers/admin.py:2105` `edit_item_field` | `bot/handlers/admin.py:2116` `edit_item_value` |
| `photo` | `bot/handlers/admin.py:1890` `edit_item_field_photo` | `bot/handlers/admin.py:1940` `edit_item_photo` |

### `AdminFinance` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | `bot/handlers/admin.py:2538` `finance_manual`<br>`bot/handlers/admin.py:2556` `finance_pick` | `bot/handlers/admin.py:2794` `finance_target` |
| `currency` | — | — |
| `amount` | `bot/handlers/admin.py:455` `pickuser_cb`<br>`bot/handlers/admin.py:2626` `finance_pick_user`<br>`bot/handlers/admin.py:2801` `finance_target` | `bot/handlers/admin.py:2809` `finance_amount` |

### `AdminTreasury` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `amount` | `bot/handlers/admin.py:2365` `treasury_give` | `bot/handlers/admin.py:2375` `treasury_amount` |
| `target` | `bot/handlers/admin.py:2391` `treasury_amount` | `bot/handlers/admin.py:2397` `treasury_target_manual` |

### `AdminStorageRestock` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `amount` | `bot/handlers/admin.py:1073` `storage_restock` | `bot/handlers/admin.py:1087` `storage_restock_amount` |

### `AdminStorageDelete` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `confirm` | `bot/handlers/admin.py:1145` `storage_purge` | `bot/handlers/admin.py:1159` `storage_purge_confirm` |

### `AdminTax` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `percent` | `bot/handlers/admin.py:2421` `admin_tax_view` | `bot/handlers/admin.py:2433` `admin_tax_set` |

### `AdminReportAutoApprove` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `value` | `bot/handlers/admin.py:4358` `report_auto_approve_edit_cb` | `bot/handlers/admin.py:4371` `report_auto_approve_edit_value` |

### `AdminReportPayCap` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `value` | `bot/handlers/admin.py:4397` `report_pay_cap_edit_cb` | `bot/handlers/admin.py:4412` `report_pay_cap_edit_value` |

### `AdminReportFix` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `daily` | `bot/handlers/admin.py:4598` `report_fix_start` | `bot/handlers/admin.py:4611` `report_fix_daily` |
| `total` | `bot/handlers/admin.py:4625` `report_fix_daily` | `bot/handlers/admin.py:4639` `report_fix_total` |

### `AdminRoles` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | `bot/handlers/admin.py:2882` `admin_roles` | `bot/handlers/admin.py:2891` `roles_target` |
| `action` | `bot/handlers/admin.py:458` `pickuser_cb`<br>`bot/handlers/admin.py:2897` `roles_target` | — |
| `role` | `bot/handlers/admin.py:2915` `roles_action` | — |

### `AdminStatuses` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `name` | `bot/handlers/admin.py:3166` `status_create_start` | `bot/handlers/admin.py:3174` `status_create_name` |
| `tag` | `bot/handlers/admin.py:3176` `status_create_name` | `bot/handlers/admin.py:3185` `status_create_tag` |
| `level` | `bot/handlers/admin.py:3192` `status_create_tag` | `bot/handlers/admin.py:3202` `status_create_level` |
| `desc` | `bot/handlers/admin.py:3213` `status_create_level` | `bot/handlers/admin.py:3218` `status_create_desc` |
| `target` | `bot/handlers/admin.py:3439` `status_grant_target`<br>`bot/handlers/admin.py:3508` `status_revoke_target` | `bot/handlers/admin.py:3449` `status_grant_target_msg` |
| `grant_action` | — | — |
| `status_pick` | `bot/handlers/admin.py:473` `pickuser_cb`<br>`bot/handlers/admin.py:482` `pickuser_cb`<br>`bot/handlers/admin.py:3460` `status_grant_target_msg`<br>`bot/handlers/admin.py:3592` `status_grant_more` | — |
| `item_pick` | — | — |
| `item_status` | — | — |

### `AdminAwards` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `name` | `bot/handlers/admin.py:3681` `award_create_start` | `bot/handlers/admin.py:3738` `award_create_name` |
| `desc` | `bot/handlers/admin.py:3744` `award_create_name` | `bot/handlers/admin.py:3752` `award_create_desc` |
| `emoji` | `bot/handlers/admin.py:3755` `award_create_desc` | `bot/handlers/admin.py:3763` `award_create_emoji` |
| `bonus` | `bot/handlers/admin.py:3729` `_award_ask_bonus` | `bot/handlers/admin.py:3771` `award_create_bonus` |
| `preview` | `bot/handlers/admin.py:3717` `_award_ask_bonus` | — |
| `target` | `bot/handlers/admin.py:4157` `award_grant_target` | `bot/handlers/admin.py:4163` `award_grant_target_msg` |
| `award_pick` | `bot/handlers/admin.py:4238` `award_revoke_pick_user` | — |
| `comment` | `bot/handlers/admin.py:4181` `award_grant_pick` | `bot/handlers/admin.py:4198` `award_grant_comment` |
| `edit_value` | `bot/handlers/admin.py:4037` `award_edit_field_pick` | `bot/handlers/admin.py:4061` `award_edit_value` |

### `AdminFishing` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `water` | — | — |
| `wf_id` | — | — |
| `value` | `bot/handlers/admin.py:6883` `admin_fishing_junk_field_pick`<br>`bot/handlers/admin.py:7297` `admin_fishing_field_pick` | `bot/handlers/admin.py:7324` `admin_fishing_value` |
| `c_name` | `bot/handlers/admin.py:7134` `admin_fishing_new` | `bot/handlers/admin.py:7143` `admin_fishing_new_name` |
| `c_desc` | `bot/handlers/admin.py:7153` `admin_fishing_new_name` | `bot/handlers/admin.py:7159` `admin_fishing_new_desc` |
| `c_sell_price` | `bot/handlers/admin.py:7162` `admin_fishing_new_desc` | `bot/handlers/admin.py:7168` `admin_fishing_new_sell_price` |
| `c_day_weight` | `bot/handlers/admin.py:7176` `admin_fishing_new_sell_price` | `bot/handlers/admin.py:7184` `admin_fishing_new_day_weight` |
| `c_night_weight` | `bot/handlers/admin.py:7192` `admin_fishing_new_day_weight` | `bot/handlers/admin.py:7200` `admin_fishing_new_night_weight` |
| `c_photo` | `bot/handlers/admin.py:7232` `admin_fishing_new_super` | `bot/handlers/admin.py:7240` `admin_fishing_new_photo` |
| `c_super_rare` | `bot/handlers/admin.py:7208` `admin_fishing_new_night_weight` | — |

### `AdminForest` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `f_id` | — | — |
| `field` | — | — |
| `value` | `bot/handlers/admin.py:7879` `admin_forest_field_pick` | `bot/handlers/admin.py:7905` `admin_forest_value` |
| `c_name` | `bot/handlers/admin.py:7961` `admin_forest_new` | `bot/handlers/admin.py:7970` `admin_forest_new_name` |
| `c_desc` | `bot/handlers/admin.py:7980` `admin_forest_new_name` | `bot/handlers/admin.py:7986` `admin_forest_new_desc` |
| `c_sell_price` | `bot/handlers/admin.py:7989` `admin_forest_new_desc` | `bot/handlers/admin.py:7995` `admin_forest_new_sell_price` |
| `c_chance` | `bot/handlers/admin.py:8002` `admin_forest_new_sell_price` | `bot/handlers/admin.py:8011` `admin_forest_new_chance` |
| `c_kind` | `bot/handlers/admin.py:8019` `admin_forest_new_chance` | — |
| `c_photo` | `bot/handlers/admin.py:8042` `admin_forest_new_kind` | `bot/handlers/admin.py:8050` `admin_forest_new_photo` |
| `zone_value` | `bot/handlers/admin.py:7559` `admin_forest_zone_chance`<br>`bot/handlers/admin.py:7634` `admin_forest_zone_set_pick`<br>`bot/handlers/admin.py:7647` `admin_forest_limit_set` | `bot/handlers/admin.py:7654` `admin_forest_zone_value` |

### `AdminEnemy` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `field` | `bot/handlers/admin.py:9399` `admin_enemies_field_pick` | `bot/handlers/admin.py:9405` `admin_enemies_field_value` |
| `photo` | `bot/handlers/admin.py:9456` `admin_enemies_photo_pick` | `bot/handlers/admin.py:9462` `admin_enemies_photo_value` |
| `onhit_value` | `bot/handlers/admin.py:6119` `source_enemy_effect_toggle` | `bot/handlers/admin.py:6125` `source_enemy_onhit_value` |
| `drop_chance` | `bot/handlers/admin.py:9616` `admin_enemies_drop_edit_chance`<br>`bot/handlers/admin.py:9690` `admin_enemies_drop_add_pick` | `bot/handlers/admin.py:9696` `admin_enemies_drop_chance_value` |
| `drop_qty` | `bot/handlers/admin.py:9629` `admin_enemies_drop_edit_qty`<br>`bot/handlers/admin.py:9717` `admin_enemies_drop_chance_value` | `bot/handlers/admin.py:9723` `admin_enemies_drop_qty_value` |
| `c_name` | `bot/handlers/admin.py:9762` `admin_enemies_new` | `bot/handlers/admin.py:9767` `admin_enemies_new_name` |
| `c_hp` | `bot/handlers/admin.py:9773` `admin_enemies_new_name` | `bot/handlers/admin.py:9778` `admin_enemies_new_hp` |
| `c_dmg` | `bot/handlers/admin.py:9784` `admin_enemies_new_hp` | `bot/handlers/admin.py:9789` `admin_enemies_new_dmg` |
| `c_dodge` | `bot/handlers/admin.py:9802` `admin_enemies_new_dmg` | `bot/handlers/admin.py:9807` `admin_enemies_new_dodge` |
| `c_chance` | `bot/handlers/admin.py:9813` `admin_enemies_new_dodge` | `bot/handlers/admin.py:9819` `admin_enemies_new_chance` |
| `c_loss_ap` | `bot/handlers/admin.py:9825` `admin_enemies_new_chance` | `bot/handlers/admin.py:9831` `admin_enemies_new_done` |

### `AdminCallsign` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | `bot/handlers/admin.py:758` `admin_callsign_start` | `bot/handlers/admin.py:779` `admin_callsign_target_msg` |
| `value` | `bot/handlers/admin.py:540` `pickuser_cb`<br>`bot/handlers/admin.py:789` `admin_callsign_target_msg` | `bot/handlers/admin.py:800` `admin_callsign_value_msg` |

### `AdminWing` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | `bot/handlers/admin.py:771` `admin_wing_start` | — |
| `value` | `bot/handlers/admin.py:551` `pickuser_cb` | — |

### `AdminStates` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | `bot/handlers/admin.py:5134` `admin_states_menu` | `bot/handlers/admin.py:5143` `admin_states_target_text` |
| `action` | `bot/handlers/admin.py:512` `pickuser_cb`<br>`bot/handlers/admin.py:5149` `admin_states_target_text` | — |
| `state_key` | `bot/handlers/admin.py:5175` `admin_states_op` | — |
| `minutes` | `bot/handlers/admin.py:5200` `admin_states_key` | `bot/handlers/admin.py:5209` `admin_states_minutes`<br>`bot/handlers/admin.py:5230` `admin_states_minutes_bad` |

### `AdminPlayerLog` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | `bot/handlers/admin.py:744` `admin_player_log_start` | `bot/handlers/admin.py:612` `admin_player_log_manual_msg` |

### `AdminSalary` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `amount` | `bot/handlers/admin.py:525` `pickuser_cb` | `bot/handlers/admin.py:5330` `admin_salary_amount` |

### `AdminLocation` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `action` | — | — |
| `target_id` | — | — |
| `key` | `bot/handlers/admin.py:8105` `loc_create` | `bot/handlers/admin.py:8369` `loc_step_key` |
| `name` | `bot/handlers/admin.py:8375` `loc_step_key` | `bot/handlers/admin.py:8380` `loc_step_name` |
| `set_name` | `bot/handlers/admin.py:8396` `loc_set_name` | `bot/handlers/admin.py:8407` `loc_step_set_name` |
| `description` | `bot/handlers/admin.py:8382` `loc_step_name`<br>`bot/handlers/admin.py:8421` `loc_step_set_name`<br>`bot/handlers/admin.py:8435` `loc_set_desc` | `bot/handlers/admin.py:8642` `loc_step_desc` |
| `mode` | `bot/handlers/admin.py:8201` `loc_set_mode`<br>`bot/handlers/admin.py:8653` `loc_step_desc` | `bot/handlers/admin.py:8214` `loc_mode_chosen` |
| `req_status` | `bot/handlers/admin.py:8227` `loc_mode_chosen`<br>`bot/handlers/admin.py:8236` `loc_mode_chosen`<br>`bot/handlers/admin.py:8245` `loc_set_status` | `bot/handlers/admin.py:8250` `loc_req_status_chosen` |
| `blocking` | `bot/handlers/admin.py:8233` `loc_mode_chosen`<br>`bot/handlers/admin.py:8264` `loc_req_status_chosen`<br>`bot/handlers/admin.py:8280` `loc_set_blocking` | `bot/handlers/admin.py:8285` `loc_blocking_chosen` |
| `preview` | `bot/handlers/admin.py:8679` `loc_glade_set`<br>`bot/handlers/admin.py:8729` `loc_clearing_set`<br>`bot/handlers/admin.py:8781` `loc_logging_set`<br>`bot/handlers/admin.py:8832` `loc_mine_set`<br>`bot/handlers/admin.py:8883` `loc_storage_set`<br>`bot/handlers/admin.py:8932` `loc_photo_set`<br>`bot/handlers/admin.py:8970` `loc_season_photo_set` | `bot/handlers/admin.py:9012` `loc_step_photo` |

### `AdminDungeon` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target_id` | — | — |
| `photo_tod` | `bot/handlers/admin.py:5491` `dungeon_photo_set` | `bot/handlers/admin.py:5527` `dungeon_step_photo` |
| `enemy_id` | — | — |
| `enemy_field` | — | — |
| `enemy_value` | `bot/handlers/admin.py:5763` `dungeon_enemy_field_pick` | `bot/handlers/admin.py:5789` `dungeon_enemy_value` |
| `onhit_value` | `bot/handlers/admin.py:6043` `dungeon_enemy_effect_toggle` | `bot/handlers/admin.py:6049` `dungeon_enemy_onhit_value` |
| `drop_chance` | `bot/handlers/admin.py:1617` `add_item_photo`<br>`bot/handlers/admin.py:6299` `enemy_drop_pick_item`<br>`bot/handlers/admin.py:6382` `enemy_drop_set_chance` | `bot/handlers/admin.py:6704` `enemy_drop_chance_value` |
| `drop_qty` | `bot/handlers/admin.py:6405` `enemy_drop_set_qty`<br>`bot/handlers/admin.py:6713` `enemy_drop_chance_value` | `bot/handlers/admin.py:6719` `enemy_drop_qty_value` |
| `drop_item_photo` | `bot/handlers/admin.py:6450` `enemy_drop_item_photo` | `bot/handlers/admin.py:6459` `enemy_drop_item_photo_value` |
| `drop_item_desc` | `bot/handlers/admin.py:6504` `enemy_drop_item_desc` | `bot/handlers/admin.py:6513` `enemy_drop_item_desc_value` |
| `drop_item_field` | — | — |
| `drop_item_value` | `bot/handlers/admin.py:6602` `enemy_drop_item_stat_pick` | `bot/handlers/admin.py:6613` `enemy_drop_item_stat_value` |
| `pending_enemy_id` | — | — |

### `ClanPhotosAdmin` — `bot/handlers/admin_clanphotos.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `wait_exp_photo` | `bot/handlers/admin_clanphotos.py:134` `clanph_exp_cb` | `bot/handlers/admin_clanphotos.py:146` `clanph_exp_photo_save` |
| `wait_building_photo` | `bot/handlers/admin_clanphotos.py:259` `clanph_bclan_cb` | `bot/handlers/admin_clanphotos.py:269` `clanph_building_photo_save` |
| `wait_construction_photo` | `bot/handlers/admin_clanphotos.py:178` `clanph_construction_cb` | `bot/handlers/admin_clanphotos.py:189` `clanph_construction_photo_save` |

### `RecipeManager` — `bot/handlers/admin_recipes.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `c_kind` | `bot/handlers/admin_recipes.py:686` `recadm_create` | — |
| `c_name` | `bot/handlers/admin_recipes.py:716` `recadm_kind` | `bot/handlers/admin_recipes.py:725` `recadm_c_name` |
| `c_desc` | `bot/handlers/admin_recipes.py:742` `recadm_c_name` | `bot/handlers/admin_recipes.py:750` `recadm_c_desc` |
| `c_ing_cat` | `bot/handlers/admin_recipes.py:759` `recadm_c_desc`<br>`bot/handlers/admin_recipes.py:775` `recadm_ing_cat`<br>`bot/handlers/admin_recipes.py:783` `recadm_ing_cats`<br>`bot/handlers/admin_recipes.py:791` `recadm_ing_more`<br>`bot/handlers/admin_recipes.py:856` `recadm_c_ing_qty`<br>`bot/handlers/admin_recipes.py:1720` `recadm_ei` | — |
| `c_ing_qty` | `bot/handlers/admin_recipes.py:809` `recadm_ing_pick` | `bot/handlers/admin_recipes.py:822` `recadm_c_ing_qty` |
| `c_book` | `bot/handlers/admin_recipes.py:756` `recadm_c_desc`<br>`bot/handlers/admin_recipes.py:963` `recadm_book_page`<br>`bot/handlers/admin_recipes.py:986` `recadm_book_pick` | — |
| `c_book_price` | `bot/handlers/admin_recipes.py:1004` `recadm_book_done` | `bot/handlers/admin_recipes.py:1013` `recadm_c_book_price` |
| `res_mode` | `bot/handlers/admin_recipes.py:890` `recadm_ing_done`<br>`bot/handlers/admin_recipes.py:1746` `recadm_er` | — |
| `c_res_cat` | `bot/handlers/admin_recipes.py:909` `recadm_res_existing`<br>`bot/handlers/admin_recipes.py:923` `recadm_res_cat`<br>`bot/handlers/admin_recipes.py:931` `recadm_res_cats` | — |
| `n_name` | `bot/handlers/admin_recipes.py:1064` `recadm_res_new` | `bot/handlers/admin_recipes.py:1072` `recadm_n_name` |
| `n_desc` | `bot/handlers/admin_recipes.py:1092` `recadm_n_name` | `bot/handlers/admin_recipes.py:1098` `recadm_n_desc` |
| `n_cat` | `bot/handlers/admin_recipes.py:1105` `recadm_n_desc` | — |
| `n_heal` | `bot/handlers/admin_recipes.py:1127` `recadm_n_cat` | `bot/handlers/admin_recipes.py:1135` `recadm_n_heal` |
| `n_regen` | `bot/handlers/admin_recipes.py:1145` `recadm_n_heal` | `bot/handlers/admin_recipes.py:1154` `recadm_n_regen` |
| `n_ap` | `bot/handlers/admin_recipes.py:1164` `recadm_n_regen` | `bot/handlers/admin_recipes.py:1172` `recadm_n_ap` |
| `n_armor` | `bot/handlers/admin_recipes.py:1182` `recadm_n_ap` | `bot/handlers/admin_recipes.py:1187` `recadm_n_armor` |
| `n_dmg` | `bot/handlers/admin_recipes.py:1197` `recadm_n_armor` | `bot/handlers/admin_recipes.py:1202` `recadm_n_dmg` |
| `n_drink` | `bot/handlers/admin_recipes.py:1212` `recadm_n_dmg` | `bot/handlers/admin_recipes.py:1220` `recadm_n_drink` |
| `n_price` | `bot/handlers/admin_recipes.py:1227` `recadm_n_drink` | `bot/handlers/admin_recipes.py:1235` `recadm_n_price` |
| `n_rarity` | `bot/handlers/admin_recipes.py:1245` `recadm_n_price` | — |
| `n_photo` | `bot/handlers/admin_recipes.py:1266` `recadm_n_rarity` | `bot/handlers/admin_recipes.py:1277` `recadm_n_photo` |
| `c_exp` | `bot/handlers/admin_recipes.py:468` `_resolve_result`<br>`bot/handlers/admin_recipes.py:512` `_newitem_done` | — |
| `c_lvl` | `bot/handlers/admin_recipes.py:1301` `recadm_exp` | — |
| `c_ap` | `bot/handlers/admin_recipes.py:1321` `recadm_lvl` | `bot/handlers/admin_recipes.py:1326` `recadm_c_ap` |
| `c_time` | `bot/handlers/admin_recipes.py:1334` `recadm_c_ap` | `bot/handlers/admin_recipes.py:1339` `recadm_c_time` |
| `c_rarity` | `bot/handlers/admin_recipes.py:1347` `recadm_c_time` | — |
| `c_qty` | `bot/handlers/admin_recipes.py:1366` `recadm_rar` | `bot/handlers/admin_recipes.py:1374` `recadm_c_qty` |
| `c_shop` | `bot/handlers/admin_recipes.py:1382` `recadm_c_qty` | `bot/handlers/admin_recipes.py:1391` `recadm_c_shop` |
| `c_confirm` | `bot/handlers/admin_recipes.py:1399` `recadm_c_shop` | — |
| `e_value` | `bot/handlers/admin_recipes.py:1509` `recadm_ef` | `bot/handlers/admin_recipes.py:1515` `recadm_e_value` |

### `ClanShopAdmin` — `bot/handlers/admin_shop_clan.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `wait_item` | `bot/handlers/admin_shop_clan.py:142` `clanshopadm_add_cb` | `bot/handlers/admin_shop_clan.py:155` `clanshopadm_item_msg` |
| `wait_price` | `bot/handlers/admin_shop_clan.py:177` `clanshopadm_item_msg` | `bot/handlers/admin_shop_clan.py:185` `clanshopadm_price_msg` |
| `wait_stock` | `bot/handlers/admin_shop_clan.py:194` `clanshopadm_price_msg` | `bot/handlers/admin_shop_clan.py:201` `clanshopadm_stock_msg` |
| `edit_price` | `bot/handlers/admin_shop_clan.py:307` `clanshopadm_edit_price_cb` | `bot/handlers/admin_shop_clan.py:313` `clanshopadm_edit_price_msg` |
| `edit_stock` | `bot/handlers/admin_shop_clan.py:341` `clanshopadm_edit_stock_cb` | `bot/handlers/admin_shop_clan.py:347` `clanshopadm_edit_stock_msg` |

### `BankStates` — `bot/handlers/bank.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `waiting_recipient` | `bot/handlers/bank.py:150` `bank_transfer_manual` | `bot/handlers/bank.py:257` `process_recipient` |
| `waiting_amount` | `bot/handlers/bank.py:162` `set_recipient` | `bot/handlers/bank.py:279` `process_amount` |
| `waiting_message` | `bot/handlers/bank.py:322` `process_amount` | `bot/handlers/bank.py:331` `process_message` |
| `waiting_treasury_amount` | `bot/handlers/bank.py:208` `bank_treasury` | `bot/handlers/bank.py:218` `process_treasury_amount` |

### `ClanHallAdminPhoto` — `bot/handlers/clan_hall.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `wait_building_photo` | `bot/handlers/clan_hall.py:1959` `clan_hall_admphoto_cb` | `bot/handlers/clan_hall.py:1995` `clan_hall_admphoto_save` |
| `wait_construction_photo` | `bot/handlers/clan_hall.py:1988` `clan_hall_admconstphoto_cb` | `bot/handlers/clan_hall.py:2013` `clan_hall_admconstphoto_save` |
| `wait_expansion_photo` | `bot/handlers/clan_hall.py:2037` `clan_hall_admexphoto_cb` | `bot/handlers/clan_hall.py:2049` `clan_hall_admexphoto_save` |

### `ClansCreate` — `bot/handlers/clans.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `kind` | — | — |
| `wait_name` | `bot/handlers/clans.py:702` `clan_create_start` | `bot/handlers/clans.py:710` `clan_create_name` |
| `wait_desc` | `bot/handlers/clans.py:717` `clan_create_name` | `bot/handlers/clans.py:725` `clan_create_desc` |
| `wait_photo` | `bot/handlers/clans.py:735` `clan_create_desc` | `bot/handlers/clans.py:779` `clan_create_photo`<br>`bot/handlers/clans.py:786` `clan_create_photo_hint` |

### `ClansEdit` — `bot/handlers/clans.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `field` | — | — |
| `wait_value` | `bot/handlers/clans.py:850` `clan_edit_field_cb` | `bot/handlers/clans.py:856` `clan_edit_finish_photo`<br>`bot/handlers/clans.py:870` `clan_edit_finish_text` |

### `ClansMessage` — `bot/handlers/clans.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `wait_text` | `bot/handlers/clans.py:907` `clan_msg_start` | `bot/handlers/clans.py:915` `clan_msg_send` |

### `DungeonFSM` — `bot/handlers/dungeon.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `in_dungeon` | `bot/handlers/dungeon.py:937` `contract_enter_confirm`<br>`bot/handlers/dungeon.py:1016` `post_captain_menu`<br>`bot/handlers/dungeon.py:2449` `resv_deeper` | — |
| `in_combat` | — | — |
| `in_boss` | `bot/handlers/dungeon.py:2081` `show_boss` | — |
| `confirm_enter` | `bot/handlers/dungeon.py:866` `contract_enter` | — |
| `in_reservoir` | `bot/handlers/dungeon.py:2103` `resv_enter`<br>`bot/handlers/dungeon.py:2118` `resv_menu`<br>`bot/handlers/dungeon.py:2185` `resv_bait_set` | — |

### `HqOrder` — `bot/handlers/hq.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | `bot/handlers/hq.py:175` `hq_order_start`<br>`bot/handlers/hq.py:717` `hq_wingcmd_send_cb` | `bot/handlers/hq.py:184` `hq_order_text` |

### `HqWingCreate` — `bot/handlers/hq.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `num` | `bot/handlers/hq.py:1071` `hq_wing_add_start` | `bot/handlers/hq.py:1080` `hq_wing_add_num` |
| `abbr` | `bot/handlers/hq.py:1089` `hq_wing_add_num` | `bot/handlers/hq.py:1099` `hq_wing_add_abbr` |
| `name` | `bot/handlers/hq.py:1108` `hq_wing_add_abbr` | `bot/handlers/hq.py:1116` `hq_wing_add_name` |
| `callsign` | `bot/handlers/hq.py:1125` `hq_wing_add_name` | `bot/handlers/hq.py:1133` `hq_wing_add_callsign` |
| `emoji` | `bot/handlers/hq.py:1141` `hq_wing_add_callsign` | `bot/handlers/hq.py:1149` `hq_wing_add_emoji` |

### `HqWingEdit` — `bot/handlers/hq.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `field` | — | — |
| `value` | `bot/handlers/hq.py:1195` `hq_wing_edit_cb` | `bot/handlers/hq.py:1205` `hq_wing_edit_value` |

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
| `waiting_photo` | `bot/handlers/profile.py:255` `set_photo` | `bot/handlers/profile.py:263` `process_photo` |
| `waiting_about` | `bot/handlers/profile.py:276` `edit_about` | `bot/handlers/profile.py:284` `process_about` |
| `waiting_callsign` | `bot/handlers/profile.py:610` `profile_callsign`<br>`bot/handlers/profile.py:621` `profile_callsign`<br>`bot/handlers/profile.py:718` `profile_callsign_buy` | `bot/handlers/profile.py:658` `profile_callsign_input` |

### `ReportSubmit` — `bot/handlers/reports.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `waiting_photo` | `bot/handlers/reports.py:102` `report_submit_start` | `bot/handlers/reports.py:112` `report_receive_photo`<br>`bot/handlers/reports.py:131` `report_photo_expected` |
| `waiting_daily_troops` | `bot/handlers/reports.py:118` `report_receive_photo` | `bot/handlers/reports.py:136` `report_receive_daily_troops`<br>`bot/handlers/reports.py:161` `report_daily_troops_expected` |
| `waiting_total_troops` | `bot/handlers/reports.py:148` `report_receive_daily_troops` | `bot/handlers/reports.py:166` `report_receive_total_troops`<br>`bot/handlers/reports.py:197` `report_total_troops_expected` |
| `waiting_region` | `bot/handlers/reports.py:175` `report_receive_total_troops` | `bot/handlers/reports.py:202` `report_receive_region`<br>`bot/handlers/reports.py:296` `report_region_expected` |

### `RepSpeech` — `bot/handlers/representative.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `waiting_text` | `bot/handlers/representative.py:101` `rep_speech_write`<br>`bot/handlers/representative.py:128` `rep_speech_delete` | `bot/handlers/representative.py:176` `rep_speech_text` |

### `SpecialDeptBuy` — `bot/handlers/shop.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `code` | `bot/handlers/shop.py:526` `_start_special_dept_buy` | `bot/handlers/shop.py:538` `special_dept_enter_code` |

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
| `bank:` | 3 | `bank:menu`, `bank:noop`, `bank:transfer_manual` |
| `booklet:` | 1 | `booklet:claim` |
| `cancel:` | 1 | `cancel` |
| `city:` | 5 | `city:clans`, `city:menu`, `city:pilots`, `city:pilots:list`, `city:vote` |
| `clanh:` | 1 | `clanh:noop` |
| `clanhph:` | 3 | `clanhph:buildings`, `clanhph:construction`, `clanhph:menu` |
| `clans:` | 4 | `clans:create_skip`, `clans:list:clan`, `clans:list:party`, `clans:noop` |
| `contracts:` | 1 | `contracts:list` |
| `duel:` | 5 | `duel:card:buy`, `duel:help`, `duel:list`, `duel:menu`, `duel:top` |
| `dungeon:` | 6 | `dungeon:enemies`, `dungeon:exit`, `dungeon:exit:cancel`, `dungeon:exit:confirm`, `dungeon:photos`, `dungeon:photos:clear` |
| `enemy_field:` | 7 | `enemy_field:armor`, `enemy_field:attack`, `enemy_field:description`, `enemy_field:dodge`, `enemy_field:hp`, `enemy_field:image`, `enemy_field:reward_nm` |
| `eqlock:` | 2 | `eqlock:potion3`, `eqlock:weapon_aux` |
| `eqpart:` | 4 | `eqpart:body`, `eqpart:hands`, `eqpart:head`, `eqpart:legs` |
| `eqslot:` | 2 | `eqslot:duel`, `eqslot:smoke` |
| `field:` | 24 | `field:ap_cost`, `field:armor`, `field:category`, `field:damage`, `field:description`, `field:drink`, `field:heal`, `field:housing_slots`, `field:housing_type`, `field:is_available`, `field:loot_only`, `field:market_ok`, `field:name`, `field:photo`, `field:plant_name`, `field:price`, `field:rarity`, `field:regen`, `field:required_status`, `field:sell_price`, `field:stock`, `field:weapon_effect`, `field:weapon_effect_chance`, `field:weapon_effect_dmg` |
| `field_req:` | 1 | `field_req:none` |
| `fin:` | 3 | `fin:manual`, `fin:nord:add`, `fin:nord:sub` |
| `finh:` | 1 | `finh:open` |
| `fish:` | 1 | `fish:recover` |
| `fishing:` | 4 | `fishing:new_super:0`, `fishing:new_super:1`, `fishing:water:lake`, `fishing:water:reservoir` |
| `fishing_field:` | 4 | `fishing_field:day_weight`, `fishing_field:night_weight`, `fishing_field:photo`, `fishing_field:sell_price` |
| `forest:` | 4 | `forest:new`, `forest:new_kind:edible`, `forest:new_kind:toxic`, `forest:zset:sold_daily_limit` |
| `forest_field:` | 3 | `forest_field:chance`, `forest_field:photo`, `forest_field:sell_price` |
| `hq:` | 19 | `hq:farms`, `hq:menu`, `hq:noop`, `hq:order:all`, `hq:region_stats`, `hq:region_stats_refresh`, `hq:roster:0`, `hq:send`, `hq:wing`, `hq:wingadd`, `hq:wingcmd`, `hq:wingcmd_send`, `hq:wingdrop:0`, `hq:wingedit:callsign`, `hq:wingedit:emoji`, `hq:wingedit:name`, `hq:wingfarm:0`, `hq:wings`, `hq:wingtake:0` |
| `inventory:` | 2 | `inventory:eq`, `inventory:list` |
| `kvp:` | 3 | `kvp:exit`, `kvp:resume`, `kvp:start` |
| `lib:` | 2 | `lib:menu`, `lib:no_access` |
| `libadmin:` | 3 | `libadmin:add`, `libadmin:list`, `libadmin:menu` |
| `loc:` | 21 | `loc:blocking:done`, `loc:blocking:none`, `loc:building_pick`, `loc:clearing_set`, `loc:create`, `loc:edit_pick`, `loc:glade_set`, `loc:logging_set`, `loc:mine_set`, `loc:mode:all`, `loc:mode:exact`, `loc:mode:min`, `loc:photos`, `loc:photos:clear`, `loc:photos:clear_seasons`, `loc:set_blocking`, `loc:set_desc`, `loc:set_mode`, `loc:set_name`, `loc:set_status`, `loc:storage_set` |
| `logsite:` | 2 | `logsite:back`, `logsite:enter` |
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
| `recadm:` | 17 | `recadm:book_done`, `recadm:bookpage:0`, `recadm:books`, `recadm:cancel`, `recadm:create`, `recadm:ing_done`, `recadm:ing_more`, `recadm:ingcats`, `recadm:kind:book`, `recadm:kind:scroll`, `recadm:list`, `recadm:menu`, `recadm:no_photo`, `recadm:noop`, `recadm:res_existing`, `recadm:res_new`, `recadm:save` |
| `rep:` | 5 | `rep:auto_approve_edit`, `rep:pay_cap_edit`, `rep:speech`, `rep:speech:delete`, `rep:speech:write` |
| `report:` | 1 | `report:menu` |
| `resv:` | 1 | `resv:recover` |
| `rolop:` | 2 | `rolop:add`, `rolop:remove` |
| `salary:` | 2 | `salary:choose`, `salary:pay` |
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

- `admin:awards`: `bot/handlers/admin.py:3598`
- `admin:callsign`: `bot/handlers/admin.py:752`
- `admin:del_photo`: `bot/handlers/admin.py:726`
- `admin:dungeons`: `bot/handlers/admin.py:5389`
- `admin:enemies`: `bot/handlers/admin.py:9205`
- `admin:finance`: `bot/handlers/admin.py:2184`
- `admin:fishing`: `bot/handlers/admin.py:6907`
- `admin:forest`: `bot/handlers/admin.py:7469`
- `admin:locations`: `bot/handlers/admin.py:5365`
- `admin:logs`: `bot/handlers/admin.py:4930`
- `admin:menu`: `bot/handlers/admin.py:716`
- `admin:player_log`: `bot/handlers/admin.py:738`
- `admin:ranks`: `bot/handlers/admin.py:4820`
- `admin:reports`: `bot/handlers/admin.py:4255`
- `admin:reports_done`: `bot/handlers/admin.py:4307`
- `admin:reports_pending`: `bot/handlers/admin.py:4264`
- `admin:roles`: `bot/handlers/admin.py:2872`
- `admin:salaries`: `bot/handlers/admin.py:5234`
- `admin:saletax`: `bot/handlers/admin.py:2451`
- `admin:shop`: `bot/handlers/admin.py:867`
- `admin:states`: `bot/handlers/admin.py:5128`
- `admin:statuses`: `bot/handlers/admin.py:3106`
- `admin:storage`: `bot/handlers/admin.py:941`
- `admin:tax`: `bot/handlers/admin.py:2414`
- `admin:treasury`: `bot/handlers/admin.py:2227`
- `admin:wing`: `bot/handlers/admin.py:765`
- `aw:ach`: `bot/handlers/admin.py:3656`
- `aw:create`: `bot/handlers/admin.py:3674`
- `aw:delete`: `bot/handlers/admin.py:3815`
- `aw:edit`: `bot/handlers/admin.py:3996`
- `aw:grant`: `bot/handlers/admin.py:4154`
- `aw:list`: `bot/handlers/admin.py:3635`
- `aw:revoke`: `bot/handlers/admin.py:4235`
- `aw_comment:skip`: `bot/handlers/admin.py:4192`
- `aw_confirm`: `bot/handlers/admin.py:3791`
- `back:main`: `bot/handlers/admin.py:5103`
- `bank:balance`: `bot/handlers/bank.py:72`
- `bank:menu`: `bot/handlers/bank.py:191`
- `bank:noop`: `bot/handlers/bank.py:453`
- `bank:transfer`: `bot/handlers/bank.py:131`
- `bank:transfer_manual`: `bot/handlers/bank.py:147`
- `bank:treasury`: `bot/handlers/bank.py:204`
- `booklet:claim`: `bot/handlers/tourist_booklet.py:71`
- `booklet:menu`: `bot/handlers/tourist_booklet.py:65`
- `cancel`: `bot/handlers/admin.py:5111`
- `city:business`: `bot/handlers/locations.py:243`
- `city:clans`: `bot/handlers/clans.py:91`
- `city:countryside`: `bot/handlers/locations.py:263`
- `city:dungeon`: `bot/handlers/dungeon.py:942`
- `city:library`: `bot/handlers/library.py:82`
- `city:menu`: `bot/handlers/start.py:158`
- `city:pilots`: `bot/handlers/pilots.py:102`
- `city:pilots:list`: `bot/handlers/pilots.py:129`
- `city:quarter`: `bot/handlers/locations.py:225`
- `city:vote`: `bot/handlers/polls.py:70`
- `clanh:noop`: `bot/handlers/clan_hall.py:2227`
- `clanhph:construction`: `bot/handlers/admin_clanphotos.py:172`
- `clanhph:menu`: `bot/handlers/admin_clanphotos.py:114`
- `clans:create_skip`: `bot/handlers/clans.py:790`
- `clans:noop`: `bot/handlers/clans.py:575`
- `clanshopadm:menu`: `bot/handlers/admin_shop_clan.py:103`
- `contracts:list`: `bot/handlers/dungeon.py:754`
- `del_item:back`: `bot/handlers/admin.py:1693`
- `duel:card:buy`: `bot/handlers/duel.py:246`
- `duel:help`: `bot/handlers/duel.py:224`
- `duel:list`: `bot/handlers/duel.py:272`
- `duel:menu`: `bot/handlers/duel.py:218`
- `duel:top`: `bot/handlers/duel.py:292`
- `dungeon:enemies`: `bot/handlers/admin.py:5705`
- `dungeon:exit`: `bot/handlers/dungeon.py:2592`
- `dungeon:exit:cancel`: `bot/handlers/dungeon.py:2677`
- `dungeon:exit:confirm`: `bot/handlers/dungeon.py:2639`
- `dungeon:photos`: `bot/handlers/admin.py:5472`
- `dungeon:photos:clear`: `bot/handlers/admin.py:5516`
- `enemy:fi`: `bot/handlers/admin.py:9243`
- `field:drink`: `bot/handlers/admin.py:1964`
- `field:loot_only`: `bot/handlers/admin.py:2028`
- `field:market_ok`: `bot/handlers/admin.py:2008`
- `field:photo`: `bot/handlers/admin.py:1885`
- `field:weapon_effect`: `bot/handlers/admin.py:1905`
- `fin:manual`: `bot/handlers/admin.py:2535`
- `finh:open`: `bot/handlers/admin.py:2720`
- `fireevent:enter`: `bot/handlers/fire_event.py:509`
- `fish:recover`: `bot/handlers/fishing.py:500`
- `forest:addlist`: `bot/handlers/admin.py:7800`
- `forest:new`: `bot/handlers/admin.py:7953`
- `forest:zset:sold_daily_limit`: `bot/handlers/admin.py:7639`
- `housing:menu`: `bot/handlers/housing.py:277`
- `housing:noop`: `bot/handlers/housing.py:784`
- `housing:pay_debt`: `bot/handlers/housing.py:322`
- `housing:pay_tax`: `bot/handlers/housing.py:313`
- `hq:farms`: `bot/handlers/hq.py:468`
- `hq:menu`: `bot/handlers/hq.py:148`
- `hq:noop`: `bot/handlers/hq.py:560`
- `hq:region_stats`: `bot/handlers/hq.py:507`
- `hq:region_stats_refresh`: `bot/handlers/hq.py:516`
- `hq:send`: `bot/handlers/hq.py:155`
- `hq:wing`: `bot/handlers/hq.py:235`
- `hq:wingadd`: `bot/handlers/hq.py:1065`
- `hq:wingcmd`: `bot/handlers/hq.py:568`
- `hq:wingcmd_send`: `bot/handlers/hq.py:706`
- `hq:wings`: `bot/handlers/hq.py:1035`
- `inventory:eq`: `bot/handlers/inventory.py:482`
- `inventory:list`: `bot/handlers/inventory.py:573`
- `kvp:exit`: `bot/handlers/kvp.py:734`
- `kvp:resume`: `bot/handlers/kvp.py:288`
- `kvp:start`: `bot/handlers/kvp.py:248`
- `lib:menu`: `bot/handlers/library.py:141`
- `lib:no_access`: `bot/handlers/library.py:136`
- `libadmin:add`: `bot/handlers/library.py:288`
- `libadmin:list`: `bot/handlers/library.py:384`
- `libadmin:menu`: `bot/handlers/library.py:271`
- `loc:building_pick`: `bot/handlers/admin.py:8131`
- `loc:clearing_clear`: `bot/handlers/admin.py:8753`
- `loc:clearing_set`: `bot/handlers/admin.py:8716`
- `loc:create`: `bot/handlers/admin.py:8099`
- `loc:edit_pick`: `bot/handlers/admin.py:8115`
- `loc:glade_clear`: `bot/handlers/admin.py:8703`
- `loc:glade_set`: `bot/handlers/admin.py:8665`
- `loc:logging_clear`: `bot/handlers/admin.py:8805`
- `loc:logging_set`: `bot/handlers/admin.py:8766`
- `loc:mine_clear`: `bot/handlers/admin.py:8856`
- `loc:mine_set`: `bot/handlers/admin.py:8818`
- `loc:photos`: `bot/handlers/admin.py:8591`
- `loc:photos:clear`: `bot/handlers/admin.py:8998`
- `loc:photos:clear_seasons`: `bot/handlers/admin.py:8614`
- `loc:set_blocking`: `bot/handlers/admin.py:8268`
- `loc:set_desc`: `bot/handlers/admin.py:8425`
- `loc:set_mode`: `bot/handlers/admin.py:8197`
- `loc:set_name`: `bot/handlers/admin.py:8386`
- `loc:set_status`: `bot/handlers/admin.py:8240`
- `loc:storage_clear`: `bot/handlers/admin.py:8907`
- `loc:storage_set`: `bot/handlers/admin.py:8869`
- `logsite:back`: `bot/handlers/logging_site.py:460`
- `logsite:enter`: `bot/handlers/logging_site.py:397`
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
- `noop`: `bot/handlers/admin.py:5098`
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
- `prof:back`: `bot/handlers/profile.py:342`
- `profile`: `bot/handlers/profile.py:244`
- `profile:achievements`: `bot/handlers/profile.py:499`
- `profile:awards`: `bot/handlers/profile.py:469`
- `profile:callsign`: `bot/handlers/profile.py:596`
- `profile:callsign_buy`: `bot/handlers/profile.py:702`
- `profile:callsign_cancel`: `bot/handlers/profile.py:650`
- `profile:choose_status`: `bot/handlers/profile.py:302`
- `profile:edit_about`: `bot/handlers/profile.py:273`
- `profile:notify_toggle`: `bot/handlers/profile.py:349`
- `profile:open`: `bot/handlers/profile.py:589`
- `profile:pilot_card`: `bot/handlers/profile.py:389`
- `profile:public_toggle`: `bot/handlers/profile.py:369`
- `profile:set_photo`: `bot/handlers/profile.py:252`
- `recadm:book_done`: `bot/handlers/admin_recipes.py:990`
- `recadm:books`: `bot/handlers/admin_recipes.py:569`
- `recadm:cancel`: `bot/handlers/admin_recipes.py:1473`
- `recadm:create`: `bot/handlers/admin_recipes.py:682`
- `recadm:ing_done`: `bot/handlers/admin_recipes.py:869`
- `recadm:ing_more`: `bot/handlers/admin_recipes.py:787`
- `recadm:ingcats`: `bot/handlers/admin_recipes.py:779`
- `recadm:list`: `bot/handlers/admin_recipes.py:561`
- `recadm:menu`: `bot/handlers/admin_recipes.py:541`
- `recadm:no_photo`: `bot/handlers/admin_recipes.py:1282`
- `recadm:noop`: `bot/handlers/admin_recipes.py:536`
- `recadm:res_existing`: `bot/handlers/admin_recipes.py:905`
- `recadm:res_new`: `bot/handlers/admin_recipes.py:1060`
- `recadm:rescats`: `bot/handlers/admin_recipes.py:927`
- `recadm:save`: `bot/handlers/admin_recipes.py:1420`
- `rep:auto_approve_edit`: `bot/handlers/admin.py:4351`
- `rep:next`: `bot/handlers/admin.py:4793`
- `rep:pay_cap_edit`: `bot/handlers/admin.py:4390`
- `rep:speech`: `bot/handlers/representative.py:77`
- `rep:speech:delete`: `bot/handlers/representative.py:109`
- `rep:speech:write`: `bot/handlers/representative.py:89`
- `report:menu`: `bot/handlers/reports.py:47`
- `report:my_reports`: `bot/handlers/reports.py:395`
- `report:submit`: `bot/handlers/reports.py:57`
- `resv:recover`: `bot/handlers/dungeon.py:2395`
- `salary:choose`: `bot/handlers/admin.py:5292`
- `salary:pay`: `bot/handlers/admin.py:5304`
- `shop:catalog`: `bot/handlers/shop.py:230`
- `shop_admin:add`: `bot/handlers/admin.py:1204`
- `shop_admin:delete`: `bot/handlers/admin.py:1664`
- `shop_admin:edit`: `bot/handlers/admin.py:1787`
- `shop_admin:special_code`: `bot/handlers/admin.py:2492`
- `shop_del:cats`: `bot/handlers/admin.py:1781`
- `shop_edit:cats`: `bot/handlers/admin.py:1766`
- `st:create`: `bot/handlers/admin.py:3160`
- `st:delete`: `bot/handlers/admin.py:3233`
- `st:grant`: `bot/handlers/admin.py:3433`
- `st:legioner`: `bot/handlers/admin.py:3378`
- `st:list`: `bot/handlers/admin.py:3143`
- `st:more`: `bot/handlers/admin.py:3579`
- `st:revoke`: `bot/handlers/admin.py:3499`
- `storage:cats`: `bot/handlers/admin.py:960`
- `storage:create`: `bot/handlers/admin.py:1205`
- `storage:menu`: `bot/handlers/storage.py:89`
- `storage:noop`: `bot/handlers/admin.py:955`
- `treasury:debts`: `bot/handlers/admin.py:2260`
- `treasury:give`: `bot/handlers/admin.py:2359`
- `treasury:stats`: `bot/handlers/admin.py:2307`
- `vote:close_cancel`: `bot/handlers/polls.py:332`
- `vote:create`: `bot/handlers/polls.py:224`
- `wall:archive`: `bot/handlers/wall.py:315`
- `wall:view`: `bot/handlers/wall.py:149`
- `wall:write`: `bot/handlers/wall.py:170`

### По префиксу (`F.data.startswith("...")`)

- `\d+$`: `bot/handlers/admin.py:1356`; `bot/handlers/admin.py:5208`; `bot/handlers/admin.py:7653`; `bot/handlers/reports.py:201`
- `\d{1,7}$`: `bot/handlers/reports.py:135`; `bot/handlers/reports.py:165`
- `act:`: `bot/handlers/admin.py:5005`
- `addreq:`: `bot/handlers/admin.py:1555`
- `aw_del:`: `bot/handlers/admin.py:3836`
- `aw_edit:`: `bot/handlers/admin.py:4016`
- `aw_ei:`: `bot/handlers/admin.py:4027`
- `aw_kind:`: `bot/handlers/admin.py:4125`
- `aw_pick:`: `bot/handlers/admin.py:4176`
- `awr_grant:`: `bot/handlers/admin.py:4243`
- `bait:set:`: `bot/handlers/fishing.py:176`
- `bank:history`: `bot/handlers/bank.py:403`
- `bank:pickrecipient:`: `bot/handlers/bank.py:177`
- `bank:transfer:list:`: `bot/handlers/bank.py:137`
- `buy5_nord:`: `bot/handlers/shop.py:493`
- `buy_housing:`: `bot/handlers/shop.py:1093`
- `buy_housing_cancel:`: `bot/handlers/shop.py:1084`
- `buy_nord:`: `bot/handlers/shop.py:483`
- `cat:`: `bot/handlers/admin.py:1277`
- `city/`: `bot/handlers/locations.py:87`
- `city:pilots:list:`: `bot/handlers/pilots.py:135`
- `clanh:admconstphoto:`: `bot/handlers/clan_hall.py:1980`
- `clanh:admexphoto:`: `bot/handlers/clan_hall.py:2023`
- `clanh:admnophoto:`: `bot/handlers/clan_hall.py:1966`
- `clanh:admphoto:`: `bot/handlers/clan_hall.py:1948`
- `clanh:bitem:`: `bot/handlers/clan_hall.py:1039`
- `clanh:buy:`: `bot/handlers/clan_hall.py:1082`
- `clanh:cancel:`: `bot/handlers/clan_hall.py:1814`
- `clanh:choose:`: `bot/handlers/clan_hall.py:1783`
- `clanh:craft:`: `bot/handlers/clan_hall.py:1405`
- `clanh:donate:`: `bot/handlers/clan_hall.py:2097`
- `clanh:expchoose:`: `bot/handlers/clan_hall.py:1272`
- `clanh:expinstall:`: `bot/handlers/clan_hall.py:1285`
- `clanh:expmanage:`: `bot/handlers/clan_hall.py:1261`
- `clanh:expup:`: `bot/handlers/clan_hall.py:1303`
- `clanh:give:`: `bot/handlers/clan_hall.py:2154`
- `clanh:hall:`: `bot/handlers/clan_hall.py:1763`
- `clanh:harvest:`: `bot/handlers/clan_hall.py:1700`
- `clanh:harvestall:`: `bot/handlers/clan_hall.py:1732`
- `clanh:inside:`: `bot/handlers/clan_hall.py:1890`
- `clanh:item:`: `bot/handlers/clan_hall.py:2123`
- `clanh:libgive:`: `bot/handlers/clan_hall.py:1145`
- `clanh:log:`: `bot/handlers/clan_hall.py:2212`
- `clanh:mushproc:`: `bot/handlers/clan_hall.py:1557`
- `clanh:mushrooms:`: `bot/handlers/clan_hall.py:1540`
- `clanh:plant:`: `bot/handlers/clan_hall.py:1676`
- `clanh:plantlist:`: `bot/handlers/clan_hall.py:1628`
- `clanh:recipe:`: `bot/handlers/clan_hall.py:1336`
- `clanh:shower:`: `bot/handlers/clan_hall.py:1592`
- `clanh:start:`: `bot/handlers/clan_hall.py:1828`
- `clanh:startfull:`: `bot/handlers/clan_hall.py:1857`
- `clanh:storage:`: `bot/handlers/clan_hall.py:2076`
- `clanh:upgrade:`: `bot/handlers/clan_hall.py:1799`
- `clanh:use:`: `bot/handlers/clan_hall.py:1319`
- `clanhier:`: `bot/handlers/clans.py:285`
- `clanhph:bclan:`: `bot/handlers/admin_clanphotos.py:247`
- `clanhph:buildings`: `bot/handlers/admin_clanphotos.py:208`
- `clanhph:exp:`: `bot/handlers/admin_clanphotos.py:123`
- `clans:add:`: `bot/handlers/clans.py:580`
- `clans:addset:`: `bot/handlers/clans.py:597`
- `clans:cancel:`: `bot/handlers/clans.py:396`
- `clans:create:`: `bot/handlers/clans.py:692`
- `clans:del:`: `bot/handlers/clans.py:944`
- `clans:delyes:`: `bot/handlers/clans.py:961`
- `clans:edit:`: `bot/handlers/clans.py:805`
- `clans:editf:`: `bot/handlers/clans.py:829`
- `clans:join:`: `bot/handlers/clans.py:359`
- `clans:kick:`: `bot/handlers/clans.py:530`
- `clans:leader:`: `bot/handlers/clans.py:621`
- `clans:leaderset:`: `bot/handlers/clans.py:638`
- `clans:leaderunset:`: `bot/handlers/clans.py:668`
- `clans:leave:`: `bot/handlers/clans.py:406`
- `clans:list:`: `bot/handlers/clans.py:131`
- `clans:manage:`: `bot/handlers/clans.py:474`
- `clans:msg:`: `bot/handlers/clans.py:899`
- `clans:reqno:`: `bot/handlers/clans.py:457`
- `clans:reqok:`: `bot/handlers/clans.py:433`
- `clans:view:`: `bot/handlers/clans.py:168`
- `clanshopadm:add:`: `bot/handlers/admin_shop_clan.py:134`
- `clanshopadm:clan:`: `bot/handlers/admin_shop_clan.py:121`
- `clanshopadm:del:`: `bot/handlers/admin_shop_clan.py:397`
- `clanshopadm:ep:`: `bot/handlers/admin_shop_clan.py:298`
- `clanshopadm:es:`: `bot/handlers/admin_shop_clan.py:332`
- `clanshopadm:hide:`: `bot/handlers/admin_shop_clan.py:369`
- `clanshopadm:it:`: `bot/handlers/admin_shop_clan.py:257`
- `clanshopadm:show:`: `bot/handlers/admin_shop_clan.py:383`
- `confirm_del_photo:`: `bot/handlers/admin.py:846`
- `contract:enter:\d+$`: `bot/handlers/dungeon.py:834`
- `contract:enter:confirm:`: `bot/handlers/dungeon.py:880`
- `contract:pick:`: `bot/handlers/dungeon.py:782`
- `del_item:`: `bot/handlers/admin.py:1678`
- `drinksel:`: `bot/handlers/admin.py:1310`
- `duel:accept:`: `bot/handlers/duel.py:399`
- `duel:atk:`: `bot/handlers/duel.py:529`
- `duel:cancel:`: `bot/handlers/duel.py:373`
- `duel:decline:`: `bot/handlers/duel.py:385`
- `duel:def:`: `bot/handlers/duel.py:545`
- `duel:invite:`: `bot/handlers/duel.py:310`
- `duel:leave:`: `bot/handlers/duel.py:448`
- `dungeon:attack:`: `bot/handlers/dungeon.py:1386`
- `dungeon:continue:`: `bot/handlers/dungeon.py:1187`
- `dungeon:edit:`: `bot/handlers/admin.py:5409`
- `dungeon:enemy:`: `bot/handlers/admin.py:5737`
- `dungeon:escape:`: `bot/handlers/dungeon.py:2002`
- `dungeon:photo_set:`: `bot/handlers/admin.py:5481`
- `dungeon:use_slot:`: `bot/handlers/dungeon.py:1698`
- `eddrop:`: `bot/handlers/admin.py:6330`
- `eddrop_del:`: `bot/handlers/admin.py:6416`
- `eddrop_desc:`: `bot/handlers/admin.py:6488`
- `eddrop_photo:`: `bot/handlers/admin.py:6434`
- `eddrop_set_ch:`: `bot/handlers/admin.py:6371`
- `eddrop_set_q:`: `bot/handlers/admin.py:6394`
- `eddrop_stat:`: `bot/handlers/admin.py:6583`
- `eddrop_stats:`: `bot/handlers/admin.py:6544`
- `eddrop_weff:`: `bot/handlers/admin.py:6646`
- `eddrop_weff_set:`: `bot/handlers/admin.py:6668`
- `edit_item:`: `bot/handlers/admin.py:1796`
- `editem_add:`: `bot/handlers/admin.py:6282`
- `editem_new:`: `bot/handlers/admin.py:6307`
- `editem_pick:`: `bot/handlers/admin.py:6237`
- `editset:drink:`: `bot/handlers/admin.py:1987`
- `editset:weff:`: `bot/handlers/admin.py:1921`
- `enemy:card:`: `bot/handlers/admin.py:9378`
- `enemy:dcard:`: `bot/handlers/admin.py:9305`
- `enemy:del:`: `bot/handlers/admin.py:9504`
- `enemy:dn:\d+$`: `bot/handlers/admin.py:9215`
- `enemy:dropadd:`: `bot/handlers/admin.py:9681`
- `enemy:dropch:`: `bot/handlers/admin.py:9608`
- `enemy:dropdel:`: `bot/handlers/admin.py:9634`
- `enemy:dropedit:`: `bot/handlers/admin.py:9570`
- `enemy:dropitem:`: `bot/handlers/admin.py:9646`
- `enemy:dropq:`: `bot/handlers/admin.py:9621`
- `enemy:drops:`: `bot/handlers/admin.py:9560`
- `enemy:effects:\d+$`: `bot/handlers/admin.py:5999`
- `enemy:fld:`: `bot/handlers/admin.py:9388`
- `enemy:fx:src:`: `bot/handlers/admin.py:6072`
- `enemy:fx:tog:\d+:\d+$`: `bot/handlers/admin.py:6018`
- `enemy:fxt:`: `bot/handlers/admin.py:6092`
- `enemy:list:[a-z]+:[\w-]+$`: `bot/handlers/admin.py:9263`
- `enemy:new:`: `bot/handlers/admin.py:9755`
- `enemy:photo:`: `bot/handlers/admin.py:9448`
- `enemy:tog:`: `bot/handlers/admin.py:9485`
- `enemy_drops:`: `bot/handlers/admin.py:6224`
- `enemy_field:`: `bot/handlers/admin.py:5750`
- `eqequip:[a-z0-9_]+:\d+$`: `bot/handlers/inventory.py:500`
- `eqlock:[a-z0-9_]+$`: `bot/handlers/inventory.py:488`
- `eqpart:`: `bot/handlers/admin.py:1388`
- `eqslot:[a-z0-9_]+$`: `bot/handlers/inventory.py:493`
- `equnequip:[a-z0-9_]+$`: `bot/handlers/inventory.py:532`
- `field:`: `bot/handlers/admin.py:2092`
- `field:required_status`: `bot/handlers/admin.py:1835`
- `field_req:`: `bot/handlers/admin.py:1868`
- `fin:`: `bot/handlers/admin.py:2545`
- `finh:h:`: `bot/handlers/admin.py:2755`
- `finh:list:`: `bot/handlers/admin.py:2731`
- `finh:u:`: `bot/handlers/admin.py:2743`
- `finuser:`: `bot/handlers/admin.py:2616`
- `fireevent:attack:`: `bot/handlers/fire_event.py:694`
- `fireevent:cont:`: `bot/handlers/fire_event.py:275`
- `fireevent:fishing:`: `bot/handlers/fire_event.py:329`
- `fireevent:leave:`: `bot/handlers/fire_event.py:480`
- `fireevent:potion:`: `bot/handlers/fire_event.py:792`
- `fireevent:step:`: `bot/handlers/fire_event.py:188`
- `fish:bait:\d+$`: `bot/handlers/fishing.py:514`
- `fish:bait:set:\d+:[a-z]+$`: `bot/handlers/fishing.py:556`
- `fish:cast:\d+$`: `bot/handlers/fishing.py:566`
- `fish:lake:\d+$`: `bot/handlers/fishing.py:493`
- `fishbuy:`: `bot/handlers/shop.py:807`
- `fishcatch:`: `bot/handlers/inventory.py:1280`
- `fishgo:`: `bot/handlers/inventory.py:1531`
- `fishing:addfish:`: `bot/handlers/admin.py:7074`
- `fishing:addlist:`: `bot/handlers/admin.py:7044`
- `fishing:del:`: `bot/handlers/admin.py:7097`
- `fishing:fish:`: `bot/handlers/admin.py:6964`
- `fishing:junk:`: `bot/handlers/admin.py:6820`
- `fishing:kind:`: `bot/handlers/admin.py:6978`
- `fishing:market:`: `bot/handlers/admin.py:7000`
- `fishing:new:`: `bot/handlers/admin.py:7122`
- `fishing:new_super:`: `bot/handlers/admin.py:7225`
- `fishing:super:`: `bot/handlers/admin.py:7022`
- `fishing:water:`: `bot/handlers/admin.py:6926`
- `fishing_field:`: `bot/handlers/admin.py:7284`
- `fishing_j:`: `bot/handlers/admin.py:6870`
- `fishmarket:`: `bot/handlers/inventory.py:1433`
- `fishoffer:`: `bot/handlers/shop.py:732`
- `fishprice:`: `bot/handlers/inventory.py:1513`
- `fishsell:`: `bot/handlers/inventory.py:1589`
- `fishuse:`: `bot/handlers/inventory.py:1288`
- `forest:add:`: `bot/handlers/admin.py:7825`
- `forest:area:\d+:(glade|clearing)$`: `bot/handlers/forest.py:426`
- `forest:battle:flee:\d+$`: `bot/handlers/forest.py:1070`
- `forest:battle:hit:\d+$`: `bot/handlers/forest.py:863`
- `forest:card:`: `bot/handlers/admin.py:7739`
- `forest:cast:\d+(?::(glade|clearing))?$`: `bot/handlers/forest.py:500`
- `forest:del:`: `bot/handlers/admin.py:7844`
- `forest:kind:`: `bot/handlers/admin.py:7753`
- `forest:market:`: `bot/handlers/admin.py:7778`
- `forest:new_kind:`: `bot/handlers/admin.py:8033`
- `forest:zadd:(glade|clearing):\d+$`: `bot/handlers/admin.py:7605`
- `forest:zaddlist:(glade|clearing)$`: `bot/handlers/admin.py:7578`
- `forest:zchance:(glade|clearing):\d+$`: `bot/handlers/admin.py:7551`
- `forest:zdel:(glade|clearing):\d+$`: `bot/handlers/admin.py:7566`
- `forest:zone:(glade|clearing)$`: `bot/handlers/admin.py:7479`
- `forest:zset:(glade|clearing):(\w+)$`: `bot/handlers/admin.py:7617`
- `forest_field:`: `bot/handlers/admin.py:7865`
- `housing:craft:`: `bot/handlers/housing.py:725`
- `housing:harvest:`: `bot/handlers/housing.py:1053`
- `housing:install:`: `bot/handlers/housing.py:791`
- `housing:install_item:`: `bot/handlers/housing.py:829`
- `housing:kitchen:`: `bot/handlers/housing.py:389`
- `housing:move:`: `bot/handlers/housing.py:1074`
- `housing:mushproc:`: `bot/handlers/housing.py:499`
- `housing:mushrooms:`: `bot/handlers/housing.py:485`
- `housing:plant:`: `bot/handlers/housing.py:1032`
- `housing:recipe:`: `bot/handlers/housing.py:680`
- `housing:room:`: `bot/handlers/housing.py:333`
- `housing:shower:`: `bot/handlers/housing.py:582`
- `housing:uninstall:`: `bot/handlers/housing.py:932`
- `housing:uninstall_confirm:`: `bot/handlers/housing.py:998`
- `hq:farms:`: `bot/handlers/hq.py:484`
- `hq:order:`: `bot/handlers/hq.py:167`
- `hq:pilot:`: `bot/handlers/hq.py:339`
- `hq:roster:`: `bot/handlers/hq.py:285`
- `hq:wing:set:`: `bot/handlers/hq.py:368`
- `hq:wingcmd:assign:`: `bot/handlers/hq.py:632`
- `hq:wingcmd:pick:`: `bot/handlers/hq.py:609`
- `hq:wingcmd:unset:`: `bot/handlers/hq.py:677`
- `hq:wingdel:`: `bot/handlers/hq.py:1231`
- `hq:wingdep:`: `bot/handlers/hq.py:910`
- `hq:wingdrop:`: `bot/handlers/hq.py:826`
- `hq:wingedit:`: `bot/handlers/hq.py:1167`
- `hq:wingfarm:`: `bot/handlers/hq.py:448`
- `hq:wingtake:`: `bot/handlers/hq.py:752`
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
- `itembuy:`: `bot/handlers/shop.py:931`
- `itemgo:`: `bot/handlers/inventory.py:1224`
- `itemmarket:`: `bot/handlers/inventory.py:1134`
- `itemoffer:`: `bot/handlers/shop.py:863`
- `itemprice:`: `bot/handlers/inventory.py:1213`
- `kvp:attack:`: `bot/handlers/kvp.py:514`
- `kvp:attempt:`: `bot/handlers/kvp.py:440`
- `kvp:continue:`: `bot/handlers/kvp.py:410`
- `libadmin_del:`: `bot/handlers/library.py:409`
- `libadmin_sec:`: `bot/handlers/library.py:297`
- `libbook:`: `bot/handlers/library.py:204`
- `libdl:`: `bot/handlers/library.py:249`
- `libsec:[a-z]+$`: `bot/handlers/library.py:178`
- `loc:blocking:`: `bot/handlers/admin.py:8284`
- `loc:building:`: `bot/handlers/admin.py:8173`
- `loc:edit:`: `bot/handlers/admin.py:8147`
- `loc:mode:`: `bot/handlers/admin.py:8213`
- `loc:photo_set:`: `bot/handlers/admin.py:8920`
- `loc:req_status:`: `bot/handlers/admin.py:8249`
- `loc:season:(winter|spring|summer|autumn)$`: `bot/handlers/admin.py:8601`
- `loc:season_clear:(winter|spring|summer|autumn)$`: `bot/handlers/admin.py:8627`
- `loc:season_photo_set:(winter|spring|summer|autumn):(dawn|day|sunset|night)$`: `bot/handlers/admin.py:8957`
- `location:enter:`: `bot/handlers/locations.py:107`
- `location:preview:`: `bot/handlers/locations.py:40`
- `locstat:`: `bot/handlers/admin.py:5064`
- `logsite:battle:flee:\d+$`: `bot/handlers/logging_site.py:1096`
- `logsite:battle:hit:\d+$`: `bot/handlers/logging_site.py:893`
- `logsite:chop:\d+$`: `bot/handlers/logging_site.py:468`
- `logsite:fire:(1|all):\d+$`: `bot/handlers/logging_site.py:742`
- `logsite:menu:\d+$`: `bot/handlers/logging_site.py:453`
- `logsite:mill:\d+$`: `bot/handlers/logging_site.py:616`
- `logsite:plank:(1|all):\d+$`: `bot/handlers/logging_site.py:679`
- `lootonly:`: `bot/handlers/admin.py:1530`
- `marketok:`: `bot/handlers/admin.py:1508`
- `mine:battle:flee:\d+$`: `bot/handlers/mine.py:725`
- `mine:battle:hit:\d+$`: `bot/handlers/mine.py:574`
- `mine:deeper:\d+$`: `bot/handlers/mine.py:391`
- `mine:dig:\d+$`: `bot/handlers/mine.py:402`
- `mine:level:\d+$`: `bot/handlers/mine.py:358`
- `mine:menu:\d+$`: `bot/handlers/mine.py:351`
- `mollusk:flee:\d+$`: `bot/handlers/dungeon.py:507`
- `mollusk:hit:\d+$`: `bot/handlers/dungeon.py:375`
- `mvd:arch:`: `bot/handlers/mvd.py:95`
- `mvd:archive:`: `bot/handlers/mvd.py:45`
- `news:(?:off|(?:dis)?allow:-?\d+|chat:-?\d+:-?\d+|topic:-?\d+:-?\d+)$`: `bot/handlers/admin.py:3045`
- `news:arch:\d+$`: `bot/handlers/news.py:179`
- `news:del:`: `bot/handlers/news.py:473`
- `news:delconf:`: `bot/handlers/news.py:495`
- `news:edit:`: `bot/handlers/news.py:400`
- `news:view:`: `bot/handlers/news.py:196`
- `nii:set:`: `bot/handlers/nii.py:319`
- `nii:view:`: `bot/handlers/nii.py:284`
- `offercancel:fish:`: `bot/handlers/shop.py:977`
- `offercancel:item:`: `bot/handlers/shop.py:982`
- `page`: `bot/handlers/admin.py:411`
- `park:admin:del:`: `bot/handlers/park.py:390`
- `park:admin:delyes:`: `bot/handlers/park.py:408`
- `park:admin:edit:`: `bot/handlers/park.py:474`
- `park:adminedit:f:`: `bot/handlers/park.py:492`
- `park:statue:`: `bot/handlers/park.py:257`
- `pickuser:`: `bot/handlers/admin.py:402`
- `pollarch:day:\d{4}-\d{2}-\d{2}(?::\d+)?$`: `bot/handlers/poll_archive.py:176`
- `pollarch:days:\d+$`: `bot/handlers/poll_archive.py:154`
- `prod:`: `bot/handlers/admin.py:1468`
- `prof_sel_status:`: `bot/handlers/profile.py:327`
- `profile:award:`: `bot/handlers/profile.py:550`
- `rank_pick:`: `bot/handlers/admin.py:4897`
- `rank_promote:`: `bot/handlers/admin.py:4856`
- `rar:`: `bot/handlers/admin.py:1268`
- `rathaus:`: `bot/handlers/pilots.py:174`
- `rathaus_prof:`: `bot/handlers/pilots.py:214`
- `recadm:bookdel:`: `bot/handlers/admin_recipes.py:617`
- `recadm:bookdel_yes:`: `bot/handlers/admin_recipes.py:641`
- `recadm:bookopen:`: `bot/handlers/admin_recipes.py:588`
- `recadm:bookpage:`: `bot/handlers/admin_recipes.py:955`
- `recadm:bookpick:`: `bot/handlers/admin_recipes.py:967`
- `recadm:bookspage:`: `bot/handlers/admin_recipes.py:577`
- `recadm:booktoggle:`: `bot/handlers/admin_recipes.py:599`
- `recadm:cat:`: `bot/handlers/admin_recipes.py:1115`
- `recadm:ed:`: `bot/handlers/admin_recipes.py:1779`
- `recadm:ed_yes:`: `bot/handlers/admin_recipes.py:1802`
- `recadm:ef:`: `bot/handlers/admin_recipes.py:1486`
- `recadm:ei:`: `bot/handlers/admin_recipes.py:1700`
- `recadm:eq:`: `bot/handlers/admin_recipes.py:1658`
- `recadm:er:`: `bot/handlers/admin_recipes.py:1731`
- `recadm:es:`: `bot/handlers/admin_recipes.py:1608`
- `recadm:et:`: `bot/handlers/admin_recipes.py:1760`
- `recadm:exp:`: `bot/handlers/admin_recipes.py:1291`
- `recadm:exv:`: `bot/handlers/admin_recipes.py:1624`
- `recadm:ingcat:`: `bot/handlers/admin_recipes.py:765`
- `recadm:ingpick:`: `bot/handlers/admin_recipes.py:795`
- `recadm:kind:`: `bot/handlers/admin_recipes.py:704`
- `recadm:lvl:`: `bot/handlers/admin_recipes.py:1311`
- `recadm:newrar:`: `bot/handlers/admin_recipes.py:1254`
- `recadm:open:`: `bot/handlers/admin_recipes.py:671`
- `recadm:page:`: `bot/handlers/admin_recipes.py:660`
- `recadm:rar:`: `bot/handlers/admin_recipes.py:1356`
- `recadm:rescat:`: `bot/handlers/admin_recipes.py:913`
- `recadm:respick:`: `bot/handlers/admin_recipes.py:935`
- `recadm:rxv:`: `bot/handlers/admin_recipes.py:1673`
- `rep:nav:`: `bot/handlers/admin.py:4782`
- `rep_fix:`: `bot/handlers/admin.py:4581`
- `rep_no:`: `bot/handlers/admin.py:4767`
- `rep_ok:`: `bot/handlers/admin.py:4698`
- `report:my:`: `bot/handlers/reports.py:390`
- `report:view:`: `bot/handlers/reports.py:402`
- `resv:bait:\d+$`: `bot/handlers/dungeon.py:2122`
- `resv:bait:set:\d+:[a-z]+$`: `bot/handlers/dungeon.py:2170`
- `resv:cast:\d+$`: `bot/handlers/dungeon.py:2189`
- `resv:deeper:\d+$`: `bot/handlers/dungeon.py:2426`
- `resv:enter:\d+$`: `bot/handlers/dungeon.py:2084`
- `resv:eq:\d+$`: `bot/handlers/dungeon.py:2461`
- `resv:eqclear:[a-z0-9_]+:\d+$`: `bot/handlers/dungeon.py:2569`
- `resv:eqset:[a-z0-9_]+:\d+:\d+$`: `bot/handlers/dungeon.py:2545`
- `resv:eqslot:[a-z0-9_]+:\d+$`: `bot/handlers/dungeon.py:2499`
- `resv:menu:\d+$`: `bot/handlers/dungeon.py:2108`
- `role:`: `bot/handlers/admin.py:2958`
- `rolop:`: `bot/handlers/admin.py:2909`
- `shop_del:cat:`: `bot/handlers/admin.py:1772`
- `shop_edit:cat:`: `bot/handlers/admin.py:1757`
- `shopcat:[^:]+$`: `bot/handlers/shop.py:250`
- `shopcat:[^:]+:\d+$`: `bot/handlers/shop.py:338`
- `shopitem:`: `bot/handlers/shop.py:349`
- `st_del:`: `bot/handlers/admin.py:3252`
- `st_key:`: `bot/handlers/admin.py:5193`
- `st_op:`: `bot/handlers/admin.py:5163`
- `st_pick:`: `bot/handlers/admin.py:3534`
- `st_rev:`: `bot/handlers/admin.py:3464`
- `storage:cat:`: `bot/handlers/admin.py:973`
- `storage:item:`: `bot/handlers/admin.py:1004`
- `storage:page:`: `bot/handlers/admin.py:990`
- `storage:purge:`: `bot/handlers/admin.py:1130`
- `storage:restock:`: `bot/handlers/admin.py:1062`
- `toggle:`: `bot/handlers/admin.py:8289`
- `vote:cast:`: `bot/handlers/polls.py:163`
- `vote:close:`: `bot/handlers/polls.py:287`
- `vote:close_confirm:`: `bot/handlers/polls.py:310`
- `vote:results:`: `bot/handlers/polls.py:185`
- `vote:show:`: `bot/handlers/polls.py:109`
- `wall:archpage:\d+$`: `bot/handlers/wall.py:338`
- `wall:archread:\d+(?::\d+)?$`: `bot/handlers/wall.py:357`
- `wall:delete:\d+$`: `bot/handlers/wall.py:224`
- `wall:page:\d+$`: `bot/handlers/wall.py:156`
- `weff:`: `bot/handlers/admin.py:1401`
- `wing_set:`: `bot/handlers/admin.py:821`
- `Испорченный`: `bot/handlers/dungeon.py:1916`
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

