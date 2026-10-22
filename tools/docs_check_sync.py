#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/docs_check_sync.py
Проверка синхронизации автосгенерированных доков с исходниками.
Сравнивает время изменения исходников и соответствующих *.md
и подсказывает команды для регенерации.

Генерируемые доки:
- FSM_STATES.md      <- tools/export_states.py + utils/states.py + bot/handlers/*.py
- MIGRATIONS.md      <- tools/export_migrations.py + database/db.py
- SMOKE_INDEX.md     <- tools/export_smokes.py + smoke_*.py
- HANDLERS.md        <- tools/export_handlers.py + bot/handlers/*.py + main.py
"""

from __future__ import annotations
import os
import sys
import time
from pathlib import Path
from typing import List, Dict, Any

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"

def mtime(p: Path) -> float:
    try:
        return p.stat().st_mtime
    except FileNotFoundError:
        return 0.0

def latest_mtime(paths: List[Path]) -> float:
    if not paths:
        return 0.0
    mx = 0.0
    for p in paths:
        if p.is_dir():
            # walk
            for root, dirs, files in os.walk(p):
                # skip __pycache__
                if "__pycache__" in root:
                    continue
                for fn in files:
                    if fn.endswith(".py"):
                        mx = max(mx, mtime(Path(root) / fn))
            continue
        if p.is_file():
            mx = max(mx, mtime(p))
            continue
        # glob
        if "*" in p.name or "?" in p.name:
            for g in ROOT.glob(str(p.relative_to(ROOT)) if p.is_absolute() is False else str(p)):
                if g.is_file():
                    mx = max(mx, mtime(g))
            continue
    return mx

CHECKS: Dict[str, Dict[str, Any]] = {
    "FSM_STATES.md": {
        "gen_script": TOOLS / "export_states.py",
        "sources": [
            TOOLS / "export_states.py",
            ROOT / "utils" / "states.py",
            ROOT / "bot" / "handlers",
            ROOT / "main.py",
        ],
        "cmd": r".\.venv\Scripts\python.exe tools\export_states.py",
    },
    "MIGRATIONS.md": {
        "gen_script": TOOLS / "export_migrations.py",
        "sources": [
            TOOLS / "export_migrations.py",
            ROOT / "database" / "db.py",
        ],
        "cmd": r".\.venv\Scripts\python.exe tools\export_migrations.py",
    },
    "SMOKE_INDEX.md": {
        "gen_script": TOOLS / "export_smokes.py",
        "sources": [
            TOOLS / "export_smokes.py",
            ROOT / "tools" / "run_smokes.py",
            ROOT,  # smoke_*.py in root
        ],
        "cmd": r".\.venv\Scripts\python.exe tools\export_smokes.py",
    },
    "HANDLERS.md": {
        "gen_script": TOOLS / "export_handlers.py",
        "sources": [
            TOOLS / "export_handlers.py",
            ROOT / "bot" / "handlers",
            ROOT / "main.py",
        ],
        "cmd": r".\.venv\Scripts\python.exe tools\export_handlers.py",
    },
}

def fmt_time(ts: float) -> str:
    if ts <= 0:
        return "-"
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))

def main() -> int:
    print("=== DOCS CHECK SYNC ===")
    print(f"ROOT: {ROOT}")
    print("")

    issues = 0
    for doc_name, cfg in CHECKS.items():
        doc_path = ROOT / doc_name
        doc_m = mtime(doc_path)
        src_list = []
        for s in cfg["sources"]:
            if s == ROOT:
                # smoke_*.py
                for g in ROOT.glob("smoke_*.py"):
                    src_list.append(g)
                continue
            src_list.append(s)
        src_m = latest_mtime(src_list)
        print(f"[{doc_name}]")
        print(f"  doc mtime: {fmt_time(doc_m)}")
        print(f"  src mtime: {fmt_time(src_m)}")
        if doc_m == 0.0:
            print("  STATUS: MISSING DOC")
            issues += 1
        elif src_m > doc_m + 1.0:  # 1s grace
            print("  STATUS: OUTDATED  <- нужно перегенерировать")
            print(f"  CMD:     {cfg['cmd']}")
            issues += 1
        else:
            print("  STATUS: UP TO DATE")
        print("")

    if issues == 0:
        print("OK: все автосгенерированные доки синхронизированы")
        return 0
    else:
        print(f"WARN: {issues} файл(ов) требуют регенерации")
        print("Совет: прогнать указанные команды, закоммитить обновлённые *.md")
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
