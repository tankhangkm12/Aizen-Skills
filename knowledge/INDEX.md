# 📚 Bản Đồ Tri Thức (Knowledge Index)
> **Agent Instruction:** Read this file first to find the exact path of the domain knowledge you need. Do not brute-force read the entire knowledge directory.

| File Path | Description |
|-----------|-------------|
| `knowledge/cecilia/cecilia-api-ux/api-ux-report-template.md` | API experience report — <TASK> · <API/service> @ <contract version or SHA> |
| `knowledge/cecilia/cecilia-api-ux/challenges-template.md` | Challenge log — <TASK> |
| `knowledge/cecilia/cecilia-api-ux/consumer-journeys.md` | Consumer journeys — calls per task |
| `knowledge/cecilia/cecilia-api-ux/contention.md` | Contention — when correctness turns into rejection |
| `knowledge/cecilia/cecilia-api-ux/dx-checklist.md` | Developer experience checklist |
| `knowledge/cecilia/cecilia-api-ux/evolution.md` | Evolution — changing the contract without breaking consumers |
| `knowledge/cecilia/cecilia-api-ux/latency-failure.md` | Latency and failure — what the consumer waits for and what happens when it breaks |
| `knowledge/cecilia/cecilia-api-ux/method.md` | API experience review — method |
| `knowledge/cecilia/cecilia-db/backup-dr.md` | Backup, point-in-time recovery and disaster recovery |
| `knowledge/cecilia/cecilia-db/challenges-template.md` | Challenge log — <TASK> |
| `knowledge/cecilia/cecilia-db/concurrency.md` | Concurrency, isolation and hot rows |
| `knowledge/cecilia/cecilia-db/connections.md` | Connections, pools and timeouts |
| `knowledge/cecilia/cecilia-db/database.md` | <unit> — database |
| `knowledge/cecilia/cecilia-db/db-code.md` | Database-side code — procedures, functions, triggers, views, jobs |
| `knowledge/cecilia/cecilia-db/dr-runbook.md` | DR runbook — <database> · <environment> |
| `knowledge/cecilia/cecilia-db/engine-adr.md` | ADR-<nn>: Database for <workload> — <status: proposed | accepted | superseded> |
| `knowledge/cecilia/cecilia-db/engine-selection.md` | Choosing a database — by workload and mechanism, not by brand |
| `knowledge/cecilia/cecilia-db/engine-tuning.md` | Engine settings, instance size and replicas — from hardware up |
| `knowledge/cecilia/cecilia-db/growth-forecast.md` | Growth forecast — from business assumptions to "when does it break" |
| `knowledge/cecilia/cecilia-db/growth-report.md` | Growth forecast — <UNIT> · <TASK> · <date> |
| `knowledge/cecilia/cecilia-db/ha-replication.md` | High availability and replication |
| `knowledge/cecilia/cecilia-db/microservices-data.md` | Data across services |
| `knowledge/cecilia/cecilia-db/migrations.md` | Safe migrations — schema changes on tables with real data |
| `knowledge/cecilia/cecilia-db/partitioning-retention.md` | Growth, partitioning and retention — keep big tables cheap |
| `knowledge/cecilia/cecilia-db/performance.md` | Query performance — find the cause, change one thing, prove it |
| `knowledge/cecilia/cecilia-db/pr-draft-template.md` | 1. Context |
| `knowledge/cecilia/cecilia-db/scaling-ladder.md` | Scaling ladder — the lowest rung that holds, with a trigger for the next |
| `knowledge/cecilia/cecilia-db/scaling-options.md` | Scaling options — <UNIT> · <problem> · <date> |
| `knowledge/cecilia/cecilia-db/schema-design.md` | Schema design → `<unit>-database.md` (one module or service per run) |
| `knowledge/cecilia/cecilia-db/security-compliance.md` | Data security and privacy engineering |
| `knowledge/cecilia/cecilia-db/workflow.md` | cecilia-db — full rules and workflow |
| `knowledge/cecilia/cecilia-db/compliance/gdpr.md` | GDPR (EU/EEA data subjects) — engineering checklist |
| `knowledge/cecilia/cecilia-db/compliance/vn-pdpl.md` | Vietnam personal-data protection — engineering checklist |
| `knowledge/cecilia/cecilia-db/engines/mongodb.md` | MongoDB engine pack |
| `knowledge/cecilia/cecilia-db/engines/mysql.md` | MySQL (InnoDB) — engine notes |
| `knowledge/cecilia/cecilia-db/engines/postgresql.md` | PostgreSQL — engine notes |
| `knowledge/cecilia/cecilia-db/engines/_new-engine.md` | Adding an engine (MariaDB, SQL Server, Oracle, CockroachDB, Cassandra, …) |
| `knowledge/cecilia/cecilia-design/api.md` | <unit> — API contract |
| `knowledge/cecilia/cecilia-design/architecture.md` | Architecture (HLD) — <project> |
| `knowledge/cecilia/cecilia-design/challenges-template.md` | Challenge log — <TASK> |
| `knowledge/cecilia/cecilia-design/database.md` | <unit> — database |
| `knowledge/cecilia/cecilia-design/decision-log.md` | Decision log → `tensura/docs/DECISIONS.md` |
| `knowledge/cecilia/cecilia-design/frontend.md` | <app> — frontend architecture |
| `knowledge/cecilia/cecilia-design/module-design.md` | <module> — module design (LLD) |
| `knowledge/cecilia/cecilia-design/security.md` | Security — <system> |
| `knowledge/cecilia/cecilia-design/traceability.md` | Traceability |
| `knowledge/cecilia/cecilia-design/workflow.md` | cecilia-design — full rules and workflow |
| `knowledge/cecilia/cecilia-design/backend/architecture-options.md` | Architecture options (stage 2 and stage 3 structure) |
| `knowledge/cecilia/cecilia-design/backend/core-flow-options.md` | CORE flow options (any non-CRUD operation) |
| `knowledge/cecilia/cecilia-design/backend/design-standards.md` | Cecilia's usual standards — offer as the RECOMMENDED option, never apply silently |
| `knowledge/cecilia/cecilia-design/backend/stage-api.md` | API contract → `<unit>-api.md` + `<unit>-api.yaml` (path per `references/common/workspace.md` §2.1; `<unit>` = module in a monolith, service in microservices) |
| `knowledge/cecilia/cecilia-design/backend/stage-db.md` | Schema design → `<unit>-database.md` (one module or service per run) |
| `knowledge/cecilia/cecilia-design/backend/stage-hld.md` | HLD → `tensura/docs/system/architecture.md` |
| `knowledge/cecilia/cecilia-design/backend/stage-lld.md` | LLD → `<module>-design.md` (one module per run; path per `references/common/workspace.md` §2.1) |
| `knowledge/cecilia/cecilia-design/frontend/fe-options.md` | Frontend option tables — present, never decide |
| `knowledge/cecilia/cecilia-design/frontend/frontend-design.md` | Frontend design → `<app>-frontend.md` (path per `references/common/workspace.md` §2.1) |
| `knowledge/cecilia/cecilia-design/security/authz-matrix.md` | Authorization matrix — the table that catches IDOR |
| `knowledge/cecilia/cecilia-design/security/threat-model.md` | Threat modelling — STRIDE per boundary and per flow |
| `knowledge/cecilia/cecilia-dev-be/challenges-template.md` | Challenge log — <TASK> |
| `knowledge/cecilia/cecilia-dev-be/pr-draft-template.md` | 1. Context |
| `knowledge/cecilia/cecilia-dev-be/workflow.md` | cecilia-dev-be — full rules and workflow |
| `knowledge/cecilia/cecilia-dev-be/code/api-contract.md` | API contract — envelope, errors, requestId, REST, DTOs, events |
| `knowledge/cecilia/cecilia-dev-be/code/architecture.md` | Architecture inside the codebase |
| `knowledge/cecilia/cecilia-dev-be/code/checklist.md` | Self-review checklist (before Draft PR) |
| `knowledge/cecilia/cecilia-dev-be/code/data-concurrency.md` | Money, time, concurrency, idempotency |
| `knowledge/cecilia/cecilia-dev-be/code/infrastructure.md` | Wrap every external dependency (ports & adapters) |
| `knowledge/cecilia/cecilia-dev-be/code/microservices.md` | Microservices (only when HLD chose them) |
| `knowledge/cecilia/cecilia-dev-be/code/module-boundaries.md` | Module & service boundaries — as few dependencies as possible |
| `knowledge/cecilia/cecilia-dev-be/code/principles.md` | Core coding principles (all languages) |
| `knowledge/cecilia/cecilia-dev-be/code/security-logging.md` | Security, validation, logging, observability |
| `knowledge/cecilia/cecilia-dev-be/stacks/java.md` | Java |
| `knowledge/cecilia/cecilia-dev-be/stacks/python.md` | Python |
| `knowledge/cecilia/cecilia-dev-be/stacks/typescript-nestjs.md` | TypeScript / NestJS (Node backend) |
| `knowledge/cecilia/cecilia-dev-be/stacks/_new-stack.md` | Stack without a dedicated file (Go, Kotlin, C#, Rust, Dart, PHP, …) |
| `knowledge/cecilia/cecilia-dev-be/workflows/bugfix.md` | Bug fix — diagnose, approve, then fix |
| `knowledge/cecilia/cecilia-dev-be/workflows/out-of-scope.md` | Work outside the docs: propose, never just do |
| `knowledge/cecilia/cecilia-dev-be/workflows/refactor.md` | Refactor — survey, approve, then change |
| `knowledge/cecilia/cecilia-dev-be/workflows/scaffold.md` | Scaffold — new project, service or module |
| `knowledge/cecilia/cecilia-dev-be/workflows/solution-options.md` | Solution options — non-CRUD logic the docs leave open |
| `knowledge/cecilia/cecilia-dev-fe/challenges-template.md` | Challenge log — <TASK> |
| `knowledge/cecilia/cecilia-dev-fe/image-to-code.md` | Image to code — build a screen from a picture (v20) |
| `knowledge/cecilia/cecilia-dev-fe/pr-draft-template.md` | 1. Context |
| `knowledge/cecilia/cecilia-dev-fe/visual-check.md` | Visual check — see what you built (v20) |
| `knowledge/cecilia/cecilia-dev-fe/web-interface-guidelines.md` | Tài liệu chuyên môn (Không có tiêu đề) |
| `knowledge/cecilia/cecilia-dev-fe/workflow.md` | cecilia-dev-fe — full rules and workflow |
| `knowledge/cecilia/cecilia-dev-fe/code/api-contract.md` | Consuming the API contract — mock, envelope, error codes, auth, retries |
| `knowledge/cecilia/cecilia-dev-fe/code/checklist.md` | Self-review checklist (before Draft PR) |
| `knowledge/cecilia/cecilia-dev-fe/code/principles.md` | Core coding principles (frontend) |
| `knowledge/cecilia/cecilia-dev-fe/code/security-logging.md` | Frontend security — the DOM, tokens, the bundle, and what never gets logged |
| `knowledge/cecilia/cecilia-dev-fe/stacks/frontend-react.md` | Frontend — React / Next.js |
| `knowledge/cecilia/cecilia-dev-fe/style/brutalist.md` | Style guide `brutalist` — Swiss / industrial: rigid grids, extreme type contrast, utilitarian colour |
| `knowledge/cecilia/cecilia-dev-fe/style/minimalist.md` | Style guide `minimalist` — editorial, warm monochrome, flat bento grids, muted accents |
| `knowledge/cecilia/cecilia-dev-fe/style/redesign.md` | Style guide `redesign` — audit an existing UI for generic patterns and upgrade it without breaking behaviour |
| `knowledge/cecilia/cecilia-dev-fe/style/soft.md` | Style guide `soft` — premium calm "agency" look: refined type, soft depth, spring motion |
| `knowledge/cecilia/cecilia-dev-fe/style/taste.md` | Style guide `taste` — general anti-generic frontend taste (upstream v1: design-taste-frontend-v1) |
| `knowledge/cecilia/cecilia-dev-fe/workflows/bugfix.md` | Bug fix — diagnose, approve, then fix |
| `knowledge/cecilia/cecilia-dev-fe/workflows/out-of-scope.md` | Work outside the docs: propose, never just do |
| `knowledge/cecilia/cecilia-dev-fe/workflows/refactor.md` | Refactor — survey, approve, then change |
| `knowledge/cecilia/cecilia-dev-fe/workflows/scaffold.md` | Scaffold — new app, route group or feature module |
| `knowledge/cecilia/cecilia-dev-fe/workflows/solution-options.md` | Solution options — frontend behaviour the design leaves open |
| `knowledge/cecilia/cecilia-devops/authority.md` | What may be run, where, and with whose approval |
| `knowledge/cecilia/cecilia-devops/challenges-template.md` | Challenge log — <TASK> |
| `knowledge/cecilia/cecilia-devops/deploy-and-rollback.md` | Deploy, verify, roll back |
| `knowledge/cecilia/cecilia-devops/environments.md` | Environments |
| `knowledge/cecilia/cecilia-devops/incident-report-template.md` | INC-nn — <short description> |
| `knowledge/cecilia/cecilia-devops/incidents.md` | Incidents — something is broken now |
| `knowledge/cecilia/cecilia-devops/infrastructure.md` | Infrastructure — <system or service> |
| `knowledge/cecilia/cecilia-devops/mcp-and-tools.md` | Working through MCP, CLI, or neither |
| `knowledge/cecilia/cecilia-devops/observability.md` | Observability |
| `knowledge/cecilia/cecilia-devops/pipeline-design.md` | CI pipeline design |
| `knowledge/cecilia/cecilia-devops/pr-draft-template.md` | Draft PR — cecilia-devops |
| `knowledge/cecilia/cecilia-devops/release-packet.md` | Release packet / G4 |
| `knowledge/cecilia/cecilia-devops/secrets.md` | Secrets — the agent never handles a value |
| `knowledge/cecilia/cecilia-devops/workflow.md` | cecilia-devops — full rules and workflow |
| `knowledge/cecilia/cecilia-devops/platforms/docker.md` | Docker — images and compose |
| `knowledge/cecilia/cecilia-devops/platforms/github-actions.md` | GitHub Actions |
| `knowledge/cecilia/cecilia-devops/platforms/gitlab-ci.md` | GitLab CI |
| `knowledge/cecilia/cecilia-devops/platforms/kubernetes-helm.md` | Kubernetes and Helm |
| `knowledge/cecilia/cecilia-devops/platforms/terraform.md` | Terraform (and IaC generally) |
| `knowledge/cecilia/cecilia-devops/platforms/_new-platform.md` | Detecting the stack, and working with one that has no guide |
| `knowledge/cecilia/cecilia-discovery/challenges-template.md` | Challenge log — <TASK> |
| `knowledge/cecilia/cecilia-discovery/decision-log.md` | Decision log → `tensura/docs/DECISIONS.md` |
| `knowledge/cecilia/cecilia-discovery/idea.md` | Idea & scope — <project> |
| `knowledge/cecilia/cecilia-discovery/onboard-report-template.md` | Onboard report — <TASK> — <scope> |
| `knowledge/cecilia/cecilia-discovery/requirements.md` | Requirements (SRS) — <project> |
| `knowledge/cecilia/cecilia-discovery/system-map.md` | System map — <project> |
| `knowledge/cecilia/cecilia-discovery/traceability.md` | Traceability |
| `knowledge/cecilia/cecilia-discovery/workflow.md` | cecilia-discovery — full rules and workflow |
| `knowledge/cecilia/cecilia-discovery/onboard/as-built.md` | Writing the as-built documents |
| `knowledge/cecilia/cecilia-discovery/onboard/confidence-labels.md` | Evidence and confidence — the rule every sentence obeys |
| `knowledge/cecilia/cecilia-discovery/onboard/conventions.md` | Project conventions page — `tensura/conventions.md` |
| `knowledge/cecilia/cecilia-discovery/onboard/reconcile.md` | Reconcile mode — existing documents vs the running system |
| `knowledge/cecilia/cecilia-discovery/onboard/risk-map.md` | Risk map — where this system is most likely to hurt |
| `knowledge/cecilia/cecilia-discovery/onboard/survey.md` | Survey — wide and shallow, before anything deep |
| `knowledge/cecilia/cecilia-discovery/requirements/stage-idea.md` | Idea, feasibility, scope → `tensura/docs/system/idea.md` |
| `knowledge/cecilia/cecilia-discovery/requirements/stage-srs.md` | SRS → `tensura/docs/system/requirements.md` |
| `knowledge/cecilia/cecilia-orchestrator/agent-brief-template.md` | Agent brief template (v20) |
| `knowledge/cecilia/cecilia-orchestrator/agent-briefs.md` | Writing the brief for a role agent (v20) |
| `knowledge/cecilia/cecilia-orchestrator/antigravity.md` | Antigravity — the main host (v20.2) |
| `knowledge/cecilia/cecilia-orchestrator/brief-more.md` | Briefing — background, splitting, re-launch, anti-patterns |
| `knowledge/cecilia/cecilia-orchestrator/brief-roles.md` | Briefing — per-role notes and review panel briefs |
| `knowledge/cecilia/cecilia-orchestrator/briefing-method.md` | How to build the briefing — synthesis, not narration |
| `knowledge/cecilia/cecilia-orchestrator/briefing-template.md` | Briefing — <project> · <TASK> |
| `knowledge/cecilia/cecilia-orchestrator/challenges-template.md` | Challenge log — <TASK> |
| `knowledge/cecilia/cecilia-orchestrator/consensus.md` | Consensus — three independent agents settle the important parts (v20, 20.2) |
| `knowledge/cecilia/cecilia-orchestrator/decision-card.md` | Decision card — `tensura/decisions/<TASK>.md` (v20, 20.1) |
| `knowledge/cecilia/cecilia-orchestrator/fallback.md` | Host differences and fallbacks (v20) |
| `knowledge/cecilia/cecilia-orchestrator/models.md` | Model choice per agent |
| `knowledge/cecilia/cecilia-orchestrator/options-template.md` | Workflow options — input for `workflow.py options` (v20) |
| `knowledge/cecilia/cecilia-orchestrator/panel-brief-blocks.md` | Review by consensus — PANEL, VOTE and MINUTES blocks for the briefs |
| `knowledge/cecilia/cecilia-orchestrator/panel-run.md` | Running the review by consensus and the fix loop (orchestrator side, v20) |
| `knowledge/cecilia/cecilia-orchestrator/presets.md` | Option shapes — what to put in the 2–3 options (v20) |
| `knowledge/cecilia/cecilia-orchestrator/relay.md` | Relaying questions from an agent to Cecilia |
| `knowledge/cecilia/cecilia-orchestrator/report-surface.md` | The report surface — schema, upsert, provenance, degradation |
| `knowledge/cecilia/cecilia-orchestrator/run-log-template.md` | Orchestration run log — <TASK> |
| `knowledge/cecilia/cecilia-orchestrator/waves.md` | Computing the waves (v20) |
| `knowledge/cecilia/cecilia-orchestrator/workflow.md` | cecilia-orchestrator — full rules and workflow (v20) |
| `knowledge/cecilia/cecilia-plan/challenges-template.md` | Challenge log — <TASK> |
| `knowledge/cecilia/cecilia-plan/plan-template.md` | Plan — <TASK> — <epic title> |
| `knowledge/cecilia/cecilia-plan/planning-method.md` | Planning method |
| `knowledge/cecilia/cecilia-plan/tracking.md` | Tracking & adjusting |
| `knowledge/cecilia/cecilia-plan/workflow.md` | cecilia-plan — full rules and workflow |
| `knowledge/cecilia/cecilia-review/challenges-template.md` | Challenge log — <TASK> |
| `knowledge/cecilia/cecilia-review/code-standards.md` | Cecilia's code standards — review reference |
| `knowledge/cecilia/cecilia-review/panel-finding-template.md` | Panel round 1 — <TASK> — lens <lens> |
| `knowledge/cecilia/cecilia-review/panel-rebuttal-template.md` | Panel ballot — voter v<n> (round 2 = the vote; file keeps its v20 name) |
| `knowledge/cecilia/cecilia-review/panel-verdict-template.md` | Panel minutes (verdict) — <TASK> — <artifact> |
| `knowledge/cecilia/cecilia-review/panel.md` | Review panel — lens reviewers find, three voters decide, the minutes record |
| `knowledge/cecilia/cecilia-review/review-asbuilt.md` | Reviewing as-built documentation |
| `knowledge/cecilia/cecilia-review/review-code.md` | Reviewing code (PR, diff, branch, module) |
| `knowledge/cecilia/cecilia-review/review-database.md` | Reviewing database work — schema, migrations, DB-side code, performance claims |
| `knowledge/cecilia/cecilia-review/review-design.md` | Reviewing design documents |
| `knowledge/cecilia/cecilia-review/review-frontend.md` | Reviewing frontend work |
| `knowledge/cecilia/cecilia-review/review-infra.md` | Reviewing infrastructure and delivery-path changes |
| `knowledge/cecilia/cecilia-review/review-plan.md` | Reviewing an execution plan |
| `knowledge/cecilia/cecilia-review/review-release.md` | Release readiness & risk review |
| `knowledge/cecilia/cecilia-review/review-report-template.md` | Review report — <TASK> — <artifact> |
| `knowledge/cecilia/cecilia-review/review-tests.md` | Reviewing tests (test code, test-case catalogs, run reports) |
| `knowledge/cecilia/cecilia-review/review-ui.md` | Reviewing UI design — before frontend code is written |
| `knowledge/cecilia/cecilia-review/security-report-template.md` | Review report — <TASK> — <artifact> |
| `knowledge/cecilia/cecilia-review/verify-report-template.md` | Verification — <TASK> briefing of <YYYY-MM-DD> |
| `knowledge/cecilia/cecilia-review/web-interface-guidelines.md` | Tài liệu chuyên môn (Không có tiêu đề) |
| `knowledge/cecilia/cecilia-review/workflow.md` | cecilia-review — full rules and workflow |
| `knowledge/cecilia/cecilia-review/security/authz-matrix.md` | Authorization matrix — the table that catches IDOR |
| `knowledge/cecilia/cecilia-review/security/review-code-security.md` | Security review of code — against the model, not against a feeling |
| `knowledge/cecilia/cecilia-review/security/supply-chain.md` | Supply chain — dependencies, builds, and what ships |
| `knowledge/cecilia/cecilia-review/security/threat-model.md` | Threat modelling — STRIDE per boundary and per flow |
| `knowledge/cecilia/cecilia-review/verify/verification-method.md` | Verification method — what counts as a source, and how each claim is checked |
| `knowledge/cecilia/cecilia-test/bug-report.md` | Bug reports (never fix product code) |
| `knowledge/cecilia/cecilia-test/challenges-template.md` | Challenge log — <TASK> |
| `knowledge/cecilia/cecilia-test/pr-draft-template.md` | 1. Context |
| `knowledge/cecilia/cecilia-test/test-design.md` | Test design |
| `knowledge/cecilia/cecilia-test/test-lens-report.md` | Test report — <TASK> — lens <lens> |
| `knowledge/cecilia/cecilia-test/test-levels.md` | Writing and running tests |
| `knowledge/cecilia/cecilia-test/test-plan.md` | Test plan — <system> |
| `knowledge/cecilia/cecilia-test/test-strategy.md` | Test strategy → `tensura/docs/system/test-plan.md` |
| `knowledge/cecilia/cecilia-test/visual-check.md` | Visual check — see what you built (v20) |
| `knowledge/cecilia/cecilia-test/web-interface-guidelines.md` | Tài liệu chuyên môn (Không có tiêu đề) |
| `knowledge/cecilia/cecilia-test/workflow.md` | cecilia-test — full rules and workflow |
| `knowledge/cecilia/cecilia-test/lenses/concurrency-perf.md` | Lens: concurrency-perf (cecilia-test v20) |
| `knowledge/cecilia/cecilia-test/lenses/database.md` | Lens: database (cecilia-test v20) |
| `knowledge/cecilia/cecilia-test/lenses/functional.md` | Lens: functional (cecilia-test v20) |
| `knowledge/cecilia/cecilia-test/lenses/infra.md` | Lens: infra (cecilia-test v20) |
| `knowledge/cecilia/cecilia-test/lenses/integration.md` | Lens: integration (cecilia-test v20) |
| `knowledge/cecilia/cecilia-test/lenses/security.md` | Lens: security (cecilia-test v20) |
| `knowledge/cecilia/cecilia-test/lenses/ui.md` | Lens: ui (cecilia-test v20) |
| `knowledge/cecilia/cecilia-ui/accessibility.md` | Accessibility — designed in, measured, written down |
| `knowledge/cecilia/cecilia-ui/challenges-template.md` | Challenge log — <TASK> |
| `knowledge/cecilia/cecilia-ui/design-process.md` | Design process — from flows to finished screens |
| `knowledge/cecilia/cecilia-ui/handoff.md` | Handoff to cecilia-dev-fe — and changing a design later |
| `knowledge/cecilia/cecilia-ui/tokens-components.md` | Design tokens and component specs |
| `knowledge/cecilia/cecilia-ui/tool-choice.md` | Choosing the design tool — ask once, record, stick to it |
| `knowledge/cecilia/cecilia-ui/ui.md` | <app> — UI design |
| `knowledge/cecilia/cecilia-ui/web-interface-guidelines.md` | Tài liệu chuyên môn (Không có tiêu đề) |
| `knowledge/cecilia/cecilia-ui/workflow.md` | cecilia-ui — full rules and workflow |
| `knowledge/cecilia/cecilia-ui/style/brutalist.md` | Style guide `brutalist` — Swiss / industrial: rigid grids, extreme type contrast, utilitarian colour |
| `knowledge/cecilia/cecilia-ui/style/minimalist.md` | Style guide `minimalist` — editorial, warm monochrome, flat bento grids, muted accents |
| `knowledge/cecilia/cecilia-ui/style/redesign.md` | Style guide `redesign` — audit an existing UI for generic patterns and upgrade it without breaking behaviour |
| `knowledge/cecilia/cecilia-ui/style/soft.md` | Style guide `soft` — premium calm "agency" look: refined type, soft depth, spring motion |
| `knowledge/cecilia/cecilia-ui/style/taste.md` | Style guide `taste` — general anti-generic frontend taste (upstream v1: design-taste-frontend-v1) |
| `knowledge/cecilia/common/capabilities.md` | Host capabilities and tools (common v20) |
| `knowledge/cecilia/common/challenge.md` | Challenge — use challenge where it pays (common v20) |
| `knowledge/cecilia/common/code-quality.md` | Code quality — small, clear, fast where it matters (common v20) |
| `knowledge/cecilia/common/core-min.md` | Core (min) — always loaded by every Cecilia role (common v20) |
| `knowledge/cecilia/common/core.md` | Core — how every Cecilia role works (common v20) |
| `knowledge/cecilia/common/decisions.md` | Asking, options and research — how decisions reach Cecilia (common v20) |
| `knowledge/cecilia/common/evidence.md` | Evidence, numbers and reports (common v20) |
| `knowledge/cecilia/common/git-handoff.md` | Git hand-off — local-only, rebase, PR text (common v20) |
| `knowledge/cecilia/common/git.md` | Git flow, checkpoints, backup and rollback (common v20) |
| `knowledge/cecilia/common/numbers.md` | Numbers — measure, project, calculate (common v20) |
| `knowledge/cecilia/common/parallel.md` | Parallel work — waves, isolation, integration, stopping and resuming (common v20) |
| `knowledge/cecilia/common/workspace.md` | Workspace — where things live and who owns them (common v20) |
| `knowledge/cecilia/common/flows/personal.md` | Flow `personal` — Cecilia decides, pushes and opens PRs herself (common v20) |
| `knowledge/cecilia/common/flows/team.md` | Flow `team` — tickets in, reviewable PRs out, the leader decides the big things (common v20) |
| `knowledge/cecilia/common/generated/flows.md` | Flows (v20.2.0) |
| `knowledge/cecilia/common/generated/lenses.md` | Lenses (v20.2.0) — test and review |
| `knowledge/cecilia/common/generated/roster.md` | Roster (v20.2.0) — roles, agent types, lanes |
