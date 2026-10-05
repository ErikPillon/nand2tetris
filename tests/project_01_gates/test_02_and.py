"""Step 2: And."""

import pytest

from hardware import spec
from hardware.gates import and_, not_
from hardware.testkit import assert_budget, assert_truth_table, assert_uses_hardware, nands_used, tuples


def test_and_truth_table():
    assert_truth_table(and_, spec.ref_and, 2, "and_")


def test_and_is_commutative():
    for a, b in tuples(2):
        assert and_(a, b) == and_(b, a)


def test_and_is_associative():
    for a, b, c in tuples(3):
        assert and_(and_(a, b), c) == and_(a, and_(b, c))


def test_and_is_idempotent_and_has_identity_one():
    for a in (0, 1):
        assert and_(a, a) == a
        assert and_(a, 1) == a
        assert and_(a, 0) == 0


def test_and_relates_to_nand_by_negation():
    from hardware.primitives import nand
    for a, b in tuples(2):
        assert and_(a, b) == not_(nand(a, b))


def test_and_is_built_from_nand():
    for a, b in tuples(2):
        assert_uses_hardware(and_, a, b, name="and_")


def test_and_within_budget():
    assert_budget(and_, tuples(2), spec.LOOSE["and_"], "and_")


@pytest.mark.optimal
def test_and_is_minimal():
    worst = max(nands_used(and_, a, b) for a, b in tuples(2))
    assert worst == spec.PAR["and_"], f"{worst} NANDs; two are enough"
