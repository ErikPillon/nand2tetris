"""Project 1 -- Elementary logic gates.  THIS IS YOUR WORKBENCH.

Rules of the workbench
----------------------
1. The only primitive is `nand`. Everything else must be built from `nand`
   and from gates defined earlier *in this file*.
2. Python is wiring notation only. No `if`, `and`, `or`, `not`, `==`, `+`,
   `&`, `|`, `^`, `~`. `for` loops, comprehensions, `zip`, `enumerate`,
   indexing and tuple building are fine -- they describe repeated wiring,
   which is exactly what an HDL `for` does.
3. Signals are the ints 0 and 1. Buses are tuples, index 0 = least
   significant bit. Read the bus convention in `hardware/primitives.py`.

Work top to bottom. `./scripts/n2t next` always points at your next task.
"""

from __future__ import annotations

from hardware.primitives import WORD, Bit, Bus, nand

TODO = "not built yet"


# =========================================================================== #
# 1.1  The three classics
# =========================================================================== #

def not_(a: Bit) -> Bit:
    """Not(a):  out = 1 when a = 0,  out = 0 when a = 1.

    Hint: NAND is NOT-AND. What is NOT (a AND a)?
    """
    return nand(a,a) 


def and_(a: Bit, b: Bit) -> Bit:
    """And(a, b):  out = 1 exactly when both inputs are 1.

    Hint: you now own a Not.
    """
    return not_(nand(a,b))


def or_(a: Bit, b: Bit) -> Bit:
    """Or(a, b):  out = 1 when at least one input is 1.

    Hint: De Morgan.  a OR b = NOT(NOT a AND NOT b).
    """
    return nand(not_(a), not_(b))


def xor(a: Bit, b: Bit) -> Bit:
    """Xor(a, b):  out = 1 exactly when the inputs differ.

    Hint: 'a and not b, or b and not a' is one route. There is a four-NAND
    route that shares a subexpression; find it for the `optimal` marker.
    """
    return or_(and_(a, not_(b)), and_(not_(a), b))


# =========================================================================== #
# 1.2  Steering signals -- where "control" is born
# =========================================================================== #

def mux(a: Bit, b: Bit, sel: Bit) -> Bit:
    """Mux(a, b, sel):  out = a when sel = 0,  out = b when sel = 1.

    This is `if` made out of matter. Everything programmable in the machine
    you are about to build traces back to this gate.
    """
    raise NotImplementedError(f"mux: {TODO} -- lesson 01, step 5")


def dmux(x: Bit, sel: Bit) -> tuple[Bit, Bit]:
    """DMux(in, sel) -> (a, b):  the inverse of Mux.

    sel = 0  ->  (x, 0)
    sel = 1  ->  (0, x)

    Returns a 2-tuple, because a chip may have several output pins.
    """
    raise NotImplementedError(f"dmux: {TODO} -- lesson 01, step 6")


# =========================================================================== #
# 1.3  Word-wide versions (16 copies of the same gate, side by side)
# =========================================================================== #

def not16(x: Bus) -> Bus:
    """Not16(in[16]) -> out[16]:  out[i] = Not(in[i]) for every i."""
    raise NotImplementedError(f"not16: {TODO} -- lesson 01, step 7")


def and16(x: Bus, y: Bus) -> Bus:
    """And16(a[16], b[16]) -> out[16]:  bitwise And."""
    raise NotImplementedError(f"and16: {TODO} -- lesson 01, step 8")


def or16(x: Bus, y: Bus) -> Bus:
    """Or16(a[16], b[16]) -> out[16]:  bitwise Or."""
    raise NotImplementedError(f"or16: {TODO} -- lesson 01, step 9")


def mux16(x: Bus, y: Bus, sel: Bit) -> Bus:
    """Mux16(a[16], b[16], sel) -> out[16]:  one selector steers all 16 wires."""
    raise NotImplementedError(f"mux16: {TODO} -- lesson 01, step 10")


# =========================================================================== #
# 1.4  Multi-way gates -- the address decoders of the memory you will build
# =========================================================================== #

def or8way(x: Bus) -> Bit:
    """Or8Way(in[8]) -> out:  1 when any of the eight wires is 1.

    `x` is an 8-wire bus, not 16. (In Project 5 this chip answers the
    question "is this word nonzero?" for the ALU's zero flag.)
    """
    raise NotImplementedError(f"or8way: {TODO} -- lesson 01, step 11")


def mux4way16(a: Bus, b: Bus, c: Bus, d: Bus, sel: Bus) -> Bus:
    """Mux4Way16: pick one of four words with a 2-wire selector.

    REMEMBER THE BUS CONVENTION. sel[0] is the low bit:

        sel = (0, 0)  i.e. binary "00"  ->  a
        sel = (1, 0)  i.e. binary "01"  ->  b
        sel = (0, 1)  i.e. binary "10"  ->  c
        sel = (1, 1)  i.e. binary "11"  ->  d

    Hint: three Mux16s in a two-level tree. Do not write this gate-by-gate.
    """
    raise NotImplementedError(f"mux4way16: {TODO} -- lesson 01, step 12")


def mux8way16(a: Bus, b: Bus, c: Bus, d: Bus,
              e: Bus, f: Bus, g: Bus, h: Bus, sel: Bus) -> Bus:
    """Mux8Way16: pick one of eight words with a 3-wire selector.

    sel = (s0, s1, s2) with s0 the low bit; "000" -> a ... "111" -> h.
    Hint: a Mux4Way16, another Mux4Way16, and a Mux16 to choose between them.
    """
    raise NotImplementedError(f"mux8way16: {TODO} -- lesson 01, step 13")


def dmux4way(x: Bit, sel: Bus) -> tuple[Bit, Bit, Bit, Bit]:
    """DMux4Way(in, sel[2]) -> (a, b, c, d):  send `x` down one of four paths.

    Same selector convention as mux4way16. The three unselected outputs are 0.
    """
    raise NotImplementedError(f"dmux4way: {TODO} -- lesson 01, step 14")


def dmux8way(x: Bit, sel: Bus) -> tuple[Bit, Bit, Bit, Bit, Bit, Bit, Bit, Bit]:
    """DMux8Way(in, sel[3]) -> (a, ..., h):  send `x` down one of eight paths.

    This is the chip that will decide *which* RAM register gets written to.
    """
    raise NotImplementedError(f"dmux8way: {TODO} -- lesson 01, step 15")
