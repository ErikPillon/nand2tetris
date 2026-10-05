# Lesson 2 — Boolean arithmetic

**Goal:** five chips in `hardware/alu.py`, all green.
**Prerequisite:** all fifteen Project 1 chips. Steps 1–4 here need only
`xor`, `and_`, `or_`; step 5 also needs `mux16`, `not16`, `and16`, `or8way`.
**Companion video:** nand2tetris Unit 2.

---

## 2.1 The one design decision

A 16-wire bus has $2^{16}$ states. We want to use them to represent integers,
and we have to choose *which* integers and *how*. The choice determines how
expensive arithmetic hardware is, so it is the single most consequential
decision in the lesson.

Suppose we want signed integers. Three candidate encodings:

**Sign-and-magnitude.** Wire 15 is the sign, wires 0–14 the magnitude.
Readable, and terrible: you get two zeros ($+0$ and $-0$), and addition needs
a case analysis — compare magnitudes, decide whether to add or subtract,
decide the sign of the result. That case analysis becomes silicon.

**Ones' complement.** Negate by flipping every bit. Still two zeros, and
addition needs an "end-around carry" correction.

**Two's complement.** Interpret the bus as the integer
$$\mathrm{val}(b) \;=\; -b_{15}\cdot 2^{15} \;+\; \sum_{i=0}^{14} b_i \cdot 2^i .$$
The top wire carries *negative* weight. Range $[-32768, 32767]$, exactly one
zero, and — the reason it won — **the same adder works for signed and unsigned
operands**.

Here is why, and it is worth seeing properly because it is the mathematical
content of this project.

Let $N = 2^{16}$. Reading a bus as an unsigned numeral gives a bijection
$u : \{0,1\}^{16} \to \mathbb{Z}/N$. A ripple-carry adder that discards its
final carry computes addition in $\mathbb{Z}/N$: that is what "discarding the
carry" *means*, since the carry's weight is $N \equiv 0$.

Now two's complement is nothing but a different choice of coset
representatives for the *same* group $\mathbb{Z}/N$: instead of
$\{0, \dots, N-1\}$ we pick $\{-N/2, \dots, N/2 - 1\}$. The map
$\mathrm{val}$ is $u$ followed by that relabelling, and relabelling
representatives does not change the group. So one adder, one circuit, serves
both interpretations, and the "sign" is not a special wire requiring special
treatment — it is wire 15 doing ordinary arithmetic with a negative weight.

Two consequences you will meet in the tests:

**Negation is complement-then-increment.** For any $x$,
$$x + \bar{x} = \underbrace{111\ldots1}_{16} = -1 \quad\Longrightarrow\quad
-x = \bar{x} + 1 .$$
That is a one-line proof and a very large practical fact: **you never need a
subtractor.** $x - y = x + \bar{y} + 1$, and the ALU gets subtraction for the
price of a few inverters it already has.

**Overflow is not an error, it is the specification.** `Add16` computes in
$\mathbb{Z}/2^{16}$. $32767 + 1 = -32768$ is not a bug; the circuit is a ring
homomorphism $\mathbb{Z} \to \mathbb{Z}/2^{16}$ and that is the correct image.
The Hack machine has no overflow flag and no trap. If a program cares, the
program checks.

One wart, worth knowing: the range is asymmetric, so $-(-32768)$ is not
representable and comes back as $-32768$. Negation is not a bijection on the
*interval*, only on the group. `test_00_arithmetic_facts.py` pins this down.

## 2.2 Addition, one column at a time

You have known this algorithm since primary school. Adding two numerals
column by column, right to left, with a carry into the next column. All that
is new is noticing that one column is a Boolean function with a small truth
table, and therefore a chip.

### Step 1 — HalfAdder

Two input bits, and $a + b \in \{0, 1, 2\}$, which needs two output wires:

| a | b | sum | carry |
|---|---|-----|-------|
| 0 | 0 |  0  |   0   |
| 0 | 1 |  1  |   0   |
| 1 | 0 |  1  |   0   |
| 1 | 1 |  0  |   1   |

Cover the `carry` column and read the `sum` column. Then cover `sum` and read
`carry`. You have built both of those chips already. That is the whole step —
it is two lines, and the reason it gets its own step is that the two columns
you are about to recognise are *why* `Xor` and `And` are the gates that matter:

$$\text{sum} = a \oplus b, \qquad \text{carry} = a \wedge b .$$

In $\mathbb{F}_2$ language: $\oplus$ is addition, $\wedge$ is multiplication,
and a half adder is the statement that $a + b$ in $\mathbb{Z}$ equals
$(a \oplus b) + 2(a \wedge b)$.

### Step 2 — FullAdder

Three inputs: two addends and a carry coming in from the right. Output is
still two wires, because $a + b + c \le 3$.

Notice that the function is **symmetric** in all three inputs — it only cares
*how many* of them are 1. So `sum` is the parity of the three, and `carry` is
the majority of the three. The tests check all six permutations, which catches
the common mistake of treating the carry-in as structurally different.

Build it as two half adders: add $a$ and $b$, then add $c$ to that sum. Each
half adder emits a carry. You get two carries and need one — and they can
never both be 1 (why?), so combining them is cheap.

### Step 3 — Add16

Sixteen columns, a carry rippling from wire 0 to wire 15, and the final carry
thrown on the floor. Wire 0 has nothing coming in, so it wants the smaller
chip; the other fifteen want the bigger one. That asymmetry is worth 9 NANDs
and is the only subtlety in the step.

This design is called **ripple-carry**, and it has an honest flaw: the carry
has to physically propagate through fifteen stages before wire 15 is
trustworthy. The circuit's *delay* is linear in the word width, even though
its *size* is too. Real adders don't do this — carry-lookahead and
carry-select schemes compute the carries in parallel, trading gate count for
$O(\log n)$ depth. We are building for correctness and clarity, not for a
clock budget, and ripple-carry is both. But now you know what the first thing
a chip designer would change is, and why.

The tests include the worst case for this design: `0111111111111111 + 1`, a
carry that has to cross every column.

### Step 4 — Inc16

$x + 1$. You could write `add16(x, ONE)` and it would pass, at 231 NANDs.

Think about why that is wasteful. In every column there is only *one* real
addend — the other is 0 except at wire 0. A column whose addend is 0 cannot
generate a carry on its own; it can only *pass on* the carry it receives. So
every column is a half adder taking the bit and the incoming carry, and the
chip costs 96 instead of 231. The default budget lets you be lazy; the
`optimal` marker does not.

`ONE` and `ZERO` live in `hardware.primitives` — hardwired constant buses,
the Python spelling of HDL's `false`.

## 2.3 The ALU

Here is the chip the rest of the course points at. Read the specification
twice before you write anything.

```
inputs:  x[16], y[16], and six control bits zx, nx, zy, ny, f, no
outputs: out[16], zr, ng

if zx == 1:  x = 0            # zero the x input
if nx == 1:  x = Not(x)       # bitwise negate the x input
if zy == 1:  y = 0
if ny == 1:  y = Not(y)
if f  == 1:  out = x + y      # integer addition
else:        out = x And y    # bitwise and
if no == 1:  out = Not(out)   # bitwise negate the output

zr = 1 if out == 0 else 0
ng = 1 if out <  0 else 0
```

### The idea you are meant to take from this

A naive ALU would be a big multiplexor choosing between eighteen separate
circuits: an adder, a subtractor, an incrementer, a decrementer, a negator,
an AND unit, an OR unit… Instead, Nisan and Schocken's ALU contains exactly
**two** functional units — one adder and one bitwise AND — surrounded by
*optional negation and zeroing of the inputs and the output*.

Six one-bit knobs, $2^6 = 64$ settings. Eighteen of them compute things the
Hack instruction set wants. The eighteen come almost free, because negation
is cheap and because of two algebraic facts you already proved:

- **De Morgan** gives you OR from the AND unit: $x \vee y = \overline{\bar{x} \wedge \bar{y}}$, which is `zx=0, nx=1, zy=0, ny=1, f=0, no=1`.
- **Complement-plus-one** gives you subtraction from the adder:
  $x - y = \overline{\bar{x} + y}$. Check it: $\overline{\bar x + y} = -(\bar x + y) - 1 = -(-x-1+y)-1 = x - y$. That is `zx=0, nx=1, zy=0, ny=0, f=1, no=1`.

This is the course's first real lesson in *architecture* as opposed to logic:
the cheap design is not the one with fewer gates per function, it is the one
that finds an algebraic structure letting one unit serve many purposes.

### The control table

Memorise none of this; you will look it up in Project 5 when you build the
instruction decoder. It lives in `spec.ALU_FUNCTIONS`.

| out | zx | nx | zy | ny | f | no |
|-----|----|----|----|----|---|----|
| `0`    | 1 | 0 | 1 | 0 | 1 | 0 |
| `1`    | 1 | 1 | 1 | 1 | 1 | 1 |
| `-1`   | 1 | 1 | 1 | 0 | 1 | 0 |
| `x`    | 0 | 0 | 1 | 1 | 0 | 0 |
| `y`    | 1 | 1 | 0 | 0 | 0 | 0 |
| `!x`   | 0 | 0 | 1 | 1 | 0 | 1 |
| `!y`   | 1 | 1 | 0 | 0 | 0 | 1 |
| `-x`   | 0 | 0 | 1 | 1 | 1 | 1 |
| `-y`   | 1 | 1 | 0 | 0 | 1 | 1 |
| `x+1`  | 0 | 1 | 1 | 1 | 1 | 1 |
| `y+1`  | 1 | 1 | 0 | 1 | 1 | 1 |
| `x-1`  | 0 | 0 | 1 | 1 | 1 | 0 |
| `y-1`  | 1 | 1 | 0 | 0 | 1 | 0 |
| `x+y`  | 0 | 0 | 0 | 0 | 1 | 0 |
| `x-y`  | 0 | 1 | 0 | 0 | 1 | 1 |
| `y-x`  | 0 | 0 | 0 | 1 | 1 | 1 |
| `x&y`  | 0 | 0 | 0 | 0 | 0 | 0 |
| `x|y`  | 0 | 1 | 0 | 1 | 0 | 1 |

Work through three of these by hand before you build the chip — `x+1`,
`x-y`, and `x|y` are the instructive ones. If you can derive those three, you
understand the design; if you cannot, building it will not help.

A worked one, `x+1` = `0 1 1 1 1 1`: $x$ is left alone then negated, so the
adder sees $\bar x$. $y$ is zeroed then negated, so the adder sees
$\overline{0} = -1$. The sum is $\bar x - 1 = (-x - 1) - 1 = -x - 2$. Then
`no` negates it: $\overline{-x-2} = -(-x-2) - 1 = x + 1$. $\square$

### Building it

Those seven `if`s are **not** control flow. Say it again: a circuit has no
control flow. Each one is a `Mux16` choosing between a value and a modified
copy of that value, and *both* are always computed. Four pre/post-processing
stages, two functional units, one selector between them:

```
x ──[zero?]──[negate?]──┐
                        ├──[And16]──┐
y ──[zero?]──[negate?]──┤           ├──[f?]──[negate?]── out
                        └──[Add16]──┘
```

The two flags:

- `ng` costs **nothing**. "Negative" in two's complement is not a computation,
  it is wire 15. Return it.
- `zr` asks whether all sixteen wires are low. `Or8Way` answers that eight
  wires at a time; two of those, combined and inverted, is 46 NANDs.

Those two bits are exactly what a CPU needs to make a decision. In Project 5
the six Hack jump conditions (`JGT JEQ JGE JLT JNE JLE`) are all Boolean
functions of `zr` and `ng` alone — `test_80_algebra.py` builds all six to
prove it. Your `if` statements, three layers of abstraction from now, will be
two wires coming out of this chip.

## 2.4 Budgets

| chip | par | loose |
|---|---|---|
| `half_adder` | 6 | 14 |
| `full_adder` | 15 | 36 |
| `add16` | 231 | 620 |
| `inc16` | 96 | 620 |
| `alu` | 741 | 1900 |

Par here means *minimal using the chips you already own*, composed the
canonical way — not the minimum reachable by dropping back to raw NANDs.
(A half adder is 5 NANDs if you hand-share a subexpression between the Xor
and the And. Par says 6, because abandoning the abstraction is the wrong
lesson at this level.) `./scripts/n2t costs` shows the whole bill.

Note that `add16`'s par of 231 assumes a par `full_adder`, which assumes a par
`xor` and `or_`. **Cost composes.** If your `or_` is 5 NANDs instead of 3, you
pay that surcharge once per `Or` in every chip above it — and there are a lot
of them by the time you reach the ALU. This is not an artificial scoring
system; it is the actual reason chip designers care about the bottom of the
stack.

## 2.5 Exercises

1. Prove that in a full adder the two intermediate carries can never both be
   1. (Then notice which gate you are therefore allowed to use to merge them,
   and that a cheaper one would also work.)
2. Derive the control bits for `y-x` from scratch, then check the table.
3. The ALU has 64 control settings and the table names 18. Of the other 46,
   how many compute a function already in the table under a different
   setting, and how many compute something new? (`test_05_alu.py` checks all
   64 against the spec, so you can answer this experimentally — but try it on
   paper first for the `f=0` half.)
4. Why does the Hack ALU have no `zr`-style flag for *overflow*? What would
   it cost, and what would a program have to do to use it?
5. Suppose you wanted `x*y`. Show that no setting of the six control bits
   produces it, and estimate what a combinational 16×16 multiplier would
   cost in NANDs. (This is why `Math.multiply` is *software*, in Project 12.)

## 2.6 Go

```bash
./scripts/n2t p2
```

When all five are green, come and tell me:

1. your derivation of the `x-y` control bits;
2. why `inc16` is 96 and not 231;
3. your answer to exercise 1.

Then we do the hard one: memory, feedback, and time.
