from __future__ import annotations

from hardware.primitives import WORD, Bit, Bus, nand


def not_(a):
    return nand(a, a)


def and_(a, b):
    t = nand(a, b)
    return nand(t, t)


def or_(a, b):
    return nand(nand(a, a), nand(b, b))


def xor(a, b):
    t = nand(a, b)
    return nand(nand(a, t), nand(b, t))


def mux(a, b, sel):
    ns = nand(sel, sel)
    return nand(nand(a, ns), nand(b, sel))


def dmux(x, sel):
    ns = nand(sel, sel)
    ta = nand(x, ns)
    tb = nand(x, sel)
    return (nand(ta, ta), nand(tb, tb))


def not16(x):
    return tuple(not_(bit) for bit in x)


def and16(x, y):
    return tuple(and_(p, q) for p, q in zip(x, y))


def or16(x, y):
    return tuple(or_(p, q) for p, q in zip(x, y))


def mux16(x, y, sel):
    return tuple(mux(p, q, sel) for p, q in zip(x, y))


def or8way(x):
    out = x[0]
    for bit in x[1:]:
        out = or_(out, bit)
    return out


def mux4way16(a, b, c, d, sel):
    ab = mux16(a, b, sel[0])
    cd = mux16(c, d, sel[0])
    return mux16(ab, cd, sel[1])


def mux8way16(a, b, c, d, e, f, g, h, sel):
    low = mux4way16(a, b, c, d, (sel[0], sel[1]))
    high = mux4way16(e, f, g, h, (sel[0], sel[1]))
    return mux16(low, high, sel[2])


def dmux4way(x, sel):
    low, high = dmux(x, sel[1])
    a, b = dmux(low, sel[0])
    c, d = dmux(high, sel[0])
    return (a, b, c, d)


def dmux8way(x, sel):
    low, high = dmux(x, sel[2])
    a, b, c, d = dmux4way(low, (sel[0], sel[1]))
    e, f, g, h = dmux4way(high, (sel[0], sel[1]))
    return (a, b, c, d, e, f, g, h)
