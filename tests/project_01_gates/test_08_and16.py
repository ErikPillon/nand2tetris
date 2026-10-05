"""Step 8: And16."""

import pytest

from hardware import spec
from hardware.gates import and16
from hardware.primitives import WORD, bus, from_bin
from hardware.testkit import assert_bus, assert_budget, nands_used, sample_words


def test_and16_on_known_words():
    cases = [
        ("0000000000000000", "0000000000000000", "0000000000000000"),
        ("0000000000000000", "1111111111111111", "0000000000000000"),
        ("1111111111111111", "1111111111111111", "1111111111111111"),
        ("1010101010101010", "0101010101010101", "0000000000000000"),
        ("0011110011000011", "0000111111110000", "0000110011000000"),
    ]
    for a, b, expected in cases:
        assert_bus(and16(from_bin(a), from_bin(b)), from_bin(expected), f"and16({a}, {b})")


def test_and16_matches_spec(rng):
    words = sample_words(rng, n=24)
    for x in words:
        for y in words[:12]:
            assert_bus(and16(x, y), spec.ref_and16(x, y), "and16")


def test_and16_wires_do_not_cross_talk():
    """out[i] may depend on a[i] and b[i] only."""
    for i in range(WORD):
        hot = bus(1 << i)
        assert and16(hot, hot)[i] == 1
        assert and16(hot, bus(~(1 << i)))[i] == 0
        assert and16(hot, bus(-1)) == hot


def test_and16_identities(rng):
    ones, zeros = bus(-1), bus(0)
    for x in sample_words(rng, n=16):
        assert and16(x, ones) == x
        assert and16(x, zeros) == zeros
        assert and16(x, x) == x


def test_and16_within_budget(rng):
    pairs = [(w, bus(0)) for w in sample_words(rng, n=3)]
    assert_budget(and16, pairs, spec.LOOSE["and16"], "and16")


@pytest.mark.optimal
def test_and16_is_minimal():
    assert nands_used(and16, bus(0), bus(0)) == spec.PAR["and16"]
