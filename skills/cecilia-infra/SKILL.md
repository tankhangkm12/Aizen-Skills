---
name: cecilia-infra
description: Knowledge pack of cecilia-coding-skills (v23) — pipelines, environments, deploy and rollback, secrets, observability, incidents, platform guides (Docker, GitHub Actions, GitLab CI, Kubernetes/Helm, Terraform). Loaded only by Cecilia roles through their brief; not a standalone skill, do not trigger it directly — use cecilia-coding-skills.
---

# Infrastructure and delivery knowledge — Cecilia knowledge pack (v23)

Part of `cecilia-coding-skills` (the coordinator, roles, rules, assets and scripts live there). This pack holds
only `references/` for: `infra`.

- **Used by:** devops; reviewer (infra lens).
- **Entry points:** `references/infra/method.md` — each has a "Guides" table; load only the rows the change touches.
- **Paths:** `references/<topic>/…` resolves to the pack that owns the topic (the brief lists them);
  `agents/`, `rules/`, `assets/`, `scripts/` and `references/{flow,common,plan,dev}/` are in `cecilia-coding-skills`.
