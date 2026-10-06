#!/usr/bin/env python3
"""guard.py — enforce the aizen-build flow through agent hooks (v24).

The agent no longer decides when a task is finished: the harness asks this script.

    G=<SKILL_DIR>/scripts/flow/guard.py
    python $G install [--workspace .]          # Claude Code + Antigravity hooks + git pre-push, this project only
    python $G check   --task SHOP-42           # the checklist, as the Stop hook sees it (exit 0 pass, 1 open items)
    python $G waive   --task SHOP-42 --step check-docs --reason "docs-only module, no code to test" \
                      --evidence "git diff --stat: 2 files, docs/** only"   # or a file path (hashed)
    python $G hook pre|post|stop --agent claude|agy   # called by the harness, JSON payload on stdin
    python $G prepush                          # git pre-push: task branches only push when the checklist passes

What runs where:
  PreToolUse   deny writes to guard-owned files (run.json, ledger, waivers, evidence); deny code edits while the
               task's plan is not approved; deny writes in .worktrees/<unit>/ outside that unit's write set.
  PostToolUse  append every write / shell command to .aizen/tasks/<TASK>/ledger.jsonl (hash-chained).
  Stop         run the checklist of manifest.json `checklist`; open items → the agent must continue, with the
               exact list. Three stops in a row without new work (or 10 in total) → status `blocked`, stop
               allowed, the owner decides.
  pre-push     same checklist for branches int/<TASK> and feature/<TASK>-*.

The checklist asks for enough, never for more, and every item is proven by an artifact someone other than the
author checks: check.py evidence PASS at each module's tip and at int/<TASK> (the machine ran the commands), the
tester's and reviewer's reports written from their own sessions (the ledger is the witness, never the
coordinator), a PASS review of the current tip whose `path:line` citations exist at that SHA, no file changed
outside the approved write sets, pr-body.md at the end. A step that truly does not apply is waived with a reason
and evidence (a file is hashed), and counts only once the reviewer writes `waiver <id>: accepted`; `plan`,
`check-int` and `review` cannot be waived. Hooks fail open (an internal error never blocks the agent); pre-push fails closed.
Python ≥ 3.9, standard library only.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[2]  # <skill>/scripts/flow/guard.py
STATE_PY = SKILL_DIR / "scripts" / "flow" / "state.py"
LIVE = ("planning", "building", "testing", "reviewing", "fixing")
GATED = ("building", "testing", "reviewing", "fixing", "done")
MAX_IDLE, MAX_BLOCKS = 2, 10
PROTECTED = re.compile(r"(^|/)\.aizen/(tasks/[^/]+/(run\.json|ledger\.jsonl|guard\.json|waivers\.json)"
                       r"|reports/[^/]+/evidence[^/]*\.json)$")
PROTECTED_NAMES = ("run.json", "ledger.jsonl", "guard.json", "waivers.json", "evidence")
MUTATES = re.compile(r">|\btee\b|\bsed\s+-i|\brm\b|\bmv\b|\bcp\b|\btruncate\b|\bdd\b|write_text|open\(|Set-Content|Out-File|Remove-Item")
OWN_SCRIPTS = re.compile(r"(guard|state|check)\.py")
CLAUDE_WRITE = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
AGY_WRITE = re.compile(r"write|edit|replace|create|delete|remove|move|rename", re.I)
SHELL_TOOLS = {"Bash", "run_command", "run_terminal_command", "shell", "execute_command"}
SHA = re.compile(r"\b[0-9a-f]{7,40}\b")
VERDICT = re.compile(r"verdict\W{0,10}(PASS|CHANGES[_ ]REQUIRED|INCOMPLETE)", re.I)


# ── workspace, task files ────────────────────────────────────────────────────────────────────────────────

def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def find_ws(start: Path) -> Path | None:
    """The main checkout: the nearest folder holding .aizen/, also from inside .worktrees/<unit>/."""
    p = start.resolve()
    parts = p.parts
    if ".worktrees" in parts:
        p = Path(*parts[:parts.index(".worktrees")])
    for d in (p, *p.parents):
        if (d / ".aizen").is_dir():
            return d
    return None


def tdir(ws: Path, task: str) -> Path:
    return ws / ".aizen" / "tasks" / task


def read_json(p: Path, default):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def write_json(p: Path, data) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_name(f".{p.name}.{os.getpid()}.tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, p)


def tasks(ws: Path) -> dict[str, dict]:
    out = {}
    for rj in sorted((ws / ".aizen" / "tasks").glob("*/run.json")):
        run = read_json(rj, None)
        if isinstance(run, dict) and run.get("status"):
            out[rj.parent.name] = run
    return out


def guard_state(ws: Path, task: str) -> dict:
    return read_json(tdir(ws, task) / "guard.json", {})


def watched(ws: Path) -> dict[str, dict]:
    """Tasks the hooks look after: live ones, and `done` ones the guard saw being built but never passed."""
    out = {}
    for t, run in tasks(ws).items():
        g = guard_state(ws, t)
        if run["status"] in LIVE or (run["status"] == "done" and g and not g.get("passed")):
            out[t] = run
    return out


def checklist() -> list[dict]:
    return read_json(SKILL_DIR / "manifest.json", {}).get("checklist", [])


# ── the plan: modules and write sets ─────────────────────────────────────────────────────────────────────

MODULE = re.compile(r"^## Module\s+`?([A-Za-z0-9._-]+)`?(.*)$", re.M)
WRITE_SET = re.compile(r"^\s*Files\s*\(write set\)\s*:\s*(.+)$", re.M | re.I)
BASE = re.compile(r"Base:\s*`?([^`\s@]+)`?\s*@\s*`?([0-9a-f]{7,40})`?")
NONE = {"", "-", "—", "none", "n/a", "(none)"}


def plan(ws: Path, task: str) -> tuple[dict[str, list[str]], str | None]:
    """{module: write-set globs} (retired ~~id~~ modules excluded) and the base SHA of the plan header."""
    return plan_full(ws, task)[:2]


def plan_full(ws: Path, task: str) -> tuple[dict[str, list[str]], str | None, set[str]]:
    """plan() plus the modules of kind `ui` (UI design work may start before approval)."""
    p = ws / ".aizen" / "plans" / f"{task}.md"
    if not p.is_file():
        return {}, None, set()
    text = p.read_text(encoding="utf-8")
    heads = list(MODULE.finditer(text))
    modules, ui = {}, set()
    for i, m in enumerate(heads):
        body = text[m.end():heads[i + 1].start() if i + 1 < len(heads) else len(text)]
        body = body.split("\n## ", 1)[0]
        ws_line = WRITE_SET.search(body)
        raw = ws_line.group(1) if ws_line else ""
        globs = re.findall(r"`([^`]+)`", raw) or [g for g in re.split(r"[,\s]+", raw) if g]
        modules[m.group(1)] = [g.strip().lstrip("./") for g in globs if g.strip().lower() not in NONE]
        if re.search(r"\bkind\s+ui\b", m.group(2)):
            ui.add(m.group(1))
    base = BASE.search(text)
    return modules, base.group(2) if base else None, ui


def glob_rx(g: str) -> re.Pattern:
    out, i = "", 0
    while i < len(g):
        if g.startswith("**", i):
            out += ".*"
            i += 2
            if g.startswith("/", i):
                i += 1
                out += "/?" if not out.endswith("/?") else ""
        elif g[i] == "*":
            out += "[^/]*"
            i += 1
        elif g[i] == "?":
            out += "[^/]"
            i += 1
        else:
            out += re.escape(g[i])
            i += 1
    return re.compile(f"^{out}(/.*)?$" if not g.endswith("*") else f"^{out}$")


def in_set(path: str, globs: list[str]) -> bool:
    return any(glob_rx(g).match(path) for g in globs)


def local_only(path: str) -> bool:
    return path.startswith((".aizen/", ".worktrees/", ".git/"))


# ── git ──────────────────────────────────────────────────────────────────────────────────────────────────

def git(ws: Path, *args: str) -> str:
    try:
        r = subprocess.run(["git", "-C", str(ws), *args], capture_output=True, text=True, timeout=30)
        return r.stdout.strip() if r.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


def tip(ws: Path, branch: str) -> str:
    return git(ws, "rev-parse", "--verify", "--quiet", f"refs/heads/{branch}")


def changed(ws: Path, base: str, branch: str) -> list[str]:
    out = git(ws, "diff", "--name-only", f"{base}...{branch}")
    return [f for f in out.splitlines() if f]


# ── the checklist ────────────────────────────────────────────────────────────────────────────────────────

def show(ws: Path, rev: str, path: str) -> list[str] | None:
    """Lines of `path` at commit `rev` (the working tree when rev is empty); None when it does not exist there."""
    if rev:
        try:
            r = subprocess.run(["git", "-C", str(ws), "show", f"{rev}:{path}"], capture_output=True, timeout=30)
        except (OSError, subprocess.SubprocessError):
            return None
        return r.stdout.decode("utf-8", "replace").splitlines() if r.returncode == 0 else None
    f = ws / path
    return f.read_text(encoding="utf-8", errors="replace").splitlines() if f.is_file() else None


CITE = re.compile(r"(?<![\w/.-])((?:[\w.-]+/)*[\w.-]+\.[A-Za-z0-9]+):(\d+)(?:-(\d+))?\b")


def citations(text: str) -> list[tuple[str, int]]:
    """`path:line` references in a report (URLs and times like 10:30 excluded)."""
    out = []
    for m in CITE.finditer(text):
        path = m.group(1)
        if "://" in text[max(0, m.start() - 8):m.start()] or path.replace(".", "").isdigit():
            continue
        out.append((path.lstrip("./"), int(m.group(3) or m.group(2))))
    return out


def writers(ws: Path, task: str) -> tuple[dict[str, str], set[str]]:
    """{file: who wrote it last} and the set of writers of code files, from the ledger (hooks are the witness)."""
    last, code = {}, set()
    for e in ledger(ws, task):
        who = e.get("writer") or e.get("session", "")
        for f in e.get("files", []):
            last[f] = who
            if not local_only(f) or f.startswith(".worktrees/"):
                code.add(who)
        for name in re.findall(r"\.aizen/reports/[^\s'\"]+\.md", e.get("cmd", "")):
            if re.search(r">|\btee\b|Set-Content|Out-File|write_text", e["cmd"]):
                last[name] = who
    return last, code


def evaluate(ws: Path, task: str) -> tuple[list[str], list[str]]:
    """Open items and accepted waivers of one task. Empty open list = the task may finish."""
    run = tasks(ws).get(task)
    if run is None:
        return [f"no task {task} in {ws}"], []
    modules, base = plan(ws, task)
    reports = ws / ".aizen" / "reports" / task
    waivers = read_json(tdir(ws, task) / "waivers.json", {})
    coordinator = guard_state(ws, task).get("coordinator")
    unit_tip = {u: tip(ws, f"feature/{task}-{u}") for u in modules}
    int_tip = tip(ws, f"int/{task}")
    built = [t for t in unit_tip.values() if t]
    final_tip = int_tip or (built[0] if len(built) == 1 else "")
    last_writer, code_writers = writers(ws, task)
    review_text = "\n".join(f.read_text(encoding="utf-8", errors="replace") for f in sorted(reports.glob("review*.md")))
    open_items, waived = [], []

    def item(step_id: str, waivable: bool, problem: str) -> None:
        if waivable and step_id in waivers:
            waived.append(step_id)
        else:
            open_items.append(f"[{step_id}] {problem}")

    def evidence(sid: str, waivable: bool, path: Path, want_tip: str, cmd: str, what: str) -> None:
        ev = read_json(path, None)
        if not isinstance(ev, dict):
            item(sid, waivable, f"no evidence for {what} — run `{cmd}`")
        elif ev.get("result") != "pass":
            item(sid, waivable, f"{what}: check.py result is {str(ev.get('result')).upper()} — fix it, re-run `{cmd}`")
        elif want_tip and not (want_tip.startswith(str(ev.get("sha", ""))[:7]) and not ev.get("dirty")):
            item(sid, waivable, f"{what}: evidence is for {str(ev.get('sha'))[:7]}"
                 f"{' (dirty tree)' if ev.get('dirty') else ''}, branch tip is {want_tip[:7]} — commit, re-run `{cmd}`")

    for c in checklist():
        kind, cid, waivable = c.get("type"), c.get("id", ""), bool(c.get("waivable"))
        if c.get("when") == "done" and run["status"] != "done":
            continue
        if kind == "approved":
            if not run.get("decision"):
                item(cid, False, "plan not approved — confirm every part with the owner, then `state.py approve`")
            if not modules:
                item(cid, False, f"no `## Module` in .aizen/plans/{task}.md")
        elif kind == "evidence" and c.get("final"):
            if int_tip:  # several units merged: the integrated branch is proven by the machine, not by a report
                evidence(cid, waivable, reports / c["path"], int_tip,
                         f"check.py --task {task} --unit int` in the int/{task} worktree", f"int/{task}")
        elif kind == "evidence":
            for u, globs in modules.items():
                if globs:  # read-only module: nothing to check
                    evidence(cid.replace("{unit}", u), waivable, reports / c["path"].replace("{unit}", u),
                             unit_tip[u], f"check.py --task {task} --unit {u}` in its worktree", f"module {u}")
        elif kind == "report":
            files = sorted(reports.glob(c["glob"]))
            if not files:
                item(cid, waivable, f"no .aizen/reports/{task}/{c['glob']} — {c.get('hint', 'write it')}")
                continue
            texts = {f: f.read_text(encoding="utf-8", errors="replace") for f in files}
            if c.get("fresh") and final_tip:
                stale = [f.name for f, t in texts.items() if not any(final_tip.startswith(x) for x in SHA.findall(t))]
                if stale:
                    item(cid, waivable, f"{', '.join(stale)} do not name the current tip {final_tip[:7]} — "
                         "re-run that pass on the current SHA")
            if c.get("by"):
                for f in files:
                    key = f.relative_to(ws).as_posix()
                    who = last_writer.get(key)
                    if not coordinator:
                        item(cid, waivable, "who wrote the reports is unknown (no coordinator in the ledger) — "
                             "the task must start with `state.py init` while the guard hooks are installed")
                        break
                    if who is None:
                        item(cid, waivable, f"{f.name}: no ledger record of who wrote it — the {c['by']} writes it "
                             "with its file tool from its own session")
                    elif who == coordinator:
                        item(cid, waivable, f"{f.name} was written by the coordinator, not by an independent "
                             f"{c['by']} — dispatch the {c['by']}")
                    elif c.get("not_author") and who in code_writers:
                        item(cid, waivable, f"{f.name}: its author also wrote code in this task — "
                             f"dispatch a fresh {c['by']}")
            if c.get("verdict"):
                for f, t in texts.items():
                    v = VERDICT.findall(t)
                    got = v[-1].upper().replace(" ", "_") if v else "none"
                    if got != c["verdict"]:
                        nxt = ("fix loop: `state.py round`, re-dispatch the owning devs with the finding ids"
                               if run.get("round", 0) < 2 else
                               "fix-loop limit reached: `state.py status --set blocked` and give the owner options")
                        item(cid, waivable, f"{f.name}: verdict {got}, need {c['verdict']} — {nxt}")
            if c.get("citations"):
                for f, t in texts.items():
                    refs = citations(t)
                    if len(refs) < c["citations"]:
                        item(cid, waivable, f"{f.name}: no `path:line` evidence — every finding and every area "
                             "judged PASS cites the file and line it was read from")
                        continue
                    bad = []
                    for path, line in refs:
                        lines = show(ws, final_tip, path) if not path.startswith(".aizen/") else show(ws, "", path)
                        if lines is None or line < 1 or line > len(lines):
                            bad.append(f"{path}:{line}")
                    if bad:
                        item(cid, waivable, f"{f.name}: cited evidence not found at {final_tip[:7] or 'the tree'}: "
                             f"{', '.join(bad[:6])}{' …' if len(bad) > 6 else ''}")
        elif kind == "scope":
            union = [g for gs in modules.values() for g in gs]
            outside: set[str] = set()
            if base and git(ws, "rev-parse", "--verify", "--quiet", base + "^{commit}"):
                for u, t in unit_tip.items():
                    if t:
                        outside |= {f for f in changed(ws, base, t) if not local_only(f) and not in_set(f, modules[u])}
                if int_tip:
                    outside |= {f for f in changed(ws, base, int_tip) if not local_only(f) and not in_set(f, union)}
            for e in ledger(ws, task):
                for f in e.get("files", []):
                    m = re.match(r"^\.worktrees/([^/]+)/(.+)$", f)
                    if m and m.group(1) in modules and not in_set(m.group(2), modules[m.group(1)]):
                        outside.add(m.group(2))
                    elif not m and not local_only(f) and union and not in_set(f, union):
                        outside.add(f)
            if outside:
                shown = sorted(outside)
                item(cid, waivable, f"changed outside the approved write sets: {', '.join(shown[:8])}"
                     f"{' …' if len(shown) > 8 else ''} — revert them, or re-confirm the module with the owner")

    # a waiver counts only with its evidence intact and the reviewer's acceptance
    accepted = []
    for w in waived:
        rec = waivers.get(w, {})
        ev_path = rec.get("evidence_file")
        if ev_path:
            p = ws / ev_path
            if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest() != rec.get("sha256"):
                open_items.append(f"[waiver {w}] its evidence {ev_path} changed or is gone — waive again")
                continue
        m = re.findall(rf"waiver\s+`?{re.escape(w)}`?\s*:\s*\**\s*(accepted|rejected)", review_text, re.I)
        if not m:
            open_items.append(f"[waiver {w}] not judged by the reviewer — review.md needs `waiver {w}: accepted` "
                              "or `rejected` with a reason")
        elif m[-1].lower() == "rejected":
            open_items.append(f"[waiver {w}] rejected by the reviewer — do the step")
        else:
            accepted.append(f"{w}: {rec.get('reason', '')}")
    if accepted and run["status"] == "done":
        body = reports / "pr-body.md"
        text = body.read_text(encoding="utf-8") if body.is_file() else ""
        missing = [w.split(":")[0] for w in accepted if w.split(":")[0] not in text]
        if missing:
            open_items.append(f"[waivers] list the waived steps in pr-body.md (## Waived): {', '.join(missing)}")
    return open_items, accepted


# ── ledger ───────────────────────────────────────────────────────────────────────────────────────────────

def ledger(ws: Path, task: str) -> list[dict]:
    p = tdir(ws, task) / "ledger.jsonl"
    if not p.is_file():
        return []
    out = []
    for line in p.read_text(encoding="utf-8").splitlines():
        try:
            out.append(json.loads(line))
        except ValueError:
            continue
    return out


def append(ws: Path, task: str, entry: dict) -> None:
    p = tdir(ws, task) / "ledger.jsonl"
    prev = ""
    if p.is_file():
        lines = p.read_text(encoding="utf-8").splitlines()
        prev = hashlib.sha256(lines[-1].encode()).hexdigest()[:16] if lines else ""
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps({**entry, "prev": prev}, ensure_ascii=False) + "\n")


# ── hook payloads ────────────────────────────────────────────────────────────────────────────────────────

def rel(ws: Path, f: str, cwd: Path) -> str:
    p = Path(f)
    p = p if p.is_absolute() else cwd / p
    try:
        return p.resolve().relative_to(ws.resolve()).as_posix()
    except ValueError:
        return p.as_posix()


def parse(agent: str, payload: dict) -> dict:
    """Normalise a Claude Code or Antigravity payload: session, cwd, tool, written files, shell command."""
    if agent == "claude":
        tool = payload.get("tool_name", "")
        args = payload.get("tool_input") or {}
        session = payload.get("session_id", "")
        writer = session + (f"/{payload['agent_id']}" if payload.get("agent_id") else "")
        cwd = payload.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
        writes = tool in CLAUDE_WRITE
        files = [args[k] for k in ("file_path", "notebook_path") if isinstance(args.get(k), str)]
    else:
        call = payload.get("toolCall") or {}
        tool = call.get("name", "")
        args = call.get("args") or {}
        session = payload.get("conversationId", "")
        writer = session  # an Antigravity sub-agent runs in its own conversation
        paths = payload.get("workspacePaths") or []
        cwd = args.get("Cwd") or (paths[0] if paths else os.getcwd())
        writes = bool(AGY_WRITE.search(tool)) and tool not in SHELL_TOOLS
        files = []
        for k, v in args.items():
            if re.search(r"file|path|target", k, re.I) and k.lower() not in ("cwd",):
                files += [v] if isinstance(v, str) else [x for x in v if isinstance(x, str)] if isinstance(v, list) else []
    cmd = ""
    for k in ("command", "CommandLine", "commandLine", "cmd"):
        if isinstance(args.get(k), str):
            cmd = args[k]
    return {"tool": tool, "session": session, "writer": writer, "cwd": Path(cwd), "writes": writes, "files": files, "cmd": cmd,
            "error": str(payload.get("error") or "")[:200]}


def deny_reason(ws: Path, ev: dict, files: list[str]) -> str | None:
    if ev["writes"] and any(PROTECTED.search(f) for f in files):
        return ("guard-owned file (run.json, ledger, waivers, evidence): only state.py, guard.py and check.py write "
                "it — run the script instead")
    cmd = ev["cmd"]
    if cmd and not OWN_SCRIPTS.search(cmd) and any(n in cmd for n in PROTECTED_NAMES) and ".aizen" in cmd \
            and MUTATES.search(cmd):
        return "this command would change a guard-owned file under .aizen/ — use state.py, guard.py or check.py"
    if not ev["writes"]:
        return None
    code = [f for f in files if not local_only(f) or f.startswith(".worktrees/")]
    if not code:
        return None
    runs = watched(ws)
    for t, run in runs.items():
        modules, _, ui = plan_full(ws, t)
        early = [f for f in code if not any(f.startswith(f".worktrees/{u}/") for u in ui)]
        if run["status"] == "planning" and not run.get("decision") and early:
            return (f"task {t}: the plan is not approved — no code before `state.py approve` "
                    "(confirm scope, every module and delivery with the owner first; an abandoned task: "
                    f"`state.py status --task {t} --set stopped`)")
        for f in code:
            m = re.match(r"^\.worktrees/([^/]+)/(.+)$", f)
            if m and m.group(1) in modules and modules[m.group(1)] and not in_set(m.group(2), modules[m.group(1)]):
                return (f"{m.group(2)} is outside the write set of module {m.group(1)} "
                        f"({', '.join(modules[m.group(1)])}) — list the change under HANDOFF: in your report, "
                        "or return BLOCKED if the module cannot be done without it")
    cfg = read_json(ws / ".aizen" / "guard.json", {})
    if cfg.get("require_task") and not any(r.get("decision") for r in runs.values()):
        return ("this project requires an approved Aizen task before code changes (.aizen/guard.json "
                "require_task) — start one with the aizen-build skill")
    return None


def hook(event: str, agent: str, payload: dict) -> tuple[dict | None, str]:
    """→ (JSON to print or None, log line). Never raises past main(): a broken guard must not brick the agent."""
    ev = parse(agent, payload)
    ws = find_ws(ev["cwd"])
    if ws is None:
        return None, "no .aizen/"
    files = [rel(ws, f, ev["cwd"]) for f in ev["files"]]

    if event == "pre":
        reason = deny_reason(ws, ev, files)
        if not reason:
            return None, "allow"
        reason = "Aizen guard: " + reason
        if agent == "claude":
            return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                           "permissionDecisionReason": reason}}, reason
        return {"decision": "deny", "reason": reason}, reason

    if event == "post":
        if not (ev["writes"] or ev["cmd"]):
            return None, "skip"
        init = re.search(r"state\.py[\"']?\s+init\b.*--task[= ]([A-Za-z0-9._-]+)", ev["cmd"])
        for t in watched(ws):
            append(ws, t, {"ts": now(), "agent": agent, "session": ev["session"], "writer": ev["writer"],
                           "tool": ev["tool"],
                           "files": files if ev["writes"] else [], "cmd": ev["cmd"][:300], "error": ev["error"]})
            if init and init.group(1) == t:
                g = guard_state(ws, t)
                g.setdefault("coordinator", ev["writer"])
                write_json(tdir(ws, t) / "guard.json", g)
        return None, "recorded"

    # stop
    blocks = []
    for t, run in watched(ws).items():
        g = guard_state(ws, t)
        if g.get("coordinator") and ev["writer"] and g["coordinator"] != ev["writer"]:
            continue  # a role's sub-agent stopping, not the coordinator
        if run["status"] not in GATED:
            continue  # planning: asking the owner is the job
        open_items, _ = evaluate(ws, t)
        if not open_items:
            g.update(passed=run["status"] == "done", blocks=0, idle=0)
            write_json(tdir(ws, t) / "guard.json", g)
            continue
        size = len(ledger(ws, t))
        g["idle"] = g.get("idle", 0) + 1 if size == g.get("ledger_size", -1) else 0
        g.update(blocks=g.get("blocks", 0) + 1, ledger_size=size)
        if g["idle"] >= MAX_IDLE or g["blocks"] >= MAX_BLOCKS:
            escalate(ws, t, open_items)
            g.update(blocks=0, idle=0)
            write_json(tdir(ws, t) / "guard.json", g)
            continue
        write_json(tdir(ws, t) / "guard.json", g)
        blocks.append(message(t, open_items))
    if not blocks:
        return None, "stop allowed"
    reason = "\n\n".join(blocks)
    return ({"decision": "block", "reason": reason} if agent == "claude"
            else {"decision": "continue", "reason": reason}), reason


def message(task: str, open_items: list[str]) -> str:
    g = Path(__file__).resolve().as_posix()
    s = STATE_PY.as_posix()
    return (f"Aizen guard: task {task} is not finished — do not stop yet. Open items:\n"
            + "\n".join(f"- {i}" for i in open_items)
            + "\nDo exactly these, nothing more. A step that truly does not apply: "
              f'python "{g}" waive --task {task} --step <id> --reason "<why>" (logged, shown to the owner). '
              f'Blocked on the owner (A3/A4, plan impossible): python "{s}" status --task {task} --set blocked, '
              "then report BLOCKED with one question.")


def escalate(ws: Path, task: str, open_items: list[str]) -> None:
    """Stop the loop: status blocked + log, so the owner sees it. Uses state.py's own writer when available."""
    run = read_json(tdir(ws, task) / "run.json", {})
    run["status"] = "blocked"
    run.setdefault("log", []).append(f"{dt.datetime.now().isoformat(timespec='seconds')} guard: stopped retrying, "
                                     f"open: {'; '.join(open_items)[:500]}")
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("aizen_state", STATE_PY)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.save(ws, task, run)
    except Exception:  # noqa: BLE001 — fall back to the machine file only
        write_json(tdir(ws, task) / "run.json", run)


# ── commands ─────────────────────────────────────────────────────────────────────────────────────────────

def cmd_check(ws: Path, task: str) -> int:
    open_items, waived = evaluate(ws, task)
    for w in waived:
        print(f"waived  {w}")
    for i in open_items:
        print(f"OPEN    {i}")
    print(f"{task}: {'PASS' if not open_items else f'{len(open_items)} open item(s)'}")
    return 0 if not open_items else 1


def cmd_waive(ws: Path, task: str, step: str, reason: str, evidence: str) -> int:
    ids = {c["id"] for c in checklist()}
    fixed = {c["id"] for c in checklist() if not c.get("waivable")}
    base_id = re.sub(r"-[A-Za-z0-9._]+$", "-{unit}", step) if step not in ids else step
    if step in fixed or base_id in fixed:
        print(f"{step} cannot be waived", file=sys.stderr)
        return 2
    if step not in ids and base_id not in ids:
        print(f"unknown step {step} — one of: {', '.join(sorted(ids - fixed))}", file=sys.stderr)
        return 2
    if len(reason.strip()) < 15:
        print("give a real reason (≥ 15 characters)", file=sys.stderr)
        return 2
    if not (tdir(ws, task) / "run.json").is_file():
        print(f"no task {task}", file=sys.stderr)
        return 2
    rec = {"reason": reason.strip(), "ts": now()}
    f = ws / evidence
    if evidence and f.is_file():
        rec.update(evidence_file=f.resolve().relative_to(ws.resolve()).as_posix(),
                   sha256=hashlib.sha256(f.read_bytes()).hexdigest())
    elif len(evidence.strip()) >= 10:
        rec["evidence"] = evidence.strip()  # one line of real output, a commit, a hash
    else:
        print("--evidence: a file in the project (hashed) or one line of real output/commit/hash (≥ 10 characters)",
              file=sys.stderr)
        return 2
    p = tdir(ws, task) / "waivers.json"
    w = read_json(p, {})
    w[step] = rec
    write_json(p, w)
    print(f"waived {step} — counts once the reviewer writes `waiver {step}: accepted`; list it under "
          "'## Waived' in pr-body.md")
    return 0


def cmd_prepush(ws: Path, stdin: str) -> int:
    names = set(tasks(ws))
    failed = 0
    for line in stdin.splitlines():
        parts = line.split()
        if len(parts) < 2 or set(parts[1]) == {"0"}:
            continue  # deleting a branch
        ref = parts[0].replace("refs/heads/", "")
        task = None
        if ref.startswith("int/") and ref[4:] in names:
            task = ref[4:]
        elif ref.startswith("feature/"):
            task = max((n for n in names if ref[8:].startswith(n + "-")), key=len, default=None)
        if not task:
            continue
        run = tasks(ws)[task]
        open_items, _ = evaluate(ws, task)
        if run["status"] != "done":
            open_items.insert(0, f"[status] task is {run['status']}, not done")
        if open_items:
            failed += 1
            print(f"Aizen guard: {ref} not pushed — task {task}:\n" + "\n".join(f"  - {i}" for i in open_items),
                  file=sys.stderr)
    return 1 if failed else 0


def cmd_install(ws: Path) -> int:
    ws = ws.resolve()
    me = Path(__file__).resolve().as_posix()
    py = Path(sys.executable).as_posix()
    call = lambda ev, agent: f'"{py}" "{me}" hook {ev} --agent {agent}'  # noqa: E731

    # Claude Code — settings.local.json: personal, absolute paths, never committed
    cp = ws / ".claude" / "settings.local.json"
    cs = read_json(cp, {})
    hooks = cs.setdefault("hooks", {})
    for event, matcher, ev in (("PreToolUse", "Write|Edit|MultiEdit|NotebookEdit|Bash", "pre"),
                               ("PostToolUse", "Write|Edit|MultiEdit|NotebookEdit|Bash", "post"),
                               ("Stop", None, "stop")):
        keep = [h for h in hooks.get(event, []) if not any("guard.py" in x.get("command", "") and " hook " in x.get("command", "")
                                                          for x in h.get("hooks", []))]
        entry = {"hooks": [{"type": "command", "command": call(ev, "claude"), "timeout": 60}]}
        if matcher:
            entry = {"matcher": matcher, **entry}
        hooks[event] = keep + [entry]
    write_json(cp, cs)

    # Antigravity — workspace .agents/hooks.json, one named group
    ap_ = ws / ".agents" / "hooks.json"
    ag = read_json(ap_, {})
    ag["aizen-guard"] = {
        "enabled": True,
        "PreToolUse": [{"matcher": "*", "hooks": [{"type": "command", "command": call("pre", "agy"), "timeout": 30}]}],
        "PostToolUse": [{"matcher": "*", "hooks": [{"type": "command", "command": call("post", "agy"), "timeout": 30}]}],
        "Stop": [{"hooks": [{"type": "command", "command": call("stop", "agy"), "timeout": 60}]}],
    }
    write_json(ap_, ag)
    (ws / ".aizen").mkdir(exist_ok=True)
    print(f"✓ Claude Code hooks → {cp}")
    print(f"✓ Antigravity hooks → {ap_}")

    # git: pre-push + keep the local-only files out of commits
    hooks_dir = git(ws, "rev-parse", "--path-format=absolute", "--git-path", "hooks")
    if not hooks_dir:
        print("· not a git repository — no pre-push hook")
        return 0
    common = git(ws, "rev-parse", "--path-format=absolute", "--git-common-dir")
    exclude = Path(common) / "info" / "exclude"
    have = exclude.read_text(encoding="utf-8").splitlines() if exclude.is_file() else []
    add = [e for e in (".aizen/", ".worktrees/", ".claude/settings.local.json", ".agents/hooks.json") if e not in have]
    if add:
        exclude.parent.mkdir(parents=True, exist_ok=True)
        with exclude.open("a", encoding="utf-8") as f:
            f.write(("\n" if have and have[-1] else "") + "\n".join(add) + "\n")
    pp = Path(hooks_dir) / "pre-push"
    script = f'#!/bin/sh\n# aizen-guard\nexec "{py}" "{me}" prepush --workspace "$(git rev-parse --show-toplevel)"\n'
    if pp.is_file() and "aizen-guard" not in pp.read_text(encoding="utf-8", errors="replace"):
        print(f"! {pp} exists and is not Aizen's — add this line to it yourself:\n  {script.splitlines()[-1]}")
    else:
        pp.parent.mkdir(parents=True, exist_ok=True)
        pp.write_text(script, encoding="utf-8")
        pp.chmod(0o755)
        print(f"✓ git pre-push → {pp}")
    return 0


def main(argv=None) -> int:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    h = sub.add_parser("hook")
    h.add_argument("event", choices=("pre", "post", "stop"))
    h.add_argument("--agent", choices=("claude", "agy"), required=True)
    for n in ("install", "check", "waive", "prepush"):
        p = sub.add_parser(n)
        p.add_argument("--workspace", default=".")
    sub.choices["check"].add_argument("--task", required=True)
    w = sub.choices["waive"]
    w.add_argument("--task", required=True)
    w.add_argument("--step", required=True)
    w.add_argument("--reason", required=True)
    w.add_argument("--evidence", required=True, help="file in the project (hashed) or one line of real output")
    a = ap.parse_args(argv)

    if a.cmd == "hook":
        try:
            raw = sys.stdin.read()
            out, _ = hook(a.event, a.agent, json.loads(raw) if raw.strip() else {})
        except Exception as e:  # noqa: BLE001 — fail open
            print(f"aizen guard error (allowed): {e}", file=sys.stderr)
            out = None
        if out is not None:
            print(json.dumps(out, ensure_ascii=False))
        elif a.agent == "agy":
            print("{}")  # Antigravity expects JSON on stdout
        return 0
    ws = Path(a.workspace)
    if a.cmd == "install":
        return cmd_install(ws)
    root = find_ws(ws)
    if a.cmd == "prepush":
        return cmd_prepush(root, sys.stdin.read()) if root else 0
    if root is None:
        print(f"no .aizen/ at or above {ws.resolve()}", file=sys.stderr)
        return 2
    if a.cmd == "check":
        return cmd_check(root, a.task)
    return cmd_waive(root, a.task, a.step, a.reason, a.evidence)


# ── self-check ───────────────────────────────────────────────────────────────────────────────────────────

def _selfcheck() -> None:
    import tempfile

    def sh(ws, *args):
        subprocess.run(["git", "-C", str(ws), "-c", "user.email=a@b", "-c", "user.name=a", *args],
                       check=True, capture_output=True)

    with tempfile.TemporaryDirectory() as tmp:
        ws = Path(tmp)
        sh(ws, "init", "-q", "-b", "main")
        (ws / "README.md").write_text("x")
        sh(ws, "add", ".")
        sh(ws, "commit", "-q", "-m", "base")
        base = git(ws, "rev-parse", "HEAD")
        T = "T-1"
        d = tdir(ws, T)
        d.mkdir(parents=True)
        write_json(d / "run.json", {"task": T, "goal": "g", "status": "planning", "round": 0, "agreed": {},
                                    "decision": None, "log": []})
        (ws / ".aizen" / "plans").mkdir(parents=True)
        (ws / ".aizen" / "plans" / f"{T}.md").write_text(
            f"# {T}\n> Plan v1 · Base: `main` @ `{base[:7]}`\n## Scope\n"
            "## Module api — API   kind be\nFiles (write set): `src/api/**`, `tests/api/**`\n"
            "## Module measure — read-only\nFiles (write set): —\n## Delivery\n", encoding="utf-8")
        c = lambda tool, inp, s="S1": {"session_id": s, "cwd": str(ws), "tool_name": tool, "tool_input": inp}  # noqa: E731

        # pre: no code before approval; plan files are fine; guard-owned files never
        out, _ = hook("pre", "claude", c("Edit", {"file_path": str(ws / "src/api/a.py")}))
        assert out and out["hookSpecificOutput"]["permissionDecision"] == "deny", out
        assert hook("pre", "claude", c("Write", {"file_path": str(ws / ".aizen/plans/T-1.md")}))[0] is None
        assert hook("pre", "claude", c("Edit", {"file_path": str(d / "run.json")}))[0]
        assert hook("pre", "claude", c("Bash", {"command": "echo {} > .aizen/reports/T-1/evidence-api.json"}))[0]
        assert hook("pre", "claude", c("Bash", {"command": "cat .aizen/tasks/T-1/ledger.jsonl"}))[0] is None
        agy = {"conversationId": "C1", "workspacePaths": [str(ws)],
               "toolCall": {"name": "write_to_file", "args": {"TargetFile": str(ws / "src/api/a.py")}}}
        assert hook("pre", "agy", agy)[0]["decision"] == "deny"

        # post: ledger + coordinator from `state.py init`
        hook("post", "claude", c("Bash", {"command": f'python "/x/state.py" init --task {T} --goal g'}))
        assert guard_state(ws, T)["coordinator"] == "S1" and len(ledger(ws, T)) == 1
        # stop while planning: allowed (asking the owner is the job)
        assert hook("stop", "claude", {"session_id": "S1", "cwd": str(ws)})[0] is None

        # approve → write set enforced inside worktrees
        run = read_json(d / "run.json", {})
        run.update(status="building", decision="ok")
        write_json(d / "run.json", run)
        assert hook("pre", "claude", c("Edit", {"file_path": str(ws / ".worktrees/api/src/api/a.py")}))[0] is None
        out, _ = hook("pre", "claude", c("Edit", {"file_path": str(ws / ".worktrees/api/src/billing/x.py")}))
        assert "write set of module api" in out["hookSpecificOutput"]["permissionDecisionReason"]

        # build the unit branch with one file outside its write set
        sh(ws, "checkout", "-q", "-b", f"feature/{T}-api")
        for f in ("src/api/a.py", "src/util/extra.py"):
            (ws / f).parent.mkdir(parents=True, exist_ok=True)
            (ws / f).write_text("x")
        sh(ws, "add", "src")
        sh(ws, "commit", "-q", "-m", "api")
        unit = git(ws, "rev-parse", "HEAD")
        sh(ws, "checkout", "-q", "main")

        # stop: open items → block (Claude) / continue (Antigravity), sub-agent sessions ignored
        out, why = hook("stop", "claude", {"session_id": "S1", "cwd": str(ws)})
        assert out["decision"] == "block" and "[check-api]" in why and "[review]" in why and "measure" not in why, why
        assert "src/util/extra.py" in why, why
        assert hook("stop", "claude", {"session_id": "SUB", "cwd": str(ws)})[0] is None
        hook("post", "claude", c("Bash", {"command": "ls"}))  # progress resets the idle counter
        assert hook("stop", "agy", {"conversationId": "S1", "workspacePaths": [str(ws)]})[0]["decision"] == "continue"

        # do the work: evidence at the tip; reports written by the roles' own sessions, with real citations
        rep = ws / ".aizen" / "reports" / T
        rep.mkdir(parents=True)
        write_json(rep / "evidence-api.json", {"result": "pass", "sha": unit[:12], "dirty": False})
        tester = {"session_id": "S1", "agent_id": "tst", "cwd": str(ws)}
        reviewer = {"session_id": "S1", "agent_id": "rev", "cwd": str(ws)}

        def report(who, name, text):
            (rep / name).write_text(text)
            hook("post", "claude", {**who, "tool_name": "Write", "tool_input": {"file_path": str(rep / name)}})

        report(tester, "test.md", f"all green @ {unit[:7]}")
        report({"session_id": "S1", "cwd": str(ws)}, "review.md", f"@ {unit[:7]} src/api/a.py:1\nVerdict: PASS\n")
        assert any("written by the coordinator" in i for i in evaluate(ws, T)[0]), evaluate(ws, T)[0]
        report(reviewer, "review.md", f"@ {unit[:7]} src/api/a.py:1\nVerdict: CHANGES_REQUIRED\n")
        assert any("verdict CHANGES_REQUIRED" in i for i in evaluate(ws, T)[0])
        report(reviewer, "review.md", f"Reviewed @ {unit[:7]}\nVerdict: PASS\n")
        assert any("no `path:line` evidence" in i for i in evaluate(ws, T)[0])
        report(reviewer, "review.md", f"Reviewed @ {unit[:7]}: src/api/a.py:1, src/api/a.py:99\nVerdict: PASS\n")
        assert any("src/api/a.py:99" in i for i in evaluate(ws, T)[0])
        dev = {"session_id": "S1", "agent_id": "dev1", "cwd": str(ws)}
        hook("post", "claude", {**dev, "tool_name": "Edit", "tool_input": {"file_path": str(ws / ".worktrees/api/src/api/a.py")}})
        report(dev, "review.md", f"Reviewed @ {unit[:7]}: src/api/a.py:1\nVerdict: PASS\n")
        assert any("also wrote code" in i for i in evaluate(ws, T)[0])
        report(reviewer, "review.md", f"Reviewed @ {unit[:7]}: src/api/a.py:1 (handler)\nVerdict: PASS\n")
        assert [i for i in evaluate(ws, T)[0] if not i.startswith("[scope]")] == [], evaluate(ws, T)[0]

        # waivers: never for review; need reason + evidence; count only once the reviewer accepts them
        assert cmd_waive(ws, T, "review", "the reviewer agreed it is fine", "x" * 12) == 2
        assert cmd_waive(ws, T, "scope", "short", "x" * 12) == 2
        assert cmd_waive(ws, T, "scope", "shared helper the owner asked for in chat", "ok") == 2
        (ws / ".aizen" / "owner-note.txt").write_text("owner: put the helper in src/util")
        assert cmd_waive(ws, T, "scope", "shared helper the owner asked for in chat", ".aizen/owner-note.txt") == 0
        assert any("not judged by the reviewer" in i for i in evaluate(ws, T)[0])
        report(reviewer, "review.md", f"@ {unit[:7]}: src/api/a.py:1\nwaiver scope: rejected — no\nVerdict: PASS\n")
        assert any("rejected by the reviewer" in i for i in evaluate(ws, T)[0])
        report(reviewer, "review.md", f"@ {unit[:7]}: src/api/a.py:1\nwaiver scope: accepted — owner note\nVerdict: PASS\n")
        assert evaluate(ws, T)[0] == [], evaluate(ws, T)[0]
        (ws / ".aizen" / "owner-note.txt").write_text("edited later")
        assert any("changed or is gone" in i for i in evaluate(ws, T)[0])
        (ws / ".aizen" / "owner-note.txt").write_text("owner: put the helper in src/util")
        assert hook("stop", "claude", {"session_id": "S1", "cwd": str(ws)})[0] is None
        assert hook("stop", "claude", {**reviewer})[0] is None

        # done: pr-body.md must exist and list the waivers; pre-push gates the task branch
        run["status"] = "done"
        write_json(d / "run.json", run)
        push = f"refs/heads/feature/{T}-api {unit} refs/heads/feature/{T}-api {'0' * 40}\n"
        assert cmd_prepush(ws, push) == 1
        (rep / "pr-body.md").write_text("## Waived\n- scope: shared helper\n")
        assert evaluate(ws, T)[0] == [] and cmd_prepush(ws, push) == 0
        assert cmd_prepush(ws, "refs/heads/other x refs/heads/other y\n") == 0

        # a stale evidence file (new commit after check.py) reopens the item
        sh(ws, "checkout", "-q", f"feature/{T}-api")
        (ws / "src/api/b.py").write_text("y")
        sh(ws, "add", "src")
        sh(ws, "commit", "-q", "-m", "more")
        sh(ws, "checkout", "-q", "main")
        assert any(i.startswith("[check-api]") and "branch tip" in i for i in evaluate(ws, T)[0])

        # several units merged → the integrated branch needs its own machine evidence (not waivable)
        sh(ws, "branch", f"int/{T}", f"feature/{T}-api")
        assert any(i.startswith("[check-int]") for i in evaluate(ws, T)[0])
        assert cmd_waive(ws, T, "check-int", "the units were already checked one by one", "x" * 12) == 2
        write_json(rep / "evidence-int.json", {"result": "pass", "sha": tip(ws, f"int/{T}"), "dirty": False})
        assert not any(i.startswith("[check-int]") for i in evaluate(ws, T)[0])
        sh(ws, "branch", "-D", f"int/{T}")

        # escalation: three stops in a row without new work → blocked, stop allowed
        run["status"] = "fixing"
        write_json(d / "run.json", run)
        write_json(d / "guard.json", {"coordinator": "S1"})
        for _ in range(2):
            assert hook("stop", "claude", {"session_id": "S1", "cwd": str(ws)})[0]["decision"] == "block"
        assert hook("stop", "claude", {"session_id": "S1", "cwd": str(ws)})[0] is None
        assert read_json(d / "run.json", {})["status"] == "blocked"

        # install writes both hook files and the pre-push hook, idempotently
        for _ in range(2):
            import contextlib
            import io
            with contextlib.redirect_stdout(io.StringIO()):
                cmd_install(ws)
        cs = read_json(ws / ".claude" / "settings.local.json", {})
        assert len(cs["hooks"]["Stop"]) == 1 and "hook stop --agent claude" in cs["hooks"]["Stop"][0]["hooks"][0]["command"]
        assert "aizen-guard" in read_json(ws / ".agents" / "hooks.json", {})
        assert (ws / ".git" / "hooks" / "pre-push").is_file()
        assert ".claude/settings.local.json" in (ws / ".git" / "info" / "exclude").read_text()
    assert glob_rx("src/api/**").match("src/api/x/y.py") and not glob_rx("src/api/**").match("src/apix.py")
    assert glob_rx("src/app.module.ts").match("src/app.module.ts") and glob_rx("web/*.ts").match("web/a.ts")
    print("guard.py self-check OK")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selfcheck"]:
        _selfcheck()
    else:
        sys.exit(main())
