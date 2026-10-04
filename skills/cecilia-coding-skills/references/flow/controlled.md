# CONTROLLED flow — what changes on high-risk work (v21)

Triggers: auth/authZ, money/stock/quota, multi-tenant data, schema or data migration, concurrency, public
contract changes, CI/CD/IaC, live clusters/VMs, secrets, destructive operations, production, multi-service.
Everything in `references/flow/standard.md` applies, plus:

1. **Plan is exact.** The planner uses `references/plan/planning-method.md`: batches with exact paths, commands,
   checks, a rollback per batch, and a measurement batch first when the root cause is not `[verified]`.
2. **Explicit approval.** The card asks Cecilia to approve the plan itself ("approve plan <TASK>"), recorded with
   `state.py answer`. Devs write only the approved paths; anything outside → stop and ask for a scope change.
3. **Wave check-in.** Stop after each build wave and show Cecilia the result before the next one.
4. **Second reviewer.** After S6, dispatch one more `reviewer` on a different model with
   `LENS=redteam` (data loss, security, irreversible steps). Its BLOCKER on data loss / secrets / destructive
   action is never overruled by the first reviewer — it goes to Cecilia.
5. **Infra.** Diff touches CI, Dockerfiles, compose, IaC, k8s/helm or `deploy/` → that unit is `devops`, not `dev`.
   Every live read and every non-prod apply is A3; production is Cecilia's.
6. **Backups first.** DB dump / state backup before any migration or data change, path in the report.
7. **Finish** includes the release/rollback packet when it ships (`assets/release-packet.md`).
