# Acceptance cases — <TASK> — <title>

> Written by the planner **before any code**, approved by the owner with the plan (`state.py answer --module
> acceptance`), frozen at `state.py approve` (hashed; the guard refuses every edit — only the owner changes it).
> The tester implements every row; the dev of the code under test never writes these tests.

Test location: `tests/acceptance/**`
<!-- one or more globs in backticks; the guard refuses writes there from a dev unit's worktree.
     Use the repo's layout, e.g. `src/test/java/**/acceptance/**`, `e2e/**`, `tests/acceptance/**`. -->

| TC | AC / FR | Kind | Given | When | Then |
|---|---|---|---|---|---|
| TC-01 | AC-1 | + | a free seat 12A on train SE1, 2026-02-10 | a signed-in user holds 12A | 200, hold id, seat shows "held" for 5 min |
| TC-02 | AC-1 | − | 12A held by user B | user A holds 12A | 409 `SEAT_ALREADY_HELD`, B's hold unchanged |
| TC-03 | AC-2 | − | a hold created 5 min 1 s ago | the user pays | 410 `HOLD_EXPIRED`, no charge |
| TC-04 | AC-2 | edge | 50 users hold 12A at the same moment | — | exactly one 200, 49 × 409 |

Rules for the planner:

- At least one **+** (it works) and one **−** (it refuses / fails safely) case per AC; add **edge** cases for
  limits, time, concurrency, permissions and money when the module touches them.
- **Then** is observable from outside: status code, error code, stored row, message, screen state — never "the
  service calls X internally".
- Each row is decided: a value or rule nobody has agreed yet is a question in the plan, not a guess in a case.
- Ids `TC-nn` are never renumbered; a case the owner drops is struck through: `~~TC-05~~ dropped D-07`.
