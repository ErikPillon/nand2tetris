"""Step 12: Mux4Way16. The selector convention bites here -- read the docstring."""

import pytest

from hardware import spec
from hardware.gates import mux4way16
from hardware.primitives import bus, from_bin
from hardware.testkit import assert_bus, assert_budget, nands_used, sample_words

A = from_bin("0001001000110100")
B = from_bin("1001100001110110")
C = from_bin("1010101010101010")
D = from_bin("0101010101010101")
INPUTS = (A, B, C, D)
NAMES = "abcd"


def test_mux4way16_selector_mapping():
    """Written binary 'sel1 sel0' -> which input. This is the classic bug."""
    expected = {"00": A, "01": B, "10": C, "11": D}
    for written, want in expected.items():
        sel = from_bin(written)          # LSB-first tuple
        assert_bus(mux4way16(*INPUTS, sel), want,
                   f"mux4way16 with sel={written} (sel[0]={sel[0]}, sel[1]={sel[1]})")


def test_mux4way16_matches_spec(rng):
    words = sample_words(rng, n=8)
    for shift in range(4):
        group = tuple(words[(shift + k) % len(words)] for k in range(4))
        for s0 in (0, 1):
            for s1 in (0, 1):
                sel = (s0, s1)
                assert_bus(mux4way16(*group, sel), spec.ref_mux4way16(*group, sel),
                           f"mux4way16(sel=({s0},{s1}))")


def test_mux4way16_ignores_the_three_unselected_words(rng):
    chosen = from_bin("0110100101101001")
    for index, sel in enumerate([(0, 0), (1, 0), (0, 1), (1, 1)]):
        for noise in sample_words(rng, n=6):
            group = [noise] * 4
            group[index] = chosen
            assert_bus(mux4way16(*group, sel), chosen,
                       f"mux4way16 leaked when selecting input {NAMES[index]}")


def test_mux4way16_with_all_inputs_equal(rng):
    for x in sample_words(rng, n=6):
        for sel in [(0, 0), (1, 0), (0, 1), (1, 1)]:
            assert mux4way16(x, x, x, x, sel) == x


def test_mux4way16_within_budget():
    args = [(*INPUTS, (s0, s1)) for s0 in (0, 1) for s1 in (0, 1)]
    assert_budget(mux4way16, args, spec.LOOSE["mux4way16"], "mux4way16")


@pytest.mark.optimal
def test_mux4way16_is_minimal():
    worst = max(nands_used(mux4way16, *INPUTS, (s0, s1)) for s0 in (0, 1) for s1 in (0, 1))
    assert worst == spec.PAR["mux4way16"], (
        f"{worst} NANDs; three Mux16s in a tree is 192 -- do not rebuild Mux from scratch"
    )
