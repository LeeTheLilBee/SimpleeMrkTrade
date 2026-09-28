# Grounds source-only production preflight error containment — 2026-09-28

The Grounds production factory's PostgreSQL adapter constructor now runs inside the same generic failure boundary as the WSGI database/schema preflight. Both a private DSN rejection and database connection/schema failure surface only the stable `GroundsProductionUnavailable` message; sensitive underlying provider diagnostics are not chained in the operator-facing exception. Independently certified Tower receiver factory initialization is treated similarly. Four fictional source regressions cover these errors and the local Tower walkthrough refusal.

This does **not** implement or certify the missing `tower.grounds_runtime_receiver`, tenant/staff assignment, private DB migration, provider backup/restore, Teller checkout, Vault, message delivery, owner consent or real tenant launch. Keep PR #51 draft/source-only; no real tenant data, deployment or paid resources.
