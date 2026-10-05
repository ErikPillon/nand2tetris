"""Project 2 -- Boolean arithmetic.  YOUR WORKBENCH.

Same rules as `gates.py`: `nand` plus the chips you already own, and Python
only as wiring notation. The difference is that you are now building *out of
Project 1*, not out of NANDs. If you find yourself typing `nand(` in this file,
stop and ask which Project 1 chip you actually wanted.

New this project: `ZERO` and `ONE` from `hardware.primitives` are hardwired
constant buses. Tying an input pin to a constant is legitimate hardware -- in
the book's HDL it is written `Mux16(a=x, b=false, sel=zx)`.

Work top to bottom. `./scripts/n2t next` points at your next task.
"""

from __future__ import annotations

from hardware.primitives import ONE, WORD, ZERO, Bit, Bus
from hardware.gates import (
    and16, and_, dmux, dmux4way, dmux8way, mux, mux16, mux4way16, mux8way16,
    not16, not_, or16, or8way, or_, xor,
)

TODO = "not built yet"


# =========================================================================== #
# 2.1  Adders
# =========================================================================== #

def half_adder(a: Bit, b: Bit) -> tuple[Bit, Bit]:
    """HalfAdder(a, b) -> (sum, carry):  the two bits of a + b.

        a b | sum carry
        0 0 |  0    0
        0 1 |  1    0
        1 0 |  1    0
        1 1 |  0    1

    Look at those two output columns and name them. You already own both chips.
    """
    raise NotImplementedError(f"half_adder: {TODO} -- lesson 02, step 1")


def full_adder(a: Bit, b: Bit, c: Bit) -> tuple[Bit, Bit]:
    """FullAdder(a, b, c) -> (sum, carry):  the two bits of a + b + c.

    `c` is the carry coming in from the column to the right. Note that the
    function is symmetric in all three inputs -- it only cares how many of them
    are 1 -- which is a useful check on whatever you build.

    Hint: add two of them, then add the third to that sum. Two HalfAdders
    produce two carries; what do you do with both?
    """
    raise NotImplementedError(f"full_adder: {TODO} -- lesson 02, step 2")


def add16(x: Bus, y: Bus) -> Bus:
    """Add16(a[16], b[16]) -> out[16]:  two's-complement addition.

    The carry out of wire 15 is thrown away, so this computes in Z / 2**16.
    Overflow is not an error here; it is the specification.

    Hint: column by column from wire 0 upward, carrying. Wire 0 has no carry
    coming in, so it needs a smaller chip than the other fifteen.
    """
    raise NotImplementedError(f"add16: {TODO} -- lesson 02, step 3")


def inc16(x: Bus) -> Bus:
    """Inc16(in[16]) -> out[16]:  in + 1, again modulo 2**16.

    You could call `add16(x, ONE)`. It would pass. It costs more than twice
    what the chip needs, because adding 1 to a column can only ever produce a
    carry -- there is no second addend to worry about. The budget allows the
    lazy version; the `optimal` marker does not.
    """
    raise NotImplementedError(f"inc16: {TODO} -- lesson 02, step 4")


# =========================================================================== #
# 2.2  The Arithmetic Logic Unit
# =========================================================================== #

def alu(x: Bus, y: Bus,
        zx: Bit, nx: Bit, zy: Bit, ny: Bit,
        f: Bit, no: Bit) -> tuple[Bus, Bit, Bit]:
    """The Hack ALU. Returns (out[16], zr, ng).

    Six control bits, applied in this order:

        if zx == 1:  x = 0            # zero the x input
        if nx == 1:  x = Not(x)       # negate (bitwise) the x input
        if zy == 1:  y = 0
        if ny == 1:  y = Not(y)
        if f  == 1:  out = x + y      # integer addition
        else:        out = x And y    # bitwise and
        if no == 1:  out = Not(out)   # negate the output

    and two status flags describing the result:

        zr = 1 if out == 0, else 0
        ng = 1 if out <  0, else 0

    Those `if`s are not control flow -- they are six Mux16s. Build the chip as
    a straight pipeline: pre-process x, pre-process y, combine, post-process.

    `ng` costs you nothing: in two's complement, "negative" *is* a wire.
    `zr` needs you to ask whether all sixteen wires are low, and Or8Way
    answers that question eight wires at a time.
    """
    raise NotImplementedError(f"alu: {TODO} -- lesson 02, step 5")
