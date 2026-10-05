"""The single source of truth about the journey: projects, chips, side quests.

`tools/costs.py` and `tools/emit_progress.py` both read this, so a chip is
described in exactly one place.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from hardware.primitives import bus, from_bin


@dataclass(frozen=True)
class Chip:
    name: str                 # attribute in the project's module
    label: str                # how the book names it
    test_file: str | None = None
    probe: tuple | None = None  # arguments for one NAND-cost measurement


@dataclass(frozen=True)
class Project:
    number: int
    slug: str                 # tests/<slug>/
    title: str
    tagline: str              # one sentence, for the station card
    module: str | None        # None once we leave the hardware layer
    workbench: str | None     # the file you edit
    lesson: str | None
    chips: list[Chip] = field(default_factory=list)


_W = [bus(0xBEEF), bus(0x1234)]

PROJECTS: list[Project] = [
    Project(
        1, "project_01_gates", "Boolean logic",
        "Fifteen gates from one NAND. The claim that a computer can exist, verified by construction.",
        "hardware.gates", "hardware/gates.py", "lessons/01-boolean-logic.md",
        [
            Chip("not_", "Not", "test_01_not.py", (0,)),
            Chip("and_", "And", "test_02_and.py", (1, 1)),
            Chip("or_", "Or", "test_03_or.py", (1, 0)),
            Chip("xor", "Xor", "test_04_xor.py", (1, 0)),
            Chip("mux", "Mux", "test_05_mux.py", (1, 0, 1)),
            Chip("dmux", "DMux", "test_06_dmux.py", (1, 1)),
            Chip("not16", "Not16", "test_07_not16.py", (_W[0],)),
            Chip("and16", "And16", "test_08_and16.py", tuple(_W)),
            Chip("or16", "Or16", "test_09_or16.py", tuple(_W)),
            Chip("mux16", "Mux16", "test_10_mux16.py", (*_W, 1)),
            Chip("or8way", "Or8Way", "test_11_or8way.py", ((0, 1, 0, 1, 0, 1, 0, 1),)),
            Chip("mux4way16", "Mux4Way16", "test_12_mux4way16.py",
                 (*[bus(v) for v in (1, 2, 3, 4)], from_bin("10"))),
            Chip("mux8way16", "Mux8Way16", "test_13_mux8way16.py",
                 (*[bus(v) for v in range(8)], from_bin("101"))),
            Chip("dmux4way", "DMux4Way", "test_14_dmux4way.py", (1, from_bin("10"))),
            Chip("dmux8way", "DMux8Way", "test_15_dmux8way.py", (1, from_bin("101"))),
        ],
    ),
    Project(
        2, "project_02_alu", "Boolean arithmetic",
        "Addition out of nothing but NAND, then an ALU that gets eighteen functions from two units.",
        "hardware.alu", "hardware/alu.py", "lessons/02-boolean-arithmetic.md",
        [
            Chip("half_adder", "HalfAdder", "test_01_half_adder.py", (1, 1)),
            Chip("full_adder", "FullAdder", "test_02_full_adder.py", (1, 1, 1)),
            Chip("add16", "Add16", "test_03_add16.py", tuple(_W)),
            Chip("inc16", "Inc16", "test_04_inc16.py", (_W[0],)),
            Chip("alu", "ALU", "test_05_alu.py", (*_W, 0, 1, 0, 0, 1, 1)),
        ],
    ),
    Project(
        3, "project_03_memory", "Sequential logic",
        "A chip whose output depends on the past. The first genuinely hard idea in the course.",
        "hardware.sequential", "hardware/sequential.py", None,
        [Chip(n.lower(), n) for n in
         ["DFF", "Bit", "Register", "RAM8", "RAM64", "RAM512", "RAM4K", "RAM16K", "PC"]],
    ),
    Project(
        4, "project_04_asm", "Machine language",
        "Write programs for a machine that does not exist yet, in its own assembly.",
        None, "projects/04/", None,
        [Chip("mult", "Mult.asm"), Chip("fill", "Fill.asm")],
    ),
    Project(
        5, "project_05_computer", "Computer architecture",
        "A fetch-execute loop made of your own gates. The summit of the hardware half.",
        "hardware.machine", "hardware/machine.py", None,
        [Chip("memory", "Memory"), Chip("cpu", "CPU"), Chip("computer", "Computer")],
    ),
    Project(
        6, "project_06_assembler", "Assembler",
        "Symbolic Hack to binary. Your first translator, and the easy one.",
        None, "software/assembler/", None,
        [Chip("parser", "Parser"), Chip("code", "Code"),
         Chip("symbol_table", "SymbolTable"), Chip("assembler", "Assembler")],
    ),
    Project(
        7, "project_07_vm_stack", "Virtual machine I",
        "A stack machine, and the realisation that a compiler does not have to target hardware.",
        None, "software/vm/", None,
        [Chip("arithmetic", "Stack arithmetic"), Chip("memory_access", "Memory access")],
    ),
    Project(
        8, "project_08_vm_control", "Virtual machine II",
        "Branching, functions, and the call stack. The hardest bookkeeping in the course.",
        None, "software/vm/", None,
        [Chip("branching", "Branching"), Chip("functions", "Function calls"),
         Chip("bootstrap", "Bootstrap")],
    ),
    Project(
        9, "project_09_jack", "A program of your own",
        "Write something in Jack before you have to compile it. Empathy for the user of your compiler.",
        None, "projects/09/", None,
        [Chip("program", "Your Jack program")],
    ),
    Project(
        10, "project_10_parser", "Compiler I: syntax",
        "Tokenizer and recursive-descent parser. Grammar as a data structure.",
        None, "software/compiler/", None,
        [Chip("tokenizer", "Tokenizer"), Chip("parser", "Parser")],
    ),
    Project(
        11, "project_11_codegen", "Compiler II: code",
        "Symbol tables and VM code generation. Where the stack of abstractions closes.",
        None, "software/compiler/", None,
        [Chip("symbols", "Symbol tables"), Chip("expressions", "Expressions"),
         Chip("statements", "Statements"), Chip("objects", "Objects"),
         Chip("arrays", "Arrays")],
    ),
    Project(
        12, "project_12_os", "Operating system",
        "Multiplication, allocation, graphics and text, written in the language you just built.",
        None, "software/os/", None,
        [Chip(n.lower(), n) for n in
         ["Math", "Memory", "Screen", "Keyboard", "String", "Array", "Output", "Sys"]],
    ),
]

PROJECTS_BY_SLUG = {p.slug: p for p in PROJECTS}


# --------------------------------------------------------------------------- #
# Side quests: everything the book does not ask for
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class SideQuest:
    id: str
    title: str
    after: int                # unlocks once this project is done
    effort: str               # "an evening" | "a weekend" | "a project"
    kind: str                 # theory | hardware | systems | tooling | languages
    blurb: str
    status: str = "idea"      # idea | started | done


SIDE_QUESTS: list[SideQuest] = [
    SideQuest("nand-golf", "Hit par on all fifteen gates", 1, "an evening", "hardware",
              "The -m optimal suite enforces the minimal NAND count for every Project 1 chip. "
              "It is a genuine puzzle set, and it teaches the one optimisation that matters: "
              "compute a shared subexpression once."),
    SideQuest("nor-world", "Rebuild everything from NOR", 1, "an evening", "theory",
              "NOR is also functionally complete. Derive the basis from it, then ask which "
              "gates get cheaper and which get dearer -- and why CMOS prefers one."),
    SideQuest("circuit-lower-bound", "Prove most functions need exponentially many gates", 1,
              "an evening", "theory",
              "A counting argument: there are 2^(2^n) Boolean functions but only so many small "
              "circuits, so almost every function needs about 2^n/n gates. Shannon, 1949. "
              "Sobering, and a nice contrast with the constructive DNF bound."),
    SideQuest("smt-verify", "Prove the chips correct instead of testing them", 1, "a weekend",
              "tooling",
              "Bit-blast a gate and its specification into SAT and check that the difference is "
              "unsatisfiable. Exhaustive testing works at 16 bits; proof scales. Z3 via its "
              "Python bindings."),
    SideQuest("carry-lookahead", "An adder with logarithmic depth", 2, "a weekend", "hardware",
              "Ripple-carry has O(n) delay. Add a depth counter to the simulator, measure the "
              "critical path, then build a carry-lookahead adder and watch depth fall to "
              "O(log n) while gate count rises. The first real area-vs-time trade."),
    SideQuest("barrel-shifter", "Shift by any amount in log-depth muxes", 2, "an evening",
              "hardware",
              "Hack has no shift instruction, which is why Jack multiplication is slow. Build a "
              "16-bit barrel shifter from four mux layers, then ask what adding a shift opcode "
              "would do to Project 12's Math.multiply."),
    SideQuest("hardware-multiplier", "A combinational 16x16 multiplier", 2, "a weekend",
              "hardware",
              "An array multiplier, measured in NANDs. Then compare against the software "
              "Math.multiply you will write in Project 12 and decide which the Hack designers "
              "should have chosen."),
    SideQuest("minifloat", "IEEE-754 addition, in miniature", 2, "a project", "hardware",
              "An 8- or 16-bit float adder: unpack, align exponents, add, renormalise, round "
              "to nearest even. Brutal, and the fastest way to understand why floating point "
              "surprises people."),
    SideQuest("event-driven-sim", "Simulate time properly", 3, "a weekend", "tooling",
              "Replace function composition with an event queue and per-gate propagation delay. "
              "Then build a flip-flop out of two NANDs and watch it go metastable -- the thing "
              "the clean abstraction hides from you."),
    SideQuest("prove-the-pc", "Verify the program counter by induction", 3, "an evening",
              "theory",
              "The PC is the first chip with a nontrivial temporal specification. State it as an "
              "invariant over clock cycles and prove it, rather than sampling 200 cycles."),
    SideQuest("rust-emulator", "Port the emulator to Rust", 5, "a project", "languages",
              "The gate-level Computer is too slow to play Pong. Write the behavioural emulator "
              "in Rust and differential-test it against the Python one. Tight integer loops, no "
              "allocation, a reference implementation to check against: a well-scoped first "
              "Rust project."),
    SideQuest("verilog-fpga", "Put your CPU on real silicon", 5, "a project", "hardware",
              "Rewrite the CPU in Verilog, synthesise with Yosys and nextpnr, and run it on a "
              "forty-euro iCE40 board. The moment the abstraction stops being a metaphor."),
    SideQuest("cache", "Add a cache and measure it", 5, "a weekend", "systems",
              "Direct-mapped first, then two-way set-associative. Instrument hit rate on real "
              "programs. Memory hierarchy is the one major architectural idea nand2tetris "
              "leaves out entirely."),
    SideQuest("pipeline", "Pipeline the CPU, then fix the hazards", 5, "a project", "hardware",
              "Split fetch and execute into two stages, discover data and control hazards, then "
              "stall and forward your way out of them. This is most of a first graduate "
              "architecture course."),
    SideQuest("turing-complete", "Prove the Hack machine is Turing-complete", 5, "an evening",
              "theory",
              "Modulo its finite memory. Simulate a two-counter machine, or reduce from a known "
              "universal model. Makes precise what 'general-purpose computer' actually claims."),
    SideQuest("debugger", "A debugger for your own machine", 6, "a weekend", "tooling",
              "Step, breakpoints, memory and register inspection, symbol lookup from the "
              "assembler's table. You will want this long before Project 8 is finished."),
    SideQuest("peephole", "Optimise the code your translator emits", 8, "a weekend", "tooling",
              "The naive VM-to-assembly translation is wildly redundant. Add constant folding "
              "and a peephole pass, then measure cycles saved on a real program. Optimisation "
              "with a number attached to it."),
    SideQuest("jack-types", "A type checker for Jack", 11, "a weekend", "languages",
              "Jack is nominally typed and almost entirely unchecked. Add a checker, then argue "
              "about how much it would have to reject to be sound."),
    SideQuest("gc", "Garbage collection for Jack objects", 11, "a project", "systems",
              "Jack has new and dispose and no safety net. Write a mark-sweep collector over "
              "your own heap, then a copying one, and compare fragmentation."),
    SideQuest("wasm-backend", "Retarget the compiler to WebAssembly", 11, "a project",
              "languages",
              "Same front end, new back end: emit WASM instead of Hack VM code and run your "
              "Jack programs in a browser. The clearest possible demonstration of why the "
              "intermediate language exists."),
    SideQuest("self-hosting", "Compile the compiler with itself", 11, "a project", "languages",
              "Rewrite the Jack compiler in Jack, compile it with the Python one, then compile "
              "it with itself and check the two outputs are identical. The classic bootstrap, "
              "and an unreasonable amount of fun."),
    SideQuest("tetris", "Actually write Tetris", 12, "a weekend", "systems",
              "The thing the course is named after, and nobody makes you do it. Your language, "
              "your compiler, your VM, your assembler, your CPU, your gates."),
]
