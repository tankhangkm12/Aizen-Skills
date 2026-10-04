[cecilia-brief TASK={{TASK}} ROLE={{ROLE}} KIND={{KIND}} UNIT={{UNIT}} LENS={{LENS}} ROUND={{ROUND}} MODE={{MODE}}]

Read `agents/{{ROLE}}.md` and `rules/core.md` in the cecilia-coding-skills skill ({{SKILL_DIR}}) first and follow them.

## Task
Goal: {{GOAL}}
Your part: <what this unit must deliver, with requirement/finding ids>
Done when: <checkable: command + expected result, test names, screens>

## Where
Project root: {{ROOT}}
Code workdir: <worktree path, or "read-only">  ·  Branch: <branch> @ <start SHA>
Write set (your lane): <path globs — nothing outside>
Runtime (yours alone): ports <range> · compose project <TASK-unit> · DB <name> · browser session <TASK-unit>

## Inputs
Plan: tensura/plans/{{TASK}}.md  ·  Decision: tensura/tasks/{{TASK}}/state.md (## Decision)
<docs, contract version, findings to fix (ROUND > 0), earlier reports>

## Allowed A3
<none | exact list Cecilia approved>

## Report
Full report: tensura/reports/{{TASK}}/{{REPORT}}  ·  Return ≤ 15 lines ending with `Deviations:`.
