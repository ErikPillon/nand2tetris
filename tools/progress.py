#!/usr/bin/env python3
"""Where am I? Runs each project's suite and prints a scoreboard."""

from __future__ import annotations

import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PY = ROOT / ".venv" / "bin" / "python"

PROJECTS = [
    ("project_01_gates", "1  Boolean logic -- elementary gates"),
    ("project_02_alu", "2  Boolean arithmetic -- adders and the ALU"),
    ("project_03_memory", "3  Sequential logic -- registers, RAM, counter"),
    ("project_04_asm", "4  Machine language -- writing Hack assembly"),
    ("project_05_computer", "5  Computer architecture -- CPU and Computer"),
    ("project_06_assembler", "6  Assembler"),
    ("project_07_vm_stack", "7  VM I -- stack arithmetic"),
    ("project_08_vm_control", "8  VM II -- program control"),
    ("project_09_jack", "9  Jack -- a program of your own"),
    ("project_10_parser", "10 Compiler I -- syntax analysis"),
    ("project_11_codegen", "11 Compiler II -- code generation"),
    ("project_12_os", "12 Operating system"),
]

COUNTS = re.compile(r"(\d+) (passed|failed|error|skipped|xfailed)")


def run(path: pathlib.Path, extra: list[str]) -> tuple[int, int, int]:
    proc = subprocess.run(
        [str(PY), "-m", "pytest", str(path), "--no-header", "-p", "no:cacheprovider", *extra],
        cwd=ROOT, capture_output=True, text=True,
    )
    tally = {kind: int(n) for n, kind in COUNTS.findall(proc.stdout)}
    return tally.get("passed", 0), tally.get("failed", 0) + tally.get("error", 0), tally.get("skipped", 0)


def bar(passed: int, failed: int, width: int = 24) -> str:
    total = passed + failed
    if total == 0:
        return "-" * width
    filled = round(width * passed / total)
    return "#" * filled + "." * (width - filled)


def main() -> int:
    print(f"\n  nand2tetris progress   ({ROOT})\n")
    unfinished = None
    for folder, title in PROJECTS:
        path = ROOT / "tests" / folder
        if not path.exists():
            print(f"   .    {title:<44} not started")
            continue
        passed, failed, _ = run(path, [])
        if passed + failed == 0:
            print(f"   ?    {title:<44} no tests collected")
            continue
        opt_passed, opt_failed, _ = run(path, ["-m", "optimal"])
        mark = "ok " if failed == 0 else "    "
        gold = " *gold*" if failed == 0 and opt_failed == 0 and opt_passed else ""
        print(f"  {mark}  {title:<44} [{bar(passed, failed)}] {passed}/{passed + failed}{gold}")
        if failed and unfinished is None:
            unfinished = folder
    print()
    if unfinished:
        print(f"  next:  ./scripts/n2t next        (first failing test in {unfinished})")
    else:
        print("  everything green. Ask for the next lesson.")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
