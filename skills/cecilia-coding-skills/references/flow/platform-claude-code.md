# Running Cecilia on Claude Code (v21)

## Dispatch

- One role instance = one **Agent** tool call. Prompt = the full output of `python scripts/state.py brief …`
  (header line first), followed by: "Read `agents/<role>.md` and `rules/core.md` in the cecilia-coding-skills
  skill, then do the brief."
- `subagent_type`: `general-purpose` for `dev`, `tester`, `devops`; `Plan` (read-only) is acceptable for
  `planner`; `general-purpose` for `reviewer` with the brief saying READ-ONLY.
- A wave = all Agent calls of that wave **in one message** so they run in parallel.
- Code writers get their own worktree. Either create it yourself (`git worktree add`) and name it in the brief,
  or pass `isolation: "worktree"` and let the harness create it — then read the branch name from the result.

## Models

| Role | Default | Why |
|---|---|---|
| planner | strongest (opus) | one plan replaces three voters; quality matters most here |
| dev | sonnet | volume work; switch to opus for CONTROLLED units |
| tester | sonnet | |
| reviewer | a different model than the devs (opus when devs ran sonnet) | independence comes from a different context **and** model |
| devops | opus | blast radius |

Cecilia may override any of these on the decision card.

## Card

Use **AskUserQuestion**: options first with the recommended one labelled "(Recommended)", then the plan's
questions (≤ 4 per call). Record the answer with `state.py answer`.

## Dispatch failed

Agent tool error, missing skill path, permission denial → stop, show the exact error, and tell Cecilia what to
check. Do not silently do the role's work instead — but in FAST mode you do the work yourself by design.
