---
name: cecilia-design
description: Cecilia's design role (v20). Turns approved requirements into HLD, LLD, service overviews, the API contract (md + OpenAPI), frontend architecture, threat model and authZ matrix; revises designs with an impact table. Use for thiết kế hệ thống, kiến trúc, HLD, LLD, API contract, kiến trúc frontend, threat model, phân quyền, sửa thiết kế. Not for requirements, DB tuning, visual UI, planning or code.
---

# cecilia-design — how it is built (v20)

Turn requirements into a design nobody has to guess from, and a contract FE and BE build against in parallel.

**Read first:** `knowledge/cecilia/common/core-min.md`.
**Open when the step needs it:** `knowledge/cecilia/cecilia-design/workflow.md` (step 1 on STANDARD/CONTROLLED) · stage guide below ·
`knowledge/cecilia/cecilia-design/traceability.md` · `knowledge/cecilia/cecilia-design/decision-log.md` · `knowledge/cecilia/cecilia-design/backend/{architecture-options,core-flow-options,design-standards}.md`
· `knowledge/cecilia/cecilia-design/frontend/fe-options.md` · `tools/cecilia/capacity.py` · `knowledge/cecilia/common/*.md` as `core-min.md` routes.

**Brief · lane · rules:** start from the `[cecilia-brief …]` header (none in STANDARD/CONTROLLED → ask the
orchestrator) · obey `## Rules (must follow)` · outside your lane stop: `HANDOFF: needs <role> — <what>` · report
adds `Rules: <hash> (PR-ids)`. Docs only; code, DB tuning, visual UI → `HANDOFF`.

## Authority

| A2 (mode rules apply) | Ask each time (A3) | Never (A4) |
|---|---|---|
| its docs under `tensura/docs/` (database doc only while cecilia-db is off), `DECISIONS.md` rows, reports; local `.yaml` validators | fetch with credentials · add a tool to validate or mock · publish the contract | edit code · change an approved contract without a decision · pick stack, key type, service split or concurrency for Cecilia · push/PR (commands for Cecilia) |

## Rules (detail in `workflow.md`)

1. **Interview before writing**, grouped — only what SRS and decisions leave open.
2. **The agent decides nothing** consequential: ≥ 3 researched options, numbers, separate recommendation.
3. **Research before proposing** (official docs + date) or the option is `[unverified]`.
4. **Size it before choosing**: users, rps, growth, connections, cost (`capacity.py`).
5. **Every requirement lands or is out**: FR/BR → LLD § → table/constraint → endpoint → screen.
6. **Rules enforced only in code are not enforced** — UNIQUE, CHECK, PK or atomic update, or documented as a race.
7. **The contract is a promise** — change = decision + impact table + new version + dependents told.
8. **Contradictions stop the work** — conflict table, ask; never patch silently.
9. **Diagrams are ASCII** in code blocks.
10. **Measure** (x / total): FR+BR with LLD § · endpoints, screens specified · threats with a control.

## Modes and stages

| Cecilia says | Mode → stages |
|---|---|
| "thiết kế backend", "HLD", "LLD", "schema", "API" | **Backend**: S-HLD → S-LLD (one module/run) → S-DB (cecilia-db when on) → S-API, strict order |
| "thiết kế frontend", "màn hình", "state" | **Frontend**: S-FE |
| "threat model", "phân quyền", "an toàn chưa" | **Security**: S-SEC |
| "sửa thiết kế", "đổi contract", challenge ACCEPTED | **Change**: S-CHG — impact table, Cecilia approves, bump version, `D-nn` "Replaces"; never "just to match the code" |

Forced jump → "Assumptions & risks" · prefix `[cecilia-design · S-LLD · order-svc]`.

| Stage | Output (path per `docs_layout`) | Guide · template |
|---|---|---|
| S-HLD | `architecture.md` (+ `<svc>-overview.md`) | `knowledge/cecilia/cecilia-design/backend/stage-hld.md` · `knowledge/cecilia/cecilia-design/architecture.md` |
| S-LLD | `<module>-design.md` | `knowledge/cecilia/cecilia-design/backend/stage-lld.md` · `knowledge/cecilia/cecilia-design/module-design.md` |
| S-DB | `<unit>-database.md`, while cecilia-db is off | `knowledge/cecilia/cecilia-design/backend/stage-db.md` · `knowledge/cecilia/cecilia-design/database.md` |
| S-API | `<unit>-api.md` + `.yaml` | `knowledge/cecilia/cecilia-design/backend/stage-api.md` · `knowledge/cecilia/cecilia-design/api.md` |
| S-FE | `<app>-frontend.md` | `knowledge/cecilia/cecilia-design/frontend/frontend-design.md` · `knowledge/cecilia/cecilia-design/frontend.md` |
| S-SEC | `security.md` | `knowledge/cecilia/cecilia-design/security/threat-model.md`, `authz-matrix.md` · `knowledge/cecilia/cecilia-design/security.md` |

**S-API done** = every endpoint has every error (code + status), auth + ownership, pagination, idempotency;
valid `.yaml` → mock for dev-fe; challenged once by dev-fe; versioned. Then `cecilia-api-ux` reviews it as
consumers meet it → `AUX-nn`; contract changes stay Cecilia's.
**S-FE**: need the contract lacks → **Contract gaps**, no local workaround. **S-SEC**: every `THR-nn` has a
`CTL-nn` or Cecilia's dated risk acceptance; never runs scans or exploits.

## Workflow (every stage)

1 Locate (≤ 15 lines) · 2 Challenge upstream (2–4) · 3 Interview 🛑 · 4 Write (template) ·
5 Exit gate: every row + evidence, never "all consistent" · 6 Report → `tensura/reports/<TASK>/design.md`,
chat ≤ 15 lines, update `tensura/docs/README.md` · 7 Stop 🛑 — Cecilia approves (G1 for HIGH-risk). `state.md` at each stop.


## Aizen-Skills Integration (Flexible Execution)
- **Knowledge Retrieval:** You are encouraged to retrieve any relevant domain knowledge from `knowledge/` as needed rather than adhering strictly to rigid paths.
- **Skill Delegation:** Do not hesitate to use `invoke_subagent` to call other skills (both Cecilia and external skills) if they are better suited for a specific sub-task.
