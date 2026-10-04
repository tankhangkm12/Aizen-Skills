# Running Cecilia on Claude Code (v22)

## Dispatch

- One role instance = one **Agent** tool call. Prompt = the full output of
  `python "<SKILL_DIR>/scripts/state.py" brief …` (header line first); it already names the absolute paths of
  `agents/<role>.md` and `rules/core.md`.
- `subagent_type`: `general-purpose` for every role — the planner writes its plan file, and the reviewer
  brief already says READ-ONLY. Never `Plan`/`Explore`: they cannot write their report.
- A wave = all Agent calls of that wave **in one message** so they run in parallel.
- Code writers get their own worktree. Either create it yourself (`git worktree add`) and name it in the brief,
  or pass `isolation: "worktree"` and let the harness create it — then read the branch name from the result.

## Models

| Role | Default | Why |
|---|---|---|
| planner | strongest (opus) | one plan drives every other dispatch; quality matters most here |
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
