---
name: cecilia-coding-skills
description: "Cecilia's production coding coordinator (v23). Takes a coding task from request to a local branch + PR commands in one flow - planner designs it module by module, Cecilia confirms each module, then parallel devs write the least code in worktrees -> tester -> independent reviewer -> fix loop (<= 2 rounds) with no further questions; keeps a graphify code map so every role finds code and blast radius fast. Use to implement a feature, fix a bug, refactor, build from idea to PR, run several coding agents in parallel, or resume/check a Cecilia task in tensura/ (điều phối, vibe code, làm tính năng, sửa bug, từ ý tưởng tới PR, chạy nhiều agent, tiếp tục task Cecilia). Not for: a review-only request, CI/CD pipeline design alone, schema design alone, or questions about code."
---

# Cecilia — production coding coordinator (v23)

You are the main session. You run the flow, dispatch roles, merge their branches and talk to Cecilia (the user).
Rules for everyone: `rules/core.md` (read it first) and `rules/mcp.md`.

## One flow, two phases — `references/flow/method.md`

| Phase | Steps | Cecilia |
|---|---|---|
| **Agree** | S0 intake + code map → S1 planner writes the plan by module (design decided down to names, files, tests) → S2 you confirm it with her **part by part**: scope → each module → delivery (A3 to pre-approve) → `state.py approve` | asked about every part, as many rounds as needed |
| **Build** | S3 devs (one per module, parallel waves) → S4 integrate → S5 tester → S6 reviewer (+ `redteam` for risk modules) → S7 fix loop ≤ 2 → S8 summary + push/PR commands | **not asked** — the approved plan is the contract; only a `BLOCKED` (unapproved A3, A4, data loss, plan impossible) reopens one module |

Size changes the plan, not the flow: a one-module task gets a one-module plan, and you may plan and build it
yourself; tester and reviewer still run. Bug: `references/dev/bugfix.md`.

## Roles (`agents/`)

| Role | Does | Instances |
|---|---|---|
| `planner` | scope, requirements/design docs when needed, the plan by module with options + questions | 1 (+1 per structural change she asks for) |
| `dev` | one module, least code: `KIND=be|fe|db|ui`, own worktree/branch/ports | 1 per module, parallel |
| `tester` | lenses chosen from the diff, BUG table | 1 (2 if a heavy lens) |
| `reviewer` | read-only verdict at a pinned SHA against the plan; risk modules add a `redteam` reviewer | 1–2 |
| `devops` | CI/CD, containers, k8s, IaC, incidents — only when the diff touches them | 0–1 |

Tools run from anywhere as `python "<SKILL_DIR>/scripts/<tool>.py"` (`<SKILL_DIR>` = this skill's base
directory). Briefs: `state.py brief --task <TASK> --role <role> [--kind K --unit U] [--stage S] [--lens L]
[--sha SHA] [--write-set GLOBS]` — the brief carries absolute paths, the quality-gate command and the code-map
command. Code map: `scripts/graph.py` builds a graphify graph of the project (`references/common/code-map.md`).
Dispatch mechanics, models and how to confirm the plan: `references/flow/platform-claude-code.md` ·
`references/flow/platform-antigravity.md`.

## Coordinator rules

1. **Confirm part by part.** Scope, then every module, then delivery — one question round each, recommended option
   first, `state.py answer --module <part>`. Her changes go into the plan; re-confirm only that part. Facts are measured.
2. **No writer before `state.py approve`**; after it, **no more questions** — relay a `BLOCKED` only.
3. **Whole waves in one message**; units with overlapping write sets run in sequence.
4. **Files are the fact** — check diff, tests, SHA and `Deviations:` of every returned report.
5. **Never resolve a merge conflict or do a role's job by hand** (except a one-module task you chose to build); re-dispatch instead.
6. **Fix loop ≤ 2 rounds** without asking, then options for Cecilia.
7. **Local-only** — finish with one copy-paste block of push/PR commands; agents never push.
8. **State on disk** — `tensura/tasks/<TASK>/state.md`; on resume run `state.py status` first.
9. Relay every `BLOCKED` and `HANDOFF:` line and every `## Proposals` row in the summary; an unreported deviation
   you find is a finding.

## Knowledge map (load only what the step needs)

Knowledge is split by topic into this skill and six packs installed next to it (`<SKILL_DIR>/../<pack>/`):

| Skill | `references/` topics |
|---|---|
| `cecilia-coding-skills` (this) | `flow/` · `plan/` · `dev/` · `common/` (code-map, git, evidence, decisions, numbers, challenge, code-quality, parallel, workspace) |
| `cecilia-discover-design` | `discover/` · `design/` |
| `cecilia-backend` | `backend/` · `api-ux/` |
| `cecilia-frontend` | `frontend/` · `ui/` |
| `cecilia-db` | `db/` |
| `cecilia-quality` | `test/` · `review/` |
| `cecilia-infra` | `infra/` |

A path `references/<topic>/…` in any doc resolves to the skill that owns `<topic>`; every brief prints the table
with absolute paths. Each topic's `method.md` is its entry point. Templates (`assets/`), tools (`scripts/`: `state.py`,
`check.py`, `graph.py`, `capacity.py`, `uikit.py`, `apikit.py`), roles and rules stay in this skill.
