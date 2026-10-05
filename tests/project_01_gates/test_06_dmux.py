"""Step 6: DMux -- routing. One input, one of several destinations."""

import pytest

from hardware import spec
from hardware.gates import dmux
from hardware.testkit import assert_bit, assert_budget, assert_uses_hardware, nands_used, tuples


def test_dmux_returns_a_pair_of_bits():
    for x, sel in tuples(2):
        out = dmux(x, sel)
        assert isinstance(out, tuple) and len(out) == 2, (
            f"dmux({x}, {sel}) returned {out!r}; expected a 2-tuple (a, b)"
        )
        assert_bit(out[0], f"dmux({x}, {sel}).a")
        assert_bit(out[1], f"dmux({x}, {sel}).b")


def test_dmux_truth_table():
    for x, sel in tuples(2):
        assert dmux(x, sel) == spec.ref_dmux(x, sel), (
            f"dmux({x}, {sel}) = {dmux(x, sel)}, specification says {spec.ref_dmux(x, sel)}"
        )


def test_dmux_never_lights_both_outputs():
    for x, sel in tuples(2):
        a, b = dmux(x, sel)
        assert (a, b) != (1, 1), "a demultiplexor drives exactly one path"


def test_dmux_is_the_left_inverse_of_mux():
    """Route then select: you get your signal back."""
    from hardware.gates import mux
    for x, sel in tuples(2):
        a, b = dmux(x, sel)
        assert mux(a, b, sel) == x


def test_dmux_is_built_from_nand():
    for args in tuples(2):
        assert_uses_hardware(dmux, *args, name="dmux")


def test_dmux_within_budget():
    assert_budget(dmux, tuples(2), spec.LOOSE["dmux"], "dmux")


@pytest.mark.optimal
def test_dmux_is_minimal():
    worst = max(nands_used(dmux, *args) for args in tuples(2))
    assert worst == spec.PAR["dmux"], f"{worst} NANDs; five suffice (share the inverted selector)"
