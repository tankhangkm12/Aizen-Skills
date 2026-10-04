---
name: skill-creator
description: Create a new skill for the Aizen-Skills repo, or improve an existing one, following the Aizen Universal Structure - interview, scaffold all 8 parts, write SKILL.md/rules/references/scripts, register it in README and docs (usage guide + prompt template), evaluate it against a baseline, then npm test, sync and commit. Use when the user wants to create, write, edit, improve, benchmark or evaluate a skill for Aizen-Skills (tạo skill, viết skill, sửa skill, cải thiện skill, đánh giá skill). Not for: copying a skill from GitHub or another folder (skill-cloner), testing a skill without changing it (agent-skill-tester), or using an existing skill.
---

# skill-creator — build Aizen skills that pass the standard (v2.1)

You create and improve skills **inside the Aizen-Skills repo** so that every skill has the same shape, is
documented for the user, and passes `npm test`.

**Read first:** `rules/aizen.md`, `rules/mcp.md`, then the standard `<REPO>/docs/aizen-skill-standard.md`
(`<REPO>` = the Aizen-Skills checkout; `scripts/new_skill.py` finds it, or ask the user for the path).

## Workflow — new skill

1. **Interview (one round, then stop and wait).** Ask only what you cannot read yourself, each with a proposed
   answer: what the skill lets an agent do · 3 real prompts that must trigger it · prompts that must not (and
   which existing skill owns them — read every `skills/*/SKILL.md` description first) · the exact output ·
   what is deterministic enough for a script · what needs the user's confirmation. Propose the name.
2. **Design note (confirm before writing).** ≤ 15 lines: name, description, workflow steps, files per part
   (rules / agents / references / scripts / assets), eval prompts. Wait for "ok".
3. **Scaffold.** `python "<SKILL_DIR>/scripts/new_skill.py" <name> --description "<…>" --title "<…>"` — never
   overwrites an existing skill.
4. **Write the skill** to the standard: `SKILL.md` lean (≤ ~150 lines) with a workflow of imperative steps,
   long knowledge in `references/` with "when to read", repeatable logic in `scripts/` (stdlib, `--help`,
   `--selfcheck`), hard limits in `rules/`. Delete `.gitkeep` from parts that now hold files.
5. **Register the docs** — the rows `new_skill.py` printed: `README.md` skill table, `docs/huong-dan-su-dung.md`
   §2 and §4, a `/<name>` prompt template in `docs/prompt-mau.md`. A script with `--selfcheck` → one line in
   `tests/check-scripts.js`.
6. **Evaluate** (below) when the skill drives judgment or multi-step work; a pure reference skill may skip it —
   say so.
7. **Finish:** `npm test` green → `node bin/cli.js sync` → `git add <the files you changed>` →
   `git commit -m "feat(<name>): …"`. Push only when the user says so for this push; else print the command.
   Report: files created, test result, eval numbers, `Deviations:` from the design note.

## Workflow — improve an existing skill

1. Read the whole skill, the user's complaint or goal, and its open feedback
   (`python "<SKILL_DIR>/scripts/feedback.py" list --skill <name> --open`); reproduce the weakness with one prompt.
2. Copy the current version to `<REPO>/.aizen-work/<name>/baseline/` (never inside `skills/`).
3. Propose the change as a short diff summary (files, what changes, why) → wait for "ok".
4. Edit; bump `manifest.json` version (patch / minor / major) and any `(vN)` in headings to match; update the
   docs rows if triggers or usage changed.
5. Add one case per fixed problem to `skills/<name>/evals/evals.json` (the logged `prompt`), so the eval set grows
   into a regression suite. Evaluate against the baseline, then step 7 above (`fix(<name>): …` or `feat(<name>): …`).
6. Mark the fixed entries: `feedback.py resolve --skill <name> --id <n> --commit <sha>`.

## Evaluate — with skill vs baseline

1. Write 2–3 realistic prompts with checkable expectations to `skills/<name>/evals/evals.json`
   (`references/schemas.md`).
2. Workspace `<REPO>/.aizen-work/<name>/iteration-<N>/eval-<id>/{with_skill,without_skill}/run-1/`.
3. Dispatch all runs in one message (Claude Code: Agent tool, `general-purpose`; Antigravity:
   `invoke_subagent`): with-skill runs get the skill path, baseline runs get none (or the baseline copy). Each
   writes its outputs and `transcript.md` into its run folder. No sub-agent tool → run them yourself and label
   the baseline `[not independent]`.
4. Grade each run with `agents/grader.md` → `grading.json`; then
   `python "<SKILL_DIR>/scripts/aggregate_benchmark.py" <iteration dir> --skill-name <name>`.
5. Show the user `iteration-<N>/review.md`: pass rate with vs without, time/tokens, the failing expectations,
   and your proposed fixes. Iterate until the user is satisfied.

## Writing well

- `description` decides triggering: what · "Use when …" (English + Vietnamese keywords) · "Not for: …".
- Explain why a step exists instead of shouting MUST; give one input → output example per non-obvious step.
- Every backtick path and markdown link must exist — `npm test` fails otherwise.
- Bundle what every run would rewrite (parsers, validators, API calls) into `scripts/`.

## Knowledge

| Need | Read |
|---|---|
| structure, manifest, docs rows, git rules | `<REPO>/docs/aizen-skill-standard.md` |
| eval JSON formats | `references/schemas.md` |
| skill feedback log (`log` / `list` / `resolve`) | `scripts/feedback.py`, `<REPO>/rules/continuous-improvement.md` |
| grading a run | `agents/grader.md` |
| skeleton files | `assets/skill-template.md`, `assets/mcp-rule.md` |
