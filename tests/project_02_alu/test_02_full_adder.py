"""Step 2: FullAdder -- one column of a long addition."""

import pytest

from hardware import spec
from hardware.alu import full_adder, half_adder
from hardware.testkit import assert_bit, assert_budget, nands_used, tuples


def test_full_adder_returns_a_pair_of_bits():
    for args in tuples(3):
        out = full_adder(*args)
        assert isinstance(out, tuple) and len(out) == 2, (
            f"full_adder{args} returned {out!r}; expected (sum, carry)"
        )
        assert_bit(out[0], f"full_adder{args}.sum")
        assert_bit(out[1], f"full_adder{args}.carry")


def test_full_adder_truth_table():
    for args in tuples(3):
        got, want = full_adder(*args), spec.ref_full_adder(*args)
        assert got == want, f"full_adder{args} = {got}, expected {want}"


def test_full_adder_computes_the_arithmetic_sum():
    for a, b, c in tuples(3):
        s, carry = full_adder(a, b, c)
        assert 2 * carry + s == a + b + c, (
            f"full_adder({a}, {b}, {c}) says {2 * carry + s}, not {a + b + c}"
        )


def test_full_adder_is_fully_symmetric():
    """It only counts how many inputs are 1, so every permutation agrees."""
    import itertools
    for args in tuples(3):
        for perm in itertools.permutations(args):
            assert full_adder(*perm) == full_adder(*args), (
                f"full_adder{args} != full_adder{perm}; a carry-in is not special"
            )


def test_full_adder_with_no_carry_in_is_a_half_adder():
    for a, b in tuples(2):
        assert full_adder(a, b, 0) == half_adder(a, b)


def test_full_adder_carry_is_the_majority_function():
    """carry = 1 iff at least two inputs are 1. Worth recognising by name."""
    for args in tuples(3):
        assert full_adder(*args)[1] == (1 if sum(args) >= 2 else 0)


def test_full_adder_sum_is_the_parity():
    for args in tuples(3):
        assert full_adder(*args)[0] == sum(args) % 2


def test_full_adder_within_budget():
    assert_budget(full_adder, tuples(3), spec.LOOSE["full_adder"], "full_adder")


@pytest.mark.optimal
def test_full_adder_is_minimal():
    worst = max(nands_used(full_adder, *args) for args in tuples(3))
    assert worst == spec.PAR["full_adder"], (
        f"{worst} NANDs; two HalfAdders (6 + 6) and an Or (3) is 15"
    )
