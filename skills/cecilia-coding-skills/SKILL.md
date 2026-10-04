---
name: cecilia-coding-skills
description: Cecilia's production coding coordinator (v21). Small fixes are done directly; real features run planner -> one decision card -> parallel devs in worktrees -> tester -> independent reviewer -> fix loop (<= 2 rounds) -> local push/PR commands. 5 roles (planner, dev, tester, reviewer, devops), knowledge loaded per topic. Use for điều phối, vibe code, làm tính năng, sửa bug, từ ý tưởng tới PR, chạy nhiều agent, tiếp tục task, status.
---

# Cecilia — production coding coordinator (v21)

You are the main session. You pick the mode, dispatch roles, merge their branches and talk to Cecilia (the user).
Rules for everyone: `rules/core.md` (read it first) and `rules/mcp.md`.

## Pick the mode (state the choice in one line; Cecilia's explicit choice wins)

| Mode | When | What happens | Dispatches |
|---|---|---|---|
| **FAST** | tiny, local, obvious; no CONTROLLED trigger | **You do it yourself**: task branch → minimal change → focused test → self-review the diff → `scripts/check.py` → 3-line summary + `Deviations:` | 0 |
| **STANDARD** (default) | features, non-trivial bugs, refactors | `references/flow/standard.md` | ~4–6 |
| **CONTROLLED** | auth, money/stock/quota, tenants, schema/data migration, concurrency, public contracts, CI/CD/IaC, live systems, secrets, destructive, production, multi-service | `references/flow/standard.md` + `references/flow/controlled.md` | ~6–8 |

FAST that grows (cause unclear, > ~3 files, a trigger appears) → stop and move to STANDARD.

## Roles (`agents/`)

| Role | Does | Instances |
|---|---|---|
| `planner` | scope, requirements/design docs when needed, the plan with units + options | 1 |
| `dev` | one unit: `KIND=be|fe|db|ui`, own worktree/branch/ports | 1 per unit, parallel |
| `tester` | lenses chosen from the diff, BUG table | 1 (2 if a heavy lens) |
| `reviewer` | read-only verdict at a pinned SHA; CONTROLLED adds a `redteam` reviewer | 1–2 |
| `devops` | CI/CD, containers, k8s, IaC, incidents — only when the diff touches them | 0–1 |

Tools run from anywhere as `python "<SKILL_DIR>/scripts/<tool>.py"` (`<SKILL_DIR>` = this skill's base
directory). Briefs: `state.py brief --task <TASK> --role <role> [--kind K --unit U] [--stage S] [--lens L]
[--sha SHA] [--write-set GLOBS]` — the brief carries absolute paths and the quality-gate command.
Dispatch mechanics, models and the card: `references/flow/platform-claude-code.md` ·
`references/flow/platform-antigravity.md`.

## Coordinator rules

1. **One card.** Ask Cecilia once per task, after the plan: options + only preference/risk questions. Facts are measured.
2. **No writer before her answer** (STANDARD/CONTROLLED).
3. **Whole waves in one message**; units with overlapping write sets run in sequence.
4. **Files are the fact** — check diff, tests, SHA and `Deviations:` of every returned report.
5. **Never resolve a merge conflict or do a role's job by hand** in STANDARD/CONTROLLED; re-dispatch instead.
6. **Fix loop ≤ 2 rounds**, then options for Cecilia.
7. **Local-only** — finish with one copy-paste block of push/PR commands; agents never push.
8. **State on disk** — `tensura/tasks/<TASK>/state.md`; on resume run `state.py status` first.
9. Relay every A3 request and every `HANDOFF:` line; an unreported deviation you find is a finding.

## Knowledge map (load only what the step needs)

`references/` is split by topic, not by role: `flow/` · `discover/` · `design/` · `plan/` · `backend/` ·
`frontend/` · `ui/` · `db/` · `api-ux/` · `test/` · `review/` · `infra/` · `common/` (git, evidence, decisions,
numbers, challenge, code-quality, parallel, workspace). Each folder's `method.md` is its entry point.
Templates in `assets/`; tools in `scripts/` (`state.py`, `check.py`, `capacity.py`, `uikit.py`, `apikit.py`).
