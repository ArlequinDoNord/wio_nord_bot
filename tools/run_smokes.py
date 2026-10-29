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


def collect_changed_files(base: str) -> set[str] | None:
    """Изменённые файлы (относительные пути с '/' из корня репо) или None при сбое.

    base == WORKING → незакоммиченное: diff HEAD (включая staged) + untracked.
    Иначе → diff от git-базы (commit/branch/тег): 'origin/main', 'HEAD~1', тег.
    Работает только внутри git-репозитория.
    """
    def run_git(*cmd: str) -> str | None:
        try:
            proc = subprocess.run(["git", *cmd], cwd=ROOT, capture_output=True,
                                  text=True, encoding="utf-8", errors="replace",
                                  timeout=30)
        except (OSError, subprocess.TimeoutExpired):
            return None
        return proc.stdout if proc.returncode == 0 else None

    files: set[str] = set()
    if base == "WORKING":
        out = run_git("diff", "--name-only", "HEAD")
        if out is None:
            return None
        files |= {line.strip().replace("\\", "/") for line in out.splitlines()
                  if line.strip()}
        out = run_git("ls-files", "--others", "--exclude-standard")
        if out is None:
            return None
        files |= {line.strip().replace("\\", "/") for line in out.splitlines()
                  if line.strip()}
    else:
        out = run_git("diff", "--name-only", f"{base}...HEAD")
        if out is None:
            out = run_git("diff", "--name-only", base)
            if out is None:
                return None
        files |= {line.strip().replace("\\", "/") for line in out.splitlines()
                  if line.strip()}
    return files


def _smoke_import_paths(path: str) -> set[str]:
    """Проектные пути, которые смоук тянет своими импортами (ast, в т.ч. внутри функций).

    Возвращает относительные пути-кандидаты с '/': точные файлы модулей и их
    pkg-префиксы (bot/handlers/fire_event.py, utils/helpers.py, database/db.py…).
    'from pkg import name' добавляет и кандидата pkg/name (модуль), и самого pkg.
    """
    import ast

    def norm(mod: str) -> str:
        return mod.replace(".", "/")

    cands: set[str] = set()
    try:
        tree = ast.parse(open(path, encoding="utf-8", errors="replace").read())
    except SyntaxError:
        return cands
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                cands.add(norm(alias.name))
        elif isinstance(node, ast.ImportFrom) and node.module:
            base = norm(node.module)
            cands.add(base)
            for alias in node.names:
                if alias.name != "*":
                    cands.add(f"{base}/{alias.name}")
    # Оставляем только то, что реально существует в ROOT (файл или каталог).
    out: set[str] = set()
    for c in cands:
        if os.path.isfile(os.path.join(ROOT, c + ".py")):
            out.add(c + ".py")
        elif os.path.isfile(os.path.join(ROOT, c)):
            out.add(c)
        elif os.path.isdir(os.path.join(ROOT, c)):
            out.add(c + "/__init__.py")
    return out


def _walk_files_importing(fpath: str) -> set[str]:
    """Файлы пакета (__init__.py) держат wildcard-импорты; берём также вложенные модули."""
    deps: set[str] = set()
    aux = fpath
    while "/" in aux:
        aux = aux.rsplit("/", 1)[0]
        init = aux + "/__init__.py"
        if os.path.isfile(os.path.join(ROOT, init)):
            deps |= _smoke_import_paths(os.path.join(ROOT, init))
    return deps


def related_to_changes(smoke_path: str, changed: set[str]) -> bool:
    """Импортирует ли смоук хоть один изменённый файл (или сам изменён)."""
    smoke_rel = os.path.relpath(smoke_path, ROOT).replace("\\", "/")
    if smoke_rel in changed:
        return True
    touched = _smoke_import_paths(smoke_path)
    for p in list(touched):
        touched |= _walk_files_importing(p)
    if not touched:
        return False
    # Совпадение точное ИЛИ смоук импортирует пакет, а изменён его файл.
    for t in touched:
        t_norm = t
        if t_norm.endswith("/__init__.py"):
            t_norm = t_norm[:-len("/__init__.py")]
        for c in changed:
            if c == t_norm or c.startswith(t_norm + "/"):
                return True
    return False


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
    parser.add_argument(
        "--related",
        nargs="?",
        const="WORKING",
        default=None,
        help=("Запустить только смоуки, чьи импорты пересекаются с изменёнными "
              "файлами. Без значения — незакоммиченные изменения (git diff "
              "HEAD + untracked); со значением — изменения относительно git-базы "
              "(коммит/ветка/тег, напр. 'origin/main'). Изменения config.py или "
              "database/db.py тянут ВСЕТ смоуки. Каркас для быстрой проверки — "
              "перед деплоем всё равно гонять полный прогон."),
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
    if args.related:
        changed = collect_changed_files(args.related)
        if changed is None:
            print("Не удалось получить изменённые файлы через git.")
            return 1
        if not changed:
            print("Изменённых файлов нет — нечего прогонять по --related.")
            return 0
        if {"config.py", "database/db.py"} & changed:
            print("Изменены config.py или database/db.py — затронуты ВСЕ смоуки, "
                  "фильтр не используется.")
        else:
            smokes = [(n, p) for n, p in smokes
                      if related_to_changes(p, changed)]
        names = ", ".join(f"smoke_{n:03d}" for n, _ in smokes) or "—"
        print(f"После фильтра --related: {len(smokes)} шт. ({names})\n")

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
