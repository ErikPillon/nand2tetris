"""The payoff: your gates really are a complete basis for Boolean logic.

These tests do not introduce new chips. They check that the chips you built
compose into *every* Boolean function -- which is the reason a computer can
exist at all. Run them once everything above is green.
"""

import itertools

import pytest

from hardware.gates import and_, dmux, mux, not_, or_, xor
from hardware.testkit import tuples

ALL_2ARY_FUNCTIONS = list(itertools.product((0, 1), repeat=4))  # 16 truth tables


def literal(value: int, polarity: int) -> int:
    """Return the variable itself, or its negation, using only your gates."""
    return mux(not_(value), value, polarity)


def dnf(table, a: int, b: int) -> int:
    """Evaluate the disjunctive normal form of `table` using only your gates.

    `table[k]` is the output for input (a, b) read as the 2-bit number 2a + b.
    Every Boolean function equals the OR of the minterms where it is 1 --
    so if your And/Or/Not are correct, this reproduces all 16 functions.
    """
    out = 0
    for k, value in enumerate(table):
        minterm_a, minterm_b = (k >> 1) & 1, k & 1
        term = and_(literal(a, minterm_a), literal(b, minterm_b))
        out = or_(out, and_(term, value))
    return out


def test_your_gates_realise_all_sixteen_binary_functions():
    """2^(2^2) = 16 functions of two variables; none may be out of reach."""
    realised = set()
    for table in ALL_2ARY_FUNCTIONS:
        produced = tuple(dnf(table, a, b) for a, b in tuples(2))
        assert produced == table, (
            f"DNF of {table} evaluated to {produced}; one of and_/or_/not_/mux is wrong"
        )
        realised.add(produced)
    assert len(realised) == 16


def test_shannon_expansion_is_exactly_what_mux_does():
    """f(a, b) = Mux(f(a, 0), f(a, 1), b). Hardware's version of case analysis."""
    for table in ALL_2ARY_FUNCTIONS:
        f = lambda a, b: dnf(table, a, b)
        for a, b in tuples(2):
            assert f(a, b) == mux(f(a, 0), f(a, 1), b)


def test_nand_alone_is_functionally_complete():
    """Rebuild the basis from NAND and confirm it is the same basis you built."""
    from hardware.primitives import nand
    for a in (0, 1):
        assert not_(a) == nand(a, a)
    for a, b in tuples(2):
        assert and_(a, b) == nand(nand(a, b), nand(a, b))
        assert or_(a, b) == nand(nand(a, a), nand(b, b))


def test_xor_is_not_monotone_but_and_or_are():
    """Why {And, Or} alone cannot be complete: everything built from them is
    monotone, and Xor is not. This is the lemma behind needing Not (or Nand)."""
    def monotone(f, arity):
        for args in tuples(arity):
            for i in range(arity):
                if args[i] == 0:
                    bigger = args[:i] + (1,) + args[i + 1:]
                    if f(*bigger) < f(*args):
                        return False
        return True

    assert monotone(and_, 2)
    assert monotone(or_, 2)
    assert not monotone(xor, 2)
    assert not monotone(not_, 1)


def test_mux_and_dmux_are_mutually_inverse_on_every_input():
    for x, sel in tuples(2):
        assert mux(*dmux(x, sel), sel) == x
