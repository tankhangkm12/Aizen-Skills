# How to reason before you act (Aizen)

Installed as a session rule by `guard.py install`. The full method and the playbooks are in aizen-core
`references/core/reasoning.md`; read the playbook that fits when a task is not trivial.

1. **Restate the problem in one sentence** with the observable result that would prove it solved. If you cannot,
   the task is unclear: say what is missing.
2. **Separate facts from guesses.** Read or run what can be checked; label the rest `[inferred]` or
   `[unverified]` and do not build on an unchecked guess when one command would check it.
3. **See at least two ways** for any choice that is costly to reverse (schema, public API, money, concurrency,
   security, a new dependency). Compare them on the criteria that matter here, not on taste.
4. **Ask "how would this fail?"** before choosing: the input, timing, scale or permission that breaks it.
   Prefer the option whose failure is visible and recoverable.
5. **Take the smallest step that teaches you something**, then check it. Two failed attempts on the same idea →
   stop, write down what you learned, and change the hypothesis instead of retrying harder.
6. **Write the decision where the owner can follow it.** In an Aizen run: `journal.py note --kind think` when you
   start weighing, `--kind decide` naming the option you took and why (one line each).

Size the effort to the stakes: a typo needs none of this; a migration or a payment flow needs all of it.
