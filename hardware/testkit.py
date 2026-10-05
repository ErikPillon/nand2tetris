"""Assertion helpers and the HDL-purity linter used by the test suite."""

from __future__ import annotations

import ast
import itertools
import pathlib
import random
from collections.abc import Callable, Iterable, Sequence

from hardware.primitives import WORD, bus, counting, to_bin

BITS = (0, 1)

#: Words worth trying on every 16-bit chip: zero, all-ones, the sign bit,
#: the largest positive, alternating patterns, a single hot bit at each index.
EDGE_WORDS: tuple[int, ...] = (
    0, -1, 1, -2, 2, 0x7FFF, -0x8000, 0x5555, -0x5556, 0x0F0F, 0x1234, -1234,
)


def tuples(n: int) -> list[tuple[int, ...]]:
    """Every combination of n bits, in counting order."""
    return list(itertools.product(BITS, repeat=n))


def sample_words(rng: random.Random, n: int = 48) -> list[tuple[int, ...]]:
    """Edge-case words plus pseudo-random ones, as 16-bit buses."""
    out = [bus(v) for v in EDGE_WORDS]
    out += [bus(1 << i) for i in range(WORD)]
    out += [bus(rng.getrandbits(WORD)) for _ in range(n)]
    return out


def nands_used(fn: Callable, *args) -> int:
    """How many NANDs one evaluation of `fn` burns."""
    with counting() as counter:
        fn(*args)
    return counter.count


# --------------------------------------------------------------------------- #
# assertions
# --------------------------------------------------------------------------- #

def assert_bit(value: object, label: str) -> None:
    assert value.__class__ is int and value in BITS, (
        f"{label} returned {value!r}; a chip output pin carries the int 0 or 1 "
        f"(got {type(value).__name__})"
    )


def assert_bus(got: object, want: Sequence[int], label: str, width: int = WORD) -> None:
    assert isinstance(got, tuple), f"{label} returned {type(got).__name__}; a bus output must be a tuple"
    assert len(got) == width, f"{label} returned {len(got)} wires, expected {width}"
    for i, bit in enumerate(got):
        assert_bit(bit, f"{label}[{i}]")
    assert tuple(got) == tuple(want), (
        f"{label}\n"
        f"  got      {to_bin(got)}\n"
        f"  expected {to_bin(want)}\n"
        f"  (MSB on the left; wires differ at indices "
        f"{[i for i, (g, w) in enumerate(zip(got, want)) if g != w]})"
    )


def assert_truth_table(fn: Callable, ref: Callable, arity: int, name: str) -> None:
    """Exhaustively compare a single-bit chip against its specification."""
    for args in tuples(arity):
        got = fn(*args)
        assert_bit(got, f"{name}{args}")
        want = ref(*args)
        assert got == want, f"{name}{args} = {got}, specification says {want}"


def assert_uses_hardware(fn: Callable, *args, name: str) -> None:
    """A chip that computes without burning a single NAND is not a chip."""
    assert nands_used(fn, *args) >= 1, (
        f"{name} produced an answer without using a single NAND gate. "
        "Arithmetic and Python logic are not hardware -- compose nand()."
    )


def assert_budget(fn: Callable, args_list: Iterable[tuple], limit: int, name: str) -> None:
    worst = max(nands_used(fn, *args) for args in args_list)
    assert worst <= limit, (
        f"{name} burns up to {worst} NANDs; the budget is {limit}.\n"
        f"  Two things cause this, and only one of them is about {name}:\n"
        f"    1. {name} itself is built from NANDs where a chip you already own would do;\n"
        f"    2. {name} is fine, but a chip it depends on is expensive, and you are\n"
        f"       paying that surcharge once per use.\n"
        f"  Run  ./scripts/n2t costs  to see the whole bill and find the lowest offender."
    )


# --------------------------------------------------------------------------- #
# the purity linter
# --------------------------------------------------------------------------- #
# Hardware has no `if`, no `and`, no `-`. Your implementation modules may use
# Python only as wiring notation: calls, names, tuples, indexing, loops,
# comprehensions. Everything that could *compute* a bit behind the simulator's
# back is rejected.

ALLOWED_IMPORT_ROOTS = frozenset({
    "__future__", "typing", "collections.abc",
    "hardware.primitives", "hardware.gates", "hardware.alu",
    "hardware.sequential", "hardware.machine",
})
FORBIDDEN_IMPORTS = frozenset({"hardware.spec", "hardware.testkit", "operator"})
ALLOWED_BUILTINS = frozenset({"range", "zip", "enumerate", "reversed", "tuple", "list", "len",
                              "NotImplementedError"})
#: Building a bus up wire by wire is fine; anything else is not wiring.
ALLOWED_METHODS = frozenset({"append", "extend"})

# Nodes that may appear in an expression we are willing to treat as a
# compile-time constant (index arithmetic, a hardwired constant bus). Every
# leaf must be a literal or a known constant name, so no signal can hide here.
_CONST_NODES = (ast.Constant, ast.Name, ast.BinOp, ast.UnaryOp, ast.Load,
                ast.Tuple, ast.List, ast.Starred,
                ast.Add, ast.Sub, ast.Mult, ast.FloorDiv, ast.USub, ast.UAdd)


class _Linter(ast.NodeVisitor):
    def __init__(self, path: pathlib.Path, source: str) -> None:
        self.path = path
        self.problems: list[str] = []
        tree = ast.parse(source, filename=str(path))
        self.tree = tree
        self.consts = {"WORD", "ZERO", "ONE"}
        self.known: set[str] = set(ALLOWED_BUILTINS)
        for node in tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                self._check_import(node)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                self.known.add(node.name)
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id.isupper():
                        self.consts.add(target.id)

    def _flag(self, node: ast.AST, message: str) -> None:
        self.problems.append(f"{self.path}:{getattr(node, 'lineno', '?')}: {message}")

    def _check_import(self, node: ast.Import | ast.ImportFrom) -> None:
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                self.known.add(alias.asname or alias.name)
            full = f"{module}.{node.names[0].name}" if module == "hardware" else module
            if full in FORBIDDEN_IMPORTS:
                self._flag(node, f"importing {full} is cheating -- that module holds the answers")
            elif full not in ALLOWED_IMPORT_ROOTS:
                self._flag(node, f"import of {full!r} is not allowed in an implementation module")
        else:
            for alias in node.names:
                self.known.add((alias.asname or alias.name).split(".")[0])
                if alias.name not in ALLOWED_IMPORT_ROOTS:
                    self._flag(node, f"import of {alias.name!r} is not allowed in an implementation module")

    # -- expression-level rules (only applied inside function bodies) -------- #

    def _is_constant_expr(self, node: ast.AST) -> bool:
        for sub in ast.walk(node):
            if isinstance(sub, ast.Name):
                if sub.id not in self.consts:
                    return False
            elif not isinstance(sub, _CONST_NODES):
                return False
        return True

    def visit_BoolOp(self, node: ast.BoolOp) -> None:
        word = "and" if isinstance(node.op, ast.And) else "or"
        self._flag(node, f"`{word}` is a Python operator, not a gate -- call your own and_/or_")
        self.generic_visit(node)

    def visit_Compare(self, node: ast.Compare) -> None:
        self._flag(node, "comparisons produce bools, not signals -- route the wire through a Mux instead")
        self.generic_visit(node)

    def visit_IfExp(self, node: ast.IfExp) -> None:
        self._flag(node, "a conditional expression is a Mux in disguise -- build the Mux")
        self.generic_visit(node)

    def visit_If(self, node: ast.If) -> None:
        self._flag(node, "`if` does not exist in hardware -- use mux()/dmux() to steer signals")
        self.generic_visit(node)

    def visit_While(self, node: ast.While) -> None:
        self._flag(node, "`while` does not exist in combinational hardware")
        self.generic_visit(node)

    def visit_Match(self, node: ast.Match) -> None:
        self._flag(node, "`match` does not exist in hardware -- that is what Mux8Way is for")
        self.generic_visit(node)

    def visit_BinOp(self, node: ast.BinOp) -> None:
        if not self._is_constant_expr(node):
            self._flag(node, f"`{type(node.op).__name__}` arithmetic on signals -- "
                             "a wire is not a number here, compose gates")
        self.generic_visit(node)

    def visit_UnaryOp(self, node: ast.UnaryOp) -> None:
        if isinstance(node.op, (ast.Not, ast.Invert)):
            self._flag(node, "`not` / `~` is Python's negation, not yours -- use not_()")
        elif not self._is_constant_expr(node):
            self._flag(node, "arithmetic on signals -- compose gates")
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        func = node.func
        if isinstance(func, ast.Name) and func.id not in self.known:
            self._flag(node, f"calls {func.id!r}, which is not a chip you built, imported, or a wiring builtin")
        elif isinstance(func, ast.Attribute) and func.attr not in ALLOWED_METHODS:
            self._flag(node, f"`.{func.attr}()` is not wiring")
        self.generic_visit(node)

    def run(self) -> list[str]:
        for node in self.tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for child in node.body:
                    self.visit(child)
        return self.problems


def lint_module(path: str | pathlib.Path) -> list[str]:
    """Return a list of 'that is not hardware' complaints about a module."""
    p = pathlib.Path(path)
    return _Linter(p, p.read_text()).run()
