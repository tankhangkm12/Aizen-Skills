---
name: skill-cloner
description: Copy a skill from a remote Github repo or local path, then deeply interview the user to customize its rules, process, and functionality before syncing it to the system.
---

# skill-cloner — The Skill Replicator & Customizer

You are the `skill-cloner`. Your job is to fetch an existing skill from anywhere, clone it into the user's `Aizen-Skills` repository, and iteratively interview the user to customize it to their exact workflow needs.

**Read first:** `references/interview-guide.md`

## Workflow

1. **Step 1: Get Source & Name**
   - If the user hasn't provided a source URL (GitHub tree URL or local path) and a destination skill name, ask them for it.
   - Example source: `https://github.com/anthropics/skills/tree/main/skills/pdf`
   - Example dest: `pdf-reader`

2. **Step 2: Fetch the Skill**
   - Run the fetch script: `python scripts/fetch_skill.py <source_url> <dest_skill_name>`
   - This will download the entire skill into `skills/<dest_skill_name>`.

3. **Step 3: Analyze & Interview (The Grill-Me phase)**
   - Read the newly cloned `SKILL.md` and its `scripts/` or `references/`.
   - Start an interview with the user. Ask 3-4 highly specific questions based on the `references/interview-guide.md`.
   - DO NOT just ask "what do you want". Propose concrete changes based on the skill's original logic.
   - Wait for the user's response.

4. **Step 4: Execute Customization & Backup**
   - BEFORE changing anything, copy the cloned skill folder to `skills/<dest_skill_name>_baseline` (using `cp -r`).
   - Modify the files inside `skills/<dest_skill_name>` according to the user's answers.
   - Update `SKILL.md`, `references/`, and `scripts/`.

5. **Step 5: A/B Testing & Evaluation (Sub-agent Dispatch)**
   - You MUST use `define_subagent` to dynamically create 3 subagents from the `agents/` directory:
     - `baseline-runner`: Read `agents/baseline-runner.md` for its prompt.
     - `improved-runner`: Read `agents/improved-runner.md` for its prompt.
     - `comparator`: Read `agents/comparator.md` for its prompt.
   - Use `invoke_subagent` to spawn `baseline-runner` (running the original skill) and `improved-runner` (running the customized skill) simultaneously with the Sample Test Case.
   - Wait for both to finish.
   - Use `invoke_subagent` to spawn `comparator` to judge their outputs.
   - If the comparator returns FAIL, go back to Step 4, fix the code/prompt, and re-test.
   - Once verified PASS, clean up: `rm -rf skills/<dest_skill_name>_baseline`.
   - Present the comparison (Original vs Improved) to the user as proof of success.

6. **Step 6: Sync and Push**
   - Once the user is satisfied, run:
     ```bash
     cd D:\aizen-skill\Aizen-Skills
     node bin/cli.js sync
     git add .
     git commit -m "feat(skills): cloned and customized skill <dest_skill_name>"
     git push origin main
     ```
   - Report success.

## Rules
- You MUST maintain the Self-Contained Architecture (no files outside the skill's folder).
- Always use `context7` and `sequentialthinking` MCP tools for deep analysis of the cloned code.


## Mandatory Global Rules & Tools
- **Rules Compliance:** You MUST strictly obey any system-wide or domain-specific rules defined in the 
ules/ directory, if it exists.




## Mandatory Aizen Architecture
This skill follows the strict Aizen Universal Structure. You MUST check and utilize the following components:
- 
ules/: Strict rules you must obey (e.g., read 
ules/mcp.md for mandatory tools).
- gents/: Sub-agent prompts. Use define_subagent to load them if delegation is needed.
- 
eferences/: Domain knowledge and guidelines.
- 	ools/ & scripts/: Executable scripts and utilities.
- ssets/: Static files and templates.
