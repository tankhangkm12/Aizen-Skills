---
name: skill-cloner
description: "Copy an existing skill from a GitHub folder or a local path into the Aizen-Skills repo, bring it to the Aizen Universal Structure (8 parts, manifest with source and licence), interview the user to customize its process, rules and scripts, prove the custom version beats the original in an A/B test, register it in README and docs, then npm test, sync and commit. Use when the user gives a skill link or folder to clone, import, fork or adapt (clone skill, chép skill, lấy skill từ GitHub, tuỳ biến skill có sẵn). Not for: writing a new skill from scratch or improving a skill already in the repo (skill-creator), or only evaluating a skill (agent-skill-tester)."
---

# skill-cloner — import a skill and make it the user's (v2)

You bring a skill from elsewhere into the Aizen-Skills repo, reshape it to the user's workflow, and prove the
result is better than the original.

**Read first:** `rules/aizen.md`, `rules/mcp.md`, the standard `<REPO>/docs/aizen-skill-standard.md`
(`<REPO>` = the Aizen-Skills checkout; `scripts/fetch_skill.py` finds it, or ask the user for the path), and
`references/interview-guide.md`.

## Workflow

1. **Source and name.** Need a GitHub folder URL (`https://github.com/<owner>/<repo>/tree/<ref>/<path>`) or a
   local folder with `SKILL.md`, and a destination name (lowercase-hyphen). Missing → ask once, proposing a
   name. An existing `skills/<name>` → propose another name; never overwrite.
2. **Fetch.** `python "<SKILL_DIR>/scripts/fetch_skill.py" <source> <name>` → the skill in `skills/<name>/`
   in the Aizen structure, the untouched original in `<REPO>/.aizen-work/<name>/baseline/`. Report the files,
   the licence it found (none → tell the user before going further) and what it added.
3. **Analyze, then interview (one round, then stop and wait).** Read the whole copied skill. Ask 3–4 questions
   from `references/interview-guide.md`, each with a concrete proposal tied to what the skill does today,
   plus the **sample task** for the A/B test.
4. **Change summary (confirm).** ≤ 15 lines: files to change and how, new rules/steps/scripts, what is removed,
   the new description. Wait for "ok".
5. **Customize** to the standard: `SKILL.md` lean with a workflow, rules in `rules/`, knowledge in
   `references/`, scripts stdlib with `--help`; description = what · "Use when …" · "Not for: …" (read the other
   skills' descriptions so it does not steal their triggers). Keep the upstream licence file and credit.
6. **A/B test** (below). FAIL → back to step 5, at most 3 rounds, then show the user the gaps.
7. **Register the docs**: a row in the `README.md` skill table, rows in `docs/huong-dan-su-dung.md` §2 and §4,
   a `/<name>` prompt in `docs/prompt-mau.md`; a script with `--selfcheck` → one line in `tests/check-scripts.js`.
8. **Finish:** `npm test` green → `node bin/cli.js sync` → `git add skills/<name> README.md docs/… tests/…` →
   `git commit -m "feat(<name>): clone from <source> and customize"`. Push only with the user's yes for this
   push; else print the command. Report: what changed vs the original, A/B verdict, test result,
   `Deviations:` from the change summary.

## A/B test

1. Workspace `<REPO>/.aizen-work/<name>/ab-<N>/{baseline,improved}/`.
2. Dispatch both runners in one message (Claude Code: Agent tool, `general-purpose`; Antigravity:
   `define_subagent` + `invoke_subagent`), each with the sample task, its skill path and its output folder:
   `agents/baseline-runner.md` (the baseline copy) and `agents/improved-runner.md` (`skills/<name>`).
3. Then `agents/comparator.md` with both output folders and the user's customization list → PASS / FAIL with
   reasons per item.
4. No sub-agent tool → run the three roles yourself in turn and label the verdict `[not independent]`.
5. Show the user the comparison table. Keep `.aizen-work/` (git-ignored) until the user is done.

## Knowledge

| Need | Read |
|---|---|
| structure, manifest, docs rows, git rules | `<REPO>/docs/aizen-skill-standard.md` |
| interview questions and mapping answers to files | `references/interview-guide.md` |
| A/B roles | `agents/baseline-runner.md`, `agents/improved-runner.md`, `agents/comparator.md` |
