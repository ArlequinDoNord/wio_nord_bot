# Карта FSM-состояний и callback-неймспейсов N.O.R.D.

> **Сгенерировано** `tools/export_states.py`. Не редактировать вручную —
> правь код и перегенерируй: `.venv\Scripts\python.exe tools/export_states.py`.
>
> Назначение: единый обзор всех `StatesGroup`, где они ставятся и где ловятся,
> а также реестр `callback_data` — чтобы не допускать конфликтов меню/хендлеров.

Всего классов состояний: **58**; полей-состояний: **244**; уникальных `callback_data`: **280**.

## 1. Классы состояний по модулям

### `AdminAddItem` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `name` | `bot/handlers/admin.py:1423` `shop_admin_add`<br>`bot/handlers/admin.py:7044` `enemy_drop_new_item` | `bot/handlers/admin.py:1431` `add_item_name` |
| `desc` | `bot/handlers/admin.py:1433` `add_item_name` | `bot/handlers/admin.py:1439` `add_item_desc` |
| `price` | `bot/handlers/admin.py:1442` `add_item_desc` | `bot/handlers/admin.py:1448` `add_item_price` |
| `sell_price` | `bot/handlers/admin.py:1458` `add_item_price` | `bot/handlers/admin.py:1464` `add_item_sell_price` |
| `rarity` | `bot/handlers/admin.py:1476` `add_item_sell_price` | — |
| `category` | `bot/handlers/admin.py:1485` `add_item_rarity` | — |
| `drink` | `bot/handlers/admin.py:1508` `add_item_category` | — |
| `plant_name` | `bot/handlers/admin.py:1497` `add_item_category` | `bot/handlers/admin.py:1533` `add_item_plant_name` |
| `stock` | `bot/handlers/admin.py:1517` `add_item_category`<br>`bot/handlers/admin.py:1527` `add_item_drink_choice`<br>`bot/handlers/admin.py:1536` `add_item_plant_name` | `bot/handlers/admin.py:1542` `add_item_stock` |
| `stats` | `bot/handlers/admin.py:1556` `add_item_stock`<br>`bot/handlers/admin.py:1561` `add_item_stock` | `bot/handlers/admin.py:1569` `add_item_stats`<br>`bot/handlers/admin.py:1609` `add_item_stats_bad` |
| `equip_slot` | `bot/handlers/admin.py:1586` `add_item_stats` | — |
| `weapon_effect` | `bot/handlers/admin.py:1574` `add_item_stats` | — |
| `weapon_effect_chance` | `bot/handlers/admin.py:1622` `add_item_weapon_effect_cb` | `bot/handlers/admin.py:1631` `add_item_weapon_effect_chance` |
| `weapon_effect_dmg` | `bot/handlers/admin.py:1643` `add_item_weapon_effect_chance` | `bot/handlers/admin.py:1655` `add_item_weapon_effect_dmg` |
| `producer` | `bot/handlers/admin.py:1670` `_go_add_item_producer` | — |
| `producer_user` | `bot/handlers/admin.py:1685` `add_item_producer` | `bot/handlers/admin.py:1697` `add_item_producer_user` |
| `market` | `bot/handlers/admin.py:1708` `_go_add_item_market` | — |
| `loot` | `bot/handlers/admin.py:1730` `_go_add_item_loot` | — |
| `status` | `bot/handlers/admin.py:1758` `_go_add_item_status` | — |
| `photo` | `bot/handlers/admin.py:1777` `add_item_status_cb` | `bot/handlers/admin.py:1785` `add_item_photo` |

### `AdminSaleTax` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `percent` | `bot/handlers/admin.py:2685` `admin_saletax_view` | `bot/handlers/admin.py:2699` `admin_saletax_set` |

### `AdminSpecialCode` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `code` | `bot/handlers/admin.py:2727` `admin_special_code_view` | `bot/handlers/admin.py:2742` `admin_special_code_set` |

### `AdminEditItem` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `item_id` | — | — |
| `field` | `bot/handlers/admin.py:2013` `edit_item_pick` | — |
| `value` | `bot/handlers/admin.py:2332` `edit_item_field` | `bot/handlers/admin.py:2343` `edit_item_value` |
| `photo` | `bot/handlers/admin.py:2102` `edit_item_field_photo` | `bot/handlers/admin.py:2165` `edit_item_photo` |

### `AdminFinance` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | `bot/handlers/admin.py:2768` `finance_manual`<br>`bot/handlers/admin.py:2790` `finance_pick` | `bot/handlers/admin.py:3175` `finance_target` |
| `currency` | — | — |
| `amount` | `bot/handlers/admin.py:483` `pickuser_cb`<br>`bot/handlers/admin.py:2860` `finance_pick_user`<br>`bot/handlers/admin.py:3182` `finance_target` | `bot/handlers/admin.py:3190` `finance_amount` |

### `AdminTreasury` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `amount` | `bot/handlers/admin.py:2592` `treasury_give` | `bot/handlers/admin.py:2602` `treasury_amount` |
| `target` | `bot/handlers/admin.py:2618` `treasury_amount` | `bot/handlers/admin.py:2624` `treasury_target_manual` |

### `AdminStorageRestock` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `amount` | `bot/handlers/admin.py:1285` `storage_restock` | `bot/handlers/admin.py:1299` `storage_restock_amount` |

### `AdminRestockAuto` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | `bot/handlers/admin.py:1214` `storage_auto_toggle`<br>`bot/handlers/admin.py:1237` `storage_auto_target` | `bot/handlers/admin.py:1245` `storage_auto_target_value` |

### `AdminShopLimit` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `value` | `bot/handlers/admin.py:1150` `storage_shop_limit_ask` | `bot/handlers/admin.py:1159` `storage_shop_limit_value` |

### `AdminStorageDelete` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `confirm` | `bot/handlers/admin.py:1357` `storage_purge` | `bot/handlers/admin.py:1371` `storage_purge_confirm` |

### `AdminTax` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `percent` | `bot/handlers/admin.py:2648` `admin_tax_view` | `bot/handlers/admin.py:2660` `admin_tax_set` |

### `AdminReportAutoApprove` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `value` | `bot/handlers/admin.py:5007` `report_auto_approve_edit_cb` | `bot/handlers/admin.py:5020` `report_auto_approve_edit_value` |

### `AdminReportPayCap` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `value` | `bot/handlers/admin.py:5046` `report_pay_cap_edit_cb` | `bot/handlers/admin.py:5061` `report_pay_cap_edit_value` |

### `AdminReportFix` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `daily` | `bot/handlers/admin.py:5247` `report_fix_start` | `bot/handlers/admin.py:5260` `report_fix_daily` |
| `total` | `bot/handlers/admin.py:5274` `report_fix_daily` | `bot/handlers/admin.py:5288` `report_fix_total` |

### `AdminReportReject` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `reason` | `bot/handlers/admin.py:5430` `report_reject` | `bot/handlers/admin.py:5438` `report_reject_reason` |

### `AdminRoles` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | `bot/handlers/admin.py:3268` `admin_roles` | `bot/handlers/admin.py:3277` `roles_target` |
| `action` | `bot/handlers/admin.py:486` `pickuser_cb`<br>`bot/handlers/admin.py:3283` `roles_target` | — |
| `role` | `bot/handlers/admin.py:3301` `roles_action` | — |

### `AdminStatuses` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `name` | `bot/handlers/admin.py:3552` `status_create_start` | `bot/handlers/admin.py:3560` `status_create_name` |
| `tag` | `bot/handlers/admin.py:3562` `status_create_name` | `bot/handlers/admin.py:3571` `status_create_tag` |
| `level` | `bot/handlers/admin.py:3578` `status_create_tag` | `bot/handlers/admin.py:3588` `status_create_level` |
| `desc` | `bot/handlers/admin.py:3599` `status_create_level` | `bot/handlers/admin.py:3604` `status_create_desc` |
| `target` | `bot/handlers/admin.py:3828` `status_grant_target`<br>`bot/handlers/admin.py:3897` `status_revoke_target` | `bot/handlers/admin.py:3838` `status_grant_target_msg` |
| `grant_action` | — | — |
| `status_pick` | `bot/handlers/admin.py:509` `pickuser_cb`<br>`bot/handlers/admin.py:518` `pickuser_cb`<br>`bot/handlers/admin.py:3849` `status_grant_target_msg`<br>`bot/handlers/admin.py:3981` `status_grant_more` | — |
| `item_pick` | — | — |
| `item_status` | — | — |

### `AdminAwards` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `name` | `bot/handlers/admin.py:4070` `award_create_start` | `bot/handlers/admin.py:4131` `award_create_name` |
| `desc` | `bot/handlers/admin.py:4137` `award_create_name` | `bot/handlers/admin.py:4145` `award_create_desc` |
| `emoji` | `bot/handlers/admin.py:4148` `award_create_desc` | `bot/handlers/admin.py:4156` `award_create_emoji` |
| `image` | `bot/handlers/admin.py:4160` `award_create_emoji` | `bot/handlers/admin.py:4168` `award_create_image` |
| `bonus` | `bot/handlers/admin.py:4122` `_award_ask_bonus` | `bot/handlers/admin.py:4181` `award_create_bonus` |
| `preview` | `bot/handlers/admin.py:4107` `_award_ask_bonus` | — |
| `target` | `bot/handlers/admin.py:4608` `award_grant_target` | `bot/handlers/admin.py:4614` `award_grant_target_msg` |
| `award_pick` | `bot/handlers/admin.py:4689` `award_revoke_pick_user` | — |
| `comment` | `bot/handlers/admin.py:4632` `award_grant_pick` | `bot/handlers/admin.py:4649` `award_grant_comment` |
| `edit_value` | `bot/handlers/admin.py:4470` `award_edit_field_pick` | `bot/handlers/admin.py:4494` `award_edit_value` |

### `AdminFishing` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `water` | — | — |
| `wf_id` | — | — |
| `value` | `bot/handlers/admin.py:7612` `admin_fishing_junk_field_pick`<br>`bot/handlers/admin.py:8186` `admin_fishing_field_pick` | `bot/handlers/admin.py:8213` `admin_fishing_value` |
| `c_name` | `bot/handlers/admin.py:8023` `admin_fishing_new` | `bot/handlers/admin.py:8032` `admin_fishing_new_name` |
| `c_desc` | `bot/handlers/admin.py:8042` `admin_fishing_new_name` | `bot/handlers/admin.py:8048` `admin_fishing_new_desc` |
| `c_sell_price` | `bot/handlers/admin.py:8051` `admin_fishing_new_desc` | `bot/handlers/admin.py:8057` `admin_fishing_new_sell_price` |
| `c_day_weight` | `bot/handlers/admin.py:8065` `admin_fishing_new_sell_price` | `bot/handlers/admin.py:8073` `admin_fishing_new_day_weight` |
| `c_night_weight` | `bot/handlers/admin.py:8081` `admin_fishing_new_day_weight` | `bot/handlers/admin.py:8089` `admin_fishing_new_night_weight` |
| `c_photo` | `bot/handlers/admin.py:8121` `admin_fishing_new_super` | `bot/handlers/admin.py:8129` `admin_fishing_new_photo` |
| `c_super_rare` | `bot/handlers/admin.py:8097` `admin_fishing_new_night_weight` | — |
| `j_name` | `bot/handlers/admin.py:7727` `admin_fishing_junk_new` | `bot/handlers/admin.py:7735` `admin_fishing_junk_new_name` |
| `j_sell` | `bot/handlers/admin.py:7741` `admin_fishing_junk_new_name` | `bot/handlers/admin.py:7747` `admin_fishing_junk_new_sell` |
| `j_chance` | `bot/handlers/admin.py:7753` `admin_fishing_junk_new_sell` | `bot/handlers/admin.py:7759` `admin_fishing_junk_new_chance` |
| `j_photo` | `bot/handlers/admin.py:7765` `admin_fishing_junk_new_chance` | `bot/handlers/admin.py:7772` `admin_fishing_junk_new_photo` |

### `AdminForest` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `f_id` | — | — |
| `field` | — | — |
| `value` | `bot/handlers/admin.py:8770` `admin_forest_field_pick` | `bot/handlers/admin.py:8796` `admin_forest_value` |
| `c_name` | `bot/handlers/admin.py:8852` `admin_forest_new` | `bot/handlers/admin.py:8861` `admin_forest_new_name` |
| `c_desc` | `bot/handlers/admin.py:8871` `admin_forest_new_name` | `bot/handlers/admin.py:8877` `admin_forest_new_desc` |
| `c_sell_price` | `bot/handlers/admin.py:8880` `admin_forest_new_desc` | `bot/handlers/admin.py:8886` `admin_forest_new_sell_price` |
| `c_chance` | `bot/handlers/admin.py:8893` `admin_forest_new_sell_price` | `bot/handlers/admin.py:8902` `admin_forest_new_chance` |
| `c_kind` | `bot/handlers/admin.py:8910` `admin_forest_new_chance` | — |
| `c_photo` | `bot/handlers/admin.py:8933` `admin_forest_new_kind` | `bot/handlers/admin.py:8941` `admin_forest_new_photo` |
| `zone_value` | `bot/handlers/admin.py:8450` `admin_forest_zone_chance`<br>`bot/handlers/admin.py:8525` `admin_forest_zone_set_pick`<br>`bot/handlers/admin.py:8538` `admin_forest_limit_set` | `bot/handlers/admin.py:8545` `admin_forest_zone_value` |

### `AdminEnemy` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `field` | `bot/handlers/admin.py:10397` `admin_enemies_field_pick` | `bot/handlers/admin.py:10403` `admin_enemies_field_value` |
| `photo` | `bot/handlers/admin.py:10454` `admin_enemies_photo_pick` | `bot/handlers/admin.py:10460` `admin_enemies_photo_value` |
| `onhit_value` | `bot/handlers/admin.py:6841` `source_enemy_effect_toggle` | `bot/handlers/admin.py:6847` `source_enemy_onhit_value` |
| `drop_chance` | `bot/handlers/admin.py:10614` `admin_enemies_drop_edit_chance`<br>`bot/handlers/admin.py:10688` `admin_enemies_drop_add_pick` | `bot/handlers/admin.py:10694` `admin_enemies_drop_chance_value` |
| `drop_qty` | `bot/handlers/admin.py:10627` `admin_enemies_drop_edit_qty`<br>`bot/handlers/admin.py:10715` `admin_enemies_drop_chance_value` | `bot/handlers/admin.py:10721` `admin_enemies_drop_qty_value` |
| `c_name` | `bot/handlers/admin.py:10760` `admin_enemies_new` | `bot/handlers/admin.py:10765` `admin_enemies_new_name` |
| `c_hp` | `bot/handlers/admin.py:10771` `admin_enemies_new_name` | `bot/handlers/admin.py:10776` `admin_enemies_new_hp` |
| `c_dmg` | `bot/handlers/admin.py:10782` `admin_enemies_new_hp` | `bot/handlers/admin.py:10787` `admin_enemies_new_dmg` |
| `c_dodge` | `bot/handlers/admin.py:10800` `admin_enemies_new_dmg` | `bot/handlers/admin.py:10805` `admin_enemies_new_dodge` |
| `c_chance` | `bot/handlers/admin.py:10811` `admin_enemies_new_dodge` | `bot/handlers/admin.py:10817` `admin_enemies_new_chance` |
| `c_loss_ap` | `bot/handlers/admin.py:10823` `admin_enemies_new_chance` | `bot/handlers/admin.py:10829` `admin_enemies_new_done` |

### `AdminCallsign` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | `bot/handlers/admin.py:799` `admin_callsign_start` | `bot/handlers/admin.py:820` `admin_callsign_target_msg` |
| `value` | `bot/handlers/admin.py:576` `pickuser_cb`<br>`bot/handlers/admin.py:830` `admin_callsign_target_msg` | `bot/handlers/admin.py:841` `admin_callsign_value_msg` |

### `AdminWing` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | `bot/handlers/admin.py:812` `admin_wing_start` | — |
| `value` | `bot/handlers/admin.py:587` `pickuser_cb` | — |

### `AdminStates` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | `bot/handlers/admin.py:5841` `admin_states_menu` | `bot/handlers/admin.py:5850` `admin_states_target_text` |
| `action` | `bot/handlers/admin.py:548` `pickuser_cb`<br>`bot/handlers/admin.py:5856` `admin_states_target_text` | — |
| `state_key` | `bot/handlers/admin.py:5885` `admin_states_op` | — |
| `minutes` | `bot/handlers/admin.py:5910` `admin_states_key` | `bot/handlers/admin.py:5919` `admin_states_minutes`<br>`bot/handlers/admin.py:5940` `admin_states_minutes_bad` |

### `AdminPlayerLog` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | `bot/handlers/admin.py:785` `admin_player_log_start` | `bot/handlers/admin.py:648` `admin_player_log_manual_msg` |

### `AdminSalary` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `amount` | `bot/handlers/admin.py:561` `pickuser_cb` | `bot/handlers/admin.py:6040` `admin_salary_amount` |

### `AdminLocation` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `action` | — | — |
| `target_id` | — | — |
| `key` | `bot/handlers/admin.py:8996` `loc_create` | `bot/handlers/admin.py:9260` `loc_step_key` |
| `name` | `bot/handlers/admin.py:9266` `loc_step_key` | `bot/handlers/admin.py:9271` `loc_step_name` |
| `set_name` | `bot/handlers/admin.py:9287` `loc_set_name` | `bot/handlers/admin.py:9298` `loc_step_set_name` |
| `description` | `bot/handlers/admin.py:9273` `loc_step_name`<br>`bot/handlers/admin.py:9312` `loc_step_set_name`<br>`bot/handlers/admin.py:9326` `loc_set_desc` | `bot/handlers/admin.py:9537` `loc_step_desc` |
| `mode` | `bot/handlers/admin.py:9092` `loc_set_mode`<br>`bot/handlers/admin.py:9548` `loc_step_desc` | `bot/handlers/admin.py:9105` `loc_mode_chosen` |
| `req_status` | `bot/handlers/admin.py:9118` `loc_mode_chosen`<br>`bot/handlers/admin.py:9127` `loc_mode_chosen`<br>`bot/handlers/admin.py:9136` `loc_set_status` | `bot/handlers/admin.py:9141` `loc_req_status_chosen` |
| `blocking` | `bot/handlers/admin.py:9124` `loc_mode_chosen`<br>`bot/handlers/admin.py:9155` `loc_req_status_chosen`<br>`bot/handlers/admin.py:9171` `loc_set_blocking` | `bot/handlers/admin.py:9176` `loc_blocking_chosen` |
| `preview` | `bot/handlers/admin.py:9574` `loc_glade_set`<br>`bot/handlers/admin.py:9660` `loc_fire_set`<br>`bot/handlers/admin.py:9708` `loc_clearing_set`<br>`bot/handlers/admin.py:9760` `loc_logging_set`<br>`bot/handlers/admin.py:9811` `loc_mine_set`<br>`bot/handlers/admin.py:9862` `loc_storage_set`<br>`bot/handlers/admin.py:9911` `loc_photo_set`<br>`bot/handlers/admin.py:9949` `loc_season_photo_set` | `bot/handlers/admin.py:9991` `loc_step_photo` |

### `AdminCityPhoto` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `photo` | `bot/handlers/admin.py:9606` `loc_city_fire` | `bot/handlers/admin.py:9625` `loc_city_fire_save` |

### `AdminDungeon` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target_id` | — | — |
| `photo_tod` | `bot/handlers/admin.py:6202` `dungeon_photo_set` | `bot/handlers/admin.py:6238` `dungeon_step_photo` |
| `enemy_id` | — | — |
| `enemy_field` | — | — |
| `enemy_value` | `bot/handlers/admin.py:6474` `dungeon_enemy_field_pick` | `bot/handlers/admin.py:6500` `dungeon_enemy_value` |
| `onhit_value` | `bot/handlers/admin.py:6765` `dungeon_enemy_effect_toggle` | `bot/handlers/admin.py:6771` `dungeon_enemy_onhit_value` |
| `drop_chance` | `bot/handlers/admin.py:1829` `add_item_photo`<br>`bot/handlers/admin.py:7021` `enemy_drop_pick_item`<br>`bot/handlers/admin.py:7104` `enemy_drop_set_chance` | `bot/handlers/admin.py:7426` `enemy_drop_chance_value` |
| `drop_qty` | `bot/handlers/admin.py:7127` `enemy_drop_set_qty`<br>`bot/handlers/admin.py:7435` `enemy_drop_chance_value` | `bot/handlers/admin.py:7441` `enemy_drop_qty_value` |
| `drop_item_photo` | `bot/handlers/admin.py:7172` `enemy_drop_item_photo` | `bot/handlers/admin.py:7181` `enemy_drop_item_photo_value` |
| `drop_item_desc` | `bot/handlers/admin.py:7226` `enemy_drop_item_desc` | `bot/handlers/admin.py:7235` `enemy_drop_item_desc_value` |
| `drop_item_field` | — | — |
| `drop_item_value` | `bot/handlers/admin.py:7324` `enemy_drop_item_stat_pick` | `bot/handlers/admin.py:7335` `enemy_drop_item_stat_value` |
| `pending_enemy_id` | — | — |

### `AdminFine` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `user_id` | `bot/handlers/admin.py:2909` `fines_new` | `bot/handlers/admin.py:2915` `fines_new_user` |
| `amount` | `bot/handlers/admin.py:502` `pickuser_cb`<br>`bot/handlers/admin.py:2931` `fines_new_user` | `bot/handlers/admin.py:2936` `fines_new_amount` |
| `reason` | `bot/handlers/admin.py:2943` `fines_new_amount` | `bot/handlers/admin.py:2948` `fines_new_reason` |

### `BerryAdmin` — `bot/handlers/admin_berries.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `chance` | `bot/handlers/admin_berries.py:89` `berry_chance` | `bot/handlers/admin_berries.py:96` `berry_chance_msg` |
| `c_name` | `bot/handlers/admin_berries.py:157` `berry_new` | `bot/handlers/admin_berries.py:163` `berry_new_name` |
| `c_sell` | `bot/handlers/admin_berries.py:169` `berry_new_name` | `bot/handlers/admin_berries.py:175` `berry_new_sell` |
| `c_chance` | `bot/handlers/admin_berries.py:181` `berry_new_sell` | `bot/handlers/admin_berries.py:186` `berry_new_chance` |

### `ClanPhotosAdmin` — `bot/handlers/admin_clanphotos.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `wait_exp_photo` | `bot/handlers/admin_clanphotos.py:136` `clanph_exp_cb` | `bot/handlers/admin_clanphotos.py:148` `clanph_exp_photo_save` |
| `wait_building_photo` | `bot/handlers/admin_clanphotos.py:341` `clanph_bset_cb` | `bot/handlers/admin_clanphotos.py:349` `clanph_building_photo_save` |
| `wait_construction_photo` | `bot/handlers/admin_clanphotos.py:180` `clanph_construction_cb` | `bot/handlers/admin_clanphotos.py:191` `clanph_construction_photo_save` |

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
| `waiting_recipient` | `bot/handlers/bank.py:152` `bank_transfer_manual` | `bot/handlers/bank.py:259` `process_recipient` |
| `waiting_amount` | `bot/handlers/bank.py:164` `set_recipient` | `bot/handlers/bank.py:281` `process_amount` |
| `waiting_message` | `bot/handlers/bank.py:324` `process_amount` | `bot/handlers/bank.py:333` `process_message` |
| `waiting_treasury_amount` | `bot/handlers/bank.py:210` `bank_treasury` | `bot/handlers/bank.py:220` `process_treasury_amount` |
| `waiting_fine_amount` | `bot/handlers/bank.py:464` `bank_fine_pay_part` | `bot/handlers/bank.py:470` `bank_fine_amount` |

### `ClanHallAdminPhoto` — `bot/handlers/clan_hall.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `wait_building_photo` | `bot/handlers/clan_hall.py:2193` `clan_hall_admphoto_cb` | `bot/handlers/clan_hall.py:2231` `clan_hall_admphoto_save` |
| `wait_construction_photo` | `bot/handlers/clan_hall.py:2224` `clan_hall_admconstphoto_cb` | `bot/handlers/clan_hall.py:2253` `clan_hall_admconstphoto_save` |
| `wait_expansion_photo` | `bot/handlers/clan_hall.py:2277` `clan_hall_admexphoto_cb` | `bot/handlers/clan_hall.py:2289` `clan_hall_admexphoto_save` |

### `ClansCreate` — `bot/handlers/clans.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `kind` | — | — |
| `wait_name` | `bot/handlers/clans.py:729` `clan_create_start` | `bot/handlers/clans.py:737` `clan_create_name` |
| `wait_desc` | `bot/handlers/clans.py:744` `clan_create_name` | `bot/handlers/clans.py:752` `clan_create_desc` |
| `wait_photo` | `bot/handlers/clans.py:762` `clan_create_desc` | `bot/handlers/clans.py:806` `clan_create_photo`<br>`bot/handlers/clans.py:813` `clan_create_photo_hint` |

### `ClansEdit` — `bot/handlers/clans.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `field` | — | — |
| `wait_value` | `bot/handlers/clans.py:877` `clan_edit_field_cb` | `bot/handlers/clans.py:883` `clan_edit_finish_photo`<br>`bot/handlers/clans.py:897` `clan_edit_finish_text` |

### `ClansMessage` — `bot/handlers/clans.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `wait_text` | `bot/handlers/clans.py:934` `clan_msg_start` | `bot/handlers/clans.py:942` `clan_msg_send` |

### `DungeonFSM` — `bot/handlers/dungeon.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `in_dungeon` | `bot/handlers/dungeon.py:937` `contract_enter_confirm`<br>`bot/handlers/dungeon.py:1016` `post_captain_menu`<br>`bot/handlers/dungeon.py:2492` `resv_deeper` | — |
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
| `target` | `bot/handlers/inventory.py:1721` `inv_transfer_start` | `bot/handlers/inventory.py:1730` `inv_transfer_target` |
| `amount` | `bot/handlers/inventory.py:1737` `inv_transfer_target` | `bot/handlers/inventory.py:1745` `inv_transfer_amount` |
| `message` | `bot/handlers/inventory.py:1777` `inv_transfer_amount` | `bot/handlers/inventory.py:1786` `inv_transfer_message` |

### `KvpFSM` — `bot/handlers/kvp.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `in_course` | `bot/handlers/kvp.py:292` `kvp_start`<br>`bot/handlers/kvp.py:316` `kvp_resume` | — |

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
| `title` | `bot/handlers/news.py:298` `news_write_start` | `bot/handlers/news.py:309` `news_write_title` |
| `body` | `bot/handlers/news.py:319` `news_write_title` | `bot/handlers/news.py:329` `news_write_body` |
| `photo` | `bot/handlers/news.py:342` `news_write_body` | `bot/handlers/news.py:360` `news_write_photo` |

### `NewsEdit` — `bot/handlers/news.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | — | — |
| `field` | `bot/handlers/news.py:415` `news_edit_start` | `bot/handlers/news.py:427` `news_edit_title` |
| `value` | `bot/handlers/news.py:445` `news_edit_title` | `bot/handlers/news.py:455` `news_edit_body` |

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
| `waiting_photo` | `bot/handlers/profile.py:259` `set_photo` | `bot/handlers/profile.py:267` `process_photo` |
| `waiting_about` | `bot/handlers/profile.py:280` `edit_about` | `bot/handlers/profile.py:288` `process_about` |
| `waiting_callsign` | `bot/handlers/profile.py:772` `profile_callsign`<br>`bot/handlers/profile.py:784` `profile_callsign`<br>`bot/handlers/profile.py:903` `profile_callsign_buy` | `bot/handlers/profile.py:821` `profile_callsign_input` |

### `ReportSubmit` — `bot/handlers/reports.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `waiting_photo` | `bot/handlers/reports.py:107` `report_submit_start` | `bot/handlers/reports.py:116` `report_receive_photo`<br>`bot/handlers/reports.py:131` `report_photo_expected` |
| `waiting_daily_troops` | `bot/handlers/reports.py:122` `report_receive_photo` | `bot/handlers/reports.py:136` `report_receive_daily_troops`<br>`bot/handlers/reports.py:160` `report_daily_troops_expected` |
| `waiting_total_troops` | `bot/handlers/reports.py:148` `report_receive_daily_troops` | `bot/handlers/reports.py:165` `report_receive_total_troops`<br>`bot/handlers/reports.py:196` `report_total_troops_expected` |
| `waiting_region` | `bot/handlers/reports.py:174` `report_receive_total_troops` | `bot/handlers/reports.py:201` `report_receive_region`<br>`bot/handlers/reports.py:295` `report_region_expected` |

### `RepSpeech` — `bot/handlers/representative.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `waiting_text` | `bot/handlers/representative.py:101` `rep_speech_write`<br>`bot/handlers/representative.py:128` `rep_speech_delete` | `bot/handlers/representative.py:176` `rep_speech_text` |

### `SpecialDeptBuy` — `bot/handlers/shop.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `code` | `bot/handlers/shop.py:529` `_start_special_dept_buy` | `bot/handlers/shop.py:541` `special_dept_enter_code` |

### `WallWrite` — `bot/handlers/wall.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `waiting_text` | `bot/handlers/wall.py:182` `wall_write_start` | `bot/handlers/wall.py:190` `wall_write_text` |

## 2. Реестр callback_data по неймспейсам

Все ключи, встречающиеся в фабриках кнопок (`callback_data=`), сгруппированы
по неймспейсу (текст до первого `:`). Это «занятые» префиксы: новый ключ
с таким же префиксом должен учитывать уже существующие фильтры (раздел 3).

| Неймспейс | Ключей | callback_data |
|---|---:|---|
| `addreq:` | 1 | `addreq:none` |
| `admin:` | 20 | `admin:awards`, `admin:dungeons`, `admin:enemies`, `admin:finance`, `admin:fishing`, `admin:forest`, `admin:locations`, `admin:menu`, `admin:ranks`, `admin:reports`, `admin:reports_done`, `admin:reports_pending`, `admin:reports_rejected`, `admin:salaries`, `admin:saletax`, `admin:shop`, `admin:statuses`, `admin:storage`, `admin:tax`, `admin:treasury` |
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
| `eqslot:` | 4 | `eqslot:clan_cape`, `eqslot:duel`, `eqslot:smoke`, `eqslot:talisman` |
| `field:` | 24 | `field:ap_cost`, `field:armor`, `field:category`, `field:damage`, `field:description`, `field:drink`, `field:heal`, `field:housing_slots`, `field:housing_type`, `field:is_available`, `field:loot_only`, `field:market_ok`, `field:name`, `field:photo`, `field:plant_name`, `field:price`, `field:rarity`, `field:regen`, `field:required_status`, `field:sell_price`, `field:stock`, `field:weapon_effect`, `field:weapon_effect_chance`, `field:weapon_effect_dmg` |
| `field_req:` | 1 | `field_req:none` |
| `fin:` | 3 | `fin:manual`, `fin:nord:add`, `fin:nord:sub` |
| `fines:` | 3 | `fines:list`, `fines:menu`, `fines:new` |
| `finh:` | 1 | `finh:open` |
| `fireevent:` | 5 | `fireevent:enter`, `fireevent:go`, `fireevent:potioncancel`, `fireevent:shop`, `fireevent:souvenir` |
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
| `profile:` | 7 | `profile`, `profile:awards:ach`, `profile:awards:awd`, `profile:callsign_buy`, `profile:callsign_cancel`, `profile:open`, `profile:recipes` |
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

- `admin:awards`: `bot/handlers/admin.py:3987`
- `admin:callsign`: `bot/handlers/admin.py:793`
- `admin:del_photo`: `bot/handlers/admin.py:767`
- `admin:dungeons`: `bot/handlers/admin.py:6100`
- `admin:enemies`: `bot/handlers/admin.py:10203`
- `admin:finance`: `bot/handlers/admin.py:2411`
- `admin:fishing`: `bot/handlers/admin.py:7795`
- `admin:forest`: `bot/handlers/admin.py:8358`
- `admin:locations`: `bot/handlers/admin.py:6075`
- `admin:logs`: `bot/handlers/admin.py:5637`
- `admin:menu`: `bot/handlers/admin.py:757`
- `admin:player_log`: `bot/handlers/admin.py:779`
- `admin:ranks`: `bot/handlers/admin.py:5527`
- `admin:reports`: `bot/handlers/admin.py:4710`
- `admin:reports_done`: `bot/handlers/admin.py:4767`
- `admin:reports_pending`: `bot/handlers/admin.py:4719`
- `admin:reports_rejected`: `bot/handlers/admin.py:4811`
- `admin:roles`: `bot/handlers/admin.py:3258`
- `admin:salaries`: `bot/handlers/admin.py:5944`
- `admin:saletax`: `bot/handlers/admin.py:2678`
- `admin:shop`: `bot/handlers/admin.py:908`
- `admin:states`: `bot/handlers/admin.py:5835`
- `admin:statuses`: `bot/handlers/admin.py:3492`
- `admin:storage`: `bot/handlers/admin.py:983`
- `admin:tax`: `bot/handlers/admin.py:2641`
- `admin:treasury`: `bot/handlers/admin.py:2454`
- `admin:wing`: `bot/handlers/admin.py:806`
- `aw:ach`: `bot/handlers/admin.py:4045`
- `aw:create`: `bot/handlers/admin.py:4063`
- `aw:delete`: `bot/handlers/admin.py:4233`
- `aw:edit`: `bot/handlers/admin.py:4423`
- `aw:grant`: `bot/handlers/admin.py:4605`
- `aw:list`: `bot/handlers/admin.py:4024`
- `aw:revoke`: `bot/handlers/admin.py:4686`
- `aw_comment:skip`: `bot/handlers/admin.py:4643`
- `aw_confirm`: `bot/handlers/admin.py:4201`
- `back:main`: `bot/handlers/admin.py:5810`
- `bank:balance`: `bot/handlers/bank.py:74`
- `bank:fines`: `bot/handlers/bank.py:435`
- `bank:menu`: `bot/handlers/bank.py:193`
- `bank:noop`: `bot/handlers/bank.py:540`
- `bank:transfer`: `bot/handlers/bank.py:133`
- `bank:transfer_manual`: `bot/handlers/bank.py:149`
- `bank:treasury`: `bot/handlers/bank.py:206`
- `booklet:claim`: `bot/handlers/tourist_booklet.py:71`
- `booklet:menu`: `bot/handlers/tourist_booklet.py:65`
- `cancel`: `bot/handlers/admin.py:5818`
- `city:business`: `bot/handlers/locations.py:247`
- `city:clans`: `bot/handlers/clans.py:92`
- `city:countryside`: `bot/handlers/locations.py:267`
- `city:dungeon`: `bot/handlers/dungeon.py:942`
- `city:library`: `bot/handlers/library.py:82`
- `city:menu`: `bot/handlers/start.py:186`
- `city:pilots`: `bot/handlers/pilots.py:102`
- `city:pilots:list`: `bot/handlers/pilots.py:129`
- `city:quarter`: `bot/handlers/locations.py:229`
- `city:vote`: `bot/handlers/polls.py:70`
- `clanh:noop`: `bot/handlers/clan_hall.py:2602`
- `clanhph:construction`: `bot/handlers/admin_clanphotos.py:174`
- `clanhph:menu`: `bot/handlers/admin_clanphotos.py:116`
- `clans:create_skip`: `bot/handlers/clans.py:817`
- `clans:noop`: `bot/handlers/clans.py:602`
- `clanshopadm:menu`: `bot/handlers/admin_shop_clan.py:103`
- `contracts:list`: `bot/handlers/dungeon.py:754`
- `del_item:back`: `bot/handlers/admin.py:1905`
- `duel:card:buy`: `bot/handlers/duel.py:246`
- `duel:help`: `bot/handlers/duel.py:224`
- `duel:list`: `bot/handlers/duel.py:278`
- `duel:menu`: `bot/handlers/duel.py:218`
- `duel:top`: `bot/handlers/duel.py:298`
- `dungeon:enemies`: `bot/handlers/admin.py:6416`
- `dungeon:exit`: `bot/handlers/dungeon.py:2635`
- `dungeon:exit:cancel`: `bot/handlers/dungeon.py:2720`
- `dungeon:exit:confirm`: `bot/handlers/dungeon.py:2682`
- `dungeon:photos`: `bot/handlers/admin.py:6183`
- `dungeon:photos:clear`: `bot/handlers/admin.py:6227`
- `enemy:fi`: `bot/handlers/admin.py:10241`
- `field:drink`: `bot/handlers/admin.py:2191`
- `field:loot_only`: `bot/handlers/admin.py:2255`
- `field:market_ok`: `bot/handlers/admin.py:2235`
- `field:photo`: `bot/handlers/admin.py:2097`
- `field:weapon_effect`: `bot/handlers/admin.py:2117`
- `fin:manual`: `bot/handlers/admin.py:2762`
- `fines:list`: `bot/handlers/admin.py:2972`
- `fines:menu`: `bot/handlers/admin.py:2891`
- `fines:new`: `bot/handlers/admin.py:2902`
- `finh:open`: `bot/handlers/admin.py:3101`
- `fireevent:enter`: `bot/handlers/fire_event.py:810`
- `fireevent:go`: `bot/handlers/fire_event.py:969`
- `fireevent:potioncancel`: `bot/handlers/fire_event.py:1404`
- `fireevent:shop`: `bot/handlers/fire_event.py:917`
- `fireevent:souvenir`: `bot/handlers/fire_event.py:841`
- `fireph:menu`: `bot/handlers/admin_firephotos.py:73`
- `fish:recover`: `bot/handlers/fishing.py:507`
- `forest:addlist`: `bot/handlers/admin.py:8691`
- `forest:new`: `bot/handlers/admin.py:8844`
- `forest:zset:sold_daily_limit`: `bot/handlers/admin.py:8530`
- `housing:menu`: `bot/handlers/housing.py:292`
- `housing:noop`: `bot/handlers/housing.py:865`
- `housing:pay_debt`: `bot/handlers/housing.py:340`
- `housing:pay_tax`: `bot/handlers/housing.py:331`
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
- `inventory:eq`: `bot/handlers/inventory.py:515`
- `inventory:list`: `bot/handlers/inventory.py:609`
- `kvp:exit`: `bot/handlers/kvp.py:752`
- `kvp:resume`: `bot/handlers/kvp.py:303`
- `kvp:start`: `bot/handlers/kvp.py:263`
- `lib:menu`: `bot/handlers/library.py:141`
- `lib:no_access`: `bot/handlers/library.py:136`
- `libadmin:add`: `bot/handlers/library.py:288`
- `libadmin:list`: `bot/handlers/library.py:384`
- `libadmin:menu`: `bot/handlers/library.py:271`
- `loc:building_pick`: `bot/handlers/admin.py:9022`
- `loc:city_fire`: `bot/handlers/admin.py:9598`
- `loc:clearing_clear`: `bot/handlers/admin.py:9732`
- `loc:clearing_set`: `bot/handlers/admin.py:9695`
- `loc:create`: `bot/handlers/admin.py:8990`
- `loc:edit_pick`: `bot/handlers/admin.py:9006`
- `loc:fire_set`: `bot/handlers/admin.py:9645`
- `loc:glade_clear`: `bot/handlers/admin.py:9682`
- `loc:glade_set`: `bot/handlers/admin.py:9560`
- `loc:logging_clear`: `bot/handlers/admin.py:9784`
- `loc:logging_set`: `bot/handlers/admin.py:9745`
- `loc:mine_clear`: `bot/handlers/admin.py:9835`
- `loc:mine_set`: `bot/handlers/admin.py:9797`
- `loc:photos`: `bot/handlers/admin.py:9486`
- `loc:photos:clear`: `bot/handlers/admin.py:9977`
- `loc:photos:clear_seasons`: `bot/handlers/admin.py:9509`
- `loc:set_blocking`: `bot/handlers/admin.py:9159`
- `loc:set_desc`: `bot/handlers/admin.py:9316`
- `loc:set_mode`: `bot/handlers/admin.py:9088`
- `loc:set_name`: `bot/handlers/admin.py:9277`
- `loc:set_status`: `bot/handlers/admin.py:9131`
- `loc:storage_clear`: `bot/handlers/admin.py:9886`
- `loc:storage_set`: `bot/handlers/admin.py:9848`
- `logsite:back`: `bot/handlers/logging_site.py:460`
- `logsite:enter`: `bot/handlers/logging_site.py:397`
- `mvd:menu`: `bot/handlers/mvd.py:29`
- `news:archive`: `bot/handlers/news.py:135`
- `news:no_photo`: `bot/handlers/news.py:353`
- `news:tab`: `bot/handlers/news.py:262`
- `news:write`: `bot/handlers/news.py:282`
- `nii:all`: `bot/handlers/nii.py:253`
- `nii:menu_back`: `bot/handlers/nii.py:247`
- `nii:mine`: `bot/handlers/nii.py:228`
- `nii:no_photo`: `bot/handlers/nii.py:130`
- `nii:write`: `bot/handlers/nii.py:77`
- `noop`: `bot/handlers/admin.py:5805`
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
- `prof:back`: `bot/handlers/profile.py:346`
- `profile`: `bot/handlers/profile.py:248`
- `profile:achievements`: `bot/handlers/profile.py:583`
- `profile:awards`: `bot/handlers/profile.py:559`
- `profile:callsign`: `bot/handlers/profile.py:757`
- `profile:callsign_buy`: `bot/handlers/profile.py:889`
- `profile:callsign_cancel`: `bot/handlers/profile.py:813`
- `profile:choose_status`: `bot/handlers/profile.py:306`
- `profile:edit_about`: `bot/handlers/profile.py:277`
- `profile:notify_toggle`: `bot/handlers/profile.py:353`
- `profile:open`: `bot/handlers/profile.py:750`
- `profile:pilot_card`: `bot/handlers/profile.py:393`
- `profile:public_toggle`: `bot/handlers/profile.py:373`
- `profile:recipes`: `bot/handlers/profile.py:722`
- `profile:set_photo`: `bot/handlers/profile.py:256`
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
- `rep:auto_approve_edit`: `bot/handlers/admin.py:5000`
- `rep:next`: `bot/handlers/admin.py:5500`
- `rep:pay_cap_edit`: `bot/handlers/admin.py:5039`
- `rep:speech`: `bot/handlers/representative.py:77`
- `rep:speech:delete`: `bot/handlers/representative.py:109`
- `rep:speech:write`: `bot/handlers/representative.py:89`
- `report:menu`: `bot/handlers/reports.py:52`
- `report:my_reports`: `bot/handlers/reports.py:404`
- `report:submit`: `bot/handlers/reports.py:62`
- `resv:recover`: `bot/handlers/dungeon.py:2438`
- `salary:choose`: `bot/handlers/admin.py:6002`
- `salary:pay`: `bot/handlers/admin.py:6014`
- `shop:catalog`: `bot/handlers/shop.py:233`
- `shop_admin:add`: `bot/handlers/admin.py:1416`
- `shop_admin:delete`: `bot/handlers/admin.py:1876`
- `shop_admin:edit`: `bot/handlers/admin.py:1999`
- `shop_admin:special_code`: `bot/handlers/admin.py:2719`
- `shop_del:cats`: `bot/handlers/admin.py:1993`
- `shop_edit:cats`: `bot/handlers/admin.py:1978`
- `st:create`: `bot/handlers/admin.py:3546`
- `st:delete`: `bot/handlers/admin.py:3619`
- `st:grant`: `bot/handlers/admin.py:3822`
- `st:legioner`: `bot/handlers/admin.py:3767`
- `st:list`: `bot/handlers/admin.py:3529`
- `st:more`: `bot/handlers/admin.py:3968`
- `st:revoke`: `bot/handlers/admin.py:3888`
- `storage:cats`: `bot/handlers/admin.py:1002`
- `storage:create`: `bot/handlers/admin.py:1417`
- `storage:menu`: `bot/handlers/storage.py:89`
- `storage:noop`: `bot/handlers/admin.py:997`
- `treasury:debts`: `bot/handlers/admin.py:2487`
- `treasury:give`: `bot/handlers/admin.py:2586`
- `treasury:stats`: `bot/handlers/admin.py:2534`
- `vote:close_cancel`: `bot/handlers/polls.py:332`
- `vote:create`: `bot/handlers/polls.py:224`
- `wall:archive`: `bot/handlers/wall.py:318`
- `wall:view`: `bot/handlers/wall.py:152`
- `wall:write`: `bot/handlers/wall.py:173`

### По префиксу (`F.data.startswith("...")`)

- `\d+$`: `bot/handlers/admin.py:1568`; `bot/handlers/admin.py:5918`; `bot/handlers/admin.py:8544`; `bot/handlers/reports.py:200`
- `\d{1,7}$`: `bot/handlers/reports.py:135`; `bot/handlers/reports.py:164`
- `act:`: `bot/handlers/admin.py:5712`
- `addreq:`: `bot/handlers/admin.py:1767`
- `aw_del:`: `bot/handlers/admin.py:4254`
- `aw_edit:`: `bot/handlers/admin.py:4443`
- `aw_ei:`: `bot/handlers/admin.py:4454`
- `aw_kind:`: `bot/handlers/admin.py:4576`
- `aw_pick:`: `bot/handlers/admin.py:4627`
- `awr_grant:`: `bot/handlers/admin.py:4694`
- `bait:set:`: `bot/handlers/fishing.py:183`
- `bank:history`: `bot/handlers/bank.py:490`
- `bank:pickrecipient:`: `bot/handlers/bank.py:179`
- `bank:transfer:list:`: `bot/handlers/bank.py:139`
- `berry:add:(glade|clearing)$`: `bot/handlers/admin_berries.py:117`
- `berry:chance:(glade|clearing):.+$`: `bot/handlers/admin_berries.py:83`
- `berry:del:(glade|clearing):.+$`: `bot/handlers/admin_berries.py:107`
- `berry:new:(glade|clearing)$`: `bot/handlers/admin_berries.py:149`
- `berry:pick:(glade|clearing):\d+$`: `bot/handlers/admin_berries.py:135`
- `berry:row:(glade|clearing):.+$`: `bot/handlers/admin_berries.py:63`
- `berry:zone:(glade|clearing)$`: `bot/handlers/admin_berries.py:54`
- `buy5_nord:`: `bot/handlers/shop.py:496`
- `buy_housing:`: `bot/handlers/shop.py:1134`
- `buy_housing_cancel:`: `bot/handlers/shop.py:1125`
- `buy_nord:`: `bot/handlers/shop.py:486`
- `cat:`: `bot/handlers/admin.py:1489`
- `city/`: `bot/handlers/locations.py:91`
- `city:pilots:list:`: `bot/handlers/pilots.py:135`
- `clanh:admconstphoto:`: `bot/handlers/clan_hall.py:2216`
- `clanh:admexphoto:`: `bot/handlers/clan_hall.py:2263`
- `clanh:admnophoto:`: `bot/handlers/clan_hall.py:2201`
- `clanh:admphoto:`: `bot/handlers/clan_hall.py:2182`
- `clanh:bitem:`: `bot/handlers/clan_hall.py:1268`
- `clanh:buy:`: `bot/handlers/clan_hall.py:1311`
- `clanh:cancel:`: `bot/handlers/clan_hall.py:2048`
- `clanh:choose:`: `bot/handlers/clan_hall.py:2017`
- `clanh:craft:`: `bot/handlers/clan_hall.py:1639`
- `clanh:donate:`: `bot/handlers/clan_hall.py:2343`
- `clanh:expchoose:`: `bot/handlers/clan_hall.py:1506`
- `clanh:expinstall:`: `bot/handlers/clan_hall.py:1519`
- `clanh:expmanage:`: `bot/handlers/clan_hall.py:1495`
- `clanh:expup:`: `bot/handlers/clan_hall.py:1537`
- `clanh:give:`: `bot/handlers/clan_hall.py:2389`
- `clanh:hall:`: `bot/handlers/clan_hall.py:1997`
- `clanh:harvest:`: `bot/handlers/clan_hall.py:1934`
- `clanh:harvestall:`: `bot/handlers/clan_hall.py:1966`
- `clanh:inside:`: `bot/handlers/clan_hall.py:2124`
- `clanh:item:`: `bot/handlers/clan_hall.py:2358`
- `clanh:libgive:`: `bot/handlers/clan_hall.py:1379`
- `clanh:log:`: `bot/handlers/clan_hall.py:2438`
- `clanh:mushproc:`: `bot/handlers/clan_hall.py:1791`
- `clanh:mushrooms:`: `bot/handlers/clan_hall.py:1774`
- `clanh:plant:`: `bot/handlers/clan_hall.py:1910`
- `clanh:plantlist:`: `bot/handlers/clan_hall.py:1862`
- `clanh:recipe:`: `bot/handlers/clan_hall.py:1570`
- `clanh:shower:`: `bot/handlers/clan_hall.py:1826`
- `clanh:start:`: `bot/handlers/clan_hall.py:2062`
- `clanh:startfull:`: `bot/handlers/clan_hall.py:2091`
- `clanh:storage:`: `bot/handlers/clan_hall.py:2316`
- `clanh:tree_essence:`: `bot/handlers/clan_hall.py:1153`
- `clanh:tree_essence_inv:`: `bot/handlers/clan_hall.py:1188`
- `clanh:tree_essence_store:`: `bot/handlers/clan_hall.py:1216`
- `clanh:tree_medit:`: `bot/handlers/clan_hall.py:1137`
- `clanh:upgrade:`: `bot/handlers/clan_hall.py:2033`
- `clanh:use:`: `bot/handlers/clan_hall.py:1553`
- `clanh:wd:`: `bot/handlers/clan_hall.py:2501`
- `clanh:wditem:`: `bot/handlers/clan_hall.py:2519`
- `clanh:wdtake:`: `bot/handlers/clan_hall.py:2553`
- `clanhier:`: `bot/handlers/clans.py:291`
- `clanhph:bclan:`: `bot/handlers/admin_clanphotos.py:303`
- `clanhph:bclr:`: `bot/handlers/admin_clanphotos.py:314`
- `clanhph:bset:`: `bot/handlers/admin_clanphotos.py:327`
- `clanhph:buildings`: `bot/handlers/admin_clanphotos.py:227`
- `clanhph:exp:`: `bot/handlers/admin_clanphotos.py:125`
- `clans:add:`: `bot/handlers/clans.py:607`
- `clans:addset:`: `bot/handlers/clans.py:624`
- `clans:cancel:`: `bot/handlers/clans.py:412`
- `clans:create:`: `bot/handlers/clans.py:719`
- `clans:del:`: `bot/handlers/clans.py:971`
- `clans:delyes:`: `bot/handlers/clans.py:988`
- `clans:edit:`: `bot/handlers/clans.py:832`
- `clans:editf:`: `bot/handlers/clans.py:856`
- `clans:join:`: `bot/handlers/clans.py:375`
- `clans:kick:`: `bot/handlers/clans.py:557`
- `clans:leader:`: `bot/handlers/clans.py:648`
- `clans:leaderset:`: `bot/handlers/clans.py:665`
- `clans:leaderunset:`: `bot/handlers/clans.py:695`
- `clans:leave:`: `bot/handlers/clans.py:422`
- `clans:list:`: `bot/handlers/clans.py:132`
- `clans:manage:`: `bot/handlers/clans.py:501`
- `clans:msg:`: `bot/handlers/clans.py:926`
- `clans:reqno:`: `bot/handlers/clans.py:484`
- `clans:reqok:`: `bot/handlers/clans.py:460`
- `clans:view:`: `bot/handlers/clans.py:169`
- `clanshopadm:add:`: `bot/handlers/admin_shop_clan.py:134`
- `clanshopadm:clan:`: `bot/handlers/admin_shop_clan.py:121`
- `clanshopadm:del:`: `bot/handlers/admin_shop_clan.py:397`
- `clanshopadm:ep:`: `bot/handlers/admin_shop_clan.py:298`
- `clanshopadm:es:`: `bot/handlers/admin_shop_clan.py:332`
- `clanshopadm:hide:`: `bot/handlers/admin_shop_clan.py:369`
- `clanshopadm:it:`: `bot/handlers/admin_shop_clan.py:257`
- `clanshopadm:show:`: `bot/handlers/admin_shop_clan.py:383`
- `confirm_del_photo:`: `bot/handlers/admin.py:887`
- `contract:enter:\d+$`: `bot/handlers/dungeon.py:834`
- `contract:enter:confirm:`: `bot/handlers/dungeon.py:880`
- `contract:pick:`: `bot/handlers/dungeon.py:782`
- `del_item:`: `bot/handlers/admin.py:1890`
- `drinksel:`: `bot/handlers/admin.py:1522`
- `duel:accept:`: `bot/handlers/duel.py:405`
- `duel:atk:`: `bot/handlers/duel.py:535`
- `duel:cancel:`: `bot/handlers/duel.py:379`
- `duel:decline:`: `bot/handlers/duel.py:391`
- `duel:def:`: `bot/handlers/duel.py:551`
- `duel:invite:`: `bot/handlers/duel.py:316`
- `duel:leave:`: `bot/handlers/duel.py:454`
- `dungeon:attack:`: `bot/handlers/dungeon.py:1386`
- `dungeon:continue:`: `bot/handlers/dungeon.py:1187`
- `dungeon:edit:`: `bot/handlers/admin.py:6120`
- `dungeon:enemy:`: `bot/handlers/admin.py:6448`
- `dungeon:escape:`: `bot/handlers/dungeon.py:2015`
- `dungeon:photo_set:`: `bot/handlers/admin.py:6192`
- `dungeon:use_slot:`: `bot/handlers/dungeon.py:1698`
- `eddrop:`: `bot/handlers/admin.py:7052`
- `eddrop_del:`: `bot/handlers/admin.py:7138`
- `eddrop_desc:`: `bot/handlers/admin.py:7210`
- `eddrop_photo:`: `bot/handlers/admin.py:7156`
- `eddrop_set_ch:`: `bot/handlers/admin.py:7093`
- `eddrop_set_q:`: `bot/handlers/admin.py:7116`
- `eddrop_stat:`: `bot/handlers/admin.py:7305`
- `eddrop_stats:`: `bot/handlers/admin.py:7266`
- `eddrop_weff:`: `bot/handlers/admin.py:7368`
- `eddrop_weff_set:`: `bot/handlers/admin.py:7390`
- `edit_item:`: `bot/handlers/admin.py:2008`
- `editem_add:`: `bot/handlers/admin.py:7004`
- `editem_new:`: `bot/handlers/admin.py:7029`
- `editem_pick:`: `bot/handlers/admin.py:6959`
- `editset:drink:`: `bot/handlers/admin.py:2214`
- `editset:weff:`: `bot/handlers/admin.py:2133`
- `enemy:card:`: `bot/handlers/admin.py:10376`
- `enemy:dcard:`: `bot/handlers/admin.py:10303`
- `enemy:del:`: `bot/handlers/admin.py:10502`
- `enemy:dn:\d+$`: `bot/handlers/admin.py:10213`
- `enemy:dropadd:`: `bot/handlers/admin.py:10679`
- `enemy:dropch:`: `bot/handlers/admin.py:10606`
- `enemy:dropdel:`: `bot/handlers/admin.py:10632`
- `enemy:dropedit:`: `bot/handlers/admin.py:10568`
- `enemy:dropitem:`: `bot/handlers/admin.py:10644`
- `enemy:dropq:`: `bot/handlers/admin.py:10619`
- `enemy:drops:`: `bot/handlers/admin.py:10558`
- `enemy:effects:\d+$`: `bot/handlers/admin.py:6721`
- `enemy:fld:`: `bot/handlers/admin.py:10386`
- `enemy:fx:src:`: `bot/handlers/admin.py:6794`
- `enemy:fx:tog:\d+:\d+$`: `bot/handlers/admin.py:6740`
- `enemy:fxt:`: `bot/handlers/admin.py:6814`
- `enemy:list:[a-z]+:[\w-]+$`: `bot/handlers/admin.py:10261`
- `enemy:new:`: `bot/handlers/admin.py:10753`
- `enemy:photo:`: `bot/handlers/admin.py:10446`
- `enemy:tog:`: `bot/handlers/admin.py:10483`
- `enemy_drops:`: `bot/handlers/admin.py:6946`
- `enemy_field:`: `bot/handlers/admin.py:6461`
- `eqequip:[a-z0-9_]+:\d+$`: `bot/handlers/inventory.py:533`
- `eqlock:[a-z0-9_]+$`: `bot/handlers/inventory.py:521`
- `eqpart:`: `bot/handlers/admin.py:1600`
- `eqslot:[a-z0-9_]+$`: `bot/handlers/inventory.py:526`
- `equnequip:[a-z0-9_]+$`: `bot/handlers/inventory.py:565`
- `field:`: `bot/handlers/admin.py:2319`
- `field:required_status`: `bot/handlers/admin.py:2047`
- `field_req:`: `bot/handlers/admin.py:2080`
- `fin:`: `bot/handlers/admin.py:2775`
- `fine:part:`: `bot/handlers/bank.py:459`
- `fine:payall:`: `bot/handlers/bank.py:448`
- `fines:cancel:`: `bot/handlers/admin.py:2997`
- `finh:h:`: `bot/handlers/admin.py:3136`
- `finh:list:`: `bot/handlers/admin.py:3112`
- `finh:u:`: `bot/handlers/admin.py:3124`
- `finuser:`: `bot/handlers/admin.py:2850`
- `fireevent:attack:`: `bot/handlers/fire_event.py:1180`
- `fireevent:backfork:`: `bot/handlers/fire_event.py:762`
- `fireevent:bait:`: `bot/handlers/fire_event.py:468`
- `fireevent:baitset:`: `bot/handlers/fire_event.py:490`
- `fireevent:cont:`: `bot/handlers/fire_event.py:374`
- `fireevent:dgive:`: `bot/handlers/fire_event.py:738`
- `fireevent:donate:`: `bot/handlers/fire_event.py:724`
- `fireevent:fishing:`: `bot/handlers/fire_event.py:556`
- `fireevent:leave:`: `bot/handlers/fire_event.py:775`
- `fireevent:potion:`: `bot/handlers/fire_event.py:1305`
- `fireevent:potionok:`: `bot/handlers/fire_event.py:1398`
- `fireevent:step:`: `bot/handlers/fire_event.py:297`
- `fireevent:wellback:`: `bot/handlers/fire_event.py:508`
- `fireevent:xchg:`: `bot/handlers/fire_event.py:929`
- `fireph:set:`: `bot/handlers/admin_firephotos.py:82`
- `fish:bait:\d+$`: `bot/handlers/fishing.py:521`
- `fish:bait:set:\d+:[a-z]+$`: `bot/handlers/fishing.py:563`
- `fish:cast:\d+$`: `bot/handlers/fishing.py:573`
- `fish:lake:\d+$`: `bot/handlers/fishing.py:500`
- `fishbuy:`: `bot/handlers/shop.py:837`
- `fishcatch:`: `bot/handlers/inventory.py:1352`
- `fishgo:`: `bot/handlers/inventory.py:1603`
- `fishing:addfish:`: `bot/handlers/admin.py:7963`
- `fishing:addlist:`: `bot/handlers/admin.py:7933`
- `fishing:del:`: `bot/handlers/admin.py:7986`
- `fishing:fish:`: `bot/handlers/admin.py:7853`
- `fishing:junk:`: `bot/handlers/admin.py:7542`
- `fishing:kind:`: `bot/handlers/admin.py:7867`
- `fishing:market:`: `bot/handlers/admin.py:7889`
- `fishing:new:`: `bot/handlers/admin.py:8011`
- `fishing:new_super:`: `bot/handlers/admin.py:8114`
- `fishing:super:`: `bot/handlers/admin.py:7911`
- `fishing:water:`: `bot/handlers/admin.py:7815`
- `fishing_field:`: `bot/handlers/admin.py:8173`
- `fishing_j:`: `bot/handlers/admin.py:7599`
- `fishing_jx:del:`: `bot/handlers/admin.py:7695`
- `fishing_jx:new:`: `bot/handlers/admin.py:7716`
- `fishing_jx:pick:`: `bot/handlers/admin.py:7668`
- `fishing_jx:pool:`: `bot/handlers/admin.py:7639`
- `fishmarket:`: `bot/handlers/inventory.py:1505`
- `fishoffer:`: `bot/handlers/shop.py:762`
- `fishprice:`: `bot/handlers/inventory.py:1585`
- `fishsell:`: `bot/handlers/inventory.py:1661`
- `fishuse:`: `bot/handlers/inventory.py:1360`
- `forest:add:`: `bot/handlers/admin.py:8716`
- `forest:area:\d+:(glade|clearing)$`: `bot/handlers/forest.py:466`
- `forest:battle:flee:\d+$`: `bot/handlers/forest.py:1238`
- `forest:battle:hit:\d+$`: `bot/handlers/forest.py:1030`
- `forest:berry:\d+:(glade|clearing)$`: `bot/handlers/forest.py:747`
- `forest:card:`: `bot/handlers/admin.py:8630`
- `forest:cast:\d+(?::(glade|clearing))?$`: `bot/handlers/forest.py:550`
- `forest:del:`: `bot/handlers/admin.py:8735`
- `forest:kind:`: `bot/handlers/admin.py:8644`
- `forest:market:`: `bot/handlers/admin.py:8669`
- `forest:new_kind:`: `bot/handlers/admin.py:8924`
- `forest:zadd:(glade|clearing):\d+$`: `bot/handlers/admin.py:8496`
- `forest:zaddlist:(glade|clearing)$`: `bot/handlers/admin.py:8469`
- `forest:zchance:(glade|clearing):\d+$`: `bot/handlers/admin.py:8442`
- `forest:zdel:(glade|clearing):\d+$`: `bot/handlers/admin.py:8457`
- `forest:zone:(glade|clearing)$`: `bot/handlers/admin.py:8368`
- `forest:zset:(glade|clearing):(\w+)$`: `bot/handlers/admin.py:8508`
- `forest_field:`: `bot/handlers/admin.py:8756`
- `housing:craft:`: `bot/handlers/housing.py:806`
- `housing:harvest:`: `bot/handlers/housing.py:1138`
- `housing:install:`: `bot/handlers/housing.py:872`
- `housing:install_item:`: `bot/handlers/housing.py:910`
- `housing:kitchen:`: `bot/handlers/housing.py:409`
- `housing:lantern_medit:`: `bot/handlers/housing.py:677`
- `housing:move:`: `bot/handlers/housing.py:1159`
- `housing:mushproc:`: `bot/handlers/housing.py:519`
- `housing:mushrooms:`: `bot/handlers/housing.py:505`
- `housing:plant:`: `bot/handlers/housing.py:1117`
- `housing:recipe:`: `bot/handlers/housing.py:761`
- `housing:room:`: `bot/handlers/housing.py:351`
- `housing:shower:`: `bot/handlers/housing.py:602`
- `housing:uninstall:`: `bot/handlers/housing.py:1017`
- `housing:uninstall_confirm:`: `bot/handlers/housing.py:1083`
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
- `inv_equip:`: `bot/handlers/inventory.py:833`
- `inv_sell:`: `bot/handlers/inventory.py:968`
- `inv_sell_ask:`: `bot/handlers/inventory.py:1066`
- `inv_sell_keep1:`: `bot/handlers/inventory.py:988`
- `inv_sell_ok:`: `bot/handlers/inventory.py:1088`
- `inv_sellall:`: `bot/handlers/inventory.py:978`
- `inv_sellmore:`: `bot/handlers/inventory.py:1198`
- `inv_slot:`: `bot/handlers/inventory.py:887`
- `inv_transfer:`: `bot/handlers/inventory.py:1693`
- `inv_unequip:`: `bot/handlers/inventory.py:863`
- `inv_unslot:`: `bot/handlers/inventory.py:922`
- `inv_use:`: `bot/handlers/inventory.py:944`
- `inventory:cat:[^:]+$`: `bot/handlers/inventory.py:628`
- `invitem:`: `bot/handlers/inventory.py:826`
- `itembuy:`: `bot/handlers/shop.py:966`
- `itemgo:`: `bot/handlers/inventory.py:1296`
- `itemmarket:`: `bot/handlers/inventory.py:1206`
- `itemoffer:`: `bot/handlers/shop.py:898`
- `itemprice:`: `bot/handlers/inventory.py:1285`
- `kvp:attack:`: `bot/handlers/kvp.py:531`
- `kvp:attempt:`: `bot/handlers/kvp.py:456`
- `kvp:continue:`: `bot/handlers/kvp.py:425`
- `libadmin_del:`: `bot/handlers/library.py:409`
- `libadmin_sec:`: `bot/handlers/library.py:297`
- `libbook:`: `bot/handlers/library.py:204`
- `libdl:`: `bot/handlers/library.py:249`
- `libsec:[a-z]+$`: `bot/handlers/library.py:178`
- `loc:blocking:`: `bot/handlers/admin.py:9175`
- `loc:building:`: `bot/handlers/admin.py:9064`
- `loc:edit:`: `bot/handlers/admin.py:9038`
- `loc:mode:`: `bot/handlers/admin.py:9104`
- `loc:photo_set:`: `bot/handlers/admin.py:9899`
- `loc:req_status:`: `bot/handlers/admin.py:9140`
- `loc:season:(winter|spring|summer|autumn)$`: `bot/handlers/admin.py:9496`
- `loc:season_clear:(winter|spring|summer|autumn)$`: `bot/handlers/admin.py:9522`
- `loc:season_photo_set:(winter|spring|summer|autumn):(dawn|day|sunset|night)$`: `bot/handlers/admin.py:9936`
- `location:enter:`: `bot/handlers/locations.py:111`
- `location:preview:`: `bot/handlers/locations.py:40`
- `locstat:`: `bot/handlers/admin.py:5771`
- `logsite:battle:flee:\d+$`: `bot/handlers/logging_site.py:1097`
- `logsite:battle:hit:\d+$`: `bot/handlers/logging_site.py:893`
- `logsite:chop:\d+$`: `bot/handlers/logging_site.py:468`
- `logsite:fire:(1|all):\d+$`: `bot/handlers/logging_site.py:742`
- `logsite:menu:\d+$`: `bot/handlers/logging_site.py:453`
- `logsite:mill:\d+$`: `bot/handlers/logging_site.py:616`
- `logsite:plank:(1|all):\d+$`: `bot/handlers/logging_site.py:679`
- `lootonly:`: `bot/handlers/admin.py:1742`
- `marketok:`: `bot/handlers/admin.py:1720`
- `mine:battle:flee:\d+$`: `bot/handlers/mine.py:741`
- `mine:battle:hit:\d+$`: `bot/handlers/mine.py:589`
- `mine:deeper:\d+$`: `bot/handlers/mine.py:391`
- `mine:dig:\d+$`: `bot/handlers/mine.py:402`
- `mine:level:\d+$`: `bot/handlers/mine.py:358`
- `mine:menu:\d+$`: `bot/handlers/mine.py:351`
- `mollusk:flee:\d+$`: `bot/handlers/dungeon.py:507`
- `mollusk:hit:\d+$`: `bot/handlers/dungeon.py:375`
- `mvd:arch:`: `bot/handlers/mvd.py:95`
- `mvd:archive:`: `bot/handlers/mvd.py:45`
- `news:(?:off|(?:dis)?allow:-?\d+|chat:-?\d+:-?\d+|topic:-?\d+:-?\d+)$`: `bot/handlers/admin.py:3431`
- `news:arch:\d+$`: `bot/handlers/news.py:182`
- `news:del:`: `bot/handlers/news.py:476`
- `news:delconf:`: `bot/handlers/news.py:498`
- `news:edit:`: `bot/handlers/news.py:403`
- `news:view:`: `bot/handlers/news.py:199`
- `nii:set:`: `bot/handlers/nii.py:319`
- `nii:view:`: `bot/handlers/nii.py:284`
- `offercancel:fish:`: `bot/handlers/shop.py:1017`
- `offercancel:item:`: `bot/handlers/shop.py:1022`
- `page`: `bot/handlers/admin.py:439`
- `park:admin:del:`: `bot/handlers/park.py:390`
- `park:admin:delyes:`: `bot/handlers/park.py:410`
- `park:admin:edit:`: `bot/handlers/park.py:478`
- `park:adminedit:f:`: `bot/handlers/park.py:496`
- `park:statue:`: `bot/handlers/park.py:257`
- `pickuser:`: `bot/handlers/admin.py:430`
- `pollarch:day:\d{4}-\d{2}-\d{2}(?::\d+)?$`: `bot/handlers/poll_archive.py:176`
- `pollarch:days:\d+$`: `bot/handlers/poll_archive.py:154`
- `prod:`: `bot/handlers/admin.py:1680`
- `prof_sel_status:`: `bot/handlers/profile.py:331`
- `profile:award:`: `bot/handlers/profile.py:591`
- `profile:awards:(ach|awd)$`: `bot/handlers/profile.py:567`
- `profile:recipe:\d+$`: `bot/handlers/profile.py:737`
- `profile:recipes:\d+$`: `bot/handlers/profile.py:729`
- `rank_pick:`: `bot/handlers/admin.py:5604`
- `rank_promote:`: `bot/handlers/admin.py:5563`
- `rar:`: `bot/handlers/admin.py:1480`
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
- `rep:nav:`: `bot/handlers/admin.py:5489`
- `rep_fix:`: `bot/handlers/admin.py:5230`
- `rep_no:`: `bot/handlers/admin.py:5416`
- `rep_ok:`: `bot/handlers/admin.py:5347`
- `rep_rej_del:`: `bot/handlers/admin.py:4948`
- `rep_rej_del_ok:`: `bot/handlers/admin.py:4976`
- `rep_rej_list:`: `bot/handlers/admin.py:4899`
- `rep_rej_view:`: `bot/handlers/admin.py:4912`
- `report:my:`: `bot/handlers/reports.py:399`
- `report:view:`: `bot/handlers/reports.py:411`
- `resv:bait:\d+$`: `bot/handlers/dungeon.py:2135`
- `resv:bait:set:\d+:[a-z]+$`: `bot/handlers/dungeon.py:2183`
- `resv:cast:\d+$`: `bot/handlers/dungeon.py:2202`
- `resv:deeper:\d+$`: `bot/handlers/dungeon.py:2469`
- `resv:enter:\d+$`: `bot/handlers/dungeon.py:2097`
- `resv:eq:\d+$`: `bot/handlers/dungeon.py:2504`
- `resv:eqclear:[a-z0-9_]+:\d+$`: `bot/handlers/dungeon.py:2612`
- `resv:eqset:[a-z0-9_]+:\d+:\d+$`: `bot/handlers/dungeon.py:2588`
- `resv:eqslot:[a-z0-9_]+:\d+$`: `bot/handlers/dungeon.py:2542`
- `resv:menu:\d+$`: `bot/handlers/dungeon.py:2121`
- `role:`: `bot/handlers/admin.py:3344`
- `rolop:`: `bot/handlers/admin.py:3295`
- `shop_del:cat:`: `bot/handlers/admin.py:1984`
- `shop_edit:cat:`: `bot/handlers/admin.py:1969`
- `shopcat:[^:]+$`: `bot/handlers/shop.py:253`
- `shopcat:[^:]+:\d+$`: `bot/handlers/shop.py:341`
- `shopitem:`: `bot/handlers/shop.py:352`
- `st_del:`: `bot/handlers/admin.py:3638`
- `st_key:`: `bot/handlers/admin.py:5903`
- `st_op:`: `bot/handlers/admin.py:5870`
- `st_pick:`: `bot/handlers/admin.py:3923`
- `st_rev:`: `bot/handlers/admin.py:3853`
- `storage:auto:`: `bot/handlers/admin.py:1186`
- `storage:auto_target:`: `bot/handlers/admin.py:1227`
- `storage:auto_toggle:`: `bot/handlers/admin.py:1202`
- `storage:cat:`: `bot/handlers/admin.py:1015`
- `storage:item:`: `bot/handlers/admin.py:1048`
- `storage:page:`: `bot/handlers/admin.py:1034`
- `storage:purge:`: `bot/handlers/admin.py:1342`
- `storage:restock:`: `bot/handlers/admin.py:1274`
- `storage:shoplim:`: `bot/handlers/admin.py:1140`
- `toggle:`: `bot/handlers/admin.py:9180`
- `vote:cast:`: `bot/handlers/polls.py:163`
- `vote:close:`: `bot/handlers/polls.py:287`
- `vote:close_confirm:`: `bot/handlers/polls.py:310`
- `vote:results:`: `bot/handlers/polls.py:185`
- `vote:show:`: `bot/handlers/polls.py:109`
- `wall:archpage:\d+$`: `bot/handlers/wall.py:341`
- `wall:archread:\d+(?::\d+)?$`: `bot/handlers/wall.py:360`
- `wall:delete:\d+$`: `bot/handlers/wall.py:227`
- `wall:page:\d+$`: `bot/handlers/wall.py:159`
- `weff:`: `bot/handlers/admin.py:1613`
- `wing_set:`: `bot/handlers/admin.py:862`
- `Испорченн`: `bot/handlers/dungeon.py:1918`
- `⛔`: `bot/handlers/wall.py:179`

## 4. ⚠️ Возможные конфликты

- Дублей точных `F.data ==` фильтров не найдено.

**Префиксный фильтр перекрывает точный ключ** (проверь порядок регистрации):

- `startswith("field:")` ⇄ `== "field:weapon_effect"`
- `startswith("field:")` ⇄ `== "field:photo"`
- `startswith("field:")` ⇄ `== "field:drink"`
- `startswith("field:")` ⇄ `== "field:market_ok"`
- `startswith("field:")` ⇄ `== "field:loot_only"`
- `startswith("fin:")` ⇄ `== "fin:manual"`

