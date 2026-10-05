# nand2tetris, from one NAND gate up

A full computer — gates, ALU, memory, CPU, assembler, virtual machine,
compiler, operating system — built from a single primitive, in Python,
test-first.

```bash
./scripts/n2t status     # scoreboard
./scripts/n2t costs      # where your NANDs go, per chip, against par
./scripts/n2t next       # the first failing test = your next task
./scripts/n2t optimal    # the NAND-golf stretch goals
./scripts/n2t repl       # interactive: nand + your gates preloaded
./scripts/n2t site       # re-measure everything and update the website
```

Read [`lessons/00-orientation.md`](lessons/00-orientation.md) first, then
[`lessons/01-boolean-logic.md`](lessons/01-boolean-logic.md), then open
[`hardware/gates.py`](hardware/gates.py) and start wiring.

| Where | What |
| --- | --- |
| `hardware/primitives.py` | the one gate you are given. Read it, never edit it. |
| `hardware/gates.py` | **your workbench** for Project 1 |
| `hardware/alu.py` | **your workbench** for Project 2 |
| `hardware/spec.py` | the specification (what each chip must compute) and the NAND budgets |
| `hardware/testkit.py` | assertion helpers and the "is this really hardware?" linter |
| `tests/` | the curriculum, as executable tests |
| `lessons/` | the teaching material |
| `ROADMAP.md` | all twelve projects and what each one costs |
| `site/` | the progress website (see `DEPLOY.md`) |
| `tools/registry.py` | projects, deliverables and side quests, in one place |
| `.reference/` | answer key. Don't. |

Python 3.13 in `.venv`. The only dependencies are `pytest` and `hypothesis`.
