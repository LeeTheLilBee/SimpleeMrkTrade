# Archive Vault reliability release gates — authoritative acceptance checklist

No claim of production readiness may be inferred from a pack count, a green UI
badge, a schema, a mocked receipt, or tests that were merely committed.

## Required gates (all must pass with recorded evidence)
1. Authorization: real Tower-issued audience/action/entity/purpose-bound grant,
   expiry, revocation and replay checks; reject caller-supplied authorization flags.
2. Intake: bounded file size/type, quarantined bytes, verified malware scanner
   result bound to exact original digest; scanner outage fails closed.
3. Encryption: authenticated encryption, independent key lifecycle, rotation,
   tamper/wrong-entity tests; no plaintext object storage.
4. Storage: Cloud returns authenticated commit receipt; independently verify
   object existence, digest, length and namespace before ARCHIVED.
5. Metadata: one canonical Vault ledger; atomic idempotent receipt commit,
   immutable correction lineage and exact-version decision snapshots.
6. Failure handling: crash after Cloud write/before registry commit; retries,
   duplicate requests, timeouts, unavailable database, recovery and orphan
   object handling. Never display ARCHIVED during an unresolved mismatch.
7. Retrieval: reauthorize through Tower at read time, enforce redaction,
   no object locations leaked, verify ciphertext and plaintext integrity.
8. Retention: holds, expiry, disposition approvals, receipts and audit.
9. Backup: independent encryption/key protection, separate failure domain,
   scheduled restore drills, byte-for-byte digest comparison and RPO/RTO.
10. Observability: entity-scoped owner status, alarms for stale reconciliation,
    scan outage, backup age, receipt mismatch and failed integrity checks.
11. Security: concurrency, malicious input, cross-entity access, key compromise,
    rate limiting, secret handling, dependency review and penetration testing.
12. Operations: restore runbook, incident owner, rollback, maintenance,
    credential rotation, monitoring and on-call ownership.

## Demonstration required
With non-sensitive synthetic evidence, archive -> scan -> encrypt -> Cloud
commit -> canonical receipt -> independent backup -> authorized retrieval ->
correction/version snapshot -> revoke -> restore -> compare hashes.
Inject failures at each boundary and preserve the original version.

## Current status
PR #76 provides an internal journal and tests, not an authenticated service.
PR #64 provides draft metadata registry. Cloud PR #38 is a separate draft.
Their integration, independent receipt authentication, executed tests, backup
restore and live Tower gate are not certified. Do not merge by assumption or
provision paid infrastructure without owner approval.
