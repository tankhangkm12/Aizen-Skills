# Parallel work — units, isolation, integration, resuming, measuring (v26)

Independent units run at the same time; each runs its own checks; they meet in one integration step.

## 1. How many

At most **`parallel.max`** units run at once — `.aizen/config/guard.json` → `"parallel": {"max": 2}` by default. Two
is the safe number on one machine: each member needs its own worktree, ports, containers and database, and every
extra unit costs a dispatch, a merge and the owner's attention when something breaks. The owner raises it when
the numbers in §6 say parallel work paid off and the machine has room. Prefer fewer, larger units.

The waves come from the plan, not from judgment:

```
uv run "<SKILL_DIR>/scripts/flow/state.py" waves --task <TASK>
```

It reads each module's `Files (write set)` and `after:`, puts a unit in the first wave after its dependencies,
and moves it to a later wave when it shares a path with a member (prefix match on the globs — conservative) or
the wave is full. The planner copies the result into the plan's `Order / waves`; the coordinator launches exactly
those waves. A unit that should run earlier needs a narrower write set or a settled seam, not a bigger wave.

## 2. When two writers may run at the same time — all three, or sequence them

1. **Seams settled** — contract version, schema, event shape, env var and port names are in the plan. A writer that
   needs to change a seam stops and reports; it never edits the other side's assumption.
2. **Disjoint files** — write sets compared path by path. Forgotten collisions: DI modules, routers, migration
   registries, lockfiles, i18n bundles, shared enums, error catalog, generated clients. A shared hot file gets **one**
   owner; others list the lines they need in their report.
3. **Isolation** — each code writer in its own worktree and branch
   (`git worktree add .aizen/worktrees/<TASK>-<unit> -b "$(state.py branch --task <TASK> --unit <unit>)" <base>`). Two agents never share a checkout.

**Runtime isolation** — give every member its own:

| Resource | How |
|---|---|
| ports | block per member (`3000+100k`, `5432+k`) passed as env vars on the command, never written to `.env` |
| docker compose | `docker compose -p <TASK>-<unit>` |
| database / test DB / caches | `<db>_<unit>`, cache dir under its worktree |
| browser | its own Playwright session `-s=<TASK>-<unit>`; never `close-all` / `kill-all` |

Creating a worktree is A2; deleting one that holds unpushed work is A3.

## 3. Waves

A wave = members launched together because none can invalidate another: dependencies finished → write sets
compared → isolation assigned. **Launch every member of a wave in one message.** A wave of one is normal.
The next wave starts after a clean wave without asking the owner. A failed check is fixed by the owning unit; an
unapproved A3, an A4 or a plan that cannot work stops the flow (`BLOCKED`).

## 4. Integration

Separate branches passing their own tests do not prove combined behaviour.

1. The PR branch (`state.py branch --task <TASK>`) from the base; `git merge --no-ff` each unit branch in plan order; record every SHA (coordinator, git only).
2. Conflict → `git merge --abort`; a `dev` with `UNIT=int` resolves it from the docs, or hands each side back to its owner.
3. The tester runs against the PR branch; review and fix rounds run on the integrated SHA.
4. Failures go back to the unit that caused them, on its own branch; then re-integrate.

Merging into a shared branch is A4 — the owner does it.

## 5. Resuming and stopping

- `uv run "<SKILL_DIR>/scripts/flow/state.py" status --task <TASK>` and `state.md` first; check current SHAs and whether files changed.
- An action whose result is unknown is checked, never repeated.
- Never start a replacement writer while the old one might still be writing.
- Cleanup of worktrees and `int/*` branches is a separate step after the owner pushed or abandoned the work (A3 if
  anything unpushed would be lost).

## 6. Measuring — did parallel work pay off?

The hooks time-stamp every write and command with who did it, so the run measures itself:

```
uv run "<CORE_DIR>/scripts/core/journal.py" stats --run <TASK>
```

prints each worker's first and last action and, for the sub-agents, their summed working time against the time
any of them was working. A factor near **1.0×** means the units ran one after the other (waiting on seams, merge
conflicts, a shared database) — the next plan should use fewer, larger units. Clearly above 1 with clean merges →
raising `parallel.max` is worth trying. `.aizen/out/latest.md` shows the same lines under "Thời gian" once two or
more sub-agents worked.

## 7. Bounded effort

Two correction attempts for a persistent failure inside one run, then stop and report. Flaky test: ≤ 2 reruns, all
recorded. Fix loop across the task: ≤ 2 rounds.
