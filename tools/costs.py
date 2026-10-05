#!/usr/bin/env python3
"""Where do your NANDs go? One line per chip: what it costs, par, budget.

Cost composes. A chip that is two NANDs over par taxes every chip built on
top of it, so when a budget test fails the culprit is often further down.
"""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from hardware import spec
from hardware.primitives import bus, from_bin
from hardware.testkit import nands_used

PROBES = {
    # project 1
    "not_": (0,), "and_": (1, 1), "or_": (1, 0), "xor": (1, 0),
    "mux": (1, 0, 1), "dmux": (1, 1),
    "not16": (bus(0xBEEF),), "and16": (bus(0xBEEF), bus(0x1234)),
    "or16": (bus(0xBEEF), bus(0x1234)), "mux16": (bus(0xBEEF), bus(0x1234), 1),
    "or8way": ((0, 1, 0, 1, 0, 1, 0, 1),),
    "mux4way16": (*[bus(v) for v in (1, 2, 3, 4)], from_bin("10")),
    "mux8way16": (*[bus(v) for v in range(8)], from_bin("101")),
    "dmux4way": (1, from_bin("10")), "dmux8way": (1, from_bin("101")),
    # project 2
    "half_adder": (1, 1), "full_adder": (1, 1, 1),
    "add16": (bus(0xBEEF), bus(0x1234)), "inc16": (bus(0xBEEF),),
    "alu": (bus(0xBEEF), bus(0x1234), 0, 1, 0, 0, 1, 1),
}

MODULES = ["hardware.gates", "hardware.alu"]


def resolve(name):
    import importlib
    for module in MODULES:
        try:
            fn = getattr(importlib.import_module(module), name, None)
        except Exception:
            continue
        if callable(fn):
            return fn
    return None


def main() -> int:
    print(f"\n  {'chip':<12} {'used':>6} {'par':>6} {'budget':>7}   note\n")
    total_over = 0
    for name, par in spec.PAR.items():
        fn = resolve(name)
        loose = spec.LOOSE[name]
        if fn is None:
            print(f"  {name:<12} {'-':>6} {par:>6} {loose:>7}   (no such chip)")
            continue
        try:
            used = nands_used(fn, *PROBES[name])
        except NotImplementedError:
            print(f"  {name:<12} {'-':>6} {par:>6} {loose:>7}   not built yet")
            continue
        except Exception as exc:
            print(f"  {name:<12} {'!':>6} {par:>6} {loose:>7}   raised {type(exc).__name__}: {exc}")
            continue
        if used > loose:
            note = f"OVER BUDGET by {used - loose}"
            total_over += 1
        elif used > par:
            note = f"{used - par} over par  ({used / par:.2f}x)"
        else:
            note = "at par"
        print(f"  {name:<12} {used:>6} {par:>6} {loose:>7}   {note}")
    print()
    if total_over:
        print("  A chip over budget is often paying for a cheaper chip it depends on.")
        print("  Fix the lowest-level offender first; the savings propagate upward.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
