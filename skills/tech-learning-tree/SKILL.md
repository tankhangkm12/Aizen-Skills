---
name: tech-learning-tree
description: Research and master new technologies, libraries, and frameworks following a structured deep-dive workflow and document them into Notion as an architecture-first tree structure. Use when the user asks to learn, research, analyze, evaluate, or structure a new technology, tool, or framework into Notion.
---

# tech-learning-tree

A structured methodology to systematically deconstruct, understand, and document new technologies using an architecture-first tree hierarchy in Notion.

## When to Use

- When tasked with learning or evaluating a new technology, framework, database, engine, or tool from scratch.
- When researching a technology across official documentation and technical YouTube tutorials.
- When creating an architecture-centric knowledge base or structured study guide in Notion.
- When analyzing real-world deployment patterns and AI agent or MCP integration feasibility for a tech stack.

## Workflow Steps

### Step 1: Identify the Core Problem

- Pinpoint the exact problem, architectural bottleneck, or limitation that prompted the creation of this technology.
- Determine the design philosophy: Why existing solutions were insufficient and what core assumptions this technology challenges.
- Formulate a clear 1-2 sentence problem-solution thesis before examining implementation details.

### Step 2: Multi-Source Information Gathering

Gather verified information by consulting official project documentation, GitHub repositories, and technical YouTube deep-dives in the following strict order:

1. **Tool Fundamentals and Usage**
   - Identify core primitives, basic CLI or API usage, hello-world workflow, and standard setup requirements.
2. **Deep Internal Architecture and Visual Diagrams**
   - Dissect the internal subsystems, memory model, execution engine, or distributed topology.
   - Search for and inspect detailed architectural diagrams to visualize component boundaries and interactions.
3. **Pros, Cons, and Strategic Trade-Offs**
   - Identify the strengths, limitations, and operational costs.
   - Explicitly detail what must be sacrificed (e.g. latency vs. consistency, simplicity vs. flexibility) when choosing this technology over alternatives.
4. **Core Operational Lifecycle and Data Flow**
   - Trace the end-to-end data lifecycle: inputs, serialization, internal queueing, processing pipelines, state transitions, and outputs.
   - Break down how each internal component transforms data.
5. **Alternative Solutions**
   - Map direct competitors, legacy equivalents, and modern alternatives.
   - Build a comparison matrix covering throughput, developer ergonomics, ecosystem maturity, and maintenance overhead.
6. **Production Deployment Across Environments and Languages**
   - Examine real-world production configurations (e.g. Docker, Kubernetes, cloud managed services, bare metal).
   - Detail SDK support and client implementations across major programming languages (e.g. Python, TypeScript, Go, Rust, Java).
7. **AI Agent, Skill, and MCP Integration Potential**
   - Evaluate whether and how this technology connects to AI agents, tool calling, Model Context Protocol (MCP) servers, or custom agent skills.
   - Identify failure modes, security boundaries, rate limits, latency overhead, and authentication risks.

### Step 3: Synthesize and Publish Tree Structure in Notion

Structure the resulting knowledge base in Notion using a strict hierarchical tree model:

- **Root (Core Architecture & Thesis)**
  - Problem statement, core thesis, and primary architectural diagram.
  - High-level system overview acting as the trunk of the document.
- **Primary Branches (Structural Components)**
  - Subsystem 1: Fundamentals & Quick Start.
  - Subsystem 2: Deep Architecture & Component Breakdown.
  - Subsystem 3: Core Lifecycle & I/O Pipeline.
  - Subsystem 4: Trade-Offs & Alternative Matrix.
- **Leaf Nodes (Extensions, Implementations & Integrations)**
  - Production deployment guides across environments.
  - Multi-language SDK examples.
  - AI Agent / MCP integration patterns and risk mitigations.
- **Notion Formatting Standards**
  - Use clear Heading levels (H1 for Root, H2 for Branches, H3 for Sub-branches, Toggles for Leaf nodes).
  - Use Callout blocks for critical trade-offs, warnings, and architectural principles.
  - Use Code blocks for syntax and configuration snippets.
  - Use Tables for alternative comparisons.

## Gotchas

- Skipping the trade-offs: Every technology is optimized for specific workloads at the expense of others. Never present a technology as universally superior.
- Surface-level learning: Do not stop at basic CLI commands. Always uncover internal state management and execution flows.
- Flat documentation: Avoid long unbroken walls of text. Preserve the tree hierarchy so dependencies and extensions branch logically from the core architecture.
- Ignoring AI/MCP security boundaries: Always assess security implications such as credential leaks or unbounded tool execution when integrating with AI agents.

## Mandatory Global Rules & Tools
- **Rules Compliance:** You MUST strictly obey any system-wide or domain-specific rules defined in the `rules/` directory, if it exists.

## Mandatory Aizen Architecture
This skill follows the Aizen Universal Structure. Check and use these components when present:
- `rules/`: Strict rules you must obey (e.g., read `rules/mcp.md` for mandatory tools).
- `agents/`: Sub-agent prompts. Load them as sub-agents if delegation is needed.
- `references/`: Domain knowledge and guidelines.
- `tools/` & `scripts/`: Executable scripts and utilities.
- `assets/`: Static files and templates.
