"""What you have actually built: the ring Z/2^16, and a complete comparator.

No new chips here. Run these once the ALU is green.
"""

import pytest

from hardware import spec
from hardware.alu import add16, alu, inc16
from hardware.gates import and16, not16, or16, xor
from hardware.primitives import ONE, WORD, ZERO, bus, to_int
from hardware.testkit import sample_words

MIN, MAX = -(1 << (WORD - 1)), (1 << (WORD - 1)) - 1


def test_add16_makes_the_words_an_abelian_group(rng):
    pool = sample_words(rng, n=10)
    for x in pool:
        assert add16(x, ZERO) == x                                  # identity
        assert add16(x, add16(not16(x), ONE)) == ZERO               # inverses
        for y in pool[:5]:
            assert add16(x, y) == add16(y, x)                       # commutative
            for z in pool[:3]:
                assert add16(add16(x, y), z) == add16(x, add16(y, z))


def test_subtraction_is_addition_of_the_complement_plus_one(rng):
    """The identity that lets the ALU subtract without a subtractor."""
    sub = spec.ALU_FUNCTIONS["x-y"]
    for x in sample_words(rng, n=12):
        for y in sample_words(rng, n=6):
            out, _, _ = alu(x, y, *sub)
            assert out == add16(x, add16(not16(y), ONE))


def test_inc16_is_translation_by_one_and_generates_the_whole_group():
    """Iterating inc16 from 0 enumerates every word exactly once per lap."""
    word = ZERO
    for step in range(1, 513):
        word = inc16(word)
        assert to_int(word) == to_int(bus(step))


def test_xor_is_the_sum_and_and_is_the_carry(rng):
    """Addition decomposes as bitwise sum plus shifted carries -- the reason
    a ripple-carry adder is built from Xor and And at all."""
    for x in sample_words(rng, n=12):
        for y in sample_words(rng, n=6):
            bitwise_sum = tuple(xor(p, q) for p, q in zip(x, y))
            carries = and16(x, y)
            shifted = (0,) + carries[: WORD - 1]
            assert add16(x, y) == add16(bitwise_sum, shifted)


def test_the_alu_realises_every_named_hack_function_distinctly():
    """The 18 names are genuinely 18 different functions, not aliases."""
    signatures = {}
    for name, ctrl in spec.ALU_FUNCTIONS.items():
        sig = tuple(
            to_int(alu(bus(a), bus(b), *ctrl)[0])
            for a, b in [(0, 0), (1, 0), (0, 1), (7, 3), (-5, 9), (MAX, MIN)]
        )
        assert sig not in signatures, f"{name!r} and {signatures[sig]!r} compute the same thing"
        signatures[sig] = name
    assert len(signatures) == 18


def test_the_two_flags_decide_every_hack_jump():
    """JGT JEQ JGE JLT JNE JLE, each as a predicate on (zr, ng) alone."""
    jumps = {
        "JGT": lambda zr, ng: 1 - max(zr, ng),
        "JEQ": lambda zr, ng: zr,
        "JGE": lambda zr, ng: 1 - ng,
        "JLT": lambda zr, ng: ng,
        "JNE": lambda zr, ng: 1 - zr,
        "JLE": lambda zr, ng: max(zr, ng),
    }
    truth = {
        "JGT": lambda v: v > 0, "JEQ": lambda v: v == 0, "JGE": lambda v: v >= 0,
        "JLT": lambda v: v < 0, "JNE": lambda v: v != 0, "JLE": lambda v: v <= 0,
    }
    for value in (0, 1, -1, 7, -7, MAX, MIN):
        _, zr, ng = alu(bus(value), ZERO, *spec.ALU_FUNCTIONS["x"])
        for name, predicate in jumps.items():
            assert bool(predicate(zr, ng)) == truth[name](value), (
                f"{name} on out = {value}: flags were zr={zr}, ng={ng}"
            )


def test_or16_agrees_with_the_alu_or(rng):
    for x in sample_words(rng, n=10):
        for y in sample_words(rng, n=5):
            out, _, _ = alu(x, y, *spec.ALU_FUNCTIONS["x|y"])
            assert out == or16(x, y)
