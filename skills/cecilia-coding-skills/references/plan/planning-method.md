# CONTROLLED plan — exact enough to approve line by line (v22)

The STANDARD shape (`method.md`) plus the detail Cecilia needs to approve a high-risk change in one read.
Template: `assets/plan-template.md`.

## 1. What CONTROLLED adds per unit

| Field | Rule |
|---|---|
| Unit | `id · kind be|fe|db|ui` (dev) or `infra` (devops) · branch `feature/<TASK>-<unit>` · worktree `.worktrees/<unit>` |
| Covers | requirement / finding ids, doc sections |
| Write set | exact paths or `dir/**` — becomes `--write-set` in the brief; anything outside → stop and ask |
| Commands | every command the unit runs (tests, builds, local services); anything else is A3 |
| Checks | the green signal (test names, `check.py` result, screens) |
| Backup | DB dump / state backup path before any migration or data change — or `none` and why |
| Rollback | concrete per unit: revert commit, down migration, flag off, `helm rollback` |
| After | the units it waits for; same wave only with disjoint write sets and settled seams |
| Confidence | brownfield: the label of the facts it stands on; an `[unverified]` root cause → a measurement unit first |

## 2. Shaping the work

- **Measure first** when the cause or a size is not `[verified]`: wave 1 is a read-only measurement unit
  (failing test, `EXPLAIN`, log query) naming the result that would change the plan.
- **One purpose per unit**; never mix a refactor with a feature. Order follows the docs: schema/migration →
  domain → service → API → UI → wiring.
- **Every requirement id lands in exactly one unit** or is stated out of scope.
- **Delivery-path work is planned, not assumed**: a new service, env var, secret name, external dependency,
  real-environment migration, CI step or alert → an `infra` unit for `devops`. None → say "no infra unit" so
  nobody looks for one. Infra units never contain application code; an app change the delivery path needs is a
  `dev` unit sequenced before it.
- **Waves**: each wave ends with a check-in (`references/flow/controlled.md` §3). A wave is safe to run in
  parallel only under `references/common/parallel.md`.
- **Local-only**: no unit pushes; the finish block carries the push / `gh pr create --draft` commands.
- Work outside the docs (refactor, perf, a bug found) is never planned silently → "Proposals" with options.

## 3. Approval

Cecilia approves the whole plan on the decision card ("approve plan <TASK>"), recorded with `state.py answer`.
Devs write only the approved write sets and run only the listed commands.

## 4. Re-plan (facts changed mid-task)

1. Name the trigger with evidence: blocked unit, doc change, BUG, review BLOCKER, Cecilia's request.
2. Detect drift: unit work outside its write set, a wave started before its `After`, docs changed after
   approval, an open BUG with no owning unit, a requirement id covered twice or not at all.
3. Show the plan diff (units before → after) with 2–3 options; never rewrite history — retired units get
   `~~id~~ replaced by …` and a "Plan changes" row (date, change, reason, approved by).
4. A changed write set, command list or rollback in CONTROLLED needs Cecilia's approval again.

## 5. Docs written by others

Record each source with path/link, version or commit and date read. External docs (Notion, Drive, PDF) can change
silently → list it as a risk and re-check before each wave.
