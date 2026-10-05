# Lesson 0 — Orientation

## 0.1 The confusion you arrived with, named

You said you have read a lot about transistors and chips and are confused. That
is the correct response to the literature, because most of it mixes four
*different* subjects and calls them all "how computers work":

1. **Solid-state physics.** Why doping silicon gives you a material whose
   conductivity you can control with a voltage. Genuinely hard, genuinely
   irrelevant to everything above it.
2. **Circuit design.** How to arrange a handful of transistors into a device
   that maps input voltages to output voltages reliably, at speed, without
   melting.
3. **Logic design.** How to arrange such devices into something that computes.
4. **Architecture and software.** How to arrange *that* into a machine you can
   program.

This course is 3 and 4. We will spend exactly one page on 2 — enough to make
the primitive feel physical rather than magical — and zero on 1.

Here is the page.

A MOSFET is a voltage-controlled switch: a gate terminal, and a channel that
either conducts or doesn't depending on the gate voltage. The n-type kind
conducts when its gate is *high*; the p-type kind conducts when its gate is
*low*. Now wire four of them like this: two p-type in **parallel** between the
supply voltage and the output, and two n-type in **series** between the output
and ground, with inputs *a* and *b* driving one of each.

- If *a* and *b* are both high: both n-type conduct, so the series path to
  ground is complete and the output is pulled **low**. Both p-type are off.
- If either input is low: that n-type breaks the series path, and the
  corresponding p-type conducts, pulling the output **high**.

Output is low exactly when both inputs are high. That is NOT-AND. Four
transistors. That is the entire physical content of this course, and you can
forget it after today — which is the point of an abstraction.

Two things worth noticing, because they explain the shape of everything that
follows. First, CMOS logic is naturally *inverting*: the cheap gates are NAND
and NOR, and AND costs strictly more than NAND (it is a NAND plus an
inverter). Nature hands you negation for free and conjunction at a markup.
Second, nothing above this line cares. We will declare that a wire carries the
number 0 or the number 1, and never speak of volts again.

## 0.2 The one rule

`hardware/primitives.py` gives you `nand(a, b)`. That is the only thing you are
given. Every other chip in this repository must be composed out of it, or out
of chips you have already composed out of it.

This is not a game. It is the claim the whole subject rests on: a universal
computer is a finite composition of one trivially simple part. You are going to
verify that claim by construction, which is the only way a mathematician is
ever really satisfied.

The repository enforces the rule two ways:

- **At runtime.** `nand` validates its inputs. If a `bool` or a `2` reaches a
  pin you get a `SignalError`, because that almost always means you reached for
  a Python comparison instead of building a gate.
- **Statically.** `hardware/testkit.py` parses your implementation file as a
  syntax tree and rejects `if`, `and`, `or`, `not`, `==`, `+`, `&`, `|`, `^`,
  `~` and friends. Python is permitted as *wiring notation only*: calls, names,
  tuples, indexing, `for`, comprehensions, `zip`, `enumerate`. Those describe
  repeated wiring, which is precisely what an HDL `for` generates.

So `return 1 - a` is not a Not gate. `return nand(a, a)` is.

## 0.3 Why not the official HDL and Java simulator

The book has you write `.hdl` files and feed them to a Java simulator. We're
writing Python instead. The trade:

**Lost:** the visual wiring metaphor, and a simulator that resolves genuinely
cyclic circuits for you. (The second matters once, in Project 3; I'll handle it
when we get there.)

**Gained:** `pytest -x`, a real debugger, exact NAND accounting, property-based
tests, algebraic-law tests, a linter that makes cheating impossible, and the
fact that in Projects 6–12 you are writing Python anyway — so the whole stack
lives in one language with one test runner.

The discipline is identical. A Python function from bits to bits, built only
from `nand`, *is* a combinational circuit. The syntax is the only difference.

## 0.4 Signals and buses

A **signal** is the Python `int` 0 or the Python `int` 1. Not `True`, not
`None`, not `0.0`.

A **bus** is a `tuple` of signals, **least significant bit at index 0**:

```python
bus(5, 4)    == (1, 0, 1, 0)      # index 0 is the ones place
to_bin(bus(5, 8)) == '00000101'   # paper order, MSB on the left
from_bin("1000") == (0, 0, 0, 1)  # the numeral eight
```

Index 0 is the LSB because that is the nand2tetris HDL convention and because
carries propagate upward from index 0 in the adder you build next week. It is
the reverse of how you write a numeral, so `to_bin` / `from_bin` exist to
translate. **Most Project 1 bugs are this convention.** When a test fails,
read the binary strings in the failure message, not the tuples.

Buses are tuples, not lists, deliberately: a bus is a bundle of wire *values*,
not a mutable container. A chip takes values in and returns values out.

A chip with several output pins returns a tuple of them:

```python
a, b = dmux(x, sel)
```

## 0.5 The loop

```bash
./scripts/n2t next      # the first failing test. That is your task. Only that.
```

Write the smallest wiring that makes it pass. Run it again. Move down the file.

Each chip's test file checks four different things, and it is worth knowing
which is which when one goes red:

- **correctness** — the truth table, exhaustively where the input space is
  small enough, against `hardware/spec.py` otherwise;
- **structure** — that the output really is a bit or a tuple of bits, that an
  unselected input doesn't leak through, that wires don't cross-talk;
- **algebra** — that your gates satisfy De Morgan, associativity,
  distributivity, absorption. These catch subtly wrong chips that happen to
  pass a truth table you typed by hand;
- **cost** — a NAND budget. The default budget is generous; it only fires when
  you have rebuilt something from scratch instead of reusing a chip you
  already own. `./scripts/n2t optimal` enforces the *minimal* count instead,
  which is a real puzzle and entirely optional.

When everything is green, `./scripts/n2t status`, then come and tell me how
you solved it. Explaining it is where the learning finishes.

## 0.6 One habit worth forming now

Build each chip out of the *largest* pieces available, not out of NANDs. A
`Mux4Way16` written as three `Mux16` calls is three lines and obviously
correct. The same chip written out of NANDs is 192 lines and you will never
find the bug. That is not a stylistic preference — it is the single technique
that makes the rest of the course possible, and the NAND budgets are there to
force the habit.

Now: `lessons/01-boolean-logic.md`.
