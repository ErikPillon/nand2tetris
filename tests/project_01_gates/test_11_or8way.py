"""Step 11: Or8Way -- 'is this bus nonzero?'. An 8-wire bus, not 16."""

import itertools

import pytest

from hardware import spec
from hardware.gates import or8way
from hardware.testkit import assert_bit, assert_budget, nands_used


def all_8bit_buses():
    return [tuple(t) for t in itertools.product((0, 1), repeat=8)]


def test_or8way_is_exhaustively_correct():
    """256 inputs: small enough to check every single one."""
    for x in all_8bit_buses():
        got = or8way(x)
        assert_bit(got, f"or8way({x})")
        assert got == spec.ref_or8way(x), f"or8way({x}) = {got}, expected {spec.ref_or8way(x)}"


def test_or8way_is_zero_only_on_the_zero_bus():
    zeros = [x for x in all_8bit_buses() if or8way(x) == 0]
    assert zeros == [(0,) * 8], f"these buses wrongly read as zero: {zeros[:5]}"


def test_or8way_sees_every_wire():
    """A single hot wire anywhere must raise the output."""
    for i in range(8):
        hot = tuple(1 if j == i else 0 for j in range(8))
        assert or8way(hot) == 1, f"wire {i} is not connected"


def test_or8way_is_monotone():
    """Turning a wire on can never turn the output off."""
    for x in all_8bit_buses():
        for i in range(8):
            if x[i] == 0:
                y = x[:i] + (1,) + x[i + 1:]
                assert or8way(y) >= or8way(x)


def test_or8way_within_budget():
    assert_budget(or8way, [(x,) for x in all_8bit_buses()[:8]], spec.LOOSE["or8way"], "or8way")


@pytest.mark.optimal
def test_or8way_is_minimal():
    worst = max(nands_used(or8way, x) for x in all_8bit_buses())
    assert worst == spec.PAR["or8way"], f"{worst} NANDs; seven Or gates is 21"
