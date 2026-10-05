from __future__ import annotations

from hardware.primitives import ONE, WORD, ZERO, Bit, Bus
from hardware.gates import (
    and16, and_, mux16, not16, not_, or8way, or_, xor,
)


def half_adder(a, b):
    return (xor(a, b), and_(a, b))


def full_adder(a, b, c):
    s1, c1 = half_adder(a, b)
    s2, c2 = half_adder(s1, c)
    return (s2, or_(c1, c2))


def add16(x, y):
    out = []
    s, carry = half_adder(x[0], y[0])
    out.append(s)
    for i in range(1, WORD):
        s, carry = full_adder(x[i], y[i], carry)
        out.append(s)
    return tuple(out)


def inc16(x):
    out = []
    carry = 1
    for bit in x:
        s, carry = half_adder(bit, carry)
        out.append(s)
    return tuple(out)


def alu(x, y, zx, nx, zy, ny, f, no):
    x1 = mux16(x, ZERO, zx)
    x2 = mux16(x1, not16(x1), nx)
    y1 = mux16(y, ZERO, zy)
    y2 = mux16(y1, not16(y1), ny)
    out1 = mux16(and16(x2, y2), add16(x2, y2), f)
    out = mux16(out1, not16(out1), no)
    zr = not_(or_(or8way(out[0:8]), or8way(out[8:WORD])))
    ng = out[WORD - 1]
    return (out, zr, ng)
