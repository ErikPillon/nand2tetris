#!/usr/bin/env python3
"""Turn the test suite into site/progress.json.

Nothing here is decorative: every number on the website is measured by running
the suite and probing the chips. Run it yourself with `./scripts/n2t site`, or
let the GitHub Action run it on every push.

Always exits 0 -- failing tests are the normal state of this repository.
"""

from __future__ import annotations

import datetime as dt
import importlib
import json
import pathlib
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import asdict

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from hardware import spec                                    # noqa: E402
from hardware.testkit import counting                        # noqa: E402
from tools.registry import PROJECTS, SIDE_QUESTS             # noqa: E402

PY = ROOT / ".venv" / "bin" / "python"
if not PY.exists():
    PY = pathlib.Path(sys.executable)


# --------------------------------------------------------------------------- #
# running the suite
# --------------------------------------------------------------------------- #

def run_suite(markers: str) -> dict[str, dict]:
    """Run the whole suite and return {test file: counts} from the JUnit report."""
    with tempfile.TemporaryDirectory() as tmp:
        report = pathlib.Path(tmp) / "report.xml"
        subprocess.run(
            [str(PY), "-m", "pytest", "tests", "--no-header", "-p", "no:cacheprovider",
             f"--junit-xml={report}", "-m", markers, "--tb=no", "-p", "no:randomly"],
            cwd=ROOT, capture_output=True, text=True,
        )
        if not report.exists():
            return {}
        tree = ET.parse(report)

    files: dict[str, dict] = {}
    for case in tree.iter("testcase"):
        path = case.get("file") or case.get("classname", "").replace(".", "/") + ".py"
        entry = files.setdefault(path, {"total": 0, "passed": 0, "failed": 0, "skipped": 0})
        entry["total"] += 1
        if case.find("failure") is not None or case.find("error") is not None:
            entry["failed"] += 1
        elif case.find("skipped") is not None:
            entry["skipped"] += 1
        else:
            entry["passed"] += 1
    return files


def totals(entries) -> dict:
    out = {"total": 0, "passed": 0, "failed": 0, "skipped": 0}
    for entry in entries:
        for key in out:
            out[key] += entry[key]
    return out


# --------------------------------------------------------------------------- #
# probing the chips
# --------------------------------------------------------------------------- #

def probe(module_name: str | None, chip) -> dict:
    """Is this chip built, and what does it cost?"""
    result = {
        "built": False, "used": None,
        "par": spec.PAR.get(chip.name), "budget": spec.LOOSE.get(chip.name),
        "note": None,
    }
    if module_name is None or chip.probe is None:
        result["note"] = "planned"
        return result
    try:
        fn = getattr(importlib.import_module(module_name), chip.name, None)
    except Exception:
        result["note"] = "module not importable"
        return result
    if not callable(fn):
        result["note"] = "planned"
        return result
    try:
        with counting() as counter:
            fn(*chip.probe)
    except NotImplementedError:
        result["note"] = "not built yet"
        return result
    except Exception as exc:
        result["note"] = f"raised {type(exc).__name__}"
        return result
    result["built"] = True
    result["used"] = counter.count
    if result["par"]:
        if counter.count <= result["par"]:
            result["note"] = "at par"
        elif counter.count <= (result["budget"] or 0):
            result["note"] = f"{counter.count - result['par']} over par"
        else:
            result["note"] = "over budget"
    return result


# --------------------------------------------------------------------------- #
# assembly
# --------------------------------------------------------------------------- #

def build() -> dict:
    default = run_suite("not optimal")
    optimal = run_suite("optimal")

    projects = []
    for project in PROJECTS:
        prefix = f"tests/{project.slug}/"
        own = {p: c for p, c in default.items() if p.startswith(prefix)}
        own_optimal = {p: c for p, c in optimal.items() if p.startswith(prefix)}
        suite = totals(own.values()) if own else {"total": 0, "passed": 0, "failed": 0, "skipped": 0}
        golf = totals(own_optimal.values()) if own_optimal else {"total": 0, "passed": 0}

        chips = []
        for chip in project.chips:
            info = probe(project.module, chip)
            tests = own.get(prefix + chip.test_file) if chip.test_file else None
            chips.append({
                "name": chip.name, "label": chip.label,
                "tests": tests,
                "green": bool(tests and tests["failed"] == 0 and tests["total"] > 0),
                **info,
            })

        built = sum(1 for c in chips if c["green"])
        if not own:
            status = "locked"
        elif suite["failed"] == 0 and suite["total"] > 0:
            status = "complete"
        elif built:
            status = "in_progress"
        else:
            # The suite exists and some scaffolding tests pass, but no chip is
            # finished yet. That is "not started", not "in progress".
            status = "open"

        projects.append({
            "number": project.number, "slug": project.slug, "title": project.title,
            "tagline": project.tagline, "workbench": project.workbench,
            "lesson": project.lesson, "status": status,
            "suite": suite, "optimal": golf,
            "chips": chips, "chips_green": built, "chips_total": len(chips),
        })

    # Exactly one deliverable in the whole journey is the next thing to do.
    for project in projects:
        if project["status"] == "locked":
            continue
        pending = next((c for c in project["chips"] if not c["green"]), None)
        if pending is not None:
            pending["next_up"] = True
            break

    suite_all = totals(p["suite"] for p in projects if p["suite"]["total"])
    golf_all = totals([{**p["optimal"], "failed": 0, "skipped": 0}
                       for p in projects if p["optimal"].get("total")])
    chips_green = sum(p["chips_green"] for p in projects)
    chips_total = sum(p["chips_total"] for p in projects)
    nands = sum(c["used"] for p in projects for c in p["chips"] if c["used"])
    at_par = sum(1 for p in projects for c in p["chips"] if c["note"] == "at par")

    current = next((p["number"] for p in projects if p["status"] == "in_progress"), None)
    if current is None:
        current = next((p["number"] for p in projects if p["status"] in ("open", "locked")), 12)

    return {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "current_project": current,
        "totals": {
            "tests_passed": suite_all["passed"], "tests_total": suite_all["total"],
            "chips_green": chips_green, "chips_total": chips_total,
            "projects_complete": sum(1 for p in projects if p["status"] == "complete"),
            "projects_total": len(projects),
            "optimal_passed": golf_all.get("passed", 0),
            "optimal_total": golf_all.get("total", 0),
            "nands_in_use": nands, "chips_at_par": at_par,
        },
        "projects": projects,
        "side_quests": [asdict(q) for q in SIDE_QUESTS],
    }


def main() -> int:
    data = build()
    out = ROOT / "site" / "progress.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(data, indent=2) + "\n")
    t = data["totals"]
    print(f"  wrote {out.relative_to(ROOT)}")
    print(f"  {t['tests_passed']}/{t['tests_total']} tests, "
          f"{t['chips_green']}/{t['chips_total']} chips, "
          f"project {data['current_project']} in progress, "
          f"{t['nands_in_use']} NANDs in use")
    return 0


if __name__ == "__main__":
    sys.exit(main())
