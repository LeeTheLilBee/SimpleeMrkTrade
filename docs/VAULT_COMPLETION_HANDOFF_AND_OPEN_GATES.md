# Vault handoff: source implementation versus live acceptance

The current source branch provides a journal, canonical archival metadata ledger,
synthetic encrypted object-store integration, internal reconciliation routine,
retention/legal-hold decision ledger, entity-scoped integrity report and CI tests.

The reconciliation routine is deliberately conservative: it cannot create a
missing canonical archival receipt after an ambiguous Cloud write. Such a
workflow remains RECONCILE_REQUIRED for an owner-authorized recovery procedure
that verifies original authorization, scan, encrypted object and exact identity
before recording a receipt. It does not run on a timer or use production Cloud.

Tower must provide an independently authenticated and revocable request-bound
authorization; scanner must attest exact bytes; Cloud must authenticate commit
and existence proofs. Do not expose internal journal/registry/report functions
to callers as authorization endpoints. Owner report must be Tower-gated.

The retention ledger records hold and policy decisions but does not authorize
or execute deletion; live disposition requires an independently approved
workflow, expiry checks and evidence of no active hold.

Prior passing CI is tied to commit 1af0f5b61fb596a7899a3cdeb309adf7553e2956,
not automatically to subsequent commits. Confirm exact-head CI before merging.
No provider credentials, paid resource, live restore drill, or deployment is
represented by these source tests. Keep production release gated until
Tower/Cloud/scanner integration and independently protected backup/restore
have demonstrated success.
