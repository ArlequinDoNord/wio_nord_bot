# Карта FSM-состояний и callback-неймспейсов N.O.R.D.

> **Сгенерировано** `tools/export_states.py`. Не редактировать вручную —
> правь код и перегенерируй: `.venv\Scripts\python.exe tools/export_states.py`.
>
> Назначение: единый обзор всех `StatesGroup`, где они ставятся и где ловятся,
> а также реестр `callback_data` — чтобы не допускать конфликтов меню/хендлеров.

Всего классов состояний: **50**; полей-состояний: **224**; уникальных `callback_data`: **261**.

## 1. Классы состояний по модулям

### `AdminAddItem` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `name` | `bot/handlers/admin.py:1210` `shop_admin_add`<br>`bot/handlers/admin.py:6169` `enemy_drop_new_item` | `bot/handlers/admin.py:1218` `add_item_name` |
| `desc` | `bot/handlers/admin.py:1220` `add_item_name` | `bot/handlers/admin.py:1226` `add_item_desc` |
| `price` | `bot/handlers/admin.py:1229` `add_item_desc` | `bot/handlers/admin.py:1235` `add_item_price` |
| `sell_price` | `bot/handlers/admin.py:1245` `add_item_price` | `bot/handlers/admin.py:1251` `add_item_sell_price` |
| `rarity` | `bot/handlers/admin.py:1263` `add_item_sell_price` | — |
| `category` | `bot/handlers/admin.py:1272` `add_item_rarity` | — |
| `drink` | `bot/handlers/admin.py:1295` `add_item_category` | — |
| `plant_name` | `bot/handlers/admin.py:1284` `add_item_category` | `bot/handlers/admin.py:1320` `add_item_plant_name` |
| `stock` | `bot/handlers/admin.py:1304` `add_item_category`<br>`bot/handlers/admin.py:1314` `add_item_drink_choice`<br>`bot/handlers/admin.py:1323` `add_item_plant_name` | `bot/handlers/admin.py:1329` `add_item_stock` |
| `stats` | `bot/handlers/admin.py:1343` `add_item_stock`<br>`bot/handlers/admin.py:1348` `add_item_stock` | `bot/handlers/admin.py:1356` `add_item_stats`<br>`bot/handlers/admin.py:1396` `add_item_stats_bad` |
| `equip_slot` | `bot/handlers/admin.py:1373` `add_item_stats` | — |
| `weapon_effect` | `bot/handlers/admin.py:1361` `add_item_stats` | — |
| `weapon_effect_chance` | `bot/handlers/admin.py:1409` `add_item_weapon_effect_cb` | `bot/handlers/admin.py:1418` `add_item_weapon_effect_chance` |
| `weapon_effect_dmg` | `bot/handlers/admin.py:1430` `add_item_weapon_effect_chance` | `bot/handlers/admin.py:1442` `add_item_weapon_effect_dmg` |
| `producer` | `bot/handlers/admin.py:1457` `_go_add_item_producer` | — |
| `producer_user` | `bot/handlers/admin.py:1472` `add_item_producer` | `bot/handlers/admin.py:1484` `add_item_producer_user` |
| `market` | `bot/handlers/admin.py:1495` `_go_add_item_market` | — |
| `loot` | `bot/handlers/admin.py:1517` `_go_add_item_loot` | — |
| `status` | `bot/handlers/admin.py:1545` `_go_add_item_status` | — |
| `photo` | `bot/handlers/admin.py:1564` `add_item_status_cb` | `bot/handlers/admin.py:1572` `add_item_photo` |

### `AdminSaleTax` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `percent` | `bot/handlers/admin.py:2454` `admin_saletax_view` | `bot/handlers/admin.py:2468` `admin_saletax_set` |

### `AdminSpecialCode` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `code` | `bot/handlers/admin.py:2496` `admin_special_code_view` | `bot/handlers/admin.py:2511` `admin_special_code_set` |

### `AdminEditItem` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `item_id` | — | — |
| `field` | `bot/handlers/admin.py:1800` `edit_item_pick` | — |
| `value` | `bot/handlers/admin.py:2104` `edit_item_field` | `bot/handlers/admin.py:2115` `edit_item_value` |
| `photo` | `bot/handlers/admin.py:1889` `edit_item_field_photo` | `bot/handlers/admin.py:1939` `edit_item_photo` |

### `AdminFinance` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | `bot/handlers/admin.py:2534` `finance_manual`<br>`bot/handlers/admin.py:2551` `finance_pick` | `bot/handlers/admin.py:2612` `finance_target` |
| `currency` | — | — |
| `amount` | `bot/handlers/admin.py:456` `pickuser_cb`<br>`bot/handlers/admin.py:2581` `finance_pick_user`<br>`bot/handlers/admin.py:2619` `finance_target` | `bot/handlers/admin.py:2627` `finance_amount` |

### `AdminTreasury` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `amount` | `bot/handlers/admin.py:2361` `treasury_give` | `bot/handlers/admin.py:2371` `treasury_amount` |
| `target` | `bot/handlers/admin.py:2387` `treasury_amount` | `bot/handlers/admin.py:2393` `treasury_target_manual` |

### `AdminStorageRestock` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `amount` | `bot/handlers/admin.py:1072` `storage_restock` | `bot/handlers/admin.py:1086` `storage_restock_amount` |

### `AdminStorageDelete` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `confirm` | `bot/handlers/admin.py:1144` `storage_purge` | `bot/handlers/admin.py:1158` `storage_purge_confirm` |

### `AdminTax` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `percent` | `bot/handlers/admin.py:2417` `admin_tax_view` | `bot/handlers/admin.py:2429` `admin_tax_set` |

### `AdminReportAutoApprove` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `value` | `bot/handlers/admin.py:4176` `report_auto_approve_edit_cb` | `bot/handlers/admin.py:4189` `report_auto_approve_edit_value` |

### `AdminReportPayCap` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `value` | `bot/handlers/admin.py:4215` `report_pay_cap_edit_cb` | `bot/handlers/admin.py:4230` `report_pay_cap_edit_value` |

### `AdminReportFix` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `daily` | `bot/handlers/admin.py:4416` `report_fix_start` | `bot/handlers/admin.py:4429` `report_fix_daily` |
| `total` | `bot/handlers/admin.py:4443` `report_fix_daily` | `bot/handlers/admin.py:4457` `report_fix_total` |

### `AdminRoles` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | `bot/handlers/admin.py:2700` `admin_roles` | `bot/handlers/admin.py:2709` `roles_target` |
| `action` | `bot/handlers/admin.py:459` `pickuser_cb`<br>`bot/handlers/admin.py:2715` `roles_target` | — |
| `role` | `bot/handlers/admin.py:2733` `roles_action` | — |

### `AdminStatuses` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `name` | `bot/handlers/admin.py:2984` `status_create_start` | `bot/handlers/admin.py:2992` `status_create_name` |
| `tag` | `bot/handlers/admin.py:2994` `status_create_name` | `bot/handlers/admin.py:3003` `status_create_tag` |
| `level` | `bot/handlers/admin.py:3010` `status_create_tag` | `bot/handlers/admin.py:3020` `status_create_level` |
| `desc` | `bot/handlers/admin.py:3031` `status_create_level` | `bot/handlers/admin.py:3036` `status_create_desc` |
| `target` | `bot/handlers/admin.py:3257` `status_grant_target`<br>`bot/handlers/admin.py:3326` `status_revoke_target` | `bot/handlers/admin.py:3267` `status_grant_target_msg` |
| `grant_action` | — | — |
| `status_pick` | `bot/handlers/admin.py:474` `pickuser_cb`<br>`bot/handlers/admin.py:483` `pickuser_cb`<br>`bot/handlers/admin.py:3278` `status_grant_target_msg`<br>`bot/handlers/admin.py:3410` `status_grant_more` | — |
| `item_pick` | — | — |
| `item_status` | — | — |

### `AdminAwards` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `name` | `bot/handlers/admin.py:3499` `award_create_start` | `bot/handlers/admin.py:3556` `award_create_name` |
| `desc` | `bot/handlers/admin.py:3562` `award_create_name` | `bot/handlers/admin.py:3570` `award_create_desc` |
| `emoji` | `bot/handlers/admin.py:3573` `award_create_desc` | `bot/handlers/admin.py:3581` `award_create_emoji` |
| `bonus` | `bot/handlers/admin.py:3547` `_award_ask_bonus` | `bot/handlers/admin.py:3589` `award_create_bonus` |
| `preview` | `bot/handlers/admin.py:3535` `_award_ask_bonus` | — |
| `target` | `bot/handlers/admin.py:3975` `award_grant_target` | `bot/handlers/admin.py:3981` `award_grant_target_msg` |
| `award_pick` | `bot/handlers/admin.py:4056` `award_revoke_pick_user` | — |
| `comment` | `bot/handlers/admin.py:3999` `award_grant_pick` | `bot/handlers/admin.py:4016` `award_grant_comment` |
| `edit_value` | `bot/handlers/admin.py:3855` `award_edit_field_pick` | `bot/handlers/admin.py:3879` `award_edit_value` |

### `AdminFishing` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `water` | — | — |
| `wf_id` | — | — |
| `value` | `bot/handlers/admin.py:6730` `admin_fishing_junk_field_pick`<br>`bot/handlers/admin.py:7144` `admin_fishing_field_pick` | `bot/handlers/admin.py:7171` `admin_fishing_value` |
| `c_name` | `bot/handlers/admin.py:6981` `admin_fishing_new` | `bot/handlers/admin.py:6990` `admin_fishing_new_name` |
| `c_desc` | `bot/handlers/admin.py:7000` `admin_fishing_new_name` | `bot/handlers/admin.py:7006` `admin_fishing_new_desc` |
| `c_sell_price` | `bot/handlers/admin.py:7009` `admin_fishing_new_desc` | `bot/handlers/admin.py:7015` `admin_fishing_new_sell_price` |
| `c_day_weight` | `bot/handlers/admin.py:7023` `admin_fishing_new_sell_price` | `bot/handlers/admin.py:7031` `admin_fishing_new_day_weight` |
| `c_night_weight` | `bot/handlers/admin.py:7039` `admin_fishing_new_day_weight` | `bot/handlers/admin.py:7047` `admin_fishing_new_night_weight` |
| `c_photo` | `bot/handlers/admin.py:7079` `admin_fishing_new_super` | `bot/handlers/admin.py:7087` `admin_fishing_new_photo` |
| `c_super_rare` | `bot/handlers/admin.py:7055` `admin_fishing_new_night_weight` | — |

### `AdminForest` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `f_id` | — | — |
| `field` | — | — |
| `value` | `bot/handlers/admin.py:7726` `admin_forest_field_pick` | `bot/handlers/admin.py:7752` `admin_forest_value` |
| `c_name` | `bot/handlers/admin.py:7808` `admin_forest_new` | `bot/handlers/admin.py:7817` `admin_forest_new_name` |
| `c_desc` | `bot/handlers/admin.py:7827` `admin_forest_new_name` | `bot/handlers/admin.py:7833` `admin_forest_new_desc` |
| `c_sell_price` | `bot/handlers/admin.py:7836` `admin_forest_new_desc` | `bot/handlers/admin.py:7842` `admin_forest_new_sell_price` |
| `c_chance` | `bot/handlers/admin.py:7849` `admin_forest_new_sell_price` | `bot/handlers/admin.py:7858` `admin_forest_new_chance` |
| `c_kind` | `bot/handlers/admin.py:7866` `admin_forest_new_chance` | — |
| `c_photo` | `bot/handlers/admin.py:7889` `admin_forest_new_kind` | `bot/handlers/admin.py:7897` `admin_forest_new_photo` |
| `zone_value` | `bot/handlers/admin.py:7406` `admin_forest_zone_chance`<br>`bot/handlers/admin.py:7481` `admin_forest_zone_set_pick`<br>`bot/handlers/admin.py:7494` `admin_forest_limit_set` | `bot/handlers/admin.py:7501` `admin_forest_zone_value` |

### `AdminEnemy` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `field` | `bot/handlers/admin.py:9246` `admin_enemies_field_pick` | `bot/handlers/admin.py:9252` `admin_enemies_field_value` |
| `photo` | `bot/handlers/admin.py:9303` `admin_enemies_photo_pick` | `bot/handlers/admin.py:9309` `admin_enemies_photo_value` |
| `onhit_value` | `bot/handlers/admin.py:5966` `source_enemy_effect_toggle` | `bot/handlers/admin.py:5972` `source_enemy_onhit_value` |
| `drop_chance` | `bot/handlers/admin.py:9463` `admin_enemies_drop_edit_chance`<br>`bot/handlers/admin.py:9537` `admin_enemies_drop_add_pick` | `bot/handlers/admin.py:9543` `admin_enemies_drop_chance_value` |
| `drop_qty` | `bot/handlers/admin.py:9476` `admin_enemies_drop_edit_qty`<br>`bot/handlers/admin.py:9564` `admin_enemies_drop_chance_value` | `bot/handlers/admin.py:9570` `admin_enemies_drop_qty_value` |
| `c_name` | `bot/handlers/admin.py:9609` `admin_enemies_new` | `bot/handlers/admin.py:9614` `admin_enemies_new_name` |
| `c_hp` | `bot/handlers/admin.py:9620` `admin_enemies_new_name` | `bot/handlers/admin.py:9625` `admin_enemies_new_hp` |
| `c_dmg` | `bot/handlers/admin.py:9631` `admin_enemies_new_hp` | `bot/handlers/admin.py:9636` `admin_enemies_new_dmg` |
| `c_dodge` | `bot/handlers/admin.py:9649` `admin_enemies_new_dmg` | `bot/handlers/admin.py:9654` `admin_enemies_new_dodge` |
| `c_chance` | `bot/handlers/admin.py:9660` `admin_enemies_new_dodge` | `bot/handlers/admin.py:9666` `admin_enemies_new_chance` |
| `c_loss_ap` | `bot/handlers/admin.py:9672` `admin_enemies_new_chance` | `bot/handlers/admin.py:9678` `admin_enemies_new_done` |

### `AdminCallsign` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | `bot/handlers/admin.py:757` `admin_callsign_start` | `bot/handlers/admin.py:778` `admin_callsign_target_msg` |
| `value` | `bot/handlers/admin.py:541` `pickuser_cb`<br>`bot/handlers/admin.py:788` `admin_callsign_target_msg` | `bot/handlers/admin.py:799` `admin_callsign_value_msg` |

### `AdminWing` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | `bot/handlers/admin.py:770` `admin_wing_start` | — |
| `value` | `bot/handlers/admin.py:552` `pickuser_cb` | — |

### `AdminStates` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | `bot/handlers/admin.py:4952` `admin_states_menu` | `bot/handlers/admin.py:4961` `admin_states_target_text` |
| `action` | `bot/handlers/admin.py:513` `pickuser_cb`<br>`bot/handlers/admin.py:4967` `admin_states_target_text` | — |
| `state_key` | `bot/handlers/admin.py:4993` `admin_states_op` | — |
| `minutes` | `bot/handlers/admin.py:5018` `admin_states_key` | `bot/handlers/admin.py:5027` `admin_states_minutes`<br>`bot/handlers/admin.py:5048` `admin_states_minutes_bad` |

### `AdminPlayerLog` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | `bot/handlers/admin.py:743` `admin_player_log_start` | `bot/handlers/admin.py:613` `admin_player_log_manual_msg` |

### `AdminSalary` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | — | — |
| `amount` | `bot/handlers/admin.py:526` `pickuser_cb` | `bot/handlers/admin.py:5129` `admin_salary_amount` |
| `period` | `bot/handlers/admin.py:5157` `admin_salary_amount` | `bot/handlers/admin.py:5169` `admin_salary_period_cb`<br>`bot/handlers/admin.py:5188` `admin_salary_period_text` |

### `AdminLocation` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `action` | — | — |
| `target_id` | — | — |
| `key` | `bot/handlers/admin.py:7952` `loc_create` | `bot/handlers/admin.py:8216` `loc_step_key` |
| `name` | `bot/handlers/admin.py:8222` `loc_step_key` | `bot/handlers/admin.py:8227` `loc_step_name` |
| `set_name` | `bot/handlers/admin.py:8243` `loc_set_name` | `bot/handlers/admin.py:8254` `loc_step_set_name` |
| `description` | `bot/handlers/admin.py:8229` `loc_step_name`<br>`bot/handlers/admin.py:8268` `loc_step_set_name`<br>`bot/handlers/admin.py:8282` `loc_set_desc` | `bot/handlers/admin.py:8489` `loc_step_desc` |
| `mode` | `bot/handlers/admin.py:8048` `loc_set_mode`<br>`bot/handlers/admin.py:8500` `loc_step_desc` | `bot/handlers/admin.py:8061` `loc_mode_chosen` |
| `req_status` | `bot/handlers/admin.py:8074` `loc_mode_chosen`<br>`bot/handlers/admin.py:8083` `loc_mode_chosen`<br>`bot/handlers/admin.py:8092` `loc_set_status` | `bot/handlers/admin.py:8097` `loc_req_status_chosen` |
| `blocking` | `bot/handlers/admin.py:8080` `loc_mode_chosen`<br>`bot/handlers/admin.py:8111` `loc_req_status_chosen`<br>`bot/handlers/admin.py:8127` `loc_set_blocking` | `bot/handlers/admin.py:8132` `loc_blocking_chosen` |
| `preview` | `bot/handlers/admin.py:8526` `loc_glade_set`<br>`bot/handlers/admin.py:8576` `loc_clearing_set`<br>`bot/handlers/admin.py:8628` `loc_logging_set`<br>`bot/handlers/admin.py:8679` `loc_mine_set`<br>`bot/handlers/admin.py:8730` `loc_storage_set`<br>`bot/handlers/admin.py:8779` `loc_photo_set`<br>`bot/handlers/admin.py:8817` `loc_season_photo_set` | `bot/handlers/admin.py:8859` `loc_step_photo` |

### `AdminDungeon` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target_id` | — | — |
| `photo_tod` | `bot/handlers/admin.py:5338` `dungeon_photo_set` | `bot/handlers/admin.py:5374` `dungeon_step_photo` |
| `enemy_id` | — | — |
| `enemy_field` | — | — |
| `enemy_value` | `bot/handlers/admin.py:5610` `dungeon_enemy_field_pick` | `bot/handlers/admin.py:5636` `dungeon_enemy_value` |
| `onhit_value` | `bot/handlers/admin.py:5890` `dungeon_enemy_effect_toggle` | `bot/handlers/admin.py:5896` `dungeon_enemy_onhit_value` |
| `drop_chance` | `bot/handlers/admin.py:1616` `add_item_photo`<br>`bot/handlers/admin.py:6146` `enemy_drop_pick_item`<br>`bot/handlers/admin.py:6229` `enemy_drop_set_chance` | `bot/handlers/admin.py:6551` `enemy_drop_chance_value` |
| `drop_qty` | `bot/handlers/admin.py:6252` `enemy_drop_set_qty`<br>`bot/handlers/admin.py:6560` `enemy_drop_chance_value` | `bot/handlers/admin.py:6566` `enemy_drop_qty_value` |
| `drop_item_photo` | `bot/handlers/admin.py:6297` `enemy_drop_item_photo` | `bot/handlers/admin.py:6306` `enemy_drop_item_photo_value` |
| `drop_item_desc` | `bot/handlers/admin.py:6351` `enemy_drop_item_desc` | `bot/handlers/admin.py:6360` `enemy_drop_item_desc_value` |
| `drop_item_field` | — | — |
| `drop_item_value` | `bot/handlers/admin.py:6449` `enemy_drop_item_stat_pick` | `bot/handlers/admin.py:6460` `enemy_drop_item_stat_value` |
| `pending_enemy_id` | — | — |

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
| `wait_building_photo` | `bot/handlers/clan_hall.py:1916` `clan_hall_admphoto_cb` | `bot/handlers/clan_hall.py:1952` `clan_hall_admphoto_save` |
| `wait_construction_photo` | `bot/handlers/clan_hall.py:1945` `clan_hall_admconstphoto_cb` | `bot/handlers/clan_hall.py:1970` `clan_hall_admconstphoto_save` |

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
| `in_dungeon` | `bot/handlers/dungeon.py:934` `contract_enter_confirm`<br>`bot/handlers/dungeon.py:1013` `post_captain_menu`<br>`bot/handlers/dungeon.py:2446` `resv_deeper` | — |
| `in_combat` | — | — |
| `in_boss` | `bot/handlers/dungeon.py:2078` `show_boss` | — |
| `confirm_enter` | `bot/handlers/dungeon.py:863` `contract_enter` | — |
| `in_reservoir` | `bot/handlers/dungeon.py:2100` `resv_enter`<br>`bot/handlers/dungeon.py:2115` `resv_menu`<br>`bot/handlers/dungeon.py:2182` `resv_bait_set` | — |

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
| `bank:` | 2 | `bank:menu`, `bank:transfer_manual` |
| `booklet:` | 1 | `booklet:claim` |
| `cancel:` | 1 | `cancel` |
| `city:` | 5 | `city:clans`, `city:menu`, `city:pilots`, `city:pilots:list`, `city:vote` |
| `clanh:` | 1 | `clanh:noop` |
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

- `admin:awards`: `bot/handlers/admin.py:3416`
- `admin:callsign`: `bot/handlers/admin.py:751`
- `admin:del_photo`: `bot/handlers/admin.py:725`
- `admin:dungeons`: `bot/handlers/admin.py:5236`
- `admin:enemies`: `bot/handlers/admin.py:9052`
- `admin:finance`: `bot/handlers/admin.py:2183`
- `admin:fishing`: `bot/handlers/admin.py:6754`
- `admin:forest`: `bot/handlers/admin.py:7316`
- `admin:locations`: `bot/handlers/admin.py:5212`
- `admin:logs`: `bot/handlers/admin.py:4748`
- `admin:menu`: `bot/handlers/admin.py:715`
- `admin:player_log`: `bot/handlers/admin.py:737`
- `admin:ranks`: `bot/handlers/admin.py:4638`
- `admin:reports`: `bot/handlers/admin.py:4073`
- `admin:reports_done`: `bot/handlers/admin.py:4125`
- `admin:reports_pending`: `bot/handlers/admin.py:4082`
- `admin:roles`: `bot/handlers/admin.py:2690`
- `admin:salaries`: `bot/handlers/admin.py:5052`
- `admin:saletax`: `bot/handlers/admin.py:2447`
- `admin:shop`: `bot/handlers/admin.py:866`
- `admin:states`: `bot/handlers/admin.py:4946`
- `admin:statuses`: `bot/handlers/admin.py:2924`
- `admin:storage`: `bot/handlers/admin.py:940`
- `admin:tax`: `bot/handlers/admin.py:2410`
- `admin:treasury`: `bot/handlers/admin.py:2223`
- `admin:wing`: `bot/handlers/admin.py:764`
- `aw:ach`: `bot/handlers/admin.py:3474`
- `aw:create`: `bot/handlers/admin.py:3492`
- `aw:delete`: `bot/handlers/admin.py:3633`
- `aw:edit`: `bot/handlers/admin.py:3814`
- `aw:grant`: `bot/handlers/admin.py:3972`
- `aw:list`: `bot/handlers/admin.py:3453`
- `aw:revoke`: `bot/handlers/admin.py:4053`
- `aw_comment:skip`: `bot/handlers/admin.py:4010`
- `aw_confirm`: `bot/handlers/admin.py:3609`
- `back:main`: `bot/handlers/admin.py:4921`
- `bank:balance`: `bot/handlers/bank.py:72`
- `bank:menu`: `bot/handlers/bank.py:191`
- `bank:transfer`: `bot/handlers/bank.py:131`
- `bank:transfer_manual`: `bot/handlers/bank.py:147`
- `bank:treasury`: `bot/handlers/bank.py:204`
- `booklet:claim`: `bot/handlers/tourist_booklet.py:71`
- `booklet:menu`: `bot/handlers/tourist_booklet.py:65`
- `cancel`: `bot/handlers/admin.py:4929`
- `city:business`: `bot/handlers/locations.py:243`
- `city:clans`: `bot/handlers/clans.py:91`
- `city:countryside`: `bot/handlers/locations.py:263`
- `city:dungeon`: `bot/handlers/dungeon.py:939`
- `city:library`: `bot/handlers/library.py:82`
- `city:menu`: `bot/handlers/start.py:158`
- `city:pilots`: `bot/handlers/pilots.py:102`
- `city:pilots:list`: `bot/handlers/pilots.py:129`
- `city:quarter`: `bot/handlers/locations.py:225`
- `city:vote`: `bot/handlers/polls.py:70`
- `clanh:noop`: `bot/handlers/clan_hall.py:2133`
- `clans:create_skip`: `bot/handlers/clans.py:790`
- `clans:noop`: `bot/handlers/clans.py:575`
- `clanshopadm:menu`: `bot/handlers/admin_shop_clan.py:103`
- `contracts:list`: `bot/handlers/dungeon.py:751`
- `del_item:back`: `bot/handlers/admin.py:1692`
- `duel:card:buy`: `bot/handlers/duel.py:246`
- `duel:help`: `bot/handlers/duel.py:224`
- `duel:list`: `bot/handlers/duel.py:272`
- `duel:menu`: `bot/handlers/duel.py:218`
- `duel:top`: `bot/handlers/duel.py:292`
- `dungeon:enemies`: `bot/handlers/admin.py:5552`
- `dungeon:exit`: `bot/handlers/dungeon.py:2589`
- `dungeon:exit:cancel`: `bot/handlers/dungeon.py:2674`
- `dungeon:exit:confirm`: `bot/handlers/dungeon.py:2636`
- `dungeon:photos`: `bot/handlers/admin.py:5319`
- `dungeon:photos:clear`: `bot/handlers/admin.py:5363`
- `enemy:fi`: `bot/handlers/admin.py:9090`
- `field:drink`: `bot/handlers/admin.py:1963`
- `field:loot_only`: `bot/handlers/admin.py:2027`
- `field:market_ok`: `bot/handlers/admin.py:2007`
- `field:photo`: `bot/handlers/admin.py:1884`
- `field:weapon_effect`: `bot/handlers/admin.py:1904`
- `fin:manual`: `bot/handlers/admin.py:2531`
- `fish:recover`: `bot/handlers/fishing.py:500`
- `forest:addlist`: `bot/handlers/admin.py:7647`
- `forest:new`: `bot/handlers/admin.py:7800`
- `forest:zset:sold_daily_limit`: `bot/handlers/admin.py:7486`
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
- `loc:building_pick`: `bot/handlers/admin.py:7978`
- `loc:clearing_clear`: `bot/handlers/admin.py:8600`
- `loc:clearing_set`: `bot/handlers/admin.py:8563`
- `loc:create`: `bot/handlers/admin.py:7946`
- `loc:edit_pick`: `bot/handlers/admin.py:7962`
- `loc:glade_clear`: `bot/handlers/admin.py:8550`
- `loc:glade_set`: `bot/handlers/admin.py:8512`
- `loc:logging_clear`: `bot/handlers/admin.py:8652`
- `loc:logging_set`: `bot/handlers/admin.py:8613`
- `loc:mine_clear`: `bot/handlers/admin.py:8703`
- `loc:mine_set`: `bot/handlers/admin.py:8665`
- `loc:photos`: `bot/handlers/admin.py:8438`
- `loc:photos:clear`: `bot/handlers/admin.py:8845`
- `loc:photos:clear_seasons`: `bot/handlers/admin.py:8461`
- `loc:set_blocking`: `bot/handlers/admin.py:8115`
- `loc:set_desc`: `bot/handlers/admin.py:8272`
- `loc:set_mode`: `bot/handlers/admin.py:8044`
- `loc:set_name`: `bot/handlers/admin.py:8233`
- `loc:set_status`: `bot/handlers/admin.py:8087`
- `loc:storage_clear`: `bot/handlers/admin.py:8754`
- `loc:storage_set`: `bot/handlers/admin.py:8716`
- `logsite:back`: `bot/handlers/logging_site.py:455`
- `logsite:enter`: `bot/handlers/logging_site.py:393`
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
- `noop`: `bot/handlers/admin.py:4916`; `bot/handlers/bank.py:453`
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
- `rep:auto_approve_edit`: `bot/handlers/admin.py:4169`
- `rep:next`: `bot/handlers/admin.py:4611`
- `rep:pay_cap_edit`: `bot/handlers/admin.py:4208`
- `rep:speech`: `bot/handlers/representative.py:77`
- `rep:speech:delete`: `bot/handlers/representative.py:109`
- `rep:speech:write`: `bot/handlers/representative.py:89`
- `report:menu`: `bot/handlers/reports.py:47`
- `report:my_reports`: `bot/handlers/reports.py:395`
- `report:submit`: `bot/handlers/reports.py:57`
- `resv:recover`: `bot/handlers/dungeon.py:2392`
- `salary:choose`: `bot/handlers/admin.py:5091`
- `salary:pay`: `bot/handlers/admin.py:5103`
- `shop:catalog`: `bot/handlers/shop.py:230`
- `shop_admin:add`: `bot/handlers/admin.py:1203`
- `shop_admin:delete`: `bot/handlers/admin.py:1663`
- `shop_admin:edit`: `bot/handlers/admin.py:1786`
- `shop_admin:special_code`: `bot/handlers/admin.py:2488`
- `shop_del:cats`: `bot/handlers/admin.py:1780`
- `shop_edit:cats`: `bot/handlers/admin.py:1765`
- `st:create`: `bot/handlers/admin.py:2978`
- `st:delete`: `bot/handlers/admin.py:3051`
- `st:grant`: `bot/handlers/admin.py:3251`
- `st:legioner`: `bot/handlers/admin.py:3196`
- `st:list`: `bot/handlers/admin.py:2961`
- `st:more`: `bot/handlers/admin.py:3397`
- `st:revoke`: `bot/handlers/admin.py:3317`
- `storage:cats`: `bot/handlers/admin.py:959`
- `storage:create`: `bot/handlers/admin.py:1204`
- `storage:menu`: `bot/handlers/storage.py:89`
- `storage:noop`: `bot/handlers/admin.py:954`
- `treasury:debts`: `bot/handlers/admin.py:2256`
- `treasury:give`: `bot/handlers/admin.py:2355`
- `treasury:stats`: `bot/handlers/admin.py:2303`
- `vote:close_cancel`: `bot/handlers/polls.py:332`
- `vote:create`: `bot/handlers/polls.py:224`
- `wall:archive`: `bot/handlers/wall.py:315`
- `wall:view`: `bot/handlers/wall.py:149`
- `wall:write`: `bot/handlers/wall.py:170`

### По префиксу (`F.data.startswith("...")`)

- `\d+$`: `bot/handlers/admin.py:1355`; `bot/handlers/admin.py:5026`; `bot/handlers/admin.py:7500`; `bot/handlers/reports.py:201`
- `\d{1,7}$`: `bot/handlers/reports.py:135`; `bot/handlers/reports.py:165`
- `act:`: `bot/handlers/admin.py:4823`
- `addreq:`: `bot/handlers/admin.py:1554`
- `aw_del:`: `bot/handlers/admin.py:3654`
- `aw_edit:`: `bot/handlers/admin.py:3834`
- `aw_ei:`: `bot/handlers/admin.py:3845`
- `aw_kind:`: `bot/handlers/admin.py:3943`
- `aw_pick:`: `bot/handlers/admin.py:3994`
- `awr_grant:`: `bot/handlers/admin.py:4061`
- `bait:set:`: `bot/handlers/fishing.py:176`
- `bank:history`: `bot/handlers/bank.py:403`
- `bank:pickrecipient:`: `bot/handlers/bank.py:177`
- `bank:transfer:list:`: `bot/handlers/bank.py:137`
- `buy5_nord:`: `bot/handlers/shop.py:493`
- `buy_housing:`: `bot/handlers/shop.py:1093`
- `buy_housing_cancel:`: `bot/handlers/shop.py:1084`
- `buy_nord:`: `bot/handlers/shop.py:483`
- `cat:`: `bot/handlers/admin.py:1276`
- `city/`: `bot/handlers/locations.py:87`
- `city:pilots:list:`: `bot/handlers/pilots.py:135`
- `clanh:admconstphoto:`: `bot/handlers/clan_hall.py:1937`
- `clanh:admnophoto:`: `bot/handlers/clan_hall.py:1923`
- `clanh:admphoto:`: `bot/handlers/clan_hall.py:1905`
- `clanh:bitem:`: `bot/handlers/clan_hall.py:1012`
- `clanh:buy:`: `bot/handlers/clan_hall.py:1055`
- `clanh:cancel:`: `bot/handlers/clan_hall.py:1771`
- `clanh:choose:`: `bot/handlers/clan_hall.py:1740`
- `clanh:craft:`: `bot/handlers/clan_hall.py:1366`
- `clanh:donate:`: `bot/handlers/clan_hall.py:2003`
- `clanh:expchoose:`: `bot/handlers/clan_hall.py:1233`
- `clanh:expinstall:`: `bot/handlers/clan_hall.py:1246`
- `clanh:expmanage:`: `bot/handlers/clan_hall.py:1222`
- `clanh:expup:`: `bot/handlers/clan_hall.py:1264`
- `clanh:give:`: `bot/handlers/clan_hall.py:2060`
- `clanh:hall:`: `bot/handlers/clan_hall.py:1720`
- `clanh:harvest:`: `bot/handlers/clan_hall.py:1657`
- `clanh:harvestall:`: `bot/handlers/clan_hall.py:1689`
- `clanh:inside:`: `bot/handlers/clan_hall.py:1847`
- `clanh:item:`: `bot/handlers/clan_hall.py:2029`
- `clanh:libgive:`: `bot/handlers/clan_hall.py:1114`
- `clanh:log:`: `bot/handlers/clan_hall.py:2118`
- `clanh:mushproc:`: `bot/handlers/clan_hall.py:1514`
- `clanh:mushrooms:`: `bot/handlers/clan_hall.py:1497`
- `clanh:plant:`: `bot/handlers/clan_hall.py:1633`
- `clanh:plantlist:`: `bot/handlers/clan_hall.py:1585`
- `clanh:recipe:`: `bot/handlers/clan_hall.py:1297`
- `clanh:shower:`: `bot/handlers/clan_hall.py:1549`
- `clanh:start:`: `bot/handlers/clan_hall.py:1785`
- `clanh:startfull:`: `bot/handlers/clan_hall.py:1814`
- `clanh:storage:`: `bot/handlers/clan_hall.py:1982`
- `clanh:upgrade:`: `bot/handlers/clan_hall.py:1756`
- `clanh:use:`: `bot/handlers/clan_hall.py:1280`
- `clanhier:`: `bot/handlers/clans.py:285`
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
- `confirm_del_photo:`: `bot/handlers/admin.py:845`
- `contract:enter:\d+$`: `bot/handlers/dungeon.py:831`
- `contract:enter:confirm:`: `bot/handlers/dungeon.py:877`
- `contract:pick:`: `bot/handlers/dungeon.py:779`
- `del_item:`: `bot/handlers/admin.py:1677`
- `drinksel:`: `bot/handlers/admin.py:1309`
- `duel:accept:`: `bot/handlers/duel.py:399`
- `duel:atk:`: `bot/handlers/duel.py:529`
- `duel:cancel:`: `bot/handlers/duel.py:373`
- `duel:decline:`: `bot/handlers/duel.py:385`
- `duel:def:`: `bot/handlers/duel.py:545`
- `duel:invite:`: `bot/handlers/duel.py:310`
- `duel:leave:`: `bot/handlers/duel.py:448`
- `dungeon:attack:`: `bot/handlers/dungeon.py:1383`
- `dungeon:continue:`: `bot/handlers/dungeon.py:1184`
- `dungeon:edit:`: `bot/handlers/admin.py:5256`
- `dungeon:enemy:`: `bot/handlers/admin.py:5584`
- `dungeon:escape:`: `bot/handlers/dungeon.py:1999`
- `dungeon:photo_set:`: `bot/handlers/admin.py:5328`
- `dungeon:use_slot:`: `bot/handlers/dungeon.py:1695`
- `eddrop:`: `bot/handlers/admin.py:6177`
- `eddrop_del:`: `bot/handlers/admin.py:6263`
- `eddrop_desc:`: `bot/handlers/admin.py:6335`
- `eddrop_photo:`: `bot/handlers/admin.py:6281`
- `eddrop_set_ch:`: `bot/handlers/admin.py:6218`
- `eddrop_set_q:`: `bot/handlers/admin.py:6241`
- `eddrop_stat:`: `bot/handlers/admin.py:6430`
- `eddrop_stats:`: `bot/handlers/admin.py:6391`
- `eddrop_weff:`: `bot/handlers/admin.py:6493`
- `eddrop_weff_set:`: `bot/handlers/admin.py:6515`
- `edit_item:`: `bot/handlers/admin.py:1795`
- `editem_add:`: `bot/handlers/admin.py:6129`
- `editem_new:`: `bot/handlers/admin.py:6154`
- `editem_pick:`: `bot/handlers/admin.py:6084`
- `editset:drink:`: `bot/handlers/admin.py:1986`
- `editset:weff:`: `bot/handlers/admin.py:1920`
- `enemy:card:`: `bot/handlers/admin.py:9225`
- `enemy:dcard:`: `bot/handlers/admin.py:9152`
- `enemy:del:`: `bot/handlers/admin.py:9351`
- `enemy:dn:\d+$`: `bot/handlers/admin.py:9062`
- `enemy:dropadd:`: `bot/handlers/admin.py:9528`
- `enemy:dropch:`: `bot/handlers/admin.py:9455`
- `enemy:dropdel:`: `bot/handlers/admin.py:9481`
- `enemy:dropedit:`: `bot/handlers/admin.py:9417`
- `enemy:dropitem:`: `bot/handlers/admin.py:9493`
- `enemy:dropq:`: `bot/handlers/admin.py:9468`
- `enemy:drops:`: `bot/handlers/admin.py:9407`
- `enemy:effects:\d+$`: `bot/handlers/admin.py:5846`
- `enemy:fld:`: `bot/handlers/admin.py:9235`
- `enemy:fx:src:`: `bot/handlers/admin.py:5919`
- `enemy:fx:tog:\d+:\d+$`: `bot/handlers/admin.py:5865`
- `enemy:fxt:`: `bot/handlers/admin.py:5939`
- `enemy:list:[a-z]+:[\w-]+$`: `bot/handlers/admin.py:9110`
- `enemy:new:`: `bot/handlers/admin.py:9602`
- `enemy:photo:`: `bot/handlers/admin.py:9295`
- `enemy:tog:`: `bot/handlers/admin.py:9332`
- `enemy_drops:`: `bot/handlers/admin.py:6071`
- `enemy_field:`: `bot/handlers/admin.py:5597`
- `eqequip:[a-z0-9_]+:\d+$`: `bot/handlers/inventory.py:500`
- `eqlock:[a-z0-9_]+$`: `bot/handlers/inventory.py:488`
- `eqpart:`: `bot/handlers/admin.py:1387`
- `eqslot:[a-z0-9_]+$`: `bot/handlers/inventory.py:493`
- `equnequip:[a-z0-9_]+$`: `bot/handlers/inventory.py:532`
- `field:`: `bot/handlers/admin.py:2091`
- `field:required_status`: `bot/handlers/admin.py:1834`
- `field_req:`: `bot/handlers/admin.py:1867`
- `fin:`: `bot/handlers/admin.py:2541`
- `finuser:`: `bot/handlers/admin.py:2571`
- `fish:bait:\d+$`: `bot/handlers/fishing.py:514`
- `fish:bait:set:\d+:[a-z]+$`: `bot/handlers/fishing.py:556`
- `fish:cast:\d+$`: `bot/handlers/fishing.py:566`
- `fish:lake:\d+$`: `bot/handlers/fishing.py:493`
- `fishbuy:`: `bot/handlers/shop.py:807`
- `fishcatch:`: `bot/handlers/inventory.py:1280`
- `fishgo:`: `bot/handlers/inventory.py:1531`
- `fishing:addfish:`: `bot/handlers/admin.py:6921`
- `fishing:addlist:`: `bot/handlers/admin.py:6891`
- `fishing:del:`: `bot/handlers/admin.py:6944`
- `fishing:fish:`: `bot/handlers/admin.py:6811`
- `fishing:junk:`: `bot/handlers/admin.py:6667`
- `fishing:kind:`: `bot/handlers/admin.py:6825`
- `fishing:market:`: `bot/handlers/admin.py:6847`
- `fishing:new:`: `bot/handlers/admin.py:6969`
- `fishing:new_super:`: `bot/handlers/admin.py:7072`
- `fishing:super:`: `bot/handlers/admin.py:6869`
- `fishing:water:`: `bot/handlers/admin.py:6773`
- `fishing_field:`: `bot/handlers/admin.py:7131`
- `fishing_j:`: `bot/handlers/admin.py:6717`
- `fishmarket:`: `bot/handlers/inventory.py:1433`
- `fishoffer:`: `bot/handlers/shop.py:732`
- `fishprice:`: `bot/handlers/inventory.py:1513`
- `fishsell:`: `bot/handlers/inventory.py:1589`
- `fishuse:`: `bot/handlers/inventory.py:1288`
- `forest:add:`: `bot/handlers/admin.py:7672`
- `forest:area:\d+:(glade|clearing)$`: `bot/handlers/forest.py:426`
- `forest:battle:flee:\d+$`: `bot/handlers/forest.py:1070`
- `forest:battle:hit:\d+$`: `bot/handlers/forest.py:863`
- `forest:card:`: `bot/handlers/admin.py:7586`
- `forest:cast:\d+(?::(glade|clearing))?$`: `bot/handlers/forest.py:500`
- `forest:del:`: `bot/handlers/admin.py:7691`
- `forest:kind:`: `bot/handlers/admin.py:7600`
- `forest:market:`: `bot/handlers/admin.py:7625`
- `forest:new_kind:`: `bot/handlers/admin.py:7880`
- `forest:zadd:(glade|clearing):\d+$`: `bot/handlers/admin.py:7452`
- `forest:zaddlist:(glade|clearing)$`: `bot/handlers/admin.py:7425`
- `forest:zchance:(glade|clearing):\d+$`: `bot/handlers/admin.py:7398`
- `forest:zdel:(glade|clearing):\d+$`: `bot/handlers/admin.py:7413`
- `forest:zone:(glade|clearing)$`: `bot/handlers/admin.py:7326`
- `forest:zset:(glade|clearing):(\w+)$`: `bot/handlers/admin.py:7464`
- `forest_field:`: `bot/handlers/admin.py:7712`
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
- `loc:blocking:`: `bot/handlers/admin.py:8131`
- `loc:building:`: `bot/handlers/admin.py:8020`
- `loc:edit:`: `bot/handlers/admin.py:7994`
- `loc:mode:`: `bot/handlers/admin.py:8060`
- `loc:photo_set:`: `bot/handlers/admin.py:8767`
- `loc:req_status:`: `bot/handlers/admin.py:8096`
- `loc:season:(winter|spring|summer|autumn)$`: `bot/handlers/admin.py:8448`
- `loc:season_clear:(winter|spring|summer|autumn)$`: `bot/handlers/admin.py:8474`
- `loc:season_photo_set:(winter|spring|summer|autumn):(dawn|day|sunset|night)$`: `bot/handlers/admin.py:8804`
- `location:enter:`: `bot/handlers/locations.py:107`
- `location:preview:`: `bot/handlers/locations.py:40`
- `locstat:`: `bot/handlers/admin.py:4882`
- `logsite:battle:flee:\d+$`: `bot/handlers/logging_site.py:1074`
- `logsite:battle:hit:\d+$`: `bot/handlers/logging_site.py:871`
- `logsite:chop:\d+$`: `bot/handlers/logging_site.py:463`
- `logsite:fire:(1|all):\d+$`: `bot/handlers/logging_site.py:724`
- `logsite:menu:\d+$`: `bot/handlers/logging_site.py:448`
- `logsite:mill:\d+$`: `bot/handlers/logging_site.py:611`
- `logsite:plank:(1|all):\d+$`: `bot/handlers/logging_site.py:665`
- `lootonly:`: `bot/handlers/admin.py:1529`
- `marketok:`: `bot/handlers/admin.py:1507`
- `mine:battle:flee:\d+$`: `bot/handlers/mine.py:725`
- `mine:battle:hit:\d+$`: `bot/handlers/mine.py:574`
- `mine:deeper:\d+$`: `bot/handlers/mine.py:391`
- `mine:dig:\d+$`: `bot/handlers/mine.py:402`
- `mine:level:\d+$`: `bot/handlers/mine.py:358`
- `mine:menu:\d+$`: `bot/handlers/mine.py:351`
- `mollusk:flee:\d+$`: `bot/handlers/dungeon.py:504`
- `mollusk:hit:\d+$`: `bot/handlers/dungeon.py:372`
- `mvd:arch:`: `bot/handlers/mvd.py:95`
- `mvd:archive:`: `bot/handlers/mvd.py:45`
- `news:(?:off|(?:dis)?allow:-?\d+|chat:-?\d+:-?\d+|topic:-?\d+:-?\d+)$`: `bot/handlers/admin.py:2863`
- `news:arch:\d+$`: `bot/handlers/news.py:179`
- `news:del:`: `bot/handlers/news.py:473`
- `news:delconf:`: `bot/handlers/news.py:495`
- `news:edit:`: `bot/handlers/news.py:400`
- `news:view:`: `bot/handlers/news.py:196`
- `nii:set:`: `bot/handlers/nii.py:319`
- `nii:view:`: `bot/handlers/nii.py:284`
- `offercancel:fish:`: `bot/handlers/shop.py:977`
- `offercancel:item:`: `bot/handlers/shop.py:982`
- `page`: `bot/handlers/admin.py:412`
- `park:admin:del:`: `bot/handlers/park.py:390`
- `park:admin:delyes:`: `bot/handlers/park.py:408`
- `park:admin:edit:`: `bot/handlers/park.py:474`
- `park:adminedit:f:`: `bot/handlers/park.py:492`
- `park:statue:`: `bot/handlers/park.py:257`
- `pickuser:`: `bot/handlers/admin.py:403`
- `pollarch:day:\d{4}-\d{2}-\d{2}(?::\d+)?$`: `bot/handlers/poll_archive.py:176`
- `pollarch:days:\d+$`: `bot/handlers/poll_archive.py:154`
- `prod:`: `bot/handlers/admin.py:1467`
- `prof_sel_status:`: `bot/handlers/profile.py:327`
- `profile:award:`: `bot/handlers/profile.py:550`
- `rank_pick:`: `bot/handlers/admin.py:4715`
- `rank_promote:`: `bot/handlers/admin.py:4674`
- `rar:`: `bot/handlers/admin.py:1267`
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
- `rep:nav:`: `bot/handlers/admin.py:4600`
- `rep_fix:`: `bot/handlers/admin.py:4399`
- `rep_no:`: `bot/handlers/admin.py:4585`
- `rep_ok:`: `bot/handlers/admin.py:4516`
- `report:my:`: `bot/handlers/reports.py:390`
- `report:view:`: `bot/handlers/reports.py:402`
- `resv:bait:\d+$`: `bot/handlers/dungeon.py:2119`
- `resv:bait:set:\d+:[a-z]+$`: `bot/handlers/dungeon.py:2167`
- `resv:cast:\d+$`: `bot/handlers/dungeon.py:2186`
- `resv:deeper:\d+$`: `bot/handlers/dungeon.py:2423`
- `resv:enter:\d+$`: `bot/handlers/dungeon.py:2081`
- `resv:eq:\d+$`: `bot/handlers/dungeon.py:2458`
- `resv:eqclear:[a-z0-9_]+:\d+$`: `bot/handlers/dungeon.py:2566`
- `resv:eqset:[a-z0-9_]+:\d+:\d+$`: `bot/handlers/dungeon.py:2542`
- `resv:eqslot:[a-z0-9_]+:\d+$`: `bot/handlers/dungeon.py:2496`
- `resv:menu:\d+$`: `bot/handlers/dungeon.py:2105`
- `role:`: `bot/handlers/admin.py:2776`
- `rolop:`: `bot/handlers/admin.py:2727`
- `salary_period:`: `bot/handlers/admin.py:5168`
- `shop_del:cat:`: `bot/handlers/admin.py:1771`
- `shop_edit:cat:`: `bot/handlers/admin.py:1756`
- `shopcat:[^:]+$`: `bot/handlers/shop.py:250`
- `shopcat:[^:]+:\d+$`: `bot/handlers/shop.py:338`
- `shopitem:`: `bot/handlers/shop.py:349`
- `st_del:`: `bot/handlers/admin.py:3070`
- `st_key:`: `bot/handlers/admin.py:5011`
- `st_op:`: `bot/handlers/admin.py:4981`
- `st_pick:`: `bot/handlers/admin.py:3352`
- `st_rev:`: `bot/handlers/admin.py:3282`
- `storage:cat:`: `bot/handlers/admin.py:972`
- `storage:item:`: `bot/handlers/admin.py:1003`
- `storage:page:`: `bot/handlers/admin.py:989`
- `storage:purge:`: `bot/handlers/admin.py:1129`
- `storage:restock:`: `bot/handlers/admin.py:1061`
- `toggle:`: `bot/handlers/admin.py:8136`
- `vote:cast:`: `bot/handlers/polls.py:163`
- `vote:close:`: `bot/handlers/polls.py:287`
- `vote:close_confirm:`: `bot/handlers/polls.py:310`
- `vote:results:`: `bot/handlers/polls.py:185`
- `vote:show:`: `bot/handlers/polls.py:109`
- `wall:archpage:\d+$`: `bot/handlers/wall.py:338`
- `wall:archread:\d+(?::\d+)?$`: `bot/handlers/wall.py:357`
- `wall:delete:\d+$`: `bot/handlers/wall.py:224`
- `wall:page:\d+$`: `bot/handlers/wall.py:156`
- `weff:`: `bot/handlers/admin.py:1400`
- `wing_set:`: `bot/handlers/admin.py:820`
- `Испорченный`: `bot/handlers/dungeon.py:1913`
- `⛔`: `bot/handlers/wall.py:176`

## 4. ⚠️ Возможные конфликты

**Один `callback_data` ловится несколькими `F.data ==`-хендлерами**
(побеждает зарегистрированный раньше — второй код мёртв):

- `noop`:
    - `bot/handlers/admin.py:4916`
    - `bot/handlers/bank.py:453`

**Префиксный фильтр перекрывает точный ключ** (проверь порядок регистрации):

- `startswith("field:")` ⇄ `== "field:weapon_effect"`
- `startswith("field:")` ⇄ `== "field:photo"`
- `startswith("field:")` ⇄ `== "field:drink"`
- `startswith("field:")` ⇄ `== "field:market_ok"`
- `startswith("field:")` ⇄ `== "field:loot_only"`
- `startswith("fin:")` ⇄ `== "fin:manual"`

