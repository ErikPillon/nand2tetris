"""Reference semantics: *what* each chip must compute, said in ordinary Python.

This file is the specification, not the implementation. It is allowed to use
`&`, `|`, `if` and friends precisely because it is not hardware -- it is the
contract the tests hold your hardware to.

You may read this file freely. You may not import it from an implementation
module; the purity tests will catch that.
"""

from __future__ import annotations

from collections.abc import Sequence

from hardware.primitives import WORD


# --- single-bit ------------------------------------------------------------ #

def ref_not(a: int) -> int:
    return 1 - a


def ref_and(a: int, b: int) -> int:
    return a & b


def ref_or(a: int, b: int) -> int:
    return a | b


def ref_xor(a: int, b: int) -> int:
    return a ^ b


def ref_mux(a: int, b: int, sel: int) -> int:
    """sel == 0 -> a, sel == 1 -> b."""
    return b if sel else a


def ref_dmux(x: int, sel: int) -> tuple[int, int]:
    """Route x to output a (sel == 0) or output b (sel == 1); other output is 0."""
    return (0, x) if sel else (x, 0)


# --- word-wide ------------------------------------------------------------- #

def ref_not16(x: Sequence[int]) -> tuple[int, ...]:
    return tuple(ref_not(bit) for bit in x)


def ref_and16(x: Sequence[int], y: Sequence[int]) -> tuple[int, ...]:
    return tuple(ref_and(p, q) for p, q in zip(x, y))


def ref_or16(x: Sequence[int], y: Sequence[int]) -> tuple[int, ...]:
    return tuple(ref_or(p, q) for p, q in zip(x, y))


def ref_mux16(x: Sequence[int], y: Sequence[int], sel: int) -> tuple[int, ...]:
    return tuple(y) if sel else tuple(x)


def ref_or8way(x: Sequence[int]) -> int:
    return 1 if any(x) else 0


def _index(sel: Sequence[int]) -> int:
    """Selector bus -> integer. sel[0] is the LSB, exactly as on the wires."""
    value = 0
    for i, bit in enumerate(sel):
        value |= bit << i
    return value


def ref_mux4way16(a, b, c, d, sel) -> tuple[int, ...]:
    return tuple((a, b, c, d)[_index(sel)])


def ref_mux8way16(a, b, c, d, e, f, g, h, sel) -> tuple[int, ...]:
    return tuple((a, b, c, d, e, f, g, h)[_index(sel)])


def ref_dmux4way(x: int, sel: Sequence[int]) -> tuple[int, int, int, int]:
    out = [0, 0, 0, 0]
    out[_index(sel)] = x
    return tuple(out)


def ref_dmux8way(x: int, sel: Sequence[int]) -> tuple[int, ...]:
    out = [0] * 8
    out[_index(sel)] = x
    return tuple(out)


# --------------------------------------------------------------------------- #
# Project 2 -- Boolean arithmetic
# --------------------------------------------------------------------------- #

def ref_half_adder(a: int, b: int) -> tuple[int, int]:
    """(sum, carry) for a + b, each a single bit."""
    total = a + b
    return (total % 2, total // 2)


def ref_full_adder(a: int, b: int, c: int) -> tuple[int, int]:
    """(sum, carry) for a + b + c, each a single bit."""
    total = a + b + c
    return (total % 2, total // 2)


def ref_add16(x: Sequence[int], y: Sequence[int]) -> tuple[int, ...]:
    """Two's-complement addition. The carry out of wire 15 is discarded, so
    this is arithmetic in the ring Z / 2**16."""
    from hardware.primitives import bus, to_int
    return bus(to_int(x) + to_int(y))


def ref_inc16(x: Sequence[int]) -> tuple[int, ...]:
    from hardware.primitives import bus, to_int
    return bus(to_int(x) + 1)


#: The Hack ALU's six control bits, and what each useful setting computes.
#: Keys are the function as written in the book; values are
#: (zx, nx, zy, ny, f, no).
ALU_FUNCTIONS: dict[str, tuple[int, int, int, int, int, int]] = {
    "0":    (1, 0, 1, 0, 1, 0),
    "1":    (1, 1, 1, 1, 1, 1),
    "-1":   (1, 1, 1, 0, 1, 0),
    "x":    (0, 0, 1, 1, 0, 0),
    "y":    (1, 1, 0, 0, 0, 0),
    "!x":   (0, 0, 1, 1, 0, 1),
    "!y":   (1, 1, 0, 0, 0, 1),
    "-x":   (0, 0, 1, 1, 1, 1),
    "-y":   (1, 1, 0, 0, 1, 1),
    "x+1":  (0, 1, 1, 1, 1, 1),
    "y+1":  (1, 1, 0, 1, 1, 1),
    "x-1":  (0, 0, 1, 1, 1, 0),
    "y-1":  (1, 1, 0, 0, 1, 0),
    "x+y":  (0, 0, 0, 0, 1, 0),
    "x-y":  (0, 1, 0, 0, 1, 1),
    "y-x":  (0, 0, 0, 1, 1, 1),
    "x&y":  (0, 0, 0, 0, 0, 0),
    "x|y":  (0, 1, 0, 1, 0, 1),
}

#: Each ALU function as a plain Python function of two ints, for cross-checking.
ALU_MEANING = {
    "0":   lambda a, b: 0,
    "1":   lambda a, b: 1,
    "-1":  lambda a, b: -1,
    "x":   lambda a, b: a,
    "y":   lambda a, b: b,
    "!x":  lambda a, b: ~a,
    "!y":  lambda a, b: ~b,
    "-x":  lambda a, b: -a,
    "-y":  lambda a, b: -b,
    "x+1": lambda a, b: a + 1,
    "y+1": lambda a, b: b + 1,
    "x-1": lambda a, b: a - 1,
    "y-1": lambda a, b: b - 1,
    "x+y": lambda a, b: a + b,
    "x-y": lambda a, b: a - b,
    "y-x": lambda a, b: b - a,
    "x&y": lambda a, b: a & b,
    "x|y": lambda a, b: a | b,
}


def ref_alu(x, y, zx, nx, zy, ny, f, no) -> tuple[tuple[int, ...], int, int]:
    """The Hack ALU, straight from the book's pseudocode.

        if zx: x = 0          if zy: y = 0
        if nx: x = !x         if ny: y = !y
        if f:  out = x + y    else:  out = x & y
        if no: out = !out
        zr = (out == 0);  ng = (out < 0)

    Returns (out_bus, zr, ng).
    """
    from hardware.primitives import WORD, bus, to_int

    xv, yv = to_int(x), to_int(y)
    if zx:
        xv = 0
    if nx:
        xv = ~xv
    if zy:
        yv = 0
    if ny:
        yv = ~yv
    out = xv + yv if f else xv & yv
    if no:
        out = ~out
    word = bus(out, WORD)
    value = to_int(word)
    return (word, 1 if value == 0 else 0, 1 if value < 0 else 0)


# --------------------------------------------------------------------------- #
# NAND budgets
# --------------------------------------------------------------------------- #
# PAR is the minimal number of NANDs a correct chip needs *given the chips you
# already own*, composed the canonical way -- not the minimum reachable by
# dropping back down to raw NANDs. (A half adder, for instance, is 5 NANDs if
# you hand-share subexpressions, but 6 if you honestly reuse Xor and And. PAR
# says 6, because abandoning the abstraction is the wrong lesson.)
# LOOSE is what the default test suite enforces: enough
# room for an honest first solution, tight enough to catch a chip that is
# accidentally quadratic. Beating LOOSE is required; reaching PAR is the
# `-m optimal` stretch goal.

PAR: dict[str, int] = {
    "not_": 1,
    "and_": 2,
    "or_": 3,
    "xor": 4,
    "mux": 4,
    "dmux": 5,
    "not16": 16,
    "and16": 32,
    "or16": 48,
    "mux16": 64,
    "or8way": 21,
    "mux4way16": 192,
    "mux8way16": 448,
    "dmux4way": 15,
    "dmux8way": 35,
    # project 2
    "half_adder": 6,
    "full_adder": 15,
    "add16": 231,
    "inc16": 96,
    "alu": 741,
}

LOOSE: dict[str, int] = {
    "not_": 2,
    "and_": 4,
    "or_": 6,
    "xor": 10,
    "mux": 10,
    "dmux": 12,
    "not16": 32,
    "and16": 64,
    "or16": 96,
    "mux16": 160,
    "or8way": 56,
    "mux4way16": 520,
    "mux8way16": 1200,
    "dmux4way": 40,
    "dmux8way": 96,
    # project 2
    "half_adder": 14,
    "full_adder": 36,
    "add16": 620,
    "inc16": 620,
    "alu": 1900,
}

IMPLEMENTATION_FILES = ["hardware/gates.py", "hardware/alu.py"]

__all__ = [name for name in dir() if name.startswith("ref_")] + [
    "PAR", "LOOSE", "IMPLEMENTATION_FILES", "WORD",
    "ALU_FUNCTIONS", "ALU_MEANING",
]
