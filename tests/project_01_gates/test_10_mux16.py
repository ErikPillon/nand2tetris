"""Step 10: Mux16 -- one selector steering a whole word."""

import pytest

from hardware import spec
from hardware.gates import mux16
from hardware.primitives import bus, from_bin
from hardware.testkit import assert_bus, assert_budget, nands_used, sample_words


def test_mux16_selects_the_right_word():
    a = from_bin("0001001000110100")
    b = from_bin("1001100001110110")
    assert_bus(mux16(a, b, 0), a, "mux16(a, b, sel=0)")
    assert_bus(mux16(a, b, 1), b, "mux16(a, b, sel=1)")


def test_mux16_matches_spec(rng):
    words = sample_words(rng, n=20)
    for x in words:
        for y in words[:10]:
            for sel in (0, 1):
                assert_bus(mux16(x, y, sel), spec.ref_mux16(x, y, sel), f"mux16(..., sel={sel})")


def test_mux16_ignores_the_unselected_word(rng):
    """With sel fixed, the other input must not reach any output wire."""
    chosen = from_bin("0110100101101001")
    for sel in (0, 1):
        for other in sample_words(rng, n=12):
            args = (chosen, other, sel) if sel == 0 else (other, chosen, sel)
            assert_bus(mux16(*args), chosen, f"mux16 leaked with sel={sel}")


def test_mux16_with_equal_inputs(rng):
    for x in sample_words(rng, n=12):
        for sel in (0, 1):
            assert mux16(x, x, sel) == x


def test_mux16_is_mux_applied_wire_by_wire(rng):
    from hardware.gates import mux
    for x in sample_words(rng, n=8):
        for y in sample_words(rng, n=4):
            for sel in (0, 1):
                expected = tuple(mux(p, q, sel) for p, q in zip(x, y))
                assert mux16(x, y, sel) == expected


def test_mux16_within_budget(rng):
    args = [(w, bus(0), s) for w in sample_words(rng, n=2) for s in (0, 1)]
    assert_budget(mux16, args, spec.LOOSE["mux16"], "mux16")


@pytest.mark.optimal
def test_mux16_is_minimal():
    assert nands_used(mux16, bus(0), bus(0), 0) == spec.PAR["mux16"]
