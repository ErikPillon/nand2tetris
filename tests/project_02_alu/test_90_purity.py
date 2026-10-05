"""Is `hardware/alu.py` hardware, and is it built from Project 1?"""

import ast
import pathlib

import pytest

from hardware import alu, spec
from hardware.testkit import lint_module

EXPECTED_CHIPS = ["half_adder", "full_adder", "add16", "inc16", "alu"]


@pytest.mark.parametrize("path", spec.IMPLEMENTATION_FILES)
def test_implementation_is_hardware_not_python(path):
    problems = lint_module(path)
    assert not problems, "\n" + "\n".join(problems)


def test_every_chip_still_exists_with_the_expected_name():
    missing = [name for name in EXPECTED_CHIPS if not callable(getattr(alu, name, None))]
    assert not missing, f"these chips are missing or no longer callable: {missing}"


def test_the_alu_module_builds_on_project_one_rather_than_on_nands():
    """A direct `nand(` call in alu.py means you reached past a chip you own."""
    tree = ast.parse(pathlib.Path("hardware/alu.py").read_text())
    offenders = [
        node.lineno
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "nand"
    ]
    assert not offenders, (
        f"hardware/alu.py calls nand() directly at line(s) {offenders}. "
        "Everything here is reachable from the Project 1 chips -- find the one you meant."
    )


def test_no_chip_is_wildly_over_budget():
    from hardware.primitives import bus
    from hardware.testkit import nands_used

    probes = {
        "half_adder": (1, 1),
        "full_adder": (1, 1, 1),
        "add16": (bus(0xBEEF), bus(0x1234)),
        "inc16": (bus(0xBEEF),),
        "alu": (bus(0xBEEF), bus(0x1234), 0, 1, 0, 0, 1, 1),
    }
    report = {name: nands_used(getattr(alu, name), *args) for name, args in probes.items()}
    over = {n: (c, spec.LOOSE[n]) for n, c in report.items() if c > spec.LOOSE[n]}
    assert not over, f"over budget (used, limit): {over}\nfull report: {report}"
