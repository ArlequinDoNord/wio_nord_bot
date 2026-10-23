#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/release_bump.py
Автоматический бамп версии под правила проекта.

Выполняет:
- Проверка git status (предупреждает о незакоммиченных изменениях)
- Определение текущей версии из config.py
- Выбор типа: patch/minor/major или ручной ввод
- Выбор формата анонса: явный (спойлер) или неявный намёк
- Обновление config.py: VERSION, VERSION_NOTES, PREV_VERSION, PREV_VERSION_NOTES
- Обновление CHANGELOG.md (добавляет секцию в начало)
- git add, git commit
- git tag на ТЕКУЩИЙ HEAD
- Подсказывает команды для пуша (server/origin)

ВАЖНО: пуш не делает автоматически.
"""

from __future__ import annotations
import os
import re
import sys
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config.py"
CHANGELOG = ROOT / "CHANGELOG.md"

def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    print(">>", " ".join(cmd))
    return subprocess.run(cmd, cwd=str(ROOT), check=check)

def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8")

def write_text(p: Path, s: str):
    p.write_text(s, encoding="utf-8", newline="\n")

def get_git_status() -> str:
    r = subprocess.run(["git", "status", "--short"], cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.stdout.strip()

def get_head() -> str:
    r = subprocess.run(["git", "log", "-1", "--oneline"], cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.stdout.strip()

def parse_version(v: str) -> tuple[int,int,int]:
    m = re.match(r"(\d+)\.(\d+)\.(\d+)", v.strip())
    if not m:
        raise ValueError(f"bad version {v}")
    return int(m.group(1)), int(m.group(2)), int(m.group(3))

def bump_version(v: str, t: str) -> str:
    a,b,c = parse_version(v)
    if t == "patch":
        return f"{a}.{b}.{c+1}"
    if t == "minor":
        return f"{a}.{b+1}.0"
    if t == "major":
        return f"{a+1}.0.0"
    return t  # manual

def extract_config_vars(s: str):
    # VERSION
    mver = re.search(r'^VERSION\s*=\s*"([^"]+)"', s, re.M)
    mprev = re.search(r'^PREV_VERSION\s*=\s*"([^"]+)"', s, re.M)
    mvn = re.search(r'^VERSION_NOTES\s*=\s*\((.*?)\)\s*$', s, re.S | re.M)
    mpvn = re.search(r'^PREV_VERSION_NOTES\s*=\s*\((.*?)\)\s*$', s, re.S | re.M)
    ver = mver.group(1) if mver else "0.0.0"
    prev = mprev.group(1) if mprev else "0.0.0"
    vn = mvn.group(1) if mvn else ""
    pvn = mpvn.group(1) if mpvn else ""
    return ver, prev, vn, pvn

def format_notes_block(s: str) -> str:
    s = s.strip()
    # try to split into lines nicely
    # if already has quotes/newlines keep as is logic
    return s

def update_config(s: str, new_ver: str, new_vn: str, old_ver: str, old_vn: str) -> str:
    # replace VERSION
    s2 = re.sub(r'^VERSION\s*=\s*"[^"]+"', f'VERSION = "{new_ver}"', s, flags=re.M)
    # replace PREV_VERSION
    s2 = re.sub(r'^PREV_VERSION\s*=\s*"[^"]+"', f'PREV_VERSION = "{old_ver}"', s2, flags=re.M)
    # replace VERSION_NOTES block
    vn_block = new_vn.strip()
    if vn_block and vn_block[0] != '"':
        vn_block = f'"{vn_block}"'
    s2 = re.sub(r'^VERSION_NOTES\s*=\s*\(.*?\)\s*$', f'VERSION_NOTES = ({vn_block})', s2, flags=re.S | re.M)
    # replace PREV_VERSION_NOTES
    pvn_block = old_vn.strip()
    if pvn_block and pvn_block[0] != '"':
        pvn_block = f'"{pvn_block}"'
    s2 = re.sub(r'^PREV_VERSION_NOTES\s*=\s*\(.*?\)\s*$', f'PREV_VERSION_NOTES = ({pvn_block})', s2, flags=re.S | re.M)
    return s2

def update_changelog(s: str, new_ver: str, notes: str, date_str: str) -> str:
    header = f"## [{new_ver}] - {date_str}\n\n### Изменено\n- {notes}\n\n"
    # insert after first line or at top
    if s.strip().startswith("#"):
        # find first "## ["
        m = re.search(r'^## \[', s, re.M)
        if m:
            return s[:m.start()] + header + s[m.start():]
    return header + s

def ask(prompt: str, choices: list[str] | None = None) -> str:
    print(prompt)
    if choices:
        for i,c in enumerate(choices,1):
            print(f"  {i}) {c}")
        while True:
            r = input("> ").strip()
            if r.isdigit() and 1 <= int(r) <= len(choices):
                return choices[int(r)-1]
            if r in choices:
                return r
            print("Неверный выбор")
    else:
        return input("> ").strip()

def main() -> int:
    print("=== RELEASE BUMP ===")
    print(f"HEAD: {get_head()}")
    st = get_git_status()
    if st:
        print("\nВНИМАНИЕ: есть незакоммиченные изменения:")
        print(st)
        if ask("\nПродолжить несмотря на это? (да/нет)", ["да","нет"]) != "да":
            return 1
    else:
        print("Рабочее дерево чистое")
    print("")

    cfg = read_text(CONFIG)
    cur_ver, cur_prev, cur_vn, cur_pvn = extract_config_vars(cfg)
    print(f"Текущая: VERSION={cur_ver}, PREV={cur_prev}")
    print("")

    t = ask("Тип бампа:", ["patch", "minor", "major", "ручной"])
    if t == "ручной":
        new_ver = ask("Новая версия (X.Y.Z):")
    else:
        new_ver = bump_version(cur_ver, t)
    print(f"Новая версия: {new_ver}")

    mode = ask("\nФормат анонса:", ["явный (спойлер)", "неявный (намёк)"])
    if mode == "явный (спойлер)":
        vn = ask("VERSION_NOTES (кратко, для /start и чата):").strip()
    else:
        vn = 'В глубинах... что-то изменилось'
    print(f"VERSION_NOTES: {vn}")

    ch_notes = ask("\nКраткое описание для коммита и CHANGELOG:").strip() or vn

    print("\n=== План ===")
    print(f"config.py: {cur_ver} -> {new_ver}, PREV={cur_ver}")
    print(f"VERSION_NOTES -> {vn}")
    print(f"PREV_VERSION_NOTES <- {cur_vn.strip()[:60]}...")
    print(f"CHANGELOG.md: добавить секцию [{new_ver}]")
    print(f"git commit -m 'release: v{new_ver} — {ch_notes}'")
    print(f"git tag v{new_ver} (на HEAD)")
    print("\nПуш: git push server main --tags && git push origin main --tags")

    if ask("\nВыполнить бамп?", ["да","нет"]) != "да":
        print("Отменено")
        return 0

    # update config
    new_cfg = update_config(cfg, new_ver, vn, cur_ver, cur_vn)
    write_text(CONFIG, new_cfg)
    print("config.py обновлён")

    # changelog
    if CHANGELOG.exists():
        ch = read_text(CHANGELOG)
        date_str = datetime.now().strftime("%Y-%m-%d")
        new_ch = update_changelog(ch, new_ver, ch_notes, date_str)
        write_text(CHANGELOG, new_ch)
        print("CHANGELOG.md обновлён")
    else:
        print("CHANGELOG.md не найден — пропущен")

    # git
    run(["git", "add", "config.py", "CHANGELOG.md"])
    run(["git", "commit", "-m", f"release: v{new_ver} — {ch_notes}"])
    run(["git", "tag", f"v{new_ver}"])
    print(f"\nГотово! Тег v{new_ver} повешен на HEAD")
    print(f"HEAD: {get_head()}")
    print("\nСледующий шаг:")
    print("  $env:GIT_SSH_COMMAND = 'C:/Windows/System32/OpenSSH/ssh.exe'")
    print("  git push server main --tags")
    print("  git push origin main --tags")
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nОтменено")
        raise SystemExit(1)
    except Exception as e:
        print(f"ERR: {e}")
        raise SystemExit(1)
