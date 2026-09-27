# ARCHIVE VAULT — SATURDAY CHECKPOINT / MONDAY RESUME
Date: September 26, 2026

## Ownership boundaries
BuyBox/Teller -> Tower -> Archive Vault -> Simplee Cloud.
Tower owns identity, authorization, purpose, classification, step-up and revocation. Vault owns document intelligence, archival evidence, immutable version lineage, decision snapshots, retention and receipts. Simplee Cloud owns ciphertext storage, infrastructure and recovery. No direct BuyBox/Teller -> Vault/Cloud access. Soulaana explains but does not authorize.

## Saturday changes on this branch
- `vault/canonical_evidence_registry.py`: SQLite append-only metadata registry for archival receipts and exact-version decision snapshots. Atomic transaction, idempotent replay, correction parent scoped to same entity/evidence, redacted receipt projection and immutability triggers.
- `vault/test_canonical_evidence_registry.py`: tests for idempotency, version correction, entity isolation, hash and opaque-ref validation, immutable rows and snapshot replay.
- This is a source-only metadata foundation. No file bytes, provider credentials, network access, or billable infrastructure. It does NOT issue proof of archival on its own: the trusted orchestration layer must first validate Tower authorization and scan receipts, commit and verify ciphertext in Simplee Cloud, then reconcile storage and database failures. Caller-supplied receipt strings alone are not proof of these operations.
- Tests committed but not executed through the GitHub connector. Do not claim production readiness.

## Monday implementation priority
1. Run tests and fix failures. Review compatibility with existing Vault registry, BuyBox draft PR #35, and Cloud's authoritative object reference contract; avoid dual canonical ledgers.
2. Build Tower-to-Vault verified internal request adapter, with authenticated provenance, expiry, replay/revocation checks. Do not trust caller-supplied booleans.
3. Implement secure intake and verified scanner result binding; fail closed when scanner unavailable.
4. Implement atomic/reconciled archival orchestration with Simplee Cloud ciphertext receipt and canonical metadata commit; explicit pending/retry/compensation state, no false ARCHIVED.
5. Implement Tower-gated redacted view, protected retrieval, retention/legal hold and audit.
6. Add integrity/recovery console and real end-to-end non-sensitive test, including corrected version and backup restore.

## PR coordination
Cloud-storage foundation PR #38 is draft and belongs to the Cloud workstream; do not merge it blindly into Vault. BuyBox handoff PR #35 is draft and separate. This Vault branch is based on vault-dev. No paid resources or production deployment without owner approval.
