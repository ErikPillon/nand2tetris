"""Step 15: DMux8Way -- this chip will choose which RAM register gets written."""

import pytest

from hardware import spec
from hardware.gates import dmux8way
from hardware.primitives import from_bin
from hardware.testkit import assert_bit, assert_budget, nands_used

SELECTORS = [from_bin(f"{i:03b}") for i in range(8)]
NAMES = "abcdefgh"


def test_dmux8way_returns_eight_bits():
    for x in (0, 1):
        for sel in SELECTORS:
            out = dmux8way(x, sel)
            assert isinstance(out, tuple) and len(out) == 8, (
                f"dmux8way({x}, {sel}) returned {out!r}; expected an 8-tuple"
            )
            for i, bit in enumerate(out):
                assert_bit(bit, f"dmux8way({x}, {sel})[{i}]")


def test_dmux8way_is_exhaustively_correct():
    for x in (0, 1):
        for sel in SELECTORS:
            got = dmux8way(x, sel)
            want = spec.ref_dmux8way(x, sel)
            assert got == want, f"dmux8way({x}, {sel}) = {got}, expected {want}"


def test_dmux8way_is_a_one_hot_decoder():
    seen = set()
    for i, sel in enumerate(SELECTORS):
        out = dmux8way(1, sel)
        assert sum(out) == 1, f"sel={i:03b} drove {sum(out)} outputs: {out}"
        assert out[i] == 1, f"sel={i:03b} should drive output {NAMES[i]}, got {out}"
        seen.add(out.index(1))
    assert seen == set(range(8)), "the eight selectors must reach eight distinct outputs"


def test_dmux8way_is_silent_on_a_zero_input():
    for sel in SELECTORS:
        assert dmux8way(0, sel) == (0,) * 8


def test_dmux8way_agrees_with_dmux4way_on_the_low_half():
    """sel[2] = 0 selects outputs a..d, which must behave exactly as DMux4Way."""
    from hardware.gates import dmux4way
    for x in (0, 1):
        for low in range(4):
            sel4 = from_bin(f"{low:02b}")
            sel8 = sel4 + (0,)
            assert dmux8way(x, sel8)[:4] == dmux4way(x, sel4)
            assert dmux8way(x, sel8)[4:] == (0, 0, 0, 0)


def test_dmux8way_within_budget():
    args = [(x, sel) for x in (0, 1) for sel in SELECTORS]
    assert_budget(dmux8way, args, spec.LOOSE["dmux8way"], "dmux8way")


@pytest.mark.optimal
def test_dmux8way_is_minimal():
    worst = max(nands_used(dmux8way, x, sel) for x in (0, 1) for sel in SELECTORS)
    assert worst == spec.PAR["dmux8way"], f"{worst} NANDs; seven DMuxes is 35"
