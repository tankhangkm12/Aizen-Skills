# Reasoning — the method and the playbooks

The short version is a session rule (`rules/reasoning.md`, installed into `.agents/rules/` and `.claude/rules/` by
`guard.py install`, so Antigravity and Claude Code read it every session). This file is the long version: read the
playbook that fits before a non-trivial step. It works the same in any agent — nothing here needs a tool that
only one platform has.

## 1. The loop

```
frame → facts → options → failure → step → check → write it down
```

| Step | Do | Done when |
|---|---|---|
| **Frame** | one sentence: what must be true afterwards, observable from outside | you could write the test or the acceptance case for it |
| **Facts** | read the code, run the command, query the data; label what you could not check (`references/core/evidence.md`) | every claim you will build on is `[verified]` or named as a risk |
| **Options** | at least two for a costly-to-reverse choice; one is "the simplest thing that could work" | each has its cost, its risk and what it rules out |
| **Failure** | for the favourite: the input, timing, scale, permission or partial failure that breaks it | you know how you would notice it in a test or a log |
| **Step** | the smallest change that tests the riskiest assumption first | it fits in one commit and one check |
| **Check** | run the check; compare with the frame, not with what you hoped | the output is quoted, not summarised |
| **Write it down** | `journal.py note --kind decide` (in a run) or the plan's Decisions | the owner can see which option and why in one line |

Two failed attempts on the same hypothesis → stop. Write `--kind stop` or `--kind think` with what the two
attempts showed, then form a different hypothesis. Retrying harder on a wrong model is the most expensive habit an
agent has.

## 2. Choosing between options

Pick criteria **before** scoring, from this task: correctness under the stated load, reversibility, blast radius,
effort, operational cost, fit with the existing code. Taste and novelty are not criteria.

| Signal | Lean towards |
|---|---|
| hard to undo (schema, public API, data format, money) | the option that keeps a way back (expand → migrate → contract, feature flag, versioned endpoint) |
| unknown load or unknown requirement | the simplest option plus a measurement that will tell you when to change it |
| the codebase already solves a similar problem | the existing pattern (`references/core/code-quality.md` reuse ladder), even if you would design it differently |
| two options tie | the one with less code and fewer moving parts |

Options and recommendations for the owner follow `references/core/decisions.md`; this section is how you reach
yours, not how you present it.

## 3. Playbooks

### Bug or failing test
1. Reproduce it with one command; save the command. No reproduction → collect the evidence (log, input, version)
   and say so; do not fix blind.
2. Read the error from the top frame that is *your* code. State one hypothesis that explains **all** symptoms.
3. Cheapest test of the hypothesis first: a log line, a breakpoint, a smaller input, `git bisect` between a good
   and a bad commit.
4. Fix the cause, not the symptom (no catch-and-ignore, no retry around a logic error). Add the reproduction as a
   regression test that fails before the fix.
5. Look for the same mistake elsewhere with a search, and list — do not silently fix — what you find.

### Design choice (a module, a table, an endpoint)
1. Write the consumer's view first: the request and response, the query, the call site.
2. Name the invariants (a seat is held by at most one user; a balance never goes negative) and where each is
   enforced — the database, a lock, a single writer, a check.
3. Walk the failure list: concurrent writers, retries and duplicates, partial failure between two systems,
   clock and timeouts, permission of the caller, very large and empty inputs.
4. Prefer enforcement closest to the data (constraint, unique index, atomic operation) over checks in application
   code that can race.

### Unknown error, unfamiliar tool or library
1. Read the exact version's documentation or source (context7, the repo at the tag) before guessing flags.
2. Make a minimal example outside the project that shows the behaviour; then bring the smallest change back.
3. Quote the source you followed in the journal or the report; an API remembered from training is `[unverified]`.

### Performance
1. Measure first, with the workload that matters (the request, the data size, the concurrency). No number → no
   optimisation.
2. Find where the time goes (profiler, query plan, trace) before changing anything.
3. Change one thing, measure again, keep the numbers in the report (`references/core/numbers.md`).

### Data, money, concurrency, security
1. Assume every request can arrive twice, out of order and at the same time as another.
2. Make the operation idempotent or atomic; know what the database guarantees at its isolation level.
3. A change that deletes or rewrites data, moves money or widens access is A3 or higher
   (`references/core/rules.md`): prepare it, show the owner, wait.

### Stuck
Signs: the same error after two fixes, a growing diff with no passing check, a plan that keeps changing.
1. Stop editing. Write in the journal what you know, what you tried and what each attempt showed.
2. Shrink the problem: the smallest input, one module, one test.
3. Still stuck → `--kind ask` with the two or three concrete options you see; the owner chooses.

## 4. What good reasoning looks like in the journal

```
- 14:02 · dev-seat · 🧠 Tôi đang nghĩ cách chặn hai người giữ cùng một ghế: khoá Redis hay unique index
- 14:05 · dev-seat · 🔧 Tôi sẽ thử SET NX PX trên seat:{id} — rủi ro: Redis mất key khi restart
- 14:11 · dev-seat · 🔀 Tôi chọn unique index (seat_id, trip_id) WHERE status='held' vì DB là nguồn sự thật; Redis chỉ cache
```

Each line says what was weighed, what was taken and why. "Đang làm task" or "đã xong bước 3" says nothing the
hooks do not already record.
