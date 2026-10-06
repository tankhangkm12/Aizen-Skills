# Team docs — one layout, written for people

`docs/` is what the team reads on GitHub: the product, the architecture, the API, the data, how to run it. It is
committed with the code. The agents' own working files stay in `.aizen/` (local, never committed): plans, runs,
journals, `decisions.md` and `lessons.md`.

## 1. Where a doc goes

```
docs/
├── README.md              the index: hand-written intro on top, the table below the marker is generated
├── product/               idea, requirements (SRS), user stories, scope, glossary, test plan
├── architecture/          architecture, system map, flows, security
│   ├── modules/<m>.md     one design doc per module (LLD)
│   └── adr/NNNN-<slug>.md decisions the team must know (context, options, decision, consequences)
├── api/                   <m>.md + <m>.yaml (OpenAPI) per module
├── data/                  data.md (ERD, main tables), <m>.md per module, ddl.sql, migrations notes
├── ui/                    <app>-frontend.md, <app>-ui.md, design tokens, exported screens
├── ops/                   infrastructure.md, environment.md (variables, no values), runbook.md, deploy
├── guides/                onboarding, how to run locally, contributing, how-tos
└── services/<svc>/        microservices only: overview.md, api.md + .yaml, database.md, infrastructure.md, modules/
```

Never guess a path: `uv run "<CORE_DIR>/scripts/core/docs.py" where <name> [--name <module|app|service>]`.
Names: `overview idea requirements test-plan system-map architecture flows security data infrastructure
module-design module-database module-api module-api-yaml app-frontend app-ui service-overview service-api
service-database service-infrastructure adr decisions lessons`.

The project chooses where design docs live, in `.aizen/config/guard.json`:

| `"docs"` | Design docs go to | Who has it |
|---|---|---|
| `"docs"` | `docs/` as above — committed, the team reads them | projects set up from aizen-core 26.2 |
| `"knowledge"` (or missing) | `.aizen/knowledge/system/`, `modules/<m>/`, `apps/<app>/` — local only | older projects, until they migrate |

`decisions.md` and `lessons.md` stay in `.aizen/knowledge/` in both modes. A decision the team must know (a
database, a protocol, a public contract, a security trade-off) also becomes an ADR in `docs/architecture/adr/`.

## 2. How a team doc reads

- First line `# Title` in the reader's terms ("Giữ ghế", not "seat-hold module LLD v2").
- Second paragraph: **one line** that says what this doc is and who it is for. The index shows it.
- Sections a reader can scan: the decision or the contract first, the reasoning after.
- File names lower-kebab-case; one topic per file; a folder's `README.md` only when the folder needs an intro.
- Links are relative and point inside the repository. Never link into `.aizen/` — nobody else has it. Copy the
  conclusion into the doc instead of linking the plan or a run report.
- No run ids, agent names or "the agent did …": the doc describes the product, not how it was made.
  Requirement and decision ids (`FR-03`, `AC-2`, `D-07`) are fine — they are part of the product's history.

## 3. Keep it true

| When | Do |
|---|---|
| a doc is added, renamed or its title/summary changes | `docs.py index` — refreshes the table in `docs/README.md` |
| before the PR of a run that touched docs | `docs.py check` — layout, titles, summaries, broken links, links into `.aizen/` |
| an older project, or a `docs/` folder grown by hand | `docs.py migrate` prints the moves (`.aizen/knowledge/` → `docs/`, loose files → a section, names → kebab-case); the owner reviews, then `docs.py migrate --apply` (uses `git mv`, sets `"docs": "docs"`) |

Moving the owner's own documents is the owner's call: show the `migrate` plan and wait for a yes.
