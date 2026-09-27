# VAJ002–006 — independent source regression for Vault archival journal

This is a test/release-proof follow-up to draft PR #76 only. The internal
state machine's explicit RECONCILE_REQUIRED hold and append-only event trail
are checked against unknown/out-of-order state changes, duplicate requests,
entity-scoped summaries, missing receipt digests, ambiguous writes and
tampered local SQLite event history.

These tests intentionally do NOT claim that a caller-provided 64-character
receipt digest proves a Tower authorization, malware scan, Cloud physical
write or canonical Vault metadata receipt. Even an internal ARCHIVED state
cannot be advertised externally until a trusted, separately reviewed
orchestrator checks current Tower grant/revocation and independently
authenticated scanner, Cloud SC002 physical reconciliation and canonical
registry PR #64. Hash chaining within the same writable SQLite database
does not protect against an administrator rewriting the whole chain;
independent checkpoints and tested recovery remain future gates.

This pack adds no provider account, credentials, external HTTP endpoint,
payment, published file, hosted traffic or paid resource. PRs #35, #38,
#64, #65 and #76 remain independent source-only drafts until full crossing
and owner acceptance.
