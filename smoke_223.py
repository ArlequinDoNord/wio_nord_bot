# -*- coding: utf-8 -*-
"""Smoke 223 — версия живёт в version.py, config реэкспортирует её.

Зачем: при бампе меняется только version.py, и `tools/run_smokes.py --related`
не тянет весь набор смоуков. Этот смоук подтверждает, что:
1. константы версии определены в version.py, а не в config.py;
2. config.py реэкспортирует их, поэтому `from config import VERSION` работает;
3. tools/release_bump.py правит version.py (а не config.py).

Прогон: .\\.venv\\Scripts\\python.exe smoke_223.py
"""
import importlib.util
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

passed = failed = 0


def check(name, cond):
    global passed, failed
    if cond:
        passed += 1
        print(f"  OK  {name}")
    else:
        failed += 1
        print(f"  FAIL: {name}")


def _read(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return f.read()


def main():
    print("\n1. Определение версии: version.py")
    version_src = _read("version.py")
    config_src = _read("config.py")
    for name in ("VERSION", "VERSION_NOTES", "PREV_VERSION", "PREV_VERSION_NOTES"):
        check(f"version.py определяет {name}",
              re.search(rf"^{name}\s*=", version_src, re.M) is not None)
        check(f"config.py не определяет {name} сам",
              re.search(rf"^{name}\s*=", config_src, re.M) is None)
    check("config.py импортирует версию из version",
          re.search(r"^from version import .*VERSION", config_src, re.M) is not None)

    print("\n2. Реэкспорт: config и version отдают одно и то же")
    import config
    import version
    check("VERSION совпадает", config.VERSION == version.VERSION)
    check("VERSION_NOTES совпадает", config.VERSION_NOTES == version.VERSION_NOTES)
    check("PREV_VERSION совпадает", config.PREV_VERSION == version.PREV_VERSION)
    check("PREV_VERSION_NOTES совпадает", config.PREV_VERSION_NOTES == version.PREV_VERSION_NOTES)
    check("VERSION в формате SemVer",
          re.fullmatch(r"\d+\.\d+\.\d+", version.VERSION) is not None)
    check("VERSION_NOTES заполнены", bool(version.VERSION_NOTES.strip()))
    check("заметки не простыня (<= 400 символов)", len(version.VERSION_NOTES) <= 400)
    from bot.handlers.start import _version_teaser
    check("тизер /start не длиннее 121 символа",
          len(_version_teaser(version.VERSION_NOTES)) <= 121)

    print("\n3. tools/release_bump.py правит version.py")
    spec = importlib.util.spec_from_file_location(
        "release_bump", os.path.join(ROOT, "tools", "release_bump.py"))
    rb = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rb)
    check("VERSION_FILE указывает на version.py",
          rb.VERSION_FILE.name == "version.py")
    check("config.py больше не цель бампа", not hasattr(rb, "CONFIG"))
    sample = 'VERSION = "1.2.3"\nPREV_VERSION = "1.2.2"\nVERSION_NOTES = ("старое")\n' \
             'PREV_VERSION_NOTES = ("ещё старее")\n'
    updated = rb.update_config(sample, "1.2.4", "новое", "1.2.3", "старое")
    check("update_config меняет VERSION",
          'VERSION = "1.2.4"' in updated)
    check("update_config сдвигает PREV_VERSION",
          'PREV_VERSION = "1.2.3"' in updated)
    check("extract_config_vars читает текущую версию из version.py",
          rb.extract_config_vars(version_src)[0] == version.VERSION)

    print(f"\nИТОГО: {passed} passed, {failed} failed")
    return failed


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
