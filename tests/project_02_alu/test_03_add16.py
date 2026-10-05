"""Step 3: Add16 -- a ripple-carry adder, and the ring Z/2^16."""

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from hardware import spec
from hardware.alu import add16
from hardware.primitives import ONE, WORD, ZERO, bus, from_bin, to_bin, to_int
from hardware.testkit import assert_bus, assert_budget, nands_used, sample_words

MOD = 1 << WORD
MIN, MAX = -(1 << (WORD - 1)), (1 << (WORD - 1)) - 1
words = st.integers(min_value=MIN, max_value=MAX)


def test_add16_on_the_cases_from_the_book():
    cases = [
        ("0000000000000000", "0000000000000000", "0000000000000000"),
        ("0000000000000000", "1111111111111111", "1111111111111111"),
        ("1111111111111111", "1111111111111111", "1111111111111110"),
        ("1010101010101010", "0101010101010101", "1111111111111111"),
        ("0011110011000011", "0000111111110000", "0100110010110011"),
        ("0001001000110100", "1001100001110110", "1010101010101010"),
    ]
    for a, b, expected in cases:
        assert_bus(add16(from_bin(a), from_bin(b)), from_bin(expected), f"add16({a}, {b})")


def test_add16_small_positive_numbers():
    for a in range(0, 40, 7):
        for b in range(0, 40, 5):
            assert to_int(add16(bus(a), bus(b))) == a + b


def test_add16_zero_is_the_identity(rng):
    for word in sample_words(rng, n=20):
        assert_bus(add16(word, ZERO), word, "add16(x, 0)")
        assert_bus(add16(ZERO, word), word, "add16(0, x)")


def test_add16_is_commutative(rng):
    pool = sample_words(rng, n=16)
    for x in pool:
        for y in pool[:8]:
            assert add16(x, y) == add16(y, x)


def test_add16_is_associative(rng):
    pool = sample_words(rng, n=8)
    for x in pool:
        for y in pool[:4]:
            for z in pool[:3]:
                assert add16(add16(x, y), z) == add16(x, add16(y, z))


def test_every_word_has_an_additive_inverse(rng):
    """(Z/2^16, add16) is a group: the inverse of x is Not(x) + 1."""
    from hardware.gates import not16
    for x in sample_words(rng, n=24):
        minus_x = add16(not16(x), ONE)
        assert_bus(add16(x, minus_x), ZERO, f"x + (-x) for x = {to_bin(x)}")


def test_add16_wraps_instead_of_overflowing():
    """The carry out of wire 15 is discarded. This is the specification."""
    assert to_int(add16(bus(MAX), ONE)) == MIN, "32767 + 1 must wrap to -32768"
    assert to_int(add16(bus(MIN), bus(-1))) == MAX, "-32768 + -1 must wrap to 32767"
    assert to_int(add16(bus(-1), ONE)) == 0
    assert to_int(add16(bus(MAX), bus(MAX))) == -2


def test_add16_carry_propagates_the_whole_way():
    """The hardest case for a ripple-carry adder: a carry crossing all 16 columns."""
    assert_bus(add16(from_bin("0111111111111111"), ONE),
               from_bin("1000000000000000"), "carry across 15 columns")
    assert_bus(add16(from_bin("1111111111111111"), ONE), ZERO, "carry off the end")


def test_add16_each_single_bit_doubles():
    for i in range(WORD - 1):
        hot = bus(1 << i)
        assert to_int(add16(hot, hot)) == to_int(bus(1 << (i + 1)))


@settings(max_examples=400, deadline=None)
@given(words, words)
def test_add16_is_addition_mod_two_to_the_sixteen(a, b):
    assert_bus(add16(bus(a), bus(b)), bus(a + b), f"add16({a}, {b})")


@settings(max_examples=200, deadline=None)
@given(words, words)
def test_add16_agrees_with_the_specification(a, b):
    x, y = bus(a), bus(b)
    assert_bus(add16(x, y), spec.ref_add16(x, y), "add16")


def test_add16_within_budget(rng):
    pool = sample_words(rng, n=3)
    assert_budget(add16, [(x, y) for x in pool for y in pool[:2]], spec.LOOSE["add16"], "add16")


@pytest.mark.optimal
def test_add16_is_minimal(rng):
    worst = max(nands_used(add16, x, bus(-1)) for x in sample_words(rng, n=4))
    assert worst == spec.PAR["add16"], (
        f"{worst} NANDs; one HalfAdder (6) for wire 0 plus fifteen FullAdders "
        f"(15 x 15) is 231. Using a FullAdder for wire 0 wastes 9."
    )
