# Workspace — where things live (v21)

Everything Cecilia's roles write lives under `tensura/` at the workspace root (the project root unless
`CLAUDE.md`/`AGENTS.md` names another). `tensura/`, `.worktrees/` are local-only: add them to `.git/info/exclude`,
never stage them.

## 1. Layout

```
tensura/
├── docs/
│   ├── README.md · DECISIONS.md          index + status of each doc · D-nn decision log
│   ├── system/                           system-map, idea, requirements, architecture, security, test-plan, infrastructure
│   ├── modules/<module>/                 <module>-design.md (LLD) · <module>-database.md · <module>-api.md + .yaml
│   └── apps/<app>/                       <app>-frontend.md · <app>-ui.md · design-tokens.json · ui-exports/
├── plans/<TASK>.md                       the plan (planner)
├── conventions.md                        one page: naming, patterns, commands — read before the first edit
├── lessons.md                            L-nn lessons from past tasks
├── tasks/<TASK>/state.md · run.json      written by scripts/state.py — read first when resuming
├── reports/<TASK>/
│   ├── plan.md · dev-<unit>.md · test.md · review.md · devops.md
│   ├── pr-body[-<unit>].md               Draft PR text for `gh pr create --body-file` (one per unit; the
│   │                                     coordinator merges them into pr-body.md for the final PR)
│   └── evidence[-<unit>].json            written by scripts/check.py (always in the main checkout)
└── backups/<TASK>/                       DB dumps and copies taken before a change (git.md §4)
```

Microservices: `docs/services/<svc>/` holds `<svc>-overview.md`, `<svc>-api.md` + `.yaml`, `<svc>-database.md`,
`<svc>-infrastructure.md` and `modules/<module>/<module>-design.md`. Names are lower-kebab-case.

## 2. Logical names → paths (under `tensura/docs/`)

| Logical name | Monolith | Microservices |
|---|---|---|
| system map · idea · requirements · architecture · security · test plan | `system/<name>.md` | same |
| module design (LLD) | `modules/<m>/<m>-design.md` | `services/<svc>/modules/<m>/<m>-design.md` |
| database doc | `modules/<m>/<m>-database.md` | `services/<svc>/<svc>-database.md` |
| API contract | `modules/<m>/<m>-api.md` + `.yaml` | `services/<svc>/<svc>-api.md` + `.yaml` |
| frontend architecture · UI design | `apps/<app>/<app>-frontend.md` · `<app>-ui.md` | same |
| infrastructure doc | `system/infrastructure.md` | `services/<svc>/<svc>-infrastructure.md` |

An existing repo with its own docs folder keeps it; record the mapping in `tensura/conventions.md`.

## 3. Priority when sources conflict

```
Cecilia's direct instruction > docs > plan > repo conventions > these skills' defaults
```

Following the higher source is never silent: note the conflict in one line. A direct instruction that contradicts
docs on business logic, schema or a public contract → confirm once before acting.

## 4. Traceability IDs

| Prefix | Meaning | Created by |
|---|---|---|
| `FR` `NFR` `BR` `AC` | requirements, rules, acceptance criteria | planner (discover) |
| `SCR` `CMP` | screen, frontend component | planner (design) or dev (ui), whoever first |
| `EP` · `THR` `CTL` | endpoint/event · threat, control | planner (design) |
| `TC` `BUG` | test case, bug | tester |
| `F` | review finding | reviewer |
| `D` | decision | whoever records it in `DECISIONS.md` |
| `U` `X` `R` | unknown, contradiction, risk in as-built docs | planner (discover) |
| `L` | lesson | any role |

IDs are never renumbered once published; retire with `~~FR-07~~ removed D-12`.
