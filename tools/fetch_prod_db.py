# -*- coding: utf-8 -*-
"""tools/fetch_prod_db.py — снимок прод-БД для локальной актуализации каталога.

Делает согласованную копию (sqlite backup API) внутри контейнера прод-сервера,
забирает байты по SSH и кладёт в data/nordmark.db (папка data/ в .gitignore:
в БД персональные данные пилотов, в git не попадает).

Только чтение: БД на проде не меняется. Копия в контейнере удаляется.

Запуск:
    .venv\\Scripts\\python.exe tools\\fetch_prod_db.py
    .venv\\Scripts\\python.exe tools\\fetch_prod_db.py --out путь\\к\\снимку.db

Требуется SSH-доступ к серверу (ключ), см. SERVER_MAINTENANCE.md.
"""
from __future__ import annotations

import argparse
import os
import sqlite3
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOST = "arlequin@89.19.210.194"
CONTAINER = "wio_nord_bot-wio_nord_bot-1"
REMOTE_DB = "/app/data/nordmark.db"

# Скрипт уходит в `docker exec -i ... python -` через stdin: кириллицы здесь нет.
REMOTE_SCRIPT = f"""
import sqlite3, sys, os
src = sqlite3.connect('file:{REMOTE_DB}?mode=ro', uri=True)
tmp = '/tmp/_nord_snapshot.db'
if os.path.exists(tmp):
    os.remove(tmp)
dst = sqlite3.connect(tmp)
src.backup(dst)
dst.close()
src.close()
with open(tmp, 'rb') as fh:
    sys.stdout.buffer.write(fh.read())
os.remove(tmp)
"""


def fetch(out_path: str) -> None:
    ssh_env = dict(os.environ)
    ssh_env.setdefault("GIT_SSH_COMMAND", "C:/Windows/System32/OpenSSH/ssh.exe")
    remote_cmd = f"docker exec -i {CONTAINER} python -"
    result = subprocess.run(
        ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=20", HOST, remote_cmd],
        input=REMOTE_SCRIPT.encode("utf-8"),
        capture_output=True,
        env=ssh_env,
    )
    if result.returncode != 0 or not result.stdout:
        sys.stderr.write(result.stderr.decode("utf-8", errors="replace"))
        raise SystemExit(f"Не удалось получить снимок (ssh exit={result.returncode}).")

    if not result.stdout.startswith(b"SQLite format 3\x00"):
        raise SystemExit("Ответ сервера не похож на SQLite-файл — снимок не сохранён.")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=os.path.dirname(out_path), suffix=".part")
    with os.fdopen(fd, "wb") as fh:
        fh.write(result.stdout)
    conn = sqlite3.connect(f"file:{tmp_path}?mode=ro", uri=True)
    try:
        verdict = conn.execute("PRAGMA integrity_check").fetchone()[0]
        items = conn.execute("SELECT COUNT(*) FROM items").fetchone()[0]
    finally:
        conn.close()
    if verdict != "ok":
        os.remove(tmp_path)
        raise SystemExit(f"integrity_check: {verdict} — снимок отброшен.")
    os.replace(tmp_path, out_path)
    size_kb = os.path.getsize(out_path) // 1024
    print(f"снимок сохранён: {out_path} ({size_kb} КБ, предметов: {items})")


def main() -> int:
    parser = argparse.ArgumentParser(description="Снимок прод-БД (только чтение).")
    parser.add_argument("--out", default=os.path.join(ROOT, "data", "nordmark.db"))
    args = parser.parse_args()
    fetch(os.path.abspath(args.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
