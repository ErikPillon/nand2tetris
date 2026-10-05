"""Step 3: Or. De Morgan's first appearance as a wiring diagram."""

import pytest

from hardware import spec
from hardware.gates import and_, not_, or_
from hardware.testkit import assert_budget, assert_truth_table, assert_uses_hardware, nands_used, tuples


def test_or_truth_table():
    assert_truth_table(or_, spec.ref_or, 2, "or_")


def test_or_is_commutative_and_associative():
    for a, b in tuples(2):
        assert or_(a, b) == or_(b, a)
    for a, b, c in tuples(3):
        assert or_(or_(a, b), c) == or_(a, or_(b, c))


def test_or_has_identity_zero_and_annihilator_one():
    for a in (0, 1):
        assert or_(a, 0) == a
        assert or_(a, 1) == 1


def test_de_morgan_holds_for_your_gates():
    for a, b in tuples(2):
        assert not_(or_(a, b)) == and_(not_(a), not_(b))
        assert not_(and_(a, b)) == or_(not_(a), not_(b))


def test_distributivity_holds_both_ways():
    """A Boolean algebra, unlike a ring, distributes in both directions."""
    for a, b, c in tuples(3):
        assert and_(a, or_(b, c)) == or_(and_(a, b), and_(a, c))
        assert or_(a, and_(b, c)) == and_(or_(a, b), or_(a, c))


def test_absorption():
    for a, b in tuples(2):
        assert or_(a, and_(a, b)) == a
        assert and_(a, or_(a, b)) == a


def test_or_is_built_from_nand():
    for a, b in tuples(2):
        assert_uses_hardware(or_, a, b, name="or_")


def test_or_within_budget():
    assert_budget(or_, tuples(2), spec.LOOSE["or_"], "or_")


@pytest.mark.optimal
def test_or_is_minimal():
    worst = max(nands_used(or_, a, b) for a, b in tuples(2))
    assert worst == spec.PAR["or_"], f"{worst} NANDs; three are enough"
