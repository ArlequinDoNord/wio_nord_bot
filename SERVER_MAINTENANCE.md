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

---

## F.A.Q.

**Можно ли просто расширить диск?** Да, если тариф позволяет — VPS-диск 14GB маленький.
Расширение через панель хостера, после чего `sudo growpart /dev/sda 1 && sudo resize2fs /dev/sda1`.

**Что если билд снова падает на «no space»?** Достаточно чаще чистить build cache:
`docker builder prune -a` (без root, от юзера `arlequin`) — это безопасно, кэш не данные.

**Почему `du /` показывает меньше, чем `df -h /`?** Часть файлов root-only
(`/swapfile`, системный journal, apt-кэш) — юзер `arlequin` их не видит без sudo.