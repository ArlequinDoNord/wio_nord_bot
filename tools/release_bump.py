#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/release_bump.py
Автоматический бамп версии под правила проекта.

Поддерживает как интерактивный режим, так и CLI-флаги:
    .venv\\Scripts\\python.exe tools/release_bump.py
    .venv\\Scripts\\python.exe tools/release_bump.py --bump patch --hint --changelog "краткое описание" --yes
    .venv\\Scripts\\python.exe tools/release_bump.py --version 0.38.7 --notes "Новинка в городе" --changelog "полное описание" --yes

Выполняет:
- Проверку git status
- Определение текущей версии из config.py
- Обновление config.py: VERSION, VERSION_NOTES, PREV_VERSION, PREV_VERSION_NOTES
- Перегенерацию CONFIG_REFERENCE.md (через tools/export_config.py)
- Обновление CHANGELOG.md в формате `## vX.Y.Z (YYYY-MM-DD)`
- git add, git commit
- git tag vX.Y.Z на ТЕКУЩИЙ HEAD
- Подсказывает команды для пуша (server/origin). ВАЖНО: пуш не делает автоматически.
"""

from __future__ import annotations
import argparse
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config.py"
CHANGELOG = ROOT / "CHANGELOG.md"
EXPORT_CONFIG = ROOT / "tools" / "export_config.py"


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    print(">>", " ".join(cmd))
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    return subprocess.run(cmd, cwd=str(ROOT), env=env, check=check)


def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def write_text(p: Path, s: str):
    p.write_text(s, encoding="utf-8", newline="\n")


def get_git_status() -> str:
    r = subprocess.run(
        ["git", "status", "--short"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return r.stdout.strip()


def get_head() -> str:
    r = subprocess.run(
        ["git", "log", "-1", "--oneline"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return r.stdout.strip()


def parse_version(v: str) -> tuple[int, int, int]:
    m = re.match(r"v?(\d+)\.(\d+)\.(\d+)", v.strip())
    if not m:
        raise ValueError(f"bad version {v}")
    return int(m.group(1)), int(m.group(2)), int(m.group(3))


def bump_version(v: str, t: str) -> str:
    a, b, c = parse_version(v)
    if t == "patch":
        return f"{a}.{b}.{c + 1}"
    if t == "minor":
        return f"{a}.{b + 1}.0"
    if t == "major":
        return f"{a + 1}.0.0"
    return t.lstrip("v")


def extract_config_vars(s: str):
    mver = re.search(r'^VERSION\s*=\s*"([^"]+)"', s, re.M)
    mprev = re.search(r'^PREV_VERSION\s*=\s*"([^"]+)"', s, re.M)
    mvn = re.search(r"^VERSION_NOTES\s*=\s*\((.*?)\)\s*$", s, re.S | re.M)
    mpvn = re.search(r"^PREV_VERSION_NOTES\s*=\s*\((.*?)\)\s*$", s, re.S | re.M)
    ver = mver.group(1) if mver else "0.0.0"
    prev = mprev.group(1) if mprev else "0.0.0"
    vn = mvn.group(1) if mvn else ""
    pvn = mpvn.group(1) if mpvn else ""
    return ver, prev, vn, pvn


def update_config(s: str, new_ver: str, new_vn: str, old_ver: str, old_vn: str) -> str:
    s2 = re.sub(r'^VERSION\s*=\s*"[^"]+"', f'VERSION = "{new_ver}"', s, flags=re.M)
    s2 = re.sub(r'^PREV_VERSION\s*=\s*"[^"]+"', f'PREV_VERSION = "{old_ver}"', s2, flags=re.M)
    vn_block = new_vn.strip()
    if vn_block and vn_block[0] != '"':
        vn_block = f'"{vn_block}"'
    s2 = re.sub(
        r"^VERSION_NOTES\s*=\s*\(.*?\)\s*$",
        f"VERSION_NOTES = ({vn_block})",
        s2,
        flags=re.S | re.M,
    )
    pvn_block = old_vn.strip()
    if pvn_block and pvn_block[0] != '"':
        pvn_block = f'"{pvn_block}"'
    s2 = re.sub(
        r"^PREV_VERSION_NOTES\s*=\s*\(.*?\)\s*$",
        f"PREV_VERSION_NOTES = ({pvn_block})",
        s2,
        flags=re.S | re.M,
    )
    return s2


def update_changelog(s: str, new_ver: str, notes: str, date_str: str) -> str:
    lines = [ln.strip() for ln in notes.splitlines() if ln.strip()]
    body = "\n".join(ln if ln.startswith("- ") else f"- {ln}" for ln in lines)
    header = f"## v{new_ver} ({date_str})\n{body}\n\n"
    m = re.search(r"^## (?:v\d+\.\d+\.\d+|\[\d+\.\d+\.\d+\])", s, re.M)
    if m:
        return s[: m.start()] + header + s[m.start() :]
    return header + s


def ask(prompt: str, choices: list[str] | None = None) -> str:
    print(prompt)
    if choices:
        for i, c in enumerate(choices, 1):
            print(f"  {i}) {c}")
        while True:
            r = input("> ").strip()
            if r.isdigit() and 1 <= int(r) <= len(choices):
                return choices[int(r) - 1]
            if r in choices:
                return r
            print("Неверный выбор")
    else:
        return input("> ").strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Бамп версии config.py + CHANGELOG.md + git tag.")
    parser.add_argument("--bump", choices=["patch", "minor", "major"], help="Тип бампа SemVer")
    parser.add_argument("--version", help="Явная версия X.Y.Z")
    parser.add_argument("--notes", help="Текст VERSION_NOTES (для явного анонса или своего намёка)")
    parser.add_argument(
        "--hint",
        action="store_true",
        help="Использовать стандартный неявный намёк ('В глубинах... что-то изменилось'), если --notes не задан",
    )
    parser.add_argument("--changelog", help="Описание для CHANGELOG.md и сообщения коммита")
    parser.add_argument("--yes", "-y", action="store_true", help="Без интерактивного подтверждения")
    args = parser.parse_args()

    print("=== RELEASE BUMP ===")
    print(f"HEAD: {get_head()}")
    st = get_git_status()
    if st and not args.yes:
        print("\nВНИМАНИЕ: есть незакоммиченные изменения:")
        print(st)
        if ask("\nПродолжить несмотря на это? (да/нет)", ["да", "нет"]) != "да":
            return 1
    elif not st:
        print("Рабочее дерево чистое")
    print("")

    cfg = read_text(CONFIG)
    cur_ver, cur_prev, cur_vn, _cur_pvn = extract_config_vars(cfg)
    print(f"Текущая: VERSION={cur_ver}, PREV={cur_prev}\n")

    if args.version:
        new_ver = args.version.lstrip("v")
        parse_version(new_ver)
    elif args.bump:
        new_ver = bump_version(cur_ver, args.bump)
    else:
        t = ask("Тип бампа:", ["patch", "minor", "major", "ручной"])
        if t == "ручной":
            new_ver = ask("Новая версия (X.Y.Z):").lstrip("v")
            parse_version(new_ver)
        else:
            new_ver = bump_version(cur_ver, t)
    print(f"Новая версия: {new_ver}")

    if args.notes:
        vn = args.notes.strip()
    elif args.hint:
        vn = "В глубинах... что-то изменилось"
    else:
        mode = ask("\nФормат анонса:", ["явный (спойлер)", "неявный (намёк)"])
        if mode == "явный (спойлер)":
            vn = ask("VERSION_NOTES (кратко, для /start и чата):").strip()
        else:
            vn = ask("Текст намёка (Enter = 'В глубинах... что-то изменилось'):").strip()
            if not vn:
                vn = "В глубинах... что-то изменилось"
    print(f"VERSION_NOTES: {vn}")

    if args.changelog:
        ch_notes = args.changelog.strip()
    elif args.yes:
        ch_notes = vn
    else:
        ch_notes = ask("\nКраткое описание для коммита и CHANGELOG:").strip() or vn

    commit_summary = ch_notes.splitlines()[0].lstrip("- ").strip()

    print("\n=== План ===")
    print(f"config.py: {cur_ver} -> {new_ver}, PREV={cur_ver}")
    print(f"VERSION_NOTES -> {vn}")
    print(f"PREV_VERSION_NOTES <- {cur_vn.strip()[:60]}...")
    print(f"CHANGELOG.md: добавить секцию ## v{new_ver}")
    print("CONFIG_REFERENCE.md: перегенерировать через tools/export_config.py")
    print(f"git commit -m 'release: v{new_ver} — {commit_summary}'")
    print(f"git tag v{new_ver} (на HEAD)")

    if not args.yes:
        if ask("\nВыполнить бамп?", ["да", "нет"]) != "да":
            print("Отменено")
            return 0

    new_cfg = update_config(cfg, new_ver, vn, cur_ver, cur_vn)
    write_text(CONFIG, new_cfg)
    print("config.py обновлён")

    if EXPORT_CONFIG.exists():
        run([sys.executable, str(EXPORT_CONFIG)])

    if CHANGELOG.exists():
        ch = read_text(CHANGELOG)
        date_str = datetime.now().strftime("%Y-%m-%d")
        new_ch = update_changelog(ch, new_ver, ch_notes, date_str)
        write_text(CHANGELOG, new_ch)
        print("CHANGELOG.md обновлён")

    files_to_stage = ["config.py", "CHANGELOG.md"]
    if (ROOT / "CONFIG_REFERENCE.md").exists():
        files_to_stage.append("CONFIG_REFERENCE.md")
    run(["git", "add", *files_to_stage])
    run(["git", "commit", "-m", f"release: v{new_ver} — {commit_summary}"])
    run(["git", "tag", f"v{new_ver}"])
    print(f"\nГотово! Тег v{new_ver} повешен на HEAD")
    print(f"HEAD: {get_head()}")
    print("\nСледующий шаг:")
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
