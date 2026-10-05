"""Step 13: Mux8Way16."""

import pytest

from hardware import spec
from hardware.gates import mux8way16
from hardware.primitives import bus, from_bin
from hardware.testkit import assert_bus, assert_budget, nands_used, sample_words

INPUTS = tuple(bus(v) for v in (0x0000, 0x1111, 0x2222, 0x3333, 0x4444, 0x5555, 0x6666, 0x7777))
NAMES = "abcdefgh"
SELECTORS = [from_bin(f"{i:03b}") for i in range(8)]


def test_mux8way16_selector_mapping():
    for i, sel in enumerate(SELECTORS):
        assert_bus(mux8way16(*INPUTS, sel), INPUTS[i],
                   f"mux8way16 with sel={i:03b} should pick input {NAMES[i]}")


def test_mux8way16_matches_spec(rng):
    words = sample_words(rng, n=10)
    for shift in range(5):
        group = tuple(words[(shift + k) % len(words)] for k in range(8))
        for sel in SELECTORS:
            assert_bus(mux8way16(*group, sel), spec.ref_mux8way16(*group, sel), "mux8way16")


def test_mux8way16_ignores_the_seven_unselected_words(rng):
    chosen = from_bin("0110100101101001")
    for index, sel in enumerate(SELECTORS):
        for noise in sample_words(rng, n=4):
            group = [noise] * 8
            group[index] = chosen
            assert_bus(mux8way16(*group, sel), chosen,
                       f"mux8way16 leaked when selecting input {NAMES[index]}")


def test_mux8way16_within_budget():
    assert_budget(mux8way16, [(*INPUTS, sel) for sel in SELECTORS],
                  spec.LOOSE["mux8way16"], "mux8way16")


@pytest.mark.optimal
def test_mux8way16_is_minimal():
    worst = max(nands_used(mux8way16, *INPUTS, sel) for sel in SELECTORS)
    assert worst == spec.PAR["mux8way16"], (
        f"{worst} NANDs; two Mux4Way16s plus one Mux16 is 448"
    )
