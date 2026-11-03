# Карта FSM-состояний и callback-неймспейсов N.O.R.D.

> **Сгенерировано** `tools/export_states.py`. Не редактировать вручную —
> правь код и перегенерируй: `.venv\Scripts\python.exe tools/export_states.py`.
>
> Назначение: единый обзор всех `StatesGroup`, где они ставятся и где ловятся,
> а также реестр `callback_data` — чтобы не допускать конфликтов меню/хендлеров.

Всего классов состояний: **55**; полей-состояний: **240**; уникальных `callback_data`: **277**.

## 1. Классы состояний по модулям

### `AdminAddItem` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `name` | `bot/handlers/admin.py:1240` `shop_admin_add`<br>`bot/handlers/admin.py:6550` `enemy_drop_new_item` | `bot/handlers/admin.py:1248` `add_item_name` |
| `desc` | `bot/handlers/admin.py:1250` `add_item_name` | `bot/handlers/admin.py:1256` `add_item_desc` |
| `price` | `bot/handlers/admin.py:1259` `add_item_desc` | `bot/handlers/admin.py:1265` `add_item_price` |
| `sell_price` | `bot/handlers/admin.py:1275` `add_item_price` | `bot/handlers/admin.py:1281` `add_item_sell_price` |
| `rarity` | `bot/handlers/admin.py:1293` `add_item_sell_price` | — |
| `category` | `bot/handlers/admin.py:1302` `add_item_rarity` | — |
| `drink` | `bot/handlers/admin.py:1325` `add_item_category` | — |
| `plant_name` | `bot/handlers/admin.py:1314` `add_item_category` | `bot/handlers/admin.py:1350` `add_item_plant_name` |
| `stock` | `bot/handlers/admin.py:1334` `add_item_category`<br>`bot/handlers/admin.py:1344` `add_item_drink_choice`<br>`bot/handlers/admin.py:1353` `add_item_plant_name` | `bot/handlers/admin.py:1359` `add_item_stock` |
| `stats` | `bot/handlers/admin.py:1373` `add_item_stock`<br>`bot/handlers/admin.py:1378` `add_item_stock` | `bot/handlers/admin.py:1386` `add_item_stats`<br>`bot/handlers/admin.py:1426` `add_item_stats_bad` |
| `equip_slot` | `bot/handlers/admin.py:1403` `add_item_stats` | — |
| `weapon_effect` | `bot/handlers/admin.py:1391` `add_item_stats` | — |
| `weapon_effect_chance` | `bot/handlers/admin.py:1439` `add_item_weapon_effect_cb` | `bot/handlers/admin.py:1448` `add_item_weapon_effect_chance` |
| `weapon_effect_dmg` | `bot/handlers/admin.py:1460` `add_item_weapon_effect_chance` | `bot/handlers/admin.py:1472` `add_item_weapon_effect_dmg` |
| `producer` | `bot/handlers/admin.py:1487` `_go_add_item_producer` | — |
| `producer_user` | `bot/handlers/admin.py:1502` `add_item_producer` | `bot/handlers/admin.py:1514` `add_item_producer_user` |
| `market` | `bot/handlers/admin.py:1525` `_go_add_item_market` | — |
| `loot` | `bot/handlers/admin.py:1547` `_go_add_item_loot` | — |
| `status` | `bot/handlers/admin.py:1575` `_go_add_item_status` | — |
| `photo` | `bot/handlers/admin.py:1594` `add_item_status_cb` | `bot/handlers/admin.py:1602` `add_item_photo` |

### `AdminSaleTax` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `percent` | `bot/handlers/admin.py:2502` `admin_saletax_view` | `bot/handlers/admin.py:2516` `admin_saletax_set` |

### `AdminSpecialCode` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `code` | `bot/handlers/admin.py:2544` `admin_special_code_view` | `bot/handlers/admin.py:2559` `admin_special_code_set` |

### `AdminEditItem` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `item_id` | — | — |
| `field` | `bot/handlers/admin.py:1830` `edit_item_pick` | — |
| `value` | `bot/handlers/admin.py:2149` `edit_item_field` | `bot/handlers/admin.py:2160` `edit_item_value` |
| `photo` | `bot/handlers/admin.py:1919` `edit_item_field_photo` | `bot/handlers/admin.py:1982` `edit_item_photo` |

### `AdminFinance` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | `bot/handlers/admin.py:2585` `finance_manual`<br>`bot/handlers/admin.py:2607` `finance_pick` | `bot/handlers/admin.py:2992` `finance_target` |
| `currency` | — | — |
| `amount` | `bot/handlers/admin.py:464` `pickuser_cb`<br>`bot/handlers/admin.py:2677` `finance_pick_user`<br>`bot/handlers/admin.py:2999` `finance_target` | `bot/handlers/admin.py:3007` `finance_amount` |

### `AdminTreasury` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `amount` | `bot/handlers/admin.py:2409` `treasury_give` | `bot/handlers/admin.py:2419` `treasury_amount` |
| `target` | `bot/handlers/admin.py:2435` `treasury_amount` | `bot/handlers/admin.py:2441` `treasury_target_manual` |

### `AdminStorageRestock` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `amount` | `bot/handlers/admin.py:1102` `storage_restock` | `bot/handlers/admin.py:1116` `storage_restock_amount` |

### `AdminStorageDelete` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `confirm` | `bot/handlers/admin.py:1174` `storage_purge` | `bot/handlers/admin.py:1188` `storage_purge_confirm` |

### `AdminTax` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `percent` | `bot/handlers/admin.py:2465` `admin_tax_view` | `bot/handlers/admin.py:2477` `admin_tax_set` |

### `AdminReportAutoApprove` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `value` | `bot/handlers/admin.py:4571` `report_auto_approve_edit_cb` | `bot/handlers/admin.py:4584` `report_auto_approve_edit_value` |

### `AdminReportPayCap` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `value` | `bot/handlers/admin.py:4610` `report_pay_cap_edit_cb` | `bot/handlers/admin.py:4625` `report_pay_cap_edit_value` |

### `AdminReportFix` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `daily` | `bot/handlers/admin.py:4811` `report_fix_start` | `bot/handlers/admin.py:4824` `report_fix_daily` |
| `total` | `bot/handlers/admin.py:4838` `report_fix_daily` | `bot/handlers/admin.py:4852` `report_fix_total` |

### `AdminRoles` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | `bot/handlers/admin.py:3085` `admin_roles` | `bot/handlers/admin.py:3094` `roles_target` |
| `action` | `bot/handlers/admin.py:467` `pickuser_cb`<br>`bot/handlers/admin.py:3100` `roles_target` | — |
| `role` | `bot/handlers/admin.py:3118` `roles_action` | — |

### `AdminStatuses` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `name` | `bot/handlers/admin.py:3369` `status_create_start` | `bot/handlers/admin.py:3377` `status_create_name` |
| `tag` | `bot/handlers/admin.py:3379` `status_create_name` | `bot/handlers/admin.py:3388` `status_create_tag` |
| `level` | `bot/handlers/admin.py:3395` `status_create_tag` | `bot/handlers/admin.py:3405` `status_create_level` |
| `desc` | `bot/handlers/admin.py:3416` `status_create_level` | `bot/handlers/admin.py:3421` `status_create_desc` |
| `target` | `bot/handlers/admin.py:3645` `status_grant_target`<br>`bot/handlers/admin.py:3714` `status_revoke_target` | `bot/handlers/admin.py:3655` `status_grant_target_msg` |
| `grant_action` | — | — |
| `status_pick` | `bot/handlers/admin.py:490` `pickuser_cb`<br>`bot/handlers/admin.py:499` `pickuser_cb`<br>`bot/handlers/admin.py:3666` `status_grant_target_msg`<br>`bot/handlers/admin.py:3798` `status_grant_more` | — |
| `item_pick` | — | — |
| `item_status` | — | — |

### `AdminAwards` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `name` | `bot/handlers/admin.py:3887` `award_create_start` | `bot/handlers/admin.py:3944` `award_create_name` |
| `desc` | `bot/handlers/admin.py:3950` `award_create_name` | `bot/handlers/admin.py:3958` `award_create_desc` |
| `emoji` | `bot/handlers/admin.py:3961` `award_create_desc` | `bot/handlers/admin.py:3969` `award_create_emoji` |
| `bonus` | `bot/handlers/admin.py:3935` `_award_ask_bonus` | `bot/handlers/admin.py:3977` `award_create_bonus` |
| `preview` | `bot/handlers/admin.py:3923` `_award_ask_bonus` | — |
| `target` | `bot/handlers/admin.py:4366` `award_grant_target` | `bot/handlers/admin.py:4372` `award_grant_target_msg` |
| `award_pick` | `bot/handlers/admin.py:4447` `award_revoke_pick_user` | — |
| `comment` | `bot/handlers/admin.py:4390` `award_grant_pick` | `bot/handlers/admin.py:4407` `award_grant_comment` |
| `edit_value` | `bot/handlers/admin.py:4246` `award_edit_field_pick` | `bot/handlers/admin.py:4270` `award_edit_value` |

### `AdminFishing` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `water` | — | — |
| `wf_id` | — | — |
| `value` | `bot/handlers/admin.py:7118` `admin_fishing_junk_field_pick`<br>`bot/handlers/admin.py:7692` `admin_fishing_field_pick` | `bot/handlers/admin.py:7719` `admin_fishing_value` |
| `c_name` | `bot/handlers/admin.py:7529` `admin_fishing_new` | `bot/handlers/admin.py:7538` `admin_fishing_new_name` |
| `c_desc` | `bot/handlers/admin.py:7548` `admin_fishing_new_name` | `bot/handlers/admin.py:7554` `admin_fishing_new_desc` |
| `c_sell_price` | `bot/handlers/admin.py:7557` `admin_fishing_new_desc` | `bot/handlers/admin.py:7563` `admin_fishing_new_sell_price` |
| `c_day_weight` | `bot/handlers/admin.py:7571` `admin_fishing_new_sell_price` | `bot/handlers/admin.py:7579` `admin_fishing_new_day_weight` |
| `c_night_weight` | `bot/handlers/admin.py:7587` `admin_fishing_new_day_weight` | `bot/handlers/admin.py:7595` `admin_fishing_new_night_weight` |
| `c_photo` | `bot/handlers/admin.py:7627` `admin_fishing_new_super` | `bot/handlers/admin.py:7635` `admin_fishing_new_photo` |
| `c_super_rare` | `bot/handlers/admin.py:7603` `admin_fishing_new_night_weight` | — |
| `j_name` | `bot/handlers/admin.py:7233` `admin_fishing_junk_new` | `bot/handlers/admin.py:7241` `admin_fishing_junk_new_name` |
| `j_sell` | `bot/handlers/admin.py:7247` `admin_fishing_junk_new_name` | `bot/handlers/admin.py:7253` `admin_fishing_junk_new_sell` |
| `j_chance` | `bot/handlers/admin.py:7259` `admin_fishing_junk_new_sell` | `bot/handlers/admin.py:7265` `admin_fishing_junk_new_chance` |
| `j_photo` | `bot/handlers/admin.py:7271` `admin_fishing_junk_new_chance` | `bot/handlers/admin.py:7278` `admin_fishing_junk_new_photo` |

### `AdminForest` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `f_id` | — | — |
| `field` | — | — |
| `value` | `bot/handlers/admin.py:8276` `admin_forest_field_pick` | `bot/handlers/admin.py:8302` `admin_forest_value` |
| `c_name` | `bot/handlers/admin.py:8358` `admin_forest_new` | `bot/handlers/admin.py:8367` `admin_forest_new_name` |
| `c_desc` | `bot/handlers/admin.py:8377` `admin_forest_new_name` | `bot/handlers/admin.py:8383` `admin_forest_new_desc` |
| `c_sell_price` | `bot/handlers/admin.py:8386` `admin_forest_new_desc` | `bot/handlers/admin.py:8392` `admin_forest_new_sell_price` |
| `c_chance` | `bot/handlers/admin.py:8399` `admin_forest_new_sell_price` | `bot/handlers/admin.py:8408` `admin_forest_new_chance` |
| `c_kind` | `bot/handlers/admin.py:8416` `admin_forest_new_chance` | — |
| `c_photo` | `bot/handlers/admin.py:8439` `admin_forest_new_kind` | `bot/handlers/admin.py:8447` `admin_forest_new_photo` |
| `zone_value` | `bot/handlers/admin.py:7956` `admin_forest_zone_chance`<br>`bot/handlers/admin.py:8031` `admin_forest_zone_set_pick`<br>`bot/handlers/admin.py:8044` `admin_forest_limit_set` | `bot/handlers/admin.py:8051` `admin_forest_zone_value` |

### `AdminEnemy` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `field` | `bot/handlers/admin.py:9903` `admin_enemies_field_pick` | `bot/handlers/admin.py:9909` `admin_enemies_field_value` |
| `photo` | `bot/handlers/admin.py:9960` `admin_enemies_photo_pick` | `bot/handlers/admin.py:9966` `admin_enemies_photo_value` |
| `onhit_value` | `bot/handlers/admin.py:6347` `source_enemy_effect_toggle` | `bot/handlers/admin.py:6353` `source_enemy_onhit_value` |
| `drop_chance` | `bot/handlers/admin.py:10120` `admin_enemies_drop_edit_chance`<br>`bot/handlers/admin.py:10194` `admin_enemies_drop_add_pick` | `bot/handlers/admin.py:10200` `admin_enemies_drop_chance_value` |
| `drop_qty` | `bot/handlers/admin.py:10133` `admin_enemies_drop_edit_qty`<br>`bot/handlers/admin.py:10221` `admin_enemies_drop_chance_value` | `bot/handlers/admin.py:10227` `admin_enemies_drop_qty_value` |
| `c_name` | `bot/handlers/admin.py:10266` `admin_enemies_new` | `bot/handlers/admin.py:10271` `admin_enemies_new_name` |
| `c_hp` | `bot/handlers/admin.py:10277` `admin_enemies_new_name` | `bot/handlers/admin.py:10282` `admin_enemies_new_hp` |
| `c_dmg` | `bot/handlers/admin.py:10288` `admin_enemies_new_hp` | `bot/handlers/admin.py:10293` `admin_enemies_new_dmg` |
| `c_dodge` | `bot/handlers/admin.py:10306` `admin_enemies_new_dmg` | `bot/handlers/admin.py:10311` `admin_enemies_new_dodge` |
| `c_chance` | `bot/handlers/admin.py:10317` `admin_enemies_new_dodge` | `bot/handlers/admin.py:10323` `admin_enemies_new_chance` |
| `c_loss_ap` | `bot/handlers/admin.py:10329` `admin_enemies_new_chance` | `bot/handlers/admin.py:10335` `admin_enemies_new_done` |

### `AdminCallsign` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | `bot/handlers/admin.py:780` `admin_callsign_start` | `bot/handlers/admin.py:801` `admin_callsign_target_msg` |
| `value` | `bot/handlers/admin.py:557` `pickuser_cb`<br>`bot/handlers/admin.py:811` `admin_callsign_target_msg` | `bot/handlers/admin.py:822` `admin_callsign_value_msg` |

### `AdminWing` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | `bot/handlers/admin.py:793` `admin_wing_start` | — |
| `value` | `bot/handlers/admin.py:568` `pickuser_cb` | — |

### `AdminStates` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | `bot/handlers/admin.py:5347` `admin_states_menu` | `bot/handlers/admin.py:5356` `admin_states_target_text` |
| `action` | `bot/handlers/admin.py:529` `pickuser_cb`<br>`bot/handlers/admin.py:5362` `admin_states_target_text` | — |
| `state_key` | `bot/handlers/admin.py:5391` `admin_states_op` | — |
| `minutes` | `bot/handlers/admin.py:5416` `admin_states_key` | `bot/handlers/admin.py:5425` `admin_states_minutes`<br>`bot/handlers/admin.py:5446` `admin_states_minutes_bad` |

### `AdminPlayerLog` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target` | `bot/handlers/admin.py:766` `admin_player_log_start` | `bot/handlers/admin.py:629` `admin_player_log_manual_msg` |

### `AdminSalary` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `amount` | `bot/handlers/admin.py:542` `pickuser_cb` | `bot/handlers/admin.py:5546` `admin_salary_amount` |

### `AdminLocation` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `action` | — | — |
| `target_id` | — | — |
| `key` | `bot/handlers/admin.py:8502` `loc_create` | `bot/handlers/admin.py:8766` `loc_step_key` |
| `name` | `bot/handlers/admin.py:8772` `loc_step_key` | `bot/handlers/admin.py:8777` `loc_step_name` |
| `set_name` | `bot/handlers/admin.py:8793` `loc_set_name` | `bot/handlers/admin.py:8804` `loc_step_set_name` |
| `description` | `bot/handlers/admin.py:8779` `loc_step_name`<br>`bot/handlers/admin.py:8818` `loc_step_set_name`<br>`bot/handlers/admin.py:8832` `loc_set_desc` | `bot/handlers/admin.py:9043` `loc_step_desc` |
| `mode` | `bot/handlers/admin.py:8598` `loc_set_mode`<br>`bot/handlers/admin.py:9054` `loc_step_desc` | `bot/handlers/admin.py:8611` `loc_mode_chosen` |
| `req_status` | `bot/handlers/admin.py:8624` `loc_mode_chosen`<br>`bot/handlers/admin.py:8633` `loc_mode_chosen`<br>`bot/handlers/admin.py:8642` `loc_set_status` | `bot/handlers/admin.py:8647` `loc_req_status_chosen` |
| `blocking` | `bot/handlers/admin.py:8630` `loc_mode_chosen`<br>`bot/handlers/admin.py:8661` `loc_req_status_chosen`<br>`bot/handlers/admin.py:8677` `loc_set_blocking` | `bot/handlers/admin.py:8682` `loc_blocking_chosen` |
| `preview` | `bot/handlers/admin.py:9080` `loc_glade_set`<br>`bot/handlers/admin.py:9166` `loc_fire_set`<br>`bot/handlers/admin.py:9214` `loc_clearing_set`<br>`bot/handlers/admin.py:9266` `loc_logging_set`<br>`bot/handlers/admin.py:9317` `loc_mine_set`<br>`bot/handlers/admin.py:9368` `loc_storage_set`<br>`bot/handlers/admin.py:9417` `loc_photo_set`<br>`bot/handlers/admin.py:9455` `loc_season_photo_set` | `bot/handlers/admin.py:9497` `loc_step_photo` |

### `AdminCityPhoto` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `photo` | `bot/handlers/admin.py:9112` `loc_city_fire` | `bot/handlers/admin.py:9131` `loc_city_fire_save` |

### `AdminDungeon` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `target_id` | — | — |
| `photo_tod` | `bot/handlers/admin.py:5708` `dungeon_photo_set` | `bot/handlers/admin.py:5744` `dungeon_step_photo` |
| `enemy_id` | — | — |
| `enemy_field` | — | — |
| `enemy_value` | `bot/handlers/admin.py:5980` `dungeon_enemy_field_pick` | `bot/handlers/admin.py:6006` `dungeon_enemy_value` |
| `onhit_value` | `bot/handlers/admin.py:6271` `dungeon_enemy_effect_toggle` | `bot/handlers/admin.py:6277` `dungeon_enemy_onhit_value` |
| `drop_chance` | `bot/handlers/admin.py:1646` `add_item_photo`<br>`bot/handlers/admin.py:6527` `enemy_drop_pick_item`<br>`bot/handlers/admin.py:6610` `enemy_drop_set_chance` | `bot/handlers/admin.py:6932` `enemy_drop_chance_value` |
| `drop_qty` | `bot/handlers/admin.py:6633` `enemy_drop_set_qty`<br>`bot/handlers/admin.py:6941` `enemy_drop_chance_value` | `bot/handlers/admin.py:6947` `enemy_drop_qty_value` |
| `drop_item_photo` | `bot/handlers/admin.py:6678` `enemy_drop_item_photo` | `bot/handlers/admin.py:6687` `enemy_drop_item_photo_value` |
| `drop_item_desc` | `bot/handlers/admin.py:6732` `enemy_drop_item_desc` | `bot/handlers/admin.py:6741` `enemy_drop_item_desc_value` |
| `drop_item_field` | — | — |
| `drop_item_value` | `bot/handlers/admin.py:6830` `enemy_drop_item_stat_pick` | `bot/handlers/admin.py:6841` `enemy_drop_item_stat_value` |
| `pending_enemy_id` | — | — |

### `AdminFine` — `bot/handlers/admin.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `user_id` | `bot/handlers/admin.py:2726` `fines_new` | `bot/handlers/admin.py:2732` `fines_new_user` |
| `amount` | `bot/handlers/admin.py:483` `pickuser_cb`<br>`bot/handlers/admin.py:2748` `fines_new_user` | `bot/handlers/admin.py:2753` `fines_new_amount` |
| `reason` | `bot/handlers/admin.py:2760` `fines_new_amount` | `bot/handlers/admin.py:2765` `fines_new_reason` |

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
| `waiting_recipient` | `bot/handlers/bank.py:151` `bank_transfer_manual` | `bot/handlers/bank.py:258` `process_recipient` |
| `waiting_amount` | `bot/handlers/bank.py:163` `set_recipient` | `bot/handlers/bank.py:280` `process_amount` |
| `waiting_message` | `bot/handlers/bank.py:323` `process_amount` | `bot/handlers/bank.py:332` `process_message` |
| `waiting_treasury_amount` | `bot/handlers/bank.py:209` `bank_treasury` | `bot/handlers/bank.py:219` `process_treasury_amount` |
| `waiting_fine_amount` | `bot/handlers/bank.py:463` `bank_fine_pay_part` | `bot/handlers/bank.py:469` `bank_fine_amount` |

### `ClanHallAdminPhoto` — `bot/handlers/clan_hall.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `wait_building_photo` | `bot/handlers/clan_hall.py:2143` `clan_hall_admphoto_cb` | `bot/handlers/clan_hall.py:2179` `clan_hall_admphoto_save` |
| `wait_construction_photo` | `bot/handlers/clan_hall.py:2172` `clan_hall_admconstphoto_cb` | `bot/handlers/clan_hall.py:2197` `clan_hall_admconstphoto_save` |
| `wait_expansion_photo` | `bot/handlers/clan_hall.py:2221` `clan_hall_admexphoto_cb` | `bot/handlers/clan_hall.py:2233` `clan_hall_admexphoto_save` |

### `ClansCreate` — `bot/handlers/clans.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `kind` | — | — |
| `wait_name` | `bot/handlers/clans.py:726` `clan_create_start` | `bot/handlers/clans.py:734` `clan_create_name` |
| `wait_desc` | `bot/handlers/clans.py:741` `clan_create_name` | `bot/handlers/clans.py:749` `clan_create_desc` |
| `wait_photo` | `bot/handlers/clans.py:759` `clan_create_desc` | `bot/handlers/clans.py:803` `clan_create_photo`<br>`bot/handlers/clans.py:810` `clan_create_photo_hint` |

### `ClansEdit` — `bot/handlers/clans.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `field` | — | — |
| `wait_value` | `bot/handlers/clans.py:874` `clan_edit_field_cb` | `bot/handlers/clans.py:880` `clan_edit_finish_photo`<br>`bot/handlers/clans.py:894` `clan_edit_finish_text` |

### `ClansMessage` — `bot/handlers/clans.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `wait_text` | `bot/handlers/clans.py:931` `clan_msg_start` | `bot/handlers/clans.py:939` `clan_msg_send` |

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
| `target` | `bot/handlers/inventory.py:1669` `inv_transfer_start` | `bot/handlers/inventory.py:1678` `inv_transfer_target` |
| `amount` | `bot/handlers/inventory.py:1685` `inv_transfer_target` | `bot/handlers/inventory.py:1693` `inv_transfer_amount` |
| `message` | `bot/handlers/inventory.py:1725` `inv_transfer_amount` | `bot/handlers/inventory.py:1734` `inv_transfer_message` |

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
| `waiting_photo` | `bot/handlers/profile.py:258` `set_photo` | `bot/handlers/profile.py:266` `process_photo` |
| `waiting_about` | `bot/handlers/profile.py:279` `edit_about` | `bot/handlers/profile.py:287` `process_about` |
| `waiting_callsign` | `bot/handlers/profile.py:614` `profile_callsign`<br>`bot/handlers/profile.py:625` `profile_callsign`<br>`bot/handlers/profile.py:722` `profile_callsign_buy` | `bot/handlers/profile.py:662` `profile_callsign_input` |

### `ReportSubmit` — `bot/handlers/reports.py`

| Состояние | Ставится (`set_state`) | Ловится (хендлер) |
|---|---|---|
| `waiting_photo` | `bot/handlers/reports.py:106` `report_submit_start` | `bot/handlers/reports.py:115` `report_receive_photo`<br>`bot/handlers/reports.py:130` `report_photo_expected` |
| `waiting_daily_troops` | `bot/handlers/reports.py:121` `report_receive_photo` | `bot/handlers/reports.py:135` `report_receive_daily_troops`<br>`bot/handlers/reports.py:159` `report_daily_troops_expected` |
| `waiting_total_troops` | `bot/handlers/reports.py:147` `report_receive_daily_troops` | `bot/handlers/reports.py:164` `report_receive_total_troops`<br>`bot/handlers/reports.py:195` `report_total_troops_expected` |
| `waiting_region` | `bot/handlers/reports.py:173` `report_receive_total_troops` | `bot/handlers/reports.py:200` `report_receive_region`<br>`bot/handlers/reports.py:294` `report_region_expected` |

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

- `admin:awards`: `bot/handlers/admin.py:3804`
- `admin:callsign`: `bot/handlers/admin.py:774`
- `admin:del_photo`: `bot/handlers/admin.py:748`
- `admin:dungeons`: `bot/handlers/admin.py:5606`
- `admin:enemies`: `bot/handlers/admin.py:9709`
- `admin:finance`: `bot/handlers/admin.py:2228`
- `admin:fishing`: `bot/handlers/admin.py:7301`
- `admin:forest`: `bot/handlers/admin.py:7864`
- `admin:locations`: `bot/handlers/admin.py:5581`
- `admin:logs`: `bot/handlers/admin.py:5143`
- `admin:menu`: `bot/handlers/admin.py:738`
- `admin:player_log`: `bot/handlers/admin.py:760`
- `admin:ranks`: `bot/handlers/admin.py:5033`
- `admin:reports`: `bot/handlers/admin.py:4468`
- `admin:reports_done`: `bot/handlers/admin.py:4520`
- `admin:reports_pending`: `bot/handlers/admin.py:4477`
- `admin:roles`: `bot/handlers/admin.py:3075`
- `admin:salaries`: `bot/handlers/admin.py:5450`
- `admin:saletax`: `bot/handlers/admin.py:2495`
- `admin:shop`: `bot/handlers/admin.py:889`
- `admin:states`: `bot/handlers/admin.py:5341`
- `admin:statuses`: `bot/handlers/admin.py:3309`
- `admin:storage`: `bot/handlers/admin.py:964`
- `admin:tax`: `bot/handlers/admin.py:2458`
- `admin:treasury`: `bot/handlers/admin.py:2271`
- `admin:wing`: `bot/handlers/admin.py:787`
- `aw:ach`: `bot/handlers/admin.py:3862`
- `aw:create`: `bot/handlers/admin.py:3880`
- `aw:delete`: `bot/handlers/admin.py:4021`
- `aw:edit`: `bot/handlers/admin.py:4205`
- `aw:grant`: `bot/handlers/admin.py:4363`
- `aw:list`: `bot/handlers/admin.py:3841`
- `aw:revoke`: `bot/handlers/admin.py:4444`
- `aw_comment:skip`: `bot/handlers/admin.py:4401`
- `aw_confirm`: `bot/handlers/admin.py:3997`
- `back:main`: `bot/handlers/admin.py:5316`
- `bank:balance`: `bot/handlers/bank.py:73`
- `bank:fines`: `bot/handlers/bank.py:434`
- `bank:menu`: `bot/handlers/bank.py:192`
- `bank:noop`: `bot/handlers/bank.py:539`
- `bank:transfer`: `bot/handlers/bank.py:132`
- `bank:transfer_manual`: `bot/handlers/bank.py:148`
- `bank:treasury`: `bot/handlers/bank.py:205`
- `booklet:claim`: `bot/handlers/tourist_booklet.py:71`
- `booklet:menu`: `bot/handlers/tourist_booklet.py:65`
- `cancel`: `bot/handlers/admin.py:5324`
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
- `clanh:noop`: `bot/handlers/clan_hall.py:2411`
- `clanhph:construction`: `bot/handlers/admin_clanphotos.py:172`
- `clanhph:menu`: `bot/handlers/admin_clanphotos.py:114`
- `clans:create_skip`: `bot/handlers/clans.py:814`
- `clans:noop`: `bot/handlers/clans.py:599`
- `clanshopadm:menu`: `bot/handlers/admin_shop_clan.py:103`
- `contracts:list`: `bot/handlers/dungeon.py:754`
- `del_item:back`: `bot/handlers/admin.py:1722`
- `duel:card:buy`: `bot/handlers/duel.py:246`
- `duel:help`: `bot/handlers/duel.py:224`
- `duel:list`: `bot/handlers/duel.py:278`
- `duel:menu`: `bot/handlers/duel.py:218`
- `duel:top`: `bot/handlers/duel.py:298`
- `dungeon:enemies`: `bot/handlers/admin.py:5922`
- `dungeon:exit`: `bot/handlers/dungeon.py:2605`
- `dungeon:exit:cancel`: `bot/handlers/dungeon.py:2690`
- `dungeon:exit:confirm`: `bot/handlers/dungeon.py:2652`
- `dungeon:photos`: `bot/handlers/admin.py:5689`
- `dungeon:photos:clear`: `bot/handlers/admin.py:5733`
- `enemy:fi`: `bot/handlers/admin.py:9747`
- `field:drink`: `bot/handlers/admin.py:2008`
- `field:loot_only`: `bot/handlers/admin.py:2072`
- `field:market_ok`: `bot/handlers/admin.py:2052`
- `field:photo`: `bot/handlers/admin.py:1914`
- `field:weapon_effect`: `bot/handlers/admin.py:1934`
- `fin:manual`: `bot/handlers/admin.py:2579`
- `fines:list`: `bot/handlers/admin.py:2789`
- `fines:menu`: `bot/handlers/admin.py:2708`
- `fines:new`: `bot/handlers/admin.py:2719`
- `finh:open`: `bot/handlers/admin.py:2918`
- `fireevent:enter`: `bot/handlers/fire_event.py:799`
- `fireevent:go`: `bot/handlers/fire_event.py:958`
- `fireevent:potioncancel`: `bot/handlers/fire_event.py:1373`
- `fireevent:shop`: `bot/handlers/fire_event.py:906`
- `fireevent:souvenir`: `bot/handlers/fire_event.py:830`
- `fireph:menu`: `bot/handlers/admin_firephotos.py:73`
- `fish:recover`: `bot/handlers/fishing.py:507`
- `forest:addlist`: `bot/handlers/admin.py:8197`
- `forest:new`: `bot/handlers/admin.py:8350`
- `forest:zset:sold_daily_limit`: `bot/handlers/admin.py:8036`
- `housing:menu`: `bot/handlers/housing.py:284`
- `housing:noop`: `bot/handlers/housing.py:857`
- `housing:pay_debt`: `bot/handlers/housing.py:332`
- `housing:pay_tax`: `bot/handlers/housing.py:323`
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
- `inventory:eq`: `bot/handlers/inventory.py:494`
- `inventory:list`: `bot/handlers/inventory.py:588`
- `kvp:exit`: `bot/handlers/kvp.py:752`
- `kvp:resume`: `bot/handlers/kvp.py:303`
- `kvp:start`: `bot/handlers/kvp.py:263`
- `lib:menu`: `bot/handlers/library.py:141`
- `lib:no_access`: `bot/handlers/library.py:136`
- `libadmin:add`: `bot/handlers/library.py:288`
- `libadmin:list`: `bot/handlers/library.py:384`
- `libadmin:menu`: `bot/handlers/library.py:271`
- `loc:building_pick`: `bot/handlers/admin.py:8528`
- `loc:city_fire`: `bot/handlers/admin.py:9104`
- `loc:clearing_clear`: `bot/handlers/admin.py:9238`
- `loc:clearing_set`: `bot/handlers/admin.py:9201`
- `loc:create`: `bot/handlers/admin.py:8496`
- `loc:edit_pick`: `bot/handlers/admin.py:8512`
- `loc:fire_set`: `bot/handlers/admin.py:9151`
- `loc:glade_clear`: `bot/handlers/admin.py:9188`
- `loc:glade_set`: `bot/handlers/admin.py:9066`
- `loc:logging_clear`: `bot/handlers/admin.py:9290`
- `loc:logging_set`: `bot/handlers/admin.py:9251`
- `loc:mine_clear`: `bot/handlers/admin.py:9341`
- `loc:mine_set`: `bot/handlers/admin.py:9303`
- `loc:photos`: `bot/handlers/admin.py:8992`
- `loc:photos:clear`: `bot/handlers/admin.py:9483`
- `loc:photos:clear_seasons`: `bot/handlers/admin.py:9015`
- `loc:set_blocking`: `bot/handlers/admin.py:8665`
- `loc:set_desc`: `bot/handlers/admin.py:8822`
- `loc:set_mode`: `bot/handlers/admin.py:8594`
- `loc:set_name`: `bot/handlers/admin.py:8783`
- `loc:set_status`: `bot/handlers/admin.py:8637`
- `loc:storage_clear`: `bot/handlers/admin.py:9392`
- `loc:storage_set`: `bot/handlers/admin.py:9354`
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
- `noop`: `bot/handlers/admin.py:5311`
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
- `prof:back`: `bot/handlers/profile.py:345`
- `profile`: `bot/handlers/profile.py:247`
- `profile:achievements`: `bot/handlers/profile.py:510`
- `profile:awards`: `bot/handlers/profile.py:472`
- `profile:callsign`: `bot/handlers/profile.py:600`
- `profile:callsign_buy`: `bot/handlers/profile.py:706`
- `profile:callsign_cancel`: `bot/handlers/profile.py:654`
- `profile:choose_status`: `bot/handlers/profile.py:305`
- `profile:edit_about`: `bot/handlers/profile.py:276`
- `profile:notify_toggle`: `bot/handlers/profile.py:352`
- `profile:open`: `bot/handlers/profile.py:593`
- `profile:pilot_card`: `bot/handlers/profile.py:392`
- `profile:public_toggle`: `bot/handlers/profile.py:372`
- `profile:set_photo`: `bot/handlers/profile.py:255`
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
- `rep:auto_approve_edit`: `bot/handlers/admin.py:4564`
- `rep:next`: `bot/handlers/admin.py:5006`
- `rep:pay_cap_edit`: `bot/handlers/admin.py:4603`
- `rep:speech`: `bot/handlers/representative.py:77`
- `rep:speech:delete`: `bot/handlers/representative.py:109`
- `rep:speech:write`: `bot/handlers/representative.py:89`
- `report:menu`: `bot/handlers/reports.py:51`
- `report:my_reports`: `bot/handlers/reports.py:393`
- `report:submit`: `bot/handlers/reports.py:61`
- `resv:recover`: `bot/handlers/dungeon.py:2408`
- `salary:choose`: `bot/handlers/admin.py:5508`
- `salary:pay`: `bot/handlers/admin.py:5520`
- `shop:catalog`: `bot/handlers/shop.py:233`
- `shop_admin:add`: `bot/handlers/admin.py:1233`
- `shop_admin:delete`: `bot/handlers/admin.py:1693`
- `shop_admin:edit`: `bot/handlers/admin.py:1816`
- `shop_admin:special_code`: `bot/handlers/admin.py:2536`
- `shop_del:cats`: `bot/handlers/admin.py:1810`
- `shop_edit:cats`: `bot/handlers/admin.py:1795`
- `st:create`: `bot/handlers/admin.py:3363`
- `st:delete`: `bot/handlers/admin.py:3436`
- `st:grant`: `bot/handlers/admin.py:3639`
- `st:legioner`: `bot/handlers/admin.py:3584`
- `st:list`: `bot/handlers/admin.py:3346`
- `st:more`: `bot/handlers/admin.py:3785`
- `st:revoke`: `bot/handlers/admin.py:3705`
- `storage:cats`: `bot/handlers/admin.py:983`
- `storage:create`: `bot/handlers/admin.py:1234`
- `storage:menu`: `bot/handlers/storage.py:89`
- `storage:noop`: `bot/handlers/admin.py:978`
- `treasury:debts`: `bot/handlers/admin.py:2304`
- `treasury:give`: `bot/handlers/admin.py:2403`
- `treasury:stats`: `bot/handlers/admin.py:2351`
- `vote:close_cancel`: `bot/handlers/polls.py:332`
- `vote:create`: `bot/handlers/polls.py:224`
- `wall:archive`: `bot/handlers/wall.py:318`
- `wall:view`: `bot/handlers/wall.py:152`
- `wall:write`: `bot/handlers/wall.py:173`

### По префиксу (`F.data.startswith("...")`)

- `\d+$`: `bot/handlers/admin.py:1385`; `bot/handlers/admin.py:5424`; `bot/handlers/admin.py:8050`; `bot/handlers/reports.py:199`
- `\d{1,7}$`: `bot/handlers/reports.py:134`; `bot/handlers/reports.py:163`
- `act:`: `bot/handlers/admin.py:5218`
- `addreq:`: `bot/handlers/admin.py:1584`
- `aw_del:`: `bot/handlers/admin.py:4042`
- `aw_edit:`: `bot/handlers/admin.py:4225`
- `aw_ei:`: `bot/handlers/admin.py:4236`
- `aw_kind:`: `bot/handlers/admin.py:4334`
- `aw_pick:`: `bot/handlers/admin.py:4385`
- `awr_grant:`: `bot/handlers/admin.py:4452`
- `bait:set:`: `bot/handlers/fishing.py:183`
- `bank:history`: `bot/handlers/bank.py:489`
- `bank:pickrecipient:`: `bot/handlers/bank.py:178`
- `bank:transfer:list:`: `bot/handlers/bank.py:138`
- `berry:add:(glade|clearing)$`: `bot/handlers/admin_berries.py:117`
- `berry:chance:(glade|clearing):.+$`: `bot/handlers/admin_berries.py:83`
- `berry:del:(glade|clearing):.+$`: `bot/handlers/admin_berries.py:107`
- `berry:new:(glade|clearing)$`: `bot/handlers/admin_berries.py:149`
- `berry:pick:(glade|clearing):\d+$`: `bot/handlers/admin_berries.py:135`
- `berry:row:(glade|clearing):.+$`: `bot/handlers/admin_berries.py:63`
- `berry:zone:(glade|clearing)$`: `bot/handlers/admin_berries.py:54`
- `buy5_nord:`: `bot/handlers/shop.py:496`
- `buy_housing:`: `bot/handlers/shop.py:1127`
- `buy_housing_cancel:`: `bot/handlers/shop.py:1118`
- `buy_nord:`: `bot/handlers/shop.py:486`
- `cat:`: `bot/handlers/admin.py:1306`
- `city/`: `bot/handlers/locations.py:91`
- `city:pilots:list:`: `bot/handlers/pilots.py:135`
- `clanh:admconstphoto:`: `bot/handlers/clan_hall.py:2164`
- `clanh:admexphoto:`: `bot/handlers/clan_hall.py:2207`
- `clanh:admnophoto:`: `bot/handlers/clan_hall.py:2150`
- `clanh:admphoto:`: `bot/handlers/clan_hall.py:2132`
- `clanh:bitem:`: `bot/handlers/clan_hall.py:1218`
- `clanh:buy:`: `bot/handlers/clan_hall.py:1261`
- `clanh:cancel:`: `bot/handlers/clan_hall.py:1998`
- `clanh:choose:`: `bot/handlers/clan_hall.py:1967`
- `clanh:craft:`: `bot/handlers/clan_hall.py:1589`
- `clanh:donate:`: `bot/handlers/clan_hall.py:2281`
- `clanh:expchoose:`: `bot/handlers/clan_hall.py:1456`
- `clanh:expinstall:`: `bot/handlers/clan_hall.py:1469`
- `clanh:expmanage:`: `bot/handlers/clan_hall.py:1445`
- `clanh:expup:`: `bot/handlers/clan_hall.py:1487`
- `clanh:give:`: `bot/handlers/clan_hall.py:2338`
- `clanh:hall:`: `bot/handlers/clan_hall.py:1947`
- `clanh:harvest:`: `bot/handlers/clan_hall.py:1884`
- `clanh:harvestall:`: `bot/handlers/clan_hall.py:1916`
- `clanh:inside:`: `bot/handlers/clan_hall.py:2074`
- `clanh:item:`: `bot/handlers/clan_hall.py:2307`
- `clanh:libgive:`: `bot/handlers/clan_hall.py:1329`
- `clanh:log:`: `bot/handlers/clan_hall.py:2396`
- `clanh:mushproc:`: `bot/handlers/clan_hall.py:1741`
- `clanh:mushrooms:`: `bot/handlers/clan_hall.py:1724`
- `clanh:plant:`: `bot/handlers/clan_hall.py:1860`
- `clanh:plantlist:`: `bot/handlers/clan_hall.py:1812`
- `clanh:recipe:`: `bot/handlers/clan_hall.py:1520`
- `clanh:shower:`: `bot/handlers/clan_hall.py:1776`
- `clanh:start:`: `bot/handlers/clan_hall.py:2012`
- `clanh:startfull:`: `bot/handlers/clan_hall.py:2041`
- `clanh:storage:`: `bot/handlers/clan_hall.py:2260`
- `clanh:tree_essence:`: `bot/handlers/clan_hall.py:1103`
- `clanh:tree_essence_inv:`: `bot/handlers/clan_hall.py:1138`
- `clanh:tree_essence_store:`: `bot/handlers/clan_hall.py:1166`
- `clanh:tree_medit:`: `bot/handlers/clan_hall.py:1087`
- `clanh:upgrade:`: `bot/handlers/clan_hall.py:1983`
- `clanh:use:`: `bot/handlers/clan_hall.py:1503`
- `clanhier:`: `bot/handlers/clans.py:290`
- `clanhph:bclan:`: `bot/handlers/admin_clanphotos.py:247`
- `clanhph:buildings`: `bot/handlers/admin_clanphotos.py:208`
- `clanhph:exp:`: `bot/handlers/admin_clanphotos.py:123`
- `clans:add:`: `bot/handlers/clans.py:604`
- `clans:addset:`: `bot/handlers/clans.py:621`
- `clans:cancel:`: `bot/handlers/clans.py:409`
- `clans:create:`: `bot/handlers/clans.py:716`
- `clans:del:`: `bot/handlers/clans.py:968`
- `clans:delyes:`: `bot/handlers/clans.py:985`
- `clans:edit:`: `bot/handlers/clans.py:829`
- `clans:editf:`: `bot/handlers/clans.py:853`
- `clans:join:`: `bot/handlers/clans.py:372`
- `clans:kick:`: `bot/handlers/clans.py:554`
- `clans:leader:`: `bot/handlers/clans.py:645`
- `clans:leaderset:`: `bot/handlers/clans.py:662`
- `clans:leaderunset:`: `bot/handlers/clans.py:692`
- `clans:leave:`: `bot/handlers/clans.py:419`
- `clans:list:`: `bot/handlers/clans.py:132`
- `clans:manage:`: `bot/handlers/clans.py:498`
- `clans:msg:`: `bot/handlers/clans.py:923`
- `clans:reqno:`: `bot/handlers/clans.py:481`
- `clans:reqok:`: `bot/handlers/clans.py:457`
- `clans:view:`: `bot/handlers/clans.py:169`
- `clanshopadm:add:`: `bot/handlers/admin_shop_clan.py:134`
- `clanshopadm:clan:`: `bot/handlers/admin_shop_clan.py:121`
- `clanshopadm:del:`: `bot/handlers/admin_shop_clan.py:397`
- `clanshopadm:ep:`: `bot/handlers/admin_shop_clan.py:298`
- `clanshopadm:es:`: `bot/handlers/admin_shop_clan.py:332`
- `clanshopadm:hide:`: `bot/handlers/admin_shop_clan.py:369`
- `clanshopadm:it:`: `bot/handlers/admin_shop_clan.py:257`
- `clanshopadm:show:`: `bot/handlers/admin_shop_clan.py:383`
- `confirm_del_photo:`: `bot/handlers/admin.py:868`
- `contract:enter:\d+$`: `bot/handlers/dungeon.py:834`
- `contract:enter:confirm:`: `bot/handlers/dungeon.py:880`
- `contract:pick:`: `bot/handlers/dungeon.py:782`
- `del_item:`: `bot/handlers/admin.py:1707`
- `drinksel:`: `bot/handlers/admin.py:1339`
- `duel:accept:`: `bot/handlers/duel.py:405`
- `duel:atk:`: `bot/handlers/duel.py:535`
- `duel:cancel:`: `bot/handlers/duel.py:379`
- `duel:decline:`: `bot/handlers/duel.py:391`
- `duel:def:`: `bot/handlers/duel.py:551`
- `duel:invite:`: `bot/handlers/duel.py:316`
- `duel:leave:`: `bot/handlers/duel.py:454`
- `dungeon:attack:`: `bot/handlers/dungeon.py:1386`
- `dungeon:continue:`: `bot/handlers/dungeon.py:1187`
- `dungeon:edit:`: `bot/handlers/admin.py:5626`
- `dungeon:enemy:`: `bot/handlers/admin.py:5954`
- `dungeon:escape:`: `bot/handlers/dungeon.py:2015`
- `dungeon:photo_set:`: `bot/handlers/admin.py:5698`
- `dungeon:use_slot:`: `bot/handlers/dungeon.py:1698`
- `eddrop:`: `bot/handlers/admin.py:6558`
- `eddrop_del:`: `bot/handlers/admin.py:6644`
- `eddrop_desc:`: `bot/handlers/admin.py:6716`
- `eddrop_photo:`: `bot/handlers/admin.py:6662`
- `eddrop_set_ch:`: `bot/handlers/admin.py:6599`
- `eddrop_set_q:`: `bot/handlers/admin.py:6622`
- `eddrop_stat:`: `bot/handlers/admin.py:6811`
- `eddrop_stats:`: `bot/handlers/admin.py:6772`
- `eddrop_weff:`: `bot/handlers/admin.py:6874`
- `eddrop_weff_set:`: `bot/handlers/admin.py:6896`
- `edit_item:`: `bot/handlers/admin.py:1825`
- `editem_add:`: `bot/handlers/admin.py:6510`
- `editem_new:`: `bot/handlers/admin.py:6535`
- `editem_pick:`: `bot/handlers/admin.py:6465`
- `editset:drink:`: `bot/handlers/admin.py:2031`
- `editset:weff:`: `bot/handlers/admin.py:1950`
- `enemy:card:`: `bot/handlers/admin.py:9882`
- `enemy:dcard:`: `bot/handlers/admin.py:9809`
- `enemy:del:`: `bot/handlers/admin.py:10008`
- `enemy:dn:\d+$`: `bot/handlers/admin.py:9719`
- `enemy:dropadd:`: `bot/handlers/admin.py:10185`
- `enemy:dropch:`: `bot/handlers/admin.py:10112`
- `enemy:dropdel:`: `bot/handlers/admin.py:10138`
- `enemy:dropedit:`: `bot/handlers/admin.py:10074`
- `enemy:dropitem:`: `bot/handlers/admin.py:10150`
- `enemy:dropq:`: `bot/handlers/admin.py:10125`
- `enemy:drops:`: `bot/handlers/admin.py:10064`
- `enemy:effects:\d+$`: `bot/handlers/admin.py:6227`
- `enemy:fld:`: `bot/handlers/admin.py:9892`
- `enemy:fx:src:`: `bot/handlers/admin.py:6300`
- `enemy:fx:tog:\d+:\d+$`: `bot/handlers/admin.py:6246`
- `enemy:fxt:`: `bot/handlers/admin.py:6320`
- `enemy:list:[a-z]+:[\w-]+$`: `bot/handlers/admin.py:9767`
- `enemy:new:`: `bot/handlers/admin.py:10259`
- `enemy:photo:`: `bot/handlers/admin.py:9952`
- `enemy:tog:`: `bot/handlers/admin.py:9989`
- `enemy_drops:`: `bot/handlers/admin.py:6452`
- `enemy_field:`: `bot/handlers/admin.py:5967`
- `eqequip:[a-z0-9_]+:\d+$`: `bot/handlers/inventory.py:512`
- `eqlock:[a-z0-9_]+$`: `bot/handlers/inventory.py:500`
- `eqpart:`: `bot/handlers/admin.py:1417`
- `eqslot:[a-z0-9_]+$`: `bot/handlers/inventory.py:505`
- `equnequip:[a-z0-9_]+$`: `bot/handlers/inventory.py:544`
- `field:`: `bot/handlers/admin.py:2136`
- `field:required_status`: `bot/handlers/admin.py:1864`
- `field_req:`: `bot/handlers/admin.py:1897`
- `fin:`: `bot/handlers/admin.py:2592`
- `fine:part:`: `bot/handlers/bank.py:458`
- `fine:payall:`: `bot/handlers/bank.py:447`
- `fines:cancel:`: `bot/handlers/admin.py:2814`
- `finh:h:`: `bot/handlers/admin.py:2953`
- `finh:list:`: `bot/handlers/admin.py:2929`
- `finh:u:`: `bot/handlers/admin.py:2941`
- `finuser:`: `bot/handlers/admin.py:2667`
- `fireevent:attack:`: `bot/handlers/fire_event.py:1149`
- `fireevent:backfork:`: `bot/handlers/fire_event.py:751`
- `fireevent:bait:`: `bot/handlers/fire_event.py:457`
- `fireevent:baitset:`: `bot/handlers/fire_event.py:479`
- `fireevent:cont:`: `bot/handlers/fire_event.py:363`
- `fireevent:dgive:`: `bot/handlers/fire_event.py:727`
- `fireevent:donate:`: `bot/handlers/fire_event.py:713`
- `fireevent:fishing:`: `bot/handlers/fire_event.py:545`
- `fireevent:leave:`: `bot/handlers/fire_event.py:764`
- `fireevent:potion:`: `bot/handlers/fire_event.py:1274`
- `fireevent:potionok:`: `bot/handlers/fire_event.py:1367`
- `fireevent:step:`: `bot/handlers/fire_event.py:286`
- `fireevent:wellback:`: `bot/handlers/fire_event.py:497`
- `fireevent:xchg:`: `bot/handlers/fire_event.py:918`
- `fireph:set:`: `bot/handlers/admin_firephotos.py:82`
- `fish:bait:\d+$`: `bot/handlers/fishing.py:521`
- `fish:bait:set:\d+:[a-z]+$`: `bot/handlers/fishing.py:563`
- `fish:cast:\d+$`: `bot/handlers/fishing.py:573`
- `fish:lake:\d+$`: `bot/handlers/fishing.py:500`
- `fishbuy:`: `bot/handlers/shop.py:830`
- `fishcatch:`: `bot/handlers/inventory.py:1300`
- `fishgo:`: `bot/handlers/inventory.py:1551`
- `fishing:addfish:`: `bot/handlers/admin.py:7469`
- `fishing:addlist:`: `bot/handlers/admin.py:7439`
- `fishing:del:`: `bot/handlers/admin.py:7492`
- `fishing:fish:`: `bot/handlers/admin.py:7359`
- `fishing:junk:`: `bot/handlers/admin.py:7048`
- `fishing:kind:`: `bot/handlers/admin.py:7373`
- `fishing:market:`: `bot/handlers/admin.py:7395`
- `fishing:new:`: `bot/handlers/admin.py:7517`
- `fishing:new_super:`: `bot/handlers/admin.py:7620`
- `fishing:super:`: `bot/handlers/admin.py:7417`
- `fishing:water:`: `bot/handlers/admin.py:7321`
- `fishing_field:`: `bot/handlers/admin.py:7679`
- `fishing_j:`: `bot/handlers/admin.py:7105`
- `fishing_jx:del:`: `bot/handlers/admin.py:7201`
- `fishing_jx:new:`: `bot/handlers/admin.py:7222`
- `fishing_jx:pick:`: `bot/handlers/admin.py:7174`
- `fishing_jx:pool:`: `bot/handlers/admin.py:7145`
- `fishmarket:`: `bot/handlers/inventory.py:1453`
- `fishoffer:`: `bot/handlers/shop.py:755`
- `fishprice:`: `bot/handlers/inventory.py:1533`
- `fishsell:`: `bot/handlers/inventory.py:1609`
- `fishuse:`: `bot/handlers/inventory.py:1308`
- `forest:add:`: `bot/handlers/admin.py:8222`
- `forest:area:\d+:(glade|clearing)$`: `bot/handlers/forest.py:455`
- `forest:battle:flee:\d+$`: `bot/handlers/forest.py:1225`
- `forest:battle:hit:\d+$`: `bot/handlers/forest.py:1017`
- `forest:berry:\d+:(glade|clearing)$`: `bot/handlers/forest.py:735`
- `forest:card:`: `bot/handlers/admin.py:8136`
- `forest:cast:\d+(?::(glade|clearing))?$`: `bot/handlers/forest.py:532`
- `forest:del:`: `bot/handlers/admin.py:8241`
- `forest:kind:`: `bot/handlers/admin.py:8150`
- `forest:market:`: `bot/handlers/admin.py:8175`
- `forest:new_kind:`: `bot/handlers/admin.py:8430`
- `forest:zadd:(glade|clearing):\d+$`: `bot/handlers/admin.py:8002`
- `forest:zaddlist:(glade|clearing)$`: `bot/handlers/admin.py:7975`
- `forest:zchance:(glade|clearing):\d+$`: `bot/handlers/admin.py:7948`
- `forest:zdel:(glade|clearing):\d+$`: `bot/handlers/admin.py:7963`
- `forest:zone:(glade|clearing)$`: `bot/handlers/admin.py:7874`
- `forest:zset:(glade|clearing):(\w+)$`: `bot/handlers/admin.py:8014`
- `forest_field:`: `bot/handlers/admin.py:8262`
- `housing:craft:`: `bot/handlers/housing.py:798`
- `housing:harvest:`: `bot/handlers/housing.py:1130`
- `housing:install:`: `bot/handlers/housing.py:864`
- `housing:install_item:`: `bot/handlers/housing.py:902`
- `housing:kitchen:`: `bot/handlers/housing.py:401`
- `housing:lantern_medit:`: `bot/handlers/housing.py:669`
- `housing:move:`: `bot/handlers/housing.py:1151`
- `housing:mushproc:`: `bot/handlers/housing.py:511`
- `housing:mushrooms:`: `bot/handlers/housing.py:497`
- `housing:plant:`: `bot/handlers/housing.py:1109`
- `housing:recipe:`: `bot/handlers/housing.py:753`
- `housing:room:`: `bot/handlers/housing.py:343`
- `housing:shower:`: `bot/handlers/housing.py:594`
- `housing:uninstall:`: `bot/handlers/housing.py:1009`
- `housing:uninstall_confirm:`: `bot/handlers/housing.py:1075`
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
- `inv_equip:`: `bot/handlers/inventory.py:806`
- `inv_sell:`: `bot/handlers/inventory.py:941`
- `inv_sell_keep1:`: `bot/handlers/inventory.py:961`
- `inv_sell_ok:`: `bot/handlers/inventory.py:1036`
- `inv_sellall:`: `bot/handlers/inventory.py:951`
- `inv_sellmore:`: `bot/handlers/inventory.py:1146`
- `inv_slot:`: `bot/handlers/inventory.py:860`
- `inv_transfer:`: `bot/handlers/inventory.py:1641`
- `inv_unequip:`: `bot/handlers/inventory.py:836`
- `inv_unslot:`: `bot/handlers/inventory.py:895`
- `inv_use:`: `bot/handlers/inventory.py:917`
- `inventory:cat:[^:]+$`: `bot/handlers/inventory.py:607`
- `invitem:`: `bot/handlers/inventory.py:799`
- `itembuy:`: `bot/handlers/shop.py:959`
- `itemgo:`: `bot/handlers/inventory.py:1244`
- `itemmarket:`: `bot/handlers/inventory.py:1154`
- `itemoffer:`: `bot/handlers/shop.py:891`
- `itemprice:`: `bot/handlers/inventory.py:1233`
- `kvp:attack:`: `bot/handlers/kvp.py:531`
- `kvp:attempt:`: `bot/handlers/kvp.py:456`
- `kvp:continue:`: `bot/handlers/kvp.py:425`
- `libadmin_del:`: `bot/handlers/library.py:409`
- `libadmin_sec:`: `bot/handlers/library.py:297`
- `libbook:`: `bot/handlers/library.py:204`
- `libdl:`: `bot/handlers/library.py:249`
- `libsec:[a-z]+$`: `bot/handlers/library.py:178`
- `loc:blocking:`: `bot/handlers/admin.py:8681`
- `loc:building:`: `bot/handlers/admin.py:8570`
- `loc:edit:`: `bot/handlers/admin.py:8544`
- `loc:mode:`: `bot/handlers/admin.py:8610`
- `loc:photo_set:`: `bot/handlers/admin.py:9405`
- `loc:req_status:`: `bot/handlers/admin.py:8646`
- `loc:season:(winter|spring|summer|autumn)$`: `bot/handlers/admin.py:9002`
- `loc:season_clear:(winter|spring|summer|autumn)$`: `bot/handlers/admin.py:9028`
- `loc:season_photo_set:(winter|spring|summer|autumn):(dawn|day|sunset|night)$`: `bot/handlers/admin.py:9442`
- `location:enter:`: `bot/handlers/locations.py:111`
- `location:preview:`: `bot/handlers/locations.py:40`
- `locstat:`: `bot/handlers/admin.py:5277`
- `logsite:battle:flee:\d+$`: `bot/handlers/logging_site.py:1097`
- `logsite:battle:hit:\d+$`: `bot/handlers/logging_site.py:893`
- `logsite:chop:\d+$`: `bot/handlers/logging_site.py:468`
- `logsite:fire:(1|all):\d+$`: `bot/handlers/logging_site.py:742`
- `logsite:menu:\d+$`: `bot/handlers/logging_site.py:453`
- `logsite:mill:\d+$`: `bot/handlers/logging_site.py:616`
- `logsite:plank:(1|all):\d+$`: `bot/handlers/logging_site.py:679`
- `lootonly:`: `bot/handlers/admin.py:1559`
- `marketok:`: `bot/handlers/admin.py:1537`
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
- `news:(?:off|(?:dis)?allow:-?\d+|chat:-?\d+:-?\d+|topic:-?\d+:-?\d+)$`: `bot/handlers/admin.py:3248`
- `news:arch:\d+$`: `bot/handlers/news.py:182`
- `news:del:`: `bot/handlers/news.py:476`
- `news:delconf:`: `bot/handlers/news.py:498`
- `news:edit:`: `bot/handlers/news.py:403`
- `news:view:`: `bot/handlers/news.py:199`
- `nii:set:`: `bot/handlers/nii.py:319`
- `nii:view:`: `bot/handlers/nii.py:284`
- `offercancel:fish:`: `bot/handlers/shop.py:1010`
- `offercancel:item:`: `bot/handlers/shop.py:1015`
- `page`: `bot/handlers/admin.py:420`
- `park:admin:del:`: `bot/handlers/park.py:390`
- `park:admin:delyes:`: `bot/handlers/park.py:410`
- `park:admin:edit:`: `bot/handlers/park.py:478`
- `park:adminedit:f:`: `bot/handlers/park.py:496`
- `park:statue:`: `bot/handlers/park.py:257`
- `pickuser:`: `bot/handlers/admin.py:411`
- `pollarch:day:\d{4}-\d{2}-\d{2}(?::\d+)?$`: `bot/handlers/poll_archive.py:176`
- `pollarch:days:\d+$`: `bot/handlers/poll_archive.py:154`
- `prod:`: `bot/handlers/admin.py:1497`
- `prof_sel_status:`: `bot/handlers/profile.py:330`
- `profile:award:`: `bot/handlers/profile.py:554`
- `rank_pick:`: `bot/handlers/admin.py:5110`
- `rank_promote:`: `bot/handlers/admin.py:5069`
- `rar:`: `bot/handlers/admin.py:1297`
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
- `rep:nav:`: `bot/handlers/admin.py:4995`
- `rep_fix:`: `bot/handlers/admin.py:4794`
- `rep_no:`: `bot/handlers/admin.py:4980`
- `rep_ok:`: `bot/handlers/admin.py:4911`
- `report:my:`: `bot/handlers/reports.py:388`
- `report:view:`: `bot/handlers/reports.py:400`
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
- `role:`: `bot/handlers/admin.py:3161`
- `rolop:`: `bot/handlers/admin.py:3112`
- `shop_del:cat:`: `bot/handlers/admin.py:1801`
- `shop_edit:cat:`: `bot/handlers/admin.py:1786`
- `shopcat:[^:]+$`: `bot/handlers/shop.py:253`
- `shopcat:[^:]+:\d+$`: `bot/handlers/shop.py:341`
- `shopitem:`: `bot/handlers/shop.py:352`
- `st_del:`: `bot/handlers/admin.py:3455`
- `st_key:`: `bot/handlers/admin.py:5409`
- `st_op:`: `bot/handlers/admin.py:5376`
- `st_pick:`: `bot/handlers/admin.py:3740`
- `st_rev:`: `bot/handlers/admin.py:3670`
- `storage:cat:`: `bot/handlers/admin.py:996`
- `storage:item:`: `bot/handlers/admin.py:1029`
- `storage:page:`: `bot/handlers/admin.py:1015`
- `storage:purge:`: `bot/handlers/admin.py:1159`
- `storage:restock:`: `bot/handlers/admin.py:1091`
- `toggle:`: `bot/handlers/admin.py:8686`
- `vote:cast:`: `bot/handlers/polls.py:163`
- `vote:close:`: `bot/handlers/polls.py:287`
- `vote:close_confirm:`: `bot/handlers/polls.py:310`
- `vote:results:`: `bot/handlers/polls.py:185`
- `vote:show:`: `bot/handlers/polls.py:109`
- `wall:archpage:\d+$`: `bot/handlers/wall.py:341`
- `wall:archread:\d+(?::\d+)?$`: `bot/handlers/wall.py:360`
- `wall:delete:\d+$`: `bot/handlers/wall.py:227`
- `wall:page:\d+$`: `bot/handlers/wall.py:159`
- `weff:`: `bot/handlers/admin.py:1430`
- `wing_set:`: `bot/handlers/admin.py:843`
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

