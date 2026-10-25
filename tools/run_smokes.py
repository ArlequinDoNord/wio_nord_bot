"""Единый прогон smoke-тестов проекта (последовательно или параллельно).

Примеры запуска:
    .venv\\Scripts\\python.exe tools/run_smokes.py                 # все смоуки в 4 потока
    .venv\\Scripts\\python.exe tools/run_smokes.py -j 1            # строго последовательно
    .venv\\Scripts\\python.exe tools/run_smokes.py --last 10       # последние 10 смоуков
    .venv\\Scripts\\python.exe tools/run_smokes.py 146 158 159     # выбранные номера
    .venv\\Scripts\\python.exe tools/run_smokes.py 150-159         # диапазон номеров

Каждый smoke_NNN.py автономен (свой тестовый БД-файл `_test_smokeNNN.db`).
После завершения каждого теста раннер дополнительно подчищает осиротевшие
`_test_smokeNNN.db*`, чтобы корень проекта не засорялся.
"""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import re
import subprocess
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PYTHON = sys.executable


def find_smokes() -> list[tuple[int, str]]:
    smokes = []
    for name in sorted(os.listdir(ROOT)):
        mtch = re.fullmatch(r"smoke_(\d{2,3})\.py", name)
        if mtch:
            smokes.append((int(mtch.group(1)), os.path.join(ROOT, name)))
    return smokes


def parse_targets(specs: list[str]) -> set[int]:
    wanted: set[int] = set()
    for raw in specs:
        for part in raw.split(","):
            part = part.strip()
            if not part:
                continue
            m_range = re.fullmatch(r"(?:smoke_)?(\d+)\s*[-..]+\s*(?:smoke_)?(\d+)", part)
            if m_range:
                a, b = int(m_range.group(1)), int(m_range.group(2))
                for x in range(min(a, b), max(a, b) + 1):
                    wanted.add(x)
                continue
            m_one = re.fullmatch(r"(?:smoke_)?(\d+)(?:\.py)?", part)
            if m_one:
                wanted.add(int(m_one.group(1)))
    return wanted


def cleanup_smoke_db(num: int) -> None:
    for prefix in (f"_test_smoke{num:03d}.db", f"_test_smoke{num}.db"):
        base = os.path.join(ROOT, prefix)
        for suffix in ("", "-wal", "-shm"):
            try:
                os.remove(base + suffix)
            except OSError:
                pass


def run_one(num: int, path: str, timeout: int = 180) -> tuple[int, bool, float, list[str]]:
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    t0 = time.monotonic()
    try:
        proc = subprocess.run(
            [PYTHON, path],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=timeout,
            errors="replace",
        )
    except subprocess.TimeoutExpired:
        dt = time.monotonic() - t0
        cleanup_smoke_db(num)
        return num, False, dt, [f"HANG: тест не завершился за {timeout} сек"]
    dt = time.monotonic() - t0
    cleanup_smoke_db(num)
    tail = (proc.stdout or "").strip().splitlines()[-6:]
    if proc.returncode != 0 and not tail:
        err_lines = (proc.stderr or "").strip().splitlines()
        tail = [err_lines[-1] if err_lines else "без вывода"]
    return num, proc.returncode == 0, dt, tail


def main() -> int:
    parser = argparse.ArgumentParser(description="Запуск smoke-тестов N.O.R.D.")
    parser.add_argument(
        "targets",
        nargs="*",
        help="Номера или диапазоны смоуков (например: 146 158-159). Без аргументов — все.",
    )
    parser.add_argument(
        "-j",
        "--jobs",
        type=int,
        default=4,
        help="Число параллельных потоков (по умолчанию 4; -j 1 для последовательного).",
    )
    parser.add_argument(
        "--last",
        type=int,
        default=0,
        help="Запустить только последние N смоуков.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=180,
        help="Таймаут на один смоук в секундах (по умолчанию 180).",
    )
    args = parser.parse_args()

    smokes = find_smokes()
    if not smokes:
        print("Smoke-тесты не найдены.")
        return 1

    if args.targets:
        wanted = parse_targets(args.targets)
        smokes = [(n, p) for n, p in smokes if n in wanted]
    if args.last and args.last > 0:
        smokes = smokes[-args.last :]

    if not smokes:
        print("Не найдено смоуков по заданному фильтру.")
        return 1

    jobs = max(1, min(args.jobs, len(smokes)))
    print(f"Всего smoke к запуску: {len(smokes)} (потоков: {jobs})\n")

    t_start = time.monotonic()
    results: dict[int, tuple[bool, float, list[str]]] = {}

    if jobs == 1:
        for num, path in smokes:
            _, ok, dt, tail = run_one(num, path, timeout=args.timeout)
            results[num] = (ok, dt, tail)
            mark = "OK  " if ok else "FAIL"
            print(f"[{mark}] smoke_{num:03d} ({dt:.1f}s)")
            for line in tail[-2:] if ok else tail:
                print(f"        {line}")
    else:
        with ThreadPoolExecutor(max_workers=jobs) as pool:
            futs = {
                pool.submit(run_one, num, path, args.timeout): num
                for num, path in smokes
            }
            for fut in as_completed(futs):
                num, ok, dt, tail = fut.result()
                results[num] = (ok, dt, tail)
                mark = "OK  " if ok else "FAIL"
                summary = tail[-1] if tail else ""
                print(f"[{mark}] smoke_{num:03d} ({dt:.1f}s)  {summary}")
                if not ok:
                    for line in tail[:-1]:
                        print(f"        {line}")

    passed = sum(1 for ok, _, _ in results.values() if ok)
    failed = sum(1 for ok, _, _ in results.values() if not ok)
    total_dt = time.monotonic() - t_start

    print("\n===== СВОДКА =====")
    print(f"PASSED: {passed}   FAILED: {failed}   TIME: {total_dt:.1f}s")
    if failed:
        bad = [f"smoke_{n:03d}" for n in sorted(results) if not results[n][0]]
        print("FAILED LIST:", ", ".join(bad))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
