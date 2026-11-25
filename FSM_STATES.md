# Карта FSM-состояний и callback-неймспейсов N.O.R.D.

> **Сгенерировано** `tools/export_states.py`. Не редактировать вручную —
> правь код и перегенерируй: `.venv\Scripts\python.exe tools/export_states.py`.
>
> Назначение: единый обзор всех `StatesGroup`, где они ставятся и где ловятся,
> а также реестр `callback_data` — чтобы не допускать конфликтов меню/хендлеров.

Всего классов состояний: **60**; полей-состояний: **259**; уникальных `callback_data`: **293**.

## 1. Классы состояний по модулям

### `AdminAddItem` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `name` | `bot/handlers/admin.py:1437` `shop_admin_add`<br>`bot/handlers/admin.py:7146` `enemy_drop_new_item` | `bot/handlers/admin.py:1445` `add_item_name` |
| `desc` | `bot/handlers/admin.py:1447` `add_item_name` | `bot/handlers/admin.py:1453` `add_item_desc` |
| `price` | `bot/handlers/admin.py:1456` `add_item_desc` | `bot/handlers/admin.py:1462` `add_item_price` |
| `sell_price` | `bot/handlers/admin.py:1472` `add_item_price` | `bot/handlers/admin.py:1478` `add_item_sell_price` |
| `rarity` | `bot/handlers/admin.py:1490` `add_item_sell_price` | — |
| `category` | `bot/handlers/admin.py:1499` `add_item_rarity` | — |
| `drink` | `bot/handlers/admin.py:1522` `add_item_category` | — |
| `plant_name` | `bot/handlers/admin.py:1511` `add_item_category` | `bot/handlers/admin.py:1547` `add_item_plant_name` |
| `stock` | `bot/handlers/admin.py:1531` `add_item_category`<br>`bot/handlers/admin.py:1541` `add_item_drink_choice`<br>`bot/handlers/admin.py:1550` `add_item_plant_name` | `bot/handlers/admin.py:1556` `add_item_stock` |
| `stats` | `bot/handlers/admin.py:1570` `add_item_stock`<br>`bot/handlers/admin.py:1575` `add_item_stock` | `bot/handlers/admin.py:1583` `add_item_stats`<br>`bot/handlers/admin.py:1623` `add_item_stats_bad` |
| `equip_slot` | `bot/handlers/admin.py:1600` `add_item_stats` | — |
| `weapon_effect` | `bot/handlers/admin.py:1588` `add_item_stats` | — |
| `weapon_effect_chance` | `bot/handlers/admin.py:1636` `add_item_weapon_effect_cb` | `bot/handlers/admin.py:1645` `add_item_weapon_effect_chance` |
| `weapon_effect_dmg` | `bot/handlers/admin.py:1657` `add_item_weapon_effect_chance` | `bot/handlers/admin.py:1669` `add_item_weapon_effect_dmg` |
| `producer` | `bot/handlers/admin.py:1684` `_go_add_item_producer` | — |
| `producer_user` | `bot/handlers/admin.py:1699` `add_item_producer` | `bot/handlers/admin.py:1711` `add_item_producer_user` |
| `market` | `bot/handlers/admin.py:1722` `_go_add_item_market` | — |
| `loot` | `bot/handlers/admin.py:1744` `_go_add_item_loot` | — |
| `status` | `bot/handlers/admin.py:1772` `_go_add_item_status` | — |
| `photo` | `bot/handlers/admin.py:1791` `add_item_status_cb` | `bot/handlers/admin.py:1799` `add_item_photo` |

### `AdminSaleTax` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `percent` | `bot/handlers/admin.py:2699` `admin_saletax_view` | `bot/handlers/admin.py:2713` `admin_saletax_set` |

### `AdminSpecialCode` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `code` | `bot/handlers/admin.py:2741` `admin_special_code_view` | `bot/handlers/admin.py:2756` `admin_special_code_set` |

### `AdminEditItem` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `item_id` | — | — |
| `field` | `bot/handlers/admin.py:2027` `edit_item_pick` | — |
| `value` | `bot/handlers/admin.py:2346` `edit_item_field` | `bot/handlers/admin.py:2357` `edit_item_value` |
| `photo` | `bot/handlers/admin.py:2116` `edit_item_field_photo` | `bot/handlers/admin.py:2179` `edit_item_photo` |

### `AdminFinance` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | `bot/handlers/admin.py:2782` `finance_manual`<br>`bot/handlers/admin.py:2804` `finance_pick` | `bot/handlers/admin.py:3189` `finance_target` |
| `currency` | — | — |
| `amount` | `bot/handlers/admin.py:497` `pickuser_cb`<br>`bot/handlers/admin.py:2874` `finance_pick_user`<br>`bot/handlers/admin.py:3196` `finance_target` | `bot/handlers/admin.py:3204` `finance_amount` |

### `AdminTreasury` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `amount` | `bot/handlers/admin.py:2606` `treasury_give` | `bot/handlers/admin.py:2616` `treasury_amount` |
| `target` | `bot/handlers/admin.py:2632` `treasury_amount` | `bot/handlers/admin.py:2638` `treasury_target_manual` |

### `AdminStorageRestock` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `amount` | `bot/handlers/admin.py:1299` `storage_restock` | `bot/handlers/admin.py:1313` `storage_restock_amount` |

### `AdminRestockAuto` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | `bot/handlers/admin.py:1228` `storage_auto_toggle`<br>`bot/handlers/admin.py:1251` `storage_auto_target` | `bot/handlers/admin.py:1259` `storage_auto_target_value` |

### `AdminShopLimit` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `value` | `bot/handlers/admin.py:1164` `storage_shop_limit_ask` | `bot/handlers/admin.py:1173` `storage_shop_limit_value` |

### `AdminStorageDelete` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `confirm` | `bot/handlers/admin.py:1371` `storage_purge` | `bot/handlers/admin.py:1385` `storage_purge_confirm` |

### `AdminTax` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `percent` | `bot/handlers/admin.py:2662` `admin_tax_view` | `bot/handlers/admin.py:2674` `admin_tax_set` |

### `AdminReportAutoApprove` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `value` | `bot/handlers/admin.py:5021` `report_auto_approve_edit_cb` | `bot/handlers/admin.py:5034` `report_auto_approve_edit_value` |

### `AdminReportPayCap` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `value` | `bot/handlers/admin.py:5060` `report_pay_cap_edit_cb` | `bot/handlers/admin.py:5075` `report_pay_cap_edit_value` |

### `AdminReportFix` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `daily` | `bot/handlers/admin.py:5261` `report_fix_start` | `bot/handlers/admin.py:5274` `report_fix_daily` |
| `total` | `bot/handlers/admin.py:5288` `report_fix_daily` | `bot/handlers/admin.py:5302` `report_fix_total` |

### `AdminReportReject` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `reason` | `bot/handlers/admin.py:5444` `report_reject` | `bot/handlers/admin.py:5452` `report_reject_reason` |

### `AdminRoles` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | `bot/handlers/admin.py:3282` `admin_roles` | `bot/handlers/admin.py:3291` `roles_target` |
| `action` | `bot/handlers/admin.py:500` `pickuser_cb`<br>`bot/handlers/admin.py:3297` `roles_target` | — |
| `role` | `bot/handlers/admin.py:3315` `roles_action` | — |

### `AdminStatuses` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `name` | `bot/handlers/admin.py:3566` `status_create_start` | `bot/handlers/admin.py:3574` `status_create_name` |
| `tag` | `bot/handlers/admin.py:3576` `status_create_name` | `bot/handlers/admin.py:3585` `status_create_tag` |
| `level` | `bot/handlers/admin.py:3592` `status_create_tag` | `bot/handlers/admin.py:3602` `status_create_level` |
| `desc` | `bot/handlers/admin.py:3613` `status_create_level` | `bot/handlers/admin.py:3618` `status_create_desc` |
| `target` | `bot/handlers/admin.py:3842` `status_grant_target`<br>`bot/handlers/admin.py:3911` `status_revoke_target` | `bot/handlers/admin.py:3852` `status_grant_target_msg` |
| `grant_action` | — | — |
| `status_pick` | `bot/handlers/admin.py:523` `pickuser_cb`<br>`bot/handlers/admin.py:532` `pickuser_cb`<br>`bot/handlers/admin.py:3863` `status_grant_target_msg`<br>`bot/handlers/admin.py:3995` `status_grant_more` | — |
| `item_pick` | — | — |
| `item_status` | — | — |

### `AdminAwards` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `name` | `bot/handlers/admin.py:4084` `award_create_start` | `bot/handlers/admin.py:4145` `award_create_name` |
| `desc` | `bot/handlers/admin.py:4151` `award_create_name` | `bot/handlers/admin.py:4159` `award_create_desc` |
| `emoji` | `bot/handlers/admin.py:4162` `award_create_desc` | `bot/handlers/admin.py:4170` `award_create_emoji` |
| `image` | `bot/handlers/admin.py:4174` `award_create_emoji` | `bot/handlers/admin.py:4182` `award_create_image` |
| `bonus` | `bot/handlers/admin.py:4136` `_award_ask_bonus` | `bot/handlers/admin.py:4195` `award_create_bonus` |
| `preview` | `bot/handlers/admin.py:4121` `_award_ask_bonus` | — |
| `target` | `bot/handlers/admin.py:4622` `award_grant_target` | `bot/handlers/admin.py:4628` `award_grant_target_msg` |
| `award_pick` | `bot/handlers/admin.py:4703` `award_revoke_pick_user` | — |
| `comment` | `bot/handlers/admin.py:4646` `award_grant_pick` | `bot/handlers/admin.py:4663` `award_grant_comment` |
| `edit_value` | `bot/handlers/admin.py:4484` `award_edit_field_pick` | `bot/handlers/admin.py:4508` `award_edit_value` |

### `AdminFishing` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `water` | — | — |
| `wf_id` | — | — |
| `value` | `bot/handlers/admin.py:7714` `admin_fishing_junk_field_pick`<br>`bot/handlers/admin.py:8288` `admin_fishing_field_pick` | `bot/handlers/admin.py:8315` `admin_fishing_value` |
| `c_name` | `bot/handlers/admin.py:8125` `admin_fishing_new` | `bot/handlers/admin.py:8134` `admin_fishing_new_name` |
| `c_desc` | `bot/handlers/admin.py:8144` `admin_fishing_new_name` | `bot/handlers/admin.py:8150` `admin_fishing_new_desc` |
| `c_sell_price` | `bot/handlers/admin.py:8153` `admin_fishing_new_desc` | `bot/handlers/admin.py:8159` `admin_fishing_new_sell_price` |
| `c_day_weight` | `bot/handlers/admin.py:8167` `admin_fishing_new_sell_price` | `bot/handlers/admin.py:8175` `admin_fishing_new_day_weight` |
| `c_night_weight` | `bot/handlers/admin.py:8183` `admin_fishing_new_day_weight` | `bot/handlers/admin.py:8191` `admin_fishing_new_night_weight` |
| `c_photo` | `bot/handlers/admin.py:8223` `admin_fishing_new_super` | `bot/handlers/admin.py:8231` `admin_fishing_new_photo` |
| `c_super_rare` | `bot/handlers/admin.py:8199` `admin_fishing_new_night_weight` | — |
| `j_name` | `bot/handlers/admin.py:7829` `admin_fishing_junk_new` | `bot/handlers/admin.py:7837` `admin_fishing_junk_new_name` |
| `j_sell` | `bot/handlers/admin.py:7843` `admin_fishing_junk_new_name` | `bot/handlers/admin.py:7849` `admin_fishing_junk_new_sell` |
| `j_chance` | `bot/handlers/admin.py:7855` `admin_fishing_junk_new_sell` | `bot/handlers/admin.py:7861` `admin_fishing_junk_new_chance` |
| `j_photo` | `bot/handlers/admin.py:7867` `admin_fishing_junk_new_chance` | `bot/handlers/admin.py:7874` `admin_fishing_junk_new_photo` |

### `AdminForest` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `f_id` | — | — |
| `field` | — | — |
| `value` | `bot/handlers/admin.py:8872` `admin_forest_field_pick` | `bot/handlers/admin.py:8898` `admin_forest_value` |
| `c_name` | `bot/handlers/admin.py:8954` `admin_forest_new` | `bot/handlers/admin.py:8963` `admin_forest_new_name` |
| `c_desc` | `bot/handlers/admin.py:8973` `admin_forest_new_name` | `bot/handlers/admin.py:8979` `admin_forest_new_desc` |
| `c_sell_price` | `bot/handlers/admin.py:8982` `admin_forest_new_desc` | `bot/handlers/admin.py:8988` `admin_forest_new_sell_price` |
| `c_chance` | `bot/handlers/admin.py:8995` `admin_forest_new_sell_price` | `bot/handlers/admin.py:9004` `admin_forest_new_chance` |
| `c_kind` | `bot/handlers/admin.py:9012` `admin_forest_new_chance` | — |
| `c_photo` | `bot/handlers/admin.py:9035` `admin_forest_new_kind` | `bot/handlers/admin.py:9043` `admin_forest_new_photo` |
| `zone_value` | `bot/handlers/admin.py:8552` `admin_forest_zone_chance`<br>`bot/handlers/admin.py:8627` `admin_forest_zone_set_pick`<br>`bot/handlers/admin.py:8640` `admin_forest_limit_set` | `bot/handlers/admin.py:8647` `admin_forest_zone_value` |

### `AdminEnemy` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `field` | `bot/handlers/admin.py:10499` `admin_enemies_field_pick` | `bot/handlers/admin.py:10505` `admin_enemies_field_value` |
| `photo` | `bot/handlers/admin.py:10556` `admin_enemies_photo_pick` | `bot/handlers/admin.py:10562` `admin_enemies_photo_value` |
| `onhit_value` | `bot/handlers/admin.py:6943` `source_enemy_effect_toggle` | `bot/handlers/admin.py:6949` `source_enemy_onhit_value` |
| `drop_chance` | `bot/handlers/admin.py:10716` `admin_enemies_drop_edit_chance`<br>`bot/handlers/admin.py:10790` `admin_enemies_drop_add_pick` | `bot/handlers/admin.py:10796` `admin_enemies_drop_chance_value` |
| `drop_qty` | `bot/handlers/admin.py:10729` `admin_enemies_drop_edit_qty`<br>`bot/handlers/admin.py:10817` `admin_enemies_drop_chance_value` | `bot/handlers/admin.py:10823` `admin_enemies_drop_qty_value` |
| `c_name` | `bot/handlers/admin.py:10862` `admin_enemies_new` | `bot/handlers/admin.py:10867` `admin_enemies_new_name` |
| `c_hp` | `bot/handlers/admin.py:10873` `admin_enemies_new_name` | `bot/handlers/admin.py:10878` `admin_enemies_new_hp` |
| `c_dmg` | `bot/handlers/admin.py:10884` `admin_enemies_new_hp` | `bot/handlers/admin.py:10889` `admin_enemies_new_dmg` |
| `c_dodge` | `bot/handlers/admin.py:10902` `admin_enemies_new_dmg` | `bot/handlers/admin.py:10907` `admin_enemies_new_dodge` |
| `c_chance` | `bot/handlers/admin.py:10913` `admin_enemies_new_dodge` | `bot/handlers/admin.py:10919` `admin_enemies_new_chance` |
| `c_loss_ap` | `bot/handlers/admin.py:10925` `admin_enemies_new_chance` | `bot/handlers/admin.py:10931` `admin_enemies_new_done` |

### `AdminCallsign` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | `bot/handlers/admin.py:813` `admin_callsign_start` | `bot/handlers/admin.py:834` `admin_callsign_target_msg` |
| `value` | `bot/handlers/admin.py:590` `pickuser_cb`<br>`bot/handlers/admin.py:844` `admin_callsign_target_msg` | `bot/handlers/admin.py:855` `admin_callsign_value_msg` |

### `AdminWing` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | `bot/handlers/admin.py:826` `admin_wing_start` | — |
| `value` | `bot/handlers/admin.py:601` `pickuser_cb` | — |

### `AdminStates` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | `bot/handlers/admin.py:5855` `admin_states_menu` | `bot/handlers/admin.py:5864` `admin_states_target_text` |
| `action` | `bot/handlers/admin.py:562` `pickuser_cb`<br>`bot/handlers/admin.py:5870` `admin_states_target_text` | — |
| `state_key` | `bot/handlers/admin.py:5899` `admin_states_op` | — |
| `minutes` | `bot/handlers/admin.py:5924` `admin_states_key` | `bot/handlers/admin.py:5933` `admin_states_minutes`<br>`bot/handlers/admin.py:5954` `admin_states_minutes_bad` |

### `AdminPlayerLog` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | `bot/handlers/admin.py:799` `admin_player_log_start` | `bot/handlers/admin.py:662` `admin_player_log_manual_msg` |

### `AdminSalary` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `amount` | `bot/handlers/admin.py:575` `pickuser_cb` | `bot/handlers/admin.py:6054` `admin_salary_amount` |

### `AdminLocation` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `action` | — | — |
| `target_id` | — | — |
| `key` | `bot/handlers/admin.py:9098` `loc_create` | `bot/handlers/admin.py:9362` `loc_step_key` |
| `name` | `bot/handlers/admin.py:9368` `loc_step_key` | `bot/handlers/admin.py:9373` `loc_step_name` |
| `set_name` | `bot/handlers/admin.py:9389` `loc_set_name` | `bot/handlers/admin.py:9400` `loc_step_set_name` |
| `description` | `bot/handlers/admin.py:9375` `loc_step_name`<br>`bot/handlers/admin.py:9414` `loc_step_set_name`<br>`bot/handlers/admin.py:9428` `loc_set_desc` | `bot/handlers/admin.py:9639` `loc_step_desc` |
| `mode` | `bot/handlers/admin.py:9194` `loc_set_mode`<br>`bot/handlers/admin.py:9650` `loc_step_desc` | `bot/handlers/admin.py:9207` `loc_mode_chosen` |
| `req_status` | `bot/handlers/admin.py:9220` `loc_mode_chosen`<br>`bot/handlers/admin.py:9229` `loc_mode_chosen`<br>`bot/handlers/admin.py:9238` `loc_set_status` | `bot/handlers/admin.py:9243` `loc_req_status_chosen` |
| `blocking` | `bot/handlers/admin.py:9226` `loc_mode_chosen`<br>`bot/handlers/admin.py:9257` `loc_req_status_chosen`<br>`bot/handlers/admin.py:9273` `loc_set_blocking` | `bot/handlers/admin.py:9278` `loc_blocking_chosen` |
| `preview` | `bot/handlers/admin.py:9676` `loc_glade_set`<br>`bot/handlers/admin.py:9762` `loc_fire_set`<br>`bot/handlers/admin.py:9810` `loc_clearing_set`<br>`bot/handlers/admin.py:9862` `loc_logging_set`<br>`bot/handlers/admin.py:9913` `loc_mine_set`<br>`bot/handlers/admin.py:9964` `loc_storage_set`<br>`bot/handlers/admin.py:10013` `loc_photo_set`<br>`bot/handlers/admin.py:10051` `loc_season_photo_set` | `bot/handlers/admin.py:10093` `loc_step_photo` |

### `AdminCityPhoto` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `photo` | `bot/handlers/admin.py:9708` `loc_city_fire` | `bot/handlers/admin.py:9727` `loc_city_fire_save` |

### `AdminDungeon` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target_id` | — | — |
| `photo_tod` | `bot/handlers/admin.py:6216` `dungeon_photo_set` | `bot/handlers/admin.py:6252` `dungeon_step_photo` |
| `enemy_id` | — | — |
| `enemy_field` | — | — |
| `enemy_value` | `bot/handlers/admin.py:6494` `dungeon_enemy_field_pick` | `bot/handlers/admin.py:6520` `dungeon_enemy_value` |
| `onhit_value` | `bot/handlers/admin.py:6867` `dungeon_enemy_effect_toggle` | `bot/handlers/admin.py:6873` `dungeon_enemy_onhit_value` |
| `drop_chance` | `bot/handlers/admin.py:1843` `add_item_photo`<br>`bot/handlers/admin.py:7123` `enemy_drop_pick_item`<br>`bot/handlers/admin.py:7206` `enemy_drop_set_chance` | `bot/handlers/admin.py:7528` `enemy_drop_chance_value` |
| `drop_qty` | `bot/handlers/admin.py:7229` `enemy_drop_set_qty`<br>`bot/handlers/admin.py:7537` `enemy_drop_chance_value` | `bot/handlers/admin.py:7543` `enemy_drop_qty_value` |
| `drop_item_photo` | `bot/handlers/admin.py:7274` `enemy_drop_item_photo` | `bot/handlers/admin.py:7283` `enemy_drop_item_photo_value` |
| `drop_item_desc` | `bot/handlers/admin.py:7328` `enemy_drop_item_desc` | `bot/handlers/admin.py:7337` `enemy_drop_item_desc_value` |
| `drop_item_field` | — | — |
| `drop_item_value` | `bot/handlers/admin.py:7426` `enemy_drop_item_stat_pick` | `bot/handlers/admin.py:7437` `enemy_drop_item_stat_value` |
| `pending_enemy_id` | — | — |

### `AdminFine` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `user_id` | `bot/handlers/admin.py:2923` `fines_new` | `bot/handlers/admin.py:2929` `fines_new_user` |
| `amount` | `bot/handlers/admin.py:516` `pickuser_cb`<br>`bot/handlers/admin.py:2945` `fines_new_user` | `bot/handlers/admin.py:2950` `fines_new_amount` |
| `reason` | `bot/handlers/admin.py:2957` `fines_new_amount` | `bot/handlers/admin.py:2962` `fines_new_reason` |

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
| `waiting_recipient` | `bot/handlers/bank.py:154` `bank_transfer_manual` | `bot/handlers/bank.py:297` `process_recipient` |
| `waiting_amount` | `bot/handlers/bank.py:166` `set_recipient` | `bot/handlers/bank.py:319` `process_amount` |
| `waiting_message` | `bot/handlers/bank.py:362` `process_amount` | `bot/handlers/bank.py:371` `process_message` |
| `waiting_treasury_amount` | `bot/handlers/bank.py:248` `bank_treasury` | `bot/handlers/bank.py:258` `process_treasury_amount` |
| `waiting_fine_amount` | `bot/handlers/bank.py:502` `bank_fine_pay_part` | `bot/handlers/bank.py:508` `bank_fine_amount` |

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
| `wait_name` | `bot/handlers/clans.py:728` `clan_create_start` | `bot/handlers/clans.py:736` `clan_create_name` |
| `wait_desc` | `bot/handlers/clans.py:743` `clan_create_name` | `bot/handlers/clans.py:751` `clan_create_desc` |
| `wait_photo` | `bot/handlers/clans.py:761` `clan_create_desc` | `bot/handlers/clans.py:805` `clan_create_photo`<br>`bot/handlers/clans.py:812` `clan_create_photo_hint` |

### `ClansEdit` — `bot/handlers/clans.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `field` | — | — |
| `wait_value` | `bot/handlers/clans.py:876` `clan_edit_field_cb` | `bot/handlers/clans.py:882` `clan_edit_finish_photo`<br>`bot/handlers/clans.py:896` `clan_edit_finish_text` |

### `ClansMessage` — `bot/handlers/clans.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `wait_text` | `bot/handlers/clans.py:933` `clan_msg_start` | `bot/handlers/clans.py:941` `clan_msg_send` |

### `DungeonFSM` — `bot/handlers/dungeon.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `in_dungeon` | `bot/handlers/dungeon.py:892` `contract_enter_confirm`<br>`bot/handlers/dungeon.py:963` `post_captain_menu`<br>`bot/handlers/dungeon.py:2358` `resv_deeper` | — |
| `in_combat` | — | — |
| `in_boss` | `bot/handlers/dungeon.py:1995` `show_boss` | — |
| `confirm_enter` | `bot/handlers/dungeon.py:827` `contract_enter` | — |
| `in_reservoir` | `bot/handlers/dungeon.py:2017` `resv_enter`<br>`bot/handlers/dungeon.py:2032` `resv_menu`<br>`bot/handlers/dungeon.py:2092` `resv_bait_set` | — |

### `HqOrder` — `bot/handlers/hq.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | `bot/handlers/hq.py:178` `hq_order_start`<br>`bot/handlers/hq.py:729` `hq_wingcmd_send_cb` | `bot/handlers/hq.py:187` `hq_order_text` |

### `HqWingCreate` — `bot/handlers/hq.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `num` | `bot/handlers/hq.py:1082` `hq_wing_add_start` | `bot/handlers/hq.py:1091` `hq_wing_add_num` |
| `abbr` | `bot/handlers/hq.py:1100` `hq_wing_add_num` | `bot/handlers/hq.py:1110` `hq_wing_add_abbr` |
| `name` | `bot/handlers/hq.py:1119` `hq_wing_add_abbr` | `bot/handlers/hq.py:1127` `hq_wing_add_name` |
| `callsign` | `bot/handlers/hq.py:1136` `hq_wing_add_name` | `bot/handlers/hq.py:1144` `hq_wing_add_callsign` |
| `emoji` | `bot/handlers/hq.py:1152` `hq_wing_add_callsign` | `bot/handlers/hq.py:1160` `hq_wing_add_emoji` |

### `HqWingEdit` — `bot/handlers/hq.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `field` | — | — |
| `value` | `bot/handlers/hq.py:1206` `hq_wing_edit_cb` | `bot/handlers/hq.py:1216` `hq_wing_edit_value` |

### `TransferItem` — `bot/handlers/inventory.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | `bot/handlers/inventory.py:1770` `inv_transfer_start` | `bot/handlers/inventory.py:1779` `inv_transfer_target` |
| `amount` | `bot/handlers/inventory.py:1786` `inv_transfer_target` | `bot/handlers/inventory.py:1794` `inv_transfer_amount` |
| `message` | `bot/handlers/inventory.py:1826` `inv_transfer_amount` | `bot/handlers/inventory.py:1835` `inv_transfer_message` |

### `KgbPassport` — `bot/handlers/kgb.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `photo` | `bot/handlers/kgb.py:226` `kgb_issue_target` | `bot/handlers/kgb.py:231` `kgb_photo_step`<br>`bot/handlers/kgb.py:241` `kgb_photo_wrong`<br>`bot/handlers/kgb.py:246` `kgb_photo_skip` |
| `series` | — | `bot/handlers/kgb.py:270` `kgb_text_step` |
| `number` | `bot/handlers/kgb.py:317` `kgb_confirm` | `bot/handlers/kgb.py:270` `kgb_text_step` |
| `full_name` | — | `bot/handlers/kgb.py:270` `kgb_text_step` |
| `position` | — | `bot/handlers/kgb.py:270` `kgb_text_step` |
| `rank` | — | `bot/handlers/kgb.py:270` `kgb_text_step` |
| `sex` | — | `bot/handlers/kgb.py:257` `kgb_sex_wrong`<br>`bot/handlers/kgb.py:292` `kgb_sex_step` |
| `marital` | — | `bot/handlers/kgb.py:270` `kgb_text_step` |
| `birth` | — | `bot/handlers/kgb.py:270` `kgb_text_step` |
| `issue` | — | `bot/handlers/kgb.py:270` `kgb_text_step` |
| `marks` | — | `bot/handlers/kgb.py:270` `kgb_text_step` |
| `confirm` | `bot/handlers/kgb.py:130` `_preview` | `bot/handlers/kgb.py:305` `kgb_confirm` |

### `KvpFSM` — `bot/handlers/kvp.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `in_course` | `bot/handlers/kvp.py:293` `kvp_start`<br>`bot/handlers/kvp.py:317` `kvp_resume` | — |

### `AdminAddBook` — `bot/handlers/library.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `section` | `bot/handlers/library.py:293` `book_add_section` | — |
| `title` | `bot/handlers/library.py:302` `book_section` | `bot/handlers/library.py:307` `book_title` |
| `author` | `bot/handlers/library.py:309` `book_title` | `bot/handlers/library.py:314` `book_author` |
| `description` | `bot/handlers/library.py:317` `book_author` | `bot/handlers/library.py:322` `book_description` |
| `cover` | `bot/handlers/library.py:324` `book_description` | `bot/handlers/library.py:333` `book_cover` |
| `content` | `bot/handlers/library.py:343` `book_cover` | `bot/handlers/library.py:351` `book_content` |

### `ContractNew` — `bot/handlers/market_contracts.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `qty` | `bot/handlers/market_contracts.py:212` `contract_pick` | `bot/handlers/market_contracts.py:219` `contract_qty` |
| `price` | `bot/handlers/market_contracts.py:229` `contract_qty` | `bot/handlers/market_contracts.py:237` `contract_price` |
| `confirm` | `bot/handlers/market_contracts.py:246` `contract_price` | `bot/handlers/market_contracts.py:260` `contract_confirm` |

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
| `waiting_photo` | `bot/handlers/profile.py:266` `set_photo` | `bot/handlers/profile.py:274` `process_photo` |
| `waiting_about` | `bot/handlers/profile.py:287` `edit_about` | `bot/handlers/profile.py:295` `process_about` |
| `waiting_callsign` | `bot/handlers/profile.py:779` `profile_callsign`<br>`bot/handlers/profile.py:791` `profile_callsign`<br>`bot/handlers/profile.py:910` `profile_callsign_buy` | `bot/handlers/profile.py:828` `profile_callsign_input` |

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
| `waiting_text` | `bot/handlers/representative.py:101` `rep_speech_write`<br>`bot/handlers/representative.py:128` `rep_speech_delete` | `bot/handlers/representative.py:177` `rep_speech_text` |

### `SpecialDeptBuy` — `bot/handlers/shop.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `code` | `bot/handlers/shop.py:531` `_start_special_dept_buy` | `bot/handlers/shop.py:543` `special_dept_enter_code` |

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
| `city:` | 6 | `city:clans`, `city:menu`, `city:pilots`, `city:pilots:list`, `city:quarter`, `city:vote` |
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
| `inventory:` | 3 | `inventory:cat:documents`, `inventory:eq`, `inventory:list` |
| `kgb:` | 7 | `kgb:cancel`, `kgb:confirm`, `kgb:issue`, `kgb:menu`, `kgb:nophoto`, `kgb:sex:f`, `kgb:sex:m` |
| `kvp:` | 3 | `kvp:exit`, `kvp:resume`, `kvp:start` |
| `lib:` | 2 | `lib:menu`, `lib:no_access` |
| `libadmin:` | 3 | `libadmin:add`, `libadmin:list`, `libadmin:menu` |
| `loc:` | 23 | `loc:blocking:done`, `loc:blocking:none`, `loc:building_pick`, `loc:city_fire`, `loc:clearing_set`, `loc:create`, `loc:edit_pick`, `loc:fire_set`, `loc:glade_set`, `loc:logging_set`, `loc:mine_set`, `loc:mode:all`, `loc:mode:exact`, `loc:mode:min`, `loc:photos`, `loc:photos:clear`, `loc:photos:clear_seasons`, `loc:set_blocking`, `loc:set_desc`, `loc:set_mode`, `loc:set_name`, `loc:set_status`, `loc:storage_set` |
| `logsite:` | 2 | `logsite:back`, `logsite:enter` |
| `lootonly:` | 2 | `lootonly:no`, `lootonly:yes` |
| `marketok:` | 2 | `marketok:no`, `marketok:yes` |
| `mkt:` | 4 | `mkt:confirm`, `mkt:contracts`, `mkt:mine`, `mkt:new` |
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

- `admin:awards`: `bot/handlers/admin.py:4001`
- `admin:callsign`: `bot/handlers/admin.py:807`
- `admin:del_photo`: `bot/handlers/admin.py:781`
- `admin:dungeons`: `bot/handlers/admin.py:6114`
- `admin:enemies`: `bot/handlers/admin.py:10305`
- `admin:finance`: `bot/handlers/admin.py:2425`
- `admin:fishing`: `bot/handlers/admin.py:7897`
- `admin:forest`: `bot/handlers/admin.py:8460`
- `admin:locations`: `bot/handlers/admin.py:6089`
- `admin:logs`: `bot/handlers/admin.py:5651`
- `admin:menu`: `bot/handlers/admin.py:771`
- `admin:player_log`: `bot/handlers/admin.py:793`
- `admin:ranks`: `bot/handlers/admin.py:5541`
- `admin:reports`: `bot/handlers/admin.py:4724`
- `admin:reports_done`: `bot/handlers/admin.py:4781`
- `admin:reports_pending`: `bot/handlers/admin.py:4733`
- `admin:reports_rejected`: `bot/handlers/admin.py:4825`
- `admin:roles`: `bot/handlers/admin.py:3272`
- `admin:salaries`: `bot/handlers/admin.py:5958`
- `admin:saletax`: `bot/handlers/admin.py:2692`
- `admin:shop`: `bot/handlers/admin.py:922`
- `admin:states`: `bot/handlers/admin.py:5849`
- `admin:statuses`: `bot/handlers/admin.py:3506`
- `admin:storage`: `bot/handlers/admin.py:997`
- `admin:tax`: `bot/handlers/admin.py:2655`
- `admin:treasury`: `bot/handlers/admin.py:2468`
- `admin:wing`: `bot/handlers/admin.py:820`
- `aw:ach`: `bot/handlers/admin.py:4059`
- `aw:create`: `bot/handlers/admin.py:4077`
- `aw:delete`: `bot/handlers/admin.py:4247`
- `aw:edit`: `bot/handlers/admin.py:4437`
- `aw:grant`: `bot/handlers/admin.py:4619`
- `aw:list`: `bot/handlers/admin.py:4038`
- `aw:revoke`: `bot/handlers/admin.py:4700`
- `aw_comment:skip`: `bot/handlers/admin.py:4657`
- `aw_confirm`: `bot/handlers/admin.py:4215`
- `back:main`: `bot/handlers/admin.py:5824`
- `bank:balance`: `bot/handlers/bank.py:76`
- `bank:fines`: `bot/handlers/bank.py:473`
- `bank:menu`: `bot/handlers/bank.py:195`
- `bank:noop`: `bot/handlers/bank.py:578`
- `bank:taxes`: `bot/handlers/bank.py:231`
- `bank:transfer`: `bot/handlers/bank.py:135`
- `bank:transfer_manual`: `bot/handlers/bank.py:151`
- `bank:treasury`: `bot/handlers/bank.py:244`
- `booklet:claim`: `bot/handlers/tourist_booklet.py:71`
- `booklet:menu`: `bot/handlers/tourist_booklet.py:65`
- `cancel`: `bot/handlers/admin.py:5832`
- `city:business`: `bot/handlers/locations.py:262`
- `city:clans`: `bot/handlers/clans.py:92`
- `city:countryside`: `bot/handlers/locations.py:282`
- `city:dungeon`: `bot/handlers/dungeon.py:897`
- `city:library`: `bot/handlers/library.py:82`
- `city:menu`: `bot/handlers/start.py:186`
- `city:pilots`: `bot/handlers/pilots.py:102`
- `city:pilots:list`: `bot/handlers/pilots.py:129`
- `city:quarter`: `bot/handlers/locations.py:244`
- `city:vote`: `bot/handlers/polls.py:70`
- `clanh:noop`: `bot/handlers/clan_hall.py:2602`
- `clanhph:construction`: `bot/handlers/admin_clanphotos.py:174`
- `clanhph:menu`: `bot/handlers/admin_clanphotos.py:116`
- `clans:create_skip`: `bot/handlers/clans.py:816`
- `clans:noop`: `bot/handlers/clans.py:602`
- `clanshopadm:menu`: `bot/handlers/admin_shop_clan.py:103`
- `contracts:list`: `bot/handlers/dungeon.py:726`
- `del_item:back`: `bot/handlers/admin.py:1919`
- `duel:card:buy`: `bot/handlers/duel.py:229`
- `duel:help`: `bot/handlers/duel.py:218`
- `duel:list`: `bot/handlers/duel.py:261`
- `duel:menu`: `bot/handlers/duel.py:212`
- `duel:top`: `bot/handlers/duel.py:281`
- `dungeon:exit`: `bot/handlers/dungeon.py:2493`
- `dungeon:exit:cancel`: `bot/handlers/dungeon.py:2574`
- `dungeon:exit:confirm`: `bot/handlers/dungeon.py:2536`
- `dungeon:photos`: `bot/handlers/admin.py:6197`
- `dungeon:photos:clear`: `bot/handlers/admin.py:6241`
- `enemy:fi`: `bot/handlers/admin.py:10343`
- `field:drink`: `bot/handlers/admin.py:2205`
- `field:loot_only`: `bot/handlers/admin.py:2269`
- `field:market_ok`: `bot/handlers/admin.py:2249`
- `field:photo`: `bot/handlers/admin.py:2111`
- `field:weapon_effect`: `bot/handlers/admin.py:2131`
- `fin:manual`: `bot/handlers/admin.py:2776`
- `fines:list`: `bot/handlers/admin.py:2986`
- `fines:menu`: `bot/handlers/admin.py:2905`
- `fines:new`: `bot/handlers/admin.py:2916`
- `finh:open`: `bot/handlers/admin.py:3115`
- `fireevent:enter`: `bot/handlers/fire_event.py:763`
- `fireevent:go`: `bot/handlers/fire_event.py:920`
- `fireevent:potioncancel`: `bot/handlers/fire_event.py:1348`
- `fireevent:shop`: `bot/handlers/fire_event.py:868`
- `fireevent:souvenir`: `bot/handlers/fire_event.py:794`
- `fireph:menu`: `bot/handlers/admin_firephotos.py:73`
- `fish:recover`: `bot/handlers/fishing.py:507`
- `forest:addlist`: `bot/handlers/admin.py:8793`
- `forest:new`: `bot/handlers/admin.py:8946`
- `forest:zset:sold_daily_limit`: `bot/handlers/admin.py:8632`
- `housing:menu`: `bot/handlers/housing.py:292`
- `housing:noop`: `bot/handlers/housing.py:865`
- `housing:pay_debt`: `bot/handlers/housing.py:340`
- `housing:pay_tax`: `bot/handlers/housing.py:331`
- `hq:farms`: `bot/handlers/hq.py:482`
- `hq:menu`: `bot/handlers/hq.py:151`
- `hq:noop`: `bot/handlers/hq.py:574`
- `hq:region_stats`: `bot/handlers/hq.py:521`
- `hq:region_stats_refresh`: `bot/handlers/hq.py:530`
- `hq:send`: `bot/handlers/hq.py:158`
- `hq:wing`: `bot/handlers/hq.py:238`
- `hq:wingadd`: `bot/handlers/hq.py:1076`
- `hq:wingcmd`: `bot/handlers/hq.py:582`
- `hq:wingcmd_send`: `bot/handlers/hq.py:718`
- `hq:wings`: `bot/handlers/hq.py:1046`
- `inventory:eq`: `bot/handlers/inventory.py:515`
- `inventory:list`: `bot/handlers/inventory.py:609`
- `kgb:cancel`: `bot/handlers/kgb.py:329`
- `kgb:confirm`: `bot/handlers/kgb.py:304`
- `kgb:issue`: `bot/handlers/kgb.py:178`
- `kgb:menu`: `bot/handlers/kgb.py:169`
- `kgb:nophoto`: `bot/handlers/kgb.py:245`
- `kvp:exit`: `bot/handlers/kvp.py:754`
- `kvp:resume`: `bot/handlers/kvp.py:304`
- `kvp:start`: `bot/handlers/kvp.py:264`
- `lib:menu`: `bot/handlers/library.py:141`
- `lib:no_access`: `bot/handlers/library.py:136`
- `libadmin:add`: `bot/handlers/library.py:288`
- `libadmin:list`: `bot/handlers/library.py:384`
- `libadmin:menu`: `bot/handlers/library.py:271`
- `loc:building_pick`: `bot/handlers/admin.py:9124`
- `loc:city_fire`: `bot/handlers/admin.py:9700`
- `loc:clearing_clear`: `bot/handlers/admin.py:9834`
- `loc:clearing_set`: `bot/handlers/admin.py:9797`
- `loc:create`: `bot/handlers/admin.py:9092`
- `loc:edit_pick`: `bot/handlers/admin.py:9108`
- `loc:fire_set`: `bot/handlers/admin.py:9747`
- `loc:glade_clear`: `bot/handlers/admin.py:9784`
- `loc:glade_set`: `bot/handlers/admin.py:9662`
- `loc:logging_clear`: `bot/handlers/admin.py:9886`
- `loc:logging_set`: `bot/handlers/admin.py:9847`
- `loc:mine_clear`: `bot/handlers/admin.py:9937`
- `loc:mine_set`: `bot/handlers/admin.py:9899`
- `loc:photos`: `bot/handlers/admin.py:9588`
- `loc:photos:clear`: `bot/handlers/admin.py:10079`
- `loc:photos:clear_seasons`: `bot/handlers/admin.py:9611`
- `loc:set_blocking`: `bot/handlers/admin.py:9261`
- `loc:set_desc`: `bot/handlers/admin.py:9418`
- `loc:set_mode`: `bot/handlers/admin.py:9190`
- `loc:set_name`: `bot/handlers/admin.py:9379`
- `loc:set_status`: `bot/handlers/admin.py:9233`
- `loc:storage_clear`: `bot/handlers/admin.py:9988`
- `loc:storage_set`: `bot/handlers/admin.py:9950`
- `logsite:back`: `bot/handlers/logging_site.py:448`
- `logsite:enter`: `bot/handlers/logging_site.py:399`
- `mkt:confirm`: `bot/handlers/market_contracts.py:259`
- `mkt:contracts`: `bot/handlers/market_contracts.py:56`
- `mkt:mine`: `bot/handlers/market_contracts.py:80`
- `mkt:new`: `bot/handlers/market_contracts.py:160`
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
- `noop`: `bot/handlers/admin.py:5819`
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
- `prof:back`: `bot/handlers/profile.py:353`
- `profile`: `bot/handlers/profile.py:255`
- `profile:achievements`: `bot/handlers/profile.py:590`
- `profile:awards`: `bot/handlers/profile.py:566`
- `profile:callsign`: `bot/handlers/profile.py:764`
- `profile:callsign_buy`: `bot/handlers/profile.py:896`
- `profile:callsign_cancel`: `bot/handlers/profile.py:820`
- `profile:choose_status`: `bot/handlers/profile.py:313`
- `profile:edit_about`: `bot/handlers/profile.py:284`
- `profile:notify_toggle`: `bot/handlers/profile.py:360`
- `profile:open`: `bot/handlers/profile.py:757`
- `profile:pilot_card`: `bot/handlers/profile.py:400`
- `profile:public_toggle`: `bot/handlers/profile.py:380`
- `profile:recipes`: `bot/handlers/profile.py:729`
- `profile:set_photo`: `bot/handlers/profile.py:263`
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
- `rep:auto_approve_edit`: `bot/handlers/admin.py:5014`
- `rep:next`: `bot/handlers/admin.py:5514`
- `rep:pay_cap_edit`: `bot/handlers/admin.py:5053`
- `rep:speech`: `bot/handlers/representative.py:77`
- `rep:speech:delete`: `bot/handlers/representative.py:109`
- `rep:speech:write`: `bot/handlers/representative.py:89`
- `report:menu`: `bot/handlers/reports.py:52`
- `report:my_reports`: `bot/handlers/reports.py:404`
- `report:submit`: `bot/handlers/reports.py:62`
- `resv:recover`: `bot/handlers/dungeon.py:2306`
- `salary:choose`: `bot/handlers/admin.py:6016`
- `salary:pay`: `bot/handlers/admin.py:6028`
- `shop:catalog`: `bot/handlers/shop.py:233`
- `shop_admin:add`: `bot/handlers/admin.py:1430`
- `shop_admin:delete`: `bot/handlers/admin.py:1890`
- `shop_admin:edit`: `bot/handlers/admin.py:2013`
- `shop_admin:special_code`: `bot/handlers/admin.py:2733`
- `shop_del:cats`: `bot/handlers/admin.py:2007`
- `shop_edit:cats`: `bot/handlers/admin.py:1992`
- `st:create`: `bot/handlers/admin.py:3560`
- `st:delete`: `bot/handlers/admin.py:3633`
- `st:grant`: `bot/handlers/admin.py:3836`
- `st:legioner`: `bot/handlers/admin.py:3781`
- `st:list`: `bot/handlers/admin.py:3543`
- `st:more`: `bot/handlers/admin.py:3982`
- `st:revoke`: `bot/handlers/admin.py:3902`
- `storage:cats`: `bot/handlers/admin.py:1016`
- `storage:create`: `bot/handlers/admin.py:1431`
- `storage:menu`: `bot/handlers/storage.py:89`
- `storage:noop`: `bot/handlers/admin.py:1011`
- `treasury:debts`: `bot/handlers/admin.py:2501`
- `treasury:give`: `bot/handlers/admin.py:2600`
- `treasury:stats`: `bot/handlers/admin.py:2548`
- `vote:close_cancel`: `bot/handlers/polls.py:332`
- `vote:create`: `bot/handlers/polls.py:224`
- `wall:archive`: `bot/handlers/wall.py:318`
- `wall:view`: `bot/handlers/wall.py:152`
- `wall:write`: `bot/handlers/wall.py:173`

### По префиксу (`F.data.startswith("...")`)

- `\d+$`: `bot/handlers/admin.py:1582`; `bot/handlers/admin.py:5932`; `bot/handlers/admin.py:8646`; `bot/handlers/reports.py:200`
- `\d{1,4}$`: `bot/handlers/market_contracts.py:218`
- `\d{1,7}$`: `bot/handlers/market_contracts.py:236`; `bot/handlers/reports.py:135`; `bot/handlers/reports.py:164`
- `act:`: `bot/handlers/admin.py:5726`
- `addreq:`: `bot/handlers/admin.py:1781`
- `aw_del:`: `bot/handlers/admin.py:4268`
- `aw_edit:`: `bot/handlers/admin.py:4457`
- `aw_ei:`: `bot/handlers/admin.py:4468`
- `aw_kind:`: `bot/handlers/admin.py:4590`
- `aw_pick:`: `bot/handlers/admin.py:4641`
- `awr_grant:`: `bot/handlers/admin.py:4708`
- `bait:set:`: `bot/handlers/fishing.py:183`
- `bank:history`: `bot/handlers/bank.py:528`
- `bank:pickrecipient:`: `bot/handlers/bank.py:181`
- `bank:transfer:list:`: `bot/handlers/bank.py:141`
- `berry:add:(glade|clearing)$`: `bot/handlers/admin_berries.py:117`
- `berry:chance:(glade|clearing):.+$`: `bot/handlers/admin_berries.py:83`
- `berry:del:(glade|clearing):.+$`: `bot/handlers/admin_berries.py:107`
- `berry:new:(glade|clearing)$`: `bot/handlers/admin_berries.py:149`
- `berry:pick:(glade|clearing):\d+$`: `bot/handlers/admin_berries.py:135`
- `berry:row:(glade|clearing):.+$`: `bot/handlers/admin_berries.py:63`
- `berry:zone:(glade|clearing)$`: `bot/handlers/admin_berries.py:54`
- `buy5_nord:`: `bot/handlers/shop.py:498`
- `buy_housing:`: `bot/handlers/shop.py:1137`
- `buy_housing_cancel:`: `bot/handlers/shop.py:1128`
- `buy_nord:`: `bot/handlers/shop.py:488`
- `cat:`: `bot/handlers/admin.py:1503`
- `city/`: `bot/handlers/locations.py:93`
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
- `clans:create:`: `bot/handlers/clans.py:718`
- `clans:del:`: `bot/handlers/clans.py:970`
- `clans:delyes:`: `bot/handlers/clans.py:987`
- `clans:edit:`: `bot/handlers/clans.py:831`
- `clans:editf:`: `bot/handlers/clans.py:855`
- `clans:join:`: `bot/handlers/clans.py:375`
- `clans:kick:`: `bot/handlers/clans.py:557`
- `clans:leader:`: `bot/handlers/clans.py:648`
- `clans:leaderset:`: `bot/handlers/clans.py:665`
- `clans:leaderunset:`: `bot/handlers/clans.py:694`
- `clans:leave:`: `bot/handlers/clans.py:422`
- `clans:list:`: `bot/handlers/clans.py:132`
- `clans:manage:`: `bot/handlers/clans.py:501`
- `clans:msg:`: `bot/handlers/clans.py:925`
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
- `confirm_del_photo:`: `bot/handlers/admin.py:901`
- `contract:enter:\d+$`: `bot/handlers/dungeon.py:798`
- `contract:enter:confirm:`: `bot/handlers/dungeon.py:838`
- `contract:pick:`: `bot/handlers/dungeon.py:754`
- `del_item:`: `bot/handlers/admin.py:1904`
- `drinksel:`: `bot/handlers/admin.py:1536`
- `duel:accept:`: `bot/handlers/duel.py:383`
- `duel:atk:`: `bot/handlers/duel.py:510`
- `duel:cancel:`: `bot/handlers/duel.py:357`
- `duel:decline:`: `bot/handlers/duel.py:369`
- `duel:def:`: `bot/handlers/duel.py:525`
- `duel:invite:`: `bot/handlers/duel.py:299`
- `duel:leave:`: `bot/handlers/duel.py:432`
- `dungeon:attack:`: `bot/handlers/dungeon.py:1310`
- `dungeon:continue:`: `bot/handlers/dungeon.py:1125`
- `dungeon:edit:`: `bot/handlers/admin.py:6134`
- `dungeon:enemies`: `bot/handlers/admin.py:6432`
- `dungeon:enemy:`: `bot/handlers/admin.py:6468`
- `dungeon:escape:`: `bot/handlers/dungeon.py:1921`
- `dungeon:photo_set:`: `bot/handlers/admin.py:6206`
- `dungeon:use_slot:`: `bot/handlers/dungeon.py:1630`
- `eddrop:`: `bot/handlers/admin.py:7154`
- `eddrop_del:`: `bot/handlers/admin.py:7240`
- `eddrop_desc:`: `bot/handlers/admin.py:7312`
- `eddrop_photo:`: `bot/handlers/admin.py:7258`
- `eddrop_set_ch:`: `bot/handlers/admin.py:7195`
- `eddrop_set_q:`: `bot/handlers/admin.py:7218`
- `eddrop_stat:`: `bot/handlers/admin.py:7407`
- `eddrop_stats:`: `bot/handlers/admin.py:7368`
- `eddrop_weff:`: `bot/handlers/admin.py:7470`
- `eddrop_weff_set:`: `bot/handlers/admin.py:7492`
- `edit_item:`: `bot/handlers/admin.py:2022`
- `editem_add:`: `bot/handlers/admin.py:7106`
- `editem_new:`: `bot/handlers/admin.py:7131`
- `editem_pick:`: `bot/handlers/admin.py:7061`
- `editset:drink:`: `bot/handlers/admin.py:2228`
- `editset:weff:`: `bot/handlers/admin.py:2147`
- `enemy:card:`: `bot/handlers/admin.py:10478`
- `enemy:dcard:`: `bot/handlers/admin.py:10405`
- `enemy:del:`: `bot/handlers/admin.py:10604`
- `enemy:dn:\d+$`: `bot/handlers/admin.py:10315`
- `enemy:dropadd:`: `bot/handlers/admin.py:10781`
- `enemy:dropch:`: `bot/handlers/admin.py:10708`
- `enemy:dropdel:`: `bot/handlers/admin.py:10734`
- `enemy:dropedit:`: `bot/handlers/admin.py:10670`
- `enemy:dropitem:`: `bot/handlers/admin.py:10746`
- `enemy:dropq:`: `bot/handlers/admin.py:10721`
- `enemy:drops:`: `bot/handlers/admin.py:10660`
- `enemy:effects:\d+$`: `bot/handlers/admin.py:6823`
- `enemy:fld:`: `bot/handlers/admin.py:10488`
- `enemy:fx:src:`: `bot/handlers/admin.py:6896`
- `enemy:fx:tog:\d+:\d+$`: `bot/handlers/admin.py:6842`
- `enemy:fxt:`: `bot/handlers/admin.py:6916`
- `enemy:list:[a-z]+:[\w-]+$`: `bot/handlers/admin.py:10363`
- `enemy:new:`: `bot/handlers/admin.py:10855`
- `enemy:photo:`: `bot/handlers/admin.py:10548`
- `enemy:res:\d+$`: `bot/handlers/admin.py:6769`
- `enemy:res:tog:\d+:\d+$`: `bot/handlers/admin.py:6785`
- `enemy:tog:`: `bot/handlers/admin.py:10585`
- `enemy_drops:`: `bot/handlers/admin.py:7048`
- `enemy_field:`: `bot/handlers/admin.py:6481`
- `eqequip:[a-z0-9_]+:\d+$`: `bot/handlers/inventory.py:533`
- `eqlock:[a-z0-9_]+$`: `bot/handlers/inventory.py:521`
- `eqpart:`: `bot/handlers/admin.py:1614`
- `eqslot:[a-z0-9_]+$`: `bot/handlers/inventory.py:526`
- `equnequip:[a-z0-9_]+$`: `bot/handlers/inventory.py:565`
- `field:`: `bot/handlers/admin.py:2333`
- `field:required_status`: `bot/handlers/admin.py:2061`
- `field_req:`: `bot/handlers/admin.py:2094`
- `fin:`: `bot/handlers/admin.py:2789`
- `fine:part:`: `bot/handlers/bank.py:497`
- `fine:payall:`: `bot/handlers/bank.py:486`
- `fines:cancel:`: `bot/handlers/admin.py:3011`
- `finh:h:`: `bot/handlers/admin.py:3150`
- `finh:list:`: `bot/handlers/admin.py:3126`
- `finh:u:`: `bot/handlers/admin.py:3138`
- `finuser:`: `bot/handlers/admin.py:2864`
- `fireevent:attack:`: `bot/handlers/fire_event.py:1126`
- `fireevent:backfork:`: `bot/handlers/fire_event.py:721`
- `fireevent:bait:`: `bot/handlers/fire_event.py:447`
- `fireevent:baitset:`: `bot/handlers/fire_event.py:466`
- `fireevent:cont:`: `bot/handlers/fire_event.py:362`
- `fireevent:dgive:`: `bot/handlers/fire_event.py:697`
- `fireevent:donate:`: `bot/handlers/fire_event.py:683`
- `fireevent:fishing:`: `bot/handlers/fire_event.py:529`
- `fireevent:leave:`: `bot/handlers/fire_event.py:734`
- `fireevent:potion:`: `bot/handlers/fire_event.py:1250`
- `fireevent:potionok:`: `bot/handlers/fire_event.py:1342`
- `fireevent:step:`: `bot/handlers/fire_event.py:292`
- `fireevent:wellback:`: `bot/handlers/fire_event.py:484`
- `fireevent:xchg:`: `bot/handlers/fire_event.py:880`
- `fireph:set:`: `bot/handlers/admin_firephotos.py:82`
- `fish:bait:\d+$`: `bot/handlers/fishing.py:521`
- `fish:bait:set:\d+:[a-z]+$`: `bot/handlers/fishing.py:563`
- `fish:cast:\d+$`: `bot/handlers/fishing.py:573`
- `fish:lake:\d+$`: `bot/handlers/fishing.py:500`
- `fishbuy:`: `bot/handlers/shop.py:839`
- `fishcatch:`: `bot/handlers/inventory.py:1401`
- `fishgo:`: `bot/handlers/inventory.py:1652`
- `fishing:addfish:`: `bot/handlers/admin.py:8065`
- `fishing:addlist:`: `bot/handlers/admin.py:8035`
- `fishing:del:`: `bot/handlers/admin.py:8088`
- `fishing:fish:`: `bot/handlers/admin.py:7955`
- `fishing:junk:`: `bot/handlers/admin.py:7644`
- `fishing:kind:`: `bot/handlers/admin.py:7969`
- `fishing:market:`: `bot/handlers/admin.py:7991`
- `fishing:new:`: `bot/handlers/admin.py:8113`
- `fishing:new_super:`: `bot/handlers/admin.py:8216`
- `fishing:super:`: `bot/handlers/admin.py:8013`
- `fishing:water:`: `bot/handlers/admin.py:7917`
- `fishing_field:`: `bot/handlers/admin.py:8275`
- `fishing_j:`: `bot/handlers/admin.py:7701`
- `fishing_jx:del:`: `bot/handlers/admin.py:7797`
- `fishing_jx:new:`: `bot/handlers/admin.py:7818`
- `fishing_jx:pick:`: `bot/handlers/admin.py:7770`
- `fishing_jx:pool:`: `bot/handlers/admin.py:7741`
- `fishmarket:`: `bot/handlers/inventory.py:1554`
- `fishoffer:`: `bot/handlers/shop.py:764`
- `fishprice:`: `bot/handlers/inventory.py:1634`
- `fishsell:`: `bot/handlers/inventory.py:1710`
- `fishuse:`: `bot/handlers/inventory.py:1409`
- `forest:add:`: `bot/handlers/admin.py:8818`
- `forest:area:\d+:(glade|clearing)$`: `bot/handlers/forest.py:448`
- `forest:battle:flee:\d+$`: `bot/handlers/forest.py:1195`
- `forest:battle:hit:\d+$`: `bot/handlers/forest.py:992`
- `forest:berry:\d+:(glade|clearing)$`: `bot/handlers/forest.py:721`
- `forest:card:`: `bot/handlers/admin.py:8732`
- `forest:cast:\d+(?::(glade|clearing))?$`: `bot/handlers/forest.py:532`
- `forest:del:`: `bot/handlers/admin.py:8837`
- `forest:kind:`: `bot/handlers/admin.py:8746`
- `forest:market:`: `bot/handlers/admin.py:8771`
- `forest:new_kind:`: `bot/handlers/admin.py:9026`
- `forest:zadd:(glade|clearing):\d+$`: `bot/handlers/admin.py:8598`
- `forest:zaddlist:(glade|clearing)$`: `bot/handlers/admin.py:8571`
- `forest:zchance:(glade|clearing):\d+$`: `bot/handlers/admin.py:8544`
- `forest:zdel:(glade|clearing):\d+$`: `bot/handlers/admin.py:8559`
- `forest:zone:(glade|clearing)$`: `bot/handlers/admin.py:8470`
- `forest:zset:(glade|clearing):(\w+)$`: `bot/handlers/admin.py:8610`
- `forest_field:`: `bot/handlers/admin.py:8858`
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
- `hq:farms:`: `bot/handlers/hq.py:498`
- `hq:order:`: `bot/handlers/hq.py:170`
- `hq:pilot:`: `bot/handlers/hq.py:353`
- `hq:roster:`: `bot/handlers/hq.py:293`
- `hq:wing:set:`: `bot/handlers/hq.py:382`
- `hq:wingcmd:assign:`: `bot/handlers/hq.py:646`
- `hq:wingcmd:pick:`: `bot/handlers/hq.py:623`
- `hq:wingcmd:unset:`: `bot/handlers/hq.py:690`
- `hq:wingdel:`: `bot/handlers/hq.py:1242`
- `hq:wingdep:`: `bot/handlers/hq.py:922`
- `hq:wingdrop:`: `bot/handlers/hq.py:838`
- `hq:wingedit:`: `bot/handlers/hq.py:1178`
- `hq:wingfarm:`: `bot/handlers/hq.py:462`
- `hq:wingtake:`: `bot/handlers/hq.py:764`
- `http`: `bot/handlers/library.py:360`
- `inv_equip:`: `bot/handlers/inventory.py:837`
- `inv_sell:`: `bot/handlers/inventory.py:972`
- `inv_sell_ask:`: `bot/handlers/inventory.py:1101`
- `inv_sell_keep1:`: `bot/handlers/inventory.py:992`
- `inv_sell_ok:`: `bot/handlers/inventory.py:1123`
- `inv_sellall:`: `bot/handlers/inventory.py:982`
- `inv_sellmore:`: `bot/handlers/inventory.py:1241`
- `inv_slot:`: `bot/handlers/inventory.py:891`
- `inv_transfer:`: `bot/handlers/inventory.py:1742`
- `inv_unequip:`: `bot/handlers/inventory.py:867`
- `inv_unslot:`: `bot/handlers/inventory.py:926`
- `inv_use:`: `bot/handlers/inventory.py:948`
- `inventory:cat:[^:]+$`: `bot/handlers/inventory.py:628`
- `invitem:`: `bot/handlers/inventory.py:830`
- `itembuy:`: `bot/handlers/shop.py:968`
- `itemgo:`: `bot/handlers/inventory.py:1339`
- `itemmarket:`: `bot/handlers/inventory.py:1249`
- `itemoffer:`: `bot/handlers/shop.py:900`
- `itemprice:`: `bot/handlers/inventory.py:1328`
- `kgb:pick:`: `bot/handlers/kgb.py:193`
- `kgb:sex:`: `bot/handlers/kgb.py:291`
- `kgb:user:`: `bot/handlers/kgb.py:208`
- `kvp:attack:`: `bot/handlers/kvp.py:532`
- `kvp:attempt:`: `bot/handlers/kvp.py:457`
- `kvp:continue:`: `bot/handlers/kvp.py:426`
- `libadmin_del:`: `bot/handlers/library.py:409`
- `libadmin_sec:`: `bot/handlers/library.py:297`
- `libbook:`: `bot/handlers/library.py:204`
- `libdl:`: `bot/handlers/library.py:249`
- `libsec:[a-z]+$`: `bot/handlers/library.py:178`
- `loc:blocking:`: `bot/handlers/admin.py:9277`
- `loc:building:`: `bot/handlers/admin.py:9166`
- `loc:edit:`: `bot/handlers/admin.py:9140`
- `loc:mode:`: `bot/handlers/admin.py:9206`
- `loc:photo_set:`: `bot/handlers/admin.py:10001`
- `loc:req_status:`: `bot/handlers/admin.py:9242`
- `loc:season:(winter|spring|summer|autumn)$`: `bot/handlers/admin.py:9598`
- `loc:season_clear:(winter|spring|summer|autumn)$`: `bot/handlers/admin.py:9624`
- `loc:season_photo_set:(winter|spring|summer|autumn):(dawn|day|sunset|night)$`: `bot/handlers/admin.py:10038`
- `location:enter:`: `bot/handlers/locations.py:113`
- `location:preview:`: `bot/handlers/locations.py:42`
- `locstat:`: `bot/handlers/admin.py:5785`
- `logsite:battle:flee:\d+$`: `bot/handlers/logging_site.py:1056`
- `logsite:battle:hit:\d+$`: `bot/handlers/logging_site.py:857`
- `logsite:chop:\d+$`: `bot/handlers/logging_site.py:456`
- `logsite:fire:(1|all):\d+$`: `bot/handlers/logging_site.py:711`
- `logsite:menu:\d+$`: `bot/handlers/logging_site.py:441`
- `logsite:mill:\d+$`: `bot/handlers/logging_site.py:598`
- `logsite:plank:(1|all):\d+$`: `bot/handlers/logging_site.py:651`
- `lootonly:`: `bot/handlers/admin.py:1756`
- `marketok:`: `bot/handlers/admin.py:1734`
- `mine:battle:flee:\d+$`: `bot/handlers/mine.py:740`
- `mine:battle:hit:\d+$`: `bot/handlers/mine.py:587`
- `mine:deeper:\d+$`: `bot/handlers/mine.py:391`
- `mine:dig:\d+$`: `bot/handlers/mine.py:400`
- `mine:level:\d+$`: `bot/handlers/mine.py:359`
- `mine:menu:\d+$`: `bot/handlers/mine.py:352`
- `mkt:cancel:\d+$`: `bot/handlers/market_contracts.py:145`
- `mkt:close:\d+$`: `bot/handlers/market_contracts.py:134`
- `mkt:newcat:[^:]+:\d+$`: `bot/handlers/market_contracts.py:175`
- `mkt:pick:\d+$`: `bot/handlers/market_contracts.py:203`
- `mkt:view:\d+$`: `bot/handlers/market_contracts.py:102`
- `mollusk:flee:\d+$`: `bot/handlers/dungeon.py:490`
- `mollusk:hit:\d+$`: `bot/handlers/dungeon.py:372`
- `mvd:arch:`: `bot/handlers/mvd.py:95`
- `mvd:archive:`: `bot/handlers/mvd.py:45`
- `news:(?:off|(?:dis)?allow:-?\d+|chat:-?\d+:-?\d+|topic:-?\d+:-?\d+)$`: `bot/handlers/admin.py:3445`
- `news:arch:\d+$`: `bot/handlers/news.py:182`
- `news:del:`: `bot/handlers/news.py:476`
- `news:delconf:`: `bot/handlers/news.py:498`
- `news:edit:`: `bot/handlers/news.py:403`
- `news:view:`: `bot/handlers/news.py:199`
- `nii:set:`: `bot/handlers/nii.py:319`
- `nii:view:`: `bot/handlers/nii.py:284`
- `offercancel:fish:`: `bot/handlers/shop.py:1020`
- `offercancel:item:`: `bot/handlers/shop.py:1025`
- `page`: `bot/handlers/admin.py:453`
- `park:admin:del:`: `bot/handlers/park.py:390`
- `park:admin:delyes:`: `bot/handlers/park.py:410`
- `park:admin:edit:`: `bot/handlers/park.py:478`
- `park:adminedit:f:`: `bot/handlers/park.py:496`
- `park:statue:`: `bot/handlers/park.py:257`
- `pickuser:`: `bot/handlers/admin.py:444`
- `pollarch:day:\d{4}-\d{2}-\d{2}(?::\d+)?$`: `bot/handlers/poll_archive.py:176`
- `pollarch:days:\d+$`: `bot/handlers/poll_archive.py:154`
- `prod:`: `bot/handlers/admin.py:1694`
- `prof_sel_status:`: `bot/handlers/profile.py:338`
- `profile:award:`: `bot/handlers/profile.py:598`
- `profile:awards:(ach|awd)$`: `bot/handlers/profile.py:574`
- `profile:recipe:\d+$`: `bot/handlers/profile.py:744`
- `profile:recipes:\d+$`: `bot/handlers/profile.py:736`
- `rank_pick:`: `bot/handlers/admin.py:5618`
- `rank_promote:`: `bot/handlers/admin.py:5577`
- `rar:`: `bot/handlers/admin.py:1494`
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
- `rep:nav:`: `bot/handlers/admin.py:5503`
- `rep_fix:`: `bot/handlers/admin.py:5244`
- `rep_no:`: `bot/handlers/admin.py:5430`
- `rep_ok:`: `bot/handlers/admin.py:5361`
- `rep_rej_del:`: `bot/handlers/admin.py:4962`
- `rep_rej_del_ok:`: `bot/handlers/admin.py:4990`
- `rep_rej_list:`: `bot/handlers/admin.py:4913`
- `rep_rej_view:`: `bot/handlers/admin.py:4926`
- `report:my:`: `bot/handlers/reports.py:399`
- `report:view:`: `bot/handlers/reports.py:411`
- `resv:bait:\d+$`: `bot/handlers/dungeon.py:2036`
- `resv:bait:set:\d+:[a-z]+$`: `bot/handlers/dungeon.py:2077`
- `resv:cast:\d+$`: `bot/handlers/dungeon.py:2096`
- `resv:deeper:\d+$`: `bot/handlers/dungeon.py:2335`
- `resv:enter:\d+$`: `bot/handlers/dungeon.py:1998`
- `resv:eq:\d+$`: `bot/handlers/dungeon.py:2368`
- `resv:eqclear:[a-z0-9_]+:\d+$`: `bot/handlers/dungeon.py:2470`
- `resv:eqset:[a-z0-9_]+:\d+:\d+$`: `bot/handlers/dungeon.py:2447`
- `resv:eqslot:[a-z0-9_]+:\d+$`: `bot/handlers/dungeon.py:2401`
- `resv:menu:\d+$`: `bot/handlers/dungeon.py:2022`
- `role:`: `bot/handlers/admin.py:3358`
- `rolop:`: `bot/handlers/admin.py:3309`
- `shop_del:cat:`: `bot/handlers/admin.py:1998`
- `shop_edit:cat:`: `bot/handlers/admin.py:1983`
- `shopcat:[^:]+$`: `bot/handlers/shop.py:253`
- `shopcat:[^:]+:\d+$`: `bot/handlers/shop.py:343`
- `shopitem:`: `bot/handlers/shop.py:354`
- `st_del:`: `bot/handlers/admin.py:3652`
- `st_key:`: `bot/handlers/admin.py:5917`
- `st_op:`: `bot/handlers/admin.py:5884`
- `st_pick:`: `bot/handlers/admin.py:3937`
- `st_rev:`: `bot/handlers/admin.py:3867`
- `storage:auto:`: `bot/handlers/admin.py:1200`
- `storage:auto_target:`: `bot/handlers/admin.py:1241`
- `storage:auto_toggle:`: `bot/handlers/admin.py:1216`
- `storage:cat:`: `bot/handlers/admin.py:1029`
- `storage:item:`: `bot/handlers/admin.py:1062`
- `storage:page:`: `bot/handlers/admin.py:1048`
- `storage:purge:`: `bot/handlers/admin.py:1356`
- `storage:restock:`: `bot/handlers/admin.py:1288`
- `storage:shoplim:`: `bot/handlers/admin.py:1154`
- `toggle:`: `bot/handlers/admin.py:9282`
- `vote:cast:`: `bot/handlers/polls.py:163`
- `vote:close:`: `bot/handlers/polls.py:287`
- `vote:close_confirm:`: `bot/handlers/polls.py:310`
- `vote:results:`: `bot/handlers/polls.py:185`
- `vote:show:`: `bot/handlers/polls.py:109`
- `wall:archpage:\d+$`: `bot/handlers/wall.py:341`
- `wall:archread:\d+(?::\d+)?$`: `bot/handlers/wall.py:360`
- `wall:delete:\d+$`: `bot/handlers/wall.py:227`
- `wall:page:\d+$`: `bot/handlers/wall.py:159`
- `weff:`: `bot/handlers/admin.py:1627`
- `wing_set:`: `bot/handlers/admin.py:876`
- `Испорченн`: `bot/handlers/dungeon.py:1837`
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

