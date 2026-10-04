---
name: cecilia-discover-design
description: Knowledge pack of cecilia-coding-skills (v22) — scope, legacy onboarding (as-built docs), idea/SRS requirements, HLD/LLD, API contract, frontend architecture, threat model. Loaded only by Cecilia roles through their brief; not a standalone skill, do not trigger it directly — use cecilia-coding-skills.
---

# Discovery and design knowledge — Cecilia knowledge pack (v22)

Part of `cecilia-coding-skills` (the coordinator, roles, rules, assets and scripts live there). This pack holds
only `references/` for: `discover`, `design`.

- **Used by:** planner (STAGE=discover|design).
- **Entry points:** `references/discover/method.md` · `references/design/method.md` — each has a "Guides" table; load only the rows the change touches.
- **Paths:** `references/<topic>/…` resolves to the pack that owns the topic (the brief lists them);
  `agents/`, `rules/`, `assets/`, `scripts/` and `references/{flow,common,plan,dev}/` are in `cecilia-coding-skills`.
