---
name: aizen-core
description: Shared core of the Aizen suite (v24) — authority levels A0–A4, evidence labels, decisions and options, git and local-only hand-off, code quality (least code, the reuse ladder), numbers and projections, workspace layout, the quality gate (check.py), the code map (graph.py) and capacity projections. Loaded by every Aizen skill through its brief or its "Read first" line; not a standalone skill, do not trigger it directly.
---

# Aizen core — the rules every Aizen skill shares (v24)

One copy of the rules that used to be repeated in every skill. Entry skills (`aizen-build`, `aizen-init`, …)
and knowledge packs point here instead of restating them.

**Read first:** `references/core/rules.md` — authority, questions, lanes, code, git, evidence, output.

## What lives here

| Need | Read / run |
|---|---|
| who may do what (A0–A4), when to ask, `BLOCKED` / `HANDOFF` | `references/core/rules.md` |
| options, recommendations, research before proposing | `references/core/decisions.md` |
| least code, the reuse ladder, size signals, `ponytail:` debt markers | `references/core/code-quality.md` |
| comments, functions, naming — language-independent style | `references/core/code-style.md` |
| evidence labels, report shape, numbers with sources | `references/core/evidence.md`, `references/core/numbers.md` |
| challenging an upstream artifact | `references/core/challenge.md` |
| branches, backups, rollback; local-only hand-off and PR text | `references/core/git.md`, `references/core/git-handoff.md` |
| where files live (`.aizen/`), source priority, vendored knowledge | `references/core/workspace.md` |
| MCP tools (context7, sequentialthinking) | `references/core/mcp.md` |
| code map: who calls what, blast radius | `references/core/code-map.md` → `scripts/core/graph.py` |
| quality gate: lint, types, build, tests, secrets, deps → evidence JSON | `scripts/core/check.py` |
| capacity, growth, contention projections | `scripts/core/capacity.py` |
| templates | `assets/core/pr-draft-template.md`, `assets/core/evidence-record.json` |

## Paths

Every Aizen path `references/<topic>/…`, `assets/<topic>/…` or `scripts/<topic>/…` belongs to the skill whose
`manifest.json` lists `<topic>` under `topics`. This pack owns `core`. Run scripts by absolute path:
`python "<CORE_DIR>/scripts/core/check.py" …` (`<CORE_DIR>` = this skill's folder; a brief prints it).
