# BUYBOX ↔ TOWER ↔ ARCHIVE VAULT — PROOF / EVIDENCE HANDOFF

Status: **contract and local-safe preparation only; NOT live archival**. Branch: `buybox-vault-proof-evidence-contract-v1`, PR #35, base `vault-dev`.

## Ownership and flow
BuyBox owns encrypted temporary acquisition intake, source document references, evidence IDs, deal evaluation and immutable decision snapshots. Tower owns identity, role/entity/purpose/classification checks, step-up/approval, redaction, permitted transfer and download protocol. Vault owns sealed original archival, canonical document/version registry, retention and archival receipts. BuyBox must never call Vault directly. Allowed flow: BuyBox → Tower → Vault → Tower → BuyBox. Teller's separate workflow stays Teller → Tower → Vault → Tower → Teller.

## Implemented in this branch
- `vault/buybox_evidence_handoff_contract.py`: exact versioned metadata-only request, strict field allowlists, hash/opaque-ref validation, response allowlist, no false ARCHIVED without canonical receipt, version and verified digest; stable request fingerprint.
- `tower/buybox_evidence_handoff.py`: Tower-facing preparation function; fails closed when any supplied Tower gate is incomplete, checks principal/entity match, returns PENDING even when checks pass. **It does not authenticate the caller or verify a signed Tower decision itself.** Do not expose this function as a public endpoint without real Tower identity/authorization middleware.
- `vault/buybox_evidence_lineage_registry.py`: local SQLite append-only pending version references, parent/correction lineage, immutable decision snapshots bound to exact evidence versions and rule version. This is NOT canonical Vault archival storage.
- Three focused test files for contract, Tower gate and local lineage.

## Remaining required work before live activation
1. Bind Tower preparation to the existing authenticated Tower identity, permission, role/entity, purpose, classification, approval and step-up services. Never accept caller-supplied booleans as proof.
2. Add an authenticated, bounded, short-lived binary transfer separate from the JSON packet. Verify actual bytes against SHA-256, content size/type, quarantine and malware scanning. Unknown scanner result must fail closed; handle archive traversal/decompression limits.
3. Implement canonical Vault immutable original-object/version storage and append-only receipts; verify source/received hashes and preserve corrections as distinct versions. Link decision snapshots to exact versions.
4. Implement retention policy and legal-hold binding, disposition approvals and access/revocation audit events. Never auto-delete on expiration.
5. Implement Tower-controlled protected download with short TTL, purpose/entity binding, replay prevention, permission/redaction recheck, and no public URLs or raw Vault locations in JSON.
6. Integrate BuyBox outbox/status reconciliation; distinguish PENDING, QUARANTINED, DENIED, FAILED, ARCHIVED. ARCHIVED only after verified canonical Vault receipt.
7. Add end-to-end tests for malicious files, corrupt transfer, mismatched entity, revoked permissions, cross-deal references, concurrent idempotency, unavailable Tower/Vault/scanner, historical correction, legal hold and replay.
8. Run tests/CI and verify branch/PR mergeability before promotion. No test execution was performed by the GitHub connector in this handoff.

## Explicit exclusions
No direct BuyBox→Vault transport; no recovery commit, GO, owner session, recording authority grant, provider connection, production storage mutation, or download authorization is introduced. Keep GP821–GP830 recovery work independent. Do not merge this draft as a live integration.
