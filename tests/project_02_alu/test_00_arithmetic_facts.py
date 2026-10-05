"""Sanity checks on two's complement itself. These pass before you write code.

If you are unsure what `add16` is supposed to do when it overflows, read this
file -- it is the specification, stated as arithmetic rather than as prose.
"""

import pytest

from hardware.primitives import ONE, WORD, ZERO, bus, to_bin, to_int

MOD = 1 << WORD
MIN, MAX = -(1 << (WORD - 1)), (1 << (WORD - 1)) - 1


def test_the_representable_range():
    assert (MIN, MAX) == (-32768, 32767)
    assert to_int(bus(MAX)) == MAX
    assert to_int(bus(MIN)) == MIN


def test_bus_is_a_ring_homomorphism_from_the_integers():
    """`bus` is reduction mod 2**16; that is the whole content of overflow."""
    for a in (0, 1, -1, 7, MAX, MIN, 12345, -12345):
        for b in (0, 1, -1, 3, MAX, MIN, 999):
            assert bus(a + b) == bus(to_int(bus(a)) + to_int(bus(b)))
            assert bus(a * b) == bus(to_int(bus(a)) * to_int(bus(b)))


def test_two_complement_negation_is_complement_plus_one():
    """-x == ~x + 1. This identity is why one adder can also subtract."""
    for value in (0, 1, -1, 7, MAX, MIN, 31415):
        complemented = ~value
        assert to_int(bus(complemented + 1)) == to_int(bus(-value))


def test_the_sign_bit_is_literally_wire_15():
    for value in (-1, MIN, -32767, -1234):
        assert bus(value)[WORD - 1] == 1
    for value in (0, 1, MAX, 1234):
        assert bus(value)[WORD - 1] == 0


def test_the_one_asymmetry_of_two_complement():
    """-MIN is not representable: negation is not a bijection on the range."""
    assert to_int(bus(-MIN)) == MIN
    assert to_bin(bus(MIN)) == "1000000000000000"


def test_the_constant_buses():
    assert to_int(ZERO) == 0
    assert to_int(ONE) == 1
    assert ONE[0] == 1 and sum(ONE) == 1
