#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""state.py — task state and briefs for the aizen-build coordinator (v26).

    S=<SKILL_DIR>/scripts/flow/state.py
    uv run $S waves   --task SHOP-42 [--max 3]          # which units may run together, from the plan's write sets + after
    uv run $S init    --task SHOP-42 --goal "add coupon to checkout" [--slug checkout-coupon] [--type feature] [--ticket SHOP-42]
    uv run $S branch  --task SHOP-42 [--unit coupon-api]   # the git branch name: <type>/<slug>[-<unit>], never the run id
    uv run $S brief   --task SHOP-42 --role planner --stage design
    uv run $S answer  --task SHOP-42 --module coupon-api --text "B: one endpoint, keep legacy"   # one per module
    uv run $S approve --task SHOP-42 --text "plan v2 approved"   # the contract: roles never ask again
    uv run $S brief  --task SHOP-42 --role dev --kind be --unit coupon-api --sha 1a2b3c --write-set "src/coupon/**"
    uv run $S round  --task SHOP-42          # exit 3 past the fix-loop limit
    uv run $S status --task SHOP-42 [--set done]

Files: <workspace>/.aizen/runs/<TASK>/state.md (human-readable; a `## Notes` section you add is kept), run.json
(machine state) and plan.md; the guard (aizen-core scripts/core/guard.py) marks the run done. Workspace = --workspace or the current directory. Standard library only.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys
import unicodedata
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[2]  # <skill>/scripts/flow/state.py
ROLES = ("planner", "dev", "tester", "reviewer", "devops")
KINDS = ("be", "fe", "db", "ui", "-")
STAGES = ("discover", "design", "plan", "-")
STATUSES = ("planning", "building", "testing", "reviewing", "fixing", "blocked", "done", "stopped")
MAX_ROUNDS = 2
REPORT = {"planner": "plan", "dev": "dev", "tester": "test", "reviewer": "review", "devops": "devops"}
ID = re.compile(r"^[A-Za-z0-9._-]+$")
NOTES = "\n## Notes\n"
VERSION = 26
BRANCH_TYPES = ("feature", "bugfix", "hotfix", "refactor", "test", "docs", "ci", "infra", "chore")
TC = re.compile(r"\bTC-\d+\b")


def now() -> str:
    return dt.datetime.now().isoformat(timespec="seconds")


def task_dir(ws: Path, task: str) -> Path:
    return ws / ".aizen" / "runs" / task


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
    agreed = "\n".join(f"- {m}: {t}" for m, t in run.get("agreed", {}).items()) or "- (nothing confirmed yet)"
    write(d / "state.md",
          f"# {task} — {run['status']}\n\n"
          f"Goal: {run['goal']}\nRound: {run['round']}/{MAX_ROUNDS} · Updated: {now()}\n\n"
          f"## Agreed (per module)\n{agreed}\n\n## Approval\n{run.get('decision') or '(plan not approved yet)'}\n\n"
          f"## Log\n{log}\n{notes}")


LOCAL_ONLY = (".aizen/",)


def exclude_local(ws: Path) -> list[str]:
    """Keep the agent workspace out of git without touching a tracked file: .git/info/exclude (references/core/workspace.md)."""
    import subprocess
    try:
        common = subprocess.run(["git", "-C", str(ws), "rev-parse", "--path-format=absolute", "--git-common-dir"],
                                capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return []  # not a git checkout: nothing to protect
    info = Path(common) / "info" / "exclude"
    info.parent.mkdir(parents=True, exist_ok=True)
    have = info.read_text(encoding="utf-8").splitlines() if info.exists() else []
    added = [e for e in LOCAL_ONLY if e not in have]
    if added:
        with info.open("a", encoding="utf-8") as f:
            f.write(("\n" if have and have[-1] else "") + "\n".join(added) + "\n")
    return added


def cmd_init(ws: Path, a) -> str:
    if (task_dir(ws, a.task) / "run.json").exists() or (ws / ".aizen" / "archive" / a.task).exists():
        raise SystemExit(f"{a.task} exists — use `status`")
    core = backlog_mod() if a.backlog else None
    if core:
        why = core.can_start(ws, a.backlog)
        if why:
            raise SystemExit(why)
    name = slugify(a.slug or a.goal)
    if not name:
        raise SystemExit("--slug: a short business name for the branch, e.g. seat-hold, payment-timeout")
    save(ws, a.task, {"run": a.task, "skill": "aizen-build", "task": a.task, "goal": a.goal, "status": "planning",
                      "round": 0, "agreed": {}, "decision": None, "outputs": [], "backlog": a.backlog,
                      "v": VERSION, "slug": name, "branch_type": a.type, "ticket": a.ticket,
                      "created": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "log": [f"{now()} init"]})
    if core:
        core.set_backlog(ws, a.backlog, "doing", a.task)
    added = exclude_local(ws)
    handoff(ws, a.task)
    note = f" · .git/info/exclude += {', '.join(added)}" if added else ""
    return f"created {task_dir(ws, a.task) / 'state.md'} · branch {branch_name(load(ws, a.task), a.task)}{note}"


def slugify(text: str, limit: int = 32) -> str:
    """Business name for a branch: ASCII kebab-case, Vietnamese accents folded (`Giữ ghế 5 phút` → `giu-ghe-5-phut`)."""
    t = unicodedata.normalize("NFKD", text.replace("đ", "d").replace("Đ", "D"))
    t = re.sub(r"[^a-z0-9]+", "-", t.encode("ascii", "ignore").decode().lower()).strip("-")
    return t[:limit].rsplit("-", 1)[0] if len(t) > limit and "-" in t[:limit] else t[:limit]


WRITE_SET = re.compile(r"^\s*Files\s*\(write set\)\s*:\s*(.+)$", re.M | re.I)
NO_FILES = {"", "-", "—", "none", "n/a", "(none)"}


def writer_units(ws: Path, task: str) -> list[str]:
    """Modules of the plan that change files (a read-only module gets no branch)."""
    p = task_dir(ws, task) / "plan.md"
    if not p.is_file():
        return []
    text = p.read_text(encoding="utf-8")
    heads = list(MODULE.finditer(text))
    out = []
    for i, m in enumerate(heads):
        body = text[m.end():heads[i + 1].start() if i + 1 < len(heads) else len(text)].split("\n## ", 1)[0]
        line = WRITE_SET.search(body)
        raw = re.findall(r"`([^`]+)`", line.group(1)) if line else []
        if any(r.strip().lower() not in NO_FILES for r in raw) or (line and not raw and line.group(1).strip().lower() not in NO_FILES):
            out.append(m.group(1))
    return out


def branch_name(run: dict, task: str, unit: str | None = None, writers: int | None = None) -> str:
    """The git branch of a run (references/core/git.md §1): named after the business change, never the run id.

    final (the PR):   <type>/<slug>             — the integration of the units, or the only unit
    one unit of many: <type>/<slug>-<unit>      — local only, merged into the final branch
    Runs started before v26 keep their old names (feature/<TASK>-<unit>, int/<TASK>).
    """
    if run.get("v", 0) < 26:
        return f"feature/{task}-{unit}" if unit else f"int/{task}"
    base = f"{run.get('branch_type') or 'feature'}/{run.get('slug') or slugify(task)}"
    return base if not unit or (writers is not None and writers <= 1) else f"{base}-{unit}"


def cmd_branch(ws: Path, a) -> str:
    run = load(ws, a.task)
    return branch_name(run, a.task, a.unit, len(writer_units(ws, a.task)))


def acceptance(ws: Path, task: str) -> tuple[Path, list[str]]:
    p = task_dir(ws, task) / "acceptance.md"
    text = re.sub(r"~~[^~]*~~", "", p.read_text(encoding="utf-8")) if p.is_file() else ""   # ~~TC-05~~ = dropped
    return p, sorted(set(TC.findall(text)))


def core_mod(name: str):
    """A script of aizen-core (project.py owns .aizen/backlog.md, journal.py the hand-off), found through the packs."""
    import importlib.util
    core = topic_dirs().get("core")
    if not core:
        raise SystemExit("aizen-core is not installed next to this skill — run `node bin/cli.js sync`")
    sys.path.insert(0, str(core / "scripts" / "core"))
    spec = importlib.util.spec_from_file_location(name, core / "scripts" / "core" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def backlog_mod():
    return core_mod("project")


def handoff(ws: Path, task: str) -> None:
    """Refresh .aizen/out/latest.md (journal.py report) at every milestone; never break the command."""
    try:
        core_mod("journal").report(ws, task)
    except (Exception, SystemExit):  # noqa: BLE001
        pass


def cmd_answer(ws: Path, a) -> str:
    run = load(ws, a.task)
    run.setdefault("agreed", {})[a.module] = a.text
    run["log"].append(f"{now()} agreed {a.module}: {a.text}")
    save(ws, a.task, run)
    return f"{a.module} recorded — next module, or `approve` once every module is agreed"


MODULE = re.compile(r"^## Module\s+`?([A-Za-z0-9._-]+)`?", re.M)


# ── waves: which units may run at the same time (references/flow/parallel.md) ────────────────────────────

UNIT_HEAD = re.compile(r"^## Module\s+`?([A-Za-z0-9._-]+)`?(.*)$", re.M)
AFTER = re.compile(r"\bafter\s*:\s*([^·|\n]+)", re.I)
WILD = re.compile(r"[*?\[{]")
PARALLEL_MAX = 2


def parallel_max(ws: Path) -> int:
    """`.aizen/config/guard.json` → "parallel": {"max": n}; default 2 — each unit costs a worktree, a dispatch,
    its own ports, containers and database on one machine."""
    try:
        cfg = json.loads((ws / ".aizen" / "config" / "guard.json").read_text(encoding="utf-8"))
        return max(1, int((cfg.get("parallel") or {}).get("max", PARALLEL_MAX)))
    except (OSError, ValueError, TypeError, AttributeError):
        return PARALLEL_MAX


def plan_units(ws: Path, task: str) -> list[dict]:
    """[{id, write: [globs], after: [ids]}] in plan order; retired ~~ids~~ are not modules."""
    p = task_dir(ws, task) / "plan.md"
    if not p.is_file():
        raise SystemExit(f"no plan at .aizen/runs/{task}/plan.md")
    text = p.read_text(encoding="utf-8")
    heads = list(UNIT_HEAD.finditer(text))
    units = []
    for i, m in enumerate(heads):
        body = text[m.end():heads[i + 1].start() if i + 1 < len(heads) else len(text)].split("\n## ", 1)[0]
        line = WRITE_SET.search(body)
        raw = line.group(1) if line else ""
        globs = re.findall(r"`([^`]+)`", raw) or [g for g in re.split(r"[,\s]+", raw) if g]
        found = AFTER.search(m.group(2)) or AFTER.search(body)
        after = [x.strip("`") for x in re.split(r"[,\s]+", found.group(1)) if x.strip("`")] if found else []
        units.append({"id": m.group(1),
                      "write": [g.strip().lstrip("./") for g in globs if g.strip().lower() not in NO_FILES],
                      "after": [x for x in after if x.lower() not in NO_FILES | {"parallel", "and"}]})
    return units


def overlaps(a: str, b: str) -> bool:
    """Conservative: two globs may touch the same file when one's fixed prefix starts the other's."""
    pa, pb = WILD.split(a, 1)[0], WILD.split(b, 1)[0]
    if not WILD.search(a) and not WILD.search(b):
        return a == b
    return pa.startswith(pb) or pb.startswith(pa)


def shared(u: dict, v: dict) -> list[str]:
    return [f"`{a}` ~ `{b}`" if a != b else f"`{a}`" for a in u["write"] for b in v["write"] if overlaps(a, b)]


def plan_waves(units: list[dict], limit: int) -> tuple[list[list[str]], list[str]]:
    """Waves in plan order: a unit joins the first wave after all of its `after` units, unless it shares files
    with a member or the wave is full — then it moves to the next wave (and says why)."""
    ids = {u["id"] for u in units}
    bad = [f"{u['id']} waits for unknown unit {x}" for u in units for x in u["after"] if x not in ids]
    if bad:
        raise SystemExit("plan: " + "; ".join(bad))
    done, waves, notes, left = set(), [], [], list(units)
    while left:
        ready = [u for u in left if all(x in done for x in u["after"])]
        if not ready:
            raise SystemExit("plan: the `after` lines form a cycle: " + ", ".join(u["id"] for u in left))
        wave = []
        for u in ready:
            clash = next(((w, shared(u, w)) for w in wave if shared(u, w)), None)
            if clash:
                notes.append(f"{u['id']} after {clash[0]['id']}: both write {', '.join(clash[1][:3])}")
            elif len(wave) >= limit:
                notes.append(f"{u['id']} waits: parallel.max = {limit}")
            else:
                wave.append(u)
        waves.append([u["id"] for u in wave])
        done |= {u["id"] for u in wave}
        left = [u for u in left if u["id"] not in done]
    return waves, notes


def cmd_waves(ws: Path, a) -> str:
    limit = a.max or parallel_max(ws)
    units = plan_units(ws, a.task)
    if not units:
        raise SystemExit(f"no modules in .aizen/runs/{a.task}/plan.md")
    waves, notes = plan_waves(units, limit)
    out = [f"Waves for {a.task} (parallel.max = {limit}, `.aizen/config/guard.json` → parallel.max):"]
    out += [f"  {i}: {' ‖ '.join(w)}" for i, w in enumerate(waves, 1)]
    if notes:
        out += ["Sequenced:", *[f"  - {n}" for n in notes]]
    out.append("Launch every unit of a wave in one message; the next wave starts when the wave is clean.")
    return "\n".join(out)


def plan_modules(ws: Path, task: str) -> list[str] | None:
    """Module ids of .aizen/runs/<TASK>/plan.md, retired ones (~~id~~) excluded; None when there is no plan file."""
    p = task_dir(ws, task) / "plan.md"
    if not p.is_file():
        return None
    return MODULE.findall(p.read_text(encoding="utf-8"))


def cmd_approve(ws: Path, a) -> str:
    run = load(ws, a.task)
    agreed = run.get("agreed") or {}
    if not agreed:
        raise SystemExit("nothing agreed yet — confirm each module with `answer --module` first")
    modules = plan_modules(ws, a.task)
    if modules is None:
        raise SystemExit(f"no plan at .aizen/runs/{a.task}/plan.md — the planner writes it before approval")
    parts = ["scope", *modules, "delivery"]
    acc, cases = acceptance(ws, a.task)
    if run.get("v", 0) >= 26:
        if not cases:
            raise SystemExit(f"no acceptance cases at .aizen/runs/{a.task}/acceptance.md — the planner writes TC-nn cases "
                             "per AC (assets/plan/acceptance-template.md) before approval")
        parts.insert(1, "acceptance")
    missing = [m for m in parts if m not in agreed]
    if missing:
        raise SystemExit("not confirmed with the owner yet: " + ", ".join(missing)
                         + " — one `answer --module <part>` each, then approve")
    run.update(decision=f"{now()} {a.text}", status="building")
    if cases:
        run["acceptance_sha"] = hashlib.sha256(acc.read_bytes()).hexdigest()
    run["log"].append(f"{now()} plan approved: {a.text}" + (f" · {len(cases)} acceptance cases frozen" if cases else ""))
    save(ws, a.task, run)
    handoff(ws, a.task)
    return "plan approved — build without further questions" + (f"; {len(cases)} acceptance cases frozen" if cases else "")


def cmd_round(ws: Path, a) -> str:
    run = load(ws, a.task)
    if run["round"] >= MAX_ROUNDS:
        print(f"fix-loop limit reached ({MAX_ROUNDS}) — give the owner options", file=sys.stderr)
        raise SystemExit(3)
    run["round"] += 1
    run["status"] = "fixing"
    run["log"].append(f"{now()} fix round {run['round']}")
    save(ws, a.task, run)
    handoff(ws, a.task)
    return f"round {run['round']}/{MAX_ROUNDS}"


def cmd_status(ws: Path, a) -> str:
    run = load(ws, a.task)
    if a.set == "done":
        raise SystemExit("the guard marks a run done when every check passes: "
                         "uv run <CORE_DIR>/scripts/core/guard.py done --run " + a.task)
    if a.set and a.set != run["status"]:
        run["log"].append(f"{now()} status {run['status']} → {a.set}")
        run["status"] = a.set
        save(ws, a.task, run)
        handoff(ws, a.task)
    return (task_dir(ws, a.task) / "state.md").read_text(encoding="utf-8")


def topic_dirs(skills_root: Path | None = None) -> dict[str, Path]:
    """topic → the installed skill that owns it, read from each sibling's manifest.json `topics`.

    Open for extension: a new pack only declares its topics; nothing here changes.
    """
    root = skills_root or SKILL_DIR.parent
    owners: dict[str, Path] = {}
    for m in sorted(root.glob("*/manifest.json")):
        try:
            data = json.loads(m.read_text(encoding="utf-8"))
        except ValueError:
            continue
        for topic in data.get("topics", []):
            owners.setdefault(topic, m.parent.resolve())
    return owners


def required_packs() -> list[str]:
    data = json.loads((SKILL_DIR / "manifest.json").read_text(encoding="utf-8"))
    return [SKILL_DIR.name, *data.get("requires", [])]


def pack_table() -> tuple[str, Path]:
    """One line per pack: the topics it owns → its absolute folder. A required pack missing → stop, never guess."""
    owners = topic_dirs()
    installed = {d.name for d in owners.values()}
    missing = [p for p in required_packs() if p not in installed]
    if missing:
        raise SystemExit("required Aizen pack(s) not installed next to this skill: " + ", ".join(missing)
                         + "\nrun `node bin/cli.js sync` in the Aizen-Skills repo, then retry")
    wanted = set(required_packs())
    by_dir: dict[Path, list[str]] = {}
    for topic, d in owners.items():
        if d.name in wanted:  # only the packs this skill declares in `requires` (Interface Segregation)
            by_dir.setdefault(d, []).append(topic)
    rows = [f"  {{references,assets,scripts}}/{{{','.join(ts)}}}/ → {d.as_posix()}/" for d, ts in by_dir.items()]
    return "\n".join(rows), owners["core"]


def optional_tools() -> str:
    """Community skills this skill may use (manifest `optional`), found next to it or not — never installed from here."""
    names = json.loads((SKILL_DIR / "manifest.json").read_text(encoding="utf-8")).get("optional", [])
    found = [f"{n} → {(SKILL_DIR.parent / n).resolve().as_posix()}" if (SKILL_DIR.parent / n / "SKILL.md").is_file()
             else f"{n}: not installed (owner: `aizen external install {n}`)" for n in names]
    return " · ".join(found) or "none"


def code_map(root: Path) -> str:
    g = root / "graphify-out" / "graph.json"
    if not g.is_file():
        return "none — search with grep/glob (the coordinator builds it with scripts/core/graph.py)"
    return (f'graphify query "<question>" --graph "{g.as_posix()}"  · also `affected "<symbol>"`, '
            '`path "A" "B"`, `explain "X"` (references/core/code-map.md)')


def cmd_brief(ws: Path, a) -> str:
    run = load(ws, a.task)
    design_work = a.role == "dev" and a.kind == "ui"  # UI design is design: confirmed stage by stage, before approve
    if a.role in ("dev", "tester", "devops") and not design_work and not run.get("decision"):
        raise SystemExit("plan not approved — confirm each module with the owner, then `state.py approve`")
    if a.role == "dev" and (a.kind == "-" or not a.unit):
        raise SystemExit("dev needs --kind be|fe|db|ui and --unit")
    packs, core_dir = pack_table()
    root = ws.resolve()
    unit = a.unit or "-"
    lens = a.lens or "-"
    writer = a.role in ("dev", "devops") and a.unit
    worktree = a.worktree or (f".aizen/worktrees/{a.task}-{unit}" if writer else "")
    workdir = (root / worktree).as_posix() if worktree else "read-only (project root)"
    suffix = unit if a.unit else ("redteam" if "redteam" in lens else "")
    report = REPORT[a.role] + (f"-{suffix}" if suffix else "") + ".md"
    if a.role == "dev":
        report += f" · PR body: .aizen/runs/{a.task}/reports/pr-body-{unit}.md"
    if a.role == "reviewer":
        report += " · READ-ONLY: no edits, commits or pushes"
    inputs = a.inputs or "-"
    if run["round"] and a.role in ("dev", "reviewer", "tester"):
        inputs += f"\nRound {run['round']}: fix/re-check only the open finding ids in .aizen/runs/{a.task}/reports/review*.md"
    fields = {
        "TASK": a.task, "ROLE": a.role, "KIND": a.kind, "UNIT": unit, "STAGE": a.stage, "LENS": lens,
        "ROUND": str(run["round"]), "GOAL": run["goal"],
        "PART": a.part or (f"unit `{unit}` of the plan" if a.unit else
                           "the whole task" if a.role == "planner" else f"{a.role} pass over the integrated branch"),
        "DONE": a.done or ("the plan exists with units, options and questions" if a.role == "planner"
                           else "every check the plan lists for this part is green or explained"),
        "ROOT": root.as_posix(), "SKILL_DIR": SKILL_DIR.as_posix(), "WORKDIR": workdir,
        "WORKDIR_CMD": (root / worktree).as_posix() if worktree else root.as_posix(),
        "BRANCH": a.branch or (branch_name(run, a.task, unit, len(writer_units(ws, a.task))) if writer
                               else branch_name(run, a.task) if a.role in ("tester", "reviewer") else "(none)"),
        "SHA": a.sha or "(record the start SHA yourself: git rev-parse HEAD)",
        "WRITE_SET": a.write_set or {"planner": f".aizen/runs/{a.task}/plan.md, .aizen/runs/{a.task}/acceptance.md, docs/** (design docs, "
                                                f"when the project publishes them), .aizen/knowledge/**, .aizen/runs/{a.task}/reports/**",
                                     "reviewer": "none (read-only)"}.get(a.role, "the unit's paths in the plan — nothing outside"),
        "PORTS": a.ports or "pick a free range of 10 and record it in your report",
        "DB": re.sub(r"[^a-z0-9]+", "_", f"{a.task}_{unit}".lower()).strip("_"),
        "CHECK_UNIT": a.unit or a.role,
        "INPUTS": inputs, "A3": a.a3 or "none", "REPORT": report, "PACKS": packs, "CORE_DIR": core_dir.as_posix(),
        "GRAPH": code_map(root), "OPTIONAL": optional_tools(),
    }
    text = (SKILL_DIR / "assets" / "flow" / "agent-brief-template.md").read_text(encoding="utf-8")
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
    ps = {n: sub.add_parser(n) for n in ("init", "brief", "answer", "approve", "round", "status", "branch", "waves")}
    for p in ps.values():
        p.add_argument("--task", required=True)
        p.add_argument("--workspace", default=".")
    ps["init"].add_argument("--goal", required=True)
    ps["init"].add_argument("--backlog", help="the approved backlog item this run implements (BL-nn)")
    ps["init"].add_argument("--slug", help="business name of the change for the branch (default: from --goal)")
    ps["init"].add_argument("--type", choices=BRANCH_TYPES, default="feature", help="branch type (git.md §1)")
    ps["init"].add_argument("--ticket", help="a real ticket id (Jira, GitHub issue) for `Refs:` in commits — not the run id")
    ps["branch"].add_argument("--unit")
    ps["waves"].add_argument("--max", type=int, help="override parallel.max for this print")
    b = ps["brief"]
    b.add_argument("--role", choices=ROLES, required=True)
    b.add_argument("--kind", choices=KINDS, default="-")
    b.add_argument("--unit")
    b.add_argument("--stage", choices=STAGES, default="-", help="planner: discover | design | plan")
    b.add_argument("--lens", help="comma-separated, e.g. functional,ui (reviewer: redteam)")
    b.add_argument("--part", help="what this instance must deliver (default: its unit in the plan)")
    b.add_argument("--done", help="checkable done criterion")
    b.add_argument("--sha", help="start / pinned SHA")
    b.add_argument("--branch", help="default <type>/<slug>-<unit> for writers, <type>/<slug> for tester/reviewer (`branch`)")
    b.add_argument("--worktree", help="relative to the project root (default .aizen/worktrees/<TASK>-<unit> for writers)")
    b.add_argument("--write-set", dest="write_set", help="path globs this instance may write")
    b.add_argument("--ports", help="port range, e.g. 4100-4109")
    b.add_argument("--inputs", help="docs, contract version, finding ids, earlier reports")
    b.add_argument("--a3", help="the exact A3 actions the owner approved")
    ps["answer"].add_argument("--module", default="scope", help="plan part/module this answer settles")
    ps["answer"].add_argument("--text", required=True)
    ps["approve"].add_argument("--text", default="plan approved")
    ps["status"].add_argument("--set", choices=STATUSES)
    a = ap.parse_args(argv)
    for v in (a.task, getattr(a, "unit", None), getattr(a, "module", None)):
        if v and not ID.match(v):
            raise SystemExit(f"invalid id {v!r} — use letters, digits, . _ -")
    fn = {"init": cmd_init, "brief": cmd_brief, "answer": cmd_answer, "approve": cmd_approve, "round": cmd_round,
          "status": cmd_status, "branch": cmd_branch, "waves": cmd_waves}
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
            main(["init", *w, "--goal", "g", "--slug", "Giữ ghế tàu Tết"])
        expect_exit(["init", *w, "--goal", "g"], "exists")
        assert slugify("Đặt vé — giữ ghế 5 phút!") == "dat-ve-giu-ghe-5-phut" and slugify("x" * 40) == "x" * 32
        import subprocess
        if subprocess.run(["git", "init", "-q", tmp], capture_output=True).returncode == 0:
            assert exclude_local(Path(tmp)) == [".aizen/"] and exclude_local(Path(tmp)) == []
            assert ".aizen/" in Path(tmp, ".git", "info", "exclude").read_text(encoding="utf-8")
        expect_exit(["init", "--workspace", tmp, "--task", "../x", "--goal", "g"], "invalid id")
        expect_exit(["brief", *w, "--role", "dev", "--kind", "be", "--unit", "u1"], "not approved")
        expect_exit(["approve", *w], "nothing agreed")
        assert "UNIT=look" in brief("--role", "dev", "--kind", "ui", "--unit", "look")
        out = brief("--role", "planner", "--stage", "design")
        assert "STAGE=design" in out and "{{" not in out and "<" not in out.split("## Task")[1], out
        # roles' notes survive state.py rewrites
        sm = Path(tmp, ".aizen", "runs", "T-1", "state.md")
        sm.write_text(sm.read_text(encoding="utf-8") + "- planner: keep v1 endpoint\n", encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()):
            main(["answer", *w, "--module", "api", "--text", "B"])
        expect_exit(["brief", *w, "--role", "tester"], "not approved")
        expect_exit(["approve", *w], "no plan")
        plan = Path(tmp, ".aizen", "runs", "T-1", "plan.md")
        plan.write_text("# T-1\n## Scope\n## Module api — API\nFiles (write set): `src/api/**`\n"
                        "## Module ~~old~~ replaced by api\n"
                        "## Module `ui` — screen\nFiles (write set): `web/**`\n## Module measure\nFiles (write set): —\n"
                        "## Delivery\n", encoding="utf-8")
        assert writer_units(Path(tmp), "T-1") == ["api", "ui"]
        U = lambda i, w, after=(): {"id": i, "write": list(w), "after": list(after)}  # noqa: E731
        wv, nt = plan_waves([U("measure", []), U("api", ["src/api/**", "src/app.module.ts"], ["measure"]),
                             U("web", ["web/**"], ["measure"]), U("auth", ["src/app.module.ts"], ["measure"]),
                             U("deploy", ["deploy/**"], ["api"])], 2)
        assert wv == [["measure"], ["api", "web"], ["auth", "deploy"]], (wv, nt)
        assert any("auth after api" in n and "src/app.module.ts" in n for n in nt), nt
        assert plan_waves([U("a", ["x/**"]), U("b", ["y/**"]), U("c", ["z/**"])], 2)[0] == [["a", "b"], ["c"]]
        assert overlaps("src/**", "src/api/x.ts") and not overlaps("web/**", "src/**")
        assert overlaps("a.ts", "a.ts") and not overlaps("a.ts", "b.ts")
        for bad, needle in (([U("a", [], ["zz"])], "unknown unit zz"), ([U("a", [], ["b"]), U("b", [], ["a"])], "cycle")):
            try:
                plan_waves(bad, 2)
                raise AssertionError(needle)
            except SystemExit as e:
                assert needle in str(e.code), e.code
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            main(["waves", *w])
        assert "1: api ‖ ui" in out.getvalue() and "2: measure" in out.getvalue() and "parallel.max = 2" in out.getvalue(), out.getvalue()
        expect_exit(["approve", *w], "no acceptance cases")  # tests are agreed before the code exists
        acc = Path(tmp, ".aizen", "runs", "T-1", "acceptance.md")
        acc.write_text("| TC | AC |\n|---|---|\n| TC-01 | AC-1 |\n| TC-02 | AC-1 |\n", encoding="utf-8")
        expect_exit(["approve", *w], "scope, acceptance, ui, measure, delivery")  # every part confirmed before approval
        for part in ("scope", "acceptance", "ui", "measure", "delivery"):
            with contextlib.redirect_stdout(io.StringIO()):
                main(["answer", *w, "--module", part, "--text", "ok"])
        with contextlib.redirect_stdout(io.StringIO()):
            main(["approve", *w])
        st = sm.read_text(encoding="utf-8")
        assert "keep v1 endpoint" in st and "- api: B" in st and "plan approved" in st and "2 acceptance cases" in st, st
        assert len(load(Path(tmp), "T-1")["acceptance_sha"]) == 64
        expect_exit(["brief", *w, "--role", "dev", "--kind", "be"], "--unit")
        d1, d2 = brief("--role", "dev", "--kind", "be", "--unit", "u1"), brief("--role", "dev", "--kind", "fe", "--unit", "u2")
        assert "ROLE=dev KIND=be UNIT=u1" in d1 and "dev-u1.md" in d1 and "pr-body-u1.md" in d1
        rows = [line for line in d1.splitlines() if "{references,assets,scripts}/" in line]
        assert any("core" in r for r in rows) and any("flow" in r for r in rows), d1
        for line in rows:  # every pack folder printed in the brief exists
            assert Path(line.split("→")[1].strip()).is_dir(), line
        assert "/scripts/core/check.py" in d1 and "aizen-core" in d1, "quality gate must come from aizen-core"
        assert "Optional tools: archify" in d1, "brief names the optional community skills"
        assert "{eval}" not in d1 and "{authoring}" not in d1, "brief lists only the packs aizen-build requires"
        assert "BRANCH=feature/giu-ghe-tau-tet-u1" in d1.replace(" ", "") or "feature/giu-ghe-tau-tet-u1" in d1, d1
        assert ".aizen/worktrees/T-1-u1" in d1 and "dev-u2.md" in d2 and "\\" not in d1 and "T-1-u1`" not in d1
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            main(["branch", *w])
        assert out.getvalue().strip() == "feature/giu-ghe-tau-tet"
        assert branch_name({"v": 25}, "T-9", "api") == "feature/T-9-api" and branch_name({"v": 25}, "T-9") == "int/T-9"
        assert branch_name({"v": 26, "slug": "seat", "branch_type": "bugfix"}, "T", "api", writers=1) == "bugfix/seat"
        r2 = brief("--role", "reviewer", "--lens", "redteam")
        assert "review-redteam.md" in r2 and "READ-ONLY" in r2
        assert "Code map (ask before reading files): none" in r2
        Path(tmp, "graphify-out").mkdir()
        Path(tmp, "graphify-out", "graph.json").write_text("{}", encoding="utf-8")
        assert "graphify-out/graph.json\"" in brief("--role", "reviewer"), "brief must point at the code map"
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
