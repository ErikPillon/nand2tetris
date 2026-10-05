# Roadmap

Twelve projects. Each one is a layer that the next one stands on, and each one
is finished when a test suite that already exists turns green. You never have
to guess whether you are done.

The structure is the book's (*The Elements of Computing Systems*, Nisan &
Schocken) and the free lectures at <https://www.nand2tetris.org> follow the same
numbering — watch the Unit *n* videos alongside lesson *n* here.

## What we are building, and in what language

Everything is Python. That is a deliberate choice, not a compromise:

- **Projects 1–5 (the hardware)** are built as Python functions over the ints
  0 and 1. This replaces the book's HDL and its Java simulator. You lose a
  pretty wiring diagram; you gain `pytest`, a debugger, exact NAND accounting,
  and a linter that refuses to let you cheat. The *discipline* is identical:
  one primitive, compose upward, no shortcuts.
- **Projects 6–12 (the software)** — assembler, VM translator, compiler, OS —
  are ordinary Python programs. This is exactly what the book intends.

**Where another language might earn its place.** Nowhere until Project 5, and
even then only for one reason: speed. A gate-level Python `Computer` runs at
maybe a few hundred clock cycles per second, so it can prove *correctness* on
small programs but cannot run Pong at a playable frame rate. So Project 5 ships
two things: the honest gate-level CPU (slow, fully tested, built from your own
chips) and a behavioural emulator (fast, Python, tested to agree with the
gate-level one on every instruction). If you then want Pong at 60 fps, porting
the behavioural emulator to Rust is a genuinely well-scoped Rust exercise —
tight integer loops, no allocation, a clear reference implementation to
differential-test against. That is the one place Rust is worth your time, and
it is optional. I'll flag it when we get there.

## The projects

| # | Project | You build | In | Tests | Lesson |
| --- | --- | --- | --- | --- | --- |
| 1 | Boolean logic | Not, And, Or, Xor, Mux, DMux, 16-bit and multi-way versions | `hardware/gates.py` | `tests/project_01_gates/` | `lessons/01-boolean-logic.md` |
| 2 | Boolean arithmetic | HalfAdder, FullAdder, Add16, Inc16, the ALU | `hardware/alu.py` | `tests/project_02_alu/` | `lessons/02-boolean-arithmetic.md` |
| 3 | Sequential logic | DFF, Bit, Register, RAM8…RAM16K, PC | `hardware/sequential.py` | `tests/project_03_memory/` | `lessons/03-...` |
| 4 | Machine language | Hack assembly programs (Mult, Fill) | `projects/04/*.asm` | `tests/project_04_asm/` | `lessons/04-...` |
| 5 | Computer architecture | Memory, CPU, Computer — the machine | `hardware/machine.py` | `tests/project_05_computer/` | `lessons/05-...` |
| 6 | Assembler | symbolic Hack → binary | `software/assembler/` | `tests/project_06_assembler/` | `lessons/06-...` |
| 7 | VM I | stack arithmetic → Hack assembly | `software/vm/` | `tests/project_07_vm_stack/` | `lessons/07-...` |
| 8 | VM II | branching, functions, the call stack | `software/vm/` | `tests/project_08_vm_control/` | `lessons/08-...` |
| 9 | Jack | a program written in the high-level language | `projects/09/` | `tests/project_09_jack/` | `lessons/09-...` |
| 10 | Compiler I | tokenizer and parser for Jack | `software/compiler/` | `tests/project_10_parser/` | `lessons/10-...` |
| 11 | Compiler II | symbol tables and VM code generation | `software/compiler/` | `tests/project_11_codegen/` | `lessons/11-...` |
| 12 | Operating system | Math, Memory, Screen, Keyboard, String, Array, Output, Sys | `software/os/` | `tests/project_12_os/` | `lessons/12-...` |

Projects 1 and 2 exist right now. Each new project's suite
arrives when you reach it — partly so you aren't staring at 1,200 red tests,
mostly because the tests for layer *n+1* are written in terms of the chips you
actually built at layer *n*.

## The three summits

Three moments are worth naming in advance, because they are the ones that
change how you see computers:

1. **End of Project 2.** You will have built addition out of nothing but
   NAND. Arithmetic stops being a primitive of the universe.
2. **End of Project 5.** A fetch–execute loop made of your own gates runs a
   program you wrote. "Software" and "hardware" turn out to be the same
   material viewed at different magnification.
3. **End of Project 11.** Your compiler compiles a program, your VM translator
   translates it, your assembler assembles it, and your CPU runs it. Every
   layer under your fingertips is yours.

## How each project runs

1. **Lesson.** I teach the layer: the mathematics, the engineering, the
   specification, and the traps. You ask questions until it's boring.
2. **Video (optional).** The nand2tetris Unit *n* lectures, as a second voice.
3. **Red.** `./scripts/n2t next` shows your first failing test.
4. **Green.** You write the chip. Only the chip.
5. **Repeat** down the file.
6. **Gold.** `./scripts/n2t optimal` for the minimal-NAND stretch goals —
   genuine puzzles, entirely skippable.
7. **Review.** You explain your solution to me; I push back where the
   reasoning is thinner than the result.

## Pacing

A realistic shape for someone with your background (mathematics, some Python):

| Projects | Rough effort | Why |
| --- | --- | --- |
| 1 | one sitting | mostly new vocabulary, little difficulty |
| 2–3 | two or three sittings each | project 3 is the first genuinely hard idea (feedback, state, time) |
| 4–5 | the long middle | project 5 is the summit of the hardware half |
| 6 | one sitting | you have written parsers before |
| 7–8 | several sittings | project 8's function-call protocol is the hardest bookkeeping in the course |
| 9 | as long as you enjoy it | |
| 10–11 | the long end | standard compiler work, well-specified |
| 12 | pick the fun ones | `Math.multiply` and `Memory.alloc` are the interesting two |

The only rule that matters: don't skip Project 3. Everything after it assumes
you are comfortable with a chip whose output depends on the past.
