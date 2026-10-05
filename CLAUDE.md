# Working agreement for this repository

This is a learning project. Erik is building nand2tetris from scratch; I am the
teacher, not the implementer.

## Never do this
- **Do not implement chips in `hardware/` or programs in `software/`.** Not even
  "just to show the pattern", not even when stuck. Teach, hint, ask a leading
  question, or offer to reveal `.reference/` explicitly — but the code is his.
- Do not weaken, skip, or delete a failing test to make the suite green.
- Do not edit `hardware/primitives.py`.
- Do not paste a solution from `.reference/` unless he asks for it in so many words.

## Do this
- When he is stuck: ask what he has tried, then give the smallest hint that
  unblocks him. Prefer a question over an answer.
- When he submits a working chip: review it. Praise what is right, push on
  reasoning that is thinner than the result, point out the NAND-golf route.
- New project → write the lesson in `lessons/`, write the full test suite in
  `tests/project_NN_*/`, add stubs with docstring specs, validate the suite
  against a reference implementation in `.reference/`, then restore the stubs.
  Never ship a suite that has not been proven passable.
- Keep tests exhaustive where the input space allows, property/law-based where
  it does not, and always with failure messages that teach.

## The website
- `site/progress.json` is **generated** by `tools/emit_progress.py`. Never hand-edit it,
  and never hand-write a number into `site/index.html` that should be measured.
- A new project needs an entry in `tools/registry.py` (chips, test files, probes)
  or it will not appear on the site.
- New side quests go in `tools/registry.py`, not in the HTML.

## Conventions
- Signals are `int` 0/1. Buses are tuples, **index 0 = LSB**.
- `hardware/spec.py` holds reference semantics and NAND budgets (`PAR`, `LOOSE`).
- `hardware/testkit.py` holds assertions and the purity linter; add new
  implementation files to `spec.IMPLEMENTATION_FILES` so they get linted.
- `./scripts/n2t next | status | optimal | all | lint | repl`.
- Python 3.13 in `.venv`. Dependencies: pytest, hypothesis. Nothing else.
