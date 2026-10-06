# Git flow, checkpoints, backup and rollback (v26)

Every change is made so that the owner can undo it at any moment. Git is the backup for everything it
tracks; `.aizen/backups/` is the backup for what it does not.

## 1. Branch model

`git.model` in `.aizen/config/conventions.md`: `auto` (default) · `gitflow` · `github`. The repository's own
convention (CONTRIBUTING, `git branch -r`, history) wins; note it once in the report.

| Model | Long-lived | Task branches from | Merge target |
|---|---|---|---|
| **gitflow** (`auto` picks it when `develop` exists, or the repo has no convention yet) | `main` (released), `develop` (integration) | `develop`; `hotfix/*` from `main`; `release/*` from `develop` | `develop` (hotfix → `main` and `develop`) |
| **github** (`auto` picks it when there is only `main`/`master`) | `main` | `main` | `main` |

**Branches are named after the business change, never after the agent's run.** The run id (`SHOP-42`,
`VT-1`) is a local bookkeeping key of `.aizen/`; a reader of the repository must not need it. `state.py init
--slug <business-name> --type <type> [--ticket <real ticket>]` fixes the name once; `state.py branch --task <TASK>
[--unit <unit>]` prints it — never type a branch name by hand.

| Branch | Name | Example |
|---|---|---|
| the change (the PR) | `<type>/<slug>` | `feature/seat-hold`, `bugfix/payment-timeout` |
| one unit of a multi-unit change (local, merged into the PR branch) | `<type>/<slug>-<unit>` | `feature/seat-hold-api`, `feature/seat-hold-web` |
| a one-unit change | the PR branch itself | `feature/seat-hold` |
| checkpoint before a risky rewrite (local, §3) | `backup/<slug>-<n>` | `backup/seat-hold-1` |

`<slug>`: 2–4 English or unaccented words, lower-kebab-case, what the business gets (`seat-hold`, not
`redis-lock-impl`, not `task-12`). Units are named the same way (`api`, `web`, `refund-rule`).

| Type | For |
|---|---|
| `feature/` | new behaviour (any unit: backend, frontend, db, infra) |
| `bugfix/` · `hotfix/` | a fix · an urgent fix to released code (gitflow: from `main`) |
| `refactor/` · `test/` · `docs/` · `ci/` · `infra/` · `chore/` | as named |

A team convention (branch pattern such as `feature/{ticket}-{slug}`, commit subject format) in `CONTRIBUTING.md` or
`.aizen/config/conventions.md` replaces the defaults here where they differ; a real ticket id (Jira, GitHub
issue) is business data and may appear — pass it as `--ticket`, the guard then lets it through.

**Agent files stay on the machine** (`hide_ai_files`, default on, in `.aizen/config/guard.json`): `guard.py
install` lists `.aizen/ .agents/ .claude/ .cursor/ .gemini/ .windsurf/ AGENTS.md CLAUDE.md GEMINI.md .mcp.json
graphify-out/ …` in `.git/info/exclude` (local, so even `.gitignore` shows no trace) and turns off Claude Code's
commit/PR attribution. The pre-push hook refuses a branch whose tree holds such a file, or whose unpushed commits
carry a run id or an AI co-author/“Generated with” line, and prints the fix. A file the repository already tracks
is not hidden by the exclude list: the owner runs the printed `git rm -r --cached …` once (A4 — it is a commit
the team will see). Set `"hide_ai_files": false` when the team deliberately shares these files.

Never create `develop`, `release/*` or any branch on the remote (A4 — the owner creates remote branches). Creating `develop`
locally for a repo that has none is a decision — ask once, record it as `D-nn`.

## 2. Before the first edit — every task

```
git status --porcelain            # unrelated changes? → ask; never stash or commit the owner's work silently
git fetch                         # A0
git switch -c <task-branch> origin/<base>     # or from local base if there is no remote
git rev-parse HEAD                # record: start SHA  → report "Rollback" section
```

Never edit on a protected branch, on a detached HEAD or outside a git repository. Worktrees for parallel roles are created the same way:
`git worktree add .aizen/worktrees/<TASK>-<unit> -b "$(state.py branch --task <TASK> --unit <unit>)" <base>` (the folder
is local and may carry the run id; the branch may not).

## 3. Checkpoints during the work

- **Commit per step** — one logical change, builds, passes its focused test:
  ```
  <type>(<scope>): <imperative summary>

  <why, in business words; requirement IDs (FR/AC) when the repo's docs use them>

  Refs: <ticket>          ← only with a real ticket (`state.py init --ticket`), never the run id
  ```
  `<scope>` is the business area (`seat`, `payment`), not a role or a run. No `Co-Authored-By`/“Generated with”
  trailer from any AI tool.
  Types: `feat fix refactor perf test docs chore build ci style`. Never commit secrets, `.env`, build
  output, dumps or commented-out code. Never `--no-verify` — a failing hook is fixed or reported.
- **Before a risky rewrite** (large refactor, rebase, generated-code regeneration, mass rename): create
  `git branch backup/<TASK>-<n>` at the current commit. Local, instant, deletable later (A3 if unpushed
  work would be lost).
- After the owner has looked at a PR, add commits; do not rewrite reviewed ones.
- Committing is local and reversible: A2. If the plan says the owner commits themselves, leave changes
  uncommitted and list them.

## 4. Backup of what git does not hold

Before changing anything git cannot restore — take the backup, check it exists and is non-empty, record
it, then proceed:

| Thing | Backup | Restore command in the report |
|---|---|---|
| local database (migration, data fix, seed reset) | `pg_dump -Fc` / `mysqldump --single-transaction` via `docker compose exec` into `.aizen/backups/<TASK>/<db>-<time>.dump` | `pg_restore --clean -d <db> <file>` / `mysql <db> < <file>` |
| a git-ignored or generated file you will overwrite (local config, fixtures) | copy to `.aizen/backups/<TASK>/` | `cp` back |
| Penpot/Figma page you will change heavily | export the page/board first into `.aizen/backups/<TASK>/` | re-import or redraw from export |

`.aizen/backups/` must be git-ignored (dumps can hold personal data); check `.gitignore` and ask the owner
to add it if missing. Shared/staging data is backed up only by the owner or devops through an approved A3
action; production is the owner's (A4).

## 5. Rollback — always written, never improvised

Every report ends its evidence with:

```
Rollback: branch <task-branch> from <base>@<start-sha>; commits <sha1..shaN>
  undo all, keep history:   git revert --no-edit <start-sha>..HEAD
  discard the branch (A3):  git switch <base> && git branch -D <task-branch>
  back to a checkpoint (A3): git reset --hard <sha>
  data:                     <restore command from §4, or "none touched">
```

Running a rollback that discards work is A3; reverting a merged change on a protected branch is A4
(the owner merges the revert).

Handing work over (local-only, rebase, PR text, commands for the owner): `git-handoff.md`.
