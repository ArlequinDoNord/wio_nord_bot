# Карта модулей-хендлеров и роутеров

> **Сгенерировано** `tools/export_handlers.py`. Перегенерация:
> `.venv\Scripts\python.exe tools/export_handlers.py`.
>
> Порядок в таблице = порядок `dp.include_router(...)` в `main.py`.
> **Чем раньше роутер подключён, тем выше приоритет его хендлеров** при
> совпадении фильтров — это главный источник «мёртвых» хендлеров.

## Порядок роутеров (main.py)

| # | Роутер (alias) | Модуль |
|---:|---|---|
| 1 | `start_router` | `bot/handlers/start.py` |
| 2 | `changelog_router` | `bot/handlers/changelog.py` |
| 3 | `profile_router` | `bot/handlers/profile.py` |
| 4 | `bank_router` | `bot/handlers/bank.py` |
| 5 | `admin_router` | `bot/handlers/admin.py` |
| 6 | `admin_recipes_router` | `bot/handlers/admin_recipes.py` |
| 7 | `shop_router` | `bot/handlers/shop.py` |
| 8 | `inventory_router` | `bot/handlers/inventory.py` |
| 9 | `reports_router` | `bot/handlers/reports.py` |
| 10 | `dungeon_router` | `bot/handlers/dungeon.py` |
| 11 | `pilots_router` | `bot/handlers/pilots.py` |
| 12 | `polls_router` | `bot/handlers/polls.py` |
| 13 | `poll_archive_router` | `bot/handlers/poll_archive.py` |
| 14 | `representative_router` | `bot/handlers/representative.py` |
| 15 | `library_router` | `bot/handlers/library.py` |
| 16 | `locations_router` | `bot/handlers/locations.py` |
| 17 | `park_router` | `bot/handlers/park.py` |
| 18 | `fishing_router` | `bot/handlers/fishing.py` |
| 19 | `forest_router` | `bot/handlers/forest.py` |
| 20 | `mine_router` | `bot/handlers/mine.py` |
| 21 | `logging_site_router` | `bot/handlers/logging_site.py` |
| 22 | `storage_router` | `bot/handlers/storage.py` |
| 23 | `housing_router` | `bot/handlers/housing.py` |
| 24 | `news_router` | `bot/handlers/news.py` |
| 25 | `kvp_router` | `bot/handlers/kvp.py` |
| 26 | `wall_router` | `bot/handlers/wall.py` |
| 27 | `hq_router` | `bot/handlers/hq.py` |
| 28 | `clans_router` | `bot/handlers/clans.py` |
| 29 | `clan_hall_router` | `bot/handlers/clan_hall.py` |
| 30 | `admin_shop_clan_router` | `bot/handlers/admin_shop_clan.py` |
| 31 | `admin_clanphotos_router` | `bot/handlers/admin_clanphotos.py` |
| 32 | `admin_firephotos_router` | `bot/handlers/admin_firephotos.py` |
| 33 | `fire_event_router` | `bot/handlers/fire_event.py` |
| 34 | `nii_router` | `bot/handlers/nii.py` |
| 35 | `tourist_booklet_router` | `bot/handlers/tourist_booklet.py` |
| 36 | `duel_router` | `bot/handlers/duel.py` |
| 37 | `mvd_router` | `bot/handlers/mvd.py` |

## Сводка по модулям

| Модуль | Назначение | Роутеры | msg | cb | Неймспейсы `F.data` | FSM-классы |
|---|---|---:|---:|---:|---|---|
| `start.py` | — | `router` | 3 | 1 | `city:` | — |
| `changelog.py` | Команда /changelog — «что нового» в боте. | `router` | 1 | 0 | — | — |
| `profile.py` | — | `router` | 5 | 16 | `prof:`, `prof_sel_status:`, `profile:` | `ProfileStates` |
| `bank.py` | — | `router` | 5 | 9 | `bank:` | `BankStates` |
| `admin.py` | Админ-панель: управление магазином, финансами, отчётами, ролями и логами. | `router` | 89 | 226 | `\d+$:`, `act:`, `addreq:`, `admin:`, `aw:`, `aw_comment:`, `aw_confirm:`, `aw_del:`, `aw_edit:`, `aw_ei:`, `aw_kind:`, `aw_pick:`, `awr_grant:`, `back:`, `cancel:`, `cat:`, `confirm_del_photo:`, `del_item:`, `drinksel:`, `dungeon:`, `eddrop:`, `eddrop_del:`, `eddrop_desc:`, `eddrop_photo:`, `eddrop_set_ch:`, `eddrop_set_q:`, `eddrop_stat:`, `eddrop_stats:`, `eddrop_weff:`, `eddrop_weff_set:`, `edit_item:`, `editem_add:`, `editem_new:`, `editem_pick:`, `editset:`, `enemy:`, `enemy_drops:`, `enemy_field:`, `eqpart:`, `field:`, `field_req:`, `fin:`, `finh:`, `finuser:`, `fishing:`, `fishing_field:`, `fishing_j:`, `forest:`, `forest_field:`, `loc:`, `locstat:`, `lootonly:`, `marketok:`, `news:`, `noop:`, `pickuser:`, `prod:`, `rank_pick:`, `rank_promote:`, `rar:`, `rep:`, `rep_fix:`, `rep_no:`, `rep_ok:`, `role:`, `rolop:`, `salary:`, `shop_admin:`, `shop_del:`, `shop_edit:`, `st:`, `st_del:`, `st_key:`, `st_op:`, `st_pick:`, `st_rev:`, `storage:`, `treasury:`, `weff:`, `wing_set:` | `AdminAddItem`, `AdminSaleTax`, `AdminSpecialCode`, `AdminEditItem`, `AdminFinance`, `AdminTreasury`, `AdminStorageRestock`, `AdminStorageDelete`, `AdminTax`, `AdminReportAutoApprove`, `AdminReportPayCap`, `AdminReportFix`, `AdminRoles`, `AdminStatuses`, `AdminAwards`, `AdminFishing`, `AdminForest`, `AdminEnemy`, `AdminCallsign`, `AdminWing`, `AdminStates`, `AdminPlayerLog`, `AdminSalary`, `AdminLocation`, `AdminCityPhoto`, `AdminDungeon` |
| `admin_recipes.py` | Менеджер рецептов крафта (v0.22.13): создание, правка и удаление рецептов. | `router` | 19 | 44 | `recadm:` | `RecipeManager` |
| `shop.py` | Магазин: каталог по категориям, покупка за Нордмарки и AP. | `router` | 3 | 14 | `buy5_nord:`, `buy_housing:`, `buy_housing_cancel:`, `buy_nord:`, `fishbuy:`, `fishoffer:`, `itembuy:`, `itemoffer:`, `offercancel:`, `shop:`, `shopcat:`, `shopitem:` | `SpecialDeptBuy` |
| `inventory.py` | Инвентарь: просмотр, использование расходников, продажа и передача предметов. | `router` | 4 | 28 | `eqequip:`, `eqlock:`, `eqslot:`, `equnequip:`, `fishcatch:`, `fishgo:`, `fishmarket:`, `fishprice:`, `fishsell:`, `fishuse:`, `inv_equip:`, `inv_sell:`, `inv_sell_keep1:`, `inv_sell_ok:`, `inv_sellall:`, `inv_sellmore:`, `inv_slot:`, `inv_transfer:`, `inv_unequip:`, `inv_unslot:`, `inv_use:`, `inventory:`, `invitem:`, `itemgo:`, `itemmarket:`, `itemprice:` | `TransferItem` |
| `reports.py` | — | `router` | 9 | 5 | `\d+$:`, `\d{1,7}$:`, `report:` | `ReportSubmit` |
| `dungeon.py` | — | `router` | 0 | 25 | `city:`, `contract:`, `contracts:`, `dungeon:`, `mollusk:`, `resv:` | `DungeonFSM` |
| `pilots.py` | Ратуша: общественный центр города — голосование, пилоты, партии, речь представителя. | `router` | 0 | 5 | `city:`, `rathaus:`, `rathaus_prof:` | — |
| `polls.py` | Голосование: показ активных опросов, участие в них и создание новых (Хранитель/Представитель). | `router` | 2 | 8 | `city:`, `vote:` | `PollCreate` |
| `poll_archive.py` | Архив опросов Ратуши — раздел библиотеки «Опросы». | `router` | 0 | 3 | `pollarch:` | — |
| `representative.py` | Голос Представителя — ежедневное обращение к городу. | `router` | 1 | 3 | `rep:` | `RepSpeech` |
| `library.py` | Библиотека Нордхайма: разделы, чтение книг, управление книгами, архив опросов. | `router` | 5 | 11 | `city:`, `lib:`, `libadmin:`, `libadmin_del:`, `libadmin_sec:`, `libbook:`, `libdl:`, `libsec:` | `AdminAddBook` |
| `locations.py` | Универсальные локации города: превью (всем) + вход (по доступу). | `router` | 0 | 5 | `city:`, `location:` | — |
| `park.py` | Городской парк Аркхольма: озеро (статика), фонтан и аллея статуй. | `router` | 7 | 14 | `park:` | `AdminStatue`, `AdminStatueEdit` |
| `fishing.py` | Рыбалка на Озере в парке. | `router` | 0 | 5 | `fish:` | — |
| `forest.py` | Лес на окраине: опушка и лесная поляна, сбор грибов и кабан. | `router` | 0 | 4 | `forest:` | — |
| `mine.py` | Железная копи: ресурсная локация (v0.31.0). | `router` | 0 | 6 | `mine:` | — |
| `logging_site.py` | Лесозаготовка: ресурсная локация в лесу (v0.37.0). | `router` | 0 | 9 | `logsite:` | — |
| `storage.py` | Городские склады: накопление выкупленных казной ресурсов. | `router` | 0 | 1 | `storage:` | — |
| `housing.py` | Жильё пилота: комнаты-расширения (кухня/верстак/кадка/душевая), крафт и растение. | `router` | 1 | 19 | `housing:` | — |
| `news.py` | Новости ГосСМИ: лента, публикация, управление выпусками, архив. | `router` | 6 | 9 | `news:` | `NewsWrite`, `NewsEdit` |
| `kvp.py` | Курс Выживания для Пилотов (К.В.П.) — тренировочный данж. | `router` | 0 | 6 | `kvp:` | `KvpFSM` |
| `wall.py` | Стена изречений — доска объявлений города. | `router` | 2 | 7 | `wall:` | `WallWrite` |
| `hq.py` | Штаб ВВС: командование рассылает приказы авиакрыльям. | `router` | 7 | 25 | `hq:` | `HqOrder`, `HqWingCreate`, `HqWingEdit` |
| `clans.py` | Партии и кланы: реестр из Ратуши. | `router` | 7 | 24 | `city:`, `clanhier:`, `clans:` | `ClansCreate`, `ClansEdit`, `ClansMessage` |
| `clan_hall.py` | Клан-холл: клановый склад и строительство кланового здания (Фаза 1). | `router` | 3 | 38 | `clanh:` | `ClanHallAdminPhoto` |
| `admin_shop_clan.py` | Админ-менеджер клановых лавок (Фаза 7). | `router` | 5 | 9 | `clanshopadm:` | `ClanShopAdmin` |
| `admin_clanphotos.py` | Админ-менеджер картинок клан-холла (Фаза 8). | `router` | 3 | 5 | `clanhph:` | `ClanPhotosAdmin` |
| `admin_firephotos.py` | Админ-менеджер картинок праздника «Пламенный Круговорот». | `router` | 1 | 2 | `fireph:` | `FirePhotosAdmin` |
| `fire_event.py` | Дни Пламенного Круговорота — праздничное событие (ТЗ — FIRE_EVENT.md). | `router` | 0 | 11 | `fireevent:` | — |
| `nii.py` | НИИ Северной Кибернетики и кремниевых систем — здание обратной связи. | `router` | 2 | 7 | `nii:` | `NiiWrite` |
| `tourist_booklet.py` | Буклет туриста: чек-лист городских локаций и разовая награда. | `router` | 0 | 2 | `booklet:` | — |
| `duel.py` | Дом Дуэлей — PvP-арена «зона на зону». | `router` | 0 | 12 | `duel:` | — |
| `mvd.py` | — | `router` | 0 | 3 | `mvd:` | — |

## Детально по модулям (точные и префиксные ключи `F.data`)

### `start.py` — —

- Роутеры: `router`
- Хендлеры: message=3, callback_query=1
- `F.data ==`: `city:menu`

### `changelog.py` — Команда /changelog — «что нового» в боте.

- Роутеры: `router`
- Хендлеры: message=1, callback_query=0

### `profile.py` — —

- Роутеры: `router`
- Хендлеры: message=5, callback_query=16
- FSM: `ProfileStates`
- `F.data.startswith`: `prof_sel_status:`, `profile:award:`
- `F.data ==`: `prof:back`, `profile`, `profile:achievements`, `profile:awards`, `profile:callsign`, `profile:callsign_buy`, `profile:callsign_cancel`, `profile:choose_status`, `profile:edit_about`, `profile:notify_toggle`, `profile:open`, `profile:pilot_card`, `profile:public_toggle`, `profile:set_photo`

### `bank.py` — —

- Роутеры: `router`
- Хендлеры: message=5, callback_query=9
- FSM: `BankStates`
- `F.data.startswith`: `bank:history`, `bank:pickrecipient:`, `bank:transfer:list:`
- `F.data ==`: `bank:balance`, `bank:menu`, `bank:noop`, `bank:transfer`, `bank:transfer_manual`, `bank:treasury`

### `admin.py` — Админ-панель: управление магазином, финансами, отчётами, ролями и логами.

- Роутеры: `router`
- Хендлеры: message=89, callback_query=226
- FSM: `AdminAddItem`, `AdminSaleTax`, `AdminSpecialCode`, `AdminEditItem`, `AdminFinance`, `AdminTreasury`, `AdminStorageRestock`, `AdminStorageDelete`, `AdminTax`, `AdminReportAutoApprove`, `AdminReportPayCap`, `AdminReportFix`, `AdminRoles`, `AdminStatuses`, `AdminAwards`, `AdminFishing`, `AdminForest`, `AdminEnemy`, `AdminCallsign`, `AdminWing`, `AdminStates`, `AdminPlayerLog`, `AdminSalary`, `AdminLocation`, `AdminCityPhoto`, `AdminDungeon`
- `F.data.startswith`: `\d+$`, `act:`, `addreq:`, `aw_del:`, `aw_edit:`, `aw_ei:`, `aw_kind:`, `aw_pick:`, `awr_grant:`, `cat:`, `confirm_del_photo:`, `del_item:`, `drinksel:`, `dungeon:edit:`, `dungeon:enemy:`, `dungeon:photo_set:`, `eddrop:`, `eddrop_del:`, `eddrop_desc:`, `eddrop_photo:`, `eddrop_set_ch:`, `eddrop_set_q:`, `eddrop_stat:`, `eddrop_stats:`, `eddrop_weff:`, `eddrop_weff_set:`, `edit_item:`, `editem_add:`, `editem_new:`, `editem_pick:`, `editset:drink:`, `editset:weff:`, `enemy:card:`, `enemy:dcard:`, `enemy:del:`, `enemy:dn:\d+$`, `enemy:dropadd:`, `enemy:dropch:`, `enemy:dropdel:`, `enemy:dropedit:`, `enemy:dropitem:`, `enemy:dropq:`, `enemy:drops:`, `enemy:effects:\d+$`, `enemy:fld:`, `enemy:fx:src:`, `enemy:fx:tog:\d+:\d+$`, `enemy:fxt:`, `enemy:list:[a-z]+:[\w-]+$`, `enemy:new:`, `enemy:photo:`, `enemy:tog:`, `enemy_drops:`, `enemy_field:`, `eqpart:`, `field:`, `field:required_status`, `field_req:`, `fin:`, `finh:h:`, `finh:list:`, `finh:u:`, `finuser:`, `fishing:addfish:`, `fishing:addlist:`, `fishing:del:`, `fishing:fish:`, `fishing:junk:`, `fishing:kind:`, `fishing:market:`, `fishing:new:`, `fishing:new_super:`, `fishing:super:`, `fishing:water:`, `fishing_field:`, `fishing_j:`, `forest:add:`, `forest:card:`, `forest:del:`, `forest:kind:`, `forest:market:`, `forest:new_kind:`, `forest:zadd:(glade|clearing):\d+$`, `forest:zaddlist:(glade|clearing)$`, `forest:zchance:(glade|clearing):\d+$`, `forest:zdel:(glade|clearing):\d+$`, `forest:zone:(glade|clearing)$`, `forest:zset:(glade|clearing):(\w+)$`, `forest_field:`, `loc:blocking:`, `loc:building:`, `loc:edit:`, `loc:mode:`, `loc:photo_set:`, `loc:req_status:`, `loc:season:(winter|spring|summer|autumn)$`, `loc:season_clear:(winter|spring|summer|autumn)$`, `loc:season_photo_set:(winter|spring|summer|autumn):(dawn|day|sunset|night)$`, `locstat:`, `lootonly:`, `marketok:`, `news:(?:off|(?:dis)?allow:-?\d+|chat:-?\d+:-?\d+|topic:-?\d+:-?\d+)$`, `pickuser:`, `prod:`, `rank_pick:`, `rank_promote:`, `rar:`, `rep:nav:`, `rep_fix:`, `rep_no:`, `rep_ok:`, `role:`, `rolop:`, `shop_del:cat:`, `shop_edit:cat:`, `st_del:`, `st_key:`, `st_op:`, `st_pick:`, `st_rev:`, `storage:cat:`, `storage:item:`, `storage:page:`, `storage:purge:`, `storage:restock:`, `weff:`, `wing_set:`
- `F.data ==`: `admin:awards`, `admin:callsign`, `admin:del_photo`, `admin:dungeons`, `admin:enemies`, `admin:finance`, `admin:fishing`, `admin:forest`, `admin:locations`, `admin:logs`, `admin:menu`, `admin:player_log`, `admin:ranks`, `admin:reports`, `admin:reports_done`, `admin:reports_pending`, `admin:roles`, `admin:salaries`, `admin:saletax`, `admin:shop`, `admin:states`, `admin:statuses`, `admin:storage`, `admin:tax`, `admin:treasury`, `admin:wing`, `aw:ach`, `aw:create`, `aw:delete`, `aw:edit`, `aw:grant`, `aw:list`, `aw:revoke`, `aw_comment:skip`, `aw_confirm`, `back:main`, `cancel`, `del_item:back`, `dungeon:enemies`, `dungeon:photos`, `dungeon:photos:clear`, `enemy:fi`, `field:drink`, `field:loot_only`, `field:market_ok`, `field:photo`, `field:weapon_effect`, `fin:manual`, `finh:open`, `forest:addlist`, `forest:new`, `forest:zset:sold_daily_limit`, `loc:building_pick`, `loc:city_fire`, `loc:clearing_clear`, `loc:clearing_set`, `loc:create`, `loc:edit_pick`, `loc:fire_set`, `loc:glade_clear`, `loc:glade_set`, `loc:logging_clear`, `loc:logging_set`, `loc:mine_clear`, `loc:mine_set`, `loc:photos`, `loc:photos:clear`, `loc:photos:clear_seasons`, `loc:set_blocking`, `loc:set_desc`, `loc:set_mode`, `loc:set_name`, `loc:set_status`, `loc:storage_clear`, `loc:storage_set`, `noop`, `rep:auto_approve_edit`, `rep:next`, `rep:pay_cap_edit`, `salary:choose`, `salary:pay`, `shop_admin:add`, `shop_admin:delete`, `shop_admin:edit`, `shop_admin:special_code`, `shop_del:cats`, `shop_edit:cats`, `st:create`, `st:delete`, `st:grant`, `st:legioner`, `st:list`, `st:more`, `st:revoke`, `storage:cats`, `storage:create`, `storage:noop`, `treasury:debts`, `treasury:give`, `treasury:stats`

### `admin_recipes.py` — Менеджер рецептов крафта (v0.22.13): создание, правка и удаление рецептов.

- Роутеры: `router`
- Хендлеры: message=19, callback_query=44
- FSM: `RecipeManager`
- `F.data.startswith`: `recadm:bookdel:`, `recadm:bookdel_yes:`, `recadm:bookopen:`, `recadm:bookpage:`, `recadm:bookpick:`, `recadm:bookspage:`, `recadm:booktoggle:`, `recadm:cat:`, `recadm:ed:`, `recadm:ed_yes:`, `recadm:ef:`, `recadm:ei:`, `recadm:eq:`, `recadm:er:`, `recadm:es:`, `recadm:et:`, `recadm:exp:`, `recadm:exv:`, `recadm:ingcat:`, `recadm:ingpick:`, `recadm:kind:`, `recadm:lvl:`, `recadm:newrar:`, `recadm:open:`, `recadm:page:`, `recadm:rar:`, `recadm:rescat:`, `recadm:respick:`, `recadm:rxv:`
- `F.data ==`: `recadm:book_done`, `recadm:books`, `recadm:cancel`, `recadm:create`, `recadm:ing_done`, `recadm:ing_more`, `recadm:ingcats`, `recadm:list`, `recadm:menu`, `recadm:no_photo`, `recadm:noop`, `recadm:res_existing`, `recadm:res_new`, `recadm:rescats`, `recadm:save`

### `shop.py` — Магазин: каталог по категориям, покупка за Нордмарки и AP.

- Роутеры: `router`
- Хендлеры: message=3, callback_query=14
- FSM: `SpecialDeptBuy`
- `F.data.startswith`: `buy5_nord:`, `buy_housing:`, `buy_housing_cancel:`, `buy_nord:`, `fishbuy:`, `fishoffer:`, `itembuy:`, `itemoffer:`, `offercancel:fish:`, `offercancel:item:`, `shopcat:[^:]+$`, `shopcat:[^:]+:\d+$`, `shopitem:`
- `F.data ==`: `shop:catalog`

### `inventory.py` — Инвентарь: просмотр, использование расходников, продажа и передача предметов.

- Роутеры: `router`
- Хендлеры: message=4, callback_query=28
- FSM: `TransferItem`
- `F.data.startswith`: `eqequip:[a-z0-9_]+:\d+$`, `eqlock:[a-z0-9_]+$`, `eqslot:[a-z0-9_]+$`, `equnequip:[a-z0-9_]+$`, `fishcatch:`, `fishgo:`, `fishmarket:`, `fishprice:`, `fishsell:`, `fishuse:`, `inv_equip:`, `inv_sell:`, `inv_sell_keep1:`, `inv_sell_ok:`, `inv_sellall:`, `inv_sellmore:`, `inv_slot:`, `inv_transfer:`, `inv_unequip:`, `inv_unslot:`, `inv_use:`, `inventory:cat:[^:]+$`, `invitem:`, `itemgo:`, `itemmarket:`, `itemprice:`
- `F.data ==`: `inventory:eq`, `inventory:list`

### `reports.py` — —

- Роутеры: `router`
- Хендлеры: message=9, callback_query=5
- FSM: `ReportSubmit`
- `F.data.startswith`: `\d+$`, `\d{1,7}$`, `report:my:`, `report:view:`
- `F.data ==`: `report:menu`, `report:my_reports`, `report:submit`

### `dungeon.py` — —

- Роутеры: `router`
- Хендлеры: message=0, callback_query=25
- FSM: `DungeonFSM`
- `F.data.startswith`: `contract:enter:\d+$`, `contract:enter:confirm:`, `contract:pick:`, `dungeon:attack:`, `dungeon:continue:`, `dungeon:escape:`, `dungeon:use_slot:`, `mollusk:flee:\d+$`, `mollusk:hit:\d+$`, `resv:bait:\d+$`, `resv:bait:set:\d+:[a-z]+$`, `resv:cast:\d+$`, `resv:deeper:\d+$`, `resv:enter:\d+$`, `resv:eq:\d+$`, `resv:eqclear:[a-z0-9_]+:\d+$`, `resv:eqset:[a-z0-9_]+:\d+:\d+$`, `resv:eqslot:[a-z0-9_]+:\d+$`, `resv:menu:\d+$`
- `F.data ==`: `city:dungeon`, `contracts:list`, `dungeon:exit`, `dungeon:exit:cancel`, `dungeon:exit:confirm`, `resv:recover`

### `pilots.py` — Ратуша: общественный центр города — голосование, пилоты, партии, речь представителя.

- Роутеры: `router`
- Хендлеры: message=0, callback_query=5
- `F.data.startswith`: `city:pilots:list:`, `rathaus:`, `rathaus_prof:`
- `F.data ==`: `city:pilots`, `city:pilots:list`

### `polls.py` — Голосование: показ активных опросов, участие в них и создание новых (Хранитель/Представитель).

- Роутеры: `router`
- Хендлеры: message=2, callback_query=8
- FSM: `PollCreate`
- `F.data.startswith`: `vote:cast:`, `vote:close:`, `vote:close_confirm:`, `vote:results:`, `vote:show:`
- `F.data ==`: `city:vote`, `vote:close_cancel`, `vote:create`

### `poll_archive.py` — Архив опросов Ратуши — раздел библиотеки «Опросы».

- Роутеры: `router`
- Хендлеры: message=0, callback_query=3
- `F.data.startswith`: `pollarch:day:\d{4}-\d{2}-\d{2}(?::\d+)?$`, `pollarch:days:\d+$`
- `F.data ==`: `pollarch:list`

### `representative.py` — Голос Представителя — ежедневное обращение к городу.

- Роутеры: `router`
- Хендлеры: message=1, callback_query=3
- FSM: `RepSpeech`
- `F.data ==`: `rep:speech`, `rep:speech:delete`, `rep:speech:write`

### `library.py` — Библиотека Нордхайма: разделы, чтение книг, управление книгами, архив опросов.

- Роутеры: `router`
- Хендлеры: message=5, callback_query=11
- FSM: `AdminAddBook`
- `F.data.startswith`: `libadmin_del:`, `libadmin_sec:`, `libbook:`, `libdl:`, `libsec:[a-z]+$`
- `F.data ==`: `city:library`, `lib:menu`, `lib:no_access`, `libadmin:add`, `libadmin:list`, `libadmin:menu`

### `locations.py` — Универсальные локации города: превью (всем) + вход (по доступу).

- Роутеры: `router`
- Хендлеры: message=0, callback_query=5
- `F.data.startswith`: `location:enter:`, `location:preview:`
- `F.data ==`: `city:business`, `city:countryside`, `city:quarter`

### `park.py` — Городской парк Аркхольма: озеро (статика), фонтан и аллея статуй.

- Роутеры: `router`
- Хендлеры: message=7, callback_query=14
- FSM: `AdminStatue`, `AdminStatueEdit`
- `F.data.startswith`: `park:admin:del:`, `park:admin:delyes:`, `park:admin:edit:`, `park:adminedit:f:`, `park:statue:`
- `F.data ==`: `park:admin`, `park:admin:add`, `park:admin:editlist`, `park:admin:list`, `park:fountain`, `park:fountain:drink`, `park:lake`, `park:menu`, `park:statues`

### `fishing.py` — Рыбалка на Озере в парке.

- Роутеры: `router`
- Хендлеры: message=0, callback_query=5
- `F.data.startswith`: `fish:bait:\d+$`, `fish:bait:set:\d+:[a-z]+$`, `fish:cast:\d+$`, `fish:lake:\d+$`
- `F.data ==`: `fish:recover`

### `forest.py` — Лес на окраине: опушка и лесная поляна, сбор грибов и кабан.

- Роутеры: `router`
- Хендлеры: message=0, callback_query=4
- `F.data.startswith`: `forest:area:\d+:(glade|clearing)$`, `forest:battle:flee:\d+$`, `forest:battle:hit:\d+$`, `forest:cast:\d+(?::(glade|clearing))?$`

### `mine.py` — Железная копи: ресурсная локация (v0.31.0).

- Роутеры: `router`
- Хендлеры: message=0, callback_query=6
- `F.data.startswith`: `mine:battle:flee:\d+$`, `mine:battle:hit:\d+$`, `mine:deeper:\d+$`, `mine:dig:\d+$`, `mine:level:\d+$`, `mine:menu:\d+$`

### `logging_site.py` — Лесозаготовка: ресурсная локация в лесу (v0.37.0).

- Роутеры: `router`
- Хендлеры: message=0, callback_query=9
- `F.data.startswith`: `logsite:battle:flee:\d+$`, `logsite:battle:hit:\d+$`, `logsite:chop:\d+$`, `logsite:fire:(1|all):\d+$`, `logsite:menu:\d+$`, `logsite:mill:\d+$`, `logsite:plank:(1|all):\d+$`
- `F.data ==`: `logsite:back`, `logsite:enter`

### `storage.py` — Городские склады: накопление выкупленных казной ресурсов.

- Роутеры: `router`
- Хендлеры: message=0, callback_query=1
- `F.data ==`: `storage:menu`

### `housing.py` — Жильё пилота: комнаты-расширения (кухня/верстак/кадка/душевая), крафт и растение.

- Роутеры: `router`
- Хендлеры: message=1, callback_query=19
- `F.data.startswith`: `housing:craft:`, `housing:harvest:`, `housing:install:`, `housing:install_item:`, `housing:kitchen:`, `housing:lantern_medit:`, `housing:move:`, `housing:mushproc:`, `housing:mushrooms:`, `housing:plant:`, `housing:recipe:`, `housing:room:`, `housing:shower:`, `housing:uninstall:`, `housing:uninstall_confirm:`
- `F.data ==`: `housing:menu`, `housing:noop`, `housing:pay_debt`, `housing:pay_tax`

### `news.py` — Новости ГосСМИ: лента, публикация, управление выпусками, архив.

- Роутеры: `router`
- Хендлеры: message=6, callback_query=9
- FSM: `NewsWrite`, `NewsEdit`
- `F.data.startswith`: `news:arch:\d+$`, `news:del:`, `news:delconf:`, `news:edit:`, `news:view:`
- `F.data ==`: `news:archive`, `news:no_photo`, `news:tab`, `news:write`

### `kvp.py` — Курс Выживания для Пилотов (К.В.П.) — тренировочный данж.

- Роутеры: `router`
- Хендлеры: message=0, callback_query=6
- FSM: `KvpFSM`
- `F.data.startswith`: `kvp:attack:`, `kvp:attempt:`, `kvp:continue:`
- `F.data ==`: `kvp:exit`, `kvp:resume`, `kvp:start`

### `wall.py` — Стена изречений — доска объявлений города.

- Роутеры: `router`
- Хендлеры: message=2, callback_query=7
- FSM: `WallWrite`
- `F.data.startswith`: `wall:archpage:\d+$`, `wall:archread:\d+(?::\d+)?$`, `wall:delete:\d+$`, `wall:page:\d+$`
- `F.data ==`: `wall:archive`, `wall:view`, `wall:write`

### `hq.py` — Штаб ВВС: командование рассылает приказы авиакрыльям.

- Роутеры: `router`
- Хендлеры: message=7, callback_query=25
- FSM: `HqOrder`, `HqWingCreate`, `HqWingEdit`
- `F.data.startswith`: `hq:farms:`, `hq:order:`, `hq:pilot:`, `hq:roster:`, `hq:wing:set:`, `hq:wingcmd:assign:`, `hq:wingcmd:pick:`, `hq:wingcmd:unset:`, `hq:wingdel:`, `hq:wingdep:`, `hq:wingdrop:`, `hq:wingedit:`, `hq:wingfarm:`, `hq:wingtake:`
- `F.data ==`: `hq:farms`, `hq:menu`, `hq:noop`, `hq:region_stats`, `hq:region_stats_refresh`, `hq:send`, `hq:wing`, `hq:wingadd`, `hq:wingcmd`, `hq:wingcmd_send`, `hq:wings`

### `clans.py` — Партии и кланы: реестр из Ратуши.

- Роутеры: `router`
- Хендлеры: message=7, callback_query=24
- FSM: `ClansCreate`, `ClansEdit`, `ClansMessage`
- `F.data.startswith`: `clanhier:`, `clans:add:`, `clans:addset:`, `clans:cancel:`, `clans:create:`, `clans:del:`, `clans:delyes:`, `clans:edit:`, `clans:editf:`, `clans:join:`, `clans:kick:`, `clans:leader:`, `clans:leaderset:`, `clans:leaderunset:`, `clans:leave:`, `clans:list:`, `clans:manage:`, `clans:msg:`, `clans:reqno:`, `clans:reqok:`, `clans:view:`
- `F.data ==`: `city:clans`, `clans:create_skip`, `clans:noop`

### `clan_hall.py` — Клан-холл: клановый склад и строительство кланового здания (Фаза 1).

- Роутеры: `router`
- Хендлеры: message=3, callback_query=38
- FSM: `ClanHallAdminPhoto`
- `F.data.startswith`: `clanh:admconstphoto:`, `clanh:admexphoto:`, `clanh:admnophoto:`, `clanh:admphoto:`, `clanh:bitem:`, `clanh:buy:`, `clanh:cancel:`, `clanh:choose:`, `clanh:craft:`, `clanh:donate:`, `clanh:expchoose:`, `clanh:expinstall:`, `clanh:expmanage:`, `clanh:expup:`, `clanh:give:`, `clanh:hall:`, `clanh:harvest:`, `clanh:harvestall:`, `clanh:inside:`, `clanh:item:`, `clanh:libgive:`, `clanh:log:`, `clanh:mushproc:`, `clanh:mushrooms:`, `clanh:plant:`, `clanh:plantlist:`, `clanh:recipe:`, `clanh:shower:`, `clanh:start:`, `clanh:startfull:`, `clanh:storage:`, `clanh:tree_essence:`, `clanh:tree_essence_inv:`, `clanh:tree_essence_store:`, `clanh:tree_medit:`, `clanh:upgrade:`, `clanh:use:`
- `F.data ==`: `clanh:noop`

### `admin_shop_clan.py` — Админ-менеджер клановых лавок (Фаза 7).

- Роутеры: `router`
- Хендлеры: message=5, callback_query=9
- FSM: `ClanShopAdmin`
- `F.data.startswith`: `clanshopadm:add:`, `clanshopadm:clan:`, `clanshopadm:del:`, `clanshopadm:ep:`, `clanshopadm:es:`, `clanshopadm:hide:`, `clanshopadm:it:`, `clanshopadm:show:`
- `F.data ==`: `clanshopadm:menu`

### `admin_clanphotos.py` — Админ-менеджер картинок клан-холла (Фаза 8).

- Роутеры: `router`
- Хендлеры: message=3, callback_query=5
- FSM: `ClanPhotosAdmin`
- `F.data.startswith`: `clanhph:bclan:`, `clanhph:buildings`, `clanhph:exp:`
- `F.data ==`: `clanhph:construction`, `clanhph:menu`

### `admin_firephotos.py` — Админ-менеджер картинок праздника «Пламенный Круговорот».

- Роутеры: `router`
- Хендлеры: message=1, callback_query=2
- FSM: `FirePhotosAdmin`
- `F.data.startswith`: `fireph:set:`
- `F.data ==`: `fireph:menu`

### `fire_event.py` — Дни Пламенного Круговорота — праздничное событие (ТЗ — FIRE_EVENT.md).

- Роутеры: `router`
- Хендлеры: message=0, callback_query=11
- `F.data.startswith`: `fireevent:attack:`, `fireevent:cont:`, `fireevent:fishing:`, `fireevent:leave:`, `fireevent:potion:`, `fireevent:potionok:`, `fireevent:step:`
- `F.data ==`: `fireevent:enter`, `fireevent:go`, `fireevent:potioncancel`, `fireevent:souvenir`

### `nii.py` — НИИ Северной Кибернетики и кремниевых систем — здание обратной связи.

- Роутеры: `router`
- Хендлеры: message=2, callback_query=7
- FSM: `NiiWrite`
- `F.data.startswith`: `nii:set:`, `nii:view:`
- `F.data ==`: `nii:all`, `nii:menu_back`, `nii:mine`, `nii:no_photo`, `nii:write`

### `tourist_booklet.py` — Буклет туриста: чек-лист городских локаций и разовая награда.

- Роутеры: `router`
- Хендлеры: message=0, callback_query=2
- `F.data ==`: `booklet:claim`, `booklet:menu`

### `duel.py` — Дом Дуэлей — PvP-арена «зона на зону».

- Роутеры: `router`
- Хендлеры: message=0, callback_query=12
- `F.data.startswith`: `duel:accept:`, `duel:atk:`, `duel:cancel:`, `duel:decline:`, `duel:def:`, `duel:invite:`, `duel:leave:`
- `F.data ==`: `duel:card:buy`, `duel:help`, `duel:list`, `duel:menu`, `duel:top`

### `mvd.py` — —

- Роутеры: `router`
- Хендлеры: message=0, callback_query=3
- `F.data.startswith`: `mvd:arch:`, `mvd:archive:`
- `F.data ==`: `mvd:menu`

