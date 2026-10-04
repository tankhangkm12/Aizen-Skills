[cecilia-brief TASK={{TASK}} ROLE={{ROLE}} KIND={{KIND}} UNIT={{UNIT}} STAGE={{STAGE}} LENS={{LENS}} ROUND={{ROUND}}]

Read `agents/{{ROLE}}.md` and `rules/core.md` in the cecilia-coding-skills skill first and follow them.
Paths: `agents/`, `rules/`, `assets/`, `scripts/` are under {{SKILL_DIR}}; each `references/<topic>/` path
resolves through this table (knowledge packs installed next to the skill):
{{PACKS}}
`tensura/` is always {{ROOT}}/tensura, also when you work in a worktree.

## Task
Goal: {{GOAL}}
Your part: {{PART}}
Done when: {{DONE}}

## Agreement
Cecilia confirmed the plan module by module: tensura/plans/{{TASK}}.md + tensura/tasks/{{TASK}}/state.md
(## Agreed, ## Approval). Once approved it is the contract: do not ask her anything — build exactly that.
Plan silent on a detail → take the simplest option that fits it and list it under `Deviations:`.
Only stop for: an A3 action not listed below, any A4, data loss, or a step that would break the agreed plan.

## Where
Project root: {{ROOT}}
Code workdir: {{WORKDIR}}  ·  Branch: {{BRANCH}} @ {{SHA}}
Write set (your lane): {{WRITE_SET}}
Runtime (yours alone): ports {{PORTS}} · compose project {{TASK}}-{{UNIT}} · DB {{DB}} · browser session {{TASK}}-{{UNIT}}

## Inputs
{{INPUTS}}

## Allowed A3 (approved with the plan)
{{A3}}

## Commands
Code map (ask before reading files): {{GRAPH}}
Quality gate: python "{{SKILL_DIR}}/scripts/check.py" --task {{TASK}} --unit {{CHECK_UNIT}} --project "{{WORKDIR_CMD}}"

## Report
Full report: tensura/reports/{{TASK}}/{{REPORT}}  ·  Return ≤ 15 lines ending with `Deviations:`.
