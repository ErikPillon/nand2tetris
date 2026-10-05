"""Step 1: HalfAdder. Two output pins, and you already own both chips."""

import pytest

from hardware import spec
from hardware.alu import half_adder
from hardware.testkit import assert_bit, assert_budget, nands_used, tuples


def test_half_adder_returns_a_pair_of_bits():
    for a, b in tuples(2):
        out = half_adder(a, b)
        assert isinstance(out, tuple) and len(out) == 2, (
            f"half_adder({a}, {b}) returned {out!r}; expected (sum, carry)"
        )
        assert_bit(out[0], f"half_adder({a}, {b}).sum")
        assert_bit(out[1], f"half_adder({a}, {b}).carry")


def test_half_adder_truth_table():
    for a, b in tuples(2):
        got, want = half_adder(a, b), spec.ref_half_adder(a, b)
        assert got == want, f"half_adder({a}, {b}) = {got}, expected (sum, carry) = {want}"


def test_half_adder_computes_the_arithmetic_sum():
    """The two output wires, read as a 2-bit numeral, must equal a + b."""
    for a, b in tuples(2):
        s, carry = half_adder(a, b)
        assert 2 * carry + s == a + b, f"half_adder({a}, {b}) says {2 * carry + s}, not {a + b}"


def test_half_adder_is_symmetric():
    for a, b in tuples(2):
        assert half_adder(a, b) == half_adder(b, a)


def test_half_adder_sum_is_xor_and_carry_is_and():
    """The point of the chip, stated as the identity it is."""
    from hardware.gates import and_, xor
    for a, b in tuples(2):
        assert half_adder(a, b) == (xor(a, b), and_(a, b))


def test_half_adder_within_budget():
    assert_budget(half_adder, tuples(2), spec.LOOSE["half_adder"], "half_adder")


@pytest.mark.optimal
def test_half_adder_is_minimal():
    worst = max(nands_used(half_adder, a, b) for a, b in tuples(2))
    assert worst == spec.PAR["half_adder"], (
        f"{worst} NANDs. Xor costs 4 and And costs 2, so 6 is par. "
        "(5 is reachable by sharing a NAND between them -- but that means "
        "leaving the abstraction, which is not the lesson here.)"
    )
