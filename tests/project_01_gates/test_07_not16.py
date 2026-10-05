"""Step 7: Not16 -- the same gate, sixteen times. Note the bus convention."""

import pytest

from hardware import spec
from hardware.gates import not16
from hardware.primitives import WORD, bus, from_bin, to_int
from hardware.testkit import assert_bus, assert_budget, nands_used, sample_words


def test_not16_on_known_words():
    cases = {
        "0000000000000000": "1111111111111111",
        "1111111111111111": "0000000000000000",
        "0000000000000001": "1111111111111110",
        "1000000000000000": "0111111111111111",
        "0101010101010101": "1010101010101010",
    }
    for given, expected in cases.items():
        assert_bus(not16(from_bin(given)), from_bin(expected), f"not16({given})")


def test_not16_matches_spec_everywhere_we_look(rng):
    for word in sample_words(rng):
        assert_bus(not16(word), spec.ref_not16(word), f"not16({word})")


def test_not16_inverts_each_wire_independently():
    """Flipping input wire i must flip output wire i and nothing else."""
    base = not16(bus(0))
    for i in range(WORD):
        flipped = not16(bus(1 << i))
        differing = [j for j in range(WORD) if flipped[j] != base[j]]
        assert differing == [i], f"changing in[{i}] changed out{differing}"


def test_not16_is_an_involution(rng):
    for word in sample_words(rng, n=16):
        assert not16(not16(word)) == word


def test_not16_is_two_complement_negation_minus_one(rng):
    """~x == -x - 1. A free arithmetic identity, and a sanity check on signs."""
    for word in sample_words(rng, n=16):
        assert to_int(not16(word)) == -to_int(word) - 1


def test_not16_within_budget(rng):
    assert_budget(not16, [(w,) for w in sample_words(rng, n=4)], spec.LOOSE["not16"], "not16")


@pytest.mark.optimal
def test_not16_is_minimal():
    assert nands_used(not16, bus(0)) == spec.PAR["not16"], "one NAND per wire, sixteen wires"
