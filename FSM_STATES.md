# Карта FSM-состояний и callback-неймспейсов N.O.R.D.

> **Сгенерировано** `tools/export_states.py`. Не редактировать вручную —
> правь код и перегенерируй: `.venv\Scripts\python.exe tools/export_states.py`.
>
> Назначение: единый обзор всех `StatesGroup`, где они ставятся и где ловятся,
> а также реестр `callback_data` — чтобы не допускать конфликтов меню/хендлеров.

Всего классов состояний: **48**; полей-состояний: **209**; уникальных `callback_data`: **241**.

## 1. Классы состояний по модулям

### `AdminAddItem` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `name` | `bot/handlers/admin.py:1208` `shop_admin_add`<br>`bot/handlers/admin.py:5836` `enemy_drop_new_item` | `bot/handlers/admin.py:1216` `add_item_name` |
| `desc` | `bot/handlers/admin.py:1218` `add_item_name` | `bot/handlers/admin.py:1224` `add_item_desc` |
| `price` | `bot/handlers/admin.py:1227` `add_item_desc` | `bot/handlers/admin.py:1233` `add_item_price` |
| `sell_price` | `bot/handlers/admin.py:1243` `add_item_price` | `bot/handlers/admin.py:1249` `add_item_sell_price` |
| `rarity` | `bot/handlers/admin.py:1261` `add_item_sell_price` | — |
| `category` | `bot/handlers/admin.py:1270` `add_item_rarity` | — |
| `drink` | `bot/handlers/admin.py:1293` `add_item_category` | — |
| `plant_name` | `bot/handlers/admin.py:1282` `add_item_category` | `bot/handlers/admin.py:1318` `add_item_plant_name` |
| `stock` | `bot/handlers/admin.py:1302` `add_item_category`<br>`bot/handlers/admin.py:1312` `add_item_drink_choice`<br>`bot/handlers/admin.py:1321` `add_item_plant_name` | `bot/handlers/admin.py:1327` `add_item_stock` |
| `stats` | `bot/handlers/admin.py:1341` `add_item_stock`<br>`bot/handlers/admin.py:1346` `add_item_stock` | `bot/handlers/admin.py:1354` `add_item_stats`<br>`bot/handlers/admin.py:1394` `add_item_stats_bad` |
| `equip_slot` | `bot/handlers/admin.py:1371` `add_item_stats` | — |
| `weapon_effect` | `bot/handlers/admin.py:1359` `add_item_stats` | — |
| `weapon_effect_chance` | `bot/handlers/admin.py:1407` `add_item_weapon_effect_cb` | `bot/handlers/admin.py:1416` `add_item_weapon_effect_chance` |
| `weapon_effect_dmg` | `bot/handlers/admin.py:1428` `add_item_weapon_effect_chance` | `bot/handlers/admin.py:1440` `add_item_weapon_effect_dmg` |
| `producer` | `bot/handlers/admin.py:1455` `_go_add_item_producer` | — |
| `producer_user` | `bot/handlers/admin.py:1470` `add_item_producer` | `bot/handlers/admin.py:1482` `add_item_producer_user` |
| `market` | `bot/handlers/admin.py:1493` `_go_add_item_market` | — |
| `loot` | `bot/handlers/admin.py:1515` `_go_add_item_loot` | — |
| `status` | `bot/handlers/admin.py:1543` `_go_add_item_status` | — |
| `photo` | `bot/handlers/admin.py:1562` `add_item_status_cb` | `bot/handlers/admin.py:1570` `add_item_photo` |

### `AdminSaleTax` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `percent` | `bot/handlers/admin.py:2452` `admin_saletax_view` | `bot/handlers/admin.py:2466` `admin_saletax_set` |

### `AdminSpecialCode` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `code` | `bot/handlers/admin.py:2494` `admin_special_code_view` | `bot/handlers/admin.py:2509` `admin_special_code_set` |

### `AdminEditItem` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `item_id` | — | — |
| `field` | `bot/handlers/admin.py:1798` `edit_item_pick` | — |
| `value` | `bot/handlers/admin.py:2102` `edit_item_field` | `bot/handlers/admin.py:2113` `edit_item_value` |
| `photo` | `bot/handlers/admin.py:1887` `edit_item_field_photo` | `bot/handlers/admin.py:1937` `edit_item_photo` |

### `AdminFinance` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | `bot/handlers/admin.py:2532` `finance_manual`<br>`bot/handlers/admin.py:2549` `finance_pick` | `bot/handlers/admin.py:2610` `finance_target` |
| `currency` | — | — |
| `amount` | `bot/handlers/admin.py:445` `pickuser_cb`<br>`bot/handlers/admin.py:2579` `finance_pick_user`<br>`bot/handlers/admin.py:2617` `finance_target` | `bot/handlers/admin.py:2625` `finance_amount` |

### `AdminTreasury` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `amount` | `bot/handlers/admin.py:2359` `treasury_give` | `bot/handlers/admin.py:2369` `treasury_amount` |
| `target` | `bot/handlers/admin.py:2385` `treasury_amount` | `bot/handlers/admin.py:2391` `treasury_target_manual` |

### `AdminStorageRestock` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `amount` | `bot/handlers/admin.py:1070` `storage_restock` | `bot/handlers/admin.py:1084` `storage_restock_amount` |

### `AdminStorageDelete` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `confirm` | `bot/handlers/admin.py:1142` `storage_purge` | `bot/handlers/admin.py:1156` `storage_purge_confirm` |

### `AdminTax` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `percent` | `bot/handlers/admin.py:2415` `admin_tax_view` | `bot/handlers/admin.py:2427` `admin_tax_set` |

### `AdminReportAutoApprove` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `value` | `bot/handlers/admin.py:4106` `report_auto_approve_edit_cb` | `bot/handlers/admin.py:4119` `report_auto_approve_edit_value` |

### `AdminReportPayCap` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `value` | `bot/handlers/admin.py:4145` `report_pay_cap_edit_cb` | `bot/handlers/admin.py:4160` `report_pay_cap_edit_value` |

### `AdminReportFix` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `daily` | `bot/handlers/admin.py:4346` `report_fix_start` | `bot/handlers/admin.py:4359` `report_fix_daily` |
| `total` | `bot/handlers/admin.py:4373` `report_fix_daily` | `bot/handlers/admin.py:4387` `report_fix_total` |

### `AdminRoles` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | `bot/handlers/admin.py:2698` `admin_roles` | `bot/handlers/admin.py:2707` `roles_target` |
| `action` | `bot/handlers/admin.py:448` `pickuser_cb`<br>`bot/handlers/admin.py:2713` `roles_target` | — |
| `role` | `bot/handlers/admin.py:2731` `roles_action` | — |

### `AdminStatuses` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `name` | `bot/handlers/admin.py:2982` `status_create_start` | `bot/handlers/admin.py:2990` `status_create_name` |
| `tag` | `bot/handlers/admin.py:2992` `status_create_name` | `bot/handlers/admin.py:3001` `status_create_tag` |
| `level` | `bot/handlers/admin.py:3008` `status_create_tag` | `bot/handlers/admin.py:3018` `status_create_level` |
| `desc` | `bot/handlers/admin.py:3029` `status_create_level` | `bot/handlers/admin.py:3034` `status_create_desc` |
| `target` | `bot/handlers/admin.py:3255` `status_grant_target`<br>`bot/handlers/admin.py:3324` `status_revoke_target` | `bot/handlers/admin.py:3265` `status_grant_target_msg` |
| `grant_action` | — | — |
| `status_pick` | `bot/handlers/admin.py:463` `pickuser_cb`<br>`bot/handlers/admin.py:472` `pickuser_cb`<br>`bot/handlers/admin.py:3276` `status_grant_target_msg`<br>`bot/handlers/admin.py:3401` `status_grant_more` | — |
| `item_pick` | — | — |
| `item_status` | — | — |

### `AdminAwards` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `name` | `bot/handlers/admin.py:3458` `award_create_start` | `bot/handlers/admin.py:3515` `award_create_name` |
| `desc` | `bot/handlers/admin.py:3521` `award_create_name` | `bot/handlers/admin.py:3529` `award_create_desc` |
| `emoji` | `bot/handlers/admin.py:3532` `award_create_desc` | `bot/handlers/admin.py:3540` `award_create_emoji` |
| `bonus` | `bot/handlers/admin.py:3506` `_award_ask_bonus` | `bot/handlers/admin.py:3548` `award_create_bonus` |
| `preview` | `bot/handlers/admin.py:3494` `_award_ask_bonus` | — |
| `target` | `bot/handlers/admin.py:3895` `award_grant_target` | `bot/handlers/admin.py:3901` `award_grant_target_msg` |
| `award_pick` | `bot/handlers/admin.py:3986` `award_revoke_pick_user` | — |
| `comment` | `bot/handlers/admin.py:3929` `award_grant_pick` | `bot/handlers/admin.py:3946` `award_grant_comment` |
| `edit_value` | `bot/handlers/admin.py:3814` `award_edit_field_pick` | `bot/handlers/admin.py:3838` `award_edit_value` |

### `AdminFishing` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `water` | — | — |
| `wf_id` | — | — |
| `value` | `bot/handlers/admin.py:6397` `admin_fishing_junk_field_pick`<br>`bot/handlers/admin.py:6811` `admin_fishing_field_pick` | `bot/handlers/admin.py:6838` `admin_fishing_value` |
| `c_name` | `bot/handlers/admin.py:6648` `admin_fishing_new` | `bot/handlers/admin.py:6657` `admin_fishing_new_name` |
| `c_desc` | `bot/handlers/admin.py:6667` `admin_fishing_new_name` | `bot/handlers/admin.py:6673` `admin_fishing_new_desc` |
| `c_sell_price` | `bot/handlers/admin.py:6676` `admin_fishing_new_desc` | `bot/handlers/admin.py:6682` `admin_fishing_new_sell_price` |
| `c_day_weight` | `bot/handlers/admin.py:6690` `admin_fishing_new_sell_price` | `bot/handlers/admin.py:6698` `admin_fishing_new_day_weight` |
| `c_night_weight` | `bot/handlers/admin.py:6706` `admin_fishing_new_day_weight` | `bot/handlers/admin.py:6714` `admin_fishing_new_night_weight` |
| `c_photo` | `bot/handlers/admin.py:6746` `admin_fishing_new_super` | `bot/handlers/admin.py:6754` `admin_fishing_new_photo` |
| `c_super_rare` | `bot/handlers/admin.py:6722` `admin_fishing_new_night_weight` | — |

### `AdminForest` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `f_id` | — | — |
| `field` | — | — |
| `value` | `bot/handlers/admin.py:7393` `admin_forest_field_pick` | `bot/handlers/admin.py:7419` `admin_forest_value` |
| `c_name` | `bot/handlers/admin.py:7475` `admin_forest_new` | `bot/handlers/admin.py:7484` `admin_forest_new_name` |
| `c_desc` | `bot/handlers/admin.py:7494` `admin_forest_new_name` | `bot/handlers/admin.py:7500` `admin_forest_new_desc` |
| `c_sell_price` | `bot/handlers/admin.py:7503` `admin_forest_new_desc` | `bot/handlers/admin.py:7509` `admin_forest_new_sell_price` |
| `c_chance` | `bot/handlers/admin.py:7516` `admin_forest_new_sell_price` | `bot/handlers/admin.py:7525` `admin_forest_new_chance` |
| `c_kind` | `bot/handlers/admin.py:7533` `admin_forest_new_chance` | — |
| `c_photo` | `bot/handlers/admin.py:7556` `admin_forest_new_kind` | `bot/handlers/admin.py:7564` `admin_forest_new_photo` |
| `zone_value` | `bot/handlers/admin.py:7073` `admin_forest_zone_chance`<br>`bot/handlers/admin.py:7148` `admin_forest_zone_set_pick`<br>`bot/handlers/admin.py:7161` `admin_forest_limit_set` | `bot/handlers/admin.py:7168` `admin_forest_zone_value` |

### `AdminEnemy` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `field` | `bot/handlers/admin.py:8695` `admin_enemies_field_pick` | `bot/handlers/admin.py:8701` `admin_enemies_field_value` |
| `photo` | `bot/handlers/admin.py:8752` `admin_enemies_photo_pick` | `bot/handlers/admin.py:8758` `admin_enemies_photo_value` |
| `drop_chance` | `bot/handlers/admin.py:8912` `admin_enemies_drop_edit_chance`<br>`bot/handlers/admin.py:8986` `admin_enemies_drop_add_pick` | `bot/handlers/admin.py:8992` `admin_enemies_drop_chance_value` |
| `drop_qty` | `bot/handlers/admin.py:8925` `admin_enemies_drop_edit_qty`<br>`bot/handlers/admin.py:9013` `admin_enemies_drop_chance_value` | `bot/handlers/admin.py:9019` `admin_enemies_drop_qty_value` |
| `c_name` | `bot/handlers/admin.py:9058` `admin_enemies_new` | `bot/handlers/admin.py:9063` `admin_enemies_new_name` |
| `c_hp` | `bot/handlers/admin.py:9069` `admin_enemies_new_name` | `bot/handlers/admin.py:9074` `admin_enemies_new_hp` |
| `c_dmg` | `bot/handlers/admin.py:9080` `admin_enemies_new_hp` | `bot/handlers/admin.py:9085` `admin_enemies_new_dmg` |
| `c_dodge` | `bot/handlers/admin.py:9098` `admin_enemies_new_dmg` | `bot/handlers/admin.py:9103` `admin_enemies_new_dodge` |
| `c_chance` | `bot/handlers/admin.py:9109` `admin_enemies_new_dodge` | `bot/handlers/admin.py:9115` `admin_enemies_new_chance` |
| `c_loss_ap` | `bot/handlers/admin.py:9121` `admin_enemies_new_chance` | `bot/handlers/admin.py:9127` `admin_enemies_new_done` |

### `AdminCallsign` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | `bot/handlers/admin.py:755` `admin_callsign_start` | `bot/handlers/admin.py:776` `admin_callsign_target_msg` |
| `value` | `bot/handlers/admin.py:539` `pickuser_cb`<br>`bot/handlers/admin.py:786` `admin_callsign_target_msg` | `bot/handlers/admin.py:797` `admin_callsign_value_msg` |

### `AdminWing` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | `bot/handlers/admin.py:768` `admin_wing_start` | — |
| `value` | `bot/handlers/admin.py:550` `pickuser_cb` | — |

### `AdminStates` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | `bot/handlers/admin.py:4882` `admin_states_menu` | `bot/handlers/admin.py:4891` `admin_states_target_text` |
| `action` | `bot/handlers/admin.py:511` `pickuser_cb`<br>`bot/handlers/admin.py:4897` `admin_states_target_text` | — |
| `state_key` | `bot/handlers/admin.py:4923` `admin_states_op` | — |
| `minutes` | `bot/handlers/admin.py:4948` `admin_states_key` | `bot/handlers/admin.py:4957` `admin_states_minutes`<br>`bot/handlers/admin.py:4978` `admin_states_minutes_bad` |

### `AdminPlayerLog` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | `bot/handlers/admin.py:741` `admin_player_log_start` | `bot/handlers/admin.py:611` `admin_player_log_manual_msg` |

### `AdminSalary` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | — | — |
| `amount` | `bot/handlers/admin.py:524` `pickuser_cb` | `bot/handlers/admin.py:5059` `admin_salary_amount` |
| `period` | `bot/handlers/admin.py:5087` `admin_salary_amount` | `bot/handlers/admin.py:5099` `admin_salary_period_cb`<br>`bot/handlers/admin.py:5118` `admin_salary_period_text` |

### `AdminLocation` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `action` | — | — |
| `target_id` | — | — |
| `key` | `bot/handlers/admin.py:7619` `loc_create` | `bot/handlers/admin.py:7883` `loc_step_key` |
| `name` | `bot/handlers/admin.py:7889` `loc_step_key` | `bot/handlers/admin.py:7894` `loc_step_name` |
| `set_name` | `bot/handlers/admin.py:7910` `loc_set_name` | `bot/handlers/admin.py:7921` `loc_step_set_name` |
| `description` | `bot/handlers/admin.py:7896` `loc_step_name`<br>`bot/handlers/admin.py:7935` `loc_step_set_name`<br>`bot/handlers/admin.py:7949` `loc_set_desc` | `bot/handlers/admin.py:8131` `loc_step_desc` |
| `mode` | `bot/handlers/admin.py:7715` `loc_set_mode`<br>`bot/handlers/admin.py:8142` `loc_step_desc` | `bot/handlers/admin.py:7728` `loc_mode_chosen` |
| `req_status` | `bot/handlers/admin.py:7741` `loc_mode_chosen`<br>`bot/handlers/admin.py:7750` `loc_mode_chosen`<br>`bot/handlers/admin.py:7759` `loc_set_status` | `bot/handlers/admin.py:7764` `loc_req_status_chosen` |
| `blocking` | `bot/handlers/admin.py:7747` `loc_mode_chosen`<br>`bot/handlers/admin.py:7778` `loc_req_status_chosen`<br>`bot/handlers/admin.py:7794` `loc_set_blocking` | `bot/handlers/admin.py:7799` `loc_blocking_chosen` |
| `preview` | `bot/handlers/admin.py:8168` `loc_glade_set`<br>`bot/handlers/admin.py:8218` `loc_clearing_set`<br>`bot/handlers/admin.py:8267` `loc_photo_set`<br>`bot/handlers/admin.py:8305` `loc_season_photo_set` | `bot/handlers/admin.py:8347` `loc_step_photo` |

### `AdminDungeon` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target_id` | — | — |
| `photo_tod` | `bot/handlers/admin.py:5268` `dungeon_photo_set` | `bot/handlers/admin.py:5304` `dungeon_step_photo` |
| `enemy_id` | — | — |
| `enemy_field` | — | — |
| `enemy_value` | `bot/handlers/admin.py:5545` `dungeon_enemy_field_pick` | `bot/handlers/admin.py:5571` `dungeon_enemy_value` |
| `drop_chance` | `bot/handlers/admin.py:1614` `add_item_photo`<br>`bot/handlers/admin.py:5813` `enemy_drop_pick_item`<br>`bot/handlers/admin.py:5896` `enemy_drop_set_chance` | `bot/handlers/admin.py:6218` `enemy_drop_chance_value` |
| `drop_qty` | `bot/handlers/admin.py:5919` `enemy_drop_set_qty`<br>`bot/handlers/admin.py:6227` `enemy_drop_chance_value` | `bot/handlers/admin.py:6233` `enemy_drop_qty_value` |
| `drop_item_photo` | `bot/handlers/admin.py:5964` `enemy_drop_item_photo` | `bot/handlers/admin.py:5973` `enemy_drop_item_photo_value` |
| `drop_item_desc` | `bot/handlers/admin.py:6018` `enemy_drop_item_desc` | `bot/handlers/admin.py:6027` `enemy_drop_item_desc_value` |
| `drop_item_field` | — | — |
| `drop_item_value` | `bot/handlers/admin.py:6116` `enemy_drop_item_stat_pick` | `bot/handlers/admin.py:6127` `enemy_drop_item_stat_value` |
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
| `target` | `bot/handlers/inventory.py:1644` `inv_transfer_start` | `bot/handlers/inventory.py:1653` `inv_transfer_target` |
| `amount` | `bot/handlers/inventory.py:1660` `inv_transfer_target` | `bot/handlers/inventory.py:1668` `inv_transfer_amount` |
| `message` | `bot/handlers/inventory.py:1700` `inv_transfer_amount` | `bot/handlers/inventory.py:1709` `inv_transfer_message` |

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
| `text` | `bot/handlers/nii.py:88` `nii_write_start` | `bot/handlers/nii.py:101` `nii_write_text` |
| `photo` | `bot/handlers/nii.py:117` `nii_write_text` | `bot/handlers/nii.py:135` `nii_write_photo` |

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
| `waiting_photo` | `bot/handlers/reports.py:88` `report_submit_start` | `bot/handlers/reports.py:97` `report_receive_photo`<br>`bot/handlers/reports.py:116` `report_photo_expected` |
| `waiting_daily_troops` | `bot/handlers/reports.py:103` `report_receive_photo` | `bot/handlers/reports.py:121` `report_receive_daily_troops`<br>`bot/handlers/reports.py:146` `report_daily_troops_expected` |
| `waiting_total_troops` | `bot/handlers/reports.py:133` `report_receive_daily_troops` | `bot/handlers/reports.py:151` `report_receive_total_troops`<br>`bot/handlers/reports.py:182` `report_total_troops_expected` |
| `waiting_region` | `bot/handlers/reports.py:160` `report_receive_total_troops` | `bot/handlers/reports.py:187` `report_receive_region`<br>`bot/handlers/reports.py:281` `report_region_expected` |

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
| `aw:` | 6 | `aw:create`, `aw:delete`, `aw:edit`, `aw:grant`, `aw:list`, `aw:revoke` |
| `aw_comment:` | 1 | `aw_comment:skip` |
| `aw_confirm:` | 1 | `aw_confirm` |
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
| `loc:` | 18 | `loc:blocking:done`, `loc:blocking:none`, `loc:building_pick`, `loc:clearing_set`, `loc:create`, `loc:edit_pick`, `loc:glade_set`, `loc:mode:all`, `loc:mode:exact`, `loc:mode:min`, `loc:photos`, `loc:photos:clear`, `loc:photos:clear_seasons`, `loc:set_blocking`, `loc:set_desc`, `loc:set_mode`, `loc:set_name`, `loc:set_status` |
| `lootonly:` | 2 | `lootonly:no`, `lootonly:yes` |
| `marketok:` | 2 | `marketok:no`, `marketok:yes` |
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
| `rolop:` | 2 | `rolop:add`, `rolop:remove` |
| `salary:` | 2 | `salary:choose`, `salary:pay` |
| `salary_period:` | 2 | `salary_period:30`, `salary_period:7` |
| `shop:` | 1 | `shop:catalog` |
| `shop_admin:` | 2 | `shop_admin:add`, `shop_admin:edit` |
| `shopcat:` | 2 | `shopcat:license`, `shopcat:market` |
| `st:` | 7 | `st:create`, `st:delete`, `st:grant`, `st:legioner`, `st:list`, `st:more`, `st:revoke` |
| `st_op:` | 2 | `st_op:clear`, `st_op:set` |
| `storage:` | 3 | `storage:cats`, `storage:create`, `storage:noop` |
| `treasury:` | 3 | `treasury:debts`, `treasury:give`, `treasury:stats` |
| `vote:` | 2 | `vote:close_cancel`, `vote:create` |
| `wall:` | 2 | `wall:archive`, `wall:write` |
| `wing_set:` | 1 | `wing_set:none` |

## 3. Фильтры хендлеров `F.data`

### Точное совпадение (`F.data == "..."`)

- `admin:awards`: `bot/handlers/admin.py:3407`
- `admin:callsign`: `bot/handlers/admin.py:749`
- `admin:del_photo`: `bot/handlers/admin.py:723`
- `admin:dungeons`: `bot/handlers/admin.py:5166`
- `admin:enemies`: `bot/handlers/admin.py:8502`
- `admin:finance`: `bot/handlers/admin.py:2181`
- `admin:fishing`: `bot/handlers/admin.py:6421`
- `admin:forest`: `bot/handlers/admin.py:6983`
- `admin:locations`: `bot/handlers/admin.py:5142`
- `admin:logs`: `bot/handlers/admin.py:4678`
- `admin:menu`: `bot/handlers/admin.py:713`
- `admin:player_log`: `bot/handlers/admin.py:735`
- `admin:ranks`: `bot/handlers/admin.py:4568`
- `admin:reports`: `bot/handlers/admin.py:4003`
- `admin:reports_done`: `bot/handlers/admin.py:4055`
- `admin:reports_pending`: `bot/handlers/admin.py:4012`
- `admin:roles`: `bot/handlers/admin.py:2688`
- `admin:salaries`: `bot/handlers/admin.py:4982`
- `admin:saletax`: `bot/handlers/admin.py:2445`
- `admin:shop`: `bot/handlers/admin.py:864`
- `admin:states`: `bot/handlers/admin.py:4876`
- `admin:statuses`: `bot/handlers/admin.py:2922`
- `admin:storage`: `bot/handlers/admin.py:938`
- `admin:tax`: `bot/handlers/admin.py:2408`
- `admin:treasury`: `bot/handlers/admin.py:2221`
- `admin:wing`: `bot/handlers/admin.py:762`
- `aw:create`: `bot/handlers/admin.py:3451`
- `aw:delete`: `bot/handlers/admin.py:3592`
- `aw:edit`: `bot/handlers/admin.py:3773`
- `aw:grant`: `bot/handlers/admin.py:3892`
- `aw:list`: `bot/handlers/admin.py:3433`
- `aw:revoke`: `bot/handlers/admin.py:3983`
- `aw_comment:skip`: `bot/handlers/admin.py:3940`
- `aw_confirm`: `bot/handlers/admin.py:3568`
- `back:main`: `bot/handlers/admin.py:4851`
- `bank:balance`: `bot/handlers/bank.py:72`
- `bank:history`: `bot/handlers/bank.py:403`
- `bank:menu`: `bot/handlers/bank.py:191`
- `bank:transfer`: `bot/handlers/bank.py:131`
- `bank:transfer_manual`: `bot/handlers/bank.py:147`
- `bank:treasury`: `bot/handlers/bank.py:204`
- `booklet:claim`: `bot/handlers/tourist_booklet.py:71`
- `booklet:menu`: `bot/handlers/tourist_booklet.py:65`
- `cancel`: `bot/handlers/admin.py:4859`
- `city:clans`: `bot/handlers/clans.py:88`
- `city:dungeon`: `bot/handlers/dungeon.py:888`
- `city:library`: `bot/handlers/library.py:82`
- `city:menu`: `bot/handlers/start.py:158`
- `city:pilots`: `bot/handlers/pilots.py:100`
- `city:pilots:list`: `bot/handlers/pilots.py:127`
- `city:vote`: `bot/handlers/polls.py:70`
- `clans:create_skip`: `bot/handlers/clans.py:651`
- `clans:noop`: `bot/handlers/clans.py:436`
- `contracts:list`: `bot/handlers/dungeon.py:700`
- `del_item:back`: `bot/handlers/admin.py:1690`
- `duel:card:buy`: `bot/handlers/duel.py:246`
- `duel:help`: `bot/handlers/duel.py:224`
- `duel:list`: `bot/handlers/duel.py:272`
- `duel:menu`: `bot/handlers/duel.py:218`
- `duel:top`: `bot/handlers/duel.py:292`
- `dungeon:enemies`: `bot/handlers/admin.py:5487`
- `dungeon:exit`: `bot/handlers/dungeon.py:2430`
- `dungeon:exit:cancel`: `bot/handlers/dungeon.py:2509`
- `dungeon:exit:confirm`: `bot/handlers/dungeon.py:2477`
- `dungeon:photos`: `bot/handlers/admin.py:5249`
- `dungeon:photos:clear`: `bot/handlers/admin.py:5293`
- `enemy:fi`: `bot/handlers/admin.py:8540`
- `field:drink`: `bot/handlers/admin.py:1961`
- `field:loot_only`: `bot/handlers/admin.py:2025`
- `field:market_ok`: `bot/handlers/admin.py:2005`
- `field:photo`: `bot/handlers/admin.py:1882`
- `field:weapon_effect`: `bot/handlers/admin.py:1902`
- `fin:manual`: `bot/handlers/admin.py:2529`
- `forest:addlist`: `bot/handlers/admin.py:7314`
- `forest:new`: `bot/handlers/admin.py:7467`
- `forest:zset:sold_daily_limit`: `bot/handlers/admin.py:7153`
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
- `loc:building_pick`: `bot/handlers/admin.py:7645`
- `loc:clearing_clear`: `bot/handlers/admin.py:8242`
- `loc:clearing_set`: `bot/handlers/admin.py:8205`
- `loc:create`: `bot/handlers/admin.py:7613`
- `loc:edit_pick`: `bot/handlers/admin.py:7629`
- `loc:glade_clear`: `bot/handlers/admin.py:8192`
- `loc:glade_set`: `bot/handlers/admin.py:8154`
- `loc:photos`: `bot/handlers/admin.py:8080`
- `loc:photos:clear`: `bot/handlers/admin.py:8333`
- `loc:photos:clear_seasons`: `bot/handlers/admin.py:8103`
- `loc:set_blocking`: `bot/handlers/admin.py:7782`
- `loc:set_desc`: `bot/handlers/admin.py:7939`
- `loc:set_mode`: `bot/handlers/admin.py:7711`
- `loc:set_name`: `bot/handlers/admin.py:7900`
- `loc:set_status`: `bot/handlers/admin.py:7754`
- `news:archive`: `bot/handlers/news.py:132`
- `news:no_photo`: `bot/handlers/news.py:350`
- `news:tab`: `bot/handlers/news.py:259`
- `news:write`: `bot/handlers/news.py:279`
- `nii:all`: `bot/handlers/nii.py:232`
- `nii:menu_back`: `bot/handlers/nii.py:226`
- `nii:mine`: `bot/handlers/nii.py:207`
- `nii:no_photo`: `bot/handlers/nii.py:128`
- `nii:write`: `bot/handlers/nii.py:76`
- `noop`: `bot/handlers/admin.py:4846`
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
- `rep:auto_approve_edit`: `bot/handlers/admin.py:4099`
- `rep:next`: `bot/handlers/admin.py:4541`
- `rep:pay_cap_edit`: `bot/handlers/admin.py:4138`
- `rep:speech`: `bot/handlers/representative.py:77`
- `rep:speech:delete`: `bot/handlers/representative.py:109`
- `rep:speech:write`: `bot/handlers/representative.py:89`
- `report:my_reports`: `bot/handlers/reports.py:285`
- `report:submit`: `bot/handlers/reports.py:43`
- `salary:choose`: `bot/handlers/admin.py:5021`
- `salary:pay`: `bot/handlers/admin.py:5033`
- `shop:catalog`: `bot/handlers/shop.py:228`
- `shop_admin:add`: `bot/handlers/admin.py:1201`
- `shop_admin:delete`: `bot/handlers/admin.py:1661`
- `shop_admin:edit`: `bot/handlers/admin.py:1784`
- `shop_admin:special_code`: `bot/handlers/admin.py:2486`
- `shop_del:cats`: `bot/handlers/admin.py:1778`
- `shop_edit:cats`: `bot/handlers/admin.py:1763`
- `st:create`: `bot/handlers/admin.py:2976`
- `st:delete`: `bot/handlers/admin.py:3049`
- `st:grant`: `bot/handlers/admin.py:3249`
- `st:legioner`: `bot/handlers/admin.py:3194`
- `st:list`: `bot/handlers/admin.py:2959`
- `st:more`: `bot/handlers/admin.py:3388`
- `st:revoke`: `bot/handlers/admin.py:3315`
- `storage:cats`: `bot/handlers/admin.py:957`
- `storage:create`: `bot/handlers/admin.py:1202`
- `storage:noop`: `bot/handlers/admin.py:952`
- `treasury:debts`: `bot/handlers/admin.py:2254`
- `treasury:give`: `bot/handlers/admin.py:2353`
- `treasury:stats`: `bot/handlers/admin.py:2301`
- `vote:close_cancel`: `bot/handlers/polls.py:332`
- `vote:create`: `bot/handlers/polls.py:224`
- `wall:archive`: `bot/handlers/wall.py:315`
- `wall:view`: `bot/handlers/wall.py:149`
- `wall:write`: `bot/handlers/wall.py:170`

### По префиксу (`F.data.startswith("...")`)

- `\d+$`: `bot/handlers/admin.py:1353`; `bot/handlers/admin.py:4956`; `bot/handlers/admin.py:7167`; `bot/handlers/reports.py:186`
- `\d{1,7}$`: `bot/handlers/reports.py:120`; `bot/handlers/reports.py:150`
- `act:`: `bot/handlers/admin.py:4753`
- `addreq:`: `bot/handlers/admin.py:1552`
- `aw_del:`: `bot/handlers/admin.py:3613`
- `aw_edit:`: `bot/handlers/admin.py:3793`
- `aw_ei:`: `bot/handlers/admin.py:3804`
- `aw_pick:`: `bot/handlers/admin.py:3924`
- `awr_grant:`: `bot/handlers/admin.py:3991`
- `bait:set:`: `bot/handlers/fishing.py:176`
- `bank:pickrecipient:`: `bot/handlers/bank.py:177`
- `bank:transfer:list:`: `bot/handlers/bank.py:137`
- `buy5_nord:`: `bot/handlers/shop.py:487`
- `buy_housing:`: `bot/handlers/shop.py:1001`
- `buy_housing_cancel:`: `bot/handlers/shop.py:992`
- `buy_nord:`: `bot/handlers/shop.py:477`
- `cat:`: `bot/handlers/admin.py:1274`
- `city/`: `bot/handlers/locations.py:83`
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
- `confirm_del_photo:`: `bot/handlers/admin.py:843`
- `contract:enter:\d+$`: `bot/handlers/dungeon.py:780`
- `contract:enter:confirm:`: `bot/handlers/dungeon.py:826`
- `contract:pick:`: `bot/handlers/dungeon.py:728`
- `del_item:`: `bot/handlers/admin.py:1675`
- `drinksel:`: `bot/handlers/admin.py:1307`
- `duel:accept:`: `bot/handlers/duel.py:399`
- `duel:atk:`: `bot/handlers/duel.py:529`
- `duel:cancel:`: `bot/handlers/duel.py:373`
- `duel:decline:`: `bot/handlers/duel.py:385`
- `duel:def:`: `bot/handlers/duel.py:545`
- `duel:invite:`: `bot/handlers/duel.py:310`
- `duel:leave:`: `bot/handlers/duel.py:448`
- `dungeon:attack:`: `bot/handlers/dungeon.py:1277`
- `dungeon:continue:`: `bot/handlers/dungeon.py:1078`
- `dungeon:edit:`: `bot/handlers/admin.py:5186`
- `dungeon:enemy:`: `bot/handlers/admin.py:5519`
- `dungeon:escape:`: `bot/handlers/dungeon.py:1893`
- `dungeon:photo_set:`: `bot/handlers/admin.py:5258`
- `dungeon:use_slot:`: `bot/handlers/dungeon.py:1594`
- `eddrop:`: `bot/handlers/admin.py:5844`
- `eddrop_del:`: `bot/handlers/admin.py:5930`
- `eddrop_desc:`: `bot/handlers/admin.py:6002`
- `eddrop_photo:`: `bot/handlers/admin.py:5948`
- `eddrop_set_ch:`: `bot/handlers/admin.py:5885`
- `eddrop_set_q:`: `bot/handlers/admin.py:5908`
- `eddrop_stat:`: `bot/handlers/admin.py:6097`
- `eddrop_stats:`: `bot/handlers/admin.py:6058`
- `eddrop_weff:`: `bot/handlers/admin.py:6160`
- `eddrop_weff_set:`: `bot/handlers/admin.py:6182`
- `edit_item:`: `bot/handlers/admin.py:1793`
- `editem_add:`: `bot/handlers/admin.py:5796`
- `editem_new:`: `bot/handlers/admin.py:5821`
- `editem_pick:`: `bot/handlers/admin.py:5751`
- `editset:drink:`: `bot/handlers/admin.py:1984`
- `editset:weff:`: `bot/handlers/admin.py:1918`
- `enemy:card:`: `bot/handlers/admin.py:8674`
- `enemy:dcard:`: `bot/handlers/admin.py:8602`
- `enemy:del:`: `bot/handlers/admin.py:8800`
- `enemy:dn:\d+$`: `bot/handlers/admin.py:8512`
- `enemy:dropadd:`: `bot/handlers/admin.py:8977`
- `enemy:dropch:`: `bot/handlers/admin.py:8904`
- `enemy:dropdel:`: `bot/handlers/admin.py:8930`
- `enemy:dropedit:`: `bot/handlers/admin.py:8866`
- `enemy:dropitem:`: `bot/handlers/admin.py:8942`
- `enemy:dropq:`: `bot/handlers/admin.py:8917`
- `enemy:drops:`: `bot/handlers/admin.py:8856`
- `enemy:fld:`: `bot/handlers/admin.py:8684`
- `enemy:list:[a-z]+:[\w-]+$`: `bot/handlers/admin.py:8560`
- `enemy:new:`: `bot/handlers/admin.py:9051`
- `enemy:photo:`: `bot/handlers/admin.py:8744`
- `enemy:tog:`: `bot/handlers/admin.py:8781`
- `enemy_drops:`: `bot/handlers/admin.py:5738`
- `enemy_field:`: `bot/handlers/admin.py:5532`
- `eqequip:[a-z0-9_]+:\d+$`: `bot/handlers/inventory.py:500`
- `eqlock:[a-z0-9_]+$`: `bot/handlers/inventory.py:488`
- `eqpart:`: `bot/handlers/admin.py:1385`
- `eqslot:[a-z0-9_]+$`: `bot/handlers/inventory.py:493`
- `equnequip:[a-z0-9_]+$`: `bot/handlers/inventory.py:532`
- `field:`: `bot/handlers/admin.py:2089`
- `field:required_status`: `bot/handlers/admin.py:1832`
- `field_req:`: `bot/handlers/admin.py:1865`
- `fin:`: `bot/handlers/admin.py:2539`
- `finuser:`: `bot/handlers/admin.py:2569`
- `fish:bait:\d+$`: `bot/handlers/fishing.py:478`
- `fish:bait:set:\d+:[a-z]+$`: `bot/handlers/fishing.py:520`
- `fish:cast:\d+$`: `bot/handlers/fishing.py:530`
- `fish:lake:\d+$`: `bot/handlers/fishing.py:471`
- `fishbuy:`: `bot/handlers/shop.py:790`
- `fishcatch:`: `bot/handlers/inventory.py:1275`
- `fishgo:`: `bot/handlers/inventory.py:1526`
- `fishing:addfish:`: `bot/handlers/admin.py:6588`
- `fishing:addlist:`: `bot/handlers/admin.py:6558`
- `fishing:del:`: `bot/handlers/admin.py:6611`
- `fishing:fish:`: `bot/handlers/admin.py:6478`
- `fishing:junk:`: `bot/handlers/admin.py:6334`
- `fishing:kind:`: `bot/handlers/admin.py:6492`
- `fishing:market:`: `bot/handlers/admin.py:6514`
- `fishing:new:`: `bot/handlers/admin.py:6636`
- `fishing:new_super:`: `bot/handlers/admin.py:6739`
- `fishing:super:`: `bot/handlers/admin.py:6536`
- `fishing:water:`: `bot/handlers/admin.py:6440`
- `fishing_field:`: `bot/handlers/admin.py:6798`
- `fishing_j:`: `bot/handlers/admin.py:6384`
- `fishmarket:`: `bot/handlers/inventory.py:1428`
- `fishoffer:`: `bot/handlers/shop.py:726`
- `fishprice:`: `bot/handlers/inventory.py:1508`
- `fishsell:`: `bot/handlers/inventory.py:1584`
- `fishuse:`: `bot/handlers/inventory.py:1283`
- `forest:add:`: `bot/handlers/admin.py:7339`
- `forest:area:\d+:(glade|clearing)$`: `bot/handlers/forest.py:427`
- `forest:battle:flee:\d+$`: `bot/handlers/forest.py:1052`
- `forest:battle:hit:\d+$`: `bot/handlers/forest.py:854`
- `forest:card:`: `bot/handlers/admin.py:7253`
- `forest:cast:\d+(?::(glade|clearing))?$`: `bot/handlers/forest.py:490`
- `forest:del:`: `bot/handlers/admin.py:7358`
- `forest:kind:`: `bot/handlers/admin.py:7267`
- `forest:market:`: `bot/handlers/admin.py:7292`
- `forest:new_kind:`: `bot/handlers/admin.py:7547`
- `forest:zadd:(glade|clearing):\d+$`: `bot/handlers/admin.py:7119`
- `forest:zaddlist:(glade|clearing)$`: `bot/handlers/admin.py:7092`
- `forest:zchance:(glade|clearing):\d+$`: `bot/handlers/admin.py:7065`
- `forest:zdel:(glade|clearing):\d+$`: `bot/handlers/admin.py:7080`
- `forest:zone:(glade|clearing)$`: `bot/handlers/admin.py:6993`
- `forest:zset:(glade|clearing):(\w+)$`: `bot/handlers/admin.py:7131`
- `forest_field:`: `bot/handlers/admin.py:7379`
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
- `inv_sellmore:`: `bot/handlers/inventory.py:1121`
- `inv_slot:`: `bot/handlers/inventory.py:840`
- `inv_transfer:`: `bot/handlers/inventory.py:1616`
- `inv_unequip:`: `bot/handlers/inventory.py:816`
- `inv_unslot:`: `bot/handlers/inventory.py:875`
- `inv_use:`: `bot/handlers/inventory.py:897`
- `inventory:cat:[^:]+$`: `bot/handlers/inventory.py:592`
- `invitem:`: `bot/handlers/inventory.py:779`
- `itembuy:`: `bot/handlers/shop.py:905`
- `itemgo:`: `bot/handlers/inventory.py:1219`
- `itemmarket:`: `bot/handlers/inventory.py:1129`
- `itemoffer:`: `bot/handlers/shop.py:845`
- `itemprice:`: `bot/handlers/inventory.py:1208`
- `kvp:attack:`: `bot/handlers/kvp.py:514`
- `kvp:attempt:`: `bot/handlers/kvp.py:440`
- `kvp:continue:`: `bot/handlers/kvp.py:410`
- `libadmin_del:`: `bot/handlers/library.py:409`
- `libadmin_sec:`: `bot/handlers/library.py:297`
- `libbook:`: `bot/handlers/library.py:204`
- `libdl:`: `bot/handlers/library.py:249`
- `libsec:[a-z]+$`: `bot/handlers/library.py:178`
- `loc:blocking:`: `bot/handlers/admin.py:7798`
- `loc:building:`: `bot/handlers/admin.py:7687`
- `loc:edit:`: `bot/handlers/admin.py:7661`
- `loc:mode:`: `bot/handlers/admin.py:7727`
- `loc:photo_set:`: `bot/handlers/admin.py:8255`
- `loc:req_status:`: `bot/handlers/admin.py:7763`
- `loc:season:(winter|spring|summer|autumn)$`: `bot/handlers/admin.py:8090`
- `loc:season_clear:(winter|spring|summer|autumn)$`: `bot/handlers/admin.py:8116`
- `loc:season_photo_set:(winter|spring|summer|autumn):(dawn|day|sunset|night)$`: `bot/handlers/admin.py:8292`
- `location:enter:`: `bot/handlers/locations.py:103`
- `location:preview:`: `bot/handlers/locations.py:34`
- `locstat:`: `bot/handlers/admin.py:4812`
- `lootonly:`: `bot/handlers/admin.py:1527`
- `marketok:`: `bot/handlers/admin.py:1505`
- `mollusk:flee:\d+$`: `bot/handlers/dungeon.py:459`
- `mollusk:hit:\d+$`: `bot/handlers/dungeon.py:365`
- `news:(?:off|(?:dis)?allow:-?\d+|chat:-?\d+:-?\d+|topic:-?\d+:-?\d+)$`: `bot/handlers/admin.py:2861`
- `news:arch:\d+$`: `bot/handlers/news.py:179`
- `news:del:`: `bot/handlers/news.py:473`
- `news:delconf:`: `bot/handlers/news.py:495`
- `news:edit:`: `bot/handlers/news.py:400`
- `news:view:`: `bot/handlers/news.py:196`
- `nii:set:`: `bot/handlers/nii.py:299`
- `nii:view:`: `bot/handlers/nii.py:263`
- `page`: `bot/handlers/admin.py:401`
- `park:admin:del:`: `bot/handlers/park.py:390`
- `park:admin:delyes:`: `bot/handlers/park.py:408`
- `park:admin:edit:`: `bot/handlers/park.py:474`
- `park:adminedit:f:`: `bot/handlers/park.py:492`
- `park:statue:`: `bot/handlers/park.py:257`
- `pickuser:`: `bot/handlers/admin.py:392`
- `pollarch:day:\d{4}-\d{2}-\d{2}(?::\d+)?$`: `bot/handlers/poll_archive.py:176`
- `pollarch:days:\d+$`: `bot/handlers/poll_archive.py:154`
- `prod:`: `bot/handlers/admin.py:1465`
- `prof_sel_status:`: `bot/handlers/profile.py:321`
- `profile:award:`: `bot/handlers/profile.py:541`
- `rank_pick:`: `bot/handlers/admin.py:4645`
- `rank_promote:`: `bot/handlers/admin.py:4604`
- `rar:`: `bot/handlers/admin.py:1265`
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
- `rep:nav:`: `bot/handlers/admin.py:4530`
- `rep_fix:`: `bot/handlers/admin.py:4329`
- `rep_no:`: `bot/handlers/admin.py:4515`
- `rep_ok:`: `bot/handlers/admin.py:4446`
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
- `role:`: `bot/handlers/admin.py:2774`
- `rolop:`: `bot/handlers/admin.py:2725`
- `salary_period:`: `bot/handlers/admin.py:5098`
- `shop_del:cat:`: `bot/handlers/admin.py:1769`
- `shop_edit:cat:`: `bot/handlers/admin.py:1754`
- `shopcat:[^:]+$`: `bot/handlers/shop.py:248`
- `shopcat:[^:]+:\d+$`: `bot/handlers/shop.py:332`
- `shopitem:`: `bot/handlers/shop.py:343`
- `st_del:`: `bot/handlers/admin.py:3068`
- `st_key:`: `bot/handlers/admin.py:4941`
- `st_op:`: `bot/handlers/admin.py:4911`
- `st_pick:`: `bot/handlers/admin.py:3350`
- `st_rev:`: `bot/handlers/admin.py:3280`
- `storage:cat:`: `bot/handlers/admin.py:970`
- `storage:item:`: `bot/handlers/admin.py:1001`
- `storage:page:`: `bot/handlers/admin.py:987`
- `storage:purge:`: `bot/handlers/admin.py:1127`
- `storage:restock:`: `bot/handlers/admin.py:1059`
- `toggle:`: `bot/handlers/admin.py:7803`
- `vote:cast:`: `bot/handlers/polls.py:163`
- `vote:close:`: `bot/handlers/polls.py:287`
- `vote:close_confirm:`: `bot/handlers/polls.py:310`
- `vote:results:`: `bot/handlers/polls.py:185`
- `vote:show:`: `bot/handlers/polls.py:109`
- `wall:archpage:\d+$`: `bot/handlers/wall.py:338`
- `wall:archread:\d+(?::\d+)?$`: `bot/handlers/wall.py:357`
- `wall:delete:\d+$`: `bot/handlers/wall.py:224`
- `wall:page:\d+$`: `bot/handlers/wall.py:156`
- `weff:`: `bot/handlers/admin.py:1398`
- `wing_set:`: `bot/handlers/admin.py:818`
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

