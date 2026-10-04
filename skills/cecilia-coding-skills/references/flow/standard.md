# STANDARD flow — the coordinator's steps (v22)

You are the main session. You run this flow, dispatch roles, merge branches and talk to Cecilia. Roles do the
specialist work. Target: **4–6 dispatches** per task. State lives in `tensura/tasks/<TASK>/`.

## S0 — Intake (you)

1. `python "<SKILL_DIR>/scripts/state.py" init --task <TASK> --mode standard --goal "<her prompt>"` (resuming →
   `state.py status --task <TASK>` and read `state.md`; never re-ask what is already answered there). Below,
   `state.py` means that same absolute path.
2. Read `CLAUDE.md`/`AGENTS.md`, `tensura/{conventions,lessons}.md`, then skim only the code the prompt names.
3. A CONTROLLED trigger (see SKILL.md) → switch to `references/flow/controlled.md` as well. FAST work that grew →
   `state.py status --task <TASK> --mode standard`, then continue at S1.

## S1 — Plan (1 × planner)

Dispatch `planner` with `state.py brief --task <TASK> --role planner [--stage discover|design]`. It measures the facts itself (no questions to
Cecilia), writes `tensura/plans/<TASK>.md`: goal, 2–5 steps, **units** (disjoint write sets), checks,
rollback, and 2–3 option shapes plus the preference/risk questions it could not settle.

Needs requirements or a design first (new product area, unclear behaviour, new public API) → the brief says
`STAGE=discover` or `STAGE=design`; the planner produces those docs in the same dispatch before the plan.

## S2 — ONE decision card (you)

Show the plan's options and questions **once** (Claude Code: AskUserQuestion, recommended option first;
Antigravity: `ask_question`; otherwise one numbered message). Record her answer:
`state.py answer --task <TASK> --text "<answer>"`. No writer starts before this answer.

## S3 — Build (N × dev, one message)

- Per unit: `git worktree add .worktrees/<unit> -b feature/<TASK>-<unit> <base>`, its own ports and DB name.
- `state.py brief --task <TASK> --role dev --kind <be|fe|db|ui> --unit <unit> --sha <start SHA> --write-set "<globs>"`
  → dispatch **all units of a wave in one message**. Infra units: `--role devops --unit <unit>`.
- Units that share a file or a seam that is not settled run in sequence, not in parallel.
- On return: read the report, then **check the files** — diff, commits, tests, `Deviations:`. A claim that the
  files do not support is a finding.

## S4 — Integrate (you, git only)

More than one unit → integration worktree, `int/<TASK>` from the base, `git merge --no-ff` each unit branch in
plan order. Clean merge is yours. Conflict → `git merge --abort` and dispatch a `dev` with `UNIT=int`
naming both branches and the intended behaviour. Never resolve a conflict by hand.

## S5 — Test (1 × tester)

`state.py brief --task <TASK> --role tester --lens <a,b,…> --sha <SHA>` on `int/<TASK>` (or the single unit branch). Pick lenses from
the diff: always `functional`; add `integration` (several units/services), `ui` (screens), `database`
(migrations, queries), `security` (auth, input, secrets), `concurrency-perf` (locks, money, load).
Split into two testers only when a heavy lens (perf, security) would dominate the run (`--unit <lens>` each,
so their reports do not collide).

## S6 — Review (1 × reviewer)

`state.py brief --task <TASK> --role reviewer --lens <…> --sha <SHA>` on the same SHA, preferably on a different model than the devs
(`references/flow/platform-*.md`). The reviewer reads the test report as evidence and returns
PASS / CHANGES_REQUIRED / INCOMPLETE with findings (BLOCKER / SHOULD-FIX / SUGGESTION).

## S7 — Fix loop (≤ 2 rounds)

While a BLOCKER/SHOULD-FIX or an open product BUG remains: `state.py round --task <TASK>` (exits 3 past the
limit) → dispatch the owning `dev` units with only those finding ids → re-integrate → re-test only affected
lenses → **delta review** of the new SHA (same reviewer brief, `ROUND=n`). Still open after round 2 → back to
Cecilia with options: another round with a changed approach, re-plan, accept the risk (her call), or stop.

## S8 — Finish (you)

Relay every A3 request verbatim (one numbered list). Merge the units' `pr-body-<unit>.md` into
`tensura/reports/<TASK>/pr-body.md` (one PR for `int/<TASK>`). Then one summary: what changed, checks with numbers,
verdict, open risks, `Deviations:`, and one copy-paste block:

```bash
git push -u origin <branch>
gh pr create --draft --base <target> --head <branch> --title "<title>" --body-file tensura/reports/<TASK>/pr-body.md
```

Collect `L-nn` lessons into `tensura/lessons.md`; `state.py status --task <TASK> --set done`.

## Checks between steps

| Check | If it fails |
|---|---|
| card answered before any dev/tester | back to S2 |
| unit write sets disjoint in one wave | run them in sequence |
| report claims match files/SHA/tests | finding; re-dispatch or tell Cecilia |
| reviewer did not author the code | re-dispatch to a fresh reviewer |
| nothing pushed by an agent | push only in the final block |
