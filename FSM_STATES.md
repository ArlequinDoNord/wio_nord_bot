# Карта FSM-состояний и callback-неймспейсов N.O.R.D.

> **Сгенерировано** `tools/export_states.py`. Не редактировать вручную —
> правь код и перегенерируй: `.venv\Scripts\python.exe tools/export_states.py`.
>
> Назначение: единый обзор всех `StatesGroup`, где они ставятся и где ловятся,
> а также реестр `callback_data` — чтобы не допускать конфликтов меню/хендлеров.

Всего классов состояний: **48**; полей-состояний: **209**; уникальных `callback_data`: **242**.

## 1. Классы состояний по модулям

### `AdminAddItem` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `name` | `bot/handlers/admin.py:1209` `shop_admin_add`<br>`bot/handlers/admin.py:5837` `enemy_drop_new_item` | `bot/handlers/admin.py:1217` `add_item_name` |
| `desc` | `bot/handlers/admin.py:1219` `add_item_name` | `bot/handlers/admin.py:1225` `add_item_desc` |
| `price` | `bot/handlers/admin.py:1228` `add_item_desc` | `bot/handlers/admin.py:1234` `add_item_price` |
| `sell_price` | `bot/handlers/admin.py:1244` `add_item_price` | `bot/handlers/admin.py:1250` `add_item_sell_price` |
| `rarity` | `bot/handlers/admin.py:1262` `add_item_sell_price` | — |
| `category` | `bot/handlers/admin.py:1271` `add_item_rarity` | — |
| `drink` | `bot/handlers/admin.py:1294` `add_item_category` | — |
| `plant_name` | `bot/handlers/admin.py:1283` `add_item_category` | `bot/handlers/admin.py:1319` `add_item_plant_name` |
| `stock` | `bot/handlers/admin.py:1303` `add_item_category`<br>`bot/handlers/admin.py:1313` `add_item_drink_choice`<br>`bot/handlers/admin.py:1322` `add_item_plant_name` | `bot/handlers/admin.py:1328` `add_item_stock` |
| `stats` | `bot/handlers/admin.py:1342` `add_item_stock`<br>`bot/handlers/admin.py:1347` `add_item_stock` | `bot/handlers/admin.py:1355` `add_item_stats`<br>`bot/handlers/admin.py:1395` `add_item_stats_bad` |
| `equip_slot` | `bot/handlers/admin.py:1372` `add_item_stats` | — |
| `weapon_effect` | `bot/handlers/admin.py:1360` `add_item_stats` | — |
| `weapon_effect_chance` | `bot/handlers/admin.py:1408` `add_item_weapon_effect_cb` | `bot/handlers/admin.py:1417` `add_item_weapon_effect_chance` |
| `weapon_effect_dmg` | `bot/handlers/admin.py:1429` `add_item_weapon_effect_chance` | `bot/handlers/admin.py:1441` `add_item_weapon_effect_dmg` |
| `producer` | `bot/handlers/admin.py:1456` `_go_add_item_producer` | — |
| `producer_user` | `bot/handlers/admin.py:1471` `add_item_producer` | `bot/handlers/admin.py:1483` `add_item_producer_user` |
| `market` | `bot/handlers/admin.py:1494` `_go_add_item_market` | — |
| `loot` | `bot/handlers/admin.py:1516` `_go_add_item_loot` | — |
| `status` | `bot/handlers/admin.py:1544` `_go_add_item_status` | — |
| `photo` | `bot/handlers/admin.py:1563` `add_item_status_cb` | `bot/handlers/admin.py:1571` `add_item_photo` |

### `AdminSaleTax` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `percent` | `bot/handlers/admin.py:2453` `admin_saletax_view` | `bot/handlers/admin.py:2467` `admin_saletax_set` |

### `AdminSpecialCode` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `code` | `bot/handlers/admin.py:2495` `admin_special_code_view` | `bot/handlers/admin.py:2510` `admin_special_code_set` |

### `AdminEditItem` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `item_id` | — | — |
| `field` | `bot/handlers/admin.py:1799` `edit_item_pick` | — |
| `value` | `bot/handlers/admin.py:2103` `edit_item_field` | `bot/handlers/admin.py:2114` `edit_item_value` |
| `photo` | `bot/handlers/admin.py:1888` `edit_item_field_photo` | `bot/handlers/admin.py:1938` `edit_item_photo` |

### `AdminFinance` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | `bot/handlers/admin.py:2533` `finance_manual`<br>`bot/handlers/admin.py:2550` `finance_pick` | `bot/handlers/admin.py:2611` `finance_target` |
| `currency` | — | — |
| `amount` | `bot/handlers/admin.py:446` `pickuser_cb`<br>`bot/handlers/admin.py:2580` `finance_pick_user`<br>`bot/handlers/admin.py:2618` `finance_target` | `bot/handlers/admin.py:2626` `finance_amount` |

### `AdminTreasury` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `amount` | `bot/handlers/admin.py:2360` `treasury_give` | `bot/handlers/admin.py:2370` `treasury_amount` |
| `target` | `bot/handlers/admin.py:2386` `treasury_amount` | `bot/handlers/admin.py:2392` `treasury_target_manual` |

### `AdminStorageRestock` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `amount` | `bot/handlers/admin.py:1071` `storage_restock` | `bot/handlers/admin.py:1085` `storage_restock_amount` |

### `AdminStorageDelete` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `confirm` | `bot/handlers/admin.py:1143` `storage_purge` | `bot/handlers/admin.py:1157` `storage_purge_confirm` |

### `AdminTax` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `percent` | `bot/handlers/admin.py:2416` `admin_tax_view` | `bot/handlers/admin.py:2428` `admin_tax_set` |

### `AdminReportAutoApprove` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `value` | `bot/handlers/admin.py:4107` `report_auto_approve_edit_cb` | `bot/handlers/admin.py:4120` `report_auto_approve_edit_value` |

### `AdminReportPayCap` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `value` | `bot/handlers/admin.py:4146` `report_pay_cap_edit_cb` | `bot/handlers/admin.py:4161` `report_pay_cap_edit_value` |

### `AdminReportFix` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `daily` | `bot/handlers/admin.py:4347` `report_fix_start` | `bot/handlers/admin.py:4360` `report_fix_daily` |
| `total` | `bot/handlers/admin.py:4374` `report_fix_daily` | `bot/handlers/admin.py:4388` `report_fix_total` |

### `AdminRoles` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | `bot/handlers/admin.py:2699` `admin_roles` | `bot/handlers/admin.py:2708` `roles_target` |
| `action` | `bot/handlers/admin.py:449` `pickuser_cb`<br>`bot/handlers/admin.py:2714` `roles_target` | — |
| `role` | `bot/handlers/admin.py:2732` `roles_action` | — |

### `AdminStatuses` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `name` | `bot/handlers/admin.py:2983` `status_create_start` | `bot/handlers/admin.py:2991` `status_create_name` |
| `tag` | `bot/handlers/admin.py:2993` `status_create_name` | `bot/handlers/admin.py:3002` `status_create_tag` |
| `level` | `bot/handlers/admin.py:3009` `status_create_tag` | `bot/handlers/admin.py:3019` `status_create_level` |
| `desc` | `bot/handlers/admin.py:3030` `status_create_level` | `bot/handlers/admin.py:3035` `status_create_desc` |
| `target` | `bot/handlers/admin.py:3256` `status_grant_target`<br>`bot/handlers/admin.py:3325` `status_revoke_target` | `bot/handlers/admin.py:3266` `status_grant_target_msg` |
| `grant_action` | — | — |
| `status_pick` | `bot/handlers/admin.py:464` `pickuser_cb`<br>`bot/handlers/admin.py:473` `pickuser_cb`<br>`bot/handlers/admin.py:3277` `status_grant_target_msg`<br>`bot/handlers/admin.py:3402` `status_grant_more` | — |
| `item_pick` | — | — |
| `item_status` | — | — |

### `AdminAwards` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `name` | `bot/handlers/admin.py:3459` `award_create_start` | `bot/handlers/admin.py:3516` `award_create_name` |
| `desc` | `bot/handlers/admin.py:3522` `award_create_name` | `bot/handlers/admin.py:3530` `award_create_desc` |
| `emoji` | `bot/handlers/admin.py:3533` `award_create_desc` | `bot/handlers/admin.py:3541` `award_create_emoji` |
| `bonus` | `bot/handlers/admin.py:3507` `_award_ask_bonus` | `bot/handlers/admin.py:3549` `award_create_bonus` |
| `preview` | `bot/handlers/admin.py:3495` `_award_ask_bonus` | — |
| `target` | `bot/handlers/admin.py:3896` `award_grant_target` | `bot/handlers/admin.py:3902` `award_grant_target_msg` |
| `award_pick` | `bot/handlers/admin.py:3987` `award_revoke_pick_user` | — |
| `comment` | `bot/handlers/admin.py:3930` `award_grant_pick` | `bot/handlers/admin.py:3947` `award_grant_comment` |
| `edit_value` | `bot/handlers/admin.py:3815` `award_edit_field_pick` | `bot/handlers/admin.py:3839` `award_edit_value` |

### `AdminFishing` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `water` | — | — |
| `wf_id` | — | — |
| `value` | `bot/handlers/admin.py:6398` `admin_fishing_junk_field_pick`<br>`bot/handlers/admin.py:6812` `admin_fishing_field_pick` | `bot/handlers/admin.py:6839` `admin_fishing_value` |
| `c_name` | `bot/handlers/admin.py:6649` `admin_fishing_new` | `bot/handlers/admin.py:6658` `admin_fishing_new_name` |
| `c_desc` | `bot/handlers/admin.py:6668` `admin_fishing_new_name` | `bot/handlers/admin.py:6674` `admin_fishing_new_desc` |
| `c_sell_price` | `bot/handlers/admin.py:6677` `admin_fishing_new_desc` | `bot/handlers/admin.py:6683` `admin_fishing_new_sell_price` |
| `c_day_weight` | `bot/handlers/admin.py:6691` `admin_fishing_new_sell_price` | `bot/handlers/admin.py:6699` `admin_fishing_new_day_weight` |
| `c_night_weight` | `bot/handlers/admin.py:6707` `admin_fishing_new_day_weight` | `bot/handlers/admin.py:6715` `admin_fishing_new_night_weight` |
| `c_photo` | `bot/handlers/admin.py:6747` `admin_fishing_new_super` | `bot/handlers/admin.py:6755` `admin_fishing_new_photo` |
| `c_super_rare` | `bot/handlers/admin.py:6723` `admin_fishing_new_night_weight` | — |

### `AdminForest` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `f_id` | — | — |
| `field` | — | — |
| `value` | `bot/handlers/admin.py:7394` `admin_forest_field_pick` | `bot/handlers/admin.py:7420` `admin_forest_value` |
| `c_name` | `bot/handlers/admin.py:7476` `admin_forest_new` | `bot/handlers/admin.py:7485` `admin_forest_new_name` |
| `c_desc` | `bot/handlers/admin.py:7495` `admin_forest_new_name` | `bot/handlers/admin.py:7501` `admin_forest_new_desc` |
| `c_sell_price` | `bot/handlers/admin.py:7504` `admin_forest_new_desc` | `bot/handlers/admin.py:7510` `admin_forest_new_sell_price` |
| `c_chance` | `bot/handlers/admin.py:7517` `admin_forest_new_sell_price` | `bot/handlers/admin.py:7526` `admin_forest_new_chance` |
| `c_kind` | `bot/handlers/admin.py:7534` `admin_forest_new_chance` | — |
| `c_photo` | `bot/handlers/admin.py:7557` `admin_forest_new_kind` | `bot/handlers/admin.py:7565` `admin_forest_new_photo` |
| `zone_value` | `bot/handlers/admin.py:7074` `admin_forest_zone_chance`<br>`bot/handlers/admin.py:7149` `admin_forest_zone_set_pick`<br>`bot/handlers/admin.py:7162` `admin_forest_limit_set` | `bot/handlers/admin.py:7169` `admin_forest_zone_value` |

### `AdminEnemy` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `field` | `bot/handlers/admin.py:8771` `admin_enemies_field_pick` | `bot/handlers/admin.py:8777` `admin_enemies_field_value` |
| `photo` | `bot/handlers/admin.py:8828` `admin_enemies_photo_pick` | `bot/handlers/admin.py:8834` `admin_enemies_photo_value` |
| `drop_chance` | `bot/handlers/admin.py:8988` `admin_enemies_drop_edit_chance`<br>`bot/handlers/admin.py:9062` `admin_enemies_drop_add_pick` | `bot/handlers/admin.py:9068` `admin_enemies_drop_chance_value` |
| `drop_qty` | `bot/handlers/admin.py:9001` `admin_enemies_drop_edit_qty`<br>`bot/handlers/admin.py:9089` `admin_enemies_drop_chance_value` | `bot/handlers/admin.py:9095` `admin_enemies_drop_qty_value` |
| `c_name` | `bot/handlers/admin.py:9134` `admin_enemies_new` | `bot/handlers/admin.py:9139` `admin_enemies_new_name` |
| `c_hp` | `bot/handlers/admin.py:9145` `admin_enemies_new_name` | `bot/handlers/admin.py:9150` `admin_enemies_new_hp` |
| `c_dmg` | `bot/handlers/admin.py:9156` `admin_enemies_new_hp` | `bot/handlers/admin.py:9161` `admin_enemies_new_dmg` |
| `c_dodge` | `bot/handlers/admin.py:9174` `admin_enemies_new_dmg` | `bot/handlers/admin.py:9179` `admin_enemies_new_dodge` |
| `c_chance` | `bot/handlers/admin.py:9185` `admin_enemies_new_dodge` | `bot/handlers/admin.py:9191` `admin_enemies_new_chance` |
| `c_loss_ap` | `bot/handlers/admin.py:9197` `admin_enemies_new_chance` | `bot/handlers/admin.py:9203` `admin_enemies_new_done` |

### `AdminCallsign` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | `bot/handlers/admin.py:756` `admin_callsign_start` | `bot/handlers/admin.py:777` `admin_callsign_target_msg` |
| `value` | `bot/handlers/admin.py:540` `pickuser_cb`<br>`bot/handlers/admin.py:787` `admin_callsign_target_msg` | `bot/handlers/admin.py:798` `admin_callsign_value_msg` |

### `AdminWing` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | `bot/handlers/admin.py:769` `admin_wing_start` | — |
| `value` | `bot/handlers/admin.py:551` `pickuser_cb` | — |

### `AdminStates` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | `bot/handlers/admin.py:4883` `admin_states_menu` | `bot/handlers/admin.py:4892` `admin_states_target_text` |
| `action` | `bot/handlers/admin.py:512` `pickuser_cb`<br>`bot/handlers/admin.py:4898` `admin_states_target_text` | — |
| `state_key` | `bot/handlers/admin.py:4924` `admin_states_op` | — |
| `minutes` | `bot/handlers/admin.py:4949` `admin_states_key` | `bot/handlers/admin.py:4958` `admin_states_minutes`<br>`bot/handlers/admin.py:4979` `admin_states_minutes_bad` |

### `AdminPlayerLog` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | `bot/handlers/admin.py:742` `admin_player_log_start` | `bot/handlers/admin.py:612` `admin_player_log_manual_msg` |

### `AdminSalary` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | — | — |
| `amount` | `bot/handlers/admin.py:525` `pickuser_cb` | `bot/handlers/admin.py:5060` `admin_salary_amount` |
| `period` | `bot/handlers/admin.py:5088` `admin_salary_amount` | `bot/handlers/admin.py:5100` `admin_salary_period_cb`<br>`bot/handlers/admin.py:5119` `admin_salary_period_text` |

### `AdminLocation` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `action` | — | — |
| `target_id` | — | — |
| `key` | `bot/handlers/admin.py:7620` `loc_create` | `bot/handlers/admin.py:7884` `loc_step_key` |
| `name` | `bot/handlers/admin.py:7890` `loc_step_key` | `bot/handlers/admin.py:7895` `loc_step_name` |
| `set_name` | `bot/handlers/admin.py:7911` `loc_set_name` | `bot/handlers/admin.py:7922` `loc_step_set_name` |
| `description` | `bot/handlers/admin.py:7897` `loc_step_name`<br>`bot/handlers/admin.py:7936` `loc_step_set_name`<br>`bot/handlers/admin.py:7950` `loc_set_desc` | `bot/handlers/admin.py:8142` `loc_step_desc` |
| `mode` | `bot/handlers/admin.py:7716` `loc_set_mode`<br>`bot/handlers/admin.py:8153` `loc_step_desc` | `bot/handlers/admin.py:7729` `loc_mode_chosen` |
| `req_status` | `bot/handlers/admin.py:7742` `loc_mode_chosen`<br>`bot/handlers/admin.py:7751` `loc_mode_chosen`<br>`bot/handlers/admin.py:7760` `loc_set_status` | `bot/handlers/admin.py:7765` `loc_req_status_chosen` |
| `blocking` | `bot/handlers/admin.py:7748` `loc_mode_chosen`<br>`bot/handlers/admin.py:7779` `loc_req_status_chosen`<br>`bot/handlers/admin.py:7795` `loc_set_blocking` | `bot/handlers/admin.py:7800` `loc_blocking_chosen` |
| `preview` | `bot/handlers/admin.py:8179` `loc_glade_set`<br>`bot/handlers/admin.py:8229` `loc_clearing_set`<br>`bot/handlers/admin.py:8280` `loc_mine_set`<br>`bot/handlers/admin.py:8329` `loc_photo_set`<br>`bot/handlers/admin.py:8367` `loc_season_photo_set` | `bot/handlers/admin.py:8409` `loc_step_photo` |

### `AdminDungeon` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target_id` | — | — |
| `photo_tod` | `bot/handlers/admin.py:5269` `dungeon_photo_set` | `bot/handlers/admin.py:5305` `dungeon_step_photo` |
| `enemy_id` | — | — |
| `enemy_field` | — | — |
| `enemy_value` | `bot/handlers/admin.py:5546` `dungeon_enemy_field_pick` | `bot/handlers/admin.py:5572` `dungeon_enemy_value` |
| `drop_chance` | `bot/handlers/admin.py:1615` `add_item_photo`<br>`bot/handlers/admin.py:5814` `enemy_drop_pick_item`<br>`bot/handlers/admin.py:5897` `enemy_drop_set_chance` | `bot/handlers/admin.py:6219` `enemy_drop_chance_value` |
| `drop_qty` | `bot/handlers/admin.py:5920` `enemy_drop_set_qty`<br>`bot/handlers/admin.py:6228` `enemy_drop_chance_value` | `bot/handlers/admin.py:6234` `enemy_drop_qty_value` |
| `drop_item_photo` | `bot/handlers/admin.py:5965` `enemy_drop_item_photo` | `bot/handlers/admin.py:5974` `enemy_drop_item_photo_value` |
| `drop_item_desc` | `bot/handlers/admin.py:6019` `enemy_drop_item_desc` | `bot/handlers/admin.py:6028` `enemy_drop_item_desc_value` |
| `drop_item_field` | — | — |
| `drop_item_value` | `bot/handlers/admin.py:6117` `enemy_drop_item_stat_pick` | `bot/handlers/admin.py:6128` `enemy_drop_item_stat_value` |
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
| `loc:` | 19 | `loc:blocking:done`, `loc:blocking:none`, `loc:building_pick`, `loc:clearing_set`, `loc:create`, `loc:edit_pick`, `loc:glade_set`, `loc:mine_set`, `loc:mode:all`, `loc:mode:exact`, `loc:mode:min`, `loc:photos`, `loc:photos:clear`, `loc:photos:clear_seasons`, `loc:set_blocking`, `loc:set_desc`, `loc:set_mode`, `loc:set_name`, `loc:set_status` |
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

- `admin:awards`: `bot/handlers/admin.py:3408`
- `admin:callsign`: `bot/handlers/admin.py:750`
- `admin:del_photo`: `bot/handlers/admin.py:724`
- `admin:dungeons`: `bot/handlers/admin.py:5167`
- `admin:enemies`: `bot/handlers/admin.py:8578`
- `admin:finance`: `bot/handlers/admin.py:2182`
- `admin:fishing`: `bot/handlers/admin.py:6422`
- `admin:forest`: `bot/handlers/admin.py:6984`
- `admin:locations`: `bot/handlers/admin.py:5143`
- `admin:logs`: `bot/handlers/admin.py:4679`
- `admin:menu`: `bot/handlers/admin.py:714`
- `admin:player_log`: `bot/handlers/admin.py:736`
- `admin:ranks`: `bot/handlers/admin.py:4569`
- `admin:reports`: `bot/handlers/admin.py:4004`
- `admin:reports_done`: `bot/handlers/admin.py:4056`
- `admin:reports_pending`: `bot/handlers/admin.py:4013`
- `admin:roles`: `bot/handlers/admin.py:2689`
- `admin:salaries`: `bot/handlers/admin.py:4983`
- `admin:saletax`: `bot/handlers/admin.py:2446`
- `admin:shop`: `bot/handlers/admin.py:865`
- `admin:states`: `bot/handlers/admin.py:4877`
- `admin:statuses`: `bot/handlers/admin.py:2923`
- `admin:storage`: `bot/handlers/admin.py:939`
- `admin:tax`: `bot/handlers/admin.py:2409`
- `admin:treasury`: `bot/handlers/admin.py:2222`
- `admin:wing`: `bot/handlers/admin.py:763`
- `aw:create`: `bot/handlers/admin.py:3452`
- `aw:delete`: `bot/handlers/admin.py:3593`
- `aw:edit`: `bot/handlers/admin.py:3774`
- `aw:grant`: `bot/handlers/admin.py:3893`
- `aw:list`: `bot/handlers/admin.py:3434`
- `aw:revoke`: `bot/handlers/admin.py:3984`
- `aw_comment:skip`: `bot/handlers/admin.py:3941`
- `aw_confirm`: `bot/handlers/admin.py:3569`
- `back:main`: `bot/handlers/admin.py:4852`
- `bank:balance`: `bot/handlers/bank.py:72`
- `bank:history`: `bot/handlers/bank.py:403`
- `bank:menu`: `bot/handlers/bank.py:191`
- `bank:transfer`: `bot/handlers/bank.py:131`
- `bank:transfer_manual`: `bot/handlers/bank.py:147`
- `bank:treasury`: `bot/handlers/bank.py:204`
- `booklet:claim`: `bot/handlers/tourist_booklet.py:71`
- `booklet:menu`: `bot/handlers/tourist_booklet.py:65`
- `cancel`: `bot/handlers/admin.py:4860`
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
- `del_item:back`: `bot/handlers/admin.py:1691`
- `duel:card:buy`: `bot/handlers/duel.py:246`
- `duel:help`: `bot/handlers/duel.py:224`
- `duel:list`: `bot/handlers/duel.py:272`
- `duel:menu`: `bot/handlers/duel.py:218`
- `duel:top`: `bot/handlers/duel.py:292`
- `dungeon:enemies`: `bot/handlers/admin.py:5488`
- `dungeon:exit`: `bot/handlers/dungeon.py:2430`
- `dungeon:exit:cancel`: `bot/handlers/dungeon.py:2509`
- `dungeon:exit:confirm`: `bot/handlers/dungeon.py:2477`
- `dungeon:photos`: `bot/handlers/admin.py:5250`
- `dungeon:photos:clear`: `bot/handlers/admin.py:5294`
- `enemy:fi`: `bot/handlers/admin.py:8616`
- `field:drink`: `bot/handlers/admin.py:1962`
- `field:loot_only`: `bot/handlers/admin.py:2026`
- `field:market_ok`: `bot/handlers/admin.py:2006`
- `field:photo`: `bot/handlers/admin.py:1883`
- `field:weapon_effect`: `bot/handlers/admin.py:1903`
- `fin:manual`: `bot/handlers/admin.py:2530`
- `forest:addlist`: `bot/handlers/admin.py:7315`
- `forest:new`: `bot/handlers/admin.py:7468`
- `forest:zset:sold_daily_limit`: `bot/handlers/admin.py:7154`
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
- `loc:building_pick`: `bot/handlers/admin.py:7646`
- `loc:clearing_clear`: `bot/handlers/admin.py:8253`
- `loc:clearing_set`: `bot/handlers/admin.py:8216`
- `loc:create`: `bot/handlers/admin.py:7614`
- `loc:edit_pick`: `bot/handlers/admin.py:7630`
- `loc:glade_clear`: `bot/handlers/admin.py:8203`
- `loc:glade_set`: `bot/handlers/admin.py:8165`
- `loc:mine_clear`: `bot/handlers/admin.py:8304`
- `loc:mine_set`: `bot/handlers/admin.py:8266`
- `loc:photos`: `bot/handlers/admin.py:8091`
- `loc:photos:clear`: `bot/handlers/admin.py:8395`
- `loc:photos:clear_seasons`: `bot/handlers/admin.py:8114`
- `loc:set_blocking`: `bot/handlers/admin.py:7783`
- `loc:set_desc`: `bot/handlers/admin.py:7940`
- `loc:set_mode`: `bot/handlers/admin.py:7712`
- `loc:set_name`: `bot/handlers/admin.py:7901`
- `loc:set_status`: `bot/handlers/admin.py:7755`
- `news:archive`: `bot/handlers/news.py:132`
- `news:no_photo`: `bot/handlers/news.py:350`
- `news:tab`: `bot/handlers/news.py:259`
- `news:write`: `bot/handlers/news.py:279`
- `nii:all`: `bot/handlers/nii.py:232`
- `nii:menu_back`: `bot/handlers/nii.py:226`
- `nii:mine`: `bot/handlers/nii.py:207`
- `nii:no_photo`: `bot/handlers/nii.py:128`
- `nii:write`: `bot/handlers/nii.py:76`
- `noop`: `bot/handlers/admin.py:4847`
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
- `rep:auto_approve_edit`: `bot/handlers/admin.py:4100`
- `rep:next`: `bot/handlers/admin.py:4542`
- `rep:pay_cap_edit`: `bot/handlers/admin.py:4139`
- `rep:speech`: `bot/handlers/representative.py:77`
- `rep:speech:delete`: `bot/handlers/representative.py:109`
- `rep:speech:write`: `bot/handlers/representative.py:89`
- `report:my_reports`: `bot/handlers/reports.py:285`
- `report:submit`: `bot/handlers/reports.py:43`
- `salary:choose`: `bot/handlers/admin.py:5022`
- `salary:pay`: `bot/handlers/admin.py:5034`
- `shop:catalog`: `bot/handlers/shop.py:228`
- `shop_admin:add`: `bot/handlers/admin.py:1202`
- `shop_admin:delete`: `bot/handlers/admin.py:1662`
- `shop_admin:edit`: `bot/handlers/admin.py:1785`
- `shop_admin:special_code`: `bot/handlers/admin.py:2487`
- `shop_del:cats`: `bot/handlers/admin.py:1779`
- `shop_edit:cats`: `bot/handlers/admin.py:1764`
- `st:create`: `bot/handlers/admin.py:2977`
- `st:delete`: `bot/handlers/admin.py:3050`
- `st:grant`: `bot/handlers/admin.py:3250`
- `st:legioner`: `bot/handlers/admin.py:3195`
- `st:list`: `bot/handlers/admin.py:2960`
- `st:more`: `bot/handlers/admin.py:3389`
- `st:revoke`: `bot/handlers/admin.py:3316`
- `storage:cats`: `bot/handlers/admin.py:958`
- `storage:create`: `bot/handlers/admin.py:1203`
- `storage:noop`: `bot/handlers/admin.py:953`
- `treasury:debts`: `bot/handlers/admin.py:2255`
- `treasury:give`: `bot/handlers/admin.py:2354`
- `treasury:stats`: `bot/handlers/admin.py:2302`
- `vote:close_cancel`: `bot/handlers/polls.py:332`
- `vote:create`: `bot/handlers/polls.py:224`
- `wall:archive`: `bot/handlers/wall.py:315`
- `wall:view`: `bot/handlers/wall.py:149`
- `wall:write`: `bot/handlers/wall.py:170`

### По префиксу (`F.data.startswith("...")`)

- `\d+$`: `bot/handlers/admin.py:1354`; `bot/handlers/admin.py:4957`; `bot/handlers/admin.py:7168`; `bot/handlers/reports.py:186`
- `\d{1,7}$`: `bot/handlers/reports.py:120`; `bot/handlers/reports.py:150`
- `act:`: `bot/handlers/admin.py:4754`
- `addreq:`: `bot/handlers/admin.py:1553`
- `aw_del:`: `bot/handlers/admin.py:3614`
- `aw_edit:`: `bot/handlers/admin.py:3794`
- `aw_ei:`: `bot/handlers/admin.py:3805`
- `aw_pick:`: `bot/handlers/admin.py:3925`
- `awr_grant:`: `bot/handlers/admin.py:3992`
- `bait:set:`: `bot/handlers/fishing.py:176`
- `bank:pickrecipient:`: `bot/handlers/bank.py:177`
- `bank:transfer:list:`: `bot/handlers/bank.py:137`
- `buy5_nord:`: `bot/handlers/shop.py:487`
- `buy_housing:`: `bot/handlers/shop.py:1001`
- `buy_housing_cancel:`: `bot/handlers/shop.py:992`
- `buy_nord:`: `bot/handlers/shop.py:477`
- `cat:`: `bot/handlers/admin.py:1275`
- `city/`: `bot/handlers/locations.py:84`
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
- `confirm_del_photo:`: `bot/handlers/admin.py:844`
- `contract:enter:\d+$`: `bot/handlers/dungeon.py:780`
- `contract:enter:confirm:`: `bot/handlers/dungeon.py:826`
- `contract:pick:`: `bot/handlers/dungeon.py:728`
- `del_item:`: `bot/handlers/admin.py:1676`
- `drinksel:`: `bot/handlers/admin.py:1308`
- `duel:accept:`: `bot/handlers/duel.py:399`
- `duel:atk:`: `bot/handlers/duel.py:529`
- `duel:cancel:`: `bot/handlers/duel.py:373`
- `duel:decline:`: `bot/handlers/duel.py:385`
- `duel:def:`: `bot/handlers/duel.py:545`
- `duel:invite:`: `bot/handlers/duel.py:310`
- `duel:leave:`: `bot/handlers/duel.py:448`
- `dungeon:attack:`: `bot/handlers/dungeon.py:1277`
- `dungeon:continue:`: `bot/handlers/dungeon.py:1078`
- `dungeon:edit:`: `bot/handlers/admin.py:5187`
- `dungeon:enemy:`: `bot/handlers/admin.py:5520`
- `dungeon:escape:`: `bot/handlers/dungeon.py:1893`
- `dungeon:photo_set:`: `bot/handlers/admin.py:5259`
- `dungeon:use_slot:`: `bot/handlers/dungeon.py:1594`
- `eddrop:`: `bot/handlers/admin.py:5845`
- `eddrop_del:`: `bot/handlers/admin.py:5931`
- `eddrop_desc:`: `bot/handlers/admin.py:6003`
- `eddrop_photo:`: `bot/handlers/admin.py:5949`
- `eddrop_set_ch:`: `bot/handlers/admin.py:5886`
- `eddrop_set_q:`: `bot/handlers/admin.py:5909`
- `eddrop_stat:`: `bot/handlers/admin.py:6098`
- `eddrop_stats:`: `bot/handlers/admin.py:6059`
- `eddrop_weff:`: `bot/handlers/admin.py:6161`
- `eddrop_weff_set:`: `bot/handlers/admin.py:6183`
- `edit_item:`: `bot/handlers/admin.py:1794`
- `editem_add:`: `bot/handlers/admin.py:5797`
- `editem_new:`: `bot/handlers/admin.py:5822`
- `editem_pick:`: `bot/handlers/admin.py:5752`
- `editset:drink:`: `bot/handlers/admin.py:1985`
- `editset:weff:`: `bot/handlers/admin.py:1919`
- `enemy:card:`: `bot/handlers/admin.py:8750`
- `enemy:dcard:`: `bot/handlers/admin.py:8678`
- `enemy:del:`: `bot/handlers/admin.py:8876`
- `enemy:dn:\d+$`: `bot/handlers/admin.py:8588`
- `enemy:dropadd:`: `bot/handlers/admin.py:9053`
- `enemy:dropch:`: `bot/handlers/admin.py:8980`
- `enemy:dropdel:`: `bot/handlers/admin.py:9006`
- `enemy:dropedit:`: `bot/handlers/admin.py:8942`
- `enemy:dropitem:`: `bot/handlers/admin.py:9018`
- `enemy:dropq:`: `bot/handlers/admin.py:8993`
- `enemy:drops:`: `bot/handlers/admin.py:8932`
- `enemy:fld:`: `bot/handlers/admin.py:8760`
- `enemy:list:[a-z]+:[\w-]+$`: `bot/handlers/admin.py:8636`
- `enemy:new:`: `bot/handlers/admin.py:9127`
- `enemy:photo:`: `bot/handlers/admin.py:8820`
- `enemy:tog:`: `bot/handlers/admin.py:8857`
- `enemy_drops:`: `bot/handlers/admin.py:5739`
- `enemy_field:`: `bot/handlers/admin.py:5533`
- `eqequip:[a-z0-9_]+:\d+$`: `bot/handlers/inventory.py:500`
- `eqlock:[a-z0-9_]+$`: `bot/handlers/inventory.py:488`
- `eqpart:`: `bot/handlers/admin.py:1386`
- `eqslot:[a-z0-9_]+$`: `bot/handlers/inventory.py:493`
- `equnequip:[a-z0-9_]+$`: `bot/handlers/inventory.py:532`
- `field:`: `bot/handlers/admin.py:2090`
- `field:required_status`: `bot/handlers/admin.py:1833`
- `field_req:`: `bot/handlers/admin.py:1866`
- `fin:`: `bot/handlers/admin.py:2540`
- `finuser:`: `bot/handlers/admin.py:2570`
- `fish:bait:\d+$`: `bot/handlers/fishing.py:478`
- `fish:bait:set:\d+:[a-z]+$`: `bot/handlers/fishing.py:520`
- `fish:cast:\d+$`: `bot/handlers/fishing.py:530`
- `fish:lake:\d+$`: `bot/handlers/fishing.py:471`
- `fishbuy:`: `bot/handlers/shop.py:790`
- `fishcatch:`: `bot/handlers/inventory.py:1275`
- `fishgo:`: `bot/handlers/inventory.py:1526`
- `fishing:addfish:`: `bot/handlers/admin.py:6589`
- `fishing:addlist:`: `bot/handlers/admin.py:6559`
- `fishing:del:`: `bot/handlers/admin.py:6612`
- `fishing:fish:`: `bot/handlers/admin.py:6479`
- `fishing:junk:`: `bot/handlers/admin.py:6335`
- `fishing:kind:`: `bot/handlers/admin.py:6493`
- `fishing:market:`: `bot/handlers/admin.py:6515`
- `fishing:new:`: `bot/handlers/admin.py:6637`
- `fishing:new_super:`: `bot/handlers/admin.py:6740`
- `fishing:super:`: `bot/handlers/admin.py:6537`
- `fishing:water:`: `bot/handlers/admin.py:6441`
- `fishing_field:`: `bot/handlers/admin.py:6799`
- `fishing_j:`: `bot/handlers/admin.py:6385`
- `fishmarket:`: `bot/handlers/inventory.py:1428`
- `fishoffer:`: `bot/handlers/shop.py:726`
- `fishprice:`: `bot/handlers/inventory.py:1508`
- `fishsell:`: `bot/handlers/inventory.py:1584`
- `fishuse:`: `bot/handlers/inventory.py:1283`
- `forest:add:`: `bot/handlers/admin.py:7340`
- `forest:area:\d+:(glade|clearing)$`: `bot/handlers/forest.py:427`
- `forest:battle:flee:\d+$`: `bot/handlers/forest.py:1052`
- `forest:battle:hit:\d+$`: `bot/handlers/forest.py:854`
- `forest:card:`: `bot/handlers/admin.py:7254`
- `forest:cast:\d+(?::(glade|clearing))?$`: `bot/handlers/forest.py:490`
- `forest:del:`: `bot/handlers/admin.py:7359`
- `forest:kind:`: `bot/handlers/admin.py:7268`
- `forest:market:`: `bot/handlers/admin.py:7293`
- `forest:new_kind:`: `bot/handlers/admin.py:7548`
- `forest:zadd:(glade|clearing):\d+$`: `bot/handlers/admin.py:7120`
- `forest:zaddlist:(glade|clearing)$`: `bot/handlers/admin.py:7093`
- `forest:zchance:(glade|clearing):\d+$`: `bot/handlers/admin.py:7066`
- `forest:zdel:(glade|clearing):\d+$`: `bot/handlers/admin.py:7081`
- `forest:zone:(glade|clearing)$`: `bot/handlers/admin.py:6994`
- `forest:zset:(glade|clearing):(\w+)$`: `bot/handlers/admin.py:7132`
- `forest_field:`: `bot/handlers/admin.py:7380`
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
- `loc:blocking:`: `bot/handlers/admin.py:7799`
- `loc:building:`: `bot/handlers/admin.py:7688`
- `loc:edit:`: `bot/handlers/admin.py:7662`
- `loc:mode:`: `bot/handlers/admin.py:7728`
- `loc:photo_set:`: `bot/handlers/admin.py:8317`
- `loc:req_status:`: `bot/handlers/admin.py:7764`
- `loc:season:(winter|spring|summer|autumn)$`: `bot/handlers/admin.py:8101`
- `loc:season_clear:(winter|spring|summer|autumn)$`: `bot/handlers/admin.py:8127`
- `loc:season_photo_set:(winter|spring|summer|autumn):(dawn|day|sunset|night)$`: `bot/handlers/admin.py:8354`
- `location:enter:`: `bot/handlers/locations.py:104`
- `location:preview:`: `bot/handlers/locations.py:35`
- `locstat:`: `bot/handlers/admin.py:4813`
- `lootonly:`: `bot/handlers/admin.py:1528`
- `marketok:`: `bot/handlers/admin.py:1506`
- `mine:battle:flee:\d+$`: `bot/handlers/mine.py:664`
- `mine:battle:hit:\d+$`: `bot/handlers/mine.py:564`
- `mine:deeper:\d+$`: `bot/handlers/mine.py:387`
- `mine:dig:\d+$`: `bot/handlers/mine.py:398`
- `mine:level:\d+$`: `bot/handlers/mine.py:355`
- `mine:menu:\d+$`: `bot/handlers/mine.py:348`
- `mollusk:flee:\d+$`: `bot/handlers/dungeon.py:459`
- `mollusk:hit:\d+$`: `bot/handlers/dungeon.py:365`
- `news:(?:off|(?:dis)?allow:-?\d+|chat:-?\d+:-?\d+|topic:-?\d+:-?\d+)$`: `bot/handlers/admin.py:2862`
- `news:arch:\d+$`: `bot/handlers/news.py:179`
- `news:del:`: `bot/handlers/news.py:473`
- `news:delconf:`: `bot/handlers/news.py:495`
- `news:edit:`: `bot/handlers/news.py:400`
- `news:view:`: `bot/handlers/news.py:196`
- `nii:set:`: `bot/handlers/nii.py:299`
- `nii:view:`: `bot/handlers/nii.py:263`
- `page`: `bot/handlers/admin.py:402`
- `park:admin:del:`: `bot/handlers/park.py:390`
- `park:admin:delyes:`: `bot/handlers/park.py:408`
- `park:admin:edit:`: `bot/handlers/park.py:474`
- `park:adminedit:f:`: `bot/handlers/park.py:492`
- `park:statue:`: `bot/handlers/park.py:257`
- `pickuser:`: `bot/handlers/admin.py:393`
- `pollarch:day:\d{4}-\d{2}-\d{2}(?::\d+)?$`: `bot/handlers/poll_archive.py:176`
- `pollarch:days:\d+$`: `bot/handlers/poll_archive.py:154`
- `prod:`: `bot/handlers/admin.py:1466`
- `prof_sel_status:`: `bot/handlers/profile.py:321`
- `profile:award:`: `bot/handlers/profile.py:541`
- `rank_pick:`: `bot/handlers/admin.py:4646`
- `rank_promote:`: `bot/handlers/admin.py:4605`
- `rar:`: `bot/handlers/admin.py:1266`
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
- `rep:nav:`: `bot/handlers/admin.py:4531`
- `rep_fix:`: `bot/handlers/admin.py:4330`
- `rep_no:`: `bot/handlers/admin.py:4516`
- `rep_ok:`: `bot/handlers/admin.py:4447`
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
- `role:`: `bot/handlers/admin.py:2775`
- `rolop:`: `bot/handlers/admin.py:2726`
- `salary_period:`: `bot/handlers/admin.py:5099`
- `shop_del:cat:`: `bot/handlers/admin.py:1770`
- `shop_edit:cat:`: `bot/handlers/admin.py:1755`
- `shopcat:[^:]+$`: `bot/handlers/shop.py:248`
- `shopcat:[^:]+:\d+$`: `bot/handlers/shop.py:332`
- `shopitem:`: `bot/handlers/shop.py:343`
- `st_del:`: `bot/handlers/admin.py:3069`
- `st_key:`: `bot/handlers/admin.py:4942`
- `st_op:`: `bot/handlers/admin.py:4912`
- `st_pick:`: `bot/handlers/admin.py:3351`
- `st_rev:`: `bot/handlers/admin.py:3281`
- `storage:cat:`: `bot/handlers/admin.py:971`
- `storage:item:`: `bot/handlers/admin.py:1002`
- `storage:page:`: `bot/handlers/admin.py:988`
- `storage:purge:`: `bot/handlers/admin.py:1128`
- `storage:restock:`: `bot/handlers/admin.py:1060`
- `toggle:`: `bot/handlers/admin.py:7804`
- `vote:cast:`: `bot/handlers/polls.py:163`
- `vote:close:`: `bot/handlers/polls.py:287`
- `vote:close_confirm:`: `bot/handlers/polls.py:310`
- `vote:results:`: `bot/handlers/polls.py:185`
- `vote:show:`: `bot/handlers/polls.py:109`
- `wall:archpage:\d+$`: `bot/handlers/wall.py:338`
- `wall:archread:\d+(?::\d+)?$`: `bot/handlers/wall.py:357`
- `wall:delete:\d+$`: `bot/handlers/wall.py:224`
- `wall:page:\d+$`: `bot/handlers/wall.py:156`
- `weff:`: `bot/handlers/admin.py:1399`
- `wing_set:`: `bot/handlers/admin.py:819`
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

