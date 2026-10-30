# Карта FSM-состояний и callback-неймспейсов N.O.R.D.

> **Сгенерировано** `tools/export_states.py`. Не редактировать вручную —
> правь код и перегенерируй: `.venv\Scripts\python.exe tools/export_states.py`.
>
> Назначение: единый обзор всех `StatesGroup`, где они ставятся и где ловятся,
> а также реестр `callback_data` — чтобы не допускать конфликтов меню/хендлеров.

Всего классов состояний: **53**; полей-состояний: **228**; уникальных `callback_data`: **268**.

## 1. Классы состояний по модулям

### `AdminAddItem` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `name` | `bot/handlers/admin.py:1218` `shop_admin_add`<br>`bot/handlers/admin.py:6355` `enemy_drop_new_item` | `bot/handlers/admin.py:1226` `add_item_name` |
| `desc` | `bot/handlers/admin.py:1228` `add_item_name` | `bot/handlers/admin.py:1234` `add_item_desc` |
| `price` | `bot/handlers/admin.py:1237` `add_item_desc` | `bot/handlers/admin.py:1243` `add_item_price` |
| `sell_price` | `bot/handlers/admin.py:1253` `add_item_price` | `bot/handlers/admin.py:1259` `add_item_sell_price` |
| `rarity` | `bot/handlers/admin.py:1271` `add_item_sell_price` | — |
| `category` | `bot/handlers/admin.py:1280` `add_item_rarity` | — |
| `drink` | `bot/handlers/admin.py:1303` `add_item_category` | — |
| `plant_name` | `bot/handlers/admin.py:1292` `add_item_category` | `bot/handlers/admin.py:1328` `add_item_plant_name` |
| `stock` | `bot/handlers/admin.py:1312` `add_item_category`<br>`bot/handlers/admin.py:1322` `add_item_drink_choice`<br>`bot/handlers/admin.py:1331` `add_item_plant_name` | `bot/handlers/admin.py:1337` `add_item_stock` |
| `stats` | `bot/handlers/admin.py:1351` `add_item_stock`<br>`bot/handlers/admin.py:1356` `add_item_stock` | `bot/handlers/admin.py:1364` `add_item_stats`<br>`bot/handlers/admin.py:1404` `add_item_stats_bad` |
| `equip_slot` | `bot/handlers/admin.py:1381` `add_item_stats` | — |
| `weapon_effect` | `bot/handlers/admin.py:1369` `add_item_stats` | — |
| `weapon_effect_chance` | `bot/handlers/admin.py:1417` `add_item_weapon_effect_cb` | `bot/handlers/admin.py:1426` `add_item_weapon_effect_chance` |
| `weapon_effect_dmg` | `bot/handlers/admin.py:1438` `add_item_weapon_effect_chance` | `bot/handlers/admin.py:1450` `add_item_weapon_effect_dmg` |
| `producer` | `bot/handlers/admin.py:1465` `_go_add_item_producer` | — |
| `producer_user` | `bot/handlers/admin.py:1480` `add_item_producer` | `bot/handlers/admin.py:1492` `add_item_producer_user` |
| `market` | `bot/handlers/admin.py:1503` `_go_add_item_market` | — |
| `loot` | `bot/handlers/admin.py:1525` `_go_add_item_loot` | — |
| `status` | `bot/handlers/admin.py:1553` `_go_add_item_status` | — |
| `photo` | `bot/handlers/admin.py:1572` `add_item_status_cb` | `bot/handlers/admin.py:1580` `add_item_photo` |

### `AdminSaleTax` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `percent` | `bot/handlers/admin.py:2465` `admin_saletax_view` | `bot/handlers/admin.py:2479` `admin_saletax_set` |

### `AdminSpecialCode` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `code` | `bot/handlers/admin.py:2507` `admin_special_code_view` | `bot/handlers/admin.py:2522` `admin_special_code_set` |

### `AdminEditItem` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `item_id` | — | — |
| `field` | `bot/handlers/admin.py:1808` `edit_item_pick` | — |
| `value` | `bot/handlers/admin.py:2112` `edit_item_field` | `bot/handlers/admin.py:2123` `edit_item_value` |
| `photo` | `bot/handlers/admin.py:1897` `edit_item_field_photo` | `bot/handlers/admin.py:1947` `edit_item_photo` |

### `AdminFinance` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | `bot/handlers/admin.py:2548` `finance_manual`<br>`bot/handlers/admin.py:2570` `finance_pick` | `bot/handlers/admin.py:2808` `finance_target` |
| `currency` | — | — |
| `amount` | `bot/handlers/admin.py:459` `pickuser_cb`<br>`bot/handlers/admin.py:2640` `finance_pick_user`<br>`bot/handlers/admin.py:2815` `finance_target` | `bot/handlers/admin.py:2823` `finance_amount` |

### `AdminTreasury` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `amount` | `bot/handlers/admin.py:2372` `treasury_give` | `bot/handlers/admin.py:2382` `treasury_amount` |
| `target` | `bot/handlers/admin.py:2398` `treasury_amount` | `bot/handlers/admin.py:2404` `treasury_target_manual` |

### `AdminStorageRestock` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `amount` | `bot/handlers/admin.py:1080` `storage_restock` | `bot/handlers/admin.py:1094` `storage_restock_amount` |

### `AdminStorageDelete` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `confirm` | `bot/handlers/admin.py:1152` `storage_purge` | `bot/handlers/admin.py:1166` `storage_purge_confirm` |

### `AdminTax` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `percent` | `bot/handlers/admin.py:2428` `admin_tax_view` | `bot/handlers/admin.py:2440` `admin_tax_set` |

### `AdminReportAutoApprove` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `value` | `bot/handlers/admin.py:4387` `report_auto_approve_edit_cb` | `bot/handlers/admin.py:4400` `report_auto_approve_edit_value` |

### `AdminReportPayCap` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `value` | `bot/handlers/admin.py:4426` `report_pay_cap_edit_cb` | `bot/handlers/admin.py:4441` `report_pay_cap_edit_value` |

### `AdminReportFix` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `daily` | `bot/handlers/admin.py:4627` `report_fix_start` | `bot/handlers/admin.py:4640` `report_fix_daily` |
| `total` | `bot/handlers/admin.py:4654` `report_fix_daily` | `bot/handlers/admin.py:4668` `report_fix_total` |

### `AdminRoles` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | `bot/handlers/admin.py:2901` `admin_roles` | `bot/handlers/admin.py:2910` `roles_target` |
| `action` | `bot/handlers/admin.py:462` `pickuser_cb`<br>`bot/handlers/admin.py:2916` `roles_target` | — |
| `role` | `bot/handlers/admin.py:2934` `roles_action` | — |

### `AdminStatuses` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `name` | `bot/handlers/admin.py:3185` `status_create_start` | `bot/handlers/admin.py:3193` `status_create_name` |
| `tag` | `bot/handlers/admin.py:3195` `status_create_name` | `bot/handlers/admin.py:3204` `status_create_tag` |
| `level` | `bot/handlers/admin.py:3211` `status_create_tag` | `bot/handlers/admin.py:3221` `status_create_level` |
| `desc` | `bot/handlers/admin.py:3232` `status_create_level` | `bot/handlers/admin.py:3237` `status_create_desc` |
| `target` | `bot/handlers/admin.py:3461` `status_grant_target`<br>`bot/handlers/admin.py:3530` `status_revoke_target` | `bot/handlers/admin.py:3471` `status_grant_target_msg` |
| `grant_action` | — | — |
| `status_pick` | `bot/handlers/admin.py:477` `pickuser_cb`<br>`bot/handlers/admin.py:486` `pickuser_cb`<br>`bot/handlers/admin.py:3482` `status_grant_target_msg`<br>`bot/handlers/admin.py:3614` `status_grant_more` | — |
| `item_pick` | — | — |
| `item_status` | — | — |

### `AdminAwards` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `name` | `bot/handlers/admin.py:3703` `award_create_start` | `bot/handlers/admin.py:3760` `award_create_name` |
| `desc` | `bot/handlers/admin.py:3766` `award_create_name` | `bot/handlers/admin.py:3774` `award_create_desc` |
| `emoji` | `bot/handlers/admin.py:3777` `award_create_desc` | `bot/handlers/admin.py:3785` `award_create_emoji` |
| `bonus` | `bot/handlers/admin.py:3751` `_award_ask_bonus` | `bot/handlers/admin.py:3793` `award_create_bonus` |
| `preview` | `bot/handlers/admin.py:3739` `_award_ask_bonus` | — |
| `target` | `bot/handlers/admin.py:4182` `award_grant_target` | `bot/handlers/admin.py:4188` `award_grant_target_msg` |
| `award_pick` | `bot/handlers/admin.py:4263` `award_revoke_pick_user` | — |
| `comment` | `bot/handlers/admin.py:4206` `award_grant_pick` | `bot/handlers/admin.py:4223` `award_grant_comment` |
| `edit_value` | `bot/handlers/admin.py:4062` `award_edit_field_pick` | `bot/handlers/admin.py:4086` `award_edit_value` |

### `AdminFishing` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `water` | — | — |
| `wf_id` | — | — |
| `value` | `bot/handlers/admin.py:6916` `admin_fishing_junk_field_pick`<br>`bot/handlers/admin.py:7331` `admin_fishing_field_pick` | `bot/handlers/admin.py:7358` `admin_fishing_value` |
| `c_name` | `bot/handlers/admin.py:7168` `admin_fishing_new` | `bot/handlers/admin.py:7177` `admin_fishing_new_name` |
| `c_desc` | `bot/handlers/admin.py:7187` `admin_fishing_new_name` | `bot/handlers/admin.py:7193` `admin_fishing_new_desc` |
| `c_sell_price` | `bot/handlers/admin.py:7196` `admin_fishing_new_desc` | `bot/handlers/admin.py:7202` `admin_fishing_new_sell_price` |
| `c_day_weight` | `bot/handlers/admin.py:7210` `admin_fishing_new_sell_price` | `bot/handlers/admin.py:7218` `admin_fishing_new_day_weight` |
| `c_night_weight` | `bot/handlers/admin.py:7226` `admin_fishing_new_day_weight` | `bot/handlers/admin.py:7234` `admin_fishing_new_night_weight` |
| `c_photo` | `bot/handlers/admin.py:7266` `admin_fishing_new_super` | `bot/handlers/admin.py:7274` `admin_fishing_new_photo` |
| `c_super_rare` | `bot/handlers/admin.py:7242` `admin_fishing_new_night_weight` | — |

### `AdminForest` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `f_id` | — | — |
| `field` | — | — |
| `value` | `bot/handlers/admin.py:7913` `admin_forest_field_pick` | `bot/handlers/admin.py:7939` `admin_forest_value` |
| `c_name` | `bot/handlers/admin.py:7995` `admin_forest_new` | `bot/handlers/admin.py:8004` `admin_forest_new_name` |
| `c_desc` | `bot/handlers/admin.py:8014` `admin_forest_new_name` | `bot/handlers/admin.py:8020` `admin_forest_new_desc` |
| `c_sell_price` | `bot/handlers/admin.py:8023` `admin_forest_new_desc` | `bot/handlers/admin.py:8029` `admin_forest_new_sell_price` |
| `c_chance` | `bot/handlers/admin.py:8036` `admin_forest_new_sell_price` | `bot/handlers/admin.py:8045` `admin_forest_new_chance` |
| `c_kind` | `bot/handlers/admin.py:8053` `admin_forest_new_chance` | — |
| `c_photo` | `bot/handlers/admin.py:8076` `admin_forest_new_kind` | `bot/handlers/admin.py:8084` `admin_forest_new_photo` |
| `zone_value` | `bot/handlers/admin.py:7593` `admin_forest_zone_chance`<br>`bot/handlers/admin.py:7668` `admin_forest_zone_set_pick`<br>`bot/handlers/admin.py:7681` `admin_forest_limit_set` | `bot/handlers/admin.py:7688` `admin_forest_zone_value` |

### `AdminEnemy` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `field` | `bot/handlers/admin.py:9540` `admin_enemies_field_pick` | `bot/handlers/admin.py:9546` `admin_enemies_field_value` |
| `photo` | `bot/handlers/admin.py:9597` `admin_enemies_photo_pick` | `bot/handlers/admin.py:9603` `admin_enemies_photo_value` |
| `onhit_value` | `bot/handlers/admin.py:6152` `source_enemy_effect_toggle` | `bot/handlers/admin.py:6158` `source_enemy_onhit_value` |
| `drop_chance` | `bot/handlers/admin.py:9757` `admin_enemies_drop_edit_chance`<br>`bot/handlers/admin.py:9831` `admin_enemies_drop_add_pick` | `bot/handlers/admin.py:9837` `admin_enemies_drop_chance_value` |
| `drop_qty` | `bot/handlers/admin.py:9770` `admin_enemies_drop_edit_qty`<br>`bot/handlers/admin.py:9858` `admin_enemies_drop_chance_value` | `bot/handlers/admin.py:9864` `admin_enemies_drop_qty_value` |
| `c_name` | `bot/handlers/admin.py:9903` `admin_enemies_new` | `bot/handlers/admin.py:9908` `admin_enemies_new_name` |
| `c_hp` | `bot/handlers/admin.py:9914` `admin_enemies_new_name` | `bot/handlers/admin.py:9919` `admin_enemies_new_hp` |
| `c_dmg` | `bot/handlers/admin.py:9925` `admin_enemies_new_hp` | `bot/handlers/admin.py:9930` `admin_enemies_new_dmg` |
| `c_dodge` | `bot/handlers/admin.py:9943` `admin_enemies_new_dmg` | `bot/handlers/admin.py:9948` `admin_enemies_new_dodge` |
| `c_chance` | `bot/handlers/admin.py:9954` `admin_enemies_new_dodge` | `bot/handlers/admin.py:9960` `admin_enemies_new_chance` |
| `c_loss_ap` | `bot/handlers/admin.py:9966` `admin_enemies_new_chance` | `bot/handlers/admin.py:9972` `admin_enemies_new_done` |

### `AdminCallsign` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | `bot/handlers/admin.py:762` `admin_callsign_start` | `bot/handlers/admin.py:783` `admin_callsign_target_msg` |
| `value` | `bot/handlers/admin.py:544` `pickuser_cb`<br>`bot/handlers/admin.py:793` `admin_callsign_target_msg` | `bot/handlers/admin.py:804` `admin_callsign_value_msg` |

### `AdminWing` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | `bot/handlers/admin.py:775` `admin_wing_start` | — |
| `value` | `bot/handlers/admin.py:555` `pickuser_cb` | — |

### `AdminStates` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | `bot/handlers/admin.py:5163` `admin_states_menu` | `bot/handlers/admin.py:5172` `admin_states_target_text` |
| `action` | `bot/handlers/admin.py:516` `pickuser_cb`<br>`bot/handlers/admin.py:5178` `admin_states_target_text` | — |
| `state_key` | `bot/handlers/admin.py:5207` `admin_states_op` | — |
| `minutes` | `bot/handlers/admin.py:5232` `admin_states_key` | `bot/handlers/admin.py:5241` `admin_states_minutes`<br>`bot/handlers/admin.py:5262` `admin_states_minutes_bad` |

### `AdminPlayerLog` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | `bot/handlers/admin.py:748` `admin_player_log_start` | `bot/handlers/admin.py:616` `admin_player_log_manual_msg` |

### `AdminSalary` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `amount` | `bot/handlers/admin.py:529` `pickuser_cb` | `bot/handlers/admin.py:5362` `admin_salary_amount` |

### `AdminLocation` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `action` | — | — |
| `target_id` | — | — |
| `key` | `bot/handlers/admin.py:8139` `loc_create` | `bot/handlers/admin.py:8403` `loc_step_key` |
| `name` | `bot/handlers/admin.py:8409` `loc_step_key` | `bot/handlers/admin.py:8414` `loc_step_name` |
| `set_name` | `bot/handlers/admin.py:8430` `loc_set_name` | `bot/handlers/admin.py:8441` `loc_step_set_name` |
| `description` | `bot/handlers/admin.py:8416` `loc_step_name`<br>`bot/handlers/admin.py:8455` `loc_step_set_name`<br>`bot/handlers/admin.py:8469` `loc_set_desc` | `bot/handlers/admin.py:8680` `loc_step_desc` |
| `mode` | `bot/handlers/admin.py:8235` `loc_set_mode`<br>`bot/handlers/admin.py:8691` `loc_step_desc` | `bot/handlers/admin.py:8248` `loc_mode_chosen` |
| `req_status` | `bot/handlers/admin.py:8261` `loc_mode_chosen`<br>`bot/handlers/admin.py:8270` `loc_mode_chosen`<br>`bot/handlers/admin.py:8279` `loc_set_status` | `bot/handlers/admin.py:8284` `loc_req_status_chosen` |
| `blocking` | `bot/handlers/admin.py:8267` `loc_mode_chosen`<br>`bot/handlers/admin.py:8298` `loc_req_status_chosen`<br>`bot/handlers/admin.py:8314` `loc_set_blocking` | `bot/handlers/admin.py:8319` `loc_blocking_chosen` |
| `preview` | `bot/handlers/admin.py:8717` `loc_glade_set`<br>`bot/handlers/admin.py:8803` `loc_fire_set`<br>`bot/handlers/admin.py:8851` `loc_clearing_set`<br>`bot/handlers/admin.py:8903` `loc_logging_set`<br>`bot/handlers/admin.py:8954` `loc_mine_set`<br>`bot/handlers/admin.py:9005` `loc_storage_set`<br>`bot/handlers/admin.py:9054` `loc_photo_set`<br>`bot/handlers/admin.py:9092` `loc_season_photo_set` | `bot/handlers/admin.py:9134` `loc_step_photo` |

### `AdminCityPhoto` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `photo` | `bot/handlers/admin.py:8749` `loc_city_fire` | `bot/handlers/admin.py:8768` `loc_city_fire_save` |

### `AdminDungeon` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target_id` | — | — |
| `photo_tod` | `bot/handlers/admin.py:5524` `dungeon_photo_set` | `bot/handlers/admin.py:5560` `dungeon_step_photo` |
| `enemy_id` | — | — |
| `enemy_field` | — | — |
| `enemy_value` | `bot/handlers/admin.py:5796` `dungeon_enemy_field_pick` | `bot/handlers/admin.py:5822` `dungeon_enemy_value` |
| `onhit_value` | `bot/handlers/admin.py:6076` `dungeon_enemy_effect_toggle` | `bot/handlers/admin.py:6082` `dungeon_enemy_onhit_value` |
| `drop_chance` | `bot/handlers/admin.py:1624` `add_item_photo`<br>`bot/handlers/admin.py:6332` `enemy_drop_pick_item`<br>`bot/handlers/admin.py:6415` `enemy_drop_set_chance` | `bot/handlers/admin.py:6737` `enemy_drop_chance_value` |
| `drop_qty` | `bot/handlers/admin.py:6438` `enemy_drop_set_qty`<br>`bot/handlers/admin.py:6746` `enemy_drop_chance_value` | `bot/handlers/admin.py:6752` `enemy_drop_qty_value` |
| `drop_item_photo` | `bot/handlers/admin.py:6483` `enemy_drop_item_photo` | `bot/handlers/admin.py:6492` `enemy_drop_item_photo_value` |
| `drop_item_desc` | `bot/handlers/admin.py:6537` `enemy_drop_item_desc` | `bot/handlers/admin.py:6546` `enemy_drop_item_desc_value` |
| `drop_item_field` | — | — |
| `drop_item_value` | `bot/handlers/admin.py:6635` `enemy_drop_item_stat_pick` | `bot/handlers/admin.py:6646` `enemy_drop_item_stat_value` |
| `pending_enemy_id` | — | — |

### `ClanPhotosAdmin` — `bot/handlers/admin_clanphotos.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `wait_exp_photo` | `bot/handlers/admin_clanphotos.py:134` `clanph_exp_cb` | `bot/handlers/admin_clanphotos.py:146` `clanph_exp_photo_save` |
| `wait_building_photo` | `bot/handlers/admin_clanphotos.py:259` `clanph_bclan_cb` | `bot/handlers/admin_clanphotos.py:269` `clanph_building_photo_save` |
| `wait_construction_photo` | `bot/handlers/admin_clanphotos.py:178` `clanph_construction_cb` | `bot/handlers/admin_clanphotos.py:189` `clanph_construction_photo_save` |

### `FirePhotosAdmin` — `bot/handlers/admin_firephotos.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `wait_photo` | `bot/handlers/admin_firephotos.py:92` `fire_photo_pick_cb` | `bot/handlers/admin_firephotos.py:104` `fire_photo_save` |

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
| `wait_building_photo` | `bot/handlers/clan_hall.py:2138` `clan_hall_admphoto_cb` | `bot/handlers/clan_hall.py:2174` `clan_hall_admphoto_save` |
| `wait_construction_photo` | `bot/handlers/clan_hall.py:2167` `clan_hall_admconstphoto_cb` | `bot/handlers/clan_hall.py:2192` `clan_hall_admconstphoto_save` |
| `wait_expansion_photo` | `bot/handlers/clan_hall.py:2216` `clan_hall_admexphoto_cb` | `bot/handlers/clan_hall.py:2228` `clan_hall_admexphoto_save` |

### `ClansCreate` — `bot/handlers/clans.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `kind` | — | — |
| `wait_name` | `bot/handlers/clans.py:703` `clan_create_start` | `bot/handlers/clans.py:711` `clan_create_name` |
| `wait_desc` | `bot/handlers/clans.py:718` `clan_create_name` | `bot/handlers/clans.py:726` `clan_create_desc` |
| `wait_photo` | `bot/handlers/clans.py:736` `clan_create_desc` | `bot/handlers/clans.py:780` `clan_create_photo`<br>`bot/handlers/clans.py:787` `clan_create_photo_hint` |

### `ClansEdit` — `bot/handlers/clans.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `field` | — | — |
| `wait_value` | `bot/handlers/clans.py:851` `clan_edit_field_cb` | `bot/handlers/clans.py:857` `clan_edit_finish_photo`<br>`bot/handlers/clans.py:871` `clan_edit_finish_text` |

### `ClansMessage` — `bot/handlers/clans.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `wait_text` | `bot/handlers/clans.py:908` `clan_msg_start` | `bot/handlers/clans.py:916` `clan_msg_send` |

### `DungeonFSM` — `bot/handlers/dungeon.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `in_dungeon` | `bot/handlers/dungeon.py:937` `contract_enter_confirm`<br>`bot/handlers/dungeon.py:1016` `post_captain_menu`<br>`bot/handlers/dungeon.py:2462` `resv_deeper` | — |
| `in_combat` | — | — |
| `in_boss` | `bot/handlers/dungeon.py:2094` `show_boss` | — |
| `confirm_enter` | `bot/handlers/dungeon.py:866` `contract_enter` | — |
| `in_reservoir` | `bot/handlers/dungeon.py:2116` `resv_enter`<br>`bot/handlers/dungeon.py:2131` `resv_menu`<br>`bot/handlers/dungeon.py:2198` `resv_bait_set` | — |

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
| `target` | `bot/handlers/inventory.py:1654` `inv_transfer_start` | `bot/handlers/inventory.py:1663` `inv_transfer_target` |
| `amount` | `bot/handlers/inventory.py:1670` `inv_transfer_target` | `bot/handlers/inventory.py:1678` `inv_transfer_amount` |
| `message` | `bot/handlers/inventory.py:1710` `inv_transfer_amount` | `bot/handlers/inventory.py:1719` `inv_transfer_message` |

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
| `field` | `bot/handlers/park.py:492` `statue_admin_edit_start`<br>`bot/handlers/park.py:557` `statue_admin_edit_value` | — |
| `value` | `bot/handlers/park.py:503` `statue_admin_edit_field` | `bot/handlers/park.py:532` `statue_admin_edit_value` |

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
| `fireevent:` | 1 | `fireevent:potioncancel` |
| `fish:` | 1 | `fish:recover` |
| `fishing:` | 5 | `fishing:new_super:0`, `fishing:new_super:1`, `fishing:water:fire_well`, `fishing:water:lake`, `fishing:water:reservoir` |
| `fishing_field:` | 4 | `fishing_field:day_weight`, `fishing_field:night_weight`, `fishing_field:photo`, `fishing_field:sell_price` |
| `forest:` | 4 | `forest:new`, `forest:new_kind:edible`, `forest:new_kind:toxic`, `forest:zset:sold_daily_limit` |
| `forest_field:` | 3 | `forest_field:chance`, `forest_field:photo`, `forest_field:sell_price` |
| `hq:` | 19 | `hq:farms`, `hq:menu`, `hq:noop`, `hq:order:all`, `hq:region_stats`, `hq:region_stats_refresh`, `hq:roster:0`, `hq:send`, `hq:wing`, `hq:wingadd`, `hq:wingcmd`, `hq:wingcmd_send`, `hq:wingdrop:0`, `hq:wingedit:callsign`, `hq:wingedit:emoji`, `hq:wingedit:name`, `hq:wingfarm:0`, `hq:wings`, `hq:wingtake:0` |
| `inventory:` | 2 | `inventory:eq`, `inventory:list` |
| `kvp:` | 3 | `kvp:exit`, `kvp:resume`, `kvp:start` |
| `lib:` | 2 | `lib:menu`, `lib:no_access` |
| `libadmin:` | 3 | `libadmin:add`, `libadmin:list`, `libadmin:menu` |
| `loc:` | 23 | `loc:blocking:done`, `loc:blocking:none`, `loc:building_pick`, `loc:city_fire`, `loc:clearing_set`, `loc:create`, `loc:edit_pick`, `loc:fire_set`, `loc:glade_set`, `loc:logging_set`, `loc:mine_set`, `loc:mode:all`, `loc:mode:exact`, `loc:mode:min`, `loc:photos`, `loc:photos:clear`, `loc:photos:clear_seasons`, `loc:set_blocking`, `loc:set_desc`, `loc:set_mode`, `loc:set_name`, `loc:set_status`, `loc:storage_set` |
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

- `admin:awards`: `bot/handlers/admin.py:3620`
- `admin:callsign`: `bot/handlers/admin.py:756`
- `admin:del_photo`: `bot/handlers/admin.py:730`
- `admin:dungeons`: `bot/handlers/admin.py:5422`
- `admin:enemies`: `bot/handlers/admin.py:9346`
- `admin:finance`: `bot/handlers/admin.py:2191`
- `admin:fishing`: `bot/handlers/admin.py:6940`
- `admin:forest`: `bot/handlers/admin.py:7503`
- `admin:locations`: `bot/handlers/admin.py:5397`
- `admin:logs`: `bot/handlers/admin.py:4959`
- `admin:menu`: `bot/handlers/admin.py:720`
- `admin:player_log`: `bot/handlers/admin.py:742`
- `admin:ranks`: `bot/handlers/admin.py:4849`
- `admin:reports`: `bot/handlers/admin.py:4284`
- `admin:reports_done`: `bot/handlers/admin.py:4336`
- `admin:reports_pending`: `bot/handlers/admin.py:4293`
- `admin:roles`: `bot/handlers/admin.py:2891`
- `admin:salaries`: `bot/handlers/admin.py:5266`
- `admin:saletax`: `bot/handlers/admin.py:2458`
- `admin:shop`: `bot/handlers/admin.py:871`
- `admin:states`: `bot/handlers/admin.py:5157`
- `admin:statuses`: `bot/handlers/admin.py:3125`
- `admin:storage`: `bot/handlers/admin.py:946`
- `admin:tax`: `bot/handlers/admin.py:2421`
- `admin:treasury`: `bot/handlers/admin.py:2234`
- `admin:wing`: `bot/handlers/admin.py:769`
- `aw:ach`: `bot/handlers/admin.py:3678`
- `aw:create`: `bot/handlers/admin.py:3696`
- `aw:delete`: `bot/handlers/admin.py:3837`
- `aw:edit`: `bot/handlers/admin.py:4021`
- `aw:grant`: `bot/handlers/admin.py:4179`
- `aw:list`: `bot/handlers/admin.py:3657`
- `aw:revoke`: `bot/handlers/admin.py:4260`
- `aw_comment:skip`: `bot/handlers/admin.py:4217`
- `aw_confirm`: `bot/handlers/admin.py:3813`
- `back:main`: `bot/handlers/admin.py:5132`
- `bank:balance`: `bot/handlers/bank.py:72`
- `bank:menu`: `bot/handlers/bank.py:191`
- `bank:noop`: `bot/handlers/bank.py:453`
- `bank:transfer`: `bot/handlers/bank.py:131`
- `bank:transfer_manual`: `bot/handlers/bank.py:147`
- `bank:treasury`: `bot/handlers/bank.py:204`
- `booklet:claim`: `bot/handlers/tourist_booklet.py:71`
- `booklet:menu`: `bot/handlers/tourist_booklet.py:65`
- `cancel`: `bot/handlers/admin.py:5140`
- `city:business`: `bot/handlers/locations.py:247`
- `city:clans`: `bot/handlers/clans.py:92`
- `city:countryside`: `bot/handlers/locations.py:267`
- `city:dungeon`: `bot/handlers/dungeon.py:942`
- `city:library`: `bot/handlers/library.py:82`
- `city:menu`: `bot/handlers/start.py:170`
- `city:pilots`: `bot/handlers/pilots.py:102`
- `city:pilots:list`: `bot/handlers/pilots.py:129`
- `city:quarter`: `bot/handlers/locations.py:229`
- `city:vote`: `bot/handlers/polls.py:70`
- `clanh:noop`: `bot/handlers/clan_hall.py:2406`
- `clanhph:construction`: `bot/handlers/admin_clanphotos.py:172`
- `clanhph:menu`: `bot/handlers/admin_clanphotos.py:114`
- `clans:create_skip`: `bot/handlers/clans.py:791`
- `clans:noop`: `bot/handlers/clans.py:576`
- `clanshopadm:menu`: `bot/handlers/admin_shop_clan.py:103`
- `contracts:list`: `bot/handlers/dungeon.py:754`
- `del_item:back`: `bot/handlers/admin.py:1700`
- `duel:card:buy`: `bot/handlers/duel.py:246`
- `duel:help`: `bot/handlers/duel.py:224`
- `duel:list`: `bot/handlers/duel.py:272`
- `duel:menu`: `bot/handlers/duel.py:218`
- `duel:top`: `bot/handlers/duel.py:292`
- `dungeon:enemies`: `bot/handlers/admin.py:5738`
- `dungeon:exit`: `bot/handlers/dungeon.py:2605`
- `dungeon:exit:cancel`: `bot/handlers/dungeon.py:2690`
- `dungeon:exit:confirm`: `bot/handlers/dungeon.py:2652`
- `dungeon:photos`: `bot/handlers/admin.py:5505`
- `dungeon:photos:clear`: `bot/handlers/admin.py:5549`
- `enemy:fi`: `bot/handlers/admin.py:9384`
- `field:drink`: `bot/handlers/admin.py:1971`
- `field:loot_only`: `bot/handlers/admin.py:2035`
- `field:market_ok`: `bot/handlers/admin.py:2015`
- `field:photo`: `bot/handlers/admin.py:1892`
- `field:weapon_effect`: `bot/handlers/admin.py:1912`
- `fin:manual`: `bot/handlers/admin.py:2542`
- `finh:open`: `bot/handlers/admin.py:2734`
- `fireevent:enter`: `bot/handlers/fire_event.py:563`
- `fireevent:potioncancel`: `bot/handlers/fire_event.py:993`
- `fireph:menu`: `bot/handlers/admin_firephotos.py:73`
- `fish:recover`: `bot/handlers/fishing.py:500`
- `forest:addlist`: `bot/handlers/admin.py:7834`
- `forest:new`: `bot/handlers/admin.py:7987`
- `forest:zset:sold_daily_limit`: `bot/handlers/admin.py:7673`
- `housing:menu`: `bot/handlers/housing.py:284`
- `housing:noop`: `bot/handlers/housing.py:854`
- `housing:pay_debt`: `bot/handlers/housing.py:329`
- `housing:pay_tax`: `bot/handlers/housing.py:320`
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
- `loc:building_pick`: `bot/handlers/admin.py:8165`
- `loc:city_fire`: `bot/handlers/admin.py:8741`
- `loc:clearing_clear`: `bot/handlers/admin.py:8875`
- `loc:clearing_set`: `bot/handlers/admin.py:8838`
- `loc:create`: `bot/handlers/admin.py:8133`
- `loc:edit_pick`: `bot/handlers/admin.py:8149`
- `loc:fire_set`: `bot/handlers/admin.py:8788`
- `loc:glade_clear`: `bot/handlers/admin.py:8825`
- `loc:glade_set`: `bot/handlers/admin.py:8703`
- `loc:logging_clear`: `bot/handlers/admin.py:8927`
- `loc:logging_set`: `bot/handlers/admin.py:8888`
- `loc:mine_clear`: `bot/handlers/admin.py:8978`
- `loc:mine_set`: `bot/handlers/admin.py:8940`
- `loc:photos`: `bot/handlers/admin.py:8629`
- `loc:photos:clear`: `bot/handlers/admin.py:9120`
- `loc:photos:clear_seasons`: `bot/handlers/admin.py:8652`
- `loc:set_blocking`: `bot/handlers/admin.py:8302`
- `loc:set_desc`: `bot/handlers/admin.py:8459`
- `loc:set_mode`: `bot/handlers/admin.py:8231`
- `loc:set_name`: `bot/handlers/admin.py:8420`
- `loc:set_status`: `bot/handlers/admin.py:8274`
- `loc:storage_clear`: `bot/handlers/admin.py:9029`
- `loc:storage_set`: `bot/handlers/admin.py:8991`
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
- `noop`: `bot/handlers/admin.py:5127`
- `park:admin`: `bot/handlers/park.py:274`
- `park:admin:add`: `bot/handlers/park.py:289`
- `park:admin:editlist`: `bot/handlers/park.py:463`
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
- `rep:auto_approve_edit`: `bot/handlers/admin.py:4380`
- `rep:next`: `bot/handlers/admin.py:4822`
- `rep:pay_cap_edit`: `bot/handlers/admin.py:4419`
- `rep:speech`: `bot/handlers/representative.py:77`
- `rep:speech:delete`: `bot/handlers/representative.py:109`
- `rep:speech:write`: `bot/handlers/representative.py:89`
- `report:menu`: `bot/handlers/reports.py:47`
- `report:my_reports`: `bot/handlers/reports.py:395`
- `report:submit`: `bot/handlers/reports.py:57`
- `resv:recover`: `bot/handlers/dungeon.py:2408`
- `salary:choose`: `bot/handlers/admin.py:5324`
- `salary:pay`: `bot/handlers/admin.py:5336`
- `shop:catalog`: `bot/handlers/shop.py:230`
- `shop_admin:add`: `bot/handlers/admin.py:1211`
- `shop_admin:delete`: `bot/handlers/admin.py:1671`
- `shop_admin:edit`: `bot/handlers/admin.py:1794`
- `shop_admin:special_code`: `bot/handlers/admin.py:2499`
- `shop_del:cats`: `bot/handlers/admin.py:1788`
- `shop_edit:cats`: `bot/handlers/admin.py:1773`
- `st:create`: `bot/handlers/admin.py:3179`
- `st:delete`: `bot/handlers/admin.py:3252`
- `st:grant`: `bot/handlers/admin.py:3455`
- `st:legioner`: `bot/handlers/admin.py:3400`
- `st:list`: `bot/handlers/admin.py:3162`
- `st:more`: `bot/handlers/admin.py:3601`
- `st:revoke`: `bot/handlers/admin.py:3521`
- `storage:cats`: `bot/handlers/admin.py:965`
- `storage:create`: `bot/handlers/admin.py:1212`
- `storage:menu`: `bot/handlers/storage.py:89`
- `storage:noop`: `bot/handlers/admin.py:960`
- `treasury:debts`: `bot/handlers/admin.py:2267`
- `treasury:give`: `bot/handlers/admin.py:2366`
- `treasury:stats`: `bot/handlers/admin.py:2314`
- `vote:close_cancel`: `bot/handlers/polls.py:332`
- `vote:create`: `bot/handlers/polls.py:224`
- `wall:archive`: `bot/handlers/wall.py:315`
- `wall:view`: `bot/handlers/wall.py:149`
- `wall:write`: `bot/handlers/wall.py:170`

### По префиксу (`F.data.startswith("...")`)

- `\d+$`: `bot/handlers/admin.py:1363`; `bot/handlers/admin.py:5240`; `bot/handlers/admin.py:7687`; `bot/handlers/reports.py:201`
- `\d{1,7}$`: `bot/handlers/reports.py:135`; `bot/handlers/reports.py:165`
- `act:`: `bot/handlers/admin.py:5034`
- `addreq:`: `bot/handlers/admin.py:1562`
- `aw_del:`: `bot/handlers/admin.py:3858`
- `aw_edit:`: `bot/handlers/admin.py:4041`
- `aw_ei:`: `bot/handlers/admin.py:4052`
- `aw_kind:`: `bot/handlers/admin.py:4150`
- `aw_pick:`: `bot/handlers/admin.py:4201`
- `awr_grant:`: `bot/handlers/admin.py:4268`
- `bait:set:`: `bot/handlers/fishing.py:176`
- `bank:history`: `bot/handlers/bank.py:403`
- `bank:pickrecipient:`: `bot/handlers/bank.py:177`
- `bank:transfer:list:`: `bot/handlers/bank.py:137`
- `buy5_nord:`: `bot/handlers/shop.py:493`
- `buy_housing:`: `bot/handlers/shop.py:1109`
- `buy_housing_cancel:`: `bot/handlers/shop.py:1100`
- `buy_nord:`: `bot/handlers/shop.py:483`
- `cat:`: `bot/handlers/admin.py:1284`
- `city/`: `bot/handlers/locations.py:91`
- `city:pilots:list:`: `bot/handlers/pilots.py:135`
- `clanh:admconstphoto:`: `bot/handlers/clan_hall.py:2159`
- `clanh:admexphoto:`: `bot/handlers/clan_hall.py:2202`
- `clanh:admnophoto:`: `bot/handlers/clan_hall.py:2145`
- `clanh:admphoto:`: `bot/handlers/clan_hall.py:2127`
- `clanh:bitem:`: `bot/handlers/clan_hall.py:1218`
- `clanh:buy:`: `bot/handlers/clan_hall.py:1261`
- `clanh:cancel:`: `bot/handlers/clan_hall.py:1993`
- `clanh:choose:`: `bot/handlers/clan_hall.py:1962`
- `clanh:craft:`: `bot/handlers/clan_hall.py:1584`
- `clanh:donate:`: `bot/handlers/clan_hall.py:2276`
- `clanh:expchoose:`: `bot/handlers/clan_hall.py:1451`
- `clanh:expinstall:`: `bot/handlers/clan_hall.py:1464`
- `clanh:expmanage:`: `bot/handlers/clan_hall.py:1440`
- `clanh:expup:`: `bot/handlers/clan_hall.py:1482`
- `clanh:give:`: `bot/handlers/clan_hall.py:2333`
- `clanh:hall:`: `bot/handlers/clan_hall.py:1942`
- `clanh:harvest:`: `bot/handlers/clan_hall.py:1879`
- `clanh:harvestall:`: `bot/handlers/clan_hall.py:1911`
- `clanh:inside:`: `bot/handlers/clan_hall.py:2069`
- `clanh:item:`: `bot/handlers/clan_hall.py:2302`
- `clanh:libgive:`: `bot/handlers/clan_hall.py:1324`
- `clanh:log:`: `bot/handlers/clan_hall.py:2391`
- `clanh:mushproc:`: `bot/handlers/clan_hall.py:1736`
- `clanh:mushrooms:`: `bot/handlers/clan_hall.py:1719`
- `clanh:plant:`: `bot/handlers/clan_hall.py:1855`
- `clanh:plantlist:`: `bot/handlers/clan_hall.py:1807`
- `clanh:recipe:`: `bot/handlers/clan_hall.py:1515`
- `clanh:shower:`: `bot/handlers/clan_hall.py:1771`
- `clanh:start:`: `bot/handlers/clan_hall.py:2007`
- `clanh:startfull:`: `bot/handlers/clan_hall.py:2036`
- `clanh:storage:`: `bot/handlers/clan_hall.py:2255`
- `clanh:tree_essence:`: `bot/handlers/clan_hall.py:1103`
- `clanh:tree_essence_inv:`: `bot/handlers/clan_hall.py:1138`
- `clanh:tree_essence_store:`: `bot/handlers/clan_hall.py:1166`
- `clanh:tree_medit:`: `bot/handlers/clan_hall.py:1087`
- `clanh:upgrade:`: `bot/handlers/clan_hall.py:1978`
- `clanh:use:`: `bot/handlers/clan_hall.py:1498`
- `clanhier:`: `bot/handlers/clans.py:286`
- `clanhph:bclan:`: `bot/handlers/admin_clanphotos.py:247`
- `clanhph:buildings`: `bot/handlers/admin_clanphotos.py:208`
- `clanhph:exp:`: `bot/handlers/admin_clanphotos.py:123`
- `clans:add:`: `bot/handlers/clans.py:581`
- `clans:addset:`: `bot/handlers/clans.py:598`
- `clans:cancel:`: `bot/handlers/clans.py:397`
- `clans:create:`: `bot/handlers/clans.py:693`
- `clans:del:`: `bot/handlers/clans.py:945`
- `clans:delyes:`: `bot/handlers/clans.py:962`
- `clans:edit:`: `bot/handlers/clans.py:806`
- `clans:editf:`: `bot/handlers/clans.py:830`
- `clans:join:`: `bot/handlers/clans.py:360`
- `clans:kick:`: `bot/handlers/clans.py:531`
- `clans:leader:`: `bot/handlers/clans.py:622`
- `clans:leaderset:`: `bot/handlers/clans.py:639`
- `clans:leaderunset:`: `bot/handlers/clans.py:669`
- `clans:leave:`: `bot/handlers/clans.py:407`
- `clans:list:`: `bot/handlers/clans.py:132`
- `clans:manage:`: `bot/handlers/clans.py:475`
- `clans:msg:`: `bot/handlers/clans.py:900`
- `clans:reqno:`: `bot/handlers/clans.py:458`
- `clans:reqok:`: `bot/handlers/clans.py:434`
- `clans:view:`: `bot/handlers/clans.py:169`
- `clanshopadm:add:`: `bot/handlers/admin_shop_clan.py:134`
- `clanshopadm:clan:`: `bot/handlers/admin_shop_clan.py:121`
- `clanshopadm:del:`: `bot/handlers/admin_shop_clan.py:397`
- `clanshopadm:ep:`: `bot/handlers/admin_shop_clan.py:298`
- `clanshopadm:es:`: `bot/handlers/admin_shop_clan.py:332`
- `clanshopadm:hide:`: `bot/handlers/admin_shop_clan.py:369`
- `clanshopadm:it:`: `bot/handlers/admin_shop_clan.py:257`
- `clanshopadm:show:`: `bot/handlers/admin_shop_clan.py:383`
- `confirm_del_photo:`: `bot/handlers/admin.py:850`
- `contract:enter:\d+$`: `bot/handlers/dungeon.py:834`
- `contract:enter:confirm:`: `bot/handlers/dungeon.py:880`
- `contract:pick:`: `bot/handlers/dungeon.py:782`
- `del_item:`: `bot/handlers/admin.py:1685`
- `drinksel:`: `bot/handlers/admin.py:1317`
- `duel:accept:`: `bot/handlers/duel.py:399`
- `duel:atk:`: `bot/handlers/duel.py:529`
- `duel:cancel:`: `bot/handlers/duel.py:373`
- `duel:decline:`: `bot/handlers/duel.py:385`
- `duel:def:`: `bot/handlers/duel.py:545`
- `duel:invite:`: `bot/handlers/duel.py:310`
- `duel:leave:`: `bot/handlers/duel.py:448`
- `dungeon:attack:`: `bot/handlers/dungeon.py:1386`
- `dungeon:continue:`: `bot/handlers/dungeon.py:1187`
- `dungeon:edit:`: `bot/handlers/admin.py:5442`
- `dungeon:enemy:`: `bot/handlers/admin.py:5770`
- `dungeon:escape:`: `bot/handlers/dungeon.py:2015`
- `dungeon:photo_set:`: `bot/handlers/admin.py:5514`
- `dungeon:use_slot:`: `bot/handlers/dungeon.py:1698`
- `eddrop:`: `bot/handlers/admin.py:6363`
- `eddrop_del:`: `bot/handlers/admin.py:6449`
- `eddrop_desc:`: `bot/handlers/admin.py:6521`
- `eddrop_photo:`: `bot/handlers/admin.py:6467`
- `eddrop_set_ch:`: `bot/handlers/admin.py:6404`
- `eddrop_set_q:`: `bot/handlers/admin.py:6427`
- `eddrop_stat:`: `bot/handlers/admin.py:6616`
- `eddrop_stats:`: `bot/handlers/admin.py:6577`
- `eddrop_weff:`: `bot/handlers/admin.py:6679`
- `eddrop_weff_set:`: `bot/handlers/admin.py:6701`
- `edit_item:`: `bot/handlers/admin.py:1803`
- `editem_add:`: `bot/handlers/admin.py:6315`
- `editem_new:`: `bot/handlers/admin.py:6340`
- `editem_pick:`: `bot/handlers/admin.py:6270`
- `editset:drink:`: `bot/handlers/admin.py:1994`
- `editset:weff:`: `bot/handlers/admin.py:1928`
- `enemy:card:`: `bot/handlers/admin.py:9519`
- `enemy:dcard:`: `bot/handlers/admin.py:9446`
- `enemy:del:`: `bot/handlers/admin.py:9645`
- `enemy:dn:\d+$`: `bot/handlers/admin.py:9356`
- `enemy:dropadd:`: `bot/handlers/admin.py:9822`
- `enemy:dropch:`: `bot/handlers/admin.py:9749`
- `enemy:dropdel:`: `bot/handlers/admin.py:9775`
- `enemy:dropedit:`: `bot/handlers/admin.py:9711`
- `enemy:dropitem:`: `bot/handlers/admin.py:9787`
- `enemy:dropq:`: `bot/handlers/admin.py:9762`
- `enemy:drops:`: `bot/handlers/admin.py:9701`
- `enemy:effects:\d+$`: `bot/handlers/admin.py:6032`
- `enemy:fld:`: `bot/handlers/admin.py:9529`
- `enemy:fx:src:`: `bot/handlers/admin.py:6105`
- `enemy:fx:tog:\d+:\d+$`: `bot/handlers/admin.py:6051`
- `enemy:fxt:`: `bot/handlers/admin.py:6125`
- `enemy:list:[a-z]+:[\w-]+$`: `bot/handlers/admin.py:9404`
- `enemy:new:`: `bot/handlers/admin.py:9896`
- `enemy:photo:`: `bot/handlers/admin.py:9589`
- `enemy:tog:`: `bot/handlers/admin.py:9626`
- `enemy_drops:`: `bot/handlers/admin.py:6257`
- `enemy_field:`: `bot/handlers/admin.py:5783`
- `eqequip:[a-z0-9_]+:\d+$`: `bot/handlers/inventory.py:500`
- `eqlock:[a-z0-9_]+$`: `bot/handlers/inventory.py:488`
- `eqpart:`: `bot/handlers/admin.py:1395`
- `eqslot:[a-z0-9_]+$`: `bot/handlers/inventory.py:493`
- `equnequip:[a-z0-9_]+$`: `bot/handlers/inventory.py:532`
- `field:`: `bot/handlers/admin.py:2099`
- `field:required_status`: `bot/handlers/admin.py:1842`
- `field_req:`: `bot/handlers/admin.py:1875`
- `fin:`: `bot/handlers/admin.py:2555`
- `finh:h:`: `bot/handlers/admin.py:2769`
- `finh:list:`: `bot/handlers/admin.py:2745`
- `finh:u:`: `bot/handlers/admin.py:2757`
- `finuser:`: `bot/handlers/admin.py:2630`
- `fireevent:attack:`: `bot/handlers/fire_event.py:784`
- `fireevent:cont:`: `bot/handlers/fire_event.py:366`
- `fireevent:fishing:`: `bot/handlers/fire_event.py:426`
- `fireevent:leave:`: `bot/handlers/fire_event.py:538`
- `fireevent:potion:`: `bot/handlers/fire_event.py:894`
- `fireevent:potionok:`: `bot/handlers/fire_event.py:987`
- `fireevent:step:`: `bot/handlers/fire_event.py:287`
- `fireph:set:`: `bot/handlers/admin_firephotos.py:82`
- `fish:bait:\d+$`: `bot/handlers/fishing.py:514`
- `fish:bait:set:\d+:[a-z]+$`: `bot/handlers/fishing.py:556`
- `fish:cast:\d+$`: `bot/handlers/fishing.py:566`
- `fish:lake:\d+$`: `bot/handlers/fishing.py:493`
- `fishbuy:`: `bot/handlers/shop.py:822`
- `fishcatch:`: `bot/handlers/inventory.py:1285`
- `fishgo:`: `bot/handlers/inventory.py:1536`
- `fishing:addfish:`: `bot/handlers/admin.py:7108`
- `fishing:addlist:`: `bot/handlers/admin.py:7078`
- `fishing:del:`: `bot/handlers/admin.py:7131`
- `fishing:fish:`: `bot/handlers/admin.py:6998`
- `fishing:junk:`: `bot/handlers/admin.py:6853`
- `fishing:kind:`: `bot/handlers/admin.py:7012`
- `fishing:market:`: `bot/handlers/admin.py:7034`
- `fishing:new:`: `bot/handlers/admin.py:7156`
- `fishing:new_super:`: `bot/handlers/admin.py:7259`
- `fishing:super:`: `bot/handlers/admin.py:7056`
- `fishing:water:`: `bot/handlers/admin.py:6960`
- `fishing_field:`: `bot/handlers/admin.py:7318`
- `fishing_j:`: `bot/handlers/admin.py:6903`
- `fishmarket:`: `bot/handlers/inventory.py:1438`
- `fishoffer:`: `bot/handlers/shop.py:747`
- `fishprice:`: `bot/handlers/inventory.py:1518`
- `fishsell:`: `bot/handlers/inventory.py:1594`
- `fishuse:`: `bot/handlers/inventory.py:1293`
- `forest:add:`: `bot/handlers/admin.py:7859`
- `forest:area:\d+:(glade|clearing)$`: `bot/handlers/forest.py:426`
- `forest:battle:flee:\d+$`: `bot/handlers/forest.py:1070`
- `forest:battle:hit:\d+$`: `bot/handlers/forest.py:863`
- `forest:card:`: `bot/handlers/admin.py:7773`
- `forest:cast:\d+(?::(glade|clearing))?$`: `bot/handlers/forest.py:500`
- `forest:del:`: `bot/handlers/admin.py:7878`
- `forest:kind:`: `bot/handlers/admin.py:7787`
- `forest:market:`: `bot/handlers/admin.py:7812`
- `forest:new_kind:`: `bot/handlers/admin.py:8067`
- `forest:zadd:(glade|clearing):\d+$`: `bot/handlers/admin.py:7639`
- `forest:zaddlist:(glade|clearing)$`: `bot/handlers/admin.py:7612`
- `forest:zchance:(glade|clearing):\d+$`: `bot/handlers/admin.py:7585`
- `forest:zdel:(glade|clearing):\d+$`: `bot/handlers/admin.py:7600`
- `forest:zone:(glade|clearing)$`: `bot/handlers/admin.py:7513`
- `forest:zset:(glade|clearing):(\w+)$`: `bot/handlers/admin.py:7651`
- `forest_field:`: `bot/handlers/admin.py:7899`
- `housing:craft:`: `bot/handlers/housing.py:795`
- `housing:harvest:`: `bot/handlers/housing.py:1127`
- `housing:install:`: `bot/handlers/housing.py:861`
- `housing:install_item:`: `bot/handlers/housing.py:899`
- `housing:kitchen:`: `bot/handlers/housing.py:398`
- `housing:lantern_medit:`: `bot/handlers/housing.py:666`
- `housing:move:`: `bot/handlers/housing.py:1148`
- `housing:mushproc:`: `bot/handlers/housing.py:508`
- `housing:mushrooms:`: `bot/handlers/housing.py:494`
- `housing:plant:`: `bot/handlers/housing.py:1106`
- `housing:recipe:`: `bot/handlers/housing.py:750`
- `housing:room:`: `bot/handlers/housing.py:340`
- `housing:shower:`: `bot/handlers/housing.py:591`
- `housing:uninstall:`: `bot/handlers/housing.py:1006`
- `housing:uninstall_confirm:`: `bot/handlers/housing.py:1072`
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
- `inv_equip:`: `bot/handlers/inventory.py:791`
- `inv_sell:`: `bot/handlers/inventory.py:926`
- `inv_sell_keep1:`: `bot/handlers/inventory.py:946`
- `inv_sell_ok:`: `bot/handlers/inventory.py:1021`
- `inv_sellall:`: `bot/handlers/inventory.py:936`
- `inv_sellmore:`: `bot/handlers/inventory.py:1131`
- `inv_slot:`: `bot/handlers/inventory.py:845`
- `inv_transfer:`: `bot/handlers/inventory.py:1626`
- `inv_unequip:`: `bot/handlers/inventory.py:821`
- `inv_unslot:`: `bot/handlers/inventory.py:880`
- `inv_use:`: `bot/handlers/inventory.py:902`
- `inventory:cat:[^:]+$`: `bot/handlers/inventory.py:592`
- `invitem:`: `bot/handlers/inventory.py:784`
- `itembuy:`: `bot/handlers/shop.py:946`
- `itemgo:`: `bot/handlers/inventory.py:1229`
- `itemmarket:`: `bot/handlers/inventory.py:1139`
- `itemoffer:`: `bot/handlers/shop.py:878`
- `itemprice:`: `bot/handlers/inventory.py:1218`
- `kvp:attack:`: `bot/handlers/kvp.py:514`
- `kvp:attempt:`: `bot/handlers/kvp.py:440`
- `kvp:continue:`: `bot/handlers/kvp.py:410`
- `libadmin_del:`: `bot/handlers/library.py:409`
- `libadmin_sec:`: `bot/handlers/library.py:297`
- `libbook:`: `bot/handlers/library.py:204`
- `libdl:`: `bot/handlers/library.py:249`
- `libsec:[a-z]+$`: `bot/handlers/library.py:178`
- `loc:blocking:`: `bot/handlers/admin.py:8318`
- `loc:building:`: `bot/handlers/admin.py:8207`
- `loc:edit:`: `bot/handlers/admin.py:8181`
- `loc:mode:`: `bot/handlers/admin.py:8247`
- `loc:photo_set:`: `bot/handlers/admin.py:9042`
- `loc:req_status:`: `bot/handlers/admin.py:8283`
- `loc:season:(winter|spring|summer|autumn)$`: `bot/handlers/admin.py:8639`
- `loc:season_clear:(winter|spring|summer|autumn)$`: `bot/handlers/admin.py:8665`
- `loc:season_photo_set:(winter|spring|summer|autumn):(dawn|day|sunset|night)$`: `bot/handlers/admin.py:9079`
- `location:enter:`: `bot/handlers/locations.py:111`
- `location:preview:`: `bot/handlers/locations.py:40`
- `locstat:`: `bot/handlers/admin.py:5093`
- `logsite:battle:flee:\d+$`: `bot/handlers/logging_site.py:1096`
- `logsite:battle:hit:\d+$`: `bot/handlers/logging_site.py:893`
- `logsite:chop:\d+$`: `bot/handlers/logging_site.py:468`
- `logsite:fire:(1|all):\d+$`: `bot/handlers/logging_site.py:742`
- `logsite:menu:\d+$`: `bot/handlers/logging_site.py:453`
- `logsite:mill:\d+$`: `bot/handlers/logging_site.py:616`
- `logsite:plank:(1|all):\d+$`: `bot/handlers/logging_site.py:679`
- `lootonly:`: `bot/handlers/admin.py:1537`
- `marketok:`: `bot/handlers/admin.py:1515`
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
- `news:(?:off|(?:dis)?allow:-?\d+|chat:-?\d+:-?\d+|topic:-?\d+:-?\d+)$`: `bot/handlers/admin.py:3064`
- `news:arch:\d+$`: `bot/handlers/news.py:179`
- `news:del:`: `bot/handlers/news.py:473`
- `news:delconf:`: `bot/handlers/news.py:495`
- `news:edit:`: `bot/handlers/news.py:400`
- `news:view:`: `bot/handlers/news.py:196`
- `nii:set:`: `bot/handlers/nii.py:319`
- `nii:view:`: `bot/handlers/nii.py:284`
- `offercancel:fish:`: `bot/handlers/shop.py:992`
- `offercancel:item:`: `bot/handlers/shop.py:997`
- `page`: `bot/handlers/admin.py:415`
- `park:admin:del:`: `bot/handlers/park.py:390`
- `park:admin:delyes:`: `bot/handlers/park.py:410`
- `park:admin:edit:`: `bot/handlers/park.py:478`
- `park:adminedit:f:`: `bot/handlers/park.py:496`
- `park:statue:`: `bot/handlers/park.py:257`
- `pickuser:`: `bot/handlers/admin.py:406`
- `pollarch:day:\d{4}-\d{2}-\d{2}(?::\d+)?$`: `bot/handlers/poll_archive.py:176`
- `pollarch:days:\d+$`: `bot/handlers/poll_archive.py:154`
- `prod:`: `bot/handlers/admin.py:1475`
- `prof_sel_status:`: `bot/handlers/profile.py:327`
- `profile:award:`: `bot/handlers/profile.py:550`
- `rank_pick:`: `bot/handlers/admin.py:4926`
- `rank_promote:`: `bot/handlers/admin.py:4885`
- `rar:`: `bot/handlers/admin.py:1275`
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
- `rep:nav:`: `bot/handlers/admin.py:4811`
- `rep_fix:`: `bot/handlers/admin.py:4610`
- `rep_no:`: `bot/handlers/admin.py:4796`
- `rep_ok:`: `bot/handlers/admin.py:4727`
- `report:my:`: `bot/handlers/reports.py:390`
- `report:view:`: `bot/handlers/reports.py:402`
- `resv:bait:\d+$`: `bot/handlers/dungeon.py:2135`
- `resv:bait:set:\d+:[a-z]+$`: `bot/handlers/dungeon.py:2183`
- `resv:cast:\d+$`: `bot/handlers/dungeon.py:2202`
- `resv:deeper:\d+$`: `bot/handlers/dungeon.py:2439`
- `resv:enter:\d+$`: `bot/handlers/dungeon.py:2097`
- `resv:eq:\d+$`: `bot/handlers/dungeon.py:2474`
- `resv:eqclear:[a-z0-9_]+:\d+$`: `bot/handlers/dungeon.py:2582`
- `resv:eqset:[a-z0-9_]+:\d+:\d+$`: `bot/handlers/dungeon.py:2558`
- `resv:eqslot:[a-z0-9_]+:\d+$`: `bot/handlers/dungeon.py:2512`
- `resv:menu:\d+$`: `bot/handlers/dungeon.py:2121`
- `role:`: `bot/handlers/admin.py:2977`
- `rolop:`: `bot/handlers/admin.py:2928`
- `shop_del:cat:`: `bot/handlers/admin.py:1779`
- `shop_edit:cat:`: `bot/handlers/admin.py:1764`
- `shopcat:[^:]+$`: `bot/handlers/shop.py:250`
- `shopcat:[^:]+:\d+$`: `bot/handlers/shop.py:338`
- `shopitem:`: `bot/handlers/shop.py:349`
- `st_del:`: `bot/handlers/admin.py:3271`
- `st_key:`: `bot/handlers/admin.py:5225`
- `st_op:`: `bot/handlers/admin.py:5192`
- `st_pick:`: `bot/handlers/admin.py:3556`
- `st_rev:`: `bot/handlers/admin.py:3486`
- `storage:cat:`: `bot/handlers/admin.py:978`
- `storage:item:`: `bot/handlers/admin.py:1011`
- `storage:page:`: `bot/handlers/admin.py:997`
- `storage:purge:`: `bot/handlers/admin.py:1137`
- `storage:restock:`: `bot/handlers/admin.py:1069`
- `toggle:`: `bot/handlers/admin.py:8323`
- `vote:cast:`: `bot/handlers/polls.py:163`
- `vote:close:`: `bot/handlers/polls.py:287`
- `vote:close_confirm:`: `bot/handlers/polls.py:310`
- `vote:results:`: `bot/handlers/polls.py:185`
- `vote:show:`: `bot/handlers/polls.py:109`
- `wall:archpage:\d+$`: `bot/handlers/wall.py:338`
- `wall:archread:\d+(?::\d+)?$`: `bot/handlers/wall.py:357`
- `wall:delete:\d+$`: `bot/handlers/wall.py:224`
- `wall:page:\d+$`: `bot/handlers/wall.py:156`
- `weff:`: `bot/handlers/admin.py:1408`
- `wing_set:`: `bot/handlers/admin.py:825`
- `Испорченный`: `bot/handlers/dungeon.py:1918`
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

