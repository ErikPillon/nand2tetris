"""Sanity checks on the equipment. These pass before you write any code.

If anything here fails, the problem is the setup, not your gates.
"""

import pytest

from hardware.primitives import (
    SignalError, bus, counting, from_bin, nand, to_bin, to_int,
)
from hardware.testkit import tuples


def test_nand_truth_table():
    assert nand(0, 0) == 1
    assert nand(0, 1) == 1
    assert nand(1, 0) == 1
    assert nand(1, 1) == 0


def test_nand_rejects_anything_that_is_not_a_clean_signal():
    for bad in (True, False, 2, -1, None, 0.0, "1", [1]):
        with pytest.raises(SignalError):
            nand(bad, 0)
        with pytest.raises(SignalError):
            nand(0, bad)


def test_counting_counts():
    with counting() as outer:
        nand(0, 0)
        with counting() as inner:
            nand(0, 1)
            nand(1, 1)
        assert inner.count == 2
    assert outer.count == 3


def test_counter_is_released_after_the_block():
    with counting() as c:
        nand(0, 0)
    nand(0, 0)
    assert c.count == 1


def test_bus_is_lsb_first():
    assert bus(1, 4) == (1, 0, 0, 0)
    assert bus(8, 4) == (0, 0, 0, 1)
    assert bus(-1, 4) == (1, 1, 1, 1)


def test_bin_helpers_use_paper_order():
    assert from_bin("0001") == (1, 0, 0, 0)
    assert to_bin((1, 0, 0, 0)) == "0001"
    assert to_bin(bus(5, 8)) == "00000101"


def test_int_roundtrip_is_two_complement():
    for value in (0, 1, -1, 32767, -32768, 1234, -1234):
        assert to_int(bus(value)) == value
    assert to_int(bus(-1), signed=False) == 65535


def test_tuples_enumerates_the_cube():
    assert tuples(2) == [(0, 0), (0, 1), (1, 0), (1, 1)]
    assert len(tuples(3)) == 8
