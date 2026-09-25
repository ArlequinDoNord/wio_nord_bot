"""Единый прогон всех smoke-тестов проекта.

Запуск: .venv\\Scripts\\python.exe tools/run_smokes.py

Каждый smoke_NNN.py автономен (свой тестовый каталог/БД), может лишь любой
из них отклониться. Раннер гоняет их по порядку, собирает PASSED/FAILED
по каждому и в конце выдаёт сводку.
"""
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PYTHON = sys.executable


def find_smokes() -> list:
    smokes = []
    for name in sorted(os.listdir(ROOT)):
        mtch = re.fullmatch(r"smoke_(\d{2,3})\.py", name)
        if mtch:
            smokes.append((int(mtch.group(1)), os.path.join(ROOT, name)))
    return smokes


def run_one(path: str, timeout: int = 180):
    env = dict(os.environ)
    proc = subprocess.run(
        [PYTHON, path], cwd=ROOT, env=env,
        capture_output=True, text=True, timeout=timeout,
    )
    tail = (proc.stdout or "").strip().splitlines()
    tail = tail[-8:]
    return proc.returncode == 0, "\n".join(tail)


def main():
    smokes = find_smokes()
    if not smokes:
        print("Smoke-тесты не найдены.")
        return 1
    print(f"Всего smoke: {len(smokes)}\n")
    passed = failed = 0
    for num, path in smokes:
        ok, tail = run_one(path)
        mark = "OK  " if ok else "FAIL"
        print(f"[{mark}] smoke_{num:03d}")
        for line in tail:
            print(f"        {line}")
        passed += ok
        failed += (not ok)
    print("\n===== СВОДКА =====\n")
    print(f"PASSED: {passed}   FAILED: {failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())