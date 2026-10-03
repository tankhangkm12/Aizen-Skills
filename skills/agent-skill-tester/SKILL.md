---
name: agent-skill-tester
description: Evaluate and test AI agent skills against baseline behavior across Outcome, Process, Style, and Efficiency. Use when validating, evaluating, or benchmarking agent skills, creating test datasets, or running LLM-as-a-judge assessments for skills.
---

# Agent Skill Tester

Framework to evaluate, test, and benchmark AI agent skills by comparing a clean-slate agent baseline against an agent equipped with the skill, using structured test suites and an LLM-as-a-judge evaluation rubric.

## When to Use

- When validating a newly created skill before deploying it to production.
- When modifying or refactoring an existing skill to ensure previous capabilities remain intact.
- When testing trigger precision (validating explicit triggers, implicit triggers, and negative control prompts).
- When benchmarking whether a skill provides a measurable improvement over an agent operating without the skill.

## Core Evaluation Dimensions

Evaluate skill runs across four distinct dimensions:

- Outcome: Did the agent produce the expected final deliverable accurately?
- Process: Did the agent follow the intended steps and invoke the required tools or scripts in correct order?
- Style: Did the agent adhere to naming conventions, directory structure, file formats, and communication tone?
- Efficiency: Did the agent avoid redundant commands, unnecessary tool calls, token waste, or rabbit holes?

## Evaluation Workflow

### 1. Define Success Criteria and Rubric

Before running tests, establish clear pass/fail definitions for the skill:

- Identify the required artifact or result (Outcome).
- Identify the mandatory tool sequences or CLI calls (Process).
- Specify output format constraints (Style).
- Set maximum tolerable steps or token budget (Efficiency).

### 2. Construct the Test Dataset

Create a structured test matrix containing at least four categories of prompts:

- Explicit Triggers: Prompts that directly name the skill (e.g., "Use model-trainer to fine-tune...").
- Implicit Triggers: Prompts describing the goal without mentioning the skill (e.g., "Train a sentiment classifier on Hugging Face").
- Conversational Guidance: Prompts requesting guidance or help where the skill should guide the user.
- Negative Controls: Prompts that share topical keywords but must NOT activate the skill (e.g., "Explain what model training is").

Record each test case with the following fields:

- id: Unique test identifier.
- prompt: Exact input prompt.
- should_trigger: Boolean indicating whether the skill must be activated.
- expected_outcome: Specific measurable result or artifact.
- evaluation_criteria: Notes on process, style, and efficiency expectations.

### 3. Execute Baseline vs. Skill Comparison

Test the prompt in two distinct configurations:

- Clean-Slate Baseline (Agent without Skill): Run the prompt with the base model and standard tools only. Observe where the agent fails, makes invalid assumptions, hallucinate commands, or requires excessive roundtrips.
- Equipped Agent (Agent with Skill): Run the exact same prompt with the target skill loaded.

Compare the two runs to measure the skill delta:

- Did the skill prevent errors observed in the baseline?
- Did the skill reduce execution steps and prompt iterations?
- Did the skill follow the defined organizational procedures?

### 4. Apply LLM-as-a-Judge Scoring

Use an independent evaluation prompt to score the equipped agent run:

- Outcome Score (Pass / Fail): Did the output match the expected deliverable?
- Process Score (Pass / Fail): Were proper tools and sequences used?
- Style Score (Pass / Fail): Were file locations, formats, and conventions respected?
- Efficiency Score (Pass / Fail): Was execution direct without unnecessary exploration?

Calculate an overall verdict (Pass, Needs Revision, or Fail) along with actionable feedback on failure modes.

### 5. Diagnose and Refine

Based on evaluation results, apply targeted fixes:

- Trigger Failures: If the skill fails to activate on implicit prompts (false negative) or activates on negative controls (false positive), refine the  field in the frontmatter.
- Process or Style Failures: If the agent deviates from instructions, add concrete input/output examples or constrain degrees of freedom.
- Efficiency Failures: If the agent wastes tokens or runs redundant commands, explicitly instruct what not to do.
- Regression Tracking: Save newly discovered edge cases and bug reports into the test dataset to prevent future regressions.

## Gotchas

- Testing by vibe: Relying on one subjective prompt instead of a reproducible test dataset leads to silent failures.
- Omitting negative controls: A skill that triggers too aggressively wastes context tokens on unrelated tasks.
- Masked flaws due to smart models: Capable LLMs often work around broken skill instructions. Monitor logs for unnecessary retries and hidden inefficiencies.
- Version control neglect: Always track skill files and test suites in Git to correlate evaluation changes with prompt modifications.


## Mandatory Global Rules & Tools
- **Rules Compliance:** You MUST strictly obey any system-wide or domain-specific rules defined in the 
ules/ directory, if it exists.


## Mandatory Global Rules & MCPs
- **Rules Compliance:** You MUST strictly obey any system-wide or domain-specific rules defined in the 
ules/ directory, if it exists.
- **MCP Usage:** For any technical task, planning, design, code reviewing, testing, or skill cloning, you MUST ALWAYS use the context7 and sequentialthinking MCP tools. Do not bypass them.
