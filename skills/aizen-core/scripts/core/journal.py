#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""journal.py — the run's journal in plain words, and the hand-off file for the owner (v26).

    J=<CORE_DIR>/scripts/core/journal.py
    uv run $J note   --run R --kind think --text "Tôi đang nghĩ cách giữ ghế bằng khoá Redis 5 phút" [--as dev-seat]
    uv run $J note   --run R --kind try   --text "Tôi sẽ thử SET NX PX thay vì bảng lock"
    uv run $J show   --run R [--tail 30]
    uv run $J report [--run R]            # → .aizen/out/latest.md (+ history/), prints only the path

Journal = .aizen/runs/<RUN>/journal.md, one short line per entry:
    - 14:32 · dev-seat · 🧠 Tôi đang nghĩ cách giữ ghế bằng khoá Redis 5 phút
Agents write the thinking lines (think · try · decide · did · ask · stop) at decision points, not every step.
The hooks write the facts (✍ wrote · ▶ ran) from the ledger, so those lines cannot be forgotten or invented.

Hand-off = .aizen/out/latest.md: goal, status, what the owner must answer, open checks, the agent's summary
(reports/summary.md), the last journal lines and the paths of the detailed files — written to be pasted
as-is into a web AI or read by a reviewer. Every report is also kept under .aizen/out/history/.
Python ≥ 3.9, standard library only.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

MAX_TEXT = 160
KINDS = {"think": "🧠", "try": "🔧", "decide": "🔀", "did": "✅", "ask": "❓", "stop": "⛔",
         "wrote": "✍", "ran": "▶"}
THINKING = ("think", "try", "decide")          # what the Stop gate looks for once files changed
AGENT_KINDS = ("think", "try", "decide", "did", "ask", "stop")
READ_ONLY = re.compile(r"^\s*(?:cd\s+\S+\s*&&\s*)?(ls|cat|head|tail|less|grep|rg|find|fd|pwd|echo|wc|tree|which|type|stat"
                       r"|git\s+(status|diff|log|show|branch|rev-parse|remote|fetch|ls-files|blame|worktree\s+list)"
                       r"|graphify\s+(query|explain|path|affected))\b")
TEXT = {
    "vi": {"wrote": "Đã ghi {files}", "ran_ok": "Đã chạy `{cmd}` → xong", "ran_bad": "Đã chạy `{cmd}` → lỗi",
           "title": "Nhật ký", "goal": "Mục tiêu", "status": "Trạng thái", "owner": "Cần bạn",
           "open": "Kiểm tra còn mở", "summary": "Agent tóm tắt", "recent": "Nhật ký gần nhất",
           "files": "File chi tiết", "none": "—", "paste": "Dán nguyên file này cho AI web hoặc người review.",
           "updated": "Cập nhật", "approved": "đã duyệt plan", "not_approved": "chưa duyệt plan",
           "round": "vòng sửa", "no_summary": "(chưa có — agent ghi reports/summary.md khi xong một chặng)"},
    "en": {"wrote": "Wrote {files}", "ran_ok": "Ran `{cmd}` → ok", "ran_bad": "Ran `{cmd}` → failed",
           "title": "Journal", "goal": "Goal", "status": "Status", "owner": "Needs you",
           "open": "Open checks", "summary": "Agent summary", "recent": "Latest journal",
           "files": "Detail files", "none": "—", "paste": "Paste this file as-is into a web AI or give it to a reviewer.",
           "updated": "Updated", "approved": "plan approved", "not_approved": "plan not approved",
           "round": "fix round", "no_summary": "(none yet — the agent writes reports/summary.md at the end of a stage)"},
}


# ── paths ────────────────────────────────────────────────────────────────────────────────────────────────

def find_ws(start: Path) -> Path | None:
    p = start.resolve()
    if ".aizen" in p.parts:
        p = Path(*p.parts[:p.parts.index(".aizen")])
    for d in (p, *p.parents):
        if (d / ".aizen").is_dir():
            return d
    return None


def run_dir(ws: Path, run: str) -> Path:
    live = ws / ".aizen" / "runs" / run
    old = ws / ".aizen" / "archive" / run
    return old if not live.exists() and old.exists() else live


def read_json(p: Path, default):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def lang(ws: Path) -> str:
    v = str(read_json(ws / ".aizen" / "config" / "guard.json", {}).get("lang", "vi")).lower()
    return v if v in TEXT else "vi"


def clock() -> str:
    return dt.datetime.now().strftime("%H:%M")


# ── journal ──────────────────────────────────────────────────────────────────────────────────────────────

def journal_path(ws: Path, run: str) -> Path:
    return run_dir(ws, run) / "journal.md"


def lines(ws: Path, run: str) -> list[str]:
    p = journal_path(ws, run)
    if not p.is_file():
        return []
    return [ln for ln in p.read_text(encoding="utf-8", errors="replace").splitlines() if ln.startswith("- ")]


def _append(ws: Path, run: str, who: str, kind: str, text: str) -> str:
    p = journal_path(ws, run)
    p.parent.mkdir(parents=True, exist_ok=True)
    head = ""
    if not p.is_file():
        goal = read_json(run_dir(ws, run) / "run.json", {}).get("goal", "")
        head = f"# {TEXT[lang(ws)]['title']} — {run}\n\n> {goal}\n\n"
    line = f"- {clock()} · {who or 'main'} · {KINDS[kind]} {' '.join(text.split())}"
    with p.open("a", encoding="utf-8") as f:
        f.write(head + line + "\n")
    return line


def note(ws: Path, run: str, kind: str, text: str, who: str = "main") -> str:
    """An entry the agent writes: one short sentence at a decision point."""
    if kind not in AGENT_KINDS:
        raise ValueError(f"--kind: one of {', '.join(AGENT_KINDS)}")
    text = " ".join(text.split())
    if not text:
        raise ValueError("--text is empty")
    if len(text) > MAX_TEXT:
        raise ValueError(f"keep it short: {len(text)} > {MAX_TEXT} characters — one sentence, the essentials")
    if not (run_dir(ws, run) / "run.json").is_file():
        raise ValueError(f"no run {run} in {ws / '.aizen'}")
    return _append(ws, run, who, kind, text)


def short_cmd(cmd: str) -> str:
    """`uv run --quiet --script "/abs/…/state.py" approve --task T` → `state.py approve --task T`."""
    c = " ".join(cmd.split())
    c = re.sub(r"^uv run(?:\s+--\S+)*\s+", "", c)
    c = re.sub(r"[\"']?(?:[A-Za-z]:)?[^\s\"']*/([^/\s\"']+\.py)[\"']?", r"\1", c)
    return c if len(c) <= 80 else c[:77] + "…"


def short_files(files: list[str]) -> str:
    names = [Path(f).name for f in files]
    seen = list(dict.fromkeys(names))
    return ", ".join(seen[:3]) + (f" +{len(seen) - 3}" if len(seen) > 3 else "")


def auto(ws: Path, run: str, who: str, files: list[str], cmd: str, failed: bool) -> str | None:
    """A fact line from a hook: what was written or run. Reads, journal calls and repeats are skipped."""
    t = TEXT[lang(ws)]
    files = [f for f in files if not re.search(r"(^|/)\.aizen/(runs|archive)/[^/]+/(journal\.md|ledger\.jsonl)$", f)]
    if files:
        kind, text = "wrote", t["wrote"].format(files=short_files(files))
    elif cmd and not READ_ONLY.search(cmd) and "journal.py" not in cmd:
        kind, text = "ran", (t["ran_bad"] if failed else t["ran_ok"]).format(cmd=short_cmd(cmd))
    else:
        return None
    last = lines(ws, run)
    if last and last[-1].split(" · ", 1)[-1] == f"{who or 'main'} · {KINDS[kind]} {text}":
        return None
    return _append(ws, run, who, kind, text)


def thinking(ws: Path, run: str) -> int:
    """How many lines the agents wrote themselves at decision points."""
    marks = tuple(KINDS[k] for k in THINKING)
    return sum(1 for ln in lines(ws, run) if ln.split(" · ", 2)[-1].startswith(marks))


# ── the hand-off file ────────────────────────────────────────────────────────────────────────────────────

def latest_run(ws: Path) -> str | None:
    found = []
    for sub in ("runs", "archive"):
        for rj in (ws / ".aizen" / sub).glob("*/run.json"):
            found.append((rj.stat().st_mtime, rj.parent.name))
    return max(found)[1] if found else None


def open_checks(rd: Path) -> list[str]:
    sheet = rd / "sheet.md"
    if not sheet.is_file():
        return []
    return [f"- {c[1].strip()}: {c[3].strip()}" for c in
            (ln.split("|") for ln in sheet.read_text(encoding="utf-8", errors="replace").splitlines())
            if len(c) > 4 and "❌" in c[2]]


def report(ws: Path, run: str | None = None) -> Path:
    """Write .aizen/out/latest.md and a dated copy in .aizen/out/history/; return the path of latest.md."""
    run = run or latest_run(ws)
    if not run:
        raise ValueError("no run under .aizen/ yet")
    rd = run_dir(ws, run)
    r = read_json(rd / "run.json", {})
    t = TEXT[lang(ws)]
    rel = lambda p: p.relative_to(ws).as_posix()  # noqa: E731
    status = r.get("status", "?")
    bits = [status]
    if r.get("skill") == "aizen-build":
        bits.append(t["approved"] if r.get("decision") else t["not_approved"])
        bits.append(f"{t['round']} {r.get('round', 0)}/2")
    owner = r.get("question") or (r.get("log", [""])[-1] if status == "blocked" else "") or t["none"]
    summary = rd / "reports" / "summary.md"
    files = [rd / n for n in ("plan.md", "acceptance.md", "sheet.md", "journal.md", "state.md") if (rd / n).is_file()]
    files += sorted((rd / "reports").glob("*.md")) if (rd / "reports").is_dir() else []
    out = [f"# {run} — {status} · {ws.resolve().name}",
           f"_{t['updated']}: {dt.datetime.now():%Y-%m-%d %H:%M} · {r.get('skill', '')} · {t['paste']}_", "",
           f"## {t['goal']}", r.get("goal", t["none"]), "",
           f"## {t['status']}", " · ".join(bits), f"**{t['owner']}:** {owner}", "",
           f"## {t['open']}", *(open_checks(rd) or [t["none"]]), "",
           f"## {t['summary']}",
           summary.read_text(encoding="utf-8", errors="replace").strip() if summary.is_file() else t["no_summary"], "",
           f"## {t['recent']}", *(lines(ws, run)[-20:] or [t["none"]]), "",
           f"## {t['files']}", *[f"- `{rel(f)}`" for f in files]]
    text = "\n".join(out).rstrip() + "\n"
    d = ws / ".aizen" / "out"
    (d / "history").mkdir(parents=True, exist_ok=True)
    (d / "latest.md").write_text(text, encoding="utf-8")
    (d / "history" / f"{dt.datetime.now():%Y%m%d-%H%M}-{run}.md").write_text(text, encoding="utf-8")
    return d / "latest.md"


def report_quiet(ws: Path, run: str) -> None:
    """For the scripts: refresh the hand-off file, never break the caller."""
    try:
        report(ws, run)
    except Exception as e:  # noqa: BLE001
        print(f"(.aizen/out/latest.md not written: {e})", file=sys.stderr)


# ── CLI ──────────────────────────────────────────────────────────────────────────────────────────────────

def main(argv=None) -> int:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("note")
    n.add_argument("--run", "--task", dest="run", required=True)
    n.add_argument("--kind", choices=AGENT_KINDS, required=True)
    n.add_argument("--text", required=True)
    n.add_argument("--as", dest="who", default="main", help="your role, e.g. planner, dev-<unit>, tester")
    s = sub.add_parser("show")
    s.add_argument("--run", "--task", dest="run", required=True)
    s.add_argument("--tail", type=int, default=30)
    r = sub.add_parser("report")
    r.add_argument("--run", "--task", dest="run")
    for q in (n, s, r):
        q.add_argument("--workspace", default=".")
    a = ap.parse_args(argv)
    ws = find_ws(Path(a.workspace))
    if ws is None:
        print(f"no .aizen/ at or above {Path(a.workspace).resolve()} — run guard.py install first", file=sys.stderr)
        return 2
    try:
        if a.cmd == "note":
            print(note(ws, a.run, a.kind, a.text, a.who))
        elif a.cmd == "show":
            print("\n".join(lines(ws, a.run)[-a.tail:]) or "(empty)")
        else:
            p = report(ws, a.run)
            print(p.relative_to(ws).as_posix())
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return 2
    return 0


def _selfcheck() -> None:
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        ws = Path(tmp)
        rd = ws / ".aizen" / "runs" / "T-1"
        rd.mkdir(parents=True)
        (rd / "run.json").write_text(json.dumps({"run": "T-1", "skill": "aizen-build", "goal": "giữ ghế", "status": "building",
                                                 "decision": "ok", "round": 0}), encoding="utf-8")
        assert "🧠 Tôi đang nghĩ cách giữ ghế" in note(ws, "T-1", "think", "Tôi đang nghĩ  cách giữ ghế", "planner")
        for bad in (("think", "x" * 200), ("wrote", "x"), ("try", "  ")):
            try:
                note(ws, "T-1", *bad)
                raise AssertionError(bad)
            except ValueError:
                pass
        assert auto(ws, "T-1", "dev-a", ["src/a.py", "src/b.py"], "", False)
        assert auto(ws, "T-1", "dev-a", ["src/a.py", "src/b.py"], "", False) is None      # repeat skipped
        assert auto(ws, "T-1", "dev-a", [], "git status", False) is None                  # reads skipped
        assert auto(ws, "T-1", "dev-a", [], 'uv run journal.py note --run T-1', False) is None
        line = auto(ws, "T-1", "dev-a", [], 'uv run --quiet --script "/x/y/state.py" approve --task T-1', True)
        assert line and "`state.py approve --task T-1` → lỗi" in line, line
        assert auto(ws, "T-1", "dev-a", [".aizen/runs/T-1/journal.md"], "", False) is None
        assert thinking(ws, "T-1") == 1 and len(lines(ws, "T-1")) == 3
        (rd / "sheet.md").write_text("| Check | Result | Detail |\n|---|---|---|\n| test | ❌ | no reports/test*.md |\n"
                                     "| plan | ✅ | ok |\n", encoding="utf-8")
        p = report(ws)
        text = p.read_text(encoding="utf-8")
        assert "# T-1 — building" in text and "- test: no reports/test*.md" in text and "plan |" not in text
        assert "giữ ghế" in text and "đã duyệt plan" in text and "`.aizen/runs/T-1/journal.md`" in text
        assert len(list((p.parent / "history").glob("*-T-1.md"))) == 1
        (ws / ".aizen" / "config").mkdir()
        (ws / ".aizen" / "config" / "guard.json").write_text('{"lang": "en"}', encoding="utf-8")
        assert "Agent summary" in report(ws, "T-1").read_text(encoding="utf-8")
        assert find_ws(rd) == ws.resolve()
    print("journal.py self-check OK")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selfcheck"]:
        _selfcheck()
    else:
        sys.exit(main())
