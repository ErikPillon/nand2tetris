"""Step 5: Mux -- `if` made out of matter."""

import pytest

from hardware import spec
from hardware.gates import and_, mux, not_, or_
from hardware.testkit import assert_budget, assert_truth_table, assert_uses_hardware, nands_used, tuples


def test_mux_truth_table():
    assert_truth_table(mux, spec.ref_mux, 3, "mux")


def test_mux_ignores_the_unselected_input():
    """Changing the input that is not selected must not change the output."""
    for sel in (0, 1):
        for chosen in (0, 1):
            outs = set()
            for other in (0, 1):
                args = (chosen, other) if sel == 0 else (other, chosen)
                outs.add(mux(*args, sel))
            assert outs == {chosen}, (
                f"with sel={sel} the output leaked from the unselected input"
            )


def test_mux_with_identical_inputs_is_that_input():
    for a in (0, 1):
        for sel in (0, 1):
            assert mux(a, a, sel) == a


def test_mux_equals_the_canonical_formula():
    for a, b, sel in tuples(3):
        assert mux(a, b, sel) == or_(and_(a, not_(sel)), and_(b, sel))


def test_mux_can_impersonate_your_other_gates():
    """Mux is 'universal enough' on its own: wire constants into it."""
    for a, b in tuples(2):
        assert mux(0, b, a) == and_(a, b)
        assert mux(b, 1, a) == or_(a, b)
        assert mux(b, not_(b), a) == (a ^ b)
    for a in (0, 1):
        assert mux(1, 0, a) == not_(a)


def test_mux_is_built_from_nand():
    for args in tuples(3):
        assert_uses_hardware(mux, *args, name="mux")


def test_mux_within_budget():
    assert_budget(mux, tuples(3), spec.LOOSE["mux"], "mux")


@pytest.mark.optimal
def test_mux_is_minimal():
    worst = max(nands_used(mux, *args) for args in tuples(3))
    assert worst == spec.PAR["mux"], f"{worst} NANDs; four suffice"
