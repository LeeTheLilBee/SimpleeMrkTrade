# Vault archival transaction improvement — integration handoff

Branch: vault-archive-transaction-state-v1 (separate from Vault PR #64 and Cloud PR #38).

Adds internal SQLite journal with explicit RECEIVED → QUARANTINED → VERIFIED →
ENCRYPTED → CLOUD_COMMITTED → ARCHIVED transitions, RECONCILE_REQUIRED and
REJECTED paths. It rejects skipped states, stale transitions, duplicate
request conflicts, missing receipt digests and ARCHIVED without separate Cloud
and registry receipt digests. Each transition appends a hash-linked event.
Entity-scoped owner summary returns counts, never raw object locations.

Important: receipt digests are *assertions supplied by a trusted caller*.
This module cannot prove Tower authorization, malware screening, Cloud write,
or registry commit. Do not expose it as a public endpoint or wire to production
until a trusted orchestrator independently validates signed/authenticated
receipts and durable registry state. Hash chaining in the same SQLite database
is corruption-evident, not administrator-tamper-proof; independently anchor
checkpoints to protected storage later.

Integration: reconcile this state journal with the canonical registry in PR
#64; use one archival receipt authority. Cloud PR #38 is a separate draft.
No paid resources, real file intake, credential setup or deployment performed.
Tests committed, execution pending CI/local runner. Owner-facing console
should show entity-scoped counts and actionable failures only after Tower
authorizes the owner context.
