---
name: cecilia-db
description: Knowledge pack of cecilia-coding-skills (v22) — schema design, migrations, concurrency, performance, connections, growth, partitioning, HA/DR, engines, compliance. Loaded only by Cecilia roles through their brief; not a standalone skill, do not trigger it directly — use cecilia-coding-skills.
---

# Database knowledge — Cecilia knowledge pack (v22)

Part of `cecilia-coding-skills` (the coordinator, roles, rules, assets and scripts live there). This pack holds
only `references/` for: `db`.

- **Used by:** dev KIND=db; planner (schema, growth, engine choice); reviewer (database lens).
- **Entry points:** `references/db/method.md` — each has a "Guides" table; load only the rows the change touches.
- **Paths:** `references/<topic>/…` resolves to the pack that owns the topic (the brief lists them);
  `agents/`, `rules/`, `assets/`, `scripts/` and `references/{flow,common,plan,dev}/` are in `cecilia-coding-skills`.
