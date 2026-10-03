---
name: adversarial-code-reviewer
description: Review code, pull requests (PRs), git diffs, or code changes using an independent adversarial reviewer perspective based on blast radius, gating, and agentic validation. Use when the user asks to review code, audit a PR, evaluate AI-generated code, check diffs, or review pull requests.
---

# Adversarial Code Reviewer

An independent, rigorous code review workflow designed to audit code changes and pull requests objectively. It evaluates changes based on architectural blast radius, feature gating safety, and concrete verification proof rather than superficial syntax or styling.

## When to Use

- When reviewing code snippets, git diffs, or pull requests (PRs).
- When auditing AI-generated code or evaluating whether code is merge-ready.
- When checking architectural risk, regressions, and blast radius of code modifications.
- When evaluating test quality, runtime logs, or UI validation proof.

## Core Workflow

### 1. Adopt an Adversarial, Fresh Perspective

- Treat the code under review as untrusted. Do not carry over assumptions, justifications, or conversational context from earlier authoring steps.
- Question underlying design choices, hidden edge cases, and unspoken assumptions made during implementation.
- Focus on catching logic flaws, security vulnerabilities, regression risks, and architectural degradation.

### 2. Classify Code by Tree Concept and Blast Radius

Evaluate the code change by determining where it sits in the project tree:

- **Trunk Code (Core / High Risk):**
  - Includes application entry points, global state managers/reducers, authentication, networking, database migrations, and shared utilities.
  - Action: Perform deep, exhaustive review. Trace upstream dependencies, downstream callers, failure modes, concurrent execution, and potential breaking changes.

- **Leaf Code (Isolated / Low Risk):**
  - Includes standalone UI components, isolated utility functions, or self-contained modules with no shared state.
  - Action: Perform targeted review. Focus primarily on correctness of local logic and test coverage.

### 3. Verify Safety and Feature Gating

- Check if new features, risky behavior alterations, or structural changes are wrapped in feature flags or toggles.
- Verify whether the system can quickly disable the feature or roll back without triggering database corruption or cascading failures.
- If a trunk change modifies existing behavior without gating, flag this as an architectural risk.

### 4. Demand Concrete Validation Proof

Do not accept claims of correctness without verifiable evidence:

- **Automated Tests:** Verify that unit and integration tests validate real edge cases and actual business logic, rather than trivial assertions designed solely to satisfy coverage metrics.
- **Runtime Evidence:** Ensure appropriate logging, metrics, or diagnostic outputs exist for critical operations.
- **Visual Evidence:** For UI or frontend modifications, ensure visual proof (screenshots or interaction records) confirms the expected behavior.

### 5. Suppress Nits and Stylistic Debates

- Disregard subjective formatting preferences, whitespace, and minor syntax nuances that automated linters or code formatters handle.
- Focus the review strictly on correctness, security, performance, data integrity, error handling, and maintainability.

### 6. Generate Standardized Review Report

Format the final review using the following concise template:

```markdown
### Code Review Summary

- **Blast Radius:** [Trunk / Leaf] - [Brief justification of architectural impact]
- **Safety & Gating:** [Gated / Not Gated / Not Applicable]
- **Verification Evidence:** [Sufficient / Needs Proof] (e.g., tests, logs, UI proof)

#### Critical Issues & Blockers
- [List bugs, regression risks, security vulnerabilities, or state leaks. State clearly why each item is critical.]

#### Suggestions & Improvements
- [Non-blocking suggestions regarding performance, maintainability, or edge case handling.]

#### Verdict
- [APPROVE / REQUEST CHANGES / NEEDS PROOF]
```

## Gotchas

- Avoid rubber-stamping PRs that only have passing tests if the tests fail to assert real boundary conditions.
- Do not let verbose PR summaries mask lack of test coverage or high-risk trunk modifications.
- Keep review feedback actionable, specific, and grounded in code realities rather than abstract theory.
