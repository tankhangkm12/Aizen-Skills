[cecilia-brief TASK={{TASK}} ROLE={{ROLE}} KIND={{KIND}} UNIT={{UNIT}} STAGE={{STAGE}} LENS={{LENS}} ROUND={{ROUND}} MODE={{MODE}}]

Read `agents/{{ROLE}}.md` and `rules/core.md` in the cecilia-coding-skills skill first and follow them.
Paths: `agents/`, `rules/`, `assets/`, `scripts/` are under {{SKILL_DIR}}; each `references/<topic>/` path
resolves through this table (knowledge packs installed next to the skill):
{{PACKS}}
`tensura/` is always {{ROOT}}/tensura, also when you work in a worktree.

## Task
Goal: {{GOAL}}
Your part: {{PART}}
Done when: {{DONE}}

## Where
Project root: {{ROOT}}
Code workdir: {{WORKDIR}}  ·  Branch: {{BRANCH}} @ {{SHA}}
Write set (your lane): {{WRITE_SET}}
Runtime (yours alone): ports {{PORTS}} · compose project {{TASK}}-{{UNIT}} · DB {{DB}} · browser session {{TASK}}-{{UNIT}}

## Inputs
Plan: tensura/plans/{{TASK}}.md  ·  Decision: tensura/tasks/{{TASK}}/state.md (## Decision)
{{INPUTS}}

## Allowed A3
{{A3}}

## Commands
Quality gate: python "{{SKILL_DIR}}/scripts/check.py" --task {{TASK}} --unit {{CHECK_UNIT}} --project "{{WORKDIR_CMD}}"

## Report
Full report: tensura/reports/{{TASK}}/{{REPORT}}  ·  Return ≤ 15 lines ending with `Deviations:`.
