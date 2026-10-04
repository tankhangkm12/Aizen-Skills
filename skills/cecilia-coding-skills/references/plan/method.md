# Planning — reduce uncertainty, not create paperwork (v21)

## Steps

1. **Locate.** Read only the docs and code needed for this change; `tensura/tasks/<TASK>/state.md` when resuming.
2. **Measure, never ask facts.** Paths, versions, config, how code behaves → read-only tools, labelled. An
   unverified assumption becomes the first (measurement) step. Only preferences/risk choices become questions,
   each with choices and a recommended default.
3. **Root cause first** for bugs and incidents: `[verified]` only when reproduced or the causing line was read at
   this SHA; otherwise step 1 is a read-only measurement (failing test, `EXPLAIN`, logs) naming the result that
   would change the plan.
4. **Write the plan** to `tensura/plans/<TASK>.md` (STANDARD shape below; CONTROLLED: `planning-method.md`).
5. **Self-challenge**: is there a simpler plan? which step is most likely wrong? (`references/common/challenge.md`).
6. **Return** ≤ 15 lines: plan path, units, options, questions.

## STANDARD plan shape

```text
Goal: <one checkable sentence>
Plan:
1. <step>   [unit · after: <step> | parallel]
2. <step>
Simpler option: <the simplest approach that would also work; why this plan is not simpler>
Units:  <id · kind be|fe|db|ui (dev) or infra (devops) · write set (globs) · seams relied on · after: <unit>>
Test lenses: <functional + …>
Checks: <tests/lint/build commands>
Backup: <DB dump / none, why>
Rollback: <how>
Stop if: <contract/schema/security/infra trigger>
Options:
  A (recommended): <units per wave, parallel or sequential, models> — why
  B: <…>
Questions for Cecilia: <preference/risk only, choices + default>
```

## Units — how parallel work stays safe

- Each unit has a **disjoint write set**. Shared hot files (router, DI module, lockfile, migration registry,
  i18n bundle) get one owner; others list the lines they need in their report.
- Units that share only **settled** seams (approved contract version, schema, env names) may run in the same wave.
- Cannot be made disjoint → sequence them. Prefer fewer, larger units over many tiny ones: every unit costs a
  dispatch, a worktree and a merge.
- Detail: `references/common/parallel.md`.

## Track and adjust

Status = measured: done / failing / next, branch + SHA, open findings. When facts change, show before → after for
the affected steps and why; CONTROLLED scope changes need Cecilia's approval again (`tracking.md`).
