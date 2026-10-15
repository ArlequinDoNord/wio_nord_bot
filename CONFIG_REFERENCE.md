# Справочник констант `config.py`

> **Сгенерировано** `tools/export_config.py`. Перегенерация:
> `.venv\Scripts\python.exe tools/export_config.py`.
>
> Все модульные константы `config.py`, сгруппированные по секциям
> (комментариям-разделителям `# ── … ──`). Длинные значения усечены `…`;
> точное значение — в `config.py` по строке из первой колонки.

Всего констант: **150**; разделов: **10**.

## Без раздела

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `VERSION` | `'0.27.0'` |  | :16 |
| `VERSION_NOTES` | `'Все враги Нордхайма обрели броню, а в северной чаще затаился тот, чья благосклонность дорогого стоит.'` |  | :17 |
| `PREV_VERSION` | `'0.26.0'` |  | :20 |
| `PREV_VERSION_NOTES` | `'Статистику войск по регионам перенесли в Штаб ВВС — теперь её видят командиры авиаформирований и представитель, а главком может смотреть любое формирование.'` |  | :21 |
| `TOURIST_BOOKLET_DESCRIPTION` | `'Печатная карта Нордхайма для гостей города. Просматривай превью городских локаций — и отмечай их в буклете. Собери все 9 и получи награду от командования.'` |  | :27 |
| `TOURIST_BOOKLET_PRICE` | `1` |  | :30 |
| `TOURIST_BOOKLET_SELL_PRICE` | `0` | буклет не продаётся (иначе чек-лист теряется) | :31 |
| `TOURIST_BOOKLET_AWARD` | `'Опытный турист'` |  | :32 |
| `TOURIST_BOOKLET_AWARD_EMOJI` | `'🧭'` |  | :33 |
| `TOURIST_BOOKLET_AWARD_DESCRIPTION` | `'Посетил все городские локации Нордхайма по «Буклету туриста». Знак почётного гостя города.'` |  | :34 |
| `TOURIST_BOOKLET_REWARD_NM` | `20` |  | :36 |
| `TOURIST_BOOKLET_REWARD_TX` | `'booklet'` |  | :37 |
| `TOURIST_BOOKLET_LOCATIONS` | `('townhall', 'library', 'park', 'gossmi', 'bank', 'kvp', 'hq', 'contracts', 'nii')` |  | :40 |
| `BOT_TOKEN` | `os.getenv('BOT_TOKEN')` |  | :45 |
| `ADMIN_IDS` | `[int(x) for x in os.getenv('ADMIN_IDS', '').split(',') if x.strip()]` |  | :46 |
| `_news_raw` | `os.getenv('NEWS_CHAT_ID', '').strip()` |  | :49 |
| `NEWS_CHAT_ID` | `int(_news_raw) if _news_raw.lstrip('-').isdigit() else None` |  | :50 |
| `DB_PATH` | `os.getenv('DATABASE_PATH', 'database/nordmark.db')` |  | :53 |
| `FSM_STORAGE_PATH` | `os.getenv('FSM_STORAGE_PATH', '').strip() or os.path.join(os.path.dirname(os.path.abspath(DB_PATH)), 'fsm')` |  | :62 |
| `REPORT_DAY_START_MINUTE` | `0` |  | :72 |
| `RANKS` | `[('Рекрут', 0), ('Рядовой', 100), ('Ефрейтор', 350), ('Капрал', 500), ('Сержант', 850), ('Старший Сержант', 1500), ('Лейтенант', 2500), ('Старший Лейтенант', 4040), ('Капитан', 6000), ('Майор', 850…` |  | :74 |
| `MAX_SELF_RANK_TROOPS` | `4040` |  | :95 |
| `AUTO_RANK_NAMES` | `('Рекрут', 'Рядовой', 'Ефрейтор', 'Капрал', 'Сержант', 'Старший Сержант', 'Лейтенант', 'Старший Лейтенант')` |  | :98 |
| `AWARD_MAX_SHOP_DISCOUNT` | `40` |  | :105 |
| `AWARD_MIN_REPORT_TAX` | `5` |  | :106 |
| `RANK_STATUS_TAGS` | `{'Ефрейтор': 'pilot2', 'Старший Сержант': 'pilot1', 'Старший Лейтенант': 'veteran', 'Майор': 'master_pilot', 'Полковник': 'ace'}` |  | :108 |
| `LEGIONER_ACCESS_CAP_ORDER` | `5` |  | :121 |
| `RANK_DAMAGE_TIERS` | `{'ace': (4, 8), 'master_pilot': (3, 5), 'veteran': (2, 4), 'pilot1': (1, 3), 'pilot2': (1, 2), 'recruit': (1, 1), 'tourist': (0, 1)}` |  | :127 |
| `RANK_CRIT_CHANCE` | `{'ace': 7.5, 'master_pilot': 6.0, 'veteran': 4.5, 'pilot1': 3.0, 'pilot2': 1.5, 'recruit': 0.0, 'tourist': 0.0}` |  | :145 |
| `PILOT_CRIT_MULT` | `1.4` |  | :159 |
| `PILOT_NO_WEAPON_DMG` | `(1, 1)` |  | :162 |
| `DUEL_ZONE_LABELS` | `{'head': 'Голова', 'body': 'Тело', 'hands': 'Руки', 'legs': 'Ноги'}` |  | :169 |
| `DUEL_ZONE_EMOJI` | `{'head': '🧠', 'body': '🫀', 'hands': '✊', 'legs': '🦵'}` |  | :175 |
| `DUEL_AP_COST` | `15` | списывается с обоих при старте боя | :181 |
| `DUEL_RATING_WIN` | `2` | рейтинг за победу | :182 |
| `DUEL_RATING_LOSS` | `-3` | рейтинг за поражение | :183 |
| `DUEL_RATING_DRAW` | `0` | рейтинг за ничью | :184 |
| `DUEL_RATING_FORFEIT` | `-1` | рейтинг тому, кто покинул бой («Покинуть дуэль») | :185 |
| `DUEL_RATING_FORFEIT_WIN` | `1` | рейтинг сопернику, если противник покинул бой (меньше чистой победы) | :186 |
| `DUEL_MIN_DAMAGE` | `1` | минимум урона за попавший (не уклонённый) удар | :187 |
| `DUEL_GUARD_REDUCTION` | `0.5` | доля урона, остающаяся при угаданной зоне защиты | :188 |
| `DUEL_HEAL_BETWEEN` | `0` | восстановление HP между раундами (пока нет) | :189 |
| `DUEL_CHALLENGE_TIMEOUT_SEC` | `120` | сколько живёт неотвеченный вызов | :190 |
| `DUEL_STALE_SEC` | `1800` | зависшая дуэль авто-завершается как void | :191 |
| `DUEL_GLOVES_NAME` | `'Дуэльные перчатки'` |  | :192 |
| `DUEL_GLOVES_DAMAGE` | `7` |  | :193 |
| `DUEL_GLOVES_PRICE` | `200` |  | :194 |
| `DUEL_GLOVES_SELL` | `100` |  | :195 |
| `DUEL_CLUB_CARD_NAME` | `'Клубная карта «Дом Дуэлей»'` |  | :196 |
| `DUEL_CLUB_CARD_PRICE` | `150` |  | :197 |
| `DUEL_CLUB_CARD_SELL` | `75` |  | :198 |
| `DUEL_CLUB_CARD_DAYS` | `30` |  | :199 |
| `DUEL_ACCESS_TAG` | `'pilot2'` |  | :202 |
| `RARITY_LEVELS` | `{1: 'Обычный', 2: 'Качественный', 3: 'Редкий', 4: 'Шедевр', 5: 'Легендарный'}` |  | :204 |
| `RARITY_EMOJI` | `{1: '⬜', 2: '🟩', 3: '🟦', 4: '🟪', 5: '🟧'}` |  | :212 |
| `ITEM_CATEGORIES` | `{'weapon': 'Оружие', 'consumable': 'Расходники', 'building': 'Недвижимость', 'housing': 'Жильё', 'furniture': 'Мебель и расширения', 'seeds': 'Семена', 'equipment': 'Одежда', 'resource': 'Ресурсы',…` |  | :220 |
| `MARKET_LICENSE_SLOTS` | `2` | доп. слоты при активной лицензии | :243 |
| `MARKET_LICENSE_DAYS` | `30` | срок действия лицензии (дней) | :244 |
| `MARKET_LICENSE_PRICE` | `500` | цена лицензии в НМ | :245 |
| `DUNGEON_HEAL_HARD_LIMIT` | `10` | после этого — ×1/2 | :262 |
| `DUNGEON_HEAL_SOFT_MULT` | `2 / 3` |  | :263 |
| `DUNGEON_HEAL_HARD_MULT` | `1 / 2` |  | :264 |
| `ESCAPE_HP_BONUS` | `20` |  | :279 |
| `DUNGEON_SMOKE_ESCAPE` | `95` |  | :280 |
| `DUNGEON_SMOKE_MAX` | `2` |  | :281 |
| `DUNGEON_ESCAPE_DRUNK_MULT` | `0.5` |  | :284 |
| `AP_MAX` | `150` |  | :286 |
| `AP_DAILY_RECOVERY` | `100` |  | :287 |
| `AP_BONUS_FROM_CONSUMABLE` | `50` |  | :288 |
| `AP_DAILY_RESTORE_LIMIT` | `150` |  | :293 |
| `AP_EXHAUSTED_MINUTES` | `2880` | 2 суток | :294 |
| `AP_EXHAUSTED_DAILY_RECOVERY` | `75` | суточное восстановление в «истощении» | :295 |
| `AP_EXHAUSTED_MAX_AP` | `90` | максимум ОД в «истощении» | :296 |
| `SEAWEED_DAILY_LIMIT` | `6` |  | :299 |
| `DIGESTIVE_UPSET_MINUTES` | `1440` | 24 часа | :300 |
| `ALCOHOL_WEAK_DRUNK_LIMIT` | `3` |  | :305 |
| `ALCOHOL_WEAK_VERY_DRUNK_LIMIT` | `6` |  | :306 |
| `ALCOHOL_STRONG_DRUNK_LIMIT` | `1` |  | :308 |
| `ALCOHOL_STRONG_VERY_DRUNK_LIMIT` | `2` |  | :309 |
| `DRUNK_MINUTES` | `60` |  | :310 |
| `VERY_DRUNK_MINUTES` | `360` | 6 часов | :311 |
| `DRINK_EFFECT_LABELS` | `{'alcohol_weak': '🍺 Слабоалкогольный: 3 шт/сутки — «пьян», 6 — «очень пьян»', 'alcohol_strong': '🥃 Крепкий алкоголь: 1 шт — «пьян», 2 — «очень пьян»', 'indigestion': '🤢 Вызывает «несварение» на сут…` |  | :314 |
| `SPECIAL_DEPT_CODE_MIN_LEN` | `4` |  | :325 |
| `SPECIAL_DEPT_CODE_MAX_LEN` | `8` |  | :326 |
| `SPECIAL_DEPT_ATTEMPTS_LIMIT` | `3` | ошибок кода подряд | :327 |
| `SPECIAL_DEPT_BLOCK_MINUTES` | `1440` | бан на 24 часа после 3 ошибок | :328 |
| `FISH_AP_COST` | `3` | стоимость одного заброса удочки | :331 |
| `RESERVOIR_AP_COST` | `5` |  | :336 |
| `FISH_WEIGHTS` | `[{'key': 'small', 'label': 'Мелкая', 'mult': 1.0, 'chance': 40}, {'key': 'medium', 'label': 'Средняя', 'mult': 1.15, 'chance': 40}, {'key': 'large', 'label': 'Большая', 'mult': 1.25, 'chance': 20}]` |  | :341 |
| `FISH_TREASURY_SALE_MULT` | `0.5` |  | :349 |
| `FISH_TREASURY_DAILY_LIMIT` | `300` |  | :354 |
| `FOREST_AP_COST` | `4` | запасной цена поиска, если у зоны нет ap_cost в БД | :357 |
| `FOREST_RESULT_DELAY` | `(5, 10)` | результат поиска через 5–10 секунд | :360 |
| `FOREST_SOLD_DAILY_LIMIT` | `250` |  | :365 |
| `FOREST_ALLOW_TOURISTS` | `False` |  | :370 |
| `FOREST_BOAR_PITY_TARGET` | `12` |  | :373 |
| `FOREST_BOAR_CHANCE` | `4.0` |  | :377 |
| `CALLSIGN_PRICE` | `500` |  | :379 |
| `PILOT_BASE_HP` | `100` |  | :381 |
| `FOREST_BOAR_HP` | `40` |  | :386 |
| `FOREST_BOAR_DMG` | `(4, 7)` |  | :387 |
| `FOREST_BOAR_DODGE` | `15` |  | :388 |
| `FOREST_BOAR_LOSS_AP` | `10` |  | :390 |
| `FOREST_BOAR_LOOT` | `[('Мясо кабана', 50), ('Шкура кабана', 20), ('Клык кабана', 10), ('', 20)]` |  | :392 |
| `FOREST_WHITE_WOLF_HP` | `120` |  | :404 |
| `FOREST_WHITE_WOLF_DMG` | `(7, 12)` |  | :405 |
| `FOREST_WHITE_WOLF_DODGE` | `20` |  | :406 |
| `FOREST_WHITE_WOLF_LOSS_AP` | `15` |  | :408 |
| `FOREST_WHITE_WOLF_CHANCE` | `2.0` |  | :409 |
| `FOREST_WHITE_WOLF_PITY_TARGET` | `36` |  | :412 |
| `FOREST_WHITE_WOLF_BLEED_CHANCE` | `30` |  | :414 |
| `FOREST_WHITE_WOLF_BLEED_DMG` | `3` |  | :415 |
| `FOREST_WHITE_WOLF_AUTOWIN_HP` | `20` |  | :417 |
| `FOREST_WHITE_WOLF_SMALL_BLESSING` | `'внимание севера'` |  | :419 |
| `FOREST_WHITE_WOLF_BIG_BLESSING` | `'благословение севера'` |  | :420 |
| `FOREST_BOAR_SEED` | `{'key': 'boar', 'spot': 'forest', 'name': 'Дикий кабан', 'hp': FOREST_BOAR_HP, 'dmg_min': FOREST_BOAR_DMG[0], 'dmg_max': FOREST_BOAR_DMG[1], 'dodge': FOREST_BOAR_DODGE, 'loss_ap': FOREST_BOAR_LOSS_…` |  | :427 |
| `FOREST_WHITE_WOLF_SEED` | `{'key': 'white_wolf', 'spot': 'forest', 'name': 'Белый Волк Севера', 'hp': FOREST_WHITE_WOLF_HP, 'dmg_min': FOREST_WHITE_WOLF_DMG[0], 'dmg_max': FOREST_WHITE_WOLF_DMG[1], 'dodge': FOREST_WHITE_WOLF…` |  | :454 |
| `MOLLUSK_SEED` | `{'key': 'mollusk', 'spot': 'reservoir', 'name': 'Мутировавший моллюск', 'hp': 24, 'dmg_min': 5, 'dmg_max': 9, 'dodge': 20, 'loss_ap': 12, 'chance': 4, 'pity_target': 0, 'bleed_chance': 0, 'bleed_dm…` |  | :479 |
| `MOLLUSK_ITEM_SEEDS` | `[('Мясо моллюска', 'Плотное мясо мутировавшего моллюска. В сыром виде есть нельзя — прожарь на кухне.', 120, 60, 3, 'resource', 0), ('Жемчужина', 'Редчайшая жемчужина из раковины мутировавшего молл…` |  | :504 |
| `MOLLUSK_ENEMY_DROPS` | `('Мясо моллюска', 'Жемчужина')` |  | :519 |
| `REPORT_DAILY_LIMIT` | `3` |  | :521 |
| `REPORT_AUTO_APPROVE_TROOPS` | `100` |  | :522 |
| `NEWS_PUBLISH_BONUS` | `10` |  | :526 |
| `NEWS_PUBLISH_CAP` | `28` |  | :527 |
| `ROLE_SALARY_PAY_DAY` | `28` |  | :530 |
| `REPORT_DAILY_PAY_CAP` | `4000` |  | :535 |
| `REPORT_MAX_TROOPS` | `1000000` |  | :536 |
| `REPORT_MAX_REGION` | `38` | 0 = Столица, 1..38 регионы | :537 |
| `WALL_TEXT_MAX_LEN` | `40` | лимит символов на одно изречение | :540 |
| `WALL_FREE_PER_DAY` | `4` | бесплатных сообщений в сутки | :541 |
| `WALL_PAID_STEPS` | `[(3, 30), (3, 90), (3, 200)]` | далее платные ступени: (кол-во, цена НМ) | :542 |
| `WALL_REVIEW_TOTAL` | `13` | максимум сообщений в сутки (4 + 3+3+3) | :547 |
| `WALL_PAGE_SIZE` | `5` | постов на страницу стены | :548 |
| `WALL_ARCHIVE_PAGE_SIZE` | `8` | записей архива стены на страницу списка | :549 |
| `POLL_MAX_DAYS` | `10` | максимум дней, сколько живёт опрос. Не закрыл | :552 |
| `POLL_VISIBLE` | `4` | сколько новейших опросов висит в меню голосования. | :555 |
| `POLL_ARCHIVE_DAYS_PER_PAGE` | `5` | дней (дат) архива опросов на страницу списка | :558 |
| `POLL_ARCHIVE_PER_DAY` | `6` | опросов под одним заголовком-днём | :559 |
| `REP_SPEECH_MAX_LEN` | `100` | лимит символов одного обращения | :562 |
| `REP_SPEECH_PER_DAY` | `2` | обращений в сутки от представителя | :563 |
| `AUTO_PROMOTE_MAX_TROOPS` | `4040` |  | :568 |

## Буклет туриста

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `TOURIST_BOOKLET_NAME` | `'Буклет туриста'` |  | :26 |

## Суточный цикл Нордхайма

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `REPORT_DAY_START_HOUR` | `10` |  | :71 |

## Дом Дуэлей (PvP-арена)

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `DUEL_ZONES` | `('head', 'body', 'hands', 'legs')` |  | :168 |

## Рынок: слоты продажи

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `MARKET_BASE_SLOTS` | `1` | слоты без лицензии | :242 |

## Налог на недвижимость (НМ/мес)

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `HOUSING_TAX` | `{'municipal': 0, 'studio': 20, 'apartment': 35, 'improved': 60, 'mansion': 100}` |  | :248 |

## Банк: лимит счёта туриста (НМ)

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `TOURIST_BALANCE_LIMIT` | `200` |  | :258 |

## Данж: лимит хила (количество применений за забег)

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `DUNGEON_HEAL_SOFT_LIMIT` | `6` | после этого — ×2/3 | :261 |

## Сброс протухших забегов подземелья

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `DUNGEON_RUN_STALE_SEC` | `3600` |  | :270 |

## Данж: побег и дымовая шашка

| Константа | Значение | Комментарий | config.py |
|---|---|---|---|
| `ESCAPE_BASE_CHANCE` | `25` |  | :278 |

