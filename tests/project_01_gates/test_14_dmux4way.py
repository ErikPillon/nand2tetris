"""Step 14: DMux4Way -- the address decoder in miniature."""

import pytest

from hardware import spec
from hardware.gates import dmux4way
from hardware.primitives import from_bin
from hardware.testkit import assert_bit, assert_budget, nands_used

SELECTORS = [from_bin(f"{i:02b}") for i in range(4)]
NAMES = "abcd"


def test_dmux4way_returns_four_bits():
    for x in (0, 1):
        for sel in SELECTORS:
            out = dmux4way(x, sel)
            assert isinstance(out, tuple) and len(out) == 4, (
                f"dmux4way({x}, {sel}) returned {out!r}; expected a 4-tuple"
            )
            for i, bit in enumerate(out):
                assert_bit(bit, f"dmux4way({x}, {sel})[{i}]")


def test_dmux4way_is_exhaustively_correct():
    for x in (0, 1):
        for sel in SELECTORS:
            got = dmux4way(x, sel)
            want = spec.ref_dmux4way(x, sel)
            assert got == want, f"dmux4way({x}, {sel}) = {got}, expected {want}"


def test_dmux4way_drives_at_most_one_output():
    for x in (0, 1):
        for sel in SELECTORS:
            assert sum(dmux4way(x, sel)) <= 1


def test_dmux4way_routes_to_the_address_named_by_sel():
    for i, sel in enumerate(SELECTORS):
        out = dmux4way(1, sel)
        assert out[i] == 1, f"sel={i:02b} should drive output {NAMES[i]}, got {out}"
        assert sum(out) == 1


def test_dmux4way_is_silent_on_a_zero_input():
    for sel in SELECTORS:
        assert dmux4way(0, sel) == (0, 0, 0, 0)


def test_dmux4way_round_trips_through_mux4way16(rng):
    """Route a word's worth of bits out and gather them back."""
    from hardware.gates import mux4way16
    from hardware.primitives import bus
    for sel in SELECTORS:
        word = bus(rng.getrandbits(16))
        lanes = [[0] * 16 for _ in range(4)]
        for i, bit in enumerate(word):
            for lane, value in enumerate(dmux4way(bit, sel)):
                lanes[lane][i] = value
        gathered = mux4way16(*[tuple(lane) for lane in lanes], sel)
        assert gathered == word


def test_dmux4way_within_budget():
    args = [(x, sel) for x in (0, 1) for sel in SELECTORS]
    assert_budget(dmux4way, args, spec.LOOSE["dmux4way"], "dmux4way")


@pytest.mark.optimal
def test_dmux4way_is_minimal():
    worst = max(nands_used(dmux4way, x, sel) for x in (0, 1) for sel in SELECTORS)
    assert worst == spec.PAR["dmux4way"], f"{worst} NANDs; three DMuxes is 15"
