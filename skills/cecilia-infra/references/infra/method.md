# Delivery path — steps (v22)

Used by `devops`. Build the path from commit to running service, prove it works, hand Cecilia the trigger.
CI/CD, manifests and IaC are CONTROLLED by default.

## Rules

1. **Never handle a secret value** (`secrets.md`) — the path a secret travels, by name; Cecilia types the value.
2. **Know the real state before proposing a change** — `plan` / `helm diff` / `kubectl diff` as an A3 read; put
   the real diff in the approval quote. Unexpected destroys or replacements stop the work.
3. **One quote per action** (`authority.md`): command, context, change, blast radius, rollback (verified to
   exist), recovery check, cost.
4. **Not done until the rollback was rehearsed** in non-production (`deploy-and-rollback.md` §4).
5. **The repo chooses the stack** — detect and follow; never introduce a tool because it is good.
6. **Unknown environment is production** until Cecilia classifies it.
7. **Build once, promote the same artifact** — pin the digest.
8. **Size and cost are computed** with `scripts/capacity.py`, low/expected/high, dated prices.
9. Production writes, IAM, secret values, DNS, certificates, billing, branch protection, releases/tags,
   `--force`/`--auto-approve`/`--no-verify`: A4. Even in an incident you prepare the rollback; Cecilia runs it.

## Path ownership

| devops | dev |
|---|---|
| `.github/workflows/`, `.gitlab-ci.yml`, `Jenkinsfile`, `ci/` | application source |
| `Dockerfile*`, `.dockerignore`, `docker-compose*.yml` | health/readiness handlers, config module |
| `deploy/`, `k8s/`, `charts/`, `helm/`, Kustomize | migration scripts (devops prepares how they run) |
| `infra/`, `*.tf`, `*.tfvars`, Pulumi/CDK | dependency manifests |
| `.env.example` keys, secret wiring, alerts/dashboards as code | code reading those variables, log statements |

## Steps

- **Y0 Locate** plan, infra docs, stack from repo files, reachable CLIs/MCP (`mcp-and-tools.md` §1) and which
  credentials this session has — a production-write credential is reported immediately.
- **Y1 Read and check** — drift between repo and reality (A3 reads only); open questions (limits, replicas,
  retention, timeouts, alert thresholds, who is paged).
- **Y2 Infra brief** — files, what is applied where, blast radius, rollback, recovery check, cost delta, secret names.
- **Y3 Build** the files; commit each step.
- **Y4 Static gate** — pipeline lint, Dockerfile lint, `helm lint`+`template`, `terraform fmt -check`+`validate`,
  secret scan. Missing tool → `[unverified]`.
- **Y5 Non-prod apply** — A3 per action: quote → yes → run → record; prove a real request works, the rollback
  worked, logs and metrics arrive.
- **Y6 Hand off** — infra doc from `assets/infrastructure.md`; PR text from `assets/release-pr-template.md`;
  every push/apply as a command with verification and rollback. Production release: `assets/release-packet.md`.

## Guides (in `references/infra/`)

| Task | Read |
|---|---|
| CI, pipeline stages, slow pipeline | `pipeline-design.md`, `platforms/github-actions.md` / `references/infra/platforms/gitlab-ci.md` |
| containerize, image | `platforms/docker.md` |
| deploy, environments, staging | `deploy-and-rollback.md`, `environments.md` |
| Kubernetes / Helm | `platforms/kubernetes-helm.md` |
| Terraform | `platforms/terraform.md` |
| monitoring, alerts, logs, health | `observability.md` |
| secret wiring | `secrets.md` first |
| production incident, postmortem | `incidents.md` (replaces Y1–Y5) |
| platform not covered yet | `platforms/_new-platform.md` |
| red pipeline | Y0 → diagnose (`mcp-and-tools.md` §4) → Y3–Y6 |
