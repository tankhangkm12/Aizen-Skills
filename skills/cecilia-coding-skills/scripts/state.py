#!/usr/bin/env python3
"""state.py — task state and briefs for the Cecilia coordinator (v21).

    python scripts/state.py init   --task SHOP-42 --mode standard --goal "add coupon to checkout"
    python scripts/state.py brief  --task SHOP-42 --role dev --kind be --unit coupon-api
    python scripts/state.py answer --task SHOP-42 --text "A; keep legacy endpoint"
    python scripts/state.py round  --task SHOP-42          # exit 3 past the fix-loop limit
    python scripts/state.py status --task SHOP-42 [--set done]

Files: <workspace>/tensura/tasks/<TASK>/state.md (human-readable) and run.json (machine state).
Workspace = --workspace or the current directory. Standard library only.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
ROLES = ("planner", "dev", "tester", "reviewer", "devops")
KINDS = ("be", "fe", "db", "ui", "-")
MODES = ("fast", "standard", "controlled")
MAX_ROUNDS = 2
REPORT = {"planner": "plan.md", "tester": "test.md", "reviewer": "review.md", "devops": "devops.md"}


def now() -> str:
    return dt.datetime.now().isoformat(timespec="seconds")


def task_dir(ws: Path, task: str) -> Path:
    return ws / "tensura" / "tasks" / task


def load(ws: Path, task: str) -> dict:
    p = task_dir(ws, task) / "run.json"
    if not p.exists():
        raise SystemExit(f"no task {task} in {ws} — run: state.py init --task {task} …")
    return json.loads(p.read_text(encoding="utf-8"))


def save(ws: Path, task: str, run: dict) -> None:
    d = task_dir(ws, task)
    d.mkdir(parents=True, exist_ok=True)
    (d / "run.json").write_text(json.dumps(run, indent=2, ensure_ascii=False), encoding="utf-8")
    log = "\n".join(f"- {e}" for e in run["log"]) or "- (none)"
    (d / "state.md").write_text(
        f"# {task} — {run['status']}\n\n"
        f"Goal: {run['goal']}\nMode: {run['mode']} · Round: {run['round']}/{MAX_ROUNDS} · Updated: {now()}\n\n"
        f"## Decision\n{run.get('decision') or '(not answered yet)'}\n\n## Log\n{log}\n",
        encoding="utf-8")


def cmd_init(ws: Path, a) -> str:
    if (task_dir(ws, a.task) / "run.json").exists():
        return f"{a.task} exists — use status"
    save(ws, a.task, {"task": a.task, "goal": a.goal, "mode": a.mode, "status": "planning",
                      "round": 0, "decision": None, "log": [f"{now()} init ({a.mode})"]})
    return f"created {task_dir(ws, a.task) / 'state.md'}"


def cmd_answer(ws: Path, a) -> str:
    run = load(ws, a.task)
    run.update(decision=a.text, status="building")
    run["log"].append(f"{now()} decision: {a.text}")
    save(ws, a.task, run)
    return "decision recorded"


def cmd_round(ws: Path, a) -> str:
    run = load(ws, a.task)
    if run["round"] >= MAX_ROUNDS:
        print(f"fix-loop limit reached ({MAX_ROUNDS}) — give Cecilia options", file=sys.stderr)
        raise SystemExit(3)
    run["round"] += 1
    run["log"].append(f"{now()} fix round {run['round']}")
    save(ws, a.task, run)
    return f"round {run['round']}/{MAX_ROUNDS}"


def cmd_status(ws: Path, a) -> str:
    run = load(ws, a.task)
    if a.set:
        run["status"] = a.set
        run["log"].append(f"{now()} status → {a.set}")
        save(ws, a.task, run)
    return (task_dir(ws, a.task) / "state.md").read_text(encoding="utf-8")


def cmd_brief(ws: Path, a) -> str:
    run = load(ws, a.task)
    if a.role in ("dev", "tester") and run["mode"] != "fast" and not run.get("decision"):
        raise SystemExit("no decision yet — show the card and run `state.py answer` before any dev/tester")
    if a.role == "dev" and a.kind == "-":
        raise SystemExit("dev needs --kind be|fe|db|ui")
    unit = a.unit or "-"
    report = REPORT.get(a.role) or f"dev-{unit}.md"
    fields = {"TASK": a.task, "ROLE": a.role, "KIND": a.kind, "UNIT": unit, "LENS": a.lens or "-",
              "ROUND": str(run["round"]), "MODE": run["mode"], "GOAL": run["goal"],
              "ROOT": str(ws.resolve()), "SKILL_DIR": str(SKILL_DIR), "REPORT": report}
    text = (SKILL_DIR / "assets" / "agent-brief-template.md").read_text(encoding="utf-8")
    for k, v in fields.items():
        text = text.replace("{{" + k + "}}", v)
    run["log"].append(f"{now()} brief {a.role} {a.kind} {unit} lens={a.lens or '-'} r{run['round']}")
    save(ws, a.task, run)
    return text


def main(argv=None) -> int:
    for s in (sys.stdout, sys.stderr):  # Windows consoles default to a legacy code page
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    ps = {n: sub.add_parser(n) for n in ("init", "brief", "answer", "round", "status")}
    for p in ps.values():
        p.add_argument("--task", required=True)
        p.add_argument("--workspace", default=".")
    ps["init"].add_argument("--goal", required=True)
    ps["init"].add_argument("--mode", choices=MODES, default="standard")
    ps["brief"].add_argument("--role", choices=ROLES, required=True)
    ps["brief"].add_argument("--kind", choices=KINDS, default="-")
    ps["brief"].add_argument("--unit")
    ps["brief"].add_argument("--lens", help="comma-separated, e.g. functional,ui")
    ps["answer"].add_argument("--text", required=True)
    ps["status"].add_argument("--set")
    a = ap.parse_args(argv)
    fn = {"init": cmd_init, "brief": cmd_brief, "answer": cmd_answer, "round": cmd_round, "status": cmd_status}
    print(fn[a.cmd](Path(a.workspace), a))
    return 0


def _selfcheck() -> None:
    import contextlib
    import io
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        w = ["--workspace", tmp, "--task", "T-1"]
        main(["init", *w, "--goal", "g"])
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                main(["brief", *w, "--role", "dev", "--kind", "be", "--unit", "u1"])
            raise AssertionError("dev brief before decision must fail")
        except SystemExit as e:
            assert "no decision" in str(e)
        main(["answer", *w, "--text", "A"])
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            main(["brief", *w, "--role", "dev", "--kind", "be", "--unit", "u1"])
        assert "ROLE=dev KIND=be UNIT=u1" in out.getvalue() and "{{" not in out.getvalue()
        main(["round", *w]); main(["round", *w])
        try:
            main(["round", *w])
            raise AssertionError("third round must exit 3")
        except SystemExit as e:
            assert e.code == 3
    print("state.py self-check OK")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selfcheck"]:
        _selfcheck()
    else:
        sys.exit(main())
