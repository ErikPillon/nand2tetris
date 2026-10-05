"""Step 4: Inc16. Trivial to get right, interesting to get cheap."""

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from hardware import spec
from hardware.alu import add16, inc16
from hardware.primitives import ONE, WORD, ZERO, bus, from_bin, to_int
from hardware.testkit import assert_bus, assert_budget, nands_used, sample_words

MIN, MAX = -(1 << (WORD - 1)), (1 << (WORD - 1)) - 1


def test_inc16_on_known_words():
    cases = [
        ("0000000000000000", "0000000000000001"),
        ("0000000000000001", "0000000000000010"),
        ("0000000000000011", "0000000000000100"),
        ("0000000011111111", "0000000100000000"),
        ("0111111111111111", "1000000000000000"),
        ("1111111111111111", "0000000000000000"),
        ("1010101010101010", "1010101010101011"),
    ]
    for given_word, expected in cases:
        assert_bus(inc16(from_bin(given_word)), from_bin(expected), f"inc16({given_word})")


def test_inc16_agrees_with_add16_of_one(rng):
    for word in sample_words(rng, n=24):
        assert_bus(inc16(word), add16(word, ONE), "inc16 vs add16(x, 1)")


def test_inc16_wraps():
    assert to_int(inc16(bus(MAX))) == MIN
    assert to_int(inc16(bus(-1))) == 0


def test_inc16_applied_sixteen_times():
    word = ZERO
    for expected in range(1, 17):
        word = inc16(word)
        assert to_int(word) == expected


def test_inc16_is_a_bijection_on_the_cycle():
    """Incrementing 2^16 times returns you to where you started."""
    word = bus(1234)
    seen = set()
    for _ in range(300):
        word = inc16(word)
        seen.add(word)
    assert len(seen) == 300, "inc16 must not repeat a value within one lap"


@settings(max_examples=400, deadline=None)
@given(st.integers(min_value=MIN, max_value=MAX))
def test_inc16_adds_one_mod_two_to_the_sixteen(value):
    assert_bus(inc16(bus(value)), bus(value + 1), f"inc16({value})")


def test_inc16_within_budget(rng):
    assert_budget(inc16, [(w,) for w in sample_words(rng, n=4)], spec.LOOSE["inc16"], "inc16")


@pytest.mark.optimal
def test_inc16_is_minimal(rng):
    worst = max(nands_used(inc16, w) for w in sample_words(rng, n=4))
    assert worst == spec.PAR["inc16"], (
        f"{worst} NANDs. Adding 1 needs no second addend: sixteen HalfAdders "
        f"carrying into each other is 96. `add16(x, ONE)` costs 231."
    )
