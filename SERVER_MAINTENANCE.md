# Памятка: обслуживание сервера N.O.R.D. (диск)

Сервер: `arlequin@89.19.210.194` (VPS, диск `/dev/sda1` — всего **14GB**).

Запрос ADMIN (24.09.2026? нет — 20.09.2026): дисковое пространство переполнялось.
**19.09.2026** docker-сборка упала: `no space left on device` при распаковке слоя
`tesseract-ocr/eng.traineddata`. Что уже сделано и что осталось под root.

---

## Уже выполнено (без root)

- `docker builder prune -a` — освобождено **797MB** кэша сборки (кэш пересоздаётся при билде).
- Из образа `wio_nord_bot` убраны неиспользуемые OCR-зависимости
  (`tesseract-ocr`, `pytesseract`, `Pillow`) — образ был 438MB, стал **255MB**.
- В `docker-compose.yml` добавлена ротация логов контейнера:
  `logging → json-file, max-size: 10m, max-file: 3`.
- Мусорная папка `~/C:UsersПользователь` (11MB, артефакт от 17.09) перенесена в
  `/tmp/C_Users_Пользователь_backup_20260920` — через время можно удалить полностью.
- Текущее состояние: `/dev/sda1` занято 76% (свободно 3.4G).

---

## Бэкап игровой БД (настроен 07.10.2026)

Живая БД — том `wio_nord_bot_nordmark_data` (`/app/data/nordmark.db`, SQLite WAL).
Снапшот делается консистентно, пока бот пишет (SQLite online backup API внутри
контейнера), проверяется `integrity_check=ok` и выносится на хост.

- Скрипт: `/home/arlequin/wio_backup.sh`; systemd user-юниты
  `wio-backup.service` + `wio-backup.timer` (`~/.config/systemd/user/`).
- Расписание: ежедневно **03:00 UTC** (+`RandomizedDelaySec=300`), `Persistent=true`
  (пропущенный запуск догоняется). Таймер включён (`systemctl --user enable --now`),
  linger у arlequin включён — работает и вне сессии ssh.
- Куда: `/home/arlequin/backups/wio_nord_bot/nordmark_YYYYMMDD_HHMMSS.db`,
  ротация — 14 последних (~1.6МБ/копия, ~23МБ всего); лог — `backup.log` там же
  и в journald (`systemctl --user status wio-backup.service`). Попутно копируется
  `backup_balance.db`.
- Проверено при настройке (07.10 09:03 UTC): файл на хосте читается,
  `integrity_check=ok`, 68 таблиц на месте.
- Восстановление при потере тома:

  ```bash
  docker run -d --rm --name n_restore -v wio_nord_bot_nordmark_data:/data wio_nord_bot-wio_nord_bot:latest sleep 300
  docker cp /home/arlequin/backups/wio_nord_bot/nordmark_<stamp>.db n_restore:/data/nordmark.db
  docker rm -f n_restore
  docker start wio_nord_bot-wio_nord_bot-1
  ```

---

## Нужен root (выполнить от root / sudo)

Юзер `arlequin` **не имеет sudo** (`sudo: I'm sorry...`). Команды ниже — от root.

### 1. Ужать системные журналы (освободит ~350MB)

```bash
sudo journalctl --vacuum-size=50M
sudo systemctl restart systemd-journald
```

На диске `/var/log/journal` лежало ~404MB — это системные журналы от root.
`journalctl --disk-usage` под `arlequin` показывает 16M, потому что видны лишь
журналы его пользователя. Vacuum уберёт архив сверх 50M.

### 2. Почистить кэш apt (освободит ~240MB)

```bash
sudo apt clean
sudo apt autoremove --purge -y
```

### 3. (Опционально) уменьшить swapfile

`/swapfile` = **2GB**, реально используется ~1.1G (RAM всего 889MB — большой gap не нужен).
Осторожно: RAM на VPS мала, не убирать совсем.

```bash
sudo swapoff /swapfile
sudo dd if=/dev/zero of=/swapfile bs=1M count=1024 status=progress
sudo mkswap /swapfile
sudo swapon /swapfile
# проверить запись в /etc/fstab на новый размер
free -h
```

### 4. (Опционально) мониторинг заполнения

Cron от root раз в час:

```bash
*/30 * * * * /usr/bin/df -h / | tail -1 | awk '{print $5}' | grep -qE '8[0-9]|9[0-9]|100' && echo "DISK HIGH ON NORD SERVER" | wall
```

### 5. Реликт root-докера: том `wio_nord_bot_nordmark_data` (07.10.2026)

На машине два демона: **rootless** (арлекин, данные в
`/home/arlequin/.local/share/docker`) и **root** (`/var/lib/docker`). Root-демон не
видит контейнер, который монтирует rootless-том, поэтому одноимённый том в
`/var/lib/docker` ему кажется `dangling`. Живая БД — **rootless** (проверено
07.10.2026: том в использовании, не dangling, БД цела, 73 игрока). «Dangling»
у root — почти наверняка **копия rootful-эры** (до миграции 17.09), её удаление
живую БД не трогает. Проверить и удалить её прицельно (НЕ `docker volume prune`):

```bash
# от root: что за том и где лежит
docker volume inspect wio_nord_bot_nordmark_data        # смотри Mountpoint (ожидается /var/lib/docker/volumes/...)
ls -la <Mountpoint>/_data                               # если лежит nordmark.db — это реликт

# сравнить с живым: размер/даты
#   реликт (root):      /var/lib/docker/volumes/wio_nord_bot_nordmark_data/_data/nordmark.db
#   живой (rootless):   /home/arlequin/.local/share/docker/volumes/wio_nord_bot_nordmark_data/_data/nordmark.db

# убедиться, что root-том не смонтирован ни в один контейнер
docker ps -q | xargs -r -I{} sh -c 'docker inspect -f "{{range .Mounts}}{{.Name}} {{.Source}} {{end}}" {}'

# удаление — только по имени, только если подтверждён реликт:
docker volume rm wio_nord_bot_nordmark_data
```

⚠️ `docker volume prune` от root **не запускать** — он не видит, что том занят
контейнером **rootless-демона**.

---

## F.A.Q.

**Можно ли просто расширить диск?** Да, если тариф позволяет — VPS-диск 14GB маленький.
Расширение через панель хостера, после чего `sudo growpart /dev/sda 1 && sudo resize2fs /dev/sda1`.

**Что если билд снова падает на «no space»?** Достаточно чаще чистить build cache:
`docker builder prune -a` (без root, от юзера `arlequin`) — это безопасно, кэш не данные.

**Почему `du /` показывает меньше, чем `df -h /`?** Часть файлов root-only
(`/swapfile`, системный journal, apt-кэш) — юзер `arlequin` их не видит без sudo.

**Почему root-docker показывает том `wio_nord_bot_nordmark_data` как dangling, и
опасен ли `docker volume prune`?** Это не живой том: живой живёт в rootless-демоне
арлекина и в использовании (не dangling). У root-демона (отдельное хранилище
`/var/lib/docker`) лежит одноимённая копия rootful-эры, её root «не видит занятой».
`docker volume prune` от root не запускать: удалить можно только одноимённый
реликт прицельно (см. «Нужен root → п.5»), а чистку кэша делать от арлекина
`docker builder prune -a` — он к данным не относится.