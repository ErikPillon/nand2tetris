"""Step 5: the ALU. The single most important chip in the machine.

Six control bits, 64 combinations, 18 of which the Hack instruction set names.
These tests check all 64 against the specification, not just the famous 18.
"""

import itertools

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from hardware import spec
from hardware.alu import alu
from hardware.primitives import WORD, bus, to_bin, to_int
from hardware.testkit import assert_bit, assert_bus, assert_budget, nands_used

MIN, MAX = -(1 << (WORD - 1)), (1 << (WORD - 1)) - 1
words = st.integers(min_value=MIN, max_value=MAX)

ALL_CONTROLS = list(itertools.product((0, 1), repeat=6))
PROBE_VALUES = [0, 1, -1, 2, -2, 7, -7, 17, MAX, MIN, 1234, -4321, 0x5555, -0x5556]


def call(xv, yv, ctrl):
    return alu(bus(xv), bus(yv), *ctrl)


def test_alu_returns_a_bus_and_two_flags():
    out, zr, ng = call(0, 0, spec.ALU_FUNCTIONS["x+y"])
    assert isinstance(out, tuple) and len(out) == WORD, (
        f"alu returned out = {out!r}; expected a 16-wire bus"
    )
    assert_bit(zr, "alu zr")
    assert_bit(ng, "alu ng")


@pytest.mark.parametrize("name", list(spec.ALU_FUNCTIONS))
def test_alu_computes_each_of_the_eighteen_named_functions(name):
    """The table the Hack instruction set is built out of."""
    ctrl = spec.ALU_FUNCTIONS[name]
    meaning = spec.ALU_MEANING[name]
    for xv in PROBE_VALUES:
        for yv in PROBE_VALUES:
            out, _, _ = call(xv, yv, ctrl)
            want = bus(meaning(xv, yv))
            assert_bus(out, want, (
                f"alu computing {name!r} with zx,nx,zy,ny,f,no = {ctrl}\n"
                f"  x = {xv} ({to_bin(bus(xv))})\n"
                f"  y = {yv} ({to_bin(bus(yv))})\n"
                f"  {name} should be {to_int(want)}"
            ))


@pytest.mark.parametrize("ctrl", ALL_CONTROLS)
def test_alu_matches_the_specification_for_every_control_setting(ctrl):
    """All 64 settings, including the 46 nobody gave a name to."""
    for xv in PROBE_VALUES:
        for yv in PROBE_VALUES:
            got = call(xv, yv, ctrl)
            want = spec.ref_alu(bus(xv), bus(yv), *ctrl)
            assert_bus(got[0], want[0], f"alu out with ctrl {ctrl}, x={xv}, y={yv}")
            assert got[1] == want[1], (
                f"zr wrong with ctrl {ctrl}, x={xv}, y={yv}: "
                f"out = {to_int(got[0])}, you said zr = {got[1]}"
            )
            assert got[2] == want[2], (
                f"ng wrong with ctrl {ctrl}, x={xv}, y={yv}: "
                f"out = {to_int(got[0])}, you said ng = {got[2]}"
            )


def test_zr_is_one_exactly_when_the_output_is_zero():
    for ctrl in ALL_CONTROLS:
        for xv in PROBE_VALUES:
            out, zr, _ = call(xv, 0, ctrl)
            assert zr == (1 if to_int(out) == 0 else 0), (
                f"ctrl {ctrl}, x={xv}: out = {to_bin(out)}, zr = {zr}"
            )


def test_ng_is_one_exactly_when_the_output_is_negative():
    for ctrl in ALL_CONTROLS:
        for xv in PROBE_VALUES:
            out, _, ng = call(xv, -3, ctrl)
            assert ng == (1 if to_int(out) < 0 else 0), (
                f"ctrl {ctrl}, x={xv}: out = {to_bin(out)}, ng = {ng}"
            )


def test_ng_is_just_wire_fifteen():
    """In two's complement the sign is not computed, it is read off."""
    for ctrl in ALL_CONTROLS[::5]:
        for xv in PROBE_VALUES:
            out, _, ng = call(xv, 9, ctrl)
            assert ng == out[WORD - 1]


def test_the_flags_are_never_both_set():
    for ctrl in ALL_CONTROLS:
        for xv in PROBE_VALUES[:6]:
            _, zr, ng = call(xv, 5, ctrl)
            assert (zr, ng) != (1, 1), "zero is not negative"


def test_subtraction_is_what_lets_a_cpu_compare():
    """x-y with the two flags is a three-way comparison. This is how `if` works."""
    ctrl = spec.ALU_FUNCTIONS["x-y"]
    for xv, yv in [(5, 3), (3, 5), (4, 4), (-7, -7), (-7, 2), (2, -7), (0, 0)]:
        _, zr, ng = call(xv, yv, ctrl)
        assert (zr == 1) == (xv == yv), f"zr should say whether {xv} == {yv}"
        assert (ng == 1) == (xv - yv < 0), f"ng should say whether {xv} < {yv}"


def test_the_and_path_and_the_add_path_are_independent():
    """f selects between two results that are both always computed."""
    for xv, yv in [(0x0F0F, 0x00FF), (-1, 1234), (MAX, MIN)]:
        and_out, _, _ = call(xv, yv, (0, 0, 0, 0, 0, 0))
        add_out, _, _ = call(xv, yv, (0, 0, 0, 0, 1, 0))
        assert to_int(and_out) == to_int(bus(xv & yv))
        assert to_int(add_out) == to_int(bus(xv + yv))


def test_de_morgan_is_why_the_alu_can_do_or_without_an_or_chip():
    """x|y comes out of the AND path by negating both inputs and the output."""
    for xv, yv in [(0x0F0F, 0x00FF), (-1, 0), (1234, -4321)]:
        out, _, _ = call(xv, yv, spec.ALU_FUNCTIONS["x|y"])
        assert to_int(out) == to_int(bus(xv | yv))


@settings(max_examples=150, deadline=None)
@given(words, words, st.sampled_from(list(spec.ALU_FUNCTIONS)))
def test_alu_named_functions_hold_for_arbitrary_words(a, b, name):
    out, zr, ng = call(a, b, spec.ALU_FUNCTIONS[name])
    want = bus(spec.ALU_MEANING[name](a, b))
    assert_bus(out, want, f"alu {name!r} with x={a}, y={b}")
    assert zr == (1 if to_int(want) == 0 else 0)
    assert ng == (1 if to_int(want) < 0 else 0)


@settings(max_examples=150, deadline=None)
@given(words, words, st.lists(st.integers(0, 1), min_size=6, max_size=6))
def test_alu_matches_specification_for_arbitrary_words_and_controls(a, b, ctrl):
    got = call(a, b, tuple(ctrl))
    want = spec.ref_alu(bus(a), bus(b), *ctrl)
    assert_bus(got[0], want[0], f"alu out, ctrl={ctrl}, x={a}, y={b}")
    assert (got[1], got[2]) == (want[1], want[2])


def test_alu_within_budget():
    args = [(bus(1234), bus(-4321), *ctrl) for ctrl in ALL_CONTROLS[::7]]
    assert_budget(alu, args, spec.LOOSE["alu"], "alu")


@pytest.mark.optimal
def test_alu_is_minimal():
    worst = max(nands_used(alu, bus(1234), bus(-4321), *ctrl) for ctrl in ALL_CONTROLS)
    assert worst == spec.PAR["alu"], (
        f"{worst} NANDs. Par is 741: four Mux16 (4 x 64) and three Not16 "
        f"(3 x 16) for the pre/post-processing, And16 (32) and Add16 (231) for "
        f"the two paths, one Mux16 (64) to choose, and 46 for zr."
    )
