#!/usr/bin/env python3
"""state.py — task state and briefs for the Cecilia coordinator (v22).

    S=<SKILL_DIR>/scripts/state.py
    python $S init   --task SHOP-42 --mode standard --goal "add coupon to checkout"
    python $S brief  --task SHOP-42 --role planner --stage design
    python $S answer --task SHOP-42 --text "A; keep legacy endpoint"
    python $S brief  --task SHOP-42 --role dev --kind be --unit coupon-api --sha 1a2b3c --write-set "src/coupon/**"
    python $S round  --task SHOP-42          # exit 3 past the fix-loop limit
    python $S status --task SHOP-42 [--set done] [--mode standard]

Files: <workspace>/tensura/tasks/<TASK>/state.md (human-readable; a `## Notes` section you add is kept)
and run.json (machine state). Workspace = --workspace or the current directory. Standard library only.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
ROLES = ("planner", "dev", "tester", "reviewer", "devops")
KINDS = ("be", "fe", "db", "ui", "-")
MODES = ("fast", "standard", "controlled")
STAGES = ("discover", "design", "plan", "-")
STATUSES = ("planning", "building", "testing", "reviewing", "fixing", "blocked", "done", "stopped")
MAX_ROUNDS = 2
REPORT = {"planner": "plan", "dev": "dev", "tester": "test", "reviewer": "review", "devops": "devops"}
ID = re.compile(r"^[A-Za-z0-9._-]+$")
NOTES = "\n## Notes\n"


def now() -> str:
    return dt.datetime.now().isoformat(timespec="seconds")


def task_dir(ws: Path, task: str) -> Path:
    return ws / "tensura" / "tasks" / task


def load(ws: Path, task: str) -> dict:
    p = task_dir(ws, task) / "run.json"
    if not p.exists():
        raise SystemExit(f"no task {task} in {ws} — run: state.py init --task {task} …")
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except ValueError as e:
        raise SystemExit(f"{p} is not valid JSON ({e}) — restore it from state.md or re-init")


def write(p: Path, text: str) -> None:
    """Atomic: briefs of one wave may run at the same time."""
    tmp = p.with_name(f".{p.name}.{os.getpid()}.tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, p)


def save(ws: Path, task: str, run: dict) -> None:
    d = task_dir(ws, task)
    d.mkdir(parents=True, exist_ok=True)
    old = (d / "state.md").read_text(encoding="utf-8") if (d / "state.md").exists() else ""
    notes = old[old.index(NOTES):] if NOTES in old else NOTES + "(roles: add notes here; state.py keeps this section)\n"
    write(d / "run.json", json.dumps(run, indent=2, ensure_ascii=False))
    log = "\n".join(f"- {e}" for e in run["log"]) or "- (none)"
    write(d / "state.md",
          f"# {task} — {run['status']}\n\n"
          f"Goal: {run['goal']}\nMode: {run['mode']} · Round: {run['round']}/{MAX_ROUNDS} · Updated: {now()}\n\n"
          f"## Decision\n{run.get('decision') or '(not answered yet)'}\n\n## Log\n{log}\n{notes}")


def cmd_init(ws: Path, a) -> str:
    if (task_dir(ws, a.task) / "run.json").exists():
        raise SystemExit(f"{a.task} exists — use `status` (and `status --mode` to change mode)")
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
    run["status"] = "fixing"
    run["log"].append(f"{now()} fix round {run['round']}")
    save(ws, a.task, run)
    return f"round {run['round']}/{MAX_ROUNDS}"


def cmd_status(ws: Path, a) -> str:
    run = load(ws, a.task)
    for key, val in (("status", a.set), ("mode", a.mode)):
        if val and val != run[key]:
            run["log"].append(f"{now()} {key} {run[key]} → {val}")
            run[key] = val
            if key == "mode" and val != "fast" and run["status"] == "building" and not run.get("decision"):
                run["status"] = "planning"  # escalated FAST work goes back through the card
    if a.set or a.mode:
        save(ws, a.task, run)
    return (task_dir(ws, a.task) / "state.md").read_text(encoding="utf-8")


def cmd_brief(ws: Path, a) -> str:
    run = load(ws, a.task)
    if a.role in ("dev", "tester", "devops") and run["mode"] != "fast" and not run.get("decision"):
        raise SystemExit("no decision yet — show the card and run `state.py answer` before any writer")
    if a.role == "dev" and (a.kind == "-" or not a.unit):
        raise SystemExit("dev needs --kind be|fe|db|ui and --unit")
    root = ws.resolve()
    unit = a.unit or "-"
    lens = a.lens or "-"
    writer = a.role in ("dev", "devops") and a.unit
    worktree = a.worktree or (f".worktrees/{unit}" if writer else "")
    workdir = (root / worktree).as_posix() if worktree else "read-only (project root)"
    suffix = unit if a.unit else ("redteam" if "redteam" in lens else "")
    report = REPORT[a.role] + (f"-{suffix}" if suffix else "") + ".md"
    if a.role == "dev":
        report += f" · PR body: tensura/reports/{a.task}/pr-body-{unit}.md"
    if a.role == "reviewer":
        report += " · READ-ONLY: no edits, commits or pushes"
    inputs = a.inputs or "-"
    if run["round"] and a.role in ("dev", "reviewer", "tester"):
        inputs += f"\nRound {run['round']}: fix/re-check only the open finding ids in tensura/reports/{a.task}/review*.md"
    fields = {
        "TASK": a.task, "ROLE": a.role, "KIND": a.kind, "UNIT": unit, "STAGE": a.stage, "LENS": lens,
        "ROUND": str(run["round"]), "MODE": run["mode"], "GOAL": run["goal"],
        "PART": a.part or (f"unit `{unit}` of the plan" if a.unit else
                           "the whole task" if a.role == "planner" else f"{a.role} pass over the integrated branch"),
        "DONE": a.done or ("the plan exists with units, options and questions" if a.role == "planner"
                           else "every check the plan lists for this part is green or explained"),
        "ROOT": root.as_posix(), "SKILL_DIR": SKILL_DIR.as_posix(), "WORKDIR": workdir,
        "WORKDIR_CMD": (root / worktree).as_posix() if worktree else root.as_posix(),
        "BRANCH": a.branch or (f"feature/{a.task}-{unit}" if writer else f"int/{a.task}" if a.role in ("tester", "reviewer")
                               else "(none)"),
        "SHA": a.sha or "(record the start SHA yourself: git rev-parse HEAD)",
        "WRITE_SET": a.write_set or {"planner": "tensura/plans/**, tensura/docs/**, tensura/reports/" + a.task + "/**",
                                     "reviewer": "none (read-only)"}.get(a.role, "the unit's paths in the plan — nothing outside"),
        "PORTS": a.ports or "pick a free range of 10 and record it in your report",
        "DB": re.sub(r"[^a-z0-9]+", "_", f"{a.task}_{unit}".lower()).strip("_"),
        "CHECK_UNIT": a.unit or a.role,
        "INPUTS": inputs, "A3": a.a3 or "none", "REPORT": report,
    }
    text = (SKILL_DIR / "assets" / "agent-brief-template.md").read_text(encoding="utf-8")
    for k, v in fields.items():
        text = text.replace("{{" + k + "}}", v)
    left = re.findall(r"\{\{\w+\}\}", text)
    if left:
        raise SystemExit(f"brief template has unfilled fields: {left}")
    run["log"].append(f"{now()} brief {a.role} {a.kind} {unit} stage={a.stage} lens={lens} r{run['round']}")
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
    b = ps["brief"]
    b.add_argument("--role", choices=ROLES, required=True)
    b.add_argument("--kind", choices=KINDS, default="-")
    b.add_argument("--unit")
    b.add_argument("--stage", choices=STAGES, default="-", help="planner: discover | design | plan")
    b.add_argument("--lens", help="comma-separated, e.g. functional,ui (reviewer: redteam)")
    b.add_argument("--part", help="what this instance must deliver (default: its unit in the plan)")
    b.add_argument("--done", help="checkable done criterion")
    b.add_argument("--sha", help="start / pinned SHA")
    b.add_argument("--branch", help="default feature/<TASK>-<unit> for writers, int/<TASK> for tester/reviewer")
    b.add_argument("--worktree", help="relative to the project root (default .worktrees/<unit> for writers)")
    b.add_argument("--write-set", dest="write_set", help="path globs this instance may write")
    b.add_argument("--ports", help="port range, e.g. 4100-4109")
    b.add_argument("--inputs", help="docs, contract version, finding ids, earlier reports")
    b.add_argument("--a3", help="the exact A3 actions Cecilia approved")
    ps["answer"].add_argument("--text", required=True)
    ps["status"].add_argument("--set", choices=STATUSES)
    ps["status"].add_argument("--mode", choices=MODES, help="escalate, e.g. FAST that grew → standard")
    a = ap.parse_args(argv)
    for v in (a.task, getattr(a, "unit", None)):
        if v and not ID.match(v):
            raise SystemExit(f"invalid id {v!r} — use letters, digits, . _ -")
    fn = {"init": cmd_init, "brief": cmd_brief, "answer": cmd_answer, "round": cmd_round, "status": cmd_status}
    print(fn[a.cmd](Path(a.workspace), a))
    return 0


def _selfcheck() -> None:
    import contextlib
    import io
    import tempfile

    def expect_exit(args, needle):
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                main(args)
        except SystemExit as e:
            assert needle in str(e.code), (args, e.code)
            return
        raise AssertionError(f"{args} must fail with {needle!r}")

    def brief(*extra) -> str:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            main(["brief", *w, *extra])
        return out.getvalue()

    with tempfile.TemporaryDirectory() as tmp:
        w = ["--workspace", tmp, "--task", "T-1"]
        with contextlib.redirect_stdout(io.StringIO()):
            main(["init", *w, "--goal", "g", "--mode", "fast"])
        expect_exit(["init", *w, "--goal", "g"], "exists")
        expect_exit(["init", "--workspace", tmp, "--task", "../x", "--goal", "g"], "invalid id")
        # FAST that grows: escalation puts the decision gate back
        with contextlib.redirect_stdout(io.StringIO()):
            main(["status", *w, "--mode", "standard"])
        expect_exit(["brief", *w, "--role", "dev", "--kind", "be", "--unit", "u1"], "no decision")
        expect_exit(["brief", *w, "--role", "dev", "--kind", "be"], "no decision")
        out = brief("--role", "planner", "--stage", "design")
        assert "STAGE=design" in out and "{{" not in out and "<" not in out.split("## Task")[1], out
        # roles' notes survive state.py rewrites
        sm = Path(tmp, "tensura", "tasks", "T-1", "state.md")
        sm.write_text(sm.read_text(encoding="utf-8") + "- planner: keep v1 endpoint\n", encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()):
            main(["answer", *w, "--text", "A"])
        assert "keep v1 endpoint" in sm.read_text(encoding="utf-8")
        expect_exit(["brief", *w, "--role", "dev", "--kind", "be"], "--unit")
        d1, d2 = brief("--role", "dev", "--kind", "be", "--unit", "u1"), brief("--role", "dev", "--kind", "fe", "--unit", "u2")
        assert "ROLE=dev KIND=be UNIT=u1" in d1 and "dev-u1.md" in d1 and "pr-body-u1.md" in d1
        assert "feature/T-1-u1" in d1 and ".worktrees/u1" in d1 and "dev-u2.md" in d2 and "\\" not in d1
        r2 = brief("--role", "reviewer", "--lens", "redteam")
        assert "review-redteam.md" in r2 and "READ-ONLY" in r2
        for _ in range(2):
            with contextlib.redirect_stdout(io.StringIO()):
                main(["round", *w])
        expect_exit(["round", *w], "3")
    print("state.py self-check OK")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selfcheck"]:
        _selfcheck()
    else:
        sys.exit(main())
