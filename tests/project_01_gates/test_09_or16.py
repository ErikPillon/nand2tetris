"""Step 9: Or16."""

import pytest

from hardware import spec
from hardware.gates import and16, not16, or16
from hardware.primitives import bus, from_bin
from hardware.testkit import assert_bus, assert_budget, nands_used, sample_words


def test_or16_on_known_words():
    cases = [
        ("0000000000000000", "0000000000000000", "0000000000000000"),
        ("0000000000000000", "1111111111111111", "1111111111111111"),
        ("1010101010101010", "0101010101010101", "1111111111111111"),
        ("0011110011000011", "0000111111110000", "0011111111110011"),
    ]
    for a, b, expected in cases:
        assert_bus(or16(from_bin(a), from_bin(b)), from_bin(expected), f"or16({a}, {b})")


def test_or16_matches_spec(rng):
    words = sample_words(rng, n=24)
    for x in words:
        for y in words[:12]:
            assert_bus(or16(x, y), spec.ref_or16(x, y), "or16")


def test_de_morgan_holds_word_wide(rng):
    for x in sample_words(rng, n=12):
        for y in sample_words(rng, n=6):
            assert not16(or16(x, y)) == and16(not16(x), not16(y))
            assert not16(and16(x, y)) == or16(not16(x), not16(y))


def test_or16_identities(rng):
    ones, zeros = bus(-1), bus(0)
    for x in sample_words(rng, n=16):
        assert or16(x, zeros) == x
        assert or16(x, ones) == ones
        assert or16(x, x) == x


def test_or16_within_budget(rng):
    pairs = [(w, bus(0)) for w in sample_words(rng, n=3)]
    assert_budget(or16, pairs, spec.LOOSE["or16"], "or16")


@pytest.mark.optimal
def test_or16_is_minimal():
    assert nands_used(or16, bus(0), bus(0)) == spec.PAR["or16"]
