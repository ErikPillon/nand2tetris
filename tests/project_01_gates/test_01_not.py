"""Step 1: Not. The whole project turns on this one line of wiring."""

import pytest

from hardware import spec
from hardware.gates import not_
from hardware.testkit import assert_budget, assert_truth_table, assert_uses_hardware, nands_used, tuples


def test_not_truth_table():
    assert_truth_table(not_, spec.ref_not, 1, "not_")


def test_not_is_an_involution():
    """Two inversions cancel: a well-known fact that catches sign errors."""
    for a in (0, 1):
        assert not_(not_(a)) == a


def test_not_is_built_from_nand():
    assert_uses_hardware(not_, 0, name="not_")
    assert_uses_hardware(not_, 1, name="not_")


def test_not_within_budget():
    assert_budget(not_, tuples(1), spec.LOOSE["not_"], "not_")


@pytest.mark.optimal
def test_not_is_minimal():
    worst = max(nands_used(not_, a) for a in (0, 1))
    assert worst == spec.PAR["not_"], f"{worst} NANDs; one is enough"
