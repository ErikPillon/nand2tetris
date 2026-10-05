"""Step 4: Xor -- addition modulo 2, and the heart of the adder you build next."""

import pytest

from hardware import spec
from hardware.gates import and_, not_, or_, xor
from hardware.testkit import assert_budget, assert_truth_table, assert_uses_hardware, nands_used, tuples


def test_xor_truth_table():
    assert_truth_table(xor, spec.ref_xor, 2, "xor")


def test_xor_is_addition_mod_two():
    for a, b in tuples(2):
        assert xor(a, b) == (a + b) % 2


def test_xor_makes_the_bits_an_abelian_group():
    """Identity 0, every element its own inverse, associative, commutative."""
    for a in (0, 1):
        assert xor(a, 0) == a
        assert xor(a, a) == 0
    for a, b in tuples(2):
        assert xor(a, b) == xor(b, a)
    for a, b, c in tuples(3):
        assert xor(xor(a, b), c) == xor(a, xor(b, c))


def test_and_distributes_over_xor():
    """So ({0,1}, xor, and_) is the field F_2 -- your gates are its operations."""
    for a, b, c in tuples(3):
        assert and_(a, xor(b, c)) == xor(and_(a, b), and_(a, c))


def test_xor_equals_the_canonical_formula():
    for a, b in tuples(2):
        assert xor(a, b) == or_(and_(a, not_(b)), and_(not_(a), b))


def test_xor_is_built_from_nand():
    for a, b in tuples(2):
        assert_uses_hardware(xor, a, b, name="xor")


def test_xor_within_budget():
    assert_budget(xor, tuples(2), spec.LOOSE["xor"], "xor")


@pytest.mark.optimal
def test_xor_is_minimal():
    worst = max(nands_used(xor, a, b) for a, b in tuples(2))
    assert worst == spec.PAR["xor"], (
        f"{worst} NANDs. Four suffice: compute t = nand(a, b) once and reuse it."
    )
