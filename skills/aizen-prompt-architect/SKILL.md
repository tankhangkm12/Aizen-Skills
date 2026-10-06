---
name: aizen-prompt-architect
description: "Interview the owner and turn a rough idea, bug or change into a ready-to-paste Aizen task prompt (v1) - one short round of questions with options and defaults, then a prompt with task id, business name, type, goal, observable acceptance criteria, scope and non-goals, constraints, pre-approved A3 actions, the stop point and Given/When/Then acceptance seeds. Also ships as a single-file kit (docs/aizen-web-kit.md) for ChatGPT, Gemini, Claude chat or DeepSeek. Use when the owner wants help writing or sharpening a prompt for aizen-build or aizen-init (viết prompt cho aizen, soạn task, phỏng vấn tôi rồi viết prompt, làm rõ yêu cầu). Not for: doing the task itself (aizen-build), project bootstrap (aizen-init) or writing a skill (aizen-skill-creator)."
---

# aizen-prompt-architect — from a rough idea to an Aizen prompt (v1)

The owner knows what they want but not every field an Aizen run needs. You interview them briefly, then hand back
one prompt they paste into Claude Code or Antigravity. You write **no code and no plan**; the plan is
`aizen-build`'s job and it will measure the repo itself.

**Read first:** `references/prompt/interview.md` (what to ask, what never to ask) and `references/prompt/format.md`
(the prompt shape and the quality check).

## Workflow

1. **Classify** the request: feature · bug · refactor · idea-to-PR · database design · CI/CD · project bootstrap
   (`references/prompt/interview.md` §1). Unsure → it is a question in step 2, with your best guess as default.
2. **One round of questions**, at most five, each with 2–4 options and a default you would pick
   (`references/prompt/interview.md` §2–3). Skip every field the owner already gave and everything the agent
   can measure in the repo. Answers leave a gap that changes the result → one more round, at most two in total.
3. **Write the prompt** in the shape of `references/prompt/format.md` §2, in the owner's language, in one code
   block. Unknown but non-blocking fields → leave the line out; never invent ids, numbers or file paths.
4. **Run the quality check** (`references/prompt/format.md` §4) and fix what fails before showing it.
5. **Deliver.** Inside a project with `.aizen/`: also save it to `.aizen/out/prompts/<business-name>.md` and say
   the path in one line. In a web chat: the code block is the delivery. Then stop — no follow-up plan.

## Gotchas

- Asking what the repo can answer (framework, folder layout, test runner) wastes the owner's time and is wrong
  more often than the agent's measurement — leave it to the run.
- An acceptance criterion that says "works well" or "is fast" is not one: make it observable or move it to a
  question.
- The business name becomes the git branch (`feature/<business-name>`): short, lowercase, words joined by `-`, no
  task code, no agent words.
- Do not promise behaviour Aizen does not have; when unsure, describe the outcome and let the run decide how.

## Web kit

`scripts/prompt/export_web.py` writes this skill as one self-contained Markdown file for chat AIs that cannot
install skills: `uv run "<SKILL_DIR>/scripts/prompt/export_web.py" --out docs/aizen-web-kit.md`
(`--check` fails when the committed kit is stale).
