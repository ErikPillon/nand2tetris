"""Is what you wrote actually hardware?

The linter reads `hardware/gates.py` as a syntax tree and rejects anything
that computes a bit by means other than composing gates: `if`, `and`, `or`,
`not`, comparisons, arithmetic, bitwise operators, imports of the answer key.

Loops, comprehensions, `zip`, `enumerate`, indexing, tuple and list building
are allowed -- they describe repeated wiring, exactly like an HDL `for`.
"""

import pytest

from hardware import gates, spec
from hardware.testkit import lint_module

EXPECTED_CHIPS = [
    "not_", "and_", "or_", "xor", "mux", "dmux",
    "not16", "and16", "or16", "mux16",
    "or8way", "mux4way16", "mux8way16", "dmux4way", "dmux8way",
]


@pytest.mark.parametrize("path", spec.IMPLEMENTATION_FILES)
def test_implementation_is_hardware_not_python(path):
    problems = lint_module(path)
    assert not problems, "\n" + "\n".join(problems)


def test_every_chip_still_exists_with_the_expected_name():
    missing = [name for name in EXPECTED_CHIPS if not callable(getattr(gates, name, None))]
    assert not missing, f"these chips are missing or no longer callable: {missing}"


def test_no_chip_is_wildly_over_budget():
    """A whole-project backstop: nothing should be an order of magnitude off."""
    from hardware.primitives import bus, from_bin
    from hardware.testkit import nands_used

    probes = {
        "not_": (0,), "and_": (1, 1), "or_": (1, 0), "xor": (1, 0),
        "mux": (1, 0, 1), "dmux": (1, 1),
        "not16": (bus(0xBEEF),), "and16": (bus(0xBEEF), bus(0x1234)),
        "or16": (bus(0xBEEF), bus(0x1234)), "mux16": (bus(0xBEEF), bus(0x1234), 1),
        "or8way": ((0, 1, 0, 1, 0, 1, 0, 1),),
        "mux4way16": (*[bus(v) for v in (1, 2, 3, 4)], from_bin("10")),
        "mux8way16": (*[bus(v) for v in range(8)], from_bin("101")),
        "dmux4way": (1, from_bin("10")),
        "dmux8way": (1, from_bin("101")),
    }
    report = {}
    for name, args in probes.items():
        report[name] = nands_used(getattr(gates, name), *args)
    over = {n: (c, spec.LOOSE[n]) for n, c in report.items() if c > spec.LOOSE[n]}
    assert not over, f"over budget (used, limit): {over}\nfull report: {report}"
