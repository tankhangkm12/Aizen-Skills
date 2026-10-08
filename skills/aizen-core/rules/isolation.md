# Data Isolation Rule

**Rule:** You must maintain a strict boundary between "Team Documentation" and "AI Workspaces".

1. **The AI Workspace (`.aizen/decisions/`, `.aizen/proposals/`, `.aizen/scratch/`):**
   - ALL brainstorming, trial-and-error logs, technology selection reasoning (Decision Logs), skill evaluations, and evolution proposals MUST be saved here.
   - This folder is meant for you (the AI) and the human to communicate and store metadata.

2. **The Team Workspace (`docs/`):**
   - This directory is sacred. It is for human developers and stakeholders.
   - ONLY save finalized, pristine documentation here (e.g., High-Level Design, API Contracts, System Requirements).
   - Do NOT save process logs, chat transcripts, or raw research notes here. The state of this directory must be 100% clean and professional for a `git push`.
