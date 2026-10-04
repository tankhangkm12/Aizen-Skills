# Frontend implementation — steps (v21)

Used by `dev` with `KIND=fe`.

## Rules

1. **Design + contract are the spec.** Every screen, state and field traces to `SCR`/`CMP`/endpoint.
2. **Never invent an endpoint, field or response shape.** Missing → contract gap in the report.
3. **Mocks are generated from the contract** and regenerated when its version changes.
4. **Every documented state is built**: loading, empty, partial, each error code, permission-denied,
   offline/stale, submitting, success.
5. **Server validation is mirrored, never contradicted**; its error codes drive the messages.
6. **Shared pieces** (design system, router, global state, i18n) only when in your write set.
7. **Build the design, not a guess.** Tokens and components from the UI design; taste (`style/<style>.md`) only
   fills gaps the design and the repo's design system leave. A new font/icon/motion library is A3.
8. **Look at it before you say it is done** — in a real browser (`visual-check.md`). No browser → visual rows
   `[unverified]`.

## Steps

- **F0 Locate.** Branch/worktree, start SHA; frontend doc, UI design (`<app>-ui.md`, `design-tokens.json`,
  `ui-exports/`), contract + version.
- **F1 Read.** Screens and every endpoint they touch, incl. the error list. List what the design does not settle
  (focus, stale list after mutation, double submit, optimistic rollback, partial failure); ask only what changes code.
- **F2 Build.** Mock from the contract, own dev-server port, small clean code (`principles.md`), commit each
  green step. Spec is an image → `image-to-code.md`.
- **F3 Quality gate.** Build, type-check, lint, tests with counts; bundle budget; self-review with `checklist.md`
  and `web-interface-guidelines.md`.
- **F4 Verify per screen in the browser** (`visual-check.md`, `scripts/uikit.py`): each state and breakpoint —
  screenshot, console, diff vs export, contrast. ≤ 3 fix rounds per screen. Against the real API once the
  backend is integrated; mock vs real differences are findings.
- **F5 Hand off.** `python scripts/check.py --task <TASK>`; PR text with the state table (screenshot paths) →
  `tensura/reports/<TASK>/pr-body.md`; report + push/PR commands for Cecilia.

## Guides (load only what the change touches)

| Change touches | Read |
|---|---|
| any frontend code | `principles.md`, `checklist.md` (before hand-off) |
| React / Next | `react.md` |
| API calls, errors, token refresh | `api-calls.md` |
| tokens in DOM/storage, logs | `security-logging.md` |
| accessibility, forms, focus | `accessibility.md`, `web-interface-guidelines.md` |
| visual style | `style/<style>.md` (taste, minimalist, soft, brutalist, redesign) |

All in `references/frontend/`. Integrator and fix rounds: same as `references/backend/method.md`.
